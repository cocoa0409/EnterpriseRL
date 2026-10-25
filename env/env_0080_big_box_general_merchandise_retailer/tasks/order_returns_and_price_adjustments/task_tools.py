"""Hidden task tools for the order_returns_and_price_adjustments difficulty (category order)."""

from decimal import Decimal, ROUND_HALF_UP

from erlbench import ToolContext, tool


class _Money:
    """Value helpers only; every write happens in the tool bodies."""

    @staticmethod
    def cents(value) -> float:
        return float(Decimal(str(value)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP))

    @staticmethod
    def is_cents(value) -> bool:
        return Decimal(str(value)) == Decimal(str(value)).quantize(Decimal("0.01"))

    @staticmethod
    def is_date(value) -> bool:
        parts = str(value).split("-")
        if not (len(str(value)) == 10 and len(parts) == 3 and all(p.isdigit() for p in parts)):
            return False
        year, month, day = int(parts[0]), int(parts[1]), int(parts[2])
        if not 1 <= month <= 12:
            return False
        leap = year % 4 == 0 and (year % 100 != 0 or year % 400 == 0)
        month_days = [31, 29 if leap else 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
        return 1 <= day <= month_days[month - 1]


class _Tender:
    """Tender check shared by the tools; values only, never writes."""

    @staticmethod
    def refusal(ctx: ToolContext, order: dict) -> str:
        if order.get("payment_method_type") != "external_card":
            return "Error: this order was not paid with an external card; it is not booked here."
        oid = order.get("order_id")
        if ctx.find("membership_events", order_id=oid, event_type="membership_cash_redeem"):
            return "Error: Northgate Cash was redeemed on this order; it is not booked here."
        if ctx.find("gift_events", source_record_id=oid, event_type="gift_redeem"):
            return "Error: a gift card was redeemed on this order; it is not booked here."
        return ""


@tool(owner="user", rw="write")
def reschedule_large_item_delivery_d930ab59(ctx: ToolContext, order_id: str, new_scheduled_date: str,
                                            late_change_fee_usd: float) -> str:
    """The customer moves the delivery appointment of their own Northgate Scheduled Large-Item Delivery order to a new date and accepts the late-change fee that goes with the change. One call records the customer's confirmed reschedule request on the order, sets the order's scheduled delivery date to the new date, raises the order's reschedule count by one, and, when the fee is above 0.00, charges it on the order as a late-change fee paid by the external payment card on file for the order, adding it to the net amount paid on the order; a 0.00 fee charges nothing and books no fee. The customer sees the new delivery date and the fee on the order at once. Only an order paid in full by an external card with no Northgate Cash or gift card redeemed on it is booked here; any other order is refused and nothing is recorded, its posting being made by a human representative.

    Args:
        order_id: Id class — the reference number of the customer's Scheduled Large-Item Delivery order whose appointment is being moved, read from the customer's order lookup.
        new_scheduled_date: Fixed-format class — the new delivery date the customer chooses, written as YYYY-MM-DD (calendar date in the store's local time zone, no time part); must be a valid calendar date.
        late_change_fee_usd: Fixed-format class — the late-change fee charged for this change, in US dollars as a non-negative number with at most 2 decimal places, already rounded half up to the cent; 0.00 when no fee is owed.

    Returns:
        A confirmation text containing: request_id (the reference number of the confirmed reschedule request, text), order_id (the order moved, text), scheduled_date (the new delivery date, YYYY-MM-DD), reschedule_count (the order's reschedule count after this change, whole number), fee_event_id (the reference number of the late-change fee charge, text, or none when no fee was charged) and late_change_fee_usd (the fee charged, USD with 2 decimals). A text starting with "Rescheduled" means the change and the fee are recorded; a text starting with "Error:" means nothing was recorded.
    """
    if not _Money.is_date(new_scheduled_date):
        return "Error: new_scheduled_date must be written as YYYY-MM-DD."
    if float(late_change_fee_usd) < 0 or not _Money.is_cents(late_change_fee_usd):
        return "Error: late_change_fee_usd must be a non-negative amount with at most 2 decimal places."
    orders = ctx.find("order_holdings", order_id=order_id)
    if not orders:
        return f"Error: no order {order_id}."
    order = orders[0]
    refusal = _Tender.refusal(ctx, order)
    if refusal:
        return refusal
    fee = _Money.cents(late_change_fee_usd)
    request_id = ctx.make_id("oreq_", order_id, new_scheduled_date, fee)
    ctx.create("order_requests", request_id, order_request_id=request_id, customer_id=order["customer_id"],
               order_id=order_id, request_type="reschedule_delivery", request_status="confirmed",
               created_at=ctx.now())
    count = int(order.get("reschedule_count") or 0) + 1
    paid = _Money.cents(Decimal(str(order.get("amount_paid_usd") or 0)) + Decimal(str(fee)))
    ctx.update("order_holdings", order_id, scheduled_date=new_scheduled_date, reschedule_count=count,
               amount_paid_usd=paid)
    fee_id = ctx.make_id("oev_", order_id, "late_change", new_scheduled_date, fee) if fee > 0 else "none"
    if fee > 0:
        ctx.create("order_events", fee_id, order_event_id=fee_id, order_id=order_id,
                   customer_id=order["customer_id"], event_type="order_charge_fee", event_date=ctx.now()[:10],
                   amount_usd=fee, line_number=0, quantity=0, fee_type="late_cancellation", standard_fee_usd=fee,
                   fee_waiver_source="none", payment_method_type="external_card",
                   item_category="not_applicable", return_class="not_applicable")
    return (f"Rescheduled: request_id={request_id}, order_id={order_id}, scheduled_date={new_scheduled_date}, "
            f"reschedule_count={count}, fee_event_id={fee_id}, late_change_fee_usd={fee:.2f}.")


class _FeeRefund:
    """Checks shared by the fee refund tools; values only, never writes."""

    @staticmethod
    def check(ctx: ToolContext, order_id: str, fee_event_id: str, amount, fee_type: str):
        if float(amount) <= 0 or not _Money.is_cents(amount):
            return None, "Error: the amount must be above zero with at most 2 decimal places."
        orders = ctx.find("order_holdings", order_id=order_id)
        if not orders:
            return None, f"Error: no order {order_id}."
        fees = ctx.find("order_events", order_event_id=fee_event_id, order_id=order_id,
                        event_type="order_charge_fee", fee_type=fee_type)
        if not fees:
            return None, f"Error: {fee_event_id} is not a {fee_type} fee charged on order {order_id}."
        refusal = _Tender.refusal(ctx, orders[0])
        if refusal:
            return None, refusal
        return orders[0], ""


@tool(owner="agent", rw="write")
def credit_missed_appointment_73d9a081(ctx: ToolContext, order_id: str, fee_event_id: str,
                                       credit_amount_usd: float) -> str:
    """Books the missed-appointment credit on a Northgate Scheduled Large-Item Delivery order: one refund of part or all of the order's large-item delivery fee, credited to the external payment card that paid the order. The refund is recorded against that delivery fee with the reason fee refund, and the net amount paid on the order goes down by the credit. The customer sees the credit on the order and on the card at once. Only an order paid in full by an external card with no Northgate Cash or gift card redeemed on it is booked here; any other order is refused and nothing is recorded, its posting being made by a human representative.

    Args:
        order_id: Id class — the reference number of the Scheduled Large-Item Delivery order, read from the customer's order lookup.
        fee_event_id: Id class — the reference number of the large-item delivery fee charged on that order, read from the order's line and fee lookup.
        credit_amount_usd: Fixed-format class — the credit refunded on the delivery fee, in US dollars as a positive number with at most 2 decimal places, already rounded half up to the cent.

    Returns:
        A confirmation text containing: refund_event_id (the reference number of the credit, text), order_id (text), fee_event_id (the delivery fee credited, text), credit_amount_usd (USD with 2 decimals) and amount_paid_usd (the order's net amount paid after the credit, USD with 2 decimals). A text starting with "Credited" means the credit is booked; a text starting with "Error:" means nothing was booked.
    """
    order, err = _FeeRefund.check(ctx, order_id, fee_event_id, credit_amount_usd, "large_item_delivery")
    if err:
        return err
    amount = _Money.cents(credit_amount_usd)
    rid = ctx.make_id("oev_", order_id, fee_event_id, "missed_appointment", amount)
    ctx.create("order_events", rid, order_event_id=rid, order_id=order_id, customer_id=order["customer_id"],
               event_type="order_refund_charge", event_date=ctx.now()[:10], original_event_id=fee_event_id,
               refund_reason="fee_refund", fee_type="large_item_delivery", quantity=0, amount_usd=amount,
               line_number=0, payment_method_type="external_card",
               item_category="not_applicable", return_class="not_applicable")
    paid = _Money.cents(Decimal(str(order.get("amount_paid_usd") or 0)) - Decimal(str(amount)))
    ctx.update("order_holdings", order_id, amount_paid_usd=paid)
    return (f"Credited: refund_event_id={rid}, order_id={order_id}, fee_event_id={fee_event_id}, "
            f"credit_amount_usd={amount:.2f}, amount_paid_usd={paid:.2f}.")


@tool(owner="agent", rw="write")
def credit_replacement_haul_away_849732e1(ctx: ToolContext, order_id: str, fee_event_id: str,
                                          credit_amount_usd: float) -> str:
    """Books the replacement haul-away credit on a Northgate Scheduled Large-Item Delivery order: one refund of part or all of the order's haul-away charge, credited to the external payment card that paid the order. The refund is recorded against that haul-away charge with the reason fee refund, and the net amount paid on the order goes down by the credit. The customer sees the credit on the order and on the card at once. Only an order paid in full by an external card with no Northgate Cash or gift card redeemed on it is booked here; any other order is refused and nothing is recorded, its posting being made by a human representative.

    Args:
        order_id: Id class — the reference number of the Scheduled Large-Item Delivery order, read from the customer's order lookup.
        fee_event_id: Id class — the reference number of the haul-away charge on that order, read from the order's line and fee lookup.
        credit_amount_usd: Fixed-format class — the credit refunded on the haul-away charge, in US dollars as a positive number with at most 2 decimal places, already rounded half up to the cent.

    Returns:
        A confirmation text containing: refund_event_id (the reference number of the credit, text), order_id (text), fee_event_id (the haul-away charge credited, text), credit_amount_usd (USD with 2 decimals) and amount_paid_usd (the order's net amount paid after the credit, USD with 2 decimals). A text starting with "Credited" means the credit is booked; a text starting with "Error:" means nothing was booked.
    """
    order, err = _FeeRefund.check(ctx, order_id, fee_event_id, credit_amount_usd, "haul_away")
    if err:
        return err
    amount = _Money.cents(credit_amount_usd)
    rid = ctx.make_id("oev_", order_id, fee_event_id, "replacement_haul_away", amount)
    ctx.create("order_events", rid, order_event_id=rid, order_id=order_id, customer_id=order["customer_id"],
               event_type="order_refund_charge", event_date=ctx.now()[:10], original_event_id=fee_event_id,
               refund_reason="fee_refund", fee_type="haul_away", quantity=0, amount_usd=amount,
               line_number=0, payment_method_type="external_card",
               item_category="not_applicable", return_class="not_applicable")
    paid = _Money.cents(Decimal(str(order.get("amount_paid_usd") or 0)) - Decimal(str(amount)))
    ctx.update("order_holdings", order_id, amount_paid_usd=paid)
    return (f"Credited: refund_event_id={rid}, order_id={order_id}, fee_event_id={fee_event_id}, "
            f"credit_amount_usd={amount:.2f}, amount_paid_usd={paid:.2f}.")


@tool(owner="agent", rw="write")
def refund_late_change_fee_56da608d(ctx: ToolContext, order_id: str, fee_event_id: str,
                                    refund_amount_usd: float) -> str:
    """Books the late-change goodwill refund on a Northgate Scheduled Large-Item Delivery order: one refund of part or all of a late-change fee charged on the order, credited to the external payment card that paid it. The refund is recorded against that late-change fee with the reason fee refund, and the net amount paid on the order goes down by the refund. The customer sees the refund on the order and on the card at once. Only an order paid in full by an external card with no Northgate Cash or gift card redeemed on it is booked here; any other order is refused and nothing is recorded, its posting being made by a human representative.

    Args:
        order_id: Id class — the reference number of the Scheduled Large-Item Delivery order, read from the customer's order lookup.
        fee_event_id: Id class — the reference number of the late-change fee charged on that order that is refunded, read from the order's line and fee lookup.
        refund_amount_usd: Fixed-format class — the amount refunded on the late-change fee, in US dollars as a positive number with at most 2 decimal places, already rounded half up to the cent.

    Returns:
        A confirmation text containing: refund_event_id (the reference number of the refund, text), order_id (text), fee_event_id (the late-change fee refunded, text), refund_amount_usd (USD with 2 decimals) and amount_paid_usd (the order's net amount paid after the refund, USD with 2 decimals). A text starting with "Refunded" means the refund is booked; a text starting with "Error:" means nothing was booked.
    """
    order, err = _FeeRefund.check(ctx, order_id, fee_event_id, refund_amount_usd, "late_cancellation")
    if err:
        return err
    amount = _Money.cents(refund_amount_usd)
    rid = ctx.make_id("oev_", order_id, fee_event_id, "late_change_goodwill", amount)
    ctx.create("order_events", rid, order_event_id=rid, order_id=order_id, customer_id=order["customer_id"],
               event_type="order_refund_charge", event_date=ctx.now()[:10], original_event_id=fee_event_id,
               refund_reason="fee_refund", fee_type="late_cancellation", quantity=0, amount_usd=amount,
               line_number=0, payment_method_type="external_card",
               item_category="not_applicable", return_class="not_applicable")
    paid = _Money.cents(Decimal(str(order.get("amount_paid_usd") or 0)) - Decimal(str(amount)))
    ctx.update("order_holdings", order_id, amount_paid_usd=paid)
    return (f"Refunded: refund_event_id={rid}, order_id={order_id}, fee_event_id={fee_event_id}, "
            f"refund_amount_usd={amount:.2f}, amount_paid_usd={paid:.2f}.")


@tool(owner="agent", rw="write")
def credit_late_express_4845a2c0(ctx: ToolContext, order_id: str, fee_event_id: str, credit_amount_usd: float) -> str:
    """Books the late-express credit on a Northgate Same-Day Delivery express order: one refund of part or all of the order's express delivery fee, credited to the external payment card that paid the order. The refund is recorded against that express fee with the reason fee refund, and the net amount paid on the order goes down by the credit. The customer sees the credit on the order and on the card at once. Only an order paid in full by an external card with no Northgate Cash or gift card redeemed on it is booked here; any other order is refused and nothing is recorded, its posting being made by a human representative.

    Args:
        order_id: Id class — the reference number of the Same-Day Delivery order, read from the customer's order lookup.
        fee_event_id: Id class — the reference number of the express delivery fee charged on that order, read from the order's line and fee lookup.
        credit_amount_usd: Fixed-format class — the credit refunded on the express delivery fee, in US dollars as a positive number with at most 2 decimal places, already rounded half up to the cent.

    Returns:
        A confirmation text containing: refund_event_id (the reference number of the credit, text), order_id (text), fee_event_id (the express fee credited, text), credit_amount_usd (USD with 2 decimals) and amount_paid_usd (the order's net amount paid after the credit, USD with 2 decimals). A text starting with "Credited" means the credit is booked; a text starting with "Error:" means nothing was booked.
    """
    order, err = _FeeRefund.check(ctx, order_id, fee_event_id, credit_amount_usd, "express_delivery")
    if err:
        return err
    amount = _Money.cents(credit_amount_usd)
    rid = ctx.make_id("oev_", order_id, fee_event_id, "late_express", amount)
    ctx.create("order_events", rid, order_event_id=rid, order_id=order_id, customer_id=order["customer_id"],
               event_type="order_refund_charge", event_date=ctx.now()[:10], original_event_id=fee_event_id,
               refund_reason="fee_refund", fee_type="express_delivery", quantity=0, amount_usd=amount,
               line_number=0, payment_method_type="external_card",
               item_category="not_applicable", return_class="not_applicable")
    paid = _Money.cents(Decimal(str(order.get("amount_paid_usd") or 0)) - Decimal(str(amount)))
    ctx.update("order_holdings", order_id, amount_paid_usd=paid)
    return (f"Credited: refund_event_id={rid}, order_id={order_id}, fee_event_id={fee_event_id}, "
            f"credit_amount_usd={amount:.2f}, amount_paid_usd={paid:.2f}.")


class _ReturnNumber:
    """Builds the 12-digit return authorization number printed on the return receipt."""

    @staticmethod
    def build(row_id: str) -> str:
        digest = row_id.split("_", 1)[-1]
        return "4" + str(int(digest, 16) % 10 ** 11).zfill(11)


@tool(owner="user", rw="write")
def return_item_at_drive_up_b4cf62ab(ctx: ToolContext, order_id: str, original_event_id: str, quantity: int,
                                     return_reason: str, restocking_fee_usd: float,
                                     refund_amount_usd: float) -> str:
    """The customer, parked at a Northgate store's Drive Up, returns units of one line of their own Northgate order with the order as the receipt and confirms the refund. One call records the return of those units on the order line with a printed return authorization number, the restocking fee withheld and the merchandise refund, credits the refund to the external payment card that paid the order, and lowers the net amount paid on the order by the refund. The customer sees the return receipt and the refund at once. Only an order paid in full by an external card with no Northgate Cash or gift card redeemed on it is booked here; any other order is refused and nothing is recorded, its posting being made by a human representative.

    Args:
        order_id: Id class — the reference number of the customer's order the returned units belong to, read from the customer's order lookup.
        original_event_id: Id class — the reference number of the order line being returned, read from the order's line and fee lookup.
        quantity: Fixed-format class — the number of units of that line handed back, an integer in the format integer >= 0, and for a return at least 1.
        return_reason: Enum class — why the customer returns the units; exactly one of: "changed_mind" when the customer simply no longer wants an item that works and is as ordered; "defective" when the item does not work; "damaged_in_transit" when the item arrived damaged; "wrong_item" when the item delivered is not the item ordered; "not_as_described" when the item differs from its listing; "not_applicable" is the value kept for entries that are not returns and is refused here.
        restocking_fee_usd: Fixed-format class — the restocking fee withheld from this return, in US dollars as a non-negative number with at most 2 decimal places, already rounded half up to the cent; 0.00 when none is withheld.
        refund_amount_usd: Fixed-format class — the merchandise refund paid back for the returned units, in US dollars as a positive number with at most 2 decimal places, already rounded half up to the cent.

    Returns:
        A confirmation text containing: return_event_id (the reference number of the return, text), return_number (the 12-digit return authorization number printed on the receipt), order_id (text), original_event_id (text), quantity (units returned, whole number), restocking_fee_usd and refund_amount_usd (USD with 2 decimals) and amount_paid_usd (the order's net amount paid after the refund, USD with 2 decimals). A text starting with "Returned" means the return and refund are recorded; a text starting with "Error:" means nothing was recorded.
    """
    reasons = ("changed_mind", "defective", "damaged_in_transit", "wrong_item", "not_as_described")
    if return_reason not in reasons:
        return "Error: return_reason must be one of " + ", ".join(reasons) + "."
    if int(quantity) != quantity or int(quantity) < 1:
        return "Error: quantity must be a whole number of 1 or more."
    if float(refund_amount_usd) <= 0 or not _Money.is_cents(refund_amount_usd):
        return "Error: refund_amount_usd must be above zero with at most 2 decimal places."
    if float(restocking_fee_usd) < 0 or not _Money.is_cents(restocking_fee_usd):
        return "Error: restocking_fee_usd must be zero or above with at most 2 decimal places."
    orders = ctx.find("order_holdings", order_id=order_id)
    if not orders:
        return f"Error: no order {order_id}."
    lines = ctx.find("order_events", order_event_id=original_event_id, order_id=order_id, event_type="order_post_line")
    if not lines:
        return f"Error: {original_event_id} is not a line of order {order_id}."
    order = orders[0]
    refusal = _Tender.refusal(ctx, order)
    if refusal:
        return refusal
    refund = _Money.cents(refund_amount_usd)
    restock = _Money.cents(restocking_fee_usd)
    rid = ctx.make_id("oev_", order_id, original_event_id, int(quantity), return_reason, restock, refund)
    number = _ReturnNumber.build(rid)
    ctx.create("order_events", rid, order_event_id=rid, order_id=order_id, customer_id=order["customer_id"],
               event_type="order_return_line", event_date=ctx.now()[:10], original_event_id=original_event_id,
               return_number=number, quantity=int(quantity), amount_usd=refund, restocking_fee_usd=restock,
               return_method="drive_up", return_reason=return_reason, receipt_type="receipt",
               refund_method="original_payment", payment_method_type="external_card", line_number=0,
               item_category="not_applicable", return_class="not_applicable")
    paid = _Money.cents(Decimal(str(order.get("amount_paid_usd") or 0)) - Decimal(str(refund)))
    ctx.update("order_holdings", order_id, amount_paid_usd=paid)
    return (f"Returned: return_event_id={rid}, return_number={number}, order_id={order_id}, "
            f"original_event_id={original_event_id}, quantity={int(quantity)}, restocking_fee_usd={restock:.2f}, "
            f"refund_amount_usd={refund:.2f}, amount_paid_usd={paid:.2f}.")

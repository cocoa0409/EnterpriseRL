"""Hidden task tools of the order_returns_care difficulty (Tailwise Online and In-Store Orders).

Each tool performs one atomic booking on one retail order and is reached only through the
unlock -> call meta-tools, by the name an extended policy of order.extended.yaml gives as its
target_tool. No tool judges eligibility, timing, ownership or any prerequisite: every value it
books is decided by the agent from the published policy and the records, and passed in.
"""

from erlbench import ToolContext, tool


# Every field of a new order-history entry, at its empty value; each tool overrides what it books.
LEDGER_BLANK = {
    "line_number": 0, "sku": "", "item_description": "", "item_category": "none", "final_sale": False,
    "quantity": 0, "unit_price_usd": 0.0, "coupon_discount_usd": 0.0, "certificate_applied_usd": 0.0,
    "deduction_usd": 0.0, "amount_usd": 0.0, "fee_kind": "none", "original_event_id": "",
    "return_reason": "none", "rma_id": None, "refund_method": "none",
}


@tool(owner="agent", rw="write")
def refund_freight_service_failure_8da9af3d(ctx: ToolContext, order_id: str, original_event_id: str,
                                            amount_usd: float) -> dict:
    """Book a service-failure refund against the freight delivery fee of a Large Item Freight
    Delivery order whose paid redelivery appointment was not kept. One call adds one fee refund of
    kind freight to the order's history, referring to the freight fee charge, sends that amount back
    to the original payment, and lowers the net amount billed on the order by the same amount. The
    customer sees the refund on the order history and on the card used for the order. The receipt
    returned below, with its refund reference, confirms the refund was booked.

    Args:
        order_id: Id class — the order number of the freight order, as returned by the order lookup.
        original_event_id: Id class — the reference number of the order history entry that charged the freight fee on this order (fee kind freight), as returned by the order history lookup.
        amount_usd: Fixed-format class — the refund amount in USD, a positive number with 2 decimal places, already rounded to the cent; it is booked exactly as given.

    Returns:
        A dict with: refund_id (string, the reference number of the new fee refund entry);
        order_id (string, the order refunded); original_event_id (string, the freight fee charge
        refunded); fee_kind (string, always freight); amount_usd (number, USD with 2 decimal places,
        the amount refunded); refund_method (string, always original_payment); event_date (string,
        YYYY-MM-DD, the booking date); billed_total_usd (number, USD with 2 decimal places, the net
        amount billed on the order with this refund taken off). A returned refund_id means the refund is booked.
    """
    found = ctx.find("orders", order_id=order_id)
    order = found[0] if found else {}
    today = ctx.now()[:10]
    amount = round(float(amount_usd), 2)
    rid = ctx.make_id("ofr_", order_id, original_event_id, amount_usd)
    ctx.create("order_events", rid, **dict(LEDGER_BLANK, order_id=order_id, customer_id=order.get("customer_id", ""), event_date=today, order_event_id=rid, event_type="order_fee_refund",
        fee_kind="freight", original_event_id=original_event_id, amount_usd=amount,
        refund_method="original_payment"))
    billed = round(float(order.get("billed_total_usd") or 0) - float(amount_usd), 2)
    ctx.update("orders", order_id, billed_total_usd=billed)
    return {"refund_id": rid, "order_id": order_id, "original_event_id": original_event_id,
            "fee_kind": "freight", "amount_usd": amount, "refund_method": "original_payment",
            "event_date": today, "billed_total_usd": billed}


@tool(owner="user", rw="write")
def book_paid_freight_redelivery_0935dc22(ctx: ToolContext, order_id: str, amount_usd: float,
                                          appointment_date: str) -> dict:
    """The customer pays the rebooking fee for another delivery of their own Large Item Freight
    Delivery order and fixes the new delivery appointment. One call charges the fee to the card on
    file as a redelivery fee entry on the order's history, raises the net amount billed on the order
    by that fee, and records the chosen appointment date as the order's promised date. The customer
    sees the charge on the order history and the new delivery date on the order. The receipt returned
    below, with its charge reference, confirms the redelivery is booked and paid.

    Args:
        order_id: Id class — the order number of the customer's freight order, as the care agent reads it from the order lookup and hands it over.
        amount_usd: Fixed-format class — the rebooking fee the customer pays, in USD, a positive number with 2 decimal places, already rounded to the cent; it is charged exactly as given.
        appointment_date: Fixed-format class — the new delivery appointment date the customer chooses, written YYYY-MM-DD (calendar date, store local time zone).

    Returns:
        A dict with: charge_id (string, the reference number of the new redelivery fee entry);
        order_id (string, the order charged); fee_kind (string, always redelivery); amount_usd
        (number, USD with 2 decimal places, the fee charged); event_date (string, YYYY-MM-DD, the
        charge date); promised_date (string, YYYY-MM-DD, the booked appointment now on the order);
        billed_total_usd (number, USD with 2 decimal places, the net amount billed on the order with
        this charge added). A returned charge_id means the redelivery is booked and paid.
    """
    found = ctx.find("orders", order_id=order_id)
    order = found[0] if found else {}
    today = ctx.now()[:10]
    amount = round(float(amount_usd), 2)
    rid = ctx.make_id("ofc_", order_id, amount_usd, appointment_date)
    ctx.create("order_events", rid, **dict(LEDGER_BLANK, order_id=order_id, customer_id=order.get("customer_id", ""), event_date=today, order_event_id=rid, event_type="order_fee_charge",
        fee_kind="redelivery", amount_usd=amount))
    billed = round(float(order.get("billed_total_usd") or 0) + float(amount_usd), 2)
    ctx.update("orders", order_id, promised_date=str(appointment_date), billed_total_usd=billed)
    return {"charge_id": rid, "order_id": order_id, "fee_kind": "redelivery", "amount_usd": amount,
            "event_date": today, "promised_date": str(appointment_date), "billed_total_usd": billed}


@tool(owner="agent", rw="write")
def refund_error_return_9d87fcb3(ctx: ToolContext, order_id: str, original_event_id: str, rma_id: str,
                                 quantity: int, return_reason: str, amount_usd: float) -> dict:
    """Refund an item that came back to Tailwise under a return authorization. One call adds one
    return refund entry to the order's history for the returned line and the authorization it
    settles, with no fee withheld, sends the amount to the original payment, marks that return
    authorization as refunded, and lowers the net amount billed on the order by the amount. The
    customer sees the refund on the order history and the authorization shown as refunded. The
    receipt returned below, with its refund reference, confirms the refund was booked.

    Args:
        order_id: Id class — the order number the returned item belongs to, as returned by the order lookup.
        original_event_id: Id class — the reference number of the order history entry that charged the returned line, as returned by the order history or return authorization lookup.
        rma_id: Id class — the return authorization number being settled, as returned by the return authorization lookup.
        quantity: Fixed-format class — the units refunded, an integer count of units, at least 1.
        return_reason: Enum class — the reason recorded on the refund, copied from the return authorization: none (not used for a return refund; reserved for rows without a reason), changed_mind (the customer no longer wanted the item), damaged (the item arrived damaged), defective (the item does not work as it should), wrong_item (a different item was sent than the one ordered), not_as_described (the item differs from its listing, such as color, size or material), quality_guarantee (opened food or treats returned under the satisfaction guarantee), missing (not used for a return refund; an item that never arrived).
        amount_usd: Fixed-format class — the refund amount in USD, a positive number with 2 decimal places, already rounded to the cent; it is booked exactly as given.

    Returns:
        A dict with: refund_id (string, the reference number of the new return refund entry);
        order_id (string); original_event_id (string, the line refunded); rma_id (string, the
        authorization settled); quantity (integer, units refunded); return_reason (string);
        amount_usd (number, USD with 2 decimal places, the amount refunded); deduction_usd (number,
        USD with 2 decimal places, always 0.00 withheld); refund_method (string, always
        original_payment); rma_status (string, always refunded); event_date (string, YYYY-MM-DD, the
        booking date); billed_total_usd (number, USD with 2 decimal places, the net amount billed on
        the order with this refund taken off). A returned refund_id means the refund is booked.
    """
    found = ctx.find("orders", order_id=order_id)
    order = found[0] if found else {}
    today = ctx.now()[:10]
    amount = round(float(amount_usd), 2)
    rid = ctx.make_id("orr_", order_id, original_event_id, rma_id, quantity, return_reason, amount_usd)
    ctx.create("order_events", rid, **dict(LEDGER_BLANK, order_id=order_id, customer_id=order.get("customer_id", ""), event_date=today, order_event_id=rid, event_type="order_return_refund",
        original_event_id=original_event_id, rma_id=rma_id, quantity=int(quantity),
        return_reason=return_reason, deduction_usd=0.0, amount_usd=amount, refund_method="original_payment"))
    ctx.update("order_return_requests", rma_id, status="refunded")
    billed = round(float(order.get("billed_total_usd") or 0) - float(amount_usd), 2)
    ctx.update("orders", order_id, billed_total_usd=billed)
    return {"refund_id": rid, "order_id": order_id, "original_event_id": original_event_id, "rma_id": rma_id,
            "quantity": int(quantity), "return_reason": return_reason, "amount_usd": amount,
            "deduction_usd": 0.0, "refund_method": "original_payment", "rma_status": "refunded",
            "event_date": today, "billed_total_usd": billed}


@tool(owner="user", rw="write")
def accept_returnless_damage_refund_2d82d69e(ctx: ToolContext, order_id: str, original_event_id: str,
                                             quantity: int, amount_usd: float) -> dict:
    """The customer takes a refund, instead of a free replacement, for units of their own order that
    arrived damaged and stay with them. One call adds one damage credit entry with reason damaged to
    the order's history for the damaged line, sends the amount to the original payment without the
    item coming back, and lowers the net amount billed on the order by the amount. The customer sees
    the credit on the order history and on the card used for the order. The receipt returned below,
    with its credit reference, confirms the credit was booked.

    Args:
        order_id: Id class — the order number of the customer's order, as the care agent reads it from the order lookup and hands it over.
        original_event_id: Id class — the reference number of the order history entry that charged the damaged line, as the care agent reads it from the order history lookup and hands it over.
        quantity: Fixed-format class — the damaged units credited, an integer count of units, at least 1.
        amount_usd: Fixed-format class — the credit amount in USD, a positive number with 2 decimal places, already rounded to the cent; it is booked exactly as given.

    Returns:
        A dict with: credit_id (string, the reference number of the new damage credit entry);
        order_id (string); original_event_id (string, the line credited); quantity (integer, units
        credited); return_reason (string, always damaged); amount_usd (number, USD with 2 decimal
        places, the amount credited); refund_method (string, always original_payment); event_date
        (string, YYYY-MM-DD, the booking date); billed_total_usd (number, USD with 2 decimal places,
        the net amount billed on the order with this credit taken off). A returned credit_id means the credit is
        booked.
    """
    found = ctx.find("orders", order_id=order_id)
    order = found[0] if found else {}
    today = ctx.now()[:10]
    amount = round(float(amount_usd), 2)
    rid = ctx.make_id("odc_", order_id, original_event_id, quantity, amount_usd)
    ctx.create("order_events", rid, **dict(LEDGER_BLANK, order_id=order_id, customer_id=order.get("customer_id", ""), event_date=today, order_event_id=rid, event_type="order_damage_credit",
        original_event_id=original_event_id, quantity=int(quantity), return_reason="damaged",
        amount_usd=amount, refund_method="original_payment"))
    billed = round(float(order.get("billed_total_usd") or 0) - float(amount_usd), 2)
    ctx.update("orders", order_id, billed_total_usd=billed)
    return {"credit_id": rid, "order_id": order_id, "original_event_id": original_event_id,
            "quantity": int(quantity), "return_reason": "damaged", "amount_usd": amount,
            "refund_method": "original_payment", "event_date": today, "billed_total_usd": billed}


@tool(owner="agent", rw="write")
def refund_order_fulfillment_fee_03b15c6d(ctx: ToolContext, order_id: str, original_event_id: str,
                                          fee_kind: str, amount_usd: float) -> dict:
    """Refund all or part of the fulfillment fee charged on a retail order. One call adds one fee
    refund entry to the order's history, referring to the fee charge it refunds, sends the amount to
    the original payment, and lowers the net amount billed on the order by the amount. The customer
    sees the refund on the order history and on the card used for the order. The receipt returned
    below, with its refund reference, confirms the refund was booked.

    Args:
        order_id: Id class — the order number, as returned by the order lookup.
        original_event_id: Id class — the reference number of the order history entry that charged the fulfillment fee being refunded, as returned by the order history lookup.
        fee_kind: Enum class — the kind of the fee refunded, copied from the fee charge being refunded: none (no fee; not used for a refund), shipping (the standard ship-to-home fee), expedited (the expedited ship-to-home fee), same_day_delivery (the same-day delivery fee), freight (the large-item freight delivery fee), redelivery (a fee paid for another freight delivery attempt).
        amount_usd: Fixed-format class — the refund amount in USD, a positive number with 2 decimal places, already rounded to the cent; it is booked exactly as given.

    Returns:
        A dict with: refund_id (string, the reference number of the new fee refund entry);
        order_id (string); original_event_id (string, the fee charge refunded); fee_kind (string);
        amount_usd (number, USD with 2 decimal places, the amount refunded); refund_method (string,
        always original_payment); event_date (string, YYYY-MM-DD, the booking date); billed_total_usd
        (number, USD with 2 decimal places, the net amount billed on the order with this refund taken off). A
        returned refund_id means the refund is booked.
    """
    found = ctx.find("orders", order_id=order_id)
    order = found[0] if found else {}
    today = ctx.now()[:10]
    amount = round(float(amount_usd), 2)
    rid = ctx.make_id("off_", order_id, original_event_id, fee_kind, amount_usd)
    ctx.create("order_events", rid, **dict(LEDGER_BLANK, order_id=order_id, customer_id=order.get("customer_id", ""), event_date=today, order_event_id=rid, event_type="order_fee_refund",
        fee_kind=fee_kind, original_event_id=original_event_id, amount_usd=amount,
        refund_method="original_payment"))
    billed = round(float(order.get("billed_total_usd") or 0) - float(amount_usd), 2)
    ctx.update("orders", order_id, billed_total_usd=billed)
    return {"refund_id": rid, "order_id": order_id, "original_event_id": original_event_id,
            "fee_kind": fee_kind, "amount_usd": amount, "refund_method": "original_payment",
            "event_date": today, "billed_total_usd": billed}

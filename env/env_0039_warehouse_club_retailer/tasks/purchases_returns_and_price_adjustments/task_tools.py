"""Hidden task tools of the purchases_returns_and_price_adjustments difficulty (Northgate Purchases & Returns).

Each tool performs one atomic posting on one purchase. No tool checks an eligibility, a prerequisite or a
policy amount: the value it books is the value it is given.
"""

from erlbench import ToolContext, tool


@tool(owner="agent", rw="write")
def invoice_route_pickup_fee_16b23a12(ctx: ToolContext, order_id: str, source_order_line_id: str,
                                      route_pickup_fee: float) -> str:
    """Invoice the route pickup fee on a business member's purchase: member services books, against the sale
    line whose merchandise the freight crew will collect, one return pickup fee entry for the amount given,
    dated today, and raises the purchase's net paid amount by that amount. The invoice appears in the
    purchase's line history as a return pickup fee pointing at that sale line. A receipt carrying the new fee
    entry's reference number means the fee is now standing on the purchase.

    Args:
        order_id: Id class — the purchase reference number of the business member's purchase the fee is
            invoiced on, read from the purchase lookup before the call.
        source_order_line_id: Id class — the reference number of the sale line the freight crew will collect,
            read from the return authorization (its sale line) or from the purchase line lookup before the call.
        route_pickup_fee: Fixed-format class — the route pickup fee to invoice, in USD, a positive amount with
            2 decimal places (cents); a value with more decimals is rounded half up to 2 decimal places at
            booking.

    Returns:
        A dictionary receipt: fee_entry_id (the reference number of the new fee entry, text), fee_type (always
        return_pickup_fee), amount (the invoiced fee in USD, 2 decimal places), event_date (the booking date,
        YYYY-MM-DD) and net_paid_amount (the purchase's net paid amount after the invoice, USD, 2 decimal
        places). The presence of fee_entry_id indicates the invoice was booked.
    """
    amount = round(float(route_pickup_fee), 2)
    holding = (ctx.find("order_holdings", order_id=order_id) or [{}])[0]
    today = ctx.now()[:10]
    rid = ctx.make_id("rpf_", order_id, source_order_line_id, amount)
    ctx.create("order_lines", rid, order_line_id=rid, order_id=order_id,
               customer_id=holding.get("customer_id", ""), event_type="order_fee_charged",
               item_number="", item_description="", merchandise_class="not_applicable", quantity=1,
               unit_price=amount, line_amount=amount, event_date=today,
               source_order_line_id=source_order_line_id, return_reason="not_applicable",
               adjustment_type="not_applicable", fee_type="return_pickup_fee", item_price_id="",
               reward_eligible=False)
    net_paid = round(float(holding.get("net_paid_amount") or 0) + amount, 2)
    ctx.update("order_holdings", order_id, net_paid_amount=net_paid)
    return str({"fee_entry_id": rid, "fee_type": "return_pickup_fee", "amount": amount, "event_date": today,
                "net_paid_amount": net_paid})


@tool(owner="user", rw="write")
def confirm_business_return_92c81b09(ctx: ToolContext, return_authorization_id: str, order_id: str,
                                     source_order_line_id: str, restocking_fee: float) -> str:
    """The business member confirms their own submitted return authorization for a freight pickup and accepts
    the restocking charge on it: the authorization changes from submitted to confirmed, one restocking fee
    entry for the amount given is booked today against the sale line being returned, and the purchase's net
    paid amount rises by that amount. Afterwards the authorization shows confirmed and the purchase's line
    history shows the restocking fee. A receipt carrying the authorization's new status and the fee entry's
    reference number means the confirmation went through.

    Args:
        return_authorization_id: Id class — the reference number of the member's submitted return
            authorization, read from the return authorization lookup and handed over by the representative.
        order_id: Id class — the purchase reference number the authorization belongs to, read from the purchase
            or return authorization lookup and handed over by the representative.
        source_order_line_id: Id class — the reference number of the sale line the authorization covers, read
            from the return authorization (its sale line) and handed over by the representative.
        restocking_fee: Fixed-format class — the restocking charge the member accepts, in USD, a non-negative
            amount with 2 decimal places (cents) as quoted by the representative; a value with more decimals is
            rounded half up to 2 decimal places at booking.

    Returns:
        A dictionary receipt: return_authorization_id (the authorization confirmed, text), authorization_status
        (always confirmed), fee_entry_id (the reference number of the new restocking fee entry, text), amount
        (the restocking charge booked in USD, 2 decimal places), event_date (the booking date, YYYY-MM-DD) and
        net_paid_amount (the purchase's net paid amount afterwards, USD, 2 decimal places). An
        authorization_status of confirmed indicates success.
    """
    ctx.update("order_return_authorizations", return_authorization_id, status="confirmed")
    amount = round(float(restocking_fee), 2)
    holding = (ctx.find("order_holdings", order_id=order_id) or [{}])[0]
    today = ctx.now()[:10]
    rid = ctx.make_id("rsf_", return_authorization_id, order_id, source_order_line_id, amount)
    ctx.create("order_lines", rid, order_line_id=rid, order_id=order_id,
               customer_id=holding.get("customer_id", ""), event_type="order_fee_charged",
               item_number="", item_description="", merchandise_class="not_applicable", quantity=1,
               unit_price=amount, line_amount=amount, event_date=today,
               source_order_line_id=source_order_line_id, return_reason="not_applicable",
               adjustment_type="not_applicable", fee_type="restocking_fee", item_price_id="",
               reward_eligible=False)
    net_paid = round(float(holding.get("net_paid_amount") or 0) + amount, 2)
    ctx.update("order_holdings", order_id, net_paid_amount=net_paid)
    return str({"return_authorization_id": return_authorization_id, "authorization_status": "confirmed",
                "fee_entry_id": rid, "amount": amount, "event_date": today, "net_paid_amount": net_paid})


@tool(owner="agent", rw="write")
def post_changed_mind_refund_b29df74c(ctx: ToolContext, order_id: str, membership_id: str, source_order_line_id: str,
                                      quantity: int, refund_amount: float, purchase_status_after: str) -> str:
    """Post a changed-mind refund on a purchase: member services books, against the sale line given, one refund
    entry for the units and the total amount given, with return reason changed_mind, dated today; the entry
    copies the sale line's item number, merchandise class and reward flag. The purchase's net paid amount falls
    by the refunded amount and the purchase takes the status given (and today's closing date when it becomes fully
    returned). Afterwards the refund shows in the purchase's line history and the money goes back to the
    purchase's tender. A receipt carrying the new refund entry's reference number means the refund was posted.

    Args:
        order_id: Id class — the purchase reference number the refund is posted on, read from the purchase lookup
            before the call.
        membership_id: Id class — the reference number of the membership presented on that purchase, read from
            the purchase lookup (its membership) before the call.
        source_order_line_id: Id class — the reference number of the sale line whose units are refunded, read
            from the received return authorization (its sale line) before the call.
        quantity: Fixed-format class — the number of units refunded, a positive integer.
        refund_amount: Fixed-format class — the total refund for those units, in USD, a positive amount with 2
            decimal places (cents); a value with more decimals is rounded half up to 2 decimal places at booking.
        purchase_status_after: Enum class — the purchase's status once this refund is posted:
            partially_returned when at least one unit sold on the purchase is still not refunded after this
            refund; fully_returned when no unit sold on the purchase remains unrefunded after this refund.

    Returns:
        A dictionary receipt: refund_entry_id (the reference number of the new refund entry, text), quantity
        (units refunded, integer), refund_amount (USD, 2 decimal places), event_date (YYYY-MM-DD),
        net_paid_amount (the purchase's net paid amount afterwards, USD, 2 decimal places) and purchase_status
        (the purchase's status afterwards). The presence of refund_entry_id indicates the refund was posted.
    """
    amount = round(float(refund_amount), 2)
    units = int(quantity)
    sale = (ctx.find("order_lines", order_line_id=source_order_line_id) or [{}])[0]
    holding = (ctx.find("order_holdings", order_id=order_id) or [{}])[0]
    today = ctx.now()[:10]
    rid = ctx.make_id("cmr_", order_id, membership_id, source_order_line_id, units, amount, purchase_status_after)
    ctx.create("order_lines", rid, order_line_id=rid, order_id=order_id, customer_id=holding.get("customer_id", ""),
               event_type="order_line_returned", item_number=sale.get("item_number", ""),
               item_description=sale.get("item_description", ""),
               merchandise_class=sale.get("merchandise_class", "not_applicable"), quantity=units,
               unit_price=round(amount / units, 2) if units else amount, line_amount=amount, event_date=today,
               source_order_line_id=source_order_line_id, return_reason="changed_mind",
               adjustment_type="not_applicable", fee_type="not_applicable", item_price_id="",
               reward_eligible=False)
    net_paid = round(float(holding.get("net_paid_amount") or 0) - amount, 2)
    fields = {"net_paid_amount": net_paid, "status": purchase_status_after}
    if purchase_status_after == "fully_returned":
        fields["closed_date"] = today
    ctx.update("order_holdings", order_id, **fields)
    return str({"refund_entry_id": rid, "quantity": units, "refund_amount": amount, "event_date": today,
                "net_paid_amount": net_paid, "purchase_status": purchase_status_after})


@tool(owner="agent", rw="write")
def charge_restocking_fee_79f2f340(ctx: ToolContext, order_id: str, source_order_line_id: str,
                                   restocking_fee: float) -> str:
    """Charge a restocking fee on a purchase: member services books, against the refunded sale line given, one
    restocking fee entry for the amount given, dated today, and raises the purchase's net paid amount by that
    amount. The fee appears in the purchase's line history pointing at that sale line. A receipt carrying the new
    fee entry's reference number means the fee is now standing on the purchase.

    Args:
        order_id: Id class — the purchase reference number the fee is charged on, read from the purchase lookup
            before the call.
        source_order_line_id: Id class — the reference number of the sale line the returned units came from, read
            from the received return authorization (its sale line) before the call.
        restocking_fee: Fixed-format class — the restocking fee to charge, in USD, a positive amount with 2 decimal
            places (cents); a value with more decimals is rounded half up to 2 decimal places at booking.

    Returns:
        A dictionary receipt: fee_entry_id (the reference number of the new fee entry, text), fee_type (always
        restocking_fee), amount (USD, 2 decimal places), event_date (YYYY-MM-DD) and net_paid_amount (the
        purchase's net paid amount afterwards, USD, 2 decimal places). The presence of fee_entry_id indicates the
        fee was booked.
    """
    amount = round(float(restocking_fee), 2)
    holding = (ctx.find("order_holdings", order_id=order_id) or [{}])[0]
    today = ctx.now()[:10]
    rid = ctx.make_id("crf_", order_id, source_order_line_id, amount)
    ctx.create("order_lines", rid, order_line_id=rid, order_id=order_id, customer_id=holding.get("customer_id", ""),
               event_type="order_fee_charged", item_number="", item_description="",
               merchandise_class="not_applicable", quantity=1, unit_price=amount, line_amount=amount,
               event_date=today, source_order_line_id=source_order_line_id, return_reason="not_applicable",
               adjustment_type="not_applicable", fee_type="restocking_fee", item_price_id="", reward_eligible=False)
    net_paid = round(float(holding.get("net_paid_amount") or 0) + amount, 2)
    ctx.update("order_holdings", order_id, net_paid_amount=net_paid)
    return str({"fee_entry_id": rid, "fee_type": "restocking_fee", "amount": amount, "event_date": today,
                "net_paid_amount": net_paid})


@tool(owner="user", rw="write")
def confirm_freight_pickup_4c90eb99(ctx: ToolContext, return_authorization_id: str, order_id: str,
                                    source_order_line_id: str, pickup_fee: float) -> str:
    """The member confirms their own submitted freight-pickup return authorization and pays the pickup fee for it:
    the authorization changes from submitted to confirmed, one return pickup fee entry for the amount given is
    booked today against the sale line being picked up, and the purchase's net paid amount rises by that amount.
    Afterwards the authorization shows confirmed (the crew is then scheduled) and the purchase's line history
    shows the pickup fee. A receipt carrying the authorization's new status and the fee entry's reference number
    means the confirmation went through.

    Args:
        return_authorization_id: Id class — the reference number of the member's submitted return authorization,
            read from the return authorization lookup and handed over by the representative.
        order_id: Id class — the purchase reference number the authorization belongs to, read from the purchase or
            return authorization lookup and handed over by the representative.
        source_order_line_id: Id class — the reference number of the sale line the authorization covers, read from
            the return authorization (its sale line) and handed over by the representative.
        pickup_fee: Fixed-format class — the pickup fee the member pays, in USD, a non-negative amount with 2
            decimal places (cents) as quoted by the representative; a value with more decimals is rounded half up
            to 2 decimal places at booking.

    Returns:
        A dictionary receipt: return_authorization_id (the authorization confirmed, text), authorization_status
        (always confirmed), fee_entry_id (the reference number of the new pickup fee entry, text), amount (USD, 2
        decimal places), event_date (YYYY-MM-DD) and net_paid_amount (the purchase's net paid amount afterwards,
        USD, 2 decimal places). An authorization_status of confirmed indicates success.
    """
    ctx.update("order_return_authorizations", return_authorization_id, status="confirmed")
    amount = round(float(pickup_fee), 2)
    holding = (ctx.find("order_holdings", order_id=order_id) or [{}])[0]
    today = ctx.now()[:10]
    rid = ctx.make_id("mpf_", return_authorization_id, order_id, source_order_line_id, amount)
    ctx.create("order_lines", rid, order_line_id=rid, order_id=order_id, customer_id=holding.get("customer_id", ""),
               event_type="order_fee_charged", item_number="", item_description="",
               merchandise_class="not_applicable", quantity=1, unit_price=amount, line_amount=amount,
               event_date=today, source_order_line_id=source_order_line_id, return_reason="not_applicable",
               adjustment_type="not_applicable", fee_type="return_pickup_fee", item_price_id="", reward_eligible=False)
    net_paid = round(float(holding.get("net_paid_amount") or 0) + amount, 2)
    ctx.update("order_holdings", order_id, net_paid_amount=net_paid)
    return str({"return_authorization_id": return_authorization_id, "authorization_status": "confirmed",
                "fee_entry_id": rid, "amount": amount, "event_date": today, "net_paid_amount": net_paid})

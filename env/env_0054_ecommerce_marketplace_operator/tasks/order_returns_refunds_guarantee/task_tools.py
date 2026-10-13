"""Hidden task tools of the order_returns_refunds_guarantee difficulty (Marketplace Orders).

Each tool performs one atomic write on one marketplace order; none of them checks an
eligibility, a deadline, an existing booking or any other business condition, and none of
them computes an amount: every value it books is passed in exactly as given.
"""

from erlbench import ToolContext, tool


@tool(owner="agent", rw="write")
def book_late_delivery_compensation_7d003665(ctx: ToolContext, order_id: str, return_id: str,
                                             refund_component: str, amount: float) -> str:
    """Book a Northloop-funded refund to the buyer on one marketplace order as compensation for a
    late delivery. One call records one refund entry dated today on that order, sent back to the
    original payment method, funded by Northloop and carrying no restocking fee, no return shipping
    fee and no late-return deduction, and lowers the order's net amount paid by the amount booked.
    The buyer sees the refund on the order's activity immediately; the receipt below confirms it.

    Args:
        order_id: Id class — the marketplace order number of the order being compensated, as shown by the order lookup.
        return_id: Id class — the return number the refund settles, read from the order activity lookup; pass "" (empty) when the refund settles no return, as is the case for a late-delivery refund.
        refund_component: Enum class — which component of the order the refund entry covers, exactly one of: item when the refund pays back the item price of units; original_shipping when it pays back the shipping charged at checkout; tax when it pays back sales tax; late_delivery_shipping when it is the compensation owed because a guaranteed delivery arrived later than its promised date.
        amount: Fixed-format class — the refund amount in USD, a positive number with 2 decimal places, rounded half up to the cent; it is booked exactly as given.

    Returns:
        A text rendering of a dictionary with these fields: status — the literal "booked" when the
        refund entry was recorded; order_event_id — the reference of the new refund entry (text);
        order_id — the order refunded; refund_component — the component recorded; amount — the USD
        amount booked with 2 decimal places; funded_by — the literal "northloop"; net_paid_amount —
        the order's net amount paid including this refund, USD with 2 decimal places; event_date — the
        booking date as YYYY-MM-DD.
    """
    amount = round(float(amount), 2)
    rows = ctx.find("order_orders", order_id=order_id)
    order = rows[0] if rows else {}
    rid = ctx.make_id("ore_", order_id, return_id, refund_component, amount)
    ctx.create("order_events", rid, order_event_id=rid, order_id=order_id,
               customer_id=order.get("customer_id", ""), event_type="order_refund",
               event_date=ctx.now()[:10], amount=amount, refund_component=refund_component,
               return_id=return_id, refund_quantity=0, funded_by="northloop",
               refund_destination="original_payment", restocking_fee_amount=0.0,
               return_shipping_fee_amount=0.0, late_return_deduction_amount=0.0)
    net = round(float(order.get("net_paid_amount") or 0) - amount, 2)
    ctx.update("order_orders", order_id, net_paid_amount=net)
    return str({"status": "booked", "order_event_id": rid, "order_id": order_id,
                "refund_component": refund_component, "amount": amount, "funded_by": "northloop",
                "net_paid_amount": net, "event_date": ctx.now()[:10]})


@tool(owner="user", rw="write")
def file_guarantee_claim_a9e31314(ctx: ToolContext, order_id: str, claim_reason: str,
                                  claim_amount: float) -> str:
    """The buyer files a Northloop Guarantee claim on one of their own marketplace orders. One call
    records one claim dated today on that order with the reason and the amount the buyer claims, and
    issues a claim number; nothing is paid by filing. The buyer sees the open claim on the order and
    can quote the claim number from the receipt below.

    Args:
        order_id: Id class — the marketplace order number the claim is filed on, as given to the buyer by the support agent from the order lookup.
        claim_reason: Enum class — the reason of the claim, exactly one of: item_not_received when the package never arrived; not_as_described when the item delivered differs materially from the listing; damaged_item when the item arrived damaged or defective and a return has been opened on the order; return_not_refunded when a returned item was received back but its refund was never issued.
        claim_amount: Fixed-format class — the amount the buyer claims in USD, a positive number with 2 decimal places, rounded half up to the cent; it is recorded exactly as given.

    Returns:
        A text rendering of a dictionary with these fields: status — the literal "filed" when the claim
        was recorded; claim_id — the claim number issued (text), which identifies the claim from
        now on; order_id — the order claimed on; claim_reason — the reason recorded; claim_amount — the
        USD amount claimed with 2 decimal places; event_date — the filing date as YYYY-MM-DD.
    """
    claim_amount = round(float(claim_amount), 2)
    rows = ctx.find("order_orders", order_id=order_id)
    order = rows[0] if rows else {}
    cid = ctx.make_id("clm_", order_id, claim_reason, claim_amount)
    rid = ctx.make_id("ocf_", cid)
    ctx.create("order_events", rid, order_event_id=rid, order_id=order_id,
               customer_id=order.get("customer_id", ""), event_type="order_claim_file",
               event_date=ctx.now()[:10], amount=0.0, claim_id=cid, claim_reason=claim_reason,
               claim_amount=claim_amount)
    return str({"status": "filed", "claim_id": cid, "order_id": order_id, "claim_reason": claim_reason,
                "claim_amount": claim_amount, "event_date": ctx.now()[:10]})


@tool(owner="agent", rw="write")
def decide_guarantee_claim_becc0a68(ctx: ToolContext, order_id: str, claim_id: str,
                                    claim_decision: str, amount: float) -> str:
    """Record Northloop's decision on a Northloop Guarantee claim, or on the single appeal against
    that decision, on a Northloop-fulfilled order, where Northloop bears whatever is granted. One call records one decision entry dated today
    for the claim, with the decision and the amount granted, funded by Northloop. The buyer sees the
    decision and the granted amount on the claim; the receipt below confirms it.

    Args:
        order_id: Id class — the marketplace order number the claim was filed on, read from the order lookup.
        claim_id: Id class — the claim number of the Northloop Guarantee claim being decided, read from the filing receipt or from the order activity lookup.
        claim_decision: Enum class — the decision stage and outcome, exactly one of: granted when the claim is upheld and an amount is paid; denied when the claim is refused and nothing is paid; appeal_granted when an appeal against a recorded decision on the claim is upheld; appeal_denied when an appeal against a recorded decision on the claim is refused.
        amount: Fixed-format class — the amount granted in USD with 2 decimal places, rounded half up to the cent; 0.00 for a refusal; it is recorded exactly as given.

    Returns:
        A text rendering of a dictionary with these fields: status — the literal "decided" when the
        decision was recorded; order_event_id — the reference of the decision entry (text); claim_id —
        the claim decided; claim_decision — the decision recorded; amount — the USD amount granted
        with 2 decimal places; funded_by — the literal "northloop"; event_date — the decision date as
        YYYY-MM-DD.
    """
    amount = round(float(amount), 2)
    rows = ctx.find("order_orders", order_id=order_id)
    order = rows[0] if rows else {}
    rid = ctx.make_id("ogd_", order_id, claim_id, claim_decision, amount)
    ctx.create("order_events", rid, order_event_id=rid, order_id=order_id,
               customer_id=order.get("customer_id", ""), event_type="order_guarantee_decision",
               event_date=ctx.now()[:10], amount=amount, claim_id=claim_id,
               claim_decision=claim_decision, funded_by="northloop")
    return str({"status": "decided", "order_event_id": rid, "claim_id": claim_id,
                "claim_decision": claim_decision, "amount": amount, "funded_by": "northloop",
                "event_date": ctx.now()[:10]})


@tool(owner="user", rw="write")
def pay_replacement_charge_b3f7fc80(ctx: ToolContext, order_id: str, return_id: str, amount: float) -> str:
    """The buyer pays, from the card on file, the charge owed on one of their own marketplace orders
    for a replacement whose original unit was not sent back in time. One call records one payment
    capture dated today on that order, marked as an unreturned-replacement charge and tied to the
    return the replacement was shipped against, and raises the order's net amount paid by the amount
    paid. The buyer sees the payment on the order immediately; the receipt below confirms it.

    Args:
        order_id: Id class — the marketplace order number the replacement was shipped for, as given to the buyer by the support agent from the order lookup.
        return_id: Id class — the return number of the original unit the replacement was shipped against, as given to the buyer by the support agent from the order activity lookup.
        amount: Fixed-format class — the amount paid in USD, a positive number with 2 decimal places, rounded half up to the cent; it is captured exactly as given.

    Returns:
        A text rendering of a dictionary with these fields: status — the literal "paid" when the
        payment was captured; order_event_id — the reference of the payment entry (text); order_id —
        the order paid on; return_id — the return the payment relates to; amount — the USD amount
        captured with 2 decimal places; net_paid_amount — the order's net amount paid including
        this payment, USD with 2 decimal places; event_date — the payment date as YYYY-MM-DD.
    """
    amount = round(float(amount), 2)
    rows = ctx.find("order_orders", order_id=order_id)
    order = rows[0] if rows else {}
    rid = ctx.make_id("orc_", order_id, return_id, amount)
    ctx.create("order_events", rid, order_event_id=rid, order_id=order_id,
               customer_id=order.get("customer_id", ""), event_type="order_charge",
               event_date=ctx.now()[:10], amount=amount, charge_reason="unreturned_replacement_item",
               return_id=return_id)
    net = round(float(order.get("net_paid_amount") or 0) + amount, 2)
    ctx.update("order_orders", order_id, net_paid_amount=net)
    return str({"status": "paid", "order_event_id": rid, "order_id": order_id, "return_id": return_id,
                "amount": amount, "net_paid_amount": net, "event_date": ctx.now()[:10]})


@tool(owner="agent", rw="write")
def refund_replacement_charge_bf6a8eb8(ctx: ToolContext, order_id: str, return_id: str,
                                       refund_component: str, amount: float) -> str:
    """Refund to the buyer, from Northloop, part or all of a replacement charge collected on one
    marketplace order, where the original unit of that replacement has come back. One call records one
    refund entry dated today on that order, tied to the return of the original unit, funded by
    Northloop and sent to the original payment method, and lowers the order's net amount paid by the
    amount refunded. The buyer sees the refund on the order's activity immediately; the receipt below
    confirms it.

    Args:
        order_id: Id class — the marketplace order number the replacement charge was collected on, read from the order lookup.
        return_id: Id class — the return number of the original unit that came back, read from the order activity lookup.
        refund_component: Enum class — which component of the order the refund entry covers, exactly one of: item when the refund pays back money collected for units of the item; original_shipping when it pays back the shipping charged at checkout; tax when it pays back sales tax; late_delivery_shipping when it is the compensation owed because a guaranteed delivery arrived later than its promised date.
        amount: Fixed-format class — the refund amount in USD, a positive number with 2 decimal places, rounded half up to the cent; it is booked exactly as given.

    Returns:
        A text rendering of a dictionary with these fields: status — the literal "refunded" when the
        refund entry was recorded; order_event_id — the reference of the refund entry (text); order_id —
        the order refunded; return_id — the return the refund settles; refund_component — the
        component recorded; amount — the USD amount refunded with 2 decimal places; funded_by — the
        literal "northloop"; net_paid_amount — the order's net amount paid including this refund, USD with
        2 decimal places; event_date — the refund date as YYYY-MM-DD.
    """
    amount = round(float(amount), 2)
    rows = ctx.find("order_orders", order_id=order_id)
    order = rows[0] if rows else {}
    rid = ctx.make_id("orr_", order_id, return_id, refund_component, amount)
    ctx.create("order_events", rid, order_event_id=rid, order_id=order_id,
               customer_id=order.get("customer_id", ""), event_type="order_refund",
               event_date=ctx.now()[:10], amount=amount, refund_component=refund_component,
               return_id=return_id, refund_quantity=0, funded_by="northloop",
               refund_destination="original_payment", restocking_fee_amount=0.0,
               return_shipping_fee_amount=0.0, late_return_deduction_amount=0.0)
    net = round(float(order.get("net_paid_amount") or 0) - amount, 2)
    ctx.update("order_orders", order_id, net_paid_amount=net)
    return str({"status": "refunded", "order_event_id": rid, "order_id": order_id, "return_id": return_id,
                "refund_component": refund_component, "amount": amount, "funded_by": "northloop",
                "net_paid_amount": net, "event_date": ctx.now()[:10]})

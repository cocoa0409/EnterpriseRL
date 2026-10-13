"""Hidden task tools of the claim repair billing desk (Insurance Claim Repairs).

Each tool performs one atomic write on an insurance claim repair order and is reached only
through unlock -> call; its name is published in the desk's knowledge base. A tool records the
values it is given and never checks a business precondition: whether and with which value an
action is due is decided from the published policy before the call.
"""

from erlbench import ToolContext, tool


@tool(owner="user", rw="write")
def sign_unrelated_damage_addition_ef94c675(ctx: ToolContext, consent_id: str, amount_usd: float) -> dict:
    """The vehicle owner signs a customer-pay addition form on their insurance claim repair order,
    agreeing to pay a stated price for repair work on damage unrelated to the claim. The form must
    already have been issued to the owner and be awaiting their signature. On success the form
    changes from awaiting the customer to signed, carries the agreed price and today's signing date,
    and the added work becomes part of the repair order at the owner's expense. The owner sees the
    signed form with its price in the receipt.

    Args:
        consent_id: Id class — reference number of the customer-pay addition form awaiting the owner's signature, as returned by the repair order form lookup.
        amount_usd: Fixed-format class — price the owner agrees to pay for the added work, in USD, 2 decimal places, a positive amount; any further digits are rounded half to even to the cent before it is recorded.

    Returns:
        dict with consent_id (str, the form signed), consent_status (str, "signed" once the signature is recorded),
        amount_usd (float, the agreed price in USD to 2 decimal places) and signed_date (str, YYYY-MM-DD, the signing
        date). A receipt whose consent_status is "signed" confirms the owner's agreement is on the repair order.
    """
    signed_on = ctx.now()[:10]
    price = round(float(amount_usd), 2)
    ctx.update("claim_consents", consent_id, consent_status="signed", amount_usd=price, signed_date=signed_on)
    return {"consent_id": consent_id, "consent_status": "signed", "amount_usd": price, "signed_date": signed_on}


@tool(owner="agent", rw="write")
def record_insurer_authorization_cee3bb86(ctx: ToolContext, claim_repair_id: str, estimated_repair_days: int) -> dict:
    """Record the insurer's authorization of an insurance claim repair order's original estimate. The
    repair order moves from assigned to authorized with today's authorization date and the planned
    repair days given, and the insurer's approval of the original estimate total is booked on the
    repair order's money history as an amount the insurer owes. The customer and the insurer can then
    see the repair order as authorized with its planned repair days.

    Args:
        claim_repair_id: Id class — reference number of the insurance claim repair order being authorized, as returned by the repair order lookup.
        estimated_repair_days: Fixed-format class — planned repair days fixed at authorization, a whole number of days given as an integer (no fractions).

    Returns:
        dict with claim_repair_id (str), status (str, "authorized"), authorized_date (str, YYYY-MM-DD),
        estimated_repair_days (int, the planned repair days recorded), approval_entry_id (str, reference number of the
        booked insurer approval) and approved_amount_usd (float, USD to 2 decimal places, the original estimate total
        booked as approved). A receipt with status "authorized" confirms the authorization is recorded.
    """
    today = ctx.now()[:10]
    days = int(estimated_repair_days)
    rows = ctx.find("claim_repairs", claim_repair_id=claim_repair_id)
    order = rows[0] if rows else {}
    approved = round(float(order.get("original_estimate_usd") or 0.0), 2)
    ctx.update("claim_repairs", claim_repair_id, status="authorized", authorized_date=today,
               estimated_repair_days=days)
    entry_id = ctx.make_id("cla_", claim_repair_id, "original_estimate", 0)
    ctx.create("claim_ledger", entry_id, ledger_entry_id=entry_id, claim_repair_id=claim_repair_id,
               customer_id=order.get("customer_id"), event_type="claim_insurer_approval", entry_date=today,
               approval_type="original_estimate", supplement_number=0, amount_usd=approved, betterment_usd=0.0)
    return {"claim_repair_id": claim_repair_id, "status": "authorized", "authorized_date": today,
            "estimated_repair_days": days, "approval_entry_id": entry_id, "approved_amount_usd": approved}


@tool(owner="user", rw="write")
def accept_denied_operations_addition_a285270b(ctx: ToolContext, consent_id: str, amount_usd: float) -> dict:
    """The vehicle owner agrees in writing to pay for repair operations their insurer refused to
    approve on a supplement, so that the center performs them at the owner's expense. The form for
    those denied operations must already have been issued to the owner and be awaiting their
    signature. On success the form changes from awaiting the customer to signed, carries the agreed
    price and today's signing date, and the denied operations become customer-pay work on the
    insurance claim repair order. The owner sees the signed form with its price in the receipt.

    Args:
        consent_id: Id class — reference number of the customer-pay form for the denied operations that awaits the owner's signature, as returned by the repair order form lookup.
        amount_usd: Fixed-format class — price the owner agrees to pay for the denied operations, in USD, 2 decimal places, a positive amount; any further digits are rounded half to even to the cent before it is recorded.

    Returns:
        dict with consent_id (str, the form signed), consent_status (str, "signed" once the signature is recorded),
        amount_usd (float, the agreed price in USD to 2 decimal places) and signed_date (str, YYYY-MM-DD, the signing
        date). A receipt whose consent_status is "signed" confirms the owner has taken on the denied operations.
    """
    signed_on = ctx.now()[:10]
    price = round(float(amount_usd), 2)
    ctx.update("claim_consents", consent_id, consent_status="signed", amount_usd=price, signed_date=signed_on)
    return {"consent_id": consent_id, "consent_status": "signed", "amount_usd": price, "signed_date": signed_on}


@tool(owner="agent", rw="write")
def issue_overpayment_refund_b142d0d2(ctx: ToolContext, claim_repair_id: str, source_entry_id: str,
                                      amount_usd: float) -> dict:
    """Refund part or all of one customer payment on an insurance claim repair order when the owner has
    paid more than the repair order owes. One refund entry is recorded against the named payment,
    dated today, for the amount given and to the same payment method as that payment; the repair
    order's customer balance rises by the refunded amount and the owner sees the money returned to
    their card, bank account or by check according to the original payment.

    Args:
        claim_repair_id: Id class — reference number of the insurance claim repair order the refund is made on, as returned by the repair order lookup.
        source_entry_id: Id class — reference number of the customer payment entry the refund returns, as returned by the repair order money history lookup.
        amount_usd: Fixed-format class — amount refunded, in USD, 2 decimal places, a positive amount; any further digits are rounded half to even to the cent before it is recorded.

    Returns:
        dict with refund_entry_id (str, reference number of the refund entry), claim_repair_id (str),
        source_entry_id (str, the payment returned), amount_usd (float, USD to 2 decimal places, the amount
        refunded), payment_method (str, the method the money goes back to: card, ach, cash, check or financing)
        and entry_date (str, YYYY-MM-DD). A receipt carrying a refund_entry_id confirms the refund is recorded.
    """
    today = ctx.now()[:10]
    refunded = round(float(amount_usd), 2)
    rows = ctx.find("claim_ledger", ledger_entry_id=source_entry_id)
    payment = rows[0] if rows else {}
    method = payment.get("payment_method") or ""
    entry_id = ctx.make_id("clr_", claim_repair_id, source_entry_id, refunded)
    ctx.create("claim_ledger", entry_id, ledger_entry_id=entry_id, claim_repair_id=claim_repair_id,
               customer_id=payment.get("customer_id"), event_type="claim_customer_refund", entry_date=today,
               source_entry_id=source_entry_id, amount_usd=refunded, payment_method=method)
    return {"refund_entry_id": entry_id, "claim_repair_id": claim_repair_id, "source_entry_id": source_entry_id,
            "amount_usd": refunded, "payment_method": method, "entry_date": today}

"""Hidden task tools — protection_plan_claims_and_refunds (Northgate Protect plans)."""

from decimal import Decimal, ROUND_HALF_UP

from erlbench import ToolContext, tool


class _Money:
    """Money normalisation shared by the tools: two decimal places, half up."""

    @staticmethod
    def cents(value) -> float:
        return float(Decimal(str(value)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP))


@tool(owner="agent", rw="write")
def register_item_limit_ba116528(ctx: ToolContext, plan_id: str, amount_usd: float) -> str:
    """Register a single-item Northgate Protect plan's covered item on the plan together with its limit of liability.

    One call books one registration entry on the plan for the covered order line the plan names, carrying that line's
    item category and the limit of liability passed in, and raises the plan's remaining limit of liability by the same
    amount. After the call the plan shows the covered item as registered and its remaining limit of liability includes
    the registered amount. The receipt below indicates the registration was booked.

    Args:
        plan_id: Id class — the identifier of the Northgate Protect plan whose covered item is being registered, read from the
            plan holdings lookup for this customer before the call.
        amount_usd: Fixed-format class — the limit of liability registered for the covered item, in US dollars as a
            positive decimal number with 2 decimal places; any further digits are rounded half up to the cent.

    Returns:
        A text receipt "Registered covered item on plan <plan_id>: registration <registration_ref>, order line
        <order_line_ref>, category <item_category>, limit of liability USD <amount>; remaining limit of liability now USD
        <remaining>." where registration_ref is the new registration reference (text), order_line_ref and item_category
        are taken from the plan, amount is the registered limit and remaining is the plan's new remaining limit of
        liability (both decimals with two places). Receiving this receipt means the registration was booked.
    """
    amount = _Money.cents(amount_usd)
    if amount <= 0:
        return "Error: amount_usd must be a positive amount in US dollars."
    plan = ctx.find("plan_holdings", plan_id=plan_id)[0]
    rid = ctx.make_id("preg_", plan_id, amount)
    ctx.create("plan_events", rid, plan_event_id=rid, plan_id=plan_id, customer_id=plan["customer_id"],
               event_type="plan_register_item", event_date=ctx.now()[:10], amount_usd=amount,
               charge_type="not_applicable", billing_period_start="", payment_method_type="none",
               card_account_id=None, original_event_id=None, refund_basis="not_applicable",
               covered_order_event_id=plan["covered_order_event_id"],
               covered_item_category=plan["covered_item_category"], claim_type="not_applicable",
               incident_date="", claim_decision="not_applicable", service_fee_usd=0.0,
               settlement_method="not_applicable")
    remaining = _Money.cents(float(plan.get("liability_remaining_usd") or 0) + amount)
    ctx.update("plan_holdings", plan_id, liability_remaining_usd=remaining)
    return (f"Registered covered item on plan {plan_id}: registration {rid}, order line "
            f"{plan['covered_order_event_id']}, category {plan['covered_item_category']}, limit of liability USD "
            f"{amount:.2f}; remaining limit of liability now USD {remaining:.2f}.")


@tool(owner="agent", rw="write")
def record_claim_decision_cf68f06d(ctx: ToolContext, claim_event_id: str, claim_decision: str,
                                   service_fee_usd: float) -> str:
    """Record the administrator's decision on one filed Northgate Protect claim, with the service fee it carries.

    One call books one decision entry on the plan the claim belongs to, pointing back at the claim, with the decision
    and the service fee passed in, and marks the claim itself with that decision. After the call the claim shows as decided
    with that decision and service fee.
    The receipt below indicates the decision was booked.

    Args:
        claim_event_id: Id class — the identifier (claim reference) of the filed claim being decided, read from the plan ledger
            lookup for the plan before the call.
        claim_decision: Enum class — the decision recorded, exactly one of:
            "approved" — the claim is accepted for settlement;
            "denied_not_covered" — the peril claimed is not one the plan covers;
            "denied_manufacturer_warranty" — the failure falls inside the manufacturer warranty and is referred to the
            manufacturer;
            "denied_waiting_period" — the incident date falls inside the plan's waiting period;
            "denied_filing_late" — the claim was filed after the filing deadline;
            "denied_claim_limit" — the plan has already reached its approved-claim limit for the rolling 12 months;
            "denied_outside_term" — the incident date falls outside the coverage term;
            "not_applicable" — no decision outcome is stated, which records the claim as handled without one.
        service_fee_usd: Fixed-format class — the service fee the decision carries, in US dollars as a decimal number
            with 2 decimal places, 0.00 when no fee is owed; any further digits are rounded half up to the cent.

    Returns:
        A text receipt "Decision <decision_ref> recorded on claim <claim_event_id> of plan <plan_id>: <claim_decision>,
        service fee USD <fee>." where decision_ref is the new decision reference (text), plan_id is the plan the claim
        belongs to and fee is the recorded service fee (decimal with two places). Receiving this receipt means the
        decision was booked.
    """
    allowed = {"approved", "denied_not_covered", "denied_manufacturer_warranty", "denied_waiting_period",
               "denied_filing_late", "denied_claim_limit", "denied_outside_term", "not_applicable"}
    if claim_decision not in allowed:
        return f"Error: claim_decision must be one of {', '.join(sorted(allowed))}."
    fee = _Money.cents(service_fee_usd)
    claim = ctx.find("plan_events", plan_event_id=claim_event_id)[0]
    rid = ctx.make_id("pdec_", claim_event_id, claim_decision, fee)
    ctx.create("plan_events", rid, plan_event_id=rid, plan_id=claim["plan_id"], customer_id=claim["customer_id"],
               event_type="plan_decide_claim", event_date=ctx.now()[:10], amount_usd=0.0,
               charge_type="not_applicable", billing_period_start="", payment_method_type="none",
               card_account_id=None, original_event_id=claim_event_id, refund_basis="not_applicable",
               covered_order_event_id=claim["covered_order_event_id"], covered_item_category="not_applicable",
               claim_type="not_applicable", incident_date="", claim_decision=claim_decision, service_fee_usd=fee,
               settlement_method="not_applicable")
    ctx.update("plan_events", claim_event_id, claim_decision=claim_decision)
    return (f"Decision {rid} recorded on claim {claim_event_id} of plan {claim['plan_id']}: {claim_decision}, "
            f"service fee USD {fee:.2f}.")


@tool(owner="agent", rw="write")
def authorize_claim_repair_5d8df043(ctx: ToolContext, claim_event_id: str, settlement_method: str,
                                    amount_usd: float) -> str:
    """Authorize the settlement of one Northgate Protect claim, by repair or by replacement, and book it on the plan.

    One call books one settlement entry on the plan the claim belongs to, pointing back at the claim and at the covered
    order line and carrying the claim's type, with the method and value passed in, and lowers the plan's remaining limit of liability by that value.
    A replacement also ends the single-item plan as fulfilled today. After the call the claim shows its settlement and the
    plan's remaining limit of liability is reduced. The receipt below indicates the settlement was booked.

    Args:
        claim_event_id: Id class — the identifier (claim reference) of the claim being settled, read from the plan
            ledger lookup for the plan before the call.
        settlement_method: Enum class — how the claim is settled, exactly one of:
            "repair" — the covered item is repaired at the authorized repair value;
            "replacement" — the covered item is replaced, booked at the item's remaining limit of liability, and the
            plan ends as fulfilled;
            "reimbursement_egift_card" — not booked by this tool, which answers with an error for this value;
            "food_loss_payment" — not booked by this tool, which answers with an error for this value;
            "not_applicable" — not booked by this tool, which answers with an error for this value.
        amount_usd: Fixed-format class — the settlement value, in US dollars as a positive decimal number with 2 decimal
            places; any further digits are rounded half up to the cent.

    Returns:
        A text receipt "Settlement authorized on claim <claim_event_id> of plan <plan_id>: <settlement_method>
        <settlement_ref>, value USD <amount>; remaining limit of liability now USD <remaining>; plan status <status>."
        where settlement_ref is the new settlement reference (text), amount and remaining are decimals with two places,
        and status is the plan's status afterwards (active, or fulfilled after a replacement). Receiving this receipt
        means the settlement was booked.
    """
    if settlement_method not in {"repair", "replacement"}:
        return "Error: this tool books only repair or replacement settlements."
    amount = _Money.cents(amount_usd)
    if amount <= 0:
        return "Error: amount_usd must be a positive amount in US dollars."
    claim = ctx.find("plan_events", plan_event_id=claim_event_id)[0]
    plan = ctx.find("plan_holdings", plan_id=claim["plan_id"])[0]
    rid = ctx.make_id("pset_", claim_event_id, settlement_method, amount)
    ctx.create("plan_events", rid, plan_event_id=rid, plan_id=claim["plan_id"], customer_id=claim["customer_id"],
               event_type="plan_settle_claim", event_date=ctx.now()[:10], amount_usd=amount,
               charge_type="not_applicable", billing_period_start="", payment_method_type="none",
               card_account_id=None, original_event_id=claim_event_id, refund_basis="not_applicable",
               covered_order_event_id=claim["covered_order_event_id"], covered_item_category="not_applicable",
               claim_type=claim["claim_type"], incident_date="", claim_decision="not_applicable", service_fee_usd=0.0,
               settlement_method=settlement_method)
    remaining = _Money.cents(float(plan.get("liability_remaining_usd") or 0) - amount)
    status = plan.get("status")
    if settlement_method == "replacement":
        status = "fulfilled"
        ctx.update("plan_holdings", claim["plan_id"], liability_remaining_usd=remaining, status=status,
                   closed_date=ctx.now()[:10])
    else:
        ctx.update("plan_holdings", claim["plan_id"], liability_remaining_usd=remaining)
    return (f"Settlement authorized on claim {claim_event_id} of plan {claim['plan_id']}: {settlement_method} {rid}, "
            f"value USD {amount:.2f}; remaining limit of liability now USD {remaining:.2f}; plan status {status}.")


@tool(owner="user", rw="write")
def cancel_accident_plan_cec4ac7d(ctx: ToolContext, plan_id: str, original_event_id: str, refund_basis: str,
                                  refund_amount_usd: float) -> str:
    """Cancel your own Northgate Protect plan as of today and receive its cancellation refund on the card that paid it.

    One call confirms your cancellation request for the plan (your most recent request still waiting is marked
    confirmed; if none is waiting, a confirmed request is recorded), closes the plan as canceled with today's date, books
    one refund of the plan charge named, of the amount and on the basis passed in, credited to the external card that
    paid that charge, and reduces the plan's net premium paid by that refund. A charge paid any other way is not
    refunded by this tool, which then answers with an error and changes nothing. After the call the plan shows as
    canceled and the refund appears on the plan ledger. The receipt below indicates the cancellation and refund were
    booked.

    Args:
        plan_id: Id class — the identifier of the plan being canceled, as the agent reads it to you from the plan holdings
            lookup before the call.
        original_event_id: Id class — the identifier of the plan charge to be refunded, as the agent reads it to you from
            the plan ledger lookup before the call.
        refund_basis: Enum class — the basis of the refund, exactly one of:
            "full_within_window" — canceled inside the full-refund window with no claim filed;
            "prorated_unused_days" — canceled outside that window and refunded for the unused coverage;
            "item_returned" — the covered item was returned or canceled;
            "billing_error" — the charge was made in error;
            "not_applicable" — no refund basis is stated, which books the refund without one.
        refund_amount_usd: Fixed-format class — the cancellation refund, in US dollars as a decimal number with 2 decimal
            places, never negative; any further digits are rounded half up to the cent.

    Returns:
        A text receipt "Plan <plan_id> canceled on <date>: request <request_ref> confirmed; refund <refund_ref> of USD
        <amount> (<refund_basis>) credited to the external card that paid the plan; net premium paid now USD <premium>."
        where date is today's date (YYYY-MM-DD), request_ref and refund_ref are the confirmed request and new refund
        references (text), and amount and premium are decimals with two places. Receiving this receipt means the
        cancellation and the refund were booked.
    """
    allowed = {"full_within_window", "prorated_unused_days", "item_returned", "billing_error", "not_applicable"}
    if refund_basis not in allowed:
        return f"Error: refund_basis must be one of {', '.join(sorted(allowed))}."
    amount = _Money.cents(refund_amount_usd)
    if amount < 0:
        return "Error: refund_amount_usd cannot be negative."
    charge = ctx.find("plan_events", plan_event_id=original_event_id)[0]
    if charge.get("payment_method_type") != "external_card":
        return "Error: this tool refunds only plan charges paid by an external card; nothing was changed."
    plan = ctx.find("plan_holdings", plan_id=plan_id)[0]
    today = ctx.now()[:10]
    waiting = sorted(ctx.find("plan_requests", plan_id=plan_id, request_type="cancel_plan", request_status="submitted"),
                     key=lambda r: str(r.get("created_at")))
    if waiting:
        req = waiting[-1]["plan_request_id"]
        ctx.update("plan_requests", req, request_status="confirmed")
    else:
        req = ctx.make_id("preq_", plan_id, "cancel_plan", today)
        ctx.create("plan_requests", req, plan_request_id=req, customer_id=plan["customer_id"], plan_id=plan_id,
                   request_type="cancel_plan", request_status="confirmed", created_at=ctx.now())
    ctx.update("plan_holdings", plan_id, status="canceled", closed_date=today)
    rid = ctx.make_id("pref_", plan_id, original_event_id, refund_basis, amount)
    ctx.create("plan_events", rid, plan_event_id=rid, plan_id=plan_id, customer_id=plan["customer_id"],
               event_type="plan_refund", event_date=today, amount_usd=amount, charge_type="not_applicable",
               billing_period_start="", payment_method_type="external_card", card_account_id=None,
               original_event_id=original_event_id, refund_basis=refund_basis, covered_order_event_id=None,
               covered_item_category="not_applicable", claim_type="not_applicable", incident_date="",
               claim_decision="not_applicable", service_fee_usd=0.0, settlement_method="not_applicable")
    premium = _Money.cents(float(plan.get("premium_paid_usd") or 0) - amount)
    ctx.update("plan_holdings", plan_id, premium_paid_usd=premium)
    return (f"Plan {plan_id} canceled on {today}: request {req} confirmed; refund {rid} of USD {amount:.2f} "
            f"({refund_basis}) credited to the external card that paid the plan; net premium paid now USD {premium:.2f}.")


@tool(owner="agent", rw="write")
def pay_food_loss_claim_b4f587dd(ctx: ToolContext, claim_event_id: str, amount_usd: float) -> str:
    """Pay one Northgate Protect food-loss claim and book the payment as the claim's food-loss settlement.

    One call books one food-loss payment settlement entry on the plan the claim belongs to, pointing back at the claim and
    at the covered order line, with the payment amount passed in, and lowers the plan's remaining limit of liability by
    that amount. After the call the claim shows a food-loss payment and the plan's remaining limit of liability is
    reduced. The receipt below indicates the payment was booked.

    Args:
        claim_event_id: Id class — the identifier (claim reference) of the food-loss claim being paid, read from
            the plan ledger lookup for the plan before the call.
        amount_usd: Fixed-format class — the food-loss payment, in US dollars as a positive decimal number with 2 decimal
            places; any further digits are rounded half up to the cent.

    Returns:
        A text receipt "Food-loss payment booked on claim <claim_event_id> of plan <plan_id>: settlement <settlement_ref>,
        USD <amount>; remaining limit of liability now USD <remaining>." where settlement_ref is the new settlement
        reference (text), amount is the payment and remaining is the plan's new remaining limit of liability (both
        decimals with two places). Receiving this receipt means the food-loss payment was booked.
    """
    amount = _Money.cents(amount_usd)
    if amount <= 0:
        return "Error: amount_usd must be a positive amount in US dollars."
    claim = ctx.find("plan_events", plan_event_id=claim_event_id)[0]
    plan = ctx.find("plan_holdings", plan_id=claim["plan_id"])[0]
    rid = ctx.make_id("pset_", claim_event_id, "food_loss_payment", amount)
    ctx.create("plan_events", rid, plan_event_id=rid, plan_id=claim["plan_id"], customer_id=claim["customer_id"],
               event_type="plan_settle_claim", event_date=ctx.now()[:10], amount_usd=amount,
               charge_type="not_applicable", billing_period_start="", payment_method_type="none",
               card_account_id=None, original_event_id=claim_event_id, refund_basis="not_applicable",
               covered_order_event_id=claim["covered_order_event_id"], covered_item_category="not_applicable",
               claim_type=claim["claim_type"], incident_date="", claim_decision="not_applicable", service_fee_usd=0.0,
               settlement_method="food_loss_payment")
    remaining = _Money.cents(float(plan.get("liability_remaining_usd") or 0) - amount)
    ctx.update("plan_holdings", claim["plan_id"], liability_remaining_usd=remaining)
    return (f"Food-loss payment booked on claim {claim_event_id} of plan {claim['plan_id']}: settlement {rid}, USD "
            f"{amount:.2f}; remaining limit of liability now USD {remaining:.2f}.")


@tool(owner="user", rw="write")
def cancel_standard_plan_ca7b280f(ctx: ToolContext, plan_id: str, original_event_id: str, refund_basis: str,
                                  refund_amount_usd: float) -> str:
    """Cancel your own single-item Northgate Protect plan today and have its cancellation refund sent to the card that paid it.

    One call confirms your cancellation request for the plan (your most recent request still waiting is marked
    confirmed; if none is waiting, a confirmed request is recorded), closes the plan as canceled with today's date, books
    one refund of the plan charge named, of the amount and on the basis passed in, sent to the external card that
    paid that charge, and reduces the plan's net premium paid by that refund. A charge paid any other way is not
    refunded by this tool, which then answers with an error and changes nothing. After the call the plan shows as
    canceled and the refund appears on the plan ledger. The receipt below indicates the cancellation and refund were
    booked.

    Args:
        plan_id: Id class — the identifier of the plan you are canceling, as the agent reads it to you from the plan holdings
            lookup before the call.
        original_event_id: Id class — the identifier of the plan charge to be refunded, as the agent reads it to you from
            the plan ledger lookup before the call.
        refund_basis: Enum class — the basis of the refund, exactly one of:
            "full_within_window" — canceled inside the full-refund window with no claim filed;
            "prorated_unused_days" — canceled outside that window and refunded for the unused coverage;
            "item_returned" — the covered item was returned or canceled;
            "billing_error" — the charge was made in error;
            "not_applicable" — no refund basis is stated, which books the refund without one.
        refund_amount_usd: Fixed-format class — the cancellation refund, in US dollars as a decimal number with 2 decimal
            places, never negative; any further digits are rounded half up to the cent.

    Returns:
        A text receipt "Plan <plan_id> canceled on <date>: request <request_ref> confirmed; refund <refund_ref> of USD
        <amount> (<refund_basis>) sent to the external card that paid the plan; net premium paid now USD <premium>."
        where date is today's date (YYYY-MM-DD), request_ref and refund_ref are the confirmed request and new refund
        references (text), and amount and premium are decimals with two places. Receiving this receipt means the
        cancellation and the refund were booked.
    """
    allowed = {"full_within_window", "prorated_unused_days", "item_returned", "billing_error", "not_applicable"}
    if refund_basis not in allowed:
        return f"Error: refund_basis must be one of {', '.join(sorted(allowed))}."
    amount = _Money.cents(refund_amount_usd)
    if amount < 0:
        return "Error: refund_amount_usd cannot be negative."
    charge = ctx.find("plan_events", plan_event_id=original_event_id)[0]
    if charge.get("payment_method_type") != "external_card":
        return "Error: this tool refunds only plan charges paid by an external card; nothing was changed."
    plan = ctx.find("plan_holdings", plan_id=plan_id)[0]
    today = ctx.now()[:10]
    waiting = sorted(ctx.find("plan_requests", plan_id=plan_id, request_type="cancel_plan", request_status="submitted"),
                     key=lambda r: str(r.get("created_at")))
    if waiting:
        req = waiting[-1]["plan_request_id"]
        ctx.update("plan_requests", req, request_status="confirmed")
    else:
        req = ctx.make_id("preq_", plan_id, "cancel_plan", today)
        ctx.create("plan_requests", req, plan_request_id=req, customer_id=plan["customer_id"], plan_id=plan_id,
                   request_type="cancel_plan", request_status="confirmed", created_at=ctx.now())
    ctx.update("plan_holdings", plan_id, status="canceled", closed_date=today)
    rid = ctx.make_id("pref_", plan_id, original_event_id, refund_basis, amount)
    ctx.create("plan_events", rid, plan_event_id=rid, plan_id=plan_id, customer_id=plan["customer_id"],
               event_type="plan_refund", event_date=today, amount_usd=amount, charge_type="not_applicable",
               billing_period_start="", payment_method_type="external_card", card_account_id=None,
               original_event_id=original_event_id, refund_basis=refund_basis, covered_order_event_id=None,
               covered_item_category="not_applicable", claim_type="not_applicable", incident_date="",
               claim_decision="not_applicable", service_fee_usd=0.0, settlement_method="not_applicable")
    premium = _Money.cents(float(plan.get("premium_paid_usd") or 0) - amount)
    ctx.update("plan_holdings", plan_id, premium_paid_usd=premium)
    return (f"Plan {plan_id} canceled on {today}: request {req} confirmed; refund {rid} of USD {amount:.2f} "
            f"({refund_basis}) sent to the external card that paid the plan; net premium paid now USD {premium:.2f}.")

"""Hidden task tools of the tenant_protection_claims difficulty (Bluegate Tenant Protection plans).

Each tool performs one atomic write on a protection plan, its fee ledger, or a protection claim's
handling history, with the values the agent has already worked out from the published policy. No tool
checks eligibility, ordering or amounts; every such judgement belongs to the agent.
"""

from erlbench import ToolContext, tool


@tool(owner="user", rw="write")
def repay_recovered_claim_money_180976c0(ctx: ToolContext, claim_id: str, reference_event_id: str, amount: float) -> str:
    """The tenant repays, from their own funds, claim money that recovered stolen property no longer supports.

    One call records the tenant's repayment on one protection claim as a void of the claim payment it
    reverses, with the void reason stolen_property_recovered and today's date, and lowers the net claim
    money shown as paid on the tenant's protection plan by the repaid amount. After the call the claim's
    handling history shows the repayment entry and the plan's claims-paid total is reduced; the receipt
    below confirms the repayment was taken.

    Args:
        claim_id: Id class — the protection claim number of the claim whose recovered property is being
            repaid, as shown in the claim lookup the agent reads out to the tenant.
        reference_event_id: Id class — the reference number of the claim payment event this repayment
            reverses, as shown in the claim's handling history the agent reads out to the tenant.
        amount: Fixed-format class — the repayment the tenant pays, in USD, a positive number with 2
            decimal places, rounded half up to the cent; no currency sign.

    Returns:
        A dictionary receipt: claim_event_id (text, the reference number of the repayment entry),
        claim_id (text, the claim repaid), reference_event_id (text, the claim payment reversed),
        amount (number in USD with 2 decimal places, the amount repaid), void_reason (text, always
        stolen_property_recovered), event_date (text, YYYY-MM-DD, the date recorded) and status (text,
        "repayment_recorded" when the repayment has been taken).
    """
    rows = ctx.find("protect_claims", claim_id=claim_id)
    claim = rows[0] if rows else {}
    plan_id = claim.get("plan_id", "")
    amt = round(float(amount), 2)
    rid = ctx.make_id("pcv_", claim_id, reference_event_id, amount)
    day = ctx.now()[:10]
    ctx.create("protect_claim_events", rid, claim_event_id=rid, plan_id=plan_id,
               customer_id=claim.get("customer_id", ""), claim_id=claim_id,
               event_type="protect_claim_payment_voided", event_date=day, amount=amt,
               reference_event_id=reference_event_id, void_reason="stolen_property_recovered")
    plans = ctx.find("protect_plans", plan_id=plan_id) if plan_id else []
    if plans:
        ctx.update("protect_plans", plan_id,
                   claims_paid_total=round(float(plans[0].get("claims_paid_total") or 0) - amt, 2))
    return str({"claim_event_id": rid, "claim_id": claim_id, "reference_event_id": reference_event_id,
                "amount": amt, "void_reason": "stolen_property_recovered", "event_date": day,
                "status": "repayment_recorded"})


@tool(owner="agent", rw="write")
def record_claim_decision_61f94ad8(ctx: ToolContext, claim_id: str, decision: str, denial_reason: str,
                                   amount: float) -> str:
    """Record the claims desk's decision on one protection claim, with the amount approved for payment.

    One call adds a decision entry dated today to the claim's handling history, carrying the outcome,
    the controlled reason and the approved amount, and moves the claim's handling status to approved
    (for either approval outcome) or denied. After the call the tenant can be told the outcome and the
    approved amount; the receipt below confirms the decision is on file.

    Args:
        claim_id: Id class — the protection claim number being decided, as returned by the claim lookup
            for the tenant's plan.
        decision: Enum class — the outcome: approved_full when the whole payable amount is approved;
            approved_partial when less than the payable amount but more than zero is approved;
            denied when nothing is approved.
        denial_reason: Enum class — the controlled reason behind the outcome: none for a full approval;
            not_in_force_on_loss_date when the plan was not in force on the loss date; excluded_peril
            when the cause of loss is an excluded peril; filed_late when the claim was filed after the
            filing deadline; no_police_report when a required police report is missing;
            no_forced_entry when a burglary shows no forced-entry evidence; documents_not_received when
            a requested document never arrived; aggregate_limit_reached when the annual aggregate cuts
            the approval; claim_count_limit_reached when the plan has already paid its maximum number
            of claims in the window; below_deductible when the loss does not exceed the deductible;
            excluded_property when the property lost is of a kind the plan never covers.
        amount: Fixed-format class — the amount approved for payment, in USD, a number with 2 decimal
            places, rounded half up to the cent; 0.00 for a denial; no currency sign.

    Returns:
        A dictionary receipt: claim_event_id (text, the reference number of the decision entry),
        claim_id (text, the claim decided), decision (text, the outcome recorded), denial_reason (text,
        the reason recorded), amount (number in USD with 2 decimal places, the approved amount),
        event_date (text, YYYY-MM-DD, the decision date) and claim_status (text, approved or denied, the
        claim's handling status after the decision).
    """
    rows = ctx.find("protect_claims", claim_id=claim_id)
    claim = rows[0] if rows else {}
    amt = round(float(amount), 2)
    rid = ctx.make_id("pcd_", claim_id, decision, denial_reason, amount)
    day = ctx.now()[:10]
    ctx.create("protect_claim_events", rid, claim_event_id=rid, plan_id=claim.get("plan_id", ""),
               customer_id=claim.get("customer_id", ""), claim_id=claim_id,
               event_type="protect_claim_decision", event_date=day, decision=decision,
               denial_reason=denial_reason, amount=amt)
    status = "denied" if decision == "denied" else "approved"
    if claim:
        ctx.update("protect_claims", claim_id, claim_status=status)
    return str({"claim_event_id": rid, "claim_id": claim_id, "decision": decision,
                "denial_reason": denial_reason, "amount": amt, "event_date": day, "claim_status": status})


@tool(owner="agent", rw="write")
def credit_protection_fee_error_2320aa46(ctx: ToolContext, plan_id: str, reference_entry_id: str, amount: float) -> str:
    """Post a billing-error correction credit against one protection fee charge on a tenant protection plan.

    One call adds a fee-ledger credit dated today, of the kind billing_error_correction, referencing the
    fee charge being corrected, and lowers the plan's protection fee balance by the credited amount (a
    negative balance is a credit the tenant holds). After the call the tenant can see the credit on the
    plan's fee ledger; the receipt below confirms it was posted.

    Args:
        plan_id: Id class — the tenant protection plan number whose fee ledger is credited, as returned by
            the plan lookup.
        reference_entry_id: Id class — the reference number of the protection fee charge entry being
            corrected, as returned by the fee ledger lookup.
        amount: Fixed-format class — the credit posted, in USD, a positive number with 2 decimal places,
            rounded half up to the cent; no currency sign.

    Returns:
        A dictionary receipt: premium_entry_id (text, the reference number of the credit entry), plan_id
        (text, the plan credited), reference_entry_id (text, the fee charge corrected), credit_type
        (text, always billing_error_correction), amount (number in USD with 2 decimal places, the credit
        posted), entry_date (text, YYYY-MM-DD, the posting date) and premium_balance_due (number in USD
        with 2 decimal places, the plan's fee balance after the credit, negative when in credit).
    """
    plans = ctx.find("protect_plans", plan_id=plan_id)
    plan = plans[0] if plans else {}
    amt = round(float(amount), 2)
    rid = ctx.make_id("ppc_", plan_id, reference_entry_id, amount)
    day = ctx.now()[:10]
    ctx.create("protect_premiums", rid, premium_entry_id=rid, plan_id=plan_id,
               customer_id=plan.get("customer_id", ""), event_type="protect_premium_credit", amount=amt,
               entry_date=day, credit_type="billing_error_correction", reference_entry_id=reference_entry_id)
    balance = round(float(plan.get("premium_balance_due") or 0) - amt, 2)
    if plan:
        ctx.update("protect_plans", plan_id, premium_balance_due=balance)
    return str({"premium_entry_id": rid, "plan_id": plan_id, "reference_entry_id": reference_entry_id,
                "credit_type": "billing_error_correction", "amount": amt, "entry_date": day,
                "premium_balance_due": balance})


@tool(owner="agent", rw="write")
def record_reconsideration_decision_ea5df16d(ctx: ToolContext, claim_id: str, decision: str, denial_reason: str,
                                             amount: float) -> str:
    """Record a reconsidered decision on one protection claim, replacing its earlier decision with the whole amount now approved.

    One call adds a decision entry dated today to the claim's handling history, carrying the reconsidered outcome, the controlled
    reason and the total approved amount, and moves the claim's handling status to approved (for either approval outcome) or
    denied. After the call the tenant can be told the reconsidered outcome and total; the receipt below confirms it is on file.

    Args:
        claim_id: Id class — the protection claim number being reconsidered, as returned by the claim lookup for the tenant's plan.
        decision: Enum class — the reconsidered outcome: approved_full when the whole payable amount is approved;
            approved_partial when less than the payable amount but more than zero is approved; denied when nothing is approved.
        denial_reason: Enum class — the controlled reason behind the outcome: none for a full approval;
            not_in_force_on_loss_date when the plan was not in force on the loss date; excluded_peril when the cause of loss is
            an excluded peril; filed_late when the claim was filed after the filing deadline; no_police_report when a required
            police report is missing; no_forced_entry when a burglary shows no forced-entry evidence; documents_not_received
            when a requested document never arrived; aggregate_limit_reached when the annual aggregate cuts the approval;
            claim_count_limit_reached when the plan has already paid its maximum number of claims in the window;
            below_deductible when the loss does not exceed the deductible; excluded_property when the property lost is of a kind
            the plan never covers.
        amount: Fixed-format class — the total amount now approved on the claim, in USD, a number with 2 decimal places, rounded
            half up to the cent; 0.00 for a denial; no currency sign.

    Returns:
        A dictionary receipt: claim_event_id (text, the reference number of the decision entry), claim_id (text, the claim
        reconsidered), decision (text, the outcome recorded), denial_reason (text, the reason recorded), amount (number in USD with
        2 decimal places, the total approved), event_date (text, YYYY-MM-DD, the decision date) and claim_status (text, approved or
        denied, the claim's handling status after the decision).
    """
    rows = ctx.find("protect_claims", claim_id=claim_id)
    claim = rows[0] if rows else {}
    amt = round(float(amount), 2)
    rid = ctx.make_id("pcr_", claim_id, decision, denial_reason, amount)
    day = ctx.now()[:10]
    ctx.create("protect_claim_events", rid, claim_event_id=rid, plan_id=claim.get("plan_id", ""),
               customer_id=claim.get("customer_id", ""), claim_id=claim_id, event_type="protect_claim_decision",
               event_date=day, decision=decision, denial_reason=denial_reason, amount=amt)
    status = "denied" if decision == "denied" else "approved"
    if claim:
        ctx.update("protect_claims", claim_id, claim_status=status)
    return str({"claim_event_id": rid, "claim_id": claim_id, "decision": decision, "denial_reason": denial_reason,
                "amount": amt, "event_date": day, "claim_status": status})


@tool(owner="user", rw="write")
def repay_duplicate_claim_payment_968ba4e6(ctx: ToolContext, claim_id: str, reference_event_id: str, amount: float) -> str:
    """The tenant repays, from their own funds, claim money a second claim payment sent in error beyond what the claim supports.

    One call records the tenant's repayment on one protection claim as a void of the claim payment it reverses, with the void
    reason issued_in_error and today's date, and lowers the net claim money shown as paid on the tenant's protection plan by the
    repaid amount. After the call the claim's handling history shows the repayment entry; the receipt below confirms it was taken.

    Args:
        claim_id: Id class — the protection claim number whose second payment is being repaid, as shown in the claim lookup the
            agent reads out to the tenant.
        reference_event_id: Id class — the reference number of the claim payment event this repayment reverses, as shown in the
            claim's handling history the agent reads out to the tenant.
        amount: Fixed-format class — the repayment the tenant pays, in USD, a positive number with 2 decimal places, rounded half
            up to the cent; no currency sign.

    Returns:
        A dictionary receipt: claim_event_id (text, the reference number of the repayment entry), claim_id (text, the claim
        repaid), reference_event_id (text, the claim payment reversed), amount (number in USD with 2 decimal places, the amount
        repaid), void_reason (text, always issued_in_error), event_date (text, YYYY-MM-DD, the date recorded) and status (text,
        "repayment_recorded" when the repayment has been taken).
    """
    rows = ctx.find("protect_claims", claim_id=claim_id)
    claim = rows[0] if rows else {}
    plan_id = claim.get("plan_id", "")
    amt = round(float(amount), 2)
    rid = ctx.make_id("pcx_", claim_id, reference_event_id, amount)
    day = ctx.now()[:10]
    ctx.create("protect_claim_events", rid, claim_event_id=rid, plan_id=plan_id, customer_id=claim.get("customer_id", ""),
               claim_id=claim_id, event_type="protect_claim_payment_voided", event_date=day, amount=amt,
               reference_event_id=reference_event_id, void_reason="issued_in_error")
    plans = ctx.find("protect_plans", plan_id=plan_id) if plan_id else []
    if plans:
        ctx.update("protect_plans", plan_id,
                   claims_paid_total=round(float(plans[0].get("claims_paid_total") or 0) - amt, 2))
    return str({"claim_event_id": rid, "claim_id": claim_id, "reference_event_id": reference_event_id, "amount": amt,
                "void_reason": "issued_in_error", "event_date": day, "status": "repayment_recorded"})


@tool(owner="agent", rw="write")
def issue_late_claim_payment_da72d11f(ctx: ToolContext, claim_id: str, amount: float) -> str:
    """Issue by direct deposit the claim money still owed on one approved protection claim.

    One call adds a claim payment entry dated today, issued by direct deposit (ach_direct_deposit), to the claim's handling history,
    raises the net claim money shown as paid on the tenant's protection plan by that amount, and moves the claim's handling status
    to paid. After the call the tenant can be told the deposit is on its way; the receipt below confirms the payment was issued.

    Args:
        claim_id: Id class — the protection claim number being paid, as returned by the claim lookup for the tenant's plan.
        amount: Fixed-format class — the payment issued, in USD, a positive number with 2 decimal places, rounded half up to the
            cent; no currency sign.

    Returns:
        A dictionary receipt: claim_event_id (text, the reference number of the payment entry), claim_id (text, the claim paid),
        amount (number in USD with 2 decimal places, the amount issued), claim_payment_method (text, always
        ach_direct_deposit), event_date (text, YYYY-MM-DD, the issue date) and claim_status (text, always paid after the call).
    """
    rows = ctx.find("protect_claims", claim_id=claim_id)
    claim = rows[0] if rows else {}
    plan_id = claim.get("plan_id", "")
    amt = round(float(amount), 2)
    rid = ctx.make_id("pcp_", claim_id, amount)
    day = ctx.now()[:10]
    ctx.create("protect_claim_events", rid, claim_event_id=rid, plan_id=plan_id, customer_id=claim.get("customer_id", ""),
               claim_id=claim_id, event_type="protect_claim_payment", event_date=day, amount=amt,
               claim_payment_method="ach_direct_deposit")
    if claim:
        ctx.update("protect_claims", claim_id, claim_status="paid")
    plans = ctx.find("protect_plans", plan_id=plan_id) if plan_id else []
    if plans:
        ctx.update("protect_plans", plan_id,
                   claims_paid_total=round(float(plans[0].get("claims_paid_total") or 0) + amt, 2))
    return str({"claim_event_id": rid, "claim_id": claim_id, "amount": amt, "claim_payment_method": "ach_direct_deposit",
                "event_date": day, "claim_status": "paid"})


@tool(owner="agent", rw="write")
def refund_plan_credit_balance_dd5eed31(ctx: ToolContext, plan_id: str, amount: float) -> str:
    """Refund to the tenant's original payment method the credit balance left on one ended tenant protection plan.

    One call adds a fee-ledger refund entry dated today, paid to the original payment method (original_payment_method), and raises
    the plan's protection fee balance by the refunded amount, bringing a credit balance back toward zero. After the call the tenant
    can be told the refund is on its way; the receipt below confirms it was issued.

    Args:
        plan_id: Id class — the tenant protection plan number whose credit balance is refunded, as returned by the plan lookup.
        amount: Fixed-format class — the refund paid, in USD, a positive number with 2 decimal places, rounded half up to the cent;
            no currency sign.

    Returns:
        A dictionary receipt: premium_entry_id (text, the reference number of the refund entry), plan_id (text, the plan
        refunded), amount (number in USD with 2 decimal places, the refund paid), refund_method (text, always
        original_payment_method), entry_date (text, YYYY-MM-DD, the refund date) and premium_balance_due (number in USD with 2
        decimal places, the plan's fee balance after the refund).
    """
    plans = ctx.find("protect_plans", plan_id=plan_id)
    plan = plans[0] if plans else {}
    amt = round(float(amount), 2)
    rid = ctx.make_id("ppr_", plan_id, amount)
    day = ctx.now()[:10]
    ctx.create("protect_premiums", rid, premium_entry_id=rid, plan_id=plan_id, customer_id=plan.get("customer_id", ""),
               event_type="protect_premium_refund", amount=amt, entry_date=day, refund_method="original_payment_method")
    balance = round(float(plan.get("premium_balance_due") or 0) + amt, 2)
    if plan:
        ctx.update("protect_plans", plan_id, premium_balance_due=balance)
    return str({"premium_entry_id": rid, "plan_id": plan_id, "amount": amt, "refund_method": "original_payment_method",
                "entry_date": day, "premium_balance_due": balance})

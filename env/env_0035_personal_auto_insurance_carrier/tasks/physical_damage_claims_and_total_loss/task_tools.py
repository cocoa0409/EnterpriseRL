"""Hidden task tools of the physical_damage_claims_and_total_loss difficulty (category physdmg).
Path: env/env_0035_personal_auto_insurance_carrier/tasks/physical_damage_claims_and_total_loss/task_tools.py

Each tool performs exactly one atomic write on the physical damage claim file and is reached through
unlock_* -> call_*. No tool checks eligibility, prerequisites or amounts: the caller supplies values
already worked out from the published rules and the records.
"""

from erlbench import ToolContext, tool


@tool(owner="agent", rw="write")
def record_claim_acceptance_ec9cfb06(ctx: ToolContext, claim_number: str, coverage_part: str,
                                     deductible_amount: float) -> str:
    """Record the claims desk's decision accepting a reported physical damage claim, with the coverage part it
    is accepted under and the deductible that applies to it. One call adds one accepted coverage decision to the
    claim's file, dated today, with no denial ground; it becomes the claim's latest coverage decision, which the
    customer and the desk then see when reviewing the claim. Nothing is paid by this action.

    Args:
        claim_number: Id class — the claim number of the reported claim being accepted (for example as shown on the
            claim's loss report entry), read from the claim file before the call.
        coverage_part: Enum class — the coverage part the claim is accepted under: collision applies when the loss
            was a collision with another vehicle or object, a rollover or a hit-and-run collision; comprehensive
            applies to every other covered cause of loss (theft, vandalism, fire, hail, wind, flood, falling objects,
            glass breakage, hitting an animal).
        deductible_amount: Fixed-format class — the deductible recorded on the accepted claim, in USD, 2 decimal
            places, rounded half up to the cent; 0.00 when no deductible is charged.

    Returns:
        A dict receipt: decision_id (str, reference of the new coverage decision entry), claim_number (str, the
        claim decided), coverage_decision (str, always "accepted"), coverage_part (str, as recorded),
        deductible_amount (float, USD to 2 decimal places, as recorded) and decided_on (str, YYYY-MM-DD, today's
        date). A receipt carrying decision_id means the acceptance is on the claim file.
    """
    report = ctx.find("physdmg_claim_events", claim_number=claim_number, event_type="physdmg_claim_report")
    coverage_id = report[0].get("coverage_id", "") if report else ""
    customer_id = report[0].get("customer_id", "") if report else ""
    amount = round(float(deductible_amount), 2)
    rid = ctx.make_id("pdd_", claim_number, coverage_part, amount)
    ctx.create("physdmg_claim_events", rid, claim_event_id=rid, coverage_id=coverage_id,
               customer_id=customer_id, event_type="physdmg_coverage_decision", claim_number=claim_number,
               coverage_part=coverage_part, coverage_decision="accepted", denial_reason="none",
               deductible_amount=amount, event_date=ctx.now()[:10])
    return str({"decision_id": rid, "claim_number": claim_number, "coverage_decision": "accepted",
                "coverage_part": coverage_part, "deductible_amount": amount, "decided_on": ctx.now()[:10]})


@tool(owner="user", rw="write")
def accept_total_loss_settlement_c07cd979(ctx: ToolContext, claim_number: str, settlement_amount: float,
                                          loss_payee_payoff_amount: float) -> str:
    """The customer accepts, in person, the total-loss settlement of their vehicle, surrendering the vehicle and
    its title to Cardinal. One call records one accepted settlement on the claim: the vehicle goes to Cardinal,
    the net settlement figure the customer accepts and the payoff their lender or lessor states are recorded,
    and the offer and acceptance are both dated today. The signed title is still to be received, so nothing is
    paid by this action; the customer sees the settlement as accepted.

    Args:
        claim_number: Id class — the claim number of the total-loss claim being settled, as the claims desk gives
            it to the customer before the call.
        settlement_amount: Fixed-format class — the net settlement the customer accepts, in USD, 2 decimal places,
            rounded half up to the cent.
        loss_payee_payoff_amount: Fixed-format class — the payoff stated on the lender's or lessor's payoff
            letter for the vehicle, in USD, 2 decimal places; 0.00 when the vehicle carries no loan or lease.

    Returns:
        A dict receipt: settlement_id (str, reference of the accepted settlement), claim_number (str),
        settlement_option (str, always "surrender_to_cardinal"), settlement_amount (float, USD to 2 decimal
        places), loss_payee_payoff_amount (float, USD to 2 decimal places), offer_status (str, always
        "accepted") and accepted_date (str, YYYY-MM-DD, today's date). A receipt carrying settlement_id means the
        acceptance is recorded.
    """
    report = ctx.find("physdmg_claim_events", claim_number=claim_number, event_type="physdmg_claim_report")
    coverage_id = report[0].get("coverage_id", "") if report else ""
    customer_id = report[0].get("customer_id", "") if report else ""
    amount = round(float(settlement_amount), 2)
    payoff = round(float(loss_payee_payoff_amount), 2)
    rid = ctx.make_id("tls_", claim_number, "surrender_to_cardinal", amount, payoff)
    ctx.create("physdmg_total_loss_settlements", rid, settlement_id=rid, customer_id=customer_id,
               coverage_id=coverage_id, claim_number=claim_number, settlement_option="surrender_to_cardinal",
               settlement_amount=amount, loss_payee_payoff_amount=payoff, offer_date=ctx.now()[:10],
               offer_status="accepted", accepted_date=ctx.now()[:10], title_received=False,
               created_at=ctx.now())
    return str({"settlement_id": rid, "claim_number": claim_number, "settlement_option": "surrender_to_cardinal",
                "settlement_amount": amount, "loss_payee_payoff_amount": payoff, "offer_status": "accepted",
                "accepted_date": ctx.now()[:10]})


@tool(owner="agent", rw="write")
def pay_loan_lease_payoff_8a830e94(ctx: ToolContext, claim_number: str, amount: float) -> str:
    """Issue the loan/lease payoff benefit on a total-loss claim to the vehicle's loss payee (the lender or
    lessor named on the coverage). One call issues one claim payment of the loan/lease payoff component, made
    out to the loss payee exactly as named on the coverage, dated today, with no deductible taken from it; the
    payment raises the net amount paid on the vehicle's claims and is visible on the claim's payment history.

    Args:
        claim_number: Id class — the claim number of the total-loss claim the benefit is paid on, read from the
            claim file before the call.
        amount: Fixed-format class — the loan/lease payoff benefit paid, in USD, 2 decimal places, rounded half up
            to the cent.

    Returns:
        A dict receipt: payment_id (str, reference of the new payment), claim_number (str), payment_component
        (str, always "loan_lease_payoff"), payee_name (str, the loss payee exactly as named on the coverage),
        amount (float, USD to 2 decimal places) and payment_date (str, YYYY-MM-DD, today's date). A receipt
        carrying payment_id means the payment was issued.
    """
    report = ctx.find("physdmg_claim_events", claim_number=claim_number, event_type="physdmg_claim_report")
    coverage_id = report[0].get("coverage_id", "") if report else ""
    customer_id = report[0].get("customer_id", "") if report else ""
    cov = ctx.find("physdmg_coverages", coverage_id=coverage_id)
    payee = cov[0].get("loss_payee_name", "") if cov else ""
    paid = round(float(amount), 2)
    rid = ctx.make_id("pdp_", claim_number, "loan_lease_payoff", paid)
    ctx.create("physdmg_payments", rid, payment_id=rid, coverage_id=coverage_id, customer_id=customer_id,
               event_type="physdmg_claim_payment", claim_number=claim_number,
               payment_component="loan_lease_payoff", payee_type="loss_payee", payee_name=payee, amount=paid,
               deductible_applied=0.0, payment_date=ctx.now()[:10])
    return str({"payment_id": rid, "claim_number": claim_number, "payment_component": "loan_lease_payoff",
                "payee_name": payee, "amount": paid, "payment_date": ctx.now()[:10]})


@tool(owner="agent", rw="write")
def grant_claim_free_credit_c23d8d33(ctx: ToolContext, coverage_id: str, credit_period_end: str,
                                     amount: float) -> str:
    """Grant a Deductible Rewards credit to one vehicle's physical damage coverage for a completed claim-free
    year. One call adds one claim-free-year credit entry dated today for the period ending on the date given and
    raises the coverage's Deductible Rewards credit balance by the amount granted; the customer sees the new
    balance on the coverage.

    Args:
        coverage_id: Id class — the reference number of the vehicle's physical damage coverage, read from the
            customer's coverage records before the call.
        credit_period_end: Fixed-format class — the last day of the claim-free year being credited, as YYYY-MM-DD.
        amount: Fixed-format class — the credit granted, in USD, 2 decimal places, rounded half up to the cent.

    Returns:
        A dict receipt: credit_id (str, reference of the credit entry), coverage_id (str), credit_reason (str, always
        "claim_free_year"), credit_period_end (str, YYYY-MM-DD), amount (float, USD to 2 decimal places),
        new_balance (float, the coverage's Deductible Rewards balance after the grant, USD to 2 decimal places) and
        granted_on (str, YYYY-MM-DD, today's date). A receipt carrying credit_id means the credit was granted.
    """
    cov = ctx.find("physdmg_coverages", coverage_id=coverage_id)
    customer_id = cov[0].get("customer_id", "") if cov else ""
    balance = float(cov[0].get("deductible_credit_balance") or 0) if cov else 0.0
    granted = round(float(amount), 2)
    rid = ctx.make_id("pdc_", coverage_id, credit_period_end, granted)
    ctx.create("physdmg_payments", rid, payment_id=rid, coverage_id=coverage_id, customer_id=customer_id,
               event_type="physdmg_deductible_credit_earned", credit_reason="claim_free_year",
               credit_period_end=credit_period_end, amount=granted, payment_date=ctx.now()[:10])
    new_balance = round(balance + granted, 2)
    ctx.update("physdmg_coverages", coverage_id, deductible_credit_balance=new_balance)
    return str({"credit_id": rid, "coverage_id": coverage_id, "credit_reason": "claim_free_year",
                "credit_period_end": credit_period_end, "amount": granted, "new_balance": new_balance,
                "granted_on": ctx.now()[:10]})


@tool(owner="user", rw="write")
def keep_total_loss_vehicle_b04c3b51(ctx: ToolContext, claim_number: str, settlement_amount: float) -> str:
    """The customer chooses, in person, to keep their total-loss vehicle as owner-retained salvage and accepts the
    kept-vehicle settlement. One call records one accepted settlement on the claim with the vehicle staying with
    the customer, the net settlement figure the customer accepts, no loss payee payoff, and the offer and
    acceptance both dated today; the owner-retained paperwork is still to be received, so nothing is paid by this
    action. The customer sees the settlement as accepted with the vehicle kept.

    Args:
        claim_number: Id class — the claim number of the total-loss claim, as the claims desk gives it to the
            customer before the call.
        settlement_amount: Fixed-format class — the net kept-vehicle settlement the customer accepts, in USD,
            2 decimal places, rounded half up to the cent.

    Returns:
        A dict receipt: settlement_id (str, reference of the accepted settlement), claim_number (str),
        settlement_option (str, always "owner_retained_salvage"), settlement_amount (float, USD to 2 decimal places),
        offer_status (str, always "accepted") and accepted_date (str, YYYY-MM-DD, today's date). A receipt carrying
        settlement_id means the acceptance is recorded.
    """
    report = ctx.find("physdmg_claim_events", claim_number=claim_number, event_type="physdmg_claim_report")
    coverage_id = report[0].get("coverage_id", "") if report else ""
    customer_id = report[0].get("customer_id", "") if report else ""
    amount = round(float(settlement_amount), 2)
    rid = ctx.make_id("tls_", claim_number, "owner_retained_salvage", amount)
    ctx.create("physdmg_total_loss_settlements", rid, settlement_id=rid, customer_id=customer_id,
               coverage_id=coverage_id, claim_number=claim_number, settlement_option="owner_retained_salvage",
               settlement_amount=amount, loss_payee_payoff_amount=0.0, offer_date=ctx.now()[:10],
               offer_status="accepted", accepted_date=ctx.now()[:10], title_received=False,
               created_at=ctx.now())
    return str({"settlement_id": rid, "claim_number": claim_number, "settlement_option": "owner_retained_salvage",
                "settlement_amount": amount, "offer_status": "accepted", "accepted_date": ctx.now()[:10]})

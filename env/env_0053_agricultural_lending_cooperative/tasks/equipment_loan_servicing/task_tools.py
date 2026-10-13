"""Hidden task tools of the equipment_loan_servicing difficulty (Equipment & Vehicle Loans).

Each tool performs one atomic servicing write on an equipment loan with the values the agent has
already worked out from the published servicing rules; no tool checks eligibility, history or a
prerequisite, and none computes an amount. Reached only through unlock_* -> call_*.
"""

from erlbench import ToolContext, tool


@tool(owner="agent", rw="write")
def assess_installment_late_charge_7bb353d6(ctx: ToolContext, loan_id: str, source_ref_id: str,
                                            late_charge_amount: float) -> str:
    """Book a late charge on one installment bill of a member's equipment or vehicle loan.

    The servicing representative records one late-charge fee entry against the installment bill named,
    dated today, for the amount given, and adds that amount to the loan's fees not yet paid. Once booked,
    the charge shows in the loan's transaction history as a late-charge fee pointing to that installment
    bill, and the loan's fees due rise by the same amount. A returned receipt with a fee reference means
    the charge was booked.

    Args:
        loan_id: Id class — the loan number of the equipment loan the installment belongs to, as returned by the equipment loan lookup.
        source_ref_id: Id class — the reference number of the installment bill (the interest billing entry of that installment) the late charge is charged on, as returned by the equipment loan transaction lookup.
        late_charge_amount: Fixed-format class — the late charge to book, in USD, 2 decimal places, always positive; format USD, 2 decimal places, always positive; pass the figure already rounded to cents; it is stored at 2 decimal places.

    Returns:
        A dict receipt: fee_txn_id (str, the reference number of the new late-charge fee entry), loan_id
        (str, the loan charged), source_ref_id (str, the installment bill charged), amount (float, USD,
        2 decimal places, the charge booked), effective_date (str, YYYY-MM-DD, today's date) and
        fees_due (float, USD, 2 decimal places, the loan's fees not yet paid after the charge). The
        presence of fee_txn_id indicates the charge was booked.
    """
    amt = round(float(late_charge_amount), 2)
    fid = ctx.make_id("eft_", loan_id, source_ref_id, amt)
    loan = (ctx.find("equipment_loans", loan_id=loan_id) or [{}])[0]
    ctx.create("equipment_transactions", fid, txn_id=fid, loan_id=loan_id, customer_id=loan.get("customer_id"),
               event_type="equipment_fee_assessed", amount=amt, effective_date=ctx.now()[:10], channel="system",
               payment_purpose="none", fee_code="late_charge", period_start="", period_end="", due_date="",
               rate_applied="", source_ref_id=source_ref_id, waiver_basis="none", return_reason="none")
    fees = round(float(loan.get("fees_due") or 0) + amt, 2)
    ctx.update("equipment_loans", loan_id, fees_due=fees)
    return str({"fee_txn_id": fid, "loan_id": loan_id, "source_ref_id": source_ref_id, "amount": amt,
                "effective_date": ctx.now()[:10], "fees_due": fees})


@tool(owner="agent", rw="write")
def assess_collateral_protection_premium_372633e7(ctx: ToolContext, loan_id: str, premium_amount: float) -> str:
    """Place collateral protection insurance on a member's equipment or vehicle loan and book its premium.

    The servicing representative records one collateral-protection premium fee entry on the loan named,
    dated today, for the premium given, and adds the premium to the loan's fees not yet paid. Once
    booked, the premium shows in the loan's transaction history as a collateral-protection fee and the
    loan's fees due rise by the same amount. A returned receipt with a fee reference means the coverage
    premium was booked.

    Args:
        loan_id: Id class — the loan number of the equipment loan whose units are being covered, as returned by the equipment loan lookup.
        premium_amount: Fixed-format class — the collateral protection premium to book, in USD, 2 decimal places, always positive; format USD, 2 decimal places, always positive; pass the figure already rounded to cents; it is stored at 2 decimal places.

    Returns:
        A dict receipt: fee_txn_id (str, the reference number of the new collateral-protection fee
        entry), loan_id (str, the loan charged), amount (float, USD, 2 decimal places, the premium
        booked), effective_date (str, YYYY-MM-DD, today's date, the placement date) and fees_due
        (float, USD, 2 decimal places, the loan's fees not yet paid after the premium). The presence of
        fee_txn_id indicates the premium was booked.
    """
    amt = round(float(premium_amount), 2)
    fid = ctx.make_id("ecp_", loan_id, amt)
    loan = (ctx.find("equipment_loans", loan_id=loan_id) or [{}])[0]
    ctx.create("equipment_transactions", fid, txn_id=fid, loan_id=loan_id, customer_id=loan.get("customer_id"),
               event_type="equipment_fee_assessed", amount=amt, effective_date=ctx.now()[:10], channel="system",
               payment_purpose="none", fee_code="collateral_protection", period_start="", period_end="",
               due_date="", rate_applied="", source_ref_id=None, waiver_basis="none", return_reason="none")
    fees = round(float(loan.get("fees_due") or 0) + amt, 2)
    ctx.update("equipment_loans", loan_id, fees_due=fees)
    return str({"fee_txn_id": fid, "loan_id": loan_id, "amount": amt, "effective_date": ctx.now()[:10],
                "fees_due": fees})


@tool(owner="user", rw="write")
def enrol_installment_autopay_aa82d556(ctx: ToolContext, loan_id: str, autopay_account_last4: str,
                                       interest_rate: float) -> str:
    """The member authorises automatic debit of the installments of their own equipment or vehicle loan.

    The member instructs that each installment of the loan named be debited from their checking account
    identified by its last four digits; the loan is marked as enrolled in automatic debit, the debited
    account is recorded exactly as the member gives it, and the contract rate in force from today is
    set to the rate given. Afterwards the loan shows autopay enrolled, the account's last four digits
    and the new contract rate. A returned receipt showing autopay_enrolled true means the instruction
    took effect.

    Args:
        loan_id: Id class — the loan number of the member's equipment loan to be debited, as read to the member by the servicing representative from the equipment loan lookup.
        autopay_account_last4: Fixed-format class — the last four digits of the member's checking account to be debited, exactly as the member states them; format 4 digits; empty when not enrolled (never empty for an enrolment).
        interest_rate: Fixed-format class — the contract rate in force from the enrolment date, as told to the member by the servicing representative; format annual percentage rate, 3 decimal places (for example 7.125).

    Returns:
        A dict receipt: loan_id (str, the loan enrolled), autopay_enrolled (bool, true once enrolled),
        autopay_account_last4 (str, 4 digits, the account debited), interest_rate (float, annual
        percentage rate, 3 decimal places, the contract rate now in force) and effective_date (str,
        YYYY-MM-DD, today's date). autopay_enrolled true indicates the authorisation took effect.
    """
    rate = round(float(interest_rate), 3)
    ctx.update("equipment_loans", loan_id, autopay_enrolled=True, autopay_account_last4=str(autopay_account_last4),
               interest_rate=rate)
    return str({"loan_id": loan_id, "autopay_enrolled": True, "autopay_account_last4": str(autopay_account_last4),
                "interest_rate": rate, "effective_date": ctx.now()[:10]})


@tool(owner="user", rw="write")
def release_total_loss_unit_e8bdf554(ctx: ToolContext, customer_id: str, loan_id: str, source_action_id: str,
                                     release_proceeds: float) -> str:
    """The member signs the release of their own pledged unit destroyed in a total loss and assigns the settlement.

    The member, as owner of the destroyed unit, signs its release from the loan and assigns the insurance
    settlement (with any difference the member pays) to the association: the association's lien on that one
    unit is released today with the release reason total loss, the release amount given is applied to the
    loan's principal as release proceeds, and the loan's principal balance and the pledged value securing it
    fall accordingly. Afterwards the unit shows as released in the loan's collateral record and the release
    proceeds show in its transaction history. A returned receipt with a release reference means the release
    took effect.

    Args:
        customer_id: Id class — the customer reference number of the member who owns the unit and holds the loan, as read to the member from the member profile lookup.
        loan_id: Id class — the loan number of the equipment loan the destroyed unit secures, as read to the member from the equipment loan lookup.
        source_action_id: Id class — the reference number of the pledge record of the destroyed unit, as read to the member from the equipment collateral lookup.
        release_proceeds: Fixed-format class — the release amount applied to principal for the destroyed unit, in USD, 2 decimal places, always positive; format USD, 2 decimal places, always positive; as told to the member by the servicing representative, stored at 2 decimal places.

    Returns:
        A dict receipt: release_action_id (str, reference number of the new release record), payment_txn_id
        (str, reference number of the release-proceeds principal payment), loan_id (str), serial_number (str,
        the released unit's serial number), release_proceeds (float, USD, 2 decimal places, the amount applied),
        principal_balance (float, USD, 2 decimal places, principal after the release), collateral_value (float,
        USD, 2 decimal places, pledged value still securing the loan) and action_date (str, YYYY-MM-DD, today).
        The presence of release_action_id indicates the release took effect.
    """
    amt = round(float(release_proceeds), 2)
    pledge = (ctx.find("equipment_collateral", collateral_action_id=source_action_id) or [{}])[0]
    loan = (ctx.find("equipment_loans", loan_id=loan_id) or [{}])[0]
    today = ctx.now()[:10]
    rel = ctx.make_id("ecr_", customer_id, loan_id, source_action_id, amt)
    ctx.create("equipment_collateral", rel, collateral_action_id=rel, loan_id=loan_id, customer_id=customer_id,
               event_type="equipment_unit_released", unit_description=pledge.get("unit_description"),
               serial_number=pledge.get("serial_number"), model_year=pledge.get("model_year"),
               pledged_value=pledge.get("pledged_value"), action_date=today, source_action_id=source_action_id,
               release_reason="total_loss")
    pay = ctx.make_id("epp_", rel, amt)
    ctx.create("equipment_transactions", pay, txn_id=pay, loan_id=loan_id, customer_id=customer_id,
               event_type="equipment_principal_payment", amount=amt, effective_date=today, channel="phone",
               payment_purpose="release_proceeds", fee_code="none", period_start="", period_end="", due_date="",
               rate_applied="", source_ref_id=rel, waiver_basis="none", return_reason="none")
    principal = round(float(loan.get("principal_balance") or 0) - amt, 2)
    coll = round(float(loan.get("collateral_value") or 0) - float(pledge.get("pledged_value") or 0), 2)
    ctx.update("equipment_loans", loan_id, principal_balance=principal, collateral_value=coll)
    return str({"release_action_id": rel, "payment_txn_id": pay, "loan_id": loan_id,
                "serial_number": pledge.get("serial_number"), "release_proceeds": amt,
                "principal_balance": principal, "collateral_value": coll, "action_date": today})


@tool(owner="agent", rw="write")
def apply_ltv_curtailment_c1e2b439(ctx: ToolContext, loan_id: str, curtailment_amount: float) -> str:
    """Apply a member's curtailment to the principal of an equipment or vehicle loan as a prepayment.

    The servicing representative books one principal payment, dated today and received by phone from the
    member's account, for the amount given, marked as a prepayment, and lowers the loan's principal balance by
    the same amount. Afterwards the payment shows in the loan's transaction history and the principal balance
    is reduced. A returned receipt with a payment reference means the curtailment was applied.

    Args:
        loan_id: Id class — the loan number of the equipment loan being paid down, as returned by the equipment loan lookup.
        curtailment_amount: Fixed-format class — the curtailment applied to principal, in USD, 2 decimal places, always positive; format USD, 2 decimal places, always positive; stored at 2 decimal places.

    Returns:
        A dict receipt: payment_txn_id (str, reference number of the prepayment entry), loan_id (str),
        amount (float, USD, 2 decimal places, the amount applied), principal_balance (float, USD, 2 decimal
        places, principal after the curtailment) and effective_date (str, YYYY-MM-DD, today). The presence
        of payment_txn_id indicates the curtailment was applied.
    """
    amt = round(float(curtailment_amount), 2)
    loan = (ctx.find("equipment_loans", loan_id=loan_id) or [{}])[0]
    pay = ctx.make_id("epc_", loan_id, amt)
    ctx.create("equipment_transactions", pay, txn_id=pay, loan_id=loan_id, customer_id=loan.get("customer_id"),
               event_type="equipment_principal_payment", amount=amt, effective_date=ctx.now()[:10], channel="phone",
               payment_purpose="prepayment", fee_code="none", period_start="", period_end="", due_date="",
               rate_applied="", source_ref_id=None, waiver_basis="none", return_reason="none")
    principal = round(float(loan.get("principal_balance") or 0) - amt, 2)
    ctx.update("equipment_loans", loan_id, principal_balance=principal)
    return str({"payment_txn_id": pay, "loan_id": loan_id, "amount": amt, "principal_balance": principal,
                "effective_date": ctx.now()[:10]})


@tool(owner="agent", rw="write")
def grant_installment_deferral_57477c3f(ctx: ToolContext, customer_id: str, loan_id: str, next_due_date: str,
                                        maturity_date: str, deferrals_used: int, deferral_fee: float) -> str:
    """Grant a deferral of the next scheduled installment of a member's equipment or vehicle loan.

    The servicing representative moves the next installment to the end of the schedule: the loan is set to
    deferred status, its next due date and maturity date are set to the dates given, its deferral count is set
    to the count given, today becomes its last deferral date, and one deferral fee entry for the amount given is
    booked today and added to the loan's fees not yet paid. Afterwards the loan shows deferred with the new dates
    and the fee shows in its transaction history. A returned receipt showing status deferred means the deferral
    was granted.

    Args:
        customer_id: Id class — the customer reference number of the member holding the loan, as returned by the member profile lookup.
        loan_id: Id class — the loan number of the equipment loan whose installment is deferred, as returned by the equipment loan lookup.
        next_due_date: Fixed-format class — the due date of the installment after the deferred one, which becomes the next due date; format YYYY-MM-DD.
        maturity_date: Fixed-format class — the new final installment due date after the deferral; format YYYY-MM-DD.
        deferrals_used: Fixed-format class — the loan's deferral count after this deferral; a non-negative integer.
        deferral_fee: Fixed-format class — the deferral fee to book, in USD, 2 decimal places, always positive; format USD, 2 decimal places, always positive; stored at 2 decimal places.

    Returns:
        A dict receipt: loan_id (str), status (str, deferred), next_due_date (str, YYYY-MM-DD),
        maturity_date (str, YYYY-MM-DD), deferrals_used (int), last_deferral_date (str, YYYY-MM-DD, today),
        fee_txn_id (str, reference number of the deferral fee entry), deferral_fee (float, USD, 2 decimal
        places) and fees_due (float, USD, 2 decimal places, fees not yet paid after the fee). status deferred
        indicates the deferral was granted.
    """
    fee = round(float(deferral_fee), 2)
    loan = (ctx.find("equipment_loans", loan_id=loan_id) or [{}])[0]
    today = ctx.now()[:10]
    fid = ctx.make_id("edf_", customer_id, loan_id, next_due_date, maturity_date, int(deferrals_used), fee)
    ctx.create("equipment_transactions", fid, txn_id=fid, loan_id=loan_id, customer_id=customer_id,
               event_type="equipment_fee_assessed", amount=fee, effective_date=today, channel="system",
               payment_purpose="none", fee_code="deferral", period_start="", period_end="", due_date="",
               rate_applied="", source_ref_id=None, waiver_basis="none", return_reason="none")
    fees = round(float(loan.get("fees_due") or 0) + fee, 2)
    ctx.update("equipment_loans", loan_id, status="deferred", next_due_date=next_due_date, maturity_date=maturity_date,
               deferrals_used=int(deferrals_used), last_deferral_date=today, fees_due=fees)
    return str({"loan_id": loan_id, "status": "deferred", "next_due_date": next_due_date,
                "maturity_date": maturity_date, "deferrals_used": int(deferrals_used), "last_deferral_date": today,
                "fee_txn_id": fid, "deferral_fee": fee, "fees_due": fees})

"""Hidden task tools for the operating_line_servicing difficulty of env_0053_agricultural_lending_cooperative.

Each tool performs exactly one atomic booking on an operating line of credit with the values the caller
supplies; none of them works out an amount, a rate or an eligibility for the caller, and none refuses a
booking because of the state of the line.
"""

from erlbench import ToolContext, tool


@tool(owner="agent", rw="write")
def record_certificate_borrowing_base_37c8bf27(ctx: ToolContext, certificate_id: str, line_id: str,
                                               borrowing_base_amount: float) -> str:
    """Record the association's own borrowing base on a borrowing base certificate the member has already
    delivered for an operating line. The servicing desk uses this when a received certificate still shows the
    figure the member worked out; the call replaces that figure with the borrowing base the association
    supplies, leaving the stated collateral values, the as-of date, the received date and the delivery channel
    untouched. Afterwards the certificate lists the recorded amount as its borrowing base wherever the line's
    certificates are looked up. Success is a receipt naming the certificate, the line and the amount now on it.

    Args:
        certificate_id: Id class — reference number of the delivered borrowing base certificate whose
            borrowing base is being recorded, as shown when the line's certificates are looked up.
        line_id: Id class — loan number of the operating line the certificate supports, as shown when the
            member's operating lines are looked up.
        borrowing_base_amount: Fixed-format class — the borrowing base to stand on the certificate, in USD,
            2 decimal places, positive, rounded half up to cents before it is passed; it replaces whatever
            figure the certificate carried.

    Returns:
        A dictionary rendered as text with the keys certificate_id (the certificate updated), line_id (the line
        it supports), borrowing_base_amount (the USD amount, 2 decimal places, now recorded on the certificate)
        and status (the literal "recorded", meaning the certificate now carries this borrowing base).
    """
    amount = round(float(borrowing_base_amount), 2)
    ctx.update("operating_borrowing_base", certificate_id, borrowing_base_amount=amount)
    return str({"certificate_id": certificate_id, "line_id": line_id,
                "borrowing_base_amount": amount, "status": "recorded"})


@tool(owner="agent", rw="write")
def assess_overadvance_fee_10e059b9(ctx: ToolContext, line_id: str, source_txn_id: str, amount: float) -> str:
    """Assess an overadvance fee on an operating line against the advance it arises from. One call books one
    new fee charge with the fee code for overadvances, dated today and marked as a platform booking, pointing to
    the named advance, and raises the line's fees owed by the same amount. The member then sees the new charge in
    the line's transaction history and in the fees the line shows as owed. Success is a receipt with the new
    charge's reference number.

    Args:
        line_id: Id class — loan number of the operating line the fee is charged on, as shown when the member's
            operating lines are looked up.
        source_txn_id: Id class — reference number of the advance the fee arises from, as shown in the line's
            transaction history.
        amount: Fixed-format class — the fee to charge, in USD, 2 decimal places, always positive, rounded half
            up to cents before it is passed.

    Returns:
        A dictionary rendered as text with the keys txn_id (reference number of the new fee charge), line_id
        (the line charged), fee_code (the literal "overadvance"), amount (the USD fee, 2 decimal places),
        effective_date (today's date, YYYY-MM-DD), fees_due (the line's fees owed after the charge, USD,
        2 decimal places) and status (the literal "assessed", meaning the charge is on the line).
    """
    fee = round(float(amount), 2)
    line = (ctx.find("operating_lines", line_id=line_id) or [{}])[0]
    today = ctx.now()[:10]
    rid = ctx.make_id("otx_", line_id, source_txn_id, "overadvance", fee)
    ctx.create("operating_transactions", rid, txn_id=rid, line_id=line_id, customer_id=line.get("customer_id"),
               event_type="operating_fee_assessed", amount=fee, effective_date=today, channel="system",
               disbursement_method="none", fee_code="overadvance", period_start="", period_end="",
               due_date="", rate_applied="", rate_basis="none", source_txn_id=source_txn_id,
               waiver_basis="none", return_reason="none")
    new_fees = round(float(line.get("fees_due") or 0) + fee, 2)
    ctx.update("operating_lines", line_id, fees_due=new_fees)
    return str({"txn_id": rid, "line_id": line_id, "fee_code": "overadvance", "amount": fee,
                "effective_date": today, "fees_due": new_fees, "status": "assessed"})


@tool(owner="user", rw="write")
def authorize_shortfall_paydown_62bf68fd(ctx: ToolContext, line_id: str, amount: float) -> str:
    """The member authorises a one-time debit of their own checking account for a principal paydown on one of
    their operating lines. One call books one principal payment of the stated amount, received today by phone,
    and lowers the line's outstanding principal by that amount. The member can then see the paydown in the
    line's transaction history and the lower principal on the line. Success is a receipt with the payment's
    reference number and the principal left on the line.

    Args:
        line_id: Id class — loan number of the member's operating line the paydown is applied to, as the
            servicing representative reads it out from the member's operating lines.
        amount: Fixed-format class — the principal paydown being debited, in USD, 2 decimal places, always
            positive, rounded half up to cents before it is passed.

    Returns:
        A dictionary rendered as text with the keys txn_id (reference number of the principal payment), line_id
        (the line paid down), amount (the USD paydown, 2 decimal places), effective_date (today's date,
        YYYY-MM-DD), outstanding_principal (the line's principal after the paydown, USD, 2 decimal places) and
        status (the literal "applied", meaning the paydown is on the line).
    """
    pay = round(float(amount), 2)
    line = (ctx.find("operating_lines", line_id=line_id) or [{}])[0]
    today = ctx.now()[:10]
    rid = ctx.make_id("otx_", line_id, "principal_paydown", pay, today)
    ctx.create("operating_transactions", rid, txn_id=rid, line_id=line_id, customer_id=line.get("customer_id"),
               event_type="operating_principal_payment", amount=pay, effective_date=today, channel="phone",
               disbursement_method="none", fee_code="none", period_start="", period_end="", due_date="",
               rate_applied="", rate_basis="none", source_txn_id="", waiver_basis="none", return_reason="none")
    left = round(float(line.get("outstanding_principal") or 0) - pay, 2)
    ctx.update("operating_lines", line_id, outstanding_principal=left)
    return str({"txn_id": rid, "line_id": line_id, "amount": pay, "effective_date": today,
                "outstanding_principal": left, "status": "applied"})


@tool(owner="agent", rw="write")
def assess_late_charge_706782fd(ctx: ToolContext, line_id: str, source_txn_id: str, amount: float) -> str:
    """Assess a late charge on an operating line against one interest bill. One call books one new fee charge with
    the late charge fee code, dated today and marked as a platform booking, pointing to the named interest bill,
    and raises the line's fees owed by the same amount. The member then sees the charge in the line's transaction
    history and in the fees the line shows as owed. Success is a receipt with the new charge's reference number.

    Args:
        line_id: Id class — loan number of the operating line the charge is booked on, as shown when the member's
            operating lines are looked up.
        source_txn_id: Id class — reference number of the interest bill the charge is assessed on, as shown in the
            line's transaction history.
        amount: Fixed-format class — the late charge, in USD, 2 decimal places, always positive, rounded half up to
            cents before it is passed.

    Returns:
        A dictionary rendered as text with the keys txn_id (reference number of the new late charge), line_id (the
        line charged), fee_code (the literal "late_charge"), amount (the USD charge, 2 decimal places),
        effective_date (today's date, YYYY-MM-DD), fees_due (the line's fees owed after the charge, USD, 2 decimal
        places) and status (the literal "assessed", meaning the charge is on the line).
    """
    fee = round(float(amount), 2)
    line = (ctx.find("operating_lines", line_id=line_id) or [{}])[0]
    today = ctx.now()[:10]
    rid = ctx.make_id("otx_", line_id, source_txn_id, "late_charge", fee)
    ctx.create("operating_transactions", rid, txn_id=rid, line_id=line_id, customer_id=line.get("customer_id"),
               event_type="operating_fee_assessed", amount=fee, effective_date=today, channel="system",
               disbursement_method="none", fee_code="late_charge", period_start="", period_end="",
               due_date="", rate_applied="", rate_basis="none", source_txn_id=source_txn_id,
               waiver_basis="none", return_reason="none")
    new_fees = round(float(line.get("fees_due") or 0) + fee, 2)
    ctx.update("operating_lines", line_id, fees_due=new_fees)
    return str({"txn_id": rid, "line_id": line_id, "fee_code": "late_charge", "amount": fee,
                "effective_date": today, "fees_due": new_fees, "status": "assessed"})


@tool(owner="user", rw="write")
def enroll_autodraft_36bd3fb2(ctx: ToolContext, line_id: str, account_last4: str, interest_rate: float) -> str:
    """The member authorises AutoDraft on one of their own operating lines: from the day of the call each interest
    bill on the line is debited on its due date from the checking account the member names. One call switches
    AutoDraft on for the line, records the last four digits of the account to be debited and puts the stated
    contract rate in force on the line from today. The member can then see AutoDraft shown as enrolled, the
    account digits and the new contract rate on the line. Success is a receipt confirming the enrolment.

    Args:
        line_id: Id class — loan number of the member's operating line AutoDraft is set up on, as the servicing
            representative reads it out from the member's operating lines.
        account_last4: Fixed-format class — last four digits of the member's checking account to be debited, as
            the member states them: 4 digits; empty when not enrolled — never empty on an enrolment.
        interest_rate: Fixed-format class — the contract rate in force from the enrolment, as an annual
            percentage rate, 3 decimal places (e.g. 8.375), rounded half up to 3 decimal places before it is passed.

    Returns:
        A dictionary rendered as text with the keys line_id (the line enrolled), autodraft_enrolled (the boolean
        true), autodraft_account_last4 (the 4 digits recorded), interest_rate (the annual percentage rate now in
        force, 3 decimal places), effective_date (today's date, YYYY-MM-DD) and status (the literal "enrolled",
        meaning AutoDraft is on for the line).
    """
    rate = round(float(interest_rate), 3)
    today = ctx.now()[:10]
    ctx.update("operating_lines", line_id, autodraft_enrolled=True, autodraft_account_last4=str(account_last4),
               interest_rate=rate)
    return str({"line_id": line_id, "autodraft_enrolled": True, "autodraft_account_last4": str(account_last4),
                "interest_rate": rate, "effective_date": today, "status": "enrolled"})


@tool(owner="agent", rw="write")
def book_operating_advance_f71c3718(ctx: ToolContext, line_id: str, amount: float) -> str:
    """Book an advance of principal on an operating line requested by phone, with the proceeds deposited to the
    member's checking account. One call books one advance of the stated amount, effective today, and raises the
    line's outstanding principal by that amount. The member can then see the advance in the line's transaction
    history and the higher principal on the line. Success is a receipt with the advance's reference number.

    Args:
        line_id: Id class — loan number of the operating line the advance is drawn on, as shown when the member's
            operating lines are looked up.
        amount: Fixed-format class — the principal advanced, in USD, 2 decimal places, always positive, rounded
            half up to cents before it is passed.

    Returns:
        A dictionary rendered as text with the keys txn_id (reference number of the advance), line_id (the line
        drawn on), amount (the USD advance, 2 decimal places), effective_date (today's date, YYYY-MM-DD),
        disbursement_method (the literal "deposit_to_checking"), outstanding_principal (the line's principal after
        the advance, USD, 2 decimal places) and status (the literal "booked", meaning the advance is on the line).
    """
    adv = round(float(amount), 2)
    line = (ctx.find("operating_lines", line_id=line_id) or [{}])[0]
    today = ctx.now()[:10]
    rid = ctx.make_id("otx_", line_id, "advance", adv, today)
    ctx.create("operating_transactions", rid, txn_id=rid, line_id=line_id, customer_id=line.get("customer_id"),
               event_type="operating_draw", amount=adv, effective_date=today, channel="phone",
               disbursement_method="deposit_to_checking", fee_code="none", period_start="", period_end="",
               due_date="", rate_applied="", rate_basis="none", source_txn_id="", waiver_basis="none",
               return_reason="none")
    owed = round(float(line.get("outstanding_principal") or 0) + adv, 2)
    ctx.update("operating_lines", line_id, outstanding_principal=owed)
    return str({"txn_id": rid, "line_id": line_id, "amount": adv, "effective_date": today,
                "disbursement_method": "deposit_to_checking", "outstanding_principal": owed, "status": "booked"})

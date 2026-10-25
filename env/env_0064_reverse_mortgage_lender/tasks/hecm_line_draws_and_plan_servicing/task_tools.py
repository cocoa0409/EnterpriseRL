"""Hidden task tools for the hecm_line_draws_and_plan_servicing difficulty (Cedarline Reverse Mortgage, LLC).

Each tool performs one atomic servicing write on a HECM loan with the figures the caller supplies;
none of them checks eligibility, ownership, timing or prior steps, and none computes an amount.
"""

from erlbench import ToolContext, tool


@tool(owner="user", rw="write")
def submit_line_draw_request_b0795434(ctx: ToolContext, hecm_loan_id: str, customer_id: str,
                                      requested_amount: float, disbursement_method: str) -> str:
    """The borrower submits their own line-of-credit draw request on their HECM loan through the
    Cedarline servicing portal. One call files one new draw request for the stated amount and
    disbursement method, dated today and waiting for processing; nothing is disbursed and neither
    the available line nor the loan balance changes. Afterwards the borrower can quote the request
    reference number, and the request shows as submitted until it is processed or declined.

    Args:
        hecm_loan_id: Id class — reference number of the borrower's HECM loan, as returned by the HECM loan lookup for that borrower.
        customer_id: Id class — customer reference number of the borrower filing the request, as returned by the customer profile lookup.
        requested_amount: Fixed-format class — the draw amount requested, in US dollars as a positive decimal number with exactly 2 decimal places (cents); the value is stored as given, rounded half up to the cent.
        disbursement_method: Enum class — how the borrower wants the funds sent, exactly one of: "ach" — a direct deposit to the borrower's bank account on file; "wire" — a same-day bank wire to the borrower's account on file; "check" — a paper check mailed to the borrower's mailing address on file; "not_applicable" — no funds to send, which applies only to requests that are not draws and so is never the right value for a draw request.

    Returns:
        A confirmation sentence (string) giving the new draw request reference number (text id beginning
        "hrq_"), the loan reference number, the requested amount in US dollars with 2 decimals, the
        disbursement method, the channel servicing_portal, the request date (YYYY-MM-DD, today) and the
        status submitted; a sentence containing "Draw request submitted" means the request is on file.
    """
    amount = round(float(requested_amount), 2)
    rid = ctx.make_id("hrq_", hecm_loan_id, customer_id, amount, disbursement_method)
    today = ctx.now()[:10]
    ctx.create("hecm_requests", rid, hecm_request_id=rid, customer_id=customer_id, hecm_loan_id=hecm_loan_id,
               request_type="loc_draw", requested_amount=amount, requested_plan="not_applicable",
               requested_term_months=0, disbursement_method=disbursement_method,
               request_channel="servicing_portal", request_date=today, request_status="submitted",
               decline_reason="not_applicable", created_at=ctx.now())
    return (f"Draw request submitted: reference {rid} on loan {hecm_loan_id} for {amount:.2f} USD by "
            f"{disbursement_method}, channel servicing_portal, dated {today}, status submitted.")


@tool(owner="agent", rw="write")
def void_uncashed_draw_check_f08764ed(ctx: ToolContext, hecm_loan_id: str, source_txn_ref: str,
                                      line_credit_amount: float, reversal_amount: float) -> str:
    """Void a line-of-credit draw check that was never cashed and settle it on the HECM loan. One
    call books, dated today, a return entry crediting the stated amount back to the loan's available
    line and a reversal entry taking the stated amount off the loan balance, both referencing the
    original draw; the loan's available line rises by the line credit and its balance falls by the
    reversal. Afterwards the borrower's available line and balance show the settled figures.

    Args:
        hecm_loan_id: Id class — reference number of the HECM loan the check was drawn on, as returned by the HECM loan lookup.
        source_txn_ref: Id class — reference number of the original line-of-credit draw entry (the draw itself, not its balance posting), as returned by the HECM transaction lookup for the loan.
        line_credit_amount: Fixed-format class — the amount credited back to the available line, in US dollars as a positive decimal number with exactly 2 decimal places; stored as given, rounded half up to the cent.
        reversal_amount: Fixed-format class — the amount taken off the loan balance, in US dollars as a positive decimal number with exactly 2 decimal places; stored as given, rounded half up to the cent.

    Returns:
        A confirmation sentence (string) giving the return entry reference (text id beginning "htr_"),
        the reversal entry reference (text id beginning "hrv_"), the original draw reference, the
        line credit and the balance reversal in US dollars with 2 decimals, the effective date
        (YYYY-MM-DD, today), and the loan's new available line and new balance in US dollars with 2
        decimals; a sentence beginning "Draw check voided" means both entries are booked.
    """
    credit = round(float(line_credit_amount), 2)
    reversal = round(float(reversal_amount), 2)
    today = ctx.now()[:10]
    rows = ctx.find("hecm_loans", hecm_loan_id=hecm_loan_id)
    loan = rows[0] if rows else {}
    cust = loan.get("customer_id", "")
    ret_id = ctx.make_id("htr_", hecm_loan_id, source_txn_ref, credit, reversal)
    rev_id = ctx.make_id("hrv_", hecm_loan_id, source_txn_ref, credit, reversal)
    ctx.create("hecm_transactions", ret_id, hecm_txn_id=ret_id, hecm_loan_id=hecm_loan_id, customer_id=cust,
               event_type="hecm_disbursement_return", amount=credit, effective_date=today, accrual_period="",
               hecm_request_id="", disbursement_method="check", advance_type="not_applicable",
               allocation_bucket="not_applicable", restores_line=False, rate_applied_pct="",
               source_txn_ref=source_txn_ref)
    ctx.create("hecm_transactions", rev_id, hecm_txn_id=rev_id, hecm_loan_id=hecm_loan_id, customer_id=cust,
               event_type="hecm_advance_reversal", amount=reversal, effective_date=today, accrual_period="",
               hecm_request_id="", disbursement_method="not_applicable", advance_type="loc_draw",
               allocation_bucket="not_applicable", restores_line=False, rate_applied_pct="",
               source_txn_ref=source_txn_ref)
    new_line = round(float(loan.get("available_line") or 0) + credit, 2)
    new_bal = round(float(loan.get("principal_balance") or 0) - reversal, 2)
    ctx.update("hecm_loans", hecm_loan_id, available_line=new_line, principal_balance=new_bal)
    return (f"Draw check voided: return {ret_id} credits {credit:.2f} USD to the line and reversal {rev_id} "
            f"takes {reversal:.2f} USD off the balance for draw {source_txn_ref}, effective {today}; "
            f"available line now {new_line:.2f} USD, balance now {new_bal:.2f} USD.")


@tool(owner="agent", rw="write")
def convert_payout_plan_to_line_d82e9c7e(ctx: ToolContext, hecm_loan_id: str, hecm_request_id: str,
                                         release_amount: float) -> str:
    """Process a borrower's signed payout plan change request that moves a HECM loan off scheduled
    monthly payments and onto the HECM Line of Credit. One call, dated today, books a release entry
    returning the stated amount to the loan's available line, switches the loan's payout plan to HECM
    Line of Credit with no scheduled payment (payment 0.00, term 0, no start month), charges the
    plan change processing fee of 20.00 USD to the loan balance, and marks the request processed.
    Afterwards the borrower sees the Line of Credit plan, the larger available line and the fee on
    the balance.

    Args:
        hecm_loan_id: Id class — reference number of the HECM loan whose plan changes, as returned by the HECM loan lookup.
        hecm_request_id: Id class — reference number of the borrower's signed payout plan change request on that loan, as returned by the HECM request lookup.
        release_amount: Fixed-format class — the amount returned to the available line, in US dollars as a positive decimal number with exactly 2 decimal places; stored as given, rounded half up to the cent.

    Returns:
        A confirmation sentence (string) giving the release entry reference (text id beginning "hrl_"),
        the processing fee entry reference (text id beginning "hpf_"), the request reference, the
        released amount and the 20.00 USD fee in US dollars with 2 decimals, the effective date
        (YYYY-MM-DD, today), the new payout plan HECM Line of Credit, and the loan's new available
        line and new balance in US dollars with 2 decimals; a sentence beginning "Plan change
        processed" means the change, the release and the fee are all booked and the request is processed.
    """
    release = round(float(release_amount), 2)
    fee = 20.00
    today = ctx.now()[:10]
    rows = ctx.find("hecm_loans", hecm_loan_id=hecm_loan_id)
    loan = rows[0] if rows else {}
    cust = loan.get("customer_id", "")
    rel_id = ctx.make_id("hrl_", hecm_loan_id, hecm_request_id, release)
    fee_id = ctx.make_id("hpf_", hecm_loan_id, hecm_request_id, release)
    ctx.create("hecm_transactions", rel_id, hecm_txn_id=rel_id, hecm_loan_id=hecm_loan_id, customer_id=cust,
               event_type="hecm_line_release", amount=release, effective_date=today, accrual_period="",
               hecm_request_id=hecm_request_id, disbursement_method="not_applicable",
               advance_type="not_applicable", allocation_bucket="not_applicable", restores_line=False,
               rate_applied_pct="", source_txn_ref="")
    ctx.create("hecm_transactions", fee_id, hecm_txn_id=fee_id, hecm_loan_id=hecm_loan_id, customer_id=cust,
               event_type="hecm_plan_change_fee", amount=fee, effective_date=today, accrual_period="",
               hecm_request_id=hecm_request_id, disbursement_method="not_applicable",
               advance_type="not_applicable", allocation_bucket="not_applicable", restores_line=False,
               rate_applied_pct="", source_txn_ref="")
    new_line = round(float(loan.get("available_line") or 0) + release, 2)
    new_bal = round(float(loan.get("principal_balance") or 0) + fee, 2)
    ctx.update("hecm_loans", hecm_loan_id, variant_name="HECM Line of Credit", scheduled_payment_amount=0.0,
               scheduled_payment_term_months=0, scheduled_payment_start_period="",
               available_line=new_line, principal_balance=new_bal)
    ctx.update("hecm_requests", hecm_request_id, request_status="processed", decline_reason="not_applicable")
    return (f"Plan change processed: request {hecm_request_id} moves loan {hecm_loan_id} to HECM Line of Credit; "
            f"release {rel_id} returns {release:.2f} USD to the line and fee {fee_id} charges {fee:.2f} USD, "
            f"effective {today}; available line now {new_line:.2f} USD, balance now {new_bal:.2f} USD.")


@tool(owner="agent", rw="write")
def restore_reinstated_line_c85e4df8(ctx: ToolContext, hecm_loan_id: str, source_txn_ref: str,
                                     restore_amount: float) -> str:
    """Credit back to a reinstated HECM loan's available line the reinstatement restoration for a
    prepaid portion that was applied while the loan was due and payable. One call books, dated today,
    one line restoration entry for the stated amount referencing that prepaid portion, and raises the
    loan's available line by the same amount; the loan balance does not change. Afterwards the
    borrower sees the higher available line and the restoration entry on the loan history.

    Args:
        hecm_loan_id: Id class — reference number of the reinstated HECM loan, as returned by the HECM loan lookup.
        source_txn_ref: Id class — reference number of the prepaid portion (a prepayment entry posted while the loan was due and payable) being restored, as returned by the HECM transaction lookup for the loan.
        restore_amount: Fixed-format class — the amount credited back to the available line, in US dollars as a positive decimal number with exactly 2 decimal places; stored as given, rounded half up to the cent.

    Returns:
        A confirmation sentence (string) giving the restoration entry reference (text id beginning
        "hrs_"), the prepaid portion it references, the amount restored in US dollars with 2 decimals,
        the effective date (YYYY-MM-DD, today) and the loan's new available line in US dollars with 2
        decimals; a sentence beginning "Line restoration booked" means the entry is on the loan.
    """
    amount = round(float(restore_amount), 2)
    today = ctx.now()[:10]
    rows = ctx.find("hecm_loans", hecm_loan_id=hecm_loan_id)
    loan = rows[0] if rows else {}
    rid = ctx.make_id("hrs_", hecm_loan_id, source_txn_ref, amount)
    ctx.create("hecm_transactions", rid, hecm_txn_id=rid, hecm_loan_id=hecm_loan_id, customer_id=loan.get("customer_id", ""),
               event_type="hecm_line_restore", amount=amount, effective_date=today, accrual_period="",
               hecm_request_id=None, disbursement_method="not_applicable", advance_type="not_applicable",
               allocation_bucket="not_applicable", restores_line=False, rate_applied_pct="", source_txn_ref=source_txn_ref)
    new_line = round(float(loan.get("available_line") or 0) + amount, 2)
    ctx.update("hecm_loans", hecm_loan_id, available_line=new_line)
    return (f"Line restoration booked: entry {rid} restores {amount:.2f} USD for prepaid portion {source_txn_ref}, "
            f"effective {today}; available line now {new_line:.2f} USD.")


@tool(owner="user", rw="write")
def sign_payout_plan_change_346bec33(ctx: ToolContext, hecm_loan_id: str, customer_id: str, requested_plan: str,
                                     requested_term_months: int, requested_amount: float) -> str:
    """The borrower signs and submits their own payout plan change request on their HECM loan as a
    signed written request. One call files one new request naming the payout plan wanted, the term in
    months for a term-based plan and the amount of the line the borrower designates to fund monthly
    payments, dated today and waiting for processing; the loan itself does not change. Afterwards the
    borrower can quote the request reference, and the request shows as submitted until processed.

    Args:
        hecm_loan_id: Id class — reference number of the borrower's HECM loan, as returned by the HECM loan lookup for that borrower.
        customer_id: Id class — customer reference number of the borrower signing the request, as returned by the customer profile lookup.
        requested_plan: Enum class — the payout plan the borrower asks to move to, exactly one of: "HECM Line of Credit" — draws only, no monthly payments; "HECM Tenure Payment Plan" — equal monthly payments for as long as a borrower lives in the home, the whole line committed; "HECM Term Payment Plan" — equal monthly payments for a fixed number of months, the whole line committed; "HECM Modified Tenure Plan" — lifetime monthly payments funded by a designated part of the line, the rest kept as a line; "HECM Modified Term Plan" — monthly payments for a fixed number of months funded by a designated part of the line, the rest kept as a line; "HECM Fixed-Rate Single Disbursement" — the closed-end fixed-rate plan, which no adjustable loan can move to; "not_applicable" — no plan change, which applies only to requests that are not plan changes and so is never the right value here.
        requested_term_months: Fixed-format class — the number of monthly payments wanted for a term-based plan, an integer count of months; 0 for a plan that is not term-based.
        requested_amount: Fixed-format class — the amount of the line designated to fund the monthly payments of a Modified plan, in US dollars as a decimal number with exactly 2 decimal places; 0.00 for any other plan; stored as given, rounded half up to the cent.

    Returns:
        A confirmation sentence (string) giving the new request reference number (text id beginning
        "hpc_"), the loan reference number, the plan requested, the term in months, the designated amount
        in US dollars with 2 decimals, the channel signed_written, the request date (YYYY-MM-DD, today)
        and the status submitted; a sentence beginning "Plan change request signed" means the request is
        on file.
    """
    amount = round(float(requested_amount), 2)
    term = int(requested_term_months)
    today = ctx.now()[:10]
    rid = ctx.make_id("hpc_", hecm_loan_id, customer_id, requested_plan, term, amount)
    ctx.create("hecm_requests", rid, hecm_request_id=rid, customer_id=customer_id, hecm_loan_id=hecm_loan_id,
               request_type="payment_plan_change", requested_amount=amount, requested_plan=requested_plan,
               requested_term_months=term, disbursement_method="not_applicable", request_channel="signed_written",
               request_date=today, request_status="submitted", decline_reason="not_applicable", created_at=ctx.now())
    return (f"Plan change request signed: reference {rid} on loan {hecm_loan_id} for {requested_plan}, term {term} months, "
            f"designated {amount:.2f} USD, channel signed_written, dated {today}, status submitted.")


@tool(owner="agent", rw="write")
def process_payout_plan_change_72a1f37c(ctx: ToolContext, hecm_loan_id: str, hecm_request_id: str, new_plan: str,
                                        committed_amount: float, scheduled_payment_amount: float,
                                        scheduled_payment_term_months: int, scheduled_payment_start_period: str) -> str:
    """Process a borrower's signed payout plan change request that moves a HECM loan from a plan without scheduled payments onto a plan with
    monthly scheduled payments. One call, dated today, books a line commitment entry taking the stated
    committed amount out of the available line, records the new payout plan with its monthly scheduled
    payment, term and first payment month on the loan, charges the plan change processing fee of
    20.00 USD to the loan balance, and marks the request processed. Afterwards the borrower sees the
    new plan, the monthly payment and its start month, the smaller available line and the fee.

    Args:
        hecm_loan_id: Id class — reference number of the HECM loan whose plan changes, as returned by the HECM loan lookup.
        hecm_request_id: Id class — reference number of the borrower's signed payout plan change request on that loan, as returned by the HECM request lookup.
        new_plan: Enum class — the payout plan recorded on the loan, exactly one of: "HECM Line of Credit" — draws only, no scheduled payment; a change onto it is not processed by this call, which then returns an error and books nothing; "HECM Tenure Payment Plan" — lifetime payments with the whole line committed; "HECM Term Payment Plan" — fixed-term payments with the whole line committed; "HECM Modified Tenure Plan" — lifetime payments from a designated part of the line; "HECM Modified Term Plan" — fixed-term payments from a designated part of the line; "HECM Fixed-Rate Single Disbursement" — the closed-end fixed-rate plan, never the result of a change; this call then returns an error and books nothing.
        committed_amount: Fixed-format class — the amount taken out of the available line to fund the payments, in US dollars as a positive decimal number with exactly 2 decimal places; stored as given, rounded half up to the cent.
        scheduled_payment_amount: Fixed-format class — the new monthly scheduled payment, in US dollars as a positive decimal number with exactly 2 decimal places; stored as given, rounded half up to the cent.
        scheduled_payment_term_months: Fixed-format class — the number of monthly payments for a term-based plan, an integer count of months; 0 for a plan that is not term-based.
        scheduled_payment_start_period: Fixed-format class — the first month in which the new payments are disbursed, written YYYY-MM (four-digit year, hyphen, two-digit month).

    Returns:
        A confirmation sentence (string) giving the commitment entry reference (text id beginning "hcm_"),
        the processing fee entry reference (text id beginning "hpf_"), the request reference, the new
        payout plan, the committed amount, the monthly payment and the 20.00 USD fee in US dollars with 2
        decimals, the term in months, the first payment month (YYYY-MM), the effective date (YYYY-MM-DD,
        today), and the loan's new available line and new balance in US dollars with 2 decimals; a
        sentence beginning "Plan change processed" means every entry is booked and the request is processed; a string beginning "Error:" means nothing was booked, which happens for the two plans named above as not processed here and for a loan whose current plan already pays scheduled payments.
    """
    if new_plan in ("HECM Line of Credit", "HECM Fixed-Rate Single Disbursement"):
        return "Error: this call processes only a change onto a plan with monthly scheduled payments; nothing was booked."
    committed = round(float(committed_amount), 2)
    payment = round(float(scheduled_payment_amount), 2)
    term = int(scheduled_payment_term_months)
    fee = 20.00
    today = ctx.now()[:10]
    rows = ctx.find("hecm_loans", hecm_loan_id=hecm_loan_id)
    loan = rows[0] if rows else {}
    if float(loan.get("scheduled_payment_amount") or 0) > 0:
        return "Error: the loan's current plan pays scheduled payments; this call processes only a change from a plan without scheduled payments; nothing was booked."
    cust = loan.get("customer_id", "")
    com_id = ctx.make_id("hcm_", hecm_loan_id, hecm_request_id, new_plan, committed, payment, term, scheduled_payment_start_period)
    fee_id = ctx.make_id("hpf_", hecm_loan_id, hecm_request_id, new_plan, committed, payment, term, scheduled_payment_start_period)
    ctx.create("hecm_transactions", com_id, hecm_txn_id=com_id, hecm_loan_id=hecm_loan_id, customer_id=cust,
               event_type="hecm_line_commitment", amount=committed, effective_date=today, accrual_period="",
               hecm_request_id=hecm_request_id, disbursement_method="not_applicable", advance_type="not_applicable",
               allocation_bucket="not_applicable", restores_line=False, rate_applied_pct="", source_txn_ref="")
    ctx.create("hecm_transactions", fee_id, hecm_txn_id=fee_id, hecm_loan_id=hecm_loan_id, customer_id=cust,
               event_type="hecm_plan_change_fee", amount=fee, effective_date=today, accrual_period="",
               hecm_request_id=hecm_request_id, disbursement_method="not_applicable", advance_type="not_applicable",
               allocation_bucket="not_applicable", restores_line=False, rate_applied_pct="", source_txn_ref="")
    new_line = round(float(loan.get("available_line") or 0) - committed, 2)
    new_bal = round(float(loan.get("principal_balance") or 0) + fee, 2)
    ctx.update("hecm_loans", hecm_loan_id, variant_name=new_plan, scheduled_payment_amount=payment,
               scheduled_payment_term_months=term, scheduled_payment_start_period=scheduled_payment_start_period,
               available_line=new_line, principal_balance=new_bal)
    ctx.update("hecm_requests", hecm_request_id, request_status="processed", decline_reason="not_applicable")
    return (f"Plan change processed: request {hecm_request_id} moves loan {hecm_loan_id} to {new_plan}; commitment {com_id} "
            f"takes {committed:.2f} USD from the line, monthly payment {payment:.2f} USD for term {term} months from "
            f"{scheduled_payment_start_period}, fee {fee_id} charges {fee:.2f} USD, effective {today}; available line now "
            f"{new_line:.2f} USD, balance now {new_bal:.2f} USD.")

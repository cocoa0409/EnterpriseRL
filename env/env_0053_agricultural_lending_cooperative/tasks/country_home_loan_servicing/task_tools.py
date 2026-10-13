"""Hidden task tools for the country_home_loan_servicing difficulty (Rural Home Loans, category homeloan).

Each tool performs one atomic servicing write on a member's Country Home loan with the values the
agent (or the member, for owner="user" tools) has already worked out from the published servicing
rules. No tool checks eligibility, status, ownership, timing or any other policy condition, and no
tool returns a policy refusal; the decisions belong to the caller.
"""

from erlbench import ToolContext, tool


class _Ledger:
    """Shared helpers (not tools), kept as static methods so the module defines tools only."""

    @staticmethod
    def unpaid(ctx: ToolContext, assessment: dict) -> float:
        # The part of one fee assessment not yet paid or waived.
        relieved = sum(float(r.get("amount") or 0)
                       for r in ctx.find("homeloan_transactions", source_ref_id=assessment["txn_id"])
                       if r.get("event_type") in ("homeloan_fee_payment", "homeloan_fee_waiver"))
        return round(float(assessment.get("amount") or 0) - relieved, 2)

    @staticmethod
    def loan(ctx: ToolContext, loan_id: str) -> dict:
        rows = ctx.find("homeloan_loans", loan_id=loan_id)
        return rows[0] if rows else {}


@tool(owner="agent", rw="write")
def assess_late_charge_eed44226(ctx: ToolContext, loan_id: str, source_ref_id: str,
                                late_charge_amount: float) -> str:
    """Book the late charge on one monthly payment of a Country Home loan.

    Records one late-charge assessment against the monthly bill named, dated today, and adds the
    amount to the fees the loan has outstanding. The charge then appears in the loan's payment
    history as a late-charge fee pointing to that monthly bill, and the loan's unpaid fees rise by
    the amount booked. Nothing is collected by this action.

    Args:
        loan_id: Id class — the loan number of the Country Home loan, as returned by the home loan lookup.
        source_ref_id: Id class — the reference number of the monthly interest bill (the monthly payment) the charge is booked against, as shown in the loan's payment history.
        late_charge_amount: Fixed-format class — the late charge in USD, 2 decimal places, always positive; pass the figure already rounded to the cent.

    Returns:
        A dictionary receipt: fee_txn_id (reference number of the late-charge entry, a string),
        source_ref_id (the monthly bill charged, a string), amount (the charge booked, USD to 2 decimal
        places), fees_due (the loan's unpaid fees after the booking, USD to 2 decimal places) and status
        ("booked" when the charge is on the loan).
    """
    loan = _Ledger.loan(ctx, loan_id)
    amount = round(float(late_charge_amount), 2)
    rid = ctx.make_id("hlf_", loan_id, source_ref_id, amount, "late_charge")
    ctx.create("homeloan_transactions", rid, txn_id=rid, loan_id=loan_id, customer_id=loan.get("customer_id", ""),
               event_type="homeloan_fee_assessed", amount=amount, effective_date=ctx.now()[:10],
               channel="system", payment_purpose="none", fee_code="late_charge", due_date="",
               rate_applied="", source_ref_id=source_ref_id, waiver_basis="none", return_reason="none")
    fees = round(float(loan.get("fees_due") or 0) + amount, 2)
    ctx.update("homeloan_loans", loan_id, fees_due=fees)
    return str({"fee_txn_id": rid, "source_ref_id": source_ref_id, "amount": amount, "fees_due": fees,
                "status": "booked"})


@tool(owner="agent", rw="write")
def assess_returned_item_fee_25e49e31(ctx: ToolContext, loan_id: str, source_ref_id: str,
                                      fee_amount: float) -> str:
    """Book the returned-payment fee for one returned remittance on a Country Home loan.

    Records one returned-payment fee assessment against the returned principal entry named (the entry
    that reversed the principal share of the remittance the bank sent back), dated today, and adds the
    amount to the loan's outstanding fees. The fee then appears in the payment history pointing to that
    returned entry, and the loan's unpaid fees rise by the amount booked. Nothing is collected here.

    Args:
        loan_id: Id class — the loan number of the Country Home loan, as returned by the home loan lookup.
        source_ref_id: Id class — the reference number of the returned principal entry of the remittance that came back unpaid, as shown in the loan's payment history.
        fee_amount: Fixed-format class — the returned-payment fee in USD, 2 decimal places, always positive; pass the figure already rounded to the cent.

    Returns:
        A dictionary receipt: fee_txn_id (reference number of the fee entry, a string), source_ref_id
        (the returned entry the fee is booked against, a string), amount (the fee booked, USD to 2
        decimal places), fees_due (the loan's unpaid fees after the booking, USD to 2 decimal places)
        and status ("booked" when the fee is on the loan).
    """
    loan = _Ledger.loan(ctx, loan_id)
    amount = round(float(fee_amount), 2)
    rid = ctx.make_id("hlr_", loan_id, source_ref_id, amount, "returned_payment")
    ctx.create("homeloan_transactions", rid, txn_id=rid, loan_id=loan_id, customer_id=loan.get("customer_id", ""),
               event_type="homeloan_fee_assessed", amount=amount, effective_date=ctx.now()[:10],
               channel="system", payment_purpose="none", fee_code="returned_payment", due_date="",
               rate_applied="", source_ref_id=source_ref_id, waiver_basis="none", return_reason="none")
    fees = round(float(loan.get("fees_due") or 0) + amount, 2)
    ctx.update("homeloan_loans", loan_id, fees_due=fees)
    return str({"fee_txn_id": rid, "source_ref_id": source_ref_id, "amount": amount, "fees_due": fees,
                "status": "booked"})


@tool(owner="agent", rw="write")
def apply_replacement_remittance_c604a214(ctx: ToolContext, loan_id: str, bill_txn_id: str,
                                          remittance_amount: float) -> str:
    """Apply a member's replacement remittance, taken by phone, to a monthly payment that a returned remittance reopened.

    The remittance is booked against the monthly bill named. The interest, principal and escrow
    shares that the bank return reversed on that bill are booked again at the amounts the reversal
    carried; out of what is left, the fees unpaid on the loan are paid one by one in the order they
    were assessed, each up to its unpaid amount; anything still left is booked as an extra principal
    payment (curtailment). The
    loan's principal, billed interest, escrow balance and unpaid fees move by the amounts booked, and
    the reopened monthly payment shows as paid in the payment history.

    Args:
        loan_id: Id class — the loan number of the Country Home loan, as returned by the home loan lookup.
        bill_txn_id: Id class — the reference number of the reopened monthly interest bill (the monthly payment being replaced), as shown in the loan's payment history.
        remittance_amount: Fixed-format class — the whole remittance taken from the member, in USD to 2 decimal places, rounded to the cent.

    Returns:
        A dictionary receipt: bill_txn_id (the monthly bill paid, a string), interest_paid,
        principal_paid and escrow_paid (the shares booked again, USD to 2 decimal places), fees_paid
        (fees paid in total, USD to 2 decimal places), curtailment (any
        extra principal booked, USD to 2 decimal places, 0.0 when none), principal_balance and
        fees_due (the loan's figures after the booking, USD to 2 decimal places) and status ("applied").
    """
    loan = _Ledger.loan(ctx, loan_id)
    cust = loan.get("customer_id", "")
    bill = (ctx.find("homeloan_transactions", txn_id=bill_txn_id) or [{}])[0]
    due = bill.get("due_date", "")
    today = ctx.now()[:10]
    total = round(float(remittance_amount), 2)

    def _reversed(table, event_type):
        return round(sum(float(r.get("amount") or 0) for r in ctx.find(table, loan_id=loan_id, event_type=event_type)
                         if r.get("due_date") == due), 2)

    interest = _reversed("homeloan_transactions", "homeloan_interest_payment_return")
    principal = _reversed("homeloan_transactions", "homeloan_principal_payment_return")
    escrow = _reversed("homeloan_escrow", "homeloan_escrow_deposit_return")
    base = dict(loan_id=loan_id, customer_id=cust, effective_date=today, channel="phone", rate_applied="",
                waiver_basis="none", return_reason="none")
    rid_i = ctx.make_id("hli_", loan_id, bill_txn_id, total, "interest")
    ctx.create("homeloan_transactions", rid_i, txn_id=rid_i, event_type="homeloan_interest_payment", amount=interest,
               payment_purpose="none", fee_code="none", due_date=due, source_ref_id=bill_txn_id, **base)
    rid_p = ctx.make_id("hlp_", loan_id, bill_txn_id, total, "principal")
    ctx.create("homeloan_transactions", rid_p, txn_id=rid_p, event_type="homeloan_principal_payment", amount=principal,
               payment_purpose="scheduled", fee_code="none", due_date=due, source_ref_id=bill_txn_id, **base)
    rid_e = ctx.make_id("hle_", loan_id, bill_txn_id, total, "escrow")
    ctx.create("homeloan_escrow", rid_e, escrow_txn_id=rid_e, loan_id=loan_id, customer_id=cust,
               event_type="homeloan_escrow_deposit", amount=escrow, effective_date=today, deposit_type="monthly",
               disbursement_type="none", payee="", coverage_period="", due_date=due, source_ref_id="",
               channel="phone")
    left = round(total - interest - principal - escrow, 2)
    owed = sorted((r for r in ctx.find("homeloan_transactions", loan_id=loan_id, event_type="homeloan_fee_assessed")
                   if _Ledger.unpaid(ctx, r) > 0), key=lambda r: (r.get("effective_date", ""), r.get("txn_id", "")))
    fees_paid = 0.0
    for fee in owed:
        pay = round(min(max(left, 0.0), _Ledger.unpaid(ctx, fee)), 2)
        if pay <= 0:
            continue
        rid_f = ctx.make_id("hlq_", loan_id, bill_txn_id, total, fee["txn_id"])
        ctx.create("homeloan_transactions", rid_f, txn_id=rid_f, event_type="homeloan_fee_payment", amount=pay,
                   payment_purpose="none", fee_code=fee.get("fee_code", "none"), due_date="",
                   source_ref_id=fee["txn_id"], **base)
        left = round(left - pay, 2)
        fees_paid = round(fees_paid + pay, 2)
    curtail = round(max(left, 0.0), 2)
    if curtail > 0:
        rid_c = ctx.make_id("hlc_", loan_id, bill_txn_id, total, "curtailment")
        ctx.create("homeloan_transactions", rid_c, txn_id=rid_c, event_type="homeloan_principal_payment",
                   amount=curtail, payment_purpose="curtailment", fee_code="none", due_date="", source_ref_id="",
                   **base)
    new_principal = round(float(loan.get("principal_balance") or 0) - principal - curtail, 2)
    new_fees = round(float(loan.get("fees_due") or 0) - fees_paid, 2)
    ctx.update("homeloan_loans", loan_id, principal_balance=new_principal,
               accrued_interest=round(float(loan.get("accrued_interest") or 0) - interest, 2),
               escrow_balance=round(float(loan.get("escrow_balance") or 0) + escrow, 2), fees_due=new_fees)
    return str({"bill_txn_id": bill_txn_id, "interest_paid": interest, "principal_paid": principal,
                "escrow_paid": escrow, "fees_paid": fees_paid, "curtailment": curtail,
                "principal_balance": new_principal, "fees_due": new_fees, "status": "applied"})


@tool(owner="user", rw="write")
def pay_escrow_shortage_8ff65e44(ctx: ToolContext, loan_id: str, shortage_amount: float) -> str:
    """Pay the escrow shortage of a Country Home loan at once, by a one-time debit the member authorises.

    The member authorises a one-time debit of their own account for the amount given, which is
    deposited to the loan's escrow account as a lump-sum shortage payment dated today. The escrow
    balance rises by that amount, the deposit shows in the escrow activity as a shortage payment, and
    no shortage spread is added to later monthly payments for it.

    Args:
        loan_id: Id class — the loan number of the Country Home loan, as the servicing agent reads it out from the loan record.
        shortage_amount: Fixed-format class — the shortage being paid, in USD, 2 decimal places, always positive, as the agent states it.

    Returns:
        A dictionary receipt: escrow_txn_id (reference number of the shortage deposit, a string),
        amount (the deposit, USD to 2 decimal places), escrow_balance (the escrow balance after the
        deposit, USD to 2 decimal places) and status ("deposited" when the payment is on the escrow
        account).
    """
    loan = _Ledger.loan(ctx, loan_id)
    amount = round(float(shortage_amount), 2)
    rid = ctx.make_id("hls_", loan_id, amount, "shortage_lump_sum")
    ctx.create("homeloan_escrow", rid, escrow_txn_id=rid, loan_id=loan_id, customer_id=loan.get("customer_id", ""),
               event_type="homeloan_escrow_deposit", amount=amount, effective_date=ctx.now()[:10],
               deposit_type="shortage_lump_sum", disbursement_type="none", payee="", coverage_period="",
               due_date="", source_ref_id="", channel="phone")
    balance = round(float(loan.get("escrow_balance") or 0) + amount, 2)
    ctx.update("homeloan_loans", loan_id, escrow_balance=balance)
    return str({"escrow_txn_id": rid, "amount": amount, "escrow_balance": balance, "status": "deposited"})


@tool(owner="user", rw="write")
def make_principal_paydown_d2fdfc16(ctx: ToolContext, loan_id: str, paydown_amount: float) -> str:
    """Make an extra principal payment (a paydown) on a Country Home loan by a one-time debit the member authorises.

    The member authorises a one-time debit of their own account for the amount given, which is booked
    today as an extra principal payment (curtailment) on the loan. The principal balance falls by that
    amount at once; the monthly payment and the next due date do not change, and the payment shows in
    the payment history as an extra principal payment.

    Args:
        loan_id: Id class — the loan number of the Country Home loan, as the servicing agent reads it out from the loan record.
        paydown_amount: Fixed-format class — the extra principal being paid, in USD, 2 decimal places, always positive, as the agent states it.

    Returns:
        A dictionary receipt: txn_id (reference number of the extra principal payment, a string),
        amount (the paydown, USD to 2 decimal places), principal_balance (the principal after the
        paydown, USD to 2 decimal places) and status ("posted" when the paydown is on the loan).
    """
    loan = _Ledger.loan(ctx, loan_id)
    amount = round(float(paydown_amount), 2)
    rid = ctx.make_id("hlk_", loan_id, amount, "curtailment")
    ctx.create("homeloan_transactions", rid, txn_id=rid, loan_id=loan_id, customer_id=loan.get("customer_id", ""),
               event_type="homeloan_principal_payment", amount=amount, effective_date=ctx.now()[:10], channel="phone",
               payment_purpose="curtailment", fee_code="none", due_date="", rate_applied="", source_ref_id="",
               waiver_basis="none", return_reason="none")
    balance = round(float(loan.get("principal_balance") or 0) - amount, 2)
    ctx.update("homeloan_loans", loan_id, principal_balance=balance)
    return str({"txn_id": rid, "amount": amount, "principal_balance": balance, "status": "posted"})


@tool(owner="agent", rw="write")
def record_escrow_waiver_439c8464(ctx: ToolContext, loan_id: str, waiver_fee: float) -> str:
    """Record the waiver of escrow on a Country Home loan and book its one-time escrow waiver fee.

    The loan is marked as escrow waived, the monthly escrow deposit is set to 0.00 and the escrow
    analysis date is cleared, so the member pays property taxes and homeowner's insurance directly from
    now on; the escrow waiver fee given is booked today as a fee on the loan, its unpaid fees rise by
    that amount, and the member's pending escrow waiver request is marked approved. Any escrow balance
    is refunded separately by the escrow refund run.

    Args:
        loan_id: Id class — the loan number of the Country Home loan, as returned by the home loan lookup.
        waiver_fee: Fixed-format class — the escrow waiver fee in USD, 2 decimal places, always positive; pass the figure already rounded to the cent.

    Returns:
        A dictionary receipt: loan_id (the loan, a string), fee_txn_id (reference number of the fee
        entry, a string), waiver_fee (the fee booked, USD to 2 decimal places), monthly_escrow_amount
        (0.0 once escrow is waived), fees_due (the loan's unpaid fees after the booking, USD to 2
        decimal places), request_id (the escrow waiver request marked approved, a string, empty when
        none was pending) and status ("escrow_waived").
    """
    loan = _Ledger.loan(ctx, loan_id)
    fee = round(float(waiver_fee), 2)
    ctx.update("homeloan_loans", loan_id, escrow_waived=True, monthly_escrow_amount=0.0, last_escrow_analysis_date="")
    rid = ctx.make_id("hlw_", loan_id, fee, "escrow_waiver")
    ctx.create("homeloan_transactions", rid, txn_id=rid, loan_id=loan_id, customer_id=loan.get("customer_id", ""),
               event_type="homeloan_fee_assessed", amount=fee, effective_date=ctx.now()[:10], channel="system",
               payment_purpose="none", fee_code="escrow_waiver", due_date="", rate_applied="", source_ref_id="",
               waiver_basis="none", return_reason="none")
    fees = round(float(loan.get("fees_due") or 0) + fee, 2)
    ctx.update("homeloan_loans", loan_id, fees_due=fees)
    pending = [r for r in ctx.find("homeloan_requests", loan_id=loan_id, request_type="escrow_waiver")
               if r.get("request_status") == "submitted"]
    request_id = pending[0]["request_id"] if pending else ""
    if request_id:
        ctx.update("homeloan_requests", request_id, request_status="approved")
    return str({"loan_id": loan_id, "fee_txn_id": rid, "waiver_fee": fee, "monthly_escrow_amount": 0.0,
                "fees_due": fees, "request_id": request_id, "status": "escrow_waived"})

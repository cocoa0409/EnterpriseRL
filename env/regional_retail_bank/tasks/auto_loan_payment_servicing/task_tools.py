"""Hidden task tools for regional_retail_bank / auto_loan_payment_servicing.

Each tool performs exactly one atomic auto-loan write with the arguments it is given. None of
them aggregates history, computes a policy amount, or checks a business precondition; every
value and every eligibility judgement comes from the agent reading the published policy and
the records. They are reached only through unlock_*_discoverable_tool -> call_*_discoverable_tool.
"""

from erlbench import ToolContext, tool


@tool(owner="agent", rw="write")
def post_installment_payment_660c6229(ctx: ToolContext, auto_loan_id: str, installment_due_date: str,
                                      amount: float, fees_portion: float, interest_portion: float,
                                      principal_portion: float, counterparty_account_id: str,
                                      next_payment_due_date: str, days_past_due: int) -> str:
    """Post one scheduled auto loan payment that the borrower pays by transfer from their own PCB checking
    account, credited today toward one installment of the loan.

    One call books the payment on the loan's activity as a scheduled payment made by PCB transfer, with
    the total split into the fees, interest and principal parts you give; when the fees part is above
    zero it also books the matching fee settlement entry. On the loan itself it lowers the unpaid
    principal by the principal part and the unpaid fees by the fees part, records today as the last
    payment date, and records the next installment due date and the days past due you give. The
    borrower sees the payment, its split and the updated balances on the loan afterwards. The call has
    succeeded when the receipt shows status "posted" with the new payment's reference number.

    Args:
        auto_loan_id: Id class — the auto loan reference number of the loan being paid, taken from the
            auto loan lookup for this borrower.
        installment_due_date: Fixed-format class — the due date of the installment this payment is
            credited toward, written YYYY-MM-DD (for example 2031-02-15); never empty for this payment.
        amount: Fixed-format class — the total payment drawn from the checking account, in USD, rounded
            to 2 decimal places, as a positive number of dollars (unit: USD).
        fees_portion: Fixed-format class — the part of the payment applied to fees due, in USD, rounded
            to 2 decimal places, 0.00 when no fees are paid (unit: USD).
        interest_portion: Fixed-format class — the part of the payment applied to accrued interest, in
            USD, rounded to 2 decimal places (unit: USD).
        principal_portion: Fixed-format class — the part of the payment applied to principal, in USD,
            rounded to 2 decimal places (unit: USD).
        counterparty_account_id: Id class — the checking account reference number of the borrower's PCB
            checking account the money is drawn from, taken from the checking account lookup.
        next_payment_due_date: Fixed-format class — the due date of the earliest installment that will
            still be unsatisfied once this payment posts, written YYYY-MM-DD (for example 2031-03-15).
        days_past_due: Fixed-format class — the loan's days past due once this payment posts, a
            non-negative integer count in units of calendar days (0 when no installment is past due).

    Returns:
        A dictionary rendered as text with: status ("posted" on success), payment_reference (the
        12-digit payment reference number), auto_txn_id (reference number of the new payment entry),
        fee_settlement_id (reference number of the fee settlement entry, or "" when the fees part is
        0.00), principal_balance (unpaid principal afterwards, USD with 2 decimal places), fees_due
        (unpaid fees afterwards, USD with 2 decimal places), next_payment_due_date (YYYY-MM-DD) and
        days_past_due (integer).
    """
    rows = ctx.find("auto_loans", auto_loan_id=auto_loan_id)
    loan = rows[0] if rows else {}
    today = ctx.now()[:10]
    rid = ctx.make_id("apy_", auto_loan_id, installment_due_date, amount, fees_portion, interest_portion,
                      principal_portion, counterparty_account_id, next_payment_due_date, days_past_due)
    ref = str(int(rid.split("_", 1)[1], 16) % 10**12).zfill(12)  # 12-digit reference from the row id
    ctx.create("auto_transactions", rid, auto_txn_id=rid, auto_loan_id=auto_loan_id,
               customer_id=loan.get("customer_id", ""), event_type="auto_payment",
               amount=round(float(amount), 2), posted_date=today, payment_channel="pcb_transfer",
               payment_type="scheduled", fees_portion=round(float(fees_portion), 2),
               interest_portion=round(float(interest_portion), 2),
               principal_portion=round(float(principal_portion), 2),
               installment_due_date=installment_due_date, reference_number=ref,
               counterparty_account_id=counterparty_account_id, fee_code="none", source_item_id="",
               adjustment_reason="none", refund_destination="none")
    settlement_id = ""
    if round(float(fees_portion), 2) > 0:
        settlement_id = ctx.make_id("afs_", rid)
        ctx.create("auto_transactions", settlement_id, auto_txn_id=settlement_id, auto_loan_id=auto_loan_id,
                   customer_id=loan.get("customer_id", ""), event_type="auto_fee_settlement",
                   amount=round(float(fees_portion), 2), posted_date=today, payment_channel="none",
                   payment_type="none", fees_portion=0.0, interest_portion=0.0, principal_portion=0.0,
                   installment_due_date="", reference_number="", counterparty_account_id="",
                   fee_code="none", source_item_id=rid, adjustment_reason="none", refund_destination="none")
    principal_balance = round(float(loan.get("principal_balance") or 0) - round(float(principal_portion), 2), 2)
    fees_due = round(float(loan.get("fees_due") or 0) - round(float(fees_portion), 2), 2)
    ctx.update("auto_loans", auto_loan_id, principal_balance=principal_balance, fees_due=fees_due,
               last_payment_date=today, next_payment_due_date=next_payment_due_date,
               days_past_due=int(days_past_due))
    return str({"status": "posted", "payment_reference": ref, "auto_txn_id": rid,
                "fee_settlement_id": settlement_id, "principal_balance": principal_balance,
                "fees_due": fees_due, "next_payment_due_date": next_payment_due_date,
                "days_past_due": int(days_past_due)})


@tool(owner="agent", rw="write")
def change_due_day_df9bec35(ctx: ToolContext, auto_loan_id: str, new_due_day: int,
                            next_payment_due_date: str) -> str:
    """Move the monthly due day of one auto loan to the day the borrower chose, as a PCB service action.

    One call records the new day of the month on which installments fall due, records the next
    installment due date on that new day, and records today as the date of the latest due date change.
    The maturity date and the balances are not touched and no fee is booked. The borrower sees the new
    due day and next due date on the loan afterwards. The call has succeeded when the receipt shows
    status "due_day_changed".

    Args:
        auto_loan_id: Id class — the auto loan reference number of the loan whose due day moves, taken
            from the auto loan lookup for this borrower.
        new_due_day: Fixed-format class — the new day of the month for installments, an integer 1-28
            in units of calendar day of the month.
        next_payment_due_date: Fixed-format class — the next installment due date on the new due day,
            written YYYY-MM-DD (for example 2031-03-28).

    Returns:
        A dictionary rendered as text with: status ("due_day_changed" on success), auto_loan_id (the
        loan reference number), payment_due_day (integer 1-28), next_payment_due_date (YYYY-MM-DD) and
        last_due_date_change_date (today's date, YYYY-MM-DD).
    """
    today = ctx.now()[:10]
    ctx.update("auto_loans", auto_loan_id, payment_due_day=int(new_due_day),
               next_payment_due_date=next_payment_due_date, last_due_date_change_date=today)
    return str({"status": "due_day_changed", "auto_loan_id": auto_loan_id,
                "payment_due_day": int(new_due_day), "next_payment_due_date": next_payment_due_date,
                "last_due_date_change_date": today})


@tool(owner="user", rw="write")
def cancel_autopay_a2c51ad3(ctx: ToolContext, auto_loan_id: str, autopay_source_account_id: str,
                            interest_rate: float, rate_discounts: str) -> str:
    """Cancel, on the borrower's own instruction, the automatic payment enrollment standing on one of their
    auto loans, and record the APR that applies once the autopay discount leaves the rate.

    One call ends the standing enrollment: the loan is marked as not enrolled, its paying checking
    account is cleared, the APR and the list of discounts included in it are recorded as given, and a
    completed autopay change request is registered on the loan as the record of the borrower's
    instruction. No payment is moved. The borrower sees autopay as off and the new APR on the loan afterwards. The call
    has succeeded when the receipt shows status "autopay_cancelled".

    Args:
        auto_loan_id: Id class — the auto loan reference number of the loan whose enrollment ends, taken
            from the auto loan lookup for this borrower.
        autopay_source_account_id: Id class — the checking account reference number of the account the
            cancelled enrollment was drawing on, as shown as the autopay paying account in the auto loan
            lookup.
        interest_rate: Fixed-format class — the APR after cancellation, a percent rounded to 2 decimal
            places (for example 7.24 means 7.24 percent).
        rate_discounts: Enum class — the discounts still included in the APR after cancellation, one of
            none (no discount remains in the APR), autopay (only the autopay discount remains in the APR),
            relationship (only the checking relationship discount remains in the APR),
            autopay_and_relationship (both the autopay and the relationship discount remain in the APR).

    Returns:
        A dictionary rendered as text with: status ("autopay_cancelled" on success), request_id (reference
        number of the completed autopay change request), auto_loan_id (the
        loan reference number), cancelled_source_account_id (the checking account the enrollment drew
        on), autopay_enrolled (false), interest_rate (percent, 2 decimal places) and rate_discounts
        (the enum value recorded).
    """
    rows = ctx.find("auto_loans", auto_loan_id=auto_loan_id)
    loan = rows[0] if rows else {}
    request_id = ctx.make_id("aqc_", auto_loan_id, autopay_source_account_id, interest_rate, rate_discounts)
    ctx.create("auto_requests", request_id, auto_request_id=request_id, customer_id=loan.get("customer_id", ""),
               auto_loan_id=auto_loan_id, request_type="autopay_change", requested_due_day="",
               extension_installments="", payoff_date="", request_status="completed", created_at=ctx.now())
    ctx.update("auto_loans", auto_loan_id, autopay_enrolled=False, autopay_source_account_id="",
               interest_rate=round(float(interest_rate), 2), rate_discounts=rate_discounts)
    return str({"status": "autopay_cancelled", "request_id": request_id, "auto_loan_id": auto_loan_id,
                "cancelled_source_account_id": autopay_source_account_id, "autopay_enrolled": False,
                "interest_rate": round(float(interest_rate), 2), "rate_discounts": rate_discounts})


@tool(owner="user", rw="write")
def enroll_autopay_b9bffdb4(ctx: ToolContext, auto_loan_id: str, autopay_source_account_id: str,
                            interest_rate: float, rate_discounts: str) -> str:
    """Enroll, on the borrower's own instruction, one of their auto loans in automatic monthly payment from a
    PCB checking account they name, and record the APR that applies with the enrollment.

    One call marks the loan as enrolled, records the checking account that each installment will be
    drawn from, records the APR and the list of discounts included in it as given, and registers a
    completed autopay change request on the loan as the record of the borrower's instruction. No
    payment is moved now. The borrower sees autopay as on, the paying account and the new APR on the loan
    afterwards. The call has succeeded when the receipt shows status "autopay_enrolled".

    Args:
        auto_loan_id: Id class — the auto loan reference number of the loan being enrolled, taken from the
            auto loan lookup for this borrower.
        autopay_source_account_id: Id class — the checking account reference number of the PCB checking
            account installments will be drawn from, taken from the checking account lookup.
        interest_rate: Fixed-format class — the APR with the enrollment, a percent rounded to 2 decimal
            places (for example 6.99 means 6.99 percent).
        rate_discounts: Enum class — the discounts included in the APR with the enrollment, one of none
            (no discount is included in the APR), autopay (only the autopay discount is included in the
            APR), relationship (only the checking relationship discount is included in the APR),
            autopay_and_relationship (both the autopay and the relationship discount are included in the
            APR).

    Returns:
        A dictionary rendered as text with: status ("autopay_enrolled" on success), request_id (reference
        number of the completed autopay change request), auto_loan_id (the loan
        reference number), autopay_source_account_id (the paying checking account), autopay_enrolled
        (true), interest_rate (percent, 2 decimal places) and rate_discounts (the enum value recorded).
    """
    rows = ctx.find("auto_loans", auto_loan_id=auto_loan_id)
    loan = rows[0] if rows else {}
    request_id = ctx.make_id("aqe_", auto_loan_id, autopay_source_account_id, interest_rate, rate_discounts)
    ctx.create("auto_requests", request_id, auto_request_id=request_id, customer_id=loan.get("customer_id", ""),
               auto_loan_id=auto_loan_id, request_type="autopay_change", requested_due_day="",
               extension_installments="", payoff_date="", request_status="completed", created_at=ctx.now())
    ctx.update("auto_loans", auto_loan_id, autopay_enrolled=True,
               autopay_source_account_id=autopay_source_account_id,
               interest_rate=round(float(interest_rate), 2), rate_discounts=rate_discounts)
    return str({"status": "autopay_enrolled", "request_id": request_id, "auto_loan_id": auto_loan_id,
                "autopay_source_account_id": autopay_source_account_id, "autopay_enrolled": True,
                "interest_rate": round(float(interest_rate), 2), "rate_discounts": rate_discounts})


@tool(owner="agent", rw="write")
def waive_returned_payment_fee_ab31cb83(ctx: ToolContext, customer_id: str, auto_loan_id: str,
                                        source_item_id: str, amount: float, applied_to_principal: float) -> str:
    """Waive in full, as a PCB bank-error correction, one returned payment fee charged on a borrower's auto loan.

    One call books a fee waiver entry on the loan's activity for the returned payment fee you name, with
    the waiver reason recorded as bank error and the fee code recorded as returned payment. On the loan
    it lowers the unpaid fees by the waived amount less the part you say is applied to principal, and
    lowers the unpaid principal by that applied part (used only when the fee had already been paid).
    The borrower sees the waiver and the reduced balances on the loan afterwards. The call has succeeded
    when the receipt shows status "waived" with the new waiver entry's reference number.

    Args:
        customer_id: Id class — the customer reference number of the borrower, taken from the customer
            profile lookup.
        auto_loan_id: Id class — the auto loan reference number of the loan the fee was charged on, taken
            from the auto loan lookup.
        source_item_id: Id class — the reference number of the returned payment fee entry being waived, as
            listed in the auto loan activity lookup.
        amount: Fixed-format class — the amount waived, equal to the whole fee, in USD rounded to 2
            decimal places (unit: USD).
        applied_to_principal: Fixed-format class — the part of the waived amount that is credited to
            principal because the fee had already been paid, in USD rounded to 2 decimal places, 0.00 when
            the fee was still unpaid (unit: USD).

    Returns:
        A dictionary rendered as text with: status ("waived" on success), waiver_id (reference number of
        the new waiver entry), waived_fee_id (the fee entry waived), amount (USD, 2 decimal places),
        fees_due (unpaid fees afterwards, USD with 2 decimal places) and principal_balance (unpaid
        principal afterwards, USD with 2 decimal places).
    """
    rows = ctx.find("auto_loans", auto_loan_id=auto_loan_id)
    loan = rows[0] if rows else {}
    waived = round(float(amount), 2)
    to_principal = round(float(applied_to_principal), 2)
    rid = ctx.make_id("awr_", customer_id, auto_loan_id, source_item_id, waived, to_principal)
    ctx.create("auto_transactions", rid, auto_txn_id=rid, auto_loan_id=auto_loan_id, customer_id=customer_id,
               event_type="auto_fee_waiver", amount=waived, posted_date=ctx.now()[:10], payment_channel="none",
               payment_type="none", fees_portion=0.0, interest_portion=0.0, principal_portion=0.0,
               installment_due_date="", reference_number="", counterparty_account_id="",
               fee_code="returned_payment", source_item_id=source_item_id, adjustment_reason="bank_error",
               refund_destination="none")
    fees_due = round(float(loan.get("fees_due") or 0) - (waived - to_principal), 2)
    principal_balance = round(float(loan.get("principal_balance") or 0) - to_principal, 2)
    ctx.update("auto_loans", auto_loan_id, fees_due=fees_due, principal_balance=principal_balance)
    return str({"status": "waived", "waiver_id": rid, "waived_fee_id": source_item_id, "amount": waived,
                "fees_due": fees_due, "principal_balance": principal_balance})


@tool(owner="agent", rw="write")
def waive_late_charge_e8055e73(ctx: ToolContext, customer_id: str, auto_loan_id: str,
                               source_item_id: str, amount: float, applied_to_principal: float) -> str:
    """Waive in full, as a PCB bank-error correction, one late charge assessed on an installment of a borrower's
    auto loan.

    One call books a fee waiver entry on the loan's activity for the late charge you name, with the
    waiver reason recorded as bank error and the fee code recorded as late charge. On the loan it lowers
    the unpaid fees by the waived amount less the part you say is applied to principal, and lowers the
    unpaid principal by that applied part (used only when the late charge had already been paid). The
    borrower sees the waiver and the reduced balances on the loan afterwards. The call has succeeded when
    the receipt shows status "waived" with the new waiver entry's reference number.

    Args:
        customer_id: Id class — the customer reference number of the borrower, taken from the customer
            profile lookup.
        auto_loan_id: Id class — the auto loan reference number of the loan the late charge was assessed
            on, taken from the auto loan lookup.
        source_item_id: Id class — the reference number of the late charge entry being waived, as listed
            in the auto loan activity lookup.
        amount: Fixed-format class — the amount waived, equal to the whole late charge, in USD rounded to
            2 decimal places (unit: USD).
        applied_to_principal: Fixed-format class — the part of the waived amount that is credited to
            principal because the late charge had already been paid, in USD rounded to 2 decimal places,
            0.00 when it was still unpaid (unit: USD).

    Returns:
        A dictionary rendered as text with: status ("waived" on success), waiver_id (reference number of
        the new waiver entry), waived_fee_id (the late charge entry waived), amount (USD, 2 decimal
        places), fees_due (unpaid fees afterwards, USD with 2 decimal places) and principal_balance
        (unpaid principal afterwards, USD with 2 decimal places).
    """
    rows = ctx.find("auto_loans", auto_loan_id=auto_loan_id)
    loan = rows[0] if rows else {}
    waived = round(float(amount), 2)
    to_principal = round(float(applied_to_principal), 2)
    rid = ctx.make_id("awl_", customer_id, auto_loan_id, source_item_id, waived, to_principal)
    ctx.create("auto_transactions", rid, auto_txn_id=rid, auto_loan_id=auto_loan_id, customer_id=customer_id,
               event_type="auto_fee_waiver", amount=waived, posted_date=ctx.now()[:10], payment_channel="none",
               payment_type="none", fees_portion=0.0, interest_portion=0.0, principal_portion=0.0,
               installment_due_date="", reference_number="", counterparty_account_id="",
               fee_code="late_charge", source_item_id=source_item_id, adjustment_reason="bank_error",
               refund_destination="none")
    fees_due = round(float(loan.get("fees_due") or 0) - (waived - to_principal), 2)
    principal_balance = round(float(loan.get("principal_balance") or 0) - to_principal, 2)
    ctx.update("auto_loans", auto_loan_id, fees_due=fees_due, principal_balance=principal_balance)
    return str({"status": "waived", "waiver_id": rid, "waived_fee_id": source_item_id, "amount": waived,
                "fees_due": fees_due, "principal_balance": principal_balance})


@tool(owner="agent", rw="write")
def post_payoff_payment_63569e96(ctx: ToolContext, auto_loan_id: str, amount: float, fees_portion: float,
                                 interest_portion: float, principal_portion: float,
                                 counterparty_account_id: str) -> str:
    """Post a payoff payment that the borrower pays today by transfer from their own PCB checking account,
    closing the auto loan.

    One call books the payment on the loan's activity as a payoff made by PCB transfer, split into the
    fees, interest and principal parts you give, and books the matching fee settlement entry when the
    fees part is above zero. On the loan it sets the unpaid principal and fees to 0.00, records today
    as the last payment date and as the closing date, marks the loan paid off with no installment due
    and no days past due, and marks the lien release as pending. The borrower sees the loan as paid off
    afterwards. The call has succeeded when the receipt shows status "paid_off" with the payment's
    reference number.

    Args:
        auto_loan_id: Id class — the auto loan reference number of the loan being paid off, taken from the
            auto loan lookup.
        amount: Fixed-format class — the total payoff payment drawn from the checking account, in USD
            rounded to 2 decimal places (unit: USD).
        fees_portion: Fixed-format class — the part of the payment applied to fees due, in USD rounded to 2
            decimal places, 0.00 when no fees are due (unit: USD).
        interest_portion: Fixed-format class — the part of the payment applied to accrued interest, in USD
            rounded to 2 decimal places (unit: USD).
        principal_portion: Fixed-format class — the part of the payment applied to principal, in USD
            rounded to 2 decimal places (unit: USD).
        counterparty_account_id: Id class — the checking account reference number of the borrower's PCB
            checking account the money is drawn from, taken from the checking account lookup.

    Returns:
        A dictionary rendered as text with: status ("paid_off" on success), payment_reference (the 12-digit
        payment reference number), auto_txn_id (reference number of the payoff entry), fee_settlement_id
        (reference number of the fee settlement entry, or "" when the fees part is 0.00), closed_date
        (today, YYYY-MM-DD) and lien_status ("release_pending").
    """
    rows = ctx.find("auto_loans", auto_loan_id=auto_loan_id)
    loan = rows[0] if rows else {}
    today = ctx.now()[:10]
    rid = ctx.make_id("apo_", auto_loan_id, amount, fees_portion, interest_portion, principal_portion,
                      counterparty_account_id)
    ref = str(int(rid.split("_", 1)[1], 16) % 10**12).zfill(12)  # 12-digit reference from the row id
    ctx.create("auto_transactions", rid, auto_txn_id=rid, auto_loan_id=auto_loan_id,
               customer_id=loan.get("customer_id", ""), event_type="auto_payment",
               amount=round(float(amount), 2), posted_date=today, payment_channel="pcb_transfer",
               payment_type="payoff", fees_portion=round(float(fees_portion), 2),
               interest_portion=round(float(interest_portion), 2),
               principal_portion=round(float(principal_portion), 2), installment_due_date="",
               reference_number=ref, counterparty_account_id=counterparty_account_id, fee_code="none",
               source_item_id="", adjustment_reason="none", refund_destination="none")
    settlement_id = ""
    if round(float(fees_portion), 2) > 0:
        settlement_id = ctx.make_id("afs_", rid)
        ctx.create("auto_transactions", settlement_id, auto_txn_id=settlement_id, auto_loan_id=auto_loan_id,
                   customer_id=loan.get("customer_id", ""), event_type="auto_fee_settlement",
                   amount=round(float(fees_portion), 2), posted_date=today, payment_channel="none",
                   payment_type="none", fees_portion=0.0, interest_portion=0.0, principal_portion=0.0,
                   installment_due_date="", reference_number="", counterparty_account_id="",
                   fee_code="none", source_item_id=rid, adjustment_reason="none", refund_destination="none")
    ctx.update("auto_loans", auto_loan_id, principal_balance=0.0, fees_due=0.0, last_payment_date=today,
               status="paid_off", closed_date=today, next_payment_due_date="", days_past_due=0,
               lien_status="release_pending")
    return str({"status": "paid_off", "payment_reference": ref, "auto_txn_id": rid,
                "fee_settlement_id": settlement_id, "closed_date": today, "lien_status": "release_pending"})

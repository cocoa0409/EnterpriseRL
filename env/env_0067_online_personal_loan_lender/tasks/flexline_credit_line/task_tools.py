"""Hidden task tools for the flexline_credit_line difficulty of env_0067_online_personal_loan_lender.

Each tool performs one atomic write on a FlexLine personal line of credit and is reached only through
the unlock/call meta-tools by the name an extended policy gives as its target tool.
"""

from erlbench import ToolContext, tool


@tool(owner="user", rw="write")
def close_line_to_draws_7539d675(ctx: ToolContext, credit_line_id: str, repayment_payment: float) -> str:
    """The borrower closes their own FlexLine to new draws while a balance is still owed.

    The line identified by the borrower's FlexLine reference stops taking draws today: its status becomes
    repayment, the last day draws were allowed becomes today's date, and the monthly payment the borrower
    owes from now on is recorded as the line's minimum payment due. The balance itself is not changed. The
    borrower sees the line shown as in repayment with the new monthly payment.

    Args:
        credit_line_id: Id class — reference number of the borrower's FlexLine line of credit, read from the
            FlexLine account lookup for this borrower.
        repayment_payment: Fixed-format class — the monthly payment the borrower will owe while the balance is
            repaid, in USD as a decimal number with 2 decimal places (cents), already rounded to the cent;
            no currency sign and no thousands separator.

    Returns:
        str: a text rendering of a dictionary with credit_line_id (the FlexLine reference), status (the new
        status, repayment), draw_period_end_date (today's date as YYYY-MM-DD, the last day draws were allowed)
        and minimum_payment_due (the recorded monthly payment, USD with 2 decimal places). A status of
        repayment confirms the line is closed to new draws.
    """
    payment = round(float(repayment_payment), 2)
    today = ctx.now()[:10]
    ctx.update("credit_lines", credit_line_id, status="repayment", draw_period_end_date=today,
               minimum_payment_due=payment)
    return str({"credit_line_id": credit_line_id, "status": "repayment",
                "draw_period_end_date": today, "minimum_payment_due": payment})


@tool(owner="agent", rw="write")
def assess_returned_payment_fee_0fd8e99d(ctx: ToolContext, credit_line_id: str, related_txn_id: str,
                                         fee_amount: float) -> str:
    """Charge the returned-payment fee for one returned payment on a FlexLine.

    One returned-payment fee entry is booked on the line, dated today and tied to the returned-payment entry
    it is charged for, and the fee is added to the line's outstanding balance. The borrower sees the new fee
    line on the account and the higher balance.

    Args:
        credit_line_id: Id class — reference number of the FlexLine the fee is charged on, read from the
            FlexLine account lookup.
        related_txn_id: Id class — reference number of the returned-payment entry the fee is charged for,
            read from the FlexLine entry lookup for that line.
        fee_amount: Fixed-format class — the fee charged, in USD as a decimal number with 2 decimal places
            (cents), already rounded to the cent; no currency sign.

    Returns:
        str: a text rendering of a dictionary with line_txn_id (reference number of the new fee entry),
        related_txn_id (the returned-payment entry it is tied to), amount (the fee, USD with 2 decimal places)
        and outstanding_balance (the line's balance including the fee, USD with 2 decimal places). The new
        line_txn_id confirms the fee was booked.
    """
    fee = round(float(fee_amount), 2)
    line = ctx.find("credit_lines", credit_line_id=credit_line_id)[0]
    rid = ctx.make_id("lrf_", credit_line_id, related_txn_id, fee)
    ctx.create("line_transactions", rid, line_txn_id=rid, credit_line_id=credit_line_id,
               customer_id=line.get("customer_id"), event_type="line_returned_payment_fee_assessed",
               txn_date=ctx.now()[:10], amount=fee, related_txn_id=related_txn_id)
    balance = round(float(line.get("outstanding_balance") or 0) + fee, 2)
    ctx.update("credit_lines", credit_line_id, outstanding_balance=balance)
    return str({"line_txn_id": rid, "related_txn_id": related_txn_id, "amount": fee,
                "outstanding_balance": balance})


@tool(owner="agent", rw="write")
def assess_draw_fee_4f046c6c(ctx: ToolContext, credit_line_id: str, related_txn_id: str, fee_amount: float) -> str:
    """Charge the draw fee for one draw on a FlexLine that carries no draw fee entry.

    One draw-fee entry is booked on the line, dated today and tied to the draw it is charged for, and the
    fee is added to the line's outstanding balance. The borrower sees the draw-fee line on the account and
    the higher balance.

    Args:
        credit_line_id: Id class — reference number of the FlexLine the draw fee is charged on, read from the
            FlexLine account lookup.
        related_txn_id: Id class — reference number of the draw entry the fee is charged for, read from the
            FlexLine entry lookup for that line.
        fee_amount: Fixed-format class — the draw fee charged, in USD as a decimal number with 2 decimal places
            (cents), already rounded to the cent; no currency sign.

    Returns:
        str: a text rendering of a dictionary with line_txn_id (reference number of the new draw-fee entry),
        related_txn_id (the draw it is tied to), amount (the draw fee, USD with 2 decimal places) and
        outstanding_balance (the line's balance including the fee, USD with 2 decimal places). The new
        line_txn_id confirms the draw fee was booked.
    """
    fee = round(float(fee_amount), 2)
    line = ctx.find("credit_lines", credit_line_id=credit_line_id)[0]
    rid = ctx.make_id("ldf_", credit_line_id, related_txn_id, fee)
    ctx.create("line_transactions", rid, line_txn_id=rid, credit_line_id=credit_line_id,
               customer_id=line.get("customer_id"), event_type="line_draw_fee_assessed",
               txn_date=ctx.now()[:10], amount=fee, related_txn_id=related_txn_id)
    balance = round(float(line.get("outstanding_balance") or 0) + fee, 2)
    ctx.update("credit_lines", credit_line_id, outstanding_balance=balance)
    return str({"line_txn_id": rid, "related_txn_id": related_txn_id, "amount": fee,
                "outstanding_balance": balance})


@tool(owner="agent", rw="write")
def assess_late_fee_ba469c06(ctx: ToolContext, credit_line_id: str, installment_due_date: str,
                             fee_amount: float) -> str:
    """Charge the late fee for one missed due date on a FlexLine.

    One late-fee entry is booked on the line, dated today and naming the due date it is charged for, and
    the fee is added to the line's outstanding balance. The borrower sees the late fee on the account and
    the higher balance.

    Args:
        credit_line_id: Id class — reference number of the FlexLine the fee is charged on, read from the
            FlexLine account lookup.
        installment_due_date: Fixed-format class — the payment due date the fee is charged for, as a calendar
            date in the format YYYY-MM-DD.
        fee_amount: Fixed-format class — the late fee charged, in USD as a decimal number with 2 decimal places
            (cents), already rounded to the cent; no currency sign.

    Returns:
        str: a text rendering of a dictionary with line_txn_id (reference number of the new late-fee entry),
        installment_due_date (YYYY-MM-DD), amount (the fee, USD with 2 decimal places) and outstanding_balance
        (the line's balance including the fee, USD with 2 decimal places). The new line_txn_id confirms the fee
        was booked.
    """
    fee = round(float(fee_amount), 2)
    line = ctx.find("credit_lines", credit_line_id=credit_line_id)[0]
    rid = ctx.make_id("llf_", credit_line_id, installment_due_date, fee)
    ctx.create("line_transactions", rid, line_txn_id=rid, credit_line_id=credit_line_id,
               customer_id=line.get("customer_id"), event_type="line_late_fee_assessed", txn_date=ctx.now()[:10],
               amount=fee, installment_due_date=installment_due_date)
    balance = round(float(line.get("outstanding_balance") or 0) + fee, 2)
    ctx.update("credit_lines", credit_line_id, outstanding_balance=balance)
    return str({"line_txn_id": rid, "installment_due_date": installment_due_date, "amount": fee,
                "outstanding_balance": balance})


@tool(owner="agent", rw="write")
def apply_limit_review_5d0a2d8e(ctx: ToolContext, credit_line_id: str, reviewed_limit: float) -> str:
    """Apply the outcome of Larkspur's credit-limit review to a FlexLine.

    The review is recorded on the line as a credit-limit decrease decided today, showing the limit before the
    review and the reviewed limit, and the line's credit limit is set to the reviewed limit at once. The
    borrower sees the new credit limit and the recorded review decision.

    Args:
        credit_line_id: Id class — reference number of the FlexLine under review, read from the FlexLine account
            lookup.
        reviewed_limit: Fixed-format class — the credit limit after the review, in USD as a decimal number with 2
            decimal places (cents); no currency sign and no thousands separator.

    Returns:
        str: a text rendering of a dictionary with limit_request_id (reference number of the recorded review
        decision), previous_limit (the credit limit before the review, USD with 2 decimal places), credit_limit
        (the reviewed limit now in force, USD with 2 decimal places) and decision_status (approved). The new
        limit_request_id confirms the review was applied.
    """
    new_limit = round(float(reviewed_limit), 2)
    line = ctx.find("credit_lines", credit_line_id=credit_line_id)[0]
    previous = round(float(line.get("credit_limit") or 0), 2)
    today = ctx.now()[:10]
    rid = ctx.make_id("lrv_", credit_line_id, new_limit)
    ctx.create("line_limit_requests", rid, limit_request_id=rid, customer_id=line.get("customer_id"),
               credit_line_id=credit_line_id, request_date=today, request_type="decrease", current_limit=previous,
               requested_limit=new_limit, decision_status="approved", approved_limit=new_limit,
               decision_date=today, created_at=ctx.now())
    ctx.update("credit_lines", credit_line_id, credit_limit=new_limit)
    return str({"limit_request_id": rid, "previous_limit": previous, "credit_limit": new_limit,
                "decision_status": "approved"})


@tool(owner="agent", rw="write")
def grant_workout_fee_relief_903cc630(ctx: ToolContext, credit_line_id: str, related_txn_id: str,
                                      relief_amount: float) -> str:
    """Grant workout relief on one late fee of a FlexLine.

    One fee-waiver entry with the basis courtesy is booked on the line, dated today and tied to the late fee it
    relieves, and the relief is taken off the line's outstanding balance. The borrower sees the relief on the account and the lower balance.

    Args:
        credit_line_id: Id class — reference number of the FlexLine, read from the FlexLine account lookup.
        related_txn_id: Id class — reference number of the late-fee entry the relief is booked against, read
            from the FlexLine entry lookup for that line.
        relief_amount: Fixed-format class — the relief granted, in USD as a decimal number with 2 decimal places
            (cents), already rounded to the cent; no currency sign.

    Returns:
        str: a text rendering of a dictionary with line_txn_id (reference number of the new waiver entry),
        related_txn_id (the fee it is booked against), amount (the relief, USD with 2 decimal places),
        waiver_reason (courtesy) and outstanding_balance (the balance after the relief, USD with 2 decimal
        places). The new line_txn_id confirms the relief was booked.
    """
    relief = round(float(relief_amount), 2)
    line = ctx.find("credit_lines", credit_line_id=credit_line_id)[0]
    rid = ctx.make_id("lwo_", credit_line_id, related_txn_id, relief)
    ctx.create("line_transactions", rid, line_txn_id=rid, credit_line_id=credit_line_id,
               customer_id=line.get("customer_id"), event_type="line_fee_waived", txn_date=ctx.now()[:10],
               amount=relief, related_txn_id=related_txn_id, waiver_reason="courtesy")
    balance = round(float(line.get("outstanding_balance") or 0) - relief, 2)
    ctx.update("credit_lines", credit_line_id, outstanding_balance=balance)
    return str({"line_txn_id": rid, "related_txn_id": related_txn_id, "amount": relief,
                "waiver_reason": "courtesy", "outstanding_balance": balance})


@tool(owner="user", rw="write")
def authorize_limit_increase_21546d5b(ctx: ToolContext, credit_line_id: str, limit_request_id: str,
                                      approved_limit: float) -> str:
    """Authorize the hard credit inquiry for a FlexLine credit-limit increase request and record its decision.

    The borrower authorizes the hard inquiry in person; the increase request awaiting decision is recorded as
    approved today with the approved limit, and the line's credit limit is set to the approved limit at once.
    The borrower sees the new credit limit and the recorded decision.

    Args:
        credit_line_id: Id class — reference number of the FlexLine, read from the FlexLine account lookup.
        limit_request_id: Id class — reference number of the increase request awaiting decision, read from the
            FlexLine limit-request lookup for that line.
        approved_limit: Fixed-format class — the credit limit approved, in USD as a decimal number with 2 decimal
            places (cents); no currency sign and no thousands separator.

    Returns:
        str: a text rendering of a dictionary with limit_request_id (the request decided), previous_limit (the
        credit limit before the decision, USD with 2 decimal places), credit_limit (the approved limit now in
        force, USD with 2 decimal places) and decision_status (approved). The decision_status confirms the
        request was decided.
    """
    new_limit = round(float(approved_limit), 2)
    line = ctx.find("credit_lines", credit_line_id=credit_line_id)[0]
    previous = round(float(line.get("credit_limit") or 0), 2)
    ctx.update("line_limit_requests", limit_request_id, decision_status="approved", approved_limit=new_limit,
               decision_date=ctx.now()[:10])
    ctx.update("credit_lines", credit_line_id, credit_limit=new_limit)
    return str({"limit_request_id": limit_request_id, "previous_limit": previous, "credit_limit": new_limit,
                "decision_status": "approved"})


@tool(owner="agent", rw="write")
def grant_returned_fee_relief_6fbb0f32(ctx: ToolContext, credit_line_id: str, related_txn_id: str,
                                       relief_amount: float) -> str:
    """Grant replacement relief on the returned-payment fee of a FlexLine.

    One fee-waiver entry with the basis courtesy is booked on the line, dated today and tied to the
    returned-payment fee it relieves, and the relief is taken off the line's outstanding balance. The borrower
    sees the relief on the account and the lower balance.

    Args:
        credit_line_id: Id class — reference number of the FlexLine, read from the FlexLine account lookup.
        related_txn_id: Id class — reference number of the returned-payment-fee entry the relief is booked
            against, read from the FlexLine entry lookup for that line.
        relief_amount: Fixed-format class — the relief granted, in USD as a decimal number with 2 decimal places
            (cents), already rounded to the cent; no currency sign.

    Returns:
        str: a text rendering of a dictionary with line_txn_id (reference number of the new waiver entry),
        related_txn_id (the fee it is booked against), amount (the relief, USD with 2 decimal places),
        waiver_reason (courtesy) and outstanding_balance (the balance after the relief, USD with 2 decimal
        places). The new line_txn_id confirms the relief was booked.
    """
    relief = round(float(relief_amount), 2)
    line = ctx.find("credit_lines", credit_line_id=credit_line_id)[0]
    rid = ctx.make_id("lrr_", credit_line_id, related_txn_id, relief)
    ctx.create("line_transactions", rid, line_txn_id=rid, credit_line_id=credit_line_id,
               customer_id=line.get("customer_id"), event_type="line_fee_waived", txn_date=ctx.now()[:10],
               amount=relief, related_txn_id=related_txn_id, waiver_reason="courtesy")
    balance = round(float(line.get("outstanding_balance") or 0) - relief, 2)
    ctx.update("credit_lines", credit_line_id, outstanding_balance=balance)
    return str({"line_txn_id": rid, "related_txn_id": related_txn_id, "amount": relief,
                "waiver_reason": "courtesy", "outstanding_balance": balance})

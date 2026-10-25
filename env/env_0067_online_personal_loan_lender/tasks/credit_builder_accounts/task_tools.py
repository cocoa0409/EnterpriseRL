"""Hidden task tools for the credit_builder_accounts difficulty of env_0067_online_personal_loan_lender.

Each tool performs exactly one atomic Credit Builder write with the values it is given. None of them
checks a policy condition, computes an amount, or refuses on business grounds.
"""

from erlbench import ToolContext, tool


@tool(owner="agent", rw="write")
def assess_late_fee_fbf509e1(ctx: ToolContext, builder_account_id: str, installment_due_date: str,
                             late_fee_amount: float) -> str:
    """Charge one late fee to a Credit Builder account for one missed due date.

    The representative books a late-fee entry on the borrower's Credit Builder account, dated today and tied
    to the due date it is charged for, and adds the fee to the account's unpaid fees. The borrower sees the
    new late fee and the higher unpaid-fee balance on the account. Success is a confirmation naming the new
    fee entry, the due date and the amount booked.

    Args:
        builder_account_id: Id class — reference number of the Credit Builder account being charged, as
            returned by the Credit Builder account lookup.
        installment_due_date: Fixed-format class — the payment due date the late fee is charged for, written
            as YYYY-MM-DD (calendar date, no time zone), exactly as it appears on the account record.
        late_fee_amount: Fixed-format class — the late fee to charge in USD, a positive amount with 2 decimal
            places, already rounded to the cent (the tool stores it rounded to 2 decimal places).

    Returns:
        A confirmation string of the form "Late fee <entry reference> of <amount> USD booked on <account
        reference> for due date <YYYY-MM-DD>; unpaid fees now <amount> USD.", where the entry reference is
        the new fee entry's reference number, amounts are USD with 2 decimal places, and the unpaid-fee figure
        is the account's unpaid fees including this fee. Receiving this text means the fee is on the account.
    """
    amount = round(float(late_fee_amount), 2)
    acct = ctx.find("builder_accounts", builder_account_id=builder_account_id)
    row = acct[0] if acct else {}
    rid = ctx.make_id("blf_", builder_account_id, installment_due_date, amount)
    ctx.create("builder_transactions", rid, builder_txn_id=rid, builder_account_id=builder_account_id,
               customer_id=row.get("customer_id"), event_type="builder_late_fee_assessed",
               txn_date=ctx.now()[:10], amount=amount, interest_portion=0.0, principal_portion=0.0,
               installment_due_date=installment_due_date, related_txn_id=None)
    fees = round(float(row.get("fees_balance") or 0) + amount, 2)
    ctx.update("builder_accounts", builder_account_id, fees_balance=fees)
    return (f"Late fee {rid} of {amount:.2f} USD booked on {builder_account_id} for due date "
            f"{installment_due_date}; unpaid fees now {fees:.2f} USD.")


@tool(owner="agent", rw="write")
def assess_returned_payment_fee_1f748b6c(ctx: ToolContext, builder_account_id: str, related_txn_id: str,
                                         returned_payment_fee_amount: float) -> str:
    """Charge one returned-payment fee to a Credit Builder account for one returned payment.

    The representative books a returned-payment fee entry on the borrower's Credit Builder account, dated
    today and linked to the returned-payment entry it is charged for, and adds the fee to the account's
    unpaid fees. The borrower sees the new fee and the higher unpaid-fee balance on the account. Success is a
    confirmation naming the new fee entry, the returned-payment entry and the amount booked.

    Args:
        builder_account_id: Id class — reference number of the Credit Builder account being charged, as
            returned by the Credit Builder account lookup.
        related_txn_id: Id class — reference number of the returned-payment entry the fee is charged for, as
            listed among the account's entries by the Credit Builder entry lookup.
        returned_payment_fee_amount: Fixed-format class — the returned-payment fee to charge in USD, a
            positive amount with 2 decimal places, already rounded to the cent (the tool stores it rounded to
            2 decimal places).

    Returns:
        A confirmation string of the form "Returned-payment fee <entry reference> of <amount> USD booked on
        <account reference> for returned payment <entry reference>; unpaid fees now <amount> USD.", where
        amounts are USD with 2 decimal places and the unpaid-fee figure includes this fee. Receiving this text
        means the fee is on the account.
    """
    amount = round(float(returned_payment_fee_amount), 2)
    acct = ctx.find("builder_accounts", builder_account_id=builder_account_id)
    row = acct[0] if acct else {}
    rid = ctx.make_id("brf_", builder_account_id, related_txn_id, amount)
    ctx.create("builder_transactions", rid, builder_txn_id=rid, builder_account_id=builder_account_id,
               customer_id=row.get("customer_id"), event_type="builder_returned_payment_fee_assessed",
               txn_date=ctx.now()[:10], amount=amount, interest_portion=0.0, principal_portion=0.0,
               related_txn_id=related_txn_id)
    fees = round(float(row.get("fees_balance") or 0) + amount, 2)
    ctx.update("builder_accounts", builder_account_id, fees_balance=fees)
    return (f"Returned-payment fee {rid} of {amount:.2f} USD booked on {builder_account_id} for returned "
            f"payment {related_txn_id}; unpaid fees now {fees:.2f} USD.")


@tool(owner="user", rw="write")
def confirm_early_closure_8372931d(ctx: ToolContext, builder_closure_id: str, builder_account_id: str,
                                   savings_applied_amount: float) -> str:
    """The borrower confirms their own pending early-closure request and closes their Credit Builder account.

    Confirming marks the early-closure request as confirmed, closes the Credit Builder account early today
    (status closed early, closing date today, closing reason borrower early close), and books the savings
    applied to the loan: the confirmed amount is taken out of the locked savings certificate as one
    savings-applied entry dated today. The borrower sees the account closed and the savings balance reduced by
    the amount applied. Success is a confirmation naming the closed account, the savings-applied entry and the
    amount applied.

    Args:
        builder_closure_id: Id class — reference number of the borrower's pending early-closure request, as
            returned by the early-closure request lookup.
        builder_account_id: Id class — reference number of the Credit Builder account being closed, as
            returned by the Credit Builder account lookup.
        savings_applied_amount: Fixed-format class — the amount of savings applied to the loan at closing in
            USD, an amount of 0.00 or more with 2 decimal places, already rounded to the cent (the tool stores
            it rounded to 2 decimal places).

    Returns:
        A confirmation string of the form "Early closure confirmed: account <account reference> closed on
        <YYYY-MM-DD>; savings applied entry <entry reference> of <amount> USD; savings balance now <amount>
        USD.", where amounts are USD with 2 decimal places and the savings balance is what remains on the
        certificate. Receiving this text means the account is closed early and the savings were applied.
    """
    amount = round(float(savings_applied_amount), 2)
    acct = ctx.find("builder_accounts", builder_account_id=builder_account_id)
    row = acct[0] if acct else {}
    today = ctx.now()[:10]
    ctx.update("builder_closure_requests", builder_closure_id, request_status="confirmed")
    savings = round(float(row.get("savings_balance") or 0) - amount, 2)
    ctx.update("builder_accounts", builder_account_id, status="closed_early", closed_date=today,
               closure_reason="borrower_early_close", savings_balance=savings)
    rid = ctx.make_id("bsa_", builder_closure_id, builder_account_id, amount)
    ctx.create("builder_transactions", rid, builder_txn_id=rid, builder_account_id=builder_account_id,
               customer_id=row.get("customer_id"), event_type="builder_savings_applied_to_loan",
               txn_date=today, amount=amount, interest_portion=0.0, principal_portion=0.0)
    return (f"Early closure confirmed: account {builder_account_id} closed on {today}; savings applied entry "
            f"{rid} of {amount:.2f} USD; savings balance now {savings:.2f} USD.")


@tool(owner="agent", rw="write")
def relieve_returned_payment_fee_d8e21ef6(ctx: ToolContext, builder_account_id: str, related_txn_id: str,
                                          relief_amount: float) -> str:
    """Grant relief on one returned-payment fee of a Credit Builder account.

    The representative books a fee waiver entry with the courtesy basis, dated today and linked to the
    returned-payment fee it relieves, and lowers the account's unpaid fees by the relief. The borrower sees
    the relief and the lower unpaid-fee balance on the account. Success is a confirmation naming the waiver
    entry, the fee relieved and the amount.

    Args:
        builder_account_id: Id class — reference number of the Credit Builder account, as returned by the
            Credit Builder account lookup.
        related_txn_id: Id class — reference number of the returned-payment fee entry being relieved, as
            listed among the account's entries by the Credit Builder entry lookup.
        relief_amount: Fixed-format class — the relief in USD, a positive amount with 2 decimal places,
            already rounded to the cent (the tool stores it rounded to 2 decimal places).

    Returns:
        A confirmation string of the form "Relief <entry reference> of <amount> USD booked on <account
        reference> against fee <entry reference>; unpaid fees now <amount> USD.", where amounts are USD with 2
        decimal places. Receiving this text means the relief is on the account.
    """
    amount = round(float(relief_amount), 2)
    acct = ctx.find("builder_accounts", builder_account_id=builder_account_id)
    row = acct[0] if acct else {}
    rid = ctx.make_id("brl_", builder_account_id, related_txn_id, amount)
    ctx.create("builder_transactions", rid, builder_txn_id=rid, builder_account_id=builder_account_id,
               customer_id=row.get("customer_id"), event_type="builder_fee_waived", txn_date=ctx.now()[:10],
               amount=amount, interest_portion=0.0, principal_portion=0.0, related_txn_id=related_txn_id,
               waiver_reason="courtesy")
    fees = round(float(row.get("fees_balance") or 0) - amount, 2)
    ctx.update("builder_accounts", builder_account_id, fees_balance=fees)
    return (f"Relief {rid} of {amount:.2f} USD booked on {builder_account_id} against fee {related_txn_id}; "
            f"unpaid fees now {fees:.2f} USD.")


@tool(owner="agent", rw="write")
def credit_goodwill_late_fee_43fbbd15(ctx: ToolContext, builder_account_id: str, related_txn_id: str,
                                      credit_amount: float) -> str:
    """Grant a goodwill credit on one late fee of a Credit Builder account at the borrower's request.

    The representative books a fee waiver entry with the courtesy basis, dated today and linked to the late fee
    it credits, and lowers the account's unpaid fees by the credit. The borrower sees the credit and the lower
    unpaid-fee balance on the account. Success is a confirmation naming the waiver entry, the late fee credited
    and the amount.

    Args:
        builder_account_id: Id class — reference number of the Credit Builder account, as returned by the
            Credit Builder account lookup.
        related_txn_id: Id class — reference number of the late fee entry being credited, as listed among the
            account's entries by the Credit Builder entry lookup.
        credit_amount: Fixed-format class — the credit in USD, a positive amount with 2 decimal places, already
            rounded to the cent (the tool stores it rounded to 2 decimal places).

    Returns:
        A confirmation string of the form "Goodwill credit <entry reference> of <amount> USD booked on <account
        reference> against late fee <entry reference>; unpaid fees now <amount> USD.", where amounts are USD
        with 2 decimal places. Receiving this text means the credit is on the account.
    """
    amount = round(float(credit_amount), 2)
    acct = ctx.find("builder_accounts", builder_account_id=builder_account_id)
    row = acct[0] if acct else {}
    rid = ctx.make_id("bgw_", builder_account_id, related_txn_id, amount)
    ctx.create("builder_transactions", rid, builder_txn_id=rid, builder_account_id=builder_account_id,
               customer_id=row.get("customer_id"), event_type="builder_fee_waived", txn_date=ctx.now()[:10],
               amount=amount, interest_portion=0.0, principal_portion=0.0, related_txn_id=related_txn_id,
               waiver_reason="courtesy")
    fees = round(float(row.get("fees_balance") or 0) - amount, 2)
    ctx.update("builder_accounts", builder_account_id, fees_balance=fees)
    return (f"Goodwill credit {rid} of {amount:.2f} USD booked on {builder_account_id} against late fee "
            f"{related_txn_id}; unpaid fees now {fees:.2f} USD.")


@tool(owner="user", rw="write")
def reenroll_autopay_5af065e7(ctx: ToolContext, builder_account_id: str, bank_account_id: str,
                              payment_due_day: int, next_due_date: str) -> str:
    """The borrower turns AutoPay back on for their own Credit Builder account and sets its due day.

    Turning AutoPay on authorizes recurring monthly debits of the payment from the named linked bank account,
    sets the account's due day to the day given and its next due date to the date given. The borrower sees
    AutoPay on, the due day and the next due date on the account. Success is a confirmation naming
    the account, the debit account, the due day and the next due date.

    Args:
        builder_account_id: Id class — reference number of the borrower's Credit Builder account, as returned
            by the Credit Builder account lookup.
        bank_account_id: Id class — reference number of the borrower's linked checking account the AutoPay
            debits come from, as returned by the linked bank account lookup.
        payment_due_day: Fixed-format class — the due day of the month the account takes, an integer from 1
            to 28 (the current due day when it does not change).
        next_due_date: Fixed-format class — the account's next due date on that due day, written as
            YYYY-MM-DD (calendar date, no time zone); the current next due date when the due day does not
            change.

    Returns:
        A confirmation string of the form "AutoPay on for <account reference> from <bank account reference>;
        due day <day>, next due date <YYYY-MM-DD>." Receiving this text means AutoPay is enrolled and the due
        day and next due date are updated.
    """
    day = int(payment_due_day)
    ctx.update("builder_accounts", builder_account_id, autopay_enrolled=True, bank_account_id=bank_account_id,
               payment_due_day=day, next_due_date=next_due_date)
    return (f"AutoPay on for {builder_account_id} from {bank_account_id}; due day {day}, next due date "
            f"{next_due_date}.")

@tool(owner="agent", rw="write")
def relieve_late_fee_at_closing_c21c573e(ctx: ToolContext, builder_account_id: str, related_txn_id: str, relief_amount: float) -> str:
    """Grant the early-closure relief on one late fee of a Credit Builder account.

    The representative books a fee waiver entry with the courtesy basis, dated today and linked to the
    late fee it relieves, and lowers the account's unpaid fees by the relief. The borrower sees the relief and
    the lower unpaid-fee balance on the account. Success is a confirmation naming the waiver entry, the fee
    relieved and the amount.

    Args:
        builder_account_id: Id class — reference number of the Credit Builder account, as returned by the
            Credit Builder account lookup.
        related_txn_id: Id class — reference number of the late fee entry being relieved, as listed among the
            account's entries by the Credit Builder entry lookup.
        relief_amount: Fixed-format class — the relief in USD, a positive amount with 2 decimal places,
            already rounded to the cent (the tool stores it rounded to 2 decimal places).

    Returns:
        A confirmation string of the form "Early-closure relief <entry reference> of <amount> USD booked on
        <account reference> against fee <entry reference>; unpaid fees now <amount> USD.", where amounts are USD
        with 2 decimal places. Receiving this text means the relief is on the account.
    """
    amount = round(float(relief_amount), 2)
    acct = ctx.find("builder_accounts", builder_account_id=builder_account_id)
    row = acct[0] if acct else {}
    rid = ctx.make_id("bcl_", builder_account_id, related_txn_id, amount)
    ctx.create("builder_transactions", rid, builder_txn_id=rid, builder_account_id=builder_account_id,
               customer_id=row.get("customer_id"), event_type="builder_fee_waived", txn_date=ctx.now()[:10],
               amount=amount, interest_portion=0.0, principal_portion=0.0, related_txn_id=related_txn_id,
               waiver_reason="courtesy")
    fees = round(float(row.get("fees_balance") or 0) - amount, 2)
    ctx.update("builder_accounts", builder_account_id, fees_balance=fees)
    return (f"Early-closure relief {rid} of {amount:.2f} USD booked on {builder_account_id} against fee "
            f"{related_txn_id}; unpaid fees now {fees:.2f} USD.")


@tool(owner="agent", rw="write")
def relieve_returned_fee_at_closing_90cd40e1(ctx: ToolContext, builder_account_id: str, related_txn_id: str, relief_amount: float) -> str:
    """Grant the early-closure relief on one returned-payment fee of a Credit Builder account.

    The representative books a fee waiver entry with the courtesy basis, dated today and linked to the
    returned-payment fee it relieves, and lowers the account's unpaid fees by the relief. The borrower sees the relief and
    the lower unpaid-fee balance on the account. Success is a confirmation naming the waiver entry, the fee
    relieved and the amount.

    Args:
        builder_account_id: Id class — reference number of the Credit Builder account, as returned by the
            Credit Builder account lookup.
        related_txn_id: Id class — reference number of the returned-payment fee entry being relieved, as listed among the
            account's entries by the Credit Builder entry lookup.
        relief_amount: Fixed-format class — the relief in USD, a positive amount with 2 decimal places,
            already rounded to the cent (the tool stores it rounded to 2 decimal places).

    Returns:
        A confirmation string of the form "Early-closure relief <entry reference> of <amount> USD booked on
        <account reference> against fee <entry reference>; unpaid fees now <amount> USD.", where amounts are USD
        with 2 decimal places. Receiving this text means the relief is on the account.
    """
    amount = round(float(relief_amount), 2)
    acct = ctx.find("builder_accounts", builder_account_id=builder_account_id)
    row = acct[0] if acct else {}
    rid = ctx.make_id("bcr_", builder_account_id, related_txn_id, amount)
    ctx.create("builder_transactions", rid, builder_txn_id=rid, builder_account_id=builder_account_id,
               customer_id=row.get("customer_id"), event_type="builder_fee_waived", txn_date=ctx.now()[:10],
               amount=amount, interest_portion=0.0, principal_portion=0.0, related_txn_id=related_txn_id,
               waiver_reason="courtesy")
    fees = round(float(row.get("fees_balance") or 0) - amount, 2)
    ctx.update("builder_accounts", builder_account_id, fees_balance=fees)
    return (f"Early-closure relief {rid} of {amount:.2f} USD booked on {builder_account_id} against fee "
            f"{related_txn_id}; unpaid fees now {fees:.2f} USD.")

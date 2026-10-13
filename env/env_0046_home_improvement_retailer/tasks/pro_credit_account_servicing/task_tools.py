"""Hidden task tools of the pro_credit_account_servicing difficulty (Ridgeline Pro Credit).

Each tool makes one atomic write on a Ridgeline Pro Credit account and is reached through the
unlock/call meta-tools by the name registered in trade.extended.yaml (extended_policies.target_tool).
No tool checks eligibility, prerequisites or amounts: every value is decided by the caller from the
published policy and the records, and the tool lands it as given.
"""

from erlbench import ToolContext, tool


@tool(owner="agent", rw="write")
def post_dispute_credit_3cc5c337(ctx: ToolContext, trade_account_id: str, original_transaction_id: str,
                                 trade_request_id: str, credit_amount: float) -> str:
    """Post the credit that settles an approved invoice dispute on a Ridgeline Pro Credit account.
    One call books one dispute credit line against the disputed invoice, carrying that invoice's
    number and the reference of the invoice dispute request it settles, dated today and placed in
    today's statement period, and lowers the account's current balance by the credited amount. The
    credit then shows in the account's activity and reduces what the business owes.

    Args:
        trade_account_id: Id class — the reference number of the Ridgeline Pro Credit account the
            disputed invoice was charged to, as returned by the Pro Credit account lookup.
        original_transaction_id: Id class — the reference number of the disputed invoice line
            itself, as returned by the Pro Credit activity lookup (the invoice line the dispute
            request names).
        trade_request_id: Id class — the reference number of the invoice dispute request this credit
            settles, as returned by the Pro Credit service request lookup.
        credit_amount: Fixed-format class — the amount credited to the business, in USD, a positive
            number rounded to 2 decimal places (cents); it is booked exactly as given.

    Returns:
        A dict confirming the booking: status ("posted" on success), trade_transaction_id (the
        reference number of the new dispute credit line), invoice_number (the invoice credited,
        exactly as printed), credit_amount (USD, 2 decimal places), transaction_date (YYYY-MM-DD,
        today) and current_balance (the account balance after the credit, USD, 2 decimal places).
    """
    found = ctx.find("trade_accounts", trade_account_id=trade_account_id)
    account = found[0] if found else {}
    invoice = ctx.find("trade_transactions", trade_transaction_id=original_transaction_id)
    invoice_number = (invoice[0].get("invoice_number") if invoice else "") or ""
    amount = round(float(credit_amount), 2)
    rid = ctx.make_id("ttx_", trade_account_id, original_transaction_id, trade_request_id, credit_amount)
    today = ctx.now()[:10]
    ctx.create("trade_transactions", rid, trade_transaction_id=rid, trade_account_id=trade_account_id,
               customer_id=account.get("customer_id"), event_type="trade_dispute_credit_posted",
               transaction_date=today, amount=amount, statement_period=today[:7],
               invoice_number=invoice_number, original_transaction_id=original_transaction_id,
               trade_request_id=trade_request_id, pricing_basis="not_applicable",
               purchase_channel="not_applicable", payment_method="not_applicable",
               return_reason="not_applicable", fee_type="not_applicable", reversal_reason="not_applicable")
    balance = round(float(account.get("current_balance") or 0) - amount, 2)
    ctx.update("trade_accounts", trade_account_id, current_balance=balance)
    return str({"status": "posted", "trade_transaction_id": rid, "invoice_number": invoice_number,
                "credit_amount": amount, "transaction_date": today, "current_balance": balance})


@tool(owner="agent", rw="write")
def assess_late_payment_charge_c9e93ff5(ctx: ToolContext, trade_account_id: str, statement_period: str,
                                        original_transaction_id: str, charge_amount: float) -> str:
    """Charge a late payment charge for one closed statement of a Ridgeline Pro Credit commercial
    account. One call books one late payment charge line that references the statement it is charged
    for and carries that statement's period, dated today, and raises the account's current balance by
    the charge. The charge then shows in the account's activity and is part of what the business owes.

    Args:
        trade_account_id: Id class — the reference number of the Ridgeline Pro Credit account being
            charged, as returned by the Pro Credit account lookup.
        statement_period: Fixed-format class — the billing period of the statement the charge is for,
            written YYYY-MM exactly as it appears on that statement line.
        original_transaction_id: Id class — the reference number of the statement line the charge is
            for, as returned by the Pro Credit activity lookup.
        charge_amount: Fixed-format class — the late payment charge, in USD, a positive number rounded
            to 2 decimal places (cents); it is booked exactly as given.

    Returns:
        A dict confirming the booking: status ("charged" on success), trade_transaction_id (the
        reference number of the new charge line), statement_period (YYYY-MM), charge_amount (USD, 2
        decimal places), transaction_date (YYYY-MM-DD, today) and current_balance (the account balance
        after the charge, USD, 2 decimal places).
    """
    found = ctx.find("trade_accounts", trade_account_id=trade_account_id)
    account = found[0] if found else {}
    amount = round(float(charge_amount), 2)
    rid = ctx.make_id("ttx_", trade_account_id, statement_period, original_transaction_id, charge_amount)
    today = ctx.now()[:10]
    ctx.create("trade_transactions", rid, trade_transaction_id=rid, trade_account_id=trade_account_id,
               customer_id=account.get("customer_id"), event_type="trade_fee_assessed",
               transaction_date=today, amount=amount, statement_period=statement_period,
               fee_type="late_payment_charge", original_transaction_id=original_transaction_id,
               pricing_basis="not_applicable", purchase_channel="not_applicable",
               payment_method="not_applicable", return_reason="not_applicable",
               reversal_reason="not_applicable")
    balance = round(float(account.get("current_balance") or 0) + amount, 2)
    ctx.update("trade_accounts", trade_account_id, current_balance=balance)
    return str({"status": "charged", "trade_transaction_id": rid, "statement_period": statement_period,
                "charge_amount": amount, "transaction_date": today, "current_balance": balance})


@tool(owner="user", rw="write")
def submit_payoff_payment_22b2623b(ctx: ToolContext, trade_account_id: str, payment_amount: float) -> str:
    """Pay off a Ridgeline Pro Credit commercial account by phone: the business itself authorizes and
    submits one debit from its bank account by phone ACH. One call credits one payment line to the
    account today, held on account under a new payment confirmation reference, and lowers the
    account's current balance by the amount paid. The business sees the payment and its confirmation
    reference in the account's activity.

    Args:
        trade_account_id: Id class — the reference number of the Ridgeline Pro Credit account being
            paid, as read out by the agent from the Pro Credit account lookup.
        payment_amount: Fixed-format class — the amount debited from the business's bank account, in
            USD, a positive number rounded to 2 decimal places (cents); it is debited exactly as given.

    Returns:
        A dict confirming the payment: status ("credited" on success), trade_transaction_id (the
        reference number of the new payment line), payment_reference (the phone payment confirmation
        reference, text beginning PH-), payment_amount (USD, 2 decimal places), transaction_date
        (YYYY-MM-DD, today) and current_balance (the account balance after the payment, USD, 2
        decimal places).
    """
    found = ctx.find("trade_accounts", trade_account_id=trade_account_id)
    account = found[0] if found else {}
    amount = round(float(payment_amount), 2)
    rid = ctx.make_id("ttx_", trade_account_id, payment_amount)
    reference = "PH-" + ctx.make_id("", trade_account_id, payment_amount, length=10).upper()
    today = ctx.now()[:10]
    ctx.create("trade_transactions", rid, trade_transaction_id=rid, trade_account_id=trade_account_id,
               customer_id=account.get("customer_id"), event_type="trade_payment_received",
               transaction_date=today, amount=amount, statement_period=today[:7],
               payment_method="phone_ach", payment_reference=reference, applied_invoice_number="",
               pricing_basis="not_applicable", purchase_channel="not_applicable",
               return_reason="not_applicable", fee_type="not_applicable", reversal_reason="not_applicable")
    balance = round(float(account.get("current_balance") or 0) - amount, 2)
    ctx.update("trade_accounts", trade_account_id, current_balance=balance)
    return str({"status": "credited", "trade_transaction_id": rid, "payment_reference": reference,
                "payment_amount": amount, "transaction_date": today, "current_balance": balance})


@tool(owner="agent", rw="write")
def decide_credit_line_increase_746194e9(ctx: ToolContext, trade_account_id: str, trade_request_id: str,
                                         new_credit_limit: float) -> str:
    """Decide a submitted credit line increase request on a Ridgeline Pro Credit account by approving
    it with a new credit line. One call marks the request approved with today's decision date and sets
    the account's credit line to the new figure, recording today as the date the line last changed.
    The business sees the new credit line on the account and the request as approved.

    Args:
        trade_account_id: Id class — the reference number of the Ridgeline Pro Credit account whose
            line changes, as returned by the Pro Credit account lookup.
        trade_request_id: Id class — the reference number of the submitted credit line increase
            request being decided, as returned by the Pro Credit service request lookup.
        new_credit_limit: Fixed-format class — the new credit line, in USD, a positive number with 2
            decimal places; it is set exactly as given.

    Returns:
        A dict confirming the decision: status ("approved" on success), trade_request_id (the request
        decided), previous_credit_limit and new_credit_limit (USD, 2 decimal places) and
        credit_limit_changed_date (YYYY-MM-DD, today).
    """
    found = ctx.find("trade_accounts", trade_account_id=trade_account_id)
    account = found[0] if found else {}
    previous = round(float(account.get("credit_limit") or 0), 2)
    line = round(float(new_credit_limit), 2)
    today = ctx.now()[:10]
    ctx.update("trade_requests", trade_request_id, status="approved", resolved_date=today)
    ctx.update("trade_accounts", trade_account_id, credit_limit=line, credit_limit_changed_date=today)
    return str({"status": "approved", "trade_request_id": trade_request_id,
                "previous_credit_limit": previous, "new_credit_limit": line,
                "credit_limit_changed_date": today})


@tool(owner="agent", rw="write")
def reverse_late_fee_excess_4d4f7d34(ctx: ToolContext, trade_account_id: str, original_transaction_id: str,
                                     reversal_amount: float) -> str:
    """Correct a late fee on a Ridgeline Pro Credit revolving account by reversing part or all of it as a
    posting error. One call books one fee reversal line that references the late fee line being
    corrected, dated today and placed in today's statement period, and lowers the account's current
    balance by the reversed amount. The correction then shows in the account's activity next to the fee.

    Args:
        trade_account_id: Id class — the reference number of the Ridgeline Pro Credit account the late
            fee was charged to, as returned by the Pro Credit account lookup.
        original_transaction_id: Id class — the reference number of the late fee line being corrected,
            as returned by the Pro Credit activity lookup.
        reversal_amount: Fixed-format class — the part of the late fee reversed, in USD, a positive
            number rounded to 2 decimal places (cents); it is booked exactly as given.

    Returns:
        A dict confirming the correction: status ("reversed" on success), trade_transaction_id (the
        reference number of the new reversal line), original_transaction_id (the late fee line
        corrected), reversal_amount (USD, 2 decimal places), transaction_date (YYYY-MM-DD, today) and
        current_balance (the account balance after the correction, USD, 2 decimal places).
    """
    found = ctx.find("trade_accounts", trade_account_id=trade_account_id)
    account = found[0] if found else {}
    amount = round(float(reversal_amount), 2)
    rid = ctx.make_id("ttx_", trade_account_id, original_transaction_id, reversal_amount)
    today = ctx.now()[:10]
    ctx.create("trade_transactions", rid, trade_transaction_id=rid, trade_account_id=trade_account_id,
               customer_id=account.get("customer_id"), event_type="trade_fee_reversed",
               transaction_date=today, amount=amount, statement_period=today[:7],
               original_transaction_id=original_transaction_id, reversal_reason="posting_error",
               fee_type="not_applicable", pricing_basis="not_applicable", purchase_channel="not_applicable",
               payment_method="not_applicable", return_reason="not_applicable")
    balance = round(float(account.get("current_balance") or 0) - amount, 2)
    ctx.update("trade_accounts", trade_account_id, current_balance=balance)
    return str({"status": "reversed", "trade_transaction_id": rid,
                "original_transaction_id": original_transaction_id, "reversal_amount": amount,
                "transaction_date": today, "current_balance": balance})


@tool(owner="user", rw="write")
def submit_minimum_payment_92c17bdd(ctx: ToolContext, trade_account_id: str, payment_amount: float) -> str:
    """Make the statement minimum payment on a Ridgeline Pro Credit revolving account by phone: the
    business itself authorizes and submits one debit from its bank account by phone ACH. One call
    credits one payment line to the account today, held on account under a new payment confirmation
    reference, and lowers the account's current balance by the amount paid. The business sees the
    payment and its confirmation reference in the account's activity.

    Args:
        trade_account_id: Id class — the reference number of the Ridgeline Pro Credit revolving account
            being paid, as read out by the agent from the Pro Credit account lookup.
        payment_amount: Fixed-format class — the amount debited from the business's bank account, in
            USD, a positive number rounded to 2 decimal places (cents); it is debited exactly as given.

    Returns:
        A dict confirming the payment: status ("credited" on success), trade_transaction_id (the
        reference number of the new payment line), payment_reference (the phone payment confirmation
        reference, text beginning PM-), payment_amount (USD, 2 decimal places), transaction_date
        (YYYY-MM-DD, today) and current_balance (the account balance after the payment, USD, 2
        decimal places).
    """
    found = ctx.find("trade_accounts", trade_account_id=trade_account_id)
    account = found[0] if found else {}
    amount = round(float(payment_amount), 2)
    rid = ctx.make_id("ttx_", trade_account_id, "minimum", payment_amount)
    reference = "PM-" + ctx.make_id("", trade_account_id, "minimum", payment_amount, length=10).upper()
    today = ctx.now()[:10]
    ctx.create("trade_transactions", rid, trade_transaction_id=rid, trade_account_id=trade_account_id,
               customer_id=account.get("customer_id"), event_type="trade_payment_received",
               transaction_date=today, amount=amount, statement_period=today[:7],
               payment_method="phone_ach", payment_reference=reference, applied_invoice_number="",
               pricing_basis="not_applicable", purchase_channel="not_applicable",
               return_reason="not_applicable", fee_type="not_applicable", reversal_reason="not_applicable")
    balance = round(float(account.get("current_balance") or 0) - amount, 2)
    ctx.update("trade_accounts", trade_account_id, current_balance=balance)
    return str({"status": "credited", "trade_transaction_id": rid, "payment_reference": reference,
                "payment_amount": amount, "transaction_date": today, "current_balance": balance})

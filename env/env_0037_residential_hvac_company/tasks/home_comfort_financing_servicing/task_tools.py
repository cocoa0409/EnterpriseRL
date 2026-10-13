"""Hidden task tools for the home_comfort_financing_servicing difficulty (Home Comfort Financing).

Each tool lands exactly one atomic write on a Home Comfort Financing account; every amount it books
is worked out beforehand by the caller from the published servicing rules and the account history.
The tools never judge eligibility, timing or prerequisites, and never compute a figure.
"""

from erlbench import ToolContext, tool


@tool(owner="agent", rw="write")
def post_late_fee_ce58c754(ctx: ToolContext, finance_account_id: str, statement_period: str,
                           amount: float) -> str:
    """Post a late fee on a Home Comfort Financing account for one statement month. The fee is added
    to the amount the borrower owes on the account, appears on that month's statement as a late fee
    line dated today, and the account balance rises by the same amount. The call succeeds when the
    receipt below comes back with status "posted".

    Args:
        finance_account_id: Id class — reference number of the financing account the late fee is
            charged to, as shown by the financing account lookup for the verified borrower.
        statement_period: Fixed-format class — the statement month the late fee belongs to, written
            YYYY-MM (four-digit year, hyphen, two-digit month, e.g. 2026-04), in Eastern time.
        amount: Fixed-format class — the late fee to post, in USD, 2 decimal places, always positive,
            already rounded to the cent by the caller.

    Returns:
        A dictionary rendered as text with the keys finance_txn_id (reference number of the new late
        fee line, text), line_type (always "late_fee"), statement_period (YYYY-MM month the fee was
        posted to), amount (USD, 2 decimal places), posted_date (YYYY-MM-DD posting date),
        account_balance (USD, 2 decimal places, the balance owed after the fee) and status
        ("posted" when the fee is on the account).
    """
    found = ctx.find("finance_accounts", finance_account_id=finance_account_id)
    acct = found[0] if found else {}
    rid = ctx.make_id("ftx_", finance_account_id, "late_fee", statement_period, amount)
    posted = ctx.now()[:10]
    ctx.create("finance_transactions", rid, finance_txn_id=rid, finance_account_id=finance_account_id,
               customer_id=acct.get("customer_id"), event_type="finance_statement_charge",
               line_type="late_fee", statement_period=statement_period,
               amount=round(float(amount), 2), posted_date=posted)
    new_balance = round(float(acct.get("account_balance") or 0) + round(float(amount), 2), 2)
    ctx.update("finance_accounts", finance_account_id, account_balance=new_balance)
    return str({"finance_txn_id": rid, "line_type": "late_fee", "statement_period": statement_period,
                "amount": round(float(amount), 2), "posted_date": posted,
                "account_balance": new_balance, "status": "posted"})


@tool(owner="agent", rw="write")
def post_post_promo_interest_b0f5a17d(ctx: ToolContext, finance_account_id: str,
                                      statement_period: str, amount: float) -> str:
    """Post the post-promotional interest charge on a Home Comfort Financing account whose
    promotional period has ended, for one closed statement month. The charge is added to the amount
    the borrower owes, appears on that month's statement as an interest line dated today, and the
    account balance rises by the same amount. The call succeeds when the receipt below comes back
    with status "posted".

    Args:
        finance_account_id: Id class — reference number of the financing account the interest is
            charged to, as shown by the financing account lookup for the verified borrower.
        statement_period: Fixed-format class — the closed statement month the interest charge
            belongs to, written YYYY-MM (four-digit year, hyphen, two-digit month, e.g. 2026-04), in
            Eastern time.
        amount: Fixed-format class — the interest charge to post, in USD, 2 decimal places, always
            positive, already rounded to the cent by the caller.

    Returns:
        A dictionary rendered as text with the keys finance_txn_id (reference number of the new
        interest line, text), line_type (always "interest"), statement_period (YYYY-MM month the
        charge was posted to), amount (USD, 2 decimal places), posted_date (YYYY-MM-DD posting date),
        account_balance (USD, 2 decimal places, the balance owed after the charge) and status
        ("posted" when the charge is on the account).
    """
    found = ctx.find("finance_accounts", finance_account_id=finance_account_id)
    acct = found[0] if found else {}
    rid = ctx.make_id("ftx_", finance_account_id, "post_promo_interest", statement_period, amount)
    posted = ctx.now()[:10]
    ctx.create("finance_transactions", rid, finance_txn_id=rid, finance_account_id=finance_account_id,
               customer_id=acct.get("customer_id"), event_type="finance_statement_charge",
               line_type="interest", statement_period=statement_period,
               amount=round(float(amount), 2), posted_date=posted)
    new_balance = round(float(acct.get("account_balance") or 0) + round(float(amount), 2), 2)
    ctx.update("finance_accounts", finance_account_id, account_balance=new_balance)
    return str({"finance_txn_id": rid, "line_type": "interest", "statement_period": statement_period,
                "amount": round(float(amount), 2), "posted_date": posted,
                "account_balance": new_balance, "status": "posted"})


@tool(owner="user", rw="write")
def submit_payoff_payment_45ecd350(ctx: ToolContext, finance_account_id: str, amount: float,
                                   payment_method: str) -> str:
    """The borrower pays off their own Home Comfort Financing account in full and closes it. The
    payment is drawn today by the method the borrower chooses, posts to the account as a payment line
    with a new confirmation number, the balance owed is cleared to 0.00, and the account becomes paid
    off with today's date as its closing date. The call succeeds when the receipt below comes back
    with status "paid_off".

    Args:
        finance_account_id: Id class — reference number of the borrower's financing account being
            paid off, as the agent reads it from the financing account lookup and hands it over.
        amount: Fixed-format class — the payoff amount the borrower pays, in USD, 2 decimal places,
            always positive, exactly as the agent states it.
        payment_method: Enum class — how the borrower pays: autopay_ach when the payment is drawn
            under the borrower's standing automatic-payment authorization; online_ach when the
            borrower pays once from a checking or savings account by routing and account number;
            debit_card when the borrower pays once with a debit card; check when the borrower pays
            by a paper check that has been received; phone_payment when a customer care agent keys
            the payment in on the borrower's behalf during a call.

    Returns:
        A dictionary rendered as text with the keys finance_txn_id (reference number of the payment
        line, text), payment_reference (confirmation number of the payment, text), amount (USD,
        2 decimal places, the amount paid), payment_method (the method used), posted_date
        (YYYY-MM-DD date the payment posted), account_balance (USD, 2 decimal places, always 0.00
        once paid off), closed_date (YYYY-MM-DD closing date) and status ("paid_off" when the
        account is closed as paid off).
    """
    found = ctx.find("finance_accounts", finance_account_id=finance_account_id)
    acct = found[0] if found else {}
    rid = ctx.make_id("ftx_", finance_account_id, "payoff", amount, payment_method)
    reference = ctx.make_id("HCF", finance_account_id, amount, payment_method, length=10).upper()
    posted = ctx.now()[:10]
    ctx.create("finance_transactions", rid, finance_txn_id=rid, finance_account_id=finance_account_id,
               customer_id=acct.get("customer_id"), event_type="finance_payment",
               line_type="payment", statement_period=posted[:7],
               amount=round(float(amount), 2), posted_date=posted,
               payment_method=payment_method, payment_reference=reference)
    ctx.update("finance_accounts", finance_account_id, account_balance=0.0, status="paid_off",
               closed_date=posted)
    return str({"finance_txn_id": rid, "payment_reference": reference,
                "amount": round(float(amount), 2), "payment_method": payment_method,
                "posted_date": posted, "account_balance": 0.0, "closed_date": posted,
                "status": "paid_off"})


@tool(owner="agent", rw="write")
def post_fixed_rate_interest_d84dbec7(ctx: ToolContext, finance_account_id: str,
                                      statement_period: str, amount: float) -> str:
    """Post the closing interest charge on a fixed-rate Home Comfort Financing account for one
    closed statement month. The charge is added to the amount the borrower owes, appears on that
    month's statement as an interest line dated today, and the account balance rises by the same
    amount. The call succeeds when the receipt below comes back with status "posted".

    Args:
        finance_account_id: Id class — reference number of the fixed-rate financing account the
            interest is charged to, as shown by the financing account lookup for the verified
            borrower.
        statement_period: Fixed-format class — the closed statement month the interest charge
            belongs to, written YYYY-MM (four-digit year, hyphen, two-digit month, e.g. 2026-04), in
            Eastern time.
        amount: Fixed-format class — the interest charge to post, in USD, 2 decimal places, always
            positive, already rounded to the cent by the caller.

    Returns:
        A dictionary rendered as text with the keys finance_txn_id (reference number of the new
        interest line, text), line_type (always "interest"), statement_period (YYYY-MM month the
        charge was posted to), amount (USD, 2 decimal places), posted_date (YYYY-MM-DD posting date),
        account_balance (USD, 2 decimal places, the balance owed after the charge) and status
        ("posted" when the charge is on the account).
    """
    found = ctx.find("finance_accounts", finance_account_id=finance_account_id)
    acct = found[0] if found else {}
    rid = ctx.make_id("ftx_", finance_account_id, "fixed_rate_interest", statement_period, amount)
    posted = ctx.now()[:10]
    ctx.create("finance_transactions", rid, finance_txn_id=rid, finance_account_id=finance_account_id,
               customer_id=acct.get("customer_id"), event_type="finance_statement_charge",
               line_type="interest", statement_period=statement_period,
               amount=round(float(amount), 2), posted_date=posted)
    new_balance = round(float(acct.get("account_balance") or 0) + round(float(amount), 2), 2)
    ctx.update("finance_accounts", finance_account_id, account_balance=new_balance)
    return str({"finance_txn_id": rid, "line_type": "interest", "statement_period": statement_period,
                "amount": round(float(amount), 2), "posted_date": posted,
                "account_balance": new_balance, "status": "posted"})


@tool(owner="user", rw="write")
def submit_makeup_payment_e9bd505b(ctx: ToolContext, finance_account_id: str, amount: float,
                                   payment_method: str) -> str:
    """The borrower makes a one-time payment on their own Home Comfort Financing account to bring a
    missed or returned installment up to date. The payment is drawn today by the method the borrower
    chooses, posts to the account as a payment line with a new confirmation number, and the balance
    owed falls by the amount paid; the account stays open. The call succeeds when the receipt below
    comes back with status "posted".

    Args:
        finance_account_id: Id class — reference number of the borrower's financing account the
            payment is made on, as the agent reads it from the financing account lookup and hands it
            over.
        amount: Fixed-format class — the amount the borrower pays, in USD, 2 decimal places, always
            positive, exactly as the agent states it.
        payment_method: Enum class — how the borrower pays: autopay_ach when the payment is drawn
            under the borrower's standing automatic-payment authorization; online_ach when the
            borrower pays once from a checking or savings account by routing and account number;
            debit_card when the borrower pays once with a debit card; check when the borrower pays
            by a paper check that has been received; phone_payment when a customer care agent keys
            the payment in on the borrower's behalf during a call.

    Returns:
        A dictionary rendered as text with the keys finance_txn_id (reference number of the payment
        line, text), payment_reference (confirmation number of the payment, text), amount (USD,
        2 decimal places, the amount paid), payment_method (the method used), posted_date
        (YYYY-MM-DD date the payment posted), account_balance (USD, 2 decimal places, the balance
        still owed) and status ("posted" when the payment is on the account).
    """
    found = ctx.find("finance_accounts", finance_account_id=finance_account_id)
    acct = found[0] if found else {}
    rid = ctx.make_id("ftx_", finance_account_id, "makeup", amount, payment_method)
    reference = ctx.make_id("HCF", finance_account_id, "makeup", amount, payment_method, length=10).upper()
    posted = ctx.now()[:10]
    ctx.create("finance_transactions", rid, finance_txn_id=rid, finance_account_id=finance_account_id,
               customer_id=acct.get("customer_id"), event_type="finance_payment",
               line_type="payment", statement_period=posted[:7],
               amount=round(float(amount), 2), posted_date=posted,
               payment_method=payment_method, payment_reference=reference)
    new_balance = round(float(acct.get("account_balance") or 0) - round(float(amount), 2), 2)
    ctx.update("finance_accounts", finance_account_id, account_balance=new_balance)
    return str({"finance_txn_id": rid, "payment_reference": reference,
                "amount": round(float(amount), 2), "payment_method": payment_method,
                "posted_date": posted, "account_balance": new_balance, "status": "posted"})


@tool(owner="agent", rw="write")
def post_returned_payment_fee_928f04f0(ctx: ToolContext, finance_account_id: str,
                                       statement_period: str, source_txn_id: str,
                                       amount: float) -> str:
    """Post the returned-payment fee for one payment that the borrower's bank returned unpaid on a
    Home Comfort Financing account. The fee line names the returned payment, appears on the statement
    month given as a returned-payment fee dated today, and the account balance rises by the fee. The
    call succeeds when the receipt below comes back with status "posted".

    Args:
        finance_account_id: Id class — reference number of the financing account the fee is charged
            to, as shown by the financing account lookup for the verified borrower.
        statement_period: Fixed-format class — the statement month the fee belongs to, written
            YYYY-MM (four-digit year, hyphen, two-digit month, e.g. 2026-04), in Eastern time.
        source_txn_id: Id class — reference number of the payment the bank returned (the payment line
            itself, not the returned-payment line), as shown in the account's transaction history.
        amount: Fixed-format class — the fee to post, in USD, 2 decimal places, always positive,
            already rounded to the cent by the caller.

    Returns:
        A dictionary rendered as text with the keys finance_txn_id (reference number of the new fee
        line, text), line_type (always "returned_payment_fee"), statement_period (YYYY-MM month the
        fee was posted to), source_txn_id (reference number of the returned payment the fee names),
        amount (USD, 2 decimal places), posted_date (YYYY-MM-DD posting date), account_balance (USD,
        2 decimal places, the balance owed after the fee) and status ("posted" when the fee is on the
        account).
    """
    found = ctx.find("finance_accounts", finance_account_id=finance_account_id)
    acct = found[0] if found else {}
    rid = ctx.make_id("ftx_", finance_account_id, "returned_payment_fee", statement_period,
                      source_txn_id, amount)
    posted = ctx.now()[:10]
    ctx.create("finance_transactions", rid, finance_txn_id=rid, finance_account_id=finance_account_id,
               customer_id=acct.get("customer_id"), event_type="finance_statement_charge",
               line_type="returned_payment_fee", statement_period=statement_period,
               source_txn_id=source_txn_id, amount=round(float(amount), 2), posted_date=posted)
    new_balance = round(float(acct.get("account_balance") or 0) + round(float(amount), 2), 2)
    ctx.update("finance_accounts", finance_account_id, account_balance=new_balance)
    return str({"finance_txn_id": rid, "line_type": "returned_payment_fee",
                "statement_period": statement_period, "source_txn_id": source_txn_id,
                "amount": round(float(amount), 2), "posted_date": posted,
                "account_balance": new_balance, "status": "posted"})

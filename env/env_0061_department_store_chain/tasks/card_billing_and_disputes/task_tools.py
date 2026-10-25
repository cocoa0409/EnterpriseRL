"""Hidden task tools of the card_billing_and_disputes difficulty (Marlowe & Finch Credit Cards).

Each tool performs one atomic write on a Marlowe & Finch card account record and returns a receipt.
The tools are reached only through the unlock/call meta-tools, by the names the card charter gives.
"""

from erlbench import ToolContext, tool


@tool(owner="agent", rw="write")
def raise_credit_line_b8050b6c(ctx: ToolContext, card_account_id: str, status: str, new_credit_limit: float) -> str:
    """Raise the credit line of one Marlowe & Finch card account on a credit line review. Customer care sets the
    account's credit line to the new amount given and records today's date as the date the credit line last
    changed; the account status, balance, card number and AutoPay do not change, and the status given is only
    confirmed on the receipt. The cardmember can spend up to the new line at once. The receipt confirms the account, the line before and after, and the
    change date.

    Args:
        card_account_id: Id class — the card account number of the account whose line is raised, as returned by
            the card account lookup for the verified customer.
        status: Enum class — the account status shown by the card account lookup, confirmed on the receipt:
            applied when the application still awaits the credit decision; active when the account is open with
            charging privileges; restricted when charging privileges are suspended for missed minimum payments;
            closed when the cardmember has closed the account; charged_off when the account has been charged off
            and placed with recovery; declined when the application was declined.
        new_credit_limit: Fixed-format class — the full new credit line of the account (not the increase), in
            USD, 2 decimal places, a positive amount with no currency sign.

    Returns:
        A dictionary receipt: "status" is "credit_line_changed" when the change is recorded; "card_account_id" is
        the account number changed; "status_confirmed" is the account status given, as confirmed on the receipt;
        "previous_credit_limit" and "credit_limit" are the line before and after the
        change in USD with 2 decimal places; "change_date" is the effective date in YYYY-MM-DD.
    """
    rows = ctx.find("card_accounts", card_account_id=card_account_id)
    previous = round(float(rows[0].get("credit_limit") or 0), 2) if rows else 0.0
    new_line = round(float(new_credit_limit), 2)
    today = ctx.now()[:10]
    ctx.update("card_accounts", card_account_id, credit_limit=new_line, last_credit_limit_change_date=today)
    return str({"status": "credit_line_changed", "card_account_id": card_account_id,
                "status_confirmed": status, "previous_credit_limit": previous, "credit_limit": new_line,
                "change_date": today})


@tool(owner="user", rw="write")
def file_double_posting_notice_03ed3b71(ctx: ToolContext, card_account_id: str, disputed_card_txn_id: str,
                                        disputed_amount: float, statement_period: str) -> str:
    """Give Northgate Retail Bank written notice, through the online billing-error form, that a purchase posted to
    the cardmember's own card account twice. The cardmember submits the notice in person; it opens a billing
    dispute with the reason duplicate charge on the one purchase posting named, for the amount stated, dated
    today, with the outcome pending. While it stays open the amount stated is treated as under open billing
    dispute on the account. The receipt shows the dispute reference and what was recorded.

    Args:
        card_account_id: Id class — the card account number the disputed purchase posted to, as given by the
            representative from the card account lookup.
        disputed_card_txn_id: Id class — the transaction reference number of the one purchase posting the notice says is
            in error, as shown in the account's transaction list and given by the representative.
        disputed_amount: Fixed-format class — the amount in dispute stated on the notice, in USD, 2 decimal
            places, a positive amount with no currency sign.
        statement_period: Fixed-format class — the billing period of the first statement on which the disputed
            posting appeared, as YYYY-MM (the month of that statement's closing date); the notice records that
            statement's closing date.

    Returns:
        A dictionary receipt: "status" is "notice_received" when the dispute is opened; "dispute_id" is the
        dispute reference; "disputed_card_txn_id" is the posting disputed; "dispute_reason" is "duplicate_charge";
        "disputed_amount" is the amount in dispute in USD with 2 decimal places; "first_statement_date" is the closing date
        of the first statement showing the posting in YYYY-MM-DD; "notice_date" is the date the
        notice was received in YYYY-MM-DD; "outcome" is "pending".
    """
    acct = ctx.find("card_accounts", card_account_id=card_account_id)
    customer_id = acct[0].get("customer_id") if acct else ""
    amount = round(float(disputed_amount), 2)
    today = ctx.now()[:10]
    stmts = ctx.find("card_statements", card_account_id=card_account_id, statement_period=statement_period)
    first_statement_date = stmts[0].get("statement_date") if stmts else ""
    rid = ctx.make_id("cdp_", card_account_id, disputed_card_txn_id, amount, statement_period)
    ctx.create("card_disputes", rid, dispute_id=rid, card_account_id=card_account_id, customer_id=customer_id,
               event_type="card_dispute_filed", disputed_card_txn_id=disputed_card_txn_id,
               dispute_reason="duplicate_charge", disputed_amount=amount, notice_date=today,
               notice_channel="online_form", first_statement_date=first_statement_date, outcome="pending",
               resolution_date="")
    return str({"status": "notice_received", "dispute_id": rid, "disputed_card_txn_id": disputed_card_txn_id,
                "dispute_reason": "duplicate_charge", "disputed_amount": amount,
                "first_statement_date": first_statement_date, "notice_date": today,
                "outcome": "pending"})


@tool(owner="user", rw="write")
def file_missing_credit_notice_85b33449(ctx: ToolContext, card_account_id: str, disputed_card_txn_id: str,
                                        disputed_amount: float, statement_period: str) -> str:
    """Give Northgate Retail Bank written notice, through the online billing-error form, that a Marlowe & Finch refund
    settled to the cardmember's own card account has not been credited in full. The cardmember submits the notice in
    person; it opens a billing dispute with the reason credit not posted on the purchase posting named, for the amount
    stated, dated today, with the outcome pending. While it stays open the amount stated is treated as under open
    billing dispute on the account. The receipt shows the dispute reference and what was recorded.

    Args:
        card_account_id: Id class — the card account number the refunded purchase was charged to, as given by the
            representative from the card account lookup.
        disputed_card_txn_id: Id class — the transaction reference number of the purchase posting whose refund has not
            been credited, as shown in the account's transaction list and given by the representative.
        disputed_amount: Fixed-format class — the amount in dispute stated on the notice, in USD, 2 decimal places, a
            positive amount with no currency sign.
        statement_period: Fixed-format class — the billing period of the first statement on which the named purchase
            posting appeared, as YYYY-MM (the month of that statement's closing date); the notice records that
            statement's closing date.

    Returns:
        A dictionary receipt: "status" is "notice_received" when the dispute is opened; "dispute_id" is the dispute
        reference; "disputed_card_txn_id" is the posting named; "dispute_reason" is "credit_not_posted";
        "disputed_amount" is the amount in dispute in USD with 2 decimal places; "first_statement_date" is the closing
        date of the first statement showing the posting in YYYY-MM-DD; "notice_date" is the date the notice was received
        in YYYY-MM-DD; "outcome" is "pending".
    """
    acct = ctx.find("card_accounts", card_account_id=card_account_id)
    customer_id = acct[0].get("customer_id") if acct else ""
    amount = round(float(disputed_amount), 2)
    today = ctx.now()[:10]
    stmts = ctx.find("card_statements", card_account_id=card_account_id, statement_period=statement_period)
    first_statement_date = stmts[0].get("statement_date") if stmts else ""
    rid = ctx.make_id("cdm_", card_account_id, disputed_card_txn_id, amount, statement_period)
    ctx.create("card_disputes", rid, dispute_id=rid, card_account_id=card_account_id, customer_id=customer_id,
               event_type="card_dispute_filed", disputed_card_txn_id=disputed_card_txn_id,
               dispute_reason="credit_not_posted", disputed_amount=amount, notice_date=today,
               notice_channel="online_form", first_statement_date=first_statement_date, outcome="pending",
               resolution_date="")
    return str({"status": "notice_received", "dispute_id": rid, "disputed_card_txn_id": disputed_card_txn_id,
                "dispute_reason": "credit_not_posted", "disputed_amount": amount,
                "first_statement_date": first_statement_date, "notice_date": today, "outcome": "pending"})


@tool(owner="agent", rw="write")
def take_phone_payment_161e7e24(ctx: ToolContext, card_account_id: str, amount: float) -> str:
    """Take a payment by phone from the cardmember's bank account on file and credit it to one Marlowe & Finch card
    account. Customer care records one payment through the phone_agent channel, credited today in the billing period
    that closes next on the account's statement closing day, and lowers the account's current balance by the amount.
    The cardmember sees the payment on the account at once. The receipt shows the payment reference, the amount, the
    credited date, the billing period and the new current balance.

    Args:
        card_account_id: Id class — the card account number the payment is credited to, as returned by the card
            account lookup for the verified customer.
        amount: Fixed-format class — the payment amount in USD, 2 decimal places, a positive amount with no currency
            sign.

    Returns:
        A dictionary receipt: "status" is "payment_credited" when the payment is recorded; "card_txn_id" is the payment
        reference; "amount" is the amount credited in USD with 2 decimal places; "credited_date" is the date credited in
        YYYY-MM-DD; "statement_period" is the billing period in YYYY-MM; "current_balance" is the account balance after
        the payment in USD with 2 decimal places.
    """
    rows = ctx.find("card_accounts", card_account_id=card_account_id)
    acct = rows[0] if rows else {}
    paid = round(float(amount), 2)
    today = ctx.now()[:10]
    year, month, day = int(today[:4]), int(today[5:7]), int(today[8:10])
    closing = int(acct.get("statement_closing_day") or 28)
    if day > closing:
        month += 1
        if month > 12:
            month, year = 1, year + 1
    period = f"{year:04d}-{month:02d}"
    rid = ctx.make_id("cpy_", card_account_id, paid, today)
    ctx.create("card_transactions", rid, card_txn_id=rid, card_account_id=card_account_id,
               customer_id=acct.get("customer_id", ""), event_type="card_payment", txn_date=today, post_date=today,
               amount=paid, merchant_name="", merchant_category="not_applicable", order_number="",
               purchase_id=None, order_event_id=None, return_id=None, original_card_txn_id=None,
               statement_period=period, promo_plan="none", welcome_discount_amount=0.0,
               payment_channel="phone_agent", fee_type="not_applicable", reversal_reason="not_applicable",
               interest_type="not_applicable", dispute_credit_kind="not_applicable", refund_method="not_applicable")
    new_balance = round(float(acct.get("current_balance") or 0) - paid, 2)
    ctx.update("card_accounts", card_account_id, current_balance=new_balance)
    return str({"status": "payment_credited", "card_txn_id": rid, "amount": paid, "credited_date": today,
                "statement_period": period, "current_balance": new_balance})


@tool(owner="agent", rw="write")
def grant_courtesy_credit_38b9fa68(ctx: ToolContext, card_account_id: str, original_card_txn_id: str,
                                   amount: float) -> str:
    """Reverse a late fee on one Marlowe & Finch card account as a courtesy. Customer care records one fee reversal
    for the late fee named, with the reason courtesy waiver, for the amount given, credited today, and lowers the
    account's current balance by that amount. The cardmember sees the credit on the account at once. The receipt
    shows the reversal reference, the fee reversed, the amount and the new current balance.

    Args:
        card_account_id: Id class — the card account number the late fee was assessed on, as returned by the card
            account lookup for the verified customer.
        original_card_txn_id: Id class — the transaction reference number of the late fee being reversed, as shown in
            the account's transaction list.
        amount: Fixed-format class — the amount reversed in USD, 2 decimal places, a positive amount with no currency
            sign.

    Returns:
        A dictionary receipt: "status" is "fee_reversed" when the reversal is recorded; "card_txn_id" is the reversal
        reference; "original_card_txn_id" is the late fee reversed; "reversal_reason" is "courtesy_waiver"; "amount" is
        the amount reversed in USD with 2 decimal places; "current_balance" is the account balance after the reversal in
        USD with 2 decimal places.
    """
    rows = ctx.find("card_accounts", card_account_id=card_account_id)
    acct = rows[0] if rows else {}
    credit = round(float(amount), 2)
    today = ctx.now()[:10]
    year, month, day = int(today[:4]), int(today[5:7]), int(today[8:10])
    closing = int(acct.get("statement_closing_day") or 28)
    if day > closing:
        month += 1
        if month > 12:
            month, year = 1, year + 1
    period = f"{year:04d}-{month:02d}"
    rid = ctx.make_id("cfr_", card_account_id, original_card_txn_id, credit)
    ctx.create("card_transactions", rid, card_txn_id=rid, card_account_id=card_account_id,
               customer_id=acct.get("customer_id", ""), event_type="card_fee_reversal", txn_date=today,
               post_date=today, amount=credit, merchant_name="", merchant_category="not_applicable", order_number="",
               purchase_id=None, order_event_id=None, return_id=None, original_card_txn_id=original_card_txn_id,
               statement_period=period, promo_plan="none", welcome_discount_amount=0.0,
               payment_channel="not_applicable", fee_type="late_fee", reversal_reason="courtesy_waiver",
               interest_type="not_applicable", dispute_credit_kind="not_applicable", refund_method="not_applicable")
    new_balance = round(float(acct.get("current_balance") or 0) - credit, 2)
    ctx.update("card_accounts", card_account_id, current_balance=new_balance)
    return str({"status": "fee_reversed", "card_txn_id": rid, "original_card_txn_id": original_card_txn_id,
                "reversal_reason": "courtesy_waiver", "amount": credit, "current_balance": new_balance})

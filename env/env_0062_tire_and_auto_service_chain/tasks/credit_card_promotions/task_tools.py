"""Hidden task tools of the credit_card_promotions difficulty (Crestline Credit Card, Northgate Bank).

Each tool lands exactly one atomic write on the card ledger with the values the caller passes; none of
them checks eligibility, ownership, status or any other business condition, and none computes a figure.
"""

from erlbench import ToolContext, tool


@tool(owner="agent", rw="write")
def apply_courtesy_fee_credit_68b22b43(ctx: ToolContext, card_account_id: str, source_card_txn_id: str,
                                       amount: float) -> str:
    """Post a courtesy credit against one late fee on a Crestline credit card account. One call adds one
    fee reversal entry to the account ledger, dated today, carrying the reason courtesy_waiver, the late
    fee entry it credits and the credited amount; it writes only that entry and changes no other record
    (the account record's stored balance field is not updated). The call succeeds whenever the account and
    the amount are supplied, and the receipt carries the new ledger entry's reference.

    Args:
        card_account_id: Id class — the reference number of the Crestline credit card account receiving
            the credit, read from the card account lookup.
        source_card_txn_id: Id class — the ledger entry reference number of the late fee being credited,
            read from the card ledger lookup of that account.
        amount: Fixed-format class — the courtesy credit, expressed as USD, 2 decimal places, positive;
            the value is kept rounded half up to the cent.

    Returns:
        A dictionary receipt: status (text, always "posted" on success), card_txn_id (text, reference of
        the new fee reversal ledger entry), card_account_id (text, the account credited),
        source_card_txn_id (text, the late fee entry credited), reversal_reason (text, always
        "courtesy_waiver"), amount (number, USD with 2 decimal places, the amount credited) and txn_date
        (text, YYYY-MM-DD posting date).
    """
    amt = round(float(amount), 2)
    acct = ctx.find("card_accounts", card_account_id=card_account_id)
    cust = acct[0].get("customer_id") if acct else None
    rid = ctx.make_id("cfr_", card_account_id, source_card_txn_id, amt)
    day = ctx.now()[:10]
    ctx.create("card_transactions", rid, card_txn_id=rid, card_account_id=card_account_id, customer_id=cust,
               event_type="card_fee_reversal", txn_date=day, amount=amt, store_id=None, source_ticket_number="",
               promo_plan="none", promo_expiration_date="", statement_date="", min_payment_due=0.0,
               payment_due_date="", payment_channel="none", payment_reference="",
               source_card_txn_id=source_card_txn_id, reversal_reason="courtesy_waiver")
    return str({"status": "posted", "card_txn_id": rid, "card_account_id": card_account_id,
                "source_card_txn_id": source_card_txn_id, "reversal_reason": "courtesy_waiver",
                "amount": amt, "txn_date": day})


@tool(owner="user", rw="write")
def pay_statement_minimum_b2a1a039(ctx: ToolContext, card_account_id: str, statement_date: str,
                                   amount: float) -> str:
    """The cardholder pays toward one statement of their own Crestline credit card account through the
    automated phone payment line, from the bank account they keep on file. One call records one payment
    on the account ledger, dated today, through the phone channel, tied to the statement it is made
    toward and carrying a new payment confirmation number; it writes only that entry and changes no
    other record (the account record's stored balance field is not updated). The call succeeds whenever the account, the statement and the amount are supplied, and
    the receipt carries the confirmation number the cardholder keeps.

    Args:
        card_account_id: Id class — the reference number of the cardholder's Crestline credit card
            account, read from the card account lookup.
        statement_date: Fixed-format class — the closing date of the statement the payment is made
            toward, exactly as that statement shows it, written YYYY-MM-DD.
        amount: Fixed-format class — the amount paid, expressed as USD, 2 decimal places, positive; the
            value is kept rounded half up to the cent.

    Returns:
        A dictionary receipt: status (text, always "received" on success), payment_reference (text, the
        confirmation number, PMT- followed by 9 digits), card_txn_id (text, reference of the new payment
        ledger entry), card_account_id (text, the account paid), statement_date (text, YYYY-MM-DD, the
        statement paid toward), amount (number, USD with 2 decimal places, the amount paid),
        payment_channel (text, always "phone") and txn_date (text, YYYY-MM-DD posting date).
    """
    amt = round(float(amount), 2)
    acct = ctx.find("card_accounts", card_account_id=card_account_id)
    cust = acct[0].get("customer_id") if acct else None
    rid = ctx.make_id("cpm_", card_account_id, statement_date, amt)
    ref = "PMT-3" + str(int(rid[4:], 16) % 100000000).zfill(8)
    day = ctx.now()[:10]
    ctx.create("card_transactions", rid, card_txn_id=rid, card_account_id=card_account_id, customer_id=cust,
               event_type="card_payment", txn_date=day, amount=amt, store_id=None, source_ticket_number="",
               promo_plan="none", promo_expiration_date="", statement_date=statement_date, min_payment_due=0.0,
               payment_due_date="", payment_channel="phone", payment_reference=ref, source_card_txn_id=None,
               reversal_reason="none")
    return str({"status": "received", "payment_reference": ref, "card_txn_id": rid,
                "card_account_id": card_account_id, "statement_date": statement_date, "amount": amt,
                "payment_channel": "phone", "txn_date": day})


@tool(owner="agent", rw="write")
def credit_returned_payment_fee_d3814d72(ctx: ToolContext, card_account_id: str, source_card_txn_id: str,
                                         amount: float) -> str:
    """Post a courtesy credit against one returned payment fee on a Crestline credit card account. One
    call adds one fee reversal entry to the account ledger, dated today, carrying the reason
    courtesy_waiver, the returned payment fee entry it credits and the credited amount; it writes only
    that entry and changes no other record (the account record's stored balance field is not updated).
    The call succeeds whenever the account and the amount are supplied, and the receipt carries the new
    ledger entry's reference.

    Args:
        card_account_id: Id class — the reference number of the Crestline credit card account receiving
            the credit, read from the card account lookup.
        source_card_txn_id: Id class — the ledger entry reference number of the returned payment fee being
            credited, read from the card ledger lookup of that account.
        amount: Fixed-format class — the courtesy credit, expressed as USD, 2 decimal places, positive;
            the value is kept rounded half up to the cent.

    Returns:
        A dictionary receipt: status (text, always "posted" on success), card_txn_id (text, reference of
        the new fee reversal ledger entry), card_account_id (text, the account credited),
        source_card_txn_id (text, the returned payment fee entry credited), reversal_reason (text, always
        "courtesy_waiver"), amount (number, USD with 2 decimal places, the amount credited) and txn_date
        (text, YYYY-MM-DD posting date).
    """
    amt = round(float(amount), 2)
    acct = ctx.find("card_accounts", card_account_id=card_account_id)
    cust = acct[0].get("customer_id") if acct else None
    rid = ctx.make_id("crf_", card_account_id, source_card_txn_id, amt)
    day = ctx.now()[:10]
    ctx.create("card_transactions", rid, card_txn_id=rid, card_account_id=card_account_id, customer_id=cust,
               event_type="card_fee_reversal", txn_date=day, amount=amt, store_id=None, source_ticket_number="",
               promo_plan="none", promo_expiration_date="", statement_date="", min_payment_due=0.0,
               payment_due_date="", payment_channel="none", payment_reference="",
               source_card_txn_id=source_card_txn_id, reversal_reason="courtesy_waiver")
    return str({"status": "posted", "card_txn_id": rid, "card_account_id": card_account_id,
                "source_card_txn_id": source_card_txn_id, "reversal_reason": "courtesy_waiver",
                "amount": amt, "txn_date": day})


@tool(owner="agent", rw="write")
def assess_deferred_interest_7b31b265(ctx: ToolContext, card_account_id: str, source_card_txn_id: str,
                                      amount: float) -> str:
    """Assess the deferred interest of one promotional purchase on a Crestline credit card account. One
    call adds one deferred interest assessment entry to the account ledger, dated today, citing the
    promotional purchase it concerns, for the amount passed; it writes only that entry and changes no
    other record (the account record's stored balance field is not updated). The call succeeds whenever the
    account, the purchase and the amount are supplied, and the receipt carries the new ledger entry's
    reference.

    Args:
        card_account_id: Id class — the reference number of the Crestline credit card account charged,
            read from the card account lookup.
        source_card_txn_id: Id class — the ledger entry reference number of the promotional purchase the
            interest concerns, read from the card ledger lookup of that account.
        amount: Fixed-format class — the deferred interest assessed, expressed as USD, 2 decimal places,
            positive; the value is kept rounded half up to the cent.

    Returns:
        A dictionary receipt: status (text, always "assessed" on success), card_txn_id (text, reference of
        the new assessment ledger entry), card_account_id (text, the account charged), source_card_txn_id
        (text, the promotional purchase concerned), amount (number, USD with 2 decimal places, the interest
        assessed) and txn_date (text, YYYY-MM-DD posting date).
    """
    amt = round(float(amount), 2)
    acct = ctx.find("card_accounts", card_account_id=card_account_id)
    cust = acct[0].get("customer_id") if acct else None
    rid = ctx.make_id("cdi_", card_account_id, source_card_txn_id, amt)
    day = ctx.now()[:10]
    ctx.create("card_transactions", rid, card_txn_id=rid, card_account_id=card_account_id, customer_id=cust,
               event_type="card_deferred_interest_assessed", txn_date=day, amount=amt, store_id=None,
               source_ticket_number="", promo_plan="none", promo_expiration_date="", statement_date="",
               min_payment_due=0.0, payment_due_date="", payment_channel="none", payment_reference="",
               source_card_txn_id=source_card_txn_id, reversal_reason="none")
    return str({"status": "assessed", "card_txn_id": rid, "card_account_id": card_account_id,
                "source_card_txn_id": source_card_txn_id, "amount": amt, "txn_date": day})


@tool(owner="user", rw="write")
def direct_payment_to_plan_c5f7b721(ctx: ToolContext, card_account_id: str, payment_reference: str,
                                    source_card_txn_id: str, statement_date: str, amount: float) -> str:
    """The cardholder directs part of one of their own payments on a Crestline credit card account to one
    of their deferred-interest promotional purchases. One call records one allocation of that payment to
    that purchase, dated today, citing the payment and the purchase, for the amount passed; it writes
    only that allocation entry and changes no other record. The call succeeds whenever the account, the payment, the purchase, the
    statement and the amount are supplied, and the receipt carries the new allocation's reference.

    Args:
        card_account_id: Id class — the reference number of the cardholder's Crestline credit card account,
            read from the card account lookup.
        payment_reference: Fixed-format class — the confirmation number of the payment being directed,
            PMT- followed by 9 digits, exactly as the payment shows it.
        source_card_txn_id: Id class — the ledger entry reference number of the promotional purchase the
            cardholder names, read from the card ledger lookup of that account.
        statement_date: Fixed-format class — the closing date of the statement the payment was made toward,
            exactly as the payment shows it, written YYYY-MM-DD.
        amount: Fixed-format class — the part of the payment directed to the purchase, expressed as USD,
            2 decimal places, positive; the value is kept rounded half up to the cent.

    Returns:
        A dictionary receipt: status (text, always "directed" on success), card_txn_id (text, reference of
        the new allocation ledger entry), payment_reference (text, the payment directed), source_card_txn_id
        (text, the promotional purchase receiving it), statement_date (text, YYYY-MM-DD), amount (number,
        USD with 2 decimal places, the amount directed) and txn_date (text, YYYY-MM-DD posting date).
    """
    amt = round(float(amount), 2)
    acct = ctx.find("card_accounts", card_account_id=card_account_id)
    cust = acct[0].get("customer_id") if acct else None
    rid = ctx.make_id("cda_", card_account_id, payment_reference, source_card_txn_id, statement_date, amt)
    day = ctx.now()[:10]
    ctx.create("card_transactions", rid, card_txn_id=rid, card_account_id=card_account_id, customer_id=cust,
               event_type="card_payment_allocation", txn_date=day, amount=amt, store_id=None,
               source_ticket_number="", promo_plan="none", promo_expiration_date="", statement_date=statement_date,
               min_payment_due=0.0, payment_due_date="", payment_channel="none", payment_reference=payment_reference,
               source_card_txn_id=source_card_txn_id, reversal_reason="none")
    return str({"status": "directed", "card_txn_id": rid, "payment_reference": payment_reference,
                "source_card_txn_id": source_card_txn_id, "statement_date": statement_date, "amount": amt,
                "txn_date": day})

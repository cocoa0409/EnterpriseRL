"""Hidden task tools of the placed_account_servicing difficulty (Ridgeline Recovery Associates).

Each tool performs one atomic write on a placed consumer account: it books one consumer payment
received through one channel, at the amount the caller passes, and keeps the account's balance due
in step with its money history. No tool checks eligibility, limits or the order of payments; those
are decided from the published policy before the call.
"""

from erlbench import ToolContext, tool


@tool(owner="agent", rw="write")
def take_debit_card_payment_cc21c0ad(ctx: ToolContext, account_id: str, amount: float) -> dict:
    """Take one debit-card payment from the consumer over the phone and post it to one placed
    consumer account. The phone desk charges the consumer's debit card once for the amount given;
    the payment is booked on the account's money history as a consumer payment received today
    through the debit-card channel, with the processor confirmation as its reference, and the
    account's balance due is reduced by the same amount. The receipt gives the consumer the
    confirmation number, and the payment appears in the account's money history dated today. The
    call has succeeded when the receipt shows status posted.

    Args:
        account_id: Id class — the Ridgeline account reference number of the placed consumer account the payment is for, read from the placed-account lookup for this consumer.
        amount: Fixed-format class — the payment amount charged to the debit card, in USD, 2 decimal places, always positive (format USD, 2 decimal places, always positive); the value is kept to 2 decimal places on receipt and the balance due, in USD, is reduced by exactly that amount.

    Returns:
        A dictionary: status (string, "posted" when the payment was booked); payment_reference
        (string, the processor confirmation number of this payment); account_id (string, the
        account reference paid); amount (number, USD to 2 decimal places, the amount posted);
        payment_channel (string, always "debit_card"); posted_date (string, YYYY-MM-DD, the date
        the payment was received); balance_due_after (number, USD to 2 decimal places, the
        account's balance due after this payment, or null when the account reference was not
        found).
    """
    accounts = ctx.find("placed_accounts", account_id=account_id)
    acct = accounts[0] if accounts else {}
    value = round(float(amount), 2)
    rid = ctx.make_id("pdc_", account_id, value, "debit_card")
    ctx.create("account_transactions", rid, txn_id=rid, account_id=account_id,
               customer_id=acct.get("customer_id", ""), agreement_id=acct.get("agreement_id", ""),
               event_type="account_payment_posted", amount=value, txn_date=ctx.now()[:10],
               payment_channel="debit_card", payment_ref=rid, source_txn_id="", plan_id="",
               settlement_id="", adjustment_reason="", client_reference="", return_reason="")
    balance_after = None
    if accounts:
        balance_after = round(float(acct.get("balance_due") or 0) - value, 2)
        ctx.update("placed_accounts", account_id, balance_due=balance_after)
    return {"status": "posted", "payment_reference": rid, "account_id": account_id,
            "amount": value, "payment_channel": "debit_card", "posted_date": ctx.now()[:10],
            "balance_due_after": balance_after}


@tool(owner="agent", rw="write")
def take_credit_card_payment_bec5ec25(ctx: ToolContext, account_id: str, amount: float) -> dict:
    """Take one credit-card payment from the consumer over the phone and post it to one placed
    consumer account. The phone desk charges the consumer's credit card once for the amount given;
    the payment is booked on the account's money history as a consumer payment received today
    through the credit-card channel, with the processor confirmation as its reference, and the
    account's balance due is reduced by the same amount. The receipt gives the consumer the
    confirmation number, and the payment appears in the account's money history dated today. The
    call has succeeded when the receipt shows status posted.

    Args:
        account_id: Id class — the Ridgeline account reference number of the placed consumer account the payment is for, read from the placed-account lookup for this consumer.
        amount: Fixed-format class — the payment amount charged to the credit card, in USD, 2 decimal places, always positive (format USD, 2 decimal places, always positive); the value is kept to 2 decimal places on receipt and the balance due, in USD, is reduced by exactly that amount.

    Returns:
        A dictionary: status (string, "posted" when the payment was booked); payment_reference
        (string, the processor confirmation number of this payment); account_id (string, the
        account reference paid); amount (number, USD to 2 decimal places, the amount posted);
        payment_channel (string, always "credit_card"); posted_date (string, YYYY-MM-DD, the date
        the payment was received); balance_due_after (number, USD to 2 decimal places, the
        account's balance due after this payment, or null when the account reference was not
        found).
    """
    accounts = ctx.find("placed_accounts", account_id=account_id)
    acct = accounts[0] if accounts else {}
    value = round(float(amount), 2)
    rid = ctx.make_id("pcc_", account_id, value, "credit_card")
    ctx.create("account_transactions", rid, txn_id=rid, account_id=account_id,
               customer_id=acct.get("customer_id", ""), agreement_id=acct.get("agreement_id", ""),
               event_type="account_payment_posted", amount=value, txn_date=ctx.now()[:10],
               payment_channel="credit_card", payment_ref=rid, source_txn_id="", plan_id="",
               settlement_id="", adjustment_reason="", client_reference="", return_reason="")
    balance_after = None
    if accounts:
        balance_after = round(float(acct.get("balance_due") or 0) - value, 2)
        ctx.update("placed_accounts", account_id, balance_due=balance_after)
    return {"status": "posted", "payment_reference": rid, "account_id": account_id,
            "amount": value, "payment_channel": "credit_card", "posted_date": ctx.now()[:10],
            "balance_due_after": balance_after}


@tool(owner="user", rw="write")
def make_portal_bank_payment_436b09cd(ctx: ToolContext, account_id: str, amount: float) -> dict:
    """The consumer makes one payment from their own bank account through Ridgeline's payment
    portal toward one placed consumer account. The portal debits the consumer's bank account once
    for the amount entered; the payment is booked on the account's money history as a consumer
    payment received today through the bank-debit channel, with the portal confirmation as its
    reference, and the account's balance due is reduced by the same amount. The consumer sees the
    confirmation number on screen and the payment appears in the account's money history dated
    today. The payment has gone through when the receipt shows status posted.

    Args:
        account_id: Id class — the Ridgeline account reference number of the placed consumer account being paid, as given to the consumer by the agent from the placed-account lookup.
        amount: Fixed-format class — the payment amount debited from the consumer's bank account, in USD, 2 decimal places, always positive (format USD, 2 decimal places, always positive); the value is kept to 2 decimal places on receipt and the balance due, in USD, is reduced by exactly that amount.

    Returns:
        A dictionary: status (string, "posted" when the payment was booked); payment_reference
        (string, the portal confirmation number of this payment); account_id (string, the account
        reference paid); amount (number, USD to 2 decimal places, the amount posted);
        payment_channel (string, always "ach_bank_debit"); posted_date (string, YYYY-MM-DD, the
        date the payment was received); balance_due_after (number, USD to 2 decimal places, the
        account's balance due after this payment, or null when the account reference was not
        found).
    """
    accounts = ctx.find("placed_accounts", account_id=account_id)
    acct = accounts[0] if accounts else {}
    value = round(float(amount), 2)
    rid = ctx.make_id("pbk_", account_id, value, "ach_bank_debit")
    ctx.create("account_transactions", rid, txn_id=rid, account_id=account_id,
               customer_id=acct.get("customer_id", ""), agreement_id=acct.get("agreement_id", ""),
               event_type="account_payment_posted", amount=value, txn_date=ctx.now()[:10],
               payment_channel="ach_bank_debit", payment_ref=rid, source_txn_id="", plan_id="",
               settlement_id="", adjustment_reason="", client_reference="", return_reason="")
    balance_after = None
    if accounts:
        balance_after = round(float(acct.get("balance_due") or 0) - value, 2)
        ctx.update("placed_accounts", account_id, balance_due=balance_after)
    return {"status": "posted", "payment_reference": rid, "account_id": account_id,
            "amount": value, "payment_channel": "ach_bank_debit", "posted_date": ctx.now()[:10],
            "balance_due_after": balance_after}


@tool(owner="user", rw="write")
def make_portal_debit_card_payment_fc4d38a9(ctx: ToolContext, account_id: str, amount: float) -> dict:
    """The consumer makes one debit-card payment through Ridgeline's payment portal toward one
    placed consumer account, keying in their own card. The portal charges the debit card once for the
    amount entered; the payment is booked on the account's money history as a consumer payment
    received today through the debit-card channel, with the portal confirmation as its reference,
    and the account's balance due is reduced by the same amount. The consumer sees the confirmation
    number on screen and the payment appears in the account's money history dated today. The
    payment has gone through when the receipt shows status posted.

    Args:
        account_id: Id class — the Ridgeline account reference number of the placed consumer account being paid, as given to the consumer by the agent from the placed-account lookup.
        amount: Fixed-format class — the payment amount the consumer charges to their own debit card, in USD, 2 decimal places, always positive (format USD, 2 decimal places, always positive); the value is kept to 2 decimal places on receipt and the balance due, in USD, is reduced by exactly that amount.

    Returns:
        A dictionary: status (string, "posted" when the payment was booked); payment_reference
        (string, the portal confirmation number of this payment); account_id (string, the account
        reference paid); amount (number, USD to 2 decimal places, the amount posted);
        payment_channel (string, always "debit_card"); posted_date (string, YYYY-MM-DD, the date the
        payment was received); balance_due_after (number, USD to 2 decimal places, the account's
        balance due after this payment, or null when the account reference was not found).
    """
    accounts = ctx.find("placed_accounts", account_id=account_id)
    acct = accounts[0] if accounts else {}
    value = round(float(amount), 2)
    rid = ctx.make_id("wdc_", account_id, value, "debit_card")
    ctx.create("account_transactions", rid, txn_id=rid, account_id=account_id,
               customer_id=acct.get("customer_id", ""), agreement_id=acct.get("agreement_id", ""),
               event_type="account_payment_posted", amount=value, txn_date=ctx.now()[:10],
               payment_channel="debit_card", payment_ref=rid, source_txn_id="", plan_id="",
               settlement_id="", adjustment_reason="", client_reference="", return_reason="")
    balance_after = None
    if accounts:
        balance_after = round(float(acct.get("balance_due") or 0) - value, 2)
        ctx.update("placed_accounts", account_id, balance_due=balance_after)
    return {"status": "posted", "payment_reference": rid, "account_id": account_id,
            "amount": value, "payment_channel": "debit_card", "posted_date": ctx.now()[:10],
            "balance_due_after": balance_after}


@tool(owner="user", rw="write")
def make_portal_credit_card_payment_7a2662c6(ctx: ToolContext, account_id: str, amount: float) -> dict:
    """The consumer makes one credit-card payment through Ridgeline's payment portal toward one
    placed consumer account, keying in their own card. The portal charges the credit card once for
    the amount entered; the payment is booked on the account's money history as a consumer payment
    received today through the credit-card channel, with the portal confirmation as its reference,
    and the account's balance due is reduced by the same amount. The consumer sees the confirmation
    number on screen and the payment appears in the account's money history dated today. The
    payment has gone through when the receipt shows status posted.

    Args:
        account_id: Id class — the Ridgeline account reference number of the placed consumer account being paid, as given to the consumer by the agent from the placed-account lookup.
        amount: Fixed-format class — the payment amount the consumer charges to their own credit card, in USD, 2 decimal places, always positive (format USD, 2 decimal places, always positive); the value is kept to 2 decimal places on receipt and the balance due, in USD, is reduced by exactly that amount.

    Returns:
        A dictionary: status (string, "posted" when the payment was booked); payment_reference
        (string, the portal confirmation number of this payment); account_id (string, the account
        reference paid); amount (number, USD to 2 decimal places, the amount posted);
        payment_channel (string, always "credit_card"); posted_date (string, YYYY-MM-DD, the date the
        payment was received); balance_due_after (number, USD to 2 decimal places, the account's
        balance due after this payment, or null when the account reference was not found).
    """
    accounts = ctx.find("placed_accounts", account_id=account_id)
    acct = accounts[0] if accounts else {}
    value = round(float(amount), 2)
    rid = ctx.make_id("wcc_", account_id, value, "credit_card")
    ctx.create("account_transactions", rid, txn_id=rid, account_id=account_id,
               customer_id=acct.get("customer_id", ""), agreement_id=acct.get("agreement_id", ""),
               event_type="account_payment_posted", amount=value, txn_date=ctx.now()[:10],
               payment_channel="credit_card", payment_ref=rid, source_txn_id="", plan_id="",
               settlement_id="", adjustment_reason="", client_reference="", return_reason="")
    balance_after = None
    if accounts:
        balance_after = round(float(acct.get("balance_due") or 0) - value, 2)
        ctx.update("placed_accounts", account_id, balance_due=balance_after)
    return {"status": "posted", "payment_reference": rid, "account_id": account_id,
            "amount": value, "payment_channel": "credit_card", "posted_date": ctx.now()[:10],
            "balance_due_after": balance_after}


@tool(owner="agent", rw="write")
def take_phone_bank_payment_d463b192(ctx: ToolContext, account_id: str, amount: float) -> dict:
    """Take one bank-debit payment over the phone on the consumer's recorded authorization and post
    it to one placed consumer account. The phone desk debits the consumer's bank account once for the
    amount given; the payment is booked on the account's money history as a consumer payment received
    today through the bank-debit channel, with the processor confirmation as its reference, and the
    account's balance due is reduced by the same amount. The receipt gives the consumer the
    confirmation number, and the payment appears in the account's money history dated today. The
    call has succeeded when the receipt shows status posted.

    Args:
        account_id: Id class — the Ridgeline account reference number of the placed consumer account being paid, read from the placed-account lookup for this consumer.
        amount: Fixed-format class — the payment amount debited from the consumer's bank account on their recorded phone authorization, in USD, 2 decimal places, always positive (format USD, 2 decimal places, always positive); the value is kept to 2 decimal places on receipt and the balance due, in USD, is reduced by exactly that amount.

    Returns:
        A dictionary: status (string, "posted" when the payment was booked); payment_reference
        (string, the processor confirmation number of this payment); account_id (string, the account
        reference paid); amount (number, USD to 2 decimal places, the amount posted);
        payment_channel (string, always "ach_bank_debit"); posted_date (string, YYYY-MM-DD, the date the
        payment was received); balance_due_after (number, USD to 2 decimal places, the account's
        balance due after this payment, or null when the account reference was not found).
    """
    accounts = ctx.find("placed_accounts", account_id=account_id)
    acct = accounts[0] if accounts else {}
    value = round(float(amount), 2)
    rid = ctx.make_id("pba_", account_id, value, "ach_bank_debit")
    ctx.create("account_transactions", rid, txn_id=rid, account_id=account_id,
               customer_id=acct.get("customer_id", ""), agreement_id=acct.get("agreement_id", ""),
               event_type="account_payment_posted", amount=value, txn_date=ctx.now()[:10],
               payment_channel="ach_bank_debit", payment_ref=rid, source_txn_id="", plan_id="",
               settlement_id="", adjustment_reason="", client_reference="", return_reason="")
    balance_after = None
    if accounts:
        balance_after = round(float(acct.get("balance_due") or 0) - value, 2)
        ctx.update("placed_accounts", account_id, balance_due=balance_after)
    return {"status": "posted", "payment_reference": rid, "account_id": account_id,
            "amount": value, "payment_channel": "ach_bank_debit", "posted_date": ctx.now()[:10],
            "balance_due_after": balance_after}

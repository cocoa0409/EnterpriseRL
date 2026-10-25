"""Hidden task tools of the worker_payroll_card_servicing difficulty (Paystride Visa Payroll Card)."""

from decimal import Decimal, ROUND_HALF_UP

from erlbench import ToolContext, tool


class _CardLedger:
    """Bookkeeping helpers shared by the card ledger tools (not tools themselves)."""

    @staticmethod
    def cents(value) -> float:
        return float(Decimal(str(value)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP))

    @staticmethod
    def plan_error(account, plans) -> str:
        if account.get("variant_name") in plans:
            return ""
        return "Error: this tool serves only cards on the " + " or ".join(p.replace("Paystride Visa Payroll Card ", "") for p in plans) + " plan."

    @staticmethod
    def next_sequence(ctx, card_account_id, event_type, posted_date) -> int:
        rows = ctx.find("card_transactions", card_account_id=card_account_id,
                        event_type=event_type, posted_date=posted_date)
        return len(rows) + 1

    @staticmethod
    def entry(ctx, rid, account, event_type, amount, dispute_id, credit_kind, related_txn_id, today):
        ctx.create("card_transactions", rid, card_txn_id=rid, card_account_id=account["card_account_id"],
                   customer_id=account["customer_id"], event_type=event_type, txn_date=today,
                   posted_date=today, amount=amount,
                   daily_sequence=_CardLedger.next_sequence(ctx, account["card_account_id"], event_type, today),
                   load_source="none", debit_type="none", atm_network="none", foreign_transaction=False,
                   atm_surcharge_usd=0.0, merchant_name="", fee_type="none", refund_reason="none",
                   credit_kind=credit_kind, related_txn_id=related_txn_id, source_ref_id=None,
                   dispute_id=dispute_id)


@tool(owner="user", rw="write")
def sign_card_loss_claim_statement_562d448e(ctx: ToolContext, dispute_id: str, credit_usd: float) -> str:
    """The cardholder signs Paystride's written statement confirming a claim about a lost or stolen
    payroll card on a Premier or Elite plan, a claim given by phone, and the provisional credit for that
    claim posts with the signature. On success the claim records today's date as its written confirmation date, one
    provisional credit for the stated amount is added to the claim's payroll card account, and the card's
    available balance rises by that amount; the claim itself stays under investigation. The cardholder
    sees the credit on the card right away.

    Args:
        dispute_id: Id class — the reference number of the card dispute (claim) the statement confirms, as returned by the card dispute lookup for the cardholder's account.
        credit_usd: Fixed-format class — the provisional credit amount the statement confirms, in US dollars, a positive number with 2 decimal places; a value with more decimals is rounded half up to the cent before it posts.

    Returns:
        A confirmation line naming the provisional credit's transaction reference number (text), the dispute
        reference number (text), the credited amount in US dollars with two decimals, the written
        confirmation date (YYYY-MM-DD) and the card's new available balance in US dollars with two decimals.
        The presence of the transaction reference number shows the credit posted.
    """
    amount = _CardLedger.cents(credit_usd)
    if amount <= 0:
        return "Error: credit_usd must be a positive dollar amount."
    disputes = ctx.find("card_disputes", dispute_id=dispute_id)
    if not disputes:
        return f"Error: no card dispute {dispute_id}."
    dispute = disputes[0]
    if dispute.get("dispute_reason") != "unauthorized_transaction" or not dispute.get("loss_learned_date"):
        return f"Error: dispute {dispute_id} is not a claim about a lost or stolen card."
    if dispute.get("notice_channel") != "phone":
        return f"Error: dispute {dispute_id} was not given by phone."
    if dispute.get("dispute_status") != "investigating":
        return f"Error: dispute {dispute_id} is not under investigation."
    account = ctx.find("card_accounts", card_account_id=dispute["card_account_id"])[0]
    plan_issue = _CardLedger.plan_error(account, ("Paystride Visa Payroll Card Premier", "Paystride Visa Payroll Card Elite"))
    if plan_issue:
        return plan_issue
    today = ctx.now()[:10]
    ctx.update("card_disputes", dispute_id, written_confirmation_date=today)
    rid = ctx.make_id("ctx_", "provisional", dispute_id, amount)
    _CardLedger.entry(ctx, rid, account, "card_provisional_credit", amount, dispute_id, "provisional", None, today)
    balance = _CardLedger.cents(float(account.get("card_balance") or 0) + amount)
    ctx.update("card_accounts", account["card_account_id"], card_balance=balance)
    return (f"Statement signed: provisional credit {rid} of ${amount:.2f} posted on dispute {dispute_id}; "
            f"written confirmation date {today}; available balance ${balance:.2f}.")


@tool(owner="agent", rw="write")
def reverse_card_claim_credit_df02de93(ctx: ToolContext, dispute_id: str, reversal_usd: float) -> str:
    """Take back, from a payroll card account on a Premier or Elite plan, part or all of the provisional
    credit posted on a resolved claim about a lost or stolen card. On success one provisional credit reversal for the stated amount is added to the
    account, pointing to that claim's provisional credit, and the card's available balance falls by that
    amount. The cardholder sees the reversal on the card history.

    Args:
        dispute_id: Id class — the reference number of the resolved card dispute whose provisional credit is taken back, as returned by the card dispute lookup for the cardholder's account.
        reversal_usd: Fixed-format class — the amount taken back, in US dollars, a positive number with 2 decimal places; a value with more decimals is rounded half up to the cent before it posts.

    Returns:
        A confirmation line naming the reversal's transaction reference number (text), the dispute reference
        number (text), the provisional credit it points to (text), the amount taken back in US dollars with
        two decimals and the card's new available balance in US dollars with two decimals. The presence of
        the transaction reference number shows the reversal posted.
    """
    amount = _CardLedger.cents(reversal_usd)
    if amount <= 0:
        return "Error: reversal_usd must be a positive dollar amount."
    disputes = ctx.find("card_disputes", dispute_id=dispute_id)
    if not disputes:
        return f"Error: no card dispute {dispute_id}."
    dispute = disputes[0]
    if dispute.get("dispute_reason") != "unauthorized_transaction" or not dispute.get("loss_learned_date"):
        return f"Error: dispute {dispute_id} is not a claim about a lost or stolen card."
    if dispute.get("dispute_status") not in ("resolved_error_found", "resolved_no_error"):
        return f"Error: dispute {dispute_id} is not resolved."
    account = ctx.find("card_accounts", card_account_id=disputes[0]["card_account_id"])[0]
    plan_issue = _CardLedger.plan_error(account, ("Paystride Visa Payroll Card Premier", "Paystride Visa Payroll Card Elite"))
    if plan_issue:
        return plan_issue
    credits = ctx.find("card_transactions", dispute_id=dispute_id, event_type="card_provisional_credit")
    if not credits:
        return f"Error: dispute {dispute_id} carries no provisional credit."
    related = credits[0]["card_txn_id"]
    today = ctx.now()[:10]
    rid = ctx.make_id("ctx_", "reversal", dispute_id, amount)
    _CardLedger.entry(ctx, rid, account, "card_provisional_credit_reversal", amount, dispute_id, "provisional", related, today)
    balance = _CardLedger.cents(float(account.get("card_balance") or 0) - amount)
    ctx.update("card_accounts", account["card_account_id"], card_balance=balance)
    return (f"Reversal {rid} of ${amount:.2f} posted on dispute {dispute_id} against provisional credit "
            f"{related}; available balance ${balance:.2f}.")


@tool(owner="agent", rw="write")
def post_card_error_claim_credit_b4851c9e(ctx: ToolContext, dispute_id: str, credit_usd: float) -> str:
    """Post the final credit on a claim about a lost or stolen payroll card on a Premier or Elite plan,
    resolved with an error found. On success one final credit for the stated amount is added to the claim's payroll
    card account and the card's available balance rises by that amount. The cardholder sees the credit on
    the card right away.

    Args:
        dispute_id: Id class — the reference number of the resolved card dispute being credited, as returned by the card dispute lookup for the cardholder's account.
        credit_usd: Fixed-format class — the final credit amount, in US dollars, a positive number with 2 decimal places; a value with more decimals is rounded half up to the cent before it posts.

    Returns:
        A confirmation line naming the final credit's transaction reference number (text), the dispute
        reference number (text), the credited amount in US dollars with two decimals and the card's new
        available balance in US dollars with two decimals. The presence of the transaction reference number
        shows the credit posted.
    """
    amount = _CardLedger.cents(credit_usd)
    if amount <= 0:
        return "Error: credit_usd must be a positive dollar amount."
    disputes = ctx.find("card_disputes", dispute_id=dispute_id)
    if not disputes:
        return f"Error: no card dispute {dispute_id}."
    dispute = disputes[0]
    if dispute.get("dispute_reason") != "unauthorized_transaction" or not dispute.get("loss_learned_date"):
        return f"Error: dispute {dispute_id} is not a claim about a lost or stolen card."
    if dispute.get("dispute_status") != "resolved_error_found":
        return f"Error: dispute {dispute_id} is not resolved with an error found."
    account = ctx.find("card_accounts", card_account_id=disputes[0]["card_account_id"])[0]
    plan_issue = _CardLedger.plan_error(account, ("Paystride Visa Payroll Card Premier", "Paystride Visa Payroll Card Elite"))
    if plan_issue:
        return plan_issue
    today = ctx.now()[:10]
    rid = ctx.make_id("ctx_", "final", dispute_id, amount)
    _CardLedger.entry(ctx, rid, account, "card_final_credit", amount, dispute_id, "final", None, today)
    balance = _CardLedger.cents(float(account.get("card_balance") or 0) + amount)
    ctx.update("card_accounts", account["card_account_id"], card_balance=balance)
    return (f"Final credit {rid} of ${amount:.2f} posted on dispute {dispute_id}; "
            f"available balance ${balance:.2f}.")


@tool(owner="user", rw="write")
def sign_card_theft_claim_form_2dc05390(ctx: ToolContext, dispute_id: str, credit_usd: float) -> str:
    """The cardholder signs Paystride's written claim form confirming a claim about a lost or stolen
    payroll card on an Advantage plan, a claim given by phone, and the provisional credit for that
    claim posts with the signature. On success the claim records today's date as its written confirmation date, one
    provisional credit for the stated amount is added to the claim's payroll card account, and the card's
    available balance rises by that amount; the claim itself stays under investigation. The cardholder
    sees the credit on the card right away.

    Args:
        dispute_id: Id class — the reference number of the card dispute (claim) the claim form confirms, as returned by the card dispute lookup for the cardholder's account.
        credit_usd: Fixed-format class — the provisional credit amount the claim form confirms, in US dollars, a positive number with 2 decimal places; a value with more decimals is rounded half up to the cent before it posts.

    Returns:
        A confirmation line naming the provisional credit's transaction reference number (text), the dispute
        reference number (text), the credited amount in US dollars with two decimals, the written
        confirmation date (YYYY-MM-DD) and the card's new available balance in US dollars with two decimals.
        The presence of the transaction reference number shows the credit posted.
    """
    amount = _CardLedger.cents(credit_usd)
    if amount <= 0:
        return "Error: credit_usd must be a positive dollar amount."
    disputes = ctx.find("card_disputes", dispute_id=dispute_id)
    if not disputes:
        return f"Error: no card dispute {dispute_id}."
    dispute = disputes[0]
    if dispute.get("dispute_reason") != "unauthorized_transaction" or not dispute.get("loss_learned_date"):
        return f"Error: dispute {dispute_id} is not a claim about a lost or stolen card."
    if dispute.get("notice_channel") != "phone":
        return f"Error: dispute {dispute_id} was not given by phone."
    if dispute.get("dispute_status") != "investigating":
        return f"Error: dispute {dispute_id} is not under investigation."
    account = ctx.find("card_accounts", card_account_id=dispute["card_account_id"])[0]
    plan_issue = _CardLedger.plan_error(account, ("Paystride Visa Payroll Card Advantage",))
    if plan_issue:
        return plan_issue
    today = ctx.now()[:10]
    ctx.update("card_disputes", dispute_id, written_confirmation_date=today)
    rid = ctx.make_id("ctx_", "provisional", dispute_id, amount)
    _CardLedger.entry(ctx, rid, account, "card_provisional_credit", amount, dispute_id, "provisional", None, today)
    balance = _CardLedger.cents(float(account.get("card_balance") or 0) + amount)
    ctx.update("card_accounts", account["card_account_id"], card_balance=balance)
    return (f"Statement signed: provisional credit {rid} of ${amount:.2f} posted on dispute {dispute_id}; "
            f"written confirmation date {today}; available balance ${balance:.2f}.")


@tool(owner="agent", rw="write")
def take_back_card_claim_excess_b240170d(ctx: ToolContext, dispute_id: str, reversal_usd: float) -> str:
    """Take back, from a payroll card account on an Advantage plan, part or all of the provisional
    credit posted on a resolved claim about a lost or stolen card. On success one provisional credit reversal for the stated amount is added to the
    account, pointing to that claim's provisional credit, and the card's available balance falls by that
    amount. The cardholder sees the reversal on the card history.

    Args:
        dispute_id: Id class — the reference number of the resolved card dispute whose provisional credit is taken back, as returned by the card dispute lookup for the cardholder's account.
        reversal_usd: Fixed-format class — the amount taken back, in US dollars, a positive number with 2 decimal places; a value with more decimals is rounded half up to the cent before it posts.

    Returns:
        A confirmation line naming the reversal's transaction reference number (text), the dispute reference
        number (text), the provisional credit it points to (text), the amount taken back in US dollars with
        two decimals and the card's new available balance in US dollars with two decimals. The presence of
        the transaction reference number shows the reversal posted.
    """
    amount = _CardLedger.cents(reversal_usd)
    if amount <= 0:
        return "Error: reversal_usd must be a positive dollar amount."
    disputes = ctx.find("card_disputes", dispute_id=dispute_id)
    if not disputes:
        return f"Error: no card dispute {dispute_id}."
    dispute = disputes[0]
    if dispute.get("dispute_reason") != "unauthorized_transaction" or not dispute.get("loss_learned_date"):
        return f"Error: dispute {dispute_id} is not a claim about a lost or stolen card."
    if dispute.get("dispute_status") not in ("resolved_error_found", "resolved_no_error"):
        return f"Error: dispute {dispute_id} is not resolved."
    account = ctx.find("card_accounts", card_account_id=disputes[0]["card_account_id"])[0]
    plan_issue = _CardLedger.plan_error(account, ("Paystride Visa Payroll Card Advantage",))
    if plan_issue:
        return plan_issue
    credits = ctx.find("card_transactions", dispute_id=dispute_id, event_type="card_provisional_credit")
    if not credits:
        return f"Error: dispute {dispute_id} carries no provisional credit."
    related = credits[0]["card_txn_id"]
    today = ctx.now()[:10]
    rid = ctx.make_id("ctx_", "reversal", dispute_id, amount)
    _CardLedger.entry(ctx, rid, account, "card_provisional_credit_reversal", amount, dispute_id, "provisional", related, today)
    balance = _CardLedger.cents(float(account.get("card_balance") or 0) - amount)
    ctx.update("card_accounts", account["card_account_id"], card_balance=balance)
    return (f"Reversal {rid} of ${amount:.2f} posted on dispute {dispute_id} against provisional credit "
            f"{related}; available balance ${balance:.2f}.")


@tool(owner="agent", rw="write")
def post_card_claim_settlement_5bc5acd3(ctx: ToolContext, dispute_id: str, credit_usd: float) -> str:
    """Post the final credit on a claim about a lost or stolen payroll card on an Advantage plan,
    resolved with an error found. On success one final credit for the stated amount is added to the claim's payroll
    card account and the card's available balance rises by that amount. The cardholder sees the credit on
    the card right away.

    Args:
        dispute_id: Id class — the reference number of the resolved card dispute being credited, as returned by the card dispute lookup for the cardholder's account.
        credit_usd: Fixed-format class — the final credit amount, in US dollars, a positive number with 2 decimal places; a value with more decimals is rounded half up to the cent before it posts.

    Returns:
        A confirmation line naming the final credit's transaction reference number (text), the dispute
        reference number (text), the credited amount in US dollars with two decimals and the card's new
        available balance in US dollars with two decimals. The presence of the transaction reference number
        shows the credit posted.
    """
    amount = _CardLedger.cents(credit_usd)
    if amount <= 0:
        return "Error: credit_usd must be a positive dollar amount."
    disputes = ctx.find("card_disputes", dispute_id=dispute_id)
    if not disputes:
        return f"Error: no card dispute {dispute_id}."
    dispute = disputes[0]
    if dispute.get("dispute_reason") != "unauthorized_transaction" or not dispute.get("loss_learned_date"):
        return f"Error: dispute {dispute_id} is not a claim about a lost or stolen card."
    if dispute.get("dispute_status") != "resolved_error_found":
        return f"Error: dispute {dispute_id} is not resolved with an error found."
    account = ctx.find("card_accounts", card_account_id=disputes[0]["card_account_id"])[0]
    plan_issue = _CardLedger.plan_error(account, ("Paystride Visa Payroll Card Advantage",))
    if plan_issue:
        return plan_issue
    today = ctx.now()[:10]
    rid = ctx.make_id("ctx_", "final", dispute_id, amount)
    _CardLedger.entry(ctx, rid, account, "card_final_credit", amount, dispute_id, "final", None, today)
    balance = _CardLedger.cents(float(account.get("card_balance") or 0) + amount)
    ctx.update("card_accounts", account["card_account_id"], card_balance=balance)
    return (f"Final credit {rid} of ${amount:.2f} posted on dispute {dispute_id}; "
            f"available balance ${balance:.2f}.")

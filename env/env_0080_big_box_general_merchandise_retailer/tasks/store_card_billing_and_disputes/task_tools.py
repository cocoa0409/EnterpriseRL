"""Hidden task tools for store_card_billing_and_disputes (Northgate Card credit accounts).

Each tool lands one atomic change on a Northgate Card account and returns a receipt. No tool judges
eligibility, timing or amounts; the amounts are worked out beforehand and passed in.
"""

from decimal import Decimal, ROUND_HALF_UP

from erlbench import ToolContext, tool


class _Money:
    """Exact cent handling shared by the tools (values only; no writes)."""

    @staticmethod
    def cents(value) -> float:
        return float(Decimal(str(value)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP))

    @staticmethod
    def positive_cents(value, label: str) -> float:
        amount = _Money.cents(value)
        if amount <= 0:
            raise ValueError(f"{label} must be a positive US dollar amount with at most two decimals")
        if abs(float(value) - amount) > 1e-9:
            raise ValueError(f"{label} must be given in whole cents (two decimal places)")
        return amount


@tool(owner="agent", rw="write")
def settle_duplicate_dispute_b93aba52(ctx: ToolContext, card_account_id: str, dispute_event_id: str,
                                      released_amount_usd: float, final_credit_usd: float) -> str:
    """Close a billing-error dispute about a Northgate purchase posted more than once, in the cardholder's favour, and post its final credit.

    One call records two linked entries on the cardholder's Northgate Card account: the dispute leaves
    dispute status with the outcome resolved for the cardholder, releasing the stated amount from the
    account's disputed balance, and a final dispute credit of the stated amount posts to the account,
    lowering the amount the cardholder owes (it may leave a credit balance). Afterwards the cardholder
    sees the dispute as resolved and the final credit on the account. The receipt confirms both entries.

    Args:
        card_account_id: Id class — the reference number of the Northgate Card account the dispute is on, as returned by the card account lookup for this customer.
        dispute_event_id: Id class — the reference number of the dispute entry being closed (the dispute-opening entry in the card account history), as returned by the card account history lookup.
        released_amount_usd: Fixed-format class — the amount that leaves dispute status, in US dollars as a positive number with 2 decimal places (whole cents; the tool applies no rounding and rejects a value that is not whole cents).
        final_credit_usd: Fixed-format class — the final dispute credit posted to the account, in US dollars as a positive number with 2 decimal places (whole cents; the tool applies no rounding and rejects a value that is not whole cents).

    Returns:
        A text receipt containing: the resolution entry reference (text id), the final credit entry reference (text id), the amount released from dispute status (USD, two decimals), the final credit posted (USD, two decimals), the account's new amount owed (USD, two decimals, negative for a credit balance) and the account's remaining disputed balance (USD, two decimals). A receipt beginning "Dispute resolved for the cardholder" means both entries were recorded.
    """
    released = _Money.positive_cents(released_amount_usd, "released_amount_usd")
    credit = _Money.positive_cents(final_credit_usd, "final_credit_usd")
    today = ctx.now()[:10]
    res_id = ctx.make_id("cev_", card_account_id, dispute_event_id, "resolve", released)
    crd_id = ctx.make_id("cev_", card_account_id, dispute_event_id, "final", credit)
    holder = ctx.find("card_holdings", card_account_id=card_account_id)
    customer_id = holder[0].get("customer_id", "") if holder else ""
    owed = _Money.cents(float(holder[0].get("current_balance") or 0) - credit) if holder else -credit
    disputed = _Money.cents(float(holder[0].get("disputed_balance") or 0) - released) if holder else 0.0
    common = dict(card_account_id=card_account_id, customer_id=customer_id, event_date=today,
                  original_event_id=dispute_event_id)
    ctx.create("card_events", res_id, card_event_id=res_id, event_type="card_resolve_dispute",
               amount_usd=released, dispute_outcome="resolved_for_cardholder", **common)
    ctx.create("card_events", crd_id, card_event_id=crd_id, event_type="card_dispute_credit",
               amount_usd=credit, credit_stage="final", **common)
    ctx.update("card_holdings", card_account_id, current_balance=owed, disputed_balance=disputed)
    return (f"Dispute resolved for the cardholder: resolution entry {res_id}, final credit entry {crd_id}; "
            f"released from dispute {released:.2f} USD; final credit {credit:.2f} USD; "
            f"amount owed now {owed:.2f} USD; disputed balance now {disputed:.2f} USD.")


@tool(owner="agent", rw="write")
def raise_credit_limit_a1e4ca90(ctx: ToolContext, card_account_id: str, new_credit_limit_usd: float) -> str:
    """Set a new credit limit on a cardholder's Northgate Card account after a requested credit line review.

    One call replaces the account's credit limit with the stated amount. Afterwards the cardholder can
    charge up to the new limit and the account shows it as its current credit limit. The receipt
    confirms the change.

    Args:
        card_account_id: Id class — the reference number of the Northgate Card account whose limit changes, as returned by the card account lookup for this customer.
        new_credit_limit_usd: Fixed-format class — the new credit limit in US dollars as a positive number with 2 decimal places (a whole-dollar amount is written with .00; the tool applies no rounding and rejects a value that is not whole cents).

    Returns:
        A text receipt containing the account reference (text id), the previous credit limit (USD, two decimals) and the new credit limit (USD, two decimals). A receipt beginning "Credit limit changed" means the new limit is in effect.
    """
    new_limit = _Money.positive_cents(new_credit_limit_usd, "new_credit_limit_usd")
    holder = ctx.find("card_holdings", card_account_id=card_account_id)
    old_limit = _Money.cents(float(holder[0].get("credit_limit_usd") or 0)) if holder else 0.0
    ctx.update("card_holdings", card_account_id, credit_limit_usd=new_limit)
    return (f"Credit limit changed on account {card_account_id}: previous limit {old_limit:.2f} USD; "
            f"new limit {new_limit:.2f} USD.")


class _Ref:
    """Customer-facing confirmation numbers (values only; no writes)."""

    @staticmethod
    def payment_number(row_id: str) -> str:
        digits = str(int(row_id.split("_")[-1], 16) % 1000000000).zfill(9)
        return "2" + digits

    @staticmethod
    def is_date(text: str) -> bool:
        parts = str(text).split("-")
        return (len(parts) == 3 and len(parts[0]) == 4 and len(parts[1]) == 2 and len(parts[2]) == 2
                and all(p.isdigit() for p in parts) and 1 <= int(parts[1]) <= 12 and 1 <= int(parts[2]) <= 31)


@tool(owner="user", rw="write")
def make_card_payment_5ec32b69(ctx: ToolContext, card_account_id: str, statement_closing_date: str,
                               amount_usd: float) -> str:
    """Let the cardholder make a payment on their own Northgate Card account through the secure payment line, entering their own bank details there.

    The cardholder completes the payment themselves; no bank or card number passes through the
    representative. One call credits the stated amount to the account as a phone payment dated
    today, recorded against the statement whose balance it pays, and lowers the amount the
    cardholder owes by that amount. Afterwards the cardholder sees the payment on the account and
    receives a payment confirmation number. The receipt confirms the payment.

    Args:
        card_account_id: Id class — the reference number of the cardholder's Northgate Card account the payment goes to, as returned by the card account lookup and given to the cardholder by the representative.
        statement_closing_date: Fixed-format class — the closing date of the statement whose balance this payment pays, written YYYY-MM-DD exactly as the statement shows it.
        amount_usd: Fixed-format class — the payment amount in US dollars as a positive number with 2 decimal places (whole cents; the tool applies no rounding and rejects a value that is not whole cents).

    Returns:
        A text receipt containing the payment confirmation number (10 digits), the amount credited (USD, two decimals), the credit date (YYYY-MM-DD), the statement closing date the payment is recorded against (YYYY-MM-DD) and the account's new amount owed (USD, two decimals, negative for a credit balance). A receipt beginning "Payment credited" means the payment is on the account.
    """
    amount = _Money.positive_cents(amount_usd, "amount_usd")
    if not _Ref.is_date(statement_closing_date):
        raise ValueError("statement_closing_date must be a date written YYYY-MM-DD")
    today = ctx.now()[:10]
    rid = ctx.make_id("cev_", card_account_id, statement_closing_date, amount, today)
    confirmation = _Ref.payment_number(rid)
    holder = ctx.find("card_holdings", card_account_id=card_account_id)
    customer_id = holder[0].get("customer_id", "") if holder else ""
    owed = _Money.cents(float(holder[0].get("current_balance") or 0) - amount) if holder else -amount
    ctx.create("card_events", rid, card_event_id=rid, card_account_id=card_account_id, customer_id=customer_id,
               event_type="card_post_payment", event_date=today, amount_usd=amount,
               payment_reference=confirmation, payment_channel="phone", statement_date=statement_closing_date)
    ctx.update("card_holdings", card_account_id, current_balance=owed)
    return (f"Payment credited: confirmation {confirmation}; amount {amount:.2f} USD; credited {today}; "
            f"recorded against the statement closed {statement_closing_date}; amount owed now {owed:.2f} USD.")


@tool(owner="agent", rw="write")
def reverse_late_fee_courtesy_ba087f69(ctx: ToolContext, card_account_id: str, late_fee_event_id: str,
                                       reversal_amount_usd: float) -> str:
    """Reverse all or part of a late fee on a cardholder's Northgate Card account as a courtesy.

    One call posts a courtesy fee reversal of the stated amount against the named late fee and lowers
    the amount the cardholder owes by that amount (it may leave or enlarge a credit balance).
    Afterwards the cardholder sees the courtesy reversal on the account next to the late fee. The
    receipt confirms the reversal.

    Args:
        card_account_id: Id class — the reference number of the Northgate Card account carrying the late fee, as returned by the card account lookup for this customer.
        late_fee_event_id: Id class — the reference number of the late fee entry being reversed, as returned by the card account history lookup.
        reversal_amount_usd: Fixed-format class — the amount of the late fee reversed, in US dollars as a positive number with 2 decimal places (whole cents; the tool applies no rounding and rejects a value that is not whole cents).

    Returns:
        A text receipt containing the reversal entry reference (text id), the late fee entry reversed (text id), the amount reversed (USD, two decimals) and the account's new amount owed (USD, two decimals, negative for a credit balance). A receipt beginning "Courtesy reversal posted" means the reversal is on the account.
    """
    amount = _Money.positive_cents(reversal_amount_usd, "reversal_amount_usd")
    today = ctx.now()[:10]
    rid = ctx.make_id("cev_", card_account_id, late_fee_event_id, "courtesy", amount)
    holder = ctx.find("card_holdings", card_account_id=card_account_id)
    customer_id = holder[0].get("customer_id", "") if holder else ""
    owed = _Money.cents(float(holder[0].get("current_balance") or 0) - amount) if holder else -amount
    ctx.create("card_events", rid, card_event_id=rid, card_account_id=card_account_id, customer_id=customer_id,
               event_type="card_reverse_fee", event_date=today, amount_usd=amount,
               original_event_id=late_fee_event_id, reversal_reason="courtesy_waiver")
    ctx.update("card_holdings", card_account_id, current_balance=owed)
    return (f"Courtesy reversal posted: entry {rid} against late fee {late_fee_event_id}; amount {amount:.2f} USD; "
            f"amount owed now {owed:.2f} USD.")


@tool(owner="user", rw="write")
def refund_credit_balance_0212c7e9(ctx: ToolContext, card_account_id: str, refund_amount_usd: float) -> str:
    """Record the cardholder's own request for a refund of the credit balance on their Northgate Card account, confirmed by the cardholder, and issue the refund.

    The cardholder decides and confirms the request themselves. One call records the request as
    confirmed and posts a credit balance refund of the stated amount, which raises the account's
    amount owed by that amount (bringing a credit balance toward zero). Afterwards the cardholder sees
    the confirmed refund request and the refund on the account. The receipt confirms both.

    Args:
        card_account_id: Id class — the reference number of the cardholder's Northgate Card account, as returned by the card account lookup and given to the cardholder by the representative.
        refund_amount_usd: Fixed-format class — the amount refunded to the cardholder, in US dollars as a positive number with 2 decimal places (whole cents; the tool applies no rounding and rejects a value that is not whole cents).

    Returns:
        A text receipt containing the request reference (text id), the refund entry reference (text id), the amount refunded (USD, two decimals), the refund date (YYYY-MM-DD) and the account's new amount owed (USD, two decimals, negative for a remaining credit balance). A receipt beginning "Credit balance refund issued" means the request is confirmed and the refund posted.
    """
    amount = _Money.positive_cents(refund_amount_usd, "refund_amount_usd")
    today = ctx.now()[:10]
    holder = ctx.find("card_holdings", card_account_id=card_account_id)
    customer_id = holder[0].get("customer_id", "") if holder else ""
    req_id = ctx.make_id("crq_", card_account_id, "credit_balance_refund", amount)
    ref_id = ctx.make_id("cev_", card_account_id, "refund", amount, today)
    owed = _Money.cents(float(holder[0].get("current_balance") or 0) + amount) if holder else amount
    ctx.create("card_requests", req_id, card_request_id=req_id, customer_id=customer_id, card_account_id=card_account_id,
               request_type="credit_balance_refund", request_status="confirmed", created_at=ctx.now())
    ctx.create("card_events", ref_id, card_event_id=ref_id, card_account_id=card_account_id, customer_id=customer_id,
               event_type="card_refund_credit_balance", event_date=today, amount_usd=amount)
    ctx.update("card_holdings", card_account_id, current_balance=owed)
    return (f"Credit balance refund issued: request {req_id} confirmed; refund entry {ref_id}; amount {amount:.2f} USD; "
            f"refund date {today}; amount owed now {owed:.2f} USD.")

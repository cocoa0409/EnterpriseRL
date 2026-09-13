"""Hidden task tools for difficulty checking_fees_overdraft_and_disputes (Personal Checking).

Every tool here performs exactly one atomic posting or record change on a Personal Checking
account with the values the agent supplies. No tool judges eligibility, ownership, status,
timing, deduplication or amounts; those decisions belong to the agent under the published
policy. Row ids are content hashes of every argument; money is rounded to cents; the date
comes only from ctx.now().
"""

from erlbench import ToolContext, tool


@tool(owner="agent", rw="write")
def post_dispute_provisional_credit_5453b90d(ctx: ToolContext, checking_account_id: str, customer_id: str,
                                             checking_dispute_id: str, source_item_id: str, amount: float,
                                             statement_cycle: str) -> str:
    """Post a provisional credit to a Personal Checking account for one electronic-transaction dispute that is under investigation.

    One call writes one provisional credit entry on the account for the named dispute, dated
    today, with the refund reason recorded as a dispute provisional credit and the disputed
    debit recorded as the related entry. The account's posted ledger balance rises by the
    amount at once, and the dispute's status is recorded as provisionally credited. The
    customer sees the credit in the account activity immediately. The tool records exactly the
    amount given and does not check the dispute, its dates or its amount.

    Args:
        checking_account_id: Id class — the reference number of the checking account the disputed debit posted to, as returned by the checking account or dispute lookup before the call.
        customer_id: Id class — the customer reference number of the account owner, as returned by the customer profile lookup.
        checking_dispute_id: Id class — the reference number of the electronic-transaction dispute being credited, as returned by the dispute lookup.
        source_item_id: Id class — the reference number of the disputed debit entry itself, as returned by the dispute lookup (its disputed transaction) or the checking activity lookup.
        amount: Fixed-format class — the provisional credit in U.S. dollars, unit USD, format USD, 2 decimal places, always positive; send a plain number such as 1234.56, rounded half-up to 2 decimal places.
        statement_cycle: Fixed-format class — the statement cycle in which today's posting falls, written YYYY-MM (the month in which that statement cycle closes).

    Returns:
        A confirmation sentence naming the new provisional credit entry reference number, the
        dispute reference number, the amount credited in USD with 2 decimal places, and the
        account's new posted ledger balance in USD with 2 decimal places; receiving it means the
        credit is posted and the dispute is recorded as provisionally credited.
    """
    rid = ctx.make_id("chk_pc_", checking_account_id, customer_id, checking_dispute_id, source_item_id,
                      amount, statement_cycle)
    value = round(float(amount), 2)
    ctx.create("checking_transactions", rid, checking_txn_id=rid, checking_account_id=checking_account_id,
               customer_id=customer_id, event_type="checking_provisional_credit", amount=value,
               posted_date=ctx.now()[:10], channel="none", description="", trace_number="", check_number="",
               atm_operator_surcharge=0.00, fee_code="none", source_item_id=source_item_id,
               statement_cycle=statement_cycle, adjustment_reason="dispute_provisional",
               checking_dispute_id=checking_dispute_id, counterparty_account_id="")
    ctx.update("checking_disputes", checking_dispute_id, dispute_status="provisional_credited")
    account = ctx.find("checking_accounts", checking_account_id=checking_account_id)
    new_balance = round((float(account[0].get("ledger_balance") or 0) if account else 0.0) + value, 2)
    ctx.update("checking_accounts", checking_account_id, ledger_balance=new_balance)
    balance = f"{new_balance:.2f}"
    return (f"Provisional credit {rid} of {value:.2f} USD posted for dispute {checking_dispute_id}; "
            f"new ledger balance {balance} USD.")


@tool(owner="agent", rw="write")
def refund_transfer_fee_error_033d9cbf(ctx: ToolContext, checking_account_id: str, customer_id: str, source_item_id: str,
                                       amount: float, statement_cycle: str) -> str:
    """Refund one overdraft protection transfer fee on a Personal Checking account in full as a bank-error correction.

    One call writes one refund entry on the account, dated today, that refunds the named
    overdraft protection transfer fee entry, records the refund as a bank-error correction for that fee
    code, and raises the account's posted ledger balance by the refunded amount at once. The
    customer sees the refund in the account activity immediately. The tool records exactly the
    amount given against the named fee and does not check the fee, its date, its amount or any
    earlier refund.

    Args:
        checking_account_id: Id class — the reference number of the checking account the fee was charged to, as returned by the checking account lookup before the call.
        customer_id: Id class — the customer reference number of the account owner, as returned by the customer profile lookup.
        source_item_id: Id class — the reference number of the overdraft protection transfer fee entry being refunded, as returned by the checking activity lookup.
        amount: Fixed-format class — the refund in U.S. dollars, unit USD, format USD, 2 decimal places, always positive; send a plain number such as 12.34, rounded half-up to 2 decimal places.
        statement_cycle: Fixed-format class — the statement cycle in which today's posting falls, written YYYY-MM (the month in which that statement cycle closes).

    Returns:
        A confirmation sentence naming the new refund entry reference number, the fee entry it
        refunds, the amount refunded in USD with 2 decimal places, and the account's new posted
        ledger balance in USD with 2 decimal places; receiving it means the refund is posted.
    """
    rid = ctx.make_id("chk_rft_", checking_account_id, customer_id, source_item_id, amount, statement_cycle)
    value = round(float(amount), 2)
    ctx.create("checking_transactions", rid, checking_txn_id=rid, checking_account_id=checking_account_id,
               customer_id=customer_id, event_type="checking_fee_refund", amount=value,
               posted_date=ctx.now()[:10], channel="none", description="", trace_number="", check_number="",
               atm_operator_surcharge=0.00, fee_code="overdraft_transfer", source_item_id=source_item_id,
               statement_cycle=statement_cycle, adjustment_reason="bank_error",
               checking_dispute_id=None, counterparty_account_id="")
    account = ctx.find("checking_accounts", checking_account_id=checking_account_id)
    new_balance = round((float(account[0].get("ledger_balance") or 0) if account else 0.0) + value, 2)
    ctx.update("checking_accounts", checking_account_id, ledger_balance=new_balance)
    return (f"Refund {rid} of {value:.2f} USD posted against fee {source_item_id}; "
            f"new ledger balance {new_balance:.2f} USD.")


@tool(owner="agent", rw="write")
def refund_same_day_maintenance_fee_e9518b99(ctx: ToolContext, checking_account_id: str, customer_id: str, source_item_id: str,
                                             amount: float, statement_cycle: str) -> str:
    """Refund one monthly maintenance fee on a Personal Checking account in full as a bank-error correction.

    One call writes one refund entry on the account, dated today, that refunds the named
    monthly maintenance fee entry, records the refund as a bank-error correction for that fee
    code, and raises the account's posted ledger balance by the refunded amount at once. The
    customer sees the refund in the account activity immediately. The tool records exactly the
    amount given against the named fee and does not check the fee, its date, its amount or any
    earlier refund.

    Args:
        checking_account_id: Id class — the reference number of the checking account the fee was charged to, as returned by the checking account lookup before the call.
        customer_id: Id class — the customer reference number of the account owner, as returned by the customer profile lookup.
        source_item_id: Id class — the reference number of the monthly maintenance fee entry being refunded, as returned by the checking activity lookup.
        amount: Fixed-format class — the refund in U.S. dollars, unit USD, format USD, 2 decimal places, always positive; send a plain number such as 12.34, rounded half-up to 2 decimal places.
        statement_cycle: Fixed-format class — the statement cycle in which today's posting falls, written YYYY-MM (the month in which that statement cycle closes).

    Returns:
        A confirmation sentence naming the new refund entry reference number, the fee entry it
        refunds, the amount refunded in USD with 2 decimal places, and the account's new posted
        ledger balance in USD with 2 decimal places; receiving it means the refund is posted.
    """
    rid = ctx.make_id("chk_rmm_", checking_account_id, customer_id, source_item_id, amount, statement_cycle)
    value = round(float(amount), 2)
    ctx.create("checking_transactions", rid, checking_txn_id=rid, checking_account_id=checking_account_id,
               customer_id=customer_id, event_type="checking_fee_refund", amount=value,
               posted_date=ctx.now()[:10], channel="none", description="", trace_number="", check_number="",
               atm_operator_surcharge=0.00, fee_code="monthly_maintenance", source_item_id=source_item_id,
               statement_cycle=statement_cycle, adjustment_reason="bank_error",
               checking_dispute_id=None, counterparty_account_id="")
    account = ctx.find("checking_accounts", checking_account_id=checking_account_id)
    new_balance = round((float(account[0].get("ledger_balance") or 0) if account else 0.0) + value, 2)
    ctx.update("checking_accounts", checking_account_id, ledger_balance=new_balance)
    return (f"Refund {rid} of {value:.2f} USD posted against fee {source_item_id}; "
            f"new ledger balance {new_balance:.2f} USD.")


@tool(owner="agent", rw="write")
def refund_uncovered_overdraft_fee_6b0f4e50(ctx: ToolContext, checking_account_id: str, customer_id: str, source_item_id: str,
                                            amount: float, statement_cycle: str) -> str:
    """Refund one overdraft item fee on a Personal Checking account in full as a bank-error correction.

    One call writes one refund entry on the account, dated today, that refunds the named
    overdraft item fee entry, records the refund as a bank-error correction for that fee
    code, and raises the account's posted ledger balance by the refunded amount at once. The
    customer sees the refund in the account activity immediately. The tool records exactly the
    amount given against the named fee and does not check the fee, its date, its amount or any
    earlier refund.

    Args:
        checking_account_id: Id class — the reference number of the checking account the fee was charged to, as returned by the checking account lookup before the call.
        customer_id: Id class — the customer reference number of the account owner, as returned by the customer profile lookup.
        source_item_id: Id class — the reference number of the overdraft item fee entry being refunded, as returned by the checking activity lookup.
        amount: Fixed-format class — the refund in U.S. dollars, unit USD, format USD, 2 decimal places, always positive; send a plain number such as 12.34, rounded half-up to 2 decimal places.
        statement_cycle: Fixed-format class — the statement cycle in which today's posting falls, written YYYY-MM (the month in which that statement cycle closes).

    Returns:
        A confirmation sentence naming the new refund entry reference number, the fee entry it
        refunds, the amount refunded in USD with 2 decimal places, and the account's new posted
        ledger balance in USD with 2 decimal places; receiving it means the refund is posted.
    """
    rid = ctx.make_id("chk_rod_", checking_account_id, customer_id, source_item_id, amount, statement_cycle)
    value = round(float(amount), 2)
    ctx.create("checking_transactions", rid, checking_txn_id=rid, checking_account_id=checking_account_id,
               customer_id=customer_id, event_type="checking_fee_refund", amount=value,
               posted_date=ctx.now()[:10], channel="none", description="", trace_number="", check_number="",
               atm_operator_surcharge=0.00, fee_code="overdraft_item", source_item_id=source_item_id,
               statement_cycle=statement_cycle, adjustment_reason="bank_error",
               checking_dispute_id=None, counterparty_account_id="")
    account = ctx.find("checking_accounts", checking_account_id=checking_account_id)
    new_balance = round((float(account[0].get("ledger_balance") or 0) if account else 0.0) + value, 2)
    ctx.update("checking_accounts", checking_account_id, ledger_balance=new_balance)
    return (f"Refund {rid} of {value:.2f} USD posted against fee {source_item_id}; "
            f"new ledger balance {new_balance:.2f} USD.")


@tool(owner="agent", rw="write")
def refund_extended_overdraft_fee_22b46ecc(ctx: ToolContext, checking_account_id: str, customer_id: str, source_item_id: str,
                                           amount: float, statement_cycle: str) -> str:
    """Refund one extended overdraft fee on a Personal Checking account in full as a bank-error correction.

    One call writes one refund entry on the account, dated today, that refunds the named
    extended overdraft fee entry, records the refund as a bank-error correction for that fee
    code, and raises the account's posted ledger balance by the refunded amount at once. The
    customer sees the refund in the account activity immediately. The tool records exactly the
    amount given against the named fee and does not check the fee, its date, its amount or any
    earlier refund.

    Args:
        checking_account_id: Id class — the reference number of the checking account the fee was charged to, as returned by the checking account lookup before the call.
        customer_id: Id class — the customer reference number of the account owner, as returned by the customer profile lookup.
        source_item_id: Id class — the reference number of the extended overdraft fee entry being refunded, as returned by the checking activity lookup.
        amount: Fixed-format class — the refund in U.S. dollars, unit USD, format USD, 2 decimal places, always positive; send a plain number such as 12.34, rounded half-up to 2 decimal places.
        statement_cycle: Fixed-format class — the statement cycle in which today's posting falls, written YYYY-MM (the month in which that statement cycle closes).

    Returns:
        A confirmation sentence naming the new refund entry reference number, the fee entry it
        refunds, the amount refunded in USD with 2 decimal places, and the account's new posted
        ledger balance in USD with 2 decimal places; receiving it means the refund is posted.
    """
    rid = ctx.make_id("chk_rxo_", checking_account_id, customer_id, source_item_id, amount, statement_cycle)
    value = round(float(amount), 2)
    ctx.create("checking_transactions", rid, checking_txn_id=rid, checking_account_id=checking_account_id,
               customer_id=customer_id, event_type="checking_fee_refund", amount=value,
               posted_date=ctx.now()[:10], channel="none", description="", trace_number="", check_number="",
               atm_operator_surcharge=0.00, fee_code="extended_overdraft", source_item_id=source_item_id,
               statement_cycle=statement_cycle, adjustment_reason="bank_error",
               checking_dispute_id=None, counterparty_account_id="")
    account = ctx.find("checking_accounts", checking_account_id=checking_account_id)
    new_balance = round((float(account[0].get("ledger_balance") or 0) if account else 0.0) + value, 2)
    ctx.update("checking_accounts", checking_account_id, ledger_balance=new_balance)
    return (f"Refund {rid} of {value:.2f} USD posted against fee {source_item_id}; "
            f"new ledger balance {new_balance:.2f} USD.")


@tool(owner="agent", rw="write")
def convert_checking_tier_696add48(ctx: ToolContext, checking_account_id: str, customer_id: str,
                                   variant_name: str) -> str:
    """Convert an existing Personal Checking account to a different checking tier while keeping its account number, balance and history.

    One call records the named tier as the account's tier from today. Nothing else on the
    account changes: the balance, activity, statement cycle, overdraft election and overdraft
    protection link stay as they are, and no fee is posted. The customer sees the new tier name
    on the account immediately. The tool records exactly the tier given and does not check the
    customer's qualification for it.

    Args:
        checking_account_id: Id class — the reference number of the checking account being converted, as returned by the checking account lookup before the call.
        customer_id: Id class — the customer reference number of the account owner, as returned by the customer profile lookup.
        variant_name: Enum class — the official full name of the tier the account becomes; one of Access Checking (the checkless tier that never pays into overdraft), Student Checking (the tier for owners aged 17 to 24), Everyday Checking (the standard fee-waivable tier), Interest Checking (the entry interest-bearing tier), Premier Checking (the relationship tier whose relationship balance counts mortgage principal), Private Client Checking (the top tier that requires the Private Client relationship balance).

    Returns:
        A confirmation sentence naming the account reference number, its tier before the call
        and the tier recorded now; receiving it means the conversion is recorded.
    """
    rows = ctx.find("checking_accounts", checking_account_id=checking_account_id)
    before = rows[0].get("variant_name") if rows else ""
    ctx.update("checking_accounts", checking_account_id, variant_name=variant_name)
    return f"Account {checking_account_id} converted from {before} to {variant_name}."

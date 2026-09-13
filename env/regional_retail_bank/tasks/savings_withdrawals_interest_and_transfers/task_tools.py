"""Hidden task tools for regional_retail_bank / savings_withdrawals_interest_and_transfers.

Each tool performs exactly one atomic write on the savings category and is reached through the
unlock/call meta tools; its name is published only by savings.extended.yaml. No tool checks a
business precondition or computes a policy value: the agent decides eligibility and amounts from
the published policy and the records, then passes the decided values in.
"""

from erlbench import ToolContext, tool


@tool(owner="user", rw="write")
def transfer_savings_to_checking_5f60835b(ctx: ToolContext, savings_account_id: str,
                                          destination_checking_account_id: str, amount: float,
                                          statement_cycle: str) -> str:
    """Move money out of your own savings or money market account into one of your own Piedmont Crescent Bank checking accounts, as a telephone transfer you instruct during this call.

    One call posts one withdrawal on the savings account with the telephone banking channel and a new
    posting trace number, naming the receiving checking account as the other side of the transfer; the
    savings account's current balance goes down by the amount at once. The withdrawal's posted date is
    the business day it posts: today when today is a business day (Monday through Friday, other than a
    Federal Reserve holiday), otherwise the next business day. Afterwards the withdrawal shows in the
    savings account's activity with the returned transaction reference.

    Args:
        savings_account_id: Id class — the reference number of the savings or money market account the money leaves, as returned by the savings account lookup.
        destination_checking_account_id: Id class — the reference number of your own checking account that receives the money, as returned by the checking account lookup.
        amount: Fixed-format class — the amount moved, in the account currency "USD, 2 decimal places, always positive"; a positive number in U.S. dollars (unit: USD) rounded to 2 decimal places.
        statement_cycle: Fixed-format class — the statement cycle in which the withdrawal posts, written "YYYY-MM (the month in which the statement cycle closes)", i.e. the YYYY-MM month in which the statement cycle that contains the withdrawal's posted date closes.

    Returns:
        A dictionary rendered as text with the keys savings_txn_id (string, the reference number of the
        posted withdrawal), posted_date (string, YYYY-MM-DD, the business day the withdrawal posted), amount (number, USD with 2
        decimal places), channel (string, always telephone_banking), trace_number (string, 15 digits) and
        new_balance (number, the savings account's current balance after the withdrawal, USD with 2
        decimal places). A returned savings_txn_id means the withdrawal posted.
    """
    amt = round(float(amount), 2)
    rid = ctx.make_id("stx_", savings_account_id, destination_checking_account_id, amt, statement_cycle, ctx.now())
    # Posting-date convention (base savings_withdrawal.posted_date: "Business day the withdrawal posted"):
    # step forward from today to the first Monday-Friday that is not a Federal Reserve holiday.
    y, m, d = (int(p) for p in ctx.now()[:10].split("-"))
    fixed = {(1, 1), (6, 19), (7, 4), (11, 11), (12, 25)}
    while True:
        leap = y % 4 == 0 and (y % 100 != 0 or y % 400 == 0)
        dim = (31, 29 if leap else 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31)[m - 1]
        yy = y - 1 if m < 3 else y
        wd = (yy + yy // 4 - yy // 100 + yy // 400 + (0, 3, 2, 5, 0, 3, 5, 1, 4, 6, 2, 4)[m - 1] + d) % 7
        nth = (d - 1) // 7 + 1  # wd: 0 = Sunday; nth: which occurrence of that weekday in the month
        holiday = ((m, d) in fixed or (wd == 1 and (m, d - 1) in fixed)
                   or (wd == 1 and ((m, nth) in {(1, 3), (2, 3), (9, 1), (10, 2)} or (m == 5 and d + 7 > dim)))
                   or (wd == 4 and m == 11 and nth == 4))
        if 1 <= wd <= 5 and not holiday:
            break
        d += 1
        if d > dim:
            d, m = 1, m + 1
            if m > 12:
                m, y = 1, y + 1
    posted = "%04d-%02d-%02d" % (y, m, d)
    acct = ctx.find("savings_accounts", savings_account_id=savings_account_id)
    owner = acct[0].get("customer_id") if acct else None
    bal = round(float(acct[0].get("current_balance") or 0) - amt, 2) if acct else None
    trace = "2" + str(int(rid.split("_")[-1], 16) % 10 ** 14).zfill(14)  # 15-digit posting trace
    ctx.create("savings_transactions", rid, savings_txn_id=rid, savings_account_id=savings_account_id,
               customer_id=owner, event_type="savings_withdrawal", amount=amt, posted_date=posted,
               channel="telephone_banking", description="TELEPHONE TRANSFER TO CHECKING",
               trace_number=trace, check_number="", fee_code="none", source_item_id="",
               statement_cycle=statement_cycle, adjustment_reason="none", interest_component="none",
               counterparty_account_id=destination_checking_account_id)
    if acct:
        ctx.update("savings_accounts", savings_account_id, current_balance=bal)
    return str({"savings_txn_id": rid, "posted_date": posted, "amount": amt,
                "channel": "telephone_banking", "trace_number": trace, "new_balance": bal})


@tool(owner="agent", rw="write")
def reactivate_savings_account_bfe70db1(ctx: ToolContext, savings_account_id: str, customer_id: str,
                                        reactivation_date: str) -> str:
    """Return a dormant savings or money market account to active status for its owner.

    One call sets the account's status to active and records the given date as the date of the
    account's latest customer-initiated activity, the date from which inactivity is counted again.
    Afterwards the account lookup shows status active and the new activity date.

    Args:
        savings_account_id: Id class — the reference number of the dormant savings or money market account, as returned by the savings account lookup.
        customer_id: Id class — the customer reference number of the account owner whose identity was verified in this conversation, as returned by the customer profile lookup.
        reactivation_date: Fixed-format class — the posted date of the customer-initiated transaction that reactivates the account, in YYYY-MM-DD form.

    Returns:
        A dictionary rendered as text with the keys savings_account_id (string, the account reactivated),
        customer_id (string, the owner), status (string, always active) and
        last_customer_activity_date (string, YYYY-MM-DD, the date recorded). status active means the
        reactivation was recorded.
    """
    ctx.update("savings_accounts", savings_account_id, status="active",
               last_customer_activity_date=reactivation_date)
    return str({"savings_account_id": savings_account_id, "customer_id": customer_id,
                "status": "active", "last_customer_activity_date": reactivation_date})


@tool(owner="agent", rw="write")
def refund_savings_maintenance_fee_bf99bb2f(ctx: ToolContext, savings_account_id: str, customer_id: str,
                                            source_item_id: str, amount: float, adjustment_reason: str,
                                            statement_cycle: str) -> str:
    """Refund one monthly maintenance fee on a savings or money market account back to that account.

    One call posts one refund credit that names the maintenance fee it refunds and the ground for the
    refund; the account's current balance goes up by the refunded amount at once. The refund's posted
    date is the business day it posts: today when today is a business day (Monday through Friday, other than a
    Federal Reserve holiday), otherwise the next business day. Afterwards the refund shows in the account's activity next to the fee it refunds.

    Args:
        savings_account_id: Id class — the reference number of the savings or money market account that was charged, as returned by the savings account lookup.
        customer_id: Id class — the customer reference number of the account owner, as returned by the customer profile lookup.
        source_item_id: Id class — the reference number of the monthly maintenance fee entry being refunded, as returned by the savings activity lookup.
        amount: Fixed-format class — the refunded amount in "USD, 2 decimal places, always positive"; a positive number in U.S. dollars (unit: USD) rounded to 2 decimal places.
        adjustment_reason: Enum class — the ground for the refund; the allowed values are exactly: courtesy_waiver (a goodwill refund of a fee that was charged correctly), bank_error (a refund of a fee that was charged contrary to the savings charter), none (not a refund ground; never used for a refund).
        statement_cycle: Fixed-format class — the statement cycle in which the refund posts, written "YYYY-MM (the month in which the statement cycle closes)", i.e. the YYYY-MM month in which the statement cycle that contains the refund's posted date closes.

    Returns:
        A dictionary rendered as text with the keys savings_txn_id (string, the reference number of the
        refund entry), refunded_fee_id (string, the fee entry refunded), amount (number, USD with 2
        decimal places), adjustment_reason (string, the ground recorded), posted_date (string, YYYY-MM-DD,
        the business day the refund posted) and new_balance (number, the account's current balance after
        the refund, USD with 2 decimal places). A returned savings_txn_id means the refund posted.
    """
    amt = round(float(amount), 2)
    rid = ctx.make_id("srf_", savings_account_id, customer_id, source_item_id, amt, adjustment_reason,
                      statement_cycle)
    # Posting-date convention (base savings_fee_refund / savings_fee posted_date: "Business day the ... posted"):
    # step forward from today to the first Monday-Friday that is not a Federal Reserve holiday.
    y, m, d = (int(p) for p in ctx.now()[:10].split("-"))
    fixed = {(1, 1), (6, 19), (7, 4), (11, 11), (12, 25)}
    while True:
        leap = y % 4 == 0 and (y % 100 != 0 or y % 400 == 0)
        dim = (31, 29 if leap else 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31)[m - 1]
        yy = y - 1 if m < 3 else y
        wd = (yy + yy // 4 - yy // 100 + yy // 400 + (0, 3, 2, 5, 0, 3, 5, 1, 4, 6, 2, 4)[m - 1] + d) % 7
        nth = (d - 1) // 7 + 1  # wd: 0 = Sunday; nth: which occurrence of that weekday in the month
        holiday = ((m, d) in fixed or (wd == 1 and (m, d - 1) in fixed)
                   or (wd == 1 and ((m, nth) in {(1, 3), (2, 3), (9, 1), (10, 2)} or (m == 5 and d + 7 > dim)))
                   or (wd == 4 and m == 11 and nth == 4))
        if 1 <= wd <= 5 and not holiday:
            break
        d += 1
        if d > dim:
            d, m = 1, m + 1
            if m > 12:
                m, y = 1, y + 1
    posted = "%04d-%02d-%02d" % (y, m, d)
    ctx.create("savings_transactions", rid, savings_txn_id=rid, savings_account_id=savings_account_id,
               customer_id=customer_id, event_type="savings_fee_refund", amount=amt,
               posted_date=posted, channel="none", description="", trace_number="",
               check_number="", fee_code="monthly_maintenance", source_item_id=source_item_id,
               statement_cycle=statement_cycle, adjustment_reason=adjustment_reason,
               interest_component="none", counterparty_account_id="")
    acct = ctx.find("savings_accounts", savings_account_id=savings_account_id)
    bal = round(float(acct[0].get("current_balance") or 0) + amt, 2) if acct else None
    if acct:
        ctx.update("savings_accounts", savings_account_id, current_balance=bal)
    return str({"savings_txn_id": rid, "refunded_fee_id": source_item_id, "amount": amt,
                "adjustment_reason": adjustment_reason, "posted_date": posted, "new_balance": bal})


@tool(owner="agent", rw="write")
def convert_savings_tier_d500151b(ctx: ToolContext, savings_account_id: str, variant_name: str) -> str:
    """Convert a savings or money market account to another savings tier, keeping its account number, balance and history.

    One call changes only the account's tier to the named tier, effective today. Afterwards the account
    lookup shows the new tier name.

    Args:
        savings_account_id: Id class — the reference number of the account being converted, as returned by the savings account lookup.
        variant_name: Enum class — the official name of the tier the account converts into; the allowed values are exactly: Starter Savings (the entry savings tier), Statement Savings (the standard statement savings tier), Goal Builder Savings (the goal-based savings tier), Money Market Account (the standard money market tier), Premier Money Market (the higher-balance money market tier), Private Client Money Market (the money market tier reserved for Private Client Checking customers).

    Returns:
        A dictionary rendered as text with the keys savings_account_id (string, the account converted),
        previous_tier (string, the tier before the call) and new_tier (string, the tier after the call).
        new_tier equal to the requested tier means the conversion was recorded.
    """
    acct = ctx.find("savings_accounts", savings_account_id=savings_account_id)
    prev = acct[0].get("variant_name") if acct else None
    ctx.update("savings_accounts", savings_account_id, variant_name=variant_name)
    return str({"savings_account_id": savings_account_id, "previous_tier": prev, "new_tier": variant_name})


@tool(owner="agent", rw="write")
def refund_savings_withdrawal_fee_774e6cc0(ctx: ToolContext, savings_account_id: str, customer_id: str,
                                           source_item_id: str, amount: float, adjustment_reason: str,
                                           statement_cycle: str) -> str:
    """Refund one excess withdrawal fee on a savings or money market account back to that account.

    One call posts one refund credit that names the excess withdrawal fee it refunds and the ground for
    the refund; the account's current balance goes up by the refunded amount at once. The refund's
    posted date is the business day it posts: today when today is a business day (Monday through Friday, other than a
    Federal Reserve holiday), otherwise the next business day. Afterwards the refund shows in the account's activity next to the fee it refunds.

    Args:
        savings_account_id: Id class — the reference number of the savings or money market account that was charged, as returned by the savings account lookup.
        customer_id: Id class — the customer reference number of the account owner, as returned by the customer profile lookup.
        source_item_id: Id class — the reference number of the excess withdrawal fee entry being refunded, as returned by the savings activity lookup.
        amount: Fixed-format class — the refunded amount in "USD, 2 decimal places, always positive"; a positive number in U.S. dollars (unit: USD) rounded to 2 decimal places.
        adjustment_reason: Enum class — the ground for the refund; the allowed values are exactly: courtesy_waiver (a goodwill refund of a fee that was charged correctly), bank_error (a refund of a fee that was charged contrary to the savings charter), none (not a refund ground; never used for a refund).
        statement_cycle: Fixed-format class — the statement cycle in which the refund posts, written "YYYY-MM (the month in which the statement cycle closes)", i.e. the YYYY-MM month in which the statement cycle that contains the refund's posted date closes.

    Returns:
        A dictionary rendered as text with the keys savings_txn_id (string, the reference number of the
        refund entry), refunded_fee_id (string, the fee entry refunded), amount (number, USD with 2
        decimal places), adjustment_reason (string, the ground recorded), posted_date (string, YYYY-MM-DD,
        the business day the refund posted) and new_balance (number, the account's current balance after
        the refund, USD with 2 decimal places). A returned savings_txn_id means the refund posted.
    """
    amt = round(float(amount), 2)
    rid = ctx.make_id("swr_", savings_account_id, customer_id, source_item_id, amt, adjustment_reason,
                      statement_cycle)
    # Posting-date convention (base savings_fee_refund / savings_fee posted_date: "Business day the ... posted"):
    # step forward from today to the first Monday-Friday that is not a Federal Reserve holiday.
    y, m, d = (int(p) for p in ctx.now()[:10].split("-"))
    fixed = {(1, 1), (6, 19), (7, 4), (11, 11), (12, 25)}
    while True:
        leap = y % 4 == 0 and (y % 100 != 0 or y % 400 == 0)
        dim = (31, 29 if leap else 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31)[m - 1]
        yy = y - 1 if m < 3 else y
        wd = (yy + yy // 4 - yy // 100 + yy // 400 + (0, 3, 2, 5, 0, 3, 5, 1, 4, 6, 2, 4)[m - 1] + d) % 7
        nth = (d - 1) // 7 + 1  # wd: 0 = Sunday; nth: which occurrence of that weekday in the month
        holiday = ((m, d) in fixed or (wd == 1 and (m, d - 1) in fixed)
                   or (wd == 1 and ((m, nth) in {(1, 3), (2, 3), (9, 1), (10, 2)} or (m == 5 and d + 7 > dim)))
                   or (wd == 4 and m == 11 and nth == 4))
        if 1 <= wd <= 5 and not holiday:
            break
        d += 1
        if d > dim:
            d, m = 1, m + 1
            if m > 12:
                m, y = 1, y + 1
    posted = "%04d-%02d-%02d" % (y, m, d)
    ctx.create("savings_transactions", rid, savings_txn_id=rid, savings_account_id=savings_account_id,
               customer_id=customer_id, event_type="savings_fee_refund", amount=amt,
               posted_date=posted, channel="none", description="", trace_number="",
               check_number="", fee_code="excess_withdrawal", source_item_id=source_item_id,
               statement_cycle=statement_cycle, adjustment_reason=adjustment_reason,
               interest_component="none", counterparty_account_id="")
    acct = ctx.find("savings_accounts", savings_account_id=savings_account_id)
    bal = round(float(acct[0].get("current_balance") or 0) + amt, 2) if acct else None
    if acct:
        ctx.update("savings_accounts", savings_account_id, current_balance=bal)
    return str({"savings_txn_id": rid, "refunded_fee_id": source_item_id, "amount": amt,
                "adjustment_reason": adjustment_reason, "posted_date": posted, "new_balance": bal})


@tool(owner="agent", rw="write")
def assess_savings_withdrawal_fee_aafc1fb2(ctx: ToolContext, savings_account_id: str, customer_id: str,
                                           source_item_id: str, amount: float, statement_cycle: str) -> str:
    """Charge one excess withdrawal fee on a savings or money market account for one withdrawal.

    One call posts one fee debit with the excess withdrawal fee code, naming the withdrawal that carries
    the fee and the statement cycle the fee belongs to; the account's current balance goes down by the
    fee amount at once. The fee's posted date is the business day it posts: today when today is a business day (Monday through Friday, other than a
    Federal Reserve holiday), otherwise the next business day. Afterwards the fee shows in the account's activity
    next to that withdrawal.

    Args:
        savings_account_id: Id class — the reference number of the savings or money market account being charged, as returned by the savings account lookup.
        customer_id: Id class — the customer reference number of the account owner, as returned by the customer profile lookup.
        source_item_id: Id class — the reference number of the withdrawal entry that carries this fee, as returned by the savings activity lookup.
        amount: Fixed-format class — the fee amount in "USD, 2 decimal places, always positive"; a positive number in U.S. dollars (unit: USD) rounded to 2 decimal places.
        statement_cycle: Fixed-format class — the statement cycle the fee belongs to, written "YYYY-MM (the month in which the statement cycle closes)", i.e. the YYYY-MM month in which the cycle of the withdrawal closes.

    Returns:
        A dictionary rendered as text with the keys savings_txn_id (string, the reference number of the
        fee entry), withdrawal_id (string, the withdrawal the fee is attached to), amount (number, USD
        with 2 decimal places), statement_cycle (string, YYYY-MM), posted_date (string, YYYY-MM-DD, the
        business day the fee posted) and new_balance (number, the account's current balance after the
        fee, USD with 2 decimal places). A returned savings_txn_id means the fee posted.
    """
    amt = round(float(amount), 2)
    rid = ctx.make_id("sfe_", savings_account_id, customer_id, source_item_id, amt, statement_cycle)
    # Posting-date convention (base savings_fee_refund / savings_fee posted_date: "Business day the ... posted"):
    # step forward from today to the first Monday-Friday that is not a Federal Reserve holiday.
    y, m, d = (int(p) for p in ctx.now()[:10].split("-"))
    fixed = {(1, 1), (6, 19), (7, 4), (11, 11), (12, 25)}
    while True:
        leap = y % 4 == 0 and (y % 100 != 0 or y % 400 == 0)
        dim = (31, 29 if leap else 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31)[m - 1]
        yy = y - 1 if m < 3 else y
        wd = (yy + yy // 4 - yy // 100 + yy // 400 + (0, 3, 2, 5, 0, 3, 5, 1, 4, 6, 2, 4)[m - 1] + d) % 7
        nth = (d - 1) // 7 + 1  # wd: 0 = Sunday; nth: which occurrence of that weekday in the month
        holiday = ((m, d) in fixed or (wd == 1 and (m, d - 1) in fixed)
                   or (wd == 1 and ((m, nth) in {(1, 3), (2, 3), (9, 1), (10, 2)} or (m == 5 and d + 7 > dim)))
                   or (wd == 4 and m == 11 and nth == 4))
        if 1 <= wd <= 5 and not holiday:
            break
        d += 1
        if d > dim:
            d, m = 1, m + 1
            if m > 12:
                m, y = 1, y + 1
    posted = "%04d-%02d-%02d" % (y, m, d)
    ctx.create("savings_transactions", rid, savings_txn_id=rid, savings_account_id=savings_account_id,
               customer_id=customer_id, event_type="savings_fee", amount=amt,
               posted_date=posted, channel="none", description="", trace_number="",
               check_number="", fee_code="excess_withdrawal", source_item_id=source_item_id,
               statement_cycle=statement_cycle, adjustment_reason="none",
               interest_component="none", counterparty_account_id="")
    acct = ctx.find("savings_accounts", savings_account_id=savings_account_id)
    bal = round(float(acct[0].get("current_balance") or 0) - amt, 2) if acct else None
    if acct:
        ctx.update("savings_accounts", savings_account_id, current_balance=bal)
    return str({"savings_txn_id": rid, "withdrawal_id": source_item_id, "amount": amt,
                "statement_cycle": statement_cycle, "posted_date": posted, "new_balance": bal})


@tool(owner="user", rw="write")
def set_savings_automatic_transfer_e1e909eb(ctx: ToolContext, savings_account_id: str,
                                            funding_checking_account_id: str, automatic_transfer_amount: float,
                                            automatic_transfer_day: int) -> str:
    """Set up or change your own recurring monthly automatic transfer from one of your Piedmont Crescent Bank checking accounts into your savings or money market account.

    One call records the instruction on the savings account: the fixed monthly amount, the day of the
    month it runs and the checking account it is drawn from, replacing any earlier instruction. The
    transfer first runs on the next occurrence of that day. Afterwards the savings account lookup shows
    the new amount, day and funding checking account.

    Args:
        savings_account_id: Id class — the reference number of the savings or money market account that receives the transfers, as returned by the savings account lookup.
        funding_checking_account_id: Id class — the reference number of your own checking account the transfers are drawn from, as returned by the checking account lookup.
        automatic_transfer_amount: Fixed-format class — the fixed monthly transfer amount in "USD, 2 decimal places"; a positive number in U.S. dollars (unit: USD) rounded to 2 decimal places.
        automatic_transfer_day: Fixed-format class — the day of the month the transfer runs, an integer from 1 to 28 (unit: day of month), as "integer 1-28, or empty string when none"; pass the integer day.

    Returns:
        A dictionary rendered as text with the keys savings_account_id (string, the receiving account),
        automatic_transfer_amount (number, USD with 2 decimal places), automatic_transfer_day (integer,
        1-28) and funding_checking_account_id (string, the funding checking account). A receipt echoing the
        requested amount and day means the instruction is recorded.
    """
    amt = round(float(automatic_transfer_amount), 2)
    day = int(automatic_transfer_day)
    ctx.update("savings_accounts", savings_account_id, automatic_transfer_amount=amt,
               automatic_transfer_day=day, funding_checking_account_id=funding_checking_account_id)
    return str({"savings_account_id": savings_account_id, "automatic_transfer_amount": amt,
                "automatic_transfer_day": day, "funding_checking_account_id": funding_checking_account_id})

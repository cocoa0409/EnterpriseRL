"""Hidden task tools for the savings_withdrawals_interest_and_transfers difficulty.

Each tool performs one atomic posting on a Piedmont Crescent Bank savings or money market
account. None of them aggregates history, reads a rate table or judges eligibility: the agent
works the figure out from the published rules and the account's own records and passes it in.
"""

from erlbench import ToolContext, tool


@tool(owner="agent", rw="write")
def post_promotional_interest_correction_acb0ec5b(ctx: ToolContext, savings_account_id: str,
                                                  customer_id: str, statement_cycle: str,
                                                  correction_amount: float) -> str:
    """Credit a savings or money market account with promotional interest that a past statement cycle left unpaid.

    One call posts a single promotional interest entry to the named account, marked as a bank
    error correction for the statement cycle given, and raises the account's posted balance by the
    credited amount on the spot. The customer sees a new promotional interest line on the account
    with today's posting date, the corrected cycle shown against it, and a balance higher by that
    amount. The call has completed when the confirmation text carries the new entry's reference
    number and the credited amount.

    Args:
        savings_account_id: Id class — the reference number of the savings or money market account the promotional interest is credited to, taken from the savings account lookup.
        customer_id: Id class — the customer reference number of the account owner, taken from the customer profile lookup.
        statement_cycle: Fixed-format class — the statement cycle the unpaid promotional interest belongs to, written as YYYY-MM, the month in which that cycle closed; an empty value is not accepted.
        correction_amount: Fixed-format class — the promotional interest being credited, in USD, 2 decimal places, always positive; values carrying more than 2 decimal places are stored rounded half up to the cent, and the bank's own Eastern Time posting date is used.

    Returns:
        A confirmation sentence containing the reference number of the promotional interest entry
        just created, the credited amount in USD to two decimal places, the statement cycle it was
        booked against, and the account's new posted balance in USD to two decimal places.
        Receiving that sentence is what indicates the credit completed.
    """
    rid = ctx.make_id("sit_", savings_account_id, customer_id, statement_cycle, correction_amount)
    amount = round(float(correction_amount), 2)
    ctx.create("savings_transactions", rid, savings_txn_id=rid, savings_account_id=savings_account_id,
               customer_id=customer_id, event_type="savings_interest_credit", amount=amount,
               posted_date=ctx.now()[:10], channel="none",
               description="Promotional interest correction", trace_number="", check_number="",
               fee_code="none", source_item_id="", statement_cycle=statement_cycle,
               adjustment_reason="bank_error", interest_component="promotional",
               counterparty_account_id="")
    credit_kinds = ("savings_deposit", "savings_interest_credit", "savings_fee_refund")
    balance = 0.0
    for row in ctx.find("savings_transactions", savings_account_id=savings_account_id):
        value = float(row.get("amount") or 0)
        balance += value if row.get("event_type") in credit_kinds else -value
    balance = round(balance, 2)
    ctx.update("savings_accounts", savings_account_id, current_balance=balance)
    return (f"Promotional interest entry {rid} posted for cycle {statement_cycle}: {amount:.2f} USD "
            f"credited; posted balance is now {balance:.2f} USD.")


@tool(owner="agent", rw="write")
def post_relationship_bonus_correction_5bb15040(ctx: ToolContext, savings_account_id: str,
                                                customer_id: str, statement_cycle: str,
                                                bonus_amount: float) -> str:
    """Credit a savings or money market account with relationship bonus interest a past statement cycle left unpaid.

    One call posts a single relationship bonus interest entry to the named account, marked as a
    bank error correction for the statement cycle given, and raises the account's posted balance by
    the credited amount immediately. The customer sees a new relationship bonus line dated today,
    carrying the corrected cycle, and a balance higher by that amount. The call has completed when
    the confirmation text carries the new entry's reference number and the credited amount.

    Args:
        savings_account_id: Id class — the reference number of the savings or money market account the relationship bonus is credited to, taken from the savings account lookup.
        customer_id: Id class — the customer reference number of the account owner, taken from the customer profile lookup.
        statement_cycle: Fixed-format class — the statement cycle the unpaid relationship bonus belongs to, written as YYYY-MM, the month in which that cycle closed; an empty value is not accepted.
        bonus_amount: Fixed-format class — the relationship bonus interest being credited, in USD, 2 decimal places, always positive; a value carrying more than 2 decimal places is stored rounded half up to the cent, and the bank's own Eastern Time posting date is used.

    Returns:
        A confirmation sentence containing the reference number of the relationship bonus entry
        just created, the credited amount in USD to two decimal places, the statement cycle it was
        booked against, and the account's new posted balance in USD to two decimal places. That
        sentence is what indicates the credit completed.
    """
    rid = ctx.make_id("srb_", savings_account_id, customer_id, statement_cycle, bonus_amount)
    amount = round(float(bonus_amount), 2)
    ctx.create("savings_transactions", rid, savings_txn_id=rid, savings_account_id=savings_account_id,
               customer_id=customer_id, event_type="savings_interest_credit", amount=amount,
               posted_date=ctx.now()[:10], channel="none",
               description="Relationship bonus interest correction", trace_number="", check_number="",
               fee_code="none", source_item_id="", statement_cycle=statement_cycle,
               adjustment_reason="bank_error", interest_component="relationship_bonus",
               counterparty_account_id="")
    credit_kinds = ("savings_deposit", "savings_interest_credit", "savings_fee_refund")
    balance = 0.0
    for row in ctx.find("savings_transactions", savings_account_id=savings_account_id):
        value = float(row.get("amount") or 0)
        balance += value if row.get("event_type") in credit_kinds else -value
    balance = round(balance, 2)
    ctx.update("savings_accounts", savings_account_id, current_balance=balance)
    return (f"Relationship bonus entry {rid} posted for cycle {statement_cycle}: {amount:.2f} USD "
            f"credited; posted balance is now {balance:.2f} USD.")


@tool(owner="agent", rw="write")
def credit_savings_courtesy_refund_0ed102a0(ctx: ToolContext, savings_account_id: str,
                                            customer_id: str, source_item_id: str,
                                            statement_cycle: str, refund_amount: float) -> str:
    """Put a courtesy credit for periodic savings fees back onto a savings or money market account.

    One call posts a single courtesy refund entry to the named account, booked against the fee
    entry whose reference number is given so that the fee it answers is identifiable, carrying the
    same fee code as that entry, and raises the account's posted balance by the credited amount
    straight away. The customer sees a courtesy credit line dated today and a higher balance. The
    call has completed when the confirmation text carries the new credit's reference number and the
    credited amount.

    Args:
        savings_account_id: Id class — the reference number of the savings or money market account receiving the courtesy credit, taken from the savings account lookup.
        customer_id: Id class — the customer reference number of the account owner, taken from the customer profile lookup.
        source_item_id: Id class — the reference number of the fee entry the courtesy credit is booked against, taken from the savings account activity lookup.
        statement_cycle: Fixed-format class — the statement cycle the courtesy credit itself posts in, written as YYYY-MM, the month in which that cycle closes; an empty value is not accepted.
        refund_amount: Fixed-format class — the courtesy credit being posted, in USD, 2 decimal places, always positive; a value carrying more than 2 decimal places is stored rounded half up to the cent, and the bank's own Eastern Time posting date is used.

    Returns:
        A confirmation sentence containing the reference number of the courtesy credit just
        created, the credited amount in USD to two decimal places, the reference number of the fee
        entry it is booked against, and the account's new posted balance in USD to two decimal
        places. That sentence is what indicates the credit completed.
    """
    rid = ctx.make_id("scr_", savings_account_id, source_item_id, statement_cycle, refund_amount)
    amount = round(float(refund_amount), 2)
    matched = ctx.find("savings_transactions", savings_txn_id=source_item_id)
    code = matched[0].get("fee_code") if matched else "none"
    ctx.create("savings_transactions", rid, savings_txn_id=rid, savings_account_id=savings_account_id,
               customer_id=customer_id, event_type="savings_fee_refund", amount=amount,
               posted_date=ctx.now()[:10], channel="none",
               description="Courtesy credit for periodic account fees", trace_number="",
               check_number="", fee_code=code, source_item_id=source_item_id,
               statement_cycle=statement_cycle, adjustment_reason="courtesy_waiver",
               interest_component="none", counterparty_account_id="")
    credit_kinds = ("savings_deposit", "savings_interest_credit", "savings_fee_refund")
    balance = 0.0
    for row in ctx.find("savings_transactions", savings_account_id=savings_account_id):
        value = float(row.get("amount") or 0)
        balance += value if row.get("event_type") in credit_kinds else -value
    balance = round(balance, 2)
    ctx.update("savings_accounts", savings_account_id, current_balance=balance)
    return (f"Courtesy credit {rid} posted against fee entry {source_item_id}: {amount:.2f} USD "
            f"credited; posted balance is now {balance:.2f} USD.")


@tool(owner="user", rw="write")
def set_savings_standing_transfer_55216172(ctx: ToolContext, savings_account_id: str,
                                           funding_checking_account_id: str,
                                           transfer_amount: float, transfer_day: int) -> str:
    """Put a recurring monthly transfer from a Piedmont Crescent Bank checking account into a savings or money market account on record, as the owner's own instruction.

    One call writes the standing instruction onto the named savings or money market account: the
    recurring amount, the day of the month it runs, and the checking account it is drawn from all
    replace whatever stood there before, and the instruction takes effect from the next scheduled
    run. The owner can see the amount, the day and the funding account on the savings account from
    that moment. The call has completed when the confirmation text repeats the recurring amount,
    the day of the month and the funding account.

    Args:
        savings_account_id: Id class — the reference number of the savings or money market account the money is transferred into, taken from the savings account lookup.
        funding_checking_account_id: Id class — the reference number of the Piedmont Crescent Bank checking account the recurring transfer is drawn from, taken from the checking account lookup.
        transfer_amount: Fixed-format class — the recurring monthly amount, in USD, 2 decimal places; a value carrying more than 2 decimal places is stored rounded half up to the cent, and 0.00 is the value that stops the instruction.
        transfer_day: Fixed-format class — the day of the month the transfer runs, given as integer 1-28, or empty string when none is being set; days 29 to 31 are not accepted because they do not occur in every month.

    Returns:
        A confirmation sentence containing the savings account's reference number, the recurring
        amount in USD to two decimal places, the day of the month the transfer runs, and the
        reference number of the funding checking account. That sentence is what indicates the
        standing instruction is on record.
    """
    amount = round(float(transfer_amount), 2)
    ctx.update("savings_accounts", savings_account_id,
               automatic_transfer_amount=amount, automatic_transfer_day=transfer_day,
               funding_checking_account_id=funding_checking_account_id)
    return (f"Standing monthly transfer recorded on savings account {savings_account_id}: "
            f"{amount:.2f} USD on day {transfer_day} of each month, drawn from checking account "
            f"{funding_checking_account_id}.")


@tool(owner="agent", rw="write")
def credit_savings_fee_review_ce0a6323(ctx: ToolContext, savings_account_id: str, customer_id: str,
                                       source_item_id: str, statement_cycle: str,
                                       review_credit_amount: float) -> str:
    """Put back onto a savings or money market account the excess withdrawal fees a fee review found were charged against withdrawals that never counted toward the allowance.

    One call posts a single bank error credit to the named account, booked against the fee entry whose
    reference number is given and carrying the same fee code as that entry, and raises the account's
    posted balance by the credited amount at once. The customer sees a bank error credit line dated
    today against that fee and a balance higher by that amount. The call has completed when the
    confirmation text carries the new credit's reference number and the credited amount.

    Args:
        savings_account_id: Id class — the reference number of the savings or money market account receiving the review credit, taken from the savings account lookup.
        customer_id: Id class — the customer reference number of the account owner, taken from the customer profile lookup.
        source_item_id: Id class — the reference number of the fee entry the review credit is booked against, taken from the savings account activity lookup.
        statement_cycle: Fixed-format class — the statement cycle the review credit itself posts in, written as YYYY-MM, the month in which that cycle closes; an empty value is not accepted.
        review_credit_amount: Fixed-format class — the review credit being posted, in USD, 2 decimal places, always positive; a value carrying more than 2 decimal places is stored rounded half up to the cent, and the bank's own Eastern Time posting date is used.

    Returns:
        A confirmation sentence containing the reference number of the review credit just created, the
        credited amount in USD to two decimal places, the reference number of the fee entry it is
        booked against, and the account's new posted balance in USD to two decimal places. That
        sentence is what indicates the credit completed.
    """
    rid = ctx.make_id("sfr_", savings_account_id, source_item_id, statement_cycle, review_credit_amount)
    amount = round(float(review_credit_amount), 2)
    matched = ctx.find("savings_transactions", savings_txn_id=source_item_id)
    code = matched[0].get("fee_code") if matched else "none"
    ctx.create("savings_transactions", rid, savings_txn_id=rid, savings_account_id=savings_account_id,
               customer_id=customer_id, event_type="savings_fee_refund", amount=amount,
               posted_date=ctx.now()[:10], channel="none",
               description="Excess withdrawal fee review credit", trace_number="", check_number="",
               fee_code=code, source_item_id=source_item_id, statement_cycle=statement_cycle,
               adjustment_reason="bank_error", interest_component="none", counterparty_account_id="")
    credit_kinds = ("savings_deposit", "savings_interest_credit", "savings_fee_refund")
    balance = 0.0
    for row in ctx.find("savings_transactions", savings_account_id=savings_account_id):
        value = float(row.get("amount") or 0)
        balance += value if row.get("event_type") in credit_kinds else -value
    balance = round(balance, 2)
    ctx.update("savings_accounts", savings_account_id, current_balance=balance)
    return (f"Fee review credit {rid} posted against fee entry {source_item_id}: {amount:.2f} USD "
            f"credited; posted balance is now {balance:.2f} USD.")


@tool(owner="user", rw="write")
def transfer_savings_surplus_c4c79a83(ctx: ToolContext, savings_account_id: str, customer_id: str,
                                      destination_account_id: str, transfer_amount: float) -> str:
    """Move money out of a savings or money market account into another Piedmont Crescent Bank account by online transfer, as the owner's own instruction.

    One call posts a single online transfer out of the named savings or money market account to the
    receiving account given, lowers the savings account's posted balance by the amount moved and shows
    the receiving account as the other side of the entry. The owner sees the transfer on the savings
    account with today's posting date and a balance lower by that amount, and the money in the
    receiving account. The call has completed when the confirmation text carries the new entry's
    reference number, the amount moved and the receiving account.

    Args:
        savings_account_id: Id class — the reference number of the savings or money market account the money is moved out of, taken from the savings account lookup.
        customer_id: Id class — the customer reference number of the account owner, taken from the customer profile lookup.
        destination_account_id: Id class — the reference number of the Piedmont Crescent Bank account receiving the money, taken from the checking account lookup.
        transfer_amount: Fixed-format class — the amount moved out, in USD, 2 decimal places, always positive; a value carrying more than 2 decimal places is stored rounded half up to the cent, and the bank's own Eastern Time posting date is used.

    Returns:
        A confirmation sentence containing the reference number of the transfer entry just created, the
        amount moved in USD to two decimal places, the reference number of the receiving account, and
        the savings account's new posted balance in USD to two decimal places. That sentence is what
        indicates the transfer completed.
    """
    rid = ctx.make_id("sot_", savings_account_id, destination_account_id, transfer_amount)
    amount = round(float(transfer_amount), 2)
    ctx.create("savings_transactions", rid, savings_txn_id=rid, savings_account_id=savings_account_id,
               customer_id=customer_id, event_type="savings_withdrawal", amount=amount,
               posted_date=ctx.now()[:10], channel="online_transfer",
               description="Online transfer to PCB checking", trace_number="", check_number="",
               fee_code="none", source_item_id="", statement_cycle=ctx.now()[:7],
               adjustment_reason="none", interest_component="none",
               counterparty_account_id=destination_account_id)
    credit_kinds = ("savings_deposit", "savings_interest_credit", "savings_fee_refund")
    balance = 0.0
    for row in ctx.find("savings_transactions", savings_account_id=savings_account_id):
        value = float(row.get("amount") or 0)
        balance += value if row.get("event_type") in credit_kinds else -value
    balance = round(balance, 2)
    ctx.update("savings_accounts", savings_account_id, current_balance=balance)
    return (f"Online transfer {rid} posted: {amount:.2f} USD moved to account {destination_account_id}; "
            f"posted balance is now {balance:.2f} USD.")

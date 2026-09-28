"""Hidden task tools of the move_out_deposit_accounting difficulty (Security Deposit Account).

Each tool performs one atomic write on the deposit ledger with the values the caller passes; none of them looks
up history, computes an amount or judges whether the write is due. They are reached through the paired
unlock_* -> call_* meta-tools, and each is named by exactly one extended policy's target_tool.
"""

from erlbench import ToolContext, tool


@tool(owner="agent", rw="write")
def post_cleaning_correction_credit_249da733(ctx: ToolContext, deposit_account_id: str, source_transaction_id: str,
                                             amount: float) -> str:
    """Post one dispute credit on a security deposit account that lowers its balance owed on account of a disputed
    cleaning line that was corrected. One call records one new dispute-credit line on the account's final account statement,
    tied to the single itemized cleaning line named as its source and dated today; the amount credited reduces
    what the former resident still owes. Nothing else on the account changes. The credit line becomes visible at
    once in the account's transactions, and the receipt below confirms it.

    Args:
        deposit_account_id: Id class — the reference number of the security deposit account that receives the
            credit, as returned by the deposit account lookup for this resident.
        source_transaction_id: Id class — the reference number of the itemized cleaning line the credit is
            posted against, as returned by the deposit transaction lookup for this account.
        amount: Fixed-format class — the credit amount in USD, a positive number with 2 decimal places, rounded
            half up to the cent before it is passed.

    Returns:
        A one-line text receipt that starts with "Dispute credit posted", followed by the new credit line's
        reference number, the deposit account reference number, the source cleaning line reference number, the
        amount credited in USD with 2 decimal places and the posting date in YYYY-MM-DD form. That receipt means the
        credit was recorded.
    """
    rid = ctx.make_id("dcr_", deposit_account_id, source_transaction_id, amount)
    today = ctx.now()[:10]
    account = ctx.find("deposit_accounts", deposit_account_id=deposit_account_id)
    ctx.create("deposit_transactions", rid, transaction_id=rid, deposit_account_id=deposit_account_id,
               customer_id=account[0].get("customer_id") if account else None, event_type="deposit_balance_credit",
               line_category="dispute_credit", item_location="not_applicable", transaction_date=today,
               amount=round(float(amount), 2), item_age_months=0, replacement_cost=0.0, labor_hours=0.0,
               quantity=0, inspection_photo_on_file=False, source_transaction_id=source_transaction_id,
               payment_method="not_applicable", payment_reference="")
    return (f"Dispute credit posted: credit line {rid} on deposit account {deposit_account_id} against cleaning "
            f"line {source_transaction_id}, amount {round(float(amount), 2):.2f} USD, posted {today}.")


@tool(owner="user", rw="write")
def pay_settlement_balance_cadbabf4(ctx: ToolContext, deposit_account_id: str, amount: float,
                                    payment_method: str) -> str:
    """The former resident pays a settlement payment toward the balance owed on their own security deposit
    account through the resident portal. One call records one payment received on the account, dated today, in
    the amount and by the instrument the resident chooses, and issues a portal confirmation number; the payment
    lowers the balance owed by the amount paid. Nothing else on the account changes. The resident sees the
    confirmation number at once, and the payment line appears in the account's transactions.

    Args:
        deposit_account_id: Id class — the reference number of the resident's security deposit account, as read
            to the resident by the resident services agent from the deposit account lookup.
        amount: Fixed-format class — the payment amount in USD, a positive number with 2 decimal places, rounded
            half up to the cent before it is paid.
        payment_method: Enum class — the instrument the resident pays with, one of: ach_one_time — a one-time bank
            debit the resident authorises in the portal; debit_card — a debit card the resident enters in the
            portal; credit_card — a credit card the resident enters in the portal; money_order — a money order
            the resident hands in at the leasing office; cashiers_check — a cashier's check the resident hands in
            at the leasing office; ach_direct_deposit — not a paying instrument, used only for refunds paid out to
            the resident; paper_check — not a paying instrument, used only for refunds mailed to the resident;
            not_applicable — used only on lines that carry no instrument, never for a payment.

    Returns:
        A one-line text receipt that starts with "Payment received", followed by the new payment line's
        reference number, the portal confirmation number (LRT- followed by eight upper-case letters and digits),
        the deposit account reference number, the amount paid in USD with 2 decimal places, the instrument and the
        payment date in YYYY-MM-DD form. That receipt means the payment was recorded.
    """
    rid = ctx.make_id("dpy_", deposit_account_id, amount, payment_method)
    confirmation = "LRT-" + rid[-8:].upper()
    today = ctx.now()[:10]
    account = ctx.find("deposit_accounts", deposit_account_id=deposit_account_id)
    ctx.create("deposit_transactions", rid, transaction_id=rid, deposit_account_id=deposit_account_id,
               customer_id=account[0].get("customer_id") if account else None, event_type="deposit_balance_payment",
               line_category="balance_payment", item_location="not_applicable", transaction_date=today,
               amount=round(float(amount), 2), item_age_months=0, replacement_cost=0.0, labor_hours=0.0,
               quantity=0, inspection_photo_on_file=False, source_transaction_id=None,
               payment_method=payment_method, payment_reference=confirmation)
    return (f"Payment received: payment line {rid}, confirmation {confirmation}, deposit account "
            f"{deposit_account_id}, amount {round(float(amount), 2):.2f} USD by {payment_method}, "
            f"paid {today}.")


@tool(owner="agent", rw="write")
def post_depreciation_correction_credit_f675d6ed(ctx: ToolContext, deposit_account_id: str,
                                                 source_transaction_id: str, amount: float) -> str:
    """Post one dispute credit on a security deposit account that lowers its balance owed on account of a disputed
    carpet replacement line that was re-depreciated. One call records one new dispute-credit line on the account's final
    account statement, tied to the single itemized carpet replacement line named as its source and dated today;
    the amount credited reduces what the former resident still owes. Nothing else on the account changes. The
    credit line becomes visible at once in the account's transactions, and the receipt below confirms it.

    Args:
        deposit_account_id: Id class — the reference number of the security deposit account that receives the
            credit, as returned by the deposit account lookup for this resident.
        source_transaction_id: Id class — the reference number of the itemized carpet replacement line the credit
            is posted against, as returned by the deposit transaction lookup for this account.
        amount: Fixed-format class — the credit amount in USD, a positive number with 2 decimal places, rounded
            half up to the cent before it is passed.

    Returns:
        A one-line text receipt that starts with "Dispute credit posted", followed by the new credit line's
        reference number, the deposit account reference number, the source carpet line reference number, the
        amount credited in USD with 2 decimal places and the posting date in YYYY-MM-DD form. That receipt means the
        credit was recorded.
    """
    rid = ctx.make_id("dcp_", deposit_account_id, source_transaction_id, amount)
    today = ctx.now()[:10]
    account = ctx.find("deposit_accounts", deposit_account_id=deposit_account_id)
    ctx.create("deposit_transactions", rid, transaction_id=rid, deposit_account_id=deposit_account_id,
               customer_id=account[0].get("customer_id") if account else None, event_type="deposit_balance_credit",
               line_category="dispute_credit", item_location="not_applicable", transaction_date=today,
               amount=round(float(amount), 2), item_age_months=0, replacement_cost=0.0, labor_hours=0.0,
               quantity=0, inspection_photo_on_file=False, source_transaction_id=source_transaction_id,
               payment_method="not_applicable", payment_reference="")
    return (f"Dispute credit posted: credit line {rid} on deposit account {deposit_account_id} against carpet "
            f"line {source_transaction_id}, amount {round(float(amount), 2):.2f} USD, posted {today}.")


@tool(owner="agent", rw="write")
def post_repair_labor_credit_05a989cb(ctx: ToolContext, deposit_account_id: str, source_transaction_id: str,
                                      amount: float) -> str:
    """Post one dispute credit on a security deposit account that lowers its balance owed on account of a disputed
    damage repair line that was re-priced. One call records one new dispute-credit line on the account's final account
    statement, tied to the single itemized damage repair line named as its source and dated today; the amount
    credited reduces what the former resident still owes. Nothing else on the account changes. The credit line
    becomes visible at once in the account's transactions, and the receipt below confirms it.

    Args:
        deposit_account_id: Id class — the reference number of the security deposit account that receives the
            credit, as returned by the deposit account lookup for this resident.
        source_transaction_id: Id class — the reference number of the itemized damage repair line the credit is
            posted against, as returned by the deposit transaction lookup for this account.
        amount: Fixed-format class — the credit amount in USD, a positive number with 2 decimal places, rounded
            half up to the cent before it is passed.

    Returns:
        A one-line text receipt that starts with "Dispute credit posted", followed by the new credit line's
        reference number, the deposit account reference number, the source repair line reference number, the
        amount credited in USD with 2 decimal places and the posting date in YYYY-MM-DD form. That receipt means the
        credit was recorded.
    """
    rid = ctx.make_id("dlr_", deposit_account_id, source_transaction_id, amount)
    today = ctx.now()[:10]
    account = ctx.find("deposit_accounts", deposit_account_id=deposit_account_id)
    ctx.create("deposit_transactions", rid, transaction_id=rid, deposit_account_id=deposit_account_id,
               customer_id=account[0].get("customer_id") if account else None, event_type="deposit_balance_credit",
               line_category="dispute_credit", item_location="not_applicable", transaction_date=today,
               amount=round(float(amount), 2), item_age_months=0, replacement_cost=0.0, labor_hours=0.0,
               quantity=0, inspection_photo_on_file=False, source_transaction_id=source_transaction_id,
               payment_method="not_applicable", payment_reference="")
    return (f"Dispute credit posted: credit line {rid} on deposit account {deposit_account_id} against repair "
            f"line {source_transaction_id}, amount {round(float(amount), 2):.2f} USD, posted {today}.")


@tool(owner="agent", rw="write")
def post_fob_count_credit_b88884f4(ctx: ToolContext, deposit_account_id: str, source_transaction_id: str,
                                   amount: float) -> str:
    """Post one dispute credit on a security deposit account that lowers its balance owed on account of a disputed
    unreturned-fob line that was recounted. One call records one new dispute-credit line on the account's final account
    statement, tied to the single itemized unreturned-fob line named as its source and dated today; the amount
    credited reduces what the former resident still owes. Nothing else on the account changes. The credit line
    becomes visible at once in the account's transactions, and the receipt below confirms it.

    Args:
        deposit_account_id: Id class — the reference number of the security deposit account that receives the
            credit, as returned by the deposit account lookup for this resident.
        source_transaction_id: Id class — the reference number of the itemized unreturned-fob line the credit is
            posted against, as returned by the deposit transaction lookup for this account.
        amount: Fixed-format class — the credit amount in USD, a positive number with 2 decimal places, rounded
            half up to the cent before it is passed.

    Returns:
        A one-line text receipt that starts with "Dispute credit posted", followed by the new credit line's
        reference number, the deposit account reference number, the source fob line reference number, the amount
        credited in USD with 2 decimal places and the posting date in YYYY-MM-DD form. That receipt means the credit
        was recorded.
    """
    rid = ctx.make_id("dfb_", deposit_account_id, source_transaction_id, amount)
    today = ctx.now()[:10]
    account = ctx.find("deposit_accounts", deposit_account_id=deposit_account_id)
    ctx.create("deposit_transactions", rid, transaction_id=rid, deposit_account_id=deposit_account_id,
               customer_id=account[0].get("customer_id") if account else None, event_type="deposit_balance_credit",
               line_category="dispute_credit", item_location="not_applicable", transaction_date=today,
               amount=round(float(amount), 2), item_age_months=0, replacement_cost=0.0, labor_hours=0.0,
               quantity=0, inspection_photo_on_file=False, source_transaction_id=source_transaction_id,
               payment_method="not_applicable", payment_reference="")
    return (f"Dispute credit posted: credit line {rid} on deposit account {deposit_account_id} against fob "
            f"line {source_transaction_id}, amount {round(float(amount), 2):.2f} USD, posted {today}.")


@tool(owner="user", rw="write")
def pay_guarantee_gap_4e6273ca(ctx: ToolContext, deposit_account_id: str, amount: float,
                               payment_method: str) -> str:
    """The former resident of a Zero-Deposit Guarantee Plan account pays, through the resident portal, the part of
    the balance owed on their own security deposit account that the deposit guarantee will not cover. One call
    records one payment received on the account, dated today, in the amount and by the instrument the resident
    chooses, and issues a portal confirmation number; the payment lowers the balance owed by the amount paid.
    Nothing else on the account changes. The resident sees the confirmation number at once, and the payment line
    appears in the account's transactions.

    Args:
        deposit_account_id: Id class — the reference number of the resident's security deposit account, as read
            to the resident by the resident services agent from the deposit account lookup.
        amount: Fixed-format class — the payment amount in USD, a positive number with 2 decimal places, rounded
            half up to the cent before it is paid.
        payment_method: Enum class — the instrument the resident pays with, one of: ach_one_time — a one-time bank
            debit the resident authorises in the portal; debit_card — a debit card the resident enters in the
            portal; credit_card — a credit card the resident enters in the portal; money_order — a money order
            the resident hands in at the leasing office; cashiers_check — a cashier's check the resident hands in
            at the leasing office; ach_direct_deposit — not a paying instrument, used only for refunds paid out to
            the resident; paper_check — not a paying instrument, used only for refunds mailed to the resident;
            not_applicable — used only on lines that carry no instrument, never for a payment.

    Returns:
        A one-line text receipt that starts with "Payment received", followed by the new payment line's
        reference number, the portal confirmation number (LRT- followed by eight upper-case letters and digits),
        the deposit account reference number, the amount paid in USD with 2 decimal places, the instrument and the
        payment date in YYYY-MM-DD form. That receipt means the payment was recorded.
    """
    rid = ctx.make_id("dgp_", deposit_account_id, amount, payment_method)
    confirmation = "LRT-" + rid[-8:].upper()
    today = ctx.now()[:10]
    account = ctx.find("deposit_accounts", deposit_account_id=deposit_account_id)
    ctx.create("deposit_transactions", rid, transaction_id=rid, deposit_account_id=deposit_account_id,
               customer_id=account[0].get("customer_id") if account else None, event_type="deposit_balance_payment",
               line_category="balance_payment", item_location="not_applicable", transaction_date=today,
               amount=round(float(amount), 2), item_age_months=0, replacement_cost=0.0, labor_hours=0.0,
               quantity=0, inspection_photo_on_file=False, source_transaction_id=None,
               payment_method=payment_method, payment_reference=confirmation)
    return (f"Payment received: payment line {rid}, confirmation {confirmation}, deposit account "
            f"{deposit_account_id}, amount {round(float(amount), 2):.2f} USD by {payment_method}, "
            f"paid {today}.")

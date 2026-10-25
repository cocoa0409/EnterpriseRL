"""Hidden task tools for meal_account_and_benefits (Calloway Creek ISD School Nutrition meal accounts).

Every tool makes one atomic write on School Nutrition meal accounts and is reached through the
unlock_* -> call_* meta tools. No tool checks an eligibility, a status or a prerequisite: those are
judged before the call from the published policies and the records.
"""

from decimal import Decimal, ROUND_HALF_UP

from erlbench import ToolContext, tool


class _MealMoney:
    """Exact money handling shared by the tools below (not a tool)."""

    @staticmethod
    def cents(value) -> float:
        """Round a dollar amount half up to the cent, exactly."""
        return float(Decimal(str(value)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP))

    @staticmethod
    def is_cent_amount(value) -> bool:
        """True when the amount is positive and carries no more than two decimal places."""
        d = Decimal(str(value))
        return d > 0 and d == d.quantize(Decimal("0.01"))

    @staticmethod
    def reference(digest: str) -> str:
        """An eight-digit confirmation number beginning with 72, derived from a row id."""
        return "72" + str(int(digest[-10:], 16) % 1000000).zfill(6)

    @staticmethod
    def account(ctx: ToolContext, meal_account_id: str):
        """The meal account record for a reference number, or None."""
        rows = ctx.find("meal_accounts", meal_account_id=meal_account_id)
        return rows[0] if rows else None

    @staticmethod
    def transfer_rows(ctx: ToolContext, prefix: str, giving_meal_account_id: str,
                      meal_account_id: str, amount: float):
        """Prepare one sibling transfer: (error or None, [(row id, fields)...], confirmation text)."""
        if not _MealMoney.is_cent_amount(amount):
            return "Error: amount must be a positive dollar amount with at most two decimal places.", [], ""
        giving = _MealMoney.account(ctx, giving_meal_account_id)
        receiving = _MealMoney.account(ctx, meal_account_id)
        if giving is None or receiving is None:
            return "Error: both meal account reference numbers must exist.", [], ""
        amt = _MealMoney.cents(amount)
        day = ctx.now()[:10]
        out_id = ctx.make_id(prefix + "out_", giving_meal_account_id, meal_account_id, amt)
        in_id = ctx.make_id(prefix + "in_", giving_meal_account_id, meal_account_id, amt)
        common = dict(amount=amt, transaction_date=day, meal_type="not_applicable",
                      price_basis="not_applicable", pos_receipt_number="", deposit_method="not_applicable",
                      deposit_reference="", source_meal_transaction_id="", void_reason="not_applicable",
                      refund_reason="not_applicable")
        rows = [(out_id, dict(meal_transaction_id=out_id, meal_account_id=giving_meal_account_id,
                              customer_id=giving.get("customer_id"), counterpart_meal_account_id=meal_account_id,
                              event_type="meals_transfer_out", **common)),
                (in_id, dict(meal_transaction_id=in_id, meal_account_id=meal_account_id,
                             customer_id=receiving.get("customer_id"), counterpart_meal_account_id=giving_meal_account_id,
                             event_type="meals_transfer_in", **common))]
        msg = (f"Sibling transfer posted: {amt:.2f} USD moved from meal account {giving_meal_account_id} "
               f"(record {out_id}) to meal account {meal_account_id} (record {in_id}), dated {day}.")
        return None, rows, msg


@tool(owner="user", rw="write")
def deposit_meal_prepayment_ffe018a7(ctx: ToolContext, meal_account_id: str, amount: float) -> str:
    """The parent or guardian makes an online card prepayment, personally, through the district's online
    payment portal, onto a student's active cafeteria meal account. One call posts one deposit to that
    account: the amount is credited to the account balance (any unpaid meal charges are cleared first
    because the deposit simply raises the balance), the deposit is recorded as an online card deposit
    dated today, and the portal issues a confirmation number the parent can quote. The payment
    processor's convenience fee is paid on top by the parent and is never posted to the account.

    Args:
        meal_account_id: Id class — the meal account reference number of the student whose account
            receives the prepayment, as returned by the meal account lookup for that student.
        amount: Fixed-format class — the prepayment credited to the account, in US dollars, a positive
            number with 2 decimal places (cents), already rounded half up to the cent; it
            excludes the processor's convenience fee.

    Returns:
        A confirmation sentence carrying four fields: the deposit record reference (text identifier of
        the new account transaction), the meal account reference credited, the amount credited in US
        dollars with two decimals, and the portal confirmation number (eight digits beginning with 72).
        The presence of the confirmation number means the deposit posted; a message beginning with
        "Error:" means nothing was posted.
    """
    if not _MealMoney.is_cent_amount(amount):
        return "Error: amount must be a positive dollar amount with at most two decimal places."
    acct = _MealMoney.account(ctx, meal_account_id)
    if acct is None:
        return f"Error: no meal account {meal_account_id}."
    amt = _MealMoney.cents(amount)
    rid = ctx.make_id("mtx_pre_", meal_account_id, amt)
    ref = _MealMoney.reference(rid)
    ctx.create("meal_transactions", rid, meal_transaction_id=rid, meal_account_id=meal_account_id,
               customer_id=acct.get("customer_id"), event_type="meals_deposit", amount=amt,
               transaction_date=ctx.now()[:10], meal_type="not_applicable", price_basis="not_applicable",
               pos_receipt_number="", deposit_method="online_card", deposit_reference=ref,
               source_meal_transaction_id="", void_reason="not_applicable", refund_reason="not_applicable",
               counterpart_meal_account_id="")
    return (f"Online prepayment posted: deposit record {rid}, meal account {meal_account_id}, "
            f"amount {amt:.2f} USD, portal confirmation number {ref}.")


@tool(owner="user", rw="write")
def pay_inactive_meal_installment_c0dba3e7(ctx: ToolContext, meal_account_id: str, amount: float) -> str:
    """The parent or guardian makes a repayment-plan payment, personally, by card through the district's
    online payment portal, toward the unpaid meal charges on an inactive cafeteria meal account of a
    student who has left the district. One call posts one payment to that account: the amount is
    credited to the account balance and reduces the unpaid meal charges by the same amount, the payment
    is recorded as an online card deposit dated today, and the portal issues a confirmation number.
    No fee, interest or penalty is added, and the processor's convenience fee is never posted.

    Args:
        meal_account_id: Id class — the meal account reference number of the departed student whose
            unpaid meal charges are being repaid, as returned by the meal account lookup for the household.
        amount: Fixed-format class — the repayment payment credited to the account, in US dollars, a
            positive number with 2 decimal places (cents), already rounded half up to the cent.

    Returns:
        A confirmation sentence carrying four fields: the payment record reference (text identifier of
        the new account transaction), the meal account reference credited, the amount credited in US
        dollars with two decimals, and the portal confirmation number (eight digits beginning with 72).
        The presence of the confirmation number means the payment posted; a message beginning with
        "Error:" means nothing was posted.
    """
    if not _MealMoney.is_cent_amount(amount):
        return "Error: amount must be a positive dollar amount with at most two decimal places."
    acct = _MealMoney.account(ctx, meal_account_id)
    if acct is None:
        return f"Error: no meal account {meal_account_id}."
    amt = _MealMoney.cents(amount)
    rid = ctx.make_id("mtx_plan_", meal_account_id, amt)
    ref = _MealMoney.reference(rid)
    ctx.create("meal_transactions", rid, meal_transaction_id=rid, meal_account_id=meal_account_id,
               customer_id=acct.get("customer_id"), event_type="meals_deposit", amount=amt,
               transaction_date=ctx.now()[:10], meal_type="not_applicable", price_basis="not_applicable",
               pos_receipt_number="", deposit_method="online_card", deposit_reference=ref,
               source_meal_transaction_id="", void_reason="not_applicable", refund_reason="not_applicable",
               counterpart_meal_account_id="")
    return (f"Repayment payment posted: payment record {rid}, meal account {meal_account_id}, "
            f"amount {amt:.2f} USD, portal confirmation number {ref}.")


@tool(owner="agent", rw="write")
def transfer_departed_charge_cover_80639818(ctx: ToolContext, giving_meal_account_id: str,
                                            meal_account_id: str, amount: float) -> str:
    """School Nutrition moves money from the inactive meal account of a student who has left the district
    to a sibling's active meal account in the same household, to clear that sibling's unpaid meal
    charges and pay for the sibling's coming meals. One call posts one sibling transfer: the amount leaves the giving
    account's balance as a transfer out and is credited to the receiving account's balance as a transfer
    in, both dated today and each naming the other account.

    Args:
        giving_meal_account_id: Id class — the meal account reference number of the departed student's
            inactive account the money comes from, as returned by the meal account lookup for the household.
        meal_account_id: Id class — the meal account reference number of the sibling's active
            account that receives the money, as returned by the meal account lookup for the household.
        amount: Fixed-format class — the amount moved, in US dollars, a positive number with 2
            decimal places (cents), already rounded half up to the cent.

    Returns:
        A confirmation sentence carrying five fields: the amount moved in US dollars with two decimals,
        the giving meal account reference, the transfer-out record reference, the receiving meal account
        reference and the transfer-in record reference, plus the posting date (YYYY-MM-DD). The presence of
        both record references means the transfer posted; a message beginning with "Error:" means nothing
        was posted.
    """
    err, rows, msg = _MealMoney.transfer_rows(ctx, "mtx_cov_", giving_meal_account_id, meal_account_id, amount)
    if err:
        return err
    for row_id, fields in rows:
        ctx.create("meal_transactions", row_id, **fields)
    return msg


@tool(owner="agent", rw="write")
def transfer_idle_sibling_balance_b810dc58(ctx: ToolContext, giving_meal_account_id: str,
                                           meal_account_id: str, amount: float) -> str:
    """School Nutrition moves the idle part of an active student's meal account balance to a sibling's
    active meal account in the same household. One call posts one
    sibling transfer: the amount leaves the giving account's balance as a transfer out and is credited
    to the receiving account's balance as a transfer in, both dated today and each naming the other
    account.

    Args:
        giving_meal_account_id: Id class — the meal account reference number of the active account whose
            idle balance is moved, as returned by the meal account lookup for the household.
        meal_account_id: Id class — the meal account reference number of the sibling's active
            account that receives the money, as returned by the meal account lookup for the household.
        amount: Fixed-format class — the amount moved, in US dollars, a positive number with 2
            decimal places (cents), already rounded half up to the cent.

    Returns:
        A confirmation sentence carrying five fields: the amount moved in US dollars with two decimals,
        the giving meal account reference, the transfer-out record reference, the receiving meal account
        reference and the transfer-in record reference, plus the posting date (YYYY-MM-DD). The presence of
        both record references means the transfer posted; a message beginning with "Error:" means nothing
        was posted.
    """
    err, rows, msg = _MealMoney.transfer_rows(ctx, "mtx_net_", giving_meal_account_id, meal_account_id, amount)
    if err:
        return err
    for row_id, fields in rows:
        ctx.create("meal_transactions", row_id, **fields)
    return msg


@tool(owner="agent", rw="write")
def refund_cep_meal_balance_19cb6a0f(ctx: ToolContext, meal_account_id: str, amount: float) -> str:
    """School Nutrition refunds, by district check mailed to the household, part or all of the balance on
    a student's active cafeteria meal account at a campus that serves reimbursable meals at no charge,
    on the household's request. One call posts one refund: the amount leaves the account balance as a
    refund dated today with the reason household request, and the rest of the balance stays on the
    account; the household receives the check by mail.

    Args:
        meal_account_id: Id class — the meal account reference number of the student whose balance is
            refunded, as returned by the meal account lookup for the household.
        amount: Fixed-format class — the refund paid by check, in US dollars, a positive number with 2
            decimal places (cents), already rounded half up to the cent.

    Returns:
        A confirmation sentence carrying four fields: the refund record reference (text identifier of the
        new account transaction), the meal account reference refunded, the refund amount in US dollars
        with two decimals and the refund date (YYYY-MM-DD). The presence of the refund record reference
        means the refund posted; a message beginning with "Error:" means nothing was posted.
    """
    if not _MealMoney.is_cent_amount(amount):
        return "Error: amount must be a positive dollar amount with at most two decimal places."
    acct = _MealMoney.account(ctx, meal_account_id)
    if acct is None:
        return f"Error: no meal account {meal_account_id}."
    amt = _MealMoney.cents(amount)
    day = ctx.now()[:10]
    rid = ctx.make_id("mtx_ref_", meal_account_id, amt)
    ctx.create("meal_transactions", rid, meal_transaction_id=rid, meal_account_id=meal_account_id,
               customer_id=acct.get("customer_id"), event_type="meals_refund", amount=amt,
               transaction_date=day, meal_type="not_applicable", price_basis="not_applicable",
               pos_receipt_number="", deposit_method="not_applicable", deposit_reference="",
               source_meal_transaction_id="", void_reason="not_applicable", refund_reason="household_request",
               counterpart_meal_account_id="")
    return (f"Refund posted: refund record {rid}, meal account {meal_account_id}, amount {amt:.2f} USD, "
            f"refund date {day}; the check is mailed to the household.")


@tool(owner="user", rw="write")
def pay_collection_meal_installment_be0f7285(ctx: ToolContext, meal_account_id: str, amount: float) -> str:
    """The parent or guardian makes a repayment-plan payment, personally, by card through the district's
    online payment portal, toward the unpaid meal charges on a student's active cafeteria meal account
    under the district's repayment plan for active accounts. One call posts one payment to that account:
    the amount is credited to the account balance and reduces its unpaid meal charges by the same amount, the payment is recorded as an online card
    deposit dated today, and the portal issues a confirmation number. No fee, interest or penalty is
    added, and the processor's convenience fee is never posted.

    Args:
        meal_account_id: Id class — the meal account reference number of the student whose unpaid
            meal charges are being repaid, as returned by the meal account lookup for the household.
        amount: Fixed-format class — the repayment payment credited to the account, in US dollars, a
            positive number with 2 decimal places (cents), already rounded half up to the cent.

    Returns:
        A confirmation sentence carrying four fields: the payment record reference (text identifier of
        the new account transaction), the meal account reference credited, the amount credited in US
        dollars with two decimals, and the portal confirmation number (eight digits beginning with 72).
        The presence of the confirmation number means the payment posted; a message beginning with
        "Error:" means nothing was posted.
    """
    if not _MealMoney.is_cent_amount(amount):
        return "Error: amount must be a positive dollar amount with at most two decimal places."
    acct = _MealMoney.account(ctx, meal_account_id)
    if acct is None:
        return f"Error: no meal account {meal_account_id}."
    amt = _MealMoney.cents(amount)
    rid = ctx.make_id("mtx_col_", meal_account_id, amt)
    ref = _MealMoney.reference(rid)
    ctx.create("meal_transactions", rid, meal_transaction_id=rid, meal_account_id=meal_account_id,
               customer_id=acct.get("customer_id"), event_type="meals_deposit", amount=amt,
               transaction_date=ctx.now()[:10], meal_type="not_applicable", price_basis="not_applicable",
               pos_receipt_number="", deposit_method="online_card", deposit_reference=ref,
               source_meal_transaction_id="", void_reason="not_applicable", refund_reason="not_applicable",
               counterpart_meal_account_id="")
    return (f"Repayment-plan payment posted: payment record {rid}, meal account {meal_account_id}, "
            f"amount {amt:.2f} USD, portal confirmation number {ref}.")


@tool(owner="agent", rw="write")
def transfer_graduate_rollover_43099774(ctx: ToolContext, giving_meal_account_id: str,
                                        meal_account_id: str, amount: float) -> str:
    """School Nutrition rolls money from the inactive meal account of a student who graduated to a
    sibling's active meal account in the same household. One call posts one sibling transfer: the amount
    leaves the graduate's account balance as a transfer out and is credited to the receiving account's
    balance as a transfer in, both dated today and each naming the other account.

    Args:
        giving_meal_account_id: Id class — the meal account reference number of the graduate's inactive
            account the money comes from, as returned by the meal account lookup for the household.
        meal_account_id: Id class — the meal account reference number of the sibling's active account
            that receives the money, as returned by the meal account lookup for the household.
        amount: Fixed-format class — the amount rolled over, in US dollars, a positive number with 2
            decimal places (cents), already rounded half up to the cent.

    Returns:
        A confirmation sentence carrying five fields: the amount moved in US dollars with two decimals,
        the giving meal account reference, the transfer-out record reference, the receiving meal account
        reference and the transfer-in record reference, plus the posting date (YYYY-MM-DD). The presence of
        both record references means the transfer posted; a message beginning with "Error:" means nothing
        was posted.
    """
    err, rows, msg = _MealMoney.transfer_rows(ctx, "mtx_grd_", giving_meal_account_id, meal_account_id, amount)
    if err:
        return err
    for row_id, fields in rows:
        ctx.create("meal_transactions", row_id, **fields)
    return msg


@tool(owner="agent", rw="write")
def transfer_departure_rollover_b6d76228(ctx: ToolContext, giving_meal_account_id: str,
                                         meal_account_id: str, amount: float) -> str:
    """School Nutrition moves money from the inactive meal account of a student who left the district for
    another state or country to a sibling's active meal account in the same household. One
    call posts one sibling transfer: the amount leaves the departed account's balance as a transfer out
    and is credited to the receiving account's balance as a transfer in, both dated today and each naming
    the other account.

    Args:
        giving_meal_account_id: Id class — the meal account reference number of the departed student's
            inactive account the money comes from, as returned by the meal account lookup for the household.
        meal_account_id: Id class — the meal account reference number of the sibling's active account
            that receives the money, as returned by the meal account lookup for the household.
        amount: Fixed-format class — the amount moved, in US dollars, a positive number with 2 decimal
            places (cents), already rounded half up to the cent.

    Returns:
        A confirmation sentence carrying five fields: the amount moved in US dollars with two decimals,
        the giving meal account reference, the transfer-out record reference, the receiving meal account
        reference and the transfer-in record reference, plus the posting date (YYYY-MM-DD). The presence of
        both record references means the transfer posted; a message beginning with "Error:" means nothing
        was posted.
    """
    err, rows, msg = _MealMoney.transfer_rows(ctx, "mtx_dep_", giving_meal_account_id, meal_account_id, amount)
    if err:
        return err
    for row_id, fields in rows:
        ctx.create("meal_transactions", row_id, **fields)
    return msg

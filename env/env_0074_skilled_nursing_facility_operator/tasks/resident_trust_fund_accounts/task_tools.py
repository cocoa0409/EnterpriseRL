"""Hidden task tools for the resident_trust_fund_accounts difficulty (Keystone Ridge resident funds accounts).

Each tool lands one atomic write on a resident funds account or on its signed requests; the amounts it
records are worked out by whoever calls it, from the published rules and the records.
"""

from decimal import Decimal, ROUND_HALF_UP

from erlbench import ToolContext, tool


class _Cents:
    """Money formatting shared by the tools: dollars to the cent, rounded half up exactly, sign as the caller states."""

    @staticmethod
    def half_up(value) -> float:
        """Round a dollar figure half up (away from zero on an exact half cent) to 2 decimal places, in exact decimal arithmetic."""
        exact = Decimal(str(value)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        return float(exact)

    @staticmethod
    def positive(value) -> float:
        """A positive amount in dollars, rounded half up to the cent."""
        return _Cents.half_up(abs(Decimal(str(value))))


@tool(owner="agent", rw="write")
def return_improper_transfer_e2970e4f(ctx: ToolContext, trust_account_id: str, withdrawal_entry_id: str,
                                      reversal_reason: str, amount: float) -> str:
    """Give money back to a resident funds account because a transfer from it that paid a charge on the
    resident's ancillary account was improper. One call records a single return entry on the account that
    names the transfer being given back and the reason it was improper, dated the processing day, and raises
    the account balance by the amount returned. The resident or representative sees the return as a credit
    line on the account's quarterly statement, and every account lookup shows the higher balance. The
    receipt confirms the return entry was recorded.

    Args:
        trust_account_id: Id class — the reference number of the resident funds account the money goes
            back into, as shown on the account record returned by the account lookup.
        withdrawal_entry_id: Id class — the reference number of the transfer entry being given back, as shown
            on that entry's line in the account ledger lookup.
        reversal_reason: Enum class — why the transfer was improper, one of:
            "payer_covered_item" — it paid for an item or service that Medicare or Medical Assistance
            covers;
            "unauthorized" — it was made without the written authority the account requires;
            "duplicate" — it repeated a ledger entry that paid the same thing;
            "amount_error" — it was made for the wrong amount.
        amount: Fixed-format class — the money returned to the account, in US dollars as a positive
            decimal number with 2 decimal places, rounded half up to the cent; no currency sign.

    Returns:
        A one-line confirmation string of the form "Returned <amount> USD to account <trust_account_id>
        for entry <withdrawal_entry_id> (<reversal_reason>) as entry <entry id>; new balance <balance>
        USD." where <amount> and <balance> are dollars with two decimals, <reversal_reason> is the reason
        recorded and <entry id> is the new return entry's reference number. The presence of the entry
        reference number indicates the return was recorded.
    """
    acct = ctx.find("trust_accounts", trust_account_id=trust_account_id)
    customer_id = acct[0].get("customer_id") if acct else ""
    balance = float(acct[0].get("account_balance") or 0) if acct else 0.0
    amt = _Cents.positive(amount)
    rid = ctx.make_id("trv_", trust_account_id, withdrawal_entry_id, reversal_reason, amt)
    ctx.create("trust_ledger", rid, trust_entry_id=rid, trust_account_id=trust_account_id,
               customer_id=customer_id, event_type="trust_reversal", entry_date=ctx.now()[:10],
               amount=amt, withdrawal_entry_id=withdrawal_entry_id, reversal_reason=reversal_reason)
    new_balance = _Cents.half_up(balance + amt)
    ctx.update("trust_accounts", trust_account_id, account_balance=new_balance)
    return (f"Returned {amt:.2f} USD to account {trust_account_id} for entry {withdrawal_entry_id} "
            f"({reversal_reason}) as entry {rid}; new balance {new_balance:.2f} USD.")


@tool(owner="user", rw="write")
def sign_bill_payment_authorization_74e4ddf9(ctx: ToolContext, trust_account_id: str, bill_category: str,
                                             bill_entry_id: str, requested_by: str, amount: float) -> str:
    """Sign a per-bill payment authorization that lets the center pay one named center charge from the
    resident funds account, up to a stated amount. One call records the signed authorization on the
    account, naming the charge, the kind of center bill it belongs to, who signed and the amount
    authorized; no money moves when it is signed and the account balance is unchanged. The signer sees
    the authorization on the account's list of signed requests. The receipt confirms the
    authorization was recorded.

    Args:
        trust_account_id: Id class — the reference number of the resident funds account the charge is to
            be paid from, as shown on the account record returned by the account lookup.
        bill_category: Enum class — the kind of center bill the named charge belongs to, one of:
            "medicaid_patient_pay" — a monthly Medical Assistance patient pay charge;
            "private_room_board" — a monthly private-pay room and board charge;
            "bed_hold" — a charge for nights a bed was held while the resident was away;
            "ancillary_charge" — a charge on the resident's ancillary and optional services account;
            "medicare_coinsurance" — a Medicare Part A skilled nursing coinsurance charge.
        bill_entry_id: Id class — the reference number of the one center charge being authorized, as shown
            on that charge's line in the ledger lookup of the billing account it sits on.
        requested_by: Enum class — who signs the authorization, one of:
            "resident" — the resident signs personally;
            "power_of_attorney" — an agent under the resident's power of attorney signs;
            "guardian" — the court-appointed guardian of the resident's estate signs.
        amount: Fixed-format class — the most the account is authorized to pay toward the named charge, in
            US dollars as a decimal number with 2 decimal places, rounded half up to the cent; no
            currency sign.

    Returns:
        A one-line confirmation string of the form "Authorization <request id> signed by <requested_by> on
        account <trust_account_id> for <bill_category> charge <bill_entry_id>: up to <amount> USD." where
        <request id> is the new authorization's reference number and <amount> is dollars with two
        decimals. The presence of the authorization reference number indicates it was recorded.
    """
    acct = ctx.find("trust_accounts", trust_account_id=trust_account_id)
    customer_id = acct[0].get("customer_id") if acct else ""
    amt = _Cents.half_up(amount)
    rid = ctx.make_id("trq_", trust_account_id, bill_category, bill_entry_id, requested_by, amt)
    ctx.create("trust_requests", rid, trust_request_id=rid, customer_id=customer_id,
               trust_account_id=trust_account_id, request_type="bill_payment_authorization",
               requested_by=requested_by, amount=amt, bill_category=bill_category,
               bill_entry_id=bill_entry_id, created_at=ctx.now())
    return (f"Authorization {rid} signed by {requested_by} on account {trust_account_id} for "
            f"{bill_category} charge {bill_entry_id}: up to {amt:.2f} USD.")


@tool(owner="agent", rw="write")
def post_patient_pay_transfer_45809d6d(ctx: ToolContext, trust_account_id: str, bill_entry_id: str,
                                       trust_request_id: str, amount: float) -> str:
    """Move money from a resident funds account to one Medical Assistance patient pay charge on the
    center's billing record, relying on the resident's standing authorization for patient pay. One call
    records a single bill transfer entry on the account, dated the processing day, that names the patient
    pay charge it pays and the standing authorization it relies on, and lowers the account balance by the
    amount transferred. The resident or representative sees the transfer as a debit line on the account's
    quarterly statement, and every account lookup shows the lower balance. The receipt confirms the
    transfer entry was recorded.

    Args:
        trust_account_id: Id class — the reference number of the resident funds account the money comes
            from, as shown on the account record returned by the account lookup.
        bill_entry_id: Id class — the reference number of the one patient pay charge being paid, as shown on
            that charge's line in the ledger lookup of the resident's Medical Assistance case.
        trust_request_id: Id class — the reference number of the signed standing authorization for patient
            pay the transfer relies on, as shown in the account's list of signed requests.
        amount: Fixed-format class — the money moved to the charge, in US dollars as a positive decimal
            number with 2 decimal places, rounded half up to the cent; no currency sign.

    Returns:
        A one-line confirmation string of the form "Transferred <amount> USD from account
        <trust_account_id> to patient pay charge <bill_entry_id> under authorization <trust_request_id> as
        entry <entry id>; new balance <balance> USD." where <amount> and <balance> are dollars with two
        decimals and <entry id> is the new transfer entry's reference number. The presence of the entry
        reference number indicates the transfer was recorded.
    """
    acct = ctx.find("trust_accounts", trust_account_id=trust_account_id)
    customer_id = acct[0].get("customer_id") if acct else ""
    balance = float(acct[0].get("account_balance") or 0) if acct else 0.0
    amt = _Cents.positive(amount)
    eid = ctx.make_id("tbt_", trust_account_id, "medicaid_patient_pay", bill_entry_id, trust_request_id, amt)
    ctx.create("trust_ledger", eid, trust_entry_id=eid, trust_account_id=trust_account_id,
               customer_id=customer_id, event_type="trust_bill_transfer", entry_date=ctx.now()[:10],
               amount=amt, bill_category="medicaid_patient_pay", bill_entry_id=bill_entry_id,
               trust_request_id=trust_request_id)
    new_balance = _Cents.half_up(balance - amt)
    ctx.update("trust_accounts", trust_account_id, account_balance=new_balance)
    return (f"Transferred {amt:.2f} USD from account {trust_account_id} to patient pay charge {bill_entry_id} "
            f"under authorization {trust_request_id} as entry {eid}; new balance {new_balance:.2f} USD.")


@tool(owner="user", rw="write")
def sign_withdrawal_request_c6615816(ctx: ToolContext, trust_account_id: str, trust_request_id: str,
                                     amount: float) -> str:
    """Enter and sign the amount on an open withdrawal request on a resident funds account, a
    request whose purpose and signer are on file but whose amount was left open. One call writes the amount
    asked for onto that request, which stands as a signed request for that amount; no money moves and the
    account balance is unchanged. The signer sees the request, with its amount, on the account's list of
    signed requests. The receipt confirms the amount was recorded on the request.

    Args:
        trust_account_id: Id class — the reference number of the resident funds account the money is to come
            from, as shown on the account record returned by the account lookup.
        trust_request_id: Id class — the reference number of the open withdrawal request whose amount is
            being entered, as shown in the account's list of signed requests returned by the request lookup.
        amount: Fixed-format class — the money asked for, in US dollars as a positive decimal number with 2
            decimal places, rounded half up to the cent; no currency sign.

    Returns:
        A one-line confirmation string of the form "Withdrawal request <trust_request_id> on account
        <trust_account_id> signed for <amount> USD." where <amount> is dollars with two decimals. The
        presence of the request reference number with the amount indicates the amount was recorded.
    """
    amt = _Cents.positive(amount)
    ctx.update("trust_requests", trust_request_id, amount=amt)
    return f"Withdrawal request {trust_request_id} on account {trust_account_id} signed for {amt:.2f} USD."


@tool(owner="agent", rw="write")
def return_bed_hold_overcharge_0789df0a(ctx: ToolContext, trust_account_id: str, withdrawal_entry_id: str,
                                        reversal_reason: str, amount: float) -> str:
    """Give money back to a resident funds account because a transfer from it paid a bed-hold charge that
    billed more than the hold allowed. One call records a single return entry on the account that names the
    transfer being given back and the reason it was improper, dated the processing day, and raises the
    account balance by the amount returned. The resident or representative sees the return as a credit line
    on the account's quarterly statement, and every account lookup shows the higher balance.
    The receipt confirms the return entry was recorded.

    Args:
        trust_account_id: Id class — the reference number of the resident funds account the money goes
            back into, as shown on the account record returned by the account lookup.
        withdrawal_entry_id: Id class — the reference number of the bed-hold transfer entry being given
            back, as shown on that entry's line in the account ledger lookup.
        reversal_reason: Enum class — why the transfer was improper, one of:
            "payer_covered_item" — it paid for an item or service that Medicare or Medical Assistance
            covers;
            "unauthorized" — it was made without the written authority the account requires;
            "duplicate" — it repeated a ledger entry that paid the same thing;
            "amount_error" — it paid more than the charge owed, for the wrong amount.
        amount: Fixed-format class — the money returned to the account, in US dollars as a positive
            decimal number with 2 decimal places, rounded half up to the cent; no currency sign.

    Returns:
        A one-line confirmation string of the form "Returned <amount> USD to account <trust_account_id>
        for bed-hold transfer <withdrawal_entry_id> (<reversal_reason>) as entry <entry id>; new balance
        <balance> USD." where <amount> and <balance> are dollars with two decimals, <reversal_reason> is the
        reason recorded and <entry id> is the new
        return entry's reference number. The presence of the entry reference number indicates the return
        was recorded.
    """
    acct = ctx.find("trust_accounts", trust_account_id=trust_account_id)
    customer_id = acct[0].get("customer_id") if acct else ""
    balance = float(acct[0].get("account_balance") or 0) if acct else 0.0
    amt = _Cents.positive(amount)
    rid = ctx.make_id("trv_", trust_account_id, withdrawal_entry_id, reversal_reason, amt)
    ctx.create("trust_ledger", rid, trust_entry_id=rid, trust_account_id=trust_account_id,
               customer_id=customer_id, event_type="trust_reversal", entry_date=ctx.now()[:10],
               amount=amt, withdrawal_entry_id=withdrawal_entry_id, reversal_reason=reversal_reason)
    new_balance = _Cents.half_up(balance + amt)
    ctx.update("trust_accounts", trust_account_id, account_balance=new_balance)
    return (f"Returned {amt:.2f} USD to account {trust_account_id} for bed-hold transfer {withdrawal_entry_id} "
            f"({reversal_reason}) as entry {rid}; new balance {new_balance:.2f} USD.")


@tool(owner="agent", rw="write")
def return_coinsurance_overcharge_2cf6d12d(ctx: ToolContext, trust_account_id: str, withdrawal_entry_id: str,
                                           reversal_reason: str, amount: float) -> str:
    """Give money back to a resident funds account because a transfer from it paid a Medicare coinsurance
    charge that billed more coinsurance than the resident owed. One call records a single return entry on
    the account that names the transfer being given back and the reason it was improper, dated the
    processing day, and raises the account balance by the amount returned. The
    resident or representative sees the return as a credit line on the account's quarterly statement, and
    every account lookup shows the higher balance.
    The receipt confirms the return entry was recorded.

    Args:
        trust_account_id: Id class — the reference number of the resident funds account the money goes
            back into, as shown on the account record returned by the account lookup.
        withdrawal_entry_id: Id class — the reference number of the coinsurance transfer entry being given
            back, as shown on that entry's line in the account ledger lookup.
        reversal_reason: Enum class — why the transfer was improper, one of:
            "payer_covered_item" — it paid for an item or service that Medicare or Medical Assistance
            covers;
            "unauthorized" — it was made without the written authority the account requires;
            "duplicate" — it repeated a ledger entry that paid the same thing;
            "amount_error" — it paid more than the charge owed, for the wrong amount.
        amount: Fixed-format class — the money returned to the account, in US dollars as a positive
            decimal number with 2 decimal places, rounded half up to the cent; no currency sign.

    Returns:
        A one-line confirmation string of the form "Returned <amount> USD to account <trust_account_id>
        for coinsurance transfer <withdrawal_entry_id> (<reversal_reason>) as entry <entry id>; new balance
        <balance> USD." where <amount> and <balance> are dollars with two decimals, <reversal_reason> is the
        reason recorded and <entry id> is the new
        return entry's reference number. The presence of the entry reference number indicates the return
        was recorded.
    """
    acct = ctx.find("trust_accounts", trust_account_id=trust_account_id)
    customer_id = acct[0].get("customer_id") if acct else ""
    balance = float(acct[0].get("account_balance") or 0) if acct else 0.0
    amt = _Cents.positive(amount)
    rid = ctx.make_id("trv_", trust_account_id, withdrawal_entry_id, reversal_reason, amt)
    ctx.create("trust_ledger", rid, trust_entry_id=rid, trust_account_id=trust_account_id,
               customer_id=customer_id, event_type="trust_reversal", entry_date=ctx.now()[:10],
               amount=amt, withdrawal_entry_id=withdrawal_entry_id, reversal_reason=reversal_reason)
    new_balance = _Cents.half_up(balance + amt)
    ctx.update("trust_accounts", trust_account_id, account_balance=new_balance)
    return (f"Returned {amt:.2f} USD to account {trust_account_id} for coinsurance transfer "
            f"{withdrawal_entry_id} ({reversal_reason}) as entry {rid}; new balance {new_balance:.2f} USD.")

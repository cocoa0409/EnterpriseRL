"""Hidden task tools of the personal_payments_limits_and_account_access difficulty (Pocketwire Personal Account).

Each tool performs one atomic posting on a personal account with the values the caller supplies; it
judges no eligibility, computes no fee, amount or date, and never refuses because of a policy condition.
The ledger balance of the account moves by exactly the amount the posting books, so the account keeps
equal to the sum of its own activity.
"""

from erlbench import ToolContext, tool


_LEDGER_DEFAULTS = dict(txn_reference="", counterparty="", payment_type="not_applicable",
                        funding_source="not_applicable", recipient_status="not_applicable",
                        transfer_speed="not_applicable", destination_last4="", fee_type="not_applicable",
                        billing_period="", source_txn_id="", source_product="not_applicable")


@tool(owner="agent", rw="write")
def charge_plan_fee_0f985a0a(ctx: ToolContext, wallet_id: str, billing_period: str, fee_amount: float,
                             next_renewal_date: str) -> str:
    """Charge the subscription fee (monthly or annual) of a paid Pocketwire plan to a personal account for the
    billing period that starts on today's renewal date. One call books one plan-fee entry dated today
    on the account's activity, carrying the billing period it covers and the fee amount given, takes
    that amount off the account's ledger balance, and moves the account's next plan renewal date to the
    date given. The customer then sees the plan fee in the app activity and the new renewal date on the
    plan screen. The call has completed when the receipt names the new fee entry.

    Args:
        wallet_id: Id class — the reference number of the personal account being charged, as returned by
            the personal account lookup for the verified customer.
        billing_period: Fixed-format class — the billing period this plan fee covers, written YYYY-MM for
            monthly billing (the calendar month in which the period starts) or YYYY for annual billing (the
            calendar year in which the period starts); no other format is accepted.
        fee_amount: Fixed-format class — the plan fee to book for that period, in USD, a non-negative
            amount with 2 decimal places, already rounded to the cent by the caller.
        next_renewal_date: Fixed-format class — the date the following plan fee falls due, written
            YYYY-MM-DD (Eastern Time calendar date).

    Returns:
        A confirmation sentence (text) naming the new plan-fee entry reference number, the billing
        period in YYYY-MM (monthly) or YYYY (annual) form, the fee booked in USD with 2 decimal places, the account's ledger
        balance in USD after the charge, and the next renewal date in YYYY-MM-DD form. A receipt that
        names the entry reference number means the fee is booked.
    """
    wallet = (ctx.find("wallet_accounts", wallet_id=wallet_id) or [{}])[0]
    cust = wallet.get("customer_id", "")
    today = ctx.now()[:10]
    fee = round(float(fee_amount), 2)
    rid = ctx.make_id("wtx_", wallet_id, billing_period, fee, next_renewal_date)
    ctx.create("wallet_transactions", rid, **dict(_LEDGER_DEFAULTS, txn_id=rid, wallet_id=wallet_id, customer_id=cust, txn_date=today, event_type="wallet_fee", amount=fee,
                fee_type="plan_fee", billing_period=billing_period))
    balance = round(float(wallet.get("ledger_balance") or 0) - fee, 2)
    ctx.update("wallet_accounts", wallet_id, ledger_balance=balance, plan_renewal_date=next_renewal_date)
    return (f"Plan fee entry {rid} booked for billing period {billing_period}: {fee:.2f} USD. "
            f"Ledger balance now {balance:.2f} USD; next renewal date {next_renewal_date}.")


@tool(owner="user", rw="write")
def transfer_balance_to_bank_3181bc35(ctx: ToolContext, wallet_id: str, amount: float,
                                      destination_last4: str) -> str:
    """The customer sends money from their own Pocketwire personal balance to their linked bank account
    by standard (free) transfer. One call books one standard cash-out dated today for the amount given
    to the bank account ending in the four digits given, takes that amount off the account's ledger
    balance, and the transfer then shows in the app activity as a standard transfer on its way to the
    bank. No fee is charged on a standard transfer. The call has completed when the receipt names the
    new transfer reference number.

    Args:
        wallet_id: Id class — the reference number of the customer's personal account the money leaves,
            as returned by the personal account lookup and given to the customer by the representative.
        amount: Fixed-format class — the amount to send to the bank, in USD, a positive amount with 2
            decimal places.
        destination_last4: Fixed-format class — the last four digits of the linked bank account that
            receives the transfer, exactly 4 digits as the customer reads them from their bank details.

    Returns:
        A confirmation sentence (text) naming the transfer reference number, the amount sent in USD with
        2 decimal places, the last four digits of the receiving bank account, and the ledger balance in
        USD left on the personal account. A receipt that names the transfer reference number means the
        standard transfer is booked.
    """
    wallet = (ctx.find("wallet_accounts", wallet_id=wallet_id) or [{}])[0]
    cust = wallet.get("customer_id", "")
    today = ctx.now()[:10]
    amt = round(float(amount), 2)
    rid = ctx.make_id("wtx_", wallet_id, amt, destination_last4, "standard")
    ctx.create("wallet_transactions", rid, **dict(_LEDGER_DEFAULTS, txn_id=rid, wallet_id=wallet_id, customer_id=cust, txn_date=today, event_type="wallet_cash_out", amount=amt,
                txn_reference=rid, transfer_speed="standard", destination_last4=str(destination_last4)))
    balance = round(float(wallet.get("ledger_balance") or 0) - amt, 2)
    ctx.update("wallet_accounts", wallet_id, ledger_balance=balance)
    return (f"Standard transfer {rid} of {amt:.2f} USD to the bank account ending {destination_last4} "
            f"is on its way. Ledger balance left: {balance:.2f} USD.")


@tool(owner="agent", rw="write")
def post_protection_reimbursement_5be5cf5a(ctx: ToolContext, wallet_id: str, source_txn_id: str,
                                           amount: float) -> str:
    """Pay the reimbursement owed on an approved purchase protection claim into the customer's
    personal balance. One call books one claim-reimbursement credit dated today that points to the
    disputed goods-and-services payment, for the amount given, and adds that amount to the account's
    ledger balance; the customer then sees the reimbursement credited in the app activity against that
    payment. The call has completed when the receipt names the new credit reference number.

    Args:
        wallet_id: Id class — the reference number of the personal account the reimbursement is paid
            into, as returned by the personal account lookup for the verified customer.
        source_txn_id: Id class — the reference number of the disputed goods-and-services payment the
            approved claim covers, as shown in the claim record and in the account activity lookup.
        amount: Fixed-format class — the reimbursement to credit, in USD, a positive amount with 2
            decimal places, already rounded to the cent by the caller.

    Returns:
        A confirmation sentence (text) naming the reimbursement credit reference number, the disputed
        payment it points to, the amount credited in USD with 2 decimal places and the ledger balance in
        USD after the credit. A receipt that names the credit reference number means the reimbursement
        is booked.
    """
    wallet = (ctx.find("wallet_accounts", wallet_id=wallet_id) or [{}])[0]
    cust = wallet.get("customer_id", "")
    today = ctx.now()[:10]
    amt = round(float(amount), 2)
    rid = ctx.make_id("wtx_", wallet_id, source_txn_id, amt)
    ctx.create("wallet_transactions", rid, **dict(_LEDGER_DEFAULTS, txn_id=rid, wallet_id=wallet_id, customer_id=cust, txn_date=today, event_type="wallet_claim_reimbursement", amount=amt,
                source_txn_id=source_txn_id))
    balance = round(float(wallet.get("ledger_balance") or 0) + amt, 2)
    ctx.update("wallet_accounts", wallet_id, ledger_balance=balance)
    return (f"Reimbursement credit {rid} of {amt:.2f} USD booked against payment {source_txn_id}. "
            f"Ledger balance now {balance:.2f} USD.")


@tool(owner="user", rw="write")
def send_instant_cash_out_cd9063e1(ctx: ToolContext, wallet_id: str, amount: float,
                                   destination_last4: str, fee_amount: float) -> str:
    """The customer sends money from their own Pocketwire personal balance to their linked external debit
    card by instant transfer and accepts the instant transfer fee shown. One call books one instant
    cash-out dated today for the amount given to the card ending in the four digits given, books the
    instant transfer fee given as a separate fee entry pointing to that cash-out, and takes both the
    amount and the fee off the account's ledger balance. The customer then sees the instant transfer
    and its fee in the app activity. The call has completed when the receipt names the new transfer
    reference number.

    Args:
        wallet_id: Id class — the reference number of the customer's personal account the money leaves,
            as returned by the personal account lookup and given to the customer by the representative.
        amount: Fixed-format class — the amount to send to the debit card, in USD, a positive amount with
            2 decimal places.
        destination_last4: Fixed-format class — the last four digits of the linked external debit card
            that receives the transfer, exactly 4 digits as printed on that card.
        fee_amount: Fixed-format class — the instant transfer fee the customer accepts for this transfer,
            in USD, a non-negative amount with 2 decimal places (0.00 when no fee applies).

    Returns:
        A confirmation sentence (text) naming the instant transfer reference number, the amount sent in
        USD with 2 decimal places, the last four digits of the receiving card, the fee entry reference
        number with the fee in USD with 2 decimal places, and the ledger balance in USD left on the
        personal account. A receipt that names the transfer reference number means the instant transfer
        and its fee are booked.
    """
    wallet = (ctx.find("wallet_accounts", wallet_id=wallet_id) or [{}])[0]
    cust = wallet.get("customer_id", "")
    today = ctx.now()[:10]
    amt = round(float(amount), 2)
    fee = round(float(fee_amount), 2)
    rid = ctx.make_id("wtx_", wallet_id, amt, destination_last4, fee, "instant")
    ctx.create("wallet_transactions", rid, **dict(_LEDGER_DEFAULTS, txn_id=rid, wallet_id=wallet_id, customer_id=cust, txn_date=today, event_type="wallet_cash_out", amount=amt,
                txn_reference=rid, transfer_speed="instant", destination_last4=str(destination_last4)))
    fid = ctx.make_id("wtx_", rid, "instant_transfer_fee", fee)
    ctx.create("wallet_transactions", fid, **dict(_LEDGER_DEFAULTS, txn_id=fid, wallet_id=wallet_id, customer_id=cust, txn_date=today, event_type="wallet_fee", amount=fee,
                fee_type="instant_transfer_fee", source_txn_id=rid))
    balance = round(float(wallet.get("ledger_balance") or 0) - amt - fee, 2)
    ctx.update("wallet_accounts", wallet_id, ledger_balance=balance)
    return (f"Instant transfer {rid} of {amt:.2f} USD to the card ending {destination_last4} is sent; "
            f"fee entry {fid}: {fee:.2f} USD. Ledger balance left: {balance:.2f} USD.")

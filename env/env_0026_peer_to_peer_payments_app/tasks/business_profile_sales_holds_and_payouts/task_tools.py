"""Hidden task tools for business_profile_sales_holds_and_payouts (Pocketwire Business Profile).

Each tool performs one atomic bookkeeping write on a business profile with the values the
caller passes; none of them judges eligibility, prerequisites or amounts.
"""

from erlbench import ToolContext, tool


# Fields that do not apply to a fee, credit or payout entry, in the charter's own literals.
BLANK_ROW = dict(buyer_username="", sale_channel="not_applicable", buyer_region="not_applicable",
                 billing_period="", hold_type="not_applicable", release_due_date="",
                 tracking_number="", destination_last4="", payout_method="not_applicable",
                 fee_type="not_applicable", source_txn_id="", txn_reference="")


@tool(owner="user", rw="write")
def send_instant_payout_0ea58e95(ctx: ToolContext, business_id: str, amount: float,
                                 fee_amount: float, destination_last4: str) -> str:
    """The business owner sends an instant payout from their Pocketwire Business Profile balance
    to their linked debit card. One call books the payout itself as an instant_card payout dated
    today, books its instant payout fee as a separate fee entry tied to that payout, and lowers the
    business balance by the payout amount plus the fee. The owner sees the payout and its fee in the
    profile's activity straight away; the money is on its way to the card. A receipt carrying the
    payout reference and status "sent" means the payout was booked.

    Args:
        business_id: Id class — the reference number of the owner's business profile the money is
            paid out from, as returned by the business profile lookup.
        amount: Fixed-format class — the payout amount sent to the debit card, in USD, 2 decimal
            places, positive, rounded half up to the cent before booking.
        fee_amount: Fixed-format class — the instant payout fee booked with this payout, in USD,
            2 decimal places, zero or positive, rounded half up to the cent before booking.
        destination_last4: Fixed-format class — the last four digits of the owner's linked debit
            card that receives the payout, written as 4 digits with no spaces or punctuation.

    Returns:
        A dictionary receipt: payout_id (string, the reference number of the booked payout entry),
        payout_reference (string, the payout reference shown to the owner in the app), fee_id
        (string, the reference number of the booked instant payout fee entry), amount (number, USD,
        2 decimal places, the amount sent), fee_amount (number, USD, 2 decimal places, the fee
        booked), payout_date (string, YYYY-MM-DD, the booking date), business_balance (number, USD,
        2 decimal places, the business balance after the payout and fee, or null when the profile
        was not found), and status (string, always "sent" once the payout is booked).
    """
    amt = round(float(amount), 2)
    fee = round(float(fee_amount), 2)
    last4 = str(destination_last4).strip()
    today = ctx.now()[:10]
    pid = ctx.make_id("bpo_", business_id, amt, fee, last4)
    ref = "PWP-" + pid[-8:].upper()
    owner = ctx.find("business_profiles", business_id=business_id)
    customer_id = owner[0].get("customer_id") if owner else ""
    row = dict(BLANK_ROW)
    row.update(business_txn_id=pid, business_id=business_id, customer_id=customer_id,
               event_type="business_payout", txn_reference=ref, txn_date=today, amount=amt,
               payout_method="instant_card", destination_last4=last4)
    ctx.create("business_transactions", pid, **row)
    fid = ctx.make_id("bfe_", pid, "instant_payout_fee", fee)
    frow = dict(BLANK_ROW)
    frow.update(business_txn_id=fid, business_id=business_id, customer_id=customer_id,
                event_type="business_fee", txn_date=today, amount=fee,
                fee_type="instant_payout_fee", source_txn_id=pid)
    ctx.create("business_transactions", fid, **frow)
    new_balance = None
    if owner:
        new_balance = round(float(owner[0].get("business_balance") or 0) - amt - fee, 2)
        ctx.update("business_profiles", business_id, business_balance=new_balance)
    return str({"payout_id": pid, "payout_reference": ref, "fee_id": fid, "amount": amt,
                "fee_amount": fee, "payout_date": today, "business_balance": new_balance,
                "status": "sent"})


@tool(owner="agent", rw="write")
def book_subscription_fee_2324701e(ctx: ToolContext, business_id: str, fee_amount: float) -> str:
    """A support representative books the current calendar month's subscription fee on a
    Pocketwire Business Profile. One call records a subscription_fee entry for this month's
    billing period, dated today, and lowers the business balance by the fee. The owner sees the
    subscription charge in the profile's activity at once. A receipt carrying the fee entry
    reference and status "booked" means the charge was recorded.

    Args:
        business_id: Id class — the reference number of the business profile being charged, as
            returned by the business profile lookup.
        fee_amount: Fixed-format class — the subscription fee charged for the month, in USD,
            2 decimal places, zero or positive, rounded half up to the cent before booking.

    Returns:
        A dictionary receipt: fee_id (string, the reference number of the booked subscription fee
        entry), billing_period (string, YYYY-MM, the month the fee covers), fee_amount (number, USD,
        2 decimal places, the fee booked), fee_date (string, YYYY-MM-DD, the booking date),
        business_balance (number, USD, 2 decimal places, the business balance after the charge, or
        null when the profile was not found), and status (string, always "booked" once recorded).
    """
    fee = round(float(fee_amount), 2)
    today = ctx.now()[:10]
    period = today[:7]
    fid = ctx.make_id("bsf_", business_id, period, fee)
    owner = ctx.find("business_profiles", business_id=business_id)
    customer_id = owner[0].get("customer_id") if owner else ""
    row = dict(BLANK_ROW)
    row.update(business_txn_id=fid, business_id=business_id, customer_id=customer_id,
               event_type="business_fee", txn_date=today, amount=fee,
               fee_type="subscription_fee", billing_period=period)
    ctx.create("business_transactions", fid, **row)
    new_balance = None
    if owner:
        new_balance = round(float(owner[0].get("business_balance") or 0) - fee, 2)
        ctx.update("business_profiles", business_id, business_balance=new_balance)
    return str({"fee_id": fid, "billing_period": period, "fee_amount": fee, "fee_date": today,
                "business_balance": new_balance, "status": "booked"})


@tool(owner="agent", rw="write")
def book_chargeback_fee_9ab6815a(ctx: ToolContext, business_id: str, chargeback_txn_id: str,
                                 fee_amount: float) -> str:
    """A support representative books the chargeback fee on one chargeback debited from a
    Pocketwire Business Profile. One call records a chargeback_fee entry tied to that chargeback,
    dated today, and lowers the business balance by the fee. The owner sees the fee next to the
    chargeback in the profile's activity at once. A receipt carrying the fee entry reference and
    status "booked" means the fee was recorded.

    Args:
        business_id: Id class — the reference number of the business profile the chargeback was
            debited from, as returned by the business profile lookup.
        chargeback_txn_id: Id class — the reference number of the chargeback entry the fee belongs
            to, as listed in the business profile activity lookup.
        fee_amount: Fixed-format class — the chargeback fee charged, in USD, 2 decimal places, zero
            or positive, rounded half up to the cent before booking.

    Returns:
        A dictionary receipt: fee_id (string, the reference number of the booked chargeback fee
        entry), chargeback_txn_id (string, the chargeback the fee is tied to), fee_amount (number,
        USD, 2 decimal places, the fee booked), fee_date (string, YYYY-MM-DD, the booking date),
        business_balance (number, USD, 2 decimal places, the business balance after the fee, or null
        when the profile was not found), and status (string, always "booked" once recorded).
    """
    fee = round(float(fee_amount), 2)
    today = ctx.now()[:10]
    fid = ctx.make_id("bcf_", business_id, chargeback_txn_id, fee)
    owner = ctx.find("business_profiles", business_id=business_id)
    customer_id = owner[0].get("customer_id") if owner else ""
    row = dict(BLANK_ROW)
    row.update(business_txn_id=fid, business_id=business_id, customer_id=customer_id,
               event_type="business_fee", txn_date=today, amount=fee,
               fee_type="chargeback_fee", source_txn_id=chargeback_txn_id)
    ctx.create("business_transactions", fid, **row)
    new_balance = None
    if owner:
        new_balance = round(float(owner[0].get("business_balance") or 0) - fee, 2)
        ctx.update("business_profiles", business_id, business_balance=new_balance)
    return str({"fee_id": fid, "chargeback_txn_id": chargeback_txn_id, "fee_amount": fee,
                "fee_date": today, "business_balance": new_balance, "status": "booked"})


@tool(owner="agent", rw="write")
def credit_refund_fee_b8556c63(ctx: ToolContext, business_id: str, fee_txn_id: str,
                               credit_amount: float) -> str:
    """A support representative credits back part of the transaction fee of a refunded sale on a
    Pocketwire Business Profile. One call records a fee credit entry of the
    transaction_fee kind tied to the sale's transaction fee entry, dated today, and raises the
    business balance by the credit. The owner sees the credit in the profile's activity at once.
    A receipt carrying the credit entry reference and status "credited" means the credit was
    recorded.

    Args:
        business_id: Id class — the reference number of the business profile that receives the
            credit, as returned by the business profile lookup.
        fee_txn_id: Id class — the reference number of the transaction fee entry of the refunded
            sale that the credit is booked against, as listed in the business profile activity
            lookup.
        credit_amount: Fixed-format class — the amount credited back, in USD, 2 decimal places, zero
            or positive, rounded half up to the cent before booking.

    Returns:
        A dictionary receipt: credit_id (string, the reference number of the booked fee credit
        entry), fee_txn_id (string, the transaction fee entry credited), credit_amount (number, USD,
        2 decimal places, the amount credited), credit_date (string, YYYY-MM-DD, the booking date),
        business_balance (number, USD, 2 decimal places, the business balance after the credit, or
        null when the profile was not found), and status (string, always "credited" once recorded).
    """
    amt = round(float(credit_amount), 2)
    today = ctx.now()[:10]
    cid = ctx.make_id("bfc_", business_id, fee_txn_id, amt)
    owner = ctx.find("business_profiles", business_id=business_id)
    customer_id = owner[0].get("customer_id") if owner else ""
    row = dict(BLANK_ROW)
    row.update(business_txn_id=cid, business_id=business_id, customer_id=customer_id,
               event_type="business_fee_credit", txn_date=today, amount=amt,
               fee_type="transaction_fee", source_txn_id=fee_txn_id)
    ctx.create("business_transactions", cid, **row)
    new_balance = None
    if owner:
        new_balance = round(float(owner[0].get("business_balance") or 0) + amt, 2)
        ctx.update("business_profiles", business_id, business_balance=new_balance)
    return str({"credit_id": cid, "fee_txn_id": fee_txn_id, "credit_amount": amt,
                "credit_date": today, "business_balance": new_balance, "status": "credited"})


@tool(owner="user", rw="write")
def pay_out_to_bank_7d50e7f4(ctx: ToolContext, business_id: str, amount: float,
                             destination_last4: str) -> str:
    """The business owner pays out money from their Pocketwire Business Profile balance to their
    linked bank account as a free standard bank transfer. One call books a standard_bank payout
    dated today and lowers the business balance by the payout amount; no fee is charged. The owner
    sees the payout in the profile's activity straight away and the bank receives it within the
    tier's standard payout time. A receipt carrying the payout reference and status "sent" means the
    payout was booked.

    Args:
        business_id: Id class — the reference number of the owner's business profile the money is
            paid out from, as returned by the business profile lookup.
        amount: Fixed-format class — the payout amount sent to the bank account, in USD, 2 decimal
            places, positive, rounded half up to the cent before booking.
        destination_last4: Fixed-format class — the last four digits of the owner's linked bank
            account that receives the payout, written as 4 digits with no spaces or punctuation.

    Returns:
        A dictionary receipt: payout_id (string, the reference number of the booked payout entry),
        payout_reference (string, the payout reference shown to the owner in the app), amount
        (number, USD, 2 decimal places, the amount sent), payout_date (string, YYYY-MM-DD, the
        booking date), business_balance (number, USD, 2 decimal places, the business balance after
        the payout, or null when the profile was not found), and status (string, always "sent" once
        the payout is booked).
    """
    amt = round(float(amount), 2)
    last4 = str(destination_last4).strip()
    today = ctx.now()[:10]
    pid = ctx.make_id("bpb_", business_id, amt, last4)
    ref = "PWB-" + pid[-8:].upper()
    owner = ctx.find("business_profiles", business_id=business_id)
    customer_id = owner[0].get("customer_id") if owner else ""
    row = dict(BLANK_ROW)
    row.update(business_txn_id=pid, business_id=business_id, customer_id=customer_id,
               event_type="business_payout", txn_reference=ref, txn_date=today, amount=amt,
               payout_method="standard_bank", destination_last4=last4)
    ctx.create("business_transactions", pid, **row)
    new_balance = None
    if owner:
        new_balance = round(float(owner[0].get("business_balance") or 0) - amt, 2)
        ctx.update("business_profiles", business_id, business_balance=new_balance)
    return str({"payout_id": pid, "payout_reference": ref, "amount": amt, "payout_date": today,
                "business_balance": new_balance, "status": "sent"})

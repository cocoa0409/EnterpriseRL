"""Hidden task tools of the seller_payouts_reserves_chargebacks difficulty (Northloop Payments).

Each tool books exactly one payments-ledger entry and moves the payments balance by that entry,
keeping the account's negative-balance date in step with the balance. No tool judges eligibility,
works out an amount, or checks whether anything else has been done first.
"""

from erlbench import ToolContext, tool


@tool(owner="agent", rw="write")
def send_scheduled_payout_7857f918(ctx: ToolContext, payout_account_id: str, amount: float) -> str:
    """Send the scheduled payout of the current payout day from a seller's Northloop Payments account to the
    bank account on file. One call books one scheduled payout entry on the payments ledger for the amount
    given, addressed to the bank account currently on file, and lowers the account's total balance by that
    amount; the payout then appears in the seller's payout history with its payout reference. The amount is
    taken exactly as given; nothing else on the account changes.

    Args:
        payout_account_id: Id class — the payments account reference number of the seller's Northloop
            Payments account, as returned by the payments account lookup.
        amount: Fixed-format class — the amount of the scheduled payout in USD, a positive number with
            2 decimal places (cents), rounded to the cent before it is passed; it is booked exactly as given.

    Returns:
        A text rendering of a dictionary describing the payout that was booked:
        status — the literal "payout_sent" when the payout entry was booked;
        payout_event_id — reference of the new payments ledger entry;
        disbursement_ref — payout reference of the scheduled payout;
        payout_method — the literal "scheduled";
        bank_last4 — last four digits of the destination bank account;
        amount — the payout amount in USD with 2 decimal places;
        balance — the account's total balance in USD after the payout, 2 decimal places;
        event_date — the payout date, YYYY-MM-DD.
    """
    acct = (ctx.find("payout_accounts", payout_account_id=payout_account_id) or [{}])[0]
    amt = round(float(amount), 2)
    day = ctx.now()[:10]
    ref = ctx.make_id("sdb_", payout_account_id, amt, day)
    eid = ctx.make_id("pev_", "payout_disbursement", payout_account_id, ref)
    ctx.create("payout_events", eid, payout_event_id=eid, payout_account_id=payout_account_id,
               customer_id=acct.get("customer_id"), event_type="payout_disbursement", event_date=day,
               amount=amt, disbursement_ref=ref, payout_method="scheduled", bank_last4=acct.get("bank_last4"))
    old = round(float(acct.get("balance") or 0), 2)
    new = round(old - amt, 2)
    since = acct.get("negative_since_date") or ""
    since = "" if new >= 0 else (since if old < 0 and since else day)
    ctx.update("payout_accounts", payout_account_id, balance=new, negative_since_date=since)
    return str({"status": "payout_sent", "payout_event_id": eid, "disbursement_ref": ref,
                "payout_method": "scheduled", "bank_last4": acct.get("bank_last4"), "amount": amt,
                "balance": new, "event_date": day})


@tool(owner="user", rw="write")
def request_on_demand_payout_667d53e6(ctx: ToolContext, payout_account_id: str, amount: float) -> str:
    """The seller requests an on-demand payout from their own Northloop Payments account to the bank account
    on file, outside the regular payout schedule. One call books one on-demand payout entry on the payments
    ledger for the amount given, addressed to the bank account currently on file, and lowers the account's
    total balance by that amount; the seller then sees the on-demand payout and its payout reference in their
    payout history. The amount is taken exactly as given; nothing else on the account changes.

    Args:
        payout_account_id: Id class — the payments account reference number of the seller's own Northloop
            Payments account, as read out by the support agent from the payments account lookup.
        amount: Fixed-format class — the amount of the on-demand payout in USD, a positive number with
            2 decimal places (cents), as stated by the support agent; it is booked exactly as given.

    Returns:
        A text rendering of a dictionary describing the payout that was booked:
        status — the literal "payout_requested" when the payout entry was booked;
        payout_event_id — reference of the new payments ledger entry;
        disbursement_ref — payout reference of the on-demand payout;
        payout_method — the literal "on_demand";
        bank_last4 — last four digits of the destination bank account;
        amount — the payout amount in USD with 2 decimal places;
        balance — the account's total balance in USD after the payout, 2 decimal places;
        event_date — the payout date, YYYY-MM-DD.
    """
    acct = (ctx.find("payout_accounts", payout_account_id=payout_account_id) or [{}])[0]
    amt = round(float(amount), 2)
    day = ctx.now()[:10]
    ref = ctx.make_id("odb_", payout_account_id, amt, day)
    eid = ctx.make_id("pev_", "payout_disbursement", payout_account_id, ref)
    ctx.create("payout_events", eid, payout_event_id=eid, payout_account_id=payout_account_id,
               customer_id=acct.get("customer_id"), event_type="payout_disbursement", event_date=day,
               amount=amt, disbursement_ref=ref, payout_method="on_demand", bank_last4=acct.get("bank_last4"))
    old = round(float(acct.get("balance") or 0), 2)
    new = round(old - amt, 2)
    since = acct.get("negative_since_date") or ""
    since = "" if new >= 0 else (since if old < 0 and since else day)
    ctx.update("payout_accounts", payout_account_id, balance=new, negative_since_date=since)
    return str({"status": "payout_requested", "payout_event_id": eid, "disbursement_ref": ref,
                "payout_method": "on_demand", "bank_last4": acct.get("bank_last4"), "amount": amt,
                "balance": new, "event_date": day})


@tool(owner="agent", rw="write")
def post_instant_payout_fee_64da22a6(ctx: ToolContext, payout_account_id: str, disbursement_ref: str,
                                     amount: float) -> str:
    """Book the fee of an instant payout on a seller's Northloop Payments account. One call books one instant
    payout fee entry on the payments ledger that names the instant payout it is charged for, and lowers the
    account's total balance by the fee; the seller then sees the fee next to that instant payout in their
    payments history. The fee is taken exactly as given; nothing else on the account changes.

    Args:
        payout_account_id: Id class — the payments account reference number of the seller's Northloop
            Payments account, as returned by the payments account lookup.
        disbursement_ref: Id class — the payout reference number of the instant payout the fee is charged
            for, as shown on that instant payout in the payments ledger lookup.
        amount: Fixed-format class — the instant payout fee in USD, a positive number with 2 decimal places
            (cents), rounded to the cent before it is passed; it is booked exactly as given.

    Returns:
        A text rendering of a dictionary describing the fee that was booked:
        status — the literal "fee_posted" when the fee entry was booked;
        payout_event_id — reference of the new payments ledger entry;
        disbursement_ref — payout reference of the instant payout charged for;
        amount — the fee in USD with 2 decimal places;
        balance — the account's total balance in USD after the fee, 2 decimal places;
        event_date — the date the fee was charged, YYYY-MM-DD.
    """
    acct = (ctx.find("payout_accounts", payout_account_id=payout_account_id) or [{}])[0]
    amt = round(float(amount), 2)
    day = ctx.now()[:10]
    eid = ctx.make_id("pev_", "payout_instant_fee", payout_account_id, disbursement_ref, amt)
    ctx.create("payout_events", eid, payout_event_id=eid, payout_account_id=payout_account_id,
               customer_id=acct.get("customer_id"), event_type="payout_instant_fee", event_date=day,
               amount=amt, disbursement_ref=disbursement_ref)
    old = round(float(acct.get("balance") or 0), 2)
    new = round(old - amt, 2)
    since = acct.get("negative_since_date") or ""
    since = "" if new >= 0 else (since if old < 0 and since else day)
    ctx.update("payout_accounts", payout_account_id, balance=new, negative_since_date=since)
    return str({"status": "fee_posted", "payout_event_id": eid, "disbursement_ref": disbursement_ref,
                "amount": amt, "balance": new, "event_date": day})


@tool(owner="agent", rw="write")
def return_won_chargeback_debit_b5e77014(ctx: ToolContext, payout_account_id: str, chargeback_case_id: str,
                                         amount: float) -> str:
    """Return the debit of a chargeback case to a seller's Northloop Payments account. One call books one
    chargeback reversal entry of the returned-debit kind on the payments ledger for the chargeback case
    named, and raises the account's total balance by the amount returned; the seller then sees the returned
    debit against that chargeback case in their payments history. The amount is taken exactly as given;
    nothing else on the account or the case changes.

    Args:
        payout_account_id: Id class — the payments account reference number of the seller's Northloop
            Payments account, as returned by the payments account lookup.
        chargeback_case_id: Id class — the chargeback case reference number the debit is returned on, as
            shown on the chargeback dispute lookup and on the chargeback debit in the payments ledger.
        amount: Fixed-format class — the debit returned in USD, a positive number with 2 decimal places
            (cents), rounded to the cent before it is passed; it is booked exactly as given.

    Returns:
        A text rendering of a dictionary describing the entry that was booked:
        status — the literal "debit_returned" when the entry was booked;
        payout_event_id — reference of the new payments ledger entry;
        chargeback_case_id — the chargeback case the debit was returned on;
        fee_movement — the literal "debit_returned";
        amount — the amount returned in USD with 2 decimal places;
        balance — the account's total balance in USD after the return, 2 decimal places;
        event_date — the date of the return, YYYY-MM-DD.
    """
    acct = (ctx.find("payout_accounts", payout_account_id=payout_account_id) or [{}])[0]
    amt = round(float(amount), 2)
    day = ctx.now()[:10]
    eid = ctx.make_id("pev_", "payout_chargeback_reversal", payout_account_id, chargeback_case_id, "debit_returned")
    ctx.create("payout_events", eid, payout_event_id=eid, payout_account_id=payout_account_id,
               customer_id=acct.get("customer_id"), event_type="payout_chargeback_reversal", event_date=day,
               amount=amt, chargeback_case_id=chargeback_case_id, fee_movement="debit_returned")
    old = round(float(acct.get("balance") or 0), 2)
    new = round(old + amt, 2)
    since = acct.get("negative_since_date") or ""
    since = "" if new >= 0 else (since if old < 0 and since else day)
    ctx.update("payout_accounts", payout_account_id, balance=new, negative_since_date=since)
    return str({"status": "debit_returned", "payout_event_id": eid, "chargeback_case_id": chargeback_case_id,
                "fee_movement": "debit_returned", "amount": amt, "balance": new, "event_date": day})


@tool(owner="agent", rw="write")
def return_won_chargeback_fee_5c062853(ctx: ToolContext, payout_account_id: str, chargeback_case_id: str,
                                       amount: float) -> str:
    """Return chargeback fee money on a chargeback case to a seller's Northloop Payments account. One call books
    one chargeback reversal entry of the fee-return kind on the payments ledger for the chargeback case named,
    and raises the account's total balance by the amount returned; the seller then sees the returned fee against
    that chargeback case in their payments history. The amount is taken exactly as given; nothing else on the
    account or the case changes.

    Args:
        payout_account_id: Id class — the payments account reference number of the seller's Northloop
            Payments account, as returned by the payments account lookup.
        chargeback_case_id: Id class — the chargeback case reference number the fee is returned on, as shown
            on the chargeback dispute lookup and on the chargeback fee in the payments ledger.
        amount: Fixed-format class — the fee amount returned in USD, a positive number with 2 decimal places
            (cents), rounded to the cent before it is passed; it is booked exactly as given.

    Returns:
        A text rendering of a dictionary describing the entry that was booked:
        status — the literal "fee_returned" when the entry was booked;
        payout_event_id — reference of the new payments ledger entry;
        chargeback_case_id — the chargeback case the fee was returned on;
        fee_movement — the literal "fee_returned";
        amount — the amount returned in USD with 2 decimal places;
        balance — the account's total balance in USD after the return, 2 decimal places;
        event_date — the date of the return, YYYY-MM-DD.
    """
    acct = (ctx.find("payout_accounts", payout_account_id=payout_account_id) or [{}])[0]
    amt = round(float(amount), 2)
    day = ctx.now()[:10]
    eid = ctx.make_id("pev_", "payout_chargeback_reversal", payout_account_id, chargeback_case_id, "fee_returned", amt)
    ctx.create("payout_events", eid, payout_event_id=eid, payout_account_id=payout_account_id,
               customer_id=acct.get("customer_id"), event_type="payout_chargeback_reversal", event_date=day,
               amount=amt, chargeback_case_id=chargeback_case_id, fee_movement="fee_returned")
    old = round(float(acct.get("balance") or 0), 2)
    new = round(old + amt, 2)
    since = acct.get("negative_since_date") or ""
    since = "" if new >= 0 else (since if old < 0 and since else day)
    ctx.update("payout_accounts", payout_account_id, balance=new, negative_since_date=since)
    return str({"status": "fee_returned", "payout_event_id": eid, "chargeback_case_id": chargeback_case_id,
                "fee_movement": "fee_returned", "amount": amt, "balance": new, "event_date": day})


@tool(owner="user", rw="write")
def pay_negative_balance_by_card_47b519ae(ctx: ToolContext, payout_account_id: str, amount: float) -> str:
    """The seller authorises a card settlement of the negative balance on their own Northloop Payments account,
    charged to the payment card on file. One call books one successful card charge entry on the payments ledger
    for the amount given and raises the account's total balance by that amount; when the balance reaches zero or
    more, the account no longer shows a negative-balance date. The seller then sees the card charge in their
    payments history. The amount is taken exactly as given; nothing else on the account changes.

    Args:
        payout_account_id: Id class — the payments account reference number of the seller's own Northloop
            Payments account, as read out by the support agent from the payments account lookup.
        amount: Fixed-format class — the amount charged to the card on file in USD, a positive number with
            2 decimal places (cents), as stated by the support agent; it is booked exactly as given.

    Returns:
        A text rendering of a dictionary describing the charge that was booked:
        status — the literal "card_charged" when the charge entry was booked;
        payout_event_id — reference of the new payments ledger entry;
        charge_attempt — the attempt number recorded for the charge (integer);
        charge_outcome — the literal "succeeded";
        amount — the amount charged in USD with 2 decimal places;
        balance — the account's total balance in USD after the charge, 2 decimal places;
        negative_since_date — the date the balance went below zero, YYYY-MM-DD, or empty when it is zero or more;
        event_date — the date of the charge, YYYY-MM-DD.
    """
    acct = (ctx.find("payout_accounts", payout_account_id=payout_account_id) or [{}])[0]
    amt = round(float(amount), 2)
    day = ctx.now()[:10]
    eid = ctx.make_id("pev_", "payout_negative_balance_charge", payout_account_id, amt, day)
    ctx.create("payout_events", eid, payout_event_id=eid, payout_account_id=payout_account_id,
               customer_id=acct.get("customer_id"), event_type="payout_negative_balance_charge", event_date=day,
               amount=amt, charge_attempt=1, charge_outcome="succeeded")
    old = round(float(acct.get("balance") or 0), 2)
    new = round(old + amt, 2)
    since = acct.get("negative_since_date") or ""
    since = "" if new >= 0 else (since if old < 0 and since else day)
    ctx.update("payout_accounts", payout_account_id, balance=new, negative_since_date=since)
    return str({"status": "card_charged", "payout_event_id": eid, "charge_attempt": 1, "charge_outcome": "succeeded",
                "amount": amt, "balance": new, "negative_since_date": since, "event_date": day})

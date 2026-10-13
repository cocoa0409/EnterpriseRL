"""Hidden task tools of the host_payouts difficulty (Roamhaven payout methods).

Each tool performs exactly one atomic write on the payout ledger with the arguments it is given. The tools
never judge eligibility, never aggregate history and never compute an amount: every figure is worked out
by the caller from the published payout policies and passed in as a fixed-format argument.
"""

from erlbench import ToolContext, tool


@tool(owner="agent", rw="write")
def book_conversion_fee_3c5b00cd(ctx: ToolContext, payout_method_id: str, source_event_id: str,
                                 amount: float) -> str:
    """Book the currency-conversion fee of one transfer against the payout method it was sent to.

    A support agent uses this to post the conversion fee that a transfer paid out in a currency other than
    USD carries. One call adds one fee entry of kind cross_currency_fee to the payout method's ledger, dated
    today, naming the transfer it belongs to and carrying the amount given; the fee is taken out of the
    method's undisbursed balance, which drops by exactly that amount. Nothing else on the method or on the
    transfer changes. The host sees the fee as its own line in the payout history and on the next earnings
    statement. The call has succeeded when the receipt below comes back with status "booked".

    Args:
        payout_method_id: Id class — the reference number of the payout method the fee is charged against,
            exactly as returned by the payout-method lookup.
        source_event_id: Id class — the reference number of the transfer record (a payout sent to the
            method) that the fee belongs to, exactly as shown by the payout ledger lookup.
        amount: Fixed-format class — the conversion fee as a positive USD amount, 2 decimal places, already
            rounded as the fee policy prescribes; the tool stores it rounded to 2 decimal places and never
            changes it otherwise.

    Returns:
        A text rendering of a dictionary with these fields: payout_txn_id (string, the reference number of
        the new fee entry), payout_method_id (string, the method charged), source_event_id (string, the
        transfer the fee belongs to), fee_type (string, always "cross_currency_fee"), amount (number, the USD
        fee booked, 2 decimal places), posted_date (string, YYYY-MM-DD, today) and status (string, "booked"
        on success).
    """
    owner_rows = ctx.find("payout_methods", payout_method_id=payout_method_id)
    rid = ctx.make_id("pcf_", payout_method_id, source_event_id, amount)
    value = round(float(amount), 2)
    ctx.create("payout_transactions", rid, payout_txn_id=rid, payout_method_id=payout_method_id,
               customer_id=owner_rows[0].get("customer_id") if owner_rows else None, event_type="payout_fee_charged",
               posted_date=ctx.now()[:10], stay_id=None, installment_number=0,
               source_event_id=source_event_id, amount=value, fee_type="cross_currency_fee",
               deduction_type="none", credit_type="none", hold_reason="none", return_reason="none")
    return str({"payout_txn_id": rid, "payout_method_id": payout_method_id,
                "source_event_id": source_event_id, "fee_type": "cross_currency_fee", "amount": value,
                "posted_date": ctx.now()[:10], "status": "booked"})


@tool(owner="user", rw="write")
def send_on_request_payout_d225f921(ctx: ToolContext, payout_method_id: str, host_account_id: str,
                                    amount: float) -> str:
    """The host confirms, in person in the host app, an on-request payout from one of their payout methods.

    The host uses this to release money from a payout method's undisbursed balance between scheduled runs.
    One call sends one transfer of the confirmed amount to the account, card or receiver profile on that
    payout method and records it in the method's payout history, dated today; the method's undisbursed
    balance drops by exactly that amount, and whatever stays in the balance waits for the next scheduled
    run. The transfer is not tied to a single stay. The host sees the payout as sent in the payout history
    straight away; arrival follows the rail's processing time. The call has succeeded when the receipt
    below comes back with status "sent".

    Args:
        payout_method_id: Id class — the reference number of the payout method the money is sent to, as
            given to the host by the support agent from the payout-method lookup.
        host_account_id: Id class — the reference number of the host account the payout method belongs
            to, as given to the host by the support agent from the host-account lookup.
        amount: Fixed-format class — the payout amount the host confirms, a positive USD amount with 2
            decimal places, exactly as the support agent stated it; the tool stores it rounded to 2 decimal
            places.

    Returns:
        A text rendering of a dictionary with these fields: payout_txn_id (string, the reference number of
        the transfer), payout_method_id (string, the method paid), host_account_id (string, the host
        account), amount (number, the USD amount sent, 2 decimal places), posted_date (string, YYYY-MM-DD,
        today) and status (string, "sent" on success).
    """
    owner_rows = ctx.find("payout_methods", payout_method_id=payout_method_id)
    rid = ctx.make_id("por_", payout_method_id, host_account_id, amount)
    value = round(float(amount), 2)
    ctx.create("payout_transactions", rid, payout_txn_id=rid, payout_method_id=payout_method_id,
               customer_id=owner_rows[0].get("customer_id") if owner_rows else None, event_type="payout_sent",
               posted_date=ctx.now()[:10], stay_id=None, installment_number=0, source_event_id=None,
               amount=value, fee_type="none", deduction_type="none", credit_type="none",
               hold_reason="none", return_reason="none")
    return str({"payout_txn_id": rid, "payout_method_id": payout_method_id,
                "host_account_id": host_account_id, "amount": value,
                "posted_date": ctx.now()[:10], "status": "sent"})


@tool(owner="agent", rw="write")
def book_return_charge_692b7e7b(ctx: ToolContext, payout_method_id: str, source_event_id: str,
                                amount: float) -> str:
    """Book the return charge of one returned transfer against the payout method it was returned to.

    A support agent uses this to post the charge that a transfer sent back by the receiving bank or rail
    carries. One call adds one fee entry of kind returned_payout_fee to the payout method's ledger, dated
    today, naming the return record it belongs to and carrying the amount given; the charge is taken out of
    the method's undisbursed balance, which drops by exactly that amount. The method's status, details and
    every other entry stay as they are. The host sees the charge as its own line in the payout history. The
    call has succeeded when the receipt below comes back with status "booked".

    Args:
        payout_method_id: Id class — the reference number of the payout method the transfer was returned to,
            exactly as returned by the payout-method lookup.
        source_event_id: Id class — the reference number of the return record (the returned transfer as
            booked back to the method) that the charge belongs to, exactly as shown by the payout ledger
            lookup.
        amount: Fixed-format class — the return charge as a positive USD amount, 2 decimal places, already
            rounded as the charge policy prescribes; the tool stores it rounded to 2 decimal places and never
            changes it otherwise.

    Returns:
        A text rendering of a dictionary with these fields: payout_txn_id (string, the reference number of
        the new charge entry), payout_method_id (string, the method charged), source_event_id (string, the
        return record the charge belongs to), fee_type (string, always "returned_payout_fee"), amount (number,
        the USD charge booked, 2 decimal places), posted_date (string, YYYY-MM-DD, today) and status (string,
        "booked" on success).
    """
    owner_rows = ctx.find("payout_methods", payout_method_id=payout_method_id)
    rid = ctx.make_id("prc_", payout_method_id, source_event_id, amount)
    value = round(float(amount), 2)
    ctx.create("payout_transactions", rid, payout_txn_id=rid, payout_method_id=payout_method_id,
               customer_id=owner_rows[0].get("customer_id") if owner_rows else None,
               event_type="payout_fee_charged", posted_date=ctx.now()[:10], stay_id=None,
               installment_number=0, source_event_id=source_event_id, amount=value,
               fee_type="returned_payout_fee", deduction_type="none", credit_type="none",
               hold_reason="none", return_reason="none")
    return str({"payout_txn_id": rid, "payout_method_id": payout_method_id,
                "source_event_id": source_event_id, "fee_type": "returned_payout_fee", "amount": value,
                "posted_date": ctx.now()[:10], "status": "booked"})


@tool(owner="agent", rw="write")
def book_transfer_fee_e67ff494(ctx: ToolContext, payout_method_id: str, source_event_id: str,
                               amount: float) -> str:
    """Book the rail transfer fee of one transfer against the payout method it was sent to.

    A support agent uses this to post the transfer fee a payout rail charges for sending a transfer, whether
    the transfer settled or came back. One call adds one fee entry of kind transfer_fee to the payout
    method's ledger, dated today, naming the transfer it belongs to and carrying the amount given; the fee is
    taken out of the method's undisbursed balance, which drops by exactly that amount. Nothing else on the
    method or on the transfer changes. The host sees the fee as its own line in the payout history and on the
    next earnings statement. The call has succeeded when the receipt below comes back with status "booked".

    Args:
        payout_method_id: Id class — the reference number of the payout method the transfer was sent to,
            exactly as returned by the payout-method lookup.
        source_event_id: Id class — the reference number of the transfer record (a payout sent to the
            method) that the fee belongs to, exactly as shown by the payout ledger lookup.
        amount: Fixed-format class — the transfer fee as a positive USD amount, 2 decimal places, already
            rounded as the fee policy prescribes; the tool stores it rounded to 2 decimal places and never
            changes it otherwise.

    Returns:
        A text rendering of a dictionary with these fields: payout_txn_id (string, the reference number of
        the new fee entry), payout_method_id (string, the method charged), source_event_id (string, the
        transfer the fee belongs to), fee_type (string, always "transfer_fee"), amount (number, the USD fee
        booked, 2 decimal places), posted_date (string, YYYY-MM-DD, today) and status (string, "booked" on
        success).
    """
    owner_rows = ctx.find("payout_methods", payout_method_id=payout_method_id)
    rid = ctx.make_id("ptf_", payout_method_id, source_event_id, amount)
    value = round(float(amount), 2)
    ctx.create("payout_transactions", rid, payout_txn_id=rid, payout_method_id=payout_method_id,
               customer_id=owner_rows[0].get("customer_id") if owner_rows else None,
               event_type="payout_fee_charged", posted_date=ctx.now()[:10], stay_id=None,
               installment_number=0, source_event_id=source_event_id, amount=value,
               fee_type="transfer_fee", deduction_type="none", credit_type="none",
               hold_reason="none", return_reason="none")
    return str({"payout_txn_id": rid, "payout_method_id": payout_method_id,
                "source_event_id": source_event_id, "fee_type": "transfer_fee", "amount": value,
                "posted_date": ctx.now()[:10], "status": "booked"})


@tool(owner="user", rw="write")
def confirm_payout_resend_90576149(ctx: ToolContext, payout_method_id: str, host_account_id: str,
                                   source_event_id: str, amount: float) -> str:
    """The host confirms, in person in the host app, the re-send of money that came back from a returned
    transfer, to the payout method whose details they updated.

    The host uses this to send again the held balance of a reactivated payout method that holds money from a
    returned transfer. One call sends one transfer of the confirmed amount to the account on that
    payout method and records it in the method's payout history, dated today and naming the return it
    re-sends; the method's undisbursed balance drops by exactly that amount, and whatever stays in the
    balance waits for the next scheduled run. The host sees the re-send as sent in the payout history straight
    away; arrival follows the rail's processing time. The call has succeeded when the receipt below comes
    back with status "sent".

    Args:
        payout_method_id: Id class — the reference number of the payout method the money is sent to, as
            given to the host by the support agent from the payout-method lookup.
        host_account_id: Id class — the reference number of the host account the payout method belongs to,
            as given to the host by the support agent from the host-account lookup.
        source_event_id: Id class — the reference number of the return record being re-sent, as given to the
            host by the support agent from the payout ledger lookup.
        amount: Fixed-format class — the re-send amount the host confirms, a positive USD amount with 2
            decimal places, exactly as the support agent stated it; the tool stores it rounded to 2 decimal
            places.

    Returns:
        A text rendering of a dictionary with these fields: payout_txn_id (string, the reference number of
        the transfer), payout_method_id (string, the method paid), host_account_id (string, the host
        account), source_event_id (string, the return re-sent), amount (number, the USD amount sent, 2
        decimal places), posted_date (string, YYYY-MM-DD, today) and status (string, "sent" on success).
    """
    owner_rows = ctx.find("payout_methods", payout_method_id=payout_method_id)
    rid = ctx.make_id("prs_", payout_method_id, host_account_id, source_event_id, amount)
    value = round(float(amount), 2)
    ctx.create("payout_transactions", rid, payout_txn_id=rid, payout_method_id=payout_method_id,
               customer_id=owner_rows[0].get("customer_id") if owner_rows else None,
               event_type="payout_sent", posted_date=ctx.now()[:10], stay_id=None, installment_number=0,
               source_event_id=source_event_id, amount=value, fee_type="none", deduction_type="none",
               credit_type="none", hold_reason="none", return_reason="none")
    return str({"payout_txn_id": rid, "payout_method_id": payout_method_id,
                "host_account_id": host_account_id, "source_event_id": source_event_id, "amount": value,
                "posted_date": ctx.now()[:10], "status": "sent"})

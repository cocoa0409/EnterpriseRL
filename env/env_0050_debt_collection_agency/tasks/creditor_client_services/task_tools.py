"""Hidden task tools for creditor_client_services (Contingency Placement Agreements).

Each tool lands exactly one atomic booking on a creditor client's placement agreement and keeps
the agreement's running balance in step with the client ledger. No tool checks eligibility,
prerequisites or amounts: the figures passed in are worked out by the agent from the published
rules and the records.
"""

from erlbench import ToolContext, tool


@tool(owner="agent", rw="write")
def book_early_termination_charge_4cc8362c(ctx: ToolContext, agreement_id: str, notice_date: str,
                                           charge_amount: float) -> str:
    """Book the early-termination charge on a creditor client's contingency placement agreement.
    One call adds one early-termination charge entry to the agreement's client money history,
    dated the day the client's termination notice was received, and raises the fees the client
    owes Ridgeline on that agreement by the same amount. The charge then appears in the
    agreement's money history and in its fees owed. Success is a receipt naming the new entry.

    Args:
        agreement_id: Id class — the placement agreement reference number (agreement id) of the creditor client's
            contingency agreement being charged, read from the placement agreement lookup.
        notice_date: Fixed-format class — the date the client's termination notice was received,
            written YYYY-MM-DD (calendar date, no time zone); it becomes the date of the charge entry.
        charge_amount: Fixed-format class — the early-termination charge, in USD, 2 decimal places, always positive;
            rounded to the nearest cent (2 decimal places) before it is passed.

    Returns:
        A text receipt of a dictionary with: entry_id (string, the reference of the new client
        money entry), agreement_id (string, the agreement charged), entry_type (string, always
        client_early_termination_fee_assessed), amount (number, USD to 2 decimal places, the charge
        booked), entry_date (string, YYYY-MM-DD, the notice date), fees_owed_after (number, USD to
        2 decimal places, the agreement's fees owed once the charge is added). Receiving the
        receipt means the charge is booked.
    """
    amount = round(float(charge_amount), 2)
    rid = ctx.make_id("ctx_", agreement_id, notice_date, amount)
    agreement = ctx.find("client_agreements", agreement_id=agreement_id)
    row = agreement[0] if agreement else {}
    ctx.create("client_ledger", rid, client_txn_id=rid, agreement_id=agreement_id,
               customer_id=row.get("customer_id", ""),
               event_type="client_early_termination_fee_assessed", amount=amount,
               txn_date=str(notice_date)[:10])
    owed = round(float(row.get("fees_receivable") or 0) + amount, 2)
    ctx.update("client_agreements", agreement_id, fees_receivable=owed)
    return str({"entry_id": rid, "agreement_id": agreement_id,
                "entry_type": "client_early_termination_fee_assessed", "amount": amount,
                "entry_date": str(notice_date)[:10], "fees_owed_after": owed})


@tool(owner="user", rw="write")
def pay_closing_fee_settlement_180c3708(ctx: ToolContext, agreement_id: str, payment_amount: float) -> str:
    """The creditor client pays its closing fee settlement on a contingency placement agreement
    for which it has given termination notice. One call records one fee payment from the client
    against that agreement, dated today, and lowers the fees the client owes Ridgeline on the
    agreement by the amount paid. The client receives a payment confirmation reference it can
    quote to its accounts-payable team. Success is a receipt carrying that reference.

    Args:
        agreement_id: Id class — the placement agreement reference number (agreement id) of the agreement being
            settled, which the representative reads from the placement agreement lookup and gives
            to the client.
        payment_amount: Fixed-format class — the amount the client pays, in USD, 2 decimal places, always positive;
            rounded to the nearest cent (2 decimal places), as the representative states it.

    Returns:
        A text receipt of a dictionary with: entry_id (string, the reference of the new client
        money entry), agreement_id (string, the agreement paid on), entry_type (string, always
        client_fee_payment_received), amount (number, USD to 2 decimal places, the amount paid),
        payment_ref (string, the payment confirmation reference issued for this payment),
        entry_date (string, YYYY-MM-DD, today), fees_owed_after (number, USD to 2 decimal places,
        the agreement's fees owed after the payment). Receiving the receipt means the payment is
        recorded.
    """
    amount = round(float(payment_amount), 2)
    rid = ctx.make_id("ctx_", agreement_id, "closing", amount)
    ref = "CLS-" + rid[-8:].upper()
    agreement = ctx.find("client_agreements", agreement_id=agreement_id)
    row = agreement[0] if agreement else {}
    today = ctx.now()[:10]
    ctx.create("client_ledger", rid, client_txn_id=rid, agreement_id=agreement_id,
               customer_id=row.get("customer_id", ""), event_type="client_fee_payment_received",
               amount=amount, txn_date=today, payment_ref=ref)
    owed = round(float(row.get("fees_receivable") or 0) - amount, 2)
    ctx.update("client_agreements", agreement_id, fees_receivable=owed)
    return str({"entry_id": rid, "agreement_id": agreement_id,
                "entry_type": "client_fee_payment_received", "amount": amount,
                "payment_ref": ref, "entry_date": today, "fees_owed_after": owed})


@tool(owner="agent", rw="write")
def assess_invoice_late_charge_7a6464d6(ctx: ToolContext, agreement_id: str, invoice_number: str,
                                        late_charge_amount: float) -> str:
    """Book one month's late charge on a past-due fee invoice of a creditor client's contingency
    placement agreement. One call adds one late-charge entry, dated today and tied to the named
    invoice, to the agreement's client money history, and raises the fees the client owes Ridgeline
    on that agreement by the same amount. The charge then appears in the agreement's money history
    under that invoice and in its fees owed. Success is a receipt naming the new entry.

    Args:
        agreement_id: Id class — the placement agreement reference number (agreement id) of the
            agreement the invoice was raised on, read from the placement agreement lookup.
        invoice_number: Verbatim class — the fee invoice number exactly as it appears on the
            invoice entry in the agreement's client money history (and as the client reads it from
            the invoice), copied character for character with its letters, digits and hyphen, no
            change of any kind (verbatim).
        late_charge_amount: Fixed-format class — the month's late charge, in USD, 2 decimal places,
            always positive; rounded to the nearest cent (2 decimal places) before it is passed.

    Returns:
        A text receipt of a dictionary with: entry_id (string, the reference of the new client
        money entry), agreement_id (string, the agreement charged), invoice_number (string, the
        invoice the charge is tied to), entry_type (string, always client_late_charge_assessed),
        amount (number, USD to 2 decimal places, the charge booked), entry_date (string,
        YYYY-MM-DD, today), fees_owed_after (number, USD to 2 decimal places, the agreement's fees
        owed once the charge is added). Receiving the receipt means the late charge is booked.
    """
    amount = round(float(late_charge_amount), 2)
    rid = ctx.make_id("ctx_", agreement_id, invoice_number, amount)
    agreement = ctx.find("client_agreements", agreement_id=agreement_id)
    row = agreement[0] if agreement else {}
    today = ctx.now()[:10]
    ctx.create("client_ledger", rid, client_txn_id=rid, agreement_id=agreement_id,
               customer_id=row.get("customer_id", ""), event_type="client_late_charge_assessed",
               amount=amount, txn_date=today, invoice_number=invoice_number)
    owed = round(float(row.get("fees_receivable") or 0) + amount, 2)
    ctx.update("client_agreements", agreement_id, fees_receivable=owed)
    return str({"entry_id": rid, "agreement_id": agreement_id, "invoice_number": invoice_number,
                "entry_type": "client_late_charge_assessed", "amount": amount,
                "entry_date": today, "fees_owed_after": owed})


@tool(owner="user", rw="write")
def pay_past_due_invoice_8492adb5(ctx: ToolContext, agreement_id: str, invoice_number: str,
                                  payment_amount: float) -> str:
    """The creditor client pays off one past-due fee invoice on its contingency placement
    agreement. One call records one fee payment from the client, dated today and applied to the
    invoice the client names, and lowers the fees the client owes Ridgeline on the agreement by the
    amount paid. The client receives a payment confirmation reference it can quote to its
    accounts-payable team. Success is a receipt carrying that reference.

    Args:
        agreement_id: Id class — the placement agreement reference number (agreement id) of the
            agreement the invoice belongs to, which the representative reads from the placement
            agreement lookup and gives to the client.
        invoice_number: Verbatim class — the fee invoice number the client names for the payment,
            exactly as the client reads it from its invoice, copied character for character with
            its letters, digits and hyphen, no change of any kind (verbatim).
        payment_amount: Fixed-format class — the amount the client pays, in USD, 2 decimal places,
            always positive; rounded to the nearest cent (2 decimal places), as the representative states it.

    Returns:
        A text receipt of a dictionary with: entry_id (string, the reference of the new client
        money entry), agreement_id (string, the agreement paid on), invoice_number (string, the
        invoice the payment is applied to), entry_type (string, always client_fee_payment_received),
        amount (number, USD to 2 decimal places, the amount paid), payment_ref (string, the payment
        confirmation reference issued for this payment), entry_date (string, YYYY-MM-DD, today),
        fees_owed_after (number, USD to 2 decimal places, the agreement's fees owed after the
        payment). Receiving the receipt means the payment is recorded.
    """
    amount = round(float(payment_amount), 2)
    rid = ctx.make_id("ctx_", agreement_id, invoice_number, "payoff", amount)
    ref = "INP-" + rid[-8:].upper()
    agreement = ctx.find("client_agreements", agreement_id=agreement_id)
    row = agreement[0] if agreement else {}
    today = ctx.now()[:10]
    ctx.create("client_ledger", rid, client_txn_id=rid, agreement_id=agreement_id,
               customer_id=row.get("customer_id", ""), event_type="client_fee_payment_received",
               amount=amount, txn_date=today, invoice_number=invoice_number, payment_ref=ref)
    owed = round(float(row.get("fees_receivable") or 0) - amount, 2)
    ctx.update("client_agreements", agreement_id, fees_receivable=owed)
    return str({"entry_id": rid, "agreement_id": agreement_id, "invoice_number": invoice_number,
                "entry_type": "client_fee_payment_received", "amount": amount,
                "payment_ref": ref, "entry_date": today, "fees_owed_after": owed})

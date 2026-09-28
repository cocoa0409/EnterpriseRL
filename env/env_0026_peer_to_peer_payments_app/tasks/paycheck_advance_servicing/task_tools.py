"""Hidden task tools of the paycheck_advance_servicing difficulty (category advance).

Each tool performs one atomic write on the Pocketwire Advance line it is given and keeps the
line's owed amount in step with the ledger rows it books. No tool checks eligibility, timing,
prior entries or any other policy condition, and none computes the amounts it is handed.
"""

from erlbench import ToolContext, tool


@tool(owner="agent", rw="write")
def grant_payroll_delay_relief_50112cf3(ctx: ToolContext, advance_line_id: str, source_txn_id: str,
                                        amount: float) -> str:
    """Book a payroll-delay relief on one late fee of a Pocketwire Advance line: a fee waiver
    with the reason courtesy, pointing at the late fee it relieves, for the amount given. The
    waiver is recorded on the line's activity with today's date, and the amount the customer
    owes on the line goes down by the amount waived (below zero when the fee had already been
    repaid, leaving a credit on the line). The customer sees the waiver in the advance activity
    and the lower amount owed straight away.

    Args:
        advance_line_id: Id class — the reference number of the customer's advance line, as
            returned by the advance line lookup.
        source_txn_id: Id class — the reference number of the late fee entry being relieved, as
            returned by the advance activity lookup for that line.
        amount: Fixed-format class — the relief amount in USD, 2 decimal places, a positive
            number rounded to the cent before it is passed; it is stored exactly as given.

    Returns:
        A text rendering of a dictionary confirming the booking: waiver_entry_id (reference
        number of the new waiver entry), advance_line_id (the line), waived_fee_entry_id (the late
        fee entry relieved), waiver_reason (always courtesy), amount_waived (USD, 2 decimal
        places), entry_date (YYYY-MM-DD, today) and outstanding_balance (USD, 2 decimal places,
        what the customer owes on the line after the waiver). A returned waiver_entry_id means the
        relief is booked.
    """
    line = ctx.find("advance_lines", advance_line_id=advance_line_id)[0]
    rid = ctx.make_id("advw_", advance_line_id, source_txn_id, amount)
    today = ctx.now()[:10]
    value = round(float(amount), 2)
    ctx.create("advance_ledger", rid, advance_entry_id=rid, advance_line_id=advance_line_id,
               customer_id=line.get("customer_id"), event_type="advance_fee_waiver",
               advance_reference="", entry_date=today, disbursed_at="", amount=value,
               source_txn_id=source_txn_id, fee_type="not_applicable", fee_period=0,
               delivery_destination="not_applicable", delivery_speed="not_applicable",
               due_date="", new_due_date="", extension_type="not_applicable",
               repayment_method="not_applicable", repayment_attempt=0, waiver_reason="courtesy")
    owed = round(float(line.get("outstanding_balance") or 0) - value, 2)
    ctx.update("advance_lines", advance_line_id, outstanding_balance=owed)
    return str({"waiver_entry_id": rid, "advance_line_id": advance_line_id,
                "waived_fee_entry_id": source_txn_id, "waiver_reason": "courtesy",
                "amount_waived": value, "entry_date": today, "outstanding_balance": owed})


@tool(owner="user", rw="write")
def request_advance_00c9f515(ctx: ToolContext, advance_line_id: str, amount: float, due_date: str,
                             flat_fee: float) -> str:
    """The customer requests a new advance on their Pocketwire Advance line, delivered by
    standard delivery to their external debit card. One call books the advance with today's
    date and the current moment as its disbursement time, the due date given, and its flat
    advance fee for the amount given; the amount the customer owes on the line goes up by the
    advance plus that fee. The customer sees the new advance, its reference, its fee and its due
    date in the app at once.

    Args:
        advance_line_id: Id class — the reference number of the customer's advance line, as
            returned by the advance line lookup.
        amount: Fixed-format class — the advance principal in USD, 2 decimal places, a whole
            multiple of the tier's advance increment; it is stored exactly as given.
        due_date: Fixed-format class — the repayment due date of the new advance, a calendar
            date written YYYY-MM-DD (Eastern Time).
        flat_fee: Fixed-format class — the flat advance fee in USD, 2 decimal places, rounded to
            the cent before it is passed; it is stored exactly as given.

    Returns:
        A text rendering of a dictionary confirming the advance: advance_entry_id (reference
        number of the advance), advance_reference (the advance reference shown in the app),
        amount (USD, 2 decimal places), flat_fee (USD, 2 decimal places), fee_entry_id (reference
        number of the fee entry), due_date (YYYY-MM-DD), delivery (always standard delivery to the
        external debit card) and outstanding_balance (USD, 2 decimal places, what the customer
        owes on the line afterwards). A returned advance_reference means the advance is booked.
    """
    line = ctx.find("advance_lines", advance_line_id=advance_line_id)[0]
    principal = round(float(amount), 2)
    fee = round(float(flat_fee), 2)
    rid = ctx.make_id("adv_", advance_line_id, principal, due_date, fee)
    reference = "PWA-" + rid[-8:].upper()
    today = ctx.now()[:10]
    moment = ctx.now()[:19].replace(" ", "T")
    ctx.create("advance_ledger", rid, advance_entry_id=rid, advance_line_id=advance_line_id,
               customer_id=line.get("customer_id"), event_type="advance_disbursement",
               advance_reference=reference, entry_date=today, disbursed_at=moment, amount=principal,
               source_txn_id="", fee_type="not_applicable", fee_period=0,
               delivery_destination="external_debit_card", delivery_speed="standard",
               due_date=due_date, new_due_date="", extension_type="not_applicable",
               repayment_method="not_applicable", repayment_attempt=0, waiver_reason="not_applicable")
    fid = ctx.make_id("advf_", rid, "advance_fee")
    ctx.create("advance_ledger", fid, advance_entry_id=fid, advance_line_id=advance_line_id,
               customer_id=line.get("customer_id"), event_type="advance_fee", advance_reference="",
               entry_date=today, disbursed_at="", amount=fee, source_txn_id=rid,
               fee_type="advance_fee", fee_period=0, delivery_destination="not_applicable",
               delivery_speed="not_applicable", due_date="", new_due_date="",
               extension_type="not_applicable", repayment_method="not_applicable",
               repayment_attempt=0, waiver_reason="not_applicable")
    owed = round(float(line.get("outstanding_balance") or 0) + principal + fee, 2)
    ctx.update("advance_lines", advance_line_id, outstanding_balance=owed)
    return str({"advance_entry_id": rid, "advance_reference": reference, "amount": principal,
                "flat_fee": fee, "fee_entry_id": fid, "due_date": due_date,
                "delivery": "standard delivery to the external debit card",
                "outstanding_balance": owed})


@tool(owner="agent", rw="write")
def assess_late_fee_a649c20a(ctx: ToolContext, advance_line_id: str, source_txn_id: str, fee_period: int,
                             amount: float) -> str:
    """Book one late fee on an advance of a Pocketwire Advance line for the late-fee period given,
    with today's date and the amount given; the amount the customer owes on the line goes up by
    that fee. The customer sees the late fee, its period number and the higher amount owed in the
    advance activity straight away.

    Args:
        advance_line_id: Id class — the reference number of the customer's advance line, as
            returned by the advance line lookup.
        source_txn_id: Id class — the reference number of the advance the late fee belongs to
            (its disbursement entry), as returned by the advance activity lookup for that line.
        fee_period: Fixed-format class — the number of the late-fee period being charged, an
            integer 1 or more (1 for the first full late-fee period after the grace period).
        amount: Fixed-format class — the late fee in USD, 2 decimal places, rounded to the cent
            before it is passed; it is stored exactly as given.

    Returns:
        A text rendering of a dictionary confirming the booking: fee_entry_id (reference number of
        the new late fee entry), advance_line_id (the line), advance_entry_id (the advance charged),
        fee_type (always late_fee), fee_period (integer), amount (USD, 2 decimal places),
        entry_date (YYYY-MM-DD, today) and outstanding_balance (USD, 2 decimal places, what the
        customer owes on the line afterwards). A returned fee_entry_id means the fee is booked.
    """
    line = ctx.find("advance_lines", advance_line_id=advance_line_id)[0]
    value = round(float(amount), 2)
    period = int(fee_period)
    rid = ctx.make_id("advl_", advance_line_id, source_txn_id, period, value)
    today = ctx.now()[:10]
    ctx.create("advance_ledger", rid, advance_entry_id=rid, advance_line_id=advance_line_id,
               customer_id=line.get("customer_id"), event_type="advance_fee", advance_reference="",
               entry_date=today, disbursed_at="", amount=value, source_txn_id=source_txn_id,
               fee_type="late_fee", fee_period=period, delivery_destination="not_applicable",
               delivery_speed="not_applicable", due_date="", new_due_date="",
               extension_type="not_applicable", repayment_method="not_applicable",
               repayment_attempt=0, waiver_reason="not_applicable")
    owed = round(float(line.get("outstanding_balance") or 0) + value, 2)
    ctx.update("advance_lines", advance_line_id, outstanding_balance=owed)
    return str({"fee_entry_id": rid, "advance_line_id": advance_line_id,
                "advance_entry_id": source_txn_id, "fee_type": "late_fee", "fee_period": period,
                "amount": value, "entry_date": today, "outstanding_balance": owed})


@tool(owner="user", rw="write")
def repay_advance_by_card_db2e846d(ctx: ToolContext, advance_line_id: str, source_txn_id: str,
                                   amount: float) -> str:
    """The customer makes a manual repayment on one advance of their Pocketwire Advance line from
    their external debit card, for the amount given, dated today. The repayment is recorded
    against that advance and the amount the customer owes on the line goes down by the amount
    repaid. The customer sees the repayment and the lower amount owed in the app at once.

    Args:
        advance_line_id: Id class — the reference number of the customer's advance line, as
            returned by the advance line lookup.
        source_txn_id: Id class — the reference number of the advance being repaid (its
            disbursement entry), as returned by the advance activity lookup for that line.
        amount: Fixed-format class — the repayment in USD, 2 decimal places, rounded to the cent
            before it is passed; it is taken from the card and stored exactly as given.

    Returns:
        A text rendering of a dictionary confirming the repayment: repayment_entry_id (reference
        number of the new repayment entry), advance_line_id (the line), advance_entry_id (the
        advance repaid), repayment_method (always manual_debit_card), amount (USD, 2 decimal
        places), entry_date (YYYY-MM-DD, today) and outstanding_balance (USD, 2 decimal places,
        what the customer owes on the line afterwards). A returned repayment_entry_id means the
        repayment is recorded.
    """
    line = ctx.find("advance_lines", advance_line_id=advance_line_id)[0]
    value = round(float(amount), 2)
    rid = ctx.make_id("advr_", advance_line_id, source_txn_id, value)
    today = ctx.now()[:10]
    ctx.create("advance_ledger", rid, advance_entry_id=rid, advance_line_id=advance_line_id,
               customer_id=line.get("customer_id"), event_type="advance_repayment", advance_reference="",
               entry_date=today, disbursed_at="", amount=value, source_txn_id=source_txn_id,
               fee_type="not_applicable", fee_period=0, delivery_destination="not_applicable",
               delivery_speed="not_applicable", due_date="", new_due_date="",
               extension_type="not_applicable", repayment_method="manual_debit_card",
               repayment_attempt=0, waiver_reason="not_applicable")
    owed = round(float(line.get("outstanding_balance") or 0) - value, 2)
    ctx.update("advance_lines", advance_line_id, outstanding_balance=owed)
    return str({"repayment_entry_id": rid, "advance_line_id": advance_line_id,
                "advance_entry_id": source_txn_id, "repayment_method": "manual_debit_card",
                "amount": value, "entry_date": today, "outstanding_balance": owed})

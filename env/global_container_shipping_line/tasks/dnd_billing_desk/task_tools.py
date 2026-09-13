"""Hidden task tools of the dnd_billing_desk difficulty (Aurelia Hanse Line demurrage and detention desk).

Each tool performs one atomic booking on a per-container free-time record. The agent works out every
amount, day count and date from the published rules and the records, and passes it in; no tool computes,
checks or refuses on a business condition.
"""

from erlbench import ToolContext, tool


@tool(owner="agent", rw="write")
def book_detention_invoice_dba94f21(ctx: ToolContext, dnd_id: str, chargeable_days: int,
                                    period_start_date: str, period_end_date: str, amount_usd: float) -> str:
    """Book the final detention charge of one container's free-time record as an invoice line dated today.

    The desk issues the detention line of the record's final demurrage and detention invoice: a new
    detention invoice entry is written on the record with the detention days billed, the first and last
    detention day covered and the amount, the amount is added to the balance the billed party owes on the
    record, and the record shows as invoiced. The invoice entry is import detention for an import record
    and export detention for an export record. Success is confirmed by a receipt naming the new invoice
    reference; the customer can then see the detention line and the higher balance on the record.

    Args:
        dnd_id: Id class — reference number of the free-time record being invoiced, as returned by the free-time record lookup.
        chargeable_days: Fixed-format class — detention days billed beyond free time, integer, calendar days; the stored field reads integer, calendar days; 0 on non-invoice rows (unit: calendar days).
        period_start_date: Fixed-format class — first detention day covered by the line, written YYYY-MM-DD.
        period_end_date: Fixed-format class — last detention day covered by the line, written YYYY-MM-DD.
        amount_usd: Fixed-format class — detention amount of the line, unit USD, a positive figure given to 2 decimal places (rounded to the cent before it is passed).

    Returns:
        A confirmation sentence of the form "Detention invoice line <invoice reference> booked on record <dnd_id>: <days> day(s) from <start> to <end>, USD <amount>; balance due now USD <balance>." The invoice reference is the id customers quote for this line; the balance is the record's outstanding amount in USD to 2 decimal places after the line. A message starting with "Error:" means no record exists under that reference and nothing was booked.
    """
    found = ctx.find("dnd_free_time", dnd_id=dnd_id)
    rec = found[0] if found else None
    if rec is None:
        return f"Error: no free-time record {dnd_id}."
    days = int(chargeable_days)
    amount = round(float(amount_usd), 2)
    charge_type = "import_detention" if rec.get("direction") == "import" else "export_detention"
    rid = ctx.make_id("dle_", dnd_id, "detention", days, period_start_date, period_end_date, amount)
    ctx.create("dnd_ledger", rid, dnd_event_id=rid, dnd_id=dnd_id, customer_id=rec.get("customer_id"),
               event_type="dnd_detention_invoiced", event_date=ctx.now()[:10], charge_type=charge_type,
               amount_usd=amount, chargeable_days=days, period_start_date=period_start_date,
               period_end_date=period_end_date, target_variant="not_applicable", waiver_reason="none",
               payment_reference="", reference_event_id=None, dispute_id=None)
    balance = round(float(rec.get("balance_due_usd") or 0) + amount, 2)
    ctx.update("dnd_free_time", dnd_id, status="invoiced", balance_due_usd=balance)
    return (f"Detention invoice line {rid} booked on record {dnd_id}: {days} day(s) from {period_start_date} "
            f"to {period_end_date}, USD {amount:.2f}; balance due now USD {balance:.2f}.")


@tool(owner="agent", rw="write")
def book_demurrage_invoice_a2ad21e7(ctx: ToolContext, dnd_id: str, chargeable_days: int,
                                    period_start_date: str, period_end_date: str, amount_usd: float) -> str:
    """Book the final demurrage charge of one container's free-time record as an invoice line dated today.

    The desk issues the demurrage line of the record's final demurrage and detention invoice: a new
    demurrage invoice entry is written on the record with the demurrage days billed, the first and last
    demurrage day covered and the amount, the amount is added to the balance the billed party owes on the
    record, and the record shows as invoiced. The invoice entry is import demurrage for an import record
    and export demurrage for an export record. Success is confirmed by a receipt naming the new invoice
    reference; the customer can then see the demurrage line and the higher balance on the record.

    Args:
        dnd_id: Id class — reference number of the free-time record being invoiced, as returned by the free-time record lookup.
        chargeable_days: Fixed-format class — demurrage days billed beyond free time, integer, calendar days; the stored field reads integer, calendar days; 0 on non-invoice rows (unit: calendar days).
        period_start_date: Fixed-format class — first demurrage day covered by the line, written YYYY-MM-DD.
        period_end_date: Fixed-format class — last demurrage day covered by the line, written YYYY-MM-DD.
        amount_usd: Fixed-format class — demurrage amount of the line, unit USD, a positive figure given to 2 decimal places (rounded to the cent before it is passed).

    Returns:
        A confirmation sentence of the form "Demurrage invoice line <invoice reference> booked on record <dnd_id>: <days> day(s) from <start> to <end>, USD <amount>; balance due now USD <balance>." The invoice reference is the id customers quote for this line and the id later waivers and credits refer to; the balance is the record's outstanding amount in USD to 2 decimal places after the line. A message starting with "Error:" means no record exists under that reference and nothing was booked.
    """
    found = ctx.find("dnd_free_time", dnd_id=dnd_id)
    rec = found[0] if found else None
    if rec is None:
        return f"Error: no free-time record {dnd_id}."
    days = int(chargeable_days)
    amount = round(float(amount_usd), 2)
    charge_type = "import_demurrage" if rec.get("direction") == "import" else "export_demurrage"
    rid = ctx.make_id("dle_", dnd_id, "demurrage", days, period_start_date, period_end_date, amount)
    ctx.create("dnd_ledger", rid, dnd_event_id=rid, dnd_id=dnd_id, customer_id=rec.get("customer_id"),
               event_type="dnd_demurrage_invoiced", event_date=ctx.now()[:10], charge_type=charge_type,
               amount_usd=amount, chargeable_days=days, period_start_date=period_start_date,
               period_end_date=period_end_date, target_variant="not_applicable", waiver_reason="none",
               payment_reference="", reference_event_id=None, dispute_id=None)
    balance = round(float(rec.get("balance_due_usd") or 0) + amount, 2)
    ctx.update("dnd_free_time", dnd_id, status="invoiced", balance_due_usd=balance)
    return (f"Demurrage invoice line {rid} booked on record {dnd_id}: {days} day(s) from {period_start_date} "
            f"to {period_end_date}, USD {amount:.2f}; balance due now USD {balance:.2f}.")


@tool(owner="agent", rw="write")
def grant_goodwill_waiver_e03c98b1(ctx: ToolContext, dnd_id: str, customer_id: str, reference_event_id: str,
                                   amount_usd: float) -> str:
    """Grant a commercial goodwill waiver against one demurrage and detention invoice line and take it off the balance owed.

    The desk writes one goodwill waiver entry dated today on the free-time record, recorded with the
    reason commercial goodwill and pointing at the invoice line it reduces, and lowers the balance the
    billed party owes on the record by the amount waived. Success is confirmed by a receipt naming the
    waiver entry; the customer then sees the waiver against that invoice line and the lower balance.

    Args:
        dnd_id: Id class — reference number of the free-time record carrying the invoice line, as returned by the free-time record lookup.
        customer_id: Id class — customer reference number of the billed party, as returned by the customer profile lookup.
        reference_event_id: Id class — invoice reference id of the invoice line being reduced, as returned by the account entry lookup or by the receipt of the line's booking.
        amount_usd: Fixed-format class — amount waived, unit USD, a positive figure given to 2 decimal places.

    Returns:
        A confirmation sentence of the form "Goodwill waiver <waiver reference> of USD <amount> booked against invoice line <invoice reference> on record <dnd_id>; balance due now USD <balance>." The balance is the record's outstanding amount in USD to 2 decimal places after the waiver. A message starting with "Error:" means no record exists under that reference and nothing was booked.
    """
    found = ctx.find("dnd_free_time", dnd_id=dnd_id)
    rec = found[0] if found else None
    if rec is None:
        return f"Error: no free-time record {dnd_id}."
    amount = round(float(amount_usd), 2)
    rid = ctx.make_id("dlw_", dnd_id, customer_id, reference_event_id, "commercial_goodwill", amount)
    ctx.create("dnd_ledger", rid, dnd_event_id=rid, dnd_id=dnd_id, customer_id=customer_id,
               event_type="dnd_charge_waived", event_date=ctx.now()[:10], charge_type="waiver",
               amount_usd=amount, chargeable_days=0, period_start_date="", period_end_date="",
               target_variant="not_applicable", waiver_reason="commercial_goodwill", payment_reference="",
               reference_event_id=reference_event_id, dispute_id=None)
    balance = round(float(rec.get("balance_due_usd") or 0) - amount, 2)
    ctx.update("dnd_free_time", dnd_id, balance_due_usd=balance)
    return (f"Goodwill waiver {rid} of USD {amount:.2f} booked against invoice line {reference_event_id} on "
            f"record {dnd_id}; balance due now USD {balance:.2f}.")


@tool(owner="user", rw="write")
def pay_dnd_balance_a831ef2f(ctx: ToolContext, dnd_id: str, payment_reference: str, amount_usd: float) -> str:
    """Pay money owed on one container's demurrage and detention record by card, as the billed party's own payment.

    The customer authorises a card payment of the stated amount against the free-time record: one
    payment entry dated today is written on the record with the customer's own payment reference, and the
    balance owed on the record goes down by the amount paid. Success is confirmed by a receipt naming the
    payment entry; the customer then sees the payment and the remaining balance on the record.

    Args:
        dnd_id: Id class — reference number of the free-time record being paid, as given to the customer by the desk from the free-time record lookup.
        payment_reference: Verbatim class — the payment reference the customer quotes for this payment, copied character for character exactly as the customer states it, preserving letters, digits and punctuation with no translation, normalisation, summarising, addition or deletion (verbatim).
        amount_usd: Fixed-format class — amount paid, unit USD, a positive figure given to 2 decimal places.

    Returns:
        A confirmation sentence of the form "Card payment <payment entry reference> of USD <amount> with reference <payment_reference> applied to record <dnd_id>; balance due now USD <balance>." The balance is the record's outstanding amount in USD to 2 decimal places after the payment. A message starting with "Error:" means no record exists under that reference and nothing was paid.
    """
    found = ctx.find("dnd_free_time", dnd_id=dnd_id)
    rec = found[0] if found else None
    if rec is None:
        return f"Error: no free-time record {dnd_id}."
    amount = round(float(amount_usd), 2)
    rid = ctx.make_id("dlp_", dnd_id, payment_reference, amount)
    ctx.create("dnd_ledger", rid, dnd_event_id=rid, dnd_id=dnd_id, customer_id=rec.get("customer_id"),
               event_type="dnd_payment_received", event_date=ctx.now()[:10], charge_type="payment",
               amount_usd=amount, chargeable_days=0, period_start_date="", period_end_date="",
               target_variant="not_applicable", waiver_reason="none", payment_reference=payment_reference,
               reference_event_id=None, dispute_id=None)
    balance = round(float(rec.get("balance_due_usd") or 0) - amount, 2)
    ctx.update("dnd_free_time", dnd_id, balance_due_usd=balance)
    return (f"Card payment {rid} of USD {amount:.2f} with reference {payment_reference} applied to record "
            f"{dnd_id}; balance due now USD {balance:.2f}.")


@tool(owner="agent", rw="write")
def settle_dnd_record_d9ada3ba(ctx: ToolContext, dnd_id: str) -> str:
    """Close one container's demurrage and detention free-time record as settled with today's date.

    The desk marks the free-time record settled and stamps today as its settlement date; nothing is
    booked on the account and the balance shown is left as it stands. Success is confirmed by a receipt
    naming the record; the customer then sees the record as settled.

    Args:
        dnd_id: Id class — reference number of the free-time record being closed, as returned by the free-time record lookup.

    Returns:
        A confirmation sentence of the form "Record <dnd_id> settled on <YYYY-MM-DD> with balance due USD <balance>." The date is today's date and the balance is the record's outstanding amount in USD to 2 decimal places. A message starting with "Error:" means no record exists under that reference and nothing changed.
    """
    found = ctx.find("dnd_free_time", dnd_id=dnd_id)
    rec = found[0] if found else None
    if rec is None:
        return f"Error: no free-time record {dnd_id}."
    today = ctx.now()[:10]
    ctx.update("dnd_free_time", dnd_id, status="settled", settled_date=today)
    balance = round(float(rec.get("balance_due_usd") or 0), 2)
    return f"Record {dnd_id} settled on {today} with balance due USD {balance:.2f}."


@tool(owner="user", rw="write")
def lodge_dnd_dispute_1c3d36b3(ctx: ToolContext, dnd_id: str, invoice_event_id: str, dispute_ground: str,
                               disputed_amount_usd: float) -> str:
    """Lodge the billed party's own dispute against one demurrage and detention invoice line.

    The customer files a dispute on a single invoice line of a free-time record: one dispute is
    registered with the ground and the amount disputed, marked as submitted and stamped with the current
    time, and it waits for the desk's decision. Nothing is booked on the account by lodging. Success is
    confirmed by a receipt naming the new dispute reference, which the desk uses when it decides the
    dispute; the customer then sees the dispute as submitted.

    Args:
        dnd_id: Id class — reference number of the free-time record whose invoice line is disputed, as given to the customer by the desk from the free-time record lookup.
        invoice_event_id: Id class — invoice reference id of the single invoice line disputed, as given to the customer by the desk from the account entry lookup.
        dispute_ground: Enum class — the ground of the dispute; the allowed values are exactly: invoice_issued_late (the line was issued after the invoicing deadline), rate_misapplied (the day rates or the rate class billed are wrong), free_time_misapplied (the free days or the day count billed are wrong), incorrect_event_dates (the recorded movement dates themselves are contested), carrier_caused_delay (the days are blamed on a delay caused by the line), terminal_closure (the days are blamed on a closure of the terminal).
        disputed_amount_usd: Fixed-format class — the part of the invoice line disputed, unit USD, a positive figure given to 2 decimal places.

    Returns:
        A confirmation sentence of the form "Dispute <dispute reference> lodged on invoice line <invoice_event_id> of record <dnd_id>: ground <dispute_ground>, USD <amount> disputed, status submitted." The dispute reference is the id the desk quotes when it decides the dispute; the amount is in USD to 2 decimal places. A message starting with "Error:" means no record exists under that reference and nothing was lodged.
    """
    found = ctx.find("dnd_free_time", dnd_id=dnd_id)
    rec = found[0] if found else None
    if rec is None:
        return f"Error: no free-time record {dnd_id}."
    amount = round(float(disputed_amount_usd), 2)
    rid = ctx.make_id("dsp_", dnd_id, invoice_event_id, dispute_ground, amount)
    ctx.create("dnd_disputes", rid, dispute_id=rid, customer_id=rec.get("customer_id"), dnd_id=dnd_id,
               invoice_event_id=invoice_event_id, dispute_ground=dispute_ground, disputed_amount_usd=amount,
               outcome="submitted", created_at=ctx.now())
    return (f"Dispute {rid} lodged on invoice line {invoice_event_id} of record {dnd_id}: ground {dispute_ground}, "
            f"USD {amount:.2f} disputed, status submitted.")


@tool(owner="agent", rw="write")
def book_dispute_credit_515e844f(ctx: ToolContext, dnd_id: str, invoice_event_id: str, outcome: str,
                                 amount_usd: float) -> str:
    """Decide the latest dispute lodged against one demurrage and detention invoice line and book its credit against that line.

    The desk writes one dispute credit entry dated today on the free-time record, pointing at the
    disputed invoice line and at the dispute most recently lodged against that line, lowers the balance
    the billed party owes on the record by the amount credited, and records the decision on that dispute.
    The dispute is identified by the invoice line alone: the one with the latest lodging time among the
    disputes filed against the line, whatever outcome it currently carries, and the outcome passed
    replaces that outcome. Success is confirmed by a receipt naming the dispute decided and the
    credit entry; the customer then sees the dispute decided and the credit against the invoice line.

    Args:
        dnd_id: Id class — reference number of the free-time record carrying the disputed invoice line, as returned by the free-time record lookup.
        invoice_event_id: Id class — invoice reference id of the disputed invoice line, as returned by the account entry lookup.
        outcome: Enum class — the decision recorded on the dispute; the allowed values are exactly: upheld (the credit equals the whole amount disputed), partially_upheld (a credit is given but it is smaller than the amount disputed), denied (the dispute fails and no credit would be due), submitted (the dispute stays undecided), withdrawn (the customer took the dispute back).
        amount_usd: Fixed-format class — amount credited, unit USD, a positive figure given to 2 decimal places.

    Returns:
        A confirmation sentence of the form "Dispute <dispute reference> decided <outcome>; credit <credit entry reference> of USD <amount> booked against invoice line <invoice_event_id> on record <dnd_id>; balance due now USD <balance>." The dispute reference is the id of the latest dispute lodged against the line (the word none when the line carries no dispute); the balance is the record's outstanding amount in USD to 2 decimal places after the credit. A message starting with "Error:" means no record exists under that reference and nothing was booked.
    """
    found = ctx.find("dnd_free_time", dnd_id=dnd_id)
    rec = found[0] if found else None
    if rec is None:
        return f"Error: no free-time record {dnd_id}."
    amount = round(float(amount_usd), 2)
    lodged = ctx.find("dnd_disputes", dnd_id=dnd_id, invoice_event_id=invoice_event_id)
    latest = max(lodged, key=lambda d: str(d.get("created_at") or "")) if lodged else None
    dispute_id = latest.get("dispute_id") if latest else None
    rid = ctx.make_id("dlc_", dnd_id, invoice_event_id, outcome, amount)
    ctx.create("dnd_ledger", rid, dnd_event_id=rid, dnd_id=dnd_id, customer_id=rec.get("customer_id"),
               event_type="dnd_dispute_credited", event_date=ctx.now()[:10], charge_type="dispute_credit",
               amount_usd=amount, chargeable_days=0, period_start_date="", period_end_date="",
               target_variant="not_applicable", waiver_reason="none", payment_reference="",
               reference_event_id=invoice_event_id, dispute_id=dispute_id)
    if dispute_id:
        ctx.update("dnd_disputes", dispute_id, outcome=outcome)
    balance = round(float(rec.get("balance_due_usd") or 0) - amount, 2)
    ctx.update("dnd_free_time", dnd_id, balance_due_usd=balance)
    return (f"Dispute {dispute_id or 'none'} decided {outcome}; credit {rid} of USD {amount:.2f} booked against invoice line "
            f"{invoice_event_id} on record {dnd_id}; balance due now USD {balance:.2f}.")


@tool(owner="agent", rw="write")
def clear_late_invoice_2264ae48(ctx: ToolContext, dnd_id: str, customer_id: str, reference_event_id: str,
                                amount_usd: float) -> str:
    """Clear an invoice line that was issued too late to be collectible, by booking a late-invoice waiver against it.

    The desk writes one waiver entry dated today on the free-time record, recorded with the reason late
    invoice and pointing at the invoice line it clears, and lowers the balance the billed party owes on the
    record by the amount waived. Success is confirmed by a receipt naming the waiver entry; the customer
    then sees the late-invoice waiver against that line and the lower balance.

    Args:
        dnd_id: Id class — reference number of the free-time record carrying the invoice line, as returned by the free-time record lookup.
        customer_id: Id class — customer reference number of the billed party, as returned by the customer profile lookup.
        reference_event_id: Id class — invoice reference id of the invoice line being cleared, as returned by the account entry lookup.
        amount_usd: Fixed-format class — amount waived, unit USD, a positive figure given to 2 decimal places.

    Returns:
        A confirmation sentence of the form "Late-invoice waiver <waiver reference> of USD <amount> booked against invoice line <reference_event_id> on record <dnd_id>; balance due now USD <balance>." The balance is the record's outstanding amount in USD to 2 decimal places after the waiver. A message starting with "Error:" means no record exists under that reference and nothing was booked.
    """
    found = ctx.find("dnd_free_time", dnd_id=dnd_id)
    rec = found[0] if found else None
    if rec is None:
        return f"Error: no free-time record {dnd_id}."
    amount = round(float(amount_usd), 2)
    rid = ctx.make_id("dlw_", dnd_id, customer_id, reference_event_id, "late_invoice", amount)
    ctx.create("dnd_ledger", rid, dnd_event_id=rid, dnd_id=dnd_id, customer_id=customer_id,
               event_type="dnd_charge_waived", event_date=ctx.now()[:10], charge_type="waiver",
               amount_usd=amount, chargeable_days=0, period_start_date="", period_end_date="",
               target_variant="not_applicable", waiver_reason="late_invoice", payment_reference="",
               reference_event_id=reference_event_id, dispute_id=None)
    balance = round(float(rec.get("balance_due_usd") or 0) - amount, 2)
    ctx.update("dnd_free_time", dnd_id, balance_due_usd=balance)
    return (f"Late-invoice waiver {rid} of USD {amount:.2f} booked against invoice line {reference_event_id} on "
            f"record {dnd_id}; balance due now USD {balance:.2f}.")

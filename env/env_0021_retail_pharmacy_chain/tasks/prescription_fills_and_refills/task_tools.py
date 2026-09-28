"""Hidden task tools of the prescription_fills_and_refills difficulty (Kestrel Pharmacy, Prescriptions).

Each tool performs one atomic booking on the prescription fill ledger and is reached only through
unlock_* -> call_*; its name is published by the target_tool of one extended policy in
rx.extended.yaml. No tool checks any business condition: every eligibility, prerequisite and
amount is decided by the agent from the policy and the records before the call.
"""

from erlbench import ToolContext, tool


@tool(owner="agent", rw="write")
def dispense_strength_error_remake_b4449648(ctx: ToolContext, error_report_id: str, quantity_dispensed: int) -> str:
    """Dispense, at no charge, the correct-strength medication that answers a confirmed wrong-strength
    dispensing-error report, and book it on the prescription's fill ledger as a corrected remake.

    One call books one remake entry against the prescription and the fill that the report names: it
    records the units handed out, a patient pay of 0.00, today's date as the dispensing and ready date,
    and the store holding the prescription. No refill is consumed and the refill-eligible date is not
    touched. After the call the remake appears among the prescription's fill entries, linked to the
    report it answers, and is ready for pickup today.

    Args:
        error_report_id: Id class — the reference number of the confirmed dispensing-error report the
            remake answers, as returned by the dispensing-error report lookup for the prescription.
        quantity_dispensed: Fixed-format class — the number of correct-strength units dispensed on the
            remake, an integer count in integer dosage units (whole tablets or capsules), no decimals.

    Returns:
        A text rendering of a dictionary describing the booked remake: "remake_id" (text, the new
        fill-ledger reference of the remake), "error_report_id" (text, the report it answers),
        "prescription_id" (text, the prescription it is booked on), "quantity_dispensed" (integer
        dosage units handed out), "patient_pay_usd" (number, always 0.0), "ready_date" (YYYY-MM-DD,
        today) and "status" (text, "remake_booked" when the entry was written).
    """
    report = (ctx.find("rx_error_reports", error_report_id=error_report_id) or [{}])[0]
    rx = (ctx.find("rx_prescriptions", prescription_id=report.get("prescription_id", "")) or [{}])[0]
    rid = ctx.make_id("rxf_", error_report_id, quantity_dispensed)
    today = ctx.now()[:10]
    ctx.create("rx_fills", rid, fill_id=rid, prescription_id=report.get("prescription_id"),
               customer_id=report.get("customer_id"), event_type="rx_error_remake", event_date=today,
               source_fill_id=report.get("fill_id"), error_report_id=error_report_id,
               quantity_dispensed=int(quantity_dispensed), patient_pay_usd=0.0, payment_basis="no_charge",
               ready_date=today, store_id=rx.get("store_id"))
    return str({"remake_id": rid, "error_report_id": error_report_id,
                "prescription_id": report.get("prescription_id"), "quantity_dispensed": int(quantity_dispensed),
                "patient_pay_usd": 0.0, "ready_date": today, "status": "remake_booked"})


@tool(owner="user", rw="write")
def decline_owed_balance_20c85924(ctx: ToolContext, source_fill_id: str, refund_usd: float) -> str:
    """Let the patient decline, in person, the units Kestrel still owes on a prescription dispensed short,
    and take back the credit for them.

    One call cancels the named owed balance for its full owed units: it books a balance cancellation
    entry on the prescription's fill ledger that names the owed-balance entry, records today's date,
    the units cancelled and the credit returned to the patient, and lowers the prescription's owed
    quantity by those units. The cancelled units are never dispensed afterwards. After the call the
    patient sees the balance as cancelled and the credit amount on the cancellation entry.

    Args:
        source_fill_id: Id class — the reference number of the owed-balance entry being declined, as the
            agent reads it from the prescription's fill ledger and tells the patient.
        refund_usd: Fixed-format class — the credit returned to the patient for the declined units, in
            USD with 2 decimal places, a positive amount rounded to the cent as the agent states it.

    Returns:
        A text rendering of a dictionary describing the cancellation: "cancellation_id" (text, the new
        fill-ledger reference), "source_fill_id" (text, the owed-balance entry cancelled),
        "owed_units_cancelled" (integer dosage units no longer owed), "refund_usd" (number, USD with 2
        decimal places credited), "owed_quantity_after" (integer units still owed on the prescription)
        and "status" (text, "balance_declined" when the entry was written).
    """
    owed = (ctx.find("rx_fills", fill_id=source_fill_id) or [{}])[0]
    rx = (ctx.find("rx_prescriptions", prescription_id=owed.get("prescription_id", "")) or [{}])[0]
    units = int(owed.get("owed_units") or 0)
    rid = ctx.make_id("rxf_", source_fill_id, refund_usd)
    ctx.create("rx_fills", rid, fill_id=rid, prescription_id=owed.get("prescription_id"),
               customer_id=owed.get("customer_id"), event_type="rx_balance_cancelled",
               event_date=ctx.now()[:10], owed_units=units, source_fill_id=source_fill_id,
               refund_usd=round(float(refund_usd), 2))
    after = int(rx.get("owed_quantity") or 0) - units
    ctx.update("rx_prescriptions", owed.get("prescription_id"), owed_quantity=after)
    return str({"cancellation_id": rid, "source_fill_id": source_fill_id, "owed_units_cancelled": units,
                "refund_usd": round(float(refund_usd), 2), "owed_quantity_after": after,
                "status": "balance_declined"})


@tool(owner="agent", rw="write")
def record_vacation_override_refill_9f5a083e(ctx: ToolContext, prescription_id: str, days_supply_dispensed: int) -> str:
    """Dispense a travel refill of an active prescription ahead of its refill-eligible date and book it on
    the fill ledger as a vacation override refill.

    One call books one refill entry with fill reason vacation_override, dispensed complete today at
    the store holding the prescription and ready for pickup today; it consumes one authorized refill,
    records the refill sequence number and the refills left, and lowers the prescription's remaining
    refills by one. After the call the refill is waiting in will-call and the prescription shows one
    refill fewer.

    Args:
        prescription_id: Id class — the reference number of the prescription record being refilled, as
            returned by the prescription lookup for the verified patient.
        days_supply_dispensed: Fixed-format class — the days of therapy the travel refill carries, an
            integer count in integer days, no decimals.

    Returns:
        A text rendering of a dictionary describing the refill: "fill_id" (text, the new fill-ledger
        reference), "prescription_id" (text), "fill_number" (integer refill sequence number),
        "fill_reason" (text, always "vacation_override"), "days_supply_dispensed" (integer days),
        "refills_remaining_after" (integer refills left), "ready_date" (YYYY-MM-DD, today) and "status"
        (text, "refill_booked" when the entry was written).
    """
    rx = (ctx.find("rx_prescriptions", prescription_id=prescription_id) or [{}])[0]
    number = len(ctx.find("rx_fills", prescription_id=prescription_id, event_type="rx_refill")) + 1
    left = int(rx.get("refills_remaining") or 0) - 1
    rid = ctx.make_id("rxf_", prescription_id, days_supply_dispensed, "vacation_override")
    today = ctx.now()[:10]
    ctx.create("rx_fills", rid, fill_id=rid, prescription_id=prescription_id, customer_id=rx.get("customer_id"),
               event_type="rx_refill", event_date=today, fill_number=number,
               days_supply_dispensed=int(days_supply_dispensed), fill_completeness="complete",
               fill_reason="vacation_override", refills_used=1, refills_remaining_after=left,
               ready_date=today, store_id=rx.get("store_id"))
    ctx.update("rx_prescriptions", prescription_id, refills_remaining=left)
    return str({"fill_id": rid, "prescription_id": prescription_id, "fill_number": number,
                "fill_reason": "vacation_override", "days_supply_dispensed": int(days_supply_dispensed),
                "refills_remaining_after": left, "ready_date": today, "status": "refill_booked"})


@tool(owner="agent", rw="write")
def record_theft_replacement_refill_fbe8d6a8(ctx: ToolContext, prescription_id: str, days_supply_dispensed: int,
                                              police_report_number: str) -> str:
    """Dispense a replacement for medication the patient lost or had stolen, ahead of the prescription's
    refill-eligible date, and book it on the fill ledger as a lost-or-stolen replacement refill.

    One call books one refill entry with fill reason lost_or_stolen_replacement, dispensed complete
    today at the store holding the prescription and ready for pickup today; it records the police
    report number the patient gave, consumes one authorized refill, records the refill sequence
    number and the refills left, and lowers the prescription's remaining refills by one. After the
    call the replacement is waiting in will-call and the prescription shows one refill fewer.

    Args:
        prescription_id: Id class — the reference number of the prescription record being replaced, as
            returned by the prescription lookup for the verified patient.
        days_supply_dispensed: Fixed-format class — the days of therapy the replacement carries, an
            integer count in integer days, no decimals.
        police_report_number: Verbatim class — the police report number exactly as the patient states it
            in the conversation, copied character for character with the same digits, letters and
            punctuation, with nothing added, removed or reformatted (verbatim).

    Returns:
        A text rendering of a dictionary describing the replacement: "fill_id" (text, the new fill-ledger
        reference), "prescription_id" (text), "fill_number" (integer refill sequence number),
        "fill_reason" (text, always "lost_or_stolen_replacement"), "days_supply_dispensed" (integer
        days), "police_report_number" (text, as recorded), "refills_remaining_after" (integer refills
        left), "ready_date" (YYYY-MM-DD, today) and "status" (text, "replacement_booked" when the entry
        was written).
    """
    rx = (ctx.find("rx_prescriptions", prescription_id=prescription_id) or [{}])[0]
    number = len(ctx.find("rx_fills", prescription_id=prescription_id, event_type="rx_refill")) + 1
    left = int(rx.get("refills_remaining") or 0) - 1
    rid = ctx.make_id("rxf_", prescription_id, days_supply_dispensed, police_report_number)
    today = ctx.now()[:10]
    ctx.create("rx_fills", rid, fill_id=rid, prescription_id=prescription_id, customer_id=rx.get("customer_id"),
               event_type="rx_refill", event_date=today, fill_number=number,
               days_supply_dispensed=int(days_supply_dispensed), fill_completeness="complete",
               fill_reason="lost_or_stolen_replacement", refills_used=1, refills_remaining_after=left,
               police_report_number=police_report_number, ready_date=today, store_id=rx.get("store_id"))
    ctx.update("rx_prescriptions", prescription_id, refills_remaining=left)
    return str({"fill_id": rid, "prescription_id": prescription_id, "fill_number": number,
                "fill_reason": "lost_or_stolen_replacement", "days_supply_dispensed": int(days_supply_dispensed),
                "police_report_number": police_report_number, "refills_remaining_after": left,
                "ready_date": today, "status": "replacement_booked"})


@tool(owner="user", rw="write")
def decline_controlled_owed_balance_a6435942(ctx: ToolContext, source_fill_id: str, refund_usd: float) -> str:
    """Let the patient decline, in person, the units Kestrel still owes on a controlled-substance prescription
    dispensed short, and take back the credit for them.

    One call cancels the named controlled owed balance for its full owed units: it books a balance
    cancellation entry on the prescription's fill ledger that names the owed-balance entry, records
    today's date, the units cancelled and the credit returned to the patient, and lowers the
    prescription's owed quantity by those units. The cancelled units are never dispensed afterwards.
    After the call the patient sees the balance as cancelled and the credit amount on the entry.

    Args:
        source_fill_id: Id class — the reference number of the controlled owed-balance entry being
            declined, as the agent reads it from the prescription's fill ledger and tells the patient.
        refund_usd: Fixed-format class — the credit returned to the patient for the declined units, in
            USD with 2 decimal places, a positive amount rounded to the cent as the agent states it.

    Returns:
        A text rendering of a dictionary describing the cancellation: "cancellation_id" (text, the new
        fill-ledger reference), "source_fill_id" (text, the owed-balance entry cancelled),
        "owed_units_cancelled" (integer dosage units no longer owed), "refund_usd" (number, USD with 2
        decimal places credited), "owed_quantity_after" (integer units still owed on the prescription)
        and "status" (text, "controlled_balance_declined" when the entry was written).
    """
    owed = (ctx.find("rx_fills", fill_id=source_fill_id) or [{}])[0]
    rx = (ctx.find("rx_prescriptions", prescription_id=owed.get("prescription_id", "")) or [{}])[0]
    units = int(owed.get("owed_units") or 0)
    rid = ctx.make_id("rxf_", source_fill_id, refund_usd, "controlled")
    ctx.create("rx_fills", rid, fill_id=rid, prescription_id=owed.get("prescription_id"),
               customer_id=owed.get("customer_id"), event_type="rx_balance_cancelled",
               event_date=ctx.now()[:10], owed_units=units, source_fill_id=source_fill_id,
               refund_usd=round(float(refund_usd), 2))
    after = int(rx.get("owed_quantity") or 0) - units
    ctx.update("rx_prescriptions", owed.get("prescription_id"), owed_quantity=after)
    return str({"cancellation_id": rid, "source_fill_id": source_fill_id, "owed_units_cancelled": units,
                "refund_usd": round(float(refund_usd), 2), "owed_quantity_after": after,
                "status": "controlled_balance_declined"})


@tool(owner="agent", rw="write")
def dispense_label_error_remake_88d3ae78(ctx: ToolContext, error_report_id: str, quantity_dispensed: int) -> str:
    """Dispense, at no charge, correctly labelled medication that answers a confirmed wrong-directions-label
    dispensing-error report, and book it on the prescription's fill ledger as a corrected remake.

    One call books one remake entry against the prescription and the fill that the report names: it
    records the units handed out under the corrected label, a patient pay of 0.00, today's date as the
    dispensing and ready date, and the store holding the prescription. No refill is consumed and the
    refill-eligible date is not touched. After the call the remake appears among the prescription's
    fill entries, linked to the report it answers, and is ready for pickup today.

    Args:
        error_report_id: Id class — the reference number of the confirmed dispensing-error report the
            remake answers, as returned by the dispensing-error report lookup for the prescription.
        quantity_dispensed: Fixed-format class — the number of correctly labelled units dispensed on the
            remake, an integer count in integer dosage units (whole tablets or capsules), no decimals.

    Returns:
        A text rendering of a dictionary describing the booked remake: "remake_id" (text, the new
        fill-ledger reference of the remake), "error_report_id" (text, the report it answers),
        "prescription_id" (text, the prescription it is booked on), "quantity_dispensed" (integer
        dosage units handed out), "patient_pay_usd" (number, always 0.0), "ready_date" (YYYY-MM-DD,
        today) and "status" (text, "relabel_remake_booked" when the entry was written).
    """
    report = (ctx.find("rx_error_reports", error_report_id=error_report_id) or [{}])[0]
    rx = (ctx.find("rx_prescriptions", prescription_id=report.get("prescription_id", "")) or [{}])[0]
    rid = ctx.make_id("rxf_", error_report_id, quantity_dispensed, "relabel")
    today = ctx.now()[:10]
    ctx.create("rx_fills", rid, fill_id=rid, prescription_id=report.get("prescription_id"),
               customer_id=report.get("customer_id"), event_type="rx_error_remake", event_date=today,
               source_fill_id=report.get("fill_id"), error_report_id=error_report_id,
               quantity_dispensed=int(quantity_dispensed), patient_pay_usd=0.0, payment_basis="no_charge",
               ready_date=today, store_id=rx.get("store_id"))
    return str({"remake_id": rid, "error_report_id": error_report_id,
                "prescription_id": report.get("prescription_id"), "quantity_dispensed": int(quantity_dispensed),
                "patient_pay_usd": 0.0, "ready_date": today, "status": "relabel_remake_booked"})

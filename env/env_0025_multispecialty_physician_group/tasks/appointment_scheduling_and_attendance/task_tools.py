"""Hidden task tools of the appointment_scheduling_and_attendance difficulty
(env_0025_multispecialty_physician_group, Linden Ridge Medical Group, In-Person Appointments).

Each tool performs exactly one atomic write on the In-Person Appointments line and is reached only
through the unlock/call meta tools after its name is read from the knowledge base. No tool judges
eligibility, timing, ownership or amounts: the caller decides every value from the published rules.
"""

from erlbench import ToolContext, tool


@tool(owner="agent", rw="write")
def cancel_patient_appointment_f57629ba(ctx: ToolContext, appointment_id: str, cancel_timing: str) -> str:
    """Cancel one open in-person appointment at the patient's own request, recording the timing class of
    the cancellation.

    The appointment named by the reference number moves to status cancelled with reason patient_request;
    the moment of cancellation is stamped as the current time, the visit's closed date becomes today, and
    the timing class supplied is stored on the appointment exactly as given. Nothing else changes: any
    booking deposit held on the visit stays recorded on it, and no fee, waiver or refund entry is written.
    Afterwards the appointment list shows the visit as cancelled with that timing, and the receipt below
    confirms the change.

    Args:
        appointment_id: Id class — reference number of the in-person appointment being cancelled, read from the appointment list returned by the appointment lookup for this patient.
        cancel_timing: Enum class — the timing class the cancellation carries under the cancellation rules, one of: not_cancelled (the class a visit carries while it has not been cancelled; never the class of a cancellation being recorded); timely (the patient gave at least the notice the visit requires); late (the patient gave less notice than the visit requires); clinic_initiated (the clinic, not the patient, cancelled the visit, which never applies to a cancellation made at the patient's request).

    Returns:
        A dictionary rendered as text with: appointment_id (the reference number of the cancelled visit), status (always "cancelled" on success), cancel_reason (always "patient_request"), cancel_timing (the timing class stored), cancelled_at (the timestamp of the cancellation as the system clock reports it) and closed_date (the date the visit closed, YYYY-MM-DD). A status of "cancelled" confirms the cancellation is recorded.
    """
    now = ctx.now()
    ctx.update("appointments", appointment_id, status="cancelled", cancel_reason="patient_request",
               cancel_timing=cancel_timing, cancelled_at=now, closed_date=now[:10])
    return str({"appointment_id": appointment_id, "status": "cancelled", "cancel_reason": "patient_request",
                "cancel_timing": cancel_timing, "cancelled_at": now, "closed_date": now[:10]})


@tool(owner="agent", rw="write")
def record_late_cancel_fee_prohibition_784c7051(ctx: ToolContext, appointment_id: str, amount: float) -> str:
    """Record, on one late-cancelled in-person appointment, that its late-cancellation fee is not charged
    because the Medicaid fee prohibition applies, entering the fee amount the prohibition covers.

    One fee-waiver entry is added to the appointment's fee and deposit history: fee type late_cancel_fee,
    reason medicaid_prohibition, dated today, carrying the visit's scheduled date and encounter number
    copied from the appointment, with no assessed-fee entry referenced (the fee is never charged, so no
    charge reaches the financial account). The appointment itself is not changed. Afterwards the fee and
    deposit history of the visit lists the waiver entry with the amount supplied.

    Args:
        appointment_id: Id class — reference number of the late-cancelled in-person appointment, read from the appointment list returned by the appointment lookup for this patient.
        amount: Fixed-format class — the late-cancellation fee amount the prohibition covers, in US dollars as a positive number with exactly 2 decimal places (cents), stored as given in the format USD, 2 decimal places, positive.

    Returns:
        A dictionary rendered as text with: appointment_event_id (reference number of the new waiver entry), appointment_id (the visit it belongs to), event_type (always "appointment_fee_waived"), fee_type (always "late_cancel_fee"), waiver_reason (always "medicaid_prohibition"), amount (the amount recorded, USD with 2 decimal places) and event_date (today, YYYY-MM-DD). The presence of appointment_event_id confirms the entry was recorded.
    """
    appt = ctx.find("appointments", appointment_id=appointment_id)
    row = appt[0] if appt else {}
    value = round(float(amount), 2)
    rid = ctx.make_id("aev_", appointment_id, "late_cancel_fee", "medicaid_prohibition", value)
    ctx.create("appointment_events", rid, appointment_event_id=rid, appointment_id=appointment_id,
               customer_id=row.get("customer_id", ""), event_type="appointment_fee_waived",
               event_date=ctx.now()[:10], service_date=row.get("scheduled_date", ""),
               encounter_number=row.get("encounter_number", ""), fee_type="late_cancel_fee",
               waiver_reason="medicaid_prohibition", amount=value, payment_method="none",
               disposition="none", applies_to_event_id="")
    return str({"appointment_event_id": rid, "appointment_id": appointment_id, "event_type": "appointment_fee_waived",
                "fee_type": "late_cancel_fee", "waiver_reason": "medicaid_prohibition", "amount": value,
                "event_date": ctx.now()[:10]})


@tool(owner="agent", rw="write")
def refund_late_cancel_deposit_f012ee38(ctx: ToolContext, appointment_id: str, amount: float) -> str:
    """Refund to the patient part or all of the booking deposit held on one late-cancelled in-person
    appointment.

    One deposit-release entry with disposition refunded, dated today and carrying the visit's encounter
    number, is added to the appointment's fee and deposit history, and the deposit shown as held on the
    appointment is reduced by the amount supplied. The refund goes back to the patient; nothing is posted
    to the financial account. Afterwards the appointment shows the lower deposit held and the history lists
    the refund entry.

    Args:
        appointment_id: Id class — reference number of the late-cancelled in-person appointment whose deposit is refunded, read from the appointment list returned by the appointment lookup for this patient.
        amount: Fixed-format class — the deposit amount refunded to the patient, in US dollars as a positive number with exactly 2 decimal places (cents), stored as given in the format USD, 2 decimal places, positive.

    Returns:
        A dictionary rendered as text with: appointment_event_id (reference number of the new refund entry), appointment_id (the visit it belongs to), disposition (always "refunded"), amount (the amount refunded, USD with 2 decimal places) and deposit_held_usd (the deposit still held on the visit after the refund, USD with 2 decimal places). The presence of appointment_event_id confirms the refund was recorded.
    """
    appt = ctx.find("appointments", appointment_id=appointment_id)
    row = appt[0] if appt else {}
    value = round(float(amount), 2)
    remaining = round(float(row.get("deposit_held_usd") or 0) - value, 2)
    rid = ctx.make_id("aev_", appointment_id, "refunded", value)
    ctx.create("appointment_events", rid, appointment_event_id=rid, appointment_id=appointment_id,
               customer_id=row.get("customer_id", ""), event_type="appointment_deposit_released",
               event_date=ctx.now()[:10], service_date="", encounter_number=row.get("encounter_number", ""),
               fee_type="none", waiver_reason="none", amount=value, payment_method="none",
               disposition="refunded", applies_to_event_id="")
    ctx.update("appointments", appointment_id, deposit_held_usd=remaining)
    return str({"appointment_event_id": rid, "appointment_id": appointment_id, "disposition": "refunded",
                "amount": value, "deposit_held_usd": remaining})


@tool(owner="user", rw="write")
def pay_booking_deposit_d4a062b3(ctx: ToolContext, appointment_id: str, amount: float) -> str:
    """The patient pays, by their own debit or credit card, the booking deposit on one of their open
    in-person appointments.

    One deposit-collection entry paid by card, dated today and carrying the visit's encounter number, is
    added to the appointment's fee and deposit history, and the deposit shown as held on the appointment
    rises by the amount paid. Afterwards the patient sees the deposit held on the visit and receives the
    payment receipt below.

    Args:
        appointment_id: Id class — reference number of the patient's open in-person appointment the deposit secures, as the agent reads it out from the appointment list.
        amount: Fixed-format class — the deposit amount the patient pays, in US dollars as a positive number with exactly 2 decimal places (cents), stored as given in the format USD, 2 decimal places, positive.

    Returns:
        A dictionary rendered as text with: appointment_event_id (the payment receipt number), appointment_id (the visit secured), payment_method (always "card"), amount (the amount paid, USD with 2 decimal places) and deposit_held_usd (the deposit held on the visit after the payment, USD with 2 decimal places). The presence of appointment_event_id confirms the payment was taken.
    """
    appt = ctx.find("appointments", appointment_id=appointment_id)
    row = appt[0] if appt else {}
    value = round(float(amount), 2)
    held = round(float(row.get("deposit_held_usd") or 0) + value, 2)
    rid = ctx.make_id("aev_", appointment_id, "booking_deposit", value)
    ctx.create("appointment_events", rid, appointment_event_id=rid, appointment_id=appointment_id,
               customer_id=row.get("customer_id", ""), event_type="appointment_deposit_collected",
               event_date=ctx.now()[:10], service_date="", encounter_number=row.get("encounter_number", ""),
               fee_type="none", waiver_reason="none", amount=value, payment_method="card",
               disposition="none", applies_to_event_id="")
    ctx.update("appointments", appointment_id, deposit_held_usd=held)
    return str({"appointment_event_id": rid, "appointment_id": appointment_id, "payment_method": "card",
                "amount": value, "deposit_held_usd": held})


@tool(owner="agent", rw="write")
def record_no_show_fee_prohibition_783ac881(ctx: ToolContext, appointment_id: str, amount: float) -> str:
    """Record, on one missed (no-show) in-person appointment, that its no-show fee is not charged because the
    Medicaid fee prohibition applies, entering the fee amount the prohibition covers.

    One fee-waiver entry is added to the appointment's fee and deposit history: fee type no_show_fee, reason
    medicaid_prohibition, dated today, carrying the visit's scheduled date and encounter number copied from the
    appointment, with no assessed-fee entry referenced (the fee is never charged, so no charge reaches the
    financial account). The appointment itself is not changed. Afterwards the fee and deposit history of the
    missed visit lists the waiver entry with the amount supplied.

    Args:
        appointment_id: Id class — reference number of the missed in-person appointment, read from the appointment list returned by the appointment lookup for this patient.
        amount: Fixed-format class — the no-show fee amount the prohibition covers, in US dollars as a positive number with exactly 2 decimal places (cents), stored as given in the format USD, 2 decimal places, positive.

    Returns:
        A dictionary rendered as text with: appointment_event_id (reference number of the new waiver entry), appointment_id (the visit it belongs to), event_type (always "appointment_fee_waived"), fee_type (always "no_show_fee"), waiver_reason (always "medicaid_prohibition"), amount (the amount recorded, USD with 2 decimal places) and event_date (today, YYYY-MM-DD). The presence of appointment_event_id confirms the entry was recorded.
    """
    appt = ctx.find("appointments", appointment_id=appointment_id)
    row = appt[0] if appt else {}
    value = round(float(amount), 2)
    rid = ctx.make_id("aev_", appointment_id, "no_show_fee", "medicaid_prohibition", value)
    ctx.create("appointment_events", rid, appointment_event_id=rid, appointment_id=appointment_id,
               customer_id=row.get("customer_id", ""), event_type="appointment_fee_waived",
               event_date=ctx.now()[:10], service_date=row.get("scheduled_date", ""),
               encounter_number=row.get("encounter_number", ""), fee_type="no_show_fee",
               waiver_reason="medicaid_prohibition", amount=value, payment_method="none",
               disposition="none", applies_to_event_id="")
    return str({"appointment_event_id": rid, "appointment_id": appointment_id, "event_type": "appointment_fee_waived",
                "fee_type": "no_show_fee", "waiver_reason": "medicaid_prohibition", "amount": value,
                "event_date": ctx.now()[:10]})


@tool(owner="agent", rw="write")
def refund_missed_visit_deposit_4264223f(ctx: ToolContext, appointment_id: str, amount: float) -> str:
    """Refund to the patient part or all of the booking deposit held on one missed (no-show) in-person
    appointment.

    One deposit-release entry with disposition refunded, dated today and carrying the visit's encounter number,
    is added to the appointment's fee and deposit history, and the deposit shown as held on the appointment is
    reduced by the amount supplied. The refund goes back to the patient; nothing is posted to the financial
    account. Afterwards the missed visit shows the lower deposit held and its history lists the refund entry.

    Args:
        appointment_id: Id class — reference number of the missed in-person appointment whose deposit is refunded, read from the appointment list returned by the appointment lookup for this patient.
        amount: Fixed-format class — the deposit amount refunded to the patient, in US dollars as a positive number with exactly 2 decimal places (cents), stored as given in the format USD, 2 decimal places, positive.

    Returns:
        A dictionary rendered as text with: appointment_event_id (reference number of the new refund entry), appointment_id (the visit it belongs to), disposition (always "refunded"), amount (the amount refunded, USD with 2 decimal places) and deposit_held_usd (the deposit still held on the visit after the refund, USD with 2 decimal places). The presence of appointment_event_id confirms the refund was recorded.
    """
    appt = ctx.find("appointments", appointment_id=appointment_id)
    row = appt[0] if appt else {}
    value = round(float(amount), 2)
    remaining = round(float(row.get("deposit_held_usd") or 0) - value, 2)
    rid = ctx.make_id("aev_", appointment_id, "missed_refund", value)
    ctx.create("appointment_events", rid, appointment_event_id=rid, appointment_id=appointment_id,
               customer_id=row.get("customer_id", ""), event_type="appointment_deposit_released",
               event_date=ctx.now()[:10], service_date="", encounter_number=row.get("encounter_number", ""),
               fee_type="none", waiver_reason="none", amount=value, payment_method="none",
               disposition="refunded", applies_to_event_id="")
    ctx.update("appointments", appointment_id, deposit_held_usd=remaining)
    return str({"appointment_event_id": rid, "appointment_id": appointment_id, "disposition": "refunded",
                "amount": value, "deposit_held_usd": remaining})


@tool(owner="user", rw="write")
def pay_deposit_balance_07a1fa0e(ctx: ToolContext, appointment_id: str, amount: float) -> str:
    """The patient pays, by their own debit or credit card, a deposit balance still owed on one of their open
    in-person appointments that already holds a deposit.

    One further deposit-collection entry paid by card, dated today and carrying the visit's encounter number,
    is added to the appointment's fee and deposit history, and the deposit shown as held on the appointment
    rises by the amount paid. Afterwards the patient sees the higher deposit held on the visit and receives the
    payment receipt below.

    Args:
        appointment_id: Id class — reference number of the patient's open in-person appointment the balance is paid on, as the agent reads it out from the appointment list.
        amount: Fixed-format class — the deposit balance the patient pays, in US dollars as a positive number with exactly 2 decimal places (cents), stored as given in the format USD, 2 decimal places, positive.

    Returns:
        A dictionary rendered as text with: appointment_event_id (the payment receipt number), appointment_id (the visit the balance is paid on), payment_method (always "card"), amount (the amount paid, USD with 2 decimal places) and deposit_held_usd (the deposit held on the visit after the payment, USD with 2 decimal places). The presence of appointment_event_id confirms the payment was taken.
    """
    appt = ctx.find("appointments", appointment_id=appointment_id)
    row = appt[0] if appt else {}
    value = round(float(amount), 2)
    held = round(float(row.get("deposit_held_usd") or 0) + value, 2)
    rid = ctx.make_id("aev_", appointment_id, "deposit_balance", value)
    ctx.create("appointment_events", rid, appointment_event_id=rid, appointment_id=appointment_id,
               customer_id=row.get("customer_id", ""), event_type="appointment_deposit_collected",
               event_date=ctx.now()[:10], service_date="", encounter_number=row.get("encounter_number", ""),
               fee_type="none", waiver_reason="none", amount=value, payment_method="card",
               disposition="none", applies_to_event_id="")
    ctx.update("appointments", appointment_id, deposit_held_usd=held)
    return str({"appointment_event_id": rid, "appointment_id": appointment_id, "payment_method": "card",
                "amount": value, "deposit_held_usd": held})

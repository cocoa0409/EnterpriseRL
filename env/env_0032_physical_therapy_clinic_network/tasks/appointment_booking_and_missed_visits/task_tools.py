"""Hidden task tools for the appointment_booking_and_missed_visits difficulty
(env_0032_physical_therapy_clinic_network, category: series).

Each tool performs exactly one atomic write on an Appointment Series and is reached only through
unlock_* -> call_* after its name is found in the published policy. No tool checks eligibility,
status, timing or any other business precondition: the caller decides, the tool records.
"""

from erlbench import ToolContext, tool


@tool(owner="agent", rw="write")
def assess_late_cancellation_fee_706e910e(ctx: ToolContext, series_id: str, source_event_id: str,
                                          amount: float) -> str:
    """Charge the late-cancellation fee for one appointment the patient cancelled with short notice
    on the day ahead of it or earlier. The call books one late-cancellation fee against the patient's
    appointment series, tied to the recorded cancellation it is for, and raises the missed-visit fees
    owed on that series by the amount charged. The patient sees the fee on the series' missed-visit
    balance and on the next statement. Success is the returned fee reference with the amount booked.

    Args:
        series_id: Id class — the reference number of the patient's appointment series that carries
            the cancelled appointment, as returned by the appointment series lookup.
        source_event_id: Id class — the reference number of the recorded cancellation entry the fee is
            for, as returned by the appointment history lookup for that series.
        amount: Fixed-format class — the late-cancellation fee to charge, in USD, a positive number
            given to 2 decimal places (cents); the value is stored exactly as passed after rounding to
            2 decimal places.

    Returns:
        A dictionary rendered as text with: fee_reference (text, the reference number of the new fee
        entry; its presence means the fee was booked), series_id (text, the series charged), fee_kind
        (text, always late_cancellation), amount (number, USD to 2 decimal places, the fee booked),
        appointment_date (text, YYYY-MM-DD, the date of the cancelled appointment), assessed_on
        (text, YYYY-MM-DD, the date the fee was charged) and missed_fee_balance (number, USD to 2
        decimal places, the missed-visit fees owed on the series once this fee is included).
    """
    series_rows = ctx.find("appointment_series", series_id=series_id)
    series = series_rows[0] if series_rows else {}
    source_rows = ctx.find("series_events", series_event_id=source_event_id)
    source = source_rows[0] if source_rows else {}
    value = round(float(amount), 2)
    rid = ctx.make_id("sfl_", series_id, source_event_id, "late_cancellation", value)
    ctx.create("series_events", rid, series_event_id=rid, series_id=series_id,
               customer_id=series.get("customer_id"), event_type="series_fee_assessed",
               event_date=ctx.now()[:10], appointment_date=source.get("appointment_date"),
               fee_kind="late_cancellation", amount=value, source_event_id=source_event_id)
    balance = round(float(series.get("missed_fee_balance") or 0) + value, 2)
    ctx.update("appointment_series", series_id, missed_fee_balance=balance)
    return str({"fee_reference": rid, "series_id": series_id, "fee_kind": "late_cancellation", "amount": value,
                "appointment_date": source.get("appointment_date"), "assessed_on": ctx.now()[:10],
                "missed_fee_balance": balance})


@tool(owner="agent", rw="write")
def assess_no_show_fee_93f38688(ctx: ToolContext, series_id: str, source_event_id: str,
                                amount: float) -> str:
    """Charge the no-show fee for one booked appointment, other than the opening appointment of the
    series, that the patient neither attended nor cancelled. The call books one no-show fee against
    the patient's appointment series, tied to the recorded no-show it is for, and raises the
    missed-visit fees owed on that series by the amount charged. The patient sees the fee on the
    series' missed-visit balance and on the next statement. Success is the returned fee reference
    with the amount booked.

    Args:
        series_id: Id class — the reference number of the patient's appointment series that carries
            the missed appointment, as returned by the appointment series lookup.
        source_event_id: Id class — the reference number of the recorded no-show entry the fee is for,
            as returned by the appointment history lookup for that series.
        amount: Fixed-format class — the no-show fee to charge, in USD, a positive number given to 2
            decimal places (cents); the value is stored exactly as passed after rounding to 2 decimal
            places.

    Returns:
        A dictionary rendered as text with: fee_reference (text, the reference number of the new fee
        entry; its presence means the fee was booked), series_id (text, the series charged), fee_kind
        (text, always no_show), amount (number, USD to 2 decimal places, the fee booked),
        appointment_date (text, YYYY-MM-DD, the date of the missed appointment), assessed_on (text,
        YYYY-MM-DD, the date the fee was charged) and missed_fee_balance (number, USD to 2 decimal
        places, the missed-visit fees owed on the series once this fee is included).
    """
    series_rows = ctx.find("appointment_series", series_id=series_id)
    series = series_rows[0] if series_rows else {}
    source_rows = ctx.find("series_events", series_event_id=source_event_id)
    source = source_rows[0] if source_rows else {}
    value = round(float(amount), 2)
    rid = ctx.make_id("sfn_", series_id, source_event_id, "no_show", value)
    ctx.create("series_events", rid, series_event_id=rid, series_id=series_id,
               customer_id=series.get("customer_id"), event_type="series_fee_assessed",
               event_date=ctx.now()[:10], appointment_date=source.get("appointment_date"),
               fee_kind="no_show", amount=value, source_event_id=source_event_id)
    balance = round(float(series.get("missed_fee_balance") or 0) + value, 2)
    ctx.update("appointment_series", series_id, missed_fee_balance=balance)
    return str({"fee_reference": rid, "series_id": series_id, "fee_kind": "no_show", "amount": value,
                "appointment_date": source.get("appointment_date"), "assessed_on": ctx.now()[:10],
                "missed_fee_balance": balance})


@tool(owner="user", rw="write")
def book_insured_portal_visits_a191f0e3(ctx: ToolContext, series_id: str, appointment_date: str,
                                        visits: int) -> str:
    """Book, as the patient in the patient portal, a batch of standing appointments on your own
    appointment series that your insurance plan of care pays for. One call books the stated number of
    consecutive standing appointments starting on the date you choose, adds them to the
    appointments still booked on the series and records the booking as made through the portal. You
    see the new appointments on your schedule. Success is the returned booking reference with the
    number of appointments booked.

    Args:
        series_id: Id class — the reference number of your appointment series, as read out to you by
            the patient services representative from the appointment series lookup.
        appointment_date: Fixed-format class — the date of the earliest appointment of the new batch,
            written YYYY-MM-DD (calendar date, clinic local time), falling on one of the series'
            standing weekdays.
        visits: Fixed-format class — how many standing appointments to book in this batch, a
            non-negative integer (visits) as told to you by the representative.

    Returns:
        A dictionary rendered as text with: booking_reference (text, the reference number of the new
        booking; its presence means the appointments were booked), series_id (text, the series the
        appointments were added to), first_appointment_date (text, YYYY-MM-DD, the date of the
        earliest appointment booked), visits_booked (integer, the number of appointments booked),
        booking_channel (text, always patient_portal) and booked_visits_remaining (integer, the
        appointments now booked and not yet attended on the series).
    """
    series_rows = ctx.find("appointment_series", series_id=series_id)
    series = series_rows[0] if series_rows else {}
    count = int(visits)
    rid = ctx.make_id("sbi_", series_id, appointment_date, count)
    ctx.create("series_events", rid, series_event_id=rid, series_id=series_id,
               customer_id=series.get("customer_id"), event_type="series_visits_booked",
               event_date=ctx.now()[:10], appointment_date=appointment_date, visits=count,
               booking_channel="patient_portal", funding_source=series.get("funding_source"))
    remaining = int(series.get("booked_visits_remaining") or 0) + count
    ctx.update("appointment_series", series_id, booked_visits_remaining=remaining)
    return str({"booking_reference": rid, "series_id": series_id, "first_appointment_date": appointment_date,
                "visits_booked": count, "booking_channel": "patient_portal",
                "booked_visits_remaining": remaining})


@tool(owner="agent", rw="write")
def assess_first_visit_no_show_fee_a4cbc15c(ctx: ToolContext, series_id: str, source_event_id: str, amount: float) -> str:
    """Charge the no-show fee for the opening appointment of a patient's appointment series when the
    patient neither attended nor cancelled it. The call books one no-show fee against the series, tied to
    the recorded no-show of that opening appointment, and raises the missed-visit fees owed on the
    series by the amount charged. The patient sees the fee on the series' missed-visit balance and on
    the next statement. Success is the returned fee reference with the amount booked.

    Args:
        series_id: Id class — the reference number of the patient's appointment series whose opening
            appointment was missed, as returned by the appointment series lookup.
        source_event_id: Id class — the reference number of the recorded no-show entry of the opening
            appointment, as returned by the appointment history lookup for that series.
        amount: Fixed-format class — the fee to charge, in USD, a positive number given to 2 decimal
            places (cents); the value is stored exactly as passed after rounding to 2 decimal places.

    Returns:
        A dictionary rendered as text with: fee_reference (text, the reference number of the new fee
        entry; its presence means the fee was booked), series_id (text, the series charged), fee_kind
        (text, always no_show), amount (number, USD to 2 decimal places, the fee booked), appointment_date
        (text, YYYY-MM-DD, the date of the missed appointment), assessed_on (text, YYYY-MM-DD, the date
        the fee was charged) and missed_fee_balance (number, USD to 2 decimal places, the missed-visit
        fees owed on the series once this fee is included).
    """
    series_rows = ctx.find("appointment_series", series_id=series_id)
    series = series_rows[0] if series_rows else {}
    source_rows = ctx.find("series_events", series_event_id=source_event_id)
    source = source_rows[0] if source_rows else {}
    value = round(float(amount), 2)
    rid = ctx.make_id("sff_", series_id, source_event_id, "no_show", value)
    ctx.create("series_events", rid, series_event_id=rid, series_id=series_id,
               customer_id=series.get("customer_id"), event_type="series_fee_assessed",
               event_date=ctx.now()[:10], appointment_date=source.get("appointment_date"),
               fee_kind="no_show", amount=value, source_event_id=source_event_id)
    balance = round(float(series.get("missed_fee_balance") or 0) + value, 2)
    ctx.update("appointment_series", series_id, missed_fee_balance=balance)
    return str({"fee_reference": rid, "series_id": series_id, "fee_kind": "no_show", "amount": value,
                "appointment_date": source.get("appointment_date"), "assessed_on": ctx.now()[:10],
                "missed_fee_balance": balance})


@tool(owner="agent", rw="write")
def assess_late_arrival_fee_e6f6ddb6(ctx: ToolContext, series_id: str, source_event_id: str, amount: float) -> str:
    """Charge the late-arrival fee for one booked appointment the patient reached later than the grace
    period of the series' format, so that the visit could not be held. The call books one late-cancellation-kind fee
    against the patient's appointment series, tied to the recorded late-arrival entry it is for, and raises the missed-visit fees owed on that series by the amount charged. The patient sees
    the fee on the series' missed-visit balance and on the next statement. Success is the returned fee
    reference with the amount booked.

    Args:
        series_id: Id class — the reference number of the patient's appointment series that carries
            the late arrival, as returned by the appointment series lookup.
        source_event_id: Id class — the reference number of the recorded late-arrival entry (a
            cancellation entry with zero hours of notice and the minutes late), as returned by the
            appointment history lookup for that series.
        amount: Fixed-format class — the fee to charge, in USD, a positive number given to 2 decimal
            places (cents); the value is stored exactly as passed after rounding to 2 decimal places.

    Returns:
        A dictionary rendered as text with: fee_reference (text, the reference number of the new fee
        entry; its presence means the fee was booked), series_id (text, the series charged), fee_kind
        (text, always late_cancellation), amount (number, USD to 2 decimal places, the fee booked), appointment_date
        (text, YYYY-MM-DD, the date of the missed appointment), assessed_on (text, YYYY-MM-DD, the date
        the fee was charged) and missed_fee_balance (number, USD to 2 decimal places, the missed-visit
        fees owed on the series once this fee is included).
    """
    series_rows = ctx.find("appointment_series", series_id=series_id)
    series = series_rows[0] if series_rows else {}
    source_rows = ctx.find("series_events", series_event_id=source_event_id)
    source = source_rows[0] if source_rows else {}
    value = round(float(amount), 2)
    rid = ctx.make_id("sfa_", series_id, source_event_id, "late_cancellation", value)
    ctx.create("series_events", rid, series_event_id=rid, series_id=series_id,
               customer_id=series.get("customer_id"), event_type="series_fee_assessed",
               event_date=ctx.now()[:10], appointment_date=source.get("appointment_date"),
               fee_kind="late_cancellation", amount=value, source_event_id=source_event_id)
    balance = round(float(series.get("missed_fee_balance") or 0) + value, 2)
    ctx.update("appointment_series", series_id, missed_fee_balance=balance)
    return str({"fee_reference": rid, "series_id": series_id, "fee_kind": "late_cancellation", "amount": value,
                "appointment_date": source.get("appointment_date"), "assessed_on": ctx.now()[:10],
                "missed_fee_balance": balance})


@tool(owner="agent", rw="write")
def assess_same_day_cancellation_fee_8648d00e(ctx: ToolContext, series_id: str, source_event_id: str, amount: float) -> str:
    """Charge the same-day cancellation fee for one booked appointment the patient cancelled on the
    appointment day itself, ahead of its start time. The call books one late-cancellation-kind fee
    against the patient's appointment series, tied to the recorded cancellation it is for, and raises
    the missed-visit fees owed on that series by the amount charged. The patient sees the fee on the
    series' missed-visit balance and on the next statement. Success is the returned fee reference with
    the amount booked.

    Args:
        series_id: Id class — the reference number of the patient's appointment series that carries
            the cancelled appointment, as returned by the appointment series lookup.
        source_event_id: Id class — the reference number of the recorded same-day cancellation entry
            the fee is for, as returned by the appointment history lookup for that series.
        amount: Fixed-format class — the fee to charge, in USD, a positive number given to 2 decimal
            places (cents); the value is stored exactly as passed after rounding to 2 decimal places.

    Returns:
        A dictionary rendered as text with: fee_reference (text, the reference number of the new fee
        entry; its presence means the fee was booked), series_id (text, the series charged), fee_kind
        (text, always late_cancellation), amount (number, USD to 2 decimal places, the fee booked), appointment_date
        (text, YYYY-MM-DD, the date of the missed appointment), assessed_on (text, YYYY-MM-DD, the date
        the fee was charged) and missed_fee_balance (number, USD to 2 decimal places, the missed-visit
        fees owed on the series once this fee is included).
    """
    series_rows = ctx.find("appointment_series", series_id=series_id)
    series = series_rows[0] if series_rows else {}
    source_rows = ctx.find("series_events", series_event_id=source_event_id)
    source = source_rows[0] if source_rows else {}
    value = round(float(amount), 2)
    rid = ctx.make_id("sfs_", series_id, source_event_id, "late_cancellation", value)
    ctx.create("series_events", rid, series_event_id=rid, series_id=series_id,
               customer_id=series.get("customer_id"), event_type="series_fee_assessed",
               event_date=ctx.now()[:10], appointment_date=source.get("appointment_date"),
               fee_kind="late_cancellation", amount=value, source_event_id=source_event_id)
    balance = round(float(series.get("missed_fee_balance") or 0) + value, 2)
    ctx.update("appointment_series", series_id, missed_fee_balance=balance)
    return str({"fee_reference": rid, "series_id": series_id, "fee_kind": "late_cancellation", "amount": value,
                "appointment_date": source.get("appointment_date"), "assessed_on": ctx.now()[:10],
                "missed_fee_balance": balance})


@tool(owner="user", rw="write")
def book_package_portal_visits_336412d0(ctx: ToolContext, series_id: str, appointment_date: str,
                                        visits: int) -> str:
    """Book, as the patient in the patient portal, a batch of standing appointments on your own
    appointment series that your Self-Pay Visit Package pays for. One call books the stated number of
    consecutive standing appointments starting on the date you choose, adds them to the
    appointments still booked on the series and records the booking as made through the portal. You
    see the new appointments on your schedule. Success is the returned booking reference with the
    number of appointments booked.

    Args:
        series_id: Id class — the reference number of your appointment series, as read out to you by
            the patient services representative from the appointment series lookup.
        appointment_date: Fixed-format class — the date of the earliest appointment of the new batch,
            written YYYY-MM-DD (calendar date, clinic local time), falling on one of the series'
            standing weekdays.
        visits: Fixed-format class — how many standing appointments to book in this batch, a
            non-negative integer (visits) as told to you by the representative.

    Returns:
        A dictionary rendered as text with: booking_reference (text, the reference number of the new
        booking; its presence means the appointments were booked), series_id (text, the series the
        appointments were added to), first_appointment_date (text, YYYY-MM-DD, the date of the
        earliest appointment booked), visits_booked (integer, the number of appointments booked),
        booking_channel (text, always patient_portal) and booked_visits_remaining (integer, the
        appointments now booked and not yet attended on the series).
    """
    series_rows = ctx.find("appointment_series", series_id=series_id)
    series = series_rows[0] if series_rows else {}
    count = int(visits)
    rid = ctx.make_id("sbp_", series_id, appointment_date, count)
    ctx.create("series_events", rid, series_event_id=rid, series_id=series_id,
               customer_id=series.get("customer_id"), event_type="series_visits_booked",
               event_date=ctx.now()[:10], appointment_date=appointment_date, visits=count,
               booking_channel="patient_portal", funding_source=series.get("funding_source"))
    remaining = int(series.get("booked_visits_remaining") or 0) + count
    ctx.update("appointment_series", series_id, booked_visits_remaining=remaining)
    return str({"booking_reference": rid, "series_id": series_id, "first_appointment_date": appointment_date,
                "visits_booked": count, "booking_channel": "patient_portal",
                "booked_visits_remaining": remaining})

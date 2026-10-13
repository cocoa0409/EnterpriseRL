"""Hidden task tools of the driver_account_holds_and_deactivations difficulty (Wayfare Mobility).

Every tool here performs one atomic write on a driver services agreement or on its standing
record, with the arguments exactly as given. None of them checks a business condition: whether a
write is due, and what value it carries, is decided by the agent from the published policy and
the records. Calendar arithmetic that turns a whole number of days or months into the stored
calendar date is done by the pure-integer helper class below (no clock or date library is used;
the only clock is ctx.now()).
"""

from erlbench import ToolContext, tool


class _CalendarDays:
    """Proleptic Gregorian calendar arithmetic on 'YYYY-MM-DD' strings, in whole days."""

    @staticmethod
    def to_ordinal(text):
        y, m, d = (int(p) for p in str(text)[:10].split("-"))
        y -= 1 if m <= 2 else 0
        era = (y if y >= 0 else y - 399) // 400
        yoe = y - era * 400
        doy = (153 * (m + (-3 if m > 2 else 9)) + 2) // 5 + d - 1
        doe = yoe * 365 + yoe // 4 - yoe // 100 + doy
        return era * 146097 + doe - 719468

    @staticmethod
    def from_ordinal(n):
        z = n + 719468
        era = (z if z >= 0 else z - 146096) // 146097
        doe = z - era * 146097
        yoe = (doe - doe // 1460 + doe // 36524 - doe // 146096) // 365
        doy = doe - (365 * yoe + yoe // 4 - yoe // 100)
        mp = (5 * doy + 2) // 153
        d = doy - (153 * mp + 2) // 5 + 1
        m = mp + (3 if mp < 10 else -9)
        y = yoe + era * 400 + (1 if m <= 2 else 0)
        return f"{y:04d}-{m:02d}-{d:02d}"

    @staticmethod
    def add_days(text, days):
        return _CalendarDays.from_ordinal(_CalendarDays.to_ordinal(text) + int(days))

    @staticmethod
    def add_months(text, months):
        y, m, d = (int(p) for p in str(text)[:10].split("-"))
        total = y * 12 + (m - 1) + int(months)
        ny, nm = total // 12, total % 12 + 1
        first_next = _CalendarDays.to_ordinal(f"{ny + (1 if nm == 12 else 0):04d}-{(nm % 12) + 1:02d}-01")
        last_day = first_next - _CalendarDays.to_ordinal(f"{ny:04d}-{nm:02d}-01")
        return f"{ny:04d}-{nm:02d}-{min(d, last_day):02d}"


# --------------------------------------------------------------------------- document lapse
@tool(owner="agent", rw="write")
def deactivate_for_document_lapse_e185dacd(ctx: ToolContext, driver_agreement_id: str,
                                            hold_started_date: str, allowance_days: int) -> str:
    """Deactivate a driver services agreement for document lapse, dated on the day its document
    hold's lapse allowance ends. One call moves the agreement from on hold to deactivated, records
    the deactivation reason document_lapse, sets the deactivation date to the hold start date
    advanced by the given number of calendar days, and clears the hold reason (to none) and the
    hold start date. Afterwards the driver agreement lookup shows the agreement as deactivated for
    document lapse on that date, and the driver cannot go online. The receipt confirms the new
    status, reason and deactivation date.

    Args:
        driver_agreement_id: Id class — the reference number of the driver services agreement
            being deactivated, as returned by the driver agreement lookup.
        hold_started_date: Fixed-format class — the start date of the document hold in force on
            that agreement, copied exactly as the driver agreement lookup shows it, written
            YYYY-MM-DD (a calendar date in the market's local time, no time of day).
        allowance_days: Fixed-format class — the lapse allowance of that hold, as a whole number of
            calendar days (integer, no decimals, no unit text); the deactivation date is that many
            calendar days after hold_started_date.

    Returns:
        A dictionary receipt: driver_agreement_id (the agreement reference number), status (the
        agreement status now in force, deactivated on success), deactivation_reason (document_lapse)
        and deactivation_date (YYYY-MM-DD, the date the deactivation is recorded on). A receipt with
        status deactivated means the deactivation is in force.
    """
    deactivation_date = _CalendarDays.add_days(hold_started_date, allowance_days)
    ctx.update("driver_agreements", driver_agreement_id, status="deactivated",
               deactivation_reason="document_lapse", deactivation_date=deactivation_date,
               hold_reason="none", hold_started_date="")
    return str({"driver_agreement_id": driver_agreement_id, "status": "deactivated",
                "deactivation_reason": "document_lapse", "deactivation_date": deactivation_date})


# --------------------------------------------------------------------------- insurance binder
@tool(owner="agent", rw="write")
def record_insurance_binder_0f7a5736(ctx: ToolContext, driver_agreement_id: str, accepted_days: int) -> str:
    """Record an uploaded insurance binder on a driver services agreement for its accepted period.
    One call sets the agreement's insurance expiry date on file to today's date (the system clock)
    advanced by the given number of calendar days; nothing else on the agreement changes. Afterwards
    the driver agreement lookup shows the new insurance expiry date, and the insurance counts as on
    file and unexpired through that date. The receipt confirms the date recorded.

    Args:
        driver_agreement_id: Id class — the reference number of the driver services agreement whose
            insurance on file is being recorded, as returned by the driver agreement lookup.
        accepted_days: Fixed-format class — the binder's accepted period as a whole number of
            calendar days counted from today (integer, no decimals, no unit text); the insurance
            expiry date on file becomes today plus that many days.

    Returns:
        A dictionary receipt: driver_agreement_id (the agreement reference number),
        insurance_expiry_date (YYYY-MM-DD, the insurance expiry date now on file) and recorded_on
        (YYYY-MM-DD, today's date). A receipt carrying the new insurance_expiry_date means the binder
        is recorded.
    """
    today = ctx.now()[:10]
    expiry = _CalendarDays.add_days(today, accepted_days)
    ctx.update("driver_agreements", driver_agreement_id, insurance_expiry_date=expiry)
    return str({"driver_agreement_id": driver_agreement_id, "insurance_expiry_date": expiry,
                "recorded_on": today})


# --------------------------------------------------------------------------- temporary license
@tool(owner="user", rw="write")
def upload_temporary_license_ef094b46(ctx: ToolContext, driver_agreement_id: str, accepted_days: int) -> str:
    """Upload, as the driver, the paper temporary driver's license issued on renewal, and put it on
    file for its accepted period. One call adds a document upload to the driver's standing record
    (document type drivers_license, dated today, with an expiry date of today's date advanced by
    the given number of calendar days) and sets the license expiry date on the driver services
    agreement to that same date. Afterwards the standing record lists the upload and the driver
    agreement lookup shows the new license expiry date. The receipt gives the upload's reference
    number and the date recorded.

    Args:
        driver_agreement_id: Id class — the reference number of the driver's own services agreement,
            as read out by the support agent from the driver agreement lookup.
        accepted_days: Fixed-format class — the accepted period of the temporary license as a whole
            number of calendar days counted from today (integer, no decimals, no unit text), as given
            by the support agent; the license expiry date on file becomes today plus that many days.

    Returns:
        A dictionary receipt: upload_reference (the reference number of the new standing record
        entry), driver_agreement_id (the agreement reference number), document_type
        (drivers_license), license_expiry_date (YYYY-MM-DD, the license expiry date now on file) and
        uploaded_on (YYYY-MM-DD, today's date). A receipt with an upload_reference means the
        temporary license is on file.
    """
    now = ctx.now()
    today = now[:10]
    expiry = _CalendarDays.add_days(today, accepted_days)
    agreements = ctx.find("driver_agreements", driver_agreement_id=driver_agreement_id)
    customer_id = agreements[0].get("customer_id") if agreements else ""
    rid = ctx.make_id("dse_", driver_agreement_id, "drivers_license", accepted_days, now)
    ctx.create("driver_standing_events", rid, driver_standing_event_id=rid,
               driver_agreement_id=driver_agreement_id, customer_id=customer_id,
               event_type="driver_document_submit", event_date=today, recorded_at=now,
               document_type="drivers_license", document_expiry_date=expiry, notice_sequence=0,
               rating_at_review=0.0, rated_trips_in_window=0, cancellation_rate_pct=0.0,
               warning_basis="none", safety_report_category="none", recheck_result="none")
    ctx.update("driver_agreements", driver_agreement_id, license_expiry_date=expiry)
    return str({"upload_reference": rid, "driver_agreement_id": driver_agreement_id,
                "document_type": "drivers_license", "license_expiry_date": expiry,
                "uploaded_on": today})


# --------------------------------------------------------------------------- cancellation warning
@tool(owner="agent", rw="write")
def record_cancellation_warning_d72ae138(ctx: ToolContext, driver_agreement_id: str, cancellation_rate_pct: float,
                                         notice_sequence: int) -> str:
    """Record a cancellation-rate quality warning on a driver's standing record. One call adds one
    quality warning entry dated today, with warning basis cancellation_rate, the driver cancellation
    rate the warning is about and the warning's sequence number; the agreement itself is not
    changed. Afterwards the standing record lookup lists the warning, and the driver sees a
    cancellation-rate warning on their account. The receipt gives the warning's reference number.

    Args:
        driver_agreement_id: Id class — the reference number of the driver services agreement being
            warned, as returned by the driver agreement lookup.
        cancellation_rate_pct: Fixed-format class — the driver cancellation rate the warning records,
            in percent, written to 1 decimal place exactly as the rating review it comes from shows
            it (no rounding beyond that, no percent sign).
        notice_sequence: Fixed-format class — the warning's sequence number in the driver's current
            warning cycle, an integer of 1 or more.

    Returns:
        A dictionary receipt: warning_reference (the reference number of the new standing record
        entry), driver_agreement_id (the agreement reference number), warning_basis
        (cancellation_rate), cancellation_rate_pct (percent, 1 decimal place), notice_sequence
        (integer) and warned_on (YYYY-MM-DD, today's date). A receipt with a warning_reference means
        the warning is on the record.
    """
    now = ctx.now()
    agreements = ctx.find("driver_agreements", driver_agreement_id=driver_agreement_id)
    customer_id = agreements[0].get("customer_id") if agreements else ""
    rate = round(float(cancellation_rate_pct), 1)
    rid = ctx.make_id("dse_", driver_agreement_id, rate, int(notice_sequence), now)
    ctx.create("driver_standing_events", rid, driver_standing_event_id=rid,
               driver_agreement_id=driver_agreement_id, customer_id=customer_id,
               event_type="driver_quality_warning", event_date=now[:10], recorded_at=now,
               document_type="none", document_expiry_date="", notice_sequence=int(notice_sequence),
               rating_at_review=0.0, rated_trips_in_window=0, cancellation_rate_pct=rate,
               warning_basis="cancellation_rate", safety_report_category="none", recheck_result="none")
    return str({"warning_reference": rid, "driver_agreement_id": driver_agreement_id,
                "warning_basis": "cancellation_rate", "cancellation_rate_pct": rate,
                "notice_sequence": int(notice_sequence), "warned_on": now[:10]})


# --------------------------------------------------------------------------- registration hold
@tool(owner="agent", rw="write")
def place_registration_hold_154e4b50(ctx: ToolContext, driver_agreement_id: str, registration_expiry_date: str,
                                     grace_days: int) -> str:
    """Put a driver services agreement on a document hold for a lapsed vehicle registration. One call
    moves the agreement from active to on hold, records the hold reason document_expired, and sets
    the hold start date to the registration's expiry date advanced by the given number of calendar
    days. Afterwards the driver agreement lookup shows the agreement on hold with that start date,
    and the driver cannot go online. The receipt confirms the status, reason and hold start date.

    Args:
        driver_agreement_id: Id class — the reference number of the driver services agreement being
            put on hold, as returned by the driver agreement lookup.
        registration_expiry_date: Fixed-format class — the expiry date of the lapsed vehicle
            registration, copied exactly as the standing record lookup shows it on the latest
            registration upload, written YYYY-MM-DD (a calendar date, no time of day).
        grace_days: Fixed-format class — the number of calendar days after that expiry date on which
            the hold begins, a whole number (integer, no decimals, no unit text).

    Returns:
        A dictionary receipt: driver_agreement_id (the agreement reference number), status (on_hold on
        success), hold_reason (document_expired) and hold_started_date (YYYY-MM-DD, the hold start
        date recorded). A receipt with status on_hold means the hold is in force.
    """
    started = _CalendarDays.add_days(registration_expiry_date, grace_days)
    ctx.update("driver_agreements", driver_agreement_id, status="on_hold", hold_reason="document_expired",
               hold_started_date=started)
    return str({"driver_agreement_id": driver_agreement_id, "status": "on_hold",
                "hold_reason": "document_expired", "hold_started_date": started})


# --------------------------------------------------------------------------- inspection validity
@tool(owner="agent", rw="write")
def record_inspection_validity_ad704ee2(ctx: ToolContext, driver_agreement_id: str, inspection_date: str,
                                        validity_days: int) -> str:
    """Record a passed vehicle inspection on a driver services agreement for its validity. One call
    sets the agreement's vehicle inspection expiry date on file to the inspection date advanced by
    the given number of calendar days; nothing else on the agreement changes. Afterwards the driver
    agreement lookup shows the new inspection expiry date, and the inspection counts as on file and
    unexpired through that date. The receipt confirms the date recorded.

    Args:
        driver_agreement_id: Id class — the reference number of the driver services agreement whose
            inspection is being recorded, as returned by the driver agreement lookup.
        inspection_date: Fixed-format class — the date the inspection was passed, copied exactly as
            the standing record lookup shows it on the inspection upload, written YYYY-MM-DD (a
            calendar date, no time of day).
        validity_days: Fixed-format class — the inspection's validity as a whole number of calendar
            days counted from inspection_date (integer, no decimals, no unit text).

    Returns:
        A dictionary receipt: driver_agreement_id (the agreement reference number),
        inspection_expiry_date (YYYY-MM-DD, the inspection expiry date now on file) and
        inspection_date (YYYY-MM-DD, as given). A receipt carrying the new inspection_expiry_date means
        the inspection is recorded.
    """
    expiry = _CalendarDays.add_days(inspection_date, validity_days)
    ctx.update("driver_agreements", driver_agreement_id, inspection_expiry_date=expiry)
    return str({"driver_agreement_id": driver_agreement_id, "inspection_expiry_date": expiry,
                "inspection_date": inspection_date})


# --------------------------------------------------------------------------- temporary permit
@tool(owner="user", rw="write")
def upload_temporary_permit_14d2792d(ctx: ToolContext, driver_agreement_id: str, accepted_days: int) -> str:
    """Upload, as the driver, the temporary for-hire permit issued on renewal (the renewal receipt),
    and put it on file for its accepted period. One call adds a document upload to the driver's
    standing record (document type commercial_permit, dated today, with an expiry date of today's
    date advanced by the given number of calendar days) and sets the for-hire permit expiry date on
    the driver services agreement to that same date. Afterwards the standing record lists the upload
    and the driver agreement lookup shows the new permit expiry date. The receipt gives the upload's
    reference number and the date recorded.

    Args:
        driver_agreement_id: Id class — the reference number of the driver's own services agreement,
            as read out by the support agent from the driver agreement lookup.
        accepted_days: Fixed-format class — the accepted period of the temporary permit as a whole
            number of calendar days counted from today (integer, no decimals, no unit text), as given
            by the support agent; the permit expiry date on file becomes today plus that many days.

    Returns:
        A dictionary receipt: upload_reference (the reference number of the new standing record
        entry), driver_agreement_id (the agreement reference number), document_type
        (commercial_permit), permit_expiry_date (YYYY-MM-DD, the permit expiry date now on file) and
        uploaded_on (YYYY-MM-DD, today's date). A receipt with an upload_reference means the temporary
        permit is on file.
    """
    now = ctx.now()
    today = now[:10]
    expiry = _CalendarDays.add_days(today, accepted_days)
    agreements = ctx.find("driver_agreements", driver_agreement_id=driver_agreement_id)
    customer_id = agreements[0].get("customer_id") if agreements else ""
    rid = ctx.make_id("dse_", driver_agreement_id, "commercial_permit", accepted_days, now)
    ctx.create("driver_standing_events", rid, driver_standing_event_id=rid,
               driver_agreement_id=driver_agreement_id, customer_id=customer_id,
               event_type="driver_document_submit", event_date=today, recorded_at=now,
               document_type="commercial_permit", document_expiry_date=expiry, notice_sequence=0,
               rating_at_review=0.0, rated_trips_in_window=0, cancellation_rate_pct=0.0,
               warning_basis="none", safety_report_category="none", recheck_result="none")
    ctx.update("driver_agreements", driver_agreement_id, commercial_permit_expiry_date=expiry)
    return str({"upload_reference": rid, "driver_agreement_id": driver_agreement_id,
                "document_type": "commercial_permit", "permit_expiry_date": expiry, "uploaded_on": today})

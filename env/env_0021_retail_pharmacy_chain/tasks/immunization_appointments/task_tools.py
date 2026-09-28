"""Hidden task tools for the immunization_appointments difficulty (Kestrel Pharmacy, category vax).

Each tool performs one atomic write on the patient's immunization records and nothing else: it
checks no eligibility, computes no derived value and refuses nothing. Every value it records is
passed in by the caller exactly as documented below.
"""

from erlbench import ToolContext, tool



class _CivilDate:
    """Pure-integer proleptic Gregorian date arithmetic on 'YYYY-MM-DD' strings (not a tool)."""

    @staticmethod
    def _days_from_civil(y: int, m: int, d: int) -> int:
        """Days since 1970-01-01 of a proleptic Gregorian date (pure integer arithmetic)."""
        y -= m <= 2
        era = (y if y >= 0 else y - 399) // 400
        yoe = y - era * 400
        doy = (153 * (m + (-3 if m > 2 else 9)) + 2) // 5 + d - 1
        doe = yoe * 365 + yoe // 4 - yoe // 100 + doy
        return era * 146097 + doe - 719468

    @staticmethod
    def _civil_from_days(z: int) -> tuple:
        """Inverse of _days_from_civil: (year, month, day) for a day count since 1970-01-01."""
        z += 719468
        era = (z if z >= 0 else z - 146096) // 146097
        doe = z - era * 146097
        yoe = (doe - doe // 1460 + doe // 36524 - doe // 146096) // 365
        y = yoe + era * 400
        doy = doe - (365 * yoe + yoe // 4 - yoe // 100)
        mp = (5 * doy + 2) // 153
        d = doy - (153 * mp + 2) // 5 + 1
        m = mp + (3 if mp < 10 else -9)
        return y + (m <= 2), m, d

    @staticmethod
    def _add_days(iso: str, days: int) -> str:
        """'YYYY-MM-DD' plus a whole number of days, returned as 'YYYY-MM-DD'."""
        y, m, d = int(iso[0:4]), int(iso[5:7]), int(iso[8:10])
        y2, m2, d2 = _CivilDate._civil_from_days(_CivilDate._days_from_civil(y, m, d) + int(days))
        if not 1 <= y2 <= 9999:
            raise OverflowError("date value out of range")
        return f"{y2:04d}-{m2:02d}-{d2:02d}"


@tool(owner="agent", rw="write")
def invalidate_series_dose_51b39017(ctx: ToolContext, course_id: str, source_event_id: str, invalid_reason: str,
                                    is_final_dose: bool, doses_remaining: int) -> str:
    """Record that a dose already on a patient's vaccination course does not count, and restate the
    course's doses still needed. One call adds one invalidation entry against the named dose, dated
    today, carrying the reason and whether the invalidated dose had been the completing dose; it
    also sets the course's count of valid doses still needed to the value given. When the
    invalidated dose had been the completing dose of a completed course, the course returns to in
    progress and its closing date is cleared. The dose itself stays on the record. The patient's course history afterwards
    shows the invalidation entry and the restated count.

    Args:
        course_id: Id class — reference number of the vaccination course that holds the dose, as returned by the vaccination course lookup.
        source_event_id: Id class — reference number of the dose entry found not to count, as returned by the vaccination history lookup.
        invalid_reason: Enum class — why the dose does not count: interval_too_short when the dose was given earlier than its minimum interval less the grace period; below_minimum_age when the patient was younger than the vaccine's minimum age on the dose date.
        is_final_dose: Enum class — whether the invalidated dose had completed the course: true when that dose entry is recorded as the completing dose; false when it did not complete the course.
        doses_remaining: Fixed-format class — valid doses the course still needs once the entry is booked, a non-negative integer count of doses.

    Returns:
        A dictionary: invalidation_id (text, reference number of the new invalidation entry),
        course_id (text), source_event_id (text), invalid_reason (text), doses_remaining (integer,
        the course's restated count of valid doses still needed), course_status (text, the
        course's status after the entry) and recorded_on (YYYY-MM-DD, today's date). A returned
        invalidation_id means the entry is on the record.
    """
    rid = ctx.make_id("vxi_", course_id, source_event_id, invalid_reason, is_final_dose, doses_remaining)
    today = ctx.now()[:10]
    ctx.create("vax_events", rid, vax_event_id=rid, course_id=course_id,
               customer_id=(ctx.find("vax_courses", course_id=course_id) or [{}])[0].get("customer_id"),
               event_type="vax_dose_invalidated", event_date=today, source_event_id=source_event_id,
               invalid_reason=invalid_reason, is_final_dose=bool(is_final_dose))
    fields = {"doses_remaining": int(doses_remaining)}
    course = (ctx.find("vax_courses", course_id=course_id) or [{}])[0]
    if bool(is_final_dose) and course.get("status") == "completed":
        fields.update(status="in_progress", closed_date=None)
    ctx.update("vax_courses", course_id, **fields)
    status = (ctx.find("vax_courses", course_id=course_id) or [{}])[0].get("status")
    return str({"invalidation_id": rid, "course_id": course_id, "source_event_id": source_event_id,
                "invalid_reason": invalid_reason, "doses_remaining": int(doses_remaining),
                "course_status": status, "recorded_on": today})


@tool(owner="agent", rw="write")
def open_resumed_course_fd79a681(ctx: ToolContext, customer_id: str, variant_name: str, store_id: str,
                                 coverage_id: str, billing_route: str, immunocompromised: bool,
                                 risk_condition_attested: bool, doses_required: int, doses_remaining: int) -> str:
    """Open a new non-seasonal vaccination course for a patient at a Kestrel store. One call creates
    one course in scheduled status, opened today, for the named vaccination, recording the store
    where it is given, how its doses are paid and by which insurance plan, the patient's attestations,
    the valid doses the course needs in all and the valid doses it still needs at opening. The new
    course then appears in the patient's vaccination courses and can take appointments.

    Args:
        customer_id: Id class — patient reference number, as returned by the patient profile lookup.
        variant_name: Enum class — the vaccination: Seasonal Influenza Standard-Dose Vaccination for the standard flu shot; Seasonal Influenza High-Dose Vaccination for the high-dose flu shot; COVID-19 Updated Vaccination for the updated COVID-19 shot; RSV Older Adult Vaccination for the older-adult RSV shot; Pneumococcal Conjugate Vaccination for the pneumococcal shot; Recombinant Zoster Two-Dose Series for the shingles series; Hepatitis B Three-Dose Series for the hepatitis B series.
        store_id: Id class — reference number of the Kestrel store where the course is given, as returned by the store lookup or an earlier course record.
        coverage_id: Id class — reference number of the insurance plan billed for the course's doses, as returned by the insurance plan lookup; pass "" when the doses are paid in cash or from Vaccines for Children stock.
        billing_route: Enum class — how the course's doses are paid: medical_benefit when billed to Medicare Part B; pharmacy_benefit when billed to a prescription insurance plan; cash when the patient pays the cash price; no_cost_program when given from Vaccines for Children stock.
        immunocompromised: Enum class — the patient's attestation: true when the patient attests being immunocompromised; false when they do not.
        risk_condition_attested: Enum class — the patient's attestation: true when the patient attests a qualifying risk condition for this vaccine; false when they do not.
        doses_required: Fixed-format class — valid doses that complete the course for this patient, a positive integer count of doses.
        doses_remaining: Fixed-format class — valid doses the course still needs at opening, a non-negative integer count of doses.

    Returns:
        A dictionary: course_id (text, reference number of the new course), variant_name (text),
        status (text, always scheduled), doses_required (integer), doses_remaining (integer),
        store_id (text) and opened_date (YYYY-MM-DD, today's date). A returned course_id means the
        course is open on the patient's profile.
    """
    rid = ctx.make_id("vxc_", customer_id, variant_name, store_id, coverage_id, billing_route, immunocompromised,
                      risk_condition_attested, doses_required, doses_remaining)
    today = ctx.now()[:10]
    ctx.create("vax_courses", rid, course_id=rid, customer_id=customer_id, variant_name=variant_name,
               status="scheduled", season_label="", doses_required=int(doses_required),
               doses_remaining=int(doses_remaining), immunocompromised=bool(immunocompromised),
               risk_condition_attested=bool(risk_condition_attested), billing_route=billing_route,
               coverage_id=coverage_id or None, store_id=store_id, opened_date=today, closed_date=None)
    return str({"course_id": rid, "variant_name": variant_name, "status": "scheduled",
                "doses_required": int(doses_required), "doses_remaining": int(doses_remaining),
                "store_id": store_id, "opened_date": today})


@tool(owner="user", rw="write")
def sign_dose_consent_2c77f168(ctx: ToolContext, course_id: str, dose_number: int, signed_by: str) -> str:
    """The patient, or their parent or guardian, signs the screening and consent form for one dose of
    a vaccination course. One call records one signed form, dated today, for the named dose of the
    course. The signed form then appears in the course's history and covers that dose for the form's
    validity period.

    Args:
        course_id: Id class — reference number of the vaccination course the form is for, as given by the representative from the course record.
        dose_number: Fixed-format class — the dose of the course the form covers, a positive integer dose number.
        signed_by: Enum class — who signs: patient when the patient signs for themselves; guardian when a parent or legal guardian signs for a patient below the guardian-consent age.

    Returns:
        A dictionary: consent_id (text, reference number of the signed form), course_id (text),
        dose_number (integer), signed_by (text) and signed_on (YYYY-MM-DD, today's date). A returned
        consent_id means the form is on file.
    """
    rid = ctx.make_id("vxk_", course_id, dose_number, signed_by)
    today = ctx.now()[:10]
    ctx.create("vax_events", rid, vax_event_id=rid, course_id=course_id,
               customer_id=(ctx.find("vax_courses", course_id=course_id) or [{}])[0].get("customer_id"),
               event_type="vax_consent_signed", event_date=today, dose_number=int(dose_number), signed_by=signed_by,
               source_event_id=None)
    return str({"consent_id": rid, "course_id": course_id, "dose_number": int(dose_number),
                "signed_by": signed_by, "signed_on": today})


@tool(owner="agent", rw="write")
def book_series_dose_9b68cabc(ctx: ToolContext, course_id: str, store_id: str, dose_number: int,
                              days_ahead: int, appointment_time: str) -> str:
    """Book a phone appointment for one dose of a patient's vaccination course. One call creates one
    booked appointment, made today through the phone channel, at the named store, for the named dose,
    on the date that lies the given number of calendar days after today and at the given start time.
    The appointment then appears in the course's history as an open appointment.

    Args:
        course_id: Id class — reference number of the vaccination course the appointment is for, as returned by the course lookup or the course opening.
        store_id: Id class — reference number of the Kestrel store where the dose is given, as returned by the store lookup or the course record.
        dose_number: Fixed-format class — the dose of the course the appointment is for, a positive integer dose number.
        days_ahead: Fixed-format class — the appointment date expressed as whole calendar days after today's date in the store's local time, an integer from 0 (today) upward; the tool records the resulting date as YYYY-MM-DD.
        appointment_time: Fixed-format class — start time of the slot in HH:MM, 24-hour, store local time, as the patient chose it.

    Returns:
        A dictionary: appointment_id (text, reference number of the booked appointment), course_id
        (text), dose_number (integer), appointment_date (YYYY-MM-DD), appointment_time (HH:MM),
        store_id (text) and booked_on (YYYY-MM-DD, today's date). A returned appointment_id means
        the appointment is booked.
    """
    today = ctx.now()[:10]
    appt = _CivilDate._add_days(today, int(days_ahead))
    rid = ctx.make_id("vxb_", course_id, store_id, dose_number, days_ahead, appointment_time)
    ctx.create("vax_events", rid, vax_event_id=rid, course_id=course_id,
               customer_id=(ctx.find("vax_courses", course_id=course_id) or [{}])[0].get("customer_id"),
               event_type="vax_appointment_booked", event_date=today, appointment_date=appt,
               appointment_time=appointment_time, store_id=store_id, dose_number=int(dose_number),
               booking_channel="phone")
    return str({"appointment_id": rid, "course_id": course_id, "dose_number": int(dose_number),
                "appointment_date": appt, "appointment_time": appointment_time, "store_id": store_id,
                "booked_on": today})


@tool(owner="agent", rw="write")
def post_missed_dose_006fe732(ctx: ToolContext, course_id: str, source_event_id: str, store_id: str, dose_number: int,
                              lot_number: str, billing_route: str, coverage_id: str, is_final_dose: bool,
                              observation_minutes: int) -> str:
    """Post the record of a vaccine dose a Kestrel pharmacist gave today whose record did not reach the
    system. One call adds one dose-given entry dated today to the course, tied to the kept appointment,
    with the store, dose number, lot number, how the dose is paid, the insurance plan billed if any,
    whether it completes the course and the observation minutes; the amount the patient pays is left
    open. It takes one dose off the course's count of valid doses still needed; a dose that completes
    the course closes it as completed today, and the first dose of a longer series marks it in progress.
    The dose then shows in the course history.

    Args:
        course_id: Id class — reference number of the vaccination course the dose belongs to, as returned by the course lookup.
        source_event_id: Id class — reference number of the booked appointment the dose was given at, as returned by the vaccination history lookup.
        store_id: Id class — reference number of the Kestrel store where the dose was given, as returned by the store lookup or the appointment.
        dose_number: Fixed-format class — the dose of the course that was given, a positive integer dose number.
        lot_number: Verbatim class — the vaccine lot number printed on the patient's vaccination record card, copied character for character as the patient reads it out (verbatim).
        billing_route: Enum class — how the dose is paid: medical_benefit when billed to Medicare Part B; pharmacy_benefit when billed to a prescription insurance plan; cash when the patient pays the cash price; no_cost_program when given from Vaccines for Children stock.
        coverage_id: Id class — reference number of the insurance plan billed for the dose, as returned by the insurance plan lookup; pass "" for a cash or Vaccines for Children dose.
        is_final_dose: Enum class — whether this dose completes the course: true when it brings the course's valid doses to the doses required; false when more doses remain.
        observation_minutes: Fixed-format class — minutes the patient is recorded as observed after the dose, in integer minutes.

    Returns:
        A dictionary: dose_record_id (text, reference number of the posted dose entry), course_id
        (text), dose_number (integer), event_date (YYYY-MM-DD, today's date), observation_minutes
        (integer), doses_remaining (integer, the course's valid doses still needed after the dose)
        and course_status (text). A returned dose_record_id means the dose is on the record.
    """
    today = ctx.now()[:10]
    rid = ctx.make_id("vxd_", course_id, source_event_id, store_id, dose_number, lot_number, billing_route,
                      coverage_id, is_final_dose, observation_minutes)
    course = (ctx.find("vax_courses", course_id=course_id) or [{}])[0]
    ctx.create("vax_events", rid, vax_event_id=rid, course_id=course_id, customer_id=course.get("customer_id"),
               event_type="vax_dose_administered", event_date=today, dose_number=int(dose_number),
               is_final_dose=bool(is_final_dose), lot_number=lot_number, store_id=store_id,
               source_event_id=source_event_id, billing_route=billing_route, coverage_id=coverage_id or None,
               patient_pay_usd=None, observation_minutes=int(observation_minutes), auto_book_next=False)
    remaining = int(course.get("doses_remaining") or 0) - 1
    fields = {"doses_remaining": remaining}
    if bool(is_final_dose):
        fields.update(status="completed", closed_date=today)
    elif course.get("status") == "scheduled":
        fields.update(status="in_progress")
    ctx.update("vax_courses", course_id, **fields)
    status = (ctx.find("vax_courses", course_id=course_id) or [{}])[0].get("status")
    return str({"dose_record_id": rid, "course_id": course_id, "dose_number": int(dose_number), "event_date": today,
                "observation_minutes": int(observation_minutes), "doses_remaining": remaining, "course_status": status})


@tool(owner="user", rw="write")
def settle_dose_charge_857cec2f(ctx: ToolContext, vax_event_id: str, course_id: str, dose_number: int,
                                patient_pay_usd: float) -> str:
    """The patient pays, by card over the phone, the amount charged for one vaccine dose already on
    their record whose payment is still open. One call records the amount paid on that dose entry.
    The dose entry then shows the amount the patient paid.

    Args:
        vax_event_id: Id class — reference number of the dose entry being paid for, as given by the representative from the posted dose record.
        course_id: Id class — reference number of the vaccination course the dose belongs to, as given by the representative.
        dose_number: Fixed-format class — the dose of the course being paid for, a positive integer dose number.
        patient_pay_usd: Fixed-format class — the amount paid for the dose in USD, 2 decimal places, rounded to the cent half up, as the representative states it.

    Returns:
        A dictionary: payment_reference (text, reference number of the payment), vax_event_id (text),
        course_id (text), dose_number (integer), patient_pay_usd (number, USD with 2 decimal places)
        and paid_on (YYYY-MM-DD, today's date). A returned payment_reference means the payment is on
        the dose record.
    """
    today = ctx.now()[:10]
    ref = ctx.make_id("vxp_", vax_event_id, course_id, dose_number, patient_pay_usd)
    ctx.update("vax_events", vax_event_id, patient_pay_usd=round(float(patient_pay_usd), 2))
    return str({"payment_reference": ref, "vax_event_id": vax_event_id, "course_id": course_id,
                "dose_number": int(dose_number), "patient_pay_usd": round(float(patient_pay_usd), 2), "paid_on": today})

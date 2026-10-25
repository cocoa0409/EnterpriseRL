"""Shared tools for env_0078_public_school_district (Calloway Creek ISD Family Services).

Every tool here is a SHARE tool, always present in its owner's tool list: one finder per
record type (the customers finder doubles as the identity entry), the identity-verification write
and the transfer-to-human handoff write.
"""

from erlbench import ToolContext, tool

# Scenario operating constants (built into the tools below):
#   K = 2  profile credentials must match for identity verification to pass
#   R = 2  explicit requests for a person before a CUSTOMER_REQUESTED handoff


@tool(owner="agent", rw="read")
def find_customers(ctx: ToolContext, customer_id: str = "", name: str = "", phone: str = "", email: str = "") -> str:
    """Look up a family's household profile to establish whose account this call is about.

    Search by the household reference number, or by what the caller can naturally tell you:
    the parent or guardian's full name, the phone number on the profile or the email address on
    the profile. Every criterion is optional; give whichever you have, and add another when more
    than one household matches. Spacing, punctuation and capitalisation in what the caller says
    do not affect the search. The profile returned shows the guardian's name, phone, email, date
    of birth, the last four digits of the photo ID presented at registration, the residence
    address and ZIP code, whether the residence lies inside the district, whether the guardian is
    a district employee, the preferred language and the date the profile was opened. Finding a
    profile does not verify the caller's identity.

    Args:
        customer_id: The household reference number; leave "" if unknown.
        name: The parent or guardian's full name as the caller states it; leave "" if not given.
        phone: The phone number on the profile, 10 digits; leave "" if not given.
        email: The email address on the profile; leave "" if not given.
    """
    match = {k: v for k, v in {"customer_id": customer_id, "name": name,
                               "phone": phone, "email": email}.items() if v}
    if not match:
        return "Error: provide at least one reference number or profile detail to find the household."
    rows = ctx.fuzzy_find("customers", **match)
    if not rows:
        return f"No household profile matches {match}."
    if len(rows) > 1:
        return f"Error: {len(rows)} household profiles match {match}; ask the caller for one more detail."
    return str(rows[0])


@tool(owner="agent", rw="write")
def verify_household_identity(ctx: ToolContext, customer_id: str, phone: str = "", email: str = "",
                              date_of_birth: str = "", id_last4: str = "") -> str:
    """Verify that the caller is the parent or guardian on the household profile, and record the outcome.

    Verification must pass before any account details are discussed or any business is done on
    the household's records. This tool performs the comparison itself: it checks each piece of
    identity information the caller states against the household profile, counts how many
    agree, and passes only when at least 2 of them agree. The household reference number only
    tells the tool which profile to compare against and never counts as a match. Callers can
    usually give only some of these details, so pass exactly what the caller said and leave the
    rest blank. The outcome is recorded; if a first attempt does not pass and a later attempt with
    more details does, the household stays verified.

    Args:
        customer_id: The household reference number from the household profile lookup; required. Used only to open the profile and never counted as a match.
        phone: The phone number on the profile as the caller states it, 10 digits with no punctuation; leave "" if not stated.
        email: The email address on the profile as the caller states it; leave "" if not stated.
        date_of_birth: The parent or guardian's date of birth as the caller states it, YYYY-MM-DD; leave "" if not stated.
        id_last4: The last four digits of the photo ID the parent or guardian presented at registration, 4 digits; leave "" if not stated.
    """
    if not customer_id:
        return "Error: customer_id is required; look up the household profile first and pass its reference number."
    rows = ctx.find("customers", customer_id=customer_id)
    if not rows:
        return f"Error: no household profile {customer_id}; cannot verify."
    rec = rows[0]
    supplied = {"phone": phone, "email": email, "date_of_birth": date_of_birth, "id_last4": id_last4}
    matched = sum(1 for field, value in supplied.items()
                  if value and str(rec.get(field, "")).strip().casefold() == str(value).strip().casefold())
    verified = matched >= 2
    rid = ctx.make_id("ver_", customer_id)
    prior = ctx.find("verification_log", verification_id=rid)
    verified = verified or bool(prior and prior[0].get("verified"))
    if prior:
        ctx.update("verification_log", rid, verified=verified, verified_at=ctx.now())
    else:
        ctx.create("verification_log", rid, verification_id=rid, customer_id=customer_id,
                   verified=verified, verified_at=ctx.now())
    if verified:
        return f"Identity verified for household {customer_id} ({matched} detail(s) matched)."
    return (f"Identity NOT verified for household {customer_id} (only {matched} of the required 2 details matched). "
            "Ask the caller for another detail on the profile and try again.")


@tool(owner="agent", rw="write")
def transfer_to_human_agent(ctx: ToolContext, customer_id: str, reason: str) -> str:
    """Hand the family over to a Family Services representative and record the handoff and its reason.

    Use it in one of two situations only: when no district policy available to you can resolve
    what the family is asking for, or when the caller has explicitly asked to speak with a person
    at least 2 times during the call.

    Args:
        customer_id: The household reference number from the household profile lookup; the profile must exist.
        reason: Why the family is being handed over; exactly one of POLICY_NOT_COVERED (no available policy can resolve the request) or CUSTOMER_REQUESTED (the caller explicitly asked for a person at least 2 times). Never free text.
    """
    allowed = {"POLICY_NOT_COVERED", "CUSTOMER_REQUESTED"}
    if reason not in allowed:
        return f"Error: unknown handoff reason '{reason}'. Valid: {', '.join(sorted(allowed))}."
    if not ctx.find("customers", customer_id=customer_id):
        return f"Error: no household profile {customer_id}; cannot record the handoff."
    rid = ctx.make_id("hof_", customer_id, reason)
    ctx.create("handoff_log", rid, handoff_id=rid, customer_id=customer_id, reason=reason, created_at=ctx.now())
    return f"Handoff to a Family Services representative recorded for household {customer_id} ({reason})."


@tool(owner="agent", rw="read")
def find_students(ctx: ToolContext, student_id: str = "", customer_id: str = "") -> str:
    """Look up the students of a household: legal name, district student ID number, date of birth, attendance-zone campus, and the designations on file (homeless, foster care or migrant designation, special education IEP or Section 504 plan and whether the IEP lists transportation, emergent bilingual identification, military-connected family).

    Supply any reference number you already hold; every criterion is optional and the
    criteria given must all match. Returns every matching student with all of its details, or a
    short message saying none was found.

    Args:
        student_id: The student reference number; leave "" if unknown.
        customer_id: The household reference number; leave "" if unknown.
    """
    match = {k: v for k, v in {"student_id": student_id, "customer_id": customer_id}.items() if v}
    rows = ctx.find("students", **match)
    return str(rows) if rows else f"No student found for {match}."


@tool(owner="agent", rw="read")
def find_verification_log(ctx: ToolContext, verification_id: str = "", customer_id: str = "") -> str:
    """Look up the recorded outcome of identity verification for a household.

    Supply any reference number you already hold; every criterion is optional and the
    criteria given must all match. Returns every matching verification record with all of its details, or a
    short message saying none was found.

    Args:
        verification_id: The reference number of the verification record itself; leave "" if unknown.
        customer_id: The household reference number; leave "" if unknown.
    """
    match = {k: v for k, v in {"verification_id": verification_id, "customer_id": customer_id}.items() if v}
    rows = ctx.find("verification_log", **match)
    return str(rows) if rows else f"No verification record found for {match}."


@tool(owner="agent", rw="read")
def find_handoff_log(ctx: ToolContext, handoff_id: str = "", customer_id: str = "") -> str:
    """Look up the handoffs to a human representative recorded for a household.

    Supply any reference number you already hold; every criterion is optional and the
    criteria given must all match. Returns every matching handoff record with all of its details, or a
    short message saying none was found.

    Args:
        handoff_id: The reference number of the handoff record itself; leave "" if unknown.
        customer_id: The household reference number; leave "" if unknown.
    """
    match = {k: v for k, v in {"handoff_id": handoff_id, "customer_id": customer_id}.items() if v}
    rows = ctx.find("handoff_log", **match)
    return str(rows) if rows else f"No handoff record found for {match}."


@tool(owner="agent", rw="read")
def find_care_enrollments(ctx: ToolContext, care_enrollment_id: str = "", customer_id: str = "", student_id: str = "") -> str:
    """Look up Creek Kids Club Extended Day enrollments: the plan held, campus, school year, status, registration, start and end dates, waitlist and offer dates, suspension date, third-party funding and the date of the last plan change.

    Supply any reference number you already hold; every criterion is optional and the
    criteria given must all match. Returns every matching Extended Day enrollment with all of its details, or a
    short message saying none was found.

    Args:
        care_enrollment_id: The Extended Day enrollment reference number; leave "" if unknown.
        customer_id: The household reference number; leave "" if unknown.
        student_id: The student reference number; leave "" if unknown.
    """
    match = {k: v for k, v in {"care_enrollment_id": care_enrollment_id, "customer_id": customer_id, "student_id": student_id}.items() if v}
    rows = ctx.find("care_enrollments", **match)
    return str(rows) if rows else f"No Extended Day enrollment found for {match}."


@tool(owner="agent", rw="read")
def find_care_ledger(ctx: ToolContext, care_ledger_id: str = "", care_enrollment_id: str = "", customer_id: str = "", source_care_ledger_id: str = "") -> str:
    """Look up the Extended Day billing history of an enrollment: registration fees, monthly tuition with its rate basis, sibling position and proration, day fees, late pickup and late payment fees, plan change fees, payments, Workforce Solutions remittances, credits, returned payments and refunds.

    Supply any reference number you already hold; every criterion is optional and the
    criteria given must all match. Returns every matching Extended Day billing entry with all of its details, or a
    short message saying none was found.

    Args:
        care_ledger_id: The reference number of the Extended Day billing entry itself; leave "" if unknown.
        care_enrollment_id: The Extended Day enrollment reference number; leave "" if unknown.
        customer_id: The household reference number; leave "" if unknown.
        source_care_ledger_id: The reference number of the original Extended Day charge or payment an entry relates to; leave "" if unknown.
    """
    match = {k: v for k, v in {"care_ledger_id": care_ledger_id, "care_enrollment_id": care_enrollment_id, "customer_id": customer_id, "source_care_ledger_id": source_care_ledger_id}.items() if v}
    rows = ctx.find("care_ledger", **match)
    return str(rows) if rows else f"No Extended Day billing entry found for {match}."


@tool(owner="agent", rw="read")
def find_care_attendance_log(ctx: ToolContext, care_attendance_id: str = "", care_enrollment_id: str = "", customer_id: str = "") -> str:
    """Look up the Extended Day attendance log of an enrollment: late pickups with their minutes late, fee status and semester, and late-pickup warning letters.

    Supply any reference number you already hold; every criterion is optional and the
    criteria given must all match. Returns every matching attendance log entry with all of its details, or a
    short message saying none was found.

    Args:
        care_attendance_id: The reference number of the attendance log entry itself; leave "" if unknown.
        care_enrollment_id: The Extended Day enrollment reference number; leave "" if unknown.
        customer_id: The household reference number; leave "" if unknown.
    """
    match = {k: v for k, v in {"care_attendance_id": care_attendance_id, "care_enrollment_id": care_enrollment_id, "customer_id": customer_id}.items() if v}
    rows = ctx.find("care_attendance_log", **match)
    return str(rows) if rows else f"No attendance log entry found for {match}."


@tool(owner="agent", rw="read")
def find_care_requests(ctx: ToolContext, care_request_id: str = "", customer_id: str = "", care_enrollment_id: str = "") -> str:
    """Look up requests a family has made about an Extended Day enrollment: withdrawal notices, plan change requests, late fee courtesy requests and drop-in bookings, with the date asked for and the handling status.

    Supply any reference number you already hold; every criterion is optional and the
    criteria given must all match. Returns every matching Extended Day request with all of its details, or a
    short message saying none was found.

    Args:
        care_request_id: The reference number of the Extended Day request itself; leave "" if unknown.
        customer_id: The household reference number; leave "" if unknown.
        care_enrollment_id: The Extended Day enrollment reference number; leave "" if unknown.
    """
    match = {k: v for k, v in {"care_request_id": care_request_id, "customer_id": customer_id, "care_enrollment_id": care_enrollment_id}.items() if v}
    rows = ctx.find("care_requests", **match)
    return str(rows) if rows else f"No Extended Day request found for {match}."


@tool(owner="agent", rw="read")
def find_enrollments(ctx: ToolContext, enrollment_id: str = "", customer_id: str = "", student_id: str = "", approved_transfer_request_id: str = "") -> str:
    """Look up district enrollment records: enrollment type, campus, grade level, school year, status, entry type, registration and entry dates, residency verification date, withdrawal date and reason, Pre-K eligibility basis and any transfer placement.

    Supply any reference number you already hold; every criterion is optional and the
    criteria given must all match. Returns every matching enrollment record with all of its details, or a
    short message saying none was found.

    Args:
        enrollment_id: The enrollment record reference number; leave "" if unknown.
        customer_id: The household reference number; leave "" if unknown.
        student_id: The student reference number; leave "" if unknown.
        approved_transfer_request_id: The reference number of the approved transfer request a placement rests on; leave "" if unknown.
    """
    match = {k: v for k, v in {"enrollment_id": enrollment_id, "customer_id": customer_id, "student_id": student_id, "approved_transfer_request_id": approved_transfer_request_id}.items() if v}
    rows = ctx.find("enrollments", **match)
    return str(rows) if rows else f"No enrollment record found for {match}."


@tool(owner="agent", rw="read")
def find_enrollment_ledger(ctx: ToolContext, enrollment_ledger_id: str = "", enrollment_id: str = "", customer_id: str = "", source_enrollment_ledger_id: str = "") -> str:
    """Look up the Pre-Kindergarten tuition history of an enrollment: monthly tuition with proration and sibling discount, late fees, payments, credits and refunds.

    Supply any reference number you already hold; every criterion is optional and the
    criteria given must all match. Returns every matching tuition entry with all of its details, or a
    short message saying none was found.

    Args:
        enrollment_ledger_id: The reference number of the tuition entry itself; leave "" if unknown.
        enrollment_id: The enrollment record reference number; leave "" if unknown.
        customer_id: The household reference number; leave "" if unknown.
        source_enrollment_ledger_id: The reference number of the original tuition charge a credit relates to; leave "" if unknown.
    """
    match = {k: v for k, v in {"enrollment_ledger_id": enrollment_ledger_id, "enrollment_id": enrollment_id, "customer_id": customer_id, "source_enrollment_ledger_id": source_enrollment_ledger_id}.items() if v}
    rows = ctx.find("enrollment_ledger", **match)
    return str(rows) if rows else f"No tuition entry found for {match}."


@tool(owner="agent", rw="read")
def find_enrollment_records_log(ctx: ToolContext, enrollment_record_id: str = "", enrollment_id: str = "", customer_id: str = "") -> str:
    """Look up the registration documents accepted for an enrollment record (proof of residency, birth certificate, immunization record, prior school records, Pre-K eligibility proof, employee verification, withdrawal notice) with the document date and the date received.

    Supply any reference number you already hold; every criterion is optional and the
    criteria given must all match. Returns every matching registration document entry with all of its details, or a
    short message saying none was found.

    Args:
        enrollment_record_id: The reference number of the registration document entry itself; leave "" if unknown.
        enrollment_id: The enrollment record reference number; leave "" if unknown.
        customer_id: The household reference number; leave "" if unknown.
    """
    match = {k: v for k, v in {"enrollment_record_id": enrollment_record_id, "enrollment_id": enrollment_id, "customer_id": customer_id}.items() if v}
    rows = ctx.find("enrollment_records_log", **match)
    return str(rows) if rows else f"No registration document entry found for {match}."


@tool(owner="agent", rw="read")
def find_transfer_requests(ctx: ToolContext, transfer_request_id: str = "", customer_id: str = "", student_id: str = "", enrollment_id: str = "") -> str:
    """Look up transfer and choice program requests: category, requested campus and program, school year, status, decision date, any revocation notice date and the moment the request was filed.

    Supply any reference number you already hold; every criterion is optional and the
    criteria given must all match. Returns every matching transfer request with all of its details, or a
    short message saying none was found.

    Args:
        transfer_request_id: The transfer request reference number; leave "" if unknown.
        customer_id: The household reference number; leave "" if unknown.
        student_id: The student reference number; leave "" if unknown.
        enrollment_id: The enrollment record reference number; leave "" if unknown.
    """
    match = {k: v for k, v in {"transfer_request_id": transfer_request_id, "customer_id": customer_id, "student_id": student_id, "enrollment_id": enrollment_id}.items() if v}
    rows = ctx.find("transfer_requests", **match)
    return str(rows) if rows else f"No transfer request found for {match}."


@tool(owner="agent", rw="read")
def find_meal_accounts(ctx: ToolContext, meal_account_id: str = "", customer_id: str = "", student_id: str = "", meal_benefit_application_id: str = "") -> str:
    """Look up School Nutrition cafeteria meal accounts: the student's current meal status, account status, cafeteria campus, the date the status took effect, the application it rests on, the reason of the last reduction, and the opened, inactive and closed dates.

    Supply any reference number you already hold; every criterion is optional and the
    criteria given must all match. Returns every matching meal account with all of its details, or a
    short message saying none was found.

    Args:
        meal_account_id: The meal account reference number; leave "" if unknown.
        customer_id: The household reference number; leave "" if unknown.
        student_id: The student reference number; leave "" if unknown.
        meal_benefit_application_id: The meal benefit application reference number; leave "" if unknown.
    """
    match = {k: v for k, v in {"meal_account_id": meal_account_id, "customer_id": customer_id, "student_id": student_id, "meal_benefit_application_id": meal_benefit_application_id}.items() if v}
    rows = ctx.find("meal_accounts", **match)
    return str(rows) if rows else f"No meal account found for {match}."


@tool(owner="agent", rw="read")
def find_meal_transactions(ctx: ToolContext, meal_transaction_id: str = "", meal_account_id: str = "", customer_id: str = "", source_meal_transaction_id: str = "", counterpart_meal_account_id: str = "") -> str:
    """Look up the transactions on a meal account: deposits, meals and items rung up with their meal type and price basis, voids, refunds, sibling transfers and returned deposits.

    Supply any reference number you already hold; every criterion is optional and the
    criteria given must all match. Returns every matching meal account transaction with all of its details, or a
    short message saying none was found.

    Args:
        meal_transaction_id: The reference number of the meal account transaction itself; leave "" if unknown.
        meal_account_id: The meal account reference number; leave "" if unknown.
        customer_id: The household reference number; leave "" if unknown.
        source_meal_transaction_id: The reference number of the original purchase line or deposit a transaction relates to; leave "" if unknown.
        counterpart_meal_account_id: The reference number of the other meal account in a sibling transfer; leave "" if unknown.
    """
    match = {k: v for k, v in {"meal_transaction_id": meal_transaction_id, "meal_account_id": meal_account_id, "customer_id": customer_id, "source_meal_transaction_id": source_meal_transaction_id, "counterpart_meal_account_id": counterpart_meal_account_id}.items() if v}
    rows = ctx.find("meal_transactions", **match)
    return str(rows) if rows else f"No meal account transaction found for {match}."


@tool(owner="agent", rw="read")
def find_meal_notices(ctx: ToolContext, meal_notice_id: str = "", meal_account_id: str = "", customer_id: str = "") -> str:
    """Look up the notices sent about a meal account: low and negative balance notices, charge limit and year-end collection notices, approval letters, verification selection letters and adverse action notices.

    Supply any reference number you already hold; every criterion is optional and the
    criteria given must all match. Returns every matching meal notice with all of its details, or a
    short message saying none was found.

    Args:
        meal_notice_id: The reference number of the notice itself; leave "" if unknown.
        meal_account_id: The meal account reference number; leave "" if unknown.
        customer_id: The household reference number; leave "" if unknown.
    """
    match = {k: v for k, v in {"meal_notice_id": meal_notice_id, "meal_account_id": meal_account_id, "customer_id": customer_id}.items() if v}
    rows = ctx.find("meal_notices", **match)
    return str(rows) if rows else f"No meal notice found for {match}."


@tool(owner="agent", rw="read")
def find_meal_benefit_applications(ctx: ToolContext, meal_benefit_application_id: str = "", customer_id: str = "", meal_account_id: str = "") -> str:
    """Look up household meal benefit applications: school year, basis, submitted date, determination and its date, and the verification outcome.

    Supply any reference number you already hold; every criterion is optional and the
    criteria given must all match. Returns every matching meal benefit application with all of its details, or a
    short message saying none was found.

    Args:
        meal_benefit_application_id: The meal benefit application reference number; leave "" if unknown.
        customer_id: The household reference number; leave "" if unknown.
        meal_account_id: The meal account reference number; leave "" if unknown.
    """
    match = {k: v for k, v in {"meal_benefit_application_id": meal_benefit_application_id, "customer_id": customer_id, "meal_account_id": meal_account_id}.items() if v}
    rows = ctx.find("meal_benefit_applications", **match)
    return str(rows) if rows else f"No meal benefit application found for {match}."


@tool(owner="agent", rw="read")
def find_transport_assignments(ctx: ToolContext, transport_assignment_id: str = "", customer_id: str = "", student_id: str = "") -> str:
    """Look up student transportation assignments: transportation type, campus, school year, status, measured distance and hazardous zone, route and AM/PM stops, start and end dates with the end reason, and any riding suspension.

    Supply any reference number you already hold; every criterion is optional and the
    criteria given must all match. Returns every matching transportation assignment with all of its details, or a
    short message saying none was found.

    Args:
        transport_assignment_id: The transportation assignment reference number; leave "" if unknown.
        customer_id: The household reference number; leave "" if unknown.
        student_id: The student reference number; leave "" if unknown.
    """
    match = {k: v for k, v in {"transport_assignment_id": transport_assignment_id, "customer_id": customer_id, "student_id": student_id}.items() if v}
    rows = ctx.find("transport_assignments", **match)
    return str(rows) if rows else f"No transportation assignment found for {match}."


@tool(owner="agent", rw="read")
def find_transport_ledger(ctx: ToolContext, transport_ledger_id: str = "", transport_assignment_id: str = "", customer_id: str = "", source_transport_ledger_id: str = "") -> str:
    """Look up the transportation billing history of an assignment: courtesy permit fees, replacement bus pass fees, payments, credits and refunds.

    Supply any reference number you already hold; every criterion is optional and the
    criteria given must all match. Returns every matching transportation billing entry with all of its details, or a
    short message saying none was found.

    Args:
        transport_ledger_id: The reference number of the transportation billing entry itself; leave "" if unknown.
        transport_assignment_id: The transportation assignment reference number; leave "" if unknown.
        customer_id: The household reference number; leave "" if unknown.
        source_transport_ledger_id: The reference number of the original fee a credit relates to; leave "" if unknown.
    """
    match = {k: v for k, v in {"transport_ledger_id": transport_ledger_id, "transport_assignment_id": transport_assignment_id, "customer_id": customer_id, "source_transport_ledger_id": source_transport_ledger_id}.items() if v}
    rows = ctx.find("transport_ledger", **match)
    return str(rows) if rows else f"No transportation billing entry found for {match}."


@tool(owner="agent", rw="read")
def find_transport_service_log(ctx: ToolContext, transport_log_id: str = "", transport_assignment_id: str = "", customer_id: str = "") -> str:
    """Look up the transportation service log of an assignment: bus passes issued, bus conduct referrals with their offense number and suspension days, and returns to campus when no adult met the student.

    Supply any reference number you already hold; every criterion is optional and the
    criteria given must all match. Returns every matching transportation log entry with all of its details, or a
    short message saying none was found.

    Args:
        transport_log_id: The reference number of the log entry itself; leave "" if unknown.
        transport_assignment_id: The transportation assignment reference number; leave "" if unknown.
        customer_id: The household reference number; leave "" if unknown.
    """
    match = {k: v for k, v in {"transport_log_id": transport_log_id, "transport_assignment_id": transport_assignment_id, "customer_id": customer_id}.items() if v}
    rows = ctx.find("transport_service_log", **match)
    return str(rows) if rows else f"No transportation log entry found for {match}."


@tool(owner="agent", rw="read")
def find_transport_requests(ctx: ToolContext, transport_request_id: str = "", customer_id: str = "", transport_assignment_id: str = "") -> str:
    """Look up requests a family has made about a transportation assignment: stop changes, alternate childcare addresses, permit cancellations, address change reports and pass replacements, with their handling status.

    Supply any reference number you already hold; every criterion is optional and the
    criteria given must all match. Returns every matching transportation request with all of its details, or a
    short message saying none was found.

    Args:
        transport_request_id: The reference number of the transportation request itself; leave "" if unknown.
        customer_id: The household reference number; leave "" if unknown.
        transport_assignment_id: The transportation assignment reference number; leave "" if unknown.
    """
    match = {k: v for k, v in {"transport_request_id": transport_request_id, "customer_id": customer_id, "transport_assignment_id": transport_assignment_id}.items() if v}
    rows = ctx.find("transport_requests", **match)
    return str(rows) if rows else f"No transportation request found for {match}."


@tool(owner="agent", rw="read")
def find_activity_participations(ctx: ToolContext, activity_participation_id: str = "", customer_id: str = "", student_id: str = "") -> str:
    """Look up student activity, athletics and trip participations: activity type and activity, campus, school year, season, status, registration, clearance and end dates, competition level, installment plan and any academic ineligibility.

    Supply any reference number you already hold; every criterion is optional and the
    criteria given must all match. Returns every matching activity participation with all of its details, or a
    short message saying none was found.

    Args:
        activity_participation_id: The activity participation reference number; leave "" if unknown.
        customer_id: The household reference number; leave "" if unknown.
        student_id: The student reference number; leave "" if unknown.
    """
    match = {k: v for k, v in {"activity_participation_id": activity_participation_id, "customer_id": customer_id, "student_id": student_id}.items() if v}
    rows = ctx.find("activity_participations", **match)
    return str(rows) if rows else f"No activity participation found for {match}."


@tool(owner="agent", rw="read")
def find_activity_ledger(ctx: ToolContext, activity_ledger_id: str = "", activity_participation_id: str = "", customer_id: str = "", source_activity_ledger_id: str = "") -> str:
    """Look up the fee history of an activity participation: fee components, equipment charges, payments, credits and refunds.

    Supply any reference number you already hold; every criterion is optional and the
    criteria given must all match. Returns every matching activity fee entry with all of its details, or a
    short message saying none was found.

    Args:
        activity_ledger_id: The reference number of the activity fee entry itself; leave "" if unknown.
        activity_participation_id: The activity participation reference number; leave "" if unknown.
        customer_id: The household reference number; leave "" if unknown.
        source_activity_ledger_id: The reference number of the original fee or charge a credit relates to; leave "" if unknown.
    """
    match = {k: v for k, v in {"activity_ledger_id": activity_ledger_id, "activity_participation_id": activity_participation_id, "customer_id": customer_id, "source_activity_ledger_id": source_activity_ledger_id}.items() if v}
    rows = ctx.find("activity_ledger", **match)
    return str(rows) if rows else f"No activity fee entry found for {match}."


@tool(owner="agent", rw="read")
def find_activity_records_log(ctx: ToolContext, activity_record_id: str = "", activity_participation_id: str = "", customer_id: str = "") -> str:
    """Look up the participation packet of an activity participation: documents accepted with their dates, and equipment or uniforms issued and returned.

    Supply any reference number you already hold; every criterion is optional and the
    criteria given must all match. Returns every matching participation record with all of its details, or a
    short message saying none was found.

    Args:
        activity_record_id: The reference number of the participation record itself; leave "" if unknown.
        activity_participation_id: The activity participation reference number; leave "" if unknown.
        customer_id: The household reference number; leave "" if unknown.
    """
    match = {k: v for k, v in {"activity_record_id": activity_record_id, "activity_participation_id": activity_participation_id, "customer_id": customer_id}.items() if v}
    rows = ctx.find("activity_records_log", **match)
    return str(rows) if rows else f"No participation record found for {match}."


@tool(owner="agent", rw="read")
def find_device_loans(ctx: ToolContext, device_loan_id: str = "", customer_id: str = "", student_id: str = "") -> str:
    """Look up student technology device loans: loan type, device type, campus, school year, asset tag, service year, status, and the checkout, plan enrollment, repair, loss report and return dates.

    Supply any reference number you already hold; every criterion is optional and the
    criteria given must all match. Returns every matching device loan with all of its details, or a
    short message saying none was found.

    Args:
        device_loan_id: The device loan reference number; leave "" if unknown.
        customer_id: The household reference number; leave "" if unknown.
        student_id: The student reference number; leave "" if unknown.
    """
    match = {k: v for k, v in {"device_loan_id": device_loan_id, "customer_id": customer_id, "student_id": student_id}.items() if v}
    rows = ctx.find("device_loans", **match)
    return str(rows) if rows else f"No device loan found for {match}."


@tool(owner="agent", rw="read")
def find_device_ledger(ctx: ToolContext, device_ledger_id: str = "", device_loan_id: str = "", customer_id: str = "", device_incident_id: str = "", source_device_ledger_id: str = "") -> str:
    """Look up the charges history of a device loan: protection plan fees, repair, loss, accessory and unreturned device charges, payments, credits and refunds.

    Supply any reference number you already hold; every criterion is optional and the
    criteria given must all match. Returns every matching device charge entry with all of its details, or a
    short message saying none was found.

    Args:
        device_ledger_id: The reference number of the device charge entry itself; leave "" if unknown.
        device_loan_id: The device loan reference number; leave "" if unknown.
        customer_id: The household reference number; leave "" if unknown.
        device_incident_id: The device incident reference number; leave "" if unknown.
        source_device_ledger_id: The reference number of the original charge a credit relates to; leave "" if unknown.
    """
    match = {k: v for k, v in {"device_ledger_id": device_ledger_id, "device_loan_id": device_loan_id, "customer_id": customer_id, "device_incident_id": device_incident_id, "source_device_ledger_id": source_device_ledger_id}.items() if v}
    rows = ctx.find("device_ledger", **match)
    return str(rows) if rows else f"No device charge entry found for {match}."


@tool(owner="agent", rw="read")
def find_device_incidents(ctx: ToolContext, device_incident_id: str = "", device_loan_id: str = "", customer_id: str = "") -> str:
    """Look up the damage, loss, theft and accessory incidents recorded on a device loan.

    Supply any reference number you already hold; every criterion is optional and the
    criteria given must all match. Returns every matching device incident with all of its details, or a
    short message saying none was found.

    Args:
        device_incident_id: The device incident reference number; leave "" if unknown.
        device_loan_id: The device loan reference number; leave "" if unknown.
        customer_id: The household reference number; leave "" if unknown.
    """
    match = {k: v for k, v in {"device_incident_id": device_incident_id, "device_loan_id": device_loan_id, "customer_id": customer_id}.items() if v}
    rows = ctx.find("device_incidents", **match)
    return str(rows) if rows else f"No device incident found for {match}."


@tool(owner="agent", rw="read")
def find_instrument_checkouts(ctx: ToolContext, instrument_checkout_id: str = "", customer_id: str = "", student_id: str = "") -> str:
    """Look up fine arts instrument checkouts: usage type, instrument and serial number, campus, school year, status, and the checkout, due-back, repair, overdue, loss and return dates.

    Supply any reference number you already hold; every criterion is optional and the
    criteria given must all match. Returns every matching instrument checkout with all of its details, or a
    short message saying none was found.

    Args:
        instrument_checkout_id: The instrument checkout reference number; leave "" if unknown.
        customer_id: The household reference number; leave "" if unknown.
        student_id: The student reference number; leave "" if unknown.
    """
    match = {k: v for k, v in {"instrument_checkout_id": instrument_checkout_id, "customer_id": customer_id, "student_id": student_id}.items() if v}
    rows = ctx.find("instrument_checkouts", **match)
    return str(rows) if rows else f"No instrument checkout found for {match}."


@tool(owner="agent", rw="read")
def find_instrument_ledger(ctx: ToolContext, instrument_ledger_id: str = "", instrument_checkout_id: str = "", customer_id: str = "", source_instrument_ledger_id: str = "") -> str:
    """Look up the charges history of an instrument checkout: usage fees, late, cleaning, repair and replacement charges, payments, credits and refunds.

    Supply any reference number you already hold; every criterion is optional and the
    criteria given must all match. Returns every matching instrument charge entry with all of its details, or a
    short message saying none was found.

    Args:
        instrument_ledger_id: The reference number of the instrument charge entry itself; leave "" if unknown.
        instrument_checkout_id: The instrument checkout reference number; leave "" if unknown.
        customer_id: The household reference number; leave "" if unknown.
        source_instrument_ledger_id: The reference number of the original charge a credit relates to; leave "" if unknown.
    """
    match = {k: v for k, v in {"instrument_ledger_id": instrument_ledger_id, "instrument_checkout_id": instrument_checkout_id, "customer_id": customer_id, "source_instrument_ledger_id": source_instrument_ledger_id}.items() if v}
    rows = ctx.find("instrument_ledger", **match)
    return str(rows) if rows else f"No instrument charge entry found for {match}."


@tool(owner="agent", rw="read")
def find_instrument_condition_log(ctx: ToolContext, instrument_condition_id: str = "", instrument_checkout_id: str = "", customer_id: str = "") -> str:
    """Look up the condition reports recorded for an instrument checkout at checkout and at return.

    Supply any reference number you already hold; every criterion is optional and the
    criteria given must all match. Returns every matching condition report with all of its details, or a
    short message saying none was found.

    Args:
        instrument_condition_id: The reference number of the condition report itself; leave "" if unknown.
        instrument_checkout_id: The instrument checkout reference number; leave "" if unknown.
        customer_id: The household reference number; leave "" if unknown.
    """
    match = {k: v for k, v in {"instrument_condition_id": instrument_condition_id, "instrument_checkout_id": instrument_checkout_id, "customer_id": customer_id}.items() if v}
    rows = ctx.find("instrument_condition_log", **match)
    return str(rows) if rows else f"No condition report found for {match}."

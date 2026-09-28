"""Hidden task tools of the prescription_renewal_handling difficulty (Linden Ridge Medical Group).
Path: env/env_0025_multispecialty_physician_group/tasks/prescription_renewal_handling/task_tools.py

Each tool performs one atomic write on the Prescriptions & Renewals line and is reached only through
unlock_* -> call_*; its name is published only as the target_tool of an extended policy in
rx.extended.yaml. No tool checks eligibility, status, ownership, timing or any prerequisite: the
agent decides those from the policy and the records before calling.
"""

from erlbench import ToolContext, tool

# Calendar days a prescription of each class stays valid from its renewal date (charter tier
# parameter prescription_validity_days); the renewal's new last-fill date is that many days from the
# renewal date, counting the renewal date itself as day one.
_VALIDITY_DAYS = {
    "Acute Short-Course Prescription": 30,
    "Standard Maintenance Prescription": 365,
    "Monitored Maintenance Prescription": 365,
    "Schedule III-V Controlled Prescription": 180,
    "Schedule II Controlled Prescription": 90,
    "Specialty Medication Prescription": 365,
}


@tool(owner="user", rw="write")
def move_prescription_pharmacy_221e1a97(ctx: ToolContext, prescription_id: str, pharmacy_name: str,
                                        days_supply: int) -> str:
    """The patient moves one of their own prescriptions, with the fills it still authorizes, to the
    pharmacy they name, and records the days' supply each fill of that prescription will dispense
    there. One call changes that single prescription: the pharmacy it stands at becomes the named
    pharmacy, its count of pharmacy moves goes up by one, and its per-fill days' supply becomes the
    value given; the fills still authorized and the last date it may be filled stay as they were.
    On success the prescription lookup shows the new pharmacy, the new per-fill days' supply and the
    raised move count. The receipt echoes the prescription and the recorded values.

    Args:
        prescription_id: Id class — reference number of the patient's prescription being moved, as
            shown by the prescription lookup for this patient.
        pharmacy_name: Verbatim class — the pharmacy the patient names to receive the prescription,
            written exactly as the patient states it, with every word, digit and punctuation mark kept
            and nothing added, shortened or reworded (verbatim).
        days_supply: Fixed-format class — days' supply each fill of this prescription dispenses at the
            receiving pharmacy, a whole number of days written as an integer (format integer > 0, days),
            with no decimals and no unit text.

    Returns:
        A dictionary receipt: prescription_id (the prescription moved), pharmacy_name (the pharmacy it
        now stands at, as recorded), days_supply (integer days per fill now recorded), transfer_count
        (integer count of pharmacy moves of this prescription, this one included) and status, which reads
        "moved" when the move is recorded.
    """
    rows = ctx.find("prescriptions", prescription_id=prescription_id)
    moves = int((rows[0].get("transfer_count") if rows else 0) or 0) + 1
    ctx.update("prescriptions", prescription_id, pharmacy_name=pharmacy_name, transfer_count=moves,
               days_supply=int(days_supply))
    return str({"prescription_id": prescription_id, "pharmacy_name": pharmacy_name,
                "days_supply": int(days_supply), "transfer_count": moves, "status": "moved"})


@tool(owner="agent", rw="write")
def authorize_replacement_fill_7c6c01e8(ctx: ToolContext, prescription_id: str, days_supply_per_fill: int,
                                        police_report_number: str = "") -> str:
    """Authorize one replacement fill on a prescription for medication the patient lost, had stolen or
    had damaged. One call posts a single fill authorization with reason replacement_fill, dated today,
    for exactly one fill of the given days' supply, and raises the fills the prescription still
    authorizes by one; the pharmacy on the prescription can dispense that fill. On success the
    fill history shows the new replacement authorization and the prescription lookup shows one more
    fill remaining. The receipt gives the reference of the new authorization entry.

    Args:
        prescription_id: Id class — reference number of the prescription the replacement is posted
            on, as shown by the prescription lookup for this patient.
        days_supply_per_fill: Fixed-format class — days' supply of the single replacement fill, a whole
            number of days written as an integer (format integer > 0, days), with no decimals and no
            unit text.
        police_report_number: Verbatim class — police report number the patient gives for stolen
            medication, copied exactly as the patient says it, every letter, digit and dash kept and
            nothing added or removed; leave it empty when the patient gives none (verbatim).

    Returns:
        A dictionary receipt: rx_event_id (reference of the new replacement authorization entry),
        prescription_id, fills (always 1), days_supply_per_fill (integer days of the replacement fill),
        authorization_reason ("replacement_fill"), fill_date (today, YYYY-MM-DD), refills_remaining
        (integer fills the prescription authorizes, this one included) and status, which reads "authorized"
        when the replacement is posted.
    """
    rows = ctx.find("prescriptions", prescription_id=prescription_id)
    rx = rows[0] if rows else {}
    today = ctx.now()[:10]
    rid = ctx.make_id("rxe_", prescription_id, days_supply_per_fill, police_report_number, today)
    ctx.create("rx_events", rid, rx_event_id=rid, prescription_id=prescription_id,
               customer_id=rx.get("customer_id", ""), event_type="rx_fills_authorized", fill_date=today,
               fills=1, days_supply_per_fill=int(days_supply_per_fill),
               authorization_reason="replacement_fill", fill_basis="none", dispensing_pharmacy="",
               void_reason="none", police_report_number=police_report_number)
    remaining = int(rx.get("refills_remaining") or 0) + 1
    ctx.update("prescriptions", prescription_id, refills_remaining=remaining)
    return str({"rx_event_id": rid, "prescription_id": prescription_id, "fills": 1,
                "days_supply_per_fill": int(days_supply_per_fill), "authorization_reason": "replacement_fill",
                "fill_date": today, "refills_remaining": remaining, "status": "authorized"})


@tool(owner="user", rw="write")
def sign_controlled_agreement_46ef2e3a(ctx: ToolContext, prescription_id: str, days_supply: int) -> str:
    """The patient signs a new controlled-substance agreement for one of their controlled
    prescriptions and, by signing, accepts the days' supply each fill of that prescription will
    dispense under the agreement. One call records on that prescription that the agreement was signed
    today and sets its per-fill days' supply to the value given; nothing else on the prescription
    changes. On success the prescription lookup shows today's date as the agreement signature date and
    the new per-fill days' supply. The receipt echoes the prescription and the recorded values.

    Args:
        prescription_id: Id class — reference number of the controlled prescription the agreement
            covers, as shown by the prescription lookup for this patient.
        days_supply: Fixed-format class — days' supply each fill of the prescription dispenses under the
            signed agreement, a whole number of days written as an integer (format integer > 0, days),
            with no decimals and no unit text.

    Returns:
        A dictionary receipt: prescription_id, controlled_agreement_signed_date (today, YYYY-MM-DD),
        days_supply (integer days per fill now recorded) and status, which reads "signed" when the
        signature is recorded.
    """
    today = ctx.now()[:10]
    ctx.update("prescriptions", prescription_id, controlled_agreement_signed_date=today,
               days_supply=int(days_supply))
    return str({"prescription_id": prescription_id, "controlled_agreement_signed_date": today,
                "days_supply": int(days_supply), "status": "signed"})


@tool(owner="agent", rw="write")
def approve_prescription_renewal_192bec69(ctx: ToolContext, prescription_id: str, appointment_id: str,
                                          fills: int) -> str:
    """Approve a pending or held renewal of a prescription and grant its new fills. One call makes the
    prescription active again with today as its renewal date, a new last date to fill of today plus the
    class's validity period (today counted as day one), and no hold; any fills left on the old
    authorization are voided as superseded_by_renewal, and one new fill authorization with reason
    renewal is posted for the given number of fills at the prescription's current per-fill days'
    supply, which become the fills it still authorizes. On success the prescription lookup shows it
    active with the new dates and fills, and the fill history shows the void, where there was one,
    and the renewal authorization. The receipt gives the reference of the new authorization entry.

    Args:
        prescription_id: Id class — reference number of the prescription whose renewal is approved, as
            shown by the prescription lookup for this patient.
        appointment_id: Id class — reference number of the patient's completed visit with the
            prescribing department that keeps the visit requirement current, as shown by the
            appointment lookup for this patient.
        fills: Fixed-format class — number of fills the renewal authorizes, the initial fill included, a
            whole number written as an integer (format integer > 0, fills); it also becomes the fills
            the prescription still authorizes (integer >= 0, fills).

    Returns:
        A dictionary receipt: rx_event_id (reference of the new renewal authorization entry),
        prescription_id, appointment_id (the qualifying visit), fills (integer fills granted),
        days_supply_per_fill (integer days per fill), voided_fills (integer fills voided from the old
        authorization, 0 when none), renewed_date (today, YYYY-MM-DD), expiration_date (new last date to
        fill, YYYY-MM-DD) and status, which reads "active" when the renewal is approved.
    """
    rows = ctx.find("prescriptions", prescription_id=prescription_id)
    rx = rows[0] if rows else {}
    today = ctx.now()[:10]
    old = int(rx.get("refills_remaining") or 0)
    per_fill = int(rx.get("days_supply") or 0)
    if old:
        vid = ctx.make_id("rxv_", prescription_id, old, today)
        ctx.create("rx_events", vid, rx_event_id=vid, prescription_id=prescription_id,
                   customer_id=rx.get("customer_id", ""), event_type="rx_fills_voided", fill_date=today,
                   fills=old, days_supply_per_fill=0, authorization_reason="none", fill_basis="none",
                   dispensing_pharmacy="", void_reason="superseded_by_renewal", police_report_number="")
    rid = ctx.make_id("rxa_", prescription_id, appointment_id, fills, today)
    ctx.create("rx_events", rid, rx_event_id=rid, prescription_id=prescription_id,
               customer_id=rx.get("customer_id", ""), event_type="rx_fills_authorized", fill_date=today,
               fills=int(fills), days_supply_per_fill=per_fill, authorization_reason="renewal",
               fill_basis="none", dispensing_pharmacy="", void_reason="none", police_report_number="")
    days = _VALIDITY_DAYS.get(rx.get("variant_name"), 365)
    # Last date to fill = today + validity - 1, in proleptic Gregorian day numbers (integer arithmetic).
    y, m, d = (int(part) for part in today.split("-"))
    y -= m <= 2
    era = y // 400
    yoe = y - era * 400
    doe = yoe * 365 + yoe // 4 - yoe // 100 + (153 * (m + (-3 if m > 2 else 9)) + 2) // 5 + d - 1
    n = era * 146097 + doe + days - 1
    era = n // 146097
    doe = n - era * 146097
    yoe = (doe - doe // 1460 + doe // 36524 - doe // 146096) // 365
    doy = doe - (365 * yoe + yoe // 4 - yoe // 100)
    mp = (5 * doy + 2) // 153
    m = mp + (3 if mp < 10 else -9)
    expires = f"{yoe + era * 400 + (m <= 2):04d}-{m:02d}-{doy - (153 * mp + 2) // 5 + 1:02d}"
    ctx.update("prescriptions", prescription_id, status="active", renewed_date=today, expiration_date=expires,
               hold_reason="none", hold_started_date="", refills_remaining=int(fills))
    return str({"rx_event_id": rid, "prescription_id": prescription_id, "appointment_id": appointment_id,
                "fills": int(fills), "days_supply_per_fill": per_fill, "voided_fills": old,
                "renewed_date": today, "expiration_date": expires, "status": "active"})

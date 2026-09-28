"""Shared tools for env_0025_multispecialty_physician_group (Linden Ridge Medical Group).
Output of the erl-scenario-blueprint skill.
Path: env/env_0025_multispecialty_physician_group/blueprint/share_tools.py

Every tool here is a SHARE tool: always present in its owner's tool list and callable in every task.
This module holds exactly the scenario-wide foundation:
  - one record finder per table in db_schema.json (the customers finder doubles as the identity entry),
  - the identity-verification write (K = 2 matching credentials),
  - the transfer-to-human write (reason POLICY_NOT_COVERED or CUSTOMER_REQUESTED; R = 2 explicit requests).
Customer-originated writes (signing, consenting, cancelling their own contracts) are hidden task tools
authored per difficulty, never here. No finder encodes eligibility, status, ownership or timing rules.
"""

from erlbench import ToolContext, tool


def _norm(value) -> str:
    # Normalise a spoken or typed credential for comparison: casefold, letters and digits only.
    return "".join(ch for ch in str(value).casefold() if ch.isalnum())


# --------------------------------------------------------------------------- identity entry
@tool(owner="agent", rw="read")
def find_customers(ctx: ToolContext, customer_id: str = "", name: str = "", phone_number: str = "",
                   email: str = "", date_of_birth: str = "", medical_record_number: str = "") -> str:
    """Look up a patient profile at Linden Ridge Medical Group to establish whose records this call is about.

    Search by the patient reference number, or by what a caller can naturally state: the full name, the
    phone number on file, the email address on file, the date of birth, or the medical record number
    printed on visit summaries and statements. Every criterion is optional; supply whichever are known,
    and add another one when several patients match. Spacing, punctuation and letter case in what the
    caller says do not matter. The returned profile shows the patient reference number, legal name, date
    of birth, contact details, medical record number, the date the profile was opened, the MyLinden portal
    status and the assigned primary care clinician. Finding a profile does not confirm that the caller is
    that patient; identity is confirmed separately.

    Args:
        customer_id: Patient reference number (for example the value shown as customer_id on a profile); leave "" if unknown.
        name: Patient's full legal name as the caller states it; leave "" if not provided.
        phone_number: Phone number on the profile, 10 digits (punctuation is ignored); leave "" if not provided.
        email: Email address on the profile; leave "" if not provided.
        date_of_birth: Date of birth as YYYY-MM-DD; leave "" if not provided.
        medical_record_number: Medical record number, "LR" followed by 7 digits; leave "" if not provided.
    """
    match = {k: v for k, v in {"customer_id": customer_id, "name": name, "phone_number": phone_number,
                               "email": email, "date_of_birth": date_of_birth,
                               "medical_record_number": medical_record_number}.items() if v}
    if not match:
        return "Error: provide at least one reference number or profile detail to find the patient."
    rows = ctx.fuzzy_find("customers", **match)
    if not rows:
        return f"No patient profile matches {match}."
    if len(rows) > 1:
        return f"Error: {len(rows)} patient profiles match {match}; ask the caller for one more detail to tell them apart."
    return str(rows[0])


# --------------------------------------------------------------------------- scenario logs
@tool(owner="agent", rw="read")
def find_identity_verifications(ctx: ToolContext, verification_id: str = "", customer_id: str = "") -> str:
    """Look up the identity-verification outcome recorded for a patient during this service interaction.

    Returns whether the caller's identity has been confirmed for the patient and when it was last checked.
    Search by the verification reference or by the patient reference number; both are optional.

    Args:
        verification_id: Reference number of the verification outcome; leave "" if unknown.
        customer_id: Patient reference number the verification belongs to; leave "" if unknown.
    """
    match = {k: v for k, v in {"verification_id": verification_id, "customer_id": customer_id}.items() if v}
    rows = ctx.find("identity_verifications", **match)
    return str(rows) if rows else f"No identity verification recorded for {match}."


@tool(owner="agent", rw="read")
def find_human_handoffs(ctx: ToolContext, handoff_id: str = "", customer_id: str = "") -> str:
    """Look up transfers of a patient to a human representative, with the reason and time of each.

    Search by the transfer reference or by the patient reference number; both are optional.

    Args:
        handoff_id: Reference number of the transfer; leave "" if unknown.
        customer_id: Patient reference number; leave "" if unknown.
    """
    match = {k: v for k, v in {"handoff_id": handoff_id, "customer_id": customer_id}.items() if v}
    rows = ctx.find("human_handoffs", **match)
    return str(rows) if rows else f"No transfer to a human representative recorded for {match}."


# --------------------------------------------------------------------------- Patient Financial Account
@tool(owner="agent", rw="read")
def find_billing_accounts(ctx: ToolContext, billing_account_id: str = "", customer_id: str = "") -> str:
    """Look up a patient's Patient Financial Account.

    The account shows the financial class (for example Commercial PPO/POS Account or Self-Pay Account),
    its status, the insurance payer and member number on file, coverage effective and verification dates,
    the copays and remaining deductible returned by the payer, the current balance owed (negative means a
    credit), any billing hold and its reason, final-notice and collection-agency dates, any
    financial-hardship approval, the statement delivery channel and whether a card is on file. Search by
    the account reference or by the patient reference number.

    Args:
        billing_account_id: Reference number of the financial account; leave "" if unknown.
        customer_id: Patient reference number; leave "" if unknown.
    """
    match = {k: v for k, v in {"billing_account_id": billing_account_id, "customer_id": customer_id}.items() if v}
    rows = ctx.find("billing_accounts", **match)
    return str(rows) if rows else f"No financial account found for {match}."


@tool(owner="agent", rw="read")
def find_billing_transactions(ctx: ToolContext, billing_txn_id: str = "", billing_account_id: str = "",
                              customer_id: str = "", applies_to_txn_id: str = "") -> str:
    """Look up the ledger of a Patient Financial Account: charges, copays, payments, adjustments, refunds,
    returned payments and statements.

    Each entry shows its kind, posting date, date of service, encounter number, what a charge is for, the
    amount, any estimate given before the service, payment method and channel, adjustment reason, the
    entry it applies to, the statement sequence and the product line it came from. Search by the entry's
    own reference, the account, the patient, or the reference of the entry it applies to (for example to
    list every payment and adjustment applied to one charge).

    Args:
        billing_txn_id: Reference number of the ledger entry itself; leave "" if unknown.
        billing_account_id: Reference number of the financial account; leave "" if unknown.
        customer_id: Patient reference number; leave "" if unknown.
        applies_to_txn_id: Reference number of the charge or payment that entries were applied to; leave "" if unknown.
    """
    match = {k: v for k, v in {"billing_txn_id": billing_txn_id, "billing_account_id": billing_account_id,
                               "customer_id": customer_id, "applies_to_txn_id": applies_to_txn_id}.items() if v}
    rows = ctx.find("billing_transactions", **match)
    return str(rows) if rows else f"No financial account entries found for {match}."


@tool(owner="agent", rw="read")
def find_billing_cases(ctx: ToolContext, billing_case_id: str = "", customer_id: str = "",
                       billing_account_id: str = "", billing_txn_id: str = "") -> str:
    """Look up billing cases opened for a patient: balance disputes, itemized statement requests,
    financial-hardship reviews, estimate disputes, coordination-of-benefits and insurance reviews, estate
    reviews and account-closure requests, each with its status and opening time.

    Search by the case reference, the patient, the financial account, or the charge a case concerns.

    Args:
        billing_case_id: Reference number of the billing case; leave "" if unknown.
        customer_id: Patient reference number; leave "" if unknown.
        billing_account_id: Reference number of the financial account; leave "" if unknown.
        billing_txn_id: Reference number of the charge the case concerns; leave "" if unknown.
    """
    match = {k: v for k, v in {"billing_case_id": billing_case_id, "customer_id": customer_id,
                               "billing_account_id": billing_account_id,
                               "billing_txn_id": billing_txn_id}.items() if v}
    rows = ctx.find("billing_cases", **match)
    return str(rows) if rows else f"No billing cases found for {match}."


# --------------------------------------------------------------------------- In-Person Appointments
@tool(owner="agent", rw="read")
def find_appointments(ctx: ToolContext, appointment_id: str = "", customer_id: str = "", referral_id: str = "") -> str:
    """Look up a patient's in-person clinic appointments.

    Each appointment shows its visit type, status, booking date, scheduled date and time, department,
    clinician, clinic location, booking channel, encounter number, the referral or authorization it is
    booked against, how many times the patient has rescheduled it, confirmation and check-in details,
    cancellation time, reason and timing, any booking deposit held, and the date it closed. Search by the
    appointment reference, the patient, or a referral to list the visits booked against it.

    Args:
        appointment_id: Reference number of the appointment; leave "" if unknown.
        customer_id: Patient reference number; leave "" if unknown.
        referral_id: Reference number of the referral or authorization the visits are booked against; leave "" if unknown.
    """
    match = {k: v for k, v in {"appointment_id": appointment_id, "customer_id": customer_id,
                               "referral_id": referral_id}.items() if v}
    rows = ctx.find("appointments", **match)
    return str(rows) if rows else f"No appointments found for {match}."


@tool(owner="agent", rw="read")
def find_appointment_events(ctx: ToolContext, appointment_event_id: str = "", appointment_id: str = "",
                            customer_id: str = "", applies_to_event_id: str = "") -> str:
    """Look up the fee and deposit history of in-person appointments: no-show and late-cancellation fees
    assessed or waived (with the waiver reason), and booking deposits collected, applied, refunded or
    forfeited.

    Search by the entry's own reference, the appointment, the patient, or the fee entry a waiver removed.

    Args:
        appointment_event_id: Reference number of the entry itself; leave "" if unknown.
        appointment_id: Reference number of the appointment; leave "" if unknown.
        customer_id: Patient reference number; leave "" if unknown.
        applies_to_event_id: Reference number of the assessed fee entry a waiver applies to; leave "" if unknown.
    """
    match = {k: v for k, v in {"appointment_event_id": appointment_event_id, "appointment_id": appointment_id,
                               "customer_id": customer_id, "applies_to_event_id": applies_to_event_id}.items() if v}
    rows = ctx.find("appointment_events", **match)
    return str(rows) if rows else f"No appointment fee or deposit entries found for {match}."


@tool(owner="agent", rw="read")
def find_appointment_waitlist(ctx: ToolContext, waitlist_id: str = "", customer_id: str = "",
                              appointment_id: str = "") -> str:
    """Look up earlier-slot waitlist entries: the visit type and department waited for, the latest
    acceptable date, the appointment the patient wants moved, the entry's status and when it was created.

    Search by the waitlist entry reference, the patient, or the appointment concerned.

    Args:
        waitlist_id: Reference number of the waitlist entry; leave "" if unknown.
        customer_id: Patient reference number; leave "" if unknown.
        appointment_id: Reference number of the appointment the patient wants moved earlier; leave "" if unknown.
    """
    match = {k: v for k, v in {"waitlist_id": waitlist_id, "customer_id": customer_id,
                               "appointment_id": appointment_id}.items() if v}
    rows = ctx.find("appointment_waitlist", **match)
    return str(rows) if rows else f"No waitlist entries found for {match}."


# --------------------------------------------------------------------------- Referrals & Prior Authorizations
@tool(owner="agent", rw="read")
def find_referrals(ctx: ToolContext, referral_id: str = "", customer_id: str = "") -> str:
    """Look up a patient's referrals and prior authorizations.

    Each shows its type (for example HMO Specialist Referral or Advanced Imaging Prior Authorization),
    status, specialty, referring clinician, authorized provider or site, urgency, request, submission and
    decision dates, payer authorization number, validity dates, units remaining, extensions granted, the
    basis of the latest approval, any denial reason, appeal date and level, cancellation reason and closing
    date. Search by the referral reference or by the patient.

    Args:
        referral_id: Reference number of the referral or authorization; leave "" if unknown.
        customer_id: Patient reference number; leave "" if unknown.
    """
    match = {k: v for k, v in {"referral_id": referral_id, "customer_id": customer_id}.items() if v}
    rows = ctx.find("referrals", **match)
    return str(rows) if rows else f"No referrals or authorizations found for {match}."


@tool(owner="agent", rw="read")
def find_referral_events(ctx: ToolContext, referral_event_id: str = "", referral_id: str = "",
                         customer_id: str = "", applies_to_unit_event_id: str = "") -> str:
    """Look up the unit history of referrals and authorizations: units granted (and why), units used by
    each completed visit with its encounter number, units restored after an error, and units that lapsed.

    Search by the entry's own reference, the referral, the patient, or the unit-use entry a restoration
    reverses.

    Args:
        referral_event_id: Reference number of the unit entry itself; leave "" if unknown.
        referral_id: Reference number of the referral or authorization; leave "" if unknown.
        customer_id: Patient reference number; leave "" if unknown.
        applies_to_unit_event_id: Reference number of the unit-use entry a restoration applies to; leave "" if unknown.
    """
    match = {k: v for k, v in {"referral_event_id": referral_event_id, "referral_id": referral_id,
                               "customer_id": customer_id,
                               "applies_to_unit_event_id": applies_to_unit_event_id}.items() if v}
    rows = ctx.find("referral_events", **match)
    return str(rows) if rows else f"No referral unit entries found for {match}."


@tool(owner="agent", rw="read")
def find_referral_requests(ctx: ToolContext, referral_request_id: str = "", customer_id: str = "",
                           referral_id: str = "") -> str:
    """Look up service requests filed on referrals: appeals, extensions, peer-to-peer reviews, provider
    changes, retroactive authorizations and out-of-network cost-share acknowledgements, with their status
    and opening time.

    Search by the request reference, the patient, or the referral concerned.

    Args:
        referral_request_id: Reference number of the referral service request; leave "" if unknown.
        customer_id: Patient reference number; leave "" if unknown.
        referral_id: Reference number of the referral the request concerns; leave "" if unknown.
    """
    match = {k: v for k, v in {"referral_request_id": referral_request_id, "customer_id": customer_id,
                               "referral_id": referral_id}.items() if v}
    rows = ctx.find("referral_requests", **match)
    return str(rows) if rows else f"No referral service requests found for {match}."


# --------------------------------------------------------------------------- Prescriptions & Renewals
@tool(owner="agent", rw="read")
def find_prescriptions(ctx: ToolContext, prescription_id: str = "", customer_id: str = "") -> str:
    """Look up a patient's prescriptions.

    Each shows its class (for example Standard Maintenance Prescription), status, medication and strength,
    days' supply, prescriber and department, pharmacy, fills remaining, expiration date, the latest renewal
    request and approval, any hold and why, prior-authorization status, the latest monitoring lab, drug
    screen, controlled-substance agreement and monitoring-database check dates, pharmacy transfers, and the
    reason and date it was discontinued or expired. Search by the prescription reference or the patient.

    Args:
        prescription_id: Reference number of the prescription; leave "" if unknown.
        customer_id: Patient reference number; leave "" if unknown.
    """
    match = {k: v for k, v in {"prescription_id": prescription_id, "customer_id": customer_id}.items() if v}
    rows = ctx.find("prescriptions", **match)
    return str(rows) if rows else f"No prescriptions found for {match}."


@tool(owner="agent", rw="read")
def find_rx_events(ctx: ToolContext, rx_event_id: str = "", prescription_id: str = "", customer_id: str = "") -> str:
    """Look up the fill history of prescriptions: fills authorized (new prescription, renewal, replacement
    or bridge), fills dispensed with their date, days' supply, basis and dispensing pharmacy, and fills
    voided with the reason.

    Search by the entry's own reference, the prescription, or the patient.

    Args:
        rx_event_id: Reference number of the fill entry itself; leave "" if unknown.
        prescription_id: Reference number of the prescription; leave "" if unknown.
        customer_id: Patient reference number; leave "" if unknown.
    """
    match = {k: v for k, v in {"rx_event_id": rx_event_id, "prescription_id": prescription_id,
                               "customer_id": customer_id}.items() if v}
    rows = ctx.find("rx_events", **match)
    return str(rows) if rows else f"No prescription fill entries found for {match}."


# --------------------------------------------------------------------------- Patient Payment Plans
@tool(owner="agent", rw="read")
def find_payment_plans(ctx: ToolContext, payment_plan_id: str = "", customer_id: str = "",
                       billing_account_id: str = "") -> str:
    """Look up a patient's payment plans.

    Each plan shows its tier (for example 6-Month Interest-Free Plan), status, proposal and signing dates,
    first due date and due day, term, installment, down payment, remaining balance, autopay set-up,
    delinquency, default and reinstatement dates and counts, modification, due-day change, pause and term
    extension counts, and how and when it ended. Search by the plan reference, the patient, or the
    financial account.

    Args:
        payment_plan_id: Reference number of the payment plan; leave "" if unknown.
        customer_id: Patient reference number; leave "" if unknown.
        billing_account_id: Reference number of the financial account the plan covers; leave "" if unknown.
    """
    match = {k: v for k, v in {"payment_plan_id": payment_plan_id, "customer_id": customer_id,
                               "billing_account_id": billing_account_id}.items() if v}
    rows = ctx.find("payment_plans", **match)
    return str(rows) if rows else f"No payment plans found for {match}."


@tool(owner="agent", rw="read")
def find_payplan_transactions(ctx: ToolContext, payplan_txn_id: str = "", payment_plan_id: str = "",
                              customer_id: str = "", billing_txn_id: str = "") -> str:
    """Look up the ledger of payment plans: charges enrolled (and why), installments paid or missed with
    their numbers, extra payments (down payment, prepayment, payoff), reductions of enrolled charges and
    balances released back to standard billing.

    Search by the entry's own reference, the plan, the patient, or a financial-account charge to see
    whether and how it is enrolled.

    Args:
        payplan_txn_id: Reference number of the plan entry itself; leave "" if unknown.
        payment_plan_id: Reference number of the payment plan; leave "" if unknown.
        customer_id: Patient reference number; leave "" if unknown.
        billing_txn_id: Reference number of the financial-account charge concerned; leave "" if unknown.
    """
    match = {k: v for k, v in {"payplan_txn_id": payplan_txn_id, "payment_plan_id": payment_plan_id,
                               "customer_id": customer_id, "billing_txn_id": billing_txn_id}.items() if v}
    rows = ctx.find("payplan_transactions", **match)
    return str(rows) if rows else f"No payment plan entries found for {match}."


# --------------------------------------------------------------------------- Virtual Care
@tool(owner="agent", rw="read")
def find_telehealth_visits(ctx: ToolContext, telehealth_visit_id: str = "", customer_id: str = "",
                           referral_id: str = "", converted_appointment_id: str = "") -> str:
    """Look up a patient's virtual care encounters (portal e-visits, phone visits, video visits and
    on-demand virtual urgent care).

    Each shows its type, status, request and scheduled dates and time, department, clinician, encounter
    number, the state the patient was located in, any referral it is covered by, prepayment held,
    reschedules, connected minutes and how it ended, cancellation timing, any in-person appointment it was
    converted to, and its closing date. Search by the encounter reference, the patient, the referral, or
    the in-person appointment it was converted to.

    Args:
        telehealth_visit_id: Reference number of the virtual encounter; leave "" if unknown.
        customer_id: Patient reference number; leave "" if unknown.
        referral_id: Reference number of the referral covering the encounter; leave "" if unknown.
        converted_appointment_id: Reference number of the in-person appointment the encounter was converted to; leave "" if unknown.
    """
    match = {k: v for k, v in {"telehealth_visit_id": telehealth_visit_id, "customer_id": customer_id,
                               "referral_id": referral_id,
                               "converted_appointment_id": converted_appointment_id}.items() if v}
    rows = ctx.find("telehealth_visits", **match)
    return str(rows) if rows else f"No virtual care encounters found for {match}."


@tool(owner="agent", rw="read")
def find_telehealth_events(ctx: ToolContext, telehealth_event_id: str = "", telehealth_visit_id: str = "",
                           customer_id: str = "", applies_to_event_id: str = "") -> str:
    """Look up prepayments and fees of virtual care encounters: prepayments collected and what became of
    them, and no-show, late-cancellation or self-pay charges assessed or waived.

    Search by the entry's own reference, the encounter, the patient, or the fee entry a waiver removed.

    Args:
        telehealth_event_id: Reference number of the entry itself; leave "" if unknown.
        telehealth_visit_id: Reference number of the virtual encounter; leave "" if unknown.
        customer_id: Patient reference number; leave "" if unknown.
        applies_to_event_id: Reference number of the assessed fee entry a waiver applies to; leave "" if unknown.
    """
    match = {k: v for k, v in {"telehealth_event_id": telehealth_event_id,
                               "telehealth_visit_id": telehealth_visit_id, "customer_id": customer_id,
                               "applies_to_event_id": applies_to_event_id}.items() if v}
    rows = ctx.find("telehealth_events", **match)
    return str(rows) if rows else f"No virtual care fee or prepayment entries found for {match}."


# --------------------------------------------------------------------------- Medical Records Requests
@tool(owner="agent", rw="read")
def find_records_requests(ctx: ToolContext, records_request_id: str = "", customer_id: str = "") -> str:
    """Look up requests to release a patient's medical records.

    Each shows its type, status, how and when it arrived, the recipient and recipient kind, delivery
    method, scope and date range requested, whether it was expedited, the fee still owed, authorization
    request, signature and expiration dates, the due date and any extension notice, fulfilment date and
    pages released, and any denial ground or cancellation reason. Search by the request reference or the
    patient.

    Args:
        records_request_id: Reference number of the records request; leave "" if unknown.
        customer_id: Patient reference number; leave "" if unknown.
    """
    match = {k: v for k, v in {"records_request_id": records_request_id, "customer_id": customer_id}.items() if v}
    rows = ctx.find("records_requests", **match)
    return str(rows) if rows else f"No records requests found for {match}."


@tool(owner="agent", rw="read")
def find_records_events(ctx: ToolContext, records_event_id: str = "", records_request_id: str = "",
                        customer_id: str = "", applies_to_event_id: str = "") -> str:
    """Look up the fee history of records requests: fee components assessed, payments, waivers with their
    reason, refunds, and fees moved to the patient's financial account.

    Search by the entry's own reference, the request, the patient, or the payment entry a refund returned.

    Args:
        records_event_id: Reference number of the fee entry itself; leave "" if unknown.
        records_request_id: Reference number of the records request; leave "" if unknown.
        customer_id: Patient reference number; leave "" if unknown.
        applies_to_event_id: Reference number of the payment entry a refund applies to; leave "" if unknown.
    """
    match = {k: v for k, v in {"records_event_id": records_event_id, "records_request_id": records_request_id,
                               "customer_id": customer_id, "applies_to_event_id": applies_to_event_id}.items() if v}
    rows = ctx.find("records_events", **match)
    return str(rows) if rows else f"No records fee entries found for {match}."


# --------------------------------------------------------------------------- Linden Memberships
@tool(owner="agent", rw="read")
def find_memberships(ctx: ToolContext, membership_id: str = "", customer_id: str = "") -> str:
    """Look up a patient's Linden membership.

    The membership shows its tier (for example Linden Plus Membership), status, enrollment and start
    dates, dues cycle and amount, dependents, commitment end date, current period, member visit credits
    remaining, freeze dates and months used, past-due date, any pending cancellation notice and its
    effective date, the latest tier change, and how and when it ended. Search by the membership reference
    or the patient.

    Args:
        membership_id: Reference number of the membership; leave "" if unknown.
        customer_id: Patient reference number; leave "" if unknown.
    """
    match = {k: v for k, v in {"membership_id": membership_id, "customer_id": customer_id}.items() if v}
    rows = ctx.find("memberships", **match)
    return str(rows) if rows else f"No memberships found for {match}."


@tool(owner="agent", rw="read")
def find_membership_events(ctx: ToolContext, membership_event_id: str = "", membership_id: str = "",
                           customer_id: str = "") -> str:
    """Look up the dues and visit-credit history of a membership: dues and fees billed per period, dues
    credited back, member visit credits granted, used (with the encounter) and expired.

    Search by the entry's own reference, the membership, or the patient.

    Args:
        membership_event_id: Reference number of the membership entry itself; leave "" if unknown.
        membership_id: Reference number of the membership; leave "" if unknown.
        customer_id: Patient reference number; leave "" if unknown.
    """
    match = {k: v for k, v in {"membership_event_id": membership_event_id, "membership_id": membership_id,
                               "customer_id": customer_id}.items() if v}
    rows = ctx.find("membership_events", **match)
    return str(rows) if rows else f"No membership entries found for {match}."


@tool(owner="agent", rw="read")
def find_membership_requests(ctx: ToolContext, membership_request_id: str = "", customer_id: str = "",
                             membership_id: str = "") -> str:
    """Look up requests a member has submitted on a membership: freezes, tier changes, dues-cycle changes and
    dependent changes, each with the target tier where relevant, the start date, the months of a freeze,
    its status and when it was submitted.

    Search by the request reference, the member, or the membership concerned.

    Args:
        membership_request_id: Reference number of the membership request; leave "" if unknown.
        customer_id: Patient reference number of the member; leave "" if unknown.
        membership_id: Reference number of the membership; leave "" if unknown.
    """
    match = {k: v for k, v in {"membership_request_id": membership_request_id, "customer_id": customer_id,
                               "membership_id": membership_id}.items() if v}
    rows = ctx.find("membership_requests", **match)
    return str(rows) if rows else f"No membership requests found for {match}."


# --------------------------------------------------------------------------- identity verification
@tool(owner="agent", rw="write")
def verify_patient_identity(ctx: ToolContext, customer_id: str, date_of_birth: str = "", phone_number: str = "",
                            email: str = "", medical_record_number: str = "", ssn_last4: str = "") -> str:
    """Confirm that the caller is the patient whose profile was found, and record the outcome for this
    interaction.

    Identity must be confirmed before any account detail is discussed or any request is acted on. This
    tool performs the comparison itself: each detail the caller states is compared with the patient
    profile, and identity is confirmed when at least 2 of them match. The patient reference number only
    selects the profile to compare against; it never counts as a match, and neither does the patient's
    name. Callers usually state only some details, so pass exactly the values the caller gave and leave
    the rest empty. If a first attempt falls short, ask for another detail on file and call again; once
    identity is confirmed it stays confirmed.

    Args:
        customer_id: Patient reference number read from the patient profile lookup. Required; used only to select the profile.
        date_of_birth: Date of birth the caller states, as YYYY-MM-DD; leave "" if not stated.
        phone_number: Phone number the caller states, 10 digits; leave "" if not stated.
        email: Email address the caller states; leave "" if not stated.
        medical_record_number: Medical record number the caller states, "LR" followed by 7 digits; leave "" if not stated.
        ssn_last4: Last four digits of the Social Security number the caller states; leave "" if not stated.
    """
    if not customer_id:
        return "Error: customer_id is required; look the patient up first and pass their reference number."
    rows = ctx.find("customers", customer_id=customer_id)
    if not rows:
        return f"Error: no patient profile {customer_id}; cannot verify identity."
    rec = rows[0]
    # The tool owns the comparison; the locator customer_id is deliberately not a credential.
    supplied = {"date_of_birth": date_of_birth, "phone_number": phone_number, "email": email,
                "medical_record_number": medical_record_number, "ssn_last4": ssn_last4}
    matched = sum(1 for field, value in supplied.items()
                  if value and rec.get(field) and _norm(rec.get(field)) == _norm(value))
    verified = matched >= 2
    rid = ctx.make_id("ver_", customer_id)
    # Store only the reproducible outcome; upsert and never downgrade a confirmed identity.
    prior = ctx.find("identity_verifications", verification_id=rid)
    verified = verified or bool(prior and prior[0].get("verified"))
    if prior:
        ctx.update("identity_verifications", rid, verified=verified, verified_at=ctx.now())
    else:
        ctx.create("identity_verifications", rid, verification_id=rid, customer_id=customer_id,
                   verified=verified, verified_at=ctx.now())
    if verified:
        return f"Identity confirmed for patient {customer_id} ({matched} detail(s) matched in this attempt)."
    return (f"Identity NOT confirmed for patient {customer_id}: only {matched} of the 2 required details "
            "matched. Ask the caller for another detail on file and try again.")


# --------------------------------------------------------------------------- transfer to a human
@tool(owner="agent", rw="write")
def transfer_to_human_agent(ctx: ToolContext, customer_id: str, reason: str) -> str:
    """Transfer the patient to a human patient-services representative and record the transfer with its
    reason.

    Use it in exactly two situations. POLICY_NOT_COVERED: the patient's request is one that no Linden Ridge
    policy allows you to resolve (it falls outside every rule you can apply, or needs a decision reserved
    to staff such as a practice manager or medical director). CUSTOMER_REQUESTED: the patient has
    explicitly asked to speak with a human representative 2 times in this conversation.

    Args:
        customer_id: Patient reference number read from the patient profile lookup (the profile must exist).
        reason: Why the patient is transferred; exactly one of POLICY_NOT_COVERED or CUSTOMER_REQUESTED, never free text.
    """
    allowed = {"POLICY_NOT_COVERED", "CUSTOMER_REQUESTED"}
    if reason not in allowed:
        return f"Error: unknown transfer reason '{reason}'. Valid: {', '.join(sorted(allowed))}."
    if not ctx.find("customers", customer_id=customer_id):
        return f"Error: no patient profile {customer_id}; cannot record the transfer."
    rid = ctx.make_id("hof_", customer_id, reason)
    ctx.create("human_handoffs", rid, handoff_id=rid, customer_id=customer_id,
               reason=reason, created_at=ctx.now())
    return f"Transfer to a human representative recorded for patient {customer_id} ({reason})."

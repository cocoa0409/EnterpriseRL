"""Shared tools for env_0073_regional_hospital_system (Riverbend Regional Health, Patient Financial Services & Scheduling).
Output of the erl-scenario-blueprint skill.

Every tool here is a SHARE tool, always present in its owner's tool list:
  - one record finder per stored record type (the customers finder doubles as the identity entry),
  - the identity-verification write (compares caller-stated credentials itself; passes at 2 matches),
  - the transfer-to-human write (two controlled reasons; customer-requested after 2 explicit asks).
Customer-originated business writes are hidden task tools in each difficulty's task_tools.py.
"""

from erlbench import ToolContext, tool


def _pick(**kwargs):
    # keep only the criteria the caller actually supplied
    return {k: v for k, v in kwargs.items() if v}


# ---------------------------------------------------------------- patient profile & logs

@tool(owner="agent", rw="read")
def find_customers(ctx: ToolContext, customer_id: str = "", full_name: str = "", phone_number: str = "",
                   email: str = "", date_of_birth: str = "", medical_record_number: str = "") -> str:
    """Look up a patient's registration profile to establish whose accounts this conversation is about.

    Search by the patient reference number, or by what a caller can naturally tell you: their name,
    the phone number or email on their registration, their date of birth, or the medical record
    number (MRN) printed on statements and wristbands. Give whatever is known; every criterion is
    optional, and the spoken form is matched loosely (spacing, punctuation and letter case do not
    matter). A match returns the full profile: name, date of birth, phone, email, MRN, last four of
    the Social Security number on file, mailing ZIP code, county of residence, preferred language for
    notices, and the date the profile was first registered. If several patients match, you are asked
    for one more detail. Finding a profile does not confirm the caller is that patient; identity is
    confirmed separately.

    Args:
        customer_id: The patient reference number, if already known; leave "" otherwise.
        full_name: The patient's full name as the caller says it; leave "" if not given.
        phone_number: The phone number on the registration, 10 digits (e.g. 9205550148); leave "" if not given.
        email: The email address on the registration; leave "" if not given.
        date_of_birth: The patient's date of birth as YYYY-MM-DD; leave "" if not given.
        medical_record_number: The MRN, "RB" followed by 8 digits (e.g. RB40218837); leave "" if not given.
    """
    match = _pick(customer_id=customer_id, full_name=full_name, phone_number=phone_number,
                  email=email, date_of_birth=date_of_birth, medical_record_number=medical_record_number)
    if not match:
        return "Error: provide at least one reference number or profile detail to find the patient."
    rows = ctx.fuzzy_find("customers", **match)
    if not rows:
        return f"No patient profile matches {match}."
    if len(rows) > 1:
        return f"Error: {len(rows)} patient profiles match {match}; ask the caller for one more detail to tell them apart."
    return str(rows[0])


@tool(owner="agent", rw="read")
def find_identity_verifications(ctx: ToolContext, verification_id: str = "", customer_id: str = "") -> str:
    """Check whether a patient's identity has already been confirmed in this service relationship.

    Returns the latest identity-confirmation outcome for the patient (confirmed or not) and when it
    was recorded. Search by the patient reference number or by the confirmation reference number.

    Args:
        verification_id: Reference number of the identity-confirmation record; leave "" if unknown.
        customer_id: Patient reference number; leave "" if unknown.
    """
    match = _pick(verification_id=verification_id, customer_id=customer_id)
    rows = ctx.find("identity_verifications", **match)
    return str(rows) if rows else f"No identity confirmation on record for {match}."


@tool(owner="agent", rw="read")
def find_handoff_records(ctx: ToolContext, handoff_id: str = "", customer_id: str = "") -> str:
    """List the transfers of a patient to a human representative, with the reason and time of each.

    Args:
        handoff_id: Reference number of a transfer; leave "" if unknown.
        customer_id: Patient reference number; leave "" if unknown.
    """
    match = _pick(handoff_id=handoff_id, customer_id=customer_id)
    rows = ctx.find("handoff_records", **match)
    return str(rows) if rows else f"No transfers to a representative on record for {match}."


# ---------------------------------------------------------------- hospital accounts

@tool(owner="agent", rw="read")
def find_encounter_accounts(ctx: ToolContext, encounter_id: str = "", customer_id: str = "") -> str:
    """Look up hospital accounts — one per visit, stay or therapy series a patient has had at Riverbend.

    Each account shows its account type (clinic, imaging and lab, recurring therapy, emergency,
    outpatient surgery, observation or inpatient), the campus, the financial class it was billed
    under, the clinical classification of the services, the service dates, the dates the final bill
    dropped and the first patient statement was sent, the billing status and any billing hold with
    its reason and start date, agency placement and closing dates, and the current total charges and
    patient balance. Search by the account (HAR) number or list every account of a patient.

    Args:
        encounter_id: Hospital account number; leave "" to list by patient.
        customer_id: Patient reference number; leave "" if searching by account number.
    """
    match = _pick(encounter_id=encounter_id, customer_id=customer_id)
    rows = ctx.find("encounter_accounts", **match)
    return str(rows) if rows else f"No hospital accounts found for {match}."


@tool(owner="agent", rw="read")
def find_encounter_transactions(ctx: ToolContext, encounter_txn_id: str = "", encounter_id: str = "",
                                customer_id: str = "", source_txn_id: str = "", claim_id: str = "") -> str:
    """Show the activity on hospital accounts: charge lines, charge credits, patient liability postings,
    discounts and adjustments, payments, refunds and the statements sent.

    Charge lines carry the line number, chargemaster and procedure codes, revenue code, service date,
    units and amount. Liability postings show where the amount came from (self-pay final bill or the
    deductible, coinsurance, copay or non-covered amount an insurer reported, with the claim it came
    from). Adjustments, credits and refunds point back to the line, posting or payment they relate to.
    Statements show their type, sequence number, date and delivery channel. Amounts are shown as
    positive figures; whether they add to or reduce the balance follows from the kind of activity.

    Args:
        encounter_txn_id: Reference number of one transaction; leave "" if unknown.
        encounter_id: Hospital account number, to list that account's activity; leave "" if unknown.
        customer_id: Patient reference number, to list activity across all their accounts; leave "" if unknown.
        source_txn_id: Reference number of an original charge, posting or payment, to find what was posted against it; leave "" if unknown.
        claim_id: Insurance claim reference number, to find the liability postings it produced; leave "" if unknown.
    """
    match = _pick(encounter_txn_id=encounter_txn_id, encounter_id=encounter_id, customer_id=customer_id,
                  source_txn_id=source_txn_id, claim_id=claim_id)
    rows = ctx.find("encounter_transactions", **match)
    return str(rows) if rows else f"No account activity found for {match}."


@tool(owner="agent", rw="read")
def find_encounter_billing_inquiries(ctx: ToolContext, inquiry_id: str = "", customer_id: str = "",
                                     encounter_id: str = "", disputed_txn_id: str = "") -> str:
    """List billing inquiries a patient has raised — itemized statement requests, charge disputes and
    insurance updates — with the account and charge line concerned, the processing outcome and when
    each was logged.

    Args:
        inquiry_id: Inquiry reference number; leave "" if unknown.
        customer_id: Patient reference number; leave "" if unknown.
        encounter_id: Hospital account number; leave "" if unknown.
        disputed_txn_id: Reference number of a disputed charge line; leave "" if unknown.
    """
    match = _pick(inquiry_id=inquiry_id, customer_id=customer_id, encounter_id=encounter_id,
                  disputed_txn_id=disputed_txn_id)
    rows = ctx.find("encounter_billing_inquiries", **match)
    return str(rows) if rows else f"No billing inquiries found for {match}."


# ---------------------------------------------------------------- insurance claims

@tool(owner="agent", rw="read")
def find_insurance_claims(ctx: ToolContext, claim_id: str = "", customer_id: str = "", encounter_id: str = "",
                          member_id: str = "") -> str:
    """Look up the insurance claims Riverbend has filed for a patient's care.

    Each claim shows the payer class, the payer and the member and group numbers billed, its place in
    the coordination-of-benefits order, the authorization reference, the first date of service, the
    original and latest submission dates and submission type, any front-end rejection reason, the
    payer's claim number, the adjudication date, the latest denial date with its reason and remark
    codes, the highest appeal level filed, the total billed and the amount still expected from the
    payer. Search by claim number, by hospital account, by patient, or by the member ID on the card.

    Args:
        claim_id: Claim reference number; leave "" if unknown.
        customer_id: Patient reference number; leave "" if unknown.
        encounter_id: Hospital account number the claim billed; leave "" if unknown.
        member_id: Member ID exactly as printed on the insurance card; leave "" if unknown.
    """
    match = _pick(claim_id=claim_id, customer_id=customer_id, encounter_id=encounter_id, member_id=member_id)
    rows = ctx.find("insurance_claims", **match)
    return str(rows) if rows else f"No insurance claims found for {match}."


@tool(owner="agent", rw="read")
def find_claim_transactions(ctx: ToolContext, claim_txn_id: str = "", claim_id: str = "", customer_id: str = "") -> str:
    """Show what has happened on insurance claims: billed amounts per submission, payer payments,
    contractual adjustments, patient-responsibility amounts released to the patient or forwarded to a
    secondary payer, denial write-offs, payer recoveries, corrected-claim filings and appeals.

    Remittance lines carry the payer's trace number, remittance date and the group and reason code
    (for example CO-45, PR-1, PR-2, PR-3, CO-197). Corrections show their sequence and reason; appeals
    show their level and type.

    Args:
        claim_txn_id: Reference number of one claim activity; leave "" if unknown.
        claim_id: Claim reference number, to list its activity; leave "" if unknown.
        customer_id: Patient reference number, to list activity across their claims; leave "" if unknown.
    """
    match = _pick(claim_txn_id=claim_txn_id, claim_id=claim_id, customer_id=customer_id)
    rows = ctx.find("claim_transactions", **match)
    return str(rows) if rows else f"No claim activity found for {match}."


@tool(owner="agent", rw="read")
def find_claim_appeal_authorizations(ctx: ToolContext, authorization_id: str = "", customer_id: str = "",
                                     claim_id: str = "") -> str:
    """List authorized-representative forms a patient has been sent or has signed so that Riverbend
    may appeal a claim on their behalf, with the form type, how and when it was signed, and whether it
    is awaiting signature, signed or revoked.

    Args:
        authorization_id: Reference number of the form; leave "" if unknown.
        customer_id: Patient reference number; leave "" if unknown.
        claim_id: Claim reference number the form covers; leave "" if unknown.
    """
    match = _pick(authorization_id=authorization_id, customer_id=customer_id, claim_id=claim_id)
    rows = ctx.find("claim_appeal_authorizations", **match)
    return str(rows) if rows else f"No representative authorizations found for {match}."


# ---------------------------------------------------------------- payment plans

@tool(owner="agent", rw="read")
def find_payment_plans(ctx: ToolContext, plan_id: str = "", customer_id: str = "") -> str:
    """Look up a patient's payment plans, current and past.

    Each plan shows its plan type, status, the date it was offered and signed, the due day of the
    month, the first and next due dates, the number of installments, the installment and down
    payment amounts, the autopay method, counts of consecutive missed installments, re-ages,
    reinstatements, patient-requested changes and skipped installments, any default and closing
    dates, and the balance still owed under the plan.

    Args:
        plan_id: Payment plan reference number; leave "" to list by patient.
        customer_id: Patient reference number; leave "" if searching by plan number.
    """
    match = _pick(plan_id=plan_id, customer_id=customer_id)
    rows = ctx.find("payment_plans", **match)
    return str(rows) if rows else f"No payment plans found for {match}."


@tool(owner="agent", rw="read")
def find_plan_transactions(ctx: ToolContext, plan_txn_id: str = "", plan_id: str = "", customer_id: str = "",
                           encounter_id: str = "") -> str:
    """Show the activity on payment plans: hospital-account balances enrolled (and when), installments
    paid (with installment number, due date, channel and confirmation number; installment 0 is the
    down payment), and reductions of enrolled balances with their reason.

    Args:
        plan_txn_id: Reference number of one plan activity; leave "" if unknown.
        plan_id: Payment plan reference number; leave "" if unknown.
        customer_id: Patient reference number; leave "" if unknown.
        encounter_id: Hospital account number, to see how that account sits on a plan; leave "" if unknown.
    """
    match = _pick(plan_txn_id=plan_txn_id, plan_id=plan_id, customer_id=customer_id, encounter_id=encounter_id)
    rows = ctx.find("plan_transactions", **match)
    return str(rows) if rows else f"No payment plan activity found for {match}."


# ---------------------------------------------------------------- financial assistance

@tool(owner="agent", rw="read")
def find_assistance_cases(ctx: ToolContext, fap_case_id: str = "", customer_id: str = "") -> str:
    """Look up a patient's financial assistance (charity care) applications and awards.

    Each case shows the assistance tier, status, application date and channel, any presumptive
    basis, the attested household size, documented annual household income and the household's
    percent of the federal poverty guideline, documented medical debt and liquid assets, the
    missing-document deadline, the determination date, the award's first and last covered dates of
    service, the medical-hardship liability cap, any denial reason, the closing date and the total
    charity adjustments booked under the award.

    Args:
        fap_case_id: Financial assistance case reference number; leave "" to list by patient.
        customer_id: Patient reference number; leave "" if searching by case number.
    """
    match = _pick(fap_case_id=fap_case_id, customer_id=customer_id)
    rows = ctx.find("assistance_cases", **match)
    return str(rows) if rows else f"No financial assistance cases found for {match}."


@tool(owner="agent", rw="read")
def find_assistance_transactions(ctx: ToolContext, fap_txn_id: str = "", fap_case_id: str = "",
                                 customer_id: str = "", encounter_id: str = "", source_fap_txn_id: str = "") -> str:
    """Show the activity on financial assistance cases: documents requested, received, accepted or
    rejected; letters sent (with language); the award applied to each covered hospital account (with
    the charge basis, the patient's liability under the award, payments already made and the charity
    adjustment); reversals; and collection-protection actions requested on accounts.

    Args:
        fap_txn_id: Reference number of one case activity; leave "" if unknown.
        fap_case_id: Financial assistance case reference number; leave "" if unknown.
        customer_id: Patient reference number; leave "" if unknown.
        encounter_id: Hospital account number; leave "" if unknown.
        source_fap_txn_id: Reference number of an award application, to find its reversal; leave "" if unknown.
    """
    match = _pick(fap_txn_id=fap_txn_id, fap_case_id=fap_case_id, customer_id=customer_id,
                  encounter_id=encounter_id, source_fap_txn_id=source_fap_txn_id)
    rows = ctx.find("assistance_transactions", **match)
    return str(rows) if rows else f"No financial assistance activity found for {match}."


# ---------------------------------------------------------------- estimates

@tool(owner="agent", rw="read")
def find_price_estimates(ctx: ToolContext, estimate_id: str = "", customer_id: str = "", encounter_id: str = "") -> str:
    """Look up good faith estimates, insured out-of-pocket estimates and self-pay package quotes.

    Each estimate shows its type, status, the coverage answer the patient gave, how and when it was
    requested, the scheduling and service dates, the principal service code, the current version
    with its issue date and total, the hospital account of the rendered service and the date on its
    initial bill, any patient-provider dispute with its initiation date and outcome, the closing date,
    and deposits currently held.

    Args:
        estimate_id: Estimate reference number; leave "" if unknown.
        customer_id: Patient reference number; leave "" if unknown.
        encounter_id: Hospital account number of the rendered service; leave "" if unknown.
    """
    match = _pick(estimate_id=estimate_id, customer_id=customer_id, encounter_id=encounter_id)
    rows = ctx.find("price_estimates", **match)
    return str(rows) if rows else f"No estimates found for {match}."


@tool(owner="agent", rw="read")
def find_estimate_transactions(ctx: ToolContext, estimate_txn_id: str = "", estimate_id: str = "",
                               customer_id: str = "", source_estimate_txn_id: str = "", encounter_id: str = "") -> str:
    """Show the detail behind estimates: each expected-charge line by version, provider or facility and
    service code; deposits collected (initial deposit or pre-service balance); and deposits applied to
    a hospital account, refunded, or kept as a late-cancellation fee, each pointing back to the deposit
    it draws on.

    Args:
        estimate_txn_id: Reference number of one estimate line or deposit activity; leave "" if unknown.
        estimate_id: Estimate reference number; leave "" if unknown.
        customer_id: Patient reference number; leave "" if unknown.
        source_estimate_txn_id: Reference number of a deposit collection, to find what drew on it; leave "" if unknown.
        encounter_id: Hospital account number a deposit was applied to; leave "" if unknown.
    """
    match = _pick(estimate_txn_id=estimate_txn_id, estimate_id=estimate_id, customer_id=customer_id,
                  source_estimate_txn_id=source_estimate_txn_id, encounter_id=encounter_id)
    rows = ctx.find("estimate_transactions", **match)
    return str(rows) if rows else f"No estimate lines or deposit activity found for {match}."


# ---------------------------------------------------------------- medical records

@tool(owner="agent", rw="read")
def find_records_requests(ctx: ToolContext, records_request_id: str = "", customer_id: str = "") -> str:
    """Look up requests for copies of medical records, releases to third parties, amendments and
    accountings of disclosures, with the request type, requester, named recipient, authorization
    signature date, receipt date, scope, delivery format, pages produced, current deadline, fulfilment
    date, any denial ground, closing date and fees still owed.

    Args:
        records_request_id: Records request reference number; leave "" to list by patient.
        customer_id: Patient reference number; leave "" if searching by request number.
    """
    match = _pick(records_request_id=records_request_id, customer_id=customer_id)
    rows = ctx.find("records_requests", **match)
    return str(rows) if rows else f"No records requests found for {match}."


@tool(owner="agent", rw="read")
def find_records_transactions(ctx: ToolContext, records_txn_id: str = "", records_request_id: str = "",
                              customer_id: str = "") -> str:
    """Show extension notices, fees assessed (by component and quantity), fee payments and fee waivers
    on medical records requests.

    Args:
        records_txn_id: Reference number of one activity; leave "" if unknown.
        records_request_id: Records request reference number; leave "" if unknown.
        customer_id: Patient reference number; leave "" if unknown.
    """
    match = _pick(records_txn_id=records_txn_id, records_request_id=records_request_id, customer_id=customer_id)
    rows = ctx.find("records_transactions", **match)
    return str(rows) if rows else f"No records request activity found for {match}."


# ---------------------------------------------------------------- appointments

@tool(owner="agent", rw="read")
def find_appointments(ctx: ToolContext, appointment_id: str = "", customer_id: str = "", encounter_id: str = "") -> str:
    """Look up a patient's appointments: visit type, status, booking channel and date, scheduled date
    and start time, provider or modality, referral and authorization status, pre-registration,
    reschedules used, cancellation details, the hospital account registered at check-in, and any
    missed-appointment fees owed.

    Args:
        appointment_id: Appointment reference number; leave "" if unknown.
        customer_id: Patient reference number; leave "" if unknown.
        encounter_id: Hospital account number registered at check-in; leave "" if unknown.
    """
    match = _pick(appointment_id=appointment_id, customer_id=customer_id, encounter_id=encounter_id)
    rows = ctx.find("appointments", **match)
    return str(rows) if rows else f"No appointments found for {match}."


@tool(owner="agent", rw="read")
def find_appointment_transactions(ctx: ToolContext, appointment_txn_id: str = "", appointment_id: str = "",
                                  customer_id: str = "") -> str:
    """Show reminders and preparation outreach sent for appointments, and missed-appointment fees
    assessed, waived (with reason) or paid.

    Args:
        appointment_txn_id: Reference number of one activity; leave "" if unknown.
        appointment_id: Appointment reference number; leave "" if unknown.
        customer_id: Patient reference number; leave "" if unknown.
    """
    match = _pick(appointment_txn_id=appointment_txn_id, appointment_id=appointment_id, customer_id=customer_id)
    rows = ctx.find("appointment_transactions", **match)
    return str(rows) if rows else f"No appointment activity found for {match}."


# ---------------------------------------------------------------- identity & handoff

@tool(owner="agent", rw="write")
def verify_patient_identity(ctx: ToolContext, customer_id: str, date_of_birth: str = "", phone_number: str = "",
                            email: str = "", medical_record_number: str = "", ssn_last4: str = "",
                            mailing_zip: str = "") -> str:
    """Confirm that the caller is the patient (or guarantor) whose profile was found, and record the
    outcome. Identity must be confirmed before any account detail is discussed or any change is made.

    This tool performs the comparison itself: each detail the caller gives is checked against the
    patient's profile, and identity is confirmed when at least 2 of them match. A name alone is never
    proof of identity and is not asked for here. Pass only the details the caller actually stated,
    exactly as stated, and leave the rest empty. If a first attempt falls short, ask for another
    detail and try again; once confirmed, the confirmation stands.

    Args:
        customer_id: Patient reference number taken from the profile lookup. Required; it only locates the profile and never counts as a matching detail.
        date_of_birth: Date of birth the caller gives, as YYYY-MM-DD; leave "" if not given.
        phone_number: Phone number the caller gives, 10 digits with no punctuation; leave "" if not given.
        email: Email address the caller gives; leave "" if not given.
        medical_record_number: MRN the caller reads from a statement or wristband, "RB" plus 8 digits; leave "" if not given.
        ssn_last4: Last four digits of the Social Security number the caller gives; leave "" if not given.
        mailing_zip: 5-digit ZIP code of the caller's mailing address; leave "" if not given.
    """
    if not customer_id:
        return "Error: customer_id is required; find the patient profile first and pass its reference number."
    rows = ctx.find("customers", customer_id=customer_id)
    if not rows:
        return f"Error: no patient profile {customer_id}; identity cannot be confirmed."
    rec = rows[0]
    supplied = {"date_of_birth": date_of_birth, "phone_number": phone_number, "email": email,
                "medical_record_number": medical_record_number, "ssn_last4": ssn_last4, "mailing_zip": mailing_zip}
    matched = sum(1 for field, value in supplied.items()
                  if value and str(rec.get(field) or "").strip().lower() == str(value).strip().lower())
    verified = matched >= 2
    rid = ctx.make_id("idv_", customer_id)
    prior = ctx.find("identity_verifications", verification_id=rid)
    verified = verified or bool(prior and prior[0].get("verified"))
    if prior:
        ctx.update("identity_verifications", rid, verified=verified, verified_at=ctx.now())
    else:
        ctx.create("identity_verifications", rid, verification_id=rid, customer_id=customer_id,
                   verified=verified, verified_at=ctx.now())
    if verified:
        return f"Identity confirmed for patient {customer_id}."
    return (f"Identity NOT confirmed for patient {customer_id}: only {matched} of the 2 required details matched. "
            "Ask the caller for another detail on file and try again.")


@tool(owner="agent", rw="write")
def transfer_to_human_agent(ctx: ToolContext, customer_id: str, reason: str) -> str:
    """Transfer the patient to a Riverbend Patient Financial Services representative and record why.

    Use POLICY_NOT_COVERED when no Riverbend policy lets you resolve what the patient is asking for.
    Use CUSTOMER_REQUESTED when the patient has explicitly asked for a person at least 2 times in this
    conversation.

    Args:
        customer_id: Patient reference number taken from the profile lookup; the profile must exist.
        reason: Exactly one of POLICY_NOT_COVERED or CUSTOMER_REQUESTED; no other wording is accepted.
    """
    allowed = {"POLICY_NOT_COVERED", "CUSTOMER_REQUESTED"}
    if reason not in allowed:
        return f"Error: unknown transfer reason '{reason}'. Valid: {', '.join(sorted(allowed))}."
    if not ctx.find("customers", customer_id=customer_id):
        return f"Error: no patient profile {customer_id}; the transfer cannot be recorded."
    rid = ctx.make_id("hof_", customer_id, reason)
    ctx.create("handoff_records", rid, handoff_id=rid, customer_id=customer_id,
               reason=reason, created_at=ctx.now())
    return f"Transfer to a representative recorded for patient {customer_id} ({reason})."

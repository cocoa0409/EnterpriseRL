"""Shared tools for env_0021_retail_pharmacy_chain (Kestrel Pharmacy Patient Care Desk).

Every tool here is a share tool: always present in its owner's tool list. This module holds the
complete record-lookup layer (one finder per record type, the patient finder doubling as the
identity entry), the identity-verification write and the transfer-to-human handoff.

Scenario-level operational constants built into these tools:
  K = 2  identity credentials that must match the patient profile to pass verification.
  R = 2  explicit requests for a human after which the patient is handed off as CUSTOMER_REQUESTED.
"""

from erlbench import ToolContext, tool


def _given(criteria: dict) -> dict:
    # Keep only the criteria the caller actually supplied (exact match on ids).
    return {k: v for k, v in criteria.items() if v}


def _report(rows: list, label: str, match: dict) -> str:
    return str(rows) if rows else f"No {label} found for {match}."


# ---------------------------------------------------------------- identity entry
@tool(owner="agent", rw="read")
def find_customers(ctx: ToolContext, customer_id: str = "", phone_number: str = "", email: str = "",
                   name: str = "", date_of_birth: str = "", preferred_store_id: str = "") -> str:
    """Look up a Kestrel patient profile to establish whose records this conversation is about.

    Search with the patient reference number if you already have it, or with what the caller
    naturally tells you: the phone number on the profile, the email address, the patient's full
    name or their date of birth. Every criterion is optional; supply whichever you know, and add
    another one when several patients match. A hit returns the whole profile: name, date of birth,
    phone, email, home address with ZIP code and state, preferred store reference and the date the
    profile was opened. Finding a profile does not confirm the caller is that patient; identity
    must still be verified before any account business.

    Args:
        customer_id: Patient reference number, if already known; leave "" otherwise.
        phone_number: Phone number the caller gives, 10 digits (spacing and punctuation are ignored); leave "" if not given.
        email: Email address the caller gives; leave "" if not given.
        name: Patient's full name as the caller says it; leave "" if not given.
        date_of_birth: Patient's date of birth as YYYY-MM-DD; leave "" if not given.
        preferred_store_id: Store reference number of the patient's home pharmacy, to list the patients who chose that store; leave "" if unknown.
    """
    match = {k: v for k, v in {"customer_id": customer_id, "phone_number": phone_number, "email": email,
                               "name": name, "date_of_birth": date_of_birth,
                               "preferred_store_id": preferred_store_id}.items() if v}
    if not match:
        return "Error: provide at least one detail to find the patient profile."
    rows = ctx.fuzzy_find("customers", **match)
    if not rows:
        return f"No patient profile matches {match}."
    if len(rows) > 1:
        return f"Error: {len(rows)} patient profiles match {match}; ask the caller for one more detail."
    return str(rows[0])


@tool(owner="agent", rw="write")
def verify_patient_identity(ctx: ToolContext, customer_id: str, date_of_birth: str = "", phone_number: str = "",
                            email: str = "", home_zip: str = "") -> str:
    """Verify that the caller is the patient on the profile, and record the result.

    No prescription, insurance, savings, vaccination, delivery or rewards business may be looked
    into or carried out for a patient until this verification has passed. This tool does the
    comparison itself: it checks each detail the caller states against the patient profile and
    passes only when at least 2 of them match exactly. The patient reference number only tells
    the tool which profile to compare against and never counts as a match, and the patient's name
    is not a verification detail. Pass only what the caller actually said, exactly as said, and
    leave the rest blank. The outcome is recorded; if a first attempt falls short and a later
    attempt with more details passes, the patient stays verified.

    Args:
        customer_id: Patient reference number from the patient profile lookup; required.
        date_of_birth: Date of birth the caller states, as YYYY-MM-DD; leave "" if not stated.
        phone_number: Phone number the caller states, 10 digits without separators; leave "" if not stated.
        email: Email address the caller states; leave "" if not stated.
        home_zip: 5-digit ZIP code of the home address the caller states; leave "" if not stated.
    """
    if not customer_id:
        return "Error: customer_id is required; look the patient up first and pass their reference number."
    rows = ctx.find("customers", customer_id=customer_id)
    if not rows:
        return f"Error: no patient profile {customer_id}; cannot verify."
    rec = rows[0]
    # The locator customer_id is deliberately not a credential.
    supplied = {"date_of_birth": date_of_birth, "phone_number": phone_number, "email": email,
                "home_zip": home_zip}
    matched = sum(1 for field, value in supplied.items()
                  if value and str(rec.get(field)).strip().lower() == str(value).strip().lower())
    verified = matched >= 2
    rid = ctx.make_id("ver_", customer_id)
    # Upsert, monotonic: a later pass is never overwritten by an earlier failure.
    prior = ctx.find("identity_verifications", verification_id=rid)
    verified = verified or bool(prior and prior[0].get("verified"))
    if prior:
        ctx.update("identity_verifications", rid, verified=verified, verified_at=ctx.now())
    else:
        ctx.create("identity_verifications", rid, verification_id=rid, customer_id=customer_id,
                   verified=verified, verified_at=ctx.now())
    return (f"Identity verified for patient {customer_id}." if verified
            else f"Identity NOT verified for patient {customer_id}: fewer than 2 of the stated details match "
                 "the profile. Ask the caller for another detail on file and try again.")


@tool(owner="agent", rw="write")
def transfer_to_human_agent(ctx: ToolContext, customer_id: str, reason: str) -> str:
    """Hand the patient over to a Kestrel Patient Care representative and record why.

    Use it in exactly two situations. POLICY_NOT_COVERED: the patient's request is one that no
    Kestrel policy lets you resolve. CUSTOMER_REQUESTED: the patient has explicitly asked to speak
    with a person 2 times in this conversation. The handoff is recorded against the patient
    profile with the moment it happened.

    Args:
        customer_id: Patient reference number from the patient profile lookup.
        reason: Exactly POLICY_NOT_COVERED or CUSTOMER_REQUESTED; no other wording is accepted.
    """
    allowed = {"POLICY_NOT_COVERED", "CUSTOMER_REQUESTED"}
    if reason not in allowed:
        return f"Error: unknown handoff reason '{reason}'. Valid: {', '.join(sorted(allowed))}."
    if not ctx.find("customers", customer_id=customer_id):
        return f"Error: no patient profile {customer_id}; cannot record the handoff."
    rid = ctx.make_id("hof_", customer_id, reason)
    ctx.create("human_handoffs", rid, handoff_id=rid, customer_id=customer_id, reason=reason,
               created_at=ctx.now())
    return f"Handoff to a Patient Care representative recorded for patient {customer_id} ({reason})."


# ---------------------------------------------------------------- reference records
@tool(owner="agent", rw="read")
def find_stores(ctx: ToolContext, store_id: str = "") -> str:
    """Look up Kestrel store details: store number and name, city and state, whether the pharmacy
    counter is open 24 hours, and whether the store has a drive-thru, a prescription pickup locker
    and in-store vaccination. Leave the reference blank to list every store.

    Args:
        store_id: Store reference number, as shown on a patient profile, prescription or fill; leave "" to list all stores.
    """
    match = _given({"store_id": store_id})
    return _report(ctx.find("stores", **match), "store", match)


@tool(owner="agent", rw="read")
def find_prescribers(ctx: ToolContext, prescriber_id: str = "") -> str:
    """Look up a prescriber's details: name and credential, NPI, office phone and whether the
    prescriber can receive and send electronic prescriptions for controlled substances.

    Args:
        prescriber_id: Prescriber reference number, as shown on a prescription or renewal request; leave "" to list all.
    """
    match = _given({"prescriber_id": prescriber_id})
    return _report(ctx.find("prescribers", **match), "prescriber", match)


@tool(owner="agent", rw="read")
def find_identity_verifications(ctx: ToolContext, verification_id: str = "", customer_id: str = "") -> str:
    """Check whether a patient's identity has already been verified in this conversation and when.

    Args:
        verification_id: Reference number of the verification result; leave "" if unknown.
        customer_id: Patient reference number; leave "" if unknown.
    """
    match = _given({"verification_id": verification_id, "customer_id": customer_id})
    return _report(ctx.find("identity_verifications", **match), "verification result", match)


@tool(owner="agent", rw="read")
def find_human_handoffs(ctx: ToolContext, handoff_id: str = "", customer_id: str = "") -> str:
    """See whether a patient has already been handed to a Patient Care representative, with the
    recorded reason and time.

    Args:
        handoff_id: Reference number of the handoff; leave "" if unknown.
        customer_id: Patient reference number; leave "" if unknown.
    """
    match = _given({"handoff_id": handoff_id, "customer_id": customer_id})
    return _report(ctx.find("human_handoffs", **match), "handoff", match)


# ---------------------------------------------------------------- prescriptions
@tool(owner="agent", rw="read")
def find_rx_prescriptions(ctx: ToolContext, prescription_id: str = "", customer_id: str = "",
                          prescriber_id: str = "", store_id: str = "") -> str:
    """Look up prescriptions on file: Kestrel prescription number, drug and strength, handling
    class, status, quantity and days supply per fill, refills written and remaining, any quantity
    still owed from a partial fill, written and expiration dates, how the prescription arrived,
    prior transfers, the holding store and the prescriber. Supply any reference numbers you have.

    Args:
        prescription_id: Prescription reference number; leave "" if unknown.
        customer_id: Patient reference number, to list all of a patient's prescriptions; leave "" if unknown.
        prescriber_id: Prescriber reference number; leave "" if unknown.
        store_id: Store reference number of the holding store; leave "" if unknown.
    """
    match = _given({"prescription_id": prescription_id, "customer_id": customer_id, "prescriber_id": prescriber_id, "store_id": store_id})
    return _report(ctx.find("rx_prescriptions", **match), "prescription", match)


@tool(owner="agent", rw="read")
def find_rx_fills(ctx: ToolContext, fill_id: str = "", prescription_id: str = "", customer_id: str = "",
                  source_fill_id: str = "", error_report_id: str = "", store_id: str = "") -> str:
    """Look up the dispensing history of prescriptions: original fills, refills with their reason,
    partial fills and the balances owed, balance completions and cancellations, returns to stock,
    pickups (channel, who collected, whether ID was checked), emergency supplies, and
    dispensing-error returns and remakes. Each entry shows its dates, quantity and days supply,
    what the patient paid and how, and the entry it refers back to where there is one.

    Args:
        fill_id: Reference number of one dispensing entry; leave "" if unknown.
        prescription_id: Prescription reference number, to list its whole history; leave "" if unknown.
        customer_id: Patient reference number; leave "" if unknown.
        source_fill_id: Reference number of an earlier entry, to find what was done to it later (its pickup, return, owed balance or correction); leave "" if unknown.
        error_report_id: Reference number of a dispensing-error report; leave "" if unknown.
        store_id: Reference number of the dispensing store; leave "" if unknown.
    """
    match = _given({"fill_id": fill_id, "prescription_id": prescription_id, "customer_id": customer_id, "source_fill_id": source_fill_id, "error_report_id": error_report_id, "store_id": store_id})
    return _report(ctx.find("rx_fills", **match), "dispensing entry", match)


@tool(owner="agent", rw="read")
def find_rx_prescriber_requests(ctx: ToolContext, request_id: str = "", prescription_id: str = "",
                                customer_id: str = "", prescriber_id: str = "",
                                source_request_id: str = "") -> str:
    """Look up renewal requests Kestrel sent to prescribers and the prescribers' declines: date,
    reason for the request, channel used, and the decline reason where one was received.

    Args:
        request_id: Reference number of a request or reply; leave "" if unknown.
        prescription_id: Prescription reference number; leave "" if unknown.
        customer_id: Patient reference number; leave "" if unknown.
        prescriber_id: Prescriber reference number; leave "" if unknown.
        source_request_id: Reference number of a request, to find the reply to it; leave "" if unknown.
    """
    match = _given({"request_id": request_id, "prescription_id": prescription_id, "customer_id": customer_id, "prescriber_id": prescriber_id, "source_request_id": source_request_id})
    return _report(ctx.find("rx_prescriber_requests", **match), "prescriber request", match)


@tool(owner="agent", rw="read")
def find_rx_error_reports(ctx: ToolContext, error_report_id: str = "", customer_id: str = "",
                          prescription_id: str = "", fill_id: str = "") -> str:
    """Look up dispensing-error reports: which fill was reported, the kind of error, when and how it
    was reported, and the pharmacist's review outcome with its date.

    Args:
        error_report_id: Reference number of the report; leave "" if unknown.
        customer_id: Patient reference number; leave "" if unknown.
        prescription_id: Prescription reference number; leave "" if unknown.
        fill_id: Reference number of the dispensing entry reported; leave "" if unknown.
    """
    match = _given({"error_report_id": error_report_id, "customer_id": customer_id, "prescription_id": prescription_id, "fill_id": fill_id})
    return _report(ctx.find("rx_error_reports", **match), "dispensing-error report", match)


# ---------------------------------------------------------------- prescription insurance
@tool(owner="agent", rw="read")
def find_coverage_plans(ctx: ToolContext, coverage_id: str = "", customer_id: str = "") -> str:
    """Look up the prescription insurance plans on a patient's profile: plan class and payer name,
    card details (BIN, PCN, group, member ID, person code), the patient's relationship to the
    cardholder, whether the plan is billed first or second, effective and termination dates, any
    workers' compensation claim number, and whether the plan is pending verification, active,
    terminated or removed.

    Args:
        coverage_id: Reference number of one insurance plan on file; leave "" if unknown.
        customer_id: Patient reference number, to list all of the patient's plans; leave "" if unknown.
    """
    match = _given({"coverage_id": coverage_id, "customer_id": customer_id})
    return _report(ctx.find("coverage_plans", **match), "insurance plan", match)


@tool(owner="agent", rw="read")
def find_coverage_claims(ctx: ToolContext, claim_id: str = "", coverage_id: str = "", customer_id: str = "",
                         prescription_id: str = "", pa_id: str = "", source_claim_id: str = "") -> str:
    """Look up insurance claim history: paid claims with the plan's payment, the patient's share
    and any deductible portion; rejected claims with the reject reason; claim reversals and their
    reason; and Medicare Prescription Payment Plan notices. Each entry shows the date of service,
    the prescription and fill billed, the billing basis, any override code and the days supply.

    Args:
        claim_id: Reference number of one claim entry; leave "" if unknown.
        coverage_id: Reference number of the insurance plan billed; leave "" if unknown.
        customer_id: Patient reference number; leave "" if unknown.
        prescription_id: Prescription reference number, to see every claim for it; leave "" if unknown.
        pa_id: Reference number of a prior authorization, to find the claims paid under it; leave "" if unknown.
        source_claim_id: Reference number of a paid claim, to find its reversal or notice; leave "" if unknown.
    """
    match = _given({"claim_id": claim_id, "coverage_id": coverage_id, "customer_id": customer_id,
                    "prescription_id": prescription_id, "pa_id": pa_id, "source_claim_id": source_claim_id})
    return _report(ctx.find("coverage_claims", **match), "claim entry", match)


@tool(owner="agent", rw="read")
def find_coverage_prior_auths(ctx: ToolContext, pa_id: str = "", coverage_id: str = "", customer_id: str = "",
                              prescription_id: str = "", source_pa_id: str = "") -> str:
    """Look up prior authorization history: requests started with the plan (standard or expedited,
    the channel and the decision due date), approvals with the last date they cover, denials with
    the plan's reason, appeals the patient filed and the plan's appeal decisions.

    Args:
        pa_id: Reference number of one prior authorization entry; leave "" if unknown.
        coverage_id: Reference number of the insurance plan; leave "" if unknown.
        customer_id: Patient reference number; leave "" if unknown.
        prescription_id: Prescription reference number; leave "" if unknown.
        source_pa_id: Reference number of an earlier entry, to find the decision, appeal or appeal decision that answers it; leave "" if unknown.
    """
    match = _given({"pa_id": pa_id, "coverage_id": coverage_id, "customer_id": customer_id,
                    "prescription_id": prescription_id, "source_pa_id": source_pa_id})
    return _report(ctx.find("coverage_prior_auths", **match), "prior authorization entry", match)


# ---------------------------------------------------------------- savings & copay assistance
@tool(owner="agent", rw="read")
def find_copay_enrollments(ctx: ToolContext, enrollment_id: str = "", customer_id: str = "",
                           linked_coverage_id: str = "", prescription_id: str = "") -> str:
    """Look up the savings and copay assistance programs on a patient's profile: program type and
    printed name, the drug it is for, card details, who enrolled the patient, the insurance plan
    and prescription it is tied to, household members covered, income attestation, the current
    benefit period with the program dollars left, membership fees paid, and its status with
    suspension, expiration and closing dates.

    Args:
        enrollment_id: Reference number of one program enrollment; leave "" if unknown.
        customer_id: Patient reference number, to list all of the patient's programs; leave "" if unknown.
        linked_coverage_id: Reference number of an insurance plan, to find the programs that pay after it; leave "" if unknown.
        prescription_id: Prescription reference number, to find the programs tied to it; leave "" if unknown.
    """
    match = _given({"enrollment_id": enrollment_id, "customer_id": customer_id,
                    "linked_coverage_id": linked_coverage_id, "prescription_id": prescription_id})
    return _report(ctx.find("copay_enrollments", **match), "program enrollment", match)


@tool(owner="agent", rw="read")
def find_copay_activity(ctx: ToolContext, activity_id: str = "", enrollment_id: str = "", customer_id: str = "",
                        prescription_id: str = "", fill_id: str = "", claim_id: str = "",
                        source_activity_id: str = "") -> str:
    """Look up what a savings or assistance program has done: benefit periods opened and closed
    with their dollars, benefits paid on fills (patient pay before and after), benefit reversals,
    discount prices given on cash fills, free bridge fills, and membership fees charged or
    refunded.

    Args:
        activity_id: Reference number of one program entry; leave "" if unknown.
        enrollment_id: Reference number of the program enrollment; leave "" if unknown.
        customer_id: Patient reference number; leave "" if unknown.
        prescription_id: Prescription reference number; leave "" if unknown.
        fill_id: Reference number of a dispensing entry, to see what a program did for that fill; leave "" if unknown.
        claim_id: Reference number of an insurance claim; leave "" if unknown.
        source_activity_id: Reference number of an earlier program entry, to find its reversal or refund; leave "" if unknown.
    """
    match = _given({"activity_id": activity_id, "enrollment_id": enrollment_id, "customer_id": customer_id,
                    "prescription_id": prescription_id, "fill_id": fill_id, "claim_id": claim_id,
                    "source_activity_id": source_activity_id})
    return _report(ctx.find("copay_activity", **match), "program entry", match)


# ---------------------------------------------------------------- immunizations
@tool(owner="agent", rw="read")
def find_vax_courses(ctx: ToolContext, course_id: str = "", customer_id: str = "", coverage_id: str = "",
                     store_id: str = "") -> str:
    """Look up a patient's vaccination courses: which vaccination and season, how many valid doses
    the course needs and how many are still to go, whether the patient attested being
    immunocompromised or a qualifying risk condition, how the doses are paid and by which
    insurance plan, the store, and whether the course is scheduled, in progress, completed or
    cancelled.

    Args:
        course_id: Reference number of one vaccination course; leave "" if unknown.
        customer_id: Patient reference number, to list all of the patient's courses; leave "" if unknown.
        coverage_id: Reference number of the insurance plan billed; leave "" if unknown.
        store_id: Store reference number; leave "" if unknown.
    """
    match = _given({"course_id": course_id, "customer_id": customer_id, "coverage_id": coverage_id,
                    "store_id": store_id})
    return _report(ctx.find("vax_courses", **match), "vaccination course", match)


@tool(owner="agent", rw="read")
def find_vax_events(ctx: ToolContext, vax_event_id: str = "", course_id: str = "", customer_id: str = "",
                    store_id: str = "", coverage_id: str = "", source_event_id: str = "") -> str:
    """Look up the history of vaccination courses: appointments booked (date, time, store, dose and
    how they were booked), cancellations with their reason, missed appointments, signed consent
    forms, doses given (lot number, whether it completed the course, how it was paid, what the
    patient paid, observation time), doses found not to count, and registry reports.

    Args:
        vax_event_id: Reference number of one vaccination entry; leave "" if unknown.
        course_id: Reference number of the vaccination course; leave "" if unknown.
        customer_id: Patient reference number; leave "" if unknown.
        store_id: Store reference number; leave "" if unknown.
        coverage_id: Reference number of the insurance plan billed for a dose; leave "" if unknown.
        source_event_id: Reference number of an earlier entry, to find what happened to it (an appointment's cancellation or dose, a dose's invalidation or report); leave "" if unknown.
    """
    match = _given({"vax_event_id": vax_event_id, "course_id": course_id, "customer_id": customer_id,
                    "store_id": store_id, "coverage_id": coverage_id, "source_event_id": source_event_id})
    return _report(ctx.find("vax_events", **match), "vaccination entry", match)


# ---------------------------------------------------------------- delivery & pickup
@tool(owner="agent", rw="read")
def find_delivery_plans(ctx: ToolContext, delivery_plan_id: str = "", customer_id: str = "", store_id: str = "") -> str:
    """Look up a patient's delivery plan: which plan, the delivery address and ZIP code, the store
    that fulfils courier orders, the trial end date, the current billing cycle, fees paid net of
    refunds, and whether the plan is enrolled, active, past due (and since when) or cancelled.

    Args:
        delivery_plan_id: Reference number of the delivery plan; leave "" if unknown.
        customer_id: Patient reference number; leave "" if unknown.
        store_id: Reference number of the fulfilling store; leave "" if unknown.
    """
    match = _given({"delivery_plan_id": delivery_plan_id, "customer_id": customer_id, "store_id": store_id})
    return _report(ctx.find("delivery_plans", **match), "delivery plan", match)


@tool(owner="agent", rw="read")
def find_delivery_orders(ctx: ToolContext, order_id: str = "", delivery_plan_id: str = "", customer_id: str = "",
                         source_order_id: str = "", store_id: str = "") -> str:
    """Look up delivery orders and what happened to them: orders placed (speed, scheduled date and
    promised window, order value, what they carry, distance, carrier), failed attempts with the
    reason, completed deliveries with the time and how they were handed over, cancellations, and
    orders returned to the store.

    Args:
        order_id: Reference number of one order entry; leave "" if unknown.
        delivery_plan_id: Reference number of the delivery plan; leave "" if unknown.
        customer_id: Patient reference number; leave "" if unknown.
        source_order_id: Reference number of an order, to find its attempts, delivery, cancellation, return or redelivery; leave "" if unknown.
        store_id: Store reference number; leave "" if unknown.
    """
    match = _given({"order_id": order_id, "delivery_plan_id": delivery_plan_id, "customer_id": customer_id,
                    "source_order_id": source_order_id, "store_id": store_id})
    return _report(ctx.find("delivery_orders", **match), "delivery order entry", match)


@tool(owner="agent", rw="read")
def find_delivery_charges(ctx: ToolContext, charge_id: str = "", delivery_plan_id: str = "", customer_id: str = "",
                          source_order_id: str = "", source_charge_id: str = "") -> str:
    """Look up delivery fees and refunds: subscription fees per billing cycle, fees charged on
    individual orders, and refunds with their reason and amount.

    Args:
        charge_id: Reference number of one fee or refund; leave "" if unknown.
        delivery_plan_id: Reference number of the delivery plan; leave "" if unknown.
        customer_id: Patient reference number; leave "" if unknown.
        source_order_id: Reference number of an order, to see its fees and refunds; leave "" if unknown.
        source_charge_id: Reference number of a fee, to find its refund; leave "" if unknown.
    """
    match = _given({"charge_id": charge_id, "delivery_plan_id": delivery_plan_id, "customer_id": customer_id,
                    "source_order_id": source_order_id, "source_charge_id": source_charge_id})
    return _report(ctx.find("delivery_charges", **match), "delivery fee entry", match)


# ---------------------------------------------------------------- auto refill & medication sync
@tool(owner="agent", rw="read")
def find_refill_enrollments(ctx: ToolContext, refill_enrollment_id: str = "", customer_id: str = "",
                            prescription_id: str = "") -> str:
    """Look up automated refill enrollments: which Auto Refill or Med Sync program a prescription is
    in, the sync day and next cycle date, pickup or home delivery, skips left this program year,
    any pause end date, and whether the enrollment is enrolled, active, paused, stopped or ended
    (with the reason).

    Args:
        refill_enrollment_id: Reference number of one enrollment; leave "" if unknown.
        customer_id: Patient reference number; leave "" if unknown.
        prescription_id: Prescription reference number; leave "" if unknown.
    """
    match = _given({"refill_enrollment_id": refill_enrollment_id, "customer_id": customer_id,
                    "prescription_id": prescription_id})
    return _report(ctx.find("refill_enrollments", **match), "refill enrollment", match)


@tool(owner="agent", rw="read")
def find_refill_cycles(ctx: ToolContext, cycle_id: str = "", refill_enrollment_id: str = "", customer_id: str = "",
                       prescription_id: str = "", source_cycle_id: str = "", fill_id: str = "") -> str:
    """Look up automated refill cycles: yearly skip allowances, cycles scheduled (date, days supply,
    short fill to the sync day), confirmations by the patient or a caregiver, cycles filled, skipped
    or held with the hold reason.

    Args:
        cycle_id: Reference number of one cycle entry; leave "" if unknown.
        refill_enrollment_id: Reference number of the enrollment; leave "" if unknown.
        customer_id: Patient reference number; leave "" if unknown.
        prescription_id: Prescription reference number; leave "" if unknown.
        source_cycle_id: Reference number of a scheduled cycle, to see whether it was confirmed, filled, skipped or held; leave "" if unknown.
        fill_id: Reference number of a dispensing entry produced by a cycle; leave "" if unknown.
    """
    match = _given({"cycle_id": cycle_id, "refill_enrollment_id": refill_enrollment_id, "customer_id": customer_id,
                    "prescription_id": prescription_id, "source_cycle_id": source_cycle_id, "fill_id": fill_id})
    return _report(ctx.find("refill_cycles", **match), "refill cycle entry", match)


# ---------------------------------------------------------------- rewards
@tool(owner="agent", rw="read")
def find_rewards_memberships(ctx: ToolContext, membership_id: str = "", customer_id: str = "") -> str:
    """Look up a patient's Kestrel Care Rewards membership: level, card number, points balance,
    Kestrel Cash available, Plus fees paid, the tier year and current Plus billing cycle, and
    whether the membership is enrolled, active, suspended or closed.

    Args:
        membership_id: Reference number of the membership; leave "" if unknown.
        customer_id: Patient reference number; leave "" if unknown.
    """
    match = _given({"membership_id": membership_id, "customer_id": customer_id})
    return _report(ctx.find("rewards_memberships", **match), "rewards membership", match)


@tool(owner="agent", rw="read")
def find_rewards_activity(ctx: ToolContext, activity_id: str = "", membership_id: str = "", customer_id: str = "",
                          source_ref_id: str = "", source_activity_id: str = "", store_id: str = "") -> str:
    """Look up rewards history: points earned (what earned them, the purchase, fill or dose, the
    multiplier), goodwill credits with their reason, reversals and expiries, conversions to Kestrel
    Cash, Kestrel Cash issued (with its expiration), redeemed or expired, and Plus fees charged or
    refunded.

    Args:
        activity_id: Reference number of one rewards entry; leave "" if unknown.
        membership_id: Reference number of the membership; leave "" if unknown.
        customer_id: Patient reference number; leave "" if unknown.
        source_ref_id: Reference number of a purchase, fill, dose or other Kestrel record, to see the rewards it produced; leave "" if unknown.
        source_activity_id: Reference number of an earlier rewards entry, to find what later acted on it; leave "" if unknown.
        store_id: Store reference number; leave "" if unknown.
    """
    match = _given({"activity_id": activity_id, "membership_id": membership_id, "customer_id": customer_id,
                    "source_ref_id": source_ref_id, "source_activity_id": source_activity_id, "store_id": store_id})
    return _report(ctx.find("rewards_activity", **match), "rewards entry", match)

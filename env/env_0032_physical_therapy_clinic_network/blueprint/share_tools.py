"""Shared tools for env_0032_physical_therapy_clinic_network (Piedmont Motion Physical Therapy).
Output of the erl-scenario-blueprint skill.

Every tool here is a SHARE tool: always present in its owner's tool list.
  - one record finder per table (the customers finder doubles as the identity entry);
  - the identity-verification write (K = 2 matching credentials);
  - the transfer-to-human write (exactly two reasons; repeat-request threshold R = 2).
Customer-originated writes (signing, consenting, cancelling their own products) are hidden task
tools authored per difficulty, never here.
"""

from erlbench import ToolContext, tool


def _criteria(**kwargs):
    # Keep only the criteria the caller actually supplied.
    return {k: v for k, v in kwargs.items() if v}


@tool(owner="agent", rw="read")
def find_customers(ctx: ToolContext, customer_id: str = "", name: str = "", phone_number: str = "",
                   email: str = "", account_number: str = "") -> str:
    """Look up a patient profile at Piedmont Motion Physical Therapy to establish whose account this call is about.

    You can search by the patient reference number, or by what a caller can naturally tell you: their
    full name, the phone number on file, the email address on file, or the patient account number printed
    on their statements. Supply whichever details you have; every criterion is optional, but at least one
    is needed. Spacing, punctuation and capitalisation in what the caller says do not prevent a match.
    The profile returned shows the patient reference number, name, date of birth, phone number, email,
    ZIP code, account number, the date the profile was opened and the patient's home clinic. If several
    patients match, you will be asked for one more detail. Finding a profile does not verify the caller's
    identity.

    Args:
        customer_id: The patient reference number, if already known; leave "" if unknown.
        name: The patient's full name as the caller states it; leave "" if not given.
        phone_number: The phone number the caller says is on file, 10 digits; leave "" if not given.
        email: The email address the caller says is on file; leave "" if not given.
        account_number: The patient account number from a statement, in the form PM- followed by 7 digits; leave "" if not given.
    """
    match = _criteria(customer_id=customer_id, name=name, phone_number=phone_number, email=email,
                      account_number=account_number)
    if not match:
        return "Error: provide at least one detail (reference number, name, phone, email or account number) to find the patient."
    rows = ctx.fuzzy_find("customers", **match)
    if not rows:
        return f"No patient profile matches {match}."
    if len(rows) > 1:
        return f"Error: {len(rows)} patient profiles match {match}; ask the caller for one more detail."
    return str(rows[0])


@tool(owner="agent", rw="read")
def find_care_plans(ctx: ToolContext, care_plan_id: str = "", customer_id: str = "") -> str:
    """Look up insured plans of care — the insurance-funded therapy episodes a patient holds.

    Each plan shows the payer program it is billed under, its status, the clinic, payer and member
    number, referral and diagnosis, the verified copay, coinsurance, deductible and visit-limit figures,
    certification dates, the authorization currently in force with its remaining visits, the patient's
    open balance on the plan, and any hold or discharge details. Search by the plan reference number or by
    the patient reference number; both are optional.

    Args:
        care_plan_id: The plan of care reference number; leave "" if unknown.
        customer_id: The patient reference number, to list all of that patient's plans of care; leave "" if unknown.
    """
    match = _criteria(care_plan_id=care_plan_id, customer_id=customer_id)
    rows = ctx.find("care_plans", **match)
    return str(rows) if rows else f"No plans of care found for {match}."


@tool(owner="agent", rw="read")
def find_care_plan_events(ctx: ToolContext, care_plan_event_id: str = "", care_plan_id: str = "",
                          customer_id: str = "", source_event_id: str = "") -> str:
    """Look up the history recorded on insured plans of care.

    The history covers authorization requests, approvals and denials, billed visits (date of service,
    visit kind, units, billed and allowed amounts, KX modifier, authorization used), patient charges
    (copays, deductible and coinsurance, non-covered visits), payments, adjustments, refunds, signed
    financial-responsibility waivers and statements. Search by the entry's own reference number, by the
    plan of care, by the patient, or by the reference of the earlier entry an entry points back to (for
    example all payments applied to one charge). Every criterion is optional.

    Args:
        care_plan_event_id: The reference number of one history entry; leave "" if unknown.
        care_plan_id: The plan of care reference number; leave "" if unknown.
        customer_id: The patient reference number; leave "" if unknown.
        source_event_id: The reference number of an earlier entry, to find the entries that point back to it; leave "" if unknown.
    """
    match = _criteria(care_plan_event_id=care_plan_event_id, care_plan_id=care_plan_id,
                      customer_id=customer_id, source_event_id=source_event_id)
    rows = ctx.find("care_plan_events", **match)
    return str(rows) if rows else f"No plan-of-care history found for {match}."


@tool(owner="agent", rw="read")
def find_appointment_series(ctx: ToolContext, series_id: str = "", customer_id: str = "", care_plan_id: str = "",
                            package_id: str = "", wc_case_id: str = "", membership_id: str = "") -> str:
    """Look up a patient's appointment series — the standing block of booked visits at a clinic.

    Each series shows its visit format, status, clinic and therapist, the standing weekday and time
    pattern, start and end dates, what funds it (a plan of care, a visit package, a workers' compensation
    referral or a wellness membership), the appointments still booked, any missed-visit fees owed, any
    booking restriction, and pause or closing details. Search by the series reference number, the patient,
    or the reference number of the plan of care, package, referral or membership that funds it; all are
    optional.

    Args:
        series_id: The appointment series reference number; leave "" if unknown.
        customer_id: The patient reference number; leave "" if unknown.
        care_plan_id: The funding plan of care reference number; leave "" if unknown.
        package_id: The funding visit package reference number; leave "" if unknown.
        wc_case_id: The funding workers' compensation referral reference number; leave "" if unknown.
        membership_id: The funding wellness membership reference number; leave "" if unknown.
    """
    match = _criteria(series_id=series_id, customer_id=customer_id, care_plan_id=care_plan_id,
                      package_id=package_id, wc_case_id=wc_case_id, membership_id=membership_id)
    rows = ctx.find("appointment_series", **match)
    return str(rows) if rows else f"No appointment series found for {match}."


@tool(owner="agent", rw="read")
def find_series_events(ctx: ToolContext, series_event_id: str = "", series_id: str = "", customer_id: str = "",
                       source_event_id: str = "") -> str:
    """Look up the appointment history of a series.

    The history covers bookings, attended appointments, reschedules, cancellations (with the notice given,
    how it reached the clinic and the reason), no-shows, late-cancellation and no-show fees, fee waivers,
    payments and refunds, and releases of remaining appointments. Search by the entry's reference number,
    the series, the patient, or the reference of the earlier entry an entry points back to (for example the
    fee charged for a given no-show). Every criterion is optional.

    Args:
        series_event_id: The reference number of one history entry; leave "" if unknown.
        series_id: The appointment series reference number; leave "" if unknown.
        customer_id: The patient reference number; leave "" if unknown.
        source_event_id: The reference number of an earlier entry, to find the entries that point back to it; leave "" if unknown.
    """
    match = _criteria(series_event_id=series_event_id, series_id=series_id, customer_id=customer_id,
                      source_event_id=source_event_id)
    rows = ctx.find("series_events", **match)
    return str(rows) if rows else f"No appointment history found for {match}."


@tool(owner="agent", rw="read")
def find_visit_packages(ctx: ToolContext, package_id: str = "", customer_id: str = "") -> str:
    """Look up self-pay visit packages a patient has bought.

    Each package shows its tier, status, clinic, list price, discount and purchase price, visits
    purchased and remaining, installments, Good Faith Estimate details, the condition and any surgery date
    it was bought for, activation and expiry dates, the amount paid so far, and freeze or closing details.
    Search by the package reference number or the patient reference number; both are optional.

    Args:
        package_id: The visit package reference number; leave "" if unknown.
        customer_id: The patient reference number; leave "" if unknown.
    """
    match = _criteria(package_id=package_id, customer_id=customer_id)
    rows = ctx.find("visit_packages", **match)
    return str(rows) if rows else f"No visit packages found for {match}."


@tool(owner="agent", rw="read")
def find_package_events(ctx: ToolContext, package_event_id: str = "", package_id: str = "", customer_id: str = "",
                        source_event_id: str = "", recipient_customer_id: str = "") -> str:
    """Look up the history of a self-pay visit package.

    The history covers payments and installments, visits credited, visits used at appointments, visits
    forfeited for missed appointments, visits expired, refunded or transferred to a family member, refunds
    issued, and billing disputes. Search by the entry's reference number, the package, the patient, the
    reference of the earlier entry an entry points back to, or the patient who received transferred visits.
    Every criterion is optional.

    Args:
        package_event_id: The reference number of one history entry; leave "" if unknown.
        package_id: The visit package reference number; leave "" if unknown.
        customer_id: The patient reference number of the package holder; leave "" if unknown.
        source_event_id: The reference number of an earlier entry, to find the entries that point back to it; leave "" if unknown.
        recipient_customer_id: The patient reference number of someone who received transferred visits; leave "" if unknown.
    """
    match = _criteria(package_event_id=package_event_id, package_id=package_id, customer_id=customer_id,
                      source_event_id=source_event_id, recipient_customer_id=recipient_customer_id)
    rows = ctx.find("package_events", **match)
    return str(rows) if rows else f"No package history found for {match}."


@tool(owner="agent", rw="read")
def find_package_refund_requests(ctx: ToolContext, refund_request_id: str = "", customer_id: str = "",
                                 package_id: str = "") -> str:
    """Look up requests to cancel a visit package for a refund, with their progress.

    Each request shows the package, the date the patient asked, the unused visits and refund amount at
    that time, and where the request stands. Search by the request reference number, the patient or the
    package; all are optional.

    Args:
        refund_request_id: The refund request reference number; leave "" if unknown.
        customer_id: The patient reference number; leave "" if unknown.
        package_id: The visit package reference number; leave "" if unknown.
    """
    match = _criteria(refund_request_id=refund_request_id, customer_id=customer_id, package_id=package_id)
    rows = ctx.find("package_refund_requests", **match)
    return str(rows) if rows else f"No package refund requests found for {match}."


@tool(owner="agent", rw="read")
def find_payment_plans(ctx: ToolContext, payment_plan_id: str = "", customer_id: str = "",
                       hardship_case_id: str = "") -> str:
    """Look up patient payment plan agreements.

    Each agreement shows its tier, status, enrolled balance, down payment, monthly installment, number of
    months, due day, automatic payment set-up, how it was enrolled, the signing, first due and default
    dates, reinstatements and modifications used, and the balance still owed under the plan. Search by
    the agreement reference number, the patient, or the hardship determination that supports a hardship
    plan; all are optional.

    Args:
        payment_plan_id: The payment plan reference number; leave "" if unknown.
        customer_id: The patient reference number; leave "" if unknown.
        hardship_case_id: The hardship determination reference number supporting the plan; leave "" if unknown.
    """
    match = _criteria(payment_plan_id=payment_plan_id, customer_id=customer_id, hardship_case_id=hardship_case_id)
    rows = ctx.find("payment_plans", **match)
    return str(rows) if rows else f"No payment plans found for {match}."


@tool(owner="agent", rw="read")
def find_payment_plan_events(ctx: ToolContext, payment_plan_event_id: str = "", payment_plan_id: str = "",
                             customer_id: str = "", care_plan_id: str = "", source_event_id: str = "") -> str:
    """Look up the history of a patient payment plan.

    The history covers charges moved into the plan, late and returned-payment fees, payments (down
    payment, installments, extra principal, payoff), adjustments, missed installments, failed automatic
    payments, payment holidays and default notices. Search by the entry's reference number, the payment
    plan, the patient, the plan of care a moved charge came from, or the reference of the earlier entry an
    entry points back to. Every criterion is optional.

    Args:
        payment_plan_event_id: The reference number of one history entry; leave "" if unknown.
        payment_plan_id: The payment plan reference number; leave "" if unknown.
        customer_id: The patient reference number; leave "" if unknown.
        care_plan_id: The plan of care a moved charge came from; leave "" if unknown.
        source_event_id: The reference number of an earlier entry, to find the entries that point back to it; leave "" if unknown.
    """
    match = _criteria(payment_plan_event_id=payment_plan_event_id, payment_plan_id=payment_plan_id,
                      customer_id=customer_id, care_plan_id=care_plan_id, source_event_id=source_event_id)
    rows = ctx.find("payment_plan_events", **match)
    return str(rows) if rows else f"No payment plan history found for {match}."


@tool(owner="agent", rw="read")
def find_wc_cases(ctx: ToolContext, wc_case_id: str = "", customer_id: str = "") -> str:
    """Look up workers' compensation referrals for an injured worker.

    Each referral shows its program, status, clinic, employer, carrier, claim number, adjuster, date of
    injury and body part, the carrier's compensability position and Form 63 date, the entry documents on
    file, the work status, the adjuster authorization in force with its remaining visits and weekly
    frequency, the amount billed and still unpaid, and suspension or discharge details. Search by the
    referral reference number or the patient reference number; both are optional.

    Args:
        wc_case_id: The workers' compensation referral reference number; leave "" if unknown.
        customer_id: The patient (injured worker) reference number; leave "" if unknown.
    """
    match = _criteria(wc_case_id=wc_case_id, customer_id=customer_id)
    rows = ctx.find("wc_cases", **match)
    return str(rows) if rows else f"No workers' compensation referrals found for {match}."


@tool(owner="agent", rw="read")
def find_wc_events(ctx: ToolContext, wc_event_id: str = "", wc_case_id: str = "", customer_id: str = "",
                   source_event_id: str = "") -> str:
    """Look up the billing and reporting history of a workers' compensation referral.

    The history covers adjuster authorizations, recorded visits and program days, charges billed with
    their submission dates and payer, payments with remittance numbers, adjustments, late-payment
    penalties, reports sent and missed visits reported. Search by the entry's reference number, the
    referral, the patient, or the reference of the charge an entry points back to. Every criterion is
    optional.

    Args:
        wc_event_id: The reference number of one history entry; leave "" if unknown.
        wc_case_id: The workers' compensation referral reference number; leave "" if unknown.
        customer_id: The patient (injured worker) reference number; leave "" if unknown.
        source_event_id: The reference number of a charge, to find the payments, adjustments and penalties on it; leave "" if unknown.
    """
    match = _criteria(wc_event_id=wc_event_id, wc_case_id=wc_case_id, customer_id=customer_id,
                      source_event_id=source_event_id)
    rows = ctx.find("wc_events", **match)
    return str(rows) if rows else f"No workers' compensation history found for {match}."


@tool(owner="agent", rw="read")
def find_wellness_memberships(ctx: ToolContext, membership_id: str = "", customer_id: str = "") -> str:
    """Look up wellness memberships.

    Each membership shows its tier, status, home clinic, sign-up and start dates, billing day, monthly
    dues, commitment end date, clearance and enrollment-fee details, freeze, past-due and cancellation
    dates, the maintenance sessions available and any dues owed. Search by the membership reference number
    or the patient reference number; both are optional.

    Args:
        membership_id: The wellness membership reference number; leave "" if unknown.
        customer_id: The member's patient reference number; leave "" if unknown.
    """
    match = _criteria(membership_id=membership_id, customer_id=customer_id)
    rows = ctx.find("wellness_memberships", **match)
    return str(rows) if rows else f"No wellness memberships found for {match}."


@tool(owner="agent", rw="read")
def find_membership_events(ctx: ToolContext, membership_event_id: str = "", membership_id: str = "",
                           customer_id: str = "", source_event_id: str = "") -> str:
    """Look up the billing and usage history of a wellness membership.

    The history covers dues and fees billed by billing period, payments, adjustments and refunds, sessions
    credited, sessions, screens, analyses and classes attended, sessions forfeited or expired, and guest
    passes used. Search by the entry's reference number, the membership, the member, or the reference of
    the earlier entry an entry points back to. Every criterion is optional.

    Args:
        membership_event_id: The reference number of one history entry; leave "" if unknown.
        membership_id: The wellness membership reference number; leave "" if unknown.
        customer_id: The member's patient reference number; leave "" if unknown.
        source_event_id: The reference number of an earlier entry, to find the entries that point back to it; leave "" if unknown.
    """
    match = _criteria(membership_event_id=membership_event_id, membership_id=membership_id,
                      customer_id=customer_id, source_event_id=source_event_id)
    rows = ctx.find("membership_events", **match)
    return str(rows) if rows else f"No membership history found for {match}."


@tool(owner="agent", rw="read")
def find_membership_requests(ctx: ToolContext, request_id: str = "", customer_id: str = "",
                             membership_id: str = "") -> str:
    """Look up membership requests (cancellation, freeze or tier change) and where each stands.

    Each request shows what was asked, the date it is to take effect and its progress. Search by the
    request reference number, the member or the membership; all are optional.

    Args:
        request_id: The membership request reference number; leave "" if unknown.
        customer_id: The member's patient reference number; leave "" if unknown.
        membership_id: The wellness membership reference number; leave "" if unknown.
    """
    match = _criteria(request_id=request_id, customer_id=customer_id, membership_id=membership_id)
    rows = ctx.find("membership_requests", **match)
    return str(rows) if rows else f"No membership requests found for {match}."


@tool(owner="agent", rw="read")
def find_hardship_cases(ctx: ToolContext, hardship_case_id: str = "", customer_id: str = "") -> str:
    """Look up Patient Hardship Discount Program applications and determinations.

    Each case shows the level applied for or approved, its status, household size and income, the
    poverty-guideline percentage, any presumptive benefits program, the documents due date and extensions,
    the determination, effective and expiry dates, who approved, any denial or revocation reason, and the
    discount granted so far. Search by the case reference number or the patient reference number; both are
    optional.

    Args:
        hardship_case_id: The hardship case reference number; leave "" if unknown.
        customer_id: The applicant's patient reference number; leave "" if unknown.
    """
    match = _criteria(hardship_case_id=hardship_case_id, customer_id=customer_id)
    rows = ctx.find("hardship_cases", **match)
    return str(rows) if rows else f"No hardship cases found for {match}."


@tool(owner="agent", rw="read")
def find_hardship_events(ctx: ToolContext, hardship_event_id: str = "", hardship_case_id: str = "",
                         customer_id: str = "", care_plan_id: str = "", source_event_id: str = "") -> str:
    """Look up the history of a hardship case: documents received, discounts applied to plan-of-care charges, and discounts reversed.

    Search by the entry's reference number, the hardship case, the applicant, the plan of care a
    discounted charge is on, or the reference of the charge or discount an entry points back to. Every
    criterion is optional.

    Args:
        hardship_event_id: The reference number of one history entry; leave "" if unknown.
        hardship_case_id: The hardship case reference number; leave "" if unknown.
        customer_id: The applicant's patient reference number; leave "" if unknown.
        care_plan_id: The plan of care of a discounted charge; leave "" if unknown.
        source_event_id: The reference number of a charge or discount, to find the entries that point back to it; leave "" if unknown.
    """
    match = _criteria(hardship_event_id=hardship_event_id, hardship_case_id=hardship_case_id,
                      customer_id=customer_id, care_plan_id=care_plan_id, source_event_id=source_event_id)
    rows = ctx.find("hardship_events", **match)
    return str(rows) if rows else f"No hardship history found for {match}."


@tool(owner="agent", rw="read")
def find_verification_log(ctx: ToolContext, verification_id: str = "", customer_id: str = "") -> str:
    """Look up the recorded outcome of identity verification for a caller.

    The record shows whether the patient's identity has been verified on this call and when the latest
    attempt was made. Search by the verification reference number or the patient reference number; both
    are optional.

    Args:
        verification_id: The verification record reference number; leave "" if unknown.
        customer_id: The patient reference number; leave "" if unknown.
    """
    match = _criteria(verification_id=verification_id, customer_id=customer_id)
    rows = ctx.find("verification_log", **match)
    return str(rows) if rows else f"No identity verification recorded for {match}."


@tool(owner="agent", rw="read")
def find_handoff_log(ctx: ToolContext, handoff_id: str = "", customer_id: str = "") -> str:
    """Look up handoffs of a patient to a human patient services representative, with the reason and time of each.

    Search by the handoff reference number or the patient reference number; both are optional.

    Args:
        handoff_id: The handoff record reference number; leave "" if unknown.
        customer_id: The patient reference number; leave "" if unknown.
    """
    match = _criteria(handoff_id=handoff_id, customer_id=customer_id)
    rows = ctx.find("handoff_log", **match)
    return str(rows) if rows else f"No handoffs recorded for {match}."


@tool(owner="agent", rw="write")
def verify_patient_identity(ctx: ToolContext, customer_id: str, date_of_birth: str = "", phone_number: str = "",
                            email: str = "", postal_code: str = "", account_number: str = "") -> str:
    """Verify the caller's identity against the patient profile and record the outcome.

    Identity must be verified before any account information is discussed or any change, payment or
    refund is made. This tool does the comparison itself: it checks each detail the caller gives against
    the patient profile, counts how many match, and verification passes only when at least 2 of them
    match. The patient reference number is used only to open the profile and never counts as a match.
    Callers usually give only some details, so pass exactly what was said and leave the rest "". The
    outcome is recorded; if a first attempt fails and a later attempt with more details passes, the pass
    stands.

    Args:
        customer_id: The patient reference number, read from the patient profile lookup. Required; used only to open the profile and never counted as a match.
        date_of_birth: The date of birth the caller states, as YYYY-MM-DD; leave "" if not stated.
        phone_number: The phone number the caller states is on file, 10 digits with no punctuation; leave "" if not stated.
        email: The email address the caller states is on file, exactly as said; leave "" if not stated.
        postal_code: The 5-digit ZIP code of the mailing address the caller states; leave "" if not stated.
        account_number: The patient account number from a statement, PM- followed by 7 digits; leave "" if not stated.
    """
    if not customer_id:
        return "Error: customer_id is required; look up the patient profile first and pass its reference number."
    rows = ctx.find("customers", customer_id=customer_id)
    if not rows:
        return f"Error: no patient profile {customer_id}; cannot verify."
    rec = rows[0]
    # The locator customer_id is deliberately NOT a credential.
    supplied = {"date_of_birth": date_of_birth, "phone_number": phone_number, "email": email,
                "postal_code": postal_code, "account_number": account_number}
    matched = sum(1 for field, value in supplied.items()
                  if value and str(rec.get(field) or "").strip().lower() == str(value).strip().lower())
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
        return f"Identity verified for patient {customer_id}."
    return (f"Identity NOT verified for patient {customer_id}: {matched} of the required 2 details matched. "
            "Ask the caller for another detail on file and try again.")


@tool(owner="agent", rw="write")
def transfer_to_human_agent(ctx: ToolContext, customer_id: str, reason: str) -> str:
    """Hand the patient over to a human patient services representative and record the handoff and its reason.

    Use it in one of two situations only: when no Piedmont Motion policy can resolve what the patient is
    asking for, or when the patient has explicitly asked to speak with a person at least 2 times during
    the call.

    Args:
        customer_id: The patient reference number, read from the patient profile lookup.
        reason: Why the patient is being handed over; exactly one of POLICY_NOT_COVERED (current policy offers no way to resolve the request) or CUSTOMER_REQUESTED (the patient has explicitly asked for a human representative at least 2 times).
    """
    allowed = {"POLICY_NOT_COVERED", "CUSTOMER_REQUESTED"}
    if reason not in allowed:
        return f"Error: unknown handoff reason '{reason}'. Valid: {', '.join(sorted(allowed))}."
    if not ctx.find("customers", customer_id=customer_id):
        return f"Error: no patient profile {customer_id}; cannot record the handoff."
    rid = ctx.make_id("hof_", customer_id, reason)
    ctx.create("handoff_log", rid, handoff_id=rid, customer_id=customer_id, reason=reason, created_at=ctx.now())
    return f"Handoff to a human representative recorded for patient {customer_id} ({reason})."

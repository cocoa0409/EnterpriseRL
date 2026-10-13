"""Shared tools for env_0055_military_health_plan_administrator (Westbridge Military Health Services,
TRICARE West Region). Output of the erl-scenario-blueprint skill.

Every tool in this file is a SHARE tool, always present in its owner's tool list:
  - one record finder per table (the customers finder doubles as the identity entry and also accepts
    what a caller can state: name, phone number, email, DoD Benefits Number, date of birth);
  - verify_beneficiary_identity, which compares the credentials the caller states against the DEERS
    profile itself and passes at 3 matches (K = 3), storing only the verified outcome;
  - transfer_to_human_agent, with exactly two reasons (POLICY_NOT_COVERED, CUSTOMER_REQUESTED); a
    customer-requested transfer applies once the caller has explicitly asked for a person 2 times (R = 2).
Customer-originated writes (consents, signatures, confirmations of the caller's own requests) are
per-difficulty hidden task tools, never share tools.
"""

from erlbench import ToolContext, tool


@tool(owner="agent", rw="read")
def find_deers_life_events(ctx: ToolContext, life_event_id: str = "", customer_id: str = "") -> str:
    """Look up the qualifying life events DEERS has recorded for a beneficiary - marriages, divorces,
    births and adoptions, moves and permanent changes of station, changes in the sponsor's status,
    gains or losses of other health insurance and similar events - with the date each event occurred
    and the date it was entered in DEERS.

    Every reference number below is optional; supply whichever are already known from earlier
    lookups or from the caller. All matching records are returned; when nothing matches, a short
    message says so.

    Args:
        life_event_id: The reference number of the DEERS life-event record; leave "" if unknown.
        customer_id: The beneficiary reference number (for a family record, the beneficiary the
            record belongs to); leave "" if unknown.
    """
    match = {k: v for k, v in {"life_event_id": life_event_id, "customer_id": customer_id}.items() if v}
    rows = ctx.find("deers_life_events", **match)
    return str(rows) if rows else f"No matching records found for {match}."


@tool(owner="agent", rw="read")
def find_providers(ctx: ToolContext, provider_id: str = "", provider_name: str = "", specialty: str = "",
                   service_area: str = "", provider_kind: str = "", panel_status: str = "") -> str:
    """Look up a provider, military hospital or clinic, facility or equipment supplier in the TRICARE
    West provider directory, including its network relationship, specialty, Prime Service Area and
    whether it is taking new TRICARE Prime enrollees as a primary care manager. Search by the directory
    reference number, by the name the caller gives, or browse by specialty, service area, network
    relationship and panel status; the criteria combine, every one is optional, and all matching
    directory entries are returned.

    Args:
        provider_id: The provider directory reference number; leave "" if unknown.
        provider_name: The provider, practice or facility name as the caller states it (matched without
            regard to capitalisation, spacing or punctuation); leave "" if not given.
        specialty: One of family_medicine, internal_medicine, pediatrics, obstetrics_gynecology,
            cardiology, orthopedic_surgery, dermatology, behavioral_health, rehabilitative_therapy,
            diagnostic_imaging, applied_behavior_analysis, durable_medical_equipment_supplier,
            home_health_agency, skilled_nursing_facility, acute_care_hospital, psychiatric_hospital,
            urgent_care_center; leave "" to include every specialty.
        service_area: One of puget_sound, san_diego, colorado_springs, las_vegas, san_antonio, el_paso,
            oahu, non_psa; leave "" to include every area.
        provider_kind: One of mtf_clinic, network_primary_care, network_specialist, network_facility,
            non_network_participating, non_network_nonparticipating; leave "" to include every kind.
        panel_status: One of open, closed_to_new_patients, not_a_pcm; leave "" to include every status.
    """
    match = {k: v for k, v in {"provider_id": provider_id, "provider_name": provider_name,
                               "specialty": specialty, "service_area": service_area,
                               "provider_kind": provider_kind, "panel_status": panel_status}.items() if v}
    if not match:
        return "Error: give at least one search criterion for the provider directory."
    # reference numbers match exactly; spoken or browsed criteria match after normalisation
    spoken = {k: v for k, v in match.items() if k != "provider_id"}
    if spoken:
        rows = ctx.fuzzy_find("providers", **spoken)
        if provider_id:
            rows = [r for r in rows if r.get("provider_id") == provider_id]
    else:
        rows = ctx.find("providers", provider_id=provider_id)
    return str(rows) if rows else f"No provider directory entries found for {match}."


@tool(owner="agent", rw="read")
def find_identity_verifications(ctx: ToolContext, verification_id: str = "", customer_id: str = "") -> str:
    """Look up the identity-verification outcome on record for a beneficiary in this contact.

    Every reference number below is optional; supply whichever are already known from earlier
    lookups or from the caller. All matching records are returned; when nothing matches, a short
    message says so.

    Args:
        verification_id: The reference number of the verification record; leave "" if unknown.
        customer_id: The beneficiary reference number (for a family record, the beneficiary the
            record belongs to); leave "" if unknown.
    """
    match = {k: v for k, v in {"verification_id": verification_id, "customer_id": customer_id}.items() if v}
    rows = ctx.find("identity_verifications", **match)
    return str(rows) if rows else f"No matching records found for {match}."


@tool(owner="agent", rw="read")
def find_handoff_log(ctx: ToolContext, handoff_id: str = "", customer_id: str = "") -> str:
    """Look up the transfers to a human representative recorded for a beneficiary.

    Every reference number below is optional; supply whichever are already known from earlier
    lookups or from the caller. All matching records are returned; when nothing matches, a short
    message says so.

    Args:
        handoff_id: The reference number of the handoff record; leave "" if unknown.
        customer_id: The beneficiary reference number (for a family record, the beneficiary the
            record belongs to); leave "" if unknown.
    """
    match = {k: v for k, v in {"handoff_id": handoff_id, "customer_id": customer_id}.items() if v}
    rows = ctx.find("handoff_log", **match)
    return str(rows) if rows else f"No matching records found for {match}."


@tool(owner="agent", rw="read")
def find_prime_enrollments(ctx: ToolContext, prime_enrollment_id: str = "", customer_id: str = "", qualifying_life_event_id: str = "") -> str:
    """Look up TRICARE Prime enrollments: the Prime tier held, enrollment status, effective and
    disenrollment dates, the basis of the enrollment, the enrollment-fee arrangement (whether the
    enrollment carries the family's fee, individual or family level, installment frequency and
    payment method), the current fee balance and whether other health insurance is on file.

    Every reference number below is optional; supply whichever are already known from earlier
    lookups or from the caller. All matching records are returned; when nothing matches, a short
    message says so.

    Args:
        prime_enrollment_id: The TRICARE Prime enrollment reference number; leave "" if unknown.
        customer_id: The beneficiary reference number (for a family record, the beneficiary the
            record belongs to); leave "" if unknown.
        qualifying_life_event_id: The reference number of the DEERS life event an enrollment or
            change relied on; leave "" if unknown.
    """
    match = {k: v for k, v in {"prime_enrollment_id": prime_enrollment_id, "customer_id": customer_id, "qualifying_life_event_id": qualifying_life_event_id}.items() if v}
    rows = ctx.find("prime_enrollments", **match)
    return str(rows) if rows else f"No matching records found for {match}."


@tool(owner="agent", rw="read")
def find_prime_fee_ledger(ctx: ToolContext, prime_fee_entry_id: str = "", prime_enrollment_id: str = "", customer_id: str = "", related_fee_entry_id: str = "") -> str:
    """Look up TRICARE Prime enrollment-fee activity: installment charges with the coverage period each
    one pays for, payments received, proration credits and refunds, each with its amount and posting
    date.

    Every reference number below is optional; supply whichever are already known from earlier
    lookups or from the caller. All matching records are returned; when nothing matches, a short
    message says so.

    Args:
        prime_fee_entry_id: The reference number of a Prime enrollment-fee entry; leave "" if
            unknown.
        prime_enrollment_id: The TRICARE Prime enrollment reference number; leave "" if unknown.
        customer_id: The beneficiary reference number (for a family record, the beneficiary the
            record belongs to); leave "" if unknown.
        related_fee_entry_id: The reference number of the fee entry this entry settles, credits or
            refunds; leave "" if unknown.
    """
    match = {k: v for k, v in {"prime_fee_entry_id": prime_fee_entry_id, "prime_enrollment_id": prime_enrollment_id, "customer_id": customer_id, "related_fee_entry_id": related_fee_entry_id}.items() if v}
    rows = ctx.find("prime_fee_ledger", **match)
    return str(rows) if rows else f"No matching records found for {match}."


@tool(owner="agent", rw="read")
def find_prime_pcm_assignments(ctx: ToolContext, pcm_assignment_id: str = "", prime_enrollment_id: str = "", customer_id: str = "", provider_id: str = "") -> str:
    """Look up the primary care manager history of a TRICARE Prime enrollee - each PCM assignment with
    its effective date and reason - together with any signed waivers of the primary care access
    standard.

    Every reference number below is optional; supply whichever are already known from earlier
    lookups or from the caller. All matching records are returned; when nothing matches, a short
    message says so.

    Args:
        pcm_assignment_id: The reference number of a PCM assignment or access-waiver record; leave
            "" if unknown.
        prime_enrollment_id: The TRICARE Prime enrollment reference number; leave "" if unknown.
        customer_id: The beneficiary reference number (for a family record, the beneficiary the
            record belongs to); leave "" if unknown.
        provider_id: The provider directory reference number; leave "" if unknown.
    """
    match = {k: v for k, v in {"pcm_assignment_id": pcm_assignment_id, "prime_enrollment_id": prime_enrollment_id, "customer_id": customer_id, "provider_id": provider_id}.items() if v}
    rows = ctx.find("prime_pcm_assignments", **match)
    return str(rows) if rows else f"No matching records found for {match}."


@tool(owner="agent", rw="read")
def find_prime_claim_lines(ctx: ToolContext, prime_claim_line_id: str = "", prime_enrollment_id: str = "", customer_id: str = "", provider_id: str = "", referral_authorization_id: str = "", reversed_claim_line_id: str = "") -> str:
    """Look up adjudicated TRICARE Prime claim lines and their reversals: claim and line number, date
    of service, provider, benefit class, the referral that covered the line, whether point-of-
    service charges applied, the allowed amount, other-insurance payment and the beneficiary's cost
    share.

    Every reference number below is optional; supply whichever are already known from earlier
    lookups or from the caller. All matching records are returned; when nothing matches, a short
    message says so.

    Args:
        prime_claim_line_id: The reference number of an adjudicated Prime claim line; leave "" if
            unknown.
        prime_enrollment_id: The TRICARE Prime enrollment reference number; leave "" if unknown.
        customer_id: The beneficiary reference number (for a family record, the beneficiary the
            record belongs to); leave "" if unknown.
        provider_id: The provider directory reference number; leave "" if unknown.
        referral_authorization_id: The referral or authorization reference number; leave "" if
            unknown.
        reversed_claim_line_id: The reference number of the claim line a reversal withdrew; leave ""
            if unknown.
    """
    match = {k: v for k, v in {"prime_claim_line_id": prime_claim_line_id, "prime_enrollment_id": prime_enrollment_id, "customer_id": customer_id, "provider_id": provider_id, "referral_authorization_id": referral_authorization_id, "reversed_claim_line_id": reversed_claim_line_id}.items() if v}
    rows = ctx.find("prime_claim_lines", **match)
    return str(rows) if rows else f"No matching records found for {match}."


@tool(owner="agent", rw="read")
def find_prime_enrollment_requests(ctx: ToolContext, prime_request_id: str = "", customer_id: str = "", prime_enrollment_id: str = "", requested_provider_id: str = "") -> str:
    """Look up TRICARE Prime requests taken by customer service, such as a voluntary disenrollment
    awaiting the beneficiary's confirmation or a request for a military clinic primary care manager
    awaiting the clinic's decision.

    Every reference number below is optional; supply whichever are already known from earlier
    lookups or from the caller. All matching records are returned; when nothing matches, a short
    message says so.

    Args:
        prime_request_id: The reference number of a Prime request taken by customer service; leave
            "" if unknown.
        customer_id: The beneficiary reference number (for a family record, the beneficiary the
            record belongs to); leave "" if unknown.
        prime_enrollment_id: The TRICARE Prime enrollment reference number; leave "" if unknown.
        requested_provider_id: The provider directory reference number of the military clinic
            requested as PCM; leave "" if unknown.
    """
    match = {k: v for k, v in {"prime_request_id": prime_request_id, "customer_id": customer_id, "prime_enrollment_id": prime_enrollment_id, "requested_provider_id": requested_provider_id}.items() if v}
    rows = ctx.find("prime_enrollment_requests", **match)
    return str(rows) if rows else f"No matching records found for {match}."


@tool(owner="agent", rw="read")
def find_select_enrollments(ctx: ToolContext, select_enrollment_id: str = "", customer_id: str = "", qualifying_life_event_id: str = "") -> str:
    """Look up TRICARE Select enrollments: the Select tier held, enrollment status, effective and
    disenrollment dates, the basis of the enrollment, the enrollment-fee arrangement, the current
    fee balance and whether other health insurance is on file.

    Every reference number below is optional; supply whichever are already known from earlier
    lookups or from the caller. All matching records are returned; when nothing matches, a short
    message says so.

    Args:
        select_enrollment_id: The TRICARE Select enrollment reference number; leave "" if unknown.
        customer_id: The beneficiary reference number (for a family record, the beneficiary the
            record belongs to); leave "" if unknown.
        qualifying_life_event_id: The reference number of the DEERS life event an enrollment or
            change relied on; leave "" if unknown.
    """
    match = {k: v for k, v in {"select_enrollment_id": select_enrollment_id, "customer_id": customer_id, "qualifying_life_event_id": qualifying_life_event_id}.items() if v}
    rows = ctx.find("select_enrollments", **match)
    return str(rows) if rows else f"No matching records found for {match}."


@tool(owner="agent", rw="read")
def find_select_fee_ledger(ctx: ToolContext, select_fee_entry_id: str = "", select_enrollment_id: str = "", customer_id: str = "", related_fee_entry_id: str = "") -> str:
    """Look up TRICARE Select enrollment-fee activity: installment charges with the coverage period
    each one pays for, payments, proration credits and refunds.

    Every reference number below is optional; supply whichever are already known from earlier
    lookups or from the caller. All matching records are returned; when nothing matches, a short
    message says so.

    Args:
        select_fee_entry_id: The reference number of a Select enrollment-fee entry; leave "" if
            unknown.
        select_enrollment_id: The TRICARE Select enrollment reference number; leave "" if unknown.
        customer_id: The beneficiary reference number (for a family record, the beneficiary the
            record belongs to); leave "" if unknown.
        related_fee_entry_id: The reference number of the fee entry this entry settles, credits or
            refunds; leave "" if unknown.
    """
    match = {k: v for k, v in {"select_fee_entry_id": select_fee_entry_id, "select_enrollment_id": select_enrollment_id, "customer_id": customer_id, "related_fee_entry_id": related_fee_entry_id}.items() if v}
    rows = ctx.find("select_fee_ledger", **match)
    return str(rows) if rows else f"No matching records found for {match}."


@tool(owner="agent", rw="read")
def find_select_claim_lines(ctx: ToolContext, select_claim_line_id: str = "", select_enrollment_id: str = "", customer_id: str = "", provider_id: str = "", prior_authorization_id: str = "", reversed_claim_line_id: str = "") -> str:
    """Look up adjudicated TRICARE Select claim lines and their reversals: claim and line number, dates
    of service and receipt, provider and its network status on the service date, benefit class,
    inpatient days, the authorization that covered the line, billed and allowed amounts, other-
    insurance payment, deductible applied, beneficiary liability, TRICARE payment and the outcome of
    the line.

    Every reference number below is optional; supply whichever are already known from earlier
    lookups or from the caller. All matching records are returned; when nothing matches, a short
    message says so.

    Args:
        select_claim_line_id: The reference number of an adjudicated Select claim line; leave "" if
            unknown.
        select_enrollment_id: The TRICARE Select enrollment reference number; leave "" if unknown.
        customer_id: The beneficiary reference number (for a family record, the beneficiary the
            record belongs to); leave "" if unknown.
        provider_id: The provider directory reference number; leave "" if unknown.
        prior_authorization_id: The reference number of the authorization that covered a claim line;
            leave "" if unknown.
        reversed_claim_line_id: The reference number of the claim line a reversal withdrew; leave ""
            if unknown.
    """
    match = {k: v for k, v in {"select_claim_line_id": select_claim_line_id, "select_enrollment_id": select_enrollment_id, "customer_id": customer_id, "provider_id": provider_id, "prior_authorization_id": prior_authorization_id, "reversed_claim_line_id": reversed_claim_line_id}.items() if v}
    rows = ctx.find("select_claim_lines", **match)
    return str(rows) if rows else f"No matching records found for {match}."


@tool(owner="agent", rw="read")
def find_select_enrollment_requests(ctx: ToolContext, select_request_id: str = "", customer_id: str = "", select_enrollment_id: str = "") -> str:
    """Look up TRICARE Select requests taken by customer service, such as a voluntary disenrollment
    awaiting the beneficiary's confirmation.

    Every reference number below is optional; supply whichever are already known from earlier
    lookups or from the caller. All matching records are returned; when nothing matches, a short
    message says so.

    Args:
        select_request_id: The reference number of a Select request taken by customer service; leave
            "" if unknown.
        customer_id: The beneficiary reference number (for a family record, the beneficiary the
            record belongs to); leave "" if unknown.
        select_enrollment_id: The TRICARE Select enrollment reference number; leave "" if unknown.
    """
    match = {k: v for k, v in {"select_request_id": select_request_id, "customer_id": customer_id, "select_enrollment_id": select_enrollment_id}.items() if v}
    rows = ctx.find("select_enrollment_requests", **match)
    return str(rows) if rows else f"No matching records found for {match}."


@tool(owner="agent", rw="read")
def find_premium_plan_enrollments(ctx: ToolContext, premium_enrollment_id: str = "", customer_id: str = "", qualifying_life_event_id: str = "") -> str:
    """Look up TRICARE Reserve Select, TRICARE Retired Reserve and TRICARE Young Adult plans: the plan
    and coverage type held, status, coverage effective and termination dates, the basis of the
    purchase, the recurring payment method, the current premium balance, the date of the latest
    coverage-type change and whether other health insurance is on file.

    Every reference number below is optional; supply whichever are already known from earlier
    lookups or from the caller. All matching records are returned; when nothing matches, a short
    message says so.

    Args:
        premium_enrollment_id: The premium-based plan reference number; leave "" if unknown.
        customer_id: The beneficiary reference number (for a family record, the beneficiary the
            record belongs to); leave "" if unknown.
        qualifying_life_event_id: The reference number of the DEERS life event an enrollment or
            change relied on; leave "" if unknown.
    """
    match = {k: v for k, v in {"premium_enrollment_id": premium_enrollment_id, "customer_id": customer_id, "qualifying_life_event_id": qualifying_life_event_id}.items() if v}
    rows = ctx.find("premium_plan_enrollments", **match)
    return str(rows) if rows else f"No matching records found for {match}."


@tool(owner="agent", rw="read")
def find_premium_ledger(ctx: ToolContext, premium_entry_id: str = "", premium_enrollment_id: str = "", customer_id: str = "", related_premium_entry_id: str = "") -> str:
    """Look up premium activity on a premium-based plan: bills for each coverage month with their due
    date, kind and days covered, payments, proration credits and refunds.

    Every reference number below is optional; supply whichever are already known from earlier
    lookups or from the caller. All matching records are returned; when nothing matches, a short
    message says so.

    Args:
        premium_entry_id: The reference number of a premium ledger entry; leave "" if unknown.
        premium_enrollment_id: The premium-based plan reference number; leave "" if unknown.
        customer_id: The beneficiary reference number (for a family record, the beneficiary the
            record belongs to); leave "" if unknown.
        related_premium_entry_id: The reference number of the premium entry this entry settles,
            credits or refunds; leave "" if unknown.
    """
    match = {k: v for k, v in {"premium_entry_id": premium_entry_id, "premium_enrollment_id": premium_enrollment_id, "customer_id": customer_id, "related_premium_entry_id": related_premium_entry_id}.items() if v}
    rows = ctx.find("premium_ledger", **match)
    return str(rows) if rows else f"No matching records found for {match}."


@tool(owner="agent", rw="read")
def find_premium_claim_lines(ctx: ToolContext, premium_claim_line_id: str = "", premium_enrollment_id: str = "", customer_id: str = "", provider_id: str = "", reversed_claim_line_id: str = "") -> str:
    """Look up adjudicated claim lines under a premium-based plan and their reversals, with the cost-
    share key each line was priced under, the allowed amount, deductible applied and beneficiary
    liability.

    Every reference number below is optional; supply whichever are already known from earlier
    lookups or from the caller. All matching records are returned; when nothing matches, a short
    message says so.

    Args:
        premium_claim_line_id: The reference number of an adjudicated premium-plan claim line; leave
            "" if unknown.
        premium_enrollment_id: The premium-based plan reference number; leave "" if unknown.
        customer_id: The beneficiary reference number (for a family record, the beneficiary the
            record belongs to); leave "" if unknown.
        provider_id: The provider directory reference number; leave "" if unknown.
        reversed_claim_line_id: The reference number of the claim line a reversal withdrew; leave ""
            if unknown.
    """
    match = {k: v for k, v in {"premium_claim_line_id": premium_claim_line_id, "premium_enrollment_id": premium_enrollment_id, "customer_id": customer_id, "provider_id": provider_id, "reversed_claim_line_id": reversed_claim_line_id}.items() if v}
    rows = ctx.find("premium_claim_lines", **match)
    return str(rows) if rows else f"No matching records found for {match}."


@tool(owner="agent", rw="read")
def find_premium_plan_requests(ctx: ToolContext, premium_request_id: str = "", customer_id: str = "", premium_enrollment_id: str = "") -> str:
    """Look up premium-plan requests taken by customer service, such as a termination awaiting the
    purchaser's confirmation.

    Every reference number below is optional; supply whichever are already known from earlier
    lookups or from the caller. All matching records are returned; when nothing matches, a short
    message says so.

    Args:
        premium_request_id: The reference number of a premium-plan request taken by customer
            service; leave "" if unknown.
        customer_id: The beneficiary reference number (for a family record, the beneficiary the
            record belongs to); leave "" if unknown.
        premium_enrollment_id: The premium-based plan reference number; leave "" if unknown.
    """
    match = {k: v for k, v in {"premium_request_id": premium_request_id, "customer_id": customer_id, "premium_enrollment_id": premium_enrollment_id}.items() if v}
    rows = ctx.find("premium_plan_requests", **match)
    return str(rows) if rows else f"No matching records found for {match}."


@tool(owner="agent", rw="read")
def find_referral_authorizations(ctx: ToolContext, referral_authorization_id: str = "", customer_id: str = "", requesting_provider_id: str = "", servicing_provider_id: str = "") -> str:
    """Look up referrals and authorizations: the authorization type, status, the referral number on the
    letter, requesting and servicing providers, the plan it was requested under, request and
    decision dates, any denial reason, the validity span, units authorized and units remaining, and
    any change of servicing provider.

    Every reference number below is optional; supply whichever are already known from earlier
    lookups or from the caller. All matching records are returned; when nothing matches, a short
    message says so.

    Args:
        referral_authorization_id: The referral or authorization reference number; leave "" if
            unknown.
        customer_id: The beneficiary reference number (for a family record, the beneficiary the
            record belongs to); leave "" if unknown.
        requesting_provider_id: The provider directory reference number of the PCM or provider who
            requested the authorization; leave "" if unknown.
        servicing_provider_id: The provider directory reference number of the provider authorized to
            deliver the care; leave "" if unknown.
    """
    match = {k: v for k, v in {"referral_authorization_id": referral_authorization_id, "customer_id": customer_id, "requesting_provider_id": requesting_provider_id, "servicing_provider_id": servicing_provider_id}.items() if v}
    rows = ctx.find("referral_authorizations", **match)
    return str(rows) if rows else f"No matching records found for {match}."


@tool(owner="agent", rw="read")
def find_referral_unit_ledger(ctx: ToolContext, referral_unit_entry_id: str = "", referral_authorization_id: str = "", customer_id: str = "") -> str:
    """Look up the unit history of a referral or authorization: units granted on approval, extensions
    with their new end dates, visits, days, hours or rental months used against a claim line, and
    units released at cancellation or expiry.

    Every reference number below is optional; supply whichever are already known from earlier
    lookups or from the caller. All matching records are returned; when nothing matches, a short
    message says so.

    Args:
        referral_unit_entry_id: The reference number of an authorization unit entry; leave "" if
            unknown.
        referral_authorization_id: The referral or authorization reference number; leave "" if
            unknown.
        customer_id: The beneficiary reference number (for a family record, the beneficiary the
            record belongs to); leave "" if unknown.
    """
    match = {k: v for k, v in {"referral_unit_entry_id": referral_unit_entry_id, "referral_authorization_id": referral_authorization_id, "customer_id": customer_id}.items() if v}
    rows = ctx.find("referral_unit_ledger", **match)
    return str(rows) if rows else f"No matching records found for {match}."


@tool(owner="agent", rw="read")
def find_referral_requests(ctx: ToolContext, referral_request_id: str = "", customer_id: str = "", referral_authorization_id: str = "") -> str:
    """Look up authorization requests taken by customer service, such as a cancellation awaiting the
    patient's confirmation.

    Every reference number below is optional; supply whichever are already known from earlier
    lookups or from the caller. All matching records are returned; when nothing matches, a short
    message says so.

    Args:
        referral_request_id: The reference number of an authorization request taken by customer
            service; leave "" if unknown.
        customer_id: The beneficiary reference number (for a family record, the beneficiary the
            record belongs to); leave "" if unknown.
        referral_authorization_id: The referral or authorization reference number; leave "" if
            unknown.
    """
    match = {k: v for k, v in {"referral_request_id": referral_request_id, "customer_id": customer_id, "referral_authorization_id": referral_authorization_id}.items() if v}
    rows = ctx.find("referral_requests", **match)
    return str(rows) if rows else f"No matching records found for {match}."


@tool(owner="agent", rw="read")
def find_appeal_cases(ctx: ToolContext, appeal_case_id: str = "", customer_id: str = "", subject_claim_line_id: str = "", subject_referral_authorization_id: str = "", subject_enrollment_id: str = "") -> str:
    """Look up appeal, review and grievance cases: the case type, status, case reference, who filed and
    whether an appointment of representative is on file, what the case is about (claim line,
    authorization, enrollment, allowed amount or service complaint) and the record it concerns, the
    determination, filing, acknowledgment, decision and escalation dates, the review track, any
    dismissal reason and the amount in dispute.

    Every reference number below is optional; supply whichever are already known from earlier
    lookups or from the caller. All matching records are returned; when nothing matches, a short
    message says so.

    Args:
        appeal_case_id: The appeal, review or grievance case reference number; leave "" if unknown.
        customer_id: The beneficiary reference number (for a family record, the beneficiary the
            record belongs to); leave "" if unknown.
        subject_claim_line_id: The reference number of the claim line a case is about; leave "" if
            unknown.
        subject_referral_authorization_id: The reference number of the authorization a case is
            about; leave "" if unknown.
        subject_enrollment_id: The reference number of the enrollment or plan a case is about; leave
            "" if unknown.
    """
    match = {k: v for k, v in {"appeal_case_id": appeal_case_id, "customer_id": customer_id, "subject_claim_line_id": subject_claim_line_id, "subject_referral_authorization_id": subject_referral_authorization_id, "subject_enrollment_id": subject_enrollment_id}.items() if v}
    rows = ctx.find("appeal_cases", **match)
    return str(rows) if rows else f"No matching records found for {match}."


@tool(owner="agent", rw="read")
def find_appeal_case_documents(ctx: ToolContext, appeal_document_id: str = "", appeal_case_id: str = "", customer_id: str = "") -> str:
    """Look up the documents received for a case and the records requests the reviewer has sent, with
    the kind of document, date and sender.

    Every reference number below is optional; supply whichever are already known from earlier
    lookups or from the caller. All matching records are returned; when nothing matches, a short
    message says so.

    Args:
        appeal_document_id: The reference number of a case document record; leave "" if unknown.
        appeal_case_id: The appeal, review or grievance case reference number; leave "" if unknown.
        customer_id: The beneficiary reference number (for a family record, the beneficiary the
            record belongs to); leave "" if unknown.
    """
    match = {k: v for k, v in {"appeal_document_id": appeal_document_id, "appeal_case_id": appeal_case_id, "customer_id": customer_id}.items() if v}
    rows = ctx.find("appeal_case_documents", **match)
    return str(rows) if rows else f"No matching records found for {match}."


@tool(owner="agent", rw="read")
def find_appeal_requests(ctx: ToolContext, appeal_request_id: str = "", customer_id: str = "", appeal_case_id: str = "") -> str:
    """Look up case requests taken by customer service, such as a withdrawal or a next-level request
    awaiting the appellant's confirmation.

    Every reference number below is optional; supply whichever are already known from earlier
    lookups or from the caller. All matching records are returned; when nothing matches, a short
    message says so.

    Args:
        appeal_request_id: The reference number of a case request taken by customer service; leave
            "" if unknown.
        customer_id: The beneficiary reference number (for a family record, the beneficiary the
            record belongs to); leave "" if unknown.
        appeal_case_id: The appeal, review or grievance case reference number; leave "" if unknown.
    """
    match = {k: v for k, v in {"appeal_request_id": appeal_request_id, "customer_id": customer_id, "appeal_case_id": appeal_case_id}.items() if v}
    rows = ctx.find("appeal_requests", **match)
    return str(rows) if rows else f"No matching records found for {match}."


@tool(owner="agent", rw="read")
def find_echo_registrations(ctx: ToolContext, echo_registration_id: str = "", customer_id: str = "") -> str:
    """Look up Extended Care Health Option (ECHO) registrations: the tier by sponsor pay grade, status,
    qualifying condition, Exceptional Family Member Program confirmation, and application, effective
    and end dates.

    Every reference number below is optional; supply whichever are already known from earlier
    lookups or from the caller. All matching records are returned; when nothing matches, a short
    message says so.

    Args:
        echo_registration_id: The ECHO registration reference number; leave "" if unknown.
        customer_id: The beneficiary reference number (for a family record, the beneficiary the
            record belongs to); leave "" if unknown.
    """
    match = {k: v for k, v in {"echo_registration_id": echo_registration_id, "customer_id": customer_id}.items() if v}
    rows = ctx.find("echo_registrations", **match)
    return str(rows) if rows else f"No matching records found for {match}."


@tool(owner="agent", rw="read")
def find_echo_service_authorizations(ctx: ToolContext, echo_authorization_id: str = "", echo_registration_id: str = "", customer_id: str = "", provider_id: str = "") -> str:
    """Look up the ECHO services the case manager has authorized for a registration, with the months
    covered, hours per month and the authorized provider.

    Every reference number below is optional; supply whichever are already known from earlier
    lookups or from the caller. All matching records are returned; when nothing matches, a short
    message says so.

    Args:
        echo_authorization_id: The reference number of an ECHO service authorization; leave "" if
            unknown.
        echo_registration_id: The ECHO registration reference number; leave "" if unknown.
        customer_id: The beneficiary reference number (for a family record, the beneficiary the
            record belongs to); leave "" if unknown.
        provider_id: The provider directory reference number; leave "" if unknown.
    """
    match = {k: v for k, v in {"echo_authorization_id": echo_authorization_id, "echo_registration_id": echo_registration_id, "customer_id": customer_id, "provider_id": provider_id}.items() if v}
    rows = ctx.find("echo_service_authorizations", **match)
    return str(rows) if rows else f"No matching records found for {match}."


@tool(owner="agent", rw="read")
def find_echo_benefit_ledger(ctx: ToolContext, echo_entry_id: str = "", echo_registration_id: str = "", customer_id: str = "", reversed_entry_id: str = "") -> str:
    """Look up ECHO payment activity: paid ECHO claim lines with the government share, service month,
    fiscal year and hours, monthly family cost shares, and reversals of either.

    Every reference number below is optional; supply whichever are already known from earlier
    lookups or from the caller. All matching records are returned; when nothing matches, a short
    message says so.

    Args:
        echo_entry_id: The reference number of an ECHO payment or cost-share entry; leave "" if
            unknown.
        echo_registration_id: The ECHO registration reference number; leave "" if unknown.
        customer_id: The beneficiary reference number (for a family record, the beneficiary the
            record belongs to); leave "" if unknown.
        reversed_entry_id: The reference number of the entry a reversal withdrew; leave "" if
            unknown.
    """
    match = {k: v for k, v in {"echo_entry_id": echo_entry_id, "echo_registration_id": echo_registration_id, "customer_id": customer_id, "reversed_entry_id": reversed_entry_id}.items() if v}
    rows = ctx.find("echo_benefit_ledger", **match)
    return str(rows) if rows else f"No matching records found for {match}."


@tool(owner="agent", rw="read")
def find_echo_requests(ctx: ToolContext, echo_request_id: str = "", customer_id: str = "", echo_registration_id: str = "") -> str:
    """Look up ECHO requests taken by customer service, such as a registration closure awaiting the
    family's confirmation.

    Every reference number below is optional; supply whichever are already known from earlier
    lookups or from the caller. All matching records are returned; when nothing matches, a short
    message says so.

    Args:
        echo_request_id: The reference number of an ECHO request taken by customer service; leave ""
            if unknown.
        customer_id: The beneficiary reference number (for a family record, the beneficiary the
            record belongs to); leave "" if unknown.
        echo_registration_id: The ECHO registration reference number; leave "" if unknown.
    """
    match = {k: v for k, v in {"echo_request_id": echo_request_id, "customer_id": customer_id, "echo_registration_id": echo_registration_id}.items() if v}
    rows = ctx.find("echo_requests", **match)
    return str(rows) if rows else f"No matching records found for {match}."


@tool(owner="agent", rw="read")
def find_dme_placements(ctx: ToolContext, dme_placement_id: str = "", customer_id: str = "", supplier_provider_id: str = "", referral_authorization_id: str = "") -> str:
    """Look up durable medical equipment placed with a patient: the payment class, status, item and
    HCPCS code, supplier, plan and authorization, order, delivery, ownership and return dates, the
    purchase fee-schedule amount, any compliance result and the rental months paid in the current
    rental period.

    Every reference number below is optional; supply whichever are already known from earlier
    lookups or from the caller. All matching records are returned; when nothing matches, a short
    message says so.

    Args:
        dme_placement_id: The equipment placement reference number; leave "" if unknown.
        customer_id: The beneficiary reference number (for a family record, the beneficiary the
            record belongs to); leave "" if unknown.
        supplier_provider_id: The provider directory reference number of the equipment supplier;
            leave "" if unknown.
        referral_authorization_id: The referral or authorization reference number; leave "" if
            unknown.
    """
    match = {k: v for k, v in {"dme_placement_id": dme_placement_id, "customer_id": customer_id, "supplier_provider_id": supplier_provider_id, "referral_authorization_id": referral_authorization_id}.items() if v}
    rows = ctx.find("dme_placements", **match)
    return str(rows) if rows else f"No matching records found for {match}."


@tool(owner="agent", rw="read")
def find_dme_rental_ledger(ctx: ToolContext, dme_rental_entry_id: str = "", dme_placement_id: str = "", customer_id: str = "", reversed_entry_id: str = "") -> str:
    """Look up equipment payment activity: each paid rental month with its position in the rental
    period, purchase and servicing payments, and reversals, with allowed amounts and patient cost
    shares.

    Every reference number below is optional; supply whichever are already known from earlier
    lookups or from the caller. All matching records are returned; when nothing matches, a short
    message says so.

    Args:
        dme_rental_entry_id: The reference number of an equipment rental ledger entry; leave "" if
            unknown.
        dme_placement_id: The equipment placement reference number; leave "" if unknown.
        customer_id: The beneficiary reference number (for a family record, the beneficiary the
            record belongs to); leave "" if unknown.
        reversed_entry_id: The reference number of the entry a reversal withdrew; leave "" if
            unknown.
    """
    match = {k: v for k, v in {"dme_rental_entry_id": dme_rental_entry_id, "dme_placement_id": dme_placement_id, "customer_id": customer_id, "reversed_entry_id": reversed_entry_id}.items() if v}
    rows = ctx.find("dme_rental_ledger", **match)
    return str(rows) if rows else f"No matching records found for {match}."


@tool(owner="agent", rw="read")
def find_dme_requests(ctx: ToolContext, dme_request_id: str = "", customer_id: str = "", dme_placement_id: str = "") -> str:
    """Look up equipment requests taken by customer service, such as an order cancellation or a return
    awaiting the patient's confirmation.

    Every reference number below is optional; supply whichever are already known from earlier
    lookups or from the caller. All matching records are returned; when nothing matches, a short
    message says so.

    Args:
        dme_request_id: The reference number of an equipment request taken by customer service;
            leave "" if unknown.
        customer_id: The beneficiary reference number (for a family record, the beneficiary the
            record belongs to); leave "" if unknown.
        dme_placement_id: The equipment placement reference number; leave "" if unknown.
    """
    match = {k: v for k, v in {"dme_request_id": dme_request_id, "customer_id": customer_id, "dme_placement_id": dme_placement_id}.items() if v}
    rows = ctx.find("dme_requests", **match)
    return str(rows) if rows else f"No matching records found for {match}."


@tool(owner="agent", rw="read")
def find_customers(ctx: ToolContext, customer_id: str = "", sponsor_customer_id: str = "", name: str = "",
                   phone_number: str = "", email: str = "", dbn: str = "", date_of_birth: str = "") -> str:
    """Look up a beneficiary's DEERS profile to establish whose coverage the call is about. Search by the
    beneficiary reference number, by the sponsor's reference number to list the whole family, or by what
    the caller can state - full name, phone number, email address, the 11-digit DoD Benefits Number on the
    ID card, or date of birth. Every criterion is optional and they combine; supply whichever are known.
    The profile shows contact details, the residential ZIP code and Prime Service Area, the relationship
    to the sponsor, the DEERS beneficiary category, the sponsor's pay grade and initial entry date into
    service, and Medicare status. Finding a profile does not verify the caller's identity.

    Args:
        customer_id: The beneficiary reference number; leave "" if unknown.
        sponsor_customer_id: The sponsor's beneficiary reference number, to list every family member under
            that sponsor; leave "" if unknown.
        name: Full name as the caller states it; leave "" if not given.
        phone_number: Phone number as the caller states it (10 digits); leave "" if not given.
        email: Email address as the caller states it; leave "" if not given.
        dbn: The 11-digit DoD Benefits Number from the caller's ID card; leave "" if not given.
        date_of_birth: Date of birth as YYYY-MM-DD; leave "" if not given.
    """
    match = {k: v for k, v in {"customer_id": customer_id, "sponsor_customer_id": sponsor_customer_id,
                               "name": name, "phone_number": phone_number, "email": email,
                               "dbn": dbn, "date_of_birth": date_of_birth}.items() if v}
    if not match:
        return "Error: provide at least one reference number or profile detail to find the beneficiary."
    # reference numbers match exactly; what the caller states matches after normalisation
    ids = {k: v for k, v in match.items() if k in ("customer_id", "sponsor_customer_id")}
    spoken = {k: v for k, v in match.items() if k not in ids}
    if spoken:
        rows = ctx.fuzzy_find("customers", **spoken)
        rows = [r for r in rows if all(r.get(k) == v for k, v in ids.items())]
    else:
        rows = ctx.find("customers", **ids)
    if not rows:
        return f"No beneficiary profile matches {match}."
    if len(rows) > 1 and not sponsor_customer_id:
        return (f"Error: {len(rows)} beneficiary profiles match {match}; ask the caller for one more "
                "detail (for example the DoD Benefits Number or date of birth) to tell them apart.")
    return str(rows if len(rows) > 1 else rows[0])


@tool(owner="agent", rw="write")
def verify_beneficiary_identity(ctx: ToolContext, customer_id: str, dbn: str = "", date_of_birth: str = "",
                                sponsor_ssn_last4: str = "", phone_number: str = "", email: str = "",
                                residence_zip: str = "") -> str:
    """Verify the caller's identity against the beneficiary's DEERS profile and record the outcome.
    Identity must be verified before any coverage, claim, referral, appeal or payment detail is discussed
    or changed. This tool performs the comparison itself: each piece of identifying information the caller
    states is compared with the profile, and verification passes when at least 3 of them match. The
    beneficiary reference number only retrieves the profile and never counts as a match. Pass exactly the
    values the caller gave, as given, and leave the others blank. If a first attempt falls short, ask for
    another item and call again; once verification has passed it stays passed for this beneficiary.

    Args:
        customer_id: The beneficiary reference number read from the profile lookup. Required; used only
            to retrieve the profile and not counted as a match.
        dbn: The 11-digit DoD Benefits Number the caller reads from the ID card; leave "" if not stated.
        date_of_birth: The caller's date of birth as YYYY-MM-DD; leave "" if not stated.
        sponsor_ssn_last4: The last four digits of the sponsor's Social Security number; leave "" if not
            stated.
        phone_number: The phone number on file as the caller states it (10 digits); leave "" if not
            stated.
        email: The email address on file as the caller states it; leave "" if not stated.
        residence_zip: The 5-digit ZIP code of the residential address; leave "" if not stated.
    """
    if not customer_id:
        return "Error: customer_id is required; look up the beneficiary profile first and pass its reference number."
    rows = ctx.find("customers", customer_id=customer_id)
    if not rows:
        return f"Error: no beneficiary profile {customer_id}; cannot verify."
    rec = rows[0]

    def _norm(value):
        # compare as stated, ignoring case, spaces and punctuation
        return "".join(ch for ch in str(value).casefold() if ch.isalnum())

    supplied = {"dbn": dbn, "date_of_birth": date_of_birth, "sponsor_ssn_last4": sponsor_ssn_last4,
                "phone_number": phone_number, "email": email, "residence_zip": residence_zip}
    matched = sum(1 for field, value in supplied.items()
                  if value and rec.get(field) not in (None, "") and _norm(rec.get(field)) == _norm(value))
    verified = matched >= 3
    rid = ctx.make_id("ver_", customer_id)
    # store only the reproducible outcome; upsert and never downgrade a pass
    prior = ctx.find("identity_verifications", verification_id=rid)
    verified = verified or bool(prior and prior[0].get("verified"))
    if prior:
        ctx.update("identity_verifications", rid, verified=verified, verified_at=ctx.now())
    else:
        ctx.create("identity_verifications", rid, verification_id=rid, customer_id=customer_id,
                   verified=verified, verified_at=ctx.now())
    if verified:
        return f"Identity verified for beneficiary {customer_id}."
    return (f"Identity NOT verified for beneficiary {customer_id}: only {matched} of the 3 required details "
            "matched. Ask the caller for another detail on file and try again.")


@tool(owner="agent", rw="write")
def transfer_to_human_agent(ctx: ToolContext, customer_id: str, reason: str) -> str:
    """Transfer the caller to a Westbridge beneficiary services representative and record the transfer
    with its reason. Use POLICY_NOT_COVERED when no published TRICARE West policy can resolve what the
    caller is asking for; use CUSTOMER_REQUESTED when the caller has explicitly asked to speak with a
    person 2 times.

    Args:
        customer_id: The beneficiary reference number read from the profile lookup (the profile must
            exist).
        reason: Exactly one of POLICY_NOT_COVERED (no published policy can resolve the request) or
            CUSTOMER_REQUESTED (the caller has explicitly asked for a person 2 times); never free text.
    """
    allowed = {"POLICY_NOT_COVERED", "CUSTOMER_REQUESTED"}
    if reason not in allowed:
        return f"Error: unknown transfer reason '{reason}'. Valid: {', '.join(sorted(allowed))}."
    if not ctx.find("customers", customer_id=customer_id):
        return f"Error: no beneficiary profile {customer_id}; cannot record the transfer."
    rid = ctx.make_id("hof_", customer_id, reason)
    ctx.create("handoff_log", rid, handoff_id=rid, customer_id=customer_id, reason=reason,
               created_at=ctx.now())
    return f"Transfer to a beneficiary services representative recorded for {customer_id} ({reason})."

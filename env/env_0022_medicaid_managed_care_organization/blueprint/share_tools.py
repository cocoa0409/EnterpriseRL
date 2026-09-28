"""Shared tools for env_0022_medicaid_managed_care_organization (Prairie Ridge Health Plan).
Output of the erl-scenario-blueprint skill.

Every tool here is a SHARE tool, always present in its owner's tool list:
  - one lookup per record type (the customers lookup doubles as the identity entry),
  - the identity verification write (at least 2 matching credentials pass),
  - the transfer to a human representative (reasons POLICY_NOT_COVERED / CUSTOMER_REQUESTED;
    CUSTOMER_REQUESTED applies once the member has asked for a person 2 times).
Lookups never judge eligibility, status or timing; they only return what is on file.
"""

from erlbench import ToolContext, tool


def _match(pairs):
    # Keep only the criteria the caller actually supplied.
    return {k: v for k, v in pairs.items() if v}


# --------------------------------------------------------------------------- members
@tool(owner="agent", rw="read")
def find_customers(ctx: ToolContext, customer_id: str = "", medicaid_id: str = "", name: str = "",
                   phone_number: str = "", email: str = "", date_of_birth: str = "") -> str:
    """Look up a Prairie Ridge member profile to establish whose account a call is about.

    You can search by the member reference number or by what a caller can naturally tell you: the
    Medicaid ID printed on the member ID card, the member's full name, the phone number or email
    address on file, or the date of birth. Supply whichever you have; every criterion is optional,
    and small differences in spacing, punctuation or capitalisation are ignored. The profile returned
    shows contact details, mailing address, county and whether it is urban or rural, preferred
    language, household size, sex on the state record, date of birth and the date the profile was
    opened. Finding a profile only tells you who the caller says they are about; it does not verify
    the caller's identity.

    Args:
        customer_id: The member reference number, if already known; leave "" if unknown.
        medicaid_id: The state Medicaid ID from the member ID card, 2 letters followed by 8 digits (e.g. PR48213377); leave "" if not given.
        name: The member's full name as the caller states it; leave "" if not given.
        phone_number: The phone number the caller gives, 10 digits; leave "" if not given.
        email: The email address the caller gives; leave "" if not given.
        date_of_birth: The member's date of birth as YYYY-MM-DD; leave "" if not given.
    """
    match = _match({"customer_id": customer_id, "medicaid_id": medicaid_id, "name": name,
                    "phone_number": phone_number, "email": email, "date_of_birth": date_of_birth})
    if not match:
        return "Error: provide at least one reference number or profile detail to find the member."
    rows = ctx.fuzzy_find("customers", **match)
    if not rows:
        return f"No member profile matches {match}."
    if len(rows) > 1:
        return f"Error: {len(rows)} member profiles match {match}; ask the caller for one more detail."
    return str(rows[0])


# --------------------------------------------------------------------------- plan membership
@tool(owner="agent", rw="read")
def find_plan_memberships(ctx: ToolContext, membership_id: str = "", customer_id: str = "") -> str:
    """Look up Medicaid plan memberships: the eligibility category, membership status, enrollment and
    coverage start dates, renewal due date, any end date and its reason, how the member came to the
    plan, household income on the state file, CHIP premium balance, American Indian or Alaska Native
    status, preferred notice channel and any suspension start date.

    Search by the membership reference number or by the member reference number; both are optional.
    Returns every matching membership, or a message when none is on file.

    Args:
        membership_id: The membership reference number; leave "" if unknown.
        customer_id: The member reference number, to list that member's memberships; leave "" if unknown.
    """
    match = _match({"membership_id": membership_id, "customer_id": customer_id})
    rows = ctx.find("plan_memberships", **match)
    return str(rows) if rows else f"No plan memberships found for {match}."


@tool(owner="agent", rw="read")
def find_plan_claims(ctx: ToolContext, plan_claim_id: str = "", membership_id: str = "", customer_id: str = "") -> str:
    """Look up the medical claim history of a membership as shown on explanation-of-benefits
    statements: claim numbers, service dates and categories, billing provider, billed and paid
    amounts, the member copay assessed, adjustments and over-cap refunds with the original claim
    they point to, denial reasons, the cost-sharing period and the booking date.

    Search by the claim entry reference, the membership reference number or the member reference
    number; all are optional. Returns every matching entry, or a message when none is on file.

    Args:
        plan_claim_id: The reference of one claim history entry; leave "" if unknown.
        membership_id: The membership reference number; leave "" if unknown.
        customer_id: The member reference number; leave "" if unknown.
    """
    match = _match({"plan_claim_id": plan_claim_id, "membership_id": membership_id, "customer_id": customer_id})
    rows = ctx.find("plan_claims", **match)
    return str(rows) if rows else f"No claim history found for {match}."


@tool(owner="agent", rw="read")
def find_plan_premiums(ctx: ToolContext, plan_premium_id: str = "", membership_id: str = "", customer_id: str = "") -> str:
    """Look up CHIP family premium activity: bills by coverage month, payments with their method and
    confirmation number, and waivers with their reason, each with the date it posted.

    Search by the premium entry reference, the membership reference number or the member reference
    number; all are optional. Returns every matching entry, or a message when none is on file.

    Args:
        plan_premium_id: The reference of one premium entry; leave "" if unknown.
        membership_id: The membership reference number; leave "" if unknown.
        customer_id: The member reference number; leave "" if unknown.
    """
    match = _match({"plan_premium_id": plan_premium_id, "membership_id": membership_id, "customer_id": customer_id})
    rows = ctx.find("plan_premiums", **match)
    return str(rows) if rows else f"No premium activity found for {match}."


@tool(owner="agent", rw="read")
def find_plan_notices(ctx: ToolContext, plan_notice_id: str = "", membership_id: str = "", customer_id: str = "") -> str:
    """Look up renewal letters and member ID cards sent for a membership: renewal packets, first and
    second reminders and procedural closure notices with the renewal cycle they belong to, and ID
    cards with the reason they were issued, the delivery channel and the date sent.

    Search by the notice reference, the membership reference number or the member reference number;
    all are optional. Returns every matching notice, or a message when none is on file.

    Args:
        plan_notice_id: The reference of one notice or card issue; leave "" if unknown.
        membership_id: The membership reference number; leave "" if unknown.
        customer_id: The member reference number; leave "" if unknown.
    """
    match = _match({"plan_notice_id": plan_notice_id, "membership_id": membership_id, "customer_id": customer_id})
    rows = ctx.find("plan_notices", **match)
    return str(rows) if rows else f"No notices or cards found for {match}."


@tool(owner="agent", rw="read")
def find_plan_change_requests(ctx: ToolContext, change_request_id: str = "", customer_id: str = "", membership_id: str = "") -> str:
    """Look up requests a member made to change health plans or leave Prairie Ridge: the kind of
    request, any documented cause, the plan asked for, where the request stands and when it was
    recorded.

    Search by the request reference, the member reference number or the membership reference number;
    all are optional. Returns every matching request, or a message when none is on file.

    Args:
        change_request_id: The plan change request reference; leave "" if unknown.
        customer_id: The member reference number; leave "" if unknown.
        membership_id: The membership reference number; leave "" if unknown.
    """
    match = _match({"change_request_id": change_request_id, "customer_id": customer_id, "membership_id": membership_id})
    rows = ctx.find("plan_change_requests", **match)
    return str(rows) if rows else f"No plan change requests found for {match}."


# --------------------------------------------------------------------------- primary care
@tool(owner="agent", rw="read")
def find_pcp_assignments(ctx: ToolContext, pcp_assignment_id: str = "", customer_id: str = "", membership_id: str = "") -> str:
    """Look up a member's primary care provider assignments, current, upcoming and past: the practice
    type, provider and practice names with the provider NPI, effective and end dates, why an
    assignment ended, how it was made, its status and the distance from the member's home.

    Search by the assignment reference, the member reference number or the membership reference
    number; all are optional. Returns every matching assignment, or a message when none is on file.

    Args:
        pcp_assignment_id: The PCP assignment reference; leave "" if unknown.
        customer_id: The member reference number; leave "" if unknown.
        membership_id: The membership reference number; leave "" if unknown.
    """
    match = _match({"pcp_assignment_id": pcp_assignment_id, "customer_id": customer_id, "membership_id": membership_id})
    rows = ctx.find("pcp_assignments", **match)
    return str(rows) if rows else f"No PCP assignments found for {match}."


@tool(owner="agent", rw="read")
def find_pcp_events(ctx: ToolContext, pcp_event_id: str = "", pcp_assignment_id: str = "", customer_id: str = "") -> str:
    """Look up the history around a member's primary care assignments: change requests with their
    reason, channel and chosen provider, notices that a provider is leaving the network or has
    dismissed the member, specialist referrals, and outreach attempts to schedule a first visit.

    Search by the entry reference, the assignment reference or the member reference number; all are
    optional. Returns every matching entry, or a message when none is on file.

    Args:
        pcp_event_id: The reference of one history entry; leave "" if unknown.
        pcp_assignment_id: The PCP assignment reference; leave "" if unknown.
        customer_id: The member reference number; leave "" if unknown.
    """
    match = _match({"pcp_event_id": pcp_event_id, "pcp_assignment_id": pcp_assignment_id, "customer_id": customer_id})
    rows = ctx.find("pcp_events", **match)
    return str(rows) if rows else f"No PCP history found for {match}."


@tool(owner="agent", rw="read")
def find_pcp_visits(ctx: ToolContext, pcp_visit_id: str = "", pcp_assignment_id: str = "", customer_id: str = "") -> str:
    """Look up visits a member had with their assigned primary care provider: visit date, kind of
    visit (initial health appointment, well visit, sick visit, follow-up), in person or telehealth,
    and the claim number of the visit.

    Search by the visit reference, the assignment reference or the member reference number; all are
    optional. Returns every matching visit, or a message when none is on file.

    Args:
        pcp_visit_id: The visit reference; leave "" if unknown.
        pcp_assignment_id: The PCP assignment reference; leave "" if unknown.
        customer_id: The member reference number; leave "" if unknown.
    """
    match = _match({"pcp_visit_id": pcp_visit_id, "pcp_assignment_id": pcp_assignment_id, "customer_id": customer_id})
    rows = ctx.find("pcp_visits", **match)
    return str(rows) if rows else f"No PCP visits found for {match}."


# --------------------------------------------------------------------------- prior authorization
@tool(owner="agent", rw="read")
def find_auth_authorizations(ctx: ToolContext, authorization_id: str = "", customer_id: str = "", membership_id: str = "") -> str:
    """Look up prior authorizations: the authorization class and number, service code and therapy
    discipline, requesting and servicing providers with network status, standard or expedited review,
    how the request arose and any prior plan authorization number, received and decision dates,
    approved dates, units requested, approved and remaining, any denial reason and the status.

    Search by the authorization reference, the member reference number or the membership reference
    number; all are optional. Returns every matching authorization, or a message when none is on file.

    Args:
        authorization_id: The authorization reference; leave "" if unknown.
        customer_id: The member reference number; leave "" if unknown.
        membership_id: The membership reference number; leave "" if unknown.
    """
    match = _match({"authorization_id": authorization_id, "customer_id": customer_id, "membership_id": membership_id})
    rows = ctx.find("auth_authorizations", **match)
    return str(rows) if rows else f"No authorizations found for {match}."


@tool(owner="agent", rw="read")
def find_auth_units(ctx: ToolContext, auth_unit_id: str = "", authorization_id: str = "", customer_id: str = "") -> str:
    """Look up the units history of authorizations: units granted with the reason (first approval,
    extension, transition of care), units used by claims with the claim number and service date, and
    units released at expiry or cancellation, each with its posting date.

    Search by the entry reference, the authorization reference or the member reference number; all
    are optional. Returns every matching entry, or a message when none is on file.

    Args:
        auth_unit_id: The reference of one units entry; leave "" if unknown.
        authorization_id: The authorization reference; leave "" if unknown.
        customer_id: The member reference number; leave "" if unknown.
    """
    match = _match({"auth_unit_id": auth_unit_id, "authorization_id": authorization_id, "customer_id": customer_id})
    rows = ctx.find("auth_units", **match)
    return str(rows) if rows else f"No units history found for {match}."


@tool(owner="agent", rw="read")
def find_auth_actions(ctx: ToolContext, auth_action_id: str = "", authorization_id: str = "", customer_id: str = "") -> str:
    """Look up requests and letters on authorizations: expedite requests and who made them, extension
    requests with units and end date asked for, decision deadline extensions, and notices sent
    (approval, adverse benefit determination, request for information, review time extension,
    refused expedite) with date and channel.

    Search by the entry reference, the authorization reference or the member reference number; all
    are optional. Returns every matching entry, or a message when none is on file.

    Args:
        auth_action_id: The reference of one request or letter; leave "" if unknown.
        authorization_id: The authorization reference; leave "" if unknown.
        customer_id: The member reference number; leave "" if unknown.
    """
    match = _match({"auth_action_id": auth_action_id, "authorization_id": authorization_id, "customer_id": customer_id})
    rows = ctx.find("auth_actions", **match)
    return str(rows) if rows else f"No authorization requests or letters found for {match}."


# --------------------------------------------------------------------------- pharmacy
@tool(owner="agent", rw="read")
def find_rx_coverages(ctx: ToolContext, rx_coverage_id: str = "", customer_id: str = "", membership_id: str = "") -> str:
    """Look up a member's pharmacy benefit: the PrairieRx plan, status, effective and end dates, any
    lock-in pharmacy and prescriber with the lock-in dates, and the over-the-counter allowance left
    this quarter.

    Search by the pharmacy coverage reference, the member reference number or the membership
    reference number; all are optional. Returns every matching coverage, or a message when none is
    on file.

    Args:
        rx_coverage_id: The pharmacy coverage reference; leave "" if unknown.
        customer_id: The member reference number; leave "" if unknown.
        membership_id: The membership reference number; leave "" if unknown.
    """
    match = _match({"rx_coverage_id": rx_coverage_id, "customer_id": customer_id, "membership_id": membership_id})
    rows = ctx.find("rx_coverages", **match)
    return str(rows) if rows else f"No pharmacy coverage found for {match}."


@tool(owner="agent", rw="read")
def find_rx_fills(ctx: ToolContext, rx_fill_id: str = "", rx_coverage_id: str = "", customer_id: str = "") -> str:
    """Look up pharmacy claims: paid fills, reversals, counter rejections with their reject reason and
    emergency supplies, showing prescription number, drug, NDC, schedule, formulary status, days
    supply, quantity, pharmacy, prescriber, kind of fill, copay, amount paid and any exception number.

    Search by the pharmacy claim reference, the pharmacy coverage reference or the member reference
    number; all are optional. Returns every matching entry, or a message when none is on file.

    Args:
        rx_fill_id: The reference of one pharmacy claim entry; leave "" if unknown.
        rx_coverage_id: The pharmacy coverage reference; leave "" if unknown.
        customer_id: The member reference number; leave "" if unknown.
    """
    match = _match({"rx_fill_id": rx_fill_id, "rx_coverage_id": rx_coverage_id, "customer_id": customer_id})
    rows = ctx.find("rx_fills", **match)
    return str(rows) if rows else f"No pharmacy claims found for {match}."


@tool(owner="agent", rw="read")
def find_rx_exceptions(ctx: ToolContext, rx_exception_id: str = "", rx_coverage_id: str = "", customer_id: str = "") -> str:
    """Look up pharmacy requests and overrides: prior authorization and formulary, quantity, step
    therapy and brand exceptions with their number, drug, who started them, whether the prescriber
    statement is in, decision, approval end date or denial reason; early refill overrides; and changes
    of lock-in pharmacy with their reason.

    Search by the entry reference, the pharmacy coverage reference or the member reference number;
    all are optional. Returns every matching entry, or a message when none is on file.

    Args:
        rx_exception_id: The reference of one request, decision or override; leave "" if unknown.
        rx_coverage_id: The pharmacy coverage reference; leave "" if unknown.
        customer_id: The member reference number; leave "" if unknown.
    """
    match = _match({"rx_exception_id": rx_exception_id, "rx_coverage_id": rx_coverage_id, "customer_id": customer_id})
    rows = ctx.find("rx_exceptions", **match)
    return str(rows) if rows else f"No pharmacy requests or overrides found for {match}."


@tool(owner="agent", rw="read")
def find_rx_otc_ledger(ctx: ToolContext, rx_otc_id: str = "", rx_coverage_id: str = "", customer_id: str = "") -> str:
    """Look up over-the-counter allowance activity: quarterly loads, purchases with channel and order
    number, and amounts forfeited at quarter end, each with the benefit quarter and posting date.

    Search by the entry reference, the pharmacy coverage reference or the member reference number;
    all are optional. Returns every matching entry, or a message when none is on file.

    Args:
        rx_otc_id: The reference of one allowance entry; leave "" if unknown.
        rx_coverage_id: The pharmacy coverage reference; leave "" if unknown.
        customer_id: The member reference number; leave "" if unknown.
    """
    match = _match({"rx_otc_id": rx_otc_id, "rx_coverage_id": rx_coverage_id, "customer_id": customer_id})
    rows = ctx.find("rx_otc_ledger", **match)
    return str(rows) if rows else f"No allowance activity found for {match}."


# --------------------------------------------------------------------------- transportation
@tool(owner="agent", rw="read")
def find_ride_benefits(ctx: ToolContext, ride_benefit_id: str = "", customer_id: str = "", membership_id: str = "") -> str:
    """Look up a member's transportation benefit: the RideLink level of service, status, effective and
    end dates, latest mobility assessment and physician certification dates, any suspension start
    date, value-added trips left this year and reimbursements approved but not yet paid.

    Search by the benefit reference, the member reference number or the membership reference number;
    all are optional. Returns every matching benefit, or a message when none is on file.

    Args:
        ride_benefit_id: The transportation benefit reference; leave "" if unknown.
        customer_id: The member reference number; leave "" if unknown.
        membership_id: The membership reference number; leave "" if unknown.
    """
    match = _match({"ride_benefit_id": ride_benefit_id, "customer_id": customer_id, "membership_id": membership_id})
    rows = ctx.find("ride_benefits", **match)
    return str(rows) if rows else f"No transportation benefit found for {match}."


@tool(owner="agent", rw="read")
def find_ride_trips(ctx: ToolContext, ride_trip_id: str = "", ride_benefit_id: str = "", customer_id: str = "") -> str:
    """Look up ride history: booked legs with reservation number, appointment date and time, pickup
    time, purpose, destination, miles, escorts and booking channel; completions; cancellations with
    who cancelled and how much notice was given; no-shows and who missed; late pickups with minutes
    late; standing orders; and monthly transit passes.

    Search by the entry reference, the benefit reference or the member reference number; all are
    optional. Returns every matching entry, or a message when none is on file.

    Args:
        ride_trip_id: The reference of one ride history entry; leave "" if unknown.
        ride_benefit_id: The transportation benefit reference; leave "" if unknown.
        customer_id: The member reference number; leave "" if unknown.
    """
    match = _match({"ride_trip_id": ride_trip_id, "ride_benefit_id": ride_benefit_id, "customer_id": customer_id})
    rows = ctx.find("ride_trips", **match)
    return str(rows) if rows else f"No ride history found for {match}."


@tool(owner="agent", rw="read")
def find_ride_ledger(ctx: ToolContext, ride_ledger_id: str = "", ride_benefit_id: str = "", customer_id: str = "") -> str:
    """Look up value-added trip allotments and member reimbursement claims: trips loaded, used and
    expired by benefit year, and mileage, lodging and meals or late-pickup alternative ride claims with
    claim number, trip, miles claimed and approved, amounts, payment method, denial reason and dates.

    Search by the entry reference, the benefit reference or the member reference number; all are
    optional. Returns every matching entry, or a message when none is on file.

    Args:
        ride_ledger_id: The reference of one allotment or reimbursement entry; leave "" if unknown.
        ride_benefit_id: The transportation benefit reference; leave "" if unknown.
        customer_id: The member reference number; leave "" if unknown.
    """
    match = _match({"ride_ledger_id": ride_ledger_id, "ride_benefit_id": ride_benefit_id, "customer_id": customer_id})
    rows = ctx.find("ride_ledger", **match)
    return str(rows) if rows else f"No allotment or reimbursement activity found for {match}."


# --------------------------------------------------------------------------- care management
@tool(owner="agent", rw="read")
def find_care_enrollments(ctx: ToolContext, care_enrollment_id: str = "", customer_id: str = "", membership_id: str = "") -> str:
    """Look up care management episodes: the tier, status, referral source and date, consent date,
    risk score, living setting, care team lead, any hold start date, closure date and reason, and
    personal care hours still available this period.

    Search by the episode reference, the member reference number or the membership reference number;
    all are optional. Returns every matching episode, or a message when none is on file.

    Args:
        care_enrollment_id: The care management episode reference; leave "" if unknown.
        customer_id: The member reference number; leave "" if unknown.
        membership_id: The membership reference number; leave "" if unknown.
    """
    match = _match({"care_enrollment_id": care_enrollment_id, "customer_id": customer_id, "membership_id": membership_id})
    rows = ctx.find("care_enrollments", **match)
    return str(rows) if rows else f"No care management episodes found for {match}."


@tool(owner="agent", rw="read")
def find_care_activities(ctx: ToolContext, care_activity_id: str = "", care_enrollment_id: str = "", customer_id: str = "") -> str:
    """Look up care team activity: outreach attempts and their outcome, assessments, care plan versions
    and whether the member signed, contacts by mode, follow-ups after hospital discharges, and changes
    of care team lead with the reason.

    Search by the activity reference, the episode reference or the member reference number; all are
    optional. Returns every matching activity, or a message when none is on file.

    Args:
        care_activity_id: The reference of one care activity; leave "" if unknown.
        care_enrollment_id: The care management episode reference; leave "" if unknown.
        customer_id: The member reference number; leave "" if unknown.
    """
    match = _match({"care_activity_id": care_activity_id, "care_enrollment_id": care_enrollment_id, "customer_id": customer_id})
    rows = ctx.find("care_activities", **match)
    return str(rows) if rows else f"No care activity found for {match}."


@tool(owner="agent", rw="read")
def find_care_hours(ctx: ToolContext, care_hours_id: str = "", care_enrollment_id: str = "", customer_id: str = "") -> str:
    """Look up personal care, respite and homemaker hours: hours authorized per service week, visits
    delivered with the visit date, attendant and electronic visit verification number, and hours that
    lapsed unused.

    Search by the entry reference, the episode reference or the member reference number; all are
    optional. Returns every matching entry, or a message when none is on file.

    Args:
        care_hours_id: The reference of one hours entry; leave "" if unknown.
        care_enrollment_id: The care management episode reference; leave "" if unknown.
        customer_id: The member reference number; leave "" if unknown.
    """
    match = _match({"care_hours_id": care_hours_id, "care_enrollment_id": care_enrollment_id, "customer_id": customer_id})
    rows = ctx.find("care_hours", **match)
    return str(rows) if rows else f"No care hours found for {match}."


# --------------------------------------------------------------------------- appeals and grievances
@tool(owner="agent", rw="read")
def find_appeal_cases(ctx: ToolContext, appeal_case_id: str = "", customer_id: str = "", membership_id: str = "") -> str:
    """Look up grievances, appeals, fair hearing requests and external reviews: the case type and
    number, status, filing date, who filed and how, subject, the decision or event it concerns and the
    date of its notice, any earlier plan appeal it follows, acknowledgment, due and resolution dates,
    the outcome, whether services were asked to continue and any continued-service balance.

    Search by the case reference, the member reference number or the membership reference number;
    all are optional. Returns every matching case, or a message when none is on file.

    Args:
        appeal_case_id: The case reference; leave "" if unknown.
        customer_id: The member reference number; leave "" if unknown.
        membership_id: The membership reference number; leave "" if unknown.
    """
    match = _match({"appeal_case_id": appeal_case_id, "customer_id": customer_id, "membership_id": membership_id})
    rows = ctx.find("appeal_cases", **match)
    return str(rows) if rows else f"No grievance or appeal cases found for {match}."


@tool(owner="agent", rw="read")
def find_appeal_actions(ctx: ToolContext, appeal_action_id: str = "", appeal_case_id: str = "", customer_id: str = "") -> str:
    """Look up letters and submissions on a grievance or appeal: acknowledgment, extension, refused
    expedite and resolution letters and case file copies with date and channel, evidence the member
    or a representative sent in, and case summaries sent to the hearing office or review organization.

    Search by the entry reference, the case reference or the member reference number; all are
    optional. Returns every matching entry, or a message when none is on file.

    Args:
        appeal_action_id: The reference of one letter or submission; leave "" if unknown.
        appeal_case_id: The case reference; leave "" if unknown.
        customer_id: The member reference number; leave "" if unknown.
    """
    match = _match({"appeal_action_id": appeal_action_id, "appeal_case_id": appeal_case_id, "customer_id": customer_id})
    rows = ctx.find("appeal_actions", **match)
    return str(rows) if rows else f"No letters or submissions found for {match}."


@tool(owner="agent", rw="read")
def find_appeal_continuation(ctx: ToolContext, appeal_continuation_id: str = "", appeal_case_id: str = "", customer_id: str = "") -> str:
    """Look up the cost of services that continued while an appeal was pending: each continued service
    with its claim number, date and cost, amounts waived with the reason, and repayments with their
    confirmation number.

    Search by the entry reference, the case reference or the member reference number; all are
    optional. Returns every matching entry, or a message when none is on file.

    Args:
        appeal_continuation_id: The reference of one continued-service entry; leave "" if unknown.
        appeal_case_id: The case reference; leave "" if unknown.
        customer_id: The member reference number; leave "" if unknown.
    """
    match = _match({"appeal_continuation_id": appeal_continuation_id, "appeal_case_id": appeal_case_id, "customer_id": customer_id})
    rows = ctx.find("appeal_continuation", **match)
    return str(rows) if rows else f"No continued-service activity found for {match}."


# --------------------------------------------------------------------------- service records
@tool(owner="agent", rw="read")
def find_verification_log(ctx: ToolContext, verification_id: str = "", customer_id: str = "") -> str:
    """Look up whether a member's identity has been verified on this call, and when it was last
    checked.

    Search by the verification reference or the member reference number; both are optional. Returns
    the matching record, or a message when no verification has been recorded.

    Args:
        verification_id: The verification reference; leave "" if unknown.
        customer_id: The member reference number; leave "" if unknown.
    """
    match = _match({"verification_id": verification_id, "customer_id": customer_id})
    rows = ctx.find("verification_log", **match)
    return str(rows) if rows else f"No identity verification recorded for {match}."


@tool(owner="agent", rw="read")
def find_handoff_log(ctx: ToolContext, handoff_id: str = "", customer_id: str = "") -> str:
    """Look up transfers of a member to a human representative, with the reason and time of each.

    Search by the transfer reference or the member reference number; both are optional. Returns every
    matching transfer, or a message when none is on file.

    Args:
        handoff_id: The transfer reference; leave "" if unknown.
        customer_id: The member reference number; leave "" if unknown.
    """
    match = _match({"handoff_id": handoff_id, "customer_id": customer_id})
    rows = ctx.find("handoff_log", **match)
    return str(rows) if rows else f"No transfers recorded for {match}."


# --------------------------------------------------------------------------- identity verification
@tool(owner="agent", rw="write")
def verify_member_identity(ctx: ToolContext, customer_id: str, medicaid_id: str = "", date_of_birth: str = "",
                           ssn_last4: str = "", phone_number: str = "", zip_code: str = "") -> str:
    """Verify the caller's identity against the member profile and record the outcome. Identity must
    be verified before any member information is discussed or any change is made on the account.

    This tool does the comparison itself: it checks each piece of identifying information the caller
    gives against the profile on file, counts how many match, and passes only when at least 2 match.
    The member reference number is used only to open the profile and never counts as a match; the
    member's name is not a credential. Callers usually know only some of these details, so pass
    exactly what the caller said and leave the rest empty. If a first attempt fails and a later
    attempt with more details passes, the member stays verified.

    Args:
        customer_id: The member reference number from the member profile lookup. Required; used only to open the profile and not counted as a match.
        medicaid_id: The Medicaid ID from the member ID card as the caller reads it, 2 letters followed by 8 digits; leave "" if not given.
        date_of_birth: The member's date of birth as YYYY-MM-DD; leave "" if not given.
        ssn_last4: The last 4 digits of the member's Social Security number; leave "" if not given.
        phone_number: The phone number on file as the caller states it, 10 digits with no punctuation; leave "" if not given.
        zip_code: The 5-digit ZIP code of the member's home address; leave "" if not given.
    """
    if not customer_id:
        return "Error: customer_id is required; look up the member profile first and pass its reference number."
    rows = ctx.find("customers", customer_id=customer_id)
    if not rows:
        return f"Error: no member profile {customer_id}; cannot verify."
    rec = rows[0]
    # The tool owns the comparison; the locator customer_id is never a credential.
    supplied = {"medicaid_id": medicaid_id, "date_of_birth": date_of_birth, "ssn_last4": ssn_last4,
                "phone_number": phone_number, "zip_code": zip_code}
    matched = sum(1 for field, value in supplied.items()
                  if value and str(rec.get(field, "")).strip().upper() == str(value).strip().upper())
    verified = matched >= 2
    rid = ctx.make_id("ver_", customer_id)
    # Upsert, monotonic: a later pass is never overwritten by an earlier failure; only the boolean is stored.
    prior = ctx.find("verification_log", verification_id=rid)
    verified = verified or bool(prior and prior[0].get("verified"))
    if prior:
        ctx.update("verification_log", rid, verified=verified, verified_at=ctx.now())
    else:
        ctx.create("verification_log", rid, verification_id=rid, customer_id=customer_id,
                   verified=verified, verified_at=ctx.now())
    if verified:
        return f"Identity verified for member {customer_id} ({matched} detail(s) matched on this attempt)."
    return (f"Identity NOT verified for member {customer_id}: only {matched} of the 2 required details matched. "
            "Ask the caller for another detail on file and try again.")


# --------------------------------------------------------------------------- human handoff
@tool(owner="agent", rw="write")
def transfer_to_human_agent(ctx: ToolContext, customer_id: str, reason: str) -> str:
    """Transfer the member to a human member services representative and record the transfer with its
    reason. Use it in exactly two situations: when no Prairie Ridge policy can resolve what the member
    is asking for, or when the member has explicitly asked to speak with a person 2 times.

    Args:
        customer_id: The member reference number from the member profile lookup; the profile must exist.
        reason: Why the member is being transferred; exactly one of these values, never free text:
            POLICY_NOT_COVERED - no Prairie Ridge policy can resolve the member's request;
            CUSTOMER_REQUESTED - the member has explicitly asked for a human representative 2 times.
    """
    allowed = {"POLICY_NOT_COVERED", "CUSTOMER_REQUESTED"}
    if reason not in allowed:
        return f"Error: unknown transfer reason '{reason}'. Valid: {', '.join(sorted(allowed))}."
    if not ctx.find("customers", customer_id=customer_id):
        return f"Error: no member profile {customer_id}; cannot record the transfer."
    rid = ctx.make_id("hof_", customer_id, reason)
    ctx.create("handoff_log", rid, handoff_id=rid, customer_id=customer_id, reason=reason, created_at=ctx.now())
    return f"Transfer to a human representative recorded for member {customer_id} ({reason})."

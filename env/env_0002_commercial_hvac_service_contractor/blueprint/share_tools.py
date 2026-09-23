"""Shared client-services tools for Halvorsen Mechanical & Controls, Inc.

Every tool defined here is always present in its owner's tool list: the complete
record-lookup layer across the company's files, the identity verification write, and
the transfer to a human representative. Business actions belonging to one desk are
authored as hidden task tools in that difficulty's task_tools.py, never here.
"""

from erlbench import ToolContext, tool


@tool(owner="agent", rw="read")
def find_customers(ctx: ToolContext, customer_id: str = "", company_name: str = "",
                   primary_contact_name: str = "", phone_number: str = "", email: str = "",
                   account_number: str = "") -> str:
    """Look up the account of a building owner and establish whose buildings this call is about.

    The account can be found by its customer reference number where the caller already has one, and
    otherwise by what a caller naturally states on the phone: the company on the invoices, the name of
    the facilities contact, the number the office calls back on, the billing email, or the account
    number printed on every invoice and work order. Every criterion is optional, so supply whichever
    are known; where more than one account matches, ask for one more detail before going further. The
    profile that comes back carries the company and contact names, the phone number and email, the
    billing address, the account number, the last digits of the tax identification number, the day the
    account was opened, the agreed payment terms and whether the account is on credit hold. Finding an
    account is not the same as verifying the caller, which is a separate step.

    Args:
        customer_id: The customer reference number; leave "" if unknown.
        company_name: The registered name of the owner or property management company, as stated; leave "" if not given.
        primary_contact_name: The name of the facilities contact on the account; leave "" if not given.
        phone_number: The account phone number, 10 digits; leave "" if not given.
        email: The billing and dispatch email address on the account; leave "" if not given.
        account_number: The 6-digit account number printed on invoices and work orders; leave "" if not given.
    """
    match = {k: v for k, v in {"customer_id": customer_id, "company_name": company_name,
                               "primary_contact_name": primary_contact_name,
                               "phone_number": phone_number, "email": email,
                               "account_number": account_number}.items() if v}
    if not match:
        return "Error: provide at least one detail to find the account."
    rows = ctx.fuzzy_find("customers", **match)
    if not rows:
        return f"No account matches {match}."
    if len(rows) > 1:
        return f"Error: {len(rows)} accounts match {match}; ask for one more detail to tell them apart."
    return str(rows[0])


@tool(owner="agent", rw="read")
def find_sites(ctx: ToolContext, site_id: str = "", customer_id: str = "") -> str:
    """Retrieve the buildings on file, with their addresses, use class, floor area, dispatch region
    and whether escorted access is needed. Supply the building reference number for one building, or
    the customer reference number to list every building an owner has with the company.

    Args:
        site_id: The building reference number; leave "" if unknown.
        customer_id: The customer reference number of the owner; leave "" if unknown.
    """
    match = {k: v for k, v in {"site_id": site_id, "customer_id": customer_id}.items() if v}
    rows = ctx.find("sites", **match)
    return str(rows) if rows else f"No buildings on file for {match}."


@tool(owner="agent", rw="read")
def find_equipment_units(ctx: ToolContext, equipment_id: str = "", site_id: str = "",
                         customer_id: str = "") -> str:
    """Read the equipment register: each unit's tag, kind, manufacturer, model and serial, the day it
    was placed in service, its capacity, its refrigerant and whether it is still running. Ask by unit
    reference number, by building to see the whole schedule, or by owner to see every unit on the
    account. The install date returned is the authoritative one for any question of a unit's age.

    Args:
        equipment_id: The equipment reference number; leave "" if unknown.
        site_id: The building reference number whose schedule is wanted; leave "" if unknown.
        customer_id: The customer reference number of the owner; leave "" if unknown.
    """
    match = {k: v for k, v in {"equipment_id": equipment_id, "site_id": site_id,
                               "customer_id": customer_id}.items() if v}
    rows = ctx.find("equipment_units", **match)
    return str(rows) if rows else f"No equipment on file for {match}."


@tool(owner="agent", rw="read")
def find_maintenance_agreements(ctx: ToolContext, agreement_id: str = "", customer_id: str = "",
                                site_id: str = "") -> str:
    """Retrieve preventive maintenance agreements with the tier held, the lifecycle standing, the term
    dates, the covered unit count and annual price, the visits and repair allowance still left in the
    term, the balance owed and any pending termination. Search by the agreement reference number, by
    owner for a whole portfolio, or by building for the agreement covering that site.

    Args:
        agreement_id: The maintenance agreement reference number; leave "" if unknown.
        customer_id: The customer reference number of the owner; leave "" if unknown.
        site_id: The building reference number the agreement covers; leave "" if unknown.
    """
    match = {k: v for k, v in {"agreement_id": agreement_id, "customer_id": customer_id,
                               "site_id": site_id}.items() if v}
    rows = ctx.find("maintenance_agreements", **match)
    return str(rows) if rows else f"No maintenance agreements for {match}."


@tool(owner="agent", rw="read")
def find_maintenance_events(ctx: ToolContext, event_id: str = "", agreement_id: str = "",
                            customer_id: str = "") -> str:
    """Read the maintenance history of an agreement: visits booked and completed, reports delivered,
    entitlement and allowance credited, repairs applied against coverage, instalments and fees
    invoiced, payments received and credits issued. Ask by the reference number of a single entry, by
    agreement for that contract's whole history, or by owner across their agreements.

    Args:
        event_id: The reference number of one maintenance history entry; leave "" if unknown.
        agreement_id: The maintenance agreement reference number; leave "" if unknown.
        customer_id: The customer reference number of the owner; leave "" if unknown.
    """
    match = {k: v for k, v in {"event_id": event_id, "agreement_id": agreement_id,
                               "customer_id": customer_id}.items() if v}
    rows = ctx.find("maintenance_events", **match)
    return str(rows) if rows else f"No maintenance history for {match}."


@tool(owner="agent", rw="read")
def find_maintenance_requests(ctx: ToolContext, request_id: str = "", customer_id: str = "",
                              agreement_id: str = "", site_id: str = "") -> str:
    """Look up what an owner has lodged on the maintenance side: pre-agreement inspections, signed
    acceptances, renewal acceptances, non-renewal and termination notices, reschedule and equipment
    change requests. Each entry shows what was lodged, how far it has been carried, the day it was
    asked for, the day any written notice reached the office and the day it takes effect.

    Args:
        request_id: The reference number of one lodged request; leave "" if unknown.
        customer_id: The customer reference number of the owner; leave "" if unknown.
        agreement_id: The maintenance agreement the request concerns; leave "" if unknown.
        site_id: The building the request concerns; leave "" if unknown.
    """
    match = {k: v for k, v in {"request_id": request_id, "customer_id": customer_id,
                               "agreement_id": agreement_id, "site_id": site_id}.items() if v}
    rows = ctx.find("maintenance_requests", **match)
    return str(rows) if rows else f"No maintenance requests lodged for {match}."


@tool(owner="agent", rw="read")
def find_service_programs(ctx: ToolContext, program_id: str = "", customer_id: str = "",
                          primary_site_id: str = "") -> str:
    """Retrieve the demand service rate program an account is set up on: the tier, its standing, the
    term dates, the prepaid hours and included emergency dispatches still left, the balance owed, the
    credit ceiling, whether a purchase order number is required on invoices and any reserved
    technician. Search by program reference number, by owner, or by the primary service address.

    Args:
        program_id: The rate program reference number; leave "" if unknown.
        customer_id: The customer reference number of the owner; leave "" if unknown.
        primary_site_id: The building reference number named as the primary service address; leave "" if unknown.
    """
    match = {k: v for k, v in {"program_id": program_id, "customer_id": customer_id,
                               "primary_site_id": primary_site_id}.items() if v}
    rows = ctx.find("service_programs", **match)
    return str(rows) if rows else f"No rate programs for {match}."


@tool(owner="agent", rw="read")
def find_service_events(ctx: ToolContext, event_id: str = "", program_id: str = "",
                        customer_id: str = "", site_id: str = "") -> str:
    """Read the demand service history: calls accepted and the moment they were dispatched, arrivals
    and completions with their hours and rate band, blocks of prepaid hours bought and drawn,
    emergency dispatches counted, quotes issued and their approval standing, invoices, payments and
    credits. Ask by one entry, by program, by owner, or by building.

    Args:
        event_id: The reference number of one service history entry; leave "" if unknown.
        program_id: The rate program reference number; leave "" if unknown.
        customer_id: The customer reference number of the owner; leave "" if unknown.
        site_id: The building the work was performed at; leave "" if unknown.
    """
    match = {k: v for k, v in {"event_id": event_id, "program_id": program_id,
                               "customer_id": customer_id, "site_id": site_id}.items() if v}
    rows = ctx.find("service_events", **match)
    return str(rows) if rows else f"No demand service history for {match}."


@tool(owner="agent", rw="read")
def find_service_requests(ctx: ToolContext, request_id: str = "", customer_id: str = "",
                          program_id: str = "", site_id: str = "") -> str:
    """Look up what has been lodged on the demand service side: signed enrollments, written approvals
    of quoted work, block purchase orders, emergency dispatch requests, callback claims, renewal
    acceptances and cancellation notices, each with the quote or work order it names, how far it has
    been carried and the day any written notice was received.

    Args:
        request_id: The reference number of one lodged request; leave "" if unknown.
        customer_id: The customer reference number of the owner; leave "" if unknown.
        program_id: The rate program the request concerns; leave "" if unknown.
        site_id: The building the request concerns; leave "" if unknown.
    """
    match = {k: v for k, v in {"request_id": request_id, "customer_id": customer_id,
                               "program_id": program_id, "site_id": site_id}.items() if v}
    rows = ctx.find("service_requests", **match)
    return str(rows) if rows else f"No demand service requests lodged for {match}."


@tool(owner="agent", rw="read")
def find_controls_plans(ctx: ToolContext, plan_id: str = "", customer_id: str = "",
                        site_id: str = "") -> str:
    """Retrieve building automation service plans: the tier, the standing, the term, how many points
    and panels are covered, the oldest controller generation and the software version on the system,
    the annual fee, the support hours and alarm responses still left this plan year, and the balance
    owed. Search by plan reference number, by owner, or by the building whose controls it covers.

    Args:
        plan_id: The automation service plan reference number; leave "" if unknown.
        customer_id: The customer reference number of the owner; leave "" if unknown.
        site_id: The building reference number whose controls system the plan covers; leave "" if unknown.
    """
    match = {k: v for k, v in {"plan_id": plan_id, "customer_id": customer_id,
                               "site_id": site_id}.items() if v}
    rows = ctx.find("controls_plans", **match)
    return str(rows) if rows else f"No automation service plans for {match}."


@tool(owner="agent", rw="read")
def find_controls_events(ctx: ToolContext, event_id: str = "", plan_id: str = "",
                         customer_id: str = "", site_id: str = "") -> str:
    """Read the controls history of a plan: tickets logged and closed with the hours they took and how
    they were resolved, alarms raised and when the monitoring desk acknowledged them, responses counted
    against the year's allowance, software patches, updates and upgrades applied, and the plan's
    invoices, payments and credits.

    Args:
        event_id: The reference number of one controls history entry; leave "" if unknown.
        plan_id: The automation service plan reference number; leave "" if unknown.
        customer_id: The customer reference number of the owner; leave "" if unknown.
        site_id: The building the entry concerns; leave "" if unknown.
    """
    match = {k: v for k, v in {"event_id": event_id, "plan_id": plan_id,
                               "customer_id": customer_id, "site_id": site_id}.items() if v}
    rows = ctx.find("controls_events", **match)
    return str(rows) if rows else f"No controls history for {match}."


@tool(owner="agent", rw="read")
def find_controls_requests(ctx: ToolContext, request_id: str = "", customer_id: str = "",
                           plan_id: str = "", site_id: str = "") -> str:
    """Look up what has been lodged on the automation side: controls site surveys, quote and renewal
    acceptances, non-renewal and cancellation notices, point change requests and upgrade
    authorisations, each with its standing, the day it was asked for and the day any written notice
    reached the office.

    Args:
        request_id: The reference number of one lodged request; leave "" if unknown.
        customer_id: The customer reference number of the owner; leave "" if unknown.
        plan_id: The automation service plan the request concerns; leave "" if unknown.
        site_id: The building the request concerns; leave "" if unknown.
    """
    match = {k: v for k, v in {"request_id": request_id, "customer_id": customer_id,
                               "plan_id": plan_id, "site_id": site_id}.items() if v}
    rows = ctx.find("controls_requests", **match)
    return str(rows) if rows else f"No automation requests lodged for {match}."


@tool(owner="agent", rw="read")
def find_energy_subscriptions(ctx: ToolContext, subscription_id: str = "", customer_id: str = "",
                              site_id: str = "") -> str:
    """Retrieve energy monitoring subscriptions: the tier, the standing including onboarding, the term
    dates, where the data comes from, the meters and dashboard users covered, the fixed baseline and
    the period it was measured over, the analyst hours and guaranteed savings still standing this year,
    and the balance owed.

    Args:
        subscription_id: The energy subscription reference number; leave "" if unknown.
        customer_id: The customer reference number of the owner; leave "" if unknown.
        site_id: The building reference number the subscription covers; leave "" if unknown.
    """
    match = {k: v for k, v in {"subscription_id": subscription_id, "customer_id": customer_id,
                               "site_id": site_id}.items() if v}
    rows = ctx.find("energy_subscriptions", **match)
    return str(rows) if rows else f"No energy subscriptions for {match}."


@tool(owner="agent", rw="read")
def find_energy_events(ctx: ToolContext, event_id: str = "", subscription_id: str = "",
                       customer_id: str = "", site_id: str = "") -> str:
    """Read the energy history of a subscription: meter and utility bill readings by period, reports
    delivered, analyst studies requested and delivered with their hours, faults flagged and notified,
    savings verified against the baseline with any shortfall, shortfall payments made, and the
    subscription's invoices, payments and credits.

    Args:
        event_id: The reference number of one energy history entry; leave "" if unknown.
        subscription_id: The energy subscription reference number; leave "" if unknown.
        customer_id: The customer reference number of the owner; leave "" if unknown.
        site_id: The building the entry concerns; leave "" if unknown.
    """
    match = {k: v for k, v in {"event_id": event_id, "subscription_id": subscription_id,
                               "customer_id": customer_id, "site_id": site_id}.items() if v}
    rows = ctx.find("energy_events", **match)
    return str(rows) if rows else f"No energy history for {match}."


@tool(owner="agent", rw="read")
def find_energy_requests(ctx: ToolContext, request_id: str = "", customer_id: str = "",
                         subscription_id: str = "", site_id: str = "") -> str:
    """Look up what has been lodged on the energy side: site surveys, quote and renewal acceptances,
    analysis requests, meter change requests, non-renewal and cancellation notices and claims against a
    savings guarantee, each with its standing and the dates that matter to it.

    Args:
        request_id: The reference number of one lodged request; leave "" if unknown.
        customer_id: The customer reference number of the owner; leave "" if unknown.
        subscription_id: The energy subscription the request concerns; leave "" if unknown.
        site_id: The building the request concerns; leave "" if unknown.
    """
    match = {k: v for k, v in {"request_id": request_id, "customer_id": customer_id,
                               "subscription_id": subscription_id, "site_id": site_id}.items() if v}
    rows = ctx.find("energy_requests", **match)
    return str(rows) if rows else f"No energy requests lodged for {match}."


@tool(owner="agent", rw="read")
def find_retrofit_projects(ctx: ToolContext, project_id: str = "", customer_id: str = "",
                           site_id: str = "") -> str:
    """Retrieve replacement and retrofit projects: the class of project, the stage it stands at, the
    estimate, award, equipment release, mobilisation, completion and closeout dates, the contract value
    and unit count, the scope, the balance owed, the retainage held and the change allowance left, and
    the warranty dates on the installed work.

    Args:
        project_id: The project reference number; leave "" if unknown.
        customer_id: The customer reference number of the owner; leave "" if unknown.
        site_id: The building reference number the work is at; leave "" if unknown.
    """
    match = {k: v for k, v in {"project_id": project_id, "customer_id": customer_id,
                               "site_id": site_id}.items() if v}
    rows = ctx.find("retrofit_projects", **match)
    return str(rows) if rows else f"No projects for {match}."


@tool(owner="agent", rw="read")
def find_retrofit_events(ctx: ToolContext, event_id: str = "", project_id: str = "",
                         customer_id: str = "", site_id: str = "") -> str:
    """Read a project's running record: equipment deliveries and whether they had to be stored,
    inspections passed, change orders issued with their authorisation and schedule impact, progress
    billings with the share of work earned, retainage withheld and released, payments received and
    credits issued.

    Args:
        event_id: The reference number of one project record entry; leave "" if unknown.
        project_id: The project reference number; leave "" if unknown.
        customer_id: The customer reference number of the owner; leave "" if unknown.
        site_id: The building the entry concerns; leave "" if unknown.
    """
    match = {k: v for k, v in {"event_id": event_id, "project_id": project_id,
                               "customer_id": customer_id, "site_id": site_id}.items() if v}
    rows = ctx.find("retrofit_events", **match)
    return str(rows) if rows else f"No project record entries for {match}."


@tool(owner="agent", rw="read")
def find_retrofit_requests(ctx: ToolContext, request_id: str = "", customer_id: str = "",
                           project_id: str = "", site_id: str = "") -> str:
    """Look up what has been lodged on a project: site surveys, signed proposals, written change
    authorisations naming a change order, schedule requests, cancellation notices, rebate
    authorisations and closeout acceptances, each with how far it has been carried and the day any
    written notice was received.

    Args:
        request_id: The reference number of one lodged request; leave "" if unknown.
        customer_id: The customer reference number of the owner; leave "" if unknown.
        project_id: The project the request concerns; leave "" if unknown.
        site_id: The building the request concerns; leave "" if unknown.
    """
    match = {k: v for k, v in {"request_id": request_id, "customer_id": customer_id,
                               "project_id": project_id, "site_id": site_id}.items() if v}
    rows = ctx.find("retrofit_requests", **match)
    return str(rows) if rows else f"No project requests lodged for {match}."


@tool(owner="agent", rw="read")
def find_warranty_plans(ctx: ToolContext, plan_id: str = "", customer_id: str = "",
                        site_id: str = "") -> str:
    """Retrieve extended equipment warranty plans: the tier, the standing, the cover dates and the day
    the waiting period ends, the units enrolled and the oldest unit's install date, the premium, the
    claim value still available this term and the balance owed, together with any suspension and its
    reason.

    Args:
        plan_id: The warranty plan reference number; leave "" if unknown.
        customer_id: The customer reference number of the owner; leave "" if unknown.
        site_id: The building reference number the covered units are in; leave "" if unknown.
    """
    match = {k: v for k, v in {"plan_id": plan_id, "customer_id": customer_id,
                               "site_id": site_id}.items() if v}
    rows = ctx.find("warranty_plans", **match)
    return str(rows) if rows else f"No warranty plans for {match}."


@tool(owner="agent", rw="read")
def find_warranty_events(ctx: ToolContext, event_id: str = "", plan_id: str = "",
                         customer_id: str = "", site_id: str = "") -> str:
    """Read the warranty history of a plan: claims filed with the unit, the component and the day the
    fault was found, how each claim was adjudicated and why any was denied, the value approved and the
    deductible billed, parts shipped and how they travelled, and the plan's premiums, payments and
    credits.

    Args:
        event_id: The reference number of one warranty history entry; leave "" if unknown.
        plan_id: The warranty plan reference number; leave "" if unknown.
        customer_id: The customer reference number of the owner; leave "" if unknown.
        site_id: The building the entry concerns; leave "" if unknown.
    """
    match = {k: v for k, v in {"event_id": event_id, "plan_id": plan_id,
                               "customer_id": customer_id, "site_id": site_id}.items() if v}
    rows = ctx.find("warranty_events", **match)
    return str(rows) if rows else f"No warranty history for {match}."


@tool(owner="agent", rw="read")
def find_warranty_requests(ctx: ToolContext, request_id: str = "", customer_id: str = "",
                           plan_id: str = "", site_id: str = "") -> str:
    """Look up what has been lodged on the warranty side: condition inspections, quote and renewal
    acceptances, prior authorisations naming a claim, claim appeals, non-renewal and cancellation
    notices and ownership transfers, each with its standing and the dates it turns on.

    Args:
        request_id: The reference number of one lodged request; leave "" if unknown.
        customer_id: The customer reference number of the owner; leave "" if unknown.
        plan_id: The warranty plan the request concerns; leave "" if unknown.
        site_id: The building the request concerns; leave "" if unknown.
    """
    match = {k: v for k, v in {"request_id": request_id, "customer_id": customer_id,
                               "plan_id": plan_id, "site_id": site_id}.items() if v}
    rows = ctx.find("warranty_requests", **match)
    return str(rows) if rows else f"No warranty requests lodged for {match}."


@tool(owner="agent", rw="read")
def find_iaq_programs(ctx: ToolContext, program_id: str = "", customer_id: str = "",
                      site_id: str = "") -> str:
    """Retrieve indoor air quality and filtration programs: the tier, the standing, the term dates, the
    units covered and the annual price, the filter sets still owed this program year, the day the next
    service visit is due and the balance owed.

    Args:
        program_id: The air quality program reference number; leave "" if unknown.
        customer_id: The customer reference number of the owner; leave "" if unknown.
        site_id: The building reference number the program covers; leave "" if unknown.
    """
    match = {k: v for k, v in {"program_id": program_id, "customer_id": customer_id,
                               "site_id": site_id}.items() if v}
    rows = ctx.find("iaq_programs", **match)
    return str(rows) if rows else f"No air quality programs for {match}."


@tool(owner="agent", rw="read")
def find_iaq_events(ctx: ToolContext, event_id: str = "", program_id: str = "",
                    customer_id: str = "", site_id: str = "") -> str:
    """Read the air quality history of a program: filter sets credited and fitted with their grade and
    who fitted them, coil cleaning, coating, drain treatment and ultraviolet lamp work, air quality
    tests with where the readings were taken and how they stood, tenant complaints investigated, and the
    program's invoices, payments and credits.

    Args:
        event_id: The reference number of one air quality history entry; leave "" if unknown.
        program_id: The air quality program reference number; leave "" if unknown.
        customer_id: The customer reference number of the owner; leave "" if unknown.
        site_id: The building the entry concerns; leave "" if unknown.
    """
    match = {k: v for k, v in {"event_id": event_id, "program_id": program_id,
                               "customer_id": customer_id, "site_id": site_id}.items() if v}
    rows = ctx.find("iaq_events", **match)
    return str(rows) if rows else f"No air quality history for {match}."


@tool(owner="agent", rw="read")
def find_iaq_requests(ctx: ToolContext, request_id: str = "", customer_id: str = "",
                      program_id: str = "", site_id: str = "") -> str:
    """Look up what has been lodged on the air quality side: filter schedule surveys, quote and renewal
    acceptances, tenant complaint reports, schedule change requests, non-renewal and cancellation
    notices, each with its standing and the dates that govern it.

    Args:
        request_id: The reference number of one lodged request; leave "" if unknown.
        customer_id: The customer reference number of the owner; leave "" if unknown.
        program_id: The air quality program the request concerns; leave "" if unknown.
        site_id: The building the request concerns; leave "" if unknown.
    """
    match = {k: v for k, v in {"request_id": request_id, "customer_id": customer_id,
                               "program_id": program_id, "site_id": site_id}.items() if v}
    rows = ctx.find("iaq_requests", **match)
    return str(rows) if rows else f"No air quality requests lodged for {match}."


@tool(owner="agent", rw="read")
def find_identity_verifications(ctx: ToolContext, verification_id: str = "",
                                customer_id: str = "") -> str:
    """Check whether the caller on an account has already been verified on this call and when that was
    last recorded. Ask by the verification reference number or, more usually, by the customer reference
    number of the account in hand.

    Args:
        verification_id: The verification reference number; leave "" if unknown.
        customer_id: The customer reference number of the account; leave "" if unknown.
    """
    match = {k: v for k, v in {"verification_id": verification_id,
                               "customer_id": customer_id}.items() if v}
    rows = ctx.find("identity_verifications", **match)
    return str(rows) if rows else f"No verification recorded for {match}."


@tool(owner="agent", rw="read")
def find_agent_handoffs(ctx: ToolContext, handoff_id: str = "", customer_id: str = "") -> str:
    """Review the handovers to a human representative already recorded on an account, with the reason
    each was made and when. Ask by the handover reference number or by the customer reference number.

    Args:
        handoff_id: The handover reference number; leave "" if unknown.
        customer_id: The customer reference number of the account; leave "" if unknown.
    """
    match = {k: v for k, v in {"handoff_id": handoff_id, "customer_id": customer_id}.items() if v}
    rows = ctx.find("agent_handoffs", **match)
    return str(rows) if rows else f"No handovers recorded for {match}."


@tool(owner="agent", rw="write")
def verify_customer_identity(ctx: ToolContext, customer_id: str, account_number: str = "",
                             phone_number: str = "", email: str = "", tax_id_last4: str = "",
                             billing_address: str = "", account_opened_date: str = "") -> str:
    """Verify the caller against the account on file and record the outcome; nothing may be booked,
    changed, credited or invoiced on an account until this has passed.

    The comparison is made here rather than judged from the conversation: each detail the caller states
    is checked against the profile, and verification passes once at least two of them match. The
    customer reference number only fetches the profile and never counts as one of the matches. Callers
    usually offer only two or three details, so pass exactly what was said, word for word, and leave the
    rest blank. Where a first attempt falls short and a later one passes with another detail, the pass
    stands.

    Args:
        customer_id: The customer reference number, read from the account lookup. Always required; it retrieves the profile and is not counted as a match.
        account_number: The 6-digit account number the caller reads off an invoice or work order; leave "" if not stated.
        phone_number: The account phone number, 10 digits, as stated; leave "" if not stated.
        email: The billing email address on the account, as stated; leave "" if not stated.
        tax_id_last4: The last four digits of the company's federal tax identification number; leave "" if not stated.
        billing_address: The billing address on file, stated as one line; leave "" if not stated.
        account_opened_date: The day the account was opened with the company, as YYYY-MM-DD; leave "" if not stated.
    """
    if not customer_id:
        return "Error: customer_id is required; find the account first and pass its reference number."
    rows = ctx.find("customers", customer_id=customer_id)
    if not rows:
        return f"Error: no account {customer_id}; cannot verify."
    rec = rows[0]
    supplied = {"account_number": account_number, "phone_number": phone_number, "email": email,
                "tax_id_last4": tax_id_last4, "billing_address": billing_address,
                "account_opened_date": account_opened_date}
    matched = sum(1 for field, value in supplied.items()
                  if value and str(rec.get(field)) == str(value))
    verified = matched >= 2
    rid = ctx.make_id("ver_", customer_id)
    prior = ctx.find("identity_verifications", verification_id=rid)
    verified = verified or bool(prior and prior[0].get("verified"))
    if prior:
        ctx.update("identity_verifications", rid, verified=verified, verified_at=ctx.now())
    else:
        ctx.create("identity_verifications", rid, verification_id=rid, customer_id=customer_id,
                   verified=verified, verified_at=ctx.now())
    return (f"Identity verified for {customer_id} ({matched} detail(s) matched)." if verified
            else f"Identity NOT verified for {customer_id} (only {matched} of the 2 required details "
                 "matched). Ask the caller for another detail held on the account and try again.")


@tool(owner="agent", rw="write")
def transfer_to_human_representative(ctx: ToolContext, customer_id: str, reason: str) -> str:
    """Hand the call to a human client services representative and record the handover with its reason.

    There are two situations for this. The first is where the company's published terms offer no way to
    settle what the caller is asking for, so no correct answer can be given from the agreements,
    programs, plans, subscriptions or projects on file. The second is where the caller has asked to
    speak to a person twice on this call; at that point the request is honoured rather than deflected.

    Args:
        customer_id: The customer reference number, read from the account lookup; the account must exist.
        reason: One of POLICY_NOT_COVERED or CUSTOMER_REQUESTED, never free text.
            POLICY_NOT_COVERED — nothing in the company's terms decides this request;
            CUSTOMER_REQUESTED — the caller has asked for a person at least 2 times on this call.
    """
    allowed = {"POLICY_NOT_COVERED", "CUSTOMER_REQUESTED"}
    if reason not in allowed:
        return f"Error: unknown handover reason '{reason}'. Valid: {', '.join(sorted(allowed))}."
    if not ctx.find("customers", customer_id=customer_id):
        return f"Error: no account {customer_id}; cannot record the handover."
    rid = ctx.make_id("hof_", customer_id, reason)
    ctx.create("agent_handoffs", rid, handoff_id=rid, customer_id=customer_id,
               reason=reason, created_at=ctx.now())
    return f"Handover to a human representative recorded for {customer_id} ({reason})."

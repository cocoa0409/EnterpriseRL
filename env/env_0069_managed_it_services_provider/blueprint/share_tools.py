"""Shared tools for env_0069_managed_it_services_provider (Stratton Bay Technology Partners).

Share tools are always present in their owner's tool list. This module holds the complete
record-lookup layer (one finder per record set; the client-profile finder doubles as the identity
entry), the identity-verification write and the transfer-to-human handoff. Client-signed actions are
authored per difficulty as hidden user tools, never here.

Scenario operational constants (implemented below, never in the charters):
  K = 2  identity credentials that must match for verification to pass.
  R = 2  explicit requests for a human after which the handoff reason is CUSTOMER_REQUESTED.
"""

from erlbench import ToolContext, tool


# ---------------------------------------------------------------- client profile (identity entry)
@tool(owner="agent", rw="read")
def find_customers(ctx: ToolContext, customer_id: str = "", name: str = "", contact_name: str = "",
                   phone_number: str = "", email: str = "") -> str:
    """Look up a client organisation's profile to establish which client this conversation is about.

    Search by the client reference number, or by what a caller can naturally tell you: the
    organisation's legal business name, the authorized contact's full name, the contact's
    registered phone number or registered email address. Every criterion is optional; supply
    whichever you have. A match returns the profile with the client reference number, legal name,
    authorized contact, registered phone and email, billing state, declared compliance framework
    and the date the client relationship began. Finding a profile does not confirm that the caller
    is who they say they are; identity is confirmed separately.

    Args:
        customer_id: The client reference number, if already known; leave "" otherwise.
        name: The organisation's legal business name as the caller states it; leave "" if not given.
        contact_name: The authorized contact's full name as the caller states it; leave "" if not given.
        phone_number: The contact's registered phone number, 10 digits; leave "" if not given.
        email: The contact's registered email address; leave "" if not given.
    """
    match = {k: v for k, v in {"customer_id": customer_id, "name": name, "contact_name": contact_name,
                               "phone_number": phone_number, "email": email}.items() if v}
    if not match:
        return "Error: provide at least one reference number or profile detail to find the client."
    rows = ctx.fuzzy_find("customers", **match)
    if not rows:
        return f"No client profile matches {match}."
    if len(rows) > 1:
        return f"Error: {len(rows)} client profiles match {match}; ask for one more detail to tell them apart."
    return str(rows[0])


@tool(owner="agent", rw="read")
def find_identity_verifications(ctx: ToolContext, verification_id: str = "", customer_id: str = "") -> str:
    """Look up the recorded outcome of caller identity verification for a client.

    Shows whether a caller for the client has passed verification and when the latest attempt
    was made. Search by the verification reference or by the client reference number; both are
    optional.

    Args:
        verification_id: Reference of the verification outcome; leave "" if unknown.
        customer_id: Client reference number; leave "" if unknown.
    """
    match = {k: v for k, v in {"verification_id": verification_id, "customer_id": customer_id}.items() if v}
    rows = ctx.find("identity_verifications", **match)
    return str(rows) if rows else f"No verification outcome on record for {match}."


@tool(owner="agent", rw="read")
def find_human_handoffs(ctx: ToolContext, handoff_id: str = "", customer_id: str = "") -> str:
    """Look up handoffs of a client's conversations to a human representative.

    Each record shows the client, the reason recorded for the handoff and when it happened.
    Search by the handoff reference or the client reference number; both are optional.

    Args:
        handoff_id: Reference of the handoff; leave "" if unknown.
        customer_id: Client reference number; leave "" if unknown.
    """
    match = {k: v for k, v in {"handoff_id": handoff_id, "customer_id": customer_id}.items() if v}
    rows = ctx.find("human_handoffs", **match)
    return str(rows) if rows else f"No handoff on record for {match}."


# ---------------------------------------------------------------- ClearPath Managed IT Services
@tool(owner="agent", rw="read")
def find_managed_agreements(ctx: ToolContext, managed_agreement_id: str = "", customer_id: str = "") -> str:
    """Look up ClearPath managed services agreements.

    An agreement shows the ClearPath tier, its status, signing and go-live dates, the current term
    dates and length, the committed seats and the seats currently covered, the contracted per-seat
    rate, auto-renewal, renewal count, any notice on file with its effective date, suspension and
    reinstatement dates, and the balance owed. Search by agreement reference or client reference
    number; both are optional.

    Args:
        managed_agreement_id: Reference number of the agreement; leave "" if unknown.
        customer_id: Client reference number of the agreement holder; leave "" if unknown.
    """
    match = {k: v for k, v in {"managed_agreement_id": managed_agreement_id, "customer_id": customer_id}.items() if v}
    rows = ctx.find("managed_agreements", **match)
    return str(rows) if rows else f"No ClearPath agreement found for {match}."


@tool(owner="agent", rw="read")
def find_managed_seat_changes(ctx: ToolContext, managed_seat_change_id: str = "", managed_agreement_id: str = "",
                              customer_id: str = "") -> str:
    """Look up the seat history of a ClearPath agreement.

    Each entry is one addition or removal of covered users: how many seats, the effective date, the
    reason (go-live baseline, new-user onboarding, monthly true-up, user offboarding, true-up
    reduction), the named user's sign-in and the service desk ticket it was requested under. All
    criteria are optional.

    Args:
        managed_seat_change_id: Reference of one seat change; leave "" if unknown.
        managed_agreement_id: Reference number of the agreement; leave "" if unknown.
        customer_id: Client reference number; leave "" if unknown.
    """
    match = {k: v for k, v in {"managed_seat_change_id": managed_seat_change_id,
                               "managed_agreement_id": managed_agreement_id,
                               "customer_id": customer_id}.items() if v}
    rows = ctx.find("managed_seat_changes", **match)
    return str(rows) if rows else f"No seat changes found for {match}."


@tool(owner="agent", rw="read")
def find_managed_billing(ctx: ToolContext, managed_billing_entry_id: str = "", managed_agreement_id: str = "",
                         customer_id: str = "", managed_seat_change_id: str = "",
                         original_billing_entry_id: str = "") -> str:
    """Look up the billing ledger of a ClearPath agreement.

    Entries cover monthly seat fees, proration for added seats, onboarding fees, billable labor,
    service credits, payments, late fees, early termination and reinstatement fees and credit
    memos, each with its amount, invoice number, service month, posting date and, where relevant,
    the ticket, seat change, remittance reference or the charge a credit memo reverses. All
    criteria are optional.

    Args:
        managed_billing_entry_id: Reference of one ledger entry; leave "" if unknown.
        managed_agreement_id: Reference number of the agreement; leave "" if unknown.
        customer_id: Client reference number; leave "" if unknown.
        managed_seat_change_id: Reference of the seat change a proration charge bills; leave "" if unknown.
        original_billing_entry_id: Reference of a charge, to find the credit memo reversing it; leave "" if unknown.
    """
    match = {k: v for k, v in {"managed_billing_entry_id": managed_billing_entry_id,
                               "managed_agreement_id": managed_agreement_id, "customer_id": customer_id,
                               "managed_seat_change_id": managed_seat_change_id,
                               "original_billing_entry_id": original_billing_entry_id}.items() if v}
    rows = ctx.find("managed_billing", **match)
    return str(rows) if rows else f"No ClearPath billing entries found for {match}."


@tool(owner="agent", rw="read")
def find_managed_tickets(ctx: ToolContext, managed_ticket_event_id: str = "", managed_agreement_id: str = "",
                         customer_id: str = "") -> str:
    """Look up service desk ticket milestones logged under a ClearPath agreement.

    Each milestone (opened, reprioritised, first response, resolved) carries the ticket number,
    the time it happened, the priority in force, and on opening the issue category, reporting
    channel and scope determination; on resolution, how the labor is settled, the labor class and
    the billable minutes. All criteria are optional.

    Args:
        managed_ticket_event_id: Reference of one ticket milestone; leave "" if unknown.
        managed_agreement_id: Reference number of the agreement; leave "" if unknown.
        customer_id: Client reference number; leave "" if unknown.
    """
    match = {k: v for k, v in {"managed_ticket_event_id": managed_ticket_event_id,
                               "managed_agreement_id": managed_agreement_id,
                               "customer_id": customer_id}.items() if v}
    rows = ctx.find("managed_tickets", **match)
    return str(rows) if rows else f"No ticket milestones found for {match}."


@tool(owner="agent", rw="read")
def find_managed_service_requests(ctx: ToolContext, managed_request_id: str = "", customer_id: str = "",
                                  managed_agreement_id: str = "") -> str:
    """Look up contract change requests raised on ClearPath agreements.

    Shows notices of non-renewal or early termination, notice withdrawals, tier changes and
    cancellations before onboarding, with the target tier, the effective date carried, whether the
    client has signed, and when the request was registered. All criteria are optional.

    Args:
        managed_request_id: Reference of the request; leave "" if unknown.
        customer_id: Client reference number; leave "" if unknown.
        managed_agreement_id: Reference number of the agreement; leave "" if unknown.
    """
    match = {k: v for k, v in {"managed_request_id": managed_request_id, "customer_id": customer_id,
                               "managed_agreement_id": managed_agreement_id}.items() if v}
    rows = ctx.find("managed_service_requests", **match)
    return str(rows) if rows else f"No ClearPath change requests found for {match}."


# ---------------------------------------------------------------- Sentinel Managed Security
@tool(owner="agent", rw="read")
def find_security_subscriptions(ctx: ToolContext, security_subscription_id: str = "", customer_id: str = "") -> str:
    """Look up Sentinel managed security subscriptions.

    A subscription shows the Sentinel tier and status, order, deployment and activation dates,
    current term, endpoint commitment and endpoints enrolled, the contracted workstation and server
    rates, incident response hours remaining this contract year, any notice on file and the balance
    owed. Both criteria are optional.

    Args:
        security_subscription_id: Reference number of the subscription; leave "" if unknown.
        customer_id: Client reference number; leave "" if unknown.
    """
    match = {k: v for k, v in {"security_subscription_id": security_subscription_id,
                               "customer_id": customer_id}.items() if v}
    rows = ctx.find("security_subscriptions", **match)
    return str(rows) if rows else f"No Sentinel subscription found for {match}."


@tool(owner="agent", rw="read")
def find_security_endpoint_changes(ctx: ToolContext, security_endpoint_change_id: str = "",
                                   security_subscription_id: str = "", customer_id: str = "") -> str:
    """Look up endpoint enrollments and retirements on a Sentinel subscription.

    Each entry gives the number of workstations or servers enrolled or retired, the date the agent
    was installed or removed, and the reason. All criteria are optional.

    Args:
        security_endpoint_change_id: Reference of one enrollment change; leave "" if unknown.
        security_subscription_id: Reference number of the subscription; leave "" if unknown.
        customer_id: Client reference number; leave "" if unknown.
    """
    match = {k: v for k, v in {"security_endpoint_change_id": security_endpoint_change_id,
                               "security_subscription_id": security_subscription_id,
                               "customer_id": customer_id}.items() if v}
    rows = ctx.find("security_endpoint_changes", **match)
    return str(rows) if rows else f"No endpoint changes found for {match}."


@tool(owner="agent", rw="read")
def find_security_billing(ctx: ToolContext, security_billing_entry_id: str = "", security_subscription_id: str = "",
                          customer_id: str = "") -> str:
    """Look up the billing ledger of a Sentinel subscription.

    Entries cover monthly fees, onboarding fees, incident response overage, service credits,
    payments, late fees and early termination fees, with amount, invoice, month and any incident
    number, billed hours or remittance reference. All criteria are optional.

    Args:
        security_billing_entry_id: Reference of one ledger entry; leave "" if unknown.
        security_subscription_id: Reference number of the subscription; leave "" if unknown.
        customer_id: Client reference number; leave "" if unknown.
    """
    match = {k: v for k, v in {"security_billing_entry_id": security_billing_entry_id,
                               "security_subscription_id": security_subscription_id,
                               "customer_id": customer_id}.items() if v}
    rows = ctx.find("security_billing", **match)
    return str(rows) if rows else f"No Sentinel billing entries found for {match}."


@tool(owner="agent", rw="read")
def find_security_incidents(ctx: ToolContext, security_incident_event_id: str = "", security_subscription_id: str = "",
                            customer_id: str = "") -> str:
    """Look up security operations center incident milestones for a client.

    Each milestone (detected, acknowledged, closed) carries the incident number, severity and
    time, and on closure whether incident response was engaged and the hours logged. All criteria
    are optional.

    Args:
        security_incident_event_id: Reference of one incident milestone; leave "" if unknown.
        security_subscription_id: Reference number of the subscription; leave "" if unknown.
        customer_id: Client reference number; leave "" if unknown.
    """
    match = {k: v for k, v in {"security_incident_event_id": security_incident_event_id,
                               "security_subscription_id": security_subscription_id,
                               "customer_id": customer_id}.items() if v}
    rows = ctx.find("security_incidents", **match)
    return str(rows) if rows else f"No incident milestones found for {match}."


@tool(owner="agent", rw="read")
def find_security_ir_ledger(ctx: ToolContext, security_ir_entry_id: str = "", security_subscription_id: str = "",
                            customer_id: str = "") -> str:
    """Look up the incident response retainer hours ledger of a Sentinel subscription.

    Entries record hours granted for a contract year (annual allotment or rollover), hours consumed
    on an incident, and hours forfeited. All criteria are optional.

    Args:
        security_ir_entry_id: Reference of one hours entry; leave "" if unknown.
        security_subscription_id: Reference number of the subscription; leave "" if unknown.
        customer_id: Client reference number; leave "" if unknown.
    """
    match = {k: v for k, v in {"security_ir_entry_id": security_ir_entry_id,
                               "security_subscription_id": security_subscription_id,
                               "customer_id": customer_id}.items() if v}
    rows = ctx.find("security_ir_ledger", **match)
    return str(rows) if rows else f"No incident response hours entries found for {match}."


@tool(owner="agent", rw="read")
def find_security_change_requests(ctx: ToolContext, security_request_id: str = "", customer_id: str = "",
                                  security_subscription_id: str = "") -> str:
    """Look up change requests raised on Sentinel subscriptions.

    Shows notices, withdrawals, tier changes and order cancellations with the target tier,
    effective date, signature status and registration time. All criteria are optional.

    Args:
        security_request_id: Reference of the request; leave "" if unknown.
        customer_id: Client reference number; leave "" if unknown.
        security_subscription_id: Reference number of the subscription; leave "" if unknown.
    """
    match = {k: v for k, v in {"security_request_id": security_request_id, "customer_id": customer_id,
                               "security_subscription_id": security_subscription_id}.items() if v}
    rows = ctx.find("security_change_requests", **match)
    return str(rows) if rows else f"No Sentinel change requests found for {match}."


# ---------------------------------------------------------------- Continuum Backup & Recovery
@tool(owner="agent", rw="read")
def find_backup_plans(ctx: ToolContext, backup_plan_id: str = "", customer_id: str = "") -> str:
    """Look up Continuum backup and recovery plans.

    A plan shows the Continuum tier and status, order, seeding and activation dates, current term,
    server commitment, the contracted server, workstation and Microsoft 365 user rates, items
    protected, cloud failover server-days left this contract year, any notice on file and the
    balance owed. Both criteria are optional.

    Args:
        backup_plan_id: Reference number of the plan; leave "" if unknown.
        customer_id: Client reference number; leave "" if unknown.
    """
    match = {k: v for k, v in {"backup_plan_id": backup_plan_id, "customer_id": customer_id}.items() if v}
    rows = ctx.find("backup_plans", **match)
    return str(rows) if rows else f"No Continuum plan found for {match}."


@tool(owner="agent", rw="read")
def find_backup_device_changes(ctx: ToolContext, backup_device_change_id: str = "", backup_plan_id: str = "",
                               customer_id: str = "") -> str:
    """Look up which servers, workstations and Microsoft 365 users were added to or removed from backup protection.

    Each entry gives the item's class, hostname or user sign-in, and the date protection started or
    stopped. All criteria are optional.

    Args:
        backup_device_change_id: Reference of one protection change; leave "" if unknown.
        backup_plan_id: Reference number of the plan; leave "" if unknown.
        customer_id: Client reference number; leave "" if unknown.
    """
    match = {k: v for k, v in {"backup_device_change_id": backup_device_change_id,
                               "backup_plan_id": backup_plan_id, "customer_id": customer_id}.items() if v}
    rows = ctx.find("backup_device_changes", **match)
    return str(rows) if rows else f"No protection changes found for {match}."


@tool(owner="agent", rw="read")
def find_backup_billing(ctx: ToolContext, backup_billing_entry_id: str = "", backup_plan_id: str = "",
                        customer_id: str = "") -> str:
    """Look up the billing ledger of a Continuum plan.

    Entries cover monthly fees with any storage overage, onboarding fees, restore labor, failover
    overage, payments, late fees and early termination fees, with amount, invoice, month and any
    recovery job or remittance reference. All criteria are optional.

    Args:
        backup_billing_entry_id: Reference of one ledger entry; leave "" if unknown.
        backup_plan_id: Reference number of the plan; leave "" if unknown.
        customer_id: Client reference number; leave "" if unknown.
    """
    match = {k: v for k, v in {"backup_billing_entry_id": backup_billing_entry_id,
                               "backup_plan_id": backup_plan_id, "customer_id": customer_id}.items() if v}
    rows = ctx.find("backup_billing", **match)
    return str(rows) if rows else f"No Continuum billing entries found for {match}."


@tool(owner="agent", rw="read")
def find_backup_recovery_events(ctx: ToolContext, backup_recovery_event_id: str = "", backup_plan_id: str = "",
                                customer_id: str = "") -> str:
    """Look up restore jobs and cloud failovers run under a Continuum plan.

    Each milestone (restore requested or completed, failover declared or ended) carries the job
    reference, the kind of recovery, the time, technician minutes on completed restores and
    server-days on ended failovers. All criteria are optional.

    Args:
        backup_recovery_event_id: Reference of one recovery milestone; leave "" if unknown.
        backup_plan_id: Reference number of the plan; leave "" if unknown.
        customer_id: Client reference number; leave "" if unknown.
    """
    match = {k: v for k, v in {"backup_recovery_event_id": backup_recovery_event_id,
                               "backup_plan_id": backup_plan_id, "customer_id": customer_id}.items() if v}
    rows = ctx.find("backup_recovery_events", **match)
    return str(rows) if rows else f"No recovery milestones found for {match}."


@tool(owner="agent", rw="read")
def find_backup_dr_ledger(ctx: ToolContext, backup_dr_entry_id: str = "", backup_plan_id: str = "",
                          customer_id: str = "") -> str:
    """Look up the cloud failover server-day allowance ledger of a Continuum plan.

    Entries record server-days granted for a contract year, used by a production failover, or
    forfeited. All criteria are optional.

    Args:
        backup_dr_entry_id: Reference of one allowance entry; leave "" if unknown.
        backup_plan_id: Reference number of the plan; leave "" if unknown.
        customer_id: Client reference number; leave "" if unknown.
    """
    match = {k: v for k, v in {"backup_dr_entry_id": backup_dr_entry_id, "backup_plan_id": backup_plan_id,
                               "customer_id": customer_id}.items() if v}
    rows = ctx.find("backup_dr_ledger", **match)
    return str(rows) if rows else f"No failover allowance entries found for {match}."


@tool(owner="agent", rw="read")
def find_backup_change_requests(ctx: ToolContext, backup_request_id: str = "", customer_id: str = "",
                                backup_plan_id: str = "") -> str:
    """Look up change requests raised on Continuum plans.

    Shows notices, withdrawals, tier changes, order cancellations and production failover
    authorizations with target tier, effective date, signature status and registration time. All
    criteria are optional.

    Args:
        backup_request_id: Reference of the request; leave "" if unknown.
        customer_id: Client reference number; leave "" if unknown.
        backup_plan_id: Reference number of the plan; leave "" if unknown.
    """
    match = {k: v for k, v in {"backup_request_id": backup_request_id, "customer_id": customer_id,
                               "backup_plan_id": backup_plan_id}.items() if v}
    rows = ctx.find("backup_change_requests", **match)
    return str(rows) if rows else f"No Continuum change requests found for {match}."


# ---------------------------------------------------------------- Microsoft 365 Cloud Subscriptions (CSP)
@tool(owner="agent", rw="read")
def find_licensing_subscriptions(ctx: ToolContext, licensing_subscription_id: str = "", customer_id: str = "") -> str:
    """Look up the Microsoft 365 subscriptions Stratton Bay resells to a client.

    A subscription shows the Microsoft 365 plan, status, tenant domain, commitment term and billing
    frequency, purchase moment and when its current cancellation window opened, term dates, licenses
    committed, the locked price per license, auto-renew and any scheduled renewal quantity or term,
    renewal count, suspension and upgrade dates and the balance owed. Both criteria are optional.

    Args:
        licensing_subscription_id: Reference number of the subscription; leave "" if unknown.
        customer_id: Client reference number; leave "" if unknown.
    """
    match = {k: v for k, v in {"licensing_subscription_id": licensing_subscription_id,
                               "customer_id": customer_id}.items() if v}
    rows = ctx.find("licensing_subscriptions", **match)
    return str(rows) if rows else f"No Microsoft 365 subscription found for {match}."


@tool(owner="agent", rw="read")
def find_licensing_license_changes(ctx: ToolContext, licensing_license_change_id: str = "",
                                   licensing_subscription_id: str = "", customer_id: str = "",
                                   source_change_id: str = "") -> str:
    """Look up license quantity changes on a Microsoft 365 subscription.

    Each entry gives the number of licenses added or removed, the moment the change was submitted,
    the reason (initial purchase, seat addition, renewal increase, in-window reduction,
    cancellation, renewal reduction, expiry) and, for a reduction of added licenses, the seat
    addition it reduces. All criteria are optional.

    Args:
        licensing_license_change_id: Reference of one quantity change; leave "" if unknown.
        licensing_subscription_id: Reference number of the subscription; leave "" if unknown.
        customer_id: Client reference number; leave "" if unknown.
        source_change_id: Reference of a seat addition, to find reductions made against it; leave "" if unknown.
    """
    match = {k: v for k, v in {"licensing_license_change_id": licensing_license_change_id,
                               "licensing_subscription_id": licensing_subscription_id,
                               "customer_id": customer_id, "source_change_id": source_change_id}.items() if v}
    rows = ctx.find("licensing_license_changes", **match)
    return str(rows) if rows else f"No license changes found for {match}."


@tool(owner="agent", rw="read")
def find_licensing_billing(ctx: ToolContext, licensing_billing_entry_id: str = "", licensing_subscription_id: str = "",
                           customer_id: str = "", licensing_license_change_id: str = "") -> str:
    """Look up the billing ledger of a Microsoft 365 subscription.

    Entries cover billing-cycle charges, prorated charges for added licenses or upgrades, refunds
    for in-window reductions and cancellations, license administration fees, payments and late
    fees, with amount, invoice, cycle or month, posting date and the related license change or
    remittance reference. All criteria are optional.

    Args:
        licensing_billing_entry_id: Reference of one ledger entry; leave "" if unknown.
        licensing_subscription_id: Reference number of the subscription; leave "" if unknown.
        customer_id: Client reference number; leave "" if unknown.
        licensing_license_change_id: Reference of the license change a charge or refund relates to; leave "" if unknown.
    """
    match = {k: v for k, v in {"licensing_billing_entry_id": licensing_billing_entry_id,
                               "licensing_subscription_id": licensing_subscription_id,
                               "customer_id": customer_id,
                               "licensing_license_change_id": licensing_license_change_id}.items() if v}
    rows = ctx.find("licensing_billing", **match)
    return str(rows) if rows else f"No Microsoft 365 billing entries found for {match}."


@tool(owner="agent", rw="read")
def find_licensing_change_requests(ctx: ToolContext, licensing_request_id: str = "", customer_id: str = "",
                                   licensing_subscription_id: str = "") -> str:
    """Look up Microsoft 365 order forms awaiting or bearing the client's signature.

    Shows new subscription orders, cancellations, renewal changes and upgrades with the plan, term,
    billing frequency, quantity and auto-renew setting asked for, the signature status and when the
    request was registered. All criteria are optional.

    Args:
        licensing_request_id: Reference of the order form request; leave "" if unknown.
        customer_id: Client reference number; leave "" if unknown.
        licensing_subscription_id: Reference number of the subscription concerned; leave "" if unknown.
    """
    match = {k: v for k, v in {"licensing_request_id": licensing_request_id, "customer_id": customer_id,
                               "licensing_subscription_id": licensing_subscription_id}.items() if v}
    rows = ctx.find("licensing_change_requests", **match)
    return str(rows) if rows else f"No Microsoft 365 order forms found for {match}."


# ---------------------------------------------------------------- TimeBank Prepaid Service Hours
@tool(owner="agent", rw="read")
def find_timebank_blocks(ctx: ToolContext, timebank_block_id: str = "", customer_id: str = "",
                         rollover_source_block_id: str = "") -> str:
    """Look up a client's TimeBank prepaid hour blocks.

    A block shows its size and status, order, activation and expiry dates, hours purchased and
    remaining, price, balance owed, auto-replenish setting, extensions used, the earlier block whose
    hours rolled into it, and when it was last depleted. All criteria are optional.

    Args:
        timebank_block_id: Reference number of the block; leave "" if unknown.
        customer_id: Client reference number; leave "" if unknown.
        rollover_source_block_id: Reference of an earlier block, to find the block its hours rolled into; leave "" if unknown.
    """
    match = {k: v for k, v in {"timebank_block_id": timebank_block_id, "customer_id": customer_id,
                               "rollover_source_block_id": rollover_source_block_id}.items() if v}
    rows = ctx.find("timebank_blocks", **match)
    return str(rows) if rows else f"No TimeBank block found for {match}."


@tool(owner="agent", rw="read")
def find_timebank_hours_ledger(ctx: ToolContext, timebank_ledger_entry_id: str = "", timebank_block_id: str = "",
                               customer_id: str = "", original_ledger_entry_id: str = "",
                               counterpart_block_id: str = "") -> str:
    """Look up the hours ledger of TimeBank blocks.

    Entries record hours granted, drawn, reversed, rolled out or in, and forfeited; a draw shows the
    work date, kind of work, time band, who did it, minutes worked, the block hours charged and the
    ticket or statement of work it was done under. All criteria are optional.

    Args:
        timebank_ledger_entry_id: Reference of one hours entry; leave "" if unknown.
        timebank_block_id: Reference number of the block; leave "" if unknown.
        customer_id: Client reference number; leave "" if unknown.
        original_ledger_entry_id: Reference of a draw, to find the reversal made against it; leave "" if unknown.
        counterpart_block_id: Reference of the other block in a rollover; leave "" if unknown.
    """
    match = {k: v for k, v in {"timebank_ledger_entry_id": timebank_ledger_entry_id,
                               "timebank_block_id": timebank_block_id, "customer_id": customer_id,
                               "original_ledger_entry_id": original_ledger_entry_id,
                               "counterpart_block_id": counterpart_block_id}.items() if v}
    rows = ctx.find("timebank_hours_ledger", **match)
    return str(rows) if rows else f"No TimeBank hours entries found for {match}."


@tool(owner="agent", rw="read")
def find_timebank_billing(ctx: ToolContext, timebank_billing_entry_id: str = "", timebank_block_id: str = "",
                          customer_id: str = "") -> str:
    """Look up the billing ledger of TimeBank blocks.

    Entries cover block invoices, overage charges, extension fees, payments, late fees and order
    credits, with amount, invoice, posting date, month, overage hours and the ticket, statement of
    work or remittance reference. All criteria are optional.

    Args:
        timebank_billing_entry_id: Reference of one ledger entry; leave "" if unknown.
        timebank_block_id: Reference number of the block; leave "" if unknown.
        customer_id: Client reference number; leave "" if unknown.
    """
    match = {k: v for k, v in {"timebank_billing_entry_id": timebank_billing_entry_id,
                               "timebank_block_id": timebank_block_id, "customer_id": customer_id}.items() if v}
    rows = ctx.find("timebank_billing", **match)
    return str(rows) if rows else f"No TimeBank billing entries found for {match}."


@tool(owner="agent", rw="read")
def find_timebank_orders(ctx: ToolContext, timebank_order_id: str = "", customer_id: str = "",
                         timebank_block_id: str = "") -> str:
    """Look up TimeBank order forms and requests awaiting or bearing the client's signature.

    Shows new block orders (with or without rollover), extensions, order cancellations and
    auto-replenish changes with the block size, quoted amount, signature status and registration
    time. All criteria are optional.

    Args:
        timebank_order_id: Reference of the order form request; leave "" if unknown.
        customer_id: Client reference number; leave "" if unknown.
        timebank_block_id: Reference number of the existing block concerned; leave "" if unknown.
    """
    match = {k: v for k, v in {"timebank_order_id": timebank_order_id, "customer_id": customer_id,
                               "timebank_block_id": timebank_block_id}.items() if v}
    rows = ctx.find("timebank_orders", **match)
    return str(rows) if rows else f"No TimeBank order forms found for {match}."


# ---------------------------------------------------------------- Professional Services Projects
@tool(owner="agent", rw="read")
def find_project_engagements(ctx: ToolContext, project_engagement_id: str = "", customer_id: str = "") -> str:
    """Look up professional services engagements delivered under statements of work.

    An engagement shows its class, status, statement of work number and title, pricing model,
    original and current contract value, locked rate discount, issue, signature, scheduled start,
    kickoff and target completion dates, hold details, acceptance requests, rejections and basis,
    completion and warranty dates, change order count, cancellation and the balance owed. Both
    criteria are optional.

    Args:
        project_engagement_id: Reference number of the engagement; leave "" if unknown.
        customer_id: Client reference number; leave "" if unknown.
    """
    match = {k: v for k, v in {"project_engagement_id": project_engagement_id,
                               "customer_id": customer_id}.items() if v}
    rows = ctx.find("project_engagements", **match)
    return str(rows) if rows else f"No project engagement found for {match}."


@tool(owner="agent", rw="read")
def find_project_billing(ctx: ToolContext, project_billing_entry_id: str = "", project_engagement_id: str = "",
                         customer_id: str = "", original_billing_entry_id: str = "",
                         source_engagement_id: str = "") -> str:
    """Look up the billing ledger of a project engagement.

    Entries cover deposits, milestone, time-and-materials and final invoices, change order,
    reschedule, remobilization and cancellation fees, expenses, assessment credits, payments, late
    fees and credit memos, with amount, invoice, posting date, month and the milestone, change
    order, expense, remittance, reversed charge or credited assessment they relate to. All criteria
    are optional.

    Args:
        project_billing_entry_id: Reference of one ledger entry; leave "" if unknown.
        project_engagement_id: Reference number of the engagement; leave "" if unknown.
        customer_id: Client reference number; leave "" if unknown.
        original_billing_entry_id: Reference of a charge, to find the credit memo reversing it; leave "" if unknown.
        source_engagement_id: Reference of an assessment engagement, to find where its fee was credited; leave "" if unknown.
    """
    match = {k: v for k, v in {"project_billing_entry_id": project_billing_entry_id,
                               "project_engagement_id": project_engagement_id, "customer_id": customer_id,
                               "original_billing_entry_id": original_billing_entry_id,
                               "source_engagement_id": source_engagement_id}.items() if v}
    rows = ctx.find("project_billing", **match)
    return str(rows) if rows else f"No project billing entries found for {match}."


@tool(owner="agent", rw="read")
def find_project_milestones(ctx: ToolContext, project_milestone_event_id: str = "", project_engagement_id: str = "",
                            customer_id: str = "") -> str:
    """Look up milestones recorded complete on a project engagement.

    Each entry gives the milestone's position and name in the statement of work and the date it
    was completed. All criteria are optional.

    Args:
        project_milestone_event_id: Reference of one milestone completion; leave "" if unknown.
        project_engagement_id: Reference number of the engagement; leave "" if unknown.
        customer_id: Client reference number; leave "" if unknown.
    """
    match = {k: v for k, v in {"project_milestone_event_id": project_milestone_event_id,
                               "project_engagement_id": project_engagement_id,
                               "customer_id": customer_id}.items() if v}
    rows = ctx.find("project_milestones", **match)
    return str(rows) if rows else f"No milestone completions found for {match}."


@tool(owner="agent", rw="read")
def find_project_work_logs(ctx: ToolContext, project_work_log_id: str = "", project_engagement_id: str = "",
                           customer_id: str = "") -> str:
    """Look up time logged on a project engagement.

    Each entry gives the statement of work, work date, level of the person, business-hours or
    after-hours band, minutes logged and how the time is settled. All criteria are optional.

    Args:
        project_work_log_id: Reference of one time entry; leave "" if unknown.
        project_engagement_id: Reference number of the engagement; leave "" if unknown.
        customer_id: Client reference number; leave "" if unknown.
    """
    match = {k: v for k, v in {"project_work_log_id": project_work_log_id,
                               "project_engagement_id": project_engagement_id,
                               "customer_id": customer_id}.items() if v}
    rows = ctx.find("project_work_logs", **match)
    return str(rows) if rows else f"No project time entries found for {match}."


@tool(owner="agent", rw="read")
def find_project_change_orders(ctx: ToolContext, project_change_order_id: str = "", customer_id: str = "",
                               project_engagement_id: str = "") -> str:
    """Look up change orders and other client sign-offs raised on project engagements.

    Shows the change order number, kind (scope addition or reduction, schedule change, termination
    notice, acceptance sign-off or rejection), value change, new target date, signature status and
    registration time. All criteria are optional.

    Args:
        project_change_order_id: Reference of the change order request; leave "" if unknown.
        customer_id: Client reference number; leave "" if unknown.
        project_engagement_id: Reference number of the engagement; leave "" if unknown.
    """
    match = {k: v for k, v in {"project_change_order_id": project_change_order_id, "customer_id": customer_id,
                               "project_engagement_id": project_engagement_id}.items() if v}
    rows = ctx.find("project_change_orders", **match)
    return str(rows) if rows else f"No project change orders found for {match}."


# ---------------------------------------------------------------- Hardware Procurement
@tool(owner="agent", rw="read")
def find_hardware_orders(ctx: ToolContext, hardware_order_id: str = "", customer_id: str = "") -> str:
    """Look up hardware quotes and orders.

    An order shows its type and status, quote number, product description and part number,
    quantity, unit cost and sell price, quote total, rush and deposit flags, quote, approval,
    purchase order, ship and delivery dates, distributor purchase order and tracking numbers, any
    cancellation and the balance owed. Both criteria are optional.

    Args:
        hardware_order_id: Reference number of the order; leave "" if unknown.
        customer_id: Client reference number; leave "" if unknown.
    """
    match = {k: v for k, v in {"hardware_order_id": hardware_order_id, "customer_id": customer_id}.items() if v}
    rows = ctx.find("hardware_orders", **match)
    return str(rows) if rows else f"No hardware order found for {match}."


@tool(owner="agent", rw="read")
def find_hardware_billing(ctx: ToolContext, hardware_billing_entry_id: str = "", hardware_order_id: str = "",
                          customer_id: str = "") -> str:
    """Look up the billing ledger of a hardware order.

    Entries cover deposit and final invoices, cancellation and restocking fees, return and order
    credits, payments and late fees, with amount, invoice, posting date, month and any return
    authorization or remittance reference. All criteria are optional.

    Args:
        hardware_billing_entry_id: Reference of one ledger entry; leave "" if unknown.
        hardware_order_id: Reference number of the order; leave "" if unknown.
        customer_id: Client reference number; leave "" if unknown.
    """
    match = {k: v for k, v in {"hardware_billing_entry_id": hardware_billing_entry_id,
                               "hardware_order_id": hardware_order_id, "customer_id": customer_id}.items() if v}
    rows = ctx.find("hardware_billing", **match)
    return str(rows) if rows else f"No hardware billing entries found for {match}."


@tool(owner="agent", rw="read")
def find_hardware_returns(ctx: ToolContext, hardware_return_event_id: str = "", hardware_order_id: str = "",
                          customer_id: str = "") -> str:
    """Look up return authorizations, receipts and dead-on-arrival replacements for hardware orders.

    Each milestone carries the return authorization number, whether the units are unwanted or dead
    on arrival, the units concerned, the inspected condition on receipt and the date. All criteria
    are optional.

    Args:
        hardware_return_event_id: Reference of one return milestone; leave "" if unknown.
        hardware_order_id: Reference number of the order; leave "" if unknown.
        customer_id: Client reference number; leave "" if unknown.
    """
    match = {k: v for k, v in {"hardware_return_event_id": hardware_return_event_id,
                               "hardware_order_id": hardware_order_id, "customer_id": customer_id}.items() if v}
    rows = ctx.find("hardware_returns", **match)
    return str(rows) if rows else f"No return milestones found for {match}."


@tool(owner="agent", rw="read")
def find_hardware_client_requests(ctx: ToolContext, hardware_request_id: str = "", customer_id: str = "",
                                  hardware_order_id: str = "") -> str:
    """Look up hardware quote approvals, cancellations and return requests awaiting or bearing the client's signature.

    Shows the request type, return type, units concerned, signature status and registration time.
    All criteria are optional.

    Args:
        hardware_request_id: Reference of the request; leave "" if unknown.
        customer_id: Client reference number; leave "" if unknown.
        hardware_order_id: Reference number of the order concerned; leave "" if unknown.
    """
    match = {k: v for k, v in {"hardware_request_id": hardware_request_id, "customer_id": customer_id,
                               "hardware_order_id": hardware_order_id}.items() if v}
    rows = ctx.find("hardware_client_requests", **match)
    return str(rows) if rows else f"No hardware client requests found for {match}."


# ---------------------------------------------------------------- identity verification and handoff
@tool(owner="agent", rw="write")
def verify_customer_identity(ctx: ToolContext, customer_id: str, phone_number: str = "", email: str = "",
                             ein_last4: str = "", support_pin: str = "", client_since: str = "") -> str:
    """Verify that the caller is the client's authorized contact, and record the outcome.

    Verification must pass before any account details are discussed or any change, payment,
    credit or order is handled for the client. The comparison is made by this tool: each piece of
    identity information the caller states is checked against the client profile, and
    verification passes only when at least 2 of them match. The client reference number only
    retrieves the profile and never counts as a match, and the organisation or contact name is not
    an identity credential. Callers usually give only some of these details: pass exactly what the
    caller said for each item given and leave the rest empty. The outcome is recorded; if a first
    attempt fails and a later attempt with more details passes, the client stays verified.

    Args:
        customer_id: Client reference number read from the client profile lookup. Required; used only to retrieve the profile.
        phone_number: The authorized contact's registered phone number as stated, 10 digits; leave "" if not stated.
        email: The authorized contact's registered email address as stated; leave "" if not stated.
        ein_last4: Last four digits of the organisation's federal Employer Identification Number as stated; leave "" if not stated.
        support_pin: The client's six-digit verbal support PIN as stated; leave "" if not stated.
        client_since: The date the client relationship began as stated, YYYY-MM-DD; leave "" if not stated.
    """
    if not customer_id:
        return "Error: customer_id is required; look up the client profile first and pass its reference number."
    rows = ctx.find("customers", customer_id=customer_id)
    if not rows:
        return f"Error: no client profile {customer_id}; cannot verify."
    rec = rows[0]
    supplied = {"phone_number": phone_number, "email": email, "ein_last4": ein_last4,
                "support_pin": support_pin, "client_since": client_since}
    matched = sum(1 for field, value in supplied.items()
                  if value and str(rec.get(field) or "").strip().lower() == str(value).strip().lower())
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
            else f"Identity NOT verified for {customer_id} (only {matched} of the required 2 details matched). "
                 "Ask the caller for another detail on file and try again.")


@tool(owner="agent", rw="write")
def transfer_to_human_agent(ctx: ToolContext, customer_id: str, reason: str) -> str:
    """Hand the client over to a human representative and record the handoff with its reason.

    Use this when no Stratton Bay policy lets the request be resolved in this conversation, or when
    the caller has explicitly asked to speak with a person at least 2 times.

    Args:
        customer_id: Client reference number read from the client profile lookup (the profile must exist).
        reason: One of POLICY_NOT_COVERED or CUSTOMER_REQUESTED, never free text.
            POLICY_NOT_COVERED - no policy offers a way to resolve the request;
            CUSTOMER_REQUESTED - the caller has explicitly asked for a human representative at least 2 times.
    """
    allowed = {"POLICY_NOT_COVERED", "CUSTOMER_REQUESTED"}
    if reason not in allowed:
        return f"Error: unknown handoff reason '{reason}'. Valid: {', '.join(sorted(allowed))}."
    if not ctx.find("customers", customer_id=customer_id):
        return f"Error: no client profile {customer_id}; cannot record the handoff."
    rid = ctx.make_id("hof_", customer_id, reason)
    ctx.create("human_handoffs", rid, handoff_id=rid, customer_id=customer_id, reason=reason, created_at=ctx.now())
    return f"Handoff to a human representative recorded for {customer_id} ({reason})."

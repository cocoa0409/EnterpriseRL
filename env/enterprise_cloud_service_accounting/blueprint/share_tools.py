"""Shared customer, contract and accounting record services for Northbridge Cloud Services."""
from erlbench import ToolContext, tool


@tool(owner="agent", rw="write")
def verify_customer_identity(ctx: ToolContext, customer_id: str, phone: str = "", email: str = "", identity_document: str = "", opened_date: str = "") -> str:
    """Compare the caller's credentials with the enterprise profile and record verification.

    At least two supplied credentials must match exactly. The customer reference locates
    the profile and never counts as a credential. Supply only information the caller actually
    states, without rewriting it. A recorded successful verification is never downgraded by
    a later unsuccessful attempt. Identity verification must succeed before account business
    is transacted or money moved.

    Args:
        customer_id: Customer reference copied from the located enterprise profile; required.
        phone: Caller-stated registered E.164 telephone number, verbatim; leave "" if unstated.
        email: Caller-stated registered finance email address, verbatim; leave "" if unstated.
        identity_document: Caller-stated eight-digit registered identity-document suffix, verbatim; leave "" if unstated.
        opened_date: Caller-stated profile opening date in YYYY-MM-DD format, verbatim; leave "" if unstated.
    """
    profiles = ctx.find("customers", customer_id=customer_id)
    if not customer_id or not profiles:
        return "Error: a located customer profile is required."
    supplied = {"phone": phone, "email": email, "identity_document": identity_document, "opened_date": opened_date}
    matched = sum(1 for key, value in supplied.items() if value and str(profiles[0].get(key)) == value)
    reference = ctx.make_id("verification", customer_id)
    prior = ctx.find("verification_log", verification_id=reference)
    verified = matched >= 2 or bool(prior and prior[0].get("verified"))
    if prior:
        ctx.update("verification_log", reference, verified=verified, verified_at=ctx.now())
    else:
        ctx.create("verification_log", reference, verification_id=reference, customer_id=customer_id, verified=verified, verified_at=ctx.now())
    return "Identity verified." if verified else "Identity not verified; another matching registered credential is needed."


@tool(owner="agent", rw="write")
def transfer_to_human_agent(ctx: ToolContext, customer_id: str, reason: str) -> str:
    """Record a referral to a human enterprise support specialist.

    Refer requests for which published policy provides no resolution, or a customer who
    explicitly asks for a human representative at least twice. The reason must use the
    corresponding controlled value; no descriptive explanation is stored.

    Args:
        customer_id: Customer reference copied from the located enterprise profile; required.
        reason: Exactly POLICY_NOT_COVERED when policy cannot resolve the request, or CUSTOMER_REQUESTED when the customer has explicitly requested a human at least two times.
    """
    if reason not in {"POLICY_NOT_COVERED", "CUSTOMER_REQUESTED"}:
        return "Error: reason must be POLICY_NOT_COVERED or CUSTOMER_REQUESTED."
    if not ctx.find("customers", customer_id=customer_id):
        return "Error: a located customer profile is required."
    reference = ctx.make_id("handoff", customer_id, reason)
    ctx.create("handoff_log", reference, handoff_id=reference, customer_id=customer_id, reason=reason, created_at=ctx.now())
    return "Human-specialist referral recorded."

@tool(owner="agent", rw="read")
def find_customers(ctx: ToolContext, customer_id: str = "", company_name: str = "", contact_name: str = "", phone: str = "", email: str = "", identity_document: str = "", opened_date: str = "") -> str:
    """Locate the enterprise customer profile by a known reference or exact contact information. The profile contains its legal company, authorized contact and registered verification credentials. This lookup does not verify identity. Supply any known criteria; matching profiles are returned, and an empty list means no match.

    Args:
        customer_id: Reference of the enterprise customer profile. Copy the reference from a retrieved business record; leave "" if unknown.
        company_name: Legal company name copied exactly from the customer. Use the exact caller-stated string; leave "" if not supplied.
        contact_name: Authorized finance contact name copied exactly from the customer. Use the exact caller-stated string; leave "" if not supplied.
        phone: Registered authorized contact telephone number. E.164 telephone string; leave "" if not supplied.
        email: Registered finance contact email address copied exactly. Use the exact caller-stated string; leave "" if not supplied.
        identity_document: Registered authorized contact identity-document suffix. Eight decimal digits; leave "" if not supplied.
        opened_date: UTC date the customer profile was opened. YYYY-MM-DD; leave "" if not supplied.
    """
    match = {k: v for k, v in {'customer_id': customer_id, 'company_name': company_name, 'contact_name': contact_name, 'phone': phone, 'email': email, 'identity_document': identity_document, 'opened_date': opened_date}.items() if v}
    return str(ctx.find("customers", **match))

@tool(owner="agent", rw="read")
def find_verification_log(ctx: ToolContext, verification_id: str = "", customer_id: str = "") -> str:
    """View the recorded identity-verification outcome for an enterprise contact using a customer or verification reference. Optional criteria select matching outcomes; an empty list means no recorded verification.

    Args:
        verification_id: Reference of the customer verification outcome. Copy the reference from a retrieved business record; leave "" if unknown.
        customer_id: Customer whose credentials were compared. Copy the reference from a retrieved business record; leave "" if unknown.
    """
    match = {k: v for k, v in {'verification_id': verification_id, 'customer_id': customer_id}.items() if v}
    return str(ctx.find("verification_log", **match))

@tool(owner="agent", rw="read")
def find_handoff_log(ctx: ToolContext, handoff_id: str = "", customer_id: str = "") -> str:
    """Retrieve human-specialist referral records with their reason and creation time. Supply a customer or referral reference if known; an empty list means no matching referral.

    Args:
        handoff_id: Reference of the handoff. Copy the reference from a retrieved business record; leave "" if unknown.
        customer_id: Customer referred to a human specialist. Copy the reference from a retrieved business record; leave "" if unknown.
    """
    match = {k: v for k, v in {'handoff_id': handoff_id, 'customer_id': customer_id}.items() if v}
    return str(ctx.find("handoff_log", **match))

@tool(owner="agent", rw="read")
def find_compute_holdings(ctx: ToolContext, compute_holding_id: str = "", customer_id: str = "", request_id: str = "") -> str:
    """View the customer's Virtual Compute contracts, including the official tier, lifecycle state, approved commercial terms and billing entity. Any known contract or customer reference can select the matching records; omitted criteria impose no restriction and an empty list means no match.

    Args:
        compute_holding_id: Reference of the Virtual Compute contract. Copy the reference from a retrieved business record; leave "" if unknown.
        customer_id: Enterprise customer that owns this contract. Copy the reference from a retrieved business record; leave "" if unknown.
        request_id: Reference of the customer authorization recorded on this contract; copy from a retrieved record, or leave "" if unknown.
    """
    match = {k: v for k, v in {'compute_holding_id': compute_holding_id, 'customer_id': customer_id, 'request_id': request_id}.items() if v}
    return str(ctx.find("compute_holdings", **match))

@tool(owner="agent", rw="read")
def find_compute_events(ctx: ToolContext, compute_event_id: str = "", compute_holding_id: str = "", customer_id: str = "", source_event_id: str = "", request_id: str = "", related_event_id: str = "") -> str:
    """Retrieve Virtual Compute consumption, invoice, adjustment, remittance and service evidence. Search by the contract or customer, an event reference, its original source, a customer request or related evidence. All criteria are optional; results preserve the recorded business details and an empty list means no match.

    Args:
        compute_event_id: Reference identifying this accounting or service event. Copy the reference from a retrieved business record; leave "" if unknown.
        compute_holding_id: Contract to which this event belongs. Copy the reference from a retrieved business record; leave "" if unknown.
        customer_id: Customer owning the event and the referenced contract. Copy the reference from a retrieved business record; leave "" if unknown.
        source_event_id: Narrowest original event corrected, billed, credited, paid or refunded; empty for an independent source. Copy the reference from a retrieved business record; leave "" if unknown.
        request_id: Customer request event reference; empty where no customer request is needed. Copy the reference from a retrieved business record; leave "" if unknown.
        related_event_id: Additional linked approval, incident or evidence event; empty when absent. Copy the reference from a retrieved business record; leave "" if unknown.
    """
    match = {k: v for k, v in {'compute_event_id': compute_event_id, 'compute_holding_id': compute_holding_id, 'customer_id': customer_id, 'source_event_id': source_event_id, 'request_id': request_id, 'related_event_id': related_event_id}.items() if v}
    return str(ctx.find("compute_events", **match))

@tool(owner="agent", rw="read")
def find_storage_holdings(ctx: ToolContext, storage_holding_id: str = "", customer_id: str = "", request_id: str = "") -> str:
    """View the customer's Object Storage contracts, including the official tier, lifecycle state, approved commercial terms and billing entity. Any known contract or customer reference can select the matching records; omitted criteria impose no restriction and an empty list means no match.

    Args:
        storage_holding_id: Reference of the Object Storage contract. Copy the reference from a retrieved business record; leave "" if unknown.
        customer_id: Enterprise customer that owns this contract. Copy the reference from a retrieved business record; leave "" if unknown.
        request_id: Reference of the customer authorization recorded on this contract; copy from a retrieved record, or leave "" if unknown.
    """
    match = {k: v for k, v in {'storage_holding_id': storage_holding_id, 'customer_id': customer_id, 'request_id': request_id}.items() if v}
    return str(ctx.find("storage_holdings", **match))

@tool(owner="agent", rw="read")
def find_storage_events(ctx: ToolContext, storage_event_id: str = "", storage_holding_id: str = "", customer_id: str = "", source_event_id: str = "", request_id: str = "", related_event_id: str = "") -> str:
    """Retrieve Object Storage consumption, invoice, adjustment, remittance and service evidence. Search by the contract or customer, an event reference, its original source, a customer request or related evidence. All criteria are optional; results preserve the recorded business details and an empty list means no match.

    Args:
        storage_event_id: Reference identifying this accounting or service event. Copy the reference from a retrieved business record; leave "" if unknown.
        storage_holding_id: Contract to which this event belongs. Copy the reference from a retrieved business record; leave "" if unknown.
        customer_id: Customer owning the event and the referenced contract. Copy the reference from a retrieved business record; leave "" if unknown.
        source_event_id: Narrowest original event corrected, billed, credited, paid or refunded; empty for an independent source. Copy the reference from a retrieved business record; leave "" if unknown.
        request_id: Customer request event reference; empty where no customer request is needed. Copy the reference from a retrieved business record; leave "" if unknown.
        related_event_id: Additional linked approval, incident or evidence event; empty when absent. Copy the reference from a retrieved business record; leave "" if unknown.
    """
    match = {k: v for k, v in {'storage_event_id': storage_event_id, 'storage_holding_id': storage_holding_id, 'customer_id': customer_id, 'source_event_id': source_event_id, 'request_id': request_id, 'related_event_id': related_event_id}.items() if v}
    return str(ctx.find("storage_events", **match))

@tool(owner="agent", rw="read")
def find_database_holdings(ctx: ToolContext, database_holding_id: str = "", customer_id: str = "", request_id: str = "") -> str:
    """View the customer's Managed Database contracts, including the official tier, lifecycle state, approved commercial terms and billing entity. Any known contract or customer reference can select the matching records; omitted criteria impose no restriction and an empty list means no match.

    Args:
        database_holding_id: Reference of the Managed Database contract. Copy the reference from a retrieved business record; leave "" if unknown.
        customer_id: Enterprise customer that owns this contract. Copy the reference from a retrieved business record; leave "" if unknown.
        request_id: Reference of the customer authorization recorded on this contract; copy from a retrieved record, or leave "" if unknown.
    """
    match = {k: v for k, v in {'database_holding_id': database_holding_id, 'customer_id': customer_id, 'request_id': request_id}.items() if v}
    return str(ctx.find("database_holdings", **match))

@tool(owner="agent", rw="read")
def find_database_events(ctx: ToolContext, database_event_id: str = "", database_holding_id: str = "", customer_id: str = "", source_event_id: str = "", request_id: str = "", related_event_id: str = "") -> str:
    """Retrieve Managed Database consumption, invoice, adjustment, remittance and service evidence. Search by the contract or customer, an event reference, its original source, a customer request or related evidence. All criteria are optional; results preserve the recorded business details and an empty list means no match.

    Args:
        database_event_id: Reference identifying this accounting or service event. Copy the reference from a retrieved business record; leave "" if unknown.
        database_holding_id: Contract to which this event belongs. Copy the reference from a retrieved business record; leave "" if unknown.
        customer_id: Customer owning the event and the referenced contract. Copy the reference from a retrieved business record; leave "" if unknown.
        source_event_id: Narrowest original event corrected, billed, credited, paid or refunded; empty for an independent source. Copy the reference from a retrieved business record; leave "" if unknown.
        request_id: Customer request event reference; empty where no customer request is needed. Copy the reference from a retrieved business record; leave "" if unknown.
        related_event_id: Additional linked approval, incident or evidence event; empty when absent. Copy the reference from a retrieved business record; leave "" if unknown.
    """
    match = {k: v for k, v in {'database_event_id': database_event_id, 'database_holding_id': database_holding_id, 'customer_id': customer_id, 'source_event_id': source_event_id, 'request_id': request_id, 'related_event_id': related_event_id}.items() if v}
    return str(ctx.find("database_events", **match))

@tool(owner="agent", rw="read")
def find_network_holdings(ctx: ToolContext, network_holding_id: str = "", customer_id: str = "", request_id: str = "") -> str:
    """View the customer's Enterprise Connectivity contracts, including the official tier, lifecycle state, approved commercial terms and billing entity. Any known contract or customer reference can select the matching records; omitted criteria impose no restriction and an empty list means no match.

    Args:
        network_holding_id: Reference of the Enterprise Connectivity contract. Copy the reference from a retrieved business record; leave "" if unknown.
        customer_id: Enterprise customer that owns this contract. Copy the reference from a retrieved business record; leave "" if unknown.
        request_id: Reference of the customer authorization recorded on this contract; copy from a retrieved record, or leave "" if unknown.
    """
    match = {k: v for k, v in {'network_holding_id': network_holding_id, 'customer_id': customer_id, 'request_id': request_id}.items() if v}
    return str(ctx.find("network_holdings", **match))

@tool(owner="agent", rw="read")
def find_network_events(ctx: ToolContext, network_event_id: str = "", network_holding_id: str = "", customer_id: str = "", source_event_id: str = "", request_id: str = "", related_event_id: str = "") -> str:
    """Retrieve Enterprise Connectivity consumption, invoice, adjustment, remittance and service evidence. Search by the contract or customer, an event reference, its original source, a customer request or related evidence. All criteria are optional; results preserve the recorded business details and an empty list means no match.

    Args:
        network_event_id: Reference identifying this accounting or service event. Copy the reference from a retrieved business record; leave "" if unknown.
        network_holding_id: Contract to which this event belongs. Copy the reference from a retrieved business record; leave "" if unknown.
        customer_id: Customer owning the event and the referenced contract. Copy the reference from a retrieved business record; leave "" if unknown.
        source_event_id: Narrowest original event corrected, billed, credited, paid or refunded; empty for an independent source. Copy the reference from a retrieved business record; leave "" if unknown.
        request_id: Customer request event reference; empty where no customer request is needed. Copy the reference from a retrieved business record; leave "" if unknown.
        related_event_id: Additional linked approval, incident or evidence event; empty when absent. Copy the reference from a retrieved business record; leave "" if unknown.
    """
    match = {k: v for k, v in {'network_event_id': network_event_id, 'network_holding_id': network_holding_id, 'customer_id': customer_id, 'source_event_id': source_event_id, 'request_id': request_id, 'related_event_id': related_event_id}.items() if v}
    return str(ctx.find("network_events", **match))

@tool(owner="agent", rw="read")
def find_support_holdings(ctx: ToolContext, support_holding_id: str = "", customer_id: str = "", request_id: str = "") -> str:
    """View the customer's Enterprise Support contracts, including the official tier, lifecycle state, approved commercial terms and billing entity. Any known contract or customer reference can select the matching records; omitted criteria impose no restriction and an empty list means no match.

    Args:
        support_holding_id: Reference of the Enterprise Support contract. Copy the reference from a retrieved business record; leave "" if unknown.
        customer_id: Enterprise customer that owns this contract. Copy the reference from a retrieved business record; leave "" if unknown.
        request_id: Reference of the customer authorization recorded on this contract; copy from a retrieved record, or leave "" if unknown.
    """
    match = {k: v for k, v in {'support_holding_id': support_holding_id, 'customer_id': customer_id, 'request_id': request_id}.items() if v}
    return str(ctx.find("support_holdings", **match))

@tool(owner="agent", rw="read")
def find_support_events(ctx: ToolContext, support_event_id: str = "", support_holding_id: str = "", customer_id: str = "", source_event_id: str = "", request_id: str = "", related_event_id: str = "") -> str:
    """Retrieve Enterprise Support consumption, invoice, adjustment, remittance and service evidence. Search by the contract or customer, an event reference, its original source, a customer request or related evidence. All criteria are optional; results preserve the recorded business details and an empty list means no match.

    Args:
        support_event_id: Reference identifying this accounting or service event. Copy the reference from a retrieved business record; leave "" if unknown.
        support_holding_id: Contract to which this event belongs. Copy the reference from a retrieved business record; leave "" if unknown.
        customer_id: Customer owning the event and the referenced contract. Copy the reference from a retrieved business record; leave "" if unknown.
        source_event_id: Narrowest original event corrected, billed, credited, paid or refunded; empty for an independent source. Copy the reference from a retrieved business record; leave "" if unknown.
        request_id: Customer request event reference; empty where no customer request is needed. Copy the reference from a retrieved business record; leave "" if unknown.
        related_event_id: Additional linked approval, incident or evidence event; empty when absent. Copy the reference from a retrieved business record; leave "" if unknown.
    """
    match = {k: v for k, v in {'support_event_id': support_event_id, 'support_holding_id': support_holding_id, 'customer_id': customer_id, 'source_event_id': source_event_id, 'request_id': request_id, 'related_event_id': related_event_id}.items() if v}
    return str(ctx.find("support_events", **match))

@tool(owner="agent", rw="read")
def find_backup_holdings(ctx: ToolContext, backup_holding_id: str = "", customer_id: str = "", request_id: str = "") -> str:
    """View the customer's Managed Backup contracts, including the official tier, lifecycle state, approved commercial terms and billing entity. Any known contract or customer reference can select the matching records; omitted criteria impose no restriction and an empty list means no match.

    Args:
        backup_holding_id: Reference of the Managed Backup contract. Copy the reference from a retrieved business record; leave "" if unknown.
        customer_id: Enterprise customer that owns this contract. Copy the reference from a retrieved business record; leave "" if unknown.
        request_id: Reference of the customer authorization recorded on this contract; copy from a retrieved record, or leave "" if unknown.
    """
    match = {k: v for k, v in {'backup_holding_id': backup_holding_id, 'customer_id': customer_id, 'request_id': request_id}.items() if v}
    return str(ctx.find("backup_holdings", **match))

@tool(owner="agent", rw="read")
def find_backup_events(ctx: ToolContext, backup_event_id: str = "", backup_holding_id: str = "", customer_id: str = "", source_event_id: str = "", request_id: str = "", related_event_id: str = "") -> str:
    """Retrieve Managed Backup consumption, invoice, adjustment, remittance and service evidence. Search by the contract or customer, an event reference, its original source, a customer request or related evidence. All criteria are optional; results preserve the recorded business details and an empty list means no match.

    Args:
        backup_event_id: Reference identifying this accounting or service event. Copy the reference from a retrieved business record; leave "" if unknown.
        backup_holding_id: Contract to which this event belongs. Copy the reference from a retrieved business record; leave "" if unknown.
        customer_id: Customer owning the event and the referenced contract. Copy the reference from a retrieved business record; leave "" if unknown.
        source_event_id: Narrowest original event corrected, billed, credited, paid or refunded; empty for an independent source. Copy the reference from a retrieved business record; leave "" if unknown.
        request_id: Customer request event reference; empty where no customer request is needed. Copy the reference from a retrieved business record; leave "" if unknown.
        related_event_id: Additional linked approval, incident or evidence event; empty when absent. Copy the reference from a retrieved business record; leave "" if unknown.
    """
    match = {k: v for k, v in {'backup_event_id': backup_event_id, 'backup_holding_id': backup_holding_id, 'customer_id': customer_id, 'source_event_id': source_event_id, 'request_id': request_id, 'related_event_id': related_event_id}.items() if v}
    return str(ctx.find("backup_events", **match))

@tool(owner="agent", rw="read")
def find_security_holdings(ctx: ToolContext, security_holding_id: str = "", customer_id: str = "", request_id: str = "") -> str:
    """View the customer's Cloud Security contracts, including the official tier, lifecycle state, approved commercial terms and billing entity. Any known contract or customer reference can select the matching records; omitted criteria impose no restriction and an empty list means no match.

    Args:
        security_holding_id: Reference of the Cloud Security contract. Copy the reference from a retrieved business record; leave "" if unknown.
        customer_id: Enterprise customer that owns this contract. Copy the reference from a retrieved business record; leave "" if unknown.
        request_id: Reference of the customer authorization recorded on this contract; copy from a retrieved record, or leave "" if unknown.
    """
    match = {k: v for k, v in {'security_holding_id': security_holding_id, 'customer_id': customer_id, 'request_id': request_id}.items() if v}
    return str(ctx.find("security_holdings", **match))

@tool(owner="agent", rw="read")
def find_security_events(ctx: ToolContext, security_event_id: str = "", security_holding_id: str = "", customer_id: str = "", source_event_id: str = "", request_id: str = "", related_event_id: str = "") -> str:
    """Retrieve Cloud Security consumption, invoice, adjustment, remittance and service evidence. Search by the contract or customer, an event reference, its original source, a customer request or related evidence. All criteria are optional; results preserve the recorded business details and an empty list means no match.

    Args:
        security_event_id: Reference identifying this accounting or service event. Copy the reference from a retrieved business record; leave "" if unknown.
        security_holding_id: Contract to which this event belongs. Copy the reference from a retrieved business record; leave "" if unknown.
        customer_id: Customer owning the event and the referenced contract. Copy the reference from a retrieved business record; leave "" if unknown.
        source_event_id: Narrowest original event corrected, billed, credited, paid or refunded; empty for an independent source. Copy the reference from a retrieved business record; leave "" if unknown.
        request_id: Customer request event reference; empty where no customer request is needed. Copy the reference from a retrieved business record; leave "" if unknown.
        related_event_id: Additional linked approval, incident or evidence event; empty when absent. Copy the reference from a retrieved business record; leave "" if unknown.
    """
    match = {k: v for k, v in {'security_event_id': security_event_id, 'security_holding_id': security_holding_id, 'customer_id': customer_id, 'source_event_id': source_event_id, 'request_id': request_id, 'related_event_id': related_event_id}.items() if v}
    return str(ctx.find("security_events", **match))

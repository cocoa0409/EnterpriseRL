"""Shared tools for env_0058_home_warranty_company (Bridgewell Home Warranty).

Every tool here is always available. It holds the record lookups (one per kind of record; the customer
lookup doubles as the way to find a caller from what they state), the identity verification, and the
handoff to a human representative. Customer-only actions and per-difficulty business writes live in each
difficulty's task tools.

Operational constants built into these tools:
  - identity verification passes when at least 2 of the stated credentials match the profile;
  - a customer is handed to a human on request once they have explicitly asked 2 times.
"""

from erlbench import ToolContext, tool


def _pick(**kwargs):
    # keep only the criteria that were actually supplied
    return {k: v for k, v in kwargs.items() if v not in ("", None)}

@tool(owner="agent", rw="read")
def find_customers(ctx: ToolContext, customer_id: str = "", full_name: str = "", phone_number: str = "",
                   email: str = "", real_estate_license_number: str = "") -> str:
    """Find the customer profile a call is about. A caller can be found by their customer reference number, or by
    what they can naturally tell you: their full name, the phone number or email address on file, or, for a real
    estate agent, their license number. Combine details when one is not enough to single out one person.

    The profile returned shows the customer's name, type (homeowner, landlord or real estate agent), phone number,
    email, mailing ZIP code, the last four digits of the card on file, the date the profile was opened and, for an
    agent, the brokerage and license number. Finding a profile does not verify the caller's identity.

    Args:
        customer_id: The customer reference number. Leave empty if unknown.
        full_name: The caller's full name as they state it. Leave empty if not given.
        phone_number: The phone number the caller gives, 10 digits. Leave empty if not given.
        email: The email address the caller gives. Leave empty if not given.
        real_estate_license_number: For a real estate agent, the license number they give. Leave empty if not given.
    """
    match = _pick(customer_id=customer_id, full_name=full_name, phone_number=phone_number, email=email,
                  real_estate_license_number=real_estate_license_number)
    if not match:
        return "Error: provide at least one detail to find the customer."
    rows = ctx.fuzzy_find("customers", **match)
    if not rows:
        return f"No customer matches {match}."
    if len(rows) > 1:
        return f"Error: {len(rows)} customers match {match}; ask the caller for one more detail."
    return str(rows[0])


@tool(owner="agent", rw="read")
def find_service_contractors(ctx: ToolContext, service_contractor_id: str = "", trade: str = "") -> str:
    """Look up contractors in the Bridgewell service network: business name, trade, the ZIP codes each one serves, network standing (preferred, standard or suspended), whether they accept emergency calls, and their trade license number. Search by contractor reference, or by trade to see every network contractor of that trade; with no criteria, the whole network is listed.

    Every criterion is optional; supply whichever reference numbers you already have and leave the rest empty.
    All matching records are returned; when nothing matches, a short notice says so.

    Args:
        service_contractor_id: Reference number: the contractor reference. Leave empty if unknown.
        trade: Trade of the contractors to list, one of: hvac, plumbing, electrical, appliance, garage_door, pool_spa, septic, well_pump, roofing, locksmith, utility_line. Leave empty for every trade.
    """
    match = _pick(service_contractor_id=service_contractor_id, trade=trade)
    rows = ctx.find("service_contractors", **match)
    return str(rows) if rows else f"No matching records for {match}."

@tool(owner="agent", rw="read")
def find_identity_verifications(ctx: ToolContext, verification_id: str = "", customer_id: str = "") -> str:
    """Look up the identity verification outcome recorded for a customer: whether verification has passed and when it was last attempted.

    Every criterion is optional; supply whichever reference numbers you already have and leave the rest empty.
    All matching records are returned; when nothing matches, a short notice says so.

    Args:
        verification_id: Reference number: the verification record reference. Leave empty if unknown.
        customer_id: Reference number: the customer reference number of the customer the record belongs to. Leave empty if unknown.
    """
    match = _pick(verification_id=verification_id, customer_id=customer_id)
    if not match:
        return "Error: provide at least one reference number to look up these records."
    rows = ctx.find("identity_verifications", **match)
    return str(rows) if rows else f"No matching records for {match}."

@tool(owner="agent", rw="read")
def find_human_handoffs(ctx: ToolContext, handoff_id: str = "", customer_id: str = "") -> str:
    """Look up handoffs of a customer to a human representative: the reason recorded and when it happened.

    Every criterion is optional; supply whichever reference numbers you already have and leave the rest empty.
    All matching records are returned; when nothing matches, a short notice says so.

    Args:
        handoff_id: Reference number: the handoff record reference. Leave empty if unknown.
        customer_id: Reference number: the customer reference number of the customer the record belongs to. Leave empty if unknown.
    """
    match = _pick(handoff_id=handoff_id, customer_id=customer_id)
    if not match:
        return "Error: provide at least one reference number to look up these records."
    rows = ctx.find("human_handoffs", **match)
    return str(rows) if rows else f"No matching records for {match}."

@tool(owner="agent", rw="read")
def find_homeplan_contracts(ctx: ToolContext, homeplan_contract_id: str = "", customer_id: str = "", realty_contract_id: str = "") -> str:
    """Look up homeowner service contracts: tier, status, covered property, enrollment channel, term dates, coverage effective date, billing frequency, service call fee option, renewal settings, any prior tier, premium balance and end date.

    Every criterion is optional; supply whichever reference numbers you already have and leave the rest empty.
    All matching records are returned; when nothing matches, a short notice says so.

    Args:
        homeplan_contract_id: Reference number: the homeowner service contract number. Leave empty if unknown.
        customer_id: Reference number: the customer reference number of the customer the record belongs to. Leave empty if unknown.
        realty_contract_id: Reference number: the real estate contract (plan) number the record belongs to. Leave empty if unknown.
    """
    match = _pick(homeplan_contract_id=homeplan_contract_id, customer_id=customer_id, realty_contract_id=realty_contract_id)
    if not match:
        return "Error: provide at least one reference number to look up these records."
    rows = ctx.find("homeplan_contracts", **match)
    return str(rows) if rows else f"No matching records for {match}."

@tool(owner="agent", rw="read")
def find_homeplan_billing_entries(ctx: ToolContext, homeplan_billing_entry_id: str = "", homeplan_contract_id: str = "", customer_id: str = "", homeplan_cancellation_request_id: str = "", homeplan_service_request_id: str = "") -> str:
    """Look up the billing history of homeowner service contracts: premium charges, payments, credits, refunds and service call fees, with dates, amounts, billing periods and confirmation numbers.

    Every criterion is optional; supply whichever reference numbers you already have and leave the rest empty.
    All matching records are returned; when nothing matches, a short notice says so.

    Args:
        homeplan_billing_entry_id: Reference number: the billing entry reference. Leave empty if unknown.
        homeplan_contract_id: Reference number: the homeowner service contract number the record belongs to. Leave empty if unknown.
        customer_id: Reference number: the customer reference number of the customer the record belongs to. Leave empty if unknown.
        homeplan_cancellation_request_id: Reference number: the cancellation request the record settles. Leave empty if unknown.
        homeplan_service_request_id: Reference number: the homeowner service request number the record relates to. Leave empty if unknown.
    """
    match = _pick(homeplan_billing_entry_id=homeplan_billing_entry_id, homeplan_contract_id=homeplan_contract_id, customer_id=customer_id, homeplan_cancellation_request_id=homeplan_cancellation_request_id, homeplan_service_request_id=homeplan_service_request_id)
    if not match:
        return "Error: provide at least one reference number to look up these records."
    rows = ctx.find("homeplan_billing_entries", **match)
    return str(rows) if rows else f"No matching records for {match}."

@tool(owner="agent", rw="read")
def find_homeplan_service_requests(ctx: ToolContext, homeplan_service_request_id: str = "", homeplan_contract_id: str = "", customer_id: str = "") -> str:
    """Look up service requests placed under homeowner service contracts: request date, failed item, trade, request type, urgency, visit window, the customer's description, and for a recall the earlier authorization it refers to.

    Every criterion is optional; supply whichever reference numbers you already have and leave the rest empty.
    All matching records are returned; when nothing matches, a short notice says so.

    Args:
        homeplan_service_request_id: Reference number: the service request number. Leave empty if unknown.
        homeplan_contract_id: Reference number: the homeowner service contract number the record belongs to. Leave empty if unknown.
        customer_id: Reference number: the customer reference number of the customer the record belongs to. Leave empty if unknown.
    """
    match = _pick(homeplan_service_request_id=homeplan_service_request_id, homeplan_contract_id=homeplan_contract_id, customer_id=customer_id)
    if not match:
        return "Error: provide at least one reference number to look up these records."
    rows = ctx.find("homeplan_service_requests", **match)
    return str(rows) if rows else f"No matching records for {match}."

@tool(owner="agent", rw="read")
def find_homeplan_claim_events(ctx: ToolContext, homeplan_claim_event_id: str = "", homeplan_contract_id: str = "", customer_id: str = "", homeplan_service_request_id: str = "", service_contractor_id: str = "") -> str:
    """Look up the handling history of homeowner service requests: contractor assignments, coverage determinations, repair and replacement authorizations, supplemental allowances, cash-in-lieu offers and payments, out-of-network reimbursements, reversals and completion reports.

    Every criterion is optional; supply whichever reference numbers you already have and leave the rest empty.
    All matching records are returned; when nothing matches, a short notice says so.

    Args:
        homeplan_claim_event_id: Reference number: the claim event reference. Leave empty if unknown.
        homeplan_contract_id: Reference number: the homeowner service contract number the record belongs to. Leave empty if unknown.
        customer_id: Reference number: the customer reference number of the customer the record belongs to. Leave empty if unknown.
        homeplan_service_request_id: Reference number: the homeowner service request number the record relates to. Leave empty if unknown.
        service_contractor_id: Reference number: the network contractor reference on the record. Leave empty if unknown.
    """
    match = _pick(homeplan_claim_event_id=homeplan_claim_event_id, homeplan_contract_id=homeplan_contract_id, customer_id=customer_id, homeplan_service_request_id=homeplan_service_request_id, service_contractor_id=service_contractor_id)
    if not match:
        return "Error: provide at least one reference number to look up these records."
    rows = ctx.find("homeplan_claim_events", **match)
    return str(rows) if rows else f"No matching records for {match}."

@tool(owner="agent", rw="read")
def find_homeplan_cancellation_requests(ctx: ToolContext, homeplan_cancellation_request_id: str = "", customer_id: str = "", homeplan_contract_id: str = "") -> str:
    """Look up cancellation requests on homeowner service contracts: notice date, reason given and whether the customer has confirmed or withdrawn the request.

    Every criterion is optional; supply whichever reference numbers you already have and leave the rest empty.
    All matching records are returned; when nothing matches, a short notice says so.

    Args:
        homeplan_cancellation_request_id: Reference number: the cancellation request reference. Leave empty if unknown.
        customer_id: Reference number: the customer reference number of the customer the record belongs to. Leave empty if unknown.
        homeplan_contract_id: Reference number: the homeowner service contract number the record belongs to. Leave empty if unknown.
    """
    match = _pick(homeplan_cancellation_request_id=homeplan_cancellation_request_id, customer_id=customer_id, homeplan_contract_id=homeplan_contract_id)
    if not match:
        return "Error: provide at least one reference number to look up these records."
    rows = ctx.find("homeplan_cancellation_requests", **match)
    return str(rows) if rows else f"No matching records for {match}."

@tool(owner="agent", rw="read")
def find_realty_contracts(ctx: ToolContext, realty_contract_id: str = "", customer_id: str = "", ordering_agent_license_number: str = "") -> str:
    """Look up real estate service contracts: plan, status, order type, ordering agent's license number and side, property details, order and listing coverage dates, expected and actual closing dates, escrow file number, buyer coverage dates, invoice balance and end date. Orders can also be found by the ordering agent's license number.

    Every criterion is optional; supply whichever reference numbers you already have and leave the rest empty.
    All matching records are returned; when nothing matches, a short notice says so.

    Args:
        realty_contract_id: Reference number: the real estate contract (plan) number. Leave empty if unknown.
        customer_id: Reference number: the customer reference number of the customer the record belongs to. Leave empty if unknown.
        ordering_agent_license_number: The ordering real estate agent's license number exactly as on file, to list that agent's orders. Leave empty if not needed.
    """
    match = _pick(realty_contract_id=realty_contract_id, customer_id=customer_id, ordering_agent_license_number=ordering_agent_license_number)
    if not match:
        return "Error: provide at least one reference number to look up these records."
    rows = ctx.find("realty_contracts", **match)
    return str(rows) if rows else f"No matching records for {match}."

@tool(owner="agent", rw="read")
def find_realty_billing_entries(ctx: ToolContext, realty_billing_entry_id: str = "", realty_contract_id: str = "", customer_id: str = "", realty_service_request_id: str = "") -> str:
    """Look up the billing history of real estate service contracts: plan invoices, failed-sale charges, payments, credit memos, refunds and service call fees, with invoice numbers, due dates, payer and confirmation numbers.

    Every criterion is optional; supply whichever reference numbers you already have and leave the rest empty.
    All matching records are returned; when nothing matches, a short notice says so.

    Args:
        realty_billing_entry_id: Reference number: the billing entry reference. Leave empty if unknown.
        realty_contract_id: Reference number: the real estate contract (plan) number the record belongs to. Leave empty if unknown.
        customer_id: Reference number: the customer reference number of the customer the record belongs to. Leave empty if unknown.
        realty_service_request_id: Reference number: the real estate service request number the record relates to. Leave empty if unknown.
    """
    match = _pick(realty_billing_entry_id=realty_billing_entry_id, realty_contract_id=realty_contract_id, customer_id=customer_id, realty_service_request_id=realty_service_request_id)
    if not match:
        return "Error: provide at least one reference number to look up these records."
    rows = ctx.find("realty_billing_entries", **match)
    return str(rows) if rows else f"No matching records for {match}."

@tool(owner="agent", rw="read")
def find_realty_service_requests(ctx: ToolContext, realty_service_request_id: str = "", realty_contract_id: str = "", customer_id: str = "") -> str:
    """Look up service requests placed under real estate service contracts: request date, coverage phase (seller listing or buyer), item, trade, request type, urgency and the caller's description.

    Every criterion is optional; supply whichever reference numbers you already have and leave the rest empty.
    All matching records are returned; when nothing matches, a short notice says so.

    Args:
        realty_service_request_id: Reference number: the service request number. Leave empty if unknown.
        realty_contract_id: Reference number: the real estate contract (plan) number the record belongs to. Leave empty if unknown.
        customer_id: Reference number: the customer reference number of the customer the record belongs to. Leave empty if unknown.
    """
    match = _pick(realty_service_request_id=realty_service_request_id, realty_contract_id=realty_contract_id, customer_id=customer_id)
    if not match:
        return "Error: provide at least one reference number to look up these records."
    rows = ctx.find("realty_service_requests", **match)
    return str(rows) if rows else f"No matching records for {match}."

@tool(owner="agent", rw="read")
def find_realty_claim_events(ctx: ToolContext, realty_claim_event_id: str = "", realty_contract_id: str = "", customer_id: str = "", realty_service_request_id: str = "", service_contractor_id: str = "") -> str:
    """Look up the handling history of real estate service requests: contractor assignments, coverage determinations, benefit authorizations and reversals.

    Every criterion is optional; supply whichever reference numbers you already have and leave the rest empty.
    All matching records are returned; when nothing matches, a short notice says so.

    Args:
        realty_claim_event_id: Reference number: the claim event reference. Leave empty if unknown.
        realty_contract_id: Reference number: the real estate contract (plan) number the record belongs to. Leave empty if unknown.
        customer_id: Reference number: the customer reference number of the customer the record belongs to. Leave empty if unknown.
        realty_service_request_id: Reference number: the real estate service request number the record relates to. Leave empty if unknown.
        service_contractor_id: Reference number: the network contractor reference on the record. Leave empty if unknown.
    """
    match = _pick(realty_claim_event_id=realty_claim_event_id, realty_contract_id=realty_contract_id, customer_id=customer_id, realty_service_request_id=realty_service_request_id, service_contractor_id=service_contractor_id)
    if not match:
        return "Error: provide at least one reference number to look up these records."
    rows = ctx.find("realty_claim_events", **match)
    return str(rows) if rows else f"No matching records for {match}."

@tool(owner="agent", rw="read")
def find_landlord_contracts(ctx: ToolContext, landlord_contract_id: str = "", customer_id: str = "") -> str:
    """Look up rental property service contracts: tier, status, rental property, unit count, year built, authorized tenant contact, term dates, billing frequency, renewal settings, transfer date, premium balance and end date.

    Every criterion is optional; supply whichever reference numbers you already have and leave the rest empty.
    All matching records are returned; when nothing matches, a short notice says so.

    Args:
        landlord_contract_id: Reference number: the rental property service contract number. Leave empty if unknown.
        customer_id: Reference number: the customer reference number of the customer the record belongs to. Leave empty if unknown.
    """
    match = _pick(landlord_contract_id=landlord_contract_id, customer_id=customer_id)
    if not match:
        return "Error: provide at least one reference number to look up these records."
    rows = ctx.find("landlord_contracts", **match)
    return str(rows) if rows else f"No matching records for {match}."

@tool(owner="agent", rw="read")
def find_landlord_billing_entries(ctx: ToolContext, landlord_billing_entry_id: str = "", landlord_contract_id: str = "", customer_id: str = "", landlord_cancellation_request_id: str = "", landlord_service_request_id: str = "") -> str:
    """Look up the billing history of rental property service contracts: premium charges with the portfolio discount applied, payments, credits, refunds, transfer fees and service call fees.

    Every criterion is optional; supply whichever reference numbers you already have and leave the rest empty.
    All matching records are returned; when nothing matches, a short notice says so.

    Args:
        landlord_billing_entry_id: Reference number: the billing entry reference. Leave empty if unknown.
        landlord_contract_id: Reference number: the rental property service contract number the record belongs to. Leave empty if unknown.
        customer_id: Reference number: the customer reference number of the customer the record belongs to. Leave empty if unknown.
        landlord_cancellation_request_id: Reference number: the cancellation request the record settles. Leave empty if unknown.
        landlord_service_request_id: Reference number: the rental property service request number the record relates to. Leave empty if unknown.
    """
    match = _pick(landlord_billing_entry_id=landlord_billing_entry_id, landlord_contract_id=landlord_contract_id, customer_id=customer_id, landlord_cancellation_request_id=landlord_cancellation_request_id, landlord_service_request_id=landlord_service_request_id)
    if not match:
        return "Error: provide at least one reference number to look up these records."
    rows = ctx.find("landlord_billing_entries", **match)
    return str(rows) if rows else f"No matching records for {match}."

@tool(owner="agent", rw="read")
def find_landlord_service_requests(ctx: ToolContext, landlord_service_request_id: str = "", landlord_contract_id: str = "", customer_id: str = "") -> str:
    """Look up service requests placed under rental property service contracts: request date, unit, who placed it (landlord or authorized tenant), item, trade, request type, urgency, visit window and description.

    Every criterion is optional; supply whichever reference numbers you already have and leave the rest empty.
    All matching records are returned; when nothing matches, a short notice says so.

    Args:
        landlord_service_request_id: Reference number: the service request number. Leave empty if unknown.
        landlord_contract_id: Reference number: the rental property service contract number the record belongs to. Leave empty if unknown.
        customer_id: Reference number: the customer reference number of the customer the record belongs to. Leave empty if unknown.
    """
    match = _pick(landlord_service_request_id=landlord_service_request_id, landlord_contract_id=landlord_contract_id, customer_id=customer_id)
    if not match:
        return "Error: provide at least one reference number to look up these records."
    rows = ctx.find("landlord_service_requests", **match)
    return str(rows) if rows else f"No matching records for {match}."

@tool(owner="agent", rw="read")
def find_landlord_claim_events(ctx: ToolContext, landlord_claim_event_id: str = "", landlord_contract_id: str = "", customer_id: str = "", landlord_service_request_id: str = "", service_contractor_id: str = "") -> str:
    """Look up the handling history of rental property service requests: contractor assignments, coverage determinations, benefit authorizations and reversals, by unit.

    Every criterion is optional; supply whichever reference numbers you already have and leave the rest empty.
    All matching records are returned; when nothing matches, a short notice says so.

    Args:
        landlord_claim_event_id: Reference number: the claim event reference. Leave empty if unknown.
        landlord_contract_id: Reference number: the rental property service contract number the record belongs to. Leave empty if unknown.
        customer_id: Reference number: the customer reference number of the customer the record belongs to. Leave empty if unknown.
        landlord_service_request_id: Reference number: the rental property service request number the record relates to. Leave empty if unknown.
        service_contractor_id: Reference number: the network contractor reference on the record. Leave empty if unknown.
    """
    match = _pick(landlord_claim_event_id=landlord_claim_event_id, landlord_contract_id=landlord_contract_id, customer_id=customer_id, landlord_service_request_id=landlord_service_request_id, service_contractor_id=service_contractor_id)
    if not match:
        return "Error: provide at least one reference number to look up these records."
    rows = ctx.find("landlord_claim_events", **match)
    return str(rows) if rows else f"No matching records for {match}."

@tool(owner="agent", rw="read")
def find_landlord_cancellation_requests(ctx: ToolContext, landlord_cancellation_request_id: str = "", customer_id: str = "", landlord_contract_id: str = "") -> str:
    """Look up cancellation requests on rental property service contracts: notice date, reason, the stated sale closing date for a sold property, and whether the landlord has confirmed or withdrawn the request.

    Every criterion is optional; supply whichever reference numbers you already have and leave the rest empty.
    All matching records are returned; when nothing matches, a short notice says so.

    Args:
        landlord_cancellation_request_id: Reference number: the cancellation request reference. Leave empty if unknown.
        customer_id: Reference number: the customer reference number of the customer the record belongs to. Leave empty if unknown.
        landlord_contract_id: Reference number: the rental property service contract number the record belongs to. Leave empty if unknown.
    """
    match = _pick(landlord_cancellation_request_id=landlord_cancellation_request_id, customer_id=customer_id, landlord_contract_id=landlord_contract_id)
    if not match:
        return "Error: provide at least one reference number to look up these records."
    rows = ctx.find("landlord_cancellation_requests", **match)
    return str(rows) if rows else f"No matching records for {match}."

@tool(owner="agent", rw="read")
def find_addon_riders(ctx: ToolContext, addon_rider_id: str = "", customer_id: str = "", homeplan_contract_id: str = "", landlord_contract_id: str = "", realty_contract_id: str = "") -> str:
    """Look up optional coverage riders: rider, status, the base contract it is attached to, add date, coverage effective date, term dates, billing frequency, the property facts stated when it was added, rider premium balance and end date.

    Every criterion is optional; supply whichever reference numbers you already have and leave the rest empty.
    All matching records are returned; when nothing matches, a short notice says so.

    Args:
        addon_rider_id: Reference number: the rider reference. Leave empty if unknown.
        customer_id: Reference number: the customer reference number of the customer the record belongs to. Leave empty if unknown.
        homeplan_contract_id: Reference number: the homeowner service contract number the record belongs to. Leave empty if unknown.
        landlord_contract_id: Reference number: the rental property service contract number the record belongs to. Leave empty if unknown.
        realty_contract_id: Reference number: the real estate contract (plan) number the record belongs to. Leave empty if unknown.
    """
    match = _pick(addon_rider_id=addon_rider_id, customer_id=customer_id, homeplan_contract_id=homeplan_contract_id, landlord_contract_id=landlord_contract_id, realty_contract_id=realty_contract_id)
    if not match:
        return "Error: provide at least one reference number to look up these records."
    rows = ctx.find("addon_riders", **match)
    return str(rows) if rows else f"No matching records for {match}."

@tool(owner="agent", rw="read")
def find_addon_billing_entries(ctx: ToolContext, addon_billing_entry_id: str = "", addon_rider_id: str = "", customer_id: str = "", addon_service_request_id: str = "") -> str:
    """Look up the billing history of optional coverage riders: rider premium charges, payments, credits, refunds and rider service call fees.

    Every criterion is optional; supply whichever reference numbers you already have and leave the rest empty.
    All matching records are returned; when nothing matches, a short notice says so.

    Args:
        addon_billing_entry_id: Reference number: the billing entry reference. Leave empty if unknown.
        addon_rider_id: Reference number: the rider reference the record belongs to. Leave empty if unknown.
        customer_id: Reference number: the customer reference number of the customer the record belongs to. Leave empty if unknown.
        addon_service_request_id: Reference number: the rider service request number the record relates to. Leave empty if unknown.
    """
    match = _pick(addon_billing_entry_id=addon_billing_entry_id, addon_rider_id=addon_rider_id, customer_id=customer_id, addon_service_request_id=addon_service_request_id)
    if not match:
        return "Error: provide at least one reference number to look up these records."
    rows = ctx.find("addon_billing_entries", **match)
    return str(rows) if rows else f"No matching records for {match}."

@tool(owner="agent", rw="read")
def find_addon_service_requests(ctx: ToolContext, addon_service_request_id: str = "", addon_rider_id: str = "", customer_id: str = "") -> str:
    """Look up service requests placed under optional coverage riders: request date, component, trade, request type, urgency, whether it is serviced alongside a base contract visit, and description.

    Every criterion is optional; supply whichever reference numbers you already have and leave the rest empty.
    All matching records are returned; when nothing matches, a short notice says so.

    Args:
        addon_service_request_id: Reference number: the rider service request number. Leave empty if unknown.
        addon_rider_id: Reference number: the rider reference the record belongs to. Leave empty if unknown.
        customer_id: Reference number: the customer reference number of the customer the record belongs to. Leave empty if unknown.
    """
    match = _pick(addon_service_request_id=addon_service_request_id, addon_rider_id=addon_rider_id, customer_id=customer_id)
    if not match:
        return "Error: provide at least one reference number to look up these records."
    rows = ctx.find("addon_service_requests", **match)
    return str(rows) if rows else f"No matching records for {match}."

@tool(owner="agent", rw="read")
def find_addon_claim_events(ctx: ToolContext, addon_claim_event_id: str = "", addon_rider_id: str = "", customer_id: str = "", addon_service_request_id: str = "", service_contractor_id: str = "") -> str:
    """Look up the handling history of rider service requests: contractor assignments, coverage determinations, benefit authorizations (including septic pumping and allowances) and reversals.

    Every criterion is optional; supply whichever reference numbers you already have and leave the rest empty.
    All matching records are returned; when nothing matches, a short notice says so.

    Args:
        addon_claim_event_id: Reference number: the claim event reference. Leave empty if unknown.
        addon_rider_id: Reference number: the rider reference the record belongs to. Leave empty if unknown.
        customer_id: Reference number: the customer reference number of the customer the record belongs to. Leave empty if unknown.
        addon_service_request_id: Reference number: the rider service request number the record relates to. Leave empty if unknown.
        service_contractor_id: Reference number: the network contractor reference on the record. Leave empty if unknown.
    """
    match = _pick(addon_claim_event_id=addon_claim_event_id, addon_rider_id=addon_rider_id, customer_id=customer_id, addon_service_request_id=addon_service_request_id, service_contractor_id=service_contractor_id)
    if not match:
        return "Error: provide at least one reference number to look up these records."
    rows = ctx.find("addon_claim_events", **match)
    return str(rows) if rows else f"No matching records for {match}."

@tool(owner="agent", rw="read")
def find_lineplan_contracts(ctx: ToolContext, lineplan_contract_id: str = "", customer_id: str = "") -> str:
    """Look up utility line protection plans: plan, status, property, partner utility, billing channel and frequency, service line material, term dates, coverage effective date, renewal settings, premium balance and end date.

    Every criterion is optional; supply whichever reference numbers you already have and leave the rest empty.
    All matching records are returned; when nothing matches, a short notice says so.

    Args:
        lineplan_contract_id: Reference number: the line protection plan number. Leave empty if unknown.
        customer_id: Reference number: the customer reference number of the customer the record belongs to. Leave empty if unknown.
    """
    match = _pick(lineplan_contract_id=lineplan_contract_id, customer_id=customer_id)
    if not match:
        return "Error: provide at least one reference number to look up these records."
    rows = ctx.find("lineplan_contracts", **match)
    return str(rows) if rows else f"No matching records for {match}."

@tool(owner="agent", rw="read")
def find_lineplan_billing_entries(ctx: ToolContext, lineplan_billing_entry_id: str = "", lineplan_contract_id: str = "", customer_id: str = "") -> str:
    """Look up the billing history of utility line protection plans: premium charges, payments or utility remittances, credits and refunds.

    Every criterion is optional; supply whichever reference numbers you already have and leave the rest empty.
    All matching records are returned; when nothing matches, a short notice says so.

    Args:
        lineplan_billing_entry_id: Reference number: the billing entry reference. Leave empty if unknown.
        lineplan_contract_id: Reference number: the line protection plan number the record belongs to. Leave empty if unknown.
        customer_id: Reference number: the customer reference number of the customer the record belongs to. Leave empty if unknown.
    """
    match = _pick(lineplan_billing_entry_id=lineplan_billing_entry_id, lineplan_contract_id=lineplan_contract_id, customer_id=customer_id)
    if not match:
        return "Error: provide at least one reference number to look up these records."
    rows = ctx.find("lineplan_billing_entries", **match)
    return str(rows) if rows else f"No matching records for {match}."

@tool(owner="agent", rw="read")
def find_lineplan_service_requests(ctx: ToolContext, lineplan_service_request_id: str = "", lineplan_contract_id: str = "", customer_id: str = "") -> str:
    """Look up line service requests: request date, line, new failure or recall, urgency and description.

    Every criterion is optional; supply whichever reference numbers you already have and leave the rest empty.
    All matching records are returned; when nothing matches, a short notice says so.

    Args:
        lineplan_service_request_id: Reference number: the line service request number. Leave empty if unknown.
        lineplan_contract_id: Reference number: the line protection plan number the record belongs to. Leave empty if unknown.
        customer_id: Reference number: the customer reference number of the customer the record belongs to. Leave empty if unknown.
    """
    match = _pick(lineplan_service_request_id=lineplan_service_request_id, lineplan_contract_id=lineplan_contract_id, customer_id=customer_id)
    if not match:
        return "Error: provide at least one reference number to look up these records."
    rows = ctx.find("lineplan_service_requests", **match)
    return str(rows) if rows else f"No matching records for {match}."

@tool(owner="agent", rw="read")
def find_lineplan_claim_events(ctx: ToolContext, lineplan_claim_event_id: str = "", lineplan_contract_id: str = "", customer_id: str = "", lineplan_service_request_id: str = "", service_contractor_id: str = "") -> str:
    """Look up the handling history of line service requests: contractor assignments, line determinations (including which side of the utility connection the failure is on), repair and replacement authorizations with restoration allowances, reversals and completion reports.

    Every criterion is optional; supply whichever reference numbers you already have and leave the rest empty.
    All matching records are returned; when nothing matches, a short notice says so.

    Args:
        lineplan_claim_event_id: Reference number: the claim event reference. Leave empty if unknown.
        lineplan_contract_id: Reference number: the line protection plan number the record belongs to. Leave empty if unknown.
        customer_id: Reference number: the customer reference number of the customer the record belongs to. Leave empty if unknown.
        lineplan_service_request_id: Reference number: the line service request number the record relates to. Leave empty if unknown.
        service_contractor_id: Reference number: the network contractor reference on the record. Leave empty if unknown.
    """
    match = _pick(lineplan_claim_event_id=lineplan_claim_event_id, lineplan_contract_id=lineplan_contract_id, customer_id=customer_id, lineplan_service_request_id=lineplan_service_request_id, service_contractor_id=service_contractor_id)
    if not match:
        return "Error: provide at least one reference number to look up these records."
    rows = ctx.find("lineplan_claim_events", **match)
    return str(rows) if rows else f"No matching records for {match}."

@tool(owner="agent", rw="read")
def find_hvaccare_agreements(ctx: ToolContext, hvaccare_agreement_id: str = "", customer_id: str = "") -> str:
    """Look up HVAC maintenance agreements: level, status, property, systems enrolled and equipment, billing frequency, qualifying inspection, term dates, renewal settings, membership balance, visits remaining and end date.

    Every criterion is optional; supply whichever reference numbers you already have and leave the rest empty.
    All matching records are returned; when nothing matches, a short notice says so.

    Args:
        hvaccare_agreement_id: Reference number: the maintenance agreement number. Leave empty if unknown.
        customer_id: Reference number: the customer reference number of the customer the record belongs to. Leave empty if unknown.
    """
    match = _pick(hvaccare_agreement_id=hvaccare_agreement_id, customer_id=customer_id)
    if not match:
        return "Error: provide at least one reference number to look up these records."
    rows = ctx.find("hvaccare_agreements", **match)
    return str(rows) if rows else f"No matching records for {match}."

@tool(owner="agent", rw="read")
def find_hvaccare_billing_entries(ctx: ToolContext, hvaccare_billing_entry_id: str = "", hvaccare_agreement_id: str = "", customer_id: str = "", hvaccare_visit_event_id: str = "") -> str:
    """Look up the billing history of HVAC maintenance agreements: membership fees, missed-appointment fees, payments, credits and refunds.

    Every criterion is optional; supply whichever reference numbers you already have and leave the rest empty.
    All matching records are returned; when nothing matches, a short notice says so.

    Args:
        hvaccare_billing_entry_id: Reference number: the billing entry reference. Leave empty if unknown.
        hvaccare_agreement_id: Reference number: the maintenance agreement number the record belongs to. Leave empty if unknown.
        customer_id: Reference number: the customer reference number of the customer the record belongs to. Leave empty if unknown.
        hvaccare_visit_event_id: Reference number: the visit the record relates to. Leave empty if unknown.
    """
    match = _pick(hvaccare_billing_entry_id=hvaccare_billing_entry_id, hvaccare_agreement_id=hvaccare_agreement_id, customer_id=customer_id, hvaccare_visit_event_id=hvaccare_visit_event_id)
    if not match:
        return "Error: provide at least one reference number to look up these records."
    rows = ctx.find("hvaccare_billing_entries", **match)
    return str(rows) if rows else f"No matching records for {match}."

@tool(owner="agent", rw="read")
def find_hvaccare_visit_events(ctx: ToolContext, hvaccare_visit_event_id: str = "", hvaccare_agreement_id: str = "", customer_id: str = "", service_contractor_id: str = "") -> str:
    """Look up the visit history of HVAC maintenance agreements: visit allotments, completed or missed tune-ups by system and season, forfeited visits, and member repair discounts.

    Every criterion is optional; supply whichever reference numbers you already have and leave the rest empty.
    All matching records are returned; when nothing matches, a short notice says so.

    Args:
        hvaccare_visit_event_id: Reference number: the visit event reference. Leave empty if unknown.
        hvaccare_agreement_id: Reference number: the maintenance agreement number the record belongs to. Leave empty if unknown.
        customer_id: Reference number: the customer reference number of the customer the record belongs to. Leave empty if unknown.
        service_contractor_id: Reference number: the network contractor reference on the record. Leave empty if unknown.
    """
    match = _pick(hvaccare_visit_event_id=hvaccare_visit_event_id, hvaccare_agreement_id=hvaccare_agreement_id, customer_id=customer_id, service_contractor_id=service_contractor_id)
    if not match:
        return "Error: provide at least one reference number to look up these records."
    rows = ctx.find("hvaccare_visit_events", **match)
    return str(rows) if rows else f"No matching records for {match}."

@tool(owner="agent", rw="read")
def find_newhome_warranties(ctx: ToolContext, newhome_warranty_id: str = "", customer_id: str = "") -> str:
    """Look up new home builder warranties: program, status, home and builder, final sale price, closing and enrollment dates, the end date of each coverage phase, builder fee balance and any resale transfer.

    Every criterion is optional; supply whichever reference numbers you already have and leave the rest empty.
    All matching records are returned; when nothing matches, a short notice says so.

    Args:
        newhome_warranty_id: Reference number: the builder warranty number. Leave empty if unknown.
        customer_id: Reference number: the customer reference number of the customer the record belongs to. Leave empty if unknown.
    """
    match = _pick(newhome_warranty_id=newhome_warranty_id, customer_id=customer_id)
    if not match:
        return "Error: provide at least one reference number to look up these records."
    rows = ctx.find("newhome_warranties", **match)
    return str(rows) if rows else f"No matching records for {match}."

@tool(owner="agent", rw="read")
def find_newhome_billing_entries(ctx: ToolContext, newhome_billing_entry_id: str = "", newhome_warranty_id: str = "", customer_id: str = "", newhome_claim_id: str = "") -> str:
    """Look up the billing history of builder warranties: builder enrollment fees and payments, and homeowner deductibles, service and mediation fees, payments and credits.

    Every criterion is optional; supply whichever reference numbers you already have and leave the rest empty.
    All matching records are returned; when nothing matches, a short notice says so.

    Args:
        newhome_billing_entry_id: Reference number: the billing entry reference. Leave empty if unknown.
        newhome_warranty_id: Reference number: the builder warranty number the record belongs to. Leave empty if unknown.
        customer_id: Reference number: the customer reference number of the customer the record belongs to. Leave empty if unknown.
        newhome_claim_id: Reference number: the builder warranty claim number the record relates to. Leave empty if unknown.
    """
    match = _pick(newhome_billing_entry_id=newhome_billing_entry_id, newhome_warranty_id=newhome_warranty_id, customer_id=customer_id, newhome_claim_id=newhome_claim_id)
    if not match:
        return "Error: provide at least one reference number to look up these records."
    rows = ctx.find("newhome_billing_entries", **match)
    return str(rows) if rows else f"No matching records for {match}."

@tool(owner="agent", rw="read")
def find_newhome_claims(ctx: ToolContext, newhome_claim_id: str = "", newhome_warranty_id: str = "", customer_id: str = "") -> str:
    """Look up claims filed under builder warranties: filing and discovery dates, category, the homeowner's description and whether emergency work was done.

    Every criterion is optional; supply whichever reference numbers you already have and leave the rest empty.
    All matching records are returned; when nothing matches, a short notice says so.

    Args:
        newhome_claim_id: Reference number: the builder warranty claim number. Leave empty if unknown.
        newhome_warranty_id: Reference number: the builder warranty number the record belongs to. Leave empty if unknown.
        customer_id: Reference number: the customer reference number of the customer the record belongs to. Leave empty if unknown.
    """
    match = _pick(newhome_claim_id=newhome_claim_id, newhome_warranty_id=newhome_warranty_id, customer_id=customer_id)
    if not match:
        return "Error: provide at least one reference number to look up these records."
    rows = ctx.find("newhome_claims", **match)
    return str(rows) if rows else f"No matching records for {match}."

@tool(owner="agent", rw="read")
def find_newhome_claim_events(ctx: ToolContext, newhome_claim_event_id: str = "", newhome_warranty_id: str = "", customer_id: str = "", newhome_claim_id: str = "") -> str:
    """Look up the handling history of builder warranty claims: tenders to the builder, builder responses, mediation requests and outcomes, determinations, payment authorizations and reversals.

    Every criterion is optional; supply whichever reference numbers you already have and leave the rest empty.
    All matching records are returned; when nothing matches, a short notice says so.

    Args:
        newhome_claim_event_id: Reference number: the claim event reference. Leave empty if unknown.
        newhome_warranty_id: Reference number: the builder warranty number the record belongs to. Leave empty if unknown.
        customer_id: Reference number: the customer reference number of the customer the record belongs to. Leave empty if unknown.
        newhome_claim_id: Reference number: the builder warranty claim number the record relates to. Leave empty if unknown.
    """
    match = _pick(newhome_claim_event_id=newhome_claim_event_id, newhome_warranty_id=newhome_warranty_id, customer_id=customer_id, newhome_claim_id=newhome_claim_id)
    if not match:
        return "Error: provide at least one reference number to look up these records."
    rows = ctx.find("newhome_claim_events", **match)
    return str(rows) if rows else f"No matching records for {match}."

@tool(owner="agent", rw="write")
def verify_customer_identity(ctx: ToolContext, customer_id: str, phone_number: str = "", email: str = "",
                             mailing_zip: str = "", payment_card_last4: str = "", profile_opened_date: str = "",
                             real_estate_license_number: str = "") -> str:
    """Verify that the caller is the customer on the profile, and record the result. Identity must be verified
    before any account details are discussed or any change, payment, claim or cancellation is handled.

    The check is made here, not by you: each piece of identity information the caller states is compared with the
    profile, and verification passes when at least 2 of them match. The customer reference number only selects the
    profile and never counts as a match, and a name alone is not accepted as proof. Callers usually know only some of
    these details, so pass exactly what the caller said and leave the rest empty. If a first attempt fails and the
    caller then supplies more matching details, call again; a passed verification stays passed.

    Args:
        customer_id: The customer reference number from the profile lookup. Required.
        phone_number: The phone number the caller states, 10 digits without punctuation. Leave empty if not stated.
        email: The email address the caller states, exactly as given. Leave empty if not stated.
        mailing_zip: The 5-digit ZIP code of the mailing address the caller states. Leave empty if not stated.
        payment_card_last4: The last 4 digits of the payment card on file, as the caller states them. Leave empty if not stated.
        profile_opened_date: The date the caller says they opened their account, as YYYY-MM-DD. Leave empty if not stated.
        real_estate_license_number: For a real estate agent, the license number the caller states. Leave empty if not stated.
    """
    if not customer_id:
        return "Error: customer_id is required; find the customer profile first."
    rows = ctx.find("customers", customer_id=customer_id)
    if not rows:
        return f"Error: no customer {customer_id}; cannot verify."
    rec = rows[0]
    # The tool owns the comparison; the locator customer_id is never counted.
    supplied = {"phone_number": phone_number, "email": email, "mailing_zip": mailing_zip,
                "payment_card_last4": payment_card_last4, "profile_opened_date": profile_opened_date,
                "real_estate_license_number": real_estate_license_number}
    matched = sum(1 for field, value in supplied.items() if value and str(rec.get(field) or "").strip().lower() == str(value).strip().lower())
    verified = matched >= 2
    rid = ctx.make_id("ver_", customer_id)
    # Store only the reproducible outcome; upsert and never downgrade a pass.
    prior = ctx.find("identity_verifications", verification_id=rid)
    verified = verified or bool(prior and prior[0].get("verified"))
    if prior:
        ctx.update("identity_verifications", rid, verified=verified, verified_at=ctx.now())
    else:
        ctx.create("identity_verifications", rid, verification_id=rid, customer_id=customer_id,
                   verified=verified, verified_at=ctx.now())
    if verified:
        return f"Identity verified for {customer_id} ({matched} detail(s) matched on this attempt)."
    return (f"Identity NOT verified for {customer_id}: only {matched} of the 2 required details matched. "
            "Ask the caller for another detail on file and try again.")


@tool(owner="agent", rw="write")
def transfer_to_human_agent(ctx: ToolContext, customer_id: str, reason: str) -> str:
    """Hand the customer over to a human Bridgewell representative and record why.

    Use it in exactly two situations. When the request is one that no Bridgewell policy allows you to resolve, use
    POLICY_NOT_COVERED. When the customer has explicitly asked to speak with a human representative 2 times, use
    CUSTOMER_REQUESTED.

    Args:
        customer_id: The customer reference number from the profile lookup.
        reason: Why the customer is handed over: POLICY_NOT_COVERED or CUSTOMER_REQUESTED, exactly as written.
    """
    allowed = {"POLICY_NOT_COVERED", "CUSTOMER_REQUESTED"}
    if reason not in allowed:
        return f"Error: unknown handoff reason '{reason}'. Valid: {', '.join(sorted(allowed))}."
    if not ctx.find("customers", customer_id=customer_id):
        return f"Error: no customer {customer_id}; cannot record the handoff."
    rid = ctx.make_id("hof_", customer_id, reason)
    ctx.create("human_handoffs", rid, handoff_id=rid, customer_id=customer_id, reason=reason, created_at=ctx.now())
    return f"Handoff to a human representative recorded for {customer_id} ({reason})."

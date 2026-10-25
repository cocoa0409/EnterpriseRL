"""Shared tools for env_0066_captive_auto_finance_company (Kestrel Motor Acceptance Corporation).
Path: env/env_0066_captive_auto_finance_company/blueprint/share_tools.py

Share tools are always present in their owner's tool list: one finder per record type (the customer
finder doubles as the identity entry), the identity-verification write (K = 3 matching credentials)
and the transfer-to-human handoff (repeat-request threshold R = 2).
"""

from erlbench import ToolContext, tool

@tool(owner="agent", rw="read")
def find_retail_contracts(ctx: ToolContext, retail_contract_id: str = "", customer_id: str = "") -> str:
    """Look up Kestrel new-vehicle retail installment contracts: credit tier, status, vehicle, rate and payment schedule, balances, days past due, extension and due-date history, state rules recorded at booking, repossession dates and title status.

    Every criterion is optional; supply whichever reference numbers are already known. All matching
    entries are returned with their full details, or a short notice when nothing matches.

    Args:
        retail_contract_id: Reference number - the reference number of this retail contract entry itself; leave "" if unknown.
        customer_id: Reference number - the customer reference number; leave "" if unknown.
    """
    match = {k: v for k, v in {"retail_contract_id": retail_contract_id, "customer_id": customer_id}.items() if v}
    rows = ctx.find("retail_contracts", **match)
    return str(rows) if rows else f"No matching entries found for {match}."


@tool(owner="agent", rw="read")
def find_retail_transactions(ctx: ToolContext, retail_txn_id: str = "", retail_contract_id: str = "", customer_id: str = "", reversed_txn_id: str = "", payment_txn_id: str = "", waived_txn_id: str = "", care_contract_id: str = "") -> str:
    """Look up the posting history of new-vehicle retail installment contracts: payments and how they were applied, returned payments, late charges, fees and waivers, due-date changes, extensions, payoff quotes, lien releases, refund credits, notices and repossession charges and sales.

    Every criterion is optional; supply whichever reference numbers are already known. All matching
    entries are returned with their full details, or a short notice when nothing matches.

    Args:
        retail_txn_id: Reference number - the reference number of this retail transaction entry itself; leave "" if unknown.
        retail_contract_id: Reference number - the reference number of the linked retail contract; leave "" if unknown.
        customer_id: Reference number - the customer reference number; leave "" if unknown.
        reversed_txn_id: Reference number - the reference number of the payment that was dishonoured; leave "" if unknown.
        payment_txn_id: Reference number - the reference number of the payment from which a fee portion was applied; leave "" if unknown.
        waived_txn_id: Reference number - the reference number of the fee or charge that was waived; leave "" if unknown.
        care_contract_id: Reference number - the reference number of the Kestrel Care plan; leave "" if unknown.
    """
    match = {k: v for k, v in {"retail_txn_id": retail_txn_id, "retail_contract_id": retail_contract_id, "customer_id": customer_id, "reversed_txn_id": reversed_txn_id, "payment_txn_id": payment_txn_id, "waived_txn_id": waived_txn_id, "care_contract_id": care_contract_id}.items() if v}
    rows = ctx.find("retail_transactions", **match)
    return str(rows) if rows else f"No matching entries found for {match}."


@tool(owner="agent", rw="read")
def find_retail_requests(ctx: ToolContext, retail_request_id: str = "", customer_id: str = "", retail_contract_id: str = "") -> str:
    """Look up requests on new-vehicle retail installment contracts that wait on the customer's own signature or action, such as extension agreements, alternate-address title releases and voluntary surrenders, with their current status.

    Every criterion is optional; supply whichever reference numbers are already known. All matching
    entries are returned with their full details, or a short notice when nothing matches.

    Args:
        retail_request_id: Reference number - the reference number of this retail request entry itself; leave "" if unknown.
        customer_id: Reference number - the customer reference number; leave "" if unknown.
        retail_contract_id: Reference number - the reference number of the linked retail contract; leave "" if unknown.
    """
    match = {k: v for k, v in {"retail_request_id": retail_request_id, "customer_id": customer_id, "retail_contract_id": retail_contract_id}.items() if v}
    rows = ctx.find("retail_requests", **match)
    return str(rows) if rows else f"No matching entries found for {match}."


@tool(owner="agent", rw="read")
def find_preowned_contracts(ctx: ToolContext, preowned_contract_id: str = "", customer_id: str = "") -> str:
    """Look up Kestrel pre-owned retail installment contracts: credit tier, status, vehicle and certification, rate and payment schedule, balances, days past due, extension and due-date history, state rules recorded at booking, repossession dates and title status.

    Every criterion is optional; supply whichever reference numbers are already known. All matching
    entries are returned with their full details, or a short notice when nothing matches.

    Args:
        preowned_contract_id: Reference number - the reference number of this preowned contract entry itself; leave "" if unknown.
        customer_id: Reference number - the customer reference number; leave "" if unknown.
    """
    match = {k: v for k, v in {"preowned_contract_id": preowned_contract_id, "customer_id": customer_id}.items() if v}
    rows = ctx.find("preowned_contracts", **match)
    return str(rows) if rows else f"No matching entries found for {match}."


@tool(owner="agent", rw="read")
def find_preowned_transactions(ctx: ToolContext, preowned_txn_id: str = "", preowned_contract_id: str = "", customer_id: str = "", reversed_txn_id: str = "", payment_txn_id: str = "", waived_txn_id: str = "", care_contract_id: str = "") -> str:
    """Look up the posting history of pre-owned retail installment contracts: payments, returned payments, late charges, fees and waivers, due-date changes, extensions, payoff quotes, lien releases, refund credits, notices and repossession charges and sales.

    Every criterion is optional; supply whichever reference numbers are already known. All matching
    entries are returned with their full details, or a short notice when nothing matches.

    Args:
        preowned_txn_id: Reference number - the reference number of this preowned transaction entry itself; leave "" if unknown.
        preowned_contract_id: Reference number - the reference number of the linked preowned contract; leave "" if unknown.
        customer_id: Reference number - the customer reference number; leave "" if unknown.
        reversed_txn_id: Reference number - the reference number of the payment that was dishonoured; leave "" if unknown.
        payment_txn_id: Reference number - the reference number of the payment from which a fee portion was applied; leave "" if unknown.
        waived_txn_id: Reference number - the reference number of the fee or charge that was waived; leave "" if unknown.
        care_contract_id: Reference number - the reference number of the Kestrel Care plan; leave "" if unknown.
    """
    match = {k: v for k, v in {"preowned_txn_id": preowned_txn_id, "preowned_contract_id": preowned_contract_id, "customer_id": customer_id, "reversed_txn_id": reversed_txn_id, "payment_txn_id": payment_txn_id, "waived_txn_id": waived_txn_id, "care_contract_id": care_contract_id}.items() if v}
    rows = ctx.find("preowned_transactions", **match)
    return str(rows) if rows else f"No matching entries found for {match}."


@tool(owner="agent", rw="read")
def find_preowned_requests(ctx: ToolContext, preowned_request_id: str = "", customer_id: str = "", preowned_contract_id: str = "") -> str:
    """Look up requests on pre-owned retail installment contracts that wait on the customer's own signature or action, with their current status.

    Every criterion is optional; supply whichever reference numbers are already known. All matching
    entries are returned with their full details, or a short notice when nothing matches.

    Args:
        preowned_request_id: Reference number - the reference number of this preowned request entry itself; leave "" if unknown.
        customer_id: Reference number - the customer reference number; leave "" if unknown.
        preowned_contract_id: Reference number - the reference number of the linked preowned contract; leave "" if unknown.
    """
    match = {k: v for k, v in {"preowned_request_id": preowned_request_id, "customer_id": customer_id, "preowned_contract_id": preowned_contract_id}.items() if v}
    rows = ctx.find("preowned_requests", **match)
    return str(rows) if rows else f"No matching entries found for {match}."


@tool(owner="agent", rw="read")
def find_balloon_contracts(ctx: ToolContext, balloon_contract_id: str = "", customer_id: str = "") -> str:
    """Look up Kestrel Advantage balloon contracts: credit tier, status, vehicle, rate, monthly and balloon installments, maturity, return option and mileage allowance, balances, days past due, state rules recorded at booking, repossession and return dates and title status.

    Every criterion is optional; supply whichever reference numbers are already known. All matching
    entries are returned with their full details, or a short notice when nothing matches.

    Args:
        balloon_contract_id: Reference number - the reference number of this balloon contract entry itself; leave "" if unknown.
        customer_id: Reference number - the customer reference number; leave "" if unknown.
    """
    match = {k: v for k, v in {"balloon_contract_id": balloon_contract_id, "customer_id": customer_id}.items() if v}
    rows = ctx.find("balloon_contracts", **match)
    return str(rows) if rows else f"No matching entries found for {match}."


@tool(owner="agent", rw="read")
def find_balloon_transactions(ctx: ToolContext, balloon_txn_id: str = "", balloon_contract_id: str = "", customer_id: str = "", reversed_txn_id: str = "", payment_txn_id: str = "", waived_txn_id: str = "", care_contract_id: str = "") -> str:
    """Look up the posting history of balloon contracts: payments, returned payments, fees and waivers, due-date changes, extensions, payoff quotes, maturity elections, refinances, return inspections and charges, lien releases, notices and repossession activity.

    Every criterion is optional; supply whichever reference numbers are already known. All matching
    entries are returned with their full details, or a short notice when nothing matches.

    Args:
        balloon_txn_id: Reference number - the reference number of this balloon transaction entry itself; leave "" if unknown.
        balloon_contract_id: Reference number - the reference number of the linked balloon contract; leave "" if unknown.
        customer_id: Reference number - the customer reference number; leave "" if unknown.
        reversed_txn_id: Reference number - the reference number of the payment that was dishonoured; leave "" if unknown.
        payment_txn_id: Reference number - the reference number of the payment from which a fee portion was applied; leave "" if unknown.
        waived_txn_id: Reference number - the reference number of the fee or charge that was waived; leave "" if unknown.
        care_contract_id: Reference number - the reference number of the Kestrel Care plan; leave "" if unknown.
    """
    match = {k: v for k, v in {"balloon_txn_id": balloon_txn_id, "balloon_contract_id": balloon_contract_id, "customer_id": customer_id, "reversed_txn_id": reversed_txn_id, "payment_txn_id": payment_txn_id, "waived_txn_id": waived_txn_id, "care_contract_id": care_contract_id}.items() if v}
    rows = ctx.find("balloon_transactions", **match)
    return str(rows) if rows else f"No matching entries found for {match}."


@tool(owner="agent", rw="read")
def find_balloon_requests(ctx: ToolContext, balloon_request_id: str = "", customer_id: str = "", balloon_contract_id: str = "") -> str:
    """Look up requests on balloon contracts that wait on the customer's own signature or action, such as extension agreements, vehicle returns, inspection disputes and alternate-address title releases.

    Every criterion is optional; supply whichever reference numbers are already known. All matching
    entries are returned with their full details, or a short notice when nothing matches.

    Args:
        balloon_request_id: Reference number - the reference number of this balloon request entry itself; leave "" if unknown.
        customer_id: Reference number - the customer reference number; leave "" if unknown.
        balloon_contract_id: Reference number - the reference number of the linked balloon contract; leave "" if unknown.
    """
    match = {k: v for k, v in {"balloon_request_id": balloon_request_id, "customer_id": customer_id, "balloon_contract_id": balloon_contract_id}.items() if v}
    rows = ctx.find("balloon_requests", **match)
    return str(rows) if rows else f"No matching entries found for {match}."


@tool(owner="agent", rw="read")
def find_lease_contracts(ctx: ToolContext, lease_contract_id: str = "", customer_id: str = "") -> str:
    """Look up Kestrel closed-end consumer leases: tier, status, vehicle, the lease disclosures (capitalized cost, residual value, money factor, payments, mileage allowance, excess mileage rate, disposition and purchase option fees), balances, days past due, maturity, extension, turn-in and purchase details.

    Every criterion is optional; supply whichever reference numbers are already known. All matching
    entries are returned with their full details, or a short notice when nothing matches.

    Args:
        lease_contract_id: Reference number - the reference number of this lease contract entry itself; leave "" if unknown.
        customer_id: Reference number - the customer reference number; leave "" if unknown.
    """
    match = {k: v for k, v in {"lease_contract_id": lease_contract_id, "customer_id": customer_id}.items() if v}
    rows = ctx.find("lease_contracts", **match)
    return str(rows) if rows else f"No matching entries found for {match}."


@tool(owner="agent", rw="read")
def find_lease_transactions(ctx: ToolContext, lease_txn_id: str = "", lease_contract_id: str = "", customer_id: str = "", reversed_txn_id: str = "", payment_txn_id: str = "", waived_txn_id: str = "", care_contract_id: str = "") -> str:
    """Look up the posting history of leases: payments and how they were applied, returned payments, late charges and waivers, purchase and termination quotes, end-of-term charges and waivers, security deposit handling, maturity extensions, refund credits and notices.

    Every criterion is optional; supply whichever reference numbers are already known. All matching
    entries are returned with their full details, or a short notice when nothing matches.

    Args:
        lease_txn_id: Reference number - the reference number of this lease transaction entry itself; leave "" if unknown.
        lease_contract_id: Reference number - the reference number of the linked lease contract; leave "" if unknown.
        customer_id: Reference number - the customer reference number; leave "" if unknown.
        reversed_txn_id: Reference number - the reference number of the payment that was dishonoured; leave "" if unknown.
        payment_txn_id: Reference number - the reference number of the payment from which a fee portion was applied; leave "" if unknown.
        waived_txn_id: Reference number - the reference number of the fee or charge that was waived; leave "" if unknown.
        care_contract_id: Reference number - the reference number of the Kestrel Care plan; leave "" if unknown.
    """
    match = {k: v for k, v in {"lease_txn_id": lease_txn_id, "lease_contract_id": lease_contract_id, "customer_id": customer_id, "reversed_txn_id": reversed_txn_id, "payment_txn_id": payment_txn_id, "waived_txn_id": waived_txn_id, "care_contract_id": care_contract_id}.items() if v}
    rows = ctx.find("lease_transactions", **match)
    return str(rows) if rows else f"No matching entries found for {match}."


@tool(owner="agent", rw="read")
def find_lease_inspections(ctx: ToolContext, lease_inspection_id: str = "", lease_contract_id: str = "", customer_id: str = "") -> str:
    """Look up vehicle inspection reports for leases, advance or final, with the inspection date, odometer, tire tread and report reference.

    Every criterion is optional; supply whichever reference numbers are already known. All matching
    entries are returned with their full details, or a short notice when nothing matches.

    Args:
        lease_inspection_id: Reference number - the reference number of the inspection report; leave "" if unknown.
        lease_contract_id: Reference number - the reference number of the linked lease contract; leave "" if unknown.
        customer_id: Reference number - the customer reference number; leave "" if unknown.
    """
    match = {k: v for k, v in {"lease_inspection_id": lease_inspection_id, "lease_contract_id": lease_contract_id, "customer_id": customer_id}.items() if v}
    rows = ctx.find("lease_inspections", **match)
    return str(rows) if rows else f"No matching entries found for {match}."


@tool(owner="agent", rw="read")
def find_lease_wear_items(ctx: ToolContext, lease_wear_item_id: str = "", lease_contract_id: str = "", customer_id: str = "", lease_inspection_id: str = "", original_wear_item_id: str = "") -> str:
    """Look up the individual wear items recorded on lease inspection reports, with category, position, severity, scheduled charge and any adjustment after a dispute.

    Every criterion is optional; supply whichever reference numbers are already known. All matching
    entries are returned with their full details, or a short notice when nothing matches.

    Args:
        lease_wear_item_id: Reference number - the reference number of this lease wear item entry itself; leave "" if unknown.
        lease_contract_id: Reference number - the reference number of the linked lease contract; leave "" if unknown.
        customer_id: Reference number - the customer reference number; leave "" if unknown.
        lease_inspection_id: Reference number - the reference number of the inspection report; leave "" if unknown.
        original_wear_item_id: Reference number - the reference number of the assessed wear item that an adjustment changes; leave "" if unknown.
    """
    match = {k: v for k, v in {"lease_wear_item_id": lease_wear_item_id, "lease_contract_id": lease_contract_id, "customer_id": customer_id, "lease_inspection_id": lease_inspection_id, "original_wear_item_id": original_wear_item_id}.items() if v}
    rows = ctx.find("lease_wear_items", **match)
    return str(rows) if rows else f"No matching entries found for {match}."


@tool(owner="agent", rw="read")
def find_lease_requests(ctx: ToolContext, lease_request_id: str = "", customer_id: str = "", lease_contract_id: str = "") -> str:
    """Look up lease requests that wait on the lessee's own signature or action, such as turn-in and inspection appointments, purchase options, early terminations, pull-aheads, inspection disputes and dealer purchase authorizations.

    Every criterion is optional; supply whichever reference numbers are already known. All matching
    entries are returned with their full details, or a short notice when nothing matches.

    Args:
        lease_request_id: Reference number - the reference number of this lease request entry itself; leave "" if unknown.
        customer_id: Reference number - the customer reference number; leave "" if unknown.
        lease_contract_id: Reference number - the reference number of the linked lease contract; leave "" if unknown.
    """
    match = {k: v for k, v in {"lease_request_id": lease_request_id, "customer_id": customer_id, "lease_contract_id": lease_contract_id}.items() if v}
    rows = ctx.find("lease_requests", **match)
    return str(rows) if rows else f"No matching entries found for {match}."


@tool(owner="agent", rw="read")
def find_fleet_units(ctx: ToolContext, fleet_unit_id: str = "", customer_id: str = "") -> str:
    """Look up commercial fleet unit lease schedules under a business's master lease agreement: program tier, lease type, vehicle, capitalized cost, depreciation and lease rates, book value, charges due, term dates, termination, sale and purchase details.

    Every criterion is optional; supply whichever reference numbers are already known. All matching
    entries are returned with their full details, or a short notice when nothing matches.

    Args:
        fleet_unit_id: Reference number - the reference number of this fleet unit entry itself; leave "" if unknown.
        customer_id: Reference number - the customer reference number; leave "" if unknown.
    """
    match = {k: v for k, v in {"fleet_unit_id": fleet_unit_id, "customer_id": customer_id}.items() if v}
    rows = ctx.find("fleet_units", **match)
    return str(rows) if rows else f"No matching entries found for {match}."


@tool(owner="agent", rw="read")
def find_fleet_transactions(ctx: ToolContext, fleet_txn_id: str = "", fleet_unit_id: str = "", customer_id: str = "", waived_txn_id: str = "") -> str:
    """Look up the billing history of fleet units: rental invoices and their components, depreciation, business payments, late charges, unit charges and waivers, sale settlements and terminal rental adjustments, purchase quotes and settlements, title transfers and refunds.

    Every criterion is optional; supply whichever reference numbers are already known. All matching
    entries are returned with their full details, or a short notice when nothing matches.

    Args:
        fleet_txn_id: Reference number - the reference number of this fleet transaction entry itself; leave "" if unknown.
        fleet_unit_id: Reference number - the reference number of the linked fleet unit; leave "" if unknown.
        customer_id: Reference number - the customer reference number; leave "" if unknown.
        waived_txn_id: Reference number - the reference number of the fee or charge that was waived; leave "" if unknown.
    """
    match = {k: v for k, v in {"fleet_txn_id": fleet_txn_id, "fleet_unit_id": fleet_unit_id, "customer_id": customer_id, "waived_txn_id": waived_txn_id}.items() if v}
    rows = ctx.find("fleet_transactions", **match)
    return str(rows) if rows else f"No matching entries found for {match}."


@tool(owner="agent", rw="read")
def find_fleet_requests(ctx: ToolContext, fleet_request_id: str = "", customer_id: str = "", fleet_unit_id: str = "") -> str:
    """Look up fleet requests that wait on a business's authorized signer, such as delivery acceptance, termination notices, purchase options and unit orders.

    Every criterion is optional; supply whichever reference numbers are already known. All matching
    entries are returned with their full details, or a short notice when nothing matches.

    Args:
        fleet_request_id: Reference number - the reference number of this fleet request entry itself; leave "" if unknown.
        customer_id: Reference number - the customer reference number; leave "" if unknown.
        fleet_unit_id: Reference number - the reference number of the linked fleet unit; leave "" if unknown.
    """
    match = {k: v for k, v in {"fleet_request_id": fleet_request_id, "customer_id": customer_id, "fleet_unit_id": fleet_unit_id}.items() if v}
    rows = ctx.find("fleet_requests", **match)
    return str(rows) if rows else f"No matching entries found for {match}."


@tool(owner="agent", rw="read")
def find_care_contracts(ctx: ToolContext, care_contract_id: str = "", customer_id: str = "") -> str:
    """Look up Kestrel Care vehicle service contracts: plan, status, covered vehicle, term in months and miles, deductible, price, how it was financed, remaining aggregate limit, claims paid, transfers and cancellation details.

    Every criterion is optional; supply whichever reference numbers are already known. All matching
    entries are returned with their full details, or a short notice when nothing matches.

    Args:
        care_contract_id: Reference number - the reference number of this care contract entry itself; leave "" if unknown.
        customer_id: Reference number - the customer reference number; leave "" if unknown.
    """
    match = {k: v for k, v in {"care_contract_id": care_contract_id, "customer_id": customer_id}.items() if v}
    rows = ctx.find("care_contracts", **match)
    return str(rows) if rows else f"No matching entries found for {match}."


@tool(owner="agent", rw="read")
def find_care_transactions(ctx: ToolContext, care_txn_id: str = "", care_contract_id: str = "", customer_id: str = "") -> str:
    """Look up Kestrel Care plan activity: limit establishment, cancellation refunds and where they were sent, and transfer fees.

    Every criterion is optional; supply whichever reference numbers are already known. All matching
    entries are returned with their full details, or a short notice when nothing matches.

    Args:
        care_txn_id: Reference number - the reference number of this care transaction entry itself; leave "" if unknown.
        care_contract_id: Reference number - the reference number of the Kestrel Care plan; leave "" if unknown.
        customer_id: Reference number - the customer reference number; leave "" if unknown.
    """
    match = {k: v for k, v in {"care_txn_id": care_txn_id, "care_contract_id": care_contract_id, "customer_id": customer_id}.items() if v}
    rows = ctx.find("care_transactions", **match)
    return str(rows) if rows else f"No matching entries found for {match}."


@tool(owner="agent", rw="read")
def find_care_claims(ctx: ToolContext, care_claim_id: str = "", care_contract_id: str = "", customer_id: str = "", parent_claim_id: str = "") -> str:
    """Look up Kestrel Care repair claims: repair order, failed component group, repair facility, estimate, authorization, denial reason and payment.

    Every criterion is optional; supply whichever reference numbers are already known. All matching
    entries are returned with their full details, or a short notice when nothing matches.

    Args:
        care_claim_id: Reference number - the reference number of this care claim entry itself; leave "" if unknown.
        care_contract_id: Reference number - the reference number of the Kestrel Care plan; leave "" if unknown.
        customer_id: Reference number - the customer reference number; leave "" if unknown.
        parent_claim_id: Reference number - the reference number of the claim opening that an authorization, denial or payment decides; leave "" if unknown.
    """
    match = {k: v for k, v in {"care_claim_id": care_claim_id, "care_contract_id": care_contract_id, "customer_id": customer_id, "parent_claim_id": parent_claim_id}.items() if v}
    rows = ctx.find("care_claims", **match)
    return str(rows) if rows else f"No matching entries found for {match}."


@tool(owner="agent", rw="read")
def find_care_requests(ctx: ToolContext, care_request_id: str = "", customer_id: str = "", care_contract_id: str = "") -> str:
    """Look up Kestrel Care requests that wait on the holder's signature, such as cancellations and transfers.

    Every criterion is optional; supply whichever reference numbers are already known. All matching
    entries are returned with their full details, or a short notice when nothing matches.

    Args:
        care_request_id: Reference number - the reference number of this care request entry itself; leave "" if unknown.
        customer_id: Reference number - the customer reference number; leave "" if unknown.
        care_contract_id: Reference number - the reference number of the Kestrel Care plan; leave "" if unknown.
    """
    match = {k: v for k, v in {"care_request_id": care_request_id, "customer_id": customer_id, "care_contract_id": care_contract_id}.items() if v}
    rows = ctx.find("care_requests", **match)
    return str(rows) if rows else f"No matching entries found for {match}."


@tool(owner="agent", rw="read")
def find_floorplan_lines(ctx: ToolContext, floorplan_line_id: str = "", customer_id: str = "") -> str:
    """Look up dealer wholesale floorplan lines: risk grade, status, new and used line amounts, outstanding principal, interest due, rate and audit dates.

    Every criterion is optional; supply whichever reference numbers are already known. All matching
    entries are returned with their full details, or a short notice when nothing matches.

    Args:
        floorplan_line_id: Reference number - the reference number of this floorplan line entry itself; leave "" if unknown.
        customer_id: Reference number - the customer reference number; leave "" if unknown.
    """
    match = {k: v for k, v in {"floorplan_line_id": floorplan_line_id, "customer_id": customer_id}.items() if v}
    rows = ctx.find("floorplan_lines", **match)
    return str(rows) if rows else f"No matching entries found for {match}."


@tool(owner="agent", rw="read")
def find_floorplan_transactions(ctx: ToolContext, floorplan_txn_id: str = "", floorplan_line_id: str = "", customer_id: str = "") -> str:
    """Look up dealer floorplan activity: unit advances, payoffs, curtailments, interest billing and payment, fees and audit results.

    Every criterion is optional; supply whichever reference numbers are already known. All matching
    entries are returned with their full details, or a short notice when nothing matches.

    Args:
        floorplan_txn_id: Reference number - the reference number of this floorplan transaction entry itself; leave "" if unknown.
        floorplan_line_id: Reference number - the reference number of the linked floorplan line; leave "" if unknown.
        customer_id: Reference number - the customer reference number; leave "" if unknown.
    """
    match = {k: v for k, v in {"floorplan_txn_id": floorplan_txn_id, "floorplan_line_id": floorplan_line_id, "customer_id": customer_id}.items() if v}
    rows = ctx.find("floorplan_transactions", **match)
    return str(rows) if rows else f"No matching entries found for {match}."


@tool(owner="agent", rw="read")
def find_identity_verifications(ctx: ToolContext, verification_id: str = "", customer_id: str = "") -> str:
    """Look up the outcome of identity verification for a customer on this contact.

    Every criterion is optional; supply whichever reference numbers are already known. All matching
    entries are returned with their full details, or a short notice when nothing matches.

    Args:
        verification_id: Reference number - the reference number of an identity verification outcome; leave "" if unknown.
        customer_id: Reference number - the customer reference number; leave "" if unknown.
    """
    match = {k: v for k, v in {"verification_id": verification_id, "customer_id": customer_id}.items() if v}
    rows = ctx.find("identity_verifications", **match)
    return str(rows) if rows else f"No matching entries found for {match}."


@tool(owner="agent", rw="read")
def find_handoff_log(ctx: ToolContext, handoff_id: str = "", customer_id: str = "") -> str:
    """Look up transfers of a customer to a human representative and their recorded reason.

    Every criterion is optional; supply whichever reference numbers are already known. All matching
    entries are returned with their full details, or a short notice when nothing matches.

    Args:
        handoff_id: Reference number - the reference number of a handoff to a human representative; leave "" if unknown.
        customer_id: Reference number - the customer reference number; leave "" if unknown.
    """
    match = {k: v for k, v in {"handoff_id": handoff_id, "customer_id": customer_id}.items() if v}
    rows = ctx.find("handoff_log", **match)
    return str(rows) if rows else f"No matching entries found for {match}."

@tool(owner="agent", rw="read")
def find_customers(ctx: ToolContext, customer_id: str = "", phone_number: str = "", email: str = "", name: str = "") -> str:
    """Find the Kestrel customer profile a call is about. Search by the customer reference number, or by
    what the caller can naturally state: the phone number on the profile, the email on the profile or the
    customer's name (a person's full name, or a business's legal name). Every criterion is optional; give
    whichever are known. The profile returned carries the customer type, contact details, billing ZIP and
    mailing address, the last four digits of the Social Security number or EIN, the date of birth for an
    individual, the date the relationship began, a business's authorized signer and any bankruptcy status.
    Finding a profile does not verify the caller's identity.

    Args:
        customer_id: Reference number - the customer reference number; leave "" if unknown.
        phone_number: The phone number the caller gives, 10 digits; leave "" if not provided.
        email: The email address the caller gives; leave "" if not provided.
        name: The full name or business legal name the caller gives; leave "" if not provided.
    """
    match = {k: v for k, v in {"customer_id": customer_id, "phone_number": phone_number,
                               "email": email, "name": name}.items() if v}
    if not match:
        return "Error: provide at least one reference number or detail to find the customer."
    rows = ctx.fuzzy_find("customers", **match)
    if not rows:
        return f"No customer matches {match}."
    if len(rows) > 1:
        return f"Error: {len(rows)} customers match {match}; ask for one more detail to tell them apart."
    return str(rows[0])


@tool(owner="agent", rw="write")
def verify_customer_identity(ctx: ToolContext, customer_id: str, phone_number: str = "", email: str = "",
                             tax_id_last4: str = "", date_of_birth: str = "", billing_zip: str = "") -> str:
    """Verify the caller's identity and record the outcome. No account information may be discussed and no
    account business transacted until verification has passed on the contact. This tool performs the
    comparison itself: it compares each piece of identity information the caller states with the customer
    profile, counts how many match, and passes only when at least 3 match. The customer reference number
    only retrieves the profile and never counts as a match. Callers usually state only some of these
    details, so pass exactly what was said and leave the rest blank. The outcome is recorded; if a first
    attempt fails and a later attempt with more information passes, the pass stands.

    Args:
        customer_id: Reference number - the customer reference number read from the customer profile lookup. Required; used only to retrieve the profile and not counted as a match.
        phone_number: The phone number the caller states, 10 digits without punctuation; leave "" if not stated.
        email: The email address the caller states; leave "" if not stated.
        tax_id_last4: The last four digits of the caller's Social Security number, or of the business's EIN, as stated; leave "" if not stated.
        date_of_birth: The individual caller's date of birth as stated, in YYYY-MM-DD form; leave "" if not stated or for a business.
        billing_zip: The 5-digit ZIP code of the billing address as stated; leave "" if not stated.
    """
    if not customer_id:
        return "Error: customer_id is required; find the customer profile first and pass its reference number."
    rows = ctx.find("customers", customer_id=customer_id)
    if not rows:
        return f"Error: no customer {customer_id}; cannot verify."
    rec = rows[0]
    supplied = {"phone_number": phone_number, "email": email, "tax_id_last4": tax_id_last4,
                "date_of_birth": date_of_birth, "billing_zip": billing_zip}
    matched = sum(1 for field, value in supplied.items()
                  if value and str(rec.get(field) or "").strip().lower() == str(value).strip().lower())
    verified = matched >= 3
    rid = ctx.make_id("ver_", customer_id)
    prior = ctx.find("identity_verifications", verification_id=rid)
    verified = verified or bool(prior and prior[0].get("verified"))
    if prior:
        ctx.update("identity_verifications", rid, verified=verified, verified_at=ctx.now())
    else:
        ctx.create("identity_verifications", rid, verification_id=rid, customer_id=customer_id,
                   verified=verified, verified_at=ctx.now())
    return (f"Identity verified for {customer_id} ({matched} detail(s) matched)." if verified
            else f"Identity NOT verified for {customer_id} (only {matched} of the required 3 details matched). Ask the caller for another detail on file and try again.")


@tool(owner="agent", rw="write")
def transfer_to_human_agent(ctx: ToolContext, customer_id: str, reason: str) -> str:
    """Transfer the customer to a human representative and record the transfer and its reason. Use it when
    no Kestrel policy can resolve what the customer needs, or when the customer has explicitly asked to
    speak with a human representative at least 2 times on the contact.

    Args:
        customer_id: Reference number - the customer reference number read from the customer profile lookup; the profile must exist.
        reason: The reason for the transfer, exactly one of POLICY_NOT_COVERED or CUSTOMER_REQUESTED, never free text. POLICY_NOT_COVERED - current policy offers no way to resolve the request; CUSTOMER_REQUESTED - the customer has explicitly asked for a human representative at least 2 times.
    """
    allowed = {"POLICY_NOT_COVERED", "CUSTOMER_REQUESTED"}
    if reason not in allowed:
        return f"Error: unknown handoff reason '{reason}'. Valid: {', '.join(sorted(allowed))}."
    if not ctx.find("customers", customer_id=customer_id):
        return f"Error: no customer {customer_id}; cannot record the transfer."
    rid = ctx.make_id("hof_", customer_id, reason)
    ctx.create("handoff_log", rid, handoff_id=rid, customer_id=customer_id, reason=reason, created_at=ctx.now())
    return f"Transfer to a human representative recorded for {customer_id} ({reason})."

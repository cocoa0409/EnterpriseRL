"""Shared tools for env_0037_residential_hvac_company (Harbison Heating & Air).
Output of the erl-scenario-blueprint skill.

Every tool here is a SHARE tool: always present in its owner's tool list.
  - One record finder per table (the customers finder doubles as the identity entry).
  - The identity-verification write (threshold K = 2 matching credentials).
  - The transfer-to-human write (repeat-request threshold R = 2).
Customer-originated writes live as hidden task tools in each difficulty's task_tools.py.
"""

from erlbench import ToolContext, tool


def _pick(**criteria):
    # Keep only the criteria the caller actually supplied.
    return {k: v for k, v in criteria.items() if v}


# --------------------------------------------------------------------------- #
# Customer profile and equipment register                                      #
# --------------------------------------------------------------------------- #

@tool(owner="agent", rw="read")
def find_customers(ctx: ToolContext, customer_id: str = "", name: str = "", phone_number: str = "",
                   email: str = "", service_address: str = "") -> str:
    """Look up a Harbison homeowner profile to establish whose account this conversation is about.

    Search by the customer reference number, or by whatever the caller naturally tells you: the
    name on the account, the phone number, the email address or the street line of the service
    address. Every criterion is optional; supply whichever you have, and add one more if several
    profiles match. The profile shows the account holder's contact details, the service address and
    ZIP code, the date the profile was opened and any courtesy discount program (senior, military
    veteran or first responder) on file. Finding a profile does not confirm that the caller is the
    account holder; identity must still be verified separately.

    Args:
        customer_id: Customer reference number, if already known; leave "" if unknown.
        name: Full name on the account as the caller states it; leave "" if not provided.
        phone_number: Phone number on the account, 10 digits (e.g. "6145550142"); leave "" if not provided.
        email: Email address on the account; leave "" if not provided.
        service_address: Street line of the service address, house number and street (e.g. "4417 Kenny Rd"); leave "" if not provided.
    """
    match = _pick(customer_id=customer_id, name=name, phone_number=phone_number,
                  email=email, service_address=service_address)
    if not match:
        return "Error: provide at least one detail to look the customer up."
    rows = ctx.fuzzy_find("customers", **match)
    if not rows:
        return f"No customer profile matches {match}."
    if len(rows) > 1:
        return (f"Error: {len(rows)} customer profiles match {match}; ask the caller for one more "
                "detail to tell them apart.")
    return str(rows[0])


@tool(owner="agent", rw="read")
def find_equipment(ctx: ToolContext, equipment_id: str = "", customer_id: str = "") -> str:
    """List the heating, cooling and water-heating equipment registered at a customer's home.

    Each unit shows its type (air conditioner, heat pump, furnace, air handler, ductless system,
    boiler or water heater), brand, model and serial number, installation date, whether Harbison
    installed it, its refrigerant, its nominal capacity in tons and whether it is still in service.
    Search by the unit's reference number or by the customer reference number; both are optional.

    Args:
        equipment_id: Reference number of one equipment unit; leave "" if unknown.
        customer_id: Customer reference number, to list every unit at that home; leave "" if unknown.
    """
    match = _pick(equipment_id=equipment_id, customer_id=customer_id)
    rows = ctx.find("equipment", **match)
    return str(rows) if rows else f"No equipment found for {match}."


# --------------------------------------------------------------------------- #
# Comfort Club maintenance agreements                                          #
# --------------------------------------------------------------------------- #

@tool(owner="agent", rw="read")
def find_plan_agreements(ctx: ToolContext, agreement_id: str = "", customer_id: str = "") -> str:
    """Retrieve Comfort Club maintenance agreements.

    An agreement shows the tier, its status, the enrollment date, the current term's start and end,
    whether dues are billed annually or monthly, how many systems are enrolled, whether it renews
    automatically, the channel it was enrolled through, the count of consecutive terms, any locked
    renewal rate, the dues balance, the maintenance visits still available this term and any
    covered-repair benefit remaining. Search by agreement reference number or customer reference
    number.

    Args:
        agreement_id: Reference number of the agreement; leave "" if unknown.
        customer_id: Customer reference number of the member; leave "" if unknown.
    """
    match = _pick(agreement_id=agreement_id, customer_id=customer_id)
    rows = ctx.find("plan_agreements", **match)
    return str(rows) if rows else f"No Comfort Club agreement found for {match}."


@tool(owner="agent", rw="read")
def find_plan_billing_entries(ctx: ToolContext, billing_entry_id: str = "", agreement_id: str = "",
                              customer_id: str = "", source_entry_id: str = "",
                              ticket_id: str = "") -> str:
    """Show the dues history of a Comfort Club agreement: every dues and fee charge, payment, credit
    and refund payout, with its billing month, amount and posting date.

    Payments and payouts carry their method and confirmation number; credits and payouts point to
    the entry they settle, and a response-guarantee credit names the service call it was earned on.
    Any of the reference numbers below can be used; all are optional.

    Args:
        billing_entry_id: Reference number of one dues entry; leave "" if unknown.
        agreement_id: Agreement reference number; leave "" if unknown.
        customer_id: Customer reference number; leave "" if unknown.
        source_entry_id: Reference number of an earlier entry, to find what offsets or settles it; leave "" if unknown.
        ticket_id: Service call reference number, to find a response-guarantee credit earned on it; leave "" if unknown.
    """
    match = _pick(billing_entry_id=billing_entry_id, agreement_id=agreement_id,
                  customer_id=customer_id, source_entry_id=source_entry_id, ticket_id=ticket_id)
    rows = ctx.find("plan_billing_entries", **match)
    return str(rows) if rows else f"No Comfort Club dues entries found for {match}."


@tool(owner="agent", rw="read")
def find_plan_service_entries(ctx: ToolContext, service_entry_id: str = "", agreement_id: str = "",
                              customer_id: str = "", equipment_id: str = "", ticket_id: str = "",
                              source_line_id: str = "") -> str:
    """Show a member's maintenance-visit and covered-repair history.

    Entries cover visits granted for a term, tune-ups completed or forfeited (with the unit, the
    season and the visit date), covered-repair benefit granted for a term, and covered-repair
    amounts drawn against a specific service call and invoice line. Search by any reference number
    below; all are optional.

    Args:
        service_entry_id: Reference number of one visit or coverage entry; leave "" if unknown.
        agreement_id: Agreement reference number; leave "" if unknown.
        customer_id: Customer reference number; leave "" if unknown.
        equipment_id: Equipment unit reference number, to see visits on that unit; leave "" if unknown.
        ticket_id: Service call reference number, to see coverage drawn for it; leave "" if unknown.
        source_line_id: Invoice line reference number, to see coverage drawn for that line; leave "" if unknown.
    """
    match = _pick(service_entry_id=service_entry_id, agreement_id=agreement_id,
                  customer_id=customer_id, equipment_id=equipment_id, ticket_id=ticket_id,
                  source_line_id=source_line_id)
    rows = ctx.find("plan_service_entries", **match)
    return str(rows) if rows else f"No Comfort Club visit or coverage entries found for {match}."


@tool(owner="agent", rw="read")
def find_plan_change_requests(ctx: ToolContext, plan_request_id: str = "", customer_id: str = "",
                              agreement_id: str = "") -> str:
    """Look up cancellation and renewal-downgrade requests a member has made on a Comfort Club
    agreement, with the tier requested for a downgrade, whether the member has confirmed or withdrawn
    it, and when it was received.

    Args:
        plan_request_id: Reference number of the request; leave "" if unknown.
        customer_id: Customer reference number; leave "" if unknown.
        agreement_id: Agreement reference number; leave "" if unknown.
    """
    match = _pick(plan_request_id=plan_request_id, customer_id=customer_id, agreement_id=agreement_id)
    rows = ctx.find("plan_change_requests", **match)
    return str(rows) if rows else f"No Comfort Club change requests found for {match}."


# --------------------------------------------------------------------------- #
# Harbison protection contracts (extended warranties)                         #
# --------------------------------------------------------------------------- #

@tool(owner="agent", rw="read")
def find_warranty_contracts(ctx: ToolContext, contract_id: str = "", customer_id: str = "",
                            equipment_id: str = "", paired_equipment_id: str = "",
                            install_id: str = "", transferred_from_contract_id: str = "") -> str:
    """Retrieve Harbison protection contracts on a homeowner's equipment.

    A contract shows the protection tier, its status, the covered unit (and the paired unit of a
    matched system), the installation it came with, how and when it was bought, the coverage start
    and end dates, the price paid, the claim benefit still available, the balance owed and, for a
    contract received on a home sale, the seller's contract it came from. Every criterion is
    optional.

    Args:
        contract_id: Reference number of the protection contract; leave "" if unknown.
        customer_id: Customer reference number of the holder; leave "" if unknown.
        equipment_id: Reference number of the primary covered unit; leave "" if unknown.
        paired_equipment_id: Reference number of the paired unit of a matched system; leave "" if unknown.
        install_id: Reference number of the installation project; leave "" if unknown.
        transferred_from_contract_id: Reference number of a seller's contract, to find the buyer's contract issued from it; leave "" if unknown.
    """
    match = _pick(contract_id=contract_id, customer_id=customer_id, equipment_id=equipment_id,
                  paired_equipment_id=paired_equipment_id, install_id=install_id,
                  transferred_from_contract_id=transferred_from_contract_id)
    rows = ctx.find("warranty_contracts", **match)
    return str(rows) if rows else f"No protection contracts found for {match}."


@tool(owner="agent", rw="read")
def find_warranty_claim_entries(ctx: ToolContext, claim_entry_id: str = "", contract_id: str = "",
                                customer_id: str = "", claim_id: str = "", ticket_id: str = "",
                                equipment_id: str = "") -> str:
    """Show the claim history of a protection contract: claims filed (failed unit, component and
    diagnosis date), each decision (outcome, governing reason and approved amount, original or
    appeal), each payout (parts, labor, refrigerant or unit replacement) and the claim benefit
    granted to the contract. All criteria are optional.

    Args:
        claim_entry_id: Reference number of one claim entry; leave "" if unknown.
        contract_id: Protection contract reference number; leave "" if unknown.
        customer_id: Customer reference number; leave "" if unknown.
        claim_id: Claim reference number, to see everything recorded on that claim; leave "" if unknown.
        ticket_id: Service call reference number on which the failure was diagnosed; leave "" if unknown.
        equipment_id: Reference number of the failed unit; leave "" if unknown.
    """
    match = _pick(claim_entry_id=claim_entry_id, contract_id=contract_id, customer_id=customer_id,
                  claim_id=claim_id, ticket_id=ticket_id, equipment_id=equipment_id)
    rows = ctx.find("warranty_claim_entries", **match)
    return str(rows) if rows else f"No protection claim entries found for {match}."


@tool(owner="agent", rw="read")
def find_warranty_billing_entries(ctx: ToolContext, warranty_billing_id: str = "",
                                  contract_id: str = "", customer_id: str = "", claim_id: str = "",
                                  ticket_id: str = "", source_billing_id: str = "") -> str:
    """Show the billing history of a protection contract: the contract price, inspection fee,
    claim service fees and transfer fee charged, payments received, credits issued and refund
    payouts, each with its amount and posting date. All criteria are optional.

    Args:
        warranty_billing_id: Reference number of one billing entry; leave "" if unknown.
        contract_id: Protection contract reference number; leave "" if unknown.
        customer_id: Customer reference number; leave "" if unknown.
        claim_id: Claim reference number, to see the service fee charged or waived on it; leave "" if unknown.
        ticket_id: Service call reference number, to see the claim service fee charged for that visit; leave "" if unknown.
        source_billing_id: Reference number of an earlier billing entry, to find what offsets or settles it; leave "" if unknown.
    """
    match = _pick(warranty_billing_id=warranty_billing_id, contract_id=contract_id,
                  customer_id=customer_id, claim_id=claim_id, ticket_id=ticket_id,
                  source_billing_id=source_billing_id)
    rows = ctx.find("warranty_billing_entries", **match)
    return str(rows) if rows else f"No protection billing entries found for {match}."


@tool(owner="agent", rw="read")
def find_warranty_change_requests(ctx: ToolContext, warranty_request_id: str = "",
                                  customer_id: str = "", contract_id: str = "",
                                  buyer_customer_id: str = "") -> str:
    """Look up cancellation and home-sale transfer requests on protection contracts, including the
    closing date of the sale and the buyer's profile for a transfer, whether the holder has confirmed
    or withdrawn the request, and when it was received.

    Args:
        warranty_request_id: Reference number of the request; leave "" if unknown.
        customer_id: Customer reference number of the holder who asked; leave "" if unknown.
        contract_id: Protection contract reference number; leave "" if unknown.
        buyer_customer_id: Customer reference number of the home buyer named on a transfer; leave "" if unknown.
    """
    match = _pick(warranty_request_id=warranty_request_id, customer_id=customer_id,
                  contract_id=contract_id, buyer_customer_id=buyer_customer_id)
    rows = ctx.find("warranty_change_requests", **match)
    return str(rows) if rows else f"No protection change requests found for {match}."


# --------------------------------------------------------------------------- #
# Service calls                                                                #
# --------------------------------------------------------------------------- #

@tool(owner="agent", rw="read")
def find_service_tickets(ctx: ToolContext, ticket_id: str = "", customer_id: str = "",
                         equipment_id: str = "", recall_of_ticket_id: str = "") -> str:
    """Retrieve service calls (work orders) for a home.

    A call shows its call class, status, when and how it was booked, the scheduled date and arrival
    window, the reported symptom, the unit concerned, dispatch and arrival times, completion and
    close-out dates, any cancellation time, the earlier call it returns to under the repair
    guarantee, and the invoice balance. Every criterion is optional.

    Args:
        ticket_id: Service call reference number; leave "" if unknown.
        customer_id: Customer reference number; leave "" if unknown.
        equipment_id: Equipment unit reference number; leave "" if unknown.
        recall_of_ticket_id: Reference number of an earlier call, to find the return visits made on it; leave "" if unknown.
    """
    match = _pick(ticket_id=ticket_id, customer_id=customer_id, equipment_id=equipment_id,
                  recall_of_ticket_id=recall_of_ticket_id)
    rows = ctx.find("service_tickets", **match)
    return str(rows) if rows else f"No service calls found for {match}."


@tool(owner="agent", rw="read")
def find_service_lines(ctx: ToolContext, line_id: str = "", ticket_id: str = "",
                       customer_id: str = "", source_line_id: str = "", claim_id: str = "",
                       agreement_id: str = "") -> str:
    """Show the invoice lines of service calls: fees, parts and labor by price-book task,
    refrigerant by the pound, member and courtesy discounts, warranty and Comfort Club coverage
    credits, payments and refunds, each with its position on the invoice, amount and posting date.
    Discounts, coverage credits and refunds point to the line they apply to. All criteria are
    optional.

    Args:
        line_id: Reference number of one invoice line; leave "" if unknown.
        ticket_id: Service call reference number, to list its whole invoice; leave "" if unknown.
        customer_id: Customer reference number; leave "" if unknown.
        source_line_id: Reference number of a charge or payment line, to find what applies to it; leave "" if unknown.
        claim_id: Warranty claim reference number, to find the coverage it paid on the invoice; leave "" if unknown.
        agreement_id: Comfort Club agreement reference number, to find benefits applied under it; leave "" if unknown.
    """
    match = _pick(line_id=line_id, ticket_id=ticket_id, customer_id=customer_id,
                  source_line_id=source_line_id, claim_id=claim_id, agreement_id=agreement_id)
    rows = ctx.find("service_lines", **match)
    return str(rows) if rows else f"No invoice lines found for {match}."


# --------------------------------------------------------------------------- #
# Replacement installations                                                    #
# --------------------------------------------------------------------------- #

@tool(owner="agent", rw="read")
def find_install_projects(ctx: ToolContext, install_id: str = "", customer_id: str = "",
                          replaced_equipment_id: str = "", finance_account_id: str = "") -> str:
    """Retrieve replacement-system installation contracts.

    A project shows the system package, its status, the signing date and where it was signed, the
    permitting jurisdiction, capacity in tons, the contract price, the balance owed, the unit being
    replaced, the financing account funding it, the install day and permit number, the installation,
    inspection, close-out or cancellation dates and the serial number of the new unit. Every
    criterion is optional.

    Args:
        install_id: Installation project reference number; leave "" if unknown.
        customer_id: Customer reference number; leave "" if unknown.
        replaced_equipment_id: Reference number of the unit being replaced; leave "" if unknown.
        finance_account_id: Financing account reference number; leave "" if unknown.
    """
    match = _pick(install_id=install_id, customer_id=customer_id,
                  replaced_equipment_id=replaced_equipment_id, finance_account_id=finance_account_id)
    rows = ctx.find("install_projects", **match)
    return str(rows) if rows else f"No installation projects found for {match}."


@tool(owner="agent", rw="read")
def find_install_ledger(ctx: ToolContext, install_entry_id: str = "", install_id: str = "",
                        customer_id: str = "", finance_account_id: str = "",
                        source_entry_id: str = "", claim_id: str = "") -> str:
    """Show the money and paperwork history of an installation project: the contract price,
    change orders, permit fee, protection upgrades and accessories charged, member credits and
    manufacturer rebates, deposits and other payments (including lender funding), refunds, and the
    manufacturer warranty registration with the serial number and the parts term it confirmed. A
    protection-contract unit replacement credited to a project names the claim that paid it. All
    criteria are optional.

    Args:
        install_entry_id: Reference number of one project entry; leave "" if unknown.
        install_id: Installation project reference number; leave "" if unknown.
        customer_id: Customer reference number; leave "" if unknown.
        finance_account_id: Financing account reference number, to see its funding or refunds; leave "" if unknown.
        source_entry_id: Reference number of an earlier entry, to find what offsets or returns it; leave "" if unknown.
        claim_id: Protection contract claim reference number, to find the unit-replacement credit it paid; leave "" if unknown.
    """
    match = _pick(install_entry_id=install_entry_id, install_id=install_id, customer_id=customer_id,
                  finance_account_id=finance_account_id, source_entry_id=source_entry_id,
                  claim_id=claim_id)
    rows = ctx.find("install_ledger", **match)
    return str(rows) if rows else f"No installation project entries found for {match}."


@tool(owner="agent", rw="read")
def find_install_change_requests(ctx: ToolContext, install_request_id: str = "",
                                 customer_id: str = "", install_id: str = "") -> str:
    """Look up cancellation notices and change-order approvals on installation projects, with
    whether the homeowner has confirmed or withdrawn each and when it was received.

    Args:
        install_request_id: Reference number of the request; leave "" if unknown.
        customer_id: Customer reference number; leave "" if unknown.
        install_id: Installation project reference number; leave "" if unknown.
    """
    match = _pick(install_request_id=install_request_id, customer_id=customer_id, install_id=install_id)
    rows = ctx.find("install_change_requests", **match)
    return str(rows) if rows else f"No installation change requests found for {match}."


# --------------------------------------------------------------------------- #
# Home Comfort Financing                                                       #
# --------------------------------------------------------------------------- #

@tool(owner="agent", rw="read")
def find_finance_accounts(ctx: ToolContext, finance_account_id: str = "", customer_id: str = "",
                          install_id: str = "") -> str:
    """Retrieve Home Comfort Financing accounts.

    An account shows the financing plan, its status, application and decision dates, the credit
    tier assigned, the amounts requested and financed, the APR and term, the funding date, the end
    of any promotional period, the monthly payment and due day, autopay enrollment, the balance owed
    and the closing date. Every criterion is optional.

    Args:
        finance_account_id: Financing account reference number; leave "" if unknown.
        customer_id: Customer reference number of the borrower; leave "" if unknown.
        install_id: Installation project reference number the account finances; leave "" if unknown.
    """
    match = _pick(finance_account_id=finance_account_id, customer_id=customer_id, install_id=install_id)
    rows = ctx.find("finance_accounts", **match)
    return str(rows) if rows else f"No financing accounts found for {match}."


@tool(owner="agent", rw="read")
def find_finance_transactions(ctx: ToolContext, finance_txn_id: str = "", finance_account_id: str = "",
                              customer_id: str = "", install_id: str = "", install_entry_id: str = "",
                              source_txn_id: str = "") -> str:
    """Show the transaction history of a financing account: the funding disbursement, interest,
    deferred-interest assessments, late and returned-payment fees, payments, merchant refund credits
    and reversals, each with its statement month, amount and posting date. All criteria are optional.

    Args:
        finance_txn_id: Reference number of one transaction; leave "" if unknown.
        finance_account_id: Financing account reference number; leave "" if unknown.
        customer_id: Customer reference number; leave "" if unknown.
        install_id: Installation project reference number; leave "" if unknown.
        install_entry_id: Reference number of an installation refund entry, to find the credit it produced; leave "" if unknown.
        source_txn_id: Reference number of a fee or interest charge, to find its reversal; leave "" if unknown.
    """
    match = _pick(finance_txn_id=finance_txn_id, finance_account_id=finance_account_id,
                  customer_id=customer_id, install_id=install_id, install_entry_id=install_entry_id,
                  source_txn_id=source_txn_id)
    rows = ctx.find("finance_transactions", **match)
    return str(rows) if rows else f"No financing transactions found for {match}."


@tool(owner="agent", rw="read")
def find_finance_requests(ctx: ToolContext, finance_request_id: str = "", customer_id: str = "",
                          finance_account_id: str = "") -> str:
    """Look up application withdrawals and plan-change requests a borrower has made before funding,
    with the plan requested, whether the borrower has confirmed or withdrawn it, and when it was
    received.

    Args:
        finance_request_id: Reference number of the request; leave "" if unknown.
        customer_id: Customer reference number; leave "" if unknown.
        finance_account_id: Financing account reference number; leave "" if unknown.
    """
    match = _pick(finance_request_id=finance_request_id, customer_id=customer_id,
                  finance_account_id=finance_account_id)
    rows = ctx.find("finance_requests", **match)
    return str(rows) if rows else f"No financing requests found for {match}."


# --------------------------------------------------------------------------- #
# FilterDirect subscriptions                                                   #
# --------------------------------------------------------------------------- #

@tool(owner="agent", rw="read")
def find_filter_subscriptions(ctx: ToolContext, subscription_id: str = "", customer_id: str = "") -> str:
    """Retrieve FilterDirect filter subscriptions: the filter grade, status, start date, filter
    size, next ship date, any pause end date, the balance owed and the cancellation date.

    Args:
        subscription_id: Subscription reference number; leave "" if unknown.
        customer_id: Customer reference number; leave "" if unknown.
    """
    match = _pick(subscription_id=subscription_id, customer_id=customer_id)
    rows = ctx.find("filter_subscriptions", **match)
    return str(rows) if rows else f"No filter subscriptions found for {match}."


@tool(owner="agent", rw="read")
def find_filter_entries(ctx: ToolContext, filter_entry_id: str = "", subscription_id: str = "",
                        customer_id: str = "", source_entry_id: str = "") -> str:
    """Show a filter subscription's shipments and billing: each shipment with its cycle and filter
    count, shipment and shipping charges, size-change fees, payments, and credits for damaged or
    wrong-size shipments. All criteria are optional.

    Args:
        filter_entry_id: Reference number of one entry; leave "" if unknown.
        subscription_id: Subscription reference number; leave "" if unknown.
        customer_id: Customer reference number; leave "" if unknown.
        source_entry_id: Reference number of a shipment or charge, to find the credit issued on it; leave "" if unknown.
    """
    match = _pick(filter_entry_id=filter_entry_id, subscription_id=subscription_id,
                  customer_id=customer_id, source_entry_id=source_entry_id)
    rows = ctx.find("filter_entries", **match)
    return str(rows) if rows else f"No filter subscription entries found for {match}."


# --------------------------------------------------------------------------- #
# ComfortLease equipment leases                                                #
# --------------------------------------------------------------------------- #

@tool(owner="agent", rw="read")
def find_lease_agreements(ctx: ToolContext, lease_id: str = "", customer_id: str = "",
                          equipment_id: str = "") -> str:
    """Retrieve ComfortLease equipment leases: the leased system, status, signing and installation
    dates, the leased unit, the current monthly rent, the balance owed and the date the lease ended.

    Args:
        lease_id: Lease reference number; leave "" if unknown.
        customer_id: Customer reference number of the lessee; leave "" if unknown.
        equipment_id: Reference number of the leased unit; leave "" if unknown.
    """
    match = _pick(lease_id=lease_id, customer_id=customer_id, equipment_id=equipment_id)
    rows = ctx.find("lease_agreements", **match)
    return str(rows) if rows else f"No equipment leases found for {match}."


@tool(owner="agent", rw="read")
def find_lease_entries(ctx: ToolContext, lease_entry_id: str = "", lease_id: str = "",
                       customer_id: str = "", source_entry_id: str = "") -> str:
    """Show a lease's billing history: monthly rent, installation, late, buyout, early-termination
    and removal charges, payments, and outage credits or fee waivers, each with its rent month,
    amount and posting date. All criteria are optional.

    Args:
        lease_entry_id: Reference number of one entry; leave "" if unknown.
        lease_id: Lease reference number; leave "" if unknown.
        customer_id: Customer reference number; leave "" if unknown.
        source_entry_id: Reference number of a charge, to find the credit that offsets it; leave "" if unknown.
    """
    match = _pick(lease_entry_id=lease_entry_id, lease_id=lease_id, customer_id=customer_id,
                  source_entry_id=source_entry_id)
    rows = ctx.find("lease_entries", **match)
    return str(rows) if rows else f"No lease entries found for {match}."


@tool(owner="agent", rw="read")
def find_lease_change_requests(ctx: ToolContext, lease_request_id: str = "", customer_id: str = "",
                               lease_id: str = "") -> str:
    """Look up buyout and early-termination requests on equipment leases, with whether the lessee
    has confirmed or withdrawn each and when it was received.

    Args:
        lease_request_id: Reference number of the request; leave "" if unknown.
        customer_id: Customer reference number; leave "" if unknown.
        lease_id: Lease reference number; leave "" if unknown.
    """
    match = _pick(lease_request_id=lease_request_id, customer_id=customer_id, lease_id=lease_id)
    rows = ctx.find("lease_change_requests", **match)
    return str(rows) if rows else f"No lease change requests found for {match}."


# --------------------------------------------------------------------------- #
# Identity verification and human handoff                                      #
# --------------------------------------------------------------------------- #

@tool(owner="agent", rw="read")
def find_verification_log(ctx: ToolContext, verification_id: str = "", customer_id: str = "") -> str:
    """Check whether a caller's identity has already been verified for a customer profile, and
    when the most recent verification attempt was made.

    Args:
        verification_id: Reference number of the verification record; leave "" if unknown.
        customer_id: Customer reference number; leave "" if unknown.
    """
    match = _pick(verification_id=verification_id, customer_id=customer_id)
    rows = ctx.find("verification_log", **match)
    return str(rows) if rows else f"No identity verification on record for {match}."


@tool(owner="agent", rw="read")
def find_handoff_log(ctx: ToolContext, handoff_id: str = "", customer_id: str = "") -> str:
    """See whether a customer has already been handed over to a human representative, for what
    reason and when.

    Args:
        handoff_id: Reference number of the handoff; leave "" if unknown.
        customer_id: Customer reference number; leave "" if unknown.
    """
    match = _pick(handoff_id=handoff_id, customer_id=customer_id)
    rows = ctx.find("handoff_log", **match)
    return str(rows) if rows else f"No handoff on record for {match}."


@tool(owner="agent", rw="write")
def verify_customer_identity(ctx: ToolContext, customer_id: str, phone_number: str = "",
                             email: str = "", service_address: str = "", account_pin: str = "") -> str:
    """Verify that the caller is the account holder, and record the outcome. Identity must be
    verified before any account details are discussed or any change, charge, credit or refund is
    made on the account.

    This tool performs the comparison itself: it checks each piece of identity information the
    caller gives against the customer profile, counts how many match, and verifies the caller only
    when at least 2 match. The customer reference number only identifies which profile to compare
    against and never counts as a match. Callers usually know only some of these details, so pass
    exactly what the caller said, unchanged, and leave the rest blank. If a first attempt falls
    short, ask for another detail on file and call again; once verified, the account stays verified
    for this conversation.

    Args:
        customer_id: Customer reference number of the profile being verified, read from the customer profile lookup. Required; does not count as a match.
        phone_number: Phone number the caller gives for the account, 10 digits; leave "" if not given.
        email: Email address the caller gives for the account; leave "" if not given.
        service_address: Street line of the service address the caller gives (house number and street); leave "" if not given.
        account_pin: Four-digit account PIN the caller gives; leave "" if not given.
    """
    if not customer_id:
        return "Error: customer_id is required; look the customer up first and pass their reference number."
    rows = ctx.find("customers", customer_id=customer_id)
    if not rows:
        return f"Error: no customer {customer_id}; cannot verify."
    rec = rows[0]

    def _norm(value):
        return "".join(ch for ch in str(value).casefold() if ch.isalnum())

    # The tool owns the comparison; the locator customer_id is never counted.
    supplied = {"phone_number": phone_number, "email": email,
                "service_address": service_address, "account_pin": account_pin}
    matched = sum(1 for field, value in supplied.items()
                  if value and _norm(rec.get(field, "")) == _norm(value))
    verified = matched >= 2
    rid = ctx.make_id("ver_", customer_id)
    # Store only the reproducible boolean; upsert and never downgrade a pass.
    prior = ctx.find("verification_log", verification_id=rid)
    verified = verified or bool(prior and prior[0].get("verified"))
    if prior:
        ctx.update("verification_log", rid, verified=verified, verified_at=ctx.now())
    else:
        ctx.create("verification_log", rid, verification_id=rid, customer_id=customer_id,
                   verified=verified, verified_at=ctx.now())
    if verified:
        return f"Identity verified for {customer_id}."
    return (f"Identity NOT verified for {customer_id}: only {matched} of the 2 required details "
            "matched. Ask the caller for another detail on file and try again.")


@tool(owner="agent", rw="write")
def transfer_to_human_agent(ctx: ToolContext, customer_id: str, reason: str) -> str:
    """Hand the customer over to a Harbison customer care representative, and record the handoff
    and its reason.

    Use it in one of two situations only: when no Harbison policy lets you resolve what the
    customer is asking for, or when the customer has explicitly asked to speak with a person at
    least 2 times in this conversation.

    Args:
        customer_id: Customer reference number, read from the customer profile lookup (the profile must exist).
        reason: Exactly one of two values, never free text. POLICY_NOT_COVERED: no current policy offers a way to resolve the request. CUSTOMER_REQUESTED: the customer has explicitly asked for a human representative at least 2 times.
    """
    allowed = {"POLICY_NOT_COVERED", "CUSTOMER_REQUESTED"}
    if reason not in allowed:
        return f"Error: unknown handoff reason '{reason}'. Valid: {', '.join(sorted(allowed))}."
    if not ctx.find("customers", customer_id=customer_id):
        return f"Error: no customer {customer_id}; cannot record the handoff."
    rid = ctx.make_id("hof_", customer_id, reason)
    ctx.create("handoff_log", rid, handoff_id=rid, customer_id=customer_id,
               reason=reason, created_at=ctx.now())
    return f"Handoff to a customer care representative recorded for {customer_id} ({reason})."

"""Shared tools for env_0023_multifamily_apartment_reit (Larkspur Residential Trust resident services).

Every tool here is always available: one lookup per kind of record (the resident profile lookup doubles as the
way to find a caller from what they can state), the identity verification write, and the handoff to a human
resident services specialist. Business actions of each difficulty live in that difficulty's task tools.
"""

from erlbench import ToolContext, tool


@tool(owner="agent", rw="read")
def find_customers(ctx: ToolContext, customer_id: str = "", phone_number: str = "", email: str = "",
                   name: str = "") -> str:
    """Look up a resident profile to establish whose account this conversation is about.

    Search by the customer reference number, or by what a caller can naturally state: the mobile number, the
    email address or the full name on the lease. Every criterion is optional; give whichever you have. On a match
    the profile is returned with the resident's name, mobile number, email address, date of birth, last four
    digits of the Social Security or ITIN number and the date the profile was opened. Finding a profile does not
    verify the caller's identity; identity is verified separately.

    Args:
        customer_id: The customer reference number; leave "" if unknown.
        phone_number: The mobile number on the profile, written NNN-NNN-NNNN; leave "" if not stated.
        email: The email address on the profile; leave "" if not stated.
        name: The resident's full name as printed on the lease; leave "" if not stated.
    """
    match = {k: v for k, v in {"customer_id": customer_id, "phone_number": phone_number,
                               "email": email, "name": name}.items() if v}
    if not match:
        return "Error: provide at least one reference number or profile detail to find the resident."
    rows = ctx.fuzzy_find("customers", **match)
    if not rows:
        return f"No resident profile matches {match}."
    if len(rows) > 1:
        return f"Error: {len(rows)} resident profiles match {match}; ask the caller for one more detail."
    return str(rows[0])


@tool(owner="agent", rw="read")
def find_identity_verifications(ctx: ToolContext, verification_id: str = "", customer_id: str = "") -> str:
    """Look up the identity verification outcome recorded for a resident in this conversation or earlier.

    Search by any reference number you already hold; every criterion is optional and several may be combined.
    Returns whether the resident has passed identity verification and when it was last attempted. When nothing matches, a short not-found message is returned.

    Args:
        verification_id: The reference number of the verification record itself; leave "" if unknown.
        customer_id: The resident's customer reference number (the resident the record belongs to); leave "" if unknown.
    """
    match = {k: v for k, v in {"verification_id": verification_id, "customer_id": customer_id}.items() if v}
    rows = ctx.find("identity_verifications", **match)
    return str(rows) if rows else f"No identity verifications records match {match}."

@tool(owner="agent", rw="read")
def find_handoffs(ctx: ToolContext, handoff_id: str = "", customer_id: str = "") -> str:
    """Look up the handoffs to a human resident services specialist recorded for a resident.

    Search by any reference number you already hold; every criterion is optional and several may be combined.
    Returns each handoff with its reason and time. When nothing matches, a short not-found message is returned.

    Args:
        handoff_id: The reference number of the handoff record itself; leave "" if unknown.
        customer_id: The resident's customer reference number (the resident the record belongs to); leave "" if unknown.
    """
    match = {k: v for k, v in {"handoff_id": handoff_id, "customer_id": customer_id}.items() if v}
    rows = ctx.find("handoffs", **match)
    return str(rows) if rows else f"No handoffs records match {match}."

@tool(owner="agent", rw="read")
def find_leases(ctx: ToolContext, lease_id: str = "", customer_id: str = "") -> str:
    """Look up apartment home leases — the application, floor plan, community and state, apartment home, move-in and move-out dates, monthly rent in force, current ledger balance, occupants, screening outcome, discount program, autopay, proof of insurance and any certified-funds restriction.

    Search by any reference number you already hold; every criterion is optional and several may be combined.
    Returns every matching lease. When nothing matches, a short not-found message is returned.

    Args:
        lease_id: The reference number of the lease itself; leave "" if unknown.
        customer_id: The resident's customer reference number (the resident the record belongs to); leave "" if unknown.
    """
    match = {k: v for k, v in {"lease_id": lease_id, "customer_id": customer_id}.items() if v}
    rows = ctx.find("leases", **match)
    return str(rows) if rows else f"No leases records match {match}."

@tool(owner="agent", rw="read")
def find_lease_charges(ctx: ToolContext, charge_id: str = "", lease_id: str = "", customer_id: str = "", source_charge_id: str = "", source_payment_id: str = "") -> str:
    """Look up lines on a lease ledger — rent, lease fees, late fees, returned payment fees, concessions, discounts, waivers and reversals — with their charge code, month, posting date, amount, proration days and, for a credit or fee, the charge or payment it relates to.

    Search by any reference number you already hold; every criterion is optional and several may be combined.
    Returns every matching ledger line. When nothing matches, a short not-found message is returned.

    Args:
        charge_id: The reference number of the ledger line itself; leave "" if unknown.
        lease_id: The reference number of the apartment home lease; leave "" if unknown.
        customer_id: The resident's customer reference number (the resident the record belongs to); leave "" if unknown.
        source_charge_id: The reference number of the charge that a credit waives, discounts or reverses; leave "" if unknown.
        source_payment_id: The reference number of the returned payment behind a returned payment fee; leave "" if unknown.
    """
    match = {k: v for k, v in {"charge_id": charge_id, "lease_id": lease_id, "customer_id": customer_id, "source_charge_id": source_charge_id, "source_payment_id": source_payment_id}.items() if v}
    rows = ctx.find("lease_charges", **match)
    return str(rows) if rows else f"No lease charges records match {match}."

@tool(owner="agent", rw="read")
def find_lease_payments(ctx: ToolContext, payment_id: str = "", lease_id: str = "", customer_id: str = "", source_payment_id: str = "", plan_request_id: str = "") -> str:
    """Look up payments received on a lease and payments returned by the bank or card network — instrument, amount, date, confirmation number, return reason and any payment plan they belong to.

    Search by any reference number you already hold; every criterion is optional and several may be combined.
    Returns every matching payment or return. When nothing matches, a short not-found message is returned.

    Args:
        payment_id: The reference number of the payment or return itself; leave "" if unknown.
        lease_id: The reference number of the apartment home lease; leave "" if unknown.
        customer_id: The resident's customer reference number (the resident the record belongs to); leave "" if unknown.
        source_payment_id: The reference number of the original payment that a return reverses; leave "" if unknown.
        plan_request_id: The reference number of the payment plan a down payment or installment belongs to; leave "" if unknown.
    """
    match = {k: v for k, v in {"payment_id": payment_id, "lease_id": lease_id, "customer_id": customer_id, "source_payment_id": source_payment_id, "plan_request_id": plan_request_id}.items() if v}
    rows = ctx.find("lease_payments", **match)
    return str(rows) if rows else f"No lease payments records match {match}."

@tool(owner="agent", rw="read")
def find_lease_notices(ctx: ToolContext, notice_id: str = "", lease_id: str = "", customer_id: str = "") -> str:
    """Look up notices served on a lease — delinquency (pay or quit) notices, violation (cure or quit) notices and eviction referrals — with their dates, cure deadlines, amounts demanded, rent month, service method and violation.

    Search by any reference number you already hold; every criterion is optional and several may be combined.
    Returns every matching notice. When nothing matches, a short not-found message is returned.

    Args:
        notice_id: The reference number of the notice or referral itself; leave "" if unknown.
        lease_id: The reference number of the apartment home lease; leave "" if unknown.
        customer_id: The resident's customer reference number (the resident the record belongs to); leave "" if unknown.
    """
    match = {k: v for k, v in {"notice_id": notice_id, "lease_id": lease_id, "customer_id": customer_id}.items() if v}
    rows = ctx.find("lease_notices", **match)
    return str(rows) if rows else f"No lease notices records match {match}."

@tool(owner="agent", rw="read")
def find_lease_payment_plan_requests(ctx: ToolContext, plan_request_id: str = "", customer_id: str = "", lease_id: str = "") -> str:
    """Look up payment plan agreements drawn up on a lease — arrears covered, down payment, installments, first due date and whether the resident has signed, completed or defaulted on the plan.

    Search by any reference number you already hold; every criterion is optional and several may be combined.
    Returns every matching plan. When nothing matches, a short not-found message is returned.

    Args:
        plan_request_id: The reference number of the payment plan itself; leave "" if unknown.
        customer_id: The resident's customer reference number (the resident the record belongs to); leave "" if unknown.
        lease_id: The reference number of the apartment home lease; leave "" if unknown.
    """
    match = {k: v for k, v in {"plan_request_id": plan_request_id, "customer_id": customer_id, "lease_id": lease_id}.items() if v}
    rows = ctx.find("lease_payment_plan_requests", **match)
    return str(rows) if rows else f"No lease payment plan requests records match {match}."

@tool(owner="agent", rw="read")
def find_lease_terms(ctx: ToolContext, term_id: str = "", customer_id: str = "", lease_id: str = "") -> str:
    """Look up Lease Term Agreements — term program, origin (new lease, renewal, transfer or month-to-month conversion), start and end dates, length, contracted rent, signing date, notice to vacate and intended move-out date, term charge balance and status.

    Search by any reference number you already hold; every criterion is optional and several may be combined.
    Returns every matching term; a lease usually has several over its life. When nothing matches, a short not-found message is returned.

    Args:
        term_id: The reference number of the term agreement itself; leave "" if unknown.
        customer_id: The resident's customer reference number (the resident the record belongs to); leave "" if unknown.
        lease_id: The reference number of the apartment home lease; leave "" if unknown.
    """
    match = {k: v for k, v in {"term_id": term_id, "customer_id": customer_id, "lease_id": lease_id}.items() if v}
    rows = ctx.find("lease_terms", **match)
    return str(rows) if rows else f"No lease terms records match {match}."

@tool(owner="agent", rw="read")
def find_term_offers(ctx: ToolContext, offer_id: str = "", term_id: str = "", customer_id: str = "") -> str:
    """Look up renewal offer lines delivered on an expiring term — the term program and length offered, offered rent, offer date and expiration date.

    Search by any reference number you already hold; every criterion is optional and several may be combined.
    Returns every matching offer line. When nothing matches, a short not-found message is returned.

    Args:
        offer_id: The reference number of the offer line itself; leave "" if unknown.
        term_id: The reference number of the Lease Term Agreement; leave "" if unknown.
        customer_id: The resident's customer reference number (the resident the record belongs to); leave "" if unknown.
    """
    match = {k: v for k, v in {"offer_id": offer_id, "term_id": term_id, "customer_id": customer_id}.items() if v}
    rows = ctx.find("term_offers", **match)
    return str(rows) if rows else f"No term offers records match {match}."

@tool(owner="agent", rw="read")
def find_term_rent_changes(ctx: ToolContext, rent_change_id: str = "", term_id: str = "", customer_id: str = "", lease_id: str = "") -> str:
    """Look up recorded rent changes — previous and new monthly rent, effective date, the date notice was delivered and the reason for the change.

    Search by any reference number you already hold; every criterion is optional and several may be combined.
    Returns every matching rent change. When nothing matches, a short not-found message is returned.

    Args:
        rent_change_id: The reference number of the rent change itself; leave "" if unknown.
        term_id: The reference number of the Lease Term Agreement; leave "" if unknown.
        customer_id: The resident's customer reference number (the resident the record belongs to); leave "" if unknown.
        lease_id: The reference number of the apartment home lease; leave "" if unknown.
    """
    match = {k: v for k, v in {"rent_change_id": rent_change_id, "term_id": term_id, "customer_id": customer_id, "lease_id": lease_id}.items() if v}
    rows = ctx.find("term_rent_changes", **match)
    return str(rows) if rows else f"No term rent changes records match {match}."

@tool(owner="agent", rw="read")
def find_term_charges(ctx: ToolContext, term_charge_id: str = "", term_id: str = "", customer_id: str = "", request_id: str = "", source_term_charge_id: str = "") -> str:
    """Look up charges, credits and payments on a Lease Term Agreement account — early termination and reletting fees, concession recapture, lease-break and holdover rent, insufficient notice and transfer fees, reletting credits, reversals and payments.

    Search by any reference number you already hold; every criterion is optional and several may be combined.
    Returns every matching line. When nothing matches, a short not-found message is returned.

    Args:
        term_charge_id: The reference number of the term charge line itself; leave "" if unknown.
        term_id: The reference number of the Lease Term Agreement; leave "" if unknown.
        customer_id: The resident's customer reference number (the resident the record belongs to); leave "" if unknown.
        request_id: The reference number of the early termination or transfer request a charge arises from; leave "" if unknown.
        source_term_charge_id: The reference number of the term charge that a credit reverses or offsets; leave "" if unknown.
    """
    match = {k: v for k, v in {"term_charge_id": term_charge_id, "term_id": term_id, "customer_id": customer_id, "request_id": request_id, "source_term_charge_id": source_term_charge_id}.items() if v}
    rows = ctx.find("term_charges", **match)
    return str(rows) if rows else f"No term charges records match {match}."

@tool(owner="agent", rw="read")
def find_term_change_requests(ctx: ToolContext, request_id: str = "", customer_id: str = "", term_id: str = "") -> str:
    """Look up early termination, lease break, statutory release, unit transfer and renewal rescission requests — the date asked for, any statutory ground, destination apartment home and rent, the amount quoted and whether the resident signed.

    Search by any reference number you already hold; every criterion is optional and several may be combined.
    Returns every matching request. When nothing matches, a short not-found message is returned.

    Args:
        request_id: The reference number of the request itself; leave "" if unknown.
        customer_id: The resident's customer reference number (the resident the record belongs to); leave "" if unknown.
        term_id: The reference number of the Lease Term Agreement; leave "" if unknown.
    """
    match = {k: v for k, v in {"request_id": request_id, "customer_id": customer_id, "term_id": term_id}.items() if v}
    rows = ctx.find("term_change_requests", **match)
    return str(rows) if rows else f"No term change requests records match {match}."

@tool(owner="agent", rw="read")
def find_utility_accounts(ctx: ToolContext, utility_account_id: str = "", customer_id: str = "", lease_id: str = "") -> str:
    """Look up utility services accounts — the utility program, service start and end dates, billed occupants, square footage, current utility balance and status.

    Search by any reference number you already hold; every criterion is optional and several may be combined.
    Returns every matching account; a transfer can leave two accounts on one lease. When nothing matches, a short not-found message is returned.

    Args:
        utility_account_id: The reference number of the utility account itself; leave "" if unknown.
        customer_id: The resident's customer reference number (the resident the record belongs to); leave "" if unknown.
        lease_id: The reference number of the apartment home lease; leave "" if unknown.
    """
    match = {k: v for k, v in {"utility_account_id": utility_account_id, "customer_id": customer_id, "lease_id": lease_id}.items() if v}
    rows = ctx.find("utility_accounts", **match)
    return str(rows) if rows else f"No utility accounts records match {match}."

@tool(owner="agent", rw="read")
def find_utility_bills(ctx: ToolContext, bill_id: str = "", utility_account_id: str = "", customer_id: str = "", source_bill_id: str = "") -> str:
    """Look up utility bill lines, adjustments and payments — service, month, bill date, amount, usage and unit, actual or estimated read, allocation share and community bill, proration days, the line an adjustment credits and the adjustment reason.

    Search by any reference number you already hold; every criterion is optional and several may be combined.
    Returns every matching line. When nothing matches, a short not-found message is returned.

    Args:
        bill_id: The reference number of the bill line itself; leave "" if unknown.
        utility_account_id: The reference number of the utility services account; leave "" if unknown.
        customer_id: The resident's customer reference number (the resident the record belongs to); leave "" if unknown.
        source_bill_id: The reference number of the bill line that an adjustment credits; leave "" if unknown.
    """
    match = {k: v for k, v in {"bill_id": bill_id, "utility_account_id": utility_account_id, "customer_id": customer_id, "source_bill_id": source_bill_id}.items() if v}
    rows = ctx.find("utility_bills", **match)
    return str(rows) if rows else f"No utility bills records match {match}."

@tool(owner="agent", rw="read")
def find_utility_meter_reads(ctx: ToolContext, read_id: str = "", utility_account_id: str = "", customer_id: str = "") -> str:
    """Look up submeter reads — service, month closed, read date, register value, usage since the previous read and whether the read was actual or estimated.

    Search by any reference number you already hold; every criterion is optional and several may be combined.
    Returns every matching read. When nothing matches, a short not-found message is returned.

    Args:
        read_id: The reference number of the meter read itself; leave "" if unknown.
        utility_account_id: The reference number of the utility services account; leave "" if unknown.
        customer_id: The resident's customer reference number (the resident the record belongs to); leave "" if unknown.
    """
    match = {k: v for k, v in {"read_id": read_id, "utility_account_id": utility_account_id, "customer_id": customer_id}.items() if v}
    rows = ctx.find("utility_meter_reads", **match)
    return str(rows) if rows else f"No utility meter reads records match {match}."

@tool(owner="agent", rw="read")
def find_utility_disputes(ctx: ToolContext, dispute_id: str = "", customer_id: str = "", utility_account_id: str = "", bill_id: str = "") -> str:
    """Look up utility bill disputes — the bill line disputed, the ground, any leak repair date and the dispute status.

    Search by any reference number you already hold; every criterion is optional and several may be combined.
    Returns every matching dispute. When nothing matches, a short not-found message is returned.

    Args:
        dispute_id: The reference number of the utility dispute itself; leave "" if unknown.
        customer_id: The resident's customer reference number (the resident the record belongs to); leave "" if unknown.
        utility_account_id: The reference number of the utility services account; leave "" if unknown.
        bill_id: The reference number of the bill line disputed; leave "" if unknown.
    """
    match = {k: v for k, v in {"dispute_id": dispute_id, "customer_id": customer_id, "utility_account_id": utility_account_id, "bill_id": bill_id}.items() if v}
    rows = ctx.find("utility_disputes", **match)
    return str(rows) if rows else f"No utility disputes records match {match}."

@tool(owner="agent", rw="read")
def find_deposit_accounts(ctx: ToolContext, deposit_account_id: str = "", customer_id: str = "", lease_id: str = "") -> str:
    """Look up security deposit accounts — deposit program, governing state, required deposit, deposit held, balance owed, move-out date, forwarding address, refund method, statement and due dates and status.

    Search by any reference number you already hold; every criterion is optional and several may be combined.
    Returns every matching account. When nothing matches, a short not-found message is returned.

    Args:
        deposit_account_id: The reference number of the deposit account itself; leave "" if unknown.
        customer_id: The resident's customer reference number (the resident the record belongs to); leave "" if unknown.
        lease_id: The reference number of the apartment home lease; leave "" if unknown.
    """
    match = {k: v for k, v in {"deposit_account_id": deposit_account_id, "customer_id": customer_id, "lease_id": lease_id}.items() if v}
    rows = ctx.find("deposit_accounts", **match)
    return str(rows) if rows else f"No deposit accounts records match {match}."

@tool(owner="agent", rw="read")
def find_deposit_transactions(ctx: ToolContext, transaction_id: str = "", deposit_account_id: str = "", customer_id: str = "", source_transaction_id: str = "") -> str:
    """Look up deposit transactions and final account statement lines — deposits and installments received, guarantee premiums, itemized move-out charges with room, age, replacement cost, labor, quantity and photo evidence, withdrawn lines, deposit applied to each ledger, refunds, balance owed, payments, guarantee claims and credits.

    Search by any reference number you already hold; every criterion is optional and several may be combined.
    Returns every matching transaction or line. When nothing matches, a short not-found message is returned.

    Args:
        transaction_id: The reference number of the deposit transaction or statement line itself; leave "" if unknown.
        deposit_account_id: The reference number of the security deposit account; leave "" if unknown.
        customer_id: The resident's customer reference number (the resident the record belongs to); leave "" if unknown.
        source_transaction_id: The reference number of the itemized line that a withdrawal or dispute credit relates to; leave "" if unknown.
    """
    match = {k: v for k, v in {"transaction_id": transaction_id, "deposit_account_id": deposit_account_id, "customer_id": customer_id, "source_transaction_id": source_transaction_id}.items() if v}
    rows = ctx.find("deposit_transactions", **match)
    return str(rows) if rows else f"No deposit transactions records match {match}."

@tool(owner="agent", rw="read")
def find_deposit_disputes(ctx: ToolContext, dispute_id: str = "", customer_id: str = "", deposit_account_id: str = "", transaction_id: str = "") -> str:
    """Look up disputes of itemized move-out lines — the line disputed and the dispute status.

    Search by any reference number you already hold; every criterion is optional and several may be combined.
    Returns every matching dispute. When nothing matches, a short not-found message is returned.

    Args:
        dispute_id: The reference number of the deposit dispute itself; leave "" if unknown.
        customer_id: The resident's customer reference number (the resident the record belongs to); leave "" if unknown.
        deposit_account_id: The reference number of the security deposit account; leave "" if unknown.
        transaction_id: The reference number of the itemized move-out line disputed; leave "" if unknown.
    """
    match = {k: v for k, v in {"dispute_id": dispute_id, "customer_id": customer_id, "deposit_account_id": deposit_account_id, "transaction_id": transaction_id}.items() if v}
    rows = ctx.find("deposit_disputes", **match)
    return str(rows) if rows else f"No deposit disputes records match {match}."

@tool(owner="agent", rw="read")
def find_parking_licenses(ctx: ToolContext, parking_license_id: str = "", customer_id: str = "", lease_id: str = "") -> str:
    """Look up parking licenses and parking requests — parking product, space or tag, registered plate, waitlist date, start and end dates, monthly fee, parking balance and status.

    Search by any reference number you already hold; every criterion is optional and several may be combined.
    Returns every matching license. When nothing matches, a short not-found message is returned.

    Args:
        parking_license_id: The reference number of the parking license itself; leave "" if unknown.
        customer_id: The resident's customer reference number (the resident the record belongs to); leave "" if unknown.
        lease_id: The reference number of the apartment home lease; leave "" if unknown.
    """
    match = {k: v for k, v in {"parking_license_id": parking_license_id, "customer_id": customer_id, "lease_id": lease_id}.items() if v}
    rows = ctx.find("parking_licenses", **match)
    return str(rows) if rows else f"No parking licenses records match {match}."

@tool(owner="agent", rw="read")
def find_parking_charges(ctx: ToolContext, parking_charge_id: str = "", parking_license_id: str = "", customer_id: str = "", source_parking_charge_id: str = "", source_activity_id: str = "") -> str:
    """Look up parking charges, credits and payments — monthly and service fees, EV charging energy and idle fees with session details, violation fines, bundle discounts, reversals and payments.

    Search by any reference number you already hold; every criterion is optional and several may be combined.
    Returns every matching line. When nothing matches, a short not-found message is returned.

    Args:
        parking_charge_id: The reference number of the parking line itself; leave "" if unknown.
        parking_license_id: The reference number of the parking license; leave "" if unknown.
        customer_id: The resident's customer reference number (the resident the record belongs to); leave "" if unknown.
        source_parking_charge_id: The reference number of the parking charge that a credit discounts or reverses; leave "" if unknown.
        source_activity_id: The reference number of the violation that a fine bills; leave "" if unknown.
    """
    match = {k: v for k, v in {"parking_charge_id": parking_charge_id, "parking_license_id": parking_license_id, "customer_id": customer_id, "source_parking_charge_id": source_parking_charge_id, "source_activity_id": source_activity_id}.items() if v}
    rows = ctx.find("parking_charges", **match)
    return str(rows) if rows else f"No parking charges records match {match}."

@tool(owner="agent", rw="read")
def find_parking_activity(ctx: ToolContext, activity_id: str = "", parking_license_id: str = "", customer_id: str = "") -> str:
    """Look up parking violations and guest passes — date, rule broken, enforcement step, plate observed and nights covered.

    Search by any reference number you already hold; every criterion is optional and several may be combined.
    Returns every matching record. When nothing matches, a short not-found message is returned.

    Args:
        activity_id: The reference number of the violation or guest pass itself; leave "" if unknown.
        parking_license_id: The reference number of the parking license; leave "" if unknown.
        customer_id: The resident's customer reference number (the resident the record belongs to); leave "" if unknown.
    """
    match = {k: v for k, v in {"activity_id": activity_id, "parking_license_id": parking_license_id, "customer_id": customer_id}.items() if v}
    rows = ctx.find("parking_activity", **match)
    return str(rows) if rows else f"No parking activity records match {match}."

@tool(owner="agent", rw="read")
def find_storage_rentals(ctx: ToolContext, storage_rental_id: str = "", customer_id: str = "", lease_id: str = "") -> str:
    """Look up storage rentals and reservations — storage product, unit label, reservation, start and end dates, monthly rent, storage balance and status.

    Search by any reference number you already hold; every criterion is optional and several may be combined.
    Returns every matching rental. When nothing matches, a short not-found message is returned.

    Args:
        storage_rental_id: The reference number of the storage rental itself; leave "" if unknown.
        customer_id: The resident's customer reference number (the resident the record belongs to); leave "" if unknown.
        lease_id: The reference number of the apartment home lease; leave "" if unknown.
    """
    match = {k: v for k, v in {"storage_rental_id": storage_rental_id, "customer_id": customer_id, "lease_id": lease_id}.items() if v}
    rows = ctx.find("storage_rentals", **match)
    return str(rows) if rows else f"No storage rentals records match {match}."

@tool(owner="agent", rw="read")
def find_storage_charges(ctx: ToolContext, storage_charge_id: str = "", storage_rental_id: str = "", customer_id: str = "", source_storage_charge_id: str = "") -> str:
    """Look up storage charges, credits and payments — rent, reservation, lock, card, key, overlock, cleanout, unit change and early termination fees, promotions, prepay discounts, reversals and payments.

    Search by any reference number you already hold; every criterion is optional and several may be combined.
    Returns every matching line. When nothing matches, a short not-found message is returned.

    Args:
        storage_charge_id: The reference number of the storage line itself; leave "" if unknown.
        storage_rental_id: The reference number of the storage rental; leave "" if unknown.
        customer_id: The resident's customer reference number (the resident the record belongs to); leave "" if unknown.
        source_storage_charge_id: The reference number of the storage charge that a credit reduces; leave "" if unknown.
    """
    match = {k: v for k, v in {"storage_charge_id": storage_charge_id, "storage_rental_id": storage_rental_id, "customer_id": customer_id, "source_storage_charge_id": source_storage_charge_id}.items() if v}
    rows = ctx.find("storage_charges", **match)
    return str(rows) if rows else f"No storage charges records match {match}."

@tool(owner="agent", rw="read")
def find_pet_addenda(ctx: ToolContext, pet_addendum_id: str = "", customer_id: str = "", lease_id: str = "") -> str:
    """Look up pet addenda and assistance animal registrations — addendum type, pet or assistance animal, name, species, breed, weight, vaccination expiry, registration, approval and end dates, pet balance and status.

    Search by any reference number you already hold; every criterion is optional and several may be combined.
    Returns every matching registration. When nothing matches, a short not-found message is returned.

    Args:
        pet_addendum_id: The reference number of the pet addendum itself; leave "" if unknown.
        customer_id: The resident's customer reference number (the resident the record belongs to); leave "" if unknown.
        lease_id: The reference number of the apartment home lease; leave "" if unknown.
    """
    match = {k: v for k, v in {"pet_addendum_id": pet_addendum_id, "customer_id": customer_id, "lease_id": lease_id}.items() if v}
    rows = ctx.find("pet_addenda", **match)
    return str(rows) if rows else f"No pet addenda records match {match}."

@tool(owner="agent", rw="read")
def find_pet_charges(ctx: ToolContext, pet_charge_id: str = "", pet_addendum_id: str = "", customer_id: str = "", source_pet_charge_id: str = "", source_incident_id: str = "") -> str:
    """Look up pet charges, credits and payments — pet fees, DNA and flea treatment fees, unauthorized pet fees, pet rent, fines, additional-pet discounts, reversals and payments.

    Search by any reference number you already hold; every criterion is optional and several may be combined.
    Returns every matching line. When nothing matches, a short not-found message is returned.

    Args:
        pet_charge_id: The reference number of the pet line itself; leave "" if unknown.
        pet_addendum_id: The reference number of the pet addendum or assistance animal registration; leave "" if unknown.
        customer_id: The resident's customer reference number (the resident the record belongs to); leave "" if unknown.
        source_pet_charge_id: The reference number of the pet charge that a credit reduces; leave "" if unknown.
        source_incident_id: The reference number of the incident that a fine bills; leave "" if unknown.
    """
    match = {k: v for k, v in {"pet_charge_id": pet_charge_id, "pet_addendum_id": pet_addendum_id, "customer_id": customer_id, "source_pet_charge_id": source_pet_charge_id, "source_incident_id": source_incident_id}.items() if v}
    rows = ctx.find("pet_charges", **match)
    return str(rows) if rows else f"No pet charges records match {match}."

@tool(owner="agent", rw="read")
def find_pet_incidents(ctx: ToolContext, incident_id: str = "", pet_addendum_id: str = "", customer_id: str = "") -> str:
    """Look up pet incidents — date, what happened and the enforcement step taken.

    Search by any reference number you already hold; every criterion is optional and several may be combined.
    Returns every matching incident. When nothing matches, a short not-found message is returned.

    Args:
        incident_id: The reference number of the incident itself; leave "" if unknown.
        pet_addendum_id: The reference number of the pet addendum or assistance animal registration; leave "" if unknown.
        customer_id: The resident's customer reference number (the resident the record belongs to); leave "" if unknown.
    """
    match = {k: v for k, v in {"incident_id": incident_id, "pet_addendum_id": pet_addendum_id, "customer_id": customer_id}.items() if v}
    rows = ctx.find("pet_incidents", **match)
    return str(rows) if rows else f"No pet incidents records match {match}."


@tool(owner="agent", rw="write")
def verify_resident_identity(ctx: ToolContext, customer_id: str, phone_number: str = "", email: str = "",
                             date_of_birth: str = "", ssn_last4: str = "") -> str:
    """Verify the caller's identity against the resident profile and record the outcome.

    Identity must be verified before any account information is discussed or any account is changed. This tool
    performs the comparison itself: it compares each piece of identity information the caller states with the
    resident profile, counts the matches, and verifies the caller only when at least 2 of them match. The customer
    reference number only retrieves the profile and never counts as a match. Callers usually state only some of
    these details, so pass exactly what the caller said and leave the rest empty. The outcome is recorded; if a
    first attempt fails and a later attempt with more details passes, the resident stays verified.

    Args:
        customer_id: The customer reference number read from the resident profile lookup; required.
        phone_number: The mobile number the caller states, written NNN-NNN-NNNN; leave "" if not stated.
        email: The email address the caller states; leave "" if not stated.
        date_of_birth: The date of birth the caller states, written YYYY-MM-DD; leave "" if not stated.
        ssn_last4: The last four digits of the Social Security or ITIN number the caller states; leave "" if not stated.
    """
    if not customer_id:
        return "Error: customer_id is required; look the resident up first and pass their reference number."
    rows = ctx.find("customers", customer_id=customer_id)
    if not rows:
        return f"Error: no resident profile {customer_id}; identity cannot be verified."
    rec = rows[0]
    # the locator customer_id is deliberately not a credential
    supplied = {"phone_number": phone_number, "email": email, "date_of_birth": date_of_birth,
                "ssn_last4": ssn_last4}
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
    if verified:
        return f"Identity verified for resident {customer_id} ({matched} detail(s) matched on this attempt)."
    return (f"Identity NOT verified for resident {customer_id}: only {matched} of the 2 required details matched. "
            "Ask the caller for another detail on the profile and try again.")


@tool(owner="agent", rw="write")
def transfer_to_human_agent(ctx: ToolContext, customer_id: str, reason: str) -> str:
    """Hand the resident over to a human resident services specialist and record why.

    Use POLICY_NOT_COVERED when no Larkspur policy can resolve what the resident is asking for, and
    CUSTOMER_REQUESTED when the resident has explicitly asked to speak with a person 2 times. The handoff is
    recorded with the time it was made.

    Args:
        customer_id: The customer reference number read from the resident profile lookup.
        reason: Exactly one of POLICY_NOT_COVERED (no policy can resolve the request) or CUSTOMER_REQUESTED (the
            resident has explicitly asked for a person 2 times); never free text.
    """
    allowed = {"POLICY_NOT_COVERED", "CUSTOMER_REQUESTED"}
    if reason not in allowed:
        return f"Error: unknown handoff reason '{reason}'. Valid: {', '.join(sorted(allowed))}."
    if not ctx.find("customers", customer_id=customer_id):
        return f"Error: no resident profile {customer_id}; the handoff cannot be recorded."
    rid = ctx.make_id("hof_", customer_id, reason)
    ctx.create("handoffs", rid, handoff_id=rid, customer_id=customer_id, reason=reason, created_at=ctx.now())
    return f"Handoff to a human resident services specialist recorded for {customer_id} ({reason})."

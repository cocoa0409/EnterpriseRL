"""Shared tools for env_0062_tire_and_auto_service_chain (Crestline Tire & Auto Care).

Share tools are always present in their owner's tool list. This module holds the record-lookup
layer (one finder per record type; the customers finder is also the identity entry), the identity
verification write, and the transfer to a human representative. Business actions on each product
line live in that difficulty's task_tools.py.
"""

from erlbench import ToolContext, tool


@tool(owner="agent", rw="read")
def find_customers(ctx: ToolContext, customer_id: str = "", store_id: str = "", phone_number: str = "",
                   email: str = "", full_name: str = "") -> str:
    """Find the customer profile a call is about. A profile can be found by its customer reference
    number, or by what a caller can naturally tell you: the phone number on the profile, the email
    address, or the full name (for a business, the authorized contact's name). Every criterion is
    optional; supply whichever are known, and add another one when several profiles match.

    The returned profile shows the customer reference number, name, phone number, email address,
    billing ZIP code, date of birth, the date the profile was opened, whether it is an individual or a
    business profile (with the business name), and the home store. Finding a profile does not confirm
    that the caller is that customer; identity is confirmed separately.

    Args:
        customer_id: Customer reference number; leave "" if unknown.
        store_id: Store reference number of the customer's home store; leave "" if unknown.
        phone_number: Phone number on the profile as the caller states it, 10 digits; leave "" if not provided.
        email: Email address on the profile as the caller states it; leave "" if not provided.
        full_name: Full name on the profile as the caller states it; leave "" if not provided.
    """
    match = {k: v for k, v in {"customer_id": customer_id, "store_id": store_id, "phone_number": phone_number,
                               "email": email, "full_name": full_name}.items() if v}
    if not match:
        return "Error: provide at least one reference number or profile detail to find the customer."
    rows = ctx.fuzzy_find("customers", **match)
    if not rows:
        return f"No customer matches {match}."
    if len(rows) > 1:
        return f"Error: {len(rows)} customers match {match}; ask for one more detail to tell them apart."
    return str(rows[0])


@tool(owner="agent", rw="read")
def find_stores(ctx: ToolContext, store_id: str = "", store_number: str = "") -> str:
    """Look up Crestline store details: store number, name, city, state, operating region and the number of service bays. Search by the store reference number or by the four-digit store number printed on tickets; with no criteria at all, every store is listed.

    Every criterion is optional; supply whichever reference numbers are known. Returns the matching
    records, or a message saying none were found.

    Args:
        store_id: Store reference number of the Crestline store involved; leave "" if unknown.
        store_number: The four-digit store number printed on tickets and invoices (for example 0417); leave "" if unknown.
    """
    match = {k: v for k, v in {"store_id": store_id, "store_number": store_number}.items() if v}
    rows = ctx.find("stores", **match)
    return str(rows) if rows else f"No matching records found for {match}."


@tool(owner="agent", rw="read")
def find_vehicles(ctx: ToolContext, vehicle_id: str = "", customer_id: str = "") -> str:
    """Look up the vehicles on file: VIN, model year, make, model, fitment class, whether the vehicle is recorded for personal or commercial use, its tire pressure monitoring type and license plate. Search by the vehicle reference number or by the customer the vehicle is registered to.

    Every criterion is optional; supply whichever reference numbers are known. Returns the matching
    records, or a message saying none were found.

    Args:
        vehicle_id: Vehicle reference number of the vehicle involved; leave "" if unknown.
        customer_id: Customer reference number of the profile the records belong to; leave "" if unknown.
    """
    match = {k: v for k, v in {"vehicle_id": vehicle_id, "customer_id": customer_id}.items() if v}
    rows = ctx.find("vehicles", **match)
    return str(rows) if rows else f"No matching records found for {match}."


@tool(owner="agent", rw="read")
def find_tire_sets(ctx: ToolContext, tire_set_id: str = "", customer_id: str = "", vehicle_id: str = "", store_id: str = "") -> str:
    """Look up tire purchases and their treadwear limited warranties: tire line and warranty class, status (ordered, active, returned, cancelled, worn out, retired), purchase and installation dates, installation odometer, tire count and size, price per tire, ticket number, tender used, and any treadwear adjustment credit still available on the set.

    Every criterion is optional; supply whichever reference numbers are known. Returns the matching
    records, or a message saying none were found.

    Args:
        tire_set_id: Reference number of the tire set (one tire purchase for one vehicle); leave "" if unknown.
        customer_id: Customer reference number of the profile the records belong to; leave "" if unknown.
        vehicle_id: Vehicle reference number of the vehicle involved; leave "" if unknown.
        store_id: Store reference number of the Crestline store involved; leave "" if unknown.
    """
    match = {k: v for k, v in {"tire_set_id": tire_set_id, "customer_id": customer_id, "vehicle_id": vehicle_id, "store_id": store_id}.items() if v}
    rows = ctx.find("tire_sets", **match)
    return str(rows) if rows else f"No matching records found for {match}."


@tool(owner="agent", rw="read")
def find_tire_events(ctx: ToolContext, tire_event_id: str = "", tire_set_id: str = "", customer_id: str = "", store_id: str = "", source_tire_event_id: str = "") -> str:
    """Look up the activity history of a tire set: installation bookings, rotations, tread inspections with measured depth and wear pattern, treadwear adjustments and their credits, workmanship replacements, credit use and expiry, and refunds.

    Every criterion is optional; supply whichever reference numbers are known. Returns the matching
    records, or a message saying none were found.

    Args:
        tire_event_id: Reference number of the tire activity entry itself; leave "" if unknown.
        tire_set_id: Reference number of the tire set (one tire purchase for one vehicle); leave "" if unknown.
        customer_id: Customer reference number of the profile the records belong to; leave "" if unknown.
        store_id: Store reference number of the Crestline store involved; leave "" if unknown.
        source_tire_event_id: Reference number of the earlier tire activity entry this one derives from (the inspection behind an adjustment, or the adjustment whose credit is used); leave "" if unknown.
    """
    match = {k: v for k, v in {"tire_event_id": tire_event_id, "tire_set_id": tire_set_id, "customer_id": customer_id, "store_id": store_id, "source_tire_event_id": source_tire_event_id}.items() if v}
    rows = ctx.find("tire_events", **match)
    return str(rows) if rows else f"No matching records found for {match}."


@tool(owner="agent", rw="read")
def find_tire_return_requests(ctx: ToolContext, tire_return_request_id: str = "", customer_id: str = "", tire_set_id: str = "") -> str:
    """Look up satisfaction-trial return requests registered for tire sets, with the requested remedy, the odometer reported and whether the customer has confirmed.

    Every criterion is optional; supply whichever reference numbers are known. Returns the matching
    records, or a message saying none were found.

    Args:
        tire_return_request_id: Reference number of the satisfaction-trial return request itself; leave "" if unknown.
        customer_id: Customer reference number of the profile the records belong to; leave "" if unknown.
        tire_set_id: Reference number of the tire set (one tire purchase for one vehicle); leave "" if unknown.
    """
    match = {k: v for k, v in {"tire_return_request_id": tire_return_request_id, "customer_id": customer_id, "tire_set_id": tire_set_id}.items() if v}
    rows = ctx.find("tire_return_requests", **match)
    return str(rows) if rows else f"No matching records found for {match}."


@tool(owner="agent", rw="read")
def find_hazard_certificates(ctx: ToolContext, hazard_certificate_id: str = "", customer_id: str = "", tire_set_id: str = "", vehicle_id: str = "", store_id: str = "") -> str:
    """Look up road hazard protection certificates: plan held, status, the tire set covered, purchase, coverage start and expiration dates, tires covered, price per tire, certificate number and the roadside calls still available.

    Every criterion is optional; supply whichever reference numbers are known. Returns the matching
    records, or a message saying none were found.

    Args:
        hazard_certificate_id: Reference number of the road hazard certificate; leave "" if unknown.
        customer_id: Customer reference number of the profile the records belong to; leave "" if unknown.
        tire_set_id: Reference number of the tire set (one tire purchase for one vehicle); leave "" if unknown.
        vehicle_id: Vehicle reference number of the vehicle involved; leave "" if unknown.
        store_id: Store reference number of the Crestline store involved; leave "" if unknown.
    """
    match = {k: v for k, v in {"hazard_certificate_id": hazard_certificate_id, "customer_id": customer_id, "tire_set_id": tire_set_id, "vehicle_id": vehicle_id, "store_id": store_id}.items() if v}
    rows = ctx.find("hazard_certificates", **match)
    return str(rows) if rows else f"No matching records found for {match}."


@tool(owner="agent", rw="read")
def find_hazard_events(ctx: ToolContext, hazard_event_id: str = "", hazard_certificate_id: str = "", customer_id: str = "", store_id: str = "") -> str:
    """Look up road hazard activity on a certificate: repairs, replacements with coverage percentage and amounts paid, out-of-area reimbursements, roadside calls, roadside allowances and cancellation refunds, each with its claim number where one was opened.

    Every criterion is optional; supply whichever reference numbers are known. Returns the matching
    records, or a message saying none were found.

    Args:
        hazard_event_id: Reference number of the road hazard activity entry itself; leave "" if unknown.
        hazard_certificate_id: Reference number of the road hazard certificate; leave "" if unknown.
        customer_id: Customer reference number of the profile the records belong to; leave "" if unknown.
        store_id: Store reference number of the Crestline store involved; leave "" if unknown.
    """
    match = {k: v for k, v in {"hazard_event_id": hazard_event_id, "hazard_certificate_id": hazard_certificate_id, "customer_id": customer_id, "store_id": store_id}.items() if v}
    rows = ctx.find("hazard_events", **match)
    return str(rows) if rows else f"No matching records found for {match}."


@tool(owner="agent", rw="read")
def find_hazard_cancellation_requests(ctx: ToolContext, hazard_cancel_request_id: str = "", customer_id: str = "", hazard_certificate_id: str = "") -> str:
    """Look up road hazard certificate cancellation requests and whether the holder has confirmed them.

    Every criterion is optional; supply whichever reference numbers are known. Returns the matching
    records, or a message saying none were found.

    Args:
        hazard_cancel_request_id: Reference number of the certificate cancellation request itself; leave "" if unknown.
        customer_id: Customer reference number of the profile the records belong to; leave "" if unknown.
        hazard_certificate_id: Reference number of the road hazard certificate; leave "" if unknown.
    """
    match = {k: v for k, v in {"hazard_cancel_request_id": hazard_cancel_request_id, "customer_id": customer_id, "hazard_certificate_id": hazard_certificate_id}.items() if v}
    rows = ctx.find("hazard_cancellation_requests", **match)
    return str(rows) if rows else f"No matching records found for {match}."


@tool(owner="agent", rw="read")
def find_card_accounts(ctx: ToolContext, card_account_id: str = "", customer_id: str = "", store_id: str = "") -> str:
    """Look up Crestline credit card accounts: card product, status, application and opening dates, credit limit, purchase APR, last four digits, statement closing day, autopay enrollment and the current balance owed.

    Every criterion is optional; supply whichever reference numbers are known. Returns the matching
    records, or a message saying none were found.

    Args:
        card_account_id: Reference number of the Crestline credit card account; leave "" if unknown.
        customer_id: Customer reference number of the profile the records belong to; leave "" if unknown.
        store_id: Store reference number of the Crestline store involved; leave "" if unknown.
    """
    match = {k: v for k, v in {"card_account_id": card_account_id, "customer_id": customer_id, "store_id": store_id}.items() if v}
    rows = ctx.find("card_accounts", **match)
    return str(rows) if rows else f"No matching records found for {match}."


@tool(owner="agent", rw="read")
def find_card_transactions(ctx: ToolContext, card_txn_id: str = "", card_account_id: str = "", customer_id: str = "", store_id: str = "", source_card_txn_id: str = "") -> str:
    """Look up card account activity: purchases with any promotional plan and its expiration date, statements with minimum payment and due date, payments and how they were allocated to promotional purchases, interest, deferred interest accruals and assessments, fees, merchandise credits and fee reversals.

    Every criterion is optional; supply whichever reference numbers are known. Returns the matching
    records, or a message saying none were found.

    Args:
        card_txn_id: Reference number of the card activity entry itself; leave "" if unknown.
        card_account_id: Reference number of the Crestline credit card account; leave "" if unknown.
        customer_id: Customer reference number of the profile the records belong to; leave "" if unknown.
        store_id: Store reference number of the Crestline store involved; leave "" if unknown.
        source_card_txn_id: Reference number of the earlier card entry this one concerns (the promotional purchase, or the fee being reversed); leave "" if unknown.
    """
    match = {k: v for k, v in {"card_txn_id": card_txn_id, "card_account_id": card_account_id, "customer_id": customer_id, "store_id": store_id, "source_card_txn_id": source_card_txn_id}.items() if v}
    rows = ctx.find("card_transactions", **match)
    return str(rows) if rows else f"No matching records found for {match}."


@tool(owner="agent", rw="read")
def find_card_requests(ctx: ToolContext, card_request_id: str = "", customer_id: str = "", card_account_id: str = "", source_card_txn_id: str = "") -> str:
    """Look up requests a cardholder has made on a card account (closure, billing dispute, payment allocation instruction, credit limit increase) and their status.

    Every criterion is optional; supply whichever reference numbers are known. Returns the matching
    records, or a message saying none were found.

    Args:
        card_request_id: Reference number of the cardholder request itself; leave "" if unknown.
        customer_id: Customer reference number of the profile the records belong to; leave "" if unknown.
        card_account_id: Reference number of the Crestline credit card account; leave "" if unknown.
        source_card_txn_id: Reference number of the earlier card entry this one concerns (the promotional purchase, or the fee being reversed); leave "" if unknown.
    """
    match = {k: v for k, v in {"card_request_id": card_request_id, "customer_id": customer_id, "card_account_id": card_account_id, "source_card_txn_id": source_card_txn_id}.items() if v}
    rows = ctx.find("card_requests", **match)
    return str(rows) if rows else f"No matching records found for {match}."


@tool(owner="agent", rw="read")
def find_fleet_accounts(ctx: ToolContext, fleet_account_id: str = "", customer_id: str = "", store_id: str = "") -> str:
    """Look up Crestline fleet accounts: fleet program, status, business legal name, application and approval dates, credit limit, ticket approval limit, purchase order requirement, billing cycle, tax exemption and the outstanding balance.

    Every criterion is optional; supply whichever reference numbers are known. Returns the matching
    records, or a message saying none were found.

    Args:
        fleet_account_id: Reference number of the fleet account; leave "" if unknown.
        customer_id: Customer reference number of the profile the records belong to; leave "" if unknown.
        store_id: Store reference number of the Crestline store involved; leave "" if unknown.
    """
    match = {k: v for k, v in {"fleet_account_id": fleet_account_id, "customer_id": customer_id, "store_id": store_id}.items() if v}
    rows = ctx.find("fleet_accounts", **match)
    return str(rows) if rows else f"No matching records found for {match}."


@tool(owner="agent", rw="read")
def find_fleet_transactions(ctx: ToolContext, fleet_txn_id: str = "", fleet_account_id: str = "", customer_id: str = "", vehicle_id: str = "", store_id: str = "", source_fleet_txn_id: str = "") -> str:
    """Look up fleet account activity: invoices with purchase order, vehicle, service category, discount and due date; remittances applied; early-pay discounts; late charges; and credit memos.

    Every criterion is optional; supply whichever reference numbers are known. Returns the matching
    records, or a message saying none were found.

    Args:
        fleet_txn_id: Reference number of the fleet invoice or account entry; leave "" if unknown.
        fleet_account_id: Reference number of the fleet account; leave "" if unknown.
        customer_id: Customer reference number of the profile the records belong to; leave "" if unknown.
        vehicle_id: Vehicle reference number of the vehicle involved; leave "" if unknown.
        store_id: Store reference number of the Crestline store involved; leave "" if unknown.
        source_fleet_txn_id: Reference number of the fleet invoice a payment, discount or credit memo applies to; leave "" if unknown.
    """
    match = {k: v for k, v in {"fleet_txn_id": fleet_txn_id, "fleet_account_id": fleet_account_id, "customer_id": customer_id, "vehicle_id": vehicle_id, "store_id": store_id, "source_fleet_txn_id": source_fleet_txn_id}.items() if v}
    rows = ctx.find("fleet_transactions", **match)
    return str(rows) if rows else f"No matching records found for {match}."


@tool(owner="agent", rw="read")
def find_fleet_roster_events(ctx: ToolContext, fleet_roster_event_id: str = "", fleet_account_id: str = "", customer_id: str = "", vehicle_id: str = "") -> str:
    """Look up the roster history of a fleet account: each vehicle added or removed, the effective date and the business's unit number.

    Every criterion is optional; supply whichever reference numbers are known. Returns the matching
    records, or a message saying none were found.

    Args:
        fleet_roster_event_id: Reference number of the roster change entry itself; leave "" if unknown.
        fleet_account_id: Reference number of the fleet account; leave "" if unknown.
        customer_id: Customer reference number of the profile the records belong to; leave "" if unknown.
        vehicle_id: Vehicle reference number of the vehicle involved; leave "" if unknown.
    """
    match = {k: v for k, v in {"fleet_roster_event_id": fleet_roster_event_id, "fleet_account_id": fleet_account_id, "customer_id": customer_id, "vehicle_id": vehicle_id}.items() if v}
    rows = ctx.find("fleet_roster_events", **match)
    return str(rows) if rows else f"No matching records found for {match}."


@tool(owner="agent", rw="read")
def find_fleet_invoice_disputes(ctx: ToolContext, fleet_dispute_id: str = "", customer_id: str = "", fleet_account_id: str = "", fleet_txn_id: str = "") -> str:
    """Look up invoice disputes raised on a fleet account, with the reason, the amount disputed and the status.

    Every criterion is optional; supply whichever reference numbers are known. Returns the matching
    records, or a message saying none were found.

    Args:
        fleet_dispute_id: Reference number of the invoice dispute itself; leave "" if unknown.
        customer_id: Customer reference number of the profile the records belong to; leave "" if unknown.
        fleet_account_id: Reference number of the fleet account; leave "" if unknown.
        fleet_txn_id: Reference number of the fleet invoice or account entry; leave "" if unknown.
    """
    match = {k: v for k, v in {"fleet_dispute_id": fleet_dispute_id, "customer_id": customer_id, "fleet_account_id": fleet_account_id, "fleet_txn_id": fleet_txn_id}.items() if v}
    rows = ctx.find("fleet_invoice_disputes", **match)
    return str(rows) if rows else f"No matching records found for {match}."


@tool(owner="agent", rw="read")
def find_alignment_plans(ctx: ToolContext, alignment_plan_id: str = "", customer_id: str = "", vehicle_id: str = "", store_id: str = "") -> str:
    """Look up alignment services and plans: service or plan held, status, the vehicle it is valid on, purchase date and odometer, expiration date, price paid, ticket number and tender used.

    Every criterion is optional; supply whichever reference numbers are known. Returns the matching
    records, or a message saying none were found.

    Args:
        alignment_plan_id: Reference number of the alignment service or plan; leave "" if unknown.
        customer_id: Customer reference number of the profile the records belong to; leave "" if unknown.
        vehicle_id: Vehicle reference number of the vehicle involved; leave "" if unknown.
        store_id: Store reference number of the Crestline store involved; leave "" if unknown.
    """
    match = {k: v for k, v in {"alignment_plan_id": alignment_plan_id, "customer_id": customer_id, "vehicle_id": vehicle_id, "store_id": store_id}.items() if v}
    rows = ctx.find("alignment_plans", **match)
    return str(rows) if rows else f"No matching records found for {match}."


@tool(owner="agent", rw="read")
def find_alignment_events(ctx: ToolContext, alignment_event_id: str = "", alignment_plan_id: str = "", customer_id: str = "", store_id: str = "", source_alignment_event_id: str = "") -> str:
    """Look up alignment activity on a plan: appointments booked, alignments performed and how each was paid, free readjustments and refunds.

    Every criterion is optional; supply whichever reference numbers are known. Returns the matching
    records, or a message saying none were found.

    Args:
        alignment_event_id: Reference number of the alignment activity entry itself; leave "" if unknown.
        alignment_plan_id: Reference number of the alignment service or plan; leave "" if unknown.
        customer_id: Customer reference number of the profile the records belong to; leave "" if unknown.
        store_id: Store reference number of the Crestline store involved; leave "" if unknown.
        source_alignment_event_id: Reference number of the alignment a readjustment corrects; leave "" if unknown.
    """
    match = {k: v for k, v in {"alignment_event_id": alignment_event_id, "alignment_plan_id": alignment_plan_id, "customer_id": customer_id, "store_id": store_id, "source_alignment_event_id": source_alignment_event_id}.items() if v}
    rows = ctx.find("alignment_events", **match)
    return str(rows) if rows else f"No matching records found for {match}."


@tool(owner="agent", rw="read")
def find_alignment_cancellation_requests(ctx: ToolContext, alignment_cancel_request_id: str = "", customer_id: str = "", alignment_plan_id: str = "") -> str:
    """Look up alignment plan cancellation requests and whether the holder has confirmed them.

    Every criterion is optional; supply whichever reference numbers are known. Returns the matching
    records, or a message saying none were found.

    Args:
        alignment_cancel_request_id: Reference number of the plan cancellation request itself; leave "" if unknown.
        customer_id: Customer reference number of the profile the records belong to; leave "" if unknown.
        alignment_plan_id: Reference number of the alignment service or plan; leave "" if unknown.
    """
    match = {k: v for k, v in {"alignment_cancel_request_id": alignment_cancel_request_id, "customer_id": customer_id, "alignment_plan_id": alignment_plan_id}.items() if v}
    rows = ctx.find("alignment_cancellation_requests", **match)
    return str(rows) if rows else f"No matching records found for {match}."


@tool(owner="agent", rw="read")
def find_brake_warranties(ctx: ToolContext, brake_warranty_id: str = "", customer_id: str = "", vehicle_id: str = "", store_id: str = "") -> str:
    """Look up brake service warranties: brake line and warranty, status, the vehicle and axle serviced, service date and odometer, repair order number, pad and labor charges, rotor work and tender used.

    Every criterion is optional; supply whichever reference numbers are known. Returns the matching
    records, or a message saying none were found.

    Args:
        brake_warranty_id: Reference number of the brake service warranty (one brake job on one axle); leave "" if unknown.
        customer_id: Customer reference number of the profile the records belong to; leave "" if unknown.
        vehicle_id: Vehicle reference number of the vehicle involved; leave "" if unknown.
        store_id: Store reference number of the Crestline store involved; leave "" if unknown.
    """
    match = {k: v for k, v in {"brake_warranty_id": brake_warranty_id, "customer_id": customer_id, "vehicle_id": vehicle_id, "store_id": store_id}.items() if v}
    rows = ctx.find("brake_warranties", **match)
    return str(rows) if rows else f"No matching records found for {match}."


@tool(owner="agent", rw="read")
def find_brake_events(ctx: ToolContext, brake_event_id: str = "", brake_warranty_id: str = "", customer_id: str = "", store_id: str = "", source_brake_event_id: str = "") -> str:
    """Look up brake activity on a warranty: appointments, inspections with measured pad thickness and finding, warranty pad replacements, noise services and rotor work, with the charges on each repair order.

    Every criterion is optional; supply whichever reference numbers are known. Returns the matching
    records, or a message saying none were found.

    Args:
        brake_event_id: Reference number of the brake activity entry itself; leave "" if unknown.
        brake_warranty_id: Reference number of the brake service warranty (one brake job on one axle); leave "" if unknown.
        customer_id: Customer reference number of the profile the records belong to; leave "" if unknown.
        store_id: Store reference number of the Crestline store involved; leave "" if unknown.
        source_brake_event_id: Reference number of the inspection a brake warranty visit rests on; leave "" if unknown.
    """
    match = {k: v for k, v in {"brake_event_id": brake_event_id, "brake_warranty_id": brake_warranty_id, "customer_id": customer_id, "store_id": store_id, "source_brake_event_id": source_brake_event_id}.items() if v}
    rows = ctx.find("brake_events", **match)
    return str(rows) if rows else f"No matching records found for {match}."


@tool(owner="agent", rw="read")
def find_battery_warranties(ctx: ToolContext, battery_warranty_id: str = "", customer_id: str = "", vehicle_id: str = "", store_id: str = "") -> str:
    """Look up battery warranties: battery line, status, the vehicle, purchase date, installed or carry-out, group size, price paid, ticket number, tender, whether a core was handed in and any core deposit still held.

    Every criterion is optional; supply whichever reference numbers are known. Returns the matching
    records, or a message saying none were found.

    Args:
        battery_warranty_id: Reference number of the battery warranty (one battery sold); leave "" if unknown.
        customer_id: Customer reference number of the profile the records belong to; leave "" if unknown.
        vehicle_id: Vehicle reference number of the vehicle involved; leave "" if unknown.
        store_id: Store reference number of the Crestline store involved; leave "" if unknown.
    """
    match = {k: v for k, v in {"battery_warranty_id": battery_warranty_id, "customer_id": customer_id, "vehicle_id": vehicle_id, "store_id": store_id}.items() if v}
    rows = ctx.find("battery_warranties", **match)
    return str(rows) if rows else f"No matching records found for {match}."


@tool(owner="agent", rw="read")
def find_battery_events(ctx: ToolContext, battery_event_id: str = "", battery_warranty_id: str = "", customer_id: str = "", store_id: str = "", source_battery_event_id: str = "") -> str:
    """Look up battery activity: core deposits charged, refunded or forfeited, battery tests with measured cranking amps, free replacements, prorated adjustments and carry-out refunds.

    Every criterion is optional; supply whichever reference numbers are known. Returns the matching
    records, or a message saying none were found.

    Args:
        battery_event_id: Reference number of the battery activity entry itself; leave "" if unknown.
        battery_warranty_id: Reference number of the battery warranty (one battery sold); leave "" if unknown.
        customer_id: Customer reference number of the profile the records belong to; leave "" if unknown.
        store_id: Store reference number of the Crestline store involved; leave "" if unknown.
        source_battery_event_id: Reference number of the earlier battery entry this one rests on (the test behind a replacement, or the core deposit being settled); leave "" if unknown.
    """
    match = {k: v for k, v in {"battery_event_id": battery_event_id, "battery_warranty_id": battery_warranty_id, "customer_id": customer_id, "store_id": store_id, "source_battery_event_id": source_battery_event_id}.items() if v}
    rows = ctx.find("battery_events", **match)
    return str(rows) if rows else f"No matching records found for {match}."


@tool(owner="agent", rw="read")
def find_identity_verifications(ctx: ToolContext, verification_id: str = "", customer_id: str = "") -> str:
    """Look up the outcome of identity verification for a customer during this contact: whether verification has passed and when it was last attempted.

    Every criterion is optional; supply whichever reference numbers are known. Returns the matching
    records, or a message saying none were found.

    Args:
        verification_id: Reference number of the verification record itself; leave "" if unknown.
        customer_id: Customer reference number of the profile the records belong to; leave "" if unknown.
    """
    match = {k: v for k, v in {"verification_id": verification_id, "customer_id": customer_id}.items() if v}
    rows = ctx.find("identity_verifications", **match)
    return str(rows) if rows else f"No matching records found for {match}."


@tool(owner="agent", rw="read")
def find_handoff_log(ctx: ToolContext, handoff_id: str = "", customer_id: str = "") -> str:
    """Look up handoffs to a human representative already recorded for a customer, with the reason and the time each was recorded.

    Every criterion is optional; supply whichever reference numbers are known. Returns the matching
    records, or a message saying none were found.

    Args:
        handoff_id: Reference number of the handoff record itself; leave "" if unknown.
        customer_id: Customer reference number of the profile the records belong to; leave "" if unknown.
    """
    match = {k: v for k, v in {"handoff_id": handoff_id, "customer_id": customer_id}.items() if v}
    rows = ctx.find("handoff_log", **match)
    return str(rows) if rows else f"No matching records found for {match}."


@tool(owner="agent", rw="write")
def verify_customer_identity(ctx: ToolContext, customer_id: str, phone_number: str = "", email: str = "",
                             billing_zip_code: str = "", date_of_birth: str = "") -> str:
    """Confirm that the caller is the customer on the profile and record the result. Identity must be
    confirmed before any account, warranty, card or fleet business is looked into or transacted for
    the caller. This tool makes the comparison itself: it compares each detail the caller states with
    the profile on file, counts how many match, and confirms identity only when at least 2 of them
    match. The customer reference number only selects the profile and never counts as a match. Pass
    exactly what the caller said for each detail they gave and leave the others empty. The result is
    recorded; if a first attempt does not pass and a later attempt with more details does, the later
    pass stands.

    Args:
        customer_id: Customer reference number, taken from the customer profile lookup. Required; it selects the profile and does not count toward the matches.
        phone_number: Phone number the caller states, 10 digits without punctuation; leave "" if not stated.
        email: Email address the caller states; leave "" if not stated.
        billing_zip_code: Five-digit ZIP code of the billing address the caller states; leave "" if not stated.
        date_of_birth: Date of birth the caller states, as YYYY-MM-DD (for a business profile, the authorized contact's); leave "" if not stated.
    """
    if not customer_id:
        return "Error: customer_id is required; find the customer profile first and pass its reference number."
    rows = ctx.find("customers", customer_id=customer_id)
    if not rows:
        return f"Error: no customer {customer_id}; identity cannot be verified."
    rec = rows[0]
    # The tool owns the comparison; the locator customer_id is never counted as a credential.
    supplied = {"phone_number": phone_number, "email": email,
                "billing_zip_code": billing_zip_code, "date_of_birth": date_of_birth}
    matched = sum(1 for field, value in supplied.items()
                  if value and str(rec.get(field) or "").strip().lower() == str(value).strip().lower())
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
        return f"Identity verified for {customer_id}."
    return (f"Identity NOT verified for {customer_id} (only {matched} of the 2 required details matched). "
            "Ask the caller for another detail on file and try again.")


@tool(owner="agent", rw="write")
def transfer_to_human_agent(ctx: ToolContext, customer_id: str, reason: str) -> str:
    """Hand the customer over to a human Crestline representative and record the handoff with its
    reason. Use it in one of two situations only: when no Crestline policy allows the request to be
    resolved here, or when the customer has explicitly asked to speak with a human representative at
    least 2 times.

    Args:
        customer_id: Customer reference number, taken from the customer profile lookup.
        reason: Reason for the handoff, exactly one of POLICY_NOT_COVERED (no policy allows the request to be resolved here) or CUSTOMER_REQUESTED (the customer has explicitly asked for a human representative at least 2 times).
    """
    allowed = {"POLICY_NOT_COVERED", "CUSTOMER_REQUESTED"}
    if reason not in allowed:
        return f"Error: unknown handoff reason '{reason}'. Valid: {', '.join(sorted(allowed))}."
    if not ctx.find("customers", customer_id=customer_id):
        return f"Error: no customer {customer_id}; the handoff cannot be recorded."
    rid = ctx.make_id("hof_", customer_id, reason)
    ctx.create("handoff_log", rid, handoff_id=rid, customer_id=customer_id,
               reason=reason, created_at=ctx.now())
    return f"Handoff to a human representative recorded for {customer_id} ({reason})."

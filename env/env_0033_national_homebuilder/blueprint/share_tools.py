"""Shared tools for env_0033_national_homebuilder (Calloway Homes, Homebuyer and Warranty Services).

Every tool here is a SHARE tool, always visible: one record finder per kind of record (the
customers finder doubling as the identity entry), the identity-verification write and the
transfer-to-human write. Customer-originated actions live as hidden task tools per difficulty.
"""

from erlbench import ToolContext, tool


@tool(owner="agent", rw="read")
def find_customers(ctx: ToolContext, customer_id: str = "", full_name: str = "", phone: str = "", email: str = "") -> str:
    """Find the buyer or homeowner profile a call is about. You may search by the customer reference
    number, or by what the caller tells you: their full name, the phone number on their profile or
    their email address. Every criterion is optional; give whichever you have, and add another if more
    than one profile matches. A match returns the profile with its customer reference number, name,
    phone, email, mailing address and ZIP code, date of birth, last four digits of the Social Security
    number and the date the profile was opened. Finding a profile does not confirm who the caller is;
    identity is confirmed separately.

    Args:
        customer_id: The customer reference number, if already known; leave "" if unknown.
        full_name: The caller's full name as they state it; leave "" if not given.
        phone: The phone number the caller gives, 10 digits; leave "" if not given.
        email: The email address the caller gives; leave "" if not given.
    """
    match = {k: v for k, v in {"customer_id": customer_id, "full_name": full_name,
                               "phone": phone, "email": email}.items() if v}
    if not match:
        return "Error: provide at least one id or attribute to find the customer."
    rows = ctx.fuzzy_find("customers", **match)
    if not rows:
        return f"No customer matches {match}."
    if len(rows) > 1:
        return f"Error: {len(rows)} customers match {match}; ask for one more attribute to disambiguate."
    return str(rows[0])


@tool(owner="agent", rw="read")
def find_homesite_reservations(ctx: ToolContext, reservation_id: str = "", customer_id: str = "") -> str:
    """Look up Homesite Reservations: the reserved lot and community, its premium class, the
    reservation and hold expiry dates, extensions, swaps and reinstatements used, the money
    currently held and how the reservation ended. Every reference number below is optional; give
    any you hold and all matching records are returned, or a note that none was found.

    Args:
        reservation_id: The reference number of a Homesite Reservation; leave "" if unknown.
        customer_id: The customer reference number of the buyer or homeowner; leave "" if unknown.
    """
    match = {k: v for k, v in {"reservation_id": reservation_id, "customer_id": customer_id}.items() if v}
    rows = ctx.find("homesite_reservations", **match)
    return str(rows) if rows else f"No homesite_reservations records for {match}."


@tool(owner="agent", rw="read")
def find_homesite_ledger(ctx: ToolContext, homesite_event_id: str = "", reservation_id: str = "", customer_id: str = "") -> str:
    """Look up the money and notice history of Homesite Reservations: each payment received with
    its component, method and receipt number, each refund, transfer to a purchase agreement,
    retention or returned payment with the receipt number it came from, and each written notice
    sent. Every reference number below is optional; give any you hold and all matching records
    are returned, or a note that none was found.

    Args:
        homesite_event_id: The reference number of one reservation payment, refund, transfer, retention or notice entry; leave "" if unknown.
        reservation_id: The reference number of a Homesite Reservation; leave "" if unknown.
        customer_id: The customer reference number of the buyer or homeowner; leave "" if unknown.
    """
    match = {k: v for k, v in {"homesite_event_id": homesite_event_id, "reservation_id": reservation_id, "customer_id": customer_id}.items() if v}
    rows = ctx.find("homesite_events", **match)
    return str(rows) if rows else f"No homesite_events records for {match}."


@tool(owner="agent", rw="read")
def find_verification_records(ctx: ToolContext, verification_id: str = "", customer_id: str = "") -> str:
    """Look up identity verification outcomes recorded for a customer during this service, showing
    whether verification has passed and when it was last attempted. Every reference number below
    is optional; give any you hold and all matching records are returned, or a note that none
    was found.

    Args:
        verification_id: The reference number of an identity verification record; leave "" if unknown.
        customer_id: The customer reference number of the buyer or homeowner; leave "" if unknown.
    """
    match = {k: v for k, v in {"verification_id": verification_id, "customer_id": customer_id}.items() if v}
    rows = ctx.find("verification_log", **match)
    return str(rows) if rows else f"No verification_log records for {match}."


@tool(owner="agent", rw="read")
def find_handoff_records(ctx: ToolContext, handoff_id: str = "", customer_id: str = "") -> str:
    """Look up transfers to a human representative recorded for a customer, with the reason given
    and when the transfer was made. Every reference number below is optional; give any you hold
    and all matching records are returned, or a note that none was found.

    Args:
        handoff_id: The reference number of a transfer-to-representative record; leave "" if unknown.
        customer_id: The customer reference number of the buyer or homeowner; leave "" if unknown.
    """
    match = {k: v for k, v in {"handoff_id": handoff_id, "customer_id": customer_id}.items() if v}
    rows = ctx.find("handoff_log", **match)
    return str(rows) if rows else f"No handoff_log records for {match}."


@tool(owner="agent", rw="read")
def find_purchase_agreements(ctx: ToolContext, purchase_id: str = "", customer_id: str = "", reservation_id: str = "") -> str:
    """Look up Home Purchase Agreements: the collection, community, lot and plan, base price, lot
    premium and contract price, the contract, completion and closing dates, the construction
    stage, financing type, home-sale contingency, extensions and transfers used, and the
    deposits, charges and incentives currently on the agreement. Every reference number below is
    optional; give any you hold and all matching records are returned, or a note that none was
    found.

    Args:
        purchase_id: The reference number of a Home Purchase Agreement; leave "" if unknown.
        customer_id: The customer reference number of the buyer or homeowner; leave "" if unknown.
        reservation_id: The reference number of a Homesite Reservation; leave "" if unknown.
    """
    match = {k: v for k, v in {"purchase_id": purchase_id, "customer_id": customer_id, "reservation_id": reservation_id}.items() if v}
    rows = ctx.find("purchase_agreements", **match)
    return str(rows) if rows else f"No purchase_agreements records for {match}."


@tool(owner="agent", rw="read")
def find_purchase_ledger(ctx: ToolContext, purchase_event_id: str = "", purchase_id: str = "", customer_id: str = "") -> str:
    """Look up the money and notice history of Home Purchase Agreements: deposits posted by
    component and receipt number, charges by charge number with any per diem period, waivers and
    collections, refunds, forfeitures and closing credits by source receipt, incentives granted,
    revoked or applied, returned payments and written contract notices. Every reference number
    below is optional; give any you hold and all matching records are returned, or a note that
    none was found.

    Args:
        purchase_event_id: The reference number of one purchase agreement deposit, charge, incentive, refund or notice entry; leave "" if unknown.
        purchase_id: The reference number of a Home Purchase Agreement; leave "" if unknown.
        customer_id: The customer reference number of the buyer or homeowner; leave "" if unknown.
    """
    match = {k: v for k, v in {"purchase_event_id": purchase_event_id, "purchase_id": purchase_id, "customer_id": customer_id}.items() if v}
    rows = ctx.find("purchase_events", **match)
    return str(rows) if rows else f"No purchase_events records for {match}."


@tool(owner="agent", rw="read")
def find_purchase_cancellation_requests(ctx: ToolContext, cancellation_request_id: str = "", purchase_id: str = "", customer_id: str = "") -> str:
    """Look up cancellation requests lodged on Home Purchase Agreements, with the basis the buyer
    gave, the date it was received and whether it is still awaiting the buyer's confirmation,
    confirmed or withdrawn. Every reference number below is optional; give any you hold and all
    matching records are returned, or a note that none was found.

    Args:
        cancellation_request_id: The reference number of a purchase agreement cancellation request; leave "" if unknown.
        purchase_id: The reference number of a Home Purchase Agreement; leave "" if unknown.
        customer_id: The customer reference number of the buyer or homeowner; leave "" if unknown.
    """
    match = {k: v for k, v in {"cancellation_request_id": cancellation_request_id, "purchase_id": purchase_id, "customer_id": customer_id}.items() if v}
    rows = ctx.find("purchase_cancellation_requests", **match)
    return str(rows) if rows else f"No purchase_cancellation_requests records for {match}."


@tool(owner="agent", rw="read")
def find_design_files(ctx: ToolContext, selection_id: str = "", customer_id: str = "", purchase_id: str = "") -> str:
    """Look up Design Studio Selections files: the package, the purchase agreement served, the date
    opened and the first appointment date, the file's status, its option total, option deposits
    held and design credit available. Every reference number below is optional; give any you
    hold and all matching records are returned, or a note that none was found.

    Args:
        selection_id: The reference number of a Design Studio Selections file; leave "" if unknown.
        customer_id: The customer reference number of the buyer or homeowner; leave "" if unknown.
        purchase_id: The reference number of a Home Purchase Agreement; leave "" if unknown.
    """
    match = {k: v for k, v in {"selection_id": selection_id, "customer_id": customer_id, "purchase_id": purchase_id}.items() if v}
    rows = ctx.find("design_selections", **match)
    return str(rows) if rows else f"No design_selections records for {match}."


@tool(owner="agent", rw="read")
def find_design_ledger(ctx: ToolContext, design_event_id: str = "", selection_id: str = "", customer_id: str = "") -> str:
    """Look up the history of Design Studio Selections files: appointments held, option lines with
    line number, catalog code, category, price and channel, removals, change orders with their
    number, reason and fee, option deposit payments, refunds, forfeitures and closing credits by
    receipt, returned payments, and design credits granted, applied or forfeited. Every
    reference number below is optional; give any you hold and all matching records are returned,
    or a note that none was found.

    Args:
        design_event_id: The reference number of one design appointment, option line, change order, deposit or credit entry; leave "" if unknown.
        selection_id: The reference number of a Design Studio Selections file; leave "" if unknown.
        customer_id: The customer reference number of the buyer or homeowner; leave "" if unknown.
    """
    match = {k: v for k, v in {"design_event_id": design_event_id, "selection_id": selection_id, "customer_id": customer_id}.items() if v}
    rows = ctx.find("design_events", **match)
    return str(rows) if rows else f"No design_events records for {match}."


@tool(owner="agent", rw="read")
def find_rate_locks(ctx: ToolContext, lock_id: str = "", customer_id: str = "", purchase_id: str = "") -> str:
    """Look up Builder Extended Rate Locks with Calloway Home Mortgage: the lock term, the purchase
    agreement financed, loan program and amount, loan-to-value and qualifying figures, par and
    locked rates, request, lock, expiration and expiry dates, extensions, float-downs and
    relocks used, and the lock fee and charges currently on the lock. Every reference number
    below is optional; give any you hold and all matching records are returned, or a note that
    none was found.

    Args:
        lock_id: The reference number of a Builder Extended Rate Lock; leave "" if unknown.
        customer_id: The customer reference number of the buyer or homeowner; leave "" if unknown.
        purchase_id: The reference number of a Home Purchase Agreement; leave "" if unknown.
    """
    match = {k: v for k, v in {"lock_id": lock_id, "customer_id": customer_id, "purchase_id": purchase_id}.items() if v}
    rows = ctx.find("rate_locks", **match)
    return str(rows) if rows else f"No rate_locks records for {match}."


@tool(owner="agent", rw="read")
def find_rate_lock_ledger(ctx: ToolContext, lock_event_id: str = "", lock_id: str = "", customer_id: str = "") -> str:
    """Look up the money and notice history of rate locks: upfront fee payments by receipt number,
    charges by charge number and type, waivers, collections, fee credits, refunds and
    forfeitures, and expiry reminders. Every reference number below is optional; give any you
    hold and all matching records are returned, or a note that none was found.

    Args:
        lock_event_id: The reference number of one rate lock fee, charge, credit or notice entry; leave "" if unknown.
        lock_id: The reference number of a Builder Extended Rate Lock; leave "" if unknown.
        customer_id: The customer reference number of the buyer or homeowner; leave "" if unknown.
    """
    match = {k: v for k, v in {"lock_event_id": lock_event_id, "lock_id": lock_id, "customer_id": customer_id}.items() if v}
    rows = ctx.find("lock_events", **match)
    return str(rows) if rows else f"No lock_events records for {match}."


@tool(owner="agent", rw="read")
def find_warranty_coverages(ctx: ToolContext, coverage_id: str = "", customer_id: str = "", purchase_id: str = "", prior_coverage_id: str = "") -> str:
    """Look up Calloway Limited Home Warranty coverages: the HomeCare program, the home's purchase
    agreement, whether the holder is the original buyer or a later owner, the ownership and
    coverage start dates, the end date of each coverage period, charges owed and payouts
    approved. Every reference number below is optional; give any you hold and all matching
    records are returned, or a note that none was found.

    Args:
        coverage_id: The reference number of one owner's Calloway Limited Home Warranty coverage; leave "" if unknown.
        customer_id: The customer reference number of the buyer or homeowner; leave "" if unknown.
        purchase_id: The reference number of a Home Purchase Agreement; leave "" if unknown.
        prior_coverage_id: The reference number of the previous owner's warranty coverage on the same home; leave "" if unknown.
    """
    match = {k: v for k, v in {"coverage_id": coverage_id, "customer_id": customer_id, "purchase_id": purchase_id, "prior_coverage_id": prior_coverage_id}.items() if v}
    rows = ctx.find("warranty_coverages", **match)
    return str(rows) if rows else f"No warranty_coverages records for {match}."


@tool(owner="agent", rw="read")
def find_warranty_ledger(ctx: ToolContext, warranty_event_id: str = "", coverage_id: str = "", customer_id: str = "") -> str:
    """Look up the warranty history of a home: claim items by item number with defect category,
    channel and emergency type, emergency dispatches, inspections with findings and
    measurements, approvals and denials with basis or reason, appointments booked and missed,
    repairs and callbacks, walkthroughs, homeowner charges, payments and waivers, and payouts.
    Every reference number below is optional; give any you hold and all matching records are
    returned, or a note that none was found.

    Args:
        warranty_event_id: The reference number of one warranty claim item, inspection, decision, appointment, walkthrough, charge or payout entry; leave "" if unknown.
        coverage_id: The reference number of one owner's Calloway Limited Home Warranty coverage; leave "" if unknown.
        customer_id: The customer reference number of the buyer or homeowner; leave "" if unknown.
    """
    match = {k: v for k, v in {"warranty_event_id": warranty_event_id, "coverage_id": coverage_id, "customer_id": customer_id}.items() if v}
    rows = ctx.find("warranty_events", **match)
    return str(rows) if rows else f"No warranty_events records for {match}."


@tool(owner="agent", rw="read")
def find_insurance_policies(ctx: ToolContext, policy_id: str = "", customer_id: str = "", purchase_id: str = "") -> str:
    """Look up homeowners insurance policies written by Calloway Insurance Agency: the HomeShield
    program, policy number, insured home, dwelling coverage, payment plan and discounts in
    force, term premium, binder, effective and expiration dates, cancellation reason and
    balance. Every reference number below is optional; give any you hold and all matching
    records are returned, or a note that none was found.

    Args:
        policy_id: The reference number of a homeowners insurance policy or quote; leave "" if unknown.
        customer_id: The customer reference number of the buyer or homeowner; leave "" if unknown.
        purchase_id: The reference number of a Home Purchase Agreement; leave "" if unknown.
    """
    match = {k: v for k, v in {"policy_id": policy_id, "customer_id": customer_id, "purchase_id": purchase_id}.items() if v}
    rows = ctx.find("insurance_policies", **match)
    return str(rows) if rows else f"No insurance_policies records for {match}."


@tool(owner="agent", rw="read")
def find_insurance_ledger(ctx: ToolContext, insurance_event_id: str = "", policy_id: str = "", customer_id: str = "") -> str:
    """Look up the billing and claim history of homeowners policies: bill lines by bill number and
    due date, payments and the bills they paid, return premium, reported losses and policy
    notices. Every reference number below is optional; give any you hold and all matching
    records are returned, or a note that none was found.

    Args:
        insurance_event_id: The reference number of one insurance bill, payment, return premium, claim or notice entry; leave "" if unknown.
        policy_id: The reference number of a homeowners insurance policy or quote; leave "" if unknown.
        customer_id: The customer reference number of the buyer or homeowner; leave "" if unknown.
    """
    match = {k: v for k, v in {"insurance_event_id": insurance_event_id, "policy_id": policy_id, "customer_id": customer_id}.items() if v}
    rows = ctx.find("insurance_events", **match)
    return str(rows) if rows else f"No insurance_events records for {match}."


@tool(owner="agent", rw="read")
def find_solar_leases(ctx: ToolContext, lease_id: str = "", customer_id: str = "", purchase_id: str = "") -> str:
    """Look up SunPath Solar Leases: the system size, the home, agreement number, signing,
    installation, permission-to-operate and first bill dates, billing preferences, current
    monthly payment and balance. Every reference number below is optional; give any you hold and
    all matching records are returned, or a note that none was found.

    Args:
        lease_id: The reference number of a SunPath Solar Lease; leave "" if unknown.
        customer_id: The customer reference number of the buyer or homeowner; leave "" if unknown.
        purchase_id: The reference number of a Home Purchase Agreement; leave "" if unknown.
    """
    match = {k: v for k, v in {"lease_id": lease_id, "customer_id": customer_id, "purchase_id": purchase_id}.items() if v}
    rows = ctx.find("solar_leases", **match)
    return str(rows) if rows else f"No solar_leases records for {match}."


@tool(owner="agent", rw="read")
def find_solar_ledger(ctx: ToolContext, solar_event_id: str = "", lease_id: str = "", customer_id: str = "") -> str:
    """Look up the history of SunPath Solar Leases: bill lines by bill number and period, payments,
    production guarantee credits, yearly production reconciliations, service visits and lease
    notices. Every reference number below is optional; give any you hold and all matching
    records are returned, or a note that none was found.

    Args:
        solar_event_id: The reference number of one solar lease bill, payment, credit, production, service or notice entry; leave "" if unknown.
        lease_id: The reference number of a SunPath Solar Lease; leave "" if unknown.
        customer_id: The customer reference number of the buyer or homeowner; leave "" if unknown.
    """
    match = {k: v for k, v in {"solar_event_id": solar_event_id, "lease_id": lease_id, "customer_id": customer_id}.items() if v}
    rows = ctx.find("solar_events", **match)
    return str(rows) if rows else f"No solar_events records for {match}."


@tool(owner="agent", rw="write")
def verify_customer_identity(ctx: ToolContext, customer_id: str, phone: str = "", email: str = "",
                             date_of_birth: str = "", ssn_last4: str = "", mailing_zip: str = "") -> str:
    """Confirm that the caller is the customer on the profile and record the outcome. This must be
    passed before any account details are discussed or any transaction is made for the customer. The
    tool itself compares each item of identity information the caller states with the profile on file
    and counts the items that match; identity is confirmed when at least 2 items match. The customer
    reference number only identifies which profile to compare against and is never counted as a match.
    Callers usually give only some of these items, so pass exactly what the caller said and leave the
    rest empty. Every attempt is recorded; once a caller has been confirmed, a later attempt never
    undoes it, so a caller who fails at first can be confirmed by asking for another item and trying
    again.

    Args:
        customer_id: The customer reference number of the profile found for this caller. Required; it selects the profile and does not count as a match.
        phone: The phone number the caller states, 10 digits with no punctuation; leave "" if not stated.
        email: The email address the caller states; leave "" if not stated.
        date_of_birth: The caller's date of birth as stated, written YYYY-MM-DD; leave "" if not stated.
        ssn_last4: The last four digits of the caller's Social Security number, as stated; leave "" if not stated.
        mailing_zip: The 5-digit ZIP code of the caller's current mailing address, as stated; leave "" if not stated.
    """
    if not customer_id:
        return "Error: customer_id is required; locate the customer first and pass their id."
    rows = ctx.find("customers", customer_id=customer_id)
    if not rows:
        return f"Error: no customer {customer_id}; cannot verify."
    rec = rows[0]
    # The locator customer_id is deliberately not a credential.
    supplied = {"phone": phone, "email": email, "date_of_birth": date_of_birth,
                "ssn_last4": ssn_last4, "mailing_zip": mailing_zip}
    matched = sum(1 for field, value in supplied.items() if value and str(rec.get(field)) == str(value))
    verified = matched >= 2
    rid = ctx.make_id("ver_", customer_id)
    # Upsert, monotonic: only the reproducible boolean is stored, never the match count.
    prior = ctx.find("verification_log", verification_id=rid)
    verified = verified or bool(prior and prior[0].get("verified"))
    if prior:
        ctx.update("verification_log", rid, verified=verified, verified_at=ctx.now())
    else:
        ctx.create("verification_log", rid, verification_id=rid, customer_id=customer_id,
                   verified=verified, verified_at=ctx.now())
    return (f"Identity verified for {customer_id} ({matched} item(s) matched)." if verified
            else f"Identity NOT verified for {customer_id} (only {matched} of the required 2 items matched). Ask the caller for another item on file and call this tool again.")


@tool(owner="agent", rw="write")
def transfer_to_human_agent(ctx: ToolContext, customer_id: str, reason: str) -> str:
    """Hand the customer over to a human representative of the Homebuyer and Warranty Services desk,
    recording the handoff and its reason. Use it in one of two situations only: when no Calloway rule
    can resolve what the customer is asking for, or when the customer has explicitly asked to speak
    with a person at least 2 times in this conversation.

    Args:
        customer_id: The customer reference number of the profile found for this caller.
        reason: Why the customer is handed over; exactly one of POLICY_NOT_COVERED (no Calloway rule can resolve the request) or CUSTOMER_REQUESTED (the customer has explicitly asked for a human representative at least 2 times). No other wording is accepted.
    """
    allowed = {"POLICY_NOT_COVERED", "CUSTOMER_REQUESTED"}
    if reason not in allowed:
        return f"Error: unknown handoff reason '{reason}'. Valid: {', '.join(sorted(allowed))}."
    if not ctx.find("customers", customer_id=customer_id):
        return f"Error: no customer {customer_id}; cannot record handoff."
    rid = ctx.make_id("hof_", customer_id, reason)
    ctx.create("handoff_log", rid, handoff_id=rid, customer_id=customer_id,
               reason=reason, created_at=ctx.now())
    return f"Handoff to a human representative recorded for {customer_id} ({reason})."

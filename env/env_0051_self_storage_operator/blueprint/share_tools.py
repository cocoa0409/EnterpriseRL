"""Shared tools for env_0051_self_storage_operator (Bluegate Self Storage customer care).

Every tool here is a share tool: always listed for its owner. It holds the record lookup layer (one
finder per record type; the customer finder doubles as the identity entry), the identity verification
write and the transfer-to-human write. Business actions on agreements, plans and authorizations are
per-difficulty task tools and are not defined here.

Scenario operating constants built into these tools:
  K = 2  identity credentials that must match for verification to pass
  R = 2  explicit requests for a human after which a CUSTOMER_REQUESTED handoff is due
"""

from erlbench import ToolContext, tool


@tool(owner="agent", rw="read")
def find_customers(ctx: ToolContext, customer_id: str = "", phone_number: str = "", email: str = "",
                   full_name: str = "") -> str:
    """Look up a customer profile to establish whose account this contact is about.

    Search by the customer reference number, or by what the caller can state: the mobile number on the
    profile, the email address on the profile, or the full name. Every criterion is optional, but at least
    one must be given; spacing, punctuation and letter case in what the caller says do not matter. The
    profile returned carries the contact details, date of birth, last four characters of the photo ID
    recorded at move-in, billing ZIP code, mailing address, profile opening date, whether the profile is an
    individual or a business, the business name, the alternate contact and the military status on file.
    Finding a profile does not verify the caller's identity.

    Args:
        customer_id: Id - the customer reference number; leave "" if unknown.
        phone_number: Fixed format - the mobile number on the profile as the caller states it, 10 digits; leave "" if not given.
        email: Verbatim - the email address on the profile as the caller states it; leave "" if not given.
        full_name: Verbatim - the customer's full name as the caller states it; leave "" if not given.
    """
    match = {k: v for k, v in {"customer_id": customer_id, "phone_number": phone_number,
                               "email": email, "full_name": full_name}.items() if v}
    if not match:
        return "Error: provide at least one reference number or profile detail to find the customer."
    rows = ctx.fuzzy_find("customers", **match)
    if not rows:
        return f"No customer matches {match}."
    if len(rows) > 1:
        return f"Error: {len(rows)} customers match {match}; ask the caller for one more detail to tell them apart."
    return str(rows[0])


@tool(owner="agent", rw="write")
def verify_customer_identity(ctx: ToolContext, customer_id: str, phone_number: str = "", email: str = "",
                             date_of_birth: str = "", drivers_license_last4: str = "",
                             billing_zip: str = "") -> str:
    """Verify the caller's identity against the customer profile and record the outcome.

    Identity must be verified before any account information is discussed or any business is transacted on
    the customer's agreements, plans or authorizations. This tool performs the comparison itself: each piece
    of identity information the caller states is compared with the profile, and verification passes only
    when at least 2 of them match. The customer reference number only identifies which profile to compare
    against and never counts as a match. Callers usually give only some of these details, so pass exactly the
    values the caller stated and leave the others blank. The outcome is recorded; if a first attempt fails
    and a later attempt with more details passes, the customer stands verified.

    Args:
        customer_id: Id - the customer reference number read from the customer profile lookup; required.
        phone_number: Fixed format - the mobile number the caller states, 10 digits with no punctuation; leave "" if not stated.
        email: Verbatim - the email address the caller states; leave "" if not stated.
        date_of_birth: Fixed format - the date of birth the caller states, YYYY-MM-DD; leave "" if not stated.
        drivers_license_last4: Fixed format - the last four characters of the photo ID the caller states; leave "" if not stated.
        billing_zip: Fixed format - the 5-digit billing ZIP code the caller states; leave "" if not stated.
    """
    if not customer_id:
        return "Error: customer_id is required; look the customer up first and pass their reference number."
    rows = ctx.find("customers", customer_id=customer_id)
    if not rows:
        return f"Error: no customer {customer_id}; cannot verify."
    rec = rows[0]
    supplied = {"phone_number": phone_number, "email": email, "date_of_birth": date_of_birth,
                "drivers_license_last4": drivers_license_last4, "billing_zip": billing_zip}
    matched = sum(1 for field, value in supplied.items()
                  if value and str(rec.get(field) or "").strip().lower() == str(value).strip().lower())
    verified = matched >= 2
    rid = ctx.make_id("ver_", customer_id)
    # Upsert, monotonic: a later pass overrides an earlier failure, never the reverse.
    prior = ctx.find("verification_log", verification_id=rid)
    verified = verified or bool(prior and prior[0].get("verified"))
    if prior:
        ctx.update("verification_log", rid, verified=verified, verified_at=ctx.now())
    else:
        ctx.create("verification_log", rid, verification_id=rid, customer_id=customer_id,
                   verified=verified, verified_at=ctx.now())
    if verified:
        return f"Identity verified for {customer_id} ({matched} detail(s) matched on this attempt)."
    return (f"Identity NOT verified for {customer_id}: {matched} of the 2 required details matched. "
            "Ask the caller for another detail on file and try again.")


@tool(owner="agent", rw="write")
def transfer_to_human_agent(ctx: ToolContext, customer_id: str, reason: str) -> str:
    """Hand the customer over to a human representative and record the handoff with its reason.

    Use POLICY_NOT_COVERED when no Bluegate policy lets the request be resolved in this contact, and
    CUSTOMER_REQUESTED once the customer has explicitly asked for a human representative 2 times.

    Args:
        customer_id: Id - the customer reference number read from the customer profile lookup; the profile must exist.
        reason: Enum - POLICY_NOT_COVERED or CUSTOMER_REQUESTED, exactly as written; no other value is accepted.
    """
    allowed = {"POLICY_NOT_COVERED", "CUSTOMER_REQUESTED"}
    if reason not in allowed:
        return f"Error: unknown handoff reason '{reason}'. Valid: {', '.join(sorted(allowed))}."
    if not ctx.find("customers", customer_id=customer_id):
        return f"Error: no customer {customer_id}; cannot record the handoff."
    rid = ctx.make_id("hof_", customer_id, reason)
    ctx.create("handoff_log", rid, handoff_id=rid, customer_id=customer_id, reason=reason,
               created_at=ctx.now())
    return f"Handoff to a human representative recorded for {customer_id} ({reason})."


@tool(owner="agent", rw="read")
def find_facility_spaces(ctx: ToolContext, facility_space_id: str = "") -> str:
    """Look up units and parking spaces in a facility's inventory, with each space's class, size, posted monthly street rate and whether it is available, reserved, occupied or out of service.

    Search by any reference number you already hold; every criterion is optional, but at least one must be
    given, and only records matching all the criteria given are returned. Returns the matching facility inventory spaces, or a
    message saying none were found.

    Args:
        facility_space_id: Id - the reference number of a unit or parking space in facility inventory; leave "" if unknown.
    """
    match = {k: v for k, v in {"facility_space_id": facility_space_id}.items() if v}
    if not match:
        return "Error: provide at least one reference number to search facility inventory spaces."
    rows = ctx.find("facility_spaces", **match)
    return str(rows) if rows else f"No facility inventory spaces found for {match}."


@tool(owner="agent", rw="read")
def find_verification_log(ctx: ToolContext, verification_id: str = "", customer_id: str = "") -> str:
    """Look up the identity verification outcome recorded for a customer during this or an earlier contact.

    Search by any reference number you already hold; every criterion is optional, but at least one must be
    given, and only records matching all the criteria given are returned. Returns the matching verification records, or a
    message saying none were found.

    Args:
        verification_id: Id - the reference number of an identity verification record; leave "" if unknown.
        customer_id: Id - the customer reference number; leave "" if unknown.
    """
    match = {k: v for k, v in {"verification_id": verification_id, "customer_id": customer_id}.items() if v}
    if not match:
        return "Error: provide at least one reference number to search verification records."
    rows = ctx.find("verification_log", **match)
    return str(rows) if rows else f"No verification records found for {match}."


@tool(owner="agent", rw="read")
def find_handoff_log(ctx: ToolContext, handoff_id: str = "", customer_id: str = "") -> str:
    """Look up the handoffs to a human representative recorded for a customer, with the reason and moment of each.

    Search by any reference number you already hold; every criterion is optional, but at least one must be
    given, and only records matching all the criteria given are returned. Returns the matching handoff records, or a
    message saying none were found.

    Args:
        handoff_id: Id - the reference number of a handoff record; leave "" if unknown.
        customer_id: Id - the customer reference number; leave "" if unknown.
    """
    match = {k: v for k, v in {"handoff_id": handoff_id, "customer_id": customer_id}.items() if v}
    if not match:
        return "Error: provide at least one reference number to search handoff records."
    rows = ctx.find("handoff_log", **match)
    return str(rows) if rows else f"No handoff records found for {match}."


@tool(owner="agent", rw="read")
def find_unit_rentals(ctx: ToolContext, rental_id: str = "", customer_id: str = "") -> str:
    """Look up storage unit rental agreements: unit class, facility, unit number and size, contracted monthly rent, status, move-in and billing day, balance due, deposit held, delinquency date, last rent change, coverage source, lock status, promotion, military discount and move-out date.

    Search by any reference number you already hold; every criterion is optional, but at least one must be
    given, and only records matching all the criteria given are returned. Returns the matching storage unit rental agreements, or a
    message saying none were found.

    Args:
        rental_id: Id - the storage unit rental agreement number; leave "" if unknown.
        customer_id: Id - the customer reference number; leave "" if unknown.
    """
    match = {k: v for k, v in {"rental_id": rental_id, "customer_id": customer_id}.items() if v}
    if not match:
        return "Error: provide at least one reference number to search storage unit rental agreements."
    rows = ctx.find("unit_rentals", **match)
    return str(rows) if rows else f"No storage unit rental agreements found for {match}."


@tool(owner="agent", rw="read")
def find_unit_ledger(ctx: ToolContext, entry_id: str = "", rental_id: str = "", customer_id: str = "", reference_entry_id: str = "", autopay_draft_id: str = "") -> str:
    """Look up the tenant ledger of storage unit agreements: rent charges by billing period, fees, payments with method and channel, reversals, credits, refunds, deposit entries and lien-sale proceeds, each with its amount and date.

    Search by any reference number you already hold; every criterion is optional, but at least one must be
    given, and only records matching all the criteria given are returned. Returns the matching storage unit ledger entries, or a
    message saying none were found.

    Args:
        entry_id: Id - the reference number of a storage unit ledger entry; leave "" if unknown.
        rental_id: Id - the storage unit rental agreement number; leave "" if unknown.
        customer_id: Id - the customer reference number; leave "" if unknown.
        reference_entry_id: Id - the reference number of the ledger entry this entry arises from or applies against; leave "" if unknown.
        autopay_draft_id: Id - the reference number of the AutoPay draft behind a payment; leave "" if unknown.
    """
    match = {k: v for k, v in {"entry_id": entry_id, "rental_id": rental_id, "customer_id": customer_id, "reference_entry_id": reference_entry_id, "autopay_draft_id": autopay_draft_id}.items() if v}
    if not match:
        return "Error: provide at least one reference number to search storage unit ledger entries."
    rows = ctx.find("unit_ledger", **match)
    return str(rows) if rows else f"No storage unit ledger entries found for {match}."


@tool(owner="agent", rw="read")
def find_unit_lien_actions(ctx: ToolContext, lien_action_id: str = "", rental_id: str = "", customer_id: str = "") -> str:
    """Look up the delinquency and lien steps taken on storage unit agreements: overlocks, preliminary letters, lien notices, sale advertisements, lock cuts, overlock removals and lien holds, with dates, delivery method, scheduled sale date and hold reason.

    Search by any reference number you already hold; every criterion is optional, but at least one must be
    given, and only records matching all the criteria given are returned. Returns the matching lien-process steps, or a
    message saying none were found.

    Args:
        lien_action_id: Id - the reference number of a lien-process step; leave "" if unknown.
        rental_id: Id - the storage unit rental agreement number; leave "" if unknown.
        customer_id: Id - the customer reference number; leave "" if unknown.
    """
    match = {k: v for k, v in {"lien_action_id": lien_action_id, "rental_id": rental_id, "customer_id": customer_id}.items() if v}
    if not match:
        return "Error: provide at least one reference number to search lien-process steps."
    rows = ctx.find("unit_lien_actions", **match)
    return str(rows) if rows else f"No lien-process steps found for {match}."


@tool(owner="agent", rw="read")
def find_unit_rate_changes(ctx: ToolContext, rate_change_id: str = "", rental_id: str = "", customer_id: str = "", source_rate_change_id: str = "") -> str:
    """Look up rent change notices on storage unit agreements: rate increases, retention concessions and rescissions, with previous and new rent, notice date and effective date.

    Search by any reference number you already hold; every criterion is optional, but at least one must be
    given, and only records matching all the criteria given are returned. Returns the matching storage unit rent change notices, or a
    message saying none were found.

    Args:
        rate_change_id: Id - the reference number of a storage unit rent change notice; leave "" if unknown.
        rental_id: Id - the storage unit rental agreement number; leave "" if unknown.
        customer_id: Id - the customer reference number; leave "" if unknown.
        source_rate_change_id: Id - the reference number of the rate increase a concession or rescission modifies; leave "" if unknown.
    """
    match = {k: v for k, v in {"rate_change_id": rate_change_id, "rental_id": rental_id, "customer_id": customer_id, "source_rate_change_id": source_rate_change_id}.items() if v}
    if not match:
        return "Error: provide at least one reference number to search storage unit rent change notices."
    rows = ctx.find("unit_rate_changes", **match)
    return str(rows) if rows else f"No storage unit rent change notices found for {match}."


@tool(owner="agent", rw="read")
def find_unit_transfers(ctx: ToolContext, transfer_id: str = "", rental_id: str = "", customer_id: str = "") -> str:
    """Look up unit transfers made on storage unit agreements, with the unit left, the unit moved into, the new rent and any transfer fee.

    Search by any reference number you already hold; every criterion is optional, but at least one must be
    given, and only records matching all the criteria given are returned. Returns the matching unit transfers, or a
    message saying none were found.

    Args:
        transfer_id: Id - the reference number of a unit transfer; leave "" if unknown.
        rental_id: Id - the storage unit rental agreement number; leave "" if unknown.
        customer_id: Id - the customer reference number; leave "" if unknown.
    """
    match = {k: v for k, v in {"transfer_id": transfer_id, "rental_id": rental_id, "customer_id": customer_id}.items() if v}
    if not match:
        return "Error: provide at least one reference number to search unit transfers."
    rows = ctx.find("unit_transfers", **match)
    return str(rows) if rows else f"No unit transfers found for {match}."


@tool(owner="agent", rw="read")
def find_unit_moveout_notices(ctx: ToolContext, moveout_notice_id: str = "", rental_id: str = "", customer_id: str = "") -> str:
    """Look up move-out notices given on storage unit agreements, with notice date, planned vacate date, status and refund preference.

    Search by any reference number you already hold; every criterion is optional, but at least one must be
    given, and only records matching all the criteria given are returned. Returns the matching storage unit move-out notices, or a
    message saying none were found.

    Args:
        moveout_notice_id: Id - the reference number of a storage unit move-out notice; leave "" if unknown.
        rental_id: Id - the storage unit rental agreement number; leave "" if unknown.
        customer_id: Id - the customer reference number; leave "" if unknown.
    """
    match = {k: v for k, v in {"moveout_notice_id": moveout_notice_id, "rental_id": rental_id, "customer_id": customer_id}.items() if v}
    if not match:
        return "Error: provide at least one reference number to search storage unit move-out notices."
    rows = ctx.find("unit_moveout_notices", **match)
    return str(rows) if rows else f"No storage unit move-out notices found for {match}."


@tool(owner="agent", rw="read")
def find_protect_plans(ctx: ToolContext, plan_id: str = "", customer_id: str = "", rental_id: str = "") -> str:
    """Look up tenant protection plans: coverage level, covered unit agreement, status, enrollment and effective dates, coverage limit, monthly fee, deductible, change, lapse, cancellation and termination dates, fee balance and claims paid to date.

    Search by any reference number you already hold; every criterion is optional, but at least one must be
    given, and only records matching all the criteria given are returned. Returns the matching tenant protection plans, or a
    message saying none were found.

    Args:
        plan_id: Id - the tenant protection plan number; leave "" if unknown.
        customer_id: Id - the customer reference number; leave "" if unknown.
        rental_id: Id - the storage unit rental agreement number; leave "" if unknown.
    """
    match = {k: v for k, v in {"plan_id": plan_id, "customer_id": customer_id, "rental_id": rental_id}.items() if v}
    if not match:
        return "Error: provide at least one reference number to search tenant protection plans."
    rows = ctx.find("protect_plans", **match)
    return str(rows) if rows else f"No tenant protection plans found for {match}."


@tool(owner="agent", rw="read")
def find_protect_premiums(ctx: ToolContext, premium_entry_id: str = "", plan_id: str = "", customer_id: str = "", reference_entry_id: str = "") -> str:
    """Look up protection fee entries: fees billed by period, collections, credits and refunds.

    Search by any reference number you already hold; every criterion is optional, but at least one must be
    given, and only records matching all the criteria given are returned. Returns the matching protection fee entries, or a
    message saying none were found.

    Args:
        premium_entry_id: Id - the reference number of a protection fee entry; leave "" if unknown.
        plan_id: Id - the tenant protection plan number; leave "" if unknown.
        customer_id: Id - the customer reference number; leave "" if unknown.
        reference_entry_id: Id - the reference number of the ledger entry this entry arises from or applies against; leave "" if unknown.
    """
    match = {k: v for k, v in {"premium_entry_id": premium_entry_id, "plan_id": plan_id, "customer_id": customer_id, "reference_entry_id": reference_entry_id}.items() if v}
    if not match:
        return "Error: provide at least one reference number to search protection fee entries."
    rows = ctx.find("protect_premiums", **match)
    return str(rows) if rows else f"No protection fee entries found for {match}."


@tool(owner="agent", rw="read")
def find_protect_plan_changes(ctx: ToolContext, plan_change_id: str = "", plan_id: str = "", customer_id: str = "") -> str:
    """Look up coverage level changes on protection plans, with the previous and new level, request date and effective date.

    Search by any reference number you already hold; every criterion is optional, but at least one must be
    given, and only records matching all the criteria given are returned. Returns the matching coverage level changes, or a
    message saying none were found.

    Args:
        plan_change_id: Id - the reference number of a coverage level change; leave "" if unknown.
        plan_id: Id - the tenant protection plan number; leave "" if unknown.
        customer_id: Id - the customer reference number; leave "" if unknown.
    """
    match = {k: v for k, v in {"plan_change_id": plan_change_id, "plan_id": plan_id, "customer_id": customer_id}.items() if v}
    if not match:
        return "Error: provide at least one reference number to search coverage level changes."
    rows = ctx.find("protect_plan_changes", **match)
    return str(rows) if rows else f"No coverage level changes found for {match}."


@tool(owner="agent", rw="read")
def find_protect_claim_events(ctx: ToolContext, claim_event_id: str = "", plan_id: str = "", customer_id: str = "", claim_id: str = "", reference_event_id: str = "") -> str:
    """Look up the handling history of protection claims: document requests, adjuster assessments by property class, decisions with approved amounts and reasons, payments and voids.

    Search by any reference number you already hold; every criterion is optional, but at least one must be
    given, and only records matching all the criteria given are returned. Returns the matching claim handling events, or a
    message saying none were found.

    Args:
        claim_event_id: Id - the reference number of a claim handling event; leave "" if unknown.
        plan_id: Id - the tenant protection plan number; leave "" if unknown.
        customer_id: Id - the customer reference number; leave "" if unknown.
        claim_id: Id - the protection claim number; leave "" if unknown.
        reference_event_id: Id - the reference number of the claim payment a void reverses; leave "" if unknown.
    """
    match = {k: v for k, v in {"claim_event_id": claim_event_id, "plan_id": plan_id, "customer_id": customer_id, "claim_id": claim_id, "reference_event_id": reference_event_id}.items() if v}
    if not match:
        return "Error: provide at least one reference number to search claim handling events."
    rows = ctx.find("protect_claim_events", **match)
    return str(rows) if rows else f"No claim handling events found for {match}."


@tool(owner="agent", rw="read")
def find_protect_claims(ctx: ToolContext, claim_id: str = "", plan_id: str = "", customer_id: str = "", rental_id: str = "") -> str:
    """Look up protection claims as filed: loss, discovery and filing dates, peril, police report details, forced-entry evidence, facility work-order reference, claimed amount, documents on file and claim status.

    Search by any reference number you already hold; every criterion is optional, but at least one must be
    given, and only records matching all the criteria given are returned. Returns the matching protection claims, or a
    message saying none were found.

    Args:
        claim_id: Id - the protection claim number; leave "" if unknown.
        plan_id: Id - the tenant protection plan number; leave "" if unknown.
        customer_id: Id - the customer reference number; leave "" if unknown.
        rental_id: Id - the storage unit rental agreement number; leave "" if unknown.
    """
    match = {k: v for k, v in {"claim_id": claim_id, "plan_id": plan_id, "customer_id": customer_id, "rental_id": rental_id}.items() if v}
    if not match:
        return "Error: provide at least one reference number to search protection claims."
    rows = ctx.find("protect_claims", **match)
    return str(rows) if rows else f"No protection claims found for {match}."


@tool(owner="agent", rw="read")
def find_protect_cancellation_requests(ctx: ToolContext, cancel_request_id: str = "", plan_id: str = "", customer_id: str = "") -> str:
    """Look up requests to cancel protection, with the request date, the tenant's own insurer and policy number, and the request status.

    Search by any reference number you already hold; every criterion is optional, but at least one must be
    given, and only records matching all the criteria given are returned. Returns the matching protection cancellation requests, or a
    message saying none were found.

    Args:
        cancel_request_id: Id - the reference number of a protection cancellation request; leave "" if unknown.
        plan_id: Id - the tenant protection plan number; leave "" if unknown.
        customer_id: Id - the customer reference number; leave "" if unknown.
    """
    match = {k: v for k, v in {"cancel_request_id": cancel_request_id, "plan_id": plan_id, "customer_id": customer_id}.items() if v}
    if not match:
        return "Error: provide at least one reference number to search protection cancellation requests."
    rows = ctx.find("protect_cancellation_requests", **match)
    return str(rows) if rows else f"No protection cancellation requests found for {match}."


@tool(owner="agent", rw="read")
def find_parking_rentals(ctx: ToolContext, parking_rental_id: str = "", customer_id: str = "") -> str:
    """Look up vehicle, RV and boat parking agreements: space class and number, facility, rent, status, start and billing day, balance due, delinquency date, last rent change, vehicle on file with registration and insurance expiry, military discount and move-out date.

    Search by any reference number you already hold; every criterion is optional, but at least one must be
    given, and only records matching all the criteria given are returned. Returns the matching parking agreements, or a
    message saying none were found.

    Args:
        parking_rental_id: Id - the parking agreement number; leave "" if unknown.
        customer_id: Id - the customer reference number; leave "" if unknown.
    """
    match = {k: v for k, v in {"parking_rental_id": parking_rental_id, "customer_id": customer_id}.items() if v}
    if not match:
        return "Error: provide at least one reference number to search parking agreements."
    rows = ctx.find("parking_rentals", **match)
    return str(rows) if rows else f"No parking agreements found for {match}."


@tool(owner="agent", rw="read")
def find_parking_ledger(ctx: ToolContext, parking_entry_id: str = "", parking_rental_id: str = "", customer_id: str = "", reference_entry_id: str = "", autopay_draft_id: str = "") -> str:
    """Look up the ledger of parking agreements: rent charges, fees, payments, reversals, credits and refunds.

    Search by any reference number you already hold; every criterion is optional, but at least one must be
    given, and only records matching all the criteria given are returned. Returns the matching parking ledger entries, or a
    message saying none were found.

    Args:
        parking_entry_id: Id - the reference number of a parking ledger entry; leave "" if unknown.
        parking_rental_id: Id - the parking agreement number; leave "" if unknown.
        customer_id: Id - the customer reference number; leave "" if unknown.
        reference_entry_id: Id - the reference number of the ledger entry this entry arises from or applies against; leave "" if unknown.
        autopay_draft_id: Id - the reference number of the AutoPay draft behind a payment; leave "" if unknown.
    """
    match = {k: v for k, v in {"parking_entry_id": parking_entry_id, "parking_rental_id": parking_rental_id, "customer_id": customer_id, "reference_entry_id": reference_entry_id, "autopay_draft_id": autopay_draft_id}.items() if v}
    if not match:
        return "Error: provide at least one reference number to search parking ledger entries."
    rows = ctx.find("parking_ledger", **match)
    return str(rows) if rows else f"No parking ledger entries found for {match}."


@tool(owner="agent", rw="read")
def find_parking_notices(ctx: ToolContext, parking_notice_id: str = "", parking_rental_id: str = "", customer_id: str = "") -> str:
    """Look up notices sent on parking agreements: gate lockouts, notices of intent to tow, compliance notices and compliance terminations, with dates and cure-by dates.

    Search by any reference number you already hold; every criterion is optional, but at least one must be
    given, and only records matching all the criteria given are returned. Returns the matching parking notices, or a
    message saying none were found.

    Args:
        parking_notice_id: Id - the reference number of a parking notice; leave "" if unknown.
        parking_rental_id: Id - the parking agreement number; leave "" if unknown.
        customer_id: Id - the customer reference number; leave "" if unknown.
    """
    match = {k: v for k, v in {"parking_notice_id": parking_notice_id, "parking_rental_id": parking_rental_id, "customer_id": customer_id}.items() if v}
    if not match:
        return "Error: provide at least one reference number to search parking notices."
    rows = ctx.find("parking_notices", **match)
    return str(rows) if rows else f"No parking notices found for {match}."


@tool(owner="agent", rw="read")
def find_parking_rate_changes(ctx: ToolContext, parking_rate_change_id: str = "", parking_rental_id: str = "", customer_id: str = "", source_rate_change_id: str = "") -> str:
    """Look up rent change notices on parking agreements: increases, retention concessions and rescissions, with previous and new rent, the street rate and tenure at notice, and the notice and effective dates.

    Search by any reference number you already hold; every criterion is optional, but at least one must be
    given, and only records matching all the criteria given are returned. Returns the matching parking rent change notices, or a
    message saying none were found.

    Args:
        parking_rate_change_id: Id - the reference number of a parking rent change notice; leave "" if unknown.
        parking_rental_id: Id - the parking agreement number; leave "" if unknown.
        customer_id: Id - the customer reference number; leave "" if unknown.
        source_rate_change_id: Id - the reference number of the rate increase a concession or rescission modifies; leave "" if unknown.
    """
    match = {k: v for k, v in {"parking_rate_change_id": parking_rate_change_id, "parking_rental_id": parking_rental_id, "customer_id": customer_id, "source_rate_change_id": source_rate_change_id}.items() if v}
    if not match:
        return "Error: provide at least one reference number to search parking rent change notices."
    rows = ctx.find("parking_rate_changes", **match)
    return str(rows) if rows else f"No parking rent change notices found for {match}."


@tool(owner="agent", rw="read")
def find_parking_moveout_notices(ctx: ToolContext, parking_moveout_notice_id: str = "", parking_rental_id: str = "", customer_id: str = "") -> str:
    """Look up move-out notices given on parking agreements, with notice date, planned vacate date, status and refund preference.

    Search by any reference number you already hold; every criterion is optional, but at least one must be
    given, and only records matching all the criteria given are returned. Returns the matching parking move-out notices, or a
    message saying none were found.

    Args:
        parking_moveout_notice_id: Id - the reference number of a parking move-out notice; leave "" if unknown.
        parking_rental_id: Id - the parking agreement number; leave "" if unknown.
        customer_id: Id - the customer reference number; leave "" if unknown.
    """
    match = {k: v for k, v in {"parking_moveout_notice_id": parking_moveout_notice_id, "parking_rental_id": parking_rental_id, "customer_id": customer_id}.items() if v}
    if not match:
        return "Error: provide at least one reference number to search parking move-out notices."
    rows = ctx.find("parking_moveout_notices", **match)
    return str(rows) if rows else f"No parking move-out notices found for {match}."


@tool(owner="agent", rw="read")
def find_truck_rentals(ctx: ToolContext, truck_rental_id: str = "", customer_id: str = "", linked_rental_id: str = "") -> str:
    """Look up truck and van rental contracts: vehicle class, facility, scheduled and actual pickup and return times, odometer and fuel readings, damage waiver, deposit card type, return condition, any linked storage unit for the free move-in truck, balance due and deposit hold.

    Search by any reference number you already hold; every criterion is optional, but at least one must be
    given, and only records matching all the criteria given are returned. Returns the matching truck rental contracts, or a
    message saying none were found.

    Args:
        truck_rental_id: Id - the truck rental contract number; leave "" if unknown.
        customer_id: Id - the customer reference number; leave "" if unknown.
        linked_rental_id: Id - the storage unit rental agreement number a free move-in truck is claimed for; leave "" if unknown.
    """
    match = {k: v for k, v in {"truck_rental_id": truck_rental_id, "customer_id": customer_id, "linked_rental_id": linked_rental_id}.items() if v}
    if not match:
        return "Error: provide at least one reference number to search truck rental contracts."
    rows = ctx.find("truck_rentals", **match)
    return str(rows) if rows else f"No truck rental contracts found for {match}."


@tool(owner="agent", rw="read")
def find_truck_charges(ctx: ToolContext, truck_charge_id: str = "", truck_rental_id: str = "", customer_id: str = "", reference_id: str = "") -> str:
    """Look up the entries on truck rental contracts: charges by type, payments, credits, refunds, deposit holds and releases.

    Search by any reference number you already hold; every criterion is optional, but at least one must be
    given, and only records matching all the criteria given are returned. Returns the matching truck contract entries, or a
    message saying none were found.

    Args:
        truck_charge_id: Id - the reference number of a truck contract entry; leave "" if unknown.
        truck_rental_id: Id - the truck rental contract number; leave "" if unknown.
        customer_id: Id - the customer reference number; leave "" if unknown.
        reference_id: Id - the reference number of the source record or credited line; leave "" if unknown.
    """
    match = {k: v for k, v in {"truck_charge_id": truck_charge_id, "truck_rental_id": truck_rental_id, "customer_id": customer_id, "reference_id": reference_id}.items() if v}
    if not match:
        return "Error: provide at least one reference number to search truck contract entries."
    rows = ctx.find("truck_charges", **match)
    return str(rows) if rows else f"No truck contract entries found for {match}."


@tool(owner="agent", rw="read")
def find_truck_incidents(ctx: ToolContext, truck_incident_id: str = "", truck_rental_id: str = "", customer_id: str = "") -> str:
    """Look up incidents on truck rental contracts: vehicle or accident damage with location and repair estimate, breakdowns, and tolls or citations, with any reason a waiver does not apply.

    Search by any reference number you already hold; every criterion is optional, but at least one must be
    given, and only records matching all the criteria given are returned. Returns the matching truck incidents, or a
    message saying none were found.

    Args:
        truck_incident_id: Id - the reference number of a truck incident; leave "" if unknown.
        truck_rental_id: Id - the truck rental contract number; leave "" if unknown.
        customer_id: Id - the customer reference number; leave "" if unknown.
    """
    match = {k: v for k, v in {"truck_incident_id": truck_incident_id, "truck_rental_id": truck_rental_id, "customer_id": customer_id}.items() if v}
    if not match:
        return "Error: provide at least one reference number to search truck incidents."
    rows = ctx.find("truck_incidents", **match)
    return str(rows) if rows else f"No truck incidents found for {match}."


@tool(owner="agent", rw="read")
def find_autopay_enrollments(ctx: ToolContext, autopay_id: str = "", customer_id: str = "", agreement_id: str = "") -> str:
    """Look up AutoPay authorizations: method, agreement drafted, status, enrollment and verification dates, card or account last four digits, card expiry, holder name, next draft due date, and suspension or end details.

    Search by any reference number you already hold; every criterion is optional, but at least one must be
    given, and only records matching all the criteria given are returned. Returns the matching AutoPay authorizations, or a
    message saying none were found.

    Args:
        autopay_id: Id - the AutoPay authorization number; leave "" if unknown.
        customer_id: Id - the customer reference number; leave "" if unknown.
        agreement_id: Id - the storage unit or parking agreement number; leave "" if unknown.
    """
    match = {k: v for k, v in {"autopay_id": autopay_id, "customer_id": customer_id, "agreement_id": agreement_id}.items() if v}
    if not match:
        return "Error: provide at least one reference number to search AutoPay authorizations."
    rows = ctx.find("autopay_enrollments", **match)
    return str(rows) if rows else f"No AutoPay authorizations found for {match}."


@tool(owner="agent", rw="read")
def find_autopay_drafts(ctx: ToolContext, autopay_draft_id: str = "", autopay_id: str = "", customer_id: str = "", agreement_id: str = "", reference_draft_id: str = "") -> str:
    """Look up AutoPay draft attempts and returns: due date, draft date, attempt number, amount, outcome, and return code.

    Search by any reference number you already hold; every criterion is optional, but at least one must be
    given, and only records matching all the criteria given are returned. Returns the matching AutoPay drafts and returns, or a
    message saying none were found.

    Args:
        autopay_draft_id: Id - the reference number of the AutoPay draft behind a payment; leave "" if unknown.
        autopay_id: Id - the AutoPay authorization number; leave "" if unknown.
        customer_id: Id - the customer reference number; leave "" if unknown.
        agreement_id: Id - the storage unit or parking agreement number; leave "" if unknown.
        reference_draft_id: Id - the reference number of the draft that a return reverses or a retry follows; leave "" if unknown.
    """
    match = {k: v for k, v in {"autopay_draft_id": autopay_draft_id, "autopay_id": autopay_id, "customer_id": customer_id, "agreement_id": agreement_id, "reference_draft_id": reference_draft_id}.items() if v}
    if not match:
        return "Error: provide at least one reference number to search AutoPay drafts and returns."
    rows = ctx.find("autopay_drafts", **match)
    return str(rows) if rows else f"No AutoPay drafts and returns found for {match}."


@tool(owner="agent", rw="read")
def find_autopay_notices(ctx: ToolContext, autopay_notice_id: str = "", autopay_id: str = "", customer_id: str = "") -> str:
    """Look up notices sent about AutoPay: varying-amount notices, card expiry reminders, failed-draft and suspension notices.

    Search by any reference number you already hold; every criterion is optional, but at least one must be
    given, and only records matching all the criteria given are returned. Returns the matching AutoPay notices, or a
    message saying none were found.

    Args:
        autopay_notice_id: Id - the reference number of an AutoPay notice; leave "" if unknown.
        autopay_id: Id - the AutoPay authorization number; leave "" if unknown.
        customer_id: Id - the customer reference number; leave "" if unknown.
    """
    match = {k: v for k, v in {"autopay_notice_id": autopay_notice_id, "autopay_id": autopay_id, "customer_id": customer_id}.items() if v}
    if not match:
        return "Error: provide at least one reference number to search AutoPay notices."
    rows = ctx.find("autopay_notices", **match)
    return str(rows) if rows else f"No AutoPay notices found for {match}."


@tool(owner="agent", rw="read")
def find_prepay_plans(ctx: ToolContext, prepay_id: str = "", customer_id: str = "", agreement_id: str = "") -> str:
    """Look up prepaid rent plans: plan, agreement covered, status, purchase and payment dates, term start and end, locked rent, prepayment price and unused prepaid credit.

    Search by any reference number you already hold; every criterion is optional, but at least one must be
    given, and only records matching all the criteria given are returned. Returns the matching prepaid rent plans, or a
    message saying none were found.

    Args:
        prepay_id: Id - the prepaid rent plan number; leave "" if unknown.
        customer_id: Id - the customer reference number; leave "" if unknown.
        agreement_id: Id - the storage unit or parking agreement number; leave "" if unknown.
    """
    match = {k: v for k, v in {"prepay_id": prepay_id, "customer_id": customer_id, "agreement_id": agreement_id}.items() if v}
    if not match:
        return "Error: provide at least one reference number to search prepaid rent plans."
    rows = ctx.find("prepay_plans", **match)
    return str(rows) if rows else f"No prepaid rent plans found for {match}."


@tool(owner="agent", rw="read")
def find_prepay_ledger(ctx: ToolContext, prepay_entry_id: str = "", prepay_id: str = "", customer_id: str = "") -> str:
    """Look up prepaid plan entries: the prepayment, each month applied, refunds and forfeiture applications.

    Search by any reference number you already hold; every criterion is optional, but at least one must be
    given, and only records matching all the criteria given are returned. Returns the matching prepaid plan entries, or a
    message saying none were found.

    Args:
        prepay_entry_id: Id - the reference number of a prepaid plan entry; leave "" if unknown.
        prepay_id: Id - the prepaid rent plan number; leave "" if unknown.
        customer_id: Id - the customer reference number; leave "" if unknown.
    """
    match = {k: v for k, v in {"prepay_entry_id": prepay_entry_id, "prepay_id": prepay_id, "customer_id": customer_id}.items() if v}
    if not match:
        return "Error: provide at least one reference number to search prepaid plan entries."
    rows = ctx.find("prepay_ledger", **match)
    return str(rows) if rows else f"No prepaid plan entries found for {match}."


@tool(owner="agent", rw="read")
def find_business_accounts(ctx: ToolContext, business_account_id: str = "", customer_id: str = "") -> str:
    """Look up business storage accounts: program, status, application and approval dates, credit limit, invoice terms, authorized users, invoice balance and past-due date.

    Search by any reference number you already hold; every criterion is optional, but at least one must be
    given, and only records matching all the criteria given are returned. Returns the matching business storage accounts, or a
    message saying none were found.

    Args:
        business_account_id: Id - the business storage account number; leave "" if unknown.
        customer_id: Id - the customer reference number; leave "" if unknown.
    """
    match = {k: v for k, v in {"business_account_id": business_account_id, "customer_id": customer_id}.items() if v}
    if not match:
        return "Error: provide at least one reference number to search business storage accounts."
    rows = ctx.find("business_accounts", **match)
    return str(rows) if rows else f"No business storage accounts found for {match}."


@tool(owner="agent", rw="read")
def find_business_invoices(ctx: ToolContext, business_invoice_id: str = "", business_account_id: str = "", customer_id: str = "", reference_id: str = "") -> str:
    """Look up business account invoice entries: monthly invoices, service charges, payments and credits.

    Search by any reference number you already hold; every criterion is optional, but at least one must be
    given, and only records matching all the criteria given are returned. Returns the matching business invoice entries, or a
    message saying none were found.

    Args:
        business_invoice_id: Id - the reference number of a business account invoice entry; leave "" if unknown.
        business_account_id: Id - the business storage account number; leave "" if unknown.
        customer_id: Id - the customer reference number; leave "" if unknown.
        reference_id: Id - the reference number of the source record or credited line; leave "" if unknown.
    """
    match = {k: v for k, v in {"business_invoice_id": business_invoice_id, "business_account_id": business_account_id, "customer_id": customer_id, "reference_id": reference_id}.items() if v}
    if not match:
        return "Error: provide at least one reference number to search business invoice entries."
    rows = ctx.find("business_invoices", **match)
    return str(rows) if rows else f"No business invoice entries found for {match}."


@tool(owner="agent", rw="read")
def find_business_deliveries(ctx: ToolContext, business_delivery_id: str = "", business_account_id: str = "", customer_id: str = "") -> str:
    """Look up deliveries handled for business accounts: receipts, collections and returns to sender, with carrier, tracking number, kind, pieces and whether the receipt was chargeable.

    Search by any reference number you already hold; every criterion is optional, but at least one must be
    given, and only records matching all the criteria given are returned. Returns the matching deliveries handled for business accounts, or a
    message saying none were found.

    Args:
        business_delivery_id: Id - the reference number of a delivery handling record; leave "" if unknown.
        business_account_id: Id - the business storage account number; leave "" if unknown.
        customer_id: Id - the customer reference number; leave "" if unknown.
    """
    match = {k: v for k, v in {"business_delivery_id": business_delivery_id, "business_account_id": business_account_id, "customer_id": customer_id}.items() if v}
    if not match:
        return "Error: provide at least one reference number to search deliveries handled for business accounts."
    rows = ctx.find("business_deliveries", **match)
    return str(rows) if rows else f"No deliveries handled for business accounts found for {match}."

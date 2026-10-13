"""Shared tools for env_0034_senior_living_operator (Larkspur Senior Living - Resident and Family Services).

Every tool here is a share tool, always present in its owner's tool list: one record finder per
table (the customer finder doubles as the identity entry), the identity verification write and the
handoff to a human representative. Customer-signed actions live as hidden task tools in each
difficulty's task_tools.py, never here.
"""

from erlbench import ToolContext, tool


@tool(owner="agent", rw="read")
def find_customers(ctx: ToolContext, customer_id: str = "", name: str = "", phone_number: str = "",
                   email: str = "", date_of_birth: str = "", representative_phone: str = "") -> str:
    """Look up a customer profile to establish whose account this contact concerns. A profile can be
    found by its customer reference number or by what a caller naturally states - the resident's full
    name, phone number, email or date of birth, or the phone number of the family representative on
    file. Every criterion is optional; supply whichever are known. The profile returned shows the
    resident's contact details, date of birth, mailing address, the representative on file and the
    authority that representative holds, any recorded date of death, and the date the profile was
    opened. Finding a profile does not verify the caller's identity.

    Args:
        customer_id: Id - the customer reference number; leave "" if unknown.
        name: Verbatim - the resident's full name as the caller states it; leave "" if not provided.
        phone_number: Fixed format - the resident's 10-digit phone number, digits only; leave "" if not provided.
        email: Verbatim - the email address on the profile; leave "" if not provided.
        date_of_birth: Fixed format - the resident's date of birth, YYYY-MM-DD; leave "" if not provided.
        representative_phone: Fixed format - the 10-digit phone number of the representative on file, digits only; leave "" if not provided.
    """
    match = {k: v for k, v in {"customer_id": customer_id, "name": name, "phone_number": phone_number,
                               "email": email, "date_of_birth": date_of_birth,
                               "representative_phone": representative_phone}.items() if v}
    if not match:
        return "Error: provide at least one reference number or profile detail to find the customer."
    rows = ctx.fuzzy_find("customers", **match)
    if not rows:
        return f"No customer matches {match}."
    if len(rows) > 1:
        return f"Error: {len(rows)} customers match {match}; ask for one more detail to tell them apart."
    return str(rows[0])


@tool(owner="agent", rw="write")
def verify_customer_identity(ctx: ToolContext, customer_id: str, date_of_birth: str = "", ssn_last4: str = "",
                             phone_number: str = "", email: str = "") -> str:
    """Verify the caller's identity against the resident's profile and record the outcome. Identity
    must be verified before any account, contract, care or billing information is discussed or any
    business is transacted. This tool performs the comparison itself: each detail the caller states
    is compared with the profile, the matching details are counted, and verification passes only when
    at least 2 details match. The customer reference number only retrieves the profile and never
    counts as a match. Callers usually state only some details, so pass exactly what was said and
    leave the rest blank. The outcome is recorded; if a first attempt fails and a later attempt with
    more details passes, the pass stands.

    Args:
        customer_id: Id - the customer reference number read from the customer profile lookup; required, used only to retrieve the profile.
        date_of_birth: Fixed format - the resident's date of birth as stated, YYYY-MM-DD; leave "" if not stated.
        ssn_last4: Fixed format - the last four digits of the resident's Social Security number as stated; leave "" if not stated.
        phone_number: Fixed format - the resident's 10-digit phone number as stated, digits only; leave "" if not stated.
        email: Verbatim - the email address on the profile as stated; leave "" if not stated.
    """
    if not customer_id:
        return "Error: customer_id is required; look up the customer profile first and pass its reference number."
    rows = ctx.find("customers", customer_id=customer_id)
    if not rows:
        return f"Error: no customer {customer_id}; cannot verify."
    rec = rows[0]
    # The locator customer_id is deliberately not compared: fetching a profile is not proving identity.
    supplied = {"date_of_birth": date_of_birth, "ssn_last4": ssn_last4,
                "phone_number": phone_number, "email": email}
    matched = sum(1 for field, value in supplied.items()
                  if value and str(rec.get(field) or "").strip().lower() == str(value).strip().lower())
    verified = matched >= 2
    rid = ctx.make_id("ver_", customer_id)
    # Store only the reproducible boolean; upsert and never downgrade a prior pass.
    prior = ctx.find("verification_log", verification_id=rid)
    verified = verified or bool(prior and prior[0].get("verified"))
    if prior:
        ctx.update("verification_log", rid, verified=verified, verified_at=ctx.now())
    else:
        ctx.create("verification_log", rid, verification_id=rid, customer_id=customer_id,
                   verified=verified, verified_at=ctx.now())
    if verified:
        return f"Identity verified for {customer_id} ({matched} detail(s) matched)."
    return (f"Identity NOT verified for {customer_id}: only {matched} of the 2 required details matched. "
            "Ask the caller for another detail on the profile and verify again.")


@tool(owner="agent", rw="write")
def transfer_to_human_agent(ctx: ToolContext, customer_id: str, reason: str) -> str:
    """Hand the customer over to a human representative of the Resident and Family Services team and
    record the handoff with its reason. Use POLICY_NOT_COVERED when no Larkspur policy can resolve
    what the customer is asking for; use CUSTOMER_REQUESTED when the customer has explicitly asked
    for a human representative 2 times.

    Args:
        customer_id: Id - the customer reference number read from the customer profile lookup; the profile must exist.
        reason: Enum - exactly one of POLICY_NOT_COVERED or CUSTOMER_REQUESTED, never free text.
    """
    allowed = {"POLICY_NOT_COVERED", "CUSTOMER_REQUESTED"}
    if reason not in allowed:
        return f"Error: unknown handoff reason '{reason}'. Valid: {', '.join(sorted(allowed))}."
    if not ctx.find("customers", customer_id=customer_id):
        return f"Error: no customer {customer_id}; cannot record the handoff."
    rid = ctx.make_id("hof_", customer_id, reason)
    ctx.create("handoff_log", rid, handoff_id=rid, customer_id=customer_id,
               reason=reason, created_at=ctx.now())
    return f"Handoff to a human representative recorded for {customer_id} ({reason})."


@tool(owner="agent", rw="read")
def find_independent_residencies(ctx: ToolContext, independent_residency_id: str = "", customer_id: str = "", referred_by_customer_id: str = "") -> str:
    """Look up independent living residency agreements: the apartment type and number, community, occupancy and second occupant, reservation, planned and actual move-in dates, the contracted monthly service fee and when it took effect, any increase notice on file, referral, notice of termination, intended and actual vacate dates, termination reason, and the current account balance and reservation deposit held.

    Every reference number below is optional; supply whichever you already hold and every matching
    record is returned in full. When nothing matches, a short note says so.

    Args:
        independent_residency_id: Id - the independent living residency reference number; leave "" if unknown.
        customer_id: Id - the customer reference number of the resident or guest the record belongs to; leave "" if unknown.
        referred_by_customer_id: Id - the customer reference number of the resident named as the referrer on a reservation; leave "" if unknown.
    """
    match = {k: v for k, v in {"independent_residency_id": independent_residency_id, "customer_id": customer_id, "referred_by_customer_id": referred_by_customer_id}.items() if v}
    rows = ctx.find("independent_residencies", **match)
    return str(rows) if rows else f"No independent_residencies records for {match}."


@tool(owner="agent", rw="read")
def find_independent_ledger(ctx: ToolContext, independent_entry_id: str = "", independent_residency_id: str = "", customer_id: str = "", source_entry_id: str = "", referred_residency_id: str = "", respite_stay_id: str = "") -> str:
    """Look up entries on independent living residency accounts: monthly fee and second person fee charges with the days they cover, community fees, scheduled service and amenity fees, late fees, payments and returned payments, credits with their reasons, reservation deposit receipts, applications, refunds and forfeits, and credit balance refunds.

    Every reference number below is optional; supply whichever you already hold and every matching
    record is returned in full. When nothing matches, a short note says so.

    Args:
        independent_entry_id: Id - the reference number of an independent living ledger entry itself; leave "" if unknown.
        independent_residency_id: Id - the independent living residency reference number; leave "" if unknown.
        customer_id: Id - the customer reference number of the resident or guest the record belongs to; leave "" if unknown.
        source_entry_id: Id - the reference number of the earlier entry this entry derives from - the charge credited or corrected, the payment returned, or the deposit or hours entry applied, refunded or restored; leave "" if unknown.
        referred_residency_id: Id - the residency reference number of a referred resident, carried on a referral credit; leave "" if unknown.
        respite_stay_id: Id - the respite or trial stay reference number; leave "" if unknown.
    """
    match = {k: v for k, v in {"independent_entry_id": independent_entry_id, "independent_residency_id": independent_residency_id, "customer_id": customer_id, "source_entry_id": source_entry_id, "referred_residency_id": referred_residency_id, "respite_stay_id": respite_stay_id}.items() if v}
    rows = ctx.find("independent_ledger", **match)
    return str(rows) if rows else f"No independent_ledger records for {match}."


@tool(owner="agent", rw="read")
def find_independent_requests(ctx: ToolContext, independent_request_id: str = "", customer_id: str = "", independent_residency_id: str = "") -> str:
    """Look up requests the desk has registered on independent living residencies for the customer's signature - move-out notices, notice withdrawals, reservation cancellations, apartment transfers and second occupant changes - with the date stated and whether each is awaiting signature, signed or withdrawn.

    Every reference number below is optional; supply whichever you already hold and every matching
    record is returned in full. When nothing matches, a short note says so.

    Args:
        independent_request_id: Id - the reference number of an independent living request itself; leave "" if unknown.
        customer_id: Id - the customer reference number of the resident or guest the record belongs to; leave "" if unknown.
        independent_residency_id: Id - the independent living residency reference number; leave "" if unknown.
    """
    match = {k: v for k, v in {"independent_request_id": independent_request_id, "customer_id": customer_id, "independent_residency_id": independent_residency_id}.items() if v}
    rows = ctx.find("independent_requests", **match)
    return str(rows) if rows else f"No independent_requests records for {match}."


@tool(owner="agent", rw="read")
def find_assisted_residencies(ctx: ToolContext, assisted_residency_id: str = "", customer_id: str = "") -> str:
    """Look up assisted living residency and care agreements: the care level billed and care points behind it, apartment type, number and rent, admission source and dates, any rent increase notice, direct insurer billing, the current or most recent absence, notice and vacate details, termination reason and the account balance.

    Every reference number below is optional; supply whichever you already hold and every matching
    record is returned in full. When nothing matches, a short note says so.

    Args:
        assisted_residency_id: Id - the assisted living residency reference number; leave "" if unknown.
        customer_id: Id - the customer reference number of the resident or guest the record belongs to; leave "" if unknown.
    """
    match = {k: v for k, v in {"assisted_residency_id": assisted_residency_id, "customer_id": customer_id}.items() if v}
    rows = ctx.find("assisted_residencies", **match)
    return str(rows) if rows else f"No assisted_residencies records for {match}."


@tool(owner="agent", rw="read")
def find_assisted_ledger(ctx: ToolContext, assisted_entry_id: str = "", assisted_residency_id: str = "", customer_id: str = "", source_entry_id: str = "", respite_stay_id: str = "", entrance_agreement_id: str = "") -> str:
    """Look up entries on assisted living accounts: rent and care fee charges with the care level and days they cover, care add-ons and service fees, community fees, late fees, payments by families or long-term care insurers, returned payments, credits with their reasons (prorations, absence care credits, entrance plan discounts, respite conversion credits, corrections) and credit balance refunds.

    Every reference number below is optional; supply whichever you already hold and every matching
    record is returned in full. When nothing matches, a short note says so.

    Args:
        assisted_entry_id: Id - the reference number of an assisted living ledger entry itself; leave "" if unknown.
        assisted_residency_id: Id - the assisted living residency reference number; leave "" if unknown.
        customer_id: Id - the customer reference number of the resident or guest the record belongs to; leave "" if unknown.
        source_entry_id: Id - the reference number of the earlier entry this entry derives from - the charge credited or corrected, the payment returned, or the deposit or hours entry applied, refunded or restored; leave "" if unknown.
        respite_stay_id: Id - the respite or trial stay reference number; leave "" if unknown.
        entrance_agreement_id: Id - the Entrance Fee Agreement reference number; leave "" if unknown.
    """
    match = {k: v for k, v in {"assisted_entry_id": assisted_entry_id, "assisted_residency_id": assisted_residency_id, "customer_id": customer_id, "source_entry_id": source_entry_id, "respite_stay_id": respite_stay_id, "entrance_agreement_id": entrance_agreement_id}.items() if v}
    rows = ctx.find("assisted_ledger", **match)
    return str(rows) if rows else f"No assisted_ledger records for {match}."


@tool(owner="agent", rw="read")
def find_assisted_assessments(ctx: ToolContext, assisted_assessment_id: str = "", assisted_residency_id: str = "", customer_id: str = "", source_assessment_id: str = "") -> str:
    """Look up nurse care-point assessments and written care level notices for assisted living residents: assessment date and type, care points, indicated level, wander risk, whether a level change was indicated, and for notices the notice date, stated level and effective date.

    Every reference number below is optional; supply whichever you already hold and every matching
    record is returned in full. When nothing matches, a short note says so.

    Args:
        assisted_assessment_id: Id - the reference number of an assessment or level notice record itself; leave "" if unknown.
        assisted_residency_id: Id - the assisted living residency reference number; leave "" if unknown.
        customer_id: Id - the customer reference number of the resident or guest the record belongs to; leave "" if unknown.
        source_assessment_id: Id - the reference number of the assessment a level notice follows; leave "" if unknown.
    """
    match = {k: v for k, v in {"assisted_assessment_id": assisted_assessment_id, "assisted_residency_id": assisted_residency_id, "customer_id": customer_id, "source_assessment_id": source_assessment_id}.items() if v}
    rows = ctx.find("assisted_assessments", **match)
    return str(rows) if rows else f"No assisted_assessments records for {match}."


@tool(owner="agent", rw="read")
def find_assisted_requests(ctx: ToolContext, assisted_request_id: str = "", customer_id: str = "", assisted_residency_id: str = "") -> str:
    """Look up requests the desk has registered on assisted living residencies for signature - admission withdrawals, move-out notices and withdrawals, apartment changes and change-of-condition reassessment requests - with their stated dates and status.

    Every reference number below is optional; supply whichever you already hold and every matching
    record is returned in full. When nothing matches, a short note says so.

    Args:
        assisted_request_id: Id - the reference number of an assisted living request itself; leave "" if unknown.
        customer_id: Id - the customer reference number of the resident or guest the record belongs to; leave "" if unknown.
        assisted_residency_id: Id - the assisted living residency reference number; leave "" if unknown.
    """
    match = {k: v for k, v in {"assisted_request_id": assisted_request_id, "customer_id": customer_id, "assisted_residency_id": assisted_residency_id}.items() if v}
    rows = ctx.find("assisted_requests", **match)
    return str(rows) if rows else f"No assisted_requests records for {match}."


@tool(owner="agent", rw="read")
def find_memory_residencies(ctx: ToolContext, memory_residency_id: str = "", customer_id: str = "") -> str:
    """Look up memory care residency agreements: suite type and care program billed, suite number, admission source and dates, care points, the monthly rate and its effective dates, direct insurer billing, absences, notices, vacate details, termination reason and the account balance.

    Every reference number below is optional; supply whichever you already hold and every matching
    record is returned in full. When nothing matches, a short note says so.

    Args:
        memory_residency_id: Id - the memory care residency reference number; leave "" if unknown.
        customer_id: Id - the customer reference number of the resident or guest the record belongs to; leave "" if unknown.
    """
    match = {k: v for k, v in {"memory_residency_id": memory_residency_id, "customer_id": customer_id}.items() if v}
    rows = ctx.find("memory_residencies", **match)
    return str(rows) if rows else f"No memory_residencies records for {match}."


@tool(owner="agent", rw="read")
def find_memory_ledger(ctx: ToolContext, memory_entry_id: str = "", memory_residency_id: str = "", customer_id: str = "", source_entry_id: str = "", respite_stay_id: str = "", entrance_agreement_id: str = "") -> str:
    """Look up entries on memory care accounts: monthly rate charges with the tier and days covered, add-ons and fees, community fees, late fees, payments, returned payments, credits with their reasons and credit balance refunds.

    Every reference number below is optional; supply whichever you already hold and every matching
    record is returned in full. When nothing matches, a short note says so.

    Args:
        memory_entry_id: Id - the reference number of a memory care ledger entry itself; leave "" if unknown.
        memory_residency_id: Id - the memory care residency reference number; leave "" if unknown.
        customer_id: Id - the customer reference number of the resident or guest the record belongs to; leave "" if unknown.
        source_entry_id: Id - the reference number of the earlier entry this entry derives from - the charge credited or corrected, the payment returned, or the deposit or hours entry applied, refunded or restored; leave "" if unknown.
        respite_stay_id: Id - the respite or trial stay reference number; leave "" if unknown.
        entrance_agreement_id: Id - the Entrance Fee Agreement reference number; leave "" if unknown.
    """
    match = {k: v for k, v in {"memory_entry_id": memory_entry_id, "memory_residency_id": memory_residency_id, "customer_id": customer_id, "source_entry_id": source_entry_id, "respite_stay_id": respite_stay_id, "entrance_agreement_id": entrance_agreement_id}.items() if v}
    rows = ctx.find("memory_ledger", **match)
    return str(rows) if rows else f"No memory_ledger records for {match}."


@tool(owner="agent", rw="read")
def find_memory_assessments(ctx: ToolContext, memory_assessment_id: str = "", memory_residency_id: str = "", customer_id: str = "") -> str:
    """Look up memory care assessments: date, type, score, indicated care program and any program notice with its effective date.

    Every reference number below is optional; supply whichever you already hold and every matching
    record is returned in full. When nothing matches, a short note says so.

    Args:
        memory_assessment_id: Id - the reference number of a memory care assessment record itself; leave "" if unknown.
        memory_residency_id: Id - the memory care residency reference number; leave "" if unknown.
        customer_id: Id - the customer reference number of the resident or guest the record belongs to; leave "" if unknown.
    """
    match = {k: v for k, v in {"memory_assessment_id": memory_assessment_id, "memory_residency_id": memory_residency_id, "customer_id": customer_id}.items() if v}
    rows = ctx.find("memory_assessments", **match)
    return str(rows) if rows else f"No memory_assessments records for {match}."


@tool(owner="agent", rw="read")
def find_memory_requests(ctx: ToolContext, memory_request_id: str = "", customer_id: str = "", memory_residency_id: str = "") -> str:
    """Look up requests registered on memory care residencies for the legal representative's signature - admission withdrawals, move-out notices and withdrawals, and suite changes - with their dates and status.

    Every reference number below is optional; supply whichever you already hold and every matching
    record is returned in full. When nothing matches, a short note says so.

    Args:
        memory_request_id: Id - the reference number of a memory care request itself; leave "" if unknown.
        customer_id: Id - the customer reference number of the resident or guest the record belongs to; leave "" if unknown.
        memory_residency_id: Id - the memory care residency reference number; leave "" if unknown.
    """
    match = {k: v for k, v in {"memory_request_id": memory_request_id, "customer_id": customer_id, "memory_residency_id": memory_residency_id}.items() if v}
    rows = ctx.find("memory_requests", **match)
    return str(rows) if rows else f"No memory_requests records for {match}."


@tool(owner="agent", rw="read")
def find_respite_stays(ctx: ToolContext, respite_stay_id: str = "", customer_id: str = "", converted_residency_id: str = "") -> str:
    """Look up respite and trial stays: stay type, community and apartment, booking date, planned arrival and departure, guests, locked nightly rate, care points, health documents on file, check-in and check-out dates, extensions, cancellation details, any conversion to a permanent residency, and the stay balance.

    Every reference number below is optional; supply whichever you already hold and every matching
    record is returned in full. When nothing matches, a short note says so.

    Args:
        respite_stay_id: Id - the respite or trial stay reference number; leave "" if unknown.
        customer_id: Id - the customer reference number of the resident or guest the record belongs to; leave "" if unknown.
        converted_residency_id: Id - the reference number of the permanent residency a stay converted into; leave "" if unknown.
    """
    match = {k: v for k, v in {"respite_stay_id": respite_stay_id, "customer_id": customer_id, "converted_residency_id": converted_residency_id}.items() if v}
    rows = ctx.find("respite_stays", **match)
    return str(rows) if rows else f"No respite_stays records for {match}."


@tool(owner="agent", rw="read")
def find_respite_ledger(ctx: ToolContext, respite_entry_id: str = "", respite_stay_id: str = "", customer_id: str = "", source_entry_id: str = "") -> str:
    """Look up entries on stay accounts: nightly charge segments with their nights, rates and basis, cancellation fees, add-ons, payments, returned payments, credits with their reasons and refunds.

    Every reference number below is optional; supply whichever you already hold and every matching
    record is returned in full. When nothing matches, a short note says so.

    Args:
        respite_entry_id: Id - the reference number of a stay ledger entry itself; leave "" if unknown.
        respite_stay_id: Id - the respite or trial stay reference number; leave "" if unknown.
        customer_id: Id - the customer reference number of the resident or guest the record belongs to; leave "" if unknown.
        source_entry_id: Id - the reference number of the earlier entry this entry derives from - the charge credited or corrected, the payment returned, or the deposit or hours entry applied, refunded or restored; leave "" if unknown.
    """
    match = {k: v for k, v in {"respite_entry_id": respite_entry_id, "respite_stay_id": respite_stay_id, "customer_id": customer_id, "source_entry_id": source_entry_id}.items() if v}
    rows = ctx.find("respite_ledger", **match)
    return str(rows) if rows else f"No respite_ledger records for {match}."


@tool(owner="agent", rw="read")
def find_respite_requests(ctx: ToolContext, respite_request_id: str = "", customer_id: str = "", respite_stay_id: str = "") -> str:
    """Look up stay cancellation and extension requests registered for the guest's signature, with the dates stated and their status.

    Every reference number below is optional; supply whichever you already hold and every matching
    record is returned in full. When nothing matches, a short note says so.

    Args:
        respite_request_id: Id - the reference number of a stay request itself; leave "" if unknown.
        customer_id: Id - the customer reference number of the resident or guest the record belongs to; leave "" if unknown.
        respite_stay_id: Id - the respite or trial stay reference number; leave "" if unknown.
    """
    match = {k: v for k, v in {"respite_request_id": respite_request_id, "customer_id": customer_id, "respite_stay_id": respite_stay_id}.items() if v}
    rows = ctx.find("respite_requests", **match)
    return str(rows) if rows else f"No respite_requests records for {match}."


@tool(owner="agent", rw="read")
def find_entrance_agreements(ctx: ToolContext, entrance_agreement_id: str = "", customer_id: str = "", independent_residency_id: str = "") -> str:
    """Look up Entrance Fee Agreements: refund plan, campus, apartment named, linked independent living residency, occupancy, entrance fee amount, qualification and screening dates, signing, planned and actual occupancy, notices, termination date and reason, re-occupancy of the apartment, refund due date and payee, estate documents on file, refundable balance and closing date.

    Every reference number below is optional; supply whichever you already hold and every matching
    record is returned in full. When nothing matches, a short note says so.

    Args:
        entrance_agreement_id: Id - the Entrance Fee Agreement reference number; leave "" if unknown.
        customer_id: Id - the customer reference number of the resident or guest the record belongs to; leave "" if unknown.
        independent_residency_id: Id - the independent living residency reference number; leave "" if unknown.
    """
    match = {k: v for k, v in {"entrance_agreement_id": entrance_agreement_id, "customer_id": customer_id, "independent_residency_id": independent_residency_id}.items() if v}
    rows = ctx.find("entrance_agreements", **match)
    return str(rows) if rows else f"No entrance_agreements records for {match}."


@tool(owner="agent", rw="read")
def find_entrance_ledger(ctx: ToolContext, entrance_entry_id: str = "", entrance_agreement_id: str = "", customer_id: str = "", offset_entry_id: str = "") -> str:
    """Look up entrance fee ledger entries: deposit and balance payments, the administrative retention, monthly amortization by month of occupancy, processing fees, offsets against unpaid residency charges, refurbishment deductions by work order, refund payments and annual tax letters.

    Every reference number below is optional; supply whichever you already hold and every matching
    record is returned in full. When nothing matches, a short note says so.

    Args:
        entrance_entry_id: Id - the reference number of an entrance fee ledger entry itself; leave "" if unknown.
        entrance_agreement_id: Id - the Entrance Fee Agreement reference number; leave "" if unknown.
        customer_id: Id - the customer reference number of the resident or guest the record belongs to; leave "" if unknown.
        offset_entry_id: Id - the reference number of the residency charge an entrance fee offset paid; leave "" if unknown.
    """
    match = {k: v for k, v in {"entrance_entry_id": entrance_entry_id, "entrance_agreement_id": entrance_agreement_id, "customer_id": customer_id, "offset_entry_id": offset_entry_id}.items() if v}
    rows = ctx.find("entrance_ledger", **match)
    return str(rows) if rows else f"No entrance_ledger records for {match}."


@tool(owner="agent", rw="read")
def find_entrance_requests(ctx: ToolContext, entrance_request_id: str = "", customer_id: str = "", entrance_agreement_id: str = "") -> str:
    """Look up requests registered on Entrance Fee Agreements for signature - rescissions, pre-occupancy cancellations, termination notices and withdrawals, occupancy extensions and apartment changes - with their dates and status.

    Every reference number below is optional; supply whichever you already hold and every matching
    record is returned in full. When nothing matches, a short note says so.

    Args:
        entrance_request_id: Id - the reference number of an entrance fee request itself; leave "" if unknown.
        customer_id: Id - the customer reference number of the resident or guest the record belongs to; leave "" if unknown.
        entrance_agreement_id: Id - the Entrance Fee Agreement reference number; leave "" if unknown.
    """
    match = {k: v for k, v in {"entrance_request_id": entrance_request_id, "customer_id": customer_id, "entrance_agreement_id": entrance_agreement_id}.items() if v}
    rows = ctx.find("entrance_requests", **match)
    return str(rows) if rows else f"No entrance_requests records for {match}."


@tool(owner="agent", rw="read")
def find_services_plans(ctx: ToolContext, services_plan_id: str = "", customer_id: str = "", independent_residency_id: str = "", assisted_residency_id: str = "") -> str:
    """Look up personal services plans: package in effect, the residence served, enrollment and effective dates, any scheduled package change, suspensions, cancellation notice, end date and reason, the hours available and the account balance.

    Every reference number below is optional; supply whichever you already hold and every matching
    record is returned in full. When nothing matches, a short note says so.

    Args:
        services_plan_id: Id - the personal services plan reference number; leave "" if unknown.
        customer_id: Id - the customer reference number of the resident or guest the record belongs to; leave "" if unknown.
        independent_residency_id: Id - the independent living residency reference number; leave "" if unknown.
        assisted_residency_id: Id - the assisted living residency reference number; leave "" if unknown.
    """
    match = {k: v for k, v in {"services_plan_id": services_plan_id, "customer_id": customer_id, "independent_residency_id": independent_residency_id, "assisted_residency_id": assisted_residency_id}.items() if v}
    rows = ctx.find("services_plans", **match)
    return str(rows) if rows else f"No services_plans records for {match}."


@tool(owner="agent", rw="read")
def find_services_ledger(ctx: ToolContext, services_entry_id: str = "", services_plan_id: str = "", customer_id: str = "", source_entry_id: str = "") -> str:
    """Look up personal services ledger entries: package fees, monthly hour grants, rollovers and expiries, hours drawn per service order and why, hours restored, hourly charges beyond the allotment, a la carte charges, late and returned payment fees, payments, returned payments and credits.

    Every reference number below is optional; supply whichever you already hold and every matching
    record is returned in full. When nothing matches, a short note says so.

    Args:
        services_entry_id: Id - the reference number of a personal services ledger entry itself; leave "" if unknown.
        services_plan_id: Id - the personal services plan reference number; leave "" if unknown.
        customer_id: Id - the customer reference number of the resident or guest the record belongs to; leave "" if unknown.
        source_entry_id: Id - the reference number of the earlier entry this entry derives from - the charge credited or corrected, the payment returned, or the deposit or hours entry applied, refunded or restored; leave "" if unknown.
    """
    match = {k: v for k, v in {"services_entry_id": services_entry_id, "services_plan_id": services_plan_id, "customer_id": customer_id, "source_entry_id": source_entry_id}.items() if v}
    rows = ctx.find("services_ledger", **match)
    return str(rows) if rows else f"No services_ledger records for {match}."


@tool(owner="agent", rw="read")
def find_services_orders(ctx: ToolContext, services_order_id: str = "", services_plan_id: str = "", customer_id: str = "") -> str:
    """Look up service orders: bookings with the service, date, start time, hours and booking moment, cancellations and no-shows with their timing, and completed visits with the minutes delivered.

    Every reference number below is optional; supply whichever you already hold and every matching
    record is returned in full. When nothing matches, a short note says so.

    Args:
        services_order_id: Id - the reference number of a service order record itself; leave "" if unknown.
        services_plan_id: Id - the personal services plan reference number; leave "" if unknown.
        customer_id: Id - the customer reference number of the resident or guest the record belongs to; leave "" if unknown.
    """
    match = {k: v for k, v in {"services_order_id": services_order_id, "services_plan_id": services_plan_id, "customer_id": customer_id}.items() if v}
    rows = ctx.find("services_orders", **match)
    return str(rows) if rows else f"No services_orders records for {match}."


@tool(owner="agent", rw="read")
def find_services_requests(ctx: ToolContext, services_request_id: str = "", customer_id: str = "", services_plan_id: str = "") -> str:
    """Look up personal services requests registered for the resident's signature - enrollments, withdrawals, package changes, cancellations and their withdrawals, and suspensions - with the dates stated and their status.

    Every reference number below is optional; supply whichever you already hold and every matching
    record is returned in full. When nothing matches, a short note says so.

    Args:
        services_request_id: Id - the reference number of a personal services request itself; leave "" if unknown.
        customer_id: Id - the customer reference number of the resident or guest the record belongs to; leave "" if unknown.
        services_plan_id: Id - the personal services plan reference number; leave "" if unknown.
    """
    match = {k: v for k, v in {"services_request_id": services_request_id, "customer_id": customer_id, "services_plan_id": services_plan_id}.items() if v}
    rows = ctx.find("services_requests", **match)
    return str(rows) if rows else f"No services_requests records for {match}."


@tool(owner="agent", rw="read")
def find_dining_plans(ctx: ToolContext, dining_plan_id: str = "", customer_id: str = "", independent_residency_id: str = "") -> str:
    """Look up dining plans: plan in effect, residency served, enrollment, effective and change dates, registered absences, cancellation notice, end date and reason, meal credits available and the account balance.

    Every reference number below is optional; supply whichever you already hold and every matching
    record is returned in full. When nothing matches, a short note says so.

    Args:
        dining_plan_id: Id - the dining plan reference number; leave "" if unknown.
        customer_id: Id - the customer reference number of the resident or guest the record belongs to; leave "" if unknown.
        independent_residency_id: Id - the independent living residency reference number; leave "" if unknown.
    """
    match = {k: v for k, v in {"dining_plan_id": dining_plan_id, "customer_id": customer_id, "independent_residency_id": independent_residency_id}.items() if v}
    rows = ctx.find("dining_plans", **match)
    return str(rows) if rows else f"No dining_plans records for {match}."


@tool(owner="agent", rw="read")
def find_dining_ledger(ctx: ToolContext, dining_entry_id: str = "", dining_plan_id: str = "", customer_id: str = "", source_entry_id: str = "") -> str:
    """Look up dining ledger entries: plan fees, monthly credit grants, rollovers and expiries, meals redeemed by check, meal period and diner, dining charges, payments, returned payments, restored credits and credits.

    Every reference number below is optional; supply whichever you already hold and every matching
    record is returned in full. When nothing matches, a short note says so.

    Args:
        dining_entry_id: Id - the reference number of a dining ledger entry itself; leave "" if unknown.
        dining_plan_id: Id - the dining plan reference number; leave "" if unknown.
        customer_id: Id - the customer reference number of the resident or guest the record belongs to; leave "" if unknown.
        source_entry_id: Id - the reference number of the earlier entry this entry derives from - the charge credited or corrected, the payment returned, or the deposit or hours entry applied, refunded or restored; leave "" if unknown.
    """
    match = {k: v for k, v in {"dining_entry_id": dining_entry_id, "dining_plan_id": dining_plan_id, "customer_id": customer_id, "source_entry_id": source_entry_id}.items() if v}
    rows = ctx.find("dining_ledger", **match)
    return str(rows) if rows else f"No dining_ledger records for {match}."


@tool(owner="agent", rw="read")
def find_dining_requests(ctx: ToolContext, dining_request_id: str = "", customer_id: str = "", dining_plan_id: str = "") -> str:
    """Look up dining requests registered for the resident's signature - enrollments, withdrawals, plan changes, cancellations and their withdrawals - with their dates and status.

    Every reference number below is optional; supply whichever you already hold and every matching
    record is returned in full. When nothing matches, a short note says so.

    Args:
        dining_request_id: Id - the reference number of a dining request itself; leave "" if unknown.
        customer_id: Id - the customer reference number of the resident or guest the record belongs to; leave "" if unknown.
        dining_plan_id: Id - the dining plan reference number; leave "" if unknown.
    """
    match = {k: v for k, v in {"dining_request_id": dining_request_id, "customer_id": customer_id, "dining_plan_id": dining_plan_id}.items() if v}
    rows = ctx.find("dining_requests", **match)
    return str(rows) if rows else f"No dining_requests records for {match}."


@tool(owner="agent", rw="read")
def find_verification_log(ctx: ToolContext, verification_id: str = "", customer_id: str = "") -> str:
    """Look up the identity verification outcome recorded for a customer during this contact and when it was last attempted.

    Every reference number below is optional; supply whichever you already hold and every matching
    record is returned in full. When nothing matches, a short note says so.

    Args:
        verification_id: Id - the reference number of an identity verification record itself; leave "" if unknown.
        customer_id: Id - the customer reference number of the resident or guest the record belongs to; leave "" if unknown.
    """
    match = {k: v for k, v in {"verification_id": verification_id, "customer_id": customer_id}.items() if v}
    rows = ctx.find("verification_log", **match)
    return str(rows) if rows else f"No verification_log records for {match}."


@tool(owner="agent", rw="read")
def find_handoff_log(ctx: ToolContext, handoff_id: str = "", customer_id: str = "") -> str:
    """Look up handoffs of a customer to a human representative, with the reason recorded and the moment of the handoff.

    Every reference number below is optional; supply whichever you already hold and every matching
    record is returned in full. When nothing matches, a short note says so.

    Args:
        handoff_id: Id - the reference number of a handoff record itself; leave "" if unknown.
        customer_id: Id - the customer reference number of the resident or guest the record belongs to; leave "" if unknown.
    """
    match = {k: v for k, v in {"handoff_id": handoff_id, "customer_id": customer_id}.items() if v}
    rows = ctx.find("handoff_log", **match)
    return str(rows) if rows else f"No handoff_log records for {match}."

"""Shared tools for env_0083_fleet_fuel_card_provider (Meridian Fleet Payments).

One record finder per table (the customers finder doubles as the identity entry), the identity
verification write and the transfer-to-human handoff write. Ordinary finders perform plain lookups
and never encode policy decisions.
"""

from erlbench import ToolContext, tool


@tool(owner="agent", rw="read")
def find_customers(ctx: ToolContext, customer_id: str = "", phone: str = "", email: str = "", legal_name: str = "", admin_name: str = "") -> str:
    """Find the fleet account a call is about. A customer can be found by the customer reference number or by what a caller can naturally state: the registered business phone number, the administrator's registered email, the fleet's legal business name or the name of its account administrator. Every criterion is optional; supply whichever are known. The returned profile shows the legal and trading names, the account administrator, the registered phone, email and billing ZIP code, the last four digits of the fleet's federal Employer Identification Number, the date the profile was opened and the kind of organization the fleet is. Finding a profile does not verify the caller's identity.

    Args:
        customer_id: The customer (fleet account) reference number; leave "" if unknown.
        phone: The registered business phone number as the caller states it (10 digits); leave "" if not provided.
        email: The account administrator's registered email address as the caller states it; leave "" if not provided.
        legal_name: The fleet's registered legal business name as the caller states it; leave "" if not provided.
        admin_name: The full name of the fleet's authorized account administrator as the caller states it; leave "" if not provided.
    """
    match = {k: v for k, v in {"customer_id": customer_id, "phone": phone, "email": email,
                               "legal_name": legal_name, "admin_name": admin_name}.items() if v}
    if not match:
        return "Error: provide at least one reference number or profile detail to find the customer."
    rows = ctx.fuzzy_find("customers", **match)
    if not rows:
        return f"No customer matches {match}."
    if len(rows) > 1:
        return f"Error: {len(rows)} customers match {match}; ask for one more detail to tell them apart."
    return str(rows[0])


@tool(owner="agent", rw="write")
def verify_customer_identity(ctx: ToolContext, customer_id: str, phone: str = "", email: str = "", ein_last4: str = "", billing_zip: str = "") -> str:
    """Verify the caller's identity for a fleet account and record the outcome. No account details may be discussed or changed, and no money moved, until verification has passed. This tool makes the comparison itself: it checks each piece of identity information the caller states against the customer profile, counts the matches, and passes only when at least 2 of them match. The customer reference number only retrieves the profile and never counts as a match. Callers usually know only some of the details, so pass only the values the caller actually gave, exactly as given, and leave the rest "". The outcome is recorded; if a first attempt fails and a later attempt with more details passes, the pass stands.

    Args:
        customer_id: The customer reference number read from the customer profile lookup. Required; used only to retrieve the profile and not counted as a match.
        phone: The registered business phone number as the caller states it (10 digits, no punctuation); leave "" if not stated.
        email: The account administrator's registered email address as the caller states it; leave "" if not stated.
        ein_last4: The last four digits of the fleet's federal Employer Identification Number as the caller states them; leave "" if not stated.
        billing_zip: The 5-digit ZIP code of the billing address as the caller states it; leave "" if not stated.
    """
    if not customer_id:
        return "Error: customer_id is required; find the customer first and pass their reference number."
    rows = ctx.find("customers", customer_id=customer_id)
    if not rows:
        return f"Error: no customer {customer_id}; cannot verify."
    rec = rows[0]
    supplied = {"phone": phone, "email": email, "ein_last4": ein_last4, "billing_zip": billing_zip}
    matched = sum(1 for field, value in supplied.items() if value and str(rec.get(field, "")).strip().lower() == str(value).strip().lower())
    verified = matched >= 2
    rid = ctx.make_id("ver_", customer_id)
    prior = ctx.find("verification_log", verification_id=rid)
    verified = verified or bool(prior and prior[0].get("verified"))
    if prior:
        ctx.update("verification_log", rid, verified=verified, verified_at=ctx.now())
    else:
        ctx.create("verification_log", rid, verification_id=rid, customer_id=customer_id,
                   verified=verified, verified_at=ctx.now())
    return (f"Identity verified for {customer_id} ({matched} detail(s) matched)." if verified
            else f"Identity NOT verified for {customer_id} (only {matched} of the required 2 details matched). Ask the caller for another detail on file and try again.")


@tool(owner="agent", rw="write")
def transfer_to_human_agent(ctx: ToolContext, customer_id: str, reason: str) -> str:
    """Hand the caller over to a human Meridian fleet support representative and record the handoff with its reason. Use it when no Meridian rule allows the request to be resolved, or when the caller has explicitly asked for a human representative at least 2 times.

    Args:
        customer_id: The customer reference number read from the customer profile lookup (the profile must exist).
        reason: Why the call is handed over; exactly one of POLICY_NOT_COVERED (no Meridian rule allows the request to be resolved) or CUSTOMER_REQUESTED (the caller has explicitly asked for a human representative at least 2 times). Never free text.
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
def find_fleet_programs(ctx: ToolContext, program_id: str = "", customer_id: str = "", credit_line_id: str = "") -> str:
    """Look up Fleet Card Program records: the program tier and any earlier tier with the date the current tier took effect, status, program number, application, approval and closure dates, the credit line that bills the program, federal excise tax exempt billing status with its certificate date, and IFTA report enrollment.

    Every criterion is optional; supply whichever reference numbers are already known and all matching records are returned. When nothing matches, the reply says so.

    Args:
        program_id: Reference number of this record itself — the Fleet Card Program reference number; leave "" if unknown.
        customer_id: The customer (fleet account) reference number the records belong to; leave "" if unknown.
        credit_line_id: The credit line reference number the records belong to; leave "" if unknown.
    """
    match = {k: v for k, v in {"program_id": program_id, "customer_id": customer_id, "credit_line_id": credit_line_id}.items() if v}
    rows = ctx.find("fleet_programs", **match)
    return str(rows) if rows else f"No fleet_programs records for {match}."


@tool(owner="agent", rw="read")
def find_program_transactions(ctx: ToolContext, program_txn_id: str = "", program_id: str = "", customer_id: str = "", fleet_card_id: str = "", original_txn_id: str = "") -> str:
    """Look up purchases and merchant credits posted to card programs, with their Level-3 detail: merchant reference, purchase date and time, posting date, merchant, site number, state and country, network, service type, product, gallons, pump price per gallon, gross amount, partner-site discount, net amount billed, odometer, driver ID entered, how the card was read, and for a merchant credit the purchase it credits and why.

    Every criterion is optional; supply whichever reference numbers are already known and all matching records are returned. When nothing matches, the reply says so.

    Args:
        program_txn_id: Reference number of this record itself — the posted purchase or merchant credit reference number; leave "" if unknown.
        program_id: The Fleet Card Program reference number the records belong to; leave "" if unknown.
        customer_id: The customer (fleet account) reference number the records belong to; leave "" if unknown.
        fleet_card_id: The card reference number the records belong to; leave "" if unknown.
        original_txn_id: Reference number of the purchase that a merchant credit credits; leave "" if unknown.
    """
    match = {k: v for k, v in {"program_txn_id": program_txn_id, "program_id": program_id, "customer_id": customer_id, "fleet_card_id": fleet_card_id, "original_txn_id": original_txn_id}.items() if v}
    rows = ctx.find("program_transactions", **match)
    return str(rows) if rows else f"No program_transactions records for {match}."


@tool(owner="agent", rw="read")
def find_program_charges(ctx: ToolContext, program_charge_id: str = "", program_id: str = "", customer_id: str = "", related_txn_id: str = "", original_charge_id: str = "") -> str:
    """Look up program fees and credits: monthly per-card fees with the counted and billed cards and the per-card rate, monthly program fees with the cycle's billed gallons, out-of-network, manual-entry and cross-border fees with the purchase each belongs to, IFTA report, setup and early termination fees, federal excise tax credits and their offsets, and fee reversals with the fee reversed and the reason.

    Every criterion is optional; supply whichever reference numbers are already known and all matching records are returned. When nothing matches, the reply says so.

    Args:
        program_charge_id: Reference number of this record itself — the program fee or credit reference number; leave "" if unknown.
        program_id: The Fleet Card Program reference number the records belong to; leave "" if unknown.
        customer_id: The customer (fleet account) reference number the records belong to; leave "" if unknown.
        related_txn_id: Reference number of the purchase (or merchant credit) a fee or credit belongs to; leave "" if unknown.
        original_charge_id: Reference number of the program fee or credit that a reversal or offset concerns; leave "" if unknown.
    """
    match = {k: v for k, v in {"program_charge_id": program_charge_id, "program_id": program_id, "customer_id": customer_id, "related_txn_id": related_txn_id, "original_charge_id": original_charge_id}.items() if v}
    rows = ctx.find("program_charges", **match)
    return str(rows) if rows else f"No program_charges records for {match}."


@tool(owner="agent", rw="read")
def find_credit_lines(ctx: ToolContext, credit_line_id: str = "", customer_id: str = "") -> str:
    """Look up commercial credit line records: tier, status, permanent credit limit, any temporary increase and its last day, billing cycle and payment terms, statement delivery, autopay enrollment, any wire-only payment requirement, the current balance owed, the security deposit held, and the application, approval, review and closure dates.

    Every criterion is optional; supply whichever reference numbers are already known and all matching records are returned. When nothing matches, the reply says so.

    Args:
        credit_line_id: Reference number of this record itself — the credit line reference number; leave "" if unknown.
        customer_id: The customer (fleet account) reference number the records belong to; leave "" if unknown.
    """
    match = {k: v for k, v in {"credit_line_id": credit_line_id, "customer_id": customer_id}.items() if v}
    rows = ctx.find("credit_lines", **match)
    return str(rows) if rows else f"No credit_lines records for {match}."


@tool(owner="agent", rw="read")
def find_credit_statements(ctx: ToolContext, statement_id: str = "", credit_line_id: str = "", customer_id: str = "") -> str:
    """Look up credit line statements: the cycle covered, statement date and due date, previous balance, payments, purchases, program fees, card fees, maintenance, dispute credits, rebate credits, credit fees, new balance, the past-due information line and how the statement was delivered.

    Every criterion is optional; supply whichever reference numbers are already known and all matching records are returned. When nothing matches, the reply says so.

    Args:
        statement_id: Reference number of this record itself — the statement reference number; leave "" if unknown.
        credit_line_id: The credit line reference number the records belong to; leave "" if unknown.
        customer_id: The customer (fleet account) reference number the records belong to; leave "" if unknown.
    """
    match = {k: v for k, v in {"statement_id": statement_id, "credit_line_id": credit_line_id, "customer_id": customer_id}.items() if v}
    rows = ctx.find("credit_statements", **match)
    return str(rows) if rows else f"No credit_statements records for {match}."


@tool(owner="agent", rw="read")
def find_credit_ledger(ctx: ToolContext, credit_entry_id: str = "", credit_line_id: str = "", customer_id: str = "", statement_id: str = "", original_entry_id: str = "") -> str:
    """Look up credit line ledger entries: payments with their confirmation or trace number and method, returned payments with their return reason, late fees with the past-due amount they were figured on, returned-payment and paper statement fees, fee reversals with the fee reversed and the reason, and security deposits received, refunded or applied.

    Every criterion is optional; supply whichever reference numbers are already known and all matching records are returned. When nothing matches, the reply says so.

    Args:
        credit_entry_id: Reference number of this record itself — the credit ledger entry reference number; leave "" if unknown.
        credit_line_id: The credit line reference number the records belong to; leave "" if unknown.
        customer_id: The customer (fleet account) reference number the records belong to; leave "" if unknown.
        statement_id: The statement reference number the records belong to; leave "" if unknown.
        original_entry_id: Reference number of the earlier entry this entry reverses, returns or corrects; leave "" if unknown.
    """
    match = {k: v for k, v in {"credit_entry_id": credit_entry_id, "credit_line_id": credit_line_id, "customer_id": customer_id, "statement_id": statement_id, "original_entry_id": original_entry_id}.items() if v}
    rows = ctx.find("credit_ledger", **match)
    return str(rows) if rows else f"No credit_ledger records for {match}."


@tool(owner="agent", rw="read")
def find_credit_requests(ctx: ToolContext, credit_request_id: str = "", credit_line_id: str = "", customer_id: str = "") -> str:
    """Look up permanent credit limit increase requests: the date asked, the limit asked for, the underwriting decision and its date, and the limit approved.

    Every criterion is optional; supply whichever reference numbers are already known and all matching records are returned. When nothing matches, the reply says so.

    Args:
        credit_request_id: Reference number of this record itself — the limit increase request reference number; leave "" if unknown.
        credit_line_id: The credit line reference number the records belong to; leave "" if unknown.
        customer_id: The customer (fleet account) reference number the records belong to; leave "" if unknown.
    """
    match = {k: v for k, v in {"credit_request_id": credit_request_id, "credit_line_id": credit_line_id, "customer_id": customer_id}.items() if v}
    rows = ctx.find("credit_requests", **match)
    return str(rows) if rows else f"No credit_requests records for {match}."


@tool(owner="agent", rw="read")
def find_fleet_cards(ctx: ToolContext, fleet_card_id: str = "", customer_id: str = "", program_id: str = "", control_profile_id: str = "", replaces_card_id: str = "") -> str:
    """Look up fleet cards: card product, status, last four digits, the program and purchase-control profile it belongs to, the vehicle unit number and tank capacity or the assigned driver and driver ID, order, activation, hold, expiry and renewal dates, the card it replaced, and the date, time and reason it closed.

    Every criterion is optional; supply whichever reference numbers are already known and all matching records are returned. When nothing matches, the reply says so.

    Args:
        fleet_card_id: Reference number of this record itself — the card reference number; leave "" if unknown.
        customer_id: The customer (fleet account) reference number the records belong to; leave "" if unknown.
        program_id: The Fleet Card Program reference number the records belong to; leave "" if unknown.
        control_profile_id: The purchase-control profile reference number the records belong to; leave "" if unknown.
        replaces_card_id: Reference number of the card this card replaced; leave "" if unknown.
    """
    match = {k: v for k, v in {"fleet_card_id": fleet_card_id, "customer_id": customer_id, "program_id": program_id, "control_profile_id": control_profile_id, "replaces_card_id": replaces_card_id}.items() if v}
    rows = ctx.find("fleet_cards", **match)
    return str(rows) if rows else f"No fleet_cards records for {match}."


@tool(owner="agent", rw="read")
def find_card_events(ctx: ToolContext, card_event_id: str = "", fleet_card_id: str = "", customer_id: str = "", new_card_id: str = "", original_event_id: str = "") -> str:
    """Look up card events: replacements ordered with their reason, the replacement card and the fee charged, expedited and overnight shipping fees, card fee reversals with the fee reversed and the reason, and PIN resets with who performed them.

    Every criterion is optional; supply whichever reference numbers are already known and all matching records are returned. When nothing matches, the reply says so.

    Args:
        card_event_id: Reference number of this record itself — the card event reference number; leave "" if unknown.
        fleet_card_id: The card reference number the records belong to; leave "" if unknown.
        customer_id: The customer (fleet account) reference number the records belong to; leave "" if unknown.
        new_card_id: Reference number of the replacement card ordered; leave "" if unknown.
        original_event_id: Reference number of the card fee a reversal concerns; leave "" if unknown.
    """
    match = {k: v for k, v in {"card_event_id": card_event_id, "fleet_card_id": fleet_card_id, "customer_id": customer_id, "new_card_id": new_card_id, "original_event_id": original_event_id}.items() if v}
    rows = ctx.find("card_events", **match)
    return str(rows) if rows else f"No card_events records for {match}."


@tool(owner="agent", rw="read")
def find_dispute_cases(ctx: ToolContext, dispute_case_id: str = "", customer_id: str = "", program_id: str = "", program_txn_id: str = "", fleet_card_id: str = "", statement_id: str = "") -> str:
    """Look up transaction dispute cases: case type, status, the disputed purchase, its card, program and the statement that billed it, the dates opened, affidavit requested and received, review started, chargeback filed and resolved, the gallons, price or promised credit the fleet stated, the disputed amount, any police report number and who bears the loss.

    Every criterion is optional; supply whichever reference numbers are already known and all matching records are returned. When nothing matches, the reply says so.

    Args:
        dispute_case_id: Reference number of this record itself — the dispute case reference number; leave "" if unknown.
        customer_id: The customer (fleet account) reference number the records belong to; leave "" if unknown.
        program_id: The Fleet Card Program reference number the records belong to; leave "" if unknown.
        program_txn_id: The posted purchase or merchant credit reference number the records belong to; leave "" if unknown.
        fleet_card_id: The card reference number the records belong to; leave "" if unknown.
        statement_id: The statement reference number the records belong to; leave "" if unknown.
    """
    match = {k: v for k, v in {"dispute_case_id": dispute_case_id, "customer_id": customer_id, "program_id": program_id, "program_txn_id": program_txn_id, "fleet_card_id": fleet_card_id, "statement_id": statement_id}.items() if v}
    rows = ctx.find("dispute_cases", **match)
    return str(rows) if rows else f"No dispute_cases records for {match}."


@tool(owner="agent", rw="read")
def find_dispute_entries(ctx: ToolContext, dispute_entry_id: str = "", dispute_case_id: str = "", customer_id: str = "", original_entry_id: str = "") -> str:
    """Look up dispute credits: provisional and final credits with any part that credits per-transaction fees, and reversals of provisional credit with the credit reversed and the reason.

    Every criterion is optional; supply whichever reference numbers are already known and all matching records are returned. When nothing matches, the reply says so.

    Args:
        dispute_entry_id: Reference number of this record itself — the dispute credit reference number; leave "" if unknown.
        dispute_case_id: The dispute case reference number the records belong to; leave "" if unknown.
        customer_id: The customer (fleet account) reference number the records belong to; leave "" if unknown.
        original_entry_id: Reference number of the earlier entry this entry reverses, returns or corrects; leave "" if unknown.
    """
    match = {k: v for k, v in {"dispute_entry_id": dispute_entry_id, "dispute_case_id": dispute_case_id, "customer_id": customer_id, "original_entry_id": original_entry_id}.items() if v}
    rows = ctx.find("dispute_entries", **match)
    return str(rows) if rows else f"No dispute_entries records for {match}."


@tool(owner="agent", rw="read")
def find_rebate_plans(ctx: ToolContext, rebate_plan_id: str = "", customer_id: str = "") -> str:
    """Look up volume rebate plans: the rebate schedule and any earlier schedule with the date the current one took effect, status, enrollment, activation and end dates, payout method and the earned rebate not yet paid.

    Every criterion is optional; supply whichever reference numbers are already known and all matching records are returned. When nothing matches, the reply says so.

    Args:
        rebate_plan_id: Reference number of this record itself — the rebate plan reference number; leave "" if unknown.
        customer_id: The customer (fleet account) reference number the records belong to; leave "" if unknown.
    """
    match = {k: v for k, v in {"rebate_plan_id": rebate_plan_id, "customer_id": customer_id}.items() if v}
    rows = ctx.find("rebate_plans", **match)
    return str(rows) if rows else f"No rebate_plans records for {match}."


@tool(owner="agent", rw="read")
def find_rebate_entries(ctx: ToolContext, rebate_entry_id: str = "", rebate_plan_id: str = "", customer_id: str = "", statement_id: str = "", original_entry_id: str = "") -> str:
    """Look up rebate entries: monthly accruals with qualifying and diesel gallons, the rate applied and the amount earned, upward and downward corrections, forfeitures with their reason, statement credits with the statement credited, and ACH payouts.

    Every criterion is optional; supply whichever reference numbers are already known and all matching records are returned. When nothing matches, the reply says so.

    Args:
        rebate_entry_id: Reference number of this record itself — the rebate entry reference number; leave "" if unknown.
        rebate_plan_id: The rebate plan reference number the records belong to; leave "" if unknown.
        customer_id: The customer (fleet account) reference number the records belong to; leave "" if unknown.
        statement_id: The statement reference number the records belong to; leave "" if unknown.
        original_entry_id: Reference number of the earlier entry this entry reverses, returns or corrects; leave "" if unknown.
    """
    match = {k: v for k, v in {"rebate_entry_id": rebate_entry_id, "rebate_plan_id": rebate_plan_id, "customer_id": customer_id, "statement_id": statement_id, "original_entry_id": original_entry_id}.items() if v}
    rows = ctx.find("rebate_entries", **match)
    return str(rows) if rows else f"No rebate_entries records for {match}."


@tool(owner="agent", rw="read")
def find_control_profiles(ctx: ToolContext, control_profile_id: str = "", customer_id: str = "", program_id: str = "") -> str:
    """Look up purchase-control profiles: template, status, profile name, the program it belongs to, per-transaction, daily and weekly dollar limits, daily gallon and purchase-count limits, allowed days and time window, the tank-capacity check, and the set-up, in-force and retirement dates.

    Every criterion is optional; supply whichever reference numbers are already known and all matching records are returned. When nothing matches, the reply says so.

    Args:
        control_profile_id: Reference number of this record itself — the purchase-control profile reference number; leave "" if unknown.
        customer_id: The customer (fleet account) reference number the records belong to; leave "" if unknown.
        program_id: The Fleet Card Program reference number the records belong to; leave "" if unknown.
    """
    match = {k: v for k, v in {"control_profile_id": control_profile_id, "customer_id": customer_id, "program_id": program_id}.items() if v}
    rows = ctx.find("control_profiles", **match)
    return str(rows) if rows else f"No control_profiles records for {match}."


@tool(owner="agent", rw="read")
def find_control_events(ctx: ToolContext, control_event_id: str = "", control_profile_id: str = "", customer_id: str = "", fleet_card_id: str = "") -> str:
    """Look up authorization declines and one-time overrides: the card, date and time, site, product, amount and gallons attempted, the decline reason, and for an override the amount allowed and when it expires.

    Every criterion is optional; supply whichever reference numbers are already known and all matching records are returned. When nothing matches, the reply says so.

    Args:
        control_event_id: Reference number of this record itself — the decline or override reference number; leave "" if unknown.
        control_profile_id: The purchase-control profile reference number the records belong to; leave "" if unknown.
        customer_id: The customer (fleet account) reference number the records belong to; leave "" if unknown.
        fleet_card_id: The card reference number the records belong to; leave "" if unknown.
    """
    match = {k: v for k, v in {"control_event_id": control_event_id, "control_profile_id": control_profile_id, "customer_id": customer_id, "fleet_card_id": fleet_card_id}.items() if v}
    rows = ctx.find("control_events", **match)
    return str(rows) if rows else f"No control_events records for {match}."


@tool(owner="agent", rw="read")
def find_maint_programs(ctx: ToolContext, maint_program_id: str = "", customer_id: str = "", program_id: str = "") -> str:
    """Look up fleet maintenance enrollments: service level, status, the card program covered, the number of vehicles enrolled and the enrollment, start and end dates.

    Every criterion is optional; supply whichever reference numbers are already known and all matching records are returned. When nothing matches, the reply says so.

    Args:
        maint_program_id: Reference number of this record itself — the maintenance enrollment reference number; leave "" if unknown.
        customer_id: The customer (fleet account) reference number the records belong to; leave "" if unknown.
        program_id: The Fleet Card Program reference number the records belong to; leave "" if unknown.
    """
    match = {k: v for k, v in {"maint_program_id": maint_program_id, "customer_id": customer_id, "program_id": program_id}.items() if v}
    rows = ctx.find("maint_programs", **match)
    return str(rows) if rows else f"No maint_programs records for {match}."


@tool(owner="agent", rw="read")
def find_maint_orders(ctx: ToolContext, repair_order_id: str = "", maint_program_id: str = "", customer_id: str = "", fleet_card_id: str = "", original_order_id: str = "") -> str:
    """Look up maintenance activity: repair-order approvals and postings with the shop, network, kind of work, labor, parts, discount, amount and approval standing, shop credits, monthly per-vehicle service fees, early end fees and fee reversals.

    Every criterion is optional; supply whichever reference numbers are already known and all matching records are returned. When nothing matches, the reply says so.

    Args:
        repair_order_id: Reference number of this record itself — the maintenance activity reference number; leave "" if unknown.
        maint_program_id: The maintenance enrollment reference number the records belong to; leave "" if unknown.
        customer_id: The customer (fleet account) reference number the records belong to; leave "" if unknown.
        fleet_card_id: The card reference number the records belong to; leave "" if unknown.
        original_order_id: Reference number of the maintenance row a credit or reversal concerns; leave "" if unknown.
    """
    match = {k: v for k, v in {"repair_order_id": repair_order_id, "maint_program_id": maint_program_id, "customer_id": customer_id, "fleet_card_id": fleet_card_id, "original_order_id": original_order_id}.items() if v}
    rows = ctx.find("maint_orders", **match)
    return str(rows) if rows else f"No maint_orders records for {match}."


@tool(owner="agent", rw="read")
def find_verification_log(ctx: ToolContext, verification_id: str = "", customer_id: str = "") -> str:
    """Look up identity verification outcomes recorded for a customer, with whether verification passed and when it was last attempted.

    Every criterion is optional; supply whichever reference numbers are already known and all matching records are returned. When nothing matches, the reply says so.

    Args:
        verification_id: Reference number of this record itself — the verification record reference number; leave "" if unknown.
        customer_id: The customer (fleet account) reference number the records belong to; leave "" if unknown.
    """
    match = {k: v for k, v in {"verification_id": verification_id, "customer_id": customer_id}.items() if v}
    rows = ctx.find("verification_log", **match)
    return str(rows) if rows else f"No verification_log records for {match}."


@tool(owner="agent", rw="read")
def find_handoff_log(ctx: ToolContext, handoff_id: str = "", customer_id: str = "") -> str:
    """Look up records of customers handed to a human representative, with the reason and when it happened.

    Every criterion is optional; supply whichever reference numbers are already known and all matching records are returned. When nothing matches, the reply says so.

    Args:
        handoff_id: Reference number of this record itself — the handoff record reference number; leave "" if unknown.
        customer_id: The customer (fleet account) reference number the records belong to; leave "" if unknown.
    """
    match = {k: v for k, v in {"handoff_id": handoff_id, "customer_id": customer_id}.items() if v}
    rows = ctx.find("handoff_log", **match)
    return str(rows) if rows else f"No handoff_log records for {match}."

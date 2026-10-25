"""Shared tools for env_0075_franchised_auto_dealer_group (Kessler Automotive Group).

Every tool here is a share tool: always present in its owner's tool list. This file holds the
record-lookup layer (one finder per record type; the customer finder also serves as the identity
entry), the identity-verification write and the handoff to a human representative.
Customer-originated writes (signing cancellation requests, authorizing estimates) are hidden task
tools in each difficulty's task_tools.py, never share tools.

Scenario operational constants: identity verification passes when at least K = 2 credentials
match the profile; a customer who explicitly asks for a human R = 2 times is handed off as
CUSTOMER_REQUESTED.
"""

from erlbench import ToolContext, tool


@tool(owner="agent", rw="read")
def find_customers(ctx: ToolContext, customer_id: str = "", name: str = "", phone: str = "", email: str = "") -> str:
    """Look up a customer profile to establish whose account this conversation is about. You can search by the customer reference number, or by what the caller naturally tells you: the name on the profile (an individual's legal name or a fleet customer's registered business name), the phone number on file, or the email address on file. Every criterion is optional; supply whichever you have. The profile shows whether the customer is an individual or a fleet business, their phone number, email, billing ZIP code, the last four characters of their driver's license or federal EIN, their state of residence and the date the profile was opened. Finding a profile does not verify the caller's identity; identity is confirmed separately.

    Args:
        customer_id: The customer reference number, if already known. Leave "" if unknown.
        name: The customer's name exactly as the caller states it (individual legal name, or registered business name for a fleet customer). Leave "" if not provided.
        phone: The phone number the caller gives, 10 digits. Leave "" if not provided.
        email: The email address the caller gives. Leave "" if not provided.
    """
    match = {k: v for k, v in {"customer_id": customer_id, "name": name,
                               "phone": phone, "email": email}.items() if v}
    if not match:
        return "Error: provide at least one reference number or profile detail to find the customer."
    rows = ctx.fuzzy_find("customers", **match)
    if not rows:
        return f"No customer matches {match}."
    if len(rows) > 1:
        return f"Error: {len(rows)} customers match {match}; ask the caller for one more detail to tell them apart."
    return str(rows[0])


@tool(owner="agent", rw="write")
def verify_customer_identity(ctx: ToolContext, customer_id: str, phone: str = "", email: str = "",
                             home_zip: str = "", id_last4: str = "", profile_opened_date: str = "") -> str:
    """Confirm the caller's identity and record the outcome. Identity must be confirmed before any account information is discussed or any business is transacted on the customer's behalf. This tool performs the comparison itself: it compares each piece of identity information the caller states with the customer profile, counts how many agree, and confirms identity only when at least 2 agree. The customer reference number is used only to open the profile and never counts as a match. Callers usually know only some of these details, so pass exactly what the caller said and leave the rest blank. The outcome is recorded; if a first attempt does not pass and a later attempt with more information does, the confirmation stands.

    Args:
        customer_id: The customer reference number read from the customer profile lookup. Required; it opens the profile and is not counted as a match.
        phone: The phone number the caller states, 10 digits with no punctuation. Leave "" if not stated.
        email: The email address the caller states, exactly as given. Leave "" if not stated.
        home_zip: The 5-digit ZIP code of the billing address the caller states. Leave "" if not stated.
        id_last4: The last four characters of the caller's driver's license number, or of the business's federal EIN for a fleet customer, as stated. Leave "" if not stated.
        profile_opened_date: The date the caller says their profile was first opened with the group, as YYYY-MM-DD. Leave "" if not stated.
    """
    if not customer_id:
        return "Error: customer_id is required; look the customer up first and pass their reference number."
    rows = ctx.find("customers", customer_id=customer_id)
    if not rows:
        return f"Error: no customer {customer_id}; cannot verify."
    rec = rows[0]
    # The tool owns the comparison; the locator customer_id is deliberately not a credential.
    supplied = {"phone": phone, "email": email, "home_zip": home_zip,
                "id_last4": id_last4, "profile_opened_date": profile_opened_date}
    matched = sum(1 for field, value in supplied.items() if value and str(rec.get(field)) == str(value))
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
    return (f"Identity verified for {customer_id} ({matched} detail(s) matched)." if verified
            else f"Identity NOT verified for {customer_id} (only {matched} of the required 2 details matched). Ask the caller for another detail on file and try again.")


@tool(owner="agent", rw="write")
def transfer_to_human_agent(ctx: ToolContext, customer_id: str, reason: str) -> str:
    """Hand the customer over to a human representative of Kessler Automotive Group and record the handoff with its reason. Use POLICY_NOT_COVERED when no published policy lets you resolve what the customer is asking for; use CUSTOMER_REQUESTED when the customer has explicitly asked to speak with a person 2 times.

    Args:
        customer_id: The customer reference number read from the customer profile lookup; the profile must exist.
        reason: Why the customer is being handed over; exactly one of POLICY_NOT_COVERED (no policy resolves the request) or CUSTOMER_REQUESTED (the customer has asked for a human representative 2 times). Never free text.
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


@tool(owner="agent", rw="read")
def find_stores(ctx: ToolContext, store_id: str = "") -> str:
    """Look up the dealership stores of the group: each store's code, trading name, the manufacturer franchise it holds, its state and its city. Use it to learn which store wrote a repair order, sold a product or issued a loaner, and which store code applies to store-specific schedules. Every criterion is optional; supply whichever reference numbers are known. Returns every matching record, or a short notice when nothing matches.

    Args:
        store_id: The reference number of the dealership store. Leave "" if unknown.
    """
    match = {k: v for k, v in {"store_id": store_id}.items() if v}
    rows = ctx.find("stores", **match)
    return str(rows) if rows else f"No stores records found for {match}."


@tool(owner="agent", rw="read")
def find_vehicles(ctx: ToolContext, vehicle_id: str = "", customer_id: str = "") -> str:
    """Look up vehicle records: VIN, model year, make, model and trim, condition class when sold, in-service date, original MSRP, registered use and title brand, together with the owner or buyer the vehicle is on file for. Every criterion is optional; supply whichever reference numbers are known. Returns every matching record, or a short notice when nothing matches.

    Args:
        vehicle_id: The reference number of the vehicle (one per VIN). Leave "" if unknown.
        customer_id: The customer reference number on the profile. Leave "" if unknown.
    """
    match = {k: v for k, v in {"vehicle_id": vehicle_id, "customer_id": customer_id}.items() if v}
    rows = ctx.find("vehicles", **match)
    return str(rows) if rows else f"No vehicles records found for {match}."


@tool(owner="agent", rw="read")
def find_verification_log(ctx: ToolContext, verification_id: str = "", customer_id: str = "") -> str:
    """Look up the recorded outcome of identity verification for a customer: whether the caller has been verified and when the latest attempt was made. Every criterion is optional; supply whichever reference numbers are known. Returns every matching record, or a short notice when nothing matches.

    Args:
        verification_id: The reference number of the identity verification record. Leave "" if unknown.
        customer_id: The customer reference number on the profile. Leave "" if unknown.
    """
    match = {k: v for k, v in {"verification_id": verification_id, "customer_id": customer_id}.items() if v}
    rows = ctx.find("verification_log", **match)
    return str(rows) if rows else f"No verification log records found for {match}."


@tool(owner="agent", rw="read")
def find_handoff_log(ctx: ToolContext, handoff_id: str = "", customer_id: str = "") -> str:
    """Look up the record of handoffs to a human representative for a customer, with the reason given and the moment of the handoff. Every criterion is optional; supply whichever reference numbers are known. Returns every matching record, or a short notice when nothing matches.

    Args:
        handoff_id: The reference number of the handoff record. Leave "" if unknown.
        customer_id: The customer reference number on the profile. Leave "" if unknown.
    """
    match = {k: v for k, v in {"handoff_id": handoff_id, "customer_id": customer_id}.items() if v}
    rows = ctx.find("handoff_log", **match)
    return str(rows) if rows else f"No handoff log records found for {match}."


@tool(owner="agent", rw="read")
def find_purchase_deals(ctx: ToolContext, purchase_deal_id: str = "", customer_id: str = "", store_id: str = "", vehicle_id: str = "") -> str:
    """Look up vehicle purchase deals: deal number and deal type, status, the vehicle and selling store, reservation and hold dates, contract and delivery dates, cash price, trade-in allowance and payoff, financing arrangement and lender, delivery method and distance, odometer at delivery, title application date, deposit held and balance due. Every criterion is optional; supply whichever reference numbers are known. Returns every matching record, or a short notice when nothing matches.

    Args:
        purchase_deal_id: The reference number of the vehicle purchase deal. Leave "" if unknown.
        customer_id: The customer reference number on the profile. Leave "" if unknown.
        store_id: The reference number of the dealership store. Leave "" if unknown.
        vehicle_id: The reference number of the vehicle (one per VIN). Leave "" if unknown.
    """
    match = {k: v for k, v in {"purchase_deal_id": purchase_deal_id, "customer_id": customer_id, "store_id": store_id, "vehicle_id": vehicle_id}.items() if v}
    rows = ctx.find("purchase_deals", **match)
    return str(rows) if rows else f"No purchase deals records found for {match}."


@tool(owner="agent", rw="read")
def find_purchase_transactions(ctx: ToolContext, purchase_txn_id: str = "", purchase_deal_id: str = "", customer_id: str = "", source_txn_id: str = "") -> str:
    """Look up the money history of vehicle purchase deals: deposits received, applied, refunded or forfeited, charges posted and reversed (price, fees, taxes, negative equity, late and returned-payment fees, exchange charges), payments, returned payments and refunds, each with its date, amount, charge code, payment method and the original transaction it acts on. Every criterion is optional; supply whichever reference numbers are known. Returns every matching record, or a short notice when nothing matches.

    Args:
        purchase_txn_id: The reference number of the deal money transaction. Leave "" if unknown.
        purchase_deal_id: The reference number of the vehicle purchase deal. Leave "" if unknown.
        customer_id: The customer reference number on the profile. Leave "" if unknown.
        source_txn_id: The reference number of the original deal transaction that this entry applies, refunds, forfeits, returns or reverses. Leave "" if unknown.
    """
    match = {k: v for k, v in {"purchase_txn_id": purchase_txn_id, "purchase_deal_id": purchase_deal_id, "customer_id": customer_id, "source_txn_id": source_txn_id}.items() if v}
    rows = ctx.find("purchase_transactions", **match)
    return str(rows) if rows else f"No purchase transactions records found for {match}."


@tool(owner="agent", rw="read")
def find_purchase_cancellation_requests(ctx: ToolContext, purchase_cancel_request_id: str = "", customer_id: str = "", purchase_deal_id: str = "") -> str:
    """Look up the signed requests buyers have made to cancel a reservation, cancel an undelivered deal or return a delivered vehicle under the exchange policy, with the request date, the odometer stated and the processing status. Every criterion is optional; supply whichever reference numbers are known. Returns every matching record, or a short notice when nothing matches.

    Args:
        purchase_cancel_request_id: The reference number of the buyer's cancellation or exchange-return request. Leave "" if unknown.
        customer_id: The customer reference number on the profile. Leave "" if unknown.
        purchase_deal_id: The reference number of the vehicle purchase deal. Leave "" if unknown.
    """
    match = {k: v for k, v in {"purchase_cancel_request_id": purchase_cancel_request_id, "customer_id": customer_id, "purchase_deal_id": purchase_deal_id}.items() if v}
    rows = ctx.find("purchase_cancellation_requests", **match)
    return str(rows) if rows else f"No purchase cancellation requests records found for {match}."


@tool(owner="agent", rw="read")
def find_service_accounts(ctx: ToolContext, service_account_id: str = "", customer_id: str = "", home_store_id: str = "") -> str:
    """Look up service accounts: account number and tier, status, home store, opening and closing dates, credit limit, the balance currently owed and the Owner Rewards points available. Every criterion is optional; supply whichever reference numbers are known. Returns every matching record, or a short notice when nothing matches.

    Args:
        service_account_id: The reference number of the service account. Leave "" if unknown.
        customer_id: The customer reference number on the profile. Leave "" if unknown.
        home_store_id: The reference number of the store where the service account was opened. Leave "" if unknown.
    """
    match = {k: v for k, v in {"service_account_id": service_account_id, "customer_id": customer_id, "home_store_id": home_store_id}.items() if v}
    rows = ctx.find("service_accounts", **match)
    return str(rows) if rows else f"No service accounts records found for {match}."


@tool(owner="agent", rw="read")
def find_service_ro_lines(ctx: ToolContext, service_line_id: str = "", service_account_id: str = "", customer_id: str = "", store_id: str = "", vehicle_id: str = "", source_line_id: str = "") -> str:
    """Look up the repair order history of a service account: diagnostic, labor and parts charges by concern line, shop fees, credits, payments, returned payments, late fees and Owner Rewards points earned, redeemed or expired, each with its repair order number, date, hours, rates, amounts and the original line it acts on. Every criterion is optional; supply whichever reference numbers are known. Returns every matching record, or a short notice when nothing matches.

    Args:
        service_line_id: The reference number of the repair order ledger line. Leave "" if unknown.
        service_account_id: The reference number of the service account. Leave "" if unknown.
        customer_id: The customer reference number on the profile. Leave "" if unknown.
        store_id: The reference number of the dealership store. Leave "" if unknown.
        vehicle_id: The reference number of the vehicle (one per VIN). Leave "" if unknown.
        source_line_id: The reference number of the original repair order line that this entry credits or takes back. Leave "" if unknown.
    """
    match = {k: v for k, v in {"service_line_id": service_line_id, "service_account_id": service_account_id, "customer_id": customer_id, "store_id": store_id, "vehicle_id": vehicle_id, "source_line_id": source_line_id}.items() if v}
    rows = ctx.find("service_ro_lines", **match)
    return str(rows) if rows else f"No service ro lines records found for {match}."


@tool(owner="agent", rw="read")
def find_service_repair_authorizations(ctx: ToolContext, service_auth_id: str = "", customer_id: str = "", service_account_id: str = "") -> str:
    """Look up customers' decisions on written repair estimates: the repair order and concern line, the estimate amount, whether the work was authorized or declined, and the date of the decision. Every criterion is optional; supply whichever reference numbers are known. Returns every matching record, or a short notice when nothing matches.

    Args:
        service_auth_id: The reference number of the customer's decision on a repair estimate. Leave "" if unknown.
        customer_id: The customer reference number on the profile. Leave "" if unknown.
        service_account_id: The reference number of the service account. Leave "" if unknown.
    """
    match = {k: v for k, v in {"service_auth_id": service_auth_id, "customer_id": customer_id, "service_account_id": service_account_id}.items() if v}
    rows = ctx.find("service_repair_authorizations", **match)
    return str(rows) if rows else f"No service repair authorizations records found for {match}."


@tool(owner="agent", rw="read")
def find_maintenance_plans(ctx: ToolContext, maintenance_plan_id: str = "", customer_id: str = "", vehicle_id: str = "", selling_store_id: str = "", purchase_deal_id: str = "") -> str:
    """Look up Kessler Care prepaid maintenance plans: plan number and plan name, status, covered vehicle, selling store and deal, sale and expiration dates, odometer at sale and expiration odometer, price paid, financing and lender, visits remaining and any refund due. Every criterion is optional; supply whichever reference numbers are known. Returns every matching record, or a short notice when nothing matches.

    Args:
        maintenance_plan_id: The reference number of the prepaid maintenance plan. Leave "" if unknown.
        customer_id: The customer reference number on the profile. Leave "" if unknown.
        vehicle_id: The reference number of the vehicle (one per VIN). Leave "" if unknown.
        selling_store_id: The reference number of the store that sold the product. Leave "" if unknown.
        purchase_deal_id: The reference number of the vehicle purchase deal. Leave "" if unknown.
    """
    match = {k: v for k, v in {"maintenance_plan_id": maintenance_plan_id, "customer_id": customer_id, "vehicle_id": vehicle_id, "selling_store_id": selling_store_id, "purchase_deal_id": purchase_deal_id}.items() if v}
    rows = ctx.find("maintenance_plans", **match)
    return str(rows) if rows else f"No maintenance plans records found for {match}."


@tool(owner="agent", rw="read")
def find_maintenance_plan_ledger(ctx: ToolContext, maintenance_entry_id: str = "", maintenance_plan_id: str = "", customer_id: str = "", store_id: str = "", source_entry_id: str = "") -> str:
    """Look up the history of a maintenance plan: visits loaded, visits redeemed (with visit number, repair order, store and odometer), reinstated, expired or cancelled, and cancellation refunds computed and paid. Every criterion is optional; supply whichever reference numbers are known. Returns every matching record, or a short notice when nothing matches.

    Args:
        maintenance_entry_id: The reference number of the maintenance plan ledger entry. Leave "" if unknown.
        maintenance_plan_id: The reference number of the prepaid maintenance plan. Leave "" if unknown.
        customer_id: The customer reference number on the profile. Leave "" if unknown.
        store_id: The reference number of the dealership store. Leave "" if unknown.
        source_entry_id: The reference number of the original entry this entry reverses or pays. Leave "" if unknown.
    """
    match = {k: v for k, v in {"maintenance_entry_id": maintenance_entry_id, "maintenance_plan_id": maintenance_plan_id, "customer_id": customer_id, "store_id": store_id, "source_entry_id": source_entry_id}.items() if v}
    rows = ctx.find("maintenance_plan_ledger", **match)
    return str(rows) if rows else f"No maintenance plan ledger records found for {match}."


@tool(owner="agent", rw="read")
def find_maintenance_cancellation_requests(ctx: ToolContext, maintenance_cancel_request_id: str = "", customer_id: str = "", maintenance_plan_id: str = "") -> str:
    """Look up the signed requests plan holders have made to cancel a maintenance plan, with the reason, the request date, the certified odometer and the processing status. Every criterion is optional; supply whichever reference numbers are known. Returns every matching record, or a short notice when nothing matches.

    Args:
        maintenance_cancel_request_id: The reference number of the plan holder's cancellation request. Leave "" if unknown.
        customer_id: The customer reference number on the profile. Leave "" if unknown.
        maintenance_plan_id: The reference number of the prepaid maintenance plan. Leave "" if unknown.
    """
    match = {k: v for k, v in {"maintenance_cancel_request_id": maintenance_cancel_request_id, "customer_id": customer_id, "maintenance_plan_id": maintenance_plan_id}.items() if v}
    rows = ctx.find("maintenance_cancellation_requests", **match)
    return str(rows) if rows else f"No maintenance cancellation requests records found for {match}."


@tool(owner="agent", rw="read")
def find_vsc_contracts(ctx: ToolContext, vsc_contract_id: str = "", customer_id: str = "", vehicle_id: str = "", purchase_deal_id: str = "", selling_store_id: str = "") -> str:
    """Look up Kessler Shield vehicle service contracts: contract number and coverage level, status, covered vehicle, selling store and deal, sale date, term start, term months and miles, expiration date and odometer, deductible, price, financing and lender, claims paid to date and any refund due. Every criterion is optional; supply whichever reference numbers are known. Returns every matching record, or a short notice when nothing matches.

    Args:
        vsc_contract_id: The reference number of the vehicle service contract. Leave "" if unknown.
        customer_id: The customer reference number on the profile. Leave "" if unknown.
        vehicle_id: The reference number of the vehicle (one per VIN). Leave "" if unknown.
        purchase_deal_id: The reference number of the vehicle purchase deal. Leave "" if unknown.
        selling_store_id: The reference number of the store that sold the product. Leave "" if unknown.
    """
    match = {k: v for k, v in {"vsc_contract_id": vsc_contract_id, "customer_id": customer_id, "vehicle_id": vehicle_id, "purchase_deal_id": purchase_deal_id, "selling_store_id": selling_store_id}.items() if v}
    rows = ctx.find("vsc_contracts", **match)
    return str(rows) if rows else f"No vsc contracts records found for {match}."


@tool(owner="agent", rw="read")
def find_vsc_ledger(ctx: ToolContext, vsc_entry_id: str = "", vsc_contract_id: str = "", customer_id: str = "", source_entry_id: str = "") -> str:
    """Look up the claim and refund history of a service contract: claim lines paid or denied (with claim number, repair order, component group, hours, labor rate paid, parts, deductible and days), reversals, and cancellation refunds computed and paid. Every criterion is optional; supply whichever reference numbers are known. Returns every matching record, or a short notice when nothing matches.

    Args:
        vsc_entry_id: The reference number of the service contract ledger entry. Leave "" if unknown.
        vsc_contract_id: The reference number of the vehicle service contract. Leave "" if unknown.
        customer_id: The customer reference number on the profile. Leave "" if unknown.
        source_entry_id: The reference number of the original entry this entry reverses or pays. Leave "" if unknown.
    """
    match = {k: v for k, v in {"vsc_entry_id": vsc_entry_id, "vsc_contract_id": vsc_contract_id, "customer_id": customer_id, "source_entry_id": source_entry_id}.items() if v}
    rows = ctx.find("vsc_ledger", **match)
    return str(rows) if rows else f"No vsc ledger records found for {match}."


@tool(owner="agent", rw="read")
def find_vsc_cancellation_requests(ctx: ToolContext, vsc_cancel_request_id: str = "", customer_id: str = "", vsc_contract_id: str = "") -> str:
    """Look up the signed requests contract holders have made to cancel a service contract, with the reason, the request date, the certified odometer and the processing status. Every criterion is optional; supply whichever reference numbers are known. Returns every matching record, or a short notice when nothing matches.

    Args:
        vsc_cancel_request_id: The reference number of the contract holder's cancellation request. Leave "" if unknown.
        customer_id: The customer reference number on the profile. Leave "" if unknown.
        vsc_contract_id: The reference number of the vehicle service contract. Leave "" if unknown.
    """
    match = {k: v for k, v in {"vsc_cancel_request_id": vsc_cancel_request_id, "customer_id": customer_id, "vsc_contract_id": vsc_contract_id}.items() if v}
    rows = ctx.find("vsc_cancellation_requests", **match)
    return str(rows) if rows else f"No vsc cancellation requests records found for {match}."


@tool(owner="agent", rw="read")
def find_gap_waivers(ctx: ToolContext, gap_waiver_id: str = "", customer_id: str = "", vehicle_id: str = "", purchase_deal_id: str = "") -> str:
    """Look up Kessler GAP waivers: waiver number and name, status, financed vehicle and deal, sale date, loan term and expiration date, price, amount financed, vehicle value basis, lienholder, loan payoff date, benefits paid and any refund due. Every criterion is optional; supply whichever reference numbers are known. Returns every matching record, or a short notice when nothing matches.

    Args:
        gap_waiver_id: The reference number of the GAP waiver. Leave "" if unknown.
        customer_id: The customer reference number on the profile. Leave "" if unknown.
        vehicle_id: The reference number of the vehicle (one per VIN). Leave "" if unknown.
        purchase_deal_id: The reference number of the vehicle purchase deal. Leave "" if unknown.
    """
    match = {k: v for k, v in {"gap_waiver_id": gap_waiver_id, "customer_id": customer_id, "vehicle_id": vehicle_id, "purchase_deal_id": purchase_deal_id}.items() if v}
    rows = ctx.find("gap_waivers", **match)
    return str(rows) if rows else f"No gap waivers records found for {match}."


@tool(owner="agent", rw="read")
def find_gap_ledger(ctx: ToolContext, gap_entry_id: str = "", gap_waiver_id: str = "", customer_id: str = "", source_entry_id: str = "") -> str:
    """Look up the claim and refund history of a GAP waiver: benefit lines paid or denied with the loss and settlement details behind them, reversals, and cancellation or termination refunds computed and paid. Every criterion is optional; supply whichever reference numbers are known. Returns every matching record, or a short notice when nothing matches.

    Args:
        gap_entry_id: The reference number of the GAP waiver ledger entry. Leave "" if unknown.
        gap_waiver_id: The reference number of the GAP waiver. Leave "" if unknown.
        customer_id: The customer reference number on the profile. Leave "" if unknown.
        source_entry_id: The reference number of the original entry this entry reverses or pays. Leave "" if unknown.
    """
    match = {k: v for k, v in {"gap_entry_id": gap_entry_id, "gap_waiver_id": gap_waiver_id, "customer_id": customer_id, "source_entry_id": source_entry_id}.items() if v}
    rows = ctx.find("gap_ledger", **match)
    return str(rows) if rows else f"No gap ledger records found for {match}."


@tool(owner="agent", rw="read")
def find_gap_cancellation_requests(ctx: ToolContext, gap_cancel_request_id: str = "", customer_id: str = "", gap_waiver_id: str = "") -> str:
    """Look up the signed requests waiver holders have made to cancel a GAP waiver, with the reason, the request date and the processing status. Every criterion is optional; supply whichever reference numbers are known. Returns every matching record, or a short notice when nothing matches.

    Args:
        gap_cancel_request_id: The reference number of the waiver holder's cancellation request. Leave "" if unknown.
        customer_id: The customer reference number on the profile. Leave "" if unknown.
        gap_waiver_id: The reference number of the GAP waiver. Leave "" if unknown.
    """
    match = {k: v for k, v in {"gap_cancel_request_id": gap_cancel_request_id, "customer_id": customer_id, "gap_waiver_id": gap_waiver_id}.items() if v}
    rows = ctx.find("gap_cancellation_requests", **match)
    return str(rows) if rows else f"No gap cancellation requests records found for {match}."


@tool(owner="agent", rw="read")
def find_warranty_coverages(ctx: ToolContext, warranty_coverage_id: str = "", customer_id: str = "", vehicle_id: str = "") -> str:
    """Look up the warranty and safety recall coverages registered on vehicles: coverage name, status, term start date and odometer, expiration date and odometer, whether the owner is the original or a later owner, and the amount paid under the coverage. Every criterion is optional; supply whichever reference numbers are known. Returns every matching record, or a short notice when nothing matches.

    Args:
        warranty_coverage_id: The reference number of the warranty or recall coverage. Leave "" if unknown.
        customer_id: The customer reference number on the profile. Leave "" if unknown.
        vehicle_id: The reference number of the vehicle (one per VIN). Leave "" if unknown.
    """
    match = {k: v for k, v in {"warranty_coverage_id": warranty_coverage_id, "customer_id": customer_id, "vehicle_id": vehicle_id}.items() if v}
    rows = ctx.find("warranty_coverages", **match)
    return str(rows) if rows else f"No warranty coverages records found for {match}."


@tool(owner="agent", rw="read")
def find_warranty_claims(ctx: ToolContext, warranty_claim_id: str = "", warranty_coverage_id: str = "", customer_id: str = "", store_id: str = "", source_claim_id: str = "") -> str:
    """Look up warranty and recall history: recall campaign notices recorded against a vehicle, claims paid or rejected (warranty repairs, recall remedies, owner reimbursements, goodwill adjustments, complimentary maintenance visits, rentals) and audit debits, with dates, repair orders, components, odometers and amounts. Every criterion is optional; supply whichever reference numbers are known. Returns every matching record, or a short notice when nothing matches.

    Args:
        warranty_claim_id: The reference number of the warranty or recall entry. Leave "" if unknown.
        warranty_coverage_id: The reference number of the warranty or recall coverage. Leave "" if unknown.
        customer_id: The customer reference number on the profile. Leave "" if unknown.
        store_id: The reference number of the dealership store. Leave "" if unknown.
        source_claim_id: The reference number of the paid claim that this entry takes back. Leave "" if unknown.
    """
    match = {k: v for k, v in {"warranty_claim_id": warranty_claim_id, "warranty_coverage_id": warranty_coverage_id, "customer_id": customer_id, "store_id": store_id, "source_claim_id": source_claim_id}.items() if v}
    rows = ctx.find("warranty_claims", **match)
    return str(rows) if rows else f"No warranty claims records found for {match}."


@tool(owner="agent", rw="read")
def find_loaner_agreements(ctx: ToolContext, loaner_agreement_id: str = "", customer_id: str = "", store_id: str = "", loaner_vehicle_id: str = "") -> str:
    """Look up loaner agreements: agreement number and program, status, issuing store and loaner unit, the repair order it supports, who pays the days and the daily allowance, out, due and return dates, extensions, odometer and fuel readings, and the balance owed. Every criterion is optional; supply whichever reference numbers are known. Returns every matching record, or a short notice when nothing matches.

    Args:
        loaner_agreement_id: The reference number of the loaner agreement. Leave "" if unknown.
        customer_id: The customer reference number on the profile. Leave "" if unknown.
        store_id: The reference number of the dealership store. Leave "" if unknown.
        loaner_vehicle_id: The reference number of the loaner unit issued. Leave "" if unknown.
    """
    match = {k: v for k, v in {"loaner_agreement_id": loaner_agreement_id, "customer_id": customer_id, "store_id": store_id, "loaner_vehicle_id": loaner_vehicle_id}.items() if v}
    rows = ctx.find("loaner_agreements", **match)
    return str(rows) if rows else f"No loaner agreements records found for {match}."


@tool(owner="agent", rw="read")
def find_loaner_charges(ctx: ToolContext, loaner_charge_id: str = "", loaner_agreement_id: str = "", customer_id: str = "", source_charge_id: str = "") -> str:
    """Look up the charges, waivers and payments on loaner agreements, each with its date, charge code, quantity, rate, amount and any toll or citation number. Every criterion is optional; supply whichever reference numbers are known. Returns every matching record, or a short notice when nothing matches.

    Args:
        loaner_charge_id: The reference number of the loaner charge or payment entry. Leave "" if unknown.
        loaner_agreement_id: The reference number of the loaner agreement. Leave "" if unknown.
        customer_id: The customer reference number on the profile. Leave "" if unknown.
        source_charge_id: The reference number of the original loaner charge this entry waives. Leave "" if unknown.
    """
    match = {k: v for k, v in {"loaner_charge_id": loaner_charge_id, "loaner_agreement_id": loaner_agreement_id, "customer_id": customer_id, "source_charge_id": source_charge_id}.items() if v}
    rows = ctx.find("loaner_charges", **match)
    return str(rows) if rows else f"No loaner charges records found for {match}."

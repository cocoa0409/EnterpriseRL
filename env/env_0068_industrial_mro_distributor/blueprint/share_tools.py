"""Shared tools for env_0068_industrial_mro_distributor (Corbett Industrial Supply, Inc.).

Every tool here is always available: one finder per record set (the customers finder doubles as
the identity entry), the caller identity verification write (passes at K = 2 matching
credentials) and the transfer-to-human write (CUSTOMER_REQUESTED after R = 2 explicit requests).
Finders encode no business policy; eligibility, status, timing and deduplication decisions stay
with the agent working from the knowledge base and the records.
"""

from erlbench import ToolContext, tool


@tool(owner="agent", rw="read")
def find_customers(ctx: ToolContext, customer_id: str = "", account_number: str = "", company_name: str = "",
                   contact_name: str = "", phone: str = "", email: str = "") -> str:
    """Look up a Corbett Industrial Supply customer profile to establish which business account this call is about.

    Search by the customer reference number, or by what a caller can naturally tell you: the Corbett
    account number printed on invoices, the company name, the contact's name, the account's phone
    number or email address. Every criterion is optional; give whichever you have. Small differences
    in spacing, punctuation or capitalisation do not prevent a match. The profile returned shows the
    company and contact names, account number, phone, email, last four digits of the federal EIN,
    bill-to ZIP code, the date the customer relationship began and the industry segment. Finding a
    profile does not verify the caller's identity.

    Args:
        customer_id: Reference number — the customer reference number; leave "" if unknown.
        account_number: The Corbett account number as the caller states it (format C-NNNNNN); leave "" if not given.
        company_name: The company's legal name as the caller states it; leave "" if not given.
        contact_name: The name of the purchasing or accounts-payable contact as the caller states it; leave "" if not given.
        phone: The account's phone number as the caller states it (10 digits); leave "" if not given.
        email: The account's email address as the caller states it; leave "" if not given.
    """
    match = {k: v for k, v in {"customer_id": customer_id, "account_number": account_number,
                               "company_name": company_name, "contact_name": contact_name,
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
def verify_caller_identity(ctx: ToolContext, customer_id: str, account_number: str = "", phone: str = "",
                           email: str = "", ein_last4: str = "", billing_zip: str = "") -> str:
    """Verify that the caller is authorized on a customer account and record the result; verification must pass before any account record is discussed or any business is transacted.

    This tool performs the comparison itself: each credential the caller states is checked against
    the customer profile, and verification passes only when at least 2 of them match. The customer
    reference number only identifies which profile to check against and never counts as a match.
    Callers usually know only some credentials, so pass exactly the values the caller gave, as given,
    and leave the others empty. The outcome is recorded; if a first attempt fails and a later attempt
    with more credentials passes, the account stays verified.

    Args:
        customer_id: Reference number — the customer reference number read from the customer profile lookup. Required; used only to select the profile and not counted as a match.
        account_number: The Corbett account number the caller states (format C-NNNNNN); leave "" if not stated.
        phone: The account's 10-digit phone number the caller states, digits only; leave "" if not stated.
        email: The account's email address the caller states; leave "" if not stated.
        ein_last4: The last four digits of the company's federal EIN the caller states; leave "" if not stated.
        billing_zip: The 5-digit ZIP code of the bill-to address the caller states; leave "" if not stated.
    """
    if not customer_id:
        return "Error: customer_id is required; look the customer up first and pass their reference number."
    rows = ctx.find("customers", customer_id=customer_id)
    if not rows:
        return f"Error: no customer {customer_id}; cannot verify."
    rec = rows[0]
    # The tool owns the comparison; the locator customer_id is never part of `supplied`.
    supplied = {"account_number": account_number, "phone": phone, "email": email,
                "ein_last4": ein_last4, "billing_zip": billing_zip}
    matched = sum(1 for field, value in supplied.items() if value and str(rec.get(field)) == str(value))
    verified = matched >= 2
    rid = ctx.make_id("ver_", customer_id)
    # Store only the reproducible boolean; upsert and never downgrade a prior pass.
    prior = ctx.find("identity_verifications", verification_id=rid)
    verified = verified or bool(prior and prior[0].get("verified"))
    if prior:
        ctx.update("identity_verifications", rid, verified=verified, verified_at=ctx.now())
    else:
        ctx.create("identity_verifications", rid, verification_id=rid, customer_id=customer_id,
                   verified=verified, verified_at=ctx.now())
    return (f"Identity verified for {customer_id} ({matched} credential(s) matched)." if verified
            else f"Identity NOT verified for {customer_id} (only {matched} of the required 2 credentials matched). "
                 "Ask the caller for another credential on file and try again.")


@tool(owner="agent", rw="write")
def transfer_to_human_agent(ctx: ToolContext, customer_id: str, reason: str) -> str:
    """Hand the customer over to a human Corbett representative and record the handoff with its reason.

    Use it in one of two situations only: no Corbett policy can resolve what the customer needs, or
    the customer has explicitly asked to speak with a person at least 2 times during the call.

    Args:
        customer_id: Reference number — the customer reference number read from the customer profile lookup (the profile must exist).
        reason: Exactly one of two values, never free text. POLICY_NOT_COVERED — no Corbett policy offers a way to resolve the request; CUSTOMER_REQUESTED — the customer has explicitly asked for a human representative at least 2 times.
    """
    allowed = {"POLICY_NOT_COVERED", "CUSTOMER_REQUESTED"}
    if reason not in allowed:
        return f"Error: unknown handoff reason '{reason}'. Valid: {', '.join(sorted(allowed))}."
    if not ctx.find("customers", customer_id=customer_id):
        return f"Error: no customer {customer_id}; cannot record the handoff."
    rid = ctx.make_id("hof_", customer_id, reason)
    ctx.create("human_handoffs", rid, handoff_id=rid, customer_id=customer_id,
               reason=reason, created_at=ctx.now())
    return f"Handoff to a human representative recorded for {customer_id} ({reason})."


@tool(owner="agent", rw="read")
def find_identity_verifications(ctx: ToolContext, verification_id: str = "", customer_id: str = "") -> str:
    """Look up the outcome recorded for a caller's identity verification on a customer account. Every criterion is optional: supply whichever reference numbers you hold, and all records carrying all of them are returned; when nothing matches, a short notice says so.

    Args:
        verification_id: Reference number — the reference number of an identity verification record; leave "" if unknown.
        customer_id: Reference number — the customer reference number of the account holder; leave "" if unknown.
    """
    match = {k: v for k, v in {"verification_id": verification_id, "customer_id": customer_id}.items() if v}
    rows = ctx.find("identity_verifications", **match)
    return str(rows) if rows else f"No identity_verifications records for {match}."


@tool(owner="agent", rw="read")
def find_human_handoffs(ctx: ToolContext, handoff_id: str = "", customer_id: str = "") -> str:
    """Look up handoffs of a customer to a human representative and the reason recorded for each. Every criterion is optional: supply whichever reference numbers you hold, and all records carrying all of them are returned; when nothing matches, a short notice says so.

    Args:
        handoff_id: Reference number — the reference number of a handoff to a human representative; leave "" if unknown.
        customer_id: Reference number — the customer reference number of the account holder; leave "" if unknown.
    """
    match = {k: v for k, v in {"handoff_id": handoff_id, "customer_id": customer_id}.items() if v}
    rows = ctx.find("human_handoffs", **match)
    return str(rows) if rows else f"No human_handoffs records for {match}."


@tool(owner="agent", rw="read")
def find_credit_accounts(ctx: ToolContext, credit_account_id: str = "", customer_id: str = "") -> str:
    """Look up Commercial Credit Account records: the terms tier, status, credit limit, open receivable balance, invoice delivery and billing cycle, hold reason, last credit review date and opening or closing dates. Every criterion is optional: supply whichever reference numbers you hold, and all records carrying all of them are returned; when nothing matches, a short notice says so.

    Args:
        credit_account_id: Reference number — the reference number of the Commercial Credit Account; leave "" if unknown.
        customer_id: Reference number — the customer reference number of the account holder; leave "" if unknown.
    """
    match = {k: v for k, v in {"credit_account_id": credit_account_id, "customer_id": customer_id}.items() if v}
    rows = ctx.find("credit_accounts", **match)
    return str(rows) if rows else f"No credit_accounts records for {match}."


@tool(owner="agent", rw="read")
def find_credit_transactions(ctx: ToolContext, credit_txn_id: str = "", credit_account_id: str = "", customer_id: str = "") -> str:
    """Look up the receivable history of a Commercial Credit Account: invoices with their dates, due dates and amount breakdown, payments and how they were applied, cash discounts, returned payments, account charges, credit memos, refunds and small-balance write-offs. Every criterion is optional: supply whichever reference numbers you hold, and all records carrying all of them are returned; when nothing matches, a short notice says so.

    Args:
        credit_txn_id: Reference number — the reference number of one receivable ledger entry (invoice, payment, discount, charge, credit memo, refund or write-off); leave "" if unknown.
        credit_account_id: Reference number — the reference number of the Commercial Credit Account; leave "" if unknown.
        customer_id: Reference number — the customer reference number of the account holder; leave "" if unknown.
    """
    match = {k: v for k, v in {"credit_txn_id": credit_txn_id, "credit_account_id": credit_account_id, "customer_id": customer_id}.items() if v}
    rows = ctx.find("credit_transactions", **match)
    return str(rows) if rows else f"No credit_transactions records for {match}."


@tool(owner="agent", rw="read")
def find_credit_disputes(ctx: ToolContext, credit_dispute_id: str = "", credit_account_id: str = "", customer_id: str = "") -> str:
    """Look up invoice disputes: the dispute reference, the invoice disputed, the reason, the amount and the outcome of each dispute. Every criterion is optional: supply whichever reference numbers you hold, and all records carrying all of them are returned; when nothing matches, a short notice says so.

    Args:
        credit_dispute_id: Reference number — the reference number of one invoice dispute entry; leave "" if unknown.
        credit_account_id: Reference number — the reference number of the Commercial Credit Account; leave "" if unknown.
        customer_id: Reference number — the customer reference number of the account holder; leave "" if unknown.
    """
    match = {k: v for k, v in {"credit_dispute_id": credit_dispute_id, "credit_account_id": credit_account_id, "customer_id": customer_id}.items() if v}
    rows = ctx.find("credit_disputes", **match)
    return str(rows) if rows else f"No credit_disputes records for {match}."


@tool(owner="agent", rw="read")
def find_credit_limit_reviews(ctx: ToolContext, credit_review_id: str = "", credit_account_id: str = "", customer_id: str = "") -> str:
    """Look up credit limit requests and their decisions: the amount asked for, permanent or temporary, the decision, the limit granted and any expiry date. Every criterion is optional: supply whichever reference numbers you hold, and all records carrying all of them are returned; when nothing matches, a short notice says so.

    Args:
        credit_review_id: Reference number — the reference number of one credit limit request or decision entry; leave "" if unknown.
        credit_account_id: Reference number — the reference number of the Commercial Credit Account; leave "" if unknown.
        customer_id: Reference number — the customer reference number of the account holder; leave "" if unknown.
    """
    match = {k: v for k, v in {"credit_review_id": credit_review_id, "credit_account_id": credit_account_id, "customer_id": customer_id}.items() if v}
    rows = ctx.find("credit_limit_reviews", **match)
    return str(rows) if rows else f"No credit_limit_reviews records for {match}."


@tool(owner="agent", rw="read")
def find_pricing_agreements(ctx: ToolContext, pricing_agreement_id: str = "", customer_id: str = "") -> str:
    """Look up Contract Pricing Agreements: the tier, status, agreement number, proposal, effective and expiration dates, annual commitment, unpaid rebate balance, renewal setting and any termination notice date. Every criterion is optional: supply whichever reference numbers you hold, and all records carrying all of them are returned; when nothing matches, a short notice says so.

    Args:
        pricing_agreement_id: Reference number — the reference number of the Contract Pricing Agreement; leave "" if unknown.
        customer_id: Reference number — the customer reference number of the account holder; leave "" if unknown.
    """
    match = {k: v for k, v in {"pricing_agreement_id": pricing_agreement_id, "customer_id": customer_id}.items() if v}
    rows = ctx.find("pricing_agreements", **match)
    return str(rows) if rows else f"No pricing_agreements records for {match}."


@tool(owner="agent", rw="read")
def find_pricing_items(ctx: ToolContext, contract_item_id: str = "", pricing_agreement_id: str = "", customer_id: str = "") -> str:
    """Look up the contract item price history of an agreement: item additions, price changes (escalations, supplier cost changes, competitive matches) and removals, with list price, supplier cost, prior and new contract price, quote and notice dates and effective dates. Every criterion is optional: supply whichever reference numbers you hold, and all records carrying all of them are returned; when nothing matches, a short notice says so.

    Args:
        contract_item_id: Reference number — the reference number of one contract item price entry; leave "" if unknown.
        pricing_agreement_id: Reference number — the reference number of the Contract Pricing Agreement; leave "" if unknown.
        customer_id: Reference number — the customer reference number of the account holder; leave "" if unknown.
    """
    match = {k: v for k, v in {"contract_item_id": contract_item_id, "pricing_agreement_id": pricing_agreement_id, "customer_id": customer_id}.items() if v}
    rows = ctx.find("pricing_items", **match)
    return str(rows) if rows else f"No pricing_items records for {match}."


@tool(owner="agent", rw="read")
def find_pricing_claims(ctx: ToolContext, price_claim_id: str = "", pricing_agreement_id: str = "", customer_id: str = "") -> str:
    """Look up contract price claims: the claim reference, the invoice and item claimed, quantities, billed and contract unit prices, the claim amount and the decision. Every criterion is optional: supply whichever reference numbers you hold, and all records carrying all of them are returned; when nothing matches, a short notice says so.

    Args:
        price_claim_id: Reference number — the reference number of one contract price claim entry; leave "" if unknown.
        pricing_agreement_id: Reference number — the reference number of the Contract Pricing Agreement; leave "" if unknown.
        customer_id: Reference number — the customer reference number of the account holder; leave "" if unknown.
    """
    match = {k: v for k, v in {"price_claim_id": price_claim_id, "pricing_agreement_id": pricing_agreement_id, "customer_id": customer_id}.items() if v}
    rows = ctx.find("pricing_claims", **match)
    return str(rows) if rows else f"No pricing_claims records for {match}."


@tool(owner="agent", rw="read")
def find_pricing_rebates(ctx: ToolContext, rebate_line_id: str = "", pricing_agreement_id: str = "", customer_id: str = "") -> str:
    """Look up volume rebate history: quarterly accruals with qualifying spend and rate, payouts with their method, and clawbacks or forfeitures. Every criterion is optional: supply whichever reference numbers you hold, and all records carrying all of them are returned; when nothing matches, a short notice says so.

    Args:
        rebate_line_id: Reference number — the reference number of one volume rebate entry; leave "" if unknown.
        pricing_agreement_id: Reference number — the reference number of the Contract Pricing Agreement; leave "" if unknown.
        customer_id: Reference number — the customer reference number of the account holder; leave "" if unknown.
    """
    match = {k: v for k, v in {"rebate_line_id": rebate_line_id, "pricing_agreement_id": pricing_agreement_id, "customer_id": customer_id}.items() if v}
    rows = ctx.find("pricing_rebates", **match)
    return str(rows) if rows else f"No pricing_rebates records for {match}."


@tool(owner="agent", rw="read")
def find_ship_to_accounts(ctx: ToolContext, ship_to_id: str = "", customer_id: str = "") -> str:
    """Look up Ship-To Fulfillment Accounts (delivery locations): the service level, status, ship-to number, site name, delivery ZIP code, opening and closing dates, last order date and open backorder value. Every criterion is optional: supply whichever reference numbers you hold, and all records carrying all of them are returned; when nothing matches, a short notice says so.

    Args:
        ship_to_id: Reference number — the reference number of a Ship-To Fulfillment Account (one delivery location); leave "" if unknown.
        customer_id: Reference number — the customer reference number of the account holder; leave "" if unknown.
    """
    match = {k: v for k, v in {"ship_to_id": ship_to_id, "customer_id": customer_id}.items() if v}
    rows = ctx.find("ship_to_accounts", **match)
    return str(rows) if rows else f"No ship_to_accounts records for {match}."


@tool(owner="agent", rw="read")
def find_order_lines(ctx: ToolContext, order_line_id: str = "", ship_to_id: str = "", customer_id: str = "") -> str:
    """Look up order history for a ship-to: booked lines, shipments with ship and delivery dates and prices, backorders with promise dates, backorder fills and cancellations, line cancellations and every freight or service fee billed on an order. Every criterion is optional: supply whichever reference numbers you hold, and all records carrying all of them are returned; when nothing matches, a short notice says so.

    Args:
        order_line_id: Reference number — the reference number of one order history entry (booking, shipment, backorder, cancellation or fee); leave "" if unknown.
        ship_to_id: Reference number — the reference number of a Ship-To Fulfillment Account (one delivery location); leave "" if unknown.
        customer_id: Reference number — the customer reference number of the account holder; leave "" if unknown.
    """
    match = {k: v for k, v in {"order_line_id": order_line_id, "ship_to_id": ship_to_id, "customer_id": customer_id}.items() if v}
    rows = ctx.find("order_lines", **match)
    return str(rows) if rows else f"No order_lines records for {match}."


@tool(owner="agent", rw="read")
def find_order_returns(ctx: ToolContext, return_line_id: str = "", ship_to_id: str = "", customer_id: str = "") -> str:
    """Look up returns: RMAs issued, declined requests, goods received with inspection condition, restocking and label fees and credit, and RMAs closed without credit. Every criterion is optional: supply whichever reference numbers you hold, and all records carrying all of them are returned; when nothing matches, a short notice says so.

    Args:
        return_line_id: Reference number — the reference number of one return entry; leave "" if unknown.
        ship_to_id: Reference number — the reference number of a Ship-To Fulfillment Account (one delivery location); leave "" if unknown.
        customer_id: Reference number — the customer reference number of the account holder; leave "" if unknown.
    """
    match = {k: v for k, v in {"return_line_id": return_line_id, "ship_to_id": ship_to_id, "customer_id": customer_id}.items() if v}
    rows = ctx.find("order_returns", **match)
    return str(rows) if rows else f"No order_returns records for {match}."


@tool(owner="agent", rw="read")
def find_vmi_programs(ctx: ToolContext, vmi_program_id: str = "", customer_id: str = "", ship_to_id: str = "") -> str:
    """Look up StockSmart Vendor-Managed Inventory Programs: the tier, status, program number, ship-to served, enrollment, go-live and closing dates, pause details, termination notice date and consigned stock value. Every criterion is optional: supply whichever reference numbers you hold, and all records carrying all of them are returned; when nothing matches, a short notice says so.

    Args:
        vmi_program_id: Reference number — the reference number of a StockSmart Vendor-Managed Inventory Program; leave "" if unknown.
        customer_id: Reference number — the customer reference number of the account holder; leave "" if unknown.
        ship_to_id: Reference number — the reference number of a Ship-To Fulfillment Account (one delivery location); leave "" if unknown.
    """
    match = {k: v for k, v in {"vmi_program_id": vmi_program_id, "customer_id": customer_id, "ship_to_id": ship_to_id}.items() if v}
    rows = ctx.find("vmi_programs", **match)
    return str(rows) if rows else f"No vmi_programs records for {match}."


@tool(owner="agent", rw="read")
def find_vmi_activity(ctx: ToolContext, vmi_activity_id: str = "", vmi_program_id: str = "", customer_id: str = "") -> str:
    """Look up StockSmart program activity: service visits and self-scan orders, bin replenishments and their billing, consigned stock placed, consumed, short or withdrawn, monthly consumption bills, program fees, pauses and buyback billing. Every criterion is optional: supply whichever reference numbers you hold, and all records carrying all of them are returned; when nothing matches, a short notice says so.

    Args:
        vmi_activity_id: Reference number — the reference number of one StockSmart program activity entry; leave "" if unknown.
        vmi_program_id: Reference number — the reference number of a StockSmart Vendor-Managed Inventory Program; leave "" if unknown.
        customer_id: Reference number — the customer reference number of the account holder; leave "" if unknown.
    """
    match = {k: v for k, v in {"vmi_activity_id": vmi_activity_id, "vmi_program_id": vmi_program_id, "customer_id": customer_id}.items() if v}
    rows = ctx.find("vmi_activity", **match)
    return str(rows) if rows else f"No vmi_activity records for {match}."


@tool(owner="agent", rw="read")
def find_vmi_bins(ctx: ToolContext, vmi_bin_id: str = "", vmi_program_id: str = "", customer_id: str = "") -> str:
    """Look up StockSmart bin history: bins added, par level changes and bin removals, with the item, special-stock, critical and consigned flags and min and max levels. Every criterion is optional: supply whichever reference numbers you hold, and all records carrying all of them are returned; when nothing matches, a short notice says so.

    Args:
        vmi_bin_id: Reference number — the reference number of one StockSmart bin change entry; leave "" if unknown.
        vmi_program_id: Reference number — the reference number of a StockSmart Vendor-Managed Inventory Program; leave "" if unknown.
        customer_id: Reference number — the customer reference number of the account holder; leave "" if unknown.
    """
    match = {k: v for k, v in {"vmi_bin_id": vmi_bin_id, "vmi_program_id": vmi_program_id, "customer_id": customer_id}.items() if v}
    rows = ctx.find("vmi_bins", **match)
    return str(rows) if rows else f"No vmi_bins records for {match}."


@tool(owner="agent", rw="read")
def find_vending_machines(ctx: ToolContext, vending_machine_id: str = "", customer_id: str = "", ship_to_id: str = "") -> str:
    """Look up VendPoint machine placements: the model tier, status, serial number, ship-to, request, installation, lock and removal dates, removal notice date, network connection and stock value loaded. Every criterion is optional: supply whichever reference numbers you hold, and all records carrying all of them are returned; when nothing matches, a short notice says so.

    Args:
        vending_machine_id: Reference number — the reference number of a VendPoint machine placement; leave "" if unknown.
        customer_id: Reference number — the customer reference number of the account holder; leave "" if unknown.
        ship_to_id: Reference number — the reference number of a Ship-To Fulfillment Account (one delivery location); leave "" if unknown.
    """
    match = {k: v for k, v in {"vending_machine_id": vending_machine_id, "customer_id": customer_id, "ship_to_id": ship_to_id}.items() if v}
    rows = ctx.find("vending_machines", **match)
    return str(rows) if rows else f"No vending_machines records for {match}."


@tool(owner="agent", rw="read")
def find_vending_transactions(ctx: ToolContext, vending_txn_id: str = "", vending_machine_id: str = "", customer_id: str = "", ship_to_id: str = "") -> str:
    """Look up VendPoint machine transactions: restocks, vends with badge and cost center, returns to the machine, vend error credits, shrink, stock withdrawals, monthly usage bills, fees and relocations. Every criterion is optional: supply whichever reference numbers you hold, and all records carrying all of them are returned; when nothing matches, a short notice says so.

    Args:
        vending_txn_id: Reference number — the reference number of one VendPoint machine transaction entry; leave "" if unknown.
        vending_machine_id: Reference number — the reference number of a VendPoint machine placement; leave "" if unknown.
        customer_id: Reference number — the customer reference number of the account holder; leave "" if unknown.
        ship_to_id: Reference number — the reference number of a Ship-To Fulfillment Account (one delivery location); leave "" if unknown.
    """
    match = {k: v for k, v in {"vending_txn_id": vending_txn_id, "vending_machine_id": vending_machine_id, "customer_id": customer_id, "ship_to_id": ship_to_id}.items() if v}
    rows = ctx.find("vending_transactions", **match)
    return str(rows) if rows else f"No vending_transactions records for {match}."


@tool(owner="agent", rw="read")
def find_vending_planogram(ctx: ToolContext, vending_slot_id: str = "", vending_machine_id: str = "", customer_id: str = "") -> str:
    """Look up VendPoint selection history: items assigned to selections, par changes and removals, with who asked for each change. Every criterion is optional: supply whichever reference numbers you hold, and all records carrying all of them are returned; when nothing matches, a short notice says so.

    Args:
        vending_slot_id: Reference number — the reference number of one VendPoint selection change entry; leave "" if unknown.
        vending_machine_id: Reference number — the reference number of a VendPoint machine placement; leave "" if unknown.
        customer_id: Reference number — the customer reference number of the account holder; leave "" if unknown.
    """
    match = {k: v for k, v in {"vending_slot_id": vending_slot_id, "vending_machine_id": vending_machine_id, "customer_id": customer_id}.items() if v}
    rows = ctx.find("vending_planogram", **match)
    return str(rows) if rows else f"No vending_planogram records for {match}."


@tool(owner="agent", rw="read")
def find_calibration_plans(ctx: ToolContext, calibration_plan_id: str = "", customer_id: str = "") -> str:
    """Look up CalCare plans: the tier, status, plan number, current plan year dates, prepaid unit balance and any cancellation notice date. Every criterion is optional: supply whichever reference numbers you hold, and all records carrying all of them are returned; when nothing matches, a short notice says so.

    Args:
        calibration_plan_id: Reference number — the reference number of the CalCare plan; leave "" if unknown.
        customer_id: Reference number — the customer reference number of the account holder; leave "" if unknown.
    """
    match = {k: v for k, v in {"calibration_plan_id": calibration_plan_id, "customer_id": customer_id}.items() if v}
    rows = ctx.find("calibration_plans", **match)
    return str(rows) if rows else f"No calibration_plans records for {match}."


@tool(owner="agent", rw="read")
def find_calibration_assets(ctx: ToolContext, calibration_asset_id: str = "", calibration_plan_id: str = "", customer_id: str = "") -> str:
    """Look up the CalCare instrument registry: instruments registered with class, model and interval, and instruments retired. Every criterion is optional: supply whichever reference numbers you hold, and all records carrying all of them are returned; when nothing matches, a short notice says so.

    Args:
        calibration_asset_id: Reference number — the reference number of one instrument registry entry; leave "" if unknown.
        calibration_plan_id: Reference number — the reference number of the CalCare plan; leave "" if unknown.
        customer_id: Reference number — the customer reference number of the account holder; leave "" if unknown.
    """
    match = {k: v for k, v in {"calibration_asset_id": calibration_asset_id, "calibration_plan_id": calibration_plan_id, "customer_id": customer_id}.items() if v}
    rows = ctx.find("calibration_assets", **match)
    return str(rows) if rows else f"No calibration_assets records for {match}."


@tool(owner="agent", rw="read")
def find_calibration_services(ctx: ToolContext, cal_service_id: str = "", calibration_plan_id: str = "", customer_id: str = "") -> str:
    """Look up CalCare service history: unit grants, top-ups and expiries, calibrations performed with certificate and as-found result, repair quotes and decisions, charges billed and service credits. Every criterion is optional: supply whichever reference numbers you hold, and all records carrying all of them are returned; when nothing matches, a short notice says so.

    Args:
        cal_service_id: Reference number — the reference number of one CalCare service entry; leave "" if unknown.
        calibration_plan_id: Reference number — the reference number of the CalCare plan; leave "" if unknown.
        customer_id: Reference number — the customer reference number of the account holder; leave "" if unknown.
    """
    match = {k: v for k, v in {"cal_service_id": cal_service_id, "calibration_plan_id": calibration_plan_id, "customer_id": customer_id}.items() if v}
    rows = ctx.find("calibration_services", **match)
    return str(rows) if rows else f"No calibration_services records for {match}."


@tool(owner="agent", rw="read")
def find_safety_programs(ctx: ToolContext, safety_program_id: str = "", customer_id: str = "") -> str:
    """Look up SafeStep programs: the tier, status, program number, go-live and allowance year dates, suspension and closing dates and the unredeemed allowance balance. Every criterion is optional: supply whichever reference numbers you hold, and all records carrying all of them are returned; when nothing matches, a short notice says so.

    Args:
        safety_program_id: Reference number — the reference number of the SafeStep program; leave "" if unknown.
        customer_id: Reference number — the customer reference number of the account holder; leave "" if unknown.
    """
    match = {k: v for k, v in {"safety_program_id": safety_program_id, "customer_id": customer_id}.items() if v}
    rows = ctx.find("safety_programs", **match)
    return str(rows) if rows else f"No safety_programs records for {match}."


@tool(owner="agent", rw="read")
def find_safety_participants(ctx: ToolContext, safety_participant_id: str = "", safety_program_id: str = "", customer_id: str = "") -> str:
    """Look up the SafeStep participant roster: employees added with job class and hire date, and employees removed. Every criterion is optional: supply whichever reference numbers you hold, and all records carrying all of them are returned; when nothing matches, a short notice says so.

    Args:
        safety_participant_id: Reference number — the reference number of one SafeStep roster entry; leave "" if unknown.
        safety_program_id: Reference number — the reference number of the SafeStep program; leave "" if unknown.
        customer_id: Reference number — the customer reference number of the account holder; leave "" if unknown.
    """
    match = {k: v for k, v in {"safety_participant_id": safety_participant_id, "safety_program_id": safety_program_id, "customer_id": customer_id}.items() if v}
    rows = ctx.find("safety_participants", **match)
    return str(rows) if rows else f"No safety_participants records for {match}."


@tool(owner="agent", rw="read")
def find_safety_redemptions(ctx: ToolContext, safety_redemption_id: str = "", safety_program_id: str = "", customer_id: str = "") -> str:
    """Look up SafeStep allowance history: allowance grants, purchases redeemed with employer and employee portions, returns, expiries, employer bills and program fees. Every criterion is optional: supply whichever reference numbers you hold, and all records carrying all of them are returned; when nothing matches, a short notice says so.

    Args:
        safety_redemption_id: Reference number — the reference number of one SafeStep allowance entry; leave "" if unknown.
        safety_program_id: Reference number — the reference number of the SafeStep program; leave "" if unknown.
        customer_id: Reference number — the customer reference number of the account holder; leave "" if unknown.
    """
    match = {k: v for k, v in {"safety_redemption_id": safety_redemption_id, "safety_program_id": safety_program_id, "customer_id": customer_id}.items() if v}
    rows = ctx.find("safety_redemptions", **match)
    return str(rows) if rows else f"No safety_redemptions records for {match}."

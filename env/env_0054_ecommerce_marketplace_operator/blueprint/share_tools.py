"""Shared tools for env_0054_ecommerce_marketplace_operator (Northloop Marketplace).

Every tool here is a SHARE tool: one record finder per table (the customers finder doubles as the
identity entry), the identity verification write, and the transfer to a human representative.
"""

from erlbench import ToolContext, tool


@tool(owner="agent", rw="read")
def find_fbn_enrollments(ctx: ToolContext, enrollment_id: str = "", customer_id: str = "") -> str:
    """Look up a seller's Fulfilled by Northloop (FBN) enrollment: the FBN program it is placed in, its status, approval and review dates, any inbound suspension and its reason, an exit request, and the units currently held in Northloop fulfillment centers.

    Every criterion is optional; supply whichever reference numbers are already known and all
    matching records are returned. When nothing matches, a short notice says so.

    Args:
        enrollment_id: The Fulfilled by Northloop enrollment reference; leave "" if unknown.
        customer_id: The customer reference number of the buyer or seller the record belongs to; leave "" if unknown.
    """
    match = {k: v for k, v in {"enrollment_id": enrollment_id, "customer_id": customer_id}.items() if v}
    rows = ctx.find("fulfill_enrollments", **match)
    return str(rows) if rows else f"No matching records for {match}."

@tool(owner="agent", rw="read")
def find_fbn_activity(ctx: ToolContext, fulfill_event_id: str = "", enrollment_id: str = "", customer_id: str = "", shipment_id: str = "", order_id: str = "", removal_order_id: str = "", case_id: str = "") -> str:
    """Look up the FBN activity of an enrollment: inbound receipts and placement fees, units shipped for orders and their fulfillment fees, monthly storage fees and aged inventory surcharges, capacity overage fees, removals and their fees, warehouse loss or damage adjustments, found inventory, restocked customer returns, reimbursements and fee credits. Each record shows its date, amount, SKU, units and the references it relates to.

    Every criterion is optional; supply whichever reference numbers are already known and all
    matching records are returned. When nothing matches, a short notice says so.

    Args:
        fulfill_event_id: The reference of the FBN fee, inventory movement or reimbursement record itself; leave "" if unknown.
        enrollment_id: The Fulfilled by Northloop enrollment reference; leave "" if unknown.
        customer_id: The customer reference number of the buyer or seller the record belongs to; leave "" if unknown.
        shipment_id: The inbound shipment number; leave "" if unknown.
        order_id: The marketplace order number; leave "" if unknown.
        removal_order_id: The removal order reference; leave "" if unknown.
        case_id: The FBN seller case reference; leave "" if unknown.
    """
    match = {k: v for k, v in {"fulfill_event_id": fulfill_event_id, "enrollment_id": enrollment_id, "customer_id": customer_id, "shipment_id": shipment_id, "order_id": order_id, "removal_order_id": removal_order_id, "case_id": case_id}.items() if v}
    rows = ctx.find("fulfill_events", **match)
    return str(rows) if rows else f"No matching records for {match}."

@tool(owner="agent", rw="read")
def find_fbn_removal_orders(ctx: ToolContext, removal_order_id: str = "", enrollment_id: str = "", customer_id: str = "") -> str:
    """Look up removal orders a seller has placed to have FBN inventory returned or disposed: the SKU, units, removal type, progress and when it was placed.

    Every criterion is optional; supply whichever reference numbers are already known and all
    matching records are returned. When nothing matches, a short notice says so.

    Args:
        removal_order_id: The removal order reference; leave "" if unknown.
        enrollment_id: The Fulfilled by Northloop enrollment reference; leave "" if unknown.
        customer_id: The customer reference number of the buyer or seller the record belongs to; leave "" if unknown.
    """
    match = {k: v for k, v in {"removal_order_id": removal_order_id, "enrollment_id": enrollment_id, "customer_id": customer_id}.items() if v}
    rows = ctx.find("fulfill_removal_orders", **match)
    return str(rows) if rows else f"No matching records for {match}."

@tool(owner="agent", rw="read")
def find_fbn_cases(ctx: ToolContext, case_id: str = "", enrollment_id: str = "", customer_id: str = "", shipment_id: str = "", order_id: str = "", removal_order_id: str = "") -> str:
    """Look up FBN seller cases: reimbursement claims for lost, damaged or missing units and FBN fee disputes, with what they concern, the units claimed and their outcome.

    Every criterion is optional; supply whichever reference numbers are already known and all
    matching records are returned. When nothing matches, a short notice says so.

    Args:
        case_id: The FBN seller case reference; leave "" if unknown.
        enrollment_id: The Fulfilled by Northloop enrollment reference; leave "" if unknown.
        customer_id: The customer reference number of the buyer or seller the record belongs to; leave "" if unknown.
        shipment_id: The inbound shipment number; leave "" if unknown.
        order_id: The marketplace order number; leave "" if unknown.
        removal_order_id: The removal order reference; leave "" if unknown.
    """
    match = {k: v for k, v in {"case_id": case_id, "enrollment_id": enrollment_id, "customer_id": customer_id, "shipment_id": shipment_id, "order_id": order_id, "removal_order_id": removal_order_id}.items() if v}
    rows = ctx.find("fulfill_cases", **match)
    return str(rows) if rows else f"No matching records for {match}."

@tool(owner="agent", rw="read")
def find_loop_plus_memberships(ctx: ToolContext, membership_id: str = "", customer_id: str = "") -> str:
    """Look up a buyer's Loop+ membership: the plan, status, sign-up and trial dates, eligibility verification date, paid-through and next billing dates, any pending cancellation or end date, the card on file and the promotional credit balance.

    Every criterion is optional; supply whichever reference numbers are already known and all
    matching records are returned. When nothing matches, a short notice says so.

    Args:
        membership_id: The Loop+ membership reference; leave "" if unknown.
        customer_id: The customer reference number of the buyer or seller the record belongs to; leave "" if unknown.
    """
    match = {k: v for k, v in {"membership_id": membership_id, "customer_id": customer_id}.items() if v}
    rows = ctx.find("member_memberships", **match)
    return str(rows) if rows else f"No matching records for {match}."

@tool(owner="agent", rw="read")
def find_loop_plus_activity(ctx: ToolContext, member_event_id: str = "", membership_id: str = "", customer_id: str = "") -> str:
    """Look up the activity on a Loop+ membership: fee charges and declined attempts, fee refunds, benefit uses, and promotional credits earned, applied or expired, each with its date and amount.

    Every criterion is optional; supply whichever reference numbers are already known and all
    matching records are returned. When nothing matches, a short notice says so.

    Args:
        member_event_id: The reference of the membership charge, refund, credit or benefit record itself; leave "" if unknown.
        membership_id: The Loop+ membership reference; leave "" if unknown.
        customer_id: The customer reference number of the buyer or seller the record belongs to; leave "" if unknown.
    """
    match = {k: v for k, v in {"member_event_id": member_event_id, "membership_id": membership_id, "customer_id": customer_id}.items() if v}
    rows = ctx.find("member_events", **match)
    return str(rows) if rows else f"No matching records for {match}."

@tool(owner="agent", rw="read")
def find_orders(ctx: ToolContext, order_id: str = "", customer_id: str = "", seller_customer_id: str = "") -> str:
    """Look up marketplace orders: the item, seller, delivery option, quantity and prices, shipping and tax, order total, gift flag, promised delivery date, shipment and tracking details, delivery outcome, any carrier exception or cancellation, the net amount paid and the order status.

    Every criterion is optional; supply whichever reference numbers are already known and all
    matching records are returned. When nothing matches, a short notice says so.

    Args:
        order_id: The marketplace order number; leave "" if unknown.
        customer_id: The customer reference number of the buyer or seller the record belongs to; leave "" if unknown.
        seller_customer_id: The customer reference number of the seller who sold the order; leave "" if unknown.
    """
    match = {k: v for k, v in {"order_id": order_id, "customer_id": customer_id, "seller_customer_id": seller_customer_id}.items() if v}
    rows = ctx.find("order_orders", **match)
    return str(rows) if rows else f"No matching records for {match}."

@tool(owner="agent", rw="read")
def find_order_activity(ctx: ToolContext, order_event_id: str = "", order_id: str = "", customer_id: str = "", return_id: str = "", claim_id: str = "", replacement_order_id: str = "") -> str:
    """Look up what has happened on an order after checkout: payment captures, return requests and return scans with their inspection result, refunds by component with any deductions, replacements, and Northloop Guarantee claims with their decisions.

    Every criterion is optional; supply whichever reference numbers are already known and all
    matching records are returned. When nothing matches, a short notice says so.

    Args:
        order_event_id: The reference of the order charge, return, refund, replacement or claim record itself; leave "" if unknown.
        order_id: The marketplace order number; leave "" if unknown.
        customer_id: The customer reference number of the buyer or seller the record belongs to; leave "" if unknown.
        return_id: The return number issued when the return was requested; leave "" if unknown.
        claim_id: The claim number; leave "" if unknown.
        replacement_order_id: The order number of a replacement order; leave "" if unknown.
    """
    match = {k: v for k, v in {"order_event_id": order_event_id, "order_id": order_id, "customer_id": customer_id, "return_id": return_id, "claim_id": claim_id, "replacement_order_id": replacement_order_id}.items() if v}
    rows = ctx.find("order_events", **match)
    return str(rows) if rows else f"No matching records for {match}."

@tool(owner="agent", rw="read")
def find_payments_accounts(ctx: ToolContext, payout_account_id: str = "", customer_id: str = "") -> str:
    """Look up a seller's Northloop Payments account: the payout plan, status, verification and bank details, total and reserved balance, the date a negative balance began, any payout hold and its reason, and closure dates.

    Every criterion is optional; supply whichever reference numbers are already known and all
    matching records are returned. When nothing matches, a short notice says so.

    Args:
        payout_account_id: The Northloop Payments account reference; leave "" if unknown.
        customer_id: The customer reference number of the buyer or seller the record belongs to; leave "" if unknown.
    """
    match = {k: v for k, v in {"payout_account_id": payout_account_id, "customer_id": customer_id}.items() if v}
    rows = ctx.find("payout_accounts", **match)
    return str(rows) if rows else f"No matching records for {match}."

@tool(owner="agent", rw="read")
def find_payments_ledger(ctx: ToolContext, payout_event_id: str = "", payout_account_id: str = "", customer_id: str = "", order_id: str = "", chargeback_case_id: str = "") -> str:
    """Look up the payments ledger of a seller: sale proceeds, reserves placed and released, payouts and instant payout fees, returned payouts, fee deductions and reversals, refund debits, chargebacks and their fees and reversals, reimbursements and their reversals, and card charges against a negative balance.

    Every criterion is optional; supply whichever reference numbers are already known and all
    matching records are returned. When nothing matches, a short notice says so.

    Args:
        payout_event_id: The reference of the payments ledger entry itself; leave "" if unknown.
        payout_account_id: The Northloop Payments account reference; leave "" if unknown.
        customer_id: The customer reference number of the buyer or seller the record belongs to; leave "" if unknown.
        order_id: The marketplace order number; leave "" if unknown.
        chargeback_case_id: The card chargeback case reference; leave "" if unknown.
    """
    match = {k: v for k, v in {"payout_event_id": payout_event_id, "payout_account_id": payout_account_id, "customer_id": customer_id, "order_id": order_id, "chargeback_case_id": chargeback_case_id}.items() if v}
    rows = ctx.find("payout_events", **match)
    return str(rows) if rows else f"No matching records for {match}."

@tool(owner="agent", rw="read")
def find_chargeback_disputes(ctx: ToolContext, dispute_id: str = "", payout_account_id: str = "", customer_id: str = "", chargeback_case_id: str = "", order_id: str = "") -> str:
    """Look up the chargeback disputes a seller has submitted: the chargeback case, the order, the evidence provided and the outcome.

    Every criterion is optional; supply whichever reference numbers are already known and all
    matching records are returned. When nothing matches, a short notice says so.

    Args:
        dispute_id: The dispute reference; leave "" if unknown.
        payout_account_id: The Northloop Payments account reference; leave "" if unknown.
        customer_id: The customer reference number of the buyer or seller the record belongs to; leave "" if unknown.
        chargeback_case_id: The card chargeback case reference; leave "" if unknown.
        order_id: The marketplace order number; leave "" if unknown.
    """
    match = {k: v for k, v in {"dispute_id": dispute_id, "payout_account_id": payout_account_id, "customer_id": customer_id, "chargeback_case_id": chargeback_case_id, "order_id": order_id}.items() if v}
    rows = ctx.find("payout_chargeback_disputes", **match)
    return str(rows) if rows else f"No matching records for {match}."

@tool(owner="agent", rw="read")
def find_protection_plans(ctx: ToolContext, plan_id: str = "", customer_id: str = "", covered_order_id: str = "") -> str:
    """Look up Northloop Protect plans a buyer holds: the plan, the covered order and item price, plan price, coverage dates, claims paid so far, and any cancellation or end date.

    Every criterion is optional; supply whichever reference numbers are already known and all
    matching records are returned. When nothing matches, a short notice says so.

    Args:
        plan_id: The Northloop Protect plan reference; leave "" if unknown.
        customer_id: The customer reference number of the buyer or seller the record belongs to; leave "" if unknown.
        covered_order_id: The order number of the item the plan covers; leave "" if unknown.
    """
    match = {k: v for k, v in {"plan_id": plan_id, "customer_id": customer_id, "covered_order_id": covered_order_id}.items() if v}
    rows = ctx.find("protect_plans", **match)
    return str(rows) if rows else f"No matching records for {match}."

@tool(owner="agent", rw="read")
def find_protection_plan_activity(ctx: ToolContext, protect_event_id: str = "", plan_id: str = "", customer_id: str = "", claim_id: str = "") -> str:
    """Look up the activity on a protection plan: the plan charge, claim settlements and reversals, claim service fees and their refunds, and cancellation refunds.

    Every criterion is optional; supply whichever reference numbers are already known and all
    matching records are returned. When nothing matches, a short notice says so.

    Args:
        protect_event_id: The reference of the plan charge, settlement, fee or refund record itself; leave "" if unknown.
        plan_id: The Northloop Protect plan reference; leave "" if unknown.
        customer_id: The customer reference number of the buyer or seller the record belongs to; leave "" if unknown.
        claim_id: The claim number; leave "" if unknown.
    """
    match = {k: v for k, v in {"protect_event_id": protect_event_id, "plan_id": plan_id, "customer_id": customer_id, "claim_id": claim_id}.items() if v}
    rows = ctx.find("protect_events", **match)
    return str(rows) if rows else f"No matching records for {match}."

@tool(owner="agent", rw="read")
def find_protection_claims(ctx: ToolContext, claim_id: str = "", plan_id: str = "", customer_id: str = "") -> str:
    """Look up claims filed under a protection plan: what happened to the item and when, the claim's progress and how it is being resolved.

    Every criterion is optional; supply whichever reference numbers are already known and all
    matching records are returned. When nothing matches, a short notice says so.

    Args:
        claim_id: The claim number; leave "" if unknown.
        plan_id: The Northloop Protect plan reference; leave "" if unknown.
        customer_id: The customer reference number of the buyer or seller the record belongs to; leave "" if unknown.
    """
    match = {k: v for k, v in {"claim_id": claim_id, "plan_id": plan_id, "customer_id": customer_id}.items() if v}
    rows = ctx.find("protect_claims", **match)
    return str(rows) if rows else f"No matching records for {match}."

@tool(owner="agent", rw="read")
def find_selling_plans(ctx: ToolContext, selling_plan_id: str = "", customer_id: str = "") -> str:
    """Look up a seller's selling plan: the plan and billing term, status, store name, verification date, term and next billing dates, and any scheduled cancellation, restriction or closure date.

    Every criterion is optional; supply whichever reference numbers are already known and all
    matching records are returned. When nothing matches, a short notice says so.

    Args:
        selling_plan_id: The selling plan reference; leave "" if unknown.
        customer_id: The customer reference number of the buyer or seller the record belongs to; leave "" if unknown.
    """
    match = {k: v for k, v in {"selling_plan_id": selling_plan_id, "customer_id": customer_id}.items() if v}
    rows = ctx.find("selling_plans", **match)
    return str(rows) if rows else f"No matching records for {match}."

@tool(owner="agent", rw="read")
def find_seller_fees(ctx: ToolContext, selling_event_id: str = "", selling_plan_id: str = "", customer_id: str = "", listing_id: str = "", order_id: str = "") -> str:
    """Look up seller fees billed on a selling plan and the credits given against them: subscription fees, insertion fees, final value fee components on orders, early termination fees and fee credits, each with its billing period, amount and what it relates to.

    Every criterion is optional; supply whichever reference numbers are already known and all
    matching records are returned. When nothing matches, a short notice says so.

    Args:
        selling_event_id: The fee reference of the seller fee or fee credit record itself; leave "" if unknown.
        selling_plan_id: The selling plan reference; leave "" if unknown.
        customer_id: The customer reference number of the buyer or seller the record belongs to; leave "" if unknown.
        listing_id: The listing number; leave "" if unknown.
        order_id: The marketplace order number; leave "" if unknown.
    """
    match = {k: v for k, v in {"selling_event_id": selling_event_id, "selling_plan_id": selling_plan_id, "customer_id": customer_id, "listing_id": listing_id, "order_id": order_id}.items() if v}
    rows = ctx.find("selling_fees", **match)
    return str(rows) if rows else f"No matching records for {match}."

@tool(owner="agent", rw="read")
def find_seller_fee_disputes(ctx: ToolContext, dispute_id: str = "", selling_plan_id: str = "", customer_id: str = "") -> str:
    """Look up the disputes a seller has raised against seller fees: the fee disputed, the ground and the outcome.

    Every criterion is optional; supply whichever reference numbers are already known and all
    matching records are returned. When nothing matches, a short notice says so.

    Args:
        dispute_id: The dispute reference; leave "" if unknown.
        selling_plan_id: The selling plan reference; leave "" if unknown.
        customer_id: The customer reference number of the buyer or seller the record belongs to; leave "" if unknown.
    """
    match = {k: v for k, v in {"dispute_id": dispute_id, "selling_plan_id": selling_plan_id, "customer_id": customer_id}.items() if v}
    rows = ctx.find("selling_fee_disputes", **match)
    return str(rows) if rows else f"No matching records for {match}."

@tool(owner="agent", rw="read")
def find_seller_standing(ctx: ToolContext, standing_id: str = "", customer_id: str = "") -> str:
    """Look up a seller's performance standing: the current performance level, account health status, evaluation dates, active violation points, and any warning, suspension, appeal, reinstatement, deactivation or closure dates.

    Every criterion is optional; supply whichever reference numbers are already known and all
    matching records are returned. When nothing matches, a short notice says so.

    Args:
        standing_id: The seller performance standing record reference; leave "" if unknown.
        customer_id: The customer reference number of the buyer or seller the record belongs to; leave "" if unknown.
    """
    match = {k: v for k, v in {"standing_id": standing_id, "customer_id": customer_id}.items() if v}
    rows = ctx.find("standing_records", **match)
    return str(rows) if rows else f"No matching records for {match}."

@tool(owner="agent", rw="read")
def find_seller_standing_activity(ctx: ToolContext, standing_event_id: str = "", standing_id: str = "", customer_id: str = "", order_id: str = "", listing_id: str = "", dispute_id: str = "") -> str:
    """Look up the standing activity of a seller: order defects recorded and removed, policy violations with their points, reversals and expiries, and feedback or reviews removed.

    Every criterion is optional; supply whichever reference numbers are already known and all
    matching records are returned. When nothing matches, a short notice says so.

    Args:
        standing_event_id: The reference of the defect, violation or removal record itself; leave "" if unknown.
        standing_id: The seller performance standing record reference; leave "" if unknown.
        customer_id: The customer reference number of the buyer or seller the record belongs to; leave "" if unknown.
        order_id: The marketplace order number; leave "" if unknown.
        listing_id: The listing number; leave "" if unknown.
        dispute_id: The dispute reference; leave "" if unknown.
    """
    match = {k: v for k, v in {"standing_event_id": standing_event_id, "standing_id": standing_id, "customer_id": customer_id, "order_id": order_id, "listing_id": listing_id, "dispute_id": dispute_id}.items() if v}
    rows = ctx.find("standing_events", **match)
    return str(rows) if rows else f"No matching records for {match}."

@tool(owner="agent", rw="read")
def find_review_disputes(ctx: ToolContext, dispute_id: str = "", standing_id: str = "", customer_id: str = "", order_id: str = "") -> str:
    """Look up the disputes a seller has raised against buyer feedback or product reviews: the feedback or review concerned, the ground and the outcome.

    Every criterion is optional; supply whichever reference numbers are already known and all
    matching records are returned. When nothing matches, a short notice says so.

    Args:
        dispute_id: The dispute reference; leave "" if unknown.
        standing_id: The seller performance standing record reference; leave "" if unknown.
        customer_id: The customer reference number of the buyer or seller the record belongs to; leave "" if unknown.
        order_id: The marketplace order number; leave "" if unknown.
    """
    match = {k: v for k, v in {"dispute_id": dispute_id, "standing_id": standing_id, "customer_id": customer_id, "order_id": order_id}.items() if v}
    rows = ctx.find("standing_review_disputes", **match)
    return str(rows) if rows else f"No matching records for {match}."

@tool(owner="agent", rw="read")
def find_standing_appeals(ctx: ToolContext, appeal_id: str = "", standing_id: str = "", customer_id: str = "") -> str:
    """Look up the appeals a seller has submitted against a suspension of selling privileges: the violation addressed, the basis of the appeal and its outcome.

    Every criterion is optional; supply whichever reference numbers are already known and all
    matching records are returned. When nothing matches, a short notice says so.

    Args:
        appeal_id: The appeal reference; leave "" if unknown.
        standing_id: The seller performance standing record reference; leave "" if unknown.
        customer_id: The customer reference number of the buyer or seller the record belongs to; leave "" if unknown.
    """
    match = {k: v for k, v in {"appeal_id": appeal_id, "standing_id": standing_id, "customer_id": customer_id}.items() if v}
    rows = ctx.find("standing_appeals", **match)
    return str(rows) if rows else f"No matching records for {match}."

@tool(owner="agent", rw="read")
def find_identity_verifications(ctx: ToolContext, verification_id: str = "", customer_id: str = "") -> str:
    """Look up the identity verification outcome recorded for a customer during support contacts.

    Every criterion is optional; supply whichever reference numbers are already known and all
    matching records are returned. When nothing matches, a short notice says so.

    Args:
        verification_id: The identity verification record reference; leave "" if unknown.
        customer_id: The customer reference number of the buyer or seller the record belongs to; leave "" if unknown.
    """
    match = {k: v for k, v in {"verification_id": verification_id, "customer_id": customer_id}.items() if v}
    rows = ctx.find("verification_log", **match)
    return str(rows) if rows else f"No matching records for {match}."

@tool(owner="agent", rw="read")
def find_handoffs(ctx: ToolContext, handoff_id: str = "", customer_id: str = "") -> str:
    """Look up handoffs of a customer to a human representative and their recorded reasons.

    Every criterion is optional; supply whichever reference numbers are already known and all
    matching records are returned. When nothing matches, a short notice says so.

    Args:
        handoff_id: The handoff record reference; leave "" if unknown.
        customer_id: The customer reference number of the buyer or seller the record belongs to; leave "" if unknown.
    """
    match = {k: v for k, v in {"handoff_id": handoff_id, "customer_id": customer_id}.items() if v}
    rows = ctx.find("handoff_log", **match)
    return str(rows) if rows else f"No matching records for {match}."

@tool(owner="agent", rw="read")
def find_customers(ctx: ToolContext, customer_id: str = "", name: str = "", email: str = "",
                   phone: str = "", business_name: str = "") -> str:
    """Look up a Northloop customer profile to establish whose account the contact is about. A
    profile can be found by its customer reference number or by what the caller naturally states:
    the name on the profile, the registered email address, the registered mobile number, or, for a
    seller, the registered business name. The profile shows the contact details, the billing ZIP
    code, the date the profile was opened, the last four digits of the default payment card,
    whether the customer buys, sells or both, and for sellers the business name and the last four
    digits of the taxpayer identification number. Finding a profile does not verify the caller's
    identity.

    Args:
        customer_id: The customer reference number; leave "" if unknown.
        name: The full name on the profile, as the caller states it; leave "" if not provided.
        email: The registered email address, as the caller states it; leave "" if not provided.
        phone: The registered mobile number, 10 digits; leave "" if not provided.
        business_name: The seller's registered business name, as the caller states it; leave "" if not provided.
    """
    match = {k: v for k, v in {"customer_id": customer_id, "name": name, "email": email,
                               "phone": phone, "business_name": business_name}.items() if v}
    if not match:
        return "Error: provide at least one reference number or profile detail to find the customer."
    rows = ctx.fuzzy_find("customers", **match)
    if not rows:
        return f"No customer matches {match}."
    if len(rows) > 1:
        return f"Error: {len(rows)} customers match {match}; ask for one more detail to tell them apart."
    return str(rows[0])


@tool(owner="agent", rw="write")
def verify_customer_identity(ctx: ToolContext, customer_id: str, email: str = "", phone: str = "",
                             billing_zip: str = "", account_opened_date: str = "",
                             payment_card_last4: str = "", tax_id_last4: str = "") -> str:
    """Verify the caller's identity against the customer profile and record the outcome. Identity
    must be verified before any account information is discussed or any change, refund, fee
    adjustment or payout action is made. This tool performs the comparison itself: each detail the
    caller states is compared with the profile on file, and verification passes when at least two
    of them match. The customer reference number only locates the profile and never counts as a
    match. Callers usually state only some details, so pass exactly the values the caller gave and
    leave the others empty. The outcome is recorded; if a first attempt fails and a later attempt
    with more details passes, the pass stands.

    Args:
        customer_id: The customer reference number read from the customer profile lookup; required. Used only to retrieve the profile and never counted as a match.
        email: The registered email address as stated by the caller; leave "" if not stated.
        phone: The registered mobile number as stated by the caller, 10 digits with no punctuation; leave "" if not stated.
        billing_zip: The 5-digit ZIP code of the default billing address as stated by the caller; leave "" if not stated.
        account_opened_date: The date the Northloop profile was opened as stated by the caller, YYYY-MM-DD; leave "" if not stated.
        payment_card_last4: The last four digits of the default payment card on file as stated by the caller; leave "" if not stated.
        tax_id_last4: For sellers, the last four digits of the taxpayer identification number as stated by the caller; leave "" if not stated.
    """
    if not customer_id:
        return "Error: customer_id is required; look the customer up first and pass their reference number."
    rows = ctx.find("customers", customer_id=customer_id)
    if not rows:
        return f"Error: no customer {customer_id}; cannot verify."
    rec = rows[0]
    # The tool owns the comparison; the locator customer_id is deliberately not a credential.
    supplied = {"email": email, "phone": phone, "billing_zip": billing_zip,
                "account_opened_date": account_opened_date,
                "payment_card_last4": payment_card_last4, "tax_id_last4": tax_id_last4}
    matched = sum(1 for field, value in supplied.items()
                  if value and rec.get(field) and str(rec.get(field)).strip().lower() == str(value).strip().lower())
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
            else f"Identity NOT verified for {customer_id} (only {matched} of the required 2 details matched). "
                 "Ask the caller for another detail on file and try again.")


@tool(owner="agent", rw="write")
def transfer_to_human_agent(ctx: ToolContext, customer_id: str, reason: str) -> str:
    """Hand the customer over to a human representative and record the handoff with its reason.
    Use it when no Northloop policy provides a way to resolve what the customer is asking for, or
    when the customer has explicitly asked to speak with a human representative at least 2 times
    during the contact.

    Args:
        customer_id: The customer reference number read from the customer profile lookup; the profile must exist.
        reason: The reason for the handoff, exactly one of POLICY_NOT_COVERED (current policy offers no way to resolve the request) or CUSTOMER_REQUESTED (the customer has explicitly asked for a human representative at least 2 times). Never free text.
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

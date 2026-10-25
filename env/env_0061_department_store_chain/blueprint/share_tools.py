"""Shared tools for env_0061_department_store_chain (Marlowe & Finch customer care).

Every tool here is a share tool, present in every task: one record finder per table (the customers
finder doubles as the identity entry), the identity verification write and the transfer to a human
representative. Customer-initiated writes live in each difficulty's task_tools.py as hidden user tools.
Scenario operational constants: identity verification passes at K = 2 matching credentials; a transfer
for CUSTOMER_REQUESTED requires the customer to have asked for a human R = 2 times.
"""

from erlbench import ToolContext, tool


@tool(owner="agent", rw="read")
def find_customers(ctx: ToolContext, customer_id: str = "", phone_number: str = "", email: str = "", name: str = "") -> str:
    """Find the customer profile this conversation is about, by the customer reference number or by what the caller can tell you: the registered mobile number, the registered email address or the full name. Every criterion is optional; give whichever you have, and add another when several customers match. The profile returned shows the name, mobile number, email, date of birth, last four digits of the Social Security number on file (for card customers), billing ZIP code, mailing address and the date the profile was opened. Finding a profile does not confirm the caller's identity; identity is confirmed separately.

    Args:
        customer_id: The customer reference number, if already known; leave "" otherwise.
        phone_number: The registered mobile number as the caller states it (10 digits; spacing and punctuation are ignored); leave "" if not given.
        email: The registered email address as the caller states it; leave "" if not given.
        name: The customer's full name as the caller states it; leave "" if not given.
    """
    match = {k: v for k, v in {"customer_id": customer_id, "phone_number": phone_number,
                               "email": email, "name": name}.items() if v}
    if not match:
        return "Error: provide at least one reference number or profile detail to find the customer."
    rows = ctx.fuzzy_find("customers", **match)
    if not rows:
        return f"No customer matches {match}."
    if len(rows) > 1:
        return f"Error: {len(rows)} customers match {match}; ask for one more detail to tell them apart."
    return str(rows[0])


@tool(owner="agent", rw="read")
def find_identity_verifications(ctx: ToolContext, verification_id: str = "", customer_id: str = "") -> str:
    """Look up the outcome of identity checks recorded for a customer: whether the caller has been verified and when the latest check was recorded. Search by any reference number you already hold; every criterion is optional and the records matching all the criteria given are returned, or a notice when none match.

    Args:
        verification_id: The reference number of the identity check record itself; leave "" if unknown.
        customer_id: The customer reference number; leave "" if unknown.
    """
    match = {k: v for k, v in {"verification_id": verification_id,
                               "customer_id": customer_id}.items() if v}
    rows = ctx.find("identity_verifications", **match)
    return str(rows) if rows else f"No identity_verifications records for {match}."


@tool(owner="agent", rw="read")
def find_handoffs(ctx: ToolContext, handoff_id: str = "", customer_id: str = "") -> str:
    """Look up the transfers to a human representative already recorded for a customer, with the reason and the moment of each transfer. Search by any reference number you already hold; every criterion is optional and the records matching all the criteria given are returned, or a notice when none match.

    Args:
        handoff_id: The reference number of the transfer record itself; leave "" if unknown.
        customer_id: The customer reference number; leave "" if unknown.
    """
    match = {k: v for k, v in {"handoff_id": handoff_id,
                               "customer_id": customer_id}.items() if v}
    rows = ctx.find("handoffs", **match)
    return str(rows) if rows else f"No handoffs records for {match}."


@tool(owner="agent", rw="read")
def find_card_accounts(ctx: ToolContext, card_account_id: str = "", customer_id: str = "") -> str:
    """Look up Marlowe & Finch credit card accounts (store card and Mastercard): the card held and its status, application, opening and closing dates, last four digits, credit line, current balance, statement closing day, AutoPay instruction and the dates of the last credit line and status changes. Search by any reference number you already hold; every criterion is optional and the records matching all the criteria given are returned, or a notice when none match.

    Args:
        card_account_id: The reference number of the Marlowe & Finch card account; leave "" if unknown.
        customer_id: The customer reference number; leave "" if unknown.
    """
    match = {k: v for k, v in {"card_account_id": card_account_id,
                               "customer_id": customer_id}.items() if v}
    rows = ctx.find("card_accounts", **match)
    return str(rows) if rows else f"No card_accounts records for {match}."


@tool(owner="agent", rw="read")
def find_card_transactions(ctx: ToolContext, card_txn_id: str = "", card_account_id: str = "", customer_id: str = "", purchase_id: str = "", order_event_id: str = "", return_id: str = "", original_card_txn_id: str = "") -> str:
    """Look up the transactions posted to a Marlowe & Finch card account: purchases, payments, returned payments, merchandise credits, fees and fee reversals, interest, dispute credits and rebills, and credit balance refunds, with their dates, amounts, billing period and the details of each kind. Search by any reference number you already hold; every criterion is optional and the records matching all the criteria given are returned, or a notice when none match.

    Args:
        card_txn_id: The reference number of a card transaction; leave "" if unknown.
        card_account_id: The reference number of the Marlowe & Finch card account; leave "" if unknown.
        customer_id: The customer reference number; leave "" if unknown.
        purchase_id: The reference number of a purchase record (one unit of one item bought); leave "" if unknown.
        order_event_id: The reference number of a payment, price adjustment or refund record of a purchase; leave "" if unknown.
        return_id: The reference number of a return; leave "" if unknown.
        original_card_txn_id: The reference number of the earlier card transaction this one reverses, refunds or was caused by; leave "" if unknown.
    """
    match = {k: v for k, v in {"card_txn_id": card_txn_id,
                               "card_account_id": card_account_id,
                               "customer_id": customer_id,
                               "purchase_id": purchase_id,
                               "order_event_id": order_event_id,
                               "return_id": return_id,
                               "original_card_txn_id": original_card_txn_id}.items() if v}
    rows = ctx.find("card_transactions", **match)
    return str(rows) if rows else f"No card_transactions records for {match}."


@tool(owner="agent", rw="read")
def find_card_statements(ctx: ToolContext, statement_id: str = "", card_account_id: str = "", customer_id: str = "") -> str:
    """Look up the monthly statements of a Marlowe & Finch card account: billing period, statement date, payment due date, statement balance, minimum payment due, past-due amount, amount excluded for open disputes and special financing balance. Search by any reference number you already hold; every criterion is optional and the records matching all the criteria given are returned, or a notice when none match.

    Args:
        statement_id: The reference number of a monthly statement; leave "" if unknown.
        card_account_id: The reference number of the Marlowe & Finch card account; leave "" if unknown.
        customer_id: The customer reference number; leave "" if unknown.
    """
    match = {k: v for k, v in {"statement_id": statement_id,
                               "card_account_id": card_account_id,
                               "customer_id": customer_id}.items() if v}
    rows = ctx.find("card_statements", **match)
    return str(rows) if rows else f"No card_statements records for {match}."


@tool(owner="agent", rw="read")
def find_card_disputes(ctx: ToolContext, dispute_id: str = "", card_account_id: str = "", customer_id: str = "", disputed_card_txn_id: str = "") -> str:
    """Look up billing disputes on a Marlowe & Finch card account: each filing, resolution or withdrawal, with the transaction disputed, the reason, the amount, the notice date and channel, the first statement date and the outcome. Search by any reference number you already hold; every criterion is optional and the records matching all the criteria given are returned, or a notice when none match.

    Args:
        dispute_id: The reference number of a dispute filing, resolution or withdrawal record; leave "" if unknown.
        card_account_id: The reference number of the Marlowe & Finch card account; leave "" if unknown.
        customer_id: The customer reference number; leave "" if unknown.
        disputed_card_txn_id: The reference number of the card transaction under dispute; leave "" if unknown.
    """
    match = {k: v for k, v in {"dispute_id": dispute_id,
                               "card_account_id": card_account_id,
                               "customer_id": customer_id,
                               "disputed_card_txn_id": disputed_card_txn_id}.items() if v}
    rows = ctx.find("card_disputes", **match)
    return str(rows) if rows else f"No card_disputes records for {match}."


@tool(owner="agent", rw="read")
def find_card_service_requests(ctx: ToolContext, card_request_id: str = "", customer_id: str = "", card_account_id: str = "") -> str:
    """Look up service requests made on a Marlowe & Finch card account (closure, credit line increase, card replacement, credit balance refund) and their processing status. Search by any reference number you already hold; every criterion is optional and the records matching all the criteria given are returned, or a notice when none match.

    Args:
        card_request_id: The reference number of a card service request; leave "" if unknown.
        customer_id: The customer reference number; leave "" if unknown.
        card_account_id: The reference number of the Marlowe & Finch card account; leave "" if unknown.
    """
    match = {k: v for k, v in {"card_request_id": card_request_id,
                               "customer_id": customer_id,
                               "card_account_id": card_account_id}.items() if v}
    rows = ctx.find("card_service_requests", **match)
    return str(rows) if rows else f"No card_service_requests records for {match}."


@tool(owner="agent", rw="read")
def find_loyalty_memberships(ctx: ToolContext, membership_id: str = "", customer_id: str = "") -> str:
    """Look up Finch Circle memberships: tier and status, member number, enrollment and closing dates, how long the tier is held, the latest tier change, and the current points, Finch Notes and alteration credit balances. Search by any reference number you already hold; every criterion is optional and the records matching all the criteria given are returned, or a notice when none match.

    Args:
        membership_id: The reference number of the Finch Circle membership; leave "" if unknown.
        customer_id: The customer reference number; leave "" if unknown.
    """
    match = {k: v for k, v in {"membership_id": membership_id,
                               "customer_id": customer_id}.items() if v}
    rows = ctx.find("loyalty_memberships", **match)
    return str(rows) if rows else f"No loyalty_memberships records for {match}."


@tool(owner="agent", rw="read")
def find_loyalty_points_ledger(ctx: ToolContext, loyalty_entry_id: str = "", membership_id: str = "", customer_id: str = "", purchase_id: str = "", card_txn_id: str = "", return_id: str = "", original_loyalty_entry_id: str = "") -> str:
    """Look up the Finch Circle points history of a membership: points earned (with their source), credited after a missing-points request, deducted for returns, converted into Finch Notes, or forfeited. Search by any reference number you already hold; every criterion is optional and the records matching all the criteria given are returned, or a notice when none match.

    Args:
        loyalty_entry_id: The reference number of a points entry; leave "" if unknown.
        membership_id: The reference number of the Finch Circle membership; leave "" if unknown.
        customer_id: The customer reference number; leave "" if unknown.
        purchase_id: The reference number of a purchase record (one unit of one item bought); leave "" if unknown.
        card_txn_id: The reference number of a card transaction; leave "" if unknown.
        return_id: The reference number of a return; leave "" if unknown.
        original_loyalty_entry_id: The reference number of the points entry a deduction takes back; leave "" if unknown.
    """
    match = {k: v for k, v in {"loyalty_entry_id": loyalty_entry_id,
                               "membership_id": membership_id,
                               "customer_id": customer_id,
                               "purchase_id": purchase_id,
                               "card_txn_id": card_txn_id,
                               "return_id": return_id,
                               "original_loyalty_entry_id": original_loyalty_entry_id}.items() if v}
    rows = ctx.find("loyalty_points_ledger", **match)
    return str(rows) if rows else f"No loyalty_points_ledger records for {match}."


@tool(owner="agent", rw="read")
def find_loyalty_note_ledger(ctx: ToolContext, note_txn_id: str = "", membership_id: str = "", customer_id: str = "", purchase_id: str = "", return_id: str = "") -> str:
    """Look up the Finch Notes of a membership: each note issued (code, value, reason, issue and expiry dates), redeemed on a purchase, or lapsed. Search by any reference number you already hold; every criterion is optional and the records matching all the criteria given are returned, or a notice when none match.

    Args:
        note_txn_id: The reference number of a Finch Note entry; leave "" if unknown.
        membership_id: The reference number of the Finch Circle membership; leave "" if unknown.
        customer_id: The customer reference number; leave "" if unknown.
        purchase_id: The reference number of a purchase record (one unit of one item bought); leave "" if unknown.
        return_id: The reference number of a return; leave "" if unknown.
    """
    match = {k: v for k, v in {"note_txn_id": note_txn_id,
                               "membership_id": membership_id,
                               "customer_id": customer_id,
                               "purchase_id": purchase_id,
                               "return_id": return_id}.items() if v}
    rows = ctx.find("loyalty_note_ledger", **match)
    return str(rows) if rows else f"No loyalty_note_ledger records for {match}."


@tool(owner="agent", rw="read")
def find_loyalty_benefit_ledger(ctx: ToolContext, benefit_txn_id: str = "", membership_id: str = "", customer_id: str = "", ticket_id: str = "") -> str:
    """Look up the Finch Circle alteration credit history of a membership: annual grants and top-ups, credit used on or restored from alteration tickets, and credit that lapsed. Search by any reference number you already hold; every criterion is optional and the records matching all the criteria given are returned, or a notice when none match.

    Args:
        benefit_txn_id: The reference number of an alteration credit entry; leave "" if unknown.
        membership_id: The reference number of the Finch Circle membership; leave "" if unknown.
        customer_id: The customer reference number; leave "" if unknown.
        ticket_id: The reference number of an alteration ticket; leave "" if unknown.
    """
    match = {k: v for k, v in {"benefit_txn_id": benefit_txn_id,
                               "membership_id": membership_id,
                               "customer_id": customer_id,
                               "ticket_id": ticket_id}.items() if v}
    rows = ctx.find("loyalty_benefit_ledger", **match)
    return str(rows) if rows else f"No loyalty_benefit_ledger records for {match}."


@tool(owner="agent", rw="read")
def find_loyalty_requests(ctx: ToolContext, loyalty_request_id: str = "", customer_id: str = "", membership_id: str = "", purchase_id: str = "") -> str:
    """Look up Finch Circle service requests (missing points, expired note reissue, membership cancellation) and their processing status. Search by any reference number you already hold; every criterion is optional and the records matching all the criteria given are returned, or a notice when none match.

    Args:
        loyalty_request_id: The reference number of a Finch Circle service request; leave "" if unknown.
        customer_id: The customer reference number; leave "" if unknown.
        membership_id: The reference number of the Finch Circle membership; leave "" if unknown.
        purchase_id: The reference number of a purchase record (one unit of one item bought); leave "" if unknown.
    """
    match = {k: v for k, v in {"loyalty_request_id": loyalty_request_id,
                               "customer_id": customer_id,
                               "membership_id": membership_id,
                               "purchase_id": purchase_id}.items() if v}
    rows = ctx.find("loyalty_requests", **match)
    return str(rows) if rows else f"No loyalty_requests records for {match}."


@tool(owner="agent", rw="read")
def find_purchases(ctx: ToolContext, purchase_id: str = "", customer_id: str = "", card_account_id: str = "", registry_id: str = "") -> str:
    """Look up purchase records: each unit bought in store, online, in the app or by phone, with its order or receipt number, merchandise class and status, dates of purchase, shipment, delivery or pickup, cancellation and return, prices and price type, tax, Finch Notes applied, tender, the card account or gift registry involved, and the amount paid that has not been refunded. Search by any reference number you already hold; every criterion is optional and the records matching all the criteria given are returned, or a notice when none match.

    Args:
        purchase_id: The reference number of a purchase record (one unit of one item bought); leave "" if unknown.
        customer_id: The customer reference number; leave "" if unknown.
        card_account_id: The reference number of the Marlowe & Finch card account; leave "" if unknown.
        registry_id: The reference number of a gift registry; leave "" if unknown.
    """
    match = {k: v for k, v in {"purchase_id": purchase_id,
                               "customer_id": customer_id,
                               "card_account_id": card_account_id,
                               "registry_id": registry_id}.items() if v}
    rows = ctx.find("purchases", **match)
    return str(rows) if rows else f"No purchases records for {match}."


@tool(owner="agent", rw="read")
def find_order_events(ctx: ToolContext, order_event_id: str = "", purchase_id: str = "", customer_id: str = "", return_id: str = "", replacement_purchase_id: str = "") -> str:
    """Look up the payment, price adjustment, refund and mattress comfort exchange records of purchases, with dates, amounts, the lower price used, refund destination and tender, and any fees deducted. Search by any reference number you already hold; every criterion is optional and the records matching all the criteria given are returned, or a notice when none match.

    Args:
        order_event_id: The reference number of a payment, price adjustment or refund record of a purchase; leave "" if unknown.
        purchase_id: The reference number of a purchase record (one unit of one item bought); leave "" if unknown.
        customer_id: The customer reference number; leave "" if unknown.
        return_id: The reference number of a return; leave "" if unknown.
        replacement_purchase_id: The reference number of the replacement mattress purchase in a comfort exchange; leave "" if unknown.
    """
    match = {k: v for k, v in {"order_event_id": order_event_id,
                               "purchase_id": purchase_id,
                               "customer_id": customer_id,
                               "return_id": return_id,
                               "replacement_purchase_id": replacement_purchase_id}.items() if v}
    rows = ctx.find("order_events", **match)
    return str(rows) if rows else f"No order_events records for {match}."


@tool(owner="agent", rw="read")
def find_return_requests(ctx: ToolContext, return_id: str = "", customer_id: str = "", purchase_id: str = "") -> str:
    """Look up returns: the unit being returned, return method and reason, proof of purchase, condition, processing status and when the return was authorized. Search by any reference number you already hold; every criterion is optional and the records matching all the criteria given are returned, or a notice when none match.

    Args:
        return_id: The reference number of a return; leave "" if unknown.
        customer_id: The customer reference number; leave "" if unknown.
        purchase_id: The reference number of a purchase record (one unit of one item bought); leave "" if unknown.
    """
    match = {k: v for k, v in {"return_id": return_id,
                               "customer_id": customer_id,
                               "purchase_id": purchase_id}.items() if v}
    rows = ctx.find("return_requests", **match)
    return str(rows) if rows else f"No return_requests records for {match}."


@tool(owner="agent", rw="read")
def find_registries(ctx: ToolContext, registry_id: str = "", customer_id: str = "") -> str:
    """Look up gift registries: registry type and status, registry number, current and original event dates, number of date changes, creation and closing dates, co-registrant, visibility, and the registry rewards and registry credit balances. Search by any reference number you already hold; every criterion is optional and the records matching all the criteria given are returned, or a notice when none match.

    Args:
        registry_id: The reference number of a gift registry; leave "" if unknown.
        customer_id: The customer reference number; leave "" if unknown.
    """
    match = {k: v for k, v in {"registry_id": registry_id,
                               "customer_id": customer_id}.items() if v}
    rows = ctx.find("registries", **match)
    return str(rows) if rows else f"No registries records for {match}."


@tool(owner="agent", rw="read")
def find_registry_events(ctx: ToolContext, registry_event_id: str = "", registry_id: str = "", customer_id: str = "", purchase_id: str = "", return_id: str = "") -> str:
    """Look up the entries of a gift registry: items added, guest gifts, completion purchases, registry rewards accrued, reversed, paid out or forfeited, and registry credit received, spent or converted. Search by any reference number you already hold; every criterion is optional and the records matching all the criteria given are returned, or a notice when none match.

    Args:
        registry_event_id: The reference number of a registry entry; leave "" if unknown.
        registry_id: The reference number of a gift registry; leave "" if unknown.
        customer_id: The customer reference number; leave "" if unknown.
        purchase_id: The reference number of a purchase record (one unit of one item bought); leave "" if unknown.
        return_id: The reference number of a return; leave "" if unknown.
    """
    match = {k: v for k, v in {"registry_event_id": registry_event_id,
                               "registry_id": registry_id,
                               "customer_id": customer_id,
                               "purchase_id": purchase_id,
                               "return_id": return_id}.items() if v}
    rows = ctx.find("registry_events", **match)
    return str(rows) if rows else f"No registry_events records for {match}."


@tool(owner="agent", rw="read")
def find_registry_requests(ctx: ToolContext, registry_request_id: str = "", customer_id: str = "", registry_id: str = "", purchase_id: str = "") -> str:
    """Look up gift registry service requests (cancellation, linking a gift, rewards inquiry) and their processing status. Search by any reference number you already hold; every criterion is optional and the records matching all the criteria given are returned, or a notice when none match.

    Args:
        registry_request_id: The reference number of a registry service request; leave "" if unknown.
        customer_id: The customer reference number; leave "" if unknown.
        registry_id: The reference number of a gift registry; leave "" if unknown.
        purchase_id: The reference number of a purchase record (one unit of one item bought); leave "" if unknown.
    """
    match = {k: v for k, v in {"registry_request_id": registry_request_id,
                               "customer_id": customer_id,
                               "registry_id": registry_id,
                               "purchase_id": purchase_id}.items() if v}
    rows = ctx.find("registry_requests", **match)
    return str(rows) if rows else f"No registry_requests records for {match}."


@tool(owner="agent", rw="read")
def find_alteration_tickets(ctx: ToolContext, ticket_id: str = "", customer_id: str = "", purchase_id: str = "") -> str:
    """Look up alteration tickets: service class and status, ticket number, garment, the Marlowe & Finch purchase of the garment, drop-off, promised, needed-by, ready, pickup and cancellation dates, rush service, quoted total, remakes and balance due. Search by any reference number you already hold; every criterion is optional and the records matching all the criteria given are returned, or a notice when none match.

    Args:
        ticket_id: The reference number of an alteration ticket; leave "" if unknown.
        customer_id: The customer reference number; leave "" if unknown.
        purchase_id: The reference number of a purchase record (one unit of one item bought); leave "" if unknown.
    """
    match = {k: v for k, v in {"ticket_id": ticket_id,
                               "customer_id": customer_id,
                               "purchase_id": purchase_id}.items() if v}
    rows = ctx.find("alteration_tickets", **match)
    return str(rows) if rows else f"No alteration_tickets records for {match}."


@tool(owner="agent", rw="read")
def find_alteration_charges(ctx: ToolContext, alteration_charge_id: str = "", ticket_id: str = "", customer_id: str = "", original_alteration_charge_id: str = "") -> str:
    """Look up the charges, waivers, payments, refunds and damage settlements of alteration tickets, with dates, amounts, operations and tenders. Search by any reference number you already hold; every criterion is optional and the records matching all the criteria given are returned, or a notice when none match.

    Args:
        alteration_charge_id: The reference number of an alteration charge, waiver, payment or refund; leave "" if unknown.
        ticket_id: The reference number of an alteration ticket; leave "" if unknown.
        customer_id: The customer reference number; leave "" if unknown.
        original_alteration_charge_id: The reference number of the charge waived or payment refunded; leave "" if unknown.
    """
    match = {k: v for k, v in {"alteration_charge_id": alteration_charge_id,
                               "ticket_id": ticket_id,
                               "customer_id": customer_id,
                               "original_alteration_charge_id": original_alteration_charge_id}.items() if v}
    rows = ctx.find("alteration_charges", **match)
    return str(rows) if rows else f"No alteration_charges records for {match}."


@tool(owner="agent", rw="read")
def find_deliveries(ctx: ToolContext, delivery_id: str = "", customer_id: str = "") -> str:
    """Look up home delivery bookings: service level and status, order number, address, booking and delivery dates, arrival window, items, stairs, distance, haul-away, attempts, reschedules, cancellation and the net delivery charges. Search by any reference number you already hold; every criterion is optional and the records matching all the criteria given are returned, or a notice when none match.

    Args:
        delivery_id: The reference number of a home delivery booking; leave "" if unknown.
        customer_id: The customer reference number; leave "" if unknown.
    """
    match = {k: v for k, v in {"delivery_id": delivery_id,
                               "customer_id": customer_id}.items() if v}
    rows = ctx.find("deliveries", **match)
    return str(rows) if rows else f"No deliveries records for {match}."


@tool(owner="agent", rw="read")
def find_delivery_events(ctx: ToolContext, delivery_event_id: str = "", delivery_id: str = "", customer_id: str = "", original_delivery_event_id: str = "") -> str:
    """Look up the charges and credits billed on home delivery bookings, with dates, amounts and their kinds or reasons. Search by any reference number you already hold; every criterion is optional and the records matching all the criteria given are returned, or a notice when none match.

    Args:
        delivery_event_id: The reference number of a delivery charge or credit; leave "" if unknown.
        delivery_id: The reference number of a home delivery booking; leave "" if unknown.
        customer_id: The customer reference number; leave "" if unknown.
        original_delivery_event_id: The reference number of the delivery charge a credit applies to; leave "" if unknown.
    """
    match = {k: v for k, v in {"delivery_event_id": delivery_event_id,
                               "delivery_id": delivery_id,
                               "customer_id": customer_id,
                               "original_delivery_event_id": original_delivery_event_id}.items() if v}
    rows = ctx.find("delivery_events", **match)
    return str(rows) if rows else f"No delivery_events records for {match}."


@tool(owner="agent", rw="read")
def find_delivery_claims(ctx: ToolContext, delivery_claim_id: str = "", customer_id: str = "", delivery_id: str = "", purchase_id: str = "") -> str:
    """Look up delivery claims for home damage or missing or damaged items and their processing status. Search by any reference number you already hold; every criterion is optional and the records matching all the criteria given are returned, or a notice when none match.

    Args:
        delivery_claim_id: The reference number of a delivery claim; leave "" if unknown.
        customer_id: The customer reference number; leave "" if unknown.
        delivery_id: The reference number of a home delivery booking; leave "" if unknown.
        purchase_id: The reference number of a purchase record (one unit of one item bought); leave "" if unknown.
    """
    match = {k: v for k, v in {"delivery_claim_id": delivery_claim_id,
                               "customer_id": customer_id,
                               "delivery_id": delivery_id,
                               "purchase_id": purchase_id}.items() if v}
    rows = ctx.find("delivery_claims", **match)
    return str(rows) if rows else f"No delivery_claims records for {match}."


@tool(owner="agent", rw="read")
def find_gift_cards(ctx: ToolContext, gift_card_id: str = "", customer_id: str = "") -> str:
    """Look up gift cards and store-value cards (gift, eGift, merchandise credit, registry reward, corporate and bonus cards): card kind and status, card number, issue, activation, expiry, freeze and closing dates, registration and balance. Search by any reference number you already hold; every criterion is optional and the records matching all the criteria given are returned, or a notice when none match.

    Args:
        gift_card_id: The reference number of a gift card record (one card number); leave "" if unknown.
        customer_id: The customer reference number; leave "" if unknown.
    """
    match = {k: v for k, v in {"gift_card_id": gift_card_id,
                               "customer_id": customer_id}.items() if v}
    rows = ctx.find("gift_cards", **match)
    return str(rows) if rows else f"No gift_cards records for {match}."


@tool(owner="agent", rw="read")
def find_gift_card_ledger(ctx: ToolContext, gc_txn_id: str = "", gift_card_id: str = "", customer_id: str = "", return_id: str = "", registry_id: str = "", purchase_id: str = "", counterpart_gift_card_id: str = "") -> str:
    """Look up the history of a gift card: value issued, reloaded, redeemed, transferred, cashed out, expired or forfeited. Search by any reference number you already hold; every criterion is optional and the records matching all the criteria given are returned, or a notice when none match.

    Args:
        gc_txn_id: The reference number of a gift card entry; leave "" if unknown.
        gift_card_id: The reference number of a gift card record (one card number); leave "" if unknown.
        customer_id: The customer reference number; leave "" if unknown.
        return_id: The reference number of a return; leave "" if unknown.
        registry_id: The reference number of a gift registry; leave "" if unknown.
        purchase_id: The reference number of a purchase record (one unit of one item bought); leave "" if unknown.
        counterpart_gift_card_id: The reference number of the other card in a balance transfer; leave "" if unknown.
    """
    match = {k: v for k, v in {"gc_txn_id": gc_txn_id,
                               "gift_card_id": gift_card_id,
                               "customer_id": customer_id,
                               "return_id": return_id,
                               "registry_id": registry_id,
                               "purchase_id": purchase_id,
                               "counterpart_gift_card_id": counterpart_gift_card_id}.items() if v}
    rows = ctx.find("gift_card_ledger", **match)
    return str(rows) if rows else f"No gift_card_ledger records for {match}."


@tool(owner="agent", rw="write")
def verify_customer_identity(ctx: ToolContext, customer_id: str, phone_number: str = "", email: str = "",
                             date_of_birth: str = "", ssn_last4: str = "", billing_zip: str = "") -> str:
    """Confirm that the caller is the customer on the profile, and record the result. Identity must be confirmed before any account information is discussed or any change is made. This tool makes the comparison itself: it checks each detail the caller gives against the profile and confirms identity when at least 2 of them match. The customer reference number only tells the tool which profile to compare with and never counts as a match. Pass only the details the caller actually stated, exactly as stated, and leave the others empty. The result is recorded; if a first attempt falls short and a later attempt with more details succeeds, the customer stays confirmed.

    Args:
        customer_id: The customer reference number from the customer profile lookup. Required; used only to retrieve the profile.
        phone_number: The registered mobile number the caller states, 10 digits; leave "" if not stated.
        email: The registered email address the caller states; leave "" if not stated.
        date_of_birth: The caller's date of birth as YYYY-MM-DD; leave "" if not stated.
        ssn_last4: The last four digits of the caller's Social Security number; leave "" if not stated.
        billing_zip: The 5-digit ZIP code of the caller's billing address; leave "" if not stated.
    """
    if not customer_id:
        return "Error: customer_id is required; find the customer profile first and pass its reference number."
    rows = ctx.find("customers", customer_id=customer_id)
    if not rows:
        return f"Error: no customer {customer_id}; cannot verify."
    rec = rows[0]
    supplied = {"phone_number": phone_number, "email": email, "date_of_birth": date_of_birth,
                "ssn_last4": ssn_last4, "billing_zip": billing_zip}
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
    return (f"Identity verified for {customer_id} ({matched} detail(s) matched)." if verified
            else f"Identity NOT verified for {customer_id} (only {matched} of the 2 required details matched). Ask the caller for another detail on file and try again.")


@tool(owner="agent", rw="write")
def transfer_to_human_agent(ctx: ToolContext, customer_id: str, reason: str) -> str:
    """Hand the customer over to a human representative and record the transfer and its reason. Use it when no Marlowe & Finch policy lets you resolve what the customer is asking for, or when the customer has explicitly asked for a human representative at least 2 times in the conversation.

    Args:
        customer_id: The customer reference number from the customer profile lookup; the profile must exist.
        reason: Why the customer is being transferred; exactly one of POLICY_NOT_COVERED (no policy offers a way to resolve the request) or CUSTOMER_REQUESTED (the customer has explicitly asked for a human representative at least 2 times).
    """
    allowed = {"POLICY_NOT_COVERED", "CUSTOMER_REQUESTED"}
    if reason not in allowed:
        return f"Error: unknown transfer reason '{reason}'. Valid: {', '.join(sorted(allowed))}."
    if not ctx.find("customers", customer_id=customer_id):
        return f"Error: no customer {customer_id}; cannot record the transfer."
    rid = ctx.make_id("hof_", customer_id, reason)
    ctx.create("handoffs", rid, handoff_id=rid, customer_id=customer_id, reason=reason, created_at=ctx.now())
    return f"Transfer to a human representative recorded for {customer_id} ({reason})."

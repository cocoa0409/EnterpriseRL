"""Shared tools for env_0080_big_box_general_merchandise_retailer (Northgate Stores customer care).

Every tool here is always available. It holds the record-lookup layer (one lookup per kind of
record, the customer lookup doubling as the identity entry), the identity-verification write and the
transfer to a human representative. Customer-initiated actions live in each difficulty's task tools.
"""

from erlbench import ToolContext, tool


@tool(owner="agent", rw="read")
def find_verification_log(ctx: ToolContext, verification_id: str = "", customer_id: str = "") -> str:
    """Look up the identity-verification outcome recorded for a customer: whether the caller's identity has been confirmed and when it was last checked.

    Every reference number below is optional; supply whichever are known. All matching records are
    returned in full; when nothing matches, a short notice says so.

    Args:
        verification_id: The reference number of the verification record itself. Leave "" if unknown.
        customer_id: The customer reference number the records belong to. Leave "" if unknown.
    """
    match = {k: v for k, v in {"verification_id": verification_id, "customer_id": customer_id}.items() if v}
    rows = ctx.find("verification_log", **match)
    return str(rows) if rows else f"No verification_log records for {match}."


@tool(owner="agent", rw="read")
def find_handoff_log(ctx: ToolContext, handoff_id: str = "", customer_id: str = "") -> str:
    """Look up the handoffs to a human representative recorded for a customer, with the reason and the moment of each handoff.

    Every reference number below is optional; supply whichever are known. All matching records are
    returned in full; when nothing matches, a short notice says so.

    Args:
        handoff_id: The reference number of the handoff record itself. Leave "" if unknown.
        customer_id: The customer reference number the records belong to. Leave "" if unknown.
    """
    match = {k: v for k, v in {"handoff_id": handoff_id, "customer_id": customer_id}.items() if v}
    rows = ctx.find("handoff_log", **match)
    return str(rows) if rows else f"No handoff_log records for {match}."


@tool(owner="agent", rw="read")
def find_membership_holdings(ctx: ToolContext, membership_id: str = "", customer_id: str = "", card_account_id: str = "") -> str:
    """Look up a customer's Northgate Rewards or Northgate+ membership: the tier, status, enrollment, trial and term dates, renewal date, billing cycle, auto-renew setting, how fees are paid, eligibility verification, payment hold date, household members and seats, and the Northgate Cash balance.

    Every reference number below is optional; supply whichever are known. All matching records are
    returned in full; when nothing matches, a short notice says so.

    Args:
        membership_id: The reference number of the membership. Leave "" if unknown.
        customer_id: The customer reference number the records belong to. Leave "" if unknown.
        card_account_id: The reference number of a Northgate Card account. Leave "" if unknown.
    """
    match = {k: v for k, v in {"membership_id": membership_id, "customer_id": customer_id, "card_account_id": card_account_id}.items() if v}
    rows = ctx.find("membership_holdings", **match)
    return str(rows) if rows else f"No membership_holdings records for {match}."


@tool(owner="agent", rw="read")
def find_membership_events(ctx: ToolContext, membership_event_id: str = "", membership_id: str = "", customer_id: str = "", card_account_id: str = "", original_event_id: str = "", order_id: str = "", source_order_event_id: str = "") -> str:
    """Look up the history of a membership: fee charges, declined fee attempts, fee refunds, recorded uses of delivery and pickup benefits, and Northgate Cash earnings, redemptions, reversals and expirations, each with its date and amount.

    Every reference number below is optional; supply whichever are known. All matching records are
    returned in full; when nothing matches, a short notice says so.

    Args:
        membership_event_id: The reference number of one membership history entry. Leave "" if unknown.
        membership_id: The reference number of the membership. Leave "" if unknown.
        customer_id: The customer reference number the records belong to. Leave "" if unknown.
        card_account_id: The reference number of a Northgate Card account. Leave "" if unknown.
        original_event_id: The reference number of the earlier history entry this entry refers back to (the fee a refund refunds, or the earning a reversal or expiry reduces). Leave "" if unknown.
        order_id: The reference number of a Northgate order. Leave "" if unknown.
        source_order_event_id: The reference number of the order line or return that caused this entry. Leave "" if unknown.
    """
    match = {k: v for k, v in {"membership_event_id": membership_event_id, "membership_id": membership_id, "customer_id": customer_id, "card_account_id": card_account_id, "original_event_id": original_event_id, "order_id": order_id, "source_order_event_id": source_order_event_id}.items() if v}
    rows = ctx.find("membership_events", **match)
    return str(rows) if rows else f"No membership_events records for {match}."


@tool(owner="agent", rw="read")
def find_membership_requests(ctx: ToolContext, membership_request_id: str = "", customer_id: str = "", membership_id: str = "") -> str:
    """Look up cancellation and auto-renew requests recorded on a membership, with what was asked for and whether the member confirmed it.

    Every reference number below is optional; supply whichever are known. All matching records are
    returned in full; when nothing matches, a short notice says so.

    Args:
        membership_request_id: The reference number of one membership request. Leave "" if unknown.
        customer_id: The customer reference number the records belong to. Leave "" if unknown.
        membership_id: The reference number of the membership. Leave "" if unknown.
    """
    match = {k: v for k, v in {"membership_request_id": membership_request_id, "customer_id": customer_id, "membership_id": membership_id}.items() if v}
    rows = ctx.find("membership_requests", **match)
    return str(rows) if rows else f"No membership_requests records for {match}."


@tool(owner="agent", rw="read")
def find_card_holdings(ctx: ToolContext, card_account_id: str = "", customer_id: str = "") -> str:
    """Look up a customer's Northgate Card accounts and applications: the card tier, status, application, opening, decline and closing dates, credit limit, statement closing day, last four digits, current and disputed balances, security deposit, autopay setting, suspension details and authorized users.

    Every reference number below is optional; supply whichever are known. All matching records are
    returned in full; when nothing matches, a short notice says so.

    Args:
        card_account_id: The reference number of a Northgate Card account. Leave "" if unknown.
        customer_id: The customer reference number the records belong to. Leave "" if unknown.
    """
    match = {k: v for k, v in {"card_account_id": card_account_id, "customer_id": customer_id}.items() if v}
    rows = ctx.find("card_holdings", **match)
    return str(rows) if rows else f"No card_holdings records for {match}."


@tool(owner="agent", rw="read")
def find_card_events(ctx: ToolContext, card_event_id: str = "", card_account_id: str = "", customer_id: str = "", source_record_id: str = "", original_event_id: str = "") -> str:
    """Look up the activity on a Northgate Card account: purchases and cash advances, merchant credits, payments and returned payments, interest and fees with any reversals, statements with minimum due and due date, disputes with their credits and outcomes, reward credits, credit balance refunds and security deposits.

    Every reference number below is optional; supply whichever are known. All matching records are
    returned in full; when nothing matches, a short notice says so.

    Args:
        card_event_id: The reference number of one card account activity entry. Leave "" if unknown.
        card_account_id: The reference number of a Northgate Card account. Leave "" if unknown.
        customer_id: The customer reference number the records belong to. Leave "" if unknown.
        source_record_id: The reference number of the Northgate record the entry relates to, such as an order, a marketplace order, a membership or a protection plan. Leave "" if unknown.
        original_event_id: The reference number of the earlier history entry this entry refers back to (the fee a refund refunds, or the earning a reversal or expiry reduces). Leave "" if unknown.
    """
    match = {k: v for k, v in {"card_event_id": card_event_id, "card_account_id": card_account_id, "customer_id": customer_id, "source_record_id": source_record_id, "original_event_id": original_event_id}.items() if v}
    rows = ctx.find("card_events", **match)
    return str(rows) if rows else f"No card_events records for {match}."


@tool(owner="agent", rw="read")
def find_card_requests(ctx: ToolContext, card_request_id: str = "", customer_id: str = "", card_account_id: str = "") -> str:
    """Look up requests recorded on a Northgate Card account, such as closing the account or refunding a credit balance, with whether the cardholder confirmed them.

    Every reference number below is optional; supply whichever are known. All matching records are
    returned in full; when nothing matches, a short notice says so.

    Args:
        card_request_id: The reference number of one card account request. Leave "" if unknown.
        customer_id: The customer reference number the records belong to. Leave "" if unknown.
        card_account_id: The reference number of a Northgate Card account. Leave "" if unknown.
    """
    match = {k: v for k, v in {"card_request_id": card_request_id, "customer_id": customer_id, "card_account_id": card_account_id}.items() if v}
    rows = ctx.find("card_requests", **match)
    return str(rows) if rows else f"No card_requests records for {match}."


@tool(owner="agent", rw="read")
def find_plan_holdings(ctx: ToolContext, plan_id: str = "", customer_id: str = "", covered_order_id: str = "", covered_order_event_id: str = "", card_account_id: str = "") -> str:
    """Look up a customer's Northgate Protect plans: the plan tier, status, purchase date, coverage start and end, the covered order and item with its category and price, how the plan is paid, the amount paid and the remaining limit of liability.

    Every reference number below is optional; supply whichever are known. All matching records are
    returned in full; when nothing matches, a short notice says so.

    Args:
        plan_id: The reference number of a Northgate Protect plan. Leave "" if unknown.
        customer_id: The customer reference number the records belong to. Leave "" if unknown.
        covered_order_id: The reference number of the order containing the covered item. Leave "" if unknown.
        covered_order_event_id: The reference number of the order line of the covered item. Leave "" if unknown.
        card_account_id: The reference number of a Northgate Card account. Leave "" if unknown.
    """
    match = {k: v for k, v in {"plan_id": plan_id, "customer_id": customer_id, "covered_order_id": covered_order_id, "covered_order_event_id": covered_order_event_id, "card_account_id": card_account_id}.items() if v}
    rows = ctx.find("plan_holdings", **match)
    return str(rows) if rows else f"No plan_holdings records for {match}."


@tool(owner="agent", rw="read")
def find_plan_events(ctx: ToolContext, plan_event_id: str = "", plan_id: str = "", customer_id: str = "", card_account_id: str = "", original_event_id: str = "", covered_order_event_id: str = "") -> str:
    """Look up the history of a Northgate Protect plan: plan charges and declined monthly fees, refunds, registered items, claims filed with their incident dates, claim decisions with service fees, and settlements by repair, replacement or reimbursement.

    Every reference number below is optional; supply whichever are known. All matching records are
    returned in full; when nothing matches, a short notice says so.

    Args:
        plan_event_id: The reference number of one plan history entry (for a claim, its claim reference). Leave "" if unknown.
        plan_id: The reference number of a Northgate Protect plan. Leave "" if unknown.
        customer_id: The customer reference number the records belong to. Leave "" if unknown.
        card_account_id: The reference number of a Northgate Card account. Leave "" if unknown.
        original_event_id: The reference number of the earlier history entry this entry refers back to (the fee a refund refunds, or the earning a reversal or expiry reduces). Leave "" if unknown.
        covered_order_event_id: The reference number of the order line of the covered item. Leave "" if unknown.
    """
    match = {k: v for k, v in {"plan_event_id": plan_event_id, "plan_id": plan_id, "customer_id": customer_id, "card_account_id": card_account_id, "original_event_id": original_event_id, "covered_order_event_id": covered_order_event_id}.items() if v}
    rows = ctx.find("plan_events", **match)
    return str(rows) if rows else f"No plan_events records for {match}."


@tool(owner="agent", rw="read")
def find_plan_requests(ctx: ToolContext, plan_request_id: str = "", customer_id: str = "", plan_id: str = "") -> str:
    """Look up requests recorded on a Northgate Protect plan, such as a cancellation, with whether the plan holder confirmed them.

    Every reference number below is optional; supply whichever are known. All matching records are
    returned in full; when nothing matches, a short notice says so.

    Args:
        plan_request_id: The reference number of one plan request. Leave "" if unknown.
        customer_id: The customer reference number the records belong to. Leave "" if unknown.
        plan_id: The reference number of a Northgate Protect plan. Leave "" if unknown.
    """
    match = {k: v for k, v in {"plan_request_id": plan_request_id, "customer_id": customer_id, "plan_id": plan_id}.items() if v}
    rows = ctx.find("plan_requests", **match)
    return str(rows) if rows else f"No plan_requests records for {match}."


@tool(owner="agent", rw="read")
def find_order_holdings(ctx: ToolContext, order_id: str = "", customer_id: str = "", card_account_id: str = "") -> str:
    """Look up a customer's Northgate orders and register purchases: the fulfilment program, status, order date, channel, store, order or receipt number, tender, scheduled delivery date, ready, fulfilled, canceled and returned dates, and the net amount paid.

    Every reference number below is optional; supply whichever are known. All matching records are
    returned in full; when nothing matches, a short notice says so.

    Args:
        order_id: The reference number of a Northgate order. Leave "" if unknown.
        customer_id: The customer reference number the records belong to. Leave "" if unknown.
        card_account_id: The reference number of a Northgate Card account. Leave "" if unknown.
    """
    match = {k: v for k, v in {"order_id": order_id, "customer_id": customer_id, "card_account_id": card_account_id}.items() if v}
    rows = ctx.find("order_holdings", **match)
    return str(rows) if rows else f"No order_holdings records for {match}."


@tool(owner="agent", rw="read")
def find_order_events(ctx: ToolContext, order_event_id: str = "", order_id: str = "", customer_id: str = "", original_event_id: str = "", plan_id: str = "", card_account_id: str = "") -> str:
    """Look up the lines and money movements of a Northgate order: each item line with its category, return class, quantity, prices, discounts and warranty, delivery and other fees with any waiver, returns with their reason, receipt type and refund method, price adjustments and price matches, and refunds made without a return.

    Every reference number below is optional; supply whichever are known. All matching records are
    returned in full; when nothing matches, a short notice says so.

    Args:
        order_event_id: The reference number of one order line or order money movement. Leave "" if unknown.
        order_id: The reference number of a Northgate order. Leave "" if unknown.
        customer_id: The customer reference number the records belong to. Leave "" if unknown.
        original_event_id: The reference number of the earlier history entry this entry refers back to (the fee a refund refunds, or the earning a reversal or expiry reduces). Leave "" if unknown.
        plan_id: The reference number of a Northgate Protect plan. Leave "" if unknown.
        card_account_id: The reference number of a Northgate Card account. Leave "" if unknown.
    """
    match = {k: v for k, v in {"order_event_id": order_event_id, "order_id": order_id, "customer_id": customer_id, "original_event_id": original_event_id, "plan_id": plan_id, "card_account_id": card_account_id}.items() if v}
    rows = ctx.find("order_events", **match)
    return str(rows) if rows else f"No order_events records for {match}."


@tool(owner="agent", rw="read")
def find_order_requests(ctx: ToolContext, order_request_id: str = "", customer_id: str = "", order_id: str = "") -> str:
    """Look up requests recorded on a Northgate order, such as a cancellation, a delivery reschedule or a return pickup, with whether the customer confirmed them.

    Every reference number below is optional; supply whichever are known. All matching records are
    returned in full; when nothing matches, a short notice says so.

    Args:
        order_request_id: The reference number of one order request. Leave "" if unknown.
        customer_id: The customer reference number the records belong to. Leave "" if unknown.
        order_id: The reference number of a Northgate order. Leave "" if unknown.
    """
    match = {k: v for k, v in {"order_request_id": order_request_id, "customer_id": customer_id, "order_id": order_id}.items() if v}
    rows = ctx.find("order_requests", **match)
    return str(rows) if rows else f"No order_requests records for {match}."


@tool(owner="agent", rw="read")
def find_market_holdings(ctx: ToolContext, market_order_id: str = "", customer_id: str = "", card_account_id: str = "") -> str:
    """Look up a customer's Northgate Marketplace orders: the seller program, status, seller, marketplace order number, order date, maximum estimated delivery date, shipping and tracking, delivery, cancellation and refund dates, how the order was paid and the net amount paid.

    Every reference number below is optional; supply whichever are known. All matching records are
    returned in full; when nothing matches, a short notice says so.

    Args:
        market_order_id: The reference number of a Northgate Marketplace order. Leave "" if unknown.
        customer_id: The customer reference number the records belong to. Leave "" if unknown.
        card_account_id: The reference number of a Northgate Card account. Leave "" if unknown.
    """
    match = {k: v for k, v in {"market_order_id": market_order_id, "customer_id": customer_id, "card_account_id": card_account_id}.items() if v}
    rows = ctx.find("market_holdings", **match)
    return str(rows) if rows else f"No market_holdings records for {match}."


@tool(owner="agent", rw="read")
def find_market_events(ctx: ToolContext, market_event_id: str = "", market_order_id: str = "", customer_id: str = "", original_event_id: str = "", card_account_id: str = "") -> str:
    """Look up the history of a Northgate Marketplace order: item lines and shipping charges, return requests and seller responses, seller refunds, messages to the seller, Northgate Marketplace Guarantee claims with their decisions, and guarantee reimbursements.

    Every reference number below is optional; supply whichever are known. All matching records are
    returned in full; when nothing matches, a short notice says so.

    Args:
        market_event_id: The reference number of one marketplace order history entry (for a claim, its claim reference). Leave "" if unknown.
        market_order_id: The reference number of a Northgate Marketplace order. Leave "" if unknown.
        customer_id: The customer reference number the records belong to. Leave "" if unknown.
        original_event_id: The reference number of the earlier history entry this entry refers back to (the fee a refund refunds, or the earning a reversal or expiry reduces). Leave "" if unknown.
        card_account_id: The reference number of a Northgate Card account. Leave "" if unknown.
    """
    match = {k: v for k, v in {"market_event_id": market_event_id, "market_order_id": market_order_id, "customer_id": customer_id, "original_event_id": original_event_id, "card_account_id": card_account_id}.items() if v}
    rows = ctx.find("market_events", **match)
    return str(rows) if rows else f"No market_events records for {match}."


@tool(owner="agent", rw="read")
def find_market_requests(ctx: ToolContext, market_request_id: str = "", customer_id: str = "", market_order_id: str = "") -> str:
    """Look up requests recorded on a Northgate Marketplace order, such as a cancellation request or a guarantee claim request, with whether the buyer confirmed them.

    Every reference number below is optional; supply whichever are known. All matching records are
    returned in full; when nothing matches, a short notice says so.

    Args:
        market_request_id: The reference number of one marketplace request. Leave "" if unknown.
        customer_id: The customer reference number the records belong to. Leave "" if unknown.
        market_order_id: The reference number of a Northgate Marketplace order. Leave "" if unknown.
    """
    match = {k: v for k, v in {"market_request_id": market_request_id, "customer_id": customer_id, "market_order_id": market_order_id}.items() if v}
    rows = ctx.find("market_requests", **match)
    return str(rows) if rows else f"No market_requests records for {match}."


@tool(owner="agent", rw="read")
def find_trade_holdings(ctx: ToolContext, trade_account_id: str = "", customer_id: str = "") -> str:
    """Look up a business's Northgate Business invoice account: the terms tier, status, organization type, application, opening and closing dates, credit line, credit hold, tax exemption certificate and outstanding balance.

    Every reference number below is optional; supply whichever are known. All matching records are
    returned in full; when nothing matches, a short notice says so.

    Args:
        trade_account_id: The reference number of a Northgate Business invoice account. Leave "" if unknown.
        customer_id: The customer reference number the records belong to. Leave "" if unknown.
    """
    match = {k: v for k, v in {"trade_account_id": trade_account_id, "customer_id": customer_id}.items() if v}
    rows = ctx.find("trade_holdings", **match)
    return str(rows) if rows else f"No trade_holdings records for {match}."


@tool(owner="agent", rw="read")
def find_trade_events(ctx: ToolContext, trade_event_id: str = "", trade_account_id: str = "", customer_id: str = "", order_id: str = "", original_event_id: str = "") -> str:
    """Look up the activity on a Northgate Business invoice account: invoices with purchase order numbers and due dates, payments and returned payments, credit memos, late charges and waivers, returned payment fees, early-payment discounts and sales tax credits.

    Every reference number below is optional; supply whichever are known. All matching records are
    returned in full; when nothing matches, a short notice says so.

    Args:
        trade_event_id: The reference number of one invoice account activity entry. Leave "" if unknown.
        trade_account_id: The reference number of a Northgate Business invoice account. Leave "" if unknown.
        customer_id: The customer reference number the records belong to. Leave "" if unknown.
        order_id: The reference number of a Northgate order. Leave "" if unknown.
        original_event_id: The reference number of the earlier history entry this entry refers back to (the fee a refund refunds, or the earning a reversal or expiry reduces). Leave "" if unknown.
    """
    match = {k: v for k, v in {"trade_event_id": trade_event_id, "trade_account_id": trade_account_id, "customer_id": customer_id, "order_id": order_id, "original_event_id": original_event_id}.items() if v}
    rows = ctx.find("trade_events", **match)
    return str(rows) if rows else f"No trade_events records for {match}."


@tool(owner="agent", rw="read")
def find_gift_holdings(ctx: ToolContext, gift_card_id: str = "", customer_id: str = "", replaced_by_gift_card_id: str = "") -> str:
    """Look up a customer's Northgate gift cards, eGift cards and merchandise return cards: the card type, status, last four digits, issue date and reason, initial value, activation and expiration dates, registration, freeze details, replacement card and current balance.

    Every reference number below is optional; supply whichever are known. All matching records are
    returned in full; when nothing matches, a short notice says so.

    Args:
        gift_card_id: The reference number of a gift card. Leave "" if unknown.
        customer_id: The customer reference number the records belong to. Leave "" if unknown.
        replaced_by_gift_card_id: The reference number of the replacement card that received a card's balance. Leave "" if unknown.
    """
    match = {k: v for k, v in {"gift_card_id": gift_card_id, "customer_id": customer_id, "replaced_by_gift_card_id": replaced_by_gift_card_id}.items() if v}
    rows = ctx.find("gift_holdings", **match)
    return str(rows) if rows else f"No gift_holdings records for {match}."


@tool(owner="agent", rw="read")
def find_gift_events(ctx: ToolContext, gift_event_id: str = "", gift_card_id: str = "", customer_id: str = "", source_record_id: str = "", original_event_id: str = "", counterpart_gift_card_id: str = "") -> str:
    """Look up the activity on a Northgate gift card: loads and reloads, purchases paid with the card, refunds credited back, expired promotional value, balance transfers and voided value.

    Every reference number below is optional; supply whichever are known. All matching records are
    returned in full; when nothing matches, a short notice says so.

    Args:
        gift_event_id: The reference number of one gift card activity entry. Leave "" if unknown.
        gift_card_id: The reference number of a gift card. Leave "" if unknown.
        customer_id: The customer reference number the records belong to. Leave "" if unknown.
        source_record_id: The reference number of the Northgate record the entry relates to, such as an order, a marketplace order, a membership or a protection plan. Leave "" if unknown.
        original_event_id: The reference number of the earlier history entry this entry refers back to (the fee a refund refunds, or the earning a reversal or expiry reduces). Leave "" if unknown.
        counterpart_gift_card_id: The reference number of the card that received a balance transfer. Leave "" if unknown.
    """
    match = {k: v for k, v in {"gift_event_id": gift_event_id, "gift_card_id": gift_card_id, "customer_id": customer_id, "source_record_id": source_record_id, "original_event_id": original_event_id, "counterpart_gift_card_id": counterpart_gift_card_id}.items() if v}
    rows = ctx.find("gift_events", **match)
    return str(rows) if rows else f"No gift_events records for {match}."


@tool(owner="agent", rw="read")
def find_customers(ctx: ToolContext, customer_id: str = "", phone: str = "", email: str = "", name: str = "", business_name: str = "") -> str:
    """Look up a Northgate customer profile to establish whose account this conversation is about.

    A profile can be found by its customer reference number or by what a caller can naturally tell
    you: the registered mobile number, the sign-in email, the full name, or, for a business account,
    the registered business name. Every criterion is optional; give whichever the caller has stated.
    A found profile shows the name, whether it is a consumer or business profile, the business name,
    contact details, date of birth, billing ZIP code, billing state, the date the profile was opened
    and the preferred store. Finding a profile does not confirm that the caller is its owner; identity
    is confirmed separately.

    Args:
        customer_id: The customer reference number, if already known. Leave "" if unknown.
        phone: The registered mobile number as the caller states it, 10 digits. Leave "" if not provided.
        email: The registered sign-in email as the caller states it. Leave "" if not provided.
        name: The customer's full name as the caller states it. Leave "" if not provided.
        business_name: The registered business name of a business account. Leave "" if not provided.
    """
    match = {k: v for k, v in {"customer_id": customer_id, "phone": phone, "email": email,
                               "name": name, "business_name": business_name}.items() if v}
    if not match:
        return "Error: provide at least one reference number or profile detail to find the customer."
    rows = ctx.fuzzy_find("customers", **match)
    if not rows:
        return f"No customer matches {match}."
    if len(rows) > 1:
        return f"Error: {len(rows)} customers match {match}; ask for one more detail to tell them apart."
    return str(rows[0])


@tool(owner="agent", rw="write")
def verify_customer_identity(ctx: ToolContext, customer_id: str, phone: str = "", email: str = "", date_of_birth: str = "", billing_zip: str = "", profile_opened_date: str = "") -> str:
    """Confirm that the caller is the owner of a Northgate customer profile and record the outcome.

    Identity must be confirmed before any account details are discussed or any business is done on
    the customer's memberships, cards, plans or orders. This tool performs the comparison itself: it
    checks each detail the caller states against the profile on file, counts how many agree, and
    confirms identity only when at least 2 details agree. The customer reference number only tells
    the tool which profile to compare against and never counts as a matching detail. Callers usually
    give only some details, so pass exactly what was stated and leave the rest blank. The outcome is
    recorded; if a first attempt falls short and a later attempt with more details succeeds, the
    successful confirmation stands.

    Args:
        customer_id: The customer reference number read from the customer profile lookup. Required; used only to retrieve that profile and not counted as a matching detail.
        phone: The registered mobile number the caller states, 10 digits with no punctuation. Leave "" if not stated.
        email: The registered sign-in email the caller states, exactly as given. Leave "" if not stated.
        date_of_birth: The date of birth the caller states (for a business account, the administrator's), formatted YYYY-MM-DD. Leave "" if not stated.
        billing_zip: The 5-digit ZIP code of the billing address the caller states. Leave "" if not stated.
        profile_opened_date: The date the caller says the Northgate profile was opened, formatted YYYY-MM-DD. Leave "" if not stated.
    """
    if not customer_id:
        return "Error: customer_id is required; look the customer up first and pass their reference number."
    rows = ctx.find("customers", customer_id=customer_id)
    if not rows:
        return f"Error: no customer {customer_id}; cannot verify."
    rec = rows[0]
    # the locator customer_id is deliberately not part of `supplied`
    supplied = {"phone": phone, "email": email, "date_of_birth": date_of_birth,
                "billing_zip": billing_zip, "profile_opened_date": profile_opened_date}
    matched = sum(1 for field, value in supplied.items()
                  if value and str(rec.get(field, "")).strip().lower() == str(value).strip().lower())
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
    """Hand the customer over to a human Northgate representative and record why.

    Use POLICY_NOT_COVERED when no Northgate policy allows the request to be resolved in this
    conversation. Use CUSTOMER_REQUESTED when the customer has explicitly asked to speak with a human
    representative at least 2 times. The handoff is recorded with the moment it was made.

    Args:
        customer_id: The customer reference number read from the customer profile lookup; the profile must exist.
        reason: Why the customer is being handed over; exactly one of POLICY_NOT_COVERED or CUSTOMER_REQUESTED, never free text.
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

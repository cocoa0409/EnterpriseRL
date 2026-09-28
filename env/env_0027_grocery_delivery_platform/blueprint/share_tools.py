"""Shared tools for env_0027_grocery_delivery_platform (Cartwise). Output of the erl-scenario-blueprint skill.

Every tool here is a SHARE tool, always present in its owner's tool list:
  - one lookup per record type (each takes every reference number the record carries, all optional);
    the customer-profile lookup doubles as the identity entry (mobile number, email, name);
  - the identity-verification write (compares the stated credentials itself; passes at 2 matches);
  - the handoff-to-human write (exactly two reasons: POLICY_NOT_COVERED, CUSTOMER_REQUESTED).
Customer- and shopper-originated writes live in each difficulty's task_tools.py as hidden user tools.
"""

from erlbench import ToolContext, tool


@tool(owner="agent", rw="read")
def find_verification_records(ctx: ToolContext, verification_id: str = "", customer_id: str = "") -> str:
    """Look up identity-verification outcomes recorded for customers: whether a caller's identity was verified and when the latest attempt was made.

    Every reference number below is optional; supply whichever you already hold and all matching records
    are returned. Supplying none returns every record of this kind.

    Args:
        verification_id: The reference number of an identity-verification record; leave "" if unknown.
        customer_id: The customer reference number of the person the record belongs to (the profile's own number on a customer profile); leave "" if unknown.
    """
    match = {k: v for k, v in {"verification_id": verification_id, "customer_id": customer_id}.items() if v}
    rows = ctx.find("verification_log", **match)
    return str(rows) if rows else f"No verification_log records for {match}."

@tool(owner="agent", rw="read")
def find_handoff_records(ctx: ToolContext, handoff_id: str = "", customer_id: str = "") -> str:
    """Look up handoffs to human representatives: which customer was handed over, for which of the two recognised reasons, and when.

    Every reference number below is optional; supply whichever you already hold and all matching records
    are returned. Supplying none returns every record of this kind.

    Args:
        handoff_id: The reference number of a handoff to a human representative; leave "" if unknown.
        customer_id: The customer reference number of the person the record belongs to (the profile's own number on a customer profile); leave "" if unknown.
    """
    match = {k: v for k, v in {"handoff_id": handoff_id, "customer_id": customer_id}.items() if v}
    rows = ctx.find("handoff_log", **match)
    return str(rows) if rows else f"No handoff_log records for {match}."

@tool(owner="agent", rw="read")
def find_memberships(ctx: ToolContext, membership_id: str = "", customer_id: str = "") -> str:
    """Look up Cartwise+ memberships: the plan held, its status, enrollment and trial dates, the current paid period and renewal date, auto-renew, past-due, pause and cancellation details, the Cartwise+ credit balance and the Priority Delivery upgrades remaining.

    Every reference number below is optional; supply whichever you already hold and all matching records
    are returned. Supplying none returns every record of this kind.

    Args:
        membership_id: The Cartwise+ membership reference number; leave "" if unknown.
        customer_id: The customer reference number of the person the record belongs to (the profile's own number on a customer profile); leave "" if unknown.
    """
    match = {k: v for k, v in {"membership_id": membership_id, "customer_id": customer_id}.items() if v}
    rows = ctx.find("memberships", **match)
    return str(rows) if rows else f"No memberships records for {match}."

@tool(owner="agent", rw="read")
def find_membership_events(ctx: ToolContext, membership_event_id: str = "", membership_id: str = "", customer_id: str = "", order_id: str = "", source_event_id: str = "", member_customer_id: str = "") -> str:
    """Look up the entries on a Cartwise+ membership: period fee charges and refunds, credit earned, applied and expired, Priority Delivery upgrades granted and used, and household members added or removed, each with its amount or quantity and date.

    Every reference number below is optional; supply whichever you already hold and all matching records
    are returned. Supplying none returns every record of this kind.

    Args:
        membership_event_id: The reference number of one membership billing, refund, credit or upgrade entry; leave "" if unknown.
        membership_id: The Cartwise+ membership reference number; leave "" if unknown.
        customer_id: The customer reference number of the person the record belongs to (the profile's own number on a customer profile); leave "" if unknown.
        order_id: The order number; leave "" if unknown.
        source_event_id: The reference number of the original membership entry that this entry refunds or expires (a period fee charge or a credit earning); leave "" if unknown.
        member_customer_id: The customer reference number of a household member who was added to or removed from a membership; leave "" if unknown.
    """
    match = {k: v for k, v in {"membership_event_id": membership_event_id, "membership_id": membership_id, "customer_id": customer_id, "order_id": order_id, "source_event_id": source_event_id, "member_customer_id": member_customer_id}.items() if v}
    rows = ctx.find("membership_events", **match)
    return str(rows) if rows else f"No membership_events records for {match}."

@tool(owner="agent", rw="read")
def find_membership_requests(ctx: ToolContext, membership_request_id: str = "", customer_id: str = "", membership_id: str = "") -> str:
    """Look up membership requests registered for a customer (immediate cancellation, cancellation at period end, turning auto-renew back on, plan switch) and whether each is pending the customer's confirmation, confirmed or withdrawn.

    Every reference number below is optional; supply whichever you already hold and all matching records
    are returned. Supplying none returns every record of this kind.

    Args:
        membership_request_id: The reference number of a membership request awaiting the customer's confirmation; leave "" if unknown.
        customer_id: The customer reference number of the person the record belongs to (the profile's own number on a customer profile); leave "" if unknown.
        membership_id: The Cartwise+ membership reference number; leave "" if unknown.
    """
    match = {k: v for k, v in {"membership_request_id": membership_request_id, "customer_id": customer_id, "membership_id": membership_id}.items() if v}
    rows = ctx.find("membership_requests", **match)
    return str(rows) if rows else f"No membership_requests records for {match}."

@tool(owner="agent", rw="read")
def find_orders(ctx: ToolContext, order_id: str = "", customer_id: str = "", membership_id: str = "", batch_id: str = "") -> str:
    """Look up grocery orders: service level, store, status, checkout date, booked window, reschedules used, the membership judged at checkout, the batch that shopped it, handoff time, cancellation, return and closing details, and the current tip.

    Every reference number below is optional; supply whichever you already hold and all matching records
    are returned. Supplying none returns every record of this kind.

    Args:
        order_id: The order number; leave "" if unknown.
        customer_id: The customer reference number of the person the record belongs to (the profile's own number on a customer profile); leave "" if unknown.
        membership_id: The Cartwise+ membership reference number; leave "" if unknown.
        batch_id: The batch number of a shopper batch; leave "" if unknown.
    """
    match = {k: v for k, v in {"order_id": order_id, "customer_id": customer_id, "membership_id": membership_id, "batch_id": batch_id}.items() if v}
    rows = ctx.find("orders", **match)
    return str(rows) if rows else f"No orders records for {match}."

@tool(owner="agent", rw="read")
def find_order_events(ctx: ToolContext, order_event_id: str = "", order_id: str = "", customer_id: str = "", source_event_id: str = "", batch_id: str = "") -> str:
    """Look up the entries on an order: each billed item line (product, category, requested and billed quantity, original and billed unit price, substitution outcome), substitution decisions, fees billed or waived and the benefit behind a waiver, item and fee refunds with their reason and destination, and tip entries.

    Every reference number below is optional; supply whichever you already hold and all matching records
    are returned. Supplying none returns every record of this kind.

    Args:
        order_event_id: The reference number of one order line, fee, refund or tip entry; leave "" if unknown.
        order_id: The order number; leave "" if unknown.
        customer_id: The customer reference number of the person the record belongs to (the profile's own number on a customer profile); leave "" if unknown.
        source_event_id: The reference number of the original order entry (item line or fee) that this refund pays back; leave "" if unknown.
        batch_id: The batch number of a shopper batch; leave "" if unknown.
    """
    match = {k: v for k, v in {"order_event_id": order_event_id, "order_id": order_id, "customer_id": customer_id, "source_event_id": source_event_id, "batch_id": batch_id}.items() if v}
    rows = ctx.find("order_events", **match)
    return str(rows) if rows else f"No order_events records for {match}."

@tool(owner="agent", rw="read")
def find_order_review_requests(ctx: ToolContext, order_review_request_id: str = "", customer_id: str = "", order_id: str = "") -> str:
    """Look up refund requests sent to the review team for an order line, why each needed review, the amount sent for review and the review outcome.

    Every reference number below is optional; supply whichever you already hold and all matching records
    are returned. Supplying none returns every record of this kind.

    Args:
        order_review_request_id: The reference number of a refund request sent to the review team; leave "" if unknown.
        customer_id: The customer reference number of the person the record belongs to (the profile's own number on a customer profile); leave "" if unknown.
        order_id: The order number; leave "" if unknown.
    """
    match = {k: v for k, v in {"order_review_request_id": order_review_request_id, "customer_id": customer_id, "order_id": order_id}.items() if v}
    rows = ctx.find("order_review_requests", **match)
    return str(rows) if rows else f"No order_review_requests records for {match}."

@tool(owner="agent", rw="read")
def find_shopper_accounts(ctx: ToolContext, shopper_account_id: str = "", customer_id: str = "") -> str:
    """Look up shopper contractor accounts: shopper level, status, application, background-check and activation dates, licence and insurance expiry dates, open rating warning, hold, deactivation, reactivation and closure details, and active violation points.

    Every reference number below is optional; supply whichever you already hold and all matching records
    are returned. Supplying none returns every record of this kind.

    Args:
        shopper_account_id: The shopper contractor account number; leave "" if unknown.
        customer_id: The customer reference number of the person the record belongs to (the profile's own number on a customer profile); leave "" if unknown.
    """
    match = {k: v for k, v in {"shopper_account_id": shopper_account_id, "customer_id": customer_id}.items() if v}
    rows = ctx.find("shopper_accounts", **match)
    return str(rows) if rows else f"No shopper_accounts records for {match}."

@tool(owner="agent", rw="read")
def find_shopper_events(ctx: ToolContext, shopper_event_id: str = "", shopper_account_id: str = "", customer_id: str = "", order_id: str = "", batch_id: str = "", source_event_id: str = "") -> str:
    """Look up the entries on a shopper account: customer ratings per order, rating exclusions and their reason, violations with their type and points, and violations cleared with their reason.

    Every reference number below is optional; supply whichever you already hold and all matching records
    are returned. Supplying none returns every record of this kind.

    Args:
        shopper_event_id: The reference number of one rating, rating exclusion or violation entry; leave "" if unknown.
        shopper_account_id: The shopper contractor account number; leave "" if unknown.
        customer_id: The customer reference number of the person the record belongs to (the profile's own number on a customer profile); leave "" if unknown.
        order_id: The order number; leave "" if unknown.
        batch_id: The batch number of a shopper batch; leave "" if unknown.
        source_event_id: The reference number of the rating or violation entry that this entry excludes or clears; leave "" if unknown.
    """
    match = {k: v for k, v in {"shopper_event_id": shopper_event_id, "shopper_account_id": shopper_account_id, "customer_id": customer_id, "order_id": order_id, "batch_id": batch_id, "source_event_id": source_event_id}.items() if v}
    rows = ctx.find("shopper_events", **match)
    return str(rows) if rows else f"No shopper_events records for {match}."

@tool(owner="agent", rw="read")
def find_shopper_appeals(ctx: ToolContext, shopper_appeal_id: str = "", customer_id: str = "", shopper_account_id: str = "", source_event_id: str = "") -> str:
    """Look up appeals and violation disputes a shopper has submitted, what each concerns and its decision.

    Every reference number below is optional; supply whichever you already hold and all matching records
    are returned. Supplying none returns every record of this kind.

    Args:
        shopper_appeal_id: The reference number of a shopper's appeal or violation dispute; leave "" if unknown.
        customer_id: The customer reference number of the person the record belongs to (the profile's own number on a customer profile); leave "" if unknown.
        shopper_account_id: The shopper contractor account number; leave "" if unknown.
        source_event_id: The reference number of the violation entry a dispute concerns; leave "" if unknown.
    """
    match = {k: v for k, v in {"shopper_appeal_id": shopper_appeal_id, "customer_id": customer_id, "shopper_account_id": shopper_account_id, "source_event_id": source_event_id}.items() if v}
    rows = ctx.find("shopper_appeals", **match)
    return str(rows) if rows else f"No shopper_appeals records for {match}."

@tool(owner="agent", rw="read")
def find_batches(ctx: ToolContext, batch_id: str = "", customer_id: str = "", shopper_account_id: str = "") -> str:
    """Look up shopper batches: batch type, status, store, acceptance and shopping start times, orders and item units, estimated and driven miles, waiting minutes, the pay shown on the offer, drop, cancellation, completion and finalization details, and the batch's earnings.

    Every reference number below is optional; supply whichever you already hold and all matching records
    are returned. Supplying none returns every record of this kind.

    Args:
        batch_id: The batch number of a shopper batch; leave "" if unknown.
        customer_id: The customer reference number of the person the record belongs to (the profile's own number on a customer profile); leave "" if unknown.
        shopper_account_id: The shopper contractor account number; leave "" if unknown.
    """
    match = {k: v for k, v in {"batch_id": batch_id, "customer_id": customer_id, "shopper_account_id": shopper_account_id}.items() if v}
    rows = ctx.find("batches", **match)
    return str(rows) if rows else f"No batches records for {match}."

@tool(owner="agent", rw="read")
def find_batch_events(ctx: ToolContext, batch_event_id: str = "", batch_id: str = "", customer_id: str = "", order_id: str = "", batch_pay_dispute_id: str = "", source_event_id: str = "") -> str:
    """Look up the earnings entries on a batch: each pay component posted, tips posted and changed, approved pay adjustments with their reason and dispute, and pay reversals with their ground.

    Every reference number below is optional; supply whichever you already hold and all matching records
    are returned. Supplying none returns every record of this kind.

    Args:
        batch_event_id: The reference number of one batch pay, tip, adjustment or reversal entry; leave "" if unknown.
        batch_id: The batch number of a shopper batch; leave "" if unknown.
        customer_id: The customer reference number of the person the record belongs to (the profile's own number on a customer profile); leave "" if unknown.
        order_id: The order number; leave "" if unknown.
        batch_pay_dispute_id: The reference number of a shopper's pay dispute; leave "" if unknown.
        source_event_id: The reference number of the pay entry that a reversal takes back; leave "" if unknown.
    """
    match = {k: v for k, v in {"batch_event_id": batch_event_id, "batch_id": batch_id, "customer_id": customer_id, "order_id": order_id, "batch_pay_dispute_id": batch_pay_dispute_id, "source_event_id": source_event_id}.items() if v}
    rows = ctx.find("batch_events", **match)
    return str(rows) if rows else f"No batch_events records for {match}."

@tool(owner="agent", rw="read")
def find_batch_pay_disputes(ctx: ToolContext, batch_pay_dispute_id: str = "", customer_id: str = "", batch_id: str = "") -> str:
    """Look up pay disputes shoppers have submitted on batches: the reason, the amount claimed and where each dispute stands.

    Every reference number below is optional; supply whichever you already hold and all matching records
    are returned. Supplying none returns every record of this kind.

    Args:
        batch_pay_dispute_id: The reference number of a shopper's pay dispute; leave "" if unknown.
        customer_id: The customer reference number of the person the record belongs to (the profile's own number on a customer profile); leave "" if unknown.
        batch_id: The batch number of a shopper batch; leave "" if unknown.
    """
    match = {k: v for k, v in {"batch_pay_dispute_id": batch_pay_dispute_id, "customer_id": customer_id, "batch_id": batch_id}.items() if v}
    rows = ctx.find("batch_pay_disputes", **match)
    return str(rows) if rows else f"No batch_pay_disputes records for {match}."

@tool(owner="agent", rw="read")
def find_payout_accounts(ctx: ToolContext, payout_account_id: str = "", customer_id: str = "", shopper_account_id: str = "") -> str:
    """Look up shopper payout accounts: payout plan, status, setup and verification dates, the last four digits and change time of the payout destination, freeze and closure details, the unpaid earnings balance and the card cashback balance.

    Every reference number below is optional; supply whichever you already hold and all matching records
    are returned. Supplying none returns every record of this kind.

    Args:
        payout_account_id: The shopper payout account number; leave "" if unknown.
        customer_id: The customer reference number of the person the record belongs to (the profile's own number on a customer profile); leave "" if unknown.
        shopper_account_id: The shopper contractor account number; leave "" if unknown.
    """
    match = {k: v for k, v in {"payout_account_id": payout_account_id, "customer_id": customer_id, "shopper_account_id": shopper_account_id}.items() if v}
    rows = ctx.find("payout_accounts", **match)
    return str(rows) if rows else f"No payout_accounts records for {match}."

@tool(owner="agent", rw="read")
def find_payout_events(ctx: ToolContext, payout_event_id: str = "", payout_account_id: str = "", customer_id: str = "", batch_id: str = "", batch_event_id: str = "", source_event_id: str = "") -> str:
    """Look up the entries on a payout account: batch earnings credited and debited, weekly deposits, instant cashouts and their fees, returned transfers, fee refunds, and card cashback earned and paid.

    Every reference number below is optional; supply whichever you already hold and all matching records
    are returned. Supplying none returns every record of this kind.

    Args:
        payout_event_id: The reference number of one payout balance, deposit, cashout, fee or cashback entry; leave "" if unknown.
        payout_account_id: The shopper payout account number; leave "" if unknown.
        customer_id: The customer reference number of the person the record belongs to (the profile's own number on a customer profile); leave "" if unknown.
        batch_id: The batch number of a shopper batch; leave "" if unknown.
        batch_event_id: The reference number of one batch pay, tip, adjustment or reversal entry; leave "" if unknown.
        source_event_id: The reference number of the related payout entry (the cashout a fee belongs to, the transfer that came back, or the fee refunded); leave "" if unknown.
    """
    match = {k: v for k, v in {"payout_event_id": payout_event_id, "payout_account_id": payout_account_id, "customer_id": customer_id, "batch_id": batch_id, "batch_event_id": batch_event_id, "source_event_id": source_event_id}.items() if v}
    rows = ctx.find("payout_events", **match)
    return str(rows) if rows else f"No payout_events records for {match}."

@tool(owner="agent", rw="read")
def find_payout_requests(ctx: ToolContext, payout_request_id: str = "", customer_id: str = "", payout_account_id: str = "") -> str:
    """Look up payout requests registered for a shopper (closing the account, changing plan, changing destination) and whether each is pending the shopper's confirmation, confirmed or withdrawn.

    Every reference number below is optional; supply whichever you already hold and all matching records
    are returned. Supplying none returns every record of this kind.

    Args:
        payout_request_id: The reference number of a payout request awaiting the shopper's confirmation; leave "" if unknown.
        customer_id: The customer reference number of the person the record belongs to (the profile's own number on a customer profile); leave "" if unknown.
        payout_account_id: The shopper payout account number; leave "" if unknown.
    """
    match = {k: v for k, v in {"payout_request_id": payout_request_id, "customer_id": customer_id, "payout_account_id": payout_account_id}.items() if v}
    rows = ctx.find("payout_requests", **match)
    return str(rows) if rows else f"No payout_requests records for {match}."

@tool(owner="agent", rw="read")
def find_giftcards(ctx: ToolContext, giftcard_id: str = "", customer_id: str = "") -> str:
    """Look up Cartwise gift cards: card type, status, last four digits, purchase, activation, expiry and registration dates, suspension, depletion and closure details, and the remaining balance.

    Every reference number below is optional; supply whichever you already hold and all matching records
    are returned. Supplying none returns every record of this kind.

    Args:
        giftcard_id: The gift card reference number; leave "" if unknown.
        customer_id: The customer reference number of the person the record belongs to (the profile's own number on a customer profile); leave "" if unknown.
    """
    match = {k: v for k, v in {"giftcard_id": giftcard_id, "customer_id": customer_id}.items() if v}
    rows = ctx.find("giftcards", **match)
    return str(rows) if rows else f"No giftcards records for {match}."

@tool(owner="agent", rw="read")
def find_giftcard_events(ctx: ToolContext, giftcard_event_id: str = "", giftcard_id: str = "", customer_id: str = "", order_id: str = "", source_event_id: str = "", counterpart_giftcard_id: str = "") -> str:
    """Look up the entries on a gift card: loads, redemptions on orders, refunds returned to the card, balance transfers between cards and value removed, each with its amount and date.

    Every reference number below is optional; supply whichever you already hold and all matching records
    are returned. Supplying none returns every record of this kind.

    Args:
        giftcard_event_id: The reference number of one gift card load, redemption, transfer or removal entry; leave "" if unknown.
        giftcard_id: The gift card reference number; leave "" if unknown.
        customer_id: The customer reference number of the person the record belongs to (the profile's own number on a customer profile); leave "" if unknown.
        order_id: The order number; leave "" if unknown.
        source_event_id: The reference number of the order refund entry returned to the card; leave "" if unknown.
        counterpart_giftcard_id: The reference number of the other gift card in a balance transfer; leave "" if unknown.
    """
    match = {k: v for k, v in {"giftcard_event_id": giftcard_event_id, "giftcard_id": giftcard_id, "customer_id": customer_id, "order_id": order_id, "source_event_id": source_event_id, "counterpart_giftcard_id": counterpart_giftcard_id}.items() if v}
    rows = ctx.find("giftcard_events", **match)
    return str(rows) if rows else f"No giftcard_events records for {match}."

@tool(owner="agent", rw="read")
def find_rewards_accounts(ctx: ToolContext, rewards_account_id: str = "", customer_id: str = "") -> str:
    """Look up Cartwise Rewards accounts: tier, status, enrollment, activation, tier-change, suspension and closure dates, and the points balance.

    Every reference number below is optional; supply whichever you already hold and all matching records
    are returned. Supplying none returns every record of this kind.

    Args:
        rewards_account_id: The Cartwise Rewards account number; leave "" if unknown.
        customer_id: The customer reference number of the person the record belongs to (the profile's own number on a customer profile); leave "" if unknown.
    """
    match = {k: v for k, v in {"rewards_account_id": rewards_account_id, "customer_id": customer_id}.items() if v}
    rows = ctx.find("rewards_accounts", **match)
    return str(rows) if rows else f"No rewards_accounts records for {match}."

@tool(owner="agent", rw="read")
def find_rewards_events(ctx: ToolContext, rewards_event_id: str = "", rewards_account_id: str = "", customer_id: str = "", order_id: str = "", source_event_id: str = "") -> str:
    """Look up the entries on a Cartwise Rewards account: points earned and their kind, points redeemed and their value, points restored, reversed and expired.

    Every reference number below is optional; supply whichever you already hold and all matching records
    are returned. Supplying none returns every record of this kind.

    Args:
        rewards_event_id: The reference number of one rewards points entry; leave "" if unknown.
        rewards_account_id: The Cartwise Rewards account number; leave "" if unknown.
        customer_id: The customer reference number of the person the record belongs to (the profile's own number on a customer profile); leave "" if unknown.
        order_id: The order number; leave "" if unknown.
        source_event_id: The reference number of the redemption restored or the order refund entry that caused a points reversal; leave "" if unknown.
    """
    match = {k: v for k, v in {"rewards_event_id": rewards_event_id, "rewards_account_id": rewards_account_id, "customer_id": customer_id, "order_id": order_id, "source_event_id": source_event_id}.items() if v}
    rows = ctx.find("rewards_events", **match)
    return str(rows) if rows else f"No rewards_events records for {match}."

@tool(owner="agent", rw="read")
def find_customers(ctx: ToolContext, customer_id: str = "", phone_number: str = "", email: str = "",
                   name: str = "") -> str:
    """Find the Cartwise profile a call is about. Customers and shoppers both hold a Cartwise profile, so this
    is where every conversation starts: search by the customer reference number, or by what the caller can
    tell you — the registered mobile number, the registered email address or the full name on the profile.
    Every criterion is optional; give whichever are known. A match returns the profile with its customer
    reference number, name, mobile number, email, date of birth, home ZIP code and state, and the date the
    profile was opened. Finding a profile only locates it; it does not confirm that the caller is its owner.

    Args:
        customer_id: The customer reference number, when already known; leave "" if unknown.
        phone_number: The mobile number registered on the profile, 10 digits, as the caller states it; leave "" if not provided.
        email: The email address registered on the profile, as the caller states it; leave "" if not provided.
        name: The full name on the profile, as the caller states it; leave "" if not provided.
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


@tool(owner="agent", rw="write")
def verify_customer_identity(ctx: ToolContext, customer_id: str, phone_number: str = "", email: str = "",
                             date_of_birth: str = "", zip_code: str = "") -> str:
    """Confirm that the caller owns the Cartwise profile before any account detail is discussed or any
    change is made on it, and record the outcome. This tool makes the comparison itself: it checks each
    detail the caller states against the profile on file, counts how many agree, and confirms the caller
    only when at least 2 of them agree. The customer reference number only tells the tool which profile to
    check and never counts as one of the matching details. Callers usually know only some details, so pass
    exactly what the caller said and leave the rest blank. The outcome is kept on the profile; if a first
    attempt falls short and a later attempt with more details succeeds, the caller stands confirmed.

    Args:
        customer_id: The customer reference number of the profile being checked, read from the profile lookup. Required; used only to find the profile and not counted as a match.
        phone_number: The mobile number the caller states, 10 digits without punctuation; leave "" if not stated.
        email: The email address the caller states, exactly as given; leave "" if not stated.
        date_of_birth: The date of birth the caller states, in YYYY-MM-DD form; leave "" if not stated.
        zip_code: The 5-digit ZIP code of the home address the caller states; leave "" if not stated.
    """
    if not customer_id:
        return "Error: customer_id is required; find the customer profile first and pass its reference number."
    rows = ctx.find("customers", customer_id=customer_id)
    if not rows:
        return f"Error: no customer {customer_id}; cannot verify."
    rec = rows[0]
    # The tool owns the comparison; customer_id is the locator and never counts toward the match.
    supplied = {"phone_number": phone_number, "email": email, "date_of_birth": date_of_birth, "zip_code": zip_code}
    matched = sum(1 for field, value in supplied.items()
                  if value and str(rec.get(field) or "").strip().lower() == str(value).strip().lower())
    verified = matched >= 2
    rid = ctx.make_id("ver_", customer_id)
    # Store only the reproducible boolean; upsert and never downgrade True -> False.
    prior = ctx.find("verification_log", verification_id=rid)
    verified = verified or bool(prior and prior[0].get("verified"))
    if prior:
        ctx.update("verification_log", rid, verified=verified, verified_at=ctx.now())
    else:
        ctx.create("verification_log", rid, verification_id=rid, customer_id=customer_id,
                   verified=verified, verified_at=ctx.now())
    if verified:
        return f"Identity verified for {customer_id} ({matched} detail(s) matched)."
    return (f"Identity NOT verified for {customer_id} (only {matched} of the required 2 details matched). "
            "Ask the caller for another detail on file and try again.")


@tool(owner="agent", rw="write")
def transfer_to_human_agent(ctx: ToolContext, customer_id: str, reason: str) -> str:
    """Hand the caller over to a human representative and record the handoff with its reason. Use it in one
    of two situations only: when no Cartwise policy provides a way to resolve what the caller needs, or when
    the caller has explicitly asked to speak with a human representative at least 2 times.

    Args:
        customer_id: The customer reference number of the caller's profile, read from the profile lookup; the profile must exist.
        reason: Why the caller is handed over; exactly one of these two values, never free text.
            POLICY_NOT_COVERED — no Cartwise policy provides a way to resolve the request;
            CUSTOMER_REQUESTED — the caller has explicitly asked for a human representative at least 2 times.
    """
    allowed = {"POLICY_NOT_COVERED", "CUSTOMER_REQUESTED"}
    if reason not in allowed:
        return f"Error: unknown handoff reason '{reason}'. Valid: {', '.join(sorted(allowed))}."
    if not ctx.find("customers", customer_id=customer_id):
        return f"Error: no customer {customer_id}; cannot record the handoff."
    rid = ctx.make_id("hof_", customer_id, reason)
    ctx.create("handoff_log", rid, handoff_id=rid, customer_id=customer_id, reason=reason, created_at=ctx.now())
    return f"Handoff to a human representative recorded for {customer_id} ({reason})."

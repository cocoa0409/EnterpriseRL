"""Shared tools for env_0039_warehouse_club_retailer (Northgate Wholesale Club member services).

Every tool here is a SHARE tool, always available to its owner in every task:
  - one record finder per table in db_schema.json (the customers finder doubles as the identity entry),
  - the identity-verification write (K = 2 matching credentials),
  - the transfer-to-human write (R = 2 explicit requests for CUSTOMER_REQUESTED).
Customer-originated writes and every business write live in the difficulties' task_tools.py.
"""

from erlbench import ToolContext, tool


def _criteria(**kwargs):
    # Keep only the criteria the caller actually supplied.
    return {k: v for k, v in kwargs.items() if v}


# ---------------------------------------------------------------- customer profile (identity entry)

@tool(owner="agent", rw="read")
def find_customers(ctx: ToolContext, customer_id: str = "", phone_number: str = "", email: str = "",
                   name: str = "") -> str:
    """Look up a member-services customer profile to establish whose account this conversation is about.

    A profile can be found by its customer reference number or by what a caller can naturally tell you:
    the phone number on file, the email address on file, or the full name. Every criterion is optional;
    supply whichever you have, and add a second one when a name alone matches more than one person. The
    profile returned shows the customer reference number, full name, phone number, email address, date of
    birth, home ZIP code and the date the profile was opened. Finding a profile does not prove that the
    caller is that person; looking a customer up is not the same as verifying their identity.

    Args:
        customer_id: The customer reference number, if already known; leave "" otherwise.
        phone_number: The phone number the caller gives, 10 digits (spaces, dashes and brackets are ignored); leave "" if not given.
        email: The email address the caller gives; leave "" if not given.
        name: The caller's full name as they state it; leave "" if not given.
    """
    match = _criteria(customer_id=customer_id, phone_number=phone_number, email=email, name=name)
    if not match:
        return "Error: provide at least one id or attribute to find the customer."
    rows = ctx.fuzzy_find("customers", **match)
    if not rows:
        return f"No customer matches {match}."
    if len(rows) > 1:
        return f"Error: {len(rows)} customers match {match}; ask for one more attribute to disambiguate."
    return str(rows[0])


# ---------------------------------------------------------------- memberships

@tool(owner="agent", rw="read")
def find_membership_holdings(ctx: ToolContext, membership_id: str = "", customer_id: str = "",
                             member_number: str = "") -> str:
    """Look up memberships: tier, status, membership number, business name, the current membership year
    (start and expiry dates), the automatic renewal setting and its payment method, the status-verification
    date for Student Club and Heroes Club tiers, and the Annual Reward balance accrued this year.

    Search by the membership reference number, by the owning customer reference number to list every
    membership a person is primary on, or by the 12-digit membership number printed on the card. Every
    criterion is optional; at least one is needed. Returns the matching memberships, or a notice that none
    match.

    Args:
        membership_id: The membership reference number; leave "" if unknown.
        customer_id: The customer reference number of the primary member; leave "" if unknown.
        member_number: The 12-digit membership number from the member's card (spaces ignored); leave "" if not given.
    """
    match = _criteria(membership_id=membership_id, customer_id=customer_id, member_number=member_number)
    if not match:
        return "Error: provide at least one reference to look up memberships."
    rows = ctx.fuzzy_find("membership_holdings", **match) if member_number else ctx.find("membership_holdings", **match)
    return str(rows) if rows else f"No memberships found for {match}."


@tool(owner="agent", rw="read")
def find_membership_transactions(ctx: ToolContext, membership_txn_id: str = "", membership_id: str = "",
                                 customer_id: str = "", membership_card_id: str = "", source_txn_id: str = "",
                                 source_ref_id: str = "") -> str:
    """Look up the membership ledger: membership fees charged (new year, renewal, upgrade, add-on card) and
    refunded, Annual Reward accrued and reversed purchase by purchase, and Annual Reward certificates issued
    and reissued. Each entry shows its date, amount, the membership year it belongs to, how a fee was paid,
    the refund reason, and the purchase or optical charge a reward entry came from. A certificate's
    reference number is the reference number of its issuance entry.

    Search by any reference you hold: the entry itself, the membership, the customer, an add-on card, the
    original entry a refund or reissue points back to, or the order line or optical charge behind a reward
    entry. Every criterion is optional; at least one is needed.

    Args:
        membership_txn_id: The reference number of the ledger entry (or certificate); leave "" if unknown.
        membership_id: The membership reference number; leave "" if unknown.
        customer_id: The customer reference number; leave "" if unknown.
        membership_card_id: The add-on card issuance an add-on fee belongs to; leave "" if unknown.
        source_txn_id: The original fee charge or certificate that a refund or reissue points back to; leave "" if unknown.
        source_ref_id: The order line or optical charge that earned or reversed a reward; leave "" if unknown.
    """
    match = _criteria(membership_txn_id=membership_txn_id, membership_id=membership_id, customer_id=customer_id,
                      membership_card_id=membership_card_id, source_txn_id=source_txn_id, source_ref_id=source_ref_id)
    if not match:
        return "Error: provide at least one reference to look up membership ledger entries."
    rows = ctx.find("membership_transactions", **match)
    return str(rows) if rows else f"No membership ledger entries found for {match}."


@tool(owner="agent", rw="read")
def find_membership_cards(ctx: ToolContext, membership_card_id: str = "", membership_id: str = "",
                          customer_id: str = "", source_card_id: str = "") -> str:
    """Look up the cards on a membership: every card issued (primary, household, business add-on, and
    replacements) and every card deactivated, with the cardholder's name, the date, and the reason for the
    issue or deactivation. A card that has an issuance but no later deactivation pointing to it is still in
    use.

    Search by the card entry's reference number, the membership, the primary member, or the earlier card
    that a replacement or deactivation points back to. Every criterion is optional; at least one is needed.

    Args:
        membership_card_id: The reference number of the card entry; leave "" if unknown.
        membership_id: The membership reference number; leave "" if unknown.
        customer_id: The customer reference number of the primary member; leave "" if unknown.
        source_card_id: The card issuance that a replacement or deactivation refers to; leave "" if unknown.
    """
    match = _criteria(membership_card_id=membership_card_id, membership_id=membership_id,
                      customer_id=customer_id, source_card_id=source_card_id)
    if not match:
        return "Error: provide at least one reference to look up membership cards."
    rows = ctx.find("membership_cards", **match)
    return str(rows) if rows else f"No membership card entries found for {match}."


@tool(owner="agent", rw="read")
def find_membership_requests(ctx: ToolContext, membership_request_id: str = "", customer_id: str = "",
                             membership_id: str = "") -> str:
    """Look up membership change requests taken by member services — cancellations with refund, downgrades
    at renewal and Plus guarantee claims — with the date the member asked, whether the member has confirmed
    or withdrawn it, and when it was recorded.

    Search by the request's reference number, the member, or the membership. Every criterion is optional;
    at least one is needed.

    Args:
        membership_request_id: The request reference number; leave "" if unknown.
        customer_id: The customer reference number of the primary member; leave "" if unknown.
        membership_id: The membership reference number; leave "" if unknown.
    """
    match = _criteria(membership_request_id=membership_request_id, customer_id=customer_id,
                      membership_id=membership_id)
    if not match:
        return "Error: provide at least one reference to look up membership requests."
    rows = ctx.find("membership_requests", **match)
    return str(rows) if rows else f"No membership requests found for {match}."


# ---------------------------------------------------------------- credit cards

@tool(owner="agent", rw="read")
def find_card_holdings(ctx: ToolContext, card_account_id: str = "", customer_id: str = "",
                       linked_membership_id: str = "") -> str:
    """Look up Northgate credit card accounts issued by Meridian Trust Bank: the card product, account
    status, the membership the card is linked to, the last four digits, the credit line, the application
    date, the card rewards earned this reward year, and the closing date if closed.

    Search by the card account reference number, the cardholder, or the linked membership. Every criterion
    is optional; at least one is needed.

    Args:
        card_account_id: The card account reference number; leave "" if unknown.
        customer_id: The customer reference number of the cardholder; leave "" if unknown.
        linked_membership_id: The reference number of the membership the card is linked to; leave "" if unknown.
    """
    match = _criteria(card_account_id=card_account_id, customer_id=customer_id,
                      linked_membership_id=linked_membership_id)
    if not match:
        return "Error: provide at least one reference to look up card accounts."
    rows = ctx.find("card_holdings", **match)
    return str(rows) if rows else f"No card accounts found for {match}."


@tool(owner="agent", rw="read")
def find_card_transactions(ctx: ToolContext, card_txn_id: str = "", card_account_id: str = "",
                           customer_id: str = "", source_txn_id: str = "") -> str:
    """Look up card reward activity: rewards earned and reversed per statement month and earning category
    (with the qualifying spend they were computed on), annual reward certificates issued and reissued, and
    rewards forfeited at closure. A card certificate's reference number is that of its issuance entry.

    Search by the entry, the card account, the cardholder, or the original certificate a reissue points
    back to. Every criterion is optional; at least one is needed.

    Args:
        card_txn_id: The reference number of the reward entry (or certificate); leave "" if unknown.
        card_account_id: The card account reference number; leave "" if unknown.
        customer_id: The customer reference number of the cardholder; leave "" if unknown.
        source_txn_id: The original certificate a reissue refers to; leave "" if unknown.
    """
    match = _criteria(card_txn_id=card_txn_id, card_account_id=card_account_id, customer_id=customer_id,
                      source_txn_id=source_txn_id)
    if not match:
        return "Error: provide at least one reference to look up card reward entries."
    rows = ctx.find("card_transactions", **match)
    return str(rows) if rows else f"No card reward entries found for {match}."


# ---------------------------------------------------------------- purchases and returns

@tool(owner="agent", rw="read")
def find_order_holdings(ctx: ToolContext, order_id: str = "", customer_id: str = "", membership_id: str = "",
                        receipt_number: str = "") -> str:
    """Look up purchases: the purchase channel, status, receipt or order number, club, order and
    fulfillment dates, the tender used, the membership whose card was presented, and the net amount paid
    after returns, adjustments and rebates.

    Search by the purchase reference number, the member, the membership, or the receipt or order number the
    member reads from the receipt. Every criterion is optional; at least one is needed.

    Args:
        order_id: The purchase reference number; leave "" if unknown.
        customer_id: The customer reference number of the buyer; leave "" if unknown.
        membership_id: The membership reference number presented for the purchase; leave "" if unknown.
        receipt_number: The 20-digit receipt or order number as the member reads it (spaces ignored); leave "" if not given.
    """
    match = _criteria(order_id=order_id, customer_id=customer_id, membership_id=membership_id,
                      receipt_number=receipt_number)
    if not match:
        return "Error: provide at least one reference to look up purchases."
    rows = ctx.fuzzy_find("order_holdings", **match) if receipt_number else ctx.find("order_holdings", **match)
    return str(rows) if rows else f"No purchases found for {match}."


@tool(owner="agent", rw="read")
def find_order_lines(ctx: ToolContext, order_line_id: str = "", order_id: str = "", customer_id: str = "",
                     source_order_line_id: str = "", item_price_id: str = "") -> str:
    """Look up the line-level entries of purchases: items sold (item number, description, merchandise
    class, quantity, unit price, whether the line earns Annual Reward), and refunds, price adjustments,
    mail-in rebate credits, order fees and fee refunds posted against them, each with its date and reason.

    Search by the entry itself, the purchase, the member, the sale line that a refund, adjustment, rebate or
    fee points back to, or the price or rebate record an adjustment or rebate was computed from. Every
    criterion is optional; at least one is needed.

    Args:
        order_line_id: The reference number of the line entry; leave "" if unknown.
        order_id: The purchase reference number; leave "" if unknown.
        customer_id: The customer reference number; leave "" if unknown.
        source_order_line_id: The sale line (or fee entry) that a refund, adjustment, rebate or fee refers to; leave "" if unknown.
        item_price_id: The price or rebate record an adjustment or rebate used; leave "" if unknown.
    """
    match = _criteria(order_line_id=order_line_id, order_id=order_id, customer_id=customer_id,
                      source_order_line_id=source_order_line_id, item_price_id=item_price_id)
    if not match:
        return "Error: provide at least one reference to look up purchase lines."
    rows = ctx.find("order_lines", **match)
    return str(rows) if rows else f"No purchase line entries found for {match}."


@tool(owner="agent", rw="read")
def find_order_return_authorizations(ctx: ToolContext, return_authorization_id: str = "", customer_id: str = "",
                                     order_id: str = "", order_line_id: str = "") -> str:
    """Look up return authorizations for merchandise going back to Northgate without a club visit: the sale
    line and quantity covered, the return method (carrier pickup, prepaid label or freight pickup), the date
    the member asked, and whether it is submitted, confirmed by the member, received by the returns center
    or withdrawn.

    Search by the authorization, the member, the purchase, or the sale line. Every criterion is optional;
    at least one is needed.

    Args:
        return_authorization_id: The return authorization reference number; leave "" if unknown.
        customer_id: The customer reference number; leave "" if unknown.
        order_id: The purchase reference number; leave "" if unknown.
        order_line_id: The sale line reference number; leave "" if unknown.
    """
    match = _criteria(return_authorization_id=return_authorization_id, customer_id=customer_id,
                      order_id=order_id, order_line_id=order_line_id)
    if not match:
        return "Error: provide at least one reference to look up return authorizations."
    rows = ctx.find("order_return_authorizations", **match)
    return str(rows) if rows else f"No return authorizations found for {match}."


@tool(owner="agent", rw="read")
def find_item_price_history(ctx: ToolContext, item_price_id: str = "", item_number: str = "") -> str:
    """Look up the price history of a Northgate item: each regular price, Instant Savings promotion,
    clearance price and manufacturer mail-in rebate offer, with the purchase channel it applies to, the
    unit price (or rebate per unit), the dates it runs, any per-membership unit limit, and a rebate's claim
    deadline.

    Search by the price record's reference number or by the item number from the receipt. Every criterion
    is optional; at least one is needed.

    Args:
        item_price_id: The price or offer record reference number; leave "" if unknown.
        item_number: The 6- or 7-digit Northgate item number printed on the receipt; leave "" if unknown.
    """
    match = _criteria(item_price_id=item_price_id, item_number=item_number)
    if not match:
        return "Error: provide an item number or a price record reference."
    rows = ctx.find("item_price_history", **match)
    return str(rows) if rows else f"No price records found for {match}."


# ---------------------------------------------------------------- delivery and installation

@tool(owner="agent", rw="read")
def find_delivery_holdings(ctx: ToolContext, delivery_id: str = "", customer_id: str = "", order_id: str = "") -> str:
    """Look up delivery and installation appointments: the service level, status, booked date and arrival
    window, delivery ZIP code and distance, booking date, how many times it was rescheduled and attempted,
    the crew's logged arrival time and the reason any attempt failed, and the completion or cancellation
    date.

    Search by the appointment, the member, or the purchase being delivered. Every criterion is optional; at
    least one is needed.

    Args:
        delivery_id: The appointment reference number; leave "" if unknown.
        customer_id: The customer reference number; leave "" if unknown.
        order_id: The purchase reference number; leave "" if unknown.
    """
    match = _criteria(delivery_id=delivery_id, customer_id=customer_id, order_id=order_id)
    if not match:
        return "Error: provide at least one reference to look up delivery appointments."
    rows = ctx.find("delivery_holdings", **match)
    return str(rows) if rows else f"No delivery appointments found for {match}."


@tool(owner="agent", rw="read")
def find_delivery_charges(ctx: ToolContext, delivery_charge_id: str = "", delivery_id: str = "",
                          customer_id: str = "", source_charge_id: str = "") -> str:
    """Look up the fees and credits on delivery appointments: base delivery, haul-away, stairs, extra
    distance, installation kits, wall mounting, reschedule and redelivery fees, and the credits posted
    against them, each with its amount, units, posting date, appointment date and credit reason.

    Search by the entry, the appointment, the member, or the charge a credit points back to. Every
    criterion is optional; at least one is needed.

    Args:
        delivery_charge_id: The reference number of the fee or credit entry; leave "" if unknown.
        delivery_id: The appointment reference number; leave "" if unknown.
        customer_id: The customer reference number; leave "" if unknown.
        source_charge_id: The charge a credit refers to; leave "" if unknown.
    """
    match = _criteria(delivery_charge_id=delivery_charge_id, delivery_id=delivery_id, customer_id=customer_id,
                      source_charge_id=source_charge_id)
    if not match:
        return "Error: provide at least one reference to look up delivery fees and credits."
    rows = ctx.find("delivery_charges", **match)
    return str(rows) if rows else f"No delivery fees or credits found for {match}."


@tool(owner="agent", rw="read")
def find_delivery_claims(ctx: ToolContext, delivery_claim_id: str = "", customer_id: str = "",
                         delivery_id: str = "") -> str:
    """Look up claims raised after a delivery — damaged merchandise, damage to the home, faulty
    installation or missing items — with the date reported and whether the claim is submitted, confirmed by
    the member, approved, denied or withdrawn.

    Search by the claim, the member, or the appointment. Every criterion is optional; at least one is
    needed.

    Args:
        delivery_claim_id: The claim reference number; leave "" if unknown.
        customer_id: The customer reference number; leave "" if unknown.
        delivery_id: The appointment reference number; leave "" if unknown.
    """
    match = _criteria(delivery_claim_id=delivery_claim_id, customer_id=customer_id, delivery_id=delivery_id)
    if not match:
        return "Error: provide at least one reference to look up delivery claims."
    rows = ctx.find("delivery_claims", **match)
    return str(rows) if rows else f"No delivery claims found for {match}."


# ---------------------------------------------------------------- Tire Center

@tool(owner="agent", rw="read")
def find_tire_holdings(ctx: ToolContext, tire_service_id: str = "", customer_id: str = "", order_id: str = "") -> str:
    """Look up Tire Center installation packages: the package, status, vehicle, tire size and item number,
    price paid per tire, number of tires, the manufacturer's treadwear mileage warranty, the appointment and
    installation dates, and the odometer at installation.

    Search by the package reference number, the member, or the purchase the tires were bought on. Every
    criterion is optional; at least one is needed.

    Args:
        tire_service_id: The installation package reference number; leave "" if unknown.
        customer_id: The customer reference number; leave "" if unknown.
        order_id: The purchase reference number; leave "" if unknown.
    """
    match = _criteria(tire_service_id=tire_service_id, customer_id=customer_id, order_id=order_id)
    if not match:
        return "Error: provide at least one reference to look up tire packages."
    rows = ctx.find("tire_holdings", **match)
    return str(rows) if rows else f"No tire packages found for {match}."


@tool(owner="agent", rw="read")
def find_tire_services(ctx: ToolContext, tire_event_id: str = "", tire_service_id: str = "", customer_id: str = "",
                       source_event_id: str = "") -> str:
    """Look up Tire Center work on a package: rotations, flat repairs, road hazard replacements and
    treadwear adjustments, with the visit date, odometer, wheel position, measured tread depth and damage
    found, plus every charge and credit posted on the package.

    Search by the entry, the package, the member, or the road hazard, treadwear or charge entry that a
    charge or credit points back to. Every criterion is optional; at least one is needed.

    Args:
        tire_event_id: The reference number of the service, charge or credit entry; leave "" if unknown.
        tire_service_id: The installation package reference number; leave "" if unknown.
        customer_id: The customer reference number; leave "" if unknown.
        source_event_id: The entry a charge or credit refers to; leave "" if unknown.
    """
    match = _criteria(tire_event_id=tire_event_id, tire_service_id=tire_service_id, customer_id=customer_id,
                      source_event_id=source_event_id)
    if not match:
        return "Error: provide at least one reference to look up Tire Center work."
    rows = ctx.find("tire_services", **match)
    return str(rows) if rows else f"No Tire Center entries found for {match}."


# ---------------------------------------------------------------- Optical

@tool(owner="agent", rw="read")
def find_optical_holdings(ctx: ToolContext, optical_order_id: str = "", customer_id: str = "",
                          membership_id: str = "") -> str:
    """Look up prescription eyewear jobs: the lens design, status, prescription issue date, frame, lens
    material, vision plan billed, the membership presented, the order and dispensed dates, and how many
    remakes have been opened.

    Search by the eyewear job, the member, or the membership. Every criterion is optional; at least one is
    needed.

    Args:
        optical_order_id: The eyewear job reference number; leave "" if unknown.
        customer_id: The customer reference number; leave "" if unknown.
        membership_id: The membership reference number presented for the job; leave "" if unknown.
    """
    match = _criteria(optical_order_id=optical_order_id, customer_id=customer_id, membership_id=membership_id)
    if not match:
        return "Error: provide at least one reference to look up eyewear jobs."
    rows = ctx.find("optical_holdings", **match)
    return str(rows) if rows else f"No eyewear jobs found for {match}."


@tool(owner="agent", rw="read")
def find_optical_transactions(ctx: ToolContext, optical_txn_id: str = "", optical_order_id: str = "",
                              customer_id: str = "", source_txn_id: str = "") -> str:
    """Look up the charges and credits on eyewear jobs: frame, lenses, coatings and options, remake
    charges with their remake number and reason, and vision plan allowances, refunds and waived charges,
    each with its date, amount and whether it earns Annual Reward.

    Search by the entry, the eyewear job, the member, or the charge a credit points back to. Every
    criterion is optional; at least one is needed.

    Args:
        optical_txn_id: The reference number of the charge or credit; leave "" if unknown.
        optical_order_id: The eyewear job reference number; leave "" if unknown.
        customer_id: The customer reference number; leave "" if unknown.
        source_txn_id: The charge a credit refers to; leave "" if unknown.
    """
    match = _criteria(optical_txn_id=optical_txn_id, optical_order_id=optical_order_id, customer_id=customer_id,
                      source_txn_id=source_txn_id)
    if not match:
        return "Error: provide at least one reference to look up optical charges and credits."
    rows = ctx.find("optical_transactions", **match)
    return str(rows) if rows else f"No optical charges or credits found for {match}."


# ---------------------------------------------------------------- Northgate Care protection plans

@tool(owner="agent", rw="read")
def find_protection_holdings(ctx: ToolContext, protection_plan_id: str = "", customer_id: str = "",
                             order_line_id: str = "") -> str:
    """Look up Northgate Care protection plans: the plan, status, the covered product's sale line and
    price, the plan purchase date, and the coverage start and end dates.

    Search by the plan, the plan holder, or the sale line of the covered product. Every criterion is
    optional; at least one is needed.

    Args:
        protection_plan_id: The plan reference number; leave "" if unknown.
        customer_id: The customer reference number of the plan holder; leave "" if unknown.
        order_line_id: The sale line of the covered product; leave "" if unknown.
    """
    match = _criteria(protection_plan_id=protection_plan_id, customer_id=customer_id, order_line_id=order_line_id)
    if not match:
        return "Error: provide at least one reference to look up protection plans."
    rows = ctx.find("protection_holdings", **match)
    return str(rows) if rows else f"No protection plans found for {match}."


@tool(owner="agent", rw="read")
def find_protection_events(ctx: ToolContext, protection_event_id: str = "", protection_plan_id: str = "",
                           customer_id: str = "", source_event_id: str = "") -> str:
    """Look up activity on Northgate Care plans: the plan charge and any refund, claims filed (failure date
    and type), and claim settlements (repair, replacement, cash settlement or denial, and the value paid). A
    claim's reference number is that of its filing entry.

    Search by the entry, the plan, the plan holder, or the claim or charge a settlement or refund points
    back to. Every criterion is optional; at least one is needed.

    Args:
        protection_event_id: The reference number of the plan entry or claim; leave "" if unknown.
        protection_plan_id: The plan reference number; leave "" if unknown.
        customer_id: The customer reference number; leave "" if unknown.
        source_event_id: The claim or plan charge a settlement or refund refers to; leave "" if unknown.
    """
    match = _criteria(protection_event_id=protection_event_id, protection_plan_id=protection_plan_id,
                      customer_id=customer_id, source_event_id=source_event_id)
    if not match:
        return "Error: provide at least one reference to look up protection plan activity."
    rows = ctx.find("protection_events", **match)
    return str(rows) if rows else f"No protection plan activity found for {match}."


# ---------------------------------------------------------------- service records

@tool(owner="agent", rw="read")
def find_verification_log(ctx: ToolContext, verification_id: str = "", customer_id: str = "") -> str:
    """Look up the identity verification outcome recorded for a customer in this conversation: whether the
    caller has been verified and when the latest attempt was made.

    Search by the verification record's reference number or the customer reference number. Every criterion
    is optional; at least one is needed.

    Args:
        verification_id: The verification record reference number; leave "" if unknown.
        customer_id: The customer reference number; leave "" if unknown.
    """
    match = _criteria(verification_id=verification_id, customer_id=customer_id)
    if not match:
        return "Error: provide at least one reference to look up verification records."
    rows = ctx.find("verification_log", **match)
    return str(rows) if rows else f"No verification records found for {match}."


@tool(owner="agent", rw="read")
def find_handoff_log(ctx: ToolContext, handoff_id: str = "", customer_id: str = "") -> str:
    """Look up transfers of a customer to a human member services representative: the reason recorded and
    when the transfer was made.

    Search by the transfer record's reference number or the customer reference number. Every criterion is
    optional; at least one is needed.

    Args:
        handoff_id: The transfer record reference number; leave "" if unknown.
        customer_id: The customer reference number; leave "" if unknown.
    """
    match = _criteria(handoff_id=handoff_id, customer_id=customer_id)
    if not match:
        return "Error: provide at least one reference to look up transfer records."
    rows = ctx.find("handoff_log", **match)
    return str(rows) if rows else f"No transfer records found for {match}."


# ---------------------------------------------------------------- identity verification and handoff

@tool(owner="agent", rw="write")
def verify_customer_identity(ctx: ToolContext, customer_id: str, phone_number: str = "", email: str = "",
                             date_of_birth: str = "", postal_code: str = "") -> str:
    """Verify that the caller is the customer on the profile, and record the outcome. A caller must pass
    this verification before any membership, purchase, card, delivery, Tire Center, Optical or protection
    plan record of theirs is discussed in detail or changed.

    This tool performs the comparison itself: it compares each piece of identity information the caller
    states with the profile on file, counts how many match exactly, and passes only when at least 2 match.
    The customer reference number is used only to open the profile and never counts as a match. Callers
    usually give only some of these details, so pass exactly the values the caller stated, unchanged, and
    leave the others empty. The outcome is recorded; if a first attempt fails and a later attempt with more
    information passes, the customer stays verified.

    Args:
        customer_id: The customer reference number, read from the customer profile. Required and never blank; used only to open the profile and not counted as a match.
        phone_number: The phone number the caller states, 10 digits with no spaces or punctuation; leave "" if not stated.
        email: The email address the caller states; leave "" if not stated.
        date_of_birth: The caller's date of birth as YYYY-MM-DD; leave "" if not stated.
        postal_code: The 5-digit ZIP code of the caller's home address; leave "" if not stated.
    """
    if not customer_id:
        return "Error: customer_id is required; locate the customer first and pass their id."
    rows = ctx.find("customers", customer_id=customer_id)
    if not rows:
        return f"Error: no customer {customer_id}; cannot verify."
    rec = rows[0]
    # The locator customer_id is deliberately not a credential.
    supplied = {"phone_number": phone_number, "email": email, "date_of_birth": date_of_birth,
                "postal_code": postal_code}
    matched = sum(1 for field, value in supplied.items() if value and str(rec.get(field)) == str(value))
    verified = matched >= 2
    rid = ctx.make_id("ver_", customer_id)
    # Store only the reproducible outcome; upsert and never downgrade a pass.
    prior = ctx.find("verification_log", verification_id=rid)
    verified = verified or bool(prior and prior[0].get("verified"))
    if prior:
        ctx.update("verification_log", rid, verified=verified, verified_at=ctx.now())
    else:
        ctx.create("verification_log", rid, verification_id=rid, customer_id=customer_id,
                   verified=verified, verified_at=ctx.now())
    return (f"Identity verified for {customer_id} ({matched} detail(s) matched)." if verified
            else f"Identity NOT verified for {customer_id} (only {matched} of the required 2 details matched). "
                 "Ask the caller for another detail on file and call this tool again.")


@tool(owner="agent", rw="write")
def transfer_to_human_agent(ctx: ToolContext, customer_id: str, reason: str) -> str:
    """Transfer the customer to a human member services representative and record the transfer and its
    reason. Use it in exactly one of two situations: no Northgate policy available to you can resolve what
    the customer needs, or the customer has explicitly asked to speak with a person at least 2 times in
    this conversation.

    Args:
        customer_id: The customer reference number, read from the customer profile (the profile must exist).
        reason: Exactly one of two values, never free text. POLICY_NOT_COVERED — no policy available to you can resolve the customer's request. CUSTOMER_REQUESTED — the customer has explicitly asked for a human representative at least 2 times.
    """
    allowed = {"POLICY_NOT_COVERED", "CUSTOMER_REQUESTED"}
    if reason not in allowed:
        return f"Error: unknown handoff reason '{reason}'. Valid: {', '.join(sorted(allowed))}."
    if not ctx.find("customers", customer_id=customer_id):
        return f"Error: no customer {customer_id}; cannot record handoff."
    rid = ctx.make_id("hof_", customer_id, reason)
    ctx.create("handoff_log", rid, handoff_id=rid, customer_id=customer_id, reason=reason, created_at=ctx.now())
    return f"Transfer to a human representative recorded for {customer_id} ({reason})."

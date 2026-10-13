"""Hidden task tools for the membership_fees_renewals_and_cardholders difficulty of Northgate Wholesale Club.

Each tool performs one atomic membership write with the values the caller passes in; none of them checks a
policy condition, works out an amount, or refuses because an earlier step is missing.
"""

from erlbench import ToolContext, tool

@tool(owner="user", rw="write")
def pay_lapsed_membership_renewal_7a245505(ctx: ToolContext, membership_id: str, renewal_tier: str,
                                           new_term_start_date: str, new_expiry_date: str,
                                           renewal_fee: float, tender: str) -> str:
    """The primary member pays the renewal of their own expired Northgate membership. One call charges the
    renewal fee to the payment method the member names, records it on the membership ledger as a renewal fee
    for the new membership year, and returns the membership to active status at the stated tier with the stated
    first day and expiry date of the new membership year, keeping the same membership number. Afterwards the
    member's cards admit them again and the membership shows the new year's dates and tier. The call succeeds
    when the receipt reports the renewal entry reference and the membership as active.

    Args:
        membership_id: Id class — the membership reference number of the expired membership being renewed, as returned by the membership lookup and read out to the member.
        renewal_tier: Enum class — the official tier the new membership year is held at, exactly one of: Northgate Student Club Membership — the discounted student tier, kept only while the student verification is valid; Northgate Heroes Club Membership — the discounted military and first-responder tier, kept only while the service verification is valid; Northgate Club Membership — the standard consumer tier, also the tier a lapsed Student Club or Heroes Club renewal converts to; Northgate Business Membership — the standard business tier held in a licensed business name; Northgate Club Plus Membership — the consumer Plus tier that earns Annual Reward; Northgate Business Plus Membership — the business Plus tier that earns Annual Reward.
        new_term_start_date: Fixed-format class — the first day of the new membership year, a calendar date written YYYY-MM-DD (local club date, no time part, never empty).
        new_expiry_date: Fixed-format class — the last day of the new membership year, a calendar date written YYYY-MM-DD (local club date, no time part, never empty).
        renewal_fee: Fixed-format class — the renewal fee charged, in USD, 2 decimal places, always positive (USD, 2 decimal places, always positive); the value is stored rounded half up to 2 decimal places as passed, with no tax added.
        tender: Enum class — how the member pays, exactly one of: cash_or_debit — paid from a debit card or cash at a counter; northgate_visa — charged to the member's Northgate Rewards Visa card; northgate_store_card — charged to the member's Northgate Store Card; other_credit_card — charged to any other credit card the member names; shop_card — paid from a Northgate Shop Card balance; reward_certificate — paid with an Annual Reward certificate; not_applicable — never used for a payment, only for entries that carry no payment.

    Returns:
        A text receipt reading "Renewal paid" followed by: the renewal entry reference (membership ledger
        reference string), the membership reference, the amount charged in USD with 2 decimals, the tender,
        the tier now held, the new membership year's first day and expiry date (YYYY-MM-DD), and the status
        "active". A receipt starting "Renewal paid" means the charge and the reactivation are both recorded.
    """
    holding = (ctx.find("membership_holdings", membership_id=membership_id) or [{}])[0]
    amount = round(float(renewal_fee), 2)
    rid = ctx.make_id("mtx_", membership_id, renewal_tier, new_term_start_date, new_expiry_date, amount, tender)
    ctx.update("membership_holdings", membership_id, status="active", variant_name=renewal_tier,
               term_start_date=new_term_start_date, expiry_date=new_expiry_date)
    ctx.create("membership_transactions", rid, membership_txn_id=rid, membership_id=membership_id,
               customer_id=holding.get("customer_id"), event_type="membership_fee_charged",
               transaction_date=ctx.now()[:10], amount=amount, fee_type="renewal_term",
               term_start_date=new_term_start_date, term_end_date=new_expiry_date, membership_card_id="",
               tender=tender, refund_reason="not_applicable", source_txn_id="", source_category="not_applicable",
               source_ref_id="", basis_amount=0.0)
    return (f"Renewal paid: entry {rid}, membership {membership_id}, {amount:.2f} USD via {tender}, "
            f"tier {renewal_tier}, year {new_term_start_date} to {new_expiry_date}, status active.")


@tool(owner="agent", rw="write")
def upgrade_membership_to_plus_9f256f7b(ctx: ToolContext, membership_id: str, upgrade_tier: str,
                                        upgrade_fee: float, tender: str) -> str:
    """Member services moves an active Northgate membership to its Plus tier in the middle of the membership
    year. One call changes the tier on the membership to the stated Plus tier, leaves the membership number and
    the expiry date unchanged, and records the upgrade fee on the membership ledger as an upgrade-difference
    charge for the membership year currently on the membership, billed to the stated tender. The member sees
    the new tier on the membership from that day. The call succeeds when the receipt reports the upgrade entry
    reference and the new tier.

    Args:
        membership_id: Id class — the membership reference number of the membership being upgraded, as returned by the membership lookup.
        upgrade_tier: Enum class — the official tier the membership moves to, exactly one of: Northgate Student Club Membership — the discounted student tier, kept only while the student verification is valid; Northgate Heroes Club Membership — the discounted military and first-responder tier, kept only while the service verification is valid; Northgate Club Membership — the standard consumer tier, also the tier a lapsed Student Club or Heroes Club renewal converts to; Northgate Business Membership — the standard business tier held in a licensed business name; Northgate Club Plus Membership — the consumer Plus tier that earns Annual Reward; Northgate Business Plus Membership — the business Plus tier that earns Annual Reward.
        upgrade_fee: Fixed-format class — the upgrade fee charged, in USD, 2 decimal places, always positive (USD, 2 decimal places, always positive); the value is stored rounded half up to 2 decimal places as passed, with no tax added.
        tender: Enum class — how the upgrade fee is paid, exactly one of: cash_or_debit — paid from a debit card or cash at a counter; northgate_visa — charged to the member's Northgate Rewards Visa card; northgate_store_card — charged to the member's Northgate Store Card; other_credit_card — charged to any other credit card the member names; shop_card — paid from a Northgate Shop Card balance; reward_certificate — paid with an Annual Reward certificate; not_applicable — never used for a payment, only for entries that carry no payment.

    Returns:
        A text receipt reading "Upgrade recorded" followed by: the upgrade entry reference (membership ledger
        reference string), the membership reference, the new tier, the fee charged in USD with 2 decimals, the
        tender, and the unchanged expiry date (YYYY-MM-DD). A receipt starting "Upgrade recorded" means the tier
        change and the fee are both on the membership.
    """
    holding = (ctx.find("membership_holdings", membership_id=membership_id) or [{}])[0]
    amount = round(float(upgrade_fee), 2)
    rid = ctx.make_id("mtx_", membership_id, upgrade_tier, amount, tender)
    ctx.update("membership_holdings", membership_id, variant_name=upgrade_tier)
    ctx.create("membership_transactions", rid, membership_txn_id=rid, membership_id=membership_id,
               customer_id=holding.get("customer_id"), event_type="membership_fee_charged",
               transaction_date=ctx.now()[:10], amount=amount, fee_type="upgrade_difference",
               term_start_date=holding.get("term_start_date", ""), term_end_date=holding.get("expiry_date", ""),
               membership_card_id="", tender=tender, refund_reason="not_applicable", source_txn_id="",
               source_category="not_applicable", source_ref_id="", basis_amount=0.0)
    return (f"Upgrade recorded: entry {rid}, membership {membership_id}, tier {upgrade_tier}, "
            f"{amount:.2f} USD via {tender}, expiry {holding.get('expiry_date', '')}.")


@tool(owner="user", rw="write")
def confirm_plus_guarantee_claim_e9c317f9(ctx: ToolContext, membership_request_id: str, membership_id: str,
                                          source_txn_id: str, term_end_date: str, guarantee_refund: float,
                                          tender: str, downgrade_tier: str) -> str:
    """The primary member confirms their own Plus guarantee claim for a completed membership year. One call marks
    the member's recorded guarantee claim request as confirmed, books the guarantee refund on the membership
    ledger against the stated fee charge for the stated membership year, returned to the stated tender, and moves
    the membership to the stated base tier from today. Afterwards the claim shows as confirmed, the refund appears
    on the ledger and the membership carries the base tier. The call succeeds when the receipt reports the refund
    entry reference and the new tier.

    Args:
        membership_request_id: Id class — the reference number of the member's guarantee claim request, as returned by the membership request lookup and read out to the member.
        membership_id: Id class — the membership reference number the claim is on, as returned by the membership lookup.
        source_txn_id: Id class — the reference number of the fee charge the refund is booked against, as returned by the membership ledger lookup.
        term_end_date: Fixed-format class — the last day of the completed membership year the claim settles, a calendar date written YYYY-MM-DD (local club date, never empty).
        guarantee_refund: Fixed-format class — the guarantee refund paid, in USD, 2 decimal places, always positive (USD, 2 decimal places, always positive); stored rounded half up to 2 decimal places as passed.
        tender: Enum class — where the refund is returned, exactly one of: cash_or_debit — back to the debit card or as cash when the charge was paid that way; northgate_visa — back to the member's Northgate Rewards Visa card; northgate_store_card — back to the member's Northgate Store Card; other_credit_card — back to the other credit card the charge was paid with; shop_card — onto a Northgate Shop Card; reward_certificate — never used for a refund destination, only for charges paid with a certificate; not_applicable — never used for a refund, only for entries that carry no payment.
        downgrade_tier: Enum class — the official tier the membership moves to, exactly one of: Northgate Student Club Membership — the discounted student tier; Northgate Heroes Club Membership — the discounted military and first-responder tier; Northgate Club Membership — the consumer base tier a Northgate Club Plus Membership moves to; Northgate Business Membership — the business base tier a Northgate Business Plus Membership moves to; Northgate Club Plus Membership — the consumer Plus tier; Northgate Business Plus Membership — the business Plus tier.

    Returns:
        A text receipt reading "Guarantee claim confirmed" followed by: the refund entry reference (membership
        ledger reference string), the claim request reference, the refund amount in USD with 2 decimals, the
        tender, the membership year end (YYYY-MM-DD) and the tier now held. A receipt starting "Guarantee claim
        confirmed" means the claim, the refund and the tier change are all recorded.
    """
    holding = (ctx.find("membership_holdings", membership_id=membership_id) or [{}])[0]
    charge = (ctx.find("membership_transactions", membership_txn_id=source_txn_id) or [{}])[0]
    amount = round(float(guarantee_refund), 2)
    rid = ctx.make_id("mtx_", membership_request_id, membership_id, source_txn_id, term_end_date, amount, tender,
                      downgrade_tier)
    ctx.update("membership_requests", membership_request_id, status="confirmed")
    ctx.create("membership_transactions", rid, membership_txn_id=rid, membership_id=membership_id,
               customer_id=holding.get("customer_id"), event_type="membership_fee_refunded",
               transaction_date=ctx.now()[:10], amount=amount, fee_type=charge.get("fee_type", "not_applicable"),
               term_start_date=charge.get("term_start_date", ""), term_end_date=term_end_date, membership_card_id="",
               tender=tender, refund_reason="shortfall_guarantee", source_txn_id=source_txn_id,
               source_category="not_applicable", source_ref_id="", basis_amount=0.0)
    ctx.update("membership_holdings", membership_id, variant_name=downgrade_tier)
    return (f"Guarantee claim confirmed: refund {rid}, request {membership_request_id}, {amount:.2f} USD to {tender}, "
            f"year ending {term_end_date}, tier now {downgrade_tier}.")


@tool(owner="agent", rw="write")
def refund_downgrade_difference_0adda8cc(ctx: ToolContext, membership_id: str, source_txn_id: str,
                                         term_end_date: str, refund_amount: float, tender: str) -> str:
    """Member services books a downgrade difference refund on a Northgate membership. One call records the refund
    on the membership ledger against the stated renewal fee charge of the stated membership year, returned to the
    stated tender; nothing else on the membership changes. The member sees the refund on the ledger and on the
    tender it is returned to. The call succeeds when the receipt reports the refund entry reference.

    Args:
        membership_id: Id class — the membership reference number, as returned by the membership lookup.
        source_txn_id: Id class — the reference number of the renewal fee charge the refund is booked against, as returned by the membership ledger lookup.
        term_end_date: Fixed-format class — the last day of the membership year the refunded charge paid for, a calendar date written YYYY-MM-DD (local club date, never empty).
        refund_amount: Fixed-format class — the refund amount, in USD, 2 decimal places, always positive (USD, 2 decimal places, always positive); stored rounded half up to 2 decimal places as passed.
        tender: Enum class — where the refund is returned, exactly one of: cash_or_debit — back to the debit card or as cash when the charge was paid that way; northgate_visa — back to the member's Northgate Rewards Visa card; northgate_store_card — back to the member's Northgate Store Card; other_credit_card — back to the other credit card the charge was paid with; shop_card — onto a Northgate Shop Card; reward_certificate — never used for a refund destination, only for charges paid with a certificate; not_applicable — never used for a refund, only for entries that carry no payment.

    Returns:
        A text receipt reading "Downgrade difference refunded" followed by: the refund entry reference
        (membership ledger reference string), the charge it is booked against, the amount in USD with 2 decimals,
        the tender and the membership year end (YYYY-MM-DD). A receipt starting "Downgrade difference refunded"
        means the refund is on the ledger.
    """
    holding = (ctx.find("membership_holdings", membership_id=membership_id) or [{}])[0]
    charge = (ctx.find("membership_transactions", membership_txn_id=source_txn_id) or [{}])[0]
    amount = round(float(refund_amount), 2)
    rid = ctx.make_id("mtx_", membership_id, source_txn_id, term_end_date, amount, tender, "downgrade_difference")
    ctx.create("membership_transactions", rid, membership_txn_id=rid, membership_id=membership_id,
               customer_id=holding.get("customer_id"), event_type="membership_fee_refunded",
               transaction_date=ctx.now()[:10], amount=amount, fee_type=charge.get("fee_type", "not_applicable"),
               term_start_date=charge.get("term_start_date", ""), term_end_date=term_end_date, membership_card_id="",
               tender=tender, refund_reason="downgrade_difference", source_txn_id=source_txn_id,
               source_category="not_applicable", source_ref_id="", basis_amount=0.0)
    return (f"Downgrade difference refunded: refund {rid} against {source_txn_id}, {amount:.2f} USD to {tender}, "
            f"year ending {term_end_date}.")


@tool(owner="agent", rw="write")
def refund_removed_addon_card_fee_e7b2031f(ctx: ToolContext, membership_id: str, membership_card_id: str,
                                           source_txn_id: str, term_end_date: str, refund_amount: float,
                                           tender: str) -> str:
    """Member services books the refund of the add-on card fee of a business add-on cardholder whom the primary
    member has removed. One call records the refund on the membership ledger against the stated add-on fee charge for the
    stated card and membership year, returned to the stated tender; the cards themselves are not changed. The
    member sees the refund on the ledger and on the tender it is returned to. The call succeeds when the receipt
    reports the refund entry reference.

    Args:
        membership_id: Id class — the membership reference number, as returned by the membership lookup.
        membership_card_id: Id class — the reference number of the add-on card issuance the fee was charged for, as returned by the membership card lookup or shown on the add-on fee entry.
        source_txn_id: Id class — the reference number of the add-on fee charge the refund is booked against, as returned by the membership ledger lookup.
        term_end_date: Fixed-format class — the last day of the membership year the add-on fee paid for, a calendar date written YYYY-MM-DD (local club date, never empty).
        refund_amount: Fixed-format class — the refund amount, in USD, 2 decimal places, always positive (USD, 2 decimal places, always positive); stored rounded half up to 2 decimal places as passed.
        tender: Enum class — where the refund is returned, exactly one of: cash_or_debit — back to the debit card or as cash when the charge was paid that way; northgate_visa — back to the member's Northgate Rewards Visa card; northgate_store_card — back to the member's Northgate Store Card; other_credit_card — back to the other credit card the charge was paid with; shop_card — onto a Northgate Shop Card; reward_certificate — never used for a refund destination, only for charges paid with a certificate; not_applicable — never used for a refund, only for entries that carry no payment.

    Returns:
        A text receipt reading "Add-on card fee refunded" followed by: the refund entry reference (membership
        ledger reference string), the add-on card reference, the charge it is booked against, the amount in USD
        with 2 decimals, the tender and the membership year end (YYYY-MM-DD). A receipt starting "Add-on card fee
        refunded" means the refund is on the ledger.
    """
    holding = (ctx.find("membership_holdings", membership_id=membership_id) or [{}])[0]
    charge = (ctx.find("membership_transactions", membership_txn_id=source_txn_id) or [{}])[0]
    amount = round(float(refund_amount), 2)
    rid = ctx.make_id("mtx_", membership_id, membership_card_id, source_txn_id, term_end_date, amount, tender)
    ctx.create("membership_transactions", rid, membership_txn_id=rid, membership_id=membership_id,
               customer_id=holding.get("customer_id"), event_type="membership_fee_refunded",
               transaction_date=ctx.now()[:10], amount=amount, fee_type="addon_card_fee",
               term_start_date=charge.get("term_start_date", ""), term_end_date=term_end_date,
               membership_card_id=membership_card_id, tender=tender, refund_reason="addon_card_removed",
               source_txn_id=source_txn_id, source_category="not_applicable", source_ref_id="", basis_amount=0.0)
    return (f"Add-on card fee refunded: refund {rid}, card {membership_card_id}, against {source_txn_id}, "
            f"{amount:.2f} USD to {tender}, year ending {term_end_date}.")


@tool(owner="user", rw="write")
def confirm_membership_cancellation_5b4de829(ctx: ToolContext, membership_id: str, source_txn_id: str,
                                             term_end_date: str, refund_amount: float, refund_reason: str,
                                             tender: str) -> str:
    """The primary member confirms the cancellation of their own Northgate membership. One call records the
    member's confirmed cancellation request dated today, sets the membership to cancelled with today's closing
    date, deactivates every card still in use on the membership, and books the cancellation refund on the
    membership ledger against the stated fee charge for the stated membership year, returned to the stated
    tender. Afterwards the membership shows as cancelled, none of its cards admit their holders, and the refund
    appears on the ledger. The call succeeds when the receipt reports the refund entry reference and the
    cancelled status.

    Args:
        membership_id: Id class — the membership reference number being cancelled, as returned by the membership lookup and read out to the member.
        source_txn_id: Id class — the reference number of the current year's fee charge the refund is booked against, as returned by the membership ledger lookup.
        term_end_date: Fixed-format class — the last day of the current membership year, a calendar date written YYYY-MM-DD (local club date, never empty).
        refund_amount: Fixed-format class — the cancellation refund, in USD, 2 decimal places, always positive (USD, 2 decimal places, always positive); stored rounded half up to 2 decimal places as passed.
        refund_reason: Enum class — the kind of refund booked, exactly one of: cancellation_full — the current-year fees are refunded whole; cancellation_prorated — only a share of the current-year fees is refunded; shortfall_guarantee — never used on a cancellation, only for Plus guarantee refunds; downgrade_difference — never used on a cancellation, only for the Plus premium refunded on a downgrade; duplicate_charge — never used on a cancellation, only for a repeated charge; addon_card_removed — never used on a cancellation, only for a removed add-on card's fee; not_applicable — never used on a refund.
        tender: Enum class — where the refund is returned, exactly one of: cash_or_debit — back to the debit card or as cash when the charge was paid that way; northgate_visa — back to the member's Northgate Rewards Visa card; northgate_store_card — back to the member's Northgate Store Card; other_credit_card — back to the other credit card the charge was paid with; shop_card — onto a Northgate Shop Card; reward_certificate — never used for a refund destination, only for charges paid with a certificate; not_applicable — never used for a refund, only for entries that carry no payment.

    Returns:
        A text receipt reading "Cancellation confirmed" followed by: the refund entry reference (membership ledger
        reference string), the membership reference, the refund amount in USD with 2 decimals, the refund reason,
        the tender, the number of cards deactivated (integer) and the status "cancelled". A receipt starting
        "Cancellation confirmed" means the cancellation, the card deactivations and the refund are all recorded.
    """
    holding = (ctx.find("membership_holdings", membership_id=membership_id) or [{}])[0]
    charge = (ctx.find("membership_transactions", membership_txn_id=source_txn_id) or [{}])[0]
    amount = round(float(refund_amount), 2)
    today = ctx.now()[:10]
    customer_id = holding.get("customer_id")
    req = ctx.make_id("mrq_", membership_id, "cancel_with_refund", today)
    ctx.create("membership_requests", req, membership_request_id=req, customer_id=customer_id,
               membership_id=membership_id, request_type="cancel_with_refund", status="confirmed",
               requested_date=today, created_at=ctx.now())
    ctx.update("membership_holdings", membership_id, status="cancelled", closed_date=today)
    cards = ctx.find("membership_cards", membership_id=membership_id)
    ended = {c.get("source_card_id") for c in cards if c.get("event_type") == "membership_card_deactivated"}
    deactivated = 0
    for card in cards:
        cid = card.get("membership_card_id")
        if card.get("event_type") != "membership_card_issued" or cid in ended:
            continue
        did = ctx.make_id("mcd_", cid, "membership_ended", today)
        ctx.create("membership_cards", did, membership_card_id=did, membership_id=membership_id,
                   customer_id=customer_id, event_type="membership_card_deactivated",
                   card_type=card.get("card_type"), cardholder_name=card.get("cardholder_name"), event_date=today,
                   issue_reason="not_applicable", deactivation_reason="membership_ended", source_card_id=cid)
        deactivated += 1
    rid = ctx.make_id("mtx_", membership_id, source_txn_id, term_end_date, amount, refund_reason, tender)
    ctx.create("membership_transactions", rid, membership_txn_id=rid, membership_id=membership_id,
               customer_id=customer_id, event_type="membership_fee_refunded", transaction_date=today, amount=amount,
               fee_type=charge.get("fee_type", "not_applicable"), term_start_date=charge.get("term_start_date", ""),
               term_end_date=term_end_date, membership_card_id="", tender=tender, refund_reason=refund_reason,
               source_txn_id=source_txn_id, source_category="not_applicable", source_ref_id="", basis_amount=0.0)
    return (f"Cancellation confirmed: refund {rid}, membership {membership_id}, {amount:.2f} USD ({refund_reason}) "
            f"to {tender}, {deactivated} card(s) deactivated, status cancelled.")

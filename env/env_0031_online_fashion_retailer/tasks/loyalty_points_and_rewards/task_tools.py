"""Hidden task tools of the loyalty_points_and_rewards difficulty (Marlowe Rewards).

Each tool performs one atomic write on the Marlowe Rewards records with the values passed in; it
judges no eligibility and computes no figure. Tool names are reached through unlock_* -> call_*.
"""

from erlbench import ToolContext, tool


@tool(owner="agent", rw="write")
def post_points_reversal_46de2c04(ctx: ToolContext, membership_id: str, return_id: str, order_id: str,
                                  points_reversed: int, reversed_spend_usd: float,
                                  tier_multiplier_applied: float) -> str:
    """Take back Marlowe Rewards points on a refunded return by posting one points-reversal entry on the member's points ledger.

    The entry is dated today, is available today, carries the return and the order it concerns, and
    debits the given number of points from the membership, so the membership's points balance falls by
    that number (it may go below zero). The reversal entry also records the refunded merchandise amount
    and the earning multiplier it refers to. The member sees the deduction on their points history at
    once. Success is the receipt line naming the new entry and the balance after it.

    Args:
        membership_id: Id class — the Marlowe Rewards membership number whose points are taken back, as shown by the membership lookup.
        return_id: Id class — the return (RMA) number whose refund caused the reversal, as shown by the return lookup.
        order_id: Id class — the order number the returned merchandise came from, as shown by the return or order lookup.
        points_reversed: Fixed-format class — the number of points to take back, given as a positive whole number (integer); it is booked as a debit in signed integer points, so 40 is recorded as -40.
        reversed_spend_usd: Fixed-format class — the refunded merchandise amount the reversal is based on, in USD to 2 decimal places, rounded half up to the cent.
        tier_multiplier_applied: Fixed-format class — the earning multiplier recorded on the order's original earning entry, a decimal with 2 decimal places (for example 1.50).

    Returns:
        A one-line text receipt "Reversal <entry id> posted: -<points> points on order <order id> for return <return id>; balance now <balance> points." where entry id is the new points-entry reference, points is the integer debited, and balance is the membership's integer points balance after the entry; the receipt appearing means the entry was booked.
    """
    pts = int(points_reversed)
    today = ctx.now()[:10]
    rid = ctx.make_id("lle_", membership_id, return_id, order_id, points_reversed, reversed_spend_usd,
                      tier_multiplier_applied)
    member = (ctx.find("loyalty_memberships", membership_id=membership_id) or [{}])[0]
    ctx.create("loyalty_ledger", rid, loyalty_entry_id=rid, membership_id=membership_id,
               customer_id=member.get("customer_id"), event_type="loyalty_points_reversed",
               posting_date=today, available_date=today, points=-pts, order_id=order_id,
               return_id=return_id, earn_source="not_applicable", qualifying_spend_usd=0.0,
               reversed_spend_usd=round(float(reversed_spend_usd), 2), tier_at_posting=member.get("variant_name", ""),
               tier_multiplier_applied=round(float(tier_multiplier_applied), 2),
               bonus_type="not_applicable", bonus_reference="", reward_value_usd=0.0,
               forfeit_reason="not_applicable", last_activity_date="")
    bal = int(sum(int(r.get("points") or 0) for r in ctx.find("loyalty_ledger", membership_id=membership_id)))
    ctx.update("loyalty_memberships", membership_id, points_balance=bal)
    return (f"Reversal {rid} posted: -{pts} points on order {order_id} for return {return_id}; "
            f"balance now {bal} points.")


@tool(owner="user", rw="write")
def accept_goodwill_points_7ea0a08d(ctx: ToolContext, membership_id: str, customer_id: str, bonus_type: str,
                                    bonus_reference: str, goodwill_points: int) -> str:
    """The member personally accepts the Marlowe Rewards service-goodwill points offered for a documented delivery failure, which credits them as one bonus entry.

    Accepting books one bonus entry on the member's points ledger, dated and available today, under the
    given bonus kind and reference, recorded at the tier the membership holds today, and adds the
    accepted points to the membership's points balance. The member sees the bonus on their points
    history immediately. Success is the receipt line naming the bonus entry and the new balance.

    Args:
        membership_id: Id class — the member's own Marlowe Rewards membership number, as read out by the agent from the membership lookup.
        customer_id: Id class — the member's customer reference number on the profile, as read out by the agent from the customer lookup.
        bonus_type: Enum class — the kind of bonus being accepted, exactly one of: service_goodwill when the points compensate a documented delivery failure on a delivery claim (the only kind this acceptance is used for); welcome when the points are the one-time enrollment bonus; birthday when the points are the yearly birthday bonus; product_review when the points reward a published product review; referral when the points reward a referred friend's first order; not_applicable when the entry is not a bonus at all.
        bonus_reference: Fixed-format class — the delivery claim number the goodwill compensates, read out by the agent from the claim lookup and
            recorded as the bonus reference, whose stored format is "membership id (welcome) | YYYY (birthday) | REV-####### (product_review) | customer id (referral) | claim id (service_goodwill); empty on non-bonus rows" — here always the claim id form, copied exactly as the claim lookup shows it.
        goodwill_points: Fixed-format class — the number of goodwill points offered and accepted, a positive whole number (integer) credited in signed integer points.

    Returns:
        A one-line text receipt "Goodwill <entry id> credited: +<points> points for claim <bonus reference>; balance now <balance> points." where entry id is the new bonus-entry reference, points is the integer credited, and balance is the membership's integer points balance afterwards; the receipt appearing means the goodwill was credited.
    """
    pts = int(goodwill_points)
    today = ctx.now()[:10]
    member = (ctx.find("loyalty_memberships", membership_id=membership_id) or [{}])[0]
    rid = ctx.make_id("lle_", membership_id, customer_id, bonus_type, bonus_reference, goodwill_points)
    ctx.create("loyalty_ledger", rid, loyalty_entry_id=rid, membership_id=membership_id,
               customer_id=customer_id, event_type="loyalty_bonus_posted",
               posting_date=today, available_date=today, points=pts, order_id=None, return_id=None,
               earn_source="not_applicable", qualifying_spend_usd=0.0, reversed_spend_usd=0.0,
               tier_at_posting=member.get("variant_name", ""), tier_multiplier_applied=0.0,
               bonus_type=bonus_type, bonus_reference=bonus_reference, reward_value_usd=0.0,
               forfeit_reason="not_applicable", last_activity_date="")
    bal = int(sum(int(r.get("points") or 0) for r in ctx.find("loyalty_ledger", membership_id=membership_id)))
    ctx.update("loyalty_memberships", membership_id, points_balance=bal)
    return f"Goodwill {rid} credited: +{pts} points for claim {bonus_reference}; balance now {bal} points."


@tool(owner="agent", rw="write")
def post_missing_points_b5bbe1fa(ctx: ToolContext, membership_id: str, order_id: str, points: int,
                                 qualifying_spend_usd: float, tier_multiplier_applied: float,
                                 available_date: str) -> str:
    """Credit Marlowe Rewards points for a dispatched order that never earned them, by posting one missing-points adjustment entry on the member's points ledger.

    The entry is dated today, names the order, records the qualifying spend it was computed on, the
    tier the membership holds today and that tier's multiplier, becomes available on the given date,
    and adds the given points to the membership's points balance. The member sees the points on their
    points history at once (as pending until the available date). Success is the receipt line naming
    the new entry and the balance after it.

    Args:
        membership_id: Id class — the Marlowe Rewards membership number to credit, as shown by the membership lookup.
        order_id: Id class — the order number that never earned its points, as shown by the order lookup.
        points: Fixed-format class — the points credited, a positive whole number (integer) booked in signed integer points.
        qualifying_spend_usd: Fixed-format class — the order's qualifying spend the points were worked out on, in USD to 2 decimal places, rounded half up to the cent.
        tier_multiplier_applied: Fixed-format class — the tier_points_multiplier of the tier the membership holds today, a decimal with 2 decimal places (for example 1.00).
        available_date: Fixed-format class — the calendar date from which the points count as available, in YYYY-MM-DD format.

    Returns:
        A one-line text receipt "Missing points <entry id> posted: +<points> points on order <order id>, available <available date>; balance now <balance> points." where entry id is the new points-entry reference, points is the integer credited, available date is YYYY-MM-DD and balance is the membership's integer points balance afterwards; the receipt appearing means the adjustment was booked.
    """
    pts = int(points)
    today = ctx.now()[:10]
    member = (ctx.find("loyalty_memberships", membership_id=membership_id) or [{}])[0]
    rid = ctx.make_id("lle_", membership_id, order_id, points, qualifying_spend_usd, tier_multiplier_applied,
                      available_date)
    ctx.create("loyalty_ledger", rid, loyalty_entry_id=rid, membership_id=membership_id,
               customer_id=member.get("customer_id"), event_type="loyalty_points_earned",
               posting_date=today, available_date=available_date, points=pts, order_id=order_id,
               return_id=None, earn_source="missing_points_adjustment",
               qualifying_spend_usd=round(float(qualifying_spend_usd), 2), reversed_spend_usd=0.0,
               tier_at_posting=member.get("variant_name", ""),
               tier_multiplier_applied=round(float(tier_multiplier_applied), 2),
               bonus_type="not_applicable", bonus_reference="", reward_value_usd=0.0,
               forfeit_reason="not_applicable", last_activity_date="")
    bal = int(sum(int(r.get("points") or 0) for r in ctx.find("loyalty_ledger", membership_id=membership_id)))
    ctx.update("loyalty_memberships", membership_id, points_balance=bal)
    return (f"Missing points {rid} posted: +{pts} points on order {order_id}, available {available_date}; "
            f"balance now {bal} points.")


@tool(owner="agent", rw="write")
def write_tier_upgrade_189dabab(ctx: ToolContext, membership_id: str, variant_name: str,
                                tier_valid_through: str) -> str:
    """Move a Marlowe Rewards membership up to a higher tier by writing the new tier on the membership.

    The membership's tier becomes the given tier with today as its start date and the given last day
    of validity; nothing else on the membership or its points changes. The member's perks follow the
    new tier from today. Success is the receipt line naming the membership, the tier written and its
    validity.

    Args:
        membership_id: Id class — the Marlowe Rewards membership number to upgrade, as shown by the membership lookup.
        variant_name: Enum class — the tier the membership moves to, exactly one of: Marlowe Rewards Member when the membership is to hold the base tier; Marlowe Rewards Silver when it is to hold the second tier; Marlowe Rewards Gold when it is to hold the third tier; Marlowe Rewards Platinum when it is to hold the fourth tier; Marlowe Rewards Icon when it is to hold the fifth tier; Marlowe Rewards Atelier when it is to hold the top tier.
        tier_valid_through: Fixed-format class — the last day the new tier is valid before the annual review re-evaluates it, a 31 December, in YYYY-MM-DD format.

    Returns:
        A one-line text receipt "Membership <membership id> now <tier> from <start date>, valid through <valid-through date>." where the dates are YYYY-MM-DD; the receipt appearing means the tier was written.
    """
    today = ctx.now()[:10]
    ctx.update("loyalty_memberships", membership_id, variant_name=variant_name, tier_start_date=today,
               tier_valid_through=tier_valid_through)
    return f"Membership {membership_id} now {variant_name} from {today}, valid through {tier_valid_through}."


@tool(owner="user", rw="write")
def claim_birthday_bonus_8dc2d134(ctx: ToolContext, membership_id: str, customer_id: str, bonus_type: str,
                                  bonus_reference: str, birthday_points: int) -> str:
    """The member personally claims a Marlowe Rewards birthday bonus that did not post on its day, confirming their own date of birth, which credits it as one bonus entry.

    Claiming books one bonus entry on the member's points ledger, dated and available today, under the
    given bonus kind and reference year, recorded at the tier the membership holds today, and adds the
    claimed points to the membership's points balance. The member sees the bonus on their points
    history immediately. Success is the receipt line naming the bonus entry and the new balance.

    Args:
        membership_id: Id class — the member's own Marlowe Rewards membership number, as read out by the agent from the membership lookup.
        customer_id: Id class — the member's customer reference number on the profile, as read out by the agent from the customer lookup.
        bonus_type: Enum class — the kind of bonus being claimed, exactly one of: birthday when the points are the yearly birthday bonus (the only kind this claim is used for); welcome when the points are the one-time enrollment bonus; product_review when the points reward a published product review; referral when the points reward a referred friend's first order; service_goodwill when the points compensate a documented delivery failure; not_applicable when the entry is not a bonus at all.
        bonus_reference: Fixed-format class — the year the birthday bonus belongs to, recorded as the bonus reference, whose stored format is
            "membership id (welcome) | YYYY (birthday) | REV-####### (product_review) | customer id (referral) | claim id (service_goodwill); empty on non-bonus rows" — here always the YYYY form of the birth-month year.
        birthday_points: Fixed-format class — the birthday points claimed, a positive whole number (integer) credited in signed integer points.

    Returns:
        A one-line text receipt "Birthday bonus <entry id> credited: +<points> points for <bonus reference>; balance now <balance> points." where entry id is the new bonus-entry reference, points is the integer credited and balance is the membership's integer points balance afterwards; the receipt appearing means the bonus was credited.
    """
    pts = int(birthday_points)
    today = ctx.now()[:10]
    member = (ctx.find("loyalty_memberships", membership_id=membership_id) or [{}])[0]
    rid = ctx.make_id("lle_", membership_id, customer_id, bonus_type, bonus_reference, birthday_points)
    ctx.create("loyalty_ledger", rid, loyalty_entry_id=rid, membership_id=membership_id,
               customer_id=customer_id, event_type="loyalty_bonus_posted",
               posting_date=today, available_date=today, points=pts, order_id=None, return_id=None,
               earn_source="not_applicable", qualifying_spend_usd=0.0, reversed_spend_usd=0.0,
               tier_at_posting=member.get("variant_name", ""), tier_multiplier_applied=0.0,
               bonus_type=bonus_type, bonus_reference=bonus_reference, reward_value_usd=0.0,
               forfeit_reason="not_applicable", last_activity_date="")
    bal = int(sum(int(r.get("points") or 0) for r in ctx.find("loyalty_ledger", membership_id=membership_id)))
    ctx.update("loyalty_memberships", membership_id, points_balance=bal)
    return f"Birthday bonus {rid} credited: +{pts} points for {bonus_reference}; balance now {bal} points."

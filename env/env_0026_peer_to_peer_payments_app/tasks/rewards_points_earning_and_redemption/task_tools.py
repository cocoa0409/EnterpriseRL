"""Hidden task tools for the rewards_points_earning_and_redemption difficulty (Pocketwire Rewards).

Each tool performs one atomic write on the Pocketwire Rewards points ledger and the membership's
points balance. The tools take the values the agent has already worked out from the published
policy and the records; they judge no eligibility and compute nothing on the agent's behalf.
"""

from erlbench import ToolContext, tool


# Helpers are plain expressions (not functions) so that every function in this file is a task tool.
_membership = lambda ctx, membership_id: (ctx.find("rewards_memberships", membership_id=membership_id) or [{}])[0]

_LEDGER_BLANK = {
    "source_txn_id": "", "spend_amount": "", "merchant_category": "not_applicable",
    "offer_code": "", "activated_at": "", "redemption_reference": "",
    "redemption_type": "not_applicable", "cash_value": "", "payee_name": "",
    "expiry_reason": "not_applicable", "referred_username": "", "bonus_type": "not_applicable",
    "bonus_period": "",
}

_ledger_row = lambda rid, membership_id, customer_id, **fields: dict(
    _LEDGER_BLANK, rewards_entry_id=rid, membership_id=membership_id, customer_id=customer_id, **fields)


@tool(owner="agent", rw="write")
def credit_anniversary_bonus_4deaf7db(ctx: ToolContext, membership_id: str, bonus_period: str,
                                      points: int) -> str:
    """Credit a Pocketwire Rewards membership anniversary bonus to a member's points balance.

    Books one anniversary bonus entry on the member's points ledger, dated today, for the
    anniversary year given, and adds the points to the membership's points balance. The member sees the bonus
    in the app's points activity and a higher points balance straight away. The receipt below
    confirms the entry was booked.

    Args:
        membership_id: Id class — the rewards membership reference number of the member being credited, as returned by the rewards membership lookup.
        bonus_period: Fixed-format class — the period the bonus is for, written as YYYY-Qn for a quarterly milestone, YYYY for an anniversary; this tool books anniversary bonuses only, so give the four-digit calendar year in which the anniversary fell.
        points: Fixed-format class — the bonus points credited, a whole integer number of points in integer points, zero or positive.

    Returns:
        A text rendering of a dictionary with these fields: status (the text "credited" when the
        entry was booked), rewards_entry_id (reference number of the new points entry),
        membership_id (the membership credited), bonus_type (always the text "anniversary"),
        bonus_period (as booked),
        points (integer points credited), entry_date (booking date, YYYY-MM-DD) and
        points_balance (the membership's integer points balance including this credit).
    """
    m = _membership(ctx, membership_id)
    bonus_type = "anniversary"
    rid = ctx.make_id("rwb_", membership_id, bonus_type, bonus_period, points)
    today = ctx.now()[:10]
    ctx.create("rewards_ledger", rid, **_ledger_row(
        rid, membership_id, m.get("customer_id", ""), event_type="rewards_bonus",
        entry_date=today, points=int(points), bonus_type=bonus_type, bonus_period=bonus_period))
    new_balance = int(m.get("points_balance") or 0) + int(points)
    ctx.update("rewards_memberships", membership_id, points_balance=new_balance)
    return str({"status": "credited", "rewards_entry_id": rid, "membership_id": membership_id,
                "bonus_type": bonus_type, "bonus_period": bonus_period, "points": int(points),
                "entry_date": today, "points_balance": new_balance})


@tool(owner="agent", rw="write")
def post_refund_clawback_4ceb9a03(ctx: ToolContext, membership_id: str, source_txn_id: str,
                                  spend_amount: float, points: int) -> str:
    """Take back Pocketwire Rewards points earned on a debit card purchase that a merchant refunded.

    Books one clawback entry on the member's points ledger, dated today, against the refunded
    debit card purchase and carrying the refunded amount, and subtracts the points from the
    membership's points balance. The member sees the clawback in the app's points activity and
    a lower points balance straight away. The receipt below confirms the entry was booked.

    Args:
        membership_id: Id class — the rewards membership reference number of the member, as returned by the rewards membership lookup.
        source_txn_id: Id class — the card transaction reference number of the refunded debit card purchase (the original purchase, not the refund), as shown by the card activity lookup on the refund entry.
        spend_amount: Fixed-format class — the refunded amount in USD, 2 decimal places, copied from the merchant refund.
        points: Fixed-format class — the points taken back, a whole integer number of points in integer points, zero or positive.

    Returns:
        A text rendering of a dictionary with these fields: status (the text "clawed_back" when
        the entry was booked), rewards_entry_id (reference number of the new points entry),
        membership_id, source_txn_id (the refunded purchase), spend_amount (refunded USD, 2
        decimal places), points (integer points taken back), entry_date (booking date,
        YYYY-MM-DD) and points_balance (the membership's integer points balance net of this entry).
    """
    m = _membership(ctx, membership_id)
    rid = ctx.make_id("rwc_", membership_id, source_txn_id, spend_amount, points)
    today = ctx.now()[:10]
    amount = round(float(spend_amount), 2)
    ctx.create("rewards_ledger", rid, **_ledger_row(
        rid, membership_id, m.get("customer_id", ""), event_type="rewards_clawback",
        entry_date=today, points=int(points), source_txn_id=source_txn_id, spend_amount=amount))
    new_balance = int(m.get("points_balance") or 0) - int(points)
    ctx.update("rewards_memberships", membership_id, points_balance=new_balance)
    return str({"status": "clawed_back", "rewards_entry_id": rid, "membership_id": membership_id,
                "source_txn_id": source_txn_id, "spend_amount": amount, "points": int(points),
                "entry_date": today, "points_balance": new_balance})


@tool(owner="user", rw="write")
def redeem_points_gift_card_91c84320(ctx: ToolContext, membership_id: str, points: int,
                                     payee_name: str, cash_value: float) -> str:
    """Redeem your own Pocketwire Rewards points for a digital gift card.

    You, the member, confirm this redemption yourself. It books one gift card redemption entry
    on your points ledger, dated today, for the points and gift card brand given and with the
    gift card face value given, and subtracts the points from your points balance. The
    redemption appears in the app's points activity with its redemption reference, and the
    digital gift card is delivered within your tier's fulfilment period. The receipt below
    confirms the redemption was booked.

    Args:
        membership_id: Id class — the rewards membership reference number of the member redeeming, as read out by the agent from the rewards membership lookup.
        points: Fixed-format class — the points redeemed, a whole integer number of points in integer points, zero or positive, as told by the agent.
        payee_name: Verbatim class — the gift card brand exactly as the member named it in the conversation, copied character for character with its original wording and punctuation (verbatim).
        cash_value: Fixed-format class — the gift card face value in USD, 2 decimal places, as told by the agent.

    Returns:
        A text rendering of a dictionary with these fields: status (the text "redeemed" when the
        redemption was booked), redemption_reference (the redemption reference shown in the
        app), rewards_entry_id (reference number of the new points entry), points (integer
        points redeemed), payee_name (gift card brand), cash_value (face value in USD, 2 decimal
        places), entry_date (redemption date, YYYY-MM-DD) and points_balance (the integer points
        balance left once the redemption is booked).
    """
    m = _membership(ctx, membership_id)
    rid = ctx.make_id("rwr_", membership_id, points, payee_name, cash_value)
    ref = "RDM-" + rid[4:12].upper()
    today = ctx.now()[:10]
    value = round(float(cash_value), 2)
    ctx.create("rewards_ledger", rid, **_ledger_row(
        rid, membership_id, m.get("customer_id", ""), event_type="rewards_redemption",
        entry_date=today, points=int(points), redemption_reference=ref,
        redemption_type="gift_card", cash_value=value, payee_name=payee_name))
    new_balance = int(m.get("points_balance") or 0) - int(points)
    ctx.update("rewards_memberships", membership_id, points_balance=new_balance)
    return str({"status": "redeemed", "redemption_reference": ref, "rewards_entry_id": rid,
                "points": int(points), "payee_name": payee_name, "cash_value": value,
                "entry_date": today, "points_balance": new_balance})


@tool(owner="agent", rw="write")
def credit_late_fulfilment_courtesy_4e426c94(ctx: ToolContext, membership_id: str, source_txn_id: str,
                                             points: int) -> str:
    """Credit Pocketwire Rewards courtesy points for a gift card or charity redemption fulfilled late.

    Books one courtesy credit entry on the member's points ledger, dated today and linked to the
    late redemption, and adds the points to the membership's points balance. Courtesy points
    are available to redeem at once. The member sees the courtesy credit in the app's points
    activity and a higher points balance straight away. The receipt below confirms the entry
    was booked.

    Args:
        membership_id: Id class — the rewards membership reference number of the member being credited, as returned by the rewards membership lookup.
        source_txn_id: Id class — the rewards entry reference number of the late gift card or charity redemption being compensated (the redemption entry itself, not its fulfilment entry), as shown by the rewards activity lookup.
        points: Fixed-format class — the courtesy points credited, a whole integer number of points in integer points, zero or positive.

    Returns:
        A text rendering of a dictionary with these fields: status (the text "credited" when the
        entry was booked), rewards_entry_id (reference number of the new points entry),
        membership_id, source_txn_id (the compensated redemption), points (integer points
        credited), entry_date (booking date, YYYY-MM-DD) and points_balance (the membership's
        integer points balance including this credit).
    """
    m = _membership(ctx, membership_id)
    rid = ctx.make_id("rwg_", membership_id, source_txn_id, points)
    today = ctx.now()[:10]
    ctx.create("rewards_ledger", rid, **_ledger_row(
        rid, membership_id, m.get("customer_id", ""), event_type="rewards_goodwill_credit",
        entry_date=today, points=int(points), source_txn_id=source_txn_id))
    new_balance = int(m.get("points_balance") or 0) + int(points)
    ctx.update("rewards_memberships", membership_id, points_balance=new_balance)
    return str({"status": "credited", "rewards_entry_id": rid, "membership_id": membership_id,
                "source_txn_id": source_txn_id, "points": int(points), "entry_date": today,
                "points_balance": new_balance})


@tool(owner="agent", rw="write")
def credit_quarterly_milestone_bonus_7b7b30cf(ctx: ToolContext, membership_id: str, bonus_period: str,
                                              points: int) -> str:
    """Credit a Pocketwire Rewards quarterly spend milestone bonus to a member's points balance.

    Books one quarterly milestone bonus entry on the member's points ledger, dated today, for the
    calendar quarter given, and adds the points to the membership's points balance. The member sees the bonus in
    the app's points activity and a higher points balance straight away. The receipt below
    confirms the entry was booked.

    Args:
        membership_id: Id class — the rewards membership reference number of the member being credited, as returned by the rewards membership lookup.
        bonus_period: Fixed-format class — the period the bonus is for, written as YYYY-Qn for a quarterly milestone, YYYY for an anniversary; this tool books quarterly milestone bonuses only, so give the four-digit year, a hyphen, the letter Q and the quarter number 1 to 4.
        points: Fixed-format class — the bonus points credited, a whole integer number of points in integer points, zero or positive.

    Returns:
        A text rendering of a dictionary with these fields: status (the text "credited" when the
        entry was booked), rewards_entry_id (reference number of the new points entry),
        membership_id, bonus_type (always the text "quarterly_milestone"), bonus_period (as
        booked), points (integer points credited), entry_date (booking date, YYYY-MM-DD) and
        points_balance (the membership's integer points balance including this credit).
    """
    m = _membership(ctx, membership_id)
    bonus_type = "quarterly_milestone"
    rid = ctx.make_id("rwq_", membership_id, bonus_type, bonus_period, points)
    today = ctx.now()[:10]
    ctx.create("rewards_ledger", rid, **_ledger_row(
        rid, membership_id, m.get("customer_id", ""), event_type="rewards_bonus",
        entry_date=today, points=int(points), bonus_type=bonus_type, bonus_period=bonus_period))
    new_balance = int(m.get("points_balance") or 0) + int(points)
    ctx.update("rewards_memberships", membership_id, points_balance=new_balance)
    return str({"status": "credited", "rewards_entry_id": rid, "membership_id": membership_id,
                "bonus_type": bonus_type, "bonus_period": bonus_period, "points": int(points),
                "entry_date": today, "points_balance": new_balance})


@tool(owner="user", rw="write")
def donate_points_to_charity_56fec22b(ctx: ToolContext, membership_id: str, points: int,
                                      payee_name: str, cash_value: float) -> str:
    """Donate your own Pocketwire Rewards points to a Pocketwire partner charity.

    You, the member, confirm this donation yourself. It books one charity redemption entry on
    your points ledger, dated today, for the points and partner charity given and with the
    donation value given, and subtracts the points from your points balance. The donation
    appears in the app's points activity with its redemption reference and is sent to the
    charity within your tier's fulfilment period. The receipt below confirms the donation was
    booked.

    Args:
        membership_id: Id class — the rewards membership reference number of the member donating, as read out by the agent from the rewards membership lookup.
        points: Fixed-format class — the points donated, a whole integer number of points in integer points, zero or positive, as told by the agent.
        payee_name: Verbatim class — the partner charity exactly as the member named it in the conversation, copied character for character with its original wording and punctuation (verbatim).
        cash_value: Fixed-format class — the donation value in USD, 2 decimal places, as told by the agent.

    Returns:
        A text rendering of a dictionary with these fields: status (the text "donated" when the
        donation was booked), redemption_reference (the redemption reference shown in the app),
        rewards_entry_id (reference number of the new points entry), points (integer points
        donated), payee_name (partner charity), cash_value (donation value in USD, 2 decimal
        places), entry_date (donation date, YYYY-MM-DD) and points_balance (the integer points
        balance left once the donation is booked).
    """
    m = _membership(ctx, membership_id)
    rid = ctx.make_id("rwd_", membership_id, points, payee_name, cash_value)
    ref = "RDM-" + rid[4:12].upper()
    today = ctx.now()[:10]
    value = round(float(cash_value), 2)
    ctx.create("rewards_ledger", rid, **_ledger_row(
        rid, membership_id, m.get("customer_id", ""), event_type="rewards_redemption",
        entry_date=today, points=int(points), redemption_reference=ref,
        redemption_type="charity", cash_value=value, payee_name=payee_name))
    new_balance = int(m.get("points_balance") or 0) - int(points)
    ctx.update("rewards_memberships", membership_id, points_balance=new_balance)
    return str({"status": "donated", "redemption_reference": ref, "rewards_entry_id": rid,
                "points": int(points), "payee_name": payee_name, "cash_value": value,
                "entry_date": today, "points_balance": new_balance})

"""Hidden task tools of the loyalty_points_and_elite_status difficulty (Ashbury Rewards).

Each tool lands one atomic posting on an Ashbury Rewards account: it records the transaction and
moves the account quantity the transaction belongs to. Values are computed by the agent from the
Ashbury Rewards rules and passed in; the tools judge no eligibility and compute nothing.
"""

from erlbench import ToolContext, tool


_BLANK_TXN = {"points": 0, "nights": 0, "reservation_id": None, "certificate_id": None, "earning_source": "",
              "eligible_spend_usd": 0.0, "purchase_amount_usd": 0.0, "counterparty_member_id": None,
              "related_transaction_id": None, "promotion_code": ""}


@tool(owner="agent", rw="write")
def post_award_stay_night_credits_8b07b6a3(ctx: ToolContext, loyalty_member_id: str, reservation_id: str,
                                           earning_source: str, nights: int) -> str:
    """Post the elite night credits of a completed Reward Night Rate stay to an Ashbury Rewards
    account. One call records one night-credit transaction of source stay_nights that names the
    award stay, dated today, and adds the credits to the elite night credits of the current
    calendar year shown on the membership. The member sees the credits in their account activity
    and in their elite night total straight away.

    Args:
        loyalty_member_id: Id class — reference number of the Ashbury Rewards membership credited,
            as returned by the membership lookup for the verified member.
        reservation_id: Id class — reference number of the completed Reward Night Rate reservation
            the credits are for, as returned by the reservation lookup.
        earning_source: Enum class — business source recorded on the transaction; the closed set
            for this posting is stay_nights — night credits earned by nights stayed on a completed
            stay.
        nights: Fixed-format class — elite night credits posted for the stay, a whole number written
            as integer nights, always positive; 0 on points transactions (integer, no decimals, no unit
            text).

    Returns:
        A dictionary string with transaction_id (reference number of the night-credit transaction
        created), loyalty_member_id (membership credited), reservation_id (award stay named),
        earning_source (source recorded),
        nights (integer credits posted), posted_date (YYYY-MM-DD posting date) and
        elite_night_credits (integer elite night total of the membership once the credits are
        added). A returned transaction_id means the credits are posted.
    """
    found = ctx.find("loyalty_memberships", loyalty_member_id=loyalty_member_id)
    member = found[0] if found else {}
    rid = ctx.make_id("lt_", earning_source, loyalty_member_id, reservation_id, nights)
    ctx.create("loyalty_transactions", rid, **dict(_BLANK_TXN, transaction_id=rid, loyalty_member_id=loyalty_member_id,
                                                   customer_id=member.get("customer_id", ""),
                                                   event_type="loyalty_night_credit", nights=int(nights),
                                                   reservation_id=reservation_id, posted_date=ctx.now()[:10],
                                                   earning_source=earning_source))
    total = int(member.get("elite_night_credits") or 0) + int(nights)
    ctx.update("loyalty_memberships", loyalty_member_id, elite_night_credits=total)
    return str({"transaction_id": rid, "loyalty_member_id": loyalty_member_id,
                "reservation_id": reservation_id, "earning_source": earning_source, "nights": int(nights),
                "posted_date": ctx.now()[:10], "elite_night_credits": total})


@tool(owner="agent", rw="write")
def post_relocation_compensation_5afb8ff3(ctx: ToolContext, loyalty_member_id: str, reservation_id: str,
                                          earning_source: str, promotion_code: str, points: int) -> str:
    """Post relocation compensation points to an Ashbury Rewards account for a reservation the hotel
    relocated. One call records one points bonus transaction of source relocation_compensation that
    names the relocated reservation, dated today, and adds the points to the points balance of the
    membership. The member sees the compensation in their account activity and in their balance
    straight away.

    Args:
        loyalty_member_id: Id class — reference number of the Ashbury Rewards membership credited,
            as returned by the membership lookup for the verified member.
        reservation_id: Id class — reference number of the relocated reservation the compensation is
            for, as returned by the reservation lookup.
        earning_source: Enum class — business source recorded on the transaction; the closed set
            for this posting is relocation_compensation — points owed because the hotel relocated a
            guaranteed reservation.
        promotion_code: Fixed-format class — code of a registered promotion the points would be
            earned under, written as upper-case letters and digits, up to 10 characters; relocation
            compensation is earned under no promotion, so the value is the empty string "".
        points: Fixed-format class — compensation points posted, a whole number written as integer
            points, always positive; 0 on night-credit transactions (integer, no decimals, no
            thousands separators).

    Returns:
        A dictionary string with transaction_id (reference number of the bonus transaction created),
        loyalty_member_id (membership credited), reservation_id (relocated reservation named),
        earning_source (source recorded),
        points (integer points posted), posted_date (YYYY-MM-DD posting date) and points_balance
        (integer points balance once the compensation is added). A returned transaction_id means
        the compensation is posted.
    """
    found = ctx.find("loyalty_memberships", loyalty_member_id=loyalty_member_id)
    member = found[0] if found else {}
    rid = ctx.make_id("lt_", earning_source, loyalty_member_id, reservation_id, promotion_code, points)
    ctx.create("loyalty_transactions", rid, **dict(_BLANK_TXN, transaction_id=rid, loyalty_member_id=loyalty_member_id,
                                                   customer_id=member.get("customer_id", ""),
                                                   event_type="loyalty_points_bonus", points=int(points),
                                                   reservation_id=reservation_id, posted_date=ctx.now()[:10],
                                                   earning_source=earning_source,
                                                   promotion_code=promotion_code))
    balance = int(member.get("points_balance") or 0) + int(points)
    ctx.update("loyalty_memberships", loyalty_member_id, points_balance=balance)
    return str({"transaction_id": rid, "loyalty_member_id": loyalty_member_id,
                "reservation_id": reservation_id, "earning_source": earning_source, "points": int(points),
                "posted_date": ctx.now()[:10], "points_balance": balance})


@tool(owner="agent", rw="write")
def return_award_cancellation_points_76b4b6d2(ctx: ToolContext, loyalty_member_id: str, reservation_id: str,
                                              related_transaction_id: str, points: int) -> str:
    """Return points to an Ashbury Rewards account from the redemption of a cancelled or no-show
    Reward Night Rate reservation. One call records one redeposit transaction of source
    award_redeposit that names the award reservation and the redemption the points come back from,
    dated today, and adds the points to the points balance of the membership. The member sees the
    returned points in their account activity and in their balance straight away.

    Args:
        loyalty_member_id: Id class — reference number of the Ashbury Rewards membership credited,
            as returned by the membership lookup for the verified member.
        reservation_id: Id class — reference number of the award reservation the points were
            redeemed for, as returned by the reservation lookup.
        related_transaction_id: Id class — reference number of the award redemption transaction the
            points are returned from, as returned by the account activity lookup.
        points: Fixed-format class — points returned, a whole number written as integer points,
            always positive; 0 on night-credit transactions (integer, no decimals, no thousands
            separators).

    Returns:
        A dictionary string with transaction_id (reference number of the redeposit transaction
        created), loyalty_member_id (membership credited), reservation_id (award reservation named),
        related_transaction_id (redemption named), points (integer points returned), posted_date
        (YYYY-MM-DD posting date) and points_balance (integer points balance once the points are
        added). A returned transaction_id means the points are back on the account.
    """
    found = ctx.find("loyalty_memberships", loyalty_member_id=loyalty_member_id)
    member = found[0] if found else {}
    rid = ctx.make_id("lt_", "award_redeposit", loyalty_member_id, reservation_id, related_transaction_id,
                      points)
    ctx.create("loyalty_transactions", rid, **dict(_BLANK_TXN, transaction_id=rid, loyalty_member_id=loyalty_member_id,
                                                   customer_id=member.get("customer_id", ""),
                                                   event_type="loyalty_points_redeposit", points=int(points),
                                                   reservation_id=reservation_id, posted_date=ctx.now()[:10],
                                                   earning_source="award_redeposit",
                                                   related_transaction_id=related_transaction_id))
    balance = int(member.get("points_balance") or 0) + int(points)
    ctx.update("loyalty_memberships", loyalty_member_id, points_balance=balance)
    return str({"transaction_id": rid, "loyalty_member_id": loyalty_member_id,
                "reservation_id": reservation_id, "related_transaction_id": related_transaction_id,
                "points": int(points), "posted_date": ctx.now()[:10], "points_balance": balance})


@tool(owner="user", rw="write")
def give_points_to_member_c374aed0(ctx: ToolContext, loyalty_member_id: str, counterparty_member_id: str,
                                   points: int) -> str:
    """The member gives points from their own Ashbury Rewards account to another member's account.
    One call records the giver's transfer transaction of source points_transfer naming the receiving
    membership and the receiver's arrival transaction mirroring it, both dated today, takes the
    points off the giver's points balance and adds them to the receiver's. The transfer is final
    and visible at once in both accounts' activity and balances.

    Args:
        loyalty_member_id: Id class — reference number of the giver's own Ashbury Rewards
            membership, as read out by the agent from the membership lookup.
        counterparty_member_id: Id class — reference number of the receiving member's Ashbury
            Rewards membership, as read out by the agent from the membership lookup of the member
            number the giver named.
        points: Fixed-format class — points given, a whole number written as integer points, always
            positive; 0 on night-credit transactions (integer, no decimals, no thousands separators),
            as stated by the agent.

    Returns:
        A dictionary string with transaction_id (reference number of the giver's transfer
        transaction), arrival_transaction_id (reference number of the receiver's arrival
        transaction), loyalty_member_id (giver's membership), counterparty_member_id (receiver's
        membership), receiver_name (full name on the receiving member's profile), points (integer
        points given), posted_date (YYYY-MM-DD transfer date) and
        points_balance (integer points balance of the giver once the points are taken off). A
        returned transaction_id means the transfer is complete.
    """
    found = ctx.find("loyalty_memberships", loyalty_member_id=loyalty_member_id)
    giver = found[0] if found else {}
    found = ctx.find("loyalty_memberships", loyalty_member_id=counterparty_member_id)
    receiver = found[0] if found else {}
    found = ctx.find("customers", customer_id=receiver.get("customer_id", ""))
    receiver_name = found[0].get("name", "") if found else ""
    rid = ctx.make_id("lt_", "points_transfer_out", loyalty_member_id, counterparty_member_id, points)
    ctx.create("loyalty_transactions", rid, **dict(_BLANK_TXN, transaction_id=rid, loyalty_member_id=loyalty_member_id,
                                                   customer_id=giver.get("customer_id", ""),
                                                   event_type="loyalty_points_transfer_out", points=int(points),
                                                   posted_date=ctx.now()[:10], earning_source="points_transfer",
                                                   counterparty_member_id=counterparty_member_id))
    arrival = ctx.make_id("lt_", "points_transfer_in", rid)
    ctx.create("loyalty_transactions", arrival, **dict(_BLANK_TXN, transaction_id=arrival,
                                                       loyalty_member_id=counterparty_member_id,
                                                       customer_id=receiver.get("customer_id", ""),
                                                       event_type="loyalty_points_transfer_in", points=int(points),
                                                       posted_date=ctx.now()[:10], earning_source="points_transfer",
                                                       counterparty_member_id=loyalty_member_id,
                                                       related_transaction_id=rid))
    balance = int(giver.get("points_balance") or 0) - int(points)
    ctx.update("loyalty_memberships", loyalty_member_id, points_balance=balance)
    ctx.update("loyalty_memberships", counterparty_member_id,
               points_balance=int(receiver.get("points_balance") or 0) + int(points))
    return str({"transaction_id": rid, "arrival_transaction_id": arrival,
                "loyalty_member_id": loyalty_member_id, "counterparty_member_id": counterparty_member_id,
                "receiver_name": receiver_name,
                "points": int(points), "posted_date": ctx.now()[:10], "points_balance": balance})


@tool(owner="agent", rw="write")
def post_stay_elite_bonus_1ee6f132(ctx: ToolContext, loyalty_member_id: str, reservation_id: str,
                                   earning_source: str, points: int) -> str:
    """Post the elite bonus of a completed stay to an Ashbury Rewards account. One call records one
    stay earning transaction that names the stay, dated today, with the elite bonus points, and adds
    the points to the points balance of the membership. The member sees the bonus in their account
    activity and in their balance straight away.

    Args:
        loyalty_member_id: Id class — reference number of the Ashbury Rewards membership credited,
            as returned by the membership lookup for the verified member.
        reservation_id: Id class — reference number of the completed stay the bonus is for, as
            returned by the reservation lookup.
        earning_source: Enum class — earning component recorded on the transaction; the closed set
            for this posting is stay_elite_bonus — the elite tier bonus earned on top of the stay's
            base points.
        points: Fixed-format class — elite bonus points posted, a whole number written as integer
            points, always positive; 0 on night-credit transactions (integer, no decimals, no thousands
            separators).

    Returns:
        A dictionary string with transaction_id (reference number of the earning transaction created),
        loyalty_member_id (membership credited), reservation_id (stay named), earning_source
        (component recorded), points (integer points posted), posted_date (YYYY-MM-DD posting date)
        and points_balance (integer points balance once the bonus is added). A returned
        transaction_id means the bonus is posted.
    """
    found = ctx.find("loyalty_memberships", loyalty_member_id=loyalty_member_id)
    member = found[0] if found else {}
    rid = ctx.make_id("lt_", earning_source, loyalty_member_id, reservation_id, points)
    ctx.create("loyalty_transactions", rid, **dict(_BLANK_TXN, transaction_id=rid, loyalty_member_id=loyalty_member_id,
                                                   customer_id=member.get("customer_id", ""),
                                                   event_type="loyalty_points_earn", points=int(points),
                                                   reservation_id=reservation_id, posted_date=ctx.now()[:10],
                                                   earning_source=earning_source))
    balance = int(member.get("points_balance") or 0) + int(points)
    ctx.update("loyalty_memberships", loyalty_member_id, points_balance=balance)
    return str({"transaction_id": rid, "loyalty_member_id": loyalty_member_id, "reservation_id": reservation_id,
                "earning_source": earning_source, "points": int(points), "posted_date": ctx.now()[:10],
                "points_balance": balance})


@tool(owner="agent", rw="write")
def post_stay_welcome_points_0494e852(ctx: ToolContext, loyalty_member_id: str, reservation_id: str,
                                      earning_source: str, promotion_code: str, points: int) -> str:
    """Post the welcome points of a completed elite stay to an Ashbury Rewards account. One call
    records one points bonus transaction that names the stay, dated today, and adds the points to the
    points balance of the membership. The member sees the welcome points in their account activity
    and in their balance straight away.

    Args:
        loyalty_member_id: Id class — reference number of the Ashbury Rewards membership credited,
            as returned by the membership lookup for the verified member.
        reservation_id: Id class — reference number of the completed stay the welcome points are
            for, as returned by the reservation lookup.
        earning_source: Enum class — business source recorded on the transaction; the closed set
            for this posting is welcome_amenity — the welcome points an elite member receives for a
            stay.
        promotion_code: Fixed-format class — code of a registered promotion the points would be
            earned under, written as upper-case letters and digits, up to 10 characters; welcome
            points are earned under no promotion, so the value is the empty string "".
        points: Fixed-format class — welcome points posted, a whole number written as integer points,
            always positive; 0 on night-credit transactions (integer, no decimals, no thousands
            separators).

    Returns:
        A dictionary string with transaction_id (reference number of the bonus transaction created),
        loyalty_member_id (membership credited), reservation_id (stay named), earning_source (source
        recorded), points (integer points posted), posted_date (YYYY-MM-DD posting date) and
        points_balance (integer points balance once the welcome points are added). A returned
        transaction_id means the welcome points are posted.
    """
    found = ctx.find("loyalty_memberships", loyalty_member_id=loyalty_member_id)
    member = found[0] if found else {}
    rid = ctx.make_id("lt_", earning_source, loyalty_member_id, reservation_id, promotion_code, points)
    ctx.create("loyalty_transactions", rid, **dict(_BLANK_TXN, transaction_id=rid, loyalty_member_id=loyalty_member_id,
                                                   customer_id=member.get("customer_id", ""),
                                                   event_type="loyalty_points_bonus", points=int(points),
                                                   reservation_id=reservation_id, posted_date=ctx.now()[:10],
                                                   earning_source=earning_source, promotion_code=promotion_code))
    balance = int(member.get("points_balance") or 0) + int(points)
    ctx.update("loyalty_memberships", loyalty_member_id, points_balance=balance)
    return str({"transaction_id": rid, "loyalty_member_id": loyalty_member_id, "reservation_id": reservation_id,
                "earning_source": earning_source, "points": int(points), "posted_date": ctx.now()[:10],
                "points_balance": balance})


@tool(owner="agent", rw="write")
def reverse_corrected_stay_points_b6469913(ctx: ToolContext, loyalty_member_id: str, reservation_id: str,
                                           related_transaction_id: str, eligible_spend_usd: float,
                                           points: int) -> str:
    """Take back from an Ashbury Rewards account the points earned on stay spend that a folio
    correction removed. One call records one stay credit reversal transaction of source
    stay_credit_reversal that names the stay, the base points transaction it reduces and the eligible
    spend removed, dated today, and takes the points off the points balance of the membership, even
    below zero. The member sees the reversal in their account activity and the lower balance straight
    away.

    Args:
        loyalty_member_id: Id class — reference number of the Ashbury Rewards membership debited,
            as returned by the membership lookup for the verified member.
        reservation_id: Id class — reference number of the stay whose folio was corrected, as returned
            by the reservation or folio lookup.
        related_transaction_id: Id class — reference number of the stay's base points earning
            transaction that the reversal reduces, as returned by the account activity lookup.
        eligible_spend_usd: Fixed-format class — eligible spend removed by the folio correction, in USD,
            2 decimal places, written as a plain number such as 1234.50 with no currency sign; the tool
            stores it rounded half to even to 2 decimal places.
        points: Fixed-format class — points taken back, a whole number written as integer points,
            always positive; 0 on night-credit transactions (integer, no decimals, no thousands
            separators).

    Returns:
        A dictionary string with transaction_id (reference number of the reversal transaction created),
        loyalty_member_id (membership debited), reservation_id (stay named), related_transaction_id
        (earning transaction reduced), eligible_spend_usd (USD removed, 2 decimal places), points
        (integer points taken back), posted_date (YYYY-MM-DD posting date) and points_balance (integer
        points balance once the points are taken off). A returned transaction_id means the reversal is
        posted.
    """
    found = ctx.find("loyalty_memberships", loyalty_member_id=loyalty_member_id)
    member = found[0] if found else {}
    rid = ctx.make_id("lt_", "stay_credit_reversal", loyalty_member_id, reservation_id, related_transaction_id,
                      eligible_spend_usd, points)
    ctx.create("loyalty_transactions", rid, **dict(_BLANK_TXN, transaction_id=rid, loyalty_member_id=loyalty_member_id,
                                                   customer_id=member.get("customer_id", ""),
                                                   event_type="loyalty_points_reversal", points=int(points),
                                                   reservation_id=reservation_id, posted_date=ctx.now()[:10],
                                                   earning_source="stay_credit_reversal",
                                                   eligible_spend_usd=round(float(eligible_spend_usd), 2),
                                                   related_transaction_id=related_transaction_id))
    balance = int(member.get("points_balance") or 0) - int(points)
    ctx.update("loyalty_memberships", loyalty_member_id, points_balance=balance)
    return str({"transaction_id": rid, "loyalty_member_id": loyalty_member_id, "reservation_id": reservation_id,
                "related_transaction_id": related_transaction_id,
                "eligible_spend_usd": round(float(eligible_spend_usd), 2), "points": int(points),
                "posted_date": ctx.now()[:10], "points_balance": balance})


@tool(owner="user", rw="write")
def buy_points_b3668dab(ctx: ToolContext, loyalty_member_id: str, points: int, purchase_amount_usd: float,
                        posted_date: str) -> str:
    """The member buys Ashbury Rewards points for their own account and pays with their card. One call
    records one points purchase transaction of source points_purchase with the points bought and the
    price charged, dated on the purchase date given, and adds the points to the points balance of the
    membership. Purchased points are visible at once in the account activity and balance.

    Args:
        loyalty_member_id: Id class — reference number of the member's own Ashbury Rewards
            membership, as read out by the agent from the membership lookup.
        points: Fixed-format class — points bought, a whole number written as integer points, always
            positive; 0 on night-credit transactions (integer, no decimals, no thousands separators), as
            stated by the agent.
        purchase_amount_usd: Fixed-format class — price charged for the points before tax, in USD, 2
            decimal places, written as a plain number such as 1234.50 with no currency sign; the tool
            stores it rounded half to even to 2 decimal places, as stated by the agent.
        posted_date: Fixed-format class — calendar date of the purchase, written YYYY-MM-DD, which is
            today's date as stated by the agent.

    Returns:
        A dictionary string with transaction_id (reference number of the purchase transaction),
        loyalty_member_id (membership credited), points (integer points bought), purchase_amount_usd
        (USD charged, 2 decimal places), posted_date (YYYY-MM-DD purchase date) and points_balance
        (integer points balance once the points are added). A returned transaction_id means the
        purchase is complete.
    """
    found = ctx.find("loyalty_memberships", loyalty_member_id=loyalty_member_id)
    member = found[0] if found else {}
    rid = ctx.make_id("lt_", "points_purchase", loyalty_member_id, points, purchase_amount_usd, posted_date)
    ctx.create("loyalty_transactions", rid, **dict(_BLANK_TXN, transaction_id=rid, loyalty_member_id=loyalty_member_id,
                                                   customer_id=member.get("customer_id", ""),
                                                   event_type="loyalty_points_purchase", points=int(points),
                                                   posted_date=posted_date, earning_source="points_purchase",
                                                   purchase_amount_usd=round(float(purchase_amount_usd), 2)))
    balance = int(member.get("points_balance") or 0) + int(points)
    ctx.update("loyalty_memberships", loyalty_member_id, points_balance=balance)
    return str({"transaction_id": rid, "loyalty_member_id": loyalty_member_id, "points": int(points),
                "purchase_amount_usd": round(float(purchase_amount_usd), 2), "posted_date": posted_date,
                "points_balance": balance})

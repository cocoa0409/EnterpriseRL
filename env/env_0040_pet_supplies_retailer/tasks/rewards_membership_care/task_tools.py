"""Hidden task tools of the rewards_membership_care difficulty (Pals Rewards and Tailwise Plus).

Every tool here performs one atomic booking on a customer's single rewards membership and
nothing else: it never checks eligibility, never aggregates history and never works out an
amount; the value it books is the one passed in.
"""

from erlbench import ToolContext, tool

# Calendar helpers (pure date arithmetic on 'YYYY-MM-DD' strings; no clock is read here).
_LEAP = lambda y: y % 4 == 0 and (y % 100 != 0 or y % 400 == 0)
_MDAYS = lambda y, m: [31, 29 if _LEAP(y) else 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31][m - 1]
_YMD = lambda s: (int(s[0:4]), int(s[5:7]), int(s[8:10]))
_FMT = lambda y, m, d: f"{y:04d}-{m:02d}-{d:02d}"
_PREV = lambda y, m, d: (y, m, d - 1) if d > 1 else ((y, m - 1, _MDAYS(y, m - 1)) if m > 1 else (y - 1, 12, 31))
_NEXT = lambda y, m, d: (y, m, d + 1) if d < _MDAYS(y, m) else ((y, m + 1, 1) if m < 12 else (y + 1, 1, 1))
_PLUS_YEAR = lambda y, m, d: (y + 1, m, min(d, _MDAYS(y + 1, m)))
_PLUS_MONTH = lambda y, m, d: (y, m + 1, min(d, _MDAYS(y, m + 1))) if m < 12 else (y + 1, 1, min(d, 31))


@tool(owner="agent", rw="write")
def post_missing_points_02f0bcb5(ctx: ToolContext, membership_id: str, source_category: str,
                                 source_event_id: str, purchase_date: str,
                                 qualifying_spend_usd: float, points: int) -> str:
    """Post Pals Rewards points that a purchase should have earned but that never reached the
    customer's rewards account. One call books one earning entry on the rewards ledger of the
    membership, tied to the purchase record it was earned on and dated on the purchase date, and
    adds the posted points to the membership's points balance. Afterwards the customer sees the
    earning in their points history and the higher balance; the receipt carries the new ledger
    entry's reference number.

    Args:
        membership_id: Id class — the reference number of the customer's Pals Rewards membership,
            read from the membership lookup for this customer.
        source_category: Enum class — the program the purchase was made in: autoship for a charged
            Autoship shipment; rx for a pharmacy fill; groom for a salon pass purchase, club fee or
            salon checkout; order for a retail order line; train for a training enrollment; vet for a
            wellness plan payment; livepet for a live animal purchase; none when the entry is not tied
            to a purchase in any program.
        source_event_id: Id class — the reference number of the purchase record the points were
            earned on (for example the Autoship shipment charge entry), read from that program's
            history lookup.
        purchase_date: Fixed-format class — the date the purchase was made, as YYYY-MM-DD, copied
            from the purchase record; it becomes the date of the earning entry.
        qualifying_spend_usd: Fixed-format class — the purchase amount that earns points, in USD
            with 2 decimal places, rounded half up to the cent.
        points: Fixed-format class — the number of points to post, a whole non-negative number
            given as integer, points.

    Returns:
        A dict confirming the posting: status ("posted" when the entry was booked);
        member_event_id (string, the reference number of the new earning entry); membership_id
        (string, the membership credited); points (integer, points posted); qualifying_spend_usd
        (number, USD with 2 decimals); points_balance (integer, the membership's points balance
        after the posting).
    """
    rid = ctx.make_id("mev_", membership_id, source_category, source_event_id, purchase_date,
                      qualifying_spend_usd, points)
    mem = ctx.find("member_memberships", membership_id=membership_id)
    row = mem[0] if mem else {}
    balance = int(row.get("points_balance") or 0) + int(points)
    ctx.create("member_events", rid, member_event_id=rid, membership_id=membership_id,
               customer_id=row.get("customer_id"), event_type="member_points_earn",
               event_date=purchase_date, source_category=source_category,
               source_event_id=source_event_id,
               qualifying_spend_usd=round(float(qualifying_spend_usd), 2), points=int(points),
               bonus_kind="none")
    ctx.update("member_memberships", membership_id, points_balance=balance)
    return str({"status": "posted", "member_event_id": rid, "membership_id": membership_id,
                "points": int(points), "qualifying_spend_usd": round(float(qualifying_spend_usd), 2),
                "points_balance": balance})


@tool(owner="agent", rw="write")
def apply_earned_tier_ebf561a6(ctx: ToolContext, membership_id: str, new_tier: str,
                               upgrade_bonus_points: int) -> str:
    """Apply a free Pals Rewards tier that the customer has earned by spend and post the bonus
    that comes with it. One call moves the membership to the stated tier effective today,
    records the change as an upgrade earned by spend, books one tier-upgrade bonus entry on the
    rewards ledger dated today, and adds the bonus to the points balance. Afterwards the customer
    sees the new tier on the account and the bonus in the points history; the receipt carries
    the bonus entry's reference number.

    Args:
        membership_id: Id class — the reference number of the customer's Pals Rewards membership,
            read from the membership lookup for this customer.
        new_tier: Enum class — the tier the membership moves to: Pals Rewards Member is the entry
            tier every member holds without qualifying spend, so it is never an upgrade target;
            Pals Rewards Insider is the free tier earned by the Insider qualifying spend; Pals
            Rewards VIP is the free tier earned by the VIP qualifying spend; Tailwise Plus Monthly
            is a paid monthly tier that is bought, never earned by spend, so it is not a target of
            this action; Tailwise Plus Annual is a paid annual tier that is bought, never earned by
            spend, so it is not a target of this action; Tailwise Plus Premier Annual is the paid
            premier annual tier that is bought, never earned by spend, so it is not a target of
            this action.
        upgrade_bonus_points: Fixed-format class — the tier-upgrade bonus to post, a whole
            non-negative number given as integer, points.

    Returns:
        A dict confirming the change: status ("tier_applied" when the tier and the bonus were
        booked); membership_id (string); variant_name (string, the tier now held); tier_effective_on
        (string, YYYY-MM-DD, today); member_event_id (string, the reference number of the bonus
        entry); upgrade_bonus_points (integer, points posted); points_balance (integer, the balance
        after the bonus).
    """
    today = ctx.now()[:10]
    rid = ctx.make_id("mev_", membership_id, new_tier, upgrade_bonus_points)
    mem = ctx.find("member_memberships", membership_id=membership_id)
    row = mem[0] if mem else {}
    balance = int(row.get("points_balance") or 0) + int(upgrade_bonus_points)
    ctx.update("member_memberships", membership_id, variant_name=new_tier, tier_effective_on=today,
               last_change_reason="spend_upgrade", points_balance=balance)
    ctx.create("member_events", rid, member_event_id=rid, membership_id=membership_id,
               customer_id=row.get("customer_id"), event_type="member_bonus_points", event_date=today,
               source_category="none", bonus_kind="tier_upgrade", points=int(upgrade_bonus_points))
    return str({"status": "tier_applied", "membership_id": membership_id, "variant_name": new_tier,
                "tier_effective_on": today, "member_event_id": rid,
                "upgrade_bonus_points": int(upgrade_bonus_points), "points_balance": balance})


@tool(owner="user", rw="write")
def buy_plus_tier_1a1727fb(ctx: ToolContext, membership_id: str, plus_tier: str,
                           first_charge_usd: float, enrollment_bonus_points: int) -> str:
    """Buy a Tailwise Plus paid tier on your own Pals Rewards membership and pay its first fee
    today with the card on file. One call moves the membership to the paid tier you choose
    starting today, opens a paid term of one billing cycle (one month for the monthly tier, one
    year for the annual tiers) beginning today with automatic renewal switched on and the next
    fee due the day after the term ends, and books one fee charge for the term in the amount
    stated, and, when an enrollment bonus is stated, books one enrollment bonus entry dated today
    and adds it to the points balance. Afterwards you see the paid tier, its term dates, the fee
    charge and any enrollment bonus on your account; the receipt carries the fee charge's
    reference number.

    Args:
        membership_id: Id class — the reference number of your Pals Rewards membership, as given to
            you by the care agent from the membership record.
        plus_tier: Enum class — the paid tier being bought: Pals Rewards Member is a free tier, not
            something that can be bought here; Pals Rewards Insider is a free tier earned by spend,
            not something that can be bought here; Pals Rewards VIP is a free tier earned by spend,
            not something that can be bought here; Tailwise Plus Monthly when you buy the paid tier
            billed every month; Tailwise Plus Annual when you buy the paid tier billed once a year;
            Tailwise Plus Premier Annual when you buy the premier paid tier billed once a year.
        first_charge_usd: Fixed-format class — the fee charged today for the first term, in USD with
            2 decimal places, rounded half up to the cent, exactly as the care agent quoted it.
        enrollment_bonus_points: Fixed-format class — the enrollment bonus posted with this
            enrollment, a whole non-negative number given as integer, points, as the care agent stated
            it; 0 when no enrollment bonus is due.

    Returns:
        A dict confirming the purchase: status ("purchased" when the tier and the charge were
        booked); membership_id (string); variant_name (string, the paid tier now held);
        plus_term_start (string, YYYY-MM-DD); plus_term_end (string, YYYY-MM-DD, last day of the
        term); next_billing_date (string, YYYY-MM-DD); member_event_id (string, the reference
        number of the fee charge); amount_usd (number, USD with 2 decimals, the fee charged);
        enrollment_bonus_points (integer, points posted as enrollment bonus); points_balance (integer,
        the balance afterwards).
    """
    today = ctx.now()[:10]
    y, m, d = _YMD(today)
    end = _PREV(*(_PLUS_MONTH(y, m, d) if plus_tier == "Tailwise Plus Monthly" else _PLUS_YEAR(y, m, d)))
    term_end = _FMT(*end)
    next_bill = _FMT(*_NEXT(*end))
    rid = ctx.make_id("mev_", membership_id, plus_tier, first_charge_usd, enrollment_bonus_points)
    mem = ctx.find("member_memberships", membership_id=membership_id)
    row = mem[0] if mem else {}
    balance = int(row.get("points_balance") or 0) + int(enrollment_bonus_points)
    ctx.update("member_memberships", membership_id, variant_name=plus_tier, tier_effective_on=today,
               last_change_reason="plus_purchase", plus_term_start=today, plus_term_end=term_end,
               next_billing_date=next_bill, auto_renew=True, trial_end_date=None,
               downgrade_effective_on=None, points_balance=balance)
    if int(enrollment_bonus_points) > 0:
        bid = ctx.make_id("mev_", rid, "enrollment")
        ctx.create("member_events", bid, member_event_id=bid, membership_id=membership_id,
                   customer_id=row.get("customer_id"), event_type="member_bonus_points", event_date=today,
                   source_category="none", bonus_kind="enrollment", points=int(enrollment_bonus_points))
    ctx.create("member_events", rid, member_event_id=rid, membership_id=membership_id,
               customer_id=row.get("customer_id"), event_type="member_fee_charge", event_date=today,
               source_category="none", billing_period_start=today,
               amount_usd=round(float(first_charge_usd), 2))
    return str({"status": "purchased", "membership_id": membership_id, "variant_name": plus_tier,
                "plus_term_start": today, "plus_term_end": term_end, "next_billing_date": next_bill,
                "member_event_id": rid, "amount_usd": round(float(first_charge_usd), 2),
                "enrollment_bonus_points": int(enrollment_bonus_points), "points_balance": balance})


@tool(owner="agent", rw="write")
def reinstate_plus_tier_c2894e52(ctx: ToolContext, membership_id: str, declined_event_id: str,
                                 overdue_fee_usd: float) -> str:
    """Collect the overdue fee of a past-due Tailwise Plus paid tier with the card on file and
    reinstate the paid tier. One call books one fee charge dated today for the billing period
    whose fee was declined, sets the membership back to active, keeps the paid term that the
    declined period opened (it starts on that period's first day and runs one billing cycle) and
    sets the next fee date to the day after that term ends. Afterwards the customer sees the paid
    tier active again, the term dates and the fee collected; the receipt carries the fee charge's
    reference number.

    Args:
        membership_id: Id class — the reference number of the customer's Pals Rewards membership,
            read from the membership lookup for this customer.
        declined_event_id: Id class — the reference number of the declined-fee entry on the
            rewards history whose billing period is being paid, read from the rewards history
            lookup.
        overdue_fee_usd: Fixed-format class — the overdue fee collected today, in USD with 2 decimal
            places, rounded half up to the cent.

    Returns:
        A dict confirming the reinstatement: status ("reinstated" when the fee and the status change
        were booked); membership_id (string); member_event_id (string, the reference number of the
        fee charge); billing_period_start (string, YYYY-MM-DD, first day of the period paid);
        amount_usd (number, USD with 2 decimals); plus_term_start (string, YYYY-MM-DD);
        plus_term_end (string, YYYY-MM-DD); next_billing_date (string, YYYY-MM-DD).
    """
    today = ctx.now()[:10]
    mem = ctx.find("member_memberships", membership_id=membership_id)
    row = mem[0] if mem else {}
    dec = ctx.find("member_events", member_event_id=declined_event_id)
    start = (dec[0].get("billing_period_start") if dec else None) or today
    y, m, d = _YMD(start)
    end = _PREV(*(_PLUS_MONTH(y, m, d) if row.get("variant_name") == "Tailwise Plus Monthly" else _PLUS_YEAR(y, m, d)))
    term_end = _FMT(*end)
    next_bill = _FMT(*_NEXT(*end))
    rid = ctx.make_id("mev_", membership_id, declined_event_id, overdue_fee_usd)
    ctx.create("member_events", rid, member_event_id=rid, membership_id=membership_id,
               customer_id=row.get("customer_id"), event_type="member_fee_charge", event_date=today,
               source_category="none", billing_period_start=start,
               amount_usd=round(float(overdue_fee_usd), 2), original_event_id=declined_event_id)
    ctx.update("member_memberships", membership_id, status="active", plus_term_start=start,
               plus_term_end=term_end, next_billing_date=next_bill)
    return str({"status": "reinstated", "membership_id": membership_id, "member_event_id": rid,
                "billing_period_start": start, "amount_usd": round(float(overdue_fee_usd), 2),
                "plus_term_start": start, "plus_term_end": term_end, "next_billing_date": next_bill})


@tool(owner="agent", rw="write")
def reissue_returned_certificate_0ad7eee8(ctx: ToolContext, membership_id: str, original_event_id: str,
                                          certificate_value_usd: float, validity_days: int) -> str:
    """Reissue a Pals Rewards reward certificate that was used on an order the customer later
    returned. One call books one certificate reissue entry on the rewards ledger, dated today,
    that refers to the certificate it replaces, carries the stated value and stays usable for the
    stated number of calendar days, today counting as day 1. Afterwards the customer sees the
    reissued certificate with its value and last usable day; the receipt carries the reissue
    entry's reference number.

    Args:
        membership_id: Id class — the reference number of the customer's Pals Rewards membership,
            read from the membership lookup for this customer.
        original_event_id: Id class — the reference number of the certificate-issue entry on the
            rewards history being reissued, read from the rewards history lookup.
        certificate_value_usd: Fixed-format class — the value of the reissued certificate in USD
            with 2 decimal places, rounded half up to the cent, copied from the certificate being
            replaced.
        validity_days: Fixed-format class — how long the reissued certificate stays usable, a whole
            number of calendar days given as an integer, today counting as day 1.

    Returns:
        A dict confirming the reissue: status ("reissued" when the entry was booked); member_event_id
        (string, the reference number of the reissue entry); original_event_id (string, the
        certificate replaced); certificate_value_usd (number, USD with 2 decimals);
        certificate_expires_on (string, YYYY-MM-DD, last usable day).
    """
    y, m, d = _YMD(ctx.now()[:10])
    for _ in range(max(int(validity_days), 1) - 1):
        y, m, d = _NEXT(y, m, d)
    expires = _FMT(y, m, d)
    mem = ctx.find("member_memberships", membership_id=membership_id)
    row = mem[0] if mem else {}
    rid = ctx.make_id("mev_", membership_id, original_event_id, certificate_value_usd, validity_days)
    ctx.create("member_events", rid, member_event_id=rid, membership_id=membership_id,
               customer_id=row.get("customer_id"), event_type="member_certificate_reissue",
               event_date=ctx.now()[:10], source_category="none", original_event_id=original_event_id,
               certificate_value_usd=round(float(certificate_value_usd), 2), certificate_expires_on=expires)
    return str({"status": "reissued", "member_event_id": rid, "original_event_id": original_event_id,
                "certificate_value_usd": round(float(certificate_value_usd), 2),
                "certificate_expires_on": expires})


@tool(owner="agent", rw="write")
def reverse_refund_points_2db3868c(ctx: ToolContext, membership_id: str, source_category: str,
                                   source_event_id: str, refund_date: str, refunded_spend_usd: float,
                                   points: int) -> str:
    """Take back Pals Rewards points that a purchase earned after that purchase was refunded. One
    call books one points-reversal entry on the rewards ledger, dated on the refund date and tied
    to the original purchase record, carrying the refunded spend and the points taken back, and
    lowers the points balance by those points. Afterwards the customer sees
    the reversal in the points history and the lower balance; the receipt carries the reversal
    entry's reference number.

    Args:
        membership_id: Id class — the reference number of the customer's Pals Rewards membership,
            read from the membership lookup for this customer.
        source_category: Enum class — the program of the refunded purchase: autoship for a charged
            Autoship shipment; rx for a pharmacy fill; groom for a salon pass purchase, club fee or
            salon checkout; order for a retail order line; train for a training enrollment; vet for a
            wellness plan payment; livepet for a live animal purchase; none when the entry is not tied
            to a purchase in any program.
        source_event_id: Id class — the reference number of the original purchase record that earned
            the points (for example the order line charge), read from that program's history lookup.
        refund_date: Fixed-format class — the date the purchase was refunded, as YYYY-MM-DD, copied
            from the refund record; it becomes the date of the reversal entry.
        refunded_spend_usd: Fixed-format class — the refunded part of the purchase's qualifying spend,
            in USD with 2 decimal places, rounded half up to the cent.
        points: Fixed-format class — the points to take back, a whole non-negative number given as
            integer, points.

    Returns:
        A dict confirming the reversal: status ("reversed" when the entry was booked); member_event_id
        (string, the reference number of the reversal entry); points (integer, points taken back);
        refunded_spend_usd (number, USD with 2 decimals); points_balance (integer, the balance after
        the reversal).
    """
    mem = ctx.find("member_memberships", membership_id=membership_id)
    row = mem[0] if mem else {}
    balance = int(row.get("points_balance") or 0) - int(points)
    rid = ctx.make_id("mev_", membership_id, source_category, source_event_id, refund_date, refunded_spend_usd, points)
    ctx.create("member_events", rid, member_event_id=rid, membership_id=membership_id,
               customer_id=row.get("customer_id"), event_type="member_points_reverse", event_date=refund_date,
               source_category=source_category, source_event_id=source_event_id,
               qualifying_spend_usd=round(float(refunded_spend_usd), 2), points=int(points), bonus_kind="none")
    ctx.update("member_memberships", membership_id, points_balance=balance)
    return str({"status": "reversed", "member_event_id": rid, "points": int(points),
                "refunded_spend_usd": round(float(refunded_spend_usd), 2), "points_balance": balance})


@tool(owner="user", rw="write")
def upgrade_plus_tier_d51b9d82(ctx: ToolContext, membership_id: str, new_tier: str, upgrade_charge_usd: float,
                               perk_credit_usd: float, enrollment_bonus_points: int) -> str:
    """Move your own Tailwise Plus membership up to a higher paid tier today and pay the upgrade
    charge with the card on file. One call moves the membership to the paid tier you choose,
    starts a new paid term of one billing cycle today with automatic renewal on and the next fee
    due the day after the term ends, books one fee charge in the amount stated, and books the
    perk credit the new term comes with, setting the perk credit balance to it, and, when an
    enrollment bonus is stated, books one enrollment bonus entry dated today and adds it to the
    points balance. Afterwards you see
    the new tier, its term dates, the charge and the perk credit on your account; the receipt
    carries the fee charge's reference number.

    Args:
        membership_id: Id class — the reference number of your Pals Rewards membership, as given to
            you by the care agent from the membership record.
        new_tier: Enum class — the paid tier you move up to: Pals Rewards Member is a free tier, not
            something you can upgrade to here; Pals Rewards Insider is a free tier earned by spend,
            not something you can upgrade to here; Pals Rewards VIP is a free tier earned by spend,
            not something you can upgrade to here; Tailwise Plus Monthly is the entry paid tier,
            never the target of a move up; Tailwise Plus Annual when you move up from the monthly
            paid tier to the annual one; Tailwise Plus Premier Annual when you move up to the
            premier annual paid tier.
        upgrade_charge_usd: Fixed-format class — the amount charged today for the upgrade, in USD
            with 2 decimal places, rounded half up to the cent, exactly as the care agent quoted it.
        perk_credit_usd: Fixed-format class — the perk credit the new term comes with, in USD with 2
            decimal places, rounded half up to the cent, as the care agent stated it; 0.00 when the
            new tier carries none.
        enrollment_bonus_points: Fixed-format class — the enrollment bonus posted with this move, a
            whole non-negative number given as integer, points, as the care agent stated it; 0 when no
            enrollment bonus is due.

    Returns:
        A dict confirming the upgrade: status ("upgraded" when the tier, charge and perk credit were
        booked); membership_id (string); variant_name (string, the paid tier now held);
        plus_term_start (string, YYYY-MM-DD); plus_term_end (string, YYYY-MM-DD);
        next_billing_date (string, YYYY-MM-DD); member_event_id (string, the reference number of the
        fee charge); amount_usd (number, USD with 2 decimals); perk_credit_balance_usd (number, USD
        with 2 decimals); enrollment_bonus_points (integer, points posted as enrollment bonus);
        points_balance (integer, the balance afterwards).
    """
    today = ctx.now()[:10]
    y, m, d = _YMD(today)
    end = _PREV(*(_PLUS_MONTH(y, m, d) if new_tier == "Tailwise Plus Monthly" else _PLUS_YEAR(y, m, d)))
    term_end = _FMT(*end)
    next_bill = _FMT(*_NEXT(*end))
    mem = ctx.find("member_memberships", membership_id=membership_id)
    row = mem[0] if mem else {}
    rid = ctx.make_id("mev_", membership_id, new_tier, upgrade_charge_usd, perk_credit_usd, enrollment_bonus_points)
    pid = ctx.make_id("mev_", rid, "perk")
    balance = int(row.get("points_balance") or 0) + int(enrollment_bonus_points)
    ctx.update("member_memberships", membership_id, variant_name=new_tier, tier_effective_on=today,
               last_change_reason="plus_upgrade", plus_term_start=today, plus_term_end=term_end,
               next_billing_date=next_bill, auto_renew=True, downgrade_effective_on=None,
               perk_credit_balance_usd=round(float(perk_credit_usd), 2), points_balance=balance)
    ctx.create("member_events", rid, member_event_id=rid, membership_id=membership_id,
               customer_id=row.get("customer_id"), event_type="member_fee_charge", event_date=today,
               source_category="none", billing_period_start=today, amount_usd=round(float(upgrade_charge_usd), 2))
    ctx.create("member_events", pid, member_event_id=pid, membership_id=membership_id,
               customer_id=row.get("customer_id"), event_type="member_perk_credit_grant", event_date=today,
               source_category="none", original_event_id=rid, perk_credit_usd=round(float(perk_credit_usd), 2))
    if int(enrollment_bonus_points) > 0:
        bid = ctx.make_id("mev_", rid, "enrollment")
        ctx.create("member_events", bid, member_event_id=bid, membership_id=membership_id,
                   customer_id=row.get("customer_id"), event_type="member_bonus_points", event_date=today,
                   source_category="none", bonus_kind="enrollment", points=int(enrollment_bonus_points))
    return str({"status": "upgraded", "membership_id": membership_id, "variant_name": new_tier,
                "plus_term_start": today, "plus_term_end": term_end, "next_billing_date": next_bill,
                "member_event_id": rid, "amount_usd": round(float(upgrade_charge_usd), 2),
                "perk_credit_balance_usd": round(float(perk_credit_usd), 2),
                "enrollment_bonus_points": int(enrollment_bonus_points), "points_balance": balance})

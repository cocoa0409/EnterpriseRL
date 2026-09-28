"""Hidden task tools of the membership_charges_and_cancellations difficulty (Cartwise+ Membership).

Each tool performs exactly one atomic write on a Cartwise+ membership and computes nothing on the agent's
behalf: every amount or length it books is passed in already worked out. No tool checks status, timing,
ownership or any other business condition; those judgements belong to the published policy and the agent.
"""

from erlbench import ToolContext, tool


class _Util:
    """Plain helpers shared by the tools below (not tools themselves)."""

    @staticmethod
    def add_months(day: str, months: int) -> str:
        """Same day of the month `months` later, falling back to that month's last day."""
        y, m, d = (int(x) for x in day[:10].split("-"))
        m0 = m - 1 + months
        y2, m2 = y + m0 // 12, m0 % 12 + 1
        d2 = min(d, _Util.month_length(y2, m2))
        return f"{y2:04d}-{m2:02d}-{d2:02d}"

    @staticmethod
    def month_length(y: int, m: int) -> int:
        """Days in month m of year y (proleptic Gregorian)."""
        if m == 2:
            return 29 if (y % 4 == 0 and (y % 100 != 0 or y % 400 == 0)) else 28
        return 30 if m in (4, 6, 9, 11) else 31

    @staticmethod
    def add_days(day: str, n: int) -> str:
        """The 'YYYY-MM-DD' date n calendar days after `day` (n may be negative), by pure day counting."""
        y, m, d = (int(x) for x in day[:10].split("-"))
        # days since 0000-03-01 (civil-from-days / days-from-civil, proleptic Gregorian)
        yy = y - (1 if m <= 2 else 0)
        era = (yy if yy >= 0 else yy - 399) // 400
        yoe = yy - era * 400
        doy = (153 * (m + (-3 if m > 2 else 9)) + 2) // 5 + d - 1
        doe = yoe * 365 + yoe // 4 - yoe // 100 + doy
        z = era * 146097 + doe + n
        era = (z if z >= 0 else z - 146096) // 146097
        doe = z - era * 146097
        yoe = (doe - doe // 1460 + doe // 36524 - doe // 146096) // 365
        doy = doe - (365 * yoe + yoe // 4 - yoe // 100)
        mp = (5 * doy + 2) // 153
        d2 = doy - (153 * mp + 2) // 5 + 1
        m2 = mp + (3 if mp < 10 else -9)
        y2 = yoe + era * 400 + (1 if m2 <= 2 else 0)
        return f"{y2:04d}-{m2:02d}-{d2:02d}"

    @staticmethod
    def membership(ctx: ToolContext, membership_id: str) -> dict:
        rows = ctx.find("memberships", membership_id=membership_id)
        return rows[0] if rows else {}


@tool(owner="user", rw="write")
def confirm_annual_term_early_end_0b7355fe(ctx: ToolContext, membership_id: str, source_event_id: str,
                                           amount_usd: float) -> str:
    """The member confirms, in person, that the annual term of their Cartwise+ membership ends early, and the
    money owed back on the charge that opened that term is returned to them. One call books one refund entry of
    the prorated-annual kind on the membership, pointing at that opening charge, for the amount confirmed, dated
    today, and returned to the original payment method; the membership's net fees paid go down by that amount.
    The membership's plan, status and dates are not changed by this action. Success is the receipt below, which carries the
    refund reference the member can quote.

    Args:
        membership_id: Id class — the reference number of the member's own Cartwise+ membership, as the agent read
            it from the membership lookup and told the member.
        source_event_id: Id class — the reference number of the fee charge that opened the annual term being ended,
            as the agent read it from the membership's entries and told the member.
        amount_usd: Fixed-format class — the amount returned to the member on that charge, in USD, a positive
            number with 2 decimal places (rounded to the nearest cent if more digits are given).

    Returns:
        A dictionary rendered as text: refund_id (the new refund entry's reference number), membership_id,
        source_event_id (the charge refunded), refund_type (always "prorated_annual"), amount_usd (USD, 2 decimal
        places, as booked), event_date (YYYY-MM-DD, today) and status ("refund_booked", meaning the refund entry now
        stands on the membership).
    """
    mem = _Util.membership(ctx, membership_id)
    amount = round(float(amount_usd), 2)
    rid = ctx.make_id("mev_", membership_id, source_event_id, "prorated_annual", amount)
    today = ctx.now()[:10]
    ctx.create("membership_events", rid, membership_event_id=rid, membership_id=membership_id,
               customer_id=mem.get("customer_id", ""), event_type="membership_fee_refunded",
               refund_type="prorated_annual", source_event_id=source_event_id, amount_usd=amount,
               event_date=today)
    return str({"refund_id": rid, "membership_id": membership_id, "source_event_id": source_event_id,
                "refund_type": "prorated_annual", "amount_usd": amount, "event_date": today,
                "status": "refund_booked"})


@tool(owner="agent", rw="write")
def refund_carried_term_value_822a3886(ctx: ToolContext, membership_id: str, source_event_id: str,
                                       amount_usd: float) -> str:
    """Return to the member the unused part of the value that an earlier fee charge carried into the membership's
    current annual term. One call books one refund entry of the prorated-annual kind on the membership, pointing
    at that earlier charge, for the amount given, dated today and returned to the original payment method; the
    membership's net fees paid go down by that amount. The plan, status and dates of the membership are not
    changed. Success is the receipt below, and the refund shows among the membership's entries.

    Args:
        membership_id: Id class — the reference number of the Cartwise+ membership, read from the membership lookup.
        source_event_id: Id class — the reference number of the earlier fee charge whose carried value is being
            returned, read from the membership's entries.
        amount_usd: Fixed-format class — the amount returned against that charge, in USD, a positive number with
            2 decimal places (rounded to the nearest cent if more digits are given).

    Returns:
        A dictionary rendered as text: refund_id (the new refund entry's reference number), membership_id,
        source_event_id (the charge the refund is booked against), refund_type (always "prorated_annual"),
        amount_usd (USD, 2 decimal places, as booked), event_date (YYYY-MM-DD, today) and status
        ("refund_booked", meaning the refund entry now stands on the membership).
    """
    mem = _Util.membership(ctx, membership_id)
    amount = round(float(amount_usd), 2)
    rid = ctx.make_id("mev_", membership_id, source_event_id, "carried", amount)
    today = ctx.now()[:10]
    ctx.create("membership_events", rid, membership_event_id=rid, membership_id=membership_id,
               customer_id=mem.get("customer_id", ""), event_type="membership_fee_refunded",
               refund_type="prorated_annual", source_event_id=source_event_id, amount_usd=amount,
               event_date=today)
    return str({"refund_id": rid, "membership_id": membership_id, "source_event_id": source_event_id,
                "refund_type": "prorated_annual", "amount_usd": amount, "event_date": today,
                "status": "refund_booked"})


@tool(owner="agent", rw="write")
def move_annual_plan_to_monthly_dc3bc730(ctx: ToolContext, membership_id: str, amount_usd: float) -> str:
    """Move a Cartwise+ membership off its annual plan onto Cartwise+ Monthly today. One call changes the
    membership's plan to Cartwise+ Monthly, records today as the date the plan switch took effect, opens a new
    one-month paid period that starts today and renews on the same day next month (the last day of that month
    when the day does not exist), and captures the given amount from the member's card as the plan-switch fee
    for that new period. The member sees the Monthly plan, the new renewal date and the plan-switch charge on
    their membership. Success is the receipt below.

    Args:
        membership_id: Id class — the reference number of the Cartwise+ membership being moved, read from the
            membership lookup.
        amount_usd: Fixed-format class — the plan-switch fee captured for the new monthly period, in USD, a
            non-negative number with 2 decimal places (rounded to the nearest cent if more digits are given).

    Returns:
        A dictionary rendered as text: charge_id (the new fee charge entry's reference number), membership_id,
        variant_name (always "Cartwise+ Monthly"), plan_switched_date (YYYY-MM-DD, today),
        current_period_start (YYYY-MM-DD, today), current_period_end (YYYY-MM-DD, the new renewal date),
        amount_usd (USD, 2 decimal places, as captured) and status ("switched", meaning the membership now stands on
        Cartwise+ Monthly with the charge captured).
    """
    mem = _Util.membership(ctx, membership_id)
    amount = round(float(amount_usd), 2)
    today = ctx.now()[:10]
    end = _Util.add_months(today, 1)
    ctx.update("memberships", membership_id, variant_name="Cartwise+ Monthly", plan_switched_date=today,
               current_period_start=today, current_period_end=end)
    cid = ctx.make_id("mev_", membership_id, "plan_switch", today, amount)
    ctx.create("membership_events", cid, membership_event_id=cid, membership_id=membership_id,
               customer_id=mem.get("customer_id", ""), event_type="membership_fee_charged",
               fee_type="plan_switch", billing_period_start=today, amount_usd=amount, event_date=today)
    return str({"charge_id": cid, "membership_id": membership_id, "variant_name": "Cartwise+ Monthly",
                "plan_switched_date": today, "current_period_start": today, "current_period_end": end,
                "amount_usd": amount, "status": "switched"})


@tool(owner="agent", rw="write")
def book_membership_pause_b6aef13b(ctx: ToolContext, membership_id: str, pause_days: int) -> str:
    """Book a pause on a Cartwise+ membership. One call pauses the membership starting on its next renewal date
    (the date its current paid period ends), for the given number of calendar days counted with that renewal date
    as the first paused day, records the first and last paused days on the membership, sets it to paused, and
    adds one entry to its pause history with the booked length. While paused no fee is charged and no order
    benefit applies. Success is the receipt below.

    Args:
        membership_id: Id class — the reference number of the Cartwise+ membership being paused, read from the
            membership lookup.
        pause_days: Fixed-format class — the booked length of the pause in calendar days, an integer of at least 1.

    Returns:
        A dictionary rendered as text: pause_entry_id (the new pause-history entry's reference number),
        membership_id, pause_start_date (YYYY-MM-DD, the first paused day), pause_end_date (YYYY-MM-DD, the last
        paused day), pause_days (integer, as booked) and status ("paused", meaning the pause now stands on the
        membership).
    """
    mem = _Util.membership(ctx, membership_id)
    days = int(pause_days)
    start = str(mem.get("current_period_end") or ctx.now()[:10])[:10]
    end = _Util.add_days(start, days - 1)
    ctx.update("memberships", membership_id, status="paused", pause_start_date=start, pause_end_date=end)
    pid = ctx.make_id("mev_", membership_id, "pause", start, days)
    ctx.create("membership_events", pid, membership_event_id=pid, membership_id=membership_id,
               customer_id=mem.get("customer_id", ""), event_type="membership_pause_logged",
               billing_period_start=start, quantity=days, event_date=ctx.now()[:10])
    return str({"pause_entry_id": pid, "membership_id": membership_id, "pause_start_date": start,
                "pause_end_date": end, "pause_days": days, "status": "paused"})


@tool(owner="user", rw="write")
def settle_past_due_membership_fee_b438dc6f(ctx: ToolContext, membership_id: str, amount_usd: float) -> str:
    """The member pays, in person with their card, the outstanding fee of a Cartwise+ membership that is past due.
    One call captures the given amount as a retry of the period fee for the period that was being billed (the
    period that starts on the membership's current period start), clears the membership's past-due date and
    returns it to active; the period dates do not move. The member sees the captured charge and an active
    membership. Success is the receipt below.

    Args:
        membership_id: Id class — the reference number of the member's own Cartwise+ membership, as the agent read it
            from the membership lookup and told the member.
        amount_usd: Fixed-format class — the amount the member pays, in USD, a positive number with 2 decimal
            places (rounded to the nearest cent if more digits are given).

    Returns:
        A dictionary rendered as text: charge_id (the new fee charge entry's reference number), membership_id,
        billing_period_start (YYYY-MM-DD, the first day of the period paid for), amount_usd (USD, 2 decimal places,
        as captured) and status ("active", meaning the membership is reinstated).
    """
    mem = _Util.membership(ctx, membership_id)
    amount = round(float(amount_usd), 2)
    today = ctx.now()[:10]
    bps = str(mem.get("current_period_start") or today)[:10]
    ctx.update("memberships", membership_id, status="active", past_due_since="")
    cid = ctx.make_id("mev_", membership_id, "renewal_retry", bps, amount)
    ctx.create("membership_events", cid, membership_event_id=cid, membership_id=membership_id,
               customer_id=mem.get("customer_id", ""), event_type="membership_fee_charged",
               fee_type="renewal_retry", billing_period_start=bps, amount_usd=amount, event_date=today)
    return str({"charge_id": cid, "membership_id": membership_id, "billing_period_start": bps,
                "amount_usd": amount, "status": "active"})


@tool(owner="agent", rw="write")
def upgrade_membership_plan_10b03fa3(ctx: ToolContext, membership_id: str, variant_name: str,
                                     amount_usd: float) -> str:
    """Move a Cartwise+ membership up to an annual plan today. One call changes the membership's plan to the
    annual plan named, records today as the date the plan switch took effect, opens a new twelve-month paid
    period that starts today and renews on the same day a year later (the last day of that month when the day
    does not exist), and captures the given amount from the member's card as the plan-switch fee for that new
    period. The member sees the new plan, the new renewal date and the plan-switch charge on their membership.
    Success is the receipt below.

    Args:
        membership_id: Id class — the reference number of the Cartwise+ membership being moved, read from the
            membership lookup.
        variant_name: Enum class — the official name of the plan the membership moves to, exactly one of:
            Cartwise+ Assist Monthly — never used with this action, because it is a monthly plan;
            Cartwise+ Student Monthly — never used with this action, because it is a monthly plan;
            Cartwise+ Monthly — never used with this action, because it is a monthly plan;
            Cartwise+ Annual — the member moves to the standard annual plan;
            Cartwise+ Family Annual — the member moves to the household annual plan;
            Cartwise+ Premier Annual — the member moves to the top annual plan.
        amount_usd: Fixed-format class — the plan-switch fee captured for the new annual period, in USD, a
            non-negative number with 2 decimal places (rounded to the nearest cent if more digits are given).

    Returns:
        A dictionary rendered as text: charge_id (the new fee charge entry's reference number), membership_id,
        variant_name (the plan now held), plan_switched_date (YYYY-MM-DD, today), current_period_start
        (YYYY-MM-DD, today), current_period_end (YYYY-MM-DD, the new renewal date), amount_usd (USD, 2 decimal
        places, as captured) and status ("switched", meaning the membership now stands on the new plan with the
        charge captured).
    """
    mem = _Util.membership(ctx, membership_id)
    amount = round(float(amount_usd), 2)
    today = ctx.now()[:10]
    end = _Util.add_months(today, 12)
    ctx.update("memberships", membership_id, variant_name=variant_name, plan_switched_date=today,
               current_period_start=today, current_period_end=end)
    cid = ctx.make_id("mev_", membership_id, "plan_switch", variant_name, today, amount)
    ctx.create("membership_events", cid, membership_event_id=cid, membership_id=membership_id,
               customer_id=mem.get("customer_id", ""), event_type="membership_fee_charged",
               fee_type="plan_switch", billing_period_start=today, amount_usd=amount, event_date=today)
    return str({"charge_id": cid, "membership_id": membership_id, "variant_name": variant_name,
                "plan_switched_date": today, "current_period_start": today, "current_period_end": end,
                "amount_usd": amount, "status": "switched"})

"""Hidden task tools of the pass_membership_billing_and_benefits difficulty (Wayfare Pass).

Each tool lands exactly one atomic membership write with the values the agent has already worked
out from the published rules and the records; none of them judges eligibility, aggregates history
or refuses because some other matter is still open.
"""

from erlbench import ToolContext, tool


class _PeriodCalendar:
    """Calendar arithmetic for billing periods, kept as plain integer maths."""

    @staticmethod
    def days_in_month(year: int, month: int) -> int:
        if month == 2:
            leap = (year % 4 == 0 and year % 100 != 0) or year % 400 == 0
            return 29 if leap else 28
        return 30 if month in (4, 6, 9, 11) else 31

    @staticmethod
    def period_end(start: str, months: int) -> str:
        """Last day of a period that starts on `start` and runs `months` calendar months: the day
        before the same day-of-month that many months later, or the last day of the shorter month
        when that day does not exist."""
        year, month, day = (int(p) for p in str(start)[:10].split("-"))
        total = (month - 1) + months
        year2, month2 = year + total // 12, total % 12 + 1
        last = _PeriodCalendar.days_in_month(year2, month2)
        if day > last:
            return f"{year2:04d}-{month2:02d}-{last:02d}"
        if day > 1:
            return f"{year2:04d}-{month2:02d}-{day - 1:02d}"
        prev_month = month2 - 1 or 12
        prev_year = year2 if month2 > 1 else year2 - 1
        return f"{prev_year:04d}-{prev_month:02d}-{_PeriodCalendar.days_in_month(prev_year, prev_month):02d}"


@tool(owner="user", rw="write")
def restore_past_due_pass_5ad4a609(ctx: ToolContext, pass_membership_id: str, amount: float) -> str:
    """The member pays the past-due renewal of their own Wayfare Pass membership with the payment
    method they now want to use, bringing the membership back from past due. One call collects one
    renewal payment for the billing period in force: it books a membership fee charge with reason
    renewal for that period, adds the amount to the membership's net fees paid, and sets the
    membership status to active with its period dates unchanged. On success the member sees an
    active membership and the new fee charge on the membership ledger.

    Args:
        pass_membership_id: Id class — the Wayfare Pass membership reference number being restored, as returned by the membership lookup.
        amount: Fixed-format class — the renewal payment collected now, in USD, a positive amount with 2 decimal places rounded half up to the cent; never empty.

    Returns:
        A dictionary: pass_event_id (string, reference number of the new fee charge), pass_membership_id
        (string, the membership restored), amount (number, USD with 2 decimal places, the payment
        collected), billing_period_start (string, YYYY-MM-DD, first day of the period paid for),
        status (string, the membership status once paid, active on success).
    """
    rows = ctx.find("pass_memberships", pass_membership_id=pass_membership_id)
    member = rows[0] if rows else {}
    period_start = member.get("current_period_start") or ""
    paid = round(float(amount), 2)
    rid = ctx.make_id("pev_", pass_membership_id, paid, "restore")
    ctx.create("pass_events", rid, pass_event_id=rid, pass_membership_id=pass_membership_id,
               customer_id=member.get("customer_id"), event_type="pass_fee_charge", event_date=ctx.now()[:10],
               amount=paid, billing_period_start=period_start, charge_reason="renewal", retry_number=0,
               original_event_id=None, trip_id=None, credit_month="", refund_basis="none", forfeit_reason="none")
    net = round(float(member.get("net_fees_paid") or 0) + paid, 2)
    ctx.update("pass_memberships", pass_membership_id, status="active", net_fees_paid=net)
    return str({"pass_event_id": rid, "pass_membership_id": pass_membership_id, "amount": paid,
                "billing_period_start": period_start, "status": "active"})


@tool(owner="user", rw="write")
def upgrade_pass_to_plus_monthly_9f7c0895(ctx: ToolContext, pass_membership_id: str, proration_charge: float) -> str:
    """The member moves their own Wayfare Pass membership up to the Wayfare Pass Plus Monthly plan
    today and pays the plan change charge. One call changes the plan to Wayfare Pass Plus Monthly,
    starts a new one-month billing period on today's date (its last day follows the plan's period end
    rule), clears any student verification date, books a membership fee charge with reason
    plan_change_proration for the new period, and adds the charge to the membership's net fees paid.
    On success the member sees the Plus Monthly plan, the new period dates and the charge on the
    membership ledger.

    Args:
        pass_membership_id: Id class — the Wayfare Pass membership reference number being moved up, as returned by the membership lookup.
        proration_charge: Fixed-format class — the plan change charge collected now, in USD, a non-negative amount with 2 decimal places, rounded half up to the cent; never empty.

    Returns:
        A dictionary: pass_event_id (string, reference number of the plan change fee charge),
        pass_membership_id (string, the membership changed), variant_name (string, the plan now held,
        Wayfare Pass Plus Monthly), current_period_start (string, YYYY-MM-DD, first day of the new
        period), current_period_end (string, YYYY-MM-DD, last day of the new period), proration_charge
        (number, USD with 2 decimal places, the amount collected).
    """
    rows = ctx.find("pass_memberships", pass_membership_id=pass_membership_id)
    member = rows[0] if rows else {}
    today = ctx.now()[:10]
    end = _PeriodCalendar.period_end(today, 1)
    charge = round(float(proration_charge), 2)
    rid = ctx.make_id("pev_", pass_membership_id, charge, "plus_monthly")
    ctx.create("pass_events", rid, pass_event_id=rid, pass_membership_id=pass_membership_id,
               customer_id=member.get("customer_id"), event_type="pass_fee_charge", event_date=today,
               amount=charge, billing_period_start=today, charge_reason="plan_change_proration", retry_number=0,
               original_event_id=None, trip_id=None, credit_month="", refund_basis="none", forfeit_reason="none")
    net = round(float(member.get("net_fees_paid") or 0) + charge, 2)
    ctx.update("pass_memberships", pass_membership_id, variant_name="Wayfare Pass Plus Monthly",
               current_period_start=today, current_period_end=end, student_verified_until="", net_fees_paid=net)
    return str({"pass_event_id": rid, "pass_membership_id": pass_membership_id,
                "variant_name": "Wayfare Pass Plus Monthly", "current_period_start": today,
                "current_period_end": end, "proration_charge": charge})


@tool(owner="user", rw="write")
def upgrade_pass_to_all_access_2d51c03c(ctx: ToolContext, pass_membership_id: str, proration_charge: float) -> str:
    """The member moves their own Wayfare Pass membership up to the Wayfare Pass All Access Annual
    plan today and pays the plan change charge. One call changes the plan to Wayfare Pass All Access
    Annual, starts a new twelve-month billing period on today's date (its last day follows the plan's
    period end rule), clears any student verification date, books a membership fee charge with reason
    plan_change_proration for the new period, and adds the charge to the membership's net fees paid.
    On success the member sees the All Access Annual plan, the new period dates and the charge on the
    membership ledger.

    Args:
        pass_membership_id: Id class — the Wayfare Pass membership reference number being moved up, as returned by the membership lookup.
        proration_charge: Fixed-format class — the plan change charge collected now, in USD, a non-negative amount with 2 decimal places, rounded half up to the cent; never empty.

    Returns:
        A dictionary: pass_event_id (string, reference number of the plan change fee charge),
        pass_membership_id (string, the membership changed), variant_name (string, the plan now held,
        Wayfare Pass All Access Annual), current_period_start (string, YYYY-MM-DD, first day of the new
        period), current_period_end (string, YYYY-MM-DD, last day of the new period), proration_charge
        (number, USD with 2 decimal places, the amount collected).
    """
    rows = ctx.find("pass_memberships", pass_membership_id=pass_membership_id)
    member = rows[0] if rows else {}
    today = ctx.now()[:10]
    end = _PeriodCalendar.period_end(today, 12)
    charge = round(float(proration_charge), 2)
    rid = ctx.make_id("pev_", pass_membership_id, charge, "all_access")
    ctx.create("pass_events", rid, pass_event_id=rid, pass_membership_id=pass_membership_id,
               customer_id=member.get("customer_id"), event_type="pass_fee_charge", event_date=today,
               amount=charge, billing_period_start=today, charge_reason="plan_change_proration", retry_number=0,
               original_event_id=None, trip_id=None, credit_month="", refund_basis="none", forfeit_reason="none")
    net = round(float(member.get("net_fees_paid") or 0) + charge, 2)
    ctx.update("pass_memberships", pass_membership_id, variant_name="Wayfare Pass All Access Annual",
               current_period_start=today, current_period_end=end, student_verified_until="", net_fees_paid=net)
    return str({"pass_event_id": rid, "pass_membership_id": pass_membership_id,
                "variant_name": "Wayfare Pass All Access Annual", "current_period_start": today,
                "current_period_end": end, "proration_charge": charge})


@tool(owner="agent", rw="write")
def post_pass_ride_credit_f79e4c68(ctx: ToolContext, pass_membership_id: str, trip_id: str, credit_month: str,
                                   billing_period_start: str, amount: float) -> str:
    """Post Pass ride credit that one completed trip of the member earned but that never reached the
    membership. One call books one credit earn entry for that trip on the membership ledger, dated
    today, counted toward the given calendar month and billing period, and adds the amount to the
    member's Pass ride credit balance. On success the member sees the credit on the ledger and in the
    spendable balance.

    Args:
        pass_membership_id: Id class — the Wayfare Pass membership reference number that earns the credit, as returned by the membership lookup.
        trip_id: Id class — the trip reference number of the completed trip the credit is for, as returned by the trip lookup.
        credit_month: Fixed-format class — the calendar month of the trip's drop-off in the member's home market time, recorded on the entry as its credit month, written YYYY-MM; never empty.
        billing_period_start: Fixed-format class — first day of the billing period that was in force at the trip's drop-off, written YYYY-MM-DD; never empty.
        amount: Fixed-format class — the credit posted, in USD, a positive amount with 2 decimal places, rounded half up to the cent; never empty.

    Returns:
        A dictionary: pass_event_id (string, reference number of the credit entry), pass_membership_id
        (string, the membership credited), trip_id (string, the trip the credit is for), amount (number,
        USD with 2 decimal places, the credit posted), member_credit_balance (number, USD with 2 decimal
        places, the spendable balance including this credit).
    """
    rows = ctx.find("pass_memberships", pass_membership_id=pass_membership_id)
    member = rows[0] if rows else {}
    credit = round(float(amount), 2)
    rid = ctx.make_id("pev_", pass_membership_id, trip_id, credit_month, billing_period_start, credit)
    ctx.create("pass_events", rid, pass_event_id=rid, pass_membership_id=pass_membership_id,
               customer_id=member.get("customer_id"), event_type="pass_credit_earn", event_date=ctx.now()[:10],
               amount=credit, billing_period_start=billing_period_start, charge_reason="none", retry_number=0,
               original_event_id=None, trip_id=trip_id, credit_month=credit_month, refund_basis="none",
               forfeit_reason="none")
    balance = round(float(member.get("member_credit_balance") or 0) + credit, 2)
    ctx.update("pass_memberships", pass_membership_id, member_credit_balance=balance)
    return str({"pass_event_id": rid, "pass_membership_id": pass_membership_id, "trip_id": trip_id,
                "amount": credit, "member_credit_balance": balance})


@tool(owner="agent", rw="write")
def forfeit_pass_ride_credit_4b5902d4(ctx: ToolContext, pass_membership_id: str, original_event_id: str,
                                      amount: float) -> str:
    """Take back Pass ride credit that a trip earned when the fare of that trip has since been reduced or
    refunded. One call books one credit forfeiture entry with reason trip_refunded on the membership ledger,
    dated today, pointing at the credit earn entry it reverses and carrying that entry's trip, calendar
    month and billing period, and lowers the member's Pass ride credit balance by the amount. On success
    the forfeiture shows on the ledger and the balance is lower by that amount.

    Args:
        pass_membership_id: Id class — the Wayfare Pass membership reference number whose credit is taken back, as returned by the membership lookup.
        original_event_id: Id class — the reference number of the credit earn entry being reversed, as returned by the membership ledger lookup.
        amount: Fixed-format class — the credit taken back, in USD, a positive amount with 2 decimal places, rounded half up to the cent; never empty.

    Returns:
        A dictionary: pass_event_id (string, reference number of the forfeiture entry),
        pass_membership_id (string, the membership concerned), original_event_id (string, the credit earn
        entry reversed), amount (number, USD with 2 decimal places, the credit taken back),
        member_credit_balance (number, USD with 2 decimal places, the spendable balance once it is taken back).
    """
    rows = ctx.find("pass_memberships", pass_membership_id=pass_membership_id)
    member = rows[0] if rows else {}
    earned = ctx.find("pass_events", pass_event_id=original_event_id)
    source = earned[0] if earned else {}
    taken = round(float(amount), 2)
    rid = ctx.make_id("pev_", pass_membership_id, original_event_id, taken)
    ctx.create("pass_events", rid, pass_event_id=rid, pass_membership_id=pass_membership_id,
               customer_id=member.get("customer_id"), event_type="pass_credit_forfeit", event_date=ctx.now()[:10],
               amount=-taken, billing_period_start=source.get("billing_period_start") or "", charge_reason="none",
               retry_number=0, original_event_id=original_event_id, trip_id=source.get("trip_id"),
               credit_month=source.get("credit_month") or "", refund_basis="none", forfeit_reason="trip_refunded")
    balance = round(float(member.get("member_credit_balance") or 0) - taken, 2)
    ctx.update("pass_memberships", pass_membership_id, member_credit_balance=balance)
    return str({"pass_event_id": rid, "pass_membership_id": pass_membership_id,
                "original_event_id": original_event_id, "amount": taken, "member_credit_balance": balance})


@tool(owner="agent", rw="write")
def refund_pass_period_fee_d96d0945(ctx: ToolContext, pass_membership_id: str, original_event_id: str,
                                    amount: float) -> str:
    """Return money on a membership fee charge under the full refund window. One call books one fee
    refund entry with refund basis full_refund_window on the membership ledger, dated today, naming the
    fee charge it returns and carrying that charge's billing period, and lowers the membership's net
    fees paid by the amount; the money goes back to the member's card. On success the refund shows on
    the ledger against that charge.

    Args:
        pass_membership_id: Id class — the Wayfare Pass membership reference number the fee belongs to, as returned by the membership lookup.
        original_event_id: Id class — the reference number of the membership fee charge being returned, as returned by the membership ledger lookup.
        amount: Fixed-format class — the amount returned to the card, in USD, a positive amount with 2 decimal places, rounded half up to the cent; never empty.

    Returns:
        A dictionary: pass_event_id (string, reference number of the refund entry), pass_membership_id
        (string, the membership concerned), original_event_id (string, the fee charge returned), amount
        (number, USD with 2 decimal places, the amount returned), net_fees_paid (number, USD with 2
        decimal places, the membership's net fees paid including this refund).
    """
    rows = ctx.find("pass_memberships", pass_membership_id=pass_membership_id)
    member = rows[0] if rows else {}
    charged = ctx.find("pass_events", pass_event_id=original_event_id)
    source = charged[0] if charged else {}
    returned = round(float(amount), 2)
    rid = ctx.make_id("pev_", pass_membership_id, original_event_id, returned)
    ctx.create("pass_events", rid, pass_event_id=rid, pass_membership_id=pass_membership_id,
               customer_id=member.get("customer_id"), event_type="pass_fee_refund", event_date=ctx.now()[:10],
               amount=-returned, billing_period_start=source.get("billing_period_start") or "", charge_reason="none",
               retry_number=0, original_event_id=original_event_id, trip_id=None, credit_month="",
               refund_basis="full_refund_window", forfeit_reason="none")
    net = round(float(member.get("net_fees_paid") or 0) - returned, 2)
    ctx.update("pass_memberships", pass_membership_id, net_fees_paid=net)
    return str({"pass_event_id": rid, "pass_membership_id": pass_membership_id,
                "original_event_id": original_event_id, "amount": returned, "net_fees_paid": net})

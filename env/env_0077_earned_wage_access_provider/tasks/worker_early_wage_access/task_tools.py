"""Hidden task tools for worker_early_wage_access (category access) of env_0077_earned_wage_access_provider.

Each tool performs one atomic write on a worker's Paystride Earned Wage Access Plan and is reached only
through the unlock/call meta-tools. No tool judges a policy condition or computes a policy figure.
"""

from decimal import Decimal, ROUND_HALF_UP

from erlbench import ToolContext, tool


class _Fmt:
    """Exact formatting helpers shared by the tool bodies."""

    @staticmethod
    def money(value) -> float:
        """Round a dollar figure half up to the cent, exactly."""
        return float(Decimal(str(value)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP))

    @staticmethod
    def is_date(text) -> bool:
        """True for a YYYY-MM-DD calendar date string."""
        s = str(text)
        if len(s) != 10 or s[4] != "-" or s[7] != "-":
            return False
        y, m, d = s[:4], s[5:7], s[8:]
        if not (y.isdigit() and m.isdigit() and d.isdigit()):
            return False
        yi, mi, di = int(y), int(m), int(d)
        if not 1 <= mi <= 12:
            return False
        leap = (yi % 4 == 0 and yi % 100 != 0) or yi % 400 == 0
        days = (31, 29 if leap else 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31)[mi - 1]
        return 1 <= di <= days

    @staticmethod
    def whole(value):
        """The value as an int when it is a whole number (not a bool), else None."""
        if isinstance(value, bool):
            return None
        try:
            f = float(value)
        except (TypeError, ValueError):
            return None
        return int(f) if f == int(f) else None


_TIERS = ("Paystride Access Starter", "Paystride Access Standard", "Paystride Access Plus",
          "Paystride Access Preferred", "Paystride Access Premier", "Paystride Access Premier Plus")


@tool(owner="user", rw="write")
def request_bank_transfer_bc93e4f0(ctx: ToolContext, access_plan_id: str, amount: float, daily_sequence: int) -> str:
    """The worker confirms, in person, a next-business-day early wage transfer from their Earned Wage
    Access Plan to their own bank account. One call books one transfer entry on the plan for the stated
    amount, for delivery by ACH on the business day following the request date, a request made past the day's
    submission cutoff or on a non-business day counting as made on the following business day, carrying the plan's current payday as the payday
    on which it is recovered, and adds the amount to the plan's outstanding balance. The worker sees the
    transfer on the plan's history at once; it shows as not yet delivered while the bank credit is
    unconfirmed. No fee is booked by this action.

    Args:
        access_plan_id: Id class — the reference number of the worker's Earned Wage Access Plan, read from the plan record the agent looked up for this worker.
        amount: Fixed-format class — the transfer amount the worker confirms, in US dollars, a positive figure with 2 decimal places, rounded half up to the cent if more places are given.
        daily_sequence: Fixed-format class — the ordinal of this transfer among the plan's transfers booked on today's Eastern Time calendar day, an integer of 1 or more.

    Returns:
        A confirmation sentence carrying the new transfer entry's reference number (text), the amount booked
        in US dollars with two decimals, the payday it is recovered on (YYYY-MM-DD), the delivery speed
        (next business day) and destination (bank account), and the plan's outstanding balance including the
        transfer in US dollars with two decimals; the reference number's presence means the transfer is booked.
    """
    amt = _Fmt.money(amount)
    if amt <= 0:
        return "Error: amount must be a positive dollar figure."
    seq = _Fmt.whole(daily_sequence)
    if seq is None or seq < 1:
        return "Error: daily_sequence must be an integer of 1 or more."
    plans = ctx.find("access_plans", access_plan_id=access_plan_id)
    if not plans:
        return f"Error: no Earned Wage Access Plan {access_plan_id}."
    plan = plans[0]
    now = ctx.now()
    rid = ctx.make_id("atr_", access_plan_id, amt, seq, "next_business_day", "bank_account", now)
    ctx.create("access_ledger", rid, access_entry_id=rid, access_plan_id=access_plan_id,
               customer_id=plan.get("customer_id"), event_type="access_transfer", entry_date=now[:10],
               pay_date=plan.get("next_pay_date"), amount=amt, daily_sequence=seq, requested_time=now[11:16],
               delivered_date="", delivery_minutes=None, related_entry_id="", delivery_speed="next_business_day",
               destination_type="bank_account", fee_type="none", recovery_method="none", reason_code="none",
               carryforward_pay_date="")
    balance = _Fmt.money(float(plan.get("outstanding_balance") or 0) + amt)
    ctx.update("access_plans", access_plan_id, outstanding_balance=balance)
    return (f"Transfer {rid} booked: {amt:.2f} USD next business day to bank account, recovered on "
            f"{plan.get('next_pay_date')}; outstanding balance now {balance:.2f} USD.")


@tool(owner="agent", rw="write")
def book_bank_transfer_fee_9f154276(ctx: ToolContext, access_plan_id: str, related_entry_id: str, amount: float) -> str:
    """Book the fee owed on one next-business-day transfer to a bank account on a worker's Earned Wage
    Access Plan; a transfer of any other speed or destination is refused with an error and nothing is
    booked. One call books one fee entry that points to that transfer, carries the transfer's payday,
    delivery speed and destination, is typed as a next-business-day fee, and adds the fee to the plan's
    outstanding balance to be recovered on that payday; the delivered transfer amount is untouched. The
    worker sees the fee on the plan's history at once.

    Args:
        access_plan_id: Id class — the reference number of the worker's Earned Wage Access Plan, read from the plan record the agent looked up for this worker.
        related_entry_id: Id class — the reference number of the plan's next-business-day transfer to a bank account the fee is owed on, read from the plan's ledger or from the confirmation the worker's transfer returned.
        amount: Fixed-format class — the fee in US dollars, a positive figure with 2 decimal places, rounded half up to the cent if more places are given.

    Returns:
        A confirmation sentence carrying the new fee entry's reference number (text), the fee booked in US
        dollars with two decimals, the transfer reference it points to, the payday it is recovered on
        (YYYY-MM-DD) and the plan's outstanding balance including the fee in US dollars with two decimals; the
        reference number's presence means the fee is booked.
    """
    amt = _Fmt.money(amount)
    if amt <= 0:
        return "Error: amount must be a positive dollar figure."
    plans = ctx.find("access_plans", access_plan_id=access_plan_id)
    if not plans:
        return f"Error: no Earned Wage Access Plan {access_plan_id}."
    plan = plans[0]
    src = ctx.find("access_ledger", access_entry_id=related_entry_id, access_plan_id=access_plan_id, event_type="access_transfer")
    if not src:
        return f"Error: {related_entry_id} is not a transfer entry on plan {access_plan_id}."
    t = src[0]
    if t.get("delivery_speed") != "next_business_day" or t.get("destination_type") != "bank_account":
        return (f"Error: {related_entry_id} is not a next-business-day transfer to a bank account "
                f"(it is {t.get('delivery_speed')} to {t.get('destination_type')}); no fee booked.")
    now = ctx.now()
    rid = ctx.make_id("afe_", access_plan_id, related_entry_id, amt, "next_business_day_fee")
    ctx.create("access_ledger", rid, access_entry_id=rid, access_plan_id=access_plan_id,
               customer_id=plan.get("customer_id"), event_type="access_fee", entry_date=now[:10],
               pay_date=t.get("pay_date"), amount=amt, daily_sequence=1, requested_time="00:00",
               delivered_date="", delivery_minutes=None, related_entry_id=related_entry_id,
               delivery_speed=t.get("delivery_speed"), destination_type=t.get("destination_type"),
               fee_type="next_business_day_fee", recovery_method="none", reason_code="none",
               carryforward_pay_date="")
    balance = _Fmt.money(float(plan.get("outstanding_balance") or 0) + amt)
    ctx.update("access_plans", access_plan_id, outstanding_balance=balance)
    return (f"Fee {rid} booked: {amt:.2f} USD on transfer {related_entry_id}, recovered on {t.get('pay_date')}; "
            f"outstanding balance now {balance:.2f} USD.")


@tool(owner="agent", rw="write")
def record_tier_review_be8f1edd(ctx: ToolContext, access_plan_id: str, new_variant_name: str, level_effective_date: str) -> str:
    """Record the tier review of a worker's Earned Wage Access Plan for a payday. One call sets the plan's
    tier to the tier the review arrives at, whether it changes or stays the same, and records the date
    from which that tier applies to new transfers. The worker sees the tier and its effective date on the
    plan at once; transfers already booked are not changed.

    Args:
        access_plan_id: Id class — the reference number of the worker's Earned Wage Access Plan, read from the plan record the agent looked up for this worker.
        new_variant_name: Enum class — the tier the review sets, exactly one of: "Paystride Access Starter" when the review places the plan on the entry tier; "Paystride Access Standard" when it places the plan on the second tier; "Paystride Access Plus" when it places the plan on the third tier; "Paystride Access Preferred" when it places the plan on the fourth tier; "Paystride Access Premier" when it places the plan on the fifth tier; "Paystride Access Premier Plus" when it places the plan on the top tier.
        level_effective_date: Fixed-format class — the calendar date from which the tier applies to transfers booked on or after it (transfers already booked keep their terms), written YYYY-MM-DD, Eastern Time.

    Returns:
        A confirmation sentence carrying the plan reference (text), the tier now held (its full tier name),
        the previously held tier (its full tier name) and the date it applies from (YYYY-MM-DD); the
        sentence's presence means the review is recorded.
    """
    if new_variant_name not in _TIERS:
        return f"Error: unknown tier '{new_variant_name}'."
    if not _Fmt.is_date(level_effective_date):
        return "Error: level_effective_date must be a real calendar date written YYYY-MM-DD."
    plans = ctx.find("access_plans", access_plan_id=access_plan_id)
    if not plans:
        return f"Error: no Earned Wage Access Plan {access_plan_id}."
    before = plans[0].get("variant_name")
    ctx.update("access_plans", access_plan_id, variant_name=new_variant_name, level_effective_date=level_effective_date)
    return (f"Tier review recorded on plan {access_plan_id}: now {new_variant_name} (was {before}), "
            f"applying from {level_effective_date}.")


@tool(owner="user", rw="write")
def request_instant_transfer_84ad3b61(ctx: ToolContext, access_plan_id: str, amount: float, daily_sequence: int) -> str:
    """The worker confirms, in person, an instant early wage transfer from their Earned Wage Access Plan
    pushed to their own external debit card. One call books one transfer entry on the plan for the stated
    amount, pushed instantly to the worker's external debit card, carrying the plan's current payday as the payday on
    which it is recovered, and adds the amount to the plan's outstanding balance. The worker sees the
    transfer on the plan's history at once; it shows as not yet delivered while the card network has not confirmed
    the push. No fee is booked by this action.

    Args:
        access_plan_id: Id class — the reference number of the worker's Earned Wage Access Plan, read from the plan record the agent looked up for this worker.
        amount: Fixed-format class — the transfer amount the worker confirms, in US dollars, a positive figure with 2 decimal places, rounded half up to the cent if more places are given.
        daily_sequence: Fixed-format class — the ordinal of this transfer among the plan's transfers booked on today's Eastern Time calendar day, an integer of 1 or more.

    Returns:
        A confirmation sentence carrying the new transfer entry's reference number (text), the amount booked
        in US dollars with two decimals, the payday it is recovered on (YYYY-MM-DD), the delivery speed
        (instant) and destination (external debit card), and the plan's outstanding balance including the
        transfer in US dollars with two decimals; the reference number's presence means the transfer is booked.
    """
    amt = _Fmt.money(amount)
    if amt <= 0:
        return "Error: amount must be a positive dollar figure."
    seq = _Fmt.whole(daily_sequence)
    if seq is None or seq < 1:
        return "Error: daily_sequence must be an integer of 1 or more."
    plans = ctx.find("access_plans", access_plan_id=access_plan_id)
    if not plans:
        return f"Error: no Earned Wage Access Plan {access_plan_id}."
    plan = plans[0]
    now = ctx.now()
    rid = ctx.make_id("atr_", access_plan_id, amt, seq, "instant", "external_debit_card", now)
    ctx.create("access_ledger", rid, access_entry_id=rid, access_plan_id=access_plan_id,
               customer_id=plan.get("customer_id"), event_type="access_transfer", entry_date=now[:10],
               pay_date=plan.get("next_pay_date"), amount=amt, daily_sequence=seq, requested_time=now[11:16],
               delivered_date="", delivery_minutes=None, related_entry_id="", delivery_speed="instant",
               destination_type="external_debit_card", fee_type="none", recovery_method="none", reason_code="none",
               carryforward_pay_date="")
    balance = _Fmt.money(float(plan.get("outstanding_balance") or 0) + amt)
    ctx.update("access_plans", access_plan_id, outstanding_balance=balance)
    return (f"Transfer {rid} booked: {amt:.2f} USD instant to external debit card, recovered on "
            f"{plan.get('next_pay_date')}; outstanding balance now {balance:.2f} USD.")


@tool(owner="agent", rw="write")
def record_missed_recovery_review_3a64d9dd(ctx: ToolContext, access_plan_id: str, new_variant_name: str, level_effective_date: str) -> str:
    """Record the review of a worker's Earned Wage Access Plan for a payday whose recovery fell short. One
    call sets the plan's tier to the tier that review lands on and records the date from which that tier
    applies to new transfers. The worker sees the tier and its effective date on the plan at once;
    transfers already booked are not changed.

    Args:
        access_plan_id: Id class — the reference number of the worker's Earned Wage Access Plan, read from the plan record the agent looked up for this worker.
        new_variant_name: Enum class — the tier the review lands on, exactly one of: "Paystride Access Starter" when the plan lands on the entry tier; "Paystride Access Standard" when it lands on the second tier; "Paystride Access Plus" when it lands on the third tier; "Paystride Access Preferred" when it lands on the fourth tier; "Paystride Access Premier" when it lands on the fifth tier; "Paystride Access Premier Plus" in no situation, since this review never lands above the tier one below the tier held (a plan already on Paystride Access Starter stays on it), and the value is refused with an error.
        level_effective_date: Fixed-format class — the calendar date from which the tier applies to transfers booked on or after it (transfers already booked keep their terms), written YYYY-MM-DD, Eastern Time.

    Returns:
        A confirmation sentence carrying the plan reference (text), the tier now held (its full tier name),
        the previously held tier (its full tier name) and the date it applies from (YYYY-MM-DD); the
        sentence's presence means the review is recorded.
    """
    if new_variant_name not in _TIERS:
        return f"Error: unknown tier '{new_variant_name}'."
    if new_variant_name == "Paystride Access Premier Plus":
        return "Error: a missed-recovery review never lands on Paystride Access Premier Plus."
    if not _Fmt.is_date(level_effective_date):
        return "Error: level_effective_date must be a real calendar date written YYYY-MM-DD."
    plans = ctx.find("access_plans", access_plan_id=access_plan_id)
    if not plans:
        return f"Error: no Earned Wage Access Plan {access_plan_id}."
    before = plans[0].get("variant_name")
    ctx.update("access_plans", access_plan_id, variant_name=new_variant_name, level_effective_date=level_effective_date)
    return (f"Missed-recovery review recorded on plan {access_plan_id}: now {new_variant_name} (was {before}), "
            f"applying from {level_effective_date}.")

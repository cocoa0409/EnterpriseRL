"""Hidden task tools for payment_arrangement_servicing (Ridgeline Recovery Associates).

Each tool performs one atomic write on a payment arrangement; every value it books is passed in
by the caller. Schedule dates are read off the plan's own schedule anchor with the calendar helper
below (pure ordinal-day arithmetic on YYYY-MM-DD strings).
"""

from erlbench import ToolContext, tool


class _Calendar:
    """Ordinal-day arithmetic on 'YYYY-MM-DD' strings (proleptic Gregorian calendar)."""

    @staticmethod
    def to_ordinal(text: str) -> int:
        y, m, d = (int(p) for p in str(text)[:10].split("-"))
        y -= 1 if m <= 2 else 0
        era = (y if y >= 0 else y - 399) // 400
        yoe = y - era * 400
        doy = (153 * (m + (-3 if m > 2 else 9)) + 2) // 5 + d - 1
        doe = yoe * 365 + yoe // 4 - yoe // 100 + doy
        return era * 146097 + doe - 719468

    @staticmethod
    def from_ordinal(z: int) -> str:
        z += 719468
        era = (z if z >= 0 else z - 146096) // 146097
        doe = z - era * 146097
        yoe = (doe - doe // 1460 + doe // 36524 - doe // 146096) // 365
        y = yoe + era * 400
        doy = doe - (365 * yoe + yoe // 4 - yoe // 100)
        mp = (5 * doy + 2) // 153
        d = doy - (153 * mp + 2) // 5 + 1
        m = mp + (3 if mp < 10 else -9)
        return f"{y + (1 if m <= 2 else 0):04d}-{m:02d}-{d:02d}"

    @staticmethod
    def add_days(text: str, days: int) -> str:
        return _Calendar.from_ordinal(_Calendar.to_ordinal(text) + int(days))

    @staticmethod
    def add_months(text: str, months: int) -> str:
        y, m, d = (int(p) for p in str(text)[:10].split("-"))
        total = y * 12 + (m - 1) + int(months)
        y2, m2 = divmod(total, 12)
        m2 += 1
        nxt_y, nxt_m = (y2 + 1, 1) if m2 == 12 else (y2, m2 + 1)
        last = _Calendar.to_ordinal(f"{nxt_y:04d}-{nxt_m:02d}-01") - _Calendar.to_ordinal(f"{y2:04d}-{m2:02d}-01")
        return f"{y2:04d}-{m2:02d}-{min(d, last):02d}"

    @staticmethod
    def due_date(plan: dict, installment_number: int) -> str:
        """Scheduled due date of an installment, read off the plan's schedule anchor."""
        steps = int(installment_number) - int(plan.get("schedule_anchor_installment") or 0)
        anchor = str(plan.get("schedule_anchor_date"))
        freq = plan.get("payment_frequency")
        if freq == "weekly":
            return _Calendar.add_days(anchor, 7 * steps)
        if freq == "biweekly":
            return _Calendar.add_days(anchor, 14 * steps)
        return _Calendar.add_months(anchor, steps)


@tool(owner="agent", rw="write")
def redate_returned_installment_ce690b15(ctx: ToolContext, plan_id: str, installment_number: int,
                                         shift_days: int) -> str:
    """Re-date one installment of a payment arrangement by a due-date change. Ridgeline records one
    granted due-date change on the arrangement's installment history and rewrites the arrangement's
    schedule: the named installment moves from its scheduled due date by the given number of
    calendar days, it becomes the schedule anchor installment with that new due date, and every
    later installment, the final one included, moves by the same number of days. The arrangement's
    amounts, installment count and payment method are not changed. The consumer can afterwards see
    the new due date of that installment and the new final due date on the arrangement.

    Args:
        plan_id: Id class — the payment plan reference number (the identifier) of the arrangement whose installment is
            re-dated, as returned by the payment arrangement lookup for the consumer.
        installment_number: Fixed-format class — the number of the installment to re-date, a
            non-negative integer (0 is the down payment, 1 the first regular installment).
        shift_days: Fixed-format class — the number of calendar days the installment's due date
            moves later, a non-negative integer of whole calendar days; 0 leaves the date unchanged.

    Returns:
        A dictionary rendered as text with: change_reference (string, the reference of the
        due-date change entry recorded), plan_id (string), installment_number (integer),
        previous_due_date (YYYY-MM-DD, the installment's scheduled due date before the change),
        new_due_date (YYYY-MM-DD), new_final_due_date (YYYY-MM-DD) and status (always
        "due_date_change_recorded"); that status confirms the change is recorded and the schedule
        rewritten.
    """
    rows = ctx.find("payment_plans", plan_id=plan_id)
    if not rows:
        return f"No payment plan found for {plan_id}."
    plan = rows[0]
    today = ctx.now()[:10]
    number = int(installment_number)
    shift = int(shift_days)
    previous_due = _Calendar.due_date(plan, number)
    new_due = _Calendar.add_days(previous_due, shift)
    new_final = _Calendar.add_days(str(plan.get("final_due_date")), shift)
    rid = ctx.make_id("pin_", plan_id, number, shift, today)
    ctx.create("plan_installments", rid, plan_txn_id=rid, plan_id=plan_id,
               customer_id=plan.get("customer_id"), account_id=plan.get("account_id"),
               event_type="plan_schedule_change_recorded", change_type="due_date_change",
               installment_number=number, due_date=new_due, txn_date=today,
               amount=round(float(plan.get("installment_amount") or 0), 2),
               funding_method=plan.get("funding_method"))
    ctx.update("payment_plans", plan_id, schedule_anchor_date=new_due,
               schedule_anchor_installment=number, final_due_date=new_final)
    return str({"change_reference": rid, "plan_id": plan_id, "installment_number": number,
                "previous_due_date": previous_due, "new_due_date": new_due,
                "new_final_due_date": new_final, "status": "due_date_change_recorded"})


@tool(owner="user", rw="write")
def authorize_payment_method_50f022be(ctx: ToolContext, plan_id: str, funding_method: str,
                                      authorization_method: str, installment_number: int) -> str:
    """The consumer personally authorizes a new payment method for the installments of their
    payment arrangement. One payment-method change is recorded on the arrangement's installment
    history, starting with the named installment, and the arrangement is rewritten with the new
    payment method, today's date as the date of the consumer's authorization and the way that
    authorization was given. The installment amount and the schedule are not changed. Afterwards
    the consumer can see the new payment method on the arrangement and the installment, with its
    due date, from which the new method collects.

    Args:
        plan_id: Id class — the payment plan reference number (the identifier) of the consumer's arrangement, as read to
            the consumer by the agent from the arrangement record.
        funding_method: Enum class — the payment method the consumer authorizes:
            ach_autopay when installments are to be debited automatically from a bank account;
            card_autopay when installments are to be charged automatically to a debit or credit
            card; manual_pay when the consumer will pay each installment themselves.
        authorization_method: Enum class — how the consumer gives this authorization:
            recorded_call when the consumer authorizes on the recorded telephone call in progress;
            e_signature when the consumer signs the authorization electronically.
        installment_number: Fixed-format class — the number of the first installment the new
            method collects, a non-negative integer (0 is the down payment, 1 the first regular
            installment).

    Returns:
        A dictionary rendered as text with: change_reference (string, the reference of the
        payment-method change entry recorded), plan_id (string), funding_method (the new method),
        authorization_method (as given), authorization_date (YYYY-MM-DD, today),
        first_installment (integer, the installment the new method collects first),
        first_due_date (YYYY-MM-DD, that installment's due date) and status (always
        "payment_method_authorized"); that status confirms the authorization is recorded.
    """
    rows = ctx.find("payment_plans", plan_id=plan_id)
    if not rows:
        return f"No payment plan found for {plan_id}."
    plan = rows[0]
    today = ctx.now()[:10]
    number = int(installment_number)
    first_due = _Calendar.due_date(plan, number)
    rid = ctx.make_id("pin_", plan_id, funding_method, authorization_method, number, today)
    ctx.create("plan_installments", rid, plan_txn_id=rid, plan_id=plan_id,
               customer_id=plan.get("customer_id"), account_id=plan.get("account_id"),
               event_type="plan_schedule_change_recorded", change_type="funding_method_change",
               installment_number=number, due_date=first_due, txn_date=today,
               amount=round(float(plan.get("installment_amount") or 0), 2),
               funding_method=funding_method)
    ctx.update("payment_plans", plan_id, funding_method=funding_method,
               authorization_date=today, authorization_method=authorization_method)
    return str({"change_reference": rid, "plan_id": plan_id, "funding_method": funding_method,
                "authorization_method": authorization_method, "authorization_date": today,
                "first_installment": number, "first_due_date": first_due,
                "status": "payment_method_authorized"})


@tool(owner="agent", rw="write")
def record_missed_installment_d21cca89(ctx: ToolContext, plan_id: str, installment_number: int) -> str:
    """Record one installment of a payment arrangement as missed. Ridgeline adds a missed entry
    for the named installment to the arrangement's installment history, carrying that
    installment's scheduled due date (read off the arrangement's schedule) and today's date as the
    date it was recorded; the missed entry moves no money, so the amount still scheduled under the
    arrangement is unchanged. The consumer and the agent can afterwards see the missed entry on
    the installment history.

    Args:
        plan_id: Id class — the payment plan reference number (the identifier) of the arrangement,
            as returned by the payment arrangement lookup for the consumer.
        installment_number: Fixed-format class — the number of the installment recorded as missed,
            a non-negative integer (0 is the down payment, 1 the first regular installment).

    Returns:
        A dictionary rendered as text with: missed_entry_reference (string, the reference of the
        missed entry recorded), plan_id (string), installment_number (integer), due_date
        (YYYY-MM-DD, the installment's scheduled due date), recorded_date (YYYY-MM-DD, today) and
        status (always "missed_entry_recorded"); that status confirms the entry is on the history.
    """
    rows = ctx.find("payment_plans", plan_id=plan_id)
    if not rows:
        return f"No payment plan found for {plan_id}."
    plan = rows[0]
    today = ctx.now()[:10]
    number = int(installment_number)
    due = _Calendar.due_date(plan, number)
    rid = ctx.make_id("pin_", plan_id, "missed", number)
    ctx.create("plan_installments", rid, plan_txn_id=rid, plan_id=plan_id,
               customer_id=plan.get("customer_id"), account_id=plan.get("account_id"),
               event_type="plan_installment_missed", installment_number=number, due_date=due,
               txn_date=today, amount=0.0)
    return str({"missed_entry_reference": rid, "plan_id": plan_id, "installment_number": number,
                "due_date": due, "recorded_date": today, "status": "missed_entry_recorded"})


@tool(owner="agent", rw="write")
def resume_suspended_plan_416c1e83(ctx: ToolContext, plan_id: str, first_installment_number: int,
                                   days_to_first_installment: int) -> str:
    """Resume a suspended payment arrangement on a new schedule. The arrangement's status returns
    to active; the named installment becomes the first installment after resumption, falling due
    the given number of calendar days after today; every later installment follows on the
    arrangement's frequency (weekly, every two weeks, or the same day of each following month),
    and the final due date is moved accordingly. Amounts and the installment count are not
    changed. The consumer can afterwards see the arrangement active again, with the new first due
    date and the new final due date.

    Args:
        plan_id: Id class — the payment plan reference number (the identifier) of the suspended
            arrangement, as returned by the payment arrangement lookup for the consumer.
        first_installment_number: Fixed-format class — the number of the installment that falls due
            first after resumption, a non-negative integer.
        days_to_first_installment: Fixed-format class — the calendar days from today to the due date
            of that first installment, a non-negative integer of whole calendar days.

    Returns:
        A dictionary rendered as text with: plan_id (string), status (always "active"),
        first_installment (integer), first_due_date (YYYY-MM-DD), final_due_date (YYYY-MM-DD) and
        resumed_date (YYYY-MM-DD, today); status "active" confirms the arrangement has resumed.
    """
    rows = ctx.find("payment_plans", plan_id=plan_id)
    if not rows:
        return f"No payment plan found for {plan_id}."
    plan = rows[0]
    today = ctx.now()[:10]
    number = int(first_installment_number)
    first_due = _Calendar.add_days(today, int(days_to_first_installment))
    resumed = dict(plan, schedule_anchor_date=first_due, schedule_anchor_installment=number)
    final_number = int(plan.get("installment_count") or 0) - 1
    final_due = _Calendar.due_date(resumed, final_number)
    ctx.update("payment_plans", plan_id, status="active", schedule_anchor_date=first_due,
               schedule_anchor_installment=number, final_due_date=final_due)
    return str({"plan_id": plan_id, "status": "active", "first_installment": number,
                "first_due_date": first_due, "final_due_date": final_due, "resumed_date": today})


@tool(owner="agent", rw="write")
def reage_missed_installment_128922de(ctx: ToolContext, plan_id: str, installment_number: int,
                                      installment_amount: float) -> str:
    """Re-age one installment of a payment arrangement by a deferral. Ridgeline records one granted
    deferral on the arrangement's installment history: the named installment is moved to one
    period after the arrangement's current final installment, the installment after it becomes the
    next one due on its scheduled date, the final due date becomes the moved installment's new due
    date, and the regular installment amount is set to the amount given. The consumer can
    afterwards see the moved installment's new due date, the next due installment and the regular
    installment amount on the arrangement.

    Args:
        plan_id: Id class — the payment plan reference number (the identifier) of the arrangement,
            as returned by the payment arrangement lookup for the consumer.
        installment_number: Fixed-format class — the number of the installment that is re-aged, a
            non-negative integer.
        installment_amount: Fixed-format class — the regular installment amount after the change, in
            USD, a decimal number rounded to 2 decimal places.

    Returns:
        A dictionary rendered as text with: deferral_reference (string, the reference of the
        deferral recorded), plan_id (string), installment_number (integer), new_due_date
        (YYYY-MM-DD, the moved installment's due date), next_installment (integer),
        next_due_date (YYYY-MM-DD), installment_amount (number, USD) and status (always
        "deferral_recorded"); that status confirms the deferral is recorded.
    """
    rows = ctx.find("payment_plans", plan_id=plan_id)
    if not rows:
        return f"No payment plan found for {plan_id}."
    plan = rows[0]
    today = ctx.now()[:10]
    number = int(installment_number)
    amount = round(float(installment_amount), 2)
    freq = plan.get("payment_frequency")
    final_due = str(plan.get("final_due_date"))
    if freq == "weekly":
        new_due = _Calendar.add_days(final_due, 7)
    elif freq == "biweekly":
        new_due = _Calendar.add_days(final_due, 14)
    else:
        new_due = _Calendar.add_months(final_due, 1)
    next_number = number + 1
    next_due = _Calendar.due_date(plan, next_number)
    rid = ctx.make_id("pin_", plan_id, "deferral", number, amount, today)
    ctx.create("plan_installments", rid, plan_txn_id=rid, plan_id=plan_id,
               customer_id=plan.get("customer_id"), account_id=plan.get("account_id"),
               event_type="plan_schedule_change_recorded", change_type="deferral",
               installment_number=number, due_date=new_due, txn_date=today, amount=amount,
               funding_method=plan.get("funding_method"))
    ctx.update("payment_plans", plan_id, schedule_anchor_installment=next_number,
               schedule_anchor_date=next_due, final_due_date=new_due, installment_amount=amount)
    return str({"deferral_reference": rid, "plan_id": plan_id, "installment_number": number,
                "new_due_date": new_due, "next_installment": next_number, "next_due_date": next_due,
                "installment_amount": amount, "status": "deferral_recorded"})


@tool(owner="user", rw="write")
def authorize_restructured_installments_370d01b0(ctx: ToolContext, plan_id: str, installment_amount: float,
                                                 installment_count: int, final_due_date: str,
                                                 stated_net_monthly_income: float,
                                                 authorization_method: str) -> str:
    """The consumer personally authorizes a restructure of their payment arrangement. One
    restructure is recorded on the arrangement's installment history, starting with the
    arrangement's next due installment, and the arrangement is rewritten with the new regular
    installment amount, the new total number of installments, the new final due date, the
    consumer's stated net monthly household income for the budget review, today's date as the
    date of the consumer's authorization and the way it was given. The payment method and the
    next due date are not changed. Afterwards the consumer can see the new regular installment,
    the installment count and the final due date on the arrangement.

    Args:
        plan_id: Id class — the payment plan reference number (the identifier) of the consumer's
            arrangement, as read to the consumer by the agent from the arrangement record.
        installment_amount: Fixed-format class — the new regular installment amount, in USD, a
            decimal number rounded to 2 decimal places.
        installment_count: Fixed-format class — the new total number of installments of the
            arrangement, counting the installments already paid and any down payment, a positive
            integer.
        final_due_date: Fixed-format class — the due date of the last installment after the
            restructure, in YYYY-MM-DD format.
        stated_net_monthly_income: Fixed-format class — the consumer's net monthly household income
            as the consumer states it for the budget review, in USD, a decimal number rounded to 2
            decimal places.
        authorization_method: Enum class — how the consumer gives this authorization:
            recorded_call when the consumer authorizes on the recorded telephone call in progress;
            e_signature when the consumer signs the authorization electronically.

    Returns:
        A dictionary rendered as text with: change_reference (string, the reference of the
        restructure recorded), plan_id (string), first_installment (integer, the first installment
        at the new amount), installment_amount (number, USD), installment_count (integer),
        final_due_date (YYYY-MM-DD), authorization_date (YYYY-MM-DD, today) and status (always
        "restructure_authorized"); that status confirms the restructure is recorded.
    """
    rows = ctx.find("payment_plans", plan_id=plan_id)
    if not rows:
        return f"No payment plan found for {plan_id}."
    plan = rows[0]
    today = ctx.now()[:10]
    amount = round(float(installment_amount), 2)
    count = int(installment_count)
    income = round(float(stated_net_monthly_income), 2)
    first = int(plan.get("schedule_anchor_installment") or 0)
    rid = ctx.make_id("pin_", plan_id, "restructure", amount, count, final_due_date, income,
                      authorization_method, today)
    ctx.create("plan_installments", rid, plan_txn_id=rid, plan_id=plan_id,
               customer_id=plan.get("customer_id"), account_id=plan.get("account_id"),
               event_type="plan_schedule_change_recorded", change_type="restructure",
               installment_number=first, due_date=plan.get("schedule_anchor_date"), txn_date=today,
               amount=amount, funding_method=plan.get("funding_method"))
    ctx.update("payment_plans", plan_id, installment_amount=amount, installment_count=count,
               final_due_date=final_due_date, stated_net_monthly_income=income,
               authorization_date=today, authorization_method=authorization_method)
    return str({"change_reference": rid, "plan_id": plan_id, "first_installment": first,
                "installment_amount": amount, "installment_count": count,
                "final_due_date": final_due_date, "authorization_date": today,
                "status": "restructure_authorized"})

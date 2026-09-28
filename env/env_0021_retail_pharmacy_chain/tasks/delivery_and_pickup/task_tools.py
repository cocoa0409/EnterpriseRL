"""Hidden task tools of the delivery_and_pickup difficulty (Kestrel Pharmacy, Delivery & Pickup Services).

Each tool performs one atomic write on a patient's delivery plan and its fee ledger. None of them
judges eligibility, prerequisites or amounts: the caller works every figure out from the published
policies and the patient's records and passes it in.
"""

from erlbench import ToolContext, tool


@tool(owner="user", rw="write")
def settle_overdue_pass_fee_c99b5804(ctx: ToolContext, delivery_plan_id: str, cycle_start_date: str,
                                     amount_usd: float) -> str:
    """The patient pays, in person with their own card, the Delivery Pass subscription fee of a
    billing cycle that could not be collected, bringing a past-due delivery plan back into good
    standing. One call books one collected subscription fee on the plan's fee ledger for the named
    billing cycle, adds the amount to the fees the patient has paid on the plan, sets the plan's
    status to active and clears its past-due date. Afterwards the patient sees the payment on the
    plan's fee history and the plan shows as active; the returned receipt carries the payment
    reference, which confirms the payment went through.

    Args:
        delivery_plan_id: Id class — reference number of the patient's delivery plan whose overdue
            cycle is being paid, as shown by the delivery plan lookup.
        cycle_start_date: Fixed-format class — start date of the billing cycle this payment covers,
            written YYYY-MM-DD exactly as the plan record shows its current billing cycle start.
        amount_usd: Fixed-format class — amount the patient pays for the overdue cycle, in USD,
            a positive number with 2 decimal places (rounded to the cent).

    Returns:
        A text rendering of a dictionary with these fields: payment_reference (string, the
        reference number of the collected subscription fee entry), delivery_plan_id (string, the
        plan paid for), cycle_start_date (string, YYYY-MM-DD, the cycle covered), amount_usd (number,
        USD with 2 decimal places, the amount collected), plan_status (string, always "active" once
        the payment is booked) and fees_net_usd (number, USD with 2 decimal places, the fees paid on
        the plan net of refunds after this payment). A receipt carrying a payment_reference means
        the payment was booked.
    """
    found = ctx.find("delivery_plans", delivery_plan_id=delivery_plan_id)
    plan = found[0] if found else {}
    rid = ctx.make_id("dch_", delivery_plan_id, cycle_start_date, amount_usd)
    ctx.create("delivery_charges", rid, charge_id=rid, delivery_plan_id=delivery_plan_id,
               customer_id=plan.get("customer_id"), event_type="delivery_subscription_charged",
               event_date=ctx.now()[:10], fee_type="subscription", cycle_start_date=cycle_start_date,
               amount_usd=round(float(amount_usd), 2))
    prev = plan.get("fees_net_usd") or 0
    fees_net_usd = round(float(prev) + float(amount_usd), 2)
    ctx.update("delivery_plans", delivery_plan_id, status="active", past_due_since="",
               fees_net_usd=fees_net_usd)
    return str({"payment_reference": rid, "delivery_plan_id": delivery_plan_id,
                "cycle_start_date": cycle_start_date, "amount_usd": round(float(amount_usd), 2),
                "plan_status": "active", "fees_net_usd": fees_net_usd})


@tool(owner="agent", rw="write")
def charge_order_fee_01b49350(ctx: ToolContext, delivery_plan_id: str, source_order_id: str, fee_type: str,
                              amount_usd: float) -> str:
    """Books one fee on one delivery order of a patient's delivery plan and adds it to the fees the
    patient has paid on that plan. One call records a single fee of the stated kind against the
    named order, dated today, with the stated amount; it does not decide whether the fee is owed or
    how much it is. Afterwards the fee appears in the plan's fee history against that order and the
    plan's net fees paid go up by the amount; the returned receipt carries the fee reference, which
    confirms the fee was booked.

    Args:
        delivery_plan_id: Id class — reference number of the delivery plan the order belongs to, as
            shown by the delivery plan lookup.
        source_order_id: Id class — reference number of the delivery order the fee is for, as shown
            by the delivery order lookup for the placed order.
        fee_type: Enum class — the kind of fee booked, exactly one of: subscription — the fee of a
            Delivery Pass billing cycle, which belongs to a cycle and is never booked against an
            order; same_day_fee — the speed fee of an order delivered by same-day courier;
            express_fee — the speed fee of an order delivered by one-hour express courier;
            extended_radius_fee — the distance fee of a courier order delivered beyond the plan's
            free delivery radius; redelivery_fee — the fee of a redelivery that replaces a failed
            order.
        amount_usd: Fixed-format class — the fee charged, in USD, a positive number with 2 decimal
            places (rounded to the cent).

    Returns:
        A text rendering of a dictionary with these fields: fee_reference (string, the reference
        number of the booked fee), delivery_plan_id (string), source_order_id (string, the order
        charged), fee_type (string, the kind of fee booked), amount_usd (number, USD with 2 decimal
        places) and fees_net_usd (number, USD with 2 decimal places, the plan's fees paid net of
        refunds after this fee). A receipt carrying a fee_reference means the fee was booked.
    """
    found = ctx.find("delivery_plans", delivery_plan_id=delivery_plan_id)
    plan = found[0] if found else {}
    rid = ctx.make_id("dch_", delivery_plan_id, source_order_id, fee_type, amount_usd)
    ctx.create("delivery_charges", rid, charge_id=rid, delivery_plan_id=delivery_plan_id,
               customer_id=plan.get("customer_id"), event_type="delivery_order_fee_charged",
               event_date=ctx.now()[:10], source_order_id=source_order_id, fee_type=fee_type,
               amount_usd=round(float(amount_usd), 2))
    prev = plan.get("fees_net_usd") or 0
    fees_net_usd = round(float(prev) + float(amount_usd), 2)
    ctx.update("delivery_plans", delivery_plan_id, fees_net_usd=fees_net_usd)
    return str({"fee_reference": rid, "delivery_plan_id": delivery_plan_id, "source_order_id": source_order_id,
                "fee_type": fee_type, "amount_usd": round(float(amount_usd), 2), "fees_net_usd": fees_net_usd})


@tool(owner="agent", rw="write")
def refund_late_delivery_fee_e6f66314(ctx: ToolContext, delivery_plan_id: str, source_charge_id: str,
                                      source_order_id: str, amount_usd: float) -> str:
    """Refunds part or all of one fee that was charged on a delivery order that arrived late, as a
    late-delivery refund to the patient. One call records a single refund, dated today, against the
    named fee and order with the stated amount and the reason late delivery, and takes the amount
    off the fees the patient has paid on the plan; it does not decide whether the order was late or
    how much is due. Afterwards the refund appears in the plan's fee history next to the fee it
    returns; the returned receipt carries the refund reference, which confirms the refund was booked.

    Args:
        delivery_plan_id: Id class — reference number of the delivery plan the order belongs to, as
            shown by the delivery plan lookup.
        source_charge_id: Id class — reference number of the single fee being refunded, as shown by
            the delivery fee lookup for the late order.
        source_order_id: Id class — reference number of the late delivery order the fee was charged
            on, as shown by the delivery order lookup.
        amount_usd: Fixed-format class — the amount refunded, in USD, a positive number with 2
            decimal places (rounded to the cent).

    Returns:
        A text rendering of a dictionary with these fields: refund_reference (string, the reference
        number of the booked refund), delivery_plan_id (string), source_charge_id (string, the fee
        refunded), source_order_id (string, the order concerned), refund_reason (string, always
        "late_delivery"), amount_usd (number, USD with 2 decimal places) and fees_net_usd (number, USD
        with 2 decimal places, the plan's fees paid net of refunds after this refund). A receipt
        carrying a refund_reference means the refund was booked.
    """
    found = ctx.find("delivery_plans", delivery_plan_id=delivery_plan_id)
    plan = found[0] if found else {}
    rid = ctx.make_id("dch_", delivery_plan_id, source_charge_id, source_order_id, "late_delivery", amount_usd)
    ctx.create("delivery_charges", rid, charge_id=rid, delivery_plan_id=delivery_plan_id,
               customer_id=plan.get("customer_id"), event_type="delivery_fee_refunded",
               event_date=ctx.now()[:10], source_charge_id=source_charge_id, source_order_id=source_order_id,
               refund_reason="late_delivery", amount_usd=round(float(amount_usd), 2))
    prev = plan.get("fees_net_usd") or 0
    fees_net_usd = round(float(prev) - float(amount_usd), 2)
    ctx.update("delivery_plans", delivery_plan_id, fees_net_usd=fees_net_usd)
    return str({"refund_reference": rid, "delivery_plan_id": delivery_plan_id, "source_charge_id": source_charge_id,
                "source_order_id": source_order_id, "refund_reason": "late_delivery",
                "amount_usd": round(float(amount_usd), 2), "fees_net_usd": fees_net_usd})


@tool(owner="agent", rw="write")
def refund_cancelled_order_fee_665693af(ctx: ToolContext, delivery_plan_id: str, source_charge_id: str,
                                        source_order_id: str, amount_usd: float) -> str:
    """Refunds one fee that was charged on a delivery order cancelled before it was dispatched. One
    call records a single refund, dated today, against the named fee and order with the stated
    amount and the reason cancelled before dispatch, and takes the amount off the fees the patient
    has paid on the plan; it does not decide whether a refund is owed or how much. Afterwards the
    refund appears in the plan's fee history next to the fee it returns; the returned receipt
    carries the refund reference, which confirms the refund was booked.

    Args:
        delivery_plan_id: Id class — reference number of the delivery plan the cancelled order
            belongs to, as shown by the delivery plan lookup.
        source_charge_id: Id class — reference number of the single fee being refunded, as shown by
            the delivery fee lookup for the cancelled order.
        source_order_id: Id class — reference number of the cancelled delivery order the fee was
            charged on, as shown by the delivery order lookup.
        amount_usd: Fixed-format class — the amount refunded, in USD, a positive number with 2
            decimal places (rounded to the cent).

    Returns:
        A text rendering of a dictionary with these fields: refund_reference (string, the reference
        number of the booked refund), delivery_plan_id (string), source_charge_id (string, the fee
        refunded), source_order_id (string, the cancelled order), refund_reason (string, always
        "cancelled_before_dispatch"), amount_usd (number, USD with 2 decimal places) and
        fees_net_usd (number, USD with 2 decimal places, the plan's fees paid net of refunds after
        this refund). A receipt carrying a refund_reference means the refund was booked.
    """
    found = ctx.find("delivery_plans", delivery_plan_id=delivery_plan_id)
    plan = found[0] if found else {}
    rid = ctx.make_id("dch_", delivery_plan_id, source_charge_id, source_order_id, "cancelled_before_dispatch",
                      amount_usd)
    ctx.create("delivery_charges", rid, charge_id=rid, delivery_plan_id=delivery_plan_id,
               customer_id=plan.get("customer_id"), event_type="delivery_fee_refunded",
               event_date=ctx.now()[:10], source_charge_id=source_charge_id, source_order_id=source_order_id,
               refund_reason="cancelled_before_dispatch", amount_usd=round(float(amount_usd), 2))
    prev = plan.get("fees_net_usd") or 0
    fees_net_usd = round(float(prev) - float(amount_usd), 2)
    ctx.update("delivery_plans", delivery_plan_id, fees_net_usd=fees_net_usd)
    return str({"refund_reference": rid, "delivery_plan_id": delivery_plan_id, "source_charge_id": source_charge_id,
                "source_order_id": source_order_id, "refund_reason": "cancelled_before_dispatch",
                "amount_usd": round(float(amount_usd), 2), "fees_net_usd": fees_net_usd})


@tool(owner="user", rw="write")
def switch_delivery_pass_b46d5026(ctx: ToolContext, delivery_plan_id: str, variant_name: str, cycle_start_date: str,
                                  amount_usd: float) -> str:
    """The patient buys, in person with their own card, a different Kestrel delivery plan in place of
    the one they hold, and pays its opening billing cycle. One call changes the plan held on the same
    delivery plan record to the chosen plan, starts its billing cycle on the stated date (the cycle
    runs one billing period from that date, its last day being one day short of the same date a
    period later: one calendar month for the monthly passes, twelve calendar months for the annual pass), keeps the plan active, books the payment as
    the subscription fee of that new cycle and adds it to the fees the patient has paid on the plan.
    Afterwards the patient sees the new plan name, the new cycle dates and the payment on the plan;
    the returned receipt carries the payment reference, which confirms the switch and payment.

    Args:
        delivery_plan_id: Id class — reference number of the patient's current delivery plan, as
            shown by the delivery plan lookup.
        variant_name: Enum class — the plan being bought, exactly one of: Kestrel Pay-Per-Delivery —
            the plan with no subscription, fees per order; Kestrel Mail Delivery — the plan with no
            subscription that ships by standard mail only; Kestrel Delivery Pass Monthly — the
            monthly subscription pass for any adult; Kestrel Senior Delivery Pass — the monthly
            subscription pass for patients aged 65 or over; Kestrel Delivery Pass Annual — the
            yearly subscription pass; Kestrel Specialty Courier Service — the courier service for
            patients holding a Specialty Limited-Distribution Prescription.
        cycle_start_date: Fixed-format class — start date of the new plan's billing cycle, written
            YYYY-MM-DD.
        amount_usd: Fixed-format class — the amount the patient pays for the new plan's opening
            billing cycle, in USD, a positive number with 2 decimal places (rounded to the cent
            before it is passed).

    Returns:
        A text rendering of a dictionary with these fields: payment_reference (string, the reference
        number of the booked subscription fee), delivery_plan_id (string), variant_name (string, the
        plan now held), cycle_start_date and cycle_end_date (strings, YYYY-MM-DD, the new billing
        cycle), amount_usd (number, USD with 2 decimal places, the amount paid), plan_status (string,
        always "active") and fees_net_usd (number, USD with 2 decimal places, the plan's fees paid net
        of refunds after this payment). A receipt carrying a payment_reference means the switch and
        payment were booked.
    """
    found = ctx.find("delivery_plans", delivery_plan_id=delivery_plan_id)
    plan = found[0] if found else {}
    months = 12 if variant_name == "Kestrel Delivery Pass Annual" else 1
    # Civil-date arithmetic with integers only (no clock access): the start date is read in the ISO 8601
    # calendar or week form (fixed-width digit fields; trailing characters are not read), the end date is the day before the same date one billing period later.
    if not isinstance(cycle_start_date, str):
        raise TypeError("fromisoformat: argument must be str")
    text = cycle_start_date

    def _bad():
        return ValueError(f"Invalid isoformat string: {cycle_start_date!r}")

    def _num(chunk, width):
        if len(chunk) != width or any(ch not in "0123456789" for ch in chunk):
            raise _bad()
        return int(chunk)

    def _leap(y):
        return y % 4 == 0 and (y % 100 != 0 or y % 400 == 0)

    def _month_len(y, m):
        return [31, 29 if _leap(y) else 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31][m - 1]

    def _ordinal(y, m, d):  # 0001-01-01 is day 1
        yb = y - 1
        before_month = sum(_month_len(y, k) for k in range(1, m))
        return yb * 365 + yb // 4 - yb // 100 + yb // 400 + before_month + d

    def _civil(n):
        y = (n - 1) // 366 + 1
        while _ordinal(y + 1, 1, 1) <= n:
            y += 1
        m = 1
        while m < 12 and _ordinal(y, m + 1, 1) <= n:
            m += 1
        return y, m, n - _ordinal(y, m, 1) + 1

    try:  # the date is read from its UTF-8 bytes, one character per byte
        text = text.encode("utf-8").decode("latin-1")
    except UnicodeEncodeError:
        raise _bad() from None
    if len(text) not in (7, 8, 10):
        raise _bad()
    s_year = _num(text[0:4], 4)
    has_sep = text[4] == "-"
    pos = 4 + has_sep
    if text[pos:pos + 1] == "W":
        pos += 1
        week = _num(text[pos:pos + 2], 2)
        pos += 2
        weekday = 1
        if len(text) > pos:
            if (text[pos:pos + 1] == "-") != has_sep:
                raise _bad()
            pos += has_sep
            weekday = _num(text[pos:pos + 1], 1)
        if s_year < 1:
            raise _bad()
        jan1_weekday = (_ordinal(s_year, 1, 1) + 6) % 7  # Monday is 0
        if not 0 < week < 53:
            if not (week == 53 and (jan1_weekday == 3 or (jan1_weekday == 2 and _leap(s_year)))):
                raise _bad()
        if not 0 < weekday < 8:
            raise _bad()
        week1_monday = _ordinal(s_year, 1, 1) - jan1_weekday + (7 if jan1_weekday > 3 else 0)
        target = week1_monday + (week - 1) * 7 + (weekday - 1)
        if target > _ordinal(9999, 12, 31):  # a week of year 9999 reaching into year 10000
            raise ValueError("year 10000 is out of range")
        s_year, s_month, s_day = _civil(target)
    else:
        s_month = _num(text[pos:pos + 2], 2)
        pos += 2
        if (text[pos:pos + 1] == "-") != has_sep:
            raise _bad()
        pos += has_sep
        s_day = _num(text[pos:pos + 2], 2)
        if not 1 <= s_year:
            raise ValueError(f"year {s_year} is out of range")
        if not 1 <= s_month <= 12:
            raise ValueError("month must be in 1..12")
        if not 1 <= s_day <= _month_len(s_year, s_month):
            raise ValueError("day is out of range for month")
    total = s_year * 12 + (s_month - 1) + months
    year, month = divmod(total, 12)
    month += 1
    if year > 9999:
        raise ValueError(f"year {year} is out of range")
    end_day = min(s_day, _month_len(year, month)) - 1
    if end_day == 0:
        month -= 1
        if month == 0:
            year, month = year - 1, 12
        end_day = _month_len(year, month)
    cycle_end_date = f"{year:04d}-{month:02d}-{end_day:02d}"
    rid = ctx.make_id("dch_", delivery_plan_id, variant_name, cycle_start_date, amount_usd)
    ctx.create("delivery_charges", rid, charge_id=rid, delivery_plan_id=delivery_plan_id,
               customer_id=plan.get("customer_id"), event_type="delivery_subscription_charged",
               event_date=ctx.now()[:10], fee_type="subscription", cycle_start_date=cycle_start_date,
               amount_usd=round(float(amount_usd), 2))
    prev = plan.get("fees_net_usd") or 0
    fees_net_usd = round(float(prev) + float(amount_usd), 2)
    ctx.update("delivery_plans", delivery_plan_id, variant_name=variant_name, status="active",
               cycle_start_date=cycle_start_date, cycle_end_date=cycle_end_date, fees_net_usd=fees_net_usd)
    return str({"payment_reference": rid, "delivery_plan_id": delivery_plan_id, "variant_name": variant_name,
                "cycle_start_date": cycle_start_date, "cycle_end_date": cycle_end_date,
                "amount_usd": round(float(amount_usd), 2), "plan_status": "active", "fees_net_usd": fees_net_usd})

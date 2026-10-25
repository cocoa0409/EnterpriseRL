"""Hidden task tools of the factory_order_milestones_and_delays difficulty (Factory Production Orders).

Each tool performs one atomic write on a factory order or its milestone record and returns a receipt.
Tools never check eligibility, prerequisites or amounts; the agent works every value out from the
published policy and the records before calling.
"""

from erlbench import ToolContext, tool


class _CalendarDay:
    """Pure calendar arithmetic on YYYY-MM-DD strings (proleptic Gregorian day numbers)."""

    @staticmethod
    def day_number(text: str) -> int:
        y, m, d = (int(part) for part in str(text)[:10].split("-"))
        y -= 1 if m <= 2 else 0
        era = (y if y >= 0 else y - 399) // 400
        yoe = y - era * 400
        doy = (153 * (m + (-3 if m > 2 else 9)) + 2) // 5 + d - 1
        doe = yoe * 365 + yoe // 4 - yoe // 100 + doy
        return era * 146097 + doe

    @staticmethod
    def from_day_number(n: int) -> str:
        era = (n if n >= 0 else n - 146096) // 146097
        doe = n - era * 146097
        yoe = (doe - doe // 1460 + doe // 36524 - doe // 146096) // 365
        y = yoe + era * 400
        doy = doe - (365 * yoe + yoe // 4 - yoe // 100)
        mp = (5 * doy + 2) // 153
        d = doy - (153 * mp + 2) // 5 + 1
        m = mp + (3 if mp < 10 else -9)
        y += 1 if m <= 2 else 0
        return f"{y:04d}-{m:02d}-{d:02d}"

    @staticmethod
    def plus_days(text: str, days: int) -> str:
        return _CalendarDay.from_day_number(_CalendarDay.day_number(text) + int(days))


@tool(owner="agent", rw="write")
def record_late_acknowledgment_notice_952cb75c(ctx: ToolContext, factory_order_id: str,
                                               days_to_revised_ship_date: int) -> str:
    """Record a late-acknowledgment delay notice on a factory production order. One call writes one
    delay notice dated today with the cause late acknowledgment and the revised projected ship date,
    and moves the order's current projected ship date later to that revised date (a notice never
    moves it earlier: when the revised date is not later, the current date stays as it is); the date
    committed on the acknowledgment is left unchanged. Afterwards the notice is listed among the order's milestone
    records and the order shows the new current ship date.

    Args:
        factory_order_id: Id class — the reference number of the factory production order the notice
            is recorded on, as returned by the factory order lookup for the customer.
        days_to_revised_ship_date: Fixed-format class — the revised projected ship date written as a
            whole integer number of calendar days from today's date to that date; 0 means today and a
            negative integer means a date before today.

    Returns:
        A dictionary receipt: status ("recorded" on success), order_milestone_id (the reference
        number of the new delay notice), factory_order_id (the order it was recorded on),
        delay_cause (always "late_acknowledgment"), notice_date (today's date, YYYY-MM-DD),
        revised_ship_date (the revised projected ship date recorded, YYYY-MM-DD) and
        current_ship_date (the order's current projected ship date after the call, YYYY-MM-DD).
    """
    order = ctx.find("factory_orders", factory_order_id=factory_order_id)
    customer_id = order[0].get("customer_id") if order else ""
    today = ctx.now()[:10]
    revised = _CalendarDay.plus_days(today, int(days_to_revised_ship_date))
    rid = ctx.make_id("omd_", factory_order_id, days_to_revised_ship_date)
    ctx.create("order_milestones", rid, order_milestone_id=rid, factory_order_id=factory_order_id,
               customer_id=customer_id, event_type="order_delay_noticed", milestone_date=today,
               milestone_kind="not_applicable", revised_ship_date=revised, delay_cause="late_acknowledgment",
               remake_cause="not_applicable", unit_count=0, week_count=0, amount=0.0,
               charge_kind="not_applicable", source_order_milestone_id=None, window_contract_id=None,
               door_contract_id=None)
    standing = str(order[0].get("current_ship_date") or "") if order else ""
    current = revised if revised > standing else standing
    ctx.update("factory_orders", factory_order_id, current_ship_date=current)
    return str({"status": "recorded", "order_milestone_id": rid, "factory_order_id": factory_order_id,
                "delay_cause": "late_acknowledgment", "notice_date": today, "revised_ship_date": revised,
                "current_ship_date": current})


@tool(owner="agent", rw="write")
def release_customer_hold_268345ec(ctx: ToolContext, factory_order_id: str, days_to_new_ship_date: int) -> str:
    """Release a customer hold on a factory production order so it re-enters the production queue.
    One call moves the order from on hold back to entered, sets its current projected ship date to
    the new date given, and records the matching delay notice dated today with the cause customer
    hold and that new date. The hold start date and the date committed on the acknowledgment stay
    as they were. Afterwards the order shows the entered status and the new current ship date, and
    the notice is listed among its milestone records.

    Args:
        factory_order_id: Id class — the reference number of the factory production order being
            released, as returned by the factory order lookup for the customer.
        days_to_new_ship_date: Fixed-format class — the new projected ship date written as a whole
            integer number of calendar days from today's date to that date; 0 means today.

    Returns:
        A dictionary receipt: status ("released" on success), factory_order_id (the released order),
        order_status (the order's status after the call, "entered"), order_milestone_id (the
        reference number of the hold delay notice), release_date (today's date, YYYY-MM-DD) and
        new_ship_date (the order's new current ship date, YYYY-MM-DD).
    """
    order = ctx.find("factory_orders", factory_order_id=factory_order_id)
    customer_id = order[0].get("customer_id") if order else ""
    today = ctx.now()[:10]
    new_date = _CalendarDay.plus_days(today, int(days_to_new_ship_date))
    ctx.update("factory_orders", factory_order_id, status="entered", current_ship_date=new_date)
    rid = ctx.make_id("omh_", factory_order_id, days_to_new_ship_date)
    ctx.create("order_milestones", rid, order_milestone_id=rid, factory_order_id=factory_order_id,
               customer_id=customer_id, event_type="order_delay_noticed", milestone_date=today,
               milestone_kind="not_applicable", revised_ship_date=new_date, delay_cause="customer_hold",
               remake_cause="not_applicable", unit_count=0, week_count=0, amount=0.0,
               charge_kind="not_applicable", source_order_milestone_id=None, window_contract_id=None,
               door_contract_id=None)
    return str({"status": "released", "factory_order_id": factory_order_id, "order_status": "entered",
                "order_milestone_id": rid, "release_date": today, "new_ship_date": new_date})


@tool(owner="user", rw="write")
def request_expedited_build_5d45bf5f(ctx: ToolContext, factory_order_id: str, fee_amount: float) -> str:
    """Place the customer's own request for an expedited build on their factory production order and
    book the expedite fee they accept. One call records one expedite fee charge on the order, dated
    today as the request date, priced on the units the order carries, and adds it to the order-level
    charges the customer owes. Afterwards the charge is listed among the order's milestone records.

    Args:
        factory_order_id: Id class — the reference number of the customer's factory production order,
            as read out by the agent from the factory order lookup.
        fee_amount: Fixed-format class — the expedite fee in USD as a positive amount with 2 decimal
            places, rounded to the cent.

    Returns:
        A dictionary receipt: status ("booked" on success), order_milestone_id (the reference number
        of the expedite fee charge), factory_order_id (the order charged), charge_kind (always
        "expedite_fee"), request_date (today's date, YYYY-MM-DD), unit_count (units the fee is
        priced on, an integer) and amount (the fee booked in USD, 2 decimal places).
    """
    order = ctx.find("factory_orders", factory_order_id=factory_order_id)
    customer_id = order[0].get("customer_id") if order else ""
    units = int(order[0].get("unit_count") or 0) if order else 0
    today = ctx.now()[:10]
    amount = round(float(fee_amount), 2)
    rid = ctx.make_id("omx_", factory_order_id, fee_amount)
    ctx.create("order_milestones", rid, order_milestone_id=rid, factory_order_id=factory_order_id,
               customer_id=customer_id, event_type="order_charge_assessed", milestone_date=today,
               milestone_kind="not_applicable", revised_ship_date="", delay_cause="not_applicable",
               remake_cause="not_applicable", unit_count=units, week_count=0, amount=amount,
               charge_kind="expedite_fee", source_order_milestone_id=None, window_contract_id=None,
               door_contract_id=None)
    return str({"status": "booked", "order_milestone_id": rid, "factory_order_id": factory_order_id,
                "charge_kind": "expedite_fee", "request_date": today, "unit_count": units, "amount": amount})


@tool(owner="agent", rw="write")
def record_remake_delay_notice_f2496c0b(ctx: ToolContext, factory_order_id: str, days_to_revised_ship_date: int) -> str:
    """Record the delay notice for a customer specification remake on a factory production order. One
    call writes one delay notice dated today with the cause customer specification remake and the
    revised projected ship date given, and moves the order's current projected ship date later to
    that revised date (a notice never moves it earlier: when the revised date is not later, the
    current date stays as it is); the date committed on the acknowledgment is left unchanged. Afterwards the notice
    is listed among the order's milestone records with its revised ship date.

    Args:
        factory_order_id: Id class — the reference number of the factory production order the notice
            is recorded on, as returned by the factory order lookup for the customer.
        days_to_revised_ship_date: Fixed-format class — the revised projected ship date written as a
            whole integer number of calendar days from today's date to that date; 0 means today and a
            negative integer means a date before today.

    Returns:
        A dictionary receipt: status ("recorded" on success), order_milestone_id (the reference
        number of the new delay notice), factory_order_id (the order it was recorded on),
        delay_cause (always "customer_spec_remake"), notice_date (today's date, YYYY-MM-DD),
        revised_ship_date (the revised projected ship date recorded, YYYY-MM-DD) and
        current_ship_date (the order's current projected ship date after the call, YYYY-MM-DD).
    """
    order = ctx.find("factory_orders", factory_order_id=factory_order_id)
    customer_id = order[0].get("customer_id") if order else ""
    today = ctx.now()[:10]
    revised = _CalendarDay.plus_days(today, int(days_to_revised_ship_date))
    rid = ctx.make_id("omr_", factory_order_id, days_to_revised_ship_date)
    ctx.create("order_milestones", rid, order_milestone_id=rid, factory_order_id=factory_order_id,
               customer_id=customer_id, event_type="order_delay_noticed", milestone_date=today,
               milestone_kind="not_applicable", revised_ship_date=revised, delay_cause="customer_spec_remake",
               remake_cause="not_applicable", unit_count=0, week_count=0, amount=0.0,
               charge_kind="not_applicable", source_order_milestone_id=None, window_contract_id=None,
               door_contract_id=None)
    standing = str(order[0].get("current_ship_date") or "") if order else ""
    current = revised if revised > standing else standing
    ctx.update("factory_orders", factory_order_id, current_ship_date=current)
    return str({"status": "recorded", "order_milestone_id": rid, "factory_order_id": factory_order_id,
                "delay_cause": "customer_spec_remake", "notice_date": today, "revised_ship_date": revised,
                "current_ship_date": current})


@tool(owner="agent", rw="write")
def assess_customer_remake_e3e4e81e(ctx: ToolContext, remake_record_id: str, charge_amount: float) -> str:
    """Bill the customer the charge for a remake of units on their factory production order. One call
    records one remake charge on the order the remake record belongs to, dated the date of that remake
    and priced on the units that remake covers, and adds it to the order-level charges the customer
    owes. Afterwards the charge is listed among the order's milestone records.

    Args:
        remake_record_id: Id class — the reference number of the remake record being charged, as
            returned by the order milestone lookup for the order.
        charge_amount: Fixed-format class — the remake charge in USD as a positive amount with 2
            decimal places, rounded to the cent.

    Returns:
        A dictionary receipt: status ("charged" on success), order_milestone_id (the reference number
        of the remake charge), factory_order_id (the order charged), charge_kind (always
        "remake_charge"), charge_date (the remake's date, YYYY-MM-DD), unit_count (units charged, an
        integer) and amount (the charge in USD, 2 decimal places).
    """
    remake = ctx.find("order_milestones", order_milestone_id=remake_record_id)
    row = remake[0] if remake else {}
    factory_order_id = row.get("factory_order_id")
    charge_date = str(row.get("milestone_date") or ctx.now()[:10])
    units = int(row.get("unit_count") or 0)
    amount = round(float(charge_amount), 2)
    rid = ctx.make_id("omc_", remake_record_id, charge_amount)
    ctx.create("order_milestones", rid, order_milestone_id=rid, factory_order_id=factory_order_id,
               customer_id=row.get("customer_id"), event_type="order_charge_assessed", milestone_date=charge_date,
               milestone_kind="not_applicable", revised_ship_date="", delay_cause="not_applicable",
               remake_cause="not_applicable", unit_count=units, week_count=0, amount=amount,
               charge_kind="remake_charge", source_order_milestone_id=None, window_contract_id=None,
               door_contract_id=None)
    return str({"status": "charged", "order_milestone_id": rid, "factory_order_id": factory_order_id,
                "charge_kind": "remake_charge", "charge_date": charge_date, "unit_count": units, "amount": amount})


@tool(owner="user", rw="write")
def file_on_time_claim_fe24f9ef(ctx: ToolContext, factory_order_id: str, credit_amount: float, weeks_late: int) -> str:
    """File the homeowner's own on-time guarantee claim on their factory production order that shipped
    late. One call books one on-time guarantee credit on the order, dated the order's ship date, with
    the credit amount, the full weeks late and the units on the order, and adds it to the guarantee
    credit the order holds. Afterwards the credit is listed among the order's milestone records.

    Args:
        factory_order_id: Id class — the reference number of the homeowner's factory production order,
            as read out by the agent from the factory order lookup.
        credit_amount: Fixed-format class — the guarantee credit in USD as a positive amount with 2
            decimal places, rounded to the cent.
        weeks_late: Fixed-format class — the full weeks late recorded with the credit, a whole
            non-negative integer count.

    Returns:
        A dictionary receipt: status ("credited" on success), order_milestone_id (the reference number
        of the guarantee credit), factory_order_id (the order credited), credit_date (the order's ship
        date, YYYY-MM-DD), weeks_late (an integer), unit_count (units on the order, an integer) and
        amount (the credit in USD, 2 decimal places).
    """
    order = ctx.find("factory_orders", factory_order_id=factory_order_id)
    row = order[0] if order else {}
    credit_date = str(row.get("ship_date") or ctx.now()[:10])
    units = int(row.get("unit_count") or 0)
    amount = round(float(credit_amount), 2)
    rid = ctx.make_id("omg_", factory_order_id, credit_amount, weeks_late)
    ctx.create("order_milestones", rid, order_milestone_id=rid, factory_order_id=factory_order_id,
               customer_id=row.get("customer_id"), event_type="order_guarantee_credit_earned",
               milestone_date=credit_date, milestone_kind="not_applicable", revised_ship_date="",
               delay_cause="not_applicable", remake_cause="not_applicable", unit_count=units,
               week_count=int(weeks_late), amount=amount, charge_kind="not_applicable",
               source_order_milestone_id=None, window_contract_id=None, door_contract_id=None)
    return str({"status": "credited", "order_milestone_id": rid, "factory_order_id": factory_order_id,
                "credit_date": credit_date, "weeks_late": int(weeks_late), "unit_count": units, "amount": amount})


@tool(owner="agent", rw="write")
def assess_branch_storage_97307cec(ctx: ToolContext, factory_order_id: str, fee_amount: float, billable_weeks: int) -> str:
    """Bill the storage fee for delivered units of a factory production order kept at the branch
    warehouse. One call records one storage fee charge on the order dated today, with the fee, the
    billable storage weeks and the units on the order, and adds it to the order-level charges the
    customer owes. Afterwards the charge is listed among the order's milestone records.

    Args:
        factory_order_id: Id class — the reference number of the factory production order whose units
            were stored, as returned by the factory order lookup for the customer.
        fee_amount: Fixed-format class — the storage fee in USD as a positive amount with 2 decimal
            places, rounded to the cent.
        billable_weeks: Fixed-format class — the billable storage weeks the fee covers, a whole
            non-negative integer count.

    Returns:
        A dictionary receipt: status ("charged" on success), order_milestone_id (the reference number
        of the storage charge), factory_order_id (the order charged), charge_kind (always
        "storage_fee"), charge_date (today's date, YYYY-MM-DD), week_count (billable weeks, an
        integer), unit_count (units on the order, an integer) and amount (the fee in USD, 2 decimal
        places).
    """
    order = ctx.find("factory_orders", factory_order_id=factory_order_id)
    row = order[0] if order else {}
    units = int(row.get("unit_count") or 0)
    today = ctx.now()[:10]
    amount = round(float(fee_amount), 2)
    rid = ctx.make_id("oms_", factory_order_id, fee_amount, billable_weeks)
    ctx.create("order_milestones", rid, order_milestone_id=rid, factory_order_id=factory_order_id,
               customer_id=row.get("customer_id"), event_type="order_charge_assessed", milestone_date=today,
               milestone_kind="not_applicable", revised_ship_date="", delay_cause="not_applicable",
               remake_cause="not_applicable", unit_count=units, week_count=int(billable_weeks), amount=amount,
               charge_kind="storage_fee", source_order_milestone_id=None, window_contract_id=None,
               door_contract_id=None)
    return str({"status": "charged", "order_milestone_id": rid, "factory_order_id": factory_order_id,
                "charge_kind": "storage_fee", "charge_date": today, "week_count": int(billable_weeks),
                "unit_count": units, "amount": amount})

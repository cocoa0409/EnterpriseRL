"""Task tools for the professional_email_seats difficulty (category email) of
env_0076_web_hosting_and_domain_registrar. Hidden atomic writes reached through unlock_* -> call_*.
"""

from erlbench import ToolContext, tool


_PRODUCTS = ('Harborline Mail Starter', 'Harborline Mail Plus', 'Harborline Mail Pro', 'Microsoft 365 Business Basic',
             'Microsoft 365 Business Standard', 'Microsoft 365 Business Premium')


class _Calc:
    """Pure-Python formatting and calendar helpers shared by the tools (no business judgement)."""

    @staticmethod
    def cents_half_up(value):
        """Round a money value half up to the cent, returning a float with two decimals."""
        cents = int(abs(float(value)) * 100 + 0.5 + 1e-9)
        sign = -1 if float(value) < 0 else 1
        return sign * cents / 100.0

    @staticmethod
    def _is_leap(y):
        return y % 4 == 0 and (y % 100 != 0 or y % 400 == 0)

    @staticmethod
    def _month_len(y, m):
        if m == 2:
            return 29 if _Calc._is_leap(y) else 28
        return 30 if m in (4, 6, 9, 11) else 31

    @staticmethod
    def add_months(iso_date, months):
        """Calendar date plus whole months, falling back to the month's last day where that day does not exist."""
        y, m, d = (int(x) for x in str(iso_date)[:10].split("-"))
        total = (y * 12 + (m - 1)) + int(months)
        ny, nm = divmod(total, 12)
        nm += 1
        nd = min(d, _Calc._month_len(ny, nm))
        return f"{ny:04d}-{nm:02d}-{nd:02d}"

    @staticmethod
    def minus_one_day(iso_date):
        """The calendar day before the given date."""
        y, m, d = (int(x) for x in str(iso_date)[:10].split("-"))
        if d > 1:
            return f"{y:04d}-{m:02d}-{d - 1:02d}"
        if m > 1:
            return f"{y:04d}-{m - 1:02d}-{_Calc._month_len(y, m - 1):02d}"
        return f"{y - 1:04d}-12-31"

    @staticmethod
    def renewal_span(term_end, billing_plan):
        """New term start, new term end and the last day the renewal line covers, by billing plan: a 12-month term on
        annual_prepaid (the line covers it all) and annual_monthly_billing (the line is its first monthly instalment),
        a 1-month term on monthly."""
        start = str(term_end)[:10]
        months = 1 if billing_plan == "monthly" else 12
        end = _Calc.add_months(start, months)
        line_end = _Calc.add_months(start, 1) if billing_plan == "annual_monthly_billing" else end
        return start, end, _Calc.minus_one_day(line_end)

    @staticmethod
    def order_number(row_id):
        """A Harborline order number, HL- followed by 8 digits, derived from the new line's reference."""
        digits = int(str(row_id)[-8:], 16) % 1000000
        return f"HL-04{digits:06d}"


@tool(owner="agent", rw="write")
def reactivate_suspended_mail_4fbd3039(ctx: ToolContext, email_plan_id: str, renewal_amount: float,
                                       renewed_seats: int, renewal_product: str) -> str:
    """Collect the unpaid renewal of a suspended email subscription on the customer's default card and reactivate it.
    One call books one renewal billing line on the subscription, charged to the default card on file, that bills
    every renewed seat, and restores mail access: the subscription becomes active, its suspension date is cleared,
    its licensed seat count becomes the renewed seat count given here, its product becomes the renewal product given
    here and the scheduled seat count and product are cleared, and its new term starts on the previous term end date
    and runs 12 calendar months on the annual prepaid and annual-billed-monthly plans or 1 calendar month on the monthly plan (falling back to the
    month's last day where that day does not exist); on the annual-billed-monthly plan the line is the new term's
    first monthly instalment. The customer sees the subscription active again with the new term dates and the
    renewal line in their email billing history.

    Args:
        email_plan_id: Id class — the reference number of the suspended email subscription being reactivated, as
            returned by the email subscription lookup for this customer.
        renewal_amount: Fixed-format class — the renewal amount to bill for the new term, in US dollars, a positive
            number with 2 decimal places; a value with more decimals is rounded half up to the cent before
            it is booked.
        renewed_seats: Fixed-format class — the number of licensed seats the subscription carries for the new term,
            every one of them billed on the line, an integer of at least 1.
        renewal_product: Enum class — the product the subscription carries for the new term, written as the official
            product name: Harborline Mail Starter, Harborline Mail Plus, Harborline Mail Pro, Microsoft 365 Business
            Basic, Microsoft 365 Business Standard or Microsoft 365 Business Premium.

    Returns:
        A one-line confirmation string. On success it reads "Reactivated subscription <email_plan_id>: renewal line
        <email_charge_id> order <order_ref> for <amount> USD (<seats> seats) charged to card; new term <term_start>
        to <term_end>; status active." where <email_charge_id> is the reference of the new billing line, <order_ref>
        is the Harborline order number (HL- followed by 8 digits), <amount> is the booked amount with two decimals,
        <seats> the renewed seat count, and <term_start>/<term_end> are YYYY-MM-DD dates. A string starting with
        "Error:" means nothing was booked (unknown subscription, a non-positive amount, a seat count below 1 or an
        unknown product name).
    """
    rows = ctx.find("email_holdings", email_plan_id=email_plan_id)
    if not rows:
        return f"Error: no email subscription {email_plan_id}."
    amount = _Calc.cents_half_up(renewal_amount)
    seats = int(renewed_seats)
    if amount <= 0 or seats < 1:
        return "Error: the renewal amount must be positive and the renewed seats at least 1."
    product = str(renewal_product or "").strip()
    if product not in _PRODUCTS:
        return f"Error: unknown email product {renewal_product}."
    sub = rows[0]
    plan = sub.get("billing_plan")
    start, end, line_end = _Calc.renewal_span(sub.get("term_end_date"), plan)
    kind = "monthly_instalment" if plan == "annual_monthly_billing" else "renewal"
    today = ctx.now()[:10]
    rid = ctx.make_id("ech_", email_plan_id, amount, seats)
    order = _Calc.order_number(rid)
    ctx.create("email_charges", rid, email_charge_id=rid, email_plan_id=email_plan_id,
               customer_id=sub.get("customer_id"), event_type="email_renewal_charge", charge_type=kind,
               amount=amount, seats=seats, target_variant="none", period_start=start,
               period_end=line_end, charge_date=today, order_ref=order, payment_method="card",
               original_email_charge_id=None, refund_destination="none")
    ctx.update("email_holdings", email_plan_id, status="active", suspended_date="", term_start_date=start,
               term_end_date=end, seat_count=seats, scheduled_seat_count=0, variant_name=product,
               scheduled_variant="none")
    return (f"Reactivated subscription {email_plan_id}: renewal line {rid} order {order} for {amount:.2f} USD "
            f"({seats} seats) charged to card; new term {start} to {end}; status active.")


@tool(owner="user", rw="write")
def upgrade_mail_product_74224a57(ctx: ToolContext, email_plan_id: str, upgrade_amount: float) -> str:
    """The account holder pays, personally at Harborline's secure checkout with PayPal, the move of their email
    subscription up to the top product of its family: Harborline Mail Pro for a Harborline Mail Starter or Plus
    subscription, Microsoft 365 Business Premium for a Microsoft 365 Business Basic or Standard one. One call books
    one upgrade billing line on the subscription covering and billing every licensed seat from today to the term end
    date, paid by PayPal, and switches the subscription's product to the target product at once; the seat count,
    billing plan and term dates do not change. The holder sees the subscription on the target product and the upgrade
    line in their email billing history.

    Args:
        email_plan_id: Id class — the reference number of the customer's email subscription being moved up, as
            returned by the email subscription lookup and read out to the customer by the agent.
        upgrade_amount: Fixed-format class — the upgrade amount to bill, in US dollars, a positive number with 2
            decimal places; a value with more decimals is rounded half up to the cent before it is booked.

    Returns:
        A one-line confirmation string. On success it reads "Upgraded subscription <email_plan_id> to <product>:
        upgrade line <email_charge_id> order <order_ref> for <amount> USD covering <seats> seats to <term_end>, paid
        by PayPal." where <product> is the target product's official name, <email_charge_id> the reference of the new
        billing line, <order_ref> the Harborline order number (HL- followed by 8 digits), <amount> the booked amount
        with two decimals, <seats> the licensed seat count upgraded and <term_end> the term end date as YYYY-MM-DD. A
        string starting with "Error:" means nothing was booked (unknown subscription, a subscription already on the
        top product of its family, or a non-positive amount).
    """
    rows = ctx.find("email_holdings", email_plan_id=email_plan_id)
    if not rows:
        return f"Error: no email subscription {email_plan_id}."
    amount = _Calc.cents_half_up(upgrade_amount)
    if amount <= 0:
        return "Error: the upgrade amount must be positive."
    sub = rows[0]
    current = str(sub.get("variant_name"))
    if current in ("Harborline Mail Starter", "Harborline Mail Plus"):
        target = "Harborline Mail Pro"
    elif current in ("Microsoft 365 Business Basic", "Microsoft 365 Business Standard"):
        target = "Microsoft 365 Business Premium"
    else:
        return f"Error: subscription {email_plan_id} is already on the top product of its family."
    seats = int(sub.get("seat_count") or 0)
    end = str(sub.get("term_end_date"))[:10]
    today = ctx.now()[:10]
    rid = ctx.make_id("ech_", email_plan_id, amount, target)
    order = _Calc.order_number(rid)
    ctx.create("email_charges", rid, email_charge_id=rid, email_plan_id=email_plan_id,
               customer_id=sub.get("customer_id"), event_type="email_seat_charge", charge_type="upgrade_proration",
               amount=amount, seats=seats, target_variant=target, period_start=today,
               period_end=end, charge_date=today, order_ref=order, payment_method="paypal",
               original_email_charge_id=None, refund_destination="none")
    ctx.update("email_holdings", email_plan_id, variant_name=target)
    return (f"Upgraded subscription {email_plan_id} to {target}: upgrade line {rid} order {order} for "
            f"{amount:.2f} USD covering {seats} seats to {end}, paid by PayPal.")


@tool(owner="agent", rw="write")
def bill_unbilled_mail_seats_5cd17f30(ctx: ToolContext, email_plan_id: str, customer_id: str, catch_up_amount: float,
                                      catch_up_seats: int) -> str:
    """Bill, on the customer's default card, seats an email subscription already carries but that were never billed
    for its current term. One call books one added-seat billing line on the subscription that bills every seat it
    covers, charged to the default card on file; the line covers the current term on record, from the term start date
    to the term end date, on every billing plan. The licensed seat count, the plan and the term dates do not change. The customer sees the new line in their email
    billing history.

    Args:
        email_plan_id: Id class — the reference number of the email subscription whose seats are being billed, as
            returned by the email subscription lookup for this customer.
        customer_id: Id class — the customer reference number of the subscription's holder, as returned by the
            customer profile lookup.
        catch_up_amount: Fixed-format class — the amount to bill for the seats, in US dollars, a positive number with 2
            decimal places; a value with more decimals is rounded half up to the cent before it is booked.
        catch_up_seats: Fixed-format class — the number of seats the line bills, an integer of at least 1.

    Returns:
        A one-line confirmation string. On success it reads "Billed <seats> seat(s) on subscription <email_plan_id>:
        line <email_charge_id> order <order_ref> for <amount> USD covering <period_start> to <period_end>, charged to
        card." where <email_charge_id> is the reference of the new billing line, <order_ref> the Harborline order number
        (HL- followed by 8 digits), <amount> the booked amount with two decimals and the period dates are YYYY-MM-DD. A
        string starting with "Error:" means nothing was booked (unknown subscription, a non-positive amount or fewer
        than 1 seat).
    """
    rows = ctx.find("email_holdings", email_plan_id=email_plan_id)
    if not rows:
        return f"Error: no email subscription {email_plan_id}."
    amount = _Calc.cents_half_up(catch_up_amount)
    seats = int(catch_up_seats)
    if amount <= 0 or seats < 1:
        return "Error: the amount must be positive and the seats at least 1."
    sub = rows[0]
    start = str(sub.get("term_start_date"))[:10]
    end = str(sub.get("term_end_date"))[:10]
    today = ctx.now()[:10]
    rid = ctx.make_id("ech_", email_plan_id, customer_id, amount, seats)
    order = _Calc.order_number(rid)
    ctx.create("email_charges", rid, email_charge_id=rid, email_plan_id=email_plan_id, customer_id=customer_id,
               event_type="email_seat_charge", charge_type="added_seats", amount=amount, seats=seats,
               target_variant="none", period_start=start, period_end=end, charge_date=today, order_ref=order,
               payment_method="card", original_email_charge_id=None, refund_destination="none")
    return (f"Billed {seats} seat(s) on subscription {email_plan_id}: line {rid} order {order} for {amount:.2f} USD "
            f"covering {start} to {end}, charged to card.")


@tool(owner="agent", rw="write")
def pay_late_mail_renewal_a889cd52(ctx: ToolContext, email_plan_id: str, renewal_amount: float,
                                   renewed_seats: int, renewal_product: str) -> str:
    """Collect, on the customer's default card on file, the renewal of an active email subscription that falls due on its
    term end date, whether it is billed on or before that due date or, overdue, after it went unpaid. One call books
    one renewal billing line on the subscription, charged to the default card on file, that bills every renewed
    seat, and starts the new term: it runs from the previous term end date for 1 calendar month on the monthly plan
    or 12 calendar months on the annual prepaid and annual-billed-monthly plans (falling back to the month's last
    day where that day does not exist), the line being the new term's first monthly instalment on the
    annual-billed-monthly plan; the licensed seat count becomes the renewed seat count given here, the product becomes the renewal
    product given here, and the scheduled seat count and product are cleared. The customer sees the new term on the
    subscription and the renewal line in their email billing history.

    Args:
        email_plan_id: Id class — the reference number of the email subscription whose renewal is being collected,
            as returned by the email subscription lookup for this customer.
        renewal_amount: Fixed-format class — the renewal amount being collected, in US dollars, a positive number with 2
            decimal places; a value with more decimals is rounded half up to the cent before it is booked.
        renewed_seats: Fixed-format class — the number of licensed seats the subscription carries for the new term, every
            one of them billed on the line, an integer of at least 1.
        renewal_product: Enum class — the product the subscription carries for the new term, written as the official
            product name: Harborline Mail Starter, Harborline Mail Plus, Harborline Mail Pro, Microsoft 365 Business
            Basic, Microsoft 365 Business Standard or Microsoft 365 Business Premium.

    Returns:
        A one-line confirmation string. On success it reads "Paid renewal of subscription <email_plan_id>: line
        <email_charge_id> order <order_ref> for <amount> USD (<seats> seats) charged to card; new term <term_start> to
        <term_end>." where <email_charge_id> is the reference of the new billing line, <order_ref> the Harborline order
        number (HL- followed by 8 digits), <amount> the booked amount with two decimals, <seats> the renewed seat count
        and the dates are YYYY-MM-DD. A string starting with "Error:" means nothing was booked (unknown subscription, a
        non-positive amount, fewer than 1 seat or an unknown product name).
    """
    rows = ctx.find("email_holdings", email_plan_id=email_plan_id)
    if not rows:
        return f"Error: no email subscription {email_plan_id}."
    amount = _Calc.cents_half_up(renewal_amount)
    seats = int(renewed_seats)
    if amount <= 0 or seats < 1:
        return "Error: the renewal amount must be positive and the renewed seats at least 1."
    product = str(renewal_product or "").strip()
    if product not in _PRODUCTS:
        return f"Error: unknown email product {renewal_product}."
    sub = rows[0]
    plan = sub.get("billing_plan")
    start, end, line_end = _Calc.renewal_span(sub.get("term_end_date"), plan)
    kind = "monthly_instalment" if plan == "annual_monthly_billing" else "renewal"
    today = ctx.now()[:10]
    rid = ctx.make_id("ech_", email_plan_id, amount, seats, start)
    order = _Calc.order_number(rid)
    ctx.create("email_charges", rid, email_charge_id=rid, email_plan_id=email_plan_id,
               customer_id=sub.get("customer_id"), event_type="email_renewal_charge", charge_type=kind,
               amount=amount, seats=seats, target_variant="none", period_start=start,
               period_end=line_end, charge_date=today, order_ref=order, payment_method="card",
               original_email_charge_id=None, refund_destination="none")
    ctx.update("email_holdings", email_plan_id, term_start_date=start, term_end_date=end, seat_count=seats,
               scheduled_seat_count=0, variant_name=product, scheduled_variant="none")
    return (f"Paid renewal of subscription {email_plan_id}: line {rid} order {order} for {amount:.2f} USD "
            f"({seats} seats) charged to card; new term {start} to {end}.")


@tool(owner="user", rw="write")
def convert_mail_to_annual_cfde09f1(ctx: ToolContext, email_plan_id: str, conversion_amount: float,
                                    annual_start_date: str) -> str:
    """The account holder pays, personally at Harborline's secure checkout with PayPal, the move of their email
    subscription from the monthly plan to the annual prepaid plan. One call books one renewal billing line for a
    12-month term, covering and billing every licensed seat, paid by PayPal, and switches the subscription to the
    annual prepaid plan with its term running for 12 calendar months (falling back to the month's last day where that
    day does not exist) from the annual start date the agent gives; any seat count scheduled for the next renewal is
    cleared and the seat count does not change. The holder sees the subscription on the annual prepaid plan with the new term dates and the line in
    their email billing history.

    Args:
        email_plan_id: Id class — the reference number of the holder's email subscription being moved to the annual
            prepaid plan, as returned by the email subscription lookup and read out to the holder by the agent.
        conversion_amount: Fixed-format class — the amount to bill for the new annual term, in US dollars, a positive
            number with 2 decimal places; a value with more decimals is rounded half up to the cent before it is booked.
        annual_start_date: Fixed-format class — the date the new 12-month annual term starts, as YYYY-MM-DD; the line
            covers that date to the day before the same date 12 months later.

    Returns:
        A one-line confirmation string. On success it reads "Converted subscription <email_plan_id> to annual prepaid:
        line <email_charge_id> order <order_ref> for <amount> USD (<seats> seats) paid by PayPal; term <term_start> to
        <term_end>." where <email_charge_id> is the reference of the new billing line, <order_ref> the Harborline order
        number (HL- followed by 8 digits), <amount> the booked amount with two decimals, <seats> the licensed seat
        count and the dates are YYYY-MM-DD. A string starting with "Error:" means nothing was booked (unknown
        subscription, a non-positive amount or a start date not in YYYY-MM-DD form).
    """
    rows = ctx.find("email_holdings", email_plan_id=email_plan_id)
    if not rows:
        return f"Error: no email subscription {email_plan_id}."
    amount = _Calc.cents_half_up(conversion_amount)
    if amount <= 0:
        return "Error: the conversion amount must be positive."
    sub = rows[0]
    seats = int(sub.get("seat_count") or 0)
    today = ctx.now()[:10]
    start = str(annual_start_date or "").strip()
    parts = start.split("-")
    if len(start) != 10 or len(parts) != 3 or not all(x.isdigit() for x in parts) or not (
            1 <= int(parts[1]) <= 12 and 1 <= int(parts[2]) <= _Calc._month_len(int(parts[0]), int(parts[1]))):
        return "Error: the annual start date must be a calendar date in YYYY-MM-DD form."
    end = _Calc.add_months(start, 12)
    rid = ctx.make_id("ech_", email_plan_id, amount, "annual_prepaid", start)
    order = _Calc.order_number(rid)
    ctx.create("email_charges", rid, email_charge_id=rid, email_plan_id=email_plan_id,
               customer_id=sub.get("customer_id"), event_type="email_renewal_charge", charge_type="renewal",
               amount=amount, seats=seats, target_variant="none", period_start=start,
               period_end=_Calc.minus_one_day(end), charge_date=today, order_ref=order, payment_method="paypal",
               original_email_charge_id=None, refund_destination="none")
    ctx.update("email_holdings", email_plan_id, billing_plan="annual_prepaid", term_start_date=start,
               term_end_date=end, scheduled_seat_count=0)
    return (f"Converted subscription {email_plan_id} to annual prepaid: line {rid} order {order} for {amount:.2f} USD "
            f"({seats} seats) paid by PayPal; term {start} to {end}.")

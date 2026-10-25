"""Hidden task tools of difficulty hosting_plans_and_billing (env_0076, Harborline Hosting & Domains).

Each tool performs one atomic hosting write (with the same-category effects its event declares) and is
reached only through the extended policy that names it as target_tool.
"""

from decimal import Decimal, ROUND_HALF_UP

from erlbench import ToolContext, tool


class _HostingCalc:
    """Pure helpers for the tools below (no clock, no randomness): cent rounding and calendar dates."""

    _MONTH_DAYS = (31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31)

    @staticmethod
    def cents(value) -> float:
        """Round a USD amount half up to the cent."""
        return float(Decimal(str(value)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP))

    @staticmethod
    def leap(year: int) -> bool:
        return year % 4 == 0 and (year % 100 != 0 or year % 400 == 0)

    @staticmethod
    def add_months(date_text: str, months: int) -> str:
        """YYYY-MM-DD plus whole calendar months, falling back to the month's last day."""
        year, month, day = (int(part) for part in str(date_text)[:10].split("-"))
        index = (month - 1) + int(months)
        year, month = year + index // 12, index % 12 + 1
        last = _HostingCalc._MONTH_DAYS[month - 1] + (1 if month == 2 and _HostingCalc.leap(year) else 0)
        return f"{year:04d}-{month:02d}-{min(day, last):02d}"

    @staticmethod
    def order_number(row_id: str) -> str:
        """A Harborline order number (HL- followed by 8 digits) derived from a deterministic row id."""
        digits = int(row_id.split("_")[-1], 16) % 1000000
        return f"HL-02{digits:06d}"


_PAYMENT_METHODS = {"card": "card", "paypal": "paypal"}
_PLAN_TIERS = ("Harborline Starter", "Harborline Plus", "Harborline Pro", "Harborline Business",
               "Harborline Cloud 4", "Harborline Cloud 8")


@tool(owner="user", rw="write")
def bill_overdue_hosting_renewal_c53aa4e7(ctx: ToolContext, hosting_id: str, amount: float, term_months: int,
                                          payment_method: str, hosting_request_id: str) -> str:
    """The customer pays, at Harborline's checkout, the renewal of their own hosting plan whose paid term has already
    ended, and the plan's next term starts.

    The customer completes the payment of the renewal amount with the payment method they choose, and it is recorded
    on the plan's billing history as a manual renewal line covering the new term. The plan's next term begins on the day
    the previous term ended and runs for the stated number of months: the plan's current term dates move to the new
    term, its billing term becomes the stated length, and the introductory-term flag is cleared. When a scheduled
    term change request is named, that request is marked as applied. On success the customer can see the new
    renewal line, with its own Harborline order number, and the plan's new term end date.

    Args:
        hosting_id: Id class — reference number of the customer's hosting plan being renewed, as given to the
            customer by the support agent from the hosting plan lookup.
        amount: Fixed-format class — renewal amount paid, in USD, positive, 2 decimal places, rounded half up to
            the cent.
        term_months: Fixed-format class — length of the new term in calendar months, an integer that is one of
            the offered billing terms 1, 12, 24 or 36.
        payment_method: Enum class — how the customer pays this renewal: card when it is charged to the customer's
            payment card; paypal when it is paid through the customer's PayPal account.
        hosting_request_id: Id class — reference number of the plan's scheduled term change request taken up by
            this renewal, as given to the customer by the support agent from the change request lookup; an empty
            string when the plan has no scheduled term change request.

    Returns:
        A dictionary rendered as text with keys: status ("renewed" on success), hosting_charge_id (reference of
        the new renewal line), order_ref (Harborline order number of the renewal, HL- followed by 8 digits),
        amount (USD charged, 2 decimal places), term_months (months of the new term, integer), term_start_date and
        term_end_date (new term dates, YYYY-MM-DD), payment_method (card or paypal) and hosting_request_id (the
        change request marked applied, or an empty string).
    """
    method = _PAYMENT_METHODS.get(str(payment_method), "")
    if not method:
        return "Error: payment_method must be card or paypal."
    months = int(term_months)
    if months not in (1, 12, 24, 36):
        return "Error: term_months must be 1, 12, 24 or 36."
    plans = ctx.find("hosting_holdings", hosting_id=hosting_id)
    if not plans:
        return f"Error: no hosting plan {hosting_id}."
    plan = plans[0]
    billed = _HostingCalc.cents(amount)
    if billed <= 0:
        return "Error: amount must be a positive USD amount."
    if hosting_request_id and not ctx.find("hosting_change_requests", hosting_request_id=hosting_request_id,
                                           hosting_id=hosting_id, request_type="term_change",
                                           request_status="scheduled"):
        return f"Error: {hosting_request_id} is not a scheduled term change request of plan {hosting_id}."
    start = str(plan.get("term_end_date"))
    end = _HostingCalc.add_months(start, months)
    rid = ctx.make_id("hch_", hosting_id, billed, months, method, hosting_request_id)
    order_ref = _HostingCalc.order_number(rid)
    ctx.create("hosting_charges", rid, hosting_charge_id=rid, hosting_id=hosting_id,
               customer_id=plan.get("customer_id"), event_type="hosting_renewal_charge", charge_type="renewal",
               amount=billed, term_months=months, target_variant="none", period_start=start, period_end=end,
               charge_date=ctx.now()[:10], order_ref=order_ref, payment_method=method,
               original_hosting_charge_id=None, refund_kind="none", refund_destination="none", uptime_month="")
    ctx.update("hosting_holdings", hosting_id, term_start_date=start, term_end_date=end,
               billing_term_months=months, first_term=False)
    if hosting_request_id:
        ctx.update("hosting_change_requests", hosting_request_id, request_status="applied")
    return str({"status": "renewed", "hosting_charge_id": rid, "order_ref": order_ref, "amount": billed,
                "term_months": months, "term_start_date": start, "term_end_date": end,
                "payment_method": method, "hosting_request_id": hosting_request_id})


@tool(owner="user", rw="write")
def buy_hosting_upgrade_8645a072(ctx: ToolContext, hosting_id: str, target_variant: str, amount: float,
                                 payment_method: str) -> str:
    """The customer buys a mid-term upgrade of their own hosting plan to a higher tier and pays for it.

    The customer pays the upgrade amount with the payment method they choose; a billing line for the upgrade is
    recorded on the plan, covering today through the plan's current term end date, and the plan moves to the new
    tier at once. The plan's term dates, billing term and introductory-term flag are not changed. On success the
    customer sees the upgrade line with its own Harborline order number and the plan's new tier.

    Args:
        hosting_id: Id class — reference number of the customer's hosting plan being upgraded, as given to the
            customer by the support agent from the hosting plan lookup.
        target_variant: Enum class — the tier the plan moves to: Harborline Starter for the entry shared tier;
            Harborline Plus for the second shared tier; Harborline Pro for the third shared tier; Harborline
            Business for the top shared tier; Harborline Cloud 4 for the smaller cloud tier; Harborline Cloud 8 for
            the larger cloud tier.
        amount: Fixed-format class — upgrade amount paid, in USD, positive, 2 decimal places, rounded half up to the
            cent.
        payment_method: Enum class — how the customer pays the upgrade: card when it is charged to the customer's
            payment card; paypal when it is paid through the customer's PayPal account.

    Returns:
        A dictionary rendered as text with keys: status ("upgraded" on success), hosting_charge_id (reference of
        the upgrade line), order_ref (Harborline order number of the upgrade, HL- followed by 8 digits), amount
        (USD paid, 2 decimal places), variant_name (the plan's new tier), period_start and period_end (dates the
        line covers, YYYY-MM-DD) and payment_method (card or paypal).
    """
    method = _PAYMENT_METHODS.get(str(payment_method), "")
    if not method:
        return "Error: payment_method must be card or paypal."
    plans = ctx.find("hosting_holdings", hosting_id=hosting_id)
    if not plans:
        return f"Error: no hosting plan {hosting_id}."
    plan = plans[0]
    paid = _HostingCalc.cents(amount)
    if paid <= 0:
        return "Error: amount must be a positive USD amount."
    if target_variant not in _PLAN_TIERS:
        return "Error: target_variant must be one of the official hosting tier names."
    today = ctx.now()[:10]
    rid = ctx.make_id("hch_", hosting_id, target_variant, paid, method, today)
    order_ref = _HostingCalc.order_number(rid)
    ctx.create("hosting_charges", rid, hosting_charge_id=rid, hosting_id=hosting_id,
               customer_id=plan.get("customer_id"), event_type="hosting_upgrade_charge",
               charge_type="upgrade_proration", amount=paid, term_months=0, target_variant=target_variant,
               period_start=today, period_end=str(plan.get("term_end_date")), charge_date=today,
               order_ref=order_ref, payment_method=method, original_hosting_charge_id=None,
               refund_kind="none", refund_destination="none", uptime_month="")
    ctx.update("hosting_holdings", hosting_id, variant_name=target_variant)
    return str({"status": "upgraded", "hosting_charge_id": rid, "order_ref": order_ref, "amount": paid,
                "variant_name": target_variant, "period_start": today,
                "period_end": str(plan.get("term_end_date")), "payment_method": method})


@tool(owner="agent", rw="write")
def refund_hosting_auto_renewal_84b3efde(ctx: ToolContext, hosting_id: str, original_hosting_charge_id: str,
                                         amount: float) -> str:
    """Refund an auto-renew charge of a hosting plan and roll the plan back to its earlier paid term.

    Harborline support returns the stated refund amount to the card or PayPal account that paid the auto-renew charge
    and records it on the plan's billing history as an auto-renew refund line pointing at the refunded charge; a
    charge paid from account credit is not refunded through this tool. The plan's
    current term dates and billing term length return to the earlier term that the refunded renewal had replaced and
    auto-renew is switched off;
    a plan whose cancellation was scheduled and whose restored term end date has already passed is closed on that
    date. On success the customer can see the refund line and the plan's restored term end date.

    Args:
        hosting_id: Id class — reference number of the hosting plan whose auto-renew charge is refunded, as returned
            by the hosting plan lookup for this customer.
        original_hosting_charge_id: Id class — reference number of the auto-renew billing line being refunded, paid by
            card or through PayPal, as returned by the hosting billing lookup for this plan.
        amount: Fixed-format class — refund amount returned to the customer, in USD, positive, 2 decimal places,
            rounded half up to the cent; it is recorded on the billing history as a negative line.

    Returns:
        A dictionary rendered as text with keys: status ("refunded" on success), hosting_charge_id (reference of the
        refund line), original_hosting_charge_id (the refunded auto-renew line), amount (USD returned, 2 decimal
        places, positive), refund_destination (original_payment_method), term_start_date and term_end_date (the
        restored term dates, YYYY-MM-DD), billing_term_months (the restored term length in months, integer) and
        auto_renew (false).
    """
    plans = ctx.find("hosting_holdings", hosting_id=hosting_id)
    lines = ctx.find("hosting_charges", hosting_charge_id=original_hosting_charge_id)
    if not plans or not lines:
        return f"Error: no hosting plan {hosting_id} or billing line {original_hosting_charge_id}."
    plan, line = plans[0], lines[0]
    if (line.get("hosting_id") != hosting_id or line.get("event_type") != "hosting_renewal_charge"
            or line.get("charge_type") != "auto_renew"):
        return f"Error: {original_hosting_charge_id} is not an auto-renew billing line of plan {hosting_id}."
    if line.get("payment_method") not in ("card", "paypal"):
        return f"Error: {original_hosting_charge_id} was not paid by card or PayPal; this tool returns refunds to a card or PayPal only."
    returned = _HostingCalc.cents(amount)
    if returned <= 0:
        return "Error: amount must be a positive USD amount."
    restored_end = str(line.get("period_start"))
    earlier = [row for row in ctx.find("hosting_charges", hosting_id=hosting_id, period_end=restored_end)
               if row.get("event_type") in ("hosting_term_charge", "hosting_renewal_charge")
               and row.get("charge_type") in ("initial_term", "renewal", "auto_renew")]
    restored_start = str(earlier[0].get("period_start")) if earlier else str(plan.get("term_start_date"))
    restored_months = int(earlier[0].get("term_months")) if earlier else int(plan.get("billing_term_months"))
    rid = ctx.make_id("hch_", hosting_id, original_hosting_charge_id, returned)
    today = ctx.now()[:10]
    ctx.create("hosting_charges", rid, hosting_charge_id=rid, hosting_id=hosting_id,
               customer_id=plan.get("customer_id"), event_type="hosting_refund", charge_type=line.get("charge_type"),
               amount=-returned, term_months=0, target_variant="none", period_start="", period_end="",
               charge_date=today, order_ref="", payment_method="none",
               original_hosting_charge_id=original_hosting_charge_id, refund_kind="auto_renew_refund",
               refund_destination="original_payment_method", uptime_month="")
    ctx.update("hosting_holdings", hosting_id, term_start_date=restored_start, term_end_date=restored_end,
               billing_term_months=restored_months, auto_renew=False)
    if plan.get("status") == "cancel_pending" and restored_end <= today:
        ctx.update("hosting_holdings", hosting_id, status="cancelled", closed_date=restored_end)
    return str({"status": "refunded", "hosting_charge_id": rid, "original_hosting_charge_id": original_hosting_charge_id,
                "amount": returned, "refund_destination": "original_payment_method",
                "term_start_date": restored_start, "term_end_date": restored_end,
                "billing_term_months": restored_months, "auto_renew": False})


@tool(owner="user", rw="write")
def pay_hosting_renewal_early_31233d6b(ctx: ToolContext, hosting_id: str, amount: float, term_months: int,
                                       payment_method: str) -> str:
    """The customer pays, at Harborline's checkout, the renewal of their own hosting plan while its current term is
    still running.

    The customer pays the renewal amount with the payment method they choose; a manual renewal line covering the next
    term is recorded on the plan. The next term begins on the current term end date and runs for the stated number
    of months: the plan's term dates move to that next term, its billing term becomes the stated length and the
    introductory-term flag is cleared; the auto-renew setting is left as it is. On success the customer sees the
    renewal line with its own Harborline order number and the plan's new term end date.

    Args:
        hosting_id: Id class — reference number of the customer's hosting plan being renewed, as given to the
            customer by the support agent from the hosting plan lookup.
        amount: Fixed-format class — renewal amount paid, in USD, positive, 2 decimal places, rounded half up to the
            cent.
        term_months: Fixed-format class — length of the next term in calendar months, an integer that is one of the
            offered billing terms 1, 12, 24 or 36.
        payment_method: Enum class — how the customer pays the renewal: card when it is charged to the customer's
            payment card; paypal when it is paid through the customer's PayPal account.

    Returns:
        A dictionary rendered as text with keys: status ("renewed" on success), hosting_charge_id (reference of the
        renewal line), order_ref (Harborline order number, HL- followed by 8 digits), amount (USD paid, 2 decimal
        places), term_months (months of the next term, integer), term_start_date and term_end_date (the next term's
        dates, YYYY-MM-DD) and payment_method (card or paypal).
    """
    method = _PAYMENT_METHODS.get(str(payment_method), "")
    if not method:
        return "Error: payment_method must be card or paypal."
    months = int(term_months)
    if months not in (1, 12, 24, 36):
        return "Error: term_months must be 1, 12, 24 or 36."
    plans = ctx.find("hosting_holdings", hosting_id=hosting_id)
    if not plans:
        return f"Error: no hosting plan {hosting_id}."
    plan = plans[0]
    paid = _HostingCalc.cents(amount)
    if paid <= 0:
        return "Error: amount must be a positive USD amount."
    start = str(plan.get("term_end_date"))
    end = _HostingCalc.add_months(start, months)
    rid = ctx.make_id("hch_", hosting_id, paid, months, method, start)
    order_ref = _HostingCalc.order_number(rid)
    ctx.create("hosting_charges", rid, hosting_charge_id=rid, hosting_id=hosting_id,
               customer_id=plan.get("customer_id"), event_type="hosting_renewal_charge", charge_type="renewal",
               amount=paid, term_months=months, target_variant="none", period_start=start, period_end=end,
               charge_date=ctx.now()[:10], order_ref=order_ref, payment_method=method,
               original_hosting_charge_id=None, refund_kind="none", refund_destination="none", uptime_month="")
    ctx.update("hosting_holdings", hosting_id, term_start_date=start, term_end_date=end,
               billing_term_months=months, first_term=False)
    return str({"status": "renewed", "hosting_charge_id": rid, "order_ref": order_ref, "amount": paid,
                "term_months": months, "term_start_date": start, "term_end_date": end, "payment_method": method})

"""Hidden task tools of the lab_orders_and_collection_fees difficulty (Larkspur Health lab orders).

Each tool performs one atomic business write with the values the agent (or the patient) supplies; no tool
judges eligibility, prerequisites or amounts.
"""

from decimal import Decimal, ROUND_HALF_UP

from erlbench import ToolContext, tool


class _LabMoney:
    """Money helpers shared by the lab tools."""

    @staticmethod
    def half_up(value) -> float:
        """Round a dollar amount half up to the cent with exact decimal arithmetic."""
        return float(Decimal(str(value)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP))

    @staticmethod
    def two_places(value) -> bool:
        """True when the amount carries no more than two decimal places."""
        return Decimal(str(value)) == Decimal(str(value)).quantize(Decimal("0.01"))


@tool(owner="agent", rw="write")
def correct_member_rate_order_9be954a8(ctx: ToolContext, lab_order_id: str, membership_id: str,
                                       original_charge_id: str, refund_amount: float) -> str:
    """Correct a lab order that was billed at the list price although the patient held a membership that should
    have priced it. In one action the order is moved to the member price path with the named membership recorded
    on it, and the overcharge on the order's panel charge line is returned to the card on file as one refund line
    of reason billing_error pointing to that panel line. When the refund amount is 0.00 the order is still moved and
    no refund line is written. The patient sees the order on the member price path and, when the amount is above
    0.00, a negative refund line on the order's billing history.

    Args:
        lab_order_id: Id class — the reference number of the lab order being corrected, as returned by the lab
            order lookup for this patient.
        membership_id: Id class — the reference number of the patient's membership to record on the order, as
            returned by the membership lookup for this patient.
        original_charge_id: Id class — the reference number of the order's panel charge line being refunded, as
            returned by the lab charge lookup for this order.
        refund_amount: Fixed-format class — the refund in US dollars as a number of at least 0.00 with 2
            decimal places (cents), rounded half up to the cent before it is passed; 0.00 when nothing is refunded.

    Returns:
        A confirmation sentence naming the order, the payment path now recorded (member_rate), the membership
        reference recorded, and either the refund line reference with the refunded amount in dollars (two
        decimals) or the statement that no refund line was written. A string starting with "Error:" means nothing
        was changed because a reference was unknown or the amount was not in the stated format.
    """
    orders = ctx.find("lab_orders", lab_order_id=lab_order_id)
    if not orders:
        return f"Error: no lab order {lab_order_id}."
    if not ctx.find("membership_holdings", membership_id=membership_id):
        return f"Error: no membership {membership_id}."
    lines = ctx.find("lab_charges", lab_charge_id=original_charge_id, lab_order_id=lab_order_id,
                     event_type="lab_panel_charged")
    if not lines:
        return f"Error: {original_charge_id} is not a panel charge line of order {lab_order_id}."
    if float(refund_amount) < 0 or not _LabMoney.two_places(refund_amount):
        return "Error: refund_amount must be a non-negative dollar amount with at most two decimals."
    amount = _LabMoney.half_up(refund_amount)
    ctx.update("lab_orders", lab_order_id, payment_path="member_rate", membership_id=membership_id)
    if amount <= 0:
        return (f"Order {lab_order_id} now on payment path member_rate with membership {membership_id}; "
                "no refund line written (0.00).")
    rid = ctx.make_id("lch_", lab_order_id, membership_id, original_charge_id, amount)
    ctx.create("lab_charges", rid, lab_charge_id=rid, lab_order_id=lab_order_id,
               customer_id=orders[0]["customer_id"], event_type="lab_charge_refunded", amount=-amount,
               charge_date=ctx.now()[:10], pricing_basis="refund", original_charge_id=original_charge_id,
               refund_reason="billing_error")
    return (f"Order {lab_order_id} now on payment path member_rate with membership {membership_id}; "
            f"refund line {rid} of {amount:.2f} USD (billing_error) posted against {original_charge_id}.")


@tool(owner="user", rw="write")
def switch_order_to_home_kit_d2ed4950(ctx: ToolContext, lab_order_id: str, membership_id: str,
                                      kit_charge: float) -> str:
    """The patient switches her own lab order from a patient service center draw to an at-home collection kit and
    confirms the kit charge quoted to her. The order's collection method becomes at_home_kit and, when the charge
    is above 0.00, one kit fee line of that amount is posted on today's date to the card on file; nothing else on
    the order changes. The patient sees the order's new collection method and the new kit line on her billing
    history.

    Args:
        lab_order_id: Id class — the reference number of the patient's lab order, as the agent read it from the
            lab order lookup and gives it to the patient.
        membership_id: Id class — the reference number of the membership recorded on the lab order, as the agent
            read it from the lab order lookup and gives it to the patient; "" when the order records no membership.
        kit_charge: Fixed-format class — the kit charge in US dollars as a number of at least 0.00 with 2
            decimal places (cents), rounded half up to the cent before it is passed; 0.00 when nothing is charged.

    Returns:
        A confirmation sentence naming the order and its collection method now recorded (at_home_kit), and either
        the kit line reference with the charged amount in dollars (two decimals) or the statement that no line was
        written. A string starting with "Error:" means nothing was changed because the order was unknown or the
        amount was not in the stated format.
    """
    orders = ctx.find("lab_orders", lab_order_id=lab_order_id)
    if not orders:
        return f"Error: no lab order {lab_order_id}."
    if membership_id and not ctx.find("membership_holdings", membership_id=membership_id):
        return f"Error: no membership {membership_id}."
    if float(kit_charge) < 0 or not _LabMoney.two_places(kit_charge):
        return "Error: kit_charge must be a non-negative dollar amount with at most two decimals."
    amount = _LabMoney.half_up(kit_charge)
    ctx.update("lab_orders", lab_order_id, collection_method="at_home_kit")
    if amount <= 0:
        return f"Order {lab_order_id} now collected by at_home_kit; no kit line written (0.00)."
    rid = ctx.make_id("lch_", lab_order_id, membership_id, "kit", amount)
    ctx.create("lab_charges", rid, lab_charge_id=rid, lab_order_id=lab_order_id,
               customer_id=orders[0]["customer_id"], event_type="lab_collection_fee_charged", amount=amount,
               charge_date=ctx.now()[:10], pricing_basis="kit_fee", original_charge_id=None, refund_reason="none")
    return f"Order {lab_order_id} now collected by at_home_kit; kit line {rid} of {amount:.2f} USD posted."


class _LabCalendar:
    """Calendar arithmetic on YYYY-MM-DD dates with plain ordinal-day numbers."""

    @staticmethod
    def to_ordinal(day: str) -> int:
        y, m, d = (int(p) for p in str(day)[:10].split("-"))
        y -= m <= 2
        era = (y if y >= 0 else y - 399) // 400
        yoe = y - era * 400
        doy = (153 * (m + (-3 if m > 2 else 9)) + 2) // 5 + d - 1
        doe = yoe * 365 + yoe // 4 - yoe // 100 + doy
        return era * 146097 + doe - 719468

    @staticmethod
    def from_ordinal(n: int) -> str:
        n += 719468
        era = (n if n >= 0 else n - 146096) // 146097
        doe = n - era * 146097
        yoe = (doe - doe // 1460 + doe // 36524 - doe // 146096) // 365
        y = yoe + era * 400
        doy = doe - (365 * yoe + yoe // 4 - yoe // 100)
        mp = (5 * doy + 2) // 153
        d = doy - (153 * mp + 2) // 5 + 1
        m = mp + (3 if mp < 10 else -9)
        return f"{y + (m <= 2):04d}-{m:02d}-{d:02d}"


@tool(owner="agent", rw="write")
def reissue_requisition_d14f4a64(ctx: ToolContext, lab_order_id: str, validity_days: int) -> str:
    """Reissue the requisition of a lab order that has not been collected, so the patient has a new period in which
    to give the specimen. The order's requisition expiry date becomes today's date plus the stated number of
    calendar days and the order's reissue count rises by one; no charge or refund is written. The patient sees the
    new last day for collection on the order.

    Args:
        lab_order_id: Id class — the reference number of the lab order whose requisition is reissued, as returned
            by the lab order lookup for this patient.
        validity_days: Fixed-format class — the reissued validity as a whole number of calendar days (integer
            precision, at least 1) counted from today's date; the new last day for collection is today plus this
            many days.

    Returns:
        A confirmation sentence naming the order, its new requisition expiry date (YYYY-MM-DD) and its reissue
        count after the reissue (an integer). A string starting with "Error:" means nothing was changed because the
        order was unknown or the number of days was not a positive whole number.
    """
    orders = ctx.find("lab_orders", lab_order_id=lab_order_id)
    if not orders:
        return f"Error: no lab order {lab_order_id}."
    if int(validity_days) != validity_days or int(validity_days) < 1:
        return "Error: validity_days must be a positive whole number of calendar days."
    today = ctx.now()[:10]
    new_expiry = _LabCalendar.from_ordinal(_LabCalendar.to_ordinal(today) + int(validity_days))
    count = int(orders[0].get("reissue_count") or 0) + 1
    ctx.update("lab_orders", lab_order_id, requisition_expiry_date=new_expiry, reissue_count=count)
    return f"Requisition of order {lab_order_id} reissued: new expiry date {new_expiry}, reissue count {count}."


@tool(owner="user", rw="write")
def switch_order_to_home_phlebotomy_06c13f87(ctx: ToolContext, lab_order_id: str, membership_id: str,
                                             home_visit_charge: float) -> str:
    """The patient switches his or her own lab order from a patient service center draw to a mobile phlebotomist
    home visit and confirms the home-visit charge quoted. The order's collection method becomes mobile_phlebotomy
    and, when the charge is above 0.00, one mobile phlebotomy fee line of that amount is posted on today's date to the
    card on file; nothing else on the order changes. The patient sees the new collection method and the new line on
    the billing history.

    Args:
        lab_order_id: Id class — the reference number of the patient's lab order, as the agent read it from the
            lab order lookup and gives it to the patient.
        membership_id: Id class — the reference number of the patient's membership, as the agent read it from the
            membership lookup and gives it to the patient; "" when the patient holds no membership.
        home_visit_charge: Fixed-format class — the home-visit charge in US dollars as a number of at least 0.00 with 2
            decimal places (cents), rounded half up to the cent before it is passed; 0.00 when nothing is charged.

    Returns:
        A confirmation sentence naming the order and its collection method now recorded (mobile_phlebotomy), and
        either the new line reference with the charged amount in dollars (two decimals) or the statement that no
        line was written. A string starting with "Error:" means nothing was changed because the order was unknown or
        the amount was not in the stated format.
    """
    orders = ctx.find("lab_orders", lab_order_id=lab_order_id)
    if not orders:
        return f"Error: no lab order {lab_order_id}."
    if membership_id and not ctx.find("membership_holdings", membership_id=membership_id):
        return f"Error: no membership {membership_id}."
    if float(home_visit_charge) < 0 or not _LabMoney.two_places(home_visit_charge):
        return "Error: home_visit_charge must be a non-negative dollar amount with at most two decimals."
    amount = _LabMoney.half_up(home_visit_charge)
    ctx.update("lab_orders", lab_order_id, collection_method="mobile_phlebotomy")
    if amount <= 0:
        return f"Order {lab_order_id} now collected by mobile_phlebotomy; no line written (0.00)."
    rid = ctx.make_id("lch_", lab_order_id, membership_id, "mobile", amount)
    ctx.create("lab_charges", rid, lab_charge_id=rid, lab_order_id=lab_order_id,
               customer_id=orders[0]["customer_id"], event_type="lab_collection_fee_charged", amount=amount,
               charge_date=ctx.now()[:10], pricing_basis="mobile_phlebotomy_fee", original_charge_id=None,
               refund_reason="none")
    return f"Order {lab_order_id} now collected by mobile_phlebotomy; line {rid} of {amount:.2f} USD posted."

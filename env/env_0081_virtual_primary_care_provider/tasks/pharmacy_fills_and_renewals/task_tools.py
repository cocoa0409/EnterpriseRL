"""Hidden task tools of the pharmacy_fills_and_renewals difficulty (category rx, Larkspur Pharmacy).

Each tool performs one atomic write on the pharmacy billing ledger and is reached through the
unlock/call meta-tools. No tool checks a policy condition; the agent decides from the published
policy and the records before calling.
"""

from decimal import Decimal, ROUND_HALF_UP

from erlbench import ToolContext, tool


class _Cents:
    """Exact money handling shared by the tools (half-up to the cent)."""

    @staticmethod
    def parse(value):
        """Return the amount as a Decimal rounded half up to the cent, or None when it is not a positive amount
        given to at most two decimal places."""
        try:
            raw = Decimal(str(value))
        except Exception:
            return None
        cents = raw.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        if cents != raw or cents <= Decimal("0"):
            return None
        return cents


@tool(owner="agent", rw="write")
def refund_rx_shipping_overcharge_36ef431c(ctx: ToolContext, original_charge_id: str, amount: float) -> str:
    """Refund part of a Larkspur Pharmacy shipping charge that was posted above what the shipment should have
    cost. The agent names the shipping charge line and the amount to give back; one billing-error refund line
    is booked against that shipping line, on the same prescription and dispensed fill, dated today, and the
    patient's card on file is credited that amount. Succeeds only for an existing shipping charge line; the
    refund then shows on the prescription's pharmacy billing lines with the shipping line as its original line.

    Args:
        original_charge_id: Id class — the reference number of the shipping charge line being corrected, exactly as
            shown on the pharmacy billing lines already looked up for the prescription.
        amount: Fixed-format class — the amount refunded, a positive USD amount given to 2 decimal places
            (cents, rounded half up before the call); it is booked as a negative amount on the refund line.

    Returns:
        A dict receipt: refund_line_id (str, reference number of the new refund line), original_charge_id (str,
        the shipping line refunded), rx_id (str, prescription), rx_fill_id (str, dispensed fill), amount (float,
        the negative USD amount booked, 2 decimal places), refund_reason (str, always billing_error),
        charge_date (str, YYYY-MM-DD posting date) and status (str, "refunded" on success). A string starting
        with "Error:" means nothing was booked.
    """
    cents = _Cents.parse(amount)
    if cents is None:
        return "Error: amount must be a positive USD amount with at most 2 decimal places."
    rows = ctx.find("rx_charges", rx_charge_id=original_charge_id)
    if not rows or rows[0].get("event_type") != "rx_shipping_charged":
        return f"Error: {original_charge_id} is not a shipping charge line."
    line = rows[0]
    value = -float(cents)
    rid = ctx.make_id("rxr_", original_charge_id, amount)
    day = ctx.now()[:10]
    ctx.create("rx_charges", rid, rx_charge_id=rid, rx_id=line["rx_id"], customer_id=line["customer_id"],
               event_type="rx_charge_refunded", amount=value, charge_date=day, rx_fill_id=line["rx_fill_id"],
               price_basis="refund", pbm_patient_pay=0.0, original_charge_id=original_charge_id,
               refund_reason="billing_error")
    return str({"refund_line_id": rid, "original_charge_id": original_charge_id, "rx_id": line["rx_id"],
                "rx_fill_id": line["rx_fill_id"], "amount": value, "refund_reason": "billing_error",
                "charge_date": day, "status": "refunded"})


@tool(owner="user", rw="write")
def pay_rx_shipment_balance_955e5801(ctx: ToolContext, rx_id: str, rx_fill_id: str, membership_id: str,
                                     coverage_id: str, amount: float) -> str:
    """The patient pays, with a card they provide themselves, the balance still owed on one Larkspur Pharmacy
    shipment whose medication was charged less than it should have been. One fill charge line on the cash
    member price basis is posted against the dispensed fill of the named prescription for the amount paid,
    dated today, and the payment shows on the prescription's pharmacy billing lines. Succeeds only when the
    fill is a dispensed fill of that prescription and every other reference names a record of the same patient.

    Args:
        rx_id: Id class — the reference number of the prescription the shipment belongs to, exactly as the agent
            read it from the patient's prescription records and gave it to the patient.
        rx_fill_id: Id class — the reference number of the dispensed fill the balance belongs to, exactly as the
            agent read it from the prescription's fill records and gave it to the patient.
        membership_id: Id class — the reference number of the patient's Larkspur membership record whose status
            the member price rests on, as read from the patient's membership records; empty when the patient
            holds no membership.
        coverage_id: Id class — the reference number of the insurance coverage the patient holds on file, as read
            from the patient's coverage records; empty when the patient holds no coverage.
        amount: Fixed-format class — the balance the patient pays, a positive USD amount given to 2 decimal
            places (cents, rounded half up), as the agent quoted it.

    Returns:
        A dict receipt: charge_line_id (str, reference number of the new fill charge line), rx_id (str,
        prescription), rx_fill_id (str, dispensed fill), amount (float, USD paid, 2 decimal places),
        price_basis (str, always cash_member_price), charge_date (str, YYYY-MM-DD) and status (str, "paid" on
        success). A string starting with "Error:" means nothing was posted.
    """
    cents = _Cents.parse(amount)
    if cents is None:
        return "Error: amount must be a positive USD amount with at most 2 decimal places."
    fills = ctx.find("rx_fills", rx_fill_id=rx_fill_id)
    if not fills or fills[0].get("event_type") != "rx_fill_dispensed" or fills[0].get("rx_id") != rx_id:
        return f"Error: {rx_fill_id} is not a dispensed fill of prescription {rx_id}."
    fill = fills[0]
    if membership_id and not ctx.find("membership_holdings", membership_id=membership_id,
                                      customer_id=fill["customer_id"]):
        return f"Error: {membership_id} is not a membership of this patient."
    if coverage_id and not ctx.find("insurance_coverages", coverage_id=coverage_id, customer_id=fill["customer_id"]):
        return f"Error: {coverage_id} is not a coverage of this patient."
    rid = ctx.make_id("rxb_", rx_id, rx_fill_id, membership_id, coverage_id, amount)
    day = ctx.now()[:10]
    ctx.create("rx_charges", rid, rx_charge_id=rid, rx_id=rx_id, customer_id=fill["customer_id"],
               event_type="rx_fill_charged", amount=float(cents), charge_date=day, rx_fill_id=rx_fill_id,
               price_basis="cash_member_price", pbm_patient_pay=0.0, original_charge_id="", refund_reason="none")
    return str({"charge_line_id": rid, "rx_id": rx_id, "rx_fill_id": rx_fill_id, "amount": float(cents),
                "price_basis": "cash_member_price", "charge_date": day, "status": "paid"})

@tool(owner="agent", rw="write")
def refund_rx_benefit_line_87d0f93d(ctx: ToolContext, original_charge_id: str, amount: float) -> str:
    """Refund part of a Larkspur Pharmacy fill charge line that was posted on the pharmacy-benefit basis above
    what the shipment should have cost. The agent names the fill charge line and the amount to give back; one
    billing-error refund line is booked against that line, on the same prescription and dispensed fill, dated
    today, and the patient's card on file is credited that amount. Succeeds only for an existing fill charge
    line; the refund then shows on the pharmacy billing lines with that line as its original line.

    Args:
        original_charge_id: Id class — the reference number of the fill charge line being corrected, exactly as shown
            on the pharmacy billing lines already looked up for the prescription.
        amount: Fixed-format class — the amount refunded, a positive USD amount given to 2 decimal places
            (cents, rounded half up before the call); it is booked as a negative amount on the refund line.

    Returns:
        A dict receipt: refund_line_id (str, reference number of the new refund line), original_charge_id (str,
        the fill charge line refunded), rx_id (str, prescription), rx_fill_id (str, dispensed fill), amount
        (float, the negative USD amount booked, 2 decimal places), refund_reason (str, always billing_error),
        charge_date (str, YYYY-MM-DD posting date) and status (str, "refunded" on success). A string starting
        with "Error:" means nothing was booked.
    """
    cents = _Cents.parse(amount)
    if cents is None:
        return "Error: amount must be a positive USD amount with at most 2 decimal places."
    rows = ctx.find("rx_charges", rx_charge_id=original_charge_id)
    if not rows or rows[0].get("event_type") != "rx_fill_charged":
        return f"Error: {original_charge_id} is not a fill charge line."
    line = rows[0]
    value = -float(cents)
    rid = ctx.make_id("rxf_", original_charge_id, amount)
    day = ctx.now()[:10]
    ctx.create("rx_charges", rid, rx_charge_id=rid, rx_id=line["rx_id"], customer_id=line["customer_id"],
               event_type="rx_charge_refunded", amount=value, charge_date=day, rx_fill_id=line["rx_fill_id"],
               price_basis="refund", pbm_patient_pay=0.0, original_charge_id=original_charge_id,
               refund_reason="billing_error")
    return str({"refund_line_id": rid, "original_charge_id": original_charge_id, "rx_id": line["rx_id"],
                "rx_fill_id": line["rx_fill_id"], "amount": value, "refund_reason": "billing_error",
                "charge_date": day, "status": "refunded"})


@tool(owner="user", rw="write")
def pay_rx_owed_shipping_bbdf4b04(ctx: ToolContext, rx_fill_id: str, membership_id: str, amount: float) -> str:
    """The patient pays, with a card they provide themselves, a shipping fee that was owed on one Larkspur
    Pharmacy shipment but never posted when the package went out. One shipping charge line is posted against
    the dispensed fill for the amount paid, dated today, and it shows on the prescription's pharmacy billing
    lines. Succeeds only for an existing dispensed fill and, when given, a membership of the same patient.

    Args:
        rx_fill_id: Id class — the reference number of the dispensed fill the shipping fee belongs to, exactly as
            the agent read it from the prescription's fill records and gave it to the patient.
        membership_id: Id class — the reference number of the patient's Larkspur membership record whose tier
            and status the shipping fee rests on, as read from the patient's membership records; empty when the
            patient holds no membership.
        amount: Fixed-format class — the shipping fee the patient pays, a positive USD amount given to 2 decimal
            places (cents, rounded half up), as the agent quoted it.

    Returns:
        A dict receipt: charge_line_id (str, reference number of the new shipping charge line), rx_id (str,
        prescription), rx_fill_id (str, dispensed fill), amount (float, USD paid, 2 decimal places), price_basis
        (str, always shipping), charge_date (str, YYYY-MM-DD) and status (str, "paid" on success). A string
        starting with "Error:" means nothing was posted.
    """
    cents = _Cents.parse(amount)
    if cents is None:
        return "Error: amount must be a positive USD amount with at most 2 decimal places."
    fills = ctx.find("rx_fills", rx_fill_id=rx_fill_id)
    if not fills or fills[0].get("event_type") != "rx_fill_dispensed":
        return f"Error: {rx_fill_id} is not a dispensed fill."
    fill = fills[0]
    if membership_id and not ctx.find("membership_holdings", membership_id=membership_id,
                                      customer_id=fill["customer_id"]):
        return f"Error: {membership_id} is not a membership of this patient."
    rid = ctx.make_id("rxs_", rx_fill_id, membership_id, amount)
    day = ctx.now()[:10]
    ctx.create("rx_charges", rid, rx_charge_id=rid, rx_id=fill["rx_id"], customer_id=fill["customer_id"],
               event_type="rx_shipping_charged", amount=float(cents), charge_date=day, rx_fill_id=rx_fill_id,
               price_basis="shipping", pbm_patient_pay=0.0, original_charge_id="", refund_reason="none")
    return str({"charge_line_id": rid, "rx_id": fill["rx_id"], "rx_fill_id": rx_fill_id, "amount": float(cents),
                "price_basis": "shipping", "charge_date": day, "status": "paid"})


@tool(owner="agent", rw="write")
def refund_rx_cash_shipment_4224ad9e(ctx: ToolContext, original_charge_id: str, amount: float) -> str:
    """Refund the amount a Larkspur Pharmacy cash shipment was overcharged, as one refund booked against the
    shipment's fill charge line. The agent names the fill charge line and the amount to give back; one
    billing-error refund line is booked against that line, on the same prescription and dispensed fill, dated
    today, and the patient's card on file is credited that amount. Succeeds only for an existing fill charge
    line; the refund then shows on the pharmacy billing lines with that line as its original line.

    Args:
        original_charge_id: Id class — the reference number of the shipment's fill charge line, exactly as shown
            on the pharmacy billing lines already looked up for the prescription.
        amount: Fixed-format class — the amount refunded, a positive USD amount given to 2 decimal places
            (cents, rounded half up before the call); it is booked as a negative amount on the refund line.

    Returns:
        A dict receipt: refund_line_id (str, reference number of the new refund line), original_charge_id (str,
        the fill charge line refunded), rx_id (str, prescription), rx_fill_id (str, dispensed fill), amount
        (float, the negative USD amount booked, 2 decimal places), refund_reason (str, always billing_error),
        charge_date (str, YYYY-MM-DD posting date) and status (str, "refunded" on success). A string starting
        with "Error:" means nothing was booked.
    """
    cents = _Cents.parse(amount)
    if cents is None:
        return "Error: amount must be a positive USD amount with at most 2 decimal places."
    rows = ctx.find("rx_charges", rx_charge_id=original_charge_id)
    if not rows or rows[0].get("event_type") != "rx_fill_charged":
        return f"Error: {original_charge_id} is not a fill charge line."
    line = rows[0]
    value = -float(cents)
    rid = ctx.make_id("rxc_", original_charge_id, amount)
    day = ctx.now()[:10]
    ctx.create("rx_charges", rid, rx_charge_id=rid, rx_id=line["rx_id"], customer_id=line["customer_id"],
               event_type="rx_charge_refunded", amount=value, charge_date=day, rx_fill_id=line["rx_fill_id"],
               price_basis="refund", pbm_patient_pay=0.0, original_charge_id=original_charge_id,
               refund_reason="billing_error")
    return str({"refund_line_id": rid, "original_charge_id": original_charge_id, "rx_id": line["rx_id"],
                "rx_fill_id": line["rx_fill_id"], "amount": value, "refund_reason": "billing_error",
                "charge_date": day, "status": "refunded"})

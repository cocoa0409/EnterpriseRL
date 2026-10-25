"""Hidden task tools of the wheelchair_mobility difficulty (Summit Ridge Home Medical).

Each tool performs one atomic write on a wheelchair record of the mobility line and is reached
only through the unlock/call meta-tools.
"""

from erlbench import ToolContext, tool


class _Rec:
    """Plumbing shared by the tools below (not a tool)."""

    @staticmethod
    def chair(ctx, mobility_holding_id):
        rows = ctx.find("mobility_holdings", mobility_holding_id=mobility_holding_id)
        return rows[0] if rows else {}

    @staticmethod
    def request(ctx, mobility_request_id):
        rows = ctx.find("mobility_requests", mobility_request_id=mobility_request_id)
        return rows[0] if rows else {}


@tool(owner="agent", rw="write")
def record_battery_warranty_job_f5177195(ctx: ToolContext, mobility_holding_id: str, mobility_request_id: str,
        labor_units: int, loaner_issued: bool) -> str:
    """Post a completed battery set replacement that the chair manufacturer's warranty pays for, as one
    repair job on the wheelchair record its repair request belongs to.

    The job is booked against the named wheelchair, dated the day its completed repair request was
    completed, with the battery set as the component repaired, the manufacturer warranty as
    the party bearing the cost, the labor units the job is claimed at, no parts cost (the battery set is supplied by the manufacturer), no patient share
    and the loaner flag given. The chair's serial number is copied
    from its record. The posted job appears in the chair's service history returned by the
    wheelchair service lookup; nothing is charged to the patient.

    Args:
        mobility_holding_id: Id class — reference number of the patient's wheelchair record the job was
            done on, as returned by the wheelchair record lookup for this patient.
        mobility_request_id: Id class — reference number of the completed repair request for this
            job, as returned by the wheelchair request lookup for the patient's chair.
        labor_units: Fixed-format class — labor claimed for the job, in whole 15-minute units, a
            non-negative integer with no decimals (unit: one unit = 15 minutes of labor).
        loaner_issued: Enum class — whether a loaner chair was out with the patient for this job; true
            applies when the chair's service history shows a loaner chair delivered for the time the chair
            was in for this repair, false applies when no loaner chair was delivered for this repair.

    Returns:
        A confirmation sentence (str) carrying four fields: the new repair job reference (str,
        starting "msv_"), the wheelchair record reference it was posted on (str), the job date
        (YYYY-MM-DD) and the labor units booked (integer). Receiving the sentence with a job
        reference means the job is posted.
    """
    req = _Rec.request(ctx, mobility_request_id)
    hid = mobility_holding_id
    chair = _Rec.chair(ctx, hid)
    day = str(req.get("decision_date") or "")
    rid = ctx.make_id("msv_", mobility_holding_id, mobility_request_id, bool(loaner_issued), "battery", labor_units)
    ctx.create("mobility_service", rid, mobility_service_id=rid, mobility_holding_id=hid,
               customer_id=chair.get("customer_id"), event_type="mobility_repair",
               service_date=day, delivery_purpose="none", delivery_mode="none",
               assessment_result="none", repair_component="battery",
               repair_coverage="manufacturer_warranty", labor_units=int(labor_units),
               parts_amount=0.00, repair_patient_share=0.00, loaner_issued=bool(loaner_issued),
               pickup_condition="none", serial_number=chair.get("serial_number"))
    return (f"Battery warranty job {rid} posted on wheelchair record {hid} dated {day} "
            f"with {int(labor_units)} labor units.")


@tool(owner="agent", rw="write")
def record_controller_warranty_job_4540982f(ctx: ToolContext, mobility_holding_id: str, mobility_request_id: str,
        labor_units: int, loaner_issued: bool) -> str:
    """Post a completed joystick and controller replacement that the chair manufacturer's warranty pays for, as one
    repair job on the wheelchair record its repair request belongs to.

    The job is booked against the named wheelchair, dated the day its completed repair request was
    completed, with the joystick and controller as the component repaired, the manufacturer warranty as
    the party bearing the cost, the labor units the job is claimed at, no parts cost (the joystick module is supplied by the manufacturer), no patient share
    and the loaner flag given. The chair's serial number is copied
    from its record. The posted job appears in the chair's service history returned by the
    wheelchair service lookup; nothing is charged to the patient.

    Args:
        mobility_holding_id: Id class — reference number of the patient's wheelchair record the job was
            done on, as returned by the wheelchair record lookup for this patient.
        mobility_request_id: Id class — reference number of the completed repair request for this
            job, as returned by the wheelchair request lookup for the patient's chair.
        labor_units: Fixed-format class — labor claimed for the job, in whole 15-minute units, a
            non-negative integer with no decimals (unit: one unit = 15 minutes of labor).
        loaner_issued: Enum class — whether a loaner chair was out with the patient for this job; true
            applies when the chair's service history shows a loaner chair delivered for the time the chair
            was in for this repair, false applies when no loaner chair was delivered for this repair.

    Returns:
        A confirmation sentence (str) carrying four fields: the new repair job reference (str,
        starting "msv_"), the wheelchair record reference it was posted on (str), the job date
        (YYYY-MM-DD) and the labor units booked (integer). Receiving the sentence with a job
        reference means the job is posted.
    """
    req = _Rec.request(ctx, mobility_request_id)
    hid = mobility_holding_id
    chair = _Rec.chair(ctx, hid)
    day = str(req.get("decision_date") or "")
    rid = ctx.make_id("msv_", mobility_holding_id, mobility_request_id, bool(loaner_issued), "joystick_controller", labor_units)
    ctx.create("mobility_service", rid, mobility_service_id=rid, mobility_holding_id=hid,
               customer_id=chair.get("customer_id"), event_type="mobility_repair",
               service_date=day, delivery_purpose="none", delivery_mode="none",
               assessment_result="none", repair_component="joystick_controller",
               repair_coverage="manufacturer_warranty", labor_units=int(labor_units),
               parts_amount=0.00, repair_patient_share=0.00, loaner_issued=bool(loaner_issued),
               pickup_condition="none", serial_number=chair.get("serial_number"))
    return (f"Controller warranty job {rid} posted on wheelchair record {hid} dated {day} "
            f"with {int(labor_units)} labor units.")


@tool(owner="agent", rw="write")
def record_drive_warranty_job_9fda7dd9(ctx: ToolContext, mobility_holding_id: str, mobility_request_id: str,
        labor_units: int, loaner_issued: bool) -> str:
    """Post a completed drive motor and gearbox replacement that the chair manufacturer's warranty pays for, as one
    repair job on the wheelchair record its repair request belongs to.

    The job is booked against the named wheelchair, dated the day its completed repair request was
    completed, with the drive motor and gearbox as the component repaired, the manufacturer warranty as
    the party bearing the cost, the labor units the job is claimed at, no parts cost (the drive unit is supplied by the manufacturer), no patient share
    and the loaner flag given. The chair's serial number is copied
    from its record. The posted job appears in the chair's service history returned by the
    wheelchair service lookup; nothing is charged to the patient.

    Args:
        mobility_holding_id: Id class — reference number of the patient's wheelchair record the job was
            done on, as returned by the wheelchair record lookup for this patient.
        mobility_request_id: Id class — reference number of the completed repair request for this
            job, as returned by the wheelchair request lookup for the patient's chair.
        labor_units: Fixed-format class — labor claimed for the job, in whole 15-minute units, a
            non-negative integer with no decimals (unit: one unit = 15 minutes of labor).
        loaner_issued: Enum class — whether a loaner chair was out with the patient for this job; true
            applies when the chair's service history shows a loaner chair delivered for the time the chair
            was in for this repair, false applies when no loaner chair was delivered for this repair.

    Returns:
        A confirmation sentence (str) carrying four fields: the new repair job reference (str,
        starting "msv_"), the wheelchair record reference it was posted on (str), the job date
        (YYYY-MM-DD) and the labor units booked (integer). Receiving the sentence with a job
        reference means the job is posted.
    """
    req = _Rec.request(ctx, mobility_request_id)
    hid = mobility_holding_id
    chair = _Rec.chair(ctx, hid)
    day = str(req.get("decision_date") or "")
    rid = ctx.make_id("msv_", mobility_holding_id, mobility_request_id, bool(loaner_issued), "motor_gearbox", labor_units)
    ctx.create("mobility_service", rid, mobility_service_id=rid, mobility_holding_id=hid,
               customer_id=chair.get("customer_id"), event_type="mobility_repair",
               service_date=day, delivery_purpose="none", delivery_mode="none",
               assessment_result="none", repair_component="motor_gearbox",
               repair_coverage="manufacturer_warranty", labor_units=int(labor_units),
               parts_amount=0.00, repair_patient_share=0.00, loaner_issued=bool(loaner_issued),
               pickup_condition="none", serial_number=chair.get("serial_number"))
    return (f"Drive warranty job {rid} posted on wheelchair record {hid} dated {day} "
            f"with {int(labor_units)} labor units.")


@tool(owner="user", rw="write")
def confirm_chair_return_refund_d347f359(ctx: ToolContext, mobility_holding_id: str, original_bill_id: str,
                                         refund_amount: float) -> str:
    """The patient confirms, in person, that the wheelchair they bought for cash is given back for good
    and accepts the refund owed on it; the refund is booked as one refund line dated today.

    The refund line is booked on the named wheelchair record against the cash sale line it reverses,
    with the amount refunded to the patient; deductions are not itemised on the line. The booked
    refund appears in the chair's billing history returned by the wheelchair billing lookup, and
    the patient is told the refund reference.

    Args:
        mobility_holding_id: Id class — reference number of the wheelchair record being given back, as
            returned by the wheelchair record lookup for this patient and passed on by the agent.
        original_bill_id: Id class — reference number of the cash sale line of that chair, as returned
            by the wheelchair billing lookup and passed on by the agent.
        refund_amount: Fixed-format class — total amount refunded to the patient, in US dollars,
            a decimal number with exactly 2 decimal places (cents), rounded half up to the cent.

    Returns:
        A confirmation sentence (str) carrying three fields: the refund line reference (str, starting
        "mbl_"), the sale line reference it reverses (str) and the amount refunded (US dollars with 2
        decimals). Receiving the sentence with a refund reference means the refund is booked.
    """
    chair = _Rec.chair(ctx, mobility_holding_id)
    amount = round(float(refund_amount), 2)
    rid = ctx.make_id("mbl_", mobility_holding_id, original_bill_id, amount)
    ctx.create("mobility_billing", rid, mobility_bill_id=rid, mobility_holding_id=mobility_holding_id,
               customer_id=chair.get("customer_id"), event_type="mobility_self_pay_refund",
               coverage_id=None, hcpcs_code=str(chair.get("variant_name", ""))[-6:-1],
               billing_modifier="none", rental_month_number=0, service_from_date=ctx.now()[:10],
               adjudication_date=ctx.now()[:10], allowed_amount=0.00, payer_paid_amount=0.00,
               patient_responsibility=0.00, upgrade_difference_amount=0.00, claim_number="",
               denial_reason="none", original_bill_id=original_bill_id, reversal_reason="none",
               related_service_id="", sale_amount=amount, fee_amount=0.00)
    return f"Refund {rid} booked against sale line {original_bill_id} for ${amount:.2f}."


@tool(owner="agent", rw="write")
def record_caster_warranty_job_ad31669e(ctx: ToolContext, mobility_holding_id: str, mobility_request_id: str,
        labor_units: int, loaner_issued: bool) -> str:
    """Post a completed tire or caster replacement that the chair manufacturer's warranty pays for, as one
    repair job on the wheelchair record its repair request belongs to.

    The job is booked against the named wheelchair, dated the day its completed repair request was
    completed, with the tires and casters as the component repaired, the manufacturer warranty as
    the party bearing the cost, the labor units the job is claimed at, no parts cost (the wheel parts are supplied by the manufacturer), no patient share
    and the loaner flag given. The chair's serial number is copied
    from its record. The posted job appears in the chair's service history returned by the
    wheelchair service lookup; nothing is charged to the patient.

    Args:
        mobility_holding_id: Id class — reference number of the patient's wheelchair record the job was
            done on, as returned by the wheelchair record lookup for this patient.
        mobility_request_id: Id class — reference number of the completed repair request for this
            job, as returned by the wheelchair request lookup for the patient's chair.
        labor_units: Fixed-format class — labor claimed for the job, in whole 15-minute units, a
            non-negative integer with no decimals (unit: one unit = 15 minutes of labor).
        loaner_issued: Enum class — whether a loaner chair was out with the patient for this job; true
            applies when the chair's service history shows a loaner chair delivered for the time the chair
            was in for this repair, false applies when no loaner chair was delivered for this repair.

    Returns:
        A confirmation sentence (str) carrying four fields: the new repair job reference (str,
        starting "msv_"), the wheelchair record reference it was posted on (str), the job date
        (YYYY-MM-DD) and the labor units booked (integer). Receiving the sentence with a job
        reference means the job is posted.
    """
    req = _Rec.request(ctx, mobility_request_id)
    hid = mobility_holding_id
    chair = _Rec.chair(ctx, hid)
    day = str(req.get("decision_date") or "")
    rid = ctx.make_id("msv_", mobility_holding_id, mobility_request_id, bool(loaner_issued), "tires_casters", labor_units)
    ctx.create("mobility_service", rid, mobility_service_id=rid, mobility_holding_id=hid,
               customer_id=chair.get("customer_id"), event_type="mobility_repair",
               service_date=day, delivery_purpose="none", delivery_mode="none",
               assessment_result="none", repair_component="tires_casters",
               repair_coverage="manufacturer_warranty", labor_units=int(labor_units),
               parts_amount=0.00, repair_patient_share=0.00, loaner_issued=bool(loaner_issued),
               pickup_condition="none", serial_number=chair.get("serial_number"))
    return (f"Caster warranty job {rid} posted on wheelchair record {hid} dated {day} "
            f"with {int(labor_units)} labor units.")


@tool(owner="user", rw="write")
def accept_chair_price_adjustment_610693ba(ctx: ToolContext, mobility_holding_id: str, original_bill_id: str,
                                           adjustment_amount: float) -> str:
    """The patient, who keeps the wheelchair they bought for cash, accepts in person the price adjustment
    Summit Ridge returns on that chair; the adjustment is booked as one refund line dated today.

    The line is booked on the named wheelchair record against the cash sale line it partly refunds, with
    the amount returned to the patient; the chair stays with the patient and nothing is withheld on the
    line. The booked adjustment appears in the chair's billing history returned by the wheelchair
    billing lookup, and the patient is told its reference.

    Args:
        mobility_holding_id: Id class — reference number of the wheelchair record the patient keeps, as
            returned by the wheelchair record lookup for this patient and passed on by the agent.
        original_bill_id: Id class — reference number of the cash sale line of that chair, as returned
            by the wheelchair billing lookup and passed on by the agent.
        adjustment_amount: Fixed-format class — amount returned to the patient, in US dollars, a decimal
            number with exactly 2 decimal places (cents), rounded half up to the cent.

    Returns:
        A confirmation sentence (str) carrying three fields: the adjustment line reference (str,
        starting "mbl_"), the sale line reference it partly refunds (str) and the amount returned (US
        dollars with 2 decimals). Receiving the sentence with a line reference means the adjustment is
        booked.
    """
    chair = _Rec.chair(ctx, mobility_holding_id)
    amount = round(float(adjustment_amount), 2)
    rid = ctx.make_id("mbl_", mobility_holding_id, original_bill_id, "adjust", amount)
    ctx.create("mobility_billing", rid, mobility_bill_id=rid, mobility_holding_id=mobility_holding_id,
               customer_id=chair.get("customer_id"), event_type="mobility_self_pay_refund",
               coverage_id=None, hcpcs_code=str(chair.get("variant_name", ""))[-6:-1],
               billing_modifier="none", rental_month_number=0, service_from_date=ctx.now()[:10],
               adjudication_date=ctx.now()[:10], allowed_amount=0.00, payer_paid_amount=0.00,
               patient_responsibility=0.00, upgrade_difference_amount=0.00, claim_number="",
               denial_reason="none", original_bill_id=original_bill_id, reversal_reason="none",
               related_service_id="", sale_amount=amount, fee_amount=0.00)
    return f"Price adjustment {rid} booked against sale line {original_bill_id} for ${amount:.2f}."

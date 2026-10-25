"""Hidden task tools of the pap_therapy_rentals difficulty (PAP Therapy Equipment, Summit Ridge Home Medical).

Each tool performs one atomic write on the PAP records and is reached through unlock -> call.
No tool checks a business prerequisite; every judgement is made by the caller from policy and records.
"""

from erlbench import ToolContext, tool


@tool(owner="agent", rw="write")
def record_return_inspection_bc7317cd(ctx: ToolContext, pap_holding_id: str, serial_number: str,
                                      labor_units: int, parts_amount: float,
                                      repair_patient_share: float) -> str:
    """Record the branch return inspection of a self-pay PAP device that has come back to Summit Ridge
    for a refund. One call files one inspection job on the device record: the reconditioning labor
    booked for the unit, the reconditioning parts it consumed, and the amount of used accessories the
    patient bears. The unit is assessed and reconditioned for stock, not repaired for the patient, so
    the job carries no repair cost assignment. On success the inspection appears in the device's
    service history dated today.

    Args:
        pap_holding_id: Id class — the PAP device record number of the returned self-pay device, as
            shown by the PAP device record lookup for the patient.
        serial_number: Verbatim class — the manufacturer serial number of the returned unit, copied
            character for character from the serial number shown on that PAP device record (verbatim).
        labor_units: Fixed-format class — reconditioning labor booked on the job, counted in 15-minute
            labor units, written as a non-negative integer (whole units, no fraction).
        parts_amount: Fixed-format class — reconditioning parts consumed by the unit, an amount in USD
            with 2 decimal places, rounded half up to the cent before it is passed.
        repair_patient_share: Fixed-format class — value of the used accessories the patient bears on the
            return, an amount in USD with 2 decimal places, rounded half up to the cent before it is
            passed.

    Returns:
        A dictionary rendered as text with keys: status ("recorded" when the inspection job was filed),
        pap_service_id (reference number of the new inspection job, text), pap_holding_id (the device
        record inspected), service_date (inspection date, YYYY-MM-DD), labor_units (integer units booked),
        parts_amount (USD, 2 decimal places) and repair_patient_share (USD, 2 decimal places).
    """
    labor = int(labor_units)
    parts = round(float(parts_amount), 2)
    share = round(float(repair_patient_share), 2)
    rid = ctx.make_id("pse_", pap_holding_id, serial_number, labor, parts, share)
    holder = ctx.find("pap_holdings", pap_holding_id=pap_holding_id)
    cust = holder[0].get("customer_id") if holder else None
    day = ctx.now()[:10]
    ctx.create("pap_service", rid, pap_service_id=rid, pap_holding_id=pap_holding_id, customer_id=cust,
               event_type="pap_repair", service_date=day, delivery_purpose="none", delivery_mode="none",
               serial_number=serial_number, repair_fault="none", repair_coverage="none",
               labor_units=labor, parts_amount=parts, repair_patient_share=share, loaner_issued=False,
               pickup_condition="none", compliance_result="none", benefit_documented=False,
               nights_in_window=0, nights_4h_plus=0, avg_daily_use_hours=0.0)
    return str({"status": "recorded", "pap_service_id": rid, "pap_holding_id": pap_holding_id,
                "service_date": day, "labor_units": labor, "parts_amount": parts,
                "repair_patient_share": share})


@tool(owner="user", rw="write")
def return_device_for_refund_b6f98fe9(ctx: ToolContext, pap_holding_id: str, original_bill_id: str,
                                      received_date: str, refund_amount: float) -> str:
    """The patient accepts the refund of a self-pay PAP device they bought outright and have sent back.
    One call books one refund line against the sale being refunded: the amount refunded to the patient
    and the date the returned unit was received. On success the refund line appears in the device's billing
    history and the patient can quote its reference number.

    Args:
        pap_holding_id: Id class — the PAP device record number of the self-pay device being refunded,
            as shown by the PAP device record lookup for the patient.
        original_bill_id: Id class — the reference number of the self-pay sale line being refunded, as
            shown in the device's billing history.
        received_date: Fixed-format class — the date the returned unit was received back by Summit Ridge,
            written YYYY-MM-DD.
        refund_amount: Fixed-format class — the amount refunded to the patient, in USD with 2 decimal
            places, rounded half up to the cent before it is passed.

    Returns:
        A dictionary rendered as text with keys: status ("refunded" when the refund line was booked),
        pap_bill_id (reference number of the refund line, text), original_bill_id (the sale refunded),
        service_from_date (the received date, YYYY-MM-DD) and refund_amount (USD, 2 decimal places).
    """
    amount = round(float(refund_amount), 2)
    rid = ctx.make_id("pbr_", pap_holding_id, original_bill_id, received_date, amount)
    holder = ctx.find("pap_holdings", pap_holding_id=pap_holding_id)
    cust = holder[0].get("customer_id") if holder else None
    sale = ctx.find("pap_billing", pap_bill_id=original_bill_id)
    code = sale[0].get("hcpcs_code") if sale else None
    ctx.create("pap_billing", rid, pap_bill_id=rid, pap_holding_id=pap_holding_id, customer_id=cust,
               event_type="pap_purchase_refund", hcpcs_code=code, billing_modifier="NU",
               rental_month_number=0, service_from_date=received_date, adjudication_date=ctx.now()[:10],
               allowed_amount=0.0, addon_allowed_amount=0.0, payer_paid_amount=0.0,
               patient_responsibility=0.0, claim_number="", denial_reason="none",
               original_bill_id=original_bill_id, reversal_reason="none", sale_amount=amount)
    return str({"status": "refunded", "pap_bill_id": rid, "original_bill_id": original_bill_id,
                "service_from_date": received_date, "refund_amount": amount})


@tool(owner="agent", rw="write")
def record_usage_download_48c54aed(ctx: ToolContext, pap_holding_id: str, serial_number: str,
                                   window_start_date: str, window_end_date: str, nights_4h_plus: int,
                                   avg_daily_use_hours: float) -> str:
    """File a usage summary download on a PAP device record: one record that summarises the therapy use
    the device modem has reported over a span of nights, with the qualifying nights credited and the
    average daily use. The summary is a usage statement for the device, not a scored compliance
    window, so it carries no met or not-met result. On success the summary appears in the device's
    service history dated today.

    Args:
        pap_holding_id: Id class — the PAP device record number the summary is filed on, as shown by the
            PAP device record lookup for the patient.
        serial_number: Verbatim class — the manufacturer serial number of the unit currently in the home,
            copied character for character from the serial number shown on that PAP device record (verbatim).
        window_start_date: Fixed-format class — first night the summary covers, written YYYY-MM-DD.
        window_end_date: Fixed-format class — last night the summary covers, written YYYY-MM-DD.
        nights_4h_plus: Fixed-format class — qualifying nights credited on the summary, written as a
            non-negative integer count of nights.
        avg_daily_use_hours: Fixed-format class — average daily use stated on the summary, in the form
            decimal, 1 place, hours: precision of 1 decimal place, rounded half up to 1 decimal place before
            it is passed.

    Returns:
        A dictionary rendered as text with keys: status ("recorded" when the summary was filed),
        pap_service_id (reference number of the summary, text), pap_holding_id (the device record),
        service_date (filing date, YYYY-MM-DD), window_start_date and window_end_date (YYYY-MM-DD),
        nights_4h_plus (integer nights) and avg_daily_use_hours (hours, one decimal place).
    """
    nights = int(nights_4h_plus)
    hours = round(float(avg_daily_use_hours), 1)
    rid = ctx.make_id("psu_", pap_holding_id, serial_number, window_start_date, window_end_date, nights, hours)
    holder = ctx.find("pap_holdings", pap_holding_id=pap_holding_id)
    cust = holder[0].get("customer_id") if holder else None
    day = ctx.now()[:10]
    ctx.create("pap_service", rid, pap_service_id=rid, pap_holding_id=pap_holding_id, customer_id=cust,
               event_type="pap_compliance_download", service_date=day, delivery_purpose="none",
               delivery_mode="none", serial_number=serial_number, window_start_date=window_start_date,
               window_end_date=window_end_date, nights_4h_plus=nights, avg_daily_use_hours=hours,
               compliance_result="none", benefit_documented=False, repair_fault="none",
               repair_coverage="none", labor_units=0, parts_amount=0.0, repair_patient_share=0.0,
               loaner_issued=False, pickup_condition="none")
    return str({"status": "recorded", "pap_service_id": rid, "pap_holding_id": pap_holding_id,
                "service_date": day, "window_start_date": window_start_date,
                "window_end_date": window_end_date, "nights_4h_plus": nights,
                "avg_daily_use_hours": hours})


@tool(owner="user", rw="write")
def purchase_home_device_8c1f8216(ctx: ToolContext, pap_holding_id: str, hcpcs_code: str,
                                  sale_amount: float) -> str:
    """The patient buys outright, as a self-pay purchase, the PAP unit that is already in their home on
    the given device record, paying the price in full. One call books one self-pay
    sale line on that device record dated today. No delivery fee is charged because the unit is already
    in the home. On success the sale line appears in the device's billing history and the patient can
    quote its reference number.

    Args:
        pap_holding_id: Id class — the PAP device record number of the unit being bought, as shown by the
            PAP device record lookup for the patient.
        hcpcs_code: Enum class — the device code of the unit bought, exactly one of: E0601 when the record's
            device class is a CPAP class (its class name ends in E0601); E0470 when the record's device
            class is the Bilevel PAP Spontaneous System; E0471 when the record's device class is the
            Bilevel PAP Spontaneous-Timed System or the Adaptive Servo-Ventilation System.
        sale_amount: Fixed-format class — the sale amount charged to the patient for the unit, in USD with
            2 decimal places, rounded half up to the cent before it is passed.

    Returns:
        A dictionary rendered as text with keys: status ("sold" when the sale line was booked),
        pap_bill_id (reference number of the sale line, text), pap_holding_id (the device record),
        service_from_date (the delivery date booked on the sale line, which for a unit already in the
        home is the day of the sale, YYYY-MM-DD), hcpcs_code (device code) and sale_amount (USD, 2
        decimal places).
    """
    amount = round(float(sale_amount), 2)
    rid = ctx.make_id("pbs_", pap_holding_id, hcpcs_code, amount)
    holder = ctx.find("pap_holdings", pap_holding_id=pap_holding_id)
    cust = holder[0].get("customer_id") if holder else None
    day = ctx.now()[:10]
    ctx.create("pap_billing", rid, pap_bill_id=rid, pap_holding_id=pap_holding_id, customer_id=cust,
               event_type="pap_purchase_sale", hcpcs_code=hcpcs_code, billing_modifier="NU",
               rental_month_number=0, service_from_date=day, adjudication_date=day, allowed_amount=0.0,
               addon_allowed_amount=0.0, payer_paid_amount=0.0, patient_responsibility=0.0,
               claim_number="", denial_reason="none", reversal_reason="none", sale_amount=amount,
               fee_amount=0.0)
    return str({"status": "sold", "pap_bill_id": rid, "pap_holding_id": pap_holding_id,
                "service_from_date": day, "hcpcs_code": hcpcs_code, "sale_amount": amount})

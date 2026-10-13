"""Hidden task tools for the cleaning_and_damage_fee_assessments difficulty of env_0056_ride_hailing_platform.

Each tool performs exactly one atomic write on a cleaning or damage fee assessment (with the ledger
entry the base event model attaches to that write) and returns a receipt. No tool checks a policy
condition, a prerequisite or an eligibility rule: the agent decides from the published policy and the
records whether and with what values a write is made.
"""

from erlbench import ToolContext, tool


@tool(owner="agent", rw="write")
def move_down_report_level_d77023ae(ctx: ToolContext, damage_assessment_id: str, new_fee_level: str,
                                    assessed_fee: float) -> str:
    """Move a cleaning fee report that is still under review down to a lower fee level and record the
    fee assessed at that new level. The assessment keeps its status, trip, driver and evidence; only the
    fee level it is held at and the fee currently assessed on it change, and the rider has not been
    charged anything by this action. Afterwards the assessment shows the new level and the assessed fee
    when it is looked up.

    Args:
        damage_assessment_id: Id class — the reference number of the cleaning or damage fee assessment being moved down, as returned by the assessment lookup.
        new_fee_level: Enum class — the official fee level the assessment is held at after the move; exactly one of: Cleaning Fee Level 1 (Minor) when the report now sits at the minor level for a small spot clean; Cleaning Fee Level 2 (Moderate) when it now sits at the moderate level for one seat or floor area; Cleaning Fee Level 3 (Significant) when it now sits at the significant level for up to two surfaces or a bodily fluid on one surface; Cleaning Fee Level 4 (Major) when it now sits at the major level that needs professional detailing; Damage Fee (Interior Repair) when it now sits at the interior repair level; Damage Fee (Exterior Repair) when it now sits at the exterior repair level.
        assessed_fee: Fixed-format class — the fee assessed at the new level, in USD as a decimal number rounded half up to 2 decimal places, for example 87.50; never empty.

    Returns:
        A dictionary rendered as text with keys: status ("moved_down" once the write has landed),
        damage_assessment_id (the assessment reference number), fee_level (the official name of the
        level now held), assessed_fee (the fee now assessed, USD with 2 decimal places) and
        assessment_status (the unchanged lifecycle status of the assessment).
    """
    rows = ctx.find("damage_assessments", damage_assessment_id=damage_assessment_id)
    current = rows[0] if rows else {}
    fee = round(float(assessed_fee), 2)
    ctx.update("damage_assessments", damage_assessment_id, variant_name=new_fee_level, assessed_fee=fee)
    return str({"status": "moved_down", "damage_assessment_id": damage_assessment_id,
                "fee_level": new_fee_level, "assessed_fee": fee,
                "assessment_status": current.get("status", "")})


@tool(owner="user", rw="write")
def upload_report_photos_a5022c03(ctx: ToolContext, damage_assessment_id: str, photos_in_upload: int) -> str:
    """The driver uploads one set of photos from the driver app to their own cleaning or damage report.
    The upload is recorded on the report's evidence ledger as one photo submission at the fee level the
    report currently holds, dated now, and the number of photos on file for the report rises by the
    photos in this upload. The driver sees the upload on the report and the new photo total.

    Args:
        damage_assessment_id: Id class — the reference number of the driver's report (the cleaning or damage fee assessment) the photos belong to, as given to the driver by support from the assessment lookup.
        photos_in_upload: Fixed-format class — the number of photos in this one upload, a whole integer count of photos (1 or more), no decimals.

    Returns:
        A dictionary rendered as text with keys: status ("photos_uploaded" once the upload is on file),
        damage_event_id (the reference number of the new photo submission entry), damage_assessment_id
        (the report reference number), photos_in_upload (integer photos in this upload) and
        photos_on_file (integer photos now on file for the report).
    """
    rows = ctx.find("damage_assessments", damage_assessment_id=damage_assessment_id)
    current = rows[0] if rows else {}
    count = int(photos_in_upload)
    on_file = int(current.get("photo_count") or 0) + count
    eid = ctx.make_id("dev_", damage_assessment_id, count)
    ctx.create("damage_events", eid, damage_event_id=eid, damage_assessment_id=damage_assessment_id,
               customer_id=current.get("customer_id", ""), event_type="damage_evidence_submit",
               event_date=ctx.now()[:10], recorded_at=ctx.now(), amount=0.0, evidence_type="photo_set",
               evidence_count=count, fee_level=current.get("variant_name", ""), original_event_id=None,
               refund_reason="none")
    ctx.update("damage_assessments", damage_assessment_id, photo_count=on_file)
    return str({"status": "photos_uploaded", "damage_event_id": eid, "damage_assessment_id": damage_assessment_id,
                "photos_in_upload": count, "photos_on_file": on_file})


@tool(owner="agent", rw="write")
def price_partner_work_order_4e0ef0e3(ctx: ToolContext, damage_assessment_id: str, cleaning_cost_on_file: float) -> str:
    """Record the price of a Wayfare partner detailer's work order that is already on file for a cleaning
    report, bringing the report's evidence totals up to date: the cleaning cost on file for the report
    is set to the amount given. Nothing is charged or paid by this action. Afterwards the assessment
    lookup shows the new cleaning cost on file.

    Args:
        damage_assessment_id: Id class — the reference number of the cleaning fee assessment whose partner work order is being priced, as returned by the assessment lookup.
        cleaning_cost_on_file: Fixed-format class — the cleaning cost to hold on file for the report, in USD as a decimal number rounded half up to 2 decimal places, for example 214.50.

    Returns:
        A dictionary rendered as text with keys: status ("cost_recorded" once the amount is on file),
        damage_assessment_id (the assessment reference number) and cleaning_cost_on_file (the cost
        now on file, USD with 2 decimal places).
    """
    cost = round(float(cleaning_cost_on_file), 2)
    ctx.update("damage_assessments", damage_assessment_id, repair_receipt_amount=cost)
    return str({"status": "cost_recorded", "damage_assessment_id": damage_assessment_id,
                "cleaning_cost_on_file": cost})


@tool(owner="agent", rw="write")
def approve_cleaning_fee_charge_639a45e8(ctx: ToolContext, damage_assessment_id: str, trip_id: str,
                                         driver_customer_id: str, fee_charged: float) -> str:
    """Approve a cleaning fee report under review at the fee level it holds and charge the fee to the
    rider who requested the trip. The assessment moves to charged, its assessed fee becomes the fee
    charged and its charge date becomes today; a fee charge entry for the amount is booked on the
    assessment ledger and the net fee billed to the rider rises by the same amount. The rider's card on
    file is charged that amount.

    Args:
        damage_assessment_id: Id class — the reference number of the cleaning fee assessment being approved, as returned by the assessment lookup.
        trip_id: Id class — the reference number of the trip the assessment is for, as shown on the assessment and the trip lookup.
        driver_customer_id: Id class — the customer reference number of the driver who made the report, as shown on the assessment.
        fee_charged: Fixed-format class — the fee charged to the rider on approval, in USD as a decimal number rounded half up to 2 decimal places, for example 142.80.

    Returns:
        A dictionary rendered as text with keys: status ("charged" once the approval and the charge have
        landed), damage_assessment_id (the assessment reference number), damage_event_id (the
        reference number of the fee charge entry), trip_id (the trip reference number),
        driver_customer_id (the reporting driver's customer reference number), fee_level (the level
        charged), fee_charged (USD with 2 decimal places), charged_date (YYYY-MM-DD) and
        net_fee_billed (the net fee now billed on the assessment, USD with 2 decimal places).
    """
    rows = ctx.find("damage_assessments", damage_assessment_id=damage_assessment_id)
    current = rows[0] if rows else {}
    fee = round(float(fee_charged), 2)
    today = ctx.now()[:10]
    net = round(float(current.get("net_fee_billed") or 0) + fee, 2)
    eid = ctx.make_id("dfc_", damage_assessment_id, trip_id, driver_customer_id, fee)
    ctx.update("damage_assessments", damage_assessment_id, status="charged", assessed_fee=fee,
               charged_date=today, net_fee_billed=net)
    ctx.create("damage_events", eid, damage_event_id=eid, damage_assessment_id=damage_assessment_id,
               customer_id=current.get("customer_id", ""), event_type="damage_fee_charge", event_date=today,
               recorded_at=ctx.now(), amount=fee, evidence_type="none", evidence_count=0,
               fee_level=current.get("variant_name", ""), original_event_id=None, refund_reason="none")
    return str({"status": "charged", "damage_assessment_id": damage_assessment_id, "damage_event_id": eid,
                "trip_id": trip_id, "driver_customer_id": driver_customer_id,
                "fee_level": current.get("variant_name", ""), "fee_charged": fee, "charged_date": today,
                "net_fee_billed": net})


@tool(owner="user", rw="write")
def file_schedule_repair_estimate_16065485(ctx: ToolContext, damage_assessment_id: str, schedule_estimate_amount: float) -> str:
    """The driver files the Wayfare repair schedule estimate for the damage on their own report from the
    driver app. The filing is recorded on the report's evidence ledger as one repair estimate submission
    at the fee level the report holds, dated now, and the repair amount on file for the report becomes
    the schedule estimate amount, replacing the amount of any earlier estimate. The driver sees the
    estimate on the report and the new repair amount on file.

    Args:
        damage_assessment_id: Id class — the reference number of the driver's damage report (the cleaning or damage fee assessment) the estimate is filed on, as given to the driver by support from the assessment lookup.
        schedule_estimate_amount: Fixed-format class — the schedule estimate amount being filed, in USD as a decimal number rounded half up to 2 decimal places, for example 486.25.

    Returns:
        A dictionary rendered as text with keys: status ("estimate_filed" once the filing is on
        record), damage_event_id (the reference number of the new estimate submission entry),
        damage_assessment_id (the report reference number) and repair_amount_on_file (the repair
        amount now on file, USD with 2 decimal places).
    """
    rows = ctx.find("damage_assessments", damage_assessment_id=damage_assessment_id)
    current = rows[0] if rows else {}
    amount = round(float(schedule_estimate_amount), 2)
    eid = ctx.make_id("dev_", damage_assessment_id, amount)
    ctx.create("damage_events", eid, damage_event_id=eid, damage_assessment_id=damage_assessment_id,
               customer_id=current.get("customer_id", ""), event_type="damage_evidence_submit",
               event_date=ctx.now()[:10], recorded_at=ctx.now(), amount=0.0, evidence_type="repair_estimate",
               evidence_count=1, fee_level=current.get("variant_name", ""), original_event_id=None,
               refund_reason="none")
    ctx.update("damage_assessments", damage_assessment_id, repair_receipt_amount=amount)
    return str({"status": "estimate_filed", "damage_event_id": eid, "damage_assessment_id": damage_assessment_id,
                "repair_amount_on_file": amount})


@tool(owner="agent", rw="write")
def approve_damage_fee_charge_55ca59de(ctx: ToolContext, damage_assessment_id: str, trip_id: str,
                                       driver_customer_id: str, fee_charged: float) -> str:
    """Approve a damage fee report under review at the receipt-based level it holds and charge the fee to
    the rider who requested the trip. The assessment moves to charged, its assessed fee becomes the fee
    charged and its charge date becomes today; a fee charge entry for the amount is booked on the
    assessment ledger and the net fee billed to the rider rises by the same amount. The rider's card on
    file is charged that amount.

    Args:
        damage_assessment_id: Id class — the reference number of the damage fee assessment being approved, as returned by the assessment lookup.
        trip_id: Id class — the reference number of the trip the assessment is for, as shown on the assessment and the trip lookup.
        driver_customer_id: Id class — the customer reference number of the driver who made the report, as shown on the assessment.
        fee_charged: Fixed-format class — the damage fee charged to the rider on approval, in USD as a decimal number rounded half up to 2 decimal places, for example 512.40.

    Returns:
        A dictionary rendered as text with keys: status ("charged" once the approval and the charge have
        landed), damage_assessment_id (the assessment reference number), damage_event_id (the
        reference number of the fee charge entry), trip_id (the trip reference number),
        driver_customer_id (the reporting driver's customer reference number), fee_level (the level
        charged), fee_charged (USD with 2 decimal places), charged_date (YYYY-MM-DD) and
        net_fee_billed (the net fee now billed on the assessment, USD with 2 decimal places).
    """
    rows = ctx.find("damage_assessments", damage_assessment_id=damage_assessment_id)
    current = rows[0] if rows else {}
    fee = round(float(fee_charged), 2)
    today = ctx.now()[:10]
    net = round(float(current.get("net_fee_billed") or 0) + fee, 2)
    eid = ctx.make_id("dfc_", damage_assessment_id, trip_id, driver_customer_id, fee)
    ctx.update("damage_assessments", damage_assessment_id, status="charged", assessed_fee=fee,
               charged_date=today, net_fee_billed=net)
    ctx.create("damage_events", eid, damage_event_id=eid, damage_assessment_id=damage_assessment_id,
               customer_id=current.get("customer_id", ""), event_type="damage_fee_charge", event_date=today,
               recorded_at=ctx.now(), amount=fee, evidence_type="none", evidence_count=0,
               fee_level=current.get("variant_name", ""), original_event_id=None, refund_reason="none")
    return str({"status": "charged", "damage_assessment_id": damage_assessment_id, "damage_event_id": eid,
                "trip_id": trip_id, "driver_customer_id": driver_customer_id,
                "fee_level": current.get("variant_name", ""), "fee_charged": fee, "charged_date": today,
                "net_fee_billed": net})


@tool(owner="agent", rw="write")
def correct_upheld_fee_level_42a82f5f(ctx: ToolContext, damage_assessment_id: str, new_fee_level: str,
                                      fee_standing: float) -> str:
    """Move an assessment whose fee has already been charged (and possibly disputed and upheld) down to a
    lower fee level and record the fee that stands at that level. The assessment keeps its status,
    charge date, dispute dates and ledger; only the level it is held at and its assessed fee change.
    No money is returned to the rider by this action. Afterwards the assessment lookup shows the new
    level and the fee standing.

    Args:
        damage_assessment_id: Id class — the reference number of the charged cleaning or damage fee assessment being corrected, as returned by the assessment lookup.
        new_fee_level: Enum class — the official fee level the assessment is held at after the correction; exactly one of: Cleaning Fee Level 1 (Minor) when it now sits at the minor level for a small spot clean; Cleaning Fee Level 2 (Moderate) when it now sits at the moderate level for one seat or floor area; Cleaning Fee Level 3 (Significant) when it now sits at the significant level for up to two surfaces or a bodily fluid on one surface; Cleaning Fee Level 4 (Major) when it now sits at the major level that needs professional detailing; Damage Fee (Interior Repair) when it now sits at the interior repair level; Damage Fee (Exterior Repair) when it now sits at the exterior repair level.
        fee_standing: Fixed-format class — the fee that stands on the assessment at the new level, in USD as a decimal number rounded half up to 2 decimal places, for example 64.20.

    Returns:
        A dictionary rendered as text with keys: status ("level_corrected" once the write has
        landed), damage_assessment_id (the assessment reference number), fee_level (the official name
        of the level now held), fee_standing (the fee now standing, USD with 2 decimal places) and
        assessment_status (the unchanged lifecycle status of the assessment).
    """
    rows = ctx.find("damage_assessments", damage_assessment_id=damage_assessment_id)
    current = rows[0] if rows else {}
    fee = round(float(fee_standing), 2)
    ctx.update("damage_assessments", damage_assessment_id, variant_name=new_fee_level, assessed_fee=fee)
    return str({"status": "level_corrected", "damage_assessment_id": damage_assessment_id,
                "fee_level": new_fee_level, "fee_standing": fee, "assessment_status": current.get("status", "")})


@tool(owner="agent", rw="write")
def refund_level_difference_30807e99(ctx: ToolContext, damage_assessment_id: str, original_event_id: str,
                                     refund_amount: float) -> str:
    """Refund to the rider's original payment method part of a cleaning or damage fee already charged,
    because the assessment now stands at a lower level. A partial refund entry for the amount is booked
    on the assessment ledger against the fee charge it returns money from, at the level the assessment
    now holds, dated today, and the net fee billed on the assessment falls by the same amount. The rider
    sees the refund on the original card.

    Args:
        damage_assessment_id: Id class — the reference number of the assessment the refund is made on, as returned by the assessment lookup.
        original_event_id: Id class — the reference number of the fee charge entry on that assessment's ledger that the refund returns money from, as returned by the assessment ledger lookup.
        refund_amount: Fixed-format class — the amount refunded to the rider, a positive number in USD rounded half up to 2 decimal places, for example 48.75; it is booked on the ledger as a negative amount.

    Returns:
        A dictionary rendered as text with keys: status ("refunded" once the refund entry is
        booked), damage_event_id (the reference number of the partial refund entry),
        damage_assessment_id (the assessment reference number), original_event_id (the fee charge
        refunded from), refund_amount (USD with 2 decimal places, positive) and net_fee_billed (the net
        fee now billed on the assessment, USD with 2 decimal places).
    """
    rows = ctx.find("damage_assessments", damage_assessment_id=damage_assessment_id)
    current = rows[0] if rows else {}
    amount = round(float(refund_amount), 2)
    net = round(float(current.get("net_fee_billed") or 0) - amount, 2)
    eid = ctx.make_id("dpr_", damage_assessment_id, original_event_id, amount)
    ctx.create("damage_events", eid, damage_event_id=eid, damage_assessment_id=damage_assessment_id,
               customer_id=current.get("customer_id", ""), event_type="damage_fee_partial_refund",
               event_date=ctx.now()[:10], recorded_at=ctx.now(), amount=-amount, evidence_type="none",
               evidence_count=0, fee_level=current.get("variant_name", ""), original_event_id=original_event_id,
               refund_reason="level_reclassified")
    ctx.update("damage_assessments", damage_assessment_id, net_fee_billed=net)
    return str({"status": "refunded", "damage_event_id": eid, "damage_assessment_id": damage_assessment_id,
                "original_event_id": original_event_id, "refund_amount": amount, "net_fee_billed": net})

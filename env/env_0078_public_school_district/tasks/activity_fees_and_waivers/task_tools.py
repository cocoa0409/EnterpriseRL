"""Hidden task tools of the activity_fees_and_waivers difficulty (Calloway Creek ISD).

Each tool performs one atomic write on a student's activity participation and is reached through
the unlock/call meta-tools by the name its extended policy registers.
"""

from decimal import Decimal, ROUND_HALF_UP

from erlbench import ToolContext, tool


class _Cents:
    """Exact half-up rounding of money amounts to the cent, and the district receipt numbering."""

    @staticmethod
    def of(value) -> float:
        return float(Decimal(str(value)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP))

    @staticmethod
    def positive(value) -> bool:
        exact = Decimal(str(value))
        return exact > 0 and exact == exact.quantize(Decimal("0.01"))

    @staticmethod
    def receipt(row_id: str) -> str:
        digits = str(int(row_id.split("_")[-1], 16) % 1000000).zfill(6)
        return "74" + digits


class _Packet:
    """Shared, write-free pieces of the packet and fee tools."""

    FORMS = ("parent_permission", "code_of_conduct", "overnight_travel_permission")

    @staticmethod
    def household(ctx: ToolContext, activity_participation_id: str) -> str:
        rows = ctx.find("activity_participations", activity_participation_id=activity_participation_id)
        return rows[0].get("customer_id", "") if rows else ""


@tool(owner="user", rw="write")
def submit_uil_packet_8c6962d4(ctx: ToolContext, activity_participation_id: str, participation_fee_amount: float) -> dict:
    """The parent or guardian submits the signed participation packet of a UIL Academic and Robotics Team registration.

    The family's own submission records the three signed packet forms on the participation's
    records (parent permission, code of conduct and overnight travel permission, each dated and
    received today) and posts the participation fee as a new fee entry dated today, so the
    household's amount due on the participation rises by that fee. The family sees the forms as
    received and the participation fee in the fee history.

    Args:
        activity_participation_id: Id class — reference number of the student's UIL Academic and Robotics Team participation, as returned by the activity participation lookup.
        participation_fee_amount: Fixed-format class — the participation fee to post, in USD, a positive amount with 2 decimal places, already rounded to the cent (half a cent rounds up); any further digits are rounded half up to the cent.

    Returns:
        A dictionary describing the submission: activity_participation_id (string), forms_recorded (list of the three form codes recorded), fee_ledger_id (string, reference number of the new participation fee entry), participation_fee_amount (number, USD with 2 decimal places), submitted_date (string, YYYY-MM-DD, today) and status (string, "submitted" when the packet was recorded). A malformed amount returns a dictionary whose status is "error" with a message and records nothing.
    """
    amount = _Cents.of(participation_fee_amount)
    if not _Cents.positive(amount):
        return {"status": "error", "message": "participation_fee_amount must be a positive USD amount"}
    household = _Packet.household(ctx, activity_participation_id)
    today = ctx.now()[:10]
    for form in _Packet.FORMS:
        rid = ctx.make_id("uildoc_", activity_participation_id, form, today)
        ctx.create("activity_records_log", rid, activity_record_id=rid, activity_participation_id=activity_participation_id,
                   customer_id=household, event_type="activity_document_received", document_type=form,
                   document_date=today, received_date=today, equipment_tag="", record_date="")
    fee_id = ctx.make_id("uilfee_", activity_participation_id, participation_fee_amount)
    ctx.create("activity_ledger", fee_id, activity_ledger_id=fee_id, activity_participation_id=activity_participation_id,
               customer_id=household, event_type="activity_fee", amount=amount, posted_date=today,
               fee_component="participation_fee", equipment_tag="", payment_method="not_applicable",
               payment_reference="", credit_reason="not_applicable", source_activity_ledger_id="")
    return {"activity_participation_id": activity_participation_id, "forms_recorded": list(_Packet.FORMS),
            "fee_ledger_id": fee_id, "participation_fee_amount": amount, "submitted_date": today,
            "status": "submitted"}


@tool(owner="agent", rw="write")
def post_uil_travel_fee_ebd1d9ff(ctx: ToolContext, activity_participation_id: str, travel_fee_amount: float) -> dict:
    """Post the competition travel fee on a UIL Academic and Robotics Team participation.

    The activity office books one new travel fee entry dated today on the participation's fee
    account; the household's amount due on the participation rises by that amount, and the entry
    is visible in the fee history with its own reference number and amount.

    Args:
        activity_participation_id: Id class — reference number of the student's UIL Academic and Robotics Team participation, as returned by the activity participation lookup.
        travel_fee_amount: Fixed-format class — the travel fee to post, in USD, a positive amount with 2 decimal places, already rounded to the cent (half a cent rounds up); any further digits are rounded half up to the cent.

    Returns:
        A dictionary describing the posted fee: activity_ledger_id (string, reference number of the new fee entry), activity_participation_id (string), fee_component (string, travel_fee), amount (number, USD with 2 decimal places), posted_date (string, YYYY-MM-DD, today) and status (string, "posted" when the fee was booked). A malformed amount returns a dictionary whose status is "error" with a message and books nothing.
    """
    amount = _Cents.of(travel_fee_amount)
    if not _Cents.positive(amount):
        return {"status": "error", "message": "the amount must be a positive USD amount"}
    household = _Packet.household(ctx, activity_participation_id)
    today = ctx.now()[:10]
    rid = ctx.make_id("uiltrv_", activity_participation_id, "travel_fee", travel_fee_amount)
    ctx.create("activity_ledger", rid, activity_ledger_id=rid, activity_participation_id=activity_participation_id,
               customer_id=household, event_type="activity_fee", amount=amount, posted_date=today,
               fee_component="travel_fee", equipment_tag="", payment_method="not_applicable",
               payment_reference="", credit_reason="not_applicable", source_activity_ledger_id="")
    return {"activity_ledger_id": rid, "activity_participation_id": activity_participation_id,
            "fee_component": "travel_fee", "amount": amount, "posted_date": today, "status": "posted"}


@tool(owner="user", rw="write")
def submit_arts_packet_1cf2bbdb(ctx: ToolContext, activity_participation_id: str, participation_fee_amount: float) -> dict:
    """The parent or guardian submits the signed participation packet of a Fine Arts Performing Ensemble registration.

    The family's own submission records the three signed packet forms on the participation's
    records (parent permission, code of conduct and overnight travel permission, each dated and
    received today) and posts the ensemble participation fee as a new fee entry dated today, so the
    household's amount due on the participation rises by that fee. The family sees the forms as
    received and the participation fee in the fee history.

    Args:
        activity_participation_id: Id class — reference number of the student's Fine Arts Performing Ensemble participation, as returned by the activity participation lookup.
        participation_fee_amount: Fixed-format class — the participation fee to post, in USD, a positive amount with 2 decimal places, already rounded to the cent (half a cent rounds up); any further digits are rounded half up to the cent.

    Returns:
        A dictionary describing the submission: activity_participation_id (string), forms_recorded (list of the three form codes recorded), fee_ledger_id (string, reference number of the new participation fee entry), participation_fee_amount (number, USD with 2 decimal places), submitted_date (string, YYYY-MM-DD, today) and status (string, "submitted" when the packet was recorded). A malformed amount returns a dictionary whose status is "error" with a message and records nothing.
    """
    amount = _Cents.of(participation_fee_amount)
    if not _Cents.positive(amount):
        return {"status": "error", "message": "participation_fee_amount must be a positive USD amount"}
    household = _Packet.household(ctx, activity_participation_id)
    today = ctx.now()[:10]
    for form in _Packet.FORMS:
        rid = ctx.make_id("artsdoc_", activity_participation_id, form, today)
        ctx.create("activity_records_log", rid, activity_record_id=rid, activity_participation_id=activity_participation_id,
                   customer_id=household, event_type="activity_document_received", document_type=form,
                   document_date=today, received_date=today, equipment_tag="", record_date="")
    fee_id = ctx.make_id("artsfee_", activity_participation_id, participation_fee_amount)
    ctx.create("activity_ledger", fee_id, activity_ledger_id=fee_id, activity_participation_id=activity_participation_id,
               customer_id=household, event_type="activity_fee", amount=amount, posted_date=today,
               fee_component="participation_fee", equipment_tag="", payment_method="not_applicable",
               payment_reference="", credit_reason="not_applicable", source_activity_ledger_id="")
    return {"activity_participation_id": activity_participation_id, "forms_recorded": list(_Packet.FORMS),
            "fee_ledger_id": fee_id, "participation_fee_amount": amount, "submitted_date": today,
            "status": "submitted"}


@tool(owner="agent", rw="write")
def post_arts_travel_fee_8b3017ab(ctx: ToolContext, activity_participation_id: str, travel_fee_amount: float) -> dict:
    """Post the performance trip travel fee on a Fine Arts Performing Ensemble participation.

    The activity office books one new travel fee entry dated today on the participation's fee
    account; the household's amount due on the participation rises by that amount, and the entry
    is visible in the fee history with its own reference number and amount.

    Args:
        activity_participation_id: Id class — reference number of the student's Fine Arts Performing Ensemble participation, as returned by the activity participation lookup.
        travel_fee_amount: Fixed-format class — the travel fee to post, in USD, a positive amount with 2 decimal places, already rounded to the cent (half a cent rounds up); any further digits are rounded half up to the cent.

    Returns:
        A dictionary describing the posted fee: activity_ledger_id (string, reference number of the new fee entry), activity_participation_id (string), fee_component (string, travel_fee), amount (number, USD with 2 decimal places), posted_date (string, YYYY-MM-DD, today) and status (string, "posted" when the fee was booked). A malformed amount returns a dictionary whose status is "error" with a message and books nothing.
    """
    amount = _Cents.of(travel_fee_amount)
    if not _Cents.positive(amount):
        return {"status": "error", "message": "the amount must be a positive USD amount"}
    household = _Packet.household(ctx, activity_participation_id)
    today = ctx.now()[:10]
    rid = ctx.make_id("artstrv_", activity_participation_id, "travel_fee", travel_fee_amount)
    ctx.create("activity_ledger", rid, activity_ledger_id=rid, activity_participation_id=activity_participation_id,
               customer_id=household, event_type="activity_fee", amount=amount, posted_date=today,
               fee_component="travel_fee", equipment_tag="", payment_method="not_applicable",
               payment_reference="", credit_reason="not_applicable", source_activity_ledger_id="")
    return {"activity_ledger_id": rid, "activity_participation_id": activity_participation_id,
            "fee_component": "travel_fee", "amount": amount, "posted_date": today, "status": "posted"}


@tool(owner="agent", rw="write")
def post_arts_attire_fee_5e2c9a17(ctx: ToolContext, activity_participation_id: str, uniform_package_amount: float) -> dict:
    """Post the concert attire package on a Fine Arts Performing Ensemble participation.

    The activity office books one new uniform package fee entry dated today on the
    participation's fee account; the household's amount due on the participation rises by that
    amount, and the entry is visible in the fee history with its own reference number and amount.

    Args:
        activity_participation_id: Id class — reference number of the student's Fine Arts Performing Ensemble participation, as returned by the activity participation lookup.
        uniform_package_amount: Fixed-format class — the concert attire package to post, in USD, a positive amount with 2 decimal places, already rounded to the cent (half a cent rounds up); any further digits are rounded half up to the cent.

    Returns:
        A dictionary describing the posted fee: activity_ledger_id (string, reference number of the new fee entry), activity_participation_id (string), fee_component (string, uniform_package), amount (number, USD with 2 decimal places), posted_date (string, YYYY-MM-DD, today) and status (string, "posted" when the fee was booked). A malformed amount returns a dictionary whose status is "error" with a message and books nothing.
    """
    amount = _Cents.of(uniform_package_amount)
    if not _Cents.positive(amount):
        return {"status": "error", "message": "the amount must be a positive USD amount"}
    household = _Packet.household(ctx, activity_participation_id)
    today = ctx.now()[:10]
    rid = ctx.make_id("artsattire_", activity_participation_id, "uniform_package", uniform_package_amount)
    ctx.create("activity_ledger", rid, activity_ledger_id=rid, activity_participation_id=activity_participation_id,
               customer_id=household, event_type="activity_fee", amount=amount, posted_date=today,
               fee_component="uniform_package", equipment_tag="", payment_method="not_applicable",
               payment_reference="", credit_reason="not_applicable", source_activity_ledger_id="")
    return {"activity_ledger_id": rid, "activity_participation_id": activity_participation_id,
            "fee_component": "uniform_package", "amount": amount, "posted_date": today, "status": "posted"}


@tool(owner="user", rw="write")
def pay_arts_first_installment_d908e75f(ctx: ToolContext, activity_participation_id: str, payment_method: str,
                                        payment_amount: float) -> dict:
    """The parent or guardian pays the first installment of a Fine Arts Performing Ensemble payment plan themselves online.

    The family's own payment is applied to the participation's fee account as one payment entry
    dated today, lowering the household's amount due by the amount paid, and the participation is
    marked as paying on the installment plan. The family receives a payment confirmation number
    and sees the payment in the fee history.

    Args:
        activity_participation_id: Id class — reference number of the student's Fine Arts Performing Ensemble participation, as returned by the activity participation lookup.
        payment_method: Enum class — how the family pays online. online_card — the family pays with a debit or credit card in the online payment portal; ach_bank_draft — the family pays by bank draft from their checking account in the online payment portal.
        payment_amount: Fixed-format class — the amount paid, in USD, a positive amount with 2 decimal places, already rounded to the cent (half a cent rounds up); any further digits are rounded half up to the cent.

    Returns:
        A dictionary describing the payment: activity_ledger_id (string, reference number of the payment entry), activity_participation_id (string), payment_reference (string, the payment confirmation number as issued), payment_method (string, online_card or ach_bank_draft), amount (number, USD with 2 decimal places), posted_date (string, YYYY-MM-DD, today), installment_plan (boolean, true) and status (string, "paid" when the payment was applied). A malformed argument returns a dictionary whose status is "error" with a message and records nothing.
    """
    amount = _Cents.of(payment_amount)
    if payment_method not in ("online_card", "ach_bank_draft") or not _Cents.positive(amount):
        return {"status": "error", "message": "payment_method must be online_card or ach_bank_draft and payment_amount a positive USD amount"}
    household = _Packet.household(ctx, activity_participation_id)
    today = ctx.now()[:10]
    rid = ctx.make_id("artspay_", activity_participation_id, payment_method, payment_amount)
    reference = _Cents.receipt(rid)
    method = "ach_bank_draft" if payment_method == "ach_bank_draft" else "online_card"
    ctx.create("activity_ledger", rid, activity_ledger_id=rid, activity_participation_id=activity_participation_id,
               customer_id=household, event_type="activity_payment", amount=amount, posted_date=today,
               fee_component="not_applicable", equipment_tag="", payment_method=method,
               payment_reference=reference, credit_reason="not_applicable", source_activity_ledger_id="")
    ctx.update("activity_participations", activity_participation_id, installment_plan=True)
    return {"activity_ledger_id": rid, "activity_participation_id": activity_participation_id,
            "payment_reference": reference, "payment_method": method, "amount": amount, "posted_date": today,
            "installment_plan": True, "status": "paid"}

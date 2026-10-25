"""Task tools for the bus_eligibility_and_stops difficulty (Student Transportation Services, Calloway Creek ISD).

Hidden tools: each is reached through unlock_* -> call_* and performs one atomic write on one
transportation assignment. No tool judges eligibility, timing or amounts; every value is passed in.
"""

from decimal import Decimal, ROUND_HALF_UP

from erlbench import ToolContext, tool


class _Money:
    """Exact cent handling for amounts written by the tools below."""

    @staticmethod
    def cents(value) -> float:
        return float(Decimal(str(value)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP))

    @staticmethod
    def has_cents_only(value) -> bool:
        return Decimal(str(value)) == Decimal(str(value)).quantize(Decimal("0.01"))


@tool(owner="agent", rw="write")
def record_fee_correction_81e67279(ctx: ToolContext, transport_assignment_id: str, permit_fee_entry_id: str,
                                   adjustment_amount: float) -> str:
    """Post a billing correction credit against the courtesy rider permit fee of one student transportation assignment.

    The transportation office uses this to correct a permit fee that is already on the assignment's billing record:
    one credit entry is added to that assignment's billing history with the reason "billing correction", linked to
    the permit fee it corrects and dated today. The household's amount due on the assignment goes down by the
    credited amount; nothing else on the assignment changes. The correction then shows in the assignment's billing
    history as a credit against that permit fee.

    Args:
        transport_assignment_id: Id class — the reference number of the student's transportation assignment whose permit fee is corrected, as returned by the transportation assignment lookup.
        permit_fee_entry_id: Id class — the reference number of the courtesy rider permit fee entry being corrected, exactly as shown on that fee in the assignment's billing history lookup; it must be a permit fee entry of the same assignment.
        adjustment_amount: Fixed-format class — the correction credited against the permit fee, in US dollars, a positive amount with 2 decimal places (cents), already rounded to the cent by the caller; the tool records it exactly as given.

    Returns:
        A confirmation sentence (string) that names the new credit entry's reference number (an opaque id beginning
        with "tlc_"), the assignment reference number, the permit fee entry it is linked to, the credited amount in
        US dollars with two decimals and the posting date (YYYY-MM-DD). A message beginning with "Error:" means
        nothing was posted because an argument did not meet the format above.
    """
    if not _Money.has_cents_only(adjustment_amount) or float(adjustment_amount) <= 0:
        return "Error: adjustment_amount must be a positive US dollar amount with at most two decimal places."
    fees = ctx.find("transport_ledger", transport_ledger_id=permit_fee_entry_id)
    if not fees or fees[0].get("transport_assignment_id") != transport_assignment_id \
            or fees[0].get("event_type") != "transport_permit_fee":
        return "Error: permit_fee_entry_id must be a permit fee entry of the named transportation assignment."
    amount = _Money.cents(adjustment_amount)
    posted = ctx.now()[:10]
    rid = ctx.make_id("tlc_", transport_assignment_id, permit_fee_entry_id, amount)
    ctx.create("transport_ledger", rid, transport_ledger_id=rid, transport_assignment_id=transport_assignment_id,
               customer_id=fees[0].get("customer_id"), event_type="transport_fee_credit", amount=amount,
               posted_date=posted, fee_period_label="not_applicable", pass_number="",
               payment_method="not_applicable", payment_reference="", credit_reason="billing_correction",
               source_transport_ledger_id=permit_fee_entry_id)
    return (f"Billing correction credit {rid} posted on assignment {transport_assignment_id} against permit fee "
            f"{permit_fee_entry_id}: {amount:.2f} USD on {posted}.")


@tool(owner="user", rw="write")
def confirm_permit_cancellation_9706a650(ctx: ToolContext, transport_assignment_id: str, transport_request_id: str,
                                         permit_fee_entry_id: str, credit_amount: float) -> str:
    """Let the parent or guardian personally confirm the cancellation of their child's courtesy rider permit.

    Confirming cancels the student's transportation assignment today: its status becomes cancelled, today's date
    is recorded as the last day of service and the closing reason is recorded as the family's own cancellation. The
    family's pending permit cancellation request is marked completed. When the credit amount given is above zero, a
    credit entry with the reason "cancellation window" is added to the assignment's billing history, linked to the
    permit fee and dated today, lowering the household's amount due on the assignment; a credit amount of zero
    posts no credit entry. The family sees the permit as cancelled and, where one posted, the credit on the
    permit fee.

    Args:
        transport_assignment_id: Id class — the reference number of the student's transportation assignment being cancelled, as returned by the transportation assignment lookup.
        transport_request_id: Id class — the reference number of the family's pending permit cancellation request on that assignment, as returned by the transportation request lookup.
        permit_fee_entry_id: Id class — the reference number of the courtesy rider permit fee entry the credit is linked to, exactly as shown on that fee in the assignment's billing history lookup; it must be a permit fee entry of the same assignment.
        credit_amount: Fixed-format class — the cancellation credit in US dollars, zero or a positive amount with 2 decimal places (cents), already rounded to the cent; zero means no credit entry is posted.

    Returns:
        A confirmation sentence (string) that states the assignment reference number and its new status
        (cancelled), the last day of service (YYYY-MM-DD), the completed request reference number, and either the
        new credit entry's reference number (an opaque id beginning with "tlx_") with the credited amount in US
        dollars with two decimals, or that no credit entry was posted. A message beginning with "Error:" means
        nothing was changed because an argument did not meet the format above.
    """
    if not _Money.has_cents_only(credit_amount) or float(credit_amount) < 0:
        return "Error: credit_amount must be zero or a positive US dollar amount with at most two decimal places."
    rows = ctx.find("transport_assignments", transport_assignment_id=transport_assignment_id)
    if not rows:
        return "Error: no transportation assignment with that reference number."
    reqs = ctx.find("transport_requests", transport_request_id=transport_request_id)
    if not reqs or reqs[0].get("transport_assignment_id") != transport_assignment_id \
            or reqs[0].get("request_type") != "permit_cancellation" or reqs[0].get("request_status") != "received":
        return "Error: transport_request_id must be a pending (received) permit cancellation request of the named assignment."
    fees = ctx.find("transport_ledger", transport_ledger_id=permit_fee_entry_id)
    if not fees or fees[0].get("transport_assignment_id") != transport_assignment_id \
            or fees[0].get("event_type") != "transport_permit_fee":
        return "Error: permit_fee_entry_id must be a permit fee entry of the named transportation assignment."
    amount = _Money.cents(credit_amount)
    last_day = ctx.now()[:10]
    ctx.update("transport_assignments", transport_assignment_id, status="cancelled", end_date=last_day,
               end_reason="family_cancellation")
    ctx.update("transport_requests", transport_request_id, request_status="completed")
    credit_note = "no credit entry was posted"
    if amount > 0:
        rid = ctx.make_id("tlx_", transport_assignment_id, transport_request_id, permit_fee_entry_id, amount)
        ctx.create("transport_ledger", rid, transport_ledger_id=rid, transport_assignment_id=transport_assignment_id,
                   customer_id=rows[0].get("customer_id"), event_type="transport_fee_credit", amount=amount,
                   posted_date=last_day, fee_period_label="not_applicable", pass_number="",
                   payment_method="not_applicable", payment_reference="", credit_reason="cancellation_window",
                   source_transport_ledger_id=permit_fee_entry_id)
        credit_note = f"cancellation credit {rid} of {amount:.2f} USD posted against permit fee {permit_fee_entry_id}"
    return (f"Assignment {transport_assignment_id} is now cancelled; last day of service {last_day}; request "
            f"{transport_request_id} completed; {credit_note}.")


@tool(owner="user", rw="write")
def sign_seat_agreement_96917571(ctx: ToolContext, transport_assignment_id: str, permit_period: str,
                                 permit_fee_amount: float) -> str:
    """Let the parent or guardian personally sign the courtesy rider permit agreement that accepts a bus seat offered from the waiting list.

    Signing records the family's acceptance of the bus rules and of the seat fee: one courtesy rider permit fee
    entry for the stated permit period is added to the student's transportation assignment, dated today, and the
    household's amount due on the assignment goes up by that fee. The assignment's status, route and stops are
    not changed by signing. The family then sees the permit fee on the assignment's billing history.

    Args:
        transport_assignment_id: Id class — the reference number of the student's transportation assignment whose offered seat is being accepted, as returned by the transportation assignment lookup.
        permit_period: Enum class — the permit period the fee covers: "fall_semester" when the assignment is a Courtesy Rider Permit (Semester) for the August to December semester; "spring_semester" when it is a Courtesy Rider Permit (Semester) for the January to May semester; "school_year" when it is a Courtesy Rider Permit (Annual) covering August to May.
        permit_fee_amount: Fixed-format class — the seat fee the parent acknowledges, in US dollars, a positive amount with 2 decimal places (cents), already rounded to the cent; the tool records it exactly as given.

    Returns:
        A confirmation sentence (string) that names the new permit fee entry's reference number (an opaque id
        beginning with "tlf_"), the assignment reference number, the permit period, the fee in US dollars with two
        decimals and the posting date (YYYY-MM-DD). A message beginning with "Error:" means nothing was posted because
        an argument did not meet the format above.
    """
    if permit_period not in ("fall_semester", "spring_semester", "school_year"):
        return "Error: permit_period must be fall_semester, spring_semester or school_year."
    if not _Money.has_cents_only(permit_fee_amount) or float(permit_fee_amount) <= 0:
        return "Error: permit_fee_amount must be a positive US dollar amount with 2 decimal places."
    rows = ctx.find("transport_assignments", transport_assignment_id=transport_assignment_id)
    if not rows:
        return "Error: no transportation assignment with that reference number."
    amount = _Money.cents(permit_fee_amount)
    posted = ctx.now()[:10]
    period_code = {"fall_semester": "fall_semester", "spring_semester": "spring_semester",
                   "school_year": "school_year"}[permit_period]
    rid = ctx.make_id("tlf_", transport_assignment_id, permit_period, amount)
    ctx.create("transport_ledger", rid, transport_ledger_id=rid, transport_assignment_id=transport_assignment_id,
               customer_id=rows[0].get("customer_id"), event_type="transport_permit_fee", amount=amount,
               posted_date=posted, fee_period_label=period_code, pass_number="",
               payment_method="not_applicable", payment_reference="", credit_reason="not_applicable",
               source_transport_ledger_id="")
    return (f"Permit fee {rid} posted on assignment {transport_assignment_id} for {permit_period}: "
            f"{amount:.2f} USD on {posted}.")


@tool(owner="agent", rw="write")
def post_waiver_credit_eb03a46e(ctx: ToolContext, transport_assignment_id: str, permit_fee_entry_id: str,
                                waiver_level: str, waiver_amount: float) -> str:
    """Post a meal-status waiver credit against the courtesy rider permit fee of one student transportation assignment.

    The transportation office uses this to credit the part of a permit fee that a student's School Nutrition
    meal status waives: one credit entry is added to the assignment's billing history with the stated waiver
    reason, linked to the permit fee and dated today, and the household's amount due on the assignment goes down
    by the credited amount. Nothing else on the assignment changes. The waiver then shows as a credit against that
    permit fee in the billing history.

    Args:
        transport_assignment_id: Id class — the reference number of the student's transportation assignment whose permit fee is waived, as returned by the transportation assignment lookup.
        permit_fee_entry_id: Id class — the reference number of the courtesy rider permit fee entry being waived, exactly as shown on that fee in the assignment's billing history lookup; it must be a permit fee entry of the same assignment.
        waiver_level: Enum class — the meal benefit level the waiver rests on, which sets the credit's waiver reason: "free" when the student holds a Free Meal Status tier (reason free meal waiver); "reduced" when the student holds a Reduced-Price Meal Status tier (reason reduced-price meal waiver).
        waiver_amount: Fixed-format class — the waiver credited against the permit fee, in US dollars, a positive amount with 2 decimal places (cents), already rounded to the cent; the tool records it exactly as given.

    Returns:
        A confirmation sentence (string) that names the new credit entry's reference number (an opaque id beginning
        with "tlw_"), the assignment reference number, the permit fee entry it is linked to, the waiver reason (free_meal_waiver or reduced_meal_waiver), the
        credited amount in US dollars with two decimals and the posting date (YYYY-MM-DD). A message beginning with
        "Error:" means nothing was posted because an argument did not meet the format above.
    """
    if waiver_level not in ("free", "reduced"):
        return "Error: waiver_level must be free or reduced."
    if not _Money.has_cents_only(waiver_amount) or float(waiver_amount) <= 0:
        return "Error: waiver_amount must be a positive US dollar amount with 2 decimal places."
    fees = ctx.find("transport_ledger", transport_ledger_id=permit_fee_entry_id)
    if not fees or fees[0].get("transport_assignment_id") != transport_assignment_id \
            or fees[0].get("event_type") != "transport_permit_fee":
        return "Error: permit_fee_entry_id must be a permit fee entry of the named transportation assignment."
    amount = _Money.cents(waiver_amount)
    posted = ctx.now()[:10]
    reason = "free_meal_waiver" if waiver_level == "free" else "reduced_meal_waiver"
    rid = ctx.make_id("tlw_", transport_assignment_id, permit_fee_entry_id, waiver_level, amount)
    ctx.create("transport_ledger", rid, transport_ledger_id=rid, transport_assignment_id=transport_assignment_id,
               customer_id=fees[0].get("customer_id"), event_type="transport_fee_credit", amount=amount,
               posted_date=posted, fee_period_label="not_applicable", pass_number="",
               payment_method="not_applicable", payment_reference="", credit_reason=reason,
               source_transport_ledger_id=permit_fee_entry_id)
    return (f"Waiver credit {rid} ({reason}) posted on assignment {transport_assignment_id} against permit fee "
            f"{permit_fee_entry_id}: {amount:.2f} USD on {posted}.")

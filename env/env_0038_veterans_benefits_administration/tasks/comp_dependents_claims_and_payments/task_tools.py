"""Hidden task tools for the comp_dependents_claims_and_payments difficulty.

Every tool here performs one atomic write on the veteran's Disability Compensation records. The amount a
tool books is worked out beforehand from the published rules and passed in; no tool evaluates eligibility,
order or amounts on the caller's behalf.
"""

from erlbench import ToolContext, tool


@tool(owner="user", rw="write")
def request_payment_replacement_543b1fec(ctx: ToolContext, award_id: str, source_payment_id: str,
                                         payment_month: str, gross_amount: float) -> str:
    """The veteran personally requests a replacement for one Disability Compensation payment that the Treasury
    sent back, and the replacement is issued at once to the payment account now on the award.

    One call books one replacement entry on the award's payment history, linked to the payment that came back,
    for the entitlement month that payment covered, issued today with single-signature authorization. The
    replacement is deposited in full: nothing is withheld from it, so the amount deposited equals the gross
    amount given. Afterwards the payment history shows the replacement next to the returned payment, and the
    award's delivered total rises by the replacement amount.

    Args:
        award_id: Id class — the reference number of the veteran's Disability Compensation award, as shown on
            the award record returned by the compensation award lookup for this veteran.
        source_payment_id: Id class — the reference number of the original monthly payment that came back, as
            shown on the returned-payment entry (its source payment) in the award's payment history.
        payment_month: Fixed-format class — the entitlement month the original payment covered, written
            YYYY-MM exactly as on that payment entry (for example a payment for March 2026 is 2026-03).
        gross_amount: Fixed-format class — the gross amount of the replacement in USD, a positive amount with
            2 decimal places (cents), rounded half up to the cent; no currency sign or thousands separator.

    Returns:
        A dictionary receipt: status (always "replacement_issued" on success), payment_id (the reference
        number of the new replacement entry), source_payment_id (the payment it replaces), payment_month
        (YYYY-MM), payment_date (the issue date, YYYY-MM-DD), gross_amount and net_amount (USD, 2 decimal
        places, equal to each other).
    """
    gross = round(float(gross_amount), 2)
    award = (ctx.find("comp_awards", award_id=award_id) or [{}])[0]
    pid = ctx.make_id("cpr_", award_id, source_payment_id, payment_month, gross)
    today = ctx.now()[:10]
    ctx.create("comp_payments", pid, payment_id=pid, award_id=award_id, customer_id=award.get("customer_id", ""),
               event_type="comp_payment_reissued", payment_month=payment_month, payment_date=today,
               gross_amount=gross, offset_withheld_amount=0.0, attorney_fee_withheld_amount=0.0,
               net_amount=gross, offset_applied=False, source_payment_id=source_payment_id, decision_id="",
               retro_period_start="", retro_period_end="", return_reason="not_applicable",
               review_level="single_signature")
    return str({"status": "replacement_issued", "payment_id": pid, "source_payment_id": source_payment_id,
                "payment_month": payment_month, "payment_date": today, "gross_amount": gross,
                "net_amount": gross})


@tool(owner="agent", rw="write")
def release_dependency_past_due_602dcd04(ctx: ToolContext, award_id: str, retro_period_start: str,
                                         retro_period_end: str, gross_amount: float, review_level: str) -> str:
    """The representative releases, as one lump sum, the past-due dependent additions owed on a veteran's
    Disability Compensation award for entitlement months that were already paid without those additions.

    One call books one retroactive payment entry on the award, covering the span of entitlement months given,
    issued today and deposited to the payment account on the award. It is not linked to any rating decision,
    and nothing is withheld from it for a debt or a representative's fee, so the amount deposited equals the
    gross amount given. Afterwards the payment history shows the release with its span, and the award's
    delivered total rises by that amount.

    Args:
        award_id: Id class — the reference number of the veteran's Disability Compensation award, as shown on
            the award record returned by the compensation award lookup for this veteran.
        retro_period_start: Fixed-format class — the first entitlement month the release covers, written
            YYYY-MM as the months appear on the award's payment entries.
        retro_period_end: Fixed-format class — the last entitlement month the release covers, written YYYY-MM
            as the months appear on the award's payment entries.
        gross_amount: Fixed-format class — the total past-due amount released in USD, a positive amount with 2
            decimal places (cents), rounded half up to the cent; no currency sign or thousands separator.
        review_level: Enum class — the authorization the release carries: single_signature when one authorizer
            releases it on their own signature; second_signature when the release needs a second authorizer's
            signature before it goes out.

    Returns:
        A dictionary receipt: status (always "past_due_released" on success), payment_id (the reference number
        of the new release entry), retro_period_start and retro_period_end (YYYY-MM), payment_date (the issue
        date, YYYY-MM-DD), gross_amount and net_amount (USD, 2 decimal places, equal to each other) and
        review_level (as given).
    """
    gross = round(float(gross_amount), 2)
    award = (ctx.find("comp_awards", award_id=award_id) or [{}])[0]
    pid = ctx.make_id("cdr_", award_id, retro_period_start, retro_period_end, gross, review_level)
    today = ctx.now()[:10]
    ctx.create("comp_payments", pid, payment_id=pid, award_id=award_id, customer_id=award.get("customer_id", ""),
               event_type="comp_retro_payment", payment_month=retro_period_end, payment_date=today,
               gross_amount=gross, offset_withheld_amount=0.0, attorney_fee_withheld_amount=0.0,
               net_amount=gross, offset_applied=False, source_payment_id="", decision_id="",
               retro_period_start=retro_period_start, retro_period_end=retro_period_end,
               return_reason="not_applicable", review_level=review_level)
    return str({"status": "past_due_released", "payment_id": pid, "retro_period_start": retro_period_start,
                "retro_period_end": retro_period_end, "payment_date": today, "gross_amount": gross,
                "net_amount": gross, "review_level": review_level})


@tool(owner="agent", rw="write")
def release_decision_past_due_fbf191c5(ctx: ToolContext, award_id: str, decision_id: str, retro_period_start: str,
                                       retro_period_end: str, gross_amount: float, review_level: str) -> str:
    """The representative releases, as one lump sum, the past-due Disability Compensation that a favorable
    rating decision created for entitlement months the award had already paid at the earlier rate.

    One call books one retroactive payment entry on the award, linked to the rating decision given and
    covering the span of entitlement months given, issued today and deposited to the payment account on the
    award. Nothing is withheld from it for a debt or a representative's fee, so the amount deposited equals
    the gross amount given. Afterwards the payment history shows the release under that decision, and the
    award's delivered total rises by that amount.

    Args:
        award_id: Id class — the reference number of the veteran's Disability Compensation award, as shown on
            the award record returned by the compensation award lookup for this veteran.
        decision_id: Id class — the reference number of the rating decision whose past-due amount is
            released, as shown on that decision in the award's rating-decision history.
        retro_period_start: Fixed-format class — the first entitlement month the release covers, written
            YYYY-MM as the months appear on the award's payment entries.
        retro_period_end: Fixed-format class — the last entitlement month the release covers, written YYYY-MM
            as the months appear on the award's payment entries.
        gross_amount: Fixed-format class — the total past-due amount released in USD, a positive amount with 2
            decimal places (cents), rounded half up to the cent; no currency sign or thousands separator.
        review_level: Enum class — the authorization the release carries: single_signature when one authorizer
            releases it on their own signature; second_signature when the release needs a second authorizer's
            signature before it goes out.

    Returns:
        A dictionary receipt: status (always "past_due_released" on success), payment_id (the reference number
        of the new release entry), decision_id (as given), retro_period_start and retro_period_end (YYYY-MM),
        payment_date (the issue date, YYYY-MM-DD), gross_amount and net_amount (USD, 2 decimal places, equal to
        each other) and review_level (as given).
    """
    gross = round(float(gross_amount), 2)
    award = (ctx.find("comp_awards", award_id=award_id) or [{}])[0]
    pid = ctx.make_id("cdp_", award_id, decision_id, retro_period_start, retro_period_end, gross, review_level)
    today = ctx.now()[:10]
    ctx.create("comp_payments", pid, payment_id=pid, award_id=award_id, customer_id=award.get("customer_id", ""),
               event_type="comp_retro_payment", payment_month=retro_period_end, payment_date=today,
               gross_amount=gross, offset_withheld_amount=0.0, attorney_fee_withheld_amount=0.0,
               net_amount=gross, offset_applied=False, source_payment_id="", decision_id=decision_id,
               retro_period_start=retro_period_start, retro_period_end=retro_period_end,
               return_reason="not_applicable", review_level=review_level)
    return str({"status": "past_due_released", "payment_id": pid, "decision_id": decision_id,
                "retro_period_start": retro_period_start, "retro_period_end": retro_period_end,
                "payment_date": today, "gross_amount": gross, "net_amount": gross, "review_level": review_level})


@tool(owner="agent", rw="write")
def release_switch_past_due_a8e85818(ctx: ToolContext, award_id: str, decision_id: str, retro_period_start: str,
                                     retro_period_end: str, gross_amount: float, review_level: str) -> str:
    """The representative releases, as one lump sum, the past-due Disability Compensation for the months before a
    newly payable award began running, together with what the award's later months still lack, net of any Veterans
    Pension already paid for the same months.

    One call books one retroactive payment entry on the compensation award, linked to the rating decision that
    made compensation payable and covering the span of entitlement months given, issued today and deposited to
    the payment account on the award. Nothing is withheld from it for a debt or a representative's fee, so the
    amount deposited equals the gross amount given. Afterwards the payment history shows the release under that
    decision, and the award's delivered total rises by that amount; no pension or debt record is changed.

    Args:
        award_id: Id class — the reference number of the veteran's Disability Compensation award, as shown on
            the award record returned by the compensation award lookup for this veteran.
        decision_id: Id class — the reference number of the rating decision that granted the compensation now
            payable, as shown on that decision in the award's rating-decision history.
        retro_period_start: Fixed-format class — the first entitlement month the release covers, written
            YYYY-MM as the months appear on the veteran's payment entries.
        retro_period_end: Fixed-format class — the last entitlement month the release covers, written YYYY-MM
            as the months appear on the veteran's payment entries.
        gross_amount: Fixed-format class — the total past-due amount released in USD, a positive amount with 2
            decimal places (cents), rounded half up to the cent; no currency sign or thousands separator.
        review_level: Enum class — the authorization the release carries: single_signature when one authorizer
            releases it on their own signature; second_signature when the release needs a second authorizer's
            signature before it goes out.

    Returns:
        A dictionary receipt: status (always "past_due_released" on success), payment_id (the reference number
        of the new release entry), decision_id (as given), retro_period_start and retro_period_end (YYYY-MM),
        payment_date (the issue date, YYYY-MM-DD), gross_amount and net_amount (USD, 2 decimal places, equal to
        each other) and review_level (as given).
    """
    gross = round(float(gross_amount), 2)
    award = (ctx.find("comp_awards", award_id=award_id) or [{}])[0]
    pid = ctx.make_id("csp_", award_id, decision_id, retro_period_start, retro_period_end, gross, review_level)
    today = ctx.now()[:10]
    ctx.create("comp_payments", pid, payment_id=pid, award_id=award_id, customer_id=award.get("customer_id", ""),
               event_type="comp_retro_payment", payment_month=retro_period_end, payment_date=today,
               gross_amount=gross, offset_withheld_amount=0.0, attorney_fee_withheld_amount=0.0,
               net_amount=gross, offset_applied=False, source_payment_id="", decision_id=decision_id,
               retro_period_start=retro_period_start, retro_period_end=retro_period_end,
               return_reason="not_applicable", review_level=review_level)
    return str({"status": "past_due_released", "payment_id": pid, "decision_id": decision_id,
                "retro_period_start": retro_period_start, "retro_period_end": retro_period_end,
                "payment_date": today, "gross_amount": gross, "net_amount": gross, "review_level": review_level})


@tool(owner="user", rw="write")
def resume_award_release_withheld_86166e35(ctx: ToolContext, award_id: str, retro_period_start: str,
                                           retro_period_end: str, gross_amount: float) -> str:
    """The veteran personally confirms, on this contact, the payment account now on a suspended Disability
    Compensation award; the confirmation resumes the award and releases at once, as one lump sum, the entitlement
    months the suspension left unpaid.

    One call changes the award's status from suspended to running and clears its suspension reason, and books one
    retroactive payment entry on the award covering the span of entitlement months given, issued today to the
    payment account on the award, single-signature, linked to no rating decision and with nothing withheld, so the
    amount deposited equals the gross amount given. Afterwards the award shows as running, monthly payments resume
    on the normal schedule, and the payment history shows the release.

    Args:
        award_id: Id class — the reference number of the veteran's Disability Compensation award, as shown on the
            award record returned by the compensation award lookup for this veteran.
        retro_period_start: Fixed-format class — the first entitlement month the release covers, written YYYY-MM
            as the months appear on the award's payment entries.
        retro_period_end: Fixed-format class — the last entitlement month the release covers, written YYYY-MM;
            a month for which no payment entry exists yet is written the same way (for example 2026-09).
        gross_amount: Fixed-format class — the total amount released in USD, a positive amount with 2 decimal
            places (cents), rounded half up to the cent; no currency sign or thousands separator.

    Returns:
        A dictionary receipt: status (always "award_resumed" on success), award_status (always "running"),
        payment_id (the reference number of the new release entry), retro_period_start and retro_period_end
        (YYYY-MM), payment_date (the issue date, YYYY-MM-DD), gross_amount and net_amount (USD, 2 decimal places,
        equal to each other).
    """
    gross = round(float(gross_amount), 2)
    award = (ctx.find("comp_awards", award_id=award_id) or [{}])[0]
    ctx.update("comp_awards", award_id, status="running", suspension_reason="none")
    pid = ctx.make_id("crs_", award_id, retro_period_start, retro_period_end, gross)
    today = ctx.now()[:10]
    ctx.create("comp_payments", pid, payment_id=pid, award_id=award_id, customer_id=award.get("customer_id", ""),
               event_type="comp_retro_payment", payment_month=retro_period_end, payment_date=today,
               gross_amount=gross, offset_withheld_amount=0.0, attorney_fee_withheld_amount=0.0,
               net_amount=gross, offset_applied=False, source_payment_id="", decision_id="",
               retro_period_start=retro_period_start, retro_period_end=retro_period_end,
               return_reason="not_applicable", review_level="single_signature")
    return str({"status": "award_resumed", "award_status": "running", "payment_id": pid,
                "retro_period_start": retro_period_start, "retro_period_end": retro_period_end,
                "payment_date": today, "gross_amount": gross, "net_amount": gross})


@tool(owner="agent", rw="write")
def release_temporary_total_past_due_0acb107c(ctx: ToolContext, award_id: str, decision_id: str,
                                              retro_period_start: str, retro_period_end: str,
                                              gross_amount: float, review_level: str) -> str:
    """The representative releases, as one lump sum, the past-due Disability Compensation that a temporary total
    rating created for entitlement months the award had already paid at its regular rate.

    One call books one retroactive payment entry on the award, linked to the temporary total rating decision given
    and covering the span of entitlement months given, issued today to the payment account on the award, with
    nothing withheld for a debt or a representative's fee, so the amount deposited equals the gross amount given.
    Afterwards the payment history shows the release under that decision and the award's delivered total rises by
    that amount.

    Args:
        award_id: Id class — the reference number of the veteran's Disability Compensation award, as shown on the
            award record returned by the compensation award lookup for this veteran.
        decision_id: Id class — the reference number of the temporary total rating decision whose past-due amount
            is released, as shown on that decision in the award's rating-decision history.
        retro_period_start: Fixed-format class — the first entitlement month the release covers, written YYYY-MM
            as the months appear on the award's payment entries.
        retro_period_end: Fixed-format class — the last entitlement month the release covers, written YYYY-MM as
            the months appear on the award's payment entries.
        gross_amount: Fixed-format class — the total past-due amount released in USD, a positive amount with 2
            decimal places (cents), rounded half up to the cent; no currency sign or thousands separator.
        review_level: Enum class — the authorization the release carries: single_signature when one authorizer
            releases it on their own signature; second_signature when the release needs a second authorizer's
            signature before it goes out.

    Returns:
        A dictionary receipt: status (always "past_due_released" on success), payment_id (the reference number of
        the new release entry), decision_id (as given), retro_period_start and retro_period_end (YYYY-MM),
        payment_date (the issue date, YYYY-MM-DD), gross_amount and net_amount (USD, 2 decimal places, equal to each
        other) and review_level (as given).
    """
    gross = round(float(gross_amount), 2)
    award = (ctx.find("comp_awards", award_id=award_id) or [{}])[0]
    pid = ctx.make_id("ctt_", award_id, decision_id, retro_period_start, retro_period_end, gross, review_level)
    today = ctx.now()[:10]
    ctx.create("comp_payments", pid, payment_id=pid, award_id=award_id, customer_id=award.get("customer_id", ""),
               event_type="comp_retro_payment", payment_month=retro_period_end, payment_date=today,
               gross_amount=gross, offset_withheld_amount=0.0, attorney_fee_withheld_amount=0.0,
               net_amount=gross, offset_applied=False, source_payment_id="", decision_id=decision_id,
               retro_period_start=retro_period_start, retro_period_end=retro_period_end,
               return_reason="not_applicable", review_level=review_level)
    return str({"status": "past_due_released", "payment_id": pid, "decision_id": decision_id,
                "retro_period_start": retro_period_start, "retro_period_end": retro_period_end,
                "payment_date": today, "gross_amount": gross, "net_amount": gross, "review_level": review_level})


@tool(owner="agent", rw="write")
def release_review_restoration_92058ca9(ctx: ToolContext, award_id: str, decision_id: str,
                                        retro_period_start: str, retro_period_end: str,
                                        gross_amount: float, review_level: str) -> str:
    """The representative releases, as one lump sum, the Disability Compensation that a rating reduction withheld
    after a decision review overturned that reduction.

    One call books one retroactive payment entry on the award, linked to the reduction decision that was
    overturned and covering the span of entitlement months given, issued today to the payment account on the award,
    with nothing withheld for a debt or a representative's fee, so the amount deposited equals the gross amount
    given. Afterwards the payment history shows the restoration under that reduction decision and the award's
    delivered total rises by that amount.

    Args:
        award_id: Id class — the reference number of the veteran's Disability Compensation award, as shown on the
            award record returned by the compensation award lookup for this veteran.
        decision_id: Id class — the reference number of the reduction decision the review overturned, as shown on
            that decision in the award's rating-decision history.
        retro_period_start: Fixed-format class — the first entitlement month the restoration covers, written
            YYYY-MM as the months appear on the award's payment entries.
        retro_period_end: Fixed-format class — the last entitlement month the restoration covers, written YYYY-MM;
            a month for which no payment entry exists yet is written the same way (for example 2026-09).
        gross_amount: Fixed-format class — the total amount restored in USD, a positive amount with 2 decimal
            places (cents), rounded half up to the cent; no currency sign or thousands separator.
        review_level: Enum class — the authorization the release carries: single_signature when one authorizer
            releases it on their own signature; second_signature when the release needs a second authorizer's
            signature before it goes out.

    Returns:
        A dictionary receipt: status (always "restoration_released" on success), payment_id (the reference number
        of the new release entry), decision_id (as given), retro_period_start and retro_period_end (YYYY-MM),
        payment_date (the issue date, YYYY-MM-DD), gross_amount and net_amount (USD, 2 decimal places, equal to each
        other) and review_level (as given).
    """
    gross = round(float(gross_amount), 2)
    award = (ctx.find("comp_awards", award_id=award_id) or [{}])[0]
    pid = ctx.make_id("crr_", award_id, decision_id, retro_period_start, retro_period_end, gross, review_level)
    today = ctx.now()[:10]
    ctx.create("comp_payments", pid, payment_id=pid, award_id=award_id, customer_id=award.get("customer_id", ""),
               event_type="comp_retro_payment", payment_month=retro_period_end, payment_date=today,
               gross_amount=gross, offset_withheld_amount=0.0, attorney_fee_withheld_amount=0.0,
               net_amount=gross, offset_applied=False, source_payment_id="", decision_id=decision_id,
               retro_period_start=retro_period_start, retro_period_end=retro_period_end,
               return_reason="not_applicable", review_level=review_level)
    return str({"status": "restoration_released", "payment_id": pid, "decision_id": decision_id,
                "retro_period_start": retro_period_start, "retro_period_end": retro_period_end,
                "payment_date": today, "gross_amount": gross, "net_amount": gross, "review_level": review_level})

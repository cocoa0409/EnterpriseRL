"""Hidden task tools for the maturity_due_and_payable_cases difficulty of env_0064_reverse_mortgage_lender.

Each tool performs one atomic business write on a maturity case and is reached only through the
unlock/call meta-tools, by the name its extended policy registers as target_tool.
"""

from erlbench import ToolContext, tool


class _CalendarDays:
    """Pure calendar arithmetic on YYYY-MM-DD strings (proleptic Gregorian calendar)."""

    @staticmethod
    def to_ordinal(day: str) -> int:
        y, m, d = (int(p) for p in str(day)[:10].split("-"))
        y -= 1 if m <= 2 else 0
        era = (y if y >= 0 else y - 399) // 400
        yoe = y - era * 400
        doy = (153 * (m + (-3 if m > 2 else 9)) + 2) // 5 + d - 1
        doe = yoe * 365 + yoe // 4 - yoe // 100 + doy
        return era * 146097 + doe - 719468

    @staticmethod
    def from_ordinal(n: int) -> str:
        z = int(n) + 719468
        era = (z if z >= 0 else z - 146096) // 146097
        doe = z - era * 146097
        yoe = (doe - doe // 1460 + doe // 36524 - doe // 146096) // 365
        y = yoe + era * 400
        doy = doe - (365 * yoe + yoe // 4 - yoe // 100)
        mp = (5 * doy + 2) // 153
        d = doy - (153 * mp + 2) // 5 + 1
        m = mp + (3 if mp < 10 else -9)
        y += 1 if m <= 2 else 0
        return f"{y:04d}-{m:02d}-{d:02d}"

    @staticmethod
    def add(day: str, days: int) -> str:
        return _CalendarDays.from_ordinal(_CalendarDays.to_ordinal(day) + int(days))

    @staticmethod
    def record_time(stamp: str) -> str:
        """The clock reading as a YYYY-MM-DDTHH:MM:SS record time, the format the request records carry."""
        text = str(stamp)
        return text[:10] + "T" + text[11:19]


@tool(owner="agent", rw="write")
def reclassify_case_to_death_eeacbce3(ctx: ToolContext, maturity_case_id: str, event_date: str,
                                      runway_days_added: int) -> str:
    """Reclassify an open maturity case to the Death of Last Surviving Borrower plan and carry its resolution deadline forward by the successor runway.

    The agent uses this on a maturity case whose borrower has died while the case was open for another
    maturity event. One call changes the case's maturity event type to Death of Last Surviving Borrower,
    replaces the case's event date with the date of death supplied, and moves the case's resolution
    deadline later by the number of runway days supplied (a value of 0 leaves it where it is). The case
    keeps its status, its due-and-payable date and its response deadline. The case lookup shows
    the new event type, event date and resolution deadline. The call succeeds when the receipt names the
    case and shows the new event type.

    Args:
        maturity_case_id: Id class — reference number of the open maturity case being reclassified, as returned by the maturity case lookup for the deceased borrower.
        event_date: Fixed-format class — the borrower's date of death that becomes the case's event date, written as a calendar date in YYYY-MM-DD form with no time and no time zone; it may not be empty.
        runway_days_added: Fixed-format class — whole number of calendar days by which the case's current resolution deadline is moved later, an integer of 0 or more with no unit text and no decimals.

    Returns:
        A text rendering of a dictionary with these fields: maturity_case_id (text, the case reference
        number), variant_name (text, the case's resulting maturity event type), event_date (text,
        YYYY-MM-DD, the case's resulting event date), previous_resolution_deadline (text, YYYY-MM-DD,
        the resolution deadline the case carried when the call was made), resolution_deadline (text,
        YYYY-MM-DD, the case's resulting resolution deadline) and runway_days_added (integer, the days applied). A receipt carrying the
        case reference number and variant_name Death of Last Surviving Borrower means the reclassification
        is recorded.
    """
    rows = ctx.find("maturity_cases", maturity_case_id=maturity_case_id)
    if not rows:
        return f"Error: no maturity case {maturity_case_id}."
    case = rows[0]
    previous = case.get("resolution_deadline") or ""
    moved = _CalendarDays.add(previous, int(runway_days_added)) if previous else previous
    ctx.update("maturity_cases", maturity_case_id, variant_name="Death of Last Surviving Borrower",
               event_date=str(event_date)[:10], resolution_deadline=moved)
    return str({"maturity_case_id": maturity_case_id, "variant_name": "Death of Last Surviving Borrower",
                "event_date": str(event_date)[:10], "previous_resolution_deadline": previous,
                "resolution_deadline": moved, "runway_days_added": int(runway_days_added)})


@tool(owner="agent", rw="write")
def mail_successor_due_notices_bb6e23d7(ctx: ToolContext, maturity_case_id: str, recipient_customer_id: str,
                                        response_window_days: int) -> str:
    """Mail a deceased borrower's successor the due-and-payable notice and the successor options letter for a maturity case and set the case's response deadline.

    The agent uses this to send one successor in interest the two case notices on today's date. One call
    records a due-and-payable notice and a successor options letter addressed to that person, both dated
    today, and sets the case's response deadline to today's date moved later by the response window days
    supplied. The case history lookup shows both notices for the recipient and the case lookup
    shows the new response deadline. The call succeeds when the receipt lists both notice references.

    Args:
        maturity_case_id: Id class — reference number of the maturity case the notices concern, as returned by the maturity case lookup.
        recipient_customer_id: Id class — customer reference number of the successor in interest the notices are addressed to, as returned by the customer lookup.
        response_window_days: Fixed-format class — whole number of calendar days from today's date to the successor's response deadline, an integer of 1 or more with no unit text and no decimals.

    Returns:
        A text rendering of a dictionary with these fields: maturity_case_id (text), recipient_customer_id
        (text), notice_references (list of two texts: the reference of the due-and-payable notice entry and
        of the successor options letter entry), mailing_date (text, YYYY-MM-DD, today's date) and
        response_deadline (text, YYYY-MM-DD, the case's resulting response deadline). A receipt with
        two notice references means both notices are recorded as mailed.
    """
    rows = ctx.find("maturity_cases", maturity_case_id=maturity_case_id)
    if not rows:
        return f"Error: no maturity case {maturity_case_id}."
    case = rows[0]
    today = ctx.now()[:10]
    refs = []
    for notice_type in ("due_and_payable_notice", "successor_options_letter"):
        rid = ctx.make_id("mev_", maturity_case_id, recipient_customer_id, notice_type, today,
                          int(response_window_days))
        ctx.create("maturity_case_events", rid, maturity_event_id=rid, maturity_case_id=maturity_case_id,
                   customer_id=case.get("customer_id"), event_type="maturity_notice_sent",
                   effective_date=today, hud_action="not_applicable", notice_type=notice_type,
                   recipient_customer_id=recipient_customer_id, extension_number=0,
                   extended_deadline="", maturity_request_id=None)
        refs.append(rid)
    deadline = _CalendarDays.add(today, int(response_window_days))
    ctx.update("maturity_cases", maturity_case_id, response_deadline=deadline)
    return str({"maturity_case_id": maturity_case_id, "recipient_customer_id": recipient_customer_id,
                "notice_references": refs, "mailing_date": today, "response_deadline": deadline})


@tool(owner="user", rw="write")
def declare_successor_intent_94ee6efc(ctx: ToolContext, maturity_case_id: str, customer_id: str,
                                      stated_intent: str, evidence_due_days: int) -> str:
    """File the caller's own declaration of how a deceased borrower's loan will be resolved, and record it on the maturity case.

    The successor in interest runs this in person. One call files an intent declaration from that person
    for the maturity case, dated today and marked accepted, and records the declared intent on the case
    with the declarant as the person acting on the case. The declaration carries an evidence due date:
    today's date moved later by the evidence due days supplied, the date by which the declarant's listing
    agreement or financing commitment is to be on file; that date is printed on the declaration receipt and
    the evidence due days form part of the declaration's reference number. The case lookup shows the
    recorded intent and declarant, and the request lookup shows the declaration. The call succeeds when the
    receipt carries a declaration reference number.

    Args:
        maturity_case_id: Id class — reference number of the deceased borrower's maturity case, as the agent reads it from the maturity case lookup and gives it to the declarant.
        customer_id: Id class — customer reference number of the declarant (the successor in interest making the declaration), as the agent reads it from the customer lookup and gives it to the declarant.
        stated_intent: Enum class — the resolution the declarant chooses, exactly one of: retain_property (the declarant will keep the home by paying the loan off), sell_property (the declarant will sell the home and repay the loan from the sale), deed_in_lieu (the declarant will hand the home to Cedarline by deed in lieu of foreclosure).
        evidence_due_days: Fixed-format class — whole number of calendar days from today's date to the evidence due date printed on the declaration, an integer of 1 or more with no unit text and no decimals.

    Returns:
        A text rendering of a dictionary with these fields: maturity_request_id (text, the declaration's
        reference number), maturity_case_id (text), stated_intent (text, the intent declared and recorded),
        declarant_customer_id (text, the person now recorded as acting on the case), declaration_date (text,
        YYYY-MM-DD, today's date) and evidence_due_date (text, YYYY-MM-DD, the evidence due date printed on
        the declaration). A receipt with a declaration reference number means the declaration is filed and
        recorded on the case.
    """
    rows = ctx.find("maturity_cases", maturity_case_id=maturity_case_id)
    if not rows:
        return f"Error: no maturity case {maturity_case_id}."
    today = ctx.now()[:10]
    rid = ctx.make_id("mrq_", maturity_case_id, customer_id, stated_intent, int(evidence_due_days))
    ctx.create("maturity_requests", rid, maturity_request_id=rid, customer_id=customer_id,
               maturity_case_id=maturity_case_id, request_type="intent_declaration",
               stated_intent=stated_intent, evidence_type="not_applicable", evidence_reference="",
               evidence_date="", request_date=today, request_status="accepted",
               decline_reason="not_applicable", created_at=_CalendarDays.record_time(ctx.now()))
    ctx.update("maturity_cases", maturity_case_id, successor_customer_id=customer_id,
               successor_intent=stated_intent)
    return str({"maturity_request_id": rid, "maturity_case_id": maturity_case_id,
                "stated_intent": stated_intent, "declarant_customer_id": customer_id,
                "declaration_date": today,
                "evidence_due_date": _CalendarDays.add(today, int(evidence_due_days))})


@tool(owner="agent", rw="write")
def grant_first_extension_77f15011(ctx: ToolContext, maturity_case_id: str, maturity_request_id: str,
                                   recipient_customer_id: str, extension_number: int, extension_days: int) -> str:
    """Grant the extension that opens a maturity case's extension period against an extension request, and mail the extension letter.

    The agent uses this to book the extension that takes a case from due and payable into its extension
    period. One call records the extension, under the extension number supplied, against the extension
    request named, moves the case into its extension period with its resolution deadline
    moved later by the extension days supplied, marks the extension request accepted, and records an
    extension letter dated today addressed to the person named. The case lookup shows status
    extension_period and the extended resolution deadline, and the case history lookup shows the extension
    and the letter. The call succeeds when the receipt shows the extended deadline.

    Args:
        maturity_case_id: Id class — reference number of the maturity case whose resolution deadline is extended, as returned by the maturity case lookup.
        maturity_request_id: Id class — reference number of the extension request the extension is granted against, as returned by the maturity request lookup.
        recipient_customer_id: Id class — customer reference number of the person acting on the case who receives the extension letter, as returned by the customer lookup.
        extension_number: Fixed-format class — sequence number of this extension on the case, written as an integer, 1-based, counting every extension the case has been granted including this one.
        extension_days: Fixed-format class — whole number of calendar days by which the case's current resolution deadline is moved later, an integer of 0 or more with no unit text and no decimals.

    Returns:
        A text rendering of a dictionary with these fields: maturity_case_id (text), extension_reference
        (text, the reference of the extension entry), letter_reference (text, the reference of the
        extension letter entry), extension_number (integer, the sequence number recorded), previous_resolution_deadline (text,
        YYYY-MM-DD, the deadline the case carried when the call was made), extended_deadline (text,
        YYYY-MM-DD, the case's resulting resolution deadline) and status (text, extension_period). A receipt
        showing the extended deadline means the extension is granted and the letter recorded.
    """
    rows = ctx.find("maturity_cases", maturity_case_id=maturity_case_id)
    if not rows:
        return f"Error: no maturity case {maturity_case_id}."
    case = rows[0]
    today = ctx.now()[:10]
    previous = case.get("resolution_deadline") or ""
    extended = _CalendarDays.add(previous, int(extension_days)) if previous else previous
    ext_id = ctx.make_id("mev_", maturity_case_id, maturity_request_id, int(extension_number), int(extension_days))
    ctx.create("maturity_case_events", ext_id, maturity_event_id=ext_id, maturity_case_id=maturity_case_id,
               customer_id=case.get("customer_id"), event_type="maturity_extension_granted",
               effective_date=today, hud_action="not_applicable", notice_type="not_applicable",
               recipient_customer_id=None, extension_number=int(extension_number), extended_deadline=extended,
               maturity_request_id=maturity_request_id)
    letter_id = ctx.make_id("mev_", maturity_case_id, recipient_customer_id, "extension_letter", today,
                            int(extension_number), int(extension_days))
    ctx.create("maturity_case_events", letter_id, maturity_event_id=letter_id, maturity_case_id=maturity_case_id,
               customer_id=case.get("customer_id"), event_type="maturity_notice_sent",
               effective_date=today, hud_action="not_applicable", notice_type="extension_letter",
               recipient_customer_id=recipient_customer_id, extension_number=0, extended_deadline="",
               maturity_request_id="")
    ctx.update("maturity_cases", maturity_case_id, status="extension_period", resolution_deadline=extended)
    ctx.update("maturity_requests", maturity_request_id, request_status="accepted")
    return str({"maturity_case_id": maturity_case_id, "extension_reference": ext_id,
                "letter_reference": letter_id, "extension_number": int(extension_number),
                "previous_resolution_deadline": previous, "extended_deadline": extended,
                "status": "extension_period"})


@tool(owner="user", rw="write")
def supplement_extension_request_11bdc0c2(ctx: ToolContext, maturity_case_id: str, maturity_request_id: str,
                                          customer_id: str, evidence_type: str, evidence_reference: str,
                                          evidence_date: str, requested_extension_days: int) -> str:
    """Re-file the caller's own pending extension request on a maturity case with new supporting evidence.

    The borrower or confirmed successor runs this in person. One call files a new extension request from
    the caller for the same case, in place of the pending request named, dated today, status received,
    carrying the supporting document supplied and the number of extension days asked for; the earlier
    request is left on file unchanged. The requested extension days form part of the new request's
    reference number and are printed on the receipt together with the deadline they would reach. The
    request lookup shows the new request next to the earlier one. The call succeeds when the receipt carries
    the new request's reference number.

    Args:
        maturity_case_id: Id class — reference number of the maturity case, as the agent reads it from the maturity case lookup and gives it to the caller.
        maturity_request_id: Id class — reference number of the caller's pending extension request this filing takes the place of, as the agent reads it from the maturity request lookup and gives it to the caller.
        customer_id: Id class — the caller's own customer reference number, as the agent reads it from the customer lookup and gives it to the caller.
        evidence_type: Enum class — kind of supporting document, exactly one of: listing_agreement (a signed listing agreement with a real estate broker), financing_commitment (a lender's written financing commitment for the purchase or refinance), reoccupancy_certification (a borrower's certification of moving back in; not evidence for an extension), repayment_receipt (a receipt for repaid property-charge advances; not evidence for an extension), repair_inspection (a passing repair inspection report; not evidence for an extension), recorded_deed (a recorded deed; not evidence for an extension), failed_condition_inspection (a failed condition inspection report; not evidence for an extension), not_applicable (no supporting document at all).
        evidence_reference: Verbatim class — the reference printed on the supporting document (commitment letter number or listing agreement number) exactly as the caller reads it from the document, copied character for character with its letters, digits and punctuation unchanged (verbatim).
        evidence_date: Fixed-format class — the date printed on the supporting document, written as a calendar date in YYYY-MM-DD form with no time and no time zone.
        requested_extension_days: Fixed-format class — whole number of calendar days the request asks to add to the case's current resolution deadline, an integer of 0 or more with no unit text and no decimals.

    Returns:
        A text rendering of a dictionary with these fields: maturity_request_id (text, the new request's
        reference number), replaced_request_id (text, the earlier request this filing takes the place of), maturity_case_id
        (text), request_date (text, YYYY-MM-DD, today's date), evidence_type (text), evidence_reference (text),
        evidence_date (text, YYYY-MM-DD), requested_extension_days (integer) and requested_through_date
        (text, YYYY-MM-DD, the case's current resolution deadline moved later by the requested days). A
        receipt with a new request reference number means the request is filed and awaiting a decision.
    """
    rows = ctx.find("maturity_cases", maturity_case_id=maturity_case_id)
    if not rows:
        return f"Error: no maturity case {maturity_case_id}."
    case = rows[0]
    today = ctx.now()[:10]
    rid = ctx.make_id("mrq_", maturity_case_id, maturity_request_id, customer_id, evidence_type,
                      evidence_reference, str(evidence_date)[:10], int(requested_extension_days))
    ctx.create("maturity_requests", rid, maturity_request_id=rid, customer_id=customer_id,
               maturity_case_id=maturity_case_id, request_type="extension_request",
               stated_intent="not_applicable", evidence_type=evidence_type,
               evidence_reference=evidence_reference, evidence_date=str(evidence_date)[:10],
               request_date=today, request_status="received", decline_reason="not_applicable",
               created_at=_CalendarDays.record_time(ctx.now()))
    deadline = case.get("resolution_deadline") or ""
    through = _CalendarDays.add(deadline, int(requested_extension_days)) if deadline else deadline
    return str({"maturity_request_id": rid, "replaced_request_id": maturity_request_id,
                "maturity_case_id": maturity_case_id, "request_date": today, "evidence_type": evidence_type,
                "evidence_reference": evidence_reference, "evidence_date": str(evidence_date)[:10],
                "requested_extension_days": int(requested_extension_days), "requested_through_date": through})


@tool(owner="agent", rw="write")
def grant_further_extension_50c8b1d2(ctx: ToolContext, maturity_case_id: str, maturity_request_id: str,
                                     recipient_customer_id: str, extension_number: int, extension_days: int) -> str:
    """Grant a further extension of the resolution deadline of a maturity case already in its extension period, and mail the extension letter.

    The agent uses this on a case whose extension period is running. One call records the extension, under
    the extension number supplied, against the extension request named, moves the case's resolution
    deadline later by the extension days supplied (the case stays in its extension period), marks the
    extension request accepted, and records an extension letter dated today addressed to the person named.
    The case lookup shows the extended resolution deadline and the case history lookup shows the extension
    and the letter. The call succeeds when the receipt shows the extended deadline.

    Args:
        maturity_case_id: Id class — reference number of the maturity case whose resolution deadline is extended, as returned by the maturity case lookup.
        maturity_request_id: Id class — reference number of the extension request the extension is granted against, as returned by the maturity request lookup or by the receipt of the request's filing.
        recipient_customer_id: Id class — customer reference number of the person acting on the case who receives the extension letter, as returned by the customer lookup.
        extension_number: Fixed-format class — sequence number of this extension on the case, written as an integer, 1-based, counting every extension the case has been granted including this one.
        extension_days: Fixed-format class — whole number of calendar days by which the case's current resolution deadline is moved later, an integer of 0 or more with no unit text and no decimals.

    Returns:
        A text rendering of a dictionary with these fields: maturity_case_id (text), extension_reference
        (text, the reference of the extension entry), letter_reference (text, the reference of the
        extension letter entry), extension_number (integer, the sequence number recorded),
        previous_resolution_deadline (text, YYYY-MM-DD, the deadline the case carried when the call was
        made) and extended_deadline (text, YYYY-MM-DD, the case's resulting resolution deadline). A receipt
        showing the extended deadline means the extension is granted and the letter recorded.
    """
    rows = ctx.find("maturity_cases", maturity_case_id=maturity_case_id)
    if not rows:
        return f"Error: no maturity case {maturity_case_id}."
    case = rows[0]
    today = ctx.now()[:10]
    previous = case.get("resolution_deadline") or ""
    extended = _CalendarDays.add(previous, int(extension_days)) if previous else previous
    ext_id = ctx.make_id("mev_", maturity_case_id, maturity_request_id, int(extension_number), int(extension_days))
    ctx.create("maturity_case_events", ext_id, maturity_event_id=ext_id, maturity_case_id=maturity_case_id,
               customer_id=case.get("customer_id"), event_type="maturity_extension_granted",
               effective_date=today, hud_action="not_applicable", notice_type="not_applicable",
               recipient_customer_id=None, extension_number=int(extension_number), extended_deadline=extended,
               maturity_request_id=maturity_request_id)
    letter_id = ctx.make_id("mev_", maturity_case_id, recipient_customer_id, "extension_letter", today,
                            int(extension_number), int(extension_days))
    ctx.create("maturity_case_events", letter_id, maturity_event_id=letter_id, maturity_case_id=maturity_case_id,
               customer_id=case.get("customer_id"), event_type="maturity_notice_sent",
               effective_date=today, hud_action="not_applicable", notice_type="extension_letter",
               recipient_customer_id=recipient_customer_id, extension_number=0, extended_deadline="",
               maturity_request_id=None)
    ctx.update("maturity_cases", maturity_case_id, resolution_deadline=extended)
    ctx.update("maturity_requests", maturity_request_id, request_status="accepted")
    return str({"maturity_case_id": maturity_case_id, "extension_reference": ext_id,
                "letter_reference": letter_id, "extension_number": int(extension_number),
                "previous_resolution_deadline": previous, "extended_deadline": extended})

"""Hidden task tools for the hardship_hold_requests difficulty (Hardship and Protective Holds).

Each tool performs one atomic write on a hardship hold or on its hold history. Tools take the
values the agent has already worked out from the published rules and the records, and record
them as given; they check no eligibility and refuse nothing.
"""

from erlbench import ToolContext, tool


class _CalendarDays:
    """Pure-Python calendar arithmetic on 'YYYY-MM-DD' strings (proleptic Gregorian)."""

    @staticmethod
    def to_ordinal(day: str) -> int:
        y, m, d = (int(p) for p in str(day)[:10].split("-"))
        a = (14 - m) // 12
        yy = y + 4800 - a
        mm = m + 12 * a - 3
        return d + (153 * mm + 2) // 5 + 365 * yy + yy // 4 - yy // 100 + yy // 400 - 32045

    @staticmethod
    def from_ordinal(n: int) -> str:
        a = n + 32044
        b = (4 * a + 3) // 146097
        c = a - 146097 * b // 4
        d = (4 * c + 3) // 1461
        e = c - 1461 * d // 4
        m = (5 * e + 2) // 153
        day = e - (153 * m + 2) // 5 + 1
        month = m + 3 - 12 * (m // 10)
        year = 100 * b + d - 4800 + m // 10
        return f"{year:04d}-{month:02d}-{day:02d}"

    @staticmethod
    def add_days(day: str, days: int) -> str:
        return _CalendarDays.from_ordinal(_CalendarDays.to_ordinal(day) + int(days))


@tool(owner="agent", rw="write")
def send_cure_notice_c402292e(ctx: ToolContext, hold_id: str, document_type: str, cure_due_days: int) -> str:
    """Send the consumer a cure notice on a hardship or protective hold request whose documentation
    arrived incomplete. One call records one notice in the hold's history as a documentation request
    for the named kind of documentation, dated today, with a cure due date that falls the given number
    of calendar days after today. The hold itself, its status and its dates are not changed. On success
    the notice and its due date appear in the hold history for the consumer and the desk.

    Args:
        hold_id: Id class — the hold reference number of the hold request the incomplete documentation
            belongs to, read from the hardship hold lookup.
        document_type: Enum class — the kind of documentation the notice asks the consumer to complete,
            exactly one of: self_attestation, when a self-attested statement is what is missing;
            income_loss_evidence, when the missing item is household income records;
            disaster_area_residence_proof, when the missing item is proof of residence in a declared
            disaster area; financial_assistance_application, when the missing item is the hospital
            financial assistance application; medical_or_disability_certification, when the missing item
            is a physician's medical or disability certification; active_duty_status_proof, when the
            missing item is proof of active military duty.
        cure_due_days: Fixed-format class — the number of calendar days from today to the cure due date,
            a whole integer of at least 1, counted so that 1 means tomorrow; no decimals, no empty value.

    Returns:
        A dictionary rendered as text with: notice_ref (string, the reference of the recorded notice),
        hold_id (string, the hold the notice was recorded on), document_type (string, as sent),
        due_date (string, YYYY-MM-DD, the cure due date recorded on the notice), sent_on (string,
        YYYY-MM-DD, today's date) and status (string, always "cure_notice_sent" when the notice is
        recorded).
    """
    hold = (ctx.find("hardship_holds", hold_id=hold_id) or [{}])[0]
    today = ctx.now()[:10]
    due = _CalendarDays.add_days(today, int(cure_due_days))
    rid = ctx.make_id("hev_", hold_id, document_type, cure_due_days, today)
    ctx.create("hardship_hold_events", rid, hold_event_id=rid, hold_id=hold_id,
               customer_id=hold.get("customer_id", ""), account_id=hold.get("account_id", ""),
               event_type="hardship_documentation_requested", event_date=today,
               document_type=document_type, due_date=due)
    return str({"notice_ref": rid, "hold_id": hold_id, "document_type": document_type,
                "due_date": due, "sent_on": today, "status": "cure_notice_sent"})


@tool(owner="user", rw="write")
def extend_longterm_hold_aa9e035f(ctx: ToolContext, hold_id: str, extension_days: int) -> str:
    """The consumer extends their own running Long-Term Hardship Hold through the self-service portal.
    One call books one extension: it records the extension in the hold history with today's date, the
    extension's sequence number and the days added, and moves the hold's last covered day forward by
    those days, counting the extension count up by one. The hold stays active. On success the consumer
    and the desk see the new last day of the hold and the extension in its history.

    Args:
        hold_id: Id class — the hold reference number of the consumer's running hold, which the agent
            reads from the hardship hold lookup and gives to the consumer.
        extension_days: Fixed-format class — the days the extension adds, as a positive integer, calendar days, that
            the agent tells the consumer; a whole number of at least 1, no decimals; the new last day of
            the hold is the current last day plus this many days.

    Returns:
        A dictionary rendered as text with: extension_ref (string, the reference of the recorded
        extension), hold_id (string), extension_number (integer, which extension of the hold this is),
        days_added (integer, calendar days), previous_end_date (string, YYYY-MM-DD), new_end_date
        (string, YYYY-MM-DD, the hold's new last covered day) and status (string, always "extended" when
        the extension is booked).
    """
    hold = (ctx.find("hardship_holds", hold_id=hold_id) or [{}])[0]
    today = ctx.now()[:10]
    previous_end = str(hold.get("end_date") or today)
    number = int(hold.get("extension_count") or 0) + 1
    new_end = _CalendarDays.add_days(previous_end, int(extension_days))
    rid = ctx.make_id("hev_", hold_id, extension_days, number)
    ctx.create("hardship_hold_events", rid, hold_event_id=rid, hold_id=hold_id,
               customer_id=hold.get("customer_id", ""), account_id=hold.get("account_id", ""),
               event_type="hardship_extension_granted", event_date=today,
               extension_number=number, days_granted=int(extension_days))
    ctx.update("hardship_holds", hold_id, end_date=new_end, extension_count=number)
    return str({"extension_ref": rid, "hold_id": hold_id, "extension_number": number,
                "days_added": int(extension_days), "previous_end_date": previous_end,
                "new_end_date": new_end, "status": "extended"})


@tool(owner="agent", rw="write")
def request_income_records_8e86e9ce(ctx: ToolContext, hold_id: str, due_in_days: int) -> str:
    """Ask the consumer for updated household income records for an upcoming status review of a
    running hardship hold. One call records one documentation request for income records in the hold
    history, dated today, with a due date the given number of calendar days after today. The hold itself
    is not changed. On success the request and its due date appear in the hold history.

    Args:
        hold_id: Id class — the hold reference number of the running hold under review, read from the
            hardship hold lookup.
        due_in_days: Fixed-format class — the number of calendar days from today to the due date of the
            income records, a whole integer of at least 1 (1 means tomorrow); no decimals, no empty value.

    Returns:
        A dictionary rendered as text with: request_ref (string, the reference of the recorded request),
        hold_id (string), document_type (string, always "income_loss_evidence"), due_date (string,
        YYYY-MM-DD), sent_on (string, YYYY-MM-DD, today) and status (string, always "requested" when the
        request is recorded).
    """
    hold = (ctx.find("hardship_holds", hold_id=hold_id) or [{}])[0]
    today = ctx.now()[:10]
    due = _CalendarDays.add_days(today, int(due_in_days))
    rid = ctx.make_id("hev_", hold_id, "income_loss_evidence", due_in_days, today)
    ctx.create("hardship_hold_events", rid, hold_event_id=rid, hold_id=hold_id,
               customer_id=hold.get("customer_id", ""), account_id=hold.get("account_id", ""),
               event_type="hardship_documentation_requested", event_date=today,
               document_type="income_loss_evidence", due_date=due)
    return str({"request_ref": rid, "hold_id": hold_id, "document_type": "income_loss_evidence",
                "due_date": due, "sent_on": today, "status": "requested"})


@tool(owner="agent", rw="write")
def request_medical_recertification_c8d32721(ctx: ToolContext, hold_id: str, due_in_days: int) -> str:
    """Ask the consumer for an updated physician's medical or disability certification for an upcoming
    status review of a running hardship hold. One call records one documentation request for the
    certification in the hold history, dated today, with a due date the given number of calendar days
    after today. The hold itself is not changed. On success the request and its due date appear in the
    hold history.

    Args:
        hold_id: Id class — the hold reference number of the running hold under review, read from the
            hardship hold lookup.
        due_in_days: Fixed-format class — the number of calendar days from today to the due date of the
            certification, a whole integer of at least 1 (1 means tomorrow); no decimals, no empty value.

    Returns:
        A dictionary rendered as text with: request_ref (string, the reference of the recorded request),
        hold_id (string), document_type (string, always "medical_or_disability_certification"), due_date
        (string, YYYY-MM-DD), sent_on (string, YYYY-MM-DD, today) and status (string, always "requested"
        when the request is recorded).
    """
    hold = (ctx.find("hardship_holds", hold_id=hold_id) or [{}])[0]
    today = ctx.now()[:10]
    due = _CalendarDays.add_days(today, int(due_in_days))
    rid = ctx.make_id("hev_", hold_id, "medical_or_disability_certification", due_in_days, today)
    ctx.create("hardship_hold_events", rid, hold_event_id=rid, hold_id=hold_id,
               customer_id=hold.get("customer_id", ""), account_id=hold.get("account_id", ""),
               event_type="hardship_documentation_requested", event_date=today,
               document_type="medical_or_disability_certification", due_date=due)
    return str({"request_ref": rid, "hold_id": hold_id,
                "document_type": "medical_or_disability_certification",
                "due_date": due, "sent_on": today, "status": "requested"})


@tool(owner="user", rw="write")
def extend_service_hold_a0a57648(ctx: ToolContext, hold_id: str, extension_days: int) -> str:
    """The servicemember extends their own running Military Service Hold through the self-service
    portal on the active-duty orders already on file. One call books one extension: it records the
    extension in the hold history with today's date, the extension's sequence number and the days added,
    and moves the hold's last covered day forward by those days, counting the extension count up by one.
    The hold stays active. On success the servicemember and the desk see the new last day of the hold and
    the extension in its history.

    Args:
        hold_id: Id class — the hold reference number of the servicemember's running Military Service Hold,
            which the agent reads from the hardship hold lookup and gives to the servicemember.
        extension_days: Fixed-format class — the days the extension adds, as a positive integer, calendar days, that
            the agent tells the servicemember; a whole number of at least 1, no decimals; the new last day of
            the hold is the current last day plus this many days.

    Returns:
        A dictionary rendered as text with: extension_ref (string, the reference of the recorded
        extension), hold_id (string), extension_number (integer, which extension of the hold this is),
        days_added (integer, calendar days), previous_end_date (string, YYYY-MM-DD), new_end_date
        (string, YYYY-MM-DD, the hold's new last covered day) and status (string, always "extended" when
        the extension is booked).
    """
    hold = (ctx.find("hardship_holds", hold_id=hold_id) or [{}])[0]
    today = ctx.now()[:10]
    previous_end = str(hold.get("end_date") or today)
    number = int(hold.get("extension_count") or 0) + 1
    new_end = _CalendarDays.add_days(previous_end, int(extension_days))
    rid = ctx.make_id("hev_", hold_id, extension_days, number)
    ctx.create("hardship_hold_events", rid, hold_event_id=rid, hold_id=hold_id,
               customer_id=hold.get("customer_id", ""), account_id=hold.get("account_id", ""),
               event_type="hardship_extension_granted", event_date=today,
               extension_number=number, days_granted=int(extension_days))
    ctx.update("hardship_holds", hold_id, end_date=new_end, extension_count=number)
    return str({"extension_ref": rid, "hold_id": hold_id, "extension_number": number,
                "days_added": int(extension_days), "previous_end_date": previous_end,
                "new_end_date": new_end, "status": "extended"})


@tool(owner="agent", rw="write")
def request_service_review_proof_12b8aafa(ctx: ToolContext, hold_id: str, due_in_days: int) -> str:
    """Ask a servicemember for current proof of active military duty for an upcoming status review of a
    running Military Service Hold. One call records one documentation request for active-duty status
    proof in the hold history, dated today, with a due date the given number of calendar days after
    today. The hold itself is not changed. On success the request and its due date appear in the hold
    history.

    Args:
        hold_id: Id class — the hold reference number of the running Military Service Hold under review,
            read from the hardship hold lookup.
        due_in_days: Fixed-format class — the number of calendar days from today to the due date of the
            proof, a whole integer of at least 1 (1 means tomorrow); no decimals, no empty value.

    Returns:
        A dictionary rendered as text with: request_ref (string, the reference of the recorded request),
        hold_id (string), document_type (string, always "active_duty_status_proof"), due_date (string,
        YYYY-MM-DD), sent_on (string, YYYY-MM-DD, today) and status (string, always "requested" when the
        request is recorded).
    """
    hold = (ctx.find("hardship_holds", hold_id=hold_id) or [{}])[0]
    today = ctx.now()[:10]
    due = _CalendarDays.add_days(today, int(due_in_days))
    rid = ctx.make_id("hev_", hold_id, "review_proof", due_in_days, today)
    ctx.create("hardship_hold_events", rid, hold_event_id=rid, hold_id=hold_id,
               customer_id=hold.get("customer_id", ""), account_id=hold.get("account_id", ""),
               event_type="hardship_documentation_requested", event_date=today,
               document_type="active_duty_status_proof", due_date=due)
    return str({"request_ref": rid, "hold_id": hold_id, "document_type": "active_duty_status_proof",
                "due_date": due, "sent_on": today, "status": "requested"})


@tool(owner="agent", rw="write")
def request_service_documentation_e72ed459(ctx: ToolContext, hold_id: str, due_in_days: int) -> str:
    """Send the initial documentation request on an undecided Military Service Hold request, asking the
    servicemember for proof of active military duty for that request. One call records one documentation
    request for active-duty status proof in the request's history, dated today, with a due date the given
    number of calendar days after today. The request itself stays undecided and unchanged. On success the
    request and its due date appear in the history of that hold request.

    Args:
        hold_id: Id class — the hold reference number of the undecided Military Service Hold request, read
            from the hardship hold lookup.
        due_in_days: Fixed-format class — the number of calendar days from today to the due date of the
            documentation, a whole integer of at least 1 (1 means tomorrow); no decimals, no empty value.

    Returns:
        A dictionary rendered as text with: request_ref (string, the reference of the recorded request),
        hold_id (string), document_type (string, always "active_duty_status_proof"), due_date (string,
        YYYY-MM-DD), sent_on (string, YYYY-MM-DD, today) and status (string, always "requested" when the
        request is recorded).
    """
    hold = (ctx.find("hardship_holds", hold_id=hold_id) or [{}])[0]
    today = ctx.now()[:10]
    due = _CalendarDays.add_days(today, int(due_in_days))
    rid = ctx.make_id("hev_", hold_id, "initial_documentation", due_in_days, today)
    ctx.create("hardship_hold_events", rid, hold_event_id=rid, hold_id=hold_id,
               customer_id=hold.get("customer_id", ""), account_id=hold.get("account_id", ""),
               event_type="hardship_documentation_requested", event_date=today,
               document_type="active_duty_status_proof", due_date=due)
    return str({"request_ref": rid, "hold_id": hold_id, "document_type": "active_duty_status_proof",
                "due_date": due, "sent_on": today, "status": "requested"})

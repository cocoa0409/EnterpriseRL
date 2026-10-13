"""Hidden task tools for the benefit_and_tax_appeals difficulty (category: appeal).

Each tool performs one atomic hearing-calendar write on one appeal. The scored day count the agent
works out from the policy is turned into a calendar date with the pure ordinal-day helper below;
nothing here judges eligibility, status, ownership or timing.
"""

from erlbench import ToolContext, tool


class _CalendarDays:
    """Pure calendar arithmetic on 'YYYY-MM-DD' text (proleptic Gregorian, no library clock)."""

    @staticmethod
    def to_ordinal(text: str) -> int:
        y, m, d = (int(p) for p in str(text)[:10].split("-"))
        y -= 1 if m <= 2 else 0
        era = (y if y >= 0 else y - 399) // 400
        yoe = y - era * 400
        doy = (153 * (m + (-3 if m > 2 else 9)) + 2) // 5 + d - 1
        doe = yoe * 365 + yoe // 4 - yoe // 100 + doy
        return era * 146097 + doe - 719468

    @staticmethod
    def from_ordinal(z: int) -> str:
        z += 719468
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
    def shift(text: str, days: int) -> str:
        return _CalendarDays.from_ordinal(_CalendarDays.to_ordinal(text) + int(days))


@tool(owner="agent", rw="write")
def docket_appeal_hearing_a28520da(ctx: ToolContext, appeal_id: str, notice_period_days: int) -> str:
    """Docket a filed appeal and set its first hearing by telephone, mailing the hearing notice today.

    One call moves the appeal from filed to scheduled, records the first hearing date on the appeal,
    and adds one hearing-setting record to the appeal's activity: a telephone hearing at 09:00 local
    time on the hearing date, with the notice mailed today and the setting marked as the first
    (initial) setting. Every interested party sees the new hearing date on the appeal and in the
    activity history. The call succeeds when the receipt shows status scheduled and the hearing date.

    Args:
        appeal_id: Id class — the docket number of the filed appeal to be set for hearing, read from the appeal lookup (find_appeals) before the call.
        notice_period_days: Fixed-format class — whole number of calendar days from today's date (the notice mailing date, counted as day 0) to the first hearing date, an integer of at least 1; the tool records the hearing date as the YYYY-MM-DD date that many calendar days after today.

    Returns:
        A text receipt of a dictionary with: appeal_id (the docket number), appeal_event_id (the
        reference number of the hearing-setting record), status (always "scheduled" after a
        successful call), hearing_date (YYYY-MM-DD), hearing_time ("09:00"), hearing_mode
        ("telephone") and notice_mailed_date (today's date, YYYY-MM-DD).
    """
    today = ctx.now()[:10]
    hearing = _CalendarDays.shift(today, notice_period_days)
    rows = ctx.find("appeals", appeal_id=appeal_id)
    appellant = rows[0].get("customer_id") if rows else None
    rid = ctx.make_id("aev_", appeal_id, notice_period_days, "initial")
    ctx.create("appeal_events", rid, appeal_event_id=rid, appeal_id=appeal_id, customer_id=appellant,
               event_type="appeal_hearing_scheduled", hearing_date=hearing, hearing_time="09:00",
               hearing_mode="telephone", notice_mailed_date=today, schedule_reason="initial",
               requested_by="not_applicable", request_date="", postponement_outcome="not_applicable",
               exhibit_type="not_applicable", received_date="", exhibit_status="not_applicable",
               language="not_applicable")
    ctx.update("appeals", appeal_id, status="scheduled", hearing_date=hearing)
    return str({"appeal_id": appeal_id, "appeal_event_id": rid, "status": "scheduled",
                "hearing_date": hearing, "hearing_time": "09:00", "hearing_mode": "telephone",
                "notice_mailed_date": today})


@tool(owner="user", rw="write")
def book_video_hearing_session_16bf8e4f(ctx: ToolContext, appeal_id: str, session_days: int) -> str:
    """Book, as the party who asked for it, a video hearing session that replaces the telephone hearing set on your appeal.

    One call records a new hearing setting on the appeal in video mode at 13:00 local time, with
    its notice mailed today, entered as a change of hearing mode made at your request (not a postponement, so no postponement reason is recorded), and moves the
    appeal's hearing date to the video session date. You see the video session date on the appeal
    and in its activity history; the earlier telephone date is no longer the hearing date. The call
    succeeds when the receipt shows hearing_mode video and the new hearing date.

    Args:
        appeal_id: Id class — the docket number of your appeal, as the agent reads it to you from the appeal record before you book.
        session_days: Fixed-format class — whole number of calendar days from today's date (counted as day 0) to the video session date, an integer the agent gives you; the tool records the session as the YYYY-MM-DD date that many calendar days after today.

    Returns:
        A text receipt of a dictionary with: appeal_id (the docket number), appeal_event_id (the
        reference number of the video-session setting), hearing_date (the video session date,
        YYYY-MM-DD), hearing_time ("13:00"), hearing_mode ("video") and notice_mailed_date
        (today's date, YYYY-MM-DD).
    """
    today = ctx.now()[:10]
    session = _CalendarDays.shift(today, session_days)
    rows = ctx.find("appeals", appeal_id=appeal_id)
    appellant = rows[0].get("customer_id") if rows else None
    role = rows[0].get("appellant_role") if rows else "not_applicable"
    rid = ctx.make_id("aev_", appeal_id, session_days, "video")
    ctx.create("appeal_events", rid, appeal_event_id=rid, appeal_id=appeal_id, customer_id=appellant,
               event_type="appeal_hearing_scheduled", hearing_date=session, hearing_time="13:00",
               hearing_mode="video", notice_mailed_date=today, schedule_reason="not_applicable",
               requested_by=role, request_date=today, postponement_outcome="not_applicable",
               exhibit_type="not_applicable", received_date="", exhibit_status="not_applicable",
               language="not_applicable")
    ctx.update("appeals", appeal_id, hearing_date=session)
    return str({"appeal_id": appeal_id, "appeal_event_id": rid, "hearing_date": session,
                "hearing_time": "13:00", "hearing_mode": "video", "notice_mailed_date": today})


@tool(owner="agent", rw="write")
def reopen_dismissed_appeal_6a7f532d(ctx: ToolContext, appeal_id: str, reopening_request_id: str,
                                     notice_period_days: int) -> str:
    """Grant the appellant's reopening request on a dismissed appeal and set the reopened hearing by telephone.

    One call marks the reopening request granted, moves the appeal from dismissed to scheduled with
    the reopened hearing date, and adds one hearing-setting record to the appeal's activity: a
    telephone hearing at 09:00 local time on that date, notice mailed today, marked as a setting
    made on reopening. The appellant and every interested party see the appeal back on the hearing
    calendar. The call succeeds when the receipt shows status scheduled, the hearing date and the
    request status granted.

    Args:
        appeal_id: Id class — the docket number of the dismissed appeal, read from the appeal lookup (find_appeals) before the call.
        reopening_request_id: Id class — the reference number of the appellant's reopening request on that appeal, read from the appeal request lookup (find_appeal_requests) before the call.
        notice_period_days: Fixed-format class — whole number of calendar days from today's date (the notice mailing date, counted as day 0) to the reopened hearing date, an integer of at least 1; the tool records the hearing date as the YYYY-MM-DD date that many calendar days after today.

    Returns:
        A text receipt of a dictionary with: appeal_id (the docket number), appeal_event_id (the
        reference number of the reopened hearing setting), reopening_request_id (the request
        reference), request_status ("granted"), status ("scheduled"), hearing_date (YYYY-MM-DD),
        hearing_time ("09:00"), hearing_mode ("telephone") and notice_mailed_date (today's date,
        YYYY-MM-DD).
    """
    today = ctx.now()[:10]
    hearing = _CalendarDays.shift(today, notice_period_days)
    rows = ctx.find("appeals", appeal_id=appeal_id)
    appellant = rows[0].get("customer_id") if rows else None
    rid = ctx.make_id("aev_", appeal_id, reopening_request_id, notice_period_days, "reopening")
    ctx.create("appeal_events", rid, appeal_event_id=rid, appeal_id=appeal_id, customer_id=appellant,
               event_type="appeal_hearing_scheduled", hearing_date=hearing, hearing_time="09:00",
               hearing_mode="telephone", notice_mailed_date=today, schedule_reason="reopening",
               requested_by="not_applicable", request_date="", postponement_outcome="not_applicable",
               exhibit_type="not_applicable", received_date="", exhibit_status="not_applicable",
               language="not_applicable")
    ctx.update("appeal_requests", reopening_request_id, request_status="granted")
    ctx.update("appeals", appeal_id, status="scheduled", hearing_date=hearing)
    return str({"appeal_id": appeal_id, "appeal_event_id": rid, "reopening_request_id": reopening_request_id,
                "request_status": "granted", "status": "scheduled", "hearing_date": hearing,
                "hearing_time": "09:00", "hearing_mode": "telephone", "notice_mailed_date": today})


@tool(owner="user", rw="write")
def book_in_person_hearing_session_05d44a0a(ctx: ToolContext, appeal_id: str, session_days: int) -> str:
    """Book, as the party who asked for it, an in-person hearing session at the Department hearing office that replaces the telephone hearing set on your appeal.

    One call records a new hearing setting on the appeal in in-person mode at 09:30 local time, with
    its notice mailed today, entered as a change of hearing mode made at your request (not a postponement, so no postponement reason is recorded), and moves the
    appeal's hearing date to the in-person session date. You see the session date on the appeal and
    in its activity history; the earlier telephone date is no longer the hearing date. The call
    succeeds when the receipt shows hearing_mode in_person and the new hearing date.

    Args:
        appeal_id: Id class — the docket number of your appeal, as the agent reads it to you from the appeal record before you book.
        session_days: Fixed-format class — whole number of calendar days from today's date (counted as day 0) to the in-person session date, an integer the agent gives you; the tool records the session as the YYYY-MM-DD date that many calendar days after today.

    Returns:
        A text receipt of a dictionary with: appeal_id (the docket number), appeal_event_id (the
        reference number of the in-person setting), hearing_date (the session date, YYYY-MM-DD),
        hearing_time ("09:30"), hearing_mode ("in_person") and notice_mailed_date (today's date,
        YYYY-MM-DD).
    """
    today = ctx.now()[:10]
    session = _CalendarDays.shift(today, session_days)
    rows = ctx.find("appeals", appeal_id=appeal_id)
    appellant = rows[0].get("customer_id") if rows else None
    role = rows[0].get("appellant_role") if rows else "not_applicable"
    rid = ctx.make_id("aev_", appeal_id, session_days, "in_person")
    ctx.create("appeal_events", rid, appeal_event_id=rid, appeal_id=appeal_id, customer_id=appellant,
               event_type="appeal_hearing_scheduled", hearing_date=session, hearing_time="09:30",
               hearing_mode="in_person", notice_mailed_date=today, schedule_reason="not_applicable",
               requested_by=role, request_date=today, postponement_outcome="not_applicable",
               exhibit_type="not_applicable", received_date="", exhibit_status="not_applicable",
               language="not_applicable")
    ctx.update("appeals", appeal_id, hearing_date=session)
    return str({"appeal_id": appeal_id, "appeal_event_id": rid, "hearing_date": session,
                "hearing_time": "09:30", "hearing_mode": "in_person", "notice_mailed_date": today})

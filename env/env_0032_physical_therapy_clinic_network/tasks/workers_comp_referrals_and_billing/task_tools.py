"""Hidden task tools of the workers_comp_referrals_and_billing difficulty (category wc).

Each tool performs one atomic write on a Workers' Compensation Referral and its history.
No tool checks eligibility, prerequisites, ownership or status: the agent decides from the
published policy and the records before it calls, and the tool lands exactly what it is given.
"""

from erlbench import ToolContext, tool


@tool(owner="agent", rw="write")
def record_program_day_6fda50ae(ctx: ToolContext, wc_case_id: str, appointment_date: str, units: int,
                                auth_reference: str) -> str:
    """Record one attended program day of an hour-billed workers' compensation program (Work
    Conditioning or Work Hardening) against the adjuster authorization in force on the referral.

    One call adds one recorded program day to the referral's history: the date of service, the
    program hours recorded for that day and the authorization reference it is drawn on. The day
    draws one authorized program day, so the referral's count of authorized program days still
    unused goes down by one. Nothing is billed by this action. On success the program day is
    visible in the referral history with the recording date set to today.

    Args:
        wc_case_id: Id class — the reference number of the workers' compensation referral the program
            day belongs to, as returned by the referral lookup.
        appointment_date: Fixed-format class — the date of service of the attended program day, in
            YYYY-MM-DD format (calendar date in the clinic's local time zone; no empty value).
        units: Fixed-format class — the program hours recorded for the day, a non-negative integer (units)
            of whole hours; no fractions and no empty value.
        auth_reference: Verbatim class — the adjuster authorization reference the day is drawn on,
            copied character for character from the authorization reference shown on the referral,
            preserving letters, digits and punctuation with no normalisation (verbatim).

    Returns:
        A dictionary rendered as text with the keys: status ("recorded" when the day was written),
        wc_event_id (reference number of the new program-day entry, text), wc_case_id (the referral,
        text), appointment_date (YYYY-MM-DD), units (integer hours recorded), auth_reference (text),
        and authorized_visits_remaining (integer count of authorized program days still unused on the
        referral after this day).
    """
    rid = ctx.make_id("wcv_", wc_case_id, appointment_date, units, auth_reference)
    ctx.create("wc_events", rid, wc_event_id=rid, wc_case_id=wc_case_id,
               customer_id=(ctx.find("wc_cases", wc_case_id=wc_case_id) or [{}])[0].get("customer_id", ""),
               event_type="wc_visit_billed", event_date=ctx.now()[:10], appointment_date=appointment_date,
               visits=1, units=int(units), auth_reference=auth_reference)
    remaining = int((ctx.find("wc_cases", wc_case_id=wc_case_id) or [{}])[0].get("authorized_visits_remaining") or 0) - 1
    ctx.update("wc_cases", wc_case_id, authorized_visits_remaining=remaining)
    return str({"status": "recorded", "wc_event_id": rid, "wc_case_id": wc_case_id,
                "appointment_date": appointment_date, "units": int(units), "auth_reference": auth_reference,
                "authorized_visits_remaining": remaining})


@tool(owner="agent", rw="write")
def post_program_day_charge_5325d445(ctx: ToolContext, wc_case_id: str, appointment_date: str, units: int,
                                     amount: float) -> str:
    """Bill one recorded program day of an hour-billed workers' compensation program to the
    workers' compensation carrier.

    One call posts one program-hours charge on the referral for the given date of service, with the
    billed hours and the billed amount, submitted to the carrier today. The referral's amount billed
    and still unpaid rises by the billed amount. On success the charge is visible in the referral
    history with today's posting and submission date and the carrier as the payer.

    Args:
        wc_case_id: Id class — the reference number of the workers' compensation referral being billed,
            as returned by the referral lookup.
        appointment_date: Fixed-format class — the date of service of the program day billed, in
            YYYY-MM-DD format (calendar date in the clinic's local time zone; no empty value).
        units: Fixed-format class — the billing units of the charge, a non-negative integer (units) of
            program hours; no fractions and no empty value.
        amount: Fixed-format class — the amount billed for the day in USD, a positive number rounded
            half up to 2 decimal places before it is passed (cents precision, no currency sign).

    Returns:
        A dictionary rendered as text with the keys: status ("posted" when the charge was written),
        wc_event_id (reference number of the new charge, text), wc_case_id (text), appointment_date
        (YYYY-MM-DD), units (integer hours billed), amount (USD, 2 decimal places), bill_submitted_date
        (YYYY-MM-DD, today) and receivable_balance (USD, 2 decimal places: the referral's amount billed
        and still unpaid after this charge).
    """
    amt = round(float(amount), 2)
    rid = ctx.make_id("wcc_", wc_case_id, appointment_date, units, amt)
    ctx.create("wc_events", rid, wc_event_id=rid, wc_case_id=wc_case_id,
               customer_id=(ctx.find("wc_cases", wc_case_id=wc_case_id) or [{}])[0].get("customer_id", ""),
               event_type="wc_charge_posted", event_date=ctx.now()[:10], appointment_date=appointment_date,
               charge_kind="program_hours", units=int(units), amount=amt, bill_submitted_date=ctx.now()[:10],
               payer_kind="carrier")
    balance = round(float((ctx.find("wc_cases", wc_case_id=wc_case_id) or [{}])[0].get("receivable_balance") or 0) + amt, 2)
    ctx.update("wc_cases", wc_case_id, receivable_balance=balance)
    return str({"status": "posted", "wc_event_id": rid, "wc_case_id": wc_case_id,
                "appointment_date": appointment_date, "units": int(units), "amount": amt,
                "bill_submitted_date": ctx.now()[:10], "receivable_balance": balance})


@tool(owner="user", rw="write")
def record_program_extension_8df51c57(ctx: ToolContext, wc_case_id: str, auth_reference: str, visits: int,
                                      visits_per_week: int, auth_start_date: str, auth_end_date: str) -> str:
    """The claims adjuster records, in person, an extension of an hour-billed workers' compensation
    program (Work Conditioning or Work Hardening): the adjuster's own authorization of further
    program days on the referral.

    One call adds one adjuster authorization to the referral's history with its reference, the
    program days and weekly frequency authorized and the first and last dates it covers. The
    referral's authorization in force becomes this one (reference, end date and weekly frequency),
    and its count of authorized program days still unused rises by the days authorized. On success
    the adjuster sees the new authorization in force on the referral.

    Args:
        wc_case_id: Id class — the reference number of the workers' compensation referral being
            extended, read out to the adjuster by the clinic from the referral lookup.
        auth_reference: Verbatim class — the adjuster's own authorization reference for this extension,
            exactly as the adjuster states it, copied character for character with its letters, digits
            and punctuation unchanged (verbatim).
        visits: Fixed-format class — the program days authorized by this extension, a non-negative
            integer (count) of days; no fractions and no empty value.
        visits_per_week: Fixed-format class — the program days per Monday-to-Sunday week the extension
            allows, a non-negative integer (count) of days; no fractions and no empty value.
        auth_start_date: Fixed-format class — the first date of service the extension covers, in
            YYYY-MM-DD format (calendar date; no empty value).
        auth_end_date: Fixed-format class — the last date of service the extension covers, in
            YYYY-MM-DD format (calendar date; no empty value).

    Returns:
        A dictionary rendered as text with the keys: status ("authorized" when the extension was
        written), wc_event_id (reference number of the new authorization entry, text), wc_case_id
        (text), auth_reference (text), visits (integer days authorized), visits_per_week (integer),
        auth_start_date and auth_end_date (YYYY-MM-DD), and authorized_visits_remaining (integer count
        of authorized program days unused on the referral after the extension).
    """
    rid = ctx.make_id("wca_", wc_case_id, auth_reference, visits, visits_per_week, auth_start_date, auth_end_date)
    ctx.create("wc_events", rid, wc_event_id=rid, wc_case_id=wc_case_id,
               customer_id=(ctx.find("wc_cases", wc_case_id=wc_case_id) or [{}])[0].get("customer_id", ""),
               event_type="wc_authorization_received", event_date=ctx.now()[:10], auth_reference=auth_reference,
               visits=int(visits), visits_per_week=int(visits_per_week), auth_start_date=auth_start_date,
               auth_end_date=auth_end_date)
    remaining = int((ctx.find("wc_cases", wc_case_id=wc_case_id) or [{}])[0].get("authorized_visits_remaining") or 0) + int(visits)
    ctx.update("wc_cases", wc_case_id, auth_reference=auth_reference, auth_end_date=auth_end_date,
               authorized_visits_per_week=int(visits_per_week), authorized_visits_remaining=remaining)
    return str({"status": "authorized", "wc_event_id": rid, "wc_case_id": wc_case_id,
                "auth_reference": auth_reference, "visits": int(visits), "visits_per_week": int(visits_per_week),
                "auth_start_date": auth_start_date, "auth_end_date": auth_end_date,
                "authorized_visits_remaining": remaining})


@tool(owner="user", rw="write")
def record_fce_authorization_83d13911(ctx: ToolContext, wc_case_id: str, auth_reference: str, hours: int,
                                      sessions: int, auth_start_date: str, auth_end_date: str) -> str:
    """The claims adjuster records, in person, the adjuster's own authorization of a Functional Capacity
    Evaluation on a workers' compensation referral: the evaluation hours and sessions authorized and
    the dates the authorization covers.

    One call adds one adjuster authorization to the referral's history. The referral's authorization
    in force becomes this one (reference, end date, and sessions per week), and its count of
    authorized evaluation hours still unused rises by the hours authorized. On success the adjuster
    sees the new authorization in force on the referral.

    Args:
        wc_case_id: Id class — the reference number of the Functional Capacity Evaluation referral being
            authorized, read out to the adjuster by the clinic from the referral lookup.
        auth_reference: Verbatim class — the adjuster's own authorization reference, exactly as the
            adjuster states it, copied character for character with its letters, digits and punctuation
            unchanged (verbatim).
        hours: Fixed-format class — the evaluation hours authorized, a non-negative integer (count) of
            whole hours; no fractions and no empty value.
        sessions: Fixed-format class — the evaluation sessions per Monday-to-Sunday week the authorization
            allows, a non-negative integer (count) of sessions; no fractions and no empty value.
        auth_start_date: Fixed-format class — the first date of service the authorization covers, in
            YYYY-MM-DD format (calendar date; no empty value).
        auth_end_date: Fixed-format class — the last date of service the authorization covers, in
            YYYY-MM-DD format (calendar date; no empty value).

    Returns:
        A dictionary rendered as text with the keys: status ("authorized" when the authorization was
        written), wc_event_id (reference number of the new authorization entry, text), wc_case_id (text),
        auth_reference (text), hours (integer hours authorized), sessions (integer sessions per week),
        auth_start_date and auth_end_date (YYYY-MM-DD), and authorized_visits_remaining (integer count of
        authorized evaluation hours unused on the referral afterwards).
    """
    rid = ctx.make_id("wcf_", wc_case_id, auth_reference, hours, sessions, auth_start_date, auth_end_date)
    case = (ctx.find("wc_cases", wc_case_id=wc_case_id) or [{}])[0]
    ctx.create("wc_events", rid, wc_event_id=rid, wc_case_id=wc_case_id, customer_id=case.get("customer_id", ""),
               event_type="wc_authorization_received", event_date=ctx.now()[:10], auth_reference=auth_reference,
               visits=int(hours), visits_per_week=int(sessions), auth_start_date=auth_start_date,
               auth_end_date=auth_end_date)
    remaining = int(case.get("authorized_visits_remaining") or 0) + int(hours)
    ctx.update("wc_cases", wc_case_id, auth_reference=auth_reference, auth_end_date=auth_end_date,
               authorized_visits_per_week=int(sessions), authorized_visits_remaining=remaining)
    return str({"status": "authorized", "wc_event_id": rid, "wc_case_id": wc_case_id,
                "auth_reference": auth_reference, "hours": int(hours), "sessions": int(sessions),
                "auth_start_date": auth_start_date, "auth_end_date": auth_end_date,
                "authorized_visits_remaining": remaining})


@tool(owner="agent", rw="write")
def post_fce_missed_fee_9edc6261(ctx: ToolContext, wc_case_id: str, appointment_date: str, amount: float) -> str:
    """Bill the workers' compensation carrier the fee for a missed Functional Capacity Evaluation
    appointment on a referral.

    One call posts one missed-evaluation fee on the referral for the date of the missed appointment,
    with the amount billed, submitted to the carrier today. The referral's amount billed and still
    unpaid rises by the amount. On success the fee is visible in the referral history with today's
    posting and submission date and the carrier as the payer.

    Args:
        wc_case_id: Id class — the reference number of the Functional Capacity Evaluation referral being
            billed, as returned by the referral lookup.
        appointment_date: Fixed-format class — the date of the missed evaluation appointment, in
            YYYY-MM-DD format (calendar date in the clinic's local time zone; no empty value).
        amount: Fixed-format class — the fee billed in USD, a non-negative number rounded half up to 2
            decimal places before it is passed (cents precision, no currency sign).

    Returns:
        A dictionary rendered as text with the keys: status ("posted" when the fee was written),
        wc_event_id (reference number of the new fee entry, text), wc_case_id (text), appointment_date
        (YYYY-MM-DD), amount (USD, 2 decimal places), bill_submitted_date (YYYY-MM-DD, today) and
        receivable_balance (USD, 2 decimal places: the referral's amount billed and still unpaid after
        the fee).
    """
    amt = round(float(amount), 2)
    rid = ctx.make_id("wcn_", wc_case_id, appointment_date, amt)
    case = (ctx.find("wc_cases", wc_case_id=wc_case_id) or [{}])[0]
    ctx.create("wc_events", rid, wc_event_id=rid, wc_case_id=wc_case_id, customer_id=case.get("customer_id", ""),
               event_type="wc_charge_posted", event_date=ctx.now()[:10], appointment_date=appointment_date,
               charge_kind="fce_no_show", units=0, amount=amt, bill_submitted_date=ctx.now()[:10],
               payer_kind="carrier")
    balance = round(float(case.get("receivable_balance") or 0) + amt, 2)
    ctx.update("wc_cases", wc_case_id, receivable_balance=balance)
    return str({"status": "posted", "wc_event_id": rid, "wc_case_id": wc_case_id,
                "appointment_date": appointment_date, "amount": amt, "bill_submitted_date": ctx.now()[:10],
                "receivable_balance": balance})

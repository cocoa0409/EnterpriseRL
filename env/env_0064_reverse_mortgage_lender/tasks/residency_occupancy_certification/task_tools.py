"""Hidden task tools for the residency_occupancy_certification difficulty of env_0064_reverse_mortgage_lender.

Each tool performs one atomic write on an occupancy certification profile, its occupancy history or its
submissions. The tools take the values the servicing desk has already worked out and record them as given;
they make no eligibility judgement and compute nothing on the caller's behalf.
"""

from erlbench import ToolContext, tool


class _Calendar:
    """Calendar-day arithmetic for the due-date tools (not a tool)."""

    @staticmethod
    def ordinal(date: str) -> int:
        """Day number of a YYYY-MM-DD date in the proleptic Gregorian calendar."""
        y, m, d = int(date[:4]), int(date[5:7]), int(date[8:10])
        y -= m <= 2
        era = y // 400
        yoe = y - era * 400
        doy = (153 * (m + (-3 if m > 2 else 9)) + 2) // 5 + d - 1
        doe = yoe * 365 + yoe // 4 - yoe // 100 + doy
        return era * 146097 + doe

    @staticmethod
    def from_ordinal(n: int) -> str:
        """The YYYY-MM-DD date of a day number produced by ordinal()."""
        era = n // 146097
        doe = n - era * 146097
        yoe = (doe - doe // 1460 + doe // 36524 - doe // 146096) // 365
        y = yoe + era * 400
        doy = doe - (365 * yoe + yoe // 4 - yoe // 100)
        mp = (5 * doy + 2) // 153
        d = doy - (153 * mp + 2) // 5 + 1
        m = mp + (3 if mp < 10 else -9)
        return f"{y + (m <= 2):04d}-{m:02d}-{d:02d}"

    @staticmethod
    def add_days(date: str, days: int) -> str:
        """The date the given number of calendar days after (or, when negative, before) a YYYY-MM-DD date."""
        return _Calendar.from_ordinal(_Calendar.ordinal(date) + int(days))


@tool(owner="agent", rw="write")
def reclassify_occupancy_plan_0e562024(ctx: ToolContext, residency_profile_id: str, residency_submission_id: str,
                                       variant_name: str, response_days: int) -> str:
    """Move an occupancy certification profile to a new certification plan after a certifying borrower's death.

    The servicing agent changes the plan recorded on the profile to the plan named here and sets the due date of
    the open certification cycle to the date that lies the given number of calendar days after today. The death
    notice the change rests on is cited in the receipt. Nothing else on the profile changes: its status, last
    certification, absence details and enrollment stay as they were. On success the profile shows the new plan and
    the new due date, and the receipt below is returned.

    Args:
        residency_profile_id: Id class — reference number of the occupancy certification profile being moved,
            as returned by the occupancy profile lookup for the borrower.
        residency_submission_id: Id class — reference number of the accepted death notice on file for this
            profile, as returned by the occupancy submission lookup.
        variant_name: Enum class — the certification plan the profile moves to, written exactly as one of:
            "Standard Annual Certification" (one living borrower remains and certifies alone);
            "Joint Borrower Certification" (two or more living borrowers remain and each certifies);
            "Non-Borrowing Spouse Household Certification" (a living borrower and an eligible non-borrowing
            spouse remain and both certify);
            "Deferral Period Certification" (no borrower remains and the eligible non-borrowing spouse certifies
            while the loan is in its deferral period);
            "Living Trust Certification" (title is held in a living trust and the trustee and each living
            borrower certify);
            "Authorized Representative Certification" (an attorney-in-fact or guardian certifies for the
            borrower).
        response_days: Fixed-format class — the calendar days from today to the due date the open certification
            cycle is to carry after the move, an integer written without decimals; negative when that due date
            lies before today.

    Returns:
        A one-line confirmation string of the form "Profile <residency_profile_id> moved to <variant_name>;
        open cycle due <new due date YYYY-MM-DD>; death notice <residency_submission_id>." Its presence (rather
        than a line beginning "Error") means the profile now carries the new plan and due date.
    """
    due = _Calendar.add_days(ctx.now()[:10], int(response_days))
    ctx.update("residency_profiles", residency_profile_id, variant_name=variant_name, certification_due_date=due)
    return (f"Profile {residency_profile_id} moved to {variant_name}; open cycle due {due}; "
            f"death notice {residency_submission_id}.")


@tool(owner="agent", rw="write")
def open_absence_monitoring_c2b89a70(ctx: ToolContext, residency_profile_id: str, residency_submission_id: str,
                                     absence_start_date: str) -> str:
    """Begin health-care absence monitoring on an occupancy certification profile.

    The servicing agent places the profile under health-care absence monitoring on the strength of the
    accepted health-care absence notice cited, and records the date from which the absence is counted. The
    profile's status becomes absence_monitoring and its absence start date becomes the date given. Nothing else
    on the profile changes. On success the profile shows the monitoring status and absence start date, and the
    receipt below is returned.

    Args:
        residency_profile_id: Id class — reference number of the occupancy certification profile, as returned
            by the occupancy profile lookup for the borrower.
        residency_submission_id: Id class — reference number of the accepted health-care absence notice on
            file for the borrower whose absence is monitored, as returned by the occupancy submission lookup.
        absence_start_date: Fixed-format class — the date from which the health-care absence is counted, a
            calendar date written YYYY-MM-DD; never empty.

    Returns:
        A one-line confirmation string of the form "Profile <residency_profile_id> under absence monitoring
        from <absence_start_date> (notice <residency_submission_id>)." Its presence (rather than a line
        beginning "Error") means the profile status is now absence_monitoring with that absence start date.
    """
    ctx.update("residency_profiles", residency_profile_id, status="absence_monitoring",
               absence_start_date=absence_start_date)
    return (f"Profile {residency_profile_id} under absence monitoring from {absence_start_date} "
            f"(notice {residency_submission_id}).")


@tool(owner="agent", rw="write")
def record_facility_checkin_6c7d3fa5(ctx: ToolContext, residency_profile_id: str, residency_submission_id: str,
                                     effective_date: str, checkin_sequence: int) -> str:
    """Record, as a health-care absence check-in, a contact that the borrower's care facility confirmed in writing.

    The servicing agent adds one check-in entry to the profile's occupancy history for the contact the cited
    facility letter confirms, carrying the contact date and the check-in number given and citing the letter.
    The entry is copied with the profile's primary borrower and loan program. Nothing else on the profile
    changes. On success the occupancy history lookup shows the new check-in entry, and the receipt below is
    returned.

    Args:
        residency_profile_id: Id class — reference number of the occupancy certification profile, as returned
            by the occupancy profile lookup for the borrower.
        residency_submission_id: Id class — reference number of the accepted facility letter on file that
            confirms the contact, as returned by the occupancy submission lookup.
        effective_date: Fixed-format class — the date of the contact as the facility letter states it, a
            calendar date written YYYY-MM-DD; never empty.
        checkin_sequence: Fixed-format class — the check-in number the contact is recorded under on the
            profile, an integer, 1-based, written without decimals.

    Returns:
        A one-line confirmation string of the form "Check-in <entry reference> recorded on profile
        <residency_profile_id>: number <checkin_sequence>, dated <effective_date>, letter
        <residency_submission_id>." The entry reference is the new history entry's reference number; its
        presence (rather than a line beginning "Error") means the check-in entry now exists.
    """
    prof = ctx.find("residency_profiles", residency_profile_id=residency_profile_id)
    owner = prof[0].get("customer_id", "") if prof else ""
    program = prof[0].get("loan_program", "") if prof else ""
    rid = ctx.make_id("rce_", residency_profile_id, residency_submission_id, effective_date, checkin_sequence)
    ctx.create("residency_events", rid, residency_event_id=rid, residency_profile_id=residency_profile_id,
               customer_id=owner, event_type="residency_absence_checkin", loan_program=program,
               effective_date=effective_date, certification_year="", notice_type="not_applicable",
               certifier_customer_id="", certification_method="not_applicable",
               residency_submission_id=residency_submission_id, inspection_reason="not_applicable",
               inspection_fee=0.00, inspection_outcome="not_applicable", checkin_sequence=int(checkin_sequence),
               source_event_ref="")
    return (f"Check-in {rid} recorded on profile {residency_profile_id}: number {int(checkin_sequence)}, "
            f"dated {effective_date}, letter {residency_submission_id}.")


@tool(owner="user", rw="write")
def confirm_absence_checkin_948ffc7a(ctx: ToolContext, residency_profile_id: str, checkin_sequence: int) -> str:
    """Let the absent borrower confirm a health-care absence check-in in person, on today's date.

    The borrower personally confirms, for the occupancy certification profile named, that they remain in care
    and intend to return home. One check-in entry dated today is added to the profile's occupancy history,
    carrying the check-in number given, the profile's primary borrower and its loan program. Nothing else on
    the profile changes. On success the borrower hears the confirmation below, and the occupancy history
    lookup shows the new entry.

    Args:
        residency_profile_id: Id class — reference number of the borrower's occupancy certification profile,
            as the servicing agent reads it out from the profile lookup.
        checkin_sequence: Fixed-format class — the check-in number the confirmation is recorded under on the
            profile, as the servicing agent states it; an integer, 1-based, written without decimals.

    Returns:
        A one-line confirmation string of the form "Check-in <entry reference> confirmed for profile
        <residency_profile_id>: number <checkin_sequence>, dated <today's date YYYY-MM-DD>." The entry
        reference is the new history entry's reference number; its presence (rather than a line beginning
        "Error") means the check-in entry now exists.
    """
    prof = ctx.find("residency_profiles", residency_profile_id=residency_profile_id)
    owner = prof[0].get("customer_id", "") if prof else ""
    program = prof[0].get("loan_program", "") if prof else ""
    today = ctx.now()[:10]
    rid = ctx.make_id("rcu_", residency_profile_id, checkin_sequence)
    ctx.create("residency_events", rid, residency_event_id=rid, residency_profile_id=residency_profile_id,
               customer_id=owner, event_type="residency_absence_checkin", loan_program=program,
               effective_date=today, certification_year="", notice_type="not_applicable",
               certifier_customer_id="", certification_method="not_applicable", residency_submission_id="",
               inspection_reason="not_applicable", inspection_fee=0.00, inspection_outcome="not_applicable",
               checkin_sequence=int(checkin_sequence), source_event_ref="")
    return (f"Check-in {rid} confirmed for profile {residency_profile_id}: number {int(checkin_sequence)}, "
            f"dated {today}.")


@tool(owner="agent", rw="write")
def record_return_home_baa2f4ef(ctx: ToolContext, residency_profile_id: str, residency_submission_id: str,
                                response_days: int) -> str:
    """End health-care absence monitoring on an occupancy certification profile because the borrowers came home.

    The servicing agent records, on the strength of the accepted return-home notice cited, that occupancy has
    resumed: the profile's status becomes current, its absence start date is cleared, and the due date of the
    open certification cycle becomes the date that lies the given number of calendar days after today. Nothing
    else on the profile changes. On success the profile shows status current, no absence start date and the new
    due date, and the receipt below is returned.

    Args:
        residency_profile_id: Id class — reference number of the occupancy certification profile under
            monitoring, as returned by the occupancy profile lookup for the borrower.
        residency_submission_id: Id class — reference number of the most recently received accepted return-home
            notice on file for the profile, as returned by the occupancy submission lookup.
        response_days: Fixed-format class — the calendar days from today to the due date the open certification
            cycle is to carry once occupancy has resumed, an integer written without decimals; negative when that
            due date lies before today.

    Returns:
        A one-line confirmation string of the form "Profile <residency_profile_id> back to current on return
        notice <residency_submission_id>; open cycle due <new due date YYYY-MM-DD>." Its presence (rather than a
        line beginning "Error") means the profile is current, its absence start date is empty and it carries
        that due date.
    """
    due = _Calendar.add_days(ctx.now()[:10], int(response_days))
    ctx.update("residency_profiles", residency_profile_id, status="current", absence_start_date="",
               certification_due_date=due)
    return (f"Profile {residency_profile_id} back to current on return notice {residency_submission_id}; "
            f"open cycle due {due}.")


@tool(owner="agent", rw="write")
def record_occupancy_certification_e8b1dc9f(ctx: ToolContext, residency_profile_id: str, residency_submission_id: str,
                                            certifier_customer_id: str, certification_method: str,
                                            effective_date: str, certification_year: int) -> str:
    """Record one signer's occupancy certification from an accepted certification form on file.

    The servicing agent adds one certification entry to the profile's occupancy history for the signer named,
    citing the accepted certification form, with the signing channel, the date the certification stands on and the
    certification year given. The entry is copied with the profile's primary borrower and loan program. The profile itself is
    not changed. On success the occupancy history lookup shows the new certification entry, and the receipt
    below is returned.

    Args:
        residency_profile_id: Id class — reference number of the occupancy certification profile the
            certification is recorded on, as returned by the occupancy profile lookup.
        residency_submission_id: Id class — reference number of the accepted occupancy certification form on
            file, as returned by the occupancy submission lookup.
        certifier_customer_id: Id class — customer reference number of the person who signed the form, as shown
            on the form's submission record in the occupancy submission lookup.
        certification_method: Enum class — the channel the signed certification came through, exactly one of:
            "mail" (a signed paper form returned by post);
            "servicing_portal" (a certification signed in the online servicing portal);
            "phone" (a certification given by the signer on a recorded call);
            "not_applicable" (the value carried by history entries that are not certifications; it describes no
            signing channel).
        effective_date: Fixed-format class — the date the recorded certification stands on, a calendar date
            written YYYY-MM-DD; never empty.
        certification_year: Fixed-format class — the certification year the signature is recorded under,
            written as a four-digit calendar year (YYYY), an integer without decimals.

    Returns:
        A one-line confirmation string of the form "Certification <entry reference> recorded on profile
        <residency_profile_id> for <certifier_customer_id>: <certification_method>, signed <effective_date>,
        certification year <certification_year>." The entry reference is the new history entry's reference
        number; its presence (rather than a line beginning "Error") means the certification entry now exists.
    """
    prof = ctx.find("residency_profiles", residency_profile_id=residency_profile_id)
    owner = prof[0].get("customer_id", "") if prof else ""
    program = prof[0].get("loan_program", "") if prof else ""
    rid = ctx.make_id("rcr_", residency_profile_id, residency_submission_id, certifier_customer_id,
                      certification_method, effective_date, certification_year)
    ctx.create("residency_events", rid, residency_event_id=rid, residency_profile_id=residency_profile_id,
               customer_id=owner, event_type="residency_certification_recorded", loan_program=program,
               effective_date=effective_date, certification_year=str(int(certification_year)),
               notice_type="not_applicable", certifier_customer_id=certifier_customer_id,
               certification_method=certification_method, residency_submission_id=residency_submission_id,
               inspection_reason="not_applicable", inspection_fee=0.00, inspection_outcome="not_applicable",
               checkin_sequence=0, source_event_ref="")
    return (f"Certification {rid} recorded on profile {residency_profile_id} for {certifier_customer_id}: "
            f"{certification_method}, signed {effective_date}, certification year {int(certification_year)}.")


@tool(owner="user", rw="write")
def confirm_return_home_701e433e(ctx: ToolContext, residency_profile_id: str, checkin_sequence: int) -> str:
    """Let a borrower who has come back home after a health-care stay confirm in person, today, that they live in the home again.

    The borrower personally confirms, for the occupancy certification profile named, that they have returned home
    and occupy it again. The confirmation is recorded as one check-in entry dated today in the profile's occupancy
    history, carrying the check-in number given, the profile's primary borrower and its loan program. The profile
    itself is not changed. On success the borrower hears the confirmation below, and the occupancy history lookup
    shows the new entry.

    Args:
        residency_profile_id: Id class — reference number of the borrower's occupancy certification profile, as
            the servicing agent reads it out from the profile lookup.
        checkin_sequence: Fixed-format class — the check-in number the confirmation is recorded under on the
            profile, as the servicing agent states it; an integer, 1-based, written without decimals.

    Returns:
        A one-line confirmation string of the form "Return confirmed as check-in <entry reference> on profile
        <residency_profile_id>: number <checkin_sequence>, dated <today's date YYYY-MM-DD>." The entry reference is
        the new history entry's reference number; its presence (rather than a line beginning "Error") means the
        check-in entry now exists.
    """
    prof = ctx.find("residency_profiles", residency_profile_id=residency_profile_id)
    owner = prof[0].get("customer_id", "") if prof else ""
    program = prof[0].get("loan_program", "") if prof else ""
    today = ctx.now()[:10]
    rid = ctx.make_id("rrh_", residency_profile_id, checkin_sequence)
    ctx.create("residency_events", rid, residency_event_id=rid, residency_profile_id=residency_profile_id,
               customer_id=owner, event_type="residency_absence_checkin", loan_program=program,
               effective_date=today, certification_year="", notice_type="not_applicable",
               certifier_customer_id="", certification_method="not_applicable", residency_submission_id="",
               inspection_reason="not_applicable", inspection_fee=0.00, inspection_outcome="not_applicable",
               checkin_sequence=int(checkin_sequence), source_event_ref="")
    return (f"Return confirmed as check-in {rid} on profile {residency_profile_id}: number {int(checkin_sequence)}, "
            f"dated {today}.")


class _Anniversary:
    """Calendar helper for the cycle-completion tool (not a tool)."""

    @staticmethod
    def next_after(due: str, closing: str) -> str:
        """The first closing anniversary strictly after the date given, as YYYY-MM-DD."""
        year = int(due[:4])
        month, day = int(closing[5:7]), int(closing[8:10])
        for y in (year, year + 1):
            d = day
            if month == 2 and day == 29 and not (y % 4 == 0 and (y % 100 != 0 or y % 400 == 0)):
                d = 28
            cand = f"{y:04d}-{month:02d}-{d:02d}"
            if cand > due:
                return cand
        return f"{year + 1:04d}-{month:02d}-{day:02d}"


@tool(owner="agent", rw="write")
def complete_certification_cycle_e152f965(ctx: ToolContext, residency_profile_id: str, last_certified_date: str) -> str:
    """Complete the open occupancy certification cycle of a profile.

    The servicing agent marks the profile's open certification cycle as complete: the profile's last certification
    date becomes the date given, its due date moves forward to the next anniversary of the monitored loan's closing
    date that falls after the current due date, and a profile that was pending its first certification or overdue
    becomes current. Nothing else on the profile changes. On success the profile lookup shows the new last
    certification date, the new due date and the status, and the receipt below is returned.

    Args:
        residency_profile_id: Id class — reference number of the occupancy certification profile whose open cycle
            is completed, as returned by the occupancy profile lookup for the borrower.
        last_certified_date: Fixed-format class — the date the completed cycle is recorded as certified, a calendar
            date written YYYY-MM-DD; never empty.

    Returns:
        A one-line confirmation string of the form "Cycle completed on profile <residency_profile_id>: certified
        <last_certified_date>, next due <new due date YYYY-MM-DD>, status <status>." Its presence (rather than a line
        beginning "Error") means the profile now carries that last certification date, due date and status.
    """
    prof = ctx.find("residency_profiles", residency_profile_id=residency_profile_id)
    row = prof[0] if prof else {}
    due = row.get("certification_due_date", "") or ""
    closing = ""
    if row.get("hecm_loan_id"):
        loans = ctx.find("hecm_loans", hecm_loan_id=row.get("hecm_loan_id"))
        closing = loans[0].get("closing_date", "") if loans else ""
    elif row.get("jumbo_loan_id"):
        loans = ctx.find("jumbo_loans", jumbo_loan_id=row.get("jumbo_loan_id"))
        closing = loans[0].get("closing_date", "") if loans else ""
    next_due = _Anniversary.next_after(due, closing) if (due and closing) else due
    status = row.get("status", "")
    if status in ("pending_first_certification", "overdue"):
        status = "current"
    ctx.update("residency_profiles", residency_profile_id, last_certified_date=last_certified_date,
               certification_due_date=next_due, status=status)
    return (f"Cycle completed on profile {residency_profile_id}: certified {last_certified_date}, next due "
            f"{next_due}, status {status}.")

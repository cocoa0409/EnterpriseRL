"""Hidden task tools for the referrals_and_authorizations difficulty of env_0055_military_health_plan_administrator
(Westbridge Military Health Services, TRICARE West Region). Each tool performs one atomic write on the
referral and authorization records; it judges no eligibility, prerequisite or amount - the representative
works those out from the published policy and the records and passes the result in.
"""

from erlbench import ToolContext, tool

@tool(owner="agent", rw="write")
def post_facility_day_use_bc338a65(ctx: ToolContext, referral_authorization_id: str, claim_number: str,
                                   line_number: int, service_date: str, units: int) -> str:
    """Post the inpatient days that one facility claim line uses against a skilled nursing facility or
    inpatient mental health authorization. One call adds exactly one use entry to the authorization's
    unit history, tied to the claim number and line number printed on the Explanation of Benefits and to
    a service date, and lowers the authorization's units remaining by the days posted. The
    authorization's status, validity span and servicing facility are not changed. Success is shown by a
    receipt carrying the new use entry's reference number.

    Args:
        referral_authorization_id: Id class — the reference number of the facility authorization the days
            are posted to, as returned by the referral and authorization lookup for the patient.
        claim_number: Verbatim class — the claim number of the facility claim line exactly as it appears on
            the claim line returned by the claim-line lookup, copied character for character with no
            reformatting (verbatim).
        line_number: Fixed-format class — the line number of that facility claim line within its claim, written
            as an integer >= 0 (in practice 1 or more), exactly as shown on the claim line.
        service_date: Fixed-format class — the service date recorded on the use entry: the first day of that
            facility line that the posting counts as used, written YYYY-MM-DD.
        units: Fixed-format class — the number of inpatient days the line uses against the authorization,
            a whole number written as an integer >= 0, counted in the authorization's unit of inpatient days.

    Returns:
        A text rendering of a dictionary with these fields: use_entry_id (text, the reference number of the
        new use entry), referral_authorization_id (text, the authorization posted to), units_posted (integer,
        the inpatient days posted), units_remaining (integer, the authorization's units remaining after the
        posting) and status ("posted" when the use entry was recorded).
    """
    rid = ctx.make_id("rul_", referral_authorization_id, claim_number, line_number, service_date, units)
    rows = ctx.find("referral_authorizations", referral_authorization_id=referral_authorization_id)
    holder = rows[0].get("customer_id") if rows else None
    ctx.create("referral_unit_ledger", rid, referral_unit_entry_id=rid,
               referral_authorization_id=referral_authorization_id, customer_id=holder,
               event_type="referral_units_consume", units=int(units), entry_date=ctx.now()[:10],
               grant_basis="not_applicable", extension_sequence=0, extended_valid_through="",
               service_date=service_date, claim_number=claim_number, line_number=int(line_number),
               release_reason="not_applicable")
    left = None
    if rows:
        left = int(rows[0].get("units_remaining") or 0) - int(units)
        ctx.update("referral_authorizations", referral_authorization_id, units_remaining=left)
    return str({"use_entry_id": rid, "referral_authorization_id": referral_authorization_id,
                "units_posted": int(units), "units_remaining": left, "status": "posted"})


@tool(owner="agent", rw="write")
def close_lapsed_authorization_515f616b(ctx: ToolContext, referral_authorization_id: str, closed_date: str,
                                        units_released: int) -> str:
    """Record that an approved referral or authorization has lapsed because its validity span has ended, and
    release the units it still carries. One call sets the authorization's status to expired with the given
    closing date, sets its units remaining to zero, and adds one release entry with the reason expiration to
    its unit history for the units released. Nothing else on the authorization changes. Success is shown by
    a receipt carrying the release entry's reference number and the expired status.

    Args:
        referral_authorization_id: Id class — the reference number of the authorization whose span has
            ended, as returned by the referral and authorization lookup for the patient.
        closed_date: Fixed-format class — the date the authorization is closed as expired, written
            YYYY-MM-DD; it is also the date of the release entry.
        units_released: Fixed-format class — the units released by the lapse, a whole number in the
            authorization's own unit of measure, written as an integer >= 0.

    Returns:
        A text rendering of a dictionary with these fields: release_entry_id (text, the reference number of
        the new release entry), referral_authorization_id (text, the authorization closed), status (text,
        "expired" once recorded), closed_date (text, YYYY-MM-DD) and units_released (integer, the units
        released by the lapse).
    """
    rid = ctx.make_id("rel_", referral_authorization_id, closed_date, units_released)
    rows = ctx.find("referral_authorizations", referral_authorization_id=referral_authorization_id)
    holder = rows[0].get("customer_id") if rows else None
    ctx.update("referral_authorizations", referral_authorization_id, status="expired", closed_date=closed_date,
               units_remaining=0)
    ctx.create("referral_unit_ledger", rid, referral_unit_entry_id=rid,
               referral_authorization_id=referral_authorization_id, customer_id=holder,
               event_type="referral_units_release", units=int(units_released), entry_date=closed_date,
               grant_basis="not_applicable", extension_sequence=0, extended_valid_through="", service_date="",
               claim_number="", line_number=0, release_reason="expiration")
    return str({"release_entry_id": rid, "referral_authorization_id": referral_authorization_id,
                "status": "expired", "closed_date": closed_date, "units_released": int(units_released)})


@tool(owner="agent", rw="write")
def issue_overturned_authorization_2ad92a55(ctx: ToolContext, referral_authorization_id: str, valid_from: str,
                                            valid_through: str, units_authorized: int) -> str:
    """Issue a denied referral or authorization whose medical necessity reconsideration was decided in the
    patient's favour. One call changes the authorization's status from denied to approved, records today as
    its decision date, sets its validity span and units authorized, clears its denial reason, sets its units
    remaining to the units authorized, and adds one grant entry on the basis of an appeal overturn to its unit
    history. The servicing provider, request details and referral number are not changed. Success is shown
    by a receipt carrying the grant entry's reference number and the approved status.

    Args:
        referral_authorization_id: Id class — the reference number of the denied authorization being issued,
            as returned by the referral and authorization lookup for the patient.
        valid_from: Fixed-format class — the first day of the validity span, written YYYY-MM-DD.
        valid_through: Fixed-format class — the last day of the validity span (inclusive), written
            YYYY-MM-DD.
        units_authorized: Fixed-format class — the units issued, a whole number in the authorization's own
            unit of measure (visits, inpatient days, hours or rental months), written as an integer >= 0.

    Returns:
        A text rendering of a dictionary with these fields: grant_entry_id (text, the reference number of the
        new grant entry), referral_authorization_id (text, the authorization issued), status (text, "approved"
        once recorded), valid_from and valid_through (text, YYYY-MM-DD) and units_authorized (integer, the
        units issued).
    """
    today = ctx.now()[:10]
    rid = ctx.make_id("grt_", referral_authorization_id, valid_from, valid_through, units_authorized)
    rows = ctx.find("referral_authorizations", referral_authorization_id=referral_authorization_id)
    holder = rows[0].get("customer_id") if rows else None
    ctx.update("referral_authorizations", referral_authorization_id, status="approved", decision_date=today,
               valid_from=valid_from, valid_through=valid_through, units_authorized=int(units_authorized),
               units_remaining=int(units_authorized), denial_reason="not_applicable")
    ctx.create("referral_unit_ledger", rid, referral_unit_entry_id=rid,
               referral_authorization_id=referral_authorization_id, customer_id=holder,
               event_type="referral_units_grant", units=int(units_authorized), entry_date=today,
               grant_basis="appeal_overturn", extension_sequence=0, extended_valid_through="", service_date="",
               claim_number="", line_number=0, release_reason="not_applicable")
    return str({"grant_entry_id": rid, "referral_authorization_id": referral_authorization_id,
                "status": "approved", "valid_from": valid_from, "valid_through": valid_through,
                "units_authorized": int(units_authorized)})


@tool(owner="user", rw="write")
def confirm_outpatient_cancellation_09e1d470(ctx: ToolContext, referral_authorization_id: str,
                                             units_released: int) -> str:
    """The patient (or the parent or guardian of a minor patient) confirms in person the cancellation of an
    approved outpatient or home-care referral or authorization they no longer need - one counted in visits,
    hours or rental months. One call records the patient's confirmed cancellation request, sets the
    authorization's status to cancelled with today as its closing date, sets its units remaining to zero, and
    adds one release entry with the reason cancellation to its unit history for the units released. A
    cancelled authorization is never reopened. Success is shown by a receipt carrying the cancellation
    request's reference number and the cancelled status.

    Args:
        referral_authorization_id: Id class — the reference number of the authorization the patient is
            cancelling, as the representative read it out from the patient's referral and authorization record.
        units_released: Fixed-format class — the units the cancellation releases, a whole number in the
            authorization's own unit of measure, written as an integer >= 0, exactly as the representative
            stated it.

    Returns:
        A text rendering of a dictionary with these fields: cancellation_request_id (text, the reference number
        of the confirmed cancellation request), release_entry_id (text, the reference number of the release
        entry), referral_authorization_id (text, the authorization cancelled), status (text, "cancelled" once
        recorded), closed_date (text, YYYY-MM-DD) and units_released (integer, the units released).
    """
    today = ctx.now()[:10]
    qid = ctx.make_id("rrq_", referral_authorization_id, units_released)
    rid = ctx.make_id("rel_", referral_authorization_id, today, units_released)
    rows = ctx.find("referral_authorizations", referral_authorization_id=referral_authorization_id)
    holder = rows[0].get("customer_id") if rows else None
    ctx.create("referral_requests", qid, referral_request_id=qid, customer_id=holder,
               referral_authorization_id=referral_authorization_id, request_kind="cancellation",
               outcome="confirmed", created_at=ctx.now())
    ctx.update("referral_authorizations", referral_authorization_id, status="cancelled", closed_date=today,
               units_remaining=0)
    ctx.create("referral_unit_ledger", rid, referral_unit_entry_id=rid,
               referral_authorization_id=referral_authorization_id, customer_id=holder,
               event_type="referral_units_release", units=int(units_released), entry_date=today,
               grant_basis="not_applicable", extension_sequence=0, extended_valid_through="", service_date="",
               claim_number="", line_number=0, release_reason="cancellation")
    return str({"cancellation_request_id": qid, "release_entry_id": rid,
                "referral_authorization_id": referral_authorization_id, "status": "cancelled",
                "closed_date": today, "units_released": int(units_released)})


@tool(owner="agent", rw="write")
def approve_pending_authorization_775ce183(ctx: ToolContext, referral_authorization_id: str, customer_id: str,
                                           variant_name: str, servicing_provider_id: str, valid_from: str,
                                           valid_through: str, units_authorized: int) -> str:
    """Approve a submitted referral or authorization request that is still awaiting its decision. One call
    changes the request's status from submitted to approved, records today as its decision date, sets its
    validity span and units authorized, sets its units remaining to the units authorized, and adds one grant
    entry on the basis of an initial approval to its unit history. The patient, authorization type and
    servicing provider named in the call are the ones on the request; they are recorded unchanged. Success is
    shown by a receipt carrying the grant entry's reference number and the approved status.

    Args:
        referral_authorization_id: Id class — the reference number of the submitted request being approved,
            as returned by the referral and authorization lookup for the patient.
        customer_id: Id class — the beneficiary reference number of the patient the request is for, as
            returned by the profile lookup.
        variant_name: Enum class — the authorization type on the request, exactly one of: Specialty Care
            Referral (a PCM referral to a specialist); Rehabilitative Therapy Referral (a PCM referral for
            therapy visits); Durable Medical Equipment Authorization (equipment rental months); Home Health Care
            Authorization (home visits for a homebound patient); Applied Behavior Analysis Authorization (ABA
            hours); Skilled Nursing Facility Authorization (skilled nursing facility days); Inpatient Mental
            Health Authorization (inpatient psychiatric days).
        servicing_provider_id: Id class — the provider directory reference number of the servicing provider
            on the request, as returned by the referral and authorization lookup.
        valid_from: Fixed-format class — the first day of the validity span, written YYYY-MM-DD.
        valid_through: Fixed-format class — the last day of the validity span (inclusive), written YYYY-MM-DD.
        units_authorized: Fixed-format class — the units approved, a whole number in the authorization's own
            unit of measure, written as an integer >= 0.

    Returns:
        A text rendering of a dictionary with these fields: grant_entry_id (text, the reference number of the
        new grant entry), referral_authorization_id (text, the request approved), status (text, "approved"
        once recorded), valid_from and valid_through (text, YYYY-MM-DD) and units_authorized (integer).
    """
    today = ctx.now()[:10]
    rid = ctx.make_id("grt_", referral_authorization_id, customer_id, variant_name, servicing_provider_id,
                      valid_from, valid_through, units_authorized)
    ctx.update("referral_authorizations", referral_authorization_id, status="approved", decision_date=today,
               customer_id=customer_id, variant_name=variant_name, servicing_provider_id=servicing_provider_id,
               valid_from=valid_from, valid_through=valid_through, units_authorized=int(units_authorized),
               units_remaining=int(units_authorized))
    ctx.create("referral_unit_ledger", rid, referral_unit_entry_id=rid,
               referral_authorization_id=referral_authorization_id, customer_id=customer_id,
               event_type="referral_units_grant", units=int(units_authorized), entry_date=today,
               grant_basis="initial_approval", extension_sequence=0, extended_valid_through="", service_date="",
               claim_number="", line_number=0, release_reason="not_applicable")
    return str({"grant_entry_id": rid, "referral_authorization_id": referral_authorization_id,
                "status": "approved", "valid_from": valid_from, "valid_through": valid_through,
                "units_authorized": int(units_authorized)})


@tool(owner="agent", rw="write")
def extend_authorization_stay_203c17fe(ctx: ToolContext, referral_authorization_id: str, extension_sequence: int,
                                       extended_valid_through: str, units: int) -> str:
    """Post an extension of an approved referral or authorization. One call adds one extension entry to the
    authorization's unit history with its sequence number, the units it adds and the new last day of the
    validity span, moves the authorization's validity span out to that day, and raises its units remaining
    by the units added. Status, servicing provider and earlier entries are not changed. Success is shown by a
    receipt carrying the extension entry's reference number and the new last day.

    Args:
        referral_authorization_id: Id class — the reference number of the approved authorization being
            extended, as returned by the referral and authorization lookup for the patient.
        extension_sequence: Fixed-format class — the number of this extension on the authorization (1 for the
            first, 2 for the second and so on), written as an integer >= 0.
        extended_valid_through: Fixed-format class — the new last day of the validity span (inclusive),
            written YYYY-MM-DD.
        units: Fixed-format class — the units the extension adds, a whole number in the authorization's own
            unit of measure, written as an integer >= 0.

    Returns:
        A text rendering of a dictionary with these fields: extension_entry_id (text, the reference number of
        the new extension entry), referral_authorization_id (text, the authorization extended),
        extension_sequence (integer), units_added (integer) and valid_through (text, YYYY-MM-DD, the new last
        day of the span) and units_remaining (integer, after the extension).
    """
    rid = ctx.make_id("ext_", referral_authorization_id, extension_sequence, extended_valid_through, units)
    rows = ctx.find("referral_authorizations", referral_authorization_id=referral_authorization_id)
    holder = rows[0].get("customer_id") if rows else None
    left = int(rows[0].get("units_remaining") or 0) + int(units) if rows else None
    ctx.create("referral_unit_ledger", rid, referral_unit_entry_id=rid,
               referral_authorization_id=referral_authorization_id, customer_id=holder,
               event_type="referral_units_extend", units=int(units), entry_date=ctx.now()[:10],
               grant_basis="not_applicable", extension_sequence=int(extension_sequence),
               extended_valid_through=extended_valid_through, service_date="", claim_number="", line_number=0,
               release_reason="not_applicable")
    if rows:
        ctx.update("referral_authorizations", referral_authorization_id, valid_through=extended_valid_through,
                   units_remaining=left)
    return str({"extension_entry_id": rid, "referral_authorization_id": referral_authorization_id,
                "extension_sequence": int(extension_sequence), "units_added": int(units),
                "valid_through": extended_valid_through, "units_remaining": left})


@tool(owner="user", rw="write")
def confirm_inpatient_closure_5bde1317(ctx: ToolContext, referral_authorization_id: str, units_released: int) -> str:
    """The patient (or the parent or guardian of a minor patient) confirms in person the cancellation of an
    approved skilled nursing facility or inpatient mental health authorization whose stay has ended and that
    is no longer needed - one counted in inpatient days. One call records the confirmed cancellation request,
    sets the authorization's status to cancelled with today as its closing date, sets its units remaining to
    zero, and adds one release entry with the reason cancellation to its unit history for the days released.
    A cancelled authorization is never reopened. Success is shown by a receipt carrying the cancellation
    request's reference number and the cancelled status.

    Args:
        referral_authorization_id: Id class — the reference number of the inpatient authorization being
            cancelled, as the representative read it out from the patient's referral and authorization record.
        units_released: Fixed-format class — the inpatient days the cancellation releases, a whole number
            written as an integer >= 0, exactly as the representative stated it.

    Returns:
        A text rendering of a dictionary with these fields: cancellation_request_id (text, the reference number
        of the confirmed cancellation request), release_entry_id (text, the reference number of the release
        entry), referral_authorization_id (text, the authorization cancelled), status (text, "cancelled" once
        recorded), closed_date (text, YYYY-MM-DD) and units_released (integer, the days released).
    """
    today = ctx.now()[:10]
    qid = ctx.make_id("rrq_", referral_authorization_id, units_released)
    rid = ctx.make_id("rel_", referral_authorization_id, today, units_released)
    rows = ctx.find("referral_authorizations", referral_authorization_id=referral_authorization_id)
    holder = rows[0].get("customer_id") if rows else None
    ctx.create("referral_requests", qid, referral_request_id=qid, customer_id=holder,
               referral_authorization_id=referral_authorization_id, request_kind="cancellation",
               outcome="confirmed", created_at=ctx.now())
    ctx.update("referral_authorizations", referral_authorization_id, status="cancelled", closed_date=today,
               units_remaining=0)
    ctx.create("referral_unit_ledger", rid, referral_unit_entry_id=rid,
               referral_authorization_id=referral_authorization_id, customer_id=holder,
               event_type="referral_units_release", units=int(units_released), entry_date=today,
               grant_basis="not_applicable", extension_sequence=0, extended_valid_through="", service_date="",
               claim_number="", line_number=0, release_reason="cancellation")
    return str({"cancellation_request_id": qid, "release_entry_id": rid,
                "referral_authorization_id": referral_authorization_id, "status": "cancelled",
                "closed_date": today, "units_released": int(units_released)})

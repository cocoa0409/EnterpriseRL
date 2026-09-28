"""Hidden task tools of the prior_authorization_services difficulty (category auth).
Output of erl-task-instantiate. Every tool is reached through unlock_* -> call_* and is named by
exactly one extended policy's target_tool in auth.extended.yaml. Each call performs one atomic
change on a Prairie Ridge prior authorization; no tool judges eligibility, timing or amounts.
"""

from erlbench import ToolContext, tool


# --------------------------------------------------------------------------- task 0
@tool(owner="agent", rw="write")
def release_expired_units_43b7942e(ctx: ToolContext, authorization_id: str, units_released: int) -> str:
    """Book the release of unused units on a Prairie Ridge prior authorization whose approval period
    has already ended. One call posts one release entry, marked as released because the approval
    expired, dated today, for the number of units given, and lowers the units-remaining balance
    shown on that authorization by the same number. The member and the provider then see those
    units as released: they can no longer be used on that authorization. Success is shown by a
    confirmation naming the release entry, the authorization and the units released.

    Args:
        authorization_id: Id class — the reference number of the ended prior authorization whose
            unused units are being released, as returned by the prior authorization lookup for the
            member.
        units_released: Fixed-format class — the number of units being released from the ended
            authorization, in the authorization's own unit basis, written as whole integer units,
            positive (the release entry records integer units, positive, and the balance on the
            authorization is kept in integer units).

    Returns:
        A confirmation sentence (text) stating the release entry reference (an identifier beginning
        with "aun_"), the authorization reference it was posted on, the whole number of units
        released, the posting date (YYYY-MM-DD, today) and the new units-remaining balance on the
        authorization (whole units). The presence of the release entry reference indicates the
        release was booked.
    """
    rows = ctx.find("auth_authorizations", authorization_id=authorization_id)
    auth = rows[0] if rows else {}
    units = int(units_released)
    rid = ctx.make_id("aun_", authorization_id, units, "expired")
    today = ctx.now()[:10]
    ctx.create("auth_units", rid, auth_unit_id=rid, authorization_id=authorization_id,
               customer_id=auth.get("customer_id", ""), event_type="auth_units_released",
               units=units, grant_type="not_applicable", release_reason="expired",
               claim_number="", service_date="", posted_date=today)
    remaining = int(auth.get("units_remaining") or 0) - units
    ctx.update("auth_authorizations", authorization_id, units_remaining=remaining)
    return (f"Release entry {rid} posted on authorization {authorization_id}: {units} unit(s) released "
            f"as expired on {today}; units remaining on the authorization now {remaining}.")


@tool(owner="agent", rw="write")
def record_transition_of_care_request_bf098d50(ctx: ToolContext, customer_id: str, membership_id: str,
                                               source_authorization_id: str, service_code: str,
                                               units_requested: int) -> str:
    """Record a new member's transition-of-care request with Prairie Ridge: a request that the
    authorization the member's prior health plan had given be honored here. One call opens one new
    prior authorization request, received today and to start today, marked as arising from
    transition of care and reviewed on the standard timeframe, for the service code and number of
    units given. It takes its authorization class, therapy discipline, requesting provider,
    servicing provider and network status from the member's earlier Prairie Ridge authorization
    named as its source, and it carries no prior-plan authorization number until one is supplied.
    The new request is visible at once in the member's list of prior authorizations with status
    submitted and its own authorization number. Success is shown by a confirmation carrying the new
    request's reference and authorization number.

    Args:
        customer_id: Id class — the member reference number of the member the request is for, as
            returned by the member profile lookup.
        membership_id: Id class — the reference number of the member's Prairie Ridge plan membership
            the request falls under, as returned by the plan membership lookup.
        source_authorization_id: Id class — the reference number of the member's earlier Prairie
            Ridge prior authorization for the same service from which the class and providers are
            taken, as returned by the prior authorization lookup for the member.
        service_code: Verbatim class — the CPT or HCPCS service code of the service to be honored,
            copied character for character exactly as it appears on the member's earlier Prairie
            Ridge authorization for that service, with no change of letters, digits or spacing
            (verbatim).
        units_requested: Fixed-format class — the number of units the transition-of-care request
            asks to honor, in the authorization class's unit basis, written as whole integer units.

    Returns:
        A confirmation sentence (text) stating the new request's reference (an identifier beginning
        with "auth_"), its authorization number (text of the form PA-YYMM-NNNNNN), its status
        (submitted), the date received (YYYY-MM-DD, today) and the whole number of units requested.
        The presence of the new reference and authorization number indicates the request was
        recorded.
    """
    rows = ctx.find("auth_authorizations", authorization_id=source_authorization_id)
    src = rows[0] if rows else {}
    units = int(units_requested)
    rid = ctx.make_id("auth_", customer_id, membership_id, source_authorization_id, service_code, units)
    today = ctx.now()[:10]
    auth_number = f"PA-{today[2:4]}{today[5:7]}-{int(rid[-6:], 16) % 1000000:06d}"
    ctx.create("auth_authorizations", rid, authorization_id=rid, customer_id=customer_id,
               membership_id=membership_id, variant_name=src.get("variant_name", ""), status="submitted",
               auth_number=auth_number, service_code=service_code,
               therapy_discipline=src.get("therapy_discipline", "not_applicable"),
               requesting_provider_npi=src.get("requesting_provider_npi", ""),
               servicing_provider_npi=src.get("servicing_provider_npi", ""),
               network_status=src.get("network_status", "in_network"), review_type="standard",
               request_origin="transition_of_care", prior_plan_auth_number="", received_date=today,
               decision_date="", start_date=today, end_date="", units_requested=units, units_approved=0,
               units_remaining=0, denial_reason="not_applicable", closed_date="")
    return (f"Transition-of-care request {rid} recorded: authorization number {auth_number}, status submitted, "
            f"received {today}, {units} unit(s) requested.")


@tool(owner="user", rw="write")
def request_review_time_extension_2522d00e(ctx: ToolContext, authorization_id: str, extension_days: int) -> str:
    """The member's own request that Prairie Ridge take more time to decide one of the member's
    undecided prior authorization requests. One call records, dated today, a deadline extension
    asked for by the member that adds the given number of calendar days to the decision deadline of
    that request, together with the written notice of the extension of review time mailed to the
    member the same day. The member then sees the extension and the mailed notice on the request's
    history. Success is shown by a confirmation carrying the extension entry and notice references.

    Args:
        authorization_id: Id class — the reference number of the member's undecided prior
            authorization request whose decision deadline is being extended, as the agent reads it
            to the member from the prior authorization records.
        extension_days: Fixed-format class — the number of calendar days added to the decision
            deadline, written as whole integer days.

    Returns:
        A confirmation sentence (text) stating the deadline-extension entry reference (an
        identifier beginning with "aac_"), the notice entry reference (also beginning with "aac_"),
        the request reference, the whole number of days added, and the date recorded and mailed
        (YYYY-MM-DD, today). The presence of both references indicates the extension was recorded.
    """
    rows = ctx.find("auth_authorizations", authorization_id=authorization_id)
    auth = rows[0] if rows else {}
    days = int(extension_days)
    today = ctx.now()[:10]
    customer_id = auth.get("customer_id", "")
    rid = ctx.make_id("aac_", authorization_id, days, "timeline_extension")
    ctx.create("auth_actions", rid, auth_action_id=rid, authorization_id=authorization_id,
               customer_id=customer_id, event_type="auth_timeline_extension", action_date=today,
               requested_by="member", provider_certified_urgent=False, requested_units=0,
               requested_end_date="", extension_days=days, notice_type="not_applicable",
               delivery_channel="not_applicable")
    nid = ctx.make_id("aac_", authorization_id, days, "extension_notice")
    ctx.create("auth_actions", nid, auth_action_id=nid, authorization_id=authorization_id,
               customer_id=customer_id, event_type="auth_notice", action_date=today,
               requested_by="not_applicable", provider_certified_urgent=False, requested_units=0,
               requested_end_date="", extension_days=0, notice_type="extension_of_review_time",
               delivery_channel="mail")
    return (f"Deadline extension {rid} recorded on request {authorization_id} at the member's request: "
            f"{days} day(s) added on {today}; notice {nid} of the extension of review time mailed {today}.")


# --------------------------------------------------------------------------- task 1
@tool(owner="agent", rw="write")
def void_authorization_7849b1e5(ctx: ToolContext, authorization_id: str, units_released: int) -> str:
    """Void one of the member's approved Prairie Ridge prior authorizations at the member's request
    because the service will not be used, releasing unused units. One call changes the
    authorization's status to voided with today as its closed date, posts one release entry marked
    as released because the approval was voided for the number of units given, and lowers the
    units-remaining balance shown on the authorization by that number. The member and the provider
    then see the authorization as voided; it is never reopened. Success is shown by a confirmation
    naming the authorization, the release entry and the units released.

    Args:
        authorization_id: Id class — the reference number of the approved prior authorization being
            voided, as returned by the prior authorization lookup for the member.
        units_released: Fixed-format class — the number of units released by the void, in the
            authorization's own unit basis, written as whole integer units, positive (the release
            entry records integer units, positive, and the balance is kept in integer units).

    Returns:
        A confirmation sentence (text) stating the authorization reference, its new status
        (voided), the closed date (YYYY-MM-DD, today), the release entry reference (an identifier
        beginning with "aun_"), the whole number of units released and the new units-remaining
        balance (whole units). The status voided and the release entry reference indicate the void
        was recorded.
    """
    rows = ctx.find("auth_authorizations", authorization_id=authorization_id)
    auth = rows[0] if rows else {}
    units = int(units_released)
    today = ctx.now()[:10]
    remaining = int(auth.get("units_remaining") or 0) - units
    ctx.update("auth_authorizations", authorization_id, status="voided", closed_date=today,
               units_remaining=remaining)
    rid = ctx.make_id("aun_", authorization_id, units, "voided")
    ctx.create("auth_units", rid, auth_unit_id=rid, authorization_id=authorization_id,
               customer_id=auth.get("customer_id", ""), event_type="auth_units_released",
               units=units, grant_type="not_applicable", release_reason="voided",
               claim_number="", service_date="", posted_date=today)
    return (f"Authorization {authorization_id} voided on {today}; release entry {rid}: {units} unit(s) released; "
            f"units remaining now {remaining}.")


@tool(owner="agent", rw="write")
def change_servicing_provider_0d360835(ctx: ToolContext, authorization_id: str, new_servicing_provider_npi: str,
                                       network_status: str, units_carried: int) -> str:
    """Move one of the member's approved Prairie Ridge prior authorizations to another servicing
    provider for the same service. One call replaces the servicing provider on the authorization
    with the new provider's NPI, records that provider's network status, and sets the
    authorization's units-remaining balance to the number of units carried over to the new
    provider; the service, the approval dates and the authorization number stay as they are. The
    member and both providers then see the new servicing provider and the carried balance on the
    authorization. Success is shown by a confirmation naming the authorization, the new provider
    and the units carried.

    Args:
        authorization_id: Id class — the reference number of the approved prior authorization whose
            servicing provider changes, as returned by the prior authorization lookup for the member.
        new_servicing_provider_npi: Fixed-format class — the National Provider Identifier of the
            provider who will deliver the service from now on, as a 10-digit NPI with no spaces or
            punctuation, as the member reads it from the new provider's paperwork.
        network_status: Enum class — the new provider's network status: in_network when the new
            provider is in Prairie Ridge's network; out_of_network when the new provider is not in
            Prairie Ridge's network.
        units_carried: Fixed-format class — the number of units carried over to the new provider,
            in the authorization's unit basis, written as whole integer units.

    Returns:
        A confirmation sentence (text) stating the authorization reference, the new servicing
        provider's 10-digit NPI, its network status (in_network or out_of_network) and the whole
        number of units carried, which is now the authorization's units-remaining balance. The
        presence of the new NPI in the confirmation indicates the change was recorded.
    """
    units = int(units_carried)
    ctx.update("auth_authorizations", authorization_id, servicing_provider_npi=new_servicing_provider_npi,
               network_status=network_status, units_remaining=units)
    return (f"Authorization {authorization_id}: servicing provider changed to NPI {new_servicing_provider_npi} "
            f"({network_status}); {units} unit(s) carried over as the units remaining.")


@tool(owner="user", rw="write")
def file_extension_request_1d826295(ctx: ToolContext, authorization_id: str, requested_units: int,
                                    requested_end_date: str) -> str:
    """The member's own request that Prairie Ridge extend one of the member's approved (or recently
    ended) prior authorizations. One call files, dated today, one extension request made by the
    member on that authorization, stating the additional units asked for and the end date asked
    for. The member then sees the extension request on the authorization's history. Success is
    shown by a confirmation carrying the extension request reference.

    Args:
        authorization_id: Id class — the reference number of the member's prior authorization the
            extension is asked for, as the agent reads it to the member from the prior authorization
            records.
        requested_units: Fixed-format class — the additional units the member asks for, in the
            authorization's unit basis, written as whole integer units.
        requested_end_date: Fixed-format class — the end date the member asks the authorization to
            run to, written as a calendar date in the format YYYY-MM-DD.

    Returns:
        A confirmation sentence (text) stating the extension request reference (an identifier
        beginning with "aac_"), the authorization reference, the whole number of units asked for,
        the end date asked for (YYYY-MM-DD) and the date filed (YYYY-MM-DD, today). The presence of
        the extension request reference indicates the request was filed.
    """
    rows = ctx.find("auth_authorizations", authorization_id=authorization_id)
    auth = rows[0] if rows else {}
    units = int(requested_units)
    today = ctx.now()[:10]
    rid = ctx.make_id("aac_", authorization_id, units, requested_end_date, "extension_request")
    ctx.create("auth_actions", rid, auth_action_id=rid, authorization_id=authorization_id,
               customer_id=auth.get("customer_id", ""), event_type="auth_extension_request", action_date=today,
               requested_by="member", provider_certified_urgent=False, requested_units=units,
               requested_end_date=requested_end_date, extension_days=0, notice_type="not_applicable",
               delivery_channel="not_applicable")
    return (f"Extension request {rid} filed by the member on authorization {authorization_id} on {today}: "
            f"{units} unit(s) asked for, end date asked {requested_end_date}.")


@tool(owner="agent", rw="write")
def record_extension_d36e0acf(ctx: ToolContext, authorization_id: str, units_added: int, new_end_date: str) -> str:
    """Record an extension of one of the member's approved Prairie Ridge prior authorizations. One
    call moves the authorization's end date to the new end date given, adds the given units to its
    total units approved and to its units-remaining balance, and posts one grant entry for those
    units marked as granted by extension, dated today. The member and the servicing provider then
    see the longer approval and the added units. Success is shown by a confirmation naming the
    grant entry, the units added and the new end date.

    Args:
        authorization_id: Id class — the reference number of the approved prior authorization being
            extended, as returned by the prior authorization lookup for the member.
        units_added: Fixed-format class — the units the extension adds, in the authorization's unit
            basis, written as whole integer units, positive (the grant entry records integer units,
            positive, and the totals are kept in integer units).
        new_end_date: Fixed-format class — the authorization's end date after the extension, written
            as a calendar date in the format YYYY-MM-DD.

    Returns:
        A confirmation sentence (text) stating the grant entry reference (an identifier beginning
        with "aun_"), the authorization reference, the whole number of units added, the new end date
        (YYYY-MM-DD), the new total units approved and the new units-remaining balance (whole
        units). The presence of the grant entry reference indicates the extension was recorded.
    """
    rows = ctx.find("auth_authorizations", authorization_id=authorization_id)
    auth = rows[0] if rows else {}
    units = int(units_added)
    today = ctx.now()[:10]
    approved = int(auth.get("units_approved") or 0) + units
    remaining = int(auth.get("units_remaining") or 0) + units
    ctx.update("auth_authorizations", authorization_id, end_date=new_end_date, units_approved=approved,
               units_remaining=remaining)
    rid = ctx.make_id("aun_", authorization_id, units, new_end_date, "extension")
    ctx.create("auth_units", rid, auth_unit_id=rid, authorization_id=authorization_id,
               customer_id=auth.get("customer_id", ""), event_type="auth_units_granted", units=units,
               grant_type="extension", release_reason="not_applicable", claim_number="", service_date="",
               posted_date=today)
    return (f"Extension recorded on authorization {authorization_id}: grant entry {rid} adds {units} unit(s); "
            f"end date now {new_end_date}; units approved {approved}; units remaining {remaining}.")

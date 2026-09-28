"""Hidden task tools of the referral_and_authorization_management difficulty (Linden Ridge Medical Group).
Path: env/env_0025_multispecialty_physician_group/tasks/referral_and_authorization_management/task_tools.py

Each tool performs exactly one atomic write on a referral or prior authorization and takes the value the
agent has already worked out from the published policy; no tool checks eligibility, status, timing or any
other business precondition, and no tool computes a policy figure.
"""

from erlbench import ToolContext, tool


class _Calendar:
    """Proleptic Gregorian calendar arithmetic on 'YYYY-MM-DD' strings, in whole integers (no clock)."""

    @staticmethod
    def shift(day: str, days: int) -> str:
        y, m, d = (int(p) for p in str(day)[:10].split("-"))
        # days since 1970-01-01 (civil-from-days / days-from-civil, integer only)
        y -= m <= 2
        era = (y if y >= 0 else y - 399) // 400
        yoe = y - era * 400
        doy = (153 * (m + (-3 if m > 2 else 9)) + 2) // 5 + d - 1
        doe = yoe * 365 + yoe // 4 - yoe // 100 + doy
        z = era * 146097 + doe - 719468 + int(days)
        z += 719468
        era = (z if z >= 0 else z - 146096) // 146097
        doe = z - era * 146097
        yoe = (doe - doe // 1460 + doe // 36524 - doe // 146096) // 365
        y = yoe + era * 400
        doy = doe - (365 * yoe + yoe // 4 - yoe // 100)
        mp = (5 * doy + 2) // 153
        d = doy - (153 * mp + 2) // 5 + 1
        m = mp + (3 if mp < 10 else -9)
        y += m <= 2
        return f"{y:04d}-{m:02d}-{d:02d}"


@tool(owner="user", rw="write")
def confirm_imaging_site_change_a21d40f9(ctx: ToolContext, referral_id: str, new_rendering_site: str,
                                         estimated_patient_share_usd: float) -> str:
    """The patient moves an approved imaging or procedure prior authorization to another site and signs
    for the pre-service estimate stated for that site.

    One call changes the site named on the authorization to the site given (units and validity dates are
    left exactly as they are) and files the patient's signed provider-change request on the authorization,
    carrying the estimated amount the patient accepted; the request is recorded as signed by the patient
    at the moment of the call. Afterwards the authorization shows the new site, and the request list shows
    one provider-change request with status patient_signed.

    Args:
        referral_id: Id class — reference number of the prior authorization being moved, as shown on the
            authorization returned by the referral lookup for this patient.
        new_rendering_site: Verbatim class — the site the study is moved to, copied exactly as the clinic
            location appears on the patient's booked study, character for character, preserving wording,
            digits and punctuation, with no translation, normalisation, summarisation, addition or deletion (verbatim).
        estimated_patient_share_usd: Fixed-format class — the pre-service estimate of the patient's own
            payment for the study at the new site that the patient signs for; US dollars, a non-negative
            number with exactly 2 decimal places (rounded half up to the cent), no currency sign.

    Returns:
        dict with: request_id (str, reference of the signed provider-change request); referral_id (str, the
        authorization moved); rendering_provider (str, the site now named on the authorization);
        estimated_patient_share_usd (float, 2 decimal places, the estimate signed for); request_status (str,
        always patient_signed, which indicates the change is recorded). A returned request_id means success.
    """
    share = round(float(estimated_patient_share_usd), 2)
    ref = (ctx.find("referrals", referral_id=referral_id) or [{}])[0]
    rid = ctx.make_id("rrq_", referral_id, new_rendering_site, share)
    ctx.update("referrals", referral_id, rendering_provider=new_rendering_site)
    ctx.create("referral_requests", rid, referral_request_id=rid, customer_id=ref.get("customer_id", ""),
               referral_id=referral_id, request_type="provider_change", request_status="patient_signed",
               created_at=ctx.now())
    return str({"request_id": rid, "referral_id": referral_id, "rendering_provider": new_rendering_site,
                "estimated_patient_share_usd": share, "request_status": "patient_signed"})


@tool(owner="agent", rw="write")
def extend_study_authorization_f1ccb059(ctx: ToolContext, referral_id: str, added_validity_days: int) -> str:
    """Record an extension decision on an approved or exhausted imaging or procedure prior authorization
    that lengthens its validity without adding any study or procedure.

    One call moves the authorization's last valid date later by the number of calendar days given, adds
    one to its count of extensions granted, marks the latest decision as an extension and dates that
    decision today. Units remaining, the named site and the starting valid date are left unchanged. The
    patient can then see the new last valid date on the authorization.

    Args:
        referral_id: Id class — reference number of the prior authorization being extended, as shown on the
            authorization returned by the referral lookup for this patient.
        added_validity_days: Fixed-format class — number of calendar days added to the current last valid
            date; a positive integer count of days, no fraction.

    Returns:
        dict with: referral_id (str, the authorization extended); valid_through (str, YYYY-MM-DD, the new last
        valid date); extension_count (int, extensions granted so far including this one);
        last_decision_basis (str, always extension); decision_date (str, YYYY-MM-DD, today). A returned
        valid_through later than the prior last valid date means success.
    """
    ref = (ctx.find("referrals", referral_id=referral_id) or [{}])[0]
    new_through = _Calendar.shift(ref.get("valid_through") or ctx.now()[:10], int(added_validity_days))
    count = int(ref.get("extension_count") or 0) + 1
    ctx.update("referrals", referral_id, valid_through=new_through, extension_count=count,
               last_decision_basis="extension", decision_date=ctx.now()[:10])
    return str({"referral_id": referral_id, "valid_through": new_through, "extension_count": count,
                "last_decision_basis": "extension", "decision_date": ctx.now()[:10]})


@tool(owner="user", rw="write")
def sign_oon_cost_share_acknowledgement_95eb7797(ctx: ToolContext, referral_id: str,
                                                 acknowledged_cost_share_usd: float) -> str:
    """The patient signs the out-of-network cost-share acknowledgement on an Out-of-Network Referral,
    accepting the stated per-visit cost share for continued visits with the outside provider.

    One call files a cost-share acknowledgement on the referral, recorded as signed by the patient at the
    moment of the call and carrying the per-visit amount the patient accepted. Nothing else on the
    referral changes. Afterwards the referral's request list shows the acknowledgement with status
    patient_signed.

    Args:
        referral_id: Id class — reference number of the Out-of-Network Referral, as shown on the referral
            returned by the referral lookup for this patient.
        acknowledged_cost_share_usd: Fixed-format class — the per-visit amount the patient accepts paying for
            each continued visit; US dollars, a non-negative number with exactly 2 decimal places (rounded
            half up to the cent), no currency sign.

    Returns:
        dict with: request_id (str, reference of the signed acknowledgement); referral_id (str, the referral
        acknowledged); acknowledged_cost_share_usd (float, 2 decimal places, the amount signed for);
        request_status (str, always patient_signed, which indicates the acknowledgement is on file). A
        returned request_id means success.
    """
    share = round(float(acknowledged_cost_share_usd), 2)
    ref = (ctx.find("referrals", referral_id=referral_id) or [{}])[0]
    rid = ctx.make_id("rrq_", referral_id, share)
    ctx.create("referral_requests", rid, referral_request_id=rid, customer_id=ref.get("customer_id", ""),
               referral_id=referral_id, request_type="oon_acknowledgement", request_status="patient_signed",
               created_at=ctx.now())
    return str({"request_id": rid, "referral_id": referral_id, "acknowledged_cost_share_usd": share,
                "request_status": "patient_signed"})


@tool(owner="agent", rw="write")
def lengthen_referral_validity_fab859e3(ctx: ToolContext, referral_id: str, added_validity_days: int) -> str:
    """Move the last valid date of a visit referral (a referral whose units are visits) later by a given
    number of calendar days.

    One call changes only the referral's last valid date. The count of extensions, the latest decision,
    the units remaining and the provider are left unchanged. The patient can then see the new last valid
    date on the referral.

    Args:
        referral_id: Id class — reference number of the visit referral, as shown on the referral returned by
            the referral lookup for this patient.
        added_validity_days: Fixed-format class — number of calendar days added to the current last valid
            date; a positive integer count of days, no fraction.

    Returns:
        dict with: referral_id (str, the referral lengthened); previous_valid_through (str, YYYY-MM-DD, the last
        valid date the referral carried until this call); valid_through (str, YYYY-MM-DD, the new last valid date). A returned
        valid_through later than previous_valid_through means success.
    """
    ref = (ctx.find("referrals", referral_id=referral_id) or [{}])[0]
    before = ref.get("valid_through") or ctx.now()[:10]
    new_through = _Calendar.shift(before, int(added_validity_days))
    ctx.update("referrals", referral_id, valid_through=new_through)
    return str({"referral_id": referral_id, "previous_valid_through": before, "valid_through": new_through})


@tool(owner="agent", rw="write")
def grant_extension_visits_d2c34b29(ctx: ToolContext, referral_id: str, extension_visits: int) -> str:
    """Post the visits an extension adds to a visit referral and record the extension decision.

    One call books a unit grant with reason extension, dated today, for the number of visits given; raises
    the referral's units remaining by that number; returns an exhausted referral to approved (an approved
    one stays approved); adds one to the count of extensions granted; marks the latest decision as an
    extension and dates it today. The validity dates and the provider are left unchanged. The patient can
    then see the added visits on the referral and the grant in its unit history.

    Args:
        referral_id: Id class — reference number of the visit referral, as shown on the referral returned by
            the referral lookup for this patient.
        extension_visits: Fixed-format class — number of visits the extension adds; integer > 0, units (one
            unit is one visit), a whole number with no fraction.

    Returns:
        dict with: grant_id (str, reference of the unit grant booked); referral_id (str, the referral);
        units_granted (int, visits added); units_remaining (int, visits now covered); status (str, approved);
        extension_count (int, extensions granted so far including this one). A returned grant_id means success.
    """
    ref = (ctx.find("referrals", referral_id=referral_id) or [{}])[0]
    gid = ctx.make_id("rfe_", referral_id, int(extension_visits))
    ctx.create("referral_events", gid, referral_event_id=gid, referral_id=referral_id,
               customer_id=ref.get("customer_id", ""), event_type="referral_units_granted",
               unit_date=ctx.now()[:10], units=int(extension_visits), grant_reason="extension",
               encounter_number="", source_category="referral", applies_to_unit_event_id="",
               restore_reason="none", forfeit_reason="none")
    remaining = int(ref.get("units_remaining") or 0) + int(extension_visits)
    count = int(ref.get("extension_count") or 0) + 1
    ctx.update("referrals", referral_id, units_remaining=remaining, status="approved",
               extension_count=count, last_decision_basis="extension", decision_date=ctx.now()[:10])
    return str({"grant_id": gid, "referral_id": referral_id, "units_granted": int(extension_visits),
                "units_remaining": remaining, "status": "approved", "extension_count": count})

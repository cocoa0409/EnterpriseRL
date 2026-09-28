"""Hidden task tools of the primary_care_assignment difficulty (category pcp).

Each tool records one specialist-referral entry on a member's primary care assignment and
nothing else. They are hidden: their names are published only through the extended policies'
target_tool, and they are reached through unlock_* -> call_*. None of them checks eligibility,
status, validity or any prerequisite; the visits written are the value passed in.
"""

from erlbench import ToolContext, tool


@tool(owner="agent", rw="write")
def carry_over_referral_de0684af(ctx: ToolContext, pcp_assignment_id: str, referral_number: str,
                                 specialist_npi: str, issue_date: str, referral_visits: int) -> str:
    """Carry an unexpired specialist referral that a member's earlier primary care provider issued
    onto the member's current primary care assignment. One call adds one referral entry to the
    current assignment's referral history, under the referral's original number and original issue
    date (so its expiry is unchanged), as a single-visit-type referral to the named specialist
    covering the number of visits given. Nothing else on the member's record changes; the member
    and the specialist's office see the referral listed under the current primary care provider.

    Args:
        pcp_assignment_id: Id class — reference number of the member's current primary care
            assignment the referral is carried onto, as it appears on the member's primary care assignment record.
        referral_number: Verbatim class — the referral number of the earlier referral being
            carried, copied character for character from the earlier assignment's referral entry in
            the member's referral history, with no change to letters, digits or hyphens (verbatim).
        specialist_npi: Fixed-format class — NPI of the specialist named on the earlier referral,
            written as the 10-digit NPI with digits only and no spaces or punctuation.
        issue_date: Fixed-format class — the original issue date of the earlier referral, written
            as a calendar date in YYYY-MM-DD format exactly as it appears on the earlier entry.
        referral_visits: Fixed-format class — the number of specialist visits the carried referral
            covers on the current assignment, a whole non-negative number in integer visits with no
            decimals.

    Returns:
        A text rendering of a dictionary receipt with these fields: status (the text "carried" when
        the entry was recorded), pcp_event_id (reference of the new referral history entry, text),
        pcp_assignment_id (the current assignment the referral now sits on, text), referral_number
        (the carried referral number, text), specialist_npi (10-digit NPI, text), issue_date
        (YYYY-MM-DD, the original issue date kept on the entry) and referral_visits (integer visits
        recorded). A receipt with status "carried" means the referral is now listed on the current
        assignment.
    """
    visits = int(referral_visits)
    owner_rows = ctx.find("pcp_assignments", pcp_assignment_id=pcp_assignment_id)
    owner_id = owner_rows[0].get("customer_id", "") if owner_rows else ""
    rid = ctx.make_id("pev_", pcp_assignment_id, referral_number, specialist_npi, issue_date, visits)
    ctx.create("pcp_events", rid, pcp_event_id=rid, pcp_assignment_id=pcp_assignment_id,
               customer_id=owner_id, event_type="pcp_referral_issue",
               event_date=issue_date, change_reason="not_applicable", request_channel="not_applicable",
               requested_provider_npi="", notice_reason="not_applicable", effective_date="",
               referral_number=referral_number, specialist_npi=specialist_npi, referral_type="single",
               referral_visits=visits, outreach_method="not_applicable")
    return str({"status": "carried", "pcp_event_id": rid, "pcp_assignment_id": pcp_assignment_id,
                "referral_number": referral_number, "specialist_npi": specialist_npi,
                "issue_date": issue_date, "referral_visits": visits})


@tool(owner="agent", rw="write")
def issue_standing_referral_d300bbad(ctx: ToolContext, pcp_assignment_id: str, specialist_npi: str,
                                     referral_visits: int) -> str:
    """Issue a standing referral on a member's active primary care assignment, letting the member
    see one specialist repeatedly for an ongoing condition. One call adds one standing-type referral
    entry, dated today and given a new referral number, to the assignment's referral history,
    naming the specialist and the number of visits the referral covers. Nothing else on the
    member's record changes; the member and the specialist's office can quote the new referral
    number from the receipt.

    Args:
        pcp_assignment_id: Id class — reference number of the member's active primary care
            assignment the standing referral is written on, as it appears on the member's primary care assignment record.
        specialist_npi: Fixed-format class — NPI of the specialist the standing referral names,
            written as the 10-digit NPI with digits only and no spaces or punctuation.
        referral_visits: Fixed-format class — the number of specialist visits the standing
            referral covers, a whole non-negative number in integer visits with no decimals.

    Returns:
        A text rendering of a dictionary receipt with these fields: status (the text "issued" when
        the referral was recorded), pcp_event_id (reference of the new referral history entry,
        text), referral_number (the new referral number in the form RF-YYMM-NNNNN, text),
        referral_type (always "standing"), specialist_npi (10-digit NPI, text), issue_date (today's
        date, YYYY-MM-DD) and referral_visits (integer visits recorded). A receipt with status
        "issued" means the standing referral is in force on the assignment.
    """
    visits = int(referral_visits)
    owner_rows = ctx.find("pcp_assignments", pcp_assignment_id=pcp_assignment_id)
    owner_id = owner_rows[0].get("customer_id", "") if owner_rows else ""
    rid = ctx.make_id("pev_", pcp_assignment_id, "standing", specialist_npi, visits)
    today = ctx.now()[:10]
    number = f"RF-{today[2:4]}{today[5:7]}-{int(rid[-8:], 16) % 100000:05d}"
    ctx.create("pcp_events", rid, pcp_event_id=rid, pcp_assignment_id=pcp_assignment_id,
               customer_id=owner_id, event_type="pcp_referral_issue",
               event_date=today, change_reason="not_applicable", request_channel="not_applicable",
               requested_provider_npi="", notice_reason="not_applicable", effective_date="",
               referral_number=number, specialist_npi=specialist_npi, referral_type="standing",
               referral_visits=visits, outreach_method="not_applicable")
    return str({"status": "issued", "pcp_event_id": rid, "referral_number": number,
                "referral_type": "standing", "specialist_npi": specialist_npi, "issue_date": today,
                "referral_visits": visits})


@tool(owner="user", rw="write")
def elect_continuity_of_care_ec21b6d4(ctx: ToolContext, pcp_assignment_id: str, provider_npi: str,
                                      referral_visits: int) -> str:
    """The member elects, in person, to keep seeing their primary care provider who is leaving the
    network, under continuity of care. One call records the member's election as one continuity
    referral entry, dated today and given a new referral number, on the member's active primary care
    assignment, naming the leaving provider and the number of visits the member may have with that
    provider after the provider's network exit date. Nothing else on the member's record changes;
    the member receives the referral number to give the provider's office.

    Args:
        pcp_assignment_id: Id class — reference number of the member's active primary care
            assignment with the provider who is leaving, as the representative reads it from the
            member's primary care assignment record and gives it to the member.
        provider_npi: Fixed-format class — NPI of the leaving primary care provider the member will
            keep seeing, written as the 10-digit NPI with digits only and no spaces or punctuation.
        referral_visits: Fixed-format class — the number of continuity visits with the leaving
            provider that the election covers, a whole number of at least one in integer visits
            with no decimals.

    Returns:
        A text rendering of a dictionary receipt with these fields: status (the text "elected" when
        the election was recorded), pcp_event_id (reference of the new referral history entry,
        text), referral_number (the continuity referral number in the form RF-YYMM-NNNNN, text),
        provider_npi (10-digit NPI of the leaving provider, text), election_date (today's date,
        YYYY-MM-DD) and referral_visits (integer continuity visits recorded). A receipt with status
        "elected" means the member's continuity of care is on record.
    """
    visits = int(referral_visits)
    owner_rows = ctx.find("pcp_assignments", pcp_assignment_id=pcp_assignment_id)
    owner_id = owner_rows[0].get("customer_id", "") if owner_rows else ""
    rid = ctx.make_id("pev_", pcp_assignment_id, "continuity", provider_npi, visits)
    today = ctx.now()[:10]
    number = f"RF-{today[2:4]}{today[5:7]}-{int(rid[-8:], 16) % 100000:05d}"
    ctx.create("pcp_events", rid, pcp_event_id=rid, pcp_assignment_id=pcp_assignment_id,
               customer_id=owner_id, event_type="pcp_referral_issue",
               event_date=today, change_reason="not_applicable", request_channel="not_applicable",
               requested_provider_npi="", notice_reason="not_applicable", effective_date="",
               referral_number=number, specialist_npi=provider_npi, referral_type="single",
               referral_visits=visits, outreach_method="not_applicable")
    return str({"status": "elected", "pcp_event_id": rid, "referral_number": number,
                "provider_npi": provider_npi, "election_date": today, "referral_visits": visits})


@tool(owner="agent", rw="write")
def issue_specialist_referral_96d4855f(ctx: ToolContext, pcp_assignment_id: str, specialist_npi: str,
                                       referral_visits: int) -> str:
    """Issue a single specialist referral on a member's active primary care assignment, sending the
    member to one named in-network specialist. One call adds one single-type referral entry, dated
    today and given a new referral number, to the assignment's referral history, naming the
    specialist and the number of visits the referral covers. Nothing else on the member's record
    changes; the member and the specialist's office can quote the new referral number from the
    receipt.

    Args:
        pcp_assignment_id: Id class — reference number of the member's active primary care
            assignment the referral is written on, as it appears on the member's primary care assignment record.
        specialist_npi: Fixed-format class — NPI of the specialist the referral names, written as
            the 10-digit NPI with digits only and no spaces or punctuation.
        referral_visits: Fixed-format class — the number of specialist visits the referral covers,
            a whole non-negative number in integer visits with no decimals.

    Returns:
        A text rendering of a dictionary receipt with these fields: status (the text "issued" when
        the referral was recorded), pcp_event_id (reference of the new referral history entry,
        text), referral_number (the new referral number in the form RF-YYMM-NNNNN, text),
        referral_type (always "single"), specialist_npi (10-digit NPI, text), issue_date (today's
        date, YYYY-MM-DD) and referral_visits (integer visits recorded). A receipt with status
        "issued" means the referral is in force on the assignment.
    """
    visits = int(referral_visits)
    owner_rows = ctx.find("pcp_assignments", pcp_assignment_id=pcp_assignment_id)
    owner_id = owner_rows[0].get("customer_id", "") if owner_rows else ""
    rid = ctx.make_id("pev_", pcp_assignment_id, "single", specialist_npi, visits)
    today = ctx.now()[:10]
    number = f"RF-{today[2:4]}{today[5:7]}-{int(rid[-8:], 16) % 100000:05d}"
    ctx.create("pcp_events", rid, pcp_event_id=rid, pcp_assignment_id=pcp_assignment_id,
               customer_id=owner_id, event_type="pcp_referral_issue",
               event_date=today, change_reason="not_applicable", request_channel="not_applicable",
               requested_provider_npi="", notice_reason="not_applicable", effective_date="",
               referral_number=number, specialist_npi=specialist_npi, referral_type="single",
               referral_visits=visits, outreach_method="not_applicable")
    return str({"status": "issued", "pcp_event_id": rid, "referral_number": number,
                "referral_type": "single", "specialist_npi": specialist_npi, "issue_date": today,
                "referral_visits": visits})


@tool(owner="user", rw="write")
def request_second_opinion_76735634(ctx: ToolContext, pcp_assignment_id: str, specialist_npi: str,
                                    referral_visits: int) -> str:
    """The member requests, in person, a no-cost second opinion from an in-network specialist of the
    member's own choosing. One call records the member's request as one second-opinion referral
    entry, dated today and given a new referral number, on the member's active primary care
    assignment, naming the chosen specialist and the number of visits the second opinion covers.
    Nothing else on the member's record changes; the member receives the referral number to give
    the chosen specialist's office when booking.

    Args:
        pcp_assignment_id: Id class — reference number of the member's active primary care
            assignment, as the representative reads it from the member's primary care assignment record and gives it
            to the member.
        specialist_npi: Fixed-format class — NPI of the specialist the member chose for the second
            opinion, written as the 10-digit NPI with digits only and no spaces or punctuation.
        referral_visits: Fixed-format class — the number of visits the second opinion covers, a
            whole number of at least one in integer visits with no decimals.

    Returns:
        A text rendering of a dictionary receipt with these fields: status (the text "requested"
        when the request was recorded), pcp_event_id (reference of the new referral history entry,
        text), referral_number (the second-opinion referral number in the form RF-YYMM-NNNNN,
        text), specialist_npi (10-digit NPI of the chosen specialist, text), request_date (today's
        date, YYYY-MM-DD) and referral_visits (integer visits recorded). A receipt with status
        "requested" means the second opinion is authorised on the assignment.
    """
    visits = int(referral_visits)
    owner_rows = ctx.find("pcp_assignments", pcp_assignment_id=pcp_assignment_id)
    owner_id = owner_rows[0].get("customer_id", "") if owner_rows else ""
    rid = ctx.make_id("pev_", pcp_assignment_id, "second_opinion", specialist_npi, visits)
    today = ctx.now()[:10]
    number = f"RF-{today[2:4]}{today[5:7]}-{int(rid[-8:], 16) % 100000:05d}"
    ctx.create("pcp_events", rid, pcp_event_id=rid, pcp_assignment_id=pcp_assignment_id,
               customer_id=owner_id, event_type="pcp_referral_issue",
               event_date=today, change_reason="not_applicable", request_channel="not_applicable",
               requested_provider_npi="", notice_reason="not_applicable", effective_date="",
               referral_number=number, specialist_npi=specialist_npi, referral_type="single",
               referral_visits=visits, outreach_method="not_applicable")
    return str({"status": "requested", "pcp_event_id": rid, "referral_number": number,
                "specialist_npi": specialist_npi, "request_date": today, "referral_visits": visits})

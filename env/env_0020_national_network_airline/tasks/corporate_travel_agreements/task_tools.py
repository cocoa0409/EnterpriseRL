"""Hidden task tools for the corporate_travel_agreements difficulty (Crestline Corporate Travel Agreements).

Each tool makes one atomic write on a corporate travel agreement and returns a receipt. No tool checks a
policy condition: the agent decides from the published policies and the records whether and with which
values to call it.
"""

from erlbench import ToolContext, tool


@tool(owner="agent", rw="write")
def assess_invoice_late_fee_9e8e2547(ctx: ToolContext, business_account_id: str, invoice_number: str,
                                     due_date: str, amount: float) -> str:
    """Charge a late fee on one invoice of a corporate travel agreement.

    The agent books one late-fee entry against the named invoice of the agreement, dated today. The fee
    is added to the amount the company owes on its invoices, so the agreement's open invoice balance rises
    by the fee. Afterwards the fee appears in the agreement's invoice history as a late fee on that
    invoice number, alongside the invoice's charges and payments. The receipt confirms the entry.

    Args:
        business_account_id: Id class — reference number of the corporate travel agreement record the
            invoice belongs to, as returned by the corporate agreement lookup.
        invoice_number: Fixed-format class — the invoice the fee is charged on, written as INV- followed
            by 9 digits exactly as it appears on the invoice entries of the agreement.
        due_date: Fixed-format class — the due date of that invoice, in YYYY-MM-DD format, exactly as it
            appears on the invoice's charge entry.
        amount: Fixed-format class — the late fee in USD, a positive amount rounded to 2 decimal places
            (cents); never an empty value.

    Returns:
        A dictionary rendered as text with keys: status ("late_fee_charged" on success),
        invoice_entry_id (reference number of the new late-fee entry), invoice_number (the invoice
        charged), amount (the fee in USD, 2 decimal places), entry_date (today's date, YYYY-MM-DD) and
        invoice_balance (the agreement's open invoice balance in USD after the fee).
    """
    fee = round(float(amount), 2)
    rid = ctx.make_id("binv_", business_account_id, invoice_number, due_date, fee)
    found = ctx.find("business_holdings", business_account_id=business_account_id)
    agreement = found[0] if found else {}
    today = ctx.now()[:10]
    ctx.create("business_invoices", rid, invoice_entry_id=rid, business_account_id=business_account_id,
               customer_id=agreement.get("customer_id"), event_type="business_late_fee",
               invoice_number=invoice_number, entry_date=today, due_date=due_date, amount=fee,
               source_ticket_id=None, payment_reference="")
    balance = round(float(agreement.get("invoice_balance") or 0) + fee, 2)
    if agreement:
        ctx.update("business_holdings", business_account_id, invoice_balance=balance)
    return str({"status": "late_fee_charged", "invoice_entry_id": rid, "invoice_number": invoice_number,
                "amount": fee, "entry_date": today, "invoice_balance": balance})


@tool(owner="agent", rw="write")
def post_card_ticket_points_2b97bc4a(ctx: ToolContext, business_account_id: str, source_ticket_id: str,
                                     segment_number: int, traveler_customer_id: str, spend_usd: float,
                                     points: int) -> str:
    """Credit company points and agreement-year spend for one flown segment of a ticket booked under a
    corporate travel agreement and paid by card.

    The agent posts, dated today, one points entry for the flown segment and the matching spend entry
    that adds the segment's eligible spend to the agreement year. The agreement's points balance rises by
    the points and its agreement-year spend rises by the spend. Afterwards both entries appear in the
    agreement's points and spend activity against that ticket and segment. The receipt confirms them.

    Args:
        business_account_id: Id class — reference number of the corporate travel agreement record that
            earns the points, as returned by the corporate agreement lookup.
        source_ticket_id: Id class — reference number of the ticket record whose segment was flown, as
            returned by the ticket lookup.
        segment_number: Fixed-format class — position of the flown segment on the ticket, an integer >= 0
            (1 for the first segment), as shown on the ticket's flown-coupon entry.
        traveler_customer_id: Id class — customer reference number of the roster traveler who flew the
            segment, as returned by the roster or ticket lookup.
        spend_usd: Fixed-format class — the segment's eligible spend in USD rounded to 2 decimal places.
        points: Fixed-format class — the company points credited for the segment, a whole number written
            as an integer >= 0.

    Returns:
        A dictionary rendered as text with keys: status ("points_posted" on success),
        points_entry_id (reference number of the points entry), spend_entry_id (reference number of the
        spend entry), points (points credited, integer), spend_usd (spend added in USD, 2 decimal places),
        activity_date (today's date, YYYY-MM-DD) and point_balance (the agreement's points balance after
        the entry, integer).
    """
    pts = int(points)
    spend = round(float(spend_usd), 2)
    seg = int(segment_number)
    found = ctx.find("business_holdings", business_account_id=business_account_id)
    agreement = found[0] if found else {}
    today = ctx.now()[:10]
    pid = ctx.make_id("bact_", "accrual", business_account_id, source_ticket_id, seg, traveler_customer_id,
                      spend, pts)
    sid = ctx.make_id("bact_", "spend", business_account_id, source_ticket_id, seg, traveler_customer_id,
                      spend, pts)
    common = dict(business_account_id=business_account_id, customer_id=agreement.get("customer_id"),
                  activity_date=today, source_ticket_id=source_ticket_id, segment_number=seg,
                  traveler_customer_id=traveler_customer_id, bonus_reason="", redemption_type="",
                  award_description="", earned_month="", agreement_year_start="")
    ctx.create("business_activity", pid, business_activity_id=pid, event_type="business_points_accrual",
               points=pts, spend_usd=spend, **common)
    ctx.create("business_activity", sid, business_activity_id=sid, event_type="business_spend_post",
               points=0, spend_usd=spend, **common)
    balance = int(agreement.get("point_balance") or 0) + pts
    year_spend = round(float(agreement.get("spend_this_agreement_year") or 0) + spend, 2)
    if agreement:
        ctx.update("business_holdings", business_account_id, point_balance=balance,
                   spend_this_agreement_year=year_spend)
    return str({"status": "points_posted", "points_entry_id": pid, "spend_entry_id": sid, "points": pts,
                "spend_usd": spend, "activity_date": today, "point_balance": balance})


@tool(owner="user", rw="write")
def redeem_gold_status_award_92a33401(ctx: ToolContext, business_account_id: str, traveler_customer_id: str,
                                      points: int) -> str:
    """Redeem company points for a Summit Gold status award for one roster traveler.

    The company's travel manager confirms the redemption: one redemption entry for a Summit Gold status
    award is booked on the agreement, dated today, naming the traveler who receives the award. The
    agreement's points balance falls by the points redeemed. Afterwards the award appears in the
    agreement's points activity as a status award for that traveler. The receipt confirms the redemption.

    Args:
        business_account_id: Id class — reference number of the corporate travel agreement record whose
            points are redeemed, as given to the travel manager by the agent from the agreement lookup.
        traveler_customer_id: Id class — customer reference number of the roster traveler who receives
            the award, as given to the travel manager by the agent from the roster lookup.
        points: Fixed-format class — the company points redeemed for the award, a whole number written as
            an integer >= 0.

    Returns:
        A dictionary rendered as text with keys: status ("status_award_redeemed" on success),
        redemption_entry_id (reference number of the redemption entry), award ("summit_gold"),
        points (points redeemed, integer), activity_date (today's date, YYYY-MM-DD) and point_balance
        (the agreement's points balance after the redemption, integer).
    """
    pts = int(points)
    found = ctx.find("business_holdings", business_account_id=business_account_id)
    agreement = found[0] if found else {}
    today = ctx.now()[:10]
    rid = ctx.make_id("bact_", "status_award", business_account_id, traveler_customer_id, pts)
    ctx.create("business_activity", rid, business_activity_id=rid, business_account_id=business_account_id,
               customer_id=agreement.get("customer_id"), event_type="business_points_redemption",
               activity_date=today, points=pts, spend_usd=0.0, source_ticket_id=None, segment_number=0,
               traveler_customer_id=traveler_customer_id, bonus_reason="", redemption_type="status_award",
               award_description="summit_gold", earned_month="", agreement_year_start="")
    balance = int(agreement.get("point_balance") or 0) - pts
    if agreement:
        ctx.update("business_holdings", business_account_id, point_balance=balance)
    return str({"status": "status_award_redeemed", "redemption_entry_id": rid, "award": "summit_gold",
                "points": pts, "activity_date": today, "point_balance": balance})


@tool(owner="agent", rw="write")
def claim_retro_segment_points_a26ae9c7(ctx: ToolContext, business_account_id: str, source_ticket_id: str,
                                        segment_number: int, traveler_customer_id: str, spend_usd: float,
                                        points: int) -> str:
    """Credit a retroactive points claim for one flown segment of a ticket the company booked without its
    corporate travel agreement.

    The agent posts, dated today, one points entry crediting the claimed segment to the agreement and the
    matching spend entry that adds the segment's eligible spend to the agreement year. The agreement's
    points balance rises by the points and its agreement-year spend rises by the spend. Afterwards both
    entries appear in the agreement's points and spend activity against that ticket and segment. The
    receipt confirms them.

    Args:
        business_account_id: Id class — reference number of the corporate travel agreement record the
            claim is credited to, as returned by the corporate agreement lookup.
        source_ticket_id: Id class — reference number of the ticket record whose segment is claimed, as
            returned by the ticket lookup.
        segment_number: Fixed-format class — position of the claimed flown segment on the ticket, an
            integer >= 0 (1 for the first segment), as shown on the ticket's flown-coupon entry.
        traveler_customer_id: Id class — customer reference number of the roster traveler who flew the
            segment, as returned by the roster lookup.
        spend_usd: Fixed-format class — the segment's eligible spend credited to the agreement year, in USD
            rounded to 2 decimal places.
        points: Fixed-format class — the company points credited for the claim, a whole number written as
            an integer >= 0.

    Returns:
        A dictionary rendered as text with keys: status ("claim_credited" on success), points_entry_id
        (reference number of the points entry), spend_entry_id (reference number of the spend entry),
        points (points credited, integer), spend_usd (spend added in USD, 2 decimal places), activity_date
        (today's date, YYYY-MM-DD) and point_balance (the agreement's points balance after the claim,
        integer).
    """
    pts = int(points)
    spend = round(float(spend_usd), 2)
    seg = int(segment_number)
    found = ctx.find("business_holdings", business_account_id=business_account_id)
    agreement = found[0] if found else {}
    today = ctx.now()[:10]
    pid = ctx.make_id("bact_", "claim", business_account_id, source_ticket_id, seg, traveler_customer_id, spend, pts)
    sid = ctx.make_id("bact_", "claim_spend", business_account_id, source_ticket_id, seg, traveler_customer_id,
                      spend, pts)
    common = dict(business_account_id=business_account_id, customer_id=agreement.get("customer_id"),
                  activity_date=today, source_ticket_id=source_ticket_id, segment_number=seg,
                  traveler_customer_id=traveler_customer_id, bonus_reason="", redemption_type="",
                  award_description="", earned_month="", agreement_year_start="")
    ctx.create("business_activity", pid, business_activity_id=pid, event_type="business_points_accrual",
               points=pts, spend_usd=spend, **common)
    ctx.create("business_activity", sid, business_activity_id=sid, event_type="business_spend_post",
               points=0, spend_usd=spend, **common)
    balance = int(agreement.get("point_balance") or 0) + pts
    year_spend = round(float(agreement.get("spend_this_agreement_year") or 0) + spend, 2)
    if agreement:
        ctx.update("business_holdings", business_account_id, point_balance=balance,
                   spend_this_agreement_year=year_spend)
    return str({"status": "claim_credited", "points_entry_id": pid, "spend_entry_id": sid, "points": pts,
                "spend_usd": spend, "activity_date": today, "point_balance": balance})


@tool(owner="agent", rw="write")
def credit_enrollment_bonus_fc1a1a80(ctx: ToolContext, business_account_id: str, points: int) -> str:
    """Credit the one-time enrollment bonus to a corporate travel agreement's company points.

    The agent books, dated today, one bonus entry with the ground "enrollment bonus", tied to the
    agreement's approval date. The agreement's points balance rises by the bonus. Afterwards the bonus
    appears in the agreement's points activity as an enrollment bonus. The receipt confirms the entry.

    Args:
        business_account_id: Id class — reference number of the corporate travel agreement record that
            receives the bonus, as returned by the corporate agreement lookup.
        points: Fixed-format class — the bonus points credited, a whole number written as an
            integer >= 0.

    Returns:
        A dictionary rendered as text with keys: status ("enrollment_bonus_credited" on success),
        bonus_entry_id (reference number of the bonus entry), points (points credited, integer),
        agreement_year_start (the agreement's approval date the bonus is tied to, YYYY-MM-DD),
        activity_date (today's date, YYYY-MM-DD) and point_balance (the agreement's points balance after
        the bonus, integer).
    """
    pts = int(points)
    found = ctx.find("business_holdings", business_account_id=business_account_id)
    agreement = found[0] if found else {}
    today = ctx.now()[:10]
    start = agreement.get("approved_date") or ""
    rid = ctx.make_id("bact_", "enrollment_bonus", business_account_id, pts)
    ctx.create("business_activity", rid, business_activity_id=rid, business_account_id=business_account_id,
               customer_id=agreement.get("customer_id"), event_type="business_bonus_points", activity_date=today,
               points=pts, spend_usd=0.0, source_ticket_id=None, segment_number=0, traveler_customer_id=None,
               bonus_reason="enrollment_bonus", redemption_type="", award_description="", earned_month="",
               agreement_year_start=start)
    balance = int(agreement.get("point_balance") or 0) + pts
    if agreement:
        ctx.update("business_holdings", business_account_id, point_balance=balance)
    return str({"status": "enrollment_bonus_credited", "bonus_entry_id": rid, "points": pts,
                "agreement_year_start": start, "activity_date": today, "point_balance": balance})


@tool(owner="agent", rw="write")
def credit_milestone_bonus_a908f78d(ctx: ToolContext, business_account_id: str, agreement_year_start: str,
                                    points: int) -> str:
    """Credit the spend-milestone bonus of one agreement year to a corporate travel agreement's company
    points.

    The agent books, dated today, one bonus entry with the ground "spend milestone" for the agreement year
    that starts on the given date. The agreement's points balance rises by the bonus. Afterwards the bonus
    appears in the agreement's points activity as a spend-milestone bonus for that agreement year. The
    receipt confirms the entry.

    Args:
        business_account_id: Id class — reference number of the corporate travel agreement record that
            receives the bonus, as returned by the corporate agreement lookup.
        agreement_year_start: Fixed-format class — first day of the agreement year the milestone belongs
            to, in YYYY-MM-DD format.
        points: Fixed-format class — the bonus points credited, a whole number written as an
            integer >= 0.

    Returns:
        A dictionary rendered as text with keys: status ("milestone_bonus_credited" on success),
        bonus_entry_id (reference number of the bonus entry), points (points credited, integer),
        agreement_year_start (the agreement year, YYYY-MM-DD), activity_date (today's date, YYYY-MM-DD) and
        point_balance (the agreement's points balance after the bonus, integer).
    """
    pts = int(points)
    found = ctx.find("business_holdings", business_account_id=business_account_id)
    agreement = found[0] if found else {}
    today = ctx.now()[:10]
    rid = ctx.make_id("bact_", "spend_milestone", business_account_id, agreement_year_start, pts)
    ctx.create("business_activity", rid, business_activity_id=rid, business_account_id=business_account_id,
               customer_id=agreement.get("customer_id"), event_type="business_bonus_points", activity_date=today,
               points=pts, spend_usd=0.0, source_ticket_id=None, segment_number=0, traveler_customer_id=None,
               bonus_reason="spend_milestone", redemption_type="", award_description="", earned_month="",
               agreement_year_start=agreement_year_start)
    balance = int(agreement.get("point_balance") or 0) + pts
    if agreement:
        ctx.update("business_holdings", business_account_id, point_balance=balance)
    return str({"status": "milestone_bonus_credited", "bonus_entry_id": rid, "points": pts,
                "agreement_year_start": agreement_year_start, "activity_date": today, "point_balance": balance})


@tool(owner="user", rw="write")
def redeem_domestic_award_ffdd59aa(ctx: ToolContext, business_account_id: str, traveler_customer_id: str,
                                   points: int) -> str:
    """Redeem company points for a domestic Crestline Main Cabin round-trip award for one roster traveler.

    The company's travel manager confirms the redemption: one redemption entry for a domestic Main Cabin
    round-trip award is booked on the agreement, dated today, naming the traveler who will fly it. The
    agreement's points balance falls by the points redeemed. Afterwards the award appears in the
    agreement's points activity as an award-ticket redemption for that traveler, ready for ticketing. The
    receipt confirms the redemption.

    Args:
        business_account_id: Id class — reference number of the corporate travel agreement record whose
            points are redeemed, as given to the travel manager by the agent from the agreement lookup.
        traveler_customer_id: Id class — customer reference number of the roster traveler who will fly the
            award, as given to the travel manager by the agent from the roster lookup.
        points: Fixed-format class — the company points redeemed for the award, a whole number written as
            an integer >= 0.

    Returns:
        A dictionary rendered as text with keys: status ("award_redeemed" on success),
        redemption_entry_id (reference number of the redemption entry), award
        ("domestic_main_round_trip"), points (points redeemed, integer), activity_date (today's date,
        YYYY-MM-DD) and point_balance (the agreement's points balance after the redemption, integer).
    """
    pts = int(points)
    found = ctx.find("business_holdings", business_account_id=business_account_id)
    agreement = found[0] if found else {}
    today = ctx.now()[:10]
    rid = ctx.make_id("bact_", "award_ticket", business_account_id, traveler_customer_id, pts)
    ctx.create("business_activity", rid, business_activity_id=rid, business_account_id=business_account_id,
               customer_id=agreement.get("customer_id"), event_type="business_points_redemption",
               activity_date=today, points=pts, spend_usd=0.0, source_ticket_id=None, segment_number=0,
               traveler_customer_id=traveler_customer_id, bonus_reason="", redemption_type="award_ticket",
               award_description="domestic_main_round_trip", earned_month="", agreement_year_start="")
    balance = int(agreement.get("point_balance") or 0) - pts
    if agreement:
        ctx.update("business_holdings", business_account_id, point_balance=balance)
    return str({"status": "award_redeemed", "redemption_entry_id": rid, "award": "domestic_main_round_trip",
                "points": pts, "activity_date": today, "point_balance": balance})

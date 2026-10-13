"""Hidden task tools of the seller_standing_reviews_account_actions difficulty (Seller Performance Standing).

Each tool performs one atomic write on a seller's standing record and returns a receipt. No tool
checks eligibility, prerequisites or amounts; those are settled from the published policy and the
records before the call.
"""

from erlbench import ToolContext, tool



@tool(owner="agent", rw="write")
def grant_clean_span_relief_513362ca(ctx: ToolContext, standing_id: str, violation_ref: str,
                                     violation_type: str, points: int) -> str:
    """Book a clean-span relief on a seller's performance standing record: Northloop takes the given
    number of violation points off the seller's active violation points as relief for a clean span,
    recorded as a points-expiry entry dated today against one policy violation. On success the
    seller's active violation points shown on the standing record drop by exactly that number and the
    entry appears in the seller's standing activity with today's date, the violation reference, its
    type and the points taken off. The receipt reports the new entry reference and the active points
    before and after.

    Args:
        standing_id: Id class — the reference number identifying the seller performance standing record of the seller, read from the standing record lookup before the call.
        violation_ref: Id class — the policy violation reference number the relief entry is booked against, read from the seller's standing activity before the call.
        violation_type: Enum class — the kind of policy violation the entry is booked against, copied from that violation's record; exactly one of: listing_policy (the violation was recorded as a listing policy breach), restricted_product (the violation was recorded for listing a restricted product), intellectual_property (the violation was recorded on an intellectual property complaint), inauthentic_complaint (the violation was recorded for filing an inauthentic complaint), product_authenticity (the violation was recorded for an authenticity concern about the product), review_manipulation (the violation was recorded for manipulating reviews).
        points: Fixed-format class — the number of violation points taken off as relief, a positive whole number of points (integer points, no decimals).

    Returns:
        A dictionary receipt: entry_id (string, reference of the new points-expiry entry), standing_id
        (string, the standing record), violation_ref (string, the violation the entry is booked
        against), points (integer points taken off), active_points_before (integer active violation
        points before the entry) and active_points_after (integer active violation points after the
        entry). A returned entry_id means the relief is booked and the standing record already shows
        active_points_after.
    """
    rid = ctx.make_id("sev_", standing_id, violation_ref, violation_type, points, "clean_span")
    rec = (ctx.find("standing_records", standing_id=standing_id) or [{}])[0]
    before = int(rec.get("violation_points") or 0)
    after = before - int(points)
    ctx.create("standing_events", rid, standing_event_id=rid, standing_id=standing_id,
               customer_id=rec.get("customer_id"), event_type="standing_points_expiry",
               event_date=ctx.now()[:10], violation_ref=violation_ref, violation_type=violation_type,
               points=int(points))
    ctx.update("standing_records", standing_id, violation_points=after)
    return str({"entry_id": rid, "standing_id": standing_id, "violation_ref": violation_ref,
                "points": int(points), "active_points_before": before, "active_points_after": after})


@tool(owner="user", rw="write")
def apply_action_plan_relief_841772f9(ctx: ToolContext, standing_id: str, violation_ref: str,
                                      violation_type: str, points: int) -> str:
    """The seller applies, on their own account, for action-plan relief after working through the
    account health action plan for their listings: the given number of violation points is taken off
    the seller's active violation points and recorded as a points-expiry entry dated today against one
    policy violation. On success the seller's active violation points shown on the standing record
    drop by exactly that number and the entry appears in the seller's standing activity with today's
    date, the violation reference, its type and the points taken off. The receipt reports the new
    entry reference and the active points before and after.

    Args:
        standing_id: Id class — the reference number identifying the seller performance standing record of the seller, as given to the seller by the support agent from the standing record lookup.
        violation_ref: Id class — the policy violation reference number the relief entry is booked against, as given to the seller by the support agent from the standing activity.
        violation_type: Enum class — the kind of policy violation the entry is booked against, copied from that violation's record; exactly one of: listing_policy (the violation was recorded as a listing policy breach), restricted_product (the violation was recorded for listing a restricted product), intellectual_property (the violation was recorded on an intellectual property complaint), inauthentic_complaint (the violation was recorded for filing an inauthentic complaint), product_authenticity (the violation was recorded for an authenticity concern about the product), review_manipulation (the violation was recorded for manipulating reviews).
        points: Fixed-format class — the number of violation points the seller applies to have taken off, a positive whole number of points (integer points, no decimals), as worked out and told to the seller by the support agent.

    Returns:
        A dictionary receipt: entry_id (string, reference of the new points-expiry entry), standing_id
        (string, the standing record), violation_ref (string, the violation the entry is booked
        against), points (integer points taken off), active_points_before (integer active violation
        points before the entry) and active_points_after (integer active violation points after the
        entry). A returned entry_id means the relief is booked and the standing record already shows
        active_points_after.
    """
    rid = ctx.make_id("sev_", standing_id, violation_ref, violation_type, points, "action_plan")
    rec = (ctx.find("standing_records", standing_id=standing_id) or [{}])[0]
    before = int(rec.get("violation_points") or 0)
    after = before - int(points)
    ctx.create("standing_events", rid, standing_event_id=rid, standing_id=standing_id,
               customer_id=rec.get("customer_id"), event_type="standing_points_expiry",
               event_date=ctx.now()[:10], violation_ref=violation_ref, violation_type=violation_type,
               points=int(points))
    ctx.update("standing_records", standing_id, violation_points=after)
    return str({"entry_id": rid, "standing_id": standing_id, "violation_ref": violation_ref,
                "points": int(points), "active_points_before": before, "active_points_after": after})


@tool(owner="agent", rw="write")
def book_listing_violation_expiry_caba69b5(ctx: ToolContext, standing_id: str, violation_ref: str,
        violation_type: str, points: int) -> str:
    """Book the expiry of a listing policy or restricted product violation on a seller's performance
    standing record: the given number of violation points expire and are recorded as a points-expiry
    entry dated today against that violation. On success the seller's active violation points shown on
    the standing record drop by exactly that number and the entry appears in the seller's standing
    activity with today's date, the violation reference, its type and the points expired. The receipt
    reports the new entry reference and the active points before and after.

    Args:
        standing_id: Id class — the reference number identifying the seller performance standing record of the seller, read from the standing record lookup before the call.
        violation_ref: Id class — the policy violation reference number the entry is booked against, read from the seller's standing activity before the call.
        violation_type: Enum class — the kind of policy violation the entry is booked against, copied from that violation's record; exactly one of: listing_policy (the violation was recorded as a listing policy breach), restricted_product (the violation was recorded for listing a restricted product), intellectual_property (the violation was recorded on an intellectual property complaint), inauthentic_complaint (the violation was recorded for filing an inauthentic complaint), product_authenticity (the violation was recorded for an authenticity concern about the product), review_manipulation (the violation was recorded for manipulating reviews).
        points: Fixed-format class — the number of violation points that expire, a positive whole number of points (integer points, no decimals).

    Returns:
        A dictionary receipt: entry_id (string, reference of the new points-expiry entry), standing_id
        (string, the standing record), violation_ref (string, the violation the entry is booked
        against), points (integer points taken off), active_points_before (integer active violation
        points before the entry) and active_points_after (integer active violation points after the
        entry). A returned entry_id means the entry is booked and the standing record already shows
        active_points_after.
    """
    rid = ctx.make_id("sev_", standing_id, violation_ref, violation_type, points, "listing_expiry")
    rec = (ctx.find("standing_records", standing_id=standing_id) or [{}])[0]
    before = int(rec.get("violation_points") or 0)
    after = before - int(points)
    ctx.create("standing_events", rid, standing_event_id=rid, standing_id=standing_id,
               customer_id=rec.get("customer_id"), event_type="standing_points_expiry",
               event_date=ctx.now()[:10], violation_ref=violation_ref, violation_type=violation_type,
               points=int(points))
    ctx.update("standing_records", standing_id, violation_points=after)
    return str({"entry_id": rid, "standing_id": standing_id, "violation_ref": violation_ref,
                "points": int(points), "active_points_before": before, "active_points_after": after})


@tool(owner="agent", rw="write")
def book_serious_step_down_71a20607(ctx: ToolContext, standing_id: str, violation_ref: str,
        violation_type: str, points: int) -> str:
    """Book the step-down of a serious policy violation (an intellectual property, inauthentic
    complaint, product authenticity or review manipulation violation) on a seller's performance
    standing record: the given number of the violation's points come off and are recorded as a
    points-expiry entry dated today against that violation, the rest staying on record. On success the
    seller's active violation points shown on the standing record drop by exactly that number and the
    entry appears in the seller's standing activity with today's date, the violation reference, its type
    and the points taken off. The receipt reports the new entry reference and the active points before
    and after.

    Args:
        standing_id: Id class — the reference number identifying the seller performance standing record of the seller, read from the standing record lookup before the call.
        violation_ref: Id class — the policy violation reference number the entry is booked against, read from the seller's standing activity before the call.
        violation_type: Enum class — the kind of policy violation the entry is booked against, copied from that violation's record; exactly one of: listing_policy (the violation was recorded as a listing policy breach), restricted_product (the violation was recorded for listing a restricted product), intellectual_property (the violation was recorded on an intellectual property complaint), inauthentic_complaint (the violation was recorded for filing an inauthentic complaint), product_authenticity (the violation was recorded for an authenticity concern about the product), review_manipulation (the violation was recorded for manipulating reviews).
        points: Fixed-format class — the number of violation points that come off at the step-down, a positive whole number of points (integer points, no decimals).

    Returns:
        A dictionary receipt: entry_id (string, reference of the new points-expiry entry), standing_id
        (string, the standing record), violation_ref (string, the violation the entry is booked
        against), points (integer points taken off), active_points_before (integer active violation
        points before the entry) and active_points_after (integer active violation points after the
        entry). A returned entry_id means the entry is booked and the standing record already shows
        active_points_after.
    """
    rid = ctx.make_id("sev_", standing_id, violation_ref, violation_type, points, "serious_step_down")
    rec = (ctx.find("standing_records", standing_id=standing_id) or [{}])[0]
    before = int(rec.get("violation_points") or 0)
    after = before - int(points)
    ctx.create("standing_events", rid, standing_event_id=rid, standing_id=standing_id,
               customer_id=rec.get("customer_id"), event_type="standing_points_expiry",
               event_date=ctx.now()[:10], violation_ref=violation_ref, violation_type=violation_type,
               points=int(points))
    ctx.update("standing_records", standing_id, violation_points=after)
    return str({"entry_id": rid, "standing_id": standing_id, "violation_ref": violation_ref,
                "points": int(points), "active_points_before": before, "active_points_after": after})


@tool(owner="agent", rw="write")
def grant_top_performer_relief_7abd26c5(ctx: ToolContext, standing_id: str, violation_ref: str,
        violation_type: str, points: int) -> str:
    """Book a top-performer relief on a seller's performance standing record: Northloop takes the given
    number of violation points off the seller's active violation points as relief for a seller placed at a
    top performance level, recorded as a points-expiry entry dated today against one policy violation.
    On success the seller's active violation points shown on the standing record drop by exactly that
    number and the entry appears in the seller's standing activity with today's date, the violation
    reference, its type and the points taken off. The receipt reports the new entry reference and the
    active points before and after.

    Args:
        standing_id: Id class — the reference number identifying the seller performance standing record of the seller, read from the standing record lookup before the call.
        violation_ref: Id class — the policy violation reference number the entry is booked against, read from the seller's standing activity before the call.
        violation_type: Enum class — the kind of policy violation the entry is booked against, copied from that violation's record; exactly one of: listing_policy (the violation was recorded as a listing policy breach), restricted_product (the violation was recorded for listing a restricted product), intellectual_property (the violation was recorded on an intellectual property complaint), inauthentic_complaint (the violation was recorded for filing an inauthentic complaint), product_authenticity (the violation was recorded for an authenticity concern about the product), review_manipulation (the violation was recorded for manipulating reviews).
        points: Fixed-format class — the number of violation points taken off as relief, a positive whole number of points (integer points, no decimals).

    Returns:
        A dictionary receipt: entry_id (string, reference of the new points-expiry entry), standing_id
        (string, the standing record), violation_ref (string, the violation the entry is booked
        against), points (integer points taken off), active_points_before (integer active violation
        points before the entry) and active_points_after (integer active violation points after the
        entry). A returned entry_id means the entry is booked and the standing record already shows
        active_points_after.
    """
    rid = ctx.make_id("sev_", standing_id, violation_ref, violation_type, points, "top_performer")
    rec = (ctx.find("standing_records", standing_id=standing_id) or [{}])[0]
    before = int(rec.get("violation_points") or 0)
    after = before - int(points)
    ctx.create("standing_events", rid, standing_event_id=rid, standing_id=standing_id,
               customer_id=rec.get("customer_id"), event_type="standing_points_expiry",
               event_date=ctx.now()[:10], violation_ref=violation_ref, violation_type=violation_type,
               points=int(points))
    ctx.update("standing_records", standing_id, violation_points=after)
    return str({"entry_id": rid, "standing_id": standing_id, "violation_ref": violation_ref,
                "points": int(points), "active_points_before": before, "active_points_after": after})


@tool(owner="user", rw="write")
def close_selling_account_c808e333(ctx: ToolContext, standing_id: str, violation_ref: str,
                                   violation_type: str, retired_points: int) -> str:
    """The seller closes their own selling account on their performance standing record: the record's
    status becomes closed with today's date as the closing date, and the given number of violation
    points is retired as a points-expiry entry dated today against one policy violation. On success
    the standing record shows status closed and the closing date, its active violation points drop by
    exactly the retired points, and the retirement entry appears in the seller's standing activity;
    the points left on the record are the closed record's active points. The receipt reports the record,
    its new status, the closing date, the retirement entry and the active points before and after.

    Args:
        standing_id: Id class — the reference number identifying the seller performance standing record being closed, as given to the seller by the support agent from the standing record lookup.
        violation_ref: Id class — the policy violation reference number the retirement entry is booked against, as given to the seller by the support agent from the standing activity.
        violation_type: Enum class — the kind of policy violation the retirement entry is booked against, copied from that violation's record; exactly one of: listing_policy (the violation was recorded as a listing policy breach), restricted_product (the violation was recorded for listing a restricted product), intellectual_property (the violation was recorded on an intellectual property complaint), inauthentic_complaint (the violation was recorded for filing an inauthentic complaint), product_authenticity (the violation was recorded for an authenticity concern about the product), review_manipulation (the violation was recorded for manipulating reviews).
        retired_points: Fixed-format class — the number of violation points retired at closing, a whole number of points zero or above (integer points, no decimals), as worked out and told to the seller by the support agent.

    Returns:
        A dictionary receipt: standing_id (string, the closed standing record), status (string, closed
        once the call succeeds), closed_date (string, YYYY-MM-DD, today's date), entry_id (string,
        reference of the retirement points-expiry entry), retired_points (integer points retired),
        active_points_before (integer active violation points before closing) and active_points_after
        (integer active violation points the closed record keeps). A returned status of closed means
        the selling account is closed.
    """
    today = ctx.now()[:10]
    rid = ctx.make_id("sev_", standing_id, violation_ref, violation_type, retired_points, "closure")
    rec = (ctx.find("standing_records", standing_id=standing_id) or [{}])[0]
    before = int(rec.get("violation_points") or 0)
    after = before - int(retired_points)
    ctx.create("standing_events", rid, standing_event_id=rid, standing_id=standing_id,
               customer_id=rec.get("customer_id"), event_type="standing_points_expiry",
               event_date=today, violation_ref=violation_ref, violation_type=violation_type,
               points=int(retired_points))
    ctx.update("standing_records", standing_id, status="closed", closed_date=today,
               violation_points=after)
    return str({"standing_id": standing_id, "status": "closed", "closed_date": today,
                "entry_id": rid, "retired_points": int(retired_points),
                "active_points_before": before, "active_points_after": after})

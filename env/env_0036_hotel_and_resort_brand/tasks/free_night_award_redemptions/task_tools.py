"""Hidden task tools of the free_night_award_redemptions difficulty (Ashbury Hotels & Resorts,
Free Night Awards). Each tool performs one atomic change to one award and writes the award-history
record that goes with it; none of them judges eligibility, aggregates history or works out a value.
Every tool is reached only through unlock_* -> call_*; its name is published by the extended policy
that targets it.
"""

from erlbench import ToolContext, tool


@tool(owner="agent", rw="write")
def forfeit_late_cancel_award_5a86721d(ctx: ToolContext, certificate_id: str, reservation_id: str,
                                       award_points_price: int) -> str:
    """Record the loss of a Free Night Award that paid the first night of a reservation cancelled
    after its cancellation deadline. Guest services uses it to close one award as lost: the award's
    status becomes forfeited, its closing date is set to today, and one loss entry is added to the
    award's history naming the award, its reservation and night, the stay's protected value given
    here, the top-off points the award carried, today's date and the reason that the
    reservation was cancelled after its deadline. Afterwards the award shows as forfeited in the
    member's account and the loss appears in its history.

    Args:
        certificate_id: Id class — the reference number of the Free Night Award being recorded as lost, read from the member's award records before the call.
        reservation_id: Id class — the reference number of the cancelled reservation whose first night the award paid, read from the member's reservation records before the call.
        award_points_price: Fixed-format class — the stay's protected value the loss entry states, in integer points (a whole number of points, no decimals, never negative).

    Returns:
        A text rendering of a dictionary: activity_id (string, the reference number of the new loss
        entry), certificate_id (string, the award closed), status (string, always "forfeited" on
        success), closed_date (string, YYYY-MM-DD, the date the award was closed) and
        award_points_price (integer points recorded on the loss entry). Receiving this dictionary
        means the award is closed as lost.
    """
    rows = ctx.find("free_night_certificates", certificate_id=certificate_id)
    award = rows[0] if rows else {}
    today = ctx.now()[:10]
    ctx.update("free_night_certificates", certificate_id, status="forfeited", closed_date=today)
    rid = ctx.make_id("fna_loss_", certificate_id, reservation_id, award_points_price)
    ctx.create("certificate_activity", rid, activity_id=rid, certificate_id=certificate_id,
               customer_id=award.get("customer_id", ""), event_type="certificate_forfeit_record",
               reservation_id=reservation_id, night_date=award.get("night_date", ""),
               award_points_price=int(award_points_price), top_off_points=int(award.get("top_off_points") or 0),
               activity_date=today, activity_reason="cancelled_after_deadline")
    return str({"activity_id": rid, "certificate_id": certificate_id, "status": "forfeited",
                "closed_date": today, "award_points_price": int(award_points_price)})


@tool(owner="agent", rw="write")
def release_later_night_award_2a59ee43(ctx: ToolContext, certificate_id: str, reservation_id: str,
                                       award_points_price: int) -> str:
    """Return to the member's account a Free Night Award that paid a night after the first night of
    a reservation cancelled after its cancellation deadline. Guest services uses it to put one award
    back: the award's status becomes issued again (it keeps its reservation and night as history and
    its original expiry date), and one return entry is added to the award's history naming the
    award, its reservation and night, the protected rebooking price given here, no top-off points,
    today's date and the reason that the reservation was cancelled after its deadline. Afterwards
    the award is usable again in the member's account and the return appears in its history.

    Args:
        certificate_id: Id class — the reference number of the Free Night Award being returned, read from the member's award records before the call.
        reservation_id: Id class — the reference number of the cancelled reservation the award comes back from, read from the member's reservation records before the call.
        award_points_price: Fixed-format class — the protected rebooking price the return entry states, in integer points (a whole number of points, no decimals, never negative).

    Returns:
        A text rendering of a dictionary: activity_id (string, the reference number of the new return
        entry), certificate_id (string, the award returned), status (string, always "issued" on
        success), activity_date (string, YYYY-MM-DD, the date of the return) and award_points_price
        (integer points recorded on the return entry). Receiving this dictionary means the award is
        back in the member's account.
    """
    rows = ctx.find("free_night_certificates", certificate_id=certificate_id)
    award = rows[0] if rows else {}
    today = ctx.now()[:10]
    ctx.update("free_night_certificates", certificate_id, status="issued")
    rid = ctx.make_id("fna_ret_", certificate_id, reservation_id, award_points_price)
    ctx.create("certificate_activity", rid, activity_id=rid, certificate_id=certificate_id,
               customer_id=award.get("customer_id", ""), event_type="certificate_release_record",
               reservation_id=reservation_id, night_date=award.get("night_date", ""),
               award_points_price=int(award_points_price), top_off_points=0,
               activity_date=today, activity_reason="cancelled_after_deadline")
    return str({"activity_id": rid, "certificate_id": certificate_id, "status": "issued",
                "activity_date": today, "award_points_price": int(award_points_price)})


@tool(owner="user", rw="write")
def apply_returned_award_7b7c21ba(ctx: ToolContext, certificate_id: str, loyalty_member_id: str,
                                   reservation_id: str, night_date: str, award_points_price: int) -> str:
    """Apply, as the member's own choice, a Free Night Award that came back from a cancelled stay to
    one night of another Reward Night Rate reservation. The member uses it to spend their award: the
    award's status becomes applied, it is attached to the reservation and night given, it carries no
    top-off points, and one hold entry is added to the award's history naming the reservation, the
    night, the rebooked night's price given here, no top-off points, today's date and the reason that
    the award was applied to a reservation. Afterwards the night shows as paid by the award.

    Args:
        certificate_id: Id class — the reference number of the Free Night Award the member spends, read from the member's award records before the call.
        loyalty_member_id: Id class — the reference number of the Ashbury Rewards membership that holds the award, read from the member's membership records before the call.
        reservation_id: Id class — the reference number of the Reward Night Rate reservation the award pays, read from the member's reservation records before the call.
        night_date: Fixed-format class — the stay night the award pays, written YYYY-MM-DD (hotel local calendar date of the night's check-in).
        award_points_price: Fixed-format class — the rebooked night's price recorded on the hold, in integer points (a whole number of points, no decimals, never negative).

    Returns:
        A text rendering of a dictionary: activity_id (string, the reference number of the new hold
        entry), certificate_id (string, the award applied), reservation_id (string, the reservation it
        pays), night_date (string, YYYY-MM-DD), status (string, always "applied" on success) and
        award_points_price (integer points recorded on the hold). Receiving this dictionary means the
        award is now held for that night.
    """
    rows = ctx.find("free_night_certificates", certificate_id=certificate_id)
    award = rows[0] if rows else {}
    today = ctx.now()[:10]
    ctx.update("free_night_certificates", certificate_id, status="applied", reservation_id=reservation_id,
               night_date=night_date, top_off_points=0)
    rid = ctx.make_id("fna_hold_", certificate_id, loyalty_member_id, reservation_id, night_date, award_points_price)
    ctx.create("certificate_activity", rid, activity_id=rid, certificate_id=certificate_id,
               customer_id=award.get("customer_id", ""), event_type="certificate_hold_record",
               reservation_id=reservation_id, night_date=night_date,
               award_points_price=int(award_points_price), top_off_points=0,
               activity_date=today, activity_reason="applied_to_reservation")
    return str({"activity_id": rid, "certificate_id": certificate_id, "reservation_id": reservation_id,
                "night_date": night_date, "status": "applied", "award_points_price": int(award_points_price)})


@tool(owner="agent", rw="write")
def release_relocated_award_8143384d(ctx: ToolContext, certificate_id: str, reservation_id: str,
                                     award_points_price: int) -> str:
    """Return to the member's account a Free Night Award that was on a reservation the hotel
    relocated (walked). Guest services uses it to put one award back: the award's status becomes
    issued again (it keeps its reservation and night as history and its original expiry date), and
    one return entry is added to the award's history naming the award, the relocated reservation and
    night, the walked-night protected price given here, no top-off points, today's date and the
    reason that the reservation was relocated. Afterwards the award stands returned in the member's
    account, keeping its original expiry date, and the return appears in its history.

    Args:
        certificate_id: Id class — the reference number of the Free Night Award being returned, read from the member's award records before the call.
        reservation_id: Id class — the reference number of the relocated reservation the award comes back from, read from the member's reservation records before the call.
        award_points_price: Fixed-format class — the walked-night protected price the return entry states, in integer points (a whole number of points, no decimals, never negative).

    Returns:
        A text rendering of a dictionary: activity_id (string, the reference number of the new return
        entry), certificate_id (string, the award returned), status (string, always "issued" on
        success), activity_date (string, YYYY-MM-DD, the date of the return) and award_points_price
        (integer points recorded on the return entry). Receiving this dictionary means the award is
        back in the member's account.
    """
    rows = ctx.find("free_night_certificates", certificate_id=certificate_id)
    award = rows[0] if rows else {}
    today = ctx.now()[:10]
    ctx.update("free_night_certificates", certificate_id, status="issued")
    rid = ctx.make_id("fna_wret_", certificate_id, reservation_id, award_points_price)
    ctx.create("certificate_activity", rid, activity_id=rid, certificate_id=certificate_id,
               customer_id=award.get("customer_id", ""), event_type="certificate_release_record",
               reservation_id=reservation_id, night_date=award.get("night_date", ""),
               award_points_price=int(award_points_price), top_off_points=0,
               activity_date=today, activity_reason="reservation_relocated")
    return str({"activity_id": rid, "certificate_id": certificate_id, "status": "issued",
                "activity_date": today, "award_points_price": int(award_points_price)})


@tool(owner="agent", rw="write")
def reissue_replacement_award_0d99e6ce(ctx: ToolContext, replaced_certificate_id: str, loyalty_member_id: str,
                                       issue_source: str, variant_name: str, expiry_date: str) -> str:
    """Deposit a new Free Night Award into a member's Ashbury Rewards account to replace an earlier
    award. Guest services uses it to issue one award: a new award is created in the membership given,
    of the type given, with status issued, today's date as its issue date, the expiry date given, no
    top-off points, the reason given and a link to the award it replaces; it receives a new award
    number. Afterwards the new award appears in the member's account as usable.

    Args:
        replaced_certificate_id: Id class — the reference number of the earlier award this new award replaces, read from the member's award records before the call.
        loyalty_member_id: Id class — the reference number of the Ashbury Rewards membership the new award is deposited into, read from the member's membership records before the call.
        issue_source: Enum class — why the new award is issued: cobrand_anniversary when it is deposited for a co-brand card account anniversary; elite_milestone when it is deposited because the year's elite night credits reached a milestone; promotion when it is deposited for a completed registered promotion; reissue_replacement when it replaces an earlier award.
        variant_name: Enum class — the award type of the new award, written as the official award name: 25K Free Night Award for an award covering a night priced up to 25,000 points; 35K Free Night Award for one covering up to 35,000 points; 40K Free Night Award for one covering up to 40,000 points; 50K Free Night Award for one covering up to 50,000 points; 85K Free Night Award for one covering up to 85,000 points; Any Hotel Free Night Award for an uncapped award usable at any eligible hotel.
        expiry_date: Fixed-format class — the last date on which a stay night covered by the new award may fall, written YYYY-MM-DD (calendar date, no time).

    Returns:
        A text rendering of a dictionary: certificate_id (string, the reference number of the new
        award), certificate_number (string, the new award number, FNA followed by 8 digits),
        variant_name (string, the award type), issued_date (string, YYYY-MM-DD), expiry_date (string,
        YYYY-MM-DD) and status (string, always "issued" on success). Receiving this dictionary means
        the new award is in the member's account.
    """
    rows = ctx.find("free_night_certificates", certificate_id=replaced_certificate_id)
    old = rows[0] if rows else {}
    today = ctx.now()[:10]
    cid = ctx.make_id("fna_", replaced_certificate_id, loyalty_member_id, issue_source, variant_name, expiry_date)
    number = "FNA64" + "%06d" % (int(cid[-8:], 16) % 1000000)
    ctx.create("free_night_certificates", cid, certificate_id=cid, customer_id=old.get("customer_id", ""),
               loyalty_member_id=loyalty_member_id, variant_name=variant_name, status="issued",
               certificate_number=number, issue_source=issue_source, issued_date=today, expiry_date=expiry_date,
               top_off_points=0, replaced_certificate_id=replaced_certificate_id)
    return str({"certificate_id": cid, "certificate_number": number, "variant_name": variant_name,
                "issued_date": today, "expiry_date": expiry_date, "status": "issued"})


@tool(owner="user", rw="write")
def apply_replacement_award_003026b1(ctx: ToolContext, certificate_id: str, loyalty_member_id: str,
                                     reservation_id: str, night_date: str, award_points_price: int) -> str:
    """Apply, as the member's own choice, a replacement Free Night Award to one night of a Reward
    Night Rate reservation. The member uses it to spend the replacement: the award's status becomes
    applied, it is attached to the reservation and night given, it carries no top-off points, and one
    hold entry is added to the award's history naming the reservation, the night, the replacement's
    night price given here, no top-off points, today's date and the reason that the award was applied
    to a reservation. Afterwards the night shows as paid by the replacement award.

    Args:
        certificate_id: Id class — the reference number of the replacement award the member spends, read from the member's award records before the call.
        loyalty_member_id: Id class — the reference number of the Ashbury Rewards membership that holds the award, read from the member's membership records before the call.
        reservation_id: Id class — the reference number of the Reward Night Rate reservation the award pays, read from the member's reservation records before the call.
        night_date: Fixed-format class — the stay night the award pays, written YYYY-MM-DD (hotel local calendar date of the night's check-in).
        award_points_price: Fixed-format class — the replacement's night price recorded on the hold, in integer points (a whole number of points, no decimals, never negative).

    Returns:
        A text rendering of a dictionary: activity_id (string, the reference number of the new hold
        entry), certificate_id (string, the award applied), reservation_id (string, the reservation it
        pays), night_date (string, YYYY-MM-DD), status (string, always "applied" on success) and
        award_points_price (integer points recorded on the hold). Receiving this dictionary means the
        replacement is now held for that night.
    """
    rows = ctx.find("free_night_certificates", certificate_id=certificate_id)
    award = rows[0] if rows else {}
    today = ctx.now()[:10]
    ctx.update("free_night_certificates", certificate_id, status="applied", reservation_id=reservation_id,
               night_date=night_date, top_off_points=0)
    rid = ctx.make_id("fna_rhold_", certificate_id, loyalty_member_id, reservation_id, night_date, award_points_price)
    ctx.create("certificate_activity", rid, activity_id=rid, certificate_id=certificate_id,
               customer_id=award.get("customer_id", ""), event_type="certificate_hold_record",
               reservation_id=reservation_id, night_date=night_date,
               award_points_price=int(award_points_price), top_off_points=0,
               activity_date=today, activity_reason="applied_to_reservation")
    return str({"activity_id": rid, "certificate_id": certificate_id, "reservation_id": reservation_id,
                "night_date": night_date, "status": "applied", "award_points_price": int(award_points_price)})

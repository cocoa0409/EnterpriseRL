"""Hidden task tools of the finch_circle_rewards difficulty (Finch Circle loyalty program).

Each tool performs one atomic change on a Finch Circle membership and its ledgers with the values
passed in; none of them checks eligibility, timing or prerequisites, and none of them works out an
amount for the caller.
"""

from erlbench import ToolContext, tool


@tool(owner="user", rw="write")
def file_missing_points_claim_8cff3bd6(ctx: ToolContext, membership_id: str, purchase_id: str,
                                       qualifying_amount: float, points: int) -> str:
    """The member files, in person, a Finch Circle missing-points claim for one purchase record of theirs on which no member number was captured at checkout, and the claim is credited at once. The member's request is recorded as a completed missing-points request naming that purchase record, one missing-points credit entry carrying the given points and qualifying amount is posted to the membership's points history, and the membership's points balance rises by the given points. The member sees the credit in the points history and the higher balance immediately; the receipt below confirms it.

    Args:
        membership_id: Id class — the reference number of the member's Finch Circle membership, as returned by the membership lookup.
        purchase_id: Id class — the reference number of the purchase record (one unit of one item) being claimed, as returned by the purchase lookup.
        qualifying_amount: Fixed-format class — the net qualifying dollars of the claimed unit on which the credit is figured, in USD, 2 decimal places, stored rounded half up to the cent.
        points: Fixed-format class — the points credited for the claimed unit, as positive integer points (a whole number with no decimal part).

    Returns:
        A dictionary rendered as text with: status ("credited" when the claim was recorded and the points posted); request_id (reference number of the completed missing-points request); entry_id (reference number of the missing-points credit entry); purchase_id (the purchase record credited); points (integer points credited); qualifying_amount (USD, 2 decimal places); points_balance (the membership's new points balance, integer points).
    """
    amount = round(float(qualifying_amount), 2)
    pts = int(points)
    member = ctx.find("loyalty_memberships", membership_id=membership_id)
    customer_id = member[0].get("customer_id") if member else None
    old_balance = int(member[0].get("points_balance") or 0) if member else 0
    new_balance = old_balance + pts
    stamp = ctx.now()
    req_id = ctx.make_id("lrq_", membership_id, purchase_id, amount, pts)
    ctx.create("loyalty_requests", req_id, loyalty_request_id=req_id, customer_id=customer_id,
               membership_id=membership_id, request_type="missing_points", purchase_id=purchase_id,
               note_code=None, request_status="completed", created_at=stamp)
    entry_id = ctx.make_id("lpe_", membership_id, purchase_id, amount, pts)
    ctx.create("loyalty_points_ledger", entry_id, loyalty_entry_id=entry_id, membership_id=membership_id,
               customer_id=customer_id, event_type="loyalty_points_adjustment", entry_date=stamp[:10],
               points=pts, earn_source="missing_points_credit", purchase_id=purchase_id, card_txn_id=None,
               return_id=None, qualifying_amount=amount, original_loyalty_entry_id=None, note_code=None,
               expiry_reason="not_applicable")
    ctx.update("loyalty_memberships", membership_id, points_balance=new_balance)
    return str({"status": "credited", "request_id": req_id, "entry_id": entry_id, "purchase_id": purchase_id,
                "points": pts, "qualifying_amount": amount, "points_balance": new_balance})


@tool(owner="agent", rw="write")
def apply_card_status_floor_f82dd75f(ctx: ToolContext, membership_id: str, status: str, new_tier: str,
                                     top_up_amount: float) -> str:
    """Customer care moves a Finch Circle membership to the tier granted by the member's Marlowe & Finch card status (a card floor) and posts the alteration credit top-up that goes with the change. The membership's tier becomes the given tier, its latest tier change is recorded as a card floor dated today, its status stays as given, one alteration credit grant marked as a tier top-up for the current benefit year is posted with the given amount, and the alteration credit balance rises by that amount. No points bonus is posted. The member sees the new tier and the higher alteration credit at once; the receipt below confirms the change.

    Args:
        membership_id: Id class — the reference number of the Finch Circle membership being changed, as returned by the membership lookup.
        status: Enum class — the membership status as the membership record shows it, which the membership keeps: active when the membership is open for earning and redemption; suspended when the membership is frozen for a program review; closed when the membership has been cancelled or terminated.
        new_tier: Enum class — the official name of the tier the membership moves to: Finch Circle Member for the entry tier; Finch Circle Silver for the second tier; Finch Circle Gold for the third tier; Finch Circle Platinum for the fourth tier; Finch Circle Diamond for the fifth tier; Finch Circle Icon for the top tier.
        top_up_amount: Fixed-format class — the alteration credit added for the current benefit year, in USD, 2 decimal places, positive, rounded half up to the cent; 0.00 when no credit is added.

    Returns:
        A dictionary rendered as text with: status ("applied" when the tier change and the top-up were recorded); membership_id (the membership changed); new_tier (official tier name now held); last_tier_change_type (always card_floor); last_tier_change_date (date of the change, YYYY-MM-DD); grant_id (reference number of the alteration credit grant entry); top_up_amount (USD, 2 decimal places); alteration_credit_balance (the new alteration credit balance, USD, 2 decimal places).
    """
    amount = round(float(top_up_amount), 2)
    member = ctx.find("loyalty_memberships", membership_id=membership_id)
    customer_id = member[0].get("customer_id") if member else None
    old_credit = float(member[0].get("alteration_credit_balance") or 0) if member else 0.0
    new_credit = round(old_credit + amount, 2)
    today = ctx.now()[:10]
    ctx.update("loyalty_memberships", membership_id, variant_name=new_tier, status=status,
               last_tier_change_date=today, last_tier_change_type="card_floor",
               alteration_credit_balance=new_credit)
    grant_id = ctx.make_id("lbg_", membership_id, status, new_tier, amount)
    ctx.create("loyalty_benefit_ledger", grant_id, benefit_txn_id=grant_id, membership_id=membership_id,
               customer_id=customer_id, event_type="loyalty_alteration_credit_grant", benefit_year=today[:4],
               amount=amount, txn_date=today, ticket_id=None, grant_reason="tier_upgrade_top_up")
    return str({"status": "applied", "membership_id": membership_id, "new_tier": new_tier,
                "last_tier_change_type": "card_floor", "last_tier_change_date": today, "grant_id": grant_id,
                "top_up_amount": amount, "alteration_credit_balance": new_credit})


class _NoteDates:
    """Pure calendar arithmetic for note expiry dates (no clock, no library calendar)."""

    @staticmethod
    def to_ordinal(day: str) -> int:
        y, m, d = (int(p) for p in str(day)[:10].split("-"))
        if m <= 2:
            y -= 1
            m += 12
        return 365 * y + y // 4 - y // 100 + y // 400 + (153 * (m - 3) + 2) // 5 + d

    @staticmethod
    def from_ordinal(n: int) -> str:
        y = (n * 400) // 146097
        while _NoteDates.to_ordinal(f"{y + 1:04d}-01-01") <= n:
            y += 1
        while _NoteDates.to_ordinal(f"{y:04d}-01-01") > n:
            y -= 1
        m = 1
        while m < 12 and _NoteDates.to_ordinal(f"{y:04d}-{m + 1:02d}-01") <= n:
            m += 1
        d = n - _NoteDates.to_ordinal(f"{y:04d}-{m:02d}-01") + 1
        return f"{y:04d}-{m:02d}-{d:02d}"

    @staticmethod
    def last_day(start: str, days: int) -> str:
        return _NoteDates.from_ordinal(_NoteDates.to_ordinal(start) + int(days) - 1)


@tool(owner="agent", rw="write")
def book_return_points_deduction_52e06983(ctx: ToolContext, membership_id: str, return_id: str, purchase_id: str,
                                          original_loyalty_entry_id: str, qualifying_amount: float, points: int) -> str:
    """Customer care books the Finch Circle points taken back for one refunded return of merchandise. One return deduction entry naming the return, the returned purchase record and the purchase points entry it is booked against is posted to the membership's points history with the given points and refunded qualifying amount, and the membership's points balance falls by the given points (it may fall below zero). The member sees the deduction in the points history and the new balance at once; the receipt below confirms it.

    Args:
        membership_id: Id class — the reference number of the Finch Circle membership, as returned by the membership lookup.
        return_id: Id class — the reference number of the refunded return record, as returned by the return lookup.
        purchase_id: Id class — the reference number of the returned purchase record (one unit), as returned by the purchase lookup.
        original_loyalty_entry_id: Id class — the reference number of the returned unit's purchase points entry (or its missing-points credit entry) the deduction is booked against, as returned by the points history lookup.
        qualifying_amount: Fixed-format class — the refunded qualifying dollars the deduction is figured on, in USD, 2 decimal places, stored rounded half up to the cent.
        points: Fixed-format class — the points taken back, as positive integer points (a whole number with no decimal part).

    Returns:
        A dictionary rendered as text with: status ("booked" when the deduction was posted); entry_id (reference number of the return deduction entry); return_id (the return deducted for); points (integer points taken back); qualifying_amount (USD, 2 decimal places); points_balance (the membership's new points balance, integer points, may be negative).
    """
    amount = round(float(qualifying_amount), 2)
    pts = int(points)
    member = ctx.find("loyalty_memberships", membership_id=membership_id)
    customer_id = member[0].get("customer_id") if member else None
    new_balance = (int(member[0].get("points_balance") or 0) if member else 0) - pts
    entry_id = ctx.make_id("lpr_", membership_id, return_id, purchase_id, original_loyalty_entry_id, amount, pts)
    ctx.create("loyalty_points_ledger", entry_id, loyalty_entry_id=entry_id, membership_id=membership_id,
               customer_id=customer_id, event_type="loyalty_points_reversal", entry_date=ctx.now()[:10], points=pts,
               earn_source="not_applicable", purchase_id=purchase_id, card_txn_id=None, return_id=return_id,
               qualifying_amount=amount, original_loyalty_entry_id=original_loyalty_entry_id, note_code=None,
               expiry_reason="not_applicable")
    ctx.update("loyalty_memberships", membership_id, points_balance=new_balance)
    return str({"status": "booked", "entry_id": entry_id, "return_id": return_id, "points": pts,
                "qualifying_amount": amount, "points_balance": new_balance})


@tool(owner="agent", rw="write")
def reinstate_returned_note_1c0adac4(ctx: ToolContext, membership_id: str, return_id: str, original_note_code: str,
                                     note_amount: float, expiry_date: str) -> str:
    """Customer care issues a new Finch Note that reinstates note value spent on merchandise the member returned and was refunded for. One new note with its own code, marked as a return reinstatement and naming the return and the original note, is issued today with the given value and last valid day, and the membership's Finch Notes balance rises by that value. The member sees the new note in the app at once; the receipt below confirms it.

    Args:
        membership_id: Id class — the reference number of the Finch Circle membership, as returned by the membership lookup.
        return_id: Id class — the reference number of the refunded return record the note value is reinstated for, as returned by the return lookup.
        original_note_code: Verbatim class — the code of the Finch Note that was spent on the returned merchandise, exactly as it appears in the member's note history, copied character for character with no change (verbatim).
        note_amount: Fixed-format class — the value of the new note, in USD, 2 decimal places, positive, rounded half up to the cent.
        expiry_date: Fixed-format class — the last day the new note can be redeemed, as a calendar date in YYYY-MM-DD format.

    Returns:
        A dictionary rendered as text with: status ("issued" when the note was created); note_code (code of the new note, FN- followed by 8 characters); note_amount (USD, 2 decimal places); issue_date (YYYY-MM-DD); expiry_date (YYYY-MM-DD); notes_balance (the membership's new Finch Notes balance, USD, 2 decimal places).
    """
    amount = round(float(note_amount), 2)
    member = ctx.find("loyalty_memberships", membership_id=membership_id)
    customer_id = member[0].get("customer_id") if member else None
    new_notes = round((float(member[0].get("notes_balance") or 0) if member else 0.0) + amount, 2)
    today = ctx.now()[:10]
    code = ctx.make_id("FN-", membership_id, return_id, original_note_code, amount, expiry_date, length=8).upper()
    txn_id = ctx.make_id("lni_", membership_id, return_id, original_note_code, amount, expiry_date)
    ctx.create("loyalty_note_ledger", txn_id, note_txn_id=txn_id, membership_id=membership_id, customer_id=customer_id,
               event_type="loyalty_note_issue", note_code=code, note_amount=amount, issue_reason="return_reinstatement",
               issue_date=today, expiry_date=str(expiry_date)[:10], txn_date=None, purchase_id=None, return_id=return_id,
               original_note_code=original_note_code, expire_reason="not_applicable")
    ctx.update("loyalty_memberships", membership_id, notes_balance=new_notes)
    return str({"status": "issued", "note_code": code, "note_amount": amount, "issue_date": today,
                "expiry_date": str(expiry_date)[:10], "notes_balance": new_notes})


@tool(owner="user", rw="write")
def request_courtesy_note_reissue_8b12a7a8(ctx: ToolContext, membership_id: str, original_note_code: str, return_id: str,
                                           note_amount: float, validity_days: int) -> str:
    """The member submits, in person, a courtesy reissue request for a Finch Note of theirs that lapsed unused, and the courtesy note is issued at once. The request is recorded as a completed expired note reissue request naming the lapsed note, one new note with its own code, marked as a courtesy reissue and naming the lapsed note, is issued today with the given value and stays valid for the given number of days counting today as day 1, and the membership's Finch Notes balance rises by that value. The member sees the new note in the app at once; the receipt below confirms it.

    Args:
        membership_id: Id class — the reference number of the member's Finch Circle membership, as returned by the membership lookup.
        original_note_code: Verbatim class — the code of the lapsed Finch Note being reissued, exactly as it appears in the member's note history, copied character for character with no change (verbatim).
        return_id: Id class — the reference number of a return record the note is tied to, as returned by the return lookup; a courtesy reissue is tied to no return, so the empty value is passed.
        note_amount: Fixed-format class — the value of the reissued note, in USD, 2 decimal places, positive, rounded half up to the cent.
        validity_days: Fixed-format class — how many calendar days the reissued note stays valid, counting the reissue date as day 1, as an integer number of days.

    Returns:
        A dictionary rendered as text with: status ("reissued" when the request was recorded and the note created); request_id (reference number of the completed reissue request); note_code (code of the new note, FN- followed by 8 characters); note_amount (USD, 2 decimal places); issue_date (YYYY-MM-DD); expiry_date (last valid day, YYYY-MM-DD); notes_balance (the membership's new Finch Notes balance, USD, 2 decimal places).
    """
    amount = round(float(note_amount), 2)
    days = int(validity_days)
    member = ctx.find("loyalty_memberships", membership_id=membership_id)
    customer_id = member[0].get("customer_id") if member else None
    new_notes = round((float(member[0].get("notes_balance") or 0) if member else 0.0) + amount, 2)
    stamp = ctx.now()
    today = stamp[:10]
    last_day = _NoteDates.last_day(today, days)
    req_id = ctx.make_id("lrq_", membership_id, original_note_code, return_id, amount, days)
    ctx.create("loyalty_requests", req_id, loyalty_request_id=req_id, customer_id=customer_id, membership_id=membership_id,
               request_type="expired_note_reissue", purchase_id=None, note_code=original_note_code,
               request_status="completed", created_at=stamp)
    code = ctx.make_id("FN-", membership_id, original_note_code, return_id, amount, days, length=8).upper()
    txn_id = ctx.make_id("lni_", membership_id, original_note_code, return_id, amount, days)
    ctx.create("loyalty_note_ledger", txn_id, note_txn_id=txn_id, membership_id=membership_id, customer_id=customer_id,
               event_type="loyalty_note_issue", note_code=code, note_amount=amount, issue_reason="courtesy_reissue",
               issue_date=today, expiry_date=last_day, txn_date=None, purchase_id=None, return_id=return_id or None,
               original_note_code=original_note_code, expire_reason="not_applicable")
    ctx.update("loyalty_memberships", membership_id, notes_balance=new_notes)
    return str({"status": "reissued", "request_id": req_id, "note_code": code, "note_amount": amount,
                "issue_date": today, "expiry_date": last_day, "notes_balance": new_notes})

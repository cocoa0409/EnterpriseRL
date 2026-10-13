"""Hidden task tools for grooming_appointment_care (Tailwise Grooming Salon passes and Groom Club Monthly).

Each tool performs exactly one atomic salon-ledger change with the values the caller has already
worked out; none of them checks eligibility, prerequisites or amounts.
"""

from erlbench import ToolContext, tool


@tool(owner="agent", rw="write")
def charge_late_cancel_fee_38a40f67(ctx: ToolContext, groom_pass_id: str, original_event_id: str,
                                    amount_usd: float) -> str:
    """Book a late-cancellation fee against a prepaid grooming pass (an Express Bath, Bath & Tidy,
    Full Groom or Spa Groom pass) for one booking that the customer cancelled late. One call adds
    one late-cancellation fee entry to the salon history of that pass, dated today, tied to the
    cancelled booking and carrying the fee amount given here; the pass status, its visits and
    every other entry stay as they are. The new entry is visible at once in the pass history.

    Args:
        groom_pass_id: Id class — the reference number of the prepaid grooming pass the fee is
            booked against, as returned by the grooming pass lookup.
        original_event_id: Id class — the reference number of the booking that was cancelled late
            (the booking entry itself, not the cancellation entry), as returned by the salon
            history lookup of the pass.
        amount_usd: Fixed-format class — the late-cancellation fee to book, in USD, given to 2
            decimal places; the tool keeps exactly 2 decimal places (rounded half to even only if
            more digits are passed).

    Returns:
        A confirmation sentence naming the new fee entry reference number (text starting with
        "lcf_"), the pass reference number, the booking reference number and the booked fee in
        USD with 2 decimal places; receiving it means the fee entry now stands on the pass.
    """
    booking = (ctx.find("groom_events", groom_event_id=original_event_id) or [{}])[0]
    pas = (ctx.find("groom_passes", groom_pass_id=groom_pass_id) or [{}])[0]
    amount = round(float(amount_usd), 2)
    rid = ctx.make_id("lcf_", groom_pass_id, original_event_id, amount)
    ctx.create("groom_events", rid, groom_event_id=rid, groom_pass_id=groom_pass_id,
               customer_id=pas.get("customer_id"), event_type="groom_late_cancel_fee",
               event_date=ctx.now()[:10], pet_id=booking.get("pet_id"), store_id=booking.get("store_id"),
               appointment_date=booking.get("appointment_date"), original_event_id=original_event_id,
               amount_usd=amount)
    return (f"Late-cancellation fee {rid} booked on pass {groom_pass_id} for booking "
            f"{original_event_id}: {amount:.2f} USD.")


@tool(owner="user", rw="write")
def cancel_groom_pass_241c8b1d(ctx: ToolContext, groom_pass_id: str, refund_usd: float) -> str:
    """Cancel your own prepaid grooming pass (an Express Bath, Bath & Tidy, Full Groom or Spa Groom
    pass) and take the refund for it. One call closes the pass for good as of today (its status
    becomes cancelled), removes every visit still left on it, and records one refund entry in the
    pass history for the refund amount given here, sent back to the original payment. On success
    the pass shows as cancelled with no visits left and the refund entry shows the amount returned.

    Args:
        groom_pass_id: Id class — the reference number of the grooming pass being cancelled, as
            read out by the care agent from the grooming pass lookup.
        refund_usd: Fixed-format class — the refund for the cancelled pass, in USD, given to 2
            decimal places as the care agent states it; 0.00 when nothing is refunded; the tool
            keeps exactly 2 decimal places.

    Returns:
        A confirmation sentence naming the refund entry reference number (text starting with
        "prf_"), the cancelled pass reference number, the number of visits removed, and the
        refund in USD with 2 decimal places sent to the original payment; receiving it means the
        pass is cancelled and the refund is recorded.
    """
    pas = (ctx.find("groom_passes", groom_pass_id=groom_pass_id) or [{}])[0]
    removed = int(pas.get("visits_remaining") or 0)
    refund = round(float(refund_usd), 2)
    today = ctx.now()[:10]
    rid = ctx.make_id("prf_", groom_pass_id, refund)
    ctx.update("groom_passes", groom_pass_id, status="cancelled", closed_on=today, visits_remaining=0)
    ctx.create("groom_events", rid, groom_event_id=rid, groom_pass_id=groom_pass_id,
               customer_id=pas.get("customer_id"), event_type="groom_pass_refund", event_date=today,
               pet_id=pas.get("pet_id"), store_id=pas.get("store_id"), visits_delta=removed,
               visits_remaining_after=0, amount_usd=refund, refund_method="original_payment")
    return (f"Pass {groom_pass_id} cancelled; refund entry {rid}: {removed} visit(s) removed, "
            f"{refund:.2f} USD refunded to the original payment.")


@tool(owner="agent", rw="write")
def charge_club_late_cancel_73de6594(ctx: ToolContext, groom_pass_id: str, original_event_id: str,
                                     amount_usd: float) -> str:
    """Book a club late-cancellation charge against a Groom Club Monthly membership for one booking
    that the member cancelled late. One call adds one late-cancellation charge entry to the salon
    history of that club, dated today, tied to the cancelled booking and carrying the charge
    amount given here; the club status, its billing date, its visits and every other entry stay as
    they are. The new entry is visible at once in the club history.

    Args:
        groom_pass_id: Id class — the reference number of the Groom Club Monthly membership the
            charge is booked against, as returned by the grooming pass lookup.
        original_event_id: Id class — the reference number of the booking that was cancelled late
            (the booking entry itself, not the cancellation entry), as returned by the salon
            history lookup of the club.
        amount_usd: Fixed-format class — the club late-cancellation charge to book, in USD, given
            to 2 decimal places; the tool keeps exactly 2 decimal places (rounded half to even
            only if more digits are passed).

    Returns:
        A confirmation sentence naming the new charge entry reference number (text starting with
        "clc_"), the club reference number, the booking reference number and the booked charge in
        USD with 2 decimal places; receiving it means the charge entry now stands on the club.
    """
    booking = (ctx.find("groom_events", groom_event_id=original_event_id) or [{}])[0]
    club = (ctx.find("groom_passes", groom_pass_id=groom_pass_id) or [{}])[0]
    amount = round(float(amount_usd), 2)
    rid = ctx.make_id("clc_", groom_pass_id, original_event_id, amount)
    ctx.create("groom_events", rid, groom_event_id=rid, groom_pass_id=groom_pass_id,
               customer_id=club.get("customer_id"), event_type="groom_late_cancel_fee",
               event_date=ctx.now()[:10], pet_id=booking.get("pet_id"), store_id=booking.get("store_id"),
               appointment_date=booking.get("appointment_date"), original_event_id=original_event_id,
               amount_usd=amount)
    return (f"Club late-cancellation charge {rid} booked on club {groom_pass_id} for booking "
            f"{original_event_id}: {amount:.2f} USD.")


@tool(owner="user", rw="write")
def cancel_groom_club_74a11dc2(ctx: ToolContext, groom_pass_id: str, settlement_usd: float) -> str:
    """Cancel your own Groom Club Monthly membership and settle it. One call cancels the club (its
    status becomes cancelled, no further monthly fee is billed, and the cancellation takes effect
    on the last day of the current billing month, which is recorded as its closing date), and
    records one settlement entry in the club history for the settlement amount given here, which
    is collected from the card on file. On success the club shows as cancelled with its closing
    date and the settlement entry shows the amount collected.

    Args:
        groom_pass_id: Id class — the reference number of the Groom Club Monthly membership being
            cancelled, as read out by the care agent from the grooming pass lookup.
        settlement_usd: Fixed-format class — the club cancellation settlement, in USD, given to 2
            decimal places as the care agent states it; 0.00 when nothing is owed; the tool keeps
            exactly 2 decimal places.

    Returns:
        A confirmation sentence naming the settlement entry reference number (text starting with
        "cst_"), the cancelled club reference number, the closing date as YYYY-MM-DD and the
        settlement in USD with 2 decimal places collected from the card on file; receiving it
        means the club is cancelled and the settlement is recorded.
    """
    club = (ctx.find("groom_passes", groom_pass_id=groom_pass_id) or [{}])[0]
    removed = int(club.get("visits_remaining") or 0)
    settlement = round(float(settlement_usd), 2)
    closing = club.get("expires_on") or ctx.now()[:10]
    rid = ctx.make_id("cst_", groom_pass_id, settlement)
    ctx.update("groom_passes", groom_pass_id, status="cancelled", closed_on=closing,
               next_billing_date=None, visits_remaining=0)
    ctx.create("groom_events", rid, groom_event_id=rid, groom_pass_id=groom_pass_id,
               customer_id=club.get("customer_id"), event_type="groom_pass_refund",
               event_date=ctx.now()[:10], pet_id=club.get("pet_id"), store_id=club.get("store_id"),
               visits_delta=removed, visits_remaining_after=0, amount_usd=settlement,
               refund_method="none")
    return (f"Club {groom_pass_id} cancelled effective {closing}; settlement entry {rid}: "
            f"{settlement:.2f} USD collected from the card on file.")

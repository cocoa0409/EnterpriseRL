"""Hidden task tools for the Wanderlane hotel reservations desk (difficulty: hotel_reservations_desk).

Every tool here is discovered only through an extended policy's target_tool and is reached through
the unlock/call meta tools. Each one performs a single atomic business write with the values the
agent has already worked out from the published terms, the folio and the traveller's wider
portfolio; none of them aggregates history, prices anything or judges whether a write is due.
"""

from erlbench import ToolContext, tool


@tool(owner="user", rw="write")
def confirm_reservation_cancellation_70c0f3f0(ctx: ToolContext, stay_reservation_id: str,
                                              penalty_amount_usd: float) -> str:
    """Let the guest give up every room still standing on one of their own hotel reservations and
    have the agreed amount withheld from what they have already paid. One call releases the rooms
    with the property and closes the booking: the reservation record moves to cancelled and is
    stamped with the moment the guest confirmed, and a cancellation penalty line for the amount
    stated is posted to that reservation's folio as money the guest does not get back. Afterwards
    the guest sees the booking shown as cancelled and the withheld amount standing on the folio as
    a penalty line. The call has completed when the confirmation text below comes back naming the
    new penalty line and the amount withheld.

    Args:
        stay_reservation_id: Id class — the internal reference number of the hotel reservation the
            guest is giving up, read from the reservation record returned by the reservation
            lookup before this call.
        penalty_amount_usd: Fixed-format class — the amount withheld from the guest, as a positive
            USD amount with 2 decimal places, rounded half to even at the second decimal and at no
            earlier point, with no thousands separator and no currency symbol; zero is written 0.0
            and means nothing is withheld.

    Returns:
        A single line of confirmation text. It names the reference of the cancellation penalty line
        just created on the folio (a string beginning stpen_), the reference of the reservation now
        standing at cancelled (a string), and the amount withheld (a USD figure with two decimal
        places). The text coming back at all is what indicates the release completed; an absent
        line or an error text means the booking is untouched.
    """
    rid = ctx.make_id("stpen_", stay_reservation_id, penalty_amount_usd)
    rows = ctx.find("stay_reservations", stay_reservation_id=stay_reservation_id)
    customer_id = rows[0].get("customer_id") if rows else ""
    ctx.update("stay_reservations", stay_reservation_id, status="cancelled", cancelled_at=ctx.now())
    ctx.create("stay_folio_entries", rid, stay_folio_entry_id=rid,
               stay_reservation_id=stay_reservation_id, customer_id=customer_id,
               event_type="stay_cancellation_charge", charge_category="cancellation_penalty",
               amount_usd=round(float(penalty_amount_usd), 2), currency_charged="USD",
               posted_date=ctx.now()[:10], posted_at=ctx.now(), night_sequence=0, room_sequence=1,
               guest_sequence=0, rooms_affected=0, reason_code="guest_cancellation")
    return (f"Cancellation confirmed on reservation {stay_reservation_id}; penalty line {rid} "
            f"posted for {round(float(penalty_amount_usd), 2)} USD.")


@tool(owner="agent", rw="write")
def raise_cancellation_refund_payout_a740a404(ctx: ToolContext, stay_reservation_id: str,
                                              source_entry_id: str,
                                              refund_amount_usd: float) -> str:
    """Return money to the card a guest originally paid a hotel reservation with. One call posts a
    single payout line to the reservation's folio against the earlier money-in line named, carrying
    the stated amount as money leaving the folio, so the guest sees the payout on the folio and the
    sum reaching the card they paid with; the folio's other lines are left exactly as they stand.
    The call has completed when the confirmation text below comes back naming the new payout line
    and the amount returned.

    Args:
        stay_reservation_id: Id class — the internal reference number of the hotel reservation
            being settled, read from the reservation record returned by the reservation lookup
            before this call.
        source_entry_id: Id class — the reference number of the earlier folio line this payout is
            raised against, read from the folio lines returned by the folio lookup before this
            call.
        refund_amount_usd: Fixed-format class — the money returned to the guest's card, stated as a
            positive USD amount with 2 decimal places, rounded half to even at the second decimal
            and at no earlier point, with no thousands separator and no currency symbol; zero is
            written 0.0 and means nothing reaches the card.

    Returns:
        A single line of confirmation text. It names the reference of the payout line just created
        on the folio (a string beginning strfd_), the reference of the earlier folio line it was
        raised against (a string), and the amount returned (a USD figure with two decimal places).
        The text coming back at all is what indicates the payout was posted; an absent line or an
        error text means nothing was returned.
    """
    rid = ctx.make_id("strfd_", stay_reservation_id, source_entry_id, refund_amount_usd)
    rows = ctx.find("stay_reservations", stay_reservation_id=stay_reservation_id)
    customer_id = rows[0].get("customer_id") if rows else ""
    ctx.create("stay_folio_entries", rid, stay_folio_entry_id=rid,
               stay_reservation_id=stay_reservation_id, customer_id=customer_id,
               event_type="stay_refund_payout", charge_category="refund_payout",
               amount_usd=-round(float(refund_amount_usd), 2), currency_charged="USD",
               posted_date=ctx.now()[:10], posted_at=ctx.now(), night_sequence=0, room_sequence=1,
               guest_sequence=0, rooms_affected=0, source_entry_id=source_entry_id,
               reason_code="guest_cancellation")
    return (f"Refund payout {rid} posted against folio line {source_entry_id} for "
            f"{round(float(refund_amount_usd), 2)} USD.")


@tool(owner="agent", rw="write")
def post_occupancy_supplement_f6d09258(ctx: ToolContext, stay_reservation_id: str,
                                       extra_occupant_charge_usd: float) -> str:
    """Charge a hotel guest for the occupants sharing their rooms beyond what the room rate covers.
    One call posts a single occupant-supplement line to the named reservation's folio for the amount
    stated, so the supplement joins the room money the guest owes for the stay and shows on the
    folio alongside the room nights. Nothing else on the reservation moves. The call has completed
    when the confirmation text below comes back naming the new folio line and the amount charged.

    Args:
        stay_reservation_id: Id class — the internal reference number of the hotel reservation the
            occupants are sharing, read from the reservation record returned by the reservation
            lookup before this call.
        extra_occupant_charge_usd: Fixed-format class — the supplement charged for those occupants
            over the whole stay, as a positive USD amount with 2 decimal places, rounded half to
            even at the second decimal and at no earlier point, with no thousands separator and no
            currency symbol; zero is written 0.0 and means no supplement is charged.

    Returns:
        A single line of confirmation text. It names the reference of the occupant-supplement line
        just created on the folio (a string beginning stocc_), the reference of the reservation it
        was posted to (a string), and the amount charged (a USD figure with two decimal places).
        The text coming back at all is what indicates the line was posted; an absent line or an
        error text means the folio is untouched.
    """
    rid = ctx.make_id("stocc_", stay_reservation_id, extra_occupant_charge_usd)
    rows = ctx.find("stay_reservations", stay_reservation_id=stay_reservation_id)
    customer_id = rows[0].get("customer_id") if rows else ""
    ctx.create("stay_folio_entries", rid, stay_folio_entry_id=rid,
               stay_reservation_id=stay_reservation_id, customer_id=customer_id,
               event_type="stay_room_charge", charge_category="extra_occupant",
               amount_usd=round(float(extra_occupant_charge_usd), 2), currency_charged="USD",
               posted_date=ctx.now()[:10], posted_at=ctx.now(), night_sequence=0, room_sequence=1,
               guest_sequence=0, rooms_affected=0, payment_channel="call_centre",
               reason_code="routine_stay")
    return (f"Occupant supplement line {rid} posted to reservation {stay_reservation_id} for "
            f"{round(float(extra_occupant_charge_usd), 2)} USD.")


@tool(owner="agent", rw="write")
def post_statutory_tax_charge_0b7e8f18(ctx: ToolContext, stay_reservation_id: str,
                                       statutory_tax_amount_usd: float) -> str:
    """Charge a hotel guest the statutory tax the authorities levy on the room money for their stay.
    One call posts a single statutory tax line to the named reservation's folio for the amount
    stated, so the tax joins what the guest owes for the stay and shows on the folio as a tax line.
    Nothing else on the reservation moves. The call has completed when the confirmation text below
    comes back naming the new folio line and the amount charged.

    Args:
        stay_reservation_id: Id class — the internal reference number of the hotel reservation the
            tax is levied on, read from the reservation record returned by the reservation lookup
            before this call.
        statutory_tax_amount_usd: Fixed-format class — the statutory tax due on the stay, as a
            positive USD amount with 2 decimal places, rounded half to even at the second decimal
            and at no earlier point, with no thousands separator and no currency symbol; zero is
            written 0.0 and means no statutory tax is due.

    Returns:
        A single line of confirmation text. It names the reference of the statutory tax line just
        created on the folio (a string beginning sttax_), the reference of the reservation it was
        posted to (a string), and the amount charged (a USD figure with two decimal places). The
        text coming back at all is what indicates the line was posted; an absent line or an error
        text means the folio is untouched.
    """
    rid = ctx.make_id("sttax_", stay_reservation_id, statutory_tax_amount_usd)
    rows = ctx.find("stay_reservations", stay_reservation_id=stay_reservation_id)
    customer_id = rows[0].get("customer_id") if rows else ""
    ctx.create("stay_folio_entries", rid, stay_folio_entry_id=rid,
               stay_reservation_id=stay_reservation_id, customer_id=customer_id,
               event_type="stay_tax_and_fee_charge", charge_category="occupancy_tax",
               amount_usd=round(float(statutory_tax_amount_usd), 2), currency_charged="USD",
               posted_date=ctx.now()[:10], posted_at=ctx.now(), night_sequence=0, room_sequence=1,
               guest_sequence=0, rooms_affected=0, reason_code="routine_stay")
    return (f"Statutory tax line {rid} posted to reservation {stay_reservation_id} for "
            f"{round(float(statutory_tax_amount_usd), 2)} USD.")


@tool(owner="user", rw="write")
def spend_resort_credit_ff384f87(ctx: ToolContext, stay_reservation_id: str, credit_reference: str,
                                 credit_applied_usd: float) -> str:
    """Let the guest spend the property credit standing on their own hotel reservation against what
    they have run up at the property. One call posts a drawdown line to the reservation's folio for
    the amount stated, carrying it as value leaving the credit, and lowers the property credit still
    unspent on the reservation by the same amount; the guest then sees the drawdown on the folio and
    a smaller credit left to spend. The call has completed when the confirmation text below comes
    back naming the drawdown line and what credit is left.

    Args:
        stay_reservation_id: Id class — the internal reference number of the guest's own hotel
            reservation the credit stands on, read from the reservation record returned by the
            reservation lookup before this call.
        credit_reference: Verbatim class — the reference of the property credit being spent, taken
            from the folio line that granted it and copied character for character as it appears
            there, preserving wording, digits, letter case and punctuation, with no translation,
            normalisation, summarisation, addition or deletion (verbatim).
        credit_applied_usd: Fixed-format class — the property credit the guest draws down, as a
            positive USD amount with 2 decimal places, rounded half to even at the second decimal
            and at no earlier point, with no thousands separator and no currency symbol; zero is
            written 0.0 and means no credit is drawn down.

    Returns:
        A single line of confirmation text. It names the reference of the drawdown line just created
        on the folio (a string beginning stcru_), the credit reference it was drawn against (a
        string), the amount drawn down (a USD figure with two decimal places) and the property
        credit left unspent afterwards (a USD figure with two decimal places). The text coming back
        at all is what indicates the drawdown was posted; an absent line or an error text means the
        credit is untouched.
    """
    rid = ctx.make_id("stcru_", stay_reservation_id, credit_reference, credit_applied_usd)
    amount = round(float(credit_applied_usd), 2)
    rows = ctx.find("stay_reservations", stay_reservation_id=stay_reservation_id)
    customer_id = rows[0].get("customer_id") if rows else ""
    remaining = round(float(rows[0].get("resort_credit_balance_usd") or 0) - amount, 2) if rows else 0.0
    ctx.create("stay_folio_entries", rid, stay_folio_entry_id=rid,
               stay_reservation_id=stay_reservation_id, customer_id=customer_id,
               event_type="stay_resort_credit_use", charge_category="resort_credit_use",
               amount_usd=-amount, currency_charged="USD", posted_date=ctx.now()[:10],
               posted_at=ctx.now(), night_sequence=0, room_sequence=1, guest_sequence=0,
               rooms_affected=0, credit_reference=credit_reference, reason_code="guest_request")
    ctx.update("stay_reservations", stay_reservation_id, resort_credit_balance_usd=remaining)
    return (f"Property credit drawdown {rid} posted against credit {credit_reference} for {amount} "
            f"USD; {remaining} USD of credit left unspent.")


@tool(owner="agent", rw="write")
def settle_departure_balance_f8243430(ctx: ToolContext, stay_reservation_id: str,
                                      closing_balance_usd: float) -> str:
    """Close off a hotel stay when the guest leaves and record what is taken from the card on file.
    One call marks the named reservation as departed, stamps it with the date the guest left and
    writes the folio total settled at departure as the amount stated, so the guest sees the stay
    shown as departed and that figure as what was taken. No folio line is added or removed. The call
    has completed when the confirmation text below comes back naming the reservation and the settled
    figure.

    Args:
        stay_reservation_id: Id class — the internal reference number of the hotel reservation being
            closed off, read from the reservation record returned by the reservation lookup before
            this call.
        closing_balance_usd: Fixed-format class — the folio total settled at departure, as a
            positive USD amount with 2 decimal places, rounded half to even at the second decimal
            and at no earlier point, with no thousands separator and no currency symbol; zero is
            written 0.0 and means nothing is taken from the card.

    Returns:
        A single line of confirmation text. It names the reference of the reservation now shown as
        departed (a string), the date of departure recorded on it (a calendar date as YYYY-MM-DD)
        and the folio total settled at departure (a USD figure with two decimal places). The text
        coming back at all is what indicates the stay was closed off; an absent line or an error
        text means the reservation is untouched.
    """
    amount = round(float(closing_balance_usd), 2)
    ctx.update("stay_reservations", stay_reservation_id, status="checked_out",
               checked_out_date=ctx.now()[:10], folio_balance_usd=amount)
    return (f"Reservation {stay_reservation_id} closed off on {ctx.now()[:10]}; folio total settled "
            f"at departure {amount} USD.")

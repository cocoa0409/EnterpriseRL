"""Hidden task tools of the reservation_cancellations_and_no_shows difficulty (Room Reservations).

Each tool performs exactly one atomic write on the Room Reservations records with the values the
caller passes; none of them looks up, checks or decides anything the policy decides.
"""

from erlbench import ToolContext, tool


@tool(owner="agent", rw="write")
def move_reservation_room_563d533b(ctx: ToolContext, reservation_id: str, room_type: str,
                                   nightly_rate: float) -> str:
    """Move one room reservation to another room type and record the nightly rate it carries in that
    room. The reservation keeps its confirmation number, dates, adults, plan and guarantee; only its
    room type and its nightly room rate before tax are replaced by the values given. The guest sees
    the new room type and the new nightly rate on the reservation straight away, and the receipt
    returned confirms the move.

    Args:
        reservation_id: Id class — reference number of the room reservation being moved, as returned
            by the reservation lookup for the guest's confirmation number.
        room_type: Enum class — the room type the reservation moves to, one of: standard_king when the
            guest moves into a standard room with one king bed; standard_two_queens when the guest
            moves into a standard room with two queen beds; deluxe_king when the guest moves into a
            deluxe room with one king bed; junior_suite when the guest moves into a junior suite;
            one_bedroom_suite when the guest moves into a suite with a separate bedroom.
        nightly_rate: Fixed-format class — nightly room rate before tax the reservation carries in the
            new room type, in USD, 2 decimal places, written as a plain number such as 123.45; it is
            stored exactly as given, rounded to 2 decimal places.

    Returns:
        A text receipt of a dictionary with the keys reservation_id (the reservation moved),
        room_type (the room type now on the reservation), nightly_rate (the nightly rate now on the
        reservation, USD with 2 decimal places) and status (the literal "moved", which shows the move
        was recorded).
    """
    rate = round(float(nightly_rate), 2)
    ctx.update("booking_reservations", reservation_id, room_type=room_type, nightly_rate=rate)
    return str({"reservation_id": reservation_id, "room_type": room_type,
                "nightly_rate": rate, "status": "moved"})


@tool(owner="agent", rw="write")
def reprice_extra_persons_22837316(ctx: ToolContext, reservation_id: str, nightly_rate: float) -> str:
    """Record the nightly room rate of one room reservation once the extra-person charge for its
    registered adults has been priced in. Only the nightly room rate before tax changes; the adults,
    room type, dates and guarantee stay as they are. The guest sees the new nightly rate on the
    reservation at once, and the receipt returned confirms the change.

    Args:
        reservation_id: Id class — reference number of the room reservation being re-priced, as
            returned by the reservation lookup for the guest's confirmation number.
        nightly_rate: Fixed-format class — nightly room rate before tax including the extra-person
            charge, in USD, 2 decimal places, written as a plain number such as 123.45; it is stored
            exactly as given, rounded to 2 decimal places.

    Returns:
        A text receipt of a dictionary with the keys reservation_id (the reservation re-priced),
        nightly_rate (the nightly rate now on the reservation, USD with 2 decimal places) and status
        (the literal "repriced", which shows the new rate was recorded).
    """
    rate = round(float(nightly_rate), 2)
    ctx.update("booking_reservations", reservation_id, nightly_rate=rate)
    return str({"reservation_id": reservation_id, "nightly_rate": rate, "status": "repriced"})


@tool(owner="user", rw="write")
def pay_deposit_topup_8cd35ccc(ctx: ToolContext, reservation_id: str, amount: float) -> str:
    """The guest pays a further advance deposit on their own room reservation with the card stored on
    their profile. One new deposit collection is recorded on the reservation for the amount given,
    dated today, and the money is added to what the hotel holds for that reservation. The guest
    sees the payment on the reservation's deposit history straight away, and the receipt returned
    carries the reference of the new collection.

    Args:
        reservation_id: Id class — reference number of the guest's room reservation the deposit is
            paid for, as given to the guest by the agent from the reservation lookup.
        amount: Fixed-format class — amount of the further deposit charged to the card, in USD,
            2 decimal places, positive, written as a plain number such as 123.45; it is stored exactly
            as given, rounded to 2 decimal places.

    Returns:
        A text receipt of a dictionary with the keys charge_id (reference of the new deposit
        collection), reservation_id (the reservation it is held for), amount (the amount collected,
        USD with 2 decimal places), posted_date (the date of the payment, YYYY-MM-DD) and status (the
        literal "collected", which shows the payment went through).
    """
    value = round(float(amount), 2)
    rows = ctx.find("booking_reservations", reservation_id=reservation_id)
    customer_id = rows[0].get("customer_id") if rows else ""
    today = ctx.now()[:10]
    rid = ctx.make_id("bkc_", reservation_id, value, "topup")
    ctx.create("booking_charges", rid, charge_id=rid, reservation_id=reservation_id,
               customer_id=customer_id, event_type="booking_deposit_collect", amount=value,
               posted_date=today, charge_basis="resort_deposit", settlement_source="card_on_file",
               related_charge_id=None, reversal_reason="not_applicable")
    return str({"charge_id": rid, "reservation_id": reservation_id, "amount": value,
                "posted_date": today, "status": "collected"})


@tool(owner="agent", rw="write")
def reverse_penalty_excess_975f0de4(ctx: ToolContext, reservation_id: str, related_charge_id: str,
                                    amount: float) -> str:
    """Reverse part of a late cancellation penalty on one room reservation because the plan's penalty
    basis was misapplied. One new reversal entry is recorded on the reservation for the amount given,
    dated today, naming the original penalty entry and recorded where that penalty was settled; the
    amount reversed goes back to the card on file. The guest sees the reversal in the reservation's
    charge history straight away, and the receipt returned carries the reference of the reversal.

    Args:
        reservation_id: Id class — reference number of the cancelled room reservation the penalty sits
            on, as returned by the reservation lookup.
        related_charge_id: Id class — reference number of the original late cancellation penalty entry
            being reversed, as returned by the reservation charge lookup for that reservation.
        amount: Fixed-format class — amount of the penalty reversed, in USD, 2 decimal places,
            positive, written as a plain number such as 123.45; it is stored exactly as given, rounded
            to 2 decimal places.

    Returns:
        A text receipt of a dictionary with the keys charge_id (reference of the new reversal entry),
        reservation_id (the reservation credited), related_charge_id (the penalty entry reversed),
        amount (the amount reversed, USD with 2 decimal places), posted_date (the date of the reversal,
        YYYY-MM-DD) and status (the literal "reversed", which shows the reversal was recorded).
    """
    value = round(float(amount), 2)
    rows = ctx.find("booking_charges", charge_id=related_charge_id)
    original = rows[0] if rows else {}
    today = ctx.now()[:10]
    rid = ctx.make_id("bkc_", reservation_id, related_charge_id, value)
    ctx.create("booking_charges", rid, charge_id=rid, reservation_id=reservation_id,
               customer_id=original.get("customer_id", ""), event_type="booking_penalty_reversal",
               amount=value, posted_date=today, charge_basis="penalty_reversal",
               settlement_source=original.get("settlement_source", "card_on_file"),
               related_charge_id=related_charge_id, reversal_reason="penalty_basis_misapplied")
    return str({"charge_id": rid, "reservation_id": reservation_id,
                "related_charge_id": related_charge_id, "amount": value, "posted_date": today,
                "status": "reversed"})


@tool(owner="agent", rw="write")
def post_no_show_charge_68d6e4c0(ctx: ToolContext, reservation_id: str, amount: float,
                                 charge_basis: str, settlement_source: str) -> str:
    """Post the no-show charge on one room reservation that the hotel's night audit has marked a
    no-show. One new no-show charge entry is recorded on the reservation for the amount given, dated
    today, under the basis and settlement given; nothing else on the reservation changes. The guest
    sees the charge in the reservation's charge history straight away, and the receipt returned
    carries the reference of the new charge.

    Args:
        reservation_id: Id class — reference number of the room reservation marked a no-show, as
            returned by the reservation lookup for the guest's confirmation number.
        amount: Fixed-format class — amount of the no-show charge, in USD, 2 decimal places, positive,
            written as a plain number such as 123.45; it is stored exactly as given, rounded to
            2 decimal places.
        charge_basis: Enum class — the basis the charge is recorded under, one of: full_prepayment
            never applies to a no-show charge; resort_deposit never applies to a no-show charge;
            first_night_room_and_tax when the reservation's plan charges a no-show the first night;
            full_stay_room_and_tax when the plan charges a no-show the whole stay; deposit_refund never
            applies to a no-show charge; deposit_forfeit never applies to a no-show charge;
            deposit_transfer never applies to a no-show charge; penalty_reversal never applies to a
            no-show charge.
        settlement_source: Enum class — where the charge is settled, one of: card_on_file when no
            money is held for the reservation and the charge goes to the card stored on the profile;
            advance_deposit when the reservation is guaranteed by money the hotel holds and the charge
            is settled from it.

    Returns:
        A text receipt of a dictionary with the keys charge_id (reference of the new no-show charge),
        reservation_id (the reservation charged), amount (the amount charged, USD with 2 decimal
        places), charge_basis (the basis recorded), settlement_source (where it was settled),
        posted_date (the date posted, YYYY-MM-DD) and status (the literal "charged", which shows the
        charge was recorded).
    """
    value = round(float(amount), 2)
    rows = ctx.find("booking_reservations", reservation_id=reservation_id)
    customer_id = rows[0].get("customer_id") if rows else ""
    today = ctx.now()[:10]
    rid = ctx.make_id("bkc_", reservation_id, value, charge_basis, settlement_source)
    ctx.create("booking_charges", rid, charge_id=rid, reservation_id=reservation_id,
               customer_id=customer_id, event_type="booking_no_show_charge", amount=value,
               posted_date=today, charge_basis=charge_basis, settlement_source=settlement_source,
               related_charge_id=None, reversal_reason="not_applicable")
    return str({"charge_id": rid, "reservation_id": reservation_id, "amount": value,
                "charge_basis": charge_basis, "settlement_source": settlement_source,
                "posted_date": today, "status": "charged"})


@tool(owner="user", rw="write")
def request_deposit_refund_05a65982(ctx: ToolContext, reservation_id: str, related_charge_id: str,
                                    amount: float) -> str:
    """The guest instructs the refund of money the hotel holds for their own room reservation to the
    card stored on their profile. One new deposit refund entry is recorded on the reservation for the
    amount given, dated today, naming the deposit payment it is recorded against; the money held for
    the reservation goes down by that amount. The guest sees the refund in the reservation's deposit
    history straight away, and the receipt returned carries the reference of the refund.

    Args:
        reservation_id: Id class — reference number of the guest's room reservation the money is held
            for, as given to the guest by the agent from the reservation lookup.
        related_charge_id: Id class — reference number of the deposit payment the refund is recorded
            against, as given to the guest by the agent from the reservation charge lookup.
        amount: Fixed-format class — amount refunded to the card, in USD, 2 decimal places, positive,
            written as a plain number such as 123.45; it is stored exactly as given, rounded to
            2 decimal places.

    Returns:
        A text receipt of a dictionary with the keys charge_id (reference of the new refund entry),
        reservation_id (the reservation refunded), related_charge_id (the deposit payment named),
        amount (the amount refunded, USD with 2 decimal places), posted_date (the date of the refund,
        YYYY-MM-DD) and status (the literal "refunded", which shows the refund was recorded).
    """
    value = round(float(amount), 2)
    rows = ctx.find("booking_reservations", reservation_id=reservation_id)
    customer_id = rows[0].get("customer_id") if rows else ""
    today = ctx.now()[:10]
    rid = ctx.make_id("bkc_", reservation_id, related_charge_id, value)
    ctx.create("booking_charges", rid, charge_id=rid, reservation_id=reservation_id,
               customer_id=customer_id, event_type="booking_deposit_refund", amount=value,
               posted_date=today, charge_basis="deposit_refund", settlement_source="card_on_file",
               related_charge_id=related_charge_id, reversal_reason="not_applicable")
    return str({"charge_id": rid, "reservation_id": reservation_id,
                "related_charge_id": related_charge_id, "amount": value, "posted_date": today,
                "status": "refunded"})

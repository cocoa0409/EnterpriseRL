"""Hidden task tools for the Wanderlane hotel reservations desk (difficulty: hotel_reservations_desk).

Each function below performs one atomic write on a hotel reservation or its folio. The tools are
hidden: their names appear only as `target_tool` on this difficulty's extended policies, and they
are reached through the unlock/call meta tools. None of them prices anything, aggregates history or
judges whether a policy permits the write; the agent works the figure out from the published terms
and the records and passes it in.
"""

from erlbench import ToolContext, tool

_CREDIT_EVENTS = ("stay_resort_credit_grant", "stay_resort_credit_use")


@tool(owner="agent", rw="write")
def post_arrival_credit_grant_b81202b7(ctx: ToolContext, stay_reservation_id: str,
                                       credit_amount_usd: float,
                                       credit_expiry_date: str) -> str:
    """Place the property credit a guest's stay carries onto their reservation once they have
    arrived, so that the credit becomes spendable at the property. One call writes a single grant
    line to the guest's folio for the amount handed in, stamps it with the last date that credit may
    be spent, and restates the reservation's unspent property credit as the sum of everything
    granted less everything already spent. Afterwards the guest can see the credit standing on the
    reservation and the property can take charges against it. The call has completed when a
    confirmation naming the new grant line, the amount placed and the reservation's restated
    unspent credit comes back.

    Args:
        stay_reservation_id: Id class — the internal reference number of the hotel reservation the
            credit is being placed on, read from the reservation record returned by the reservation
            lookup before this call.
        credit_amount_usd: Fixed-format class — how much property credit is placed on the
            reservation, as a positive USD amount with 2 decimal places, rounded half up to the
            cent; it is stored on the grant line exactly as handed in and is never blank.
        credit_expiry_date: Fixed-format class — the last calendar date on which this credit may be
            spent at the property, written as YYYY-MM-DD in the property's own local calendar, with
            no time part and never blank.

    Returns:
        A confirmation sentence in plain text. It names the reference of the grant line now standing
        on the folio, repeats the amount placed on the reservation as a USD figure to two decimal
        places, repeats the last date the credit may be spent as YYYY-MM-DD, and states the
        reservation's restated unspent property credit as a USD figure to two decimal places. The
        appearance of that sentence, with a grant reference in it, is what indicates the credit has
        been placed.
    """
    reservations = ctx.find("stay_reservations", stay_reservation_id=stay_reservation_id)
    customer_id = reservations[0].get("customer_id") if reservations else ""
    credit_reference = ctx.make_id("scr_", stay_reservation_id)
    entry_id = ctx.make_id("sfe_", stay_reservation_id, credit_amount_usd, credit_expiry_date)
    ctx.create("stay_folio_entries", entry_id,
               stay_folio_entry_id=entry_id,
               stay_reservation_id=stay_reservation_id,
               customer_id=customer_id,
               event_type="stay_resort_credit_grant",
               charge_category="resort_credit_grant",
               amount_usd=round(float(credit_amount_usd), 2),
               posted_date=ctx.now()[:10],
               posted_at=ctx.now(),
               room_sequence=1,
               credit_reference=credit_reference,
               credit_expires_on=credit_expiry_date,
               reason_code="routine_stay")
    _rows = ctx.find("stay_folio_entries", stay_reservation_id=stay_reservation_id)
    balance = round(sum(float(r.get("amount_usd") or 0)
                        for r in _rows if r.get("event_type") in _CREDIT_EVENTS), 2)
    ctx.update("stay_reservations", stay_reservation_id, resort_credit_balance_usd=balance)
    return (f"Property credit grant {entry_id} placed on reservation {stay_reservation_id}: "
            f"{round(float(credit_amount_usd), 2):.2f} USD under credit reference {credit_reference}, "
            f"spendable up to and including {credit_expiry_date}. Unspent property credit on this "
            f"reservation is now {balance:.2f} USD.")


@tool(owner="user", rw="write")
def apply_property_credit_f4ca2b6a(ctx: ToolContext, stay_reservation_id: str,
                                   source_folio_entry_id: str,
                                   credit_applied_usd: float) -> str:
    """Let the guest spend property credit standing on their own reservation against a charge that
    has landed on their folio. One call writes a single credit-use line against the folio line named,
    takes the amount handed in off the property credit held on the reservation, and restates the
    reservation's unspent property credit as the sum of everything granted less everything spent.
    Afterwards the guest owes that much less at the property and can see the credit drawn down. The
    call has completed when a confirmation naming the new credit-use line, the charge it was set
    against and the reservation's restated unspent credit comes back.

    Args:
        stay_reservation_id: Id class — the internal reference number of the guest's own hotel
            reservation whose property credit is being spent, read from the reservation record
            returned by the reservation lookup before this call.
        source_folio_entry_id: Id class — the internal reference number of the folio line the credit
            is being set against, read from the folio lines returned by the folio lookup before this
            call.
        credit_applied_usd: Fixed-format class — how much property credit the guest spends here, as
            a positive USD amount with 2 decimal places, rounded half up to the cent; it is recorded
            on the credit account as a reduction of that size and is never blank.

    Returns:
        A confirmation sentence in plain text. It names the reference of the credit-use line now
        standing on the folio, repeats the amount of credit spent as a USD figure to two decimal
        places, names the folio line the credit was set against, and states the reservation's
        restated unspent property credit as a USD figure to two decimal places. The appearance of
        that sentence, with a credit-use reference in it, is what indicates the credit has been
        spent.
    """
    reservations = ctx.find("stay_reservations", stay_reservation_id=stay_reservation_id)
    customer_id = reservations[0].get("customer_id") if reservations else ""
    grants = [r for r in ctx.find("stay_folio_entries", stay_reservation_id=stay_reservation_id)
              if r.get("event_type") == "stay_resort_credit_grant"]
    credit_reference = grants[0].get("credit_reference") if grants else ""
    entry_id = ctx.make_id("sfe_", stay_reservation_id, source_folio_entry_id, credit_applied_usd)
    ctx.create("stay_folio_entries", entry_id,
               stay_folio_entry_id=entry_id,
               stay_reservation_id=stay_reservation_id,
               customer_id=customer_id,
               event_type="stay_resort_credit_use",
               charge_category="resort_credit_use",
               amount_usd=-round(float(credit_applied_usd), 2),
               posted_date=ctx.now()[:10],
               posted_at=ctx.now(),
               room_sequence=1,
               credit_reference=credit_reference,
               source_entry_id=source_folio_entry_id,
               reason_code="guest_request")
    _rows = ctx.find("stay_folio_entries", stay_reservation_id=stay_reservation_id)
    balance = round(sum(float(r.get("amount_usd") or 0)
                        for r in _rows if r.get("event_type") in _CREDIT_EVENTS), 2)
    ctx.update("stay_reservations", stay_reservation_id, resort_credit_balance_usd=balance)
    return (f"Property credit use {entry_id} recorded on reservation {stay_reservation_id}: "
            f"{round(float(credit_applied_usd), 2):.2f} USD of credit set against folio line "
            f"{source_folio_entry_id}. Unspent property credit on this reservation is now "
            f"{balance:.2f} USD.")


@tool(owner="agent", rw="write")
def post_closing_room_night_00233ccc(ctx: ToolContext, stay_reservation_id: str,
                                     room_night_amount_usd: float, stay_date: str) -> str:
    """Bring a guest's folio up to date by posting the room rate for one night of their stay that
    has not yet been charged. One call writes a single room-night line to the folio for the night
    named and the amount handed in, numbered after the room nights already standing there, so that
    the folio shows every night of the stay charged. Afterwards the guest can see that night's room
    rate on the folio alongside the nights already posted. The call has completed when a confirmation
    naming the new room-night line, the night it covers and the amount charged comes back.

    Args:
        stay_reservation_id: Id class — the internal reference number of the hotel reservation whose
            folio is being brought up to date, read from the reservation record returned by the
            reservation lookup before this call.
        room_night_amount_usd: Fixed-format class — the room rate charged for that one night, as a
            positive USD amount with 2 decimal places, rounded half up to the cent; it is posted to
            the folio exactly as handed in and is never blank.
        stay_date: Fixed-format class — the night of the stay the room rate is charged for, written
            as YYYY-MM-DD in the property's own local calendar, with no time part and never blank.

    Returns:
        A confirmation sentence in plain text. It names the reference of the room-night line now
        standing on the folio, repeats the night charged as YYYY-MM-DD, repeats the amount charged as
        a USD figure to two decimal places, and states which night of the stay the line was numbered
        as. The appearance of that sentence, with a room-night reference in it, is what indicates the
        night has been charged.
    """
    reservations = ctx.find("stay_reservations", stay_reservation_id=stay_reservation_id)
    customer_id = reservations[0].get("customer_id") if reservations else ""
    existing = [r for r in ctx.find("stay_folio_entries", stay_reservation_id=stay_reservation_id)
                if r.get("charge_category") == "room_night"]
    night_number = len(existing) + 1
    entry_id = ctx.make_id("sfe_", stay_reservation_id, room_night_amount_usd, stay_date)
    ctx.create("stay_folio_entries", entry_id,
               stay_folio_entry_id=entry_id,
               stay_reservation_id=stay_reservation_id,
               customer_id=customer_id,
               event_type="stay_room_charge",
               charge_category="room_night",
               amount_usd=round(float(room_night_amount_usd), 2),
               currency_charged="USD",
               stay_date=stay_date,
               posted_date=ctx.now()[:10],
               posted_at=ctx.now(),
               night_sequence=night_number,
               room_sequence=1,
               payment_channel="property_front_desk",
               reason_code="routine_stay")
    return (f"Room night {entry_id} posted to reservation {stay_reservation_id} for {stay_date}: "
            f"{round(float(room_night_amount_usd), 2):.2f} USD, numbered as night {night_number} of "
            "the stay.")


@tool(owner="agent", rw="write")
def post_closing_tax_charge_e4008804(ctx: ToolContext, stay_reservation_id: str,
                                     tax_amount_usd: float, stay_date: str) -> str:
    """Post the statutory charge a guest owes for one night of their stay to their folio. One call
    writes a single statutory line to the folio for the night named and the amount handed in, so that
    the folio shows the tax settled for that night. Afterwards the guest can see the statutory charge
    for that night standing alongside the room rate it follows. The call has completed when a
    confirmation naming the new statutory line, the night it covers and the amount charged comes
    back.

    Args:
        stay_reservation_id: Id class — the internal reference number of the hotel reservation whose
            folio the statutory charge is posted to, read from the reservation record returned by the
            reservation lookup before this call.
        tax_amount_usd: Fixed-format class — the statutory charge for that one night, as a positive
            USD amount with 2 decimal places, rounded half up to the cent; it is posted to the folio
            exactly as handed in and is never blank.
        stay_date: Fixed-format class — the night of the stay the statutory charge is raised for,
            written as YYYY-MM-DD in the property's own local calendar, with no time part and never
            blank.

    Returns:
        A confirmation sentence in plain text. It names the reference of the statutory line now
        standing on the folio, repeats the night it covers as YYYY-MM-DD, and repeats the amount
        charged as a USD figure to two decimal places. The appearance of that sentence, with a
        statutory line reference in it, is what indicates the charge has been posted.
    """
    reservations = ctx.find("stay_reservations", stay_reservation_id=stay_reservation_id)
    customer_id = reservations[0].get("customer_id") if reservations else ""
    existing = [r for r in ctx.find("stay_folio_entries", stay_reservation_id=stay_reservation_id)
                if r.get("charge_category") == "occupancy_tax"]
    entry_id = ctx.make_id("sfe_", stay_reservation_id, tax_amount_usd, stay_date)
    ctx.create("stay_folio_entries", entry_id,
               stay_folio_entry_id=entry_id,
               stay_reservation_id=stay_reservation_id,
               customer_id=customer_id,
               event_type="stay_tax_and_fee_charge",
               charge_category="occupancy_tax",
               amount_usd=round(float(tax_amount_usd), 2),
               currency_charged="USD",
               stay_date=stay_date,
               posted_date=ctx.now()[:10],
               posted_at=ctx.now(),
               night_sequence=len(existing) + 1,
               room_sequence=1,
               reason_code="routine_stay")
    return (f"Statutory charge {entry_id} posted to reservation {stay_reservation_id} for "
            f"{stay_date}: {round(float(tax_amount_usd), 2):.2f} USD.")


@tool(owner="agent", rw="write")
def post_closing_breakfast_charge_10224aa5(ctx: ToolContext, stay_reservation_id: str,
                                           breakfast_amount_usd: float, stay_date: str) -> str:
    """Post the breakfast a guest owes for one morning of their stay to their folio. One call writes
    a single breakfast line to the folio against the lead guest for the morning named and the amount
    handed in, so that the folio shows the breakfast settled for that morning. Afterwards the guest
    can see the breakfast standing on the folio with the other extras taken at the property. The call
    has completed when a confirmation naming the new breakfast line, the morning it covers and the
    amount charged comes back.

    Args:
        stay_reservation_id: Id class — the internal reference number of the hotel reservation whose
            folio the breakfast is posted to, read from the reservation record returned by the
            reservation lookup before this call.
        breakfast_amount_usd: Fixed-format class — the breakfast charged for that one morning, as a
            positive USD amount with 2 decimal places, rounded half up to the cent; it is posted to
            the folio exactly as handed in and is never blank.
        stay_date: Fixed-format class — the morning of the stay the breakfast is charged for, written
            as YYYY-MM-DD in the property's own local calendar, with no time part and never blank.

    Returns:
        A confirmation sentence in plain text. It names the reference of the breakfast line now
        standing on the folio, repeats the morning it covers as YYYY-MM-DD, and repeats the amount
        charged as a USD figure to two decimal places. The appearance of that sentence, with a
        breakfast line reference in it, is what indicates the breakfast has been charged.
    """
    reservations = ctx.find("stay_reservations", stay_reservation_id=stay_reservation_id)
    customer_id = reservations[0].get("customer_id") if reservations else ""
    entry_id = ctx.make_id("sfe_", stay_reservation_id, breakfast_amount_usd, stay_date)
    ctx.create("stay_folio_entries", entry_id,
               stay_folio_entry_id=entry_id,
               stay_reservation_id=stay_reservation_id,
               customer_id=customer_id,
               event_type="stay_incidental_charge",
               charge_category="breakfast",
               amount_usd=round(float(breakfast_amount_usd), 2),
               currency_charged="USD",
               stay_date=stay_date,
               posted_date=ctx.now()[:10],
               posted_at=ctx.now(),
               night_sequence=0,
               room_sequence=1,
               guest_sequence=1,
               payment_channel="property_front_desk",
               reason_code="guest_request")
    return (f"Breakfast {entry_id} posted to reservation {stay_reservation_id} for {stay_date}: "
            f"{round(float(breakfast_amount_usd), 2):.2f} USD.")


@tool(owner="user", rw="write")
def settle_departure_folio_3e89900b(ctx: ToolContext, stay_reservation_id: str,
                                    closing_folio_balance_usd: float) -> str:
    """Let the guest close off their own folio as they leave the property. One call moves the
    reservation from in house to departed, stamps the date the guest actually left, and records the
    figure the guest settles on the card held against the reservation as the folio balance. Afterwards
    the reservation reads as departed and the settled figure stands against it, so nothing further is
    taken at the front desk. The call has completed when a confirmation naming the reservation, the
    departure date recorded and the settled figure comes back.

    Args:
        stay_reservation_id: Id class — the internal reference number of the guest's own hotel
            reservation being closed off, read from the reservation record returned by the reservation
            lookup before this call.
        closing_folio_balance_usd: Fixed-format class — the figure the guest settles as the folio is
            closed, as a USD amount with 2 decimal places, rounded half up to the cent; it is recorded
            against the reservation exactly as handed in and is never blank.

    Returns:
        A confirmation sentence in plain text. It names the reservation now recorded as departed,
        repeats the departure date recorded as YYYY-MM-DD, and repeats the settled folio figure as a
        USD figure to two decimal places. The appearance of that sentence, naming the reservation as
        departed, is what indicates the folio has been closed off.
    """
    ctx.update("stay_reservations", stay_reservation_id,
               status="checked_out",
               checked_out_date=ctx.now()[:10],
               folio_balance_usd=round(float(closing_folio_balance_usd), 2))
    return (f"Reservation {stay_reservation_id} recorded as departed on {ctx.now()[:10]}; folio "
            f"closed off at {round(float(closing_folio_balance_usd), 2):.2f} USD settled on the card "
            "held against the reservation.")

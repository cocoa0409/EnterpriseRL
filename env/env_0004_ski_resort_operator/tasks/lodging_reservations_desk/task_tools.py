"""Hidden task tools for the lodging reservations desk of the Granite Ridge Mountain Collective.

Each tool lands exactly one business act on one reservation. The desk agent (or the household
itself, where the act is the household's own) works the figure out from the collective's published
terms and the records, and passes it in; these tools only write what they are given.
"""

from erlbench import ToolContext, tool


@tool(owner="agent", rw="write")
def post_stay_room_charge_ee3504ba(ctx: ToolContext, lodging_id: str, room_charge_amount_usd: float,
                                   nights_covered: int, rate_plan: str) -> str:
    """Price a booked stay onto its folio: post the room rate for the stay to the folio of one lodging
    reservation as a single room rate entry covering the nights stated, and raise the reservation's
    outstanding folio balance by the amount posted. The household sees one room rate line on the folio
    carrying the amount, the number of nights it covers and the published rate window the nights were
    priced in, and the folio balance on the reservation rises by that amount. The call has completed
    when the confirmation naming the new folio entry reference and the amount posted comes back.

    Args:
        lodging_id: Id class — the reference number identifying the lodging reservation whose folio the
            room rate is posted to; read it from the reservation record the lodging
            reservation lookup returns.
        room_charge_amount_usd: Fixed-format class — the room rate for the stay that is posted to the
            folio, in USD, as a decimal amount rounded to 2 decimal places; a value carrying more
            decimals is stored rounded to the cent.
        nights_covered: Fixed-format class — how many nights of the stay the posted entry covers,
            given as a whole number of nights, persons or items, that is an integer count of nights
            with no fractions and no unit text.
        rate_plan: Enum class — the published rate window the nights on this entry were priced in, one
            of exactly these values: holiday, used where the nights of the entry are priced at the unit
            type's holiday nightly rate; peak, used where they are priced at its peak nightly rate;
            base, used where they are priced at its base nightly rate; none, which records no rate
            window at all and is reserved for folio entries that are not room rate entries.

    Returns:
        A confirmation sentence on success, carrying the reference number of the folio entry created,
        the amount in USD posted to the folio, the number of nights the entry covers, the rate window
        recorded on it and the reservation's folio balance after the posting. Receiving that sentence,
        with a folio entry reference in it, is what indicates the entry has been written.
    """
    rows = ctx.find("lodging_holdings", lodging_id=lodging_id)
    reservation = rows[0] if rows else {}
    amount = round(float(room_charge_amount_usd), 2)
    rid = ctx.make_id("lfe_", lodging_id, room_charge_amount_usd, nights_covered, rate_plan)
    ctx.create("lodging_folio", rid, folio_event_id=rid, lodging_id=lodging_id,
               customer_id=reservation.get("customer_id", ""), event_type="lodging_room_charge",
               season_code=reservation.get("season_code", ""), event_date=ctx.now()[:10],
               service_date=reservation.get("arrival_date", ""), amount_usd=amount,
               quantity=int(nights_covered), charge_category="room_rate", rate_plan=rate_plan,
               payment_method="none", deposit_status="none", outlet="none")
    balance = round(float(reservation.get("folio_balance_usd") or 0) + amount, 2)
    ctx.update("lodging_holdings", lodging_id, folio_balance_usd=balance)
    return (f"Room rate posted to folio {rid}: {amount} USD over {int(nights_covered)} night(s) on the "
            f"{rate_plan} rate window; folio balance now {balance} USD.")


@tool(owner="user", rw="write")
def authorise_reservation_deposit_3e63cb2f(ctx: ToolContext, lodging_id: str, deposit_amount_usd: float,
                                           payment_method: str) -> str:
    """Let the household itself authorise the deposit on one of its lodging reservations and have it
    taken: a deposit entry for the amount authorised is written to that reservation's folio against the
    payment route named, and the deposit standing against the reservation rises by that amount. The
    household sees the deposit line on the folio and the deposit held on the reservation go up by what
    they authorised, with the money taken from the route they named. The call has completed when the
    confirmation naming the new folio entry reference and the deposit held comes back.

    Args:
        lodging_id: Id class — the reference number identifying the lodging reservation the deposit is
            authorised on; it is read from the reservation record the desk has on screen and given to
            the household.
        deposit_amount_usd: Fixed-format class — the deposit the household authorises, in USD, as a
            decimal amount rounded to 2 decimal places; a value carrying more decimals is taken rounded
            to the cent.
        payment_method: Enum class — where the money is taken from, one of exactly these values:
            card_on_file, used where it is taken from the card the household already has registered
            with the collective; card_at_desk, used where the household presents a card in person;
            bank_transfer, used where the household sends the money from their bank; lodging_credit,
            used where the household spends lodging credit it already holds; travel_partner, used where
            a travel partner settles on the household's behalf; none, which records no money route at
            all and is reserved for folio entries that move no money.

    Returns:
        A confirmation sentence on success, carrying the reference number of the folio entry created,
        the deposit amount in USD authorised, the route the money was taken from and the deposit now
        standing against the reservation. Receiving that sentence, with a folio entry reference in it,
        is what indicates the deposit has been taken.
    """
    rows = ctx.find("lodging_holdings", lodging_id=lodging_id)
    reservation = rows[0] if rows else {}
    amount = round(float(deposit_amount_usd), 2)
    rid = ctx.make_id("lfe_", lodging_id, deposit_amount_usd, payment_method)
    ctx.create("lodging_folio", rid, folio_event_id=rid, lodging_id=lodging_id,
               customer_id=reservation.get("customer_id", ""), event_type="lodging_deposit_charge",
               season_code=reservation.get("season_code", ""), event_date=ctx.now()[:10],
               amount_usd=amount, charge_category="deposit", deposit_status="held",
               payment_method=payment_method, rate_plan="none", outlet="none")
    held = round(float(reservation.get("deposit_held_usd") or 0) + amount, 2)
    ctx.update("lodging_holdings", lodging_id, deposit_held_usd=held)
    return (f"Deposit authorised and taken on folio {rid}: {amount} USD via {payment_method}; "
            f"deposit now held against the reservation {held} USD.")


@tool(owner="agent", rw="write")
def post_stay_resort_charge_f79fa34a(ctx: ToolContext, lodging_id: str, resort_charge_amount_usd: float,
                                     nights_covered: int) -> str:
    """Put the nightly resort charge a stay owes onto its folio: post one resort charge entry to the
    folio of a lodging reservation for the amount stated over the nights stated, and raise the
    reservation's outstanding folio balance by that amount. The household sees a single resort charge
    line on the folio carrying the amount and the number of nights it covers, and the folio balance on
    the reservation goes up by the same amount. The call has completed when the confirmation naming the
    new folio entry reference and the amount posted comes back.

    Args:
        lodging_id: Id class — the reference number identifying the lodging reservation whose folio the
            resort charge is posted to; read it from the reservation record the lodging
            reservation lookup returns.
        resort_charge_amount_usd: Fixed-format class — the resort charge posted for the stay, in USD, as
            a decimal amount rounded to 2 decimal places; a value carrying more decimals is stored
            rounded to the cent.
        nights_covered: Fixed-format class — how many nights of the stay this resort charge entry
            covers, given as a whole number of nights, persons or items, that is an integer count of
            nights with no fractions and no unit text.

    Returns:
        A confirmation sentence on success, carrying the reference number of the folio entry created,
        the amount in USD posted, the number of nights the entry covers and the reservation's folio
        balance after the posting. Receiving that sentence, with a folio entry reference in it, is what
        indicates the entry has been written.
    """
    rows = ctx.find("lodging_holdings", lodging_id=lodging_id)
    reservation = rows[0] if rows else {}
    amount = round(float(resort_charge_amount_usd), 2)
    rid = ctx.make_id("lfe_", lodging_id, resort_charge_amount_usd, nights_covered)
    ctx.create("lodging_folio", rid, folio_event_id=rid, lodging_id=lodging_id,
               customer_id=reservation.get("customer_id", ""), event_type="lodging_resort_fee",
               season_code=reservation.get("season_code", ""), event_date=ctx.now()[:10],
               service_date=reservation.get("arrival_date", ""), amount_usd=amount,
               quantity=int(nights_covered), charge_category="resort_fee", rate_plan="none",
               payment_method="none", deposit_status="none", outlet="none")
    balance = round(float(reservation.get("folio_balance_usd") or 0) + amount, 2)
    ctx.update("lodging_holdings", lodging_id, folio_balance_usd=balance)
    return (f"Resort charge posted to folio {rid}: {amount} USD over {int(nights_covered)} night(s); "
            f"folio balance now {balance} USD.")


@tool(owner="agent", rw="write")
def post_departure_service_charge_1468621e(ctx: ToolContext, lodging_id: str,
                                           service_charge_amount_usd: float, nights_covered: int) -> str:
    """Put what a stay owes on departure for servicing the unit and for its nightly extras onto its
    folio: post one departure services entry to the folio of a lodging reservation for the amount
    stated over the nights stated, and raise the reservation's outstanding folio balance by that
    amount. The household sees a single housekeeping line on the folio carrying the amount and the
    nights the nightly extras were worked out over, and the folio balance on the reservation goes up by
    the same amount. The call has completed when the confirmation naming the new folio entry reference
    and the amount posted comes back.

    Args:
        lodging_id: Id class — the reference number identifying the lodging reservation whose folio the
            departure services charge is posted to; read it from the reservation record the
            lodging reservation lookup returns.
        service_charge_amount_usd: Fixed-format class — the departure services charge posted for the
            stay, in USD, as a decimal amount rounded to 2 decimal places; a value carrying more
            decimals is stored rounded to the cent.
        nights_covered: Fixed-format class — how many nights the nightly elements of this entry were
            worked out over, given as a whole number of nights, persons or items, that is an integer
            count of nights with no fractions and no unit text.

    Returns:
        A confirmation sentence on success, carrying the reference number of the folio entry created,
        the amount in USD posted, the number of nights the nightly elements were worked out over and
        the reservation's folio balance after the posting. Receiving that sentence, with a folio entry
        reference in it, is what indicates the entry has been written.
    """
    rows = ctx.find("lodging_holdings", lodging_id=lodging_id)
    reservation = rows[0] if rows else {}
    amount = round(float(service_charge_amount_usd), 2)
    rid = ctx.make_id("lfe_", lodging_id, service_charge_amount_usd, nights_covered)
    ctx.create("lodging_folio", rid, folio_event_id=rid, lodging_id=lodging_id,
               customer_id=reservation.get("customer_id", ""), event_type="lodging_incidental_charge",
               season_code=reservation.get("season_code", ""), event_date=ctx.now()[:10],
               service_date=reservation.get("checked_out_at", "")[:10], amount_usd=amount,
               quantity=int(nights_covered), charge_category="cleaning_fee", rate_plan="none",
               payment_method="none", deposit_status="none", outlet="front_desk")
    balance = round(float(reservation.get("folio_balance_usd") or 0) + amount, 2)
    ctx.update("lodging_holdings", lodging_id, folio_balance_usd=balance)
    return (f"Departure services charge posted to folio {rid}: {amount} USD over {int(nights_covered)} "
            f"night(s); folio balance now {balance} USD.")


@tool(owner="agent", rw="write")
def post_early_departure_charge_bb461064(ctx: ToolContext, lodging_id: str, retained_amount_usd: float,
                                         nights_retained: int) -> str:
    """Put what a stay retains for nights the party gave up by leaving early onto its folio: post one
    retained room rate entry to the folio of a lodging reservation for the amount stated over the
    nights stated, and raise the reservation's outstanding folio balance by that amount. The household
    sees a single retained nights line on the folio carrying the amount and how many nights it was
    worked out over, and the folio balance on the reservation goes up by the same amount. The call has
    completed when the confirmation naming the new folio entry reference and the amount retained comes
    back.

    Args:
        lodging_id: Id class — the reference number identifying the lodging reservation whose folio the
            retained amount is posted to; read it from the reservation record the lodging
            reservation lookup returns.
        retained_amount_usd: Fixed-format class — the amount retained for the nights given up, in USD,
            as a decimal amount rounded to 2 decimal places; a value carrying more decimals is stored
            rounded to the cent.
        nights_retained: Fixed-format class — how many nights the retained amount was worked out over,
            given as a whole number of nights, persons or items, that is an integer count of nights
            with no fractions and no unit text.

    Returns:
        A confirmation sentence on success, carrying the reference number of the folio entry created,
        the amount in USD retained, the number of nights it was worked out over and the reservation's
        folio balance after the posting. Receiving that sentence, with a folio entry reference in it,
        is what indicates the entry has been written.
    """
    rows = ctx.find("lodging_holdings", lodging_id=lodging_id)
    reservation = rows[0] if rows else {}
    amount = round(float(retained_amount_usd), 2)
    rid = ctx.make_id("lfe_", lodging_id, retained_amount_usd, nights_retained)
    ctx.create("lodging_folio", rid, folio_event_id=rid, lodging_id=lodging_id,
               customer_id=reservation.get("customer_id", ""), event_type="lodging_fee_charge",
               season_code=reservation.get("season_code", ""), event_date=ctx.now()[:10],
               amount_usd=amount, quantity=int(nights_retained),
               charge_category="cancellation_fee", rate_plan="none", payment_method="none",
               deposit_status="none", outlet="none")
    balance = round(float(reservation.get("folio_balance_usd") or 0) + amount, 2)
    ctx.update("lodging_holdings", lodging_id, folio_balance_usd=balance)
    return (f"Retained room rate posted to folio {rid}: {amount} USD over {int(nights_retained)} "
            f"night(s) given up; folio balance now {balance} USD.")


@tool(owner="user", rw="write")
def settle_departure_folio_07fd1088(ctx: ToolContext, lodging_id: str, settlement_amount_usd: float,
                                    payment_method: str) -> str:
    """Let the household itself settle the folio of one of its lodging reservations: a payment entry
    for the amount the household settles is written to that reservation's folio against the payment
    route named, and the reservation's outstanding folio balance falls by that amount. The household
    sees the payment line on the folio and the amount still to be collected on the reservation come
    down by what they paid, with the money taken from the route they named. The call has completed
    when the confirmation naming the new folio entry reference and the folio balance left comes back.

    Args:
        lodging_id: Id class — the reference number identifying the lodging reservation whose folio the
            household settles; it is read from the reservation record the desk has on screen and given
            to the household.
        settlement_amount_usd: Fixed-format class — the amount the household settles, in USD, as a
            decimal amount rounded to 2 decimal places; a value carrying more decimals is taken rounded
            to the cent.
        payment_method: Enum class — where the money is taken from, one of exactly these values:
            card_on_file, used where it is taken from the card the household already has registered
            with the collective; card_at_desk, used where the household presents a card in person;
            bank_transfer, used where the household sends the money from their bank; lodging_credit,
            used where the household spends lodging credit it already holds; travel_partner, used where
            a travel partner settles on the household's behalf; none, which records no money route at
            all and is reserved for folio entries that move no money.

    Returns:
        A confirmation sentence on success, carrying the reference number of the folio entry created,
        the amount in USD settled, the route the money was taken from and the amount left on the folio
        afterwards. Receiving that sentence, with a folio entry reference in it, is what indicates the
        payment has been written.
    """
    rows = ctx.find("lodging_holdings", lodging_id=lodging_id)
    reservation = rows[0] if rows else {}
    amount = round(float(settlement_amount_usd), 2)
    rid = ctx.make_id("lfe_", lodging_id, settlement_amount_usd, payment_method)
    ctx.create("lodging_folio", rid, folio_event_id=rid, lodging_id=lodging_id,
               customer_id=reservation.get("customer_id", ""), event_type="lodging_payment",
               season_code=reservation.get("season_code", ""), event_date=ctx.now()[:10],
               amount_usd=amount, charge_category="room_rate", rate_plan="none",
               payment_method=payment_method, deposit_status="none", outlet="none")
    balance = round(float(reservation.get("folio_balance_usd") or 0) - amount, 2)
    ctx.update("lodging_holdings", lodging_id, folio_balance_usd=balance)
    return (f"Folio settled on entry {rid}: {amount} USD via {payment_method}; "
            f"folio balance now {balance} USD.")

"""Hidden task tools for the air ticketing desk (scenario: online_travel_agency).

Each function lands exactly one atomic business write on an air booking or on its ledger of
booked lines. None of them aggregates history, prices anything, or judges whether the write is
due: the desk works the figure out from the published terms and the records, and passes it in.
"""

from erlbench import ToolContext, tool


@tool(owner="agent", rw="write")
def withhold_no_show_penalty_8882d2a1(ctx: ToolContext, air_booking_id: str, customer_id: str,
                                      penalty_amount_usd: float) -> str:
    """Withhold a no-show penalty from an air booking held in a traveller's name. One call posts a
    single penalty line to that booking's ledger for the stated sum, marks it as the booking's
    no-show penalty, dates it on today's business date, and raises the booking's net paid total by
    the same sum, so the money stays with the airline instead of returning to the traveller. The
    traveller can see the penalty line and the new net paid total on the booking as soon as the
    call comes back with the reference of the line that was posted.

    Args:
        air_booking_id: Id class — the internal reference number of the air booking the penalty is
            withheld from, read from the traveller's booking record returned by the booking lookup.
        customer_id: Id class — the traveller reference number the penalty line is recorded
            against, read from the traveller profile returned by the profile lookup.
        penalty_amount_usd: Fixed-format class — the sum withheld from the booking, in USD with
            exactly 2 decimal places, stated as a positive number and rounded to the nearest
            cent at the moment it is passed; there is no empty value and no other currency.

    Returns:
        A plain-language confirmation line naming the reference of the penalty line that was
        posted, the sum withheld in USD to two decimal places, and the booking's net paid total
        after the line landed. The presence of that line reference is what indicates the penalty
        was recorded; nothing is returned when no line is posted.
    """
    amount = round(float(penalty_amount_usd), 2)
    rid = ctx.make_id("aev_", air_booking_id, customer_id, amount, "no_show_penalty")
    ctx.create("air_booking_events", rid, air_event_id=rid, air_booking_id=air_booking_id,
               customer_id=customer_id, event_type="air_penalty_charge",
               charge_category="no_show_penalty", amount_usd=amount, currency_charged="USD",
               posted_date=ctx.now()[:10], posted_at=ctx.now(), passenger_sequence=1,
               segment_sequence=0, bag_sequence=0, payment_channel="call_centre",
               source_event_id="", credit_voucher_code="", credit_expires_on="",
               schedule_change_minutes=0, notice_reference="", reason_code="traveller_no_show")
    rows = ctx.find("air_bookings", air_booking_id=air_booking_id)
    total = round(float(rows[0].get("amount_paid_usd") or 0) + amount, 2) if rows else amount
    if rows:
        ctx.update("air_bookings", air_booking_id, amount_paid_usd=total)
    return (f"Penalty line {rid} posted to booking {air_booking_id}: {amount:.2f} USD withheld as "
            f"the no-show penalty. Net paid on the booking is now {total:.2f} USD.")


@tool(owner="agent", rw="write")
def return_unflown_taxes_e343d675(ctx: ToolContext, air_booking_id: str, customer_id: str,
                                  payout_amount_usd: float) -> str:
    """Return carrier-imposed taxes and fees on an unflown air ticket to the card the traveller
    paid with. One call posts a single payout line to that booking's ledger for the stated sum,
    marks it as money going back to the original form of payment, dates it on today's business
    date, and lowers the booking's net paid total by the same sum. The traveller sees the payout
    line on the booking and the money on the card statement the airline settles it to; the call
    comes back with the reference of the payout line that was posted.

    Args:
        air_booking_id: Id class — the internal reference number of the air booking whose taxes are
            returned, read from the traveller's booking record returned by the booking lookup.
        customer_id: Id class — the traveller reference number the payout line is recorded against,
            read from the traveller profile returned by the profile lookup.
        payout_amount_usd: Fixed-format class — the sum returned to the card, in USD with exactly
            2 decimal places, stated as a positive number and rounded to the nearest
            cent at the moment it is passed; there is no empty value and no other currency.

    Returns:
        A plain-language confirmation line naming the reference of the payout line that was posted,
        the sum returned in USD to two decimal places, and the booking's net paid total once the
        payout landed. The presence of that line reference is what indicates the money was sent
        back; nothing is returned when no line is posted.
    """
    amount = round(float(payout_amount_usd), 2)
    rid = ctx.make_id("aev_", air_booking_id, customer_id, amount, "refund_payout")
    ctx.create("air_booking_events", rid, air_event_id=rid, air_booking_id=air_booking_id,
               customer_id=customer_id, event_type="air_refund_payout",
               charge_category="refund_payout", amount_usd=-amount, currency_charged="USD",
               posted_date=ctx.now()[:10], posted_at=ctx.now(), passenger_sequence=1,
               segment_sequence=0, bag_sequence=0, payment_channel="call_centre",
               source_event_id="", credit_voucher_code="", credit_expires_on="",
               schedule_change_minutes=0, notice_reference="", reason_code="routine_booking")
    rows = ctx.find("air_bookings", air_booking_id=air_booking_id)
    total = round(float(rows[0].get("amount_paid_usd") or 0) - amount, 2) if rows else -amount
    if rows:
        ctx.update("air_bookings", air_booking_id, amount_paid_usd=total)
    return (f"Payout line {rid} posted to booking {air_booking_id}: {amount:.2f} USD returned to "
            f"the original form of payment. Net paid on the booking is now {total:.2f} USD.")


@tool(owner="agent", rw="write")
def issue_travel_credit_599fe29f(ctx: ToolContext, air_booking_id: str, customer_id: str,
                                 voucher_value_usd: float, voucher_expires_on: str) -> str:
    """Put the value left on a cancelled air ticket onto a travel credit voucher in the
    traveller's own name. One call mints a voucher code, posts a single credit-issue line carrying
    the stated value and the stated last redeemable date to that booking's ledger, and raises the
    booking's open travel credit by the same value. The traveller can quote the voucher code
    against a future itinerary and see the open credit on the booking; the call comes back with
    the voucher code and the reference of the line that carries it.

    Args:
        air_booking_id: Id class — the internal reference number of the air booking whose remaining
            value goes onto the voucher, read from the traveller's booking record returned by the
            booking lookup.
        customer_id: Id class — the traveller reference number the voucher is issued to, read from
            the traveller profile returned by the profile lookup.
        voucher_value_usd: Fixed-format class — the value placed on the voucher, in USD with
            exactly 2 decimal places, stated as a positive number and rounded to the nearest
            cent at the moment it is passed; there is no empty value and no other currency.
        voucher_expires_on: Fixed-format class — the last calendar date on which the voucher may be
            redeemed, written as YYYY-MM-DD in the traveller's local calendar, with no time part
            and no empty value.

    Returns:
        A plain-language confirmation line naming the voucher code that was minted, the reference
        of the credit-issue line that carries it, the value placed on it in USD to two decimal
        places, and the last date it may be redeemed. The presence of the voucher code is what
        indicates the voucher now stands in the traveller's name; nothing is returned when no
        voucher is minted.
    """
    value = round(float(voucher_value_usd), 2)
    rid = ctx.make_id("aev_", air_booking_id, customer_id, value, "credit_issue")
    code = "WL" + rid[-8:].upper()
    ctx.create("air_booking_events", rid, air_event_id=rid, air_booking_id=air_booking_id,
               customer_id=customer_id, event_type="air_credit_issue",
               charge_category="credit_issue", amount_usd=value, currency_charged="USD",
               posted_date=ctx.now()[:10], posted_at=ctx.now(), passenger_sequence=1,
               segment_sequence=0, bag_sequence=0, payment_channel="call_centre",
               source_event_id="", credit_voucher_code=code,
               credit_expires_on=str(voucher_expires_on), schedule_change_minutes=0,
               notice_reference="", reason_code="routine_booking")
    rows = ctx.find("air_bookings", air_booking_id=air_booking_id)
    if rows:
        ctx.update("air_bookings", air_booking_id,
                   credit_balance_usd=round(float(rows[0].get("credit_balance_usd") or 0) + value, 2))
    return (f"Voucher {code} issued on line {rid} against booking {air_booking_id}: "
            f"{value:.2f} USD, redeemable up to and including {voucher_expires_on}.")


@tool(owner="user", rw="write")
def apply_travel_credit_e74c9b2a(ctx: ToolContext, air_booking_id: str, customer_id: str,
                                 credit_voucher_code: str, credit_applied_usd: float,
                                 source_event_id: str) -> str:
    """Spend a travel credit voucher standing in the traveller's own name against the price of an
    itinerary they are holding. The traveller makes this call themselves, since the voucher is
    their property. One call posts a single redemption line carrying the voucher code and the
    stated sum to the itinerary being paid for, and takes the same sum off the open travel credit
    of the booking the voucher was raised on. The traveller sees the redemption line on the
    itinerary and a smaller open credit on the old booking; the call comes back with the reference
    of the redemption line.

    Args:
        air_booking_id: Id class — the internal reference number of the air booking the voucher is
            spent on, read from the traveller's booking record returned by the booking lookup.
        customer_id: Id class — the traveller reference number the redemption is recorded against,
            read from the traveller profile returned by the profile lookup.
        credit_voucher_code: Verbatim class — the voucher code as it is quoted on the credit the
            traveller holds, as the booking's credit lines record it, copied character for
            character, keeping its wording, digits and punctuation, with no translation,
            normalisation, summarisation, addition or deletion (verbatim).
        credit_applied_usd: Fixed-format class — the sum taken off the voucher, in USD with exactly
            2 decimal places, stated as a positive number and rounded to the nearest
            cent at the moment it is passed; there is no empty value and no other currency.
        source_event_id: Id class — the reference number of the credit-issue line that carries this
            voucher, read from that line on the booking's ledger.

    Returns:
        A plain-language confirmation line naming the reference of the redemption line that was
        posted, the voucher code it was taken from, the sum applied in USD to two decimal places,
        and the open travel credit left on the booking the voucher was raised on. The presence of
        that line reference is what indicates the value moved onto the itinerary; nothing is
        returned when no redemption line is posted.
    """
    applied = round(float(credit_applied_usd), 2)
    rid = ctx.make_id("aev_", air_booking_id, customer_id, applied, str(credit_voucher_code))
    ctx.create("air_booking_events", rid, air_event_id=rid, air_booking_id=air_booking_id,
               customer_id=customer_id, event_type="air_credit_redeem",
               charge_category="credit_redemption", amount_usd=-applied, currency_charged="USD",
               posted_date=ctx.now()[:10], posted_at=ctx.now(), passenger_sequence=1,
               segment_sequence=0, bag_sequence=0, payment_channel="call_centre",
               source_event_id=str(source_event_id), credit_voucher_code=str(credit_voucher_code),
               credit_expires_on="", schedule_change_minutes=0, notice_reference="",
               reason_code="routine_booking")
    source = ctx.find("air_booking_events", air_event_id=str(source_event_id))
    left = applied
    if source:
        held = ctx.find("air_bookings", air_booking_id=source[0].get("air_booking_id"))
        if held:
            left = round(float(held[0].get("credit_balance_usd") or 0) - applied, 2)
            ctx.update("air_bookings", source[0].get("air_booking_id"), credit_balance_usd=left)
    return (f"Redemption line {rid} posted to booking {air_booking_id}: {applied:.2f} USD taken "
            f"from voucher {credit_voucher_code}. Open travel credit on the originating booking "
            f"is now {left:.2f} USD.")


@tool(owner="user", rw="write")
def settle_agency_service_charge_b626effa(ctx: ToolContext, air_booking_id: str, customer_id: str,
                                          service_charge_usd: float) -> str:
    """Settle the agency service charge standing against an air booking from the traveller's own card.
    The traveller makes this call themselves, since it is their card that is presented. One call posts a
    single agency service line for the stated sum to that booking's ledger and raises the booking's net
    paid total by the same sum, so the booking's travellers are all covered for the service charge. The
    traveller sees the service line and the new net paid total on the booking, and the call comes back
    with the reference of the line that was posted.

    Args:
        air_booking_id: Id class — the internal reference number of the air booking the service charge is
            settled against, read from the traveller's booking record returned by the booking lookup.
        customer_id: Id class — the traveller reference number the service line is recorded against, read
            from the traveller profile returned by the profile lookup.
        service_charge_usd: Fixed-format class — the sum settled, in USD with exactly 2 decimal places,
            stated as a positive number and rounded to the nearest cent at the moment it is
            passed; there is no empty value and no other currency.

    Returns:
        A plain-language confirmation line naming the reference of the service line that was posted, the
        sum settled in USD to two decimal places, and the booking's net paid total once the line landed.
        The presence of that line reference is what indicates the charge is settled; nothing is returned
        when no line is posted.
    """
    amount = round(float(service_charge_usd), 2)
    rid = ctx.make_id("aev_", air_booking_id, customer_id, amount, "agency_service_fee")
    ctx.create("air_booking_events", rid, air_event_id=rid, air_booking_id=air_booking_id,
               customer_id=customer_id, event_type="air_fare_charge",
               charge_category="agency_service_fee", amount_usd=amount, currency_charged="USD",
               posted_date=ctx.now()[:10], posted_at=ctx.now(), passenger_sequence=1,
               segment_sequence=0, bag_sequence=0, payment_channel="call_centre",
               source_event_id="", credit_voucher_code="", credit_expires_on="",
               schedule_change_minutes=0, notice_reference="", reason_code="routine_booking")
    rows = ctx.find("air_bookings", air_booking_id=air_booking_id)
    total = round(float(rows[0].get("amount_paid_usd") or 0) + amount, 2) if rows else amount
    if rows:
        ctx.update("air_bookings", air_booking_id, amount_paid_usd=total)
    return (f"Service line {rid} posted to booking {air_booking_id}: {amount:.2f} USD settled. "
            f"Net paid on the booking is now {total:.2f} USD.")


@tool(owner="agent", rw="write")
def charge_cabin_upgrade_d9ccb8ec(ctx: ToolContext, air_booking_id: str, customer_id: str,
                                  upgrade_copay_usd: float) -> str:
    """Sell the travellers on an air booking a move into a higher cabin. One call posts a single
    optional-extra line for the stated co-payment to that booking's ledger, marks it as the seating line
    the move is sold under, dates it on today's business date and raises the booking's net paid total by
    the same sum; the cabin the booking is held in is left as it stands, because the move is sold as
    an extra rather than as a change of fare brand. The traveller sees the upgrade line and the new net
    paid total on the booking, and the call comes back with the reference of the line that was posted.

    Args:
        air_booking_id: Id class — the internal reference number of the air booking the move is sold on,
            read from the traveller's booking record returned by the booking lookup.
        customer_id: Id class — the traveller reference number the upgrade line is recorded against, read
            from the traveller profile returned by the profile lookup.
        upgrade_copay_usd: Fixed-format class — the co-payment collected for the move, in USD with
            exactly 2 decimal places, stated as a positive number and rounded to the nearest
            cent at the moment it is passed; there is no empty value and no other currency.

    Returns:
        A plain-language confirmation line naming the reference of the upgrade line that was posted, the
        co-payment collected in USD to two decimal places, and the booking's net paid total once the line
        landed. The presence of that line reference is what indicates the move was sold; nothing is
        returned when no line is posted.
    """
    amount = round(float(upgrade_copay_usd), 2)
    rid = ctx.make_id("aev_", air_booking_id, customer_id, amount, "cabin_upgrade")
    ctx.create("air_booking_events", rid, air_event_id=rid, air_booking_id=air_booking_id,
               customer_id=customer_id, event_type="air_ancillary_charge",
               charge_category="seat_assignment", amount_usd=amount, currency_charged="USD",
               posted_date=ctx.now()[:10], posted_at=ctx.now(), passenger_sequence=1,
               segment_sequence=0, bag_sequence=0, payment_channel="call_centre",
               source_event_id="", credit_voucher_code="", credit_expires_on="",
               schedule_change_minutes=0, notice_reference="", reason_code="routine_booking")
    rows = ctx.find("air_bookings", air_booking_id=air_booking_id)
    total = round(float(rows[0].get("amount_paid_usd") or 0) + amount, 2) if rows else amount
    if rows:
        ctx.update("air_bookings", air_booking_id, amount_paid_usd=total)
    return (f"Upgrade line {rid} posted to booking {air_booking_id}: {amount:.2f} USD collected as the "
            f"cabin co-payment. Net paid on the booking is now {total:.2f} USD.")

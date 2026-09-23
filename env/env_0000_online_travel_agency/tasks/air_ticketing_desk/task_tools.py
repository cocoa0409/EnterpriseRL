"""Hidden task tools for the air_ticketing_desk difficulty of the Wanderlane Travel Group scenario.

Each function below performs exactly one atomic write against the air booking records. None of them
aggregates history, prices anything, or judges whether a business condition holds: the agent works
the figure out from the published terms and the records, then passes it in.
"""

from erlbench import ToolContext, tool


@tool(owner="agent", rw="write")
def withhold_cancellation_penalty_77ca3b84(ctx: ToolContext, air_booking_id: str,
                                           source_event_id: str, passenger_sequence: int,
                                           penalty_amount_usd: float) -> str:
    """Withhold a cancellation penalty on an air booking the traveller has given up. One call posts a
    single penalty line to that booking's money ledger: the amount named is held back from the
    traveller and the line is filed against the original fare line it is withheld from, so the
    booking's paid balance afterwards shows the penalty standing on it. The traveller sees the
    penalty as a separate withheld line on the booking alongside the fares and taxes already posted,
    quoted under its own line reference. The call has completed when the confirmation naming that
    new line reference and the amount withheld comes back.

    Args:
        air_booking_id: Id class — the reference number of the air booking record the penalty is
            withheld on, as returned by the air booking lookup for this traveller.
        source_event_id: Id class — the reference number of the money line on the same booking that
            the penalty is withheld against, as returned by the air booking event lookup.
        passenger_sequence: Fixed-format class — which traveller on the booking the penalty belongs
            to, in ticket order, written as a whole number starting at 1; there is no empty value
            and no rounding, since the position is counted exactly.
        penalty_amount_usd: Fixed-format class — the amount held back from the traveller, as a
            positive USD amount with 2 decimal places, given to the cent exactly as the published terms produce it; US dollars only, and there is no empty value.

    Returns:
        A confirmation sentence in plain text. It names the new penalty line's reference (a string
        beginning "apen_"), the air booking reference the line was posted to, and the amount
        withheld in US dollars to two decimal places. Receiving that sentence means the penalty line
        now stands on the booking.
    """
    rid = ctx.make_id("apen_", air_booking_id, source_event_id, passenger_sequence,
                      penalty_amount_usd)
    owner = ctx.find("air_bookings", air_booking_id=air_booking_id)
    customer_id = owner[0]["customer_id"] if owner else ""
    amount = round(float(penalty_amount_usd), 2)
    ctx.create("air_booking_events", rid, air_event_id=rid, air_booking_id=air_booking_id,
               customer_id=customer_id, event_type="air_penalty_charge",
               charge_category="cancellation_penalty", amount_usd=amount,
               currency_charged="USD", posted_date=ctx.now()[:10], posted_at=ctx.now(),
               passenger_sequence=int(passenger_sequence), segment_sequence=0, bag_sequence=0,
               payment_channel="call_centre", source_event_id=source_event_id,
               credit_voucher_code="", credit_expires_on="", schedule_change_minutes=0,
               notice_reference="", reason_code="voluntary_change")
    return (f"Cancellation penalty line {rid} posted to air booking {air_booking_id}; "
            f"{amount:.2f} USD withheld.")


@tool(owner="agent", rw="write")
def return_airline_refunded_taxes_4767edfd(ctx: ToolContext, air_booking_id: str,
                                           source_event_id: str, passenger_sequence: int,
                                           tax_return_amount_usd: float) -> str:
    """Return to the traveller's original form of payment the taxes and carrier fees the airline
    gives back on an air booking that has been given up. One call posts a single payout line to that
    booking's money ledger, filed against the tax line it reverses, and the money leaves the
    booking's paid balance, which falls by the amount returned. The traveller sees the money back on
    the card the booking was paid with and a payout line standing on the booking under its own line
    reference. The call has completed when the confirmation naming that new line reference and the
    amount returned comes back.

    Args:
        air_booking_id: Id class — the reference number of the air booking record the payout is
            raised on, as returned by the air booking lookup for this traveller.
        source_event_id: Id class — the reference number of the tax line on the same booking that
            the payout is raised against, as returned by the air booking event lookup.
        passenger_sequence: Fixed-format class — which traveller on the booking the payout belongs
            to, in ticket order, written as a whole number starting at 1; there is no empty value
            and no rounding, since the position is counted exactly.
        tax_return_amount_usd: Fixed-format class — how much goes back to the card, given as a
            positive USD amount with 2 decimal places, given to the cent exactly as the published terms produce it; the line itself is filed as money leaving the booking. US dollars
            only, and there is no empty value.

    Returns:
        A confirmation sentence in plain text. It names the new payout line's reference (a string
        beginning "apay_"), the air booking reference the line was posted to, and the amount
        returned in US dollars to two decimal places. Receiving that sentence means the money has
        been returned and the payout line stands on the booking.
    """
    rid = ctx.make_id("apay_", air_booking_id, source_event_id, passenger_sequence,
                      tax_return_amount_usd)
    owner = ctx.find("air_bookings", air_booking_id=air_booking_id)
    customer_id = owner[0]["customer_id"] if owner else ""
    amount = round(float(tax_return_amount_usd), 2)
    ctx.create("air_booking_events", rid, air_event_id=rid, air_booking_id=air_booking_id,
               customer_id=customer_id, event_type="air_refund_payout",
               charge_category="refund_payout", amount_usd=-amount,
               currency_charged="USD", posted_date=ctx.now()[:10], posted_at=ctx.now(),
               passenger_sequence=int(passenger_sequence), segment_sequence=0, bag_sequence=0,
               payment_channel="call_centre", source_event_id=source_event_id,
               credit_voucher_code="", credit_expires_on="", schedule_change_minutes=0,
               notice_reference="", reason_code="routine_booking")
    return (f"Tax payout line {rid} posted to air booking {air_booking_id}; "
            f"{amount:.2f} USD returned to the original form of payment.")


@tool(owner="agent", rw="write")
def issue_travel_credit_voucher_dd7ecc26(ctx: ToolContext, air_booking_id: str,
                                         source_event_id: str, passenger_sequence: int,
                                         credit_expires_on: str,
                                         voucher_value_usd: float) -> str:
    """Issue a travel credit voucher in the traveller's name against an air booking they have given
    up. One call mints one voucher and posts the matching issue line to that booking's credit
    ledger, so the booking afterwards carries an open travel credit of the value named, redeemable
    until the last date given. The traveller sees a voucher code they can quote and the value
    standing open against the booking. The call has completed when the confirmation naming the
    voucher code, the line reference and the value comes back.

    Args:
        air_booking_id: Id class — the reference number of the air booking record whose ticket
            produced the voucher, as returned by the air booking lookup for this traveller.
        source_event_id: Id class — the reference number of the original fare line on the same
            booking whose value the voucher replaces, as returned by the air booking event lookup.
        passenger_sequence: Fixed-format class — which traveller on the booking the voucher is
            issued for, in ticket order, written as a whole number starting at 1; there is no empty
            value and no rounding, since the position is counted exactly.
        credit_expires_on: Fixed-format class — the last date the voucher may be redeemed, written
            as a calendar date YYYY-MM-DD in the traveller's own local calendar, with no time part;
            there is no empty value, because every voucher carries a last date.
        voucher_value_usd: Fixed-format class — the value placed on the voucher, as a positive USD
            amount with 2 decimal places, given to the cent exactly as the published terms produce it; US dollars only, and there is no empty value.

    Returns:
        A confirmation sentence in plain text. It names the voucher code minted (a string beginning
        "WLTC"), the new issue line's reference (a string beginning "acrd_"), the air booking
        reference the line was posted to, the value placed on the voucher in US dollars to two
        decimal places, and the last date it may be redeemed. Receiving that sentence means the
        voucher now stands open in the traveller's name.
    """
    rid = ctx.make_id("acrd_", air_booking_id, source_event_id, passenger_sequence,
                      voucher_value_usd)
    code = "WLTC" + ctx.make_id("", air_booking_id, voucher_value_usd, length=8).upper()
    owner = ctx.find("air_bookings", air_booking_id=air_booking_id)
    customer_id = owner[0]["customer_id"] if owner else ""
    amount = round(float(voucher_value_usd), 2)
    ctx.create("air_booking_events", rid, air_event_id=rid, air_booking_id=air_booking_id,
               customer_id=customer_id, event_type="air_credit_issue",
               charge_category="credit_issue", amount_usd=amount,
               currency_charged="USD", posted_date=ctx.now()[:10], posted_at=ctx.now(),
               passenger_sequence=int(passenger_sequence), segment_sequence=0, bag_sequence=0,
               payment_channel="call_centre", source_event_id=source_event_id,
               credit_voucher_code=code, credit_expires_on=credit_expires_on,
               schedule_change_minutes=0, notice_reference="", reason_code="routine_booking")
    return (f"Travel credit voucher {code} issued on line {rid} against air booking "
            f"{air_booking_id}; {amount:.2f} USD open until {credit_expires_on}.")


@tool(owner="user", rw="write")
def release_travel_credit_value_2b680572(ctx: ToolContext, air_booking_id: str,
                                         credit_voucher_code: str, source_event_id: str,
                                         passenger_sequence: int,
                                         released_credit_usd: float) -> str:
    """Release value from a travel credit voucher standing in the traveller's own name and put it
    against an air booking they are holding. The traveller does this themselves. One call posts a
    single redemption line to the holding booking's credit ledger, the value named comes off the
    voucher, and the booking afterwards carries that much credit toward its price. The traveller
    sees the voucher balance reduced and the credit standing against the booking they are holding.
    The call has completed when the confirmation naming the new line reference and the value
    released comes back.

    Args:
        air_booking_id: Id class — the reference number of the air booking record the value is put
            against, as returned by the air booking lookup for this traveller.
        credit_voucher_code: Verbatim class — the voucher code as it was given when the travel
            credit was issued, copied character for character with the same letters, digits and
            punctuation, with no translation, normalisation, summarisation, addition or deletion
            (verbatim).
        source_event_id: Id class — the reference number of the issue line that created the
            voucher, as returned by the air booking event lookup.
        passenger_sequence: Fixed-format class — which traveller on the holding booking the released
            value belongs to, in ticket order, written as a whole number starting at 1; there is no
            empty value and no rounding, since the position is counted exactly.
        released_credit_usd: Fixed-format class — how much value comes off the voucher, as a
            positive USD amount with 2 decimal places, given to the cent exactly as the published terms produce it; the line itself is filed as value leaving the voucher. US dollars
            only, and there is no empty value.

    Returns:
        A confirmation sentence in plain text. It names the new redemption line's reference (a
        string beginning "ared_"), the voucher code the value came off, the air booking reference
        the value was put against, and the amount released in US dollars to two decimal places.
        Receiving that sentence means the value now stands against that booking.
    """
    rid = ctx.make_id("ared_", air_booking_id, credit_voucher_code, passenger_sequence,
                      released_credit_usd)
    owner = ctx.find("air_bookings", air_booking_id=air_booking_id)
    customer_id = owner[0]["customer_id"] if owner else ""
    amount = round(float(released_credit_usd), 2)
    ctx.create("air_booking_events", rid, air_event_id=rid, air_booking_id=air_booking_id,
               customer_id=customer_id, event_type="air_credit_redeem",
               charge_category="credit_redemption", amount_usd=-amount,
               currency_charged="USD", posted_date=ctx.now()[:10], posted_at=ctx.now(),
               passenger_sequence=int(passenger_sequence), segment_sequence=0, bag_sequence=0,
               payment_channel="call_centre", source_event_id=source_event_id,
               credit_voucher_code=credit_voucher_code, credit_expires_on="",
               schedule_change_minutes=0, notice_reference="", reason_code="routine_booking")
    return (f"Redemption line {rid} posted from voucher {credit_voucher_code} to air booking "
            f"{air_booking_id}; {amount:.2f} USD released.")


@tool(owner="agent", rw="write")
def charge_credit_reissue_fee_efe635ea(ctx: ToolContext, air_booking_id: str, source_event_id: str,
                                       passenger_sequence: int, reissue_fee_usd: float) -> str:
    """Charge the traveller the fee for putting a lapsed travel credit from an air booking back into
    use. One call posts a single fee line to that booking's money ledger, filed against the credit
    line whose value is being put back into use, and the booking's paid balance rises by the amount
    charged. The traveller sees a separate fee line standing on the
    booking under its own line reference, met out of the travel credit being put back into use. The call has completed when the
    confirmation naming that new line reference and the amount charged comes back.

    Args:
        air_booking_id: Id class — the reference number of the air booking record the fee is charged
            on, as returned by the air booking lookup for this traveller.
        source_event_id: Id class — the reference number of the travel credit line on the same
            booking whose value is being put back into use, as returned by the air booking event
            lookup.
        passenger_sequence: Fixed-format class — which traveller on the booking the fee belongs to,
            in ticket order, written as a whole number starting at 1; there is no empty value and no
            rounding, since the position is counted exactly.
        reissue_fee_usd: Fixed-format class — the amount charged to the traveller, as a positive USD
            amount with 2 decimal places, given to the cent exactly as the published terms produce it; US dollars only, and there is no empty value.

    Returns:
        A confirmation sentence in plain text. It names the new fee line's reference (a string
        beginning "arif_"), the air booking reference the line was posted to, and the amount charged
        in US dollars to two decimal places. Receiving that sentence means the fee line now stands
        charged on the booking.
    """
    rid = ctx.make_id("arif_", air_booking_id, source_event_id, passenger_sequence, reissue_fee_usd)
    owner = ctx.find("air_bookings", air_booking_id=air_booking_id)
    customer_id = owner[0]["customer_id"] if owner else ""
    amount = round(float(reissue_fee_usd), 2)
    ctx.create("air_booking_events", rid, air_event_id=rid, air_booking_id=air_booking_id,
               customer_id=customer_id, event_type="air_fare_charge",
               charge_category="credit_reissue_fee", amount_usd=amount,
               currency_charged="USD", posted_date=ctx.now()[:10], posted_at=ctx.now(),
               passenger_sequence=int(passenger_sequence), segment_sequence=0, bag_sequence=0,
               payment_channel="call_centre", source_event_id=source_event_id,
               credit_voucher_code="", credit_expires_on="", schedule_change_minutes=0,
               notice_reference="", reason_code="routine_booking")
    return (f"Credit reissue fee line {rid} posted to air booking {air_booking_id}; "
            f"{amount:.2f} USD charged.")


@tool(owner="user", rw="write")
def reissue_lapsed_travel_credit_f544c035(ctx: ToolContext, air_booking_id: str,
                                          source_event_id: str, passenger_sequence: int,
                                          credit_expires_on: str,
                                          carried_value_usd: float) -> str:
    """Carry the value of a lapsed travel credit onto a fresh voucher in the traveller's own name.
    The traveller does this themselves, because it spends their one chance to put that value back
    into use. One call mints one fresh voucher and posts the matching issue line to the booking's
    credit ledger, so the booking afterwards carries an open travel credit of the value named,
    redeemable until the last date given, while the lapsed lines stay on the record as they were.
    The traveller sees a new voucher code they can quote and the value standing open again. The call
    has completed when the confirmation naming the fresh voucher code, the line reference and the
    value comes back.

    Args:
        air_booking_id: Id class — the reference number of the air booking record whose lapsed
            travel credit is being carried forward, as returned by the air booking lookup for this
            traveller.
        source_event_id: Id class — the reference number of the lapsed travel credit line on the
            same booking whose value is carried onto the fresh voucher, as returned by the air
            booking event lookup.
        passenger_sequence: Fixed-format class — which traveller on the booking the fresh voucher is
            issued for, in ticket order, written as a whole number starting at 1; there is no empty
            value and no rounding, since the position is counted exactly.
        credit_expires_on: Fixed-format class — the last date the fresh voucher may be redeemed,
            written as a calendar date YYYY-MM-DD in the traveller's own local calendar, with no
            time part; there is no empty value, because every voucher carries a last date.
        carried_value_usd: Fixed-format class — the value placed on the fresh voucher, as a positive
            USD amount with 2 decimal places, given to the cent exactly as the published terms produce it; US dollars only, and there is no empty value.

    Returns:
        A confirmation sentence in plain text. It names the fresh voucher code minted (a string
        beginning "WLTR"), the new issue line's reference (a string beginning "arew_"), the air
        booking reference the line was posted to, the value placed on the fresh voucher in US
        dollars to two decimal places, and the last date it may be redeemed. Receiving that sentence
        means the fresh voucher now stands open in the traveller's name.
    """
    rid = ctx.make_id("arew_", air_booking_id, source_event_id, passenger_sequence,
                      carried_value_usd)
    code = "WLTR" + ctx.make_id("", air_booking_id, carried_value_usd, length=8).upper()
    owner = ctx.find("air_bookings", air_booking_id=air_booking_id)
    customer_id = owner[0]["customer_id"] if owner else ""
    amount = round(float(carried_value_usd), 2)
    ctx.create("air_booking_events", rid, air_event_id=rid, air_booking_id=air_booking_id,
               customer_id=customer_id, event_type="air_credit_issue",
               charge_category="credit_issue", amount_usd=amount,
               currency_charged="USD", posted_date=ctx.now()[:10], posted_at=ctx.now(),
               passenger_sequence=int(passenger_sequence), segment_sequence=0, bag_sequence=0,
               payment_channel="call_centre", source_event_id=source_event_id,
               credit_voucher_code=code, credit_expires_on=credit_expires_on,
               schedule_change_minutes=0, notice_reference="", reason_code="routine_booking")
    return (f"Fresh travel credit voucher {code} issued on line {rid} against air booking "
            f"{air_booking_id}; {amount:.2f} USD open until {credit_expires_on}.")

"""Hidden task tools of the listing_settings_and_compliance difficulty (Roamhaven Listings).

Every tool here saves one numeric setting on one listing and, when the saved value differs from the one
the listing carried, logs that change as one fee-change record (the listing_fee_change_logged event the
listing_pricing_updated event triggers under the Listings charter). A tool never works out the value it
saves, never checks whether the value is allowed and never refuses: the value is decided by the Listings
policies and passed in by whoever performs the save.
"""

from erlbench import ToolContext, tool


@tool(owner="agent", rw="write")
def reset_pet_fee_f8e15273(ctx: ToolContext, listing_id: str, pet_fee: float) -> str:
    """Support resets the per-stay pet fee of one host listing to the amount given and logs the change.

    The listing's pet fee is overwritten with the amount passed in; from then on it is the pet fee new
    bookings of that listing are priced with, while stays already booked keep the pet fee frozen on them.
    When the amount differs from the pet fee the listing carried at the moment of the call, one fee-change
    record is added to the listing's history carrying the old and the new amount and today's date; an
    amount equal to the one already carried changes nothing and logs nothing. The host sees the new pet fee
    on the listing and the change in its history. The call has completed when the receipt comes back with
    the listing reference number and the new amount.

    Args:
        listing_id: Id class — the reference number of the host listing whose pet fee is reset, as returned
            by the listing lookup for the verified host.
        pet_fee: Fixed-format class — the pet fee charged once per stay with pets, as a USD amount, 2 decimal
            places, rounded half up to the cent before saving; 0.00 means pets are not charged.

    Returns:
        A dictionary receipt: listing_id (string, the listing reference number), setting (string, always
        pet_fee), previous_amount (number, USD to 2 decimal places, the pet fee the listing carried when the
        call was made), new_amount (number, USD to 2 decimal places, the pet fee now saved), change_logged
        (boolean, true when a fee-change record was added), change_record_id (string, the reference number of
        that record, empty when nothing was logged) and saved_on (string, YYYY-MM-DD, the date of the save).
        A receipt carrying the new amount means the reset is in force.
    """
    value = round(float(pet_fee), 2)
    rows = ctx.find("listings", listing_id=listing_id)
    listing = rows[0] if rows else {}
    carried = listing.get("pet_fee")
    carried = round(float(carried), 2) if carried not in (None, "") else 0.0
    ctx.update("listings", listing_id, pet_fee=value)
    day = ctx.now()[:10]
    record_id = ""
    if round(float(value), 2) != carried:
        record_id = ctx.make_id("lfc_", listing_id, "pet_fee", value, day)
        ctx.create("listing_events", record_id, listing_event_id=record_id, listing_id=listing_id,
                   customer_id=listing.get("customer_id", ""), event_type="listing_fee_change_logged",
                   event_date=day, fee_type="pet_fee", previous_amount=carried,
                   new_amount=round(float(value), 2), block_start_date="", block_end_date="",
                   block_reason="none", assessment_quarter="", average_rating=0.0, review_count=0,
                   quality_outcome="none", notice_type="none", notice_reference="", cure_deadline="")
    return str({"listing_id": listing_id, "setting": "pet_fee", "previous_amount": carried,
                "new_amount": round(float(value), 2), "change_logged": bool(record_id),
                "change_record_id": record_id, "saved_on": day})


@tool(owner="agent", rw="write")
def reset_cleaning_fee_77ae9a3d(ctx: ToolContext, listing_id: str, cleaning_fee: float) -> str:
    """Support resets the regular per-stay cleaning fee of one host listing to the amount given and logs it.

    The listing's regular cleaning fee is overwritten with the amount passed in; from then on it is the
    cleaning fee new bookings of that listing are priced with (stays already booked keep the cleaning fee
    frozen on them), and the short-stay cleaning fee of the listing is left as it stands. When the amount
    differs from the cleaning fee the listing carried at the moment of the call, one fee-change record is
    added to the listing's history with the old and the new amount and today's date; an unchanged amount
    logs nothing. The host sees the new cleaning fee on the listing. The call has completed when the
    receipt comes back with the listing reference number and the new amount.

    Args:
        listing_id: Id class — the reference number of the host listing whose regular cleaning fee is reset,
            as returned by the listing lookup for the verified host.
        cleaning_fee: Fixed-format class — the regular cleaning fee charged once per stay, as a USD amount,
            2 decimal places, rounded half up to the cent before saving.

    Returns:
        A dictionary receipt: listing_id (string, the listing reference number), setting (string, always
        cleaning_fee), previous_amount (number, USD to 2 decimal places, the cleaning fee the listing carried
        when the call was made), new_amount (number, USD to 2 decimal places, the cleaning fee now saved),
        change_logged (boolean, true when a fee-change record was added), change_record_id (string, the
        reference number of that record, empty when nothing was logged) and saved_on (string, YYYY-MM-DD,
        the date of the save). A receipt carrying the new amount means the reset is in force.
    """
    value = round(float(cleaning_fee), 2)
    rows = ctx.find("listings", listing_id=listing_id)
    listing = rows[0] if rows else {}
    carried = listing.get("cleaning_fee")
    carried = round(float(carried), 2) if carried not in (None, "") else 0.0
    ctx.update("listings", listing_id, cleaning_fee=value)
    day = ctx.now()[:10]
    record_id = ""
    if round(float(value), 2) != carried:
        record_id = ctx.make_id("lfc_", listing_id, "cleaning_fee", value, day)
        ctx.create("listing_events", record_id, listing_event_id=record_id, listing_id=listing_id,
                   customer_id=listing.get("customer_id", ""), event_type="listing_fee_change_logged",
                   event_date=day, fee_type="cleaning_fee", previous_amount=carried,
                   new_amount=round(float(value), 2), block_start_date="", block_end_date="",
                   block_reason="none", assessment_quarter="", average_rating=0.0, review_count=0,
                   quality_outcome="none", notice_type="none", notice_reference="", cure_deadline="")
    return str({"listing_id": listing_id, "setting": "cleaning_fee", "previous_amount": carried,
                "new_amount": round(float(value), 2), "change_logged": bool(record_id),
                "change_record_id": record_id, "saved_on": day})


@tool(owner="user", rw="write")
def save_short_stay_cleaning_fee_f18844b5(ctx: ToolContext, listing_id: str,
                                          short_stay_cleaning_fee: float) -> str:
    """The host saves, from their own listing editor, the short-stay cleaning fee of one of their listings.

    The listing's short-stay cleaning fee is overwritten with the amount the host enters; from then on new
    bookings of that listing short enough to qualify are charged it in place of the regular cleaning fee,
    while stays already booked keep the cleaning fee frozen on them. When the amount differs from the
    short-stay cleaning fee the listing carried at the moment of the save, one fee-change record is added to
    the listing's history with the old and the new amount and today's date; an unchanged amount logs
    nothing. The host sees the short-stay cleaning fee on the listing as soon as the receipt comes back with
    the listing reference number and the saved amount.

    Args:
        listing_id: Id class — the reference number of the host's own listing whose short-stay cleaning fee
            is saved, as read out to the host by support from the listing lookup.
        short_stay_cleaning_fee: Fixed-format class — the cleaning fee charged once per short stay, as a USD
            amount, 2 decimal places, rounded half up to the cent before saving; 0.00 means no short-stay
            cleaning fee is set.

    Returns:
        A dictionary receipt: listing_id (string, the listing reference number), setting (string, always
        short_stay_cleaning_fee), previous_amount (number, USD to 2 decimal places, the short-stay cleaning
        fee the listing carried when the host saved), new_amount (number, USD to 2 decimal places, the
        short-stay cleaning fee now saved), change_logged (boolean, true when a fee-change record was added),
        change_record_id (string, the reference number of that record, empty when nothing was logged) and
        saved_on (string, YYYY-MM-DD, the date of the save). A receipt carrying the new amount means the fee
        is in force.
    """
    value = round(float(short_stay_cleaning_fee), 2)
    rows = ctx.find("listings", listing_id=listing_id)
    listing = rows[0] if rows else {}
    carried = listing.get("short_stay_cleaning_fee")
    carried = round(float(carried), 2) if carried not in (None, "") else 0.0
    ctx.update("listings", listing_id, short_stay_cleaning_fee=value)
    day = ctx.now()[:10]
    record_id = ""
    if round(float(value), 2) != carried:
        record_id = ctx.make_id("lfc_", listing_id, "short_stay_cleaning_fee", value, day)
        ctx.create("listing_events", record_id, listing_event_id=record_id, listing_id=listing_id,
                   customer_id=listing.get("customer_id", ""), event_type="listing_fee_change_logged",
                   event_date=day, fee_type="short_stay_cleaning_fee", previous_amount=carried,
                   new_amount=round(float(value), 2), block_start_date="", block_end_date="",
                   block_reason="none", assessment_quarter="", average_rating=0.0, review_count=0,
                   quality_outcome="none", notice_type="none", notice_reference="", cure_deadline="")
    return str({"listing_id": listing_id, "setting": "short_stay_cleaning_fee", "previous_amount": carried,
                "new_amount": round(float(value), 2), "change_logged": bool(record_id),
                "change_record_id": record_id, "saved_on": day})


@tool(owner="agent", rw="write")
def raise_minimum_stay_1aeaa300(ctx: ToolContext, listing_id: str, minimum_nights: int) -> str:
    """Support sets the minimum stay of one host listing to the number of nights given and logs the change.

    The listing's minimum stay is overwritten with the number of nights passed in; from then on new bookings
    of that listing must be at least that long, while stays already booked are not touched. When the number
    differs from the minimum stay the listing carried at the moment of the call, one change record is added to
    the listing's history carrying the old and the new number of nights and today's date; an unchanged number
    logs nothing. The host sees the new minimum stay on the listing. The call has completed when the receipt
    comes back with the listing reference number and the new number of nights.

    Args:
        listing_id: Id class — the reference number of the host listing whose minimum stay is set, as returned
            by the listing lookup for the verified host.
        minimum_nights: Fixed-format class — the shortest stay new bookings may have, in nights, written as a
            non-negative integer (whole nights, no fractions).

    Returns:
        A dictionary receipt: listing_id (string, the listing reference number), setting (string, always
        minimum_nights), previous_amount (number, nights to 2 decimal places, the minimum stay the listing
        carried when the call was made), new_amount (number, nights to 2 decimal places, the minimum stay now
        saved), change_logged (boolean, true when a change record was added), change_record_id (string, the
        reference number of that record, empty when nothing was logged) and saved_on (string, YYYY-MM-DD, the
        date of the save). A receipt carrying the new number of nights means the minimum stay is in force.
    """
    value = int(minimum_nights)
    rows = ctx.find("listings", listing_id=listing_id)
    listing = rows[0] if rows else {}
    carried = listing.get("minimum_nights")
    carried = round(float(carried), 2) if carried not in (None, "") else 0.0
    ctx.update("listings", listing_id, minimum_nights=value)
    day = ctx.now()[:10]
    record_id = ""
    if round(float(value), 2) != carried:
        record_id = ctx.make_id("lfc_", listing_id, "minimum_nights", value, day)
        ctx.create("listing_events", record_id, listing_event_id=record_id, listing_id=listing_id,
                   customer_id=listing.get("customer_id", ""), event_type="listing_fee_change_logged",
                   event_date=day, fee_type="minimum_nights", previous_amount=carried,
                   new_amount=round(float(value), 2), block_start_date="", block_end_date="",
                   block_reason="none", assessment_quarter="", average_rating=0.0, review_count=0,
                   quality_outcome="none", notice_type="none", notice_reference="", cure_deadline="")
    return str({"listing_id": listing_id, "setting": "minimum_nights", "previous_amount": carried,
                "new_amount": round(float(value), 2), "change_logged": bool(record_id),
                "change_record_id": record_id, "saved_on": day})


@tool(owner="agent", rw="write")
def reset_extra_guest_fee_9609655d(ctx: ToolContext, listing_id: str, extra_guest_fee: float) -> str:
    """Support resets the per-night extra-guest fee of one host listing to the amount given and logs it.

    The listing's extra-guest fee (charged per night for each guest beyond the listing's extra-guest
    threshold) is overwritten with the amount passed in; the threshold itself is left as it stands. From then
    on new bookings of that listing are priced with the new fee, while stays already booked keep the amounts
    frozen on them. When the amount differs from the extra-guest fee the listing carried at the moment of the
    call, one fee-change record is added to the listing's history with the old and the new amount and today's
    date; an unchanged amount logs nothing. The call has completed when the receipt comes back with the
    listing reference number and the new amount.

    Args:
        listing_id: Id class — the reference number of the host listing whose extra-guest fee is reset, as
            returned by the listing lookup for the verified host.
        extra_guest_fee: Fixed-format class — the fee per extra guest per night, as a USD amount, 2 decimal
            places, rounded half up to the cent before saving; 0.00 means extra guests are not charged.

    Returns:
        A dictionary receipt: listing_id (string, the listing reference number), setting (string, always
        extra_guest_fee), previous_amount (number, USD to 2 decimal places, the extra-guest fee the listing
        carried when the call was made), new_amount (number, USD to 2 decimal places, the extra-guest fee now
        saved), change_logged (boolean, true when a fee-change record was added), change_record_id (string, the
        reference number of that record, empty when nothing was logged) and saved_on (string, YYYY-MM-DD, the
        date of the save). A receipt carrying the new amount means the reset is in force.
    """
    value = round(float(extra_guest_fee), 2)
    rows = ctx.find("listings", listing_id=listing_id)
    listing = rows[0] if rows else {}
    carried = listing.get("extra_guest_fee")
    carried = round(float(carried), 2) if carried not in (None, "") else 0.0
    ctx.update("listings", listing_id, extra_guest_fee=value)
    day = ctx.now()[:10]
    record_id = ""
    if round(float(value), 2) != carried:
        record_id = ctx.make_id("lfc_", listing_id, "extra_guest_fee", value, day)
        ctx.create("listing_events", record_id, listing_event_id=record_id, listing_id=listing_id,
                   customer_id=listing.get("customer_id", ""), event_type="listing_fee_change_logged",
                   event_date=day, fee_type="extra_guest_fee", previous_amount=carried,
                   new_amount=round(float(value), 2), block_start_date="", block_end_date="",
                   block_reason="none", assessment_quarter="", average_rating=0.0, review_count=0,
                   quality_outcome="none", notice_type="none", notice_reference="", cure_deadline="")
    return str({"listing_id": listing_id, "setting": "extra_guest_fee", "previous_amount": carried,
                "new_amount": round(float(value), 2), "change_logged": bool(record_id),
                "change_record_id": record_id, "saved_on": day})


@tool(owner="user", rw="write")
def save_nightly_rate_d0fc8a90(ctx: ToolContext, listing_id: str, nightly_rate: float) -> str:
    """The host saves, from their own listing editor, the base nightly rate of one of their listings.

    The listing's nightly rate is overwritten with the amount the host enters; from then on it is the price
    per night new bookings of that listing are quoted from (discounts are still worked out on it), while
    stays already booked keep the nightly subtotal frozen on them. When the amount differs from the nightly
    rate the listing carried at the moment of the save, one change record is added to the listing's history
    with the old and the new rate and today's date; an unchanged amount logs nothing. The host sees the new
    rate on the listing as soon as the receipt comes back with the listing reference number and the amount.

    Args:
        listing_id: Id class — the reference number of the host's own listing whose nightly rate is saved, as
            read out to the host by support from the listing lookup.
        nightly_rate: Fixed-format class — the base price of one night, as a USD amount, 2 decimal places,
            rounded half up to the cent before saving.

    Returns:
        A dictionary receipt: listing_id (string, the listing reference number), setting (string, always
        nightly_rate), previous_amount (number, USD to 2 decimal places, the nightly rate the listing carried
        when the host saved), new_amount (number, USD to 2 decimal places, the nightly rate now saved),
        change_logged (boolean, true when a change record was added), change_record_id (string, the reference
        number of that record, empty when nothing was logged) and saved_on (string, YYYY-MM-DD, the date of the
        save). A receipt carrying the new amount means the rate is in force.
    """
    value = round(float(nightly_rate), 2)
    rows = ctx.find("listings", listing_id=listing_id)
    listing = rows[0] if rows else {}
    carried = listing.get("nightly_rate")
    carried = round(float(carried), 2) if carried not in (None, "") else 0.0
    ctx.update("listings", listing_id, nightly_rate=value)
    day = ctx.now()[:10]
    record_id = ""
    if round(float(value), 2) != carried:
        record_id = ctx.make_id("lfc_", listing_id, "nightly_rate", value, day)
        ctx.create("listing_events", record_id, listing_event_id=record_id, listing_id=listing_id,
                   customer_id=listing.get("customer_id", ""), event_type="listing_fee_change_logged",
                   event_date=day, fee_type="nightly_rate", previous_amount=carried,
                   new_amount=round(float(value), 2), block_start_date="", block_end_date="",
                   block_reason="none", assessment_quarter="", average_rating=0.0, review_count=0,
                   quality_outcome="none", notice_type="none", notice_reference="", cure_deadline="")
    return str({"listing_id": listing_id, "setting": "nightly_rate", "previous_amount": carried,
                "new_amount": round(float(value), 2), "change_logged": bool(record_id),
                "change_record_id": record_id, "saved_on": day})

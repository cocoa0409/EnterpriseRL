"""Hidden task tools of the booking_changes_desk difficulty (Aurelia Hanse Line, Container Bookings).

Each tool performs exactly one atomic write on a booking's charge account or booking record, with
the arguments the caller has already decided from the published rules and the records. No tool
checks eligibility, status, ownership, time limits, duplicates or any other business condition, and
none computes an amount: every value is passed in exactly as decided.
"""

from erlbench import ToolContext, tool


@tool(owner="agent", rw="write")
def charge_destination_change_fee_9814adc0(ctx: ToolContext, booking_id: str, vessel_voyage: str,
                                           fee_usd: float) -> str:
    """Charge one change-of-destination fee to a container booking's charge account for a change of port of discharge that is already on the booking.

    One call books one change-of-destination fee entry (tariff code pod_change_fee, amendment kind
    pod_change) on the booking's charge history, dated today, and raises the booking's outstanding
    charges by exactly the amount passed in. The booking's port of discharge, sailing, containers and
    status are not touched. Afterwards the new fee entry is visible in the booking's charge history
    and the booking shows the increased charges still outstanding. The call is complete when the
    receipt below is returned.
    The new entry also carries the booking's equipment type; it records no container count, because the
    amount passed in is already the whole amount of the entry.

    Args:
        booking_id: Id class — booking reference number of the booking being charged, as returned by the booking lookup for the verified customer.
        vessel_voyage: Verbatim class — the vessel and voyage shown on the change-of-destination amendment entry this fee charges, taken from the booking's charge history and copied character for character, preserving every letter, digit, space and punctuation mark, with no translation, normalisation, addition or deletion (verbatim).
        fee_usd: Fixed-format class — the change-of-destination fee to book, in USD as the money unit, a positive decimal amount with 2 decimal places; a value given with more digits is rounded half-to-even to 2 decimal places when booked.

    Returns:
        A text rendering of a dictionary describing the booked entry: booking_event_id (string, reference
        of the new fee entry in the charge history), booking_id (string, the booking charged),
        charge_code (string, always pod_change_fee), vessel_voyage (string, the sailing recorded on
        the entry), amount_usd (number, USD with 2 decimal places, the fee booked), event_date (string,
        YYYY-MM-DD, the booking date of the entry) and charges_due_usd (number, USD with 2 decimal
        places, the booking's outstanding charges after the fee). A returned booking_event_id means
        the fee is on the account.
    """
    amount = round(float(fee_usd), 2)
    today = ctx.now()[:10]
    rid = ctx.make_id("bkc_", booking_id, "pod_change_fee", vessel_voyage, amount, today)
    booking = ctx.find("bookings", booking_id=booking_id)
    customer_id = booking[0].get("customer_id", "") if booking else ""
    due = round((float(booking[0].get("charges_due_usd") or 0.0) if booking else 0.0) + amount, 2)
    ctx.create("booking_charges", rid, booking_event_id=rid, booking_id=booking_id,
               equipment_type=(booking[0].get("equipment_type", "") if booking else ""), customer_id=customer_id,
               event_type="booking_amendment_fee_charged", event_date=today, charge_code="pod_change_fee",
               amount_usd=round(float(fee_usd), 2), vessel_voyage=vessel_voyage, amendment_type="pod_change",
               roll_initiator="none", payment_reference="", reference_event_id="")
    ctx.update("bookings", booking_id, charges_due_usd=due)
    return str({"booking_event_id": rid, "booking_id": booking_id, "charge_code": "pod_change_fee",
                "vessel_voyage": vessel_voyage, "amount_usd": amount, "event_date": today,
                "charges_due_usd": due})


@tool(owner="agent", rw="write")
def charge_customer_roll_fee_5e1ab19d(ctx: ToolContext, booking_id: str, vessel_voyage: str,
                                      fee_usd: float) -> str:
    """Charge one customer roll fee to a container booking's charge account for a move to another sailing that the customer caused and that is already recorded on the booking.

    One call books one customer roll fee entry (tariff code customer_roll_fee, amendment kind
    customer_requested_vessel_change) on the booking's charge history, dated today, and raises the
    booking's outstanding charges by exactly the amount passed in. The booking's sailing, cut-offs,
    containers and status are not touched. Afterwards the new fee entry is visible in the booking's
    charge history and the booking shows the increased charges still outstanding. The call is
    complete when the receipt below is returned.
    The new entry also carries the booking's equipment type; it records no container count, because the
    amount passed in is already the whole amount of the entry.

    Args:
        booking_id: Id class — booking reference number of the booking being charged, as returned by the booking lookup for the verified customer.
        vessel_voyage: Verbatim class — the vessel and voyage the charged roll moved the booking off, as shown on that roll's entry in the booking's charge history, copied character for character, preserving every letter, digit, space and punctuation mark, with no translation, normalisation, addition or deletion (verbatim).
        fee_usd: Fixed-format class — the customer roll fee to book, in USD as the money unit, a positive decimal amount with 2 decimal places; a value given with more digits is rounded half-to-even to 2 decimal places when booked.

    Returns:
        A text rendering of a dictionary describing the booked entry: booking_event_id (string, reference
        of the new fee entry in the charge history), booking_id (string, the booking charged),
        charge_code (string, always customer_roll_fee), vessel_voyage (string, the sailing recorded on
        the entry), amount_usd (number, USD with 2 decimal places, the fee booked), event_date (string,
        YYYY-MM-DD, the booking date of the entry) and charges_due_usd (number, USD with 2 decimal
        places, the booking's outstanding charges after the fee). A returned booking_event_id means
        the fee is on the account.
    """
    amount = round(float(fee_usd), 2)
    today = ctx.now()[:10]
    rid = ctx.make_id("bkc_", booking_id, "customer_roll_fee", vessel_voyage, amount, today)
    booking = ctx.find("bookings", booking_id=booking_id)
    customer_id = booking[0].get("customer_id", "") if booking else ""
    due = round((float(booking[0].get("charges_due_usd") or 0.0) if booking else 0.0) + amount, 2)
    ctx.create("booking_charges", rid, booking_event_id=rid, booking_id=booking_id,
               equipment_type=(booking[0].get("equipment_type", "") if booking else ""), customer_id=customer_id,
               event_type="booking_amendment_fee_charged", event_date=today, charge_code="customer_roll_fee",
               amount_usd=round(float(fee_usd), 2), vessel_voyage=vessel_voyage,
               amendment_type="customer_requested_vessel_change", roll_initiator="none",
               payment_reference="", reference_event_id="")
    ctx.update("bookings", booking_id, charges_due_usd=due)
    return str({"booking_event_id": rid, "booking_id": booking_id, "charge_code": "customer_roll_fee",
                "vessel_voyage": vessel_voyage, "amount_usd": amount, "event_date": today,
                "charges_due_usd": due})


@tool(owner="agent", rw="write")
def waive_customer_roll_fee_66cbaf18(ctx: ToolContext, booking_id: str, customer_id: str,
                                     reference_event_id: str, waiver_usd: float) -> str:
    """Waive one customer roll fee entry of a container booking as goodwill, cancelling that fee entry in full on the booking's charge account.

    One call books one goodwill waiver entry (tariff code waiver) on the booking's charge history,
    dated today, pointing at the fee entry it cancels, and lowers the booking's outstanding charges by
    exactly the amount passed in. The cancelled fee entry itself stays in the history unchanged, and
    the booking's sailing, containers and status are not touched. Afterwards the waiver entry is
    visible in the booking's charge history next to the fee it cancels and the booking shows the
    reduced charges still outstanding. The call is complete when the receipt below is returned.
    The new entry also carries the booking's equipment type; it records no container count, because the
    amount passed in is already the whole amount of the entry.

    Args:
        booking_id: Id class — booking reference number of the booking whose fee is waived, as returned by the booking lookup for the verified customer.
        customer_id: Id class — customer reference number of the booking party, as returned by the customer profile lookup.
        reference_event_id: Id class — reference number of the customer roll fee entry being waived, as shown in the booking's charge history or in the receipt of the charge that booked it.
        waiver_usd: Fixed-format class — the amount waived, in USD as the money unit, a positive decimal amount with 2 decimal places; a value given with more digits is rounded half-to-even to 2 decimal places when booked.

    Returns:
        A text rendering of a dictionary describing the booked waiver: booking_event_id (string, reference
        of the new waiver entry), booking_id (string, the booking concerned), charge_code (string,
        always waiver), reference_event_id (string, the fee entry cancelled), amount_usd (number, USD
        with 2 decimal places, the amount waived), event_date (string, YYYY-MM-DD, the booking date of
        the waiver) and charges_due_usd (number, USD with 2 decimal places, the booking's outstanding
        charges after the waiver). A returned booking_event_id means the waiver is on the account.
    """
    amount = round(float(waiver_usd), 2)
    today = ctx.now()[:10]
    rid = ctx.make_id("bkc_", booking_id, "waiver", reference_event_id, amount, today)
    booking = ctx.find("bookings", booking_id=booking_id)
    due = round((float(booking[0].get("charges_due_usd") or 0.0) if booking else 0.0) - amount, 2)
    ctx.create("booking_charges", rid, booking_event_id=rid, booking_id=booking_id,
               equipment_type=(booking[0].get("equipment_type", "") if booking else ""), customer_id=customer_id,
               event_type="booking_charge_waived", event_date=today, charge_code="waiver",
               amount_usd=round(float(waiver_usd), 2), amendment_type="none", roll_initiator="none",
               payment_reference="", reference_event_id=reference_event_id)
    ctx.update("bookings", booking_id, charges_due_usd=due)
    return str({"booking_event_id": rid, "booking_id": booking_id, "charge_code": "waiver",
                "reference_event_id": reference_event_id, "amount_usd": amount, "event_date": today,
                "charges_due_usd": due})


@tool(owner="agent", rw="write")
def credit_roll_compensation_f67bce09(ctx: ToolContext, booking_id: str, reference_event_id: str,
                                      compensation_usd: float) -> str:
    """Credit roll compensation to a container booking's charge account for one carrier roll already recorded on the booking.

    One call books one roll compensation entry (tariff code roll_compensation) on the booking's charge
    history, dated today and pointing at the roll entry it compensates, and lowers the booking's
    outstanding charges by exactly the amount passed in. The roll entry itself, the booking's sailing,
    containers and status are not touched. Afterwards the compensation entry is visible in the charge
    history next to the roll it compensates and the booking shows the reduced charges still
    outstanding. The call is complete when the receipt below is returned.
    The new entry also carries the booking's equipment type; it records no container count, because the
    amount passed in is already the whole amount of the entry.

    Args:
        booking_id: Id class — booking reference number of the booking being credited, as returned by the booking lookup for the verified customer.
        reference_event_id: Id class — reference number of the carrier roll entry being compensated, as shown in the booking's charge history.
        compensation_usd: Fixed-format class — the compensation to credit, in USD as the money unit, a positive decimal amount with 2 decimal places; a value given with more digits is rounded half-to-even to 2 decimal places when booked.

    Returns:
        A text rendering of a dictionary describing the booked credit: booking_event_id (string, reference
        of the new compensation entry), booking_id (string, the booking credited), charge_code (string,
        always roll_compensation), reference_event_id (string, the roll entry compensated), amount_usd
        (number, USD with 2 decimal places, the credit booked), event_date (string, YYYY-MM-DD, the
        booking date of the entry) and charges_due_usd (number, USD with 2 decimal places, the booking's
        outstanding charges after the credit). A returned booking_event_id means the credit is on the
        account.
    """
    amount = round(float(compensation_usd), 2)
    today = ctx.now()[:10]
    rid = ctx.make_id("bkc_", booking_id, "roll_compensation", reference_event_id, amount, today)
    booking = ctx.find("bookings", booking_id=booking_id)
    customer_id = booking[0].get("customer_id", "") if booking else ""
    due = round((float(booking[0].get("charges_due_usd") or 0.0) if booking else 0.0) - amount, 2)
    ctx.create("booking_charges", rid, booking_event_id=rid, booking_id=booking_id,
               equipment_type=(booking[0].get("equipment_type", "") if booking else ""), customer_id=customer_id,
               event_type="booking_roll_compensation_credited", event_date=today, charge_code="roll_compensation",
               amount_usd=round(float(compensation_usd), 2), amendment_type="none", roll_initiator="none",
               payment_reference="", reference_event_id=reference_event_id)
    ctx.update("bookings", booking_id, charges_due_usd=due)
    return str({"booking_event_id": rid, "booking_id": booking_id, "charge_code": "roll_compensation",
                "reference_event_id": reference_event_id, "amount_usd": amount, "event_date": today,
                "charges_due_usd": due})


@tool(owner="agent", rw="write")
def record_late_si_fee_242ae989(ctx: ToolContext, booking_id: str, fee_usd: float) -> str:
    """Record one late shipping-instructions entry on a container booking's charge account for its allocated sailing, at the amount passed in.

    One call books one late documentation entry (tariff code late_si_fee) on the booking's charge
    history, dated today and carrying the sailing the booking is currently allocated to, and raises
    the booking's outstanding charges by exactly the amount passed in; an amount of 0.00 records the
    late submission without a charge. The booking's documents, sailing and status are not touched.
    Afterwards the entry is visible in the booking's charge history. The call is complete when the
    receipt below is returned.
    The new entry also carries the booking's equipment type; it records no container count, because the
    amount passed in is already the whole amount of the entry.

    Args:
        booking_id: Id class — booking reference number of the booking whose shipping instructions were late, as returned by the booking lookup for the verified customer.
        fee_usd: Fixed-format class — the amount of the late entry, in USD as the money unit, a non-negative decimal amount with 2 decimal places where 0.00 records the late submission free of charge; a value given with more digits is rounded half-to-even to 2 decimal places when booked.

    Returns:
        A text rendering of a dictionary describing the booked entry: booking_event_id (string, reference
        of the new entry), booking_id (string, the booking concerned), charge_code (string, always
        late_si_fee), vessel_voyage (string, the sailing the entry is recorded for), amount_usd (number,
        USD with 2 decimal places, the amount booked, possibly 0.00), event_date (string, YYYY-MM-DD,
        the booking date of the entry) and charges_due_usd (number, USD with 2 decimal places, the
        booking's outstanding charges afterwards). A returned booking_event_id means the entry is on
        the account.
    """
    amount = round(float(fee_usd), 2)
    today = ctx.now()[:10]
    booking = ctx.find("bookings", booking_id=booking_id)
    customer_id = booking[0].get("customer_id", "") if booking else ""
    vessel = booking[0].get("vessel_voyage", "") if booking else ""
    rid = ctx.make_id("bkc_", booking_id, "late_si_fee", vessel, amount, today)
    due = round((float(booking[0].get("charges_due_usd") or 0.0) if booking else 0.0) + amount, 2)
    ctx.create("booking_charges", rid, booking_event_id=rid, booking_id=booking_id,
               equipment_type=(booking[0].get("equipment_type", "") if booking else ""), customer_id=customer_id,
               event_type="booking_late_document_fee_charged", event_date=today, charge_code="late_si_fee",
               amount_usd=round(float(fee_usd), 2), vessel_voyage=vessel, amendment_type="none",
               roll_initiator="none", payment_reference="", reference_event_id="")
    ctx.update("bookings", booking_id, charges_due_usd=due)
    return str({"booking_event_id": rid, "booking_id": booking_id, "charge_code": "late_si_fee",
                "vessel_voyage": vessel, "amount_usd": amount, "event_date": today, "charges_due_usd": due})


@tool(owner="user", rw="write")
def submit_vgm_declaration_120f73ac(ctx: ToolContext, booking_id: str) -> str:
    """Transmit the shipper's own signed verified gross mass declaration for a container booking to the line, so that it is recorded as received now.

    The shipper performs this itself, as the party responsible for the verified gross mass: one call
    records the current moment as the time the booking's verified gross mass was received by the line,
    replacing any earlier receipt time on the booking. Nothing else on the booking and no charge is
    changed. Afterwards the booking shows the verified gross mass as received at that moment. The call
    is complete when the receipt below is returned.

    Args:
        booking_id: Id class — booking reference number of the booking the declaration is for, as given to the shipper by the service agent from the booking lookup.

    Returns:
        A text rendering of a dictionary confirming the transmission: booking_id (string, the booking the
        declaration was recorded on), document (string, always verified_gross_mass) and received_at
        (string, YYYY-MM-DDTHH:MM in the local time of the clock the line records, the moment recorded
        as receipt). A returned received_at means the declaration is on record.
    """
    now = ctx.now()
    received_at = now[:10] + "T" + now[11:16]
    ctx.update("bookings", booking_id, vgm_submitted_at=received_at)
    return str({"booking_id": booking_id, "document": "verified_gross_mass", "received_at": received_at})


@tool(owner="agent", rw="write")
def record_late_vgm_fee_5d1f74dd(ctx: ToolContext, booking_id: str, fee_usd: float) -> str:
    """Record one late verified-gross-mass entry on a container booking's charge account for its allocated sailing, at the amount passed in.

    One call books one late documentation entry (tariff code late_vgm_fee) on the booking's charge
    history, dated today and carrying the sailing the booking is currently allocated to, and raises
    the booking's outstanding charges by exactly the amount passed in; an amount of 0.00 records the
    late submission without a charge. The booking's documents, sailing and status are not touched.
    Afterwards the entry is visible in the booking's charge history. The call is complete when the
    receipt below is returned.
    The new entry also carries the booking's equipment type; it records no container count, because the
    amount passed in is already the whole amount of the entry.

    Args:
        booking_id: Id class — booking reference number of the booking whose verified gross mass was late, as returned by the booking lookup for the verified customer.
        fee_usd: Fixed-format class — the amount of the late entry, in USD as the money unit, a non-negative decimal amount with 2 decimal places where 0.00 records the late submission free of charge; a value given with more digits is rounded half-to-even to 2 decimal places when booked.

    Returns:
        A text rendering of a dictionary describing the booked entry: booking_event_id (string, reference
        of the new entry), booking_id (string, the booking concerned), charge_code (string, always
        late_vgm_fee), vessel_voyage (string, the sailing the entry is recorded for), amount_usd
        (number, USD with 2 decimal places, the amount booked, possibly 0.00), event_date (string,
        YYYY-MM-DD, the booking date of the entry) and charges_due_usd (number, USD with 2 decimal
        places, the booking's outstanding charges afterwards). A returned booking_event_id means the
        entry is on the account.
    """
    amount = round(float(fee_usd), 2)
    today = ctx.now()[:10]
    booking = ctx.find("bookings", booking_id=booking_id)
    customer_id = booking[0].get("customer_id", "") if booking else ""
    vessel = booking[0].get("vessel_voyage", "") if booking else ""
    rid = ctx.make_id("bkc_", booking_id, "late_vgm_fee", vessel, amount, today)
    due = round((float(booking[0].get("charges_due_usd") or 0.0) if booking else 0.0) + amount, 2)
    ctx.create("booking_charges", rid, booking_event_id=rid, booking_id=booking_id,
               equipment_type=(booking[0].get("equipment_type", "") if booking else ""), customer_id=customer_id,
               event_type="booking_late_document_fee_charged", event_date=today, charge_code="late_vgm_fee",
               amount_usd=round(float(fee_usd), 2), vessel_voyage=vessel, amendment_type="none",
               roll_initiator="none", payment_reference="", reference_event_id="")
    ctx.update("bookings", booking_id, charges_due_usd=due)
    return str({"booking_event_id": rid, "booking_id": booking_id, "charge_code": "late_vgm_fee",
                "vessel_voyage": vessel, "amount_usd": amount, "event_date": today, "charges_due_usd": due})

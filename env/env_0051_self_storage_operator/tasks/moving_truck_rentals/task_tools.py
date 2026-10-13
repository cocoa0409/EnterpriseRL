"""Task tools of the moving_truck_rentals difficulty (Bluegate Moving Truck Rental).

Hidden atomic writes on truck rental contracts, reached only through unlock_* -> call_*. Each tool
lands one business action with exactly the values it is given; none of them judges eligibility,
works out an amount or checks what else stands on the contract.
"""

from erlbench import ToolContext, tool


@tool(owner="user", rw="write")
def cancel_truck_reservation_ee0618b8(ctx: ToolContext, truck_rental_id: str,
                                      late_cancellation_fee: float) -> str:
    """The renter cancels one of their own truck reservations and accepts the cancellation fee shown to them.

    The reservation is moved to cancelled status with the cancellation date and time stamped at the moment of the
    call. When the fee given is above zero, a late cancellation fee line for that amount is posted to the same
    reservation, dated the cancellation date, and the amount owed on the reservation rises by it; a fee of 0.00
    posts no fee line. The renter sees the reservation listed as cancelled and, where a fee applies, the fee owed.

    Args:
        truck_rental_id: Id class — the truck rental contract number of the reservation being cancelled, read from
            the renter's truck rentals in the truck rental lookup.
        late_cancellation_fee: Fixed-format class — the cancellation fee the renter accepts, in USD, a non-negative
            amount rounded to 2 decimal places; 0.00 when no fee applies.

    Returns:
        A dict with: status ("cancelled"), truck_rental_id (the contract number cancelled), cancelled_at (the
        cancellation timestamp, YYYY-MM-DD HH:MM:SS with the time zone), fee_charge_id (the id of the posted fee
        line, or "" when no fee line was posted), late_cancellation_fee (the fee posted, USD with 2 decimal places)
        and balance_due (the amount now owed on the reservation, USD with 2 decimal places). A status of
        "cancelled" means the cancellation is recorded.
    """
    fee = round(float(late_cancellation_fee), 2)
    now = ctx.now()
    found = ctx.find("truck_rentals", truck_rental_id=truck_rental_id)
    row = found[0] if found else {}
    balance = round(float(row.get("balance_due") or 0) + fee, 2)
    ctx.update("truck_rentals", truck_rental_id, status="cancelled", cancelled_at_date=now[:10],
               cancelled_at_time=now[11:16], balance_due=balance)
    charge_id = ""
    if fee > 0:
        charge_id = ctx.make_id("tch_", truck_rental_id, fee)
        ctx.create("truck_charges", charge_id, truck_charge_id=charge_id, truck_rental_id=truck_rental_id,
                   customer_id=row.get("customer_id", ""), event_type="truck_charge",
                   charge_type="late_cancellation_fee", credit_type="", amount=fee, service_date=now[:10],
                   quantity=1, reference_id="", payment_method="", release_type="")
    return str({"status": "cancelled", "truck_rental_id": truck_rental_id, "cancelled_at": now,
                "fee_charge_id": charge_id, "late_cancellation_fee": fee, "balance_due": balance})


@tool(owner="agent", rw="write")
def post_additional_rental_day_charge_add5e32c(ctx: ToolContext, truck_rental_id: str, customer_id: str,
                                               service_date: str, additional_days: int, amount: float) -> str:
    """Post the charge for the rental days a returned truck contract ran beyond its opening day.

    One base rental fee line is added to the contract for the given amount, carrying the number of additional
    rental days as its quantity and the given service date, and the amount owed on the contract rises by that
    amount. The renter sees the additional-day line on the final invoice.

    Args:
        truck_rental_id: Id class — the truck rental contract number the charge belongs to, read from the truck
            rental lookup.
        customer_id: Id class — the customer reference number of the renter on that contract, read from the customer
            profile lookup.
        service_date: Fixed-format class — the date the additional-day line relates to, in YYYY-MM-DD format.
        additional_days: Fixed-format class — the number of rental days started beyond the opening day, a whole integer
            count.
        amount: Fixed-format class — the additional-day charge in USD, a positive amount rounded to 2 decimal places.

    Returns:
        A dict with: status ("posted"), truck_charge_id (the id of the new charge line), truck_rental_id,
        charge_type ("base_rental_fee"), amount (USD with 2 decimal places), quantity (the additional days, integer),
        service_date (YYYY-MM-DD) and balance_due (the amount now owed on the contract, USD with 2 decimal places).
        A status of "posted" means the line is on the contract.
    """
    amt = round(float(amount), 2)
    days = int(additional_days)
    found = ctx.find("truck_rentals", truck_rental_id=truck_rental_id)
    row = found[0] if found else {}
    balance = round(float(row.get("balance_due") or 0) + amt, 2)
    charge_id = ctx.make_id("tch_", truck_rental_id, customer_id, service_date, days, amt)
    ctx.create("truck_charges", charge_id, truck_charge_id=charge_id, truck_rental_id=truck_rental_id,
               customer_id=customer_id, event_type="truck_charge", charge_type="base_rental_fee", credit_type="",
               amount=amt, service_date=service_date, quantity=days, reference_id="", payment_method="",
               release_type="")
    ctx.update("truck_rentals", truck_rental_id, balance_due=balance)
    return str({"status": "posted", "truck_charge_id": charge_id, "truck_rental_id": truck_rental_id,
                "charge_type": "base_rental_fee", "amount": amt, "quantity": days, "service_date": service_date,
                "balance_due": balance})


@tool(owner="agent", rw="write")
def apply_move_in_claim_miles_credit_24951572(ctx: ToolContext, truck_rental_id: str, linked_rental_id: str,
                                              reference_id: str, amount: float) -> str:
    """Record a storage unit's free move-in claim on a truck contract and credit the claimed miles against its mileage line.

    The contract's linked storage unit is set to the given storage rental agreement, and one free move-in waiver
    credit for the given amount is posted against the given mileage charge line, dated the day of the call; the
    amount owed on the contract falls by that amount. The renter sees the contract tied to the storage unit and
    the mileage credit on the invoice.

    Args:
        truck_rental_id: Id class — the truck rental contract number the claim is recorded on, read from the truck
            rental lookup.
        linked_rental_id: Id class — the storage unit rental agreement number the free move-in is claimed for, read
            from the storage unit rental lookup.
        reference_id: Id class — the id of the mileage charge line being credited, read from the truck contract
            charge lookup.
        amount: Fixed-format class — the mileage credit in USD, a positive amount rounded to 2 decimal places.

    Returns:
        A dict with: status ("credited"), truck_charge_id (the id of the new credit line), truck_rental_id,
        linked_rental_id (the storage agreement now on the contract), credit_type ("free_move_in_waiver"),
        reference_id (the credited mileage line), amount (USD with 2 decimal places) and balance_due (the amount now
        owed on the contract, USD with 2 decimal places). A status of "credited" means the claim and the credit are
        recorded.
    """
    amt = round(float(amount), 2)
    found = ctx.find("truck_rentals", truck_rental_id=truck_rental_id)
    row = found[0] if found else {}
    balance = round(float(row.get("balance_due") or 0) - amt, 2)
    credit_id = ctx.make_id("tcr_", truck_rental_id, linked_rental_id, reference_id, amt)
    ctx.update("truck_rentals", truck_rental_id, linked_rental_id=linked_rental_id, balance_due=balance)
    ctx.create("truck_charges", credit_id, truck_charge_id=credit_id, truck_rental_id=truck_rental_id,
               customer_id=row.get("customer_id", ""), event_type="truck_credit", charge_type="",
               credit_type="free_move_in_waiver", amount=amt, service_date=ctx.now()[:10], quantity="",
               reference_id=reference_id, payment_method="", release_type="")
    return str({"status": "credited", "truck_charge_id": credit_id, "truck_rental_id": truck_rental_id,
                "linked_rental_id": linked_rental_id, "credit_type": "free_move_in_waiver",
                "reference_id": reference_id, "amount": amt, "balance_due": balance})


@tool(owner="agent", rw="write")
def credit_move_in_rental_waiver_7c9a948d(ctx: ToolContext, truck_rental_id: str, linked_rental_id: str,
                                          reference_id: str, amount: float) -> str:
    """Credit the free move-in rental waiver against the first-day rental fee line of a truck contract.

    One free move-in waiver credit for the given amount is posted against the given first-day rental fee line,
    dated the day of the call, for the storage unit rental agreement named; the amount owed on the contract falls
    by that amount. The renter sees the rental waiver credit on the invoice.

    Args:
        truck_rental_id: Id class — the truck rental contract number the waiver is credited on, read from the truck
            rental lookup.
        linked_rental_id: Id class — the storage unit rental agreement number the free move-in benefit belongs to,
            read from the storage unit rental lookup.
        reference_id: Id class — the id of the first-day rental fee line being credited, read from the truck contract
            charge lookup.
        amount: Fixed-format class — the rental waiver in USD, a positive amount rounded to 2 decimal places.

    Returns:
        A dict with: status ("credited"), truck_charge_id (the id of the new credit line), truck_rental_id,
        linked_rental_id (the storage agreement the benefit belongs to), credit_type ("free_move_in_waiver"),
        reference_id (the credited first-day fee line), amount (USD with 2 decimal places) and balance_due (the amount
        now owed on the contract, USD with 2 decimal places). A status of "credited" means the waiver is recorded.
    """
    amt = round(float(amount), 2)
    found = ctx.find("truck_rentals", truck_rental_id=truck_rental_id)
    row = found[0] if found else {}
    balance = round(float(row.get("balance_due") or 0) - amt, 2)
    credit_id = ctx.make_id("tcr_", truck_rental_id, linked_rental_id, reference_id, amt)
    ctx.create("truck_charges", credit_id, truck_charge_id=credit_id, truck_rental_id=truck_rental_id,
               customer_id=row.get("customer_id", ""), event_type="truck_credit", charge_type="",
               credit_type="free_move_in_waiver", amount=amt, service_date=ctx.now()[:10], quantity="",
               reference_id=reference_id, payment_method="", release_type="")
    ctx.update("truck_rentals", truck_rental_id, balance_due=balance)
    return str({"status": "credited", "truck_charge_id": credit_id, "truck_rental_id": truck_rental_id,
                "linked_rental_id": linked_rental_id, "credit_type": "free_move_in_waiver",
                "reference_id": reference_id, "amount": amt, "balance_due": balance})


@tool(owner="agent", rw="write")
def post_first_day_rental_fee_f35b099c(ctx: ToolContext, truck_rental_id: str, customer_id: str, amount: float) -> str:
    """Post the first-day rental fee on a truck rental contract.

    One base rental fee line for the given amount is added to the contract, dated the day of the call with a
    quantity of one, and the amount owed on the contract rises by that amount. The renter sees the first-day fee
    among the charges on the contract.

    Args:
        truck_rental_id: Id class — the truck rental contract number the fee is posted on, read from the truck rental
            lookup.
        customer_id: Id class — the customer reference number of the renter on that contract, read from the customer
            profile lookup.
        amount: Fixed-format class — the first-day rental fee in USD, a positive amount rounded to 2 decimal places.

    Returns:
        A dict with: status ("posted"), truck_charge_id (the id of the new fee line), truck_rental_id,
        charge_type ("base_rental_fee"), amount (USD with 2 decimal places), service_date (YYYY-MM-DD, the day the
        line is posted) and balance_due (the amount now owed on the contract, USD with 2 decimal places). A status of
        "posted" means the fee line is on the contract.
    """
    amt = round(float(amount), 2)
    found = ctx.find("truck_rentals", truck_rental_id=truck_rental_id)
    row = found[0] if found else {}
    balance = round(float(row.get("balance_due") or 0) + amt, 2)
    day = ctx.now()[:10]
    charge_id = ctx.make_id("tch_", truck_rental_id, customer_id, amt)
    ctx.create("truck_charges", charge_id, truck_charge_id=charge_id, truck_rental_id=truck_rental_id,
               customer_id=customer_id, event_type="truck_charge", charge_type="base_rental_fee", credit_type="",
               amount=amt, service_date=day, quantity=1, reference_id="", payment_method="", release_type="")
    ctx.update("truck_rentals", truck_rental_id, balance_due=balance)
    return str({"status": "posted", "truck_charge_id": charge_id, "truck_rental_id": truck_rental_id,
                "charge_type": "base_rental_fee", "amount": amt, "service_date": day, "balance_due": balance})


@tool(owner="user", rw="write")
def sign_truck_rental_contract_074f2414(ctx: ToolContext, truck_rental_id: str, customer_id: str,
                                        truck_unit_number: str, odometer_out: int, fuel_out_eighths: int,
                                        damage_waiver: str, additional_drivers: int,
                                        deposit_hold_amount: float) -> str:
    """The renter signs their truck rental contract at pickup and takes the vehicle.

    The reservation moves to picked_up with the pickup date and time stamped at the moment of signing, and the
    fleet number, odometer and fuel readings, damage waiver choice and number of additional drivers given are
    recorded on the contract. An authorization hold for the given amount is placed on the card on file with the
    reservation, dated the pickup date, and the hold on the contract rises by that amount. The renter sees the
    contract as signed and the vehicle released, with the hold shown against the card.

    Args:
        truck_rental_id: Id class — the truck rental contract number of the renter's reservation, read from the truck
            rental lookup.
        customer_id: Id class — the customer reference number of the renter signing, read from the customer profile
            lookup.
        truck_unit_number: Verbatim class — the fleet number of the vehicle handed over, exactly as the renter reads
            it from the key tag, copied character for character with no change (verbatim).
        odometer_out: Fixed-format class — the odometer reading at pickup as the renter reads it, integer miles.
        fuel_out_eighths: Fixed-format class — the fuel gauge reading at pickup, an integer 0-8 counted in eighths of
            a tank.
        damage_waiver: Enum class — the damage waiver the renter takes at signing: none when the renter declines any
            waiver and carries the full repair estimate for damage; basic when the renter buys the basic damage
            waiver and carries damage up to its deductible; premium when the renter buys the premium damage waiver
            with its lower deductible.
        additional_drivers: Fixed-format class — the number of additional authorized drivers added at signing,
            integer; 0 when the renter is the only driver.
        deposit_hold_amount: Fixed-format class — the authorization hold placed on the card, in USD, a positive amount
            rounded to 2 decimal places.

    Returns:
        A dict with: status ("picked_up"), truck_rental_id, actual_pickup (YYYY-MM-DD HH:MM:SS with the time zone),
        truck_unit_number (as recorded), hold_id (the id of the hold entry), deposit_hold_amount (the hold placed, USD
        with 2 decimal places) and hold_on_card (the total hold now on the contract, USD with 2 decimal places). A
        status of "picked_up" means the contract is signed and the vehicle released.
    """
    hold = round(float(deposit_hold_amount), 2)
    now = ctx.now()
    found = ctx.find("truck_rentals", truck_rental_id=truck_rental_id)
    row = found[0] if found else {}
    on_card = round(float(row.get("deposit_hold_amount") or 0) + hold, 2)
    ctx.update("truck_rentals", truck_rental_id, status="picked_up", actual_pickup_date=now[:10],
               actual_pickup_time=now[11:16], truck_unit_number=truck_unit_number, odometer_out=int(odometer_out),
               fuel_out_eighths=int(fuel_out_eighths), damage_waiver=damage_waiver,
               additional_drivers=int(additional_drivers), deposit_hold_amount=on_card)
    hold_id = ctx.make_id("thd_", truck_rental_id, customer_id, truck_unit_number, odometer_out, fuel_out_eighths,
                          damage_waiver, additional_drivers, hold)
    ctx.create("truck_charges", hold_id, truck_charge_id=hold_id, truck_rental_id=truck_rental_id,
               customer_id=customer_id, event_type="truck_deposit_hold", charge_type="", credit_type="",
               amount=hold, service_date=now[:10], quantity="", reference_id="", payment_method="", release_type="")
    return str({"status": "picked_up", "truck_rental_id": truck_rental_id, "actual_pickup": now,
                "truck_unit_number": truck_unit_number, "hold_id": hold_id, "deposit_hold_amount": hold,
                "hold_on_card": on_card})

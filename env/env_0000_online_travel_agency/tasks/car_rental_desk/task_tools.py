"""Hidden task tools for the car rental desk (scenario: online_travel_agency).

Each tool is reached only through the unlock/call meta tools; its name is registered in
drive.extended.yaml as an extended policy's target_tool. Every tool performs one atomic
business action with the values the agent has already worked out from the published terms.
"""

from erlbench import ToolContext, tool


@tool(owner="agent", rw="write")
def charge_additional_driver_79b211ed(ctx: ToolContext, drive_rental_id: str,
                                      additional_driver_charge_usd: float) -> str:
    """Put the additional driver charge owed on a car rental agreement onto that rental's ledger.
    One call raises a single additional driver line against the rental for the drivers named on the
    agreement beyond the ones it carries free, at the amount supplied. The rental's ledger gains
    that line, the amount is billed to the card held against the rental, and the renter sees a
    single "additional driver" entry on the agreement. The call has completed when the confirmation
    below comes back carrying the new ledger line's reference and the amount charged.

    Args:
        drive_rental_id: Id class — the reference number of the car rental agreement the charge
            belongs to, as it stands on the rental record returned by the car rental lookup.
        additional_driver_charge_usd: Fixed-format class — the money charged for the additional
            drivers named on the agreement, in US dollars as a positive USD amount with 2 decimal
            places, rounded half to even at the last step only, carrying no currency symbol and no
            thousands separator.

    Returns:
        A confirmation sentence naming the reference of the additional driver ledger line just
        raised (a string beginning "adr_"), the rental agreement it was raised against and the
        amount in US dollars to two decimal places that now stands on the ledger. Any other text
        means the line was not raised.
    """
    rows = ctx.find("drive_rentals", drive_rental_id=drive_rental_id)
    customer_id = rows[0].get("customer_id") if rows else ""
    amount = round(float(additional_driver_charge_usd), 2)
    rid = ctx.make_id("adr_", drive_rental_id, additional_driver_charge_usd)
    ctx.create("drive_rental_entries", rid, drive_entry_id=rid, drive_rental_id=drive_rental_id,
               customer_id=customer_id, event_type="drive_extras_charge",
               charge_category="additional_driver", amount_usd=amount, currency_charged="USD",
               rental_day_sequence=0, driver_sequence=0, item_sequence=0, miles_delta=0,
               posted_date=ctx.now()[:10], posted_at=ctx.now(), payment_channel="call_centre",
               reason_code="routine_rental")
    return (f"Additional driver charge {rid} raised on rental {drive_rental_id} "
            f"for {amount:.2f} US dollars.")


@tool(owner="user", rw="write")
def release_rental_booking_4b632ce9(ctx: ToolContext, drive_rental_id: str,
                                    release_charge_usd: float) -> str:
    """Give up a confirmed car rental the renter holds in their own name. One call by the renter
    releases the vehicle back to the supplier: the rental record moves to cancelled and is stamped
    with the moment the renter gave it up, and a single release charge line at the amount supplied
    is withheld on the rental's ledger against the money already taken. Afterwards the renter holds
    no booking with the supplier and sees one release charge on the agreement. The call has
    completed when the confirmation below comes back naming the released rental and the charge
    withheld.

    Args:
        drive_rental_id: Id class — the reference number of the renter's own car rental agreement
            being given up, as it stands on the rental record returned by the car rental lookup.
        release_charge_usd: Fixed-format class — the money withheld from the renter for giving the
            rental up, in US dollars as a positive USD amount with 2 decimal places, rounded half to
            even at the last step only, carrying no currency symbol and no thousands separator.

    Returns:
        A confirmation sentence naming the released rental agreement, the reference of the release
        charge line just withheld (a string beginning "rel_") and the amount in US dollars to two
        decimal places withheld against it, together with the new state of the rental record.
        Any other text means the rental was not released.
    """
    rows = ctx.find("drive_rentals", drive_rental_id=drive_rental_id)
    customer_id = rows[0].get("customer_id") if rows else ""
    amount = round(float(release_charge_usd), 2)
    rid = ctx.make_id("rel_", drive_rental_id, release_charge_usd)
    ctx.create("drive_rental_entries", rid, drive_entry_id=rid, drive_rental_id=drive_rental_id,
               customer_id=customer_id, event_type="drive_cancellation_charge",
               charge_category="cancellation_fee", amount_usd=amount, currency_charged="USD",
               rental_day_sequence=0, driver_sequence=0, item_sequence=0, miles_delta=0,
               posted_date=ctx.now()[:10], posted_at=ctx.now(), payment_channel="call_centre",
               reason_code="renter_cancellation")
    ctx.update("drive_rentals", drive_rental_id, status="cancelled", cancelled_at=ctx.now())
    return (f"Rental {drive_rental_id} released and now cancelled; release charge {rid} "
            f"withheld for {amount:.2f} US dollars.")


@tool(owner="agent", rw="write")
def grant_included_mileage_444a2a24(ctx: ToolContext, drive_rental_id: str, miles_granted: int) -> str:
    """Place the included mileage a car rental agreement carries onto that rental's allowance. One
    call credits the rental with a single grant covering the whole hire at the figure supplied, so
    the rental's included allowance stands at that many miles once the grant is placed, and the
    renter can be told how far the hire lets them drive on the miles the class includes. The call
    has completed when the confirmation below comes back naming the grant and the miles credited.

    Args:
        drive_rental_id: Id class — the reference number of the car rental agreement the allowance
            belongs to, as it stands on the rental record returned by the car rental lookup.
        miles_granted: Fixed-format class — the included miles placed on the rental, given as a
            whole number of miles, negative when miles are consumed, so a grant is stated as a
            positive integer with no decimal part, no thousands separator and no unit written after
            it.

    Returns:
        A confirmation sentence naming the reference of the mileage grant just placed (a string
        beginning "mlg_"), the rental agreement it was placed on and the whole number of included
        miles now standing on that rental's allowance. Any other text means the grant was not placed.
    """
    rows = ctx.find("drive_rentals", drive_rental_id=drive_rental_id)
    customer_id = rows[0].get("customer_id") if rows else ""
    miles = int(miles_granted)
    rid = ctx.make_id("mlg_", drive_rental_id, miles_granted)
    ctx.create("drive_rental_entries", rid, drive_entry_id=rid, drive_rental_id=drive_rental_id,
               customer_id=customer_id, event_type="drive_mileage_grant",
               charge_category="mileage_grant", amount_usd=0.0, currency_charged="USD",
               rental_day_sequence=0, driver_sequence=0, item_sequence=0, miles_delta=miles,
               posted_date=ctx.now()[:10], posted_at=ctx.now(), payment_channel="call_centre",
               reason_code="routine_rental")
    return (f"Included mileage grant {rid} placed on rental {drive_rental_id}: "
            f"{miles} miles now stand on the allowance.")


@tool(owner="user", rw="write")
def close_rental_return_9b1c513c(ctx: ToolContext, drive_rental_id: str,
                                 excess_mileage_charge_usd: float) -> str:
    """Confirm that the renter has handed their own hired vehicle back, and settle the excess
    mileage on the agreement in the same act. One call by the renter moves their rental record to
    returned and stamps it with the moment it came back, and puts a single excess mileage line at
    the amount supplied onto the rental's ledger against the card held for the hire. Afterwards the
    renter holds no vehicle on the agreement and sees one excess mileage entry closing it off. The
    call has completed when the confirmation below comes back naming the returned rental and the
    excess mileage settled.

    Args:
        drive_rental_id: Id class — the reference number of the renter's own car rental agreement
            being closed off, as it stands on the rental record returned by the car rental lookup.
        excess_mileage_charge_usd: Fixed-format class — the money settled for the miles driven
            beyond what the hire included, in US dollars as a positive USD amount with 2 decimal
            places, rounded half to even at the last step only, carrying no currency symbol and no
            thousands separator.

    Returns:
        A confirmation sentence naming the rental agreement now standing as returned, the reference
        of the excess mileage line just settled (a string beginning "xms_") and the amount in US
        dollars to two decimal places that now stands on the ledger. Any other text means the return
        was not recorded.
    """
    rows = ctx.find("drive_rentals", drive_rental_id=drive_rental_id)
    customer_id = rows[0].get("customer_id") if rows else ""
    amount = round(float(excess_mileage_charge_usd), 2)
    rid = ctx.make_id("xms_", drive_rental_id, excess_mileage_charge_usd)
    ctx.create("drive_rental_entries", rid, drive_entry_id=rid, drive_rental_id=drive_rental_id,
               customer_id=customer_id, event_type="drive_extras_charge",
               charge_category="excess_mileage", amount_usd=amount, currency_charged="USD",
               rental_day_sequence=0, driver_sequence=0, item_sequence=1, miles_delta=0,
               posted_date=ctx.now()[:10], posted_at=ctx.now(), payment_channel="call_centre",
               reason_code="routine_rental")
    ctx.update("drive_rentals", drive_rental_id, status="returned", returned_at=ctx.now())
    return (f"Rental {drive_rental_id} now stands returned; excess mileage {rid} settled "
            f"for {amount:.2f} US dollars.")

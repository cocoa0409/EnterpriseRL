"""Hidden task tools for the Keyturn trip booking and settlement desk.

Each tool performs one atomic write on the trip records. None of them aggregates history,
prices anything or judges whether the write is due: the agent reads the marketplace rules and
the reservation's own records, works the figure out, and passes it in.
"""

from erlbench import ToolContext, tool


@tool(owner="agent", rw="write")
def grant_mileage_topup_0373887d(ctx: ToolContext, booking_id: str, customer_id: str,
                                 granted_miles: int) -> str:
    """Add a bought top-up of included miles to one trip reservation. The call books a single
    grant against the reservation's mileage record, dated today and marked as a purchased
    top-up made part way through the trip, so that the miles it adds stay separable from the
    allowance the reservation was granted when it was confirmed and from any miles an
    extension brings. After the call the reservation's mileage record carries the added miles
    and the guest can see them among the included miles granted to the trip. The call has
    completed when the confirmation naming the new mileage record and the miles added comes
    back.

    Args:
        booking_id: Id class — the reference number of the trip reservation the miles are added
            to, read from the trip booking lookup before the call.
        customer_id: Id class — the member reference number of the guest holding that
            reservation, read from the member profile lookup before the call.
        granted_miles: Fixed-format class — how many included miles this top-up adds, written in
            whole miles, signed, positive on a grant, with no decimal part and no thousands
            separator.

    Returns:
        A confirmation sentence naming the reference number of the new mileage record, the
        reservation it was booked against and the miles added, in whole miles. Receiving that
        sentence means the grant is on the reservation's mileage record; anything else means no
        miles were added.
    """
    rid = ctx.make_id("usg_", booking_id, customer_id, granted_miles)
    ctx.create("trips_usage", rid, usage_id=rid, booking_id=booking_id, customer_id=customer_id,
               event_type="trips_mileage_allowance_granted", usage_date=ctx.now()[:10],
               reading_point="mid_trip", odometer_reading=0, miles_delta=int(granted_miles),
               fuel_percent=0, usage_source="guest_report", grant_reason="purchased_package")
    return (f"Mileage record {rid} booked against reservation {booking_id}: "
            f"{int(granted_miles)} included miles added.")


@tool(owner="user", rw="write")
def pay_for_mileage_topup_d571ad94(ctx: ToolContext, booking_id: str, customer_id: str,
                                   purchase_amount: float) -> str:
    """Let the guest pay for the extra included miles standing on their own trip reservation.
    The call posts a single priced line for the mileage purchase to that reservation, dated
    today, taken from the card held on the trip, and raises the balance owed on the reservation
    by the amount paid for. After the call the guest sees the mileage purchase as its own line
    among the trip's priced lines, separate from the rate, the trip fee and the deposit. The
    call has completed when the receipt naming the new line and the amount comes back.

    Args:
        booking_id: Id class — the reference number of the guest's trip reservation the purchase
            is posted to, as the desk read it out from the trip booking lookup.
        customer_id: Id class — the member reference number of the guest making the purchase, as
            the desk read it out from the member profile lookup.
        purchase_amount: Fixed-format class — the money the mileage purchase costs, in USD, 2
            decimal places, rounded half up to the cent, positive because it is money the guest
            owes.

    Returns:
        A receipt sentence naming the reference number of the new priced line, the reservation
        it was posted to and the amount in USD to two decimal places. Receiving that sentence
        means the line is on the trip and the balance has risen by it; anything else means
        nothing was posted.
    """
    rid = ctx.make_id("chg_", booking_id, customer_id, purchase_amount)
    ctx.create("trips_charges", rid, charge_id=rid, booking_id=booking_id,
               customer_id=customer_id, event_type="trips_reservation_charge_posted",
               charge_date=ctx.now()[:10], charge_amount=round(float(purchase_amount), 2),
               charge_basis="extra_miles_package", quantity_units=0.0, unit_rate_amount=0.00,
               billing_period="at_trip_start", payment_channel="card_on_file",
               waiver_code="none")
    return (f"Charge line {rid} posted to reservation {booking_id} for the mileage purchase: "
            f"{round(float(purchase_amount), 2):.2f} USD.")


@tool(owner="agent", rw="write")
def post_young_driver_surcharge_8e3312c3(ctx: ToolContext, booking_id: str, customer_id: str,
                                         surcharge_amount: float) -> str:
    """Raise the young-driver surcharge owed on one trip reservation as its own priced line.
    The call posts a single line of that kind to the reservation, dated today, taken from the
    card held on the trip, and raises the balance the guest owes by it; keeping the surcharge
    on a line of its own is what lets it be given back on its own if the driver's age on file
    turns out to be wrong. After the call the guest sees the surcharge among the trip's priced
    lines, apart from the rate, the marketplace fee and the deposit. The call has completed
    when the confirmation naming the new line and the amount comes back.

    Args:
        booking_id: Id class — the reference number of the trip reservation the surcharge is
            raised on, read from the trip booking lookup before the call.
        customer_id: Id class — the member reference number of the guest the line is raised
            against, read from the member profile lookup before the call.
        surcharge_amount: Fixed-format class — the money the young-driver surcharge comes to, in
            USD, 2 decimal places, rounded half up to the cent, positive because it is money the
            guest owes.

    Returns:
        A confirmation sentence naming the reference number of the new priced line, the
        reservation it was raised on and the amount in USD to two decimal places. Receiving that
        sentence means the surcharge now stands on the trip and the balance has risen by it;
        anything else means no line was raised.
    """
    rid = ctx.make_id("chg_", booking_id, customer_id, surcharge_amount)
    ctx.create("trips_charges", rid, charge_id=rid, booking_id=booking_id,
               customer_id=customer_id, event_type="trips_reservation_charge_posted",
               charge_date=ctx.now()[:10], charge_amount=round(float(surcharge_amount), 2),
               charge_basis="young_driver_surcharge", quantity_units=0.0, unit_rate_amount=0.00,
               billing_period="at_booking", payment_channel="card_on_file", waiver_code="none")
    return (f"Charge line {rid} raised on reservation {booking_id} for the young-driver "
            f"surcharge: {round(float(surcharge_amount), 2):.2f} USD.")


@tool(owner="user", rw="write")
def submit_extension_request_8f69bfd6(ctx: ToolContext, booking_id: str, customer_id: str,
                                      requested_end_date: str, additional_hours: float,
                                      quoted_amount: float) -> str:
    """Let the guest ask, for themselves, to keep the vehicle on their own reservation for
    longer. The call puts one request on the extension request register against that
    reservation, carrying the new last day wanted, how much longer that is and the price the
    desk quoted for the extra time, and leaves it standing as submitted and waiting on the
    host. The reservation itself is untouched by the call: its dates, its allowance and its
    balance stay as they were, and the guest can see the request and the price they were
    quoted on it. The call has completed when the acknowledgement naming the new request comes
    back.

    Args:
        booking_id: Id class — the reference number of the guest's own trip reservation the
            request is put against, as the desk read it out from the trip booking lookup.
        customer_id: Id class — the member reference number of the guest asking, as the desk
            read it out from the member profile lookup.
        requested_end_date: Fixed-format class — the new last day of the trip being asked for,
            written as YYYY-MM-DD, a calendar date in the same time zone the trip dates are kept
            in, never a range and never blank.
        additional_hours: Fixed-format class — how much longer the vehicle is wanted for,
            measured from the return currently scheduled, in hours, 1 decimal place, positive.
        quoted_amount: Fixed-format class — the price the desk quoted for that extra time, in
            USD, 2 decimal places, rounded half up to the cent, positive.

    Returns:
        An acknowledgement sentence naming the reference number of the new request, the
        reservation it stands against, the new last day asked for and the amount quoted in USD
        to two decimal places. Receiving that sentence means the request is on the register and
        waiting on the host; anything else means nothing was lodged.
    """
    rid = ctx.make_id("ext_", booking_id, customer_id, requested_end_date, additional_hours,
                      quoted_amount)
    ctx.create("trips_extension_requests", rid, extension_request_id=rid, booking_id=booking_id,
               customer_id=customer_id, requested_end_date=requested_end_date,
               additional_hours=round(float(additional_hours), 1),
               quoted_amount=round(float(quoted_amount), 2), request_status="submitted",
               created_at=ctx.now())
    return (f"Extension request {rid} lodged against reservation {booking_id} to "
            f"{requested_end_date}, quoted at {round(float(quoted_amount), 2):.2f} USD.")

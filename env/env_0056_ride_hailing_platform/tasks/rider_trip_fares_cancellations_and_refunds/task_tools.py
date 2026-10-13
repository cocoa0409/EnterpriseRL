"""Hidden task tools for the rider_trip_fares_cancellations_and_refunds difficulty of
env_0056_ride_hailing_platform (Wayfare rider trips: fares, corrections, fare reviews and
unpaid trip charges).

Every tool here performs exactly one atomic write on the rider's trip records and is reached
only through unlock_* -> call_*; the amounts they take are worked out beforehand from the
published rules and the rider's records. No tool checks eligibility, prerequisites or amounts.
"""

from erlbench import ToolContext, tool


@tool(owner="agent", rw="write")
def adjust_fare_above_guarantee_d9a21c99(ctx: ToolContext, trip_id: str, original_charge_id: str,
                                         adjustment_amount: float) -> dict:
    """Book an upfront guarantee correction against one fare charge of a rider's completed trip.

    The support agent takes money back from a single fare charge that was billed above the
    price the rider was guaranteed. One call writes one fare adjustment entry of the
    fare-above-upfront kind on the trip, linked to the fare charge it reduces, dated today, for
    the amount given (recorded as money returned to the rider), and lowers the trip's net amount
    charged by the same amount. The rider sees the adjustment on the trip's receipt and the money
    goes back to the original payment method. A receipt with status "booked" means the entry
    exists.

    Args:
        trip_id: Id class — the trip reference number of the completed trip whose fare is being
            corrected, as returned by the trip lookup.
        original_charge_id: Id class — the charge reference number of the fare charge being
            reduced, as returned by the trip charge lookup for that trip.
        adjustment_amount: Fixed-format class — the amount taken back from the fare charge, in
            USD as a positive number with 2 decimal places, rounded half up to the cent; the entry
            records it as a negative movement on the rider's charges.

    Returns:
        A dict receipt: trip_charge_id (string, reference number of the new fare adjustment
        entry), trip_id (string, the trip corrected), original_charge_id (string, the fare charge
        reduced), amount (number, the signed entry amount in USD, negative, 2 decimal places),
        net_charged (number, the trip's net amount charged after the entry, USD, 2 decimal
        places) and status (string, "booked" when the entry was written).
    """
    trip = ctx.find("trips", trip_id=trip_id)
    customer_id = trip[0].get("customer_id") if trip else None
    amount = -round(float(adjustment_amount), 2)
    rid = ctx.make_id("tch_", trip_id, original_charge_id, adjustment_amount)
    ctx.create("trip_charges", rid, trip_charge_id=rid, trip_id=trip_id, customer_id=customer_id,
               event_type="trip_fare_adjustment", charge_date=ctx.now()[:10], charged_at=ctx.now(),
               amount=amount, member_discount_amount=0.0, member_credit_applied=0.0,
               payment_source="none", fare_basis="none", wait_minutes_billed=0,
               toll_facility="none", airport_code="none", original_charge_id=original_charge_id,
               adjustment_reason="fare_above_upfront", waiver_basis="none", waived_fee_type="none",
               settlement_method="none")
    net = None
    if trip:
        net = round(float(trip[0].get("net_charged") or 0) + amount, 2)
        ctx.update("trips", trip_id, net_charged=net)
    return {"trip_charge_id": rid, "trip_id": trip_id, "original_charge_id": original_charge_id,
            "amount": amount, "net_charged": net, "status": "booked"}


@tool(owner="user", rw="write")
def submit_dropoff_fare_review_f18c58a7(ctx: ToolContext, trip_id: str, original_charge_id: str,
                                        requested_amount: float) -> dict:
    """File a wrong drop-off fare review from the rider's own app, for one fare charge.

    The rider themselves sends the fare review team a request to look at a trip whose driver
    ended it somewhere other than the destination asked for. One call registers one fare review
    request with the reason wrong drop-off location, in submitted status, against the disputed
    fare charge of the trip, for the amount given; it changes no charge and moves no money until
    the fare review team decides. The rider sees the request listed under the trip's help
    history. A receipt with review_status "submitted" means the request is registered.

    Args:
        trip_id: Id class — the trip reference number of the trip under review, as read out by
            the agent from the trip lookup.
        original_charge_id: Id class — the charge reference number of the fare charge disputed,
            as read out by the agent from the trip charge lookup.
        requested_amount: Fixed-format class — the review amount entered on the request, in USD
            as a positive number with 2 decimal places, rounded half up to the cent.

    Returns:
        A dict receipt: fare_review_id (string, reference number of the new fare review
        request), trip_id (string, the trip under review), trip_charge_id (string, the disputed
        fare charge), review_reason (string, always "wrong_dropoff_location"), requested_amount
        (number, USD, 2 decimal places) and review_status (string, "submitted" when registered).
    """
    trip = ctx.find("trips", trip_id=trip_id)
    customer_id = trip[0].get("customer_id") if trip else None
    rid = ctx.make_id("frv_", trip_id, original_charge_id, requested_amount)
    ctx.create("trip_fare_reviews", rid, fare_review_id=rid, customer_id=customer_id,
               trip_id=trip_id, trip_charge_id=original_charge_id,
               review_reason="wrong_dropoff_location",
               requested_amount=round(float(requested_amount), 2), review_status="submitted",
               created_at=ctx.now())
    return {"fare_review_id": rid, "trip_id": trip_id, "trip_charge_id": original_charge_id,
            "review_reason": "wrong_dropoff_location",
            "requested_amount": round(float(requested_amount), 2), "review_status": "submitted"}


@tool(owner="agent", rw="write")
def apply_detour_toll_return_b5bdaa70(ctx: ToolContext, trip_id: str, original_charge_id: str,
                                      offset_amount: float) -> dict:
    """Apply a detour toll return to a rider's unpaid fare.

    The support agent applies money Wayfare gives back for a toll caused by a driver's detour
    against the fare charge of the same trip that failed to collect. One call writes one
    settlement entry of the refund-offset kind against that unpaid fare charge, dated today, with
    the reason toll not incurred, for the amount given; the trip's unpaid amount and its net
    amount charged both drop by that amount, while the toll charge itself and the rider's card
    are left untouched. The rider sees the unpaid balance of the trip go down. A receipt with
    status "applied" means the entry exists.

    Args:
        trip_id: Id class — the trip reference number of the detoured trip, as returned by the
            trip lookup.
        original_charge_id: Id class — the charge reference number of the trip's unpaid fare
            charge the return is applied against, as returned by the trip charge lookup.
        offset_amount: Fixed-format class — the amount applied against the unpaid fare, in USD as a
            positive number with 2 decimal places, rounded half up to the cent; the entry records
            it as a negative movement on the unpaid balance.

    Returns:
        A dict receipt: trip_charge_id (string, reference number of the new settlement entry),
        trip_id (string), original_charge_id (string, the unpaid fare charge), amount (number,
        signed entry amount in USD, negative, 2 decimal places), outstanding_amount (number, the
        trip's unpaid amount after the entry, USD, 2 decimal places), net_charged (number, the
        trip's net amount charged after the entry, USD, 2 decimal places) and status (string,
        "applied" when the entry was written).
    """
    trip = ctx.find("trips", trip_id=trip_id)
    customer_id = trip[0].get("customer_id") if trip else None
    signed = -round(float(offset_amount), 2)
    rid = ctx.make_id("tst_", trip_id, original_charge_id, offset_amount)
    ctx.create("trip_charges", rid, trip_charge_id=rid, trip_id=trip_id, customer_id=customer_id,
               event_type="trip_balance_settlement", charge_date=ctx.now()[:10], charged_at=ctx.now(),
               amount=signed, member_discount_amount=0.0, member_credit_applied=0.0,
               payment_source="none", fare_basis="none", wait_minutes_billed=0, toll_facility="none",
               airport_code="none", original_charge_id=original_charge_id, adjustment_reason="toll_not_incurred",
               waiver_basis="none", waived_fee_type="none", settlement_method="refund_offset")
    outstanding = net = None
    if trip:
        outstanding = round(float(trip[0].get("outstanding_amount") or 0) + signed, 2)
        net = round(float(trip[0].get("net_charged") or 0) + signed, 2)
        ctx.update("trips", trip_id, outstanding_amount=outstanding, net_charged=net)
    return {"trip_charge_id": rid, "trip_id": trip_id, "original_charge_id": original_charge_id,
            "amount": signed, "outstanding_amount": outstanding, "net_charged": net, "status": "applied"}


@tool(owner="agent", rw="write")
def book_detour_fare_offset_50a7c54a(ctx: ToolContext, trip_id: str, original_charge_id: str,
                                     offset_amount: float) -> dict:
    """Book a detour fare correction against a rider's unpaid fare.

    The support agent reduces what a rider owes on a fare charge that failed to collect, because
    the driver lengthened the trip. One call writes one settlement entry of the refund-offset kind
    against that unpaid fare charge, dated today, with the reason route inefficiency, for the
    amount given; the trip's unpaid amount and its net amount charged both drop by that amount and
    no money moves to or from the rider's card. The rider sees the unpaid balance of the trip go
    down. A receipt with status "booked" means the entry exists.

    Args:
        trip_id: Id class — the trip reference number of the detoured trip, as returned by the
            trip lookup.
        original_charge_id: Id class — the charge reference number of the unpaid fare charge being
            corrected, as returned by the trip charge lookup.
        offset_amount: Fixed-format class — the correction applied against the unpaid fare, in USD
            as a positive number with 2 decimal places, rounded half up to the cent; the entry
            records it as a negative movement on the unpaid balance.

    Returns:
        A dict receipt: trip_charge_id (string, reference number of the new settlement entry),
        trip_id (string), original_charge_id (string, the unpaid fare charge), amount (number,
        signed entry amount in USD, negative, 2 decimal places), outstanding_amount (number, the
        trip's unpaid amount after the entry, USD, 2 decimal places), net_charged (number, the
        trip's net amount charged after the entry, USD, 2 decimal places) and status (string,
        "booked" when the entry was written).
    """
    trip = ctx.find("trips", trip_id=trip_id)
    customer_id = trip[0].get("customer_id") if trip else None
    signed = -round(float(offset_amount), 2)
    rid = ctx.make_id("tdf_", trip_id, original_charge_id, offset_amount)
    ctx.create("trip_charges", rid, trip_charge_id=rid, trip_id=trip_id, customer_id=customer_id,
               event_type="trip_balance_settlement", charge_date=ctx.now()[:10], charged_at=ctx.now(),
               amount=signed, member_discount_amount=0.0, member_credit_applied=0.0,
               payment_source="none", fare_basis="none", wait_minutes_billed=0, toll_facility="none",
               airport_code="none", original_charge_id=original_charge_id, adjustment_reason="route_inefficiency",
               waiver_basis="none", waived_fee_type="none", settlement_method="refund_offset")
    outstanding = net = None
    if trip:
        outstanding = round(float(trip[0].get("outstanding_amount") or 0) + signed, 2)
        net = round(float(trip[0].get("net_charged") or 0) + signed, 2)
        ctx.update("trips", trip_id, outstanding_amount=outstanding, net_charged=net)
    return {"trip_charge_id": rid, "trip_id": trip_id, "original_charge_id": original_charge_id,
            "amount": signed, "outstanding_amount": outstanding, "net_charged": net, "status": "booked"}


@tool(owner="agent", rw="write")
def refer_detour_delay_review_b094ef4b(ctx: ToolContext, trip_id: str, original_charge_id: str,
                                       requested_amount: float) -> dict:
    """Refer the time a rider lost to a driver's detour to the fare review team.

    The support agent registers one fare review request against the fare charge of a detoured
    trip, with the reason route inefficiency, in submitted status, for the amount given. It
    changes no charge and moves no money until the fare review team decides; the rider sees the
    request under the trip's help history. A receipt with review_status "submitted" means the
    request is registered.

    Args:
        trip_id: Id class — the trip reference number of the detoured trip, as returned by the
            trip lookup.
        original_charge_id: Id class — the charge reference number of the trip's fare charge the
            review is registered against, as returned by the trip charge lookup.
        requested_amount: Fixed-format class — the amount referred to the review team, in USD as a
            positive number with 2 decimal places, rounded half up to the cent.

    Returns:
        A dict receipt: fare_review_id (string, reference number of the new fare review
        request), trip_id (string), trip_charge_id (string, the fare charge under review),
        review_reason (string, always "route_inefficiency"), requested_amount (number, USD, 2
        decimal places) and review_status (string, "submitted" when registered).
    """
    trip = ctx.find("trips", trip_id=trip_id)
    customer_id = trip[0].get("customer_id") if trip else None
    rid = ctx.make_id("frd_", trip_id, original_charge_id, requested_amount)
    ctx.create("trip_fare_reviews", rid, fare_review_id=rid, customer_id=customer_id,
               trip_id=trip_id, trip_charge_id=original_charge_id, review_reason="route_inefficiency",
               requested_amount=round(float(requested_amount), 2), review_status="submitted",
               created_at=ctx.now())
    return {"fare_review_id": rid, "trip_id": trip_id, "trip_charge_id": original_charge_id,
            "review_reason": "route_inefficiency",
            "requested_amount": round(float(requested_amount), 2), "review_status": "submitted"}


@tool(owner="user", rw="write")
def pay_unpaid_fare_new_card_1dc475f0(ctx: ToolContext, trip_id: str, original_charge_id: str,
                                      payment_amount: float) -> dict:
    """Pay toward a fare that failed to collect, with a payment method newly added in the app.

    The rider themselves pays an amount toward one unpaid fare charge of their trip using the
    card they have just added. One call charges that card and writes one settlement entry of the
    new-payment-method kind against the unpaid fare charge, dated today, for the amount given; the
    trip's unpaid amount drops by that amount. The rider sees the payment confirmation and the
    trip's remaining unpaid amount. A receipt with status "paid" means the payment went through.

    Args:
        trip_id: Id class — the trip reference number of the trip with the unpaid fare, as read
            out by the agent from the trip lookup.
        original_charge_id: Id class — the charge reference number of the unpaid fare charge, as
            read out by the agent from the trip charge lookup.
        payment_amount: Fixed-format class — the amount paid with the new card, in USD as a
            positive number with 2 decimal places, rounded half up to the cent; the entry records
            it as a negative movement on the unpaid balance.

    Returns:
        A dict receipt: trip_charge_id (string, reference number of the new settlement entry),
        trip_id (string), original_charge_id (string, the unpaid fare charge), amount (number,
        signed entry amount in USD, negative, 2 decimal places), outstanding_amount (number, the
        trip's unpaid amount left after the payment, USD, 2 decimal places) and status (string,
        "paid" when the payment went through).
    """
    trip = ctx.find("trips", trip_id=trip_id)
    customer_id = trip[0].get("customer_id") if trip else None
    signed = -round(float(payment_amount), 2)
    rid = ctx.make_id("tnp_", trip_id, original_charge_id, payment_amount)
    ctx.create("trip_charges", rid, trip_charge_id=rid, trip_id=trip_id, customer_id=customer_id,
               event_type="trip_balance_settlement", charge_date=ctx.now()[:10], charged_at=ctx.now(),
               amount=signed, member_discount_amount=0.0, member_credit_applied=0.0,
               payment_source="none", fare_basis="none", wait_minutes_billed=0, toll_facility="none",
               airport_code="none", original_charge_id=original_charge_id, adjustment_reason="none",
               waiver_basis="none", waived_fee_type="none", settlement_method="new_payment_method")
    outstanding = net = None
    if trip:
        outstanding = round(float(trip[0].get("outstanding_amount") or 0) + signed, 2)
        ctx.update("trips", trip_id, outstanding_amount=outstanding)
    return {"trip_charge_id": rid, "trip_id": trip_id, "original_charge_id": original_charge_id,
            "amount": signed, "outstanding_amount": outstanding, "status": "paid"}

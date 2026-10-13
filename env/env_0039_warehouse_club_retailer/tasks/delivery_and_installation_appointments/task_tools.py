"""Hidden task tools for the delivery_and_installation_appointments difficulty of
env_0039_warehouse_club_retailer (Northgate Delivery & Installation).

Each tool lands exactly one fee entry on one delivery appointment. Amounts are worked out by the
caller from the published delivery policies; the tools never check eligibility, never aggregate
history and never refuse on business grounds.
"""

from erlbench import ToolContext, tool


@tool(owner="agent", rw="write")
def post_extended_distance_charge_120a0e6d(ctx: ToolContext, customer_id: str, delivery_id: str,
                                           service_date: str, miles_beyond_radius: int,
                                           amount: float) -> str:
    """Post an extended-distance charge on a member's delivery appointment: member services adds one
    extended-distance fee entry to the appointment for the road miles its delivery address lies beyond
    the radius the service level includes. On success the appointment's fee history shows a new
    extended-distance charge for the amount given, posted today and tied to the appointment date given,
    and the amount becomes part of the delivery fees the member pays for that appointment.

    Args:
        customer_id: Id class — the customer reference number of the member who owns the appointment, as returned by the customer lookup and shown on the appointment.
        delivery_id: Id class — the reference number of the delivery appointment being charged, as returned by the delivery appointment lookup.
        service_date: Fixed-format class — the appointment date the charge relates to, written YYYY-MM-DD (calendar date, no time or time zone); never empty.
        miles_beyond_radius: Fixed-format class — the billing units of the entry: the appointment's road miles beyond the service level's included radius, as a whole non-negative integer (format: positive integer).
        amount: Fixed-format class — the extended-distance charge to post, in USD, 2 decimal places, always positive; values are stored rounded to the cent.

    Returns:
        A dict describing the posted entry: status ("posted" on success), delivery_charge_id (the new fee
        entry's reference number, a string), delivery_id (the appointment charged), charge_type (always
        "extended_distance"), units (the miles beyond the radius recorded, an integer), amount (the
        charge in USD, a number with 2 decimal places), event_date (the posting date, YYYY-MM-DD) and
        service_date (the appointment date the charge relates to, YYYY-MM-DD).
    """
    amt = round(float(amount), 2)
    units = int(miles_beyond_radius)
    rid = ctx.make_id("dch_", customer_id, delivery_id, service_date, units, amt, "extended_distance")
    posted = ctx.now()[:10]
    ctx.create("delivery_charges", rid, delivery_charge_id=rid, delivery_id=delivery_id,
               customer_id=customer_id, event_type="delivery_service_charged",
               charge_type="extended_distance", amount=amt, event_date=posted,
               service_date=service_date, units=units, credit_reason="not_applicable",
               source_charge_id="")
    return str({"status": "posted", "delivery_charge_id": rid, "delivery_id": delivery_id,
                "charge_type": "extended_distance", "units": units, "amount": amt,
                "event_date": posted, "service_date": service_date})


@tool(owner="agent", rw="write")
def post_reschedule_fee_c618067c(ctx: ToolContext, customer_id: str, delivery_id: str,
                                 service_date: str, amount: float) -> str:
    """Post a reschedule fee on a member's delivery appointment: member services adds one reschedule
    fee entry to the appointment for moves of its delivery date that are charged. On success the
    appointment's fee history shows a new reschedule fee for the amount given, posted today and tied
    to the appointment date given, and the amount becomes part of the delivery fees the member pays
    for that appointment. The appointment's date, window and move count are not changed.

    Args:
        customer_id: Id class — the customer reference number of the member who owns the appointment, as returned by the customer lookup and shown on the appointment.
        delivery_id: Id class — the reference number of the delivery appointment being charged, as returned by the delivery appointment lookup.
        service_date: Fixed-format class — the appointment date the fee relates to, written YYYY-MM-DD (calendar date, no time or time zone); never empty.
        amount: Fixed-format class — the reschedule fee to post, in USD, 2 decimal places, always positive; values are stored rounded to the cent.

    Returns:
        A dict describing the posted entry: status ("posted" on success), delivery_charge_id (the new fee
        entry's reference number, a string), delivery_id (the appointment charged), charge_type (always
        "reschedule_fee"), units (always 1), amount (the fee in USD, a number with 2 decimal places),
        event_date (the posting date, YYYY-MM-DD) and service_date (the appointment date the fee relates
        to, YYYY-MM-DD).
    """
    amt = round(float(amount), 2)
    rid = ctx.make_id("dch_", customer_id, delivery_id, service_date, amt, "reschedule_fee")
    posted = ctx.now()[:10]
    ctx.create("delivery_charges", rid, delivery_charge_id=rid, delivery_id=delivery_id,
               customer_id=customer_id, event_type="delivery_service_charged",
               charge_type="reschedule_fee", amount=amt, event_date=posted,
               service_date=service_date, units=1, credit_reason="not_applicable",
               source_charge_id="")
    return str({"status": "posted", "delivery_charge_id": rid, "delivery_id": delivery_id,
                "charge_type": "reschedule_fee", "units": 1, "amount": amt,
                "event_date": posted, "service_date": service_date})


@tool(owner="user", rw="write")
def authorize_wall_mounting_3e376943(ctx: ToolContext, customer_id: str, delivery_id: str,
                                     service_date: str, televisions: int, amount: float) -> str:
    """The member authorizes wall mounting on their own TV delivery appointment: the member adds the
    crew's wall-mount installation for the televisions the appointment delivers and accepts its labor
    charge, which lands as one wall-mount labor entry on the appointment. On success the appointment's
    fee history shows a new wall-mount labor charge for the amount and the number of televisions
    given, posted today and tied to the appointment date given, and the crew is booked to mount those
    televisions on the delivery date.

    Args:
        customer_id: Id class — the member's own customer reference number, as read out to the member from the customer lookup by the representative.
        delivery_id: Id class — the reference number of the member's delivery appointment, as read out to the member from the delivery appointment lookup by the representative.
        service_date: Fixed-format class — the appointment date the mounting relates to, written YYYY-MM-DD (calendar date, no time or time zone); never empty.
        televisions: Fixed-format class — the billing units of the entry: the number of televisions to be mounted, as a whole positive integer (format: positive integer).
        amount: Fixed-format class — the wall-mount labor charge the member accepts, in USD, 2 decimal places, always positive; values are stored rounded to the cent.

    Returns:
        A dict describing the authorized entry: status ("authorized" on success), delivery_charge_id (the
        new fee entry's reference number, a string), delivery_id (the appointment charged), charge_type
        (always "wall_mount_labor"), units (the televisions to be mounted, an integer), amount (the charge
        in USD, a number with 2 decimal places), event_date (the posting date, YYYY-MM-DD) and service_date
        (the appointment date the mounting relates to, YYYY-MM-DD).
    """
    amt = round(float(amount), 2)
    units = int(televisions)
    rid = ctx.make_id("dch_", customer_id, delivery_id, service_date, units, amt, "wall_mount_labor")
    posted = ctx.now()[:10]
    ctx.create("delivery_charges", rid, delivery_charge_id=rid, delivery_id=delivery_id,
               customer_id=customer_id, event_type="delivery_service_charged",
               charge_type="wall_mount_labor", amount=amt, event_date=posted,
               service_date=service_date, units=units, credit_reason="not_applicable",
               source_charge_id="")
    return str({"status": "authorized", "delivery_charge_id": rid, "delivery_id": delivery_id,
                "charge_type": "wall_mount_labor", "units": units, "amount": amt,
                "event_date": posted, "service_date": service_date})


@tool(owner="agent", rw="write")
def post_installation_kit_charge_19cc3b17(ctx: ToolContext, customer_id: str, delivery_id: str,
                                          service_date: str, kits: int, amount: float) -> str:
    """Post an installation parts kit charge on a member's installation appointment: member services
    adds one installation parts kit fee entry to the appointment for the hoses, cords, vents or water
    lines the crew brings to install appliances. On success the appointment's fee history shows a new
    installation parts kit charge for the number of kits and the amount given, posted today and tied to
    the appointment date given, and the amount becomes part of the delivery fees the member pays for
    that appointment.

    Args:
        customer_id: Id class — the customer reference number of the member who owns the appointment, as returned by the customer lookup and shown on the appointment.
        delivery_id: Id class — the reference number of the installation appointment being charged, as returned by the delivery appointment lookup.
        service_date: Fixed-format class — the appointment date the charge relates to, written YYYY-MM-DD (calendar date, no time or time zone); never empty.
        kits: Fixed-format class — the billing units of the entry: the number of installation parts kits charged, as a whole positive integer (format: positive integer).
        amount: Fixed-format class — the installation parts kit charge to post, in USD, 2 decimal places, always positive; values are stored rounded to the cent.

    Returns:
        A dict describing the posted entry: status ("posted" on success), delivery_charge_id (the new fee
        entry's reference number, a string), delivery_id (the appointment charged), charge_type (always
        "installation_parts_kit"), units (the kits charged, an integer), amount (the charge in USD, a number
        with 2 decimal places), event_date (the posting date, YYYY-MM-DD) and service_date (the appointment
        date the charge relates to, YYYY-MM-DD).
    """
    amt = round(float(amount), 2)
    units = int(kits)
    rid = ctx.make_id("dch_", customer_id, delivery_id, service_date, units, amt, "installation_parts_kit")
    posted = ctx.now()[:10]
    ctx.create("delivery_charges", rid, delivery_charge_id=rid, delivery_id=delivery_id,
               customer_id=customer_id, event_type="delivery_service_charged",
               charge_type="installation_parts_kit", amount=amt, event_date=posted,
               service_date=service_date, units=units, credit_reason="not_applicable",
               source_charge_id="")
    return str({"status": "posted", "delivery_charge_id": rid, "delivery_id": delivery_id,
                "charge_type": "installation_parts_kit", "units": units, "amount": amt,
                "event_date": posted, "service_date": service_date})


@tool(owner="user", rw="write")
def authorize_haul_away_734a64e4(ctx: ToolContext, customer_id: str, delivery_id: str,
                                 service_date: str, old_items: int, amount: float) -> str:
    """The member authorizes haul-away on their own installation appointment: the member asks the
    crew to take away old appliances on the delivery date and accepts the removal charge, which lands
    as one haul-away entry on the appointment. On success the appointment's fee history shows a new
    haul-away charge for the number of old items and the amount given, posted today and tied to the
    appointment date given, and the crew is booked to remove those old items on the delivery date.

    Args:
        customer_id: Id class — the member's own customer reference number, as read out to the member from the customer lookup by the representative.
        delivery_id: Id class — the reference number of the member's installation appointment, as read out to the member from the delivery appointment lookup by the representative.
        service_date: Fixed-format class — the appointment date the removal relates to, written YYYY-MM-DD (calendar date, no time or time zone); never empty.
        old_items: Fixed-format class — the billing units of the entry: the number of old items to be taken away, as a whole positive integer (format: positive integer).
        amount: Fixed-format class — the haul-away charge the member accepts, in USD, 2 decimal places, always positive; values are stored rounded to the cent.

    Returns:
        A dict describing the authorized entry: status ("authorized" on success), delivery_charge_id (the
        new fee entry's reference number, a string), delivery_id (the appointment charged), charge_type
        (always "haul_away"), units (the old items to be removed, an integer), amount (the charge in USD, a
        number with 2 decimal places), event_date (the posting date, YYYY-MM-DD) and service_date (the
        appointment date the removal relates to, YYYY-MM-DD).
    """
    amt = round(float(amount), 2)
    units = int(old_items)
    rid = ctx.make_id("dch_", customer_id, delivery_id, service_date, units, amt, "haul_away")
    posted = ctx.now()[:10]
    ctx.create("delivery_charges", rid, delivery_charge_id=rid, delivery_id=delivery_id,
               customer_id=customer_id, event_type="delivery_service_charged",
               charge_type="haul_away", amount=amt, event_date=posted,
               service_date=service_date, units=units, credit_reason="not_applicable",
               source_charge_id="")
    return str({"status": "authorized", "delivery_charge_id": rid, "delivery_id": delivery_id,
                "charge_type": "haul_away", "units": units, "amount": amt,
                "event_date": posted, "service_date": service_date})

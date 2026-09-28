"""Hidden task tools for the ticket_changes_refunds_and_disruptions difficulty of Crestline Airways.

Each tool performs one atomic write on a ticket's service-fee ledger with the value the agent (or the
customer) has already worked out from the published ticket rules. No tool checks eligibility, status,
ownership, dedup or any prerequisite, and none computes a charge or a refund: the value passed in is the
value booked.
"""

from erlbench import ToolContext, tool


@tool(owner="agent", rw="write")
def post_same_day_change_fee_61b8e8ae(ctx: ToolContext, ticket_id: str, related_transaction_id: str,
                                       corporate_account_id: str, fee_amount: float) -> dict:
    """Post the same-day confirmed change fee owed for one same-day exchange already recorded on a ticket.

    The agent books one same-day change fee charge on the ticket's service-fee ledger, linked to the
    same-day exchange entry it is charged for, at the amount given, paid through the call center. The
    ticket's net fee charges rise by that amount and the charge becomes visible on the ticket's service
    fees straight away. One call books exactly one charge; the receipt echoes the new charge reference.

    Args:
        ticket_id: Id class — reference number of the ticket record the fee is charged on, as returned by the ticket lookup for this customer.
        related_transaction_id: Id class — reference number of the same-day exchange entry on the ticket's fare history that this fee is charged for, as returned by the fare-history lookup.
        corporate_account_id: Id class — reference number of the corporate travel agreement the ticket names, copied from the ticket record's corporate agreement field; pass "" when the ticket names no agreement.
        fee_amount: Fixed-format class — the same-day change fee charged, in USD, a non-negative number rounded to 2 decimal places (to the cent) before it is passed.

    Returns:
        A dictionary receipt: service_id (string, reference number of the new fee charge), ticket_id
        (string, the ticket charged), related_transaction_id (string, the exchange entry charged for),
        service_type (string, always same_day_change_fee), amount (number, USD to 2 decimal places, the
        fee booked), service_date (string, YYYY-MM-DD business date of the charge) and status (string,
        "posted" when the charge was booked).
    """
    amount = round(float(fee_amount), 2)
    sid = ctx.make_id("tsv_", ticket_id, related_transaction_id, corporate_account_id, amount)
    holder = ctx.find("ticket_holdings", ticket_id=ticket_id)
    customer_id = holder[0].get("customer_id", "") if holder else ""
    day = ctx.now()[:10]
    ctx.create("ticket_services", sid, service_id=sid, ticket_id=ticket_id, customer_id=customer_id,
               event_type="ticket_change_fee", service_date=day, service_type="same_day_change_fee",
               segment_number=0, segment_miles=0, seat_number="", travel_direction="", bag_tag_number="",
               bag_weight_lb=0, bag_linear_inches=0, amount=amount, sales_channel="call_center",
               related_transaction_id=related_transaction_id, refunded_service_id="",
               source_disruption_id="", fee_refund_reason="")
    return {"service_id": sid, "ticket_id": ticket_id, "related_transaction_id": related_transaction_id,
            "service_type": "same_day_change_fee", "amount": amount, "service_date": day, "status": "posted"}


@tool(owner="agent", rw="write")
def refund_seat_charge_excess_9145fc3e(ctx: ToolContext, ticket_id: str, refunded_service_id: str,
                                       source_disruption_id: str, refund_amount: float) -> dict:
    """Refund to the original payment the part of one advance seat charge that was charged in error.

    The agent books one fee-refund entry on the ticket's service-fee ledger that reverses the named
    seat charge by the amount given, with the refund ground charged_in_error; the entry carries the
    seat charge's own seat kind and flight segment. The ticket's net fee charges fall by that amount
    and the refund is visible on the ticket's service fees at once, returned to the original form of
    payment. One call books exactly one refund entry against exactly one seat charge.

    Args:
        ticket_id: Id class — reference number of the ticket record the seat charge sits on, as returned by the ticket lookup for this customer.
        refunded_service_id: Id class — reference number of the seat charge entry being partly or wholly refunded, as returned by the service-fee lookup for the ticket.
        source_disruption_id: Id class — reference number of the irregular-operations record the refund rests on, as returned by the irregular-operations lookup; pass "" when the refund rests on no such record, as a charge made in error does.
        refund_amount: Fixed-format class — the amount refunded against the seat charge, in USD, a non-negative number rounded to 2 decimal places (to the cent) before it is passed.

    Returns:
        A dictionary receipt: service_id (string, reference number of the new refund entry), ticket_id
        (string), refunded_service_id (string, the seat charge reversed), service_type (string, the seat
        kind of the charge refunded), segment_number (integer, the flight segment of that charge),
        amount (number, USD to 2 decimal places, the amount refunded), fee_refund_reason (string, always
        charged_in_error), service_date (string, YYYY-MM-DD) and status (string, "refunded" when booked).
    """
    amount = round(float(refund_amount), 2)
    sid = ctx.make_id("tsv_", ticket_id, refunded_service_id, source_disruption_id, amount)
    holder = ctx.find("ticket_holdings", ticket_id=ticket_id)
    customer_id = holder[0].get("customer_id", "") if holder else ""
    charge = ctx.find("ticket_services", service_id=refunded_service_id)
    kind = charge[0].get("service_type", "") if charge else ""
    segment = charge[0].get("segment_number", 0) if charge else 0
    day = ctx.now()[:10]
    ctx.create("ticket_services", sid, service_id=sid, ticket_id=ticket_id, customer_id=customer_id,
               event_type="ticket_fee_refund", service_date=day, service_type=kind,
               segment_number=segment, segment_miles=0, seat_number="", travel_direction="",
               bag_tag_number="", bag_weight_lb=0, bag_linear_inches=0, amount=amount, sales_channel="",
               related_transaction_id="", refunded_service_id=refunded_service_id,
               source_disruption_id=source_disruption_id, fee_refund_reason="charged_in_error")
    return {"service_id": sid, "ticket_id": ticket_id, "refunded_service_id": refunded_service_id,
            "service_type": kind, "segment_number": segment, "amount": amount,
            "fee_refund_reason": "charged_in_error", "service_date": day, "status": "refunded"}


@tool(owner="user", rw="write")
def purchase_first_upgrade_fa17fda8(ctx: ToolContext, ticket_id: str, segment_number: int,
                                    segment_miles: int, upgrade_fee: float) -> dict:
    """Buy, as the ticket holder, a paid upgrade into First on one unflown flight segment of your ticket.

    The customer confirms and pays for the upgrade in person with the card on the booking; one upgrade
    purchase entry of kind upgrade_first is booked on the ticket's service-fee ledger for the segment
    named, at the price given, and the passenger's seat on that segment moves into the First cabin. The
    ticket's net fee charges rise by the price paid and the purchase shows on the ticket's service fees
    at once. One call buys exactly one segment.

    Args:
        ticket_id: Id class — reference number of the ticket record being upgraded, as read out by the agent from the ticket lookup.
        segment_number: Fixed-format class — position of the flight segment on the ticket being upgraded, an integer >= 0 (the first flight is 1), as read out by the agent.
        segment_miles: Fixed-format class — great-circle distance of that segment, an integer number of statute miles, as read out by the agent from the segment's service entries.
        upgrade_fee: Fixed-format class — the upgrade price paid, in USD, a non-negative number rounded to 2 decimal places (to the cent) before it is passed.

    Returns:
        A dictionary receipt: service_id (string, reference number of the upgrade purchase), ticket_id
        (string), segment_number (integer, the segment upgraded), service_type (string, always
        upgrade_first), amount (number, USD to 2 decimal places, the price paid), service_date (string,
        YYYY-MM-DD) and status (string, "purchased" when the upgrade was booked).
    """
    amount = round(float(upgrade_fee), 2)
    seg = int(segment_number)
    miles = int(segment_miles)
    sid = ctx.make_id("tsv_", ticket_id, seg, miles, amount)
    holder = ctx.find("ticket_holdings", ticket_id=ticket_id)
    customer_id = holder[0].get("customer_id", "") if holder else ""
    day = ctx.now()[:10]
    ctx.create("ticket_services", sid, service_id=sid, ticket_id=ticket_id, customer_id=customer_id,
               event_type="ticket_upgrade_purchase", service_date=day, service_type="upgrade_first",
               segment_number=seg, segment_miles=miles, seat_number="", travel_direction="",
               bag_tag_number="", bag_weight_lb=0, bag_linear_inches=0, amount=amount,
               sales_channel="online", related_transaction_id="", refunded_service_id="",
               source_disruption_id="", fee_refund_reason="")
    return {"service_id": sid, "ticket_id": ticket_id, "segment_number": seg, "service_type": "upgrade_first",
            "amount": amount, "service_date": day, "status": "purchased"}


@tool(owner="agent", rw="write")
def post_change_fee_ac050962(ctx: ToolContext, ticket_id: str, related_transaction_id: str, corporate_account_id: str,
                             fee_amount: float) -> dict:
    """Post the change fee owed for one voluntary (standard) exchange already recorded on a ticket.

    The agent books one change fee charge on the ticket's service-fee ledger, at the itinerary level
    (segment 0), linked to the standard exchange entry it is charged for, at the amount given, paid
    through the call center. The ticket's net fee charges rise by that amount and the charge shows on the
    ticket's service fees at once. One call books exactly one charge; the receipt echoes the new charge.

    Args:
        ticket_id: Id class — reference number of the ticket record the fee is charged on, as returned by the ticket lookup.
        related_transaction_id: Id class — reference number of the standard exchange entry on the ticket's fare history that this fee is charged for, as returned by the fare-history lookup.
        corporate_account_id: Id class — reference number of the corporate travel agreement the ticket names, copied from the ticket record's corporate agreement field; pass "" when the ticket names no agreement.
        fee_amount: Fixed-format class — the change fee charged, in USD, a non-negative number rounded to 2 decimal places (to the cent) before it is passed.

    Returns:
        A dictionary receipt: service_id (string, reference number of the new fee charge), ticket_id
        (string), related_transaction_id (string, the exchange entry charged for), service_type (string,
        always change_fee), amount (number, USD to 2 decimal places, the fee booked), service_date (string,
        YYYY-MM-DD) and status (string, "posted" when the charge was booked).
    """
    amount = round(float(fee_amount), 2)
    sid = ctx.make_id("tsv_", ticket_id, related_transaction_id, corporate_account_id, amount)
    holder = ctx.find("ticket_holdings", ticket_id=ticket_id)
    customer_id = holder[0].get("customer_id", "") if holder else ""
    day = ctx.now()[:10]
    ctx.create("ticket_services", sid, service_id=sid, ticket_id=ticket_id, customer_id=customer_id,
               event_type="ticket_change_fee", service_date=day, service_type="change_fee", segment_number=0,
               segment_miles=0, seat_number="", travel_direction="", bag_tag_number="", bag_weight_lb=0,
               bag_linear_inches=0, amount=amount, sales_channel="call_center",
               related_transaction_id=related_transaction_id, refunded_service_id="", source_disruption_id="",
               fee_refund_reason="")
    return {"service_id": sid, "ticket_id": ticket_id, "related_transaction_id": related_transaction_id,
            "service_type": "change_fee", "amount": amount, "service_date": day, "status": "posted"}


@tool(owner="agent", rw="write")
def post_bag_sequence_charge_b2992c63(ctx: ToolContext, ticket_id: str, bag_tag_number: str, corporate_account_id: str,
                                      bag_sequence_position: int, charge_amount: float) -> dict:
    """Post the checked-bag charge for one tagged bag whose place in the bag count has not yet been charged.

    The agent books one bag charge on the ticket's service-fee ledger for the tagged bag, recorded as the
    first, second or third-and-later bag according to the position given, carrying the bag's travel
    direction, flight segment, weight and size as already recorded for that tag, at the amount given,
    paid through the call center. The ticket's net fee charges rise by that amount and the charge shows on
    the ticket's service fees at once. One call books exactly one bag charge.

    Args:
        ticket_id: Id class — reference number of the ticket record the bag travels on, as returned by the ticket lookup.
        bag_tag_number: Fixed-format class — the bag tag of the bag being charged, CR followed by 6 digits, copied from the ticket's service-fee entries for that bag.
        corporate_account_id: Id class — reference number of the corporate travel agreement the ticket names, copied from the ticket record's corporate agreement field; pass "" when the ticket names no agreement.
        bag_sequence_position: Fixed-format class — the bag's place in the bag count, an integer of 1 or more (1 books a first bag, 2 a second bag, 3 or more a third-and-later bag).
        charge_amount: Fixed-format class — the bag charge, in USD, a non-negative number rounded to 2 decimal places (to the cent) before it is passed.

    Returns:
        A dictionary receipt: service_id (string, reference number of the new bag charge), ticket_id
        (string), bag_tag_number (string), service_type (string, first_bag, second_bag or third_bag),
        travel_direction (string, outbound or return), amount (number, USD to 2 decimal places, the charge
        booked), service_date (string, YYYY-MM-DD) and status (string, "posted" when the charge was booked).
    """
    amount = round(float(charge_amount), 2)
    position = int(bag_sequence_position)
    kind = "first_bag" if position <= 1 else ("second_bag" if position == 2 else "third_bag")
    sid = ctx.make_id("tsv_", ticket_id, bag_tag_number, corporate_account_id, position, amount)
    holder = ctx.find("ticket_holdings", ticket_id=ticket_id)
    customer_id = holder[0].get("customer_id", "") if holder else ""
    tagged = ctx.find("ticket_services", ticket_id=ticket_id, bag_tag_number=bag_tag_number)
    ref = tagged[0] if tagged else {}
    day = ctx.now()[:10]
    ctx.create("ticket_services", sid, service_id=sid, ticket_id=ticket_id, customer_id=customer_id,
               event_type="ticket_bag_charge", service_date=day, service_type=kind,
               segment_number=ref.get("segment_number", 0), segment_miles=0, seat_number="",
               travel_direction=ref.get("travel_direction", ""), bag_tag_number=bag_tag_number,
               bag_weight_lb=ref.get("bag_weight_lb", 0), bag_linear_inches=ref.get("bag_linear_inches", 0),
               amount=amount, sales_channel="call_center", related_transaction_id="", refunded_service_id="",
               source_disruption_id="", fee_refund_reason="")
    return {"service_id": sid, "ticket_id": ticket_id, "bag_tag_number": bag_tag_number, "service_type": kind,
            "travel_direction": ref.get("travel_direction", ""), "amount": amount, "service_date": day,
            "status": "posted"}


@tool(owner="agent", rw="write")
def post_bag_weight_charge_02a99017(ctx: ToolContext, ticket_id: str, bag_tag_number: str, corporate_account_id: str,
                                    charge_component: str, charge_amount: float) -> dict:
    """Post the weight or size charge for one tagged checked bag that carries no such charge yet.

    The agent books one weight-or-size charge entry on the ticket's service-fee ledger for the tagged bag,
    of the component named, carrying the bag's travel direction, flight segment, weight and size as
    already recorded for that tag, at the amount given, paid through the call center. The ticket's net
    fee charges rise by that amount and the charge shows on the ticket's service fees at once. One call
    books exactly one component for one bag.

    Args:
        ticket_id: Id class — reference number of the ticket record the bag travels on, as returned by the ticket lookup.
        bag_tag_number: Fixed-format class — the bag tag of the bag being charged, CR followed by 6 digits, copied from the ticket's service-fee entries for that bag.
        corporate_account_id: Id class — reference number of the corporate travel agreement the ticket names, copied from the ticket record's corporate agreement field; pass "" when the ticket names no agreement.
        charge_component: Enum class — the component booked: overweight_bag when the charge recorded is the bag's weight charge (the weight charge is the higher of the two, or the bag is within the size limit); oversize_bag when the charge recorded is the bag's size charge (the size charge is the higher of the two).
        charge_amount: Fixed-format class — the weight-or-size charge, in USD, a non-negative number rounded to 2 decimal places (to the cent) before it is passed.

    Returns:
        A dictionary receipt: service_id (string, reference number of the new charge), ticket_id (string),
        bag_tag_number (string), service_type (string, overweight_bag or oversize_bag), amount (number, USD
        to 2 decimal places, the charge booked), service_date (string, YYYY-MM-DD) and status (string,
        "posted" when the charge was booked).
    """
    amount = round(float(charge_amount), 2)
    component = "oversize_bag" if charge_component == "oversize_bag" else "overweight_bag"
    sid = ctx.make_id("tsv_", ticket_id, bag_tag_number, corporate_account_id, component, amount)
    holder = ctx.find("ticket_holdings", ticket_id=ticket_id)
    customer_id = holder[0].get("customer_id", "") if holder else ""
    tagged = ctx.find("ticket_services", ticket_id=ticket_id, bag_tag_number=bag_tag_number)
    ref = tagged[0] if tagged else {}
    day = ctx.now()[:10]
    ctx.create("ticket_services", sid, service_id=sid, ticket_id=ticket_id, customer_id=customer_id,
               event_type="ticket_bag_charge", service_date=day, service_type=component,
               segment_number=ref.get("segment_number", 0), segment_miles=0, seat_number="",
               travel_direction=ref.get("travel_direction", ""), bag_tag_number=bag_tag_number,
               bag_weight_lb=ref.get("bag_weight_lb", 0), bag_linear_inches=ref.get("bag_linear_inches", 0),
               amount=amount, sales_channel="call_center", related_transaction_id="", refunded_service_id="",
               source_disruption_id="", fee_refund_reason="")
    return {"service_id": sid, "ticket_id": ticket_id, "bag_tag_number": bag_tag_number, "service_type": component,
            "amount": amount, "service_date": day, "status": "posted"}


@tool(owner="user", rw="write")
def purchase_premium_economy_upgrade_2477ee45(ctx: ToolContext, ticket_id: str, segment_number: int,
                                              upgrade_fee: float) -> dict:
    """Buy, as the ticket holder, a paid upgrade into Premium Economy on one unflown flight segment of a ticket.

    The ticket holder (for a company-held ticket, the company's travel manager) confirms and pays for the
    upgrade in person with the holder's card; one upgrade purchase entry of kind upgrade_premium_economy is
    booked on the ticket's service-fee ledger for the segment named, at the price given, and the
    passenger's seat on that segment moves into the Premium Economy cabin. The ticket's net fee charges
    rise by the price paid and the purchase shows on the ticket's service fees at once. One call buys
    exactly one segment.

    Args:
        ticket_id: Id class — reference number of the ticket record being upgraded, as read out by the agent from the ticket lookup.
        segment_number: Fixed-format class — position of the flight segment on the ticket being upgraded, an integer >= 0 (the first flight is 1), as read out by the agent.
        upgrade_fee: Fixed-format class — the upgrade price paid, in USD, a non-negative number rounded to 2 decimal places (to the cent) before it is passed.

    Returns:
        A dictionary receipt: service_id (string, reference number of the upgrade purchase), ticket_id
        (string), segment_number (integer, the segment upgraded), service_type (string, always
        upgrade_premium_economy), amount (number, USD to 2 decimal places, the price paid), service_date
        (string, YYYY-MM-DD) and status (string, "purchased" when the upgrade was booked).
    """
    amount = round(float(upgrade_fee), 2)
    seg = int(segment_number)
    sid = ctx.make_id("tsv_", ticket_id, seg, amount)
    holder = ctx.find("ticket_holdings", ticket_id=ticket_id)
    customer_id = holder[0].get("customer_id", "") if holder else ""
    day = ctx.now()[:10]
    ctx.create("ticket_services", sid, service_id=sid, ticket_id=ticket_id, customer_id=customer_id,
               event_type="ticket_upgrade_purchase", service_date=day, service_type="upgrade_premium_economy",
               segment_number=seg, segment_miles=0, seat_number="", travel_direction="", bag_tag_number="",
               bag_weight_lb=0, bag_linear_inches=0, amount=amount, sales_channel="online",
               related_transaction_id="", refunded_service_id="", source_disruption_id="", fee_refund_reason="")
    return {"service_id": sid, "ticket_id": ticket_id, "segment_number": seg,
            "service_type": "upgrade_premium_economy", "amount": amount, "service_date": day, "status": "purchased"}

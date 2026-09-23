"""Hidden task tools for the Northbeam Returns and Restocking desk.

Each tool performs one atomic write on the returns records and nothing else: it books the
value the agent has already worked out from the published rules and the customer's records.
No tool aggregates history, judges eligibility, or refuses because some other entry is not
yet on the record.
"""

from erlbench import ToolContext, tool


@tool(owner="agent", rw="write")
def issue_collection_booking_70222685(ctx: ToolContext, return_authorization_id: str,
                                      booking_open_days: int, carrier_name: str) -> str:
    """Book the carrier that is to bring a returned item back and put the booking on the return.

    One call adds a collection booking entry to the return's history: the carrier that will move
    the item, a tracking reference the retailer issues for it, the day the booking was made and
    the last day the booking may still be used. The customer can quote the tracking reference to
    the carrier from that moment, and the booking shows on the return alongside everything else
    booked against it. The return itself keeps its current state; only the new entry appears.

    Args:
        return_authorization_id: Id class — the reference number of the return authorisation the
            collection belongs to, read from the return authorisation record retrieved for the
            customer before the call.
        booking_open_days: Fixed-format class — how long the booking stays usable, as a whole
            number of days counted from today, which fixes the last day it may be used; a plain
            integer with no unit suffix and no decimal part, never negative, and 0 means the
            booking may be used only today.
        carrier_name: Enum class — who is to move the item back, exactly one of:
            retailer_van, the retailer's own crew collects the item from the customer's address;
            national_parcel, the item travels back through the parcel network on a label;
            regional_freight, a freight crew collects a palletised or large appliance item;
            customer_delivered, the customer brings the item to a store counter themselves.

    Returns:
        A confirmation sentence naming the collection booking entry reference that was created,
        the carrier recorded on it, the tracking reference issued for the movement, and the last
        day the booking may be used as YYYY-MM-DD. The sentence appearing at all means the entry
        was written and is visible on the return's history from now on.
    """
    def _civil_from_days(z):
        z += 719468
        era = (z if z >= 0 else z - 146096) // 146097
        doe = z - era * 146097
        yoe = (doe - doe // 1460 + doe // 36524 - doe // 146096) // 365
        y = yoe + era * 400
        doy = doe - (365 * yoe + yoe // 4 - yoe // 100)
        mp = (5 * doy + 2) // 153
        d = doy - (153 * mp + 2) // 5 + 1
        m = mp + (3 if mp < 10 else -9)
        return f"{y + (1 if m <= 2 else 0):04d}-{m:02d}-{d:02d}"

    def _days_from_civil(ymd):
        y, m, d = (int(part) for part in str(ymd)[:10].split("-"))
        y -= 1 if m <= 2 else 0
        era = y // 400
        yoe = y - era * 400
        doy = (153 * (m + (-3 if m > 2 else 9)) + 2) // 5 + d - 1
        doe = yoe * 365 + yoe // 4 - yoe // 100 + doy
        return era * 146097 + doe - 719468

    today = ctx.now()[:10]
    rows = ctx.find("return_authorizations", return_authorization_id=return_authorization_id)
    rma = rows[0] if rows else {}
    expiry = _civil_from_days(_days_from_civil(today) + int(booking_open_days))
    rid = ctx.make_id("rev_", return_authorization_id, booking_open_days, carrier_name)
    tracking = ctx.make_id("NBR", return_authorization_id, carrier_name, length=10).upper()
    ctx.create("return_events", rid, return_event_id=rid,
               return_authorization_id=return_authorization_id,
               customer_id=rma.get("customer_id"),
               event_type="returns_shipping_label_issue",
               order_line_reference=rma.get("order_line_reference"),
               carrier_name=carrier_name, tracking_reference=tracking,
               label_expiry_date=expiry, event_date=today, channel="phone",
               tier_at_event=rma.get("variant_name"))
    return (f"Collection booking {rid} recorded with {carrier_name}; tracking reference {tracking}; "
            f"usable up to and including {expiry}.")


@tool(owner="user", rw="write")
def confirm_collection_slot_e0893723(ctx: ToolContext, return_authorization_id: str,
                                     pickup_notice_days: int, pickup_window: str) -> str:
    """Take the customer's own confirmation of the day and part-day their returned item is to be
    collected, and put that confirmation on the return.

    One call raises a collection request against the return holding the day the customer has
    agreed to, the part of the day they have chosen, and their confirmation of it, with no moves
    recorded against it yet. From that moment the collection stands as confirmed by the customer
    rather than pending, and the customer can see the day and part-day they agreed to on the
    return. Only the customer may make this confirmation.

    Args:
        return_authorization_id: Id class — the reference number of the return authorisation the
            collection belongs to, read from the return authorisation record retrieved for the
            customer before the call.
        pickup_notice_days: Fixed-format class — the notice the collection is booked at, as a
            whole number of days counted from today, which fixes the day the crew is to come; a
            plain integer with no unit suffix and no decimal part, never negative, and 0 means
            the collection is agreed for today.
        pickup_window: Enum class — the part of the day the customer has agreed to, exactly one of
            these four values. morning, the crew comes before midday; afternoon, the crew comes
            after midday; all_day, the customer will be in all day and takes whichever slot the
            crew has; business_hours, a business address where the crew may come any time the
            premises are open.

    Returns:
        A confirmation sentence naming the collection request reference that was created, the day
        agreed as YYYY-MM-DD, the part of the day chosen, and that the customer has confirmed it.
        The sentence appearing at all means the confirmation was recorded against the return.
    """
    def _civil_from_days(z):
        z += 719468
        era = (z if z >= 0 else z - 146096) // 146097
        doe = z - era * 146097
        yoe = (doe - doe // 1460 + doe // 36524 - doe // 146096) // 365
        y = yoe + era * 400
        doy = doe - (365 * yoe + yoe // 4 - yoe // 100)
        mp = (5 * doy + 2) // 153
        d = doy - (153 * mp + 2) // 5 + 1
        m = mp + (3 if mp < 10 else -9)
        return f"{y + (1 if m <= 2 else 0):04d}-{m:02d}-{d:02d}"

    def _days_from_civil(ymd):
        y, m, d = (int(part) for part in str(ymd)[:10].split("-"))
        y -= 1 if m <= 2 else 0
        era = y // 400
        yoe = y - era * 400
        doy = (153 * (m + (-3 if m > 2 else 9)) + 2) // 5 + d - 1
        doe = yoe * 365 + yoe // 4 - yoe // 100 + doy
        return era * 146097 + doe - 719468

    today = ctx.now()[:10]
    rows = ctx.find("return_authorizations", return_authorization_id=return_authorization_id)
    rma = rows[0] if rows else {}
    pickup_day = _civil_from_days(_days_from_civil(today) + int(pickup_notice_days))
    rid = ctx.make_id("rpr_", return_authorization_id, pickup_notice_days, pickup_window)
    ctx.create("return_pickup_requests", rid, return_pickup_request_id=rid,
               customer_id=rma.get("customer_id"),
               return_authorization_id=return_authorization_id,
               requested_pickup_date=pickup_day, pickup_window=pickup_window,
               customer_confirmation="confirmed_by_customer", reschedule_count=0,
               created_at=ctx.now())
    return (f"Collection request {rid} confirmed by the customer for {pickup_day} "
            f"({pickup_window}).")


@tool(owner="agent", rw="write")
def charge_restocking_fee_677c7b7a(ctx: ToolContext, return_authorization_id: str,
                                   restocking_fee_amount: float, inspection_grade: str) -> str:
    """Charge a restocking fee against a return and raise what the customer owes on it by that amount.

    One call adds a restocking fee entry to the return's history, recorded as the restocking fee
    component of the settlement and carrying the condition the item was graded at, and raises the
    restocking fee still outstanding on the return by the amount charged. The customer can see the
    fee and the grade it rests on against their return from that moment, and the return's own
    outstanding figure moves with it. The return keeps its current state.

    Args:
        return_authorization_id: Id class — the reference number of the return authorisation the fee
            is charged against, read from the return authorisation record retrieved for the customer
            before the call.
        restocking_fee_amount: Fixed-format class — the fee being charged, in USD to 2 decimal
            places, always positive, given to the cent with at most two decimal places and never
            carrying a currency symbol or thousands separator.
        inspection_grade: Enum class — the condition the item was graded at, which the fee is
            recorded against, exactly one of these seven values. as_new_sealed, the packaging was
            never opened; open_box_complete, the item was opened and everything that belongs in the
            box came back; open_box_incomplete, the item was opened and something is missing from
            the box; damaged_by_customer, the item carries damage the customer caused;
            defective_on_arrival, the item failed or was damaged when it reached the customer;
            not_as_described, the item is not what the order said it was; beyond_economic_repair,
            the item cannot be put right for less than it is worth.

    Returns:
        A confirmation sentence naming the restocking fee entry reference that was created, the
        amount charged in USD to two decimal places, the grade it was recorded against and the
        restocking fee now outstanding on the return. The sentence appearing at all means the entry
        was written and the outstanding figure has moved.
    """
    today = ctx.now()[:10]
    rows = ctx.find("return_authorizations", return_authorization_id=return_authorization_id)
    rma = rows[0] if rows else {}
    amount = round(float(restocking_fee_amount), 2)
    outstanding = round(float(rma.get("restocking_fee_outstanding") or 0) + amount, 2)
    rid = ctx.make_id("rev_", return_authorization_id, restocking_fee_amount, inspection_grade)
    ctx.create("return_events", rid, return_event_id=rid,
               return_authorization_id=return_authorization_id,
               customer_id=rma.get("customer_id"),
               event_type="returns_restocking_fee_charge",
               order_line_reference=rma.get("order_line_reference"),
               restocking_fee_amount=amount, settlement_component="restocking_fee",
               inspection_grade=inspection_grade, event_date=today, channel="phone",
               tier_at_event=rma.get("variant_name"))
    ctx.update("return_authorizations", return_authorization_id,
               restocking_fee_outstanding=outstanding)
    return (f"Restocking fee entry {rid} charged at {amount:.2f} USD on grade {inspection_grade}; "
            f"restocking fee outstanding on the return is now {outstanding:.2f} USD.")


@tool(owner="agent", rw="write")
def waive_restocking_fee_47bbe442(ctx: ToolContext, return_authorization_id: str,
                                  waived_fee_amount: float, fee_waiver_reason: str) -> str:
    """Relieve part or all of a restocking fee standing against a return and lower what the customer
    owes on it by that amount.

    One call adds a waiver entry to the return's history carrying the amount relieved and the ground
    it rests on, and lowers the restocking fee still outstanding on the return by that amount. The
    customer can see what was taken off and why against their return from that moment, and the
    return's own outstanding figure moves with it. The return keeps its current state and the fee
    entry it relieves is left as it stands.

    Args:
        return_authorization_id: Id class — the reference number of the return authorisation whose
            fee is being relieved, read from the return authorisation record retrieved for the
            customer before the call.
        waived_fee_amount: Fixed-format class — the amount of the fee being relieved, in USD to 2
            decimal places, always positive, given to the cent with at most two decimal places and never
            carrying a currency symbol or thousands separator.
        fee_waiver_reason: Enum class — the ground the relief rests on, exactly one of these six
            values. defective_item, the item was graded as having failed or been damaged before the
            customer got it; retailer_error, the retailer sent or handled the wrong thing;
            membership_benefit, the customer's Circle membership relieves the fee; goodwill, the
            relief is given as a gesture with no other ground; business_contract_term, a business
            contract term provides for it; none, no ground is recorded.

    Returns:
        A confirmation sentence naming the waiver entry reference that was created, the amount
        relieved in USD to two decimal places, the ground recorded and the restocking fee now
        outstanding on the return. The sentence appearing at all means the entry was written and the
        outstanding figure has moved.
    """
    today = ctx.now()[:10]
    rows = ctx.find("return_authorizations", return_authorization_id=return_authorization_id)
    rma = rows[0] if rows else {}
    amount = round(float(waived_fee_amount), 2)
    outstanding = round(float(rma.get("restocking_fee_outstanding") or 0) - amount, 2)
    rid = ctx.make_id("rev_", return_authorization_id, waived_fee_amount, fee_waiver_reason)
    ctx.create("return_events", rid, return_event_id=rid,
               return_authorization_id=return_authorization_id,
               customer_id=rma.get("customer_id"),
               event_type="returns_restocking_fee_waive",
               order_line_reference=rma.get("order_line_reference"),
               restocking_fee_amount=amount, fee_waiver_reason=fee_waiver_reason,
               event_date=today, channel="phone", tier_at_event=rma.get("variant_name"))
    ctx.update("return_authorizations", return_authorization_id,
               restocking_fee_outstanding=outstanding)
    return (f"Waiver entry {rid} recorded relieving {amount:.2f} USD on the ground "
            f"{fee_waiver_reason}; restocking fee outstanding on the return is now "
            f"{outstanding:.2f} USD.")


@tool(owner="user", rw="write")
def accept_exchange_item_1cf629c9(ctx: ToolContext, return_authorization_id: str,
                                  price_difference_amount: float, exchange_sku: str) -> str:
    """Take the customer's own acceptance of a replacement item in place of money back, and put the
    exchange on the return with the difference coming back to them.

    One call adds an exchange entry to the return's history naming the stock number going out to the
    customer, an exchange order reference the retailer issues for it and the difference being
    returned to the customer on the swap, and marks the return as taking a replacement rather than
    money. From that moment the customer can see that they have taken the replacement rather than the
    money, and what is coming back to them alongside it. Only the
    customer may accept an exchange, since it disposes of what they are owed on the return.

    Args:
        return_authorization_id: Id class — the reference number of the return authorisation being
            settled by the swap, read from the return authorisation record retrieved for the
            customer before the call.
        price_difference_amount: Fixed-format class — the difference coming back to the customer on
            the swap, in USD to 2 decimal places, never negative, given to the cent with at most two
            decimal places and never carrying a currency symbol or thousands separator; 0.00 where
            nothing comes back.
        exchange_sku: Verbatim class — the stock number of the item going out to the customer, copied
            character for character from the stock number shown on the return authorisation record,
            preserving its wording, digits, letters, case and punctuation exactly, with no
            translation, normalisation, summarising, addition or deletion (verbatim).

    Returns:
        A confirmation sentence naming the exchange entry reference that was created, the stock
        number going out, the exchange order reference issued for it and the difference returned in
        USD to two decimal places. The sentence appearing at all means the exchange was recorded
        against the return.
    """
    today = ctx.now()[:10]
    rows = ctx.find("return_authorizations", return_authorization_id=return_authorization_id)
    rma = rows[0] if rows else {}
    amount = round(float(price_difference_amount), 2)
    rid = ctx.make_id("rev_", return_authorization_id, price_difference_amount, exchange_sku)
    reference = ctx.make_id("NBX", return_authorization_id, exchange_sku, length=9).upper()
    ctx.create("return_events", rid, return_event_id=rid,
               return_authorization_id=return_authorization_id,
               customer_id=rma.get("customer_id"),
               event_type="returns_exchange_issue",
               order_line_reference=rma.get("order_line_reference"),
               exchange_sku=exchange_sku, exchange_reference=reference,
               refund_amount=amount, event_date=today, channel="phone",
               tier_at_event=rma.get("variant_name"))
    ctx.update("return_authorizations", return_authorization_id, exchange_flag=True)
    return (f"Exchange entry {rid} recorded: {exchange_sku} going out on exchange order "
            f"{reference}, with {amount:.2f} USD returned to the customer as the difference.")

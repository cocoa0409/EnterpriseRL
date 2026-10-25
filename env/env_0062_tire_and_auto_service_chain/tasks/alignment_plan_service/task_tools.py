"""Hidden task tools of the alignment_plan_service difficulty (Crestline Alignment Services & Plans).

Each tool performs exactly one atomic business write on alignment records and is reached through the
unlock/call meta tools. No tool judges eligibility, ordering or amounts: every value it books is passed in.
"""

from erlbench import ToolContext, tool

_REFUND_TENDERS = ("cash_or_debit", "bank_card")
_PLAN_TENDERS = ("cash_or_debit", "bank_card")
_BASIS_VALUES = ("plan_included", "member_early_price")
_LIFETIME_TIERS = ("Crestline Lifetime Alignment Plan", "Crestline Lifetime Alignment Plan Truck & Performance")


@tool(owner="agent", rw="write")
def price_alignment_work_order_228c355b(ctx: ToolContext, alignment_plan_id: str, alignment_event_id: str,
                                        service_basis: str, charge_amount: float) -> str:
    """Set the labor of an open alignment work order on a plan. A store posts the work order of an alignment it
    performed on a plan vehicle with its service basis left open (none) and no labor charged; this action fills in
    how the alignment is paid and the labor amount charged for it. On success that work order shows the service basis
    and labor charge given here, which the customer sees on the ticket; its date, odometer, alignment type and parts
    charge are left as they are.

    Args:
        alignment_plan_id: Id class — reference number of the alignment plan the work order is posted on, taken from
            the alignment plan lookup.
        alignment_event_id: Id class — reference number of the open alignment work order (an alignment performed entry
            on the plan whose service basis is none), taken from the plan's alignment activity lookup.
        service_basis: Enum class — how the alignment is paid: plan_included when no labor is charged because the
            alignment is included in the plan; member_early_price when labor is charged for this alignment. The values
            none and guarantee_readjustment describe bookings, refunds and readjustments and are not accepted here.
        charge_amount: Fixed-format class — labor charged for the alignment, in USD, a non-negative amount with 2
            decimal places (rounded to the nearest cent by the tool when more digits are given); 0.00 when nothing is
            charged.

    Returns:
        A text rendering of a dictionary with alignment_plan_id (the plan reference number, text), alignment_event_id
        (the work order reference number, text), service_basis (the basis now booked, text), charge_amount (the labor now booked, USD number with 2 decimal
        places) and status (the text priced, which confirms the work order now carries its labor). An input outside
        the accepted service basis values returns a text starting with Error: and changes nothing.
    """
    if service_basis not in _BASIS_VALUES:
        return f"Error: service_basis must be one of {', '.join(_BASIS_VALUES)}."
    amount = round(float(charge_amount), 2)
    ctx.update("alignment_events", alignment_event_id, alignment_plan_id=alignment_plan_id,
               service_basis=service_basis, charge_amount=amount)
    return str({"alignment_plan_id": alignment_plan_id, "alignment_event_id": alignment_event_id,
                "service_basis": service_basis,
                "charge_amount": amount, "status": "priced"})


@tool(owner="agent", rw="write")
def price_work_order_parts_2c1ce050(ctx: ToolContext, alignment_plan_id: str, alignment_event_id: str,
                                    parts_charge: float) -> str:
    """Set the parts charge of an alignment work order on a plan. The store lists the adjustment parts it installed on
    the work order at their list price; this action replaces that listed figure with the parts amount the customer is
    charged for the work order. On success the work order shows the parts charge given here on the ticket; its labor,
    service basis, date, odometer and alignment type are left as they are.

    Args:
        alignment_plan_id: Id class — reference number of the alignment plan the work order is posted on, taken from
            the alignment plan lookup.
        alignment_event_id: Id class — reference number of the alignment work order (an alignment performed entry on
            the plan), taken from the plan's alignment activity lookup.
        parts_charge: Fixed-format class — parts charged on the work order, in USD, a non-negative amount with 2
            decimal places (rounded to the nearest cent by the tool when more digits are given); 0.00 when no parts
            are charged.

    Returns:
        A text rendering of a dictionary with alignment_plan_id (the plan reference number, text), alignment_event_id
        (the work order reference number, text), parts_charge (the parts amount now booked, USD number with 2 decimal places) and status (the text
        parts_priced, which confirms the work order now carries its parts charge).
    """
    amount = round(float(parts_charge), 2)
    ctx.update("alignment_events", alignment_event_id, alignment_plan_id=alignment_plan_id, parts_charge=amount)
    return str({"alignment_plan_id": alignment_plan_id, "alignment_event_id": alignment_event_id,
                "parts_charge": amount, "status": "parts_priced"})


@tool(owner="agent", rw="write")
def price_alignment_readjustment_e00d4c5e(ctx: ToolContext, alignment_event_id: str, source_alignment_event_id: str,
                                          parts_charge: float) -> str:
    """Confirm an open readjustment as a free guarantee readjustment and set its parts charge. A store posts a
    readjustment of an earlier alignment with its service basis left open (none) and the replacement parts listed at
    their list price; this action books the readjustment as a guarantee readjustment with no labor charged and
    replaces the listed parts figure with the parts amount the customer is charged. On success the readjustment shows
    service basis guarantee_readjustment, labor 0.00 and the parts charge given here; the alignment it corrects, its
    date and its odometer are left as they are.

    Args:
        alignment_event_id: Id class — reference number of the open readjustment (a readjustment entry on the plan
            whose service basis is none), taken from the plan's alignment activity lookup.
        source_alignment_event_id: Id class — reference number of the alignment the readjustment corrects (an
            alignment performed entry on the same plan), taken from the plan's alignment activity lookup.
        parts_charge: Fixed-format class — parts charged on the readjustment, in USD, a non-negative amount with 2
            decimal places (rounded to the nearest cent by the tool when more digits are given); 0.00 when no parts
            are charged.

    Returns:
        A text rendering of a dictionary with alignment_event_id (the readjustment reference number, text),
        source_alignment_event_id (the corrected alignment's reference number, text), service_basis (the text guarantee_readjustment), charge_amount (labor booked, always 0.0), parts_charge (the
        parts amount now booked, USD number with 2 decimal places) and status (the text readjustment_priced, which
        confirms the readjustment is booked).
    """
    amount = round(float(parts_charge), 2)
    ctx.update("alignment_events", alignment_event_id, source_alignment_event_id=source_alignment_event_id,
               service_basis="guarantee_readjustment", charge_amount=0.0, parts_charge=amount)
    return str({"alignment_event_id": alignment_event_id, "source_alignment_event_id": source_alignment_event_id,
                "service_basis": "guarantee_readjustment",
                "charge_amount": 0.0, "parts_charge": amount, "status": "readjustment_priced"})


@tool(owner="user", rw="write")
def confirm_alignment_cancellation_b0865de9(ctx: ToolContext, alignment_cancel_request_id: str, alignment_plan_id: str,
                                            refund_amount: float, refund_tender: str) -> str:
    """The plan holder confirms a pending cancellation request for their own alignment plan. On success the request
    becomes confirmed, the plan is closed with status cancelled and a closing date of today, and a refund entry is
    booked on the plan for the refund amount and tender given here, which the holder can see on the plan's activity.

    Args:
        alignment_cancel_request_id: Id class — reference number of the cancellation request awaiting the holder's
            confirmation, given to the holder by the agent from the plan's cancellation request lookup.
        alignment_plan_id: Id class — reference number of the alignment plan being cancelled, given to the holder by
            the agent from the alignment plan lookup.
        refund_amount: Fixed-format class — refund paid to the holder, written in the refund entry's format USD, 2
            decimal places, positive; the amount is never negative and is 0.00 when the refund works out to nothing;
            rounded to the nearest cent by the tool when more digits are given.
        refund_tender: Enum class — where the refund goes: cash_or_debit when the plan was paid in cash or with a
            debit card; bank_card when the plan was paid with an outside bank credit card. The value none names no
            tender and is not accepted; crestline_card is not accepted because a refund to the Crestline card posts
            through the card account; fleet_account is not accepted because a refund to a fleet account posts
            through that account.

    Returns:
        A text rendering of a dictionary with alignment_cancel_request_id (text), request_status (the text
        confirmed), alignment_plan_id (text), plan_status (the text cancelled), closed_date (today, YYYY-MM-DD),
        refund_event_id (reference number of the booked refund entry, text), refund_amount (USD number with 2 decimal
        places) and refund_tender (text). An input outside the accepted refund tenders returns a text starting with
        Error: and changes nothing.
    """
    if refund_tender not in _REFUND_TENDERS:
        return f"Error: refund_tender must be one of {', '.join(_REFUND_TENDERS)}."
    amount = round(float(refund_amount), 2)
    today = ctx.now()[:10]
    ctx.update("alignment_cancellation_requests", alignment_cancel_request_id, request_status="confirmed")
    ctx.update("alignment_plans", alignment_plan_id, status="cancelled", closed_date=today)
    plan_rows = ctx.find("alignment_plans", alignment_plan_id=alignment_plan_id)
    customer_id = plan_rows[0].get("customer_id") if plan_rows else ""
    rid = ctx.make_id("ale_", alignment_cancel_request_id, alignment_plan_id, amount, refund_tender)
    ctx.create("alignment_events", rid, alignment_event_id=rid, alignment_plan_id=alignment_plan_id,
               customer_id=customer_id, event_type="alignment_refund", event_date=today, store_id="",
               odometer=0, appointment_date="", appointment_time="", alignment_type="none", service_basis="none",
               charge_amount=0.0, parts_charge=0.0, source_alignment_event_id="", amount=amount,
               payment_method=refund_tender)
    return str({"alignment_cancel_request_id": alignment_cancel_request_id, "request_status": "confirmed",
                "alignment_plan_id": alignment_plan_id, "plan_status": "cancelled", "closed_date": today,
                "refund_event_id": rid, "refund_amount": amount, "refund_tender": refund_tender})


class _TicketNumbers:
    """Deterministic store ticket numbers for plans sold through the plan desk (T- and 8 digits)."""

    @staticmethod
    def build(ctx: ToolContext, *parts) -> str:
        digest = ctx.make_id("tkt", *parts)[3:]
        return "T-5" + str(int(digest, 16) % 10000000).zfill(7)


@tool(owner="user", rw="write")
def enroll_household_alignment_plan_f0fe3800(ctx: ToolContext, household_plan_id: str, vehicle_id: str, store_id: str,
                                             purchase_odometer: int, payment_method: str,
                                             purchase_price: float) -> str:
    """The customer buys, for another vehicle of their own, a lifetime alignment plan of the same tier as the active
    lifetime plan they already hold, at the household price the agent quoted. On success a new active alignment plan
    of that tier is created for the given vehicle, dated today, with no expiration date, the purchase odometer, tender
    and price given here and a newly issued store ticket number; the customer sees the new plan on their profile.

    Args:
        household_plan_id: Id class — reference number of the customer's active lifetime alignment plan whose tier
            the new plan takes, taken from the alignment plan lookup.
        vehicle_id: Id class — reference number of the vehicle the new plan is bought for, taken from the vehicle
            lookup.
        store_id: Id class — reference number of the Crestline store the plan is sold through, taken from the store
            lookup.
        purchase_odometer: Fixed-format class — odometer of the vehicle on the purchase date, in integer miles, as
            written on that vehicle's work order of the day.
        payment_method: Enum class — tender the customer pays with: cash_or_debit for cash or a debit card; bank_card
            for an outside bank credit card. The values crestline_card and fleet_account are not accepted here,
            because tickets on those accounts post through them.
        purchase_price: Fixed-format class — price of the new plan, in USD, with 2 decimal places, before tax
            (rounded to the nearest cent by the tool when more digits are given).

    Returns:
        A text rendering of a dictionary with alignment_plan_id (reference number of the new plan, text),
        variant_name (the tier taken from the household plan, text), vehicle_id (text), status (the text active),
        purchase_date (today, YYYY-MM-DD), purchase_ticket_number (T- followed by 8 digits) and purchase_price (USD
        number with 2 decimal places). An input outside the accepted tenders, or a household plan reference that is
        not a lifetime plan, returns a text starting with Error: and changes nothing.
    """
    if payment_method not in _PLAN_TENDERS:
        return f"Error: payment_method must be one of {', '.join(_PLAN_TENDERS)}."
    anchor = ctx.find("alignment_plans", alignment_plan_id=household_plan_id)
    tier = anchor[0].get("variant_name") if anchor else ""
    if tier not in _LIFETIME_TIERS:
        return "Error: household_plan_id must reference a lifetime alignment plan."
    price = round(float(purchase_price), 2)
    today = ctx.now()[:10]
    customer_id = anchor[0].get("customer_id")
    rid = ctx.make_id("alp_", household_plan_id, vehicle_id, store_id, int(purchase_odometer), payment_method, price)
    ticket = _TicketNumbers.build(ctx, rid)
    ctx.create("alignment_plans", rid, alignment_plan_id=rid, customer_id=customer_id, vehicle_id=vehicle_id,
               store_id=store_id, variant_name=tier, status="active", purchase_date=today,
               purchase_odometer=int(purchase_odometer), expiration_date="", purchase_price=price,
               purchase_ticket_number=ticket, payment_method=payment_method, closed_date="")
    return str({"alignment_plan_id": rid, "variant_name": tier, "vehicle_id": vehicle_id, "status": "active",
                "purchase_date": today, "purchase_ticket_number": ticket, "purchase_price": price})


@tool(owner="user", rw="write")
def renew_alignment_plan_418ab11e(ctx: ToolContext, expired_plan_id: str, vehicle_id: str, store_id: str,
                                  purchase_odometer: int, expiration_date: str, payment_method: str,
                                  purchase_price: float) -> str:
    """The customer renews their own expired month-based alignment plan at the renewal price the agent quoted. On
    success a new active alignment plan of the same tier and customer as the expired plan is created for the given
    vehicle, dated today, with the expiration date, purchase odometer, tender and price given here and a newly issued
    store ticket number; the expired plan itself is left as it is, and the customer sees the new plan on their
    profile.

    Args:
        expired_plan_id: Id class — reference number of the customer's expired month-based alignment plan being
            renewed, taken from the alignment plan lookup.
        vehicle_id: Id class — reference number of the vehicle the expired plan was valid on and the renewal is
            bought for, taken from the vehicle lookup.
        store_id: Id class — reference number of the Crestline store the renewal is sold through, taken from the
            store lookup.
        purchase_odometer: Fixed-format class — odometer of the vehicle on the renewal date, in integer miles, as
            written on that vehicle's work order of the day.
        expiration_date: Fixed-format class — last day of the new plan's term, as a calendar date in YYYY-MM-DD.
        payment_method: Enum class — tender the customer pays with: cash_or_debit for cash or a debit card; bank_card
            for an outside bank credit card. The values crestline_card and fleet_account are not accepted here,
            because tickets on those accounts post through them.
        purchase_price: Fixed-format class — price of the renewal, in USD, with 2 decimal places, before tax (rounded
            to the nearest cent by the tool when more digits are given).

    Returns:
        A text rendering of a dictionary with alignment_plan_id (reference number of the new plan, text),
        variant_name (the tier taken from the expired plan, text), vehicle_id (text), status (the text active),
        purchase_date (today, YYYY-MM-DD), expiration_date (YYYY-MM-DD), purchase_ticket_number (T- followed by 8
        digits) and purchase_price (USD number with 2 decimal places). An input outside the accepted tenders, or an
        expired plan reference that is unknown, returns a text starting with Error: and changes nothing.
    """
    if payment_method not in _PLAN_TENDERS:
        return f"Error: payment_method must be one of {', '.join(_PLAN_TENDERS)}."
    old = ctx.find("alignment_plans", alignment_plan_id=expired_plan_id)
    if not old:
        return "Error: expired_plan_id does not reference an alignment plan."
    price = round(float(purchase_price), 2)
    today = ctx.now()[:10]
    rid = ctx.make_id("alp_", expired_plan_id, vehicle_id, store_id, int(purchase_odometer), expiration_date,
                      payment_method, price)
    ticket = _TicketNumbers.build(ctx, rid)
    ctx.create("alignment_plans", rid, alignment_plan_id=rid, customer_id=old[0].get("customer_id"),
               vehicle_id=vehicle_id, store_id=store_id, variant_name=old[0].get("variant_name"),
               status="active", purchase_date=today, purchase_odometer=int(purchase_odometer),
               expiration_date=expiration_date, purchase_price=price, purchase_ticket_number=ticket,
               payment_method=payment_method, closed_date="")
    return str({"alignment_plan_id": rid, "variant_name": old[0].get("variant_name"),
                "vehicle_id": vehicle_id, "status": "active", "purchase_date": today,
                "expiration_date": expiration_date, "purchase_ticket_number": ticket, "purchase_price": price})

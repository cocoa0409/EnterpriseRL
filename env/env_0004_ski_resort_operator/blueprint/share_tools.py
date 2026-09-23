"""Shared tools for the Granite Ridge Mountain Collective guest services centre.

Every tool defined here is present in its owner's tool list on every task of the scenario: the
complete record-lookup layer (one finder per kind of record, with the guest profile finder doubling
as the entry point a call starts from), the identity verification write, and the transfer to a human
representative. Business actions that belong to one desk are authored as that difficulty's own task
tools, never here.
"""

from erlbench import ToolContext, tool


# ---------------------------------------------------------------------------
# Guest profile: the entry point of every call, and the by-id finder.
# ---------------------------------------------------------------------------

@tool(owner="agent", rw="read")
def find_customers(ctx: ToolContext, customer_id: str = "", mobile_phone: str = "",
                   email: str = "", name: str = "", passholder_number: str = "") -> str:
    """Look up the household account this call is about and read back the profile the collective
    holds for it. A household may be found by its account reference number or by anything the caller
    can naturally say on the phone: the mobile number registered with the collective, the registered
    email address, the account holder's full name, or the passholder number printed on their media.
    Every criterion is optional, so pass whichever the caller has given; passing more than one
    narrows the search. Matching ignores spacing, punctuation and capitalisation, so a number read
    out with dashes or a name given with a trailing full stop still finds the household. The profile
    returned carries the account reference, the account holder's name, contact details, date of
    birth, home postal code, the date the household first opened an account, whether a payment method
    is stored and which mountain they nominate as their usual hill. Finding a household is not the
    same as proving who is on the line: identity is established by the separate verification step.
    Where nothing matches, that is reported; where several households match, one more detail is asked
    for rather than a guess being made.

    Args:
        customer_id: The household account reference number, where the caller already has it; leave "" if unknown.
        mobile_phone: The mobile number registered with the collective, 10 digits; leave "" if not given.
        email: The email address registered with the collective; leave "" if not given.
        name: The account holder's full name as they state it; leave "" if not given.
        passholder_number: The passholder number printed on the guest's media, the letters GR followed by 8 digits; leave "" if not given.
    """
    match = {k: v for k, v in {"customer_id": customer_id, "mobile_phone": mobile_phone,
                               "email": email, "name": name,
                               "passholder_number": passholder_number}.items() if v}
    if not match:
        return "Error: provide at least one detail — account reference, mobile number, email, name or passholder number."
    rows = ctx.fuzzy_find("customers", **match)
    if not rows:
        return f"No household account matches {match}."
    if len(rows) > 1:
        return (f"Error: {len(rows)} household accounts match {match}; ask the caller for one more "
                "detail to tell them apart.")
    return str(rows[0])


# ---------------------------------------------------------------------------
# Season passes
# ---------------------------------------------------------------------------

@tool(owner="agent", rw="read")
def find_season_passes(ctx: ToolContext, pass_id: str = "", customer_id: str = "") -> str:
    """Read back the season pass records the collective holds, each one a pass bought for a single
    named passholder for a single season. A record carries the tier by its official name, the state
    the pass stands in, the season it admits the holder to, the passholder's name and age band, the
    home mountain, how the price is being collected, the dates the pass was applied for, activated
    and closed, the price committed to, the amount still to be collected, the resort credit and buddy
    tickets left on it, the media serial, the tier it was moved up from, why it was given up and the
    season it was carried forward to. Search by the pass reference number to read one record, or by
    the household account reference to read every pass on that account; both are optional and giving
    neither returns the whole register.

    Args:
        pass_id: The reference number of a single season pass record; leave "" if unknown.
        customer_id: The household account reference number, to list every pass bought on that account; leave "" if unknown.
    """
    match = {k: v for k, v in {"pass_id": pass_id, "customer_id": customer_id}.items() if v}
    rows = ctx.find("passes_holdings", **match)
    return str(rows) if rows else f"No season pass records for {match}."


@tool(owner="agent", rw="read")
def find_pass_account_entries(ctx: ToolContext, pass_event_id: str = "", pass_id: str = "",
                              customer_id: str = "", related_event_id: str = "") -> str:
    """Read back the entries on a pass account: the instalment plan openings, the instalments that
    cleared and the ones the payment method refused, the late and service fees, the amount due for a
    move up, the resort credit issued and applied, the lift scans, and the buddy ticket allotment
    loaded and drawn. Each entry carries the date it happened, the amount, the instalment position
    where it belongs to a schedule, where the money was taken, what the charge was for, why a payment
    method refused, why credit was issued, and for a scan the mountain, the lift, the time and the
    media presented. Search by a single entry reference, by the pass the entries belong to, by the
    household account, or by the entry another entry answers to — for instance to find the late fee
    raised against a particular refused instalment. Every criterion is optional.

    Args:
        pass_event_id: The reference number of a single pass account entry; leave "" if unknown.
        pass_id: The reference number of the season pass whose entries are wanted; leave "" if unknown.
        customer_id: The household account reference number; leave "" if unknown.
        related_event_id: The reference number of the entry that other entries answer to, such as the refused instalment a late fee was raised against; leave "" if unknown.
    """
    match = {k: v for k, v in {"pass_event_id": pass_event_id, "pass_id": pass_id,
                               "customer_id": customer_id,
                               "related_event_id": related_event_id}.items() if v}
    rows = ctx.find("passes_ledger", **match)
    return str(rows) if rows else f"No pass account entries for {match}."


@tool(owner="agent", rw="read")
def find_pass_service_requests(ctx: ToolContext, pass_request_id: str = "", customer_id: str = "",
                               pass_id: str = "") -> str:
    """Read back the service requests raised against season passes — cancellations, carry-forwards,
    moves up, re-registrations, refund reviews and media replacements. Each request carries what was
    asked for, the tier asked to move to where that applies, the reason the household gave in their
    own words before any record confirmed it, where the request stands, and the moment it was
    registered. Search by the request reference, by the household account, or by the pass the request
    concerns; all three are optional.

    Args:
        pass_request_id: The reference number of a single pass service request; leave "" if unknown.
        customer_id: The household account reference number; leave "" if unknown.
        pass_id: The reference number of the season pass the request concerns; leave "" if unknown.
    """
    match = {k: v for k, v in {"pass_request_id": pass_request_id, "customer_id": customer_id,
                               "pass_id": pass_id}.items() if v}
    rows = ctx.find("passes_requests", **match)
    return str(rows) if rows else f"No pass service requests for {match}."


# ---------------------------------------------------------------------------
# Snowsports school
# ---------------------------------------------------------------------------

@tool(owner="agent", rw="read")
def find_lesson_bookings(ctx: ToolContext, lesson_id: str = "", customer_id: str = "") -> str:
    """Read back the snowsports school bookings the collective holds, each one a place for a single
    participant starting on a single date. A record carries the product by its official name, the
    state the booking stands in, the season, the participant's name, age band and assessed ability
    level, the discipline and language, the mountain, the date and time of the first session, how
    many sessions the block holds and how many are still to come, the instructor and meeting point,
    the dates the booking was recorded and completed, the amount still to be collected, the school
    credit standing on it, why it was given up and how many times it has been moved. Search by the
    booking reference to read one, or by the household account reference to read every booking on
    that account.

    Args:
        lesson_id: The reference number of a single school booking; leave "" if unknown.
        customer_id: The household account reference number, to list every booking on that account; leave "" if unknown.
    """
    match = {k: v for k, v in {"lesson_id": lesson_id, "customer_id": customer_id}.items() if v}
    rows = ctx.find("lessons_holdings", **match)
    return str(rows) if rows else f"No school bookings for {match}."


@tool(owner="agent", rw="read")
def find_lesson_account_entries(ctx: ToolContext, lesson_event_id: str = "", lesson_id: str = "",
                                customer_id: str = "", related_event_id: str = "") -> str:
    """Read back the entries on a school account: the tuition raised, the add-ons the household took
    such as a lift ticket, rental equipment or a supervised lunch, the school fees for a late
    cancellation, a missed session, a move to another date or a change of participant, the payments
    collected, the block of sessions loaded, each session delivered with the instructor who gave it,
    and the school credit issued and applied. Each entry carries the date, the amount, the session
    date and position where it belongs to a session, what the charge was for, how the money was
    taken, and why credit was issued. Search by a single entry reference, by the booking, by the
    household account, or by the entry another entry answers to, such as the charge a payment
    settles. Every criterion is optional.

    Args:
        lesson_event_id: The reference number of a single school account entry; leave "" if unknown.
        lesson_id: The reference number of the school booking whose entries are wanted; leave "" if unknown.
        customer_id: The household account reference number; leave "" if unknown.
        related_event_id: The reference number of the entry that other entries answer to, such as the charge a payment settles; leave "" if unknown.
    """
    match = {k: v for k, v in {"lesson_event_id": lesson_event_id, "lesson_id": lesson_id,
                               "customer_id": customer_id,
                               "related_event_id": related_event_id}.items() if v}
    rows = ctx.find("lessons_ledger", **match)
    return str(rows) if rows else f"No school account entries for {match}."


@tool(owner="agent", rw="read")
def find_lesson_service_requests(ctx: ToolContext, lesson_request_id: str = "",
                                 customer_id: str = "", lesson_id: str = "") -> str:
    """Read back the service requests raised against school bookings — cancellations, moves to
    another date, changes of participant, makeup bookings, named instructor requests and refund
    reviews. Each request carries what was asked for, the session date asked for where that applies,
    the reason the household gave in their own words before any record confirmed it, where the
    request stands, and the moment it was registered. Search by the request reference, by the
    household account, or by the booking concerned.

    Args:
        lesson_request_id: The reference number of a single school service request; leave "" if unknown.
        customer_id: The household account reference number; leave "" if unknown.
        lesson_id: The reference number of the school booking the request concerns; leave "" if unknown.
    """
    match = {k: v for k, v in {"lesson_request_id": lesson_request_id, "customer_id": customer_id,
                               "lesson_id": lesson_id}.items() if v}
    rows = ctx.find("lessons_requests", **match)
    return str(rows) if rows else f"No school service requests for {match}."


# ---------------------------------------------------------------------------
# Equipment rental
# ---------------------------------------------------------------------------

@tool(owner="agent", rw="read")
def find_rental_agreements(ctx: ToolContext, rental_id: str = "", customer_id: str = "") -> str:
    """Read back the equipment rental agreements the collective holds, each one written over a single
    named rider. A record carries the package by its official name, the state the agreement stands
    in, the season, the rider's name, age band, height, weight and ability level, the discipline, the
    shops the kit was collected from and handed in at, the collection, due and hand-in dates, the
    days the agreement covers and the days still left, the serial of the kit and the boot size fitted,
    whether the damage waiver was taken, the security hold standing, the amount still to be
    collected, how many times the kit has been changed, why the reservation was given up and whether
    the signed liability release is on file. Search by the agreement reference to read one, or by the
    household account reference to read every agreement on that account.

    Args:
        rental_id: The reference number of a single rental agreement; leave "" if unknown.
        customer_id: The household account reference number, to list every agreement on that account; leave "" if unknown.
    """
    match = {k: v for k, v in {"rental_id": rental_id, "customer_id": customer_id}.items() if v}
    rows = ctx.find("rentals_holdings", **match)
    return str(rows) if rows else f"No rental agreements for {match}."


@tool(owner="agent", rw="read")
def find_rental_account_entries(ctx: ToolContext, rental_event_id: str = "", rental_id: str = "",
                                customer_id: str = "", related_event_id: str = "") -> str:
    """Read back the entries on a rental account: the block of rental days loaded, each day the kit
    was out, the rate and add-ons charged, the shop fees for a change of kit, an extension, a late
    hand-in, a cancellation or an uncollected reservation, the damage a technician assessed against a
    particular item, the payments collected, and the security hold placed and released. Each entry
    carries the date, the amount, the day of use where it records one, what the charge was for, how
    the money moved, the serial and kind of the item, the mountain, what was found wrong with the
    item, and where the hold stands. Search by a single entry reference, by the agreement, by the
    household account, or by the entry another entry answers to, such as the hold a release answers
    to.

    Args:
        rental_event_id: The reference number of a single rental account entry; leave "" if unknown.
        rental_id: The reference number of the rental agreement whose entries are wanted; leave "" if unknown.
        customer_id: The household account reference number; leave "" if unknown.
        related_event_id: The reference number of the entry that other entries answer to, such as the security hold a release answers to; leave "" if unknown.
    """
    match = {k: v for k, v in {"rental_event_id": rental_event_id, "rental_id": rental_id,
                               "customer_id": customer_id,
                               "related_event_id": related_event_id}.items() if v}
    rows = ctx.find("rentals_ledger", **match)
    return str(rows) if rows else f"No rental account entries for {match}."


@tool(owner="agent", rw="read")
def find_rental_service_requests(ctx: ToolContext, rental_request_id: str = "",
                                 customer_id: str = "", rental_id: str = "") -> str:
    """Read back the service requests raised against rental agreements — cancellations, extensions,
    size changes, damage reviews, security hold reviews and early hand-ins. Each request carries what
    was asked for, the due date asked for where that applies, the reason the guest gave in their own
    words before any record confirmed it, where the request stands, and the moment it was registered.
    Search by the request reference, by the household account, or by the agreement concerned.

    Args:
        rental_request_id: The reference number of a single rental service request; leave "" if unknown.
        customer_id: The household account reference number; leave "" if unknown.
        rental_id: The reference number of the rental agreement the request concerns; leave "" if unknown.
    """
    match = {k: v for k, v in {"rental_request_id": rental_request_id, "customer_id": customer_id,
                               "rental_id": rental_id}.items() if v}
    rows = ctx.find("rentals_requests", **match)
    return str(rows) if rows else f"No rental service requests for {match}."


# ---------------------------------------------------------------------------
# Lodging
# ---------------------------------------------------------------------------

@tool(owner="agent", rw="read")
def find_lodging_reservations(ctx: ToolContext, lodging_id: str = "", customer_id: str = "") -> str:
    """Read back the lodging reservations the collective holds, each one a unit taken over a set of
    dates for one party. A record carries the unit type by its official name, the state the
    reservation stands in, the season, the lead guest, the mountain, the arrival and departure dates
    and the nights covered and still to come, the adults, children, dogs and parking spaces, the unit
    number and building once assigned, the published rate window the stay is priced on, the dates the
    reservation was recorded and the deposit fell due, the moments the party arrived and left, the
    deposit standing and the folio still to be collected, and why the reservation was given up.
    Search by the reservation reference to read one, or by the household account reference to read
    every reservation on that account.

    Args:
        lodging_id: The reference number of a single lodging reservation; leave "" if unknown.
        customer_id: The household account reference number, to list every reservation on that account; leave "" if unknown.
    """
    match = {k: v for k, v in {"lodging_id": lodging_id, "customer_id": customer_id}.items() if v}
    rows = ctx.find("lodging_holdings", **match)
    return str(rows) if rows else f"No lodging reservations for {match}."


@tool(owner="agent", rw="read")
def find_lodging_folio_entries(ctx: ToolContext, folio_event_id: str = "", lodging_id: str = "",
                               customer_id: str = "", related_event_id: str = "") -> str:
    """Read back the entries on a lodging folio: the deposit taken and later applied or returned, the
    block of nights loaded and each night occupied, the room rate posted night by night, the resort
    charge, the incidentals the party raised around the mountain, the reservation fees for a change,
    a re-registration, a cancellation or an unclaimed night, and the payments collected. Each entry
    carries the date it was posted, the night or day it is for, the amount, what it is for, the rate
    window the night was priced in, the unit, the outlet an incidental arose at, how the money moved
    and where the deposit stands. Search by a single entry reference, by the reservation, by the
    household account, or by the entry another entry answers to, such as the charge a payment
    settles.

    Args:
        folio_event_id: The reference number of a single folio entry; leave "" if unknown.
        lodging_id: The reference number of the lodging reservation whose folio is wanted; leave "" if unknown.
        customer_id: The household account reference number; leave "" if unknown.
        related_event_id: The reference number of the entry that other entries answer to, such as the deposit an application answers to; leave "" if unknown.
    """
    match = {k: v for k, v in {"folio_event_id": folio_event_id, "lodging_id": lodging_id,
                               "customer_id": customer_id,
                               "related_event_id": related_event_id}.items() if v}
    rows = ctx.find("lodging_folio", **match)
    return str(rows) if rows else f"No folio entries for {match}."


@tool(owner="agent", rw="read")
def find_lodging_service_requests(ctx: ToolContext, lodging_request_id: str = "",
                                  customer_id: str = "", lodging_id: str = "") -> str:
    """Read back the service requests raised against lodging reservations — cancellations, date
    changes, unit changes, party changes, changes of lead guest, deposit reviews and folio disputes.
    Each request carries what was asked for, the arrival date or unit type asked for where those
    apply, the reason the household gave in their own words before any record confirmed it, where the
    request stands, and the moment it was registered. Search by the request reference, by the
    household account, or by the reservation concerned.

    Args:
        lodging_request_id: The reference number of a single lodging service request; leave "" if unknown.
        customer_id: The household account reference number; leave "" if unknown.
        lodging_id: The reference number of the lodging reservation the request concerns; leave "" if unknown.
    """
    match = {k: v for k, v in {"lodging_request_id": lodging_request_id, "customer_id": customer_id,
                               "lodging_id": lodging_id}.items() if v}
    rows = ctx.find("lodging_requests", **match)
    return str(rows) if rows else f"No lodging service requests for {match}."


# ---------------------------------------------------------------------------
# Pass and trip protection
# ---------------------------------------------------------------------------

@tool(owner="agent", rw="read")
def find_protection_plans(ctx: ToolContext, protection_plan_id: str = "", customer_id: str = "",
                          covered_holding_id: str = "") -> str:
    """Read back the protection plans the collective holds, each one written over exactly one holding
    for one named insured. A record carries the plan by its official name, the state it stands in,
    the season, the insured's name, which product line the covered holding belongs to and its
    reference number, the value the premium and benefit were worked out from, the premium quoted and
    the premium still to be collected, the cover left for the season, the dates the plan was taken,
    cover began and ends and the waiting period ends, the beneficiary, the date an open claim was
    made, what is being claimed on and how it was decided, whether the papers are complete, and why
    the plan was given up. Search by the plan reference, by the household account, or by the
    reference number of the holding the plan is written over — which answers whether a particular
    pass, stay or booking is protected at all.

    Args:
        protection_plan_id: The reference number of a single protection plan; leave "" if unknown.
        customer_id: The household account reference number, to list every plan on that account; leave "" if unknown.
        covered_holding_id: The reference number of the holding a plan is written over, to find the plan protecting it; leave "" if unknown.
    """
    match = {k: v for k, v in {"protection_plan_id": protection_plan_id, "customer_id": customer_id,
                               "covered_holding_id": covered_holding_id}.items() if v}
    rows = ctx.find("insure_holdings", **match)
    return str(rows) if rows else f"No protection plans for {match}."


@tool(owner="agent", rw="read")
def find_protection_account_entries(ctx: ToolContext, insure_event_id: str = "",
                                    protection_plan_id: str = "", customer_id: str = "",
                                    related_event_id: str = "", covered_holding_id: str = "") -> str:
    """Read back the entries on a protection account: the premiums raised and the payments that
    settled them, the plan fees for a reinstatement, a cancellation or an amendment, the benefit limit
    loaded when cover began, the payouts made on allowed claims, and every paper received against a
    claim with a note of whether it was accepted, illegible, incomplete or superseded. Each entry
    carries the date, the amount, what a charge was for, what a claim was made on, how a payout
    reached the household, and which holding the cover concerns. Search by a single entry reference,
    by the plan, by the household account, by the entry another entry answers to, or by the covered
    holding.

    Args:
        insure_event_id: The reference number of a single protection account entry; leave "" if unknown.
        protection_plan_id: The reference number of the protection plan whose entries are wanted; leave "" if unknown.
        customer_id: The household account reference number; leave "" if unknown.
        related_event_id: The reference number of the entry that other entries answer to, such as the premium a payment settles; leave "" if unknown.
        covered_holding_id: The reference number of the holding the cover is written over; leave "" if unknown.
    """
    match = {k: v for k, v in {"insure_event_id": insure_event_id,
                               "protection_plan_id": protection_plan_id,
                               "customer_id": customer_id, "related_event_id": related_event_id,
                               "covered_holding_id": covered_holding_id}.items() if v}
    rows = ctx.find("insure_ledger", **match)
    return str(rows) if rows else f"No protection account entries for {match}."


@tool(owner="agent", rw="read")
def find_protection_service_requests(ctx: ToolContext, insure_request_id: str = "",
                                     customer_id: str = "", protection_plan_id: str = "") -> str:
    """Read back the service requests raised against protection plans — claims, cancellations,
    amendments, reinstatements, appeals and paper uploads. Each request carries what was asked for,
    the reason the household gave in their own words, the date they say the event they are claiming
    on occurred before any paper proved it, where the request stands, and the moment it was
    registered. Search by the request reference, by the household account, or by the plan concerned.

    Args:
        insure_request_id: The reference number of a single protection service request; leave "" if unknown.
        customer_id: The household account reference number; leave "" if unknown.
        protection_plan_id: The reference number of the protection plan the request concerns; leave "" if unknown.
    """
    match = {k: v for k, v in {"insure_request_id": insure_request_id, "customer_id": customer_id,
                               "protection_plan_id": protection_plan_id}.items() if v}
    rows = ctx.find("insure_requests", **match)
    return str(rows) if rows else f"No protection service requests for {match}."


# ---------------------------------------------------------------------------
# Lift tickets
# ---------------------------------------------------------------------------

@tool(owner="agent", rw="read")
def find_ticket_orders(ctx: ToolContext, ticket_order_id: str = "", customer_id: str = "") -> str:
    """Read back the lift ticket orders the collective holds, each one a block of ski days bought on
    one product. A record carries the product by its official name, the state the order stands in,
    the season, the holder's name and age band where the product names one, the ski date where the
    product names one, how many tickets and ski days the order holds and how many days are left, the
    mountain, the dates the order was recorded, the media issued and the first day skied, the amount
    committed to, the amount still to be collected, the ticket credit standing on it, the media
    serial, and why the order was abandoned or given back. Search by the order reference or by the
    household account reference.

    Args:
        ticket_order_id: The reference number of a single ticket order; leave "" if unknown.
        customer_id: The household account reference number, to list every ticket order on that account; leave "" if unknown.
    """
    match = {k: v for k, v in {"ticket_order_id": ticket_order_id,
                               "customer_id": customer_id}.items() if v}
    rows = ctx.find("tickets_holdings", **match)
    return str(rows) if rows else f"No ticket orders for {match}."


@tool(owner="agent", rw="read")
def find_ticket_account_entries(ctx: ToolContext, ticket_event_id: str = "",
                                ticket_order_id: str = "", customer_id: str = "",
                                related_event_id: str = "") -> str:
    """Read back the entries on a ticket account: the price of the order and any holiday surcharge,
    the ticket office fees for a date change, a change of holder, replacement media or an abandoned
    order, the payments collected, the block of ski days loaded onto the media, each day drawn when
    the holder scanned, and the ticket credit issued and applied. Each entry carries the date, the ski
    date it concerns, the amount, what a charge was for, how the money moved, why credit was issued,
    the mountain and the media presented. Search by a single entry reference, by the order, by the
    household account, or by the entry another entry answers to.

    Args:
        ticket_event_id: The reference number of a single ticket account entry; leave "" if unknown.
        ticket_order_id: The reference number of the ticket order whose entries are wanted; leave "" if unknown.
        customer_id: The household account reference number; leave "" if unknown.
        related_event_id: The reference number of the entry that other entries answer to, such as the day drawn that a storm credit answers to; leave "" if unknown.
    """
    match = {k: v for k, v in {"ticket_event_id": ticket_event_id,
                               "ticket_order_id": ticket_order_id, "customer_id": customer_id,
                               "related_event_id": related_event_id}.items() if v}
    rows = ctx.find("tickets_ledger", **match)
    return str(rows) if rows else f"No ticket account entries for {match}."


@tool(owner="agent", rw="read")
def find_ticket_service_requests(ctx: ToolContext, ticket_request_id: str = "",
                                 customer_id: str = "", ticket_order_id: str = "") -> str:
    """Read back the service requests raised at the ticket office — date changes, changes of holder,
    refunds, storm credits, media replacements and abandoned orders. Each request carries what was
    asked for, the ski date asked for where that applies, the reason the guest gave in their own
    words before any record confirmed it, where the request stands, and the moment it was registered.
    Search by the request reference, by the household account, or by the order concerned.

    Args:
        ticket_request_id: The reference number of a single ticket office service request; leave "" if unknown.
        customer_id: The household account reference number; leave "" if unknown.
        ticket_order_id: The reference number of the ticket order the request concerns; leave "" if unknown.
    """
    match = {k: v for k, v in {"ticket_request_id": ticket_request_id, "customer_id": customer_id,
                               "ticket_order_id": ticket_order_id}.items() if v}
    rows = ctx.find("tickets_requests", **match)
    return str(rows) if rows else f"No ticket office service requests for {match}."


# ---------------------------------------------------------------------------
# Mountain dining plans
# ---------------------------------------------------------------------------

@tool(owner="agent", rw="read")
def find_dining_plans(ctx: ToolContext, dining_plan_id: str = "", customer_id: str = "") -> str:
    """Read back the mountain dining plans the collective holds, each one a loaded balance registered
    to a named holder. A record carries the plan by its official name, the state it stands in, the
    season, the holder's name, the mountain whose outlets the household expects to use, how many
    cards are issued and the serial the holder carries, the dates the plan was opened, first became
    spendable and last stood open, the spending power left, the plan fees still to be collected,
    whether it tops itself up, why spending was stopped and why the plan was given up. Search by the
    plan reference or by the household account reference.

    Args:
        dining_plan_id: The reference number of a single dining plan; leave "" if unknown.
        customer_id: The household account reference number, to list every dining plan on that account; leave "" if unknown.
    """
    match = {k: v for k, v in {"dining_plan_id": dining_plan_id,
                               "customer_id": customer_id}.items() if v}
    rows = ctx.find("dining_holdings", **match)
    return str(rows) if rows else f"No dining plans for {match}."


@tool(owner="agent", rw="read")
def find_dining_account_entries(ctx: ToolContext, dining_event_id: str = "",
                                dining_plan_id: str = "", customer_id: str = "",
                                related_event_id: str = "") -> str:
    """Read back the entries on a dining account: the money loaded and the bonus each load earned,
    every transaction at an outlet, balances returned on a cancellation, the plan fees for enrolment,
    an extra or replacement card, a transfer or a reinstatement, the payments that settled those
    fees, and the statements drawn up for the household. Each entry carries the date, the amount,
    where a load was made, what a fee was for, why a balance was returned, the outlet and mountain a
    transaction arose at, the card presented, the kind of goods bought, and for a statement the period
    it covers. Search by a single entry reference, by the plan, by the household account, or by the
    entry another entry answers to, such as the load a bonus was earned on.

    Args:
        dining_event_id: The reference number of a single dining account entry; leave "" if unknown.
        dining_plan_id: The reference number of the dining plan whose entries are wanted; leave "" if unknown.
        customer_id: The household account reference number; leave "" if unknown.
        related_event_id: The reference number of the entry that other entries answer to, such as the load a bonus was earned on; leave "" if unknown.
    """
    match = {k: v for k, v in {"dining_event_id": dining_event_id, "dining_plan_id": dining_plan_id,
                               "customer_id": customer_id,
                               "related_event_id": related_event_id}.items() if v}
    rows = ctx.find("dining_ledger", **match)
    return str(rows) if rows else f"No dining account entries for {match}."


@tool(owner="agent", rw="read")
def find_dining_service_requests(ctx: ToolContext, dining_request_id: str = "",
                                 customer_id: str = "", dining_plan_id: str = "",
                                 disputed_event_id: str = "") -> str:
    """Read back the service requests raised against dining plans — cancellations, card replacements,
    extra cards, transfers to another household, disputed transactions and balance refunds. Each
    request carries what was asked for, the transaction the household disputes where there is one,
    the reason they gave in their own words before any record confirmed it, where the request stands,
    and the moment it was registered. Search by the request reference, by the household account, by
    the plan concerned, or by the transaction under dispute.

    Args:
        dining_request_id: The reference number of a single dining service request; leave "" if unknown.
        customer_id: The household account reference number; leave "" if unknown.
        dining_plan_id: The reference number of the dining plan the request concerns; leave "" if unknown.
        disputed_event_id: The reference number of the dining account entry the household disputes; leave "" if unknown.
    """
    match = {k: v for k, v in {"dining_request_id": dining_request_id, "customer_id": customer_id,
                               "dining_plan_id": dining_plan_id,
                               "disputed_event_id": disputed_event_id}.items() if v}
    rows = ctx.find("dining_requests", **match)
    return str(rows) if rows else f"No dining service requests for {match}."


# ---------------------------------------------------------------------------
# Identity and escalation records
# ---------------------------------------------------------------------------

@tool(owner="agent", rw="read")
def find_identity_verifications(ctx: ToolContext, verification_id: str = "",
                                customer_id: str = "") -> str:
    """Read back the record of identity checks carried out on a household account: whether the caller
    on that account has cleared verification and the moment of the most recent attempt. Search by the
    verification record reference or by the household account reference.

    Args:
        verification_id: The reference number of a single verification record; leave "" if unknown.
        customer_id: The household account reference number; leave "" if unknown.
    """
    match = {k: v for k, v in {"verification_id": verification_id,
                               "customer_id": customer_id}.items() if v}
    rows = ctx.find("identity_verifications", **match)
    return str(rows) if rows else f"No identity verification records for {match}."


@tool(owner="agent", rw="read")
def find_human_handoffs(ctx: ToolContext, handoff_id: str = "", customer_id: str = "") -> str:
    """Read back the record of calls passed to a human representative on a household account: the
    reason each handoff was made and the moment it was recorded. Search by the handoff record
    reference or by the household account reference.

    Args:
        handoff_id: The reference number of a single handoff record; leave "" if unknown.
        customer_id: The household account reference number; leave "" if unknown.
    """
    match = {k: v for k, v in {"handoff_id": handoff_id, "customer_id": customer_id}.items() if v}
    rows = ctx.find("human_handoffs", **match)
    return str(rows) if rows else f"No handoff records for {match}."


@tool(owner="agent", rw="write")
def verify_guest_identity(ctx: ToolContext, customer_id: str, mobile_phone: str = "",
                          email: str = "", date_of_birth: str = "", passholder_number: str = "",
                          home_postal_code: str = "", profile_opened_date: str = "") -> str:
    """Establish that the caller is the household whose account is on screen, and record the outcome.
    Nothing may be transacted on a household account until this has passed. The comparison is made
    here rather than judged by eye: each piece of information the caller states is checked against the
    profile on file, the matches are counted, and the check passes only when at least 2 of them agree.
    The account reference number is used only to fetch the profile and never counts as a match, since
    knowing an account number proves nothing about who is holding the phone. Callers usually remember
    only some of what is on file, so pass exactly the values they actually state, word for word as
    they say them, and leave the rest empty. A caller who fails a first attempt and then gives another
    piece of information that brings the count up passes, and the earlier failure does not stand
    against them.

    Args:
        customer_id: The household account reference number, read from the guest profile lookup. Required and never blank; it is used only to fetch that profile and is not counted toward the number of matches.
        mobile_phone: The mobile number the caller gives as registered with the collective, 10 digits, exactly as stated; leave "" if not stated.
        email: The email address the caller gives as registered with the collective, exactly as stated; leave "" if not stated.
        date_of_birth: The account holder's date of birth as the caller states it, in the form YYYY-MM-DD; leave "" if not stated.
        passholder_number: The passholder number the caller reads off their media, the letters GR followed by 8 digits; leave "" if not stated.
        home_postal_code: The home postal code the caller gives, 5 digits; leave "" if not stated.
        profile_opened_date: The date the caller says they first opened an account with the collective, in the form YYYY-MM-DD; leave "" if not stated.
    """
    if not customer_id:
        return "Error: customer_id is required; look the household up first and pass their account reference."
    rows = ctx.find("customers", customer_id=customer_id)
    if not rows:
        return f"Error: no household account {customer_id}; cannot verify."
    rec = rows[0]
    # The tool owns the comparison. The locator customer_id is deliberately absent from `supplied`:
    # fetching a record is not proving identity.
    supplied = {"mobile_phone": mobile_phone, "email": email, "date_of_birth": date_of_birth,
                "passholder_number": passholder_number, "home_postal_code": home_postal_code,
                "profile_opened_date": profile_opened_date}
    matched = sum(1 for field, value in supplied.items()
                  if value and str(rec.get(field)) == str(value))
    verified = matched >= 2
    rid = ctx.make_id("ver_", customer_id)
    # Store only the reproducible outcome, never the match count. Upsert and never downgrade, so a
    # caller who misses once and then passes with a further attribute ends up recorded as verified.
    prior = ctx.find("identity_verifications", verification_id=rid)
    verified = verified or bool(prior and prior[0].get("verified"))
    if prior:
        ctx.update("identity_verifications", rid, verified=verified, verified_at=ctx.now())
    else:
        ctx.create("identity_verifications", rid, verification_id=rid, customer_id=customer_id,
                   verified=verified, verified_at=ctx.now())
    return (f"Identity verified for {customer_id} ({matched} detail(s) matched the profile)."
            if verified else
            f"Identity NOT verified for {customer_id} (only {matched} of the required 2 details "
            "matched). Ask the caller for another detail held on the account and check again.")


@tool(owner="agent", rw="write")
def transfer_to_human_representative(ctx: ToolContext, customer_id: str, reason: str) -> str:
    """Pass the call to a human representative at the guest services centre and record the handoff
    against the household account together with the reason for it. There are exactly two situations
    in which a call is passed on. The first is where nothing in the collective's published terms
    settles what the household is asking for, so no answer can be given without inventing one. The
    second is where the household has asked to speak to a person at least 2 separate times in the
    conversation, which is taken as a settled preference rather than a passing remark.

    Args:
        customer_id: The household account reference number, read from the guest profile lookup; the account must exist.
        reason: Why the call is being passed on; exactly one of POLICY_NOT_COVERED or CUSTOMER_REQUESTED, never free text.
            POLICY_NOT_COVERED — nothing in the collective's terms decides the request;
            CUSTOMER_REQUESTED — the household has explicitly asked for a person at least 2 times.
    """
    allowed = {"POLICY_NOT_COVERED", "CUSTOMER_REQUESTED"}
    if reason not in allowed:
        return f"Error: unknown handoff reason '{reason}'. Valid: {', '.join(sorted(allowed))}."
    if not ctx.find("customers", customer_id=customer_id):
        return f"Error: no household account {customer_id}; cannot record handoff."
    rid = ctx.make_id("hof_", customer_id, reason)
    ctx.create("human_handoffs", rid, handoff_id=rid, customer_id=customer_id,
               reason=reason, created_at=ctx.now())
    return f"Call passed to a human representative for {customer_id} ({reason})."

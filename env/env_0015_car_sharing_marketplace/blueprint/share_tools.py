"""Shared tools for env_0015_car_sharing_marketplace (Keyturn Mobility, Inc.).

Everything defined here is a SHARE tool: always in its owner's tool list and callable in
every task. Three kinds of utility live here and nothing else — the complete record-lookup
layer (one finder per record kind, the member finder doubling as the identity entry), the
identity-verification write, and the transfer to a human representative.

Member-originated writes (electing protection, asking to be paid out, snoozing a listing,
cancelling a trip) are per-difficulty business actions and are authored as hidden task tools
in each difficulty's task_tools.py, never here.
"""

from erlbench import ToolContext, tool


# ---------------------------------------------------------------- identity entry

@tool(owner="agent", rw="read")
def find_customers(ctx: ToolContext, customer_id: str = "", phone_number: str = "",
                   email: str = "", name: str = "", driver_licence_number: str = "",
                   postal_code: str = "") -> str:
    """Look up the member profile behind this call, whether the caller is renting a car as a
    guest, sharing one as a host, or both. The profile can be retrieved by the member
    reference number or by anything the caller naturally says about themselves — the mobile
    number on the profile, the email on it, their name as it appears on their licence, the
    licence number itself, or the postal code of their billing address. Every criterion is
    optional, so pass whichever were given; a single hit returns the whole profile, including
    contact details, licence details, the date the profile was opened, the driving score and
    which sides of the marketplace the member is registered on. Where several members match,
    ask the caller for one more detail and search again. Retrieving a profile establishes
    whose account is being discussed; it is not the same as verifying who is on the line.

    Args:
        customer_id: Id class — the member reference number; leave "" if unknown.
        phone_number: Fixed-format class — the mobile number registered on the profile, 10 digits with no separators; leave "" if not given.
        email: Verbatim class — the email address registered on the profile, copied exactly as the caller states it; leave "" if not given.
        name: Verbatim class — the member's full name as printed on their driving licence; leave "" if not given.
        driver_licence_number: Verbatim class — the driving licence number held on the profile, copied exactly; leave "" if not given.
        postal_code: Fixed-format class — the 5-digit ZIP code of the billing address on the profile; leave "" if not given.
    """
    match = {k: v for k, v in {"customer_id": customer_id, "phone_number": phone_number,
                               "email": email, "name": name,
                               "driver_licence_number": driver_licence_number,
                               "postal_code": postal_code}.items() if v}
    if not match:
        return "Error: provide at least one reference number or profile detail to find the member."
    rows = ctx.fuzzy_find("customers", **match)
    if not rows:
        return f"No member matches {match}."
    if len(rows) > 1:
        return f"Error: {len(rows)} members match {match}; ask for one more detail to tell them apart."
    return str(rows[0])


# ---------------------------------------------------------------- trip records

@tool(owner="agent", rw="read")
def find_trips_bookings(ctx: ToolContext, booking_id: str = "", customer_id: str = "",
                        host_customer_id: str = "", vehicle_id: str = "",
                        election_id: str = "") -> str:
    """Retrieve trip bookings and everything the marketplace records about them — the rate plan
    the trip is priced under, its state from request through to settlement, the reserved and
    actual dates, the daily price locked in at confirmation, the reserved hours, the included
    miles still unused, the balance the guest owes, how the vehicle is handed over and where it
    is delivered. Search by the booking reference, by the guest, by the host whose vehicle is
    booked, by the vehicle, or by the protection election attached to the trip; supply whichever
    references are in hand and leave the rest blank.

    Args:
        booking_id: Id class — the booking reference number itself; leave "" if unknown.
        customer_id: Id class — the member reference number of the guest who booked; leave "" if unknown.
        host_customer_id: Id class — the member reference number of the host whose vehicle is booked; leave "" if unknown.
        vehicle_id: Id class — the listing reference number of the booked vehicle; leave "" if unknown.
        election_id: Id class — the reference number of the protection election attached to the trip; leave "" if unknown.
    """
    match = {k: v for k, v in {"booking_id": booking_id, "customer_id": customer_id,
                               "host_customer_id": host_customer_id, "vehicle_id": vehicle_id,
                               "election_id": election_id}.items() if v}
    rows = ctx.find("trips_bookings", **match)
    return str(rows) if rows else f"No trip bookings for {match}."


@tool(owner="agent", rw="read")
def find_trips_charges(ctx: ToolContext, charge_id: str = "", booking_id: str = "",
                       customer_id: str = "", source_charge_id: str = "") -> str:
    """Retrieve the priced lines raised on a trip — the base rate, the marketplace trip fee,
    deposits, surcharges, extensions, mileage and fuel settlements, late returns, cancellation
    fees and every refund. Each line carries the date it was posted, the money it moved, what it
    was priced on, the units and per-unit rate behind it, when it fell due, how the money was
    taken and any ground on which it was waived. Search by the charge reference, by the booking,
    by the guest, or by the earlier line a reversal was raised against.

    Args:
        charge_id: Id class — the reference number of the charge line itself; leave "" if unknown.
        booking_id: Id class — the booking reference the lines belong to; leave "" if unknown.
        customer_id: Id class — the member reference number of the guest charged; leave "" if unknown.
        source_charge_id: Id class — the reference number of the original line a credit or reversal was raised against; leave "" if unknown.
    """
    match = {k: v for k, v in {"charge_id": charge_id, "booking_id": booking_id,
                               "customer_id": customer_id,
                               "source_charge_id": source_charge_id}.items() if v}
    rows = ctx.find("trips_charges", **match)
    return str(rows) if rows else f"No trip charge lines for {match}."


@tool(owner="agent", rw="read")
def find_trips_usage(ctx: ToolContext, usage_id: str = "", booking_id: str = "",
                     customer_id: str = "") -> str:
    """Retrieve the mileage and fuel records of a trip — the included miles granted at booking,
    at extension or by a purchased package, the odometer readings taken at each handover and the
    miles they consumed, and the fuel or battery level read at collection and at return. Each
    record shows the moment in the trip it was captured at and where the reading came from, so a
    telematics figure and a figure the host or guest reported can be told apart.

    Args:
        usage_id: Id class — the reference number of the usage record itself; leave "" if unknown.
        booking_id: Id class — the booking reference the records belong to; leave "" if unknown.
        customer_id: Id class — the member reference number of the guest on the trip; leave "" if unknown.
    """
    match = {k: v for k, v in {"usage_id": usage_id, "booking_id": booking_id,
                               "customer_id": customer_id}.items() if v}
    rows = ctx.find("trips_usage", **match)
    return str(rows) if rows else f"No trip usage records for {match}."


@tool(owner="agent", rw="read")
def find_trips_extension_requests(ctx: ToolContext, extension_request_id: str = "",
                                  booking_id: str = "", customer_id: str = "") -> str:
    """Retrieve requests from guests to keep a vehicle longer — the new return date asked for,
    how many further hours that is, the price quoted for the extra time, how far the request has
    got with the host, and when it was lodged. Search by the request reference, by the booking it
    belongs to, or by the guest who made it.

    Args:
        extension_request_id: Id class — the reference number of the extension request itself; leave "" if unknown.
        booking_id: Id class — the booking reference the request belongs to; leave "" if unknown.
        customer_id: Id class — the member reference number of the guest who asked; leave "" if unknown.
    """
    match = {k: v for k, v in {"extension_request_id": extension_request_id,
                               "booking_id": booking_id, "customer_id": customer_id}.items() if v}
    rows = ctx.find("trips_extension_requests", **match)
    return str(rows) if rows else f"No extension requests for {match}."


# ---------------------------------------------------------------- host protection records

@tool(owner="agent", rw="read")
def find_hostplan_enrollments(ctx: ToolContext, enrollment_id: str = "", customer_id: str = "",
                              vehicle_id: str = "") -> str:
    """Retrieve the protection enrolments a host holds on their vehicles — which plan covers
    which vehicle, whether cover is live, paused or has fallen away, the dates it was applied
    for, took effect and ceased, the territory it is written for, the value the host declared,
    how long the enrolment has been free of settled claims, and what is currently owed to the
    host or by them. Search by the enrolment reference, by the host, or by the vehicle covered.

    Args:
        enrollment_id: Id class — the reference number of the protection enrolment itself; leave "" if unknown.
        customer_id: Id class — the member reference number of the host; leave "" if unknown.
        vehicle_id: Id class — the listing reference number of the covered vehicle; leave "" if unknown.
    """
    match = {k: v for k, v in {"enrollment_id": enrollment_id, "customer_id": customer_id,
                               "vehicle_id": vehicle_id}.items() if v}
    rows = ctx.find("hostplan_enrollments", **match)
    return str(rows) if rows else f"No protection enrolments for {match}."


@tool(owner="agent", rw="read")
def find_hostplan_claims(ctx: ToolContext, claim_id: str = "", enrollment_id: str = "",
                         customer_id: str = "", booking_id: str = "",
                         source_claim_id: str = "") -> str:
    """Retrieve the damage claim records made under a host's protection — the filing, the
    appraisal and what it valued the loss at, any supplement added afterwards, refusals and
    withdrawals, the deductible raised against the host, the money paid out to them and any
    recovery received. Each record carries the date, the date of loss, the trip the loss happened
    on, the kind of damage, who was found responsible, how the loss was valued, how much money it
    moved and who took the decision. Search by the claim reference, by the enrolment, by the host,
    by the trip, or by the original claim a later record was raised against.

    Args:
        claim_id: Id class — the reference number of the claim record itself; leave "" if unknown.
        enrollment_id: Id class — the protection enrolment reference the claim is made under; leave "" if unknown.
        customer_id: Id class — the member reference number of the host claiming; leave "" if unknown.
        booking_id: Id class — the booking reference of the trip the loss happened on; leave "" if unknown.
        source_claim_id: Id class — the reference number of the original claim a supplement, payment or recovery belongs to; leave "" if unknown.
    """
    match = {k: v for k, v in {"claim_id": claim_id, "enrollment_id": enrollment_id,
                               "customer_id": customer_id, "booking_id": booking_id,
                               "source_claim_id": source_claim_id}.items() if v}
    rows = ctx.find("hostplan_claims", **match)
    return str(rows) if rows else f"No claim records for {match}."


@tool(owner="agent", rw="read")
def find_hostplan_claim_intake(ctx: ToolContext, claim_intake_id: str = "", customer_id: str = "",
                               enrollment_id: str = "", booking_id: str = "") -> str:
    """Retrieve the damage reports hosts have lodged before a claim is opened — what kind of
    damage was reported, against which enrolment and which trip, how many photographs and
    documents are attached, how far the report has got, and when it was lodged. Search by the
    report reference, by the host, by the enrolment, or by the trip the damage is attributed to.

    Args:
        claim_intake_id: Id class — the reference number of the damage report itself; leave "" if unknown.
        customer_id: Id class — the member reference number of the host who lodged it; leave "" if unknown.
        enrollment_id: Id class — the protection enrolment reference the report will be filed under; leave "" if unknown.
        booking_id: Id class — the booking reference of the trip the damage is attributed to; leave "" if unknown.
    """
    match = {k: v for k, v in {"claim_intake_id": claim_intake_id, "customer_id": customer_id,
                               "enrollment_id": enrollment_id, "booking_id": booking_id}.items() if v}
    rows = ctx.find("hostplan_claim_intake", **match)
    return str(rows) if rows else f"No damage reports for {match}."


# ---------------------------------------------------------------- guest protection records

@tool(owner="agent", rw="read")
def find_guestplan_elections(ctx: ToolContext, election_id: str = "", customer_id: str = "",
                             booking_id: str = "") -> str:
    """Retrieve the protection a guest chose for a trip — which level was quoted or elected, how
    far the election has got from quote through to completion, the dates it was chosen, took
    effect and ended, how many trip days it has been charged for, what protection fee and what
    deductible are outstanding, how many additional drivers were declared, the guest's own insurer
    where they declined marketplace cover, and the ground on which an election was voided. Search
    by the election reference, by the guest, or by the trip it is attached to.

    Args:
        election_id: Id class — the reference number of the protection election itself; leave "" if unknown.
        customer_id: Id class — the member reference number of the guest; leave "" if unknown.
        booking_id: Id class — the booking reference of the trip the protection covers; leave "" if unknown.
    """
    match = {k: v for k, v in {"election_id": election_id, "customer_id": customer_id,
                               "booking_id": booking_id}.items() if v}
    rows = ctx.find("guestplan_elections", **match)
    return str(rows) if rows else f"No protection elections for {match}."


@tool(owner="agent", rw="read")
def find_guestplan_charges(ctx: ToolContext, protection_charge_id: str = "", election_id: str = "",
                           customer_id: str = "", booking_id: str = "", covered_claim_id: str = "",
                           source_charge_id: str = "") -> str:
    """Retrieve the lines raised on a guest's protection — the daily protection fee, the
    difference charged or credited when the level changed, additional driver fees, the deductible
    raised when a loss was settled against the guest, any waiver of it, and refunds. Each line
    shows the date, the money moved, what it was priced on, how many trip days it covers, which
    stretch of the trip it belongs to and why it was raised. Search by the line reference, by the
    election, by the guest, by the trip, by the claim a deductible belongs to, or by the earlier
    line a credit was raised against.

    Args:
        protection_charge_id: Id class — the reference number of the protection line itself; leave "" if unknown.
        election_id: Id class — the protection election reference the lines belong to; leave "" if unknown.
        customer_id: Id class — the member reference number of the guest charged; leave "" if unknown.
        booking_id: Id class — the booking reference of the trip the protection covers; leave "" if unknown.
        covered_claim_id: Id class — the claim reference a deductible or waiver belongs to; leave "" if unknown.
        source_charge_id: Id class — the reference number of the original line a credit or refund was raised against; leave "" if unknown.
    """
    match = {k: v for k, v in {"protection_charge_id": protection_charge_id,
                               "election_id": election_id, "customer_id": customer_id,
                               "booking_id": booking_id, "covered_claim_id": covered_claim_id,
                               "source_charge_id": source_charge_id}.items() if v}
    rows = ctx.find("guestplan_charges", **match)
    return str(rows) if rows else f"No protection charge lines for {match}."


@tool(owner="agent", rw="read")
def find_guestplan_change_requests(ctx: ToolContext, change_request_id: str = "",
                                   customer_id: str = "", election_id: str = "",
                                   booking_id: str = "") -> str:
    """Retrieve requests from guests to move to a different protection level — which level they
    asked for, how far the request has got, the price difference quoted for the remaining trip
    days, and when it was lodged. Search by the request reference, by the guest, by the election
    being changed, or by the trip it belongs to.

    Args:
        change_request_id: Id class — the reference number of the change request itself; leave "" if unknown.
        customer_id: Id class — the member reference number of the guest who asked; leave "" if unknown.
        election_id: Id class — the protection election reference being changed; leave "" if unknown.
        booking_id: Id class — the booking reference of the trip the election is attached to; leave "" if unknown.
    """
    match = {k: v for k, v in {"change_request_id": change_request_id, "customer_id": customer_id,
                               "election_id": election_id, "booking_id": booking_id}.items() if v}
    rows = ctx.find("guestplan_change_requests", **match)
    return str(rows) if rows else f"No protection change requests for {match}."


# ---------------------------------------------------------------- payout records

@tool(owner="agent", rw="read")
def find_payouts_accounts(ctx: ToolContext, payout_account_id: str = "", customer_id: str = "") -> str:
    """Retrieve the account a host's earnings settle through — the payout schedule it runs on,
    whether it is live, on hold, suspended or closed, when it was opened and closed, the last four
    digits of the deposit account and the default way money leaves it, the balance free to be paid
    out and the balance held back in reserve, the next date it is due to be swept, the state of the
    tax documentation, how statements are delivered and any ground currently stopping money from
    leaving. Search by the account reference or by the host.

    Args:
        payout_account_id: Id class — the reference number of the payout account itself; leave "" if unknown.
        customer_id: Id class — the member reference number of the host; leave "" if unknown.
    """
    match = {k: v for k, v in {"payout_account_id": payout_account_id,
                               "customer_id": customer_id}.items() if v}
    rows = ctx.find("payouts_accounts", **match)
    return str(rows) if rows else f"No payout accounts for {match}."


@tool(owner="agent", rw="read")
def find_payouts_ledger(ctx: ToolContext, ledger_id: str = "", payout_account_id: str = "",
                        customer_id: str = "", booking_id: str = "",
                        source_ledger_id: str = "") -> str:
    """Retrieve the entries booked to a host's payout account — earnings credited from trips and
    extensions, the marketplace commission and other deductions, reserves held back and released,
    transfers sent out and any that came back, and corrections. Each entry shows the date, the
    money it moved, what it was for, the trip behind it where there is one, how the money was sent,
    why anything was withheld, the statement month it falls in and the bank reference the host can
    quote. Search by the entry reference, by the account, by the host, by the trip, or by the
    earlier entry a release or correction was raised against.

    Args:
        ledger_id: Id class — the reference number of the ledger entry itself; leave "" if unknown.
        payout_account_id: Id class — the payout account reference the entries are booked to; leave "" if unknown.
        customer_id: Id class — the member reference number of the host; leave "" if unknown.
        booking_id: Id class — the booking reference of the trip the entry arises from; leave "" if unknown.
        source_ledger_id: Id class — the reference number of the earlier entry a release, return or correction belongs to; leave "" if unknown.
    """
    match = {k: v for k, v in {"ledger_id": ledger_id, "payout_account_id": payout_account_id,
                               "customer_id": customer_id, "booking_id": booking_id,
                               "source_ledger_id": source_ledger_id}.items() if v}
    rows = ctx.find("payouts_ledger", **match)
    return str(rows) if rows else f"No payout ledger entries for {match}."


@tool(owner="agent", rw="read")
def find_payouts_requests(ctx: ToolContext, payout_request_id: str = "", customer_id: str = "",
                          payout_account_id: str = "") -> str:
    """Retrieve requests from hosts to be paid — how much they asked to draw, how they asked to be
    paid, how far the request has got, and when it was lodged. Search by the request reference, by
    the host, or by the payout account it was made against.

    Args:
        payout_request_id: Id class — the reference number of the payout request itself; leave "" if unknown.
        customer_id: Id class — the member reference number of the host who asked; leave "" if unknown.
        payout_account_id: Id class — the payout account reference the request was made against; leave "" if unknown.
    """
    match = {k: v for k, v in {"payout_request_id": payout_request_id, "customer_id": customer_id,
                               "payout_account_id": payout_account_id}.items() if v}
    rows = ctx.find("payouts_requests", **match)
    return str(rows) if rows else f"No payout requests for {match}."


# ---------------------------------------------------------------- listing records

@tool(owner="agent", rw="read")
def find_listings_vehicles(ctx: ToolContext, vehicle_id: str = "", customer_id: str = "") -> str:
    """Retrieve the vehicles a host lists — the value class the listing sits in and whether it is
    in draft, under review, live, snoozed, suspended or taken down, the make, model, model year and
    the last six characters of the vehicle identification number, the odometer, the marketplace
    valuation and the daily price asked, how the vehicle is titled and any lender recorded on it,
    where it is based, its seats, fuel and transmission, when its registration expires, when the
    next inspection falls due and how many miles are left before it does, and any ground on which
    the listing is suspended. Search by the listing reference or by the host who owns it.

    Args:
        vehicle_id: Id class — the listing reference number of the vehicle itself; leave "" if unknown.
        customer_id: Id class — the member reference number of the host who owns it; leave "" if unknown.
    """
    match = {k: v for k, v in {"vehicle_id": vehicle_id, "customer_id": customer_id}.items() if v}
    rows = ctx.find("listings_vehicles", **match)
    return str(rows) if rows else f"No vehicle listings for {match}."


@tool(owner="agent", rw="read")
def find_listings_inspections(ctx: ToolContext, inspection_id: str = "", vehicle_id: str = "",
                              customer_id: str = "", booking_id: str = "",
                              source_inspection_id: str = "") -> str:
    """Retrieve the condition records held against a vehicle — completed inspections and what they
    found, odometer readings and the miles they consumed of the inspection interval, faults
    reported by guests, hosts, workshops or recall notices, marketplace valuations and the class
    they put the vehicle in, and documents checked and verified. Each record shows its date, how it
    was produced, the photographs attached and the interval it granted. Search by the record
    reference, by the vehicle, by the host, by the trip whose handover produced the reading, or by
    the earlier record a re-examination belongs to.

    Args:
        inspection_id: Id class — the reference number of the condition record itself; leave "" if unknown.
        vehicle_id: Id class — the listing reference number of the vehicle; leave "" if unknown.
        customer_id: Id class — the member reference number of the host who owns it; leave "" if unknown.
        booking_id: Id class — the booking reference of the trip whose handover produced the record; leave "" if unknown.
        source_inspection_id: Id class — the reference number of the earlier record this one re-examines or corrects; leave "" if unknown.
    """
    match = {k: v for k, v in {"inspection_id": inspection_id, "vehicle_id": vehicle_id,
                               "customer_id": customer_id, "booking_id": booking_id,
                               "source_inspection_id": source_inspection_id}.items() if v}
    rows = ctx.find("listings_inspections", **match)
    return str(rows) if rows else f"No vehicle condition records for {match}."


@tool(owner="agent", rw="read")
def find_listings_review_queue(ctx: ToolContext, review_id: str = "", customer_id: str = "",
                               vehicle_id: str = "") -> str:
    """Retrieve listing review cases — why the listing was put in front of a reviewer, whether it
    is a new listing, a value class change, a reported fault, an expiring document, a request to
    put a suspended vehicle back or a compliance audit, how far the case has got, how many
    supporting documents the host attached and when it was raised. Search by the case reference, by
    the host, or by the listing under review.

    Args:
        review_id: Id class — the reference number of the review case itself; leave "" if unknown.
        customer_id: Id class — the member reference number of the host; leave "" if unknown.
        vehicle_id: Id class — the listing reference number under review; leave "" if unknown.
    """
    match = {k: v for k, v in {"review_id": review_id, "customer_id": customer_id,
                               "vehicle_id": vehicle_id}.items() if v}
    rows = ctx.find("listings_review_queue", **match)
    return str(rows) if rows else f"No listing review cases for {match}."


# ---------------------------------------------------------------- roadside records

@tool(owner="agent", rw="read")
def find_roadside_subscriptions(ctx: ToolContext, subscription_id: str = "", customer_id: str = "",
                                vehicle_id: str = "") -> str:
    """Retrieve roadside assistance subscriptions — which plan covers which vehicle, whether cover
    is live, paused or has fallen away, when it began, when it ends and when the term next renews,
    how many callouts are still included, the territory it dispatches in and how the member came to
    hold it. Search by the subscription reference, by the member, or by the covered vehicle.

    Args:
        subscription_id: Id class — the reference number of the subscription itself; leave "" if unknown.
        customer_id: Id class — the member reference number of the holder; leave "" if unknown.
        vehicle_id: Id class — the listing reference number of the covered vehicle; leave "" if unknown.
    """
    match = {k: v for k, v in {"subscription_id": subscription_id, "customer_id": customer_id,
                               "vehicle_id": vehicle_id}.items() if v}
    rows = ctx.find("roadside_subscriptions", **match)
    return str(rows) if rows else f"No roadside subscriptions for {match}."


@tool(owner="agent", rw="read")
def find_roadside_callouts(ctx: ToolContext, callout_id: str = "", subscription_id: str = "",
                           customer_id: str = "", booking_id: str = "",
                           source_callout_id: str = "") -> str:
    """Retrieve roadside assistance records — callouts dispatched and completed, the assistance
    given, the distance a vehicle was towed, callouts granted to the subscription, charges raised
    for an excess or an overage, and callouts that were called off. Each record shows its date, how
    assistance was requested, how it ended, the callouts it granted or consumed and the recovery
    operator's job reference. Search by the record reference, by the subscription, by the member, by
    the trip the vehicle was on, or by the dispatch a later record belongs to.

    Args:
        callout_id: Id class — the reference number of the callout record itself; leave "" if unknown.
        subscription_id: Id class — the subscription reference the call was made under; leave "" if unknown.
        customer_id: Id class — the member reference number of the caller; leave "" if unknown.
        booking_id: Id class — the booking reference of the trip the vehicle was on; leave "" if unknown.
        source_callout_id: Id class — the reference number of the dispatch a completion, charge or cancellation belongs to; leave "" if unknown.
    """
    match = {k: v for k, v in {"callout_id": callout_id, "subscription_id": subscription_id,
                               "customer_id": customer_id, "booking_id": booking_id,
                               "source_callout_id": source_callout_id}.items() if v}
    rows = ctx.find("roadside_callouts", **match)
    return str(rows) if rows else f"No roadside callout records for {match}."


# ---------------------------------------------------------------- care plan records

@tool(owner="agent", rw="read")
def find_service_plans(ctx: ToolContext, care_plan_id: str = "", customer_id: str = "",
                       vehicle_id: str = "") -> str:
    """Retrieve vehicle care plans — which plan services which vehicle, whether it is live, paused
    or has fallen away, when it began and ended, when the next included service falls due, how many
    included services are still unused, the day of the month it is billed on and the workshop the
    host prefers. Search by the care plan reference, by the host, or by the vehicle it services.

    Args:
        care_plan_id: Id class — the reference number of the care plan itself; leave "" if unknown.
        customer_id: Id class — the member reference number of the host; leave "" if unknown.
        vehicle_id: Id class — the listing reference number of the serviced vehicle; leave "" if unknown.
    """
    match = {k: v for k, v in {"care_plan_id": care_plan_id, "customer_id": customer_id,
                               "vehicle_id": vehicle_id}.items() if v}
    rows = ctx.find("service_plans", **match)
    return str(rows) if rows else f"No care plans for {match}."


@tool(owner="agent", rw="read")
def find_service_visits(ctx: ToolContext, visit_id: str = "", care_plan_id: str = "",
                        customer_id: str = "", vehicle_id: str = "",
                        source_visit_id: str = "") -> str:
    """Retrieve workshop records held against a care plan — completed visits and the work carried
    out, included services granted to the plan, invoices raised for an excess or for work outside
    the allowance, visits that did not happen, and the monthly plan billing. Each record shows its
    date, the work, where it was carried out, the services it granted or consumed, the odometer
    recorded and how it ended. Search by the record reference, by the care plan, by the host, by the
    vehicle, or by the booking a later record belongs to.

    Args:
        visit_id: Id class — the reference number of the workshop record itself; leave "" if unknown.
        care_plan_id: Id class — the care plan reference the record belongs to; leave "" if unknown.
        customer_id: Id class — the member reference number of the host; leave "" if unknown.
        vehicle_id: Id class — the listing reference number of the serviced vehicle; leave "" if unknown.
        source_visit_id: Id class — the reference number of the earlier booking or visit this record belongs to; leave "" if unknown.
    """
    match = {k: v for k, v in {"visit_id": visit_id, "care_plan_id": care_plan_id,
                               "customer_id": customer_id, "vehicle_id": vehicle_id,
                               "source_visit_id": source_visit_id}.items() if v}
    rows = ctx.find("service_visits", **match)
    return str(rows) if rows else f"No workshop records for {match}."


# ---------------------------------------------------------------- service log records

@tool(owner="agent", rw="read")
def find_identity_verifications(ctx: ToolContext, verification_id: str = "",
                                customer_id: str = "") -> str:
    """Retrieve the record of identity checks carried out on a member — whether the check passed
    and the moment of the most recent one. Search by the verification reference or by the member.

    Args:
        verification_id: Id class — the reference number of the verification record itself; leave "" if unknown.
        customer_id: Id class — the member reference number checked; leave "" if unknown.
    """
    match = {k: v for k, v in {"verification_id": verification_id,
                               "customer_id": customer_id}.items() if v}
    rows = ctx.find("identity_verifications", **match)
    return str(rows) if rows else f"No identity verification records for {match}."


@tool(owner="agent", rw="read")
def find_agent_handoffs(ctx: ToolContext, handoff_id: str = "", customer_id: str = "") -> str:
    """Retrieve the record of conversations handed over to a human representative — the reason the
    handover was made and the moment it happened. Search by the handover reference or by the member.

    Args:
        handoff_id: Id class — the reference number of the handover record itself; leave "" if unknown.
        customer_id: Id class — the member reference number handed over; leave "" if unknown.
    """
    match = {k: v for k, v in {"handoff_id": handoff_id, "customer_id": customer_id}.items() if v}
    rows = ctx.find("agent_handoffs", **match)
    return str(rows) if rows else f"No handover records for {match}."


# ---------------------------------------------------------------- identity verification

@tool(owner="agent", rw="write")
def verify_member_identity(ctx: ToolContext, customer_id: str, phone_number: str = "",
                           email: str = "", date_of_birth: str = "",
                           driver_licence_number: str = "", postal_code: str = "",
                           account_opened_date: str = "") -> str:
    """Confirm that the caller is the member whose account is being discussed, and record the
    outcome of that check. Nothing that moves money, changes a trip, alters a listing or touches a
    payout may be done before this check has passed. The comparison is made here rather than
    judged in conversation: each piece of information the caller offers is checked against what the
    profile holds, and the check passes only when at least two of them match. The member reference
    number is used solely to fetch the profile and never counts as one of the matches. Callers
    usually remember only some of what is on file, so pass exactly what was said, word for word,
    and leave the rest blank. Where a first attempt falls short and a later attempt succeeds with
    more information, the successful outcome stands.

    Args:
        customer_id: Id class — the member reference number read from the member profile lookup. Required, never blank, used only to fetch the profile and not counted toward the matches.
        phone_number: The mobile number on the profile, 10 digits with no separators; leave "" if not stated.
        email: The email address on the profile, copied exactly as the caller says it; leave "" if not stated.
        date_of_birth: The date of birth on the licence held on file, as YYYY-MM-DD; leave "" if not stated.
        driver_licence_number: The driving licence number on the profile, copied exactly; leave "" if not stated.
        postal_code: The 5-digit ZIP code of the billing address on the profile; leave "" if not stated.
        account_opened_date: The date the member profile was opened, as YYYY-MM-DD; leave "" if not stated.
    """
    if not customer_id:
        return "Error: customer_id is required; find the member first and pass their reference number."
    rows = ctx.find("customers", customer_id=customer_id)
    if not rows:
        return f"Error: no member {customer_id}; cannot verify."
    rec = rows[0]
    # The tool owns the comparison. The locator customer_id is deliberately absent from
    # `supplied` — fetching a profile is not proving identity.
    supplied = {"phone_number": phone_number, "email": email, "date_of_birth": date_of_birth,
                "driver_licence_number": driver_licence_number, "postal_code": postal_code,
                "account_opened_date": account_opened_date}
    matched = sum(1 for field, value in supplied.items()
                  if value and str(rec.get(field)) == str(value))
    verified = matched >= 2
    rid = ctx.make_id("ver_", customer_id)
    # Store only the reproducible outcome, never the match count. Upsert and never downgrade:
    # a caller who fails once and then passes with more detail must end up recorded as verified.
    prior = ctx.find("identity_verifications", verification_id=rid)
    verified = verified or bool(prior and prior[0].get("verified"))
    if prior:
        ctx.update("identity_verifications", rid, verified=verified, verified_at=ctx.now())
    else:
        ctx.create("identity_verifications", rid, verification_id=rid, customer_id=customer_id,
                   verified=verified, verified_at=ctx.now())
    return (f"Identity confirmed for {customer_id} ({matched} detail(s) matched)." if verified
            else f"Identity not confirmed for {customer_id} (only {matched} of the 2 required details matched). "
                 "Ask the caller for another detail held on the profile and try again.")


# ---------------------------------------------------------------- human handover

@tool(owner="agent", rw="write")
def transfer_to_human_representative(ctx: ToolContext, customer_id: str, reason: str) -> str:
    """Pass the conversation to a human representative and record that it was passed on, with the
    reason. Use it in exactly two situations: where nothing in marketplace policy can resolve what
    the member is asking for, and where the member has asked to speak to a person at least twice in
    the same conversation.

    Args:
        customer_id: Id class — the member reference number read from the member profile lookup; the profile must exist.
        reason: Enum class — one of POLICY_NOT_COVERED or CUSTOMER_REQUESTED, never free text.
            POLICY_NOT_COVERED — no marketplace policy offers a way to resolve the request;
            CUSTOMER_REQUESTED — the member has explicitly asked for a human representative at least 2 times.
    """
    allowed = {"POLICY_NOT_COVERED", "CUSTOMER_REQUESTED"}
    if reason not in allowed:
        return f"Error: unknown handover reason '{reason}'. Valid: {', '.join(sorted(allowed))}."
    if not ctx.find("customers", customer_id=customer_id):
        return f"Error: no member {customer_id}; cannot record the handover."
    rid = ctx.make_id("hof_", customer_id, reason)
    ctx.create("agent_handoffs", rid, handoff_id=rid, customer_id=customer_id,
               reason=reason, created_at=ctx.now())
    return f"Handed over to a human representative for {customer_id} ({reason})."

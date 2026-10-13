"""Shared tools for env_0056_ride_hailing_platform (Wayfare Mobility rider and driver support).

Every tool here is always available to its owner. This module holds the complete record-lookup
layer (one finder per record type; the customer finder doubles as the identity entry), the
identity-verification write and the transfer-to-human write. Customer-initiated actions live in
each difficulty's task tools, never here.
"""

from erlbench import ToolContext, tool


def _pick(**criteria):
    # keep only the criteria the caller actually supplied
    return {k: v for k, v in criteria.items() if v}


def _report(rows, match, label):
    if rows:
        return str(rows)
    return f"No {label} found for {match}." if match else f"No {label} on file."


# ---------------------------------------------------------------- identity entry
@tool(owner="agent", rw="read")
def find_customers(ctx: ToolContext, customer_id: str = "", phone_number: str = "", email: str = "",
                   name: str = "") -> str:
    """Look up a Wayfare customer profile to establish whose account this conversation is about.

    A profile belongs to one person and covers both sides of the platform: it shows the name, the
    registered mobile number and email, the date of birth, the last four digits of the default
    payment card, the date the profile was opened, whether the person rides, drives or both, the
    home metro market and the current rider rating. Search by the customer reference number when
    it is already known, or by what the caller naturally states: the mobile number, the email or
    the full name. Every criterion is optional; supply whichever are known. Spacing, punctuation and
    letter case in what the caller says do not prevent a match. When several profiles match, the
    reply asks for one more detail. Finding a profile does not confirm that the caller is its owner.

    Args:
        customer_id: The customer reference number; leave "" if unknown.
        phone_number: The registered mobile number, 10 digits (for example 3035550142); leave "" if not provided.
        email: The registered email address; leave "" if not provided.
        name: The full name on the profile; leave "" if not provided.
    """
    match = _pick(customer_id=customer_id, phone_number=phone_number, email=email, name=name)
    if not match:
        return "Error: provide at least one detail (reference number, mobile number, email or name) to find the customer."
    rows = ctx.fuzzy_find("customers", **match)
    if not rows:
        return f"No customer matches {match}."
    if len(rows) > 1:
        return f"Error: {len(rows)} customers match {match}; ask the caller for one more detail to tell them apart."
    return str(rows[0])


@tool(owner="agent", rw="write")
def verify_customer_identity(ctx: ToolContext, customer_id: str, phone_number: str = "", email: str = "",
                             date_of_birth: str = "", payment_card_last4: str = "",
                             account_created_date: str = "") -> str:
    """Verify that the caller is the owner of a Wayfare profile and record the outcome.

    Identity must be verified before any account details are discussed or any charge, refund,
    payout, membership or account standing is changed. This tool performs the comparison itself:
    each detail the caller states is checked against the profile, and verification passes only
    when at least 2 of the stated details match. The customer reference number only identifies
    which profile to check and never counts as a match; the name is not accepted as a proof of
    identity. Callers usually know only some details, so pass exactly what the caller said and
    leave the rest "". If an attempt fails, ask for another detail and call again; once a caller
    has passed, the profile stays verified.

    Args:
        customer_id: The customer reference number of the profile being verified, as shown by the profile lookup. Required.
        phone_number: The mobile number the caller states, 10 digits with no spaces or punctuation; leave "" if not stated.
        email: The email address the caller states, exactly as given; leave "" if not stated.
        date_of_birth: The date of birth the caller states, as YYYY-MM-DD; leave "" if not stated.
        payment_card_last4: The last four digits of the default payment card the caller states, 4 digits; leave "" if not stated.
        account_created_date: The date the caller says the profile was opened, as YYYY-MM-DD; leave "" if not stated.
    """
    if not customer_id:
        return "Error: customer_id is required; look the customer up first and pass their reference number."
    rows = ctx.find("customers", customer_id=customer_id)
    if not rows:
        return f"Error: no customer {customer_id}; cannot verify."
    rec = rows[0]
    # The tool owns the comparison; the locator customer_id is never part of `supplied`.
    supplied = {"phone_number": phone_number, "email": email, "date_of_birth": date_of_birth,
                "payment_card_last4": payment_card_last4, "account_created_date": account_created_date}
    matched = sum(
        1 for field, value in supplied.items()
        if value and (str(rec.get(field) or "").strip().lower() == str(value).strip().lower()
                      if field == "email"
                      else str(rec.get(field) or "").strip() == str(value).strip()))
    verified = matched >= 2
    rid = ctx.make_id("ver_", customer_id)
    # Store only the reproducible outcome; upsert and never downgrade a pass.
    prior = ctx.find("identity_verifications", verification_id=rid)
    verified = verified or bool(prior and prior[0].get("verified"))
    if prior:
        ctx.update("identity_verifications", rid, verified=verified, verified_at=ctx.now())
    else:
        ctx.create("identity_verifications", rid, verification_id=rid, customer_id=customer_id,
                   verified=verified, verified_at=ctx.now())
    if verified:
        return f"Identity verified for {customer_id}."
    return (f"Identity NOT verified for {customer_id}: only {matched} of the required 2 details matched. "
            "Ask the caller for another detail on the profile and try again.")


@tool(owner="agent", rw="write")
def transfer_to_human_agent(ctx: ToolContext, customer_id: str, reason: str) -> str:
    """Hand the customer over to a human Wayfare support specialist and record why.

    Use POLICY_NOT_COVERED when the request is one that no Wayfare rule allows you to resolve,
    and CUSTOMER_REQUESTED when the customer has explicitly asked for a human representative 2
    times in this conversation. The handoff is recorded against the customer's profile.

    Args:
        customer_id: The customer reference number, as shown by the profile lookup.
        reason: Exactly one of POLICY_NOT_COVERED or CUSTOMER_REQUESTED. POLICY_NOT_COVERED: no
            Wayfare rule can resolve the request. CUSTOMER_REQUESTED: the customer has asked for a
            human representative 2 times.
    """
    allowed = {"POLICY_NOT_COVERED", "CUSTOMER_REQUESTED"}
    if reason not in allowed:
        return f"Error: unknown handoff reason '{reason}'. Valid: {', '.join(sorted(allowed))}."
    if not ctx.find("customers", customer_id=customer_id):
        return f"Error: no customer {customer_id}; cannot record the handoff."
    rid = ctx.make_id("hof_", customer_id, reason)
    ctx.create("human_handoffs", rid, handoff_id=rid, customer_id=customer_id, reason=reason, created_at=ctx.now())
    return f"Handoff to a human specialist recorded for {customer_id} ({reason})."


@tool(owner="agent", rw="read")
def find_identity_verifications(ctx: ToolContext, verification_id: str = "", customer_id: str = "") -> str:
    """Look up the identity verification outcome recorded for a customer in this conversation.

    The record shows whether the caller has passed verification and when the latest attempt was
    made. Every criterion is optional.

    Args:
        verification_id: The verification record reference number; leave "" if unknown.
        customer_id: The customer reference number; leave "" if unknown.
    """
    match = _pick(verification_id=verification_id, customer_id=customer_id)
    rows = ctx.find("identity_verifications", **match)
    return _report(rows, match, "identity verification records")


@tool(owner="agent", rw="read")
def find_human_handoffs(ctx: ToolContext, handoff_id: str = "", customer_id: str = "") -> str:
    """Look up handoffs to a human specialist recorded for a customer, with their reason and time.

    Every criterion is optional.

    Args:
        handoff_id: The handoff record reference number; leave "" if unknown.
        customer_id: The customer reference number; leave "" if unknown.
    """
    match = _pick(handoff_id=handoff_id, customer_id=customer_id)
    rows = ctx.find("human_handoffs", **match)
    return _report(rows, match, "handoff records")


# ---------------------------------------------------------------- Wayfare Pass
@tool(owner="agent", rw="read")
def find_pass_memberships(ctx: ToolContext, pass_membership_id: str = "", customer_id: str = "") -> str:
    """Look up Wayfare Pass memberships: the plan held, its status, how it was taken out, trial and
    billing-period dates, auto-renew setting, student verification date, pause dates, cancellation
    date, the Pass ride credit balance and the net membership fees paid.

    Every criterion is optional; supply whichever reference numbers are known.

    Args:
        pass_membership_id: The membership reference number; leave "" if unknown.
        customer_id: The member's customer reference number; leave "" if unknown.
    """
    match = _pick(pass_membership_id=pass_membership_id, customer_id=customer_id)
    rows = ctx.find("pass_memberships", **match)
    return _report(rows, match, "Wayfare Pass memberships")


@tool(owner="agent", rw="read")
def find_pass_events(ctx: ToolContext, pass_event_id: str = "", pass_membership_id: str = "", customer_id: str = "",
                     original_event_id: str = "", trip_id: str = "") -> str:
    """Look up the Wayfare Pass membership ledger: membership fee charges and refunds, declined
    payment attempts, and Pass ride credits earned, redeemed or forfeited, each with its date,
    amount, billing period, reason codes and the trip it relates to.

    Every criterion is optional; supply whichever reference numbers are known.

    Args:
        pass_event_id: The ledger entry reference number; leave "" if unknown.
        pass_membership_id: The membership reference number; leave "" if unknown.
        customer_id: The member's customer reference number; leave "" if unknown.
        original_event_id: The reference number of the fee charge or credit an entry returns or reverses; leave "" if unknown.
        trip_id: The trip reference number a credit relates to; leave "" if unknown.
    """
    match = _pick(pass_event_id=pass_event_id, pass_membership_id=pass_membership_id, customer_id=customer_id, original_event_id=original_event_id, trip_id=trip_id)
    rows = ctx.find("pass_events", **match)
    return _report(rows, match, "Wayfare Pass ledger entries")


# ---------------------------------------------------------------- trips
@tool(owner="agent", rw="read")
def find_trips(ctx: ToolContext, trip_id: str = "", customer_id: str = "", driver_customer_id: str = "",
               driver_agreement_id: str = "", pass_membership_id: str = "") -> str:
    """Look up trips: the ride option, status, on-demand or reserved booking, market, the request,
    acceptance, arrival, pickup, drop-off and cancellation times, the driver's original pickup
    estimate, airport details, estimated and actual distance and duration, whether the rider changed
    the route, the busy-time multiplier, the upfront fare, seats requested, the net amount charged
    and any unpaid amount.

    Search by the trip itself, the rider, the driver, the driver's agreement or the rider's Wayfare
    Pass membership. Every criterion is optional.

    Args:
        trip_id: The trip reference number; leave "" if unknown.
        customer_id: The rider's customer reference number; leave "" if unknown.
        driver_customer_id: The driver's customer reference number; leave "" if unknown.
        driver_agreement_id: The driver services agreement reference number; leave "" if unknown.
        pass_membership_id: The rider's Wayfare Pass membership reference number; leave "" if unknown.
    """
    match = _pick(trip_id=trip_id, customer_id=customer_id, driver_customer_id=driver_customer_id, driver_agreement_id=driver_agreement_id, pass_membership_id=pass_membership_id)
    rows = ctx.find("trips", **match)
    return _report(rows, match, "trips")


@tool(owner="agent", rw="read")
def find_trip_charges(ctx: ToolContext, trip_charge_id: str = "", trip_id: str = "", customer_id: str = "",
                      pass_membership_id: str = "", original_charge_id: str = "") -> str:
    """Look up the charges on a rider's trips: fares, reservation fees, wait time, tolls, airport
    surcharges, priority pickup, cancellation and no-show fees, tips, fee waivers, fare adjustments,
    refunds, failed payments and settlements of unpaid balances, each with its amount, date and
    reason codes.

    Every criterion is optional; supply whichever reference numbers are known.

    Args:
        trip_charge_id: The charge reference number; leave "" if unknown.
        trip_id: The trip reference number; leave "" if unknown.
        customer_id: The rider's customer reference number; leave "" if unknown.
        pass_membership_id: The Wayfare Pass membership whose benefit applied; leave "" if unknown.
        original_charge_id: The reference number of the charge an adjustment, refund or settlement relates to; leave "" if unknown.
    """
    match = _pick(trip_charge_id=trip_charge_id, trip_id=trip_id, customer_id=customer_id, pass_membership_id=pass_membership_id, original_charge_id=original_charge_id)
    rows = ctx.find("trip_charges", **match)
    return _report(rows, match, "trip charges")


@tool(owner="agent", rw="read")
def find_trip_fare_reviews(ctx: ToolContext, fare_review_id: str = "", customer_id: str = "", trip_id: str = "",
                           trip_charge_id: str = "") -> str:
    """Look up fare review requests sent to the fare review team: the trip and charge disputed, the
    reason, the amount sent for review, the outcome and when the request was registered.

    Every criterion is optional.

    Args:
        fare_review_id: The fare review reference number; leave "" if unknown.
        customer_id: The rider's customer reference number; leave "" if unknown.
        trip_id: The trip reference number; leave "" if unknown.
        trip_charge_id: The disputed charge reference number; leave "" if unknown.
    """
    match = _pick(fare_review_id=fare_review_id, customer_id=customer_id, trip_id=trip_id, trip_charge_id=trip_charge_id)
    rows = ctx.find("trip_fare_reviews", **match)
    return _report(rows, match, "fare reviews")


# ---------------------------------------------------------------- cleaning and damage
@tool(owner="agent", rw="read")
def find_damage_assessments(ctx: ToolContext, damage_assessment_id: str = "", customer_id: str = "", trip_id: str = "",
                            driver_customer_id: str = "", driver_agreement_id: str = "") -> str:
    """Look up cleaning and damage fee assessments: the fee level, status, trip, reporting driver,
    when it was reported, what was reported, photos and receipts submitted, the fee assessed, the
    charge, dispute and closing dates and the net fee billed to the rider.

    Search by the assessment, the rider charged, the trip, or the reporting driver. Every criterion
    is optional.

    Args:
        damage_assessment_id: The assessment reference number; leave "" if unknown.
        customer_id: The rider's customer reference number; leave "" if unknown.
        trip_id: The trip reference number; leave "" if unknown.
        driver_customer_id: The reporting driver's customer reference number; leave "" if unknown.
        driver_agreement_id: The reporting driver's agreement reference number; leave "" if unknown.
    """
    match = _pick(damage_assessment_id=damage_assessment_id, customer_id=customer_id, trip_id=trip_id, driver_customer_id=driver_customer_id, driver_agreement_id=driver_agreement_id)
    rows = ctx.find("damage_assessments", **match)
    return _report(rows, match, "fee assessments")


@tool(owner="agent", rw="read")
def find_damage_events(ctx: ToolContext, damage_event_id: str = "", damage_assessment_id: str = "",
                       customer_id: str = "", original_event_id: str = "") -> str:
    """Look up the ledger of a cleaning or damage fee assessment: evidence submissions, fee charges,
    refunds and partial refunds, with dates, amounts, fee levels and reason codes.

    Every criterion is optional.

    Args:
        damage_event_id: The ledger entry reference number; leave "" if unknown.
        damage_assessment_id: The assessment reference number; leave "" if unknown.
        customer_id: The rider's customer reference number; leave "" if unknown.
        original_event_id: The reference number of the fee charge a refund returns; leave "" if unknown.
    """
    match = _pick(damage_event_id=damage_event_id, damage_assessment_id=damage_assessment_id, customer_id=customer_id, original_event_id=original_event_id)
    rows = ctx.find("damage_events", **match)
    return _report(rows, match, "assessment ledger entries")


# ---------------------------------------------------------------- driver earnings
@tool(owner="agent", rw="read")
def find_earnings_accounts(ctx: ToolContext, earnings_account_id: str = "", customer_id: str = "",
                           driver_agreement_id: str = "") -> str:
    """Look up a driver's earnings account: the Wayfare Pro status for the current quarter, the
    account status, payout method, any payout hold and its reason, the quarter start, the available
    balance and the Pro points earned this quarter.

    Every criterion is optional.

    Args:
        earnings_account_id: The earnings account reference number; leave "" if unknown.
        customer_id: The driver's customer reference number; leave "" if unknown.
        driver_agreement_id: The driver services agreement reference number; leave "" if unknown.
    """
    match = _pick(earnings_account_id=earnings_account_id, customer_id=customer_id, driver_agreement_id=driver_agreement_id)
    rows = ctx.find("earnings_accounts", **match)
    return _report(rows, match, "earnings accounts")


@tool(owner="agent", rw="read")
def find_earnings_ledger(ctx: ToolContext, earnings_entry_id: str = "", earnings_account_id: str = "",
                         customer_id: str = "", trip_id: str = "", damage_assessment_id: str = "",
                         bonus_offer_id: str = "", rental_charge_id: str = "", original_entry_id: str = "") -> str:
    """Look up a driver's earnings statement entries: trip earnings, tips, cancellation and cleaning
    payouts, bonuses, adjustments, instant cashouts and their fees, weekly payouts, rental
    deductions, bonus clawbacks and Pro points, each with amount, points, date and reason codes.

    Search by any reference the entry carries. Every criterion is optional.

    Args:
        earnings_entry_id: The statement entry reference number; leave "" if unknown.
        earnings_account_id: The earnings account reference number; leave "" if unknown.
        customer_id: The driver's customer reference number; leave "" if unknown.
        trip_id: The trip reference number; leave "" if unknown.
        damage_assessment_id: The cleaning or damage assessment reference number; leave "" if unknown.
        bonus_offer_id: The incentive offer reference number; leave "" if unknown.
        rental_charge_id: The rental charge reference number; leave "" if unknown.
        original_entry_id: The reference number of the entry a fee or adjustment belongs to; leave "" if unknown.
    """
    match = _pick(earnings_entry_id=earnings_entry_id, earnings_account_id=earnings_account_id, customer_id=customer_id, trip_id=trip_id, damage_assessment_id=damage_assessment_id, bonus_offer_id=bonus_offer_id, rental_charge_id=rental_charge_id, original_entry_id=original_entry_id)
    rows = ctx.find("earnings_ledger", **match)
    return _report(rows, match, "earnings entries")


@tool(owner="agent", rw="read")
def find_bonus_offers(ctx: ToolContext, bonus_offer_id: str = "", earnings_account_id: str = "", customer_id: str = "",
                      source_offer_id: str = "", referred_customer_id: str = "") -> str:
    """Look up incentive offers made to a driver and the driver's opt-ins: quests, consecutive-trip
    bonuses, earnings guarantees and referral bonuses, with their market, window, trip target,
    reward, guaranteed amount and required online time.

    Every criterion is optional.

    Args:
        bonus_offer_id: The offer or opt-in reference number; leave "" if unknown.
        earnings_account_id: The earnings account reference number; leave "" if unknown.
        customer_id: The driver's customer reference number; leave "" if unknown.
        source_offer_id: The reference number of the offer an opt-in belongs to; leave "" if unknown.
        referred_customer_id: The customer reference number of a referred new driver; leave "" if unknown.
    """
    match = _pick(bonus_offer_id=bonus_offer_id, earnings_account_id=earnings_account_id, customer_id=customer_id, source_offer_id=source_offer_id, referred_customer_id=referred_customer_id)
    rows = ctx.find("bonus_offers", **match)
    return _report(rows, match, "incentive offers")


# ---------------------------------------------------------------- driver agreements
@tool(owner="agent", rw="read")
def find_driver_agreements(ctx: ToolContext, driver_agreement_id: str = "", customer_id: str = "") -> str:
    """Look up driver services agreements: the service level, status, market, signing, activation
    and closing dates, the registered vehicle, document expiry dates, the latest background check,
    any hold or deactivation with its reason and date, the current rating, rated trips in the
    rating window and lifetime trips.

    Every criterion is optional.

    Args:
        driver_agreement_id: The driver services agreement reference number; leave "" if unknown.
        customer_id: The driver's customer reference number; leave "" if unknown.
    """
    match = _pick(driver_agreement_id=driver_agreement_id, customer_id=customer_id)
    rows = ctx.find("driver_agreements", **match)
    return _report(rows, match, "driver agreements")


@tool(owner="agent", rw="read")
def find_driver_standing_events(ctx: ToolContext, driver_standing_event_id: str = "", driver_agreement_id: str = "",
                                customer_id: str = "", related_trip_id: str = "") -> str:
    """Look up a driver's standing record: documents submitted, document expiry notices, rating
    reviews, quality warnings, safety reports, quality course completions and background rechecks,
    each with its date and details.

    Every criterion is optional.

    Args:
        driver_standing_event_id: The standing record entry reference number; leave "" if unknown.
        driver_agreement_id: The driver services agreement reference number; leave "" if unknown.
        customer_id: The driver's customer reference number; leave "" if unknown.
        related_trip_id: The trip reference number a safety report concerns; leave "" if unknown.
    """
    match = _pick(driver_standing_event_id=driver_standing_event_id, driver_agreement_id=driver_agreement_id, customer_id=customer_id, related_trip_id=related_trip_id)
    rows = ctx.find("driver_standing_events", **match)
    return _report(rows, match, "standing record entries")


@tool(owner="agent", rw="read")
def find_driver_appeals(ctx: ToolContext, driver_appeal_id: str = "", customer_id: str = "",
                        driver_agreement_id: str = "") -> str:
    """Look up a driver's appeals and reactivation requests: what was appealed, the outcome, when it
    was submitted and when it was decided.

    Every criterion is optional.

    Args:
        driver_appeal_id: The appeal reference number; leave "" if unknown.
        customer_id: The driver's customer reference number; leave "" if unknown.
        driver_agreement_id: The driver services agreement reference number; leave "" if unknown.
    """
    match = _pick(driver_appeal_id=driver_appeal_id, customer_id=customer_id, driver_agreement_id=driver_agreement_id)
    rows = ctx.find("driver_appeals", **match)
    return _report(rows, match, "appeals")


# ---------------------------------------------------------------- vehicle rentals
@tool(owner="agent", rw="read")
def find_rental_agreements(ctx: ToolContext, rental_agreement_id: str = "", customer_id: str = "",
                           driver_agreement_id: str = "") -> str:
    """Look up Wayfare Rentals weekly vehicle rentals: the vehicle class, status, hub, plate,
    reservation, pickup, return-due, return and closing dates, odometer readings, the balance due
    and the deposit held.

    Every criterion is optional.

    Args:
        rental_agreement_id: The rental reference number; leave "" if unknown.
        customer_id: The driver's customer reference number; leave "" if unknown.
        driver_agreement_id: The driver services agreement reference number; leave "" if unknown.
    """
    match = _pick(rental_agreement_id=rental_agreement_id, customer_id=customer_id, driver_agreement_id=driver_agreement_id)
    rows = ctx.find("rental_agreements", **match)
    return _report(rows, match, "rentals")


@tool(owner="agent", rw="read")
def find_rental_charges(ctx: ToolContext, rental_charge_id: str = "", rental_agreement_id: str = "",
                        customer_id: str = "", original_charge_id: str = "") -> str:
    """Look up the ledger of a vehicle rental: weekly charges, mileage overage, damage, tolls, late
    return fees, payments from earnings or card, and security deposit holds, releases and
    applications.

    Every criterion is optional.

    Args:
        rental_charge_id: The rental ledger entry reference number; leave "" if unknown.
        rental_agreement_id: The rental reference number; leave "" if unknown.
        customer_id: The driver's customer reference number; leave "" if unknown.
        original_charge_id: The reference number of the charge a payment or offset settles; leave "" if unknown.
    """
    match = _pick(rental_charge_id=rental_charge_id, rental_agreement_id=rental_agreement_id, customer_id=customer_id, original_charge_id=original_charge_id)
    rows = ctx.find("rental_charges", **match)
    return _report(rows, match, "rental ledger entries")


# ---------------------------------------------------------------- bikes and scooters
@tool(owner="agent", rw="read")
def find_bike_plans(ctx: ToolContext, bike_plan_id: str = "", customer_id: str = "") -> str:
    """Look up Wayfare Bikes plans: the plan held, status, bike share system, purchase, expiry and
    cancellation dates, auto-renew setting and the net amount charged under the plan.

    Every criterion is optional.

    Args:
        bike_plan_id: The bike plan reference number; leave "" if unknown.
        customer_id: The rider's customer reference number; leave "" if unknown.
    """
    match = _pick(bike_plan_id=bike_plan_id, customer_id=customer_id)
    rows = ctx.find("bike_plans", **match)
    return _report(rows, match, "bike plans")


@tool(owner="agent", rw="read")
def find_bike_rides(ctx: ToolContext, bike_charge_id: str = "", bike_plan_id: str = "", customer_id: str = "",
                    original_charge_id: str = "") -> str:
    """Look up bike and scooter charges: plan fees, ride charges, overtime and parking fees, lost
    vehicle fees and refunds, with ride start time, vehicle type, ride length and amount.

    Every criterion is optional.

    Args:
        bike_charge_id: The charge reference number; leave "" if unknown.
        bike_plan_id: The bike plan reference number; leave "" if unknown.
        customer_id: The rider's customer reference number; leave "" if unknown.
        original_charge_id: The reference number of the charge a refund returns; leave "" if unknown.
    """
    match = _pick(bike_charge_id=bike_charge_id, bike_plan_id=bike_plan_id, customer_id=customer_id, original_charge_id=original_charge_id)
    rows = ctx.find("bike_rides", **match)
    return _report(rows, match, "bike and scooter charges")

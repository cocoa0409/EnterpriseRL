"""Hidden task tools for difficulty medical_transportation_benefits (category ride).
Output of erl-task-instantiate. Each tool is reached only through unlock_* -> call_* and performs one
atomic ledger write on a member's RideLink transportation benefit; none of them checks eligibility,
timing, duplicates or any other policy condition, and none computes an amount for the caller.
"""

from erlbench import ToolContext, tool


@tool(owner="agent", rw="write")
def approve_stay_lodging_meals_3bb3a021(ctx: ToolContext, ride_benefit_id: str, trip_number: str, leg: str,
                                        reimbursement_type: str, claim_trip_date: str, lodging_nights: int,
                                        meal_days: int, amount: float) -> str:
    """Book an approved lodging and meals reimbursement for one registered long-distance trip on a member's
    RideLink transportation benefit. One call adds one approved reimbursement claim to the benefit's
    reimbursement ledger with a newly issued member reimbursement claim number, the trip's reservation
    number, the leg, the trip date, the lodging nights and meal days approved and the approved amount,
    dated today; the approved amount is then owed to the member until it is paid. The member can see the
    new approved claim, its claim number and amount on their reimbursement history. Nothing else on the
    benefit changes.

    Args:
        ride_benefit_id: Id class — the reference number of the member's transportation benefit, as
            returned by the transportation benefit lookup for the verified member.
        trip_number: Verbatim class — the trip's reservation number (for example RL-5580213) exactly as it
            appears on the trip's registered legs in the member's ride history or as the member reads it
            from their confirmation, copied character for character with no change (verbatim).
        leg: Enum class — which part of the trip the claim covers: outbound when the claim covers only the
            leg from home to the appointment; return when it covers only the leg back home; round_trip when
            it covers the whole trip out and back, as a lodging and meals claim for a stay does;
            not_applicable when the claim is tied to no trip leg at all.
        reimbursement_type: Enum class — the kind of reimbursement being approved: lodging_meals for lodging
            nights and meals of a long-distance stay, the kind this booking records; mileage for miles the
            member drove, which this booking never records; late_pickup_alternative for an alternative ride
            after a late pickup, which this booking never records; not_applicable for a ledger line that is
            no reimbursement, which this booking never records.
        claim_trip_date: Fixed-format class — the trip date the claim is for, written YYYY-MM-DD (four-digit
            year, two-digit month, two-digit day), a calendar date with no time or time zone.
        lodging_nights: Fixed-format class — the lodging nights approved, a whole number written as an
            integer nights count (no decimals), zero or more.
        meal_days: Fixed-format class — the travel days approved for meals, a whole number written as an
            integer days count (no decimals), zero or more.
        amount: Fixed-format class — the approved reimbursement amount in USD, 2 decimal places, a positive
            number; it is stored rounded to 2 decimal places exactly as passed.

    Returns:
        A dictionary rendered as text with these fields: status is the literal "approved" when the claim was
        booked; reimbursement_claim_number is the new member reimbursement claim number in the form
        MR-YYMMDD-NNNN; ledger_entry is the reference of the new reimbursement ledger entry; trip_number,
        leg, reimbursement_type and claim_trip_date echo what was booked; lodging_nights and meal_days are
        the integers booked; amount is the approved USD amount with 2 decimal places; posted_date is today's
        date as YYYY-MM-DD. A returned status of "approved" is the success receipt.
    """
    rid = ctx.make_id("rlg_", ride_benefit_id, trip_number, leg, reimbursement_type, claim_trip_date,
                      lodging_nights, meal_days, amount)
    posted = ctx.now()[:10]
    claim_no = f"MR-{posted[2:4]}{posted[5:7]}{posted[8:10]}-{int(rid[-8:], 16) % 10000:04d}"
    owner_rows = ctx.find("ride_benefits", ride_benefit_id=ride_benefit_id)
    ctx.create("ride_ledger", rid, ride_ledger_id=rid, ride_benefit_id=ride_benefit_id,
               customer_id=owner_rows[0].get("customer_id", "") if owner_rows else "", event_type="ride_mileage_approved", benefit_year="",
               trips=0, trip_number=trip_number, leg=leg, reimbursement_claim_number=claim_no,
               reimbursement_type=reimbursement_type, claim_trip_date=claim_trip_date,
               lodging_nights=int(lodging_nights), meal_days=int(meal_days), amount=round(float(amount), 2),
               payment_method="not_applicable", denial_reason="not_applicable", posted_date=posted)
    return str({"status": "approved", "reimbursement_claim_number": claim_no, "ledger_entry": rid,
                "trip_number": trip_number, "leg": leg, "reimbursement_type": reimbursement_type,
                "claim_trip_date": claim_trip_date, "lodging_nights": int(lodging_nights),
                "meal_days": int(meal_days), "amount": round(float(amount), 2), "posted_date": posted})


@tool(owner="agent", rw="write")
def approve_trip_mileage_f67ba186(ctx: ToolContext, ride_benefit_id: str, trip_number: str, leg: str,
                                  reimbursement_type: str, claim_trip_date: str, approved_miles: float,
                                  amount: float) -> str:
    """Book an approved mileage reimbursement for one registered trip on a member's RideLink transportation
    benefit. One call adds one approved reimbursement claim to the benefit's reimbursement ledger with a
    newly issued member reimbursement claim number, the trip's reservation number, the leg, the trip date,
    the approved miles and the approved amount, dated today; the approved amount is then owed to the member
    until it is paid. The member can see the new approved claim, its claim number, miles and amount on
    their reimbursement history. Nothing else on the benefit changes.

    Args:
        ride_benefit_id: Id class — the reference number of the member's transportation benefit, as
            returned by the transportation benefit lookup for the verified member.
        trip_number: Verbatim class — the trip's reservation number (for example RL-5580213) exactly as it
            appears on the trip's registered legs in the member's ride history or as the member reads it
            from their confirmation, copied character for character with no change (verbatim).
        leg: Enum class — which part of the trip the claim covers: outbound when the claim covers only the
            leg from home to the appointment; return when it covers only the leg back home; round_trip when
            it covers the whole trip out and back; not_applicable when the claim is tied to no trip leg.
        reimbursement_type: Enum class — the kind of reimbursement being approved: mileage for miles the
            member's household drove, the kind this booking records; lodging_meals for lodging and meals of
            a stay, which this booking never records; late_pickup_alternative for an alternative ride after
            a late pickup, which this booking never records; not_applicable for a ledger line that is no
            reimbursement, which this booking never records.
        claim_trip_date: Fixed-format class — the trip date the claim is for, written YYYY-MM-DD (four-digit
            year, two-digit month, two-digit day), a calendar date with no time or time zone.
        approved_miles: Fixed-format class — the approved miles in miles, 1 decimal place (tenths of a mile),
            zero or more; stored rounded to 1 decimal place exactly as passed.
        amount: Fixed-format class — the approved reimbursement amount in USD, 2 decimal places, a positive
            number; it is stored rounded to 2 decimal places exactly as passed.

    Returns:
        A dictionary rendered as text with these fields: status is the literal "approved" when the claim was
        booked; reimbursement_claim_number is the new member reimbursement claim number in the form
        MR-YYMMDD-NNNN; ledger_entry is the reference of the new reimbursement ledger entry; trip_number,
        leg, reimbursement_type and claim_trip_date echo what was booked; approved_miles is the miles booked
        with 1 decimal place; amount is the approved USD amount with 2 decimal places; posted_date is today's
        date as YYYY-MM-DD. A returned status of "approved" is the success receipt.
    """
    rid = ctx.make_id("rlm_", ride_benefit_id, trip_number, leg, reimbursement_type, claim_trip_date,
                      approved_miles, amount)
    posted = ctx.now()[:10]
    claim_no = f"MR-{posted[2:4]}{posted[5:7]}{posted[8:10]}-{int(rid[-8:], 16) % 10000:04d}"
    owner_rows = ctx.find("ride_benefits", ride_benefit_id=ride_benefit_id)
    ctx.create("ride_ledger", rid, ride_ledger_id=rid, ride_benefit_id=ride_benefit_id,
               customer_id=owner_rows[0].get("customer_id", "") if owner_rows else "", event_type="ride_mileage_approved", benefit_year="",
               trips=0, trip_number=trip_number, leg=leg, reimbursement_claim_number=claim_no,
               reimbursement_type=reimbursement_type, claim_trip_date=claim_trip_date,
               approved_miles=round(float(approved_miles), 1), amount=round(float(amount), 2),
               payment_method="not_applicable", denial_reason="not_applicable", posted_date=posted)
    return str({"status": "approved", "reimbursement_claim_number": claim_no, "ledger_entry": rid,
                "trip_number": trip_number, "leg": leg, "reimbursement_type": reimbursement_type,
                "claim_trip_date": claim_trip_date, "approved_miles": round(float(approved_miles), 1),
                "amount": round(float(amount), 2), "posted_date": posted})


@tool(owner="user", rw="write")
def collect_trip_settlement_816cec94(ctx: ToolContext, ride_benefit_id: str, reimbursement_claim_number: str,
                                     payment_method: str, amount: float) -> str:
    """The member collects the settlement of one trip's approved reimbursement from their own RideLink
    account, choosing how it is paid. One call adds one payment to the benefit's reimbursement ledger under
    the given member reimbursement claim number, for the amount given, by the payment method the member
    picks, dated today; the money is then on its way to the member by that method. The member sees the
    payment, its amount and method on their reimbursement history. Nothing else on the benefit changes.

    Args:
        ride_benefit_id: Id class — the reference number of the member's transportation benefit, as
            returned by the transportation benefit lookup and read to the member by the agent.
        reimbursement_claim_number: Verbatim class — the member reimbursement claim number the settlement is
            recorded under, in the form MR-YYMMDD-NNNN, copied character for character as it appears on the
            member's reimbursement history or as the agent reads it out, with no change (verbatim).
        payment_method: Enum class — how the member wants to be paid: prepaid_card when the money is loaded
            onto the member's RideLink prepaid card; direct_deposit when it is sent to the member's bank
            account on file; check when a paper check is mailed to the mailing address on file;
            not_applicable when no payment is made, which never applies to a settlement.
        amount: Fixed-format class — the settlement amount paid in USD, 2 decimal places, a positive number;
            it is stored rounded to 2 decimal places exactly as passed.

    Returns:
        A dictionary rendered as text with these fields: status is the literal "paid" when the payment was
        recorded; payment_entry is the reference of the new payment entry; reimbursement_claim_number echoes
        the claim number paid under; payment_method echoes the method chosen; amount is the USD amount paid
        with 2 decimal places; posted_date is today's date as YYYY-MM-DD. A returned status of "paid" is the
        success receipt.
    """
    rid = ctx.make_id("rlp_", ride_benefit_id, reimbursement_claim_number, payment_method, amount)
    posted = ctx.now()[:10]
    owner_rows = ctx.find("ride_benefits", ride_benefit_id=ride_benefit_id)
    ctx.create("ride_ledger", rid, ride_ledger_id=rid, ride_benefit_id=ride_benefit_id,
               customer_id=owner_rows[0].get("customer_id", "") if owner_rows else "", event_type="ride_mileage_paid", benefit_year="",
               trips=0, trip_number="", leg="not_applicable", reimbursement_claim_number=reimbursement_claim_number,
               reimbursement_type="not_applicable", amount=round(float(amount), 2), payment_method=payment_method,
               denial_reason="not_applicable", posted_date=posted)
    return str({"status": "paid", "payment_entry": rid, "reimbursement_claim_number": reimbursement_claim_number,
                "payment_method": payment_method, "amount": round(float(amount), 2), "posted_date": posted})


@tool(owner="agent", rw="write")
def expire_year_trips_0d38b23b(ctx: ToolContext, ride_benefit_id: str, benefit_year: str, trips: int) -> str:
    """Post the year-end expiry of a benefit year's unused value-added trips on a member's RideLink
    transportation benefit. One call adds one expiry entry to the benefit's value-added trip ledger for the
    given benefit year and number of trips, dated today; those trips are then gone from the member's
    value-added trips for good. The member sees the expiry, its year and trip count in their value-added trip
    history. Nothing else on the benefit changes.

    Args:
        ride_benefit_id: Id class — the reference number of the member's transportation benefit, as
            returned by the transportation benefit lookup for the verified member.
        benefit_year: Fixed-format class — the benefit year whose trips expire, written YYYY as a four-digit
            calendar year with no month or day.
        trips: Fixed-format class — the number of trips that expire, written as integer trips, positive
            (a whole number of one-way trips, no decimals).

    Returns:
        A dictionary rendered as text with these fields: status is the literal "expired" when the entry was
        posted; ledger_entry is the reference of the new expiry entry; benefit_year echoes the year as YYYY;
        trips is the integer number of trips expired; posted_date is today's date as YYYY-MM-DD. A returned
        status of "expired" is the success receipt.
    """
    rid = ctx.make_id("rle_", ride_benefit_id, benefit_year, trips)
    posted = ctx.now()[:10]
    owner_rows = ctx.find("ride_benefits", ride_benefit_id=ride_benefit_id)
    ctx.create("ride_ledger", rid, ride_ledger_id=rid, ride_benefit_id=ride_benefit_id,
               customer_id=owner_rows[0].get("customer_id", "") if owner_rows else "",
               event_type="ride_allotment_expire", benefit_year=str(benefit_year), trips=int(trips), trip_number="",
               leg="not_applicable", reimbursement_claim_number="", reimbursement_type="not_applicable",
               payment_method="not_applicable", denial_reason="not_applicable", posted_date=posted)
    return str({"status": "expired", "ledger_entry": rid, "benefit_year": str(benefit_year), "trips": int(trips),
                "posted_date": posted})


@tool(owner="agent", rw="write")
def load_year_allotment_a6239ac8(ctx: ToolContext, ride_benefit_id: str, benefit_year: str, trips: int) -> str:
    """Load a benefit year's value-added trip allotment onto a member's RideLink transportation benefit. One
    call adds one allotment load entry to the benefit's value-added trip ledger for the given benefit year and
    number of trips, dated today; the member can then use those trips for value-added rides such as
    pharmacy, WIC, food bank or community health class trips. The member sees the load, its year and trip
    count in their value-added trip history. Nothing else on the benefit changes.

    Args:
        ride_benefit_id: Id class — the reference number of the member's transportation benefit, as
            returned by the transportation benefit lookup for the verified member.
        benefit_year: Fixed-format class — the benefit year the trips are loaded for, written YYYY as a
            four-digit calendar year with no month or day.
        trips: Fixed-format class — the number of trips loaded, written as integer trips, positive (a whole
            number of one-way trips, no decimals).

    Returns:
        A dictionary rendered as text with these fields: status is the literal "loaded" when the entry was
        posted; ledger_entry is the reference of the new allotment entry; benefit_year echoes the year as
        YYYY; trips is the integer number of trips loaded; posted_date is today's date as YYYY-MM-DD. A
        returned status of "loaded" is the success receipt.
    """
    rid = ctx.make_id("rla_", ride_benefit_id, benefit_year, trips)
    posted = ctx.now()[:10]
    owner_rows = ctx.find("ride_benefits", ride_benefit_id=ride_benefit_id)
    ctx.create("ride_ledger", rid, ride_ledger_id=rid, ride_benefit_id=ride_benefit_id,
               customer_id=owner_rows[0].get("customer_id", "") if owner_rows else "",
               event_type="ride_trip_allotment", benefit_year=str(benefit_year), trips=int(trips), trip_number="",
               leg="not_applicable", reimbursement_claim_number="", reimbursement_type="not_applicable",
               payment_method="not_applicable", denial_reason="not_applicable", posted_date=posted)
    return str({"status": "loaded", "ledger_entry": rid, "benefit_year": str(benefit_year), "trips": int(trips),
                "posted_date": posted})


@tool(owner="user", rw="write")
def file_alternative_ride_claim_fa98ae6a(ctx: ToolContext, ride_benefit_id: str, trip_number: str, leg: str,
                                         reimbursement_type: str, claim_trip_date: str, amount: float) -> str:
    """The member files their own alternative-ride reimbursement claim from their RideLink account for a
    ride they took after a late pickup, at the amount entered. One call adds one approved reimbursement claim
    to the benefit's reimbursement ledger with a newly issued member reimbursement claim number, the trip's
    reservation number, the leg, the trip date and the amount, dated today; the amount is then owed to the
    member until it is paid. The member sees the claim, its number and amount in their reimbursement
    history. Nothing else on the benefit changes.

    Args:
        ride_benefit_id: Id class — the reference number of the member's transportation benefit, as
            returned by the transportation benefit lookup and read to the member by the agent.
        trip_number: Verbatim class — the reservation number of the trip whose pickup was late (for example
            RL-5580213) exactly as the member reads it from their ride confirmation or as the agent reads it
            from the ride history, copied character for character with no change (verbatim).
        leg: Enum class — the leg whose pickup was late: outbound when the late pickup was on the way to the
            destination; return when it was on the way back home; round_trip when the claim covers both legs
            of the trip; not_applicable when the claim is tied to no leg.
        reimbursement_type: Enum class — the kind of reimbursement claimed: late_pickup_alternative for an
            alternative ride after a late pickup, the kind this filing records; mileage for miles the member
            drove, which this filing never records; lodging_meals for lodging and meals of a stay, which this
            filing never records; not_applicable for a ledger line that is no reimbursement, which this filing
            never records.
        claim_trip_date: Fixed-format class — the date of the late leg, written YYYY-MM-DD (four-digit year,
            two-digit month, two-digit day), a calendar date with no time or time zone.
        amount: Fixed-format class — the amount claimed in USD, 2 decimal places, a positive number; it is
            stored rounded to 2 decimal places exactly as entered.

    Returns:
        A dictionary rendered as text with these fields: status is the literal "filed" when the claim was
        recorded; reimbursement_claim_number is the new member reimbursement claim number in the form
        MR-YYMMDD-NNNN; ledger_entry is the reference of the new claim entry; trip_number, leg,
        reimbursement_type and claim_trip_date echo what was filed; amount is the USD amount with 2 decimal
        places; posted_date is today's date as YYYY-MM-DD. A returned status of "filed" is the success receipt.
    """
    rid = ctx.make_id("rlx_", ride_benefit_id, trip_number, leg, reimbursement_type, claim_trip_date, amount)
    posted = ctx.now()[:10]
    claim_no = f"MR-{posted[2:4]}{posted[5:7]}{posted[8:10]}-{int(rid[-8:], 16) % 10000:04d}"
    owner_rows = ctx.find("ride_benefits", ride_benefit_id=ride_benefit_id)
    ctx.create("ride_ledger", rid, ride_ledger_id=rid, ride_benefit_id=ride_benefit_id,
               customer_id=owner_rows[0].get("customer_id", "") if owner_rows else "",
               event_type="ride_mileage_approved", benefit_year="", trips=0, trip_number=trip_number, leg=leg,
               reimbursement_claim_number=claim_no, reimbursement_type=reimbursement_type,
               claim_trip_date=claim_trip_date, amount=round(float(amount), 2), payment_method="not_applicable",
               denial_reason="not_applicable", posted_date=posted)
    return str({"status": "filed", "reimbursement_claim_number": claim_no, "ledger_entry": rid,
                "trip_number": trip_number, "leg": leg, "reimbursement_type": reimbursement_type,
                "claim_trip_date": claim_trip_date, "amount": round(float(amount), 2), "posted_date": posted})

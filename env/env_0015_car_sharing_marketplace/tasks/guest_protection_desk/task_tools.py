"""Hidden task tools for the Keyturn guest protection desk.

Each function lands one atomic business write on a guest's protection election. None of
them aggregates history, judges eligibility or works out an amount: the desk reads the
records, applies the published protection rules and passes the finished figure in.
"""

from erlbench import ToolContext, tool


@tool(owner="user", rw="write")
def declare_additional_driver_a214c8dd(ctx: ToolContext, election_id: str, customer_id: str,
                                       booking_id: str, driver_fee_amount: float,
                                       days_covered: int) -> str:
    """Take an additional driver onto the protection covering a trip. The guest themselves puts
    the extra driver on their own cover, and the marketplace records it by raising the additional
    driver fee against the protection election: a new protection line is written on the election
    carrying the fee agreed, the days of the trip the extra driver is covered for, and today's
    date, and the money is added to the protection fee the guest owes on that election. With that
    line on the election the extra driver stands as an approved driver on that trip, covered on the
    same terms as the guest. The call has done its work when the receipt comes back naming the new
    protection line.

    Args:
        election_id: Id class — the reference number of the protection election covering the
            trip the extra driver is joining, read from the guest's protection election record.
        customer_id: Id class — the member reference number of the guest who holds the election
            and is charged for the extra driver, read from the member profile lookup.
        booking_id: Id class — the booking reference number of the trip the extra driver is
            joining, read from the protection election record or from the trip booking record.
        driver_fee_amount: Fixed-format class — the fee charged for this extra driver, in USD to
            2 decimal places, rounded half up to the cent and never rounded anywhere but at the
            end, always a positive amount.
        days_covered: Fixed-format class — the seat days the extra driver's fee was measured
            across, in whole days, as a positive integer with no fraction.

    Returns:
        A one-line confirmation string. It names the reference number of the protection line
        just written, the fee in USD to 2 decimal places, and the whole number of days that line
        covers. The line appearing in the confirmation is what shows the extra driver now stands
        approved and charged on that election; any other outcome is reported in the text instead.
    """
    rid = ctx.make_id("gpd_", election_id, customer_id, booking_id, driver_fee_amount, days_covered)
    ctx.create("guestplan_charges", rid, protection_charge_id=rid, election_id=election_id,
               customer_id=customer_id, booking_id=booking_id,
               event_type="guestplan_secondary_driver_charged", charge_basis="secondary_driver_fee",
               charge_date=ctx.now()[:10], charge_amount=round(float(driver_fee_amount), 2),
               days_covered=int(days_covered), coverage_segment="initial", adjustment_reason="none")
    return (f"Additional driver taken onto election {election_id}: protection line {rid} for "
            f"{round(float(driver_fee_amount), 2):.2f} USD covering {int(days_covered)} day(s).")


@tool(owner="agent", rw="write")
def post_young_driver_surcharge_f46febb9(ctx: ToolContext, election_id: str, customer_id: str,
                                         booking_id: str, source_charge_id: str,
                                         surcharge_amount: float) -> str:
    """Raise the young-driver protection surcharge on a guest's protection election. The desk
    posts the loading a guest under the marketplace's young-driver threshold carries on the cover
    for their trip: a separate protection line is written on the election, naming the protection
    fee line the loading is measured against, which keeps the loading separable from the fee
    itself, and the amount is added to the protection fee the guest owes on that election. The line is flat, so
    it carries no days of its own. The call has done its work when the receipt comes back naming
    the new surcharge line.

    Args:
        election_id: Id class — the reference number of the protection election the loading is
            raised on, read from the guest's protection election record.
        customer_id: Id class — the member reference number of the guest who owes the loading,
            read from the member profile lookup.
        booking_id: Id class — the booking reference number of the trip the protection covers,
            read from the protection election record or from the trip booking record.
        source_charge_id: Id class — the reference number of the protection fee line this
            loading is measured against, read from the protection lines already on the election.
        surcharge_amount: Fixed-format class — the loading charged, in USD to 2 decimal places,
            rounded half up to the cent and never rounded anywhere but at the end, always a
            positive amount.

    Returns:
        A one-line confirmation string. It names the reference number of the surcharge line just
        written, the amount in USD to 2 decimal places, and the protection fee line it was
        measured against. The line appearing in the confirmation is what shows the loading now
        stands on that election; any other outcome is reported in the text instead.
    """
    rid = ctx.make_id("gpy_", election_id, customer_id, booking_id, source_charge_id, surcharge_amount)
    ctx.create("guestplan_charges", rid, protection_charge_id=rid, election_id=election_id,
               customer_id=customer_id, booking_id=booking_id, source_charge_id=source_charge_id,
               event_type="guestplan_protection_fee_charged",
               charge_basis="young_driver_protection_surcharge", charge_date=ctx.now()[:10],
               charge_amount=round(float(surcharge_amount), 2), days_covered=0,
               coverage_segment="initial", adjustment_reason="none")
    return (f"Young-driver protection surcharge {rid} of {round(float(surcharge_amount), 2):.2f} USD "
            f"posted to election {election_id} against protection line {source_charge_id}.")


@tool(owner="agent", rw="write")
def price_level_change_f4995b0a(ctx: ToolContext, election_id: str, customer_id: str,
                                booking_id: str, change_request_id: str, source_charge_id: str,
                                difference_amount: float, days_covered: int) -> str:
    """Price an approved request to move a trip's protection to a different level. The desk
    settles what the move costs the guest: a protection line is written on the election for the
    difference, measured against the protection fee line standing for the level first held and
    covering the upgraded stretch of the trip, and the same figure is written back onto the
    change request as the difference quoted to the guest. The money is added to the protection
    fee the guest owes on that election. The call has done its work when the receipt comes back
    naming the new difference line.

    Args:
        election_id: Id class — the reference number of the protection election being moved,
            read from the guest's protection election record.
        customer_id: Id class — the member reference number of the guest charged the difference,
            read from the member profile lookup.
        booking_id: Id class — the booking reference number of the trip the protection covers,
            read from the protection election record or from the trip booking record.
        change_request_id: Id class — the reference number of the request to move level that is
            being priced, read from the guest's protection change request record.
        source_charge_id: Id class — the reference number of the protection fee line raised for
            the level first held, which the difference is measured against, read from the
            protection lines already on the election.
        difference_amount: Fixed-format class — the difference charged for the move, in USD to
            2 decimal places, rounded half up to the cent and never rounded anywhere but at the
            end, positive when the guest owes more.
        days_covered: Fixed-format class — how many days of the trip the difference is priced
            on, in whole days, as a positive integer with no fraction.

    Returns:
        A one-line confirmation string. It names the reference number of the difference line just
        written, the difference in USD to 2 decimal places, the whole number of days it was
        priced on, and the change request it settles. The line appearing in the confirmation is
        what shows the move now stands priced on that election; any other outcome is reported in
        the text instead.
    """
    rid = ctx.make_id("gpl_", election_id, customer_id, booking_id, change_request_id,
                      source_charge_id, difference_amount, days_covered)
    ctx.create("guestplan_charges", rid, protection_charge_id=rid, election_id=election_id,
               customer_id=customer_id, booking_id=booking_id, source_charge_id=source_charge_id,
               event_type="guestplan_level_change_charged", charge_basis="level_upgrade_difference",
               charge_date=ctx.now()[:10], charge_amount=round(float(difference_amount), 2),
               days_covered=int(days_covered), coverage_segment="upgraded",
               adjustment_reason="mid_trip_upgrade")
    ctx.update("guestplan_change_requests", change_request_id,
               quoted_difference_amount=round(float(difference_amount), 2))
    return (f"Level change {change_request_id} priced on election {election_id}: difference line "
            f"{rid} for {round(float(difference_amount), 2):.2f} USD over {int(days_covered)} day(s).")


@tool(owner="user", rw="write")
def confirm_protection_level_63b6fff8(ctx: ToolContext, election_id: str, booking_id: str,
                                      protection_level_name: str, covered_days_count: int) -> str:
    """Take a protection level for a trip. The guest themselves settles the cover that will run on
    their own trip: the quote on the election becomes a live choice, the level named is written onto
    the election as the level that will cover the trip, today's date is recorded as the day the
    level was taken, and the number of days of cover the election will carry is written onto it. The
    guest can afterwards see the election standing as chosen rather than as a quote, on the level
    named and for the days recorded. The call has done its work when the receipt comes back naming
    the election, the level taken and the days of cover recorded.

    Args:
        election_id: Id class — the reference number of the protection election being settled, read
            from the guest's protection election record.
        booking_id: Id class — the booking reference number of the trip the cover will run on, read
            from the protection election record or from the trip booking record.
        protection_level_name: Enum class — the protection level the guest takes, written as the
            official full level name, one of exactly these six.
            Keyturn Declined Protection — the guest carries their own motor policy and wants no
            marketplace cover on the trip.
            Keyturn Minimum Protection — the guest wants the least cover the marketplace writes,
            with the largest share of a loss left with them.
            Keyturn Standard Protection — the guest wants the everyday level of cover, with a
            moderate share of a loss left with them.
            Keyturn Advantage Protection — the guest wants broader cover with a small share of a
            loss left with them and a longer trip carried.
            Keyturn Premier Protection — the guest wants cover that leaves no share of a loss with
            them at all.
            Keyturn Business Traveler Protection — the guest is travelling for work and wants cover
            written for commercial use and the longest trips.
        covered_days_count: Fixed-format class — how many days of cover the election will carry, in
            whole days, as a positive integer with no fraction.

    Returns:
        A one-line confirmation string. It names the reference number of the election just settled,
        the official full level name taken, and the whole number of days of cover recorded on it.
        The election appearing in the confirmation as chosen on that level is what shows the cover
        now stands; any other outcome is reported in the text instead.
    """
    ctx.update("guestplan_elections", election_id, status="elected",
               protection_level_name=protection_level_name, booking_id=booking_id,
               elected_date=ctx.now()[:10], coverage_days=int(covered_days_count))
    return (f"Protection election {election_id} taken on {protection_level_name} "
            f"for {int(covered_days_count)} day(s) of cover.")


@tool(owner="agent", rw="write")
def post_protection_fee_513639f7(ctx: ToolContext, election_id: str, customer_id: str,
                                 booking_id: str, fee_amount: float, days_covered: int) -> str:
    """Charge the protection fee for a trip to the guest's protection election. The desk posts the
    fee the elected level produces for the trip: a new protection line is written on the election
    for the initial stretch of the trip, carrying the fee and the days of cover it was priced on and
    today's date, and the money is added to the protection fee the guest owes on that election. The
    guest can afterwards see the fee standing against their cover for the trip. The call has done
    its work when the receipt comes back naming the new protection line.

    Args:
        election_id: Id class — the reference number of the protection election the fee is charged
            to, read from the guest's protection election record.
        customer_id: Id class — the member reference number of the guest being charged, read from
            the member profile lookup.
        booking_id: Id class — the booking reference number of the trip the protection covers, read
            from the protection election record or from the trip booking record.
        fee_amount: Fixed-format class — the protection fee charged for the trip, in USD to 2
            decimal places, rounded half up to the cent and never rounded anywhere but at the
            end, always a positive amount.
        days_covered: Fixed-format class — how many days of cover the fee was priced on, in whole
            days, as a positive integer with no fraction.

    Returns:
        A one-line confirmation string. It names the reference number of the protection line just
        written, the fee in USD to 2 decimal places, and the whole number of days it was priced on.
        The line appearing in the confirmation is what shows the protection fee now stands on that
        election; any other outcome is reported in the text instead.
    """
    rid = ctx.make_id("gpf_", election_id, customer_id, booking_id, fee_amount, days_covered)
    ctx.create("guestplan_charges", rid, protection_charge_id=rid, election_id=election_id,
               customer_id=customer_id, booking_id=booking_id,
               event_type="guestplan_protection_fee_charged", charge_basis="daily_protection_fee",
               charge_date=ctx.now()[:10], charge_amount=round(float(fee_amount), 2),
               days_covered=int(days_covered), coverage_segment="initial", adjustment_reason="none")
    return (f"Protection fee line {rid} of {round(float(fee_amount), 2):.2f} USD posted to election "
            f"{election_id} over {int(days_covered)} day(s) of cover.")

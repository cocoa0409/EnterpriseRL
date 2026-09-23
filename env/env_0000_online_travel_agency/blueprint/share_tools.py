"""Shared tools for the Wanderlane Travel Group support desk (scenario: online_travel_agency).

Every tool defined here is a SHARE tool: always present in its owner's tool list and directly
callable in every task. Only three kinds of utility belong here, and each difficulty reuses them
unchanged: the complete record-lookup layer (one finder per table, with the traveller-profile
finder doubling as the identity entry point), the identity-verification write, and the
transfer-to-human handoff. Customer-originated business writes are authored per difficulty as
hidden task tools and never live here.
"""

from erlbench import ToolContext, tool


@tool(owner="agent", rw="read")
def find_customers(ctx: ToolContext, customer_id: str = "", full_name: str = "", email: str = "",
                   mobile_number: str = "", passport_last4: str = "",
                   billing_postal_code: str = "") -> str:
    """Find the traveller profile this call is about and read the reference number every other
    lookup needs. The profile can be reached by the traveller reference number itself, or by what a
    caller naturally says out loud — their name, their registered email, the mobile number the
    booking notifications go to, the last four characters of the passport held on file, or the
    postal code of the billing address. Each criterion is optional, and what comes back is the
    profile on file: contact details, date of birth, passport and billing details, the date the
    profile was opened, the country of residence, the preferred language and the contact
    preference. Where two or more profiles answer to what was given, nothing is returned and one
    further detail is asked for. Finding a traveller is not the same as verifying who is on the
    line: that is a separate step and must still be carried out before anything on the account is
    discussed or moved.

    Args:
        customer_id: Id class — the traveller reference number on the profile; leave "" if unknown.
        full_name: Verbatim class — the traveller's name as it appears on their identity document, copied down exactly as stated; leave "" if not given.
        email: Verbatim class — the registered contact email address; leave "" if not given.
        mobile_number: Fixed-format class — the registered mobile number, 10 digits with no spaces or punctuation; leave "" if not given.
        passport_last4: Fixed-format class — the last four characters of the passport number on file, exactly 4 digits; leave "" if not given.
        billing_postal_code: Fixed-format class — the postal code of the billing address, uppercase and without spaces; leave "" if not given.
    """
    match = {k: v for k, v in {"customer_id": customer_id, "full_name": full_name,
                               "email": email, "mobile_number": mobile_number,
                               "passport_last4": passport_last4,
                               "billing_postal_code": billing_postal_code}.items() if v}
    if not match:
        return "Error: provide at least one reference number or profile detail to find the traveller."
    rows = ctx.fuzzy_find("customers", **match)
    if not rows:
        return f"No traveller profile matches {match}."
    if len(rows) > 1:
        return (f"Error: {len(rows)} traveller profiles match {match}; ask the caller for one more "
                "detail on file to tell them apart.")
    return str(rows[0])


@tool(owner="agent", rw="read")
def find_air_bookings(ctx: ToolContext, air_booking_id: str = "", customer_id: str = "", corporate_program_id: str = "") -> str:
    """Look up the air bookings held in a traveller's name. Each record carries the fare brand sold, the routing and travel dates, the record locator, how many travellers are ticketed, where the booking stands in its life, what has been paid toward it and what travel credit it still carries.

    Every criterion below is optional: supply whichever reference numbers are already in
    hand and the matching records are returned, or a plain message when nothing matches.

    Args:
        air_booking_id: Id class — the internal reference of the air booking; leave "" if unknown.
        customer_id: Id class — the traveller reference number on the profile; leave "" if unknown.
        corporate_program_id: Id class — the corporate travel programme the record was booked under; leave "" if unknown.
    """
    match = {k: v for k, v in {"air_booking_id": air_booking_id, "customer_id": customer_id, "corporate_program_id": corporate_program_id}.items() if v}
    rows = ctx.find("air_bookings", **match)
    return str(rows) if rows else f"No air bookings records match {match}."


@tool(owner="agent", rw="read")
def find_air_booking_events(ctx: ToolContext, air_event_id: str = "", air_booking_id: str = "", customer_id: str = "", source_event_id: str = "") -> str:
    """Look up the individual lines posted to air bookings: fares, taxes and agency service fees, optional extras, change and name-correction fees, penalties, refunds to the card, travel-credit vouchers issued and redeemed, and the airline's own schedule notices. Every line states what it is for, what it came to, when it posted and which traveller and segment it belongs to.

    Every criterion below is optional: supply whichever reference numbers are already in
    hand and the matching records are returned, or a plain message when nothing matches.

    Args:
        air_event_id: Id class — the reference of a single line on an air booking; leave "" if unknown.
        air_booking_id: Id class — the internal reference of the air booking; leave "" if unknown.
        customer_id: Id class — the traveller reference number on the profile; leave "" if unknown.
        source_event_id: Id class — a reference number carried on the record; leave "" if unknown.
    """
    match = {k: v for k, v in {"air_event_id": air_event_id, "air_booking_id": air_booking_id, "customer_id": customer_id, "source_event_id": source_event_id}.items() if v}
    rows = ctx.find("air_booking_events", **match)
    return str(rows) if rows else f"No air booking events records match {match}."


@tool(owner="agent", rw="read")
def find_air_service_requests(ctx: ToolContext, air_request_id: str = "", customer_id: str = "", air_booking_id: str = "") -> str:
    """Look up the requests a traveller has put to the air back office — refund reviews, name corrections, disruption rebookings, special assistance and waiver reviews — together with where each one stands and when it was decided.

    Every criterion below is optional: supply whichever reference numbers are already in
    hand and the matching records are returned, or a plain message when nothing matches.

    Args:
        air_request_id: Id class — the reference of an air service request; leave "" if unknown.
        customer_id: Id class — the traveller reference number on the profile; leave "" if unknown.
        air_booking_id: Id class — the internal reference of the air booking; leave "" if unknown.
    """
    match = {k: v for k, v in {"air_request_id": air_request_id, "customer_id": customer_id, "air_booking_id": air_booking_id}.items() if v}
    rows = ctx.find("air_service_requests", **match)
    return str(rows) if rows else f"No air service requests records match {match}."


@tool(owner="agent", rw="read")
def find_stay_reservations(ctx: ToolContext, stay_reservation_id: str = "", customer_id: str = "", corporate_program_id: str = "") -> str:
    """Look up the hotel reservations held in a guest's name. Each record carries the rate plan booked, the property and city, arrival and departure dates, how many rooms and occupants, where the reservation stands in its life, the folio total and any property credit still unspent.

    Every criterion below is optional: supply whichever reference numbers are already in
    hand and the matching records are returned, or a plain message when nothing matches.

    Args:
        stay_reservation_id: Id class — the internal reference of the hotel reservation; leave "" if unknown.
        customer_id: Id class — the traveller reference number on the profile; leave "" if unknown.
        corporate_program_id: Id class — the corporate travel programme the record was booked under; leave "" if unknown.
    """
    match = {k: v for k, v in {"stay_reservation_id": stay_reservation_id, "customer_id": customer_id, "corporate_program_id": corporate_program_id}.items() if v}
    rows = ctx.find("stay_reservations", **match)
    return str(rows) if rows else f"No stay reservations records match {match}."


@tool(owner="agent", rw="read")
def find_stay_folio_entries(ctx: ToolContext, stay_folio_entry_id: str = "", stay_reservation_id: str = "", customer_id: str = "", source_entry_id: str = "") -> str:
    """Look up the lines posted to a hotel folio: room nights, deposits, occupancy and city taxes, facility and parking charges, optional extras taken during the stay, cancellation and no-show penalties, refunds, property credit granted and spent, and the property's own operational notices.

    Every criterion below is optional: supply whichever reference numbers are already in
    hand and the matching records are returned, or a plain message when nothing matches.

    Args:
        stay_folio_entry_id: Id class — the reference of a single line on a hotel folio; leave "" if unknown.
        stay_reservation_id: Id class — the internal reference of the hotel reservation; leave "" if unknown.
        customer_id: Id class — the traveller reference number on the profile; leave "" if unknown.
        source_entry_id: Id class — the reference of the earlier line this one was raised against; leave "" if unknown.
    """
    match = {k: v for k, v in {"stay_folio_entry_id": stay_folio_entry_id, "stay_reservation_id": stay_reservation_id, "customer_id": customer_id, "source_entry_id": source_entry_id}.items() if v}
    rows = ctx.find("stay_folio_entries", **match)
    return str(rows) if rows else f"No stay folio entries records match {match}."


@tool(owner="agent", rw="read")
def find_stay_change_requests(ctx: ToolContext, stay_request_id: str = "", customer_id: str = "", stay_reservation_id: str = "") -> str:
    """Look up the requests a guest has put to the property desk — date changes, name changes, rate reviews, refund reviews and overbooking relocations — together with where each one stands and when it was decided.

    Every criterion below is optional: supply whichever reference numbers are already in
    hand and the matching records are returned, or a plain message when nothing matches.

    Args:
        stay_request_id: Id class — the reference of a hotel change request; leave "" if unknown.
        customer_id: Id class — the traveller reference number on the profile; leave "" if unknown.
        stay_reservation_id: Id class — the internal reference of the hotel reservation; leave "" if unknown.
    """
    match = {k: v for k, v in {"stay_request_id": stay_request_id, "customer_id": customer_id, "stay_reservation_id": stay_reservation_id}.items() if v}
    rows = ctx.find("stay_change_requests", **match)
    return str(rows) if rows else f"No stay change requests records match {match}."


@tool(owner="agent", rw="read")
def find_care_policies(ctx: ToolContext, care_policy_id: str = "", customer_id: str = "", linked_air_booking_id: str = "", linked_bundle_package_id: str = "") -> str:
    """Look up the travel protection policies held in a traveller's name. Each record carries the plan bought, the certificate number, the travellers named, the declared trip cost and destination, the journey dates, where the policy stands in its life, the premium paid and the benefit already consumed.

    Every criterion below is optional: supply whichever reference numbers are already in
    hand and the matching records are returned, or a plain message when nothing matches.

    Args:
        care_policy_id: Id class — the internal reference of the travel protection policy; leave "" if unknown.
        customer_id: Id class — the traveller reference number on the profile; leave "" if unknown.
        linked_air_booking_id: Id class — the air booking the cover was bought alongside; leave "" if unknown.
        linked_bundle_package_id: Id class — the vacation package the cover was bought alongside; leave "" if unknown.
    """
    match = {k: v for k, v in {"care_policy_id": care_policy_id, "customer_id": customer_id, "linked_air_booking_id": linked_air_booking_id, "linked_bundle_package_id": linked_bundle_package_id}.items() if v}
    rows = ctx.find("care_policies", **match)
    return str(rows) if rows else f"No care policies records match {match}."


@tool(owner="agent", rw="read")
def find_care_premium_entries(ctx: ToolContext, care_premium_entry_id: str = "", care_policy_id: str = "", customer_id: str = "", source_entry_id: str = "") -> str:
    """Look up the premium lines charged against a travel protection policy: the base premium, the age and destination loadings, medical condition loadings, cancel-for-any-reason upgrades, the policy fee, re-rating adjustments and returned premium.

    Every criterion below is optional: supply whichever reference numbers are already in
    hand and the matching records are returned, or a plain message when nothing matches.

    Args:
        care_premium_entry_id: Id class — the reference of a single premium line; leave "" if unknown.
        care_policy_id: Id class — the internal reference of the travel protection policy; leave "" if unknown.
        customer_id: Id class — the traveller reference number on the profile; leave "" if unknown.
        source_entry_id: Id class — the reference of the earlier line this one was raised against; leave "" if unknown.
    """
    match = {k: v for k, v in {"care_premium_entry_id": care_premium_entry_id, "care_policy_id": care_policy_id, "customer_id": customer_id, "source_entry_id": source_entry_id}.items() if v}
    rows = ctx.find("care_premium_entries", **match)
    return str(rows) if rows else f"No care premium entries records match {match}."


@tool(owner="agent", rw="read")
def find_care_claims(ctx: ToolContext, care_claim_id: str = "", care_policy_id: str = "", customer_id: str = "", source_claim_id: str = "") -> str:
    """Look up the claims made under a travel protection policy: what was claimed and for which benefit, when the incident happened, what the insurer decided, what was paid, what deductible was withheld and what was later recovered from a liable third party.

    Every criterion below is optional: supply whichever reference numbers are already in
    hand and the matching records are returned, or a plain message when nothing matches.

    Args:
        care_claim_id: Id class — the reference of a claim record; leave "" if unknown.
        care_policy_id: Id class — the internal reference of the travel protection policy; leave "" if unknown.
        customer_id: Id class — the traveller reference number on the profile; leave "" if unknown.
        source_claim_id: Id class — the reference of the earlier claim record this row was raised against; leave "" if unknown.
    """
    match = {k: v for k, v in {"care_claim_id": care_claim_id, "care_policy_id": care_policy_id, "customer_id": customer_id, "source_claim_id": source_claim_id}.items() if v}
    rows = ctx.find("care_claims", **match)
    return str(rows) if rows else f"No care claims records match {match}."


@tool(owner="agent", rw="read")
def find_care_policy_requests(ctx: ToolContext, care_request_id: str = "", customer_id: str = "", care_policy_id: str = "") -> str:
    """Look up the requests a policyholder has put to the underwriting desk — cover upgrades, trip cost amendments, free-look cancellations, claim appeals and medical condition reviews — together with where each one stands and when it was decided.

    Every criterion below is optional: supply whichever reference numbers are already in
    hand and the matching records are returned, or a plain message when nothing matches.

    Args:
        care_request_id: Id class — the reference of a policy service request; leave "" if unknown.
        customer_id: Id class — the traveller reference number on the profile; leave "" if unknown.
        care_policy_id: Id class — the internal reference of the travel protection policy; leave "" if unknown.
    """
    match = {k: v for k, v in {"care_request_id": care_request_id, "customer_id": customer_id, "care_policy_id": care_policy_id}.items() if v}
    rows = ctx.find("care_policy_requests", **match)
    return str(rows) if rows else f"No care policy requests records match {match}."


@tool(owner="agent", rw="read")
def find_drive_rentals(ctx: ToolContext, drive_rental_id: str = "", customer_id: str = "", corporate_program_id: str = "") -> str:
    """Look up the car rentals held in a renter's name. Each record carries the rate class booked, the supplier and vehicle class, the collection and return branches and times, the driver's age and any additional drivers, where the rental stands in its life, the amount charged and the included mileage still unused.

    Every criterion below is optional: supply whichever reference numbers are already in
    hand and the matching records are returned, or a plain message when nothing matches.

    Args:
        drive_rental_id: Id class — the internal reference of the car rental; leave "" if unknown.
        customer_id: Id class — the traveller reference number on the profile; leave "" if unknown.
        corporate_program_id: Id class — the corporate travel programme the record was booked under; leave "" if unknown.
    """
    match = {k: v for k, v in {"drive_rental_id": drive_rental_id, "customer_id": customer_id, "corporate_program_id": corporate_program_id}.items() if v}
    rows = ctx.find("drive_rentals", **match)
    return str(rows) if rows else f"No drive rentals records match {match}."


@tool(owner="agent", rw="read")
def find_drive_rental_entries(ctx: ToolContext, drive_entry_id: str = "", drive_rental_id: str = "", customer_id: str = "", source_entry_id: str = "") -> str:
    """Look up the lines posted to a car rental: rental days and extra hours, prepayments, protection products and optional equipment, driver and statutory fees, fuel settlements, damage, cleaning, tolls and fines recharged after return, cancellation and no-show charges, refunds, and the mileage granted and consumed.

    Every criterion below is optional: supply whichever reference numbers are already in
    hand and the matching records are returned, or a plain message when nothing matches.

    Args:
        drive_entry_id: Id class — the reference of a single line on a rental; leave "" if unknown.
        drive_rental_id: Id class — the internal reference of the car rental; leave "" if unknown.
        customer_id: Id class — the traveller reference number on the profile; leave "" if unknown.
        source_entry_id: Id class — the reference of the earlier line this one was raised against; leave "" if unknown.
    """
    match = {k: v for k, v in {"drive_entry_id": drive_entry_id, "drive_rental_id": drive_rental_id, "customer_id": customer_id, "source_entry_id": source_entry_id}.items() if v}
    rows = ctx.find("drive_rental_entries", **match)
    return str(rows) if rows else f"No drive rental entries records match {match}."


@tool(owner="agent", rw="read")
def find_drive_damage_reviews(ctx: ToolContext, drive_review_id: str = "", customer_id: str = "", drive_rental_id: str = "") -> str:
    """Look up the reviews a renter has asked the rental desk to decide — damage assessments, fuel and toll disputes, late-return waivers and rate reviews — together with the amount in dispute, where each one stands and when it was decided.

    Every criterion below is optional: supply whichever reference numbers are already in
    hand and the matching records are returned, or a plain message when nothing matches.

    Args:
        drive_review_id: Id class — the reference of a rental damage review; leave "" if unknown.
        customer_id: Id class — the traveller reference number on the profile; leave "" if unknown.
        drive_rental_id: Id class — the internal reference of the car rental; leave "" if unknown.
    """
    match = {k: v for k, v in {"drive_review_id": drive_review_id, "customer_id": customer_id, "drive_rental_id": drive_rental_id}.items() if v}
    rows = ctx.find("drive_damage_reviews", **match)
    return str(rows) if rows else f"No drive damage reviews records match {match}."


@tool(owner="agent", rw="read")
def find_bundle_packages(ctx: ToolContext, bundle_package_id: str = "", customer_id: str = "", linked_care_policy_id: str = "") -> str:
    """Look up the vacation packages held in a traveller's name. Each record carries the package product booked, the resort, ship or tour, the departure and return dates, the travelling party and the rooms or cabins held, where the package stands in its life, the quoted price, what has been paid and what future travel credit it carries.

    Every criterion below is optional: supply whichever reference numbers are already in
    hand and the matching records are returned, or a plain message when nothing matches.

    Args:
        bundle_package_id: Id class — the internal reference of the vacation package; leave "" if unknown.
        customer_id: Id class — the traveller reference number on the profile; leave "" if unknown.
        linked_care_policy_id: Id class — the travel protection policy bought with the package; leave "" if unknown.
    """
    match = {k: v for k, v in {"bundle_package_id": bundle_package_id, "customer_id": customer_id, "linked_care_policy_id": linked_care_policy_id}.items() if v}
    rows = ctx.find("bundle_packages", **match)
    return str(rows) if rows else f"No bundle packages records match {match}."


@tool(owner="agent", rw="read")
def find_bundle_ledger_entries(ctx: ToolContext, bundle_entry_id: str = "", bundle_package_id: str = "", customer_id: str = "", source_entry_id: str = "") -> str:
    """Look up the lines posted to a vacation package: the deposit and each instalment of the balance, the priced components, supplements, discounts and upgrades, amendment and cancellation charges, refunds, future travel credit issued and redeemed, and the operator's own notices about the itinerary or a surcharge.

    Every criterion below is optional: supply whichever reference numbers are already in
    hand and the matching records are returned, or a plain message when nothing matches.

    Args:
        bundle_entry_id: Id class — the reference of a single line on a package; leave "" if unknown.
        bundle_package_id: Id class — the internal reference of the vacation package; leave "" if unknown.
        customer_id: Id class — the traveller reference number on the profile; leave "" if unknown.
        source_entry_id: Id class — the reference of the earlier line this one was raised against; leave "" if unknown.
    """
    match = {k: v for k, v in {"bundle_entry_id": bundle_entry_id, "bundle_package_id": bundle_package_id, "customer_id": customer_id, "source_entry_id": source_entry_id}.items() if v}
    rows = ctx.find("bundle_ledger_entries", **match)
    return str(rows) if rows else f"No bundle ledger entries records match {match}."


@tool(owner="agent", rw="read")
def find_bundle_change_requests(ctx: ToolContext, bundle_request_id: str = "", customer_id: str = "", bundle_package_id: str = "") -> str:
    """Look up the requests a party has put to the operations desk — name changes, date changes, component substitutions, refund reviews and surcharge disputes — together with where each one stands and when it was decided.

    Every criterion below is optional: supply whichever reference numbers are already in
    hand and the matching records are returned, or a plain message when nothing matches.

    Args:
        bundle_request_id: Id class — the reference of a package change request; leave "" if unknown.
        customer_id: Id class — the traveller reference number on the profile; leave "" if unknown.
        bundle_package_id: Id class — the internal reference of the vacation package; leave "" if unknown.
    """
    match = {k: v for k, v in {"bundle_request_id": bundle_request_id, "customer_id": customer_id, "bundle_package_id": bundle_package_id}.items() if v}
    rows = ctx.find("bundle_change_requests", **match)
    return str(rows) if rows else f"No bundle change requests records match {match}."


@tool(owner="agent", rw="read")
def find_club_memberships(ctx: ToolContext, club_membership_id: str = "", customer_id: str = "", household_pool_id: str = "") -> str:
    """Look up a traveller's club membership. The record carries the tier currently held, the membership number, when the tier took effect and when it will next be reviewed, where the membership stands in its life, the spendable points balance and the tier-qualifying count in the current period.

    Every criterion below is optional: supply whichever reference numbers are already in
    hand and the matching records are returned, or a plain message when nothing matches.

    Args:
        club_membership_id: Id class — the internal reference of the club membership; leave "" if unknown.
        customer_id: Id class — the traveller reference number on the profile; leave "" if unknown.
        household_pool_id: Id class — the household points pool the membership contributes to; leave "" if unknown.
    """
    match = {k: v for k, v in {"club_membership_id": club_membership_id, "customer_id": customer_id, "household_pool_id": household_pool_id}.items() if v}
    rows = ctx.find("club_memberships", **match)
    return str(rows) if rows else f"No club memberships records match {match}."


@tool(owner="agent", rw="read")
def find_club_points_entries(ctx: ToolContext, club_points_entry_id: str = "", club_membership_id: str = "", customer_id: str = "", source_entry_id: str = "") -> str:
    """Look up the rows on a club membership's ledger: points accrued from booked activity, bonuses and promotions, redemptions against awards and bookings, expiry sweeps, the tier-qualifying count and its end-of-period clear-down, and the uses of the named benefits the tier grants.

    Every criterion below is optional: supply whichever reference numbers are already in
    hand and the matching records are returned, or a plain message when nothing matches.

    Args:
        club_points_entry_id: Id class — the reference of a single club ledger row; leave "" if unknown.
        club_membership_id: Id class — the internal reference of the club membership; leave "" if unknown.
        customer_id: Id class — the traveller reference number on the profile; leave "" if unknown.
        source_entry_id: Id class — the reference of the earlier line this one was raised against; leave "" if unknown.
    """
    match = {k: v for k, v in {"club_points_entry_id": club_points_entry_id, "club_membership_id": club_membership_id, "customer_id": customer_id, "source_entry_id": source_entry_id}.items() if v}
    rows = ctx.find("club_points_entries", **match)
    return str(rows) if rows else f"No club points entries records match {match}."


@tool(owner="agent", rw="read")
def find_club_tier_reviews(ctx: ToolContext, club_review_id: str = "", customer_id: str = "", club_membership_id: str = "") -> str:
    """Look up the reviews a member has asked the programme office to decide — annual reviews, status matches, status challenges, retention appeals and points reinstatements — together with the tier claimed, where each one stands and when it was decided.

    Every criterion below is optional: supply whichever reference numbers are already in
    hand and the matching records are returned, or a plain message when nothing matches.

    Args:
        club_review_id: Id class — the reference of a club tier review; leave "" if unknown.
        customer_id: Id class — the traveller reference number on the profile; leave "" if unknown.
        club_membership_id: Id class — the internal reference of the club membership; leave "" if unknown.
    """
    match = {k: v for k, v in {"club_review_id": club_review_id, "customer_id": customer_id, "club_membership_id": club_membership_id}.items() if v}
    rows = ctx.find("club_tier_reviews", **match)
    return str(rows) if rows else f"No club tier reviews records match {match}."


@tool(owner="agent", rw="read")
def find_biz_programs(ctx: ToolContext, biz_program_id: str = "", customer_id: str = "") -> str:
    """Look up a company's corporate travel programme. The record carries the programme tier held, the corporate account number, the registered company name and country, the contract term and renewal notice date, where the programme stands in its life, the seats contracted, the amount billed and the seats still unassigned.

    Every criterion below is optional: supply whichever reference numbers are already in
    hand and the matching records are returned, or a plain message when nothing matches.

    Args:
        biz_program_id: Id class — the internal reference of the corporate travel programme; leave "" if unknown.
        customer_id: Id class — the traveller reference number on the profile; leave "" if unknown.
    """
    match = {k: v for k, v in {"biz_program_id": biz_program_id, "customer_id": customer_id}.items() if v}
    rows = ctx.find("biz_programs", **match)
    return str(rows) if rows else f"No biz programs records match {match}."


@tool(owner="agent", rw="read")
def find_biz_billing_entries(ctx: ToolContext, biz_entry_id: str = "", biz_program_id: str = "", customer_id: str = "", source_entry_id: str = "", traveller_customer_id: str = "") -> str:
    """Look up the lines billed to a corporate travel programme: the platform subscription and seat licences, the onboarding charge, transaction fees by booking channel and product, transactions charged beyond the included allowance, credit notes, rebates and service credits, the seats granted and assigned, and the agency's contractual notices.

    Every criterion below is optional: supply whichever reference numbers are already in
    hand and the matching records are returned, or a plain message when nothing matches.

    Args:
        biz_entry_id: Id class — the reference of a single line on a programme invoice; leave "" if unknown.
        biz_program_id: Id class — the internal reference of the corporate travel programme; leave "" if unknown.
        customer_id: Id class — the traveller reference number on the profile; leave "" if unknown.
        source_entry_id: Id class — the reference of the earlier line this one was raised against; leave "" if unknown.
        traveller_customer_id: Id class — the traveller whose seat or booking the line concerns; leave "" if unknown.
    """
    match = {k: v for k, v in {"biz_entry_id": biz_entry_id, "biz_program_id": biz_program_id, "customer_id": customer_id, "source_entry_id": source_entry_id, "traveller_customer_id": traveller_customer_id}.items() if v}
    rows = ctx.find("biz_billing_entries", **match)
    return str(rows) if rows else f"No biz billing entries records match {match}."


@tool(owner="agent", rw="read")
def find_biz_seat_requests(ctx: ToolContext, biz_request_id: str = "", customer_id: str = "", biz_program_id: str = "") -> str:
    """Look up the requests a programme administrator has put to the corporate desk — seat additions, removals and reassignments, tier changes and invoice disputes — together with the seat count asked for, where each one stands and when it was decided.

    Every criterion below is optional: supply whichever reference numbers are already in
    hand and the matching records are returned, or a plain message when nothing matches.

    Args:
        biz_request_id: Id class — the reference of a programme seat request; leave "" if unknown.
        customer_id: Id class — the traveller reference number on the profile; leave "" if unknown.
        biz_program_id: Id class — the internal reference of the corporate travel programme; leave "" if unknown.
    """
    match = {k: v for k, v in {"biz_request_id": biz_request_id, "customer_id": customer_id, "biz_program_id": biz_program_id}.items() if v}
    rows = ctx.find("biz_seat_requests", **match)
    return str(rows) if rows else f"No biz seat requests records match {match}."


@tool(owner="agent", rw="read")
def find_verification_log(ctx: ToolContext, verification_id: str = "", customer_id: str = "") -> str:
    """Look up the identity checks already recorded against a traveller's profile, so it is plain whether this caller has already been satisfactorily identified and when that was last done.

    Every criterion below is optional: supply whichever reference numbers are already in
    hand and the matching records are returned, or a plain message when nothing matches.

    Args:
        verification_id: Id class — the reference of an identity check already recorded; leave "" if unknown.
        customer_id: Id class — the traveller reference number on the profile; leave "" if unknown.
    """
    match = {k: v for k, v in {"verification_id": verification_id, "customer_id": customer_id}.items() if v}
    rows = ctx.find("verification_log", **match)
    return str(rows) if rows else f"No verification log records match {match}."


@tool(owner="agent", rw="read")
def find_handoff_log(ctx: ToolContext, handoff_id: str = "", customer_id: str = "") -> str:
    """Look up the occasions on which a traveller has already been handed over to a human representative, together with the reason recorded for each handover and when it took place.

    Every criterion below is optional: supply whichever reference numbers are already in
    hand and the matching records are returned, or a plain message when nothing matches.

    Args:
        handoff_id: Id class — the reference of a handover already recorded; leave "" if unknown.
        customer_id: Id class — the traveller reference number on the profile; leave "" if unknown.
    """
    match = {k: v for k, v in {"handoff_id": handoff_id, "customer_id": customer_id}.items() if v}
    rows = ctx.find("handoff_log", **match)
    return str(rows) if rows else f"No handoff log records match {match}."


@tool(owner="agent", rw="write")
def verify_traveller_identity(ctx: ToolContext, customer_id: str, mobile_number: str = "",
                              email: str = "", date_of_birth: str = "", passport_last4: str = "",
                              billing_postal_code: str = "",
                              profile_opened_date: str = "") -> str:
    """Establish that the caller really is the traveller whose profile has been found, and record
    the outcome. Nothing on an account may be discussed in detail, and no money, booking or
    membership may be moved, until this has passed. The comparison is made here rather than judged
    at the desk: each piece of information the caller offers is checked against the profile on
    file, and the check passes only when at least two of them agree. Callers seldom remember
    everything, so pass only the details actually given, exactly as they were said, and leave the
    rest empty. The traveller reference number is used solely to fetch the profile and never counts
    toward the two. Where a first attempt falls short and a later attempt succeeds with more
    information, the passing outcome is the one that stands.

    Args:
        customer_id: Id class — the traveller reference number read from the traveller profile. Required and never blank; it only fetches the profile and is not counted as one of the matching details.
        mobile_number: Fixed-format class — the registered mobile number, 10 digits with no spaces or punctuation; leave "" if not stated.
        email: Verbatim class — the registered contact email address, copied down exactly as stated; leave "" if not stated.
        date_of_birth: Fixed-format class — the traveller's date of birth as YYYY-MM-DD; leave "" if not stated.
        passport_last4: Fixed-format class — the last four characters of the passport number on file, exactly 4 digits; leave "" if not stated.
        billing_postal_code: Fixed-format class — the postal code of the billing address, uppercase and without spaces; leave "" if not stated.
        profile_opened_date: Fixed-format class — the date the traveller profile was first opened, as YYYY-MM-DD; leave "" if not stated.
    """
    if not customer_id:
        return "Error: customer_id is required; find the traveller profile first and pass its reference."
    rows = ctx.find("customers", customer_id=customer_id)
    if not rows:
        return f"Error: no traveller profile {customer_id}; cannot verify."
    rec = rows[0]
    # The tool owns the comparison. The locator customer_id is deliberately absent from `supplied`:
    # fetching a profile is not proof of identity.
    supplied = {"mobile_number": mobile_number, "email": email, "date_of_birth": date_of_birth,
                "passport_last4": passport_last4, "billing_postal_code": billing_postal_code,
                "profile_opened_date": profile_opened_date}
    matched = sum(1 for field, value in supplied.items()
                  if value and str(rec.get(field)) == str(value))
    verified = matched >= 2
    rid = ctx.make_id("ver_", customer_id)
    # Only the reproducible `verified` outcome is stored; the match count depends on which valid
    # subset of details this particular caller happened to offer.
    prior = ctx.find("verification_log", verification_id=rid)
    verified = verified or bool(prior and prior[0].get("verified"))
    if prior:
        ctx.update("verification_log", rid, verified=verified, verified_at=ctx.now())
    else:
        ctx.create("verification_log", rid, verification_id=rid, customer_id=customer_id,
                   verified=verified, verified_at=ctx.now())
    return (f"Identity verified for {customer_id} ({matched} detail(s) matched)." if verified
            else f"Identity NOT verified for {customer_id} (only {matched} of the required 2 "
                 "details matched). Ask the caller for another detail held on file and call this "
                 "tool again.")


@tool(owner="agent", rw="write")
def transfer_to_human_agent(ctx: ToolContext, customer_id: str, reason: str) -> str:
    """Pass the traveller to a human representative to carry on, and record the handover against
    their profile with the reason for it. There are two occasions for this and no others. The first
    is where nothing in the published terms can resolve what the traveller is asking for, so that
    continuing at the desk would mean inventing an answer. The second is where the traveller has
    asked outright to speak to a person on two separate occasions in this conversation; a single
    passing remark is not such a request, and the desk should first try to help.

    Args:
        customer_id: Id class — the traveller reference number read from the traveller profile, which must already exist.
        reason: Enum class — why the handover is being made; exactly one of POLICY_NOT_COVERED or CUSTOMER_REQUESTED, never anything else and never free text.
            POLICY_NOT_COVERED — no published term can decide the request;
            CUSTOMER_REQUESTED — the traveller has explicitly asked for a human representative at least 2 times.
    """
    allowed = {"POLICY_NOT_COVERED", "CUSTOMER_REQUESTED"}
    if reason not in allowed:
        return f"Error: unknown handoff reason '{reason}'. Valid: {', '.join(sorted(allowed))}."
    if not ctx.find("customers", customer_id=customer_id):
        return f"Error: no traveller profile {customer_id}; cannot record the handover."
    rid = ctx.make_id("hof_", customer_id, reason)
    ctx.create("handoff_log", rid, handoff_id=rid, customer_id=customer_id,
               reason=reason, created_at=ctx.now())
    return f"Handover to a human representative recorded for {customer_id} ({reason})."

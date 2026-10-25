"""Hidden task tools for the warranty_claims_and_transfers difficulty of env_0060_window_replacement_company
(Ridgeline Window & Door). Each tool performs one atomic write on warranty records with the value the
caller has already worked out; none of them judges eligibility or computes a charge.
"""

from erlbench import ToolContext, tool


@tool(owner="agent", rw="write")
def bill_missed_visit_fee_18fefa1f(ctx: ToolContext, warranty_registration_id: str, warranty_claim_id: str,
                                   visit_date: str, amount: float) -> str:
    """Bill the no-show fee for one missed technician visit on a warranty claim. One call adds one no-show
    fee entry to the warranty charges of the registration, dated with the date of the missed visit, tied
    to the claim the visit was booked for and carrying the claim's component; the amount owed by the
    registered owner rises by exactly that fee. Nothing else on the registration or the claim changes.
    The owner can see the new fee on the warranty charges of the registration.

    Args:
        warranty_registration_id: Id class — the identifier of the
            registration whose owner missed the visit, as returned by the warranty registration lookup.
        warranty_claim_id: Id class — the identifier of the warranty claim the missed visit was booked for,
            as returned by the warranty claim lookup or shown on the visit in the warranty activity lookup.
        visit_date: Fixed-format class — the date of the missed technician visit exactly as shown on that
            visit in the warranty activity lookup, written YYYY-MM-DD; it becomes the date of the fee.
        amount: Fixed-format class — the no-show fee owed for that visit, in USD, a positive amount
            rounded half up to 2 decimal places.

    Returns:
        A dictionary receipt: warranty_activity_id (text, the reference of the new no-show fee entry),
        warranty_registration_id (text, the registration billed), warranty_claim_id (text, the claim the
        fee belongs to), charge_kind (text, always no_show_fee), activity_date (text, YYYY-MM-DD, the date
        the fee carries) and amount (number, USD to 2 decimal places, the fee booked). A receipt carrying a
        warranty_activity_id means the fee is now on the registration's warranty charges.
    """
    regs = ctx.find("warranty_registrations", warranty_registration_id=warranty_registration_id)
    claims = ctx.find("warranty_claims", warranty_claim_id=warranty_claim_id)
    customer_id = regs[0].get("customer_id") if regs else ""
    component = claims[0].get("component") if claims else "not_applicable"
    fee = round(float(amount), 2)
    rid = ctx.make_id("wac_", warranty_registration_id, warranty_claim_id, visit_date, fee)
    ctx.create("warranty_activities", rid, warranty_activity_id=rid,
               warranty_registration_id=warranty_registration_id, customer_id=customer_id,
               event_type="warranty_charge_assessed", activity_date=visit_date,
               warranty_claim_id=warranty_claim_id, component=component,
               claim_decision="not_applicable", visit_outcome="not_applicable", units=0,
               labor_hours=0.0, amount=fee, charge_kind="no_show_fee", source_warranty_activity_id="")
    return str({"warranty_activity_id": rid, "warranty_registration_id": warranty_registration_id,
                "warranty_claim_id": warranty_claim_id, "charge_kind": "no_show_fee",
                "activity_date": visit_date, "amount": fee})


@tool(owner="agent", rw="write")
def bill_visit_trip_5cd049ac(ctx: ToolContext, warranty_registration_id: str, warranty_claim_id: str,
                             visit_date: str, amount: float) -> str:
    """Bill the trip charge for one completed technician visit on a warranty claim. One call adds one trip
    charge entry to the warranty charges of the registration, dated with the date of the visit, tied to
    the claim the visit served and carrying the claim's component; the amount owed by the registered owner
    rises by exactly that charge. Nothing else on the registration or the claim changes. The owner can see
    the new trip charge on the warranty charges of the registration.

    Args:
        warranty_registration_id: Id class — the identifier of the
            registration the visit was made under, as returned by the warranty registration lookup.
        warranty_claim_id: Id class — the identifier of the warranty claim the visit served, as returned by
            the warranty claim lookup or shown on the visit in the warranty activity lookup.
        visit_date: Fixed-format class — the date of the technician visit exactly as shown on that visit in
            the warranty activity lookup, written YYYY-MM-DD; it becomes the date of the trip charge.
        amount: Fixed-format class — the trip charge owed for that visit, in USD, a positive amount rounded
            half up to 2 decimal places.

    Returns:
        A dictionary receipt: warranty_activity_id (text, the reference of the new trip charge entry),
        warranty_registration_id (text, the registration billed), warranty_claim_id (text, the claim the
        charge belongs to), charge_kind (text, always trip_charge), activity_date (text, YYYY-MM-DD, the
        date the charge carries) and amount (number, USD to 2 decimal places, the charge booked). A receipt
        carrying a warranty_activity_id means the trip charge is now on the registration's warranty charges.
    """
    regs = ctx.find("warranty_registrations", warranty_registration_id=warranty_registration_id)
    claims = ctx.find("warranty_claims", warranty_claim_id=warranty_claim_id)
    customer_id = regs[0].get("customer_id") if regs else ""
    component = claims[0].get("component") if claims else "not_applicable"
    charge = round(float(amount), 2)
    rid = ctx.make_id("wac_", warranty_registration_id, warranty_claim_id, visit_date, charge, "trip")
    ctx.create("warranty_activities", rid, warranty_activity_id=rid,
               warranty_registration_id=warranty_registration_id, customer_id=customer_id,
               event_type="warranty_charge_assessed", activity_date=visit_date,
               warranty_claim_id=warranty_claim_id, component=component,
               claim_decision="not_applicable", visit_outcome="not_applicable", units=0,
               labor_hours=0.0, amount=charge, charge_kind="trip_charge", source_warranty_activity_id="")
    return str({"warranty_activity_id": rid, "warranty_registration_id": warranty_registration_id,
                "warranty_claim_id": warranty_claim_id, "charge_kind": "trip_charge",
                "activity_date": visit_date, "amount": charge})


@tool(owner="user", rw="write")
def confirm_coverage_transfer_ce1107bd(ctx: ToolContext, warranty_registration_id: str,
                                       warranty_transfer_request_id: str, transfer_fee: float) -> str:
    """The registered owner who sold the home confirms, in person, the request to pass the warranty
    coverage to the buyer named on a transfer request already on file, and accepts the transfer fee. One
    call places the registration in transfer pending status with today's date as the date the transfer was
    requested, and adds one transfer fee entry for the given amount to the warranty charges of the
    registration, so the amount the seller owes rises by exactly that fee. The transfer request on file and
    the buyer details on it are left as they are. The owner sees the coverage shown as transfer pending and
    the fee among the warranty charges.

    Args:
        warranty_registration_id: Id class — the identifier of the
            coverage being passed to the buyer, as returned by the warranty registration lookup.
        warranty_transfer_request_id: Id class — the identifier of the transfer request on file that names
            the buyer and the home sale closing date, as returned by the warranty transfer request lookup.
        transfer_fee: Fixed-format class — the transfer fee the seller accepts, in USD, a non-negative
            amount rounded half up to 2 decimal places.

    Returns:
        A dictionary receipt: warranty_registration_id (text, the coverage now pending transfer),
        warranty_transfer_request_id (text, the request confirmed), status (text, always transfer_pending),
        transfer_requested_date (text, YYYY-MM-DD, today's date), warranty_activity_id (text, the reference
        of the transfer fee entry) and transfer_fee (number, USD to 2 decimal places, the fee booked). A
        receipt showing status transfer_pending means the transfer request is recorded and the fee charged.
    """
    today = ctx.now()[:10]
    regs = ctx.find("warranty_registrations", warranty_registration_id=warranty_registration_id)
    customer_id = regs[0].get("customer_id") if regs else ""
    fee = round(float(transfer_fee), 2)
    ctx.update("warranty_registrations", warranty_registration_id, status="transfer_pending",
               transfer_requested_date=today)
    rid = ctx.make_id("wac_", warranty_registration_id, warranty_transfer_request_id, fee, "transfer")
    ctx.create("warranty_activities", rid, warranty_activity_id=rid,
               warranty_registration_id=warranty_registration_id, customer_id=customer_id,
               event_type="warranty_charge_assessed", activity_date=today, warranty_claim_id="",
               component="not_applicable", claim_decision="not_applicable", visit_outcome="not_applicable",
               units=0, labor_hours=0.0, amount=fee, charge_kind="transfer_fee", source_warranty_activity_id="")
    return str({"warranty_registration_id": warranty_registration_id,
                "warranty_transfer_request_id": warranty_transfer_request_id, "status": "transfer_pending",
                "transfer_requested_date": today, "warranty_activity_id": rid, "transfer_fee": fee})


@tool(owner="agent", rw="write")
def bill_visit_labor_b6354c72(ctx: ToolContext, warranty_registration_id: str, warranty_claim_id: str,
                              visit_date: str, billable_hours: float, amount: float) -> str:
    """Bill the labor for one completed technician visit on a warranty claim. One call adds one labor charge
    entry to the warranty charges of the registration, dated with the date of the visit, tied to the claim
    the visit served, carrying the claim's component, the billable hours and the labor amount; the amount
    owed by the registered owner rises by exactly that labor amount. Nothing else on the registration or
    the claim changes. The owner can see the new labor charge on the warranty charges of the registration.

    Args:
        warranty_registration_id: Id class — the identifier of the registration the visit was made under,
            as returned by the warranty registration lookup.
        warranty_claim_id: Id class — the identifier of the warranty claim the visit served, as returned by
            the warranty claim lookup or shown on the visit in the warranty activity lookup.
        visit_date: Fixed-format class — the date of the technician visit exactly as shown on that visit in
            the warranty activity lookup, written YYYY-MM-DD; it becomes the date of the labor charge.
        billable_hours: Fixed-format class — the billable labor hours of the visit as the warranty labor
            terms define them, the hours the labor amount is priced on, in decimal hours to 1 decimal place,
            a non-negative number.
        amount: Fixed-format class — the labor charge owed for that visit, in USD, a positive amount rounded
            half up to 2 decimal places.

    Returns:
        A dictionary receipt: warranty_activity_id (text, the reference of the new labor charge entry),
        warranty_registration_id (text, the registration billed), warranty_claim_id (text, the claim the
        charge belongs to), charge_kind (text, always labor_charge), activity_date (text, YYYY-MM-DD, the
        date the charge carries), labor_hours (number, decimal hours to 1 decimal place) and amount (number,
        USD to 2 decimal places, the charge booked). A receipt carrying a warranty_activity_id means the
        labor charge is now on the registration's warranty charges.
    """
    regs = ctx.find("warranty_registrations", warranty_registration_id=warranty_registration_id)
    claims = ctx.find("warranty_claims", warranty_claim_id=warranty_claim_id)
    customer_id = regs[0].get("customer_id") if regs else ""
    component = claims[0].get("component") if claims else "not_applicable"
    hours = round(float(billable_hours), 1)
    charge = round(float(amount), 2)
    rid = ctx.make_id("wac_", warranty_registration_id, warranty_claim_id, visit_date, hours, charge, "labor")
    ctx.create("warranty_activities", rid, warranty_activity_id=rid,
               warranty_registration_id=warranty_registration_id, customer_id=customer_id,
               event_type="warranty_charge_assessed", activity_date=visit_date,
               warranty_claim_id=warranty_claim_id, component=component,
               claim_decision="not_applicable", visit_outcome="not_applicable", units=0,
               labor_hours=hours, amount=charge, charge_kind="labor_charge", source_warranty_activity_id="")
    return str({"warranty_activity_id": rid, "warranty_registration_id": warranty_registration_id,
                "warranty_claim_id": warranty_claim_id, "charge_kind": "labor_charge",
                "activity_date": visit_date, "labor_hours": hours, "amount": charge})


@tool(owner="user", rw="write")
def accept_prorated_glass_share_5fbbc0c6(ctx: ToolContext, warranty_registration_id: str, warranty_claim_id: str,
                                         units: int, share_amount: float) -> str:
    """The registered owner accepts, in person, a prorated replacement of sealed glass units approved on a
    seal-failure claim and agrees to pay the owner's share. One call adds one prorated parts share entry,
    dated today, to the warranty charges of the registration, tied to the claim, carrying the claim's
    component and the number of units accepted; the amount the owner owes rises by exactly that share.
    Nothing else on the registration or the claim changes. The owner sees the share among the warranty
    charges.

    Args:
        warranty_registration_id: Id class — the identifier of the registration the claim was decided
            under, as returned by the warranty registration lookup.
        warranty_claim_id: Id class — the identifier of the seal-failure claim approved with proration, as
            returned by the warranty claim lookup.
        units: Fixed-format class — the number of sealed units approved for prorated replacement on the
            claim's decision and accepted by the owner, a non-negative integer count.
        share_amount: Fixed-format class — the owner's share the owner agrees to pay, in USD, a positive
            amount rounded half up to 2 decimal places.

    Returns:
        A dictionary receipt: warranty_activity_id (text, the reference of the new share entry),
        warranty_registration_id (text, the registration charged), warranty_claim_id (text, the claim the
        share belongs to), charge_kind (text, always prorated_parts_share), activity_date (text, YYYY-MM-DD,
        today's date), units (integer, the units accepted) and share_amount (number, USD to 2 decimal
        places, the share booked). A receipt carrying a warranty_activity_id means the share is recorded.
    """
    today = ctx.now()[:10]
    regs = ctx.find("warranty_registrations", warranty_registration_id=warranty_registration_id)
    claims = ctx.find("warranty_claims", warranty_claim_id=warranty_claim_id)
    customer_id = regs[0].get("customer_id") if regs else ""
    component = claims[0].get("component") if claims else "not_applicable"
    count = int(units)
    share = round(float(share_amount), 2)
    rid = ctx.make_id("wac_", warranty_registration_id, warranty_claim_id, count, share, "share")
    ctx.create("warranty_activities", rid, warranty_activity_id=rid,
               warranty_registration_id=warranty_registration_id, customer_id=customer_id,
               event_type="warranty_charge_assessed", activity_date=today,
               warranty_claim_id=warranty_claim_id, component=component,
               claim_decision="not_applicable", visit_outcome="not_applicable", units=count,
               labor_hours=0.0, amount=share, charge_kind="prorated_parts_share", source_warranty_activity_id="")
    return str({"warranty_activity_id": rid, "warranty_registration_id": warranty_registration_id,
                "warranty_claim_id": warranty_claim_id, "charge_kind": "prorated_parts_share",
                "activity_date": today, "units": count, "share_amount": share})

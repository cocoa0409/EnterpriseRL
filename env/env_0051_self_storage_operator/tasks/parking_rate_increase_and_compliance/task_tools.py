"""Hidden task tools for the parking_rate_increase_and_compliance difficulty (Bluegate parking agreements).

Each tool lands exactly one atomic business write on a vehicle, RV or boat parking agreement with the
values it is given; it reads the agreement only to copy its tenant and running balance onto the new
entry and never decides eligibility, amounts or timing.
"""

from erlbench import ToolContext, tool


@tool(owner="agent", rw="write")
def credit_parking_billing_error_d978766a(ctx: ToolContext, parking_rental_id: str, reference_entry_id: str,
                                          amount: float) -> dict:
    """Post a billing-error correction credit on a parking agreement's ledger against one fee entry.

    The care agent uses this to correct a fee that was charged in error: one credit entry of the kind
    "billing error correction", dated today and tied to the fee entry it corrects, is added to the
    agreement's ledger, and the agreement's balance due is lowered by the credited amount. The tenant
    sees the credit on the ledger and the lower balance at once. The call is complete when the receipt
    comes back with the new credit entry number and the resulting balance due.

    Args:
        parking_rental_id: Id class — the parking agreement number of the agreement being credited, as
            returned by the parking agreement lookup for this tenant.
        reference_entry_id: Id class — the ledger entry number of the fee charge this credit corrects, as
            returned by the parking ledger lookup for the agreement.
        amount: Fixed-format class — the credit amount in USD, a positive number with 2 decimal places;
            the value is stored rounded half-up to the cent exactly as given.

    Returns:
        dict with credit_entry_id (str, the new ledger entry number), parking_rental_id (str, the agreement
        credited), reference_entry_id (str, the fee entry the credit applies against), credit_type (str,
        always billing_error_correction), amount (float, USD with 2 decimal places as booked), entry_date
        (str, YYYY-MM-DD posting date) and balance_due (float, USD with 2 decimal places, the agreement's resulting
        balance due; negative means a credit balance).
    """
    rental = (ctx.find("parking_rentals", parking_rental_id=parking_rental_id) or [{}])[0]
    amt = round(float(amount), 2)
    rid = ctx.make_id("pke_", parking_rental_id, reference_entry_id, amt, "billing_error_correction")
    ctx.create("parking_ledger", rid, parking_entry_id=rid, parking_rental_id=parking_rental_id,
               customer_id=rental.get("customer_id"), event_type="parking_credit", amount=amt,
               entry_date=ctx.now()[:10], credit_type="billing_error_correction",
               reference_entry_id=reference_entry_id)
    bal = round(float(rental.get("balance_due") or 0) - amt, 2)
    ctx.update("parking_rentals", parking_rental_id, balance_due=bal)
    return {"credit_entry_id": rid, "parking_rental_id": parking_rental_id,
            "reference_entry_id": reference_entry_id, "credit_type": "billing_error_correction",
            "amount": amt, "entry_date": ctx.now()[:10], "balance_due": bal}


@tool(owner="agent", rw="write")
def post_parking_late_fee_42918014(ctx: ToolContext, parking_rental_id: str, reference_entry_id: str,
                                   period_start: str, amount: float) -> dict:
    """Post a late fee on a parking agreement's ledger for one billing period whose rent is unpaid.

    The care agent uses this to book a late fee: one fee entry of the kind "late fee", dated today, tied
    to the unpaid rent charge it arises from and to that billing period's due date, is added to the
    agreement's ledger, and the agreement's balance due rises by the fee. The tenant sees the fee on the
    ledger and the higher balance at once. The call is complete when the receipt comes back with the
    new fee entry number and the resulting balance due.

    Args:
        parking_rental_id: Id class — the parking agreement number of the agreement being charged, as
            returned by the parking agreement lookup for this tenant.
        reference_entry_id: Id class — the ledger entry number of the unpaid rent charge the late fee
            arises from, as returned by the parking ledger lookup for the agreement.
        period_start: Fixed-format class — the due date of the billing period the late fee relates to, in
            YYYY-MM-DD format, exactly as shown on that rent charge.
        amount: Fixed-format class — the late fee in USD, a positive number with 2 decimal places; the value
            is stored rounded half-up to the cent exactly as given.

    Returns:
        dict with fee_entry_id (str, the new ledger entry number), parking_rental_id (str, the agreement
        charged), reference_entry_id (str, the rent charge the fee arises from), fee_type (str, always
        late_fee), period_start (str, YYYY-MM-DD due date of the period), amount (float, USD with 2 decimal
        places as booked), entry_date (str, YYYY-MM-DD posting date) and balance_due (float, USD with 2
        decimal places, the agreement's resulting balance due).
    """
    rental = (ctx.find("parking_rentals", parking_rental_id=parking_rental_id) or [{}])[0]
    amt = round(float(amount), 2)
    rid = ctx.make_id("pke_", parking_rental_id, reference_entry_id, period_start, amt, "late_fee")
    ctx.create("parking_ledger", rid, parking_entry_id=rid, parking_rental_id=parking_rental_id,
               customer_id=rental.get("customer_id"), event_type="parking_fee_charge", amount=amt,
               entry_date=ctx.now()[:10], period_start=period_start, fee_type="late_fee",
               reference_entry_id=reference_entry_id)
    bal = round(float(rental.get("balance_due") or 0) + amt, 2)
    ctx.update("parking_rentals", parking_rental_id, balance_due=bal)
    return {"fee_entry_id": rid, "parking_rental_id": parking_rental_id,
            "reference_entry_id": reference_entry_id, "fee_type": "late_fee", "period_start": period_start,
            "amount": amt, "entry_date": ctx.now()[:10], "balance_due": bal}


@tool(owner="user", rw="write")
def pay_parking_past_due_d726500b(ctx: ToolContext, parking_rental_id: str, amount: float,
                                  payment_method: str) -> dict:
    """Make a one-time payment from the tenant's own card or bank account on a parking agreement.

    The tenant runs this to pay toward their own parking agreement over the phone: one payment entry for
    the amount given, dated today, taken through the care center by the method the tenant names, is added
    to the agreement's ledger, and the agreement's balance due is lowered by that amount (it may go below
    zero, which is a credit carried toward future rent). The tenant sees the payment on the ledger and
    the new balance at once. The call is complete when the receipt comes back with the payment entry
    number and the resulting balance due.

    Args:
        parking_rental_id: Id class — the parking agreement number the payment is for, as the care agent
            reads it from the parking agreement lookup and gives it to the tenant.
        amount: Fixed-format class — the amount paid in USD, a positive number with 2 decimal places; the
            value is stored rounded half-up to the cent exactly as given.
        payment_method: Enum class — how the tenant pays: credit_card when the tenant pays with a credit
            card; debit_card when the tenant pays with a debit card drawn on their bank account;
            ach_bank_account when the tenant pays by giving a checking or savings account and routing number;
            cash when the tenant hands over bank notes at a facility office; money_order when the tenant
            sends or hands in a money order; prepaid_rent_plan when a month is applied from a Bluegate
            prepaid rent plan rather than paid from the tenant's own funds.

    Returns:
        dict with payment_entry_id (str, the new ledger entry number), parking_rental_id (str, the agreement
        paid), amount (float, USD with 2 decimal places as booked), payment_method (str, the method
        recorded), payment_channel (str, always care_center_phone), entry_date (str, YYYY-MM-DD date
        received) and balance_due (float, USD with 2 decimal places, the agreement's resulting balance due;
        negative means a credit balance).
    """
    rental = (ctx.find("parking_rentals", parking_rental_id=parking_rental_id) or [{}])[0]
    amt = round(float(amount), 2)
    rid = ctx.make_id("pke_", parking_rental_id, amt, payment_method, "care_center_phone", ctx.now())
    ctx.create("parking_ledger", rid, parking_entry_id=rid, parking_rental_id=parking_rental_id,
               customer_id=rental.get("customer_id"), event_type="parking_payment", amount=amt,
               entry_date=ctx.now()[:10], payment_method=payment_method, payment_channel="care_center_phone")
    bal = round(float(rental.get("balance_due") or 0) - amt, 2)
    ctx.update("parking_rentals", parking_rental_id, balance_due=bal)
    return {"payment_entry_id": rid, "parking_rental_id": parking_rental_id, "amount": amt,
            "payment_method": payment_method, "payment_channel": "care_center_phone",
            "entry_date": ctx.now()[:10], "balance_due": bal}


@tool(owner="agent", rw="write")
def grant_parking_retention_concession_aac1dee9(ctx: ToolContext, parking_rental_id: str,
                                                source_rate_change_id: str, new_rent: float) -> dict:
    """Record a retention concession that lowers a noticed parking rent increase.

    The care agent uses this to grant a retention concession on one noticed rent increase: a rent change
    notice of the kind "retention concession", dated today, is added to the agreement's rent change
    history with the concession rent given, linked to the increase it modifies and carrying that
    increase's effective date, pre-increase rent, street rate and tenure at notice. The tenant
    sees the concession rent as the rent that will apply from the increase's effective date. The call is
    complete when the receipt comes back with the concession's rent change number.

    Args:
        parking_rental_id: Id class — the parking agreement number of the agreement whose increase is
            lowered, as returned by the parking agreement lookup for this tenant.
        source_rate_change_id: Id class — the rent change number of the noticed increase the concession
            modifies, as returned by the parking rent change lookup for the agreement.
        new_rent: Fixed-format class — the monthly rent in USD that applies under the concession, with 2
            decimal places; the value is stored rounded half-up to the cent exactly as given.

    Returns:
        dict with rate_change_id (str, the concession's rent change number), parking_rental_id (str),
        source_rate_change_id (str, the increase modified), change_reason (str, always
        retention_concession), previous_rent (float, USD with 2 decimal places, the pre-increase rent of the
        increase), new_rent (float, USD with 2 decimal places, the concession rent), notice_date (str,
        YYYY-MM-DD date granted) and effective_date (str, YYYY-MM-DD rent due date from which the concession
        rent applies).
    """
    src = (ctx.find("parking_rate_changes", parking_rate_change_id=source_rate_change_id) or [{}])[0]
    rent = round(float(new_rent), 2)
    rid = ctx.make_id("prc_", parking_rental_id, source_rate_change_id, rent, "retention_concession")
    ctx.create("parking_rate_changes", rid, parking_rate_change_id=rid, parking_rental_id=parking_rental_id,
               customer_id=src.get("customer_id"), event_type="parking_rate_change_notice",
               change_reason="retention_concession", previous_rent=src.get("previous_rent"), new_rent=rent,
               street_rate_at_notice=src.get("street_rate_at_notice"),
               tenure_months_at_notice=src.get("tenure_months_at_notice"), notice_date=ctx.now()[:10],
               effective_date=src.get("effective_date"), source_rate_change_id=source_rate_change_id)
    return {"rate_change_id": rid, "parking_rental_id": parking_rental_id,
            "source_rate_change_id": source_rate_change_id, "change_reason": "retention_concession",
            "previous_rent": src.get("previous_rent"), "new_rent": rent, "notice_date": ctx.now()[:10],
            "effective_date": src.get("effective_date")}


@tool(owner="agent", rw="write")
def post_parking_tow_notice_fee_6c1b851a(ctx: ToolContext, parking_rental_id: str, reference_entry_id: str,
                                         period_start: str, amount: float) -> dict:
    """Post the notice-of-intent-to-tow fee on a parking agreement's ledger.

    The care agent uses this to book the fee that goes with a notice of intent to tow: one fee entry of
    the kind "tow notice fee", dated today, tied to the oldest unpaid rent charge of the delinquency
    cycle and to that period's due date, is added to the agreement's ledger, and the agreement's balance
    due rises by the fee. The tenant sees the fee on the ledger and the higher balance at once. The call
    is complete when the receipt comes back with the new fee entry number and the resulting balance due.

    Args:
        parking_rental_id: Id class — the parking agreement number of the agreement being charged, as
            returned by the parking agreement lookup for this tenant.
        reference_entry_id: Id class — the ledger entry number of the oldest unpaid rent charge of the
            delinquency cycle the notice was sent for, as returned by the parking ledger lookup.
        period_start: Fixed-format class — the due date of that oldest unpaid billing period, in YYYY-MM-DD
            format, exactly as shown on that rent charge.
        amount: Fixed-format class — the tow notice fee in USD, a positive number with 2 decimal places; the
            value is stored rounded half-up to the cent exactly as given.

    Returns:
        dict with fee_entry_id (str, the new ledger entry number), parking_rental_id (str, the agreement
        charged), reference_entry_id (str, the rent charge the fee relates to), fee_type (str, always
        tow_notice_fee), period_start (str, YYYY-MM-DD), amount (float, USD with 2 decimal places as
        booked), entry_date (str, YYYY-MM-DD posting date) and balance_due (float, USD with 2 decimal
        places, the agreement's resulting balance due).
    """
    rental = (ctx.find("parking_rentals", parking_rental_id=parking_rental_id) or [{}])[0]
    amt = round(float(amount), 2)
    rid = ctx.make_id("pke_", parking_rental_id, reference_entry_id, period_start, amt, "tow_notice_fee")
    ctx.create("parking_ledger", rid, parking_entry_id=rid, parking_rental_id=parking_rental_id,
               customer_id=rental.get("customer_id"), event_type="parking_fee_charge", amount=amt,
               entry_date=ctx.now()[:10], period_start=period_start, fee_type="tow_notice_fee",
               reference_entry_id=reference_entry_id)
    bal = round(float(rental.get("balance_due") or 0) + amt, 2)
    ctx.update("parking_rentals", parking_rental_id, balance_due=bal)
    return {"fee_entry_id": rid, "parking_rental_id": parking_rental_id,
            "reference_entry_id": reference_entry_id, "fee_type": "tow_notice_fee", "period_start": period_start,
            "amount": amt, "entry_date": ctx.now()[:10], "balance_due": bal}


@tool(owner="user", rw="write")
def pay_parking_tow_redemption_54345a56(ctx: ToolContext, parking_rental_id: str, amount: float,
                                        payment_method: str) -> dict:
    """Redeem a parking agreement under a notice of intent to tow with a payment from the tenant's own funds.

    The tenant runs this to pay off their own parking agreement while a notice of intent to tow stands:
    one payment entry for the amount given, dated today, taken through the care center by the method the
    tenant names, is added to the agreement's ledger, the balance due is lowered by that amount, and the
    agreement is returned to active standing with its delinquency date cleared and the gate code
    restored. The tenant sees the payment, the new balance and the active standing at once. The call is
    complete when the receipt comes back with the payment entry number, the resulting balance due and the
    status active.

    Args:
        parking_rental_id: Id class — the parking agreement number the redemption is for, as the care agent
            reads it from the parking agreement lookup and gives it to the tenant.
        amount: Fixed-format class — the amount paid in USD, a positive number with 2 decimal places; the
            value is stored rounded half-up to the cent exactly as given.
        payment_method: Enum class — how the tenant pays: credit_card when the tenant pays with a credit
            card; debit_card when the tenant pays with a debit card drawn on their bank account;
            ach_bank_account when the tenant pays by giving a checking or savings account and routing number;
            cash when the tenant hands over bank notes at a facility office; money_order when the tenant
            sends or hands in a money order; prepaid_rent_plan when a month is applied from a Bluegate
            prepaid rent plan rather than paid from the tenant's own funds.

    Returns:
        dict with payment_entry_id (str, the new ledger entry number), parking_rental_id (str, the agreement
        redeemed), amount (float, USD with 2 decimal places as booked), payment_method (str, the method
        recorded), entry_date (str, YYYY-MM-DD date received), balance_due (float, USD with 2 decimal
        places, the resulting balance due; negative means a credit balance) and status (str, always active,
        the agreement's standing on completion).
    """
    rental = (ctx.find("parking_rentals", parking_rental_id=parking_rental_id) or [{}])[0]
    amt = round(float(amount), 2)
    rid = ctx.make_id("pke_", parking_rental_id, amt, payment_method, "tow_redemption", ctx.now())
    ctx.create("parking_ledger", rid, parking_entry_id=rid, parking_rental_id=parking_rental_id,
               customer_id=rental.get("customer_id"), event_type="parking_payment", amount=amt,
               entry_date=ctx.now()[:10], payment_method=payment_method, payment_channel="care_center_phone")
    bal = round(float(rental.get("balance_due") or 0) - amt, 2)
    ctx.update("parking_rentals", parking_rental_id, balance_due=bal, status="active", delinquent_since="")
    return {"payment_entry_id": rid, "parking_rental_id": parking_rental_id, "amount": amt,
            "payment_method": payment_method, "entry_date": ctx.now()[:10], "balance_due": bal, "status": "active"}


@tool(owner="agent", rw="write")
def swap_parking_vehicle_d3106476(ctx: ToolContext, parking_rental_id: str, vehicle_type: str, vehicle_length_ft: int,
                                  vehicle_plate: str, registration_expiry: str, insurance_expiry: str,
                                  swap_fee: float) -> dict:
    """Put a different vehicle on file for a parking agreement and post the vehicle swap fee.

    The care agent uses this when a tenant replaces the vehicle kept in their space: the vehicle type,
    overall length, plate and the registration and insurance expiry dates on file are replaced with the
    new vehicle's details, and one fee entry of the kind "vehicle swap fee", dated today with today as its
    request date, is added to the agreement's ledger, raising the balance due by the fee. The tenant sees
    the new vehicle on file and the fee on the ledger at once. The call is complete when the receipt comes
    back with the vehicle details now on file, the fee entry number and the resulting balance due.

    Args:
        parking_rental_id: Id class — the parking agreement number whose vehicle on file is replaced, as
            returned by the parking agreement lookup for this tenant.
        vehicle_type: Enum class — the type of the new vehicle: car_or_pickup for a passenger car, SUV or
            pickup truck; motorcycle for a motorcycle or scooter; utility_trailer for an open or enclosed
            utility trailer; boat_on_trailer for a boat kept on its trailer; travel_trailer for a bumper-pull
            travel trailer; fifth_wheel for a fifth-wheel trailer; class_a_motorhome for a bus-style motorhome;
            class_b_motorhome for a camper van; class_c_motorhome for a cab-over motorhome on a truck chassis.
        vehicle_length_ft: Fixed-format class — the new vehicle's overall length including any tongue or
            outboard motor, an integer number of feet as the tenant reads it from the registration.
        vehicle_plate: Verbatim class — the new vehicle's plate number exactly as the tenant reads it from
            the registration card, copied character for character with no spacing or letter changes (verbatim).
        registration_expiry: Fixed-format class — the expiry date printed on the new vehicle's registration,
            in YYYY-MM-DD format.
        insurance_expiry: Fixed-format class — the expiry date printed on the new vehicle's liability
            insurance card, in YYYY-MM-DD format.
        swap_fee: Fixed-format class — the vehicle swap fee in USD, a positive number with 2 decimal places;
            the value is stored rounded half-up to the cent exactly as given.

    Returns:
        dict with parking_rental_id (str), vehicle_type (str), vehicle_length_ft (int, feet), vehicle_plate
        (str), registration_expiry (str, YYYY-MM-DD), insurance_expiry (str, YYYY-MM-DD) — the vehicle now on
        file — and fee_entry_id (str, the new ledger entry number), fee_type (str, always vehicle_swap_fee),
        swap_fee (float, USD with 2 decimal places as booked), entry_date (str, YYYY-MM-DD) and balance_due
        (float, USD with 2 decimal places, the agreement's resulting balance due; negative means a credit
        balance).
    """
    rental = (ctx.find("parking_rentals", parking_rental_id=parking_rental_id) or [{}])[0]
    fee = round(float(swap_fee), 2)
    length = int(vehicle_length_ft)
    ctx.update("parking_rentals", parking_rental_id, vehicle_type=vehicle_type, vehicle_length_ft=length,
               vehicle_plate=vehicle_plate, registration_expiry=registration_expiry, insurance_expiry=insurance_expiry)
    rid = ctx.make_id("pke_", parking_rental_id, vehicle_type, length, vehicle_plate, registration_expiry,
                      insurance_expiry, fee, "vehicle_swap_fee")
    ctx.create("parking_ledger", rid, parking_entry_id=rid, parking_rental_id=parking_rental_id,
               customer_id=rental.get("customer_id"), event_type="parking_fee_charge", amount=fee,
               entry_date=ctx.now()[:10], period_start=ctx.now()[:10], fee_type="vehicle_swap_fee")
    bal = round(float(rental.get("balance_due") or 0) + fee, 2)
    ctx.update("parking_rentals", parking_rental_id, balance_due=bal)
    return {"parking_rental_id": parking_rental_id, "vehicle_type": vehicle_type, "vehicle_length_ft": length,
            "vehicle_plate": vehicle_plate, "registration_expiry": registration_expiry,
            "insurance_expiry": insurance_expiry, "fee_entry_id": rid, "fee_type": "vehicle_swap_fee",
            "swap_fee": fee, "entry_date": ctx.now()[:10], "balance_due": bal}

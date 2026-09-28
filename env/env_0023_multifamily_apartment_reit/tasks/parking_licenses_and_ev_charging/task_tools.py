"""Hidden task tools of the parking_licenses_and_ev_charging difficulty (Larkspur Residential Trust).

Each tool lands one atomic change on a parking license or its ledger with the values the caller supplies;
it judges no eligibility and computes no amount. Every tool is named by exactly one extended policy's
target_tool in parking.extended.yaml and is reached through the unlock/call meta-tools.
"""

from erlbench import ToolContext, tool


@tool(owner="agent", rw="write")
def credit_idle_fee_rerate_1959dfce(ctx: ToolContext, parking_license_id: str, source_parking_charge_id: str,
                                    credit_amount: float) -> str:
    """Post a correction credit against one EV charging idle fee line of a parking license.

    The resident services agent uses this to reduce one idle fee line that was billed on a resident's parking
    license: one charge reversal credit is added to the license's parking ledger for exactly the amount given,
    pointing at the idle fee line it corrects, dated today and belonging to the current billing month, and the
    license's outstanding parking balance goes down by the same amount. The idle fee line itself stays on the
    ledger unchanged; the resident sees the credit on the parking statement next to that line. The call is
    complete when the receipt below comes back with the new credit's reference number.

    Args:
        parking_license_id: Id class — the reference number of the resident's parking license whose ledger
            receives the credit, as returned by the parking license lookup.
        source_parking_charge_id: Id class — the reference number of the idle fee line being corrected, as
            returned for that line by the parking charges lookup.
        credit_amount: Fixed-format class — the amount credited against the idle fee line, in USD, a positive
            amount written with 2 decimal places (cents); any further digits are rounded half up to the cent
            when the credit is posted.

    Returns:
        A dictionary receipt: credit_id (text, the reference number of the new credit line),
        parking_license_id (text, the license credited), source_parking_charge_id (text, the idle fee line the
        credit points at), charge_code (text, always charge_reversal), credit_amount (number, USD with 2
        decimal places, the amount credited), posted_on (text, YYYY-MM-DD, today's posting date) and
        resulting_parking_balance (number, USD with 2 decimal places, the license's outstanding parking balance
        including this credit). A receipt carrying credit_id means the credit is on the ledger.
    """
    rows = ctx.find("parking_licenses", parking_license_id=parking_license_id)
    lic = rows[0] if rows else {}
    rid = ctx.make_id("pcr_", parking_license_id, source_parking_charge_id, credit_amount)
    today = ctx.now()[:10]
    ctx.create("parking_charges", rid, parking_charge_id=rid, parking_license_id=parking_license_id,
               customer_id=lic.get("customer_id", ""), event_type="parking_credit", charge_code="charge_reversal",
               billing_period=today[:7], charge_date=today, amount=round(float(credit_amount), 2), energy_kwh=0,
               rate_period="not_applicable", idle_minutes=0, session_reference="", proration_days=0,
               days_in_period=0, source_parking_charge_id=source_parking_charge_id, source_activity_id="",
               payment_method="not_applicable", payment_reference="")
    balance = round(float(lic.get("balance_due") or 0) - round(float(credit_amount), 2), 2)
    ctx.update("parking_licenses", parking_license_id, balance_due=balance)
    return str({"credit_id": rid, "parking_license_id": parking_license_id,
                "source_parking_charge_id": source_parking_charge_id, "charge_code": "charge_reversal",
                "credit_amount": round(float(credit_amount), 2), "posted_on": ctx.now()[:10],
                "resulting_parking_balance": balance})


@tool(owner="user", rw="write")
def sign_parking_cancellation_notice_d2378b15(ctx: ToolContext, parking_license_id: str, end_date: str,
                                              early_cancellation_fee: float) -> str:
    """Sign, as the resident, a cancellation notice that ends one of your parking licenses on a chosen date.

    The resident signs the notice in person: the parking license moves to notice-given status with the stated
    end date as its last licensed day, and when the notice carries an early cancellation fee above zero that fee
    is billed on the license's parking ledger today and added to the outstanding parking balance; a fee of 0.00
    bills nothing. The space stays usable through the end date. The signature is complete when the receipt below
    comes back with the notice status and, for a fee above zero, the reference number of the fee line.

    Args:
        parking_license_id: Id class — the reference number of the parking license being cancelled, as read to
            you by the agent from the parking license lookup.
        end_date: Fixed-format class — the last licensed day you are choosing for the space, written
            YYYY-MM-DD as a calendar date in the community's local time.
        early_cancellation_fee: Fixed-format class — the early cancellation fee the notice carries, in USD,
            written with 2 decimal places (cents), 0.00 when the notice carries no fee; any further digits are
            rounded half up to the cent.

    Returns:
        A dictionary receipt: parking_license_id (text, the license the notice ends), status (text, always
        notice_given for a signed notice), end_date (text, YYYY-MM-DD, the last licensed day), fee_line_id (text, the
        reference number of the early cancellation fee line, empty when the fee is 0.00),
        early_cancellation_fee (number, USD with 2 decimal places, the fee billed) and
        resulting_parking_balance (number, USD with 2 decimal places, the license's outstanding parking balance
        including any fee the notice bills). A receipt with status notice_given means the notice is signed.
    """
    rows = ctx.find("parking_licenses", parking_license_id=parking_license_id)
    lic = rows[0] if rows else {}
    fee = round(float(early_cancellation_fee), 2)
    ctx.update("parking_licenses", parking_license_id, status="notice_given", end_date=end_date)
    fee_line_id = ""
    balance = round(float(lic.get("balance_due") or 0), 2)
    if fee > 0:
        fee_line_id = ctx.make_id("pfc_", parking_license_id, end_date, early_cancellation_fee)
        today = ctx.now()[:10]
        ctx.create("parking_charges", fee_line_id, parking_charge_id=fee_line_id, parking_license_id=parking_license_id,
                   customer_id=lic.get("customer_id", ""), event_type="parking_fee_charge", charge_code="early_cancellation_fee",
                   billing_period=today[:7], charge_date=today, amount=fee, energy_kwh=0,
                   rate_period="not_applicable", idle_minutes=0, session_reference="", proration_days=0,
                   days_in_period=0, source_parking_charge_id="", source_activity_id="",
                   payment_method="not_applicable", payment_reference="")
        balance = round(balance + fee, 2)
        ctx.update("parking_licenses", parking_license_id, balance_due=balance)
    return str({"parking_license_id": parking_license_id, "status": "notice_given", "end_date": end_date,
                "fee_line_id": fee_line_id, "early_cancellation_fee": fee,
                "resulting_parking_balance": balance})


@tool(owner="agent", rw="write")
def credit_violation_fine_rerate_f29c2916(ctx: ToolContext, parking_license_id: str, source_activity_id: str,
                                         source_parking_charge_id: str, credit_amount: float) -> str:
    """Post a correction credit against one violation fine billed on a parking license.

    The resident services agent uses this to reduce one violation fine on a resident's parking license: one charge
    reversal credit is added to the license's parking ledger for exactly the amount given, pointing both at the fine
    line it reduces and at the violation that fine bills, dated today and belonging to the current billing month,
    and the license's outstanding parking balance goes down by the same amount. The violation record and the fine
    line stay unchanged; the resident sees the credit next to the fine on the parking statement. The call is
    complete when the receipt below comes back with the new credit's reference number.

    Args:
        parking_license_id: Id class — the reference number of the resident's parking license whose ledger
            receives the credit, as returned by the parking license lookup.
        source_activity_id: Id class — the reference number of the violation record the fine bills, as returned by
            the parking activity lookup and shown on the fine line.
        source_parking_charge_id: Id class — the reference number of the fine line being reduced, as returned for
            that line by the parking charges lookup.
        credit_amount: Fixed-format class — the amount credited against the fine, in USD, a positive amount written
            with 2 decimal places (cents); any further digits are rounded half up to the cent when the credit is
            posted.

    Returns:
        A dictionary receipt: credit_id (text, the reference number of the new credit line), parking_license_id
        (text, the license credited), source_activity_id (text, the violation the fine bills),
        source_parking_charge_id (text, the fine line the credit points at), charge_code (text, always
        charge_reversal), credit_amount (number, USD with 2 decimal places, the amount credited), posted_on (text,
        YYYY-MM-DD, today's posting date) and resulting_parking_balance (number, USD with 2 decimal places, the
        license's outstanding parking balance including this credit). A receipt carrying credit_id means the
        credit is on the ledger.
    """
    rows = ctx.find("parking_licenses", parking_license_id=parking_license_id)
    lic = rows[0] if rows else {}
    rid = ctx.make_id("pcr_", parking_license_id, source_activity_id, source_parking_charge_id, credit_amount)
    today = ctx.now()[:10]
    ctx.create("parking_charges", rid, parking_charge_id=rid, parking_license_id=parking_license_id,
               customer_id=lic.get("customer_id", ""), event_type="parking_credit", charge_code="charge_reversal",
               billing_period=today[:7], charge_date=today, amount=round(float(credit_amount), 2), energy_kwh=0,
               rate_period="not_applicable", idle_minutes=0, session_reference="", proration_days=0,
               days_in_period=0, source_parking_charge_id=source_parking_charge_id,
               source_activity_id=source_activity_id, payment_method="not_applicable", payment_reference="")
    balance = round(float(lic.get("balance_due") or 0) - round(float(credit_amount), 2), 2)
    ctx.update("parking_licenses", parking_license_id, balance_due=balance)
    return str({"credit_id": rid, "parking_license_id": parking_license_id, "source_activity_id": source_activity_id,
                "source_parking_charge_id": source_parking_charge_id, "charge_code": "charge_reversal",
                "credit_amount": round(float(credit_amount), 2), "posted_on": today,
                "resulting_parking_balance": balance})


@tool(owner="agent", rw="write")
def credit_bundle_discount_a8c94fb6(ctx: ToolContext, parking_license_id: str, source_parking_charge_id: str,
                                   discount_amount: float) -> str:
    """Post a storage bundle discount credit against one monthly license fee line of a parking license.

    The resident services agent uses this to grant the storage bundle discount on one monthly license fee line: one
    bundle discount credit is added to the license's parking ledger for exactly the amount given, pointing at the
    monthly fee line it discounts, dated today and belonging to the current billing month, and the license's
    outstanding parking balance goes down by the same amount. The fee line itself stays unchanged; the resident sees
    the discount next to that month's fee on the parking statement. The call is complete when the receipt below
    comes back with the new credit's reference number.

    Args:
        parking_license_id: Id class — the reference number of the resident's parking license whose ledger
            receives the discount, as returned by the parking license lookup.
        source_parking_charge_id: Id class — the reference number of the monthly license fee line being
            discounted, as returned for that line by the parking charges lookup.
        discount_amount: Fixed-format class — the discount credited against the fee line, in USD, a positive amount
            written with 2 decimal places (cents); any further digits are rounded half up to the cent when the
            credit is posted.

    Returns:
        A dictionary receipt: credit_id (text, the reference number of the new discount line),
        parking_license_id (text, the license credited), source_parking_charge_id (text, the monthly fee line the
        discount points at), charge_code (text, always bundle_discount), discount_amount (number, USD with 2
        decimal places, the discount credited), posted_on (text, YYYY-MM-DD, today's posting date) and
        resulting_parking_balance (number, USD with 2 decimal places, the license's outstanding parking balance
        including this discount). A receipt carrying credit_id means the discount is on the ledger.
    """
    rows = ctx.find("parking_licenses", parking_license_id=parking_license_id)
    lic = rows[0] if rows else {}
    rid = ctx.make_id("pbd_", parking_license_id, source_parking_charge_id, discount_amount)
    today = ctx.now()[:10]
    ctx.create("parking_charges", rid, parking_charge_id=rid, parking_license_id=parking_license_id,
               customer_id=lic.get("customer_id", ""), event_type="parking_credit", charge_code="bundle_discount",
               billing_period=today[:7], charge_date=today, amount=round(float(discount_amount), 2), energy_kwh=0,
               rate_period="not_applicable", idle_minutes=0, session_reference="", proration_days=0,
               days_in_period=0, source_parking_charge_id=source_parking_charge_id, source_activity_id="",
               payment_method="not_applicable", payment_reference="")
    balance = round(float(lic.get("balance_due") or 0) - round(float(discount_amount), 2), 2)
    ctx.update("parking_licenses", parking_license_id, balance_due=balance)
    return str({"credit_id": rid, "parking_license_id": parking_license_id,
                "source_parking_charge_id": source_parking_charge_id, "charge_code": "bundle_discount",
                "discount_amount": round(float(discount_amount), 2), "posted_on": today,
                "resulting_parking_balance": balance})


@tool(owner="user", rw="write")
def pay_parking_balance_59b25ecc(ctx: ToolContext, parking_license_id: str, payment_amount: float,
                                 payment_method: str) -> str:
    """Pay, as the resident, an amount toward the parking balance of one of your parking licenses.

    The resident makes the payment in person through the resident portal: one payment line for exactly the amount
    given is received on the license's parking ledger today with the chosen payment instrument and a newly issued
    confirmation number, and the license's outstanding parking balance goes down by the amount paid (it may fall
    below zero, which is a credit held on the license). The payment is complete when the receipt below comes back
    with its confirmation number.

    Args:
        parking_license_id: Id class — the reference number of the parking license the payment is for, as read to
            you by the agent from the parking license lookup.
        payment_amount: Fixed-format class — the amount you pay, in USD, a positive amount written with 2 decimal
            places (cents); any further digits are rounded half up to the cent.
        payment_method: Enum class — the instrument you pay with, exactly one of: ach_autopay — a recurring
            portal bank draft already enrolled on the account runs the payment; ach_one_time — you authorise a
            single bank-account draft for this payment; debit_card — you pay with a debit card; credit_card — you
            pay with a credit card; money_order — you pay with a money order handed in at the leasing office;
            cashiers_check — you pay with a cashier's check handed in at the leasing office; deposit_application —
            only the property applies a security deposit at final accounting, never a resident paying today;
            not_applicable — marks lines that are not payments and is never a payment instrument.

    Returns:
        A dictionary receipt: payment_id (text, the reference number of the payment line), parking_license_id
        (text, the license paid), payment_amount (number, USD with 2 decimal places, the amount received),
        payment_method (text, the instrument used), confirmation_number (text, the confirmation number issued for
        this payment), received_on (text, YYYY-MM-DD, today's date) and resulting_parking_balance (number, USD with
        2 decimal places, the license's outstanding parking balance including this payment; below zero means
        a credit). A receipt carrying a confirmation_number means the payment was received.
    """
    rows = ctx.find("parking_licenses", parking_license_id=parking_license_id)
    lic = rows[0] if rows else {}
    amount = round(float(payment_amount), 2)
    rid = ctx.make_id("ppy_", parking_license_id, payment_amount, payment_method)
    confirmation = ctx.make_id("PKP-", parking_license_id, payment_amount, payment_method, ctx.now())
    today = ctx.now()[:10]
    ctx.create("parking_charges", rid, parking_charge_id=rid, parking_license_id=parking_license_id,
               customer_id=lic.get("customer_id", ""), event_type="parking_payment", charge_code="payment_received",
               billing_period=today[:7], charge_date=today, amount=amount, energy_kwh=0,
               rate_period="not_applicable", idle_minutes=0, session_reference="", proration_days=0,
               days_in_period=0, source_parking_charge_id="", source_activity_id="",
               payment_method=payment_method, payment_reference=confirmation)
    balance = round(float(lic.get("balance_due") or 0) - amount, 2)
    ctx.update("parking_licenses", parking_license_id, balance_due=balance)
    return str({"payment_id": rid, "parking_license_id": parking_license_id, "payment_amount": amount,
                "payment_method": payment_method, "confirmation_number": confirmation, "received_on": today,
                "resulting_parking_balance": balance})


@tool(owner="agent", rw="write")
def restore_parking_privileges_f55d0d0b(ctx: ToolContext, parking_license_id: str, reinstatement_fee: float) -> str:
    """Restore the suspended parking privileges of a parking license and bill the reinstatement fee with it.

    The resident services agent uses this to lift a parking suspension: the license goes back to active status, so
    the space, gate remotes and charger work again, and one reinstatement fee line for exactly the amount given is
    billed on the license's parking ledger today and added to the outstanding parking balance. The call is complete
    when the receipt below comes back showing the active status and the fee line's reference number.

    Args:
        parking_license_id: Id class — the reference number of the suspended parking license being restored, as
            returned by the parking license lookup.
        reinstatement_fee: Fixed-format class — the reinstatement fee billed with the restoration, in USD, a
            positive amount written with 2 decimal places (cents); any further digits are rounded half up to the
            cent.

    Returns:
        A dictionary receipt: parking_license_id (text, the license restored), status (text, active for restored privileges), fee_line_id (text, the reference number of the reinstatement fee line), reinstatement_fee
        (number, USD with 2 decimal places, the fee billed), posted_on (text, YYYY-MM-DD, today's posting date) and
        resulting_parking_balance (number, USD with 2 decimal places, the license's outstanding parking balance
        including this fee). A receipt with status active means privileges are restored.
    """
    rows = ctx.find("parking_licenses", parking_license_id=parking_license_id)
    lic = rows[0] if rows else {}
    fee = round(float(reinstatement_fee), 2)
    fee_line_id = ctx.make_id("prf_", parking_license_id, reinstatement_fee)
    today = ctx.now()[:10]
    ctx.update("parking_licenses", parking_license_id, status="active")
    ctx.create("parking_charges", fee_line_id, parking_charge_id=fee_line_id, parking_license_id=parking_license_id,
               customer_id=lic.get("customer_id", ""), event_type="parking_fee_charge", charge_code="reinstatement_fee",
               billing_period=today[:7], charge_date=today, amount=fee, energy_kwh=0,
               rate_period="not_applicable", idle_minutes=0, session_reference="", proration_days=0,
               days_in_period=0, source_parking_charge_id="", source_activity_id="",
               payment_method="not_applicable", payment_reference="")
    balance = round(float(lic.get("balance_due") or 0) + fee, 2)
    ctx.update("parking_licenses", parking_license_id, balance_due=balance)
    return str({"parking_license_id": parking_license_id, "status": "active", "fee_line_id": fee_line_id,
                "reinstatement_fee": fee, "posted_on": today, "resulting_parking_balance": balance})

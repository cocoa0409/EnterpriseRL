"""Hidden task tools for the rental_property_renewals_and_cancellations difficulty
(Bridgewell Rental Property Service Contracts: renewals, upgrades, billing and cancellations).

Each tool performs one atomic write on the landlord's own rental contract records with the
values passed in; it judges no eligibility and computes no amount.
"""

from erlbench import ToolContext, tool


class _CalendarDays:
    """Pure calendar arithmetic on 'YYYY-MM-DD' strings (proleptic Gregorian day numbers)."""

    @staticmethod
    def to_number(stamp: str) -> int:
        y, m, d = (int(p) for p in str(stamp)[:10].split("-"))
        a = (14 - m) // 12
        yy = y + 4800 - a
        mm = m + 12 * a - 3
        return d + (153 * mm + 2) // 5 + 365 * yy + yy // 4 - yy // 100 + yy // 400 - 32045

    @staticmethod
    def from_number(n: int) -> str:
        a = n + 32044
        b = (4 * a + 3) // 146097
        c = a - 146097 * b // 4
        d = (4 * c + 3) // 1461
        e = c - 1461 * d // 4
        m = (5 * e + 2) // 153
        day = e - (153 * m + 2) // 5 + 1
        month = m + 3 - 12 * (m // 10)
        year = 100 * b + d - 4800 + m // 10
        return f"{year:04d}-{month:02d}-{day:02d}"

    @staticmethod
    def year_term_end(start: str) -> str:
        y, m, d = (int(p) for p in str(start)[:10].split("-"))
        if m == 2 and d == 29:
            d = 28
        anniversary = f"{y + 1:04d}-{m:02d}-{d:02d}"
        return _CalendarDays.from_number(_CalendarDays.to_number(anniversary) - 1)

    @staticmethod
    def month_period_end(start: str) -> str:
        y, m, d = (int(p) for p in str(start)[:10].split("-"))
        ny, nm = (y + 1, 1) if m == 12 else (y, m + 1)
        last = _CalendarDays.to_number(f"{ny + (nm == 12):04d}-{(nm % 12) + 1:02d}-01") - _CalendarDays.to_number(f"{ny:04d}-{nm:02d}-01")
        nd = min(d, last)
        return _CalendarDays.from_number(_CalendarDays.to_number(f"{ny:04d}-{nm:02d}-{nd:02d}") - 1)


@tool(owner="agent", rw="write")
def bill_upgrade_catchup_f812c6ed(ctx: ToolContext, landlord_contract_id: str, catchup_amount: float,
                                  portfolio_discount_rate: float) -> str:
    """Bill the catch-up charge for a tier upgrade on a rental property service contract whose upgrade
    charge was never billed. One call adds one upgrade proration charge to the contract's billing
    history, dated today, covering the period from the recorded plan change date to the end date of
    the term shown on the contract, and raises the contract's premium balance by the amount billed.
    The landlord sees the new charge on the contract's billing history and a higher balance owed.

    Args:
        landlord_contract_id: Id class — the rental property service contract number of the contract
            being billed, as returned by the rental contract lookup for the landlord.
        catchup_amount: Fixed-format class — the catch-up charge in USD, a positive amount with 2 decimal
            places; the value is stored rounded to 2 decimal places.
        portfolio_discount_rate: Fixed-format class — the portfolio discount rate the charge records, a
            decimal fraction with 2 decimal places (for example 0.05 for five percent); 0.00 when none.

    Returns:
        A dictionary rendered as text with: status ("billed" on success); billing_entry_id (text, the new
        billing entry reference); landlord_contract_id (text); charge_type ("upgrade_proration");
        amount (number, USD with 2 decimal places); billing_period_start and billing_period_end
        (YYYY-MM-DD); premium_balance (number, USD with 2 decimal places, the balance owed once the
        charge is added).
    """
    rows = ctx.find("landlord_contracts", landlord_contract_id=landlord_contract_id)
    contract = rows[0] if rows else {}
    amount = round(float(catchup_amount), 2)
    rate = round(float(portfolio_discount_rate), 2)
    rid = ctx.make_id("lbe_", landlord_contract_id, amount, rate, "upgrade_catchup")
    period_start = contract.get("last_plan_change_date") or ""
    period_end = contract.get("term_end_date") or ""
    ctx.create("landlord_billing_entries", rid, landlord_billing_entry_id=rid,
               landlord_contract_id=landlord_contract_id, customer_id=contract.get("customer_id", ""),
               event_type="landlord_premium_charge", entry_date=ctx.now()[:10], amount=amount,
               charge_type="upgrade_proration", billing_period_start=period_start,
               billing_period_end=period_end, portfolio_discount_rate=rate)
    balance = round(float(contract.get("premium_balance") or 0) + amount, 2)
    ctx.update("landlord_contracts", landlord_contract_id, premium_balance=balance)
    return str({"status": "billed", "billing_entry_id": rid, "landlord_contract_id": landlord_contract_id,
                "charge_type": "upgrade_proration", "amount": amount,
                "billing_period_start": period_start, "billing_period_end": period_end,
                "premium_balance": balance})


@tool(owner="agent", rw="write")
def record_late_renewal_5b858282(ctx: ToolContext, landlord_contract_id: str, renewal_premium: float,
                                 portfolio_discount_rate: float) -> str:
    """Renew an expired rental property service contract late, within its grace period. One call sets
    the contract back to active for a new full term that starts today and ends the day ahead of the same
    calendar date next year, raises the term number by one, clears the contract's end date and its
    renewal notice date, bills the new term's annual premium as one annual premium charge dated today,
    and raises the premium balance by that premium. The landlord sees the contract active again with
    the new term dates and the annual premium on the billing history.

    Args:
        landlord_contract_id: Id class — the rental property service contract number of the expired
            contract, as returned by the rental contract lookup for the landlord.
        renewal_premium: Fixed-format class — the annual premium for the new term in USD, a positive
            amount with 2 decimal places; the value is stored rounded to 2 decimal places.
        portfolio_discount_rate: Fixed-format class — the portfolio discount rate the annual premium
            charge records, a decimal fraction with 2 decimal places (for example 0.05); 0.00 when none.

    Returns:
        A dictionary rendered as text with: status ("renewed" on success); landlord_contract_id (text);
        contract_status ("active"); term_start_date and term_end_date (YYYY-MM-DD, the new term);
        term_number (integer); billing_entry_id (text, the annual premium charge reference);
        annual_premium (number, USD with 2 decimal places); premium_balance (number, USD with 2
        decimal places, the balance owed once the premium is billed).
    """
    rows = ctx.find("landlord_contracts", landlord_contract_id=landlord_contract_id)
    contract = rows[0] if rows else {}
    amount = round(float(renewal_premium), 2)
    rate = round(float(portfolio_discount_rate), 2)
    today = ctx.now()[:10]
    term_end = _CalendarDays.year_term_end(today)
    term_number = int(contract.get("term_number") or 0) + 1
    balance = round(float(contract.get("premium_balance") or 0) + amount, 2)
    ctx.update("landlord_contracts", landlord_contract_id, status="active", term_start_date=today,
               term_end_date=term_end, term_number=term_number, end_date="", renewal_notice_date="",
               premium_balance=balance)
    rid = ctx.make_id("lbe_", landlord_contract_id, amount, rate, today, "late_renewal")
    ctx.create("landlord_billing_entries", rid, landlord_billing_entry_id=rid,
               landlord_contract_id=landlord_contract_id, customer_id=contract.get("customer_id", ""),
               event_type="landlord_premium_charge", entry_date=today, amount=amount,
               charge_type="annual_premium", billing_period_start=today, billing_period_end=term_end,
               portfolio_discount_rate=rate)
    return str({"status": "renewed", "landlord_contract_id": landlord_contract_id, "contract_status": "active",
                "term_start_date": today, "term_end_date": term_end, "term_number": term_number,
                "billing_entry_id": rid, "annual_premium": amount, "premium_balance": balance})


@tool(owner="agent", rw="write")
def bill_returned_payment_fee_d229d74e(ctx: ToolContext, landlord_contract_id: str, payment_reference: str,
                                       fee_amount: float) -> str:
    """Bill the returned-payment fee for a premium payment that was returned unpaid on a rental property
    service contract. One call adds one returned-payment fee charge to the contract's billing history,
    dated today and naming the returned payment, and raises the contract's premium balance by the fee.
    The landlord sees the fee on the billing history next to the returned payment and a higher balance.

    Args:
        landlord_contract_id: Id class — the rental property service contract number the returned payment
            belongs to, as returned by the rental contract lookup for the landlord.
        payment_reference: Id class — the payment confirmation number of the returned payment, as shown on
            the returned payment charge in the contract's billing history.
        fee_amount: Fixed-format class — the returned-payment fee in USD, a positive amount with 2 decimal
            places; the value is stored rounded to 2 decimal places.

    Returns:
        A dictionary rendered as text with: status ("billed" on success); billing_entry_id (text, the new
        fee charge reference); landlord_contract_id (text); charge_type ("returned_payment_fee");
        payment_reference (text, the returned payment named); amount (number, USD with 2 decimal
        places); premium_balance (number, USD with 2 decimal places, the balance owed once the fee is
        added).
    """
    rows = ctx.find("landlord_contracts", landlord_contract_id=landlord_contract_id)
    contract = rows[0] if rows else {}
    amount = round(float(fee_amount), 2)
    rid = ctx.make_id("lbe_", landlord_contract_id, payment_reference, amount, "returned_fee")
    ctx.create("landlord_billing_entries", rid, landlord_billing_entry_id=rid,
               landlord_contract_id=landlord_contract_id, customer_id=contract.get("customer_id", ""),
               event_type="landlord_premium_charge", entry_date=ctx.now()[:10], amount=amount,
               charge_type="returned_payment_fee", payment_reference=payment_reference,
               portfolio_discount_rate=0.0)
    balance = round(float(contract.get("premium_balance") or 0) + amount, 2)
    ctx.update("landlord_contracts", landlord_contract_id, premium_balance=balance)
    return str({"status": "billed", "billing_entry_id": rid, "landlord_contract_id": landlord_contract_id,
                "charge_type": "returned_payment_fee", "payment_reference": payment_reference,
                "amount": amount, "premium_balance": balance})


@tool(owner="user", rw="write")
def accept_plus_upgrade_7955ec7e(ctx: ToolContext, landlord_contract_id: str, new_variant_name: str,
                                 upgrade_charge: float, portfolio_discount_rate: float) -> str:
    """The landlord accepts moving their own rental property service contract up to a higher tier at the
    stated upgrade charge. One call changes the contract's tier to the tier named, keeps the tier it
    replaces as the prior tier, records today as the plan change date, bills the accepted charge as one
    upgrade proration charge covering today through the term end date, and raises the premium balance by
    that charge. The landlord sees the new tier on the contract and the charge on the billing history.

    Args:
        landlord_contract_id: Id class — the rental property service contract number of the landlord's
            contract, as the agent reads it out from the rental contract lookup.
        new_variant_name: Enum class — the tier the contract moves to, exactly one of:
            Bridgewell Rental Appliance (the appliance-only single-unit tier);
            Bridgewell Rental Systems (the systems-only single-unit tier);
            Bridgewell Rental Combo (the single-unit tier covering systems and the kitchen appliance);
            Bridgewell Rental Combo Plus (the top single-unit tier with laundry, garage door opener and higher limits);
            Bridgewell Rental Multi-Unit Combo (the systems and kitchen tier for a two- to four-unit building);
            Bridgewell Rental Multi-Unit Combo Plus (the top tier for a two- to four-unit building).
        upgrade_charge: Fixed-format class — the upgrade charge the landlord accepts, in USD, a positive
            amount with 2 decimal places; the value is stored rounded to 2 decimal places.
        portfolio_discount_rate: Fixed-format class — the portfolio discount rate the upgrade charge
            records, a decimal fraction with 2 decimal places (for example 0.05); 0.00 when none.

    Returns:
        A dictionary rendered as text with: status ("upgraded" on success); landlord_contract_id (text);
        variant_name (text, the tier now held); prior_variant_name (text, the tier replaced);
        last_plan_change_date (YYYY-MM-DD); billing_entry_id (text, the upgrade charge reference);
        upgrade_charge (number, USD with 2 decimal places); premium_balance (number, USD with 2 decimal
        places, the balance owed once the charge is added).
    """
    rows = ctx.find("landlord_contracts", landlord_contract_id=landlord_contract_id)
    contract = rows[0] if rows else {}
    amount = round(float(upgrade_charge), 2)
    rate = round(float(portfolio_discount_rate), 2)
    today = ctx.now()[:10]
    prior = contract.get("variant_name") or "none"
    balance = round(float(contract.get("premium_balance") or 0) + amount, 2)
    ctx.update("landlord_contracts", landlord_contract_id, variant_name=new_variant_name,
               prior_variant_name=prior, last_plan_change_date=today, premium_balance=balance)
    rid = ctx.make_id("lbe_", landlord_contract_id, new_variant_name, amount, rate, today)
    ctx.create("landlord_billing_entries", rid, landlord_billing_entry_id=rid,
               landlord_contract_id=landlord_contract_id, customer_id=contract.get("customer_id", ""),
               event_type="landlord_premium_charge", entry_date=today, amount=amount,
               charge_type="upgrade_proration", billing_period_start=today,
               billing_period_end=contract.get("term_end_date") or "", portfolio_discount_rate=rate)
    return str({"status": "upgraded", "landlord_contract_id": landlord_contract_id,
                "variant_name": new_variant_name, "prior_variant_name": prior,
                "last_plan_change_date": today, "billing_entry_id": rid, "upgrade_charge": amount,
                "premium_balance": balance})


@tool(owner="agent", rw="write")
def post_rerating_correction_12887c54(ctx: ToolContext, landlord_contract_id: str, billing_period_start: str,
                                      correction_amount: float) -> str:
    """Post a billing-correction credit on a rental property service contract for monthly installments
    that were billed at the wrong portfolio discount rate. One call adds one premium credit with the
    reason billing_correction to the contract's billing history, dated today and naming the earliest
    billing period it corrects, and lowers the contract's premium balance by the credit. The landlord sees
    the correction credit on the billing history and a lower balance owed (or a credit balance).

    Args:
        landlord_contract_id: Id class — the rental property service contract number of the contract being
            corrected, as returned by the rental contract lookup for the landlord.
        billing_period_start: Fixed-format class — the start date of the earliest billing period the credit
            corrects, as YYYY-MM-DD, copied from that installment's billing period start in the billing history.
        correction_amount: Fixed-format class — the correction credit in USD, a positive amount with 2 decimal
            places; the value is stored rounded to 2 decimal places.

    Returns:
        A dictionary rendered as text with: status ("credited" on success); billing_entry_id (text, the new
        credit reference); landlord_contract_id (text); credit_reason ("billing_correction");
        billing_period_start (YYYY-MM-DD); amount (number, USD with 2 decimal places); premium_balance
        (number, USD with 2 decimal places, the balance once the credit is applied; negative means a credit
        owed to the landlord).
    """
    rows = ctx.find("landlord_contracts", landlord_contract_id=landlord_contract_id)
    contract = rows[0] if rows else {}
    amount = round(float(correction_amount), 2)
    rid = ctx.make_id("lbe_", landlord_contract_id, billing_period_start, amount, "billing_correction")
    ctx.create("landlord_billing_entries", rid, landlord_billing_entry_id=rid,
               landlord_contract_id=landlord_contract_id, customer_id=contract.get("customer_id", ""),
               event_type="landlord_premium_credit", entry_date=ctx.now()[:10], amount=amount,
               credit_reason="billing_correction", billing_period_start=billing_period_start)
    balance = round(float(contract.get("premium_balance") or 0) - amount, 2)
    ctx.update("landlord_contracts", landlord_contract_id, premium_balance=balance)
    return str({"status": "credited", "billing_entry_id": rid, "landlord_contract_id": landlord_contract_id,
                "credit_reason": "billing_correction", "billing_period_start": billing_period_start,
                "amount": amount, "premium_balance": balance})


@tool(owner="agent", rw="write")
def bill_period_installment_43ec6687(ctx: ToolContext, landlord_contract_id: str, billing_period_start: str,
                                     installment_amount: float, portfolio_discount_rate: float) -> str:
    """Bill the monthly installment for one billing period of a monthly-billed rental property service
    contract. One call adds one monthly installment charge to the contract's billing history, dated today,
    covering the billing period that starts on the date given and ends the day ahead of the same calendar
    day in the following month, and raises the contract's premium balance by the installment. The landlord
    sees the installment on the billing history and a higher balance owed.

    Args:
        landlord_contract_id: Id class — the rental property service contract number of the contract being
            billed, as returned by the rental contract lookup for the landlord.
        billing_period_start: Fixed-format class — the start date (due date) of the billing period billed, as
            YYYY-MM-DD; periods start on the same calendar day of the month as the contract's term start.
        installment_amount: Fixed-format class — the installment in USD, a positive amount with 2 decimal
            places; the value is stored rounded to 2 decimal places.
        portfolio_discount_rate: Fixed-format class — the portfolio discount rate the installment records, a
            decimal fraction with 2 decimal places (for example 0.05); 0.00 when none.

    Returns:
        A dictionary rendered as text with: status ("billed" on success); billing_entry_id (text, the new
        installment reference); landlord_contract_id (text); charge_type ("monthly_installment");
        billing_period_start and billing_period_end (YYYY-MM-DD); amount (number, USD with 2 decimal
        places); premium_balance (number, USD with 2 decimal places, the balance owed once the installment
        is added).
    """
    rows = ctx.find("landlord_contracts", landlord_contract_id=landlord_contract_id)
    contract = rows[0] if rows else {}
    amount = round(float(installment_amount), 2)
    rate = round(float(portfolio_discount_rate), 2)
    period_end = _CalendarDays.month_period_end(billing_period_start)
    rid = ctx.make_id("lbe_", landlord_contract_id, billing_period_start, amount, rate, "installment")
    ctx.create("landlord_billing_entries", rid, landlord_billing_entry_id=rid,
               landlord_contract_id=landlord_contract_id, customer_id=contract.get("customer_id", ""),
               event_type="landlord_premium_charge", entry_date=ctx.now()[:10], amount=amount,
               charge_type="monthly_installment", billing_period_start=billing_period_start,
               billing_period_end=period_end, portfolio_discount_rate=rate)
    balance = round(float(contract.get("premium_balance") or 0) + amount, 2)
    ctx.update("landlord_contracts", landlord_contract_id, premium_balance=balance)
    return str({"status": "billed", "billing_entry_id": rid, "landlord_contract_id": landlord_contract_id,
                "charge_type": "monthly_installment", "billing_period_start": billing_period_start,
                "billing_period_end": period_end, "amount": amount, "premium_balance": balance})


@tool(owner="agent", rw="write")
def bill_upgrade_difference_aa78d3be(ctx: ToolContext, landlord_contract_id: str, difference_amount: float,
                                     portfolio_discount_rate: float, billing_period_end: str) -> str:
    """Bill the upgrade difference for the rest of the billing period in which a monthly-billed rental
    property service contract was moved to a higher tier. One call adds one upgrade proration charge to the
    contract's billing history, dated today, covering the recorded plan change date through the period end
    date given, and raises the contract's premium balance by the charge. The landlord sees the charge on
    the billing history and a higher balance owed.

    Args:
        landlord_contract_id: Id class — the rental property service contract number of the upgraded
            contract, as returned by the rental contract lookup for the landlord.
        difference_amount: Fixed-format class — the upgrade difference charge in USD, a positive amount with 2
            decimal places; the value is stored rounded to 2 decimal places.
        portfolio_discount_rate: Fixed-format class — the portfolio discount rate the charge records, a decimal
            fraction with 2 decimal places (for example 0.05); 0.00 when none.
        billing_period_end: Fixed-format class — the last day of the billing period in which the tier changed,
            as YYYY-MM-DD, copied from that period's installment in the billing history.

    Returns:
        A dictionary rendered as text with: status ("billed" on success); billing_entry_id (text, the new
        charge reference); landlord_contract_id (text); charge_type ("upgrade_proration");
        billing_period_start and billing_period_end (YYYY-MM-DD); amount (number, USD with 2 decimal
        places); premium_balance (number, USD with 2 decimal places, the balance owed once the charge is
        added).
    """
    rows = ctx.find("landlord_contracts", landlord_contract_id=landlord_contract_id)
    contract = rows[0] if rows else {}
    amount = round(float(difference_amount), 2)
    rate = round(float(portfolio_discount_rate), 2)
    period_start = contract.get("last_plan_change_date") or ""
    rid = ctx.make_id("lbe_", landlord_contract_id, amount, rate, billing_period_end, "upgrade_difference")
    ctx.create("landlord_billing_entries", rid, landlord_billing_entry_id=rid,
               landlord_contract_id=landlord_contract_id, customer_id=contract.get("customer_id", ""),
               event_type="landlord_premium_charge", entry_date=ctx.now()[:10], amount=amount,
               charge_type="upgrade_proration", billing_period_start=period_start,
               billing_period_end=billing_period_end, portfolio_discount_rate=rate)
    balance = round(float(contract.get("premium_balance") or 0) + amount, 2)
    ctx.update("landlord_contracts", landlord_contract_id, premium_balance=balance)
    return str({"status": "billed", "billing_entry_id": rid, "landlord_contract_id": landlord_contract_id,
                "charge_type": "upgrade_proration", "billing_period_start": period_start,
                "billing_period_end": billing_period_end, "amount": amount, "premium_balance": balance})


@tool(owner="user", rw="write")
def confirm_sale_cancellation_d8f9046f(ctx: ToolContext, landlord_contract_id: str,
                                       landlord_cancellation_request_id: str, cancellation_credit: float) -> str:
    """The landlord confirms the cancellation request on file for their own rental property service contract
    and accepts the cancellation credit stated. One call marks the cancellation request confirmed, sets the
    contract to cancelled with its end date equal to the notice date on the request, posts the credit as one
    cancellation credit naming the request, and lowers the contract's premium balance by the credit. The
    landlord sees the contract cancelled and the credit on the billing history.

    Args:
        landlord_contract_id: Id class — the rental property service contract number of the contract being
            cancelled, as the agent reads it out from the rental contract lookup.
        landlord_cancellation_request_id: Id class — the reference number of the cancellation request on file
            for that contract, as the agent reads it out from the cancellation request lookup.
        cancellation_credit: Fixed-format class — the cancellation credit in USD with 2 decimal places, zero or
            positive; the value is stored rounded to 2 decimal places.

    Returns:
        A dictionary rendered as text with: status ("cancelled" on success); landlord_contract_id (text);
        landlord_cancellation_request_id (text); request_status ("confirmed"); contract_status
        ("cancelled"); end_date (YYYY-MM-DD, the notice date); billing_entry_id (text, the credit
        reference); cancellation_credit (number, USD with 2 decimal places); premium_balance (number, USD
        with 2 decimal places, the balance once the credit is applied; negative means a credit owed back).
    """
    rows = ctx.find("landlord_contracts", landlord_contract_id=landlord_contract_id)
    contract = rows[0] if rows else {}
    reqs = ctx.find("landlord_cancellation_requests", landlord_cancellation_request_id=landlord_cancellation_request_id)
    request = reqs[0] if reqs else {}
    amount = round(float(cancellation_credit), 2)
    end_date = request.get("notice_date") or ctx.now()[:10]
    ctx.update("landlord_cancellation_requests", landlord_cancellation_request_id, request_status="confirmed")
    balance = round(float(contract.get("premium_balance") or 0) - amount, 2)
    ctx.update("landlord_contracts", landlord_contract_id, status="cancelled", end_date=end_date,
               premium_balance=balance)
    rid = ctx.make_id("lbe_", landlord_contract_id, landlord_cancellation_request_id, amount, "cancellation_credit")
    ctx.create("landlord_billing_entries", rid, landlord_billing_entry_id=rid,
               landlord_contract_id=landlord_contract_id, customer_id=contract.get("customer_id", ""),
               event_type="landlord_premium_credit", entry_date=ctx.now()[:10], amount=amount,
               credit_reason="cancellation_refund_credit",
               landlord_cancellation_request_id=landlord_cancellation_request_id)
    return str({"status": "cancelled", "landlord_contract_id": landlord_contract_id,
                "landlord_cancellation_request_id": landlord_cancellation_request_id,
                "request_status": "confirmed", "contract_status": "cancelled", "end_date": end_date,
                "billing_entry_id": rid, "cancellation_credit": amount, "premium_balance": balance})

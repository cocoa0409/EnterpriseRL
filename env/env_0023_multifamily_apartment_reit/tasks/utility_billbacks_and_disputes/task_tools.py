"""Hidden task tools of the utility_billbacks_and_disputes difficulty (Larkspur Residential Trust).

Each tool performs exactly one atomic write on a utility services account and computes nothing on the
agent's behalf: every amount, usage figure and period it receives has already been worked out by the
agent from the published utility charter and the account's records. No tool checks an eligibility,
a status, a deadline or any other policy condition, and none refuses a call because such a condition
is unmet; those judgements belong to the agent.
"""

from erlbench import ToolContext, tool


@tool(owner="agent", rw="write")
def post_gas_trueup_line_465c860d(ctx: ToolContext, utility_account_id: str, billing_period: str,
                                  usage_quantity: float, amount: float) -> str:
    """Post the gas true-up usage line of one billing period on a resident's utility services account.

    The resident services agent uses this to issue, on the account, the gas usage line of the service
    month whose actual gas read followed estimated gas reads. One call records one new gas usage line,
    marked as resting on an actual read, dated today, carrying the therms billed and the amount billed,
    and raises the account's outstanding utility balance by that amount. Afterwards the line appears
    among the account's bill lines and the higher utility balance is visible on the account. A receipt
    naming the new line is returned when the line has been posted.

    Args:
        utility_account_id: Id class — the reference number of the resident's utility services account
            the line is posted on, as returned by the utility account lookup.
        billing_period: Fixed-format class — the service month the gas line bills, written YYYY-MM
            (for example the month closed by the actual gas read).
        usage_quantity: Fixed-format class — the gas usage the line bills, in therms, written as a
            decimal with up to 3 places, in usage_unit (therm); recorded rounded to 3 decimal places.
        amount: Fixed-format class — the amount the line bills, in USD, 2 decimal places, rounded half
            up to the cent; always zero or positive.

    Returns:
        A dictionary rendered as text with these keys: status (the string "posted" when the line was
        recorded), bill_id (the reference number of the new gas usage line), billing_period (the service
        month billed, YYYY-MM), usage_quantity (the therms billed, 3 decimal places), amount (the amount
        billed, USD with 2 decimal places) and balance_due (the account's outstanding utility balance
        after the line, USD with 2 decimal places).
    """
    acct_rows = ctx.find("utility_accounts", utility_account_id=utility_account_id)
    acct = acct_rows[0] if acct_rows else {}
    rid = ctx.make_id("ubl_", utility_account_id, billing_period, usage_quantity, amount)
    amt = round(float(amount), 2)
    ctx.create("utility_bills", rid, bill_id=rid, utility_account_id=utility_account_id,
               customer_id=acct.get("customer_id"), event_type="utility_usage_billback",
               service_type="gas", billing_period=billing_period, bill_date=ctx.now()[:10],
               amount=amt, usage_quantity=round(float(usage_quantity), 3), usage_unit="therm",
               read_type="actual", allocation_factor=0.0, property_bill_amount=0.0,
               proration_days=0, days_in_period=0, source_bill_id=None,
               adjustment_reason="not_applicable", payment_method="not_applicable",
               payment_reference=None)
    balance = round(float(acct.get("balance_due") or 0) + amt, 2)
    ctx.update("utility_accounts", utility_account_id, balance_due=balance)
    return str({"status": "posted", "bill_id": rid, "billing_period": billing_period,
                "usage_quantity": round(float(usage_quantity), 3), "amount": amt,
                "balance_due": balance})


@tool(owner="agent", rw="write")
def bill_estimated_electric_line_1c085b40(ctx: ToolContext, utility_account_id: str, billing_period: str,
                                          usage_quantity: float, amount: float) -> str:
    """Bill the estimated electricity usage line of one billing period on a resident's utility services account.

    The resident services agent uses this to issue, on the account, the electricity usage line of a
    service month for which no electricity read was obtained. One call records one new electricity
    usage line, marked as resting on an estimated read, dated today, carrying the kilowatt-hours billed
    and the amount billed, and raises the account's outstanding utility balance by that amount.
    Afterwards the estimated line appears among the account's bill lines and the higher utility balance
    is visible on the account. A receipt naming the new line is returned when the line has been billed.

    Args:
        utility_account_id: Id class — the reference number of the resident's utility services account
            the line is billed on, as returned by the utility account lookup.
        billing_period: Fixed-format class — the service month the electricity line bills, written
            YYYY-MM.
        usage_quantity: Fixed-format class — the estimated electricity usage the line bills, in
            kilowatt-hours, written as a decimal with up to 3 places, in usage_unit (kwh); recorded
            rounded to 3 decimal places.
        amount: Fixed-format class — the amount the line bills, in USD, 2 decimal places, rounded half
            up to the cent; always zero or positive.

    Returns:
        A dictionary rendered as text with these keys: status (the string "billed" when the line was
        recorded), bill_id (the reference number of the new electricity usage line), billing_period (the
        service month billed, YYYY-MM), usage_quantity (the kilowatt-hours billed, 3 decimal places),
        amount (the amount billed, USD with 2 decimal places) and balance_due (the account's outstanding
        utility balance after the line, USD with 2 decimal places).
    """
    acct_rows = ctx.find("utility_accounts", utility_account_id=utility_account_id)
    acct = acct_rows[0] if acct_rows else {}
    rid = ctx.make_id("ubl_", utility_account_id, billing_period, usage_quantity, amount)
    amt = round(float(amount), 2)
    ctx.create("utility_bills", rid, bill_id=rid, utility_account_id=utility_account_id,
               customer_id=acct.get("customer_id"), event_type="utility_usage_billback",
               service_type="electric", billing_period=billing_period, bill_date=ctx.now()[:10],
               amount=amt, usage_quantity=round(float(usage_quantity), 3), usage_unit="kwh",
               read_type="estimated", allocation_factor=0.0, property_bill_amount=0.0,
               proration_days=0, days_in_period=0, source_bill_id=None,
               adjustment_reason="not_applicable", payment_method="not_applicable",
               payment_reference=None)
    balance = round(float(acct.get("balance_due") or 0) + amt, 2)
    ctx.update("utility_accounts", utility_account_id, balance_due=balance)
    return str({"status": "billed", "bill_id": rid, "billing_period": billing_period,
                "usage_quantity": round(float(usage_quantity), 3), "amount": amt,
                "balance_due": balance})


@tool(owner="user", rw="write")
def pay_undisputed_utility_balance_990e05bb(ctx: ToolContext, utility_account_id: str, amount: float,
                                            payment_method: str) -> str:
    """Make a payment of the undisputed utility balance on your own utility services account.

    The resident uses this to pay, with an instrument of their own, an amount toward the outstanding
    balance of their utility services account while a charge on it is under dispute. One call records
    one payment received today for the amount given and lowers the account's outstanding utility
    balance by that amount; the payment is issued a confirmation number. Afterwards the payment appears
    among the account's lines and the lower utility balance is visible on the account. A receipt with
    the confirmation number is returned when the payment has been received.

    Args:
        utility_account_id: Id class — the reference number of your utility services account, as the
            resident services agent reads it to you from the utility account lookup.
        amount: Fixed-format class — the amount you pay, in USD, 2 decimal places, rounded half up to
            the cent; always positive.
        payment_method: Enum class — the instrument you pay with, exactly one of: ach_one_time — a
            one-time bank transfer from your checking or savings account; debit_card — a payment with
            your debit card; credit_card — a payment with your credit card; money_order — a money order
            you hand in or mail with its serial number; cashiers_check — a cashier's check you hand in
            or mail with its serial number; ach_autopay — reserved for the recurring automatic bank
            draft and never used for a payment you make here; deposit_application — reserved for
            applying the security deposit at final accounting and never used for a payment you make
            here; not_applicable — marks lines that are not payments and is never used for a payment.

    Returns:
        A dictionary rendered as text with these keys: status (the string "received" when the payment
        was recorded), bill_id (the reference number of the payment line), payment_reference (the
        confirmation number issued for the payment), amount (the amount received, USD with 2 decimal
        places), payment_method (the instrument recorded) and balance_due (the account's outstanding
        utility balance after the payment, USD with 2 decimal places).
    """
    acct_rows = ctx.find("utility_accounts", utility_account_id=utility_account_id)
    acct = acct_rows[0] if acct_rows else {}
    rid = ctx.make_id("ubl_", utility_account_id, amount, payment_method)
    ref = ctx.make_id("UTP", utility_account_id, amount, payment_method, length=10).upper()
    amt = round(float(amount), 2)
    today = ctx.now()[:10]
    ctx.create("utility_bills", rid, bill_id=rid, utility_account_id=utility_account_id,
               customer_id=acct.get("customer_id"), event_type="utility_payment",
               service_type="not_applicable", billing_period=today[:7], bill_date=today,
               amount=amt, usage_quantity=0.0, usage_unit="not_applicable",
               read_type="not_applicable", allocation_factor=0.0, property_bill_amount=0.0,
               proration_days=0, days_in_period=0, source_bill_id=None,
               adjustment_reason="not_applicable", payment_method=payment_method,
               payment_reference=ref)
    balance = round(float(acct.get("balance_due") or 0) - amt, 2)
    ctx.update("utility_accounts", utility_account_id, balance_due=balance)
    return str({"status": "received", "bill_id": rid, "payment_reference": ref, "amount": amt,
                "payment_method": payment_method, "balance_due": balance})


@tool(owner="agent", rw="write")
def credit_leak_adjustment_a9c6c674(ctx: ToolContext, utility_account_id: str, source_bill_id: str,
                                    credit_amount: float) -> str:
    """Credit a leak adjustment against one disputed water usage line of a resident's utility services account.

    The resident services agent uses this to decide a suspected-leak dispute with a credit. One call
    records one leak adjustment credit dated today against the named bill line, for the service and
    month of that line, lowers the account's outstanding utility balance by the credit, and marks the
    suspected-leak dispute recorded against that line as credited. Afterwards the credit appears among
    the account's lines, linked to the line it credits, the dispute shows as credited and the lower
    utility balance is visible. A receipt naming the credit is returned when it has been posted.

    Args:
        utility_account_id: Id class — the reference number of the resident's utility services account,
            as returned by the utility account lookup.
        source_bill_id: Id class — the reference number of the disputed water usage line being credited,
            as returned by the bill line lookup or named on the dispute record.
        credit_amount: Fixed-format class — the leak adjustment credited, in USD, 2 decimal places,
            rounded half up to the cent; always zero or positive.

    Returns:
        A dictionary rendered as text with these keys: status (the string "credited" when the credit was
        recorded), bill_id (the reference number of the new credit), source_bill_id (the line credited),
        credit_amount (the credit, USD with 2 decimal places), disputes_marked (how many disputes against
        that line were marked credited, an integer) and balance_due (the account's outstanding utility
        balance after the credit, USD with 2 decimal places).
    """
    acct_rows = ctx.find("utility_accounts", utility_account_id=utility_account_id)
    acct = acct_rows[0] if acct_rows else {}
    src_rows = ctx.find("utility_bills", bill_id=source_bill_id)
    src = src_rows[0] if src_rows else {}
    rid = ctx.make_id("ubl_", utility_account_id, source_bill_id, "leak_adjustment", credit_amount)
    amt = round(float(credit_amount), 2)
    ctx.create("utility_bills", rid, bill_id=rid, utility_account_id=utility_account_id,
               customer_id=acct.get("customer_id"), event_type="utility_bill_adjustment",
               service_type=src.get("service_type") or "water",
               billing_period=src.get("billing_period"), bill_date=ctx.now()[:10], amount=amt,
               usage_quantity=0.0, usage_unit="not_applicable", read_type="not_applicable",
               allocation_factor=0.0, property_bill_amount=0.0, proration_days=0, days_in_period=0,
               source_bill_id=source_bill_id, adjustment_reason="leak_adjustment",
               payment_method="not_applicable", payment_reference=None)
    marked = 0
    for d in ctx.find("utility_disputes", bill_id=source_bill_id, dispute_reason="suspected_leak"):
        ctx.update("utility_disputes", d["dispute_id"], dispute_status="credited")
        marked += 1
    balance = round(float(acct.get("balance_due") or 0) - amt, 2)
    ctx.update("utility_accounts", utility_account_id, balance_due=balance)
    return str({"status": "credited", "bill_id": rid, "source_bill_id": source_bill_id,
                "credit_amount": amt, "disputes_marked": marked, "balance_due": balance})


@tool(owner="agent", rw="write")
def post_final_package_fee_c766a545(ctx: ToolContext, utility_account_id: str, billing_period: str,
                                    proration_days: int, days_in_period: int, amount: float) -> str:
    """Post the final package fee line of an All-Inclusive Utility Package account whose billing responsibility has ended.

    The resident services agent uses this to issue, on an account in final billing, the package fee line
    of its final service month. One call records one new package fee line dated today for that month,
    carrying the days charged and the days of the period it was prorated over and the amount billed, and
    raises the account's outstanding utility balance by that amount. Afterwards the line appears among the
    account's bill lines with its proration days and the higher utility balance is visible on the account.
    A receipt naming the new line is returned when the line has been posted.

    Args:
        utility_account_id: Id class — the reference number of the resident's utility services account in
            final billing, as returned by the utility account lookup.
        billing_period: Fixed-format class — the final service month the package fee line bills, written
            YYYY-MM.
        proration_days: Fixed-format class — the days charged on the line, an integer count of days
            recorded as the line's proration days.
        days_in_period: Fixed-format class — the days of the period the fee is prorated over, an integer
            count of days recorded as the line's days in period.
        amount: Fixed-format class — the package fee billed, in USD, 2 decimal places, rounded half up to
            the cent; always zero or positive.

    Returns:
        A dictionary rendered as text with these keys: status (the string "posted" when the line was
        recorded), bill_id (the reference number of the new package fee line), billing_period (the month
        billed, YYYY-MM), proration_days and days_in_period (the integers recorded on the line), amount
        (the fee billed, USD with 2 decimal places) and balance_due (the account's outstanding utility
        balance after the line, USD with 2 decimal places).
    """
    acct_rows = ctx.find("utility_accounts", utility_account_id=utility_account_id)
    acct = acct_rows[0] if acct_rows else {}
    rid = ctx.make_id("ubl_", utility_account_id, billing_period, proration_days, days_in_period, amount)
    amt = round(float(amount), 2)
    ctx.create("utility_bills", rid, bill_id=rid, utility_account_id=utility_account_id,
               customer_id=acct.get("customer_id"), event_type="utility_flat_charge",
               service_type="utility_package", billing_period=billing_period, bill_date=ctx.now()[:10],
               amount=amt, usage_quantity=0.0, usage_unit="not_applicable", read_type="not_applicable",
               allocation_factor=0.0, property_bill_amount=0.0, proration_days=int(proration_days),
               days_in_period=int(days_in_period), source_bill_id=None, adjustment_reason="not_applicable",
               payment_method="not_applicable", payment_reference=None)
    balance = round(float(acct.get("balance_due") or 0) + amt, 2)
    ctx.update("utility_accounts", utility_account_id, balance_due=balance)
    return str({"status": "posted", "bill_id": rid, "billing_period": billing_period,
                "proration_days": int(proration_days), "days_in_period": int(days_in_period),
                "amount": amt, "balance_due": balance})


@tool(owner="agent", rw="write")
def post_final_water_overage_2681eca1(ctx: ToolContext, utility_account_id: str, billing_period: str,
                                      usage_quantity: float, amount: float) -> str:
    """Post the final water overage line of an All-Inclusive Utility Package account whose billing responsibility has ended.

    The resident services agent uses this to issue, on an account in final billing, the water overage
    line of its final service month: the water used above the final water allowance, which also carries
    sewer. One call records one new water overage line dated today, resting on the actual service-end read,
    carrying the thousand gallons billed above the allowance and the amount billed, and raises the
    account's outstanding utility balance by that amount. Afterwards the line appears among the account's
    bill lines and the higher utility balance is visible. A receipt naming the new line is returned.

    Args:
        utility_account_id: Id class — the reference number of the resident's utility services account in
            final billing, as returned by the utility account lookup.
        billing_period: Fixed-format class — the final service month the overage line bills, written
            YYYY-MM.
        usage_quantity: Fixed-format class — the water usage above the final allowance, in thousand
            gallons, written as a decimal with up to 3 places, in usage_unit (kgal); recorded rounded to 3
            decimal places.
        amount: Fixed-format class — the overage charge billed, in USD, 2 decimal places, rounded half up
            to the cent; always zero or positive.

    Returns:
        A dictionary rendered as text with these keys: status (the string "posted" when the line was
        recorded), bill_id (the reference number of the new water overage line), billing_period (the month
        billed, YYYY-MM), usage_quantity (the thousand gallons billed above the allowance, 3 decimal
        places), amount (the charge billed, USD with 2 decimal places) and balance_due (the account's
        outstanding utility balance after the line, USD with 2 decimal places).
    """
    acct_rows = ctx.find("utility_accounts", utility_account_id=utility_account_id)
    acct = acct_rows[0] if acct_rows else {}
    rid = ctx.make_id("ubl_", utility_account_id, billing_period, "water", usage_quantity, amount)
    amt = round(float(amount), 2)
    ctx.create("utility_bills", rid, bill_id=rid, utility_account_id=utility_account_id,
               customer_id=acct.get("customer_id"), event_type="utility_package_overage",
               service_type="water", billing_period=billing_period, bill_date=ctx.now()[:10],
               amount=amt, usage_quantity=round(float(usage_quantity), 3), usage_unit="kgal",
               read_type="actual", allocation_factor=0.0, property_bill_amount=0.0, proration_days=0,
               days_in_period=0, source_bill_id=None, adjustment_reason="not_applicable",
               payment_method="not_applicable", payment_reference=None)
    balance = round(float(acct.get("balance_due") or 0) + amt, 2)
    ctx.update("utility_accounts", utility_account_id, balance_due=balance)
    return str({"status": "posted", "bill_id": rid, "billing_period": billing_period,
                "usage_quantity": round(float(usage_quantity), 3), "amount": amt, "balance_due": balance})


@tool(owner="agent", rw="write")
def post_final_electric_overage_b496acda(ctx: ToolContext, utility_account_id: str, billing_period: str,
                                         usage_quantity: float, amount: float) -> str:
    """Post the final electricity overage line of an All-Inclusive Utility Package account whose billing responsibility has ended.

    The resident services agent uses this to issue, on an account in final billing, the electricity
    overage line of its final service month: the electricity used above the final electricity allowance.
    One call records one new electricity overage line dated today, resting on the actual service-end read,
    carrying the kilowatt-hours billed above the allowance and the amount billed, and raises the account's
    outstanding utility balance by that amount. Afterwards the line appears among the account's bill lines
    and the higher utility balance is visible. A receipt naming the new line is returned.

    Args:
        utility_account_id: Id class — the reference number of the resident's utility services account in
            final billing, as returned by the utility account lookup.
        billing_period: Fixed-format class — the final service month the overage line bills, written
            YYYY-MM.
        usage_quantity: Fixed-format class — the electricity usage above the final allowance, in
            kilowatt-hours, written as a decimal with up to 3 places, in usage_unit (kwh); recorded rounded
            to 3 decimal places.
        amount: Fixed-format class — the overage charge billed, in USD, 2 decimal places, rounded half up
            to the cent; always zero or positive.

    Returns:
        A dictionary rendered as text with these keys: status (the string "posted" when the line was
        recorded), bill_id (the reference number of the new electricity overage line), billing_period (the
        month billed, YYYY-MM), usage_quantity (the kilowatt-hours billed above the allowance, 3 decimal
        places), amount (the charge billed, USD with 2 decimal places) and balance_due (the account's
        outstanding utility balance after the line, USD with 2 decimal places).
    """
    acct_rows = ctx.find("utility_accounts", utility_account_id=utility_account_id)
    acct = acct_rows[0] if acct_rows else {}
    rid = ctx.make_id("ubl_", utility_account_id, billing_period, "electric", usage_quantity, amount)
    amt = round(float(amount), 2)
    ctx.create("utility_bills", rid, bill_id=rid, utility_account_id=utility_account_id,
               customer_id=acct.get("customer_id"), event_type="utility_package_overage",
               service_type="electric", billing_period=billing_period, bill_date=ctx.now()[:10],
               amount=amt, usage_quantity=round(float(usage_quantity), 3), usage_unit="kwh",
               read_type="actual", allocation_factor=0.0, property_bill_amount=0.0, proration_days=0,
               days_in_period=0, source_bill_id=None, adjustment_reason="not_applicable",
               payment_method="not_applicable", payment_reference=None)
    balance = round(float(acct.get("balance_due") or 0) + amt, 2)
    ctx.update("utility_accounts", utility_account_id, balance_due=balance)
    return str({"status": "posted", "bill_id": rid, "billing_period": billing_period,
                "usage_quantity": round(float(usage_quantity), 3), "amount": amt, "balance_due": balance})


@tool(owner="user", rw="write")
def pay_moveout_utility_share_762d5a93(ctx: ToolContext, utility_account_id: str, amount: float,
                                       payment_method: str) -> str:
    """Make your move-out utility payment on the utility services account of the apartment home you have left.

    The former resident uses this to pay, with an instrument of their own, the part of the final utility
    balance of their account in final billing that they settle in person. One call records one payment
    received today for the amount given and lowers the account's outstanding utility balance by that
    amount; the payment is issued a confirmation number. Afterwards the payment appears among the
    account's lines and the lower utility balance is visible on the account. A receipt with the
    confirmation number is returned when the payment has been received.

    Args:
        utility_account_id: Id class — the reference number of your utility services account, as the
            resident services agent reads it to you from the utility account lookup.
        amount: Fixed-format class — the amount you pay, in USD, 2 decimal places, rounded half up to the
            cent; always positive.
        payment_method: Enum class — the instrument you pay with, exactly one of: ach_one_time — a one-time
            bank transfer from your checking or savings account; debit_card — a payment with your debit
            card; credit_card — a payment with your credit card; money_order — a money order you mail with
            its serial number; cashiers_check — a cashier's check you mail with its serial number;
            ach_autopay — reserved for the recurring automatic bank draft and never used for a payment you
            make here; deposit_application — reserved for applying the security deposit at final
            accounting and never used for a payment you make here; not_applicable — marks lines that are
            not payments and is never used for a payment.

    Returns:
        A dictionary rendered as text with these keys: status (the string "received" when the payment was
        recorded), bill_id (the reference number of the payment line), payment_reference (the confirmation
        number issued for the payment), amount (the amount received, USD with 2 decimal places),
        payment_method (the instrument recorded) and balance_due (the account's outstanding utility balance
        after the payment, USD with 2 decimal places).
    """
    acct_rows = ctx.find("utility_accounts", utility_account_id=utility_account_id)
    acct = acct_rows[0] if acct_rows else {}
    rid = ctx.make_id("ubl_", utility_account_id, "moveout", amount, payment_method)
    ref = ctx.make_id("UMO", utility_account_id, amount, payment_method, length=10).upper()
    amt = round(float(amount), 2)
    today = ctx.now()[:10]
    ctx.create("utility_bills", rid, bill_id=rid, utility_account_id=utility_account_id,
               customer_id=acct.get("customer_id"), event_type="utility_payment",
               service_type="not_applicable", billing_period=today[:7], bill_date=today,
               amount=amt, usage_quantity=0.0, usage_unit="not_applicable",
               read_type="not_applicable", allocation_factor=0.0, property_bill_amount=0.0,
               proration_days=0, days_in_period=0, source_bill_id=None,
               adjustment_reason="not_applicable", payment_method=payment_method,
               payment_reference=ref)
    balance = round(float(acct.get("balance_due") or 0) - amt, 2)
    ctx.update("utility_accounts", utility_account_id, balance_due=balance)
    return str({"status": "received", "bill_id": rid, "payment_reference": ref, "amount": amt,
                "payment_method": payment_method, "balance_due": balance})

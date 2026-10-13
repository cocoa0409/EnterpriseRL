"""Hidden task tools for the utility_pass_through_billing difficulty (Hearthstone Communities).

Each tool performs one atomic write on a resident's Utility Pass-Through Service account: it
books exactly the entry described, moves the account's utility balance by that entry, and
returns a receipt. No tool judges eligibility, timing, ordering or amounts; the desk decides
every value from the published utility policies and the account's records before calling.
"""

from erlbench import ToolContext, tool


@tool(owner="agent", rw="write")
def post_estimated_water_read_4835faa0(ctx: ToolContext, utility_account_id: str, billing_period: str,
                                       read_date: str, prior_reading: float, consumption: float) -> str:
    """Record an estimated water submeter reading on a resident's utility account for a read cycle
    whose meter could not be read on the read day.

    The desk enters one estimated water read for the statement month given. The new read starts
    from the prior register reading supplied, carries the estimated consumption supplied, and its
    register reading becomes the prior reading plus that consumption. Recording the read does not
    bill it and does not change the utility balance; the read appears in the account's
    ledger as an estimated water read that a usage charge can bill.

    Args:
        utility_account_id: Id class — reference number of the resident's utility account, as returned by the utility account lookup for this resident.
        billing_period: Fixed-format class — statement month on which the estimated read is billed, written YYYY-MM.
        read_date: Fixed-format class — date of the read day the estimate stands in for, written YYYY-MM-DD.
        prior_reading: Fixed-format class — register reading the estimated consumption is measured from, the latest register reading on the account's water reads, written as a decimal register reading in the meter's unit (thousand gallons, 2 decimal places, as shown in the ledger).
        consumption: Fixed-format class — estimated water consumption for the cycle, written as decimal, 2 places, in consumption_unit (thousand gallons, kgal, 2 decimal places), already rounded half up to the hundredth.

    Returns:
        A receipt text containing a dictionary with: utility_entry_id (reference number of the new
        estimated read, used by a usage charge as the read it bills), billing_period (YYYY-MM),
        entry_date (read day, YYYY-MM-DD), read_type (always "estimated"), prior_reading and
        current_reading (register readings, thousand gallons, 2 decimal places) and consumption
        (kgal, 2 decimal places). A returned utility_entry_id means the read is recorded.
    """
    rid = ctx.make_id("ure_", utility_account_id, billing_period, read_date, prior_reading, consumption)
    acct = ctx.find("utility_accounts", utility_account_id=utility_account_id)
    customer_id = acct[0].get("customer_id") if acct else ""
    prior = round(float(prior_reading), 2)
    cons = round(float(consumption), 2)
    current = round(prior + cons, 2)
    ctx.create("utility_ledger", rid, utility_entry_id=rid, utility_account_id=utility_account_id,
               customer_id=customer_id, event_type="utility_meter_read", billing_period=billing_period,
               entry_date=read_date, utility_service="water", read_type="estimated",
               prior_reading=prior, current_reading=current, consumption=cons, consumption_unit="kgal")
    return str({"utility_entry_id": rid, "billing_period": billing_period, "entry_date": read_date,
                "read_type": "estimated", "prior_reading": prior, "current_reading": current,
                "consumption": cons})


@tool(owner="agent", rw="write")
def post_water_usage_charge_d31cd699(ctx: ToolContext, utility_account_id: str, source_entry_id: str,
                                     amount: float, due_date: str) -> str:
    """Post the regular water usage charge that bills one water read on a resident's utility
    statement.

    The charge is booked against the water read identified, on the statement month and with the
    consumption that read carries, dated today as the statement date and due on the due date
    given. The utility balance rises by the charge amount, and the charge appears in the ledger
    as a regular water usage charge pointing back to the read it bills.

    Args:
        utility_account_id: Id class — reference number of the resident's utility account, as returned by the utility account lookup for this resident.
        source_entry_id: Id class — reference number of the water read this charge bills, taken from the account's ledger or from the receipt that recorded the read.
        amount: Fixed-format class — water usage charge in USD, 2 decimal places, already rounded half up to the cent.
        due_date: Fixed-format class — due date of the statement the charge is billed on, written YYYY-MM-DD, the same due date the statement's other charges carry.

    Returns:
        A receipt text containing a dictionary with: utility_entry_id (reference number of the new
        charge), billing_period (statement month, YYYY-MM), consumption (kgal billed, 2 decimal
        places), amount (USD, 2 decimal places), due_date (YYYY-MM-DD) and utility_balance (the
        account balance after the charge, USD, 2 decimal places). A returned utility_entry_id means
        the charge is posted.
    """
    rid = ctx.make_id("uuc_", utility_account_id, source_entry_id, amount, due_date)
    read = ctx.find("utility_ledger", utility_entry_id=source_entry_id)
    src = read[0] if read else {}
    acct = ctx.find("utility_accounts", utility_account_id=utility_account_id)
    row = acct[0] if acct else {}
    amt = round(float(amount), 2)
    ctx.create("utility_ledger", rid, utility_entry_id=rid, utility_account_id=utility_account_id,
               customer_id=row.get("customer_id", ""), event_type="utility_usage_charge",
               billing_period=src.get("billing_period", ""), entry_date=ctx.now()[:10], due_date=due_date,
               utility_service="water", consumption=src.get("consumption"), consumption_unit="kgal",
               charge_basis="regular", source_entry_id=source_entry_id, amount=amt)
    balance = round(float(row.get("utility_balance") or 0) + amt, 2)
    ctx.update("utility_accounts", utility_account_id, utility_balance=balance)
    return str({"utility_entry_id": rid, "billing_period": src.get("billing_period", ""),
                "consumption": src.get("consumption"), "amount": amt, "due_date": due_date,
                "utility_balance": balance})


@tool(owner="user", rw="write")
def prepay_final_statement_ca2cf476(ctx: ToolContext, utility_account_id: str, amount: float,
                                    payment_channel: str) -> str:
    """Make the resident's own prepayment of their estimated final utility statement on their
    utility account while its service end date is still to come.

    The resident pays the amount given through the channel chosen; the payment is recorded on
    the account dated today, the utility balance falls by the amount paid (any part above what
    is finally billed stays as a credit for the final statement), and a payment confirmation
    number is issued.

    Args:
        utility_account_id: Id class — reference number of the resident's utility account, as given to the resident by the desk from the utility account lookup.
        amount: Fixed-format class — prepayment in USD, 2 decimal places, already rounded half up to the cent.
        payment_channel: Enum class — how the resident pays: ach_autopay is a scheduled automatic bank draft; online_portal_ach is a one-time bank-account (checking or savings) payment made in the resident portal; online_portal_card is a debit or credit card payment made in the resident portal; office_money_order is a money order handed in at the community office; office_cashiers_check is a cashier's check handed in at the community office; office_personal_check is a personal check handed in or mailed to the community office.

    Returns:
        A receipt text containing a dictionary with: utility_entry_id (reference number of the
        payment), payment_ref (payment confirmation number issued for this payment), amount (USD,
        2 decimal places), payment_channel (the channel used), entry_date (date received,
        YYYY-MM-DD) and utility_balance (the resulting account balance, USD, 2 decimal
        places; negative means a credit). A returned payment_ref means the payment is recorded.
    """
    rid = ctx.make_id("upp_", utility_account_id, amount, payment_channel)
    ref = "HCP-" + ctx.make_id("", utility_account_id, amount, payment_channel, length=8).upper()
    acct = ctx.find("utility_accounts", utility_account_id=utility_account_id)
    row = acct[0] if acct else {}
    amt = round(float(amount), 2)
    ctx.create("utility_ledger", rid, utility_entry_id=rid, utility_account_id=utility_account_id,
               customer_id=row.get("customer_id", ""), event_type="utility_payment",
               entry_date=ctx.now()[:10], amount=amt, payment_channel=payment_channel, payment_ref=ref)
    balance = round(float(row.get("utility_balance") or 0) - amt, 2)
    ctx.update("utility_accounts", utility_account_id, utility_balance=balance)
    return str({"utility_entry_id": rid, "payment_ref": ref, "amount": amt,
                "payment_channel": payment_channel, "entry_date": ctx.now()[:10],
                "utility_balance": balance})


@tool(owner="agent", rw="write")
def post_late_fee_5fe5b1d1(ctx: ToolContext, utility_account_id: str, billing_period: str,
                           amount: float) -> str:
    """Charge a late fee on a resident's utility account for one statement left unpaid past its
    grace period.

    The fee is booked against the statement month given, dated today, and the utility balance
    rises by the fee, and the fee appears in the ledger as a utility late fee for that
    statement month.

    Args:
        utility_account_id: Id class — reference number of the resident's utility account, as returned by the utility account lookup for this resident.
        billing_period: Fixed-format class — statement month the late fee is charged on, written YYYY-MM.
        amount: Fixed-format class — late fee in USD, 2 decimal places, already rounded half up to the cent.

    Returns:
        A receipt text containing a dictionary with: utility_entry_id (reference number of the
        fee), billing_period (YYYY-MM), entry_date (posting date, YYYY-MM-DD), amount (USD, 2
        decimal places) and utility_balance (the resulting account balance, USD, 2 decimal
        places; negative means a credit). A returned utility_entry_id means the fee is charged.
    """
    rid = ctx.make_id("ulf_", utility_account_id, billing_period, amount)
    acct = ctx.find("utility_accounts", utility_account_id=utility_account_id)
    row = acct[0] if acct else {}
    amt = round(float(amount), 2)
    ctx.create("utility_ledger", rid, utility_entry_id=rid, utility_account_id=utility_account_id,
               customer_id=row.get("customer_id", ""), event_type="utility_late_fee",
               billing_period=billing_period, entry_date=ctx.now()[:10], amount=amt)
    balance = round(float(row.get("utility_balance") or 0) + amt, 2)
    ctx.update("utility_accounts", utility_account_id, utility_balance=balance)
    return str({"utility_entry_id": rid, "billing_period": billing_period, "entry_date": ctx.now()[:10],
                "amount": amt, "utility_balance": balance})


@tool(owner="user", rw="write")
def request_credit_refund_3a7a9c57(ctx: ToolContext, utility_account_id: str, amount: float) -> str:
    """Submit the former resident's own request for a refund check of credit on their final-billed
    utility account.

    The resident requests a refund of the amount given; the refund is recorded on the account
    dated today, a check for that amount is issued to the mailing address on the resident's
    profile, and the account's credit balance shrinks by the amount refunded (the utility balance
    rises toward zero).

    Args:
        utility_account_id: Id class — reference number of the resident's utility account, as given to the resident by the desk from the utility account lookup.
        amount: Fixed-format class — refund in USD, 2 decimal places, already rounded half up to the cent.

    Returns:
        A receipt text containing a dictionary with: utility_entry_id (reference number of the
        refund, quoted on the check), amount (USD, 2 decimal places), entry_date (date the check
        is issued, YYYY-MM-DD) and utility_balance (the resulting account balance, USD, 2
        decimal places; negative means credit still held). A returned utility_entry_id means the
        refund check is issued.
    """
    rid = ctx.make_id("ucr_", utility_account_id, amount)
    acct = ctx.find("utility_accounts", utility_account_id=utility_account_id)
    row = acct[0] if acct else {}
    amt = round(float(amount), 2)
    ctx.create("utility_ledger", rid, utility_entry_id=rid, utility_account_id=utility_account_id,
               customer_id=row.get("customer_id", ""), event_type="utility_credit_refund",
               entry_date=ctx.now()[:10], amount=amt)
    balance = round(float(row.get("utility_balance") or 0) + amt, 2)
    ctx.update("utility_accounts", utility_account_id, utility_balance=balance)
    return str({"utility_entry_id": rid, "amount": amt, "entry_date": ctx.now()[:10],
                "utility_balance": balance})

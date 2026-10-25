"""Hidden task tools for the fleet_business_servicing difficulty (Kestrel Commercial Fleet Lease).

Each tool performs one atomic posting on a commercial fleet unit lease schedule. Tools never judge
eligibility, prerequisites or amounts; the agent works out every value from the published policy and
the records, and the tool simply books it.
"""

from erlbench import ToolContext, tool


@tool(owner="agent", rw="write")
def bill_early_termination_18cdd752(ctx: ToolContext, fleet_unit_id: str, amount: float) -> str:
    """Bill the early termination charge on a commercial fleet unit lease schedule. The servicing agent
    books one unit charge of the type early termination fee on the named unit, dated today, in the amount
    given, and the unit's charges due balance rises by that amount. The business sees the early
    termination charge listed among the unit's billed charges and in its charges due. Success is the
    confirmation line carrying the new charge's reference number.

    Args:
        fleet_unit_id: Id class — the reference number of the fleet unit lease schedule being billed, read
            from the fleet unit lookup for the business.
        amount: Fixed-format class — the early termination charge in USD, a positive number with 2 decimal
            places (cents), already rounded to the cent; no currency symbol.

    Returns:
        A confirmation line of text naming the charge reference number (an opaque identifier for the new
        charge), the fleet unit reference number, the charge type early_termination_fee, the amount billed
        in USD with 2 decimal places, the billing date in YYYY-MM-DD form, and the unit's charges due
        balance in USD with 2 decimal places including this charge; a line beginning "Error:" means
        no unit matched the reference number and nothing was billed.
    """
    units = ctx.find("fleet_units", fleet_unit_id=fleet_unit_id)
    if not units:
        return f"Error: no fleet unit {fleet_unit_id}."
    unit = units[0]
    amt = round(float(amount), 2)
    rid = ctx.make_id("fltx_", fleet_unit_id, amount, "early_termination_fee")
    today = ctx.now()[:10]
    ctx.create("fleet_transactions", rid, fleet_txn_id=rid, fleet_unit_id=fleet_unit_id,
               customer_id=unit.get("customer_id"), event_type="fleet_unit_charge", txn_date=today,
               amount=amt, fee_type="early_termination_fee")
    balance = round(float(unit.get("charges_due_balance") or 0) + amt, 2)
    ctx.update("fleet_units", fleet_unit_id, charges_due_balance=balance)
    return (f"Charge {rid} billed on fleet unit {fleet_unit_id}: early_termination_fee {amt:.2f} USD "
            f"dated {today}; charges due balance now {balance:.2f} USD.")


@tool(owner="agent", rw="write")
def bill_excess_mileage_e7ed45ad(ctx: ToolContext, fleet_unit_id: str, amount: float) -> str:
    """Bill the excess mileage charge on a turned-in commercial fleet unit lease schedule. The servicing
    agent books one unit charge of the type excess mileage charge on the named unit, dated today, in the
    amount given, and the unit's charges due balance rises by that amount. The business sees the excess
    mileage charge listed among the unit's billed charges and in its charges due. Success is the
    confirmation line carrying the new charge's reference number.

    Args:
        fleet_unit_id: Id class — the reference number of the fleet unit lease schedule being billed, read
            from the fleet unit lookup for the business.
        amount: Fixed-format class — the excess mileage charge in USD, a positive number with 2 decimal
            places (cents), already rounded to the cent; no currency symbol.

    Returns:
        A confirmation line of text naming the charge reference number (an opaque identifier for the new
        charge), the fleet unit reference number, the charge type excess_mileage_charge, the amount billed
        in USD with 2 decimal places, the billing date in YYYY-MM-DD form, and the unit's charges due
        balance in USD with 2 decimal places including this charge; a line beginning "Error:" means
        no unit matched the reference number and nothing was billed.
    """
    units = ctx.find("fleet_units", fleet_unit_id=fleet_unit_id)
    if not units:
        return f"Error: no fleet unit {fleet_unit_id}."
    unit = units[0]
    amt = round(float(amount), 2)
    rid = ctx.make_id("fltx_", fleet_unit_id, amount, "excess_mileage_charge")
    today = ctx.now()[:10]
    ctx.create("fleet_transactions", rid, fleet_txn_id=rid, fleet_unit_id=fleet_unit_id,
               customer_id=unit.get("customer_id"), event_type="fleet_unit_charge", txn_date=today,
               amount=amt, fee_type="excess_mileage_charge")
    balance = round(float(unit.get("charges_due_balance") or 0) + amt, 2)
    ctx.update("fleet_units", fleet_unit_id, charges_due_balance=balance)
    return (f"Charge {rid} billed on fleet unit {fleet_unit_id}: excess_mileage_charge {amt:.2f} USD "
            f"dated {today}; charges due balance now {balance:.2f} USD.")


@tool(owner="agent", rw="write")
def assess_late_charge_6db1a799(ctx: ToolContext, fleet_unit_id: str, billing_period: str, amount: float) -> str:
    """Assess a late charge on one rental invoice month of a commercial fleet unit lease schedule. The
    servicing agent books one late charge on the named unit for the named rental month, dated today, in
    the amount given, and the unit's charges due balance rises by that amount. The business sees the late
    charge against that rental month among the unit's charges. Success is the confirmation line carrying
    the new late charge's reference number.

    Args:
        fleet_unit_id: Id class — the reference number of the fleet unit lease schedule being charged, read
            from the fleet unit lookup for the business.
        billing_period: Fixed-format class — the rental invoice month the late charge relates to, written
            YYYY-MM exactly as the billing period printed on that month's rental invoice.
        amount: Fixed-format class — the late charge in USD, a positive number with 2 decimal places
            (cents), already rounded to the cent; no currency symbol.

    Returns:
        A confirmation line of text naming the late charge reference number (an opaque identifier for the
        new charge), the fleet unit reference number, the rental month in YYYY-MM form, the amount in USD
        with 2 decimal places, the assessment date in YYYY-MM-DD form, and the unit's charges due balance in
        USD with 2 decimal places including this charge; a line beginning "Error:" means no unit
        matched the reference number and nothing was charged.
    """
    units = ctx.find("fleet_units", fleet_unit_id=fleet_unit_id)
    if not units:
        return f"Error: no fleet unit {fleet_unit_id}."
    unit = units[0]
    amt = round(float(amount), 2)
    rid = ctx.make_id("fltx_", fleet_unit_id, billing_period, amount, "late_charge")
    today = ctx.now()[:10]
    ctx.create("fleet_transactions", rid, fleet_txn_id=rid, fleet_unit_id=fleet_unit_id,
               customer_id=unit.get("customer_id"), event_type="fleet_late_charge", txn_date=today,
               billing_period=billing_period, amount=amt, fee_type="late_charge")
    balance = round(float(unit.get("charges_due_balance") or 0) + amt, 2)
    ctx.update("fleet_units", fleet_unit_id, charges_due_balance=balance)
    return (f"Late charge {rid} assessed on fleet unit {fleet_unit_id} for {billing_period}: {amt:.2f} USD "
            f"dated {today}; charges due balance now {balance:.2f} USD.")


@tool(owner="user", rw="write")
def request_credit_refund_a747b6b6(ctx: ToolContext, fleet_unit_id: str, amount: float, payment_channel: str) -> str:
    """The business's named authorized signer requests the refund of a credit balance standing on one of
    its commercial fleet unit lease schedules. One refund is booked on the named unit, dated today, in
    the amount given, with the refund channel chosen recorded on it, and the unit's charges due balance
    rises by that amount. The business sees the refund, its amount and its channel among the unit's
    postings. Success is the confirmation line carrying the refund reference
    number.

    Args:
        fleet_unit_id: Id class — the reference number of the fleet unit lease schedule carrying the credit,
            as the servicing agent reads it out from the fleet unit lookup.
        amount: Fixed-format class — the refund amount in USD, a positive number with 2 decimal places
            (cents), already rounded to the cent; no currency symbol.
        payment_channel: Enum class — the refund channel recorded on the refund, one of: ach_credit for a
            refund to the business's bank account on file by ACH credit; ach_debit is a collection
            channel and is never used for a refund; wire for a refund to the business's account on file
            by bank wire; business_check for a refund by check to the business's billing address;
            not_applicable for a posting that moves no money and is never used for a refund.

    Returns:
        A confirmation line of text naming the refund reference number (an opaque identifier for the
        refund), the fleet unit reference number, the refund amount in USD with 2 decimal places, the refund
        channel as chosen, the refund date in YYYY-MM-DD form, and the unit's charges due balance in USD with
        2 decimal places with the refund booked; a line beginning "Error:" means no unit matched the
        reference number and nothing was refunded.
    """
    units = ctx.find("fleet_units", fleet_unit_id=fleet_unit_id)
    if not units:
        return f"Error: no fleet unit {fleet_unit_id}."
    unit = units[0]
    amt = round(float(amount), 2)
    rid = ctx.make_id("fltx_", fleet_unit_id, amount, payment_channel, "refund")
    today = ctx.now()[:10]
    ctx.create("fleet_transactions", rid, fleet_txn_id=rid, fleet_unit_id=fleet_unit_id,
               customer_id=unit.get("customer_id"), event_type="fleet_credit_refund", txn_date=today,
               amount=amt, payment_channel=payment_channel)
    balance = round(float(unit.get("charges_due_balance") or 0) + amt, 2)
    ctx.update("fleet_units", fleet_unit_id, charges_due_balance=balance)
    return (f"Refund {rid} booked on fleet unit {fleet_unit_id}: {amt:.2f} USD by {payment_channel} "
            f"dated {today}; charges due balance now {balance:.2f} USD.")


@tool(owner="agent", rw="write")
def bill_trac_deficiency_eb6903d6(ctx: ToolContext, fleet_unit_id: str, amount: float) -> str:
    """Bill the terminal rental adjustment deficiency on a sold TRAC fleet unit lease schedule. The
    servicing agent books one deficiency charge on the named unit, dated today, in the amount given, and the
    unit's charges due balance rises by that amount. The business sees the deficiency among the unit's
    charges and in its charges due. Success is the confirmation line carrying the new charge's reference
    number.

    Args:
        fleet_unit_id: Id class — the reference number of the sold fleet unit lease schedule being billed,
            read from the fleet unit lookup for the business.
        amount: Fixed-format class — the deficiency charge in USD, a number of zero or more with 2 decimal
            places (cents), already rounded to the cent; no currency symbol.

    Returns:
        A confirmation line of text naming the deficiency charge reference number (an opaque identifier for
        the new charge), the fleet unit reference number, the amount billed in USD with 2 decimal places, the
        billing date in YYYY-MM-DD form, and the unit's charges due balance in USD with 2 decimal places
        including this charge; a line beginning "Error:" means no unit matched the reference number and
        nothing was billed.
    """
    units = ctx.find("fleet_units", fleet_unit_id=fleet_unit_id)
    if not units:
        return f"Error: no fleet unit {fleet_unit_id}."
    unit = units[0]
    amt = round(float(amount), 2)
    rid = ctx.make_id("fltx_", fleet_unit_id, amount, "trac_deficiency")
    today = ctx.now()[:10]
    ctx.create("fleet_transactions", rid, fleet_txn_id=rid, fleet_unit_id=fleet_unit_id,
               customer_id=unit.get("customer_id"), event_type="fleet_trac_deficiency_charge", txn_date=today,
               amount=amt)
    balance = round(float(unit.get("charges_due_balance") or 0) + amt, 2)
    ctx.update("fleet_units", fleet_unit_id, charges_due_balance=balance)
    return (f"Deficiency charge {rid} billed on fleet unit {fleet_unit_id}: {amt:.2f} USD dated {today}; "
            f"charges due balance now {balance:.2f} USD.")


@tool(owner="user", rw="write")
def remit_arrangement_payment_506aa8ae(ctx: ToolContext, fleet_unit_id: str, amount: float, payment_channel: str) -> str:
    """The business's named authorized signer authorizes a payment under a deficiency payment arrangement
    on one of its fleet unit lease schedules. One business payment is booked on the named unit, dated today,
    in the amount given, with the channel chosen recorded on it, recorded against no rental invoice month,
    and the unit's charges due balance falls by that amount. The business sees the payment, its amount and
    its channel among the unit's postings. Success is the confirmation line carrying the payment reference number.

    Args:
        fleet_unit_id: Id class — the reference number of the fleet unit lease schedule the payment is
            applied to, as the servicing agent reads it out from the fleet unit lookup.
        amount: Fixed-format class — the payment amount in USD, a positive number with 2 decimal places
            (cents), already rounded to the cent; no currency symbol.
        payment_channel: Enum class — the payment channel recorded on the payment, one of: ach_debit for
            a one-time debit of the business's bank account on file authorized by the signer; ach_credit
            for an ACH credit from the business's own bank; wire for a bank wire from the business;
            business_check for a check from the business; not_applicable for a posting that moves no money
            and is never used for a payment.

    Returns:
        A confirmation line of text naming the payment reference number (an opaque identifier for the
        payment, also recorded as its remittance reference), the fleet unit reference number, the amount in
        USD with 2 decimal places, the channel as chosen, the posting date in YYYY-MM-DD form, and the unit's
        charges due balance in USD with 2 decimal places with the payment applied; a line beginning
        "Error:" means no unit matched the reference number and nothing was posted.
    """
    units = ctx.find("fleet_units", fleet_unit_id=fleet_unit_id)
    if not units:
        return f"Error: no fleet unit {fleet_unit_id}."
    unit = units[0]
    amt = round(float(amount), 2)
    rid = ctx.make_id("fltx_", fleet_unit_id, amount, payment_channel, "arrangement_payment")
    today = ctx.now()[:10]
    ctx.create("fleet_transactions", rid, fleet_txn_id=rid, fleet_unit_id=fleet_unit_id,
               customer_id=unit.get("customer_id"), event_type="fleet_payment", txn_date=today,
               amount=amt, payment_channel=payment_channel, remittance_reference=rid, billing_period="")
    balance = round(float(unit.get("charges_due_balance") or 0) - amt, 2)
    ctx.update("fleet_units", fleet_unit_id, charges_due_balance=balance)
    return (f"Payment {rid} posted on fleet unit {fleet_unit_id}: {amt:.2f} USD by {payment_channel} dated {today}; "
            f"charges due balance now {balance:.2f} USD.")

"""Hidden task tools for the security_deposit_lifecycle difficulty of env_0043_rural_electric_cooperative.

Each tool performs one atomic write on a Security Deposits record and judges no eligibility, prerequisite
or amount; every figure it receives has been worked out by the caller from the published policies.
"""

from erlbench import ToolContext, tool


@tool(owner="user", rw="write")
def pay_reinstated_deposit_installment_114bda0d(ctx: ToolContext, deposit_account_id: str, amount: float,
                                                installment_number: int) -> dict:
    """The member pays, by card over the phone, one installment of a security deposit that is waiting to be
    paid, and the payment is posted to that deposit record. One call posts one deposit payment entry dated
    today with a new confirmation number, adds the amount to the cash the cooperative holds on the record,
    and moves the record to partially paid, or to held with today as its paid-in-full date when the cash
    held reaches the required amount. The member sees the confirmation number and the cash now held.

    Args:
        deposit_account_id: Id class — the reference number of the security deposit record being paid, as
            returned by the deposit record lookup for the member.
        amount: Fixed-format class — the amount the member pays toward the deposit, in USD, a positive
            number with 2 decimal places, rounded to the nearest cent before posting.
        installment_number: Fixed-format class — which installment of the deposit this payment is, an
            integer starting at 1 for the first installment.

    Returns:
        A dict receipt: status ("posted" on success), deposit_entry_id (reference number of the new deposit
        ledger entry), payment_reference (confirmation number issued for the card payment, text),
        deposit_account_id (the record paid), amount (USD, 2 decimal places, as posted), installment_number
        (integer), held_amount (cash now held on the record, USD, 2 decimal places) and deposit_status
        (partially_paid or held).
    """
    amt = round(float(amount), 2)
    inst = int(installment_number)
    rec = ctx.find("deposit_accounts", deposit_account_id=deposit_account_id)
    row = rec[0] if rec else {}
    today = ctx.now()[:10]
    eid = ctx.make_id("dpe_", deposit_account_id, amt, inst)
    ref = "44" + ctx.make_id("", deposit_account_id, amt, inst, length=8).upper()
    ctx.create("deposit_ledger", eid, deposit_entry_id=eid, deposit_account_id=deposit_account_id,
               customer_id=row.get("customer_id"), event_type="deposit_payment", entry_date=today,
               amount=amt, installment_number=inst, payment_reference=ref)
    held = round(float(row.get("held_amount") or 0) + amt, 2)
    required = round(float(row.get("required_amount") or 0), 2)
    if held >= required:
        ctx.update("deposit_accounts", deposit_account_id, held_amount=held, status="held", paid_in_full_date=today)
        status = "held"
    else:
        ctx.update("deposit_accounts", deposit_account_id, held_amount=held, status="partially_paid")
        status = "partially_paid"
    return {"status": "posted", "deposit_entry_id": eid, "payment_reference": ref,
            "deposit_account_id": deposit_account_id, "amount": amt, "installment_number": inst,
            "held_amount": held, "deposit_status": status}




@tool(owner="agent", rw="write")
def assess_reconnection_deposit_9009d8a2(ctx: ToolContext, service_account_id: str, assessment_basis: str,
                                         required_amount: float, installment_count: int) -> dict:
    """Assess a Residential Credit Reestablishment Deposit on a Schedule R or Schedule FH electric service
    account and bill it to the member who holds the account. One call opens one new deposit record in
    assessed status, dated today, on the Residential Credit Reestablishment Deposit tier, with the amount
    required and the number of installments granted, and with no cash held yet. The member sees the new
    deposit on the account and is billed for it.

    Args:
        service_account_id: Id class — the reference number of the electric service account the deposit
            secures, as returned by the service account lookup for the member.
        assessment_basis: Enum class — why the deposit is assessed, exactly one of: new_service (the
            service account is opened for new service), reconnect_after_nonpay (the account is being
            reconnected after a nonpayment disconnection), usage_reassessment (an additional deposit
            because the account's bills have grown), waiver_reinstatement (a deposit that had been
            waived is reinstated as a cash deposit).
        required_amount: Fixed-format class — the deposit required, in USD, a positive number with 2
            decimal places, rounded to the nearest cent before it is recorded.
        installment_count: Fixed-format class — the number of installments granted, an integer; 1 means
            the deposit is due in full.

    Returns:
        A dict receipt: status ("assessed" on success), deposit_account_id (reference number of the new
        deposit record), service_account_id (the account secured), variant_name (the deposit tier, always
        Residential Credit Reestablishment Deposit), assessment_basis (as recorded), required_amount (USD,
        2 decimal places), installment_count (integer) and assessed_date (YYYY-MM-DD, today).
    """
    amt = round(float(required_amount), 2)
    n = int(installment_count)
    acct = ctx.find("service_accounts", service_account_id=service_account_id)
    cust = acct[0].get("customer_id") if acct else None
    today = ctx.now()[:10]
    tier = "Residential Credit Reestablishment Deposit"
    did = ctx.make_id("dep_", service_account_id, assessment_basis, amt, n)
    ctx.create("deposit_accounts", did, deposit_account_id=did, customer_id=cust,
               service_account_id=service_account_id, variant_name=tier, status="assessed",
               assessment_basis=assessment_basis, assessed_date=today, required_amount=amt,
               installment_count=n, held_amount=0.0, accrued_interest=0.0)
    return {"status": "assessed", "deposit_account_id": did, "service_account_id": service_account_id,
            "variant_name": tier, "assessment_basis": assessment_basis, "required_amount": amt,
            "installment_count": n, "assessed_date": today}


@tool(owner="agent", rw="write")
def assess_reinstated_deposit_c3ac4854(ctx: ToolContext, service_account_id: str, variant_name: str,
                                       assessment_basis: str, required_amount: float,
                                       installment_count: int) -> dict:
    """Assess a cash security deposit that replaces a deposit waiver which no longer stands, on the electric
    service account the waiver covered, and bill it to the member who holds the account. One call opens
    one new deposit record in assessed status, dated today, on the deposit tier given, with the amount
    required and the number of installments granted, and with no cash held yet. The member sees the new
    deposit on that account and is billed for it.

    Args:
        service_account_id: Id class — the reference number of the electric service account the deposit
            secures, as returned by the service account lookup for the member.
        variant_name: Enum class — the official deposit tier, exactly one of: Residential Standard Deposit
            (an account on Schedule R Residential Service), Residential Credit Reestablishment Deposit (a
            Schedule R or Schedule FH account reconnected after a nonpayment disconnection), Seasonal
            Residence Deposit (an account on Schedule RS Seasonal Residential Service), Farm Service Deposit
            (an account on Schedule FH Farm and Home Service), General Service Deposit (an account on
            Schedule GS-1 or Schedule GS-3 general service), Irrigation and Large Power Deposit (an account
            on Schedule IR Irrigation Service or Schedule LP Large Power Service).
        assessment_basis: Enum class — why the deposit is assessed, exactly one of: new_service (the
            service account is opened for new service), reconnect_after_nonpay (the account is being
            reconnected after a nonpayment disconnection), usage_reassessment (an additional deposit
            because the account's bills have grown), waiver_reinstatement (a deposit that had been
            waived is reinstated as a cash deposit).
        required_amount: Fixed-format class — the deposit required, in USD, a positive number with 2
            decimal places, rounded to the nearest cent before it is recorded.
        installment_count: Fixed-format class — the number of installments granted, an integer; 1 means
            the deposit is due in full.

    Returns:
        A dict receipt: status ("assessed" on success), deposit_account_id (reference number of the new
        deposit record), service_account_id (the account secured), variant_name (the deposit tier as
        recorded), assessment_basis (as recorded), required_amount (USD, 2 decimal places),
        installment_count (integer) and assessed_date (YYYY-MM-DD, today).
    """
    amt = round(float(required_amount), 2)
    n = int(installment_count)
    acct = ctx.find("service_accounts", service_account_id=service_account_id)
    cust = acct[0].get("customer_id") if acct else None
    today = ctx.now()[:10]
    did = ctx.make_id("dep_", service_account_id, variant_name, assessment_basis, amt, n)
    ctx.create("deposit_accounts", did, deposit_account_id=did, customer_id=cust,
               service_account_id=service_account_id, variant_name=variant_name, status="assessed",
               assessment_basis=assessment_basis, assessed_date=today, required_amount=amt,
               installment_count=n, held_amount=0.0, accrued_interest=0.0)
    return {"status": "assessed", "deposit_account_id": did, "service_account_id": service_account_id,
            "variant_name": variant_name, "assessment_basis": assessment_basis, "required_amount": amt,
            "installment_count": n, "assessed_date": today}


@tool(owner="agent", rw="write")
def post_year_end_deposit_interest_3b717487(ctx: ToolContext, deposit_account_id: str, accrual_period_start: str,
                                            accrual_period_end: str, interest_rate_pct: float, accrual_days: int,
                                            amount: float) -> dict:
    """Post the December 31 interest accrual of one calendar year on a cash security deposit. One call writes
    one interest accrual entry dated today on the deposit's ledger with the accrual period, the annual rate,
    the days counted and the interest amount, and adds that amount to the interest accrued and not yet paid
    out on the deposit record. The member sees the year's interest on the deposit.

    Args:
        deposit_account_id: Id class — the reference number of the security deposit record, as returned by
            the deposit record lookup for the member.
        accrual_period_start: Fixed-format class — the first day of the accrual period, a date in
            YYYY-MM-DD format.
        accrual_period_end: Fixed-format class — the last day of the accrual period, a date in YYYY-MM-DD
            format.
        interest_rate_pct: Fixed-format class — the annual interest rate applied, in percent, with 2
            decimal places (for example 2.07 means 2.07 percent).
        accrual_days: Fixed-format class — the number of days of the period on which interest is counted,
            an integer.
        amount: Fixed-format class — the interest accrued for the period, in USD, a positive number with 2
            decimal places, rounded to the nearest cent.

    Returns:
        A dict receipt: status ("accrued" on success), deposit_entry_id (reference number of the new ledger
        entry), deposit_account_id, accrual_period_start and accrual_period_end (YYYY-MM-DD),
        interest_rate_pct (percent, 2 decimal places), accrual_days (integer), amount (USD, 2 decimal
        places) and accrued_interest (interest now accrued and unpaid on the record, USD, 2 decimal places).
    """
    amt = round(float(amount), 2)
    rate = round(float(interest_rate_pct), 2)
    days = int(accrual_days)
    rec = ctx.find("deposit_accounts", deposit_account_id=deposit_account_id)
    row = rec[0] if rec else {}
    eid = ctx.make_id("dpy_", deposit_account_id, accrual_period_start, accrual_period_end, rate, days, amt)
    ctx.create("deposit_ledger", eid, deposit_entry_id=eid, deposit_account_id=deposit_account_id,
               customer_id=row.get("customer_id"), event_type="deposit_interest_accrual", entry_date=ctx.now()[:10],
               accrual_period_start=accrual_period_start, accrual_period_end=accrual_period_end,
               interest_rate_pct=rate, accrual_days=days, amount=amt)
    accrued = round(float(row.get("accrued_interest") or 0) + amt, 2)
    ctx.update("deposit_accounts", deposit_account_id, accrued_interest=accrued)
    return {"status": "accrued", "deposit_entry_id": eid, "deposit_account_id": deposit_account_id,
            "accrual_period_start": accrual_period_start, "accrual_period_end": accrual_period_end,
            "interest_rate_pct": rate, "accrual_days": days, "amount": amt, "accrued_interest": accrued}


@tool(owner="agent", rw="write")
def post_refund_date_deposit_interest_50449ec1(ctx: ToolContext, deposit_account_id: str, accrual_period_start: str,
                                               accrual_period_end: str, interest_rate_pct: float,
                                               accrual_days: int, amount: float) -> dict:
    """Post the interest accrual of the part of a year that ends on the day a cash security deposit is
    refunded. One call writes one interest accrual entry dated today on the deposit's ledger with the
    accrual period, the annual rate, the days counted and the interest amount, and adds that amount to the
    interest accrued and not yet paid out on the deposit record. The member sees the part-year interest on
    the deposit.

    Args:
        deposit_account_id: Id class — the reference number of the security deposit record, as returned by
            the deposit record lookup for the member.
        accrual_period_start: Fixed-format class — the first day of the accrual period, a date in
            YYYY-MM-DD format.
        accrual_period_end: Fixed-format class — the last day of the accrual period, a date in YYYY-MM-DD
            format.
        interest_rate_pct: Fixed-format class — the annual interest rate applied, in percent, with 2
            decimal places (for example 1.84 means 1.84 percent).
        accrual_days: Fixed-format class — the number of days of the period on which interest is counted,
            an integer.
        amount: Fixed-format class — the interest accrued for the period, in USD, a positive number with 2
            decimal places, rounded to the nearest cent.

    Returns:
        A dict receipt: status ("accrued" on success), deposit_entry_id (reference number of the new ledger
        entry), deposit_account_id, accrual_period_start and accrual_period_end (YYYY-MM-DD),
        interest_rate_pct (percent, 2 decimal places), accrual_days (integer), amount (USD, 2 decimal
        places) and accrued_interest (interest now accrued and unpaid on the record, USD, 2 decimal places).
    """
    amt = round(float(amount), 2)
    rate = round(float(interest_rate_pct), 2)
    days = int(accrual_days)
    rec = ctx.find("deposit_accounts", deposit_account_id=deposit_account_id)
    row = rec[0] if rec else {}
    eid = ctx.make_id("dpp_", deposit_account_id, accrual_period_start, accrual_period_end, rate, days, amt)
    ctx.create("deposit_ledger", eid, deposit_entry_id=eid, deposit_account_id=deposit_account_id,
               customer_id=row.get("customer_id"), event_type="deposit_interest_accrual", entry_date=ctx.now()[:10],
               accrual_period_start=accrual_period_start, accrual_period_end=accrual_period_end,
               interest_rate_pct=rate, accrual_days=days, amount=amt)
    accrued = round(float(row.get("accrued_interest") or 0) + amt, 2)
    ctx.update("deposit_accounts", deposit_account_id, accrued_interest=accrued)
    return {"status": "accrued", "deposit_entry_id": eid, "deposit_account_id": deposit_account_id,
            "accrual_period_start": accrual_period_start, "accrual_period_end": accrual_period_end,
            "interest_rate_pct": rate, "accrual_days": days, "amount": amt, "accrued_interest": accrued}


@tool(owner="user", rw="write")
def refund_deposit_by_check_ead765c2(ctx: ToolContext, deposit_account_id: str, refund_amount: float) -> dict:
    """The member asks for a security deposit refund to be paid by check to the mailing address on file
    instead of as a bill credit, and the refund is booked on the deposit record. One call writes one refund
    entry dated today, paid by check, for the amount given; the interest accrued and not yet paid out on the
    record is paid with it and the rest of the amount comes out of the cash held. When no cash is left the
    record ends as refunded with today as its closing date; otherwise it stays held. The member sees the
    check amount and the cash still held.

    Args:
        deposit_account_id: Id class — the reference number of the security deposit record being refunded,
            as returned by the deposit record lookup for the member.
        refund_amount: Fixed-format class — the total amount of the refund check, in USD, a positive number
            with 2 decimal places, rounded to the nearest cent.

    Returns:
        A dict receipt: status ("refunded" on success), deposit_entry_id (reference number of the refund
        entry), deposit_account_id, refund_amount (USD, 2 decimal places), disbursement_method (always
        check), interest_paid (USD, 2 decimal places), cash_refunded (USD, 2 decimal places), held_amount
        (cash still held, USD, 2 decimal places) and deposit_status (held or refunded).
    """
    amt = round(float(refund_amount), 2)
    rec = ctx.find("deposit_accounts", deposit_account_id=deposit_account_id)
    row = rec[0] if rec else {}
    today = ctx.now()[:10]
    interest = round(float(row.get("accrued_interest") or 0), 2)
    cash = round(amt - interest, 2)
    held = round(float(row.get("held_amount") or 0) - cash, 2)
    eid = ctx.make_id("dpr_", deposit_account_id, amt)
    ctx.create("deposit_ledger", eid, deposit_entry_id=eid, deposit_account_id=deposit_account_id,
               customer_id=row.get("customer_id"), event_type="deposit_refund", entry_date=today,
               disbursement_method="check", amount=amt)
    if held <= 0:
        ctx.update("deposit_accounts", deposit_account_id, held_amount=0.0, accrued_interest=0.0,
                   status="refunded", closed_date=today)
        status = "refunded"
    else:
        ctx.update("deposit_accounts", deposit_account_id, held_amount=held, accrued_interest=0.0)
        status = "held"
    return {"status": "refunded", "deposit_entry_id": eid, "deposit_account_id": deposit_account_id,
            "refund_amount": amt, "disbursement_method": "check", "interest_paid": interest,
            "cash_refunded": cash, "held_amount": max(held, 0.0), "deposit_status": status}

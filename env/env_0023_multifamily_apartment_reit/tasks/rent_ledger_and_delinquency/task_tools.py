"""Hidden task tools of the rent_ledger_and_delinquency difficulty (Apartment Home Lease ledger).

Each tool is reached only through unlock_* -> call_* and performs exactly one atomic ledger write with the
values the agent has already worked out from the lease charter; no tool aggregates history, judges
eligibility, checks a prerequisite or refuses a call.
"""

from erlbench import ToolContext, tool


@tool(owner="agent", rw="write")
def post_employer_discount_credit_34aaf7ea(ctx: ToolContext, lease_id: str, billing_period: str,
                                           source_charge_id: str, amount: float) -> str:
    """Post one preferred employer discount credit to an apartment home lease ledger.

    The resident services agent credits the lease's rent for one billing period under the preferred employer rent
    discount program. One call records a single credit line coded preferred_employer_discount against the named base
    rent charge, dated today, for the amount given, and lowers the lease's current balance due by that amount. The
    resident sees the credit on the lease ledger immediately. The receipt echoes the new credit line and the balance
    due after it.

    Args:
        lease_id: Id class — the reference number of the apartment home lease whose ledger is credited, read from the
            lease lookup for the verified resident.
        billing_period: Fixed-format class — the rent month the credit belongs to, written YYYY-MM (the same month as
            the base rent charge being discounted).
        source_charge_id: Id class — the reference number of the single base rent charge line this discount credit is
            posted against, read from the lease charge lookup.
        amount: Fixed-format class — the credit amount in USD as a positive number with 2 decimal places (rounded to
            the cent before it is passed).

    Returns:
        A text rendering of a dictionary with: status ("posted" when the credit line was recorded); charge_id (the
        reference number of the new credit line); charge_code ("preferred_employer_discount"); billing_period (the
        YYYY-MM month credited); source_charge_id (the base rent charge credited); amount (the USD amount credited,
        2 decimal places); new_balance_due (the lease balance due in USD after the credit, 2 decimal places).
    """
    rows = ctx.find("leases", lease_id=lease_id)
    lease = rows[0] if rows else {}
    amt = round(float(amount), 2)
    rid = ctx.make_id("lcr_", lease_id, billing_period, source_charge_id, amt)
    ctx.create("lease_charges", rid, charge_id=rid, lease_id=lease_id, customer_id=lease.get("customer_id", ""),
               event_type="lease_charge_credit", charge_code="preferred_employer_discount", billing_period=billing_period,
               charge_date=ctx.now()[:10], amount=amt, proration_days=0, days_in_period=0,
               service_window="not_applicable", source_charge_id=source_charge_id, source_payment_id="")
    new_balance = round(float(lease.get("balance_due") or 0) - amt, 2)
    if lease:
        ctx.update("leases", lease_id, balance_due=new_balance)
    return str({"status": "posted", "charge_id": rid, "charge_code": "preferred_employer_discount",
                "billing_period": billing_period, "source_charge_id": source_charge_id,
                "amount": amt, "new_balance_due": new_balance})


@tool(owner="user", rw="write")
def make_rent_catch_up_payment_381e22a2(ctx: ToolContext, lease_id: str, payment_method: str, amount: float,
                                        plan_request_id: str) -> str:
    """Make a one-time payment on your own apartment home lease to catch up rent that is behind.

    You, the leaseholder, pay the stated amount onto your lease ledger today with the instrument you choose. One call
    records a single payment received on the lease, dated today, issues a portal confirmation number for it, and
    lowers the lease's current balance due by the amount paid. The payment and its confirmation number appear on your
    lease ledger at once. The receipt shows the confirmation number and the balance due after the payment.

    Args:
        lease_id: Id class — the reference number of your apartment home lease, as the agent read it from the lease
            lookup and gave it to you.
        payment_method: Enum class — the instrument used for this payment, exactly one of: ach_autopay — a recurring
            autopay bank draft taken on the rent due date by an existing enrollment, never a payment made by hand;
            ach_one_time — a single bank transfer you authorize now from your checking or savings account;
            debit_card — a payment charged now to your debit card; credit_card — a payment charged now to your credit
            card; money_order — a money order delivered to the leasing office; cashiers_check — a cashier's check
            delivered to the leasing office; deposit_application — the security deposit applied to the lease balance
            at final accounting after move-out, never a payment you make during the tenancy.
        amount: Fixed-format class — the amount paid in USD as a positive number with 2 decimal places, as the agent
            stated it to you.
        plan_request_id: Id class — the reference number of the signed payment plan this payment is a down payment or
            installment of, as read from the payment plan lookup; pass an empty string "" for a payment that belongs
            to no payment plan.

    Returns:
        A text rendering of a dictionary with: status ("received" when the payment was recorded); payment_id (the
        reference number of the new payment); payment_reference (the portal confirmation number issued for this
        payment); payment_method (the instrument recorded); amount (the USD amount received, 2 decimal places);
        payment_date (today's date, YYYY-MM-DD); new_balance_due (the lease balance due in USD after the payment,
        2 decimal places).
    """
    rows = ctx.find("leases", lease_id=lease_id)
    lease = rows[0] if rows else {}
    amt = round(float(amount), 2)
    rid = ctx.make_id("lpy_", lease_id, payment_method, amt, plan_request_id)
    reference = "LRT-" + rid[-8:].upper()
    ctx.create("lease_payments", rid, payment_id=rid, lease_id=lease_id, customer_id=lease.get("customer_id", ""),
               event_type="lease_payment", payment_method=payment_method, amount=amt,
               payment_date=ctx.now()[:10], payment_reference=reference, source_payment_id="",
               return_reason="not_applicable", plan_request_id=plan_request_id or None)
    new_balance = round(float(lease.get("balance_due") or 0) - amt, 2)
    if lease:
        ctx.update("leases", lease_id, balance_due=new_balance)
    return str({"status": "received", "payment_id": rid, "payment_reference": reference,
                "payment_method": payment_method, "amount": amt, "payment_date": ctx.now()[:10],
                "new_balance_due": new_balance})


@tool(owner="agent", rw="write")
def grant_courtesy_late_fee_waiver_1c994f24(ctx: ToolContext, lease_id: str, billing_period: str,
                                            source_charge_id: str, amount: float) -> str:
    """Grant a courtesy late fee waiver on an apartment home lease ledger.

    The resident services agent grants the resident a courtesy waiver of late fees for one billing period. One call
    records a single credit line coded late_fee_waiver against the named initial late fee charge, dated today, for
    the amount given, and lowers the lease's current balance due by that amount. The resident sees the waiver credit
    on the lease ledger immediately. The receipt echoes the new credit line and the balance due after it.

    Args:
        lease_id: Id class — the reference number of the apartment home lease whose ledger is credited, read from the
            lease lookup for the verified resident.
        billing_period: Fixed-format class — the rent month whose late fees are waived, written YYYY-MM (the same month
            as the initial late fee charge named below).
        source_charge_id: Id class — the reference number of the initial late fee charge line the waiver credit is
            posted against, read from the lease charge lookup.
        amount: Fixed-format class — the waiver amount in USD as a positive number with 2 decimal places (rounded to
            the cent before it is passed).

    Returns:
        A text rendering of a dictionary with: status ("posted" when the waiver credit was recorded); charge_id (the
        reference number of the new credit line); charge_code ("late_fee_waiver"); billing_period (the YYYY-MM month
        whose late fees were waived); source_charge_id (the initial late fee charge credited); amount (the USD amount
        waived, 2 decimal places); new_balance_due (the lease balance due in USD after the waiver, 2 decimal places).
    """
    rows = ctx.find("leases", lease_id=lease_id)
    lease = rows[0] if rows else {}
    amt = round(float(amount), 2)
    rid = ctx.make_id("lcw_", lease_id, billing_period, source_charge_id, amt)
    ctx.create("lease_charges", rid, charge_id=rid, lease_id=lease_id, customer_id=lease.get("customer_id", ""),
               event_type="lease_charge_credit", charge_code="late_fee_waiver", billing_period=billing_period,
               charge_date=ctx.now()[:10], amount=amt, proration_days=0, days_in_period=0,
               service_window="not_applicable", source_charge_id=source_charge_id, source_payment_id="")
    new_balance = round(float(lease.get("balance_due") or 0) - amt, 2)
    if lease:
        ctx.update("leases", lease_id, balance_due=new_balance)
    return str({"status": "posted", "charge_id": rid, "charge_code": "late_fee_waiver",
                "billing_period": billing_period, "source_charge_id": source_charge_id,
                "amount": amt, "new_balance_due": new_balance})


@tool(owner="agent", rw="write")
def post_late_fee_review_reversal_dc9bc174(ctx: ToolContext, lease_id: str, billing_period: str,
                                          source_charge_id: str, amount: float) -> str:
    """Post one late fee review reversal to an apartment home lease ledger.

    The resident services agent reverses the part of one billing period's late fees that a late fee review does not
    allow. One call records a single credit line coded charge_reversal against the named initial late fee charge,
    dated today, for the amount given, and lowers the lease's current balance due by that amount. The resident sees
    the reversal on the lease ledger immediately. The receipt echoes the new credit line and the balance due after it.

    Args:
        lease_id: Id class — the reference number of the apartment home lease whose ledger is credited, read from the
            lease lookup for the verified resident.
        billing_period: Fixed-format class — the rent month whose late fees were reviewed, written YYYY-MM (the same
            month as the initial late fee charge named below).
        source_charge_id: Id class — the reference number of the initial late fee charge line the reversal credit is
            posted against, read from the lease charge lookup.
        amount: Fixed-format class — the reversal amount in USD as a positive number with 2 decimal places (rounded to
            the cent before it is passed).

    Returns:
        A text rendering of a dictionary with: status ("posted" when the reversal credit was recorded); charge_id (the
        reference number of the new credit line); charge_code ("charge_reversal"); billing_period (the YYYY-MM month
        whose late fees were reviewed); source_charge_id (the initial late fee charge credited); amount (the USD amount
        reversed, 2 decimal places); new_balance_due (the lease balance due in USD after the reversal, 2 decimal
        places).
    """
    rows = ctx.find("leases", lease_id=lease_id)
    lease = rows[0] if rows else {}
    amt = round(float(amount), 2)
    rid = ctx.make_id("lcv_", lease_id, billing_period, source_charge_id, amt)
    ctx.create("lease_charges", rid, charge_id=rid, lease_id=lease_id, customer_id=lease.get("customer_id", ""),
               event_type="lease_charge_credit", charge_code="charge_reversal", billing_period=billing_period,
               charge_date=ctx.now()[:10], amount=amt, proration_days=0, days_in_period=0,
               service_window="not_applicable", source_charge_id=source_charge_id, source_payment_id="")
    new_balance = round(float(lease.get("balance_due") or 0) - amt, 2)
    if lease:
        ctx.update("leases", lease_id, balance_due=new_balance)
    return str({"status": "posted", "charge_id": rid, "charge_code": "charge_reversal",
                "billing_period": billing_period, "source_charge_id": source_charge_id,
                "amount": amt, "new_balance_due": new_balance})


@tool(owner="user", rw="write")
def sign_payment_plan_b63c5de9(ctx: ToolContext, plan_request_id: str, lease_id: str, arrears_amount: float,
                               down_payment_amount: float, installment_count: int, installment_amount: float,
                               first_installment_date: str) -> str:
    """Sign the payment plan drawn up for your own apartment home lease.

    You, the leaseholder, sign a payment plan request that has been drawn up for your lease and is waiting for your
    signature. One call records your signature on that request, writes onto it the figures you are signing (the
    arrears the plan covers, the down payment, the number and amount of installments and the first installment date)
    and changes its status from submitted to signed. The signed plan and its figures appear on your account at once.
    The receipt echoes the plan reference and the figures recorded.

    Args:
        plan_request_id: Id class — the reference number of the payment plan request awaiting your signature, as the
            agent read it from the payment plan lookup and gave it to you.
        lease_id: Id class — the reference number of your apartment home lease the plan belongs to, as read from the
            lease lookup.
        arrears_amount: Fixed-format class — the past-due amount the plan covers, in USD as a positive number with
            2 decimal places, as the agent stated it to you.
        down_payment_amount: Fixed-format class — the down payment of the plan, in USD as a positive number with
            2 decimal places, as the agent stated it to you.
        installment_count: Fixed-format class — the number of equal installments after the down payment, an integer
            count of at least 1.
        installment_amount: Fixed-format class — the amount of each installment, in USD with 2 decimal places (the last
            installment absorbs any rounding difference).
        first_installment_date: Fixed-format class — the due date of the first installment, a calendar date written
            YYYY-MM-DD.

    Returns:
        A text rendering of a dictionary with: status ("signed" when your signature and the figures were recorded);
        plan_request_id (the plan reference signed); arrears_amount, down_payment_amount and installment_amount (USD,
        2 decimal places); installment_count (integer); first_installment_date (YYYY-MM-DD); signed_at (the moment
        the signature was recorded, as the system clock gives it).
    """
    arrears = round(float(arrears_amount), 2)
    down = round(float(down_payment_amount), 2)
    each = round(float(installment_amount), 2)
    count = int(installment_count)
    ctx.update("lease_payment_plan_requests", plan_request_id, lease_id=lease_id, arrears_amount=arrears,
               down_payment_amount=down, installment_count=count, installment_amount=each,
               first_installment_date=first_installment_date, request_status="signed")
    return str({"status": "signed", "plan_request_id": plan_request_id, "arrears_amount": arrears,
                "down_payment_amount": down, "installment_count": count, "installment_amount": each,
                "first_installment_date": first_installment_date, "signed_at": ctx.now()})

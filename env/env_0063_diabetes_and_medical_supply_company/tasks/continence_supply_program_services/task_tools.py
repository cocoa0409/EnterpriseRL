"""Hidden task tools for continence_supply_program_services (Larkfield Medical Supply).

Each tool performs one atomic write on a Urology and Continence Supply Program and is reached
only through the unlock/call meta-tools. No tool checks eligibility, prerequisites or amounts;
the values passed in are recorded as given.
"""

from erlbench import ToolContext, tool


@tool(owner="agent", rw="write")
def ship_catheter_refill_863073b5(ctx: ToolContext, customer_id: str, continence_program_id: str,
                                  coverage_id: str, continence_order_id: str, previous_continence_shipment_id: str,
                                  units: int, supply_days: int) -> str:
    """Release one refill package of straight-tip intermittent catheters (HCPCS A4351) on a
    customer's Urology and Continence Supply Program. One call records one package leaving the
    warehouse today by standard ground shipping, billed to the program's payer by claim, drawing
    the given billing units from the named authorization grant; the program's billing units still
    authorized to ship fall by the units shipped, and today's date is recorded as the customer's
    refill confirmation date. The customer can then be told the package is on its way. Success is
    shown by the receipt below carrying the new shipment reference.

    Args:
        customer_id: Id class — the customer reference number of the program holder, read from
            the customer profile lookup; the package is addressed to this customer.
        continence_program_id: Id class — the reference number of the customer's Urology and
            Continence Supply Program the refill ships on, read from the program lookup.
        coverage_id: Id class — the reference number of the insurance coverage record the program
            bills, read from the program lookup; it is part of the package's reference.
        continence_order_id: Id class — the reference number of the authorization grant record
            the refill draws its units from, read from the program's prescription and
            authorization file lookup.
        previous_continence_shipment_id: Id class — the reference number of the program's latest
            earlier refill package of the same catheter, read from the shipment history lookup;
            it is part of the new package's reference.
        units: Fixed-format class — the billing units of straight-tip catheters in the package,
            in integer billing units (one billing unit is one catheter, so the package also holds
            that integer count of physical pieces); a whole number, no decimals.
        supply_days: Fixed-format class — the days of supply the package covers, in integer
            calendar days, multiple of 30.

    Returns:
        A dictionary receipt with: status ("shipped" on success); continence_shipment_id (the new
        shipment reference); item_code (always A4351); units (integer billing units shipped);
        supply_days (integer calendar days covered); ship_date (today, YYYY-MM-DD);
        authorized_units_remaining (integer billing units still authorized after this package).
    """
    rid = ctx.make_id("csh_", customer_id, continence_program_id, coverage_id, continence_order_id,
                      previous_continence_shipment_id, units, supply_days)
    program = (ctx.find("continence_programs", continence_program_id=continence_program_id) or [{}])[0]
    today = ctx.now()[:10]
    ctx.create("continence_shipments", rid, continence_shipment_id=rid,
               continence_program_id=continence_program_id, customer_id=customer_id,
               event_type="continence_refill_shipment", continence_order_id=continence_order_id,
               item_code="A4351", units=int(units), pieces=int(units), supply_days=int(supply_days),
               ship_date=today, shipping_method="standard", billing_route="payer_claim",
               refill_confirmed_date=today)
    remaining = int(program.get("authorized_units_remaining") or 0) - int(units)
    ctx.update("continence_programs", continence_program_id, authorized_units_remaining=remaining)
    return str({"status": "shipped", "continence_shipment_id": rid, "item_code": "A4351",
                "units": int(units), "supply_days": int(supply_days), "ship_date": today,
                "authorized_units_remaining": remaining})


@tool(owner="user", rw="write")
def sign_liability_notice_4a664827(ctx: ToolContext, continence_program_id: str, notice_type: str,
                                   notice_units: int) -> str:
    """The customer, or the customer's authorized representative on their behalf, signs an advance
    notice of financial liability for straight-tip intermittent catheters (HCPCS A4351) on the
    customer's own Urology and Continence Supply Program; no Larkfield representative signs it,
    accepting that the stated billing units may be billed to them if their payer does not pay
    for them. One call records one signed notice dated today for the item and units given; the
    notice then stands on the program's file. Success is shown by the receipt below carrying the
    notice reference.

    Args:
        continence_program_id: Id class — the reference number of the customer's Urology and
            Continence Supply Program the notice is signed for, as given by the agent from the
            program lookup.
        notice_type: Enum class — the notice form being signed, exactly one of:
            plan_member_waiver — the commercial plan's member waiver, used on a commercial HMO or
            PPO program; abn_cms_r_131 — the Medicare Advance Beneficiary Notice of Noncoverage
            (form CMS-R-131), used on an Original Medicare program; medicaid_non_covered_agreement —
            the state Medicaid non-covered services agreement, used on a Medicaid program.
        notice_units: Fixed-format class — the billing units of straight-tip catheters the
            notice covers, in integer billing units; a whole number, no decimals.

    Returns:
        A dictionary receipt with: status ("signed" on success); continence_order_id (the new
        notice reference); notice_type (the form signed); item_code (always A4351); notice_units
        (integer billing units covered); notice_date (today, YYYY-MM-DD).
    """
    rid = ctx.make_id("cln_", continence_program_id, notice_type, notice_units)
    program = (ctx.find("continence_programs", continence_program_id=continence_program_id) or [{}])[0]
    today = ctx.now()[:10]
    ctx.create("continence_orders", rid, continence_order_id=rid, continence_program_id=continence_program_id,
               customer_id=program.get("customer_id"), event_type="continence_liability_notice_signed",
               notice_type=notice_type, item_code="A4351", notice_units=int(notice_units), notice_date=today)
    return str({"status": "signed", "continence_order_id": rid, "notice_type": notice_type,
                "item_code": "A4351", "notice_units": int(notice_units), "notice_date": today})


@tool(owner="agent", rw="write")
def post_hardship_waiver_d1a5476f(ctx: ToolContext, continence_program_id: str,
                                  original_continence_ledger_id: str, amount: float) -> str:
    """Post a financial-hardship waiver on a customer's Urology and Continence Supply Program.
    One call records one credit adjustment with reason hardship waiver, dated today, against the
    named billing posting, and lowers the customer's balance on the program by the amount given;
    the customer can then be told the waiver is on their account. Success is shown by the receipt
    below carrying the adjustment reference and the new balance.

    Args:
        continence_program_id: Id class — the reference number of the customer's Urology and
            Continence Supply Program the waiver is posted on, read from the program lookup.
        original_continence_ledger_id: Id class — the reference number of the billing posting the
            waiver is posted against, read from the program's billing history lookup.
        amount: Fixed-format class — the waiver amount in USD, a positive figure to 2 decimal
            places.

    Returns:
        A dictionary receipt with: status ("posted" on success); continence_ledger_id (the new
        adjustment reference); adjustment_reason (always hardship_waiver); amount (USD, 2 decimal
        places); posting_date (today, YYYY-MM-DD); patient_balance_due (the program balance in USD
        after the waiver, 2 decimal places).
    """
    rid = ctx.make_id("cbl_", continence_program_id, original_continence_ledger_id, amount)
    program = (ctx.find("continence_programs", continence_program_id=continence_program_id) or [{}])[0]
    today = ctx.now()[:10]
    value = round(float(amount), 2)
    ctx.create("continence_billing", rid, continence_ledger_id=rid, continence_program_id=continence_program_id,
               customer_id=program.get("customer_id"), event_type="continence_balance_adjustment",
               original_continence_ledger_id=original_continence_ledger_id,
               adjustment_reason="hardship_waiver", amount=value, posting_date=today)
    balance = round(float(program.get("patient_balance_due") or 0) - value, 2)
    ctx.update("continence_programs", continence_program_id, patient_balance_due=balance)
    return str({"status": "posted", "continence_ledger_id": rid, "adjustment_reason": "hardship_waiver",
                "amount": value, "posting_date": today, "patient_balance_due": balance})


@tool(owner="user", rw="write")
def accept_payment_plan_f3b8d099(ctx: ToolContext, continence_program_id: str, plan_months: int,
                                 monthly_amount_usd: float) -> str:
    """The customer personally accepts an interest-free payment plan for the balance of their own
    Urology and Continence Supply Program. One call records one approved payment plan, accepted
    today, with the number of monthly installments and the monthly installment given; the plan then
    stands on the program and the customer can be told it is in place. Success is shown by the
    receipt below carrying the plan reference.

    Args:
        continence_program_id: Id class — the reference number of the customer's Urology and
            Continence Supply Program the plan covers, as given by the agent from the program lookup.
        plan_months: Fixed-format class — the number of monthly installments of the plan, in integer
            months; a whole number, no decimals.
        monthly_amount_usd: Fixed-format class — the monthly installment in USD, a positive figure to
            2 decimal places.

    Returns:
        A dictionary receipt with: status ("accepted" on success); continence_request_id (the new plan
        reference); request_type (always payment_plan); request_status (always approved); plan_months
        (integer months); monthly_amount_usd (USD, 2 decimal places); received_at (the acceptance
        moment, as the clock gives it).
    """
    rid = ctx.make_id("cpp_", continence_program_id, plan_months, monthly_amount_usd)
    program = (ctx.find("continence_programs", continence_program_id=continence_program_id) or [{}])[0]
    moment = ctx.now()
    value = round(float(monthly_amount_usd), 2)
    ctx.create("continence_requests", rid, continence_request_id=rid, customer_id=program.get("customer_id"),
               continence_program_id=continence_program_id, request_type="payment_plan", request_status="approved",
               received_at=moment, plan_months=int(plan_months), monthly_amount_usd=value)
    return str({"status": "accepted", "continence_request_id": rid, "request_type": "payment_plan",
                "request_status": "approved", "plan_months": int(plan_months), "monthly_amount_usd": value,
                "received_at": moment})


@tool(owner="agent", rw="write")
def post_noncovered_charge_0f5c8cfb(ctx: ToolContext, continence_program_id: str, continence_shipment_id: str,
                                    item_code: str, amount: float) -> str:
    """Post a non-covered item charge on a customer's Urology and Continence Supply Program for
    catheters of one shipment that the customer's plan did not pay and that the customer agreed in
    writing to pay. One call records one patient charge of charge type non-covered item, dated today,
    against the named shipment, and raises the customer's balance on the program by the amount given;
    the customer can then be told the charge is on their account. Success is shown by the receipt
    below carrying the charge reference and the new balance.

    Args:
        continence_program_id: Id class — the reference number of the customer's Urology and
            Continence Supply Program the charge is posted on, read from the program lookup.
        continence_shipment_id: Id class — the reference number of the shipment the charge relates
            to, read from the program's shipment history lookup.
        item_code: Enum class — the HCPCS code of the catheters charged, exactly one of: A4351 — the
            charge is for straight-tip intermittent catheters; A4352 — the charge is for coude-tip
            intermittent catheters; A4353 — the charge is for closed-system intermittent catheter
            kits. It is part of the charge's reference.
        amount: Fixed-format class — the charge in USD, a positive figure to 2 decimal places.

    Returns:
        A dictionary receipt with: status ("posted" on success); continence_ledger_id (the new charge
        reference); charge_type (always non_covered_item); item_code (as given); amount (USD, 2 decimal
        places); posting_date (today, YYYY-MM-DD); patient_balance_due (the program balance in USD
        after the charge, 2 decimal places).
    """
    rid = ctx.make_id("cch_", continence_program_id, continence_shipment_id, item_code, amount)
    program = (ctx.find("continence_programs", continence_program_id=continence_program_id) or [{}])[0]
    today = ctx.now()[:10]
    value = round(float(amount), 2)
    ctx.create("continence_billing", rid, continence_ledger_id=rid, continence_program_id=continence_program_id,
               customer_id=program.get("customer_id"), event_type="continence_patient_charge",
               continence_shipment_id=continence_shipment_id, charge_type="non_covered_item", amount=value,
               posting_date=today)
    balance = round(float(program.get("patient_balance_due") or 0) + value, 2)
    ctx.update("continence_programs", continence_program_id, patient_balance_due=balance)
    return str({"status": "posted", "continence_ledger_id": rid, "charge_type": "non_covered_item",
                "item_code": item_code, "amount": value, "posting_date": today, "patient_balance_due": balance})


@tool(owner="agent", rw="write")
def post_return_credit_03d701bf(ctx: ToolContext, continence_program_id: str, original_continence_ledger_id: str,
                                amount: float) -> str:
    """Post a return credit on a customer's Urology and Continence Supply Program for returned
    catheters the warehouse accepted. One call records one credit adjustment with reason return
    credit, dated today, against the named billing posting, and lowers the customer's balance on the
    program by the amount given; the customer can then be told the credit is on their account.
    Success is shown by the receipt below carrying the adjustment reference and the new balance.

    Args:
        continence_program_id: Id class — the reference number of the customer's Urology and
            Continence Supply Program the credit is posted on, read from the program lookup.
        original_continence_ledger_id: Id class — the reference number of the billing posting the
            credit is posted against, read from the program's billing history lookup.
        amount: Fixed-format class — the credit in USD, a positive figure to 2 decimal places.

    Returns:
        A dictionary receipt with: status ("posted" on success); continence_ledger_id (the new
        adjustment reference); adjustment_reason (always return_credit); amount (USD, 2 decimal
        places); posting_date (today, YYYY-MM-DD); patient_balance_due (the program balance in USD
        after the credit, 2 decimal places).
    """
    rid = ctx.make_id("crc_", continence_program_id, original_continence_ledger_id, amount)
    program = (ctx.find("continence_programs", continence_program_id=continence_program_id) or [{}])[0]
    today = ctx.now()[:10]
    value = round(float(amount), 2)
    ctx.create("continence_billing", rid, continence_ledger_id=rid, continence_program_id=continence_program_id,
               customer_id=program.get("customer_id"), event_type="continence_balance_adjustment",
               original_continence_ledger_id=original_continence_ledger_id, adjustment_reason="return_credit",
               amount=value, posting_date=today)
    balance = round(float(program.get("patient_balance_due") or 0) - value, 2)
    ctx.update("continence_programs", continence_program_id, patient_balance_due=balance)
    return str({"status": "posted", "continence_ledger_id": rid, "adjustment_reason": "return_credit",
                "amount": value, "posting_date": today, "patient_balance_due": balance})

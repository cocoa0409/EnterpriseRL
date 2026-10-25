"""Hidden task tools for the Ostomy Supply Program difficulty (ostomy_supply_program_services).

Each tool performs one atomic write on an Ostomy Supply Program enrollment. The values passed
in are worked out by the caller from the published policies and the records; the tools never
judge eligibility, never aggregate history and never refuse a well-formed call.
"""

from erlbench import ToolContext, tool


@tool(owner="agent", rw="write")
def post_plan_denial_charge_c6cdcbbb(ctx: ToolContext, ostomy_program_id: str, ostomy_shipment_id: str,
                                     item_code: str, amount: float) -> str:
    """Post a non-covered item charge on an Ostomy Supply Program enrollment for barriers of one
    refill shipment that the customer's health plan declined to pay. The charge is added to the
    customer's balance on that enrollment and appears on the enrollment's billing history as a
    patient charge of the non-covered item type linked to the shipment it bills; the enrollment's
    balance due rises by the amount posted. The posting date is today's date.

    Args:
        ostomy_program_id: Id class — the reference number of the Ostomy Supply Program enrollment the charge is posted on, read from the enrollment lookup.
        ostomy_shipment_id: Id class — the reference number of the refill shipment record the charge bills, read from the shipment history lookup of that enrollment.
        item_code: Enum class — the HCPCS code of the item the charge is for, exactly as on the shipment record: A4414 when the item is a flat skin barrier with flange 4x4 in or smaller; A4407 when it is an extended-wear skin barrier with built-in convexity; A4409 when it is an extended-wear flat skin barrier; A4416 when it is a one-piece closed pouch with filter; A4423 when it is a two-piece closed pouch for a locking-flange barrier; A4424 when it is a one-piece drainable pouch; A4427 when it is a two-piece drainable pouch; A4431 when it is a one-piece urinary pouch with tap; A4434 when it is a two-piece urinary pouch with tap; A4406 when it is pectin-based paste per ounce; A4455 when it is adhesive remover per ounce; A4367 when it is an ostomy belt; A4357 when it is a bedside drainage bag.
        amount: Fixed-format class — the charge in USD, a positive amount with 2 decimal places (rounded to the cent by the caller); the tool stores it rounded to 2 decimal places.

    Returns:
        A dictionary receipt: status ("posted" when the charge was recorded), ostomy_ledger_id (the
        reference number of the new billing record), ostomy_program_id (the enrollment charged),
        ostomy_shipment_id (the shipment billed), item_code (the HCPCS code of the item charged),
        charge_type (always non_covered_item), amount
        (the USD amount posted, 2 decimal places), posting_date (YYYY-MM-DD) and patient_balance_due
        (the enrollment's balance due in USD after the charge, 2 decimal places).
    """
    amt = round(float(amount), 2)
    prog = ctx.find("ostomy_programs", ostomy_program_id=ostomy_program_id)
    cust = prog[0].get("customer_id") if prog else ""
    bal = round(float(prog[0].get("patient_balance_due") or 0) + amt, 2) if prog else amt
    rid = ctx.make_id("obl_", ostomy_program_id, ostomy_shipment_id, item_code, amt, "non_covered_item")
    day = ctx.now()[:10]
    ctx.create("ostomy_billing", rid, ostomy_ledger_id=rid, ostomy_program_id=ostomy_program_id,
               customer_id=cust, event_type="ostomy_patient_charge", ostomy_shipment_id=ostomy_shipment_id,
               charge_type="non_covered_item", amount=amt, posting_date=day)
    if prog:
        ctx.update("ostomy_programs", ostomy_program_id, patient_balance_due=bal)
    return str({"status": "posted", "ostomy_ledger_id": rid, "ostomy_program_id": ostomy_program_id,
                "ostomy_shipment_id": ostomy_shipment_id, "item_code": item_code, "charge_type": "non_covered_item",
                "amount": amt,
                "posting_date": day, "patient_balance_due": bal})


@tool(owner="agent", rw="write")
def post_hardship_waiver_31941945(ctx: ToolContext, ostomy_program_id: str, original_ostomy_ledger_id: str,
                                  amount: float) -> str:
    """Post a financial-hardship waiver on an Ostomy Supply Program enrollment against one
    patient-balance posting. The waiver is recorded as a balance adjustment of the hardship-waiver
    reason linked to the posting it adjusts, and the enrollment's balance due falls by the amount
    waived; the waiver then shows on the enrollment's billing history with today's posting date.

    Args:
        ostomy_program_id: Id class — the reference number of the Ostomy Supply Program enrollment the waiver is posted on, read from the enrollment lookup.
        original_ostomy_ledger_id: Id class — the reference number of the billing record (the patient-balance posting) the waiver adjusts, read from the billing history or the customer request lookup of that enrollment.
        amount: Fixed-format class — the amount waived in USD, a positive amount with 2 decimal places (rounded to the cent by the caller); the tool stores it rounded to 2 decimal places.

    Returns:
        A dictionary receipt: status ("posted" when the waiver was recorded), ostomy_ledger_id (the
        reference number of the new adjustment record), ostomy_program_id (the enrollment adjusted),
        original_ostomy_ledger_id (the posting adjusted), adjustment_reason (always hardship_waiver),
        amount (the USD amount waived, 2 decimal places), posting_date (YYYY-MM-DD) and
        patient_balance_due (the enrollment's balance due in USD after the waiver, 2 decimal places).
    """
    amt = round(float(amount), 2)
    prog = ctx.find("ostomy_programs", ostomy_program_id=ostomy_program_id)
    cust = prog[0].get("customer_id") if prog else ""
    bal = round(float(prog[0].get("patient_balance_due") or 0) - amt, 2) if prog else -amt
    rid = ctx.make_id("obl_", ostomy_program_id, original_ostomy_ledger_id, amt, "hardship_waiver")
    day = ctx.now()[:10]
    ctx.create("ostomy_billing", rid, ostomy_ledger_id=rid, ostomy_program_id=ostomy_program_id,
               customer_id=cust, event_type="ostomy_balance_adjustment",
               original_ostomy_ledger_id=original_ostomy_ledger_id, adjustment_reason="hardship_waiver",
               amount=amt, posting_date=day)
    if prog:
        ctx.update("ostomy_programs", ostomy_program_id, patient_balance_due=bal)
    return str({"status": "posted", "ostomy_ledger_id": rid, "ostomy_program_id": ostomy_program_id,
                "original_ostomy_ledger_id": original_ostomy_ledger_id, "adjustment_reason": "hardship_waiver",
                "amount": amt, "posting_date": day, "patient_balance_due": bal})


@tool(owner="user", rw="write")
def accept_payment_plan_7a7f8df9(ctx: ToolContext, ostomy_program_id: str, plan_months: int,
                                 monthly_amount_usd: float) -> str:
    """The customer personally accepts an interest-free payment plan for the balance on their own
    Ostomy Supply Program enrollment. Acceptance records an approved payment plan request on that
    enrollment carrying the number of monthly installments and the monthly installment the customer
    agreed to, logged with the moment of acceptance; the plan then shows in the enrollment's
    customer requests as approved.

    Args:
        ostomy_program_id: Id class — the reference number of the customer's Ostomy Supply Program enrollment the plan covers, as the representative reads it from the enrollment lookup and tells the customer.
        plan_months: Fixed-format class — the number of monthly installments in the plan, a whole number given as integer months (at least 1).
        monthly_amount_usd: Fixed-format class — the monthly installment in USD with 2 decimal places, as the representative states it; the tool stores it rounded to 2 decimal places.

    Returns:
        A dictionary receipt: status ("accepted" when the plan was recorded), ostomy_request_id (the
        reference number of the payment plan request), ostomy_program_id (the enrollment covered),
        request_status (always approved), plan_months (integer months), monthly_amount_usd (USD,
        2 decimal places) and received_at (the moment of acceptance, exactly as the system clock
        records it).
    """
    months = int(plan_months)
    monthly = round(float(monthly_amount_usd), 2)
    prog = ctx.find("ostomy_programs", ostomy_program_id=ostomy_program_id)
    cust = prog[0].get("customer_id") if prog else ""
    rid = ctx.make_id("orq_", ostomy_program_id, months, monthly, "payment_plan")
    stamp = ctx.now()
    ctx.create("ostomy_requests", rid, ostomy_request_id=rid, customer_id=cust,
               ostomy_program_id=ostomy_program_id, ostomy_shipment_id="", ostomy_ledger_id="",
               request_type="payment_plan", request_status="approved", received_at=stamp,
               requested_effective_date="", plan_months=months, monthly_amount_usd=monthly)
    return str({"status": "accepted", "ostomy_request_id": rid, "ostomy_program_id": ostomy_program_id,
                "request_status": "approved", "plan_months": months, "monthly_amount_usd": monthly,
                "received_at": stamp})




@tool(owner="agent", rw="write")
def ship_ostomy_refill_57098f77(ctx: ToolContext, ostomy_program_id: str, customer_id: str, coverage_id: str,
                                ostomy_order_id: str, previous_ostomy_shipment_id: str, item_code: str,
                                units: int, supply_days: int, billing_route: str, refill_confirmed_date: str) -> str:
    """Ship one refill package of one ostomy item on an Ostomy Supply Program enrollment, drawing the
    shipped billing units from one authorization grant. The refill is recorded on the enrollment's
    shipment history with today's ship date, standard ground shipping, the supply days it covers, how
    it is billed and the date the customer confirmed the refill; the enrollment's billing units still
    authorized to ship fall by the units shipped.

    Args:
        ostomy_program_id: Id class — the reference number of the Ostomy Supply Program enrollment the refill ships on, read from the enrollment lookup.
        customer_id: Id class — the reference number of the customer who holds the enrollment, read from the customer profile lookup.
        coverage_id: Id class — the reference number of the insurance coverage record the enrollment bills, read from the enrollment or coverage lookup; an empty string on the self-pay tier.
        ostomy_order_id: Id class — the reference number of the authorization grant record the refill draws its units from, read from the order and authorization lookup of that enrollment.
        previous_ostomy_shipment_id: Id class — the reference number of the enrollment's previous refill shipment record of the same item, read from the shipment history lookup; an empty string for a first fill.
        item_code: Enum class — the HCPCS code of the item shipped: A4414 when the item is a flat skin barrier with flange 4x4 in or smaller; A4407 when it is an extended-wear skin barrier with built-in convexity; A4409 when it is an extended-wear flat skin barrier; A4416 when it is a one-piece closed pouch with filter; A4423 when it is a two-piece closed pouch for a locking-flange barrier; A4424 when it is a one-piece drainable pouch; A4427 when it is a two-piece drainable pouch; A4431 when it is a one-piece urinary pouch with tap; A4434 when it is a two-piece urinary pouch with tap; A4406 when it is pectin-based paste per ounce; A4455 when it is adhesive remover per ounce; A4367 when it is an ostomy belt; A4357 when it is a bedside drainage bag.
        units: Fixed-format class — the billing units shipped, a whole number given as integer billing units (each barrier, pouch, belt or bedside drainage bag; per ounce of paste or adhesive remover); the physical pieces recorded equal the units.
        supply_days: Fixed-format class — the days of supply the refill covers, an integer number of calendar days that is a multiple of 30.
        billing_route: Enum class — how the shipped units are billed: payer_claim when the enrollment bills an insurance coverage and the refill is billed to that payer by claim; self_pay when the enrollment is on the self-pay tier and the customer is charged the cash price.
        refill_confirmed_date: Fixed-format class — the date the customer confirmed continued use and supply on hand for this refill, in YYYY-MM-DD format; an empty string when the tier requires no confirmation.

    Returns:
        A dictionary receipt: status ("shipped" when the refill was recorded), ostomy_shipment_id (the
        reference number of the new shipment record), ostomy_program_id, ostomy_order_id (the grant
        drawn), previous_ostomy_shipment_id (the previous refill named), item_code, units (integer billing units), supply_days (integer days), ship_date
        (YYYY-MM-DD), billing_route and authorized_units_remaining (the enrollment's integer billing
        units still authorized to ship after the refill).
    """
    n = int(units)
    days = int(supply_days)
    prog = ctx.find("ostomy_programs", ostomy_program_id=ostomy_program_id)
    cust = prog[0].get("customer_id") if prog else ""
    left = int(prog[0].get("authorized_units_remaining") or 0) - n if prog else -n
    rid = ctx.make_id("osh_", ostomy_program_id, customer_id, coverage_id, ostomy_order_id,
                      previous_ostomy_shipment_id, item_code, n, days, billing_route, refill_confirmed_date)
    day = ctx.now()[:10]
    ctx.create("ostomy_shipments", rid, ostomy_shipment_id=rid, ostomy_program_id=ostomy_program_id,
               customer_id=cust, event_type="ostomy_refill_shipment", ostomy_order_id=ostomy_order_id,
               item_code=item_code, units=n, pieces=n, supply_days=days, ship_date=day,
               shipping_method="standard", billing_route=billing_route,
               refill_confirmed_date=refill_confirmed_date)
    if prog:
        ctx.update("ostomy_programs", ostomy_program_id, authorized_units_remaining=left)
    return str({"status": "shipped", "ostomy_shipment_id": rid, "ostomy_program_id": ostomy_program_id,
                "ostomy_order_id": ostomy_order_id, "previous_ostomy_shipment_id": previous_ostomy_shipment_id,
                "item_code": item_code, "units": n, "supply_days": days,
                "ship_date": day, "billing_route": billing_route, "authorized_units_remaining": left})


@tool(owner="user", rw="write")
def sign_liability_notice_87444016(ctx: ToolContext, ostomy_program_id: str, item_code: str, notice_type: str,
                                   notice_units: int) -> str:
    """The customer personally signs an advance notice of financial liability for one ostomy item on
    their own Ostomy Supply Program enrollment, accepting that they may be billed for the stated
    number of billing units if their payer does not pay for them. The signed notice is recorded in
    the enrollment's order and authorization file with today's signing date, the form signed, the
    item and the units it covers.

    Args:
        ostomy_program_id: Id class — the reference number of the customer's Ostomy Supply Program enrollment the notice is for, as the representative reads it from the enrollment lookup and tells the customer.
        item_code: Enum class — the HCPCS code of the item the notice covers: A4414 when the item is a flat skin barrier with flange 4x4 in or smaller; A4407 when it is an extended-wear skin barrier with built-in convexity; A4409 when it is an extended-wear flat skin barrier; A4416 when it is a one-piece closed pouch with filter; A4423 when it is a two-piece closed pouch for a locking-flange barrier; A4424 when it is a one-piece drainable pouch; A4427 when it is a two-piece drainable pouch; A4431 when it is a one-piece urinary pouch with tap; A4434 when it is a two-piece urinary pouch with tap; A4406 when it is pectin-based paste per ounce; A4455 when it is adhesive remover per ounce; A4367 when it is an ostomy belt; A4357 when it is a bedside drainage bag.
        notice_type: Enum class — the notice form signed: plan_member_waiver when the enrollment is on a commercial plan tier that uses the plan's member waiver; abn_cms_r_131 when it is on the Original Medicare tier and the form is the Advance Beneficiary Notice of Noncoverage; medicaid_non_covered_agreement when it is on the Medicaid tier and the form is the non-covered service agreement.
        notice_units: Fixed-format class — the billing units the notice covers, a whole number given as integer billing units (each barrier, pouch, belt or bedside drainage bag; per ounce of paste or adhesive remover).

    Returns:
        A dictionary receipt: status ("signed" when the notice was recorded), ostomy_order_id (the
        reference number of the signed-notice record), ostomy_program_id, item_code, notice_type,
        notice_units (integer billing units) and notice_date (YYYY-MM-DD, the signing date).
    """
    n = int(notice_units)
    prog = ctx.find("ostomy_programs", ostomy_program_id=ostomy_program_id)
    cust = prog[0].get("customer_id") if prog else ""
    npi = prog[0].get("prescriber_npi") if prog else ""
    rid = ctx.make_id("oor_", ostomy_program_id, item_code, notice_type, n)
    day = ctx.now()[:10]
    ctx.create("ostomy_orders", rid, ostomy_order_id=rid, ostomy_program_id=ostomy_program_id, customer_id=cust,
               event_type="ostomy_liability_notice_signed", prescriber_npi=npi, item_code=item_code,
               notice_type=notice_type, notice_units=n, notice_date=day)
    return str({"status": "signed", "ostomy_order_id": rid, "ostomy_program_id": ostomy_program_id,
                "item_code": item_code, "notice_type": notice_type, "notice_units": n, "notice_date": day})


@tool(owner="agent", rw="write")
def post_expedite_charge_9c5d9761(ctx: ToolContext, ostomy_program_id: str, ostomy_shipment_id: str, item_code: str,
                                  amount: float) -> str:
    """Post an expedited shipping charge on an Ostomy Supply Program enrollment for one refill shipment
    the customer asked to have sent expedited. The charge is added to the customer's balance on that
    enrollment and appears on the enrollment's billing history as a patient charge of the expedited
    shipping type linked to the shipment; the enrollment's balance due rises by the amount posted. The
    posting date is today's date.

    Args:
        ostomy_program_id: Id class — the reference number of the Ostomy Supply Program enrollment the charge is posted on, read from the enrollment lookup.
        ostomy_shipment_id: Id class — the reference number of the expedited refill shipment record the charge relates to, read from the shipment history lookup of that enrollment.
        item_code: Enum class — the HCPCS code of the item on the expedited shipment: A4414 when the item is a flat skin barrier with flange 4x4 in or smaller; A4407 when it is an extended-wear skin barrier with built-in convexity; A4409 when it is an extended-wear flat skin barrier; A4416 when it is a one-piece closed pouch with filter; A4423 when it is a two-piece closed pouch for a locking-flange barrier; A4424 when it is a one-piece drainable pouch; A4427 when it is a two-piece drainable pouch; A4431 when it is a one-piece urinary pouch with tap; A4434 when it is a two-piece urinary pouch with tap; A4406 when it is pectin-based paste per ounce; A4455 when it is adhesive remover per ounce; A4367 when it is an ostomy belt; A4357 when it is a bedside drainage bag.
        amount: Fixed-format class — the charge in USD, a positive amount with 2 decimal places (rounded to the cent by the caller); the tool stores it rounded to 2 decimal places.

    Returns:
        A dictionary receipt: status ("posted" when the charge was recorded), ostomy_ledger_id (the
        reference number of the new billing record), ostomy_program_id, ostomy_shipment_id, item_code
        (the HCPCS code of the item on the shipment), charge_type (always expedited_shipping), amount
        (USD, 2 decimal places), posting_date (YYYY-MM-DD) and patient_balance_due (the enrollment's
        balance due in USD after the charge, 2 decimal places).
    """
    amt = round(float(amount), 2)
    prog = ctx.find("ostomy_programs", ostomy_program_id=ostomy_program_id)
    cust = prog[0].get("customer_id") if prog else ""
    bal = round(float(prog[0].get("patient_balance_due") or 0) + amt, 2) if prog else amt
    rid = ctx.make_id("obl_", ostomy_program_id, ostomy_shipment_id, item_code, amt, "expedited_shipping")
    day = ctx.now()[:10]
    ctx.create("ostomy_billing", rid, ostomy_ledger_id=rid, ostomy_program_id=ostomy_program_id,
               customer_id=cust, event_type="ostomy_patient_charge", ostomy_shipment_id=ostomy_shipment_id,
               charge_type="expedited_shipping", amount=amt, posting_date=day)
    if prog:
        ctx.update("ostomy_programs", ostomy_program_id, patient_balance_due=bal)
    return str({"status": "posted", "ostomy_ledger_id": rid, "ostomy_program_id": ostomy_program_id,
                "ostomy_shipment_id": ostomy_shipment_id, "item_code": item_code,
                "charge_type": "expedited_shipping", "amount": amt, "posting_date": day,
                "patient_balance_due": bal})


@tool(owner="agent", rw="write")
def post_reship_correction_64ee6975(ctx: ToolContext, ostomy_program_id: str, original_ostomy_ledger_id: str,
                                    amount: float) -> str:
    """Post a billing correction on an Ostomy Supply Program enrollment against one patient charge
    posted in error. The correction is recorded as a balance adjustment of the billing-correction
    reason linked to the charge it corrects, and the enrollment's balance due falls by the amount
    posted; it then shows on the enrollment's billing history with today's posting date.

    Args:
        ostomy_program_id: Id class — the reference number of the Ostomy Supply Program enrollment the correction is posted on, read from the enrollment lookup.
        original_ostomy_ledger_id: Id class — the reference number of the billing record (the patient charge) the correction adjusts, read from the billing history lookup of that enrollment.
        amount: Fixed-format class — the correction in USD, a positive amount with 2 decimal places (rounded to the cent by the caller); the tool stores it rounded to 2 decimal places.

    Returns:
        A dictionary receipt: status ("posted" when the correction was recorded), ostomy_ledger_id (the
        reference number of the new adjustment record), ostomy_program_id, original_ostomy_ledger_id,
        adjustment_reason (always billing_correction), amount (USD, 2 decimal places), posting_date
        (YYYY-MM-DD) and patient_balance_due (the enrollment's balance due in USD after the
        correction, 2 decimal places).
    """
    amt = round(float(amount), 2)
    prog = ctx.find("ostomy_programs", ostomy_program_id=ostomy_program_id)
    cust = prog[0].get("customer_id") if prog else ""
    bal = round(float(prog[0].get("patient_balance_due") or 0) - amt, 2) if prog else -amt
    rid = ctx.make_id("obl_", ostomy_program_id, original_ostomy_ledger_id, amt, "billing_correction")
    day = ctx.now()[:10]
    ctx.create("ostomy_billing", rid, ostomy_ledger_id=rid, ostomy_program_id=ostomy_program_id,
               customer_id=cust, event_type="ostomy_balance_adjustment",
               original_ostomy_ledger_id=original_ostomy_ledger_id, adjustment_reason="billing_correction",
               amount=amt, posting_date=day)
    if prog:
        ctx.update("ostomy_programs", ostomy_program_id, patient_balance_due=bal)
    return str({"status": "posted", "ostomy_ledger_id": rid, "ostomy_program_id": ostomy_program_id,
                "original_ostomy_ledger_id": original_ostomy_ledger_id, "adjustment_reason": "billing_correction",
                "amount": amt, "posting_date": day, "patient_balance_due": bal})

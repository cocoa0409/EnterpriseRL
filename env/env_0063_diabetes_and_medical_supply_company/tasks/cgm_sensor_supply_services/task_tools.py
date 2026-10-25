"""Hidden task tools for the cgm_sensor_supply_services difficulty (Larkfield Medical Supply).

Each tool performs one atomic write on a Continuous Glucose Monitoring Supply Program record
with values the agent has already worked out; no tool checks eligibility or computes a value.
"""

from erlbench import ToolContext, tool


@tool(owner="agent", rw="write")
def record_order_authorization_630fe26e(ctx: ToolContext, cgm_program_id: str, related_cgm_order_id: str,
                                        item_code: str, valid_from: str, valid_through: str,
                                        units_authorized: int) -> str:
    """Record an order-based authorization grant on a Continuous Glucose Monitoring Supply Program
    enrollment: Larkfield writes one authorization on the basis of the prescriber's written order
    (authorization basis written order, no payer reference), dated today as its decision date,
    covering the stated span, and credits the stated billing units to the enrollment's units still
    authorized to ship. On success the enrollment shows the new authorization in its prescription
    and authorization file and its units still authorized to ship rise by the units recorded.

    Args:
        cgm_program_id: Id class — the reference number of the CGM supply program enrollment the
            authorization belongs to, as returned by the CGM program lookup.
        related_cgm_order_id: Id class — the reference number of the written order the authorization
            rests on, as returned by the CGM prescription and authorization file lookup.
        item_code: Enum class — the HCPCS item the authorization covers; exactly one of:
            "A4239" when the authorization covers the CGM supply allowance (sensors, one unit per 30
            days of supply); "E2103" when it covers a CGM receiver or reader.
        valid_from: Fixed-format class — the first date the authorization covers, as a calendar date
            in YYYY-MM-DD format with no time or time zone.
        valid_through: Fixed-format class — the last date the authorization covers, as a calendar
            date in YYYY-MM-DD format with no time or time zone.
        units_authorized: Fixed-format class — the billing units the authorization carries, a
            non-negative integer in integer billing units, with no decimals.

    Returns:
        A confirmation sentence naming the new authorization's reference number (prefix "auth_"
        followed by 12 hexadecimal characters), the enrollment reference number, the item, the
        units recorded, the covered span and the enrollment's units still authorized to ship after
        the credit (a whole number). The presence of the authorization reference number indicates
        the authorization was recorded.
    """
    rid = ctx.make_id("auth_", cgm_program_id, related_cgm_order_id, item_code, valid_from, valid_through,
                      units_authorized)
    prog = ctx.find("cgm_programs", cgm_program_id=cgm_program_id)
    customer_id = prog[0].get("customer_id") if prog else ""
    ctx.create("cgm_orders", rid, cgm_order_id=rid, cgm_program_id=cgm_program_id, customer_id=customer_id,
               event_type="cgm_authorization_grant", related_cgm_order_id=related_cgm_order_id,
               order_reference="", pa_reference="", prescriber_npi="", item_code=item_code, order_date="",
               quantity_per_30_days=0, valid_from=valid_from, valid_through=valid_through,
               units_authorized=int(units_authorized), authorization_basis="written_order", request_priority="",
               request_date="", decision_date=ctx.now()[:10], denial_reason="", record_purpose="", visit_date="",
               visit_type="", notice_type="", notice_units=0, notice_date="")
    remaining = int((prog[0].get("authorized_units_remaining") if prog else 0) or 0) + int(units_authorized)
    if prog:
        ctx.update("cgm_programs", cgm_program_id, authorized_units_remaining=remaining)
    return (f"Authorization {rid} recorded on enrollment {cgm_program_id} for {item_code}: {int(units_authorized)} "
            f"unit(s), valid {valid_from} through {valid_through}; units still authorized to ship now {remaining}.")


@tool(owner="user", rw="write")
def sign_medicare_advance_notice_77a558d1(ctx: ToolContext, cgm_program_id: str, item_code: str,
                                          notice_units: int) -> str:
    """The customer personally signs the Medicare Advance Beneficiary Notice of Noncoverage (form
    CMS-R-131) for one item on their Continuous Glucose Monitoring Supply Program enrollment,
    accepting that they may owe for the stated billing units if Medicare does not pay. One call
    records one signed notice, dated today, in the enrollment's prescription and authorization
    file; on success the customer can see the signed notice listed with its item and units.

    Args:
        cgm_program_id: Id class — the reference number of the customer's CGM supply program
            enrollment, as the representative reads it from the CGM program lookup and gives it to
            the customer.
        item_code: Enum class — the HCPCS item the notice covers; exactly one of: "A4239" when the
            notice covers the CGM supply allowance (sensors); "E2103" when it covers a CGM receiver
            or reader.
        notice_units: Fixed-format class — the billing units the notice covers, a positive integer
            in integer billing units, with no decimals.

    Returns:
        A confirmation sentence naming the signed notice's reference number (prefix "abn_" followed
        by 12 hexadecimal characters), the enrollment reference number, the item, the units covered
        and the signing date in YYYY-MM-DD format. The presence of the notice reference number
        indicates the notice was signed and recorded.
    """
    rid = ctx.make_id("abn_", cgm_program_id, item_code, notice_units)
    prog = ctx.find("cgm_programs", cgm_program_id=cgm_program_id)
    customer_id = prog[0].get("customer_id") if prog else ""
    today = ctx.now()[:10]
    ctx.create("cgm_orders", rid, cgm_order_id=rid, cgm_program_id=cgm_program_id, customer_id=customer_id,
               event_type="cgm_liability_notice_signed", related_cgm_order_id="", order_reference="",
               pa_reference="", prescriber_npi="", item_code=item_code, order_date="", quantity_per_30_days=0,
               valid_from="", valid_through="", units_authorized=0, authorization_basis="", request_priority="",
               request_date="", decision_date="", denial_reason="", record_purpose="", visit_date="", visit_type="",
               notice_type="abn_cms_r_131", notice_units=int(notice_units), notice_date=today)
    return (f"Advance notice {rid} signed on enrollment {cgm_program_id} for {item_code}: "
            f"{int(notice_units)} unit(s), signed {today}.")


@tool(owner="agent", rw="write")
def record_model_change_authorization_2da97677(ctx: ToolContext, cgm_program_id: str, related_cgm_order_id: str,
                                               item_code: str, pa_reference: str, valid_from: str,
                                               valid_through: str, units_authorized: int) -> str:
    """Record an authorization grant for a new written order on a Continuous Glucose Monitoring
    Supply Program enrollment under the payer prior authorization already in force: Larkfield
    writes one authorization with basis payer prior authorization, carrying the stated payer PA
    reference, dated today as its decision date, covering the stated span, and credits the stated
    billing units to the enrollment's units still authorized to ship. On success the enrollment
    shows the new authorization, tied to the written order, in its prescription and authorization
    file, and its units still authorized to ship rise by the units recorded.

    Args:
        cgm_program_id: Id class — the reference number of the CGM supply program enrollment the
            authorization belongs to, as returned by the CGM program lookup.
        related_cgm_order_id: Id class — the reference number of the written order the authorization
            rests on, as returned by the CGM prescription and authorization file lookup.
        item_code: Enum class — the HCPCS item the authorization covers; exactly one of:
            "A4239" when the authorization covers the CGM supply allowance (sensors, one unit per 30
            days of supply); "E2103" when it covers a CGM receiver or reader.
        pa_reference: Verbatim class — the payer's prior authorization reference the authorization
            is recorded under, copied character for character from the payer authorization on file
            (verbatim).
        valid_from: Fixed-format class — the first date the authorization covers, as a calendar date
            in YYYY-MM-DD format with no time or time zone.
        valid_through: Fixed-format class — the last date the authorization covers, as a calendar
            date in YYYY-MM-DD format with no time or time zone.
        units_authorized: Fixed-format class — the billing units the authorization carries, a
            non-negative integer in integer billing units, with no decimals.

    Returns:
        A confirmation sentence naming the new authorization's reference number (prefix "auth_"
        followed by 12 hexadecimal characters), the enrollment reference number, the item, the
        payer PA reference, the units recorded, the covered span and the enrollment's units still
        authorized to ship after the credit (a whole number). The presence of the authorization
        reference number indicates the authorization was recorded.
    """
    rid = ctx.make_id("auth_", cgm_program_id, related_cgm_order_id, item_code, pa_reference, valid_from,
                      valid_through, units_authorized)
    prog = ctx.find("cgm_programs", cgm_program_id=cgm_program_id)
    customer_id = prog[0].get("customer_id") if prog else ""
    ctx.create("cgm_orders", rid, cgm_order_id=rid, cgm_program_id=cgm_program_id, customer_id=customer_id,
               event_type="cgm_authorization_grant", related_cgm_order_id=related_cgm_order_id,
               order_reference="", pa_reference=pa_reference, prescriber_npi="", item_code=item_code,
               order_date="", quantity_per_30_days=0, valid_from=valid_from, valid_through=valid_through,
               units_authorized=int(units_authorized), authorization_basis="payer_prior_authorization",
               request_priority="", request_date="", decision_date=ctx.now()[:10], denial_reason="",
               record_purpose="", visit_date="", visit_type="", notice_type="", notice_units=0, notice_date="")
    remaining = int((prog[0].get("authorized_units_remaining") if prog else 0) or 0) + int(units_authorized)
    if prog:
        ctx.update("cgm_programs", cgm_program_id, authorized_units_remaining=remaining)
    return (f"Authorization {rid} recorded on enrollment {cgm_program_id} for {item_code} under payer PA "
            f"{pa_reference}: {int(units_authorized)} unit(s), valid {valid_from} through {valid_through}; "
            f"units still authorized to ship now {remaining}.")


@tool(owner="user", rw="write")
def sign_plan_member_waiver_eca832b6(ctx: ToolContext, cgm_program_id: str, item_code: str,
                                     notice_units: int) -> str:
    """The customer personally signs their health plan's member waiver of liability for one item on
    their Continuous Glucose Monitoring Supply Program enrollment, accepting that they may owe for
    the stated billing units if the plan does not pay for them. One call records one signed waiver,
    dated today, in the enrollment's prescription and authorization file; on success the customer
    can see the signed waiver listed with its item and units.

    Args:
        cgm_program_id: Id class — the reference number of the customer's CGM supply program
            enrollment, as the representative reads it from the CGM program lookup and gives it to
            the customer.
        item_code: Enum class — the HCPCS item the waiver covers; exactly one of: "A4239" when the
            waiver covers the CGM supply allowance (sensors); "E2103" when it covers a CGM receiver
            or reader.
        notice_units: Fixed-format class — the billing units the waiver covers, a positive integer
            in integer billing units, with no decimals.

    Returns:
        A confirmation sentence naming the signed waiver's reference number (prefix "pmw_" followed
        by 12 hexadecimal characters), the enrollment reference number, the item, the units covered
        and the signing date in YYYY-MM-DD format. The presence of the waiver reference number
        indicates the waiver was signed and recorded.
    """
    rid = ctx.make_id("pmw_", cgm_program_id, item_code, notice_units)
    prog = ctx.find("cgm_programs", cgm_program_id=cgm_program_id)
    customer_id = prog[0].get("customer_id") if prog else ""
    today = ctx.now()[:10]
    ctx.create("cgm_orders", rid, cgm_order_id=rid, cgm_program_id=cgm_program_id, customer_id=customer_id,
               event_type="cgm_liability_notice_signed", order_reference="", pa_reference="", prescriber_npi="",
               item_code=item_code, order_date="", quantity_per_30_days=0, valid_from="", valid_through="",
               units_authorized=0, authorization_basis="", request_priority="", request_date="",
               decision_date="", denial_reason="", record_purpose="", visit_date="", visit_type="",
               notice_type="plan_member_waiver", notice_units=int(notice_units), notice_date=today)
    return (f"Plan member waiver {rid} signed on enrollment {cgm_program_id} for {item_code}: "
            f"{int(notice_units)} unit(s), signed {today}.")


@tool(owner="user", rw="write")
def accept_payment_plan_9d194c19(ctx: ToolContext, cgm_program_id: str, plan_months: int,
                                 monthly_amount_usd: float) -> str:
    """The customer accepts an interest-free payment plan offered on their Continuous Glucose
    Monitoring Supply Program enrollment: one call records one approved payment plan request,
    logged now, for the stated number of monthly installments of the stated amount. On success the
    customer can see the approved plan, its installment count and its monthly amount among the
    enrollment's requests.

    Args:
        cgm_program_id: Id class — the reference number of the customer's CGM supply program
            enrollment, as the representative reads it from the CGM program lookup and gives it to
            the customer.
        plan_months: Fixed-format class — the number of monthly installments, a positive integer
            in integer months, with no decimals.
        monthly_amount_usd: Fixed-format class — the amount of each monthly installment in USD, 2
            decimal places, with no currency symbol.

    Returns:
        A confirmation sentence naming the plan request's reference number (prefix "plan_" followed
        by 12 hexadecimal characters), the enrollment reference number, the number of installments,
        the monthly amount with 2 decimal places and the request status approved. The presence of
        the plan reference number indicates the plan was accepted and recorded.
    """
    rid = ctx.make_id("plan_", cgm_program_id, plan_months, monthly_amount_usd)
    prog = ctx.find("cgm_programs", cgm_program_id=cgm_program_id)
    customer_id = prog[0].get("customer_id") if prog else ""
    amount = round(float(monthly_amount_usd), 2)
    ctx.create("cgm_requests", rid, cgm_request_id=rid, customer_id=customer_id, cgm_program_id=cgm_program_id,
               request_type="payment_plan", request_status="approved", received_at=ctx.now(),
               requested_effective_date="", plan_months=int(plan_months), monthly_amount_usd=amount)
    return (f"Payment plan {rid} approved on enrollment {cgm_program_id}: {int(plan_months)} monthly "
            f"installment(s) of {amount:.2f} USD; status approved.")


@tool(owner="agent", rw="write")
def ship_sensor_refill_e9d57917(ctx: ToolContext, cgm_program_id: str, cgm_order_id: str,
                                previous_cgm_shipment_id: str, coverage_id: str, customer_id: str,
                                units: int, pieces: int, supply_days: int) -> str:
    """Ship one CGM sensor refill package on a Continuous Glucose Monitoring Supply Program
    enrollment: Larkfield records one refill shipment of the CGM supply allowance (A4239), shipped
    today by standard ground with the payer-claim billing route, drawing the stated billing units on
    the stated authorization, records today's date as the customer's refill confirmation, and
    debits the units from the enrollment's units still authorized to ship. On success the
    enrollment's shipment history shows the new package with its units, sensor count and days of
    supply, and its units still authorized to ship fall by the units shipped.

    Args:
        cgm_program_id: Id class — the reference number of the CGM supply program enrollment the
            refill ships on, as returned by the CGM program lookup.
        cgm_order_id: Id class — the reference number of the authorization grant the refill draws
            on, as returned by the CGM prescription and authorization file lookup or by the tool that
            recorded the authorization.
        previous_cgm_shipment_id: Id class — the reference number of the enrollment's latest earlier
            refill shipment of the item, as returned by the CGM shipment history lookup.
        coverage_id: Id class — the reference number of the coverage record the enrollment bills, as
            returned by the coverage lookup.
        customer_id: Id class — the reference number of the customer profile, as returned by the
            customer lookup.
        units: Fixed-format class — the billing units shipped, a positive integer in integer billing
            units, with no decimals.
        pieces: Fixed-format class — the physical sensors in the package, as an integer count of
            physical pieces, with no decimals.
        supply_days: Fixed-format class — the days of supply the package covers, in integer calendar
            days, multiple of 30, with no decimals.

    Returns:
        A confirmation sentence naming the new shipment's reference number (prefix "ship_" followed
        by 12 hexadecimal characters), the enrollment reference number, the units, pieces and days of
        supply shipped, the ship date in YYYY-MM-DD format and the enrollment's units still
        authorized to ship after the debit (a whole number). The presence of the shipment reference
        number indicates the refill was shipped and recorded.
    """
    rid = ctx.make_id("ship_", cgm_program_id, cgm_order_id, previous_cgm_shipment_id, units, pieces, supply_days)
    prog = ctx.find("cgm_programs", cgm_program_id=cgm_program_id)
    today = ctx.now()[:10]
    ctx.create("cgm_shipments", rid, cgm_shipment_id=rid, cgm_program_id=cgm_program_id, customer_id=customer_id,
               event_type="cgm_refill_shipment", cgm_order_id=cgm_order_id, item_code="A4239", units=int(units),
               pieces=int(pieces), supply_days=int(supply_days), ship_date=today, shipping_method="standard",
               billing_route="payer_claim", refill_confirmed_date=today, replacement_reason="",
               delivery_date="", pod_type="", rma_issue_date="", receipt_date="")
    remaining = int((prog[0].get("authorized_units_remaining") if prog else 0) or 0) - int(units)
    if prog:
        ctx.update("cgm_programs", cgm_program_id, authorized_units_remaining=remaining)
    return (f"Refill {rid} shipped on enrollment {cgm_program_id}: {int(units)} unit(s), {int(pieces)} sensor(s), "
            f"{int(supply_days)} days of supply, shipped {today}; units still authorized to ship now {remaining}.")

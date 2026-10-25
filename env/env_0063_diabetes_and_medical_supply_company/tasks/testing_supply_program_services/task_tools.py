"""Hidden task tools of the testing_supply_program_services difficulty (Blood Glucose Testing Supply Program).

Each tool performs one atomic write on a Blood Glucose Testing Supply Program record and is reached only
through the unlock/call meta-tools. No tool judges eligibility, prerequisites or amounts: the caller passes
the values the published policies determine, and the tool records them as given.
"""

from erlbench import ToolContext, tool


@tool(owner="agent", rw="write")
def issue_return_authorization_3dfb992f(ctx: ToolContext, bgm_program_id: str, original_bgm_shipment_id: str,
                                        item_code: str, units: int) -> str:
    """Issue a return authorization, with a prepaid return label, for unopened sealed units of one delivered
    shipment on a Blood Glucose Testing Supply Program enrollment. One call records one return authorization
    on the enrollment's shipment history, dated today, naming the original shipment, the item and the number
    of billing units the customer may send back; nothing is credited until the warehouse accepts the returned
    units. The customer can afterwards see the authorization and the units it covers on the enrollment.

    Args:
        bgm_program_id: Id class — the reference number of the Blood Glucose Testing Supply Program enrollment
            the shipment belongs to, as returned by the enrollment lookup.
        original_bgm_shipment_id: Id class — the reference number of the delivered shipment record, a refill or
            a replacement, that the sealed units came from, as returned by the shipment-history lookup.
        item_code: Enum class — the HCPCS code of the item being sent back: A4253 when the units are blood
            glucose test strips (one unit is 50 strips); A4259 when they are lancets (one unit is 100 lancets);
            A4256 when they are control solution; A4258 when they are a spring-powered lancing device; E0607
            when they are a home blood glucose meter.
        units: Fixed-format class — the number of billing units authorized for return, as an integer count of
            integer billing units; zero or negative values are not meaningful.

    Returns:
        A confirmation sentence naming the new return authorization reference number, the issue date in
        YYYY-MM-DD form, the item code, the integer billing units authorized and the original shipment
        reference number; its presence means the authorization is on the enrollment.
    """
    program = ctx.find("bgm_programs", bgm_program_id=bgm_program_id)
    customer_id = program[0].get("customer_id") if program else ""
    issued = ctx.now()[:10]
    rid = ctx.make_id("bgs_", bgm_program_id, original_bgm_shipment_id, item_code, int(units), issued)
    ctx.create("bgm_shipments", rid, bgm_shipment_id=rid, bgm_program_id=bgm_program_id, customer_id=customer_id,
               event_type="bgm_return_authorization", original_bgm_shipment_id=original_bgm_shipment_id,
               item_code=item_code, units=int(units), rma_issue_date=issued)
    return (f"Return authorization {rid} issued {issued} for {int(units)} unit(s) of {item_code} from shipment "
            f"{original_bgm_shipment_id}; a prepaid return label is on its way to the customer.")


@tool(owner="user", rw="write")
def sign_liability_notice_3f2fa265(ctx: ToolContext, bgm_program_id: str, item_code: str, notice_type: str,
                                   notice_units: int) -> str:
    """The customer personally signs the advance notice of financial liability for an item or quantity on
    their Blood Glucose Testing Supply Program enrollment that the payer is expected not to pay. One call
    records one signed notice on the enrollment's prescription and authorization file, dated today, with the
    notice form, the item and the number of billing units it covers; once signed, those units may be billed
    to the customer if the payer denies them. The customer sees the signed notice on the enrollment.

    Args:
        bgm_program_id: Id class — the reference number of the customer's Blood Glucose Testing Supply Program
            enrollment, as read to the customer by the representative from the enrollment lookup.
        item_code: Enum class — the HCPCS code of the item the notice covers: A4253 for blood glucose test
            strips (one unit is 50 strips); A4259 for lancets (one unit is 100 lancets); A4256 for control
            solution; A4258 for a spring-powered lancing device; E0607 for a home blood glucose meter.
        notice_type: Enum class — the notice form being signed: plan_member_waiver when the enrollment is on a
            commercial plan tier whose notice is the plan member waiver; abn_cms_r_131 when it is on the
            Original Medicare tier and the notice is the CMS Advance Beneficiary Notice of Noncoverage;
            medicaid_non_covered_agreement when it is on the Medicaid tier and the notice is the Medicaid
            non-covered services agreement.
        notice_units: Fixed-format class — the number of billing units the notice covers, as an integer count
            of integer billing units.

    Returns:
        A confirmation sentence naming the signed notice's reference number, the signing date in YYYY-MM-DD
        form, the notice form, the item code and the integer billing units covered; its presence means the
        notice is on the enrollment's file.
    """
    program = ctx.find("bgm_programs", bgm_program_id=bgm_program_id)
    customer_id = program[0].get("customer_id") if program else ""
    signed = ctx.now()[:10]
    rid = ctx.make_id("bgo_", bgm_program_id, item_code, notice_type, int(notice_units), signed)
    ctx.create("bgm_orders", rid, bgm_order_id=rid, bgm_program_id=bgm_program_id, customer_id=customer_id,
               event_type="bgm_liability_notice_signed", notice_type=notice_type, item_code=item_code,
               notice_units=int(notice_units), notice_date=signed)
    return (f"Liability notice {rid} ({notice_type}) signed {signed} for {int(notice_units)} unit(s) of "
            f"{item_code}.")


@tool(owner="agent", rw="write")
def ship_strip_refill_72890190(ctx: ToolContext, bgm_program_id: str, customer_id: str, bgm_order_id: str,
                               previous_bgm_shipment_id: str, coverage_id: str, units: int, supply_days: int,
                               billing_route: str, refill_confirmation: str) -> str:
    """Ship one refill package of blood glucose test strips (item A4253) on a Blood Glucose Testing Supply
    Program enrollment by standard ground shipping today. One call records the refill shipment on the
    enrollment's shipment history, drawing the given billing units from the named authorization grant, with
    50 test strips per unit as the package's pieces, the supply days it covers, how it is billed and the
    customer's confirmation date where one was given; the enrollment's billing units still authorized to ship
    are reduced by the units shipped. The customer can afterwards see the package on the shipment history.

    Args:
        bgm_program_id: Id class — the reference number of the Blood Glucose Testing Supply Program enrollment
            the refill ships on, as returned by the enrollment lookup.
        customer_id: Id class — the customer reference number of the enrollment holder, as returned by the
            customer profile lookup.
        bgm_order_id: Id class — the reference number of the authorization grant record for test strips the
            refill draws its units from, as returned by the prescription and authorization lookup.
        previous_bgm_shipment_id: Id class — the reference number of the enrollment's previous test-strip
            refill shipment that this refill follows, as returned by the shipment-history lookup; it is quoted
            on the receipt.
        coverage_id: Id class — the reference number of the insurance coverage record the enrollment bills, as
            returned by the coverage lookup; it is quoted on the receipt.
        units: Fixed-format class — the number of billing units of test strips shipped, as an integer count of
            integer billing units (one unit is 50 strips); the package's pieces, an integer count of physical
            pieces, are recorded as 50 strips for every unit.
        supply_days: Fixed-format class — the days of supply the refill covers, in integer calendar days,
            multiple of 30.
        billing_route: Enum class — how the shipped units are billed: payer_claim when the enrollment's tier
            bills a payer by claim; self_pay when the enrollment is on the self-pay tier and the units are
            charged to the customer at the cash price.
        refill_confirmation: Enum class — whether the customer's own confirmation is recorded with the refill:
            confirmed_today when the customer confirmed in this contact that they still use the strips and how
            many they have on hand, so today's date is recorded as the confirmation date; not_required when the
            enrollment's tier ships refills without a per-shipment confirmation, so no confirmation date is
            recorded.

    Returns:
        A confirmation sentence naming the new refill shipment reference number, the ship date in YYYY-MM-DD
        form, the integer billing units and pieces shipped, the supply days, the billing route, the
        authorization grant drawn on, the previous refill and coverage reference numbers, and the billing
        units still authorized to ship on the enrollment afterwards; its presence means the package shipped.
    """
    shipped = ctx.now()[:10]
    confirmed = shipped if refill_confirmation == "confirmed_today" else ""
    rid = ctx.make_id("bgs_", bgm_program_id, customer_id, bgm_order_id, previous_bgm_shipment_id, coverage_id,
                      int(units), int(supply_days), billing_route, refill_confirmation, shipped)
    ctx.create("bgm_shipments", rid, bgm_shipment_id=rid, bgm_program_id=bgm_program_id, customer_id=customer_id,
               event_type="bgm_refill_shipment", bgm_order_id=bgm_order_id, item_code="A4253", units=int(units),
               pieces=int(units) * 50, supply_days=int(supply_days), ship_date=shipped, shipping_method="standard",
               billing_route=billing_route, refill_confirmed_date=confirmed)
    program = ctx.find("bgm_programs", bgm_program_id=bgm_program_id)
    remaining = int((program[0].get("authorized_units_remaining") if program else 0) or 0) - int(units)
    ctx.update("bgm_programs", bgm_program_id, authorized_units_remaining=remaining)
    return (f"Strip refill {rid} shipped {shipped}: {int(units)} unit(s), {int(units) * 50} strips, "
            f"{int(supply_days)} days, billed {billing_route}, drawing on grant {bgm_order_id}, following refill "
            f"{previous_bgm_shipment_id}, coverage {coverage_id}; {remaining} unit(s) remain authorized.")


@tool(owner="agent", rw="write")
def ship_courtesy_reship_05d6f35c(ctx: ToolContext, bgm_program_id: str, original_bgm_shipment_id: str, units: int,
                                  shipping_method: str) -> str:
    """Send a no-charge courtesy reship of blood glucose test strips (item A4253) on a Blood Glucose Testing Supply
    Program enrollment for a refill package the carrier shows as delivered but the customer did not receive. One
    call records the replacement shipment on the enrollment's shipment history, shipped today against the named
    original refill with the reason delivered_not_received, 50 test strips per unit as its pieces; it draws no
    authorized units and is never billed. The customer can afterwards see the reship on the shipment history.

    Args:
        bgm_program_id: Id class — the reference number of the Blood Glucose Testing Supply Program enrollment, as
            returned by the enrollment lookup.
        original_bgm_shipment_id: Id class — the reference number of the refill shipment record the customer did not
            receive, as returned by the shipment-history lookup.
        units: Fixed-format class — the number of billing units of test strips reshipped, as an integer count of
            integer billing units (one unit is 50 strips); the package's pieces, an integer count of physical pieces,
            are recorded as 50 strips for every unit.
        shipping_method: Enum class — how the reship travels: standard when it goes by ordinary ground shipping;
            expedited_no_charge when the reship goes by two-day shipping that Larkfield pays for; expedited when the
            customer asked for two-day shipping and pays for it.

    Returns:
        A confirmation sentence naming the new reship reference number, the ship date in YYYY-MM-DD form, the integer
        billing units and pieces sent, the shipping method and the original refill reference number; its presence
        means the reship left the warehouse.
    """
    program = ctx.find("bgm_programs", bgm_program_id=bgm_program_id)
    customer_id = program[0].get("customer_id") if program else ""
    shipped = ctx.now()[:10]
    rid = ctx.make_id("bgs_", bgm_program_id, original_bgm_shipment_id, int(units), shipping_method, shipped)
    ctx.create("bgm_shipments", rid, bgm_shipment_id=rid, bgm_program_id=bgm_program_id, customer_id=customer_id,
               event_type="bgm_replacement_shipment", original_bgm_shipment_id=original_bgm_shipment_id,
               replacement_reason="delivered_not_received", item_code="A4253", units=int(units),
               pieces=int(units) * 50, ship_date=shipped, shipping_method=shipping_method)
    return (f"Courtesy reship {rid} shipped {shipped}: {int(units)} unit(s), {int(units) * 50} strips, "
            f"{shipping_method}, for refill {original_bgm_shipment_id}; no charge.")


@tool(owner="user", rw="write")
def accept_payment_plan_2bd91da1(ctx: ToolContext, bgm_program_id: str, plan_months: int,
                                 monthly_amount_usd: float) -> str:
    """The customer personally accepts an interest-free payment plan for the balance on their Blood Glucose Testing
    Supply Program enrollment. One call records one payment plan request on the enrollment, approved on the
    customer's acceptance and dated now, with the number of monthly installments and the monthly installment. The
    customer sees the approved plan on the enrollment.

    Args:
        bgm_program_id: Id class — the reference number of the customer's Blood Glucose Testing Supply Program
            enrollment, as read to the customer by the representative from the enrollment lookup.
        plan_months: Fixed-format class — the number of monthly installments, in integer months.
        monthly_amount_usd: Fixed-format class — the monthly installment in USD, 2 decimal places, already rounded
            to the cent before it is passed.

    Returns:
        A confirmation sentence naming the new payment plan request reference number, its status approved, the
        timestamp it was logged in the form returned by the system clock, the integer months and the monthly
        installment in USD to 2 decimal places; its presence means the plan is in place.
    """
    program = ctx.find("bgm_programs", bgm_program_id=bgm_program_id)
    customer_id = program[0].get("customer_id") if program else ""
    logged = ctx.now()
    rid = ctx.make_id("bgr_", bgm_program_id, int(plan_months), round(float(monthly_amount_usd), 2), logged)
    ctx.create("bgm_requests", rid, bgm_request_id=rid, customer_id=customer_id, bgm_program_id=bgm_program_id,
               request_type="payment_plan", request_status="approved",
               received_at=logged, requested_effective_date="", plan_months=int(plan_months),
               monthly_amount_usd=round(float(monthly_amount_usd), 2))
    return (f"Payment plan {rid} approved {logged}: {int(plan_months)} monthly installment(s) of "
            f"{round(float(monthly_amount_usd), 2):.2f} USD.")


@tool(owner="agent", rw="write")
def post_noncovered_charge_41a38519(ctx: ToolContext, bgm_program_id: str, bgm_shipment_id: str, item_code: str,
                                    amount: float) -> str:
    """Post a non-covered item patient charge on a Blood Glucose Testing Supply Program enrollment for the units of
    one shipment that the payer denied and a signed liability notice covers. One call records one patient charge of
    type non_covered_item against the named shipment, dated today, and adds its amount to the customer's balance on
    the enrollment. The customer sees the charge and the new balance on the enrollment's billing history.

    Args:
        bgm_program_id: Id class — the reference number of the Blood Glucose Testing Supply Program enrollment, as
            returned by the enrollment lookup.
        bgm_shipment_id: Id class — the reference number of the shipment record whose denied units are charged, as
            returned by the shipment-history or billing-history lookup.
        item_code: Enum class — the HCPCS code of the charged item: A4253 for blood glucose test strips (one unit is
            50 strips); A4259 for lancets (one unit is 100 lancets); A4256 for control solution; A4258 for a
            spring-powered lancing device; E0607 for a home blood glucose meter.
        amount: Fixed-format class — the charge in USD, 2 decimal places, already rounded to the cent before it is
            passed.

    Returns:
        A confirmation sentence naming the new charge reference number, the posting date in YYYY-MM-DD form, the
        item code, the amount in USD to 2 decimal places and the customer's balance on the enrollment afterwards in
        USD to 2 decimal places; its presence means the charge is posted.
    """
    posted = ctx.now()[:10]
    program = ctx.find("bgm_programs", bgm_program_id=bgm_program_id)
    customer_id = program[0].get("customer_id") if program else ""
    rid = ctx.make_id("bgb_", bgm_program_id, bgm_shipment_id, item_code, round(float(amount), 2), posted)
    ctx.create("bgm_billing", rid, bgm_ledger_id=rid, bgm_program_id=bgm_program_id, customer_id=customer_id,
               event_type="bgm_patient_charge", bgm_shipment_id=bgm_shipment_id, charge_type="non_covered_item",
               amount=round(float(amount), 2), posting_date=posted)
    balance = round(float((program[0].get("patient_balance_due") if program else 0) or 0) + round(float(amount), 2), 2)
    ctx.update("bgm_programs", bgm_program_id, patient_balance_due=balance)
    return (f"Non-covered charge {rid} posted {posted}: {item_code} {round(float(amount), 2):.2f} USD; "
            f"balance now {balance:.2f} USD.")


@tool(owner="agent", rw="write")
def post_hardship_waiver_f8410ea4(ctx: ToolContext, bgm_program_id: str, original_bgm_ledger_id: str,
                                  amount: float) -> str:
    """Post a hardship waiver balance adjustment on a Blood Glucose Testing Supply Program enrollment against the one
    posting named on the customer's approved hardship application. One call records one balance adjustment with
    the reason hardship_waiver against that posting, dated today, and takes its amount off the customer's balance
    on the enrollment. The customer sees the waiver and the new balance on the enrollment's billing history.

    Args:
        bgm_program_id: Id class — the reference number of the Blood Glucose Testing Supply Program enrollment, as
            returned by the enrollment lookup.
        original_bgm_ledger_id: Id class — the reference number of the billing record the waiver is posted against,
            the posting named on the approved hardship application, as returned by the request or billing lookup.
        amount: Fixed-format class — the waiver in USD, 2 decimal places, already rounded to the cent before it is
            passed.

    Returns:
        A confirmation sentence naming the new adjustment reference number, the posting date in YYYY-MM-DD form, the
        amount in USD to 2 decimal places, the posting it adjusts and the customer's balance on the enrollment
        afterwards in USD to 2 decimal places; its presence means the waiver is posted.
    """
    posted = ctx.now()[:10]
    program = ctx.find("bgm_programs", bgm_program_id=bgm_program_id)
    customer_id = program[0].get("customer_id") if program else ""
    rid = ctx.make_id("bgb_", bgm_program_id, original_bgm_ledger_id, round(float(amount), 2), posted)
    ctx.create("bgm_billing", rid, bgm_ledger_id=rid, bgm_program_id=bgm_program_id, customer_id=customer_id,
               event_type="bgm_balance_adjustment", original_bgm_ledger_id=original_bgm_ledger_id,
               adjustment_reason="hardship_waiver", amount=round(float(amount), 2), posting_date=posted)
    balance = round(float((program[0].get("patient_balance_due") if program else 0) or 0) - round(float(amount), 2), 2)
    ctx.update("bgm_programs", bgm_program_id, patient_balance_due=balance)
    return (f"Hardship waiver {rid} posted {posted}: {round(float(amount), 2):.2f} USD against {original_bgm_ledger_id}; "
            f"balance now {balance:.2f} USD.")

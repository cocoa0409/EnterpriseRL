"""Hidden task tools for insulin_pump_program_services (Larkfield Medical Supply, pump category).

Each tool performs one atomic write on the customer's insulin pump program records and keeps the
program's running totals (authorized units remaining, patient balance due) in step with the ledger
row it books. No tool checks eligibility, ownership, status or any prerequisite: those are decided
by the representative from the published policy and the records before the call.
"""

from erlbench import ToolContext, tool


class _Ledger:
    """Compute-only helpers shared by the tools below (no writes happen here)."""

    @staticmethod
    def program(ctx: ToolContext, pump_program_id: str) -> dict:
        rows = ctx.find("pump_programs", pump_program_id=pump_program_id)
        return rows[0] if rows else {}

    @staticmethod
    def adjustment(ctx: ToolContext, prefix: str, pump_program_id: str, original_pump_ledger_id: str,
                   reason: str, amount: float) -> dict:
        prog = _Ledger.program(ctx, pump_program_id)
        value = round(float(amount), 2)
        lid = ctx.make_id(prefix, pump_program_id, original_pump_ledger_id, reason, value)
        balance = round(float(prog.get("patient_balance_due") or 0) - value, 2)
        fields = dict(pump_ledger_id=lid, pump_program_id=pump_program_id, customer_id=prog.get("customer_id", ""),
                      event_type="pump_balance_adjustment", pump_shipment_id="",
                      original_pump_ledger_id=original_pump_ledger_id, claim_number="", submission_type="",
                      billed_amount=0.0, allowed_amount=0.0, payer_paid_amount=0.0, amount=value,
                      posting_date=ctx.now()[:10], denial_code="", appeal_level="", charge_type="",
                      payment_method="", adjustment_reason=reason, rental_month_number=0)
        return {"id": lid, "fields": fields, "balance": balance, "amount": value}


@tool(owner="agent", rw="write")
def ship_cartridge_refill_a415cb78(ctx: ToolContext, pump_program_id: str, customer_id: str, coverage_id: str,
                                   pump_order_id: str, previous_pump_shipment_id: str, item_code: str,
                                   units: int, supply_days: int, refill_confirmed_date: str,
                                   billing_route: str) -> str:
    """Ship one cartridge or reservoir refill package on an insulin pump program by standard ground
    carrier. The call books one refill shipment line for the cartridge or reservoir item, drawing the
    shipped billing units from the named authorization grant: the program's authorized units remaining
    go down by the units shipped, and the shipment line records the confirmation date the customer gave,
    the days of supply and the billing route. Each cartridge or reservoir is one billing unit and one
    physical piece. The customer sees a new refill shipment on the program with today's ship date.

    Args:
        pump_program_id: Id class — the reference number of the customer's insulin pump program, read from the pump program lookup.
        customer_id: Id class — the reference number of the customer who holds the program, read from the customer profile lookup.
        coverage_id: Id class — the reference number of the insurance coverage record the program bills, read from the pump program lookup or the coverage lookup; pass an empty string on the self-pay tier.
        pump_order_id: Id class — the reference number of the authorization grant record the refill draws on, read from the pump order lookup for the program.
        previous_pump_shipment_id: Id class — the reference number of the program's latest earlier refill shipment line of the same item, read from the pump shipments lookup; pass an empty string when the item has never shipped on the program.
        item_code: Enum class — the cartridge or reservoir item shipped: A4225 is the syringe-type cartridge used by Tandem t:slim X2, Tandem Mobi and Beta Bionics iLet pumps; A4232 is the reservoir used by the MiniMed 780G pump; E0784 is the pump itself, A4224 is the infusion-set supply and A4239 is the pump-integrated sensor allowance, none of which is a cartridge or reservoir line.
        units: Fixed-format class — the cartridges or reservoirs shipped, in integer billing units (one billing unit per cartridge or reservoir), which is also the integer count of physical pieces in the package, zero or more.
        supply_days: Fixed-format class — the days of supply the refill covers, in integer calendar days, multiple of 30.
        refill_confirmed_date: Fixed-format class — the calendar date the customer confirmed continued use and supply on hand for this refill, in YYYY-MM-DD format; pass an empty string only on a tier that requires no refill confirmation.
        billing_route: Enum class — how the shipped units are billed: payer_claim when the program bills an insurance coverage by claim; self_pay when the program is on the self-pay tier and the customer pays the Larkfield cash price.

    Returns:
        A dictionary receipt with: pump_shipment_id (string, the reference number of the new refill shipment line), item_code (string, the item shipped), units (integer, billing units shipped), supply_days (integer, days of supply), ship_date (string, YYYY-MM-DD, today's date), authorized_units_remaining (integer, the program's units still available after this refill) and status (string, the value shipped when the line is booked).
    """
    sid = ctx.make_id("psh_", pump_program_id, customer_id, coverage_id, pump_order_id, previous_pump_shipment_id, item_code,
                      units, supply_days, refill_confirmed_date, billing_route)
    prog = _Ledger.program(ctx, pump_program_id)
    today = ctx.now()[:10]
    ctx.create("pump_shipments", sid, pump_shipment_id=sid, pump_program_id=pump_program_id,
               customer_id=customer_id, event_type="pump_refill_shipment",
               pump_order_id=pump_order_id, original_pump_shipment_id="", item_code=item_code,
               units=int(units), pieces=int(units), supply_days=int(supply_days), ship_date=today,
               shipping_method="standard", billing_route=billing_route,
               refill_confirmed_date=refill_confirmed_date, replacement_reason="", delivery_date="",
               pod_type="", rma_issue_date="", receipt_date="", device_serial_number="")
    remaining = int(prog.get("authorized_units_remaining") or 0) - int(units)
    ctx.update("pump_programs", pump_program_id, authorized_units_remaining=remaining)
    return str({"pump_shipment_id": sid, "item_code": item_code, "units": int(units),
                "supply_days": int(supply_days), "ship_date": today,
                "authorized_units_remaining": remaining, "status": "shipped"})


@tool(owner="user", rw="write")
def sign_cartridge_liability_notice_61b55bc8(ctx: ToolContext, pump_program_id: str, related_pump_order_id: str,
                                             item_code: str, notice_type: str, notice_units: int) -> str:
    """The customer personally signs the tier's advance notice of financial liability for cartridges or
    reservoirs on their insulin pump program. The call records one signed notice on the program's order
    records for the item, against the authorization grant it is signed for, with the notice form and the
    billing units it covers, dated today; the customer
    becomes able to receive those units billable to them. The customer sees the signed notice listed on
    the program.

    Args:
        pump_program_id: Id class — the reference number of the customer's insulin pump program, as the representative reads it from the pump program lookup and passes it on.
        related_pump_order_id: Id class — the reference number of the authorization grant record for the item that the noticed units will draw on and that the notice is signed against, as the representative reads it from the pump order lookup and passes it on.
        item_code: Enum class — the item the notice covers: A4225 is the syringe-type cartridge used by Tandem t:slim X2, Tandem Mobi and Beta Bionics iLet pumps; A4232 is the reservoir used by the MiniMed 780G pump; E0784 is the pump itself, A4224 is the infusion-set supply and A4239 is the pump-integrated sensor allowance, none of which is a cartridge or reservoir line.
        notice_type: Enum class — the notice form signed: plan_member_waiver is the member waiver of a commercial HMO or PPO plan; abn_cms_r_131 is the Original Medicare Advance Beneficiary Notice of Noncoverage, form CMS-R-131; medicaid_non_covered_agreement is the state Medicaid non-covered service agreement.
        notice_units: Fixed-format class — the cartridges or reservoirs the notice covers, in integer billing units, one or more.

    Returns:
        A dictionary receipt with: pump_order_id (string, the reference number of the signed notice record), related_pump_order_id (string, the authorization grant it is signed against), item_code (string, the item covered), notice_type (string, the form signed), notice_units (integer, units covered), notice_date (string, YYYY-MM-DD, today's date) and status (string, the value signed when the notice is recorded).
    """
    oid = ctx.make_id("pnt_", pump_program_id, related_pump_order_id, item_code, notice_type, notice_units)
    prog = _Ledger.program(ctx, pump_program_id)
    today = ctx.now()[:10]
    ctx.create("pump_orders", oid, pump_order_id=oid, pump_program_id=pump_program_id,
               customer_id=prog.get("customer_id", ""), event_type="pump_liability_notice_signed",
               related_pump_order_id=related_pump_order_id, order_reference="", pa_reference="",
               prescriber_npi="", item_code=item_code, notice_type=notice_type, notice_units=int(notice_units),
               notice_date=today)
    return str({"pump_order_id": oid, "related_pump_order_id": related_pump_order_id,
                "item_code": item_code, "notice_type": notice_type,
                "notice_units": int(notice_units), "notice_date": today, "status": "signed"})


@tool(owner="agent", rw="write")
def post_hardship_waiver_2af40412(ctx: ToolContext, pump_program_id: str, original_pump_ledger_id: str,
                                  amount: float) -> str:
    """Post a financial-hardship waiver on an insulin pump program against the one patient-balance posting
    an approved hardship application names. The call books one balance adjustment with reason
    hardship_waiver against that posting, dated today, and lowers the program's patient balance due by the
    amount. The customer sees the waiver on the program ledger and a lower balance.

    Args:
        pump_program_id: Id class — the reference number of the customer's insulin pump program, read from the pump program lookup.
        original_pump_ledger_id: Id class — the reference number of the billing record the waiver adjusts, read from the pump billing lookup or from the hardship application on the pump requests lookup.
        amount: Fixed-format class — the waiver in USD, a positive amount with 2 decimal places, as the governing policy rounds it.

    Returns:
        A dictionary receipt with: pump_ledger_id (string, the reference number of the new adjustment record), adjustment_reason (string, hardship_waiver), amount (number, USD with 2 decimal places), posting_date (string, YYYY-MM-DD, today's date), patient_balance_due (number, USD with 2 decimal places, the program balance after the waiver) and status (string, the value posted when the adjustment is booked).
    """
    adj = _Ledger.adjustment(ctx, "phw_", pump_program_id, original_pump_ledger_id, "hardship_waiver", amount)
    ctx.create("pump_billing", adj["id"], **adj["fields"])
    ctx.update("pump_programs", pump_program_id, patient_balance_due=adj["balance"])
    return str({"pump_ledger_id": adj["id"], "adjustment_reason": "hardship_waiver", "amount": adj["amount"],
                "posting_date": adj["fields"]["posting_date"], "patient_balance_due": adj["balance"],
                "status": "posted"})


@tool(owner="agent", rw="write")
def reverse_unsupported_liability_charge_60bc70aa(ctx: ToolContext, pump_program_id: str,
                                                  original_pump_ledger_id: str, amount: float) -> str:
    """Reverse the part of a non-covered item patient charge on an insulin pump program that the charge
    may not carry. The call books one balance adjustment with reason billing_correction against that
    patient charge, dated today, and lowers the program's patient balance due by the amount reversed. The
    customer sees the correction on the program ledger and a lower balance.

    Args:
        pump_program_id: Id class — the reference number of the customer's insulin pump program, read from the pump program lookup.
        original_pump_ledger_id: Id class — the reference number of the non-covered item patient charge being corrected, read from the pump billing lookup.
        amount: Fixed-format class — the amount reversed in USD, a positive amount with 2 decimal places, as the governing policy rounds it.

    Returns:
        A dictionary receipt with: pump_ledger_id (string, the reference number of the new adjustment record), adjustment_reason (string, billing_correction), amount (number, USD with 2 decimal places), posting_date (string, YYYY-MM-DD, today's date), patient_balance_due (number, USD with 2 decimal places, the program balance after the correction) and status (string, the value posted when the adjustment is booked).
    """
    adj = _Ledger.adjustment(ctx, "prv_", pump_program_id, original_pump_ledger_id, "billing_correction", amount)
    ctx.create("pump_billing", adj["id"], **adj["fields"])
    ctx.update("pump_programs", pump_program_id, patient_balance_due=adj["balance"])
    return str({"pump_ledger_id": adj["id"], "adjustment_reason": "billing_correction", "amount": adj["amount"],
                "posting_date": adj["fields"]["posting_date"], "patient_balance_due": adj["balance"],
                "status": "posted"})


@tool(owner="agent", rw="write")
def correct_remittance_posting_ab84bf6f(ctx: ToolContext, pump_program_id: str, original_pump_ledger_id: str,
                                        amount: float) -> str:
    """Correct the patient responsibility a payer remittance posting placed on an insulin pump program's
    balance. The call books one balance adjustment with reason billing_correction against that remittance
    posting, dated today, and lowers the program's patient balance due by the amount corrected. The
    customer sees the correction on the program ledger and a lower balance.

    Args:
        pump_program_id: Id class — the reference number of the customer's insulin pump program, read from the pump program lookup.
        original_pump_ledger_id: Id class — the reference number of the remittance posting being corrected, read from the pump billing lookup.
        amount: Fixed-format class — the amount corrected in USD, a positive amount with 2 decimal places, as the governing policy rounds it.

    Returns:
        A dictionary receipt with: pump_ledger_id (string, the reference number of the new adjustment record), adjustment_reason (string, billing_correction), amount (number, USD with 2 decimal places), posting_date (string, YYYY-MM-DD, today's date), patient_balance_due (number, USD with 2 decimal places, the program balance after the correction) and status (string, the value posted when the adjustment is booked).
    """
    adj = _Ledger.adjustment(ctx, "prc_", pump_program_id, original_pump_ledger_id, "billing_correction", amount)
    ctx.create("pump_billing", adj["id"], **adj["fields"])
    ctx.update("pump_programs", pump_program_id, patient_balance_due=adj["balance"])
    return str({"pump_ledger_id": adj["id"], "adjustment_reason": "billing_correction", "amount": adj["amount"],
                "posting_date": adj["fields"]["posting_date"], "patient_balance_due": adj["balance"],
                "status": "posted"})


@tool(owner="agent", rw="write")
def ship_infusion_set_refill_1f98af27(ctx: ToolContext, pump_program_id: str, customer_id: str, coverage_id: str,
                                      pump_order_id: str, previous_pump_shipment_id: str, units: int,
                                      pieces: int, supply_days: int, refill_confirmed_date: str,
                                      billing_route: str) -> str:
    """Ship one infusion-set refill package (A4224 infusion catheter supplies) on an insulin pump program by
    standard ground carrier. The call books one refill shipment line drawing the billing units from the
    named authorization grant: the program's authorized units remaining go down by the billing units, and
    the line records the number of infusion sets in the package, the days of supply, the confirmation
    date and the billing route. The customer sees a new infusion-set shipment with today's ship date.

    Args:
        pump_program_id: Id class — the reference number of the customer's insulin pump program, read from the pump program lookup.
        customer_id: Id class — the reference number of the customer who holds the program, read from the customer profile lookup.
        coverage_id: Id class — the reference number of the insurance coverage record the program bills, read from the pump program lookup or the coverage lookup; pass an empty string on the self-pay tier.
        pump_order_id: Id class — the reference number of the infusion-set authorization grant record the refill draws on, read from the pump order lookup for the program.
        previous_pump_shipment_id: Id class — the reference number of the program's latest earlier refill shipment line of the same item, read from the pump shipments lookup; pass an empty string when the item has never shipped on the program.
        units: Fixed-format class — the A4224 billing units shipped, in integer billing units where one unit is one week of infusion catheter supplies.
        pieces: Fixed-format class — the infusion sets in the package, as an integer count of physical pieces.
        supply_days: Fixed-format class — the days of supply the refill covers, in integer calendar days, multiple of 30.
        refill_confirmed_date: Fixed-format class — the calendar date the customer confirmed continued use and supply on hand for this refill, in YYYY-MM-DD format; pass an empty string only on a tier that requires no refill confirmation.
        billing_route: Enum class — how the shipped units are billed: payer_claim when the program bills an insurance coverage by claim; self_pay when the program is on the self-pay tier and the customer pays the Larkfield cash price.

    Returns:
        A dictionary receipt with: pump_shipment_id (string, the reference number of the new refill shipment line), units (integer, billing units shipped), pieces (integer, infusion sets shipped), supply_days (integer, days of supply), ship_date (string, YYYY-MM-DD, today's date), authorized_units_remaining (integer, the program's units still available after this refill) and status (string, the value shipped when the line is booked).
    """
    sid = ctx.make_id("pss_", pump_program_id, customer_id, coverage_id, pump_order_id, previous_pump_shipment_id, units,
                      pieces, supply_days, refill_confirmed_date, billing_route)
    prog = _Ledger.program(ctx, pump_program_id)
    today = ctx.now()[:10]
    ctx.create("pump_shipments", sid, pump_shipment_id=sid, pump_program_id=pump_program_id,
               customer_id=customer_id, event_type="pump_refill_shipment",
               pump_order_id=pump_order_id, original_pump_shipment_id="", item_code="A4224",
               units=int(units), pieces=int(pieces), supply_days=int(supply_days), ship_date=today,
               shipping_method="standard", billing_route=billing_route,
               refill_confirmed_date=refill_confirmed_date, replacement_reason="", delivery_date="",
               pod_type="", rma_issue_date="", receipt_date="", device_serial_number="")
    remaining = int(prog.get("authorized_units_remaining") or 0) - int(units)
    ctx.update("pump_programs", pump_program_id, authorized_units_remaining=remaining)
    return str({"pump_shipment_id": sid, "units": int(units), "pieces": int(pieces),
                "supply_days": int(supply_days), "ship_date": today,
                "authorized_units_remaining": remaining, "status": "shipped"})


@tool(owner="user", rw="write")
def accept_payment_plan_163cafb9(ctx: ToolContext, pump_program_id: str, plan_months: int,
                                 monthly_amount_usd: float) -> str:
    """The customer personally accepts an interest-free payment plan for the balance on their insulin pump
    program. The call records one payment plan request on the program in approved status, received now,
    with the number of monthly installments and the monthly installment; the balance the plan covers is
    then paid in those installments. The customer sees the approved plan on their program.

    Args:
        pump_program_id: Id class — the reference number of the customer's insulin pump program, as the representative reads it from the pump program lookup and passes it on.
        plan_months: Fixed-format class — the number of monthly installments, in integer months, one or more.
        monthly_amount_usd: Fixed-format class — the monthly installment in USD, a positive amount with 2 decimal places, as the governing policy rounds it.

    Returns:
        A dictionary receipt with: pump_request_id (string, the reference number of the payment plan request), request_type (string, payment_plan), request_status (string, approved), plan_months (integer, installments), monthly_amount_usd (number, USD with 2 decimal places), received_at (string, the timestamp the plan was recorded) and status (string, the value accepted when the plan is recorded).
    """
    rid = ctx.make_id("ppl_", pump_program_id, plan_months, monthly_amount_usd)
    prog = _Ledger.program(ctx, pump_program_id)
    stamp = ctx.now()
    value = round(float(monthly_amount_usd), 2)
    ctx.create("pump_requests", rid, pump_request_id=rid, customer_id=prog.get("customer_id", ""),
               pump_program_id=pump_program_id, pump_shipment_id="", pump_ledger_id="",
               request_type="payment_plan", request_status="approved", received_at=stamp,
               requested_effective_date="", plan_months=int(plan_months), monthly_amount_usd=value)
    return str({"pump_request_id": rid, "request_type": "payment_plan", "request_status": "approved",
                "plan_months": int(plan_months), "monthly_amount_usd": value, "received_at": stamp,
                "status": "accepted"})


@tool(owner="agent", rw="write")
def post_non_covered_item_charge_86d5d568(ctx: ToolContext, pump_program_id: str, pump_shipment_id: str,
                                          item_code: str, amount: float) -> str:
    """Post a non-covered item patient charge on an insulin pump program for one shipment whose units the
    payer denied and the customer's signed liability notice covers. The call books one patient charge of
    charge type non_covered_item for that shipment, dated today, and raises the program's patient balance
    due by the amount. The customer sees the charge on the program ledger and a higher balance.

    Args:
        pump_program_id: Id class — the reference number of the customer's insulin pump program, read from the pump program lookup.
        pump_shipment_id: Id class — the reference number of the refill shipment line the charge relates to, read from the pump shipments lookup.
        item_code: Enum class — the item of that shipment line the charge is for: A4225 is the syringe-type cartridge used by Tandem t:slim X2, Tandem Mobi and Beta Bionics iLet pumps; A4232 is the reservoir used by the MiniMed 780G pump; E0784 is the pump itself; A4224 is the infusion-set supply; A4239 is the pump-integrated sensor allowance.
        amount: Fixed-format class — the charge in USD, a positive amount with 2 decimal places, as the governing policy rounds it.

    Returns:
        A dictionary receipt with: pump_ledger_id (string, the reference number of the new patient charge), charge_type (string, non_covered_item), amount (number, USD with 2 decimal places), posting_date (string, YYYY-MM-DD, today's date), patient_balance_due (number, USD with 2 decimal places, the program balance after the charge) and status (string, the value posted when the charge is booked).
    """
    prog = _Ledger.program(ctx, pump_program_id)
    value = round(float(amount), 2)
    lid = ctx.make_id("pnc_", pump_program_id, pump_shipment_id, item_code, value)
    today = ctx.now()[:10]
    balance = round(float(prog.get("patient_balance_due") or 0) + value, 2)
    ctx.create("pump_billing", lid, pump_ledger_id=lid, pump_program_id=pump_program_id,
               customer_id=prog.get("customer_id", ""), event_type="pump_patient_charge",
               pump_shipment_id=pump_shipment_id, original_pump_ledger_id="", claim_number="",
               submission_type="", billed_amount=0.0, allowed_amount=0.0, payer_paid_amount=0.0,
               amount=value, posting_date=today, denial_code="", appeal_level="",
               charge_type="non_covered_item", payment_method="", adjustment_reason="", rental_month_number=0)
    ctx.update("pump_programs", pump_program_id, patient_balance_due=balance)
    return str({"pump_ledger_id": lid, "charge_type": "non_covered_item", "amount": value,
                "posting_date": today, "patient_balance_due": balance, "status": "posted"})

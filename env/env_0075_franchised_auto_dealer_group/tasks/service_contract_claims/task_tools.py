"""Hidden task tools of the service_contract_claims difficulty (category vsc).

Each tool performs one atomic write on a Kessler Shield service contract record set and
nothing else; every figure it books is passed in by the caller.
"""

from erlbench import ToolContext, tool


class _Fmt:
    """Format helpers shared by the tools (not tools themselves)."""

    GROUPS = ("engine", "transmission", "drive_axle", "cooling", "fuel_system", "electrical", "air_conditioning",
              "steering", "suspension", "brakes", "high_tech_electronics", "seals_and_gaskets")
    METHODS = ("flat_free_look", "flat_deal_unwound", "pro_rata")

    @staticmethod
    def cents(x):
        """Round a money figure to the cent, half away from zero, without binary-float rounding."""
        v = float(x)
        text = "%.9f" % abs(v)
        whole, frac = text.split(".")
        n = int(whole) * 100 + int(frac[:2]) + (1 if int(frac[2]) >= 5 else 0)
        return (-n if v < 0 else n) / 100.0

    @staticmethod
    def is_date(s):
        t = str(s)
        return (len(t) == 10 and t[4] == "-" and t[7] == "-" and (t[:4] + t[5:7] + t[8:]).isdigit()
                and 1 <= int(t[5:7]) <= 12 and 1 <= int(t[8:]) <= 31)


@tool(owner="agent", rw="write")
def reimburse_waiting_denial_repair_5808cf06(ctx: ToolContext, vsc_contract_id: str, claim_number: str,
                                            repair_order_number: str, component_group: str,
                                            odometer: int, amount: float) -> str:
    """Pay a Kessler Shield service contract holder back for a covered component repair the holder already paid the store for on customer pay after the contract had denied that claim line. One call books one paid component-repair claim line on the contract under the given claim number, repair order and component group, dated today, carrying the repair-order odometer and the reimbursement total as one amount (the labor-hour, labor-rate, parts and deductible breakdown fields of the line are left at zero because the line records a reimbursement total), and raises the contract's claims-paid total by that amount. The paid line is visible at once on the contract's claim history and counts against the contract's aggregate claim limit.

    Args:
        vsc_contract_id: Id class — the service contract record identifier of the holder's Kessler Shield contract, as returned by the service contract lookup.
        claim_number: Verbatim class — the claim authorization number exactly as it appears on the contract's denied claim line in the claim history, copied character for character with no change to letters, digits or hyphens (verbatim).
        repair_order_number: Verbatim class — the repair order number exactly as it appears on the contract's denied claim line and on the store's repair-order lines, copied character for character including its spacing (verbatim).
        component_group: Enum class — the component group of the repaired failure, written exactly as one of: engine (internally lubricated engine parts), transmission (transmission or transfer case), drive_axle (front or rear drive axle assembly), cooling (water pump, radiator or thermostat), fuel_system (fuel pump, injectors or pressure regulator), electrical (alternator, starter, power window or lock motors, wiring harnesses), air_conditioning (compressor, condenser or evaporator), steering (steering gear, rack or power steering pump), suspension (control arms, ball joints or bushings), brakes (master cylinder, calipers or ABS module), high_tech_electronics (infotainment, navigation, camera or driver-assist modules), seals_and_gaskets (seals and gaskets of covered components), not_applicable (not accepted by this action; it marks benefit and refund entries only).
        odometer: Fixed-format class — the odometer on the repair order, in integer miles with no separators.
        amount: Fixed-format class — the reimbursement total paid to the holder, in USD with 2 decimal places (half-up to the cent), greater than 0.00.

    Returns:
        A confirmation string naming the new claim line reference (an opaque id), the contract, the claim number and the amount paid in USD with 2 decimal places; its presence means the paid line was booked and the contract's claims-paid total was raised by that amount.
    """
    if float(amount) <= 0 or int(odometer) < 0 or component_group not in _Fmt.GROUPS:
        return "Error: amount must be a USD figure above 0.00, odometer whole miles of 0 or more, and component_group one of the component groups."
    amt = _Fmt.cents(amount)
    rid = ctx.make_id("vsl_", vsc_contract_id, claim_number, repair_order_number, component_group, odometer, amt)
    contract = ctx.find("vsc_contracts", vsc_contract_id=vsc_contract_id)
    holder = contract[0].get("customer_id") if contract else ""
    paid_before = _Fmt.cents(contract[0].get("claims_paid_total") or 0) if contract else 0.0
    ctx.create("vsc_ledger", rid, vsc_entry_id=rid, vsc_contract_id=vsc_contract_id, customer_id=holder,
               event_type="vsc_claim_paid", entry_date=ctx.now()[:10], claim_number=claim_number,
               repair_order_number=repair_order_number, claim_line_type="component_repair",
               component_group=component_group, odometer=int(odometer), labor_hours=0.0,
               labor_rate_paid=0.0, parts_amount=0.0, deductible_applied=0.0, days=0, amount=amt,
               denial_reason="not_applicable", cancel_method="not_applicable",
               refund_payee="not_applicable", source_entry_id="")
    ctx.update("vsc_contracts", vsc_contract_id, claims_paid_total=_Fmt.cents(paid_before + amt))
    return (f"Claim line {rid} booked on contract {vsc_contract_id}: claim {claim_number}, "
            f"reimbursement paid {amt:.2f} USD.")


@tool(owner="agent", rw="write")
def pay_claim_rental_line_3f5378a0(ctx: ToolContext, vsc_contract_id: str, claim_number: str,
                                  repair_order_number: str, odometer: int, days: int, amount: float) -> str:
    """Pay the rental benefit of an authorized Kessler Shield claim. One call books one paid rental claim line on the contract under the given claim number and repair order, dated today, recording the rental days paid, the repair-order odometer and the rental amount, with no deductible, and raises the contract's claims-paid total by that amount. The paid rental line is visible at once on the contract's claim history and counts against the contract's aggregate claim limit.

    Args:
        vsc_contract_id: Id class — the service contract record identifier of the holder's Kessler Shield contract, as returned by the service contract lookup.
        claim_number: Verbatim class — the claim authorization number exactly as it appears on the claim's component-repair line in the contract's claim history, copied character for character (verbatim).
        repair_order_number: Verbatim class — the repair order number exactly as it appears on the claim's component-repair line, copied character for character including its spacing (verbatim).
        odometer: Fixed-format class — the odometer on the repair order, in integer miles with no separators.
        days: Fixed-format class — the rental days paid on this line, in integer days, 1 or more.
        amount: Fixed-format class — the rental amount paid, in USD with 2 decimal places (half-up to the cent), greater than 0.00.

    Returns:
        A confirmation string naming the new rental line reference (an opaque id), the contract, the claim number, the days paid and the amount paid in USD with 2 decimal places; its presence means the rental line was booked and the contract's claims-paid total was raised by that amount.
    """
    if float(amount) <= 0 or int(days) < 1 or int(odometer) < 0:
        return "Error: amount must be a USD figure above 0.00, days a whole number of 1 or more, and odometer whole miles of 0 or more."
    amt = _Fmt.cents(amount)
    rid = ctx.make_id("vsl_", vsc_contract_id, claim_number, repair_order_number, odometer, days, amt)
    contract = ctx.find("vsc_contracts", vsc_contract_id=vsc_contract_id)
    holder = contract[0].get("customer_id") if contract else ""
    paid_before = _Fmt.cents(contract[0].get("claims_paid_total") or 0) if contract else 0.0
    ctx.create("vsc_ledger", rid, vsc_entry_id=rid, vsc_contract_id=vsc_contract_id, customer_id=holder,
               event_type="vsc_claim_paid", entry_date=ctx.now()[:10], claim_number=claim_number,
               repair_order_number=repair_order_number, claim_line_type="rental",
               component_group="not_applicable", odometer=int(odometer), labor_hours=0.0,
               labor_rate_paid=0.0, parts_amount=0.0, deductible_applied=0.0, days=int(days), amount=amt,
               denial_reason="not_applicable", cancel_method="not_applicable",
               refund_payee="not_applicable", source_entry_id="")
    ctx.update("vsc_contracts", vsc_contract_id, claims_paid_total=_Fmt.cents(paid_before + amt))
    return (f"Rental line {rid} booked on contract {vsc_contract_id}: claim {claim_number}, "
            f"{int(days)} day(s), paid {amt:.2f} USD.")


@tool(owner="user", rw="write")
def accept_kept_vehicle_cancellation_d270783c(ctx: ToolContext, vsc_contract_id: str, vsc_cancel_request_id: str,
                                             effective_date: str, odometer_at_request: int,
                                             cancel_method: str, refund_amount: float) -> str:
    """The contract holder accepts the cancellation quote for a Kessler Shield service contract on a vehicle the holder keeps, completing the signed cancellation request already on file. One call marks that cancellation request completed, moves the contract to cancelled with the given effective date as its closed date, books one refund calculation entry on the contract dated the effective date with the certified odometer, the refund basis and the refund amount, and raises the contract's refund-due balance by that amount. The holder can see the contract as cancelled with the refund recorded as due.

    Args:
        vsc_contract_id: Id class — the service contract record identifier of the contract being cancelled, as returned by the service contract lookup and read to the holder by the desk.
        vsc_cancel_request_id: Id class — the identifier of the holder's signed cancellation request on file for this contract, as returned by the cancellation request lookup and read to the holder by the desk.
        effective_date: Fixed-format class — the effective cancellation date, written YYYY-MM-DD.
        odometer_at_request: Fixed-format class — the odometer certified on the cancellation request, in integer miles with no separators.
        cancel_method: Enum class — the basis of the refund, written exactly as one of: flat_free_look (the full price is refunded inside the free look), flat_deal_unwound (the full price is refunded because the purchase deal was unwound), pro_rata (the refund is the unused share of the price), not_applicable (not accepted by this action; it marks claim entries only).
        refund_amount: Fixed-format class — the refund the holder accepts, in USD with 2 decimal places (half-up to the cent), 0.00 or more.

    Returns:
        A confirmation string naming the refund calculation reference (an opaque id), the cancelled contract, the effective date and the refund amount in USD with 2 decimal places; its presence means the request was completed, the contract is cancelled and the refund is recorded as due.
    """
    if float(refund_amount) < 0 or int(odometer_at_request) < 0 or cancel_method not in _Fmt.METHODS or not _Fmt.is_date(effective_date):
        return "Error: refund_amount must be a USD figure of 0.00 or more, odometer_at_request whole miles, cancel_method one of the refund bases, and effective_date written YYYY-MM-DD."
    amt = _Fmt.cents(refund_amount)
    rid = ctx.make_id("vsr_", vsc_contract_id, vsc_cancel_request_id, effective_date, odometer_at_request,
                      cancel_method, amt)
    contract = ctx.find("vsc_contracts", vsc_contract_id=vsc_contract_id)
    holder = contract[0].get("customer_id") if contract else ""
    due_before = _Fmt.cents(contract[0].get("refund_due_balance") or 0) if contract else 0.0
    ctx.update("vsc_cancellation_requests", vsc_cancel_request_id, request_status="completed")
    ctx.update("vsc_contracts", vsc_contract_id, status="cancelled", closed_date=effective_date,
               refund_due_balance=_Fmt.cents(due_before + amt))
    ctx.create("vsc_ledger", rid, vsc_entry_id=rid, vsc_contract_id=vsc_contract_id, customer_id=holder,
               event_type="vsc_refund_calculated", entry_date=effective_date, claim_number="",
               repair_order_number="", claim_line_type="not_applicable", component_group="not_applicable",
               odometer=int(odometer_at_request), labor_hours=0.0, labor_rate_paid=0.0, parts_amount=0.0,
               deductible_applied=0.0, days=0, amount=amt, denial_reason="not_applicable",
               cancel_method=cancel_method, refund_payee="not_applicable", source_entry_id="")
    return (f"Refund calculation {rid} booked: contract {vsc_contract_id} cancelled effective {effective_date}, "
            f"refund due {amt:.2f} USD.")


@tool(owner="agent", rw="write")
def reimburse_maintenance_denial_repair_6315e699(ctx: ToolContext, vsc_contract_id: str, claim_number: str,
                                            repair_order_number: str, component_group: str,
                                            odometer: int, amount: float) -> str:
    """Repay a Kessler Shield service contract holder for an engine, transmission or drive-axle repair the holder paid the store for on customer pay after the contract had denied that claim line for lack of maintenance. One call books one paid component-repair claim line on the contract under the given claim number, repair order and component group, dated today, carrying the repair-order odometer and the reimbursement total as one amount (the labor-hour, labor-rate, parts and deductible breakdown fields of the line are left at zero because the line records a reimbursement total), and raises the contract's claims-paid total by that amount. The paid line is visible at once on the contract's claim history and counts against the contract's aggregate claim limit.

    Args:
        vsc_contract_id: Id class — the service contract record identifier of the holder's Kessler Shield contract, as returned by the service contract lookup.
        claim_number: Verbatim class — the claim authorization number exactly as it appears on the contract's denied claim line in the claim history, copied character for character with no change to letters, digits or hyphens (verbatim).
        repair_order_number: Verbatim class — the repair order number exactly as it appears on the contract's denied claim line and on the store's repair-order lines, copied character for character including its spacing (verbatim).
        component_group: Enum class — the component group of the repaired failure, written exactly as one of: engine (internally lubricated engine parts), transmission (transmission or transfer case), drive_axle (front or rear drive axle assembly), cooling (water pump, radiator or thermostat), fuel_system (fuel pump, injectors or pressure regulator), electrical (alternator, starter, power window or lock motors, wiring harnesses), air_conditioning (compressor, condenser or evaporator), steering (steering gear, rack or power steering pump), suspension (control arms, ball joints or bushings), brakes (master cylinder, calipers or ABS module), high_tech_electronics (infotainment, navigation, camera or driver-assist modules), seals_and_gaskets (seals and gaskets of covered components), not_applicable (not accepted by this action; it marks benefit and refund entries only).
        odometer: Fixed-format class — the odometer on the repair order, in integer miles with no separators.
        amount: Fixed-format class — the reimbursement total paid to the holder, in USD with 2 decimal places (half-up to the cent), greater than 0.00.

    Returns:
        A confirmation string naming the new claim line reference (an opaque id), the contract, the claim number and the amount paid in USD with 2 decimal places; its presence means the paid line was booked and the contract's claims-paid total was raised by that amount.
    """
    if float(amount) <= 0 or int(odometer) < 0 or component_group not in _Fmt.GROUPS:
        return "Error: amount must be a USD figure above 0.00, odometer whole miles of 0 or more, and component_group one of the component groups."
    amt = _Fmt.cents(amount)
    rid = ctx.make_id("vsl_", vsc_contract_id, claim_number, repair_order_number, component_group, odometer, amt)
    contract = ctx.find("vsc_contracts", vsc_contract_id=vsc_contract_id)
    holder = contract[0].get("customer_id") if contract else ""
    paid_before = _Fmt.cents(contract[0].get("claims_paid_total") or 0) if contract else 0.0
    ctx.create("vsc_ledger", rid, vsc_entry_id=rid, vsc_contract_id=vsc_contract_id, customer_id=holder,
               event_type="vsc_claim_paid", entry_date=ctx.now()[:10], claim_number=claim_number,
               repair_order_number=repair_order_number, claim_line_type="component_repair",
               component_group=component_group, odometer=int(odometer), labor_hours=0.0,
               labor_rate_paid=0.0, parts_amount=0.0, deductible_applied=0.0, days=0, amount=amt,
               denial_reason="not_applicable", cancel_method="not_applicable",
               refund_payee="not_applicable", source_entry_id="")
    ctx.update("vsc_contracts", vsc_contract_id, claims_paid_total=_Fmt.cents(paid_before + amt))
    return (f"Claim line {rid} booked on contract {vsc_contract_id}: claim {claim_number}, "
            f"reimbursement paid {amt:.2f} USD.")


@tool(owner="agent", rw="write")
def reimburse_coverage_denial_repair_73971dca(ctx: ToolContext, vsc_contract_id: str, claim_number: str,
                                            repair_order_number: str, component_group: str,
                                            odometer: int, amount: float) -> str:
    """Repay a Kessler Shield service contract holder for a component repair the holder paid the store for on customer pay after the contract had denied that claim line as not covered. One call books one paid component-repair claim line on the contract under the given claim number, repair order and component group, dated today, carrying the repair-order odometer and the reimbursement total as one amount (the labor-hour, labor-rate, parts and deductible breakdown fields of the line are left at zero because the line records a reimbursement total), and raises the contract's claims-paid total by that amount. The paid line is visible at once on the contract's claim history and counts against the contract's aggregate claim limit.

    Args:
        vsc_contract_id: Id class — the service contract record identifier of the holder's Kessler Shield contract, as returned by the service contract lookup.
        claim_number: Verbatim class — the claim authorization number exactly as it appears on the contract's denied claim line in the claim history, copied character for character with no change to letters, digits or hyphens (verbatim).
        repair_order_number: Verbatim class — the repair order number exactly as it appears on the contract's denied claim line and on the store's repair-order lines, copied character for character including its spacing (verbatim).
        component_group: Enum class — the component group of the repaired failure, written exactly as one of: engine (internally lubricated engine parts), transmission (transmission or transfer case), drive_axle (front or rear drive axle assembly), cooling (water pump, radiator or thermostat), fuel_system (fuel pump, injectors or pressure regulator), electrical (alternator, starter, power window or lock motors, wiring harnesses), air_conditioning (compressor, condenser or evaporator), steering (steering gear, rack or power steering pump), suspension (control arms, ball joints or bushings), brakes (master cylinder, calipers or ABS module), high_tech_electronics (infotainment, navigation, camera or driver-assist modules), seals_and_gaskets (seals and gaskets of covered components), not_applicable (not accepted by this action; it marks benefit and refund entries only).
        odometer: Fixed-format class — the odometer on the repair order, in integer miles with no separators.
        amount: Fixed-format class — the reimbursement total paid to the holder, in USD with 2 decimal places (half-up to the cent), greater than 0.00.

    Returns:
        A confirmation string naming the new claim line reference (an opaque id), the contract, the claim number and the amount paid in USD with 2 decimal places; its presence means the paid line was booked and the contract's claims-paid total was raised by that amount.
    """
    if float(amount) <= 0 or int(odometer) < 0 or component_group not in _Fmt.GROUPS:
        return "Error: amount must be a USD figure above 0.00, odometer whole miles of 0 or more, and component_group one of the component groups."
    amt = _Fmt.cents(amount)
    rid = ctx.make_id("vsl_", vsc_contract_id, claim_number, repair_order_number, component_group, odometer, amt)
    contract = ctx.find("vsc_contracts", vsc_contract_id=vsc_contract_id)
    holder = contract[0].get("customer_id") if contract else ""
    paid_before = _Fmt.cents(contract[0].get("claims_paid_total") or 0) if contract else 0.0
    ctx.create("vsc_ledger", rid, vsc_entry_id=rid, vsc_contract_id=vsc_contract_id, customer_id=holder,
               event_type="vsc_claim_paid", entry_date=ctx.now()[:10], claim_number=claim_number,
               repair_order_number=repair_order_number, claim_line_type="component_repair",
               component_group=component_group, odometer=int(odometer), labor_hours=0.0,
               labor_rate_paid=0.0, parts_amount=0.0, deductible_applied=0.0, days=0, amount=amt,
               denial_reason="not_applicable", cancel_method="not_applicable",
               refund_payee="not_applicable", source_entry_id="")
    ctx.update("vsc_contracts", vsc_contract_id, claims_paid_total=_Fmt.cents(paid_before + amt))
    return (f"Claim line {rid} booked on contract {vsc_contract_id}: claim {claim_number}, "
            f"reimbursement paid {amt:.2f} USD.")


@tool(owner="user", rw="write")
def accept_traded_vehicle_cancellation_f71aca80(ctx: ToolContext, vsc_contract_id: str, vsc_cancel_request_id: str,
                                             effective_date: str, odometer_at_request: int,
                                             cancel_method: str, refund_amount: float) -> str:
    """The contract holder accepts the cancellation quote for a Kessler Shield service contract on a vehicle the holder has sold or traded, completing the signed cancellation request already on file. One call marks that cancellation request completed, moves the contract to cancelled with the given effective date as its closed date, books one refund calculation entry on the contract dated the effective date with the certified odometer, the refund basis and the refund amount, and raises the contract's refund-due balance by that amount. The holder can see the contract as cancelled with the refund recorded as due.

    Args:
        vsc_contract_id: Id class — the service contract record identifier of the contract being cancelled, as returned by the service contract lookup and read to the holder by the desk.
        vsc_cancel_request_id: Id class — the identifier of the holder's signed cancellation request on file for this contract, as returned by the cancellation request lookup and read to the holder by the desk.
        effective_date: Fixed-format class — the effective cancellation date, written YYYY-MM-DD.
        odometer_at_request: Fixed-format class — the odometer certified on the cancellation request, in integer miles with no separators.
        cancel_method: Enum class — the basis of the refund, written exactly as one of: flat_free_look (the full price is refunded inside the free look), flat_deal_unwound (the full price is refunded because the purchase deal was unwound), pro_rata (the refund is the unused share of the price), not_applicable (not accepted by this action; it marks claim entries only).
        refund_amount: Fixed-format class — the refund the holder accepts, in USD with 2 decimal places (half-up to the cent), 0.00 or more.

    Returns:
        A confirmation string naming the refund calculation reference (an opaque id), the cancelled contract, the effective date and the refund amount in USD with 2 decimal places; its presence means the request was completed, the contract is cancelled and the refund is recorded as due.
    """
    if float(refund_amount) < 0 or int(odometer_at_request) < 0 or cancel_method not in _Fmt.METHODS or not _Fmt.is_date(effective_date):
        return "Error: refund_amount must be a USD figure of 0.00 or more, odometer_at_request whole miles, cancel_method one of the refund bases, and effective_date written YYYY-MM-DD."
    amt = _Fmt.cents(refund_amount)
    rid = ctx.make_id("vsr_", vsc_contract_id, vsc_cancel_request_id, effective_date, odometer_at_request,
                      cancel_method, amt)
    contract = ctx.find("vsc_contracts", vsc_contract_id=vsc_contract_id)
    holder = contract[0].get("customer_id") if contract else ""
    due_before = _Fmt.cents(contract[0].get("refund_due_balance") or 0) if contract else 0.0
    ctx.update("vsc_cancellation_requests", vsc_cancel_request_id, request_status="completed")
    ctx.update("vsc_contracts", vsc_contract_id, status="cancelled", closed_date=effective_date,
               refund_due_balance=_Fmt.cents(due_before + amt))
    ctx.create("vsc_ledger", rid, vsc_entry_id=rid, vsc_contract_id=vsc_contract_id, customer_id=holder,
               event_type="vsc_refund_calculated", entry_date=effective_date, claim_number="",
               repair_order_number="", claim_line_type="not_applicable", component_group="not_applicable",
               odometer=int(odometer_at_request), labor_hours=0.0, labor_rate_paid=0.0, parts_amount=0.0,
               deductible_applied=0.0, days=0, amount=amt, denial_reason="not_applicable",
               cancel_method=cancel_method, refund_payee="not_applicable", source_entry_id="")
    return (f"Refund calculation {rid} booked: contract {vsc_contract_id} cancelled effective {effective_date}, "
            f"refund due {amt:.2f} USD.")

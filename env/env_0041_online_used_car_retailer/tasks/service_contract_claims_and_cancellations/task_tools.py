"""Hidden task tools of difficulty service_contract_claims_and_cancellations (KestrelCare Vehicle Service
Contracts). Each tool performs one atomic booking with the values the caller has already worked out; none of
them checks a policy condition or computes an amount."""

from erlbench import ToolContext, tool


@tool(owner="agent", rw="write")
def authorize_stack_remainder_2296c771(ctx: ToolContext, service_contract_id: str, repair_order_number: str,
                                       failure_date: str, odometer_at_failure: int, component_system: str,
                                       repair_facility_type: str, claim_decision: str, requested_amount: float,
                                       deductible_amount: float, approved_amount: float) -> str:
    """Record the KestrelCare decision on a repair facility's authorization request for one repair order on a
    service contract. One call books one claim decision entry on the contract's history, carrying the repair
    order number, the failure date and odometer, the vehicle system, the facility type, the decision, the estimate
    the decision was made on, the deductible applied and the amount payable to the facility. This booking leaves the
    contract's coverage remaining unchanged. On success the decision appears in the
    contract's service history and a receipt with the new entry reference is returned.

    Args:
        service_contract_id: Id class — the reference number of the KestrelCare service contract the repair
            order is decided under, as returned by the service contract lookup.
        repair_order_number: Verbatim class — the repair facility's repair order number, copied exactly as it is
            printed on the limited warranty decision record or as the holder reads it from the repair order,
            character for character with no reformatting (verbatim).
        failure_date: Fixed-format class — the date the failure was reported to the repair facility, written as
            YYYY-MM-DD (calendar date, no time part).
        odometer_at_failure: Fixed-format class — the odometer reading on the repair order, a non-negative integer
            (miles) with no separators.
        component_system: Enum class — the vehicle system the failed part belongs to; exactly one of: engine
            when the failed part is in the engine; transmission when it is in the transmission; drive_axle when it
            is in a drive axle; transfer_case when it is in the transfer case; cooling_system when it is in the
            cooling system; fuel_system when it is in the fuel system; electrical when it is in the electrical
            system; air_conditioning when it is in the air conditioning; steering when it is in the steering;
            brakes when it is in the brakes; suspension when it is in the suspension; hybrid_ev_drive_system when
            it is in a hybrid or electric drive system; high_tech_electronics when it is in the high-tech
            electronics; seals_and_gaskets when it is a seal or gasket; not_applicable only for a request that
            names no vehicle system at all.
        repair_facility_type: Enum class — the kind of facility doing the repair; exactly one of: kestrel_network
            when the facility is a Kestrel network facility; franchise_dealer when it is a franchised new-car
            dealer; independent_licensed when it is an independent licensed repair shop; not_applicable only when
            no facility is involved.
        claim_decision: Enum class — the decision; exactly one of: approved when the request is approved for
            payment; denied_waiting_period when the failure falls before coverage started; denied_contract_not_in_force
            when the contract was not in force for the failure; denied_not_covered_component when the failed part
            is outside the covered components; denied_preexisting_condition when the condition existed before the
            sale or the vehicle is in commercial use; denied_maintenance_records when required maintenance proof is
            missing; not_applicable is never used for a decision and appears only on other entries.
        requested_amount: Fixed-format class — the repair estimate the decision is made on, in USD with 2 decimal
            places, rounded to the nearest cent.
        deductible_amount: Fixed-format class — the plan deductible applied on this decision, in USD with 2
            decimal places; 0.00 when none is applied.
        approved_amount: Fixed-format class — the amount payable to the facility under this decision, in USD with
            2 decimal places, rounded to the nearest cent; 0.00 for a denial.

    Returns:
        A text receipt of a dictionary with: status (the string "recorded" when the decision was booked),
        warranty_txn_id (reference of the new claim decision entry), repair_order_number (the repair order
        decided), claim_decision (the decision booked) and approved_amount (the amount payable in USD with 2
        decimals).
    """
    rid = ctx.make_id("wtx_", service_contract_id, repair_order_number, failure_date, odometer_at_failure,
                      component_system, repair_facility_type, claim_decision, requested_amount,
                      deductible_amount, approved_amount)
    ctx.create("service_contract_transactions", rid, warranty_txn_id=rid, service_contract_id=service_contract_id,
               customer_id=(ctx.find("service_contracts", service_contract_id=service_contract_id) or [{}])[0].get("customer_id", ""), event_type="warranty_claim_adjudicated",
               txn_date=ctx.now()[:10], amount=round(float(approved_amount), 2),
               repair_order_number=repair_order_number, failure_date=failure_date,
               odometer_at_failure=int(odometer_at_failure), component_system=component_system,
               claim_decision=claim_decision, requested_amount=round(float(requested_amount), 2),
               deductible_amount=round(float(deductible_amount), 2), repair_facility_type=repair_facility_type,
               benefit_type="not_applicable", benefit_days=0, cancellation_basis="not_applicable",
               refund_payee="not_applicable", source_txn_id="")
    return str({"status": "recorded", "warranty_txn_id": rid, "repair_order_number": repair_order_number,
                "claim_decision": claim_decision, "approved_amount": round(float(approved_amount), 2)})


@tool(owner="user", rw="write")
def file_rental_reimbursement_5fdd83af(ctx: ToolContext, service_contract_id: str, repair_order_number: str,
                                       rental_days: int, reimbursement_amount: float) -> str:
    """The holder files their own rental car reimbursement claim for one repair order under their KestrelCare
    service contract, attesting to the rental they paid while the vehicle was in the shop. One call books one
    rental car reimbursement entry on the contract's history with the repair order, the rental days and the
    reimbursement amount; the reimbursement is paid to the holder and does not change the coverage remaining. On
    success the reimbursement appears in the contract's service history and a receipt is returned.

    Args:
        service_contract_id: Id class — the reference number of the holder's KestrelCare service contract, as the
            representative reads it from the service contract lookup and gives it to the holder.
        repair_order_number: Verbatim class — the repair facility's repair order number the rental belongs to,
            copied exactly as printed on the holder's repair order, character for character (verbatim).
        rental_days: Fixed-format class — the rental days being reimbursed, a non-negative integer (days).
        reimbursement_amount: Fixed-format class — the reimbursement the holder is paid, in USD with 2 decimal
            places, rounded to the nearest cent, as the representative states it.

    Returns:
        A text receipt of a dictionary with: status (the string "filed" when the reimbursement was booked),
        warranty_txn_id (reference of the new reimbursement entry), repair_order_number (the repair order it
        belongs to), rental_days (days reimbursed) and reimbursement_amount (USD with 2 decimals).
    """
    rid = ctx.make_id("wtx_", service_contract_id, repair_order_number, "rental_car", rental_days,
                      reimbursement_amount)
    ctx.create("service_contract_transactions", rid, warranty_txn_id=rid, service_contract_id=service_contract_id,
               customer_id=(ctx.find("service_contracts", service_contract_id=service_contract_id) or [{}])[0].get("customer_id", ""), event_type="warranty_benefit_reimbursed",
               txn_date=ctx.now()[:10], amount=round(float(reimbursement_amount), 2),
               repair_order_number=repair_order_number, failure_date="", odometer_at_failure=0,
               component_system="not_applicable", claim_decision="not_applicable", requested_amount=0.0,
               deductible_amount=0.0, repair_facility_type="not_applicable", benefit_type="rental_car",
               benefit_days=int(rental_days), cancellation_basis="not_applicable", refund_payee="not_applicable",
               source_txn_id="")
    return str({"status": "filed", "warranty_txn_id": rid, "repair_order_number": repair_order_number,
                "rental_days": int(rental_days), "reimbursement_amount": round(float(reimbursement_amount), 2)})


@tool(owner="agent", rw="write")
def cancel_plan_with_refund_1804bd93(ctx: ToolContext, service_contract_id: str, effective_date: str,
                                     cancellation_basis: str, refund_amount: float) -> str:
    """Cancel a KestrelCare service contract and book its cancellation refund to the holder in one settlement.
    One call sets the contract's status to cancelled with the given effective date as its closing date and books
    one cancellation refund entry, paid to the holder, carrying the refund basis and the refund amount. On success
    the contract shows as cancelled, the refund appears in its service history, and a receipt is returned.

    Args:
        service_contract_id: Id class — the reference number of the KestrelCare service contract being
            cancelled, as returned by the service contract lookup.
        effective_date: Fixed-format class — the date the cancellation takes effect, written as YYYY-MM-DD
            (calendar date, no time part); it becomes the contract's closing date.
        cancellation_basis: Enum class — the basis the refund is settled on; exactly one of:
            free_look_full_refund when the full price is refunded inside the free-look period with no claim paid;
            pro_rata when the refund is the unused share of the price; flat_cancel_vehicle_returned when the plan
            is cancelled from inception because the vehicle came back under the 7-day return; not_applicable is
            never a refund basis and appears only on other entries.
        refund_amount: Fixed-format class — the refund paid to the holder, in USD with 2 decimal places, rounded
            half up to the cent.

    Returns:
        A text receipt of a dictionary with: status (the string "cancelled" when the settlement was booked),
        service_contract_id (the contract cancelled), closed_date (effective date, YYYY-MM-DD), warranty_txn_id
        (reference of the refund entry), cancellation_basis (the basis booked) and refund_amount (USD with 2
        decimals).
    """
    ctx.update("service_contracts", service_contract_id, status="cancelled", closed_date=effective_date)
    rid = ctx.make_id("wtx_", service_contract_id, effective_date, cancellation_basis, refund_amount)
    ctx.create("service_contract_transactions", rid, warranty_txn_id=rid, service_contract_id=service_contract_id,
               customer_id=(ctx.find("service_contracts", service_contract_id=service_contract_id) or [{}])[0].get("customer_id", ""), event_type="warranty_cancellation_refund_issued",
               txn_date=ctx.now()[:10], amount=round(float(refund_amount), 2), repair_order_number="",
               failure_date="", odometer_at_failure=0, component_system="not_applicable",
               claim_decision="not_applicable", requested_amount=0.0, deductible_amount=0.0,
               repair_facility_type="not_applicable", benefit_type="not_applicable", benefit_days=0,
               cancellation_basis=cancellation_basis, refund_payee="customer", source_txn_id="")
    return str({"status": "cancelled", "service_contract_id": service_contract_id, "closed_date": effective_date,
                "warranty_txn_id": rid, "cancellation_basis": cancellation_basis,
                "refund_amount": round(float(refund_amount), 2)})


@tool(owner="agent", rw="write")
def recover_overpaid_claim_bcfb33cc(ctx: ToolContext, service_contract_id: str, payment_txn_id: str,
                                    recovery_amount: float) -> str:
    """Book the recovery of a claim payment made in error on a KestrelCare service contract. One call books one
    payment recovery entry naming the claim payment being recovered and raises the contract's coverage remaining by
    the recovered amount, restoring the limit of liability. On success the recovery appears in the contract's
    service history, the coverage remaining shows the restored figure, and a receipt is returned.

    Args:
        service_contract_id: Id class — the reference number of the KestrelCare service contract the payment was
            charged to, as returned by the service contract lookup.
        payment_txn_id: Id class — the reference number of the claim payment entry being recovered, as shown in
            the contract's service history lookup.
        recovery_amount: Fixed-format class — the amount recovered and restored to the limit, in USD with 2
            decimal places, rounded to the nearest cent.

    Returns:
        A text receipt of a dictionary with: status (the string "recovered" when the recovery was booked),
        warranty_txn_id (reference of the new recovery entry), payment_txn_id (the payment recovered),
        recovery_amount (USD with 2 decimals) and coverage_remaining (the contract's coverage remaining after the
        recovery, USD with 2 decimals).
    """
    rows = ctx.find("service_contracts", service_contract_id=service_contract_id)
    contract = rows[0] if rows else {}
    remaining = round(float(contract.get("coverage_remaining") or 0) + round(float(recovery_amount), 2), 2)
    rid = ctx.make_id("wtx_", service_contract_id, payment_txn_id, recovery_amount)
    ctx.create("service_contract_transactions", rid, warranty_txn_id=rid, service_contract_id=service_contract_id,
               customer_id=contract.get("customer_id", ""), event_type="warranty_claim_payment_recovered",
               txn_date=ctx.now()[:10], amount=round(float(recovery_amount), 2), repair_order_number="",
               failure_date="", odometer_at_failure=0, component_system="not_applicable",
               claim_decision="not_applicable", requested_amount=0.0, deductible_amount=0.0,
               repair_facility_type="not_applicable", benefit_type="not_applicable", benefit_days=0,
               cancellation_basis="not_applicable", refund_payee="not_applicable", source_txn_id=payment_txn_id)
    ctx.update("service_contracts", service_contract_id, coverage_remaining=remaining)
    return str({"status": "recovered", "warranty_txn_id": rid, "payment_txn_id": payment_txn_id,
                "recovery_amount": round(float(recovery_amount), 2), "coverage_remaining": remaining})


@tool(owner="agent", rw="write")
def pay_diagnostic_time_6cc9f33c(ctx: ToolContext, service_contract_id: str, adjudication_txn_id: str,
                                 repair_order_number: str, payment_amount: float) -> str:
    """Pay a repair facility for the diagnostic time on one approved repair order under a KestrelCare service
    contract. One call books one claim payment entry for the diagnostic time, linked to the decision it pays and
    the repair order, and lowers the contract's coverage remaining by the amount paid. On success the payment
    appears in the contract's service history, the coverage remaining shows the reduced figure, and a receipt is
    returned.

    Args:
        service_contract_id: Id class — the reference number of the KestrelCare service contract, as returned by
            the service contract lookup.
        adjudication_txn_id: Id class — the reference number of the approved claim decision entry whose diagnostic
            time is paid, as shown in the contract's service history lookup.
        repair_order_number: Verbatim class — the repair order number exactly as it appears on that claim decision
            entry, copied character for character (verbatim).
        payment_amount: Fixed-format class — the diagnostic time paid to the facility, in USD with 2 decimal
            places, rounded to the nearest cent.

    Returns:
        A text receipt of a dictionary with: status (the string "paid" when the payment was booked),
        warranty_txn_id (reference of the new payment entry), repair_order_number (the repair order paid),
        payment_amount (USD with 2 decimals) and coverage_remaining (coverage remaining after the payment, USD with
        2 decimals).
    """
    rows = ctx.find("service_contracts", service_contract_id=service_contract_id)
    contract = rows[0] if rows else {}
    remaining = round(float(contract.get("coverage_remaining") or 0) - round(float(payment_amount), 2), 2)
    rid = ctx.make_id("wtx_", service_contract_id, adjudication_txn_id, "diagnostic", repair_order_number,
                      payment_amount)
    ctx.create("service_contract_transactions", rid, warranty_txn_id=rid, service_contract_id=service_contract_id,
               customer_id=contract.get("customer_id", ""), event_type="warranty_claim_paid",
               txn_date=ctx.now()[:10], amount=round(float(payment_amount), 2),
               repair_order_number=repair_order_number, failure_date="", odometer_at_failure=0,
               component_system="not_applicable", claim_decision="not_applicable", requested_amount=0.0,
               deductible_amount=0.0, repair_facility_type="not_applicable", benefit_type="not_applicable",
               benefit_days=0, cancellation_basis="not_applicable", refund_payee="not_applicable",
               source_txn_id=adjudication_txn_id)
    ctx.update("service_contracts", service_contract_id, coverage_remaining=remaining)
    return str({"status": "paid", "warranty_txn_id": rid, "repair_order_number": repair_order_number,
                "payment_amount": round(float(payment_amount), 2), "coverage_remaining": remaining})


@tool(owner="agent", rw="write")
def pay_repair_facility_1c2b8918(ctx: ToolContext, service_contract_id: str, adjudication_txn_id: str,
                                 repair_order_number: str, payment_amount: float) -> str:
    """Pay a repair facility for the repair work on one approved repair order under a KestrelCare service
    contract, so the facility can release the vehicle. One call books one claim payment entry for the repair work,
    linked to the decision it pays and the repair order, and lowers the contract's coverage remaining by the amount
    paid. On success the payment appears in the contract's service history, the coverage remaining shows the
    reduced figure, and a receipt is returned.

    Args:
        service_contract_id: Id class — the reference number of the KestrelCare service contract, as returned by
            the service contract lookup.
        adjudication_txn_id: Id class — the reference number of the approved claim decision entry whose repair work
            is paid, as shown in the contract's service history lookup.
        repair_order_number: Verbatim class — the repair order number exactly as it appears on that claim decision
            entry, copied character for character (verbatim).
        payment_amount: Fixed-format class — the amount paid to the facility for the repair work, in USD with 2
            decimal places, rounded to the nearest cent.

    Returns:
        A text receipt of a dictionary with: status (the string "paid" when the payment was booked),
        warranty_txn_id (reference of the new payment entry), repair_order_number (the repair order paid),
        payment_amount (USD with 2 decimals) and coverage_remaining (coverage remaining after the payment, USD with
        2 decimals).
    """
    rows = ctx.find("service_contracts", service_contract_id=service_contract_id)
    contract = rows[0] if rows else {}
    remaining = round(float(contract.get("coverage_remaining") or 0) - round(float(payment_amount), 2), 2)
    rid = ctx.make_id("wtx_", service_contract_id, adjudication_txn_id, "repair", repair_order_number,
                      payment_amount)
    ctx.create("service_contract_transactions", rid, warranty_txn_id=rid, service_contract_id=service_contract_id,
               customer_id=contract.get("customer_id", ""), event_type="warranty_claim_paid",
               txn_date=ctx.now()[:10], amount=round(float(payment_amount), 2),
               repair_order_number=repair_order_number, failure_date="", odometer_at_failure=0,
               component_system="not_applicable", claim_decision="not_applicable", requested_amount=0.0,
               deductible_amount=0.0, repair_facility_type="not_applicable", benefit_type="not_applicable",
               benefit_days=0, cancellation_basis="not_applicable", refund_payee="not_applicable",
               source_txn_id=adjudication_txn_id)
    ctx.update("service_contracts", service_contract_id, coverage_remaining=remaining)
    return str({"status": "paid", "warranty_txn_id": rid, "repair_order_number": repair_order_number,
                "payment_amount": round(float(payment_amount), 2), "coverage_remaining": remaining})


@tool(owner="user", rw="write")
def file_trip_interruption_claim_d37559b2(ctx: ToolContext, service_contract_id: str, repair_order_number: str,
                                          trip_days: int, reimbursement_amount: float) -> str:
    """The holder files their own trip interruption claim for lodging and meals paid while a covered breakdown far
    from home kept them away, under their KestrelCare service contract. One call books one trip interruption
    reimbursement entry on the contract's history with the repair order, the trip days and the reimbursement
    amount; the reimbursement is paid to the holder and does not change the coverage remaining. On success the
    reimbursement appears in the contract's service history and a receipt is returned.

    Args:
        service_contract_id: Id class — the reference number of the holder's KestrelCare service contract, as the
            representative reads it from the service contract lookup and gives it to the holder.
        repair_order_number: Verbatim class — the repair facility's repair order number for the breakdown, copied
            exactly as printed on the holder's repair order, character for character (verbatim).
        trip_days: Fixed-format class — the trip days being reimbursed, a non-negative integer (days).
        reimbursement_amount: Fixed-format class — the reimbursement the holder is paid, in USD with 2 decimal
            places, rounded to the nearest cent, as the representative states it.

    Returns:
        A text receipt of a dictionary with: status (the string "filed" when the reimbursement was booked),
        warranty_txn_id (reference of the new reimbursement entry), repair_order_number (the repair order it
        belongs to), trip_days (days reimbursed) and reimbursement_amount (USD with 2 decimals).
    """
    rows = ctx.find("service_contracts", service_contract_id=service_contract_id)
    contract = rows[0] if rows else {}
    rid = ctx.make_id("wtx_", service_contract_id, repair_order_number, "trip_interruption", trip_days,
                      reimbursement_amount)
    ctx.create("service_contract_transactions", rid, warranty_txn_id=rid, service_contract_id=service_contract_id,
               customer_id=contract.get("customer_id", ""), event_type="warranty_benefit_reimbursed",
               txn_date=ctx.now()[:10], amount=round(float(reimbursement_amount), 2),
               repair_order_number=repair_order_number, failure_date="", odometer_at_failure=0,
               component_system="not_applicable", claim_decision="not_applicable", requested_amount=0.0,
               deductible_amount=0.0, repair_facility_type="not_applicable", benefit_type="trip_interruption",
               benefit_days=int(trip_days), cancellation_basis="not_applicable", refund_payee="not_applicable",
               source_txn_id="")
    return str({"status": "filed", "warranty_txn_id": rid, "repair_order_number": repair_order_number,
                "trip_days": int(trip_days), "reimbursement_amount": round(float(reimbursement_amount), 2)})

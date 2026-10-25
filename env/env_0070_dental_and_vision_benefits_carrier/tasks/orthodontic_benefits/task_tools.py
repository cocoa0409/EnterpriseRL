"""Hidden task tools for the orthodontic_benefits difficulty of env_0070 (Cascade Mutual Dental & Vision).

Each tool performs one atomic write on the orthodontic rider records with the values it is given;
none of them checks eligibility, prerequisites or amounts, and none of them computes a benefit figure.
"""

from erlbench import ToolContext, tool


@tool(owner="user", rw="write")
def move_ortho_case_49ae8ecf(ctx: ToolContext, ortho_rider_id: str, ortho_case_event_id: str, provider_agreement_id: str,
                             network_status: str, treatment_months: int, months_remaining: int,
                             total_case_fee: float, allowed_case_fee: float) -> str:
    """The subscriber moves an open orthodontic case to the orthodontist now treating the patient.
    One call records a transfer entry on that case: the case keeps its case number, rider, case
    origin, appliance type and banding date, and from the moment of the call the case shows the new
    practice's agreement (or none), its network status, the revised treatment plan, the new
    practice's fee for the remaining treatment and the fee Cascade recognises for that remaining
    treatment. Nothing is paid by this call. The subscriber can see the case listed with the new
    practice and the recognised fee; the returned receipt carries the reference of the new transfer
    entry, which signals that the move was recorded.

    Args:
        ortho_rider_id: Id class — the identifier (reference number) of the patient's orthodontic rider the case is paid under, as returned by the orthodontic rider lookup for the subscriber.
        ortho_case_event_id: Id class — the identifier (reference number) of the establishment entry of the orthodontic case being moved, as returned by the orthodontic case lookup for the patient's rider.
        provider_agreement_id: Id class — the identifier (reference number) of the participation agreement of the new orthodontist as returned by the provider agreement lookup for that practice; pass an empty string when the new orthodontist holds no Cascade agreement.
        network_status: Enum class — network status of the new orthodontist on the day of the move: in_network when the new orthodontist holds a Cascade PPO or Premier participating agreement in force on that day with the orthodontist specialty; out_of_network when the new orthodontist holds no such agreement in force on that day.
        treatment_months: Fixed-format class — revised total planned months of active treatment counted from the original banding date, as stated on the new orthodontist's treatment plan; an integer number of months.
        months_remaining: Fixed-format class — planned months of active treatment still to come on the day of the move, as stated on the new orthodontist's treatment plan; an integer number of months.
        total_case_fee: Fixed-format class — the new orthodontist's fee for the remaining treatment as stated on that practice's treatment plan, in USD, 2 decimal places, rounded half up to the cent.
        allowed_case_fee: Fixed-format class — the fee Cascade recognises for the remaining treatment, in USD, 2 decimal places, rounded half up to the cent; the value is stored as given.

    Returns:
        A text rendering of a dictionary with these keys: transfer_entry (string, the reference of the
        new transfer entry), case_number (string, the unchanged case number), network_status (string,
        the network status recorded), months_remaining (integer, as recorded), allowed_case_fee (number,
        USD with 2 decimal places, as recorded) and event_date (string, YYYY-MM-DD, the date of the move).
        A receipt carrying a transfer_entry reference means the case now shows the new practice.
    """
    est = ctx.find("ortho_cases", ortho_case_event_id=ortho_case_event_id)
    src = est[0] if est else {}
    rid = ctx.make_id("ocx_", ortho_rider_id, ortho_case_event_id, provider_agreement_id, network_status, treatment_months,
                      months_remaining, total_case_fee, allowed_case_fee)
    day = ctx.now()[:10]
    ctx.create("ortho_cases", rid, ortho_case_event_id=rid, ortho_rider_id=ortho_rider_id,
               customer_id=src.get("customer_id", ""), event_type="ortho_case_transferred",
               case_number=src.get("case_number", ""), provider_agreement_id=provider_agreement_id,
               network_status=network_status, case_origin=src.get("case_origin", ""),
               appliance_type=src.get("appliance_type", ""), banding_date=src.get("banding_date", ""),
               treatment_months=int(treatment_months), months_remaining=int(months_remaining),
               total_case_fee=round(float(total_case_fee), 2), allowed_case_fee=round(float(allowed_case_fee), 2),
               event_date=day, closure_reason="not_closed", original_case_event_id=ortho_case_event_id)
    return str({"transfer_entry": rid, "case_number": src.get("case_number", ""), "network_status": network_status,
                "months_remaining": int(months_remaining), "allowed_case_fee": round(float(allowed_case_fee), 2),
                "event_date": day})


@tool(owner="agent", rw="write")
def issue_ortho_carried_payment_56eb10f4(ctx: ToolContext, ortho_case_event_id: str, installment_number: int,
                                         service_period: str, payee: str, provider_agreement_id: str,
                                         amount: float) -> str:
    """Issue one orthodontic benefit payment on a case that has moved to a new orthodontist. One call
    books a single installment payment on the case for the stated service period and payee, dated
    today, and adds the amount to the orthodontic benefit paid under the patient's rider. Nothing else
    on the case changes. The payee receives the payment and the case history shows it with its
    installment position and service period; the returned receipt carries the payment reference,
    which signals that the payment was issued.

    Args:
        ortho_case_event_id: Id class — the identifier (reference number) of the establishment entry of the orthodontic case, as returned by the orthodontic case lookup for the patient's rider.
        installment_number: Fixed-format class — the position of this payment in the case payment schedule, written as an integer; 0 for the initial payment, 1 upward for installments.
        service_period: Fixed-format class — the month the payment covers, or the starting month of the quarter it covers, written YYYY-MM.
        payee: Enum class — who receives the payment: practice when the orthodontist now treating the patient is paid under an assignment of benefits as a participating practice; member when the orthodontist now treating the patient is not participating and the subscriber is paid.
        provider_agreement_id: Id class — the identifier (reference number) of the participation agreement of the practice that receives the payment, as returned by the provider agreement lookup; pass an empty string when the member is paid.
        amount: Fixed-format class — the payment amount, in USD, 2 decimal places, always positive, rounded half up to the cent; the value is booked as given.

    Returns:
        A text rendering of a dictionary with these keys: payment (string, the reference of the new
        payment), case_number (string), installment_number (integer), service_period (string, YYYY-MM),
        payee (string), amount (number, USD with 2 decimal places), payment_date (string, YYYY-MM-DD) and
        lifetime_benefit_paid (number, USD with 2 decimal places, the orthodontic benefit paid under the
        rider including this payment). A receipt carrying a payment reference means the payment was issued.
    """
    est = ctx.find("ortho_cases", ortho_case_event_id=ortho_case_event_id)
    src = est[0] if est else {}
    rider_id = src.get("ortho_rider_id", "")
    rid = ctx.make_id("opx_", ortho_case_event_id, installment_number, service_period, payee,
                      provider_agreement_id, amount)
    day = ctx.now()[:10]
    ctx.create("ortho_payments", rid, ortho_payment_id=rid, ortho_rider_id=rider_id,
               customer_id=src.get("customer_id", ""), event_type="ortho_installment_payment",
               ortho_case_event_id=ortho_case_event_id, case_number=src.get("case_number", ""),
               installment_number=int(installment_number), service_period=service_period, payee=payee,
               provider_agreement_id=provider_agreement_id, amount=round(float(amount), 2),
               payment_date=day, original_ortho_payment_id="")
    riders = ctx.find("ortho_riders", ortho_rider_id=rider_id)
    paid = round(float((riders[0] if riders else {}).get("lifetime_benefit_paid") or 0) + round(float(amount), 2), 2)
    if riders:
        ctx.update("ortho_riders", rider_id, lifetime_benefit_paid=paid)
    return str({"payment": rid, "case_number": src.get("case_number", ""), "installment_number": int(installment_number),
                "service_period": service_period, "payee": payee, "amount": round(float(amount), 2),
                "payment_date": day, "lifetime_benefit_paid": paid})


@tool(owner="agent", rw="write")
def record_ortho_takeover_case_574129ed(ctx: ToolContext, ortho_rider_id: str, ortho_case_event_id: str,
                                        provider_agreement_id: str, network_status: str,
                                        months_remaining: int, allowed_case_fee: float) -> str:
    """Re-establish an orthodontic case as a takeover. One call records a new establishment entry for
    the case with the takeover origin: it keeps the case number, banding date, appliance, planned
    treatment months and treatment fee of the establishment entry it supersedes, and records the
    participation agreement and network status of the practice now treating the patient, the
    months of treatment still to come and the fee Cascade recognises for the covered treatment as
    given. No payment is made or taken back by this call. Afterwards the case
    history shows the takeover entry as its latest establishment; the returned receipt carries the
    reference of the new entry, which signals that the re-establishment was recorded.

    Args:
        ortho_rider_id: Id class — the identifier (reference number) of the patient's orthodontic rider, as returned by the orthodontic rider lookup for the subscriber.
        ortho_case_event_id: Id class — the identifier (reference number) of the establishment entry being superseded, as returned by the orthodontic case lookup for that rider.
        provider_agreement_id: Id class — the identifier (reference number) of the participation agreement in force for the practice now treating the patient on the date of the takeover entry, as returned by the provider agreement lookup; pass an empty string when that practice holds no Cascade agreement.
        network_status: Enum class — network status of the practice now treating the patient on the date of the takeover entry: in_network when it holds a Cascade PPO or Premier participating agreement in force on that day with the orthodontist specialty; out_of_network otherwise.
        months_remaining: Fixed-format class — months of planned treatment still to come when coverage of the case begins, an integer number of months.
        allowed_case_fee: Fixed-format class — the fee Cascade recognises for the covered treatment, in USD, 2 decimal places, rounded half up to the cent; the value is stored as given.

    Returns:
        A text rendering of a dictionary with these keys: establishment_entry (string, the reference of
        the new takeover entry), case_number (string), case_origin (string, always takeover),
        network_status (string),
        months_remaining (integer), allowed_case_fee (number, USD with 2 decimal places) and event_date
        (string, YYYY-MM-DD). A receipt carrying an establishment_entry reference means the case is now
        recorded as a takeover.
    """
    old = ctx.find("ortho_cases", ortho_case_event_id=ortho_case_event_id)
    src = old[0] if old else {}
    rid = ctx.make_id("otk_", ortho_rider_id, ortho_case_event_id, provider_agreement_id, network_status,
                      months_remaining, allowed_case_fee)
    day = ctx.now()[:10]
    ctx.create("ortho_cases", rid, ortho_case_event_id=rid, ortho_rider_id=ortho_rider_id,
               customer_id=src.get("customer_id", ""), event_type="ortho_case_established",
               case_number=src.get("case_number", ""), provider_agreement_id=provider_agreement_id or None,
               network_status=network_status, case_origin="takeover",
               appliance_type=src.get("appliance_type", ""), banding_date=src.get("banding_date", ""),
               treatment_months=src.get("treatment_months", 0), months_remaining=int(months_remaining),
               total_case_fee=src.get("total_case_fee", 0.0), allowed_case_fee=round(float(allowed_case_fee), 2),
               event_date=day, closure_reason="not_closed", original_case_event_id=None)
    return str({"establishment_entry": rid, "case_number": src.get("case_number", ""), "case_origin": "takeover",
                "network_status": network_status, "months_remaining": int(months_remaining), "allowed_case_fee": round(float(allowed_case_fee), 2),
                "event_date": day})


@tool(owner="user", rw="write")
def repay_ortho_overpayment_ce1ed3cf(ctx: ToolContext, original_ortho_payment_id: str, amount: float) -> str:
    """The member pays back money Cascade overpaid on an orthodontic case. One call records the
    member's repayment as a reversal of the stated orthodontic payment for the stated amount, dated
    today, keeping that payment's case, installment position, service period and payee, and takes
    the amount off the orthodontic benefit paid under the rider. The member can see the repayment in
    the case payment history; the returned receipt carries the reference of the reversal, which
    signals that the repayment was recorded.

    Args:
        original_ortho_payment_id: Id class — the identifier (reference number) of the orthodontic payment the repayment is recorded against, as returned by the orthodontic payment lookup and read out by the agent.
        amount: Fixed-format class — the amount the member repays, in USD, 2 decimal places, always positive, rounded half up to the cent; the value is recorded as given.

    Returns:
        A text rendering of a dictionary with these keys: reversal (string, the reference of the
        repayment entry), case_number (string), amount (number, USD with 2 decimal places), payment_date
        (string, YYYY-MM-DD) and lifetime_benefit_paid (number, USD with 2 decimal places, the
        orthodontic benefit paid under the rider after the repayment). A receipt carrying a reversal
        reference means the repayment was recorded.
    """
    orig = ctx.find("ortho_payments", ortho_payment_id=original_ortho_payment_id)
    src = orig[0] if orig else {}
    rider_id = src.get("ortho_rider_id", "")
    rid = ctx.make_id("orv_", original_ortho_payment_id, amount)
    day = ctx.now()[:10]
    ctx.create("ortho_payments", rid, ortho_payment_id=rid, ortho_rider_id=rider_id,
               customer_id=src.get("customer_id", ""), event_type="ortho_payment_reversal",
               ortho_case_event_id=src.get("ortho_case_event_id", ""), case_number=src.get("case_number", ""),
               installment_number=src.get("installment_number", 0), service_period=src.get("service_period", ""),
               payee=src.get("payee", ""), provider_agreement_id=src.get("provider_agreement_id"),
               amount=round(float(amount), 2), payment_date=day, original_ortho_payment_id=original_ortho_payment_id)
    riders = ctx.find("ortho_riders", ortho_rider_id=rider_id)
    paid = round(float((riders[0] if riders else {}).get("lifetime_benefit_paid") or 0) - round(float(amount), 2), 2)
    if riders:
        ctx.update("ortho_riders", rider_id, lifetime_benefit_paid=paid)
    return str({"reversal": rid, "case_number": src.get("case_number", ""), "amount": round(float(amount), 2),
                "payment_date": day, "lifetime_benefit_paid": paid})

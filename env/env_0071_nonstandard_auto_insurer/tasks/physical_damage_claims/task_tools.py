"""Hidden task tools of the physical_damage_claims difficulty (category physdam) of
env_0071_nonstandard_auto_insurer. Each tool performs one atomic write with the values the agent
has already worked out; none of them checks a business precondition.
"""

from erlbench import ToolContext, tool


@tool(owner="user", rw="write")
def assign_repair_payment_77b6ee43(ctx: ToolContext, physdam_coverage_id: str, claim_number: str,
                                   estimate_sequence: int, amount: float, deductible_applied: float) -> str:
    """The named insured signs a direction to pay on their own physical damage claim, so that the
    repair payment for one estimate of the claim is issued straight to the repair facility. One call
    books one repair payment on the claim, made out to the repair facility and dated today, records
    the deductible withheld from it and the estimate it pays, and adds the payment to the net claim
    payments of the vehicle coverage. The insured sees the payment confirmation and the facility
    receives the funds.

    Args:
        physdam_coverage_id: Id class — the coverage id, the record identifier of the vehicle's comprehensive and collision coverage the claim belongs to, read from the coverage lookup before the call.
        claim_number: Fixed-format class — the claim number the payment belongs to, in the format CLM-<9 digits>, exactly as it appears on the claim's file entries.
        estimate_sequence: Fixed-format class — the sequence number of the estimate or supplement this payment pays, an integer of 1 or more (whole-number precision), as recorded on that estimate entry.
        amount: Fixed-format class — the repair payment issued to the repair facility, in US dollars as a positive number with 2 decimal places, rounded to the nearest cent.
        deductible_applied: Fixed-format class — the deductible withheld from this payment, in US dollars with 2 decimal places, rounded to the nearest cent; 0.00 when none is withheld.

    Returns:
        A one-line confirmation string naming the new payment reference (a text id), the claim
        number, the estimate sequence paid, the amount issued to the repair facility in USD with
        2 decimals, the deductible withheld in USD with 2 decimals, the payment date (YYYY-MM-DD)
        and the coverage's net claim payments after the payment in USD with 2 decimals; a string
        starting with "Repair payment issued" means the payment was booked.
    """
    amt = round(float(amount), 2)
    ded = round(float(deductible_applied), 2)
    seq = int(estimate_sequence)
    day = ctx.now()[:10]
    cov = ctx.find("physdam_coverages", physdam_coverage_id=physdam_coverage_id)
    cust = cov[0].get("customer_id") if cov else ""
    rid = ctx.make_id("pdpay_", physdam_coverage_id, claim_number, seq, amt, ded)
    ctx.create("physdam_claim_payments", rid, physdam_payment_id=rid, physdam_coverage_id=physdam_coverage_id,
               customer_id=cust, event_type="physdam_repair_payment", claim_number=claim_number,
               payment_date=day, amount=amt, payee_type="repair_facility", deductible_applied=ded,
               sales_tax_amount=0.0, title_fee_amount=0.0, estimate_sequence=seq)
    net = round(float((cov[0].get("net_loss_paid_total") if cov else 0) or 0) + amt, 2)
    ctx.update("physdam_coverages", physdam_coverage_id, net_loss_paid_total=net)
    return (f"Repair payment issued: {rid} on {claim_number}, estimate {seq}, {amt:.2f} USD to the repair facility, "
            f"deductible withheld {ded:.2f} USD, dated {day}; coverage net claim payments now {net:.2f} USD.")


@tool(owner="agent", rw="write")
def issue_deductible_refund_f60554e2(ctx: ToolContext, physdam_coverage_id: str, claim_number: str,
                                     amount: float) -> str:
    """Issue to the named insured a refund of part or all of the deductible on one physical damage
    claim. One call books one deductible refund payment on the claim, made out to the named insured
    and dated today, and adds it to the net claim payments of the vehicle coverage. The insured can
    be told the refund amount and date as soon as it is booked.

    Args:
        physdam_coverage_id: Id class — the coverage id, the record identifier of the vehicle's comprehensive and collision coverage the claim belongs to, read from the coverage lookup before the call.
        claim_number: Fixed-format class — the claim number the refund belongs to, in the format CLM-<9 digits>, exactly as it appears on the claim's file entries.
        amount: Fixed-format class — the deductible refund paid to the named insured, in US dollars as a positive number with 2 decimal places, rounded to the nearest cent.

    Returns:
        A one-line confirmation string naming the new refund payment reference (a text id), the
        claim number, the refund amount in USD with 2 decimals, the payment date (YYYY-MM-DD) and the
        coverage's net claim payments after the refund in USD with 2 decimals; a string starting with
        "Deductible refund issued" means the refund was booked.
    """
    amt = round(float(amount), 2)
    day = ctx.now()[:10]
    cov = ctx.find("physdam_coverages", physdam_coverage_id=physdam_coverage_id)
    cust = cov[0].get("customer_id") if cov else ""
    rid = ctx.make_id("pdref_", physdam_coverage_id, claim_number, amt)
    ctx.create("physdam_claim_payments", rid, physdam_payment_id=rid, physdam_coverage_id=physdam_coverage_id,
               customer_id=cust, event_type="physdam_deductible_reimbursement", claim_number=claim_number,
               payment_date=day, amount=amt, payee_type="named_insured", deductible_applied=0.0,
               sales_tax_amount=0.0, title_fee_amount=0.0, estimate_sequence=0)
    net = round(float((cov[0].get("net_loss_paid_total") if cov else 0) or 0) + amt, 2)
    ctx.update("physdam_coverages", physdam_coverage_id, net_loss_paid_total=net)
    return (f"Deductible refund issued: {rid} on {claim_number}, {amt:.2f} USD to the named insured, dated {day}; "
            f"coverage net claim payments now {net:.2f} USD.")


@tool(owner="agent", rw="write")
def pay_loss_payee_settlement_0684ec8f(ctx: ToolContext, physdam_coverage_id: str, claim_number: str,
                                       amount: float, deductible_applied: float) -> str:
    """Issue the vehicle-value part of a total loss settlement to the loss payee (the lienholder or
    lessor named on the vehicle's coverage). One call books one total loss payment on the claim, made
    out to the loss payee and dated today, records the deductible withheld from it, and adds the
    payment to the net claim payments of the vehicle coverage. The loss payee receives the funds and
    the insured can be told the amount sent.

    Args:
        physdam_coverage_id: Id class — the coverage id, the record identifier of the vehicle's comprehensive and collision coverage the claim belongs to, read from the coverage lookup before the call.
        claim_number: Fixed-format class — the claim number the payment belongs to, in the format CLM-<9 digits>, exactly as it appears on the claim's file entries.
        amount: Fixed-format class — the total loss payment issued to the loss payee, in US dollars as a positive number with 2 decimal places, rounded to the nearest cent.
        deductible_applied: Fixed-format class — the deductible withheld from this payment, in US dollars with 2 decimal places, rounded to the nearest cent; 0.00 when none is withheld.

    Returns:
        A one-line confirmation string naming the new payment reference (a text id), the claim
        number, the amount issued to the loss payee in USD with 2 decimals, the deductible withheld in
        USD with 2 decimals, the payment date (YYYY-MM-DD) and the coverage's net claim payments after
        the payment in USD with 2 decimals; a string starting with "Loss payee payment issued" means
        the payment was booked.
    """
    amt = round(float(amount), 2)
    ded = round(float(deductible_applied), 2)
    day = ctx.now()[:10]
    cov = ctx.find("physdam_coverages", physdam_coverage_id=physdam_coverage_id)
    cust = cov[0].get("customer_id") if cov else ""
    rid = ctx.make_id("pdtlp_", physdam_coverage_id, claim_number, amt, ded)
    ctx.create("physdam_claim_payments", rid, physdam_payment_id=rid, physdam_coverage_id=physdam_coverage_id,
               customer_id=cust, event_type="physdam_total_loss_payment", claim_number=claim_number,
               payment_date=day, amount=amt, payee_type="loss_payee", deductible_applied=ded,
               sales_tax_amount=0.0, title_fee_amount=0.0, estimate_sequence=0)
    net = round(float((cov[0].get("net_loss_paid_total") if cov else 0) or 0) + amt, 2)
    ctx.update("physdam_coverages", physdam_coverage_id, net_loss_paid_total=net)
    return (f"Loss payee payment issued: {rid} on {claim_number}, {amt:.2f} USD to the loss payee, "
            f"deductible withheld {ded:.2f} USD, dated {day}; coverage net claim payments now {net:.2f} USD.")


@tool(owner="user", rw="write")
def accept_total_loss_settlement_6ed13516(ctx: ToolContext, physdam_coverage_id: str, claim_number: str,
                                          amount: float, sales_tax_amount: float, title_fee_amount: float) -> str:
    """The named insured accepts their own part of a total loss settlement on their claim, and with
    the acceptance the owner's payment is issued to them. One call books one total loss payment on the
    claim, made out to the named insured and dated today, records the sales tax and the title fee it
    carries, and adds the payment to the net claim payments of the vehicle coverage. The insured sees
    the payment confirmation.

    Args:
        physdam_coverage_id: Id class — the coverage id, the record identifier of the vehicle's comprehensive and collision coverage the claim belongs to, read from the coverage lookup before the call.
        claim_number: Fixed-format class — the claim number the payment belongs to, in the format CLM-<9 digits>, exactly as it appears on the claim's file entries.
        amount: Fixed-format class — the total payment issued to the named insured, in US dollars as a positive number with 2 decimal places, rounded to the nearest cent.
        sales_tax_amount: Fixed-format class — the sales tax included in the payment, in US dollars with 2 decimal places, rounded to the nearest cent; 0.00 when none.
        title_fee_amount: Fixed-format class — the title fee included in the payment, in US dollars with 2 decimal places, rounded to the nearest cent; 0.00 when none.

    Returns:
        A one-line confirmation string naming the new payment reference (a text id), the claim
        number, the amount issued to the named insured in USD with 2 decimals, the sales tax and the
        title fee it includes in USD with 2 decimals, the payment date (YYYY-MM-DD) and the coverage's
        net claim payments after the payment in USD with 2 decimals; a string starting with
        "Settlement payment issued" means the payment was booked.
    """
    amt = round(float(amount), 2)
    tax = round(float(sales_tax_amount), 2)
    fee = round(float(title_fee_amount), 2)
    day = ctx.now()[:10]
    cov = ctx.find("physdam_coverages", physdam_coverage_id=physdam_coverage_id)
    cust = cov[0].get("customer_id") if cov else ""
    rid = ctx.make_id("pdtli_", physdam_coverage_id, claim_number, amt, tax, fee)
    ctx.create("physdam_claim_payments", rid, physdam_payment_id=rid, physdam_coverage_id=physdam_coverage_id,
               customer_id=cust, event_type="physdam_total_loss_payment", claim_number=claim_number,
               payment_date=day, amount=amt, payee_type="named_insured", deductible_applied=0.0,
               sales_tax_amount=tax, title_fee_amount=fee, estimate_sequence=0)
    net = round(float((cov[0].get("net_loss_paid_total") if cov else 0) or 0) + amt, 2)
    ctx.update("physdam_coverages", physdam_coverage_id, net_loss_paid_total=net)
    return (f"Settlement payment issued: {rid} on {claim_number}, {amt:.2f} USD to the named insured "
            f"(sales tax {tax:.2f} USD, title fee {fee:.2f} USD), dated {day}; "
            f"coverage net claim payments now {net:.2f} USD.")


@tool(owner="agent", rw="write")
def remove_totaled_coverage_12b8272a(ctx: ToolContext, physdam_coverage_id: str, amount: float,
                                     premium_days: int, vehicle_term_coverage_premium: float) -> str:
    """Remove a vehicle's comprehensive and collision coverage at the named insured's request, effective
    today, and book the premium returned for it. One call sets the coverage to removed with the
    insured's request as the reason and today as its end date, books one coverage premium return dated
    today with the full-term rate and the days it is figured on, and lowers the coverage's net premium
    by the amount returned. The insured can be told the coverage has ended and the amount returned.

    Args:
        physdam_coverage_id: Id class — the coverage id, the record identifier of the vehicle's comprehensive and collision coverage to remove, read from the coverage lookup before the call.
        amount: Fixed-format class — the premium returned, in US dollars as a number of 0.00 or more with 2 decimal places, rounded to the nearest cent.
        premium_days: Fixed-format class — the number of calendar days the return is figured on, an integer of 0 or more (whole-number precision).
        vehicle_term_coverage_premium: Fixed-format class — the full-term coverage premium rate the return is figured on, in US dollars with 2 decimal places, rounded to the nearest cent.

    Returns:
        A one-line confirmation string naming the new premium return reference (a text id), the
        coverage's new status (removed), the removal date (YYYY-MM-DD), the amount returned in USD with
        2 decimals, the days and the full-term rate it was figured on, and the coverage's net premium
        after the return in USD with 2 decimals; a string starting with "Coverage removed" means the
        removal and the return were booked.
    """
    amt = round(float(amount), 2)
    rate = round(float(vehicle_term_coverage_premium), 2)
    days = int(premium_days)
    day = ctx.now()[:10]
    cov = ctx.find("physdam_coverages", physdam_coverage_id=physdam_coverage_id)
    row = cov[0] if cov else {}
    term = ctx.find("auto_policies", auto_policy_id=row.get("auto_policy_id")) if row.get("auto_policy_id") else []
    term_days = int((term[0].get("term_days") if term else 0) or 0)
    rid = ctx.make_id("pdret_", physdam_coverage_id, amt, days, rate)
    ctx.create("physdam_premium_transactions", rid, physdam_premium_txn_id=rid, physdam_coverage_id=physdam_coverage_id,
               customer_id=row.get("customer_id", ""), event_type="physdam_premium_returned", transaction_date=day,
               effective_date=day, amount=amt, vehicle_term_coverage_premium=rate, premium_days=days,
               owner_term_days=term_days, transaction_reason="coverage_removed")
    net = round(float(row.get("term_coverage_premium") or 0) - amt, 2)
    ctx.update("physdam_coverages", physdam_coverage_id, status="removed", removal_reason="insured_request",
               closed_date=day, term_coverage_premium=net)
    return (f"Coverage removed: {physdam_coverage_id} is now removed as of {day}; premium return {rid} of {amt:.2f} USD "
            f"figured on {days} days at a full-term rate of {rate:.2f} USD; coverage net premium now {net:.2f} USD.")

"""Hidden task tools for the optional_coverage_riders difficulty (Bridgewell Optional Coverage Add-Ons).

Each tool performs one atomic business write on a rider and its own ledger. None of them checks a
policy condition, an eligibility gate or a prerequisite: the amounts and choices passed in are worked
out by the agent from the published policy and the records, and the tool books them as given.
"""

from erlbench import ToolContext, tool


@tool(owner="agent", rw="write")
def post_rider_premium_correction_851994d3(ctx: ToolContext, addon_rider_id: str, billing_period_start: str,
                                            amount: float) -> str:
    """Post one premium billing correction to an optional coverage rider's billing ledger, correcting a
    rider premium already charged down to the amount that was due. The correction is booked as a new
    premium credit entry dated today against the rider named, with the reason billing_correction and
    the billing period it relates to, and the rider's premium balance goes down by the credited amount
    (a negative balance means money owed back to the customer). The customer sees the credit on the
    rider's billing history immediately; the receipt below confirms it was booked.

    Args:
        addon_rider_id: Id class — the rider reference number of the optional coverage rider being
            credited, as returned by the rider lookup for this customer.
        billing_period_start: Fixed-format class — the first day of the billing period the credit
            relates to, copied from the premium charge entry being credited, written as YYYY-MM-DD.
        amount: Fixed-format class — the credit in USD, a positive amount with 2 decimal places
            (rounded to the nearest cent before it is booked).

    Returns:
        A confirmation string of the form "Rider premium billing correction <entry reference> posted on
        rider <rider reference>: USD <amount> for the period starting <YYYY-MM-DD>; rider premium balance
        now USD <balance>." The entry reference is the new billing entry's reference number,
        the amount and balance are USD with 2 decimal places, and the presence of the entry reference
        means the credit was booked.
    """
    rid = ctx.make_id("abe_", addon_rider_id, billing_period_start, amount)
    riders = ctx.find("addon_riders", addon_rider_id=addon_rider_id)
    rider = riders[0] if riders else {}
    credited = round(float(amount), 2)
    ctx.create("addon_billing_entries", rid, addon_billing_entry_id=rid, addon_rider_id=addon_rider_id,
               customer_id=rider.get("customer_id"), event_type="addon_premium_credit",
               entry_date=ctx.now()[:10], amount=credited, credit_reason="billing_correction",
               billing_period_start=billing_period_start)
    balance = round(float(rider.get("premium_balance") or 0) - credited, 2)
    ctx.update("addon_riders", addon_rider_id, premium_balance=balance)
    return (f"Rider premium billing correction {rid} posted on rider {addon_rider_id}: USD {credited:.2f} "
            f"for the period starting {billing_period_start}; rider premium balance now USD {balance:.2f}.")


@tool(owner="agent", rw="write")
def authorize_rider_work_f2a2f75a(ctx: ToolContext, addon_service_request_id: str, resolution_type: str,
                                  amount: float) -> str:
    """Issue one work authorization on a rider service request: Bridgewell commits to pay for the
    failed component to be repaired, or to be replaced with a like unit. The authorization is booked
    as a new authorization entry dated today on the request's handling history, under a newly issued
    authorization number, with the component taken from the request and the repair estimate and
    contracted replacement cost taken from the request's latest coverage determination; the amount is
    what Bridgewell commits to pay for that work. This tool books repair or replacement work only. The
    customer and the contractor can see the authorization number and amount on the request right
    away; the receipt below confirms it.

    Args:
        addon_service_request_id: Id class — the rider service request number the authorization is
            issued on, as returned by the rider service request lookup.
        resolution_type: Enum class — the work authorized, one of: repair when the contractor repairs
            the failed component in place; replacement when the failed component is removed and
            replaced with a like unit. Any other value is booked as repair.
        amount: Fixed-format class — the amount Bridgewell pays for the work, in USD, a non-negative
            amount with 2 decimal places (rounded to the nearest cent before it is booked).

    Returns:
        A confirmation string of the form "Work authorization <authorization number> issued on rider
        service request <request number>: <repair or replacement> of <component>, USD <amount>." The
        authorization number is the newly issued reference, the amount is USD with 2 decimal places,
        and its presence means the authorization was booked.
    """
    work = "replacement" if resolution_type == "replacement" else "repair"
    rid = ctx.make_id("acw_", addon_service_request_id, work, amount)
    auth_no = ctx.make_id("4w", addon_service_request_id, work, amount)
    requests = ctx.find("addon_service_requests", addon_service_request_id=addon_service_request_id)
    req = requests[0] if requests else {}
    dets = ctx.find("addon_claim_events", addon_service_request_id=addon_service_request_id,
                    event_type="addon_coverage_determination")
    det = sorted(dets, key=lambda r: str(r.get("event_date")))[-1] if dets else {}
    paid = round(float(amount), 2)
    ctx.create("addon_claim_events", rid, addon_claim_event_id=rid, addon_rider_id=req.get("addon_rider_id"),
               customer_id=req.get("customer_id"), event_type="addon_benefit_authorization",
               addon_service_request_id=addon_service_request_id, event_date=ctx.now()[:10],
               component=req.get("component"), authorization_number=auth_no, resolution_type=work,
               repair_estimate=det.get("repair_estimate"), replacement_cost=det.get("replacement_cost"),
               amount=paid)
    return (f"Work authorization {auth_no} issued on rider service request {addon_service_request_id}: "
            f"{work} of {req.get('component')}, USD {paid:.2f}.")


@tool(owner="user", rw="write")
def remove_rider_with_credit_c919c4de(ctx: ToolContext, addon_rider_id: str, amount: float) -> str:
    """The customer removes one of their own optional coverage riders while keeping the base contract,
    and the unused rider premium returned for it is booked in the same step. The rider's status becomes
    removed with today as its end date, a premium credit entry dated today with the reason
    rider_removal_credit is added to the rider's billing ledger for the rider's current term, and the rider's premium balance goes down by the
    credited amount. The customer sees the rider as removed and the credit on its billing history; the
    receipt below confirms both.

    Args:
        addon_rider_id: Id class — the rider reference number of the customer's rider being removed,
            as the agent read it from the rider lookup and gave it to the customer.
        amount: Fixed-format class — the credit for the unused rider premium, in USD, a non-negative
            amount with 2 decimal places (rounded to the nearest cent before it is booked).

    Returns:
        A confirmation string of the form "Rider <rider reference> removed effective <YYYY-MM-DD>;
        removal credit <entry reference> of USD <amount> posted; rider premium balance now USD
        <balance>." The effective date is today, the entry reference is the new billing entry's
        reference number, amounts are USD with 2 decimal places, and the confirmation means the
        removal and the credit were both booked.
    """
    today = ctx.now()[:10]
    riders = ctx.find("addon_riders", addon_rider_id=addon_rider_id)
    rider = riders[0] if riders else {}
    credited = round(float(amount), 2)
    rid = ctx.make_id("abe_", addon_rider_id, "rider_removal_credit", amount)
    ctx.create("addon_billing_entries", rid, addon_billing_entry_id=rid, addon_rider_id=addon_rider_id,
               customer_id=rider.get("customer_id"), event_type="addon_premium_credit", entry_date=today,
               amount=credited, credit_reason="rider_removal_credit",
               billing_period_start=rider.get("term_start_date"))
    balance = round(float(rider.get("premium_balance") or 0) - credited, 2)
    ctx.update("addon_riders", addon_rider_id, status="removed", end_date=today, premium_balance=balance)
    return (f"Rider {addon_rider_id} removed effective {today}; removal credit {rid} of USD {credited:.2f} "
            f"posted; rider premium balance now USD {balance:.2f}.")


@tool(owner="agent", rw="write")
def charge_rider_visit_fee_fc58860f(ctx: ToolContext, addon_service_request_id: str, amount: float) -> str:
    """Collect the service call fee on one rider service request. The fee is booked as a new service
    call fee entry dated today on the billing ledger of the rider the request was placed under, linked
    to that request, and counts toward the service call fees collected on the rider. The customer sees
    the fee on the rider's billing history right away; the receipt below confirms it was booked.

    Args:
        addon_service_request_id: Id class — the rider service request number the fee is collected on,
            as returned by the rider service request lookup.
        amount: Fixed-format class — the service call fee in USD, a non-negative amount with 2 decimal
            places (rounded to the nearest cent before it is booked).

    Returns:
        A confirmation string of the form "Service call fee <entry reference> of USD <amount> collected
        on rider service request <request number> under rider <rider reference>." The entry reference is
        the new billing entry's reference number, the amount is USD with 2 decimal places, and its
        presence means the fee was booked.
    """
    rid = ctx.make_id("abe_", addon_service_request_id, amount)
    requests = ctx.find("addon_service_requests", addon_service_request_id=addon_service_request_id)
    req = requests[0] if requests else {}
    fee = round(float(amount), 2)
    ctx.create("addon_billing_entries", rid, addon_billing_entry_id=rid, addon_rider_id=req.get("addon_rider_id"),
               customer_id=req.get("customer_id"), event_type="addon_service_fee_charge",
               entry_date=ctx.now()[:10], amount=fee, addon_service_request_id=addon_service_request_id)
    return (f"Service call fee {rid} of USD {fee:.2f} collected on rider service request {addon_service_request_id} "
            f"under rider {req.get('addon_rider_id')}.")


@tool(owner="agent", rw="write")
def authorize_haul_away_allowance_ee656dca(ctx: ToolContext, addon_service_request_id: str, amount: float) -> str:
    """Issue a haul-away allowance on one rider service request, paying toward removing and disposing
    of the component replaced under that request. The allowance is booked as a new allowance
    authorization dated today on the request's handling history, under a newly issued authorization
    number, with the component taken from the request and the documented removal cost taken from the
    request's latest coverage determination; the amount is what Bridgewell pays toward the removal. The
    customer and contractor can see the authorization number and amount on the request right away.

    Args:
        addon_service_request_id: Id class — the rider service request number on which the replaced
            component was authorized, as returned by the rider service request lookup.
        amount: Fixed-format class — the haul-away allowance in USD, a non-negative amount with 2
            decimal places (rounded to the nearest cent before it is booked).

    Returns:
        A confirmation string of the form "Haul-away allowance <authorization number> issued on rider
        service request <request number> for <component>: USD <amount> against a documented removal
        cost of USD <cost>." The authorization number is the newly issued reference, amounts are USD
        with 2 decimal places, and the confirmation means the allowance was booked.
    """
    rid = ctx.make_id("ace_", addon_service_request_id, "haul_away", amount)
    auth_no = ctx.make_id("4", addon_service_request_id, "haul_away", amount)
    requests = ctx.find("addon_service_requests", addon_service_request_id=addon_service_request_id)
    req = requests[0] if requests else {}
    dets = ctx.find("addon_claim_events", addon_service_request_id=addon_service_request_id,
                    event_type="addon_coverage_determination")
    det = sorted(dets, key=lambda r: str(r.get("event_date")))[-1] if dets else {}
    paid = round(float(amount), 2)
    ctx.create("addon_claim_events", rid, addon_claim_event_id=rid, addon_rider_id=req.get("addon_rider_id"),
               customer_id=req.get("customer_id"), event_type="addon_benefit_authorization",
               addon_service_request_id=addon_service_request_id, event_date=ctx.now()[:10],
               component=req.get("component"), authorization_number=auth_no, resolution_type="allowance",
               allowance_type="haul_away", invoice_amount=det.get("invoice_amount"), amount=paid)
    return (f"Haul-away allowance {auth_no} issued on rider service request {addon_service_request_id} for "
            f"{req.get('component')}: USD {paid:.2f} against a documented removal cost of USD {det.get('invoice_amount')}.")


@tool(owner="user", rw="write")
def accept_rider_cash_settlement_51ff485a(ctx: ToolContext, addon_service_request_id: str, amount: float) -> str:
    """The customer accepts a cash settlement on one of their own covered rider service requests in
    place of having Bridgewell replace the failed component. The settlement is booked as a new
    cash-in-lieu authorization dated today on the request's handling history, under a newly issued
    authorization number, with the component taken from the request and the repair estimate and
    contracted replacement cost taken from the request's latest coverage determination; the amount is
    the cash Bridgewell pays the customer. The customer sees the authorization number and the cash
    amount right away; the receipt below confirms the settlement was booked.

    Args:
        addon_service_request_id: Id class — the rider service request number being settled in cash, as
            the agent read it from the rider service request lookup and gave it to the customer.
        amount: Fixed-format class — the cash settlement in USD, a non-negative amount with 2 decimal
            places (rounded to the nearest cent before it is booked).

    Returns:
        A confirmation string of the form "Cash settlement <authorization number> accepted on rider
        service request <request number> for <component>: USD <amount>." The authorization number is the
        newly issued reference, the amount is USD with 2 decimal places, and the confirmation means the
        settlement was booked.
    """
    rid = ctx.make_id("ace_", addon_service_request_id, "cash_in_lieu", amount)
    auth_no = ctx.make_id("4", addon_service_request_id, "cash_in_lieu", amount)
    requests = ctx.find("addon_service_requests", addon_service_request_id=addon_service_request_id)
    req = requests[0] if requests else {}
    dets = ctx.find("addon_claim_events", addon_service_request_id=addon_service_request_id,
                    event_type="addon_coverage_determination")
    det = sorted(dets, key=lambda r: str(r.get("event_date")))[-1] if dets else {}
    cash = round(float(amount), 2)
    ctx.create("addon_claim_events", rid, addon_claim_event_id=rid, addon_rider_id=req.get("addon_rider_id"),
               customer_id=req.get("customer_id"), event_type="addon_benefit_authorization",
               addon_service_request_id=addon_service_request_id, event_date=ctx.now()[:10],
               component=req.get("component"), authorization_number=auth_no, resolution_type="cash_in_lieu",
               repair_estimate=det.get("repair_estimate"), replacement_cost=det.get("replacement_cost"), amount=cash)
    return (f"Cash settlement {auth_no} accepted on rider service request {addon_service_request_id} for "
            f"{req.get('component')}: USD {cash:.2f}.")

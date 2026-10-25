"""Hidden task tools for the homeowner_claims_and_replacement difficulty (Bridgewell Homeowner Service Contracts).

Each tool lands exactly one business action on a homeowner service contract's claim-handling history. The
values a tool records come from the published Bridgewell rules and the account's records;
the tools themselves judge nothing and compute nothing.
"""

from erlbench import ToolContext, tool


@tool(owner="agent", rw="write")
def authorize_stalled_repair_replacement_b6f80e12(ctx: ToolContext, homeplan_contract_id: str,
                                                   homeplan_service_request_id: str, covered_item: str,
                                                   repair_estimate: float, replacement_cost: float,
                                                   amount: float) -> str:
    """Record Bridgewell's authorization to replace a covered item on a homeowner service request because the
    repair it had authorized could not be carried out for want of parts. One call adds one replacement
    authorization, with the reason parts_unavailable, to the request's claim-handling history and issues a new
    authorization number; the amount recorded is what Bridgewell commits toward the replacement and it counts
    against the contract's benefits from today. On success the request shows the new replacement
    authorization with its number, basis and amount.

    Args:
        homeplan_contract_id: Id class — the homeowner service contract number the request is placed under, as
            returned by the homeowner contract lookup.
        homeplan_service_request_id: Id class — the service request number of the failed item being replaced, as
            returned by the service request or claim-history lookup.
        covered_item: Enum class — the item being replaced, one of: heating_system (the furnace, boiler or heat
            pump heating side), cooling_system (the central air conditioning), ductwork (heating and cooling
            ducts), plumbing_leak (an interior water supply or drain leak), plumbing_stoppage (an interior drain
            stoppage), water_heater (the water heater), electrical (the interior electrical system), ceiling_fan
            (a ceiling fan), garbage_disposal (the garbage disposal), whirlpool_tub (the whirlpool bathtub motor
            and pump), refrigerator (the kitchen refrigerator), oven_range_cooktop (the oven, range or cooktop),
            dishwasher (the dishwasher), built_in_microwave (the built-in microwave), clothes_washer (the clothes
            washer), clothes_dryer (the clothes dryer), garage_door_opener (the garage door opener).
        repair_estimate: Fixed-format class — the contractor's repair estimate that was compared, in USD, rounded
            to 2 decimal places, positive.
        replacement_cost: Fixed-format class — the like-unit cost (equipment plus installation) to record on the
            authorization as its replacement_cost, in USD, rounded to 2 decimal places, positive.
        amount: Fixed-format class — the amount Bridgewell commits toward the replacement, in USD, rounded to 2
            decimal places, positive.

    Returns:
        A dict confirming the authorization: authorization_number (the new replacement authorization number,
        text), homeplan_service_request_id (the request it was issued on), covered_item (the item replaced),
        replacement_basis (always parts_unavailable), amount (USD, 2 decimal places) and status ("authorized"
        when the authorization was recorded).
    """
    auth = ctx.make_id("RPA-", homeplan_contract_id, homeplan_service_request_id, covered_item,
                       repair_estimate, replacement_cost, amount)
    ctx.create("homeplan_claim_events", auth, homeplan_claim_event_id=auth,
               homeplan_contract_id=homeplan_contract_id, event_type="homeplan_replacement_authorization",
               homeplan_service_request_id=homeplan_service_request_id, event_date=ctx.now()[:10],
               covered_item=covered_item, authorization_number=auth,
               repair_estimate=round(float(repair_estimate), 2),
               replacement_cost=round(float(replacement_cost), 2),
               replacement_basis="parts_unavailable", amount=round(float(amount), 2))
    return str({"authorization_number": auth, "homeplan_service_request_id": homeplan_service_request_id,
                "covered_item": covered_item, "replacement_basis": "parts_unavailable",
                "amount": round(float(amount), 2), "status": "authorized"})


@tool(owner="user", rw="write")
def elect_cash_in_place_of_replacement_7cf483ad(ctx: ToolContext, homeplan_contract_id: str,
                                                homeplan_service_request_id: str, covered_item: str,
                                                replaced_authorization_number: str, replaced_amount: float,
                                                cash_amount: float) -> str:
    """The homeowner takes cash in place of a replacement Bridgewell has authorized for them. One call records
    the customer's own cash settlement on the service request, issues a cash settlement number, and, in the
    same action, reverses in full the replacement authorization the cash takes the place of. On success the
    request shows a customer-elected cash payment and no standing replacement; the cash is what Bridgewell
    pays the homeowner and no unit will be installed on that request.

    Args:
        homeplan_contract_id: Id class — the homeowner service contract number the request is placed under, as
            the agent reads it from the contract record.
        homeplan_service_request_id: Id class — the service request number on which the cash is taken, as the
            agent reads it from the claim history.
        covered_item: Enum class — the item settled in cash, one of: heating_system (the furnace, boiler or heat
            pump heating side), cooling_system (the central air conditioning), ductwork (heating and cooling
            ducts), plumbing_leak (an interior water supply or drain leak), plumbing_stoppage (an interior drain
            stoppage), water_heater (the water heater), electrical (the interior electrical system), ceiling_fan
            (a ceiling fan), garbage_disposal (the garbage disposal), whirlpool_tub (the whirlpool bathtub motor
            and pump), refrigerator (the kitchen refrigerator), oven_range_cooktop (the oven, range or cooktop),
            dishwasher (the dishwasher), built_in_microwave (the built-in microwave), clothes_washer (the clothes
            washer), clothes_dryer (the clothes dryer), garage_door_opener (the garage door opener).
        replaced_authorization_number: Id class — the number of the replacement authorization the cash takes the
            place of, as shown on that authorization in the claim history.
        replaced_amount: Fixed-format class — the amount recorded on the replacement authorization being
            reversed, in USD, rounded to 2 decimal places, positive.
        cash_amount: Fixed-format class — the cash the homeowner receives, in USD, rounded to 2 decimal places,
            positive.

    Returns:
        A dict confirming the settlement: settlement_number (the cash settlement number issued, text),
        homeplan_service_request_id (the request settled), cash_amount (USD, 2 decimal places),
        settlement_basis (always customer_elected), reversed_authorization_number (the replacement
        authorization reversed), reversed_amount (USD, 2 decimal places) and status ("paid" when the settlement
        and its reversal were recorded).
    """
    settle = ctx.make_id("CIL-", homeplan_contract_id, homeplan_service_request_id, covered_item,
                         replaced_authorization_number, replaced_amount, cash_amount)
    rev = ctx.make_id("REV-", homeplan_contract_id, homeplan_service_request_id, replaced_authorization_number,
                      replaced_amount)
    ctx.create("homeplan_claim_events", settle, homeplan_claim_event_id=settle,
               homeplan_contract_id=homeplan_contract_id, event_type="homeplan_cash_in_lieu_payment",
               homeplan_service_request_id=homeplan_service_request_id, event_date=ctx.now()[:10],
               covered_item=covered_item, authorization_number=settle, amount=round(float(cash_amount), 2),
               settlement_basis="customer_elected", reversed_authorization_number=replaced_authorization_number)
    ctx.create("homeplan_claim_events", rev, homeplan_claim_event_id=rev,
               homeplan_contract_id=homeplan_contract_id, event_type="homeplan_authorization_reversal",
               homeplan_service_request_id=homeplan_service_request_id, event_date=ctx.now()[:10],
               covered_item=covered_item, reversed_authorization_number=replaced_authorization_number,
               reversal_reason="cash_in_lieu_elected", amount=round(float(replaced_amount), 2))
    return str({"settlement_number": settle, "homeplan_service_request_id": homeplan_service_request_id,
                "cash_amount": round(float(cash_amount), 2), "settlement_basis": "customer_elected",
                "reversed_authorization_number": replaced_authorization_number,
                "reversed_amount": round(float(replaced_amount), 2), "status": "paid"})


@tool(owner="agent", rw="write")
def book_supplemental_allowance_cce1a240(ctx: ToolContext, homeplan_contract_id: str,
                                         homeplan_service_request_id: str, allowance_type: str,
                                         invoice_amount: float, amount: float) -> str:
    """Record a supplemental allowance Bridgewell pays on a homeowner service request that carries a repair or
    replacement authorization. One call adds one allowance of one type to the request's claim-handling history;
    the amount recorded counts toward the contract's aggregate benefit limit from today and never toward an item
    cap. On success the request shows the allowance as paid.

    Args:
        homeplan_contract_id: Id class — the homeowner service contract number the request is placed under, as
            returned by the homeowner contract lookup.
        homeplan_service_request_id: Id class — the service request number the allowance is paid on, as returned
            by the claim-history lookup.
        allowance_type: Enum class — which allowance is paid, one of: code_violation (correcting a code violation
            that must be fixed to complete the covered work), permit (permits the covered work requires),
            haul_away (removing and disposing of equipment Bridgewell replaced), refrigerant (refrigerant recovery
            and recharge on covered cooling work), crane_access (crane or lift access to rooftop equipment),
            slab_access (opening and closing a concrete slab to reach a covered leak).
        invoice_amount: Fixed-format class — the documented or contracted charge the allowance pays toward, in
            USD, rounded to 2 decimal places, positive.
        amount: Fixed-format class — the allowance payment recorded, in USD, rounded to 2 decimal places,
            positive.

    Returns:
        A dict confirming the payment: allowance_reference (the allowance record reference, text),
        homeplan_service_request_id (the request paid on), allowance_type (the type recorded), invoice_amount
        (USD, 2 decimal places), amount (USD, 2 decimal places) and status ("paid" when recorded).
    """
    ref = ctx.make_id("SPA-", homeplan_contract_id, homeplan_service_request_id, allowance_type, invoice_amount,
                      amount)
    ctx.create("homeplan_claim_events", ref, homeplan_claim_event_id=ref,
               homeplan_contract_id=homeplan_contract_id, event_type="homeplan_supplemental_allowance",
               homeplan_service_request_id=homeplan_service_request_id, event_date=ctx.now()[:10],
               allowance_type=allowance_type, invoice_amount=round(float(invoice_amount), 2),
               amount=round(float(amount), 2))
    return str({"allowance_reference": ref, "homeplan_service_request_id": homeplan_service_request_id,
                "allowance_type": allowance_type, "invoice_amount": round(float(invoice_amount), 2),
                "amount": round(float(amount), 2), "status": "paid"})


@tool(owner="agent", rw="write")
def issue_company_cash_offer_eabc2067(ctx: ToolContext, homeplan_contract_id: str,
                                      homeplan_service_request_id: str, covered_item: str,
                                      replacement_cost: float, amount: float, offer_expiration_date: str) -> str:
    """Record a cash-in-lieu offer that Bridgewell itself elects to make because the replacement it authorized
    cannot be installed through its contractor network. One call adds one company-elected cash offer to the
    service request's claim-handling history; recording the offer pays nothing and uses no benefit. On success
    the request shows the open offer, its amount and the last day it may be accepted.

    Args:
        homeplan_contract_id: Id class — the homeowner service contract number the request is placed under, as
            returned by the homeowner contract lookup.
        homeplan_service_request_id: Id class — the service request number of the replacement that cannot be
            installed, as returned by the claim-history lookup.
        covered_item: Enum class — the item the offer concerns, one of: heating_system (the furnace, boiler or
            heat pump heating side), cooling_system (the central air conditioning), ductwork (heating and
            cooling ducts), plumbing_leak (an interior water supply or drain leak), plumbing_stoppage (an
            interior drain stoppage), water_heater (the water heater), electrical (the interior electrical
            system), ceiling_fan (a ceiling fan), garbage_disposal (the garbage disposal), whirlpool_tub (the
            whirlpool bathtub motor and pump), refrigerator (the kitchen refrigerator), oven_range_cooktop (the
            oven, range or cooktop), dishwasher (the dishwasher), built_in_microwave (the built-in microwave),
            clothes_washer (the clothes washer), clothes_dryer (the clothes dryer), garage_door_opener (the
            garage door opener).
        replacement_cost: Fixed-format class — the like-unit cost to record on the offer as its replacement_cost,
            in USD, rounded to 2 decimal places, positive.
        amount: Fixed-format class — the cash offered, in USD, rounded to 2 decimal places, positive.
        offer_expiration_date: Fixed-format class — the last calendar day on which the offer may be accepted, as
            a date in YYYY-MM-DD format.

    Returns:
        A dict confirming the offer: offer_reference (the offer record reference, text),
        homeplan_service_request_id (the request it was made on), settlement_basis (always company_elected),
        amount (USD, 2 decimal places), offer_expiration_date (YYYY-MM-DD) and status ("offered" when recorded).
    """
    ref = ctx.make_id("CO-", homeplan_contract_id, homeplan_service_request_id, covered_item, replacement_cost,
                      amount, offer_expiration_date)
    ctx.create("homeplan_claim_events", ref, homeplan_claim_event_id=ref,
               homeplan_contract_id=homeplan_contract_id, event_type="homeplan_cash_in_lieu_offer",
               homeplan_service_request_id=homeplan_service_request_id, event_date=ctx.now()[:10],
               covered_item=covered_item, replacement_cost=round(float(replacement_cost), 2),
               amount=round(float(amount), 2), settlement_basis="company_elected",
               offer_expiration_date=str(offer_expiration_date))
    return str({"offer_reference": ref, "homeplan_service_request_id": homeplan_service_request_id,
                "settlement_basis": "company_elected", "amount": round(float(amount), 2),
                "offer_expiration_date": str(offer_expiration_date), "status": "offered"})


@tool(owner="user", rw="write")
def accept_company_cash_offer_2503240a(ctx: ToolContext, homeplan_contract_id: str,
                                       homeplan_service_request_id: str, covered_item: str,
                                       standing_authorization_number: str, standing_amount: float,
                                       payment_amount: float) -> str:
    """The homeowner accepts the cash Bridgewell has offered in place of a replacement it could not install.
    One call records the customer's acceptance as a company-elected cash payment on the service request,
    issues a cash settlement number, and, in the same action, reverses in full the replacement authorization
    that was standing on the request. On success the request shows the cash payment and no standing
    replacement; the payment is what Bridgewell pays the homeowner.

    Args:
        homeplan_contract_id: Id class — the homeowner service contract number the request is placed under, as
            the agent reads it from the contract record.
        homeplan_service_request_id: Id class — the service request number the accepted offer was made on, as
            the agent reads it from the claim history.
        covered_item: Enum class — the item settled in cash, one of: heating_system (the furnace, boiler or heat
            pump heating side), cooling_system (the central air conditioning), ductwork (heating and cooling
            ducts), plumbing_leak (an interior water supply or drain leak), plumbing_stoppage (an interior drain
            stoppage), water_heater (the water heater), electrical (the interior electrical system), ceiling_fan
            (a ceiling fan), garbage_disposal (the garbage disposal), whirlpool_tub (the whirlpool bathtub motor
            and pump), refrigerator (the kitchen refrigerator), oven_range_cooktop (the oven, range or cooktop),
            dishwasher (the dishwasher), built_in_microwave (the built-in microwave), clothes_washer (the clothes
            washer), clothes_dryer (the clothes dryer), garage_door_opener (the garage door opener).
        standing_authorization_number: Id class — the number of the replacement authorization standing on the
            request, as shown on that authorization in the claim history.
        standing_amount: Fixed-format class — the amount recorded on that standing replacement authorization,
            in USD, rounded to 2 decimal places, positive.
        payment_amount: Fixed-format class — the cash paid to the homeowner on acceptance, in USD, rounded to 2
            decimal places, positive.

    Returns:
        A dict confirming the acceptance: settlement_number (the cash settlement number issued, text),
        homeplan_service_request_id (the request settled), payment_amount (USD, 2 decimal places),
        settlement_basis (always company_elected), reversed_authorization_number (the replacement
        authorization reversed), reversed_amount (USD, 2 decimal places) and status ("paid" when the payment
        and its reversal were recorded).
    """
    settle = ctx.make_id("CIL-", homeplan_contract_id, homeplan_service_request_id, covered_item,
                         standing_authorization_number, standing_amount, payment_amount)
    rev = ctx.make_id("REV-", homeplan_contract_id, homeplan_service_request_id, standing_authorization_number,
                      standing_amount)
    ctx.create("homeplan_claim_events", settle, homeplan_claim_event_id=settle,
               homeplan_contract_id=homeplan_contract_id, event_type="homeplan_cash_in_lieu_payment",
               homeplan_service_request_id=homeplan_service_request_id, event_date=ctx.now()[:10],
               covered_item=covered_item, authorization_number=settle, amount=round(float(payment_amount), 2),
               settlement_basis="company_elected")
    ctx.create("homeplan_claim_events", rev, homeplan_claim_event_id=rev,
               homeplan_contract_id=homeplan_contract_id, event_type="homeplan_authorization_reversal",
               homeplan_service_request_id=homeplan_service_request_id, event_date=ctx.now()[:10],
               covered_item=covered_item, reversed_authorization_number=standing_authorization_number,
               reversal_reason="cash_in_lieu_elected", amount=round(float(standing_amount), 2))
    return str({"settlement_number": settle, "homeplan_service_request_id": homeplan_service_request_id,
                "payment_amount": round(float(payment_amount), 2), "settlement_basis": "company_elected",
                "reversed_authorization_number": standing_authorization_number,
                "reversed_amount": round(float(standing_amount), 2), "status": "paid"})

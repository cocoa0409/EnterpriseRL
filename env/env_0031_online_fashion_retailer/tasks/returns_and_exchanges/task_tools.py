"""Hidden task tools of the returns_and_exchanges difficulty (Marlowe & Finch Returns & Exchanges).

Each tool performs one atomic write on a return authorization and is reached only through the
unlock/call meta-tools; its name is published by the extended charter's target_tool. No tool judges
eligibility, prerequisites or amounts: the agent works every figure out from the policy and the
records and passes it in.
"""

from erlbench import ToolContext, tool


@tool(owner="agent", rw="write")
def credit_inspected_line_1e38d691(ctx: ToolContext, return_id: str, booked_line_id: str,
                                   merchandise_amount_usd: float, tax_amount_usd: float) -> str:
    """Book the credit entry for the units of one returned order line that inspection accepted.

    The returns desk records, on the return's money ledger, the value Marlowe & Finch now owes the
    customer for the accepted units of one booked order line: a merchandise part and a sales-tax part,
    with no shipping part. The entry is dated today and its total is the two parts added together; it
    raises what is owed on the return by that total. After the call the entry appears among the
    return's settlement entries as a credit for that booking line.

    Args:
        return_id: Id class — the RMA number of the return the accepted units came back on, as shown by the return lookup.
        booked_line_id: Id class — the reference number of the order's booking line whose accepted units are credited, as shown on the return's inspection entries and in the order lines lookup.
        merchandise_amount_usd: Fixed-format class — the merchandise value credited for the accepted units, in USD, a positive amount with 2 decimal places, already rounded half up to the cent.
        tax_amount_usd: Fixed-format class — the sales tax credited with those units, in USD, a non-negative amount with 2 decimal places, already rounded half up to the cent; 0.00 when no tax is credited.

    Returns:
        A confirmation sentence naming the new credit entry reference (a "rs_" reference), the RMA
        number, the booking line, the merchandise and tax parts and the total credited in USD with 2
        decimal places; the presence of the entry reference means the credit was booked.
    """
    rows = ctx.find("return_cases", return_id=return_id)
    if not rows:
        return f"Error: no return {return_id}."
    rec = rows[0]
    rid = ctx.make_id("rs_", return_id, booked_line_id, merchandise_amount_usd, tax_amount_usd)
    merch = round(float(merchandise_amount_usd), 2)
    tax = round(float(tax_amount_usd), 2)
    ctx.create("return_settlements", rid, settlement_id=rid, return_id=return_id,
               customer_id=rec.get("customer_id"), event_type="returns_refund_credited",
               event_date=ctx.now()[:10], order_id=rec.get("order_id"), booked_line_id=booked_line_id,
               merchandise_amount_usd=merch, tax_amount_usd=tax, shipping_amount_usd=0.0,
               amount_usd=round(merch + tax, 2), fee_type="not_applicable", refund_stage="not_applicable",
               tender_type="not_applicable", instrument_id=None, recovered_from="not_applicable",
               exchange_order_id=None, exchange_sku="", hold_action="not_applicable")
    return (f"Credit entry {rid} booked on return {return_id} for line {booked_line_id}: "
            f"merchandise {merch:.2f} USD + tax {tax:.2f} USD = {merch + tax:.2f} USD credited.")


@tool(owner="agent", rw="write")
def assess_restocking_fee_49fe3caa(ctx: ToolContext, return_id: str, booked_line_id: str,
                                   fee_amount_usd: float) -> str:
    """Withhold the restocking fee for the grade B units of one returned order line.

    The returns desk enters, on the return's money ledger, one restocking fee for one booked order
    line, dated today; the fee lowers what is owed to the customer on the return by its amount. After
    the call the fee appears among the return's settlement entries as a restocking fee on that line.

    Args:
        return_id: Id class — the RMA number of the return carrying the grade B units, as shown by the return lookup.
        booked_line_id: Id class — the reference number of the order's booking line the fee is charged on, as shown on the return's inspection entries.
        fee_amount_usd: Fixed-format class — the restocking fee withheld for the line, in USD, a non-negative amount with 2 decimal places, already rounded half up to the cent (0.00 when the fee is fully waived); it is recorded as a deduction.

    Returns:
        A confirmation sentence naming the new fee entry reference (a "rs_" reference), the RMA number,
        the booking line and the fee withheld in USD with 2 decimal places; the presence of the entry
        reference means the fee was booked.
    """
    rows = ctx.find("return_cases", return_id=return_id)
    if not rows:
        return f"Error: no return {return_id}."
    rec = rows[0]
    rid = ctx.make_id("rs_", return_id, booked_line_id, "restocking_fee", fee_amount_usd)
    fee = round(float(fee_amount_usd), 2)
    ctx.create("return_settlements", rid, settlement_id=rid, return_id=return_id,
               customer_id=rec.get("customer_id"), event_type="returns_fee_assessed",
               event_date=ctx.now()[:10], order_id=rec.get("order_id"), booked_line_id=booked_line_id,
               merchandise_amount_usd=0.0, tax_amount_usd=0.0, shipping_amount_usd=0.0,
               amount_usd=-fee, fee_type="restocking_fee", refund_stage="not_applicable",
               tender_type="not_applicable", instrument_id=None, recovered_from="not_applicable",
               exchange_order_id=None, exchange_sku="", hold_action="not_applicable")
    return f"Restocking fee entry {rid} booked on return {return_id}, line {booked_line_id}: {fee:.2f} USD withheld."


@tool(owner="user", rw="write")
def authorize_spent_credit_charge_4aac9d1c(ctx: ToolContext, return_id: str, charge_amount_usd: float) -> str:
    """Authorize, as the cardholder, a charge on the original card for instant store credit already spent.

    The customer personally authorizes Marlowe & Finch to charge the card used on the original order
    for the part of a Store Credit Return's instant store credit that inspection and fees left
    unearned and that has already been spent. One recovery entry from the original card is recorded on
    the return, dated today; it lowers what the customer owes back on the return by the amount
    charged. After the call the charge appears among the return's settlement entries as a recovery
    from the original card.

    Args:
        return_id: Id class — the RMA number of the Store Credit Return the instant credit was issued on, as the agent reads it out from the return lookup.
        charge_amount_usd: Fixed-format class — the amount the cardholder authorizes on the original card, in USD, a positive amount with 2 decimal places, already rounded half up to the cent, exactly as the agent states it.

    Returns:
        A confirmation sentence naming the recovery entry reference (a "rs_" reference), the RMA number
        and the amount charged to the original card in USD with 2 decimal places; the presence of the
        entry reference means the charge was authorized and recorded.
    """
    rows = ctx.find("return_cases", return_id=return_id)
    if not rows:
        return f"Error: no return {return_id}."
    rec = rows[0]
    rid = ctx.make_id("rs_", return_id, "original_card", charge_amount_usd)
    amt = round(float(charge_amount_usd), 2)
    ctx.create("return_settlements", rid, settlement_id=rid, return_id=return_id,
               customer_id=rec.get("customer_id"), event_type="returns_instant_credit_reversed",
               event_date=ctx.now()[:10], order_id=rec.get("order_id"), booked_line_id=None,
               merchandise_amount_usd=0.0, tax_amount_usd=0.0, shipping_amount_usd=0.0,
               amount_usd=amt, fee_type="not_applicable", refund_stage="not_applicable",
               tender_type="not_applicable", instrument_id=None, recovered_from="original_card",
               exchange_order_id=None, exchange_sku="", hold_action="not_applicable")
    return f"Card charge {rid} authorized on return {return_id}: {amt:.2f} USD charged to the original card."


@tool(owner="agent", rw="write")
def extend_return_deadline_be33eaa2(ctx: ToolContext, return_id: str, extension_days: int) -> str:
    """Move the return-by date of an open return authorization later by a number of calendar days.

    The returns desk extends one return authorization: its return-by date becomes the current
    return-by date plus the given number of calendar days, and its count of deadline extensions used
    goes up by one. After the call the return lookup shows the new return-by date.

    Args:
        return_id: Id class — the RMA number of the authorization being extended, as shown by the return lookup.
        extension_days: Fixed-format class — the number of calendar days added to the current return-by date, a positive integer.

    Returns:
        A confirmation sentence naming the RMA number, the previous and the new return-by date
        (YYYY-MM-DD) and the number of extensions now used; the new date in the sentence means the
        extension was recorded.
    """
    rows = ctx.find("return_cases", return_id=return_id)
    if not rows:
        return f"Error: no return {return_id}."
    rec = rows[0]
    old = str(rec.get("return_by_date"))
    y, m, d = (int(x) for x in old[:10].split("-"))
    d += int(extension_days)
    month_days = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
    while True:
        dim = 29 if (m == 2 and y % 4 == 0 and (y % 100 != 0 or y % 400 == 0)) else month_days[m - 1]
        if d > dim:
            d -= dim
            m += 1
            if m > 12:
                m, y = 1, y + 1
        elif d < 1:
            m -= 1
            if m < 1:
                m, y = 12, y - 1
            d += 29 if (m == 2 and y % 4 == 0 and (y % 100 != 0 or y % 400 == 0)) else month_days[m - 1]
        else:
            break
    new = f"{y:04d}-{m:02d}-{d:02d}"
    used = int(rec.get("deadline_extensions_used") or 0) + 1
    ctx.update("return_cases", return_id, return_by_date=new, deadline_extensions_used=used)
    return f"Return {return_id} extended: return-by date {old} -> {new}; extensions used {used}."


@tool(owner="agent", rw="write")
def assess_box_fee_f48699d7(ctx: ToolContext, return_id: str, booked_line_id: str, fee_amount_usd: float) -> str:
    """Withhold the shoebox fee for the footwear units of one returned order line.

    The returns desk enters, on the return's money ledger, one shoebox fee for one booked footwear
    line whose units came back without their original box or in a damaged box or a box used as the
    shipping carton, dated today; the fee lowers what is owed to the customer on the return by its
    amount. After the call the fee appears among the return's settlement entries as a missing box fee.

    Args:
        return_id: Id class — the RMA number of the return carrying the footwear units, as shown by the return lookup.
        booked_line_id: Id class — the reference number of the order's footwear booking line the fee is charged on, as shown on the return's inspection entries.
        fee_amount_usd: Fixed-format class — the shoebox fee withheld for the line, in USD, a non-negative amount with 2 decimal places, already rounded half up to the cent (0.00 when the fee is fully waived); it is recorded as a deduction.

    Returns:
        A confirmation sentence naming the new fee entry reference (a "rs_" reference), the RMA number,
        the booking line and the fee withheld in USD with 2 decimal places; the presence of the entry
        reference means the fee was booked.
    """
    rows = ctx.find("return_cases", return_id=return_id)
    if not rows:
        return f"Error: no return {return_id}."
    rec = rows[0]
    rid = ctx.make_id("rs_", return_id, booked_line_id, "missing_box_fee", fee_amount_usd)
    fee = round(float(fee_amount_usd), 2)
    ctx.create("return_settlements", rid, settlement_id=rid, return_id=return_id,
               customer_id=rec.get("customer_id"), event_type="returns_fee_assessed",
               event_date=ctx.now()[:10], order_id=rec.get("order_id"), booked_line_id=booked_line_id,
               merchandise_amount_usd=0.0, tax_amount_usd=0.0, shipping_amount_usd=0.0,
               amount_usd=-fee, fee_type="missing_box_fee", refund_stage="not_applicable",
               tender_type="not_applicable", instrument_id=None, recovered_from="not_applicable",
               exchange_order_id=None, exchange_sku="", hold_action="not_applicable")
    return f"Shoebox fee entry {rid} booked on return {return_id}, line {booked_line_id}: {fee:.2f} USD withheld."


@tool(owner="agent", rw="write")
def withhold_return_shipping_fee_e68e1eec(ctx: ToolContext, return_id: str, fee_amount_usd: float) -> str:
    """Withhold the return shipping (method) fee once on a return.

    The returns desk enters, on the return's money ledger, the single fee charged for the return
    method the parcel travelled by, dated today and not tied to any one order line; the fee lowers
    what is owed to the customer on the return by its amount. After the call the fee appears among the
    return's settlement entries as the method fee.

    Args:
        return_id: Id class — the RMA number of the return whose shipping fee is withheld, as shown by the return lookup.
        fee_amount_usd: Fixed-format class — the return shipping fee withheld, in USD, a non-negative amount with 2 decimal places, already rounded half up to the cent (0.00 when the fee is fully waived); it is recorded as a deduction.

    Returns:
        A confirmation sentence naming the new fee entry reference (a "rs_" reference), the RMA number
        and the fee withheld in USD with 2 decimal places; the presence of the entry reference means
        the fee was booked.
    """
    rows = ctx.find("return_cases", return_id=return_id)
    if not rows:
        return f"Error: no return {return_id}."
    rec = rows[0]
    rid = ctx.make_id("rs_", return_id, "method_fee", fee_amount_usd)
    fee = round(float(fee_amount_usd), 2)
    ctx.create("return_settlements", rid, settlement_id=rid, return_id=return_id,
               customer_id=rec.get("customer_id"), event_type="returns_fee_assessed",
               event_date=ctx.now()[:10], order_id=rec.get("order_id"), booked_line_id=None,
               merchandise_amount_usd=0.0, tax_amount_usd=0.0, shipping_amount_usd=0.0,
               amount_usd=-fee, fee_type="method_fee", refund_stage="not_applicable",
               tender_type="not_applicable", instrument_id=None, recovered_from="not_applicable",
               exchange_order_id=None, exchange_sku="", hold_action="not_applicable")
    return f"Method fee entry {rid} booked on return {return_id}: {fee:.2f} USD withheld."


@tool(owner="agent", rw="write")
def pay_final_card_refund_b5173030(ctx: ToolContext, return_id: str, refund_stage: str, tender_type: str,
                                   instrument_id: str, refund_amount_usd: float) -> str:
    """Pay the final-settlement refund of a return to the card or wallet the order was paid with.

    The returns desk pays one refund on a return to the card or digital wallet captured on the
    original order and records it on the return's money ledger, dated today; the payment lowers what
    is still owed on the return by its amount. This action pays only a final-settlement refund to the
    card or wallet: refunds owed to a stored-value instrument are booked through the instrument's own
    ledger and are not paid here. After the call the refund appears among the return's settlement
    entries.

    Args:
        return_id: Id class — the RMA number of the return being refunded, as shown by the return lookup.
        refund_stage: Enum class — when the refund is paid: not_applicable is never a refund stage and is refused; instant_credit_at_scan is the store credit issued at the parcel's first carrier scan, which this action does not pay; final_settlement is the refund paid when the inspected return is settled, the only stage this action pays.
        tender_type: Enum class — the payment method refunded: card_or_wallet is the card or digital wallet captured on the order and the only tender this action pays; not_applicable is never a tender and is refused; gift_card is a Marlowe & Finch gift card used on the order, refunded through the card's own ledger and not here; return_store_credit is existing Return Store Credit used on the order, not paid here; bonus_gift_card is a holiday Bonus Gift Card used on the order, not paid here; goodwill_credit is a Goodwill Credit used on the order, not paid here; rewards_note is a Marlowe Rewards Note used on the order, not paid here; return_store_credit_new is a newly issued Return Store Credit, not paid here.
        instrument_id: Id class — the reference number of a stored-value instrument refunded; a card or wallet has no instrument reference, so pass "" for a card_or_wallet refund.
        refund_amount_usd: Fixed-format class — the amount paid back to the card or wallet, in USD, a positive amount with 2 decimal places, already rounded half up to the cent; it is recorded as a payment out.

    Returns:
        A confirmation sentence naming the refund entry reference (a "rs_" reference), the RMA number,
        the stage, the tender and the amount refunded in USD with 2 decimal places; the presence of the
        entry reference means the refund was paid. Any other stage, tender or an instrument reference
        returns an error sentence and records nothing.
    """
    if refund_stage != "final_settlement" or tender_type != "card_or_wallet" or instrument_id:
        return ("Error: this action pays only a final_settlement refund to card_or_wallet with no instrument "
                "reference.")
    rows = ctx.find("return_cases", return_id=return_id)
    if not rows:
        return f"Error: no return {return_id}."
    rec = rows[0]
    rid = ctx.make_id("rs_", return_id, refund_stage, tender_type, instrument_id, refund_amount_usd)
    amt = round(float(refund_amount_usd), 2)
    ctx.create("return_settlements", rid, settlement_id=rid, return_id=return_id,
               customer_id=rec.get("customer_id"), event_type="returns_refund_issued",
               event_date=ctx.now()[:10], order_id=rec.get("order_id"), booked_line_id=None,
               merchandise_amount_usd=0.0, tax_amount_usd=0.0, shipping_amount_usd=0.0,
               amount_usd=-amt, fee_type="not_applicable", refund_stage=refund_stage,
               tender_type=tender_type, instrument_id=instrument_id or None, recovered_from="not_applicable",
               exchange_order_id=None, exchange_sku="", hold_action="not_applicable")
    return f"Refund {rid} paid on return {return_id} ({refund_stage}, {tender_type}): {amt:.2f} USD."


@tool(owner="user", rw="write")
def place_exchange_hold_2c1506d4(ctx: ToolContext, return_id: str, hold_amount_usd: float) -> str:
    """Place, as the cardholder, the card hold that releases an Instant Exchange replacement.

    The customer personally consents to an authorization hold on the card used on the original order
    for an Instant Exchange return, in the amount the agent states. One hold entry is recorded on the
    return's exchange-hold ledger, dated today; the hold stays open on the card until the returned
    units are received or the hold is charged. After the call the hold appears among the return's
    settlement entries as placed.

    Args:
        return_id: Id class — the RMA number of the Instant Exchange return, as shown on the exchange confirmation and by the return lookup.
        hold_amount_usd: Fixed-format class — the hold amount the cardholder consents to, in USD, a positive amount with 2 decimal places, already rounded half up to the cent, exactly as the agent states it.

    Returns:
        A confirmation sentence naming the hold entry reference (a "rs_" reference), the RMA number and
        the amount held on the card in USD with 2 decimal places; the presence of the entry reference
        means the hold was placed.
    """
    rows = ctx.find("return_cases", return_id=return_id)
    if not rows:
        return f"Error: no return {return_id}."
    rec = rows[0]
    rid = ctx.make_id("rs_", return_id, "placed", hold_amount_usd)
    amt = round(float(hold_amount_usd), 2)
    ctx.create("return_settlements", rid, settlement_id=rid, return_id=return_id,
               customer_id=rec.get("customer_id"), event_type="returns_hold_placed",
               event_date=ctx.now()[:10], order_id=rec.get("order_id"), booked_line_id=None,
               merchandise_amount_usd=0.0, tax_amount_usd=0.0, shipping_amount_usd=0.0,
               amount_usd=amt, fee_type="not_applicable", refund_stage="not_applicable",
               tender_type="not_applicable", instrument_id=None, recovered_from="not_applicable",
               exchange_order_id=None, exchange_sku=rec.get("exchange_sku") or "", hold_action="placed")
    return f"Card hold {rid} placed on Instant Exchange {return_id}: {amt:.2f} USD held."

"""Hidden task tools for d2_contract_pricing_claims_and_rebates (Contract Pricing Agreement).

Each tool performs one atomic write on the pricing agreement's own records and nothing else; every
figure it records is worked out by the agent from the knowledge base and the records and passed in.
"""

from erlbench import ToolContext, tool


@tool(owner="agent", rw="write")
def book_rebate_return_clawback_ccd0c1e2(ctx: ToolContext, pricing_agreement_id: str, rebate_period: str,
                                         rma_number: str, returned_merchandise_value: float,
                                         rebate_rate_pct: float, amount: float) -> str:
    """Book a volume rebate clawback for one customer return on a Contract Pricing Agreement.

    The agent records, on the agreement's rebate ledger, one reversal line for the return material
    authorization named, against the rebate period named: the line carries the merchandise value
    returned (recorded as negative qualifying spend), the rebate rate applied and the rebate amount
    reversed, is dated on the day of the call, and the agreement's unpaid rebate balance is reduced
    by the amount reversed. The customer sees the clawback on the agreement's rebate statement.

    Args:
        pricing_agreement_id: Id class — the reference number of the customer's Contract Pricing Agreement, read from the pricing agreement lookup.
        rebate_period: Fixed-format class — the calendar-quarter rebate period the clawback is booked against, written YYYY-Qn (four-digit year, a hyphen, the letter Q and the quarter digit 1 to 4).
        rma_number: Verbatim class — the return material authorization number exactly as the customer's return records show it, copied character for character (verbatim).
        returned_merchandise_value: Fixed-format class — the merchandise value returned that the clawback is worked out on, passed as a positive figure in USD, 2 decimal places, rounded half up to the cent; it is recorded on the ledger line with its sign reversed, in USD, 2 decimal places, signed.
        rebate_rate_pct: Fixed-format class — the rebate rate applied to that value, in percent, 2 decimal places (percentage points, not a fraction).
        amount: Fixed-format class — the rebate amount reversed, in USD, 2 decimal places, positive, rounded half up to the cent.

    Returns:
        A dictionary rendered as text with: status ("booked" when the reversal line was written),
        rebate_line_id (reference number of the new rebate ledger line), rebate_period (YYYY-Qn),
        source_reference (the return material authorization number recorded), amount (USD, 2 decimal
        places, the rebate reversed) and rebate_balance (USD, 2 decimal places, the agreement's unpaid
        rebate balance once the reversal is booked).
    """
    agreement = (ctx.find("pricing_agreements", pricing_agreement_id=pricing_agreement_id) or [{}])[0]
    period_label = str(rebate_period).strip()
    amt = round(float(amount), 2)
    value = round(float(returned_merchandise_value), 2)
    rid = ctx.make_id("prb_", pricing_agreement_id, rebate_period, rma_number, value, rebate_rate_pct, amt)
    ctx.create("pricing_rebates", rid, rebate_line_id=rid, pricing_agreement_id=pricing_agreement_id,
               customer_id=agreement.get("customer_id"), event_type="pricing_rebate_reversed",
               rebate_period=period_label, qualifying_spend=round(-value, 2),
               rebate_rate_pct=round(float(rebate_rate_pct), 2), amount=amt, payout_method="none",
               event_date=ctx.now()[:10], source_reference=rma_number)
    balance = round(float(agreement.get("rebate_balance") or 0) - amt, 2)
    ctx.update("pricing_agreements", pricing_agreement_id, rebate_balance=balance)
    return str({"status": "booked", "rebate_line_id": rid, "rebate_period": rebate_period,
                "source_reference": rma_number, "amount": amt, "rebate_balance": balance})


@tool(owner="agent", rw="write")
def book_termination_rebate_forfeiture_47cc59ce(ctx: ToolContext, pricing_agreement_id: str, rebate_period: str,
                                                amount: float) -> str:
    """Book the volume rebate forfeiture that an early termination of a Contract Pricing Agreement carries.

    The agent records, on the agreement's rebate ledger, one forfeiture reversal line against the
    rebate period named: the line carries the rebate amount forfeited, zero qualifying spend and a
    zero rate, references the agreement number, is dated on the day of the call, and the agreement's
    unpaid rebate balance is reduced by the amount forfeited. The customer sees the forfeiture on the
    agreement's rebate statement.

    Args:
        pricing_agreement_id: Id class — the reference number of the customer's Contract Pricing Agreement, read from the pricing agreement lookup.
        rebate_period: Fixed-format class — the calendar-quarter rebate period the forfeiture is booked against, written YYYY-Qn (four-digit year, a hyphen, the letter Q and the quarter digit 1 to 4).
        amount: Fixed-format class — the rebate amount forfeited, in USD, 2 decimal places, positive, rounded half up to the cent.

    Returns:
        A dictionary rendered as text with: status ("booked" when the forfeiture line was written),
        rebate_line_id (reference number of the new rebate ledger line), rebate_period (YYYY-Qn),
        source_reference (the agreement number recorded on the line), amount (USD, 2 decimal places,
        the rebate forfeited) and rebate_balance (USD, 2 decimal places, the agreement's unpaid rebate
        balance once the forfeiture is booked).
    """
    agreement = (ctx.find("pricing_agreements", pricing_agreement_id=pricing_agreement_id) or [{}])[0]
    period_label = str(rebate_period).strip()
    amt = round(float(amount), 2)
    rid = ctx.make_id("prb_", pricing_agreement_id, rebate_period, "forfeiture", amt)
    reference = agreement.get("agreement_number")
    ctx.create("pricing_rebates", rid, rebate_line_id=rid, pricing_agreement_id=pricing_agreement_id,
               customer_id=agreement.get("customer_id"), event_type="pricing_rebate_reversed",
               rebate_period=period_label, qualifying_spend=0.0, rebate_rate_pct=0.0, amount=amt,
               payout_method="none", event_date=ctx.now()[:10], source_reference=reference)
    balance = round(float(agreement.get("rebate_balance") or 0) - amt, 2)
    ctx.update("pricing_agreements", pricing_agreement_id, rebate_balance=balance)
    return str({"status": "booked", "rebate_line_id": rid, "rebate_period": rebate_period,
                "source_reference": reference, "amount": amt, "rebate_balance": balance})


@tool(owner="user", rw="write")
def request_final_rebate_check_d4aa8dfe(ctx: ToolContext, pricing_agreement_id: str, rebate_period: str,
                                        amount: float) -> str:
    """The customer requests payment of the unpaid volume rebate on its Contract Pricing Agreement by check.

    The customer's authorized contact instructs Corbett to pay the stated amount of the agreement's
    unpaid rebate by check. One payout line is recorded on the agreement's rebate ledger against the
    rebate period named, with check as the payout method, a newly issued check payout reference and
    the day of the call as the payout date, and the agreement's unpaid rebate balance is reduced by the
    amount paid. The customer receives the check payout reference for its records.

    Args:
        pricing_agreement_id: Id class — the reference number of the customer's Contract Pricing Agreement, as the agent reads it from the agreement lookup and hands it to the customer.
        rebate_period: Fixed-format class — the calendar-quarter rebate period the payout line is recorded against, written YYYY-Qn (four-digit year, a hyphen, the letter Q and the quarter digit 1 to 4), as the agent hands it to the customer.
        amount: Fixed-format class — the amount the check pays, in USD, 2 decimal places, positive, rounded half up to the cent, as the agent hands it to the customer.

    Returns:
        A dictionary rendered as text with: status ("check requested" when the payout line was
        written), rebate_line_id (reference number of the new rebate ledger line), payout_reference
        (the check payout reference issued), payout_method (always check), amount (USD, 2 decimal
        places, the amount the check pays) and rebate_balance (USD, 2 decimal places, the agreement's
        unpaid rebate balance once the payout is recorded).
    """
    agreement = (ctx.find("pricing_agreements", pricing_agreement_id=pricing_agreement_id) or [{}])[0]
    period_label = str(rebate_period).strip()
    amt = round(float(amount), 2)
    rid = ctx.make_id("prb_", pricing_agreement_id, rebate_period, "check", amt)
    payout_reference = "RBC-2" + str(int(rid[-10:], 16) % 100000).zfill(5)
    ctx.create("pricing_rebates", rid, rebate_line_id=rid, pricing_agreement_id=pricing_agreement_id,
               customer_id=agreement.get("customer_id"), event_type="pricing_rebate_paid",
               rebate_period=period_label, qualifying_spend=0.0, rebate_rate_pct=0.0, amount=amt,
               payout_method="check", event_date=ctx.now()[:10], source_reference=payout_reference)
    balance = round(float(agreement.get("rebate_balance") or 0) - amt, 2)
    ctx.update("pricing_agreements", pricing_agreement_id, rebate_balance=balance)
    return str({"status": "check requested", "rebate_line_id": rid, "payout_reference": payout_reference,
                "payout_method": "check", "amount": amt, "rebate_balance": balance})


@tool(owner="agent", rw="write")
def decide_pending_price_claim_4f6327a3(ctx: ToolContext, pricing_agreement_id: str, claim_reference: str, outcome: str,
                                        quantity: int, billed_unit_price: float, contract_unit_price: float) -> str:
    """Record the support desk's decision on a contract price claim that is still pending on a Contract Pricing Agreement.

    The agent records one decision line for the claim named, on the agreement's price claim records:
    it carries the claim's invoice number and item number as filed, the quantity, the billed unit price
    and the unit price the agreement sets as decided, a credited amount of zero, the decision and the
    day of the call. No credit is issued by this tool. The customer sees the claim's status change from
    pending to the decision recorded.

    Args:
        pricing_agreement_id: Id class — the reference number of the customer's Contract Pricing Agreement, read from the pricing agreement lookup.
        claim_reference: Verbatim class — the price claim reference exactly as the agreement's price claim records show it on the pending filing, copied character for character (verbatim).
        outcome: Enum class — the decision recorded; exactly one of: denied — the billed unit price is at or below the unit price the agreement sets, or the overbilling is below the tier's smallest claim, so nothing is owed; referred_to_pricing_desk — the overbilling exceeds what the support desk may approve, so the claim goes to the Pricing Desk for review.
        quantity: Fixed-format class — the quantity decided, in integer selling units.
        billed_unit_price: Fixed-format class — the unit price billed on the claimed invoice line, in USD, 4 decimal places.
        contract_unit_price: Fixed-format class — the unit price the agreement sets for the claimed line as decided, in USD, 4 decimal places, rounded half up.

    Returns:
        A dictionary rendered as text with: status ("decided" when the decision line was written),
        price_claim_id (reference number of the new decision line), claim_reference (the claim decided),
        outcome (the decision recorded), contract_unit_price (USD, 4 decimal places) and claim_amount
        (USD, 2 decimal places, always zero on these decisions).
    """
    filing = (ctx.find("pricing_claims", claim_reference=claim_reference, event_type="pricing_claim_filed") or [{}])[0]
    decision = str(outcome).strip()
    price = round(float(contract_unit_price), 4)
    rid = ctx.make_id("pcl_", pricing_agreement_id, claim_reference, decision, int(quantity), billed_unit_price, price)
    ctx.create("pricing_claims", rid, price_claim_id=rid, pricing_agreement_id=pricing_agreement_id,
               customer_id=filing.get("customer_id"), event_type="pricing_claim_decided",
               claim_reference=claim_reference, invoice_number=filing.get("invoice_number"), sku=filing.get("sku"),
               quantity=int(quantity), billed_unit_price=round(float(billed_unit_price), 4), contract_unit_price=price,
               claim_amount=0.0, event_date=ctx.now()[:10], outcome=decision)
    return str({"status": "decided", "price_claim_id": rid, "claim_reference": claim_reference, "outcome": decision,
                "contract_unit_price": price, "claim_amount": 0.0})


@tool(owner="agent", rw="write")
def close_out_discontinued_item_dd8bcab8(ctx: ToolContext, pricing_agreement_id: str, sku: str, contract_unit_price: float,
                                         effective_date: str) -> str:
    """Close out a discontinued contract item on a Contract Pricing Agreement by ending its contract price line.

    The agent records one removal line for the item number named on the agreement's contract item list:
    it ends the item's contract price from the effective date given, records the close-out price as the
    contract unit price that ends, carries the item's product category, list price and supplier cost from
    its current price line, the call date as the notice date and a newly issued change reference. The
    customer sees the item drop off the contract item list from that date.

    Args:
        pricing_agreement_id: Id class — the reference number of the customer's Contract Pricing Agreement, read from the pricing agreement lookup.
        sku: Verbatim class — the Corbett item number of the discontinued contract item exactly as the agreement's contract item records show it, copied character for character (verbatim).
        contract_unit_price: Fixed-format class — the close-out price recorded as the contract unit price that ends, in USD, 4 decimal places, rounded half up.
        effective_date: Fixed-format class — the ship date from which the item no longer carries its contract price, written YYYY-MM-DD.

    Returns:
        A dictionary rendered as text with: status ("closed out" when the removal line was written),
        contract_item_id (reference number of the new removal line), sku (the item number),
        effective_date (YYYY-MM-DD), contract_unit_price (USD, 4 decimal places, the price that ends) and
        change_reference (the change reference issued).
    """
    current = sorted(ctx.find("pricing_items", pricing_agreement_id=pricing_agreement_id, sku=sku),
                     key=lambda row: str(row.get("effective_date")))
    current = current[-1] if current else {}
    price = round(float(contract_unit_price), 4)
    rid = ctx.make_id("pit_", pricing_agreement_id, sku, price, effective_date, "removal")
    change_reference = "PCH-2" + str(int(rid[-10:], 16) % 100000).zfill(5)
    ctx.create("pricing_items", rid, contract_item_id=rid, pricing_agreement_id=pricing_agreement_id,
               customer_id=current.get("customer_id"), event_type="pricing_item_removed", sku=sku,
               product_category=current.get("product_category"), list_price=current.get("list_price", 0.0),
               supplier_cost=current.get("supplier_cost", 0.0), contract_unit_price=price,
               prior_unit_price=current.get("contract_unit_price", 0.0), competitor_unit_price=0.0, quote_date="",
               notice_date=ctx.now()[:10], effective_date=effective_date, change_reason="removal",
               change_reference=change_reference)
    return str({"status": "closed out", "contract_item_id": rid, "sku": sku, "effective_date": effective_date,
                "contract_unit_price": price, "change_reference": change_reference})


@tool(owner="agent", rw="write")
def protect_substitute_price_656c6d72(ctx: ToolContext, pricing_agreement_id: str, sku: str, replaced_sku: str,
                                      contract_unit_price: float, prior_unit_price: float, effective_date: str) -> str:
    """Add the price protection line of a Corbett-approved substitute for a discontinued contract item on a Contract Pricing Agreement.

    The agent records one contract item line for the substitute's item number: it takes effect on the
    effective date given at the protected contract unit price, records the unit price the customer was
    billed for the substitute on its regular shipment, carries the product category of the discontinued item it
    replaces, carries no list price or supplier cost (zero), and receives a newly issued change
    reference. The customer sees the substitute on the contract item list at the protected price.

    Args:
        pricing_agreement_id: Id class — the reference number of the customer's Contract Pricing Agreement, read from the pricing agreement lookup.
        sku: Verbatim class — the Corbett item number of the substitute exactly as the customer's order records show it on the substitute shipments, copied character for character (verbatim).
        replaced_sku: Verbatim class — the Corbett item number of the discontinued contract item the substitute replaces, exactly as the agreement's contract item records show it, copied character for character (verbatim).
        contract_unit_price: Fixed-format class — the protected contract unit price, in USD, 4 decimal places, rounded half up.
        prior_unit_price: Fixed-format class — the unit price the customer was billed for the substitute on its latest regular shipment, in USD, 4 decimal places.
        effective_date: Fixed-format class — the ship date from which the protected price applies, written YYYY-MM-DD.

    Returns:
        A dictionary rendered as text with: status ("protected" when the line was written),
        contract_item_id (reference number of the new contract item line), sku (the substitute's item
        number), effective_date (YYYY-MM-DD), contract_unit_price (USD, 4 decimal places) and
        change_reference (the change reference issued).
    """
    replaced = sorted(ctx.find("pricing_items", pricing_agreement_id=pricing_agreement_id, sku=replaced_sku),
                      key=lambda row: str(row.get("effective_date")))
    replaced = replaced[-1] if replaced else {}
    price = round(float(contract_unit_price), 4)
    rid = ctx.make_id("pit_", pricing_agreement_id, sku, replaced_sku, price, prior_unit_price, effective_date)
    change_reference = "PCH-2" + str(int(rid[-10:], 16) % 100000).zfill(5)
    ctx.create("pricing_items", rid, contract_item_id=rid, pricing_agreement_id=pricing_agreement_id,
               customer_id=replaced.get("customer_id"), event_type="pricing_item_added", sku=sku,
               product_category=replaced.get("product_category"), list_price=0.0, supplier_cost=0.0,
               contract_unit_price=price, prior_unit_price=round(float(prior_unit_price), 4),
               competitor_unit_price=0.0, quote_date="", notice_date="", effective_date=effective_date,
               change_reason="discontinued_substitute", change_reference=change_reference)
    return str({"status": "protected", "contract_item_id": rid, "sku": sku, "effective_date": effective_date,
                "contract_unit_price": price, "change_reference": change_reference})


@tool(owner="user", rw="write")
def file_contract_price_claim_992a36b2(ctx: ToolContext, pricing_agreement_id: str, invoice_number: str, sku: str,
                                       quantity: int, billed_unit_price: float, contract_unit_price: float,
                                       claim_amount: float) -> str:
    """The customer files a contract price claim on one invoice line billed above its Contract Pricing Agreement price.

    The customer's authorized contact files one claim line on the agreement's price claim records for
    the invoice and item named: it carries the quantity claimed, the unit price billed, the unit price
    the agreement sets, the claim amount, the filing date (the day of the call), a pending status and a
    newly issued claim reference. The customer receives the claim reference to track the claim.

    Args:
        pricing_agreement_id: Id class — the reference number of the customer's Contract Pricing Agreement, as the agent reads it from the agreement lookup and hands it to the customer.
        invoice_number: Verbatim class — the invoice number exactly as printed on the customer's invoice, copied character for character (verbatim).
        sku: Verbatim class — the Corbett item number of the billed line exactly as printed on the invoice, copied character for character (verbatim).
        quantity: Fixed-format class — the quantity claimed, in integer selling units, as the agent hands it to the customer.
        billed_unit_price: Fixed-format class — the unit price billed on the line, in USD, 4 decimal places, as printed on the invoice.
        contract_unit_price: Fixed-format class — the unit price the agreement sets for the line, in USD, 4 decimal places, as the agent hands it to the customer.
        claim_amount: Fixed-format class — the claim amount, in USD, 2 decimal places, rounded half up to the cent, as the agent hands it to the customer.

    Returns:
        A dictionary rendered as text with: status ("filed" when the claim line was written),
        price_claim_id (reference number of the new claim line), claim_reference (the claim reference
        issued), claim_amount (USD, 2 decimal places) and outcome (pending, the status of a claim awaiting its decision).
    """
    agreement = (ctx.find("pricing_agreements", pricing_agreement_id=pricing_agreement_id) or [{}])[0]
    amount = round(float(claim_amount), 2)
    rid = ctx.make_id("pcl_", pricing_agreement_id, invoice_number, sku, int(quantity), billed_unit_price,
                      contract_unit_price, amount)
    claim_reference = "PCL-2" + str(int(rid[-10:], 16) % 100000).zfill(5)
    ctx.create("pricing_claims", rid, price_claim_id=rid, pricing_agreement_id=pricing_agreement_id,
               customer_id=agreement.get("customer_id"), event_type="pricing_claim_filed",
               claim_reference=claim_reference, invoice_number=invoice_number, sku=sku, quantity=int(quantity),
               billed_unit_price=round(float(billed_unit_price), 4),
               contract_unit_price=round(float(contract_unit_price), 4), claim_amount=amount,
               event_date=ctx.now()[:10], outcome="pending")
    return str({"status": "filed", "price_claim_id": rid, "claim_reference": claim_reference,
                "claim_amount": amount, "outcome": "pending"})

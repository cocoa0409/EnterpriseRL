"""Hidden task tools of the marketplace_orders_and_guarantee difficulty (category market)."""
from decimal import Decimal, ROUND_HALF_UP

from erlbench import ToolContext, tool


class _Money:
    """Exact half-up rounding to the cent for money arguments."""

    @staticmethod
    def cents(x) -> float:
        return float(Decimal(str(x)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP))

    @staticmethod
    def is_cents(x) -> bool:
        return Decimal(str(x)) == Decimal(str(x)).quantize(Decimal("0.01"))


class _Kit:
    """Field defaults for ledger entries and reference checks shared by the tools."""

    @staticmethod
    def row(**kw):
        row = dict(amount_usd=0.0, line_number=0, sku="", item_description="", quantity=0, unit_price_usd=0.0,
                   item_condition="not_applicable", original_event_id="", return_reason="not_applicable",
                   seller_response="not_applicable", refund_type="not_applicable", restocking_fee_usd=0.0,
                   contact_reason="not_applicable", claim_reason="not_applicable", claim_decision="not_applicable",
                   payment_method_type="none", card_account_id=None)
        row.update(kw)
        return row

    @staticmethod
    def claim_check(ctx, claim_event_id, amount, reason):
        claim = ctx.find("market_events", market_event_id=claim_event_id)
        if not claim or claim[0].get("event_type") != "market_open_claim" or claim[0].get("claim_reason") != reason:
            return None, f"Error: {claim_event_id} is not a {reason} guarantee claim."
        order = ctx.find("market_holdings", market_order_id=claim[0]["market_order_id"])
        if not order or order[0].get("payment_method_type") != "external_card":
            return None, "Error: this reimbursement can be credited only to an order paid with an external card."
        if float(amount) < 0 or not _Money.is_cents(amount):
            return None, "Error: amount_reimbursed_usd must be zero or positive with exactly two decimal places."
        return (claim[0], order[0]), None


@tool(owner="user", rw="write")
def file_return_refund_claim_24f7de0f(ctx: ToolContext, market_order_id: str, line_event_id: str,
                                      units: int, amount_claimed_usd: float) -> str:
    """The buyer files, in person, a Northgate Marketplace Guarantee claim for a return the seller has not refunded
    on one item line of one of their marketplace orders. One call records the buyer's confirmed guarantee-claim
    request on the order and opens the claim with the claim reason return_not_refunded, the item line it concerns,
    the units it covers and the amount claimed, dated today. The claim then waits for the seller's response period
    and Northgate's decision; nothing is refunded by this call. The buyer can see the new claim and its claim
    reference on the order straight away.

    Args:
        market_order_id: Id class — the reference number of the Northgate Marketplace order the claim is filed on,
            read from the buyer's marketplace order lookup.
        line_event_id: Id class — the reference number of the item line of that order the claim concerns, read from
            the order history lookup (an item line entry of this same order).
        units: Fixed-format class — the number of units of that line the claim covers, an integer (whole number, no decimals) of at least 1.
        amount_claimed_usd: Fixed-format class — the amount claimed in US dollars, a positive number rounded to 2
            decimal places (cents), rounded half up to the cent before it is passed.

    Returns:
        A confirmation string reading "Guarantee claim <claim_reference> filed on <market_order_id> (request
        <request_reference>): return_not_refunded, line <line_event_id>, <units> unit(s), USD <amount>." where
        claim_reference is the new claim's reference number (text), request_reference the reference of the
        confirmed claim request (text), units an integer and amount the amount claimed with two decimals. The
        claim reference in the receipt is the sign that the claim is on record.
    """
    order = ctx.find("market_holdings", market_order_id=market_order_id)
    if not order:
        return f"Error: no marketplace order {market_order_id}."
    line = ctx.find("market_events", market_event_id=line_event_id)
    if not line or line[0].get("market_order_id") != market_order_id or line[0].get("event_type") != "market_post_line":
        return f"Error: {line_event_id} is not an item line of order {market_order_id}."
    if int(units) != units or int(units) < 1:
        return "Error: units must be an integer (whole number, no decimals) of at least 1."
    if float(amount_claimed_usd) <= 0 or not _Money.is_cents(amount_claimed_usd):
        return "Error: amount_claimed_usd must be positive with exactly two decimal places."
    amount = _Money.cents(amount_claimed_usd)
    cust = order[0]["customer_id"]
    today = ctx.now()[:10]
    req = ctx.make_id("mrq_", market_order_id, "guarantee_claim", line_event_id, units, amount)
    ctx.create("market_requests", req, market_request_id=req, customer_id=cust, market_order_id=market_order_id,
               request_type="guarantee_claim", request_status="confirmed", created_at=ctx.now())
    cid = ctx.make_id("mev_", market_order_id, "market_open_claim", line_event_id, units, amount)
    ctx.create("market_events", cid, **_Kit.row(
        market_event_id=cid, market_order_id=market_order_id, customer_id=cust, event_type="market_open_claim",
        event_date=today, amount_usd=amount, quantity=int(units), original_event_id=line_event_id,
        claim_reason="return_not_refunded"))
    return (f"Guarantee claim {cid} filed on {market_order_id} (request {req}): return_not_refunded, "
            f"line {line_event_id}, {int(units)} unit(s), USD {amount:.2f}.")


@tool(owner="agent", rw="write")
def grant_return_refund_claim_d58e2e3e(ctx: ToolContext, original_event_id: str, amount_reimbursed_usd: float) -> str:
    """Northgate grants a buyer's Northgate Marketplace Guarantee claim filed because a seller did not refund a
    return, and pays the reimbursement. One call marks that claim as granted, records Northgate's granted decision on
    it dated today, books the guarantee reimbursement of the amount given to the external card the order was paid
    with, and lowers the order's net amount paid by that amount. The buyer sees the claim as granted and the
    reimbursement on the order history.

    Args:
        original_event_id: Id class — the claim reference number of the buyer's return_not_refunded guarantee claim, read from
            the order history lookup (a claim entry of that order).
        amount_reimbursed_usd: Fixed-format class — the reimbursement in US dollars, a number of zero or more rounded to
            2 decimal places (cents), rounded half up to the cent before it is passed. A value of 0.00 does not grant the
            claim; it marks the claim as denied as not covered, records that decision dated today and books no
            reimbursement and no change to the order's net amount paid.

    Returns:
        A confirmation string reading "Claim <original_event_id> granted (decision <decision_reference>); reimbursement
        <reimbursement_reference> of USD <amount> credited to the external card; order <market_order_id> net paid now
        USD <net_paid>." where the references are text, amount and net_paid carry two decimals. The reimbursement
        reference is the sign that the money was booked. For 0.00 it reads "Claim <original_event_id> decided
        denied_not_covered (decision <decision_reference>); no reimbursement booked." where the references are text.
    """
    got, err = _Kit.claim_check(ctx, original_event_id, amount_reimbursed_usd, "return_not_refunded")
    if err:
        return err
    claim, order = got
    amount = _Money.cents(amount_reimbursed_usd)
    mo, cust, today = claim["market_order_id"], claim["customer_id"], ctx.now()[:10]
    if amount == 0:
        ctx.update("market_events", original_event_id, claim_decision="denied_not_covered")
        did = ctx.make_id("mev_", original_event_id, "market_decide_claim", "denied_not_covered")
        ctx.create("market_events", did, **_Kit.row(
            market_event_id=did, market_order_id=mo, customer_id=cust, event_type="market_decide_claim",
            event_date=today, original_event_id=original_event_id, claim_decision="denied_not_covered"))
        return f"Claim {original_event_id} decided denied_not_covered (decision {did}); no reimbursement booked."
    ctx.update("market_events", original_event_id, claim_decision="granted")
    did = ctx.make_id("mev_", original_event_id, "market_decide_claim", "granted")
    ctx.create("market_events", did, **_Kit.row(
        market_event_id=did, market_order_id=mo, customer_id=cust, event_type="market_decide_claim",
        event_date=today, original_event_id=original_event_id, claim_decision="granted"))
    rid = ctx.make_id("mev_", original_event_id, "market_guarantee_reimburse", amount)
    ctx.create("market_events", rid, **_Kit.row(
        market_event_id=rid, market_order_id=mo, customer_id=cust, event_type="market_guarantee_reimburse",
        event_date=today, amount_usd=amount, original_event_id=original_event_id, payment_method_type="external_card"))
    net = _Money.cents(float(order["amount_paid_usd"]) - amount)
    ctx.update("market_holdings", mo, amount_paid_usd=net)
    return (f"Claim {original_event_id} granted (decision {did}); reimbursement {rid} of USD {amount:.2f} credited to "
            f"the external card; order {mo} net paid now USD {net:.2f}.")


@tool(owner="agent", rw="write")
def grant_unresponsive_seller_claim_064f9cf7(ctx: ToolContext, original_event_id: str,
                                             amount_reimbursed_usd: float) -> str:
    """Northgate grants a buyer's Northgate Marketplace Guarantee claim filed because the seller did not respond,
    and pays the reimbursement. One call marks that claim as granted, records Northgate's granted decision on it
    dated today, books the guarantee reimbursement of the amount given to the external card the order was paid with,
    and lowers the order's net amount paid by that amount. The buyer sees the claim as granted and the reimbursement
    on the order history.

    Args:
        original_event_id: Id class — the claim reference number of the buyer's seller_unresponsive guarantee claim, read from
            the order history lookup (a claim entry of that order).
        amount_reimbursed_usd: Fixed-format class — the reimbursement in US dollars, a number of zero or more rounded to
            2 decimal places (cents), rounded half up to the cent before it is passed. A value of 0.00 does not grant the
            claim; it marks the claim as denied as not covered, records that decision dated today and books no
            reimbursement and no change to the order's net amount paid.

    Returns:
        A confirmation string reading "Claim <original_event_id> granted (decision <decision_reference>); reimbursement
        <reimbursement_reference> of USD <amount> credited to the external card; order <market_order_id> net paid now
        USD <net_paid>." where the references are text, amount and net_paid carry two decimals. The reimbursement
        reference is the sign that the money was booked. For 0.00 it reads "Claim <original_event_id> decided
        denied_not_covered (decision <decision_reference>); no reimbursement booked." where the references are text.
    """
    got, err = _Kit.claim_check(ctx, original_event_id, amount_reimbursed_usd, "seller_unresponsive")
    if err:
        return err
    claim, order = got
    amount = _Money.cents(amount_reimbursed_usd)
    mo, cust, today = claim["market_order_id"], claim["customer_id"], ctx.now()[:10]
    if amount == 0:
        ctx.update("market_events", original_event_id, claim_decision="denied_not_covered")
        did = ctx.make_id("mev_", original_event_id, "market_decide_claim", "denied_not_covered")
        ctx.create("market_events", did, **_Kit.row(
            market_event_id=did, market_order_id=mo, customer_id=cust, event_type="market_decide_claim",
            event_date=today, original_event_id=original_event_id, claim_decision="denied_not_covered"))
        return f"Claim {original_event_id} decided denied_not_covered (decision {did}); no reimbursement booked."
    ctx.update("market_events", original_event_id, claim_decision="granted")
    did = ctx.make_id("mev_", original_event_id, "market_decide_claim", "granted")
    ctx.create("market_events", did, **_Kit.row(
        market_event_id=did, market_order_id=mo, customer_id=cust, event_type="market_decide_claim",
        event_date=today, original_event_id=original_event_id, claim_decision="granted"))
    rid = ctx.make_id("mev_", original_event_id, "market_guarantee_reimburse", amount)
    ctx.create("market_events", rid, **_Kit.row(
        market_event_id=rid, market_order_id=mo, customer_id=cust, event_type="market_guarantee_reimburse",
        event_date=today, amount_usd=amount, original_event_id=original_event_id, payment_method_type="external_card"))
    net = _Money.cents(float(order["amount_paid_usd"]) - amount)
    ctx.update("market_holdings", mo, amount_paid_usd=net)
    return (f"Claim {original_event_id} granted (decision {did}); reimbursement {rid} of USD {amount:.2f} credited to "
            f"the external card; order {mo} net paid now USD {net:.2f}.")


@tool(owner="agent", rw="write")
def refund_keepit_units_1db7244d(ctx: ToolContext, request_event_id: str, amount_refunded_usd: float) -> str:
    """Book the refund a marketplace seller agreed to give without asking for the item back, for the units of one
    return request. One call books a unit refund on the item line of that return request for the units the request
    named, of the amount given, with no restocking fee recorded, credited to the external card the order was paid
    with, and lowers the order's net amount paid by that amount. The buyer sees the refund on the order history and
    keeps the item.

    Args:
        request_event_id: Id class — the reference number of the return request the seller answered with a refund
            without return, read from the order history lookup (a return request entry of the order).
        amount_refunded_usd: Fixed-format class — the refund in US dollars, a positive number rounded to 2
            decimal places (cents), rounded half up to the cent before it is passed.

    Returns:
        A confirmation string reading "Refund <refund_reference> of USD <amount> booked on line <line_event_id> for
        <units> unit(s) of request <request_event_id>, credited to the external card; order <market_order_id> net
        paid now USD <net_paid>." where references are text, units an integer, amount and net_paid carry two
        decimals. The refund reference is the sign that the refund was booked.
    """
    req = ctx.find("market_events", market_event_id=request_event_id)
    if not req or req[0].get("event_type") != "market_request_return":
        return f"Error: {request_event_id} is not a return request."
    answers = ctx.find("market_events", original_event_id=request_event_id, event_type="market_seller_respond")
    if not any(a.get("seller_response") == "refund_without_return" for a in answers):
        return f"Error: {request_event_id} was not answered with a refund without return."
    order = ctx.find("market_holdings", market_order_id=req[0]["market_order_id"])
    if not order or order[0].get("payment_method_type") != "external_card":
        return "Error: this refund can be credited only to an order paid with an external card."
    if float(amount_refunded_usd) <= 0 or not _Money.is_cents(amount_refunded_usd):
        return "Error: amount_refunded_usd must be positive with exactly two decimal places."
    amount = _Money.cents(amount_refunded_usd)
    r, mo = req[0], req[0]["market_order_id"]
    rid = ctx.make_id("mev_", request_event_id, "market_seller_refund", amount)
    ctx.create("market_events", rid, **_Kit.row(
        market_event_id=rid, market_order_id=mo, customer_id=r["customer_id"], event_type="market_seller_refund",
        event_date=ctx.now()[:10], amount_usd=amount, quantity=int(r["quantity"]),
        original_event_id=r["original_event_id"], refund_type="return_refund", payment_method_type="external_card"))
    net = _Money.cents(float(order[0]["amount_paid_usd"]) - amount)
    ctx.update("market_holdings", mo, amount_paid_usd=net)
    return (f"Refund {rid} of USD {amount:.2f} booked on line {r['original_event_id']} for {int(r['quantity'])} "
            f"unit(s) of request {request_event_id}, credited to the external card; order {mo} net paid now "
            f"USD {net:.2f}.")


@tool(owner="user", rw="write")
def file_item_condition_claim_763dfc78(ctx: ToolContext, market_order_id: str, line_event_id: str,
                                      units: int, amount_claimed_usd: float) -> str:
    """The buyer files, in person, a Northgate Marketplace Guarantee claim for items that arrived not as described
    on one item line of one of their marketplace orders. One call records the buyer's confirmed guarantee-claim
    request on the order and opens the claim with the claim reason not_as_described, the item line it concerns,
    the units it covers and the amount claimed, dated today. The claim then waits for the seller's response period
    and Northgate's decision; nothing is refunded by this call. The buyer can see the new claim and its claim
    reference on the order straight away.

    Args:
        market_order_id: Id class — the reference number of the Northgate Marketplace order the claim is filed on,
            read from the buyer's marketplace order lookup.
        line_event_id: Id class — the reference number of the item line of that order the claim concerns, read from
            the order history lookup (an item line entry of this same order).
        units: Fixed-format class — the number of units of that line the claim covers, an integer (whole number, no decimals) of at least 1.
        amount_claimed_usd: Fixed-format class — the amount claimed in US dollars, a positive number rounded to 2
            decimal places (cents), rounded half up to the cent before it is passed.

    Returns:
        A confirmation string reading "Guarantee claim <claim_reference> filed on <market_order_id> (request
        <request_reference>): not_as_described, line <line_event_id>, <units> unit(s), USD <amount>." where
        claim_reference is the new claim's reference number (text), request_reference the reference of the
        confirmed claim request (text), units an integer and amount the amount claimed with two decimals. The
        claim reference in the receipt is the sign that the claim is on record.
    """
    order = ctx.find("market_holdings", market_order_id=market_order_id)
    if not order:
        return f"Error: no marketplace order {market_order_id}."
    line = ctx.find("market_events", market_event_id=line_event_id)
    if not line or line[0].get("market_order_id") != market_order_id or line[0].get("event_type") != "market_post_line":
        return f"Error: {line_event_id} is not an item line of order {market_order_id}."
    if int(units) != units or int(units) < 1:
        return "Error: units must be an integer (whole number, no decimals) of at least 1."
    if float(amount_claimed_usd) <= 0 or not _Money.is_cents(amount_claimed_usd):
        return "Error: amount_claimed_usd must be positive with exactly two decimal places."
    amount = _Money.cents(amount_claimed_usd)
    cust = order[0]["customer_id"]
    today = ctx.now()[:10]
    req = ctx.make_id("mrq_", market_order_id, "guarantee_claim", line_event_id, units, amount)
    ctx.create("market_requests", req, market_request_id=req, customer_id=cust, market_order_id=market_order_id,
               request_type="guarantee_claim", request_status="confirmed", created_at=ctx.now())
    cid = ctx.make_id("mev_", market_order_id, "market_open_claim", line_event_id, units, amount)
    ctx.create("market_events", cid, **_Kit.row(
        market_event_id=cid, market_order_id=market_order_id, customer_id=cust, event_type="market_open_claim",
        event_date=today, amount_usd=amount, quantity=int(units), original_event_id=line_event_id,
        claim_reason="not_as_described"))
    return (f"Guarantee claim {cid} filed on {market_order_id} (request {req}): not_as_described, "
            f"line {line_event_id}, {int(units)} unit(s), USD {amount:.2f}.")


@tool(owner="agent", rw="write")
def grant_missing_item_claim_35c21a00(ctx: ToolContext, original_event_id: str,
                                             amount_reimbursed_usd: float) -> str:
    """Northgate grants a buyer's Northgate Marketplace Guarantee claim filed because ordered items never arrived,
    and pays the reimbursement. One call marks that claim as granted, records Northgate's granted decision on it
    dated today, books the guarantee reimbursement of the amount given to the external card the order was paid with,
    and lowers the order's net amount paid by that amount. The buyer sees the claim as granted and the reimbursement
    on the order history.

    Args:
        original_event_id: Id class — the claim reference number of the buyer's not_received guarantee claim, read from
            the order history lookup (a claim entry of that order).
        amount_reimbursed_usd: Fixed-format class — the reimbursement in US dollars, a number of zero or more rounded to
            2 decimal places (cents), rounded half up to the cent before it is passed. A value of 0.00 does not grant the
            claim; it marks the claim as denied as not covered, records that decision dated today and books no
            reimbursement and no change to the order's net amount paid.

    Returns:
        A confirmation string reading "Claim <original_event_id> granted (decision <decision_reference>); reimbursement
        <reimbursement_reference> of USD <amount> credited to the external card; order <market_order_id> net paid now
        USD <net_paid>." where the references are text, amount and net_paid carry two decimals. The reimbursement
        reference is the sign that the money was booked. For 0.00 it reads "Claim <original_event_id> decided
        denied_not_covered (decision <decision_reference>); no reimbursement booked." where the references are text.
    """
    got, err = _Kit.claim_check(ctx, original_event_id, amount_reimbursed_usd, "not_received")
    if err:
        return err
    claim, order = got
    amount = _Money.cents(amount_reimbursed_usd)
    mo, cust, today = claim["market_order_id"], claim["customer_id"], ctx.now()[:10]
    if amount == 0:
        ctx.update("market_events", original_event_id, claim_decision="denied_not_covered")
        did = ctx.make_id("mev_", original_event_id, "market_decide_claim", "denied_not_covered")
        ctx.create("market_events", did, **_Kit.row(
            market_event_id=did, market_order_id=mo, customer_id=cust, event_type="market_decide_claim",
            event_date=today, original_event_id=original_event_id, claim_decision="denied_not_covered"))
        return f"Claim {original_event_id} decided denied_not_covered (decision {did}); no reimbursement booked."
    ctx.update("market_events", original_event_id, claim_decision="granted")
    did = ctx.make_id("mev_", original_event_id, "market_decide_claim", "granted")
    ctx.create("market_events", did, **_Kit.row(
        market_event_id=did, market_order_id=mo, customer_id=cust, event_type="market_decide_claim",
        event_date=today, original_event_id=original_event_id, claim_decision="granted"))
    rid = ctx.make_id("mev_", original_event_id, "market_guarantee_reimburse", amount)
    ctx.create("market_events", rid, **_Kit.row(
        market_event_id=rid, market_order_id=mo, customer_id=cust, event_type="market_guarantee_reimburse",
        event_date=today, amount_usd=amount, original_event_id=original_event_id, payment_method_type="external_card"))
    net = _Money.cents(float(order["amount_paid_usd"]) - amount)
    ctx.update("market_holdings", mo, amount_paid_usd=net)
    return (f"Claim {original_event_id} granted (decision {did}); reimbursement {rid} of USD {amount:.2f} credited to "
            f"the external card; order {mo} net paid now USD {net:.2f}.")


@tool(owner="agent", rw="write")
def refund_restocking_shortfall_469f1911(ctx: ToolContext, request_event_id: str, amount_refunded_usd: float) -> str:
    """Book Northgate's top-up of a seller's return refund that withheld more restocking than allowed for the
    request's reason, for one return request. One call books a top-up refund on the item line of that return request, with no units (the units
    were already refunded by the seller) and no restocking fee recorded, of the amount given, credited to the external
    card the order was paid with, and lowers the order's net amount paid by that amount. The buyer sees the top-up on
    the order history.

    Args:
        request_event_id: Id class — the reference number of the return request whose seller refund is being
            topped up, read from the order history lookup (a return request entry of the order that the seller
            answered with a return authorization).
        amount_refunded_usd: Fixed-format class — the refund in US dollars, a positive number rounded to 2
            decimal places (cents), rounded half up to the cent before it is passed.

    Returns:
        A confirmation string reading "Refund <refund_reference> of USD <amount> booked on line <line_event_id> for
        request <request_event_id>, credited to the external card; order <market_order_id> net paid now USD
        <net_paid>." where references are text, amount and net_paid carry two decimals. The refund reference is
        the sign that the top-up was booked.
    """
    req = ctx.find("market_events", market_event_id=request_event_id)
    if not req or req[0].get("event_type") != "market_request_return":
        return f"Error: {request_event_id} is not a return request."
    answers = ctx.find("market_events", original_event_id=request_event_id, event_type="market_seller_respond")
    if not any(a.get("seller_response") == "authorized_return" for a in answers):
        return f"Error: {request_event_id} carries no return authorization."
    order = ctx.find("market_holdings", market_order_id=req[0]["market_order_id"])
    if not order or order[0].get("payment_method_type") != "external_card":
        return "Error: this refund can be credited only to an order paid with an external card."
    if float(amount_refunded_usd) <= 0 or not _Money.is_cents(amount_refunded_usd):
        return "Error: amount_refunded_usd must be positive with exactly two decimal places."
    amount = _Money.cents(amount_refunded_usd)
    r, mo = req[0], req[0]["market_order_id"]
    rid = ctx.make_id("mev_", request_event_id, "market_seller_refund", "top_up", amount)
    ctx.create("market_events", rid, **_Kit.row(
        market_event_id=rid, market_order_id=mo, customer_id=r["customer_id"], event_type="market_seller_refund",
        event_date=ctx.now()[:10], amount_usd=amount, quantity=0,
        original_event_id=r["original_event_id"], refund_type="return_refund", payment_method_type="external_card"))
    net = _Money.cents(float(order[0]["amount_paid_usd"]) - amount)
    ctx.update("market_holdings", mo, amount_paid_usd=net)
    return (f"Refund {rid} of USD {amount:.2f} booked on line {r['original_event_id']} "
            f"for request {request_event_id}, credited to the external card; order {mo} net paid now "
            f"USD {net:.2f}.")

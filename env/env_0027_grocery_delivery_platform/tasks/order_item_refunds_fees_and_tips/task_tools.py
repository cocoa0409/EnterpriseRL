"""Hidden task tools for env_0027_grocery_delivery_platform / order_item_refunds_fees_and_tips (category: order).

Each tool performs one atomic write on a Cartwise grocery order and is reached only through the
unlock_* -> call_* meta-tools after its name has been read from the order charter. No tool checks a
policy precondition, aggregates history or computes an amount: the agent settles eligibility and the
figure from the published policy and the records, and passes the figure in.
"""

from erlbench import ToolContext, tool


@tool(owner="agent", rw="write")
def refund_wrong_item_79d6dec9(ctx: ToolContext, customer_id: str, order_id: str, line_number: int,
                               source_event_id: str, refund_reason: str, amount_usd: float) -> str:
    """Book a refund on one billed item line of a Cartwise grocery order for a product that was handed over
    in place of the one the customer had approved. One call adds one item-refund entry to the order: it
    names the order line and the billed line entry it pays back, carries the controlled refund reason and
    the refunded amount, and returns the money to the customer's original payment method, lowering the
    net amount billed on the order by that amount. The refund shows at once among the order's entries
    with today's date; the receipt below confirms it was booked.

    Args:
        customer_id: Id class — the customer reference number of the person who placed the order, read from the customer profile lookup before the call.
        order_id: Id class — the order number of the grocery order being refunded, read from the order lookup before the call.
        line_number: Fixed-format class — the position of the refunded item line on the order, an integer (1, 2, 3 ...) exactly as shown on the billed line entry; no decimals.
        source_event_id: Id class — the reference number of the billed item line entry (the line charge) this refund pays back, read from the order entries lookup before the call.
        refund_reason: Enum class — the controlled reason recorded on the refund, exactly one of these literals:
            missing — the billed product never reached the customer;
            damaged — the product arrived broken, crushed or leaking;
            wrong_item — a different product from the one ordered or approved was handed over;
            quality — the product arrived spoiled, expired or otherwise unfit;
            substitution_rejected — the customer turned down a delivered replacement product;
            substitution_price_protection — the replacement was billed above the protected price of the original;
            weight_overage — a product sold by weight was billed above the allowed weight;
            alcohol_id_failed — alcohol lines were taken back because the ID check at handoff failed;
            returned_order — the whole order went back to the store undelivered;
            late_delivery — a fee returned because the order completed late (fee refunds only);
            item_refund_share — the service fee share returned with item refunds (fee refunds only).
        amount_usd: Fixed-format class — the amount refunded on the line, in USD, a positive number with 2 decimal places, rounded half up to the cent before it is passed; never 0 or negative.

    Returns:
        A dictionary rendered as text with these fields: order_event_id (text, the reference number of the
        new refund entry), order_id (text, the order refunded), line_number (integer, the refunded line),
        refund_reason (text, the reason recorded), refund_destination (text, always original_payment_method),
        amount_usd (number, USD with 2 decimal places, the amount booked) and status (text, "booked" when the
        refund entry now stands on the order).
    """
    rid = ctx.make_id("oev_", customer_id, order_id, line_number, source_event_id, refund_reason, amount_usd)
    amount = round(float(amount_usd), 2)
    ctx.create("order_events", rid, order_event_id=rid, order_id=order_id, customer_id=customer_id,
               event_type="order_item_refunded", line_number=int(line_number), source_event_id=source_event_id,
               refund_reason=refund_reason, refund_destination="original_payment_method",
               amount_usd=amount, event_date=ctx.now()[:10])
    return str({"order_event_id": rid, "order_id": order_id, "line_number": int(line_number),
                "refund_reason": refund_reason, "refund_destination": "original_payment_method",
                "amount_usd": amount, "status": "booked"})


@tool(owner="agent", rw="write")
def refund_unfound_item_93423917(ctx: ToolContext, customer_id: str, order_id: str, line_number: int,
                                 source_event_id: str, refund_reason: str, amount_usd: float) -> str:
    """Book a refund on one billed item line of a Cartwise grocery order whose product the shopper recorded
    as not found in the store although the line was still billed. One call adds one item-refund entry to the
    order: it names the order line and the billed line entry it pays back, carries the controlled refund
    reason and the refunded amount, and returns the money to the customer's original payment method,
    lowering the net amount billed on the order by that amount. The refund shows at once among the order's
    entries with today's date; the receipt below confirms it was booked.

    Args:
        customer_id: Id class — the customer reference number of the person who placed the order, read from the customer profile lookup before the call.
        order_id: Id class — the order number of the grocery order being refunded, read from the order lookup before the call.
        line_number: Fixed-format class — the position of the refunded item line on the order, an integer (1, 2, 3 ...) exactly as shown on the billed line entry; no decimals.
        source_event_id: Id class — the reference number of the billed item line entry (the line charge) this refund pays back, read from the order entries lookup before the call.
        refund_reason: Enum class — the controlled reason recorded on the refund, exactly one of these literals:
            missing — the billed product never reached the customer;
            damaged — the product arrived broken, crushed or leaking;
            wrong_item — a different product from the one ordered or approved was handed over;
            quality — the product arrived spoiled, expired or otherwise unfit;
            substitution_rejected — the customer turned down a delivered replacement product;
            substitution_price_protection — the replacement was billed above the protected price of the original;
            weight_overage — a product sold by weight was billed above the allowed weight;
            alcohol_id_failed — alcohol lines were taken back because the ID check at handoff failed;
            returned_order — the whole order went back to the store undelivered;
            late_delivery — a fee returned because the order completed late (fee refunds only);
            item_refund_share — the service fee share returned with item refunds (fee refunds only).
        amount_usd: Fixed-format class — the amount refunded on the line, in USD, a positive number with 2 decimal places, rounded half up to the cent before it is passed; never 0 or negative.

    Returns:
        A dictionary rendered as text with these fields: order_event_id (text, the reference number of the
        new refund entry), order_id (text, the order refunded), line_number (integer, the refunded line),
        refund_reason (text, the reason recorded), refund_destination (text, always original_payment_method),
        amount_usd (number, USD with 2 decimal places, the amount booked) and status (text, "booked" when the
        refund entry now stands on the order).
    """
    rid = ctx.make_id("oev_", customer_id, order_id, line_number, source_event_id, refund_reason, amount_usd)
    amount = round(float(amount_usd), 2)
    ctx.create("order_events", rid, order_event_id=rid, order_id=order_id, customer_id=customer_id,
               event_type="order_item_refunded", line_number=int(line_number), source_event_id=source_event_id,
               refund_reason=refund_reason, refund_destination="original_payment_method",
               amount_usd=amount, event_date=ctx.now()[:10])
    return str({"order_event_id": rid, "order_id": order_id, "line_number": int(line_number),
                "refund_reason": refund_reason, "refund_destination": "original_payment_method",
                "amount_usd": amount, "status": "booked"})


@tool(owner="agent", rw="write")
def register_over_cap_review_9b0d89a0(ctx: ToolContext, customer_id: str, order_id: str, line_number: int,
                                      refund_reason: str, requested_amount_usd: float) -> str:
    """Send to the Cartwise refund review team the part of an item refund on one order line that the support
    desk does not book itself because it lies above the order's self-service refund limit. One call registers
    one review request for the named order line with the review type "refund over cap", the requested amount
    and the status "submitted"; nothing is refunded by this call and the order's billed amount does not
    change. The request shows at once among the order's review requests, stamped with the current time,
    and stays submitted until the review team approves or denies it.

    Args:
        customer_id: Id class — the customer reference number of the person who placed the order, read from the customer profile lookup before the call.
        order_id: Id class — the order number of the grocery order the request concerns, read from the order lookup before the call.
        line_number: Fixed-format class — the position of the order line the request concerns, an integer (1, 2, 3 ...) exactly as shown on the billed line entry; no decimals.
        refund_reason: Enum class — the controlled reason of the item refund the request continues, exactly one of these literals:
            missing — the billed product never reached the customer;
            damaged — the product arrived broken, crushed or leaking;
            wrong_item — a different product from the one ordered or approved was handed over;
            quality — the product arrived spoiled, expired or otherwise unfit.
        requested_amount_usd: Fixed-format class — the amount sent to the review team, in USD, a positive number with 2 decimal places, rounded half up to the cent before it is passed; never 0 or negative.

    Returns:
        A dictionary rendered as text with these fields: order_review_request_id (text, the reference number
        of the new review request), order_id (text, the order concerned), line_number (integer, the line
        concerned), refund_reason (text, the reason the request continues), request_type (text, always
        refund_over_cap), requested_amount_usd (number, USD with 2 decimal places) and request_status (text,
        "submitted" when the request now waits for the review team).
    """
    rid = ctx.make_id("orr_", customer_id, order_id, line_number, refund_reason, requested_amount_usd)
    amount = round(float(requested_amount_usd), 2)
    ctx.create("order_review_requests", rid, order_review_request_id=rid, customer_id=customer_id,
               order_id=order_id, line_number=int(line_number), request_type="refund_over_cap",
               requested_amount_usd=amount, request_status="submitted", created_at=ctx.now())
    return str({"order_review_request_id": rid, "order_id": order_id, "line_number": int(line_number),
                "refund_reason": refund_reason, "request_type": "refund_over_cap",
                "requested_amount_usd": amount, "request_status": "submitted"})


@tool(owner="user", rw="write")
def submit_limit_review_claim_079a4c96(ctx: ToolContext, customer_id: str, order_id: str, line_number: int,
                                       refund_reason: str, requested_amount_usd: float) -> str:
    """The customer submits, from their own Cartwise account, their claim on one item line of a grocery
    order to the refund review team, when the support desk cannot book that refund because the customer's
    recent refunds have reached the rolling limits. One call registers one review request for the named
    order line with the review type "rolling limit review", the requested amount and the status
    "submitted"; nothing is refunded by this call and the order's billed amount does not change. The
    customer sees the claim at once among the order's review requests, stamped with the current time, and
    it stays submitted until the review team approves or denies it.

    Args:
        customer_id: Id class — the customer reference number of the claimant's own profile, handed over by the support agent from the customer profile lookup.
        order_id: Id class — the order number of the grocery order the claim concerns, handed over by the support agent from the order lookup.
        line_number: Fixed-format class — the position of the claimed item line on the order, an integer (1, 2, 3 ...) exactly as shown on the billed line entry; no decimals.
        refund_reason: Enum class — the controlled reason of the claim, exactly one of these literals:
            missing — the billed product never reached the customer;
            damaged — the product arrived broken, crushed or leaking;
            wrong_item — a different product from the one ordered or approved was handed over;
            quality — the product arrived spoiled, melted, expired or otherwise unfit.
        requested_amount_usd: Fixed-format class — the amount the claim asks the review team for, in USD, a positive number with 2 decimal places, rounded half up to the cent before it is passed; never 0 or negative.

    Returns:
        A dictionary rendered as text with these fields: order_review_request_id (text, the reference number
        of the new claim), order_id (text, the order concerned), line_number (integer, the line claimed),
        refund_reason (text, the reason claimed), request_type (text, always refund_limit_review),
        requested_amount_usd (number, USD with 2 decimal places) and request_status (text, "submitted" when
        the claim now waits for the review team).
    """
    rid = ctx.make_id("orr_", customer_id, order_id, line_number, refund_reason, requested_amount_usd)
    amount = round(float(requested_amount_usd), 2)
    ctx.create("order_review_requests", rid, order_review_request_id=rid, customer_id=customer_id,
               order_id=order_id, line_number=int(line_number), request_type="refund_limit_review",
               requested_amount_usd=amount, request_status="submitted", created_at=ctx.now())
    return str({"order_review_request_id": rid, "order_id": order_id, "line_number": int(line_number),
                "refund_reason": refund_reason, "request_type": "refund_limit_review",
                "requested_amount_usd": amount, "request_status": "submitted"})


@tool(owner="agent", rw="write")
def refund_weight_overage_a9b70a98(ctx: ToolContext, customer_id: str, order_id: str, line_number: int,
                                 source_event_id: str, refund_reason: str, amount_usd: float) -> str:
    """Book a refund on one billed item line of a Cartwise grocery order for a product sold by weight that
    was billed on more weight than the customer may be charged for. One call adds one item-refund entry to the
    order: it names the order line and the billed line entry it pays back, carries the controlled refund
    reason and the refunded amount, and returns the money to the customer's original payment method,
    lowering the net amount billed on the order by that amount. The refund shows at once among the order's
    entries with today's date; the receipt below confirms it was booked.

    Args:
        customer_id: Id class — the customer reference number of the person who placed the order, read from the customer profile lookup before the call.
        order_id: Id class — the order number of the grocery order being refunded, read from the order lookup before the call.
        line_number: Fixed-format class — the position of the refunded item line on the order, an integer (1, 2, 3 ...) exactly as shown on the billed line entry; no decimals.
        source_event_id: Id class — the reference number of the billed item line entry (the line charge) this refund pays back, read from the order entries lookup before the call.
        refund_reason: Enum class — the controlled reason recorded on the refund, exactly one of these literals:
            missing — the billed product never reached the customer;
            damaged — the product arrived broken, crushed or leaking;
            wrong_item — a different product from the one ordered or approved was handed over;
            quality — the product arrived spoiled, expired or otherwise unfit;
            substitution_rejected — the customer turned down a delivered replacement product;
            substitution_price_protection — the replacement was billed above the protected price of the original;
            weight_overage — a product sold by weight was billed above the allowed weight;
            alcohol_id_failed — alcohol lines were taken back because the ID check at handoff failed;
            returned_order — the whole order went back to the store undelivered;
            late_delivery — a fee returned because the order completed late (fee refunds only);
            item_refund_share — the service fee share returned with item refunds (fee refunds only).
        amount_usd: Fixed-format class — the amount refunded on the line, in USD, a positive number with 2 decimal places, rounded half up to the cent before it is passed; never 0 or negative.

    Returns:
        A dictionary rendered as text with these fields: order_event_id (text, the reference number of the
        new refund entry), order_id (text, the order refunded), line_number (integer, the refunded line),
        refund_reason (text, the reason recorded), refund_destination (text, always original_payment_method),
        amount_usd (number, USD with 2 decimal places, the amount booked) and status (text, "booked" when the
        refund entry now stands on the order).
    """
    rid = ctx.make_id("oev_", customer_id, order_id, line_number, source_event_id, refund_reason, amount_usd)
    amount = round(float(amount_usd), 2)
    ctx.create("order_events", rid, order_event_id=rid, order_id=order_id, customer_id=customer_id,
               event_type="order_item_refunded", line_number=int(line_number), source_event_id=source_event_id,
               refund_reason=refund_reason, refund_destination="original_payment_method",
               amount_usd=amount, event_date=ctx.now()[:10])
    return str({"order_event_id": rid, "order_id": order_id, "line_number": int(line_number),
                "refund_reason": refund_reason, "refund_destination": "original_payment_method",
                "amount_usd": amount, "status": "booked"})


@tool(owner="agent", rw="write")
def refund_substitution_overcharge_0e292d66(ctx: ToolContext, customer_id: str, order_id: str, line_number: int,
                                 source_event_id: str, refund_reason: str, amount_usd: float) -> str:
    """Book a refund on one billed item line of a Cartwise grocery order where the replacement product the
    shopper chose was billed above the price the customer is protected at. One call adds one item-refund entry to the
    order: it names the order line and the billed line entry it pays back, carries the controlled refund
    reason and the refunded amount, and returns the money to the customer's original payment method,
    lowering the net amount billed on the order by that amount. The refund shows at once among the order's
    entries with today's date; the receipt below confirms it was booked.

    Args:
        customer_id: Id class — the customer reference number of the person who placed the order, read from the customer profile lookup before the call.
        order_id: Id class — the order number of the grocery order being refunded, read from the order lookup before the call.
        line_number: Fixed-format class — the position of the refunded item line on the order, an integer (1, 2, 3 ...) exactly as shown on the billed line entry; no decimals.
        source_event_id: Id class — the reference number of the billed item line entry (the line charge) this refund pays back, read from the order entries lookup before the call.
        refund_reason: Enum class — the controlled reason recorded on the refund, exactly one of these literals:
            missing — the billed product never reached the customer;
            damaged — the product arrived broken, crushed or leaking;
            wrong_item — a different product from the one ordered or approved was handed over;
            quality — the product arrived spoiled, expired or otherwise unfit;
            substitution_rejected — the customer turned down a delivered replacement product;
            substitution_price_protection — the replacement was billed above the protected price of the original;
            weight_overage — a product sold by weight was billed above the allowed weight;
            alcohol_id_failed — alcohol lines were taken back because the ID check at handoff failed;
            returned_order — the whole order went back to the store undelivered;
            late_delivery — a fee returned because the order completed late (fee refunds only);
            item_refund_share — the service fee share returned with item refunds (fee refunds only).
        amount_usd: Fixed-format class — the amount refunded on the line, in USD, a positive number with 2 decimal places, rounded half up to the cent before it is passed; never 0 or negative.

    Returns:
        A dictionary rendered as text with these fields: order_event_id (text, the reference number of the
        new refund entry), order_id (text, the order refunded), line_number (integer, the refunded line),
        refund_reason (text, the reason recorded), refund_destination (text, always original_payment_method),
        amount_usd (number, USD with 2 decimal places, the amount booked) and status (text, "booked" when the
        refund entry now stands on the order).
    """
    rid = ctx.make_id("oev_", customer_id, order_id, line_number, source_event_id, refund_reason, amount_usd)
    amount = round(float(amount_usd), 2)
    ctx.create("order_events", rid, order_event_id=rid, order_id=order_id, customer_id=customer_id,
               event_type="order_item_refunded", line_number=int(line_number), source_event_id=source_event_id,
               refund_reason=refund_reason, refund_destination="original_payment_method",
               amount_usd=amount, event_date=ctx.now()[:10])
    return str({"order_event_id": rid, "order_id": order_id, "line_number": int(line_number),
                "refund_reason": refund_reason, "refund_destination": "original_payment_method",
                "amount_usd": amount, "status": "booked"})


@tool(owner="agent", rw="write")
def refund_service_fee_share_1e350a8d(ctx: ToolContext, customer_id: str, order_id: str, source_event_id: str,
                                      amount_usd: float) -> str:
    """Return to the customer part of the service fee billed on a Cartwise grocery order, as the service-fee
    share that goes back with item refunds on that order. One call adds one fee-refund entry to the order for
    the service fee charge it names, with the reason "item refund share" and the refunded amount, paid to the
    customer's original payment method; the order's net billed amount falls by that amount. The fee refund
    shows at once among the order's entries with today's date; the receipt below confirms it was booked.

    Args:
        customer_id: Id class — the customer reference number of the person who placed the order, read from the customer profile lookup before the call.
        order_id: Id class — the order number of the grocery order whose service fee is partly returned, read from the order lookup before the call.
        source_event_id: Id class — the reference number of the service fee charge entry on that order that this refund pays back, read from the order entries lookup before the call.
        amount_usd: Fixed-format class — the amount of service fee returned, in USD, a positive number with 2 decimal places, rounded half up to the cent before it is passed; never 0 or negative.

    Returns:
        A dictionary rendered as text with these fields: order_event_id (text, the reference number of the
        new fee-refund entry), order_id (text, the order refunded), fee_type (text, always service),
        refund_reason (text, always item_refund_share), refund_destination (text, always
        original_payment_method), amount_usd (number, USD with 2 decimal places, the amount booked) and status
        (text, "booked" when the fee refund now stands on the order).
    """
    rid = ctx.make_id("oev_", customer_id, order_id, source_event_id, amount_usd)
    amount = round(float(amount_usd), 2)
    ctx.create("order_events", rid, order_event_id=rid, order_id=order_id, customer_id=customer_id,
               event_type="order_fee_refunded", source_event_id=source_event_id, fee_type="service",
               refund_reason="item_refund_share", refund_destination="original_payment_method",
               amount_usd=amount, event_date=ctx.now()[:10])
    return str({"order_event_id": rid, "order_id": order_id, "fee_type": "service",
                "refund_reason": "item_refund_share", "refund_destination": "original_payment_method",
                "amount_usd": amount, "status": "booked"})


@tool(owner="user", rw="write")
def submit_photo_review_claim_a5aac31c(ctx: ToolContext, customer_id: str, order_id: str, line_number: int,
                                       refund_reason: str, requested_amount_usd: float) -> str:
    """The customer submits, from their own Cartwise account, their claim that an item on one line of a
    grocery order arrived damaged or spoiled, for the refund review team to decide on a line whose charge is
    too high for the support desk to refund without a photo on the case. One call registers one review
    request for the named order line with the review type "photo review", the requested amount and the
    status "submitted"; nothing is refunded by this call and the order's billed amount does not change. The
    customer sees the claim at once among the order's review requests, stamped with the current time, and it
    stays submitted until the review team approves or denies it.

    Args:
        customer_id: Id class — the customer reference number of the claimant's own profile, handed over by the support agent from the customer profile lookup.
        order_id: Id class — the order number of the grocery order the claim concerns, handed over by the support agent from the order lookup.
        line_number: Fixed-format class — the position of the claimed item line on the order, an integer (1, 2, 3 ...) exactly as shown on the billed line entry; no decimals.
        refund_reason: Enum class — the controlled reason of the claim, exactly one of these literals:
            missing — the billed product never reached the customer;
            damaged — the product arrived broken, crushed or leaking;
            wrong_item — a different product from the one ordered or approved was handed over;
            quality — the product arrived spoiled, off-smelling, expired or otherwise unfit.
        requested_amount_usd: Fixed-format class — the amount the claim asks the review team for, in USD, a positive number with 2 decimal places, rounded half up to the cent before it is passed; never 0 or negative.

    Returns:
        A dictionary rendered as text with these fields: order_review_request_id (text, the reference number
        of the new claim), order_id (text, the order concerned), line_number (integer, the line claimed),
        refund_reason (text, the reason claimed), request_type (text, always photo_review),
        requested_amount_usd (number, USD with 2 decimal places) and request_status (text, "submitted" when
        the claim now waits for the review team).
    """
    rid = ctx.make_id("orr_", customer_id, order_id, line_number, refund_reason, requested_amount_usd)
    amount = round(float(requested_amount_usd), 2)
    ctx.create("order_review_requests", rid, order_review_request_id=rid, customer_id=customer_id,
               order_id=order_id, line_number=int(line_number), request_type="photo_review",
               requested_amount_usd=amount, request_status="submitted", created_at=ctx.now())
    return str({"order_review_request_id": rid, "order_id": order_id, "line_number": int(line_number),
                "refund_reason": refund_reason, "request_type": "photo_review",
                "requested_amount_usd": amount, "request_status": "submitted"})

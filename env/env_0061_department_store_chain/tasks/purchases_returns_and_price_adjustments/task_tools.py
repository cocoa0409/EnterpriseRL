"""Hidden task tools of the purchases_returns_and_price_adjustments difficulty (Marlowe & Finch).

Every tool books one price adjustment record on one purchase record (one unit) and lowers the unit's
amount paid and not refunded by the amount booked; the refund goes to the tender the unit was paid
with, as shown on the purchase record. Tools are reached through unlock_* -> call_*.
"""

from erlbench import ToolContext, tool


@tool(owner="agent", rw="write")
def correct_shelf_price_8a80c6f7(ctx: ToolContext, purchase_id: str, new_unit_price: float, amount: float) -> str:
    """Book a shelf-price correction on one purchase record: customer care records a register-error price adjustment
    for a unit that rang up above its shelf ticket, stating the price the unit should have rung at and the amount
    refunded. On success one price adjustment entry is added to the unit's records with today's date, the reason
    register price error, the corrected price and the amount; the amount goes back to the tender the unit was paid
    with, and the unit's amount paid and not refunded goes down by the same amount. The corrected price is recorded
    only on the new price adjustment entry; the unit's selling price on the purchase record is left as rung. The
    customer sees the refund on the original tender.

    Args:
        purchase_id: Id class — the reference number of the purchase record (one unit of one item) being corrected, as returned by the purchase lookup for this customer.
        new_unit_price: Fixed-format class — the price the unit should have rung at, recorded as the new unit price on the price adjustment entry; USD, 2 decimal places, rounded half up to the cent before it is passed; never empty.
        amount: Fixed-format class — the total refunded by this correction; USD, 2 decimal places, positive, rounded half up to the cent before it is passed; never empty.

    Returns:
        A confirmation sentence (string) naming the new price adjustment reference number (an opaque text reference),
        the purchase record reference number, the corrected unit price and the amount refunded (both USD with 2
        decimal places), the tender refunded, and the unit's remaining amount paid and not refunded (USD, 2 decimal
        places). A sentence starting with "Shelf-price correction booked" means the entry was recorded.
    """
    p = ctx.find("purchases", purchase_id=purchase_id)[0]
    rid = ctx.make_id("opa_", purchase_id, new_unit_price, amount)
    ctx.create("order_events", rid, order_event_id=rid, purchase_id=purchase_id, customer_id=p["customer_id"],
               event_type="order_price_adjustment", event_date=ctx.now()[:10], amount=round(float(amount), 2),
               tender_type="not_applicable", new_unit_price=round(float(new_unit_price), 2),
               adjustment_reason="register_price_error", refund_trigger="not_applicable",
               refund_destination="not_applicable", refund_tender_type=p["tender_type"],
               restocking_fee_amount=0.0, return_fee_amount=0.0, gwp_deduction_amount=0.0)
    remaining = round(float(p["net_paid_amount"]) - float(amount), 2)
    ctx.update("purchases", purchase_id, net_paid_amount=remaining)
    return (f"Shelf-price correction booked: {rid} on purchase {purchase_id}, corrected unit price "
            f"{float(new_unit_price):.2f}, refunded {float(amount):.2f} to {p['tender_type']}; "
            f"amount paid and not refunded now {remaining:.2f}.")


@tool(owner="agent", rw="write")
def refund_registry_credit_shortfall_17a5cd98(ctx: ToolContext, purchase_id: str, amount: float) -> str:
    """Book a registry credit shortfall refund on one purchase record: customer care records a register-error price
    adjustment that returns the card money captured for the part of the unit the registrant's registry credit had
    already paid, together with any credits owed for it. On success one price adjustment entry with today's date and
    the reason register price error is added to the unit's records, with no new unit price; the amount goes back to
    the tender the unit was paid with, and the unit's amount paid and not refunded goes down by the same amount. The
    registry credit itself stays spent. The customer sees the refund on the original tender.

    Args:
        purchase_id: Id class — the reference number of the purchase record (one unit of one item) the registry credit was spent on, as returned by the purchase lookup for this customer.
        amount: Fixed-format class — the total refunded by this entry; USD, 2 decimal places, positive, rounded half up to the cent before it is passed; never empty.

    Returns:
        A confirmation sentence (string) naming the new price adjustment reference number (an opaque text reference),
        the purchase record reference number, the amount refunded (USD, 2 decimal places), the tender refunded, and the
        unit's remaining amount paid and not refunded (USD, 2 decimal places). A sentence starting with "Registry credit
        shortfall refund booked" means the entry was recorded.
    """
    p = ctx.find("purchases", purchase_id=purchase_id)[0]
    rid = ctx.make_id("opa_", purchase_id, "registry_credit", amount)
    ctx.create("order_events", rid, order_event_id=rid, purchase_id=purchase_id, customer_id=p["customer_id"],
               event_type="order_price_adjustment", event_date=ctx.now()[:10], amount=round(float(amount), 2),
               tender_type="not_applicable", adjustment_reason="register_price_error",
               refund_trigger="not_applicable", refund_destination="not_applicable",
               refund_tender_type=p["tender_type"], restocking_fee_amount=0.0, return_fee_amount=0.0,
               gwp_deduction_amount=0.0)
    remaining = round(float(p["net_paid_amount"]) - float(amount), 2)
    ctx.update("purchases", purchase_id, net_paid_amount=remaining)
    return (f"Registry credit shortfall refund booked: {rid} on purchase {purchase_id}, refunded "
            f"{float(amount):.2f} to {p['tender_type']}; amount paid and not refunded now {remaining:.2f}.")


@tool(owner="user", rw="write")
def claim_registry_price_protection_38d04d45(ctx: ToolContext, purchase_id: str, new_unit_price: float, amount: float) -> str:
    """File a registry price protection claim on one of your own purchases: you, the registrant, claim the price
    protection on an item from your own gift registry that a guest later bought at a lower price, stating that lower
    price and the protection amount the representative gave you. On success one price-drop adjustment entry with
    today's date, the lower price recorded as the new unit price on that entry and the amount is added to your purchase;
    the amount is refunded to the tender you paid with, and the purchase's amount paid and not refunded goes down by the
    same amount. The selling price on your purchase record is left as charged. You see the refund on your original
    tender.

    Args:
        purchase_id: Id class — the reference number of your purchase record (one unit of one item) the claim is for, as read to you by the representative from the purchase lookup.
        new_unit_price: Fixed-format class — the lower price the protection is based on, recorded as the new unit price on the price-drop adjustment entry; USD, 2 decimal places, rounded half up to the cent; never empty.
        amount: Fixed-format class — the protection amount refunded, as the representative gave it to you; USD, 2 decimal places, positive, rounded half up to the cent; never empty.

    Returns:
        A confirmation sentence (string) naming the new price adjustment reference number (an opaque text reference),
        the purchase record reference number, the protection lower price and the amount refunded (both USD with 2
        decimal places), the tender refunded, and the purchase's remaining amount paid and not refunded (USD, 2 decimal
        places). A sentence starting with "Registry price protection claim filed" means the claim was recorded.
    """
    p = ctx.find("purchases", purchase_id=purchase_id)[0]
    rid = ctx.make_id("opa_", purchase_id, new_unit_price, amount)
    ctx.create("order_events", rid, order_event_id=rid, purchase_id=purchase_id, customer_id=p["customer_id"],
               event_type="order_price_adjustment", event_date=ctx.now()[:10], amount=round(float(amount), 2),
               tender_type="not_applicable", new_unit_price=round(float(new_unit_price), 2),
               adjustment_reason="mf_price_drop", refund_trigger="not_applicable",
               refund_destination="not_applicable", refund_tender_type=p["tender_type"],
               restocking_fee_amount=0.0, return_fee_amount=0.0, gwp_deduction_amount=0.0)
    remaining = round(float(p["net_paid_amount"]) - float(amount), 2)
    ctx.update("purchases", purchase_id, net_paid_amount=remaining)
    return (f"Registry price protection claim filed: {rid} on purchase {purchase_id}, protection lower price "
            f"{float(new_unit_price):.2f}, refunded {float(amount):.2f} to {p['tender_type']}; "
            f"amount paid and not refunded now {remaining:.2f}.")


@tool(owner="agent", rw="write")
def refund_note_shortfall_1f084e1e(ctx: ToolContext, purchase_id: str, amount: float) -> str:
    """Book a Finch Note shortfall refund on one purchase record: customer care records a register-error price adjustment
    that returns the card money captured for the part of the unit a redeemed Finch Note had already paid, together with
    any credits owed for it. On success one price adjustment entry with today's date and the reason register price error
    is added to the unit's records, with no new unit price; the amount goes back to the tender the unit was paid with, and
    the unit's amount paid and not refunded goes down by the same amount. The note itself stays redeemed. The customer
    sees the refund on the original tender.

    Args:
        purchase_id: Id class — the reference number of the purchase record (one unit of one item) the Finch Note was redeemed on, as returned by the purchase lookup for this customer.
        amount: Fixed-format class — the total refunded by this entry; USD, 2 decimal places, positive, rounded half up to the cent before it is passed; never empty.

    Returns:
        A confirmation sentence (string) naming the new price adjustment reference number (an opaque text reference),
        the purchase record reference number, the amount refunded (USD, 2 decimal places), the tender refunded, and the
        unit's remaining amount paid and not refunded (USD, 2 decimal places). A sentence starting with "Finch Note shortfall refund booked" means
        the entry was recorded.
    """
    p = ctx.find("purchases", purchase_id=purchase_id)[0]
    rid = ctx.make_id("opa_", purchase_id, "finch_note", amount)
    ctx.create("order_events", rid, order_event_id=rid, purchase_id=purchase_id, customer_id=p["customer_id"],
               event_type="order_price_adjustment", event_date=ctx.now()[:10], amount=round(float(amount), 2),
               tender_type="not_applicable", adjustment_reason="register_price_error",
               refund_trigger="not_applicable", refund_destination="not_applicable",
               refund_tender_type=p["tender_type"], restocking_fee_amount=0.0, return_fee_amount=0.0,
               gwp_deduction_amount=0.0)
    remaining = round(float(p["net_paid_amount"]) - float(amount), 2)
    ctx.update("purchases", purchase_id, net_paid_amount=remaining)
    return (f"Finch Note shortfall refund booked: {rid} on purchase {purchase_id}, refunded "
            f"{float(amount):.2f} to {p['tender_type']}; amount paid and not refunded now {remaining:.2f}.")


@tool(owner="agent", rw="write")
def refund_note_tax_482f19cd(ctx: ToolContext, purchase_id: str, amount: float) -> str:
    """Book a Finch Note tax refund on one purchase record: customer care records a register-error price adjustment
    that returns the sales tax charged on the part of the unit a redeemed Finch Note had paid, together with any credits
    owed for it. On success one price adjustment entry with today's date and the reason register price error is added
    to the unit's records, with no new unit price; the amount goes back to the tender the unit was paid with, and the
    unit's amount paid and not refunded goes down by the same amount. The note itself is not changed. The customer sees
    the refund on the original tender.

    Args:
        purchase_id: Id class — the reference number of the purchase record (one unit of one item) the Finch Note was redeemed on, as returned by the purchase lookup for this customer.
        amount: Fixed-format class — the total refunded by this entry; USD, 2 decimal places, positive, rounded half up to the cent before it is passed; never empty.

    Returns:
        A confirmation sentence (string) naming the new price adjustment reference number (an opaque text reference),
        the purchase record reference number, the amount refunded (USD, 2 decimal places), the tender refunded, and the
        unit's remaining amount paid and not refunded (USD, 2 decimal places). A sentence starting with "Finch Note tax
        refund booked" means the entry was recorded.
    """
    p = ctx.find("purchases", purchase_id=purchase_id)[0]
    rid = ctx.make_id("opa_", purchase_id, "note_tax", amount)
    ctx.create("order_events", rid, order_event_id=rid, purchase_id=purchase_id, customer_id=p["customer_id"],
               event_type="order_price_adjustment", event_date=ctx.now()[:10], amount=round(float(amount), 2),
               tender_type="not_applicable", adjustment_reason="register_price_error",
               refund_trigger="not_applicable", refund_destination="not_applicable",
               refund_tender_type=p["tender_type"], restocking_fee_amount=0.0, return_fee_amount=0.0,
               gwp_deduction_amount=0.0)
    remaining = round(float(p["net_paid_amount"]) - float(amount), 2)
    ctx.update("purchases", purchase_id, net_paid_amount=remaining)
    return (f"Finch Note tax refund booked: {rid} on purchase {purchase_id}, refunded "
            f"{float(amount):.2f} to {p['tender_type']}; amount paid and not refunded now {remaining:.2f}.")


@tool(owner="agent", rw="write")
def refund_duplicate_capture_6e7f744e(ctx: ToolContext, purchase_id: str, amount: float) -> str:
    """Book a duplicate-capture refund on one purchase record: customer care records a register-error price adjustment
    that returns a second capture of the unit's payment, together with any credits owed for it. On success one price
    adjustment entry with today's date and the reason register price error is added to the unit's records, with no new
    unit price; the amount goes back to the tender the unit was paid with, and the unit's amount paid and not refunded
    goes down by the same amount. The payment entries themselves are left as recorded. The customer sees the refund on
    the original tender.

    Args:
        purchase_id: Id class — the reference number of the purchase record (one unit of one item) whose payment was captured twice, as returned by the purchase lookup for this customer.
        amount: Fixed-format class — the total refunded by this entry; USD, 2 decimal places, positive, rounded half up to the cent before it is passed; never empty.

    Returns:
        A confirmation sentence (string) naming the new price adjustment reference number (an opaque text reference),
        the purchase record reference number, the amount refunded (USD, 2 decimal places), the tender refunded, and the
        unit's remaining amount paid and not refunded (USD, 2 decimal places). A sentence starting with "Duplicate-capture refund booked" means
        the entry was recorded.
    """
    p = ctx.find("purchases", purchase_id=purchase_id)[0]
    rid = ctx.make_id("opa_", purchase_id, "second_capture", amount)
    ctx.create("order_events", rid, order_event_id=rid, purchase_id=purchase_id, customer_id=p["customer_id"],
               event_type="order_price_adjustment", event_date=ctx.now()[:10], amount=round(float(amount), 2),
               tender_type="not_applicable", adjustment_reason="register_price_error",
               refund_trigger="not_applicable", refund_destination="not_applicable",
               refund_tender_type=p["tender_type"], restocking_fee_amount=0.0, return_fee_amount=0.0,
               gwp_deduction_amount=0.0)
    remaining = round(float(p["net_paid_amount"]) - float(amount), 2)
    ctx.update("purchases", purchase_id, net_paid_amount=remaining)
    return (f"Duplicate-capture refund booked: {rid} on purchase {purchase_id}, refunded "
            f"{float(amount):.2f} to {p['tender_type']}; amount paid and not refunded now {remaining:.2f}.")


@tool(owner="user", rw="write")
def claim_gift_card_shortfall_5b13f7c5(ctx: ToolContext, purchase_id: str, amount: float) -> str:
    """File a gift card shortfall claim on one of your own purchases: you claim back the card money you were charged for
    the part of your purchase a Marlowe & Finch gift card or Bonus Card you used had already paid, with the amount the representative
    gave you. On success one price adjustment entry with today's date and the reason register price error is added to your
    purchase, with no new unit price; the amount is refunded to the tender you paid with, and the purchase's amount paid and
    not refunded goes down by the same amount. The card balances are not changed. You see the refund on your original
    tender.

    Args:
        purchase_id: Id class — the reference number of your purchase record (one unit of one item) the claim is for, as read to you by the representative from the purchase lookup.
        amount: Fixed-format class — the claim amount refunded, as the representative gave it to you; USD, 2 decimal places, positive, rounded half up to the cent before it is passed; never empty.

    Returns:
        A confirmation sentence (string) naming the new price adjustment reference number (an opaque text reference),
        the purchase record reference number, the amount refunded (USD, 2 decimal places), the tender refunded, and the
        unit's remaining amount paid and not refunded (USD, 2 decimal places). A sentence starting with "Gift card shortfall claim filed" means
        the entry was recorded.
    """
    p = ctx.find("purchases", purchase_id=purchase_id)[0]
    rid = ctx.make_id("opa_", purchase_id, "gift_card", amount)
    ctx.create("order_events", rid, order_event_id=rid, purchase_id=purchase_id, customer_id=p["customer_id"],
               event_type="order_price_adjustment", event_date=ctx.now()[:10], amount=round(float(amount), 2),
               tender_type="not_applicable", adjustment_reason="register_price_error",
               refund_trigger="not_applicable", refund_destination="not_applicable",
               refund_tender_type=p["tender_type"], restocking_fee_amount=0.0, return_fee_amount=0.0,
               gwp_deduction_amount=0.0)
    remaining = round(float(p["net_paid_amount"]) - float(amount), 2)
    ctx.update("purchases", purchase_id, net_paid_amount=remaining)
    return (f"Gift card shortfall claim filed: {rid} on purchase {purchase_id}, refunded "
            f"{float(amount):.2f} to {p['tender_type']}; amount paid and not refunded now {remaining:.2f}.")

"""Hidden task tools of the delivery_claims difficulty (Marlowe & Finch Delivery Claims).

Each tool performs one atomic write on the claims ledger with the value the caller has already
worked out; none of them aggregates history, computes an amount or judges eligibility.
They are reached through unlock_* -> call_* and are named by the target_tool of exactly one
extended policy in claims.extended.yaml.
"""

from erlbench import ToolContext, tool


@tool(owner="agent", rw="write")
def book_late_delivery_charge_refund_805d7478(ctx: ToolContext, claim_id: str, amount_usd: float) -> str:
    """Book the delivery-charge refund owed on a Late Delivery Claim, as one compensation entry on that claim.

    The desk uses this when a guaranteed parcel arrived later than its promised date and the claim has been
    approved: one call adds a single shipping-fee-refund compensation entry, dated today, to the claim's
    ledger for the whole parcel (no order line, no units), carrying the amount given. Nothing else on
    the claim changes: its status stays as it is. The booked entry appears among the claim's
    compensation records, where the customer's delivery-charge refund can be seen.

    Args:
        claim_id: Id class — the claim number of the Late Delivery Claim the refund is booked on, as returned by the delivery-claim lookup for the customer.
        amount_usd: Fixed-format class — the delivery-charge refund given on the claim, in USD, a positive amount rounded to 2 decimal places (to the nearest cent, on the final figure); it is stored exactly as passed.

    Returns:
        A text rendering of a dictionary with: "entry_id" (string, the reference of the new compensation entry), "claim_id" (string, the claim it was booked on), "compensation_type" (string, always "shipping_fee_refund"), "amount_usd" (number, USD with 2 decimal places, the amount booked) and "booked_on" (string, YYYY-MM-DD, today's date). Receiving this receipt means the refund entry now stands on the claim.
    """
    rid = ctx.make_id("cev_", claim_id, "shipping_fee_refund", amount_usd)
    amount = round(float(amount_usd), 2)
    today = ctx.now()[:10]
    claim_rows = ctx.find("delivery_claims", claim_id=claim_id)  # copies the claim's customer onto the entry; no check
    owner = claim_rows[0].get("customer_id") if claim_rows else ""
    ctx.create("claim_events", rid, claim_event_id=rid, claim_id=claim_id,
               customer_id=owner, event_type="claims_compensation_issued",
               event_date=today, evidence_type="not_applicable", evidence_reference="",
               booked_line_id="", compensation_type="shipping_fee_refund", quantity=0,
               amount_usd=amount, replacement_order_id="", recovery_reason="not_applicable")
    return str({"entry_id": rid, "claim_id": claim_id, "compensation_type": "shipping_fee_refund",
                "amount_usd": amount, "booked_on": today})


@tool(owner="agent", rw="write")
def book_late_delivery_goodwill_699f3402(ctx: ToolContext, claim_id: str, amount_usd: float) -> str:
    """Book the Goodwill Credit given on a Late Delivery Claim, as one compensation entry on that claim.

    The desk uses this to record, on an approved claim for a guaranteed parcel that arrived late, the
    Goodwill Credit the customer receives: one call adds a single goodwill-credit compensation entry,
    dated today, for the whole parcel (no order line, no units), carrying the credit value. The claim's
    status is not changed. The booked credit value shows among the claim's compensation records.

    Args:
        claim_id: Id class — the claim number of the Late Delivery Claim the credit is booked on, as returned by the delivery-claim lookup for the customer.
        amount_usd: Fixed-format class — the Goodwill Credit value given on the claim, in USD, a positive amount rounded to 2 decimal places (to the nearest cent, on the final figure); it is stored exactly as passed.

    Returns:
        A text rendering of a dictionary with: "entry_id" (string, the reference of the new compensation entry), "claim_id" (string, the claim it was booked on), "compensation_type" (string, always "goodwill_credit"), "amount_usd" (number, USD with 2 decimal places, the credit value booked) and "booked_on" (string, YYYY-MM-DD, today's date). Receiving this receipt means the Goodwill Credit entry now stands on the claim.
    """
    rid = ctx.make_id("cev_", claim_id, "goodwill_credit", amount_usd)
    amount = round(float(amount_usd), 2)
    today = ctx.now()[:10]
    claim_rows = ctx.find("delivery_claims", claim_id=claim_id)  # copies the claim's customer onto the entry; no check
    owner = claim_rows[0].get("customer_id") if claim_rows else ""
    ctx.create("claim_events", rid, claim_event_id=rid, claim_id=claim_id,
               customer_id=owner, event_type="claims_compensation_issued",
               event_date=today, evidence_type="not_applicable", evidence_reference="",
               booked_line_id="", compensation_type="goodwill_credit", quantity=0,
               amount_usd=amount, replacement_order_id="", recovery_reason="not_applicable")
    return str({"entry_id": rid, "claim_id": claim_id, "compensation_type": "goodwill_credit",
                "amount_usd": amount, "booked_on": today})


@tool(owner="user", rw="write")
def authorize_found_parcel_charge_f3b6f0d4(ctx: ToolContext, claim_id: str, booked_line_id: str,
                                           quantity: int, amount_usd: float) -> str:
    """Authorize, as the customer, the charge to your original card for items you keep from a parcel that was compensated as undelivered and has turned up.

    You use this yourself when a parcel you reported as not received (and were compensated for) has
    turned up and you choose to keep what was in it rather than send it back. One call records a
    single charge on your claim for one order line: the number of units you keep and the amount you
    agree to be charged, dated today, which is taken from the card you paid the order with. The claim
    itself is not otherwise changed. The recorded charge shows on the claim as value recovered for a
    found parcel kept.

    Args:
        claim_id: Id class — the claim number of your Delivered Not Received or Lost in Transit Claim, as the representative reads it to you from the claim record.
        booked_line_id: Id class — the order line reference number (the identifier of the booked order line) whose items you keep, as the representative reads it to you from the claim's compensation record.
        quantity: Fixed-format class — how many units of that line you keep, a non-negative integer units count (a whole number, at least 1).
        amount_usd: Fixed-format class — the amount you authorize to be charged, in USD, a positive amount rounded to 2 decimal places (to the nearest cent, on the final figure) as the representative states it; it is recorded on the claim as value recovered.

    Returns:
        A text rendering of a dictionary with: "charge_id" (string, the reference of the recorded charge), "claim_id" (string, your claim number), "booked_line_id" (string, the order line kept), "quantity" (integer, units kept), "amount_charged_usd" (number, USD with 2 decimal places, the amount taken from your card) and "charged_on" (string, YYYY-MM-DD, today's date). Receiving this receipt means the charge has been authorized and recorded.
    """
    rid = ctx.make_id("cev_", claim_id, "found_parcel_kept", booked_line_id, quantity, amount_usd)
    amount = round(float(amount_usd), 2)
    today = ctx.now()[:10]
    claim_rows = ctx.find("delivery_claims", claim_id=claim_id)  # copies the claim's customer onto the entry; no check
    owner = claim_rows[0].get("customer_id") if claim_rows else ""
    ctx.create("claim_events", rid, claim_event_id=rid, claim_id=claim_id,
               customer_id=owner, event_type="claims_compensation_recovered",
               event_date=today, evidence_type="not_applicable", evidence_reference="",
               booked_line_id=booked_line_id, compensation_type="not_applicable", quantity=int(quantity),
               amount_usd=-amount, replacement_order_id="", recovery_reason="found_parcel_kept")
    return str({"charge_id": rid, "claim_id": claim_id, "booked_line_id": booked_line_id,
                "quantity": int(quantity), "amount_charged_usd": amount, "charged_on": today})


@tool(owner="agent", rw="write")
def book_wrong_shipment_delivery_refund_014b5564(ctx: ToolContext, claim_id: str, amount_usd: float) -> str:
    """Book the delivery-charge refund owed on a Wrong Item Claim, as one compensation entry on that claim.

    The desk uses this when the parcel of an order brought the wrong items and the approved Wrong Item
    Claim owes back part or all of the delivery charge: one call adds a single shipping-fee-refund
    compensation entry, dated today, to the claim's ledger for the whole parcel (no order line, no
    units), carrying the amount given. The claim's status is not changed. The booked entry appears
    among the claim's compensation records next to its merchandise refunds.

    Args:
        claim_id: Id class — the claim number of the Wrong Item Claim the refund is booked on, as returned by the delivery-claim lookup for the customer.
        amount_usd: Fixed-format class — the delivery-charge refund given on the claim, in USD, a positive amount rounded to 2 decimal places (to the nearest cent, on the final figure); it is stored exactly as passed.

    Returns:
        A text rendering of a dictionary with: "entry_id" (string, the reference of the new compensation entry), "claim_id" (string, the claim it was booked on), "compensation_type" (string, always "shipping_fee_refund"), "amount_usd" (number, USD with 2 decimal places, the amount booked) and "booked_on" (string, YYYY-MM-DD, today's date). Receiving this receipt means the refund entry now stands on the claim.
    """
    rid = ctx.make_id("cev_", claim_id, "wrong_shipment_delivery", amount_usd)
    amount = round(float(amount_usd), 2)
    today = ctx.now()[:10]
    claim_rows = ctx.find("delivery_claims", claim_id=claim_id)  # copies the claim's customer onto the entry; no check
    owner = claim_rows[0].get("customer_id") if claim_rows else ""
    ctx.create("claim_events", rid, claim_event_id=rid, claim_id=claim_id,
               customer_id=owner, event_type="claims_compensation_issued",
               event_date=today, evidence_type="not_applicable", evidence_reference="",
               booked_line_id="", compensation_type="shipping_fee_refund", quantity=0,
               amount_usd=amount, replacement_order_id="", recovery_reason="not_applicable")
    return str({"entry_id": rid, "claim_id": claim_id, "compensation_type": "shipping_fee_refund",
                "amount_usd": amount, "booked_on": today})


@tool(owner="agent", rw="write")
def book_undelivered_parcel_delivery_refund_8864d5c2(ctx: ToolContext, claim_id: str, amount_usd: float) -> str:
    """Book the delivery-charge refund owed on a Delivered Not Received or Lost in Transit Claim, as one compensation entry on that claim.

    The desk uses this for a parcel that never reached the customer, on an approved claim whose merchandise
    is refunded or reshipped: one call adds a single shipping-fee-refund compensation entry, dated
    today, for the whole parcel (no order line, no units), carrying the amount given. The claim's
    status is not changed. The booked entry appears among the claim's compensation records.

    Args:
        claim_id: Id class — the claim number of the Delivered Not Received or Lost in Transit Claim the refund is booked on, as returned by the delivery-claim lookup for the customer.
        amount_usd: Fixed-format class — the delivery-charge refund given on the claim, in USD, a positive amount rounded to 2 decimal places (to the nearest cent, on the final figure); it is stored exactly as passed.

    Returns:
        A text rendering of a dictionary with: "entry_id" (string, the reference of the new compensation entry), "claim_id" (string, the claim it was booked on), "compensation_type" (string, always "shipping_fee_refund"), "amount_usd" (number, USD with 2 decimal places, the amount booked) and "booked_on" (string, YYYY-MM-DD, today's date). Receiving this receipt means the refund entry now stands on the claim.
    """
    rid = ctx.make_id("cev_", claim_id, "undelivered_parcel_delivery", amount_usd)
    amount = round(float(amount_usd), 2)
    today = ctx.now()[:10]
    claim_rows = ctx.find("delivery_claims", claim_id=claim_id)  # copies the claim's customer onto the entry; no check
    owner = claim_rows[0].get("customer_id") if claim_rows else ""
    ctx.create("claim_events", rid, claim_event_id=rid, claim_id=claim_id,
               customer_id=owner, event_type="claims_compensation_issued",
               event_date=today, evidence_type="not_applicable", evidence_reference="",
               booked_line_id="", compensation_type="shipping_fee_refund", quantity=0,
               amount_usd=amount, replacement_order_id="", recovery_reason="not_applicable")
    return str({"entry_id": rid, "claim_id": claim_id, "compensation_type": "shipping_fee_refund",
                "amount_usd": amount, "booked_on": today})


@tool(owner="user", rw="write")
def authorize_wrong_item_keep_charge_d92bb3d2(ctx: ToolContext, claim_id: str, booked_line_id: str,
                                              quantity: int, amount_usd: float) -> str:
    """Authorize, as the customer, the charge to your original card for a wrong item you received and choose to keep instead of sending it back.

    You use this yourself when a parcel brought you an item other than the one you ordered, your Wrong
    Item Claim has been approved, and you would rather keep the item you received than return it with
    the prepaid label. One call records a single charge on your claim for the order line the wrong item
    came in place of: the number of units you keep and the amount you agree to be charged, dated today,
    taken from the card you paid the order with. The claim is not otherwise changed. The recorded charge
    shows on the claim as value recovered for a wrong item kept.

    Args:
        claim_id: Id class — the claim number of your Wrong Item Claim, as the representative reads it to you from the claim record.
        booked_line_id: Id class — the order line reference number (the identifier of the booked order line) the wrong item came in place of, as the representative reads it to you from the claim record.
        quantity: Fixed-format class — how many units you keep, a non-negative integer units count (a whole number, at least 1).
        amount_usd: Fixed-format class — the amount you authorize to be charged, in USD, a positive amount rounded to 2 decimal places (to the nearest cent, on the final figure) as the representative states it; it is recorded on the claim as value recovered.

    Returns:
        A text rendering of a dictionary with: "charge_id" (string, the reference of the recorded charge), "claim_id" (string, your claim number), "booked_line_id" (string, the order line concerned), "quantity" (integer, units kept), "amount_charged_usd" (number, USD with 2 decimal places, the amount taken from your card) and "charged_on" (string, YYYY-MM-DD, today's date). Receiving this receipt means the charge has been authorized and recorded.
    """
    rid = ctx.make_id("cev_", claim_id, "wrong_item_kept", booked_line_id, quantity, amount_usd)
    amount = round(float(amount_usd), 2)
    today = ctx.now()[:10]
    claim_rows = ctx.find("delivery_claims", claim_id=claim_id)  # copies the claim's customer onto the entry; no check
    owner = claim_rows[0].get("customer_id") if claim_rows else ""
    ctx.create("claim_events", rid, claim_event_id=rid, claim_id=claim_id,
               customer_id=owner, event_type="claims_compensation_recovered",
               event_date=today, evidence_type="not_applicable", evidence_reference="",
               booked_line_id=booked_line_id, compensation_type="not_applicable", quantity=int(quantity),
               amount_usd=-amount, replacement_order_id="", recovery_reason="wrong_item_not_returned")
    return str({"charge_id": rid, "claim_id": claim_id, "booked_line_id": booked_line_id,
                "quantity": int(quantity), "amount_charged_usd": amount, "charged_on": today})

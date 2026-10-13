"""Hidden task tools for the pharmacy_prescription_care difficulty of env_0040_pet_supplies_retailer.

Each tool performs one atomic pharmacy write with the values the agent (or, for a customer's own
write, the customer at the agent's hand-over) has already worked out. No tool checks a business
precondition, aggregates history or computes a policy value; every judgement belongs to the caller.
"""

from erlbench import ToolContext, tool


@tool(owner="agent", rw="write")
def refund_dispensing_error_93fa9db7(ctx: ToolContext, rx_prescription_id: str, original_event_id: str,
                                     error_type: str, amount_usd: float) -> dict:
    """Refund a dispensed pharmacy fill that carries a confirmed dispensing error, to the customer's
    original payment, and credit that fill back to the prescription. One call books a refund entry
    against the named fill on the prescription's pharmacy ledger (the refunded amount, the error
    being remedied, refund to the original payment, dated today), books a matching credit-back entry
    for the same fill carrying that fill's days' supply, and raises the prescription's fills still available by one. On success the
    pharmacy ledger of the prescription shows both entries and the prescription shows one more fill
    available; the refund is on its way to the card or account the fill was paid with.

    Args:
        rx_prescription_id: Id class — the prescription reference number the erroneous fill belongs to, as returned by the prescription lookup for the customer.
        original_event_id: Id class — the pharmacy ledger reference number of the dispensed fill being refunded, as returned by the pharmacy ledger lookup for that prescription.
        error_type: Enum class — the dispensing error this refund remedies, exactly one of: wrong_medication when a different medication or diet was dispensed than the one prescribed; wrong_strength when the right medication was dispensed at a strength or formula other than the prescribed one; wrong_quantity when the number of packages dispensed differs from the packages billed for the fill; wrong_label when the product was right but its label carries wrong information; none when the fill carries no dispensing error at all, which never describes a refund and is listed only to complete the closed set.
        amount_usd: Fixed-format class — the total amount refunded to the original payment for this fill, in USD, a positive number with 2 decimal places, rounded half up to the cent.

    Returns:
        dict with refund_event_id (str, reference number of the refund entry on the pharmacy ledger),
        credit_event_id (str, reference number of the fill credit-back entry), original_event_id (str,
        the refunded fill), amount_usd (float, USD with 2 decimal places, the amount refunded),
        refund_method (str, always original_payment), fills_remaining (int, the prescription's fills
        still available including the credit-back) and status (str, refunded when the entries are booked).
    """
    amount = round(float(amount_usd), 2)
    today = ctx.now()[:10]
    rx = (ctx.find("rx_prescriptions", rx_prescription_id=rx_prescription_id) or [{}])[0]
    customer_id = rx.get("customer_id")
    fills_after = int(rx.get("fills_remaining") or 0) + 1
    fill = (ctx.find("rx_events", rx_event_id=original_event_id) or [{}])[0]
    rid = ctx.make_id("rxr_", rx_prescription_id, original_event_id, error_type, amount)
    ctx.create("rx_events", rid, rx_event_id=rid, rx_prescription_id=rx_prescription_id, customer_id=customer_id,
               event_type="rx_error_refund", event_date=today, fill_number=0, fill_channel="none",
               amount_usd=amount, override_reason="none", original_event_id=original_event_id,
               error_type=error_type, refund_method="original_payment")
    cid = ctx.make_id("rxc_", rx_prescription_id, original_event_id)
    ctx.create("rx_events", cid, rx_event_id=cid, rx_prescription_id=rx_prescription_id, customer_id=customer_id,
               event_type="rx_fill_restore", event_date=today, fill_number=0, fill_channel="none",
               fills_remaining_after=fills_after, days_supply=fill.get("days_supply"), override_reason="none",
               original_event_id=original_event_id,
               error_type="none", refund_method="none")
    ctx.update("rx_prescriptions", rx_prescription_id, fills_remaining=fills_after)
    return {"refund_event_id": rid, "credit_event_id": cid, "original_event_id": original_event_id,
            "amount_usd": amount, "refund_method": "original_payment", "fills_remaining": fills_after,
            "status": "refunded"}


@tool(owner="user", rw="write")
def place_rx_renewal_order_580a75e8(ctx: ToolContext, customer_id: str, pet_id: str, vet_id: str,
                                    medication: str, strength: str, renewal_of_rx_id: str,
                                    days_supply_per_fill: int, quantity_per_fill: int) -> dict:
    """The customer places, in person, a renewal order for a pet's prescription that can no longer be
    filled. One call opens a new prescription for the same pet, medication and strength, marked as the
    renewal of the prescription being renewed and waiting for the veterinarian's authorization, carrying the
    renewed prescription's class, package item number and current package price together with the
    days' supply per fill and the packages per fill given here, ordered today. On success the customer
    can see the new prescription in status pending_vet_authorization with no fills authorized yet;
    the renewed prescription is left exactly as it was.

    Args:
        customer_id: Id class — the customer reference number of the prescription owner, as returned by the customer lookup.
        pet_id: Id class — the pet profile reference number of the patient, as returned by the pet lookup and shown on the renewed prescription.
        vet_id: Id class — the reference number of the veterinarian the renewal is addressed to, as shown on the renewed prescription and returned by the veterinarian lookup.
        medication: Verbatim class — the medication name exactly as written on the renewed prescription returned by the prescription lookup, copied character for character with no change of wording, spelling or punctuation (verbatim).
        strength: Verbatim class — the strength exactly as written on the renewed prescription returned by the prescription lookup, copied character for character with digits, units and punctuation unchanged (verbatim).
        renewal_of_rx_id: Id class — the prescription reference number of the renewed prescription being renewed, as returned by the prescription lookup.
        days_supply_per_fill: Fixed-format class — the days' supply each fill of the renewal is to contain, an integer number of days, at least 1.
        quantity_per_fill: Fixed-format class — the packages dispensed in each fill of the renewal, an integer number of packages, at least 1.

    Returns:
        dict with rx_prescription_id (str, reference number of the new renewal prescription),
        renewal_of_rx_id (str, the renewed prescription), medication (str), strength (str),
        days_supply_per_fill (int, days), quantity_per_fill (int, packages), ordered_on (str,
        YYYY-MM-DD, today) and status (str, pending_vet_authorization once the order is placed).
    """
    old = (ctx.find("rx_prescriptions", rx_prescription_id=renewal_of_rx_id) or [{}])[0]
    today = ctx.now()[:10]
    days = int(days_supply_per_fill)
    qty = int(quantity_per_fill)
    rid = ctx.make_id("rxn_", customer_id, pet_id, vet_id, medication, strength, renewal_of_rx_id, days, qty)
    ctx.create("rx_prescriptions", rid, rx_prescription_id=rid, customer_id=customer_id, pet_id=pet_id,
               vet_id=vet_id, variant_name=old.get("variant_name"), status="pending_vet_authorization",
               medication=medication, strength=strength, sku=old.get("sku"),
               unit_price_usd=old.get("unit_price_usd"), quantity_per_fill=qty, days_supply_per_fill=days,
               origin="renewal", renewal_of_rx_id=renewal_of_rx_id, transfer_count=0, ordered_on=today,
               authorized_on=None, expires_on=None, fills_authorized=0, fills_remaining=0,
               denial_reason="none", closed_on=None)
    return {"rx_prescription_id": rid, "renewal_of_rx_id": renewal_of_rx_id, "medication": medication,
            "strength": strength, "days_supply_per_fill": days, "quantity_per_fill": qty,
            "ordered_on": today, "status": "pending_vet_authorization"}


@tool(owner="agent", rw="write")
def place_pharmacy_renewal_864ea03f(ctx: ToolContext, customer_id: str, pet_id: str, vet_id: str, medication: str,
                                    strength: str, renewal_of_rx_id: str, days_supply_per_fill: int) -> dict:
    """The pharmacy places its own renewal for a pet's prescription whose class it renews by itself and
    sends the renewal request to the veterinarian. One call opens a new prescription for the same pet,
    medication and strength, marked as the renewal of the prescription being renewed and waiting for the
    veterinarian's authorization, carrying that prescription's class, package item number, current
    package price and packages per fill, the days' supply per fill given here, and today as its order
    date; the same call records, against the prescription being renewed, a renewal request sent today
    to the named veterinarian by e-authorization as attempt 1, awaiting the answer. On success the new
    prescription shows in status pending_vet_authorization with no fills authorized yet, the prescription
    being renewed shows a pending renewal request, and its own status and fills are left as they were.

    Args:
        customer_id: Id class — the customer reference number of the prescription owner, as returned by the customer lookup.
        pet_id: Id class — the pet profile reference number of the patient, as shown on the prescription being renewed and returned by the pet lookup.
        vet_id: Id class — the reference number of the veterinarian the renewal is addressed to, as shown on the prescription being renewed and returned by the veterinarian lookup.
        medication: Verbatim class — the medication or diet name exactly as written on the prescription being renewed, as returned by the prescription lookup, copied character for character (verbatim).
        strength: Verbatim class — the strength or formula exactly as written on the prescription being renewed, as returned by the prescription lookup, copied character for character with digits and units unchanged (verbatim).
        renewal_of_rx_id: Id class — the prescription reference number of the prescription being renewed, as returned by the prescription lookup.
        days_supply_per_fill: Fixed-format class — the days' supply each fill of the renewal is to contain, an integer number of days, at least 1.

    Returns:
        dict with rx_prescription_id (str, reference number of the new renewal prescription),
        renewal_of_rx_id (str, the prescription renewed), auth_request_id (str, reference number of the
        renewal request sent to the veterinarian), days_supply_per_fill (int, days), quantity_per_fill
        (int, packages, as on the prescription renewed), ordered_on (str, YYYY-MM-DD, today) and status
        (str, pending_vet_authorization once the renewal is placed).
    """
    old = (ctx.find("rx_prescriptions", rx_prescription_id=renewal_of_rx_id) or [{}])[0]
    today = ctx.now()[:10]
    days = int(days_supply_per_fill)
    rid = ctx.make_id("rxp_", customer_id, pet_id, vet_id, medication, strength, renewal_of_rx_id, days)
    ctx.create("rx_prescriptions", rid, rx_prescription_id=rid, customer_id=customer_id, pet_id=pet_id,
               vet_id=vet_id, variant_name=old.get("variant_name"), status="pending_vet_authorization",
               medication=medication, strength=strength, sku=old.get("sku"),
               unit_price_usd=old.get("unit_price_usd"), quantity_per_fill=old.get("quantity_per_fill"),
               days_supply_per_fill=days, origin="renewal", renewal_of_rx_id=renewal_of_rx_id, transfer_count=0,
               ordered_on=today, authorized_on=None, expires_on=None, fills_authorized=0, fills_remaining=0,
               denial_reason="none", closed_on=None)
    aid = ctx.make_id("rxa_", renewal_of_rx_id, vet_id, today)
    ctx.create("rx_authorization_requests", aid, auth_request_id=aid, customer_id=customer_id,
               rx_prescription_id=renewal_of_rx_id, vet_id=vet_id, request_kind="renewal", channel="e_authorization",
               attempt_number=1, requested_on=today, outcome="pending", responded_on=None)
    return {"rx_prescription_id": rid, "renewal_of_rx_id": renewal_of_rx_id, "auth_request_id": aid,
            "days_supply_per_fill": days,
            "quantity_per_fill": old.get("quantity_per_fill"), "ordered_on": today,
            "status": "pending_vet_authorization"}


@tool(owner="user", rw="write")
def place_rx_new_order_4605ac63(ctx: ToolContext, customer_id: str, pet_id: str, vet_id: str, medication: str,
                                strength: str, ships_with_rx_id: str, days_supply_per_fill: int) -> dict:
    """The customer places, in person, a new prescription order for a pet, for a medication or diet that
    another of the customer's prescriptions already carries in the same package. One call opens a new
    prescription for the named pet, medication and strength, sent to the named veterinarian as a new
    order and waiting for that veterinarian's authorization; it carries the class, package item number,
    current package price and packages per fill of the named companion prescription, the days' supply per
    fill given here, and today as its order date. On success the customer can see the new prescription in
    status pending_vet_authorization with no fills authorized yet; the companion prescription is not
    changed.

    Args:
        customer_id: Id class — the customer reference number of the prescription owner, as returned by the customer lookup.
        pet_id: Id class — the pet profile reference number of the pet the new order is for, as returned by the pet lookup.
        vet_id: Id class — the reference number of the veterinarian who prescribed for this pet and receives the new order, as returned by the pet or veterinarian lookup.
        medication: Verbatim class — the medication or diet name exactly as written on the companion prescription returned by the prescription lookup, copied character for character (verbatim).
        strength: Verbatim class — the strength or formula exactly as written on the companion prescription returned by the prescription lookup, copied character for character with digits and units unchanged (verbatim).
        ships_with_rx_id: Id class — the prescription reference number of the companion prescription whose package the new order uses, as returned by the prescription lookup.
        days_supply_per_fill: Fixed-format class — the days' supply each fill of the new order is to contain, an integer number of days, at least 1.

    Returns:
        dict with rx_prescription_id (str, reference number of the new prescription), pet_id (str),
        medication (str), strength (str), days_supply_per_fill (int, days), quantity_per_fill (int,
        packages), ordered_on (str, YYYY-MM-DD, today) and status (str, pending_vet_authorization once the
        order is placed).
    """
    mate = (ctx.find("rx_prescriptions", rx_prescription_id=ships_with_rx_id) or [{}])[0]
    today = ctx.now()[:10]
    days = int(days_supply_per_fill)
    rid = ctx.make_id("rxo_", customer_id, pet_id, vet_id, medication, strength, ships_with_rx_id, days)
    ctx.create("rx_prescriptions", rid, rx_prescription_id=rid, customer_id=customer_id, pet_id=pet_id,
               vet_id=vet_id, variant_name=mate.get("variant_name"), status="pending_vet_authorization",
               medication=medication, strength=strength, sku=mate.get("sku"),
               unit_price_usd=mate.get("unit_price_usd"), quantity_per_fill=mate.get("quantity_per_fill"),
               days_supply_per_fill=days, origin="new_from_vet", renewal_of_rx_id=None, transfer_count=0,
               ordered_on=today, authorized_on=None, expires_on=None, fills_authorized=0, fills_remaining=0,
               denial_reason="none", closed_on=None)
    return {"rx_prescription_id": rid, "pet_id": pet_id, "medication": medication, "strength": strength,
            "days_supply_per_fill": days, "quantity_per_fill": mate.get("quantity_per_fill"),
            "ordered_on": today, "status": "pending_vet_authorization"}

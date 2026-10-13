"""Hidden task tools of the preorders_and_backorders difficulty (Marlowe & Finch Pre-Orders & Back-Orders).

Each tool performs one atomic business write on a reservation; it never judges eligibility,
never checks a prerequisite and never computes an amount or a date for the caller. Every amount
and date it records is passed in by the caller exactly as the published pre-order policies fix it.
"""

from erlbench import ToolContext, tool


@tool(owner="user", rw="write")
def confirm_made_to_order_cancellation_940e1e7b(ctx: ToolContext, reservation_id: str, reservation_request_id: str,
                                                work_charge_usd: float, deposit_refund_usd: float) -> str:
    """The customer personally confirms the cancellation of their own Made-to-Order Reservation whose
    production has already started, and with that confirmation settles its deposit. One call cancels the
    reservation at the customer's request (dated today) and books two deposit entries on it: the work
    charge Marlowe & Finch keeps from the deposit, and the refund of the rest of the deposit to the card
    the deposit was charged to. The customer's pending cancellation request for that reservation is marked
    as confirmed at the same time. Afterwards the reservation shows as cancelled for reason
    customer_request, the request shows as confirmed, and the reservation history shows the amount kept
    and the amount refunded.

    Args:
        reservation_id: Id class — the reservation number of the made-to-order pair being cancelled, as shown on the customer's reservation record returned by the reservation lookup.
        reservation_request_id: Id class — the request number identifying the customer's pending cancellation request for that pair, as returned by the reservation request lookup.
        work_charge_usd: Fixed-format class — the part of the deposit kept as the work charge, in USD, a non-negative amount with 2 decimal places (cents), already rounded half up to the cent; recorded on the history as a negative deposit entry; pass 0.00 when nothing is kept.
        deposit_refund_usd: Fixed-format class — the part of the deposit refunded to the original card, in USD, a non-negative amount with 2 decimal places (cents), already rounded half up to the cent; recorded on the history as a negative deposit entry; pass 0.00 when nothing is refunded.

    Returns:
        A dict confirming the settlement: reservation_id (the reservation number, text), status (always
        "cancelled"), cancelled_date (today, YYYY-MM-DD), cancel_reason (always "customer_request"),
        reservation_request_id (the request reference, text), request_status (always "confirmed"),
        work_charge_entry_id (reference of the amount-kept entry, text), work_charge_usd (amount kept,
        USD with 2 decimal places), refund_entry_id (reference of the refund entry, text) and
        deposit_refund_usd (amount refunded, USD with 2 decimal places). A returned dict with status
        "cancelled" means the cancellation and both entries were recorded.
    """
    today = ctx.now()[:10]
    owner = (ctx.find("reservations", reservation_id=reservation_id) or [{}])[0].get("customer_id", "")
    kept = round(float(work_charge_usd), 2)
    back = round(float(deposit_refund_usd), 2)
    ctx.update("reservation_requests", reservation_request_id, request_status="confirmed")
    ctx.update("reservations", reservation_id, status="cancelled", cancelled_date=today,
               cancel_reason="customer_request")
    fid = ctx.make_id("rev_", reservation_id, reservation_request_id, "forfeit", kept, back)
    ctx.create("reservation_events", fid, reservation_event_id=fid, reservation_id=reservation_id,
               customer_id=owner,
               event_type="preorders_deposit_forfeited", event_date=today, amount_usd=round(-kept, 2),
               tender_type="not_applicable", refund_reason="customer_request", fulfilment_order_id=None,
               notice_number=0, revised_ship_by_date="", consent_mode="not_applicable",
               auth_amount_usd=0.00, auth_outcome="not_applicable")
    rid = ctx.make_id("rev_", reservation_id, reservation_request_id, "refund", kept, back)
    ctx.create("reservation_events", rid, reservation_event_id=rid, reservation_id=reservation_id,
               customer_id=owner,
               event_type="preorders_deposit_refunded", event_date=today, amount_usd=round(-back, 2),
               tender_type="not_applicable", refund_reason="customer_request", fulfilment_order_id=None,
               notice_number=0, revised_ship_by_date="", consent_mode="not_applicable",
               auth_amount_usd=0.00, auth_outcome="not_applicable")
    return str({"reservation_id": reservation_id, "status": "cancelled", "cancelled_date": today,
                "cancel_reason": "customer_request", "reservation_request_id": reservation_request_id,
                "request_status": "confirmed", "work_charge_entry_id": fid, "work_charge_usd": kept,
                "refund_entry_id": rid, "deposit_refund_usd": back})


@tool(owner="agent", rw="write")
def take_made_to_order_remake_13bceb2b(ctx: ToolContext, remade_reservation_id: str, size: str,
                                       personalization_text: str, deposit_required_usd: float,
                                       original_ship_by_date: str) -> str:
    """Takes a new Made-to-Order Reservation that remakes a made-to-order pair the customer has cancelled,
    and charges its deposit to the card on the customer's account. The new reservation is for the same
    customer, style, colour, product name and reserved unit price as the cancelled pair, for one unit, in
    the size and with the personalisation given in the call; its SKU is the cancelled pair's style and
    colour followed by the new size code (the US size times ten). It is created in status reserved, dated
    today at the current Eastern Time, with the ship-by date given as both its original and its current
    ship-by date, no delay notices, no size changes and specifications not yet confirmed, and the deposit
    charge is booked on its history. Afterwards the customer has a new reservation number showing the
    size, personalisation, price and deposit recorded.

    Args:
        remade_reservation_id: Id class — the reservation number of the cancelled made-to-order pair being remade, as returned by the reservation lookup.
        size: Verbatim class — the US size the customer states for the new pair, copied exactly as the customer says it, for example "US 9" (verbatim).
        personalization_text: Verbatim class — the personalisation exactly as the customer gives it for the new pair, preserving letters, spaces and punctuation; "" when the customer wants none (verbatim).
        deposit_required_usd: Fixed-format class — the deposit charged to the card at reservation, in USD with 2 decimal places, already rounded half up to the cent.
        original_ship_by_date: Fixed-format class — the promised ship-by date of the new pair, YYYY-MM-DD, an Eastern Time calendar date.

    Returns:
        A dict confirming the new reservation: reservation_id (the new reservation number, text), status
        (always "reserved"), reserved_date (today, YYYY-MM-DD), sku (text, MF-######-CCC-SS), size (as
        recorded), unit_price_usd (USD, 2 decimal places), deposit_required_usd (USD, 2 decimal places),
        original_ship_by_date (YYYY-MM-DD), personalization_text (as recorded) and deposit_entry_id
        (reference of the deposit charge entry, text). A returned dict with status "reserved" means the
        reservation and its deposit charge were recorded.
    """
    old = (ctx.find("reservations", reservation_id=remade_reservation_id) or [{}])[0]
    now = ctx.now()
    today = now[:10]
    deposit = round(float(deposit_required_usd), 2)
    size_code = f"{int(round(float(str(size).split()[-1]) * 10)):02d}"
    sku = "-".join(str(old.get("sku", "")).split("-")[:3] + [size_code])
    customer_id = old.get("customer_id", "")
    price = round(float(old.get("unit_price_usd") or 0), 2)
    nid = ctx.make_id("res_", remade_reservation_id, size, personalization_text, deposit, original_ship_by_date)
    ctx.create("reservations", nid, reservation_id=nid, customer_id=customer_id,
               variant_name="Made-to-Order Reservation", status="reserved", reserved_date=today,
               reserved_time_et=now[11:16], sku=sku, style_code=old.get("style_code", ""),
               style_name=old.get("style_name", ""), size=size, quantity=1, unit_price_usd=price,
               deposit_required_usd=deposit, original_ship_by_date=original_ship_by_date,
               current_ship_by_date=original_ship_by_date, delay_notice_count=0, consent_deadline_date="",
               personalization_text=personalization_text, specs_confirmed_date="", size_changes_used=0,
               production_start_date="", allocated_date="", fulfilled_date="", fulfilment_order_id=None,
               cancelled_date="", cancel_reason="none")
    did = ctx.make_id("rev_", nid, "captured", deposit)
    ctx.create("reservation_events", did, reservation_event_id=did, reservation_id=nid, customer_id=customer_id,
               event_type="preorders_deposit_captured", event_date=today, amount_usd=deposit,
               tender_type="card_or_wallet", refund_reason="not_applicable", fulfilment_order_id=None,
               notice_number=0, revised_ship_by_date="", consent_mode="not_applicable",
               auth_amount_usd=0.00, auth_outcome="not_applicable")
    return str({"reservation_id": nid, "status": "reserved", "reserved_date": today, "sku": sku, "size": size,
                "unit_price_usd": price, "deposit_required_usd": deposit,
                "original_ship_by_date": original_ship_by_date, "personalization_text": personalization_text,
                "deposit_entry_id": did})


@tool(owner="agent", rw="write")
def lower_reserved_price_a108b215(ctx: ToolContext, reservation_id: str, new_unit_price_usd: float) -> str:
    """Lowers the reserved unit price of one open reservation under price protection. One call sets the
    reservation's reserved unit price to the amount given; nothing else on the reservation changes and no
    money moves. Afterwards the reservation shows the new reserved unit price.

    Args:
        reservation_id: Id class — the reservation number whose reserved price is lowered, as returned by the reservation lookup.
        new_unit_price_usd: Fixed-format class — the new reserved price per unit, in USD with 2 decimal places, already rounded half up to the cent.

    Returns:
        A dict confirming the change: reservation_id (the reservation number, text), previous_unit_price_usd
        (the price before the change, USD with 2 decimal places) and unit_price_usd (the reserved unit
        price now recorded, USD with 2 decimal places). A returned dict whose unit_price_usd equals the
        amount given means the price was lowered.
    """
    before = (ctx.find("reservations", reservation_id=reservation_id) or [{}])[0].get("unit_price_usd")
    price = round(float(new_unit_price_usd), 2)
    ctx.update("reservations", reservation_id, unit_price_usd=price)
    return str({"reservation_id": reservation_id, "previous_unit_price_usd": before, "unit_price_usd": price})


@tool(owner="user", rw="write")
def confirm_preorder_cancellation_aa3f8734(ctx: ToolContext, reservation_id: str, cancellation_charge_usd: float,
                                           deposit_refund_usd: float) -> str:
    """The customer personally confirms the cancellation of their own Deposit Pre-Order that has not
    been allocated, and with that confirmation settles its deposit. One call cancels the reservation at
    the customer's request (dated today) and books two deposit entries on it: the cancellation charge
    Marlowe & Finch keeps from the deposit, and the refund of the rest of the deposit to the card the
    deposit was charged to. Afterwards the reservation shows as cancelled for reason customer_request and
    its history shows the amount kept and the amount refunded.

    Args:
        reservation_id: Id class — the reservation number of the Deposit Pre-Order being cancelled, as returned by the reservation lookup.
        cancellation_charge_usd: Fixed-format class — the part of the deposit kept as the cancellation charge, in USD, a non-negative amount with 2 decimal places, already rounded half up to the cent; recorded on the history as a negative deposit entry; pass 0.00 when nothing is kept.
        deposit_refund_usd: Fixed-format class — the part of the deposit refunded to the original card, in USD, a non-negative amount with 2 decimal places, already rounded half up to the cent; recorded on the history as a negative deposit entry; pass 0.00 when nothing is refunded.

    Returns:
        A dict confirming the settlement: reservation_id (the reservation number, text), status (always
        "cancelled"), cancelled_date (today, YYYY-MM-DD), cancel_reason (always "customer_request"),
        charge_entry_id (reference of the amount-kept entry, text), cancellation_charge_usd (amount kept,
        USD with 2 decimal places), refund_entry_id (reference of the refund entry, text) and
        deposit_refund_usd (amount refunded, USD with 2 decimal places). A returned dict with status
        "cancelled" means the cancellation and both entries were recorded.
    """
    today = ctx.now()[:10]
    owner = (ctx.find("reservations", reservation_id=reservation_id) or [{}])[0].get("customer_id", "")
    kept = round(float(cancellation_charge_usd), 2)
    back = round(float(deposit_refund_usd), 2)
    ctx.update("reservations", reservation_id, status="cancelled", cancelled_date=today, cancel_reason="customer_request")
    fid = ctx.make_id("rev_", reservation_id, "charge", kept, back)
    ctx.create("reservation_events", fid, reservation_event_id=fid, reservation_id=reservation_id, customer_id=owner,
               event_type="preorders_deposit_forfeited", event_date=today, amount_usd=round(-kept, 2),
               tender_type="not_applicable", refund_reason="customer_request", fulfilment_order_id=None,
               notice_number=0, revised_ship_by_date="", consent_mode="not_applicable",
               auth_amount_usd=0.00, auth_outcome="not_applicable")
    rid = ctx.make_id("rev_", reservation_id, "refund", kept, back)
    ctx.create("reservation_events", rid, reservation_event_id=rid, reservation_id=reservation_id, customer_id=owner,
               event_type="preorders_deposit_refunded", event_date=today, amount_usd=round(-back, 2),
               tender_type="not_applicable", refund_reason="customer_request", fulfilment_order_id=None,
               notice_number=0, revised_ship_by_date="", consent_mode="not_applicable",
               auth_amount_usd=0.00, auth_outcome="not_applicable")
    return str({"reservation_id": reservation_id, "status": "cancelled", "cancelled_date": today,
                "cancel_reason": "customer_request", "charge_entry_id": fid, "cancellation_charge_usd": kept,
                "refund_entry_id": rid, "deposit_refund_usd": back})


@tool(owner="user", rw="write")
def pay_reservation_deposit_93996964(ctx: ToolContext, reservation_id: str, deposit_usd: float) -> str:
    """The customer personally pays the deposit of one of their own reservations whose deposit has not
    been charged, using a card of their choice. One call records the amount paid as the reservation's
    deposit due and books the deposit charge on its history, dated today. Afterwards the reservation
    shows its deposit due and a deposit charged for that amount.

    Args:
        reservation_id: Id class — the reservation number whose deposit is paid, as returned by the reservation lookup.
        deposit_usd: Fixed-format class — the deposit paid, in USD, a positive amount with 2 decimal places, already rounded half up to the cent.

    Returns:
        A dict confirming the payment: reservation_id (the reservation number, text),
        deposit_required_usd (the deposit now recorded as due, USD with 2 decimal places), deposit_entry_id
        (reference of the deposit charge entry, text) and paid_date (today, YYYY-MM-DD). A returned dict
        with a deposit_entry_id means the deposit was charged.
    """
    today = ctx.now()[:10]
    owner = (ctx.find("reservations", reservation_id=reservation_id) or [{}])[0].get("customer_id", "")
    paid = round(float(deposit_usd), 2)
    ctx.update("reservations", reservation_id, deposit_required_usd=paid)
    did = ctx.make_id("rev_", reservation_id, "captured", paid)
    ctx.create("reservation_events", did, reservation_event_id=did, reservation_id=reservation_id, customer_id=owner,
               event_type="preorders_deposit_captured", event_date=today, amount_usd=paid,
               tender_type="card_or_wallet", refund_reason="not_applicable", fulfilment_order_id=None,
               notice_number=0, revised_ship_by_date="", consent_mode="not_applicable",
               auth_amount_usd=0.00, auth_outcome="not_applicable")
    return str({"reservation_id": reservation_id, "deposit_required_usd": paid, "deposit_entry_id": did,
                "paid_date": today})


_SIZE_CODES = {"XXS": "2X", "XS": "XS", "S": "SM", "M": "MD", "L": "LG", "XL": "XL", "XXL": "2L"}


@tool(owner="agent", rw="write")
def take_replacement_reservation_e3795f43(ctx: ToolContext, replaced_reservation_id: str, size: str,
                                          deposit_required_usd: float) -> str:
    """Takes a new Deposit Pre-Order that replaces a Deposit Pre-Order of the customer in another size,
    and charges its deposit to the card on the customer's account. The new reservation is for the same
    customer, style, colour, product name, units, reserved unit price and original and current ship-by
    dates as the reservation it replaces, in the size given; its SKU is that reservation's style and colour
    followed by the size code of the new size (XS, SM, MD, LG, XL for XS, S, M, L, XL). It is created in
    status reserved, dated today at the current Eastern Time, with no delay notices and no size changes
    used, and the deposit charge is booked on its history. Afterwards the customer has a new reservation
    number showing the size, price, ship-by date and deposit recorded.

    Args:
        replaced_reservation_id: Id class — the reservation number of the Deposit Pre-Order being replaced, as returned by the reservation lookup.
        size: Verbatim class — the size the customer states for the replacement, copied exactly as the customer says it, for example "L" (verbatim).
        deposit_required_usd: Fixed-format class — the deposit charged to the card at reservation, in USD with 2 decimal places, already rounded half up to the cent.

    Returns:
        A dict confirming the new reservation: reservation_id (the new reservation number, text), status
        (always "reserved"), reserved_date (today, YYYY-MM-DD), sku (text, MF-######-CCC-SS), size (as
        recorded), unit_price_usd (USD, 2 decimal places), current_ship_by_date (YYYY-MM-DD),
        deposit_required_usd (USD, 2 decimal places) and deposit_entry_id (reference of the deposit charge
        entry, text). A returned dict with status "reserved" means the reservation and its deposit charge
        were recorded.
    """
    old = (ctx.find("reservations", reservation_id=replaced_reservation_id) or [{}])[0]
    now = ctx.now()
    today = now[:10]
    deposit = round(float(deposit_required_usd), 2)
    code = _SIZE_CODES.get(str(size).strip().upper(), str(size).strip().upper()[:2])
    sku = "-".join(str(old.get("sku", "")).split("-")[:3] + [code])
    customer_id = old.get("customer_id", "")
    nid = ctx.make_id("res_", replaced_reservation_id, size, deposit)
    ctx.create("reservations", nid, reservation_id=nid, customer_id=customer_id, variant_name="Deposit Pre-Order",
               status="reserved", reserved_date=today, reserved_time_et=now[11:16], sku=sku,
               style_code=old.get("style_code", ""), style_name=old.get("style_name", ""), size=size,
               quantity=old.get("quantity", 1), unit_price_usd=old.get("unit_price_usd"),
               deposit_required_usd=deposit, original_ship_by_date=old.get("original_ship_by_date", ""),
               current_ship_by_date=old.get("current_ship_by_date", ""), delay_notice_count=0,
               consent_deadline_date="", personalization_text="", specs_confirmed_date="", size_changes_used=0,
               production_start_date="", allocated_date="", fulfilled_date="", fulfilment_order_id=None,
               cancelled_date="", cancel_reason="none")
    did = ctx.make_id("rev_", nid, "captured", deposit)
    ctx.create("reservation_events", did, reservation_event_id=did, reservation_id=nid, customer_id=customer_id,
               event_type="preorders_deposit_captured", event_date=today, amount_usd=deposit,
               tender_type="card_or_wallet", refund_reason="not_applicable", fulfilment_order_id=None,
               notice_number=0, revised_ship_by_date="", consent_mode="not_applicable",
               auth_amount_usd=0.00, auth_outcome="not_applicable")
    return str({"reservation_id": nid, "status": "reserved", "reserved_date": today, "sku": sku, "size": size,
                "unit_price_usd": old.get("unit_price_usd"), "current_ship_by_date": old.get("current_ship_by_date", ""),
                "deposit_required_usd": deposit, "deposit_entry_id": did})

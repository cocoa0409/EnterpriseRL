"""Hidden task tools of the pap_supply_replenishment difficulty (PAP Supply Replenishment Program).

Each tool performs exactly one atomic write on a patient's PAP supply enrollment and takes the values
the agent has already worked out from the published policy; no tool judges eligibility, aggregates
history or computes a value on the agent's behalf.
"""

from erlbench import ToolContext, tool


@tool(owner="user", rw="write")
def confirm_refill_request_b3535d21(ctx: ToolContext, resupply_holding_id: str, items_requested: str,
                                    supply_status_confirmed: str) -> str:
    """The patient, on this phone call, places a refill request for PAP supplies on their own supply
    enrollment. One call records one refill confirmation dated today, received through the phone
    channel, naming the supply items the patient asks to receive and the supply status the patient
    reports. Once recorded, the request is visible on the enrollment's refill-contact history. Success is the receipt below with status "recorded".

    Args:
        resupply_holding_id: Id class — the reference number of the patient's PAP supply enrollment,
            read from the enrollment lookup before the call.
        items_requested: Fixed-format class — the supply items the request names, written as HCPCS codes
            separated by commas in ascending order, no spaces, each code written in full as one capital
            letter followed by four digits and named once; an empty string is not accepted as a request.
        supply_status_confirmed: Enum class — what the patient reports about the supply on hand of the
            items named: nearly_exhausted when the patient says the supply of those items is used up or
            about to run out; not_exhausted when the patient says those items still have useful supply
            left.

    Returns:
        A dictionary receipt: "status" is "recorded" when the request was written; "resupply_contact_id"
        is the reference number of the new refill confirmation (text); "contact_date" is today's date as
        YYYY-MM-DD; "contact_channel" is "phone_call"; "items_requested" echoes the HCPCS codes recorded
        (text, comma separated, ascending); "supply_status_confirmed" echoes the reported supply status.
    """
    holding = ctx.find("resupply_holdings", resupply_holding_id=resupply_holding_id)
    customer_id = holding[0].get("customer_id") if holding else ""
    today = ctx.now()[:10]
    rid = ctx.make_id("rsc_", resupply_holding_id, items_requested, supply_status_confirmed, today)
    ctx.create("resupply_contacts", rid, resupply_contact_id=rid, resupply_holding_id=resupply_holding_id,
               customer_id=customer_id, event_type="resupply_refill_confirmed", contact_date=today,
               contact_channel="phone_call", items_requested=items_requested,
               supply_status_confirmed=supply_status_confirmed)
    return str({"status": "recorded", "resupply_contact_id": rid, "contact_date": today,
                "contact_channel": "phone_call", "items_requested": items_requested,
                "supply_status_confirmed": supply_status_confirmed})


@tool(owner="agent", rw="write")
def ship_covered_refill_e8c1261e(ctx: ToolContext, resupply_holding_id: str, resupply_contact_id: str,
                                 coverage_id: str, hcpcs_code: str, quantity: int,
                                 covers_through_date: str, shipping_method: str) -> str:
    """Books one coverage-billed shipment line of a PAP supply item on the patient's supply enrollment,
    shipping today. One call creates one shipped item
    line dated today, billed to the named coverage record, carrying the units shipped and the last day
    of use they cover; the claim is pending, so the allowed, paid and patient amounts are
    recorded as 0.00. The line then appears in the enrollment's shipment history.
    Success is the receipt below with status "shipped".

    Args:
        resupply_holding_id: Id class — the reference number of the patient's PAP supply enrollment,
            read from the enrollment lookup before the call.
        resupply_contact_id: Id class — the reference number of the refill confirmation the shipment
            rests on, read from the refill-contact lookup before the call; it identifies this booking and is
            not stored on the line.
        coverage_id: Id class — the reference number of the coverage record the line is billed to, read
            from the enrollment or coverage lookup before the call.
        hcpcs_code: Enum class — the supply item shipped: A7030 a full face mask; A7031 a full face mask
            cushion; A7034 a nasal mask or nasal pillows interface; A7032 a nasal mask cushion; A7033 a
            pair of nasal pillows; A7035 headgear; A7036 a chinstrap; A7037 standard tubing; A4604 heated
            tubing; A7038 a disposable filter; A7039 a non-disposable filter; A7046 a humidifier water
            chamber; none never applies to an item line and is not accepted here.
        quantity: Fixed-format class — the units of the item shipped on the line, a non-negative
            integer.
        covers_through_date: Fixed-format class — the last day of use the units shipped cover, as
            YYYY-MM-DD.
        shipping_method: Enum class — how the shipment travels: ground when it goes by the standard
            carrier; expedited when the patient asked for the faster paid service; branch_pickup when
            the patient collects it at a Summit Ridge branch; none never applies to a shipped item and is
            not accepted here.

    Returns:
        A dictionary receipt: "status" is "shipped" when the line was written; "resupply_line_id" is the
        reference number of the new shipment line (text); "hcpcs_code" and "quantity" echo the item and
        units; "service_from_date" is today's ship date as YYYY-MM-DD; "covers_through_date" echoes the
        last day covered as YYYY-MM-DD; "billing_basis" is "coverage"; "coverage_id" echoes the coverage
        record billed.
    """
    holding = ctx.find("resupply_holdings", resupply_holding_id=resupply_holding_id)
    customer_id = holding[0].get("customer_id") if holding else ""
    today = ctx.now()[:10]
    rid = ctx.make_id("rsl_", resupply_holding_id, resupply_contact_id, coverage_id, hcpcs_code,
                      quantity, covers_through_date, shipping_method, today)
    ctx.create("resupply_shipments", rid, resupply_line_id=rid, resupply_holding_id=resupply_holding_id,
               customer_id=customer_id, event_type="resupply_item_shipped", coverage_id=coverage_id,
               billing_basis="coverage", hcpcs_code=hcpcs_code, quantity=int(quantity),
               service_from_date=today, covers_through_date=covers_through_date, adjudication_date="",
               allowed_amount=0.0, payer_paid_amount=0.0, patient_responsibility=0.0, self_pay_amount=0.0,
               shipping_method=shipping_method, claim_number="", denial_reason="none", original_line_id="",
               reversal_reason="none", replacement_reason="none")
    return str({"status": "shipped", "resupply_line_id": rid, "hcpcs_code": hcpcs_code,
                "quantity": int(quantity), "service_from_date": today,
                "covers_through_date": covers_through_date, "billing_basis": "coverage",
                "coverage_id": coverage_id})


@tool(owner="agent", rw="write")
def send_no_charge_replacement_8a217fc0(ctx: ToolContext, resupply_holding_id: str, original_line_id: str,
                                        replacement_reason: str, hcpcs_code: str, quantity: int,
                                        covers_through_date: str, shipping_method: str) -> str:
    """Ships a supply item again at no charge to replace one earlier shipment line of the patient's PAP
    supply enrollment. One call creates one no-charge replacement line dated today that names the line
    it replaces and why, carries the item and units sent and the last day of use they cover, and bills
    neither the coverage nor the patient. The replacement then appears in the enrollment's shipment
    history linked to the replaced line. Success is the receipt below with status "replacement_sent".

    Args:
        resupply_holding_id: Id class — the reference number of the patient's PAP supply enrollment,
            read from the enrollment lookup before the call.
        original_line_id: Id class — the reference number of the earlier shipment line being replaced,
            read from the shipment-line lookup before the call.
        replacement_reason: Enum class — why the line is replaced: mask_fit_exchange when a newly shipped
            interface or cushion is exchanged because it does not fit the patient; manufacturer_defect
            when the item arrived defective; carrier_lost when the carrier lost the package and it was
            never delivered; wrong_item when Summit Ridge shipped an item other than the one that fits
            the patient's recorded equipment; none never applies to a replacement and is not accepted
            here.
        hcpcs_code: Enum class — the supply item sent as the replacement: A7030 a full face mask; A7031 a
            full face mask cushion; A7034 a nasal mask or nasal pillows interface; A7032 a nasal mask
            cushion; A7033 a pair of nasal pillows; A7035 headgear; A7036 a chinstrap; A7037 standard
            tubing; A4604 heated tubing; A7038 a disposable filter; A7039 a non-disposable filter; A7046 a
            humidifier water chamber; none never applies to an item line and is not accepted here.
        quantity: Fixed-format class — the units of the item sent, a non-negative integer.
        covers_through_date: Fixed-format class — the last day of use the replacement covers, as
            YYYY-MM-DD.
        shipping_method: Enum class — how the replacement travels: ground when it goes by the standard
            carrier; expedited when the patient asked for the faster paid service; branch_pickup when the
            patient collects it at a Summit Ridge branch; none never applies to a shipped item and is not
            accepted here.

    Returns:
        A dictionary receipt: "status" is "replacement_sent" when the line was written;
        "resupply_line_id" is the reference number of the new replacement line (text);
        "original_line_id" echoes the replaced line; "replacement_reason" echoes the reason;
        "hcpcs_code" and "quantity" echo the item and units sent; "service_from_date" is today's ship
        date as YYYY-MM-DD; "covers_through_date" echoes the last day covered as YYYY-MM-DD;
        "billing_basis" is "no_charge".
    """
    holding = ctx.find("resupply_holdings", resupply_holding_id=resupply_holding_id)
    customer_id = holding[0].get("customer_id") if holding else ""
    today = ctx.now()[:10]
    rid = ctx.make_id("rsr_", resupply_holding_id, original_line_id, replacement_reason, hcpcs_code,
                      quantity, covers_through_date, shipping_method, today)
    ctx.create("resupply_shipments", rid, resupply_line_id=rid, resupply_holding_id=resupply_holding_id,
               customer_id=customer_id, event_type="resupply_no_charge_replacement", coverage_id="",
               billing_basis="no_charge", hcpcs_code=hcpcs_code, quantity=int(quantity),
               service_from_date=today, covers_through_date=covers_through_date, adjudication_date="",
               allowed_amount=0.0, payer_paid_amount=0.0, patient_responsibility=0.0, self_pay_amount=0.0,
               shipping_method=shipping_method, claim_number="", denial_reason="none",
               original_line_id=original_line_id, reversal_reason="none",
               replacement_reason=replacement_reason)
    return str({"status": "replacement_sent", "resupply_line_id": rid, "original_line_id": original_line_id,
                "replacement_reason": replacement_reason, "hcpcs_code": hcpcs_code, "quantity": int(quantity),
                "service_from_date": today, "covers_through_date": covers_through_date,
                "billing_basis": "no_charge"})


@tool(owner="agent", rw="write")
def record_continued_use_proof_c97fce72(ctx: ToolContext, resupply_holding_id: str,
                                        last_continued_use_date: str) -> str:
    """Records a newer proof of continued PAP device use on the patient's supply enrollment. One call
    replaces the enrollment's continued-use date with the date credited to the proof taken from the
    device's compliance data or the treating practitioner's note; the supply order date and every other
    enrollment detail stay as they are. The new date is visible on the enrollment at once. Success is
    the receipt below with status "proof_recorded".

    Args:
        resupply_holding_id: Id class — the reference number of the patient's PAP supply enrollment,
            read from the enrollment lookup before the call.
        last_continued_use_date: Fixed-format class — the date credited to the proof of continued use,
            as YYYY-MM-DD.

    Returns:
        A dictionary receipt: "status" is "proof_recorded" when the enrollment was updated;
        "resupply_holding_id" echoes the enrollment; "last_continued_use_date" is the continued-use date
        now on the enrollment as YYYY-MM-DD; "previous_continued_use_date" is the date it replaced as
        YYYY-MM-DD.
    """
    holding = ctx.find("resupply_holdings", resupply_holding_id=resupply_holding_id)
    previous = holding[0].get("last_continued_use_date") if holding else ""
    ctx.update("resupply_holdings", resupply_holding_id, last_continued_use_date=last_continued_use_date)
    return str({"status": "proof_recorded", "resupply_holding_id": resupply_holding_id,
                "last_continued_use_date": last_continued_use_date,
                "previous_continued_use_date": previous})


@tool(owner="agent", rw="write")
def update_mask_style_bfa4256b(ctx: ToolContext, resupply_holding_id: str, mask_style: str) -> str:
    """Updates the interface style recorded on the patient's PAP supply enrollment. One call replaces the
    enrollment's mask style with the style given; humidifier use, tubing use, the automatic-shipment
    choice and every other enrollment detail stay as they are. The new style is visible on the
    enrollment at once. Success
    is the receipt below with status "style_updated".

    Args:
        resupply_holding_id: Id class — the reference number of the patient's PAP supply enrollment,
            read from the enrollment lookup before the call.
        mask_style: Enum class — the interface style to record: full_face when the patient uses a full
            face mask with full face cushions; nasal when the patient uses a nasal mask with nasal
            cushions; nasal_pillows when the patient uses a nasal pillows interface with pillow pairs.

    Returns:
        A dictionary receipt: "status" is "style_updated" when the enrollment was changed;
        "resupply_holding_id" echoes the enrollment; "mask_style" is the style now recorded (text);
        "previous_mask_style" is the style it replaced (text).
    """
    holding = ctx.find("resupply_holdings", resupply_holding_id=resupply_holding_id)
    previous = holding[0].get("mask_style") if holding else ""
    ctx.update("resupply_holdings", resupply_holding_id, mask_style=mask_style)
    return str({"status": "style_updated", "resupply_holding_id": resupply_holding_id, "mask_style": mask_style,
                "previous_mask_style": previous})


@tool(owner="agent", rw="write")
def book_subscription_line_cd282959(ctx: ToolContext, resupply_holding_id: str, hcpcs_code: str, quantity: int,
                                    self_pay_amount: float, covers_through_date: str,
                                    shipping_method: str) -> str:
    """Books one self-pay standing-order line of a PAP supply item on the patient's supply enrollment,
    shipping today and charged to the patient's card on file. One call creates one shipped item line
    dated today carrying the item, the units, the amount charged to the card and the last day of use
    the units cover; it is never billed to a coverage record. The line then appears in the enrollment's
    shipment history and the amount is recorded as charged to the card on file on the ship date. Success is the receipt below with
    status "shipped".

    Args:
        resupply_holding_id: Id class — the reference number of the patient's PAP supply enrollment,
            read from the enrollment lookup before the call.
        hcpcs_code: Enum class — the supply item shipped: A7030 a full face mask; A7031 a full face mask
            cushion; A7034 a nasal mask or nasal pillows interface; A7032 a nasal mask cushion; A7033 a
            pair of nasal pillows; A7035 headgear; A7036 a chinstrap; A7037 standard tubing; A4604 heated
            tubing; A7038 a disposable filter; A7039 a non-disposable filter; A7046 a humidifier water
            chamber; none never applies to an item line and is not accepted here.
        quantity: Fixed-format class — the units of the item shipped on the line, a non-negative
            integer.
        self_pay_amount: Fixed-format class — the amount charged to the patient's card for the line, in
            USD, 2 decimal places, rounded to the cent half up.
        covers_through_date: Fixed-format class — the last day of use the units shipped cover, as
            YYYY-MM-DD.
        shipping_method: Enum class — how the shipment travels: ground when it goes by the standard
            carrier; expedited when the patient asked for the faster paid service; branch_pickup when the
            patient collects it at a Summit Ridge branch; none never applies to a shipped item and is not
            accepted here.

    Returns:
        A dictionary receipt: "status" is "shipped" when the line was written; "resupply_line_id" is the
        reference number of the new line (text); "hcpcs_code" and "quantity" echo the item and units;
        "self_pay_amount" is the amount charged to the card in USD with 2 decimal places;
        "service_from_date" is today's ship date as YYYY-MM-DD; "covers_through_date" echoes the last
        day covered as YYYY-MM-DD; "billing_basis" is "self_pay".
    """
    holding = ctx.find("resupply_holdings", resupply_holding_id=resupply_holding_id)
    customer_id = holding[0].get("customer_id") if holding else ""
    today = ctx.now()[:10]
    amount = round(float(self_pay_amount), 2)
    rid = ctx.make_id("rss_", resupply_holding_id, hcpcs_code, quantity, amount, covers_through_date,
                      shipping_method, today)
    ctx.create("resupply_shipments", rid, resupply_line_id=rid, resupply_holding_id=resupply_holding_id,
               customer_id=customer_id, event_type="resupply_item_shipped", coverage_id=None,
               billing_basis="self_pay", hcpcs_code=hcpcs_code, quantity=int(quantity), service_from_date=today,
               covers_through_date=covers_through_date, adjudication_date=today, allowed_amount=0.0,
               payer_paid_amount=0.0, patient_responsibility=0.0, self_pay_amount=amount,
               shipping_method=shipping_method, claim_number="", denial_reason="none", original_line_id="",
               reversal_reason="none", replacement_reason="none")
    return str({"status": "shipped", "resupply_line_id": rid, "hcpcs_code": hcpcs_code, "quantity": int(quantity),
                "self_pay_amount": amount, "service_from_date": today,
                "covers_through_date": covers_through_date, "billing_basis": "self_pay"})


@tool(owner="agent", rw="write")
def book_ground_shipping_charge_38ca3aab(ctx: ToolContext, resupply_holding_id: str, service_from_date: str,
                                         self_pay_amount: float) -> str:
    """Books the patient-paid ground shipping charge for one shipment of the patient's PAP supply
    enrollment that went out by ground on a given ship date. One call creates one ground shipping-charge
    line dated with that shipment's ship date and charged to the patient's card on file; it is never
    billed to coverage. The charge then appears in the enrollment's shipment history under that
    shipment's ship date. Success is the receipt below with status "charge_booked".

    Args:
        resupply_holding_id: Id class — the reference number of the patient's PAP supply enrollment,
            read from the enrollment lookup before the call.
        service_from_date: Fixed-format class — the ship date of the shipment the charge belongs to, as
            YYYY-MM-DD.
        self_pay_amount: Fixed-format class — the ground shipping charge taken from the patient's card,
            in USD, 2 decimal places, rounded to the cent half up.

    Returns:
        A dictionary receipt: "status" is "charge_booked" when the charge was written;
        "resupply_line_id" is the reference number of the shipping-charge line (text);
        "service_from_date" echoes the shipment's ship date as YYYY-MM-DD; "shipping_method" is
        "ground"; "self_pay_amount" is the charge in USD with 2 decimal places.
    """
    holding = ctx.find("resupply_holdings", resupply_holding_id=resupply_holding_id)
    customer_id = holding[0].get("customer_id") if holding else ""
    amount = round(float(self_pay_amount), 2)
    rid = ctx.make_id("rsg_", resupply_holding_id, service_from_date, amount)
    ctx.create("resupply_shipments", rid, resupply_line_id=rid, resupply_holding_id=resupply_holding_id,
               customer_id=customer_id, event_type="resupply_shipping_charge", coverage_id=None,
               billing_basis="self_pay", hcpcs_code="none", quantity=0, service_from_date=service_from_date,
               covers_through_date="", adjudication_date=ctx.now()[:10], allowed_amount=0.0,
               payer_paid_amount=0.0, patient_responsibility=0.0, self_pay_amount=amount,
               shipping_method="ground", claim_number="", denial_reason="none", original_line_id="",
               reversal_reason="none", replacement_reason="none")
    return str({"status": "charge_booked", "resupply_line_id": rid, "service_from_date": service_from_date,
                "shipping_method": "ground", "self_pay_amount": amount})


@tool(owner="user", rw="write")
def pay_expedited_shipping_41dc5e4a(ctx: ToolContext, resupply_holding_id: str, self_pay_amount: float) -> str:
    """The patient, on this call, pays for expedited shipping of today's shipment from their own PAP
    supply enrollment. One call creates one expedited shipping-charge line dated today and charged to
    the patient's card on file; it is never billed to coverage. The charge then appears in the
    enrollment's shipment history under today's date. Success is the receipt below with status
    "charge_paid".

    Args:
        resupply_holding_id: Id class — the reference number of the patient's PAP supply enrollment,
            read to the patient by the agent from the enrollment lookup before the call.
        self_pay_amount: Fixed-format class — the expedited shipping charge the patient pays, in USD, 2
            decimal places, rounded to the cent half up.

    Returns:
        A dictionary receipt: "status" is "charge_paid" when the charge was written; "resupply_line_id"
        is the reference number of the shipping-charge line (text); "service_from_date" is today's ship
        date as YYYY-MM-DD; "shipping_method" is "expedited"; "self_pay_amount" is the charge in USD
        with 2 decimal places.
    """
    holding = ctx.find("resupply_holdings", resupply_holding_id=resupply_holding_id)
    customer_id = holding[0].get("customer_id") if holding else ""
    today = ctx.now()[:10]
    amount = round(float(self_pay_amount), 2)
    rid = ctx.make_id("rse_", resupply_holding_id, amount, today)
    ctx.create("resupply_shipments", rid, resupply_line_id=rid, resupply_holding_id=resupply_holding_id,
               customer_id=customer_id, event_type="resupply_shipping_charge", coverage_id=None,
               billing_basis="self_pay", hcpcs_code="none", quantity=0, service_from_date=today,
               covers_through_date="", adjudication_date=today, allowed_amount=0.0, payer_paid_amount=0.0,
               patient_responsibility=0.0, self_pay_amount=amount, shipping_method="expedited",
               claim_number="", denial_reason="none", original_line_id="", reversal_reason="none",
               replacement_reason="none")
    return str({"status": "charge_paid", "resupply_line_id": rid, "service_from_date": today,
                "shipping_method": "expedited", "self_pay_amount": amount})

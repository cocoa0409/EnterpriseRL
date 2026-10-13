"""Hidden task tools of the sensor_calibration_desk difficulty (ADAS Sensor Calibrations).

Each tool performs one atomic write on a calibration order's money history. None of them checks a
business prerequisite or works out a figure: the amount is decided by the caller from the published
rules and passed in.
"""

from erlbench import ToolContext, tool


@tool(owner="agent", rw="write")
def post_alignment_check_charge_59500100(ctx: ToolContext, adas_order_id: str, amount_usd: float) -> str:
    """Post the alignment check charge on a sensor calibration order. One call books a single
    alignment check charge, dated today, against the calibration order named, for the amount given;
    the charge raises what is owed on that order by exactly that amount and appears from then on in
    the order's calibration money history as an alignment check charge. Nothing else on the order
    changes. A successful call returns a receipt carrying the new entry's reference number.

    Args:
        adas_order_id: Id class — reference number of the calibration order the charge is booked on, as returned by the calibration order lookup for the customer.
        amount_usd: Fixed-format class — the alignment check charge in US dollars (USD), a positive amount with 2 decimal places, already rounded to the cent by the caller; it is stored exactly as given.

    Returns:
        A dictionary rendered as text with: status (the text "posted" when the charge was booked),
        adas_entry_id (reference number of the new charge entry), adas_order_id (the calibration
        order charged), charge_type (always "alignment_check"), amount_usd (the amount booked, USD,
        2 decimal places) and entry_date (the business date of the entry, YYYY-MM-DD).
    """
    rows = ctx.find("adas_orders", adas_order_id=adas_order_id)
    customer_id = rows[0].get("customer_id") if rows else ""
    amount = round(float(amount_usd), 2)
    rid = ctx.make_id("adl_", adas_order_id, amount_usd)
    ctx.create("adas_ledger", rid, adas_entry_id=rid, adas_order_id=adas_order_id, customer_id=customer_id,
               event_type="adas_charge", entry_date=ctx.now()[:10], charge_type="alignment_check",
               amount_usd=amount)
    return str({"status": "posted", "adas_entry_id": rid, "adas_order_id": adas_order_id,
                "charge_type": "alignment_check", "amount_usd": amount, "entry_date": ctx.now()[:10]})


@tool(owner="agent", rw="write")
def post_comeback_goodwill_credit_c6e84f0b(ctx: ToolContext, adas_order_id: str, source_entry_id: str,
                                            amount_usd: float) -> str:
    """Write off part of a charge on a sensor calibration order as a goodwill credit for an alignment
    comeback. One call books a single goodwill write-off, dated today, on the calibration order named,
    reducing the charge entry named by the amount given; what is owed on the order falls by exactly
    that amount and the write-off appears in the order's calibration money history as a goodwill
    write-off referring to that charge. The charge itself is not altered. A successful call returns a
    receipt carrying the new entry's reference number.

    Args:
        adas_order_id: Id class — reference number of the calibration order the write-off is booked on, as returned by the calibration order lookup for the customer.
        source_entry_id: Id class — reference number of the charge entry being reduced, as listed in the order's calibration money history lookup.
        amount_usd: Fixed-format class — the goodwill write-off in US dollars (USD), a positive amount with 2 decimal places, already rounded to the cent by the caller; it is stored exactly as given.

    Returns:
        A dictionary rendered as text with: status (the text "written_off" when the write-off was
        booked), adas_entry_id (reference number of the new write-off entry), adas_order_id (the
        calibration order), source_entry_id (the charge reduced), no_charge_reason (always
        "goodwill"), amount_usd (the amount written off, USD, 2 decimal places) and entry_date (the
        business date of the entry, YYYY-MM-DD).
    """
    rows = ctx.find("adas_orders", adas_order_id=adas_order_id)
    customer_id = rows[0].get("customer_id") if rows else ""
    amount = round(float(amount_usd), 2)
    rid = ctx.make_id("adw_", adas_order_id, source_entry_id, amount_usd)
    ctx.create("adas_ledger", rid, adas_entry_id=rid, adas_order_id=adas_order_id, customer_id=customer_id,
               event_type="adas_no_charge", entry_date=ctx.now()[:10], source_entry_id=source_entry_id,
               no_charge_reason="goodwill", amount_usd=amount)
    return str({"status": "written_off", "adas_entry_id": rid, "adas_order_id": adas_order_id,
                "source_entry_id": source_entry_id, "no_charge_reason": "goodwill", "amount_usd": amount,
                "entry_date": ctx.now()[:10]})


@tool(owner="user", rw="write")
def pay_alignment_correction_authorization_61ce2890(ctx: ToolContext, adas_order_id: str, amount_usd: float,
                                                     payment_method: str) -> str:
    """The customer authorizes the four-wheel alignment correction on their own sensor calibration
    order by paying the authorization amount. One call books a single customer payment, dated today,
    on the calibration order named, for the amount given and by the method given; what is owed on the
    order falls by exactly that amount and the payment appears in the order's calibration money
    history as a customer payment. A successful call returns a receipt carrying the payment's
    reference number, which the customer can quote afterwards.

    Args:
        adas_order_id: Id class — reference number of the customer's calibration order, as read to the customer by the desk from the calibration order lookup.
        amount_usd: Fixed-format class — the authorization amount in US dollars (USD), a positive amount with 2 decimal places, already rounded to the cent; it is charged and stored exactly as given.
        payment_method: Enum class — how the customer pays: card when the customer pays with a debit or credit card, including over the phone; cash when the customer hands over cash at the center; check when the customer pays with a personal check at the center; remittance only for an insurer glass program paying under its own remittance, never for a customer paying for themselves.

    Returns:
        A dictionary rendered as text with: status (the text "paid" when the payment was booked),
        adas_entry_id (reference number of the payment), adas_order_id (the calibration order paid),
        payer_kind (always "customer"), payment_method (the method used), amount_usd (the amount paid,
        USD, 2 decimal places) and entry_date (the business date of the payment, YYYY-MM-DD).
    """
    rows = ctx.find("adas_orders", adas_order_id=adas_order_id)
    customer_id = rows[0].get("customer_id") if rows else ""
    amount = round(float(amount_usd), 2)
    rid = ctx.make_id("adc_", adas_order_id, amount_usd, payment_method)
    ctx.create("adas_ledger", rid, adas_entry_id=rid, adas_order_id=adas_order_id, customer_id=customer_id,
               event_type="adas_payment", entry_date=ctx.now()[:10], payer_kind="customer",
               payment_method=payment_method, payment_reference="", amount_usd=amount)
    return str({"status": "paid", "adas_entry_id": rid, "adas_order_id": adas_order_id, "payer_kind": "customer",
                "payment_method": payment_method, "amount_usd": amount, "entry_date": ctx.now()[:10]})


@tool(owner="user", rw="write")
def pay_calibration_acceptance_f9e8bcf7(ctx: ToolContext, adas_order_id: str, amount_usd: float,
                                         payment_method: str) -> str:
    """The customer accepts the sensor calibration on their own customer-pay calibration order by
    paying the acceptance amount. One call books a single customer payment, dated today, on the
    calibration order named, for the amount given and by the method given; what is owed on the order
    falls by exactly that amount, the payment appears in the order's calibration money history as a
    customer payment, and it stands as the customer's acceptance of the calibration. A successful call
    returns a receipt carrying the payment's reference number, which the customer can quote afterwards.

    Args:
        adas_order_id: Id class — reference number of the customer's calibration order, as read to the customer by the desk from the calibration order lookup.
        amount_usd: Fixed-format class — the acceptance amount in US dollars (USD), a positive amount with 2 decimal places, already rounded to the cent; it is charged and stored exactly as given.
        payment_method: Enum class — how the customer pays: card when the customer pays with a debit or credit card, including over the phone; cash when the customer hands over cash at the center; check when the customer pays with a personal check at the center; remittance only for an insurer glass program paying under its own remittance, never for a customer paying for themselves.

    Returns:
        A dictionary rendered as text with: status (the text "accepted" when the payment was booked),
        adas_entry_id (reference number of the payment), adas_order_id (the calibration order
        accepted), payer_kind (always "customer"), payment_method (the method used), amount_usd (the
        amount paid, USD, 2 decimal places) and entry_date (the business date of the payment,
        YYYY-MM-DD).
    """
    rows = ctx.find("adas_orders", adas_order_id=adas_order_id)
    customer_id = rows[0].get("customer_id") if rows else ""
    amount = round(float(amount_usd), 2)
    rid = ctx.make_id("ada_", adas_order_id, amount_usd, payment_method)
    ctx.create("adas_ledger", rid, adas_entry_id=rid, adas_order_id=adas_order_id, customer_id=customer_id,
               event_type="adas_payment", entry_date=ctx.now()[:10], payer_kind="customer",
               payment_method=payment_method, payment_reference="", amount_usd=amount)
    return str({"status": "accepted", "adas_entry_id": rid, "adas_order_id": adas_order_id,
                "payer_kind": "customer", "payment_method": payment_method, "amount_usd": amount,
                "entry_date": ctx.now()[:10]})

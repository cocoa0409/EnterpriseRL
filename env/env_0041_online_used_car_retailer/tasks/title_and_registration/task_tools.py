"""Hidden task tools of the title_and_registration difficulty (env_0041_online_used_car_retailer, Kestrel Auto).

Each tool performs one atomic write on a Title & Registration Services order and is reached only through
unlock_* -> call_*; its name is published by exactly one extended policy's target_tool.
"""

from erlbench import ToolContext, tool

_MONTH_DAYS = (31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31)


@tool(owner="user", rw="write")
def pay_title_fee_shortage_f6fcb150(ctx: ToolContext, title_order_id: str, amount: float) -> str:
    """The buyer pays, in person, their payment toward the fee shortage the state named when it sent their
    title and registration packet back. One call books one payment from the buyer on the title and
    registration order as a state fee collected against the registration fee, dated today, and adds the
    amount to the state fees Kestrel is holding on that order for the state. The buyer sees the payment
    on the order's history immediately; the receipt below confirms it was booked.

    Args:
        title_order_id: Id class — the reference number of the buyer's title and registration order, as
            shown by the title and registration order lookup for this buyer before the call.
        amount: Fixed-format class — the payment the buyer makes now, in USD, a positive amount with 2
            decimal places (cents), already rounded to the cent; it is booked exactly as passed.

    Returns:
        A dict: status ("payment_recorded" when the payment was booked), title_txn_id (reference number of
        the new fee entry), title_order_id (the order paid on), fee_type (always "registration_fee"),
        amount (USD with 2 decimal places as booked), txn_date (booking date, YYYY-MM-DD) and
        state_fees_held (USD with 2 decimal places now held on the order after this payment).
    """
    amt = round(float(amount), 2)
    rid = ctx.make_id("ttx_", title_order_id, amt, "shortage_payment")
    today = ctx.now()[:10]
    ctx.create("title_transactions", rid, title_txn_id=rid, title_order_id=title_order_id,
               customer_id=(ctx.find("title_orders", title_order_id=title_order_id) or [{}])[0].get("customer_id"),
               event_type="title_state_fee_collected", txn_date=today, amount=amt, fee_type="registration_fee",
               document_type="not_applicable", tag_sequence=0, temp_tag_number="", tag_expires_date="",
               reject_code="not_applicable", reimbursement_reason="not_applicable",
               document_format="not_applicable", document_date="", citation_number="", source_txn_id="")
    order = (ctx.find("title_orders", title_order_id=title_order_id) or [{}])[0]
    held = round(float(order.get("state_fees_held") or 0) + amt, 2)
    ctx.update("title_orders", title_order_id, state_fees_held=held)
    return str({"status": "payment_recorded", "title_txn_id": rid, "title_order_id": title_order_id,
                "fee_type": "registration_fee", "amount": amt, "txn_date": today, "state_fees_held": held})


@tool(owner="agent", rw="write")
def issue_title_extension_tag_53dbe274(ctx: ToolContext, title_order_id: str, valid_days: int) -> str:
    """Issue an extension temporary tag for the vehicle on a title and registration order. One call books
    a new temporary tag in the order's history dated today, numbered in sequence after the tags already
    issued on the order, with a newly printed tag number and an expiration date that is today plus the
    number of calendar days passed; it then records that tag on the order as the tag currently on the
    vehicle (tag number and expiration) and counts one more extension tag used. The buyer can print and
    display the new tag at once; the receipt gives its number and expiration.

    Args:
        title_order_id: Id class — the reference number of the title and registration order, as shown by
            the title and registration order lookup for this buyer before the call.
        valid_days: Fixed-format class — how many calendar days the new tag is valid counted from today's
            issue date, a positive integer number of days; the tag's printed expiration is today plus this
            many days, written as YYYY-MM-DD.

    Returns:
        A dict: status ("extension_tag_issued" on success), title_order_id, title_txn_id (reference number
        of the tag entry), tag_sequence (integer position of this tag, 1 being the original),
        temp_tag_number (the number printed on the new tag), issued_date (YYYY-MM-DD), tag_expires_date
        (YYYY-MM-DD printed on the tag) and temp_tag_extensions_used (integer count of extension tags now
        used on the order).
    """
    order = (ctx.find("title_orders", title_order_id=title_order_id) or [{}])[0]
    used = int(order.get("temp_tag_extensions_used") or 0)
    seq = used + 2
    today = ctx.now()[:10]
    y, m, d = (int(p) for p in today.split("-"))
    n = int(valid_days)
    while n > 0:  # calendar arithmetic on the issue date; no clock is read
        leap = (y % 4 == 0 and y % 100 != 0) or y % 400 == 0
        last = 29 if (m == 2 and leap) else _MONTH_DAYS[m - 1]
        step = min(n, last - d + 1)
        d += step
        n -= step
        if d > last:
            d, m = 1, m + 1
            if m > 12:
                m, y = 1, y + 1
    expires = f"{y:04d}-{m:02d}-{d:02d}"
    rid = ctx.make_id("ttx_", title_order_id, int(valid_days), seq)
    tag_no = "KX" + ctx.make_id("", title_order_id, seq, length=6).upper()
    ctx.create("title_transactions", rid, title_txn_id=rid, title_order_id=title_order_id,
               customer_id=order.get("customer_id"), event_type="title_temp_tag_issued", txn_date=today,
               amount=0.0, fee_type="not_applicable", document_type="not_applicable", tag_sequence=seq,
               temp_tag_number=tag_no, tag_expires_date=expires, reject_code="not_applicable",
               reimbursement_reason="not_applicable", document_format="not_applicable", document_date="",
               citation_number="", source_txn_id="")
    ctx.update("title_orders", title_order_id, temp_tag_number=tag_no, temp_tag_expires_date=expires,
               temp_tag_extensions_used=used + 1)
    return str({"status": "extension_tag_issued", "title_order_id": title_order_id, "title_txn_id": rid,
                "tag_sequence": seq, "temp_tag_number": tag_no, "issued_date": today,
                "tag_expires_date": expires, "temp_tag_extensions_used": used + 1})


@tool(owner="user", rw="write")
def pay_title_late_penalty_3594d5af(ctx: ToolContext, title_order_id: str, amount: float) -> str:
    """The buyer pays, in person, the state's late-registration penalty on their title and registration
    order. One call books one payment from the buyer on the order as a state charge collected that is not
    a schedule fee, dated today, and adds the amount to the state fees Kestrel is holding on that order for
    the state. The buyer sees the payment on the order's history immediately; the receipt below confirms
    it was booked.

    Args:
        title_order_id: Id class — the reference number of the buyer's title and registration order, as
            shown by the title and registration order lookup for this buyer before the call.
        amount: Fixed-format class — the penalty the buyer pays now, in USD, a positive amount with 2
            decimal places (cents), already rounded to the cent; it is booked exactly as passed.

    Returns:
        A dict: status ("penalty_payment_recorded" when booked), title_txn_id (reference number of the new
        entry), title_order_id, fee_type (always "not_applicable", the penalty being no schedule fee),
        amount (USD with 2 decimal places as booked), txn_date (booking date, YYYY-MM-DD) and
        state_fees_held (USD with 2 decimal places now held on the order after this payment).
    """
    amt = round(float(amount), 2)
    order = (ctx.find("title_orders", title_order_id=title_order_id) or [{}])[0]
    rid = ctx.make_id("ttx_", title_order_id, amt, "late_penalty_payment")
    today = ctx.now()[:10]
    ctx.create("title_transactions", rid, title_txn_id=rid, title_order_id=title_order_id,
               customer_id=order.get("customer_id"), event_type="title_state_fee_collected", txn_date=today,
               amount=amt, fee_type="not_applicable", document_type="not_applicable", tag_sequence=0,
               temp_tag_number="", tag_expires_date="", reject_code="not_applicable",
               reimbursement_reason="not_applicable", document_format="not_applicable", document_date="",
               citation_number="", source_txn_id="")
    held = round(float(order.get("state_fees_held") or 0) + amt, 2)
    ctx.update("title_orders", title_order_id, state_fees_held=held)
    return str({"status": "penalty_payment_recorded", "title_txn_id": rid, "title_order_id": title_order_id,
                "fee_type": "not_applicable", "amount": amt, "txn_date": today, "state_fees_held": held})


@tool(owner="user", rw="write")
def pay_title_lien_charges_e09cfc3d(ctx: ToolContext, title_order_id: str, amount: float) -> str:
    """The buyer pays, in person, the state's charges for recording the lien on their title and
    registration order. One call books one payment from the buyer on the order as a lien recording fee
    collected, dated today, and adds the amount to the state fees Kestrel is holding on that order for the
    state. The buyer sees the payment on the order's history immediately; the receipt below confirms it
    was booked.

    Args:
        title_order_id: Id class — the reference number of the buyer's title and registration order, as
            shown by the title and registration order lookup for this buyer before the call.
        amount: Fixed-format class — the lien charges the buyer pays now, in USD, a positive amount with 2
            decimal places (cents), already rounded to the cent; it is booked exactly as passed.

    Returns:
        A dict: status ("lien_payment_recorded" when booked), title_txn_id (reference number of the new
        entry), title_order_id, fee_type (always "lien_recording_fee"), amount (USD with 2 decimal places
        as booked), txn_date (booking date, YYYY-MM-DD) and state_fees_held (USD with 2 decimal places now
        held on the order after this payment).
    """
    amt = round(float(amount), 2)
    order = (ctx.find("title_orders", title_order_id=title_order_id) or [{}])[0]
    rid = ctx.make_id("ttx_", title_order_id, amt, "lien_charges_payment")
    today = ctx.now()[:10]
    ctx.create("title_transactions", rid, title_txn_id=rid, title_order_id=title_order_id,
               customer_id=order.get("customer_id"), event_type="title_state_fee_collected", txn_date=today,
               amount=amt, fee_type="lien_recording_fee", document_type="not_applicable", tag_sequence=0,
               temp_tag_number="", tag_expires_date="", reject_code="not_applicable",
               reimbursement_reason="not_applicable", document_format="not_applicable", document_date="",
               citation_number="", source_txn_id="")
    held = round(float(order.get("state_fees_held") or 0) + amt, 2)
    ctx.update("title_orders", title_order_id, state_fees_held=held)
    return str({"status": "lien_payment_recorded", "title_txn_id": rid, "title_order_id": title_order_id,
                "fee_type": "lien_recording_fee", "amount": amt, "txn_date": today, "state_fees_held": held})


@tool(owner="agent", rw="write")
def resubmit_title_packet_8a13d7a9(ctx: ToolContext, title_order_id: str, purchase_order_id: str,
                                   remit_amount: float) -> str:
    """Send a title and registration packet that the state returned back to the state, with payment. One
    call makes the returned order ready again and submits it in the same action, so the order ends as
    submitted; it stamps today as its most recent submission date with a new state
    receipt number, books one remittance to the state for the amount passed, dated today, and clears the
    state fees held on the order to 0.00. The buyer can see the order as submitted at once; the receipt
    below gives the state receipt number and the amount remitted.

    Args:
        title_order_id: Id class — the reference number of the returned title and registration order, as
            shown by the title and registration order lookup for this buyer before the call.
        purchase_order_id: Id class — the reference number of the purchase order the vehicle was bought on,
            as shown on the title and registration order and by the purchase order lookup before the call.
        remit_amount: Fixed-format class — the total paid to the state with the packet, in USD, a positive
            amount with 2 decimal places (cents), already rounded to the cent; it is booked exactly as passed.

    Returns:
        A dict: status ("resubmitted" on success), title_order_id, purchase_order_id, title_txn_id
        (reference number of the remittance entry), dmv_transaction_number (the state's receipt number for
        this submission), submitted_date (YYYY-MM-DD), remit_amount (USD with 2 decimal places as booked)
        and state_fees_held (USD with 2 decimal places, 0.00 after the remittance).
    """
    amt = round(float(remit_amount), 2)
    order = (ctx.find("title_orders", title_order_id=title_order_id) or [{}])[0]
    today = ctx.now()[:10]
    rid = ctx.make_id("ttx_", title_order_id, purchase_order_id, amt, "resubmission")
    receipt = "DMV-" + ctx.make_id("", title_order_id, purchase_order_id, today, length=8).upper()
    ctx.create("title_transactions", rid, title_txn_id=rid, title_order_id=title_order_id,
               customer_id=order.get("customer_id"), event_type="title_state_fee_remitted", txn_date=today,
               amount=amt, fee_type="not_applicable", document_type="not_applicable", tag_sequence=0,
               temp_tag_number="", tag_expires_date="", reject_code="not_applicable",
               reimbursement_reason="not_applicable", document_format="not_applicable", document_date="",
               citation_number="", source_txn_id="")
    ctx.update("title_orders", title_order_id, status="submitted", submitted_date=today,
               dmv_transaction_number=receipt, state_fees_held=0.0)
    return str({"status": "resubmitted", "title_order_id": title_order_id, "purchase_order_id": purchase_order_id,
                "title_txn_id": rid, "dmv_transaction_number": receipt, "submitted_date": today,
                "remit_amount": amt, "state_fees_held": 0.0})


@tool(owner="agent", rw="write")
def reimburse_title_late_penalty_e7fb1913(ctx: ToolContext, title_order_id: str, citation_number: str,
                                          amount: float) -> str:
    """Pay the buyer a reimbursement toward a state late-registration penalty on a title and registration
    order. One call books one reimbursement paid to the buyer, dated today, against the state penalty
    notice whose number is passed, with the reason recorded as a state late-registration penalty. The buyer
    sees the reimbursement on the order's history at once; the receipt below confirms the payment.

    Args:
        title_order_id: Id class — the reference number of the title and registration order, as shown by
            the title and registration order lookup for this buyer before the call.
        citation_number: Verbatim class — the state penalty notice number exactly as printed on the notice
            and as shown on the state's return in the order's history, copied character for character
            with its letters, digits and hyphens, without translation, normalisation, summary, addition or
            deletion (verbatim).
        amount: Fixed-format class — the reimbursement paid, in USD, a positive amount with 2 decimal
            places (cents), already rounded to the cent; it is booked exactly as passed.

    Returns:
        A dict: status ("reimbursement_paid" on success), title_txn_id (reference number of the
        reimbursement entry), title_order_id, citation_number (as booked), reimbursement_reason (always
        "state_late_registration_penalty"), amount (USD with 2 decimal places) and txn_date (payment
        date, YYYY-MM-DD).
    """
    amt = round(float(amount), 2)
    order = (ctx.find("title_orders", title_order_id=title_order_id) or [{}])[0]
    today = ctx.now()[:10]
    rid = ctx.make_id("ttx_", title_order_id, citation_number, amt, "penalty_reimbursement")
    ctx.create("title_transactions", rid, title_txn_id=rid, title_order_id=title_order_id,
               customer_id=order.get("customer_id"), event_type="title_reimbursement_paid", txn_date=today,
               amount=amt, fee_type="not_applicable", document_type="not_applicable", tag_sequence=0,
               temp_tag_number="", tag_expires_date="", reject_code="not_applicable",
               reimbursement_reason="state_late_registration_penalty", document_format="not_applicable",
               document_date="", citation_number=citation_number, source_txn_id="")
    return str({"status": "reimbursement_paid", "title_txn_id": rid, "title_order_id": title_order_id,
                "citation_number": citation_number, "reimbursement_reason": "state_late_registration_penalty",
                "amount": amt, "txn_date": today})

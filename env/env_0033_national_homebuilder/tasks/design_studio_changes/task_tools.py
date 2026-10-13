"""Hidden task tools of the design_studio_changes difficulty (Design Studio Selections, Calloway Homes).

Each tool performs exactly one atomic write on one design studio file and returns a receipt. No tool
judges eligibility, prerequisites or amounts: the figures are worked out by the agent from the
published rules and the records, and passed in.
"""

from erlbench import ToolContext, tool


@tool(owner="agent", rw="write")
def record_change_order_fee_50efc86e(ctx: ToolContext, selection_id: str, change_order_number: str,
                                     change_order_reason: str, fee_amount: float) -> str:
    """Write the change order entry for a set of selection changes on one Design Studio Selections
    file, with the change order fee charged for it. One call books one change order entry on the
    file's design ledger (dated today, carrying the change order number, the reason and the fee) and
    adds the fee to the file's option total, the amount added to what the buyer owes at closing. A
    fee of 0.00 books a change order that carries no fee. The buyer sees the change order and its fee
    on the selection sheet and on the design ledger.

    Args:
        selection_id: Id class — the reference number of the Design Studio Selections file the change
            order belongs to, as returned by the design file lookup.
        change_order_number: Verbatim class — the change order number exactly as it is printed on
            the option lines of that change order in the design ledger, copied character for character with no added or removed spaces or
            letters (verbatim).
        change_order_reason: Enum class — why the change order is written: buyer_request when the
            buyer asked for the changes in the change order; builder_error when the change order
            corrects a mistake made by the design studio or by Calloway.
        fee_amount: Fixed-format class — the change order fee charged for this change order, in
            USD, 2 decimal places, rounded half up to the cent; 0.00 when the change order carries
            no fee.

    Returns:
        A dictionary receipt: design_event_id (text, the reference number of the change order entry
        just booked), change_order_number (text, as passed), change_order_reason (text, as passed),
        fee_amount (number, the fee booked in USD with 2 decimals), option_total (number, the file's
        option total in USD including this fee) and status ("recorded" when the change order
        entry was written).
    """
    fee = round(float(fee_amount), 2)
    rid = ctx.make_id("dco_", selection_id, change_order_number, change_order_reason, fee)
    file_rows = ctx.find("design_selections", selection_id=selection_id)
    customer_id = file_rows[0].get("customer_id") if file_rows else None
    ctx.create("design_events", rid, design_event_id=rid, selection_id=selection_id,
               customer_id=customer_id, event_type="design_change_order_recorded", amount=fee,
               change_order_number=change_order_number, change_order_reason=change_order_reason,
               event_date=ctx.now()[:10])
    new_total = None
    if file_rows:
        new_total = round(float(file_rows[0].get("option_total") or 0) + fee, 2)
        ctx.update("design_selections", selection_id, option_total=new_total)
    return str({"design_event_id": rid, "change_order_number": change_order_number,
                "change_order_reason": change_order_reason, "fee_amount": fee,
                "option_total": new_total, "status": "recorded"})


@tool(owner="agent", rw="write")
def book_studio_consult_fee_3108e630(ctx: ToolContext, selection_id: str, appointment_seq: int,
                                     fee_amount: float) -> str:
    """Book the design consultation fee for one design appointment as a studio fee line on a Design
    Studio Selections file. One call adds one design_consult_fee line to the file's selection sheet
    (dated on the date of the appointment it bills, tied to that appointment, with a new printed line
    number) and adds the fee
    to the file's option total, the amount added to what the buyer owes at closing. The buyer sees
    the fee line, its line number and its price on the selection sheet and on the design ledger.

    Args:
        selection_id: Id class — the reference number of the Design Studio Selections file the
            appointment was held on, as returned by the design file lookup.
        appointment_seq: Fixed-format class — the sequence number of the design appointment being
            billed, exactly as shown on that appointment's entry in the design ledger; an integer
            >= 1.
        fee_amount: Fixed-format class — the design consultation fee charged for that appointment,
            in USD, 2 decimal places, rounded half up to the cent.

    Returns:
        A dictionary receipt: design_event_id (text, the reference number of the fee line entry),
        event_date (text, YYYY-MM-DD, the date the fee line carries), option_line_ref (text, the line number printed for the new fee line, OPT-DSF- followed by
        five digits), appointment_seq (integer, the appointment billed), fee_amount (number, the fee
        booked in USD with 2 decimals), option_total (number, the file's option total in USD
        including this fee) and status ("booked" when the fee line was written).
    """
    fee = round(float(fee_amount), 2)
    seq = int(appointment_seq)
    rid = ctx.make_id("dcf_", selection_id, seq, fee)
    line_ref = f"OPT-DSF-{str(int(rid.split('_', 1)[-1][:10], 16))[-5:].rjust(5, '0')}"
    file_rows = ctx.find("design_selections", selection_id=selection_id)
    customer_id = file_rows[0].get("customer_id") if file_rows else None
    held = ctx.find("design_events", selection_id=selection_id, event_type="design_appointment_held",
                    appointment_seq=seq)
    fee_date = held[0].get("event_date") if held else ctx.now()[:10]
    ctx.create("design_events", rid, design_event_id=rid, selection_id=selection_id,
               customer_id=customer_id, event_type="design_option_added", amount=fee,
               option_line_ref=line_ref, option_code="STUDIO-CONSULT-FEE",
               option_category="design_consult_fee", selection_channel="studio",
               appointment_seq=seq, event_date=fee_date)
    new_total = None
    if file_rows:
        new_total = round(float(file_rows[0].get("option_total") or 0) + fee, 2)
        ctx.update("design_selections", selection_id, option_total=new_total)
    return str({"design_event_id": rid, "event_date": fee_date, "option_line_ref": line_ref, "appointment_seq": seq,
                "fee_amount": fee, "option_total": new_total, "status": "booked"})


@tool(owner="agent", rw="write")
def grant_goodwill_credit_33ff7b41(ctx: ToolContext, selection_id: str, change_order_number: str,
                                   credit_amount: float) -> str:
    """Grant builder goodwill design credit on a Design Studio Selections file for one change order
    that corrected a design studio or builder error. One call adds one builder goodwill credit grant
    to the file's design ledger (dated today, with a new printed credit memo number and the change
    order it compensates) and raises the file's design credit available by the amount granted. The
    buyer sees the credit memo and the higher design credit balance on the design file.

    Args:
        selection_id: Id class — the reference number of the Design Studio Selections file that
            receives the credit, as returned by the design file lookup.
        change_order_number: Verbatim class — the number of the error-correcting change order the
            credit compensates, exactly as printed on that change order's entry in the design ledger,
            copied character for character (verbatim).
        credit_amount: Fixed-format class — the builder goodwill credit granted, in USD, 2 decimal
            places, rounded half up to the cent.

    Returns:
        A dictionary receipt: design_event_id (text, the reference number of the credit grant entry),
        credit_reference (text, the printed credit memo number, DCM- followed by five digits),
        change_order_number (text, as passed), credit_amount (number, the credit granted in USD
        with 2 decimals), design_credit_balance (number, the file's design credit available in USD
        including this grant) and status ("granted" when the credit was written).
    """
    amount = round(float(credit_amount), 2)
    rid = ctx.make_id("dgw_", selection_id, change_order_number, amount)
    memo = f"DCM-{str(int(rid.split('_', 1)[-1][:10], 16))[-5:].rjust(5, '0')}"
    file_rows = ctx.find("design_selections", selection_id=selection_id)
    customer_id = file_rows[0].get("customer_id") if file_rows else None
    ctx.create("design_events", rid, design_event_id=rid, selection_id=selection_id,
               customer_id=customer_id, event_type="design_credit_granted", amount=amount,
               credit_source="builder_goodwill", credit_reference=memo,
               change_order_number=change_order_number, event_date=ctx.now()[:10])
    new_balance = None
    if file_rows:
        new_balance = round(float(file_rows[0].get("design_credit_balance") or 0) + amount, 2)
        ctx.update("design_selections", selection_id, design_credit_balance=new_balance)
    return str({"design_event_id": rid, "credit_reference": memo, "change_order_number": change_order_number,
                "credit_amount": amount, "design_credit_balance": new_balance, "status": "granted"})


@tool(owner="user", rw="write")
def pay_option_deposit_3846be30(ctx: ToolContext, selection_id: str, option_line_ref: str,
                                payment_method: str, amount: float) -> str:
    """Pay an option deposit on your own Design Studio Selections file. One call posts one option
    deposit payment from you (dated today, with the payment method you choose and the option line
    whose deposit it settles), prints a new Calloway receipt number for it and raises the option
    deposits Calloway holds on the file by the amount paid. You see the receipt number and the new
    deposits-held figure straight away, and the payment is shown on the design ledger.

    Args:
        selection_id: Id class — the reference number of your Design Studio Selections file, as
            given to you by the representative.
        option_line_ref: Verbatim class — the line number of the option line whose deposit this
            payment settles, exactly as printed on your selection sheet and read to you by the
            representative, copied character for character (verbatim).
        payment_method: Enum class — how you pay: card when you pay with a debit or credit card;
            ach when you pay by electronic transfer from your bank account; check when you pay by
            paper check; wire when you pay by bank wire transfer.
        amount: Fixed-format class — the amount you pay, in USD, 2 decimal places, rounded half up
            to the cent.

    Returns:
        A dictionary receipt: design_event_id (text, the reference number of the payment entry),
        payment_reference (text, the Calloway receipt number printed for this payment, RCPT-DS-
        followed by five digits), option_line_ref (text, as passed), payment_method (text, as
        passed), amount (number, the amount paid in USD with 2 decimals), option_deposit_held
        (number, the option deposits held on the file in USD including this payment) and status
        ("posted" when the payment was recorded).
    """
    paid = round(float(amount), 2)
    rid = ctx.make_id("ddp_", selection_id, option_line_ref, payment_method, paid)
    receipt = f"RCPT-DS-{str(int(rid.split('_', 1)[-1][:10], 16))[-5:].rjust(5, '0')}"
    file_rows = ctx.find("design_selections", selection_id=selection_id)
    customer_id = file_rows[0].get("customer_id") if file_rows else None
    ctx.create("design_events", rid, design_event_id=rid, selection_id=selection_id,
               customer_id=customer_id, event_type="design_deposit_paid", amount=paid,
               payment_method=payment_method, payment_reference=receipt,
               option_line_ref=option_line_ref, event_date=ctx.now()[:10])
    new_held = None
    if file_rows:
        new_held = round(float(file_rows[0].get("option_deposit_held") or 0) + paid, 2)
        ctx.update("design_selections", selection_id, option_deposit_held=new_held)
    return str({"design_event_id": rid, "payment_reference": receipt, "option_line_ref": option_line_ref,
                "payment_method": payment_method, "amount": paid, "option_deposit_held": new_held,
                "status": "posted"})


@tool(owner="agent", rw="write")
def book_returned_payment_fee_69a7241d(ctx: ToolContext, selection_id: str, source_payment_ref: str,
                                       fee_amount: float) -> str:
    """Book the returned payment fee for one option deposit payment that came back unpaid on a Design
    Studio Selections file. One call adds one returned_payment_fee line to the file's selection sheet
    (dated on the date Calloway was notified of that return, carrying the receipt number of the
    returned payment and a new printed line number) and adds the fee to the file's option total, the
    amount added to what the buyer owes at closing. The buyer sees the fee line, its line number and
    its price on the selection sheet and on the design ledger.

    Args:
        selection_id: Id class — the reference number of the Design Studio Selections file the
            returned payment was made on, as returned by the design file lookup.
        source_payment_ref: Verbatim class — the Calloway receipt number of the option deposit
            payment that was returned, exactly as printed on the returned-payment entry of the design
            ledger, copied character for character (verbatim).
        fee_amount: Fixed-format class — the returned payment fee charged, in USD, 2 decimal places,
            rounded half up to the cent.

    Returns:
        A dictionary receipt: design_event_id (text, the reference number of the fee line entry),
        option_line_ref (text, the line number printed for the new fee line, OPT-DSR- followed by
        five digits), source_payment_ref (text, as passed), event_date (text, YYYY-MM-DD, the date
        the fee line carries), fee_amount (number, the fee booked in USD with 2 decimals),
        option_total (number, the file's option total in USD including this fee) and status
        ("booked" when the fee line was written).
    """
    fee = round(float(fee_amount), 2)
    rid = ctx.make_id("drf_", selection_id, source_payment_ref, fee)
    line_ref = f"OPT-DSR-{str(int(rid.split('_', 1)[-1][:10], 16))[-5:].rjust(5, '0')}"
    file_rows = ctx.find("design_selections", selection_id=selection_id)
    customer_id = file_rows[0].get("customer_id") if file_rows else None
    returned = ctx.find("design_events", selection_id=selection_id, event_type="design_payment_returned",
                        source_payment_ref=source_payment_ref)
    fee_date = returned[0].get("event_date") if returned else ctx.now()[:10]
    ctx.create("design_events", rid, design_event_id=rid, selection_id=selection_id,
               customer_id=customer_id, event_type="design_option_added", amount=fee,
               option_line_ref=line_ref, option_code="FEE-RETURNED-PAYMENT",
               option_category="returned_payment_fee", selection_channel="studio",
               source_payment_ref=source_payment_ref, event_date=fee_date)
    new_total = None
    if file_rows:
        new_total = round(float(file_rows[0].get("option_total") or 0) + fee, 2)
        ctx.update("design_selections", selection_id, option_total=new_total)
    return str({"design_event_id": rid, "option_line_ref": line_ref, "source_payment_ref": source_payment_ref,
                "event_date": fee_date, "fee_amount": fee, "option_total": new_total, "status": "booked"})


@tool(owner="agent", rw="write")
def return_line_allowance_4e51d426(ctx: ToolContext, selection_id: str, source_line_ref: str,
                                   credit_amount: float) -> str:
    """Return package allowance to a Design Studio Selections file for one option line that was
    removed while package allowance was applied to it. One call adds one package allowance credit
    entry to the file's design ledger (dated today, carrying the line number of the removed line and
    a new printed credit memo number) and raises the file's design credit available by the amount
    returned. The buyer sees the credit memo and the higher design credit balance on the design file.

    Args:
        selection_id: Id class — the reference number of the Design Studio Selections file that
            receives the returned allowance, as returned by the design file lookup.
        source_line_ref: Verbatim class — the line number of the removed option line the allowance
            had been applied to, exactly as printed on its removal entry in the design ledger, copied
            character for character (verbatim).
        credit_amount: Fixed-format class — the package allowance returned to the file, in USD,
            2 decimal places, rounded half up to the cent.

    Returns:
        A dictionary receipt: design_event_id (text, the reference number of the credit entry),
        credit_reference (text, the printed credit memo number, DCM- followed by five digits),
        source_line_ref (text, as passed), credit_amount (number, the allowance returned in USD
        with 2 decimals), design_credit_balance (number, the file's design credit available in USD
        including this return) and status ("returned" when the credit was written).
    """
    amount = round(float(credit_amount), 2)
    rid = ctx.make_id("dar_", selection_id, source_line_ref, amount)
    memo = f"DCM-{str(int(rid.split('_', 1)[-1][:10], 16))[-5:].rjust(5, '0')}"
    file_rows = ctx.find("design_selections", selection_id=selection_id)
    customer_id = file_rows[0].get("customer_id") if file_rows else None
    ctx.create("design_events", rid, design_event_id=rid, selection_id=selection_id,
               customer_id=customer_id, event_type="design_credit_granted", amount=amount,
               credit_source="package_allowance", credit_reference=memo,
               source_line_ref=source_line_ref, event_date=ctx.now()[:10])
    new_balance = None
    if file_rows:
        new_balance = round(float(file_rows[0].get("design_credit_balance") or 0) + amount, 2)
        ctx.update("design_selections", selection_id, design_credit_balance=new_balance)
    return str({"design_event_id": rid, "credit_reference": memo, "source_line_ref": source_line_ref,
                "credit_amount": amount, "design_credit_balance": new_balance, "status": "returned"})


@tool(owner="user", rw="write")
def reinstate_option_line_5b4fa2c4(ctx: ToolContext, selection_id: str, source_line_ref: str,
                                   change_order_number: str, appointment_seq: int, price: float) -> str:
    """Put a removed option line back on your own Design Studio Selections file through the buyer
    portal. One call adds one option line to your selection sheet (dated today, with the catalog code
    and category of the removed line it reinstates, the change order it belongs to, the selection
    appointment it is recorded against and a new printed line number) at the price you enter, and adds that
    price to the file's option total, the amount added to what you owe at closing. You see the new
    line number and price on your selection sheet straight away.

    Args:
        selection_id: Id class — the reference number of your Design Studio Selections file, as
            given to you by the representative.
        source_line_ref: Verbatim class — the line number of the removed option line you are putting
            back, exactly as printed on your selection sheet and read to you by the representative,
            copied character for character (verbatim).
        change_order_number: Verbatim class — the change order number the line is written under,
            exactly as read to you by the representative from your design ledger, copied character
            for character (verbatim).
        appointment_seq: Fixed-format class — the sequence number of the most recent selection
            appointment on your file, the appointment the reinstated line is recorded against, as read
            to you by the representative; an integer >= 1.
        price: Fixed-format class — the price of the reinstated line, in USD, 2 decimal places,
            rounded half up to the cent.

    Returns:
        A dictionary receipt: design_event_id (text, the reference number of the new line entry),
        option_line_ref (text, the line number printed for the reinstated line, OPT-DSI- followed by
        five digits), source_line_ref (text, as passed), option_code (text, the catalog code carried
        over from the removed line), price (number, the price booked in USD with 2 decimals),
        option_total (number, the file's option total in USD including this line) and status
        ("reinstated" when the line was written).
    """
    amount = round(float(price), 2)
    seq = int(appointment_seq)
    rid = ctx.make_id("dri_", selection_id, source_line_ref, change_order_number, seq, amount)
    line_ref = f"OPT-DSI-{str(int(rid.split('_', 1)[-1][:10], 16))[-5:].rjust(5, '0')}"
    file_rows = ctx.find("design_selections", selection_id=selection_id)
    customer_id = file_rows[0].get("customer_id") if file_rows else None
    source = ctx.find("design_events", selection_id=selection_id, event_type="design_option_added",
                      option_line_ref=source_line_ref)
    code = source[0].get("option_code") if source else None
    category = source[0].get("option_category") if source else None
    ctx.create("design_events", rid, design_event_id=rid, selection_id=selection_id,
               customer_id=customer_id, event_type="design_option_added", amount=amount,
               option_line_ref=line_ref, option_code=code, option_category=category,
               selection_channel="portal", change_order_number=change_order_number,
               appointment_seq=seq, source_line_ref=source_line_ref, event_date=ctx.now()[:10])
    new_total = None
    if file_rows:
        new_total = round(float(file_rows[0].get("option_total") or 0) + amount, 2)
        ctx.update("design_selections", selection_id, option_total=new_total)
    return str({"design_event_id": rid, "option_line_ref": line_ref, "source_line_ref": source_line_ref,
                "option_code": code, "price": amount, "option_total": new_total, "status": "reinstated"})

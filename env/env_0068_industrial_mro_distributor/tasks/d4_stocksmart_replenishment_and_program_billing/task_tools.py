"""Hidden task tools of d4_stocksmart_replenishment_and_program_billing (StockSmart Vendor-Managed Inventory Program).

Each tool performs one atomic StockSmart booking with the values the agent (or the customer) has already
worked out; no tool checks eligibility, ordering or any prerequisite.
"""

from erlbench import ToolContext, tool


class _Refs:
    """Pure formatting helpers shared by the tools (not tools themselves)."""

    @staticmethod
    def bin_request(ctx: ToolContext, *parts) -> str:
        digest = ctx.make_id("vbr_", *parts)
        return "VBR-4" + str(int(digest[-10:], 16) % 100000).zfill(5)


@tool(owner="user", rw="write")
def submit_vended_item_bin_request_0334ff8e(ctx: ToolContext, vmi_program_id: str, bin_label: str, sku: str,
                                            special_stock: bool, max_qty: int) -> str:
    """The customer files, in person, its own written request for a new consigned StockSmart bin on one of its programs.

    One call books a single new-bin entry on the program's bin history: the bin label, the item, whether
    the item is non-catalog special stock, and the fill-to level the bin is filled to. The bin is booked as
    a consigned bin (Corbett-owned stock billed on consumption), not flagged critical, and with a reorder
    point of 0, since the request itself names no reorder point. The entry is effective today and carries a
    request reference of the form VBR-NNNNNN. Success is the receipt below with status recorded.

    Args:
        vmi_program_id: Id class — the reference number of the customer's StockSmart program the bin is added to, read from the StockSmart program lookup.
        bin_label: Verbatim class — the storeroom location label the customer gives for the new bin, copied character for character exactly as the customer says it, with no reformatting (verbatim).
        sku: Verbatim class — the Corbett item number the bin will hold, copied character for character from the item number shown on the customer's VendPoint selection or vend records, preserving every digit (verbatim).
        special_stock: Enum class — true when the item is a non-catalog special item Corbett stocks only for this customer, as flagged on its VendPoint selection; false when the item is a regular Corbett catalog item.
        max_qty: Fixed-format class — the fill-to level of the new bin, a whole number in integer units of the item, 1 or more.

    Returns:
        A dictionary rendered as text with: status ("recorded" on success); vmi_bin_id (reference number of the new bin entry); change_reference (the request reference, format VBR-NNNNNN); bin_label; sku; consigned (always True); min_qty (always 0 on this request); max_qty (integer units); event_date (effective date, YYYY-MM-DD).
    """
    program = ctx.find("vmi_programs", vmi_program_id=vmi_program_id)
    customer_id = program[0].get("customer_id") if program else ""
    ref = _Refs.bin_request(ctx, vmi_program_id, bin_label, sku, special_stock, max_qty)
    rid = ctx.make_id("vbn_", vmi_program_id, bin_label, sku, special_stock, max_qty)
    day = ctx.now()[:10]
    ctx.create("vmi_bins", rid, vmi_bin_id=rid, vmi_program_id=vmi_program_id, customer_id=customer_id,
               event_type="vmi_bin_set", bin_label=bin_label, sku=sku, special_stock=bool(special_stock),
               critical_item=False, consigned=True, min_qty=0, max_qty=int(max_qty), change_type="new_bin",
               removal_reason="none", change_reference=ref, event_date=day)
    return str({"status": "recorded", "vmi_bin_id": rid, "change_reference": ref, "bin_label": bin_label, "sku": sku,
                "consigned": True, "min_qty": 0, "max_qty": int(max_qty), "event_date": day})


@tool(owner="agent", rw="write")
def record_consigned_reorder_point_33b5bdc5(ctx: ToolContext, vmi_program_id: str, bin_label: str, sku: str,
                                            special_stock: bool, critical_item: bool, max_qty: int,
                                            min_qty: int) -> str:
    """Corbett records the reorder point of one consigned StockSmart bin as a par level entry on the program's bin history.

    One call books a single par change entry for the bin, effective today: the bin stays consigned, keeps the
    item, special-stock and critical flags and the fill-to level passed in, and takes the reorder point passed
    in (the level at or below which the bin is refilled). Corbett's own entries carry a review reference of the
    form VBR-NNNNNN. Success is the receipt below with status recorded.

    Args:
        vmi_program_id: Id class — the reference number of the StockSmart program that holds the bin, read from the StockSmart program lookup.
        bin_label: Verbatim class — the bin label exactly as it appears on the bin's latest entry in the bin history, copied character for character (verbatim).
        sku: Verbatim class — the Corbett item number exactly as it appears on the bin's latest entry in the bin history, copied character for character (verbatim).
        special_stock: Enum class — true when the bin's latest entry flags the item as non-catalog special stock; false when it does not.
        critical_item: Enum class — true when the bin's latest entry flags the bin critical; false when it does not.
        max_qty: Fixed-format class — the bin's fill-to level, a whole number in integer units, as it stands on the bin's latest entry.
        min_qty: Fixed-format class — the reorder point being recorded, a whole number in integer units of the item, 0 or more.

    Returns:
        A dictionary rendered as text with: status ("recorded" on success); vmi_bin_id (reference number of the par entry); change_reference (format VBR-NNNNNN); bin_label; sku; min_qty and max_qty (integer units); consigned (always True); event_date (YYYY-MM-DD).
    """
    program = ctx.find("vmi_programs", vmi_program_id=vmi_program_id)
    customer_id = program[0].get("customer_id") if program else ""
    ref = _Refs.bin_request(ctx, "rop", vmi_program_id, bin_label, sku, min_qty, max_qty)
    rid = ctx.make_id("vbp_", vmi_program_id, bin_label, sku, special_stock, critical_item, max_qty, min_qty)
    day = ctx.now()[:10]
    ctx.create("vmi_bins", rid, vmi_bin_id=rid, vmi_program_id=vmi_program_id, customer_id=customer_id,
               event_type="vmi_bin_set", bin_label=bin_label, sku=sku, special_stock=bool(special_stock),
               critical_item=bool(critical_item), consigned=True, min_qty=int(min_qty), max_qty=int(max_qty),
               change_type="par_change", removal_reason="none", change_reference=ref, event_date=day)
    return str({"status": "recorded", "vmi_bin_id": rid, "change_reference": ref, "bin_label": bin_label, "sku": sku,
                "min_qty": int(min_qty), "max_qty": int(max_qty), "consigned": True, "event_date": day})


@tool(owner="agent", rw="write")
def stock_opening_consignment_2b5b5df3(ctx: ToolContext, vmi_program_id: str, activity_reference: str, bin_label: str,
                                       sku: str, quantity: int, unit_price: float) -> str:
    """Corbett books Corbett-owned consigned stock placed into one consigned StockSmart bin at a service visit.

    One call books a single consigned-stocking line for the bin at the visit given: the units placed, the
    contract unit price they are carried at and their value (units times unit price, rounded half up to the
    cent). The program's consigned stock value rises by that value. The line is dated today. Success is the
    receipt below with status recorded.

    Args:
        vmi_program_id: Id class — the reference number of the StockSmart program that holds the bin, read from the StockSmart program lookup.
        activity_reference: Verbatim class — the reference of the service visit at which the stock is placed, copied character for character from the visit line in the program activity history (format VV-NNNNNN) (verbatim).
        bin_label: Verbatim class — the consigned bin's label exactly as it appears on its entry in the bin history, copied character for character (verbatim).
        sku: Verbatim class — the Corbett item number exactly as it appears on the bin's entry in the bin history, copied character for character (verbatim).
        quantity: Fixed-format class — the units placed in the bin, a whole number in integer units, 1 or more.
        unit_price: Fixed-format class — the contract unit price of the item in USD, 4 decimal places, as shown on the item's contract price line.

    Returns:
        A dictionary rendered as text with: status ("recorded" on success); vmi_activity_id (reference number of the stocking line); activity_reference; bin_label; sku; quantity (integer units); unit_price (USD, 4 decimal places); extended_amount (USD, 2 decimal places); consigned_stock_value (the program's consigned stock value including this booking, USD, 2 decimal places); event_date (YYYY-MM-DD).
    """
    program = ctx.find("vmi_programs", vmi_program_id=vmi_program_id)
    customer_id = program[0].get("customer_id") if program else ""
    price = round(float(unit_price), 4)
    value = round(int(quantity) * price + 1e-9, 2)
    rid = ctx.make_id("vcs_", vmi_program_id, activity_reference, bin_label, sku, quantity, unit_price)
    day = ctx.now()[:10]
    ctx.create("vmi_activity", rid, vmi_activity_id=rid, vmi_program_id=vmi_program_id, customer_id=customer_id,
               event_type="vmi_consignment_stocked", activity_reference=activity_reference, visit_type="none",
               bin_label=bin_label, sku=sku, quantity=int(quantity), unit_price=price, extended_amount=value,
               freight_amount=0.0, critical_item=False, billing_period="", fee_type="none", pause_start_date="",
               pause_end_date="", pause_reason="none", event_date=day)
    balance = round(float((program[0].get("consigned_stock_value") if program else 0) or 0) + value, 2)
    ctx.update("vmi_programs", vmi_program_id, consigned_stock_value=balance)
    return str({"status": "recorded", "vmi_activity_id": rid, "activity_reference": activity_reference,
                "bin_label": bin_label, "sku": sku, "quantity": int(quantity), "unit_price": price,
                "extended_amount": value, "consigned_stock_value": balance, "event_date": day})


@tool(owner="user", rw="write")
def submit_critical_bin_request_f65e9169(ctx: ToolContext, vmi_program_id: str, bin_label: str, sku: str, special_stock: bool,
                                         consigned: bool, critical_item: bool, max_qty: int) -> str:
    """The customer files, in person, its own written request setting the customer-owned fill-to level of one of its StockSmart bins, and whether the bin is flagged critical.

    One call books a single par level entry on the program's bin history, effective today: the bin keeps its
    label, item, special-stock flag and the consigned flag passed in, takes the fill-to level passed in and the
    critical flag the customer chooses, and carries a reorder point of 0, since the request itself names no
    reorder point. The entry carries a request reference of the form VBR-NNNNNN. Success is the receipt below
    with status recorded.

    Args:
        vmi_program_id: Id class — the reference number of the customer's StockSmart program that holds the bin, read from the StockSmart program lookup.
        bin_label: Verbatim class — the bin label exactly as it appears on the bin's entries in the bin history, copied character for character (verbatim).
        sku: Verbatim class — the Corbett item number exactly as it appears on the bin's entries in the bin history, copied character for character (verbatim).
        special_stock: Enum class — true when the bin's latest entry flags the item as non-catalog special stock; false when it does not.
        consigned: Enum class — true when the bin's latest entry still shows the bin as consigned; false when it already shows it customer-owned.
        critical_item: Enum class — true when the customer asks for the bin to be flagged critical; false when the customer does not.
        max_qty: Fixed-format class — the customer-owned fill-to level of the bin, a whole number in integer units, 1 or more.

    Returns:
        A dictionary rendered as text with: status ("recorded" on success); vmi_bin_id (reference number of the par entry); change_reference (format VBR-NNNNNN); bin_label; sku; critical_item (true or false); consigned (true or false); min_qty (always 0 on this request); max_qty (integer units); event_date (YYYY-MM-DD).
    """
    program = ctx.find("vmi_programs", vmi_program_id=vmi_program_id)
    customer_id = program[0].get("customer_id") if program else ""
    ref = _Refs.bin_request(ctx, "crit", vmi_program_id, bin_label, sku, critical_item, max_qty)
    rid = ctx.make_id("vbc_", vmi_program_id, bin_label, sku, special_stock, consigned, critical_item, max_qty)
    day = ctx.now()[:10]
    ctx.create("vmi_bins", rid, vmi_bin_id=rid, vmi_program_id=vmi_program_id, customer_id=customer_id,
               event_type="vmi_bin_set", bin_label=bin_label, sku=sku, special_stock=bool(special_stock),
               critical_item=bool(critical_item), consigned=bool(consigned), min_qty=0, max_qty=int(max_qty),
               change_type="par_change", removal_reason="none", change_reference=ref, event_date=day)
    return str({"status": "recorded", "vmi_bin_id": rid, "change_reference": ref, "bin_label": bin_label, "sku": sku,
                "critical_item": bool(critical_item), "consigned": bool(consigned), "min_qty": 0, "max_qty": int(max_qty),
                "event_date": day})


@tool(owner="agent", rw="write")
def record_customer_owned_conversion_b1c25ecb(ctx: ToolContext, vmi_program_id: str, bin_label: str, sku: str,
                                              special_stock: bool, critical_item: bool, max_qty: int, min_qty: int) -> str:
    """Corbett records the conversion of one StockSmart bin from consigned to customer-owned replenishment as a par level entry on the program's bin history.

    One call books a single par level entry, effective today, that shows the bin as no longer consigned: it
    keeps the item, the special-stock and critical flags and the fill-to level passed in, and takes the
    customer-owned reorder point passed in. Corbett's entries carry a reference of the form VBR-NNNNNN.
    Success is the receipt below with status recorded.

    Args:
        vmi_program_id: Id class — the reference number of the StockSmart program that holds the bin, read from the StockSmart program lookup.
        bin_label: Verbatim class — the bin label exactly as it appears on the bin's latest entry in the bin history, copied character for character (verbatim).
        sku: Verbatim class — the Corbett item number exactly as it appears on the bin's latest entry, copied character for character (verbatim).
        special_stock: Enum class — true when the bin's latest entry flags the item as non-catalog special stock; false when it does not.
        critical_item: Enum class — true when the bin's latest entry flags the bin critical; false when it does not.
        max_qty: Fixed-format class — the bin's fill-to level as it stands on its latest entry, a whole number in integer units.
        min_qty: Fixed-format class — the customer-owned reorder point being recorded, a whole number in integer units, 0 or more.

    Returns:
        A dictionary rendered as text with: status ("recorded" on success); vmi_bin_id (reference number of the conversion entry); change_reference (format VBR-NNNNNN); bin_label; sku; consigned (always false); min_qty and max_qty (integer units); event_date (YYYY-MM-DD).
    """
    program = ctx.find("vmi_programs", vmi_program_id=vmi_program_id)
    customer_id = program[0].get("customer_id") if program else ""
    ref = _Refs.bin_request(ctx, "conv", vmi_program_id, bin_label, sku, min_qty, max_qty)
    rid = ctx.make_id("vbv_", vmi_program_id, bin_label, sku, special_stock, critical_item, max_qty, min_qty)
    day = ctx.now()[:10]
    ctx.create("vmi_bins", rid, vmi_bin_id=rid, vmi_program_id=vmi_program_id, customer_id=customer_id,
               event_type="vmi_bin_set", bin_label=bin_label, sku=sku, special_stock=bool(special_stock),
               critical_item=bool(critical_item), consigned=False, min_qty=int(min_qty), max_qty=int(max_qty),
               change_type="par_change", removal_reason="none", change_reference=ref, event_date=day)
    return str({"status": "recorded", "vmi_bin_id": rid, "change_reference": ref, "bin_label": bin_label, "sku": sku,
                "consigned": False, "min_qty": int(min_qty), "max_qty": int(max_qty), "event_date": day})


@tool(owner="agent", rw="write")
def book_converted_bin_fill_19b3cec5(ctx: ToolContext, vmi_program_id: str, customer_id: str, activity_reference: str, bin_label: str, sku: str,
                                     critical_item: bool, quantity: int, unit_price: float) -> str:
    """Corbett books one customer-owned replenishment line: units delivered into one StockSmart bin at a service visit.

    One call books a single replenishment-delivered line for the bin at the visit given: the units delivered,
    the billing unit price, their value (units times unit price, rounded half up to the cent) and whether the
    bin is flagged critical. The line is dated today. Success is the receipt below with status recorded.

    Args:
        vmi_program_id: Id class — the reference number of the StockSmart program that holds the bin, read from the StockSmart program lookup.
        customer_id: Id class — the customer reference number of the account holder whose bin is replenished, read from the customer profile lookup.
        activity_reference: Verbatim class — the reference of the service visit the delivery belongs to, copied character for character from the visit line in the program activity history (format VV-NNNNNN) (verbatim).
        bin_label: Verbatim class — the bin label exactly as it appears on the bin's entries in the bin history, copied character for character (verbatim).
        sku: Verbatim class — the Corbett item number exactly as it appears on the bin's entries, copied character for character (verbatim).
        critical_item: Enum class — true when the bin's latest entry flags the bin critical; false when it does not.
        quantity: Fixed-format class — the units delivered into the bin, a whole number in integer units, 1 or more.
        unit_price: Fixed-format class — the billing unit price of the item in USD, 4 decimal places.

    Returns:
        A dictionary rendered as text with: status ("recorded" on success); vmi_activity_id (reference number of the delivery line); activity_reference; bin_label; sku; quantity (integer units); unit_price (USD, 4 decimal places); extended_amount (USD, 2 decimal places); critical_item (true or false); event_date (YYYY-MM-DD).
    """
    price = round(float(unit_price), 4)
    value = round(int(quantity) * price + 1e-9, 2)
    rid = ctx.make_id("vrd_", vmi_program_id, customer_id, activity_reference, bin_label, sku, critical_item, quantity, unit_price)
    day = ctx.now()[:10]
    ctx.create("vmi_activity", rid, vmi_activity_id=rid, vmi_program_id=vmi_program_id, customer_id=customer_id,
               event_type="vmi_replenishment_delivered", activity_reference=activity_reference, visit_type="none",
               bin_label=bin_label, sku=sku, quantity=int(quantity), unit_price=price, extended_amount=value,
               freight_amount=0.0, critical_item=bool(critical_item), billing_period="", fee_type="none",
               pause_start_date="", pause_end_date="", pause_reason="none", event_date=day)
    return str({"status": "recorded", "vmi_activity_id": rid, "activity_reference": activity_reference,
                "bin_label": bin_label, "sku": sku, "quantity": int(quantity), "unit_price": price,
                "extended_amount": value, "critical_item": bool(critical_item), "event_date": day})

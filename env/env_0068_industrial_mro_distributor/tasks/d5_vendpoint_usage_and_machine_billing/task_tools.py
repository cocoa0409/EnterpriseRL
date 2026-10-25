"""Hidden task tools of d5_vendpoint_usage_and_machine_billing (VendPoint Industrial Vending Program).

Each tool performs one atomic write on VendPoint records with the values the agent (or the customer)
passes in; no tool checks eligibility, prerequisites or amounts.
"""

from erlbench import ToolContext, tool


@tool(owner="agent", rw="write")
def resize_selection_par_58ce1bb4(ctx: ToolContext, vending_machine_id: str, slot_label: str, sku: str,
                                  par_qty: int) -> str:
    """Record a par change made by Corbett on one selection of a VendPoint machine: a new selection history
    entry sets the par quantity of the named selection and item to the value given, marked as a Corbett
    change of type par change, dated today and carrying the next planogram request reference in sequence,
    one above the highest planogram request reference on record. The
    item's product category and special-item flag are carried over from the existing entries of that
    selection and item. Success is a receipt naming the new entry and its reference.

    Args:
        vending_machine_id: Id class — the reference number of the VendPoint machine placement whose selection is re-sized, as returned by the machine lookup.
        slot_label: Verbatim class — the label of the selection (door, coil or bay) exactly as it appears on the machine's selection history entries; copy it character for character with no change to letters, digits or punctuation (verbatim).
        sku: Verbatim class — the Corbett item number held in that selection exactly as it appears on the machine's selection history entries; copy it character for character with no change to letters, digits or punctuation (verbatim).
        par_qty: Fixed-format class — the new par quantity of the selection, a whole number of integer units of the item, zero or more, with no decimal part.

    Returns:
        A dictionary rendered as text with: status (the text "par_changed" when the entry was recorded),
        vending_slot_id (reference number of the new selection history entry), vending_machine_id (the machine
        reference echoed back), slot_label (the selection label echoed back), sku (the item number echoed back),
        par_qty (the new par as an integer number of units), change_reference (the planogram request reference
        issued for the change, letters VPC, a hyphen and six digits) and effective_date (the date of the entry
        in YYYY-MM-DD form).
    """
    rid = ctx.make_id("vps_", vending_machine_id, slot_label, sku, par_qty)
    numbers = [int(str(r.get("change_reference", ""))[4:]) for r in ctx.find("vending_planogram")
               if str(r.get("change_reference", "")).startswith("VPC-") and str(r.get("change_reference", ""))[4:].isdigit()]
    reference = "VPC-" + str((max(numbers) if numbers else 0) + 1).zfill(6)
    machines = ctx.find("vending_machines", vending_machine_id=vending_machine_id)
    customer_id = machines[0].get("customer_id", "") if machines else ""
    prior = ctx.find("vending_planogram", vending_machine_id=vending_machine_id, slot_label=slot_label, sku=sku)
    prior = sorted(prior, key=lambda r: (str(r.get("event_date")), str(r.get("change_reference"))))
    category = prior[-1].get("product_category", "") if prior else ""
    special = prior[-1].get("special_item", False) if prior else False
    today = ctx.now()[:10]
    ctx.create("vending_planogram", rid, vending_slot_id=rid, vending_machine_id=vending_machine_id,
               customer_id=customer_id, event_type="vending_selection_set", slot_label=slot_label, sku=sku,
               product_category=category, par_qty=int(par_qty), special_item=special, change_type="par_change",
               change_source="corbett", removal_reason="none", change_reference=reference, event_date=today)
    return str({"status": "par_changed", "vending_slot_id": rid, "vending_machine_id": vending_machine_id,
                "slot_label": slot_label, "sku": sku, "par_qty": int(par_qty), "change_reference": reference,
                "effective_date": today})



class _Ledger:
    """Pure-Python reference and rounding helpers shared by the tools below."""

    @staticmethod
    def next_reference(ctx: ToolContext, table: str, field: str, prefix: str, start: int) -> str:
        numbers = [int(str(r.get(field, ""))[len(prefix):]) for r in ctx.find(table)
                   if str(r.get(field, "")).startswith(prefix) and str(r.get(field, ""))[len(prefix):].isdigit()]
        return prefix + str((max(numbers) if numbers else start) + 1)

    @staticmethod
    def cents_half_up(value: float) -> float:
        return int(float(value) * 100 + 0.5 + 1e-9) / 100.0

@tool(owner="user", rw="write")
def return_startup_item_units_bfc1c22c(ctx: ToolContext, vending_machine_id: str, original_txn_reference: str,
                                       quantity: int, unit_credit: float) -> str:
    """Return unused units of a vended item into a VendPoint machine for credit: a new machine transaction
    of type item returned is recorded against the named original vend, dated today, carrying the next return
    transaction number in sequence, one above the highest return transaction number on record. The item,
    product category, badge, cost center and unit price are copied from the original vend; the units returned
    are the quantity given, and the credit value is the quantity multiplied by the unit credit given, rounded
    half up to the cent. The credit value is added to the machine's consigned stock value. Success is a
    receipt naming the new transaction and its credit value.

    Args:
        vending_machine_id: Id class — the reference number of the VendPoint machine placement the units are returned into, as returned by the machine lookup.
        original_txn_reference: Verbatim class — the vend transaction number of the original vend exactly as it appears on the machine's transactions; copy it character for character with no change to letters, digits or punctuation (verbatim).
        quantity: Fixed-format class — the number of units returned, a whole number of integer units greater than zero, with no decimal part.
        unit_credit: Fixed-format class — the credit for each unit returned, a decimal amount in US dollars (USD), zero or more, with 2 decimal places, rounded half up to the cent.

    Returns:
        A dictionary rendered as text with: status (the text "returned" when the transaction was recorded),
        vending_txn_id (reference number of the new transaction), txn_reference (the return transaction number,
        letters VR, a hyphen and digits), original_txn_reference (echoed back), sku (the item copied from the
        original vend), quantity (units returned as an integer), unit_credit (echoed back as a decimal amount in
        USD), extended_amount (the credit value in USD with two decimals) and event_date (today in YYYY-MM-DD
        form).
    """
    rid = ctx.make_id("vrt_", vending_machine_id, original_txn_reference, quantity, unit_credit)
    reference = _Ledger.next_reference(ctx, "vending_transactions", "txn_reference", "VR-", 5000000)
    machines = ctx.find("vending_machines", vending_machine_id=vending_machine_id)
    machine = machines[0] if machines else {}
    vends = ctx.find("vending_transactions", vending_machine_id=vending_machine_id, txn_reference=original_txn_reference)
    vend = vends[0] if vends else {}
    amount = _Ledger.cents_half_up(int(quantity) * float(unit_credit))
    today = ctx.now()[:10]
    ctx.create("vending_transactions", rid, vending_txn_id=rid, vending_machine_id=vending_machine_id,
               customer_id=machine.get("customer_id", ""), ship_to_id=None, event_type="vending_item_returned",
               txn_reference=reference, original_txn_reference=original_txn_reference, sku=vend.get("sku", ""),
               product_category=vend.get("product_category", "none"), quantity=int(quantity),
               unit_price=vend.get("unit_price", 0.0), extended_amount=amount, employee_badge=vend.get("employee_badge", ""),
               cost_center=vend.get("cost_center", ""), vended_at="", visit_type="none", billing_period="",
               fee_type="none", event_date=today)
    if machine:
        ctx.update("vending_machines", vending_machine_id,
                   machine_stock_value=_Ledger.cents_half_up(float(machine.get("machine_stock_value") or 0.0) + amount))
    return str({"status": "returned", "vending_txn_id": rid, "txn_reference": reference,
                "original_txn_reference": original_txn_reference, "sku": vend.get("sku", ""),
                "quantity": int(quantity), "unit_credit": float(unit_credit), "extended_amount": amount,
                "event_date": today})


@tool(owner="agent", rw="write")
def credit_retired_item_vends_2f4f7780(ctx: ToolContext, vending_machine_id: str, original_txn_reference: str,
                                       quantity: int, credit_amount: float) -> str:
    """Record a vend error credit on a VendPoint machine: a new machine transaction of type vend error credited
    is recorded against the named vend, dated today, carrying the next error credit reference in sequence, one
    above the highest error credit reference on record. The item, product category, cost center and unit price
    are copied from the named vend; the units credited and the credit value are the values given. The credit
    value is added to the machine's consigned stock value. Success is a receipt naming the new transaction.

    Args:
        vending_machine_id: Id class — the reference number of the VendPoint machine placement the credit is recorded on, as returned by the machine lookup.
        original_txn_reference: Verbatim class — the vend transaction number of the vend being credited exactly as it appears on the machine's transactions; copy it character for character with no change to letters, digits or punctuation (verbatim).
        quantity: Fixed-format class — the number of units credited, a whole number of integer units greater than zero, with no decimal part.
        credit_amount: Fixed-format class — the credit value, a decimal amount in US dollars (USD), zero or more, with 2 decimal places, rounded half up to the cent.

    Returns:
        A dictionary rendered as text with: status (the text "credited" when the transaction was recorded),
        vending_txn_id (reference number of the new transaction), txn_reference (the error credit reference,
        letters VE, a hyphen and digits), original_txn_reference (echoed back), sku (the item copied from the
        named vend), quantity (units credited as an integer), extended_amount (the credit value in USD with two
        decimals) and event_date (today in YYYY-MM-DD form).
    """
    rid = ctx.make_id("vec_", vending_machine_id, original_txn_reference, quantity, credit_amount)
    reference = _Ledger.next_reference(ctx, "vending_transactions", "txn_reference", "VE-", 500000)
    machines = ctx.find("vending_machines", vending_machine_id=vending_machine_id)
    machine = machines[0] if machines else {}
    vends = ctx.find("vending_transactions", vending_machine_id=vending_machine_id, txn_reference=original_txn_reference)
    vend = vends[0] if vends else {}
    amount = _Ledger.cents_half_up(credit_amount)
    today = ctx.now()[:10]
    ctx.create("vending_transactions", rid, vending_txn_id=rid, vending_machine_id=vending_machine_id,
               customer_id=machine.get("customer_id", ""), ship_to_id=None, event_type="vending_vend_error_credited",
               txn_reference=reference, original_txn_reference=original_txn_reference, sku=vend.get("sku", ""),
               product_category=vend.get("product_category", "none"), quantity=int(quantity),
               unit_price=vend.get("unit_price", 0.0), extended_amount=amount, employee_badge="",
               cost_center=vend.get("cost_center", ""), vended_at="", visit_type="none", billing_period="",
               fee_type="none", event_date=today)
    if machine:
        ctx.update("vending_machines", vending_machine_id,
                   machine_stock_value=_Ledger.cents_half_up(float(machine.get("machine_stock_value") or 0.0) + amount))
    return str({"status": "credited", "vending_txn_id": rid, "txn_reference": reference,
                "original_txn_reference": original_txn_reference, "sku": vend.get("sku", ""),
                "quantity": int(quantity), "extended_amount": amount, "event_date": today})


@tool(owner="agent", rw="write")
def place_substitute_selection_72f4b244(ctx: ToolContext, vending_machine_id: str, slot_label: str, sku: str,
                                        par_qty: int) -> str:
    """Record an item placed by Corbett into one selection of a VendPoint machine: a new selection history
    entry of type add item assigns the named item to the named selection at the par quantity given, marked
    as a Corbett change, dated today and carrying the next planogram request reference in sequence, one above
    the highest planogram request reference on record. The item's product category is copied from the
    customer's contract price line for that item, and the entry is marked as a catalog item. Success is a
    receipt naming the new entry and its reference.

    Args:
        vending_machine_id: Id class — the reference number of the VendPoint machine placement whose selection receives the item, as returned by the machine lookup.
        slot_label: Verbatim class — the label of the selection (door, coil or bay) exactly as it appears on the machine's selection history entries; copy it character for character with no change to letters, digits or punctuation (verbatim).
        sku: Verbatim class — the Corbett item number placed in the selection exactly as it appears on the customer's contract price lines; copy it character for character with no change to letters, digits or punctuation (verbatim).
        par_qty: Fixed-format class — the par quantity of the selection, a whole number of integer units of the item, zero or more, with no decimal part.

    Returns:
        A dictionary rendered as text with: status (the text "item_added" when the entry was recorded),
        vending_slot_id (reference number of the new selection history entry), vending_machine_id (echoed back),
        slot_label (echoed back), sku (echoed back), product_category (the category copied for the item),
        par_qty (the par as an integer number of units), change_reference (the planogram request reference
        issued, letters VPC, a hyphen and six digits) and effective_date (the date of the entry in YYYY-MM-DD
        form).
    """
    rid = ctx.make_id("vpa_", vending_machine_id, slot_label, sku, par_qty)
    reference = _Ledger.next_reference(ctx, "vending_planogram", "change_reference", "VPC-", 500000)
    machines = ctx.find("vending_machines", vending_machine_id=vending_machine_id)
    customer_id = machines[0].get("customer_id", "") if machines else ""
    lines = ctx.find("pricing_items", customer_id=customer_id, sku=sku)
    lines = sorted(lines, key=lambda r: (str(r.get("effective_date")), str(r.get("change_reference"))))
    category = lines[-1].get("product_category", "") if lines else ""
    today = ctx.now()[:10]
    ctx.create("vending_planogram", rid, vending_slot_id=rid, vending_machine_id=vending_machine_id,
               customer_id=customer_id, event_type="vending_selection_set", slot_label=slot_label, sku=sku,
               product_category=category, par_qty=int(par_qty), special_item=False, change_type="add_item",
               change_source="corbett", removal_reason="none", change_reference=reference, event_date=today)
    return str({"status": "item_added", "vending_slot_id": rid, "vending_machine_id": vending_machine_id,
                "slot_label": slot_label, "sku": sku, "product_category": category, "par_qty": int(par_qty),
                "change_reference": reference, "effective_date": today})


@tool(owner="user", rw="write")
def set_substitute_selection_par_5d8137ae(ctx: ToolContext, vending_machine_id: str, slot_label: str, sku: str,
                                          par_qty: int) -> str:
    """Record a par change asked for by the customer on one selection of a VendPoint machine: a new selection
    history entry sets the par quantity of the named selection and item to the value given, marked as a
    customer change of type par change, dated today and carrying the next planogram request reference in
    sequence, one above the highest planogram request reference on record. The item's product category and
    special-item flag are carried over from the latest existing entry of that selection and item. Success is
    a receipt naming the new entry and its reference.

    Args:
        vending_machine_id: Id class — the reference number of the VendPoint machine placement whose selection is changed, as returned by the machine lookup.
        slot_label: Verbatim class — the label of the selection (door, coil or bay) exactly as it appears on the machine's selection history entries; copy it character for character with no change to letters, digits or punctuation (verbatim).
        sku: Verbatim class — the Corbett item number held in that selection exactly as it appears on the machine's selection history entries; copy it character for character with no change to letters, digits or punctuation (verbatim).
        par_qty: Fixed-format class — the new par quantity of the selection, a whole number of integer units of the item, zero or more, with no decimal part.

    Returns:
        A dictionary rendered as text with: status (the text "par_changed" when the entry was recorded),
        vending_slot_id (reference number of the new selection history entry), vending_machine_id (echoed back),
        slot_label (echoed back), sku (echoed back), par_qty (the new par as an integer number of units),
        change_reference (the planogram request reference issued, letters VPC, a hyphen and six digits) and
        effective_date (the date of the entry in YYYY-MM-DD form).
    """
    rid = ctx.make_id("vpp_", vending_machine_id, slot_label, sku, par_qty)
    reference = _Ledger.next_reference(ctx, "vending_planogram", "change_reference", "VPC-", 500000)
    machines = ctx.find("vending_machines", vending_machine_id=vending_machine_id)
    customer_id = machines[0].get("customer_id", "") if machines else ""
    prior = ctx.find("vending_planogram", vending_machine_id=vending_machine_id, slot_label=slot_label, sku=sku)
    prior = sorted(prior, key=lambda r: str(r.get("change_reference")))
    category = prior[-1].get("product_category", "") if prior else ""
    special = prior[-1].get("special_item", False) if prior else False
    today = ctx.now()[:10]
    ctx.create("vending_planogram", rid, vending_slot_id=rid, vending_machine_id=vending_machine_id,
               customer_id=customer_id, event_type="vending_selection_set", slot_label=slot_label, sku=sku,
               product_category=category, par_qty=int(par_qty), special_item=special, change_type="par_change",
               change_source="customer", removal_reason="none", change_reference=reference, event_date=today)
    return str({"status": "par_changed", "vending_slot_id": rid, "vending_machine_id": vending_machine_id,
                "slot_label": slot_label, "sku": sku, "par_qty": int(par_qty), "change_reference": reference,
                "effective_date": today})

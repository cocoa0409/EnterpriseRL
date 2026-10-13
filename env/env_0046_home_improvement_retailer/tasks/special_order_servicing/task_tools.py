"""Hidden task tools for special_order_servicing (Ridgeline Special Order Services).

Each tool performs one atomic write on a Ridgeline special order and is reached only through
unlock_* -> call_*; its name is published by the extended policy whose target_tool it is.
No tool checks eligibility, prerequisites or amounts: the agent decides those from the policy.
"""

from erlbench import ToolContext, tool


@tool(owner="agent", rw="write")
def bill_prepaid_delivery_3669e7a4(ctx: ToolContext, special_order_id: str, delivery_charge: float) -> str:
    """Bill the home delivery charge on a special order that Ridgeline has delivered to the
    customer's address. One call adds one home delivery fee line, dated today, to the order's
    ledger and raises the amount the customer owes on the order (its balance due) by the charge.
    The customer sees the delivery charge as a new line on the order and a higher balance due.

    Args:
        special_order_id: Id class — the reference number of the special order being charged,
            as returned by the special order lookup for this customer.
        delivery_charge: Fixed-format class — the home delivery charge to bill, in US dollars as a
            plain number with 2 decimal places (e.g. 42.10); the tool rounds to the nearest cent;
            0.00 bills a zero-amount line.

    Returns:
        A confirmation sentence carrying: the fee line reference number (text starting
        "sofee_"), the special order number (text), the charge billed (USD, 2 decimals) and the
        order's new balance due (USD, 2 decimals, negative when money is owed back). The
        sentence begins "Home delivery charge billed" when the line was recorded.
    """
    amount = round(float(delivery_charge), 2)
    rid = ctx.make_id("sofee_", special_order_id, "home_delivery_fee", amount)
    order = ctx.find("special_orders", special_order_id=special_order_id)
    order = order[0] if order else {}
    ctx.create("special_order_events", rid, special_order_event_id=rid, special_order_id=special_order_id,
               customer_id=order.get("customer_id"), event_type="special_fee_charged",
               order_number=order.get("order_number"), event_date=ctx.now()[:10], amount=amount,
               payment_method="not_applicable", payment_purpose="not_applicable", fee_type="home_delivery_fee",
               storage_days=0, credit_type="not_applicable", refund_method="not_applicable",
               original_event_id=None, special_request_id=None, inspection_point="not_applicable",
               inspection_condition="not_applicable")
    balance = round(float(order.get("balance_due") or 0) + amount, 2)
    ctx.update("special_orders", special_order_id, balance_due=balance)
    return (f"Home delivery charge billed: line {rid} on order {order.get('order_number')}, "
            f"charge {amount:.2f} USD, balance due now {balance:.2f} USD.")


@tool(owner="user", rw="write")
def accept_damage_allowance_e64dc664(ctx: ToolContext, special_order_id: str, special_request_id: str,
                                     allowance_amount: float) -> str:
    """The customer accepts, in person, the damage allowance offered on a special order item that
    arrived with cosmetic damage, choosing to keep the item. One call records the customer's remedy
    choice (keep the item with an allowance) on their damage claim, marks the claim completed today,
    and books one damage allowance credit line, dated today, that lowers the order's balance due by
    the allowance. The customer sees the claim closed with the allowance and the credit on the order.

    Args:
        special_order_id: Id class — the reference number of the special order the damaged item
            belongs to, as returned by the special order lookup for this customer.
        special_request_id: Id class — the reference number of the customer's open damage claim on
            that order, as returned by the special order request lookup.
        allowance_amount: Fixed-format class — the allowance being accepted, in US dollars as a plain
            number with 2 decimal places (e.g. 312.75); the tool rounds to the nearest cent.

    Returns:
        A confirmation sentence carrying: the credit line reference number (text starting
        "socr_"), the damage claim reference number (text), the allowance credited (USD, 2
        decimals) and the order's new balance due (USD, 2 decimals, negative when money is owed
        back). The sentence begins "Damage allowance accepted" when the choice and credit were
        recorded.
    """
    amount = round(float(allowance_amount), 2)
    rid = ctx.make_id("socr_", special_order_id, special_request_id, "damage_allowance", amount)
    order = ctx.find("special_orders", special_order_id=special_order_id)
    order = order[0] if order else {}
    ctx.update("special_requests", special_request_id, remedy_choice="damage_allowance", status="completed",
               resolved_date=ctx.now()[:10])
    ctx.create("special_order_events", rid, special_order_event_id=rid, special_order_id=special_order_id,
               customer_id=order.get("customer_id"), event_type="special_credit_applied",
               order_number=order.get("order_number"), event_date=ctx.now()[:10], amount=amount,
               payment_method="not_applicable", payment_purpose="not_applicable", fee_type="not_applicable",
               storage_days=0, credit_type="damage_allowance", refund_method="not_applicable",
               original_event_id=None, special_request_id=special_request_id, inspection_point="not_applicable",
               inspection_condition="not_applicable")
    balance = round(float(order.get("balance_due") or 0) - amount, 2)
    ctx.update("special_orders", special_order_id, balance_due=balance)
    return (f"Damage allowance accepted: credit line {rid} for claim {special_request_id}, "
            f"allowance {amount:.2f} USD, balance due now {balance:.2f} USD.")


_LINE_DEFAULTS = dict(payment_method="not_applicable", payment_purpose="not_applicable",
                      fee_type="not_applicable", storage_days=0, credit_type="not_applicable",
                      refund_method="not_applicable", original_event_id=None, special_request_id=None,
                      inspection_point="not_applicable", inspection_condition="not_applicable")


@tool(owner="agent", rw="write")
def bill_deposit_delivery_6add7fad(ctx: ToolContext, special_order_id: str, delivery_charge: float) -> str:
    """Bill the home delivery charge on a deposit-program special order (one paid by a deposit at order
    with the balance due at release) that Ridgeline has delivered to the customer's address. One call adds
    one home delivery fee line, dated today, to the order's ledger and raises the order's balance due
    by the charge; the customer sees the delivery charge on the order and the higher balance due.

    Args:
        special_order_id: Id class — the reference number of the delivered special order, as returned
            by the special order lookup for this customer.
        delivery_charge: Fixed-format class — the home delivery charge to bill, in US dollars as a plain
            number with 2 decimal places (e.g. 96.40); the tool rounds to the nearest cent.

    Returns:
        A confirmation sentence carrying: the fee line reference number (text starting "sodlv_"),
        the special order number (text), the charge billed (USD, 2 decimals) and the order's new
        balance due (USD, 2 decimals, negative when money is owed back). The sentence begins
        "Delivery charge billed" when the line was recorded.
    """
    amount = round(float(delivery_charge), 2)
    rid = ctx.make_id("sodlv_", special_order_id, amount)
    found = ctx.find("special_orders", special_order_id=special_order_id)
    order = found[0] if found else {"special_order_id": special_order_id}
    ctx.create("special_order_events", rid, **{**_LINE_DEFAULTS, **dict(special_order_event_id=rid, special_order_id=special_order_id, customer_id=order.get("customer_id"), order_number=order.get("order_number"), event_date=ctx.now()[:10], event_type="special_fee_charged", amount=amount, fee_type="home_delivery_fee")})
    balance = round(float(order.get("balance_due") or 0) + amount, 2)
    ctx.update("special_orders", special_order_id, balance_due=balance)
    return (f"Delivery charge billed: line {rid} on order {order.get('order_number')}, charge {amount:.2f} USD, "
            f"balance due now {balance:.2f} USD.")


@tool(owner="agent", rw="write")
def post_damage_allowance_1c94fd89(ctx: ToolContext, special_order_id: str, special_request_id: str,
                                   allowance_amount: float) -> str:
    """Book the damage allowance on a special order whose customer has already chosen, on their damage
    claim, to keep a cosmetically damaged item with an allowance. One call books one damage allowance
    credit line, dated today, against that claim, lowers the order's balance due by the allowance and
    marks the claim completed today. The customer sees the credit on the order and the claim closed.

    Args:
        special_order_id: Id class — the reference number of the special order the damaged item belongs
            to, as returned by the special order lookup for this customer.
        special_request_id: Id class — the reference number of the damage claim on that order, as
            returned by the special order request lookup.
        allowance_amount: Fixed-format class — the allowance to credit, in US dollars as a plain number
            with 2 decimal places (e.g. 512.30); the tool rounds to the nearest cent.

    Returns:
        A confirmation sentence carrying: the credit line reference number (text starting "sodmg_"),
        the damage claim reference number (text), the allowance credited (USD, 2 decimals) and the
        order's new balance due (USD, 2 decimals, negative when money is owed back). The sentence
        begins "Damage allowance credited" when the credit was recorded.
    """
    amount = round(float(allowance_amount), 2)
    rid = ctx.make_id("sodmg_", special_order_id, special_request_id, amount)
    found = ctx.find("special_orders", special_order_id=special_order_id)
    order = found[0] if found else {"special_order_id": special_order_id}
    ctx.create("special_order_events", rid, **{**_LINE_DEFAULTS, **dict(special_order_event_id=rid, special_order_id=special_order_id, customer_id=order.get("customer_id"), order_number=order.get("order_number"), event_date=ctx.now()[:10], event_type="special_credit_applied", amount=amount, credit_type="damage_allowance",
                special_request_id=special_request_id)})
    ctx.update("special_requests", special_request_id, status="completed", resolved_date=ctx.now()[:10])
    balance = round(float(order.get("balance_due") or 0) - amount, 2)
    ctx.update("special_orders", special_order_id, balance_due=balance)
    return (f"Damage allowance credited: line {rid} for claim {special_request_id}, allowance {amount:.2f} USD, "
            f"balance due now {balance:.2f} USD.")


@tool(owner="agent", rw="write")
def bill_storage_fee_4a2244a6(ctx: ToolContext, special_order_id: str, storage_days: int, storage_fee: float) -> str:
    """Bill the storage charge on a special order whose item was held at the store and has now left it.
    One call adds one storage fee line, dated today, recording the storage days billed and the charge,
    and raises the order's balance due by the charge; the customer sees the storage line, its day count
    and the higher balance due.

    Args:
        special_order_id: Id class — the reference number of the special order the item was stored for,
            as returned by the special order lookup for this customer.
        storage_days: Fixed-format class — the number of storage days billed on the line, an integer
            count of days at integer precision (no decimals), 0 or more (e.g. 9).
        storage_fee: Fixed-format class — the storage charge to bill, in US dollars as a plain number with
            2 decimal places (e.g. 45.60); the tool rounds to the nearest cent.

    Returns:
        A confirmation sentence carrying: the fee line reference number (text starting "sostg_"), the
        special order number (text), the storage days billed (whole number), the charge billed (USD, 2
        decimals) and the order's new balance due (USD, 2 decimals, negative when money is owed back).
        The sentence begins "Storage charge billed" when the line was recorded.
    """
    amount = round(float(storage_fee), 2)
    days = int(storage_days)
    rid = ctx.make_id("sostg_", special_order_id, days, amount)
    found = ctx.find("special_orders", special_order_id=special_order_id)
    order = found[0] if found else {"special_order_id": special_order_id}
    ctx.create("special_order_events", rid, **{**_LINE_DEFAULTS, **dict(special_order_event_id=rid, special_order_id=special_order_id, customer_id=order.get("customer_id"), order_number=order.get("order_number"), event_date=ctx.now()[:10], event_type="special_fee_charged", amount=amount, fee_type="storage_fee",
                storage_days=days)})
    balance = round(float(order.get("balance_due") or 0) + amount, 2)
    ctx.update("special_orders", special_order_id, balance_due=balance)
    return (f"Storage charge billed: line {rid} on order {order.get('order_number')}, {days} storage days, "
            f"charge {amount:.2f} USD, balance due now {balance:.2f} USD.")


@tool(owner="user", rw="write")
def accept_delay_credit_eaface8f(ctx: ToolContext, special_order_id: str, credit_amount: float) -> str:
    """The customer chooses, in person, to keep a special order the vendor delivered late and take the
    delay credit offered. One call registers the customer's delay remedy request with the choice of the
    delay credit, marked completed today, and books one delay credit line, dated today, that lowers the
    order's balance due by the credit. The customer sees the remedy recorded and the credit on the order.

    Args:
        special_order_id: Id class — the reference number of the delayed special order, as returned by the
            special order lookup for this customer.
        credit_amount: Fixed-format class — the delay credit being accepted, in US dollars as a plain number
            with 2 decimal places (e.g. 140.25); the tool rounds to the nearest cent.

    Returns:
        A confirmation sentence carrying: the delay remedy request reference number (text starting
        "sorq_"), the credit line reference number (text starting "sodly_"), the credit (USD, 2
        decimals) and the order's new balance due (USD, 2 decimals, negative when money is owed back).
        The sentence begins "Delay credit accepted" when the choice and the credit were recorded.
    """
    amount = round(float(credit_amount), 2)
    req = ctx.make_id("sorq_", special_order_id, "delay_remedy", amount)
    rid = ctx.make_id("sodly_", special_order_id, amount)
    found = ctx.find("special_orders", special_order_id=special_order_id)
    order = found[0] if found else {"special_order_id": special_order_id}
    ctx.create("special_requests", req, special_request_id=req, customer_id=order.get("customer_id"),
               special_order_id=special_order_id, request_type="delay_remedy", remedy_choice="delay_credit",
               status="completed", created_at=ctx.now(), resolved_date=ctx.now()[:10])
    ctx.create("special_order_events", rid, **{**_LINE_DEFAULTS, **dict(special_order_event_id=rid, special_order_id=special_order_id, customer_id=order.get("customer_id"), order_number=order.get("order_number"), event_date=ctx.now()[:10], event_type="special_credit_applied", amount=amount, credit_type="delay_credit",
                special_request_id=req)})
    balance = round(float(order.get("balance_due") or 0) - amount, 2)
    ctx.update("special_orders", special_order_id, balance_due=balance)
    return (f"Delay credit accepted: request {req}, credit line {rid}, credit {amount:.2f} USD, "
            f"balance due now {balance:.2f} USD.")

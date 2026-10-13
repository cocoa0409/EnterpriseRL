"""Hidden task tools for difficulty purchase_reservations_and_returns (Kestrel Auto, purchase orders).

Every tool here is reached only through unlock_* -> call_* and is named by exactly one extended policy's
target_tool in purchase.extended.yaml. Each tool performs one atomic booking on a purchase order and
judges nothing: whether the booking is due, and the amount it carries, are settled by the policy before
the call.
"""

from erlbench import ToolContext, tool


@tool(owner="agent", rw="write")
def post_exchange_shipping_fee_0e49ee13(ctx: ToolContext, purchase_order_id: str, amount: float) -> str:
    """Book the shipping fee for transporting an exchange replacement vehicle to the buyer's market onto that
    replacement purchase order. One call adds one shipping-fee charge, dated today, to the order's money
    history and raises the amount the buyer still owes on the order by the same figure; nothing else on the
    order changes. The buyer sees the new charge in the order history and a higher balance due. The call has
    succeeded when the receipt shows the booked entry reference and the new balance.

    Args:
        purchase_order_id: Id class — the purchase order reference number of the exchange replacement order
            that receives the charge, as returned by the purchase order lookup for this customer.
        amount: Fixed-format class — the shipping fee to book, in USD, a non-negative number with 2 decimal
            places (cents), already rounded half up to the cent; 0.00 books a zero-amount shipping entry.

    Returns:
        A confirmation sentence (string) stating the booked entry reference (text beginning "ptx_"), the
        charge type (shipping fee), the amount booked in USD with 2 decimal places, the posting date in
        YYYY-MM-DD, the purchase order reference number, and the order's new balance due in USD with 2
        decimal places. A receipt containing the entry reference means the charge is on the order.
    """
    amt = round(float(amount), 2)
    rid = ctx.make_id("ptx_", purchase_order_id, "shipping_fee", amt)
    order = ctx.find("purchase_orders", purchase_order_id=purchase_order_id)
    customer_id = order[0].get("customer_id") if order else None
    ctx.create("purchase_transactions", rid, purchase_txn_id=rid, purchase_order_id=purchase_order_id,
               customer_id=customer_id, event_type="purchase_charge_posted", txn_date=ctx.now()[:10],
               amount=amt, charge_type="shipping_fee", payment_source="not_applicable",
               payment_channel="not_applicable", refund_type="not_applicable", reason_code="not_applicable",
               source_txn_id=None, linked_reference_id=None)
    new_balance = round(float((order[0].get("order_balance") if order else 0) or 0) + amt, 2)
    ctx.update("purchase_orders", purchase_order_id, order_balance=new_balance)
    return (f"Shipping fee entry {rid} booked: {amt:.2f} USD on purchase order {purchase_order_id}, "
            f"posted {ctx.now()[:10]}; balance due now {new_balance:.2f} USD.")


@tool(owner="user", rw="write")
def pay_order_by_debit_card_8f259234(ctx: ToolContext, purchase_order_id: str, amount: float) -> str:
    """The buyer pays money toward the balance of their own purchase order with their debit card. One call
    takes one debit-card payment from the buyer, records it in the order's money history as a down payment
    received today on the debit-card rail, and lowers the amount the buyer still owes on the order by the
    amount paid. The buyer sees the payment in the order history and a lower balance due. The call has
    succeeded when the receipt shows the payment reference and the new balance.

    Args:
        purchase_order_id: Id class — the purchase order reference number of the buyer's order the payment
            goes toward, as given to the buyer by the representative from the purchase order lookup.
        amount: Fixed-format class — the amount charged to the buyer's debit card, in USD, a positive number
            with 2 decimal places (cents), already rounded half up to the cent.

    Returns:
        A confirmation sentence (string) stating the payment reference (text beginning "ptx_"), the amount
        paid in USD with 2 decimal places, the rail (debit card), the date received in YYYY-MM-DD, the
        purchase order reference number, and the order's new balance due in USD with 2 decimal places. A
        receipt containing the payment reference means the money is on the order.
    """
    amt = round(float(amount), 2)
    rid = ctx.make_id("ptx_", purchase_order_id, "debit_card_down_payment", amt)
    order = ctx.find("purchase_orders", purchase_order_id=purchase_order_id)
    customer_id = order[0].get("customer_id") if order else None
    ctx.create("purchase_transactions", rid, purchase_txn_id=rid, purchase_order_id=purchase_order_id,
               customer_id=customer_id, event_type="purchase_payment_posted", txn_date=ctx.now()[:10],
               amount=amt, charge_type="not_applicable", payment_source="down_payment",
               payment_channel="debit_card", refund_type="not_applicable", reason_code="not_applicable",
               source_txn_id=None, linked_reference_id=None)
    new_balance = round(float((order[0].get("order_balance") if order else 0) or 0) - amt, 2)
    ctx.update("purchase_orders", purchase_order_id, order_balance=new_balance)
    return (f"Debit card payment {rid} received: {amt:.2f} USD toward purchase order {purchase_order_id} on "
            f"{ctx.now()[:10]}; balance due now {new_balance:.2f} USD.")


@tool(owner="agent", rw="write")
def post_transfer_shipping_fee_29e5e50b(ctx: ToolContext, purchase_order_id: str, amount: float) -> str:
    """Book the transfer shipping fee for transporting a signed order's vehicle from its hub to the buyer's market
    onto that purchase order. One call adds one shipping-fee charge, dated today, to the order's money history
    and raises the amount the buyer still owes on the order by the same figure; nothing else on the order
    changes. The buyer sees the new charge in the order history and a higher balance due. The call has
    succeeded when the receipt shows the booked entry reference and the new balance.

    Args:
        purchase_order_id: Id class — the purchase order reference number of the signed order whose vehicle is
            transported, as returned by the purchase order lookup for this customer.
        amount: Fixed-format class — the transfer shipping fee to book, in USD, a non-negative number with 2
            decimal places (cents), already rounded half up to the cent; 0.00 books a zero-amount entry.

    Returns:
        A confirmation sentence (string) stating the booked entry reference (text beginning "ptx_"), the
        charge type (shipping fee), the amount booked in USD with 2 decimal places, the posting date in
        YYYY-MM-DD, the purchase order reference number, and the order's new balance due in USD with 2
        decimal places. A receipt containing the entry reference means the charge is on the order.
    """
    amt = round(float(amount), 2)
    rid = ctx.make_id("ptx_", purchase_order_id, "transfer_shipping_fee", amt)
    order = ctx.find("purchase_orders", purchase_order_id=purchase_order_id)
    customer_id = order[0].get("customer_id") if order else None
    ctx.create("purchase_transactions", rid, purchase_txn_id=rid, purchase_order_id=purchase_order_id,
               customer_id=customer_id, event_type="purchase_charge_posted", txn_date=ctx.now()[:10],
               amount=amt, charge_type="shipping_fee", payment_source="not_applicable",
               payment_channel="not_applicable", refund_type="not_applicable", reason_code="not_applicable",
               source_txn_id=None, linked_reference_id=None)
    new_balance = round(float((order[0].get("order_balance") if order else 0) or 0) + amt, 2)
    ctx.update("purchase_orders", purchase_order_id, order_balance=new_balance)
    return (f"Shipping fee entry {rid} booked: {amt:.2f} USD on purchase order {purchase_order_id}, "
            f"posted {ctx.now()[:10]}; balance due now {new_balance:.2f} USD.")


@tool(owner="agent", rw="write")
def post_documentation_fee_307ebcc3(ctx: ToolContext, purchase_order_id: str, amount: float) -> str:
    """Book the documentation fee for preparing a signed order's sale, title and registration paperwork onto
    that purchase order. One call adds one documentation-fee charge, dated today, to the order's money history
    and raises the amount the buyer still owes on the order by the same figure; nothing else on the order
    changes. The buyer sees the new charge in the order history and a higher balance due. The call has
    succeeded when the receipt shows the booked entry reference and the new balance.

    Args:
        purchase_order_id: Id class — the purchase order reference number of the signed order that receives the
            charge, as returned by the purchase order lookup for this customer.
        amount: Fixed-format class — the documentation fee to book, in USD, a non-negative number with 2
            decimal places (cents), already rounded half up to the cent.

    Returns:
        A confirmation sentence (string) stating the booked entry reference (text beginning "ptx_"), the
        charge type (documentation fee), the amount booked in USD with 2 decimal places, the posting date in
        YYYY-MM-DD, the purchase order reference number, and the order's new balance due in USD with 2
        decimal places. A receipt containing the entry reference means the charge is on the order.
    """
    amt = round(float(amount), 2)
    rid = ctx.make_id("ptx_", purchase_order_id, "documentation_fee", amt)
    order = ctx.find("purchase_orders", purchase_order_id=purchase_order_id)
    customer_id = order[0].get("customer_id") if order else None
    ctx.create("purchase_transactions", rid, purchase_txn_id=rid, purchase_order_id=purchase_order_id,
               customer_id=customer_id, event_type="purchase_charge_posted", txn_date=ctx.now()[:10],
               amount=amt, charge_type="documentation_fee", payment_source="not_applicable",
               payment_channel="not_applicable", refund_type="not_applicable", reason_code="not_applicable",
               source_txn_id=None, linked_reference_id=None)
    new_balance = round(float((order[0].get("order_balance") if order else 0) or 0) + amt, 2)
    ctx.update("purchase_orders", purchase_order_id, order_balance=new_balance)
    return (f"Documentation fee entry {rid} booked: {amt:.2f} USD on purchase order {purchase_order_id}, "
            f"posted {ctx.now()[:10]}; balance due now {new_balance:.2f} USD.")


@tool(owner="user", rw="write")
def pay_finance_down_payment_by_ach_50ed840f(ctx: ToolContext, purchase_order_id: str, amount: float) -> str:
    """The buyer pays the cash down payment on their own purchase order that is being financed through Kestrel
    Auto Finance, from their bank account by ACH. One call takes one ACH payment from the buyer, records it in
    the order's money history as a down payment received today on the ACH rail, and lowers the amount the
    buyer still owes on the order by the amount paid. The buyer sees the payment in the order history and a
    lower balance due. The call has succeeded when the receipt shows the payment reference and the new
    balance.

    Args:
        purchase_order_id: Id class — the purchase order reference number of the buyer's financed order the
            down payment goes toward, as given to the buyer by the representative from the purchase order
            lookup.
        amount: Fixed-format class — the amount drawn from the buyer's bank account, in USD, a positive number
            with 2 decimal places (cents), already rounded half up to the cent.

    Returns:
        A confirmation sentence (string) stating the payment reference (text beginning "ptx_"), the amount
        paid in USD with 2 decimal places, the rail (ACH), the date received in YYYY-MM-DD, the purchase order
        reference number, and the order's new balance due in USD with 2 decimal places. A receipt containing
        the payment reference means the money is on the order.
    """
    amt = round(float(amount), 2)
    rid = ctx.make_id("ptx_", purchase_order_id, "ach_down_payment", amt)
    order = ctx.find("purchase_orders", purchase_order_id=purchase_order_id)
    customer_id = order[0].get("customer_id") if order else None
    ctx.create("purchase_transactions", rid, purchase_txn_id=rid, purchase_order_id=purchase_order_id,
               customer_id=customer_id, event_type="purchase_payment_posted", txn_date=ctx.now()[:10],
               amount=amt, charge_type="not_applicable", payment_source="down_payment",
               payment_channel="ach", refund_type="not_applicable", reason_code="not_applicable",
               source_txn_id=None, linked_reference_id=None)
    new_balance = round(float((order[0].get("order_balance") if order else 0) or 0) - amt, 2)
    ctx.update("purchase_orders", purchase_order_id, order_balance=new_balance)
    return (f"ACH down payment {rid} received: {amt:.2f} USD toward purchase order {purchase_order_id} on "
            f"{ctx.now()[:10]}; balance due now {new_balance:.2f} USD.")

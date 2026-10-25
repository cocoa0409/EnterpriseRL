"""Hidden task tools for env_0059_residential_mortgage_lender / appraisal_orders_and_fees.

Each tool performs one atomic write on an appraisal order's fee ledger and keeps the order's net
appraisal charges in step with the entry it books. No tool checks eligibility, ordering or any
policy precondition, and no tool works out an amount: the amount is passed in by the caller.
"""

from erlbench import ToolContext, tool


@tool(owner="agent", rw="write")
def book_size_value_addon_5d867e2e(ctx: ToolContext, appraisal_order_id: str, loan_file_id: str,
                                   addon_amount: float, payment_method: str) -> str:
    """Book the complexity add-on of an appraisal order: collect, on the card or account the order was already paid with, one charge on the order's gross-living-area surcharge line for the stated amount, dated today. On success the order's fee history gains one new charge entry for that line and the order's net appraisal charges paid rise by exactly that amount; the borrower sees the add-on as a separate collected charge on the order.

    Args:
        appraisal_order_id: Id class — reference number of the appraisal order the add-on is booked on, as returned by the appraisal order lookup for the customer.
        loan_file_id: Id class — reference number of the mortgage loan file the appraisal order supports, as shown on that appraisal order and returned by the loan file lookup.
        addon_amount: Fixed-format class — amount of the add-on collected, in USD, 2 decimal places, a positive number; it is stored rounded to 2 decimal places.
        payment_method: Enum class — the card or account charged, one of: debit_card when the order's earlier charges were collected from the borrower's debit card; credit_card when they were collected from the borrower's credit card; ach_debit when they were debited from the borrower's bank account by ACH.

    Returns:
        A dictionary rendered as text: appraisal_fee_entry_id (string, reference number of the new charge entry), appraisal_order_id (string, the order charged), fee_component (string, always gla_surcharge), amount (number, USD with 2 decimal places, the amount collected), entry_date (string, YYYY-MM-DD, today's date), fee_balance (number, USD with 2 decimal places, the order's net appraisal charges paid after this entry) and status (string, always booked). A status of booked means the charge now stands on the order.
    """
    amount = round(float(addon_amount), 2)
    rid = ctx.make_id("afe_", appraisal_order_id, loan_file_id, amount, payment_method)
    order = ctx.find("appraisal_orders", appraisal_order_id=appraisal_order_id)
    customer_id = order[0].get("customer_id") if order else ""
    balance = round(float((order[0].get("fee_balance") if order else 0) or 0) + amount, 2)
    ctx.create("appraisal_fee_ledger", rid, appraisal_fee_entry_id=rid, appraisal_order_id=appraisal_order_id,
               customer_id=customer_id, event_type="appraisal_fee_charged", fee_component="gla_surcharge",
               amount=amount, entry_date=ctx.now()[:10], payment_method=payment_method,
               original_fee_entry_id=None, refund_reason="none")
    ctx.update("appraisal_orders", appraisal_order_id, fee_balance=balance)
    return str({"appraisal_fee_entry_id": rid, "appraisal_order_id": appraisal_order_id,
                "fee_component": "gla_surcharge", "amount": amount, "entry_date": ctx.now()[:10],
                "fee_balance": balance, "status": "booked"})


@tool(owner="user", rw="write")
def pay_update_inspection_charge_fc307ba0(ctx: ToolContext, appraisal_order_id: str, loan_file_id: str,
                                          charge_amount: float, payment_method: str) -> str:
    """The borrower authorises and pays, from their own card or bank account, the charge for a Form 1004D appraisal update visit on their appraisal order, for the stated amount, dated today. On success the order's fee history gains one new charge entry on the reinspection line and the order's net appraisal charges paid rise by exactly that amount; the borrower sees the payment confirmed with its entry reference.

    Args:
        appraisal_order_id: Id class — reference number of the borrower's appraisal order the update visit is for, as read to the borrower from the appraisal order lookup.
        loan_file_id: Id class — reference number of the mortgage loan file the appraisal order supports, as read to the borrower from the appraisal order or loan file lookup.
        charge_amount: Fixed-format class — amount the borrower pays, in USD, 2 decimal places, a positive number; it is stored rounded to 2 decimal places.
        payment_method: Enum class — how the borrower pays, one of: debit_card when the borrower pays with a debit card; credit_card when the borrower pays with a credit card; ach_debit when the borrower pays by ACH debit from a bank account.

    Returns:
        A dictionary rendered as text: appraisal_fee_entry_id (string, reference number of the new charge entry), appraisal_order_id (string, the order charged), fee_component (string, always reinspection_fee), amount (number, USD with 2 decimal places, the amount paid), entry_date (string, YYYY-MM-DD, today's date), fee_balance (number, USD with 2 decimal places, the order's net appraisal charges paid after this payment) and status (string, always paid). A status of paid means the payment now stands on the order.
    """
    amount = round(float(charge_amount), 2)
    rid = ctx.make_id("afe_", appraisal_order_id, loan_file_id, amount, payment_method, "update")
    order = ctx.find("appraisal_orders", appraisal_order_id=appraisal_order_id)
    customer_id = order[0].get("customer_id") if order else ""
    balance = round(float((order[0].get("fee_balance") if order else 0) or 0) + amount, 2)
    ctx.create("appraisal_fee_ledger", rid, appraisal_fee_entry_id=rid, appraisal_order_id=appraisal_order_id,
               customer_id=customer_id, event_type="appraisal_fee_charged", fee_component="reinspection_fee",
               amount=amount, entry_date=ctx.now()[:10], payment_method=payment_method,
               original_fee_entry_id=None, refund_reason="none")
    ctx.update("appraisal_orders", appraisal_order_id, fee_balance=balance)
    return str({"appraisal_fee_entry_id": rid, "appraisal_order_id": appraisal_order_id,
                "fee_component": "reinspection_fee", "amount": amount, "entry_date": ctx.now()[:10],
                "fee_balance": balance, "status": "paid"})


@tool(owner="agent", rw="write")
def refund_late_rush_charge_6e5bda3a(ctx: ToolContext, appraisal_order_id: str, original_fee_entry_id: str,
                                     refund_amount: float, payment_method: str) -> str:
    """Refund part or all of a rush charge on an appraisal order to the borrower, dated today, with the refund reason that the rush promise was missed. On success the order's fee history gains one refund entry on the rush line that names the charge entry it returns, and the order's net appraisal charges paid fall by exactly the refunded amount; the borrower sees the refund on the card or account it is returned to.

    Args:
        appraisal_order_id: Id class — reference number of the appraisal order the rush charge was collected on, as returned by the appraisal order lookup.
        original_fee_entry_id: Id class — reference number of the rush charge entry being returned, as returned by the appraisal fee history lookup for the order.
        refund_amount: Fixed-format class — amount returned to the borrower, in USD, 2 decimal places, a positive number; it is stored rounded to 2 decimal places.
        payment_method: Enum class — the card or account the refund is returned to, one of: debit_card when the rush charge was collected from the borrower's debit card; credit_card when it was collected from the borrower's credit card; ach_debit when it was debited from the borrower's bank account by ACH.

    Returns:
        A dictionary rendered as text: appraisal_fee_entry_id (string, reference number of the new refund entry), original_fee_entry_id (string, the rush charge entry returned), fee_component (string, always rush_fee), amount (number, USD with 2 decimal places, the amount refunded), refund_reason (string, always rush_deadline_missed), entry_date (string, YYYY-MM-DD, today's date), fee_balance (number, USD with 2 decimal places, the order's net appraisal charges paid after the refund) and status (string, always refunded). A status of refunded means the refund now stands on the order.
    """
    amount = round(float(refund_amount), 2)
    rid = ctx.make_id("afe_", appraisal_order_id, original_fee_entry_id, amount, payment_method)
    order = ctx.find("appraisal_orders", appraisal_order_id=appraisal_order_id)
    customer_id = order[0].get("customer_id") if order else ""
    balance = round(float((order[0].get("fee_balance") if order else 0) or 0) - amount, 2)
    ctx.create("appraisal_fee_ledger", rid, appraisal_fee_entry_id=rid, appraisal_order_id=appraisal_order_id,
               customer_id=customer_id, event_type="appraisal_fee_refunded", fee_component="rush_fee",
               amount=amount, entry_date=ctx.now()[:10], payment_method=payment_method,
               original_fee_entry_id=original_fee_entry_id, refund_reason="rush_deadline_missed")
    ctx.update("appraisal_orders", appraisal_order_id, fee_balance=balance)
    return str({"appraisal_fee_entry_id": rid, "original_fee_entry_id": original_fee_entry_id,
                "fee_component": "rush_fee", "amount": amount, "refund_reason": "rush_deadline_missed",
                "entry_date": ctx.now()[:10], "fee_balance": balance, "status": "refunded"})


@tool(owner="user", rw="write")
def pay_final_inspection_charge_e30bacb7(ctx: ToolContext, appraisal_order_id: str, loan_file_id: str,
                                         charge_amount: float, payment_method: str) -> str:
    """The borrower authorises and pays, from their own card or bank account, the charge for a Form 1004D completion (final inspection) visit on their appraisal order, for the stated amount, dated today. On success the order's fee history gains one new charge entry on the reinspection line and the order's net appraisal charges paid rise by exactly that amount; the borrower sees the payment confirmed with its entry reference.

    Args:
        appraisal_order_id: Id class — reference number of the borrower's appraisal order the final inspection is for, as read to the borrower from the appraisal order lookup.
        loan_file_id: Id class — reference number of the mortgage loan file the appraisal order supports, as read to the borrower from the appraisal order or loan file lookup.
        charge_amount: Fixed-format class — amount the borrower pays, in USD, 2 decimal places, a positive number; it is stored rounded to 2 decimal places.
        payment_method: Enum class — how the borrower pays, one of: debit_card when the borrower pays with a debit card; credit_card when the borrower pays with a credit card; ach_debit when the borrower pays by ACH debit from a bank account.

    Returns:
        A dictionary rendered as text: appraisal_fee_entry_id (string, reference number of the new charge entry), appraisal_order_id (string, the order charged), fee_component (string, always reinspection_fee), amount (number, USD with 2 decimal places, the amount paid), entry_date (string, YYYY-MM-DD, today's date), fee_balance (number, USD with 2 decimal places, the order's net appraisal charges paid after this payment) and status (string, always paid). A status of paid means the payment now stands on the order.
    """
    amount = round(float(charge_amount), 2)
    rid = ctx.make_id("afe_", appraisal_order_id, loan_file_id, amount, payment_method, "completion")
    order = ctx.find("appraisal_orders", appraisal_order_id=appraisal_order_id)
    customer_id = order[0].get("customer_id") if order else ""
    balance = round(float((order[0].get("fee_balance") if order else 0) or 0) + amount, 2)
    ctx.create("appraisal_fee_ledger", rid, appraisal_fee_entry_id=rid, appraisal_order_id=appraisal_order_id,
               customer_id=customer_id, event_type="appraisal_fee_charged", fee_component="reinspection_fee",
               amount=amount, entry_date=ctx.now()[:10], payment_method=payment_method,
               original_fee_entry_id=None, refund_reason="none")
    ctx.update("appraisal_orders", appraisal_order_id, fee_balance=balance)
    return str({"appraisal_fee_entry_id": rid, "appraisal_order_id": appraisal_order_id,
                "fee_component": "reinspection_fee", "amount": amount, "entry_date": ctx.now()[:10],
                "fee_balance": balance, "status": "paid"})

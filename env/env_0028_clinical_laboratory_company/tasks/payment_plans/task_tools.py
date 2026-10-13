"""Hidden task tools of the payment_plans difficulty (Halverson Clinical Laboratories).

Each tool is named by exactly one extended policy's target_tool in plans.extended.yaml and is
reached through the unlock/call meta tools. Every tool performs one atomic write on the
Patient Payment Plans records with the arguments as given; none of them judges eligibility,
standing, timing or any amount, and none refuses a call for a business reason.
"""

from erlbench import ToolContext, tool


@tool(owner="user", rw="write")
def pay_catch_up_2a071954(ctx: ToolContext, plan_id: str, installment_number: int, due_date: str,
                          amount: float, payment_method: str) -> str:
    """The patient pays, with their own payment method, the catch-up payment on their own past-due
    payment plan. One call posts one payment on the plan's activity, marked as an arrears payment
    against the installment named, lowers the plan's remaining balance by the amount paid, and
    returns the plan to current standing (status active). The patient sees the payment on the plan
    straight away together with a payment reference.

    Args:
        plan_id: Id class — the reference number of the patient's payment plan, as shown by the payment-plan lookup.
        installment_number: Fixed-format class — the number of the missed installment this payment settles, copied from the missed-installment line on the plan's activity; a non-negative integer (0 = down payment).
        due_date: Fixed-format class — the due date of that missed installment, copied from the same line, written as YYYY-MM-DD.
        amount: Fixed-format class — the amount the patient pays, in USD, a positive number to 2 decimal places, rounded to the nearest cent.
        payment_method: Enum class — how the patient pays, exactly one of: credit_card when the patient pays with a credit card; debit_card when the patient pays with a debit card; ach_bank_transfer when the patient pays from a checking or savings account by bank transfer; check when the patient pays by a mailed paper check; hsa_fsa_card when the patient pays with a health savings or flexible spending account card.

    Returns:
        A dict with: payment_id (string, the reference of the posted payment), plan_id (string),
        amount_paid (number, USD to 2 decimal places), plan_balance (number, USD to 2 decimal
        places, the plan's remaining balance once the payment is applied) and plan_status (string,
        "active"). A returned payment_id means the payment was posted.
    """
    plans = ctx.find("payment_plans", plan_id=plan_id)
    paid = round(float(amount), 2)
    rid = ctx.make_id("ppay_", plan_id, installment_number, due_date, paid, payment_method)
    ctx.create("plan_transactions", rid, plan_transaction_id=rid, plan_id=plan_id,
               customer_id=plans[0].get("customer_id") if plans else "",
               event_type="plans_installment_paid", event_date=ctx.now()[:10], amount=paid,
               installment_number=int(installment_number), due_date=due_date,
               payment_type="arrears_cure", payment_method=payment_method)
    balance = round(float((plans[0].get("plan_balance") if plans else 0) or 0) - paid, 2)
    ctx.update("payment_plans", plan_id, plan_balance=balance, status="active")
    return str({"payment_id": rid, "plan_id": plan_id, "amount_paid": paid,
                "plan_balance": balance, "plan_status": "active"})


@tool(owner="user", rw="write")
def pay_add_on_down_payment_958d6e13(ctx: ToolContext, plan_id: str, amount: float,
                                     payment_method: str) -> str:
    """The patient pays, with their own payment method, the down payment that goes with a bill
    being added to their payment plan. One call posts one payment on the plan's activity, marked as
    a down payment dated today, and lowers the plan's remaining balance by the amount paid; the
    plan's status, installment and due day are not changed. The patient sees the payment on the
    plan straight away together with a payment reference.

    Args:
        plan_id: Id class — the reference number of the patient's payment plan, as shown by the payment-plan lookup.
        amount: Fixed-format class — the amount the patient pays, in USD, a positive number to 2 decimal places, rounded to the nearest cent.
        payment_method: Enum class — how the patient pays, exactly one of: credit_card when the patient pays with a credit card; debit_card when the patient pays with a debit card; ach_bank_transfer when the patient pays from a checking or savings account by bank transfer; check when the patient pays by a mailed paper check; hsa_fsa_card when the patient pays with a health savings or flexible spending account card.

    Returns:
        A dict with: payment_id (string, the reference of the posted payment), plan_id (string),
        amount_paid (number, USD to 2 decimal places) and plan_balance (number, USD to 2 decimal
        places, the plan's remaining balance once the payment is applied). A returned payment_id
        means the payment was posted.
    """
    plans = ctx.find("payment_plans", plan_id=plan_id)
    paid = round(float(amount), 2)
    today = ctx.now()[:10]
    rid = ctx.make_id("pdwn_", plan_id, paid, payment_method)
    ctx.create("plan_transactions", rid, plan_transaction_id=rid, plan_id=plan_id,
               customer_id=plans[0].get("customer_id") if plans else "",
               event_type="plans_installment_paid", event_date=today, amount=paid,
               installment_number=0, due_date=today, payment_type="down_payment",
               payment_method=payment_method)
    balance = round(float((plans[0].get("plan_balance") if plans else 0) or 0) - paid, 2)
    ctx.update("payment_plans", plan_id, plan_balance=balance)
    return str({"payment_id": rid, "plan_id": plan_id, "amount_paid": paid, "plan_balance": balance})


@tool(owner="agent", rw="write")
def reset_relief_installment_53948494(ctx: ToolContext, plan_id: str, installment_amount: float) -> str:
    """Sets a new regular monthly installment on a patient's payment plan to reflect a
    financial-assistance release booked on the plan. One call replaces the installment amount on the plan;
    the remaining balance, due day, automatic-payment setup and status are left as they are. The
    patient's next statements and automatic draws show the new installment.

    Args:
        plan_id: Id class — the reference number of the patient's payment plan, as shown by the payment-plan lookup.
        installment_amount: Fixed-format class — the new regular monthly installment, in USD, a positive number to 2 decimal places, rounded to the nearest cent.

    Returns:
        A dict with: plan_id (string), installment_amount (number, USD to 2 decimal places, the
        installment now on the plan) and status (string, "installment_updated"). A returned status
        of installment_updated means the change was saved.
    """
    amt = round(float(installment_amount), 2)
    ctx.update("payment_plans", plan_id, installment_amount=amt)
    return str({"plan_id": plan_id, "installment_amount": amt, "status": "installment_updated"})


@tool(owner="agent", rw="write")
def add_invoice_to_plan_14a3a600(ctx: ToolContext, plan_id: str, invoice_id: str,
                                 enrolled_amount: float, installment_amount: float) -> str:
    """Puts one more of the patient's invoices on their existing payment plan. One call books the
    invoice's balance onto the plan's activity as an enrollment dated today, raises the plan's
    remaining balance by that amount and sets the plan's new regular monthly installment; the due
    day, automatic-payment setup and status are left as they are. The patient sees the invoice
    listed on the plan and the new installment on the next statement.

    Args:
        plan_id: Id class — the reference number of the patient's payment plan, as shown by the payment-plan lookup.
        invoice_id: Id class — the reference number of the invoice being put on the plan, as shown by the invoice lookup.
        enrolled_amount: Fixed-format class — the invoice balance carried onto the plan, in USD, a positive number to 2 decimal places, rounded to the nearest cent.
        installment_amount: Fixed-format class — the new regular monthly installment of the plan, in USD, a positive number to 2 decimal places, rounded to the nearest cent.

    Returns:
        A dict with: enrollment_id (string, the reference of the enrollment line), plan_id
        (string), invoice_id (string), enrolled_amount (number, USD to 2 decimal places),
        plan_balance (number, USD to 2 decimal places, the plan's remaining balance including the
        invoice) and installment_amount (number, USD to 2 decimal places). A returned
        enrollment_id means the invoice is on the plan.
    """
    plans = ctx.find("payment_plans", plan_id=plan_id)
    amt = round(float(enrolled_amount), 2)
    inst = round(float(installment_amount), 2)
    rid = ctx.make_id("penr_", plan_id, invoice_id, amt, inst)
    ctx.create("plan_transactions", rid, plan_transaction_id=rid, plan_id=plan_id,
               customer_id=plans[0].get("customer_id") if plans else "",
               event_type="plans_invoice_enrolled", event_date=ctx.now()[:10], amount=amt,
               invoice_id=invoice_id)
    balance = round(float((plans[0].get("plan_balance") if plans else 0) or 0) + amt, 2)
    ctx.update("payment_plans", plan_id, plan_balance=balance, installment_amount=inst)
    return str({"enrollment_id": rid, "plan_id": plan_id, "invoice_id": invoice_id,
                "enrolled_amount": amt, "plan_balance": balance, "installment_amount": inst})


@tool(owner="user", rw="write")
def pay_reinstatement_amount_fe9b74b8(ctx: ToolContext, plan_id: str, installment_number: int, due_date: str,
                                      amount: float, payment_method: str) -> str:
    """The patient pays, with their own payment method, the reinstatement payment on their own defaulted
    payment plan. One call posts one payment on the plan's activity, marked as an arrears payment against
    the installment named, and lowers the plan's balance figure by the amount paid; the plan's status is
    left as it is. The patient sees the payment on the plan straight away together with a payment
    reference.

    Args:
        plan_id: Id class — the reference number of the patient's payment plan, as shown by the payment-plan lookup.
        installment_number: Fixed-format class — the number of the missed installment this payment is posted against, copied from the missed-installment line on the plan's activity; a non-negative integer (0 = down payment).
        due_date: Fixed-format class — the due date of that missed installment, copied from the same line, written as YYYY-MM-DD.
        amount: Fixed-format class — the amount the patient pays, in USD, a positive number to 2 decimal places, rounded to the nearest cent.
        payment_method: Enum class — how the patient pays, exactly one of: credit_card when the patient pays with a credit card; debit_card when the patient pays with a debit card; ach_bank_transfer when the patient pays from a checking or savings account by bank transfer; check when the patient pays by a mailed paper check; hsa_fsa_card when the patient pays with a health savings or flexible spending account card.

    Returns:
        A dict with: payment_id (string, the reference of the posted payment), plan_id (string),
        amount_paid (number, USD to 2 decimal places), plan_balance (number, USD to 2 decimal places,
        the plan's balance figure once the payment is applied) and plan_status (string, the plan's
        status, unchanged). A returned payment_id means the payment was posted.
    """
    plans = ctx.find("payment_plans", plan_id=plan_id)
    paid = round(float(amount), 2)
    rid = ctx.make_id("prei_", plan_id, installment_number, due_date, paid, payment_method)
    ctx.create("plan_transactions", rid, plan_transaction_id=rid, plan_id=plan_id,
               customer_id=plans[0].get("customer_id") if plans else "",
               event_type="plans_installment_paid", event_date=ctx.now()[:10], amount=paid,
               installment_number=int(installment_number), due_date=due_date,
               payment_type="arrears_cure", payment_method=payment_method)
    balance = round(float((plans[0].get("plan_balance") if plans else 0) or 0) - paid, 2)
    ctx.update("payment_plans", plan_id, plan_balance=balance)
    return str({"payment_id": rid, "plan_id": plan_id, "amount_paid": paid, "plan_balance": balance,
                "plan_status": plans[0].get("status") if plans else ""})


@tool(owner="agent", rw="write")
def reinstate_plan_60f00772(ctx: ToolContext, plan_id: str, invoice_id: str, reenrolled_amount: float,
                            installment_amount: float) -> str:
    """Puts a patient's defaulted payment plan back in force. One call returns the plan to active
    status, adds one to the plan's reinstatement count (the default date is kept as history), books the
    named invoice's balance back onto the plan's activity as an enrollment dated today, raises the plan's
    balance figure by that amount and sets the plan's regular monthly installment. The patient's plan
    shows as active again with the invoice on it and the new installment on the next statement.

    Args:
        plan_id: Id class — the reference number of the patient's payment plan, as shown by the payment-plan lookup.
        invoice_id: Id class — the reference number of the invoice whose balance goes back onto the plan, as shown by the invoice lookup.
        reenrolled_amount: Fixed-format class — the invoice balance booked back onto the plan, in USD, a positive number to 2 decimal places, rounded to the nearest cent.
        installment_amount: Fixed-format class — the plan's regular monthly installment once it is back in force, in USD, a positive number to 2 decimal places, rounded to the nearest cent.

    Returns:
        A dict with: enrollment_id (string, the reference of the enrollment line), plan_id (string),
        plan_status (string, "active"), reinstatement_count (integer, the count after this
        reinstatement), plan_balance (number, USD to 2 decimal places) and installment_amount (number,
        USD to 2 decimal places). A returned plan_status of active means the plan is back in force.
    """
    plans = ctx.find("payment_plans", plan_id=plan_id)
    amt = round(float(reenrolled_amount), 2)
    inst = round(float(installment_amount), 2)
    count = int((plans[0].get("reinstatement_count") if plans else 0) or 0) + 1
    rid = ctx.make_id("prin_", plan_id, invoice_id, amt, inst)
    ctx.create("plan_transactions", rid, plan_transaction_id=rid, plan_id=plan_id,
               customer_id=plans[0].get("customer_id") if plans else "",
               event_type="plans_invoice_enrolled", event_date=ctx.now()[:10], amount=amt,
               invoice_id=invoice_id)
    balance = round(float((plans[0].get("plan_balance") if plans else 0) or 0) + amt, 2)
    ctx.update("payment_plans", plan_id, status="active", reinstatement_count=count,
               plan_balance=balance, installment_amount=inst)
    return str({"enrollment_id": rid, "plan_id": plan_id, "plan_status": "active",
                "reinstatement_count": count, "plan_balance": balance, "installment_amount": inst})

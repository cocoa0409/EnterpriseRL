"""Hidden task tools for env_0067_online_personal_loan_lender / practicepay_patient_financing (category pos).

Each tool performs one atomic write on a PracticePay plan and its ledger. No tool judges eligibility,
prerequisites or amounts: the caller supplies the value the published policy yields.
"""

from erlbench import ToolContext, tool


@tool(owner="agent", rw="write")
def assess_returned_payment_fee_f9ef5ea0(ctx: ToolContext, pos_plan_id: str, related_txn_id: str, fee_amount: float) -> str:
    """Charge a returned-payment fee to a PracticePay plan for one payment that came back unpaid.

    The service desk books one returned-payment fee entry on the plan's ledger, dated today and tied to the
    returned-payment entry it is charged for, and raises the plan balance by the fee. The patient sees the fee on
    the plan's ledger and in the higher balance; the receipt confirms the entry booked and the new plan balance.

    Args:
        pos_plan_id: Id class — reference number of the PracticePay plan the fee is charged to, as returned by the
            PracticePay plan lookup.
        related_txn_id: Id class — reference number of the returned-payment ledger entry the fee is for, as shown by
            the PracticePay ledger lookup for that plan.
        fee_amount: Fixed-format class — the returned-payment fee in USD, 2 decimal places, a positive amount; the
            value is stored rounded to the cent.

    Returns:
        A dictionary rendered as text with: pos_txn_id (str, reference number of the new fee entry), pos_plan_id
        (str, the plan charged), related_txn_id (str, the returned-payment entry the fee is for), fee_amount (float,
        USD, 2 decimal places, the fee booked), assessed_date (str, YYYY-MM-DD, today's date) and plan_balance (float,
        USD, 2 decimal places, the plan balance including the fee). A pos_txn_id in the receipt means the fee is booked.
    """
    plan = (ctx.find("pos_plans", pos_plan_id=pos_plan_id) or [{}])[0]
    amount = round(float(fee_amount), 2)
    today = ctx.now()[:10]
    rid = ctx.make_id("ptx_", pos_plan_id, related_txn_id, amount)
    ctx.create("pos_transactions", rid, pos_txn_id=rid, pos_plan_id=pos_plan_id,
               customer_id=plan.get("customer_id"), event_type="pos_returned_payment_fee_assessed",
               txn_date=today, amount=amount, related_txn_id=related_txn_id)
    new_balance = round(float(plan.get("plan_balance") or 0) + amount, 2)
    ctx.update("pos_plans", pos_plan_id, plan_balance=new_balance)
    return str({"pos_txn_id": rid, "pos_plan_id": pos_plan_id, "related_txn_id": related_txn_id,
                "fee_amount": amount, "assessed_date": today, "plan_balance": new_balance})


@tool(owner="agent", rw="write")
def assess_late_fee_02ab9d3a(ctx: ToolContext, pos_plan_id: str, installment_due_date: str, fee_amount: float) -> str:
    """Charge a late fee to a PracticePay plan for one monthly due date whose payment stayed unpaid.

    The service desk books one late-fee entry on the plan's ledger, dated today and tied to the monthly due date it
    is charged for, and raises the plan balance by the fee. The patient sees the late fee on the plan's ledger and in
    the higher balance; the receipt confirms the entry booked and the new plan balance.

    Args:
        pos_plan_id: Id class — reference number of the PracticePay plan the fee is charged to, as returned by the
            PracticePay plan lookup.
        installment_due_date: Fixed-format class — the monthly due date the late fee is charged for, written
            YYYY-MM-DD, a calendar date with no time or time zone.
        fee_amount: Fixed-format class — the late fee in USD, 2 decimal places, a positive amount; the value is stored
            rounded to the cent.

    Returns:
        A dictionary rendered as text with: pos_txn_id (str, reference number of the new late-fee entry),
        pos_plan_id (str, the plan charged), installment_due_date (str, YYYY-MM-DD, the due date the fee is for),
        fee_amount (float, USD, 2 decimal places, the fee booked), assessed_date (str, YYYY-MM-DD, today's date) and
        plan_balance (float, USD, 2 decimal places, the plan balance including the fee). A pos_txn_id in the receipt
        means the late fee is booked.
    """
    plan = (ctx.find("pos_plans", pos_plan_id=pos_plan_id) or [{}])[0]
    amount = round(float(fee_amount), 2)
    today = ctx.now()[:10]
    rid = ctx.make_id("ptx_", pos_plan_id, installment_due_date, amount)
    ctx.create("pos_transactions", rid, pos_txn_id=rid, pos_plan_id=pos_plan_id,
               customer_id=plan.get("customer_id"), event_type="pos_late_fee_assessed",
               txn_date=today, amount=amount, installment_due_date=installment_due_date)
    new_balance = round(float(plan.get("plan_balance") or 0) + amount, 2)
    ctx.update("pos_plans", pos_plan_id, plan_balance=new_balance)
    return str({"pos_txn_id": rid, "pos_plan_id": pos_plan_id, "installment_due_date": installment_due_date,
                "fee_amount": amount, "assessed_date": today, "plan_balance": new_balance})


@tool(owner="user", rw="write")
def pay_off_plan_f18fb847(ctx: ToolContext, pos_plan_id: str, bank_account_id: str, payment_amount: float) -> str:
    """Make a one-time payment from a linked bank account to pay a PracticePay plan off.

    The patient authorizes a single online ACH debit from one of their linked bank accounts for the amount given. The
    payment is credited to the plan today toward its oldest unpaid due date, the plan balance falls by the amount
    paid and the amount past due is cleared; any part of the amount beyond what the plan finally owes stays on the
    plan as a credit balance. The receipt confirms the payment entry and the plan balance left after it.

    Args:
        pos_plan_id: Id class — reference number of the PracticePay plan being paid, as returned by the PracticePay
            plan lookup.
        bank_account_id: Id class — reference number of the patient's linked bank account to debit, as returned by
            the linked bank account lookup.
        payment_amount: Fixed-format class — the amount of the one-time payment in USD, 2 decimal places, a positive
            amount; the value is debited and stored rounded to the cent.

    Returns:
        A dictionary rendered as text with: pos_txn_id (str, reference number of the payment entry), pos_plan_id (str,
        the plan paid), bank_account_id (str, the account debited), payment_amount (float, USD, 2 decimal places, the
        amount credited), effective_date (str, YYYY-MM-DD, today's date) and plan_balance (float, USD, 2 decimal
        places, the plan balance left after the payment; a negative figure is a credit balance). A pos_txn_id in the
        receipt means the payment is credited.
    """
    plan = (ctx.find("pos_plans", pos_plan_id=pos_plan_id) or [{}])[0]
    amount = round(float(payment_amount), 2)
    today = ctx.now()[:10]
    rid = ctx.make_id("ptx_", pos_plan_id, bank_account_id, amount)
    ctx.create("pos_transactions", rid, pos_txn_id=rid, pos_plan_id=pos_plan_id,
               customer_id=plan.get("customer_id"), event_type="pos_payment_posted", txn_date=today,
               amount=amount, payment_channel="online_ach", bank_account_id=bank_account_id,
               installment_due_date=plan.get("next_due_date"))
    new_balance = round(float(plan.get("plan_balance") or 0) - amount, 2)
    ctx.update("pos_plans", pos_plan_id, plan_balance=new_balance, amount_past_due=0.0)
    return str({"pos_txn_id": rid, "pos_plan_id": pos_plan_id, "bank_account_id": bank_account_id,
                "payment_amount": amount, "effective_date": today, "plan_balance": new_balance})


@tool(owner="agent", rw="write")
def relieve_late_fee_b1a4bf3c(ctx: ToolContext, pos_plan_id: str, related_txn_id: str, relief_amount: float) -> str:
    """Book a make-up relief on a late fee of a PracticePay plan whose missed monthly payment has been made up.

    The service desk books one waiver entry on the plan's ledger, dated today, on the courtesy basis, naming the
    late-fee entry it relieves, and lowers the plan balance by the amount relieved. The patient sees the relief on the
    plan's ledger and in the lower balance; the receipt confirms the entry and the new plan balance.

    Args:
        pos_plan_id: Id class — reference number of the PracticePay plan, as returned by the PracticePay plan lookup.
        related_txn_id: Id class — reference number of the late-fee entry being relieved, as shown by the PracticePay
            ledger lookup for that plan.
        relief_amount: Fixed-format class — the amount relieved in USD, 2 decimal places, a positive amount; the value
            is stored rounded to the cent.

    Returns:
        A dictionary rendered as text with: pos_txn_id (str, reference number of the waiver entry), pos_plan_id (str,
        the plan), related_txn_id (str, the late-fee entry relieved), relief_amount (float, USD, 2 decimal places, the
        amount relieved), waiver_reason (str, the courtesy basis the entry is booked on), relief_date (str,
        YYYY-MM-DD, today's date) and plan_balance (float, USD, 2 decimal places, the plan balance after the relief).
        A pos_txn_id in the receipt means the relief is booked.
    """
    plan = (ctx.find("pos_plans", pos_plan_id=pos_plan_id) or [{}])[0]
    amount = round(float(relief_amount), 2)
    today = ctx.now()[:10]
    rid = ctx.make_id("ptx_", pos_plan_id, related_txn_id, amount, "late_relief")
    ctx.create("pos_transactions", rid, pos_txn_id=rid, pos_plan_id=pos_plan_id,
               customer_id=plan.get("customer_id"), event_type="pos_fee_waived", txn_date=today, amount=amount,
               related_txn_id=related_txn_id, waiver_reason="courtesy")
    new_balance = round(float(plan.get("plan_balance") or 0) - amount, 2)
    ctx.update("pos_plans", pos_plan_id, plan_balance=new_balance)
    return str({"pos_txn_id": rid, "pos_plan_id": pos_plan_id, "related_txn_id": related_txn_id,
                "relief_amount": amount, "waiver_reason": "courtesy", "relief_date": today,
                "plan_balance": new_balance})


@tool(owner="agent", rw="write")
def relieve_returned_payment_fee_3fbe4785(ctx: ToolContext, pos_plan_id: str, related_txn_id: str, relief_amount: float) -> str:
    """Book a make-up relief on a returned-payment fee of a PracticePay plan whose returned payment has been replaced.

    The service desk books one waiver entry on the plan's ledger, dated today, on the courtesy basis, naming the
    returned-payment fee entry it relieves, and lowers the plan balance by the amount relieved. The patient sees the
    relief on the plan's ledger and in the lower balance; the receipt confirms the entry and the new plan balance.

    Args:
        pos_plan_id: Id class — reference number of the PracticePay plan, as returned by the PracticePay plan lookup.
        related_txn_id: Id class — reference number of the returned-payment fee entry being relieved, as shown by the
            PracticePay ledger lookup for that plan.
        relief_amount: Fixed-format class — the amount relieved in USD, 2 decimal places, a positive amount; the value
            is stored rounded to the cent.

    Returns:
        A dictionary rendered as text with: pos_txn_id (str, reference number of the waiver entry), pos_plan_id (str,
        the plan), related_txn_id (str, the returned-payment fee entry relieved), relief_amount (float, USD, 2 decimal
        places, the amount relieved), waiver_reason (str, the courtesy basis the entry is booked on), relief_date
        (str, YYYY-MM-DD, today's date) and plan_balance (float, USD, 2 decimal places, the plan balance after the
        relief). A pos_txn_id in the receipt means the relief is booked.
    """
    plan = (ctx.find("pos_plans", pos_plan_id=pos_plan_id) or [{}])[0]
    amount = round(float(relief_amount), 2)
    today = ctx.now()[:10]
    rid = ctx.make_id("ptx_", pos_plan_id, related_txn_id, amount, "returned_relief")
    ctx.create("pos_transactions", rid, pos_txn_id=rid, pos_plan_id=pos_plan_id,
               customer_id=plan.get("customer_id"), event_type="pos_fee_waived", txn_date=today, amount=amount,
               related_txn_id=related_txn_id, waiver_reason="courtesy")
    new_balance = round(float(plan.get("plan_balance") or 0) - amount, 2)
    ctx.update("pos_plans", pos_plan_id, plan_balance=new_balance)
    return str({"pos_txn_id": rid, "pos_plan_id": pos_plan_id, "related_txn_id": related_txn_id,
                "relief_amount": amount, "waiver_reason": "courtesy", "relief_date": today,
                "plan_balance": new_balance})


@tool(owner="user", rw="write")
def reset_monthly_payment_233e8b10(ctx: ToolContext, pos_plan_id: str, monthly_payment_amount: float, plan_apr: float) -> str:
    """Reset the monthly payment and the rate of the customer's own PracticePay plan at the customer's request.

    The patient confirms the monthly payment and the annual rate given as the plan's required monthly payment and its
    rate from now on. Only the plan's monthly payment and APR change to the values given; the due day, the next due
    date and the AutoPay setting stay as they are. The receipt shows the payment and rate now in force.

    Args:
        pos_plan_id: Id class — reference number of the PracticePay plan being reset, as returned by the PracticePay
            plan lookup.
        monthly_payment_amount: Fixed-format class — the required monthly payment from now on in USD, 2 decimal places,
            a positive amount; the value is stored rounded to the cent.
        plan_apr: Fixed-format class — the annual rate from now on, annual rate in percent, 2 decimal places, written as
            the number of percentage points; the value is stored rounded to 2 decimal places.

    Returns:
        A dictionary rendered as text with: pos_plan_id (str, the plan updated), monthly_payment_amount (float, USD, 2
        decimal places, the monthly payment now in force), plan_apr (float, annual rate in percent, 2 decimal places,
        the rate now in force), autopay_enrolled (bool, the unchanged AutoPay setting), payment_due_day (int, the
        unchanged due day) and next_due_date (str, YYYY-MM-DD, the unchanged next due date). The new amount in the
        receipt means the reset is in force.
    """
    plan = (ctx.find("pos_plans", pos_plan_id=pos_plan_id) or [{}])[0]
    amount = round(float(monthly_payment_amount), 2)
    rate = round(float(plan_apr), 2)
    ctx.update("pos_plans", pos_plan_id, monthly_payment_amount=amount, plan_apr=rate)
    return str({"pos_plan_id": pos_plan_id, "monthly_payment_amount": amount, "plan_apr": rate,
                "autopay_enrolled": plan.get("autopay_enrolled"), "payment_due_day": plan.get("payment_due_day"),
                "next_due_date": plan.get("next_due_date")})

"""Hidden task tools of the patient_payment_plans difficulty (Patient Payment Plan, category payplan).

Every tool here is reached only through unlock_* -> call_*; its name is published solely as the
target_tool of an extended policy in payplan.extended.yaml. Each tool performs one atomic write on
the payment plan ledger and decides nothing: eligibility, amounts and timing are worked out by the
agent from the published policy and the records for each call.
"""

from erlbench import ToolContext, tool


@tool(owner="agent", rw="write")
def assess_payment_plan_late_fee_b662389f(ctx: ToolContext, payment_plan_id: str, installment_due_date: str,
                                          amount: float) -> dict:
    """Book a late-fee entry on a patient payment plan for one missed installment.

    The agent uses this to post the late fee owed for an installment of the patient's payment plan
    agreement that was recorded as missed. One call books exactly one late-fee entry, dated today,
    tied to the installment named by its due date, and adds the fee amount to the balance the patient
    owes under the plan. The patient sees the fee as a new line on the plan's history and in the plan
    balance. The receipt returns the reference of the new entry and the plan balance including the new fee.

    Args:
        payment_plan_id: Id class — the reference number of the patient's payment plan agreement, as
            returned by the payment plan lookup for this patient.
        installment_due_date: Fixed-format class — the due date of the missed installment the fee is
            for, written YYYY-MM-DD exactly as it appears on that installment's missed-installment
            entry in the plan history; no time of day and no time zone.
        amount: Fixed-format class — the late fee being added to the plan balance, in USD as a
            positive number with 2 decimal places (cents); it is stored rounded to the cent.

    Returns:
        A dictionary confirming the posting: fee_entry_id (string, reference of the new late-fee
        entry), payment_plan_id (string, the plan charged), installment_due_date (string, YYYY-MM-DD,
        the installment the fee relates to), amount (number, USD with 2 decimal places, the fee
        booked), plan_balance (number, USD with 2 decimal places, the balance owed under the plan
        including this fee) and status (string, always "fee_posted" when the entry was booked).
    """
    amt = round(float(amount), 2)
    rows = ctx.find("payment_plans", payment_plan_id=payment_plan_id)
    plan = rows[0] if rows else {}
    rid = ctx.make_id("ppe_", payment_plan_id, installment_due_date, amt, "late_fee")
    ctx.create("payment_plan_events", rid, payment_plan_event_id=rid, payment_plan_id=payment_plan_id,
               customer_id=plan.get("customer_id"), event_type="payplan_fee_assessed",
               event_date=ctx.now()[:10], fee_kind="late_fee", installment_due_date=installment_due_date,
               amount=amt)
    balance = round(float(plan.get("plan_balance") or 0) + amt, 2)
    ctx.update("payment_plans", payment_plan_id, plan_balance=balance)
    return {"fee_entry_id": rid, "payment_plan_id": payment_plan_id, "installment_due_date": installment_due_date,
            "amount": amt, "plan_balance": balance, "status": "fee_posted"}


@tool(owner="user", rw="write")
def pay_payment_plan_past_due_400c78cb(ctx: ToolContext, payment_plan_id: str, installment_due_date: str,
                                       amount: float, payment_method: str) -> dict:
    """Make a catch-up payment on your own past-due patient payment plan and bring it current.

    The patient uses this to pay, in one payment, the catch-up amount the representative has quoted
    for their payment plan agreement. One call records exactly one installment payment dated today,
    taken by phone with the method the patient chooses and tied to the most recent missed installment
    by its due date; the amount is taken off the balance owed under the plan and the agreement is
    marked current (active) again. The receipt returns the payment reference, the new plan balance and
    the plan status, which the patient can see straight away.

    Args:
        payment_plan_id: Id class — the reference number of the patient's payment plan agreement,
            read to the patient by the representative from the payment plan lookup.
        installment_due_date: Fixed-format class — the due date of the most recent missed installment
            this catch-up payment is recorded against, written YYYY-MM-DD as shown on that missed
            installment in the plan history; no time of day and no time zone.
        amount: Fixed-format class — the catch-up amount being paid, in USD as a positive number with
            2 decimal places (cents); it is stored rounded to the cent.
        payment_method: Enum class — how the patient pays: card (a credit or debit card read out on
            the call), ach (a bank transfer from a checking or savings account the patient gives),
            check (a mailed paper check the patient commits to), cash (cash handed in at a clinic
            front desk), hsa_fsa_card (a health savings or flexible spending account card).

    Returns:
        A dictionary confirming the payment: payment_id (string, reference of the payment entry),
        payment_plan_id (string, the plan paid), installment_due_date (string, YYYY-MM-DD, the missed
        installment the payment is recorded against), amount (number, USD with 2 decimal places, the
        amount paid), payment_method (string, the method used), plan_balance (number, USD with 2
        decimal places, the balance still owed net of this payment) and plan_status (string, always
        "active" once the payment is recorded).
    """
    amt = round(float(amount), 2)
    rows = ctx.find("payment_plans", payment_plan_id=payment_plan_id)
    plan = rows[0] if rows else {}
    rid = ctx.make_id("ppp_", payment_plan_id, installment_due_date, amt, payment_method)
    ctx.create("payment_plan_events", rid, payment_plan_event_id=rid, payment_plan_id=payment_plan_id,
               customer_id=plan.get("customer_id"), event_type="payplan_payment_received",
               event_date=ctx.now()[:10], payment_kind="installment", installment_due_date=installment_due_date,
               amount=amt, payment_method=payment_method, channel="phone")
    balance = round(float(plan.get("plan_balance") or 0) - amt, 2)
    ctx.update("payment_plans", payment_plan_id, plan_balance=balance, status="active")
    return {"payment_id": rid, "payment_plan_id": payment_plan_id, "installment_due_date": installment_due_date,
            "amount": amt, "payment_method": payment_method, "plan_balance": balance, "plan_status": "active"}


@tool(owner="agent", rw="write")
def book_payment_plan_returned_fee_3086fcb8(ctx: ToolContext, payment_plan_id: str, installment_due_date: str,
                                           amount: float) -> dict:
    """Book a returned-payment fee entry on a patient payment plan for one bank draft that came back unpaid.

    The agent uses this to post the returned-payment fee owed when an automatic bank draft for an
    installment of the patient's payment plan agreement was returned by the bank. One call books
    exactly one returned-payment fee entry, dated today, tied to the installment named by its due
    date, and adds the fee amount to the balance the patient owes under the plan. The patient sees
    the fee as a new line on the plan's history and in the plan balance. The receipt returns the
    reference of the new entry and the plan balance including the fee.

    Args:
        payment_plan_id: Id class — the reference number of the patient's payment plan agreement, as
            returned by the payment plan lookup for this patient.
        installment_due_date: Fixed-format class — the due date of the installment whose draft came
            back, written YYYY-MM-DD exactly as it appears on that draft's failed-payment entry in the
            plan history; no time of day and no time zone.
        amount: Fixed-format class — the returned-payment fee being added to the plan balance, in USD
            as a positive number with 2 decimal places (cents); it is stored rounded to the cent.

    Returns:
        A dictionary confirming the posting: fee_entry_id (string, reference of the new
        returned-payment fee entry), payment_plan_id (string, the plan charged), installment_due_date
        (string, YYYY-MM-DD, the installment whose draft came back), amount (number, USD with 2
        decimal places, the fee booked), plan_balance (number, USD with 2 decimal places, the balance
        owed under the plan including this fee) and status (string, always "fee_posted" when the
        entry was booked).
    """
    amt = round(float(amount), 2)
    rows = ctx.find("payment_plans", payment_plan_id=payment_plan_id)
    plan = rows[0] if rows else {}
    rid = ctx.make_id("ppe_", payment_plan_id, installment_due_date, amt, "returned_payment_fee")
    ctx.create("payment_plan_events", rid, payment_plan_event_id=rid, payment_plan_id=payment_plan_id,
               customer_id=plan.get("customer_id"), event_type="payplan_fee_assessed",
               event_date=ctx.now()[:10], fee_kind="returned_payment_fee",
               installment_due_date=installment_due_date, amount=amt)
    balance = round(float(plan.get("plan_balance") or 0) + amt, 2)
    ctx.update("payment_plans", payment_plan_id, plan_balance=balance)
    return {"fee_entry_id": rid, "payment_plan_id": payment_plan_id, "installment_due_date": installment_due_date,
            "amount": amt, "plan_balance": balance, "status": "fee_posted"}


@tool(owner="user", rw="write")
def accept_payment_plan_modification_53d89fa9(ctx: ToolContext, payment_plan_id: str, monthly_payment: float,
                                              term_months: int) -> dict:
    """Accept new installment terms on your own patient payment plan agreement.

    The patient uses this to agree, in their own name, to the modified monthly installment and
    number of installments the representative has quoted for their payment plan agreement. One call
    replaces the installment amount and the total number of monthly installments on the agreement
    and counts one modification used on the plan; the balance owed does not change. An installment
    already queued for automatic collection is still drafted at the amount it was scheduled at, and the
    new installment applies to the installments that follow it. The receipt
    returns the new installment, the new number of installments and the modifications used, which
    the patient can see on the agreement straight away.

    Args:
        payment_plan_id: Id class — the reference number of the patient's payment plan agreement,
            read to the patient by the representative from the payment plan lookup.
        monthly_payment: Fixed-format class — the new monthly installment the patient accepts, in USD
            as a positive number with 2 decimal places (cents); it is stored rounded to the cent.
        term_months: Fixed-format class — the new total number of monthly installments on the
            agreement, counting every installment of the plan from its start, as a non-negative integer
            (months).

    Returns:
        A dictionary confirming the change: payment_plan_id (string, the agreement changed),
        monthly_payment (number, USD with 2 decimal places, the installment now in force),
        term_months (integer, the total number of monthly installments now on the agreement),
        modifications_used (integer, modifications of the plan including this one) and status
        (string, always "terms_modified" once the new terms are recorded).
    """
    rows = ctx.find("payment_plans", payment_plan_id=payment_plan_id)
    plan = rows[0] if rows else {}
    used = int(plan.get("modifications_used") or 0) + 1
    pay = round(float(monthly_payment), 2)
    ctx.update("payment_plans", payment_plan_id, monthly_payment=pay, term_months=int(term_months),
               modifications_used=used)
    return {"payment_plan_id": payment_plan_id, "monthly_payment": pay, "term_months": int(term_months),
            "modifications_used": used, "status": "terms_modified"}

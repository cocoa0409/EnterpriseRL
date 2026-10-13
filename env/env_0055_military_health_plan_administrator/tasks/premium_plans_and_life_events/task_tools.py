"""Hidden task tools for the premium_plans_and_life_events difficulty of
env_0055_military_health_plan_administrator (TRICARE Premium-Based Plans).

Each tool performs exactly one atomic write on a premium-based plan and keeps the plan's
premium balance equal to the running total of its premium ledger. No tool checks a policy
precondition: which entry is owed, against which bill and for how much is decided by the
caller from the published policy and the records before the call.
"""

from erlbench import ToolContext, tool


class _PlanLedger:
    """Shared bookkeeping for the tools below (not a tool): lays out one premium-ledger entry and
    the plan's new cached premium balance, so that each tool can book the entry and keep the
    balance equal to the running total of the plan's premium ledger."""

    @staticmethod
    def purchaser(ctx: ToolContext, premium_enrollment_id: str) -> str:
        rows = ctx.find("premium_plan_enrollments", premium_enrollment_id=premium_enrollment_id)
        return rows[0].get("customer_id") if rows else ""

    @staticmethod
    def new_balance(ctx: ToolContext, premium_enrollment_id: str, delta: float):
        rows = ctx.find("premium_plan_enrollments", premium_enrollment_id=premium_enrollment_id)
        if not rows:
            return None
        return round(float(rows[0].get("premium_balance_due") or 0.0) + delta, 2)

    @staticmethod
    def credit_row(ctx: ToolContext, prefix: str, premium_enrollment_id: str, related_premium_entry_id: str,
                   coverage_month: str, coverage_days: int, amount: float, reason: str):
        amt = round(float(amount), 2)
        days = int(coverage_days)
        rid = ctx.make_id(prefix, premium_enrollment_id, related_premium_entry_id, coverage_month, days, amt, reason)
        row = dict(premium_entry_id=rid, premium_enrollment_id=premium_enrollment_id,
                   customer_id=_PlanLedger.purchaser(ctx, premium_enrollment_id),
                   event_type="premium_proration_credit", coverage_month=coverage_month, due_date="",
                   billing_kind="not_applicable", coverage_days=days, amount=amt, posted_date=ctx.now()[:10],
                   payment_method="not_applicable", adjustment_reason=reason,
                   related_premium_entry_id=related_premium_entry_id)
        return rid, row

    @staticmethod
    def credit_receipt(row: dict, balance) -> str:
        return str({"premium_entry_id": row["premium_entry_id"], "premium_enrollment_id": row["premium_enrollment_id"],
                    "related_premium_entry_id": row["related_premium_entry_id"], "coverage_month": row["coverage_month"],
                    "coverage_days": row["coverage_days"], "amount": row["amount"],
                    "adjustment_reason": row["adjustment_reason"],
                    "premium_balance_due": 0.0 if balance is None else balance, "status": "posted"})


@tool(owner="agent", rw="write")
def post_early_duty_month_credit_9948ac5b(ctx: ToolContext, premium_enrollment_id: str, related_premium_entry_id: str,
        coverage_month: str, coverage_days: int, amount: float) -> str:
    """Post an activation-on-orders credit on a TRICARE Reserve Select plan against the monthly bill of
    a coverage month the purchaser has already paid, returning the premium for the days of that
    month on which the purchaser's active duty TRICARE coverage overlapped the plan. One call
    books one credit entry (reason: activation on orders) on the plan's premium ledger, tied to
    the named bill and coverage month, and lowers the plan's premium balance by the credited
    amount. The receipt confirms the new credit entry and the plan's resulting balance.

    Args:
        premium_enrollment_id: Id class — the reference number of the premium-based plan, as returned
            by the premium-plan lookup for the purchaser.
        related_premium_entry_id: Id class — the reference number of the monthly bill the credit is posted
            against, as returned by the premium-ledger lookup for the plan.
        coverage_month: Fixed-format class — the coverage month of that bill, written YYYY-MM exactly as
            the bill shows it.
        coverage_days: Fixed-format class — the number of days of that month the credit covers, an
            integer from 1 to 31.
        amount: Fixed-format class — the credit amount in USD, a positive number with 2 decimal places,
            already rounded to the cent; it is booked exactly as given.

    Returns:
        A dictionary rendered as text with premium_entry_id (str, reference number of the new credit
        entry), premium_enrollment_id (str, the plan), related_premium_entry_id (str, the bill credited),
        coverage_month (str, YYYY-MM), coverage_days (int), amount (float, USD with 2 decimal places),
        adjustment_reason (str, always activation_on_orders), premium_balance_due (float, the plan's premium balance
        in USD after the credit; negative means money is owed to the purchaser) and status (str,
        "posted" once the credit is booked).
    """
    rid, row = _PlanLedger.credit_row(ctx, "pde_", premium_enrollment_id, related_premium_entry_id,
                                      coverage_month, coverage_days, amount, "activation_on_orders")
    ctx.create("premium_ledger", rid, **row)
    balance = _PlanLedger.new_balance(ctx, premium_enrollment_id, -row["amount"])
    if balance is not None:
        ctx.update("premium_plan_enrollments", premium_enrollment_id, premium_balance_due=balance)
    return _PlanLedger.credit_receipt(row, balance)


@tool(owner="agent", rw="write")
def relieve_family_adjustment_280360d9(ctx: ToolContext, premium_enrollment_id: str, related_premium_entry_id: str,
        coverage_month: str, coverage_days: int, amount: float) -> str:
    """Post an activation-on-orders credit on a TRICARE Reserve Select plan against a coverage-type
    adjustment bill, relieving the added family premium for the days that bill covers on which
    the purchaser's active duty TRICARE coverage also covered the family; the bill need not
    carry a payment. One call books one credit entry (reason: activation on orders) tied to the
    named adjustment bill and coverage month, and lowers the plan's premium balance by the
    relieved amount. The receipt confirms the new credit entry and the plan's resulting balance.

    Args:
        premium_enrollment_id: Id class — the reference number of the premium-based plan, as returned
            by the premium-plan lookup for the purchaser.
        related_premium_entry_id: Id class — the reference number of the coverage-type adjustment bill the credit is posted
            against, as returned by the premium-ledger lookup for the plan.
        coverage_month: Fixed-format class — the coverage month of that bill, written YYYY-MM exactly as
            the bill shows it.
        coverage_days: Fixed-format class — the number of days of that month the credit covers, an
            integer from 1 to 31.
        amount: Fixed-format class — the credit amount in USD, a positive number with 2 decimal places,
            already rounded to the cent; it is booked exactly as given.

    Returns:
        A dictionary rendered as text with premium_entry_id (str, reference number of the new credit
        entry), premium_enrollment_id (str, the plan), related_premium_entry_id (str, the bill credited),
        coverage_month (str, YYYY-MM), coverage_days (int), amount (float, USD with 2 decimal places),
        adjustment_reason (str, always activation_on_orders), premium_balance_due (float, the plan's premium balance
        in USD after the credit; negative means money is owed to the purchaser) and status (str,
        "posted" once the credit is booked).
    """
    rid, row = _PlanLedger.credit_row(ctx, "pfa_", premium_enrollment_id, related_premium_entry_id,
                                      coverage_month, coverage_days, amount, "activation_on_orders")
    ctx.create("premium_ledger", rid, **row)
    balance = _PlanLedger.new_balance(ctx, premium_enrollment_id, -row["amount"])
    if balance is not None:
        ctx.update("premium_plan_enrollments", premium_enrollment_id, premium_balance_due=balance)
    return _PlanLedger.credit_receipt(row, balance)


@tool(owner="agent", rw="write")
def relieve_later_month_family_adjustment_600a6ce9(ctx: ToolContext, premium_enrollment_id: str, related_premium_entry_id: str,
        coverage_month: str, coverage_days: int, amount: float) -> str:
    """Post an activation-on-orders credit on a TRICARE Reserve Select plan against the coverage-type
    adjustment bill of a coverage month billed in advance, later than the most recently paid
    month, relieving the added family premium for the days of that month on which the
    purchaser's active duty TRICARE coverage also covered the family; the bill need not carry a
    payment. One call books one credit entry (reason: activation on orders) tied to the named
    adjustment bill and coverage month, and lowers the plan's premium balance by the relieved
    amount. The receipt confirms the new credit entry and the plan's resulting balance.

    Args:
        premium_enrollment_id: Id class — the reference number of the premium-based plan, as returned
            by the premium-plan lookup for the purchaser.
        related_premium_entry_id: Id class — the reference number of the coverage-type adjustment bill the credit is posted
            against, as returned by the premium-ledger lookup for the plan.
        coverage_month: Fixed-format class — the coverage month of that bill, written YYYY-MM exactly as
            the bill shows it.
        coverage_days: Fixed-format class — the number of days of that month the credit covers, an
            integer from 1 to 31.
        amount: Fixed-format class — the credit amount in USD, a positive number with 2 decimal places,
            already rounded to the cent; it is booked exactly as given.

    Returns:
        A dictionary rendered as text with premium_entry_id (str, reference number of the new credit
        entry), premium_enrollment_id (str, the plan), related_premium_entry_id (str, the bill credited),
        coverage_month (str, YYYY-MM), coverage_days (int), amount (float, USD with 2 decimal places),
        adjustment_reason (str, always activation_on_orders), premium_balance_due (float, the plan's premium balance
        in USD after the credit; negative means money is owed to the purchaser) and status (str,
        "posted" once the credit is booked).
    """
    rid, row = _PlanLedger.credit_row(ctx, "pfl_", premium_enrollment_id, related_premium_entry_id,
                                      coverage_month, coverage_days, amount, "activation_on_orders")
    ctx.create("premium_ledger", rid, **row)
    balance = _PlanLedger.new_balance(ctx, premium_enrollment_id, -row["amount"])
    if balance is not None:
        ctx.update("premium_plan_enrollments", premium_enrollment_id, premium_balance_due=balance)
    return _PlanLedger.credit_receipt(row, balance)


@tool(owner="user", rw="write")
def confirm_reserve_select_ending_f251f30d(ctx: ToolContext, premium_request_id: str, premium_enrollment_id: str, termination_date: str,
        related_premium_entry_id: str, coverage_month: str, coverage_days: int, amount: float) -> str:
    """The purchaser of a TRICARE Reserve Select plan confirms in person the ending of the plan they
    asked for. The confirmation marks the purchaser's pending request to end the plan as
    confirmed and ends the plan (status terminated by request) on the termination date given. As
    the consequence of that confirmation, the plan books its closing reconciliation: one
    termination-by-request credit tied to the named bill and coverage month, for the amount
    stated, which lowers the plan's premium balance by that amount. The receipt confirms the
    request, the plan's ended status and termination date, the closing-reconciliation credit
    entry and the resulting balance.

    Args:
        premium_request_id: Id class — the reference number of the purchaser's pending request to end
            the plan, as the representative reads it out from the plan's request record.
        premium_enrollment_id: Id class — the reference number of the premium-based plan being ended,
            as the representative reads it out from the purchaser's plan record.
        termination_date: Fixed-format class — the last day of coverage, written YYYY-MM-DD, exactly as
            the representative reads it out.
        related_premium_entry_id: Id class — the reference number of the monthly bill the closing
            reconciliation is posted against, as the representative reads it out from the premium ledger.
        coverage_month: Fixed-format class — the coverage month of that bill, written YYYY-MM exactly as
            the bill shows it.
        coverage_days: Fixed-format class — the number of days of that month the closing reconciliation
            counts, an integer from 1 to 31, exactly as the representative reads it out.
        amount: Fixed-format class — the closing reconciliation in USD, a positive number with 2 decimal
            places, already rounded to the cent, exactly as the representative states it.

    Returns:
        A dictionary rendered as text with premium_request_id (str, the request confirmed),
        request_outcome (str, always confirmed), premium_enrollment_id (str, the plan ended),
        plan_status (str, always terminated_by_request), termination_date (str, YYYY-MM-DD),
        premium_entry_id (str, reference number of the new credit entry), related_premium_entry_id
        (str, the bill credited), coverage_month (str, YYYY-MM), coverage_days (int), amount (float, USD
        with 2 decimal places), adjustment_reason (str, always termination_by_request) and
        premium_balance_due (float, the plan's premium balance in USD after the credit; negative means
        money is owed to the purchaser).
    """
    ctx.update("premium_plan_requests", premium_request_id, outcome="confirmed")
    rid, row = _PlanLedger.credit_row(ctx, "pcr_", premium_enrollment_id, related_premium_entry_id,
                                      coverage_month, coverage_days, amount, "termination_by_request")
    ctx.create("premium_ledger", rid, **row)
    balance = _PlanLedger.new_balance(ctx, premium_enrollment_id, -row["amount"])
    ctx.update("premium_plan_enrollments", premium_enrollment_id, status="terminated_by_request",
               termination_date=termination_date,
               premium_balance_due=0.0 if balance is None else balance)
    return str({"premium_request_id": premium_request_id, "request_outcome": "confirmed",
                "premium_enrollment_id": premium_enrollment_id, "plan_status": "terminated_by_request",
                "termination_date": termination_date, "premium_entry_id": rid,
                "related_premium_entry_id": related_premium_entry_id, "coverage_month": row["coverage_month"],
                "coverage_days": row["coverage_days"], "amount": row["amount"],
                "adjustment_reason": "termination_by_request",
                "premium_balance_due": 0.0 if balance is None else balance})


@tool(owner="agent", rw="write")
def post_recall_paid_month_credit_948d1b7a(ctx: ToolContext, premium_enrollment_id: str, related_premium_entry_id: str,
        coverage_month: str, coverage_days: int, amount: float) -> str:
    """Post an activation-on-orders credit on a TRICARE Retired Reserve plan against the monthly bill
    of a coverage month the purchaser has already paid, returning the premium for the days of
    that month on which the purchaser's active duty TRICARE coverage after a recall overlapped
    the plan. One call books one credit entry (reason: activation on orders) on the plan's
    premium ledger, tied to the named bill and coverage month, and lowers the plan's premium
    balance by the credited amount. The receipt confirms the new credit entry and the plan's
    resulting balance.

    Args:
        premium_enrollment_id: Id class — the reference number of the premium-based plan, as returned
            by the premium-plan lookup for the purchaser.
        related_premium_entry_id: Id class — the reference number of the monthly bill the credit is posted
            against, as returned by the premium-ledger lookup for the plan.
        coverage_month: Fixed-format class — the coverage month of that bill, written YYYY-MM exactly as
            the bill shows it.
        coverage_days: Fixed-format class — the number of days of that month the credit covers, an
            integer from 1 to 31.
        amount: Fixed-format class — the credit amount in USD, a positive number with 2 decimal places,
            already rounded to the cent; it is booked exactly as given.

    Returns:
        A dictionary rendered as text with premium_entry_id (str, reference number of the new credit
        entry), premium_enrollment_id (str, the plan), related_premium_entry_id (str, the bill credited),
        coverage_month (str, YYYY-MM), coverage_days (int), amount (float, USD with 2 decimal places),
        adjustment_reason (str, always activation_on_orders), premium_balance_due (float, the plan's premium balance
        in USD after the credit; negative means money is owed to the purchaser) and status (str,
        "posted" once the credit is booked).
    """
    rid, row = _PlanLedger.credit_row(ctx, "prp_", premium_enrollment_id, related_premium_entry_id,
                                      coverage_month, coverage_days, amount, "activation_on_orders")
    ctx.create("premium_ledger", rid, **row)
    balance = _PlanLedger.new_balance(ctx, premium_enrollment_id, -row["amount"])
    if balance is not None:
        ctx.update("premium_plan_enrollments", premium_enrollment_id, premium_balance_due=balance)
    return _PlanLedger.credit_receipt(row, balance)


@tool(owner="agent", rw="write")
def relieve_recall_adjustment_165573c8(ctx: ToolContext, premium_enrollment_id: str, related_premium_entry_id: str,
        coverage_month: str, coverage_days: int, amount: float) -> str:
    """Post an activation-on-orders credit on a TRICARE Retired Reserve plan against a coverage-type
    adjustment bill, relieving the added family premium for the days that bill covers on which
    the purchaser's active duty TRICARE coverage after a recall also covered the family; the
    bill need not carry a payment. One call books one credit entry (reason: activation on
    orders) tied to the named adjustment bill and coverage month, and lowers the plan's premium
    balance by the relieved amount. The receipt confirms the new credit entry and the plan's
    resulting balance.

    Args:
        premium_enrollment_id: Id class — the reference number of the premium-based plan, as returned
            by the premium-plan lookup for the purchaser.
        related_premium_entry_id: Id class — the reference number of the coverage-type adjustment bill the credit is posted
            against, as returned by the premium-ledger lookup for the plan.
        coverage_month: Fixed-format class — the coverage month of that bill, written YYYY-MM exactly as
            the bill shows it.
        coverage_days: Fixed-format class — the number of days of that month the credit covers, an
            integer from 1 to 31.
        amount: Fixed-format class — the credit amount in USD, a positive number with 2 decimal places,
            already rounded to the cent; it is booked exactly as given.

    Returns:
        A dictionary rendered as text with premium_entry_id (str, reference number of the new credit
        entry), premium_enrollment_id (str, the plan), related_premium_entry_id (str, the bill credited),
        coverage_month (str, YYYY-MM), coverage_days (int), amount (float, USD with 2 decimal places),
        adjustment_reason (str, always activation_on_orders), premium_balance_due (float, the plan's premium balance
        in USD after the credit; negative means money is owed to the purchaser) and status (str,
        "posted" once the credit is booked).
    """
    rid, row = _PlanLedger.credit_row(ctx, "pra_", premium_enrollment_id, related_premium_entry_id,
                                      coverage_month, coverage_days, amount, "activation_on_orders")
    ctx.create("premium_ledger", rid, **row)
    balance = _PlanLedger.new_balance(ctx, premium_enrollment_id, -row["amount"])
    if balance is not None:
        ctx.update("premium_plan_enrollments", premium_enrollment_id, premium_balance_due=balance)
    return _PlanLedger.credit_receipt(row, balance)


@tool(owner="agent", rw="write")
def relieve_recall_later_month_3979698d(ctx: ToolContext, premium_enrollment_id: str, related_premium_entry_id: str,
        coverage_month: str, coverage_days: int, amount: float) -> str:
    """Post an activation-on-orders credit on a TRICARE Retired Reserve plan against the monthly bill
    of a coverage month billed in advance, later than the most recently paid month, relieving
    the premium that monthly bill charges for the days of that month on which the purchaser's
    active duty TRICARE coverage after a recall covered the plan; the bill need not carry a
    payment. One call books one credit entry (reason: activation on orders) tied to the named
    monthly bill and coverage month, and lowers the plan's premium balance by the relieved
    amount. The receipt confirms the new credit entry and the plan's resulting balance.

    Args:
        premium_enrollment_id: Id class — the reference number of the premium-based plan, as returned
            by the premium-plan lookup for the purchaser.
        related_premium_entry_id: Id class — the reference number of the monthly bill the credit is posted
            against, as returned by the premium-ledger lookup for the plan.
        coverage_month: Fixed-format class — the coverage month of that bill, written YYYY-MM exactly as
            the bill shows it.
        coverage_days: Fixed-format class — the number of days of that month the credit covers, an
            integer from 1 to 31.
        amount: Fixed-format class — the credit amount in USD, a positive number with 2 decimal places,
            already rounded to the cent; it is booked exactly as given.

    Returns:
        A dictionary rendered as text with premium_entry_id (str, reference number of the new credit
        entry), premium_enrollment_id (str, the plan), related_premium_entry_id (str, the bill credited),
        coverage_month (str, YYYY-MM), coverage_days (int), amount (float, USD with 2 decimal places),
        adjustment_reason (str, always activation_on_orders), premium_balance_due (float, the plan's premium balance
        in USD after the credit; negative means money is owed to the purchaser) and status (str,
        "posted" once the credit is booked).
    """
    rid, row = _PlanLedger.credit_row(ctx, "prl_", premium_enrollment_id, related_premium_entry_id,
                                      coverage_month, coverage_days, amount, "activation_on_orders")
    ctx.create("premium_ledger", rid, **row)
    balance = _PlanLedger.new_balance(ctx, premium_enrollment_id, -row["amount"])
    if balance is not None:
        ctx.update("premium_plan_enrollments", premium_enrollment_id, premium_balance_due=balance)
    return _PlanLedger.credit_receipt(row, balance)


@tool(owner="user", rw="write")
def confirm_retired_reserve_ending_efdb5596(ctx: ToolContext, premium_request_id: str, premium_enrollment_id: str, termination_date: str,
        related_premium_entry_id: str, coverage_month: str, coverage_days: int, amount: float) -> str:
    """The purchaser of a TRICARE Retired Reserve plan confirms in person the ending of the plan they
    asked for. The confirmation marks the purchaser's pending request to end the plan as
    confirmed and ends the plan (status terminated by request) on the termination date given. As
    the consequence of that confirmation, the plan books its closing reconciliation: one
    termination-by-request credit tied to the named bill and coverage month, for the amount
    stated, which lowers the plan's premium balance by that amount. The receipt confirms the
    request, the plan's ended status and termination date, the closing-reconciliation credit
    entry and the resulting balance.

    Args:
        premium_request_id: Id class — the reference number of the purchaser's pending request to end
            the plan, as the representative reads it out from the plan's request record.
        premium_enrollment_id: Id class — the reference number of the premium-based plan being ended,
            as the representative reads it out from the purchaser's plan record.
        termination_date: Fixed-format class — the last day of coverage, written YYYY-MM-DD, exactly as
            the representative reads it out.
        related_premium_entry_id: Id class — the reference number of the monthly bill the closing
            reconciliation is posted against, as the representative reads it out from the premium ledger.
        coverage_month: Fixed-format class — the coverage month of that bill, written YYYY-MM exactly as
            the bill shows it.
        coverage_days: Fixed-format class — the number of days of that month the closing reconciliation
            counts, an integer from 1 to 31, exactly as the representative reads it out.
        amount: Fixed-format class — the closing reconciliation in USD, a positive number with 2 decimal
            places, already rounded to the cent, exactly as the representative states it.

    Returns:
        A dictionary rendered as text with premium_request_id (str, the request confirmed),
        request_outcome (str, always confirmed), premium_enrollment_id (str, the plan ended),
        plan_status (str, always terminated_by_request), termination_date (str, YYYY-MM-DD),
        premium_entry_id (str, reference number of the new credit entry), related_premium_entry_id
        (str, the bill credited), coverage_month (str, YYYY-MM), coverage_days (int), amount (float, USD
        with 2 decimal places), adjustment_reason (str, always termination_by_request) and
        premium_balance_due (float, the plan's premium balance in USD after the credit; negative means
        money is owed to the purchaser).
    """
    ctx.update("premium_plan_requests", premium_request_id, outcome="confirmed")
    rid, row = _PlanLedger.credit_row(ctx, "pcq_", premium_enrollment_id, related_premium_entry_id,
                                      coverage_month, coverage_days, amount, "termination_by_request")
    ctx.create("premium_ledger", rid, **row)
    balance = _PlanLedger.new_balance(ctx, premium_enrollment_id, -row["amount"])
    ctx.update("premium_plan_enrollments", premium_enrollment_id, status="terminated_by_request",
               termination_date=termination_date,
               premium_balance_due=0.0 if balance is None else balance)
    return str({"premium_request_id": premium_request_id, "request_outcome": "confirmed",
                "premium_enrollment_id": premium_enrollment_id, "plan_status": "terminated_by_request",
                "termination_date": termination_date, "premium_entry_id": rid,
                "related_premium_entry_id": related_premium_entry_id, "coverage_month": row["coverage_month"],
                "coverage_days": row["coverage_days"], "amount": row["amount"],
                "adjustment_reason": "termination_by_request",
                "premium_balance_due": 0.0 if balance is None else balance})

"""Hidden task tools for metro_gym_chain / corporate_wellness_partnerships.
Path: env/metro_gym_chain/tasks/corporate_wellness_partnerships/task_tools.py

Output of erl-task-instantiate. Every tool here is HIDDEN (absent from every tool list); the agent
discovers a tool's name only through this difficulty's extended policy target_tool / a workflow
step, and reaches it through unlock_agent_discoverable_tool -> call_agent_discoverable_tool (or the
user-owned pair for owner="user" tools). Each tool performs exactly one atomic state change; every
multi-factor value it receives (a billed amount, a payment allocation, a waiver, a reinstatement
fee) has already been computed by the agent from policy, history, tier and cross-category reads
before the call -- no tool aggregates history or judges a policy precondition on the agent's behalf.
"""

from erlbench import ToolContext, tool


# ---------------------------------------------------------------------------
# Task 0 tools -- new-enrollment onboarding workflow + wellness-reimbursement waiver
# ---------------------------------------------------------------------------

@tool(owner="agent", rw="write")
def activate_corp_enrollment_8f54bf3c(ctx: ToolContext, enrollment_id: str) -> str:
    """Activate a pending corporate wellness enrollment on the representative's own initiative,
    once the employee's proof of employment has been reviewed in this conversation. This
    transitions the enrollment's lifecycle status from applied to active; it does not itself bill
    anything.

    Args:
        enrollment_id: Id class — the reference number of the enrollment to activate, read from the
            enrollment record returned when the enrollment was located or created.

    Returns:
        A string confirming the enrollment reference number and that its lifecycle status is now
        active.
    """
    rows = ctx.find("corporate_wellness_enrollments", enrollment_id=enrollment_id)
    if not rows:
        return f"Error: no corporate wellness enrollment {enrollment_id}."
    ctx.update("corporate_wellness_enrollments", enrollment_id, status="active")
    return f"Enrollment {enrollment_id} activated; status is now active."


@tool(owner="agent", rw="write")
def bill_corp_enrollment_dues_4e718c02(ctx: ToolContext, enrollment_id: str, amount_usd: float,
                                        billing_cycle_month: str) -> str:
    """Bill the employer's master account for this employee's recurring corporate wellness dues
    for one billing cycle. This adds one dues-billed entry to the enrollment's billing history and
    increases the net amount currently owed by the employer's master account for this employee's
    enrollment by the same amount.

    Args:
        enrollment_id: Id class — the reference number of the enrollment being billed, read from
            the enrollment record.
        amount_usd: Fixed-format class — the dollar amount to bill, in USD (the unit of every amount
            in this system), rounded to exactly 2 decimal places; do not pass an amount that has
            not already been rounded to the cent.
        billing_cycle_month: Fixed-format class — the billing cycle this charge covers, in YYYY-MM
            form (four-digit year, hyphen, two-digit month).

    Returns:
        A string confirming the new billing-history entry's reference number (event_id), the amount
        billed, the billing cycle it covers, and the enrollment's resulting balance owed by the
        employer's master account.
    """
    rows = ctx.find("corporate_wellness_enrollments", enrollment_id=enrollment_id)
    if not rows:
        return f"Error: no corporate wellness enrollment {enrollment_id}."
    enr = rows[0]
    amt = round(float(amount_usd), 2)
    rid = ctx.make_id("cwv_", enrollment_id, billing_cycle_month, ctx.now())
    ctx.create("corporate_wellness_events", rid, event_id=rid, enrollment_id=enrollment_id,
               customer_id=enr["customer_id"], event_type="corp_dues_billed",
               event_timestamp=ctx.now(), amount_usd=amt, billing_cycle_month=billing_cycle_month,
               employer_account_id=enr["employer_account_id"])
    new_balance = round(float(enr.get("corporate_dues_balance") or 0.0) + amt, 2)
    ctx.update("corporate_wellness_enrollments", enrollment_id, corporate_dues_balance=new_balance)
    return (f"Billed {amt:.2f} to enrollment {enrollment_id} for cycle {billing_cycle_month} "
            f"(entry {rid}); balance owed is now {new_balance:.2f}.")


@tool(owner="user", rw="write")
def record_corp_dues_payment_5148c010(ctx: ToolContext, enrollment_id: str,
                                       amount_usd: float) -> str:
    """Let the employee confirm and post their employer's payment against their own corporate
    wellness balance, on the employer's behalf. This adds one payment entry to the enrollment's
    billing history and decreases the net amount currently owed by the employer's master account
    for this employee's enrollment by the same amount.

    Args:
        enrollment_id: Id class — the reference number of the enrollment the payment is being
            applied to, read from the enrollment record.
        amount_usd: Fixed-format class — the dollar amount actually applied against the balance, in
            USD (the unit of every amount in this system), rounded to exactly 2 decimal places; do
            not pass an amount that has not already been rounded to the cent.

    Returns:
        A string confirming the new payment-history entry's reference number (event_id), the amount
        applied, and the enrollment's resulting balance owed by the employer's master account.
    """
    rows = ctx.find("corporate_wellness_enrollments", enrollment_id=enrollment_id)
    if not rows:
        return f"Error: no corporate wellness enrollment {enrollment_id}."
    enr = rows[0]
    amt = round(float(amount_usd), 2)
    rid = ctx.make_id("cwp_", enrollment_id, amt, ctx.now())
    ctx.create("corporate_wellness_events", rid, event_id=rid, enrollment_id=enrollment_id,
               customer_id=enr["customer_id"], event_type="corp_dues_payment_received",
               event_timestamp=ctx.now(), amount_usd=amt, billing_cycle_month="",
               employer_account_id=enr["employer_account_id"])
    new_balance = round(float(enr.get("corporate_dues_balance") or 0.0) - amt, 2)
    ctx.update("corporate_wellness_enrollments", enrollment_id, corporate_dues_balance=new_balance)
    return (f"Payment of {amt:.2f} applied to enrollment {enrollment_id} (entry {rid}); balance "
            f"owed is now {new_balance:.2f}.")


@tool(owner="agent", rw="write")
def waive_corp_wellness_reimbursement_b40ef430(ctx: ToolContext, enrollment_id: str,
                                                amount_usd: float) -> str:
    """Waive part of this employee's corporate wellness balance as an employer-funded wellness-
    reimbursement credit. This adds one waiver entry to the enrollment's billing history and
    decreases the net amount currently owed by the employer's master account for this employee's
    enrollment by the same amount.

    Args:
        enrollment_id: Id class — the reference number of the enrollment the waiver is being
            applied to, read from the enrollment record.
        amount_usd: Fixed-format class — the dollar amount to waive, in USD (the unit of every amount
            in this system), rounded to exactly 2 decimal places; do not pass an amount that has
            not already been rounded to the cent.

    Returns:
        A string confirming the new waiver-history entry's reference number (event_id), the amount
        waived, and the enrollment's resulting balance owed by the employer's master account.
    """
    rows = ctx.find("corporate_wellness_enrollments", enrollment_id=enrollment_id)
    if not rows:
        return f"Error: no corporate wellness enrollment {enrollment_id}."
    enr = rows[0]
    amt = round(float(amount_usd), 2)
    rid = ctx.make_id("cww_", enrollment_id, amt, ctx.now())
    ctx.create("corporate_wellness_events", rid, event_id=rid, enrollment_id=enrollment_id,
               customer_id=enr["customer_id"], event_type="corp_dues_waived",
               event_timestamp=ctx.now(), amount_usd=amt, billing_cycle_month="",
               employer_account_id=enr["employer_account_id"])
    new_balance = round(float(enr.get("corporate_dues_balance") or 0.0) - amt, 2)
    ctx.update("corporate_wellness_enrollments", enrollment_id, corporate_dues_balance=new_balance)
    return (f"Waived {amt:.2f} against enrollment {enrollment_id} (entry {rid}); balance owed is "
            f"now {new_balance:.2f}.")


# ---------------------------------------------------------------------------
# Task 1 tools -- suspended-enrollment reinstatement (late fee, missed-payment
# recovery, reinstatement fee, and the reinstatement transition itself)
# ---------------------------------------------------------------------------

@tool(owner="agent", rw="write")
def bill_corp_late_fee_4428c2eb(ctx: ToolContext, enrollment_id: str, amount_usd: float,
                                 billing_cycle_month: str) -> str:
    """Assess a one-time late-payment fee against the employer's master account for a missed
    corporate wellness billing cycle on this enrollment. This adds one dues-billed entry to the
    enrollment's billing history and increases the net amount currently owed by the employer's
    master account for this employee's enrollment by the same amount.

    Args:
        enrollment_id: Id class — the reference number of the enrollment the late fee is assessed
            against, read from the enrollment record.
        amount_usd: Fixed-format class — the dollar amount of the late fee, in USD (the unit of
            every amount in this system), rounded to exactly 2 decimal places; do not pass an
            amount that has not already been rounded to the cent.
        billing_cycle_month: Fixed-format class — the missed billing cycle this late fee relates
            to, in YYYY-MM form (four-digit year, hyphen, two-digit month).

    Returns:
        A string confirming the new billing-history entry's reference number (event_id), the late
        fee amount assessed, the billing cycle it relates to, and the enrollment's resulting
        balance owed by the employer's master account.
    """
    rows = ctx.find("corporate_wellness_enrollments", enrollment_id=enrollment_id)
    if not rows:
        return f"Error: no corporate wellness enrollment {enrollment_id}."
    enr = rows[0]
    amt = round(float(amount_usd), 2)
    rid = ctx.make_id("cwl_", enrollment_id, billing_cycle_month, ctx.now())
    ctx.create("corporate_wellness_events", rid, event_id=rid, enrollment_id=enrollment_id,
               customer_id=enr["customer_id"], event_type="corp_dues_billed",
               event_timestamp=ctx.now(), amount_usd=amt, billing_cycle_month=billing_cycle_month,
               employer_account_id=enr["employer_account_id"])
    new_balance = round(float(enr.get("corporate_dues_balance") or 0.0) + amt, 2)
    ctx.update("corporate_wellness_enrollments", enrollment_id, corporate_dues_balance=new_balance)
    return (f"Assessed a late fee of {amt:.2f} on enrollment {enrollment_id} for cycle "
            f"{billing_cycle_month} (entry {rid}); balance owed is now {new_balance:.2f}.")


@tool(owner="agent", rw="write")
def post_corp_dues_payment_af691ae5(ctx: ToolContext, enrollment_id: str,
                                     amount_usd: float) -> str:
    """Post a payment received from the employer's master account to settle missed corporate
    wellness billing on this enrollment. This adds one payment entry to the enrollment's billing
    history and decreases the net amount currently owed by the employer's master account for this
    employee's enrollment by the same amount.

    Args:
        enrollment_id: Id class — the reference number of the enrollment the payment is being
            applied to, read from the enrollment record.
        amount_usd: Fixed-format class — the dollar amount actually applied against the balance, in
            USD (the unit of every amount in this system), rounded to exactly 2 decimal places; do
            not pass an amount that has not already been rounded to the cent.

    Returns:
        A string confirming the new payment-history entry's reference number (event_id), the amount
        applied, and the enrollment's resulting balance owed by the employer's master account.
    """
    rows = ctx.find("corporate_wellness_enrollments", enrollment_id=enrollment_id)
    if not rows:
        return f"Error: no corporate wellness enrollment {enrollment_id}."
    enr = rows[0]
    amt = round(float(amount_usd), 2)
    rid = ctx.make_id("cwq_", enrollment_id, amt, ctx.now())
    ctx.create("corporate_wellness_events", rid, event_id=rid, enrollment_id=enrollment_id,
               customer_id=enr["customer_id"], event_type="corp_dues_payment_received",
               event_timestamp=ctx.now(), amount_usd=amt, billing_cycle_month="",
               employer_account_id=enr["employer_account_id"])
    new_balance = round(float(enr.get("corporate_dues_balance") or 0.0) - amt, 2)
    ctx.update("corporate_wellness_enrollments", enrollment_id, corporate_dues_balance=new_balance)
    return (f"Payment of {amt:.2f} posted to enrollment {enrollment_id} (entry {rid}); balance "
            f"owed is now {new_balance:.2f}.")


@tool(owner="agent", rw="write")
def bill_corp_reinstatement_fee_377eb087(ctx: ToolContext, enrollment_id: str,
                                          amount_usd: float) -> str:
    """Bill the employer's master account a one-time reinstatement fee for bringing a suspended
    corporate wellness enrollment back current, and reinstate the enrollment in the same action.
    This adds one dues-billed entry to the enrollment's billing history, increases the net amount
    currently owed by the employer's master account for this employee's enrollment by the same
    amount, and transitions the enrollment's lifecycle status from suspended to active.

    Args:
        enrollment_id: Id class — the reference number of the enrollment being reinstated, read
            from the enrollment record.
        amount_usd: Fixed-format class — the dollar amount of the reinstatement fee, in USD (the
            unit of every amount in this system), rounded to exactly 2 decimal places; do not pass
            an amount that has not already been rounded to the cent. Pass 0.00 when this
            enrollment's reinstatement fee has been waived.

    Returns:
        A string confirming the new billing-history entry's reference number (event_id), the
        reinstatement fee amount billed, the enrollment's resulting balance owed by the employer's
        master account, and that its lifecycle status is now active.
    """
    rows = ctx.find("corporate_wellness_enrollments", enrollment_id=enrollment_id)
    if not rows:
        return f"Error: no corporate wellness enrollment {enrollment_id}."
    enr = rows[0]
    amt = round(float(amount_usd), 2)
    rid = ctx.make_id("cwr_", enrollment_id, amt, ctx.now())
    ctx.create("corporate_wellness_events", rid, event_id=rid, enrollment_id=enrollment_id,
               customer_id=enr["customer_id"], event_type="corp_dues_billed",
               event_timestamp=ctx.now(), amount_usd=amt, billing_cycle_month="",
               employer_account_id=enr["employer_account_id"])
    new_balance = round(float(enr.get("corporate_dues_balance") or 0.0) + amt, 2)
    ctx.update("corporate_wellness_enrollments", enrollment_id, corporate_dues_balance=new_balance,
               status="active")
    return (f"Billed a reinstatement fee of {amt:.2f} to enrollment {enrollment_id} (entry {rid}); "
            f"balance owed is now {new_balance:.2f}; status is now active.")

"""Hidden task tools for the Equipment Replacement & Retrofit Projects desk.

Each function performs one atomic write on a project record and is reached only through the
unlock/call meta-tools; none of them aggregates history, prices anything, or judges whether the
write is due. The agent works the figure out from the published rules and the project's own
records and passes it in.
"""

from erlbench import ToolContext, tool


@tool(owner="agent", rw="write")
def bill_storage_charge_e8c4e90e(ctx: ToolContext, project_id: str, storage_amount_usd: float) -> str:
    """Invoice the owner for equipment that has been standing in storage on a replacement or retrofit
    project. One call raises a single storage line on that project's running account: the line is added
    to the project's record entries as a storage billing dated today, and the amount owed on the project
    goes up by the same amount. Afterwards the owner sees a storage charge on the project statement and
    a higher project balance. The call has completed when the confirmation naming the new record entry
    and the amount billed comes back.

    Args:
        project_id: Id class — the reference number of the replacement or retrofit project the storage
            line is raised on, read from the project lookup for this owner.
        storage_amount_usd: Fixed-format class — the money amount of the storage line, in USD, given as a
            decimal number rounded half to even to 2 decimal places; it is stored to that same precision
            and may not be left empty.

    Returns:
        A confirmation sentence in plain text carrying the reference of the storage record entry created
        on the project, the amount billed in USD to two decimal places, the day the line was dated, and
        the project balance after the line was added. The sentence coming back is what indicates the
        storage line was raised; the owner can see the same line and the same balance on the project
        statement.
    """
    rid = ctx.make_id("rse_", project_id, storage_amount_usd)
    amount = round(float(storage_amount_usd), 2)
    rows = ctx.find("retrofit_projects", project_id=project_id)
    if not rows:
        return f"No project {project_id} on file; nothing was billed."
    project = rows[0]
    today = ctx.now()[:10]
    ctx.create("retrofit_events", rid, event_id=rid, project_id=project_id,
               customer_id=project.get("customer_id"), site_id=project.get("site_id"),
               event_type="retrofit_progress_billed", billing_class="storage",
               amount_usd=amount, billing_period=today[:7], due_date=today, percent_complete=0)
    balance = round(float(project.get("balance_due") or 0) + amount, 2)
    ctx.update("retrofit_projects", project_id, balance_due=balance)
    return (f"Storage line {rid} raised on project {project_id} for {amount:.2f} USD dated {today}; "
            f"the project balance is now {balance:.2f} USD.")


@tool(owner="user", rw="write")
def settle_project_cancellation_6d1f2e6f(ctx: ToolContext, project_id: str,
                                         settlement_amount_usd: float,
                                         cancellation_reason: str) -> str:
    """Stop a replacement or retrofit project on the owner's own instruction and settle it. One call
    marks that project stopped as of today, records the stage it had reached and why the owner stopped
    it, raises the settlement line for the figure the owner is settling at, and adds that figure to what
    is owed on the project. Afterwards the project is closed to further work, the owner sees a
    cancellation line on the project statement and the project balance carries the settlement. The call
    has completed when the confirmation naming the stopped project and the settlement figure comes back.

    Args:
        project_id: Id class — the reference number of the replacement or retrofit project being stopped,
            read from the project lookup for this owner.
        settlement_amount_usd: Fixed-format class — the money figure the project is settled at, in USD,
            given as a decimal number rounded half to even to 2 decimal places; it is stored to that same
            precision and may not be left empty.
        cancellation_reason: Enum class — why the owner is stopping the project, one of:
            customer_convenience, where the owner simply no longer wants the work done and gives no other
            ground; non_payment, where the company stops the project because invoices on it have gone
            unpaid; estimate_lapsed, where the estimate ran out before it was awarded and is closed
            instead of repriced; budget_withdrawn, where the money for the work has been taken away from
            the owner's capital plan; scope_replaced, where the same scope is being carried by another
            project instead; site_sold_or_closed, where the building has been sold or shut and the work
            can no longer be done there.

    Returns:
        A confirmation sentence in plain text carrying the project reference, the stage the project had
        reached when it was stopped, the reason recorded, the reference of the settlement record entry
        created on the project, the settlement figure in USD to two decimal places and the project
        balance after it. The sentence coming back is what indicates the project was stopped and settled;
        the owner can see the same stopped status and the same settlement line on the project statement.
    """
    rid = ctx.make_id("rcs_", project_id, settlement_amount_usd, cancellation_reason)
    amount = round(float(settlement_amount_usd), 2)
    rows = ctx.find("retrofit_projects", project_id=project_id)
    if not rows:
        return f"No project {project_id} on file; nothing was stopped."
    project = rows[0]
    today = ctx.now()[:10]
    stage = project.get("status")
    ctx.create("retrofit_events", rid, event_id=rid, project_id=project_id,
               customer_id=project.get("customer_id"), site_id=project.get("site_id"),
               event_type="retrofit_progress_billed", billing_class="cancellation",
               amount_usd=amount, billing_period=today[:7], due_date=today, percent_complete=0)
    balance = round(float(project.get("balance_due") or 0) + amount, 2)
    ctx.update("retrofit_projects", project_id, status="cancelled", cancellation_date=today,
               cancellation_stage=stage, cancellation_reason=cancellation_reason,
               balance_due=balance)
    return (f"Project {project_id} stopped at the {stage} stage for {cancellation_reason}; settlement "
            f"line {rid} raised for {amount:.2f} USD and the project balance is now {balance:.2f} USD.")


@tool(owner="agent", rw="write")
def credit_liquidated_damages_732a84c1(ctx: ToolContext, project_id: str,
                                       damages_credit_usd: float) -> str:
    """Credit an owner for a replacement or retrofit project that was handed over late. One call puts a
    single liquidated damages credit on that project's running account: the credit is added to the
    project's record entries dated today and marked as damages for lateness, and the amount owed on the
    project falls by the same amount. Afterwards the owner sees the credit on the project statement and a
    lower project balance. The call has completed when the confirmation naming the new record entry and
    the amount credited comes back.

    Args:
        project_id: Id class — the reference number of the replacement or retrofit project the credit is
            put on, read from the project lookup for this owner.
        damages_credit_usd: Fixed-format class — the money amount of the credit, in USD, given as a
            decimal number rounded half to even to 2 decimal places; it is stored to that same precision
            and may not be left empty.

    Returns:
        A confirmation sentence in plain text carrying the reference of the credit record entry created on
        the project, the amount credited in USD to two decimal places, the day the credit was dated and
        the project balance after it. The sentence coming back is what indicates the credit was put on;
        the owner can see the same credit line and the same balance on the project statement.
    """
    rid = ctx.make_id("rld_", project_id, damages_credit_usd)
    amount = round(float(damages_credit_usd), 2)
    rows = ctx.find("retrofit_projects", project_id=project_id)
    if not rows:
        return f"No project {project_id} on file; nothing was credited."
    project = rows[0]
    today = ctx.now()[:10]
    ctx.create("retrofit_events", rid, event_id=rid, project_id=project_id,
               customer_id=project.get("customer_id"), site_id=project.get("site_id"),
               event_type="retrofit_credit_issued", credit_reason="liquidated_damages",
               amount_usd=amount, issued_date=today)
    balance = round(float(project.get("balance_due") or 0) - amount, 2)
    ctx.update("retrofit_projects", project_id, balance_due=balance)
    return (f"Credit {rid} put on project {project_id} for {amount:.2f} USD dated {today}; the project "
            f"balance is now {balance:.2f} USD.")


@tool(owner="agent", rw="write")
def bill_overdue_late_fee_5c3179f3(ctx: ToolContext, project_id: str,
                                   late_fee_amount_usd: float) -> str:
    """Charge an owner the late fee their replacement or retrofit project has run up on billings that went
    past their due day. One call raises a single late fee line on that project's running account: the line
    is added to the project's record entries as a late fee dated today and falling due today, and the
    amount owed on the project goes up by the same amount. Afterwards the owner sees a late fee on the
    project statement and a higher project balance. The call has completed when the confirmation naming
    the new record entry and the amount charged comes back.

    Args:
        project_id: Id class — the reference number of the replacement or retrofit project the late fee is
            raised on, read from the project lookup for this owner.
        late_fee_amount_usd: Fixed-format class — the money amount of the late fee line, in USD, given as
            a decimal number rounded half to even to 2 decimal places; it is stored to that same precision
            and may not be left empty.

    Returns:
        A confirmation sentence in plain text carrying the reference of the late fee record entry created
        on the project, the amount charged in USD to two decimal places, the day the line was dated and
        the project balance after it. The sentence coming back is what indicates the late fee was raised;
        the owner can see the same line and the same balance on the project statement.
    """
    rid = ctx.make_id("rlf_", project_id, late_fee_amount_usd)
    amount = round(float(late_fee_amount_usd), 2)
    rows = ctx.find("retrofit_projects", project_id=project_id)
    if not rows:
        return f"No project {project_id} on file; nothing was charged."
    project = rows[0]
    today = ctx.now()[:10]
    ctx.create("retrofit_events", rid, event_id=rid, project_id=project_id,
               customer_id=project.get("customer_id"), site_id=project.get("site_id"),
               event_type="retrofit_progress_billed", billing_class="late_fee",
               amount_usd=amount, billing_period=today[:7], due_date=today, percent_complete=0)
    balance = round(float(project.get("balance_due") or 0) + amount, 2)
    ctx.update("retrofit_projects", project_id, balance_due=balance)
    return (f"Late fee line {rid} raised on project {project_id} for {amount:.2f} USD dated {today}; the "
            f"project balance is now {balance:.2f} USD.")


@tool(owner="agent", rw="write")
def release_project_retainage_a81bb865(ctx: ToolContext, project_id: str,
                                       retainage_release_usd: float) -> str:
    """Release retainage that has been held back on a replacement or retrofit project and bill it to the
    owner. One call records a single release on that project's running account: the release is added to
    the project's record entries dated today, the retainage the project still holds falls by the amount
    released and the amount owed on the project goes up by the same amount. Afterwards the owner sees the
    released retainage on the project statement, a smaller retainage holding and a higher project balance.
    The call has completed when the confirmation naming the new record entry and the amount released comes
    back.

    Args:
        project_id: Id class — the reference number of the replacement or retrofit project the retainage
            is released on, read from the project lookup for this owner.
        retainage_release_usd: Fixed-format class — the money amount of retainage released, in USD, given
            as a decimal number rounded half to even to 2 decimal places; it is stored to that same
            precision and may not be left empty.

    Returns:
        A confirmation sentence in plain text carrying the reference of the release record entry created
        on the project, the amount released in USD to two decimal places, the day the release was dated,
        the retainage the project still holds and the project balance after it. The sentence coming back
        is what indicates the release was recorded; the owner can see the same release line, holding and
        balance on the project statement.
    """
    rid = ctx.make_id("rrr_", project_id, retainage_release_usd)
    amount = round(float(retainage_release_usd), 2)
    rows = ctx.find("retrofit_projects", project_id=project_id)
    if not rows:
        return f"No project {project_id} on file; nothing was released."
    project = rows[0]
    today = ctx.now()[:10]
    ctx.create("retrofit_events", rid, event_id=rid, project_id=project_id,
               customer_id=project.get("customer_id"), site_id=project.get("site_id"),
               event_type="retrofit_retainage_released", amount_usd=amount, released_date=today)
    held = round(float(project.get("retainage_held_usd") or 0) - amount, 2)
    balance = round(float(project.get("balance_due") or 0) + amount, 2)
    ctx.update("retrofit_projects", project_id, retainage_held_usd=held, balance_due=balance)
    return (f"Retainage release {rid} recorded on project {project_id} for {amount:.2f} USD dated {today}; "
            f"the project now holds {held:.2f} USD of retainage and its balance is {balance:.2f} USD.")


@tool(owner="user", rw="write")
def pay_project_balance_ec87bb4f(ctx: ToolContext, project_id: str, payment_amount_usd: float,
                                 payment_method: str) -> str:
    """Pay money the owner owes on a replacement or retrofit project. One call records a single payment on
    that project's running account: the payment is added to the project's record entries dated today with
    the way the money was sent, and the amount owed on the project falls by the amount paid. Afterwards
    the owner sees the payment on the project statement and a lower project balance. The call has
    completed when the confirmation naming the new record entry and the amount paid comes back.

    Args:
        project_id: Id class — the reference number of the replacement or retrofit project the money is
            paid on, read from the project lookup for this owner.
        payment_amount_usd: Fixed-format class — the money amount the owner is paying, in USD, given as a
            decimal number rounded half to even to 2 decimal places; it is stored to that same precision
            and may not be left empty.
        payment_method: Enum class — how the owner is sending the money, one of: check, where a paper
            cheque is posted or handed to the office; ach, where the money is sent by bank transfer out of
            the owner's account through the automated clearing house; credit_card, where the owner pays on
            a company card; wire, where the owner's bank wires the money the same day.

    Returns:
        A confirmation sentence in plain text carrying the reference of the payment record entry created
        on the project, the amount paid in USD to two decimal places, the way the money was sent, the day
        the payment was dated and the project balance after it. The sentence coming back is what indicates
        the payment was recorded; the owner can see the same payment line and the same balance on the
        project statement.
    """
    rid = ctx.make_id("rpb_", project_id, payment_amount_usd, payment_method)
    amount = round(float(payment_amount_usd), 2)
    rows = ctx.find("retrofit_projects", project_id=project_id)
    if not rows:
        return f"No project {project_id} on file; nothing was paid."
    project = rows[0]
    today = ctx.now()[:10]
    ctx.create("retrofit_events", rid, event_id=rid, project_id=project_id,
               customer_id=project.get("customer_id"), site_id=project.get("site_id"),
               event_type="retrofit_payment_received", amount_usd=amount,
               payment_method=payment_method, received_date=today)
    balance = round(float(project.get("balance_due") or 0) - amount, 2)
    ctx.update("retrofit_projects", project_id, balance_due=balance)
    return (f"Payment {rid} recorded on project {project_id} for {amount:.2f} USD by {payment_method} "
            f"dated {today}; the project balance is now {balance:.2f} USD.")

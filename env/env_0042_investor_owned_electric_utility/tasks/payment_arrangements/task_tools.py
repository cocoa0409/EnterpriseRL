"""Hidden task tools of the payment_arrangements difficulty (Lakeshore Power & Light Company).

Each tool performs one atomic change on a payment arrangement record and nothing else. None of
them checks eligibility, status, timing or any other business precondition, and none computes a
value: the amounts and counts they receive are worked out beforehand from the published policy
and the customer's records, and the tool records them exactly as given. Tool names are frozen;
each one is reached through the unlock/call meta-tools.
"""

from erlbench import ToolContext, tool


@tool(owner="agent", rw="write")
def reinstate_arrangement_7e9638f2(ctx: ToolContext, arrangement_id: str, redeferred_amount: float) -> str:
    """Reinstate one deferred payment agreement (Standard or Extended) that is in default, putting it back into force today.

    The deferred payment agreement identified by the reference number is set back to active status with today's date
    as its latest status change, and the balance held under it is set to the re-deferred amount given,
    which from then on is the deferred balance repaid by the arrangement's remaining installments. The
    installment count and the regular installment amount on file are left as they are. Afterwards a
    lookup of the arrangement shows it active, dated today, with the new balance remaining. A receipt
    naming the arrangement, its new status and the balance now held under it confirms the change.

    Args:
        arrangement_id: Id class — the reference number of the deferred payment agreement being
            reinstated, as returned by the payment arrangement lookup for the customer's service account.
        redeferred_amount: Fixed-format class — the balance placed back under the arrangement at
            reinstatement, in USD with 2 decimal places (a plain number such as 1234.56, no currency
            sign or thousands separator); it is stored rounded half-up to the cent and must not be
            negative.

    Returns:
        A text receipt "Arrangement <arrangement_id> reinstated: status active as of <YYYY-MM-DD>,
        balance remaining <amount> USD." where <arrangement_id> is the reference number given,
        <YYYY-MM-DD> is today's date (the new status date) and <amount> is the balance now held under
        the arrangement with 2 decimal places. Receiving this receipt means the reinstatement is
        recorded.
    """
    amount = round(float(redeferred_amount), 2)
    today = ctx.now()[:10]
    ctx.update("arrangement_plans", arrangement_id, status="active", status_date=today,
               remaining_balance=amount)
    return (f"Arrangement {arrangement_id} reinstated: status active as of {today}, "
            f"balance remaining {amount:.2f} USD.")


@tool(owner="user", rw="write")
def renegotiate_arrangement_installments_743d0532(ctx: ToolContext, arrangement_id: str, installment_count: int,
                                                  installment_amount: float) -> str:
    """Record the customer's own acceptance of a new installment schedule on one of their payment arrangements.

    The customer, acting in person, confirms a new total number of installments for the arrangement
    identified by the reference number (the total counts the installments already billed) and the new
    regular installment that will be billed for each installment not yet billed; the final installment
    carries whatever remainder is left. The arrangement's installment count and regular installment
    amount are replaced by the values confirmed; its status, balance and deferred amount are unchanged.
    Afterwards a lookup of the arrangement shows the new count and amount. A receipt naming the
    arrangement and the schedule now on file confirms the change.

    Args:
        arrangement_id: Id class — the reference number of the customer's payment arrangement whose
            schedule is being changed, as the representative reads it out from the payment
            arrangement lookup.
        installment_count: Fixed-format class — the new total number of installments of the
            arrangement, counting those already billed, as a whole number (integer, at least 1).
        installment_amount: Fixed-format class — the new regular installment for each installment not
            yet billed, in USD with 2 decimal places (a plain number such as 87.63, no currency sign);
            it is stored rounded half-up to the cent.

    Returns:
        A text receipt "Arrangement <arrangement_id> schedule changed: <count> installments in total,
        regular installment <amount> USD." where <count> is the new total count as an integer and
        <amount> the new regular installment with 2 decimal places. Receiving this receipt means the
        new schedule is recorded.
    """
    count = int(installment_count)
    amount = round(float(installment_amount), 2)
    ctx.update("arrangement_plans", arrangement_id, installment_count=count, installment_amount=amount)
    return (f"Arrangement {arrangement_id} schedule changed: {count} installments in total, "
            f"regular installment {amount:.2f} USD.")


@tool(owner="user", rw="write")
def accept_payment_extension_fc63ed0e(ctx: ToolContext, customer_id: str, service_account_id: str,
                                      eligible_balance: float, down_payment_amount: float,
                                      extended_amount: float) -> str:
    """Record the customer's own acceptance of a Payment Extension on one of their electric service agreements.

    The customer, acting in person, accepts a Payment Extension: the balance placed under it, the part
    of that balance to be paid now and the amount carried to the extended date as one single
    installment. A new Payment Extension is created for the service agreement, set up by an agent,
    dated today, in pending down payment status with today as the last day for the payment due now,
    one installment equal to the amount extended, and nothing yet deferred off the agreement. A lookup
    of the customer's payment arrangements then shows the new extension. A receipt with the new
    arrangement reference number confirms it.

    Args:
        customer_id: Id class — the customer reference number of the account holder, as returned by
            the customer profile lookup.
        service_account_id: Id class — the service account number of the agreement the extension is
            for, as printed on the customer's disconnection notice and returned by the service
            agreement lookup.
        eligible_balance: Fixed-format class — the balance placed under the extension, in USD with 2
            decimal places (a plain number such as 512.40, no currency sign); stored rounded half-up to
            the cent.
        down_payment_amount: Fixed-format class — the part of that balance to be paid now, in USD with
            2 decimal places (0.00 when nothing is due now); stored rounded half-up to the cent.
        extended_amount: Fixed-format class — the amount carried to the extended date as the single
            installment, in USD with 2 decimal places; stored rounded half-up to the cent.

    Returns:
        A text receipt "Payment Extension <arrangement_id> accepted on <service_account_id>: balance
        <eligible> USD, due now <due_now> USD by <YYYY-MM-DD>, extended <extended> USD." where
        <arrangement_id> is the new arrangement reference number, <YYYY-MM-DD> is today's date and the
        amounts carry 2 decimal places. Receiving this receipt means the extension is recorded.
    """
    eligible = round(float(eligible_balance), 2)
    due_now = round(float(down_payment_amount), 2)
    extended = round(float(extended_amount), 2)
    today = ctx.now()[:10]
    rid = ctx.make_id("arr_", customer_id, service_account_id, eligible, due_now, extended)
    ctx.create("arrangement_plans", rid, arrangement_id=rid, customer_id=customer_id,
               service_account_id=service_account_id, variant_name="Payment Extension",
               status="pending_down_payment", enrolled_date=today, enrollment_channel="agent_assisted",
               disconnected_at_enrollment=False, eligible_balance=eligible, down_payment_waived=False,
               down_payment_amount=due_now, down_payment_due_date=today, deferred_amount=extended,
               installment_count=1, installment_amount=extended, status_date=today, remaining_balance=0.0)
    return (f"Payment Extension {rid} accepted on {service_account_id}: balance {eligible:.2f} USD, "
            f"due now {due_now:.2f} USD by {today}, extended {extended:.2f} USD.")


@tool(owner="agent", rw="write")
def post_arrangement_forgiveness_78b684e3(ctx: ToolContext, arrangement_id: str, installment_number: int,
                                          bill_id: str, amount: float) -> str:
    """Post a forgiveness entry for one scheduled installment of an Arrearage Management Program plan.

    A forgiveness entry dated today is added to the plan's history for the installment number given,
    linked to the bill whose payment earned it, and the plan's remaining balance is reduced by the
    amount forgiven. Afterwards the plan history shows the forgiveness and the plan lookup shows the
    lower remaining balance. A receipt naming the entry, the installment and the amount confirms it.

    Args:
        arrangement_id: Id class — the reference number of the Arrearage Management Program plan, as
            returned by the payment arrangement lookup.
        installment_number: Fixed-format class — the position of the scheduled installment being
            forgiven (1 = first), as a whole number (integer).
        bill_id: Id class — the bill reference number of the program bill whose payment earned the
            forgiveness, as returned by the bill lookup.
        amount: Fixed-format class — the amount forgiven, in USD with 2 decimal places (a plain number
            such as 140.25, no currency sign); stored rounded half-up to the cent.

    Returns:
        A text receipt "Forgiveness <entry_id> posted on <arrangement_id> for installment <n>: <amount>
        USD; remaining balance <balance> USD." where <entry_id> is the new history entry reference
        number, <n> the installment number, and both amounts carry 2 decimal places. Receiving this
        receipt means the forgiveness is posted.
    """
    amt = round(float(amount), 2)
    n = int(installment_number)
    plan = ctx.find("arrangement_plans", arrangement_id=arrangement_id)
    rec = plan[0] if plan else {}
    today = ctx.now()[:10]
    rid = ctx.make_id("fgv_", arrangement_id, n, bill_id, amt)
    ctx.create("arrangement_ledger", rid, arrangement_ledger_id=rid, arrangement_id=arrangement_id,
               customer_id=rec.get("customer_id"), service_account_id=rec.get("service_account_id"),
               event_type="arrangement_forgiveness", posting_date=today, amount=amt,
               deferral_kind="not_applicable", installment_number=n, bill_id=bill_id,
               return_reason="not_applicable")
    remaining = round(float(rec.get("remaining_balance") or 0) - amt, 2)
    ctx.update("arrangement_plans", arrangement_id, remaining_balance=remaining)
    return (f"Forgiveness {rid} posted on {arrangement_id} for installment {n}: {amt:.2f} USD; "
            f"remaining balance {remaining:.2f} USD.")


@tool(owner="agent", rw="write")
def record_missed_program_bill_7606bb4e(ctx: ToolContext, arrangement_id: str, installment_number: int,
                                        bill_id: str, amount: float) -> str:
    """Record that a program bill of an Arrearage Management Program plan is counted as missed.

    A missed-installment entry dated today is added to the plan's history for the installment number
    that bill carries, linked to the bill and carrying the missed amount given. The plan's status and
    balance are not changed. Afterwards the plan history shows the missed entry. A receipt naming the
    entry, the installment and the amount confirms it.

    Args:
        arrangement_id: Id class — the reference number of the Arrearage Management Program plan, as
            returned by the payment arrangement lookup.
        installment_number: Fixed-format class — the position of the scheduled installment the missed
            bill carries (1 = first), as a whole number (integer).
        bill_id: Id class — the bill reference number of the program bill counted as missed, as
            returned by the bill lookup.
        amount: Fixed-format class — the missed amount recorded, in USD with 2 decimal places (a plain
            number such as 11.91, no currency sign); stored rounded half-up to the cent.

    Returns:
        A text receipt "Missed entry <entry_id> recorded on <arrangement_id> for installment <n>:
        <amount> USD." where <entry_id> is the new history entry reference number, <n> the installment
        number and the amount carries 2 decimal places. Receiving this receipt means the entry is
        recorded.
    """
    amt = round(float(amount), 2)
    n = int(installment_number)
    plan = ctx.find("arrangement_plans", arrangement_id=arrangement_id)
    rec = plan[0] if plan else {}
    rid = ctx.make_id("mis_", arrangement_id, n, bill_id, amt)
    ctx.create("arrangement_ledger", rid, arrangement_ledger_id=rid, arrangement_id=arrangement_id,
               customer_id=rec.get("customer_id"), service_account_id=rec.get("service_account_id"),
               event_type="arrangement_missed_installment", posting_date=ctx.now()[:10], amount=amt,
               deferral_kind="not_applicable", installment_number=n, bill_id=bill_id,
               return_reason="not_applicable")
    return f"Missed entry {rid} recorded on {arrangement_id} for installment {n}: {amt:.2f} USD."


@tool(owner="agent", rw="write")
def reinstate_winter_protection_plan_6f5d50f4(ctx: ToolContext, arrangement_id: str, redeferred_amount: float) -> str:
    """Reinstate one Winter Protection Plan that is in default, putting it back into force today.

    The Winter Protection Plan identified by the reference number is set back to active status with
    today's date as its latest status change, and the balance held under it is set to the re-deferred
    amount given, which from then on is repaid by the plan's remaining installments. The installment
    count and regular installment on file are left as they are. Afterwards a lookup of the plan shows
    it active, dated today, with the new balance remaining. A receipt naming the plan, its new status
    and the balance now held confirms the change.

    Args:
        arrangement_id: Id class — the reference number of the Winter Protection Plan being
            reinstated, as returned by the payment arrangement lookup.
        redeferred_amount: Fixed-format class — the balance placed back under the plan at
            reinstatement, in USD with 2 decimal places (a plain number such as 327.60, no currency
            sign); stored rounded half-up to the cent.

    Returns:
        A text receipt "Winter Protection Plan <arrangement_id> reinstated: status active as of
        <YYYY-MM-DD>, balance remaining <amount> USD." where <YYYY-MM-DD> is today's date and <amount>
        carries 2 decimal places. Receiving this receipt means the reinstatement is recorded.
    """
    amount = round(float(redeferred_amount), 2)
    today = ctx.now()[:10]
    ctx.update("arrangement_plans", arrangement_id, status="active", status_date=today, remaining_balance=amount)
    return (f"Winter Protection Plan {arrangement_id} reinstated: status active as of {today}, "
            f"balance remaining {amount:.2f} USD.")

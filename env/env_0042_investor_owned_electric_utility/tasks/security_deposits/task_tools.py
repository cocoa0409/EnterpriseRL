"""Hidden task tools of the security_deposits difficulty (Lakeshore Power & Light Company).

Each tool performs one atomic write on a security deposit and is reached only through the
unlock_* -> call_* meta-tools; its name is published only as an extended policy's target tool.
No tool judges eligibility, works out an amount or refuses for a policy reason: the caller has
already decided the action and every value from the published rules and the records.
"""

import calendar

from erlbench import ToolContext, tool


@tool(owner="agent", rw="write")
def extend_deposit_review_04d6c850(ctx: ToolContext, deposit_id: str, extension_months: int) -> str:
    """Record that a security deposit stays held because its satisfactory payment review was not passed,
    moving its refund review date out by a stated number of whole calendar months.

    The deposit keeps its status and its cash; only its refund review date changes. The new review
    date is the review date currently recorded on the deposit, shifted forward by the stated number
    of calendar months to the same day of the month (or to the last day of that month when the month
    is shorter). The new date shows on the deposit at once. If no deposit carries the reference
    number, nothing is changed and the reply says so.

    Args:
        deposit_id: Id class — the deposit reference number of the security deposit whose review date
            moves, as returned by the security-deposit lookup for the customer.
        extension_months: Fixed-format class — the number of whole calendar months by which the
            recorded refund review date moves out; a positive integer count of months, no fractions.

    Returns:
        A one-line text receipt naming the deposit reference number, the review date that was
        recorded, the new refund review date (YYYY-MM-DD) and the number of months applied; the new
        date appearing in the receipt confirms the change was recorded.
    """
    rows = ctx.find("deposit_accounts", deposit_id=deposit_id)
    if not rows:
        return f"No security deposit {deposit_id} on file; nothing was changed."
    old = rows[0].get("refund_review_date") or ctx.now()[:10]
    y, m, d = (int(p) for p in str(old)[:10].split("-"))
    total = y * 12 + (m - 1) + int(extension_months)
    ny, nm = total // 12, total % 12 + 1
    nd = min(d, calendar.monthrange(ny, nm)[1])
    new = f"{ny:04d}-{nm:02d}-{nd:02d}"
    ctx.update("deposit_accounts", deposit_id, refund_review_date=new)
    return (f"Refund review date of deposit {deposit_id} moved from {old} to {new} "
            f"({int(extension_months)} months).")


@tool(owner="agent", rw="write")
def credit_deposit_interest_e2c6de3a(ctx: ToolContext, deposit_id: str, interest_period_end: str,
                                     interest_amount: float) -> str:
    """Credit one period of simple interest to a cash security deposit.

    Books an interest credit on the deposit for the period ending on the stated date, dated today,
    and raises the cash and interest held on the deposit by the amount credited. The credit then
    appears among the deposit's transactions and the held amount shown on the deposit includes it.

    Args:
        deposit_id: Id class — the deposit reference number of the security deposit being credited,
            as returned by the security-deposit lookup for the customer.
        interest_period_end: Fixed-format class — the last day of the interest period this credit
            covers, written YYYY-MM-DD as a calendar date with no time of day.
        interest_amount: Fixed-format class — the interest credited, in USD with 2 decimal places,
            a positive amount already rounded to the cent.

    Returns:
        A one-line text receipt naming the new deposit transaction reference number, the deposit,
        the interest amount credited in USD with 2 decimal places, the period end date and the
        resulting held amount; the transaction reference number in the receipt confirms the credit
        was booked.
    """
    rows = ctx.find("deposit_accounts", deposit_id=deposit_id)
    dep = rows[0] if rows else {}
    amount = round(float(interest_amount), 2)
    rid = ctx.make_id("dtx_", deposit_id, interest_period_end, amount)
    ctx.create("deposit_transactions", rid, deposit_transaction_id=rid, deposit_id=deposit_id,
               customer_id=dep.get("customer_id"), service_account_id=dep.get("service_account_id"),
               event_type="deposit_interest_credit", transaction_date=ctx.now()[:10], amount=amount,
               installment_number=0, interest_period_end=str(interest_period_end)[:10],
               refund_kind="not_applicable", refund_method="not_applicable")
    held = round(float(dep.get("held_amount") or 0) + amount, 2)
    ctx.update("deposit_accounts", deposit_id, held_amount=held)
    return (f"Interest credit {rid} of {amount:.2f} USD booked on deposit {deposit_id} for the period "
            f"ending {str(interest_period_end)[:10]}; held amount now {held:.2f} USD.")


@tool(owner="agent", rw="write")
def require_additional_deposit_b541b477(ctx: ToolContext, deposit_id: str, required_amount: float,
                                        average_monthly_bill: float, due_date: str) -> str:
    """Record a raised requirement on a held business security deposit, returning the deposit to
    assessed status with the new required amount.

    The deposit's required amount and the average monthly bill behind it are replaced by the stated
    values, the date the additional amount falls due is recorded, the deposit's status becomes
    assessed and today becomes both its assessment date and its status date. The cash already held
    stays on the deposit. The new requirement and due date show on the deposit at once.

    Args:
        deposit_id: Id class — the deposit reference number of the held deposit whose requirement is
            raised, as returned by the security-deposit lookup for the customer.
        required_amount: Fixed-format class — the new required deposit amount, in USD with 2 decimal
            places, a whole-dollar amount written with .00 cents.
        average_monthly_bill: Fixed-format class — the average monthly bill the new requirement rests
            on, in USD with 2 decimal places, rounded to the cent.
        due_date: Fixed-format class — the date by which the additional amount is due, written
            YYYY-MM-DD as a calendar date with no time of day.

    Returns:
        A one-line text receipt naming the deposit, its new required amount and average monthly bill
        in USD with 2 decimal places, its status (assessed) and the due date; the assessed status in
        the receipt confirms the raised requirement was recorded.
    """
    req = round(float(required_amount), 2)
    avg = round(float(average_monthly_bill), 2)
    today = ctx.now()[:10]
    ctx.update("deposit_accounts", deposit_id, status="assessed", required_amount=req,
               average_monthly_bill=avg, first_installment_due_date=str(due_date)[:10],
               assessed_date=today, status_date=today)
    return (f"Deposit {deposit_id} now requires {req:.2f} USD on an average monthly bill of {avg:.2f} USD; "
            f"status assessed; additional amount due {str(due_date)[:10]}.")


@tool(owner="user", rw="write")
def pay_additional_deposit_64b1dc0d(ctx: ToolContext, deposit_id: str, installment_number: int,
                                    installment_count: int, amount: float) -> str:
    """Pay, as the customer, an installment of the additional amount owed on a business security
    deposit whose requirement was raised.

    Books a cash deposit payment received today on the deposit under the stated installment number,
    records on the deposit the number of installments in which the additional amount is being paid,
    and raises the cash and interest held on the deposit by the amount paid. The payment then appears
    among the deposit's transactions, and the deposit shows the installment count and the new held
    amount.

    Args:
        deposit_id: Id class — the deposit reference number of the deposit being paid, as given to
            the customer from the security-deposit lookup.
        installment_number: Fixed-format class — the installment number this payment satisfies on the
            deposit, an integer counting from 1 for the deposit's earliest installment.
        installment_count: Fixed-format class — the number of installments in which the additional
            amount is being paid, a positive integer.
        amount: Fixed-format class — the amount paid, in USD with 2 decimal places, a positive amount
            rounded to the cent.

    Returns:
        A one-line text receipt naming the new deposit transaction reference number, the installment
        number and the installment count, the amount received in USD with 2 decimal places, the deposit
        and the resulting held amount; the transaction reference number in the receipt confirms the payment was
        received.
    """
    rows = ctx.find("deposit_accounts", deposit_id=deposit_id)
    dep = rows[0] if rows else {}
    paid = round(float(amount), 2)
    rid = ctx.make_id("dtx_", deposit_id, installment_number, paid)
    ctx.create("deposit_transactions", rid, deposit_transaction_id=rid, deposit_id=deposit_id,
               customer_id=dep.get("customer_id"), service_account_id=dep.get("service_account_id"),
               event_type="deposit_payment", transaction_date=ctx.now()[:10], amount=paid,
               installment_number=int(installment_number), interest_period_end="",
               refund_kind="not_applicable", refund_method="not_applicable")
    held = round(float(dep.get("held_amount") or 0) + paid, 2)
    ctx.update("deposit_accounts", deposit_id, held_amount=held, installment_count=int(installment_count))
    return (f"Deposit payment {rid} received: installment {int(installment_number)} of "
            f"{int(installment_count)} for {paid:.2f} USD on deposit {deposit_id}; held amount now {held:.2f} USD.")


@tool(owner="agent", rw="write")
def assess_new_service_deposit_5e8da269(ctx: ToolContext, customer_id: str, service_account_id: str,
                                        variant_name: str, average_monthly_bill: float, required_amount: float,
                                        first_installment_due_date: str) -> str:
    """Assess a cash security deposit on a newly opened service agreement of a customer.

    Creates a new security deposit in assessed status on the stated agreement, dated today, for the
    reason of new service, to be met in cash, with the stated kind, average monthly bill, required
    amount and first installment due date; nothing has been received on it yet and its number of
    installments is left at zero until an installment is paid. The deposit then shows in the
    customer's security deposits with its new reference number.

    Args:
        customer_id: Id class — the customer reference number of the agreement's customer of record,
            as returned by the customer profile lookup.
        service_account_id: Id class — the service account number of the newly opened agreement the
            deposit secures, as returned by the service-agreement lookup for the customer.
        variant_name: Enum class — the deposit kind, one of: "Residential New Service Deposit" for a
            residential agreement on Schedules RS, RT or REV opened without a waiver basis;
            "Residential Reestablishment Deposit" for a residential agreement disconnected for
            nonpayment or with a late payment history; "Residential Unauthorized Use Deposit" for a
            residential agreement with confirmed meter tampering or diversion; "Small Commercial Service
            Deposit" for a business agreement on Schedules GS or GST; "Medium Commercial Service
            Deposit" for a business agreement on Schedule GD; "Large Power Service Deposit" for a
            business agreement on Schedule LP.
        average_monthly_bill: Fixed-format class — the average monthly bill the requirement rests on,
            in USD with 2 decimal places, rounded to the cent.
        required_amount: Fixed-format class — the deposit amount required, in USD with 2 decimal
            places, a whole-dollar amount written with .00 cents.
        first_installment_due_date: Fixed-format class — the date the first (or only) installment is
            due, written YYYY-MM-DD as a calendar date with no time of day.

    Returns:
        A one-line text receipt naming the new deposit reference number, the agreement, the deposit
        kind, the required amount and average monthly bill in USD with 2 decimal places, the status
        (assessed) and the first installment due date; the deposit reference number in the receipt
        confirms the deposit was assessed.
    """
    req = round(float(required_amount), 2)
    avg = round(float(average_monthly_bill), 2)
    today = ctx.now()[:10]
    rid = ctx.make_id("dep_", customer_id, service_account_id, variant_name, avg, req, first_installment_due_date)
    ctx.create("deposit_accounts", rid, deposit_id=rid, customer_id=customer_id,
               service_account_id=service_account_id, variant_name=variant_name, status="assessed",
               assessed_date=today, assessment_reason="new_service", average_monthly_bill=avg,
               required_amount=req, installment_count=0, security_instrument="cash",
               first_installment_due_date=str(first_installment_due_date)[:10], waiver_basis="not_applicable",
               fully_secured_date="", refund_review_date="", status_date=today, held_amount=0.0)
    return (f"Deposit {rid} assessed on agreement {service_account_id}: {variant_name}, required {req:.2f} USD "
            f"on an average monthly bill of {avg:.2f} USD; status assessed; first installment due "
            f"{str(first_installment_due_date)[:10]}.")


@tool(owner="user", rw="write")
def pay_deposit_installment_d7ce4a9b(ctx: ToolContext, deposit_id: str, installment_number: int,
                                     installment_count: int, amount: float) -> str:
    """Pay, as the customer, an installment of a newly assessed security deposit.

    Books a cash deposit payment received today on the deposit under the stated installment number,
    records on the deposit the number of installments in which it is being paid, and raises the cash
    held on the deposit by the amount paid. The payment then appears among the deposit's
    transactions, and the deposit shows the installment count and the new held amount.

    Args:
        deposit_id: Id class — the deposit reference number of the newly assessed deposit being paid,
            as given to the customer from the assessment receipt or the security-deposit lookup.
        installment_number: Fixed-format class — the installment number this payment satisfies on the
            deposit, an integer counting from 1 for the deposit's earliest installment.
        installment_count: Fixed-format class — the number of installments in which the deposit is
            being paid, a positive integer.
        amount: Fixed-format class — the amount paid, in USD with 2 decimal places, a positive amount
            rounded to the cent.

    Returns:
        A one-line text receipt naming the new deposit transaction reference number, the installment
        number and the installment count, the amount received in USD with 2 decimal places, the
        deposit and the resulting held amount; the transaction reference number in the
        receipt confirms the payment was received.
    """
    rows = ctx.find("deposit_accounts", deposit_id=deposit_id)
    dep = rows[0] if rows else {}
    paid = round(float(amount), 2)
    rid = ctx.make_id("dtx_", deposit_id, installment_number, paid)
    ctx.create("deposit_transactions", rid, deposit_transaction_id=rid, deposit_id=deposit_id,
               customer_id=dep.get("customer_id"), service_account_id=dep.get("service_account_id"),
               event_type="deposit_payment", transaction_date=ctx.now()[:10], amount=paid,
               installment_number=int(installment_number), interest_period_end="",
               refund_kind="not_applicable", refund_method="not_applicable")
    held = round(float(dep.get("held_amount") or 0) + paid, 2)
    ctx.update("deposit_accounts", deposit_id, held_amount=held, installment_count=int(installment_count))
    return (f"Deposit payment {rid} received: installment {int(installment_number)} of "
            f"{int(installment_count)} for {paid:.2f} USD on deposit {deposit_id}; held amount now {held:.2f} USD.")


@tool(owner="agent", rw="write")
def refund_deposit_by_check_703d791f(ctx: ToolContext, deposit_id: str, refund_amount: float) -> str:
    """Refund a held security deposit in full by check on a passed satisfactory payment review.

    Books a full refund of the stated amount, paid by check and dated today, on the deposit, sets the
    deposit's status to refunded with today as its status date, and brings the cash and interest held
    on the deposit to zero. The refund then appears among the deposit's transactions and the deposit
    shows as refunded.

    Args:
        deposit_id: Id class — the deposit reference number of the held deposit being refunded, as
            returned by the security-deposit lookup for the customer.
        refund_amount: Fixed-format class — the full amount refunded by check, in USD with 2 decimal
            places, rounded to the cent.

    Returns:
        A one-line text receipt naming the new deposit transaction reference number, the deposit, the
        amount refunded by check in USD with 2 decimal places and the deposit's new status (refunded);
        the refunded status in the receipt confirms the refund was issued.
    """
    rows = ctx.find("deposit_accounts", deposit_id=deposit_id)
    dep = rows[0] if rows else {}
    amt = round(float(refund_amount), 2)
    today = ctx.now()[:10]
    rid = ctx.make_id("dtx_", deposit_id, "full_refund", amt)
    ctx.create("deposit_transactions", rid, deposit_transaction_id=rid, deposit_id=deposit_id,
               customer_id=dep.get("customer_id"), service_account_id=dep.get("service_account_id"),
               event_type="deposit_refund", transaction_date=today, amount=amt, installment_number=0,
               interest_period_end="", refund_kind="full_refund", refund_method="check")
    ctx.update("deposit_accounts", deposit_id, status="refunded", status_date=today, held_amount=0.0)
    return f"Refund {rid} of {amt:.2f} USD paid by check on deposit {deposit_id}; deposit status refunded."

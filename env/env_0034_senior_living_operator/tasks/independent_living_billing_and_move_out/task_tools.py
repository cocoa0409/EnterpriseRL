"""Hidden task tools of the independent_living_billing_and_move_out difficulty (Larkspur Senior Living).

Each tool performs one atomic write on an Independent Living Residency Agreement or its ledger with
the values the caller passes; it computes nothing and checks no policy condition.
"""

import calendar

from erlbench import ToolContext, tool


@tool(owner="agent", rw="write")
def record_annual_increase_315a2923(ctx: ToolContext, independent_residency_id: str, monthly_service_fee: float,
                                    rate_effective_date: str) -> str:
    """Record an annual increase of the monthly service fee on an independent living residency agreement.
    One call replaces the contracted base monthly service fee in effect on the agreement with the new fee
    passed in, sets the date from which that new fee applies, and clears the pending increase notice
    amount so that no increase remains pending. The second person fee and the ledger are not touched;
    statements billed from the new effective date onward use the new fee. On success the residency shows
    the new fee and its effective date, and a receipt confirming both is returned.

    Args:
        independent_residency_id: Id class — the reference number of the independent living residency agreement whose fee changes, read from the residency lookup for the customer.
        monthly_service_fee: Fixed-format class — the new contracted base monthly service fee being recorded, in USD per calendar month, a positive amount with 2 decimal places, rounded half up to the cent; excludes the second person fee.
        rate_effective_date: Fixed-format class — the calendar date from which the new fee applies, written YYYY-MM-DD in the community's local date.

    Returns:
        A text rendering of a dictionary with keys independent_residency_id (the agreement changed, text),
        monthly_service_fee (the fee now in effect, USD with 2 decimal places), rate_effective_date (the
        date it applies from, YYYY-MM-DD) and status (the text "increase_recorded" when the change was
        saved).
    """
    fee = round(float(monthly_service_fee), 2)
    ctx.update("independent_residencies", independent_residency_id, monthly_service_fee=fee,
               rate_effective_date=str(rate_effective_date), proposed_monthly_service_fee="")
    return str({"independent_residency_id": independent_residency_id, "monthly_service_fee": fee,
                "rate_effective_date": str(rate_effective_date), "status": "increase_recorded"})


@tool(owner="agent", rw="write")
def assess_late_fee_72eb1d9b(ctx: ToolContext, independent_residency_id: str, billing_period: str,
                             late_fee_amount: float) -> str:
    """Post a late fee for one billing period on an independent living residency account. One call writes a
    late fee charge entry on the residency ledger for the billing period given, dated today, and raises the
    account balance the resident owes by the same amount. On success the new late fee entry appears on the
    residency ledger and the account balance shown on the residency rises by the late fee; a receipt with the
    entry reference is returned.

    Args:
        independent_residency_id: Id class — the reference number of the independent living residency agreement whose account is charged, read from the residency lookup for the customer.
        billing_period: Fixed-format class — the calendar month whose monthly fees were past due, written YYYY-MM.
        late_fee_amount: Fixed-format class — the late fee charged, in USD, a positive amount with 2 decimal places, rounded half up to the cent.

    Returns:
        A text rendering of a dictionary with keys independent_entry_id (the reference number of the new
        late fee entry, text), billing_period (YYYY-MM), amount (the fee charged, USD with 2 decimal places),
        account_balance (the balance owed after the charge, USD with 2 decimal places) and status (the text
        "late_fee_posted" on success).
    """
    res = (ctx.find("independent_residencies", independent_residency_id=independent_residency_id) or [{}])[0]
    amount = round(float(late_fee_amount), 2)
    rid = ctx.make_id("ilf_", independent_residency_id, billing_period, late_fee_amount)
    ctx.create("independent_ledger", rid, independent_entry_id=rid, independent_residency_id=independent_residency_id,
               customer_id=res.get("customer_id"), event_type="independent_late_fee_charge", amount=amount,
               posting_date=ctx.now()[:10], billing_period=str(billing_period))
    balance = round(float(res.get("account_balance") or 0) + amount, 2)
    ctx.update("independent_residencies", independent_residency_id, account_balance=balance)
    return str({"independent_entry_id": rid, "billing_period": str(billing_period), "amount": amount,
                "account_balance": balance, "status": "late_fee_posted"})


@tool(owner="user", rw="write")
def make_advance_payment_0a0cd4e1(ctx: ToolContext, independent_residency_id: str, amount: float) -> str:
    """The resident or the resident's financial representative pays an amount onto an independent living
    residency account by a one-time ACH draft from their own bank account, authorizing it in person. One call
    posts the payment on the residency ledger, dated today, under a newly issued ACH trace reference, and lowers
    the account balance owed by the amount paid. On success the payment appears on the ledger and the
    residency's account balance falls by the amount; the receipt shows the trace reference to keep.

    Args:
        independent_residency_id: Id class — the reference number of the independent living residency agreement the payment is for, as given by the Resident and Family Services representative from the residency lookup.
        amount: Fixed-format class — the amount drawn from the payer's bank account, in USD, a positive amount with 2 decimal places, rounded half up to the cent.

    Returns:
        A text rendering of a dictionary with keys independent_entry_id (the reference number of the payment
        entry, text), payment_reference (the ACH trace reference issued for this draft, text), amount (USD
        with 2 decimal places), payment_method (always "ach_one_time"), account_balance (the balance owed
        after the payment, USD with 2 decimal places, negative when the account holds a credit) and status
        (the text "payment_posted" on success).
    """
    res = (ctx.find("independent_residencies", independent_residency_id=independent_residency_id) or [{}])[0]
    paid = round(float(amount), 2)
    rid = ctx.make_id("ipy_", independent_residency_id, amount)
    trace = "ACH" + ctx.make_id("", independent_residency_id, amount, "trace", length=10).upper()
    ctx.create("independent_ledger", rid, independent_entry_id=rid, independent_residency_id=independent_residency_id,
               customer_id=res.get("customer_id"), event_type="independent_payment", amount=paid,
               posting_date=ctx.now()[:10], payment_reference=trace, payment_method="ach_one_time")
    balance = round(float(res.get("account_balance") or 0) - paid, 2)
    ctx.update("independent_residencies", independent_residency_id, account_balance=balance)
    return str({"independent_entry_id": rid, "payment_reference": trace, "amount": paid,
                "payment_method": "ach_one_time", "account_balance": balance, "status": "payment_posted"})


@tool(owner="agent", rw="write")
def post_final_month_charge_713925f6(ctx: ToolContext, independent_residency_id: str, service_to_date: str,
                                     amount: float) -> str:
    """Post the base monthly service fee charge of the final, partly used month on an independent living residency
    account. One call writes one base fee charge entry marked as a move-out proration, covering the days from the
    first day of the calendar month of the last day given through that last day, dated today, and raises the account
    balance owed by the amount. On success the new charge appears on the residency ledger with the days it covers and
    the account balance shown on the residency rises by the amount; a receipt with the entry reference is returned.

    Args:
        independent_residency_id: Id class — the reference number of the independent living residency agreement whose account is charged, read from the residency lookup for the customer.
        service_to_date: Fixed-format class — the last day the charge covers, the date the residency's monthly fees end, written YYYY-MM-DD; the charge runs from the first day of that calendar month.
        amount: Fixed-format class — the charge amount, in USD, a positive amount with 2 decimal places, rounded half up to the cent.

    Returns:
        A text rendering of a dictionary with keys independent_entry_id (the reference number of the new charge
        entry, text), billing_period (the month charged, YYYY-MM), service_from_date and service_to_date (the first
        and last day covered, YYYY-MM-DD), days_billed (integer days covered, both ends included), amount (USD with
        2 decimal places), account_balance (the balance owed after the charge, USD with 2 decimal places) and status
        (the text "final_month_charge_posted" on success).
    """
    res = (ctx.find("independent_residencies", independent_residency_id=independent_residency_id) or [{}])[0]
    last = str(service_to_date)[:10]
    period = last[:7]
    first = period + "-01"
    days = int(last[8:10])
    dim = calendar.monthrange(int(last[:4]), int(last[5:7]))[1]
    charged = round(float(amount), 2)
    rid = ctx.make_id("ifm_", independent_residency_id, last, amount)
    ctx.create("independent_ledger", rid, independent_entry_id=rid, independent_residency_id=independent_residency_id,
               customer_id=res.get("customer_id"), event_type="independent_monthly_fee_charge", amount=charged,
               posting_date=ctx.now()[:10], billing_period=period, fee_component="base_fee",
               charge_basis="prorated_move_out", service_from_date=first, service_to_date=last, days_billed=days,
               days_in_period=dim)
    balance = round(float(res.get("account_balance") or 0) + charged, 2)
    ctx.update("independent_residencies", independent_residency_id, account_balance=balance)
    return str({"independent_entry_id": rid, "billing_period": period, "service_from_date": first,
                "service_to_date": last, "days_billed": days, "amount": charged, "account_balance": balance,
                "status": "final_month_charge_posted"})


@tool(owner="user", rw="write")
def make_closing_payment_d2bd6461(ctx: ToolContext, independent_residency_id: str, amount: float) -> str:
    """The resident or the resident's financial representative settles an independent living residency that is
    ending by authorizing, in person, one closing payment drawn as a one-time ACH draft from their own bank account.
    One call posts the payment on the residency ledger, dated today, under a newly issued ACH trace reference, and
    lowers the account balance owed by the amount paid. On success the payment appears on the ledger and the
    residency's account balance falls by the amount, showing a credit for charges still to post; the receipt shows
    the trace reference to keep.

    Args:
        independent_residency_id: Id class — the reference number of the independent living residency agreement being settled, as given by the Resident and Family Services representative from the residency lookup.
        amount: Fixed-format class — the closing amount drawn from the payer's bank account, in USD, a positive amount with 2 decimal places, rounded half up to the cent.

    Returns:
        A text rendering of a dictionary with keys independent_entry_id (the reference number of the payment entry,
        text), payment_reference (the ACH trace reference issued for this draft, text), amount (USD with 2 decimal
        places), payment_method (always "ach_one_time"), account_balance (the balance after the payment, USD with
        2 decimal places, negative when the account holds a credit) and status (the text "closing_payment_posted"
        on success).
    """
    res = (ctx.find("independent_residencies", independent_residency_id=independent_residency_id) or [{}])[0]
    paid = round(float(amount), 2)
    rid = ctx.make_id("icp_", independent_residency_id, amount)
    trace = "ACH" + ctx.make_id("", independent_residency_id, amount, "closing", length=10).upper()
    ctx.create("independent_ledger", rid, independent_entry_id=rid, independent_residency_id=independent_residency_id,
               customer_id=res.get("customer_id"), event_type="independent_payment", amount=paid,
               posting_date=ctx.now()[:10], payment_reference=trace, payment_method="ach_one_time")
    balance = round(float(res.get("account_balance") or 0) - paid, 2)
    ctx.update("independent_residencies", independent_residency_id, account_balance=balance)
    return str({"independent_entry_id": rid, "payment_reference": trace, "amount": paid,
                "payment_method": "ach_one_time", "account_balance": balance, "status": "closing_payment_posted"})

"""Hidden task tools of garden_cancellations_and_termination_fees (Meadowlark Community Solar, env_0082).

Each tool performs one atomic write on the Garden fixed-rate billing ledger. Values are worked out by the caller
from the published rules and passed in; the tools do not judge eligibility and do not compute amounts.
"""

from erlbench import ToolContext, tool


class _Money:
    @staticmethod
    def cents(x):
        """Round a non-negative amount half up to the cent with integer arithmetic."""
        v = float(x)
        neg = v < 0
        v = abs(v)
        c = int(v * 100 + 0.5 + 1e-9)
        out = c / 100.0
        return -out if neg else out


@tool(owner="agent", rw="write")
def assess_closing_etf_d780691d(ctx: ToolContext, garden_sub_id: str, amount: float, assessment_date: str,
                                due_date: str) -> str:
    """Book the early termination fee of a closed Garden Business fixed-rate subscription on its billing ledger.
    One call adds one early-termination-fee line to that subscription's ledger, raising the balance the business
    owes Meadowlark by the amount given; the line is dual billed, belongs to the statement month of the assessment
    date and appears at once among the subscription's billing lines.

    Args:
        garden_sub_id: Id class — the reference number of the Garden fixed-rate subscription agreement the fee is
            booked on, as returned by the Garden subscription lookup.
        amount: Fixed-format class — the fee in US dollars, a positive number with 2 decimal places (a value that is not positive books
            nothing); the tool rounds the value half up to the cent once, on receipt.
        assessment_date: Fixed-format class — the date the fee is assessed, written YYYY-MM-DD (calendar date,
            Central time); the line's statement month is the year and month of this date.
        due_date: Fixed-format class — the date the fee falls due, written YYYY-MM-DD (calendar date, Central time).

    Returns:
        A one-line confirmation string naming the new ledger line reference (text), the subscription reference
        (text), the fee booked in US dollars with two decimals, the statement month (YYYY-MM) and the due date
        (YYYY-MM-DD). The presence of the line reference indicates the fee line was booked. An amount that is not positive books nothing and returns a one-line notice saying so.
    """
    subs = ctx.find("garden_subscriptions", garden_sub_id=garden_sub_id)
    customer_id = subs[0].get("customer_id", "") if subs else ""
    amt = _Money.cents(amount)
    if amt <= 0:
        return "Nothing booked: the amount must be a positive number of US dollars with 2 decimal places."
    rid = ctx.make_id("gbl_", garden_sub_id, amount, assessment_date, due_date, "etf")
    ctx.create("garden_billing", rid, garden_bill_id=rid, garden_sub_id=garden_sub_id, customer_id=customer_id,
               event_type="garden_etf_assessed", amount=amt, bill_date=assessment_date,
               billing_month=str(assessment_date)[:7], due_date=due_date, garden_credit_id="", garden_ref_bill_id="",
               charge_basis="not_applicable", billing_type="dual", payment_method="not_applicable",
               credit_reason="not_applicable")
    return (f"Early termination fee line {rid} booked on subscription {garden_sub_id}: {amt:.2f} USD, "
            f"statement month {str(assessment_date)[:7]}, due {due_date}.")


@tool(owner="agent", rw="write")
def assess_reopened_late_fee_7f086ee4(ctx: ToolContext, garden_sub_id: str, garden_ref_bill_id: str, amount: float,
                                      assessment_date: str, due_date: str) -> str:
    """Book a late fee on one overdue subscription charge of a Garden Business fixed-rate subscription. One call
    adds one late-fee line that refers to the overdue charge, raising the balance the business owes Meadowlark by
    the amount given; the line takes the statement month of the overdue charge, is dual billed and appears at once
    among the subscription's billing lines.

    Args:
        garden_sub_id: Id class — the reference number of the Garden fixed-rate subscription agreement, as returned
            by the Garden subscription lookup.
        garden_ref_bill_id: Id class — the reference number of the overdue subscription charge line the fee is
            assessed on, as returned by the Garden billing ledger lookup.
        amount: Fixed-format class — the late fee in US dollars, a positive number with 2 decimal places; the
            tool rounds the value half up to the cent once, on receipt.
        assessment_date: Fixed-format class — the date the fee is assessed, written YYYY-MM-DD (calendar date,
            Central time).
        due_date: Fixed-format class — the date the fee falls due, written YYYY-MM-DD (calendar date, Central time).

    Returns:
        A one-line confirmation string naming the new ledger line reference (text), the overdue charge it refers
        to (text), the fee booked in US dollars with two decimals, the statement month (YYYY-MM) and the due date
        (YYYY-MM-DD). The presence of the line reference indicates the fee line was booked. An amount that is not positive books nothing and returns a one-line notice saying so.
    """
    subs = ctx.find("garden_subscriptions", garden_sub_id=garden_sub_id)
    customer_id = subs[0].get("customer_id", "") if subs else ""
    ref = ctx.find("garden_billing", garden_bill_id=garden_ref_bill_id)
    month = ref[0].get("billing_month", "") if ref else ""
    amt = _Money.cents(amount)
    if amt <= 0:
        return "Nothing booked: the amount must be a positive number of US dollars with 2 decimal places."
    rid = ctx.make_id("gbl_", garden_sub_id, garden_ref_bill_id, amount, assessment_date, due_date, "late")
    ctx.create("garden_billing", rid, garden_bill_id=rid, garden_sub_id=garden_sub_id, customer_id=customer_id,
               event_type="garden_late_fee_assessed", amount=amt, bill_date=assessment_date, billing_month=month,
               due_date=due_date, garden_credit_id="", garden_ref_bill_id=garden_ref_bill_id,
               charge_basis="not_applicable", billing_type="dual", payment_method="not_applicable",
               credit_reason="not_applicable")
    return (f"Late fee line {rid} booked on subscription {garden_sub_id} for charge {garden_ref_bill_id}: "
            f"{amt:.2f} USD, statement month {month}, due {due_date}.")


@tool(owner="agent", rw="write")
def assess_decrease_fee_e48668a1(ctx: ToolContext, garden_sub_id: str, decrease_filing_id: str, amount: float,
                                 assessment_date: str, due_date: str) -> str:
    """Book the excess-decrease fee for one subscriber decrease of a Garden Business fixed-rate subscription. One
    call adds one excess-decrease-fee line, raising the balance the business owes Meadowlark by the amount given;
    the line takes the filing month of the decrease filing as its statement month, is dual billed and appears at
    once among the subscription's billing lines.

    Args:
        garden_sub_id: Id class — the reference number of the Garden fixed-rate subscription agreement, as returned
            by the Garden subscription lookup.
        decrease_filing_id: Id class — the reference number of the allocation filing line that removed the kW the
            subscriber asked to remove, as returned by the Garden allocation filing lookup.
        amount: Fixed-format class — the fee in US dollars, a positive number with 2 decimal places (a value that is not positive books
            nothing); the tool rounds the value half up to the cent once, on receipt.
        assessment_date: Fixed-format class — the date the fee is assessed, written YYYY-MM-DD (calendar date,
            Central time).
        due_date: Fixed-format class — the date the fee falls due, written YYYY-MM-DD (calendar date, Central time).

    Returns:
        A one-line confirmation string naming the new ledger line reference (text), the decrease filing it prices
        (text), the fee booked in US dollars with two decimals, the statement month (YYYY-MM) and the due date
        (YYYY-MM-DD). The presence of the line reference indicates the fee line was booked. An amount that is not positive books nothing and returns a one-line notice saying so.
    """
    subs = ctx.find("garden_subscriptions", garden_sub_id=garden_sub_id)
    customer_id = subs[0].get("customer_id", "") if subs else ""
    fil = ctx.find("garden_allocations", garden_filing_id=decrease_filing_id)
    month = fil[0].get("filing_month", "") if fil else ""
    amt = _Money.cents(amount)
    if amt <= 0:
        return "Nothing booked: the amount must be a positive number of US dollars with 2 decimal places."
    rid = ctx.make_id("gbl_", garden_sub_id, decrease_filing_id, amount, assessment_date, due_date, "chg")
    ctx.create("garden_billing", rid, garden_bill_id=rid, garden_sub_id=garden_sub_id, customer_id=customer_id,
               event_type="garden_change_fee_assessed", amount=amt, bill_date=assessment_date, billing_month=month,
               due_date=due_date, garden_credit_id="", garden_ref_bill_id="", charge_basis="not_applicable",
               billing_type="dual", payment_method="not_applicable", credit_reason="not_applicable")
    return (f"Excess-decrease fee line {rid} booked on subscription {garden_sub_id} for filing {decrease_filing_id}: "
            f"{amt:.2f} USD, statement month {month}, due {due_date}.")


@tool(owner="user", rw="write")
def pay_garden_settlement_c372b67a(ctx: ToolContext, garden_sub_id: str, amount: float, payment_method: str) -> str:
    """Pay a settlement on a Garden Business fixed-rate subscription through Meadowlark's secure payment portal.
    The account holder makes the payment personally: one call records one payment received on that subscription,
    lowering its balance by the amount paid; the payment carries today's date and statement month and appears at
    once among the subscription's billing lines.

    Args:
        garden_sub_id: Id class — the reference number of the Garden fixed-rate subscription agreement being paid,
            as given to the account holder by the representative from the Garden subscription lookup.
        amount: Fixed-format class — the amount paid in US dollars, a positive number with 2 decimal places; the
            portal rounds the value half up to the cent once, on receipt.
        payment_method: Enum class — how the account holder pays: ach (a debit from the holder's bank account
            entered by the holder in the portal); card (a debit or credit card entered by the holder in the
            portal); check (a paper check the holder mails, recorded on receipt); utility_remittance (the utility
            paying a consolidated-billed charge on the holder's utility bill); not_applicable (a ledger line that is
            not a payment).

    Returns:
        A one-line confirmation string naming the payment reference (text), the subscription reference (text), the
        amount paid in US dollars with two decimals, the method and the receipt date (YYYY-MM-DD). The presence of
        the payment reference indicates the payment was recorded. An amount that is not positive records
        nothing and returns a one-line notice saying so.
    """
    subs = ctx.find("garden_subscriptions", garden_sub_id=garden_sub_id)
    customer_id = subs[0].get("customer_id", "") if subs else ""
    amt = _Money.cents(amount)
    if amt <= 0:
        return "Nothing booked: the amount must be a positive number of US dollars with 2 decimal places."
    today = ctx.now()[:10]
    rid = ctx.make_id("gpy_", garden_sub_id, amount, payment_method)
    ctx.create("garden_billing", rid, garden_bill_id=rid, garden_sub_id=garden_sub_id, customer_id=customer_id,
               event_type="garden_payment_received", amount=amt, bill_date=today, billing_month=today[:7],
               due_date="", garden_credit_id="", garden_ref_bill_id="", charge_basis="not_applicable",
               billing_type="dual", payment_method=payment_method, credit_reason="not_applicable")
    return (f"Payment {rid} recorded on subscription {garden_sub_id}: {amt:.2f} USD by {payment_method}, "
            f"received {today}.")


@tool(owner="agent", rw="write")
def assess_closing_etf_e3af903e(ctx: ToolContext, garden_sub_id: str, amount: float, assessment_date: str,
                                due_date: str) -> str:
    """Book the early termination fee of a closed residential Garden fixed-rate subscription on its billing ledger.
    One call adds one early-termination-fee line to that subscription's ledger, raising the balance the business
    owes Meadowlark by the amount given; the line is dual billed, belongs to the statement month of the assessment
    date and appears at once among the subscription's billing lines.

    Args:
        garden_sub_id: Id class — the reference number of the Garden fixed-rate subscription agreement the fee is
            booked on, as returned by the Garden subscription lookup.
        amount: Fixed-format class — the fee in US dollars, a positive number with 2 decimal places (a value that is not positive books
            nothing); the tool rounds the value half up to the cent once, on receipt.
        assessment_date: Fixed-format class — the date the fee is assessed, written YYYY-MM-DD (calendar date,
            Central time); the line's statement month is the year and month of this date.
        due_date: Fixed-format class — the date the fee falls due, written YYYY-MM-DD (calendar date, Central time).

    Returns:
        A one-line confirmation string naming the new ledger line reference (text), the subscription reference
        (text), the fee booked in US dollars with two decimals, the statement month (YYYY-MM) and the due date
        (YYYY-MM-DD). The presence of the line reference indicates the fee line was booked. An amount that is not positive books nothing and returns a one-line notice saying so.
    """
    subs = ctx.find("garden_subscriptions", garden_sub_id=garden_sub_id)
    customer_id = subs[0].get("customer_id", "") if subs else ""
    amt = _Money.cents(amount)
    if amt <= 0:
        return "Nothing booked: the amount must be a positive number of US dollars with 2 decimal places."
    rid = ctx.make_id("gbl_", garden_sub_id, amount, assessment_date, due_date, "etf")
    ctx.create("garden_billing", rid, garden_bill_id=rid, garden_sub_id=garden_sub_id, customer_id=customer_id,
               event_type="garden_etf_assessed", amount=amt, bill_date=assessment_date,
               billing_month=str(assessment_date)[:7], due_date=due_date, garden_credit_id="", garden_ref_bill_id="",
               charge_basis="not_applicable", billing_type="dual", payment_method="not_applicable",
               credit_reason="not_applicable")
    return (f"Early termination fee line {rid} booked on subscription {garden_sub_id}: {amt:.2f} USD, "
            f"statement month {str(assessment_date)[:7]}, due {due_date}.")


@tool(owner="agent", rw="write")
def assess_reopened_late_fee_3e91b283(ctx: ToolContext, garden_sub_id: str, garden_ref_bill_id: str, amount: float,
                                      assessment_date: str, due_date: str) -> str:
    """Book a late fee on one overdue subscription charge of a residential Garden fixed-rate subscription. One call
    adds one late-fee line that refers to the overdue charge, raising the balance the household owes Meadowlark by
    the amount given; the line takes the statement month of the overdue charge, is dual billed and appears at once
    among the subscription's billing lines.

    Args:
        garden_sub_id: Id class — the reference number of the Garden fixed-rate subscription agreement, as returned
            by the Garden subscription lookup.
        garden_ref_bill_id: Id class — the reference number of the overdue subscription charge line the fee is
            assessed on, as returned by the Garden billing ledger lookup.
        amount: Fixed-format class — the late fee in US dollars, a positive number with 2 decimal places; the
            tool rounds the value half up to the cent once, on receipt.
        assessment_date: Fixed-format class — the date the fee is assessed, written YYYY-MM-DD (calendar date,
            Central time).
        due_date: Fixed-format class — the date the fee falls due, written YYYY-MM-DD (calendar date, Central time).

    Returns:
        A one-line confirmation string naming the new ledger line reference (text), the overdue charge it refers
        to (text), the fee booked in US dollars with two decimals, the statement month (YYYY-MM) and the due date
        (YYYY-MM-DD). The presence of the line reference indicates the fee line was booked. An amount that is not positive books nothing and returns a one-line notice saying so.
    """
    subs = ctx.find("garden_subscriptions", garden_sub_id=garden_sub_id)
    customer_id = subs[0].get("customer_id", "") if subs else ""
    ref = ctx.find("garden_billing", garden_bill_id=garden_ref_bill_id)
    month = ref[0].get("billing_month", "") if ref else ""
    amt = _Money.cents(amount)
    if amt <= 0:
        return "Nothing booked: the amount must be a positive number of US dollars with 2 decimal places."
    rid = ctx.make_id("gbl_", garden_sub_id, garden_ref_bill_id, amount, assessment_date, due_date, "late")
    ctx.create("garden_billing", rid, garden_bill_id=rid, garden_sub_id=garden_sub_id, customer_id=customer_id,
               event_type="garden_late_fee_assessed", amount=amt, bill_date=assessment_date, billing_month=month,
               due_date=due_date, garden_credit_id="", garden_ref_bill_id=garden_ref_bill_id,
               charge_basis="not_applicable", billing_type="dual", payment_method="not_applicable",
               credit_reason="not_applicable")
    return (f"Late fee line {rid} booked on subscription {garden_sub_id} for charge {garden_ref_bill_id}: "
            f"{amt:.2f} USD, statement month {month}, due {due_date}.")


@tool(owner="agent", rw="write")
def assess_decrease_fee_99d02cc8(ctx: ToolContext, garden_sub_id: str, decrease_filing_id: str, amount: float,
                                 assessment_date: str, due_date: str) -> str:
    """Book the excess-decrease fee for one subscriber decrease of a residential Garden fixed-rate subscription. One
    call adds one excess-decrease-fee line, raising the balance the household owes Meadowlark by the amount given;
    the line takes the filing month of the decrease filing as its statement month, is dual billed and appears at
    once among the subscription's billing lines.

    Args:
        garden_sub_id: Id class — the reference number of the Garden fixed-rate subscription agreement, as returned
            by the Garden subscription lookup.
        decrease_filing_id: Id class — the reference number of the allocation filing line that removed the kW the
            subscriber asked to remove, as returned by the Garden allocation filing lookup.
        amount: Fixed-format class — the fee in US dollars, a positive number with 2 decimal places (a value that is not positive books
            nothing); the tool rounds the value half up to the cent once, on receipt.
        assessment_date: Fixed-format class — the date the fee is assessed, written YYYY-MM-DD (calendar date,
            Central time).
        due_date: Fixed-format class — the date the fee falls due, written YYYY-MM-DD (calendar date, Central time).

    Returns:
        A one-line confirmation string naming the new ledger line reference (text), the decrease filing it prices
        (text), the fee booked in US dollars with two decimals, the statement month (YYYY-MM) and the due date
        (YYYY-MM-DD). The presence of the line reference indicates the fee line was booked. An amount that is not positive books nothing and returns a one-line notice saying so.
    """
    subs = ctx.find("garden_subscriptions", garden_sub_id=garden_sub_id)
    customer_id = subs[0].get("customer_id", "") if subs else ""
    fil = ctx.find("garden_allocations", garden_filing_id=decrease_filing_id)
    month = fil[0].get("filing_month", "") if fil else ""
    amt = _Money.cents(amount)
    if amt <= 0:
        return "Nothing booked: the amount must be a positive number of US dollars with 2 decimal places."
    rid = ctx.make_id("gbl_", garden_sub_id, decrease_filing_id, amount, assessment_date, due_date, "chg")
    ctx.create("garden_billing", rid, garden_bill_id=rid, garden_sub_id=garden_sub_id, customer_id=customer_id,
               event_type="garden_change_fee_assessed", amount=amt, bill_date=assessment_date, billing_month=month,
               due_date=due_date, garden_credit_id="", garden_ref_bill_id="", charge_basis="not_applicable",
               billing_type="dual", payment_method="not_applicable", credit_reason="not_applicable")
    return (f"Excess-decrease fee line {rid} booked on subscription {garden_sub_id} for filing {decrease_filing_id}: "
            f"{amt:.2f} USD, statement month {month}, due {due_date}.")


@tool(owner="user", rw="write")
def pay_garden_settlement_8237cc21(ctx: ToolContext, garden_sub_id: str, amount: float, payment_method: str) -> str:
    """Pay a settlement on a residential Garden fixed-rate subscription through Meadowlark's secure payment portal.
    The account holder makes the payment personally: one call records one payment received on that subscription,
    lowering its balance by the amount paid; the payment carries today's date and statement month and appears at
    once among the subscription's billing lines.

    Args:
        garden_sub_id: Id class — the reference number of the Garden fixed-rate subscription agreement being paid,
            as given to the account holder by the representative from the Garden subscription lookup.
        amount: Fixed-format class — the amount paid in US dollars, a positive number with 2 decimal places; the
            portal rounds the value half up to the cent once, on receipt.
        payment_method: Enum class — how the account holder pays: ach (a debit from the holder's bank account
            entered by the holder in the portal); card (a debit or credit card entered by the holder in the
            portal); check (a paper check the holder mails, recorded on receipt); utility_remittance (the utility
            paying a consolidated-billed charge on the holder's utility bill); not_applicable (a ledger line that is
            not a payment).

    Returns:
        A one-line confirmation string naming the payment reference (text), the subscription reference (text), the
        amount paid in US dollars with two decimals, the method and the receipt date (YYYY-MM-DD). The presence of
        the payment reference indicates the payment was recorded. An amount that is not positive records
        nothing and returns a one-line notice saying so.
    """
    subs = ctx.find("garden_subscriptions", garden_sub_id=garden_sub_id)
    customer_id = subs[0].get("customer_id", "") if subs else ""
    amt = _Money.cents(amount)
    if amt <= 0:
        return "Nothing booked: the amount must be a positive number of US dollars with 2 decimal places."
    today = ctx.now()[:10]
    rid = ctx.make_id("gpy_", garden_sub_id, amount, payment_method)
    ctx.create("garden_billing", rid, garden_bill_id=rid, garden_sub_id=garden_sub_id, customer_id=customer_id,
               event_type="garden_payment_received", amount=amt, bill_date=today, billing_month=today[:7],
               due_date="", garden_credit_id="", garden_ref_bill_id="", charge_basis="not_applicable",
               billing_type="dual", payment_method=payment_method, credit_reason="not_applicable")
    return (f"Payment {rid} recorded on subscription {garden_sub_id}: {amt:.2f} USD by {payment_method}, "
            f"received {today}.")

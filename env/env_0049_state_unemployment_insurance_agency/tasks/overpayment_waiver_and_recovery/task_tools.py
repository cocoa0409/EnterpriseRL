"""Hidden task tools for the overpayment_waiver_and_recovery difficulty (Benefit Overpayment Accounts).

Each tool performs one atomic write on the claimant's overpayment records with the values it is
given; it judges no eligibility, ordering or amount. Calendar arithmetic is done with the pure
helper class below, because a module-level helper function would be read as a tool.
"""

from erlbench import ToolContext, tool


class _CivilCalendar:
    """Pure calendar arithmetic on YYYY-MM-DD strings (proleptic Gregorian, no clock access)."""

    @staticmethod
    def to_day_number(day: str) -> int:
        y, m, d = (int(p) for p in str(day)[:10].split("-"))
        y -= 1 if m <= 2 else 0
        era = (y if y >= 0 else y - 399) // 400
        yoe = y - era * 400
        doy = (153 * (m + (-3 if m > 2 else 9)) + 2) // 5 + d - 1
        doe = yoe * 365 + yoe // 4 - yoe // 100 + doy
        return era * 146097 + doe - 719468

    @staticmethod
    def from_day_number(n: int) -> str:
        n += 719468
        era = (n if n >= 0 else n - 146096) // 146097
        doe = n - era * 146097
        yoe = (doe - doe // 1460 + doe // 36524 - doe // 146096) // 365
        y = yoe + era * 400
        doy = doe - (365 * yoe + yoe // 4 - yoe // 100)
        mp = (5 * doy + 2) // 153
        d = doy - (153 * mp + 2) // 5 + 1
        m = mp + (3 if mp < 10 else -9)
        y += 1 if m <= 2 else 0
        return f"{y:04d}-{m:02d}-{d:02d}"

    @staticmethod
    def add_days(day: str, days: int) -> str:
        return _CivilCalendar.from_day_number(_CivilCalendar.to_day_number(day) + int(days))


@tool(owner="agent", rw="write")
def book_returned_payment_fee_10cb479c(ctx: ToolContext, overpayment_id: str, payment_reference: str,
                                       fee_amount: float) -> str:
    """Book the returned-payment fee owed for one repayment that the claimant's bank returned unpaid.

    The Department's representative uses this to charge the fee for a single returned repayment on
    a benefit overpayment. One call adds one fee entry of the given amount, tied to the returned
    repayment's confirmation number, to the overpayment's ledger as its own fee component, and
    raises the overpayment's balance due by the same amount. On success the fee appears on
    the overpayment's ledger and in its balance due; nothing else on the overpayment changes.

    Args:
        overpayment_id: Id class — the reference number of the benefit overpayment the returned repayment was made toward, as shown on the overpayment record returned by the overpayment lookup.
        payment_reference: Verbatim class — the confirmation number of the returned repayment exactly as it appears on that repayment's return entry in the overpayment ledger lookup, copied character for character with no change to letters, digits or punctuation (verbatim).
        fee_amount: Fixed-format class — the fee to charge, in USD, 2 decimal places, always positive; amounts with more decimals are rounded to the nearest cent when booked.

    Returns:
        A text rendering of a dictionary receipt with these fields: fee_entry_id (string, the
        reference number of the new fee entry, present only when the fee was booked),
        overpayment_id (string, the overpayment charged), payment_reference (string, the returned
        repayment the fee is for), fee_amount (number, the fee booked in USD to 2 decimal places),
        booked_on (string, YYYY-MM-DD date of booking) and balance_due (number, the overpayment's
        balance due in USD including the fee). A receipt carrying a fee_entry_id means the fee is
        booked. If the overpayment reference number matches no overpayment, the text starts with
        "Error:" and nothing is booked.
    """
    rows = ctx.find("overpayments", overpayment_id=overpayment_id)
    if not rows:
        return f"Error: no overpayment {overpayment_id}."
    holding = rows[0]
    amount = round(float(fee_amount), 2)
    today = ctx.now()[:10]
    rid = ctx.make_id("opf_", overpayment_id, payment_reference, amount)
    ctx.create("overpay_ledger", rid, overpay_entry_id=rid, overpayment_id=overpayment_id,
               customer_id=holding.get("customer_id"), event_type="overpay_fee_assessed", component="fee",
               amount=amount, entry_date=today, accrual_month="", fee_type="returned_payment",
               payment_reference=payment_reference, payment_channel="not_applicable",
               intercept_source="not_applicable", intercept_reference="", source_payment_id=None,
               source_payment_amount=0.0, week_ending_date="", waiver_request_id=None, appeal_id=None,
               refund_basis="none")
    new_balance = round(float(holding.get("balance_due") or 0) + amount, 2)
    ctx.update("overpayments", overpayment_id, balance_due=new_balance)
    return str({"fee_entry_id": rid, "overpayment_id": overpayment_id, "payment_reference": payment_reference,
                "fee_amount": amount, "booked_on": today, "balance_due": new_balance})


@tool(owner="user", rw="write")
def pay_overpayment_arrears_d9b1e543(ctx: ToolContext, overpayment_id: str, amount: float) -> str:
    """Pay the arrears of a defaulted overpayment repayment plan by card through the Department's payment line.

    The claimant uses this to make one card repayment designated to one of their benefit
    overpayments. One call takes one payment of the given amount, records it on the overpayment's
    ledger as a repayment applied to the overpayment's penalty component with the card channel and
    a newly issued confirmation number, and lowers the overpayment's balance due by the amount.
    The card vendor's convenience fee is charged separately by the vendor and is never part of the
    amount. On success the payment and its confirmation number appear on the overpayment's
    ledger and the balance due is lower.

    Args:
        overpayment_id: Id class — the reference number of the benefit overpayment the claimant is paying, as given to the claimant by the representative from the overpayment record.
        amount: Fixed-format class — the payment amount in USD, 2 decimal places, always positive, as the representative states it; amounts with more decimals are rounded to the nearest cent when booked.

    Returns:
        A text rendering of a dictionary receipt with these fields: payment_reference (string, the
        confirmation number issued for this payment, present only when the payment was taken),
        overpayment_id (string, the overpayment paid), amount_applied (number, USD to 2 decimal
        places), component (string, always penalty), payment_channel (string, always
        debit_or_credit_card), received_on (string, YYYY-MM-DD) and balance_due (number, the
        overpayment's balance due in USD net of the payment). A receipt carrying a
        payment_reference means the payment was taken. If the overpayment reference number
        matches no overpayment, the text starts with "Error:" and nothing is taken.
    """
    rows = ctx.find("overpayments", overpayment_id=overpayment_id)
    if not rows:
        return f"Error: no overpayment {overpayment_id}."
    holding = rows[0]
    paid = round(float(amount), 2)
    today = ctx.now()[:10]
    reference = ctx.make_id("LKP-CC-", overpayment_id, paid, today)
    rid = ctx.make_id("opr_", overpayment_id, paid, reference)
    ctx.create("overpay_ledger", rid, overpay_entry_id=rid, overpayment_id=overpayment_id,
               customer_id=holding.get("customer_id"), event_type="overpay_repayment_received",
               component="penalty", amount=paid, entry_date=today, accrual_month="", fee_type="none",
               payment_reference=reference, payment_channel="debit_or_credit_card",
               intercept_source="not_applicable", intercept_reference="", source_payment_id=None,
               source_payment_amount=0.0, week_ending_date="", waiver_request_id=None, appeal_id=None,
               refund_basis="none")
    new_balance = round(float(holding.get("balance_due") or 0) - paid, 2)
    ctx.update("overpayments", overpayment_id, balance_due=new_balance)
    return str({"payment_reference": reference, "overpayment_id": overpayment_id, "amount_applied": paid,
                "component": "penalty", "payment_channel": "debit_or_credit_card", "received_on": today,
                "balance_due": new_balance})


@tool(owner="user", rw="write")
def reinstate_repayment_plan_54c54ed5(ctx: ToolContext, overpayment_id: str, monthly_amount: float) -> str:
    """Reinstate the claimant's defaulted monthly repayment plan on one benefit overpayment.

    The claimant uses this to agree to have a defaulted repayment plan put back in force. One call
    sets the plan status on the overpayment to current and replaces the plan's monthly installment
    with the given amount; the due date of the plan's opening installment and the monthly due day
    stay as they were. On success the overpayment record shows the plan as current with the
    new monthly installment.

    Args:
        overpayment_id: Id class — the reference number of the benefit overpayment whose plan is reinstated, as given to the claimant by the representative from the overpayment record.
        monthly_amount: Fixed-format class — the reinstated monthly installment in USD, 2 decimal places; 0.00 when no plan, as the representative states it; amounts with more decimals are rounded to the nearest cent when recorded.

    Returns:
        A text rendering of a dictionary receipt with these fields: overpayment_id (string),
        repayment_plan_status (string, current when the plan was reinstated),
        repayment_plan_monthly_amount (number, the installment recorded in USD to 2 decimal places)
        and repayment_plan_start_date (string, YYYY-MM-DD due date of the plan's opening
        installment, unchanged). A receipt showing repayment_plan_status current means the plan is
        reinstated. If the overpayment reference number matches no overpayment, the text starts
        with "Error:" and nothing changes.
    """
    rows = ctx.find("overpayments", overpayment_id=overpayment_id)
    if not rows:
        return f"Error: no overpayment {overpayment_id}."
    installment = round(float(monthly_amount), 2)
    ctx.update("overpayments", overpayment_id, repayment_plan_status="current",
               repayment_plan_monthly_amount=installment)
    return str({"overpayment_id": overpayment_id, "repayment_plan_status": "current",
                "repayment_plan_monthly_amount": installment,
                "repayment_plan_start_date": rows[0].get("repayment_plan_start_date")})


@tool(owner="user", rw="write")
def set_up_repayment_plan_0b609272(ctx: ToolContext, overpayment_id: str, monthly_amount: float) -> str:
    """Set up a new monthly repayment plan on one benefit overpayment that has no plan.

    The claimant uses this to agree to a monthly repayment plan. One call sets the plan status on
    the overpayment to current, records the given monthly installment, and records the due date of
    the plan's opening installment as thirty calendar days from today; the remaining installments fall due
    on the classification's monthly due day. On success the overpayment record shows the plan
    as current with its installment and opening due date.

    Args:
        overpayment_id: Id class — the reference number of the benefit overpayment the plan is set on, as given to the claimant by the representative from the overpayment record.
        monthly_amount: Fixed-format class — the agreed monthly installment in USD, 2 decimal places; 0.00 when no plan, as the representative states it; amounts with more decimals are rounded to the nearest cent when recorded.

    Returns:
        A text rendering of a dictionary receipt with these fields: overpayment_id (string),
        repayment_plan_status (string, current when the plan was set),
        repayment_plan_monthly_amount (number, the installment recorded in USD to 2 decimal places)
        and repayment_plan_start_date (string, YYYY-MM-DD due date of the plan's opening
        installment). A receipt showing repayment_plan_status current means the plan is set. If the
        overpayment reference number matches no overpayment, the text starts with "Error:" and
        nothing changes.
    """
    rows = ctx.find("overpayments", overpayment_id=overpayment_id)
    if not rows:
        return f"Error: no overpayment {overpayment_id}."
    installment = round(float(monthly_amount), 2)
    opening_due = _CivilCalendar.add_days(ctx.now()[:10], 30)
    ctx.update("overpayments", overpayment_id, repayment_plan_status="current",
               repayment_plan_monthly_amount=installment, repayment_plan_start_date=opening_due)
    return str({"overpayment_id": overpayment_id, "repayment_plan_status": "current",
                "repayment_plan_monthly_amount": installment, "repayment_plan_start_date": opening_due})


@tool(owner="user", rw="write")
def complete_waiver_household_income_abba3816(ctx: ToolContext, overpayment_id: str, waiver_request_id: str,
                                              annual_household_income: float) -> str:
    """Complete the claimant's own waiver request by entering the household's annual income on it.

    The claimant uses this to fill in the annual household income on a waiver request they lodged
    for one of their benefit overpayments. One call writes the given amount into the request's
    annual household income; the household size, the date received and the request's status stay
    as they were. On success the waiver request shows the entered annual household income.

    Args:
        overpayment_id: Id class — the reference number of the benefit overpayment the waiver request was lodged for, as given to the claimant by the representative from the overpayment record.
        waiver_request_id: Id class — the reference number of the claimant's waiver request, as given to the claimant by the representative from the waiver request record.
        annual_household_income: Fixed-format class — the household's annual income in USD, 2 decimal places, as the representative states it; amounts with more decimals are rounded to the nearest cent when recorded.

    Returns:
        A text rendering of a dictionary receipt with these fields: waiver_request_id (string),
        overpayment_id (string), household_size (integer, the household size already on the
        request), annual_household_income (number, the income recorded in USD to 2 decimal places)
        and request_status (string, the request's unchanged status). A receipt showing the entered
        annual_household_income means the request is completed. If the two reference numbers do
        not match one waiver request, the text starts with "Error:" and nothing changes.
    """
    rows = ctx.find("overpay_waiver_requests", waiver_request_id=waiver_request_id, overpayment_id=overpayment_id)
    if not rows:
        return f"Error: no waiver request {waiver_request_id} on overpayment {overpayment_id}."
    income = round(float(annual_household_income), 2)
    ctx.update("overpay_waiver_requests", waiver_request_id, annual_household_income=income)
    return str({"waiver_request_id": waiver_request_id, "overpayment_id": overpayment_id,
                "household_size": rows[0].get("household_size"), "annual_household_income": income,
                "request_status": rows[0].get("request_status")})


@tool(owner="agent", rw="write")
def record_waiver_decision_07f617be(ctx: ToolContext, overpayment_id: str, waiver_request_id: str, decision: str,
                                    waived_amount: float) -> str:
    """Record the Department's decision on a claimant's waiver request and remove any waived principal.

    The Department's representative uses this to decide one waiver request under review on a benefit
    overpayment. One call records the decision on the request; when the waived amount is above zero
    it adds one waiver adjustment of that amount to the overpayment's ledger, tied to the request,
    and lowers the balance due by it. A granted request closes the overpayment as waived with
    today's date; a partially granted or denied request returns the overpayment to recovery. On
    success the request shows its decision and the overpayment shows its new status and balance.

    Args:
        overpayment_id: Id class — the reference number of the benefit overpayment the request concerns, as shown on the overpayment record returned by the overpayment lookup.
        waiver_request_id: Id class — the reference number of the waiver request being decided, as shown on the waiver request record returned by the waiver request lookup.
        decision: Enum class — the decision recorded on the request, exactly one of: received — the request is left undecided and nothing else is recorded; granted — the whole unpaid principal is waived and the overpayment closes as waived; partially_granted — an amount above zero but less than the whole unpaid principal is waived and the rest stays in recovery; denied — nothing is waived and the overpayment returns to recovery.
        waived_amount: Fixed-format class — the principal waived in USD, 2 decimal places, always positive when a waiver adjustment is booked; 0.00 for a denial or an undecided request, in which case no adjustment is booked; amounts with more decimals are rounded to the nearest cent.

    Returns:
        A text rendering of a dictionary receipt with these fields: overpayment_id (string),
        waiver_request_id (string), decision (string, the decision recorded), waived_amount
        (number, USD to 2 decimal places), adjustment_entry_id (string reference number of the
        waiver adjustment, or None when nothing was waived), overpayment_status (string, the
        overpayment's status as recorded by this call) and balance_due (number, the overpayment's balance due in
        USD). A receipt showing the decision means it is recorded. If the overpayment reference
        number matches no overpayment, the text starts with "Error:" and nothing changes.
    """
    rows = ctx.find("overpayments", overpayment_id=overpayment_id)
    if not rows:
        return f"Error: no overpayment {overpayment_id}."
    holding = rows[0]
    waived = round(float(waived_amount), 2)
    today = ctx.now()[:10]
    ctx.update("overpay_waiver_requests", waiver_request_id, request_status=decision)
    balance = round(float(holding.get("balance_due") or 0), 2)
    entry_id = None
    if decision != "received" and waived > 0:
        entry_id = ctx.make_id("opw_", overpayment_id, waiver_request_id, waived)
        ctx.create("overpay_ledger", entry_id, overpay_entry_id=entry_id, overpayment_id=overpayment_id,
                   customer_id=holding.get("customer_id"), event_type="overpay_waiver_adjusted", component="principal",
                   amount=waived, entry_date=today, accrual_month="", fee_type="none", payment_reference="",
                   payment_channel="not_applicable", intercept_source="not_applicable", intercept_reference="",
                   source_payment_id=None, source_payment_amount=0.0, week_ending_date="",
                   waiver_request_id=waiver_request_id, appeal_id=None, refund_basis="none")
        balance = round(balance - waived, 2)
    status = holding.get("status")
    if decision == "granted":
        status = "waived"
        ctx.update("overpayments", overpayment_id, status=status, closed_date=today, balance_due=balance)
    elif decision in ("partially_granted", "denied"):
        status = "in_recovery"
        ctx.update("overpayments", overpayment_id, status=status, balance_due=balance)
    return str({"overpayment_id": overpayment_id, "waiver_request_id": waiver_request_id, "decision": decision,
                "waived_amount": waived, "adjustment_entry_id": entry_id, "overpayment_status": status,
                "balance_due": balance})


@tool(owner="user", rw="write")
def change_repayment_plan_f1933d01(ctx: ToolContext, overpayment_id: str, monthly_amount: float) -> str:
    """Change the monthly installment of the claimant's current repayment plan on one benefit overpayment.

    The claimant uses this to agree to a new monthly installment on a plan that is already in force.
    One call replaces the plan's monthly installment with the given amount; the plan status, the
    due date of the plan's opening installment and the monthly due day stay as they were. On
    success the overpayment record shows the plan with the new monthly installment.

    Args:
        overpayment_id: Id class — the reference number of the benefit overpayment whose plan is changed, as given to the claimant by the representative from the overpayment record.
        monthly_amount: Fixed-format class — the new monthly installment in USD, 2 decimal places; 0.00 when no plan, as the representative states it; amounts with more decimals are rounded to the nearest cent when recorded.

    Returns:
        A text rendering of a dictionary receipt with these fields: overpayment_id (string),
        repayment_plan_status (string, the plan status, unchanged), repayment_plan_monthly_amount
        (number, the installment recorded in USD to 2 decimal places) and repayment_plan_start_date
        (string, YYYY-MM-DD due date of the plan's opening installment, unchanged). A receipt
        showing the new repayment_plan_monthly_amount means the change is recorded. If the
        overpayment reference number matches no overpayment, the text starts with "Error:" and
        nothing changes.
    """
    rows = ctx.find("overpayments", overpayment_id=overpayment_id)
    if not rows:
        return f"Error: no overpayment {overpayment_id}."
    installment = round(float(monthly_amount), 2)
    ctx.update("overpayments", overpayment_id, repayment_plan_monthly_amount=installment)
    return str({"overpayment_id": overpayment_id, "repayment_plan_status": rows[0].get("repayment_plan_status"),
                "repayment_plan_monthly_amount": installment,
                "repayment_plan_start_date": rows[0].get("repayment_plan_start_date")})

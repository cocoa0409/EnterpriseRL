"""Hidden task tools for env_0072_subprime_auto_lender, difficulty recovery_repossession_and_reinstatement.

Each tool performs one atomic write on a repossession case of Harborline Acceptance Corporation.
Tools never check policy conditions; the agent decides from the published policy and the records.
"""

from erlbench import ToolContext, tool


class _CalendarMath:
    """Pure calendar arithmetic on 'YYYY-MM-DD' strings (proleptic Gregorian day numbers)."""

    @staticmethod
    def to_ordinal(day: str) -> int:
        y, m, d = (int(p) for p in str(day)[:10].split("-"))
        y -= m <= 2
        era = (y if y >= 0 else y - 399) // 400
        yoe = y - era * 400
        doy = (153 * (m + (-3 if m > 2 else 9)) + 2) // 5 + d - 1
        doe = yoe * 365 + yoe // 4 - yoe // 100 + doy
        return era * 146097 + doe

    @staticmethod
    def from_ordinal(n: int) -> str:
        era = (n if n >= 0 else n - 146096) // 146097
        doe = n - era * 146097
        yoe = (doe - doe // 1460 + doe // 36524 - doe // 146096) // 365
        y = yoe + era * 400
        doy = doe - (365 * yoe + yoe // 4 - yoe // 100)
        mp = (5 * doy + 2) // 153
        d = doy - (153 * mp + 2) // 5 + 1
        m = mp + (3 if mp < 10 else -9)
        y += m <= 2
        return f"{y:04d}-{m:02d}-{d:02d}"

    @staticmethod
    def plus_days(day: str, days: int) -> str:
        return _CalendarMath.from_ordinal(_CalendarMath.to_ordinal(day) + int(days))


_ACTIVITY_DEFAULTS = dict(
    notice_type="not_applicable", delivery_method="not_applicable", deadline_date="",
    stated_amount_usd=0.0, expense_type="not_applicable", amount_usd=0.0, chargeable_days=0,
    related_activity_id="", waiver_reason="not_applicable", settlement_method="not_applicable",
    past_due_installments_usd=0.0, late_charges_usd=0.0, expenses_usd=0.0,
    property_disposition="not_applicable",
)


@tool(owner="agent", rw="write")
def post_agency_recovery_fee_54cbecc0(ctx: ToolContext, recovery_case_id: str, amount_usd: float) -> str:
    """Charge the recovery agency's fee for an involuntary recovery to a repossession case. One call
    records one new expense of kind involuntary repossession fee on the case, dated today, and raises
    the case's posted recovery expenses outstanding by the same amount; the borrower and the agent can
    then see the new expense in the case activity and the higher outstanding figure on the case.

    Args:
        recovery_case_id: Id class — the reference number of the repossession case the fee is charged
            to, as returned by the repossession case lookup for this borrower's contract.
        amount_usd: Fixed-format class — the agency recovery fee being charged, in US dollars as a
            positive decimal number with exactly 2 decimal places, already rounded to the cent; the
            tool stores it rounded to 2 decimal places.

    Returns:
        A confirmation string naming the new case activity reference number (a text identifier that
        begins with "rfee_"), the case reference number, the fee charged in USD with 2 decimal places,
        the posting date in YYYY-MM-DD form and the case's new recovery expenses outstanding in USD
        with 2 decimal places. A string that begins with "Recovery fee posted" means the expense was
        recorded.
    """
    case = (ctx.find("recovery_cases", recovery_case_id=recovery_case_id) or [{}])[0]
    amount = round(float(amount_usd), 2)
    today = ctx.now()[:10]
    rid = ctx.make_id("rfee_", recovery_case_id, amount_usd)
    fields = dict(_ACTIVITY_DEFAULTS)
    fields.update(recovery_activity_id=rid, recovery_case_id=recovery_case_id,
                  contract_id=case.get("contract_id", ""), customer_id=case.get("customer_id", ""),
                  event_type="recovery_expense_posted", activity_date=today,
                  expense_type="involuntary_repossession_fee", amount_usd=amount)
    ctx.create("recovery_activities", rid, **fields)
    new_outstanding = round(float(case.get("expenses_outstanding_usd") or 0) + amount, 2)
    ctx.update("recovery_cases", recovery_case_id, expenses_outstanding_usd=new_outstanding)
    return (f"Recovery fee posted: activity {rid} on case {recovery_case_id}, {amount:.2f} USD dated "
            f"{today}; recovery expenses outstanding now {new_outstanding:.2f} USD.")


@tool(owner="agent", rw="write")
def mail_corrected_sale_notice_6ba1fcf2(ctx: ToolContext, recovery_case_id: str, sale_notice_days: int,
                                        stated_amount_usd: float) -> str:
    """Mail the borrower a notice of intent to sell the repossessed vehicle on a repossession case. One
    call records one notice of intent to sell on the case, mailed today by certified mail with return
    receipt, whose earliest sale date is today's date moved forward by the given number of calendar
    days, and which states the given reinstatement amount. The notice, its mailing date, its earliest
    sale date and its stated amount then show in the case activity.

    Args:
        recovery_case_id: Id class — the reference number of the repossession case the notice is
            mailed on, as returned by the repossession case lookup for this borrower's contract.
        sale_notice_days: Fixed-format class — the sale period of the notice as a whole number of
            calendar days counted from today's mailing date to the earliest sale date (an integer of 1
            or more, no fractions); the tool sets the earliest sale date to today's date plus this many
            calendar days.
        stated_amount_usd: Fixed-format class — the reinstatement amount the notice states, in US
            dollars as a decimal number with exactly 2 decimal places, 0.00 when the notice states no
            reinstatement amount; the tool stores it rounded to 2 decimal places.

    Returns:
        A confirmation string naming the new case activity reference number (a text identifier that
        begins with "rnoi_"), the case reference number, the mailing date and the earliest sale date
        both in YYYY-MM-DD form, the delivery method certified_mail_return_receipt and the stated
        reinstatement amount in USD with 2 decimal places. A string that begins with "Notice of intent
        to sell mailed" means the notice was recorded.
    """
    case = (ctx.find("recovery_cases", recovery_case_id=recovery_case_id) or [{}])[0]
    today = ctx.now()[:10]
    sale_date = _CalendarMath.plus_days(today, int(sale_notice_days))
    stated = round(float(stated_amount_usd), 2)
    rid = ctx.make_id("rnoi_", recovery_case_id, sale_notice_days, stated_amount_usd)
    fields = dict(_ACTIVITY_DEFAULTS)
    fields.update(recovery_activity_id=rid, recovery_case_id=recovery_case_id,
                  contract_id=case.get("contract_id", ""), customer_id=case.get("customer_id", ""),
                  event_type="recovery_notice_sent", activity_date=today,
                  notice_type="notice_of_intent_to_sell", delivery_method="certified_mail_return_receipt",
                  deadline_date=sale_date, stated_amount_usd=stated)
    ctx.create("recovery_activities", rid, **fields)
    return (f"Notice of intent to sell mailed: activity {rid} on case {recovery_case_id}, mailed {today}, "
            f"earliest sale date {sale_date}, delivery certified_mail_return_receipt, stated amount "
            f"{stated:.2f} USD.")


@tool(owner="user", rw="write")
def pay_redemption_recovery_expenses_4986a691(ctx: ToolContext, recovery_case_id: str, amount_usd: float) -> str:
    """The borrower pays, from their own funds, the recovery
    expense portion of redeeming their repossessed vehicle on a repossession case. One call records one
    settlement of the case's recovery expenses paid by the borrower, dated today, for the given amount,
    and lowers the case's posted recovery expenses outstanding by that amount, never below 0.00. The
    borrower then sees the payment in the case activity and the reduced outstanding figure on the case.

    Args:
        recovery_case_id: Id class — the reference number of the borrower's repossession case, as the
            agent reads it out from the repossession case lookup for the borrower's contract.
        amount_usd: Fixed-format class — the amount the borrower pays toward the case's recovery
            expenses, in US dollars as a positive decimal number with exactly 2 decimal places, already
            rounded to the cent; the tool stores it rounded to 2 decimal places.

    Returns:
        A confirmation string naming the new case activity reference number (a text identifier that
        begins with "rdxp_"), the case reference number, the amount paid in USD with 2 decimal places,
        the settlement method paid_by_borrower, the payment date in YYYY-MM-DD form and the case's
        remaining recovery expenses outstanding in USD with 2 decimal places. A string that begins with
        "Redemption expense payment received" means the payment was recorded.
    """
    case = (ctx.find("recovery_cases", recovery_case_id=recovery_case_id) or [{}])[0]
    amount = round(float(amount_usd), 2)
    today = ctx.now()[:10]
    rid = ctx.make_id("rdxp_", recovery_case_id, amount_usd)
    fields = dict(_ACTIVITY_DEFAULTS)
    fields.update(recovery_activity_id=rid, recovery_case_id=recovery_case_id,
                  contract_id=case.get("contract_id", ""), customer_id=case.get("customer_id", ""),
                  event_type="recovery_expense_settled", activity_date=today,
                  settlement_method="paid_by_borrower", amount_usd=amount)
    ctx.create("recovery_activities", rid, **fields)
    remaining = round(max(float(case.get("expenses_outstanding_usd") or 0) - amount, 0.0), 2)
    ctx.update("recovery_cases", recovery_case_id, expenses_outstanding_usd=remaining)
    return (f"Redemption expense payment received: activity {rid} on case {recovery_case_id}, {amount:.2f} USD, "
            f"settlement paid_by_borrower dated {today}; recovery expenses outstanding now {remaining:.2f} USD.")


@tool(owner="agent", rw="write")
def post_surrender_fee_edb82254(ctx: ToolContext, recovery_case_id: str, amount_usd: float) -> str:
    """Charge the voluntary surrender fee to a repossession case whose vehicle the borrower gave up
    voluntarily. One call records one new expense of kind voluntary surrender fee on the case, dated
    today, and raises the case's posted recovery expenses outstanding by the same amount; the new
    expense then shows in the case activity and the higher outstanding figure shows on the case.

    Args:
        recovery_case_id: Id class — the reference number of the repossession case the fee is charged
            to, as returned by the repossession case lookup for this borrower's contract.
        amount_usd: Fixed-format class — the voluntary surrender fee being charged, in US dollars as a
            positive decimal number with exactly 2 decimal places, already rounded to the cent; the
            tool stores it rounded to 2 decimal places.

    Returns:
        A confirmation string naming the new case activity reference number (a text identifier that
        begins with "rsur_"), the case reference number, the fee charged in USD with 2 decimal places,
        the posting date in YYYY-MM-DD form and the case's new recovery expenses outstanding in USD
        with 2 decimal places. A string that begins with "Surrender fee posted" means the expense was
        recorded.
    """
    case = (ctx.find("recovery_cases", recovery_case_id=recovery_case_id) or [{}])[0]
    amount = round(float(amount_usd), 2)
    today = ctx.now()[:10]
    rid = ctx.make_id("rsur_", recovery_case_id, amount_usd)
    fields = dict(_ACTIVITY_DEFAULTS)
    fields.update(recovery_activity_id=rid, recovery_case_id=recovery_case_id,
                  contract_id=case.get("contract_id", ""), customer_id=case.get("customer_id", ""),
                  event_type="recovery_expense_posted", activity_date=today,
                  expense_type="voluntary_surrender_fee", amount_usd=amount)
    ctx.create("recovery_activities", rid, **fields)
    new_outstanding = round(float(case.get("expenses_outstanding_usd") or 0) + amount, 2)
    ctx.update("recovery_cases", recovery_case_id, expenses_outstanding_usd=new_outstanding)
    return (f"Surrender fee posted: activity {rid} on case {recovery_case_id}, {amount:.2f} USD dated "
            f"{today}; recovery expenses outstanding now {new_outstanding:.2f} USD.")


@tool(owner="user", rw="write")
def pay_reinstatement_recovery_expenses_82a1a2b9(ctx: ToolContext, recovery_case_id: str, amount_usd: float) -> str:
    """The borrower pays, from their own funds, the recovery
    expense portion of reinstating their contract and getting their repossessed vehicle back on a
    repossession case. One call records one settlement of the case's recovery expenses paid by the
    borrower, dated today, for the given amount, and lowers the case's posted recovery expenses
    outstanding by that amount, never below 0.00. The borrower then sees the payment in the case
    activity and the reduced outstanding figure on the case.

    Args:
        recovery_case_id: Id class — the reference number of the borrower's repossession case, as the
            agent reads it out from the repossession case lookup for the borrower's contract.
        amount_usd: Fixed-format class — the amount the borrower pays toward the case's recovery
            expenses, in US dollars as a positive decimal number with exactly 2 decimal places, already
            rounded to the cent; the tool stores it rounded to 2 decimal places.

    Returns:
        A confirmation string naming the new case activity reference number (a text identifier that
        begins with "rrxp_"), the case reference number, the amount paid in USD with 2 decimal places,
        the settlement method paid_by_borrower, the payment date in YYYY-MM-DD form and the case's
        remaining recovery expenses outstanding in USD with 2 decimal places. A string that begins with
        "Reinstatement expense payment received" means the payment was recorded.
    """
    case = (ctx.find("recovery_cases", recovery_case_id=recovery_case_id) or [{}])[0]
    amount = round(float(amount_usd), 2)
    today = ctx.now()[:10]
    rid = ctx.make_id("rrxp_", recovery_case_id, amount_usd)
    fields = dict(_ACTIVITY_DEFAULTS)
    fields.update(recovery_activity_id=rid, recovery_case_id=recovery_case_id,
                  contract_id=case.get("contract_id", ""), customer_id=case.get("customer_id", ""),
                  event_type="recovery_expense_settled", activity_date=today,
                  settlement_method="paid_by_borrower", amount_usd=amount)
    ctx.create("recovery_activities", rid, **fields)
    remaining = round(max(float(case.get("expenses_outstanding_usd") or 0) - amount, 0.0), 2)
    ctx.update("recovery_cases", recovery_case_id, expenses_outstanding_usd=remaining)
    return (f"Reinstatement expense payment received: activity {rid} on case {recovery_case_id}, {amount:.2f} USD, "
            f"settlement paid_by_borrower dated {today}; recovery expenses outstanding now {remaining:.2f} USD.")

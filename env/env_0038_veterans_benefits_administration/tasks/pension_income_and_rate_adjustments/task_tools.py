"""Hidden task tools for pension_income_and_rate_adjustments (Veterans Pension).

Each tool performs exactly one atomic write on the veteran's Veterans Pension records. None of them
checks eligibility, timing, ownership or any other business precondition, and none computes a
figure: every amount, date and reference passed in is decided by the caller from the published
rules and the records.
"""

from erlbench import ToolContext, tool


@tool(owner="user", rw="write")
def certify_benefit_income_d2f4edcf(ctx: ToolContext, pension_award_id: str, change_effective_date: str,
                                    annual_amount: float) -> str:
    """The veteran certifies, in his own name, the annual benefit income he receives (his own Social Security and
    the VA disability compensation counted for him) and files it on his Veterans Pension award as an income
    change report for the benefit-income source. One call adds one new income change report to the award,
    received today by telephone; nothing already on the award is changed. On success the veteran hears back the
    reference number of the filed statement and the amount he certified.

    Args:
        pension_award_id: Id class — the reference number of the veteran's Veterans Pension award, as shown by the
            pension award lookup for this veteran.
        change_effective_date: Fixed-format class — the date the benefit-income change began, written YYYY-MM-DD
            (calendar date, no time of day, no time zone).
        annual_amount: Fixed-format class — the certified annual benefit income, in USD, a decimal number with 2
            decimal places (cents), rounded half up to the cent; 0.00 is allowed when no benefit income remains.

    Returns:
        A confirmation sentence (str) of the form "Benefit income statement <report_id> filed on award
        <pension_award_id>: annual amount <annual_amount> USD, change effective <change_effective_date>, received
        <received_date> by phone." where report_id is the new statement's reference number, annual_amount is
        shown with 2 decimal places and received_date is today's date as YYYY-MM-DD. Receiving this sentence means
        the statement is on file.
    """
    amount = round(float(annual_amount), 2)
    rid = ctx.make_id("pir_", pension_award_id, change_effective_date, amount)
    award = ctx.find("pension_awards", pension_award_id=pension_award_id)
    customer_id = award[0].get("customer_id") if award else ""
    received = ctx.now()[:10]
    ctx.create("pension_income_reports", rid, report_id=rid, pension_award_id=pension_award_id,
               customer_id=customer_id, event_type="pension_income_change_reported", income_source="other",
               annual_amount=amount, change_effective_date=change_effective_date, received_date=received,
               expense_period_start="", expense_period_end="", medical_expense_amount=0.0, transfer_date="",
               transfer_amount=0.0, penalty_months=0, adjusted_annual_rate=0, source_report_id="",
               report_channel="phone", overpayment_created=False)
    return (f"Benefit income statement {rid} filed on award {pension_award_id}: annual amount {amount:.2f} USD, "
            f"change effective {change_effective_date}, received {received} by phone.")


@tool(owner="agent", rw="write")
def record_rate_adjustment_fee79930(ctx: ToolContext, pension_award_id: str, source_report_id: str,
                                    change_effective_date: str, adjusted_annual_rate: int,
                                    report_channel: str) -> str:
    """Record on a veteran's Veterans Pension award a rate adjustment that sets a new annual pension from a given
    effective date, made from a report already on the award. One call adds one rate adjustment entry naming the
    source report, the effective date, the new annual pension and the channel of the source report; the entry
    records no penalty months and no overpayment. Nothing else on the award changes. On success the new annual
    pension and its effective date can be read back with the adjustment's reference number.

    Args:
        pension_award_id: Id class — the reference number of the Veterans Pension award being adjusted, as shown by
            the pension award lookup for this veteran.
        source_report_id: Id class — the reference number of the report on the award that the adjustment rests on,
            as shown by the pension income report lookup.
        change_effective_date: Fixed-format class — the date the new annual pension takes effect, written
            YYYY-MM-DD (calendar date, no time of day, no time zone).
        adjusted_annual_rate: Fixed-format class — the new annual pension in USD, whole dollars, an integer with no
            cents; 0 is allowed.
        report_channel: Enum class — how the source report reached VA, copied from that report: phone when it was
            taken by telephone; online when it was submitted online; mail when it arrived by mail; va_initiated
            when VA itself produced it from a data match.

    Returns:
        A confirmation sentence (str) of the form "Rate adjustment <report_id> recorded on award
        <pension_award_id>: annual pension <adjusted_annual_rate> USD effective <change_effective_date>, source
        <source_report_id>." where report_id is the new adjustment's reference number. Receiving this sentence
        means the adjustment is on the award.
    """
    rate = int(adjusted_annual_rate)
    rid = ctx.make_id("pra_", pension_award_id, source_report_id, change_effective_date, rate, report_channel)
    award = ctx.find("pension_awards", pension_award_id=pension_award_id)
    customer_id = award[0].get("customer_id") if award else ""
    ctx.create("pension_income_reports", rid, report_id=rid, pension_award_id=pension_award_id,
               customer_id=customer_id, event_type="pension_rate_adjusted", income_source="not_applicable",
               annual_amount=0.0, change_effective_date=change_effective_date, received_date=ctx.now()[:10],
               expense_period_start="", expense_period_end="", medical_expense_amount=0.0, transfer_date="",
               transfer_amount=0.0, penalty_months=0, adjusted_annual_rate=rate,
               source_report_id=source_report_id, report_channel=report_channel, overpayment_created=False)
    return (f"Rate adjustment {rid} recorded on award {pension_award_id}: annual pension {rate} USD effective "
            f"{change_effective_date}, source {source_report_id}.")


@tool(owner="agent", rw="write")
def release_retro_payment_a1af7a43(ctx: ToolContext, pension_award_id: str, adjustment_id: str,
                                   retro_period_start: str, retro_period_end: str, gross_amount: float) -> str:
    """Release to the veteran one retroactive Veterans Pension payment covering a span of entitlement months under a
    rate adjustment. One call adds one retroactive payment entry to the award, issued today, delivered in full
    with nothing withheld (the net amount equals the gross amount). Nothing else on the award changes. On success
    the veteran can see the released amount and the months it covers.

    Args:
        pension_award_id: Id class — the reference number of the Veterans Pension award being paid, as shown by the
            pension award lookup for this veteran.
        adjustment_id: Id class — the reference number of the rate adjustment the release is made under, as shown
            by the pension income report lookup or returned when that adjustment was recorded.
        retro_period_start: Fixed-format class — the first entitlement month covered, written YYYY-MM.
        retro_period_end: Fixed-format class — the last entitlement month covered, written YYYY-MM.
        gross_amount: Fixed-format class — the amount released, in USD, a decimal number with 2 decimal places
            (cents), rounded half up to the cent.

    Returns:
        A confirmation sentence (str) of the form "Retroactive payment <pension_payment_id> released on award
        <pension_award_id>: <gross_amount> USD for <retro_period_start> to <retro_period_end>, issued
        <payment_date>." where pension_payment_id is the new payment's reference number, gross_amount is shown with
        2 decimal places and payment_date is today's date as YYYY-MM-DD. Receiving this sentence means the payment
        has been issued.
    """
    amount = round(float(gross_amount), 2)
    pid = ctx.make_id("ppy_", pension_award_id, adjustment_id, retro_period_start, retro_period_end, amount)
    award = ctx.find("pension_awards", pension_award_id=pension_award_id)
    customer_id = award[0].get("customer_id") if award else ""
    issued = ctx.now()[:10]
    ctx.create("pension_payments", pid, pension_payment_id=pid, pension_award_id=pension_award_id,
               customer_id=customer_id, event_type="pension_retro_payment", payment_month=retro_period_end,
               payment_date=issued, gross_amount=amount, offset_withheld_amount=0.0, net_amount=amount,
               offset_applied=False, source_payment_id="", adjustment_id=adjustment_id,
               retro_period_start=retro_period_start, retro_period_end=retro_period_end,
               return_reason="not_applicable")
    return (f"Retroactive payment {pid} released on award {pension_award_id}: {amount:.2f} USD for "
            f"{retro_period_start} to {retro_period_end}, issued {issued}.")


@tool(owner="user", rw="write")
def declare_lump_sum_cb649dee(ctx: ToolContext, pension_award_id: str, change_effective_date: str,
                              annual_amount: float) -> str:
    """The veteran declares, in his own name, the one-time VA payments deposited to him that count as income, and
    files the declaration on his Veterans Pension award as an income change report for one-time payments. One call
    adds one new income change report to the award, received today by telephone; nothing already on the award is
    changed. On success the veteran hears back the reference number of the filed declaration and the amount he
    declared.

    Args:
        pension_award_id: Id class — the reference number of the veteran's Veterans Pension award, as shown by the
            pension award lookup for this veteran.
        change_effective_date: Fixed-format class — the date the declared one-time payment was deposited, written
            YYYY-MM-DD (calendar date, no time of day, no time zone).
        annual_amount: Fixed-format class — the declared one-time amount that counts as income, in USD, a decimal
            number with 2 decimal places (cents), rounded half up to the cent; 0.00 is allowed.

    Returns:
        A confirmation sentence (str) of the form "One-time payment declaration <report_id> filed on award
        <pension_award_id>: amount <annual_amount> USD, deposited <change_effective_date>, received <received_date>
        by phone." where report_id is the new declaration's reference number, annual_amount is shown with 2 decimal
        places and received_date is today's date as YYYY-MM-DD. Receiving this sentence means the declaration is on
        file.
    """
    amount = round(float(annual_amount), 2)
    rid = ctx.make_id("pod_", pension_award_id, change_effective_date, amount)
    award = ctx.find("pension_awards", pension_award_id=pension_award_id)
    customer_id = award[0].get("customer_id") if award else ""
    received = ctx.now()[:10]
    ctx.create("pension_income_reports", rid, report_id=rid, pension_award_id=pension_award_id,
               customer_id=customer_id, event_type="pension_income_change_reported", income_source="other",
               annual_amount=amount, change_effective_date=change_effective_date, received_date=received,
               expense_period_start="", expense_period_end="", medical_expense_amount=0.0, transfer_date="",
               transfer_amount=0.0, penalty_months=0, adjusted_annual_rate=0, source_report_id="",
               report_channel="phone", overpayment_created=False)
    return (f"One-time payment declaration {rid} filed on award {pension_award_id}: amount {amount:.2f} USD, "
            f"deposited {change_effective_date}, received {received} by phone.")


@tool(owner="agent", rw="write")
def update_countable_income_81bdd26c(ctx: ToolContext, pension_award_id: str, annual_countable_income: float) -> str:
    """Set the recurring countable income recorded on a veteran's Veterans Pension award to a redetermined figure.
    One call replaces the award's countable income figure with the value given; no other figure, status or entry on
    the award changes and no payment is made. On success the new countable income can be read back on the award.

    Args:
        pension_award_id: Id class — the reference number of the Veterans Pension award, as shown by the pension
            award lookup for this veteran.
        annual_countable_income: Fixed-format class — the redetermined annual countable income, in USD, a decimal
            number with 2 decimal places (cents), rounded half up to the cent; 0.00 is allowed.

    Returns:
        A confirmation sentence (str) of the form "Countable income on award <pension_award_id> set to
        <annual_countable_income> USD." with the amount shown with 2 decimal places. Receiving this sentence means
        the award now carries that figure.
    """
    amount = round(float(annual_countable_income), 2)
    ctx.update("pension_awards", pension_award_id, annual_countable_income=amount)
    return f"Countable income on award {pension_award_id} set to {amount:.2f} USD."


@tool(owner="agent", rw="write")
def update_net_worth_02de4f94(ctx: ToolContext, pension_award_id: str, net_worth: float) -> str:
    """Set the net worth recorded on a veteran's Veterans Pension award to a redetermined figure. One call replaces
    the award's net worth figure with the value given; no other figure, status or entry on the award changes and no
    payment is made. On success the new net worth can be read back on the award.

    Args:
        pension_award_id: Id class — the reference number of the Veterans Pension award, as shown by the pension
            award lookup for this veteran.
        net_worth: Fixed-format class — the redetermined net worth, in USD, a decimal number with 2 decimal places
            (cents), rounded half up to the cent.

    Returns:
        A confirmation sentence (str) of the form "Net worth on award <pension_award_id> set to <net_worth> USD."
        with the amount shown with 2 decimal places. Receiving this sentence means the award now carries that
        figure.
    """
    amount = round(float(net_worth), 2)
    ctx.update("pension_awards", pension_award_id, net_worth=amount)
    return f"Net worth on award {pension_award_id} set to {amount:.2f} USD."


@tool(owner="agent", rw="write")
def record_annual_rate_redetermination_a1a40d3e(ctx: ToolContext, pension_award_id: str, source_report_id: str,
                                                change_effective_date: str, adjusted_annual_rate: int,
                                                report_channel: str) -> str:
    """Record on a veteran's Veterans Pension award the redetermination of the annual pension going forward, made
    from a declaration or report already on the award. One call adds one rate adjustment entry naming the source
    report, the date the redetermined pension takes effect, the redetermined annual pension and the channel of the
    source report; the entry records no penalty months and no overpayment. Nothing else on the award changes. On
    success the redetermined pension and its effective date can be read back with the entry's reference number.

    Args:
        pension_award_id: Id class — the reference number of the Veterans Pension award, as shown by the pension
            award lookup for this veteran.
        source_report_id: Id class — the reference number of the declaration or report on the award the
            redetermination rests on, as shown by the pension income report lookup or returned when it was filed.
        change_effective_date: Fixed-format class — the date the redetermined annual pension takes effect, written
            YYYY-MM-DD (calendar date, no time of day, no time zone).
        adjusted_annual_rate: Fixed-format class — the redetermined annual pension in USD, whole dollars, an integer
            with no cents; 0 is allowed.
        report_channel: Enum class — how the source report reached VA, copied from that report: phone when it was
            taken or filed by telephone; online when it was submitted online; mail when it arrived by mail;
            va_initiated when VA itself produced it from a data match.

    Returns:
        A confirmation sentence (str) of the form "Annual rate redetermination <report_id> recorded on award
        <pension_award_id>: annual pension <adjusted_annual_rate> USD effective <change_effective_date>, source
        <source_report_id>." where report_id is the new entry's reference number. Receiving this sentence means the
        redetermination is on the award.
    """
    rate = int(adjusted_annual_rate)
    rid = ctx.make_id("prd_", pension_award_id, source_report_id, change_effective_date, rate, report_channel)
    award = ctx.find("pension_awards", pension_award_id=pension_award_id)
    customer_id = award[0].get("customer_id") if award else ""
    ctx.create("pension_income_reports", rid, report_id=rid, pension_award_id=pension_award_id,
               customer_id=customer_id, event_type="pension_rate_adjusted", income_source="not_applicable",
               annual_amount=0.0, change_effective_date=change_effective_date, received_date=ctx.now()[:10],
               expense_period_start="", expense_period_end="", medical_expense_amount=0.0, transfer_date="",
               transfer_amount=0.0, penalty_months=0, adjusted_annual_rate=rate,
               source_report_id=source_report_id, report_channel=report_channel, overpayment_created=False)
    return (f"Annual rate redetermination {rid} recorded on award {pension_award_id}: annual pension {rate} USD "
            f"effective {change_effective_date}, source {source_report_id}.")

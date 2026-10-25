"""Hidden task tools for the extended_day_care_billing difficulty (Creek Kids Club Extended Day).

Each tool performs one atomic write on one Creek Kids Club enrollment and is reached only through
the unlock/call meta-tools, by the name an extended policy gives as its target_tool.
"""

from decimal import Decimal, ROUND_HALF_UP

from erlbench import ToolContext, tool


class _Money:
    """Exact money handling shared by the tools of this file."""

    @staticmethod
    def cents(value) -> float:
        """Round a dollar amount to the cent, half a cent rounding up, using exact decimals."""
        return float(Decimal(str(value)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP))

    @staticmethod
    def is_cent_exact(value) -> bool:
        """True when the amount carries no digits beyond the cent."""
        d = Decimal(str(value))
        return d == d.quantize(Decimal("0.01"))

    @staticmethod
    def reference(row_id: str) -> str:
        """A ten-digit confirmation number derived from a row id, always beginning with 71."""
        digits = "".join(str(int(ch, 16) % 10) for ch in row_id[-8:])
        return "71" + digits

    @staticmethod
    def enrollment(ctx: ToolContext, care_enrollment_id: str):
        """The enrollment row for a reference number, or None when there is none."""
        rows = ctx.find("care_enrollments", care_enrollment_id=care_enrollment_id)
        return rows[0] if rows else None


@tool(owner="agent", rw="write")
def post_late_pickup_fee_6e670263(ctx: ToolContext, care_enrollment_id: str, service_date: str,
                                  fee_amount: float) -> str:
    """Post the late pickup fee for one late pickup recorded as chargeable on a Creek Kids Club Extended
    Day enrollment. One call books one late pickup fee entry on the enrollment's billing history for the
    given day of care, dated today; the enrollment's balance due goes up by the fee and the fee then
    shows in the billing history next to that day of care.

    Args:
        care_enrollment_id: Id class — the Extended Day enrollment reference number of the student who
            was picked up late, as returned by the Extended Day enrollment lookup.
        service_date: Fixed-format class — the day of care of the late pickup, YYYY-MM-DD, exactly as
            shown on the late pickup entry in the enrollment's attendance log lookup.
        fee_amount: Fixed-format class — the fee in US dollars, a positive amount with at most 2
            decimal places (already rounded to the cent, half a cent rounding up); zero or negative
            amounts are not accepted.

    Returns:
        A confirmation sentence naming the new fee entry's reference number (text, prefix clp_), the
        enrollment reference number, the day of care (YYYY-MM-DD), the fee in dollars with two decimals
        and the posting date (YYYY-MM-DD); its presence means the fee is booked. A sentence beginning
        with "Error:" means nothing was booked.
    """
    if not (float(fee_amount) > 0 and _Money.is_cent_exact(fee_amount)):
        return "Error: fee_amount must be a positive dollar amount with at most two decimal places."
    if not (len(service_date) == 10 and service_date[4] == "-" and service_date[7] == "-"):
        return "Error: service_date must be written YYYY-MM-DD."
    enr = _Money.enrollment(ctx, care_enrollment_id)
    if enr is None:
        return f"Error: no Extended Day enrollment {care_enrollment_id}."
    amount = _Money.cents(fee_amount)
    rid = ctx.make_id("clp_", care_enrollment_id, service_date, amount)
    day = ctx.now()[:10]
    ctx.create("care_ledger", rid, care_ledger_id=rid, care_enrollment_id=care_enrollment_id,
               customer_id=enr.get("customer_id"), event_type="care_late_pickup_fee", amount=amount,
               posted_date=day, school_year="", billing_month="", service_date=service_date,
               day_type="not_applicable", rate_basis="not_applicable", sibling_position=1,
               proration="not_applicable", payment_method="not_applicable", payment_reference="",
               credit_reason="not_applicable", source_care_ledger_id="", subsidy_payer="not_applicable")
    return (f"Late pickup fee {rid} of ${amount:.2f} for {service_date} posted on {day} to enrollment "
            f"{care_enrollment_id}.")


@tool(owner="user", rw="write")
def pay_extended_day_settlement_f9b88247(ctx: ToolContext, care_enrollment_id: str, payment_amount: float,
                                        payment_method: str) -> str:
    """The family pays, in person through the district's online payment portal or at the campus cashier,
    the amount the support desk quotes for one current-year Creek Kids Club Extended Day enrollment, such
    as the first payment of a payment plan. One call books one family payment on that enrollment's billing
    history, dated today, and issues a confirmation number; the enrollment's balance due goes down by the
    amount paid.

    Args:
        care_enrollment_id: Id class — the Extended Day enrollment reference number the payment is for, as
            read out by the support desk from the Extended Day enrollment lookup.
        payment_amount: Fixed-format class — the amount paid in US dollars, a positive amount with at most
            2 decimal places (already rounded to the cent, half a cent rounding up); zero or negative
            amounts are not accepted.
        payment_method: Enum class — how the family pays: online_card when paying by debit or credit card
            through the online payment portal; ach_bank_draft when paying by bank draft through the
            online payment portal; personal_check when paying by personal check at the campus cashier;
            money_order when paying by money order at the campus cashier; not_applicable is never a
            family payment method and a call carrying it is refused.

    Returns:
        A confirmation sentence naming the payment's confirmation number (ten digits), the payment entry
        reference number (text, prefix cpy_), the enrollment reference number, the amount paid in dollars
        with two decimals, the method and the posting date (YYYY-MM-DD); its presence means the payment
        is booked. A sentence beginning with "Error:" means nothing was booked.
    """
    methods = {"online_card", "ach_bank_draft", "personal_check", "money_order"}
    if payment_method not in methods:
        return "Error: payment_method must be one of online_card, ach_bank_draft, personal_check, money_order."
    if not (float(payment_amount) > 0 and _Money.is_cent_exact(payment_amount)):
        return "Error: payment_amount must be a positive dollar amount with at most two decimal places."
    enr = _Money.enrollment(ctx, care_enrollment_id)
    if enr is None:
        return f"Error: no Extended Day enrollment {care_enrollment_id}."
    amount = _Money.cents(payment_amount)
    rid = ctx.make_id("cpy_", care_enrollment_id, amount, payment_method)
    ref = _Money.reference(rid)
    day = ctx.now()[:10]
    ctx.create("care_ledger", rid, care_ledger_id=rid, care_enrollment_id=care_enrollment_id,
               customer_id=enr.get("customer_id"), event_type="care_payment", amount=amount, posted_date=day,
               school_year="", billing_month="", service_date="", day_type="not_applicable",
               rate_basis="not_applicable", sibling_position=1, proration="not_applicable",
               payment_method=payment_method, payment_reference=ref, credit_reason="not_applicable",
               source_care_ledger_id="", subsidy_payer="not_applicable")
    return (f"Payment confirmation {ref}: ${amount:.2f} by {payment_method} posted on {day} to enrollment "
            f"{care_enrollment_id} (entry {rid}).")


@tool(owner="agent", rw="write")
def post_notice_period_credit_667047da(ctx: ToolContext, care_enrollment_id: str, source_care_ledger_id: str,
                                      credit_amount: float) -> str:
    """Post a notice-period adjustment credit on a withdrawn Creek Kids Club Extended Day enrollment for the
    part of the final billed month's tuition that the withdrawal notice period does not reach. One call
    books one credit entry on the enrollment's billing history, linked to the tuition charge it reduces,
    dated today, with credit reason notice_period_adjustment; the enrollment's balance due goes down by the
    credit amount and the credit then shows in the billing history.

    Args:
        care_enrollment_id: Id class — the Extended Day enrollment reference number of the withdrawn
            enrollment, as returned by the Extended Day enrollment lookup.
        source_care_ledger_id: Id class — the reference number of the final month's tuition charge being
            reduced, as shown on that charge in the enrollment's Extended Day billing history lookup.
        credit_amount: Fixed-format class — the credit in US dollars, a positive amount with at most 2
            decimal places (already rounded to the cent, half a cent rounding up); zero or negative amounts
            are not accepted.

    Returns:
        A confirmation sentence naming the new credit entry's reference number (text, prefix cnp_), the
        enrollment reference number, the reduced charge's reference number, the credited amount in dollars
        with two decimals and the posting date (YYYY-MM-DD); its presence means the credit is booked. A
        sentence beginning with "Error:" means nothing was booked.
    """
    if not (float(credit_amount) > 0 and _Money.is_cent_exact(credit_amount)):
        return "Error: credit_amount must be a positive dollar amount with at most two decimal places."
    enr = _Money.enrollment(ctx, care_enrollment_id)
    if enr is None:
        return f"Error: no Extended Day enrollment {care_enrollment_id}."
    amount = _Money.cents(credit_amount)
    rid = ctx.make_id("cnp_", care_enrollment_id, source_care_ledger_id, amount)
    day = ctx.now()[:10]
    ctx.create("care_ledger", rid, care_ledger_id=rid, care_enrollment_id=care_enrollment_id,
               customer_id=enr.get("customer_id"), event_type="care_credit", amount=amount, posted_date=day,
               school_year="", billing_month="", service_date="", day_type="not_applicable",
               rate_basis="not_applicable", sibling_position=1, proration="not_applicable",
               payment_method="not_applicable", payment_reference="", credit_reason="notice_period_adjustment",
               source_care_ledger_id=source_care_ledger_id, subsidy_payer="not_applicable")
    return (f"Notice-period adjustment credit {rid} of ${amount:.2f} posted on {day} to enrollment "
            f"{care_enrollment_id} against charge {source_care_ledger_id}.")


@tool(owner="user", rw="write")
def pay_prior_year_installment_d4311e53(ctx: ToolContext, care_enrollment_id: str, payment_amount: float,
                                       payment_method: str) -> str:
    """The family pays, in person through the district's online payment portal or at the campus cashier,
    the first installment quoted for the balance of an earlier school year's Creek Kids Club Extended Day
    enrollment. One call books one family payment on that earlier-year enrollment's billing history, dated
    today, and issues a confirmation number; that enrollment's balance due goes down by the amount paid.

    Args:
        care_enrollment_id: Id class — the reference number of the earlier-year Extended Day enrollment the
            installment is for, as read out by the support desk from the Extended Day enrollment lookup.
        payment_amount: Fixed-format class — the amount paid in US dollars, a positive amount with at most 2
            decimal places (already rounded to the cent, half a cent rounding up); zero or negative amounts
            are not accepted.
        payment_method: Enum class — how the family pays: online_card when paying by debit or credit card
            through the online payment portal; ach_bank_draft when paying by bank draft through the online
            payment portal; personal_check when paying by personal check at the campus cashier; money_order
            when paying by money order at the campus cashier; not_applicable is never a family payment
            method and a call carrying it is refused.

    Returns:
        A confirmation sentence naming the payment's confirmation number (ten digits), the payment entry
        reference number (text, prefix cpi_), the enrollment reference number, the amount paid in dollars
        with two decimals, the method and the posting date (YYYY-MM-DD); its presence means the payment is
        booked. A sentence beginning with "Error:" means nothing was booked.
    """
    methods = {"online_card", "ach_bank_draft", "personal_check", "money_order"}
    if payment_method not in methods:
        return "Error: payment_method must be one of online_card, ach_bank_draft, personal_check, money_order."
    if not (float(payment_amount) > 0 and _Money.is_cent_exact(payment_amount)):
        return "Error: payment_amount must be a positive dollar amount with at most two decimal places."
    enr = _Money.enrollment(ctx, care_enrollment_id)
    if enr is None:
        return f"Error: no Extended Day enrollment {care_enrollment_id}."
    amount = _Money.cents(payment_amount)
    rid = ctx.make_id("cpi_", care_enrollment_id, amount, payment_method)
    ref = _Money.reference(rid)
    day = ctx.now()[:10]
    ctx.create("care_ledger", rid, care_ledger_id=rid, care_enrollment_id=care_enrollment_id,
               customer_id=enr.get("customer_id"), event_type="care_payment", amount=amount, posted_date=day,
               school_year="", billing_month="", service_date="", day_type="not_applicable",
               rate_basis="not_applicable", sibling_position=1, proration="not_applicable",
               payment_method=payment_method, payment_reference=ref, credit_reason="not_applicable",
               source_care_ledger_id="", subsidy_payer="not_applicable")
    return (f"Payment confirmation {ref}: ${amount:.2f} by {payment_method} posted on {day} to enrollment "
            f"{care_enrollment_id} (entry {rid}).")


@tool(owner="agent", rw="write")
def post_late_payment_fee_d20db65b(ctx: ToolContext, care_enrollment_id: str, billing_month: str,
                                   fee_amount: float) -> str:
    """Post the late payment fee for one billing month of a Creek Kids Club Extended Day enrollment whose
    tuition was not paid in full by its due day. One call books one late payment fee entry on the
    enrollment's billing history for that billing month, dated today; the enrollment's balance due goes up
    by the fee and the fee then shows in the billing history next to that month.

    Args:
        care_enrollment_id: Id class — the Extended Day enrollment reference number whose month was paid
            late, as returned by the Extended Day enrollment lookup.
        billing_month: Fixed-format class — the billing month the fee is for, YYYY-MM, exactly as shown on
            that month's tuition charge in the enrollment's billing history lookup.
        fee_amount: Fixed-format class — the fee in US dollars, a positive amount with at most 2 decimal
            places (already rounded to the cent, half a cent rounding up); zero or negative amounts are not
            accepted.

    Returns:
        A confirmation sentence naming the new fee entry's reference number (text, prefix clf_), the
        enrollment reference number, the billing month (YYYY-MM), the fee in dollars with two decimals and
        the posting date (YYYY-MM-DD); its presence means the fee is booked. A sentence beginning with
        "Error:" means nothing was booked.
    """
    if not (float(fee_amount) > 0 and _Money.is_cent_exact(fee_amount)):
        return "Error: fee_amount must be a positive dollar amount with at most two decimal places."
    if not (len(billing_month) == 7 and billing_month[4] == "-"):
        return "Error: billing_month must be written YYYY-MM."
    enr = _Money.enrollment(ctx, care_enrollment_id)
    if enr is None:
        return f"Error: no Extended Day enrollment {care_enrollment_id}."
    amount = _Money.cents(fee_amount)
    rid = ctx.make_id("clf_", care_enrollment_id, billing_month, amount)
    day = ctx.now()[:10]
    ctx.create("care_ledger", rid, care_ledger_id=rid, care_enrollment_id=care_enrollment_id,
               customer_id=enr.get("customer_id"), event_type="care_late_payment_fee", amount=amount,
               posted_date=day, school_year="", billing_month=billing_month, service_date="",
               day_type="not_applicable", rate_basis="not_applicable", sibling_position=1,
               proration="not_applicable", payment_method="not_applicable", payment_reference="",
               credit_reason="not_applicable", source_care_ledger_id="", subsidy_payer="not_applicable")
    return (f"Late payment fee {rid} of ${amount:.2f} for billing month {billing_month} posted on {day} to "
            f"enrollment {care_enrollment_id}.")


@tool(owner="agent", rw="write")
def post_booked_day_fee_4f9449e5(ctx: ToolContext, care_enrollment_id: str, service_date: str, day_type: str,
                                 fee_amount: float) -> str:
    """Post the fee for one day booked on a Creek Kids Club Extended Day enrollment through a drop-in booking
    request. One call books one day fee entry on the enrollment's billing history for the booked day of
    care and its day type, dated today; the enrollment's balance due goes up by the fee and the booked day
    then shows in the billing history.

    Args:
        care_enrollment_id: Id class — the Extended Day enrollment reference number the day is booked on, as
            returned by the Extended Day enrollment lookup.
        service_date: Fixed-format class — the booked day of care, YYYY-MM-DD, exactly as the requested date
            shown on the drop-in booking request in the enrollment's request lookup.
        day_type: Enum class — how the day is booked: drop_in_day when it is booked as a drop-in day of care
            outside the plan's schedule; holiday_camp_day when it is booked as a district holiday camp day;
            early_release_day when it is booked as an early-release afternoon; not_applicable is never a
            booked day and a call carrying it is refused.
        fee_amount: Fixed-format class — the fee in US dollars, a positive amount with at most 2 decimal
            places (already rounded to the cent, half a cent rounding up); zero or negative amounts are not
            accepted.

    Returns:
        A confirmation sentence naming the new day fee entry's reference number (text, prefix cdf_), the
        enrollment reference number, the booked day (YYYY-MM-DD), the day type, the fee in dollars with two
        decimals and the posting date (YYYY-MM-DD); its presence means the day is booked and charged. A
        sentence beginning with "Error:" means nothing was booked.
    """
    if day_type not in {"drop_in_day", "holiday_camp_day", "early_release_day"}:
        return "Error: day_type must be one of drop_in_day, holiday_camp_day, early_release_day."
    if not (float(fee_amount) > 0 and _Money.is_cent_exact(fee_amount)):
        return "Error: fee_amount must be a positive dollar amount with at most two decimal places."
    if not (len(service_date) == 10 and service_date[4] == "-" and service_date[7] == "-"):
        return "Error: service_date must be written YYYY-MM-DD."
    enr = _Money.enrollment(ctx, care_enrollment_id)
    if enr is None:
        return f"Error: no Extended Day enrollment {care_enrollment_id}."
    amount = _Money.cents(fee_amount)
    rid = ctx.make_id("cdf_", care_enrollment_id, service_date, day_type, amount)
    day = ctx.now()[:10]
    ctx.create("care_ledger", rid, care_ledger_id=rid, care_enrollment_id=care_enrollment_id,
               customer_id=enr.get("customer_id"), event_type="care_day_fee", amount=amount, posted_date=day,
               school_year="", billing_month="", service_date=service_date, day_type=day_type,
               rate_basis="not_applicable", sibling_position=1, proration="not_applicable",
               payment_method="not_applicable", payment_reference="", credit_reason="not_applicable",
               source_care_ledger_id="", subsidy_payer="not_applicable")
    return (f"Booked day fee {rid} of ${amount:.2f} for {service_date} ({day_type}) posted on {day} to "
            f"enrollment {care_enrollment_id}.")

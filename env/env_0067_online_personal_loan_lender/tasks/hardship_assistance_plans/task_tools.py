"""Hidden task tools for the hardship_assistance_plans difficulty (Larkspur Lending, category `hardship`).

Each tool performs one atomic write on a hardship assistance plan and is reached only through the
unlock/call meta-tools; its name is published only as an extended policy's target_tool.
"""

from erlbench import ToolContext, tool


@tool(owner="agent", rw="write")
def offer_reduced_payment_plan_00434f76(ctx: ToolContext, hardship_plan_id: str, loan_id: str,
                                        pre_plan_payment_amount: float, pre_plan_interest_rate: float,
                                        balance_at_request: float, remaining_months_at_request: int,
                                        start_date: str, end_date: str, plan_payment_amount: float) -> str:
    """Decide a pending Reduced Payment Plan request by setting its terms and presenting them to the borrower.

    The request moves from requested to offered and today becomes its decision date. The offer records the
    loan's figures on the decision date (its scheduled installment, its interest rate and its unpaid
    principal, plus the number of loan due dates left through maturity), the earliest and latest loan due
    dates the plan covers, the program's three plan months and the monthly plan installment the borrower would pay;
    the plan sets no plan rate, defers no installment, adds no term and carries no settlement amount. The
    borrower sees an offer awaiting acceptance with these terms. Nothing changes on the loan itself.

    Args:
        hardship_plan_id: Id class — the reference number of the borrower's pending Reduced Payment Plan
            request, read from the hardship plan lookup.
        loan_id: Id class — the reference number of the personal loan the request concerns, read from the
            loan lookup or from the request's own loan reference.
        pre_plan_payment_amount: Fixed-format class — the loan's scheduled monthly installment on the
            decision date, in USD, 2 decimal places, rounded half up to the cent.
        pre_plan_interest_rate: Fixed-format class — the loan's current interest rate on the decision date,
            as an annual percentage rate written in percent units, 2 decimal places, rounded half up.
        balance_at_request: Fixed-format class — the loan's unpaid principal on the decision date, in USD,
            2 decimal places, rounded half up to the cent.
        remaining_months_at_request: Fixed-format class — the count of loan due dates from the loan's next due
            date through its maturity date, as an integer number of months.
        start_date: Fixed-format class — the earliest loan due date the plan covers, as a calendar date in the
            format YYYY-MM-DD.
        end_date: Fixed-format class — the latest loan due date the plan covers, as a calendar date in the
            format YYYY-MM-DD.
        plan_payment_amount: Fixed-format class — the monthly plan installment offered, in USD, 2 decimal
            places, rounded half up to the cent.

    Returns:
        A confirmation sentence (string) naming the hardship plan reference number, the status offered, the
        decision date in YYYY-MM-DD format, the plan installment in USD with 2 decimal places and the earliest
        and latest covered due dates; receiving it means the offer now stands on the request.
    """
    pre_rate = round(float(pre_plan_interest_rate), 2)
    ctx.update("hardship_plans", hardship_plan_id, loan_id=loan_id, status="offered",
               decision_date=ctx.now()[:10],
               pre_plan_payment_amount=round(float(pre_plan_payment_amount), 2),
               pre_plan_interest_rate=pre_rate,
               balance_at_request=round(float(balance_at_request), 2),
               remaining_months_at_request=int(remaining_months_at_request),
               start_date=start_date, end_date=end_date, plan_months=3,
               plan_payment_amount=round(float(plan_payment_amount), 2),
               plan_interest_rate="", deferred_installment_count=0, term_extension_months=0,
               settlement_amount=0.0)
    return (f"Reduced Payment Plan {hardship_plan_id} is now offered (decision date {ctx.now()[:10]}): "
            f"plan installment {round(float(plan_payment_amount), 2):.2f} USD from {start_date} "
            f"through {end_date}.")


@tool(owner="user", rw="write")
def record_settlement_installments_ebffb995(ctx: ToolContext, hardship_plan_id: str, plan_months: int) -> str:
    """Let the borrower record, on their own pending Charged-Off Settlement Plan request, how many monthly
    installments they choose to settle in.

    The borrower's choice is stored on the request as its plan months: 1 means a single settlement payment,
    and a larger number means that many monthly installments. The request stays in requested status; no
    payment is taken and nothing changes on the loan. A successful call leaves the request showing the
    recorded number of installments.

    Args:
        hardship_plan_id: Id class — the reference number of the borrower's pending Charged-Off Settlement Plan
            request, as given to the borrower by the representative from the hardship plan lookup.
        plan_months: Fixed-format class — the number of monthly settlement installments the borrower chooses,
            as an integer number of months (1 for a single payment).

    Returns:
        A confirmation sentence (string) naming the hardship plan reference number and the number of monthly
        installments now recorded on the request; receiving it means the choice is saved.
    """
    ctx.update("hardship_plans", hardship_plan_id, plan_months=int(plan_months))
    return (f"Settlement request {hardship_plan_id} now records {int(plan_months)} monthly "
            f"installment(s) chosen by the borrower.")


@tool(owner="agent", rw="write")
def offer_charged_off_settlement_3f4a16ef(ctx: ToolContext, hardship_plan_id: str, loan_id: str,
                                          balance_at_request: float, plan_payment_amount: float,
                                          settlement_amount: float) -> str:
    """Decide a pending Charged-Off Settlement Plan request by setting the settlement terms and presenting
    them to the borrower.

    The request moves from requested to offered and today becomes its decision date. The offer records the
    charged-off balance the settlement is measured on, the total settlement amount and the settlement
    installment payable each month; the request's number of installments is not changed by this call. The borrower sees a settlement offer awaiting
    acceptance. Nothing is paid and nothing changes on the loan itself.

    Args:
        hardship_plan_id: Id class — the reference number of the borrower's pending Charged-Off Settlement Plan
            request, read from the hardship plan lookup.
        loan_id: Id class — the reference number of the charged-off personal loan the request concerns, read
            from the loan lookup or from the request's own loan reference.
        balance_at_request: Fixed-format class — the charged-off balance on the decision date (unpaid principal
            plus unpaid fees), in USD, 2 decimal places, rounded half up to the cent.
        plan_payment_amount: Fixed-format class — the settlement installment due each month (the whole
            settlement for a single payment), in USD, 2 decimal places, rounded half up to the cent.
        settlement_amount: Fixed-format class — the total amount accepted to settle the charged-off balance, in
            USD, 2 decimal places, rounded half up to the cent.

    Returns:
        A confirmation sentence (string) naming the hardship plan reference number, the status offered, the
        decision date in YYYY-MM-DD format, the settlement amount and the settlement installment in USD with
        2 decimal places; receiving it means the settlement offer now stands on the request.
    """
    ctx.update("hardship_plans", hardship_plan_id, loan_id=loan_id, status="offered",
               decision_date=ctx.now()[:10],
               balance_at_request=round(float(balance_at_request), 2),
               plan_payment_amount=round(float(plan_payment_amount), 2),
               settlement_amount=round(float(settlement_amount), 2),
               deferred_installment_count=0, term_extension_months=0)
    return (f"Charged-Off Settlement Plan {hardship_plan_id} is now offered (decision date {ctx.now()[:10]}): "
            f"settlement {round(float(settlement_amount), 2):.2f} USD, installment "
            f"{round(float(plan_payment_amount), 2):.2f} USD.")


@tool(owner="user", rw="write")
def report_military_service_end_1d04825e(ctx: ToolContext, hardship_plan_id: str, end_date: str,
                                         plan_months: int) -> str:
    """Let the servicemember personally certify the end of their military service on their own active
    Servicemember Rate Cap Benefit, recording the benefit's end date and the number of loan due dates the
    benefit covers.

    The benefit records the given date as its end date and the given number of loan due dates as its plan
    months. The benefit stays active; no payment is taken and nothing changes on the loan itself. A
    successful call leaves the benefit showing the recorded end date and plan months.

    Args:
        hardship_plan_id: Id class — the reference number of the servicemember's Servicemember Rate Cap Benefit,
            as given to the servicemember by the representative from the hardship plan lookup.
        end_date: Fixed-format class — the benefit's end date: the last loan due date the benefit applies
            to, or the end of military service for a benefit that covers no loan due date, as a calendar date
            in the format YYYY-MM-DD.
        plan_months: Fixed-format class — the number of loan due dates the benefit covers, as an integer
            number of months (0 when it covers none).

    Returns:
        A confirmation sentence (string) naming the benefit reference number, the recorded end date in
        YYYY-MM-DD format and the plan months now recorded; receiving it means the certification is saved.
    """
    ctx.update("hardship_plans", hardship_plan_id, end_date=end_date, plan_months=int(plan_months))
    return (f"Servicemember benefit {hardship_plan_id} now records end date {end_date} "
            f"and {int(plan_months)} covered loan due date(s).")


@tool(owner="agent", rw="write")
def schedule_benefit_plan_installment_71e01653(ctx: ToolContext, hardship_plan_id: str, customer_id: str,
                                               loan_id: str, installment_due_date: str, amount: float) -> str:
    """Schedule one plan installment line on an active hardship benefit for one loan due date.

    A new plan installment line is recorded on the benefit, dated today, for the given loan due date and
    amount; it adds that amount to the plan amount due on the benefit. Nothing is debited and nothing
    changes on the loan itself. A successful call leaves the benefit's history showing the new line.

    Args:
        hardship_plan_id: Id class — the reference number of the active hardship benefit, read from the
            hardship plan lookup.
        customer_id: Id class — the customer reference number of the borrower, read from the customer profile
            lookup.
        loan_id: Id class — the reference number of the personal loan the benefit applies to, read from the
            loan lookup or from the benefit's own loan reference.
        installment_due_date: Fixed-format class — the loan due date the plan installment falls due on, as a
            calendar date in the format YYYY-MM-DD.
        amount: Fixed-format class — the plan installment due on that date, in USD, 2 decimal places, rounded
            half up to the cent.

    Returns:
        A confirmation sentence (string) naming the new line's reference number, the benefit reference number,
        the due date in YYYY-MM-DD format and the amount in USD with 2 decimal places; receiving it means the
        line is recorded.
    """
    eid = ctx.make_id("hpe_", hardship_plan_id, customer_id, loan_id, installment_due_date, amount)
    ctx.create("hardship_plan_events", eid, hardship_event_id=eid, hardship_plan_id=hardship_plan_id,
               customer_id=customer_id, loan_id=loan_id, event_type="hardship_plan_installment_scheduled",
               event_date=ctx.now()[:10], document_type="", installment_due_date=installment_due_date,
               amount=round(float(amount), 2), loan_txn_id=None)
    return (f"Plan installment line {eid} recorded on benefit {hardship_plan_id}: "
            f"{round(float(amount), 2):.2f} USD due {installment_due_date}.")


@tool(owner="agent", rw="write")
def offer_rate_reduction_plan_52a2ad4e(ctx: ToolContext, hardship_plan_id: str, loan_id: str,
                                       pre_plan_payment_amount: float, pre_plan_interest_rate: float,
                                       balance_at_request: float, remaining_months_at_request: int,
                                       start_date: str, end_date: str, plan_interest_rate: float,
                                       plan_payment_amount: float) -> str:
    """Decide a pending Temporary Rate Reduction Plan request by setting its terms and presenting them to the
    borrower.

    The request moves from requested to offered and today becomes its decision date. The offer records the
    loan's figures on the decision date (its scheduled installment, its interest rate and its unpaid
    principal, plus the number of loan due dates left through maturity), the earliest and latest loan due
    dates the plan covers, the program's six plan months, the plan interest rate and the monthly plan
    installment; it defers no installment, adds no term and carries no settlement amount. The borrower sees an
    offer awaiting acceptance with these terms. Nothing changes on the loan itself.

    Args:
        hardship_plan_id: Id class — the reference number of the borrower's pending Temporary Rate Reduction
            Plan request, read from the hardship plan lookup.
        loan_id: Id class — the reference number of the personal loan the request concerns, read from the
            loan lookup or from the request's own loan reference.
        pre_plan_payment_amount: Fixed-format class — the loan's scheduled monthly installment on the
            decision date, in USD, 2 decimal places, rounded half up to the cent.
        pre_plan_interest_rate: Fixed-format class — the loan's current interest rate on the decision date,
            as an annual percentage rate written in percent units, 2 decimal places, rounded half up.
        balance_at_request: Fixed-format class — the loan's unpaid principal on the decision date, in USD,
            2 decimal places, rounded half up to the cent.
        remaining_months_at_request: Fixed-format class — the count of loan due dates from the loan's next due
            date through its maturity date, as an integer number of months.
        start_date: Fixed-format class — the earliest loan due date the plan covers, as a calendar date in the
            format YYYY-MM-DD.
        end_date: Fixed-format class — the latest loan due date the plan covers, as a calendar date in the
            format YYYY-MM-DD.
        plan_interest_rate: Fixed-format class — the interest rate set for the plan months, as an annual rate
            in percent units, 2 decimal places, rounded half up.
        plan_payment_amount: Fixed-format class — the monthly plan installment offered, in USD, 2 decimal
            places, rounded half up to the cent.

    Returns:
        A confirmation sentence (string) naming the hardship plan reference number, the status offered, the
        decision date in YYYY-MM-DD format, the plan rate in percent, the plan installment in USD with 2
        decimal places and the earliest and latest covered due dates; receiving it means the offer now stands
        on the request.
    """
    pre_rate = round(float(pre_plan_interest_rate), 2)
    plan_rate = round(float(plan_interest_rate), 2)
    ctx.update("hardship_plans", hardship_plan_id, loan_id=loan_id, status="offered",
               decision_date=ctx.now()[:10],
               pre_plan_payment_amount=round(float(pre_plan_payment_amount), 2),
               pre_plan_interest_rate=pre_rate,
               balance_at_request=round(float(balance_at_request), 2),
               remaining_months_at_request=int(remaining_months_at_request),
               start_date=start_date, end_date=end_date, plan_months=6,
               plan_interest_rate=plan_rate,
               plan_payment_amount=round(float(plan_payment_amount), 2),
               deferred_installment_count=0, term_extension_months=0, settlement_amount=0.0)
    return (f"Temporary Rate Reduction Plan {hardship_plan_id} is now offered (decision date {ctx.now()[:10]}): "
            f"plan rate {round(float(plan_interest_rate), 2):.2f}%, plan installment "
            f"{round(float(plan_payment_amount), 2):.2f} USD from {start_date} through {end_date}.")

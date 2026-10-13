"""Hidden task tools for the debt_waivers_disputes_and_repayment difficulty.

Each tool lands exactly one atomic write on a VA benefit debt. None of them checks eligibility,
timing, status or any prerequisite, and none computes an amount: every value is worked out by
the representative from the published rules and the records, and passed in.
"""

from erlbench import ToolContext, tool


@tool(owner="user", rw="write")
def pay_plan_reinstatement_66656e17(ctx: ToolContext, debt_id: str, amount: float) -> str:
    """The debtor authorizes, during this call, a one-time direct payment on one of their VA debts whose
    repayment plan was cancelled for missed installments (a reinstatement deposit). One call posts one payment
    and sets up no plan: the debt's
    activity shows a new direct payment received through the phone channel, dated today, with no plan month
    attached, and the debt's outstanding balance drops by exactly the amount paid. Success is shown by the
    receipt below carrying the new transaction reference and the balance left after the payment.

    Args:
        debt_id: Id class — the reference number of the VA debt being paid, as shown on the debt record
            returned by the debt lookup for this debtor.
        amount: Fixed-format class — the amount the debtor pays now, in USD, a positive number with 2
            decimal places (the value is stored rounded half-to-even to the cent; pass it already at
            cent precision).

    Returns:
        A dict rendered as text with keys: debt_txn_id (string, reference number of the posted payment),
        debt_id (string, the debt paid), amount (number, USD with 2 decimal places, the amount posted),
        transaction_date (string, YYYY-MM-DD, the posting date), payment_channel (string, always "phone"),
        new_balance (number, USD with 2 decimal places, the balance outstanding after the payment). The
        presence of debt_txn_id means the payment posted.
    """
    amt = round(float(amount), 2)
    rid = ctx.make_id("dtx_", debt_id, amt)
    today = ctx.now()[:10]
    ctx.create("debt_transactions", rid, debt_txn_id=rid, debt_id=debt_id,
               customer_id=(ctx.find("debt_accounts", debt_id=debt_id) or [{}])[0].get("customer_id"),
               event_type="debt_payment_received", amount=amt, transaction_date=today,
               collection_source="direct_payment", source_payment_id=None, request_id=None,
               payment_channel="phone", period_month="")
    rows = ctx.find("debt_accounts", debt_id=debt_id)
    new_balance = round(float((rows or [{}])[0].get("current_balance") or 0) - amt, 2)
    ctx.update("debt_accounts", debt_id, current_balance=new_balance)
    return str({"debt_txn_id": rid, "debt_id": debt_id, "amount": amt, "transaction_date": today,
                "payment_channel": "phone", "new_balance": new_balance})


@tool(owner="user", rw="write")
def submit_waiver_request_4f8614a0(ctx: ToolContext, debt_id: str, requested_amount: float,
                                   fsr_submitted: bool, received_within_hold_window: bool) -> str:
    """The debtor signs and submits, during this call, a request asking VA to waive part or all of one of
    their VA debts. One call records one waiver request on that debt, received today by phone and pending a
    decision by the Committee on Waivers and Compromises, together with whether a Financial Status Report is
    attached. The debt's balance and collection status are not changed by this call. Success is shown by the
    receipt below carrying the new request reference.

    Args:
        debt_id: Id class — the reference number of the VA debt the waiver is asked on, as shown on the debt
            record returned by the debt lookup for this debtor.
        requested_amount: Fixed-format class — the amount the debtor asks VA to waive, in USD, a positive
            number with 2 decimal places (stored rounded half-to-even to the cent; pass it at cent precision).
        fsr_submitted: Enum class — whether a Financial Status Report accompanies the request: true when the
            debtor attaches a signed Financial Status Report to this request; false when the request goes in
            without one and the report is still to follow.
        received_within_hold_window: Enum class — whether today falls inside the debt's collection-hold
            window counted from its notice date: true when today is within that window, so the request is
            one that holds collection; false when today is after that window has closed.

    Returns:
        A dict rendered as text with keys: request_id (string, reference number of the waiver request),
        debt_id (string), request_kind (string, always "waiver"), received_date (string, YYYY-MM-DD),
        requested_amount (number, USD with 2 decimal places), fsr_submitted (boolean),
        received_within_hold_window (boolean), decision_outcome (string, always "pending"). The presence of
        request_id means the request is on file.
    """
    amt = round(float(requested_amount), 2)
    rid = ctx.make_id("drq_", debt_id, amt, fsr_submitted, received_within_hold_window)
    today = ctx.now()[:10]
    cust = (ctx.find("debt_accounts", debt_id=debt_id) or [{}])[0].get("customer_id")
    ctx.create("debt_requests", rid, request_id=rid, debt_id=debt_id, customer_id=cust,
               event_type="debt_waiver_requested", request_kind="waiver", received_date=today,
               requested_amount=amt, requested_term_months=0, fsr_submitted=bool(fsr_submitted),
               received_within_hold_window=bool(received_within_hold_window), decision_outcome="pending",
               decided_amount=0.0, source_request_id=None, channel="phone")
    return str({"request_id": rid, "debt_id": debt_id, "request_kind": "waiver", "received_date": today,
                "requested_amount": amt, "fsr_submitted": bool(fsr_submitted),
                "received_within_hold_window": bool(received_within_hold_window),
                "decision_outcome": "pending"})


@tool(owner="agent", rw="write")
def record_repayment_plan_request_018c5870(ctx: ToolContext, debt_id: str, requested_term_months: int,
                                           received_within_hold_window: bool) -> str:
    """Record, on a verified caller's behalf, the debtor's request to repay one VA debt in monthly
    installments paid directly. One call records one pending repayment plan request on that debt, received
    today by phone, stating the number of months the plan is to run; the request carries no Financial Status
    Report of its own and proposes no installment. The debt's
    balance and status are not changed. Success is shown by the receipt below carrying the new request
    reference.

    Args:
        debt_id: Id class — the reference number of the VA debt the plan is for, as shown on the debt record
            returned by the debt lookup for this debtor.
        requested_term_months: Fixed-format class — the number of months the plan is to run, an integer count
            of whole months, at least 1.
        received_within_hold_window: Enum class — whether today falls inside the debt's collection-hold
            window counted from its notice date: true when today is within that window; false when today is
            after that window has closed.

    Returns:
        A dict rendered as text with keys: request_id (string, reference number of the plan request),
        debt_id (string), request_kind (string, always "repayment_plan"), received_date (string,
        YYYY-MM-DD), requested_term_months (integer months), decision_outcome (string, always "pending").
        The presence of request_id means the request is on file.
    """
    months = int(requested_term_months)
    rid = ctx.make_id("drq_", debt_id, "repayment_plan", months, received_within_hold_window)
    today = ctx.now()[:10]
    cust = (ctx.find("debt_accounts", debt_id=debt_id) or [{}])[0].get("customer_id")
    ctx.create("debt_requests", rid, request_id=rid, debt_id=debt_id, customer_id=cust,
               event_type="debt_repayment_plan_requested", request_kind="repayment_plan", received_date=today,
               requested_amount=0.0, requested_term_months=months, fsr_submitted=False,
               received_within_hold_window=bool(received_within_hold_window), decision_outcome="pending",
               decided_amount=0.0, source_request_id=None, channel="phone")
    return str({"request_id": rid, "debt_id": debt_id, "request_kind": "repayment_plan",
                "received_date": today, "requested_term_months": months, "decision_outcome": "pending"})


@tool(owner="agent", rw="write")
def start_repayment_plan_5152504c(ctx: ToolContext, debt_id: str, monthly_amount: float,
                                  start_month: str) -> str:
    """Start, on a verified caller's behalf, a repayment plan paid by monthly direct payments on one VA debt.
    One call puts the debt into repayment-plan status with the payment method set to direct payment, the
    approved monthly installment and the first plan month recorded on the debt; the balance is not changed.
    Success is shown by the receipt below echoing the plan terms now on the debt.

    Args:
        debt_id: Id class — the reference number of the VA debt the plan is for, as shown on the debt record
            returned by the debt lookup for this debtor.
        monthly_amount: Fixed-format class — the approved monthly installment, in USD, a positive number with
            2 decimal places (stored rounded half-to-even to the cent; pass it at cent precision).
        start_month: Fixed-format class — the first plan month, written YYYY-MM.

    Returns:
        A dict rendered as text with keys: debt_id (string), status (string, always "repayment_plan"),
        repayment_plan_method (string, always "direct_payment"), repayment_plan_monthly_amount (number, USD
        with 2 decimal places), repayment_plan_start_month (string, YYYY-MM). A status of "repayment_plan"
        means the plan is in effect.
    """
    amt = round(float(monthly_amount), 2)
    ctx.update("debt_accounts", debt_id, status="repayment_plan", repayment_plan_method="direct_payment",
               repayment_plan_monthly_amount=amt, repayment_plan_start_month=str(start_month))
    return str({"debt_id": debt_id, "status": "repayment_plan", "repayment_plan_method": "direct_payment",
                "repayment_plan_monthly_amount": amt, "repayment_plan_start_month": str(start_month)})


@tool(owner="agent", rw="write")
def record_reduced_withholding_request_043db99b(ctx: ToolContext, debt_id: str, requested_amount: float,
                                                received_within_hold_window: bool) -> str:
    """Record, on a verified caller's behalf, the debtor's request to have the monthly withholding from their VA
    benefit payments for one debt reduced to a smaller monthly amount. One call records one pending
    reduced-withholding request on that debt, received today by phone, stating the monthly withholding
    proposed; the request carries no Financial Status Report of its own. The debt's balance, status and current
    withholding are not changed. Success is shown by the receipt below carrying the new request reference.

    Args:
        debt_id: Id class — the reference number of the VA debt whose withholding is to be reduced, as shown on
            the debt record returned by the debt lookup for this debtor.
        requested_amount: Fixed-format class — the monthly withholding proposed, in USD, a positive number with
            2 decimal places (stored rounded half-to-even to the cent; pass it at cent precision).
        received_within_hold_window: Enum class — whether today falls inside the debt's collection-hold
            window counted from its notice date: true when today is within that window; false when today is
            after that window has closed.

    Returns:
        A dict rendered as text with keys: request_id (string, reference number of the request), debt_id
        (string), request_kind (string, always "reduced_withholding"), received_date (string, YYYY-MM-DD),
        requested_amount (number, USD with 2 decimal places), decision_outcome (string, always "pending"). The
        presence of request_id means the request is on file.
    """
    amt = round(float(requested_amount), 2)
    rid = ctx.make_id("drq_", debt_id, "reduced_withholding", amt, received_within_hold_window)
    today = ctx.now()[:10]
    cust = (ctx.find("debt_accounts", debt_id=debt_id) or [{}])[0].get("customer_id")
    ctx.create("debt_requests", rid, request_id=rid, debt_id=debt_id, customer_id=cust,
               event_type="debt_repayment_plan_requested", request_kind="reduced_withholding",
               received_date=today, requested_amount=amt, requested_term_months=0, fsr_submitted=False,
               received_within_hold_window=bool(received_within_hold_window), decision_outcome="pending",
               decided_amount=0.0, source_request_id=None, channel="phone")
    return str({"request_id": rid, "debt_id": debt_id, "request_kind": "reduced_withholding",
                "received_date": today, "requested_amount": amt, "decision_outcome": "pending"})


@tool(owner="agent", rw="write")
def start_reduced_withholding_20dc00ef(ctx: ToolContext, debt_id: str, monthly_amount: float,
                                       start_month: str) -> str:
    """Start, on a verified caller's behalf, reduced monthly withholding from VA benefit payments on one debt.
    One call puts the debt into repayment-plan status with the payment method set to benefit withholding, the
    approved monthly withholding and the first withholding month recorded on the debt; from then on each
    monthly benefit payment is withheld only that amount. The balance is not changed. Success is shown by the
    receipt below echoing the terms now on the debt.

    Args:
        debt_id: Id class — the reference number of the VA debt, as shown on the debt record returned by the
            debt lookup for this debtor.
        monthly_amount: Fixed-format class — the approved monthly withholding, in USD, a positive number with 2
            decimal places (stored rounded half-to-even to the cent; pass it at cent precision).
        start_month: Fixed-format class — the first month of reduced withholding, written YYYY-MM.

    Returns:
        A dict rendered as text with keys: debt_id (string), status (string, always "repayment_plan"),
        repayment_plan_method (string, always "benefit_withholding"), repayment_plan_monthly_amount (number,
        USD with 2 decimal places), repayment_plan_start_month (string, YYYY-MM). A status of "repayment_plan"
        means the reduced withholding is in effect.
    """
    amt = round(float(monthly_amount), 2)
    ctx.update("debt_accounts", debt_id, status="repayment_plan", repayment_plan_method="benefit_withholding",
               repayment_plan_monthly_amount=amt, repayment_plan_start_month=str(start_month))
    return str({"debt_id": debt_id, "status": "repayment_plan", "repayment_plan_method": "benefit_withholding",
                "repayment_plan_monthly_amount": amt, "repayment_plan_start_month": str(start_month)})


@tool(owner="user", rw="write")
def submit_compromise_offer_8c2d0269(ctx: ToolContext, debt_id: str, requested_amount: float,
                                     fsr_submitted: bool, received_within_hold_window: bool) -> str:
    """The debtor signs and submits, during this call, an offer to settle one of their VA debts for a lump sum
    smaller than the balance. One call records one compromise offer on that debt, received today by phone and
    pending a decision, stating the lump sum offered and whether a Financial Status Report is attached. The
    debt's balance and status are not changed by this call. Success is shown by the receipt below carrying the
    new offer reference.

    Args:
        debt_id: Id class — the reference number of the VA debt the offer is made on, as shown on the debt
            record returned by the debt lookup for this debtor.
        requested_amount: Fixed-format class — the lump sum offered, in USD, a positive number with 2 decimal
            places (stored rounded half-to-even to the cent; pass it at cent precision).
        fsr_submitted: Enum class — whether a Financial Status Report accompanies the offer: true when the
            debtor attaches a signed Financial Status Report to this offer; false when the offer goes in without
            one.
        received_within_hold_window: Enum class — whether today falls inside the debt's collection-hold
            window counted from its notice date: true when today is within that window; false when today is
            after that window has closed.

    Returns:
        A dict rendered as text with keys: request_id (string, reference number of the offer), debt_id
        (string), request_kind (string, always "compromise"), received_date (string, YYYY-MM-DD),
        requested_amount (number, USD with 2 decimal places), fsr_submitted (boolean),
        decision_outcome (string, always "pending"). The presence of request_id means the offer is on file.
    """
    amt = round(float(requested_amount), 2)
    rid = ctx.make_id("drq_", debt_id, "compromise", amt, fsr_submitted, received_within_hold_window)
    today = ctx.now()[:10]
    cust = (ctx.find("debt_accounts", debt_id=debt_id) or [{}])[0].get("customer_id")
    ctx.create("debt_requests", rid, request_id=rid, debt_id=debt_id, customer_id=cust,
               event_type="debt_compromise_offered", request_kind="compromise", received_date=today,
               requested_amount=amt, requested_term_months=0, fsr_submitted=bool(fsr_submitted),
               received_within_hold_window=bool(received_within_hold_window), decision_outcome="pending",
               decided_amount=0.0, source_request_id=None, channel="phone")
    return str({"request_id": rid, "debt_id": debt_id, "request_kind": "compromise", "received_date": today,
                "requested_amount": amt, "fsr_submitted": bool(fsr_submitted), "decision_outcome": "pending"})

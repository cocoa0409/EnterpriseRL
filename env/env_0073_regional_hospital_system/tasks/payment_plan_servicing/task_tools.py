"""Hidden task tools for the payment_plan_servicing difficulty (category: plan) of env_0073_regional_hospital_system.

Each tool performs exactly one atomic write on a Riverbend patient payment plan with the values the caller
supplies. No tool checks plan status, eligibility, deadlines or any other business condition, and no tool
derives a figure for the caller.
"""

from erlbench import ToolContext, tool


@tool(owner="agent", rw="write")
def pause_plan_installments_136536f5(ctx: ToolContext, plan_id: str, term_months: int) -> str:
    """Record an assistance pause on a patient's payment plan. The installments that are paused while the
    patient's financial assistance application is open are moved to the end of the schedule, which is booked
    by setting the plan's number of scheduled monthly installments to the figure given. The plan's status,
    its count of missed installments, its installment amount and its due dates are left exactly as they are.
    On success the plan shows the new number of scheduled installments and the receipt below is returned.

    Args:
        plan_id: Id class — the reference number of the patient's payment plan, as returned by the payment plan lookup for this patient.
        term_months: Fixed-format class — the plan's number of scheduled monthly installments with the pause booked, as a positive integer count of installments (no decimals, no unit text).

    Returns:
        A confirmation string of the form "Assistance pause recorded on plan <plan_id>: <term_months> scheduled installments."
        where <plan_id> is the plan reference number and <term_months> the positive integer now on the plan; receiving this
        string means the pause was booked.
    """
    ctx.update("payment_plans", plan_id, term_months=int(term_months))
    return f"Assistance pause recorded on plan {plan_id}: {int(term_months)} scheduled installments."


@tool(owner="agent", rw="write")
def reage_payment_plan_e7c586c0(ctx: ToolContext, plan_id: str, term_months: int, next_due_date: str) -> str:
    """Re-age a past-due patient payment plan at the patient's request. The plan's missed installments are
    settled by the re-age: the plan returns to active status, its count of consecutive missed installments
    is cleared to zero, its count of re-ages used goes up by one, and its number of scheduled monthly
    installments and its next due date are set to the values given. The installment amount, the first due date
    and the due day are left as they are. On success the plan shows as active with no missed installment and the
    receipt below is returned.

    Args:
        plan_id: Id class — the reference number of the patient's payment plan, as returned by the payment plan lookup for this patient.
        term_months: Fixed-format class — the plan's number of scheduled monthly installments with the re-age booked, as a positive integer count of installments (no decimals, no unit text).
        next_due_date: Fixed-format class — the plan's next installment due date with the re-age booked, as a calendar date written YYYY-MM-DD.

    Returns:
        A confirmation string of the form "Plan <plan_id> re-aged: active, <term_months> scheduled installments, next due <next_due_date>, re-age <n> used."
        where <plan_id> is the plan reference number, <term_months> the positive integer now on the plan, <next_due_date> the
        date now on the plan and <n> the integer count of re-ages used including this one; receiving this string means the
        re-age was booked.
    """
    rows = ctx.find("payment_plans", plan_id=plan_id)
    used = int((rows[0].get("reage_count") if rows else 0) or 0) + 1
    ctx.update("payment_plans", plan_id, status="active", missed_installments=0, reage_count=used, term_months=int(term_months), next_due_date=str(next_due_date))
    return f"Plan {plan_id} re-aged: active, {int(term_months)} scheduled installments, next due {next_due_date}, re-age {used} used."


@tool(owner="agent", rw="write")
def recompute_plan_installment_b9083db3(ctx: ToolContext, plan_id: str, monthly_payment_usd: float) -> str:
    """Book a recomputed installment on a patient's signed payment plan that has had balances added to it.
    The plan's regular monthly installment is replaced by the amount given; the plan balance, the number of
    scheduled installments, the status and the due dates are left as they are. On success the plan shows the
    new installment amount and the receipt below is returned.

    Args:
        plan_id: Id class — the reference number of the patient's payment plan, as returned by the payment plan lookup for this patient.
        monthly_payment_usd: Fixed-format class — the recomputed regular monthly installment in USD, 2 decimal places (cents), already rounded by the caller; a plain number without a currency sign.

    Returns:
        A confirmation string of the form "Installment on plan <plan_id> recomputed to <monthly_payment_usd> USD."
        where <plan_id> is the plan reference number and <monthly_payment_usd> the installment now on the plan in USD with
        2 decimal places; receiving this string means the recomputed installment was booked.
    """
    amount = round(float(monthly_payment_usd), 2)
    ctx.update("payment_plans", plan_id, monthly_payment_usd=amount)
    return f"Installment on plan {plan_id} recomputed to {amount:.2f} USD."


@tool(owner="user", rw="write")
def set_requested_installment_eff91f18(ctx: ToolContext, plan_id: str, monthly_payment_usd: float) -> str:
    """Sign, as the patient, an installment change on your own payment plan that lowers the regular monthly
    installment to the amount given. The plan's installment is replaced by that amount and the plan's count
    of patient-requested installment or due-day changes goes up by one; the plan balance, status and due dates
    are left as they are. On success the plan shows the new installment and the receipt below is returned.

    Args:
        plan_id: Id class — the reference number of your payment plan, as read to you by the representative from the payment plan record.
        monthly_payment_usd: Fixed-format class — the new regular monthly installment in USD, 2 decimal places (cents), as given to you by the representative; a plain number without a currency sign.

    Returns:
        A confirmation string of the form "Installment change signed on plan <plan_id>: <monthly_payment_usd> USD per month, change <n> of the plan."
        where <plan_id> is the plan reference number, <monthly_payment_usd> the installment now on the plan in USD with
        2 decimal places and <n> the integer count of patient-requested changes including this one; receiving this
        string means the change was signed and booked.
    """
    rows = ctx.find("payment_plans", plan_id=plan_id)
    changes = int((rows[0].get("terms_change_count") if rows else 0) or 0) + 1
    amount = round(float(monthly_payment_usd), 2)
    ctx.update("payment_plans", plan_id, monthly_payment_usd=amount, terms_change_count=changes)
    return f"Installment change signed on plan {plan_id}: {amount:.2f} USD per month, change {changes} of the plan."


@tool(owner="agent", rw="write")
def refigure_plan_offer_04613189(ctx: ToolContext, plan_id: str, monthly_payment_usd: float, term_months: int) -> str:
    """Re-figure the installment on a payment plan offer the patient has not signed yet. The offer's regular
    monthly installment is replaced by the amount given and its number of monthly installments by the term
    given; the enrolled balances, the down payment on the offer, the due dates and the status
    pending_signature are left as they are. On success the offer shows the re-figured installment and term
    and the receipt below is returned.

    Args:
        plan_id: Id class — the reference number of the unsigned payment plan offer, as returned by the payment plan lookup for this patient.
        monthly_payment_usd: Fixed-format class — the re-figured regular monthly installment in USD, 2 decimal places (cents), already rounded by the caller; a plain number without a currency sign.
        term_months: Fixed-format class — the number of monthly installments the re-figured offer is booked with, a positive integer.

    Returns:
        A confirmation string of the form "Offer <plan_id> re-figured: <monthly_payment_usd> USD per month over <term_months> months."
        where <plan_id> is the offer reference number, <monthly_payment_usd> the installment now on the offer in USD with
        2 decimal places and <term_months> the number of installments now on the offer; receiving this string means the
        re-figured installment and term were booked.
    """
    amount = round(float(monthly_payment_usd), 2)
    ctx.update("payment_plans", plan_id, monthly_payment_usd=amount, term_months=int(term_months))
    return f"Offer {plan_id} re-figured: {amount:.2f} USD per month over {int(term_months)} months."


@tool(owner="user", rw="write")
def sign_plan_agreement_1c5ceaa0(ctx: ToolContext, plan_id: str, autopay_method: str, down_payment_usd: float) -> str:
    """Sign, as the patient, the Riverbend Patient Payment Plan Agreement on your own payment plan offer and
    authorize its autopay method and the down payment drawn at signing. The plan becomes active, today's date
    is stamped as its signing date, the autopay method given is recorded, and the down payment amount given is
    recorded as the down payment due at signing. On success the plan shows as active and the receipt below is
    returned.

    Args:
        plan_id: Id class — the reference number of your payment plan offer, as read to you by the representative from the payment plan record.
        autopay_method: Enum class — the autopay method you authorize for your installments, exactly one of: ACH — drafts are drawn from your checking or savings account by ACH; CARD — drafts are charged to your debit or credit card; NONE — no autopay, each installment is paid by hand (only on plans that do not require autopay).
        down_payment_usd: Fixed-format class — the down payment drawn at signing in USD, 2 decimal places (cents), as given to you by the representative; 0.00 when none is due; a plain number without a currency sign.

    Returns:
        A confirmation string of the form "Agreement signed on plan <plan_id> on <signed_date>: autopay <autopay_method>, down payment <down_payment_usd> USD."
        where <plan_id> is the plan reference number, <signed_date> the signing date as YYYY-MM-DD, <autopay_method> the
        method recorded and <down_payment_usd> the down payment recorded in USD with 2 decimal places; receiving this
        string means the agreement is signed and the plan is active.
    """
    amount = round(float(down_payment_usd), 2)
    signed = ctx.now()[:10]
    ctx.update("payment_plans", plan_id, status="active", signed_date=signed, autopay_method=autopay_method, down_payment_usd=amount)
    return f"Agreement signed on plan {plan_id} on {signed}: autopay {autopay_method}, down payment {amount:.2f} USD."

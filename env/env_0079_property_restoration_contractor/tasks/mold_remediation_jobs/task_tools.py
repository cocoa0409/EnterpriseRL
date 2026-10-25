"""Hidden task tools of the mold_remediation_jobs difficulty (category: mold).

Each tool performs one atomic business write on one mold remediation job. The agent reaches the
agent-owned tools through unlock_agent_discoverable_tool -> call_agent_discoverable_tool, and the
customer runs the user-owned tools through unlock_user_discoverable_tool ->
call_user_discoverable_tool once the agent hands them over.
"""

from decimal import Decimal, ROUND_HALF_UP

from erlbench import ToolContext, tool


class _MoldFormat:
    """Format helpers shared by the tool bodies (values only; every write stays in the tool)."""

    @staticmethod
    def cents(value) -> float:
        """Round a money value to the cent, half up, exactly."""
        return float(Decimal(str(value)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP))

    @staticmethod
    def is_cents(value) -> bool:
        """True when the value carries no more than two decimal places."""
        d = Decimal(str(value))
        return d == d.quantize(Decimal("0.01"))

    @staticmethod
    def is_date(text) -> bool:
        """True when the text is a calendar date written YYYY-MM-DD."""
        s = str(text)
        if len(s) != 10 or s[4] != "-" or s[7] != "-":
            return False
        y, m, d = s[:4], s[5:7], s[8:]
        if not (y.isdigit() and m.isdigit() and d.isdigit()):
            return False
        yi, mi, di = int(y), int(m), int(d)
        if mi < 1 or mi > 12 or di < 1:
            return False
        month_days = [31, 29 if (yi % 4 == 0 and (yi % 100 != 0 or yi % 400 == 0)) else 28,
                      31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
        return di <= month_days[mi - 1]


@tool(owner="agent", rw="write")
def book_mold_presample_d4275783(ctx: ToolContext, mold_job_id: str, service_date: str, amount: float) -> str:
    """Book the pre-removal asbestos sampling charge on one mold remediation job.

    The desk records, on the named job, one sampling charge line coded asbestos_sampling for the samples
    collected before any drywall, texture or insulation removal. The line is booked as quantity 1 each
    with the line amount as its rate, in the business_hours window, and the job's balance due rises by
    the amount. The new line is immediately visible among the job's charge lines.

    Args:
        mold_job_id: Id class — the reference number of the mold remediation job the sampling is billed on,
            read from the job lookup for this customer.
        service_date: Fixed-format class — the date the samples were collected, written YYYY-MM-DD as a
            calendar date with no time or time zone; an empty value is not accepted.
        amount: Fixed-format class — the sampling charge in US dollars, a positive number with at most 2
            decimal places, already rounded to the cent half up; it is stored to the cent.

    Returns:
        A confirmation string naming the new charge line's reference number, the job reference number,
        the charge code asbestos_sampling, the service date (YYYY-MM-DD), the amount booked (USD, 2
        decimals) and the job's new balance due (USD, 2 decimals). A string starting with "Error:" means
        nothing was booked because an argument did not meet its stated format.
    """
    if not _MoldFormat.is_date(service_date):
        return "Error: service_date must be a calendar date written YYYY-MM-DD."
    if float(amount) <= 0 or not _MoldFormat.is_cents(amount):
        return "Error: amount must be a positive USD value with at most 2 decimal places."
    value = _MoldFormat.cents(amount)
    jobs = ctx.find("mold_jobs", mold_job_id=mold_job_id)
    job = jobs[0] if jobs else {}
    rid = ctx.make_id("mch_", mold_job_id, service_date, amount)
    ctx.create("mold_charges", rid, mold_charge_id=rid, mold_job_id=mold_job_id,
               customer_id=job.get("customer_id"), event_type="mold_remediation_charge",
               charge_code="asbestos_sampling", service_date=service_date, quantity=1.0, unit="each",
               unit_rate=value, rate_window="business_hours", amount=value)
    balance = _MoldFormat.cents(float(job.get("balance_due") or 0) + value)
    ctx.update("mold_jobs", mold_job_id, balance_due=balance)
    return (f"Charge line {rid} booked on job {mold_job_id}: asbestos_sampling dated {service_date}, "
            f"amount {value:.2f} USD; job balance due is now {balance:.2f} USD.")


@tool(owner="agent", rw="write")
def book_mold_workplan_1501986a(ctx: ToolContext, mold_job_id: str, service_date: str, amount: float) -> str:
    """Book the supervisor's work-plan visit charge on one mold remediation job.

    The desk records, on the named job, one supervisor_labor charge line for the visit at which the
    remediation supervisor walked the site with the assessor's protocol and wrote the remediation work
    plan. The line is booked as quantity 1 each with the line amount as its rate, in the business_hours
    window, and the job's balance due rises by the amount. The new line is immediately visible among the
    job's charge lines.

    Args:
        mold_job_id: Id class — the reference number of the mold remediation job the visit is billed on,
            read from the job lookup for this customer.
        service_date: Fixed-format class — the date of the work-plan visit, written YYYY-MM-DD as a
            calendar date with no time or time zone; an empty value is not accepted.
        amount: Fixed-format class — the visit charge in US dollars, a positive number with at most 2
            decimal places, already rounded to the cent half up; it is stored to the cent.

    Returns:
        A confirmation string naming the new charge line's reference number, the job reference number,
        the charge code supervisor_labor, the service date (YYYY-MM-DD), the amount booked (USD, 2
        decimals) and the job's new balance due (USD, 2 decimals). A string starting with "Error:" means
        nothing was booked because an argument did not meet its stated format.
    """
    if not _MoldFormat.is_date(service_date):
        return "Error: service_date must be a calendar date written YYYY-MM-DD."
    if float(amount) <= 0 or not _MoldFormat.is_cents(amount):
        return "Error: amount must be a positive USD value with at most 2 decimal places."
    value = _MoldFormat.cents(amount)
    jobs = ctx.find("mold_jobs", mold_job_id=mold_job_id)
    job = jobs[0] if jobs else {}
    rid = ctx.make_id("mch_", mold_job_id, service_date, amount)
    ctx.create("mold_charges", rid, mold_charge_id=rid, mold_job_id=mold_job_id,
               customer_id=job.get("customer_id"), event_type="mold_remediation_charge",
               charge_code="supervisor_labor", service_date=service_date, quantity=1.0, unit="each",
               unit_rate=value, rate_window="business_hours", amount=value)
    balance = _MoldFormat.cents(float(job.get("balance_due") or 0) + value)
    ctx.update("mold_jobs", mold_job_id, balance_due=balance)
    return (f"Charge line {rid} booked on job {mold_job_id}: supervisor_labor work-plan visit dated "
            f"{service_date}, amount {value:.2f} USD; job balance due is now {balance:.2f} USD.")


@tool(owner="agent", rw="write")
def book_mold_disposal_772b05b2(ctx: ToolContext, mold_job_id: str, service_date: str, amount: float) -> str:
    """Book the bagged debris haul-off charge on one mold remediation job.

    The desk records, on the named job, one debris_disposal charge line for hauling off the bagged
    drywall and insulation removed from the work area. The line is booked as quantity 1 each with the
    line amount as its rate, in the business_hours window, and the job's balance due rises by the
    amount. The new line is immediately visible among the job's charge lines.

    Args:
        mold_job_id: Id class — the reference number of the mold remediation job the haul-off is billed
            on, read from the job lookup for this customer.
        service_date: Fixed-format class — the date the debris was hauled off, written YYYY-MM-DD as a
            calendar date with no time or time zone; an empty value is not accepted.
        amount: Fixed-format class — the haul-off charge in US dollars, a positive number with at most 2
            decimal places, already rounded to the cent half up; it is stored to the cent.

    Returns:
        A confirmation string naming the new charge line's reference number, the job reference number,
        the charge code debris_disposal, the service date (YYYY-MM-DD), the amount booked (USD, 2
        decimals) and the job's new balance due (USD, 2 decimals). A string starting with "Error:" means
        nothing was booked because an argument did not meet its stated format.
    """
    if not _MoldFormat.is_date(service_date):
        return "Error: service_date must be a calendar date written YYYY-MM-DD."
    if float(amount) <= 0 or not _MoldFormat.is_cents(amount):
        return "Error: amount must be a positive USD value with at most 2 decimal places."
    value = _MoldFormat.cents(amount)
    jobs = ctx.find("mold_jobs", mold_job_id=mold_job_id)
    job = jobs[0] if jobs else {}
    rid = ctx.make_id("mch_", mold_job_id, service_date, amount)
    ctx.create("mold_charges", rid, mold_charge_id=rid, mold_job_id=mold_job_id,
               customer_id=job.get("customer_id"), event_type="mold_remediation_charge",
               charge_code="debris_disposal", service_date=service_date, quantity=1.0, unit="each",
               unit_rate=value, rate_window="business_hours", amount=value)
    balance = _MoldFormat.cents(float(job.get("balance_due") or 0) + value)
    ctx.update("mold_jobs", mold_job_id, balance_due=balance)
    return (f"Charge line {rid} booked on job {mold_job_id}: debris_disposal dated {service_date}, "
            f"amount {value:.2f} USD; job balance due is now {balance:.2f} USD.")


@tool(owner="user", rw="write")
def sign_mold_agreement_2b99f603(ctx: ToolContext, mold_job_id: str, deposit_amount: float,
                                 payment_method: str) -> str:
    """Sign the remediation agreement for one scheduled mold job and pay its signing deposit in the same act.

    The property owner, or the owner's authorized agent, signs the remediation agreement in the
    company's secure signing and payment channel and pays the signing deposit there; no card or bank
    details pass through company staff. On completion the job moves to authorized status with today's
    date as its signing date. When the deposit is above 0.00 it is posted in full as one customer
    payment on the job dated today and lowers the balance due; a credit card payment also books a card
    surcharge line of 2.95 percent of the payment, rounded to the cent half up, which raises the balance
    due. A deposit of 0.00 signs the agreement without posting a payment.

    Args:
        mold_job_id: Id class — the reference number of the scheduled mold remediation job being signed,
            as the agent reads it from the job lookup and gives it to the customer.
        deposit_amount: Fixed-format class — the signing deposit the agent states, in US dollars, zero or
            positive, with at most 2 decimal places, already rounded to the cent half up.
        payment_method: Enum class — the tender the customer pays the deposit with, exactly one of:
            "credit_card" when the customer pays with a credit card (a card surcharge line is added);
            "debit_card" when the customer pays with a debit card; "ach" when the customer pays by bank
            transfer from a checking or savings account; "check" when the customer pays by an electronic
            check drawn on their bank account.

    Returns:
        A confirmation string giving the job reference number, its new status authorized, the signing
        date (YYYY-MM-DD), and, when a deposit was paid, the payment line's reference number, the
        payment confirmation number generated by the channel, the tender, the amount paid (USD, 2
        decimals), any card surcharge booked (USD, 2 decimals) and the job's new balance due (USD, 2
        decimals). A string starting with "Error:" means nothing was signed or paid because an argument
        did not meet its stated format.
    """
    methods = ("credit_card", "debit_card", "ach", "check")
    if payment_method not in methods:
        return "Error: payment_method must be one of credit_card, debit_card, ach or check."
    if float(deposit_amount) < 0 or not _MoldFormat.is_cents(deposit_amount):
        return "Error: deposit_amount must be zero or a positive USD value with at most 2 decimal places."
    value = _MoldFormat.cents(deposit_amount)
    today = ctx.now()[:10]
    jobs = ctx.find("mold_jobs", mold_job_id=mold_job_id)
    job = jobs[0] if jobs else {}
    balance = float(job.get("balance_due") or 0)
    ctx.update("mold_jobs", mold_job_id, status="authorized", authorized_date=today)
    if value == 0:
        return (f"Agreement signed for job {mold_job_id}: status authorized, signing date {today}; "
                f"no deposit was due, so no payment was posted; balance due {balance:.2f} USD.")
    pid = ctx.make_id("mpy_", mold_job_id, deposit_amount, payment_method)
    confirmation = "SPC" + pid[-8:].upper()
    ctx.create("mold_payments", pid, mold_payment_id=pid, mold_job_id=mold_job_id,
               customer_id=job.get("customer_id"), event_type="mold_customer_payment",
               payment_method=payment_method, payment_reference=confirmation, posted_date=today,
               amount=value)
    balance = balance - value
    surcharge = 0.0
    if payment_method == "credit_card":
        surcharge = _MoldFormat.cents(value * 2.95 / 100)
        sid = ctx.make_id("mch_", pid, "card_surcharge")
        ctx.create("mold_charges", sid, mold_charge_id=sid, mold_job_id=mold_job_id,
                   customer_id=job.get("customer_id"), event_type="mold_card_surcharge",
                   charge_code="card_surcharge", source_payment_id=pid, amount=surcharge)
        balance = balance + surcharge
    balance = _MoldFormat.cents(balance)
    ctx.update("mold_jobs", mold_job_id, balance_due=balance)
    return (f"Agreement signed for job {mold_job_id}: status authorized, signing date {today}. Deposit "
            f"payment {pid} posted, confirmation {confirmation}, tender {payment_method}, amount "
            f"{value:.2f} USD, card surcharge {surcharge:.2f} USD; balance due is now {balance:.2f} USD.")


@tool(owner="user", rw="write")
def pay_mold_insured_share_5816092f(ctx: ToolContext, mold_job_id: str, payment_amount: float,
                                    payment_method: str) -> str:
    """Pay the customer's own share of one mold remediation job through the secure payment channel.

    The customer completes the payment in the company's secure payment channel; no card or bank details
    pass through company staff. The payment is posted in full as one customer payment on the named job,
    dated today, and lowers the job's balance due by the amount paid; a credit card payment also books a
    card surcharge line of 2.95 percent of the payment, rounded to the cent half up, which raises the
    balance due. The payment is immediately visible among the job's payment lines.

    Args:
        mold_job_id: Id class — the reference number of the mold remediation job being paid, as the agent
            reads it from the job lookup and gives it to the customer.
        payment_amount: Fixed-format class — the amount the agent states for the customer's own share, in
            US dollars, a positive number with at most 2 decimal places, already rounded to the cent half up.
        payment_method: Enum class — the tender the customer pays with, exactly one of: "credit_card" when
            the customer pays with a credit card (a card surcharge line is added); "debit_card" when the
            customer pays with a debit card; "ach" when the customer pays by bank transfer from a checking
            or savings account; "check" when the customer pays by an electronic check drawn on their bank
            account.

    Returns:
        A confirmation string giving the payment line's reference number, the payment confirmation number
        generated by the channel, the job reference number, the tender, the amount paid (USD, 2 decimals),
        the posting date (YYYY-MM-DD), any card surcharge booked (USD, 2 decimals) and the job's new
        balance due (USD, 2 decimals). A string starting with "Error:" means nothing was paid because an
        argument did not meet its stated format.
    """
    methods = ("credit_card", "debit_card", "ach", "check")
    if payment_method not in methods:
        return "Error: payment_method must be one of credit_card, debit_card, ach or check."
    if float(payment_amount) <= 0 or not _MoldFormat.is_cents(payment_amount):
        return "Error: payment_amount must be a positive USD value with at most 2 decimal places."
    value = _MoldFormat.cents(payment_amount)
    today = ctx.now()[:10]
    jobs = ctx.find("mold_jobs", mold_job_id=mold_job_id)
    job = jobs[0] if jobs else {}
    pid = ctx.make_id("mpy_", mold_job_id, payment_amount, payment_method)
    confirmation = "SPC" + pid[-8:].upper()
    ctx.create("mold_payments", pid, mold_payment_id=pid, mold_job_id=mold_job_id,
               customer_id=job.get("customer_id"), event_type="mold_customer_payment",
               payment_method=payment_method, payment_reference=confirmation, posted_date=today,
               amount=value)
    balance = float(job.get("balance_due") or 0) - value
    surcharge = 0.0
    if payment_method == "credit_card":
        surcharge = _MoldFormat.cents(value * 2.95 / 100)
        sid = ctx.make_id("mch_", pid, "card_surcharge")
        ctx.create("mold_charges", sid, mold_charge_id=sid, mold_job_id=mold_job_id,
                   customer_id=job.get("customer_id"), event_type="mold_card_surcharge",
                   charge_code="card_surcharge", source_payment_id=pid, amount=surcharge)
        balance = balance + surcharge
    balance = _MoldFormat.cents(balance)
    ctx.update("mold_jobs", mold_job_id, balance_due=balance)
    return (f"Payment {pid} posted on job {mold_job_id}, confirmation {confirmation}, tender {payment_method}, "
            f"amount {value:.2f} USD, posted {today}, card surcharge {surcharge:.2f} USD; balance due is now "
            f"{balance:.2f} USD.")

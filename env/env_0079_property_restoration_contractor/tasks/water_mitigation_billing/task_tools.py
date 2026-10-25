"""Hidden task tools for water_mitigation_billing (Water Damage Mitigation).

Each tool performs one atomic write on a water mitigation job and returns a receipt. No tool
checks any business precondition; the agent decides every value from the published policy,
the job's records and the conversation.
"""

from decimal import Decimal, ROUND_HALF_UP

from erlbench import ToolContext, tool


class _Fmt:
    """Formatting helpers used by the tool bodies (format enforcement only, no business logic)."""

    @staticmethod
    def money(value) -> float:
        return float(Decimal(str(value)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP))

    @staticmethod
    def is_two_place(value) -> bool:
        d = Decimal(str(value))
        return d == d.quantize(Decimal("0.01"))

    @staticmethod
    def is_date(text) -> bool:
        s = str(text or "")
        if len(s) != 10 or s[4] != "-" or s[7] != "-":
            return False
        y, m, d = s[:4], s[5:7], s[8:]
        if not (y.isdigit() and m.isdigit() and d.isdigit()):
            return False
        return 1 <= int(m) <= 12 and 1 <= int(d) <= 31


@tool(owner="agent", rw="write")
def book_tearout_debris_a8b773d4(ctx: ToolContext, water_job_id: str, service_date: str, loads: float,
                                 unit_rate: float, amount: float) -> str:
    """Book the tear-out debris haul-off charge on one water mitigation job.

    The desk agent books, on the named water mitigation job, one debris haul-off charge line billed
    in pickup-truck loads for the debris removed during tear-out. On success a new charge line with
    service code debris_haul, unit load, the given loads, per-load rate and amount is added to the
    job, and the job's balance due rises by the amount. The customer sees the line on the job's
    charge list and the higher balance. The call succeeds when the receipt starts with "Booked".

    Args:
        water_job_id: Id class — the reference number of the water mitigation job the debris was removed from, read from the water mitigation job lookup before the call.
        service_date: Fixed-format class — the calendar date the debris haul-off line is dated, written YYYY-MM-DD with no time and no time zone; never empty.
        loads: Fixed-format class — the number of pickup-truck loads billed, a positive whole number of loads written in the decimal, up to 2 places format with no fractional part (unit: load).
        unit_rate: Fixed-format class — the per-load rate in USD, a positive amount with exactly 2 decimal places, already rounded to the cent half up before the call.
        amount: Fixed-format class — the line amount in USD, a positive amount with exactly 2 decimal places, already rounded to the cent half up before the call.

    Returns:
        A text receipt "Booked debris haul-off charge <charge reference> on job <job reference>: <loads> load(s) at <per-load rate> = <amount> USD; balance due now <balance> USD." where the charge reference is the new line's reference number, the amounts are USD with 2 decimals and the balance is the job's balance due after the line. A text starting with "Error:" means nothing was booked because an argument broke its format.
    """
    if not _Fmt.is_date(service_date):
        return "Error: service_date must be written YYYY-MM-DD."
    if float(loads) <= 0 or float(loads) != int(float(loads)):
        return "Error: loads must be a positive whole number."
    if float(unit_rate) <= 0 or float(amount) <= 0:
        return "Error: unit_rate and amount must be positive."
    if not (_Fmt.is_two_place(unit_rate) and _Fmt.is_two_place(amount)):
        return "Error: unit_rate and amount must carry exactly 2 decimal places."
    jobs = ctx.find("water_jobs", water_job_id=water_job_id)
    if not jobs:
        return f"Error: no water mitigation job {water_job_id}."
    job = jobs[0]
    amt = _Fmt.money(amount)
    rid = ctx.make_id("wch_", water_job_id, service_date, loads, unit_rate, amount)
    ctx.create("water_charges", rid, water_charge_id=rid, water_job_id=water_job_id, customer_id=job.get("customer_id"),
               event_type="water_mitigation_service_charge", charge_code="debris_haul", service_date=service_date,
               quantity=float(int(float(loads))), unit="load", unit_rate=_Fmt.money(unit_rate), amount=amt)
    new_balance = _Fmt.money(float(job.get("balance_due") or 0) + amt)
    ctx.update("water_jobs", water_job_id, balance_due=new_balance)
    return (f"Booked debris haul-off charge {rid} on job {water_job_id}: {int(float(loads))} load(s) at "
            f"{_Fmt.money(unit_rate):.2f} = {amt:.2f} USD; balance due now {new_balance:.2f} USD.")


@tool(owner="agent", rw="write")
def book_tearout_antimicrobial_173ee43e(ctx: ToolContext, water_job_id: str, service_date: str, square_feet: float,
                                        unit_rate: float, amount: float) -> str:
    """Book the tear-out antimicrobial treatment charge on one water mitigation job.

    The desk agent books, on the named water mitigation job, one antimicrobial application charge
    line billed by the square foot for the surfaces the tear-out exposed. On success a new charge
    line with service code antimicrobial, unit sqft, the given square feet, rate per square foot and
    amount is added to the job, and the job's balance due rises by the amount. The customer sees the
    line on the job's charge list and the higher balance. The call succeeds when the receipt starts
    with "Booked".

    Args:
        water_job_id: Id class — the reference number of the water mitigation job whose surfaces were treated, read from the water mitigation job lookup before the call.
        service_date: Fixed-format class — the calendar date the antimicrobial line is dated, written YYYY-MM-DD with no time and no time zone; never empty.
        square_feet: Fixed-format class — the billed square feet, a positive number in the decimal, up to 2 places format, already rounded half up before the call (unit: square foot).
        unit_rate: Fixed-format class — the rate per square foot in USD, a positive amount with exactly 2 decimal places, already rounded to the cent half up before the call.
        amount: Fixed-format class — the line amount in USD, a positive amount with exactly 2 decimal places, already rounded to the cent half up before the call.

    Returns:
        A text receipt "Booked antimicrobial charge <charge reference> on job <job reference>: <square feet> sq ft at <rate> = <amount> USD; balance due now <balance> USD." where the charge reference is the new line's reference number, the amounts are USD with 2 decimals and the balance is the job's balance due after the line. A text starting with "Error:" means nothing was booked because an argument broke its format.
    """
    if not _Fmt.is_date(service_date):
        return "Error: service_date must be written YYYY-MM-DD."
    if float(square_feet) <= 0 or float(unit_rate) <= 0 or float(amount) <= 0:
        return "Error: square_feet, unit_rate and amount must be positive."
    if not (_Fmt.is_two_place(square_feet) and _Fmt.is_two_place(unit_rate) and _Fmt.is_two_place(amount)):
        return "Error: square_feet, unit_rate and amount must carry at most 2 decimal places."
    jobs = ctx.find("water_jobs", water_job_id=water_job_id)
    if not jobs:
        return f"Error: no water mitigation job {water_job_id}."
    job = jobs[0]
    amt = _Fmt.money(amount)
    rid = ctx.make_id("wch_", water_job_id, service_date, square_feet, unit_rate, amount)
    ctx.create("water_charges", rid, water_charge_id=rid, water_job_id=water_job_id, customer_id=job.get("customer_id"),
               event_type="water_mitigation_service_charge", charge_code="antimicrobial", service_date=service_date,
               quantity=_Fmt.money(square_feet), unit="sqft", unit_rate=_Fmt.money(unit_rate), amount=amt)
    new_balance = _Fmt.money(float(job.get("balance_due") or 0) + amt)
    ctx.update("water_jobs", water_job_id, balance_due=new_balance)
    return (f"Booked antimicrobial charge {rid} on job {water_job_id}: {_Fmt.money(square_feet):.2f} sq ft at "
            f"{_Fmt.money(unit_rate):.2f} = {amt:.2f} USD; balance due now {new_balance:.2f} USD.")


@tool(owner="user", rw="write")
def pay_drying_deposit_ee9a2909(ctx: ToolContext, water_job_id: str, payment_method: str, amount: float) -> str:
    """Pay the drying deposit on one's own water mitigation job through the secure payment channel.

    The customer pays, in person through the company's secure payment channel, the drying deposit
    on their own water mitigation job. On success one customer payment is posted in full to the
    named job with the chosen tender, a processor confirmation number is issued, and the job's
    balance due falls by the amount. The customer sees the confirmation number and the new balance.
    The call succeeds when the receipt starts with "Payment posted".

    Args:
        water_job_id: Id class — the reference number of the customer's water mitigation job, as the desk agent reads it from the water mitigation job lookup and gives it to the customer before the payment.
        payment_method: Enum class — the tender the customer pays with, exactly one of: "credit_card" when the customer pays with a credit card; "debit_card" when the customer pays with a debit card; "ach" when the customer pays by bank transfer from a checking or savings account; "check" when the customer pays with a paper or electronic check.
        amount: Fixed-format class — the amount paid in USD, a positive amount with exactly 2 decimal places, already rounded to the cent half up before the call.

    Returns:
        A text receipt "Payment posted: <amount> USD by <tender> to job <job reference>, confirmation <confirmation number>, payment reference <payment reference>; balance due now <balance> USD." where the confirmation number is the processor confirmation issued for this payment, the payment reference is the new payment line's reference number and the balance is the job's balance due after the payment. A text starting with "Error:" means nothing was paid because an argument broke its format.
    """
    allowed = {"credit_card", "debit_card", "ach", "check"}
    if payment_method not in allowed:
        return f"Error: payment_method must be one of {', '.join(sorted(allowed))}."
    if float(amount) <= 0 or not _Fmt.is_two_place(amount):
        return "Error: amount must be positive with exactly 2 decimal places."
    jobs = ctx.find("water_jobs", water_job_id=water_job_id)
    if not jobs:
        return f"Error: no water mitigation job {water_job_id}."
    job = jobs[0]
    amt = _Fmt.money(amount)
    rid = ctx.make_id("wpy_", water_job_id, payment_method, amount)
    confirmation = "DP" + rid[-10:].upper()
    ctx.create("water_payments", rid, water_payment_id=rid, water_job_id=water_job_id, customer_id=job.get("customer_id"),
               event_type="water_customer_payment", payment_method=payment_method, payment_reference=confirmation,
               posted_date=ctx.now()[:10], amount=amt)
    new_balance = _Fmt.money(float(job.get("balance_due") or 0) - amt)
    ctx.update("water_jobs", water_job_id, balance_due=new_balance)
    return (f"Payment posted: {amt:.2f} USD by {payment_method} to job {water_job_id}, confirmation {confirmation}, "
            f"payment reference {rid}; balance due now {new_balance:.2f} USD.")


@tool(owner="agent", rw="write")
def book_final_hepa_eb899e1c(ctx: ToolContext, water_job_id: str, service_date: str, square_feet: float,
                             unit_rate: float, amount: float) -> str:
    """Book the final HEPA vacuuming charge on one water mitigation job.

    The desk agent books, on the named water mitigation job, one HEPA vacuuming charge line billed by
    the square foot for the final cleaning of the surfaces the tear-out exposed. On success a new
    charge line with service code hepa_vacuum, unit sqft, the given square feet, rate per square foot
    and amount is added to the job, and the job's balance due rises by the amount. The customer sees
    the line on the job's charge list and the higher balance. The call succeeds when the receipt
    starts with "Booked".

    Args:
        water_job_id: Id class — the reference number of the water mitigation job that was vacuumed, read from the water mitigation job lookup before the call.
        service_date: Fixed-format class — the calendar date the HEPA vacuuming line is dated, written YYYY-MM-DD with no time and no time zone; never empty.
        square_feet: Fixed-format class — the billed square feet, a positive number in the decimal, up to 2 places format, already rounded half up before the call (unit: square foot).
        unit_rate: Fixed-format class — the rate per square foot in USD, a positive amount with exactly 2 decimal places as carried on the job's tier.
        amount: Fixed-format class — the line amount in USD, a positive amount with exactly 2 decimal places, already rounded to the cent half up before the call.

    Returns:
        A text receipt "Booked HEPA vacuuming charge <charge reference> on job <job reference>: <square feet> sq ft at <rate> = <amount> USD; balance due now <balance> USD." where the charge reference is the new line's reference number, the amounts are USD with 2 decimals and the balance is the job's balance due after the line. A text starting with "Error:" means nothing was booked because an argument broke its format.
    """
    if not _Fmt.is_date(service_date):
        return "Error: service_date must be written YYYY-MM-DD."
    if float(square_feet) <= 0 or float(unit_rate) <= 0 or float(amount) <= 0:
        return "Error: square_feet, unit_rate and amount must be positive."
    if not (_Fmt.is_two_place(square_feet) and _Fmt.is_two_place(unit_rate) and _Fmt.is_two_place(amount)):
        return "Error: square_feet, unit_rate and amount must carry at most 2 decimal places."
    jobs = ctx.find("water_jobs", water_job_id=water_job_id)
    if not jobs:
        return f"Error: no water mitigation job {water_job_id}."
    job = jobs[0]
    amt = _Fmt.money(amount)
    rid = ctx.make_id("wch_", water_job_id, service_date, square_feet, unit_rate, amount)
    ctx.create("water_charges", rid, water_charge_id=rid, water_job_id=water_job_id, customer_id=job.get("customer_id"),
               event_type="water_mitigation_service_charge", charge_code="hepa_vacuum", service_date=service_date,
               quantity=_Fmt.money(square_feet), unit="sqft", unit_rate=_Fmt.money(unit_rate), amount=amt)
    new_balance = _Fmt.money(float(job.get("balance_due") or 0) + amt)
    ctx.update("water_jobs", water_job_id, balance_due=new_balance)
    return (f"Booked HEPA vacuuming charge {rid} on job {water_job_id}: {_Fmt.money(square_feet):.2f} sq ft at "
            f"{_Fmt.money(unit_rate):.2f} = {amt:.2f} USD; balance due now {new_balance:.2f} USD.")


@tool(owner="user", rw="write")
def pay_insured_share_cc172b06(ctx: ToolContext, water_job_id: str, payment_method: str, amount: float) -> str:
    """Pay one's own share of an insurance-funded water mitigation job through the secure payment channel.

    The insured customer pays, in person through the company's secure payment channel, their own
    share of their insurance-funded water mitigation job. On success one customer payment is posted
    in full to the named job with the chosen tender, a processor confirmation number is issued, and
    the job's balance due falls by the amount. The customer sees the confirmation number and the new
    balance. The call succeeds when the receipt starts with "Payment posted".

    Args:
        water_job_id: Id class — the reference number of the customer's water mitigation job, as the desk agent reads it from the water mitigation job lookup and gives it to the customer before the payment.
        payment_method: Enum class — the tender the customer pays with, exactly one of: "credit_card" when the customer pays with a credit card; "debit_card" when the customer pays with a debit card; "ach" when the customer pays by bank transfer from a checking or savings account; "check" when the customer pays with a paper or electronic check.
        amount: Fixed-format class — the amount paid in USD, a positive amount with exactly 2 decimal places, already rounded to the cent half up before the call.

    Returns:
        A text receipt "Payment posted: <amount> USD by <tender> to job <job reference>, confirmation <confirmation number>, payment reference <payment reference>; balance due now <balance> USD." where the confirmation number is the processor confirmation issued for this payment, the payment reference is the new payment line's reference number and the balance is the job's balance due after the payment. A text starting with "Error:" means nothing was paid because an argument broke its format.
    """
    allowed = {"credit_card", "debit_card", "ach", "check"}
    if payment_method not in allowed:
        return f"Error: payment_method must be one of {', '.join(sorted(allowed))}."
    if float(amount) <= 0 or not _Fmt.is_two_place(amount):
        return "Error: amount must be positive with exactly 2 decimal places."
    jobs = ctx.find("water_jobs", water_job_id=water_job_id)
    if not jobs:
        return f"Error: no water mitigation job {water_job_id}."
    job = jobs[0]
    amt = _Fmt.money(amount)
    rid = ctx.make_id("wpy_", water_job_id, payment_method, amount)
    confirmation = "IS" + rid[-10:].upper()
    ctx.create("water_payments", rid, water_payment_id=rid, water_job_id=water_job_id, customer_id=job.get("customer_id"),
               event_type="water_customer_payment", payment_method=payment_method, payment_reference=confirmation,
               posted_date=ctx.now()[:10], amount=amt)
    new_balance = _Fmt.money(float(job.get("balance_due") or 0) - amt)
    ctx.update("water_jobs", water_job_id, balance_due=new_balance)
    return (f"Payment posted: {amt:.2f} USD by {payment_method} to job {water_job_id}, confirmation {confirmation}, "
            f"payment reference {rid}; balance due now {new_balance:.2f} USD.")

"""Hidden task tools of the contents_packout_and_storage difficulty (env_0079).

Each tool performs exactly one business write on one contents job and judges no policy:
amounts, periods and tenders are worked out by the agent from the published rules and the
records, and passed in already settled.
"""

from erlbench import ToolContext, tool


class _Ledger:
    """Value formatting shared by the tools (computes no business figure)."""

    @staticmethod
    def half_up(value) -> float:
        from decimal import Decimal, ROUND_HALF_UP
        return float(Decimal(str(value)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP))

    @staticmethod
    def is_date(text) -> bool:
        parts = str(text).split("-")
        if len(parts) != 3 or [len(p) for p in parts] != [4, 2, 2]:
            return False
        if not all(p.isdigit() for p in parts):
            return False
        month, day = int(parts[1]), int(parts[2])
        return 1 <= month <= 12 and 1 <= day <= 31


@tool(owner="agent", rw="write")
def charge_customer_vault_storage_2f9c3128(ctx: ToolContext, contents_job_id: str, claim_file_id: str,
                                           storage_period_start: str, amount: float) -> str:
    """Book the vault storage line of one storage period on a contents job, billed to the customer.

    Adds one vault storage charge for the storage period that begins on the given first day to the
    named contents job, billed to customer, and raises the job's balance due by the same amount. The
    customer can see the new storage line and the higher balance on the job straight away. A second
    call for the same job, period and amount books nothing new: it returns status already_booked with that line's
    id and leaves the balance due unchanged.

    Args:
        contents_job_id: Id class — the reference number of the contents job the storage line belongs to, as returned by the contents job lookup.
        claim_file_id: Id class — the reference number of the insurance claim file the contents job is billed under, as shown on the contents job record; pass "" for a self-pay job, which has none. It is echoed on the receipt.
        storage_period_start: Fixed-format class — the first day of the storage period the line covers, written YYYY-MM-DD (calendar date, no time part).
        amount: Fixed-format class — the line amount in USD, a positive figure rounded to 2 decimal places, half up.

    Returns:
        A receipt with: status ("booked" when the line was added), contents_charge_id (reference
        number of the new storage line), contents_job_id (the job charged), claim_file_id (the claim
        file the job is billed under, "" for a self-pay job), storage_period_start
        (YYYY-MM-DD), bill_to (always "customer"), amount (USD, 2 decimal places) and balance_due (the
        job's balance due after the line, USD, 2 decimal places).
    """
    if not _Ledger.is_date(storage_period_start):
        return "Error: storage_period_start must be a calendar date written YYYY-MM-DD."
    if float(amount) <= 0:
        return "Error: amount must be a positive USD figure."
    rows = ctx.find("contents_jobs", contents_job_id=contents_job_id)
    job = rows[0] if rows else {}
    rid = ctx.make_id("cch_", contents_job_id, storage_period_start, amount)
    if ctx.find("contents_charges", contents_charge_id=rid):
        return str({"status": "already_booked", "contents_charge_id": rid, "contents_job_id": contents_job_id,
                    "amount": _Ledger.half_up(amount), "balance_due": _Ledger.half_up(float(job.get("balance_due") or 0))})
    ctx.create("contents_charges", rid, contents_charge_id=rid, contents_job_id=contents_job_id,
               customer_id=job.get("customer_id"), event_type="contents_storage_charge",
               charge_code="vault_storage", storage_period_start=storage_period_start, bill_to="customer",
               unit="vault", amount=_Ledger.half_up(amount))
    balance = _Ledger.half_up(float(job.get("balance_due") or 0) + _Ledger.half_up(amount))
    ctx.update("contents_jobs", contents_job_id, balance_due=balance)
    return str({"status": "booked", "contents_charge_id": rid, "contents_job_id": contents_job_id,
                "claim_file_id": claim_file_id, "storage_period_start": storage_period_start,
                "bill_to": "customer", "amount": _Ledger.half_up(amount), "balance_due": balance})


@tool(owner="agent", rw="write")
def charge_declared_value_coverage_b3c8ef16(ctx: ToolContext, contents_job_id: str, claim_file_id: str,
                                            storage_period_start: str, amount: float) -> str:
    """Book the declared-value coverage line of one storage period on a contents job.

    Adds one declared-value coverage charge for the storage period that begins on the given first
    day to the named contents job, billed to customer, records the job's declared value on the line
    as its quantity, and raises the job's balance due by the same amount. The customer can see the
    coverage line and the higher balance on the job straight away. A second call for the same job,
    period and amount books nothing new: it returns status already_booked with that line's
    id and leaves the balance due unchanged.

    Args:
        contents_job_id: Id class — the reference number of the contents job the coverage line belongs to, as returned by the contents job lookup.
        claim_file_id: Id class — the reference number of the insurance claim file the contents job is billed under, as shown on the contents job record; pass "" for a self-pay job, which has none. It is echoed on the receipt.
        storage_period_start: Fixed-format class — the first day of the storage period the coverage line covers, written YYYY-MM-DD (calendar date, no time part).
        amount: Fixed-format class — the coverage line amount in USD, a positive figure rounded to 2 decimal places, half up.

    Returns:
        A receipt with: status ("booked" when the line was added), contents_charge_id (reference
        number of the new coverage line), contents_job_id (the job charged), claim_file_id (the claim
        file the job is billed under, "" for a self-pay job), storage_period_start
        (YYYY-MM-DD), bill_to (always "customer"), declared_value (the job's declared value carried
        on the line, USD, 2 decimal places), amount (USD, 2 decimal places) and balance_due (the job's
        balance due after the line, USD, 2 decimal places).
    """
    if not _Ledger.is_date(storage_period_start):
        return "Error: storage_period_start must be a calendar date written YYYY-MM-DD."
    if float(amount) <= 0:
        return "Error: amount must be a positive USD figure."
    rows = ctx.find("contents_jobs", contents_job_id=contents_job_id)
    job = rows[0] if rows else {}
    declared = _Ledger.half_up(float(job.get("declared_value") or 0))
    rid = ctx.make_id("cch_", contents_job_id, storage_period_start, "valuation", amount)
    if ctx.find("contents_charges", contents_charge_id=rid):
        return str({"status": "already_booked", "contents_charge_id": rid, "contents_job_id": contents_job_id,
                    "amount": _Ledger.half_up(amount), "balance_due": _Ledger.half_up(float(job.get("balance_due") or 0))})
    ctx.create("contents_charges", rid, contents_charge_id=rid, contents_job_id=contents_job_id,
               customer_id=job.get("customer_id"), event_type="contents_storage_charge",
               charge_code="valuation_coverage", storage_period_start=storage_period_start,
               bill_to="customer", quantity=declared, unit="each", amount=_Ledger.half_up(amount))
    balance = _Ledger.half_up(float(job.get("balance_due") or 0) + _Ledger.half_up(amount))
    ctx.update("contents_jobs", contents_job_id, balance_due=balance)
    return str({"status": "booked", "contents_charge_id": rid, "contents_job_id": contents_job_id,
                "claim_file_id": claim_file_id, "storage_period_start": storage_period_start,
                "bill_to": "customer", "declared_value": declared, "amount": _Ledger.half_up(amount),
                "balance_due": balance})


@tool(owner="user", rw="write")
def pay_contents_customer_share_24e82212(ctx: ToolContext, contents_job_id: str, payment_method: str,
                                         amount: float, surcharge_amount: float) -> str:
    """Pay toward your own contents job through the company's secure payment channel.

    You, the customer, enter your own card or bank details in the secure payment channel; the payment
    is posted in full to the one contents job named and lowers that job's balance due by the amount
    paid. When you pay by credit card, the credit card surcharge on the payment is booked on the same job
    as its own line at the same moment and raises the balance by that surcharge. The payment channel
    issues a confirmation number at the moment of payment, and the posted payment, any surcharge line and
    the new balance show on the job straight away.

    Args:
        contents_job_id: Id class — the reference number of the contents job being paid, as given to you by the representative from the contents job record.
        payment_method: Enum class — the tender you pay with: credit_card when you pay with a credit card; debit_card when you pay with a debit card drawn on your bank account; ach when you pay by bank transfer from your checking or savings account; check when you pay by a paper or electronic check.
        amount: Fixed-format class — the amount you pay in USD, a positive figure rounded to 2 decimal places, half up.
        surcharge_amount: Fixed-format class — the credit card surcharge on this payment in USD, rounded to 2 decimal places, half up; 0.00 when payment_method is not credit_card, and above zero only for a credit_card payment.

    Returns:
        A receipt with: status ("posted" when the payment went through), contents_payment_id
        (reference number of the posted payment), payment_reference (the confirmation number the
        payment channel issued), contents_job_id (the job paid), payment_method (the tender used),
        posted_date (YYYY-MM-DD), amount (USD, 2 decimal places), surcharge_amount (the surcharge booked
        with the payment, USD, 2 decimal places, 0.00 when none), surcharge_charge_id (reference number of
        the surcharge line, "" when none) and balance_due (the job's balance due after the payment and any
        surcharge, USD, 2 decimal places).
    """
    if payment_method not in ("credit_card", "debit_card", "ach", "check"):
        return "Error: payment_method must be one of credit_card, debit_card, ach or check."
    if float(amount) <= 0:
        return "Error: amount must be a positive USD figure."
    if float(surcharge_amount) < 0 or (payment_method != "credit_card" and float(surcharge_amount) != 0):
        return "Error: surcharge_amount must be 0.00 unless payment_method is credit_card, and never negative."
    rows = ctx.find("contents_jobs", contents_job_id=contents_job_id)
    job = rows[0] if rows else {}
    seq = len(ctx.find("contents_payments", contents_job_id=contents_job_id, event_type="contents_customer_payment"))
    rid = ctx.make_id("cpy_", contents_job_id, payment_method, amount, seq)
    reference = ctx.make_id("CNF-", contents_job_id, payment_method, amount, seq, length=10).upper()
    posted = ctx.now()[:10]
    ctx.create("contents_payments", rid, contents_payment_id=rid, contents_job_id=contents_job_id,
               customer_id=job.get("customer_id"), event_type="contents_customer_payment",
               payment_method=payment_method, payment_reference=reference, posted_date=posted,
               amount=_Ledger.half_up(amount))
    surcharge = _Ledger.half_up(surcharge_amount)
    surcharge_id = ""
    if surcharge > 0:
        surcharge_id = ctx.make_id("cch_", rid, "card_surcharge", surcharge_amount)
        ctx.create("contents_charges", surcharge_id, contents_charge_id=surcharge_id, contents_job_id=contents_job_id,
                   customer_id=job.get("customer_id"), event_type="contents_card_surcharge", charge_code="card_surcharge",
                   source_payment_id=rid, amount=_Ledger.half_up(surcharge_amount))
    balance = _Ledger.half_up(float(job.get("balance_due") or 0) - _Ledger.half_up(amount) + surcharge)
    ctx.update("contents_jobs", contents_job_id, balance_due=balance)
    return str({"status": "posted", "contents_payment_id": rid, "payment_reference": reference,
                "contents_job_id": contents_job_id, "payment_method": payment_method,
                "posted_date": posted, "amount": _Ledger.half_up(amount), "surcharge_amount": surcharge,
                "surcharge_charge_id": surcharge_id, "balance_due": balance})


@tool(owner="agent", rw="write")
def charge_pack_back_boxes_26b5c86b(ctx: ToolContext, contents_job_id: str, service_date: str, amount: float) -> str:
    """Book the pack-back box line of a return on a contents job.

    Adds one move-back charge with charge code pack_back_box, dated the day the boxes were brought back
    and unpacked, to the named contents job, and raises the job's balance due by the same amount. The customer can see the new move-back line and the higher balance on the job straight
    away. A second call for the same job, date and amount books nothing new: it returns status already_booked with that line's
    id and leaves the balance due unchanged.

    Args:
        contents_job_id: Id class — the reference number of the contents job the move-back line belongs to, as returned by the contents job lookup.
        service_date: Fixed-format class — the date the move-back work was performed, written YYYY-MM-DD (calendar date, no time part).
        amount: Fixed-format class — the line amount in USD, a positive figure rounded to 2 decimal places, half up.

    Returns:
        A receipt with: status ("booked" when the line was added), contents_charge_id (reference
        number of the new move-back line), contents_job_id (the job charged), charge_code (always
        "pack_back_box"), service_date (YYYY-MM-DD), amount (USD, 2 decimal places) and balance_due (the job's
        balance due after the line, USD, 2 decimal places).
    """
    if not _Ledger.is_date(service_date):
        return "Error: service_date must be a calendar date written YYYY-MM-DD."
    if float(amount) <= 0:
        return "Error: amount must be a positive USD figure."
    rows = ctx.find("contents_jobs", contents_job_id=contents_job_id)
    job = rows[0] if rows else {}
    rid = ctx.make_id("cch_", contents_job_id, "pack_back_box", service_date, amount)
    if ctx.find("contents_charges", contents_charge_id=rid):
        return str({"status": "already_booked", "contents_charge_id": rid, "contents_job_id": contents_job_id,
                    "amount": _Ledger.half_up(amount), "balance_due": _Ledger.half_up(float(job.get("balance_due") or 0))})
    ctx.create("contents_charges", rid, contents_charge_id=rid, contents_job_id=contents_job_id,
               customer_id=job.get("customer_id"), event_type="contents_pack_back_charge",
               charge_code="pack_back_box", service_date=service_date, amount=_Ledger.half_up(amount))
    balance = _Ledger.half_up(float(job.get("balance_due") or 0) + _Ledger.half_up(amount))
    ctx.update("contents_jobs", contents_job_id, balance_due=balance)
    return str({"status": "booked", "contents_charge_id": rid, "contents_job_id": contents_job_id,
                "charge_code": "pack_back_box", "service_date": service_date,
                "amount": _Ledger.half_up(amount), "balance_due": balance})


@tool(owner="agent", rw="write")
def charge_furniture_reset_9904d302(ctx: ToolContext, contents_job_id: str, service_date: str, amount: float) -> str:
    """Book the furniture reset line of a return on a contents job.

    Adds one move-back charge with charge code furniture_reset, dated the day the furniture and other
    pieces were set back in place, to the named contents job, and raises the job's balance due by the
    same amount. The customer can see the new move-back line and the higher balance on the job straight
    away. A second call for the same job, date and amount books nothing new: it returns status already_booked with that line's
    id and leaves the balance due unchanged.

    Args:
        contents_job_id: Id class — the reference number of the contents job the move-back line belongs to, as returned by the contents job lookup.
        service_date: Fixed-format class — the date the move-back work was performed, written YYYY-MM-DD (calendar date, no time part).
        amount: Fixed-format class — the line amount in USD, a positive figure rounded to 2 decimal places, half up.

    Returns:
        A receipt with: status ("booked" when the line was added), contents_charge_id (reference
        number of the new move-back line), contents_job_id (the job charged), charge_code (always
        "furniture_reset"), service_date (YYYY-MM-DD), amount (USD, 2 decimal places) and balance_due (the job's
        balance due after the line, USD, 2 decimal places).
    """
    if not _Ledger.is_date(service_date):
        return "Error: service_date must be a calendar date written YYYY-MM-DD."
    if float(amount) <= 0:
        return "Error: amount must be a positive USD figure."
    rows = ctx.find("contents_jobs", contents_job_id=contents_job_id)
    job = rows[0] if rows else {}
    rid = ctx.make_id("cch_", contents_job_id, "furniture_reset", service_date, amount)
    if ctx.find("contents_charges", contents_charge_id=rid):
        return str({"status": "already_booked", "contents_charge_id": rid, "contents_job_id": contents_job_id,
                    "amount": _Ledger.half_up(amount), "balance_due": _Ledger.half_up(float(job.get("balance_due") or 0))})
    ctx.create("contents_charges", rid, contents_charge_id=rid, contents_job_id=contents_job_id,
               customer_id=job.get("customer_id"), event_type="contents_pack_back_charge",
               charge_code="furniture_reset", service_date=service_date, amount=_Ledger.half_up(amount))
    balance = _Ledger.half_up(float(job.get("balance_due") or 0) + _Ledger.half_up(amount))
    ctx.update("contents_jobs", contents_job_id, balance_due=balance)
    return str({"status": "booked", "contents_charge_id": rid, "contents_job_id": contents_job_id,
                "charge_code": "furniture_reset", "service_date": service_date,
                "amount": _Ledger.half_up(amount), "balance_due": balance})


@tool(owner="agent", rw="write")
def charge_return_truck_loads_2b0047ce(ctx: ToolContext, contents_job_id: str, service_date: str, amount: float) -> str:
    """Book the truck loads that brought a contents job home as one move-back line.

    Adds one move-back charge with charge code truck_trip, dated the day the loads were delivered, to the
    named contents job, and raises the job's balance due by the same amount. The customer can see the new move-back line and the higher balance on the job straight
    away. A second call for the same job, date and amount books nothing new: it returns status already_booked with that line's
    id and leaves the balance due unchanged.

    Args:
        contents_job_id: Id class — the reference number of the contents job the move-back line belongs to, as returned by the contents job lookup.
        service_date: Fixed-format class — the date the move-back work was performed, written YYYY-MM-DD (calendar date, no time part).
        amount: Fixed-format class — the line amount in USD, a positive figure rounded to 2 decimal places, half up.

    Returns:
        A receipt with: status ("booked" when the line was added), contents_charge_id (reference
        number of the new move-back line), contents_job_id (the job charged), charge_code (always
        "truck_trip"), service_date (YYYY-MM-DD), amount (USD, 2 decimal places) and balance_due (the job's
        balance due after the line, USD, 2 decimal places).
    """
    if not _Ledger.is_date(service_date):
        return "Error: service_date must be a calendar date written YYYY-MM-DD."
    if float(amount) <= 0:
        return "Error: amount must be a positive USD figure."
    rows = ctx.find("contents_jobs", contents_job_id=contents_job_id)
    job = rows[0] if rows else {}
    rid = ctx.make_id("cch_", contents_job_id, "truck_trip", service_date, amount)
    if ctx.find("contents_charges", contents_charge_id=rid):
        return str({"status": "already_booked", "contents_charge_id": rid, "contents_job_id": contents_job_id,
                    "amount": _Ledger.half_up(amount), "balance_due": _Ledger.half_up(float(job.get("balance_due") or 0))})
    ctx.create("contents_charges", rid, contents_charge_id=rid, contents_job_id=contents_job_id,
               customer_id=job.get("customer_id"), event_type="contents_pack_back_charge",
               charge_code="truck_trip", service_date=service_date, amount=_Ledger.half_up(amount))
    balance = _Ledger.half_up(float(job.get("balance_due") or 0) + _Ledger.half_up(amount))
    ctx.update("contents_jobs", contents_job_id, balance_due=balance)
    return str({"status": "booked", "contents_charge_id": rid, "contents_job_id": contents_job_id,
                "charge_code": "truck_trip", "service_date": service_date,
                "amount": _Ledger.half_up(amount), "balance_due": balance})


@tool(owner="user", rw="write")
def pay_contents_closing_balance_f918d993(ctx: ToolContext, contents_job_id: str, payment_method: str,
                                          amount: float, surcharge_amount: float) -> str:
    """Make your closing payment on a contents job whose belongings are home, through the secure payment channel.

    You, the customer, enter your own card or bank details in the secure payment channel; the payment
    is posted in full to the one contents job named and lowers that job's balance due by the amount
    paid. When you pay by credit card, the credit card surcharge on the payment is booked on the same job
    as its own line at the same moment and raises the balance by that surcharge. The payment channel
    issues a confirmation number at the moment of payment, and the posted payment, any surcharge line and
    the new balance show on the job straight away.

    Args:
        contents_job_id: Id class — the reference number of the contents job being paid, as given to you by the representative from the contents job record.
        payment_method: Enum class — the tender you pay with: credit_card when you pay with a credit card; debit_card when you pay with a debit card drawn on your bank account; ach when you pay by bank transfer from your checking or savings account; check when you pay by a paper or electronic check.
        amount: Fixed-format class — the amount you pay in USD, a positive figure rounded to 2 decimal places, half up.
        surcharge_amount: Fixed-format class — the credit card surcharge on this payment in USD, rounded to 2 decimal places, half up; 0.00 when payment_method is not credit_card, and above zero only for a credit_card payment.

    Returns:
        A receipt with: status ("posted" when the payment went through), contents_payment_id
        (reference number of the posted payment), payment_reference (the confirmation number the
        payment channel issued), contents_job_id (the job paid), payment_method (the tender used),
        posted_date (YYYY-MM-DD), amount (USD, 2 decimal places), surcharge_amount (the surcharge booked
        with the payment, USD, 2 decimal places, 0.00 when none), surcharge_charge_id (reference number of
        the surcharge line, "" when none) and balance_due (the job's balance due after the payment and any
        surcharge, USD, 2 decimal places).
    """
    if payment_method not in ("credit_card", "debit_card", "ach", "check"):
        return "Error: payment_method must be one of credit_card, debit_card, ach or check."
    if float(amount) <= 0:
        return "Error: amount must be a positive USD figure."
    if float(surcharge_amount) < 0 or (payment_method != "credit_card" and float(surcharge_amount) != 0):
        return "Error: surcharge_amount must be 0.00 unless payment_method is credit_card, and never negative."
    rows = ctx.find("contents_jobs", contents_job_id=contents_job_id)
    job = rows[0] if rows else {}
    seq = len(ctx.find("contents_payments", contents_job_id=contents_job_id, event_type="contents_customer_payment"))
    rid = ctx.make_id("cpy_", contents_job_id, "closing", payment_method, amount, seq)
    reference = ctx.make_id("CNF-", contents_job_id, "closing", payment_method, amount, seq, length=10).upper()
    posted = ctx.now()[:10]
    ctx.create("contents_payments", rid, contents_payment_id=rid, contents_job_id=contents_job_id,
               customer_id=job.get("customer_id"), event_type="contents_customer_payment",
               payment_method=payment_method, payment_reference=reference, posted_date=posted,
               amount=_Ledger.half_up(amount))
    surcharge = _Ledger.half_up(surcharge_amount)
    surcharge_id = ""
    if surcharge > 0:
        surcharge_id = ctx.make_id("cch_", rid, "card_surcharge", surcharge_amount)
        ctx.create("contents_charges", surcharge_id, contents_charge_id=surcharge_id, contents_job_id=contents_job_id,
                   customer_id=job.get("customer_id"), event_type="contents_card_surcharge", charge_code="card_surcharge",
                   source_payment_id=rid, amount=_Ledger.half_up(surcharge_amount))
    balance = _Ledger.half_up(float(job.get("balance_due") or 0) - _Ledger.half_up(amount) + surcharge)
    ctx.update("contents_jobs", contents_job_id, balance_due=balance)
    return str({"status": "posted", "contents_payment_id": rid, "payment_reference": reference,
                "contents_job_id": contents_job_id, "payment_method": payment_method,
                "posted_date": posted, "amount": _Ledger.half_up(amount), "surcharge_amount": surcharge,
                "surcharge_charge_id": surcharge_id, "balance_due": balance})

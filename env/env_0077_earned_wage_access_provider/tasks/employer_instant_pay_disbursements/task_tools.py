"""Hidden task tools of the employer_instant_pay_disbursements difficulty (category disburse).

Each tool performs one booking on an employer's Paystride Instant Pay Disbursement service with the
values the desk has already worked out; none of them judges eligibility or computes an amount.
"""

from decimal import Decimal, ROUND_HALF_UP

from erlbench import ToolContext, tool


class _Money:
    """Exact half-up rounding of US dollar amounts to the cent."""

    @staticmethod
    def cents(value) -> float:
        return float(Decimal(str(value)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP))


@tool(owner="agent", rw="write")
def book_closing_month_fee_4be79540(ctx: ToolContext, disburse_service_id: str, fee_type: str, related_entry_id: str,
                                    amount: float) -> str:
    """Debit the platform fee for the current calendar month from an employer's Instant Pay
    Disbursement service as the fee of the month in which the service is closing. One call books one
    platform fee entry for the current month on the service's ledger, pointing to no other entry, and
    lowers the service's prefund balance by the amount; the employer sees the fee on its ledger at
    once. An amount that is not greater than zero, or a fee kind or source other than those
    described below, books nothing and is reported back.

    Args:
        disburse_service_id: Id class — the reference number of the employer's Instant Pay
            Disbursement service, read from the service record returned by the service lookup.
        fee_type: Enum class — monthly_platform — the platform fee of the month in which the
            service is closing, the only kind of fee this tool books.
        related_entry_id: Id class — the reference number of the ledger entry the fee arises
            from; a closing-month platform fee arises from no ledger entry, so it is passed as an
            empty string.
        amount: Fixed-format class — the platform fee to debit for the current month, in US dollars
            as a positive number with exactly 2 decimal places (cents); a value with more decimals
            is rounded half up to the cent before booking.

    Returns:
        A one-line confirmation string naming the new ledger entry reference (text), the service
        reference (text), the billing month (YYYY-MM, the current month), the amount debited (USD,
        two decimals) and the prefund balance after the debit (USD, two decimals); the entry
        reference being present means the fee was booked. A message beginning with "Not booked"
        means the amount, fee kind or source was not accepted and nothing changed.
    """
    fee = _Money.cents(amount)
    if fee_type != "monthly_platform" or (related_entry_id or "") != "":
        return (f"Not booked: this tool books only a monthly_platform fee arising from no ledger entry "
                f"(got {fee_type!r}, {related_entry_id!r}); nothing changed.")
    if fee <= 0:
        return f"Not booked: the amount {fee:.2f} is not greater than zero; nothing changed."
    today = ctx.now()[:10]
    month = today[:7]
    svc = (ctx.find("disburse_services", disburse_service_id=disburse_service_id) or [{}])[0]
    rid = ctx.make_id("dfee_", disburse_service_id, "monthly_platform", month, fee)
    ctx.create("disburse_ledger", rid, disburse_entry_id=rid, disburse_service_id=disburse_service_id,
               customer_id=svc.get("customer_id"), event_type="disburse_fee", entry_date=today,
               amount=fee, fee_type="monthly_platform", billing_month=month, related_entry_id=None,
               disbursement_type="none", destination_type="none", funding_method="none",
               deposit_source="none", credit_reason="none", return_reason="none")
    balance = _Money.cents(float(svc.get("prefund_balance") or 0) - fee)
    ctx.update("disburse_services", disburse_service_id, prefund_balance=balance)
    return (f"Platform fee entry {rid} booked on service {disburse_service_id} for billing month {month}: "
            f"{fee:.2f} USD debited; prefund balance now {balance:.2f} USD.")


@tool(owner="user", rw="write")
def confirm_service_closure_f3d256bb(ctx: ToolContext, disburse_service_id: str, disburse_request_id: str,
                                     early_closure_fee: float) -> str:
    """The employer's authorized contact confirms, in person, the closure of the employer's Instant Pay
    Disbursement service against its pending service-closure request. One call sets the service's
    status to closed with today's date as its closing date, marks that closure request confirmed, and
    debits the early closure fee quoted by the desk from the prefund balance as an early-closure fee
    entry; when the fee given is zero no fee entry is booked. After the call the employer sees the
    service closed, payouts stopped and any fee on its ledger.

    Args:
        disburse_service_id: Id class — the reference number of the employer's Instant Pay
            Disbursement service, as read to the employer by the desk from the service record.
        disburse_request_id: Id class — the reference number of the employer's pending
            service-closure request, as read to the employer by the desk from the request record.
        early_closure_fee: Fixed-format class — the early closure fee the desk quoted, in US dollars
            as a number with exactly 2 decimal places (cents), zero or greater; a value with more
            decimals is rounded half up to the cent before booking.

    Returns:
        A one-line confirmation string naming the service reference (text), its new status (closed),
        the closing date (YYYY-MM-DD), the closure request reference (text) with its new status
        (confirmed), the fee entry reference (text, or "none" when the fee was zero), the fee debited
        (USD, two decimals) and the prefund balance after the debit (USD, two decimals); the status
        closed being reported means the closure took effect. A message beginning with "Not
        confirmed" means the fee given was below zero and nothing changed.
    """
    fee = _Money.cents(early_closure_fee)
    if fee < 0:
        return f"Not confirmed: the early closure fee {fee:.2f} is below zero; nothing changed."
    today = ctx.now()[:10]
    svc = (ctx.find("disburse_services", disburse_service_id=disburse_service_id) or [{}])[0]
    ctx.update("disburse_services", disburse_service_id, status="closed", closed_date=today)
    ctx.update("disburse_requests", disburse_request_id, request_status="confirmed")
    balance = _Money.cents(float(svc.get("prefund_balance") or 0))
    entry = "none"
    if fee > 0:
        entry = ctx.make_id("dfee_", disburse_service_id, "early_closure", disburse_request_id, fee)
        ctx.create("disburse_ledger", entry, disburse_entry_id=entry, disburse_service_id=disburse_service_id,
                   customer_id=svc.get("customer_id"), event_type="disburse_fee", entry_date=today,
                   amount=fee, fee_type="early_closure", billing_month=None, related_entry_id=None,
                   disbursement_type="none", destination_type="none", funding_method="none",
                   deposit_source="none", credit_reason="none", return_reason="none")
        balance = _Money.cents(balance - fee)
        ctx.update("disburse_services", disburse_service_id, prefund_balance=balance)
    return (f"Service {disburse_service_id} status closed, closing date {today}; closure request "
            f"{disburse_request_id} confirmed; early closure fee entry {entry}: {fee:.2f} USD debited; "
            f"prefund balance now {balance:.2f} USD.")


@tool(owner="agent", rw="write")
def debit_platform_fee_9215b300(ctx: ToolContext, disburse_service_id: str, fee_type: str, related_entry_id: str,
                                amount: float) -> str:
    """Debit the platform fee of the calendar month before the current one from an employer's Instant
    Pay Disbursement service, as the fee of that completed billing month. One call books one platform
    fee entry for that billing month on the service's ledger, pointing to no other entry, and lowers
    the service's prefund balance by the amount; the employer sees the fee on its ledger at once. An
    amount that is not greater than zero, or a fee kind or source other than those described below,
    books nothing and is reported back.

    Args:
        disburse_service_id: Id class — the reference number of the employer's Instant Pay
            Disbursement service, read from the service record returned by the service lookup.
        fee_type: Enum class — monthly_platform — the platform fee of a completed billing month, the
            only kind of fee this tool books.
        related_entry_id: Id class — the reference number of the ledger entry the fee arises from; a
            platform fee arises from no ledger entry, so it is passed as an empty string.
        amount: Fixed-format class — the platform fee to debit for the completed month, in US dollars
            as a positive number with exactly 2 decimal places (cents); a value with more decimals
            is rounded half up to the cent before booking.

    Returns:
        A one-line confirmation string naming the new ledger entry reference (text), the service
        reference (text), the billing month (YYYY-MM, the month before the current one), the amount
        debited (USD, two decimals) and the prefund balance after the debit (USD, two decimals); the
        entry reference being present means the fee was booked. A message beginning with "Not
        booked" means the amount, fee kind or source was not accepted and nothing changed.
    """
    fee = _Money.cents(amount)
    if fee_type != "monthly_platform" or (related_entry_id or "") != "":
        return (f"Not booked: this tool books only a monthly_platform fee arising from no ledger entry "
                f"(got {fee_type!r}, {related_entry_id!r}); nothing changed.")
    if fee <= 0:
        return f"Not booked: the amount {fee:.2f} is not greater than zero; nothing changed."
    today = ctx.now()[:10]
    year, month = int(today[:4]), int(today[5:7])
    year, month = (year - 1, 12) if month == 1 else (year, month - 1)
    billing_month = f"{year:04d}-{month:02d}"
    svc = (ctx.find("disburse_services", disburse_service_id=disburse_service_id) or [{}])[0]
    rid = ctx.make_id("dfee_", disburse_service_id, "monthly_platform", billing_month, fee)
    ctx.create("disburse_ledger", rid, disburse_entry_id=rid, disburse_service_id=disburse_service_id,
               customer_id=svc.get("customer_id"), event_type="disburse_fee", entry_date=today,
               amount=fee, fee_type="monthly_platform", billing_month=billing_month, related_entry_id=None,
               disbursement_type="none", destination_type="none", funding_method="none",
               deposit_source="none", credit_reason="none", return_reason="none")
    balance = _Money.cents(float(svc.get("prefund_balance") or 0) - fee)
    ctx.update("disburse_services", disburse_service_id, prefund_balance=balance)
    return (f"Platform fee entry {rid} booked on service {disburse_service_id} for billing month {billing_month}: "
            f"{fee:.2f} USD debited; prefund balance now {balance:.2f} USD.")


@tool(owner="user", rw="write")
def confirm_alert_level_1c610295(ctx: ToolContext, disburse_service_id: str, low_balance_alert_usd: float) -> str:
    """The employer's authorized contact confirms, in person, the low-balance alert level of the
    employer's Instant Pay Disbursement service, the balance below which automatic replenishment
    debits are pulled from the employer's bank account. One call records the confirmed amount as the
    service's alert level on file and leaves the funding method and the automatic replenishment
    setting as they are; the employer sees the new alert level on its service at once.

    Args:
        disburse_service_id: Id class — the reference number of the employer's Instant Pay
            Disbursement service, as read to the employer by the desk from the service record.
        low_balance_alert_usd: Fixed-format class — the alert level the employer confirms, in US
            dollars as a positive number with exactly 2 decimal places (cents); a value with more
            decimals is rounded half up to the cent before it is recorded.

    Returns:
        A one-line confirmation string naming the service reference (text), the previous alert level
        (USD, two decimals) and the alert level now on file (USD, two decimals); the new alert level
        being reported means the election was recorded. A message beginning with "Not recorded"
        means the amount was not greater than zero and nothing changed.
    """
    level = _Money.cents(low_balance_alert_usd)
    if level <= 0:
        return f"Not recorded: the alert level {level:.2f} is not greater than zero; nothing changed."
    svc = (ctx.find("disburse_services", disburse_service_id=disburse_service_id) or [{}])[0]
    previous = _Money.cents(float(svc.get("low_balance_alert_usd") or 0))
    ctx.update("disburse_services", disburse_service_id, low_balance_alert_usd=level)
    return (f"Service {disburse_service_id}: alert level changed from {previous:.2f} USD to {level:.2f} USD "
            f"on file.")


@tool(owner="agent", rw="write")
def book_replenishment_debit_b3fe8e59(ctx: ToolContext, disburse_service_id: str, amount: float) -> str:
    """Pull an automatic replenishment debit from the employer's bank account under its standing
    authorization for an Instant Pay Disbursement service. One call books one prefund deposit dated
    today, made by ACH debit and marked as an automatic replenishment, and raises the service's
    prefund balance by the amount; the employer sees the debit on its ledger at once, and the money
    can be paid out once the tier's ACH availability period has passed.

    Args:
        disburse_service_id: Id class — the reference number of the employer's Instant Pay
            Disbursement service, read from the service record returned by the service lookup.
        amount: Fixed-format class — the amount to debit, in US dollars as a positive number with
            exactly 2 decimal places (cents); a value with more decimals is rounded half up to the
            cent before booking.

    Returns:
        A one-line confirmation string naming the new ledger entry reference (text), the service
        reference (text), the entry date (YYYY-MM-DD), the ordinal of the deposit among the
        service's deposits booked that day (integer), the amount debited (USD, two decimals) and
        the prefund balance after the debit (USD, two decimals); the entry reference being present
        means the debit was booked. A message beginning with "Not booked" means the amount was not
        greater than zero and nothing changed.
    """
    value = _Money.cents(amount)
    if value <= 0:
        return f"Not booked: the amount {value:.2f} is not greater than zero; nothing changed."
    today = ctx.now()[:10]
    svc = (ctx.find("disburse_services", disburse_service_id=disburse_service_id) or [{}])[0]
    sequence = 1 + len(ctx.find("disburse_ledger", disburse_service_id=disburse_service_id,
                                event_type="disburse_prefund_deposit", entry_date=today))
    rid = ctx.make_id("ddep_", disburse_service_id, "auto_replenish", today, sequence, value)
    ctx.create("disburse_ledger", rid, disburse_entry_id=rid, disburse_service_id=disburse_service_id,
               customer_id=svc.get("customer_id"), event_type="disburse_prefund_deposit", entry_date=today,
               amount=value, daily_sequence=sequence, funding_method="ach_debit_authorization",
               deposit_source="auto_replenish", disbursement_type="none", destination_type="none",
               fee_type="none", credit_reason="none", return_reason="none", related_entry_id=None)
    balance = _Money.cents(float(svc.get("prefund_balance") or 0) + value)
    ctx.update("disburse_services", disburse_service_id, prefund_balance=balance)
    return (f"Replenishment debit {rid} booked on service {disburse_service_id} on {today} (deposit {sequence} of "
            f"the day): {value:.2f} USD; prefund balance now {balance:.2f} USD.")


@tool(owner="user", rw="write")
def send_prefund_ach_credit_62da4f1e(ctx: ToolContext, disburse_service_id: str, amount: float) -> str:
    """The employer's authorized contact sends, from the employer's own bank account, an ACH credit
    that prefunds the employer's Instant Pay Disbursement service. One call books one prefund deposit
    dated today, made by employer ACH credit and marked as sent by the employer, and raises the
    service's prefund balance by the amount; the employer sees the deposit on its ledger at once, and
    the money can be paid out once the tier's ACH availability period has passed.

    Args:
        disburse_service_id: Id class — the reference number of the employer's Instant Pay
            Disbursement service, as read to the employer by the desk from the service record.
        amount: Fixed-format class — the amount the employer sends, in US dollars as a positive
            number with exactly 2 decimal places (cents); a value with more decimals is rounded half
            up to the cent before booking.

    Returns:
        A one-line confirmation string naming the new ledger entry reference (text), the service
        reference (text), the entry date (YYYY-MM-DD), the ordinal of the deposit among the
        service's deposits booked that day (integer), the amount credited (USD, two decimals) and
        the prefund balance after the credit (USD, two decimals); the entry reference being present
        means the deposit was booked. A message beginning with "Not booked" means the amount was
        not greater than zero and nothing changed.
    """
    value = _Money.cents(amount)
    if value <= 0:
        return f"Not booked: the amount {value:.2f} is not greater than zero; nothing changed."
    today = ctx.now()[:10]
    svc = (ctx.find("disburse_services", disburse_service_id=disburse_service_id) or [{}])[0]
    sequence = 1 + len(ctx.find("disburse_ledger", disburse_service_id=disburse_service_id,
                                event_type="disburse_prefund_deposit", entry_date=today))
    rid = ctx.make_id("ddep_", disburse_service_id, "employer_initiated", today, sequence, value)
    ctx.create("disburse_ledger", rid, disburse_entry_id=rid, disburse_service_id=disburse_service_id,
               customer_id=svc.get("customer_id"), event_type="disburse_prefund_deposit", entry_date=today,
               amount=value, daily_sequence=sequence, funding_method="employer_ach_credit",
               deposit_source="employer_initiated", disbursement_type="none", destination_type="none",
               fee_type="none", credit_reason="none", return_reason="none", related_entry_id=None)
    balance = _Money.cents(float(svc.get("prefund_balance") or 0) + value)
    ctx.update("disburse_services", disburse_service_id, prefund_balance=balance)
    return (f"Employer ACH credit {rid} booked on service {disburse_service_id} on {today} (deposit {sequence} of "
            f"the day): {value:.2f} USD; prefund balance now {balance:.2f} USD.")

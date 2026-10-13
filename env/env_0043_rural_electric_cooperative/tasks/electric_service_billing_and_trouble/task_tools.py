"""Hidden task tools for the electric_service_billing_and_trouble difficulty of Cedar Fork Electric
Cooperative. Each tool lands exactly one business write on one electric service account with the values
the agent has already worked out from the knowledge base and the records; no tool judges eligibility,
computes an amount or checks whether anything else has been done."""

from erlbench import ToolContext, tool


# Reads the account row a write lands on (the member reference and the current balance).
_account = lambda ctx, service_account_id: (ctx.find("service_accounts", service_account_id=service_account_id) or [{}])[0]


@tool(owner="agent", rw="write")
def assess_late_charge_b4948c69(ctx: ToolContext, service_account_id: str, billing_period: str,
                                late_charge_amount: float) -> str:
    """Assess the late payment charge on one bill of a member's electric service account. One call adds
    a single late payment charge line for the named billing period to the account, dated today, and raises
    the account's current balance by the charge, so the member sees the charge on the account right away
    and on the next bill. The call succeeds when the receipt below is returned.

    Args:
        service_account_id: Id class — the reference number of the electric service account (one metered location) whose bill is charged, as shown by the service account lookup.
        billing_period: Fixed-format class — the billing period of the bill the charge is assessed on, written YYYY-MM (the month whose meter read closes the period), exactly as printed on that bill's lines.
        late_charge_amount: Fixed-format class — the late payment charge in USD, a positive amount with 2 decimal places, already rounded to the cent.

    Returns:
        A dictionary rendered as text with: charge_id (the reference number of the new late payment charge line), service_account_id (the account charged), billing_period (YYYY-MM of the bill charged), amount (the charge booked, USD with 2 decimal places), charge_date (YYYY-MM-DD, today), account_balance (the account's new balance, USD with 2 decimal places) and status ("assessed", meaning the charge is now on the account).
    """
    acct = _account(ctx, service_account_id)
    amount = round(float(late_charge_amount), 2)
    rid = ctx.make_id("lc_", service_account_id, billing_period, amount)
    today = ctx.now()[:10]
    ctx.create("service_charges", rid, charge_id=rid, service_account_id=service_account_id,
               customer_id=acct.get("customer_id"), event_type="service_late_charge",
               billing_period=billing_period, charge_component="late_payment_charge", charge_date=today,
               kwh=0, metered_kw=0.0, billed_kw=0.0, amount=amount, credit_reason="", source_reference_id="")
    balance = round(float(acct.get("account_balance") or 0) + amount, 2)
    ctx.update("service_accounts", service_account_id, account_balance=balance)
    return str({"charge_id": rid, "service_account_id": service_account_id, "billing_period": billing_period,
                "amount": amount, "charge_date": today, "account_balance": balance, "status": "assessed"})


@tool(owner="agent", rw="write")
def post_meter_error_credit_d380ee62(ctx: ToolContext, service_account_id: str, source_reference_id: str,
                                     credit_reason: str, refund_amount: float) -> str:
    """Post the bill credit that settles a member-requested meter test on an electric service account. One
    call adds a single bill credit, dated today, that names the meter test it comes from and the reason for
    the credit, and lowers the account's current balance by the credited amount; the member sees the credit
    on the account at once and on the next bill. The call succeeds when the receipt below is returned.

    Args:
        service_account_id: Id class — the reference number of the electric service account (one metered location) being credited, as shown by the service account lookup.
        source_reference_id: Id class — the reference number of the meter test record the credit settles, as shown by the trouble report and meter test lookup for the same account.
        credit_reason: Enum class — why the credit is given, one of: deposit_refund (a security deposit returned to the bill); deposit_application (a held deposit applied against the balance); deposit_interest (interest earned on a deposit paid out to the bill); capital_credit_retirement (retired capital credits paid as a bill credit); capital_credit_offset (capital credits offset against an unpaid balance); arrears_to_prepay (a past-due amount moved onto a PrePay Power enrollment); prepay_balance_transfer (a remaining prepaid balance moved back to the bill); arrears_to_arrangement (a past-due amount moved into a payment arrangement); late_charge_waiver (a courtesy waiver of one late payment charge); meter_error_refund (money returned because a tested meter was found registering fast); billing_error_correction (a line billed at the wrong schedule or quantity corrected); area_light_outage_credit (credit for an area light that stayed out).
        refund_amount: Fixed-format class — the credit in USD, a positive amount with 2 decimal places, already rounded to the cent.

    Returns:
        A dictionary rendered as text with: charge_id (the reference number of the new bill credit), service_account_id (the account credited), source_reference_id (the meter test the credit settles), credit_reason (the reason recorded), amount (the credit booked, USD with 2 decimal places), charge_date (YYYY-MM-DD, today), account_balance (the account's new balance, USD with 2 decimal places) and status ("credited", meaning the credit is now on the account).
    """
    acct = _account(ctx, service_account_id)
    amount = round(float(refund_amount), 2)
    rid = ctx.make_id("bc_", service_account_id, source_reference_id, credit_reason, amount)
    today = ctx.now()[:10]
    ctx.create("service_charges", rid, charge_id=rid, service_account_id=service_account_id,
               customer_id=acct.get("customer_id"), event_type="service_bill_credit",
               billing_period=today[:7], charge_component="bill_credit", charge_date=today,
               kwh=0, metered_kw=0.0, billed_kw=0.0, amount=amount, credit_reason=credit_reason,
               source_reference_id=source_reference_id)
    balance = round(float(acct.get("account_balance") or 0) - amount, 2)
    ctx.update("service_accounts", service_account_id, account_balance=balance)
    return str({"charge_id": rid, "service_account_id": service_account_id,
                "source_reference_id": source_reference_id, "credit_reason": credit_reason, "amount": amount,
                "charge_date": today, "account_balance": balance, "status": "credited"})


@tool(owner="user", rw="write")
def pay_reconnection_amount_66e1876e(ctx: ToolContext, service_account_id: str, payment_amount: float) -> str:
    """Make your own card payment toward getting power restored on your electric service account that stands
    disconnected for nonpayment, through the cooperative's automated phone payment line; it is not the line
    for an idle seasonal or irrigation account or for an account in service. One call posts a single card
    payment, dated today, to the disconnected account and lowers the account's current balance by the amount
    paid; the payment line reads back a confirmation number you can keep. The call succeeds when the receipt
    below is returned.

    Args:
        service_account_id: Id class — the reference number of the disconnected electric service account (one metered location) you are paying, as the representative reads it to you from the service account lookup.
        payment_amount: Fixed-format class — the amount you pay in USD, a positive amount with 2 decimal places, exactly as the representative quotes it.

    Returns:
        A dictionary rendered as text with: payment_id (the reference number of the posted payment), service_account_id (the account paid), amount (the amount posted, USD with 2 decimal places), payment_date (YYYY-MM-DD, today), payment_channel (always phone_ivr_card, the automated phone card line), payment_reference (the eight-digit confirmation number the payment line issues), account_balance (the account's new balance, USD with 2 decimal places) and status ("posted", meaning the payment is on the account).
    """
    acct = _account(ctx, service_account_id)
    amount = round(float(payment_amount), 2)
    rid = ctx.make_id("pay_", service_account_id, amount)
    reference = "41" + str(int(rid[-8:], 16) % 1000000).zfill(6)
    today = ctx.now()[:10]
    ctx.create("service_payments", rid, payment_id=rid, service_account_id=service_account_id,
               customer_id=acct.get("customer_id"), event_type="service_payment", payment_date=today,
               payment_channel="phone_ivr_card", amount=amount, payment_reference=reference,
               original_payment_id="", return_reason="", assistance_agency="")
    balance = round(float(acct.get("account_balance") or 0) - amount, 2)
    ctx.update("service_accounts", service_account_id, account_balance=balance)
    return str({"payment_id": rid, "service_account_id": service_account_id, "amount": amount,
                "payment_date": today, "payment_channel": "phone_ivr_card", "payment_reference": reference,
                "account_balance": balance, "status": "posted"})


@tool(owner="agent", rw="write")
def reconnect_service_ea86e786(ctx: ToolContext, service_account_id: str, reconnect_fee_amount: float) -> str:
    """Reconnect an electric service account that was disconnected for nonpayment and bill its reconnect
    fee. One call returns the account to active service, clears the disconnect date, the disconnect notice
    date and the past-due amount the notice demanded, adds a single reconnect fee line dated today, and raises
    the account's current balance by that fee; the member's power is restored and the fee appears on the next
    bill. The call succeeds when the receipt below is returned.

    Args:
        service_account_id: Id class — the reference number of the electric service account (one metered location) being reconnected, as shown by the service account lookup.
        reconnect_fee_amount: Fixed-format class — the reconnect fee in USD, a positive amount with 2 decimal places, already rounded to the cent.

    Returns:
        A dictionary rendered as text with: charge_id (the reference number of the reconnect fee line), service_account_id (the account reconnected), status (always "active", the account's new state), amount (the reconnect fee booked, USD with 2 decimal places), charge_date (YYYY-MM-DD, today) and account_balance (the account's new balance, USD with 2 decimal places).
    """
    acct = _account(ctx, service_account_id)
    amount = round(float(reconnect_fee_amount), 2)
    rid = ctx.make_id("rcf_", service_account_id, amount)
    today = ctx.now()[:10]
    ctx.create("service_charges", rid, charge_id=rid, service_account_id=service_account_id,
               customer_id=acct.get("customer_id"), event_type="service_fee", billing_period=today[:7],
               charge_component="reconnect_fee", charge_date=today, kwh=0, metered_kw=0.0, billed_kw=0.0,
               amount=amount, credit_reason="", source_reference_id=service_account_id)
    balance = round(float(acct.get("account_balance") or 0) + amount, 2)
    ctx.update("service_accounts", service_account_id, status="active", disconnect_date="",
               disconnect_notice_date="", disconnect_past_due_amount=0.0, account_balance=balance)
    return str({"charge_id": rid, "service_account_id": service_account_id, "status": "active",
                "amount": amount, "charge_date": today, "account_balance": balance})


@tool(owner="agent", rw="write")
def bill_seasonal_minimum_25412e46(ctx: ToolContext, service_account_id: str, adjustment_amount: float) -> str:
    """Bill the seasonal minimum settlement of an irrigation service account. One call adds a single
    annual minimum adjustment line, dated today and placed on the bill of the current month, to the account
    and raises the account's current balance by it, so the member sees the adjustment on the account at once
    and on that bill. The call succeeds when the receipt below is returned.

    Args:
        service_account_id: Id class — the reference number of the electric service account (one metered location) the adjustment is billed on, as shown by the service account lookup.
        adjustment_amount: Fixed-format class — the minimum adjustment in USD, a positive amount with 2 decimal places, already rounded to the cent.

    Returns:
        A dictionary rendered as text with: charge_id (the reference number of the new adjustment line), service_account_id (the account billed), billing_period (YYYY-MM, the current month's bill), amount (the adjustment booked, USD with 2 decimal places), charge_date (YYYY-MM-DD, today), account_balance (the account's new balance, USD with 2 decimal places) and status ("billed", meaning the adjustment is now on the account).
    """
    acct = _account(ctx, service_account_id)
    amount = round(float(adjustment_amount), 2)
    rid = ctx.make_id("amin_", service_account_id, amount)
    today = ctx.now()[:10]
    ctx.create("service_charges", rid, charge_id=rid, service_account_id=service_account_id,
               customer_id=acct.get("customer_id"), event_type="service_usage_charge", billing_period=today[:7],
               charge_component="annual_minimum_adjustment", charge_date=today, kwh=0, metered_kw=0.0, billed_kw=0.0,
               amount=amount, credit_reason="", source_reference_id="")
    balance = round(float(acct.get("account_balance") or 0) + amount, 2)
    ctx.update("service_accounts", service_account_id, account_balance=balance)
    return str({"charge_id": rid, "service_account_id": service_account_id, "billing_period": today[:7],
                "amount": amount, "charge_date": today, "account_balance": balance, "status": "billed"})


@tool(owner="user", rw="write")
def pay_restore_balance_91f3e2ab(ctx: ToolContext, service_account_id: str, payment_amount: float) -> str:
    """Pay toward your idle seasonal or irrigation service account yourself, by card, on the cooperative's
    automated phone payment line; it is not the line for an account disconnected for nonpayment or for an
    account in service. One call posts a single card payment, dated today, to the account and lowers
    the account's current balance by the amount paid; the line reads back a confirmation number for you to
    keep. The call succeeds when the receipt below is returned.

    Args:
        service_account_id: Id class — the reference number of the idle electric service account (one metered location) you are paying, as the representative reads it to you from the service account lookup.
        payment_amount: Fixed-format class — the amount you pay in USD, a positive amount with 2 decimal places, exactly as the representative quotes it.

    Returns:
        A dictionary rendered as text with: payment_id (the reference number of the posted payment), service_account_id (the account paid), amount (the amount posted, USD with 2 decimal places), payment_date (YYYY-MM-DD, today), payment_channel (always phone_ivr_card, the automated phone card line), payment_reference (the eight-digit confirmation number the line issues), account_balance (the account's new balance, USD with 2 decimal places) and status ("posted", meaning the payment is on the account).
    """
    acct = _account(ctx, service_account_id)
    amount = round(float(payment_amount), 2)
    rid = ctx.make_id("rpay_", service_account_id, amount)
    reference = "41" + str(int(rid[-8:], 16) % 1000000).zfill(6)
    today = ctx.now()[:10]
    ctx.create("service_payments", rid, payment_id=rid, service_account_id=service_account_id,
               customer_id=acct.get("customer_id"), event_type="service_payment", payment_date=today,
               payment_channel="phone_ivr_card", amount=amount, payment_reference=reference,
               original_payment_id="", return_reason="", assistance_agency="")
    balance = round(float(acct.get("account_balance") or 0) - amount, 2)
    ctx.update("service_accounts", service_account_id, account_balance=balance)
    return str({"payment_id": rid, "service_account_id": service_account_id, "amount": amount,
                "payment_date": today, "payment_channel": "phone_ivr_card", "payment_reference": reference,
                "account_balance": balance, "status": "posted"})


@tool(owner="agent", rw="write")
def restore_seasonal_service_78495a78(ctx: ToolContext, service_account_id: str, service_order_id: str,
                                      restore_fee_amount: float) -> str:
    """Carry out a member's confirmed seasonal restore order on an idle service account. One call returns
    the account to active service and clears its idle date, marks the restore order completed, adds a single
    seasonal restore fee line dated today, and raises the account's current balance by that fee; the meter is
    re-energized and the fee appears on the next bill. The call succeeds when the receipt below is returned.

    Args:
        service_account_id: Id class — the reference number of the idle electric service account (one metered location) being restored, as shown by the service account lookup.
        service_order_id: Id class — the reference number of the member's seasonal restore order for that account, as shown by the service order lookup.
        restore_fee_amount: Fixed-format class — the seasonal restore fee in USD, a positive amount with 2 decimal places, already rounded to the cent.

    Returns:
        A dictionary rendered as text with: charge_id (the reference number of the restore fee line), service_account_id (the account restored), service_order_id (the order carried out), status (always "active", the account's new state), order_status (always "completed"), amount (the restore fee booked, USD with 2 decimal places), charge_date (YYYY-MM-DD, today) and account_balance (the account's new balance, USD with 2 decimal places).
    """
    acct = _account(ctx, service_account_id)
    amount = round(float(restore_fee_amount), 2)
    rid = ctx.make_id("rsf_", service_account_id, service_order_id, amount)
    today = ctx.now()[:10]
    ctx.create("service_charges", rid, charge_id=rid, service_account_id=service_account_id,
               customer_id=acct.get("customer_id"), event_type="service_fee", billing_period=today[:7],
               charge_component="seasonal_restore_fee", charge_date=today, kwh=0, metered_kw=0.0, billed_kw=0.0,
               amount=amount, credit_reason="", source_reference_id=service_account_id)
    balance = round(float(acct.get("account_balance") or 0) + amount, 2)
    ctx.update("service_accounts", service_account_id, status="active", idle_date="", account_balance=balance)
    ctx.update("service_orders", service_order_id, order_status="completed")
    return str({"charge_id": rid, "service_account_id": service_account_id, "service_order_id": service_order_id,
                "status": "active", "order_status": "completed", "amount": amount, "charge_date": today,
                "account_balance": balance})

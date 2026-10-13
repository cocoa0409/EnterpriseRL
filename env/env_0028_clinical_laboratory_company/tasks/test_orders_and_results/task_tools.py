"""Hidden task tools of the test_orders_and_results difficulty (category: orders).

Each tool is reached through unlock_* -> call_*; its name is published only through the
target_tool of an extended policy in orders.extended.yaml. Every tool performs one atomic
business write with the values the agent (or the customer) passes; none of them checks a
policy precondition or refuses a call.
"""

from erlbench import ToolContext, tool

_DAYS_IN_MONTH = (31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31)


@tool(owner="agent", rw="write")
def request_specimen_recollection_7c5f4bb7(ctx: ToolContext, order_id: str, rejected_event_id: str,
                                           recollection_window_days: int) -> str:
    """Record that Halverson Clinical Laboratories offers the patient a no-charge recollection for one
    rejected specimen of a laboratory test order. One call writes one recollection request on the
    order's history, linked to the rejection it answers, dated today, and carrying the last date on
    which the recollected specimen may be collected; that last date is the rejection's own date moved
    forward by the number of calendar days granted. The order itself keeps its current status. On success
    the request and its recollect-by date appear in the order's history lines.

    Args:
        order_id: Id class — the reference number of the laboratory test order whose specimen was
            rejected, as returned by the order lookup for the verified patient.
        rejected_event_id: Id class — the reference number of the specimen-rejection history line this
            recollection answers, as returned by the order history lookup for that order.
        recollection_window_days: Fixed-format class — the whole number of calendar days granted for
            the recollection, an integer of 1 or more, counted from the rejection date as day 0; the
            recollect-by date recorded from it is written as YYYY-MM-DD.

    Returns:
        A confirmation sentence (string) stating the recollection request reference number (12
        lowercase hexadecimal characters after the prefix rcq_), the order reference number, the
        rejection reference number it answers, the request date (YYYY-MM-DD) and the recollect-by
        date (YYYY-MM-DD); the presence of the request reference number means the request was recorded.
    """
    def _add_calendar_days(date_text: str, days: int) -> str:
        """Code-level helper (not a tool): a 'YYYY-MM-DD' date moved forward by whole calendar days."""
        year, month, day = (int(part) for part in str(date_text)[:10].split("-"))
        remaining = int(days)
        while remaining > 0:
            leap = year % 4 == 0 and (year % 100 != 0 or year % 400 == 0)
            month_length = 29 if (month == 2 and leap) else _DAYS_IN_MONTH[month - 1]
            step = min(remaining, month_length - day + 1)
            day += step
            remaining -= step
            if day > month_length:
                day = 1
                month += 1
                if month > 12:
                    month = 1
                    year += 1
        return f"{year:04d}-{month:02d}-{day:02d}"

    days = int(recollection_window_days)
    rejection_rows = ctx.find("order_events", order_event_id=rejected_event_id)
    rejection = rejection_rows[0] if rejection_rows else {}
    anchor = str(rejection.get("event_date") or ctx.now()[:10])
    recollect_by = _add_calendar_days(anchor, days)
    rid = ctx.make_id("rcq_", order_id, rejected_event_id, days)
    ctx.create("order_events", rid, order_event_id=rid, order_id=order_id,
               customer_id=rejection.get("customer_id", ""), event_type="orders_recollection_requested",
               event_date=ctx.now()[:10], rejected_event_id=rejected_event_id,
               recollect_by_date=recollect_by)
    return (f"Recollection request {rid} recorded on order {order_id} for rejection {rejected_event_id}: "
            f"requested {ctx.now()[:10]}, recollect by {recollect_by}.")


@tool(owner="agent", rw="write")
def issue_genetic_self_pay_quote_0325000c(ctx: ToolContext, order_id: str, quote_amount: float) -> str:
    """Issue the good faith estimate (self-pay quote) for one genetic-testing order that the patient pays
    directly. One call writes the quoted amount and today's date as the order's current good faith
    estimate, replacing any estimate previously shown on that order; no other order of the requisition
    is changed and no charge line is posted. On success the order lookup shows the new estimate
    amount and its estimate date.

    Args:
        order_id: Id class — the reference number of the genetic-testing order being quoted, as returned
            by the order lookup for the verified patient.
        quote_amount: Fixed-format class — the quoted self-pay amount in USD, a positive number with 2
            decimal places, rounded to the cent.

    Returns:
        A confirmation sentence (string) stating the order reference number, the estimate amount in USD
        with 2 decimal places and the estimate date (YYYY-MM-DD); the confirmation means the estimate is
        now the order's current good faith estimate.
    """
    amount = round(float(quote_amount), 2)
    ctx.update("orders", order_id, good_faith_estimate_amount=amount, estimate_date=ctx.now()[:10])
    return f"Good faith estimate on order {order_id} set to {amount:.2f} USD, dated {ctx.now()[:10]}."


@tool(owner="user", rw="write")
def cancel_genetic_test_order_d90cc330(ctx: ToolContext, order_id: str, handling_fee_amount: float) -> str:
    """Cancel, as the patient, one of your own genetic-testing orders while testing has not started. One call sets
    the order to cancelled with the reason patient request and today's cancellation date, clears any hold
    reason, credits in full every test or add-on charge line still standing on the order (credit reason cancelled_before_testing), posts one cancellation handling fee line at the amount given when that
    amount is above 0.00, and brings the order's list-price total to the charges still standing on it. On success the order shows as cancelled and its history shows the credits and any handling fee.

    Args:
        order_id: Id class — the reference number of your genetic-testing order to cancel, as the agent
            reads it to you from the order lookup.
        handling_fee_amount: Fixed-format class — the cancellation handling fee in USD that the agent
            tells you, a number of 0.00 or more with 2 decimal places, rounded to the cent.

    Returns:
        A confirmation sentence (string) stating the order reference number, the new status cancelled,
        the cancellation date (YYYY-MM-DD), how many charge lines were credited (an integer), the
        handling fee posted in USD with 2 decimal places (0.00 when none) and the order's list-price total
        in USD with 2 decimal places; the status cancelled in the confirmation means the cancellation was
        recorded.
    """
    fee = round(float(handling_fee_amount), 2)
    today = ctx.now()[:10]
    order_rows = ctx.find("orders", order_id=order_id)
    order = order_rows[0] if order_rows else {}
    lines = ctx.find("order_events", order_id=order_id)
    credited_ids = {row.get("credited_event_id") for row in lines
                    if row.get("event_type") == "orders_test_charge_credited"}
    credited_total = 0.0
    credited_count = 0
    for row in lines:
        is_test_line = (row.get("event_type") == "orders_add_on_posted"
                        or (row.get("event_type") == "orders_test_charge_posted"
                            and row.get("charge_reason") in ("ordered", "reflex")))
        if not is_test_line or row.get("order_event_id") in credited_ids:
            continue
        cid = ctx.make_id("crd_", order_id, row.get("order_event_id"))
        ctx.create("order_events", cid, order_event_id=cid, order_id=order_id,
                   customer_id=row.get("customer_id", ""), event_type="orders_test_charge_credited",
                   event_date=today, test_code=row.get("test_code", ""),
                   charge_amount=round(float(row.get("charge_amount") or 0), 2),
                   credit_reason="cancelled_before_testing", credited_event_id=row.get("order_event_id"))
        credited_total += float(row.get("charge_amount") or 0)
        credited_count += 1
    if fee > 0:
        fid = ctx.make_id("hfe_", order_id, fee)
        ctx.create("order_events", fid, order_event_id=fid, order_id=order_id,
                   customer_id=order.get("customer_id", ""), event_type="orders_test_charge_posted",
                   event_date=today, test_code="", charge_amount=fee,
                   charge_reason="cancellation_handling_fee")
    total = round(float(order.get("list_price_total") or 0) - credited_total + fee, 2)
    ctx.update("orders", order_id, status="cancelled", cancellation_reason="patient_request",
               cancelled_date=today, hold_reason="none", list_price_total=total)
    return (f"Order {order_id} is now cancelled as of {today}: {credited_count} charge line(s) credited, "
            f"handling fee {fee:.2f} USD, list-price total {total:.2f} USD.")


@tool(owner="agent", rw="write")
def issue_reference_test_estimate_b0801821(ctx: ToolContext, order_id: str, estimate_amount: float) -> str:
    """Issue the good faith estimate (self-pay estimate) for one reference-testing order that the patient
    pays directly. One call writes the estimated amount and today's date as the order's current good faith
    estimate, replacing any estimate previously shown on that order; no other order is changed and no charge
    line is posted. On success the order lookup shows the new estimate amount and its estimate date.

    Args:
        order_id: Id class — the reference number of the reference-testing order being estimated, as returned
            by the order lookup for the verified patient.
        estimate_amount: Fixed-format class — the estimated self-pay amount in USD, a positive number with 2
            decimal places, rounded to the cent.

    Returns:
        A confirmation sentence (string) stating the order reference number, the estimate amount in USD with 2
        decimal places and the estimate date (YYYY-MM-DD); the confirmation means the estimate is now the
        order's current good faith estimate.
    """
    amount = round(float(estimate_amount), 2)
    ctx.update("orders", order_id, good_faith_estimate_amount=amount, estimate_date=ctx.now()[:10])
    return f"Good faith estimate on order {order_id} set to {amount:.2f} USD, dated {ctx.now()[:10]}."


@tool(owner="user", rw="write")
def cancel_reference_test_order_ed257856(ctx: ToolContext, order_id: str, handling_fee_amount: float) -> str:
    """Cancel, as the patient, one of your own reference-testing orders while testing has not started. One call sets the
    order to cancelled with the reason patient request and today's cancellation date, clears any hold reason,
    credits in full every test or add-on charge line still standing on the order (credit reason cancelled_before_testing), posts one cancellation handling fee line at the amount given when that amount is above
    0.00, and brings the order's list-price total to the charges still standing on it. On success the order shows as
    cancelled and its history shows the credits and any handling fee.

    Args:
        order_id: Id class — the reference number of your reference-testing order to cancel, as the agent reads
            it to you from the order lookup.
        handling_fee_amount: Fixed-format class — the cancellation handling fee in USD that the agent tells you,
            a number of 0.00 or more with 2 decimal places, rounded to the cent.

    Returns:
        A confirmation sentence (string) stating the order reference number, the new status cancelled, the
        cancellation date (YYYY-MM-DD), how many charge lines were credited (an integer), the handling fee posted
        in USD with 2 decimal places (0.00 when none) and the order's list-price total in USD with 2 decimal
        places; the status cancelled in the confirmation means the cancellation was recorded.
    """
    fee = round(float(handling_fee_amount), 2)
    today = ctx.now()[:10]
    order_rows = ctx.find("orders", order_id=order_id)
    order = order_rows[0] if order_rows else {}
    lines = ctx.find("order_events", order_id=order_id)
    credited_ids = {row.get("credited_event_id") for row in lines
                    if row.get("event_type") == "orders_test_charge_credited"}
    credited_total = 0.0
    credited_count = 0
    for row in lines:
        is_test_line = (row.get("event_type") == "orders_add_on_posted"
                        or (row.get("event_type") == "orders_test_charge_posted"
                            and row.get("charge_reason") in ("ordered", "reflex")))
        if not is_test_line or row.get("order_event_id") in credited_ids:
            continue
        cid = ctx.make_id("crd_", order_id, row.get("order_event_id"))
        ctx.create("order_events", cid, order_event_id=cid, order_id=order_id,
                   customer_id=row.get("customer_id", ""), event_type="orders_test_charge_credited",
                   event_date=today, test_code=row.get("test_code", ""),
                   charge_amount=round(float(row.get("charge_amount") or 0), 2),
                   credit_reason="cancelled_before_testing", credited_event_id=row.get("order_event_id"))
        credited_total += float(row.get("charge_amount") or 0)
        credited_count += 1
    if fee > 0:
        fid = ctx.make_id("hfe_", order_id, fee)
        ctx.create("order_events", fid, order_event_id=fid, order_id=order_id,
                   customer_id=order.get("customer_id", ""), event_type="orders_test_charge_posted",
                   event_date=today, test_code="", charge_amount=fee,
                   charge_reason="cancellation_handling_fee")
    total = round(float(order.get("list_price_total") or 0) - credited_total + fee, 2)
    ctx.update("orders", order_id, status="cancelled", cancellation_reason="patient_request",
               cancelled_date=today, hold_reason="none", list_price_total=total)
    return (f"Order {order_id} is now cancelled as of {today}: {credited_count} charge line(s) credited, "
            f"handling fee {fee:.2f} USD, list-price total {total:.2f} USD.")

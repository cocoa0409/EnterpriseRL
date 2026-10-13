"""Hidden task tools of the estimate_booking_desk difficulty (Repair Estimates & Appointments).

Each tool performs exactly one atomic write on an estimate booking's history. None of them checks a
policy condition, a prerequisite or a balance: the desk works those out from the published policies and
the records before calling, and passes the finished figures in.
"""

from erlbench import ToolContext, tool


@tool(owner="agent", rw="write")
def post_storage_statement_c4ddc4f2(ctx: ToolContext, booking_id: str, period_start_date: str,
                                    period_end_date: str, amount_usd: float) -> str:
    """Post a storage statement charge on an estimate booking whose vehicle is standing at the
    repair center: one storage charge covering the billed storage days from the first billed day
    through the last billed day, both included. On success a new storage charge stands on the
    booking's estimate-stage fees (the booking balance rises by the amount), dated today, and it
    can be paid or waived by quoting its charge reference number.

    Args:
        booking_id: Id class — reference number of the estimate booking the storage is charged on, as returned by the estimate booking lookup.
        period_start_date: Fixed-format class — first billed storage day of this statement, written YYYY-MM-DD (calendar date in the repair center's local time zone).
        period_end_date: Fixed-format class — last billed storage day of this statement (included in the period), written YYYY-MM-DD (calendar date in the repair center's local time zone).
        amount_usd: Fixed-format class — storage charged by this statement, in USD with 2 decimal places, positive; a value with more decimals is rounded half-up to the cent when stored.

    Returns:
        A confirmation string naming the new charge reference number (an id beginning with "eev_"),
        the booking reference number, the billed period start and end dates (YYYY-MM-DD) and the
        amount posted in USD with 2 decimals; seeing that reference number means the charge was
        posted and now counts toward the booking's outstanding estimate-stage fees.
    """
    booking = ctx.find("estimate_bookings", booking_id=booking_id)
    cust = booking[0].get("customer_id") if booking else ""
    amount = round(float(amount_usd), 2)
    rid = ctx.make_id("eev_", booking_id, "storage", period_start_date, period_end_date, amount)
    ctx.create("estimate_events", rid, estimate_event_id=rid, booking_id=booking_id, customer_id=cust,
               event_type="estimate_fee_charge", event_date=ctx.now()[:10], fee_type="storage",
               amount_usd=amount, period_start_date=period_start_date, period_end_date=period_end_date,
               tow_miles=0.0, charge_event_id="")
    return (f"Storage charge {rid} posted on booking {booking_id} for {period_start_date} through "
            f"{period_end_date}: USD {amount:.2f}.")


@tool(owner="agent", rw="write")
def waive_storage_goodwill_2cb3c7ba(ctx: ToolContext, booking_id: str, charge_event_id: str,
                                    amount_usd: float) -> str:
    """Book a goodwill waiver against one storage charge of an estimate booking. The waiver reduces
    that charge's outstanding amount by the waived sum, dated today, with the waiver reason goodwill;
    the customer sees the storage charge lowered by that amount on the booking's fee history.

    Args:
        booking_id: Id class — reference number of the estimate booking the storage charge belongs to, as returned by the estimate booking lookup.
        charge_event_id: Id class — reference number of the storage charge being relieved, as returned by the estimate booking history lookup or by the storage posting receipt.
        amount_usd: Fixed-format class — goodwill waived on that charge, in USD with 2 decimal places, positive; a value with more decimals is rounded half-up to the cent when stored.

    Returns:
        A confirmation string naming the new waiver reference number (an id beginning with "eev_"),
        the storage charge reference number it reduces and the amount waived in USD with 2 decimals;
        seeing that reference number means the goodwill waiver was booked and the charge's outstanding
        amount is lower by that sum.
    """
    booking = ctx.find("estimate_bookings", booking_id=booking_id)
    cust = booking[0].get("customer_id") if booking else ""
    amount = round(float(amount_usd), 2)
    rid = ctx.make_id("eev_", booking_id, charge_event_id, "goodwill", amount)
    ctx.create("estimate_events", rid, estimate_event_id=rid, booking_id=booking_id, customer_id=cust,
               event_type="estimate_fee_waiver", event_date=ctx.now()[:10], charge_event_id=charge_event_id,
               amount_usd=amount, waiver_reason="goodwill")
    return f"Goodwill waiver {rid} booked against charge {charge_event_id}: USD {amount:.2f}."


@tool(owner="user", rw="write")
def pay_estimate_charge_54cbd3ef(ctx: ToolContext, booking_id: str, charge_event_id: str,
                                 amount_usd: float, payment_method: str) -> str:
    """The vehicle owner pays, in person, an amount toward one estimate-stage charge on their own
    booking. The payment is applied to that charge, dated today, and lowers its outstanding amount
    by the sum paid; the owner receives a payment reference number for their records.

    Args:
        booking_id: Id class — reference number of the owner's estimate booking, as given to the owner by the desk from the estimate booking lookup.
        charge_event_id: Id class — reference number of the charge being paid, as given to the owner by the desk from the booking history or a posting receipt.
        amount_usd: Fixed-format class — amount the owner pays toward that charge, in USD with 2 decimal places, positive; a value with more decimals is rounded half-up to the cent when stored.
        payment_method: Enum class — how the owner pays: card when the owner pays with a credit or debit card; ach when the owner pays by bank transfer from a checking account; cash when the owner pays in cash at the center; check when the owner pays by personal check; insurer_direct only when the insurer itself remits the money, which an owner paying in person never uses.

    Returns:
        A confirmation string naming the new payment reference number (an id beginning with "eev_"),
        the charge reference number paid, the amount paid in USD with 2 decimals and the payment
        method; seeing that reference number means the payment was applied and the charge's
        outstanding amount is lower by that sum.
    """
    booking = ctx.find("estimate_bookings", booking_id=booking_id)
    cust = booking[0].get("customer_id") if booking else ""
    amount = round(float(amount_usd), 2)
    rid = ctx.make_id("eev_", booking_id, charge_event_id, "payment", amount, payment_method)
    ctx.create("estimate_events", rid, estimate_event_id=rid, booking_id=booking_id, customer_id=cust,
               event_type="estimate_fee_payment", event_date=ctx.now()[:10], charge_event_id=charge_event_id,
               amount_usd=amount, payment_method=payment_method)
    return (f"Payment {rid} of USD {amount:.2f} by {payment_method} applied to charge {charge_event_id} "
            f"on booking {booking_id}.")


@tool(owner="agent", rw="write")
def post_teardown_charge_9aa30e52(ctx: ToolContext, booking_id: str, amount_usd: float) -> str:
    """Post the teardown charge on an estimate booking whose vehicle was disassembled for a teardown
    estimate. On success one teardown charge, dated today, stands on the booking's estimate-stage
    fees (the booking balance rises by the amount) and can be paid or waived by quoting its charge
    reference number.

    Args:
        booking_id: Id class — reference number of the estimate booking the teardown is charged on, as returned by the estimate booking lookup.
        amount_usd: Fixed-format class — teardown charge posted, in USD with 2 decimal places, positive; a value with more decimals is rounded half-up to the cent when stored.

    Returns:
        A confirmation string naming the new charge reference number (an id beginning with "eev_"),
        the booking reference number and the amount posted in USD with 2 decimals; seeing that
        reference number means the teardown charge now stands on the booking.
    """
    booking = ctx.find("estimate_bookings", booking_id=booking_id)
    cust = booking[0].get("customer_id") if booking else ""
    amount = round(float(amount_usd), 2)
    rid = ctx.make_id("eev_", booking_id, "teardown", amount)
    ctx.create("estimate_events", rid, estimate_event_id=rid, booking_id=booking_id, customer_id=cust,
               event_type="estimate_fee_charge", event_date=ctx.now()[:10], fee_type="teardown",
               amount_usd=amount, tow_miles=0.0, charge_event_id="")
    return f"Teardown charge {rid} posted on booking {booking_id}: USD {amount:.2f}."


@tool(owner="agent", rw="write")
def post_measurement_charge_e807c387(ctx: ToolContext, booking_id: str, amount_usd: float) -> str:
    """Post the structural measurement charge on an estimate booking whose vehicle received an
    electronic three-dimensional measurement report. On success one measurement charge, dated today,
    stands on the booking's estimate-stage fees (the booking balance rises by the amount) and can be
    paid or waived by quoting its charge reference number.

    Args:
        booking_id: Id class — reference number of the estimate booking the measurement is charged on, as returned by the estimate booking lookup.
        amount_usd: Fixed-format class — measurement charge posted, in USD with 2 decimal places, positive; a value with more decimals is rounded half-up to the cent when stored.

    Returns:
        A confirmation string naming the new charge reference number (an id beginning with "eev_"),
        the booking reference number and the amount posted in USD with 2 decimals; seeing that
        reference number means the measurement charge now stands on the booking.
    """
    booking = ctx.find("estimate_bookings", booking_id=booking_id)
    cust = booking[0].get("customer_id") if booking else ""
    amount = round(float(amount_usd), 2)
    rid = ctx.make_id("eev_", booking_id, "measurement", amount)
    ctx.create("estimate_events", rid, estimate_event_id=rid, booking_id=booking_id, customer_id=cust,
               event_type="estimate_fee_charge", event_date=ctx.now()[:10], fee_type="measurement",
               amount_usd=amount, tow_miles=0.0, charge_event_id="")
    return f"Measurement charge {rid} posted on booking {booking_id}: USD {amount:.2f}."


@tool(owner="user", rw="write")
def remit_insurer_direct_payment_12af7a63(ctx: ToolContext, booking_id: str, charge_event_id: str,
                                          amount_usd: float) -> str:
    """The insurer on an insurance-claim estimate booking remits, itself, a direct payment toward one
    estimate-stage charge of its policyholder's booking. The payment is recorded as an insurer direct
    payment on that charge, dated today, and lowers the charge's outstanding amount by the sum
    remitted; the insurer receives a payment reference number for its file.

    Args:
        booking_id: Id class — reference number of the policyholder's estimate booking, as given to the insurer by the desk from the estimate booking lookup.
        charge_event_id: Id class — reference number of the charge the insurer pays, as given to the insurer by the desk from the booking history or a posting receipt.
        amount_usd: Fixed-format class — amount the insurer remits toward that charge, in USD with 2 decimal places, positive; a value with more decimals is rounded half-up to the cent when stored.

    Returns:
        A confirmation string naming the new payment reference number (an id beginning with "eev_"),
        the charge reference number paid and the amount remitted in USD with 2 decimals; seeing that
        reference number means the insurer's direct payment was applied and the charge's outstanding
        amount is lower by that sum.
    """
    booking = ctx.find("estimate_bookings", booking_id=booking_id)
    cust = booking[0].get("customer_id") if booking else ""
    amount = round(float(amount_usd), 2)
    rid = ctx.make_id("eev_", booking_id, charge_event_id, "insurer_direct", amount)
    ctx.create("estimate_events", rid, estimate_event_id=rid, booking_id=booking_id, customer_id=cust,
               event_type="estimate_fee_payment", event_date=ctx.now()[:10], charge_event_id=charge_event_id,
               amount_usd=amount, payment_method="insurer_direct")
    return (f"Insurer direct payment {rid} of USD {amount:.2f} applied to charge {charge_event_id} "
            f"on booking {booking_id}.")

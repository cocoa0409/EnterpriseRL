"""Hidden task tools of the collection_appointments difficulty (Halverson Clinical Laboratories).

Each tool performs one atomic write on a specimen collection visit and takes the values the
agent has already worked out from the published policies; no tool checks eligibility, order
or prerequisites, and none computes a charge on the agent's behalf.
"""

from erlbench import ToolContext, tool


@tool(owner="agent", rw="write")
def assess_trip_fee_73c5b19a(ctx: ToolContext, visit_id: str, fee_amount: float) -> str:
    """Post the trip charge on a collected home (mobile in-home) collection visit. One call adds one
    assessed trip-fee line, dated today, to the visit's collection-service fee record and raises the
    visit's outstanding collection-fee balance by that amount. Afterwards the trip charge appears in
    the visit's fee history as an assessed trip fee and the patient owes it until it is settled.

    Args:
        visit_id: Id class — the reference number of the collection visit the trip charge belongs to, read from the visit lookup for the patient.
        fee_amount: Fixed-format class — the trip charge to post, in USD, a positive amount given to 2 decimal places (cents); the value is posted exactly as given, already rounded to the cent.

    Returns:
        A dictionary receipt: visit_event_id (string, the reference number of the new assessed trip-fee
        line), visit_id (string, the visit charged), fee_type (string, always trip_fee), fee_amount (number,
        the amount posted in USD to 2 decimal places), event_date (string, YYYY-MM-DD, today's posting date)
        and fee_balance (number, the visit's outstanding collection-fee balance in USD after posting). A
        receipt carrying a visit_event_id means the charge is on the visit.
    """
    rows = ctx.find("visits", visit_id=visit_id)
    visit = rows[0] if rows else {}
    amount = round(float(fee_amount), 2)
    rid = ctx.make_id("vfa_", visit_id, "trip_fee", amount)
    ctx.create("visit_events", rid, visit_event_id=rid, visit_id=visit_id,
               customer_id=visit.get("customer_id", ""), event_type="visits_fee_assessed",
               event_date=ctx.now()[:10], fee_type="trip_fee", fee_amount=amount,
               waiver_reason="", payment_method="", assessed_event_id=None, paid_event_id=None)
    balance = round(float(visit.get("fee_balance") or 0) + amount, 2)
    ctx.update("visits", visit_id, fee_balance=balance)
    return str({"visit_event_id": rid, "visit_id": visit_id, "fee_type": "trip_fee",
                "fee_amount": amount, "event_date": ctx.now()[:10], "fee_balance": balance})


@tool(owner="agent", rw="write")
def assess_household_fee_59046739(ctx: ToolContext, visit_id: str, fee_amount: float) -> str:
    """Post the household charge for the additional household members drawn at a collected home
    collection visit. One call adds one assessed additional-patient fee line, dated today, to the
    visit's collection-service fee record and raises the visit's outstanding collection-fee balance by
    that amount; the patient then sees it in the visit's fee history as an assessed additional-patient
    fee owed until settled.

    Args:
        visit_id: Id class — the reference number of the collection visit at which the household members were drawn, read from the visit lookup for the patient.
        fee_amount: Fixed-format class — the household charge to post, in USD, a positive amount given to 2 decimal places (cents); the value is posted exactly as given, already rounded to the cent.

    Returns:
        A dictionary receipt: visit_event_id (string, the reference number of the new assessed
        additional-patient fee line), visit_id (string, the visit charged), fee_type (string, always
        additional_patient_fee), fee_amount (number, the amount posted in USD to 2 decimal places),
        event_date (string, YYYY-MM-DD, today's posting date) and fee_balance (number, the visit's
        outstanding collection-fee balance in USD after posting). A receipt carrying a visit_event_id
        means the charge is on the visit.
    """
    rows = ctx.find("visits", visit_id=visit_id)
    visit = rows[0] if rows else {}
    amount = round(float(fee_amount), 2)
    rid = ctx.make_id("vfa_", visit_id, "additional_patient_fee", amount)
    ctx.create("visit_events", rid, visit_event_id=rid, visit_id=visit_id,
               customer_id=visit.get("customer_id", ""), event_type="visits_fee_assessed",
               event_date=ctx.now()[:10], fee_type="additional_patient_fee", fee_amount=amount,
               waiver_reason="", payment_method="", assessed_event_id=None, paid_event_id=None)
    balance = round(float(visit.get("fee_balance") or 0) + amount, 2)
    ctx.update("visits", visit_id, fee_balance=balance)
    return str({"visit_event_id": rid, "visit_id": visit_id, "fee_type": "additional_patient_fee",
                "fee_amount": amount, "event_date": ctx.now()[:10], "fee_balance": balance})


@tool(owner="agent", rw="write")
def assess_weekend_surcharge_242d901c(ctx: ToolContext, visit_id: str, fee_amount: float) -> str:
    """Post the weekend charge on a collected home collection visit held on a Saturday or Sunday. One
    call adds one assessed weekend-surcharge line, dated today, to the visit's collection-service fee
    record and raises the visit's outstanding collection-fee balance by that amount; the patient then
    sees it in the visit's fee history as an assessed weekend surcharge owed until settled.

    Args:
        visit_id: Id class — the reference number of the weekend collection visit to charge, read from the visit lookup for the patient.
        fee_amount: Fixed-format class — the weekend charge to post, in USD, a positive amount given to 2 decimal places (cents); the value is posted exactly as given, already rounded to the cent.

    Returns:
        A dictionary receipt: visit_event_id (string, the reference number of the new assessed
        weekend-surcharge line), visit_id (string, the visit charged), fee_type (string, always
        weekend_surcharge), fee_amount (number, the amount posted in USD to 2 decimal places), event_date
        (string, YYYY-MM-DD, today's posting date) and fee_balance (number, the visit's outstanding
        collection-fee balance in USD after posting). A receipt carrying a visit_event_id means the charge
        is on the visit.
    """
    rows = ctx.find("visits", visit_id=visit_id)
    visit = rows[0] if rows else {}
    amount = round(float(fee_amount), 2)
    rid = ctx.make_id("vfa_", visit_id, "weekend_surcharge", amount)
    ctx.create("visit_events", rid, visit_event_id=rid, visit_id=visit_id,
               customer_id=visit.get("customer_id", ""), event_type="visits_fee_assessed",
               event_date=ctx.now()[:10], fee_type="weekend_surcharge", fee_amount=amount,
               waiver_reason="", payment_method="", assessed_event_id=None, paid_event_id=None)
    balance = round(float(visit.get("fee_balance") or 0) + amount, 2)
    ctx.update("visits", visit_id, fee_balance=balance)
    return str({"visit_event_id": rid, "visit_id": visit_id, "fee_type": "weekend_surcharge",
                "fee_amount": amount, "event_date": ctx.now()[:10], "fee_balance": balance})


@tool(owner="user", rw="write")
def pay_home_visit_fees_e8e0d8a4(ctx: ToolContext, visit_id: str, assessed_event_id: str,
                                 fee_amount: float, payment_method: str) -> str:
    """The patient pays, with their own card, the settlement charge for the service charges (trip,
    additional-patient and weekend) of a collected home collection visit. One call records one card
    payment, dated today, against the visit's assessed trip-fee line and marks the visit's
    collection-fee balance as settled (0.00); the patient sees the payment in the visit's fee history
    and nothing further is owed for those service charges.

    Args:
        visit_id: Id class — the reference number of the home collection visit being settled, as the agent reads it from the visit lookup and gives it to the patient.
        assessed_event_id: Id class — the reference number of the visit's assessed trip-fee line the payment is recorded against, as listed in the visit's fee history.
        fee_amount: Fixed-format class — the settlement charge to put on the card, in USD, a positive amount given to 2 decimal places (cents), exactly as the agent states it.
        payment_method: Enum class — the card the patient pays with: credit_card when the patient pays with a credit card; debit_card when the patient pays with a debit card drawn on a bank account; hsa_fsa_card when the patient pays with a health savings account or flexible spending account card.

    Returns:
        A dictionary receipt: visit_event_id (string, the reference number of the new payment line),
        visit_id (string, the visit settled), assessed_event_id (string, the trip-fee line the payment is
        recorded against), fee_amount (number, the amount charged to the card in USD to 2 decimal places),
        payment_method (string, the card type used), event_date (string, YYYY-MM-DD, today's payment date)
        and fee_balance (number, the visit's collection-fee balance after settlement, 0.00). A receipt
        carrying a visit_event_id means the payment was taken.
    """
    rows = ctx.find("visits", visit_id=visit_id)
    visit = rows[0] if rows else {}
    line = ctx.find("visit_events", visit_event_id=assessed_event_id)
    fee_type = line[0].get("fee_type", "") if line else ""
    amount = round(float(fee_amount), 2)
    rid = ctx.make_id("vfp_", visit_id, assessed_event_id, amount, payment_method)
    ctx.create("visit_events", rid, visit_event_id=rid, visit_id=visit_id,
               customer_id=visit.get("customer_id", ""), event_type="visits_fee_paid",
               event_date=ctx.now()[:10], fee_type=fee_type, fee_amount=amount, waiver_reason="",
               payment_method=payment_method, assessed_event_id=assessed_event_id, paid_event_id=None)
    ctx.update("visits", visit_id, fee_balance=0.0)
    return str({"visit_event_id": rid, "visit_id": visit_id, "assessed_event_id": assessed_event_id,
                "fee_amount": amount, "payment_method": payment_method, "event_date": ctx.now()[:10],
                "fee_balance": 0.0})


@tool(owner="agent", rw="write")
def assess_no_show_fee_12606755(ctx: ToolContext, visit_id: str, fee_amount: float) -> str:
    """Post the no-show charge on a home collection visit that was recorded as missed (the patient was
    not there when the phlebotomist arrived). One call adds one assessed no-show fee line, dated today,
    to the visit's collection-service fee record and raises the visit's outstanding collection-fee
    balance by that amount; the patient then sees an assessed no-show fee owed on the missed visit.

    Args:
        visit_id: Id class — the reference number of the missed collection visit to charge, read from the visit lookup for the patient.
        fee_amount: Fixed-format class — the no-show charge to post, in USD, a positive amount given to 2 decimal places (cents); the value is posted exactly as given, already rounded to the cent.

    Returns:
        A dictionary receipt: visit_event_id (string, the reference number of the new assessed no-show
        fee line), visit_id (string, the visit charged), fee_type (string, always no_show_fee), fee_amount
        (number, the amount posted in USD to 2 decimal places), event_date (string, YYYY-MM-DD, today's
        posting date) and fee_balance (number, the visit's outstanding collection-fee balance in USD after
        posting). A receipt carrying a visit_event_id means the charge is on the visit.
    """
    rows = ctx.find("visits", visit_id=visit_id)
    visit = rows[0] if rows else {}
    amount = round(float(fee_amount), 2)
    rid = ctx.make_id("vfa_", visit_id, "no_show_fee", amount)
    ctx.create("visit_events", rid, visit_event_id=rid, visit_id=visit_id,
               customer_id=visit.get("customer_id", ""), event_type="visits_fee_assessed",
               event_date=ctx.now()[:10], fee_type="no_show_fee", fee_amount=amount,
               waiver_reason="", payment_method="", assessed_event_id=None, paid_event_id=None)
    balance = round(float(visit.get("fee_balance") or 0) + amount, 2)
    ctx.update("visits", visit_id, fee_balance=balance)
    return str({"visit_event_id": rid, "visit_id": visit_id, "fee_type": "no_show_fee",
                "fee_amount": amount, "event_date": ctx.now()[:10], "fee_balance": balance})


@tool(owner="user", rw="write")
def pay_missed_visit_fee_baa116ed(ctx: ToolContext, visit_id: str, assessed_event_id: str,
                                  fee_amount: float, payment_method: str) -> str:
    """The patient pays, with their own card, the settlement charge for the no-show fee on a missed
    home collection visit. One call records one card payment, dated today, against the visit's assessed
    no-show fee line and marks the missed visit's collection-fee balance as settled (0.00); the patient
    sees the payment in the visit's fee history and nothing further is owed for that no-show fee.

    Args:
        visit_id: Id class — the reference number of the missed collection visit being settled, as the agent reads it from the visit lookup and gives it to the patient.
        assessed_event_id: Id class — the reference number of the missed visit's assessed no-show fee line the payment is recorded against, as listed in the visit's fee history.
        fee_amount: Fixed-format class — the settlement charge to put on the card, in USD, a positive amount given to 2 decimal places (cents), exactly as the agent states it.
        payment_method: Enum class — the card the patient pays with: credit_card when the patient pays with a credit card; debit_card when the patient pays with a debit card drawn on a bank account; hsa_fsa_card when the patient pays with a health savings account or flexible spending account card.

    Returns:
        A dictionary receipt: visit_event_id (string, the reference number of the new payment line),
        visit_id (string, the visit settled), assessed_event_id (string, the no-show fee line the payment
        is recorded against), fee_amount (number, the amount charged to the card in USD to 2 decimal
        places), payment_method (string, the card type used), event_date (string, YYYY-MM-DD, today's
        payment date) and fee_balance (number, the visit's collection-fee balance after settlement, 0.00).
        A receipt carrying a visit_event_id means the payment was taken.
    """
    rows = ctx.find("visits", visit_id=visit_id)
    visit = rows[0] if rows else {}
    amount = round(float(fee_amount), 2)
    rid = ctx.make_id("vfp_", visit_id, assessed_event_id, amount, payment_method)
    ctx.create("visit_events", rid, visit_event_id=rid, visit_id=visit_id,
               customer_id=visit.get("customer_id", ""), event_type="visits_fee_paid",
               event_date=ctx.now()[:10], fee_type="no_show_fee", fee_amount=amount, waiver_reason="",
               payment_method=payment_method, assessed_event_id=assessed_event_id, paid_event_id=None)
    ctx.update("visits", visit_id, fee_balance=0.0)
    return str({"visit_event_id": rid, "visit_id": visit_id, "assessed_event_id": assessed_event_id,
                "fee_amount": amount, "payment_method": payment_method, "event_date": ctx.now()[:10],
                "fee_balance": 0.0})


@tool(owner="agent", rw="write")
def reschedule_home_visit_6b0b2488(ctx: ToolContext, visit_id: str, appointment_date: str,
                                   appointment_time: str, fee_amount: float) -> str:
    """Move a booked home (mobile in-home) collection visit to a new date and start time and post the
    late-change charge it carries. One call sets the visit's appointment date and start time to the new
    values, adds one to the number of times the visit has been rescheduled, and, when fee_amount is above
    0.00, adds one assessed late-cancellation fee line dated today and raises the visit's outstanding
    collection-fee balance by it. The visit stays booked; the patient sees the new date and time on the
    visit and, where a charge was given, the late-change charge in its fee history.

    Args:
        visit_id: Id class — the reference number of the booked home visit being moved, read from the visit lookup for the patient.
        appointment_date: Fixed-format class — the new visit date the patient asks for, written YYYY-MM-DD, local calendar date of the visit.
        appointment_time: Fixed-format class — the new start of the arrival window the patient asks for, written HH:MM, 24-hour, local time of the site.
        fee_amount: Fixed-format class — the late-change charge to post with the move, in USD, given to 2 decimal places (cents); 0.00 when the move carries no charge, in which case no fee line is posted.

    Returns:
        A dictionary receipt: visit_id (string, the visit moved), appointment_date (string, YYYY-MM-DD, the
        new date), appointment_time (string, HH:MM, the new start), reschedule_count (integer, times the
        visit has now been rescheduled), visit_event_id (string, the reference number of the late-change
        fee line, empty when no charge was posted), fee_amount (number, the charge posted in USD to 2
        decimal places) and fee_balance (number, the visit's outstanding collection-fee balance in USD after
        the move). A receipt carrying the new appointment_date means the visit was moved.
    """
    rows = ctx.find("visits", visit_id=visit_id)
    visit = rows[0] if rows else {}
    amount = round(float(fee_amount), 2)
    count = int(visit.get("reschedule_count") or 0) + 1
    balance = round(float(visit.get("fee_balance") or 0) + amount, 2)
    rid = ""
    if amount > 0:
        rid = ctx.make_id("vfa_", visit_id, "late_cancellation_fee", amount, appointment_date, appointment_time)
        ctx.create("visit_events", rid, visit_event_id=rid, visit_id=visit_id,
                   customer_id=visit.get("customer_id", ""), event_type="visits_fee_assessed",
                   event_date=ctx.now()[:10], fee_type="late_cancellation_fee", fee_amount=amount,
                   waiver_reason="", payment_method="", assessed_event_id=None, paid_event_id=None)
    ctx.update("visits", visit_id, appointment_date=appointment_date, appointment_time=appointment_time,
               reschedule_count=count, fee_balance=balance)
    return str({"visit_id": visit_id, "appointment_date": appointment_date, "appointment_time": appointment_time,
                "reschedule_count": count, "visit_event_id": rid, "fee_amount": amount, "fee_balance": balance})

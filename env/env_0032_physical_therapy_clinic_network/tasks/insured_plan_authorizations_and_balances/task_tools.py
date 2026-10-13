"""Hidden task tools for the insured_plan_authorizations_and_balances difficulty
(Piedmont Motion Physical Therapy, Insured Plan of Care).

Every tool performs exactly one atomic write on an insured plan of care and keeps the plan's
running patient balance in step with the entry it books. No tool checks eligibility, status,
prerequisites or amounts: the caller has already decided all of that from the published policy
and the records, and passes the figures in.
"""

from erlbench import ToolContext, tool


@tool(owner="agent", rw="write")
def correct_overposted_coinsurance_fd44d809(ctx: ToolContext, care_plan_id: str, source_event_id: str,
                                           amount: float) -> dict:
    """Book a billing error correction that removes the overstated part of one coinsurance charge on a
    patient's insured plan of care.

    One call records a single balance adjustment of kind billing_error_correction against the
    coinsurance charge named, dated today, for the amount given, and lowers the patient's open balance
    on that plan of care by the same amount (a balance that falls below zero becomes a credit owed to
    the patient). The patient sees the corrected balance on the plan and on the next statement. The
    original coinsurance charge stays in the history; the correction points back to it.

    Args:
        care_plan_id: Id class — the reference number of the insured plan of care the coinsurance charge
            sits on, as returned by the plan-of-care lookup.
        source_event_id: Id class — the reference number of the coinsurance charge entry being corrected,
            as returned by the plan-of-care history lookup.
        amount: Fixed-format class — the amount removed from the charge, in USD, a positive number with
            2 decimal places, rounded half up to the cent before it is passed.

    Returns:
        A dictionary confirming the correction: adjustment_id (string, the reference number of the new
        adjustment entry), care_plan_id (string, the plan of care adjusted), source_event_id (string, the
        coinsurance charge it corrects), adjustment_kind (string, always billing_error_correction),
        amount (number, USD to 2 decimals, the amount removed), event_date (string, YYYY-MM-DD, the date
        booked) and patient_balance (number, USD to 2 decimals, the plan's open patient balance after the
        correction; negative means a credit). A returned adjustment_id means the correction is on file.
    """
    rows = ctx.find("care_plans", care_plan_id=care_plan_id)
    plan = rows[0] if rows else {}
    amt = round(float(amount), 2)
    rid = ctx.make_id("cpe_", care_plan_id, source_event_id, amt, "billing_error_correction")
    today = ctx.now()[:10]
    ctx.create("care_plan_events", rid, care_plan_event_id=rid, care_plan_id=care_plan_id,
               customer_id=plan.get("customer_id", ""), event_type="plan_patient_adjustment", event_date=today,
               adjustment_kind="billing_error_correction", amount=amt, source_event_id=source_event_id)
    balance = round(float(plan.get("patient_due_balance") or 0) - amt, 2)
    if plan:
        ctx.update("care_plans", care_plan_id, patient_due_balance=balance)
    return {"adjustment_id": rid, "care_plan_id": care_plan_id, "source_event_id": source_event_id,
            "adjustment_kind": "billing_error_correction", "amount": amt, "event_date": today,
            "patient_balance": balance}


@tool(owner="agent", rw="write")
def post_noncovered_visit_charge_a3bfc726(ctx: ToolContext, care_plan_id: str, visit_date: str,
                                         source_event_id: str, amount: float) -> dict:
    """Post the patient's charge for one visit the payer did not cover because the calendar-year visit
    limit was used up, on the patient's insured plan of care.

    One call records a single patient charge of kind non_covered_service for the date of service given,
    dated today and pointing back to the billed visit, and raises the patient's open balance on that plan
    of care by the amount (a credit standing on the plan is reduced first in the running balance). The
    patient sees the charge on the plan and on the next statement.

    Args:
        care_plan_id: Id class — the reference number of the insured plan of care the visit was billed
            under, as returned by the plan-of-care lookup.
        visit_date: Fixed-format class — the date of service of the visit being charged, in YYYY-MM-DD
            format, copied from the billed visit entry.
        source_event_id: Id class — the reference number of the billed visit entry the charge belongs to,
            as returned by the plan-of-care history lookup.
        amount: Fixed-format class — the amount charged to the patient for the visit, in USD, a positive
            number with 2 decimal places, rounded half up to the cent before it is passed.

    Returns:
        A dictionary confirming the charge: charge_id (string, the reference number of the new charge
        entry), care_plan_id (string), visit_date (string, YYYY-MM-DD), charge_kind (string, always
        non_covered_service), amount (number, USD to 2 decimals), event_date (string, YYYY-MM-DD, the date
        posted) and patient_balance (number, USD to 2 decimals, the plan's open patient balance after the
        charge; negative means a credit). A returned charge_id means the charge is on file.
    """
    rows = ctx.find("care_plans", care_plan_id=care_plan_id)
    plan = rows[0] if rows else {}
    amt = round(float(amount), 2)
    rid = ctx.make_id("cpe_", care_plan_id, visit_date, source_event_id, amt, "non_covered_service")
    today = ctx.now()[:10]
    ctx.create("care_plan_events", rid, care_plan_event_id=rid, care_plan_id=care_plan_id,
               customer_id=plan.get("customer_id", ""), event_type="plan_patient_charge_posted", event_date=today,
               visit_date=visit_date, charge_kind="non_covered_service", amount=amt, source_event_id=source_event_id)
    balance = round(float(plan.get("patient_due_balance") or 0) + amt, 2)
    if plan:
        ctx.update("care_plans", care_plan_id, patient_due_balance=balance)
    return {"charge_id": rid, "care_plan_id": care_plan_id, "visit_date": visit_date,
            "charge_kind": "non_covered_service", "amount": amt, "event_date": today, "patient_balance": balance}


@tool(owner="agent", rw="write")
def issue_credit_refund_cc5fc5ad(ctx: ToolContext, care_plan_id: str, source_event_id: str, refund_method: str,
                                 amount: float) -> dict:
    """Issue a refund of credit standing on a patient's insured plan of care, returning money against one
    earlier patient payment.

    One call records a single refund entry dated today against the payment named, by the refund method
    given, and raises the plan's patient balance by the amount (the credit owed to the patient shrinks by
    what is refunded). The patient receives the money back on the original card or by mailed check and
    can see the refund in the plan history.

    Args:
        care_plan_id: Id class — the reference number of the insured plan of care the credit stands on, as
            returned by the plan-of-care lookup.
        source_event_id: Id class — the reference number of the patient payment entry the refund returns,
            as returned by the plan-of-care history lookup.
        refund_method: Enum class — how the money goes back: original_card when the refund is returned to
            the card the payment was made with; check when the refund is mailed to the patient as a paper
            check.
        amount: Fixed-format class — the amount refunded, in USD, a positive number with 2 decimal places,
            rounded half up to the cent before it is passed.

    Returns:
        A dictionary confirming the refund: refund_id (string, the reference number of the new refund
        entry), care_plan_id (string), source_event_id (string, the payment returned), refund_method
        (string, original_card or check), amount (number, USD to 2 decimals), event_date (string,
        YYYY-MM-DD, the date issued) and patient_balance (number, USD to 2 decimals, the plan's patient
        balance after the refund; negative means credit still standing). A returned refund_id means the
        refund has been issued.
    """
    rows = ctx.find("care_plans", care_plan_id=care_plan_id)
    plan = rows[0] if rows else {}
    amt = round(float(amount), 2)
    rid = ctx.make_id("cpe_", care_plan_id, source_event_id, refund_method, amt, "refund")
    today = ctx.now()[:10]
    ctx.create("care_plan_events", rid, care_plan_event_id=rid, care_plan_id=care_plan_id,
               customer_id=plan.get("customer_id", ""), event_type="plan_patient_refund", event_date=today,
               amount=amt, refund_method=refund_method, source_event_id=source_event_id)
    balance = round(float(plan.get("patient_due_balance") or 0) + amt, 2)
    if plan:
        ctx.update("care_plans", care_plan_id, patient_due_balance=balance)
    return {"refund_id": rid, "care_plan_id": care_plan_id, "source_event_id": source_event_id,
            "refund_method": refund_method, "amount": amt, "event_date": today, "patient_balance": balance}


@tool(owner="user", rw="write")
def pay_previsit_amount_3bf14ac0(ctx: ToolContext, care_plan_id: str, source_event_id: str, payment_method: str,
                                 amount: float) -> dict:
    """Make a payment by phone toward your own insured plan of care, ahead of a visit booked under it.

    You (the patient) authorize one payment through the secure payment line, applied to the open charge
    named; the payment is recorded today with channel phone, and your open balance on that plan of care
    drops by the amount (anything above the open charges stands as a credit until the day's visit is
    posted). You see the payment on the plan and receive the confirmation reference returned here.

    Args:
        care_plan_id: Id class — the reference number of the insured plan of care the payment goes to, as
            given to you by the representative from the plan-of-care lookup.
        source_event_id: Id class — the reference number of the open charge entry the payment is applied
            to, as given to you by the representative from the plan-of-care history lookup.
        payment_method: Enum class — how you pay: card when paying with a credit or debit card; cash when
            paying cash (front desk only); check when paying by check; hsa_fsa_card when paying with a
            health savings or flexible spending account card; ach when paying from a bank account.
        amount: Fixed-format class — the amount you pay, in USD, a positive number with 2 decimal places,
            rounded half up to the cent before it is passed.

    Returns:
        A dictionary confirming the payment: payment_id (string, the confirmation reference of the
        payment entry), care_plan_id (string), source_event_id (string, the charge it was applied to),
        payment_method (string), channel (string, always phone), amount (number, USD to 2 decimals),
        event_date (string, YYYY-MM-DD) and patient_balance (number, USD to 2 decimals, the plan's patient
        balance after the payment; negative means a credit). A returned payment_id means the payment went
        through.
    """
    rows = ctx.find("care_plans", care_plan_id=care_plan_id)
    plan = rows[0] if rows else {}
    amt = round(float(amount), 2)
    rid = ctx.make_id("cpe_", care_plan_id, source_event_id, payment_method, amt, "payment")
    today = ctx.now()[:10]
    ctx.create("care_plan_events", rid, care_plan_event_id=rid, care_plan_id=care_plan_id,
               customer_id=plan.get("customer_id", ""), event_type="plan_patient_payment", event_date=today,
               amount=amt, payment_method=payment_method, channel="phone", source_event_id=source_event_id)
    balance = round(float(plan.get("patient_due_balance") or 0) - amt, 2)
    if plan:
        ctx.update("care_plans", care_plan_id, patient_due_balance=balance)
    return {"payment_id": rid, "care_plan_id": care_plan_id, "source_event_id": source_event_id,
            "payment_method": payment_method, "channel": "phone", "amount": amt, "event_date": today,
            "patient_balance": balance}


@tool(owner="agent", rw="write")
def submit_retro_authorization_d347b3c8(ctx: ToolContext, care_plan_id: str, visit_date: str, source_event_id: str,
                                        requested_visits: int) -> dict:
    """Submit a retroactive authorization request to the payer for visits already attended on a patient's insured
    plan of care without an authorization covering them.

    One call records a single authorization request of kind retro on the plan of care, dated today, asking the payer
    to cover the number of visits given, starting from the visit date given. The request then shows in the plan's
    history as awaiting the payer's answer; the visits it covers can be billed once the payer approves it. Nothing
    is charged to the patient by this call.

    Args:
        care_plan_id: Id class — the reference number of the insured plan of care the visits were attended under, as
            returned by the plan-of-care lookup.
        visit_date: Fixed-format class — the date of service of the earliest visit the request asks the payer to cover,
            in YYYY-MM-DD format, copied from the appointment history of the plan's series.
        source_event_id: Id class — the reference number of a payer denial the request contests, as returned by the
            plan-of-care history lookup; a retroactive request contests no denial, so pass "" (an empty string).
        requested_visits: Fixed-format class — the number of visits the request asks the payer to cover, a
            non-negative integer (visits).

    Returns:
        A dictionary confirming the request: request_id (string, the reference number of the new request entry),
        care_plan_id (string), auth_kind (string, always retro), visit_date (string, YYYY-MM-DD), requested_visits
        (integer), event_date (string, YYYY-MM-DD, the date submitted) and status (string, always
        awaiting_payer_answer). A returned request_id means the request has been submitted.
    """
    rows = ctx.find("care_plans", care_plan_id=care_plan_id)
    plan = rows[0] if rows else {}
    visits = int(requested_visits)
    rid = ctx.make_id("cpe_", care_plan_id, visit_date, source_event_id, visits, "retro")
    today = ctx.now()[:10]
    ctx.create("care_plan_events", rid, care_plan_event_id=rid, care_plan_id=care_plan_id,
               customer_id=plan.get("customer_id", ""), event_type="plan_auth_requested", event_date=today,
               auth_kind="retro", requested_visits=visits, visit_date=visit_date, source_event_id=source_event_id)
    return {"request_id": rid, "care_plan_id": care_plan_id, "auth_kind": "retro", "visit_date": visit_date,
            "requested_visits": visits, "event_date": today, "status": "awaiting_payer_answer"}


@tool(owner="agent", rw="write")
def submit_auth_extension_019a16d0(ctx: ToolContext, care_plan_id: str, visit_date: str, source_event_id: str,
                                   requested_visits: int) -> dict:
    """Submit an extension request to the payer for more authorized visits on a patient's insured plan of care.

    One call records a single authorization request of kind extension on the plan of care, dated today, asking the
    payer to authorize the number of visits given for the coming authorization period. The request then shows in the
    plan's history as awaiting the payer's answer; an approval, when it arrives, adds the visits it grants to the
    plan's authorized visits. Nothing is charged to the patient by this call.

    Args:
        care_plan_id: Id class — the reference number of the insured plan of care the visits are planned under, as
            returned by the plan-of-care lookup.
        visit_date: Fixed-format class — the date of service of the earliest past visit the request asks the payer to
            cover, in YYYY-MM-DD format; an extension request covers only visits still to come, so pass "" (an empty
            string).
        source_event_id: Id class — the reference number of a payer denial the request contests, as returned by the
            plan-of-care history lookup; an extension request contests no denial, so pass "" (an empty string).
        requested_visits: Fixed-format class — the number of visits the request asks the payer to authorize, a
            non-negative integer (visits).

    Returns:
        A dictionary confirming the request: request_id (string, the reference number of the new request entry),
        care_plan_id (string), auth_kind (string, always extension), requested_visits (integer), event_date (string,
        YYYY-MM-DD, the date submitted) and status (string, always awaiting_payer_answer). A returned request_id means
        the request has been submitted.
    """
    rows = ctx.find("care_plans", care_plan_id=care_plan_id)
    plan = rows[0] if rows else {}
    visits = int(requested_visits)
    rid = ctx.make_id("cpe_", care_plan_id, visit_date, source_event_id, visits, "extension")
    today = ctx.now()[:10]
    ctx.create("care_plan_events", rid, care_plan_event_id=rid, care_plan_id=care_plan_id,
               customer_id=plan.get("customer_id", ""), event_type="plan_auth_requested", event_date=today,
               auth_kind="extension", requested_visits=visits, visit_date=visit_date, source_event_id=source_event_id)
    return {"request_id": rid, "care_plan_id": care_plan_id, "auth_kind": "extension", "requested_visits": visits,
            "event_date": today, "status": "awaiting_payer_answer"}


@tool(owner="user", rw="write")
def sign_noncovered_waiver_5d672975(ctx: ToolContext, care_plan_id: str, waiver_kind: str, visit_date: str) -> dict:
    """Sign, as the patient, an advance financial-responsibility waiver on your own insured plan of care for the
    visits your insurance is not expected to cover because its yearly visit limit has been reached.

    You (the patient) e-sign one waiver form, recorded today on your plan of care, accepting that visits from the
    first date of service given onward that run past your payer's calendar-year visit limit are billed to you. The
    signed waiver then shows in your plan's history; it covers no visit dated before that first date.

    Args:
        care_plan_id: Id class — the reference number of your insured plan of care, as given to you by the
            representative from the plan-of-care lookup.
        waiver_kind: Enum class — the form you sign: abn when your plan is a Medicare plan and the form is the Medicare
            Advance Beneficiary Notice of Noncoverage; commercial_waiver when your plan is a commercial insurance plan
            and the form is the commercial non-covered services waiver.
        visit_date: Fixed-format class — the first date of service the waiver covers, in YYYY-MM-DD format, as given
            to you by the representative.

    Returns:
        A dictionary confirming the signature: waiver_id (string, the reference number of the signed waiver entry),
        care_plan_id (string), waiver_kind (string, abn or commercial_waiver), visit_date (string, YYYY-MM-DD, the
        first date of service covered) and event_date (string, YYYY-MM-DD, the date signed). A returned waiver_id means
        the waiver is on file.
    """
    rows = ctx.find("care_plans", care_plan_id=care_plan_id)
    plan = rows[0] if rows else {}
    rid = ctx.make_id("cpe_", care_plan_id, waiver_kind, visit_date)
    today = ctx.now()[:10]
    ctx.create("care_plan_events", rid, care_plan_event_id=rid, care_plan_id=care_plan_id,
               customer_id=plan.get("customer_id", ""), event_type="plan_waiver_signed", event_date=today,
               waiver_kind=waiver_kind, visit_date=visit_date)
    return {"waiver_id": rid, "care_plan_id": care_plan_id, "waiver_kind": waiver_kind, "visit_date": visit_date,
            "event_date": today}

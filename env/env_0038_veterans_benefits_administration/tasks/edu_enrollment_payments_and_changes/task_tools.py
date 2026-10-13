"""Hidden task tools for the edu_enrollment_payments_and_changes difficulty.

Each tool performs exactly one atomic business write on the education records. None of them checks
eligibility, verification, timing, entitlement or any other business precondition: those judgements
are made by the representative from the published policy and the records before the call.
"""

from erlbench import ToolContext, tool


@tool(owner="user", rw="write")
def verify_enrollment_month_96d675a6(ctx: ToolContext, source_enrollment_id: str, verification_month: str,
                                     verification_channel: str, rate_of_pursuit_pct: int) -> str:
    """The student's own monthly enrollment verification: the student confirms, for one completed month of a
    school's term certification, that they attended the enrollment read back to them, stated as the rate of
    pursuit the month is measured at. One call records one verification entry for that certification and
    month on the student's education benefit, carrying the month, the channel the student used and the
    confirmed rate of pursuit; nothing else on the benefit, the certification or any payment changes. Once
    recorded, the verification shows on the student's enrollment history for that month. The call succeeds
    when the receipt returns status "verified" with the new verification reference number.

    Args:
        source_enrollment_id: Id class — the reference number of the school's term certification being
            verified, as shown on the student's enrollment records found for this caller.
        verification_month: Fixed-format class — the calendar month of training being verified, written
            YYYY-MM (four-digit year, hyphen, two-digit month), no day and no time zone.
        verification_channel: Enum class — how the student gives this verification; exactly one of:
            online when the student confirms through the VA website;
            text_message when the student confirms by replying to the verification text message;
            phone when the student confirms by telephone on a call with the representative;
            not_applicable when the entry is not a student statement at all (never used for a verification
            the student gives).
        rate_of_pursuit_pct: Fixed-format class — the rate of pursuit the student confirms for the month,
            as an integer percent (integer percent, whole number from 0 to 100, no decimal places and no
            percent sign).

    Returns:
        A dictionary with: status (text, always "verified" on success); verification_id (text, the
        reference number of the new verification entry); source_enrollment_id (text, the certification
        verified); verification_month (text, YYYY-MM); verification_channel (text, the channel recorded);
        rate_of_pursuit_pct (integer percent confirmed).
    """
    cert = ctx.find("edu_enrollments", enrollment_id=source_enrollment_id)
    cert = cert[0] if cert else {}
    rid = ctx.make_id("ever_", source_enrollment_id, verification_month, verification_channel, rate_of_pursuit_pct)
    ctx.create("edu_enrollments", rid, enrollment_id=rid, edu_benefit_id=cert.get("edu_benefit_id"),
               customer_id=cert.get("customer_id"), event_type="edu_enrollment_verified",
               school_name=cert.get("school_name"), facility_code=cert.get("facility_code"),
               term_start_date=cert.get("term_start_date"), term_end_date=cert.get("term_end_date"),
               source_enrollment_id=source_enrollment_id, verification_month=verification_month,
               verification_channel=verification_channel, rate_of_pursuit_pct=int(rate_of_pursuit_pct),
               amendment_reason="not_applicable")
    return str({"status": "verified", "verification_id": rid, "source_enrollment_id": source_enrollment_id,
                "verification_month": verification_month, "verification_channel": verification_channel,
                "rate_of_pursuit_pct": int(rate_of_pursuit_pct)})


@tool(owner="agent", rw="write")
def release_monthly_benefit_payment_750f9b6a(ctx: ToolContext, enrollment_id: str, payment_month: str,
                                             days_paid: int, amount: float) -> str:
    """Release the flat monthly education benefit (Chapter 30, 35 or 1606) to the student for one month of
    training under a school's term certification. One call issues one monthly payment to the student for
    that certification and month, dated today, with the days of the month it covers and the amount paid;
    the payment is added to the money paid on the student's education benefit and is delivered by the
    payment method already on the benefit. Nothing else on the benefit or the certification changes. The
    student can see the payment on their payment history from the issue date. The call succeeds when the
    receipt returns status "issued" with the new payment reference number.

    Args:
        enrollment_id: Id class — the reference number of the school's term certification the month of
            training belongs to, as shown on the student's enrollment records.
        payment_month: Fixed-format class — the calendar month of training paid, written YYYY-MM (four-digit
            year, hyphen, two-digit month), no day and no time zone.
        days_paid: Fixed-format class — the days of that month the payment covers, as integer days 0-30
            (a whole number, a full month counting as 30).
        amount: Fixed-format class — the amount paid to the student, in USD, 2 decimal places, signed
            (USD, 2 decimal places, signed; positive for a payment, rounded half up to the cent before the
            call, no currency symbol).

    Returns:
        A dictionary with: status (text, always "issued" on success); edu_payment_id (text, the reference
        number of the new payment); enrollment_id (text, the certification paid); payment_month (text,
        YYYY-MM); payment_date (text, YYYY-MM-DD issue date); days_paid (integer days covered); amount
        (number, USD to 2 decimal places).
    """
    cert = ctx.find("edu_enrollments", enrollment_id=enrollment_id)
    cert = cert[0] if cert else {}
    rid = ctx.make_id("epay_", enrollment_id, payment_month, days_paid, amount)
    paid_on = ctx.now()[:10]
    ctx.create("edu_payments", rid, edu_payment_id=rid, edu_benefit_id=cert.get("edu_benefit_id"),
               customer_id=cert.get("customer_id"), event_type="edu_monthly_benefit_payment",
               enrollment_id=enrollment_id, payment_month=payment_month, payment_date=paid_on, payee="student",
               days_paid=int(days_paid), amount=round(float(amount), 2), return_reason="not_applicable")
    return str({"status": "issued", "edu_payment_id": rid, "enrollment_id": enrollment_id,
                "payment_month": payment_month, "payment_date": paid_on, "days_paid": int(days_paid),
                "amount": round(float(amount), 2)})


@tool(owner="agent", rw="write")
def restore_amended_entitlement_47573840(ctx: ToolContext, enrollment_id: str, restoration_reason: str, days: int,
                                         charge_period_start: str, charge_period_end: str) -> str:
    """Give back education entitlement charged for a term certification whose training was cut short. One call
    records one restoration entry on the student's entitlement history for that certification, with the days
    given back, the first and last day of training they cover and the reason, and adds those days to the
    entitlement remaining on the student's education benefit. Nothing else on the benefit, the certification or
    any payment changes. The student sees the higher entitlement balance on their benefit straight away. The call
    succeeds when the receipt returns status "restored" with the new restoration reference number.

    Args:
        enrollment_id: Id class — the reference number of the school's term certification whose charged
            entitlement is given back, as shown on the student's enrollment and entitlement records.
        restoration_reason: Enum class — why the entitlement is given back; exactly one of:
            amended_enrollment when the school reported a reduction or withdrawal that left days no longer certified;
            school_closure when the school closed during the term;
            program_disapproval when the student's program lost its approval during the term;
            not_applicable when the entry is a charge rather than a restoration (never used for a restoration).
        days: Fixed-format class — the entitlement days given back, as integer days (a whole number, positive).
        charge_period_start: Fixed-format class — the first day of training the restoration covers, written
            YYYY-MM-DD, no time and no time zone.
        charge_period_end: Fixed-format class — the last day of training the restoration covers, written
            YYYY-MM-DD, no time and no time zone.

    Returns:
        A dictionary with: status (text, always "restored" on success); entitlement_txn_id (text, the reference
        number of the restoration entry); enrollment_id (text, the certification); days (integer days given back);
        charge_period_start and charge_period_end (text, YYYY-MM-DD); entitlement_days_remaining (integer days now
        remaining on the benefit).
    """
    cert = ctx.find("edu_enrollments", enrollment_id=enrollment_id)
    cert = cert[0] if cert else {}
    bid = cert.get("edu_benefit_id")
    rid = ctx.make_id("erst_", enrollment_id, restoration_reason, days, charge_period_start, charge_period_end)
    ctx.create("edu_entitlement_ledger", rid, entitlement_txn_id=rid, edu_benefit_id=bid,
               customer_id=cert.get("customer_id"), event_type="edu_entitlement_restored", enrollment_id=enrollment_id,
               days=int(days), charge_period_start=charge_period_start, charge_period_end=charge_period_end,
               restoration_reason=restoration_reason)
    ben = ctx.find("edu_benefits", edu_benefit_id=bid)
    remaining = int((ben[0].get("entitlement_days_remaining") if ben else 0) or 0) + int(days)
    if ben:
        ctx.update("edu_benefits", bid, entitlement_days_remaining=remaining)
    return str({"status": "restored", "entitlement_txn_id": rid, "enrollment_id": enrollment_id, "days": int(days),
                "charge_period_start": charge_period_start, "charge_period_end": charge_period_end,
                "entitlement_days_remaining": remaining})


@tool(owner="user", rw="write")
def elect_post911_in_place_of_chapter_2e090e13(ctx: ToolContext, edu_benefit_id: str, post911_variant_name: str,
                                               post911_entitlement_days: int) -> str:
    """The student's own irrevocable election of the Post-9/11 GI Bill in place of a Montgomery GI Bill chapter
    they hold. One call marks that chapter relinquished as of today and, in the same election, opens the
    student's Post-9/11 GI Bill benefit at the benefit level stated, credited with the Post-9/11 entitlement days
    stated, payable to the same payment method and account as the relinquished chapter and with no delimiting
    date. The relinquished chapter can never be used again. The student sees the relinquished chapter and the
    new Post-9/11 benefit on their education benefits straight away. The call succeeds when the receipt returns
    status "elected" with the new Post-9/11 benefit reference number.

    Args:
        edu_benefit_id: Id class — the reference number of the education benefit being relinquished, as shown on
            the student's education benefits.
        post911_variant_name: Enum class — the Post-9/11 GI Bill benefit level opened by the election; exactly one of:
            Montgomery GI Bill - Selected Reserve (Chapter 1606) never applies to an election (it is not a Post-9/11 level);
            Survivors' and Dependents' Educational Assistance (Chapter 35) never applies to an election (it is not a Post-9/11 level);
            Montgomery GI Bill - Active Duty (Chapter 30) never applies to an election (it is not a Post-9/11 level);
            Post-9/11 GI Bill (Chapter 33) - 60% Benefit Level when aggregate post-9/11 active service is 6 to less than 18 months;
            Post-9/11 GI Bill (Chapter 33) - 70% Benefit Level when it is 18 to less than 24 months;
            Post-9/11 GI Bill (Chapter 33) - 80% Benefit Level when it is 24 to less than 30 months;
            Post-9/11 GI Bill (Chapter 33) - 90% Benefit Level when it is 30 to less than 36 months;
            Post-9/11 GI Bill (Chapter 33) - 100% Benefit Level when it is 36 months or more, or a Purple Heart, or 30 continuous days with a service-connected disability discharge.
        post911_entitlement_days: Fixed-format class — the Post-9/11 entitlement credited on the election, as
            integer days (integer days (one month = 30 days), a whole number).

    Returns:
        A dictionary with: status (text, always "elected" on success); relinquished_benefit_id (text, the chapter
        given up); relinquished_on (text, YYYY-MM-DD date of the election); post911_benefit_id (text, the reference
        number of the new Post-9/11 benefit); post911_variant_name (text, the level opened);
        post911_entitlement_days (integer days credited).
    """
    old = ctx.find("edu_benefits", edu_benefit_id=edu_benefit_id)
    old = old[0] if old else {}
    today = ctx.now()[:10]
    ctx.update("edu_benefits", edu_benefit_id, status="relinquished", closed_date=today)
    nid = ctx.make_id("e33_", edu_benefit_id, post911_variant_name, post911_entitlement_days)
    ctx.create("edu_benefits", nid, edu_benefit_id=nid, customer_id=old.get("customer_id"),
               variant_name=post911_variant_name, status="active",
               original_entitlement_days=int(post911_entitlement_days),
               entitlement_days_remaining=int(post911_entitlement_days), delimiting_date="", coe_issued_date=today,
               yellow_ribbon_school_agreement=False, payment_method=old.get("payment_method"),
               payment_account_last4=old.get("payment_account_last4"), opened_date=today, closed_date="")
    return str({"status": "elected", "relinquished_benefit_id": edu_benefit_id, "relinquished_on": today,
                "post911_benefit_id": nid, "post911_variant_name": post911_variant_name,
                "post911_entitlement_days": int(post911_entitlement_days)})

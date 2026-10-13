"""Hidden task tools for difficulty weekly_certification_and_benefit_payment (category claim) of
env_0049_state_unemployment_insurance_agency (Lakeland Department of Workforce Security).

Each tool performs one atomic write on the claim records with the values passed in; it checks
no eligibility, computes no benefit figure and refuses nothing. Dates come only from ctx.now().
"""

from erlbench import ToolContext, tool


class _Cal:
    """Pure-arithmetic calendar helpers (proleptic Gregorian ordinal days, no clock access)."""

    HOLIDAYS = ("2026-01-01", "2026-01-19", "2026-02-16", "2026-05-25", "2026-06-19", "2026-07-03",
                "2026-09-07", "2026-11-11", "2026-11-26", "2026-11-27", "2026-12-25",
                "2027-01-01", "2027-01-18", "2027-02-15", "2027-05-31", "2027-06-18", "2027-07-05",
                "2027-09-06", "2027-11-11", "2027-11-25", "2027-11-26", "2027-12-24")

    @staticmethod
    def to_ord(text):
        y, m, d = int(text[0:4]), int(text[5:7]), int(text[8:10])
        y2 = y - 1 if m <= 2 else y
        era = y2 // 400
        yoe = y2 - era * 400
        mp = (m + 9) % 12
        doy = (153 * mp + 2) // 5 + d - 1
        doe = yoe * 365 + yoe // 4 - yoe // 100 + doy
        return era * 146097 + doe

    @staticmethod
    def from_ord(n):
        era = n // 146097
        doe = n - era * 146097
        yoe = (doe - doe // 1460 + doe // 36524 - doe // 146096) // 365
        y = yoe + era * 400
        doy = doe - (365 * yoe + yoe // 4 - yoe // 100)
        mp = (5 * doy + 2) // 153
        d = doy - (153 * mp + 2) // 5 + 1
        m = mp + 3 if mp < 10 else mp - 9
        if m <= 2:
            y += 1
        return f"{y:04d}-{m:02d}-{d:02d}"

    @staticmethod
    def weekday(n):
        # 0 = Monday ... 6 = Sunday (ordinal 0 is 0000-03-01, a Wednesday)
        return (n + 2) % 7

    @staticmethod
    def add_business_days(text, count):
        n = _Cal.to_ord(text)
        left = int(count)
        while left > 0:
            n += 1
            if _Cal.weekday(n) < 5 and _Cal.from_ord(n) not in _Cal.HOLIDAYS:
                left -= 1
        return _Cal.from_ord(n)

    @staticmethod
    def add_days(text, days):
        return _Cal.from_ord(_Cal.to_ord(text) + int(days))


@tool(owner="agent", rw="write")
def record_dependency_redetermination_c7b3c182(ctx: ToolContext, claim_id: str, dependency_allowance: float,
                                               amount: float) -> str:
    """Issue a dependency redetermination on one unemployment benefit claim: set the claim's weekly
    dependency allowance to the redetermined figure and credit the increase in the maximum benefit
    amount. On success the claim shows the new dependency allowance, a maximum benefit amount and a
    remaining balance both raised by the credited amount, the next determination number and today's
    date as its latest monetary determination date, and the claim's payment history gains one
    entitlement-credit entry for the credited amount.

    Args:
        claim_id: Id class — the claim reference number of the claim being redetermined, read from the claim lookup before the call.
        dependency_allowance: Fixed-format class — the redetermined weekly dependency allowance for the claim, in USD, 2 decimal places, rounded to the cent as passed.
        amount: Fixed-format class — the increase in the maximum benefit amount credited to the remaining balance,, in USD, 2 decimal places, always positive.

    Returns:
        A dict confirming the redetermination: entry_id (text, the reference number of the
        entitlement-credit entry), claim_id (text), determination_number (integer, the new
        determination number), dependency_allowance (number, USD per week), credited (number, USD),
        max_benefit_amount (number, USD, after the credit) and remaining_balance (number, USD,
        after the credit). Receiving entry_id means the redetermination is on the claim.
    """
    claim = (ctx.find("claims", claim_id=claim_id) or [{}])[0]
    det = int(claim.get("determination_number") or 0) + 1
    credit = round(float(amount), 2)
    mba = round(float(claim.get("max_benefit_amount") or 0) + credit, 2)
    bal = round(float(claim.get("remaining_balance") or 0) + credit, 2)
    today = ctx.now()[:10]
    rid = ctx.make_id("cl_", claim_id, dependency_allowance, amount)
    ctx.create("claim_ledger", rid, ledger_entry_id=rid, claim_id=claim_id, customer_id=claim.get("customer_id"),
               event_type="claim_entitlement_credited", entry_date=today, week_ending_date="",
               determination_number=det, payment_kind="not_applicable", amount=credit,
               earnings_deduction=0.00, other_pay_deduction=0.00, offset_amount=0.00, offset_applied=False,
               withholding_applied=False, charge_code="not_applicable", payment_method="not_applicable",
               original_payment_id=None, cancel_reason="none")
    ctx.update("claims", claim_id, dependency_allowance=round(float(dependency_allowance), 2),
               max_benefit_amount=mba, remaining_balance=bal, determination_number=det,
               monetary_determination_date=today, monetary_status="eligible")
    return str({"entry_id": rid, "claim_id": claim_id, "determination_number": det,
                "dependency_allowance": round(float(dependency_allowance), 2), "credited": credit,
                "max_benefit_amount": mba, "remaining_balance": bal})


@tool(owner="user", rw="write")
def elect_payment_method_0e517696(ctx: ToolContext, claim_id: str, payment_method: str,
                                  lead_business_days: int) -> str:
    """Record the claimant's own election of how benefits on one claim are paid. The claimant makes
    this election personally. On success the claim shows the elected payment method and a payment
    method effective date that falls the given number of business days (Monday through Friday,
    excluding Lakeland state holidays) after today; payments issued on or after that date use the
    elected method.

    Args:
        claim_id: Id class — the claim reference number of the claimant's claim, read to the claimant by the agent from the claim lookup.
        payment_method: Enum class — the method the claimant elects: direct_deposit_checking when benefits go by direct deposit to a checking account in the claimant's name; direct_deposit_savings when they go by direct deposit to a savings account in the claimant's name; debit_card when they go to the state benefit debit card; paper_check when they are mailed as a paper check to the mailing address of record.
        lead_business_days: Fixed-format class — the election lead time, an integer number of business days counted from the day after today, as told to the claimant by the agent.

    Returns:
        A dict confirming the election: claim_id (text), payment_method (text, the elected method)
        and payment_method_effective_date (text, YYYY-MM-DD, the first payment date that uses the
        elected method). Receiving payment_method_effective_date means the election is recorded.
    """
    eff = _Cal.add_business_days(ctx.now()[:10], int(lead_business_days))
    ctx.update("claims", claim_id, payment_method=payment_method, payment_method_effective_date=eff)
    return str({"claim_id": claim_id, "payment_method": payment_method, "payment_method_effective_date": eff})


@tool(owner="agent", rw="write")
def issue_supplemental_payment_38b81267(ctx: ToolContext, claim_id: str, customer_id: str, week_ending_date: str,
                                        payment_kind: str, payment_method: str, amount: float) -> str:
    """Issue one supplemental benefit payment that corrects a week already paid short on a claim of a
    program not charged to employers. On success the claim's payment history gains one payment entry
    for that week with the given kind, method and amount, issued today, with no overpayment offset and
    no withholding taken; the amount is debited from the claim's remaining balance, and a claim whose
    remaining balance reaches zero shows status exhausted.

    Args:
        claim_id: Id class — the claim reference number of the claim paid, read from the claim lookup before the call.
        customer_id: Id class — the claimant's customer reference number, read from the profile lookup before the call.
        week_ending_date: Fixed-format class — the Saturday ending the benefit week being corrected, written YYYY-MM-DD (always a Saturday).
        payment_kind: Enum class — the kind of payment entry: weekly for the first payment of a certified week; supplemental for a correction added to a week already paid; reissue for a replacement of a cancelled payment; not_applicable for an entry that is not a payment, never used for a payment.
        payment_method: Enum class — how the payment is issued: direct_deposit_checking for direct deposit to the claimant's checking account; direct_deposit_savings for direct deposit to the claimant's savings account; debit_card for the state benefit debit card; paper_check for a check mailed to the address of record; not_applicable for an entry that is not a payment, never used for a payment.
        amount: Fixed-format class — the gross amount of the payment, in USD, 2 decimal places, always positive.

    Returns:
        A dict confirming the payment: entry_id (text, the payment reference number), claim_id
        (text), week_ending_date (text, YYYY-MM-DD), amount (number, USD), remaining_balance
        (number, USD, after the payment) and status (text, the claim status after the payment).
        Receiving entry_id means the payment is issued.
    """
    claim = (ctx.find("claims", claim_id=claim_id) or [{}])[0]
    amt = round(float(amount), 2)
    bal = round(float(claim.get("remaining_balance") or 0) - amt, 2)
    status = "exhausted" if bal <= 0 else claim.get("status")
    rid = ctx.make_id("cl_", claim_id, customer_id, week_ending_date, payment_kind, payment_method, amount)
    ctx.create("claim_ledger", rid, ledger_entry_id=rid, claim_id=claim_id, customer_id=customer_id,
               event_type="claim_benefit_paid", entry_date=ctx.now()[:10], week_ending_date=week_ending_date,
               determination_number=0, payment_kind=payment_kind, amount=amt, offset_amount=0.00,
               offset_applied=False, withholding_applied=False, charge_code="non_charged",
               payment_method=payment_method, original_payment_id=None, cancel_reason="none")
    ctx.update("claims", claim_id, remaining_balance=bal, status=status)
    return str({"entry_id": rid, "claim_id": claim_id, "week_ending_date": week_ending_date, "amount": amt,
                "remaining_balance": bal, "status": status})


@tool(owner="agent", rw="write")
def determine_extension_entitlement_db601fac(ctx: ToolContext, claim_id: str, parent_claim_id: str,
                                             weekly_benefit_amount: float, dependency_allowance: float,
                                             max_benefit_amount: float) -> str:
    """Record the first monetary determination on a filed Extended Benefits claim. On success the
    Extended Benefits claim shows the weekly benefit amount and dependency allowance carried from its
    parent claim, the determined maximum benefit amount, an equal remaining balance, monetary status
    eligible, determination number 1, today's date as its monetary determination date and status
    active, and its payment history gains one entitlement-credit entry for the maximum benefit amount.

    Args:
        claim_id: Id class — the claim reference number of the filed Extended Benefits claim, read from the claim lookup before the call.
        parent_claim_id: Id class — the claim reference number of the parent claim the Extended Benefits claim extends, read from the parent field of the Extended Benefits claim.
        weekly_benefit_amount: Fixed-format class — the weekly benefit amount carried to the Extended Benefits claim, in USD, whole dollars with 2 decimal places.
        dependency_allowance: Fixed-format class — the weekly dependency allowance carried to the Extended Benefits claim, in USD, 2 decimal places.
        max_benefit_amount: Fixed-format class — the determined Extended Benefits maximum benefit amount, in USD, whole dollars with 2 decimal places.

    Returns:
        A dict confirming the determination: entry_id (text, the entitlement-credit reference
        number), claim_id (text), status (text, active), max_benefit_amount (number, USD) and
        remaining_balance (number, USD). Receiving entry_id means the determination is recorded.
    """
    claim = (ctx.find("claims", claim_id=claim_id) or [{}])[0]
    mba = round(float(max_benefit_amount), 2)
    today = ctx.now()[:10]
    rid = ctx.make_id("cl_", claim_id, parent_claim_id, weekly_benefit_amount, dependency_allowance, max_benefit_amount)
    ctx.create("claim_ledger", rid, ledger_entry_id=rid, claim_id=claim_id, customer_id=claim.get("customer_id"),
               event_type="claim_entitlement_credited", entry_date=today, week_ending_date="",
               determination_number=1, payment_kind="not_applicable", amount=mba, earnings_deduction=0.00,
               other_pay_deduction=0.00, offset_amount=0.00, offset_applied=False, withholding_applied=False,
               charge_code="not_applicable", payment_method="not_applicable", original_payment_id=None,
               cancel_reason="none")
    ctx.update("claims", claim_id, weekly_benefit_amount=round(float(weekly_benefit_amount), 2),
               dependency_allowance=round(float(dependency_allowance), 2), max_benefit_amount=mba,
               remaining_balance=mba, monetary_status="eligible", determination_number=1,
               monetary_determination_date=today, status="active")
    return str({"entry_id": rid, "claim_id": claim_id, "status": "active", "max_benefit_amount": mba,
                "remaining_balance": mba})


@tool(owner="agent", rw="write")
def record_dependency_disallowance_f94a20ca(ctx: ToolContext, claim_id: str, dependency_allowance: float,
                                            amount: float) -> str:
    """Issue a dependency disallowance on one unemployment benefit claim: set the claim's weekly
    dependency allowance to the redetermined figure and debit the reduction from the maximum benefit
    amount. On success the claim shows the new dependency allowance, a maximum benefit amount and a
    remaining balance both lowered by the reduction, the next determination number and today's date
    as its latest monetary determination date, and the claim's payment history gains one
    entitlement-reduction entry for the reduction. Payments already issued are untouched.

    Args:
        claim_id: Id class — the claim reference number of the claim being redetermined, read from the claim lookup before the call.
        dependency_allowance: Fixed-format class — the redetermined weekly dependency allowance for the claim, in USD, 2 decimal places, rounded to the cent as passed.
        amount: Fixed-format class — the reduction debited from the maximum benefit amount and the remaining balance, in USD, 2 decimal places, always positive.

    Returns:
        A dict confirming the disallowance: entry_id (text, the reference number of the
        entitlement-reduction entry), claim_id (text), determination_number (integer, the new
        determination number), dependency_allowance (number, USD per week), reduced (number, USD),
        max_benefit_amount (number, USD, after the reduction) and remaining_balance (number, USD,
        after the reduction). Receiving entry_id means the disallowance is on the claim.
    """
    claim = (ctx.find("claims", claim_id=claim_id) or [{}])[0]
    det = int(claim.get("determination_number") or 0) + 1
    red = round(float(amount), 2)
    mba = round(float(claim.get("max_benefit_amount") or 0) - red, 2)
    bal = round(float(claim.get("remaining_balance") or 0) - red, 2)
    today = ctx.now()[:10]
    rid = ctx.make_id("cl_", claim_id, dependency_allowance, amount)
    ctx.create("claim_ledger", rid, ledger_entry_id=rid, claim_id=claim_id, customer_id=claim.get("customer_id"),
               event_type="claim_entitlement_reduced", entry_date=today, week_ending_date="",
               determination_number=det, payment_kind="not_applicable", amount=red,
               earnings_deduction=0.00, other_pay_deduction=0.00, offset_amount=0.00, offset_applied=False,
               withholding_applied=False, charge_code="not_applicable", payment_method="not_applicable",
               original_payment_id=None, cancel_reason="none")
    ctx.update("claims", claim_id, dependency_allowance=round(float(dependency_allowance), 2),
               max_benefit_amount=mba, remaining_balance=bal, determination_number=det,
               monetary_determination_date=today)
    return str({"entry_id": rid, "claim_id": claim_id, "determination_number": det,
                "dependency_allowance": round(float(dependency_allowance), 2), "reduced": red,
                "max_benefit_amount": mba, "remaining_balance": bal})


@tool(owner="user", rw="write")
def certify_week_by_phone_ea18d1f2(ctx: ToolContext, claim_id: str, week_ending_date: str, cert_timeliness: str,
                                   able_and_available: bool, work_refused: bool, gross_earnings: float,
                                   hours_worked: float, work_search_contacts: int, other_pay_type: str,
                                   other_pay_amount: float) -> str:
    """The claimant certifies one benefit week on the phone line, answering the weekly questions
    personally. On success the claim carries one weekly certification for that week, filed today
    through the phone line, with the answers, earnings, hours, work-search contacts and other pay
    entered, and the timeliness class given.

    Args:
        claim_id: Id class — the claim reference number of the claimant's claim, read to the claimant by the agent from the claim lookup.
        week_ending_date: Fixed-format class — the Saturday ending the week certified, written YYYY-MM-DD (always a Saturday).
        cert_timeliness: Enum class — the timeliness class of this certification: timely when it is filed within the certification window after the week ended; late_good_cause when it is filed after the window with an approved late-certification request inside the good-cause limit; late_no_good_cause when it is filed after the window without such approval.
        able_and_available: Enum class — the claimant's answer about the whole week: true when the claimant was able and available for full-time work all week; false when the claimant was not.
        work_refused: Enum class — the claimant's answer about offers of work: true when the claimant refused an offer of work during the week; false when no offer was refused.
        gross_earnings: Fixed-format class — gross earnings for work performed in the week as the claimant states them, in USD, 2 decimal places.
        hours_worked: Fixed-format class — hours worked in the week as the claimant states them, in decimal hours, 1 decimal place.
        work_search_contacts: Fixed-format class — the number of work-search contacts made in the week, an integer count.
        other_pay_type: Enum class — the kind of other pay for the week: none when no other pay was received; vacation_pay when vacation pay was paid for the week; holiday_pay when holiday pay was paid for a holiday in the week; severance_pay when severance or dismissal pay was received; pension_employer_funded when a pension wholly paid for by a base-period employer was received; pension_claimant_contributed when a pension the claimant paid into was received.
        other_pay_amount: Fixed-format class — the amount of the other pay for the week as the agent tells the claimant to enter it, in USD, 2 decimal places; 0.00 when none.

    Returns:
        A dict confirming the certification: certification_id (text, the reference number of the
        certification), claim_id (text), week_ending_date (text, YYYY-MM-DD), certified_date (text,
        YYYY-MM-DD, today) and cert_channel (text, phone_line). Receiving certification_id means
        the week is certified.
    """
    today = ctx.now()[:10]
    claim = (ctx.find("claims", claim_id=claim_id) or [{}])[0]
    rid = ctx.make_id("cc_", claim_id, week_ending_date, cert_timeliness, able_and_available, work_refused,
                      gross_earnings, hours_worked, work_search_contacts, other_pay_type, other_pay_amount)
    ctx.create("claim_certifications", rid, certification_id=rid, claim_id=claim_id, customer_id=claim.get("customer_id"),
               event_type="claim_week_certified", week_ending_date=week_ending_date, certified_date=today,
               cert_channel="phone_line", cert_timeliness=cert_timeliness, able_and_available=bool(able_and_available),
               work_refused=bool(work_refused), gross_earnings=round(float(gross_earnings), 2),
               hours_worked=round(float(hours_worked), 1), work_search_contacts=int(work_search_contacts),
               other_pay_type=other_pay_type, other_pay_amount=round(float(other_pay_amount), 2))
    return str({"certification_id": rid, "claim_id": claim_id, "week_ending_date": week_ending_date,
                "certified_date": today, "cert_channel": "phone_line"})


@tool(owner="agent", rw="write")
def record_waiting_week_428070c9(ctx: ToolContext, claim_id: str, week_ending_date: str, amount: float) -> str:
    """Record one certified week of a claim as the unpaid waiting week of its benefit year, stating the
    value the week would have paid. On success the claim's payment history gains one waiting-week
    entry dated today for that week with the value given; nothing is paid and the remaining balance is
    unchanged.

    Args:
        claim_id: Id class — the claim reference number of the claim, read from the claim lookup before the call.
        week_ending_date: Fixed-format class — the Saturday ending the week served as the waiting week, written YYYY-MM-DD (always a Saturday).
        amount: Fixed-format class — the value the week would have paid, in USD, 2 decimal places, always positive.

    Returns:
        A dict confirming the entry: entry_id (text, the reference number of the waiting-week
        entry), claim_id (text), week_ending_date (text, YYYY-MM-DD) and amount (number, USD).
        Receiving entry_id means the waiting week is recorded as served.
    """
    claim = (ctx.find("claims", claim_id=claim_id) or [{}])[0]
    rid = ctx.make_id("cl_", claim_id, week_ending_date, amount)
    ctx.create("claim_ledger", rid, ledger_entry_id=rid, claim_id=claim_id, customer_id=claim.get("customer_id"),
               event_type="claim_waiting_week_served", entry_date=ctx.now()[:10], week_ending_date=week_ending_date,
               determination_number=0, payment_kind="not_applicable", amount=round(float(amount), 2),
               earnings_deduction=0.00, other_pay_deduction=0.00, offset_amount=0.00, offset_applied=False,
               withholding_applied=False, charge_code="not_applicable", payment_method="not_applicable",
               original_payment_id=None, cancel_reason="none")
    return str({"entry_id": rid, "claim_id": claim_id, "week_ending_date": week_ending_date,
                "amount": round(float(amount), 2)})


@tool(owner="agent", rw="write")
def issue_weekly_payment_6cd10c49(ctx: ToolContext, claim_id: str, customer_id: str, week_ending_date: str,
                                  payment_kind: str, payment_method: str, amount: float) -> str:
    """Issue the weekly benefit payment for one certified week on a claim of a program not charged to
    employers. On success the claim's payment history gains one payment entry for that week with the
    given kind, method and amount, issued today, with no overpayment offset and no withholding taken;
    the amount is debited from the claim's remaining balance, and a claim whose remaining balance
    reaches zero shows status exhausted.

    Args:
        claim_id: Id class — the claim reference number of the claim paid, read from the claim lookup before the call.
        customer_id: Id class — the claimant's customer reference number, read from the profile lookup before the call.
        week_ending_date: Fixed-format class — the Saturday ending the benefit week paid, written YYYY-MM-DD (always a Saturday).
        payment_kind: Enum class — the kind of payment entry: weekly for the first payment of a certified week; supplemental for a correction added to a week already paid; reissue for a replacement of a cancelled payment; not_applicable for an entry that is not a payment, never used for a payment.
        payment_method: Enum class — how the payment is issued: direct_deposit_checking for direct deposit to the claimant's checking account; direct_deposit_savings for direct deposit to the claimant's savings account; debit_card for the state benefit debit card; paper_check for a check mailed to the address of record; not_applicable for an entry that is not a payment, never used for a payment.
        amount: Fixed-format class — the gross payable amount of the payment, in USD, 2 decimal places, always positive.

    Returns:
        A dict confirming the payment: entry_id (text, the payment reference number), claim_id
        (text), week_ending_date (text, YYYY-MM-DD), amount (number, USD), remaining_balance
        (number, USD, after the payment) and status (text, the claim status after the payment).
        Receiving entry_id means the payment is issued.
    """
    claim = (ctx.find("claims", claim_id=claim_id) or [{}])[0]
    amt = round(float(amount), 2)
    bal = round(float(claim.get("remaining_balance") or 0) - amt, 2)
    status = "exhausted" if bal <= 0 else claim.get("status")
    rid = ctx.make_id("cl_", claim_id, customer_id, week_ending_date, payment_kind, payment_method, amount)
    ctx.create("claim_ledger", rid, ledger_entry_id=rid, claim_id=claim_id, customer_id=customer_id,
               event_type="claim_benefit_paid", entry_date=ctx.now()[:10], week_ending_date=week_ending_date,
               determination_number=0, payment_kind=payment_kind, amount=amt, offset_amount=0.00,
               offset_applied=False, withholding_applied=False, charge_code="non_charged",
               payment_method=payment_method, original_payment_id=None, cancel_reason="none")
    ctx.update("claims", claim_id, remaining_balance=bal, status=status)
    return str({"entry_id": rid, "claim_id": claim_id, "week_ending_date": week_ending_date, "amount": amt,
                "remaining_balance": bal, "status": status})

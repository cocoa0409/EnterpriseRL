"""Hidden task tools for transfers_and_enrollment_changes (Student Enrollment, Transfers and
Pre-Kindergarten Admissions) — Calloway Creek ISD.

Each tool performs exactly one atomic write on a Pre-Kindergarten (Tuition-Based) enrollment's
tuition ledger. No tool checks eligibility, prerequisites or amounts; the amounts are worked out
by the caller from the published rules and passed in as fixed-format values.
"""

from decimal import Decimal, ROUND_HALF_UP
import re

from erlbench import ToolContext, tool


class _Fmt:
    """Formatting helpers shared by the tools (not tools themselves)."""

    @staticmethod
    def money(value) -> float:
        """Exact half-up rounding of a USD amount to two decimal places."""
        return float(Decimal(str(value)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP))

    @staticmethod
    def is_month(text: str) -> bool:
        return bool(re.fullmatch(r"\d{4}-(0[1-9]|1[0-2])", str(text or "")))

    @staticmethod
    def confirmation(rid: str) -> str:
        """Payment confirmation number: the digits 75 followed by six digits derived from the entry."""
        return "75" + str(int(rid.split("_")[-1], 16) % 1000000).zfill(6)


@tool(owner="agent", rw="write")
def post_prek_late_fee_f766f23b(ctx: ToolContext, enrollment_id: str, billing_month: str, amount: float) -> str:
    """Post the monthly tuition late fee on a family's tuition-based Pre-K enrollment for one billing
    month. The support agent books one late fee entry on the enrollment's tuition account, dated
    today; it raises the amount the household owes on that enrollment by the fee. The family sees
    the late fee on the enrollment's tuition statement for that billing month. The call succeeds
    when the receipt confirms the new late fee entry and its reference.

    Args:
        enrollment_id: Id class — the reference number of the student's Pre-K enrollment record for
            the school year, as returned by the enrollment lookup for the household.
        billing_month: Fixed-format class — the billing month whose tuition was paid late, written
            YYYY-MM (four-digit year, hyphen, two-digit month), exactly as the billing month shown on
            that month's tuition charge.
        amount: Fixed-format class — the late fee to book, in US dollars as a positive number with
            2 decimal places; the tool rounds half up to the cent before booking.

    Returns:
        A one-line text receipt beginning "Late fee posted:" that gives the new ledger entry
        reference (text id), the enrollment reference (text id), the billing month (YYYY-MM), the
        amount booked (USD, two decimals) and the posting date (YYYY-MM-DD). A receipt beginning
        "Error:" means nothing was booked because an argument did not meet its format.
    """
    if not _Fmt.is_month(billing_month):
        return "Error: billing_month must be written YYYY-MM."
    amt = _Fmt.money(amount)
    if amt <= 0:
        return "Error: amount must be a positive USD amount with two decimal places."
    rows = ctx.find("enrollments", enrollment_id=enrollment_id)
    customer_id = rows[0].get("customer_id", "") if rows else ""
    rid = ctx.make_id("eld_", enrollment_id, billing_month, amt, "late_fee")
    posted = ctx.now()[:10]
    ctx.create("enrollment_ledger", rid, enrollment_ledger_id=rid, enrollment_id=enrollment_id,
               customer_id=customer_id, event_type="enroll_tuition_late_fee", amount=amt,
               posted_date=posted, billing_month=billing_month, proration="not_applicable",
               sibling_discount_applied=False, payment_method="not_applicable", payment_reference="",
               credit_reason="not_applicable", source_enrollment_ledger_id="")
    return (f"Late fee posted: entry {rid} on enrollment {enrollment_id}, billing month {billing_month}, "
            f"amount {amt:.2f} USD, posted {posted}.")


@tool(owner="agent", rw="write")
def credit_prek_combined_program_abf513c1(ctx: ToolContext, enrollment_ledger_id: str, amount: float) -> str:
    """Post the combined-program credit for a Pre-K child who also attends Creek Kids Club Pre-K
    Wraparound Care, against one tuition charge of the child's tuition-based Pre-K enrollment. The
    support agent books one credit entry, dated today, that offsets the named tuition charge and
    lowers the amount the household owes on that enrollment by the credit. The family sees the
    credit next to that month's tuition charge on the statement. The call succeeds when the receipt
    confirms the new credit entry and the charge it offsets.

    Args:
        enrollment_ledger_id: Id class — the identifier of the tuition charge entry being offset, as
            returned by the tuition ledger lookup for the enrollment.
        amount: Fixed-format class — the credit to book, in US dollars as a positive number with
            2 decimal places; the tool rounds half up to the cent before booking.

    Returns:
        A one-line text receipt beginning "Combined-program credit posted:" that gives the new
        credit entry reference (text id), the tuition charge reference it offsets (text id), the
        enrollment reference (text id), the amount booked (USD, two decimals) and the posting date
        (YYYY-MM-DD). A receipt beginning "Error:" means nothing was booked because the charge
        reference was not found or the amount did not meet its format.
    """
    amt = _Fmt.money(amount)
    if amt <= 0:
        return "Error: amount must be a positive USD amount with two decimal places."
    src = ctx.find("enrollment_ledger", enrollment_ledger_id=enrollment_ledger_id)
    if not src:
        return f"Error: no tuition ledger entry {enrollment_ledger_id}."
    s = src[0]
    rid = ctx.make_id("eld_", enrollment_ledger_id, amt, "billing_correction")
    posted = ctx.now()[:10]
    ctx.create("enrollment_ledger", rid, enrollment_ledger_id=rid, enrollment_id=s.get("enrollment_id", ""),
               customer_id=s.get("customer_id", ""), event_type="enroll_tuition_credit", amount=amt,
               posted_date=posted, billing_month="", proration="not_applicable",
               sibling_discount_applied=False, payment_method="not_applicable", payment_reference="",
               credit_reason="billing_correction", source_enrollment_ledger_id=enrollment_ledger_id)
    return (f"Combined-program credit posted: entry {rid} offsets charge {enrollment_ledger_id} on enrollment "
            f"{s.get('enrollment_id', '')}, amount {amt:.2f} USD, posted {posted}.")


@tool(owner="user", rw="write")
def pay_prek_tuition_in_advance_058a705f(ctx: ToolContext, enrollment_id: str, amount: float, payment_method: str) -> str:
    """Make the advance payment of the rest of the school year's Pre-K tuition on the family's
    tuition-based Pre-K enrollment through the district's online payment portal. The parent or
    guardian completes this payment personally; it books one tuition payment entry on the
    enrollment, dated today, which lowers the amount the household owes and leaves any amount beyond
    the open charges standing as a credit for the months it covers. The parent receives a payment
    confirmation number. The call succeeds when the receipt shows that confirmation number.

    Args:
        enrollment_id: Id class — the reference number of the student's Pre-K enrollment record for
            the school year, as given by the support agent from the enrollment lookup.
        amount: Fixed-format class — the advance payment amount quoted by the support agent, in US
            dollars as a positive number with 2 decimal places; the portal rounds half up
            to the cent.
        payment_method: Enum class — how the parent pays; exactly one of these values:
            online_card (the parent pays with a debit or credit card entered in the portal);
            ach_bank_draft (the parent pays from a checking or savings account by bank draft entered
            in the portal); personal_check (a paper check, taken only at the campus cashier, so the
            portal refuses it); money_order (taken only at the campus cashier, so the portal refuses
            it); not_applicable (no payment method, which the portal refuses).

    Returns:
        A one-line text receipt beginning "Advance payment received:" that gives the payment
        confirmation number (eight digits), the new ledger entry reference (text id), the
        enrollment reference (text id), the amount paid (USD, two decimals), the payment method and
        the posting date (YYYY-MM-DD). A receipt beginning "Error:" means no payment was taken
        because an argument did not meet its format.
    """
    if payment_method not in ("online_card", "ach_bank_draft"):
        return "Error: payment_method must be online_card or ach_bank_draft."
    amt = _Fmt.money(amount)
    if amt <= 0:
        return "Error: amount must be a positive USD amount with two decimal places."
    rows = ctx.find("enrollments", enrollment_id=enrollment_id)
    customer_id = rows[0].get("customer_id", "") if rows else ""
    rid = ctx.make_id("eld_", enrollment_id, amt, payment_method, "advance_payment")
    ref = _Fmt.confirmation(rid)
    posted = ctx.now()[:10]
    ctx.create("enrollment_ledger", rid, enrollment_ledger_id=rid, enrollment_id=enrollment_id,
               customer_id=customer_id, event_type="enroll_tuition_payment", amount=amt,
               posted_date=posted, billing_month="", proration="not_applicable",
               sibling_discount_applied=False, payment_method=payment_method, payment_reference=ref,
               credit_reason="not_applicable", source_enrollment_ledger_id="")
    return (f"Advance payment received: confirmation {ref}, entry {rid} on enrollment {enrollment_id}, "
            f"amount {amt:.2f} USD by {payment_method}, posted {posted}.")



@tool(owner="agent", rw="write")
def credit_prek_eligibility_month_43743e06(ctx: ToolContext, enrollment_ledger_id: str, amount: float) -> str:
    """Post the eligibility credit for the billing month in which a Pre-K child's state eligibility
    basis came on file, against that month's tuition charge on the child's Pre-K enrollment. The
    support agent books one credit entry, dated today, marked as an eligibility-established credit,
    that offsets the named tuition charge and lowers the amount the household owes on that
    enrollment by the credit. The family sees the credit next to that month's tuition charge on the
    statement. The call succeeds when the receipt confirms the new credit entry and the charge it
    offsets.

    Args:
        enrollment_ledger_id: Id class — the identifier of the tuition charge entry being offset, as
            returned by the tuition ledger lookup for the enrollment.
        amount: Fixed-format class — the credit to book, in US dollars as a positive number with
            2 decimal places; the tool rounds half up to the cent before booking.

    Returns:
        A one-line text receipt beginning "Eligibility credit posted:" that gives the new credit
        entry reference (text id), the tuition charge reference it offsets (text id), the enrollment
        reference (text id), the amount booked (USD, two decimals) and the posting date
        (YYYY-MM-DD). A receipt beginning "Error:" means nothing was booked because the charge
        reference was not found or the amount did not meet its format.
    """
    amt = _Fmt.money(amount)
    if amt <= 0:
        return "Error: amount must be a positive USD amount with two decimal places."
    src = ctx.find("enrollment_ledger", enrollment_ledger_id=enrollment_ledger_id)
    if not src:
        return f"Error: no tuition ledger entry {enrollment_ledger_id}."
    s = src[0]
    rid = ctx.make_id("eld_", enrollment_ledger_id, amt, "eligibility_established")
    posted = ctx.now()[:10]
    ctx.create("enrollment_ledger", rid, enrollment_ledger_id=rid, enrollment_id=s.get("enrollment_id", ""),
               customer_id=s.get("customer_id", ""), event_type="enroll_tuition_credit", amount=amt,
               posted_date=posted, billing_month="", proration="not_applicable",
               sibling_discount_applied=False, payment_method="not_applicable", payment_reference="",
               credit_reason="eligibility_established", source_enrollment_ledger_id=enrollment_ledger_id)
    return (f"Eligibility credit posted: entry {rid} offsets charge {enrollment_ledger_id} on enrollment "
            f"{s.get('enrollment_id', '')}, amount {amt:.2f} USD, posted {posted}.")


@tool(owner="agent", rw="write")
def credit_prek_late_fee_reversal_2a81de73(ctx: ToolContext, enrollment_ledger_id: str, amount: float) -> str:
    """Post the reversal of all or part of a Pre-K tuition late fee for a billing month whose tuition was
    credited because the child's state eligibility was established. The support agent books one
    credit entry, dated today, marked as an eligibility-established credit, against the named late
    fee entry; it lowers the amount the household owes on the enrollment by the reversal. The family
    sees the reversal next to that late fee on the statement. The call succeeds when the receipt
    confirms the new credit entry and the late fee it offsets.

    Args:
        enrollment_ledger_id: Id class — the identifier of the late fee entry being reversed, as
            returned by the tuition ledger lookup for the enrollment.
        amount: Fixed-format class — the reversal to book, in US dollars as a positive number with
            2 decimal places; the tool rounds half up to the cent before booking.

    Returns:
        A one-line text receipt beginning "Late fee reversal posted:" that gives the new credit entry
        reference (text id), the late fee reference it offsets (text id), the enrollment reference
        (text id), the amount booked (USD, two decimals) and the posting date (YYYY-MM-DD). A receipt
        beginning "Error:" means nothing was booked because the late fee reference was not found or
        the amount did not meet its format.
    """
    amt = _Fmt.money(amount)
    if amt <= 0:
        return "Error: amount must be a positive USD amount with two decimal places."
    src = ctx.find("enrollment_ledger", enrollment_ledger_id=enrollment_ledger_id)
    if not src:
        return f"Error: no tuition ledger entry {enrollment_ledger_id}."
    s = src[0]
    rid = ctx.make_id("eld_", enrollment_ledger_id, amt, "late_fee_reversal")
    posted = ctx.now()[:10]
    ctx.create("enrollment_ledger", rid, enrollment_ledger_id=rid, enrollment_id=s.get("enrollment_id", ""),
               customer_id=s.get("customer_id", ""), event_type="enroll_tuition_credit", amount=amt,
               posted_date=posted, billing_month="", proration="not_applicable",
               sibling_discount_applied=False, payment_method="not_applicable", payment_reference="",
               credit_reason="eligibility_established", source_enrollment_ledger_id=enrollment_ledger_id)
    return (f"Late fee reversal posted: entry {rid} offsets late fee {enrollment_ledger_id} on enrollment "
            f"{s.get('enrollment_id', '')}, amount {amt:.2f} USD, posted {posted}.")


@tool(owner="agent", rw="write")
def credit_prek_late_fee_waiver_decba573(ctx: ToolContext, enrollment_ledger_id: str, amount: float) -> str:
    """Post the eligibility-transition waiver on a Pre-K tuition late fee. The support agent books one
    credit entry, dated today, marked as a billing correction, against the named late fee entry; it
    lowers the amount the household owes on the enrollment by the waiver. The family sees the waiver
    next to that late fee on the statement. The call succeeds when the receipt confirms the new
    credit entry and the late fee it offsets.

    Args:
        enrollment_ledger_id: Id class — the identifier of the late fee entry being waived, as
            returned by the tuition ledger lookup for the enrollment.
        amount: Fixed-format class — the waiver to book, in US dollars as a positive number with
            2 decimal places; the tool rounds half up to the cent before booking.

    Returns:
        A one-line text receipt beginning "Late fee waiver posted:" that gives the new credit entry
        reference (text id), the late fee reference it offsets (text id), the enrollment reference
        (text id), the amount booked (USD, two decimals) and the posting date (YYYY-MM-DD). A receipt
        beginning "Error:" means nothing was booked because the late fee reference was not found or
        the amount did not meet its format.
    """
    amt = _Fmt.money(amount)
    if amt <= 0:
        return "Error: amount must be a positive USD amount with two decimal places."
    src = ctx.find("enrollment_ledger", enrollment_ledger_id=enrollment_ledger_id)
    if not src:
        return f"Error: no tuition ledger entry {enrollment_ledger_id}."
    s = src[0]
    rid = ctx.make_id("eld_", enrollment_ledger_id, amt, "transition_waiver")
    posted = ctx.now()[:10]
    ctx.create("enrollment_ledger", rid, enrollment_ledger_id=rid, enrollment_id=s.get("enrollment_id", ""),
               customer_id=s.get("customer_id", ""), event_type="enroll_tuition_credit", amount=amt,
               posted_date=posted, billing_month="", proration="not_applicable",
               sibling_discount_applied=False, payment_method="not_applicable", payment_reference="",
               credit_reason="billing_correction", source_enrollment_ledger_id=enrollment_ledger_id)
    return (f"Late fee waiver posted: entry {rid} offsets late fee {enrollment_ledger_id} on enrollment "
            f"{s.get('enrollment_id', '')}, amount {amt:.2f} USD, posted {posted}.")


@tool(owner="user", rw="write")
def pay_prek_plan_installment_1e1e8562(ctx: ToolContext, enrollment_id: str, amount: float, payment_method: str) -> str:
    """Pay the first installment of a Pre-K tuition payment plan on the child's Pre-K enrollment
    through the district's online payment portal. The parent or guardian completes this payment
    personally; it books one tuition payment entry on the enrollment, dated today, which lowers the
    amount the household owes by the installment, the rest of the balance staying open for the later
    installments. The parent receives a payment confirmation number. The call succeeds when the
    receipt shows that confirmation number.

    Args:
        enrollment_id: Id class — the reference number of the student's Pre-K enrollment record for
            the school year, as given by the support agent from the enrollment lookup.
        amount: Fixed-format class — the first installment quoted by the support agent, in US dollars
            as a positive number with 2 decimal places; the portal rounds half up to the cent.
        payment_method: Enum class — how the parent pays; exactly one of these values:
            online_card (the parent pays with a debit or credit card entered in the portal);
            ach_bank_draft (the parent pays from a checking or savings account by bank draft entered
            in the portal); personal_check (a paper check, taken only at the campus cashier, so the
            portal refuses it); money_order (taken only at the campus cashier, so the portal refuses
            it); not_applicable (no payment method, which the portal refuses).

    Returns:
        A one-line text receipt beginning "Plan installment received:" that gives the payment
        confirmation number (eight digits), the new ledger entry reference (text id), the enrollment
        reference (text id), the amount paid (USD, two decimals), the payment method and the posting
        date (YYYY-MM-DD). A receipt beginning "Error:" means no payment was taken because an
        argument did not meet its format.
    """
    if payment_method not in ("online_card", "ach_bank_draft"):
        return "Error: payment_method must be online_card or ach_bank_draft."
    amt = _Fmt.money(amount)
    if amt <= 0:
        return "Error: amount must be a positive USD amount with two decimal places."
    rows = ctx.find("enrollments", enrollment_id=enrollment_id)
    customer_id = rows[0].get("customer_id", "") if rows else ""
    rid = ctx.make_id("eld_", enrollment_id, amt, payment_method, "plan_installment")
    ref = _Fmt.confirmation(rid)
    posted = ctx.now()[:10]
    ctx.create("enrollment_ledger", rid, enrollment_ledger_id=rid, enrollment_id=enrollment_id,
               customer_id=customer_id, event_type="enroll_tuition_payment", amount=amt,
               posted_date=posted, billing_month="", proration="not_applicable",
               sibling_discount_applied=False, payment_method=payment_method, payment_reference=ref,
               credit_reason="not_applicable", source_enrollment_ledger_id="")
    return (f"Plan installment received: confirmation {ref}, entry {rid} on enrollment {enrollment_id}, "
            f"amount {amt:.2f} USD by {payment_method}, posted {posted}.")

"""Hidden task tools for the select_claims_and_cost_shares difficulty of
env_0055_military_health_plan_administrator (Westbridge Military Health Services, TRICARE West Region).

Each tool performs one atomic write on a TRICARE Select enrollment's claim lines or fee account. The
values passed in are worked out by the caller from the published policies and the records; no tool
judges eligibility, ordering or amounts.
"""

from erlbench import ToolContext, tool


class _Lookup:
    """Record copies shared by the tools below (not tools themselves)."""

    @staticmethod
    def reversed_source(ctx: ToolContext, reversed_claim_line_id: str) -> dict:
        """The adjudicated claim line the reversal named, or {} when it cannot be found."""
        rows = ctx.find("select_claim_lines", select_claim_line_id=reversed_claim_line_id)
        return dict(rows[0]) if rows else {}


@tool(owner="agent", rw="write")
def post_select_professional_line_96ff63a5(ctx: ToolContext, reversed_claim_line_id: str, line_number: int,
                                           prior_authorization_id: str, deductible_applied: float,
                                           cost_share_amount: float, tricare_paid_amount: float) -> str:
    """Post the corrected adjudication of a TRICARE Select professional or other outpatient claim line
    whose earlier adjudication stands reversed. The agent posts it for the verified beneficiary: one new
    paid line is added to the same claim, repeating the reversed line's claim number, patient, service
    date, rendering provider, network relationship, service class, receipt date, billed, allowed and
    other-insurance amounts, and carrying the deductible, the beneficiary liability and the TRICARE
    payment given here. The beneficiary's outpatient liability for the plan year grows by the liability
    posted, and the corrected line then shows on the Explanation of Benefits as paid.

    Args:
        reversed_claim_line_id: Id class — the reference number of the adjudicated claim line that the
            reversal withdrew, read from the reversal entry's reversed-line field in the claim-line
            lookup for the enrollment.
        line_number: Fixed-format class — the line number the corrected adjudication takes on the same
            claim, an integer, integer >= 1, written with no decimal point.
        prior_authorization_id: Id class — the reference number of the approved authorization that
            covers this line's provider and service date, read from the referral and authorization
            lookup, given only when the line's service class needs prior authorization; pass "" otherwise.
        deductible_applied: Fixed-format class — the part of the line applied to the patient's
            deductible, in USD (US dollars) as a plain number with 2 decimal places (cents, rounded half up
            to the cent), 0.00 when none.
        cost_share_amount: Fixed-format class — the total beneficiary liability on the corrected line
            (the deductible applied plus the cost share), in USD (US dollars) as a plain number with 2
            decimal places (cents, rounded half up to the cent).
        tricare_paid_amount: Fixed-format class — the amount TRICARE pays on the corrected line, in USD
            dollars as a plain number with 2 decimal places (cents, rounded half up to the cent).

    Returns:
        A confirmation sentence (str) naming: the new claim-line reference number (text starting
        "scl_"), the claim number and line number posted, the line outcome "paid", and the deductible,
        beneficiary liability and TRICARE payment posted, each in US dollars with 2 decimals. The
        sentence beginning "Corrected professional line posted" indicates the line was added.
    """
    src = _Lookup.reversed_source(ctx, reversed_claim_line_id)
    rid = ctx.make_id("scl_", reversed_claim_line_id, line_number, prior_authorization_id, deductible_applied,
                      cost_share_amount, tricare_paid_amount)
    ctx.create("select_claim_lines", rid, select_claim_line_id=rid,
               select_enrollment_id=src.get("select_enrollment_id", ""), customer_id=src.get("customer_id", ""),
               event_type="select_claim_line_post", claim_number=src.get("claim_number", ""),
               line_number=int(line_number), service_date=src.get("service_date", ""),
               claim_received_date=src.get("claim_received_date", ""), provider_id=src.get("provider_id", ""),
               provider_network_status=src.get("provider_network_status", ""),
               service_class=src.get("service_class", ""), inpatient_days=0,
               prior_authorization_id=prior_authorization_id, billed_amount=src.get("billed_amount", 0.0),
               allowed_amount=src.get("allowed_amount", 0.0), ohi_paid_amount=src.get("ohi_paid_amount", 0.0),
               deductible_applied=round(float(deductible_applied), 2),
               cost_share_amount=round(float(cost_share_amount), 2),
               tricare_paid_amount=round(float(tricare_paid_amount), 2), line_outcome="paid",
               posted_date=ctx.now()[:10], reversed_claim_line_id="", reversal_reason="not_applicable")
    return (f"Corrected professional line posted: {rid} on claim {src.get('claim_number', '')} line {int(line_number)}, "
            f"outcome paid, deductible {round(float(deductible_applied), 2):.2f}, beneficiary liability "
            f"{round(float(cost_share_amount), 2):.2f}, TRICARE payment {round(float(tricare_paid_amount), 2):.2f}.")


@tool(owner="agent", rw="write")
def post_select_inpatient_stay_a4ca4c06(ctx: ToolContext, reversed_claim_line_id: str, line_number: int,
                                        inpatient_days: int, prior_authorization_id: str,
                                        cost_share_amount: float, tricare_paid_amount: float) -> str:
    """Post the corrected adjudication of a TRICARE Select inpatient facility claim line (a hospital or
    psychiatric hospital stay) whose earlier adjudication stands reversed. The agent posts it for the
    verified beneficiary: one new paid line is added to the same claim, repeating the reversed line's
    claim number, patient, admission date, facility, network relationship, service class, receipt date,
    billed, allowed and other-insurance amounts, and carrying the covered inpatient days, the
    beneficiary liability and the TRICARE payment given here, with no deductible on the stay. The family
    catastrophic total for the plan year grows by the liability posted, and the corrected stay then
    shows on the Explanation of Benefits as paid.

    Args:
        reversed_claim_line_id: Id class — the reference number of the adjudicated stay line that the
            reversal withdrew, read from the reversal entry's reversed-line field in the claim-line
            lookup for the enrollment.
        line_number: Fixed-format class — the line number the corrected adjudication takes on the same
            claim, an integer, integer >= 1, written with no decimal point.
        inpatient_days: Fixed-format class — the number of covered inpatient days on the corrected
            stay, an integer, integer >= 0, written with no decimal point.
        prior_authorization_id: Id class — the reference number of the approved inpatient authorization
            on file for the patient at this facility, read from the referral and authorization lookup;
            pass "" when none is on file.
        cost_share_amount: Fixed-format class — the beneficiary liability on the corrected stay, in USD
            dollars as a plain number with 2 decimal places (cents, rounded half up to the cent).
        tricare_paid_amount: Fixed-format class — the amount TRICARE pays on the corrected stay, in USD
            dollars as a plain number with 2 decimal places (cents, rounded half up to the cent).

    Returns:
        A confirmation sentence (str) naming: the new claim-line reference number (text starting
        "scl_"), the claim number and line number posted, the covered inpatient days (whole number),
        the line outcome "paid", and the beneficiary liability and TRICARE payment posted in USD
        dollars with 2 decimals. The sentence beginning "Corrected inpatient stay posted" indicates
        the line was added.
    """
    src = _Lookup.reversed_source(ctx, reversed_claim_line_id)
    rid = ctx.make_id("scl_", reversed_claim_line_id, line_number, inpatient_days, prior_authorization_id,
                      cost_share_amount, tricare_paid_amount)
    ctx.create("select_claim_lines", rid, select_claim_line_id=rid,
               select_enrollment_id=src.get("select_enrollment_id", ""), customer_id=src.get("customer_id", ""),
               event_type="select_claim_line_post", claim_number=src.get("claim_number", ""),
               line_number=int(line_number), service_date=src.get("service_date", ""),
               claim_received_date=src.get("claim_received_date", ""), provider_id=src.get("provider_id", ""),
               provider_network_status=src.get("provider_network_status", ""),
               service_class=src.get("service_class", ""), inpatient_days=int(inpatient_days),
               prior_authorization_id=prior_authorization_id, billed_amount=src.get("billed_amount", 0.0),
               allowed_amount=src.get("allowed_amount", 0.0), ohi_paid_amount=src.get("ohi_paid_amount", 0.0),
               deductible_applied=0.0, cost_share_amount=round(float(cost_share_amount), 2),
               tricare_paid_amount=round(float(tricare_paid_amount), 2), line_outcome="paid",
               posted_date=ctx.now()[:10], reversed_claim_line_id="", reversal_reason="not_applicable")
    return (f"Corrected inpatient stay posted: {rid} on claim {src.get('claim_number', '')} line {int(line_number)}, "
            f"{int(inpatient_days)} covered days, outcome paid, beneficiary liability "
            f"{round(float(cost_share_amount), 2):.2f}, TRICARE payment {round(float(tricare_paid_amount), 2):.2f}.")


@tool(owner="user", rw="write")
def pay_select_installment_by_card_fa3a0d38(ctx: ToolContext, related_fee_entry_id: str, amount: float) -> str:
    """The beneficiary makes a one-time card payment toward one quarterly or annual TRICARE Select
    enrollment-fee installment. The payment is received on the beneficiary's fee account as a single
    card payment and is tied to the installment charge named here, and the enrollment's recorded fee
    balance (fee_balance_due) falls by the amount paid, never below 0.00. The beneficiary sees the
    payment confirmation with its reference number.

    Args:
        related_fee_entry_id: Id class — the reference number of the quarterly or annual installment
            charge being paid, read by the agent from the fee-account lookup for the enrollment and
            given to the beneficiary.
        amount: Fixed-format class — the amount paid, in USD (US dollars) as a plain number with 2 decimal
            places (cents, rounded half up to the cent), greater than 0.00.

    Returns:
        A confirmation sentence (str) naming: the payment reference number (text starting "sfp_"), the
        amount paid in US dollars with 2 decimals, the payment method "card_single", the installment
        charge reference it settles, and the coverage period start and end of that installment
        (YYYY-MM-DD). The sentence beginning "Card payment received" indicates the payment was taken.
    """
    rows = ctx.find("select_fee_ledger", select_fee_entry_id=related_fee_entry_id)
    charge = dict(rows[0]) if rows else {}
    rid = ctx.make_id("sfp_", related_fee_entry_id, amount)
    ctx.create("select_fee_ledger", rid, select_fee_entry_id=rid,
               select_enrollment_id=charge.get("select_enrollment_id", ""), customer_id=charge.get("customer_id", ""),
               event_type="select_fee_payment", coverage_period_start="", coverage_period_end="",
               installment_frequency="not_applicable",
               amount=round(float(amount), 2), posted_date=ctx.now()[:10], payment_method="card_single",
               adjustment_reason="not_applicable", related_fee_entry_id=related_fee_entry_id)
    enr_id = charge.get("select_enrollment_id", "")
    enr = ctx.find("select_enrollments", select_enrollment_id=enr_id)
    if enr:
        left = round(float(enr[0].get("fee_balance_due") or 0.0) - round(float(amount), 2), 2)
        ctx.update("select_enrollments", enr_id, fee_balance_due=left if left > 0 else 0.0)
    return (f"Card payment received: {rid} for {round(float(amount), 2):.2f} USD by card_single against installment "
            f"{related_fee_entry_id} covering {charge.get('coverage_period_start', '')} to "
            f"{charge.get('coverage_period_end', '')}.")


@tool(owner="agent", rw="write")
def post_select_ohi_reprocessed_line_2895a639(ctx: ToolContext, reversed_claim_line_id: str, line_number: int,
                                              deductible_applied: float, cost_share_amount: float,
                                              tricare_paid_amount: float) -> str:
    """Post the reprocessed adjudication of a TRICARE Select outpatient claim line that was reversed because
    the beneficiary's other health insurance was found retroactively. The agent posts it for the verified
    beneficiary: one new paid line is added to the same claim, repeating the reversed line's claim number,
    patient, service date, rendering provider, network relationship, service class, receipt date, billed,
    allowed and other-insurance amounts, and carrying the deductible, the beneficiary liability and the
    TRICARE payment given here, now figured with TRICARE paying after the other insurer. The reprocessed
    line then shows on the Explanation of Benefits as paid.

    Args:
        reversed_claim_line_id: Id class — the reference number of the adjudicated outpatient line that
            the other-insurance reversal withdrew, read from the reversal entry's reversed-line field in the
            claim-line lookup for the enrollment.
        line_number: Fixed-format class — the line number the reprocessed adjudication takes on the same
            claim, an integer, integer >= 1, written with no decimal point.
        deductible_applied: Fixed-format class — the part of the line applied to the patient's deductible,
            in USD (US dollars) as a plain number with 2 decimal places (cents, rounded half up to the
            cent), 0.00 when none.
        cost_share_amount: Fixed-format class — the total beneficiary liability on the reprocessed line
            (deductible applied plus cost share), in USD (US dollars) as a plain number with 2 decimal
            places (cents, rounded half up to the cent).
        tricare_paid_amount: Fixed-format class — the amount TRICARE pays on the reprocessed line, in USD
            (US dollars) as a plain number with 2 decimal places (cents, rounded half up to the cent).

    Returns:
        A confirmation sentence (str) naming: the new claim-line reference number (text starting "scl_"),
        the claim number and line number posted, the line outcome "paid", and the deductible, beneficiary
        liability and TRICARE payment posted, each in USD with 2 decimals. The sentence beginning
        "Other-insurance reprocessed line posted" indicates the line was added.
    """
    src = _Lookup.reversed_source(ctx, reversed_claim_line_id)
    rid = ctx.make_id("scl_", "ohi_line", reversed_claim_line_id, line_number, deductible_applied,
                      cost_share_amount, tricare_paid_amount)
    ctx.create("select_claim_lines", rid, select_claim_line_id=rid,
               select_enrollment_id=src.get("select_enrollment_id", ""), customer_id=src.get("customer_id", ""),
               event_type="select_claim_line_post", claim_number=src.get("claim_number", ""),
               line_number=int(line_number), service_date=src.get("service_date", ""),
               claim_received_date=src.get("claim_received_date", ""), provider_id=src.get("provider_id", ""),
               provider_network_status=src.get("provider_network_status", ""),
               service_class=src.get("service_class", ""), inpatient_days=0,
               prior_authorization_id=src.get("prior_authorization_id", ""), billed_amount=src.get("billed_amount", 0.0),
               allowed_amount=src.get("allowed_amount", 0.0), ohi_paid_amount=src.get("ohi_paid_amount", 0.0),
               deductible_applied=round(float(deductible_applied), 2),
               cost_share_amount=round(float(cost_share_amount), 2),
               tricare_paid_amount=round(float(tricare_paid_amount), 2), line_outcome="paid",
               posted_date=ctx.now()[:10], reversed_claim_line_id="", reversal_reason="not_applicable")
    return (f"Other-insurance reprocessed line posted: {rid} on claim {src.get('claim_number', '')} line {int(line_number)}, "
            f"outcome paid, deductible {round(float(deductible_applied), 2):.2f}, beneficiary liability "
            f"{round(float(cost_share_amount), 2):.2f}, TRICARE payment {round(float(tricare_paid_amount), 2):.2f}.")


@tool(owner="agent", rw="write")
def post_select_ohi_reprocessed_stay_ac99ca71(ctx: ToolContext, reversed_claim_line_id: str, line_number: int,
                                              cost_share_amount: float, tricare_paid_amount: float) -> str:
    """Post the reprocessed adjudication of a TRICARE Select inpatient facility stay that was reversed
    because the beneficiary's other health insurance was found retroactively. The agent posts it for the
    verified beneficiary: one new paid line is added to the same claim, repeating the reversed line's claim
    number, patient, admission date, facility, network relationship, service class, inpatient days,
    receipt date, billed, allowed and other-insurance amounts, and carrying the beneficiary liability and
    the TRICARE payment given here, with no deductible on the stay. The family catastrophic total for the
    plan year grows by the liability posted, and the reprocessed stay then shows on the Explanation of
    Benefits as paid.

    Args:
        reversed_claim_line_id: Id class — the reference number of the adjudicated stay line that the
            other-insurance reversal withdrew, read from the reversal entry's reversed-line field in the
            claim-line lookup for the enrollment.
        line_number: Fixed-format class — the line number the reprocessed adjudication takes on the same
            claim, an integer, integer >= 1, written with no decimal point.
        cost_share_amount: Fixed-format class — the beneficiary liability on the reprocessed stay, in USD
            (US dollars) as a plain number with 2 decimal places (cents, rounded half up to the cent).
        tricare_paid_amount: Fixed-format class — the amount TRICARE pays on the reprocessed stay, in USD
            (US dollars) as a plain number with 2 decimal places (cents, rounded half up to the cent).

    Returns:
        A confirmation sentence (str) naming: the new claim-line reference number (text starting "scl_"),
        the claim number and line number posted, the line outcome "paid", and the beneficiary liability and
        TRICARE payment posted in USD with 2 decimals. The sentence beginning "Other-insurance reprocessed
        stay posted" indicates the line was added.
    """
    src = _Lookup.reversed_source(ctx, reversed_claim_line_id)
    rid = ctx.make_id("scl_", "ohi_stay", reversed_claim_line_id, line_number, cost_share_amount, tricare_paid_amount)
    ctx.create("select_claim_lines", rid, select_claim_line_id=rid,
               select_enrollment_id=src.get("select_enrollment_id", ""), customer_id=src.get("customer_id", ""),
               event_type="select_claim_line_post", claim_number=src.get("claim_number", ""),
               line_number=int(line_number), service_date=src.get("service_date", ""),
               claim_received_date=src.get("claim_received_date", ""), provider_id=src.get("provider_id", ""),
               provider_network_status=src.get("provider_network_status", ""),
               service_class=src.get("service_class", ""), inpatient_days=int(src.get("inpatient_days", 0) or 0),
               prior_authorization_id=src.get("prior_authorization_id", ""), billed_amount=src.get("billed_amount", 0.0),
               allowed_amount=src.get("allowed_amount", 0.0), ohi_paid_amount=src.get("ohi_paid_amount", 0.0),
               deductible_applied=0.0, cost_share_amount=round(float(cost_share_amount), 2),
               tricare_paid_amount=round(float(tricare_paid_amount), 2), line_outcome="paid",
               posted_date=ctx.now()[:10], reversed_claim_line_id="", reversal_reason="not_applicable")
    return (f"Other-insurance reprocessed stay posted: {rid} on claim {src.get('claim_number', '')} line {int(line_number)}, "
            f"outcome paid, beneficiary liability {round(float(cost_share_amount), 2):.2f}, TRICARE payment "
            f"{round(float(tricare_paid_amount), 2):.2f}.")


@tool(owner="agent", rw="write")
def post_select_cap_reprocessed_line_5ecdf694(ctx: ToolContext, reversed_claim_line_id: str, line_number: int,
                                              cost_share_amount: float, tricare_paid_amount: float) -> str:
    """Post the reprocessed adjudication of a TRICARE Select outpatient claim line that was reversed for
    catastrophic-cap reprocessing. The agent posts it for the verified beneficiary: one new paid line is
    added to the same claim, repeating the reversed line's claim number, patient, service date, rendering
    provider, network relationship, service class, receipt date, billed, allowed and other-insurance
    amounts, and carrying the beneficiary liability and the TRICARE payment given here, with no deductible.
    The reprocessed line then shows on the Explanation of Benefits as paid.

    Args:
        reversed_claim_line_id: Id class — the reference number of the adjudicated line that the
            catastrophic-cap reversal withdrew, read from the reversal entry's reversed-line field in the
            claim-line lookup for the enrollment.
        line_number: Fixed-format class — the line number the reprocessed adjudication takes on the same
            claim, an integer, integer >= 1, written with no decimal point.
        cost_share_amount: Fixed-format class — the beneficiary liability on the reprocessed line, in USD
            (US dollars) as a plain number with 2 decimal places (cents, rounded half up to the cent),
            0.00 when none.
        tricare_paid_amount: Fixed-format class — the amount TRICARE pays on the reprocessed line, in USD
            (US dollars) as a plain number with 2 decimal places (cents, rounded half up to the cent).

    Returns:
        A confirmation sentence (str) naming: the new claim-line reference number (text starting "scl_"),
        the claim number and line number posted, the line outcome "paid", and the beneficiary liability and
        TRICARE payment posted in USD with 2 decimals. The sentence beginning "Cap-reprocessed line posted"
        indicates the line was added.
    """
    src = _Lookup.reversed_source(ctx, reversed_claim_line_id)
    rid = ctx.make_id("scl_", "cap_line", reversed_claim_line_id, line_number, cost_share_amount, tricare_paid_amount)
    ctx.create("select_claim_lines", rid, select_claim_line_id=rid,
               select_enrollment_id=src.get("select_enrollment_id", ""), customer_id=src.get("customer_id", ""),
               event_type="select_claim_line_post", claim_number=src.get("claim_number", ""),
               line_number=int(line_number), service_date=src.get("service_date", ""),
               claim_received_date=src.get("claim_received_date", ""), provider_id=src.get("provider_id", ""),
               provider_network_status=src.get("provider_network_status", ""),
               service_class=src.get("service_class", ""), inpatient_days=0,
               prior_authorization_id=src.get("prior_authorization_id", ""), billed_amount=src.get("billed_amount", 0.0),
               allowed_amount=src.get("allowed_amount", 0.0), ohi_paid_amount=src.get("ohi_paid_amount", 0.0),
               deductible_applied=0.0, cost_share_amount=round(float(cost_share_amount), 2),
               tricare_paid_amount=round(float(tricare_paid_amount), 2), line_outcome="paid",
               posted_date=ctx.now()[:10], reversed_claim_line_id="", reversal_reason="not_applicable")
    return (f"Cap-reprocessed line posted: {rid} on claim {src.get('claim_number', '')} line {int(line_number)}, "
            f"outcome paid, beneficiary liability {round(float(cost_share_amount), 2):.2f}, TRICARE payment "
            f"{round(float(tricare_paid_amount), 2):.2f}.")


@tool(owner="user", rw="write")
def authorize_select_bank_draft_0bb89bb0(ctx: ToolContext, related_fee_entry_id: str, amount: float) -> str:
    """The beneficiary authorizes a one-time bank draft from their own checking or savings account toward a
    TRICARE Select enrollment-fee installment. The draft is received on the beneficiary's fee account as an
    electronic funds transfer tied to the installment charge named here, and the enrollment's recorded fee
    balance (fee_balance_due) falls by the amount drafted, never below 0.00. The
    beneficiary sees the draft confirmation with its reference number.

    Args:
        related_fee_entry_id: Id class — the reference number of the installment charge the draft is
            recorded against, read by the agent from the fee-account lookup for the enrollment and given to
            the beneficiary.
        amount: Fixed-format class — the amount drafted, in USD (US dollars) as a plain number with 2
            decimal places (cents, rounded half up to the cent), greater than 0.00.

    Returns:
        A confirmation sentence (str) naming: the draft reference number (text starting "sfd_"), the amount
        drafted in USD with 2 decimals, the payment method "electronic_funds_transfer", the installment
        charge reference it is recorded against, and the coverage period start and end of that installment
        (YYYY-MM-DD). The sentence beginning "Bank draft received" indicates the draft was taken.
    """
    rows = ctx.find("select_fee_ledger", select_fee_entry_id=related_fee_entry_id)
    charge = dict(rows[0]) if rows else {}
    rid = ctx.make_id("sfd_", related_fee_entry_id, amount)
    ctx.create("select_fee_ledger", rid, select_fee_entry_id=rid,
               select_enrollment_id=charge.get("select_enrollment_id", ""), customer_id=charge.get("customer_id", ""),
               event_type="select_fee_payment", coverage_period_start="", coverage_period_end="",
               installment_frequency="not_applicable",
               amount=round(float(amount), 2), posted_date=ctx.now()[:10], payment_method="electronic_funds_transfer",
               adjustment_reason="not_applicable", related_fee_entry_id=related_fee_entry_id)
    enr_id = charge.get("select_enrollment_id", "")
    enr = ctx.find("select_enrollments", select_enrollment_id=enr_id)
    if enr:
        left = round(float(enr[0].get("fee_balance_due") or 0.0) - round(float(amount), 2), 2)
        ctx.update("select_enrollments", enr_id, fee_balance_due=left if left > 0 else 0.0)
    return (f"Bank draft received: {rid} for {round(float(amount), 2):.2f} USD by electronic_funds_transfer against "
            f"installment {related_fee_entry_id} covering {charge.get('coverage_period_start', '')} to "
            f"{charge.get('coverage_period_end', '')}.")

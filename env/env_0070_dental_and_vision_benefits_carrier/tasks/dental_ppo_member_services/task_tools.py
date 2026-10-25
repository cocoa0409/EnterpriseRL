"""Hidden task tools for the dental_ppo_member_services difficulty of env_0070 (Cascade Mutual Dental & Vision).

Each tool performs one atomic business write on Dental PPO records with the values the caller passes;
no tool judges eligibility, prerequisites or amounts.
"""

from erlbench import ToolContext, tool


class _LineBook:
    """Value helpers shared by the reprocessing tools (they compute values only and never write)."""

    TRACKS = ("annual_maximum", "pediatric_in_network", "pediatric_out_of_network")

    @staticmethod
    def carried(o):
        keys = ("dental_plan_id", "customer_id", "claim_number", "line_number", "provider_agreement_id", "network_status",
                "cdt_code", "procedure_category", "service_class", "tooth_or_area", "date_of_service", "procedure_start_date",
                "extraction_date", "received_date", "benefit_year", "submitted_amount", "allowed_amount",
                "alternate_allowed_amount", "cob_other_paid")
        return {k: o.get(k) for k in keys}

    @staticmethod
    def postings(track, paid, ded, resp, rollover=0.0):
        """List of (event_type, amount) the corrected decision posts for the stated accumulator track."""
        out = []
        if track == "annual_maximum" and round(paid - rollover, 2) > 0:
            out.append(("dental_max_posting", round(paid - rollover, 2)))
        if track == "annual_maximum" and rollover > 0:
            out.append(("dental_rollover_draw", rollover))
        if ded > 0:
            out.append(("dental_deductible_posting", ded))
        if track == "pediatric_in_network" and resp > 0:
            out.append(("dental_ped_oop_posting", resp))
        return out

    @staticmethod
    def reversal_of(event_type):
        return {"dental_max_posting": "dental_max_reversal", "dental_deductible_posting": "dental_deductible_reversal",
                "dental_ped_oop_posting": "dental_ped_oop_reversal"}.get(event_type)




@tool(owner="agent", rw="write")
def reprocess_wait_denial_e5c18a2f(ctx: ToolContext, denied_claim_line_id: str, deductible_applied: float, coinsurance_pct: int,
                                   plan_paid: float, rollover_amount: float, member_responsibility: float,
                                   accumulator_track: str) -> str:
    """Reprocess one Dental PPO claim line that stands denied for a waiting period counted from the enrollment's
    coverage effective date: books a corrected decision that replaces the denial, carrying over the denied line's
    claim number, line number, practice, network status, procedure, tooth, extraction date, dates of service and
    receipt, benefit year, billed, allowed and alternate allowances and other-carrier payment, and recording the
    corrected deductible, coinsurance, total plan payment and patient share with remark ADJUSTED_REPROCESSED and
    today's decision date. In the same write any deductible taken is posted to the person's deductible, the payment
    or patient share is posted to the accumulator named by the accumulator track, and on the annual-maximum track any
    part of the payment funded from rollover dollars is drawn from the rollover balance instead of being posted to the
    annual maximum. Afterwards the member's
    Explanation of Benefits shows the corrected decision and the accumulators reflect it.

    Args:
        denied_claim_line_id: Id class — reference number of the denied claim-line decision being replaced, as returned by the dental claim-line lookup for the member's enrollment.
        deductible_applied: Fixed-format class — deductible taken on the corrected decision, in USD with 2 decimal places, rounded half up to the cent; 0.00 when no deductible is taken.
        coinsurance_pct: Fixed-format class — coinsurance percentage the corrected decision pays at, integer percent 0-100 (a whole number).
        plan_paid: Fixed-format class — corrected total plan payment for the line, in USD with 2 decimal places, rounded half up to the cent; 0.00 when nothing is paid.
        rollover_amount: Fixed-format class — part of the corrected plan payment funded from the person's rollover balance, in USD with 2 decimal places, rounded half up to the cent; 0.00 when no rollover dollars are used.
        member_responsibility: Fixed-format class — corrected patient share for the line, in USD with 2 decimal places, rounded half up to the cent.
        accumulator_track: Enum class — accumulator the corrected decision posts to, besides any deductible taken: annual_maximum when the plan payment counts against the person's annual maximum; pediatric_in_network when the person receives the pediatric essential-health-benefit treatment and the line is from an in-network practice, so nothing is posted to the annual maximum and the patient share is posted to the pediatric out-of-pocket accumulator; pediatric_out_of_network when the person receives that treatment and the line is from an out-of-network practice, so nothing is posted to either.

    Returns:
        A dictionary rendered as text with keys: status ("reprocessed" on success), dental_claim_line_id (reference
        number of the new corrected decision), original_claim_line_id (the denial replaced), plan_paid (USD 2
        decimals), rollover_amount (USD 2 decimals), member_responsibility (USD 2 decimals), accumulator_track (as
        booked), adjudicated_date
        (YYYY-MM-DD decision date of the correction).
    """
    rows = ctx.find("dental_claim_lines", dental_claim_line_id=denied_claim_line_id)
    o = rows[0] if rows else {}
    today = ctx.now()[:10]
    paid = round(float(plan_paid), 2)
    ded = round(float(deductible_applied), 2)
    resp = round(float(member_responsibility), 2)
    roll = round(float(rollover_amount), 2)
    rid = ctx.make_id("dcl_", denied_claim_line_id, deductible_applied, coinsurance_pct, plan_paid, rollover_amount,
                      member_responsibility, accumulator_track)
    ctx.create("dental_claim_lines", rid, dental_claim_line_id=rid, event_type="dental_claim_line_adjusted",
               adjudicated_date=today, deductible_applied=ded, coinsurance_pct=int(coinsurance_pct), plan_paid=paid,
               member_responsibility=resp, remark_code="ADJUSTED_REPROCESSED", original_claim_line_id=denied_claim_line_id,
               dental_appeal_id=None, dental_estimate_id=None, **_LineBook.carried(o))
    for kind, amount in _LineBook.postings(accumulator_track, paid, ded, resp, roll):
        pid = ctx.make_id("dap_", rid, kind)
        ctx.create("dental_accumulator_postings", pid, dental_accum_posting_id=pid, dental_plan_id=o.get("dental_plan_id"),
                   customer_id=o.get("customer_id"), event_type=kind, dental_claim_line_id=rid,
                   benefit_year=o.get("benefit_year"), amount=amount, posted_date=today)
    return str({"status": "reprocessed", "dental_claim_line_id": rid, "original_claim_line_id": denied_claim_line_id,
                "plan_paid": paid, "rollover_amount": roll, "member_responsibility": resp, "accumulator_track": accumulator_track,
                "adjudicated_date": today})


@tool(owner="agent", rw="write")
def reprocess_upgrade_denial_9a74d03b(ctx: ToolContext, denied_claim_line_id: str, deductible_applied: float, coinsurance_pct: int,
                                      plan_paid: float, member_responsibility: float, accumulator_track: str) -> str:
    """Reprocess one Dental PPO claim line that stands denied for the new waiting period that followed a change of
    the enrollment to a richer plan: books a corrected decision that replaces the denial, carrying over the denied
    line's claim number, line number, practice, network status, procedure, tooth, extraction date, dates of service
    and receipt, benefit year, billed, allowed and alternate allowances and other-carrier payment, and recording the
    corrected deductible, coinsurance, total plan payment and patient share with remark ADJUSTED_REPROCESSED and
    today's decision date. In the same write any deductible taken is posted to the person's deductible and the
    payment or patient share is posted to the accumulator named by the accumulator track. Afterwards the member's
    Explanation of Benefits shows the corrected decision and the accumulators reflect it.

    Args:
        denied_claim_line_id: Id class — reference number of the denied claim-line decision being replaced, as returned by the dental claim-line lookup for the member's enrollment.
        deductible_applied: Fixed-format class — deductible taken on the corrected decision, in USD with 2 decimal places, rounded half up to the cent; 0.00 when no deductible is taken.
        coinsurance_pct: Fixed-format class — coinsurance percentage the corrected decision pays at, integer percent 0-100 (a whole number).
        plan_paid: Fixed-format class — corrected total plan payment for the line, in USD with 2 decimal places, rounded half up to the cent; 0.00 when nothing is paid.
        member_responsibility: Fixed-format class — corrected patient share for the line, in USD with 2 decimal places, rounded half up to the cent.
        accumulator_track: Enum class — accumulator the corrected decision posts to, besides any deductible taken: annual_maximum when the plan payment counts against the person's annual maximum; pediatric_in_network when the person receives the pediatric essential-health-benefit treatment and the line is from an in-network practice, so nothing is posted to the annual maximum and the patient share is posted to the pediatric out-of-pocket accumulator; pediatric_out_of_network when the person receives that treatment and the line is from an out-of-network practice, so nothing is posted to either.

    Returns:
        A dictionary rendered as text with keys: status ("reprocessed" on success), dental_claim_line_id (reference
        number of the new corrected decision), original_claim_line_id (the denial replaced), plan_paid (USD 2
        decimals), member_responsibility (USD 2 decimals), accumulator_track (as booked), adjudicated_date
        (YYYY-MM-DD decision date of the correction).
    """
    rows = ctx.find("dental_claim_lines", dental_claim_line_id=denied_claim_line_id)
    o = rows[0] if rows else {}
    today = ctx.now()[:10]
    paid = round(float(plan_paid), 2)
    ded = round(float(deductible_applied), 2)
    resp = round(float(member_responsibility), 2)
    rid = ctx.make_id("dcl_", denied_claim_line_id, deductible_applied, coinsurance_pct, plan_paid, member_responsibility,
                      accumulator_track, "upgrade")
    ctx.create("dental_claim_lines", rid, dental_claim_line_id=rid, event_type="dental_claim_line_adjusted",
               adjudicated_date=today, deductible_applied=ded, coinsurance_pct=int(coinsurance_pct), plan_paid=paid,
               member_responsibility=resp, remark_code="ADJUSTED_REPROCESSED", original_claim_line_id=denied_claim_line_id,
               dental_appeal_id=None, dental_estimate_id=None, **_LineBook.carried(o))
    for kind, amount in _LineBook.postings(accumulator_track, paid, ded, resp):
        pid = ctx.make_id("dap_", rid, kind)
        ctx.create("dental_accumulator_postings", pid, dental_accum_posting_id=pid, dental_plan_id=o.get("dental_plan_id"),
                   customer_id=o.get("customer_id"), event_type=kind, dental_claim_line_id=rid,
                   benefit_year=o.get("benefit_year"), amount=amount, posted_date=today)
    return str({"status": "reprocessed", "dental_claim_line_id": rid, "original_claim_line_id": denied_claim_line_id,
                "plan_paid": paid, "member_responsibility": resp, "accumulator_track": accumulator_track,
                "adjudicated_date": today})


@tool(owner="agent", rw="write")
def reprocess_grace_denial_4c0e9d17(ctx: ToolContext, denied_claim_line_id: str, deductible_applied: float, coinsurance_pct: int,
                                    plan_paid: float, member_responsibility: float, accumulator_track: str) -> str:
    """Reprocess one Dental PPO claim line that stands denied as not eligible for a date of service on which the
    enrollment was in force while its funding billing account was in a premium grace period: books a corrected
    decision that replaces the denial, carrying over the denied line's claim number, line number, practice, network
    status, procedure, tooth, extraction date, dates of service and receipt, benefit year, billed, allowed and
    alternate allowances and other-carrier payment, and recording the corrected deductible, coinsurance, total plan
    payment and patient share with remark ADJUSTED_REPROCESSED and today's decision date. In the same write any
    deductible taken is posted to the person's deductible and the payment or patient share is posted to the
    accumulator named by the accumulator track. Afterwards the member's Explanation of Benefits shows the corrected
    decision and the accumulators reflect it.

    Args:
        denied_claim_line_id: Id class — reference number of the denied claim-line decision being replaced, as returned by the dental claim-line lookup for the member's enrollment.
        deductible_applied: Fixed-format class — deductible taken on the corrected decision, in USD with 2 decimal places, rounded half up to the cent; 0.00 when no deductible is taken.
        coinsurance_pct: Fixed-format class — coinsurance percentage the corrected decision pays at, integer percent 0-100 (a whole number).
        plan_paid: Fixed-format class — corrected total plan payment for the line, in USD with 2 decimal places, rounded half up to the cent; 0.00 when nothing is paid.
        member_responsibility: Fixed-format class — corrected patient share for the line, in USD with 2 decimal places, rounded half up to the cent; 0.00 when the member owes nothing.
        accumulator_track: Enum class — accumulator the corrected decision posts to, besides any deductible taken: annual_maximum when the plan payment counts against the person's annual maximum; pediatric_in_network when the person receives the pediatric essential-health-benefit treatment and the line is from an in-network practice, so nothing is posted to the annual maximum and the patient share is posted to the pediatric out-of-pocket accumulator; pediatric_out_of_network when the person receives that treatment and the line is from an out-of-network practice, so nothing is posted to either.

    Returns:
        A dictionary rendered as text with keys: status ("reprocessed" on success), dental_claim_line_id (reference
        number of the new corrected decision), original_claim_line_id (the denial replaced), plan_paid (USD 2
        decimals), member_responsibility (USD 2 decimals), accumulator_track (as booked), adjudicated_date
        (YYYY-MM-DD decision date of the correction).
    """
    rows = ctx.find("dental_claim_lines", dental_claim_line_id=denied_claim_line_id)
    o = rows[0] if rows else {}
    today = ctx.now()[:10]
    paid = round(float(plan_paid), 2)
    ded = round(float(deductible_applied), 2)
    resp = round(float(member_responsibility), 2)
    rid = ctx.make_id("dcl_", denied_claim_line_id, deductible_applied, coinsurance_pct, plan_paid, member_responsibility,
                      accumulator_track, "grace")
    ctx.create("dental_claim_lines", rid, dental_claim_line_id=rid, event_type="dental_claim_line_adjusted",
               adjudicated_date=today, deductible_applied=ded, coinsurance_pct=int(coinsurance_pct), plan_paid=paid,
               member_responsibility=resp, remark_code="ADJUSTED_REPROCESSED", original_claim_line_id=denied_claim_line_id,
               dental_appeal_id=None, dental_estimate_id=None, **_LineBook.carried(o))
    for kind, amount in _LineBook.postings(accumulator_track, paid, ded, resp):
        pid = ctx.make_id("dap_", rid, kind)
        ctx.create("dental_accumulator_postings", pid, dental_accum_posting_id=pid, dental_plan_id=o.get("dental_plan_id"),
                   customer_id=o.get("customer_id"), event_type=kind, dental_claim_line_id=rid,
                   benefit_year=o.get("benefit_year"), amount=amount, posted_date=today)
    return str({"status": "reprocessed", "dental_claim_line_id": rid, "original_claim_line_id": denied_claim_line_id,
                "plan_paid": paid, "member_responsibility": resp, "accumulator_track": accumulator_track,
                "adjudicated_date": today})


@tool(owner="agent", rw="write")
def reprocess_upgrade_paid_line_3fd2b6c9(ctx: ToolContext, original_claim_line_id: str, benefit_year: str,
                                         deductible_applied: float, coinsurance_pct: int, plan_paid: float,
                                         member_responsibility: float, accumulator_track: str) -> str:
    """Reprocess one paid Dental PPO claim line that was paid at the coinsurance of the plan the enrollment held before a
    change to a richer plan: books a corrected decision that replaces the paid decision, carrying over its claim
    number, line number, practice, network status, procedure, tooth, extraction date, dates of service and receipt,
    billed, allowed and alternate allowances and other-carrier payment, and recording the benefit year it is booked
    to, the corrected deductible, coinsurance, total plan payment and patient share with remark ADJUSTED_REPROCESSED
    and today's decision date. In the same write every annual-maximum, deductible and pediatric out-of-pocket
    posting the replaced decision made is backed out for the same amount and the benefit year it was posted to, any
    deductible taken by the corrected decision is posted to the person's deductible for the benefit year the
    correction is booked to, and its payment or patient share is posted, for that benefit year, to the accumulator
    named by the accumulator track. Afterwards the member's Explanation of Benefits shows the corrected decision and
    the accumulators reflect it.

    Args:
        original_claim_line_id: Id class — reference number of the paid claim-line decision being replaced, as returned by the dental claim-line lookup for the member's enrollment.
        benefit_year: Fixed-format class — benefit year the corrected decision and its postings are booked to, as a four-digit year (YYYY).
        deductible_applied: Fixed-format class — deductible taken on the corrected decision, in USD with 2 decimal places, rounded half up to the cent; 0.00 when no deductible is taken.
        coinsurance_pct: Fixed-format class — coinsurance percentage the corrected decision pays at, integer percent 0-100 (a whole number).
        plan_paid: Fixed-format class — corrected total plan payment for the line (the whole payment, not a difference), in USD with 2 decimal places, rounded half up to the cent.
        member_responsibility: Fixed-format class — corrected patient share for the line, in USD with 2 decimal places, rounded half up to the cent.
        accumulator_track: Enum class — accumulator the corrected decision posts to, besides any deductible taken: annual_maximum when the plan payment counts against the person's annual maximum; pediatric_in_network when the person receives the pediatric essential-health-benefit treatment and the line is from an in-network practice, so nothing is posted to the annual maximum and the patient share is posted to the pediatric out-of-pocket accumulator; pediatric_out_of_network when the person receives that treatment and the line is from an out-of-network practice, so nothing is posted to either.

    Returns:
        A dictionary rendered as text with keys: status ("reprocessed" on success), dental_claim_line_id (reference
        number of the new corrected decision), original_claim_line_id (the decision replaced), plan_paid (USD 2
        decimals), member_responsibility (USD 2 decimals), accumulator_track (as booked), benefit_year (YYYY, as
        booked), adjudicated_date
        (YYYY-MM-DD decision date of the correction).
    """
    rows = ctx.find("dental_claim_lines", dental_claim_line_id=original_claim_line_id)
    o = rows[0] if rows else {}
    today = ctx.now()[:10]
    paid = round(float(plan_paid), 2)
    ded = round(float(deductible_applied), 2)
    resp = round(float(member_responsibility), 2)
    year = str(benefit_year)
    rid = ctx.make_id("dcl_", original_claim_line_id, year, deductible_applied, coinsurance_pct, plan_paid,
                      member_responsibility, accumulator_track, "priorlevel")
    kept = _LineBook.carried(o)
    kept["benefit_year"] = year
    ctx.create("dental_claim_lines", rid, dental_claim_line_id=rid, event_type="dental_claim_line_adjusted",
               adjudicated_date=today, deductible_applied=ded, coinsurance_pct=int(coinsurance_pct), plan_paid=paid,
               member_responsibility=resp, remark_code="ADJUSTED_REPROCESSED", original_claim_line_id=original_claim_line_id,
               dental_appeal_id=None, dental_estimate_id=None, **kept)
    for posted in ctx.find("dental_accumulator_postings", dental_claim_line_id=original_claim_line_id):
        kind = _LineBook.reversal_of(posted.get("event_type"))
        if kind:
            pid = ctx.make_id("dap_", rid, kind)
            ctx.create("dental_accumulator_postings", pid, dental_accum_posting_id=pid,
                       dental_plan_id=o.get("dental_plan_id"), customer_id=o.get("customer_id"), event_type=kind,
                       dental_claim_line_id=original_claim_line_id, benefit_year=posted.get("benefit_year"),
                       amount=posted.get("amount"), posted_date=today)
    for kind, amount in _LineBook.postings(accumulator_track, paid, ded, resp):
        pid = ctx.make_id("dap_", rid, kind)
        ctx.create("dental_accumulator_postings", pid, dental_accum_posting_id=pid, dental_plan_id=o.get("dental_plan_id"),
                   customer_id=o.get("customer_id"), event_type=kind, dental_claim_line_id=rid,
                   benefit_year=year, amount=amount, posted_date=today)
    return str({"status": "reprocessed", "dental_claim_line_id": rid, "original_claim_line_id": original_claim_line_id,
                "plan_paid": paid, "member_responsibility": resp, "accumulator_track": accumulator_track,
                "benefit_year": year, "adjudicated_date": today})


@tool(owner="user", rw="write")
def file_claim_appeal_86dbcb40(ctx: ToolContext, dental_plan_id: str, dental_claim_line_id: str, appeal_level: str,
                               original_appeal_id: str, decision_due_date: str, amount_in_dispute: float) -> str:
    """The member files, in person, an internal post-service appeal of one Dental PPO claim-line decision.
    One call records the filing on the member's enrollment with today's filing date, filed by the member,
    outcome pending and the stated decision due date; for a second-level filing it is linked to the first-level
    decision being appealed. The amount in dispute stated by the member becomes part of the appeal's reference
    number and is printed on the acknowledgment. Afterwards the appeal shows as pending review and the member can
    quote its reference number.

    Args:
        dental_plan_id: Id class — reference number of the member's dental PPO enrollment the appealed decision was made under, as returned by the dental enrollment lookup.
        dental_claim_line_id: Id class — reference number of the appealed claim line, as shown by the dental claim-line lookup; for a second_level filing, the claim line the first-level filing names (shown on the appeal lookup), even where that line has since been reprocessed.
        appeal_level: Enum class — internal review level of this filing: first_level when the line has not been appealed at any level yet; second_level when a decided appeal of the same line is taken to the next internal level (group enrollments only).
        original_appeal_id: Id class — for a second_level filing, reference number of the first-level decision record being appealed, as shown by the dental appeal lookup; an empty string for a first_level filing.
        decision_due_date: Fixed-format class — date by which the appeal must be decided, in YYYY-MM-DD.
        amount_in_dispute: Fixed-format class — plan payment the member contests on the appealed decision, in USD with 2 decimal places, rounded half up to the cent; 0.00 when nothing is contested.

    Returns:
        A dictionary rendered as text with keys: status ("appeal_filed" on success), dental_appeal_id
        (appeal reference number), dental_claim_line_id (line appealed), appeal_level (as filed),
        filed_date (YYYY-MM-DD filing date), decision_due_date (YYYY-MM-DD), amount_in_dispute (USD 2 decimals).
    """
    today = ctx.now()[:10]
    amt = round(float(amount_in_dispute), 2)
    rid = ctx.make_id("dap_appeal_", dental_plan_id, dental_claim_line_id, appeal_level, original_appeal_id,
                      decision_due_date, amount_in_dispute)
    rows = ctx.find("dental_plans", dental_plan_id=dental_plan_id)
    cust = rows[0].get("customer_id") if rows else ""
    ctx.create("dental_appeals", rid, dental_appeal_id=rid, dental_plan_id=dental_plan_id, customer_id=cust,
               event_type="dental_appeal_filed", dental_claim_line_id=dental_claim_line_id, dental_estimate_id=None,
               appeal_type="post_service", appeal_level=appeal_level, filed_by="member", filed_date=today,
               decision_due_date=decision_due_date, decided_date="", outcome="pending",
               original_appeal_id=original_appeal_id or None)
    return str({"status": "appeal_filed", "dental_appeal_id": rid, "dental_claim_line_id": dental_claim_line_id,
                "appeal_level": appeal_level, "filed_date": today, "decision_due_date": decision_due_date,
                "amount_in_dispute": amt})


@tool(owner="user", rw="write")
def submit_estimate_request_d87add4f(ctx: ToolContext, dental_plan_id: str, cdt_code: str, procedure_category: str, tooth_or_area: str,
                                     network_status: str, proposed_fee: float, estimated_allowed: float, estimated_plan_payment: float,
                                     estimated_member_cost: float, estimate_remark: str, valid_through: str) -> str:
    """The member, in person, submits a pre-treatment estimate request for one proposed procedure on their Dental
    PPO enrollment, and the estimate is issued at once with the figures entered: one estimate line is recorded with
    today's request and issue date, a newly generated estimate reference, the proposed procedure, tooth, network,
    proposed fee, allowance, estimated plan payment, estimated patient cost, outcome remark and the last date of
    service it applies to. Afterwards the member can quote the estimate reference to the practice.

    Args:
        dental_plan_id: Id class — reference number of the member's dental PPO enrollment the estimate is for, as returned by the dental enrollment lookup.
        cdt_code: Fixed-format class — proposed procedure code, D followed by 4 digits (ADA CDT code).
        procedure_category: Enum class — Cascade benefit category of the proposed procedure: exam for an oral evaluation; prophylaxis for a cleaning; bitewing_xray for bitewing films; full_mouth_xray for a full-mouth series or panoramic film; fluoride for topical fluoride; sealant for a sealant; filling_amalgam for an amalgam filling; filling_composite_posterior for a tooth-colored filling on a back tooth; filling_composite_anterior for a tooth-colored filling on a front tooth; extraction_simple for a simple extraction; extraction_surgical for a surgical extraction; emergency_palliative for palliative emergency treatment; root_canal for endodontic therapy; scaling_root_planing for scaling and root planing; perio_maintenance for periodontal maintenance; crown for a crown; bridge for a fixed bridge; denture for a denture; implant for an implant; cosmetic_other for cosmetic or other services.
        tooth_or_area: Fixed-format class — tooth number 1-32, primary tooth letter A-T, quadrant UR/UL/LR/LL, or FM for full mouth.
        network_status: Enum class — network the estimate is computed under: in_network_ppo when the practice holds a Cascade PPO Participating Dentist Agreement in force; in_network_premier when it holds a Cascade Premier Participating Dentist Agreement in force and the plan has Premier access; out_of_network when neither applies.
        proposed_fee: Fixed-format class — fee the practice proposed for the procedure, in USD with 2 decimal places.
        estimated_allowed: Fixed-format class — allowance the estimate is computed on, in USD with 2 decimal places.
        estimated_plan_payment: Fixed-format class — estimated plan payment, in USD with 2 decimal places, rounded half up to the cent.
        estimated_member_cost: Fixed-format class — estimated patient cost, in USD with 2 decimal places, rounded half up to the cent.
        estimate_remark: Enum class — outcome remark printed on the estimate: ESTIMATE_COVERED when the procedure is estimated as covered at its own allowance; ESTIMATE_ALTERNATE_BENEFIT when it is estimated on the allowance of an alternate procedure; ESTIMATE_WAITING_PERIOD when a waiting period has not run; ESTIMATE_NOT_COVERED when the procedure is not covered by the plan; ESTIMATE_FREQUENCY_LIMIT when a frequency or interval limit is exceeded; ESTIMATE_MISSING_TOOTH when the missing-tooth clause applies; VOID_COVERAGE_ENDED and VOID_PRACTICE_REQUEST are used only on voided estimates and never on a new request.
        valid_through: Fixed-format class — last date of service the estimate applies to, in YYYY-MM-DD.

    Returns:
        A dictionary rendered as text with keys: status ("estimate_issued" on success), dental_estimate_id (reference
        of the estimate line), estimate_number (estimate reference printed on the estimate), estimated_plan_payment
        (USD 2 decimals), estimated_member_cost (USD 2 decimals), issued_date (YYYY-MM-DD), valid_through (YYYY-MM-DD).
    """
    rows = ctx.find("dental_plans", dental_plan_id=dental_plan_id)
    cust = rows[0].get("customer_id") if rows else ""
    today = ctx.now()[:10]
    rid = ctx.make_id("dpe_", dental_plan_id, cdt_code, procedure_category, tooth_or_area, network_status, proposed_fee,
                      estimated_allowed, estimated_plan_payment, estimated_member_cost, estimate_remark, valid_through)
    number = "PTE71-" + rid[-8:].upper()
    pay = round(float(estimated_plan_payment), 2)
    cost = round(float(estimated_member_cost), 2)
    ctx.create("dental_pretreatment_estimates", rid, dental_estimate_id=rid, dental_plan_id=dental_plan_id, customer_id=cust,
               event_type="dental_estimate_issued", estimate_number=number, provider_agreement_id=None, network_status=network_status,
               cdt_code=cdt_code, procedure_category=procedure_category, tooth_or_area=tooth_or_area, received_date=today,
               issued_date=today, valid_through=valid_through, proposed_fee=round(float(proposed_fee), 2),
               estimated_allowed=round(float(estimated_allowed), 2), estimated_plan_payment=pay, estimated_member_cost=cost,
               estimate_remark=estimate_remark, original_estimate_id=None)
    return str({"status": "estimate_issued", "dental_estimate_id": rid, "estimate_number": number,
                "estimated_plan_payment": pay, "estimated_member_cost": cost, "issued_date": today, "valid_through": valid_through})

"""Hidden task tools of the insurance_claims_and_denials difficulty (coverage category).

Each tool performs one atomic write on the patient's coverage claim ledger. None of them
checks eligibility, status, ownership, deadlines or prerequisites: those are decided by the
agent from the published policy and the records before the call.
"""

from erlbench import ToolContext, tool


@tool(owner="agent", rw="write")
def file_internal_appeal_c10f15cc(ctx: ToolContext, coverage_id: str, customer_id: str, claim_number: str,
                                  order_id: str, source_claim_event_id: str, appeal_level: str,
                                  amount_in_dispute: float) -> str:
    """The laboratory files an internal appeal with a contracted commercial health plan against a
    denial on one of the patient's laboratory claims. One call records one appeal filing, dated
    today, on the claim ledger of the coverage the claim was filed with: the claim number, the
    order the claim bills, the denial line being appealed, the appeal level and the amount in
    dispute. Nothing else on the coverage or the claim changes. On success the appeal filing
    appears in the coverage's claim history and the receipt below is returned.

    Args:
        coverage_id: Id class — reference number of the coverage (health plan on file) the
            appealed claim was filed with, as returned by the coverage lookup.
        customer_id: Id class — the patient's customer reference number, as returned by the
            customer lookup.
        claim_number: Fixed-format class — laboratory claim number of the appealed claim, written
            as 'C' followed by 10 digits exactly as shown on the claim history.
        order_id: Id class — reference number of the order the appealed claim bills, as shown
            on the claim history line.
        source_claim_event_id: Id class — reference number of the denial line being appealed,
            as returned by the claim-history lookup.
        appeal_level: Enum class — the appeal level filed: first_level when no appeal has yet
            been filed on this claim; second_level when the claim's first-level appeal was decided
            and is being taken further; third_level when the claim's second-level appeal was
            decided and is being taken to the final review.
        amount_in_dispute: Fixed-format class — amount in dispute recorded on the filing, in
            USD with 2 decimal places, a positive number rounded half up to the cent.

    Returns:
        A text receipt of the form {'claim_event_id': ..., 'event_type': 'coverage_appeal_filed',
        'claim_number': ..., 'appeal_level': ..., 'amount': ..., 'event_date': ...}:
        claim_event_id is the reference number of the new appeal filing (text); event_type
        confirms an appeal filing was recorded; claim_number and appeal_level echo the claim and
        level filed; amount is the amount in dispute recorded, USD with 2 decimal places;
        event_date is today's date as YYYY-MM-DD. A receipt carrying a claim_event_id means the
        filing was recorded.
    """
    rid = ctx.make_id("cev_", coverage_id, customer_id, claim_number, order_id, source_claim_event_id,
                      appeal_level, amount_in_dispute)
    ctx.create("claim_events", rid, claim_event_id=rid, coverage_id=coverage_id, customer_id=customer_id,
               event_type="coverage_appeal_filed", order_id=order_id, claim_number=claim_number,
               event_date=ctx.now()[:10], amount=round(float(amount_in_dispute), 2), denial_code="",
               responsibility_type="", resubmission_reason="", appeal_level=appeal_level,
               appeal_outcome="", eligibility_result="", source_claim_event_id=source_claim_event_id)
    return str({"claim_event_id": rid, "event_type": "coverage_appeal_filed", "claim_number": claim_number,
                "appeal_level": appeal_level, "amount": round(float(amount_in_dispute), 2),
                "event_date": ctx.now()[:10]})


@tool(owner="agent", rw="write")
def file_information_correction_a0c86b6b(ctx: ToolContext, coverage_id: str, customer_id: str,
                                         claim_number: str, order_id: str, source_claim_event_id: str,
                                         rebill_amount: float) -> str:
    """The laboratory files a corrected claim answering a missing-information denial on one of
    the patient's laboratory claims. One call records one corrected-claim resubmission, dated
    today, on the claim ledger of the coverage the claim was filed with, under the original claim
    number, linked to the denial line it answers and carrying the amount put back in front of
    the plan. Nothing else on the coverage or the claim changes. On success the resubmission
    appears in the coverage's claim history and the receipt below is returned.

    Args:
        coverage_id: Id class — reference number of the coverage the corrected claim goes to, as
            returned by the coverage lookup.
        customer_id: Id class — the patient's customer reference number, as returned by the
            customer lookup.
        claim_number: Fixed-format class — laboratory claim number of the claim being corrected,
            written as 'C' followed by 10 digits exactly as shown on the claim history.
        order_id: Id class — reference number of the order the corrected claim bills, as shown on
            the claim history line.
        source_claim_event_id: Id class — reference number of the missing-information denial line
            the corrected claim answers, as returned by the claim-history lookup.
        rebill_amount: Fixed-format class — amount the corrected claim puts back in front of the
            plan, in USD with 2 decimal places, a non-negative number rounded half up to the cent.

    Returns:
        A text receipt of the form {'claim_event_id': ..., 'event_type':
        'coverage_claim_resubmitted', 'resubmission_reason': 'corrected_claim', 'claim_number': ...,
        'amount': ..., 'event_date': ...}: claim_event_id is the reference number of the new
        resubmission (text); event_type and resubmission_reason confirm a corrected claim was
        recorded; claim_number echoes the claim corrected; amount is the amount put back, USD with
        2 decimal places; event_date is today's date as YYYY-MM-DD. A receipt carrying a
        claim_event_id means the corrected claim was recorded.
    """
    rid = ctx.make_id("cev_", coverage_id, customer_id, claim_number, order_id, source_claim_event_id,
                      rebill_amount, "info")
    ctx.create("claim_events", rid, claim_event_id=rid, coverage_id=coverage_id, customer_id=customer_id,
               event_type="coverage_claim_resubmitted", order_id=order_id, claim_number=claim_number,
               event_date=ctx.now()[:10], amount=round(float(rebill_amount), 2), denial_code="",
               responsibility_type="", resubmission_reason="corrected_claim", appeal_level="",
               appeal_outcome="", eligibility_result="", source_claim_event_id=source_claim_event_id)
    return str({"claim_event_id": rid, "event_type": "coverage_claim_resubmitted",
                "resubmission_reason": "corrected_claim", "claim_number": claim_number,
                "amount": round(float(rebill_amount), 2), "event_date": ctx.now()[:10]})


@tool(owner="user", rw="write")
def sign_member_appeal_c7144598(ctx: ToolContext, coverage_id: str, customer_id: str, claim_number: str,
                                order_id: str, source_claim_event_id: str, appeal_level: str,
                                amount_in_dispute: float) -> str:
    """The patient personally signs and lodges a member appeal with an out-of-network health plan
    that pays second for them, naming the laboratory as their authorized representative for the
    claim. One call records one member appeal filing, dated today, on the claim ledger of that
    coverage: the claim number, the order the claim bills, the denial line appealed, the appeal
    level and the amount in dispute. Nothing else on the coverage or the claim changes. On
    success the member appeal appears in the coverage's claim history and the receipt below is
    returned to the patient.

    Args:
        coverage_id: Id class — reference number of the patient's coverage the member appeal is
            lodged with, as given to the patient by the representative.
        customer_id: Id class — the patient's own customer reference number, as given to the
            patient by the representative.
        claim_number: Fixed-format class — laboratory claim number of the appealed claim, written
            as 'C' followed by 10 digits exactly as given by the representative.
        order_id: Id class — reference number of the order the appealed claim bills, as given by
            the representative.
        source_claim_event_id: Id class — reference number of the denial line appealed, as given
            by the representative.
        appeal_level: Enum class — the appeal level lodged: first_level when no appeal has yet
            been lodged on this claim; second_level when the claim's first-level appeal was decided
            and is being taken further; third_level when the claim's second-level appeal was
            decided and is being taken to the final review.
        amount_in_dispute: Fixed-format class — amount in dispute recorded on the member appeal,
            in USD with 2 decimal places, a positive number rounded half up to the cent, as told to
            the patient by the representative.

    Returns:
        A text receipt of the form {'claim_event_id': ..., 'event_type': 'coverage_appeal_filed',
        'claim_number': ..., 'appeal_level': ..., 'amount': ..., 'event_date': ...}:
        claim_event_id is the reference number of the lodged member appeal (text); event_type
        confirms an appeal filing was recorded; claim_number and appeal_level echo the claim and
        level; amount is the amount in dispute recorded, USD with 2 decimal places; event_date is
        today's date as YYYY-MM-DD. A receipt carrying a claim_event_id means the member appeal
        was lodged.
    """
    rid = ctx.make_id("cev_", coverage_id, customer_id, claim_number, order_id, source_claim_event_id,
                      appeal_level, amount_in_dispute, "member")
    ctx.create("claim_events", rid, claim_event_id=rid, coverage_id=coverage_id, customer_id=customer_id,
               event_type="coverage_appeal_filed", order_id=order_id, claim_number=claim_number,
               event_date=ctx.now()[:10], amount=round(float(amount_in_dispute), 2), denial_code="",
               responsibility_type="", resubmission_reason="", appeal_level=appeal_level,
               appeal_outcome="", eligibility_result="", source_claim_event_id=source_claim_event_id)
    return str({"claim_event_id": rid, "event_type": "coverage_appeal_filed", "claim_number": claim_number,
                "appeal_level": appeal_level, "amount": round(float(amount_in_dispute), 2),
                "event_date": ctx.now()[:10]})


@tool(owner="agent", rw="write")
def file_identification_correction_4ff16e31(ctx: ToolContext, coverage_id: str, customer_id: str,
                                            claim_number: str, order_id: str, source_claim_event_id: str,
                                            rebill_amount: float) -> str:
    """The laboratory files a corrected claim answering a patient-identification denial on one of
    the patient's laboratory claims, with the patient's details corrected. One call records one
    corrected-claim resubmission, dated today, on the claim ledger of the coverage the claim was
    filed with, under the original claim number, linked to the denial line it answers and
    carrying the amount put back in front of the plan. Nothing else on the coverage or the claim
    changes. On success the resubmission appears in the coverage's claim history and the receipt
    below is returned.

    Args:
        coverage_id: Id class — reference number of the coverage the corrected claim goes to, as
            returned by the coverage lookup.
        customer_id: Id class — the patient's customer reference number, as returned by the
            customer lookup.
        claim_number: Fixed-format class — laboratory claim number of the claim being corrected,
            written as 'C' followed by 10 digits exactly as shown on the claim history.
        order_id: Id class — reference number of the order the corrected claim bills, as shown on
            the claim history line.
        source_claim_event_id: Id class — reference number of the patient-identification denial
            line the corrected claim answers, as returned by the claim-history lookup.
        rebill_amount: Fixed-format class — amount the corrected claim puts back in front of the
            plan, in USD with 2 decimal places, a non-negative number rounded half up to the cent.

    Returns:
        A text receipt of the form {'claim_event_id': ..., 'event_type':
        'coverage_claim_resubmitted', 'resubmission_reason': 'corrected_claim', 'claim_number': ...,
        'amount': ..., 'event_date': ...}: claim_event_id is the reference number of the new
        resubmission (text); event_type and resubmission_reason confirm a corrected claim was
        recorded; claim_number echoes the claim corrected; amount is the amount put back, USD with
        2 decimal places; event_date is today's date as YYYY-MM-DD. A receipt carrying a
        claim_event_id means the corrected claim was recorded.
    """
    rid = ctx.make_id("cev_", coverage_id, customer_id, claim_number, order_id, source_claim_event_id,
                      rebill_amount, "ident")
    ctx.create("claim_events", rid, claim_event_id=rid, coverage_id=coverage_id, customer_id=customer_id,
               event_type="coverage_claim_resubmitted", order_id=order_id, claim_number=claim_number,
               event_date=ctx.now()[:10], amount=round(float(rebill_amount), 2), denial_code="",
               responsibility_type="", resubmission_reason="corrected_claim", appeal_level="",
               appeal_outcome="", eligibility_result="", source_claim_event_id=source_claim_event_id)
    return str({"claim_event_id": rid, "event_type": "coverage_claim_resubmitted",
                "resubmission_reason": "corrected_claim", "claim_number": claim_number,
                "amount": round(float(rebill_amount), 2), "event_date": ctx.now()[:10]})


@tool(owner="agent", rw="write")
def file_plan_appeal_d031f80e(ctx: ToolContext, coverage_id: str, customer_id: str, claim_number: str,
                              order_id: str, source_claim_event_id: str, appeal_level: str,
                              amount_in_dispute: float) -> str:
    """The laboratory files a plan appeal with a Medicaid managed care plan against a denial on one
    of the patient's laboratory claims that plan holds. One call records one appeal filing, dated
    today, on the claim ledger of the Medicaid coverage: the claim number, the order the claim
    bills, the denial line appealed, the appeal level and the amount in dispute. Nothing else on
    the coverage or the claim changes. On success the plan appeal appears in the coverage's claim
    history and the receipt below is returned.

    Args:
        coverage_id: Id class — reference number of the Medicaid coverage holding the appealed
            claim, as returned by the coverage lookup.
        customer_id: Id class — the patient's customer reference number, as returned by the
            customer lookup.
        claim_number: Fixed-format class — laboratory claim number of the appealed claim, written
            as 'C' followed by 10 digits exactly as shown on the claim history.
        order_id: Id class — reference number of the order the appealed claim bills, as shown on
            the claim history line.
        source_claim_event_id: Id class — reference number of the denial line appealed, as
            returned by the claim-history lookup.
        appeal_level: Enum class — the appeal level filed: first_level when no appeal has yet
            been filed on this claim; second_level when the claim's first-level appeal was decided
            and is being taken further; third_level when the claim's second-level appeal was
            decided and is being taken to the final review.
        amount_in_dispute: Fixed-format class — amount in dispute recorded on the filing, in
            USD with 2 decimal places, a positive number rounded half up to the cent.

    Returns:
        A text receipt of the form {'claim_event_id': ..., 'event_type': 'coverage_appeal_filed',
        'claim_number': ..., 'appeal_level': ..., 'amount': ..., 'event_date': ...}:
        claim_event_id is the reference number of the new plan appeal (text); event_type confirms
        an appeal filing was recorded; claim_number and appeal_level echo the claim and level;
        amount is the amount in dispute recorded, USD with 2 decimal places; event_date is
        today's date as YYYY-MM-DD. A receipt carrying a claim_event_id means the plan appeal was
        filed.
    """
    rid = ctx.make_id("cev_", coverage_id, customer_id, claim_number, order_id, source_claim_event_id,
                      appeal_level, amount_in_dispute, "plan")
    ctx.create("claim_events", rid, claim_event_id=rid, coverage_id=coverage_id, customer_id=customer_id,
               event_type="coverage_appeal_filed", order_id=order_id, claim_number=claim_number,
               event_date=ctx.now()[:10], amount=round(float(amount_in_dispute), 2), denial_code="",
               responsibility_type="", resubmission_reason="", appeal_level=appeal_level,
               appeal_outcome="", eligibility_result="", source_claim_event_id=source_claim_event_id)
    return str({"claim_event_id": rid, "event_type": "coverage_appeal_filed", "claim_number": claim_number,
                "appeal_level": appeal_level, "amount": round(float(amount_in_dispute), 2),
                "event_date": ctx.now()[:10]})


@tool(owner="agent", rw="write")
def file_authorization_correction_79145f91(ctx: ToolContext, coverage_id: str, customer_id: str,
                                           claim_number: str, order_id: str, source_claim_event_id: str,
                                           rebill_amount: float) -> str:
    """The laboratory files a corrected claim carrying the retroactive authorization, answering an
    authorization-absent denial on one of the patient's laboratory claims. One call records one
    corrected-claim resubmission, dated today, on the claim ledger of the coverage holding the
    claim, under the original claim number, linked to the denial line it answers and carrying the
    amount put back in front of the plan. Nothing else on the coverage or the claim changes. On
    success the resubmission appears in the coverage's claim history and the receipt below is
    returned.

    Args:
        coverage_id: Id class — reference number of the coverage holding the claim, as returned by
            the coverage lookup.
        customer_id: Id class — the patient's customer reference number, as returned by the
            customer lookup.
        claim_number: Fixed-format class — laboratory claim number of the claim being corrected,
            written as 'C' followed by 10 digits exactly as shown on the claim history.
        order_id: Id class — reference number of the order the corrected claim bills, as shown on
            the claim history line.
        source_claim_event_id: Id class — reference number of the authorization denial line the
            corrected claim answers, as returned by the claim-history lookup.
        rebill_amount: Fixed-format class — amount the corrected claim puts back in front of the
            plan, in USD with 2 decimal places, a non-negative number rounded half up to the cent.

    Returns:
        A text receipt of the form {'claim_event_id': ..., 'event_type':
        'coverage_claim_resubmitted', 'resubmission_reason': 'corrected_claim', 'claim_number': ...,
        'amount': ..., 'event_date': ...}: claim_event_id is the reference number of the new
        resubmission (text); event_type and resubmission_reason confirm a corrected claim was
        recorded; claim_number echoes the claim corrected; amount is the amount put back, USD with
        2 decimal places; event_date is today's date as YYYY-MM-DD. A receipt carrying a
        claim_event_id means the corrected claim was recorded.
    """
    rid = ctx.make_id("cev_", coverage_id, customer_id, claim_number, order_id, source_claim_event_id,
                      rebill_amount, "auth")
    ctx.create("claim_events", rid, claim_event_id=rid, coverage_id=coverage_id, customer_id=customer_id,
               event_type="coverage_claim_resubmitted", order_id=order_id, claim_number=claim_number,
               event_date=ctx.now()[:10], amount=round(float(rebill_amount), 2), denial_code="",
               responsibility_type="", resubmission_reason="corrected_claim", appeal_level="",
               appeal_outcome="", eligibility_result="", source_claim_event_id=source_claim_event_id)
    return str({"claim_event_id": rid, "event_type": "coverage_claim_resubmitted",
                "resubmission_reason": "corrected_claim", "claim_number": claim_number,
                "amount": round(float(rebill_amount), 2), "event_date": ctx.now()[:10]})


@tool(owner="user", rw="write")
def sign_primary_member_appeal_ad6f2953(ctx: ToolContext, coverage_id: str, customer_id: str,
                                        claim_number: str, order_id: str, source_claim_event_id: str,
                                        appeal_level: str, amount_in_dispute: float) -> str:
    """The patient personally signs and lodges a member appeal with an out-of-network health plan
    that pays first for them, naming the laboratory as their authorized representative for the
    claim. One call records one member appeal filing, dated today, on the claim ledger of that
    coverage: the claim number, the order the claim bills, the denial line appealed, the appeal
    level and the amount in dispute. Nothing else on the coverage or the claim changes. On success
    the member appeal appears in the coverage's claim history and the receipt below is returned to
    the patient.

    Args:
        coverage_id: Id class — reference number of the patient's coverage the member appeal is
            lodged with, as given to the patient by the representative.
        customer_id: Id class — the patient's own customer reference number, as given to the
            patient by the representative.
        claim_number: Fixed-format class — laboratory claim number of the appealed claim, written
            as 'C' followed by 10 digits exactly as given by the representative.
        order_id: Id class — reference number of the order the appealed claim bills, as given by
            the representative.
        source_claim_event_id: Id class — reference number of the denial line appealed, as given
            by the representative.
        appeal_level: Enum class — the appeal level lodged: first_level when no appeal has yet
            been lodged on this claim; second_level when the claim's first-level appeal was decided
            and is being taken further; third_level when the claim's second-level appeal was
            decided and is being taken to the final review.
        amount_in_dispute: Fixed-format class — amount in dispute recorded on the member appeal,
            in USD with 2 decimal places, a positive number rounded half up to the cent, as told to
            the patient by the representative.

    Returns:
        A text receipt of the form {'claim_event_id': ..., 'event_type': 'coverage_appeal_filed',
        'claim_number': ..., 'appeal_level': ..., 'amount': ..., 'event_date': ...}:
        claim_event_id is the reference number of the lodged member appeal (text); event_type
        confirms an appeal filing was recorded; claim_number and appeal_level echo the claim and
        level; amount is the amount in dispute recorded, USD with 2 decimal places; event_date is
        today's date as YYYY-MM-DD. A receipt carrying a claim_event_id means the member appeal
        was lodged.
    """
    rid = ctx.make_id("cev_", coverage_id, customer_id, claim_number, order_id, source_claim_event_id,
                      appeal_level, amount_in_dispute, "first-plan member")
    ctx.create("claim_events", rid, claim_event_id=rid, coverage_id=coverage_id, customer_id=customer_id,
               event_type="coverage_appeal_filed", order_id=order_id, claim_number=claim_number,
               event_date=ctx.now()[:10], amount=round(float(amount_in_dispute), 2), denial_code="",
               responsibility_type="", resubmission_reason="", appeal_level=appeal_level,
               appeal_outcome="", eligibility_result="", source_claim_event_id=source_claim_event_id)
    return str({"claim_event_id": rid, "event_type": "coverage_appeal_filed", "claim_number": claim_number,
                "appeal_level": appeal_level, "amount": round(float(amount_in_dispute), 2),
                "event_date": ctx.now()[:10]})


@tool(owner="agent", rw="write")
def file_coordination_correction_d59a8135(ctx: ToolContext, coverage_id: str, customer_id: str,
                                          claim_number: str, order_id: str, source_claim_event_id: str,
                                          rebill_amount: float) -> str:
    """The laboratory refiles a claim with the patient's current coordination of benefits,
    answering an other-coverage denial on one of the patient's laboratory claims. One call records
    one coordination-of-benefits resubmission, dated today, on the claim ledger of the coverage the
    claim was filed with, under the original claim number, linked to the denial line it answers
    and carrying the amount put back in front of the plan. Nothing else on the coverage or the
    claim changes. On success the resubmission appears in the coverage's claim history and the
    receipt below is returned.

    Args:
        coverage_id: Id class — reference number of the coverage the claim is refiled with, as
            returned by the coverage lookup.
        customer_id: Id class — the patient's customer reference number, as returned by the
            customer lookup.
        claim_number: Fixed-format class — laboratory claim number of the claim being refiled,
            written as 'C' followed by 10 digits exactly as shown on the claim history.
        order_id: Id class — reference number of the order the refiled claim bills, as shown on the
            claim history line.
        source_claim_event_id: Id class — reference number of the other-coverage denial line the
            refiled claim answers, as returned by the claim-history lookup.
        rebill_amount: Fixed-format class — amount the refiled claim puts back in front of the
            plan, in USD with 2 decimal places, a non-negative number rounded half up to the cent.

    Returns:
        A text receipt of the form {'claim_event_id': ..., 'event_type':
        'coverage_claim_resubmitted', 'resubmission_reason': 'coordination_of_benefits_update',
        'claim_number': ..., 'amount': ..., 'event_date': ...}: claim_event_id is the reference
        number of the new resubmission (text); event_type and resubmission_reason confirm a
        coordination-of-benefits resubmission was recorded; claim_number echoes the claim refiled;
        amount is the amount put back, USD with 2 decimal places; event_date is today's date as
        YYYY-MM-DD. A receipt carrying a claim_event_id means the refiled claim was recorded.
    """
    rid = ctx.make_id("cev_", coverage_id, customer_id, claim_number, order_id, source_claim_event_id,
                      rebill_amount, "coord")
    ctx.create("claim_events", rid, claim_event_id=rid, coverage_id=coverage_id, customer_id=customer_id,
               event_type="coverage_claim_resubmitted", order_id=order_id, claim_number=claim_number,
               event_date=ctx.now()[:10], amount=round(float(rebill_amount), 2), denial_code="",
               responsibility_type="", resubmission_reason="coordination_of_benefits_update",
               appeal_level="", appeal_outcome="", eligibility_result="",
               source_claim_event_id=source_claim_event_id)
    return str({"claim_event_id": rid, "event_type": "coverage_claim_resubmitted",
                "resubmission_reason": "coordination_of_benefits_update", "claim_number": claim_number,
                "amount": round(float(rebill_amount), 2), "event_date": ctx.now()[:10]})

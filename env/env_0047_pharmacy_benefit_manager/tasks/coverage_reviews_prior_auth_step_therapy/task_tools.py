"""Hidden task tools of the coverage_reviews_prior_auth_step_therapy difficulty (category review).

Each tool lands one atomic coverage-review write on a member's Utilization Management Program; it
takes the values the agent has already worked out from policy and records, performs no eligibility
judgement, and is reached only through the unlock_* -> call_* meta-tools.
"""

from erlbench import ToolContext, tool


@tool(owner="user", rw="write")
def file_coverage_review_request_fd0cbfbe(ctx: ToolContext, customer_id: str, review_program_id: str,
                                           drug_name: str, drug_strength: str, review_type: str,
                                           prescriber_npi: str, requested_quantity_per_30: float) -> str:
    """The member files, in their own name, a first-time coverage review request for one drug on
    their Utilization Management Program. One call opens one new undecided review case recorded as
    requested by the member, at standard priority, not as a renewal, with no diagnosis and no clinical
    ground of its own (the prescriber's clinical information is what the reviewer decides on), carrying
    the drug, the strength, the kind of review, the prescriber and the quantity per rolling 30 days the
    request asks for. Afterwards the member's case history shows the new open case with its reference
    number; the request is complete when the receipt shows status "open".

    Args:
        customer_id: Id class — the customer reference number of the member filing the request, as read from the customer profile lookup.
        review_program_id: Id class — the reference number of the member's Utilization Management Program, as read from the review program lookup.
        drug_name: Enum class — the drug the request is for, one of: atorvastatin when the case concerns atorvastatin; lisinopril when the case concerns lisinopril;
            metformin when the case concerns metformin; sertraline when the case concerns
            sertraline; levothyroxine when the case concerns levothyroxine; sumatriptan when the
            case concerns sumatriptan; oxycodone-acetaminophen when the case concerns oxycodone-
            acetaminophen; insulin glargine-yfgn when the case concerns insulin glargine-yfgn;
            Lantus when the case concerns Lantus; Eliquis when the case concerns Eliquis;
            Xarelto when the case concerns Xarelto; Jardiance when the case concerns Jardiance;
            Ozempic when the case concerns Ozempic; Mounjaro when the case concerns Mounjaro;
            Wegovy when the case concerns Wegovy; Zepbound when the case concerns Zepbound;
            Trelegy Ellipta when the case concerns Trelegy Ellipta; Breztri Aerosphere when the
            case concerns Breztri Aerosphere; Nurtec ODT when the case concerns Nurtec ODT;
            Ubrelvy when the case concerns Ubrelvy; Humira when the case concerns Humira;
            adalimumab-adaz when the case concerns adalimumab-adaz; Dupixent when the case
            concerns Dupixent; Skyrizi when the case concerns Skyrizi; Rinvoq when the case
            concerns Rinvoq; Enbrel when the case concerns Enbrel; Biktarvy when the case
            concerns Biktarvy; Ibrance when the case concerns Ibrance.
        drug_strength: Verbatim class — the strength and dosage form of the drug exactly as the member reads it from their prescription label in the conversation, copied character for character (verbatim).
        review_type: Enum class — the kind of coverage review requested: prior_authorization when the drug needs a prior authorization approval before it is covered; step_therapy_exception when the drug failed a step therapy edit and the request asks to cover it without the required earlier trials; quantity_limit_exception when the request asks to cover more of the drug per rolling 30 days than its quantity limit allows.
        prescriber_npi: Fixed-format class — the NPI of the prescriber who wrote the prescription the request concerns, as shown on the member's prescription records, written as 10 digits with no spaces or punctuation.
        requested_quantity_per_30: Fixed-format class — the quantity of the drug per rolling 30 days the request asks for, in decimal units, up to 3 decimals (rounded to 3 decimal places); 0 for a request that is not a quantity limit exception.

    Returns:
        A dictionary receipt with: case_id (string, the reference number of the newly opened review
        case), drug_name (string, the drug), review_type (string, the kind of review),
        requested_quantity_per_30 (number, the quantity per rolling 30 days asked for, up to 3
        decimals), requested_by (string, always "member"), status (string, "open" when the request was
        filed) and opened_at (string, the moment the request was received, ISO timestamp).
    """
    rid = ctx.make_id("rvc_", customer_id, review_program_id, drug_name, drug_strength, review_type,
                      prescriber_npi, requested_quantity_per_30)
    qty = round(float(requested_quantity_per_30), 3)
    ctx.create("review_cases", rid, review_case_id=rid, review_program_id=review_program_id,
               customer_id=customer_id, event_type="review_case_opened", source_case_id="",
               drug_name=drug_name, drug_strength=drug_strength, review_type=review_type,
               is_renewal=False, review_priority="standard", requested_by="member",
               prescriber_npi=str(prescriber_npi), diagnosis_code="", criteria_basis="not_applicable",
               requested_quantity_per_30=qty, event_at=ctx.now(), decision_reason="not_applicable")
    return str({"case_id": rid, "drug_name": drug_name, "review_type": review_type,
                "requested_quantity_per_30": qty, "requested_by": "member", "status": "open",
                "opened_at": ctx.now()})


@tool(owner="agent", rw="write")
def approve_quantity_exception_611b3a5d(ctx: ToolContext, customer_id: str, review_program_id: str,
                                        source_case_id: str, drug_name: str,
                                        approved_quantity_per_30: float, effective_date: str,
                                        expiration_date: str) -> str:
    """Approve one undecided first-time quantity limit exception case and put its quantity limit
    authorization in force. One call records the approval decision on the case with the reason
    criteria_met and the approved quantity, and records a new quantity limit authorization for the
    drug, produced by clinical review, carrying the approved quantity per rolling 30 days and its
    first and last days in force. Afterwards the case shows as approved and the member's
    authorizations list the new quantity limit authorization; the approval is complete when the
    receipt shows status "approved".

    Args:
        customer_id: Id class — the customer reference number of the member, as read from the customer profile lookup.
        review_program_id: Id class — the reference number of the member's Utilization Management Program, as read from the review program lookup.
        source_case_id: Id class — the reference number of the opening of the case being approved, as returned when the request was filed or as read from the review case lookup.
        drug_name: Enum class — the drug of the case, one of: atorvastatin when the authorization concerns atorvastatin; lisinopril when the authorization
            concerns lisinopril; metformin when the authorization concerns metformin; sertraline
            when the authorization concerns sertraline; levothyroxine when the authorization
            concerns levothyroxine; sumatriptan when the authorization concerns sumatriptan;
            oxycodone-acetaminophen when the authorization concerns oxycodone-acetaminophen;
            insulin glargine-yfgn when the authorization concerns insulin glargine-yfgn; Lantus
            when the authorization concerns Lantus; Eliquis when the authorization concerns
            Eliquis; Xarelto when the authorization concerns Xarelto; Jardiance when the
            authorization concerns Jardiance; Ozempic when the authorization concerns Ozempic;
            Mounjaro when the authorization concerns Mounjaro; Wegovy when the authorization
            concerns Wegovy; Zepbound when the authorization concerns Zepbound; Trelegy Ellipta
            when the authorization concerns Trelegy Ellipta; Breztri Aerosphere when the
            authorization concerns Breztri Aerosphere; Nurtec ODT when the authorization
            concerns Nurtec ODT; Ubrelvy when the authorization concerns Ubrelvy; Humira when
            the authorization concerns Humira; adalimumab-adaz when the authorization concerns
            adalimumab-adaz; Dupixent when the authorization concerns Dupixent; Skyrizi when the
            authorization concerns Skyrizi; Rinvoq when the authorization concerns Rinvoq;
            Enbrel when the authorization concerns Enbrel; Biktarvy when the authorization
            concerns Biktarvy; Ibrance when the authorization concerns Ibrance.
        approved_quantity_per_30: Fixed-format class — the approved quantity of the drug per rolling 30 days, in decimal units, up to 3 decimals (rounded to 3 decimal places).
        effective_date: Fixed-format class — the first day the authorization is in force, written YYYY-MM-DD.
        expiration_date: Fixed-format class — the last day the authorization is in force, written YYYY-MM-DD.

    Returns:
        A dictionary receipt with: decision_id (string, the reference number of the approval
        decision on the case), authorization_id (string, the reference number of the new quantity
        limit authorization), drug_name (string), approved_quantity_per_30 (number, up to 3
        decimals), effective_date and expiration_date (strings, YYYY-MM-DD) and status (string,
        "approved" when the case was approved and the authorization put in force).
    """
    qty = round(float(approved_quantity_per_30), 3)
    did = ctx.make_id("rvd_", customer_id, review_program_id, source_case_id, drug_name, qty,
                      effective_date, expiration_date)
    aid = ctx.make_id("rva_", customer_id, review_program_id, source_case_id, drug_name, qty,
                      effective_date, expiration_date)
    ctx.create("review_cases", did, review_case_id=did, review_program_id=review_program_id,
               customer_id=customer_id, event_type="review_case_approved", source_case_id=source_case_id,
               drug_name=drug_name, review_type="quantity_limit_exception", is_renewal=False,
               requested_quantity_per_30=qty, decision_reason="criteria_met", event_at=ctx.now())
    ctx.create("review_authorizations", aid, review_authorization_id=aid,
               review_program_id=review_program_id, customer_id=customer_id,
               event_type="review_auth_granted", source_case_id=source_case_id,
               source_authorization_id="", drug_name=drug_name, authorization_type="quantity_limit",
               auth_basis="clinical_review", approved_quantity_per_30=qty,
               effective_date=effective_date, expiration_date=expiration_date,
               termination_reason="not_applicable")
    return str({"decision_id": did, "authorization_id": aid, "drug_name": drug_name,
                "approved_quantity_per_30": qty, "effective_date": effective_date,
                "expiration_date": expiration_date, "status": "approved"})


@tool(owner="agent", rw="write")
def grant_continuity_authorization_38eb93b7(ctx: ToolContext, customer_id: str, review_program_id: str,
                                            source_case_id: str, drug_name: str,
                                            approved_quantity_per_30: float, effective_date: str,
                                            expiration_date: str) -> str:
    """Put a continuity-of-care quantity limit authorization in force for a new member whose prior
    pharmacy carrier's approval for the drug is on file. One call records one new quantity limit
    authorization for the drug that came about through continuity of care, linked to the member's case
    that carries the prior carrier's approval, with the quantity per rolling 30 days it covers and its
    first and last days in force; no review decision is recorded. Afterwards the member's
    authorizations list it; the grant is complete when the receipt shows status "in_force".

    Args:
        customer_id: Id class — the customer reference number of the member, as read from the customer profile lookup.
        review_program_id: Id class — the reference number of the member's Utilization Management Program, as read from the review program lookup.
        source_case_id: Id class — the reference number of the opening of the member's case that relies on the prior carrier's approval, as read from the review case lookup.
        drug_name: Enum class — the drug the authorization covers, one of: atorvastatin when the authorization concerns atorvastatin; lisinopril when the authorization
            concerns lisinopril; metformin when the authorization concerns metformin; sertraline
            when the authorization concerns sertraline; levothyroxine when the authorization
            concerns levothyroxine; sumatriptan when the authorization concerns sumatriptan;
            oxycodone-acetaminophen when the authorization concerns oxycodone-acetaminophen;
            insulin glargine-yfgn when the authorization concerns insulin glargine-yfgn; Lantus
            when the authorization concerns Lantus; Eliquis when the authorization concerns
            Eliquis; Xarelto when the authorization concerns Xarelto; Jardiance when the
            authorization concerns Jardiance; Ozempic when the authorization concerns Ozempic;
            Mounjaro when the authorization concerns Mounjaro; Wegovy when the authorization
            concerns Wegovy; Zepbound when the authorization concerns Zepbound; Trelegy Ellipta
            when the authorization concerns Trelegy Ellipta; Breztri Aerosphere when the
            authorization concerns Breztri Aerosphere; Nurtec ODT when the authorization
            concerns Nurtec ODT; Ubrelvy when the authorization concerns Ubrelvy; Humira when
            the authorization concerns Humira; adalimumab-adaz when the authorization concerns
            adalimumab-adaz; Dupixent when the authorization concerns Dupixent; Skyrizi when the
            authorization concerns Skyrizi; Rinvoq when the authorization concerns Rinvoq;
            Enbrel when the authorization concerns Enbrel; Biktarvy when the authorization
            concerns Biktarvy; Ibrance when the authorization concerns Ibrance.
        approved_quantity_per_30: Fixed-format class — the quantity of the drug per rolling 30 days the authorization covers, in decimal units, up to 3 decimals (rounded to 3 decimal places).
        effective_date: Fixed-format class — the first day the authorization is in force, written YYYY-MM-DD.
        expiration_date: Fixed-format class — the last day the authorization is in force, written YYYY-MM-DD.

    Returns:
        A dictionary receipt with: authorization_id (string, the reference number of the new
        authorization), drug_name (string), auth_basis (string, always "continuity_of_care"),
        approved_quantity_per_30 (number, up to 3 decimals), effective_date and expiration_date
        (strings, YYYY-MM-DD) and status (string, "in_force" when the authorization was recorded).
    """
    qty = round(float(approved_quantity_per_30), 3)
    aid = ctx.make_id("rva_", customer_id, review_program_id, source_case_id, drug_name, qty,
                      effective_date, expiration_date, "continuity")
    ctx.create("review_authorizations", aid, review_authorization_id=aid,
               review_program_id=review_program_id, customer_id=customer_id,
               event_type="review_auth_granted", source_case_id=source_case_id,
               source_authorization_id="", drug_name=drug_name, authorization_type="quantity_limit",
               auth_basis="continuity_of_care", approved_quantity_per_30=qty,
               effective_date=effective_date, expiration_date=expiration_date,
               termination_reason="not_applicable")
    return str({"authorization_id": aid, "drug_name": drug_name, "auth_basis": "continuity_of_care",
                "approved_quantity_per_30": qty, "effective_date": effective_date,
                "expiration_date": expiration_date, "status": "in_force"})


@tool(owner="user", rw="write")
def file_renewal_request_18124eb7(ctx: ToolContext, customer_id: str, review_program_id: str,
                                  drug_name: str, drug_strength: str, review_type: str,
                                  prescriber_npi: str, requested_quantity_per_30: float) -> str:
    """The member files, in their own name, a renewal request for an authorization they hold on one
    drug under their Utilization Management Program. One call opens one new undecided review case
    recorded as a renewal requested by the member, at standard priority, with no diagnosis and no
    clinical ground of its own, carrying the drug, the strength, the kind of review, the prescriber and
    the quantity per rolling 30 days the renewal asks for. Afterwards the member's case history shows
    the new open renewal case with its reference number; the request is complete when the receipt
    shows status "open".

    Args:
        customer_id: Id class — the customer reference number of the member filing the renewal, as read from the customer profile lookup.
        review_program_id: Id class — the reference number of the member's Utilization Management Program, as read from the review program lookup.
        drug_name: Enum class — the drug whose authorization is renewed, one of: atorvastatin when the case concerns atorvastatin; lisinopril when the case concerns lisinopril;
            metformin when the case concerns metformin; sertraline when the case concerns
            sertraline; levothyroxine when the case concerns levothyroxine; sumatriptan when the
            case concerns sumatriptan; oxycodone-acetaminophen when the case concerns oxycodone-
            acetaminophen; insulin glargine-yfgn when the case concerns insulin glargine-yfgn;
            Lantus when the case concerns Lantus; Eliquis when the case concerns Eliquis;
            Xarelto when the case concerns Xarelto; Jardiance when the case concerns Jardiance;
            Ozempic when the case concerns Ozempic; Mounjaro when the case concerns Mounjaro;
            Wegovy when the case concerns Wegovy; Zepbound when the case concerns Zepbound;
            Trelegy Ellipta when the case concerns Trelegy Ellipta; Breztri Aerosphere when the
            case concerns Breztri Aerosphere; Nurtec ODT when the case concerns Nurtec ODT;
            Ubrelvy when the case concerns Ubrelvy; Humira when the case concerns Humira;
            adalimumab-adaz when the case concerns adalimumab-adaz; Dupixent when the case
            concerns Dupixent; Skyrizi when the case concerns Skyrizi; Rinvoq when the case
            concerns Rinvoq; Enbrel when the case concerns Enbrel; Biktarvy when the case
            concerns Biktarvy; Ibrance when the case concerns Ibrance.
        drug_strength: Verbatim class — the strength and dosage form of the drug exactly as the member reads it from their prescription label in the conversation, copied character for character (verbatim).
        review_type: Enum class — the kind of authorization being renewed: prior_authorization when the renewal continues a prior authorization approval; step_therapy_exception when it continues a step therapy approval; quantity_limit_exception when it continues coverage of more of the drug per rolling 30 days than its quantity limit allows.
        prescriber_npi: Fixed-format class — the NPI of the prescriber of the drug, as shown on the member's prescription records, written as 10 digits with no spaces or punctuation.
        requested_quantity_per_30: Fixed-format class — the quantity of the drug per rolling 30 days the renewal asks for, in decimal units, up to 3 decimals (rounded to 3 decimal places); 0 for a renewal that is not a quantity limit exception.

    Returns:
        A dictionary receipt with: case_id (string, the reference number of the newly opened renewal
        case), drug_name (string, the drug), review_type (string, the kind of review), is_renewal
        (boolean, always true), requested_quantity_per_30 (number, up to 3 decimals), status (string,
        "open" when the renewal was filed) and opened_at (string, the moment it was received, ISO
        timestamp).
    """
    rid = ctx.make_id("rvc_", customer_id, review_program_id, drug_name, drug_strength, review_type,
                      prescriber_npi, requested_quantity_per_30, "renewal")
    qty = round(float(requested_quantity_per_30), 3)
    ctx.create("review_cases", rid, review_case_id=rid, review_program_id=review_program_id,
               customer_id=customer_id, event_type="review_case_opened", source_case_id="",
               drug_name=drug_name, drug_strength=drug_strength, review_type=review_type,
               is_renewal=True, review_priority="standard", requested_by="member",
               prescriber_npi=str(prescriber_npi), diagnosis_code="", criteria_basis="not_applicable",
               requested_quantity_per_30=qty, event_at=ctx.now(), decision_reason="not_applicable")
    return str({"case_id": rid, "drug_name": drug_name, "review_type": review_type, "is_renewal": True,
                "requested_quantity_per_30": qty, "status": "open", "opened_at": ctx.now()})


@tool(owner="agent", rw="write")
def approve_quantity_renewal_696a9005(ctx: ToolContext, customer_id: str, review_program_id: str,
                                      source_case_id: str, drug_name: str,
                                      approved_quantity_per_30: float, effective_date: str,
                                      expiration_date: str) -> str:
    """Approve one undecided quantity limit renewal case and put the renewed quantity limit
    authorization in force. One call records the approval decision on the renewal case with the reason
    criteria_met and the approved quantity, and records a new quantity limit authorization for the
    drug, produced by clinical review, carrying the approved quantity per rolling 30 days and its first
    and last days in force. Afterwards the renewal case shows as approved and the member's
    authorizations list the renewed authorization; the approval is complete when the receipt shows
    status "renewed".

    Args:
        customer_id: Id class — the customer reference number of the member, as read from the customer profile lookup.
        review_program_id: Id class — the reference number of the member's Utilization Management Program, as read from the review program lookup.
        source_case_id: Id class — the reference number of the opening of the renewal case being approved, as returned when the renewal was filed or as read from the review case lookup.
        drug_name: Enum class — the drug of the renewal, one of: atorvastatin when the authorization concerns atorvastatin; lisinopril when the authorization
            concerns lisinopril; metformin when the authorization concerns metformin; sertraline
            when the authorization concerns sertraline; levothyroxine when the authorization
            concerns levothyroxine; sumatriptan when the authorization concerns sumatriptan;
            oxycodone-acetaminophen when the authorization concerns oxycodone-acetaminophen;
            insulin glargine-yfgn when the authorization concerns insulin glargine-yfgn; Lantus
            when the authorization concerns Lantus; Eliquis when the authorization concerns
            Eliquis; Xarelto when the authorization concerns Xarelto; Jardiance when the
            authorization concerns Jardiance; Ozempic when the authorization concerns Ozempic;
            Mounjaro when the authorization concerns Mounjaro; Wegovy when the authorization
            concerns Wegovy; Zepbound when the authorization concerns Zepbound; Trelegy Ellipta
            when the authorization concerns Trelegy Ellipta; Breztri Aerosphere when the
            authorization concerns Breztri Aerosphere; Nurtec ODT when the authorization
            concerns Nurtec ODT; Ubrelvy when the authorization concerns Ubrelvy; Humira when
            the authorization concerns Humira; adalimumab-adaz when the authorization concerns
            adalimumab-adaz; Dupixent when the authorization concerns Dupixent; Skyrizi when the
            authorization concerns Skyrizi; Rinvoq when the authorization concerns Rinvoq;
            Enbrel when the authorization concerns Enbrel; Biktarvy when the authorization
            concerns Biktarvy; Ibrance when the authorization concerns Ibrance.
        approved_quantity_per_30: Fixed-format class — the approved quantity of the drug per rolling 30 days, in decimal units, up to 3 decimals (rounded to 3 decimal places).
        effective_date: Fixed-format class — the first day the renewed authorization is in force, written YYYY-MM-DD.
        expiration_date: Fixed-format class — the last day the renewed authorization is in force, written YYYY-MM-DD.

    Returns:
        A dictionary receipt with: decision_id (string, the reference number of the approval decision
        on the renewal case), authorization_id (string, the reference number of the renewed
        authorization), drug_name (string), approved_quantity_per_30 (number, up to 3 decimals),
        effective_date and expiration_date (strings, YYYY-MM-DD) and status (string, "renewed" when the
        case was approved and the authorization put in force).
    """
    qty = round(float(approved_quantity_per_30), 3)
    did = ctx.make_id("rvd_", customer_id, review_program_id, source_case_id, drug_name, qty,
                      effective_date, expiration_date, "renewal")
    aid = ctx.make_id("rva_", customer_id, review_program_id, source_case_id, drug_name, qty,
                      effective_date, expiration_date, "renewal")
    ctx.create("review_cases", did, review_case_id=did, review_program_id=review_program_id,
               customer_id=customer_id, event_type="review_case_approved", source_case_id=source_case_id,
               drug_name=drug_name, review_type="quantity_limit_exception", is_renewal=True,
               requested_quantity_per_30=qty, decision_reason="criteria_met", event_at=ctx.now())
    ctx.create("review_authorizations", aid, review_authorization_id=aid,
               review_program_id=review_program_id, customer_id=customer_id,
               event_type="review_auth_granted", source_case_id=source_case_id,
               source_authorization_id="", drug_name=drug_name, authorization_type="quantity_limit",
               auth_basis="clinical_review", approved_quantity_per_30=qty,
               effective_date=effective_date, expiration_date=expiration_date,
               termination_reason="not_applicable")
    return str({"decision_id": did, "authorization_id": aid, "drug_name": drug_name,
                "approved_quantity_per_30": qty, "effective_date": effective_date,
                "expiration_date": expiration_date, "status": "renewed"})


@tool(owner="agent", rw="write")
def grant_overturn_authorization_6da113c2(ctx: ToolContext, customer_id: str, review_program_id: str,
                                          source_case_id: str, drug_name: str,
                                          approved_quantity_per_30: float, effective_date: str,
                                          expiration_date: str) -> str:
    """Put in force the quantity limit authorization owed after an appeal overturned the denial of a
    member's quantity limit exception request. One call records one new quantity limit authorization
    for the drug that came about through the appeal overturn, linked to the opening of the denied
    case, with the quantity per rolling 30 days it covers and its first and last days in force; the
    denied case itself keeps its decision. Afterwards the member's authorizations list it; the
    effectuation is complete when the receipt shows status "in_force".

    Args:
        customer_id: Id class — the customer reference number of the member, as read from the customer profile lookup.
        review_program_id: Id class — the reference number of the member's Utilization Management Program, as read from the review program lookup.
        source_case_id: Id class — the reference number of the opening of the denied case the appeal overturned, as named on the appeal and read from the appeal or review case lookup.
        drug_name: Enum class — the drug the authorization covers, one of: atorvastatin when the authorization concerns atorvastatin; lisinopril when the authorization
            concerns lisinopril; metformin when the authorization concerns metformin; sertraline
            when the authorization concerns sertraline; levothyroxine when the authorization
            concerns levothyroxine; sumatriptan when the authorization concerns sumatriptan;
            oxycodone-acetaminophen when the authorization concerns oxycodone-acetaminophen;
            insulin glargine-yfgn when the authorization concerns insulin glargine-yfgn; Lantus
            when the authorization concerns Lantus; Eliquis when the authorization concerns
            Eliquis; Xarelto when the authorization concerns Xarelto; Jardiance when the
            authorization concerns Jardiance; Ozempic when the authorization concerns Ozempic;
            Mounjaro when the authorization concerns Mounjaro; Wegovy when the authorization
            concerns Wegovy; Zepbound when the authorization concerns Zepbound; Trelegy Ellipta
            when the authorization concerns Trelegy Ellipta; Breztri Aerosphere when the
            authorization concerns Breztri Aerosphere; Nurtec ODT when the authorization
            concerns Nurtec ODT; Ubrelvy when the authorization concerns Ubrelvy; Humira when
            the authorization concerns Humira; adalimumab-adaz when the authorization concerns
            adalimumab-adaz; Dupixent when the authorization concerns Dupixent; Skyrizi when the
            authorization concerns Skyrizi; Rinvoq when the authorization concerns Rinvoq;
            Enbrel when the authorization concerns Enbrel; Biktarvy when the authorization
            concerns Biktarvy; Ibrance when the authorization concerns Ibrance.
        approved_quantity_per_30: Fixed-format class — the quantity of the drug per rolling 30 days the authorization covers, in decimal units, up to 3 decimals (rounded to 3 decimal places).
        effective_date: Fixed-format class — the first day the authorization is in force, written YYYY-MM-DD.
        expiration_date: Fixed-format class — the last day the authorization is in force, written YYYY-MM-DD.

    Returns:
        A dictionary receipt with: authorization_id (string, the reference number of the new
        authorization), drug_name (string), auth_basis (string, always "appeal_overturn"),
        approved_quantity_per_30 (number, up to 3 decimals), effective_date and expiration_date
        (strings, YYYY-MM-DD) and status (string, "in_force" when the authorization was recorded).
    """
    qty = round(float(approved_quantity_per_30), 3)
    aid = ctx.make_id("rva_", customer_id, review_program_id, source_case_id, drug_name, qty,
                      effective_date, expiration_date, "overturn")
    ctx.create("review_authorizations", aid, review_authorization_id=aid,
               review_program_id=review_program_id, customer_id=customer_id,
               event_type="review_auth_granted", source_case_id=source_case_id,
               source_authorization_id="", drug_name=drug_name, authorization_type="quantity_limit",
               auth_basis="appeal_overturn", approved_quantity_per_30=qty,
               effective_date=effective_date, expiration_date=expiration_date,
               termination_reason="not_applicable")
    return str({"authorization_id": aid, "drug_name": drug_name, "auth_basis": "appeal_overturn",
                "approved_quantity_per_30": qty, "effective_date": effective_date,
                "expiration_date": expiration_date, "status": "in_force"})

"""Hidden task tools for retail_claims_and_reimbursements (Northbridge Rx retail pharmacy network benefit).

Each tool makes one atomic write on the retail benefit's records with the values the caller passes.
No tool checks a business precondition, computes a policy amount or refuses on policy grounds.
"""


from erlbench import ToolContext, tool


class _Calendar:
    """Pure calendar arithmetic on YYYY-MM-DD strings (no clock access)."""

    @staticmethod
    def plus_days(stamp: str, days: int) -> str:
        y, m, d = (int(p) for p in str(stamp)[:10].split("-"))
        d += days
        while True:
            leap = y % 4 == 0 and (y % 100 != 0 or y % 400 == 0)
            dim = [31, 29 if leap else 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31][m - 1]
            if d <= dim:
                break
            d -= dim
            m += 1
            if m > 12:
                m, y = 1, y + 1
        return f"{y:04d}-{m:02d}-{d:02d}"


@tool(owner="agent", rw="write")
def approve_paper_claim_1f52e397(ctx: ToolContext, source_reimbursement_id: str, allowed_amount: float,
                                 deductible_amount: float, member_cost_share: float,
                                 reimbursement_amount: float) -> str:
    """Record the approval decision on one paper claim (direct member reimbursement) that a member
    filed for a prescription they paid for themselves. The approval is recorded today against the
    submission named, with the submission's date of service, drug, strength, days supply, pharmacy
    and formulary tier carried onto the decision, together with the allowed amount, the deductible
    portion, the member cost share and the reimbursement amount given here, and decision reason
    approved_network_rate. The reimbursement amount is added to the reimbursement owed to the member
    on their retail benefit, where it stays until it is paid. On success the submission shows an
    approval, and the member can be told the approved amount.

    Args:
        source_reimbursement_id: Id class — the reference number of the paper-claim submission being decided, read from the member's paper-claim records (the submission row, which has no source reference of its own).
        allowed_amount: Fixed-format class — the allowed amount used to price the claim, in USD, 2 decimal places, rounded half up to the cent.
        deductible_amount: Fixed-format class — the portion of the member cost share applied to the plan deductible, in USD, 2 decimal places; 0.00 when none.
        member_cost_share: Fixed-format class — the member cost share the plan applies to this claim, in USD, 2 decimal places; 0.00 when none.
        reimbursement_amount: Fixed-format class — the amount approved for reimbursement to the member, in USD, 2 decimal places.

    Returns:
        A dictionary rendered as text with: status ("approved" when the decision was recorded);
        decision_id (string, the reference number of the new approval record); source_reimbursement_id
        (string, the submission decided); reimbursement_amount (number, USD to 2 decimal places, the
        amount approved); reimbursement_balance (number, USD to 2 decimal places, the total approved
        and not yet paid on the retail benefit including this approval).
    """
    src_rows = ctx.find("retail_reimbursements", retail_reimbursement_id=source_reimbursement_id)
    src = src_rows[0] if src_rows else {}
    benefit_id = src.get("retail_benefit_id", "")
    amount = round(float(reimbursement_amount), 2)
    rid = ctx.make_id("rrm_", source_reimbursement_id, allowed_amount, deductible_amount,
                      member_cost_share, reimbursement_amount)
    ctx.create("retail_reimbursements", rid, retail_reimbursement_id=rid, retail_benefit_id=benefit_id,
               customer_id=src.get("customer_id", ""), event_type="retail_dmr_approved",
               source_reimbursement_id=source_reimbursement_id, received_date=ctx.now()[:10],
               date_of_service=src.get("date_of_service", ""), pharmacy_npi=src.get("pharmacy_npi", ""),
               pharmacy_network_status=src.get("pharmacy_network_status", ""),
               foreign_purchase=src.get("foreign_purchase", False), drug_name=src.get("drug_name", ""),
               drug_strength=src.get("drug_strength", ""), days_supply=src.get("days_supply", 0),
               formulary_tier=src.get("formulary_tier", "not_applicable"),
               submitted_amount=src.get("submitted_amount", 0.0),
               allowed_amount=round(float(allowed_amount), 2),
               deductible_amount=round(float(deductible_amount), 2),
               member_cost_share=round(float(member_cost_share), 2),
               reimbursement_amount=amount, decision_reason="approved_network_rate",
               payment_method="not_applicable")
    balance = 0.0
    benefits = ctx.find("retail_benefits", retail_benefit_id=benefit_id) if benefit_id else []
    if benefits:
        balance = round(float(benefits[0].get("reimbursement_balance") or 0) + amount, 2)
        ctx.update("retail_benefits", benefit_id, reimbursement_balance=balance)
    return str({"status": "approved", "decision_id": rid, "source_reimbursement_id": source_reimbursement_id,
                "reimbursement_amount": amount, "reimbursement_balance": balance})


@tool(owner="agent", rw="write")
def grant_review_bridge_supply_635c815d(ctx: ToolContext, retail_benefit_id: str, rx_number: str,
                                         days_supply_allowed: int) -> str:
    """Grant an emergency-supply override on a member's retail pharmacy benefit for one prescription
    whose drug is waiting on a coverage review decision, so that a network pharmacy can dispense a
    bridge supply of that prescription while the review is still undecided. The override is recorded today
    against the prescription number given, for the drug of the member's paid claims on that
    prescription, allows the number of days given, and can be used by the pharmacy through the
    seventh calendar day from today. On success the member can fill the bridge supply at a
    network pharmacy.

    Args:
        retail_benefit_id: Id class — the reference number of the member's retail pharmacy network benefit, read from the member's retail benefit record.
        rx_number: Verbatim class — the prescription number exactly as it appears on the member's paid claim records for the drug, copied character for character, preserving the original wording, digits and punctuation, with no translation, normalisation, summarisation, addition or deletion (verbatim).
        days_supply_allowed: Fixed-format class — the bridge supply the override permits, as a whole number of days (integer days).

    Returns:
        A dictionary rendered as text with: status ("granted" when the override was recorded);
        override_id (string, the reference number of the override); override_type ("emergency_supply");
        drug_name (string, the drug the override applies to); rx_number (string); days_supply_allowed
        (integer days); valid_through_date (string, YYYY-MM-DD, the last day a pharmacy may use it).
    """
    claims = ctx.find("retail_claims", retail_benefit_id=retail_benefit_id, rx_number=rx_number)
    drug = claims[0].get("drug_name", "") if claims else ""
    benefits = ctx.find("retail_benefits", retail_benefit_id=retail_benefit_id)
    customer = benefits[0].get("customer_id", "") if benefits else ""
    today = ctx.now()[:10]
    valid = _Calendar.plus_days(today, 7)
    rid = ctx.make_id("rov_", "emergency_supply", retail_benefit_id, rx_number, days_supply_allowed)
    ctx.create("retail_overrides", rid, retail_override_id=rid, retail_benefit_id=retail_benefit_id,
               customer_id=customer, event_type="retail_override_granted", override_type="emergency_supply",
               drug_name=drug, rx_number=rx_number, granted_date=today, valid_through_date=valid,
               days_supply_allowed=int(days_supply_allowed), departure_date="", police_report_number="")
    return str({"status": "granted", "override_id": rid, "override_type": "emergency_supply",
                "drug_name": drug, "rx_number": rx_number, "days_supply_allowed": int(days_supply_allowed),
                "valid_through_date": valid})


@tool(owner="user", rw="write")
def request_vacation_supply_35815dad(ctx: ToolContext, retail_benefit_id: str, rx_number: str,
                                      departure_date: str, days_supply_allowed: int) -> str:
    """The member records their own vacation-supply request on their retail pharmacy benefit, which
    is entered as a vacation-supply override for one prescription so that a network pharmacy can
    fill it early for the member's trip. The override is recorded today against the
    prescription number given, for the drug of the member's paid claims on that prescription, with
    the departure date the member gives and the number of days given, and can be used by the
    pharmacy through the seventh calendar day from today. On success the member can pick up the
    vacation supply at a network pharmacy.

    Args:
        retail_benefit_id: Id class — the reference number of the member's retail pharmacy network benefit, as the agent reads it from the member's retail benefit record and gives it to the member.
        rx_number: Verbatim class — the prescription number exactly as it appears on the member's paid claim records for the drug, as the agent gives it to the member, copied character for character, preserving the original wording, digits and punctuation, with no translation, normalisation, summarisation, addition or deletion (verbatim).
        departure_date: Fixed-format class — the date the member leaves on the trip, as the member states it, written YYYY-MM-DD.
        days_supply_allowed: Fixed-format class — the vacation supply the override permits, as a whole number of days (integer days), as the agent tells the member.

    Returns:
        A dictionary rendered as text with: status ("recorded" when the request was entered);
        override_id (string, the reference number of the override); override_type ("vacation_supply");
        drug_name (string); rx_number (string); departure_date (string, YYYY-MM-DD);
        days_supply_allowed (integer days); valid_through_date (string, YYYY-MM-DD, the last day a
        pharmacy may use it).
    """
    claims = ctx.find("retail_claims", retail_benefit_id=retail_benefit_id, rx_number=rx_number)
    drug = claims[0].get("drug_name", "") if claims else ""
    benefits = ctx.find("retail_benefits", retail_benefit_id=retail_benefit_id)
    customer = benefits[0].get("customer_id", "") if benefits else ""
    today = ctx.now()[:10]
    valid = _Calendar.plus_days(today, 7)
    rid = ctx.make_id("rov_", "vacation_supply", retail_benefit_id, rx_number, departure_date,
                      days_supply_allowed)
    ctx.create("retail_overrides", rid, retail_override_id=rid, retail_benefit_id=retail_benefit_id,
               customer_id=customer, event_type="retail_override_granted", override_type="vacation_supply",
               drug_name=drug, rx_number=rx_number, granted_date=today, valid_through_date=valid,
               days_supply_allowed=int(days_supply_allowed), departure_date=str(departure_date)[:10],
               police_report_number="")
    return str({"status": "recorded", "override_id": rid, "override_type": "vacation_supply",
                "drug_name": drug, "rx_number": rx_number, "departure_date": str(departure_date)[:10],
                "days_supply_allowed": int(days_supply_allowed), "valid_through_date": valid})


@tool(owner="agent", rw="write")
def grant_dose_change_override_e9e89c2d(ctx: ToolContext, retail_benefit_id: str, drug_name: str, rx_number: str,
                                        days_supply_allowed: int) -> str:
    """Grant a dose-change override on a member's retail pharmacy benefit so that a network pharmacy can fill
    the member's new, higher-dose prescription even though the supply of the earlier fill has not yet run out. The override is
    recorded today against the drug and prescription number given, allows the number of days given, and can be used
    by the pharmacy through the seventh calendar day from today. On success the member can fill the new
    prescription at a network pharmacy.

    Args:
        retail_benefit_id: Id class — the reference number of the member's retail pharmacy network benefit, read from the member's retail benefit record.
        drug_name: Enum class — the drug the override applies to, exactly one of: atorvastatin when the override is for atorvastatin; lisinopril when the override is for lisinopril; metformin when the override is for metformin; sertraline when the override is for sertraline; levothyroxine when the override is for levothyroxine; sumatriptan when the override is for sumatriptan; oxycodone-acetaminophen when the override is for oxycodone-acetaminophen; insulin glargine-yfgn when the override is for insulin glargine-yfgn; Lantus when the override is for Lantus; Eliquis when the override is for Eliquis; Xarelto when the override is for Xarelto; Jardiance when the override is for Jardiance; Ozempic when the override is for Ozempic; Mounjaro when the override is for Mounjaro; Wegovy when the override is for Wegovy; Zepbound when the override is for Zepbound; Trelegy Ellipta when the override is for Trelegy Ellipta; Breztri Aerosphere when the override is for Breztri Aerosphere; Nurtec ODT when the override is for Nurtec ODT; Ubrelvy when the override is for Ubrelvy; Humira when the override is for Humira; adalimumab-adaz when the override is for adalimumab-adaz; Dupixent when the override is for Dupixent; Skyrizi when the override is for Skyrizi; Rinvoq when the override is for Rinvoq; Enbrel when the override is for Enbrel; Biktarvy when the override is for Biktarvy; Ibrance when the override is for Ibrance.
        rx_number: Verbatim class — the prescription number the member's network pharmacy holds for the prescription to be filled, as the member reads it from the pharmacy's notice or label, copied character for character, preserving the original wording, digits and punctuation, with no translation, normalisation, summarisation, addition or deletion (verbatim).
        days_supply_allowed: Fixed-format class — the supply the override permits, as a whole number of days (integer days), as worked out for the dose change.

    Returns:
        A dictionary rendered as text with: status ("granted" when the override was recorded);
        override_id (string, the reference number of the override); override_type ("dose_change");
        drug_name (string); rx_number (string); days_supply_allowed (integer days);
        valid_through_date (string, YYYY-MM-DD, the last day a pharmacy may use it).
    """
    benefits = ctx.find("retail_benefits", retail_benefit_id=retail_benefit_id)
    customer = benefits[0].get("customer_id", "") if benefits else ""
    today = ctx.now()[:10]
    valid = _Calendar.plus_days(today, 7)
    rid = ctx.make_id("rov_", "dose_change", retail_benefit_id, drug_name, rx_number, days_supply_allowed)
    ctx.create("retail_overrides", rid, retail_override_id=rid, retail_benefit_id=retail_benefit_id,
               customer_id=customer, event_type="retail_override_granted", override_type="dose_change",
               drug_name=drug_name, rx_number=rx_number, granted_date=today, valid_through_date=valid,
               days_supply_allowed=int(days_supply_allowed), departure_date="", police_report_number="")
    return str({"status": "granted", "override_id": rid, "override_type": "dose_change", "drug_name": drug_name,
                "rx_number": rx_number, "days_supply_allowed": int(days_supply_allowed), "valid_through_date": valid})


@tool(owner="user", rw="write")
def report_lost_stolen_replacement_dcea41b5(ctx: ToolContext, retail_benefit_id: str, drug_name: str, rx_number: str,
                                            days_supply_allowed: int) -> str:
    """The member reports their own lost, stolen or damaged medication on their retail pharmacy benefit, which is
    entered as a lost-or-stolen replacement override so that a network pharmacy can dispense a replacement supply
    early. The override is recorded today against the drug and prescription number given, allows the number of days
    given, and can be used by the pharmacy through the seventh calendar day from today. On success the member
    can pick up the replacement at a network pharmacy.

    Args:
        retail_benefit_id: Id class — the reference number of the member's retail pharmacy network benefit, as the agent reads it from the member's retail benefit record and gives it to the member.
        drug_name: Enum class — the drug the override applies to, exactly one of: atorvastatin when the override is for atorvastatin; lisinopril when the override is for lisinopril; metformin when the override is for metformin; sertraline when the override is for sertraline; levothyroxine when the override is for levothyroxine; sumatriptan when the override is for sumatriptan; oxycodone-acetaminophen when the override is for oxycodone-acetaminophen; insulin glargine-yfgn when the override is for insulin glargine-yfgn; Lantus when the override is for Lantus; Eliquis when the override is for Eliquis; Xarelto when the override is for Xarelto; Jardiance when the override is for Jardiance; Ozempic when the override is for Ozempic; Mounjaro when the override is for Mounjaro; Wegovy when the override is for Wegovy; Zepbound when the override is for Zepbound; Trelegy Ellipta when the override is for Trelegy Ellipta; Breztri Aerosphere when the override is for Breztri Aerosphere; Nurtec ODT when the override is for Nurtec ODT; Ubrelvy when the override is for Ubrelvy; Humira when the override is for Humira; adalimumab-adaz when the override is for adalimumab-adaz; Dupixent when the override is for Dupixent; Skyrizi when the override is for Skyrizi; Rinvoq when the override is for Rinvoq; Enbrel when the override is for Enbrel; Biktarvy when the override is for Biktarvy; Ibrance when the override is for Ibrance.
        rx_number: Verbatim class — the prescription number the member's network pharmacy holds for the prescription to be filled, as the member reads it from the pharmacy's notice or label, copied character for character, preserving the original wording, digits and punctuation, with no translation, normalisation, summarisation, addition or deletion (verbatim).
        days_supply_allowed: Fixed-format class — the supply the override permits, as a whole number of days (integer days), as the agent tells the member.

    Returns:
        A dictionary rendered as text with: status ("recorded" when the override was recorded);
        override_id (string, the reference number of the override); override_type ("lost_stolen");
        drug_name (string); rx_number (string); days_supply_allowed (integer days);
        valid_through_date (string, YYYY-MM-DD, the last day a pharmacy may use it).
    """
    benefits = ctx.find("retail_benefits", retail_benefit_id=retail_benefit_id)
    customer = benefits[0].get("customer_id", "") if benefits else ""
    today = ctx.now()[:10]
    valid = _Calendar.plus_days(today, 7)
    rid = ctx.make_id("rov_", "lost_stolen", retail_benefit_id, drug_name, rx_number, days_supply_allowed)
    ctx.create("retail_overrides", rid, retail_override_id=rid, retail_benefit_id=retail_benefit_id,
               customer_id=customer, event_type="retail_override_granted", override_type="lost_stolen",
               drug_name=drug_name, rx_number=rx_number, granted_date=today, valid_through_date=valid,
               days_supply_allowed=int(days_supply_allowed), departure_date="", police_report_number="")
    return str({"status": "recorded", "override_id": rid, "override_type": "lost_stolen", "drug_name": drug_name,
                "rx_number": rx_number, "days_supply_allowed": int(days_supply_allowed), "valid_through_date": valid})

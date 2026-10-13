"""Hidden task tools for the formulary_exceptions_and_transition difficulty of
env_0047_pharmacy_benefit_manager (Northbridge Rx Formulary Benefit).

Every tool here performs exactly one atomic write on the member's formulary records and
returns a receipt. No tool checks eligibility, prerequisites or the value it is given; the
values are worked out by the agent from the published policy and the member's records.
"""

from erlbench import ToolContext, tool


@tool(owner="agent", rw="write")
def record_specialty_transition_supply_d4f54566(ctx: ToolContext, formulary_assignment_id: str, drug_name: str,
                                                drug_strength: str, transition_basis: str,
                                                days_supply: int) -> str:
    """Record a temporary transition supply of a non-formulary drug dispensed through the specialty
    pharmacy for a member, under the member's formulary assignment. One call adds one transition
    fill to the member's transition-fill history, dated today, with the specialty channel and the
    days supply given; the fill then appears whenever the member's transition fills are looked up,
    and the pharmacy dispenses that many days. A receipt with the new transition fill reference
    number and status "recorded" means the supply was recorded.

    Args:
        formulary_assignment_id: Id class — the reference number of the member's formulary assignment, read from the formulary assignment lookup for the member.
        drug_name: Enum class — the drug dispensed, exactly one of the drug master list names: atorvastatin (the generic statin), lisinopril (the generic ACE inhibitor), metformin (the generic biguanide), sertraline (the generic SSRI), levothyroxine (the generic thyroid hormone), sumatriptan (the generic triptan), oxycodone-acetaminophen (the generic opioid combination), insulin glargine-yfgn (the interchangeable glargine biosimilar), Lantus (the reference glargine brand), Eliquis (the apixaban brand), Xarelto (the rivaroxaban brand), Jardiance (the empagliflozin brand), Ozempic (the semaglutide diabetes pen), Mounjaro (the tirzepatide diabetes pen), Wegovy (the semaglutide weight-management pen), Zepbound (the tirzepatide weight-management pen), Trelegy Ellipta (the triple-therapy inhaler), Breztri Aerosphere (the triple-therapy aerosol inhaler), Nurtec ODT (the rimegepant tablet), Ubrelvy (the ubrogepant tablet), Humira (the reference adalimumab biologic), adalimumab-adaz (the adalimumab biosimilar), Dupixent (the dupilumab biologic), Skyrizi (the risankizumab biologic), Rinvoq (the upadacitinib tablet), Enbrel (the etanercept biologic), Biktarvy (the HIV single-tablet regimen), Ibrance (the palbociclib oncology drug).
        drug_strength: Verbatim class — the strength and dosage form being dispensed, copied character for character from the strength shown on the member's latest specialty fill of the drug, with no change to wording, digits or punctuation (verbatim).
        transition_basis: Enum class — why the member is in a transition window: new_enrollment (the formulary assignment has no formulary change date, so the window runs from the coverage effective date) or formulary_change (the assignment carries a formulary change date because the sponsor moved the member to this formulary).
        days_supply: Fixed-format class — the days supply dispensed, an integer number of days, no decimals; it is stored exactly as given.

    Returns:
        A dictionary receipt: formulary_transition_fill_id (string, the reference number of the new transition fill), drug_name (string, the drug recorded), fill_date (string, YYYY-MM-DD, today's date of service), days_supply (integer, days recorded), dispensing_channel (string, always specialty for this tool) and status (string, "recorded" on success).
    """
    days = int(days_supply)
    rid = ctx.make_id("ftf_sp_", formulary_assignment_id, drug_name, drug_strength, transition_basis, days)
    fill_date = ctx.now()[:10]
    owners = ctx.find("formulary_assignments", formulary_assignment_id=formulary_assignment_id)
    ctx.create("formulary_transition_fills", rid, formulary_transition_fill_id=rid,
               formulary_assignment_id=formulary_assignment_id,
               customer_id=owners[0].get("customer_id", "") if owners else "",
               event_type="formulary_transition_fill", drug_name=drug_name, drug_strength=drug_strength,
               fill_date=fill_date, days_supply=days, transition_basis=transition_basis,
               dispensing_channel="specialty")
    return str({"formulary_transition_fill_id": rid, "drug_name": drug_name, "fill_date": fill_date,
                "days_supply": days, "dispensing_channel": "specialty", "status": "recorded"})


@tool(owner="agent", rw="write")
def record_retail_transition_supply_5b1515b2(ctx: ToolContext, formulary_assignment_id: str, drug_name: str,
                                             drug_strength: str, transition_basis: str,
                                             days_supply: int) -> str:
    """Record a temporary transition supply of a non-formulary drug dispensed at a network retail
    pharmacy for a member, under the member's formulary assignment. One call adds one transition
    fill to the member's transition-fill history, dated today, with the retail channel and the days
    supply given; the member's pharmacy can then dispense that many days and the fill appears whenever
    the member's transition fills are looked up. A receipt with the new transition fill reference
    number and status "recorded" means the supply was recorded.

    Args:
        formulary_assignment_id: Id class — the reference number of the member's formulary assignment, read from the formulary assignment lookup for the member.
        drug_name: Enum class — the drug dispensed, exactly one of the drug master list names: atorvastatin (the generic statin), lisinopril (the generic ACE inhibitor), metformin (the generic biguanide), sertraline (the generic SSRI), levothyroxine (the generic thyroid hormone), sumatriptan (the generic triptan), oxycodone-acetaminophen (the generic opioid combination), insulin glargine-yfgn (the interchangeable glargine biosimilar), Lantus (the reference glargine brand), Eliquis (the apixaban brand), Xarelto (the rivaroxaban brand), Jardiance (the empagliflozin brand), Ozempic (the semaglutide diabetes pen), Mounjaro (the tirzepatide diabetes pen), Wegovy (the semaglutide weight-management pen), Zepbound (the tirzepatide weight-management pen), Trelegy Ellipta (the triple-therapy inhaler), Breztri Aerosphere (the triple-therapy aerosol inhaler), Nurtec ODT (the rimegepant tablet), Ubrelvy (the ubrogepant tablet), Humira (the reference adalimumab biologic), adalimumab-adaz (the adalimumab biosimilar), Dupixent (the dupilumab biologic), Skyrizi (the risankizumab biologic), Rinvoq (the upadacitinib tablet), Enbrel (the etanercept biologic), Biktarvy (the HIV single-tablet regimen), Ibrance (the palbociclib oncology drug).
        drug_strength: Verbatim class — the strength and dosage form being dispensed, copied character for character from the strength shown on the member's latest paid retail fill of the drug, with no change to wording, digits or punctuation (verbatim).
        transition_basis: Enum class — why the member is in a transition window: new_enrollment (the formulary assignment has no formulary change date, so the window runs from the coverage effective date) or formulary_change (the assignment carries a formulary change date because the sponsor moved the member to this formulary).
        days_supply: Fixed-format class — the days supply dispensed, an integer number of days, no decimals; it is stored exactly as given.

    Returns:
        A dictionary receipt: formulary_transition_fill_id (string, the reference number of the new transition fill), drug_name (string, the drug recorded), fill_date (string, YYYY-MM-DD, today's date of service), days_supply (integer, days recorded), dispensing_channel (string, always retail for this tool) and status (string, "recorded" on success).
    """
    days = int(days_supply)
    rid = ctx.make_id("ftf_rt_", formulary_assignment_id, drug_name, drug_strength, transition_basis, days)
    fill_date = ctx.now()[:10]
    owners = ctx.find("formulary_assignments", formulary_assignment_id=formulary_assignment_id)
    ctx.create("formulary_transition_fills", rid, formulary_transition_fill_id=rid,
               formulary_assignment_id=formulary_assignment_id,
               customer_id=owners[0].get("customer_id", "") if owners else "",
               event_type="formulary_transition_fill", drug_name=drug_name, drug_strength=drug_strength,
               fill_date=fill_date, days_supply=days, transition_basis=transition_basis,
               dispensing_channel="retail")
    return str({"formulary_transition_fill_id": rid, "drug_name": drug_name, "fill_date": fill_date,
                "days_supply": days, "dispensing_channel": "retail", "status": "recorded"})


@tool(owner="agent", rw="write")
def record_home_delivery_transition_supply_6840b972(ctx: ToolContext, formulary_assignment_id: str,
                                                    drug_name: str, drug_strength: str,
                                                    transition_basis: str, days_supply: int) -> str:
    """Record a temporary transition supply of a non-formulary drug shipped by the home delivery
    pharmacy for a member, under the member's formulary assignment. One call adds one transition
    fill to the member's transition-fill history, dated today, with the home delivery channel and the
    days supply given; the home delivery pharmacy can then ship that many days and the fill appears
    whenever the member's transition fills are looked up. A receipt with the new transition fill
    reference number and status "recorded" means the supply was recorded.

    Args:
        formulary_assignment_id: Id class — the reference number of the member's formulary assignment, read from the formulary assignment lookup for the member.
        drug_name: Enum class — the drug shipped, exactly one of the drug master list names: atorvastatin (the generic statin), lisinopril (the generic ACE inhibitor), metformin (the generic biguanide), sertraline (the generic SSRI), levothyroxine (the generic thyroid hormone), sumatriptan (the generic triptan), oxycodone-acetaminophen (the generic opioid combination), insulin glargine-yfgn (the interchangeable glargine biosimilar), Lantus (the reference glargine brand), Eliquis (the apixaban brand), Xarelto (the rivaroxaban brand), Jardiance (the empagliflozin brand), Ozempic (the semaglutide diabetes pen), Mounjaro (the tirzepatide diabetes pen), Wegovy (the semaglutide weight-management pen), Zepbound (the tirzepatide weight-management pen), Trelegy Ellipta (the triple-therapy inhaler), Breztri Aerosphere (the triple-therapy aerosol inhaler), Nurtec ODT (the rimegepant tablet), Ubrelvy (the ubrogepant tablet), Humira (the reference adalimumab biologic), adalimumab-adaz (the adalimumab biosimilar), Dupixent (the dupilumab biologic), Skyrizi (the risankizumab biologic), Rinvoq (the upadacitinib tablet), Enbrel (the etanercept biologic), Biktarvy (the HIV single-tablet regimen), Ibrance (the palbociclib oncology drug).
        drug_strength: Verbatim class — the strength and dosage form being shipped, copied character for character from the strength on the member's latest prescription for the drug on file at the home delivery pharmacy, with no change to wording, digits or punctuation (verbatim).
        transition_basis: Enum class — why the member is in a transition window: new_enrollment (the formulary assignment has no formulary change date, so the window runs from the coverage effective date) or formulary_change (the assignment carries a formulary change date because the sponsor moved the member to this formulary).
        days_supply: Fixed-format class — the days supply shipped, an integer number of days, no decimals; it is stored exactly as given.

    Returns:
        A dictionary receipt: formulary_transition_fill_id (string, the reference number of the new transition fill), drug_name (string, the drug recorded), fill_date (string, YYYY-MM-DD, today's date of service), days_supply (integer, days recorded), dispensing_channel (string, always home_delivery for this tool) and status (string, "recorded" on success).
    """
    days = int(days_supply)
    rid = ctx.make_id("ftf_hd_", formulary_assignment_id, drug_name, drug_strength, transition_basis, days)
    fill_date = ctx.now()[:10]
    owners = ctx.find("formulary_assignments", formulary_assignment_id=formulary_assignment_id)
    ctx.create("formulary_transition_fills", rid, formulary_transition_fill_id=rid,
               formulary_assignment_id=formulary_assignment_id,
               customer_id=owners[0].get("customer_id", "") if owners else "",
               event_type="formulary_transition_fill", drug_name=drug_name, drug_strength=drug_strength,
               fill_date=fill_date, days_supply=days, transition_basis=transition_basis,
               dispensing_channel="home_delivery")
    return str({"formulary_transition_fill_id": rid, "drug_name": drug_name, "fill_date": fill_date,
                "days_supply": days, "dispensing_channel": "home_delivery", "status": "recorded"})


@tool(owner="user", rw="write")
def submit_member_exception_request_38483004(ctx: ToolContext, formulary_assignment_id: str, customer_id: str,
                                             drug_name: str,
                                             drug_strength: str, exception_type: str, prescriber_npi: str,
                                             review_priority: str) -> str:
    """Submit, as the member, the member's own formulary exception request for one drug under the
    member's formulary assignment. One call opens one new exception case in the member's exception
    history, received now, marked as opened by the member, naming the prescriber who will be asked
    for the supporting statement and carrying the priority given; the case then shows as an open
    request whenever the member's exception history is looked up. A receipt with the new request
    reference number and status "received" means the request was submitted.

    Args:
        formulary_assignment_id: Id class — the reference number of the member's formulary assignment, as read out to the member from the formulary assignment lookup.
        customer_id: Id class — the member's own customer reference number, as read out to the member from the customer profile lookup.
        drug_name: Enum class — the drug the exception is requested for, exactly one of the drug master list names: atorvastatin (the generic statin), lisinopril (the generic ACE inhibitor), metformin (the generic biguanide), sertraline (the generic SSRI), levothyroxine (the generic thyroid hormone), sumatriptan (the generic triptan), oxycodone-acetaminophen (the generic opioid combination), insulin glargine-yfgn (the interchangeable glargine biosimilar), Lantus (the reference glargine brand), Eliquis (the apixaban brand), Xarelto (the rivaroxaban brand), Jardiance (the empagliflozin brand), Ozempic (the semaglutide diabetes pen), Mounjaro (the tirzepatide diabetes pen), Wegovy (the semaglutide weight-management pen), Zepbound (the tirzepatide weight-management pen), Trelegy Ellipta (the triple-therapy inhaler), Breztri Aerosphere (the triple-therapy aerosol inhaler), Nurtec ODT (the rimegepant tablet), Ubrelvy (the ubrogepant tablet), Humira (the reference adalimumab biologic), adalimumab-adaz (the adalimumab biosimilar), Dupixent (the dupilumab biologic), Skyrizi (the risankizumab biologic), Rinvoq (the upadacitinib tablet), Enbrel (the etanercept biologic), Biktarvy (the HIV single-tablet regimen), Ibrance (the palbociclib oncology drug).
        drug_strength: Verbatim class — the strength and dosage form the member is prescribed, copied character for character from the strength on the member's latest prescription for the drug as read out to the member, with no change to wording, digits or punctuation (verbatim).
        exception_type: Enum class — the kind of exception: tier_exception (the drug is on the formulary and the member asks for it at a lower cost-share tier) or non_formulary_exception (the drug is coded non-formulary and the member asks for it to be covered).
        prescriber_npi: Fixed-format class — the National Provider Identifier of the prescriber who will be asked for the supporting statement, 10 digits with no spaces or punctuation.
        review_priority: Enum class — the priority of the request: standard (the request is decided on the standard timeframe) or expedited (the request is decided on the expedited timeframe).

    Returns:
        A dictionary receipt: formulary_exception_id (string, the reference number of the new request), drug_name (string, the drug requested), exception_type (string, the kind of exception), review_priority (string, the priority recorded), requested_by (string, always member for this tool), received_at (string, the moment the request was received, as the system clock shows it) and status (string, "received" on success).
    """
    rid = ctx.make_id("fex_mr_", formulary_assignment_id, customer_id, drug_name, drug_strength, exception_type,
                      prescriber_npi, review_priority)
    received_at = ctx.now()
    ctx.create("formulary_exceptions", rid, formulary_exception_id=rid,
               formulary_assignment_id=formulary_assignment_id, customer_id=customer_id,
               event_type="formulary_exception_requested", source_exception_id="",
               drug_name=drug_name, drug_strength=drug_strength, exception_type=exception_type,
               review_priority=review_priority, requested_by="member", prescriber_npi=prescriber_npi,
               statement_basis="not_applicable", event_at=received_at, decision_reason="not_applicable",
               review_outcome="not_applicable", approved_tier="not_applicable",
               approval_effective_date="", approval_expiration_date="")
    return str({"formulary_exception_id": rid, "drug_name": drug_name, "exception_type": exception_type,
                "review_priority": review_priority, "requested_by": "member", "received_at": received_at,
                "status": "received"})



@tool(owner="agent", rw="write")
def approve_standard_nonformulary_exception_57f550b5(ctx: ToolContext, formulary_assignment_id: str, source_exception_id: str, drug_name: str,
        approved_tier: str, approval_months: int) -> str:
    """Record the approval of one non-formulary exception request of a member, decided on the standard timeframe. One
    call adds one approval decision to the request's case history, dated today, covering the drug at
    the tier given; the approval is effective today and its expiration date is the day before the same
    day-of-month the given number of whole months later (the last day of that month when the day does
    not exist), so the member's claims for the drug are covered at that tier through that date. A
    receipt with the new decision reference number and status "approved" means the approval was recorded.

    Args:
        formulary_assignment_id: Id class — the reference number of the member's formulary assignment, read from the formulary assignment lookup for the member.
        source_exception_id: Id class — the reference number of the original exception request being approved, read from the member's exception history (the request row itself, not its statement row).
        drug_name: Enum class — the drug of the request, exactly one of the drug master list names: atorvastatin (the generic statin), lisinopril (the generic ACE inhibitor), metformin (the generic biguanide), sertraline (the generic SSRI), levothyroxine (the generic thyroid hormone), sumatriptan (the generic triptan), oxycodone-acetaminophen (the generic opioid combination), insulin glargine-yfgn (the interchangeable glargine biosimilar), Lantus (the reference glargine brand), Eliquis (the apixaban brand), Xarelto (the rivaroxaban brand), Jardiance (the empagliflozin brand), Ozempic (the semaglutide diabetes pen), Mounjaro (the tirzepatide diabetes pen), Wegovy (the semaglutide weight-management pen), Zepbound (the tirzepatide weight-management pen), Trelegy Ellipta (the triple-therapy inhaler), Breztri Aerosphere (the triple-therapy aerosol inhaler), Nurtec ODT (the rimegepant tablet), Ubrelvy (the ubrogepant tablet), Humira (the reference adalimumab biologic), adalimumab-adaz (the adalimumab biosimilar), Dupixent (the dupilumab biologic), Skyrizi (the risankizumab biologic), Rinvoq (the upadacitinib tablet), Enbrel (the etanercept biologic), Biktarvy (the HIV single-tablet regimen), Ibrance (the palbociclib oncology drug).
        approved_tier: Enum class — the cost-share tier at which the approved exception covers the drug: 1 (the generic tier), 2 (the preferred brand tier), 3 (the non-preferred brand tier), 4 (the first specialty tier), 5 (the second specialty tier), not_applicable (only for a record that carries no approval; never correct on an approval).
        approval_months: Fixed-format class — the length of the approval in whole calendar months, an integer number of months, no decimals; the expiration date is derived from it as described above.

    Returns:
        A dictionary receipt: formulary_exception_id (string, the reference number of the approval decision), source_exception_id (string, the request approved), drug_name (string), approved_tier (string, the tier recorded), approval_effective_date (string, YYYY-MM-DD, today), approval_expiration_date (string, YYYY-MM-DD, the last day the approval is in force) and status (string, "approved" on success).
    """
    def _ordinal(yy, mm, dd):
        yy -= mm <= 2
        era = yy // 400
        yoe = yy - era * 400
        doy = (153 * (mm + (-3 if mm > 2 else 9)) + 2) // 5 + dd - 1
        return era * 146097 + yoe * 365 + yoe // 4 - yoe // 100 + doy

    def _civil(n):
        era = n // 146097
        doe = n - era * 146097
        yoe = (doe - doe // 1460 + doe // 36524 - doe // 146096) // 365
        doy = doe - (365 * yoe + yoe // 4 - yoe // 100)
        mp = (5 * doy + 2) // 153
        dd = doy - (153 * mp + 2) // 5 + 1
        mm = mp + (3 if mp < 10 else -9)
        return "%04d-%02d-%02d" % (yoe + era * 400 + (mm <= 2), mm, dd)

    months = int(approval_months)
    today = ctx.now()[:10]
    y, m, d = (int(x) for x in today.split("-"))
    total = (m - 1) + months
    y2, m2 = y + total // 12, total % 12 + 1
    month_len = _ordinal(y2 + (m2 == 12), m2 % 12 + 1, 1) - _ordinal(y2, m2, 1)
    expiration = _civil(_ordinal(y2, m2, min(d, month_len)) - 1)
    rid = ctx.make_id("fex_nfa_", formulary_assignment_id, source_exception_id, drug_name, approved_tier, months)
    req = ctx.find("formulary_exceptions", formulary_exception_id=source_exception_id)
    owners = ctx.find("formulary_assignments", formulary_assignment_id=formulary_assignment_id)
    ctx.create("formulary_exceptions", rid, formulary_exception_id=rid,
               formulary_assignment_id=formulary_assignment_id,
               customer_id=owners[0].get("customer_id", "") if owners else "",
               event_type="formulary_exception_approved", source_exception_id=source_exception_id,
               drug_name=drug_name, drug_strength=req[0].get("drug_strength", "") if req else "",
               exception_type="non_formulary_exception", review_priority="standard", requested_by="prescriber",
               prescriber_npi=req[0].get("prescriber_npi", "") if req else "", statement_basis="not_applicable",
               event_at=ctx.now(), decision_reason="criteria_met", review_outcome="not_applicable",
               approved_tier=approved_tier, approval_effective_date=today, approval_expiration_date=expiration)
    return str({"formulary_exception_id": rid, "source_exception_id": source_exception_id, "drug_name": drug_name,
                "approved_tier": approved_tier, "approval_effective_date": today,
                "approval_expiration_date": expiration, "status": "approved"})


@tool(owner="agent", rw="write")
def approve_tier_exception_8a527f11(ctx: ToolContext, formulary_assignment_id: str, source_exception_id: str, drug_name: str,
        approved_tier: str, approval_months: int) -> str:
    """Record the approval of one tier exception request of a member, decided on the standard timeframe. One
    call adds one approval decision to the request's case history, dated today, covering the drug at
    the tier given; the approval is effective today and its expiration date is the day before the same
    day-of-month the given number of whole months later (the last day of that month when the day does
    not exist), so the member's claims for the drug are covered at that tier through that date. A
    receipt with the new decision reference number and status "approved" means the approval was recorded.

    Args:
        formulary_assignment_id: Id class — the reference number of the member's formulary assignment, read from the formulary assignment lookup for the member.
        source_exception_id: Id class — the reference number of the original exception request being approved, read from the member's exception history (the request row itself, not its statement row).
        drug_name: Enum class — the drug of the request, exactly one of the drug master list names: atorvastatin (the generic statin), lisinopril (the generic ACE inhibitor), metformin (the generic biguanide), sertraline (the generic SSRI), levothyroxine (the generic thyroid hormone), sumatriptan (the generic triptan), oxycodone-acetaminophen (the generic opioid combination), insulin glargine-yfgn (the interchangeable glargine biosimilar), Lantus (the reference glargine brand), Eliquis (the apixaban brand), Xarelto (the rivaroxaban brand), Jardiance (the empagliflozin brand), Ozempic (the semaglutide diabetes pen), Mounjaro (the tirzepatide diabetes pen), Wegovy (the semaglutide weight-management pen), Zepbound (the tirzepatide weight-management pen), Trelegy Ellipta (the triple-therapy inhaler), Breztri Aerosphere (the triple-therapy aerosol inhaler), Nurtec ODT (the rimegepant tablet), Ubrelvy (the ubrogepant tablet), Humira (the reference adalimumab biologic), adalimumab-adaz (the adalimumab biosimilar), Dupixent (the dupilumab biologic), Skyrizi (the risankizumab biologic), Rinvoq (the upadacitinib tablet), Enbrel (the etanercept biologic), Biktarvy (the HIV single-tablet regimen), Ibrance (the palbociclib oncology drug).
        approved_tier: Enum class — the cost-share tier at which the approved exception covers the drug: 1 (the generic tier), 2 (the preferred brand tier), 3 (the non-preferred brand tier), 4 (the first specialty tier), 5 (the second specialty tier), not_applicable (only for a record that carries no approval; never correct on an approval).
        approval_months: Fixed-format class — the length of the approval in whole calendar months, an integer number of months, no decimals; the expiration date is derived from it as described above.

    Returns:
        A dictionary receipt: formulary_exception_id (string, the reference number of the approval decision), source_exception_id (string, the request approved), drug_name (string), approved_tier (string, the tier recorded), approval_effective_date (string, YYYY-MM-DD, today), approval_expiration_date (string, YYYY-MM-DD, the last day the approval is in force) and status (string, "approved" on success).
    """
    def _ordinal(yy, mm, dd):
        yy -= mm <= 2
        era = yy // 400
        yoe = yy - era * 400
        doy = (153 * (mm + (-3 if mm > 2 else 9)) + 2) // 5 + dd - 1
        return era * 146097 + yoe * 365 + yoe // 4 - yoe // 100 + doy

    def _civil(n):
        era = n // 146097
        doe = n - era * 146097
        yoe = (doe - doe // 1460 + doe // 36524 - doe // 146096) // 365
        doy = doe - (365 * yoe + yoe // 4 - yoe // 100)
        mp = (5 * doy + 2) // 153
        dd = doy - (153 * mp + 2) // 5 + 1
        mm = mp + (3 if mp < 10 else -9)
        return "%04d-%02d-%02d" % (yoe + era * 400 + (mm <= 2), mm, dd)

    months = int(approval_months)
    today = ctx.now()[:10]
    y, m, d = (int(x) for x in today.split("-"))
    total = (m - 1) + months
    y2, m2 = y + total // 12, total % 12 + 1
    month_len = _ordinal(y2 + (m2 == 12), m2 % 12 + 1, 1) - _ordinal(y2, m2, 1)
    expiration = _civil(_ordinal(y2, m2, min(d, month_len)) - 1)
    rid = ctx.make_id("fex_tia_", formulary_assignment_id, source_exception_id, drug_name, approved_tier, months)
    req = ctx.find("formulary_exceptions", formulary_exception_id=source_exception_id)
    owners = ctx.find("formulary_assignments", formulary_assignment_id=formulary_assignment_id)
    ctx.create("formulary_exceptions", rid, formulary_exception_id=rid,
               formulary_assignment_id=formulary_assignment_id,
               customer_id=owners[0].get("customer_id", "") if owners else "",
               event_type="formulary_exception_approved", source_exception_id=source_exception_id,
               drug_name=drug_name, drug_strength=req[0].get("drug_strength", "") if req else "",
               exception_type="tier_exception", review_priority="standard", requested_by="prescriber",
               prescriber_npi=req[0].get("prescriber_npi", "") if req else "", statement_basis="not_applicable",
               event_at=ctx.now(), decision_reason="criteria_met", review_outcome="not_applicable",
               approved_tier=approved_tier, approval_effective_date=today, approval_expiration_date=expiration)
    return str({"formulary_exception_id": rid, "source_exception_id": source_exception_id, "drug_name": drug_name,
                "approved_tier": approved_tier, "approval_effective_date": today,
                "approval_expiration_date": expiration, "status": "approved"})


@tool(owner="agent", rw="write")
def approve_expedited_exception_8cc2ac55(ctx: ToolContext, formulary_assignment_id: str, source_exception_id: str,
                                         drug_name: str, exception_type: str, approved_tier: str,
                                         approval_days: int) -> str:
    """Record the approval of one exception request of a member decided on the expedited timeframe. One
    call adds one expedited approval decision to the request's case history, dated today, covering the
    drug at the tier given; the approval is effective today and runs the given number of calendar days
    with today as day 1, so its expiration date is today plus that number of days less one, and the
    member's claims for the drug are covered at that tier through that date. A receipt with the new
    decision reference number and status "approved" means the approval was recorded.

    Args:
        formulary_assignment_id: Id class — the reference number of the member's formulary assignment, read from the formulary assignment lookup for the member.
        source_exception_id: Id class — the reference number of the original exception request being approved, read from the member's exception history (the request row itself, not its statement row).
        drug_name: Enum class — the drug of the request, exactly one of the drug master list names: atorvastatin (the generic statin), lisinopril (the generic ACE inhibitor), metformin (the generic biguanide), sertraline (the generic SSRI), levothyroxine (the generic thyroid hormone), sumatriptan (the generic triptan), oxycodone-acetaminophen (the generic opioid combination), insulin glargine-yfgn (the interchangeable glargine biosimilar), Lantus (the reference glargine brand), Eliquis (the apixaban brand), Xarelto (the rivaroxaban brand), Jardiance (the empagliflozin brand), Ozempic (the semaglutide diabetes pen), Mounjaro (the tirzepatide diabetes pen), Wegovy (the semaglutide weight-management pen), Zepbound (the tirzepatide weight-management pen), Trelegy Ellipta (the triple-therapy inhaler), Breztri Aerosphere (the triple-therapy aerosol inhaler), Nurtec ODT (the rimegepant tablet), Ubrelvy (the ubrogepant tablet), Humira (the reference adalimumab biologic), adalimumab-adaz (the adalimumab biosimilar), Dupixent (the dupilumab biologic), Skyrizi (the risankizumab biologic), Rinvoq (the upadacitinib tablet), Enbrel (the etanercept biologic), Biktarvy (the HIV single-tablet regimen), Ibrance (the palbociclib oncology drug).
        exception_type: Enum class — the kind of exception approved: tier_exception (a formulary drug covered at a lower cost-share tier) or non_formulary_exception (a drug coded non-formulary covered by exception).
        approved_tier: Enum class — the cost-share tier at which the approved exception covers the drug: 1 (the generic tier), 2 (the preferred brand tier), 3 (the non-preferred brand tier), 4 (the first specialty tier), 5 (the second specialty tier), not_applicable (only for a record that carries no approval; never correct on an approval).
        approval_days: Fixed-format class — the length of the approval in calendar days with today counted as day 1, an integer number of days, no decimals.

    Returns:
        A dictionary receipt: formulary_exception_id (string, the reference number of the approval decision), source_exception_id (string, the request approved), drug_name (string), approved_tier (string, the tier recorded), approval_effective_date (string, YYYY-MM-DD, today), approval_expiration_date (string, YYYY-MM-DD, the last day the approval is in force) and status (string, "approved" on success).
    """
    def _ordinal(yy, mm, dd):
        yy -= mm <= 2
        era = yy // 400
        yoe = yy - era * 400
        doy = (153 * (mm + (-3 if mm > 2 else 9)) + 2) // 5 + dd - 1
        return era * 146097 + yoe * 365 + yoe // 4 - yoe // 100 + doy

    def _civil(n):
        era = n // 146097
        doe = n - era * 146097
        yoe = (doe - doe // 1460 + doe // 36524 - doe // 146096) // 365
        doy = doe - (365 * yoe + yoe // 4 - yoe // 100)
        mp = (5 * doy + 2) // 153
        dd = doy - (153 * mp + 2) // 5 + 1
        mm = mp + (3 if mp < 10 else -9)
        return "%04d-%02d-%02d" % (yoe + era * 400 + (mm <= 2), mm, dd)

    days = int(approval_days)
    today = ctx.now()[:10]
    expiration = _civil(_ordinal(*(int(x) for x in today.split("-"))) + days - 1)
    rid = ctx.make_id("fex_exa_", formulary_assignment_id, source_exception_id, drug_name, exception_type,
                      approved_tier, days)
    req = ctx.find("formulary_exceptions", formulary_exception_id=source_exception_id)
    owners = ctx.find("formulary_assignments", formulary_assignment_id=formulary_assignment_id)
    ctx.create("formulary_exceptions", rid, formulary_exception_id=rid,
               formulary_assignment_id=formulary_assignment_id,
               customer_id=owners[0].get("customer_id", "") if owners else "",
               event_type="formulary_exception_approved", source_exception_id=source_exception_id,
               drug_name=drug_name, drug_strength=req[0].get("drug_strength", "") if req else "",
               exception_type=exception_type, review_priority="expedited", requested_by="prescriber",
               prescriber_npi=req[0].get("prescriber_npi", "") if req else "", statement_basis="not_applicable",
               event_at=ctx.now(), decision_reason="criteria_met", review_outcome="not_applicable",
               approved_tier=approved_tier, approval_effective_date=today, approval_expiration_date=expiration)
    return str({"formulary_exception_id": rid, "source_exception_id": source_exception_id, "drug_name": drug_name,
                "approved_tier": approved_tier, "approval_effective_date": today,
                "approval_expiration_date": expiration, "status": "approved"})


@tool(owner="user", rw="write")
def request_external_exception_review_e71b5dce(ctx: ToolContext, formulary_assignment_id: str, customer_id: str,
                                               source_exception_id: str, drug_name: str,
                                               review_priority: str) -> str:
    """Submit, as the member, the member's own request for an independent external review of a denied
    formulary exception. One call adds one external review request to the denied request's case
    history, received now, marked as asked for by the member and carrying the priority given; the
    review then shows as pending whenever the member's exception history is looked up. A receipt with
    the new review request reference number and status "received" means the request was submitted.

    Args:
        formulary_assignment_id: Id class — the reference number of the member's formulary assignment, as read out to the member from the formulary assignment lookup.
        customer_id: Id class — the member's own customer reference number, as read out to the member from the customer profile lookup.
        source_exception_id: Id class — the reference number of the original exception request whose denial is to be reviewed, as read out to the member from the exception history (the request row itself, not its denial row).
        drug_name: Enum class — the drug of the denied request, exactly one of the drug master list names: atorvastatin (the generic statin), lisinopril (the generic ACE inhibitor), metformin (the generic biguanide), sertraline (the generic SSRI), levothyroxine (the generic thyroid hormone), sumatriptan (the generic triptan), oxycodone-acetaminophen (the generic opioid combination), insulin glargine-yfgn (the interchangeable glargine biosimilar), Lantus (the reference glargine brand), Eliquis (the apixaban brand), Xarelto (the rivaroxaban brand), Jardiance (the empagliflozin brand), Ozempic (the semaglutide diabetes pen), Mounjaro (the tirzepatide diabetes pen), Wegovy (the semaglutide weight-management pen), Zepbound (the tirzepatide weight-management pen), Trelegy Ellipta (the triple-therapy inhaler), Breztri Aerosphere (the triple-therapy aerosol inhaler), Nurtec ODT (the rimegepant tablet), Ubrelvy (the ubrogepant tablet), Humira (the reference adalimumab biologic), adalimumab-adaz (the adalimumab biosimilar), Dupixent (the dupilumab biologic), Skyrizi (the risankizumab biologic), Rinvoq (the upadacitinib tablet), Enbrel (the etanercept biologic), Biktarvy (the HIV single-tablet regimen), Ibrance (the palbociclib oncology drug).
        review_priority: Enum class — the priority of the external review: standard (decided on the reviewer's standard timeframe) or expedited (decided on the reviewer's expedited timeframe).

    Returns:
        A dictionary receipt: formulary_exception_id (string, the reference number of the review request), source_exception_id (string, the denied request under review), drug_name (string), review_priority (string, the priority recorded), requested_by (string, always member for this tool), received_at (string, the moment received, as the system clock shows it) and status (string, "received" on success).
    """
    rid = ctx.make_id("fex_xr_", formulary_assignment_id, customer_id, source_exception_id, drug_name, review_priority)
    received_at = ctx.now()
    req = ctx.find("formulary_exceptions", formulary_exception_id=source_exception_id)
    ctx.create("formulary_exceptions", rid, formulary_exception_id=rid,
               formulary_assignment_id=formulary_assignment_id, customer_id=customer_id,
               event_type="formulary_external_review_requested", source_exception_id=source_exception_id,
               drug_name=drug_name, drug_strength=req[0].get("drug_strength", "") if req else "",
               exception_type=req[0].get("exception_type", "non_formulary_exception") if req else "non_formulary_exception",
               review_priority=review_priority, requested_by="member",
               prescriber_npi=req[0].get("prescriber_npi", "") if req else "",
               statement_basis="not_applicable", event_at=received_at, decision_reason="not_applicable",
               review_outcome="not_applicable", approved_tier="not_applicable",
               approval_effective_date="", approval_expiration_date="")
    return str({"formulary_exception_id": rid, "source_exception_id": source_exception_id, "drug_name": drug_name,
                "review_priority": review_priority, "requested_by": "member", "received_at": received_at,
                "status": "received"})

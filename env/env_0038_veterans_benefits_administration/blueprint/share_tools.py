"""Shared tools for env_0038_veterans_benefits_administration.

Every tool here is a SHARE tool: always present in its owner's tool list.
Contents: one finder per record type (the customers finder doubles as the identity entry),
the identity-verification write, and the transfer-to-representative write.
Business decisions (eligibility, status, timing, deduplication) are never encoded here;
the agent makes them from the knowledge base and the records.
"""

from erlbench import ToolContext, tool


@tool(owner="agent", rw="read")
def find_customers(ctx: ToolContext, customer_id: str = "", sponsor_customer_id: str = "", full_name: str = "",
                   phone_number: str = "", email: str = "", va_file_number: str = "", date_of_birth: str = "") -> str:
    """Find a beneficiary's VA profile and establish whose records this contact is about.

    Search by the beneficiary's reference number when it is known, or by what a caller can naturally state: their
    name, telephone number, email address, VA file number or date of birth. Every criterion is optional; give as many
    as you have. The profile returned shows the beneficiary's role (veteran, surviving spouse or dependent), the
    sponsoring veteran for survivors and dependents, contact details, branch of service, service entry and
    separation dates, character of discharge and any date of death. Survivors and dependents linked to a veteran can
    be found by giving that veteran's reference number as the sponsor. Finding a profile does not verify the caller's
    identity.

    Args:
        customer_id: The beneficiary's reference number, if already known; leave "" otherwise.
        sponsor_customer_id: The reference number of the veteran a survivor or dependent is linked to; leave "" otherwise.
        full_name: The caller's full name as they state it; leave "" if not given.
        phone_number: The caller's telephone number, 10 digits; leave "" if not given.
        email: The caller's email address; leave "" if not given.
        va_file_number: The caller's VA file number, 8 or 9 digits; leave "" if not given.
        date_of_birth: The caller's date of birth as YYYY-MM-DD; leave "" if not given.
    """
    match = {k: v for k, v in {"customer_id": customer_id, "sponsor_customer_id": sponsor_customer_id,
                               "full_name": full_name, "phone_number": phone_number, "email": email,
                               "va_file_number": va_file_number, "date_of_birth": date_of_birth}.items() if v}
    if not match:
        return "Error: provide at least one reference number or profile detail to find the beneficiary."
    rows = ctx.fuzzy_find("customers", **match)
    if not rows:
        return f"No beneficiary profile matches {match}."
    if len(rows) > 1 and "sponsor_customer_id" not in match:
        return (f"Error: {len(rows)} profiles match {match}; ask the caller for one more detail "
                "(for example the VA file number or date of birth) to tell them apart.")
    return str(rows if len(rows) > 1 else rows[0])


@tool(owner="agent", rw="read")
def find_identity_verifications(ctx: ToolContext, verification_id: str = "", customer_id: str = "") -> str:
    """Look up the outcome of identity checks recorded for a caller on this contact: whether verification passed and
    when it was last attempted. Give any reference number you hold; every criterion is optional, and with none the
    full list is returned.

    Args:
        verification_id: The reference number of the identity-check record itself; leave "" if not known.
        customer_id: The beneficiary's reference number (the person whose records these are); leave "" if not known.
    """
    match = {k: v for k, v in {"verification_id": verification_id, "customer_id": customer_id}.items() if v}
    rows = ctx.find("identity_verifications", **match)
    return str(rows) if rows else f"No matching records for {match}."

@tool(owner="agent", rw="read")
def find_human_handoffs(ctx: ToolContext, handoff_id: str = "", customer_id: str = "") -> str:
    """Look up transfers to a human representative already recorded for a beneficiary, with the reason given and the
    time of each transfer. Give any reference number you hold; every criterion is optional, and with none the full
    list is returned.

    Args:
        handoff_id: The reference number of the transfer record itself; leave "" if not known.
        customer_id: The beneficiary's reference number (the person whose records these are); leave "" if not known.
    """
    match = {k: v for k, v in {"handoff_id": handoff_id, "customer_id": customer_id}.items() if v}
    rows = ctx.find("human_handoffs", **match)
    return str(rows) if rows else f"No matching records for {match}."

@tool(owner="agent", rw="read")
def find_comp_awards(ctx: ToolContext, award_id: str = "", customer_id: str = "") -> str:
    """Look up a veteran's disability compensation award: the combined rating tier in effect and its effective date,
    the date service connection began, award status (authorized, running, suspended or terminated) and any
    suspension or termination reason, static, permanent-and-total and individual unemployability findings, special
    monthly compensation (k) awards, whether a representative fee agreement is on file, and how payments are
    delivered. Give any reference number you hold; every criterion is optional, and with none the full list is
    returned.

    Args:
        award_id: The reference number of the disability compensation award; leave "" if not known.
        customer_id: The beneficiary's reference number (the person whose records these are); leave "" if not known.
    """
    match = {k: v for k, v in {"award_id": award_id, "customer_id": customer_id}.items() if v}
    rows = ctx.find("comp_awards", **match)
    return str(rows) if rows else f"No matching records for {match}."

@tool(owner="agent", rw="read")
def find_comp_payments(ctx: ToolContext, payment_id: str = "", award_id: str = "", customer_id: str = "", source_payment_id: str = "", decision_id: str = "") -> str:
    """Look up disability compensation payments: each monthly payment by entitlement month, retroactive releases with
    the span of months they cover, payments the Treasury returned and their reissues, with the gross amount, any
    debt offset or representative fee withheld, the net amount delivered and the issue date. Give any reference
    number you hold; every criterion is optional, and with none the full list is returned.

    Args:
        payment_id: The reference number of the compensation payment itself; leave "" if not known.
        award_id: The reference number of the disability compensation award; leave "" if not known.
        customer_id: The beneficiary's reference number (the person whose records these are); leave "" if not known.
        source_payment_id: The reference number of the original payment that this entry returns, reissues or was withheld from; leave "" if not known.
        decision_id: The reference number of the rating decision or notice; leave "" if not known.
    """
    match = {k: v for k, v in {"payment_id": payment_id, "award_id": award_id, "customer_id": customer_id, "source_payment_id": source_payment_id, "decision_id": decision_id}.items() if v}
    rows = ctx.find("comp_payments", **match)
    return str(rows) if rows else f"No matching records for {match}."

@tool(owner="agent", rw="read")
def find_comp_decisions(ctx: ToolContext, decision_id: str = "", award_id: str = "", customer_id: str = "", claim_id: str = "", proposal_decision_id: str = "") -> str:
    """Look up rating decisions and due-process notices on a compensation award: the decision and notice dates, the
    outcome, the combined rating before and after, the effective date assigned, the disability and diagnostic code
    addressed, proposed reductions and incarceration adjustments. Give any reference number you hold; every
    criterion is optional, and with none the full list is returned.

    Args:
        decision_id: The reference number of the rating decision or notice; leave "" if not known.
        award_id: The reference number of the disability compensation award; leave "" if not known.
        customer_id: The beneficiary's reference number (the person whose records these are); leave "" if not known.
        claim_id: The reference number of the compensation claim; leave "" if not known.
        proposal_decision_id: The reference number of the proposed-reduction notice that a final reduction carries out; leave "" if not known.
    """
    match = {k: v for k, v in {"decision_id": decision_id, "award_id": award_id, "customer_id": customer_id, "claim_id": claim_id, "proposal_decision_id": proposal_decision_id}.items() if v}
    rows = ctx.find("comp_decisions", **match)
    return str(rows) if rows else f"No matching records for {match}."

@tool(owner="agent", rw="read")
def find_comp_claims(ctx: ToolContext, claim_id: str = "", award_id: str = "", customer_id: str = "", itf_id: str = "", source_claim_id: str = "", related_decision_id: str = "") -> str:
    """Look up compensation submissions: intents to file, claims filed with their type, received date and channel,
    withdrawals, and predetermination hearing requests. Give any reference number you hold; every criterion is
    optional, and with none the full list is returned.

    Args:
        claim_id: The reference number of the compensation claim; leave "" if not known.
        award_id: The reference number of the disability compensation award; leave "" if not known.
        customer_id: The beneficiary's reference number (the person whose records these are); leave "" if not known.
        itf_id: The reference number of the intent to file that protects a claim's date; leave "" if not known.
        source_claim_id: The reference number of the claim that a withdrawal withdraws; leave "" if not known.
        related_decision_id: The reference number of the proposed-reduction notice that a hearing request answers; leave "" if not known.
    """
    match = {k: v for k, v in {"claim_id": claim_id, "award_id": award_id, "customer_id": customer_id, "itf_id": itf_id, "source_claim_id": source_claim_id, "related_decision_id": related_decision_id}.items() if v}
    rows = ctx.find("comp_claims", **match)
    return str(rows) if rows else f"No matching records for {match}."

@tool(owner="agent", rw="read")
def find_comp_dependents(ctx: ToolContext, dependent_event_id: str = "", award_id: str = "", customer_id: str = "", source_dependent_event_id: str = "", claim_id: str = "") -> str:
    """Look up dependents added to or removed from a compensation award: relationship, name and date of birth, the life
    event and its date, the effective date and first month paid at the changed rate, the reason for a removal, how
    it was reported, and whether a removal created an overpayment. Give any reference number you hold; every
    criterion is optional, and with none the full list is returned.

    Args:
        dependent_event_id: The reference number of the dependency action itself; leave "" if not known.
        award_id: The reference number of the disability compensation award; leave "" if not known.
        customer_id: The beneficiary's reference number (the person whose records these are); leave "" if not known.
        source_dependent_event_id: The reference number of the dependent addition that a removal ends; leave "" if not known.
        claim_id: The reference number of the compensation claim; leave "" if not known.
    """
    match = {k: v for k, v in {"dependent_event_id": dependent_event_id, "award_id": award_id, "customer_id": customer_id, "source_dependent_event_id": source_dependent_event_id, "claim_id": claim_id}.items() if v}
    rows = ctx.find("comp_dependents", **match)
    return str(rows) if rows else f"No matching records for {match}."

@tool(owner="agent", rw="read")
def find_pension_awards(ctx: ToolContext, pension_award_id: str = "", customer_id: str = "") -> str:
    """Look up a veteran's Veterans Pension award: the rate category in effect and its effective date, award status,
    the wartime period of service, the countable income, accepted medical expenses and net worth on file, additional
    children, Medicaid nursing-home status, and how payments are delivered. Give any reference number you hold;
    every criterion is optional, and with none the full list is returned.

    Args:
        pension_award_id: The reference number of the Veterans Pension award; leave "" if not known.
        customer_id: The beneficiary's reference number (the person whose records these are); leave "" if not known.
    """
    match = {k: v for k, v in {"pension_award_id": pension_award_id, "customer_id": customer_id}.items() if v}
    rows = ctx.find("pension_awards", **match)
    return str(rows) if rows else f"No matching records for {match}."

@tool(owner="agent", rw="read")
def find_pension_payments(ctx: ToolContext, pension_payment_id: str = "", pension_award_id: str = "", customer_id: str = "", source_payment_id: str = "", adjustment_id: str = "") -> str:
    """Look up Veterans Pension payments: monthly payments by entitlement month, retroactive releases, and returned
    payments, with gross, withheld and net amounts and issue dates. Give any reference number you hold; every
    criterion is optional, and with none the full list is returned.

    Args:
        pension_payment_id: The reference number of the pension payment itself; leave "" if not known.
        pension_award_id: The reference number of the Veterans Pension award; leave "" if not known.
        customer_id: The beneficiary's reference number (the person whose records these are); leave "" if not known.
        source_payment_id: The reference number of the original payment that this entry returns, reissues or was withheld from; leave "" if not known.
        adjustment_id: The reference number of the rate adjustment that produced a retroactive pension payment; leave "" if not known.
    """
    match = {k: v for k, v in {"pension_payment_id": pension_payment_id, "pension_award_id": pension_award_id, "customer_id": customer_id, "source_payment_id": source_payment_id, "adjustment_id": adjustment_id}.items() if v}
    rows = ctx.find("pension_payments", **match)
    return str(rows) if rows else f"No matching records for {match}."

@tool(owner="agent", rw="read")
def find_pension_income_reports(ctx: ToolContext, report_id: str = "", pension_award_id: str = "", customer_id: str = "", source_report_id: str = "") -> str:
    """Look up what has been reported or found about a pensioner's finances: income changes by source, medical expense
    reports by period, asset transfers, Social Security or IRS income matches, and the rate adjustments made from
    them, including effective dates, new annual rates, penalty months and whether an overpayment resulted. Give any
    reference number you hold; every criterion is optional, and with none the full list is returned.

    Args:
        report_id: The reference number of the income, expense or asset report, income match or rate adjustment itself; leave "" if not known.
        pension_award_id: The reference number of the Veterans Pension award; leave "" if not known.
        customer_id: The beneficiary's reference number (the person whose records these are); leave "" if not known.
        source_report_id: The reference number of the report or income match that a rate adjustment acts on; leave "" if not known.
    """
    match = {k: v for k, v in {"report_id": report_id, "pension_award_id": pension_award_id, "customer_id": customer_id, "source_report_id": source_report_id}.items() if v}
    rows = ctx.find("pension_income_reports", **match)
    return str(rows) if rows else f"No matching records for {match}."

@tool(owner="agent", rw="read")
def find_edu_benefits(ctx: ToolContext, edu_benefit_id: str = "", customer_id: str = "") -> str:
    """Look up a student's education benefits, one per chapter: the chapter and benefit level held, status, entitlement
    granted and remaining, the delimiting date if any, the Certificate of Eligibility date, the school's Yellow
    Ribbon status, and how payments to the student are delivered. Give any reference number you hold; every
    criterion is optional, and with none the full list is returned.

    Args:
        edu_benefit_id: The reference number of the education benefit (one per chapter); leave "" if not known.
        customer_id: The beneficiary's reference number (the person whose records these are); leave "" if not known.
    """
    match = {k: v for k, v in {"edu_benefit_id": edu_benefit_id, "customer_id": customer_id}.items() if v}
    rows = ctx.find("edu_benefits", **match)
    return str(rows) if rows else f"No matching records for {match}."

@tool(owner="agent", rw="read")
def find_edu_enrollments(ctx: ToolContext, enrollment_id: str = "", edu_benefit_id: str = "", customer_id: str = "", source_enrollment_id: str = "") -> str:
    """Look up enrollment records for an education benefit: term certifications by school with dates, credits, training
    time, rate of pursuit, tuition and fees and the campus housing rate; amendments for reductions or withdrawals
    with their effective date and outcome; and the student's monthly enrollment verifications. Give any reference
    number you hold; every criterion is optional, and with none the full list is returned.

    Args:
        enrollment_id: The reference number of the school's enrollment certification; leave "" if not known.
        edu_benefit_id: The reference number of the education benefit (one per chapter); leave "" if not known.
        customer_id: The beneficiary's reference number (the person whose records these are); leave "" if not known.
        source_enrollment_id: The reference number of the certification that an amendment or monthly verification refers to; leave "" if not known.
    """
    match = {k: v for k, v in {"enrollment_id": enrollment_id, "edu_benefit_id": edu_benefit_id, "customer_id": customer_id, "source_enrollment_id": source_enrollment_id}.items() if v}
    rows = ctx.find("edu_enrollments", **match)
    return str(rows) if rows else f"No matching records for {match}."

@tool(owner="agent", rw="read")
def find_edu_payments(ctx: ToolContext, edu_payment_id: str = "", edu_benefit_id: str = "", customer_id: str = "", enrollment_id: str = "", source_payment_id: str = "") -> str:
    """Look up education payments: tuition and fees paid to the school, monthly housing allowance and flat monthly
    payments to the student by month of training, books stipends, and money returned, with amounts, payees and
    dates. Give any reference number you hold; every criterion is optional, and with none the full list is returned.

    Args:
        edu_payment_id: The reference number of the education payment itself; leave "" if not known.
        edu_benefit_id: The reference number of the education benefit (one per chapter); leave "" if not known.
        customer_id: The beneficiary's reference number (the person whose records these are); leave "" if not known.
        enrollment_id: The reference number of the school's enrollment certification; leave "" if not known.
        source_payment_id: The reference number of the original payment that this entry returns, reissues or was withheld from; leave "" if not known.
    """
    match = {k: v for k, v in {"edu_payment_id": edu_payment_id, "edu_benefit_id": edu_benefit_id, "customer_id": customer_id, "enrollment_id": enrollment_id, "source_payment_id": source_payment_id}.items() if v}
    rows = ctx.find("edu_payments", **match)
    return str(rows) if rows else f"No matching records for {match}."

@tool(owner="agent", rw="read")
def find_edu_entitlement_ledger(ctx: ToolContext, entitlement_txn_id: str = "", edu_benefit_id: str = "", customer_id: str = "", enrollment_id: str = "") -> str:
    """Look up entitlement charged to or restored on an education benefit, with the days, the training period covered
    and the reason for a restoration. Give any reference number you hold; every criterion is optional, and with none
    the full list is returned.

    Args:
        entitlement_txn_id: The reference number of the entitlement charge or restoration itself; leave "" if not known.
        edu_benefit_id: The reference number of the education benefit (one per chapter); leave "" if not known.
        customer_id: The beneficiary's reference number (the person whose records these are); leave "" if not known.
        enrollment_id: The reference number of the school's enrollment certification; leave "" if not known.
    """
    match = {k: v for k, v in {"entitlement_txn_id": entitlement_txn_id, "edu_benefit_id": edu_benefit_id, "customer_id": customer_id, "enrollment_id": enrollment_id}.items() if v}
    rows = ctx.find("edu_entitlement_ledger", **match)
    return str(rows) if rows else f"No matching records for {match}."

@tool(owner="agent", rw="read")
def find_loan_guaranties(ctx: ToolContext, loan_id: str = "", customer_id: str = "") -> str:
    """Look up a veteran's VA home loans: the loan program, VA loan number, servicer, property state and county limit,
    closing date and loan amount, first or subsequent use, down payment, guaranty, funding fee exemption, unpaid
    balance, occupancy and release-of-liability status, any partial claim owed, and loan status. Give any reference
    number you hold; every criterion is optional, and with none the full list is returned.

    Args:
        loan_id: The reference number of the VA home loan record; leave "" if not known.
        customer_id: The beneficiary's reference number (the person whose records these are); leave "" if not known.
    """
    match = {k: v for k, v in {"loan_id": loan_id, "customer_id": customer_id}.items() if v}
    rows = ctx.find("loan_guaranties", **match)
    return str(rows) if rows else f"No matching records for {match}."

@tool(owner="agent", rw="read")
def find_loan_transactions(ctx: ToolContext, loan_txn_id: str = "", loan_id: str = "", customer_id: str = "", source_txn_id: str = "") -> str:
    """Look up money movements on a VA home loan: funding fees charged and refunded, partial claims paid and repaid,
    and guaranty claims paid after liquidation. Give any reference number you hold; every criterion is optional, and
    with none the full list is returned.

    Args:
        loan_txn_id: The reference number of the loan money transaction itself; leave "" if not known.
        loan_id: The reference number of the VA home loan record; leave "" if not known.
        customer_id: The beneficiary's reference number (the person whose records these are); leave "" if not known.
        source_txn_id: The reference number of the original charge, premium or partial claim that this entry refunds or repays; leave "" if not known.
    """
    match = {k: v for k, v in {"loan_txn_id": loan_txn_id, "loan_id": loan_id, "customer_id": customer_id, "source_txn_id": source_txn_id}.items() if v}
    rows = ctx.find("loan_transactions", **match)
    return str(rows) if rows else f"No matching records for {match}."

@tool(owner="agent", rw="read")
def find_loan_entitlement_actions(ctx: ToolContext, entitlement_action_id: str = "", loan_id: str = "", customer_id: str = "", substitute_customer_id: str = "") -> str:
    """Look up home loan entitlement charged to a loan and restored from it, with the amount, date and basis of each
    restoration. Give any reference number you hold; every criterion is optional, and with none the full list is
    returned.

    Args:
        entitlement_action_id: The reference number of the entitlement charge or restoration itself; leave "" if not known.
        loan_id: The reference number of the VA home loan record; leave "" if not known.
        customer_id: The beneficiary's reference number (the person whose records these are); leave "" if not known.
        substitute_customer_id: The reference number of the assuming veteran who substituted entitlement; leave "" if not known.
    """
    match = {k: v for k, v in {"entitlement_action_id": entitlement_action_id, "loan_id": loan_id, "customer_id": customer_id, "substitute_customer_id": substitute_customer_id}.items() if v}
    rows = ctx.find("loan_entitlement_actions", **match)
    return str(rows) if rows else f"No matching records for {match}."

@tool(owner="agent", rw="read")
def find_debt_accounts(ctx: ToolContext, debt_id: str = "", customer_id: str = "", source_record_id: str = "") -> str:
    """Look up a beneficiary's VA debts: the debt type, the benefit line and record that created it, the original
    amount and current balance, the date of the initial notice, collection status and any hold reason, repayment
    plan terms, fraud finding, and any Treasury referral or credit bureau report. Give any reference number you
    hold; every criterion is optional, and with none the full list is returned.

    Args:
        debt_id: The reference number of the VA debt; leave "" if not known.
        customer_id: The beneficiary's reference number (the person whose records these are); leave "" if not known.
        source_record_id: The reference number of the benefit record whose overpayment or claim created the debt; leave "" if not known.
    """
    match = {k: v for k, v in {"debt_id": debt_id, "customer_id": customer_id, "source_record_id": source_record_id}.items() if v}
    rows = ctx.find("debt_accounts", **match)
    return str(rows) if rows else f"No matching records for {match}."

@tool(owner="agent", rw="read")
def find_debt_transactions(ctx: ToolContext, debt_txn_id: str = "", debt_id: str = "", customer_id: str = "", source_payment_id: str = "", request_id: str = "") -> str:
    """Look up activity on a VA debt: amounts collected by benefit offset or direct payment, waiver and compromise
    credits, balance corrections, interest and Treasury fees added, and refunds of overcollection. Give any
    reference number you hold; every criterion is optional, and with none the full list is returned.

    Args:
        debt_txn_id: The reference number of the debt transaction itself; leave "" if not known.
        debt_id: The reference number of the VA debt; leave "" if not known.
        customer_id: The beneficiary's reference number (the person whose records these are); leave "" if not known.
        source_payment_id: The reference number of the original payment that this entry returns, reissues or was withheld from; leave "" if not known.
        request_id: The reference number of the waiver, dispute, compromise or plan request; leave "" if not known.
    """
    match = {k: v for k, v in {"debt_txn_id": debt_txn_id, "debt_id": debt_id, "customer_id": customer_id, "source_payment_id": source_payment_id, "request_id": request_id}.items() if v}
    rows = ctx.find("debt_transactions", **match)
    return str(rows) if rows else f"No matching records for {match}."

@tool(owner="agent", rw="read")
def find_debt_requests(ctx: ToolContext, request_id: str = "", debt_id: str = "", customer_id: str = "", source_request_id: str = "") -> str:
    """Look up requests a debtor has made about a VA debt - waivers, disputes, compromise offers and repayment plan or
    reduced withholding requests - and the decisions on them, with dates, amounts, whether a Financial Status Report
    was included and whether the request arrived within the collection-hold window. Give any reference number you
    hold; every criterion is optional, and with none the full list is returned.

    Args:
        request_id: The reference number of the waiver, dispute, compromise or plan request; leave "" if not known.
        debt_id: The reference number of the VA debt; leave "" if not known.
        customer_id: The beneficiary's reference number (the person whose records these are); leave "" if not known.
        source_request_id: The reference number of the request that a decision decides; leave "" if not known.
    """
    match = {k: v for k, v in {"request_id": request_id, "debt_id": debt_id, "customer_id": customer_id, "source_request_id": source_request_id}.items() if v}
    rows = ctx.find("debt_requests", **match)
    return str(rows) if rows else f"No matching records for {match}."

@tool(owner="agent", rw="read")
def find_decision_reviews(ctx: ToolContext, review_id: str = "", customer_id: str = "", contested_decision_id: str = "", prior_review_id: str = "") -> str:
    """Look up decision reviews and appeals: the lane chosen, the benefit line, decision and issue under review, the
    decision notice and received dates, any earlier review it continues, hearing and docket details, status and
    outcome. Give any reference number you hold; every criterion is optional, and with none the full list is
    returned.

    Args:
        review_id: The reference number of the decision review; leave "" if not known.
        customer_id: The beneficiary's reference number (the person whose records these are); leave "" if not known.
        contested_decision_id: The reference number of the decision being reviewed; leave "" if not known.
        prior_review_id: The reference number of the earlier review that this review continues; leave "" if not known.
    """
    match = {k: v for k, v in {"review_id": review_id, "customer_id": customer_id, "contested_decision_id": contested_decision_id, "prior_review_id": prior_review_id}.items() if v}
    rows = ctx.find("decision_reviews", **match)
    return str(rows) if rows else f"No matching records for {match}."

@tool(owner="agent", rw="read")
def find_appeal_actions(ctx: ToolContext, appeal_action_id: str = "", review_id: str = "", customer_id: str = "") -> str:
    """Look up actions within a decision review: evidence submitted, informal conferences, Board hearings, duty-to-
    assist errors found and decisions issued. Give any reference number you hold; every criterion is optional, and
    with none the full list is returned.

    Args:
        appeal_action_id: The reference number of the review action itself; leave "" if not known.
        review_id: The reference number of the decision review; leave "" if not known.
        customer_id: The beneficiary's reference number (the person whose records these are); leave "" if not known.
    """
    match = {k: v for k, v in {"appeal_action_id": appeal_action_id, "review_id": review_id, "customer_id": customer_id}.items() if v}
    rows = ctx.find("appeal_actions", **match)
    return str(rows) if rows else f"No matching records for {match}."

@tool(owner="agent", rw="read")
def find_ins_policies(ctx: ToolContext, ins_policy_id: str = "", customer_id: str = "") -> str:
    """Look up a veteran's Veterans' Group Life Insurance policy: coverage tier, policy number, policy status, the SGLI
    end date and application date, billing frequency and payment method, paid-to date, beneficiary designation date
    and whether an accelerated benefit was paid. Give any reference number you hold; every criterion is optional,
    and with none the full list is returned.

    Args:
        ins_policy_id: The reference number of the VGLI policy; leave "" if not known.
        customer_id: The beneficiary's reference number (the person whose records these are); leave "" if not known.
    """
    match = {k: v for k, v in {"ins_policy_id": ins_policy_id, "customer_id": customer_id}.items() if v}
    rows = ctx.find("ins_policies", **match)
    return str(rows) if rows else f"No matching records for {match}."

@tool(owner="agent", rw="read")
def find_ins_premium_ledger(ctx: ToolContext, ins_txn_id: str = "", ins_policy_id: str = "", customer_id: str = "", source_txn_id: str = "") -> str:
    """Look up premium and benefit activity on a VGLI policy: premiums paid by coverage period and age band, premium
    refunds, accelerated and death benefits paid, and beneficiary designations. Give any reference number you hold;
    every criterion is optional, and with none the full list is returned.

    Args:
        ins_txn_id: The reference number of the premium, benefit or beneficiary entry itself; leave "" if not known.
        ins_policy_id: The reference number of the VGLI policy; leave "" if not known.
        customer_id: The beneficiary's reference number (the person whose records these are); leave "" if not known.
        source_txn_id: The reference number of the original charge, premium or partial claim that this entry refunds or repays; leave "" if not known.
    """
    match = {k: v for k, v in {"ins_txn_id": ins_txn_id, "ins_policy_id": ins_policy_id, "customer_id": customer_id, "source_txn_id": source_txn_id}.items() if v}
    rows = ctx.find("ins_premium_ledger", **match)
    return str(rows) if rows else f"No matching records for {match}."

@tool(owner="agent", rw="read")
def find_dic_awards(ctx: ToolContext, dic_award_id: str = "", customer_id: str = "", veteran_customer_id: str = "") -> str:
    """Look up a surviving spouse's Dependency and Indemnity Compensation award: the rate category, status, the
    deceased veteran and date of death, marriage date, effective date, transitional benefit period, termination
    reason and how payments are delivered. Give any reference number you hold; every criterion is optional, and with
    none the full list is returned.

    Args:
        dic_award_id: The reference number of the DIC award; leave "" if not known.
        customer_id: The beneficiary's reference number (the person whose records these are); leave "" if not known.
        veteran_customer_id: The reference number of the deceased veteran's profile; leave "" if not known.
    """
    match = {k: v for k, v in {"dic_award_id": dic_award_id, "customer_id": customer_id, "veteran_customer_id": veteran_customer_id}.items() if v}
    rows = ctx.find("dic_awards", **match)
    return str(rows) if rows else f"No matching records for {match}."

@tool(owner="agent", rw="read")
def find_dic_payments(ctx: ToolContext, dic_payment_id: str = "", dic_award_id: str = "", customer_id: str = "", source_payment_id: str = "") -> str:
    """Look up DIC payments: monthly payments by entitlement month, retroactive releases and returned payments, with
    amounts and dates. Give any reference number you hold; every criterion is optional, and with none the full list
    is returned.

    Args:
        dic_payment_id: The reference number of the DIC payment itself; leave "" if not known.
        dic_award_id: The reference number of the DIC award; leave "" if not known.
        customer_id: The beneficiary's reference number (the person whose records these are); leave "" if not known.
        source_payment_id: The reference number of the original payment that this entry returns, reissues or was withheld from; leave "" if not known.
    """
    match = {k: v for k, v in {"dic_payment_id": dic_payment_id, "dic_award_id": dic_award_id, "customer_id": customer_id, "source_payment_id": source_payment_id}.items() if v}
    rows = ctx.find("dic_payments", **match)
    return str(rows) if rows else f"No matching records for {match}."

@tool(owner="agent", rw="read")
def find_dic_children(ctx: ToolContext, dic_child_event_id: str = "", dic_award_id: str = "", customer_id: str = "", source_child_event_id: str = "") -> str:
    """Look up children added to or removed from a DIC award, with names, birth dates, effective dates and removal
    reasons. Give any reference number you hold; every criterion is optional, and with none the full list is
    returned.

    Args:
        dic_child_event_id: The reference number of the child addition or removal itself; leave "" if not known.
        dic_award_id: The reference number of the DIC award; leave "" if not known.
        customer_id: The beneficiary's reference number (the person whose records these are); leave "" if not known.
        source_child_event_id: The reference number of the child addition that a removal ends; leave "" if not known.
    """
    match = {k: v for k, v in {"dic_child_event_id": dic_child_event_id, "dic_award_id": dic_award_id, "customer_id": customer_id, "source_child_event_id": source_child_event_id}.items() if v}
    rows = ctx.find("dic_children", **match)
    return str(rows) if rows else f"No matching records for {match}."


@tool(owner="agent", rw="write")
def verify_identity(ctx: ToolContext, customer_id: str, ssn_last4: str = "", va_file_number: str = "",
                    date_of_birth: str = "", phone_number: str = "", email: str = "") -> str:
    """Verify the caller's identity against the beneficiary's VA profile and record the result.

    Identity must be verified before discussing or changing anything on the beneficiary's benefits, payments or
    debts. This tool does the comparison itself: it checks each item the caller states against the profile on file,
    counts how many agree, and passes only when at least 3 items match. The beneficiary's reference number only
    selects the profile to compare against and never counts as a match. Callers usually give only some of these
    items, so pass exactly what the caller said, unchanged, and leave the rest "". The result is recorded; if a first
    attempt falls short and a later attempt with more items passes, the pass stands.

    Args:
        customer_id: The beneficiary's reference number, taken from the profile found for this caller. Required.
        ssn_last4: The last four digits of the caller's Social Security number, 4 digits; leave "" if not stated.
        va_file_number: The caller's VA file number, 8 or 9 digits with no separators; leave "" if not stated.
        date_of_birth: The caller's date of birth as YYYY-MM-DD; leave "" if not stated.
        phone_number: The caller's telephone number, 10 digits with no separators; leave "" if not stated.
        email: The caller's email address exactly as stated; leave "" if not stated.
    """
    if not customer_id:
        return "Error: customer_id is required; find the beneficiary's profile first."
    rows = ctx.find("customers", customer_id=customer_id)
    if not rows:
        return f"Error: no beneficiary profile {customer_id}; cannot verify."
    rec = rows[0]
    supplied = {"ssn_last4": ssn_last4, "va_file_number": va_file_number, "date_of_birth": date_of_birth,
                "phone_number": phone_number, "email": email}
    matched = sum(1 for field, value in supplied.items()
                  if value and str(rec.get(field, "")).strip().lower() == str(value).strip().lower())
    verified = matched >= 3
    rid = ctx.make_id("idv_", customer_id)
    prior = ctx.find("identity_verifications", verification_id=rid)
    verified = verified or bool(prior and prior[0].get("verified"))
    if prior:
        ctx.update("identity_verifications", rid, verified=verified, verified_at=ctx.now())
    else:
        ctx.create("identity_verifications", rid, verification_id=rid, customer_id=customer_id,
                   verified=verified, verified_at=ctx.now())
    if verified:
        return f"Identity verified for {customer_id}."
    return (f"Identity NOT verified for {customer_id}: only {matched} of the 3 required items matched. "
            "Ask the caller for another item on file and try again.")


@tool(owner="agent", rw="write")
def transfer_to_human_agent(ctx: ToolContext, customer_id: str, reason: str) -> str:
    """Transfer the caller to a human Veterans Service Representative and record the transfer with its reason.

    Use it in one of two situations only: when no published policy lets you resolve what the caller is asking for,
    or when the caller has asked for a human representative 2 times. After the transfer, the representative takes
    over the contact.

    Args:
        customer_id: The beneficiary's reference number, taken from the profile found for this caller.
        reason: Exactly one of POLICY_NOT_COVERED (no published policy resolves the request) or CUSTOMER_REQUESTED
            (the caller has asked for a human representative 2 times). No other wording is accepted.
    """
    allowed = {"POLICY_NOT_COVERED", "CUSTOMER_REQUESTED"}
    if reason not in allowed:
        return f"Error: unknown transfer reason '{reason}'. Use one of: {', '.join(sorted(allowed))}."
    if not ctx.find("customers", customer_id=customer_id):
        return f"Error: no beneficiary profile {customer_id}; cannot record the transfer."
    rid = ctx.make_id("hof_", customer_id, reason)
    ctx.create("human_handoffs", rid, handoff_id=rid, customer_id=customer_id, reason=reason, created_at=ctx.now())
    return f"Transfer to a human representative recorded for {customer_id} ({reason})."

"""Hidden task tools of the financial_assistance_screening difficulty (category `assist`).

Each tool performs one atomic write on a financial assistance case and returns a plain-text
receipt. The tools judge no eligibility and compute no figure: every amount, percent, day count
and date they record is passed in by the caller exactly as worked out from the published
Financial Assistance Policy.
"""

from erlbench import ToolContext, tool


class _Calendar:
    """Pure calendar arithmetic on YYYY-MM-DD strings (no clock, no randomness)."""

    @staticmethod
    def to_ordinal(ymd: str) -> int:
        y, m, d = (int(p) for p in str(ymd)[:10].split("-"))
        y2 = y - (1 if m <= 2 else 0)
        era = (y2 if y2 >= 0 else y2 - 399) // 400
        yoe = y2 - era * 400
        mp = (m + 9) % 12
        doy = (153 * mp + 2) // 5 + d - 1
        doe = yoe * 365 + yoe // 4 - yoe // 100 + doy
        return era * 146097 + doe

    @staticmethod
    def from_ordinal(n: int) -> str:
        era = (n if n >= 0 else n - 146096) // 146097
        doe = n - era * 146097
        yoe = (doe - doe // 1460 + doe // 36524 - doe // 146096) // 365
        y = yoe + era * 400
        doy = doe - (365 * yoe + yoe // 4 - yoe // 100)
        mp = (5 * doy + 2) // 153
        d = doy - (153 * mp + 2) // 5 + 1
        m = mp + 3 if mp < 10 else mp - 9
        y = y + (1 if m <= 2 else 0)
        return f"{y:04d}-{m:02d}-{d:02d}"

    @staticmethod
    def add_days(ymd: str, days: int) -> str:
        return _Calendar.from_ordinal(_Calendar.to_ordinal(ymd) + int(days))


@tool(owner="user", rw="write")
def sign_hardship_supplement_15cad132(ctx: ToolContext, fap_case_id: str, qualifying_medical_debt_usd: float) -> str:
    """The patient signs, through the Riverbend patient portal, a Medical Hardship supplement to their own
    open financial assistance application. The signed supplement is received on that same open case as
    supporting information, and the medical debt it claims is recorded on the case as the case's
    qualifying medical debt figure, replacing the figure shown there. The case keeps its status, tier,
    application date and every other figure. The patient sees a confirmation that the supplement was
    received on the case together with the claimed amount now on file.

    Args:
        fap_case_id: Id class — the reference number of the patient's open financial assistance case, as
            shown by the financial assistance case lookup for this patient.
        qualifying_medical_debt_usd: Fixed-format class — the medical debt the supplement claims, in USD,
            a non-negative amount stated to 2 decimal places (cents); the value is stored rounded
            half-up to 2 decimal places.

    Returns:
        A one-line text receipt: "Hardship supplement received on case <fap_case_id>; claimed medical debt
        on file: <amount> USD." The amount is the recorded figure with 2 decimal places; the receipt
        appearing means the supplement is on the case.
    """
    amount = round(float(qualifying_medical_debt_usd), 2)
    ctx.update("assistance_cases", fap_case_id, qualifying_medical_debt_usd=amount)
    return f"Hardship supplement received on case {fap_case_id}; claimed medical debt on file: {amount:.2f} USD."


@tool(owner="agent", rw="write")
def record_qualifying_debt_da5f54be(ctx: ToolContext, fap_case_id: str, qualifying_medical_debt_usd: float) -> str:
    """A financial counselor records on a financial assistance case the qualifying medical debt that
    Riverbend has documented for its own charges. The case's qualifying medical debt figure is
    replaced by the documented amount; status, tier, dates and the other household figures stay as they
    are. The counselor and the patient can see the documented figure on the case.

    Args:
        fap_case_id: Id class — the reference number of the financial assistance case being documented, as
            shown by the financial assistance case lookup for the patient.
        qualifying_medical_debt_usd: Fixed-format class — the documented qualifying medical debt, in USD,
            a non-negative amount stated to 2 decimal places (cents); stored rounded half-up to 2
            decimal places.

    Returns:
        A one-line text receipt: "Qualifying medical debt documented on case <fap_case_id>: <amount> USD."
        The amount carries 2 decimal places; the receipt appearing means the figure is on the case.
    """
    amount = round(float(qualifying_medical_debt_usd), 2)
    ctx.update("assistance_cases", fap_case_id, qualifying_medical_debt_usd=amount)
    return f"Qualifying medical debt documented on case {fap_case_id}: {amount:.2f} USD."


@tool(owner="agent", rw="write")
def record_documented_costs_4c71e2b9(ctx: ToolContext, fap_case_id: str, qualifying_medical_debt_usd: float) -> str:
    """A financial counselor records on a financial assistance case the qualifying medical debt documented
    with the medical costs that no Riverbend bill yet carries or that the patient's claim set aside. The
    case's qualifying medical debt figure is replaced by the documented amount; status, tier, dates and the
    other household figures stay as they are. The counselor and the patient can see the documented figure
    on the case.

    Args:
        fap_case_id: Id class — the reference number of the financial assistance case being documented, as
            shown by the financial assistance case lookup for the patient.
        qualifying_medical_debt_usd: Fixed-format class — the qualifying medical debt documented with those
            costs, in USD, a non-negative amount stated to 2 decimal places (cents); stored rounded half-up
            to 2 decimal places.

    Returns:
        A one-line text receipt: "Qualifying medical debt with other medical costs recorded on case
        <fap_case_id>: <amount> USD." The amount carries 2 decimal places; the receipt appearing means the
        figure is on the case.
    """
    amount = round(float(qualifying_medical_debt_usd), 2)
    ctx.update("assistance_cases", fap_case_id, qualifying_medical_debt_usd=amount)
    return f"Qualifying medical debt with other medical costs recorded on case {fap_case_id}: {amount:.2f} USD."


@tool(owner="agent", rw="write")
def approve_hardship_award_afb08b0b(ctx: ToolContext, fap_case_id: str, hardship_liability_cap_usd: float,
                                    award_start_date: str, award_end_date: str, notice_language: str) -> str:
    """A financial counselor approves a Medical Hardship financial assistance case. The case moves to
    approved status with today's date as its determination date, the given earliest and last
    covered dates of service, and the given hardship liability cap; an approval letter is logged on the case,
    dated today and written in the given language. The patient can see the approved award, its
    covered dates and its liability cap, and the approval letter on the case.

    Args:
        fap_case_id: Id class — the reference number of the financial assistance case being approved, as
            shown by the financial assistance case lookup for the patient.
        hardship_liability_cap_usd: Fixed-format class — the hardship liability cap of the award, in USD, a
            non-negative amount stated to 2 decimal places (cents); stored rounded half-up to 2
            decimal places.
        award_start_date: Fixed-format class — the earliest date of service the award covers, written as
            YYYY-MM-DD.
        award_end_date: Fixed-format class — the last date of service the award covers, written as
            YYYY-MM-DD.
        notice_language: Enum class — the language of the approval letter: English applies when the
            patient's preferred language on the registration profile is English or is not one of the
            letter languages; Spanish applies when the preferred language is Spanish; Hmong applies when
            the preferred language is Hmong.

    Returns:
        A one-line text receipt: "Case <fap_case_id> approved on <determination date YYYY-MM-DD>: covers
        services <award_start_date> to <award_end_date>, hardship liability cap <amount> USD; approval
        letter <letter reference> logged in <language>." The receipt appearing means the award is
        approved and the letter is on the case.
    """
    cap = round(float(hardship_liability_cap_usd), 2)
    today = ctx.now()[:10]
    ctx.update("assistance_cases", fap_case_id, status="approved", determination_date=today,
               award_start_date=award_start_date, award_end_date=award_end_date,
               hardship_liability_cap_usd=cap, denial_reason="NONE")
    case_rows = ctx.find("assistance_cases", fap_case_id=fap_case_id)
    customer = case_rows[0].get("customer_id") if case_rows else ""
    letter = ctx.make_id("fapt_", fap_case_id, "APPROVAL_LETTER", today, notice_language)
    ctx.create("assistance_transactions", letter, fap_txn_id=letter, fap_case_id=fap_case_id,
               customer_id=customer, event_type="assist_notice_sent", notice_type="APPROVAL_LETTER",
               notice_language=notice_language, posting_date=today, amount=0.0)
    return (f"Case {fap_case_id} approved on {today}: covers services {award_start_date} to {award_end_date}, "
            f"hardship liability cap {cap:.2f} USD; approval letter {letter} logged in {notice_language}.")


@tool(owner="user", rw="write")
def sign_renewal_debt_claim_3b9e07c1(ctx: ToolContext, fap_case_id: str, qualifying_medical_debt_usd: float) -> str:
    """The patient signs, through the Riverbend patient portal, the claim of medical debt on their own
    renewal application for a Medical Hardship award. The medical debt the signed claim states is
    recorded on the renewal case as the case's qualifying medical debt figure, replacing the figure shown
    there. The renewal case keeps its status, tier, application date and every other figure, and the
    approved award being renewed is left unchanged. The patient sees a confirmation that the claim was
    received on the renewal case together with the claimed amount now on file.

    Args:
        fap_case_id: Id class — the reference number of the patient's renewal case, as shown by the
            financial assistance case lookup for this patient.
        qualifying_medical_debt_usd: Fixed-format class — the medical debt the renewal claims, in USD, a
            non-negative amount stated to 2 decimal places (cents); the value is stored rounded half-up
            to 2 decimal places.

    Returns:
        A one-line text receipt: "Renewal medical-debt claim received on case <fap_case_id>; claimed
        medical debt on file: <amount> USD." The amount is the recorded figure with 2 decimal places; the
        receipt appearing means the claim is on the renewal case.
    """
    amount = round(float(qualifying_medical_debt_usd), 2)
    ctx.update("assistance_cases", fap_case_id, qualifying_medical_debt_usd=amount)
    return f"Renewal medical-debt claim received on case {fap_case_id}; claimed medical debt on file: {amount:.2f} USD."


@tool(owner="agent", rw="write")
def send_missing_information_notice_7f5665e5(ctx: ToolContext, fap_case_id: str, response_days: int,
                                             notice_language: str, income_proof_request: str,
                                             residency_request: str, outside_bills_request: str,
                                             bank_statement_request: str, medicaid_notice_request: str) -> str:
    """A financial counselor sends the missing-information notice on an incomplete financial assistance
    case. The case moves to pending documents and its documents due date is set to today plus the given
    number of calendar days; the notice is logged on the case, dated today, in the given language; and
    each document type marked as requested is logged on the case as requested, dated today. The patient
    can see the pending-documents status, the due date and the list of requested documents.

    Args:
        fap_case_id: Id class — the reference number of the financial assistance case the notice is sent
            on, as shown by the financial assistance case lookup for the patient.
        response_days: Fixed-format class — the number of calendar days the patient is given, an integer
            of at least 1; the due date is today's date plus that many calendar days, written YYYY-MM-DD.
        notice_language: Enum class — the language of the notice: English applies when the patient's
            preferred language on the registration profile is English or is not one of the letter
            languages; Spanish applies when the preferred language is Spanish; Hmong applies when the
            preferred language is Hmong.
        income_proof_request: Enum class — whether proof of income is on the list, a request being logged
            as pay stubs for the last 90 days: REQUESTED applies when no income document has been accepted
            on the case; NOT_REQUESTED applies when one has.
        residency_request: Enum class — whether proof of residency is on the list: REQUESTED applies when no
            proof of residency has been accepted on the case; NOT_REQUESTED applies when one has.
        outside_bills_request: Enum class — whether outside medical bills are on the list: REQUESTED applies
            when the tier requires outside medical bills and none have been accepted on the case;
            NOT_REQUESTED applies otherwise.
        bank_statement_request: Enum class — whether a bank statement is on the list: REQUESTED applies when
            the tier requires a bank statement and none has been accepted on the case; NOT_REQUESTED applies
            otherwise.
        medicaid_notice_request: Enum class — whether a BadgerCare Plus (Wisconsin Medicaid) determination
            notice is on the list: REQUESTED applies when the tier requires a Medicaid determination notice and
            none has been accepted on the case; NOT_REQUESTED applies otherwise.

    Returns:
        A one-line text receipt: "Missing-information notice <notice reference> sent on case <fap_case_id>
        in <language>; documents due <due date YYYY-MM-DD>; requested: <comma list of requested document
        types, or none>." The receipt appearing means the case is pending documents with that due date.
    """
    today = ctx.now()[:10]
    due = _Calendar.add_days(today, int(response_days))
    case_rows = ctx.find("assistance_cases", fap_case_id=fap_case_id)
    customer = case_rows[0].get("customer_id") if case_rows else ""
    ctx.update("assistance_cases", fap_case_id, status="pending_documents", documents_due_date=due)
    notice = ctx.make_id("fapt_", fap_case_id, "MISSING_INFORMATION_NOTICE", today, int(response_days),
                         notice_language, income_proof_request, residency_request, outside_bills_request,
                         bank_statement_request, medicaid_notice_request)
    ctx.create("assistance_transactions", notice, fap_txn_id=notice, fap_case_id=fap_case_id,
               customer_id=customer, event_type="assist_notice_sent", notice_type="MISSING_INFORMATION_NOTICE",
               notice_language=notice_language, posting_date=today, amount=0.0)
    requested = []
    for doc_type, flag in (("PAY_STUBS_LAST_90_DAYS", income_proof_request),
                           ("PROOF_OF_RESIDENCY", residency_request),
                           ("OUTSIDE_MEDICAL_BILLS", outside_bills_request),
                           ("BANK_STATEMENT", bank_statement_request),
                           ("MEDICAID_DETERMINATION_NOTICE", medicaid_notice_request)):
        if flag == "REQUESTED":
            row = ctx.make_id("fapt_", fap_case_id, doc_type, "REQUESTED", today)
            ctx.create("assistance_transactions", row, fap_txn_id=row, fap_case_id=fap_case_id,
                       customer_id=customer, event_type="assist_document_logged", document_type=doc_type,
                       document_status="REQUESTED", posting_date=today, amount=0.0)
            requested.append(doc_type)
    listed = ", ".join(requested) if requested else "none"
    return (f"Missing-information notice {notice} sent on case {fap_case_id} in {notice_language}; "
            f"documents due {due}; requested: {listed}.")

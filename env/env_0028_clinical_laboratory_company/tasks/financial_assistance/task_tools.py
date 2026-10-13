"""Hidden task tools of the financial_assistance difficulty (Patient Financial Assistance Program).

Every tool here is reached only through unlock_* -> call_* and is named by exactly one
extended policy's target_tool in assistance.extended.yaml. Each tool performs one atomic
write on this category's own records (assistance_cases / assistance_events), takes the values
the agent has already worked out from policy and records, and performs no eligibility,
prerequisite or amount judgement of its own.
"""

from erlbench import ToolContext, tool


@tool(owner="agent", rw="write")
def apply_award_discount_6c746b08(ctx: ToolContext, assistance_case_id: str, invoice_id: str,
                                  discount_amount: float) -> str:
    """Book an approved financial-assistance award's discount on one patient invoice the award covers.
    One call records one discount line under the assistance case for that invoice, dated today, and adds
    the amount to the discount the case has granted so far; it does not post anything else and does not
    check the award, the invoice or the amount. After success the discount line is visible in the case's
    assistance activity and the case's running discount total includes it.

    Args:
        assistance_case_id: Id class — the reference number of the approved assistance case (the award)
            under which the discount is booked, as returned by the assistance-case lookup.
        invoice_id: Id class — the reference number of the patient invoice being discounted, as returned
            by the invoice lookup.
        discount_amount: Fixed-format class — the discount booked on the invoice, in USD, a positive
            amount with 2 decimal places, already rounded to the cent before the call.

    Returns:
        A text rendering of a dictionary with: status ("discount_booked" on success), discount_line_id
        (reference number of the new discount line), assistance_case_id and invoice_id (echoed reference
        numbers), discount_amount (USD, 2 decimal places, as booked), event_date (today, YYYY-MM-DD) and
        discount_granted_total (the case's running discount total after this line, USD, 2 decimal places).
    """
    amount = round(float(discount_amount), 2)
    today = ctx.now()[:10]
    rid = ctx.make_id("asd_", assistance_case_id, invoice_id, amount)
    case = ctx.find("assistance_cases", assistance_case_id=assistance_case_id)
    customer = case[0].get("customer_id") if case else None
    prior_total = float(case[0].get("discount_granted_total") or 0) if case else 0.0
    ctx.create("assistance_events", rid, assistance_event_id=rid, assistance_case_id=assistance_case_id,
               customer_id=customer, event_type="assistance_discount_applied", event_date=today,
               invoice_id=invoice_id, discount_amount=amount)
    new_total = round(prior_total + amount, 2)
    if case:
        ctx.update("assistance_cases", assistance_case_id, discount_granted_total=new_total)
    return str({"status": "discount_booked", "discount_line_id": rid, "assistance_case_id": assistance_case_id,
                "invoice_id": invoice_id, "discount_amount": amount, "event_date": today,
                "discount_granted_total": new_total})


@tool(owner="user", rw="write")
def submit_renewal_application_d691b1b8(ctx: ToolContext, customer_id: str, variant_name: str,
                                        household_size: int, annual_household_income: float,
                                        insurance_status: str) -> str:
    """The applicant submits, in person through the patient portal, a renewal application for financial
    assistance. One call opens one new assistance case for the applicant in the submitted status, received
    today through the online portal, at the tier the applicant selects, with the household size, annual
    household income and insurance status the applicant enters, no presumptive enrollment and nothing
    granted yet. After success the new case appears in the applicant's assistance cases with its own
    reference number.

    Args:
        customer_id: Id class — the applicant's customer reference number, as read from the profile lookup
            and given to the applicant.
        variant_name: Enum class — the assistance tier the renewal is assessed at, exactly one of:
            Financial Assistance 25% Discount when the renewal is assessed at the 25% income tier;
            Financial Assistance 50% Discount when it is assessed at the 50% income tier;
            Financial Assistance 75% Discount when it is assessed at the 75% income tier;
            Financial Assistance Full Discount when it is assessed at the full-discount income tier;
            Presumptive Eligibility Full Discount when it is assessed on a program enrollment;
            Catastrophic Medical Hardship Adjustment when it is assessed under the medical hardship adjustment.
        household_size: Fixed-format class — the number of people in the household as the applicant
            states it, a positive integer.
        annual_household_income: Fixed-format class — the annual household income the applicant states,
            in USD, with 2 decimal places.
        insurance_status: Enum class — whether the applicant has health coverage, exactly one of:
            uninsured when the applicant has no live health coverage; insured when the applicant has at
            least one live health coverage.

    Returns:
        A text rendering of a dictionary with: status ("submitted" on success), assistance_case_id
        (reference number of the new renewal case), customer_id (echoed), variant_name (tier recorded),
        application_date (today, YYYY-MM-DD) and application_channel ("online_portal").
    """
    today = ctx.now()[:10]
    income = round(float(annual_household_income), 2)
    size = int(household_size)
    rid = ctx.make_id("asc_", customer_id, variant_name, size, income, insurance_status, today)
    ctx.create("assistance_cases", rid, assistance_case_id=rid, customer_id=customer_id,
               variant_name=variant_name, status="submitted", application_date=today,
               application_channel="online_portal", household_size=size,
               annual_household_income=income, fpl_percent=None, insurance_status=insurance_status,
               presumptive_basis="none", documents_requested_date=None, documents_due_date=None,
               extension_count=0, documents_complete_date=None, decision_date=None,
               award_start_date=None, award_end_date=None, denial_reason=None,
               discount_granted_total=0.0, closed_date=None)
    return str({"status": "submitted", "assistance_case_id": rid, "customer_id": customer_id,
                "variant_name": variant_name, "application_date": today,
                "application_channel": "online_portal"})


@tool(owner="agent", rw="write")
def reassess_assistance_percent_a70c4477(ctx: ToolContext, assistance_case_id: str, fpl_percent: float,
                                         variant_name: str) -> str:
    """Record a reassessment of a financial-assistance case's percent of the federal poverty guideline and the
    tier that goes with it, while the case is still being decided. One call replaces the percent and the tier
    recorded on that case; the household size and the annual household income already recorded stay as they
    are, and nothing else is changed or checked. After success the case shows the new percent and tier.

    Args:
        assistance_case_id: Id class — the reference number of the assistance case being reassessed, as
            returned by the assistance-case lookup.
        fpl_percent: Fixed-format class — the reassessed percent of the federal poverty guideline, a percent
            with 1 decimal place (precision 0.1), already rounded to 1 decimal place before the call.
        variant_name: Enum class — the tier recorded with the reassessed percent, exactly one of:
            Financial Assistance 25% Discount when the percent falls in the 25% income band;
            Financial Assistance 50% Discount when it falls in the 50% income band;
            Financial Assistance 75% Discount when it falls in the 75% income band;
            Financial Assistance Full Discount when it falls in the full-discount income band;
            Presumptive Eligibility Full Discount when the case rests on a program enrollment;
            Catastrophic Medical Hardship Adjustment when the case is assessed under the medical hardship adjustment.

    Returns:
        A text rendering of a dictionary with: status ("reassessed" on success), assistance_case_id (echoed),
        fpl_percent (the percent now recorded, one decimal place) and variant_name (the tier now recorded).
    """
    pct = round(float(fpl_percent), 1)
    ctx.update("assistance_cases", assistance_case_id, fpl_percent=pct, variant_name=variant_name)
    return str({"status": "reassessed", "assistance_case_id": assistance_case_id, "fpl_percent": pct,
                "variant_name": variant_name})


@tool(owner="agent", rw="write")
def request_assistance_documents_a6db5abf(ctx: ToolContext, assistance_case_id: str, response_days: int) -> str:
    """Issue the documents request on a submitted financial-assistance application. One call records today
    as the date the missing documents were requested, records a documents due date that falls the given
    number of calendar days after today, and moves the case to pending documents; nothing else is checked or
    changed. After success the case shows its documents-requested date, its documents due date and the
    pending-documents status, and the applicant is sent the request.

    Args:
        assistance_case_id: Id class — the reference number of the assistance case the request is issued on,
            as returned by the assistance-case lookup.
        response_days: Fixed-format class — the number of calendar days from today (today counted as day 0) to
            the documents due date, a positive integer; the due date recorded is today's date moved forward by
            this many calendar days.

    Returns:
        A text rendering of a dictionary with: status ("documents_requested" on success), assistance_case_id
        (echoed), documents_requested_date (today, YYYY-MM-DD) and documents_due_date (YYYY-MM-DD).
    """
    def to_days(d):
        y, m, dd = int(d[0:4]), int(d[5:7]), int(d[8:10])
        y -= m <= 2
        era = (y if y >= 0 else y - 399) // 400
        yoe = y - era * 400
        doy = (153 * (m + (-3 if m > 2 else 9)) + 2) // 5 + dd - 1
        doe = yoe * 365 + yoe // 4 - yoe // 100 + doy
        return era * 146097 + doe - 719468

    def to_date(z):
        z += 719468
        era = (z if z >= 0 else z - 146096) // 146097
        doe = z - era * 146097
        yoe = (doe - doe // 1460 + doe // 36524 - doe // 146096) // 365
        y = yoe + era * 400
        doy = doe - (365 * yoe + yoe // 4 - yoe // 100)
        mp = (5 * doy + 2) // 153
        d = doy - (153 * mp + 2) // 5 + 1
        m = mp + (3 if mp < 10 else -9)
        y += m <= 2
        return f"{y:04d}-{m:02d}-{d:02d}"

    today = ctx.now()[:10]
    due = to_date(to_days(today) + int(response_days))
    ctx.update("assistance_cases", assistance_case_id, status="pending_documents",
               documents_requested_date=today, documents_due_date=due)
    return str({"status": "documents_requested", "assistance_case_id": assistance_case_id,
                "documents_requested_date": today, "documents_due_date": due})


@tool(owner="user", rw="write")
def request_document_extension_ca0bff0a(ctx: ToolContext, assistance_case_id: str, extension_days: int) -> str:
    """The applicant asks, on their own behalf, for an extension of the documents due date on their pending
    financial-assistance application. One call moves the case's documents due date forward by the given
    number of calendar days and adds one to the extensions granted on the case; nothing else is checked or
    changed. After success the applicant sees the new documents due date on the case.

    Args:
        assistance_case_id: Id class — the reference number of the applicant's assistance case, as given to the
            applicant by the agent from the assistance-case lookup.
        extension_days: Fixed-format class — the number of calendar days the documents due date moves forward,
            a positive integer, as given to the applicant by the agent.

    Returns:
        A text rendering of a dictionary with: status ("extension_recorded" on success), assistance_case_id
        (echoed), documents_due_date (the new due date, YYYY-MM-DD) and extension_count (extensions granted on
        the case after this one, an integer).
    """
    def to_days(d):
        y, m, dd = int(d[0:4]), int(d[5:7]), int(d[8:10])
        y -= m <= 2
        era = (y if y >= 0 else y - 399) // 400
        yoe = y - era * 400
        doy = (153 * (m + (-3 if m > 2 else 9)) + 2) // 5 + dd - 1
        doe = yoe * 365 + yoe // 4 - yoe // 100 + doy
        return era * 146097 + doe - 719468

    def to_date(z):
        z += 719468
        era = (z if z >= 0 else z - 146096) // 146097
        doe = z - era * 146097
        yoe = (doe - doe // 1460 + doe // 36524 - doe // 146096) // 365
        y = yoe + era * 400
        doy = doe - (365 * yoe + yoe // 4 - yoe // 100)
        mp = (5 * doy + 2) // 153
        d = doy - (153 * mp + 2) // 5 + 1
        m = mp + (3 if mp < 10 else -9)
        y += m <= 2
        return f"{y:04d}-{m:02d}-{d:02d}"

    rows = ctx.find("assistance_cases", assistance_case_id=assistance_case_id)
    current = (rows[0].get("documents_due_date") if rows else None) or ctx.now()[:10]
    count = int((rows[0].get("extension_count") if rows else 0) or 0) + 1
    new_due = to_date(to_days(str(current)) + int(extension_days))
    ctx.update("assistance_cases", assistance_case_id, documents_due_date=new_due, extension_count=count)
    return str({"status": "extension_recorded", "assistance_case_id": assistance_case_id,
                "documents_due_date": new_due, "extension_count": count})

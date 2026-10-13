"""Shared tools for env_0049_state_unemployment_insurance_agency (Lakeland Department of Workforce Security).

Always-visible tools reused by every difficulty: one record lookup per table (the customer
profile lookup doubles as the identity entry), the caller identity verification, and the
transfer to a human representative. Customer-originated writes live in each difficulty's
task_tools.py as hidden user tools, never here.
"""

from erlbench import ToolContext, tool


# --------------------------------------------------------------------------- identity entry

@tool(owner="agent", rw="read")
def find_customers(ctx: ToolContext, customer_id: str = "", name: str = "", phone_number: str = "",
                   email: str = "", mailing_zip: str = "") -> str:
    """Look up a customer profile to establish whose claim or employer account this contact is about.

    A profile belongs either to an individual claimant or to an employer registered for
    unemployment insurance tax. You can search by the customer reference number, or by what
    the caller can naturally tell you: the name on the profile (a claimant's legal name or an
    employer's registered business name), the phone number of record, the email address of
    record, or the ZIP code of the mailing address. Every criterion is optional; give whichever
    you have, and add another one if several profiles match. The profile returned shows the
    customer type, contact details, mailing address, the last four digits of the Social Security
    or Federal Employer Identification Number, the date of birth for claimants, and the date the
    profile was opened. Finding a profile does not verify the caller's identity.

    Args:
        customer_id: The customer reference number, if already known; leave "" otherwise.
        name: The claimant's legal name or the employer's registered business name as the caller states it; leave "" if not given.
        phone_number: The phone number the caller gives, 10 digits; leave "" if not given.
        email: The email address the caller gives; leave "" if not given.
        mailing_zip: The 5-digit ZIP code of the caller's mailing address; leave "" if not given.
    """
    match = {k: v for k, v in {"customer_id": customer_id, "name": name, "phone_number": phone_number,
                               "email": email, "mailing_zip": mailing_zip}.items() if v}
    if not match:
        return "Error: provide at least one reference number or profile detail to find the customer."
    rows = ctx.fuzzy_find("customers", **match)
    if not rows:
        return f"No customer matches {match}."
    if len(rows) > 1:
        return f"Error: {len(rows)} customers match {match}; ask for one more detail to tell them apart."
    return str(rows[0])


@tool(owner="agent", rw="write")
def verify_caller_identity(ctx: ToolContext, customer_id: str, phone_number: str = "", email: str = "",
                           tax_id_last4: str = "", date_of_birth: str = "", mailing_zip: str = "") -> str:
    """Verify that the caller is the customer on the profile, and record the outcome for this contact.

    No claim, payment, overpayment, appeal, withholding, tax account or charge information may be
    discussed or changed until the caller is verified. This tool performs the comparison itself:
    it checks each detail the caller states against the profile on file, counts the details that
    match, and verifies the caller only when at least 3 of them match. The customer reference
    number only tells the tool which profile to compare against and never counts as a match.
    Pass exactly what the caller said for each detail they gave, and leave the others "". If the
    first attempt falls short, ask for another detail and call again; once a caller is verified,
    that result stands for the rest of the contact.

    Args:
        customer_id: The customer reference number read from the profile lookup. Required; it selects the profile and is not a matching detail.
        phone_number: The phone number of record as the caller states it, 10 digits; leave "" if not stated.
        email: The email address of record as the caller states it; leave "" if not stated.
        tax_id_last4: The last four digits of the caller's Social Security number (claimants) or of the employer's Federal Employer Identification Number (employers), as stated; leave "" if not stated.
        date_of_birth: The claimant's date of birth as stated, in YYYY-MM-DD form; employers have none; leave "" if not stated.
        mailing_zip: The 5-digit ZIP code of the mailing address of record as stated; leave "" if not stated.
    """
    if not customer_id:
        return "Error: customer_id is required; look the customer up first and pass their reference number."
    rows = ctx.find("customers", customer_id=customer_id)
    if not rows:
        return f"Error: no customer {customer_id}; cannot verify."
    rec = rows[0]
    # The tool owns the comparison; the locator customer_id never counts toward the match.
    supplied = {"phone_number": phone_number, "email": email, "tax_id_last4": tax_id_last4,
                "date_of_birth": date_of_birth, "mailing_zip": mailing_zip}
    matched = sum(1 for field, value in supplied.items()
                  if value and str(rec.get(field) or "").strip().lower() == str(value).strip().lower())
    verified = matched >= 3
    rid = ctx.make_id("cv_", customer_id)
    # Store only the reproducible boolean; upsert and never downgrade a prior pass.
    prior = ctx.find("caller_verifications", verification_id=rid)
    verified = verified or bool(prior and prior[0].get("verified"))
    if prior:
        ctx.update("caller_verifications", rid, verified=verified, verified_at=ctx.now())
    else:
        ctx.create("caller_verifications", rid, verification_id=rid, customer_id=customer_id,
                   verified=verified, verified_at=ctx.now())
    if verified:
        return f"Identity verified for {customer_id} ({matched} detail(s) matched on this attempt)."
    return (f"Identity NOT verified for {customer_id}: only {matched} of the required 3 details matched. "
            "Ask the caller for another detail on file and try again.")


@tool(owner="agent", rw="write")
def transfer_to_human_agent(ctx: ToolContext, customer_id: str, reason: str) -> str:
    """Transfer the customer to a human representative of the Department and record the transfer.

    Use it in one of two situations only: no published policy lets you resolve what the customer
    is asking for, or the customer has explicitly asked to speak with a human representative at
    least 2 times during this contact. The reason is recorded with the transfer.

    Args:
        customer_id: The customer reference number read from the profile lookup; the profile must exist.
        reason: Exactly one of two values, never free text. POLICY_NOT_COVERED - no published policy can resolve the request. CUSTOMER_REQUESTED - the customer has explicitly asked for a human representative at least 2 times.
    """
    allowed = {"POLICY_NOT_COVERED", "CUSTOMER_REQUESTED"}
    if reason not in allowed:
        return f"Error: unknown transfer reason '{reason}'. Valid: {', '.join(sorted(allowed))}."
    if not ctx.find("customers", customer_id=customer_id):
        return f"Error: no customer {customer_id}; cannot record the transfer."
    rid = ctx.make_id("hof_", customer_id, reason)
    ctx.create("handoffs", rid, handoff_id=rid, customer_id=customer_id, reason=reason, created_at=ctx.now())
    return f"Transfer to a human representative recorded for {customer_id} ({reason})."


@tool(owner="agent", rw="read")
def find_caller_verifications(ctx: ToolContext, verification_id: str = "", customer_id: str = "") -> str:
    """Check whether a caller has already been verified for a customer during this contact.

    Returns the verification record (whether verification passed and when it was last attempted)
    for the customer reference number given. Every criterion is optional.

    Args:
        verification_id: The reference number of the verification record; leave "" if unknown.
        customer_id: The customer reference number whose verification you want to see; leave "" if unknown.
    """
    match = {k: v for k, v in {"verification_id": verification_id, "customer_id": customer_id}.items() if v}
    rows = ctx.find("caller_verifications", **match)
    return str(rows) if rows else f"No verification on record for {match}."


@tool(owner="agent", rw="read")
def find_handoffs(ctx: ToolContext, handoff_id: str = "", customer_id: str = "") -> str:
    """Look up transfers to a human representative already recorded for a customer.

    Each record shows the reason given and when the transfer was recorded. Every criterion is optional.

    Args:
        handoff_id: The reference number of the transfer record; leave "" if unknown.
        customer_id: The customer reference number; leave "" if unknown.
    """
    match = {k: v for k, v in {"handoff_id": handoff_id, "customer_id": customer_id}.items() if v}
    rows = ctx.find("handoffs", **match)
    return str(rows) if rows else f"No transfer records for {match}."


# --------------------------------------------------------------------------- claims

@tool(owner="agent", rw="read")
def find_claims(ctx: ToolContext, claim_id: str = "", customer_id: str = "",
                separating_employer_account_id: str = "", parent_claim_id: str = "") -> str:
    """Look up unemployment benefit claims.

    A claim record shows the program it was filed under, its status, filing and effective dates,
    benefit year end date, base period and wages, weekly benefit amount, dependency allowance,
    maximum benefit amount and remaining balance, the latest monetary determination, the reported
    separation, any recall date, approved training, any hold and its reason, and the payment
    method in force. Search by the claim reference number, by the claimant's customer reference
    number to list all of their claims, by the separating employer's account reference number, or
    by the reference number of a claim that an Extended Benefits or Trade Readjustment Allowances
    claim extends. Every criterion is optional.

    Args:
        claim_id: The claim reference number; leave "" if unknown.
        customer_id: The claimant's customer reference number; leave "" if unknown.
        separating_employer_account_id: The tax account reference number of the claimant's separating employer; leave "" if unknown.
        parent_claim_id: The reference number of the exhausted claim that an extension claim continues; leave "" if unknown.
    """
    match = {k: v for k, v in {"claim_id": claim_id, "customer_id": customer_id,
                               "separating_employer_account_id": separating_employer_account_id,
                               "parent_claim_id": parent_claim_id}.items() if v}
    rows = ctx.find("claims", **match)
    return str(rows) if rows else f"No claims for {match}."


@tool(owner="agent", rw="read")
def find_claim_certifications(ctx: ToolContext, certification_id: str = "", claim_id: str = "",
                              customer_id: str = "") -> str:
    """Look up the weekly certifications a claimant filed.

    Each certification shows the week ending date, when and how it was filed, whether it was
    timely, the able-and-available and refusal-of-work answers, earnings and hours reported,
    work-search contacts, and any vacation, holiday, severance or pension pay reported.
    Every criterion is optional.

    Args:
        certification_id: The reference number of one certification; leave "" if unknown.
        claim_id: The claim reference number, to list every week certified on it; leave "" if unknown.
        customer_id: The claimant's customer reference number; leave "" if unknown.
    """
    match = {k: v for k, v in {"certification_id": certification_id, "claim_id": claim_id,
                               "customer_id": customer_id}.items() if v}
    rows = ctx.find("claim_certifications", **match)
    return str(rows) if rows else f"No certifications for {match}."


@tool(owner="agent", rw="read")
def find_claim_ledger(ctx: ToolContext, ledger_entry_id: str = "", claim_id: str = "", customer_id: str = "",
                      original_payment_id: str = "") -> str:
    """Look up the payment history and entitlement entries of a claim.

    Entries cover entitlement credited or reduced by monetary determinations, waiting weeks served,
    benefit payments (weekly, supplemental and reissued) with their earnings and other-pay
    deductions, overpayment offsets, withholding flags, charge codes and payment method, and
    cancelled payments with their reason. Search by an entry's reference number, by claim, by
    claimant, or by the reference number of an original payment to find its cancellation or reissue.
    Every criterion is optional.

    Args:
        ledger_entry_id: The reference number of one entry or payment; leave "" if unknown.
        claim_id: The claim reference number; leave "" if unknown.
        customer_id: The claimant's customer reference number; leave "" if unknown.
        original_payment_id: The reference number of an original payment, to find the cancellation or reissue that refers to it; leave "" if unknown.
    """
    match = {k: v for k, v in {"ledger_entry_id": ledger_entry_id, "claim_id": claim_id,
                               "customer_id": customer_id, "original_payment_id": original_payment_id}.items() if v}
    rows = ctx.find("claim_ledger", **match)
    return str(rows) if rows else f"No claim ledger entries for {match}."


@tool(owner="agent", rw="read")
def find_claim_tax_statements(ctx: ToolContext, statement_id: str = "", claim_id: str = "",
                              customer_id: str = "") -> str:
    """Look up Form 1099-G statements issued for a claim.

    Each statement shows the tax year, issue date, benefits paid (Box 1), federal income tax
    withheld (Box 4), state income tax withheld (Box 11), and whether it is the original statement
    or a correction and why. Every criterion is optional.

    Args:
        statement_id: The reference number of one statement; leave "" if unknown.
        claim_id: The claim reference number; leave "" if unknown.
        customer_id: The claimant's customer reference number; leave "" if unknown.
    """
    match = {k: v for k, v in {"statement_id": statement_id, "claim_id": claim_id,
                               "customer_id": customer_id}.items() if v}
    rows = ctx.find("claim_tax_statements", **match)
    return str(rows) if rows else f"No Form 1099-G statements for {match}."


@tool(owner="agent", rw="read")
def find_claim_requests(ctx: ToolContext, request_id: str = "", claim_id: str = "", customer_id: str = "") -> str:
    """Look up requests a claimant has lodged on a claim.

    Requests are claim withdrawals, backdating requests and late-certification requests; each shows
    the dates asked for, the good cause stated and the outcome so far. Every criterion is optional.

    Args:
        request_id: The reference number of one request; leave "" if unknown.
        claim_id: The claim reference number; leave "" if unknown.
        customer_id: The claimant's customer reference number; leave "" if unknown.
    """
    match = {k: v for k, v in {"request_id": request_id, "claim_id": claim_id,
                               "customer_id": customer_id}.items() if v}
    rows = ctx.find("claim_requests", **match)
    return str(rows) if rows else f"No claim requests for {match}."


# --------------------------------------------------------------------------- identity verification cases

@tool(owner="agent", rw="read")
def find_idv_cases(ctx: ToolContext, idv_case_id: str = "", customer_id: str = "", claim_id: str = "") -> str:
    """Look up identity verification cases opened for claims.

    A case shows the proofing pathway, its status, the notice date and verification deadline,
    extensions granted, and the verified or closed date. Search by case, by claimant or by claim.
    Every criterion is optional.

    Args:
        idv_case_id: The reference number of the verification case; leave "" if unknown.
        customer_id: The claimant's customer reference number; leave "" if unknown.
        claim_id: The claim reference number; leave "" if unknown.
    """
    match = {k: v for k, v in {"idv_case_id": idv_case_id, "customer_id": customer_id,
                               "claim_id": claim_id}.items() if v}
    rows = ctx.find("idv_cases", **match)
    return str(rows) if rows else f"No identity verification cases for {match}."


@tool(owner="agent", rw="read")
def find_idv_events(ctx: ToolContext, idv_event_id: str = "", idv_case_id: str = "", customer_id: str = "") -> str:
    """Look up the activity on identity verification cases.

    Activity covers proofing attempts and their results, documents received with their role and
    review result, and appointments booked or missed. Every criterion is optional.

    Args:
        idv_event_id: The reference number of one activity record; leave "" if unknown.
        idv_case_id: The verification case reference number; leave "" if unknown.
        customer_id: The claimant's customer reference number; leave "" if unknown.
    """
    match = {k: v for k, v in {"idv_event_id": idv_event_id, "idv_case_id": idv_case_id,
                               "customer_id": customer_id}.items() if v}
    rows = ctx.find("idv_events", **match)
    return str(rows) if rows else f"No identity verification activity for {match}."


# --------------------------------------------------------------------------- overpayments

@tool(owner="agent", rw="read")
def find_overpayments(ctx: ToolContext, overpayment_id: str = "", customer_id: str = "", claim_id: str = "") -> str:
    """Look up benefit overpayments a claimant owes.

    An overpayment shows its classification, status, determination date, the overpaid weeks and
    cause, the principal established, the balance still due, any fraud penalty weeks, the repayment
    plan, and referral for tax refund offset. Search by overpayment, by claimant or by the claim it
    was established on. Every criterion is optional.

    Args:
        overpayment_id: The overpayment reference number; leave "" if unknown.
        customer_id: The claimant's customer reference number; leave "" if unknown.
        claim_id: The claim reference number; leave "" if unknown.
    """
    match = {k: v for k, v in {"overpayment_id": overpayment_id, "customer_id": customer_id,
                               "claim_id": claim_id}.items() if v}
    rows = ctx.find("overpayments", **match)
    return str(rows) if rows else f"No overpayments for {match}."


@tool(owner="agent", rw="read")
def find_overpay_ledger(ctx: ToolContext, overpay_entry_id: str = "", overpayment_id: str = "", customer_id: str = "",
                        source_payment_id: str = "", waiver_request_id: str = "", appeal_id: str = "") -> str:
    """Look up the balance history of overpayments.

    Entries cover principal, penalty, interest and fees assessed; repayments, benefit offsets and
    tax refund intercepts applied; returned repayments; waiver, cancellation and write-off
    adjustments; and refunds. Search by entry, overpayment or claimant, by the benefit payment an
    offset came from, by the waiver request behind an adjustment, or by the appeal behind a
    cancellation. Every criterion is optional.

    Args:
        overpay_entry_id: The reference number of one entry; leave "" if unknown.
        overpayment_id: The overpayment reference number; leave "" if unknown.
        customer_id: The claimant's customer reference number; leave "" if unknown.
        source_payment_id: The benefit payment reference number an offset was taken from; leave "" if unknown.
        waiver_request_id: The waiver request reference number; leave "" if unknown.
        appeal_id: The appeal reference number behind a cancellation; leave "" if unknown.
    """
    match = {k: v for k, v in {"overpay_entry_id": overpay_entry_id, "overpayment_id": overpayment_id,
                               "customer_id": customer_id, "source_payment_id": source_payment_id,
                               "waiver_request_id": waiver_request_id, "appeal_id": appeal_id}.items() if v}
    rows = ctx.find("overpay_ledger", **match)
    return str(rows) if rows else f"No overpayment entries for {match}."


@tool(owner="agent", rw="read")
def find_overpay_waiver_requests(ctx: ToolContext, waiver_request_id: str = "", overpayment_id: str = "",
                                 customer_id: str = "") -> str:
    """Look up overpayment waiver requests lodged by claimants.

    Each request shows the date received, the household size and annual household income stated,
    and its outcome. Every criterion is optional.

    Args:
        waiver_request_id: The waiver request reference number; leave "" if unknown.
        overpayment_id: The overpayment reference number; leave "" if unknown.
        customer_id: The claimant's customer reference number; leave "" if unknown.
    """
    match = {k: v for k, v in {"waiver_request_id": waiver_request_id, "overpayment_id": overpayment_id,
                               "customer_id": customer_id}.items() if v}
    rows = ctx.find("overpay_waiver_requests", **match)
    return str(rows) if rows else f"No waiver requests for {match}."


# --------------------------------------------------------------------------- withholding and deduction orders

@tool(owner="agent", rw="read")
def find_withholding_orders(ctx: ToolContext, withholding_order_id: str = "", customer_id: str = "",
                            claim_id: str = "") -> str:
    """Look up income tax withholding elections and child support or SNAP deduction orders.

    Each record shows the kind of election or order, its status, the dates received and effective,
    the IV-D case or SNAP claim number, the weekly or certified amount, and the end date.
    Every criterion is optional.

    Args:
        withholding_order_id: The reference number of the election or order; leave "" if unknown.
        customer_id: The claimant's customer reference number; leave "" if unknown.
        claim_id: The claim reference number; leave "" if unknown.
    """
    match = {k: v for k, v in {"withholding_order_id": withholding_order_id, "customer_id": customer_id,
                               "claim_id": claim_id}.items() if v}
    rows = ctx.find("withholding_orders", **match)
    return str(rows) if rows else f"No withholding elections or orders for {match}."


@tool(owner="agent", rw="read")
def find_withholding_ledger(ctx: ToolContext, withholding_entry_id: str = "", withholding_order_id: str = "",
                            customer_id: str = "", source_payment_id: str = "", original_deduction_id: str = "") -> str:
    """Look up deductions taken or skipped from benefit payments, remittances and refunds.

    Search by entry, by election or order, by claimant, by the benefit payment a deduction came
    from, or by the deduction a refund repays. Every criterion is optional.

    Args:
        withholding_entry_id: The reference number of one entry; leave "" if unknown.
        withholding_order_id: The election or order reference number; leave "" if unknown.
        customer_id: The claimant's customer reference number; leave "" if unknown.
        source_payment_id: The benefit payment reference number; leave "" if unknown.
        original_deduction_id: The reference number of a deduction that was refunded; leave "" if unknown.
    """
    match = {k: v for k, v in {"withholding_entry_id": withholding_entry_id,
                               "withholding_order_id": withholding_order_id, "customer_id": customer_id,
                               "source_payment_id": source_payment_id,
                               "original_deduction_id": original_deduction_id}.items() if v}
    rows = ctx.find("withholding_ledger", **match)
    return str(rows) if rows else f"No withholding entries for {match}."


@tool(owner="agent", rw="read")
def find_withholding_requests(ctx: ToolContext, withholding_request_id: str = "", customer_id: str = "",
                              claim_id: str = "", withholding_order_id: str = "") -> str:
    """Look up a claimant's requests to start or stop voluntary income tax withholding.

    Each request shows the kind of request, the date received and its status. Every criterion is optional.

    Args:
        withholding_request_id: The request reference number; leave "" if unknown.
        customer_id: The claimant's customer reference number; leave "" if unknown.
        claim_id: The claim reference number; leave "" if unknown.
        withholding_order_id: The election a stop request concerns; leave "" if unknown.
    """
    match = {k: v for k, v in {"withholding_request_id": withholding_request_id, "customer_id": customer_id,
                               "claim_id": claim_id, "withholding_order_id": withholding_order_id}.items() if v}
    rows = ctx.find("withholding_requests", **match)
    return str(rows) if rows else f"No withholding requests for {match}."


# --------------------------------------------------------------------------- appeals

@tool(owner="agent", rw="read")
def find_appeals(ctx: ToolContext, appeal_id: str = "", customer_id: str = "", determination_record_id: str = "",
                 claim_id: str = "", employer_account_id: str = "", parent_appeal_id: str = "") -> str:
    """Look up appeals filed by claimants or employers.

    An appeal shows its docket, status, the appellant's role, what was appealed and when it was
    mailed, the filing date and channel, any late-filing reason, the hearing date, the decision
    outcome and mailing date, and any dismissal reason. Search by appeal (docket number), by
    appellant, by the reference number of the appealed record (a claim, overpayment, charge
    position, employer account or lower appeal), by claim, by employer account, or by the lower
    appeal a Board of Review appeal follows. Every criterion is optional.

    Args:
        appeal_id: The appeal docket reference number; leave "" if unknown.
        customer_id: The appellant's customer reference number; leave "" if unknown.
        determination_record_id: The reference number of the appealed record; leave "" if unknown.
        claim_id: The claim reference number; leave "" if unknown.
        employer_account_id: The employer tax account reference number; leave "" if unknown.
        parent_appeal_id: The lower appeal a Board of Review appeal follows; leave "" if unknown.
    """
    match = {k: v for k, v in {"appeal_id": appeal_id, "customer_id": customer_id,
                               "determination_record_id": determination_record_id, "claim_id": claim_id,
                               "employer_account_id": employer_account_id,
                               "parent_appeal_id": parent_appeal_id}.items() if v}
    rows = ctx.find("appeals", **match)
    return str(rows) if rows else f"No appeals for {match}."


@tool(owner="agent", rw="read")
def find_appeal_events(ctx: ToolContext, appeal_event_id: str = "", appeal_id: str = "", customer_id: str = "") -> str:
    """Look up hearing settings, postponement decisions, exhibits and interpreter requests on appeals.

    Every criterion is optional.

    Args:
        appeal_event_id: The reference number of one activity record; leave "" if unknown.
        appeal_id: The appeal docket reference number; leave "" if unknown.
        customer_id: The appellant's customer reference number; leave "" if unknown.
    """
    match = {k: v for k, v in {"appeal_event_id": appeal_event_id, "appeal_id": appeal_id,
                               "customer_id": customer_id}.items() if v}
    rows = ctx.find("appeal_events", **match)
    return str(rows) if rows else f"No appeal activity for {match}."


@tool(owner="agent", rw="read")
def find_appeal_requests(ctx: ToolContext, appeal_request_id: str = "", appeal_id: str = "", customer_id: str = "") -> str:
    """Look up withdrawal, reopening, postponement and subpoena requests made on appeals.

    Each request shows its type, the date received, the reason stated and its status.
    Every criterion is optional.

    Args:
        appeal_request_id: The request reference number; leave "" if unknown.
        appeal_id: The appeal docket reference number; leave "" if unknown.
        customer_id: The requesting party's customer reference number; leave "" if unknown.
    """
    match = {k: v for k, v in {"appeal_request_id": appeal_request_id, "appeal_id": appeal_id,
                               "customer_id": customer_id}.items() if v}
    rows = ctx.find("appeal_requests", **match)
    return str(rows) if rows else f"No appeal requests for {match}."


# --------------------------------------------------------------------------- employer tax accounts

@tool(owner="agent", rw="read")
def find_employer_accounts(ctx: ToolContext, employer_account_id: str = "", customer_id: str = "",
                           predecessor_account_id: str = "") -> str:
    """Look up employer unemployment insurance tax accounts.

    An account shows its financing class, status, state account number, entity type and industry
    code, registration and liability dates, the contribution rate and rate year with the reserve
    ratio and rate notice date, average taxable payroll, the balance due and reserve balance, any
    experience transferred in, and inactivation or closure dates. Search by account, by the
    employer's customer reference number, or by a predecessor account whose experience was
    transferred. Every criterion is optional.

    Args:
        employer_account_id: The employer tax account reference number; leave "" if unknown.
        customer_id: The employer's customer reference number; leave "" if unknown.
        predecessor_account_id: The reference number of a predecessor account; leave "" if unknown.
    """
    match = {k: v for k, v in {"employer_account_id": employer_account_id, "customer_id": customer_id,
                               "predecessor_account_id": predecessor_account_id}.items() if v}
    rows = ctx.find("employer_accounts", **match)
    return str(rows) if rows else f"No employer accounts for {match}."


@tool(owner="agent", rw="read")
def find_employer_wage_reports(ctx: ToolContext, wage_report_id: str = "", employer_account_id: str = "",
                               customer_id: str = "") -> str:
    """Look up quarterly contribution and wage reports filed by employers.

    Each report shows the quarter, whether it is original, amended or final, filing and due dates,
    channel, total, excess and taxable wages, and the monthly employee counts. Every criterion is optional.

    Args:
        wage_report_id: The reference number of one report; leave "" if unknown.
        employer_account_id: The employer tax account reference number; leave "" if unknown.
        customer_id: The employer's customer reference number; leave "" if unknown.
    """
    match = {k: v for k, v in {"wage_report_id": wage_report_id, "employer_account_id": employer_account_id,
                               "customer_id": customer_id}.items() if v}
    rows = ctx.find("employer_wage_reports", **match)
    return str(rows) if rows else f"No wage reports for {match}."


@tool(owner="agent", rw="read")
def find_employer_tax_ledger(ctx: ToolContext, tax_entry_id: str = "", employer_account_id: str = "",
                             customer_id: str = "", predecessor_account_id: str = "", successor_account_id: str = "",
                             account_request_id: str = "") -> str:
    """Look up the balance and reserve history of employer tax accounts.

    Entries cover contributions assessed, reimbursement bills, late report penalties, interest,
    payments, credits and refunds, reserve credits, voluntary contributions, benefit charges
    posted to the reserve, and reserve transfers between predecessor and successor. Search by
    entry, account or employer, by the other account of a reserve transfer, or by the request a
    refund was paid against. Every criterion is optional.

    Args:
        tax_entry_id: The reference number of one entry; leave "" if unknown.
        employer_account_id: The employer tax account reference number; leave "" if unknown.
        customer_id: The employer's customer reference number; leave "" if unknown.
        predecessor_account_id: The predecessor account of a reserve transfer in; leave "" if unknown.
        successor_account_id: The successor account of a reserve transfer out; leave "" if unknown.
        account_request_id: The employer request a refund was paid against; leave "" if unknown.
    """
    match = {k: v for k, v in {"tax_entry_id": tax_entry_id, "employer_account_id": employer_account_id,
                               "customer_id": customer_id, "predecessor_account_id": predecessor_account_id,
                               "successor_account_id": successor_account_id,
                               "account_request_id": account_request_id}.items() if v}
    rows = ctx.find("employer_tax_ledger", **match)
    return str(rows) if rows else f"No tax account entries for {match}."


@tool(owner="agent", rw="read")
def find_employer_account_requests(ctx: ToolContext, account_request_id: str = "", employer_account_id: str = "",
                                   customer_id: str = "") -> str:
    """Look up requests an employer has made on its tax account.

    Requests are account closures, refunds of a credit balance, penalty abatements, reimbursing
    financing elections or terminations, and experience transfers; each shows the date, quarter,
    amount asked for and status. Every criterion is optional.

    Args:
        account_request_id: The request reference number; leave "" if unknown.
        employer_account_id: The employer tax account reference number; leave "" if unknown.
        customer_id: The employer's customer reference number; leave "" if unknown.
    """
    match = {k: v for k, v in {"account_request_id": account_request_id,
                               "employer_account_id": employer_account_id, "customer_id": customer_id}.items() if v}
    rows = ctx.find("employer_account_requests", **match)
    return str(rows) if rows else f"No employer account requests for {match}."


# --------------------------------------------------------------------------- employer benefit charging

@tool(owner="agent", rw="read")
def find_charge_positions(ctx: ToolContext, charge_position_id: str = "", customer_id: str = "",
                          employer_account_id: str = "", claim_id: str = "") -> str:
    """Look up an employer's chargeable positions on claims.

    A position shows the employer's charge class on the claim, its status, when the notice of claim
    was mailed and the response was due and received, the separation reason the employer reported,
    the base-period wages it paid and its charge share, the total charged, and any relief or protest.
    Search by position, by employer, by employer account, or by claim to see every employer charged
    on it. Every criterion is optional.

    Args:
        charge_position_id: The charge position reference number; leave "" if unknown.
        customer_id: The employer's customer reference number; leave "" if unknown.
        employer_account_id: The employer tax account reference number; leave "" if unknown.
        claim_id: The claim reference number; leave "" if unknown.
    """
    match = {k: v for k, v in {"charge_position_id": charge_position_id, "customer_id": customer_id,
                               "employer_account_id": employer_account_id, "claim_id": claim_id}.items() if v}
    rows = ctx.find("charge_positions", **match)
    return str(rows) if rows else f"No charge positions for {match}."


@tool(owner="agent", rw="read")
def find_charge_ledger(ctx: ToolContext, charge_entry_id: str = "", charge_position_id: str = "", customer_id: str = "",
                       source_payment_id: str = "", source_charge_id: str = "") -> str:
    """Look up benefit charges, credits and statements of charges on employer positions.

    Search by entry, by position, by employer, by the benefit payment a charge came from, or by the
    charge a credit reduces. Every criterion is optional.

    Args:
        charge_entry_id: The reference number of one entry; leave "" if unknown.
        charge_position_id: The charge position reference number; leave "" if unknown.
        customer_id: The employer's customer reference number; leave "" if unknown.
        source_payment_id: The benefit payment reference number; leave "" if unknown.
        source_charge_id: The reference number of a posted charge, to find credits against it; leave "" if unknown.
    """
    match = {k: v for k, v in {"charge_entry_id": charge_entry_id, "charge_position_id": charge_position_id,
                               "customer_id": customer_id, "source_payment_id": source_payment_id,
                               "source_charge_id": source_charge_id}.items() if v}
    rows = ctx.find("charge_ledger", **match)
    return str(rows) if rows else f"No charge entries for {match}."


@tool(owner="agent", rw="read")
def find_charge_requests(ctx: ToolContext, charge_request_id: str = "", charge_position_id: str = "",
                         customer_id: str = "") -> str:
    """Look up separation responses and charge protests an employer has submitted.

    Each submission shows its type, the date received, the separation reason or protest ground
    stated, the statement quarter for a protest, and its status. Every criterion is optional.

    Args:
        charge_request_id: The submission reference number; leave "" if unknown.
        charge_position_id: The charge position reference number; leave "" if unknown.
        customer_id: The employer's customer reference number; leave "" if unknown.
    """
    match = {k: v for k, v in {"charge_request_id": charge_request_id, "charge_position_id": charge_position_id,
                               "customer_id": customer_id}.items() if v}
    rows = ctx.find("charge_requests", **match)
    return str(rows) if rows else f"No charge submissions for {match}."

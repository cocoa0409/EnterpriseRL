"""Shared tools for env_0064_reverse_mortgage_lender (Cedarline Reverse Mortgage, LLC).

Share tools are always present in their owner's tool list. This module holds the three
foundations every difficulty reuses: one record finder per table (the customers finder doubles
as the identity entry), the identity-verification write, and the transfer to a human
representative. Customer-originated writes live as hidden task tools in each difficulty.
"""

from erlbench import ToolContext, tool


def _report(rows, label, match):
    # Shared formatting for every finder (not a tool; never touches the database).
    return str(rows) if rows else f"No {label} found for {match}."


@tool(owner="agent", rw="read")
def find_customers(ctx: ToolContext, customer_id: str = "", linked_customer_id: str = "",
                   full_name: str = "", phone_number: str = "", email: str = "") -> str:
    """Look up a customer profile to establish whose account this call concerns.

    A profile may belong to a borrower, a non-borrowing spouse, a confirmed successor in interest
    (an heir, executor or trustee) or a third party the borrower authorized. You can search by the
    customer reference number, by the reference number of the borrower a person is linked to, or by
    what the caller can naturally tell you: full name, phone number or email address. Every
    criterion is optional; supply whichever you have. The profile returned shows the person's
    capacity, linked borrower, date of birth, contact details, the last four digits of the Social
    Security number, the property ZIP code, mailing address and the date the profile was opened.
    Finding a profile does not verify the caller's identity.

    Args:
        customer_id: Customer reference number; leave "" if unknown.
        linked_customer_id: Reference number of the borrower this person is linked to, to list the spouses, successors and authorized parties of a borrower; leave "" if unknown.
        full_name: Full legal name as the caller states it; leave "" if not given.
        phone_number: Phone number as the caller states it (10 digits); leave "" if not given.
        email: Email address as the caller states it; leave "" if not given.
    """
    match = {k: v for k, v in {"customer_id": customer_id, "linked_customer_id": linked_customer_id,
                               "full_name": full_name, "phone_number": phone_number,
                               "email": email}.items() if v}
    if not match:
        return "Error: provide at least one reference number or profile detail to find a customer."
    rows = ctx.fuzzy_find("customers", **match)
    if not rows:
        return f"No customer matches {match}."
    if len(rows) > 1 and not linked_customer_id:
        return (f"Error: {len(rows)} customers match {match}; ask the caller for one more detail "
                f"to tell them apart.")
    return str(rows if len(rows) > 1 else rows[0])


@tool(owner="agent", rw="read")
def find_hecm_loans(ctx: ToolContext, hecm_loan_id: str = "", customer_id: str = "",
                    co_borrower_customer_id: str = "", nbs_customer_id: str = "") -> str:
    """Look up Home Equity Conversion Mortgage (HECM) loans.

    Returns each matching loan's payout plan, status, loan and FHA case numbers, closing and funding
    dates, rate type and rates, maximum claim amount, principal limit and first-year disbursement
    figures, current balance and available line, scheduled payment terms, servicing fee option,
    property type and any due-and-payable, deferral or termination dates. Search by any reference
    number you hold; every criterion is optional.

    Args:
        hecm_loan_id: Reference number of the HECM loan; leave "" if unknown.
        customer_id: Reference number of the primary borrower; leave "" if unknown.
        co_borrower_customer_id: Reference number of a second borrower on the note; leave "" if unknown.
        nbs_customer_id: Reference number of the non-borrowing spouse named on the loan; leave "" if unknown.
    """
    match = {k: v for k, v in {"hecm_loan_id": hecm_loan_id, "customer_id": customer_id,
                               "co_borrower_customer_id": co_borrower_customer_id,
                               "nbs_customer_id": nbs_customer_id}.items() if v}
    return _report(ctx.find("hecm_loans", **match), "HECM loans", match)


@tool(owner="agent", rw="read")
def find_hecm_transactions(ctx: ToolContext, hecm_txn_id: str = "", hecm_loan_id: str = "",
                           customer_id: str = "", hecm_request_id: str = "") -> str:
    """Look up the transaction history of HECM loans.

    Returns line-of-credit draws and their balance postings, scheduled payments, monthly interest,
    mortgage insurance premium and servicing fee postings, line growth credits, prepayment
    allocations and line restorations, returned draws and reversals, plan change fees and line
    commitments or releases, each with its amount, dates, period and originating reference. Search
    by any reference number you hold; every criterion is optional.

    Args:
        hecm_txn_id: Reference number of one transaction; leave "" if unknown.
        hecm_loan_id: Reference number of the HECM loan; leave "" if unknown.
        customer_id: Reference number of the primary borrower; leave "" if unknown.
        hecm_request_id: Reference number of the borrower request a transaction carried out; leave "" if unknown.
    """
    match = {k: v for k, v in {"hecm_txn_id": hecm_txn_id, "hecm_loan_id": hecm_loan_id,
                               "customer_id": customer_id,
                               "hecm_request_id": hecm_request_id}.items() if v}
    return _report(ctx.find("hecm_transactions", **match), "HECM transactions", match)


@tool(owner="agent", rw="read")
def find_hecm_requests(ctx: ToolContext, hecm_request_id: str = "", customer_id: str = "",
                       hecm_loan_id: str = "") -> str:
    """Look up borrower requests on HECM loans: draw requests, payout plan change requests and rescission notices.

    Each request shows the amount or plan requested, the term, the disbursement method, the channel
    it came through, the date received, its processing status and any decline reason. Search by
    any reference number you hold; every criterion is optional.

    Args:
        hecm_request_id: Reference number of the request; leave "" if unknown.
        customer_id: Reference number of the borrower who submitted it; leave "" if unknown.
        hecm_loan_id: Reference number of the HECM loan; leave "" if unknown.
    """
    match = {k: v for k, v in {"hecm_request_id": hecm_request_id, "customer_id": customer_id,
                               "hecm_loan_id": hecm_loan_id}.items() if v}
    return _report(ctx.find("hecm_requests", **match), "HECM requests", match)


@tool(owner="agent", rw="read")
def find_jumbo_loans(ctx: ToolContext, jumbo_loan_id: str = "", customer_id: str = "",
                     co_borrower_customer_id: str = "") -> str:
    """Look up Cedarline Summit proprietary reverse mortgages.

    Returns each loan's Summit plan, status, loan number, closing and funding dates, note rate,
    principal limit, appraised value, current balance and undrawn line, draw period end date,
    property state and any due-and-payable or termination date. Search by any reference number you
    hold; every criterion is optional.

    Args:
        jumbo_loan_id: Reference number of the Summit loan; leave "" if unknown.
        customer_id: Reference number of the primary borrower; leave "" if unknown.
        co_borrower_customer_id: Reference number of a second borrower; leave "" if unknown.
    """
    match = {k: v for k, v in {"jumbo_loan_id": jumbo_loan_id, "customer_id": customer_id,
                               "co_borrower_customer_id": co_borrower_customer_id}.items() if v}
    return _report(ctx.find("jumbo_loans", **match), "Summit loans", match)


@tool(owner="agent", rw="read")
def find_jumbo_transactions(ctx: ToolContext, jumbo_txn_id: str = "", jumbo_loan_id: str = "",
                            customer_id: str = "") -> str:
    """Look up the transaction history of Summit loans.

    Returns draws, balance postings for draws, reserve payments and advances, monthly interest,
    line growth, prepayments and restorations and the cancellation of an undrawn line, each with
    its amount, dates and originating reference. Search by any reference number you hold; every
    criterion is optional.

    Args:
        jumbo_txn_id: Reference number of one transaction; leave "" if unknown.
        jumbo_loan_id: Reference number of the Summit loan; leave "" if unknown.
        customer_id: Reference number of the primary borrower; leave "" if unknown.
    """
    match = {k: v for k, v in {"jumbo_txn_id": jumbo_txn_id, "jumbo_loan_id": jumbo_loan_id,
                               "customer_id": customer_id}.items() if v}
    return _report(ctx.find("jumbo_transactions", **match), "Summit transactions", match)


@tool(owner="agent", rw="read")
def find_setaside_accounts(ctx: ToolContext, setaside_id: str = "", customer_id: str = "",
                           hecm_loan_id: str = "", jumbo_loan_id: str = "") -> str:
    """Look up set-aside accounts reserved on a loan.

    Returns each set-aside's plan, status, the loan it belongs to, establishment and closing dates,
    the amount reserved and the balance remaining, the annual property tax and insurance premiums
    on file, any semi-annual installment and any repair estimate. Search by any reference number
    you hold; every criterion is optional.

    Args:
        setaside_id: Reference number of the set-aside; leave "" if unknown.
        customer_id: Reference number of the primary borrower; leave "" if unknown.
        hecm_loan_id: Reference number of the HECM loan; leave "" if unknown.
        jumbo_loan_id: Reference number of the Summit loan; leave "" if unknown.
    """
    match = {k: v for k, v in {"setaside_id": setaside_id, "customer_id": customer_id,
                               "hecm_loan_id": hecm_loan_id,
                               "jumbo_loan_id": jumbo_loan_id}.items() if v}
    return _report(ctx.find("setaside_accounts", **match), "set-asides", match)


@tool(owner="agent", rw="read")
def find_setaside_transactions(ctx: ToolContext, setaside_txn_id: str = "", setaside_id: str = "",
                               customer_id: str = "", setaside_request_id: str = "") -> str:
    """Look up the activity of set-aside accounts.

    Returns opening funding, tax and insurance payments, semi-annual installments to the borrower,
    repair draws, servicing fee draws, monthly growth, refunds and releases, each with its amount,
    date, period, coverage, repair draw number and the bill or request it paid. Search by any
    reference number you hold; every criterion is optional.

    Args:
        setaside_txn_id: Reference number of one set-aside transaction; leave "" if unknown.
        setaside_id: Reference number of the set-aside; leave "" if unknown.
        customer_id: Reference number of the primary borrower; leave "" if unknown.
        setaside_request_id: Reference number of the bill or request a payment covered; leave "" if unknown.
    """
    match = {k: v for k, v in {"setaside_txn_id": setaside_txn_id, "setaside_id": setaside_id,
                               "customer_id": customer_id,
                               "setaside_request_id": setaside_request_id}.items() if v}
    return _report(ctx.find("setaside_transactions", **match), "set-aside transactions", match)


@tool(owner="agent", rw="read")
def find_setaside_requests(ctx: ToolContext, setaside_request_id: str = "", customer_id: str = "",
                           setaside_id: str = "") -> str:
    """Look up tax bills, insurance bills, repair draw requests and cancellation requests addressed to a set-aside.

    Each shows its type, the bill or invoice reference, the amount billed, the due date, any
    inspection findings, the date received, its processing status and any decline reason. Search
    by any reference number you hold; every criterion is optional.

    Args:
        setaside_request_id: Reference number of the bill or request; leave "" if unknown.
        customer_id: Reference number of the primary borrower; leave "" if unknown.
        setaside_id: Reference number of the set-aside; leave "" if unknown.
    """
    match = {k: v for k, v in {"setaside_request_id": setaside_request_id,
                               "customer_id": customer_id, "setaside_id": setaside_id}.items() if v}
    return _report(ctx.find("setaside_requests", **match), "set-aside bills or requests", match)


@tool(owner="agent", rw="read")
def find_propcharge_plans(ctx: ToolContext, propcharge_plan_id: str = "", customer_id: str = "",
                          hecm_loan_id: str = "", jumbo_loan_id: str = "") -> str:
    """Look up property charge repayment records for taxes or insurance Cedarline advanced.

    Returns each record's arrangement, status, the loan, the date it opened, the unrepaid amount,
    the installment and term, the first installment date and the dates the agreement was issued,
    signed, defaulted or closed. Search by any reference number you hold; every criterion is
    optional.

    Args:
        propcharge_plan_id: Reference number of the repayment record; leave "" if unknown.
        customer_id: Reference number of the primary borrower; leave "" if unknown.
        hecm_loan_id: Reference number of the HECM loan; leave "" if unknown.
        jumbo_loan_id: Reference number of the Summit loan; leave "" if unknown.
    """
    match = {k: v for k, v in {"propcharge_plan_id": propcharge_plan_id, "customer_id": customer_id,
                               "hecm_loan_id": hecm_loan_id,
                               "jumbo_loan_id": jumbo_loan_id}.items() if v}
    return _report(ctx.find("propcharge_plans", **match), "property charge repayment records", match)


@tool(owner="agent", rw="read")
def find_propcharge_transactions(ctx: ToolContext, propcharge_txn_id: str = "",
                                 propcharge_plan_id: str = "", customer_id: str = "") -> str:
    """Look up the activity of property charge repayment records.

    Returns advances Cedarline paid with the bill reference and charge type, repayments with their
    confirmation numbers, missed installments and at-risk extension reviews. Search by any
    reference number you hold; every criterion is optional.

    Args:
        propcharge_txn_id: Reference number of one entry; leave "" if unknown.
        propcharge_plan_id: Reference number of the repayment record; leave "" if unknown.
        customer_id: Reference number of the primary borrower; leave "" if unknown.
    """
    match = {k: v for k, v in {"propcharge_txn_id": propcharge_txn_id,
                               "propcharge_plan_id": propcharge_plan_id,
                               "customer_id": customer_id}.items() if v}
    return _report(ctx.find("propcharge_transactions", **match), "property charge entries", match)


@tool(owner="agent", rw="read")
def find_residency_profiles(ctx: ToolContext, residency_profile_id: str = "", customer_id: str = "",
                            hecm_loan_id: str = "", jumbo_loan_id: str = "", nbs_customer_id: str = "",
                            representative_customer_id: str = "") -> str:
    """Look up occupancy certification profiles.

    Returns each profile's certification plan, status, the loan it monitors, the enrollment date,
    the current certification due date, the last completed certification, any health-care absence
    start date, any confirmed non-occupancy and its basis, and the closing date. Search by any
    reference number you hold; every criterion is optional.

    Args:
        residency_profile_id: Reference number of the profile; leave "" if unknown.
        customer_id: Reference number of the primary borrower; leave "" if unknown.
        hecm_loan_id: Reference number of the HECM loan; leave "" if unknown.
        jumbo_loan_id: Reference number of the Summit loan; leave "" if unknown.
        nbs_customer_id: Reference number of the non-borrowing spouse who certifies; leave "" if unknown.
        representative_customer_id: Reference number of the trustee, attorney-in-fact or guardian who signs; leave "" if unknown.
    """
    match = {k: v for k, v in {"residency_profile_id": residency_profile_id, "customer_id": customer_id,
                               "hecm_loan_id": hecm_loan_id, "jumbo_loan_id": jumbo_loan_id,
                               "nbs_customer_id": nbs_customer_id,
                               "representative_customer_id": representative_customer_id}.items() if v}
    return _report(ctx.find("residency_profiles", **match), "occupancy profiles", match)


@tool(owner="agent", rw="read")
def find_residency_events(ctx: ToolContext, residency_event_id: str = "", residency_profile_id: str = "",
                          customer_id: str = "", certifier_customer_id: str = "",
                          residency_submission_id: str = "") -> str:
    """Look up the occupancy certification history of a profile.

    Returns notices mailed, certifications recorded with the signer and method, inspection orders
    with their reason and fee, inspection results, and health-care absence check-ins, each with its
    date and certification year. Search by any reference number you hold; every criterion is
    optional.

    Args:
        residency_event_id: Reference number of one entry; leave "" if unknown.
        residency_profile_id: Reference number of the profile; leave "" if unknown.
        customer_id: Reference number of the primary borrower; leave "" if unknown.
        certifier_customer_id: Reference number of a person whose certification was recorded; leave "" if unknown.
        residency_submission_id: Reference number of the submission an entry recorded; leave "" if unknown.
    """
    match = {k: v for k, v in {"residency_event_id": residency_event_id,
                               "residency_profile_id": residency_profile_id, "customer_id": customer_id,
                               "certifier_customer_id": certifier_customer_id,
                               "residency_submission_id": residency_submission_id}.items() if v}
    return _report(ctx.find("residency_events", **match), "occupancy history entries", match)


@tool(owner="agent", rw="read")
def find_residency_submissions(ctx: ToolContext, residency_submission_id: str = "", customer_id: str = "",
                               residency_profile_id: str = "", subject_customer_id: str = "") -> str:
    """Look up occupancy-related submissions: signed certifications, health-care absence and return notices, permanent move statements, death notices and supporting documents.

    Each shows who submitted it, whom it concerns, the date stated in it, the document reference,
    the channel, the date received, its review status and any rejection reason. Search by any
    reference number you hold; every criterion is optional.

    Args:
        residency_submission_id: Reference number of the submission; leave "" if unknown.
        customer_id: Reference number of the person who submitted it; leave "" if unknown.
        residency_profile_id: Reference number of the profile; leave "" if unknown.
        subject_customer_id: Reference number of the person the submission is about; leave "" if unknown.
    """
    match = {k: v for k, v in {"residency_submission_id": residency_submission_id,
                               "customer_id": customer_id, "residency_profile_id": residency_profile_id,
                               "subject_customer_id": subject_customer_id}.items() if v}
    return _report(ctx.find("residency_submissions", **match), "occupancy submissions", match)


@tool(owner="agent", rw="read")
def find_maturity_cases(ctx: ToolContext, maturity_case_id: str = "", customer_id: str = "",
                        hecm_loan_id: str = "", jumbo_loan_id: str = "", successor_customer_id: str = "") -> str:
    """Look up maturity and due-and-payable cases.

    Returns each case's maturity event type, status, the loan, the event and opening dates, any
    HUD request date, the due-and-payable date with the response and resolution deadlines, the
    latest appraisal, the successor and the intent declared, any foreclosure referral, and how and
    when the case ended. Search by any reference number you hold; every criterion is optional.

    Args:
        maturity_case_id: Reference number of the case; leave "" if unknown.
        customer_id: Reference number of the borrower of record; leave "" if unknown.
        hecm_loan_id: Reference number of the HECM loan; leave "" if unknown.
        jumbo_loan_id: Reference number of the Summit loan; leave "" if unknown.
        successor_customer_id: Reference number of the successor or borrower acting on the case; leave "" if unknown.
    """
    match = {k: v for k, v in {"maturity_case_id": maturity_case_id, "customer_id": customer_id,
                               "hecm_loan_id": hecm_loan_id, "jumbo_loan_id": jumbo_loan_id,
                               "successor_customer_id": successor_customer_id}.items() if v}
    return _report(ctx.find("maturity_cases", **match), "maturity cases", match)


@tool(owner="agent", rw="read")
def find_maturity_case_events(ctx: ToolContext, maturity_event_id: str = "", maturity_case_id: str = "",
                              customer_id: str = "", recipient_customer_id: str = "",
                              maturity_request_id: str = "") -> str:
    """Look up the history of a maturity case: HUD notifications, approvals and extension decisions, notices sent, and extensions granted with their new deadlines.

    Search by any reference number you hold; every criterion is optional.

    Args:
        maturity_event_id: Reference number of one entry; leave "" if unknown.
        maturity_case_id: Reference number of the case; leave "" if unknown.
        customer_id: Reference number of the borrower of record; leave "" if unknown.
        recipient_customer_id: Reference number of a person a notice was sent to; leave "" if unknown.
        maturity_request_id: Reference number of the request an entry acted on; leave "" if unknown.
    """
    match = {k: v for k, v in {"maturity_event_id": maturity_event_id, "maturity_case_id": maturity_case_id,
                               "customer_id": customer_id, "recipient_customer_id": recipient_customer_id,
                               "maturity_request_id": maturity_request_id}.items() if v}
    return _report(ctx.find("maturity_case_events", **match), "maturity case entries", match)


@tool(owner="agent", rw="read")
def find_maturity_requests(ctx: ToolContext, maturity_request_id: str = "", customer_id: str = "",
                           maturity_case_id: str = "") -> str:
    """Look up requests on maturity cases: intent declarations, extension requests, cure evidence and event reports.

    Each shows the intent stated, the type, reference and date of the supporting document, the date
    received, its processing status and any decline reason. Search by any reference number you
    hold; every criterion is optional.

    Args:
        maturity_request_id: Reference number of the request; leave "" if unknown.
        customer_id: Reference number of the person who made it; leave "" if unknown.
        maturity_case_id: Reference number of the case; leave "" if unknown.
    """
    match = {k: v for k, v in {"maturity_request_id": maturity_request_id, "customer_id": customer_id,
                               "maturity_case_id": maturity_case_id}.items() if v}
    return _report(ctx.find("maturity_requests", **match), "maturity case requests", match)


@tool(owner="agent", rw="read")
def find_payoff_cases(ctx: ToolContext, payoff_case_id: str = "", customer_id: str = "",
                      borrower_customer_id: str = "", hecm_loan_id: str = "", jumbo_loan_id: str = "",
                      maturity_case_id: str = "") -> str:
    """Look up payoff cases.

    Returns each case's payoff plan, status, requester and borrower, the loan and any maturity
    case, the statement date and good-through date, statement balance and daily accrual, the
    appraised value, contract price and closing costs relied on, the required payoff amount, funds
    held, any relocation incentive due, and the acceptance and closing dates. Search by any
    reference number you hold; every criterion is optional.

    Args:
        payoff_case_id: Reference number of the payoff case; leave "" if unknown.
        customer_id: Reference number of the requester; leave "" if unknown.
        borrower_customer_id: Reference number of the borrower of record; leave "" if unknown.
        hecm_loan_id: Reference number of the HECM loan; leave "" if unknown.
        jumbo_loan_id: Reference number of the Summit loan; leave "" if unknown.
        maturity_case_id: Reference number of the related maturity case; leave "" if unknown.
    """
    match = {k: v for k, v in {"payoff_case_id": payoff_case_id, "customer_id": customer_id,
                               "borrower_customer_id": borrower_customer_id, "hecm_loan_id": hecm_loan_id,
                               "jumbo_loan_id": jumbo_loan_id,
                               "maturity_case_id": maturity_case_id}.items() if v}
    return _report(ctx.find("payoff_cases", **match), "payoff cases", match)


@tool(owner="agent", rw="read")
def find_payoff_transactions(ctx: ToolContext, payoff_txn_id: str = "", payoff_case_id: str = "",
                             customer_id: str = "") -> str:
    """Look up the money movements on payoff cases: funds received with their wire or check reference and sender, returned funds, refunds of excess, the amount applied at satisfaction, and relocation incentives committed or paid.

    Search by any reference number you hold; every criterion is optional.

    Args:
        payoff_txn_id: Reference number of one entry; leave "" if unknown.
        payoff_case_id: Reference number of the payoff case; leave "" if unknown.
        customer_id: Reference number of the requester; leave "" if unknown.
    """
    match = {k: v for k, v in {"payoff_txn_id": payoff_txn_id, "payoff_case_id": payoff_case_id,
                               "customer_id": customer_id}.items() if v}
    return _report(ctx.find("payoff_transactions", **match), "payoff entries", match)


@tool(owner="agent", rw="read")
def find_payoff_requests(ctx: ToolContext, payoff_request_id: str = "", customer_id: str = "",
                         payoff_case_id: str = "", hecm_loan_id: str = "", jumbo_loan_id: str = "") -> str:
    """Look up payoff submissions: payoff statement requests, purchase contracts, signed agreements, deed-in-lieu recording confirmations and withdrawals.

    Each shows the plan, the capacity the submitter acts in, contract price and costs, the buyer's
    relationship, the listing date, document reference, date received, processing status and any
    decline reason. Search by any reference number you hold; every criterion is optional.

    Args:
        payoff_request_id: Reference number of the submission; leave "" if unknown.
        customer_id: Reference number of the person who submitted it; leave "" if unknown.
        payoff_case_id: Reference number of the payoff case; leave "" if unknown.
        hecm_loan_id: Reference number of the HECM loan; leave "" if unknown.
        jumbo_loan_id: Reference number of the Summit loan; leave "" if unknown.
    """
    match = {k: v for k, v in {"payoff_request_id": payoff_request_id, "customer_id": customer_id,
                               "payoff_case_id": payoff_case_id, "hecm_loan_id": hecm_loan_id,
                               "jumbo_loan_id": jumbo_loan_id}.items() if v}
    return _report(ctx.find("payoff_requests", **match), "payoff submissions", match)


@tool(owner="agent", rw="read")
def find_verification_log(ctx: ToolContext, verification_id: str = "", customer_id: str = "") -> str:
    """Look up the recorded outcome of identity verification for a customer: whether verification passed and when it was last attempted.

    Args:
        verification_id: Reference number of the verification record; leave "" if unknown.
        customer_id: Reference number of the customer; leave "" if unknown.
    """
    match = {k: v for k, v in {"verification_id": verification_id, "customer_id": customer_id}.items() if v}
    return _report(ctx.find("verification_log", **match), "verification records", match)


@tool(owner="agent", rw="read")
def find_handoff_log(ctx: ToolContext, handoff_id: str = "", customer_id: str = "") -> str:
    """Look up earlier transfers of a customer to a human representative, with the reason and time of each.

    Args:
        handoff_id: Reference number of the transfer record; leave "" if unknown.
        customer_id: Reference number of the customer; leave "" if unknown.
    """
    match = {k: v for k, v in {"handoff_id": handoff_id, "customer_id": customer_id}.items() if v}
    return _report(ctx.find("handoff_log", **match), "transfer records", match)


@tool(owner="agent", rw="write")
def verify_customer_identity(ctx: ToolContext, customer_id: str, phone_number: str = "",
                             email: str = "", ssn_last4: str = "", date_of_birth: str = "",
                             property_zip: str = "") -> str:
    """Verify the caller's identity and record the outcome; verification must pass before any account information is discussed or any transaction is handled.

    This tool performs the comparison itself: it checks each piece of identity information the
    caller states against the customer profile, counts the matches, and passes only when at least
    2 of them match. The customer reference number only retrieves the profile and never counts as
    a match. Callers usually know only some of these details, so pass exactly what the caller said
    and leave the rest blank. The outcome is recorded; if a first attempt fails and a later attempt
    with more information passes, the pass stands.

    Args:
        customer_id: Customer reference number taken from the profile lookup; required, and used only to retrieve the profile.
        phone_number: Phone number on file as the caller states it, 10 digits with no punctuation; leave "" if not stated.
        email: Email address on file as the caller states it; leave "" if not stated.
        ssn_last4: Last four digits of the Social Security number as the caller states them; leave "" if not stated.
        date_of_birth: Caller's date of birth in YYYY-MM-DD form; leave "" if not stated.
        property_zip: 5-digit ZIP code of the mortgaged property as the caller states it; leave "" if not stated.
    """
    if not customer_id:
        return "Error: customer_id is required; look the customer up first and pass their reference number."
    rows = ctx.find("customers", customer_id=customer_id)
    if not rows:
        return f"Error: no customer {customer_id}; cannot verify."
    rec = rows[0]
    supplied = {"phone_number": phone_number, "email": email, "ssn_last4": ssn_last4,
                "date_of_birth": date_of_birth, "property_zip": property_zip}
    matched = sum(1 for field, value in supplied.items()
                  if value and str(rec.get(field, "")).strip().lower() == str(value).strip().lower())
    verified = matched >= 2
    rid = ctx.make_id("ver_", customer_id)
    prior = ctx.find("verification_log", verification_id=rid)
    verified = verified or bool(prior and prior[0].get("verified"))
    if prior:
        ctx.update("verification_log", rid, verified=verified, verified_at=ctx.now())
    else:
        ctx.create("verification_log", rid, verification_id=rid, customer_id=customer_id,
                   verified=verified, verified_at=ctx.now())
    return (f"Identity verified for {customer_id} ({matched} detail(s) matched)." if verified
            else f"Identity NOT verified for {customer_id} (only {matched} of the required 2 details matched). "
                 f"Ask the caller for another detail on file and try again.")


@tool(owner="agent", rw="write")
def transfer_to_human_agent(ctx: ToolContext, customer_id: str, reason: str) -> str:
    """Transfer the customer to a human representative and record the transfer and its reason.

    Use it in one of two situations only: no Cedarline policy can resolve what the customer is
    asking for, or the customer has explicitly asked to speak with a person at least 2 times in
    this conversation.

    Args:
        customer_id: Customer reference number taken from the profile lookup; the profile must exist.
        reason: Why the customer is being transferred, exactly one of POLICY_NOT_COVERED (current policy offers no way to resolve the request) or CUSTOMER_REQUESTED (the customer has explicitly asked for a human representative at least 2 times); never free text.
    """
    allowed = {"POLICY_NOT_COVERED", "CUSTOMER_REQUESTED"}
    if reason not in allowed:
        return f"Error: unknown transfer reason '{reason}'. Valid: {', '.join(sorted(allowed))}."
    if not ctx.find("customers", customer_id=customer_id):
        return f"Error: no customer {customer_id}; cannot record the transfer."
    rid = ctx.make_id("hof_", customer_id, reason)
    ctx.create("handoff_log", rid, handoff_id=rid, customer_id=customer_id,
               reason=reason, created_at=ctx.now())
    return f"Transfer to a human representative recorded for {customer_id} ({reason})."

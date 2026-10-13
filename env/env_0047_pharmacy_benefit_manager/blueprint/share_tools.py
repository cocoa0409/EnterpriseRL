"""Shared tools for env_0047_pharmacy_benefit_manager (Northbridge Rx member and plan sponsor services).

Every tool here is a SHARE tool: always present in its owner's tool list. This file holds
the record-lookup layer (one finder per table; the customers finder doubles as the identity
entry), the identity-verification write and the transfer-to-human write. Customer-originated
writes are hidden task tools in each difficulty's task_tools.py.

Scenario operational constants built into these tools:
  K = 2  identity credentials that must match the profile for verification to pass
         (date of birth, member ID, phone, email, ZIP code, sponsor tax ID last four;
         a name alone is never a credential).
  R = 2  explicit requests for a human representative before a CUSTOMER_REQUESTED handoff.
"""

from erlbench import ToolContext, tool


def _norm(value) -> str:
    # Compare caller statements after normalisation (casefold, letters and digits only),
    # the same way the customer lookup matches, so punctuation or spacing never decides a match.
    return "".join(ch for ch in str(value or "").casefold() if ch.isalnum())


@tool(owner="agent", rw="read")
def find_customers(ctx: ToolContext, customer_id: str = "", name: str = "", phone_number: str = "",
                   email: str = "", member_number: str = "", group_number: str = "",
                   customer_type: str = "", subscriber_customer_id: str = "",
                   sponsor_customer_id: str = "") -> str:
    """Look up a customer profile to establish whose account this call is about. Northbridge Rx
    serves two kinds of customers: covered members, and plan sponsors (the employers, unions and
    plans that contract for pharmacy benefits). A profile can be found by its customer reference
    number or by what a caller can naturally state: full name, phone number, email address,
    member ID from the prescription card, or the group number of the sponsor's plan. Every
    criterion is optional; supply whichever are known. The profile returned shows the customer
    type, name, date of birth (members), member ID and group number, sponsor tax ID last four
    (sponsors), phone, email, ZIP code and state, the member's relationship to the subscriber,
    the subscriber's and the plan sponsor's customer reference numbers, and the date the profile
    was opened. Finding a profile does not verify the caller's identity.

    When searching by a subscriber or sponsor reference number, every profile linked to it is
    returned (for example all family members of a subscriber, or all members of a sponsor);
    otherwise the search must narrow to exactly one profile.

    Args:
        customer_id: The customer reference number; leave "" if unknown.
        name: The full name as the caller states it (member's legal name, or the sponsor's legal entity name); leave "" if not provided.
        phone_number: The phone number on file, 10 digits; leave "" if not provided.
        email: The email address on file; leave "" if not provided.
        member_number: The member ID printed on the prescription card (three letters and nine digits, e.g. NBX204418873); leave "" if not provided.
        group_number: The group number of the sponsor's pharmacy plan as printed on cards (e.g. NB-04417); leave "" if not provided.
        customer_type: "member" or "plan_sponsor", to narrow a search that matches both; leave "" if not needed.
        subscriber_customer_id: The customer reference number of a subscriber, to list the members of that family; leave "" if unknown.
        sponsor_customer_id: The customer reference number of a plan sponsor, to list the members it covers; leave "" if unknown.
    """
    match = {k: v for k, v in {"customer_id": customer_id, "name": name, "phone_number": phone_number,
                               "email": email, "member_number": member_number,
                               "group_number": group_number, "customer_type": customer_type,
                               "subscriber_customer_id": subscriber_customer_id,
                               "sponsor_customer_id": sponsor_customer_id}.items() if v}
    if not match:
        return "Error: provide at least one reference number or profile detail to find the customer."
    rows = ctx.fuzzy_find("customers", **match)
    if not rows:
        return f"No customer matches {match}."
    if subscriber_customer_id or sponsor_customer_id:
        return str(rows)
    if len(rows) > 1:
        return (f"Error: {len(rows)} customers match {match}; ask the caller for one more detail "
                "(or give customer_type) to narrow it to one profile.")
    return str(rows[0])


@tool(owner="agent", rw="read")
def find_plan_enrollments(ctx: ToolContext, plan_enrollment_id: str = "", customer_id: str = "", sponsor_customer_id: str = "") -> str:
    """Look up a member's pharmacy benefit plan enrollments: the plan design held, coverage
    status and dates, coverage level, plan year start, COBRA dates, other-coverage (coordination
    of benefits) status, and the deductible and out-of-pocket amounts met so far this plan year.
    Every reference number below is optional; give whichever are known, and every record
    carrying all of them is returned. With none given, nothing is searched.

    Args:
        plan_enrollment_id: The reference number of the plan enrollment itself; leave "" if unknown.
        customer_id: The customer reference number of the covered member; leave "" if unknown.
        sponsor_customer_id: The customer reference number of the plan sponsor providing the coverage (returns every enrollment under that sponsor); leave "" if unknown.
    """
    match = {k: v for k, v in {"plan_enrollment_id": plan_enrollment_id, "customer_id": customer_id, "sponsor_customer_id": sponsor_customer_id}.items() if v}
    if not match:
        return "Error: give at least one reference number to look up plan enrollments."
    rows = ctx.find("plan_enrollments", **match)
    return str(rows) if rows else f"No matching records found for {match}."


@tool(owner="agent", rw="read")
def find_plan_accumulator_ledger(ctx: ToolContext, plan_accumulator_entry_id: str = "", plan_enrollment_id: str = "", customer_id: str = "", source_reference_id: str = "") -> str:
    """Look up the deductible and out-of-pocket accumulator history behind a member's plan
    enrollment: every amount credited or taken back, the date it accrues to, the plan year, what
    produced it (pharmacy claim, medical carrier feed, prior-carrier transfer, fourth-quarter
    carryover, correction or plan-year reset), the dispensing channel, the funding source and
    the claim's tier and allowed amount. Every reference number below is optional; give
    whichever are known, and every record carrying all of them is returned. With none given,
    nothing is searched.

    Args:
        plan_accumulator_entry_id: The reference number of one accumulator entry; leave "" if unknown.
        plan_enrollment_id: The reference number of the plan enrollment; leave "" if unknown.
        customer_id: The customer reference number of the member; leave "" if unknown.
        source_reference_id: The reference number of the claim, order, fill or entry that produced the movement; leave "" if unknown.
    """
    match = {k: v for k, v in {"plan_accumulator_entry_id": plan_accumulator_entry_id, "plan_enrollment_id": plan_enrollment_id, "customer_id": customer_id, "source_reference_id": source_reference_id}.items() if v}
    if not match:
        return "Error: give at least one reference number to look up plan accumulator ledger."
    rows = ctx.find("plan_accumulator_ledger", **match)
    return str(rows) if rows else f"No matching records found for {match}."


@tool(owner="agent", rw="read")
def find_plan_service_records(ctx: ToolContext, plan_service_record_id: str = "", plan_enrollment_id: str = "", customer_id: str = "") -> str:
    """Look up a member's plan service history: replacement ID cards issued (reason and delivery
    method) and coordination-of-benefits questionnaire cycles with the member's answers. Every
    reference number below is optional; give whichever are known, and every record carrying all
    of them is returned. With none given, nothing is searched.

    Args:
        plan_service_record_id: The reference number of one service record; leave "" if unknown.
        plan_enrollment_id: The reference number of the plan enrollment; leave "" if unknown.
        customer_id: The customer reference number of the member; leave "" if unknown.
    """
    match = {k: v for k, v in {"plan_service_record_id": plan_service_record_id, "plan_enrollment_id": plan_enrollment_id, "customer_id": customer_id}.items() if v}
    if not match:
        return "Error: give at least one reference number to look up plan service records."
    rows = ctx.find("plan_service_records", **match)
    return str(rows) if rows else f"No matching records found for {match}."


@tool(owner="agent", rw="read")
def find_formulary_assignments(ctx: ToolContext, formulary_assignment_id: str = "", customer_id: str = "", plan_enrollment_id: str = "") -> str:
    """Look up the formulary a member is assigned to: formulary name, status, effective and end
    dates, the start of the member's transition window and any formulary change date. Every
    reference number below is optional; give whichever are known, and every record carrying all
    of them is returned. With none given, nothing is searched.

    Args:
        formulary_assignment_id: The reference number of the formulary assignment; leave "" if unknown.
        customer_id: The customer reference number of the member; leave "" if unknown.
        plan_enrollment_id: The reference number of the plan enrollment the formulary belongs to; leave "" if unknown.
    """
    match = {k: v for k, v in {"formulary_assignment_id": formulary_assignment_id, "customer_id": customer_id, "plan_enrollment_id": plan_enrollment_id}.items() if v}
    if not match:
        return "Error: give at least one reference number to look up formulary assignments."
    rows = ctx.find("formulary_assignments", **match)
    return str(rows) if rows else f"No matching records found for {match}."


@tool(owner="agent", rw="read")
def find_formulary_exceptions(ctx: ToolContext, formulary_exception_id: str = "", formulary_assignment_id: str = "", customer_id: str = "", source_exception_id: str = "") -> str:
    """Look up formulary exception case history: requests for tier or non-formulary exceptions,
    prescriber supporting statements, approvals with their tier and approval period, denials
    with their reasons, withdrawals and external exception reviews. Each follow-up event carries
    the reference number of the original request. Every reference number below is optional; give
    whichever are known, and every record carrying all of them is returned. With none given,
    nothing is searched.

    Args:
        formulary_exception_id: The reference number of one exception case event; leave "" if unknown.
        formulary_assignment_id: The reference number of the formulary assignment; leave "" if unknown.
        customer_id: The customer reference number of the member; leave "" if unknown.
        source_exception_id: The reference number of the original request (returns every follow-up event on it); leave "" if unknown.
    """
    match = {k: v for k, v in {"formulary_exception_id": formulary_exception_id, "formulary_assignment_id": formulary_assignment_id, "customer_id": customer_id, "source_exception_id": source_exception_id}.items() if v}
    if not match:
        return "Error: give at least one reference number to look up formulary exceptions."
    rows = ctx.find("formulary_exceptions", **match)
    return str(rows) if rows else f"No matching records found for {match}."


@tool(owner="agent", rw="read")
def find_formulary_transition_fills(ctx: ToolContext, formulary_transition_fill_id: str = "", formulary_assignment_id: str = "", customer_id: str = "") -> str:
    """Look up the temporary transition supplies of non-formulary drugs a member has received:
    drug, strength, fill date, days supply, why the member was in a transition window and the
    dispensing channel. Every reference number below is optional; give whichever are known, and
    every record carrying all of them is returned. With none given, nothing is searched.

    Args:
        formulary_transition_fill_id: The reference number of one transition fill; leave "" if unknown.
        formulary_assignment_id: The reference number of the formulary assignment; leave "" if unknown.
        customer_id: The customer reference number of the member; leave "" if unknown.
    """
    match = {k: v for k, v in {"formulary_transition_fill_id": formulary_transition_fill_id, "formulary_assignment_id": formulary_assignment_id, "customer_id": customer_id}.items() if v}
    if not match:
        return "Error: give at least one reference number to look up formulary transition fills."
    rows = ctx.find("formulary_transition_fills", **match)
    return str(rows) if rows else f"No matching records found for {match}."


@tool(owner="agent", rw="read")
def find_formulary_notices(ctx: ToolContext, formulary_notice_id: str = "", formulary_assignment_id: str = "", customer_id: str = "") -> str:
    """Look up formulary change notices sent to a member: the drug, the kind of change, its new
    status, the notice date and the date the change takes effect. Every reference number below
    is optional; give whichever are known, and every record carrying all of them is returned.
    With none given, nothing is searched.

    Args:
        formulary_notice_id: The reference number of one notice; leave "" if unknown.
        formulary_assignment_id: The reference number of the formulary assignment; leave "" if unknown.
        customer_id: The customer reference number of the member; leave "" if unknown.
    """
    match = {k: v for k, v in {"formulary_notice_id": formulary_notice_id, "formulary_assignment_id": formulary_assignment_id, "customer_id": customer_id}.items() if v}
    if not match:
        return "Error: give at least one reference number to look up formulary notices."
    rows = ctx.find("formulary_notices", **match)
    return str(rows) if rows else f"No matching records found for {match}."


@tool(owner="agent", rw="read")
def find_retail_benefits(ctx: ToolContext, retail_benefit_id: str = "", customer_id: str = "", plan_enrollment_id: str = "") -> str:
    """Look up a member's retail pharmacy network benefit: network name, status, effective and
    end dates, maintenance-medication choice, controlled-substance lock-in details and any
    approved paper-claim reimbursement not yet paid. Every reference number below is optional;
    give whichever are known, and every record carrying all of them is returned. With none
    given, nothing is searched.

    Args:
        retail_benefit_id: The reference number of the retail benefit; leave "" if unknown.
        customer_id: The customer reference number of the member; leave "" if unknown.
        plan_enrollment_id: The reference number of the plan enrollment it belongs to; leave "" if unknown.
    """
    match = {k: v for k, v in {"retail_benefit_id": retail_benefit_id, "customer_id": customer_id, "plan_enrollment_id": plan_enrollment_id}.items() if v}
    if not match:
        return "Error: give at least one reference number to look up retail benefits."
    rows = ctx.find("retail_benefits", **match)
    return str(rows) if rows else f"No matching records found for {match}."


@tool(owner="agent", rw="read")
def find_retail_claims(ctx: ToolContext, retail_claim_id: str = "", retail_benefit_id: str = "", customer_id: str = "", original_claim_id: str = "", override_reference_id: str = "") -> str:
    """Look up retail pharmacy claims: paid claims and reversals with prescription number, fill
    number, date of service, pharmacy and prescriber, network status, drug, quantity, days
    supply, tier, dispense-as-written code, any override used, and the allowed amount,
    deductible, copay, brand difference, member payment, amount counted toward out-of-pocket and
    plan payment. A reversal carries the reference number of the claim it reverses. Every
    reference number below is optional; give whichever are known, and every record carrying all
    of them is returned. With none given, nothing is searched.

    Args:
        retail_claim_id: The reference number of one claim transaction; leave "" if unknown.
        retail_benefit_id: The reference number of the retail benefit; leave "" if unknown.
        customer_id: The customer reference number of the member; leave "" if unknown.
        original_claim_id: The reference number of a paid claim (returns the reversal of it, if any); leave "" if unknown.
        override_reference_id: The reference number of an override (returns the claims paid under it); leave "" if unknown.
    """
    match = {k: v for k, v in {"retail_claim_id": retail_claim_id, "retail_benefit_id": retail_benefit_id, "customer_id": customer_id, "original_claim_id": original_claim_id, "override_reference_id": override_reference_id}.items() if v}
    if not match:
        return "Error: give at least one reference number to look up retail claims."
    rows = ctx.find("retail_claims", **match)
    return str(rows) if rows else f"No matching records found for {match}."


@tool(owner="agent", rw="read")
def find_retail_overrides(ctx: ToolContext, retail_override_id: str = "", retail_benefit_id: str = "", customer_id: str = "") -> str:
    """Look up refill overrides granted to a member: vacation supply, lost or stolen medication,
    dose change or emergency supply, with the prescription number, drug, grant date, last valid
    date, days supply allowed, departure date and police report number where they apply. Every
    reference number below is optional; give whichever are known, and every record carrying all
    of them is returned. With none given, nothing is searched.

    Args:
        retail_override_id: The reference number of one override; leave "" if unknown.
        retail_benefit_id: The reference number of the retail benefit; leave "" if unknown.
        customer_id: The customer reference number of the member; leave "" if unknown.
    """
    match = {k: v for k, v in {"retail_override_id": retail_override_id, "retail_benefit_id": retail_benefit_id, "customer_id": customer_id}.items() if v}
    if not match:
        return "Error: give at least one reference number to look up retail overrides."
    rows = ctx.find("retail_overrides", **match)
    return str(rows) if rows else f"No matching records found for {match}."


@tool(owner="agent", rw="read")
def find_retail_reimbursements(ctx: ToolContext, retail_reimbursement_id: str = "", retail_benefit_id: str = "", customer_id: str = "", source_reimbursement_id: str = "") -> str:
    """Look up paper claims (direct member reimbursements): submissions with the receipt
    details, approvals and denials with their pricing and reasons, and payments. Each decision
    or payment carries the reference number of the submission. Every reference number below is
    optional; give whichever are known, and every record carrying all of them is returned. With
    none given, nothing is searched.

    Args:
        retail_reimbursement_id: The reference number of one paper-claim event; leave "" if unknown.
        retail_benefit_id: The reference number of the retail benefit; leave "" if unknown.
        customer_id: The customer reference number of the member; leave "" if unknown.
        source_reimbursement_id: The reference number of the original submission (returns every decision and payment on it); leave "" if unknown.
    """
    match = {k: v for k, v in {"retail_reimbursement_id": retail_reimbursement_id, "retail_benefit_id": retail_benefit_id, "customer_id": customer_id, "source_reimbursement_id": source_reimbursement_id}.items() if v}
    if not match:
        return "Error: give at least one reference number to look up retail reimbursements."
    rows = ctx.find("retail_reimbursements", **match)
    return str(rows) if rows else f"No matching records found for {match}."


@tool(owner="agent", rw="read")
def find_mail_accounts(ctx: ToolContext, mail_account_id: str = "", customer_id: str = "") -> str:
    """Look up a member's home delivery pharmacy account: program name, status, opening and
    closing dates, payment method type on file, shipping ZIP, automatic refill enrollment, any
    hold reason, payment plan length and the balance due. Every reference number below is
    optional; give whichever are known, and every record carrying all of them is returned. With
    none given, nothing is searched.

    Args:
        mail_account_id: The reference number of the home delivery account; leave "" if unknown.
        customer_id: The customer reference number of the member; leave "" if unknown.
    """
    match = {k: v for k, v in {"mail_account_id": mail_account_id, "customer_id": customer_id}.items() if v}
    if not match:
        return "Error: give at least one reference number to look up mail accounts."
    rows = ctx.find("mail_accounts", **match)
    return str(rows) if rows else f"No matching records found for {match}."


@tool(owner="agent", rw="read")
def find_mail_prescriptions(ctx: ToolContext, mail_prescription_id: str = "", mail_account_id: str = "", customer_id: str = "") -> str:
    """Look up the prescriptions on file at the home delivery pharmacy: prescription number,
    drug and strength, prescriber, how it was received (including transfers from a retail
    pharmacy), written and expiration dates, refills authorized, quantity and days supply per
    fill. Every reference number below is optional; give whichever are known, and every record
    carrying all of them is returned. With none given, nothing is searched.

    Args:
        mail_prescription_id: The reference number of one prescription on file; leave "" if unknown.
        mail_account_id: The reference number of the home delivery account; leave "" if unknown.
        customer_id: The customer reference number of the member; leave "" if unknown.
    """
    match = {k: v for k, v in {"mail_prescription_id": mail_prescription_id, "mail_account_id": mail_account_id, "customer_id": customer_id}.items() if v}
    if not match:
        return "Error: give at least one reference number to look up mail prescriptions."
    rows = ctx.find("mail_prescriptions", **match)
    return str(rows) if rows else f"No matching records found for {match}."


@tool(owner="agent", rw="read")
def find_mail_orders(ctx: ToolContext, mail_order_id: str = "", mail_account_id: str = "", customer_id: str = "", source_order_id: str = "", mail_prescription_id: str = "") -> str:
    """Look up home delivery orders: orders placed, shipped, cancelled or replaced, and
    expedited shipping charges, with fill number, dates, drug, quantity, days supply, tier,
    shipping method, member charge and its deductible and out-of-pocket parts, tracking number
    and reasons. Each follow-up event carries the reference number of the placed order. Every
    reference number below is optional; give whichever are known, and every record carrying all
    of them is returned. With none given, nothing is searched.

    Args:
        mail_order_id: The reference number of one order event; leave "" if unknown.
        mail_account_id: The reference number of the home delivery account; leave "" if unknown.
        customer_id: The customer reference number of the member; leave "" if unknown.
        source_order_id: The reference number of the placed order (returns every follow-up event on it); leave "" if unknown.
        mail_prescription_id: The reference number of the prescription filled; leave "" if unknown.
    """
    match = {k: v for k, v in {"mail_order_id": mail_order_id, "mail_account_id": mail_account_id, "customer_id": customer_id, "source_order_id": source_order_id, "mail_prescription_id": mail_prescription_id}.items() if v}
    if not match:
        return "Error: give at least one reference number to look up mail orders."
    rows = ctx.find("mail_orders", **match)
    return str(rows) if rows else f"No matching records found for {match}."


@tool(owner="agent", rw="read")
def find_mail_payments(ctx: ToolContext, mail_payment_id: str = "", mail_account_id: str = "", customer_id: str = "", source_order_id: str = "") -> str:
    """Look up payments, credits and refunds on a home delivery account: date, amount, payment
    method, credit reason, installment number and, for pharmacy-error credits, the order
    credited. Every reference number below is optional; give whichever are known, and every
    record carrying all of them is returned. With none given, nothing is searched.

    Args:
        mail_payment_id: The reference number of one payment, credit or refund; leave "" if unknown.
        mail_account_id: The reference number of the home delivery account; leave "" if unknown.
        customer_id: The customer reference number of the member; leave "" if unknown.
        source_order_id: The reference number of an order (returns the credits issued against it); leave "" if unknown.
    """
    match = {k: v for k, v in {"mail_payment_id": mail_payment_id, "mail_account_id": mail_account_id, "customer_id": customer_id, "source_order_id": source_order_id}.items() if v}
    if not match:
        return "Error: give at least one reference number to look up mail payments."
    rows = ctx.find("mail_payments", **match)
    return str(rows) if rows else f"No matching records found for {match}."


@tool(owner="agent", rw="read")
def find_mail_service_requests(ctx: ToolContext, mail_service_request_id: str = "", mail_account_id: str = "", customer_id: str = "") -> str:
    """Look up home delivery service requests: account closures, prescription transfers from a
    retail pharmacy and payment plans, with their status, date and details. Every reference
    number below is optional; give whichever are known, and every record carrying all of them is
    returned. With none given, nothing is searched.

    Args:
        mail_service_request_id: The reference number of one service request; leave "" if unknown.
        mail_account_id: The reference number of the home delivery account; leave "" if unknown.
        customer_id: The customer reference number of the member; leave "" if unknown.
    """
    match = {k: v for k, v in {"mail_service_request_id": mail_service_request_id, "mail_account_id": mail_account_id, "customer_id": customer_id}.items() if v}
    if not match:
        return "Error: give at least one reference number to look up mail service requests."
    rows = ctx.find("mail_service_requests", **match)
    return str(rows) if rows else f"No matching records found for {match}."


@tool(owner="agent", rw="read")
def find_specialty_enrollments(ctx: ToolContext, specialty_enrollment_id: str = "", customer_id: str = "") -> str:
    """Look up a member's specialty therapy enrollments: program name, status, drug and
    condition, prescriber, referral, activation and discharge dates, hold reason and start,
    maximizer and copay-program consent details, remaining manufacturer assistance and balance
    due. Every reference number below is optional; give whichever are known, and every record
    carrying all of them is returned. With none given, nothing is searched.

    Args:
        specialty_enrollment_id: The reference number of the specialty enrollment; leave "" if unknown.
        customer_id: The customer reference number of the member; leave "" if unknown.
    """
    match = {k: v for k, v in {"specialty_enrollment_id": specialty_enrollment_id, "customer_id": customer_id}.items() if v}
    if not match:
        return "Error: give at least one reference number to look up specialty enrollments."
    rows = ctx.find("specialty_enrollments", **match)
    return str(rows) if rows else f"No matching records found for {match}."


@tool(owner="agent", rw="read")
def find_specialty_fills(ctx: ToolContext, specialty_fill_id: str = "", specialty_enrollment_id: str = "", customer_id: str = "", source_fill_id: str = "") -> str:
    """Look up specialty fills: scheduled deliveries, shipments (including fills by outside
    pharmacies) and reshipments, with fill number, dispensing pharmacy, drug, quantity, days
    supply, split-fill flag, delivery date and location, tier, allowed amount, deductible,
    copay, total cost share, out-of-pocket amount and plan payment. Every reference number below
    is optional; give whichever are known, and every record carrying all of them is returned.
    With none given, nothing is searched.

    Args:
        specialty_fill_id: The reference number of one fill event; leave "" if unknown.
        specialty_enrollment_id: The reference number of the specialty enrollment; leave "" if unknown.
        customer_id: The customer reference number of the member; leave "" if unknown.
        source_fill_id: The reference number of a scheduled or shipped fill (returns the shipment or reshipment of it); leave "" if unknown.
    """
    match = {k: v for k, v in {"specialty_fill_id": specialty_fill_id, "specialty_enrollment_id": specialty_enrollment_id, "customer_id": customer_id, "source_fill_id": source_fill_id}.items() if v}
    if not match:
        return "Error: give at least one reference number to look up specialty fills."
    rows = ctx.find("specialty_fills", **match)
    return str(rows) if rows else f"No matching records found for {match}."


@tool(owner="agent", rw="read")
def find_specialty_ledger(ctx: ToolContext, specialty_ledger_id: str = "", specialty_enrollment_id: str = "", customer_id: str = "", specialty_fill_id: str = "") -> str:
    """Look up manufacturer copay assistance and payments on a specialty enrollment: program
    benefit loaded for a program year, assistance applied to fills, and payments by the member,
    the manufacturer program or a foundation. Every reference number below is optional; give
    whichever are known, and every record carrying all of them is returned. With none given,
    nothing is searched.

    Args:
        specialty_ledger_id: The reference number of one ledger entry; leave "" if unknown.
        specialty_enrollment_id: The reference number of the specialty enrollment; leave "" if unknown.
        customer_id: The customer reference number of the member; leave "" if unknown.
        specialty_fill_id: The reference number of a shipped fill (returns the assistance and payments applied to it); leave "" if unknown.
    """
    match = {k: v for k, v in {"specialty_ledger_id": specialty_ledger_id, "specialty_enrollment_id": specialty_enrollment_id, "customer_id": customer_id, "specialty_fill_id": specialty_fill_id}.items() if v}
    if not match:
        return "Error: give at least one reference number to look up specialty ledger."
    rows = ctx.find("specialty_ledger", **match)
    return str(rows) if rows else f"No matching records found for {match}."


@tool(owner="agent", rw="read")
def find_specialty_care_contacts(ctx: ToolContext, specialty_care_contact_id: str = "", specialty_enrollment_id: str = "", customer_id: str = "") -> str:
    """Look up specialty care contacts: onboarding calls, clinical assessments, refill
    reminders, adherence outreach and injection training, with date, outcome and adherence
    score. Every reference number below is optional; give whichever are known, and every record
    carrying all of them is returned. With none given, nothing is searched.

    Args:
        specialty_care_contact_id: The reference number of one care contact; leave "" if unknown.
        specialty_enrollment_id: The reference number of the specialty enrollment; leave "" if unknown.
        customer_id: The customer reference number of the member; leave "" if unknown.
    """
    match = {k: v for k, v in {"specialty_care_contact_id": specialty_care_contact_id, "specialty_enrollment_id": specialty_enrollment_id, "customer_id": customer_id}.items() if v}
    if not match:
        return "Error: give at least one reference number to look up specialty care contacts."
    rows = ctx.find("specialty_care_contacts", **match)
    return str(rows) if rows else f"No matching records found for {match}."


@tool(owner="agent", rw="read")
def find_specialty_service_requests(ctx: ToolContext, specialty_service_request_id: str = "", specialty_enrollment_id: str = "", customer_id: str = "") -> str:
    """Look up specialty service requests: transfers to another pharmacy, disenrollments and
    copay program enrollments, with status, date and details. Every reference number below is
    optional; give whichever are known, and every record carrying all of them is returned. With
    none given, nothing is searched.

    Args:
        specialty_service_request_id: The reference number of one service request; leave "" if unknown.
        specialty_enrollment_id: The reference number of the specialty enrollment; leave "" if unknown.
        customer_id: The customer reference number of the member; leave "" if unknown.
    """
    match = {k: v for k, v in {"specialty_service_request_id": specialty_service_request_id, "specialty_enrollment_id": specialty_enrollment_id, "customer_id": customer_id}.items() if v}
    if not match:
        return "Error: give at least one reference number to look up specialty service requests."
    rows = ctx.find("specialty_service_requests", **match)
    return str(rows) if rows else f"No matching records found for {match}."


@tool(owner="agent", rw="read")
def find_review_programs(ctx: ToolContext, review_program_id: str = "", customer_id: str = "", plan_enrollment_id: str = "") -> str:
    """Look up a member's utilization management (coverage review) program: package name, status
    and dates. Every reference number below is optional; give whichever are known, and every
    record carrying all of them is returned. With none given, nothing is searched.

    Args:
        review_program_id: The reference number of the review program; leave "" if unknown.
        customer_id: The customer reference number of the member; leave "" if unknown.
        plan_enrollment_id: The reference number of the plan enrollment it belongs to; leave "" if unknown.
    """
    match = {k: v for k, v in {"review_program_id": review_program_id, "customer_id": customer_id, "plan_enrollment_id": plan_enrollment_id}.items() if v}
    if not match:
        return "Error: give at least one reference number to look up review programs."
    rows = ctx.find("review_programs", **match)
    return str(rows) if rows else f"No matching records found for {match}."


@tool(owner="agent", rw="read")
def find_review_cases(ctx: ToolContext, review_case_id: str = "", review_program_id: str = "", customer_id: str = "", source_case_id: str = "") -> str:
    """Look up coverage review cases (prior authorization, step therapy exception, quantity
    limit exception): case openings, information requests and receipts, approvals, denials,
    withdrawals and automated step approvals, with drug, review type, priority, requester,
    prescriber, diagnosis, clinical ground, requested quantity, timestamps and decision reasons.
    Each follow-up event carries the reference number of the case opening. Every reference
    number below is optional; give whichever are known, and every record carrying all of them is
    returned. With none given, nothing is searched.

    Args:
        review_case_id: The reference number of one case event; leave "" if unknown.
        review_program_id: The reference number of the review program; leave "" if unknown.
        customer_id: The customer reference number of the member; leave "" if unknown.
        source_case_id: The reference number of the case opening (returns every follow-up event on it); leave "" if unknown.
    """
    match = {k: v for k, v in {"review_case_id": review_case_id, "review_program_id": review_program_id, "customer_id": customer_id, "source_case_id": source_case_id}.items() if v}
    if not match:
        return "Error: give at least one reference number to look up review cases."
    rows = ctx.find("review_cases", **match)
    return str(rows) if rows else f"No matching records found for {match}."


@tool(owner="agent", rw="read")
def find_review_authorizations(ctx: ToolContext, review_authorization_id: str = "", review_program_id: str = "", customer_id: str = "", source_case_id: str = "", source_authorization_id: str = "") -> str:
    """Look up coverage authorizations in force or ended: drug, what edit each satisfies, how it
    came about, approved quantity, effective and expiration dates, and any early end with its
    reason. Every reference number below is optional; give whichever are known, and every record
    carrying all of them is returned. With none given, nothing is searched.

    Args:
        review_authorization_id: The reference number of one authorization record; leave "" if unknown.
        review_program_id: The reference number of the review program; leave "" if unknown.
        customer_id: The customer reference number of the member; leave "" if unknown.
        source_case_id: The reference number of the case that produced the authorization; leave "" if unknown.
        source_authorization_id: The reference number of an authorization (returns the early end of it, if any); leave "" if unknown.
    """
    match = {k: v for k, v in {"review_authorization_id": review_authorization_id, "review_program_id": review_program_id, "customer_id": customer_id, "source_case_id": source_case_id, "source_authorization_id": source_authorization_id}.items() if v}
    if not match:
        return "Error: give at least one reference number to look up review authorizations."
    rows = ctx.find("review_authorizations", **match)
    return str(rows) if rows else f"No matching records found for {match}."


@tool(owner="agent", rw="read")
def find_appeal_programs(ctx: ToolContext, appeal_program_id: str = "", customer_id: str = "", plan_enrollment_id: str = "") -> str:
    """Look up a member's appeal program: package name, status (including runout after coverage
    ends) and dates. Every reference number below is optional; give whichever are known, and
    every record carrying all of them is returned. With none given, nothing is searched.

    Args:
        appeal_program_id: The reference number of the appeal program; leave "" if unknown.
        customer_id: The customer reference number of the member; leave "" if unknown.
        plan_enrollment_id: The reference number of the plan enrollment it belongs to; leave "" if unknown.
    """
    match = {k: v for k, v in {"appeal_program_id": appeal_program_id, "customer_id": customer_id, "plan_enrollment_id": plan_enrollment_id}.items() if v}
    if not match:
        return "Error: give at least one reference number to look up appeal programs."
    rows = ctx.find("appeal_programs", **match)
    return str(rows) if rows else f"No matching records found for {match}."


@tool(owner="agent", rw="read")
def find_appeal_cases(ctx: ToolContext, appeal_case_id: str = "", appeal_program_id: str = "", customer_id: str = "", source_appeal_id: str = "", denied_record_id: str = "") -> str:
    """Look up appeal case history: appeals filed at each level, information requests,
    decisions, withdrawals and external reviews, with the denial appealed, its notice date, the
    drug, priority, timing, requester, timestamps and outcomes. Each follow-up event carries the
    reference number of the filing. Every reference number below is optional; give whichever are
    known, and every record carrying all of them is returned. With none given, nothing is
    searched.

    Args:
        appeal_case_id: The reference number of one appeal event; leave "" if unknown.
        appeal_program_id: The reference number of the appeal program; leave "" if unknown.
        customer_id: The customer reference number of the member; leave "" if unknown.
        source_appeal_id: The reference number of an appeal filing (returns every follow-up event on it); leave "" if unknown.
        denied_record_id: The reference number of the denied review case, exception request or paper claim (returns every appeal of it); leave "" if unknown.
    """
    match = {k: v for k, v in {"appeal_case_id": appeal_case_id, "appeal_program_id": appeal_program_id, "customer_id": customer_id, "source_appeal_id": source_appeal_id, "denied_record_id": denied_record_id}.items() if v}
    if not match:
        return "Error: give at least one reference number to look up appeal cases."
    rows = ctx.find("appeal_cases", **match)
    return str(rows) if rows else f"No matching records found for {match}."


@tool(owner="agent", rw="read")
def find_sponsor_agreements(ctx: ToolContext, sponsor_agreement_id: str = "", customer_id: str = "") -> str:
    """Look up a plan sponsor's PBM services agreement: pricing arrangement, status, funding
    arrangement, signing, go-live, renewal and termination dates, enrolled employees, amount
    owed and rebates not yet settled. Every reference number below is optional; give whichever
    are known, and every record carrying all of them is returned. With none given, nothing is
    searched.

    Args:
        sponsor_agreement_id: The reference number of the agreement; leave "" if unknown.
        customer_id: The customer reference number of the plan sponsor; leave "" if unknown.
    """
    match = {k: v for k, v in {"sponsor_agreement_id": sponsor_agreement_id, "customer_id": customer_id}.items() if v}
    if not match:
        return "Error: give at least one reference number to look up sponsor agreements."
    rows = ctx.find("sponsor_agreements", **match)
    return str(rows) if rows else f"No matching records found for {match}."


@tool(owner="agent", rw="read")
def find_sponsor_invoices(ctx: ToolContext, sponsor_invoice_id: str = "", sponsor_agreement_id: str = "", customer_id: str = "", source_invoice_id: str = "") -> str:
    """Look up a plan sponsor's invoices, payments, late charges and credit memos: billing
    period, dates, amounts, claim counts, employee-months, credit reasons and payment methods.
    Payments, late charges and credits carry the reference number of the invoice they apply to.
    Every reference number below is optional; give whichever are known, and every record
    carrying all of them is returned. With none given, nothing is searched.

    Args:
        sponsor_invoice_id: The reference number of one invoice, payment or credit; leave "" if unknown.
        sponsor_agreement_id: The reference number of the agreement; leave "" if unknown.
        customer_id: The customer reference number of the plan sponsor; leave "" if unknown.
        source_invoice_id: The reference number of an invoice (returns the payments, late charges and credits applied to it); leave "" if unknown.
    """
    match = {k: v for k, v in {"sponsor_invoice_id": sponsor_invoice_id, "sponsor_agreement_id": sponsor_agreement_id, "customer_id": customer_id, "source_invoice_id": source_invoice_id}.items() if v}
    if not match:
        return "Error: give at least one reference number to look up sponsor invoices."
    rows = ctx.find("sponsor_invoices", **match)
    return str(rows) if rows else f"No matching records found for {match}."


@tool(owner="agent", rw="read")
def find_sponsor_rebates(ctx: ToolContext, sponsor_rebate_id: str = "", sponsor_agreement_id: str = "", customer_id: str = "", source_rebate_id: str = "", source_invoice_id: str = "") -> str:
    """Look up a plan sponsor's rebate accruals by quarter, with prescription counts, and the
    payments and invoice offsets that settled them. Every reference number below is optional;
    give whichever are known, and every record carrying all of them is returned. With none
    given, nothing is searched.

    Args:
        sponsor_rebate_id: The reference number of one rebate entry; leave "" if unknown.
        sponsor_agreement_id: The reference number of the agreement; leave "" if unknown.
        customer_id: The customer reference number of the plan sponsor; leave "" if unknown.
        source_rebate_id: The reference number of an accrual (returns its payment or offset); leave "" if unknown.
        source_invoice_id: The reference number of an invoice (returns the rebate offsets applied to it); leave "" if unknown.
    """
    match = {k: v for k, v in {"sponsor_rebate_id": sponsor_rebate_id, "sponsor_agreement_id": sponsor_agreement_id, "customer_id": customer_id, "source_rebate_id": source_rebate_id, "source_invoice_id": source_invoice_id}.items() if v}
    if not match:
        return "Error: give at least one reference number to look up sponsor rebates."
    rows = ctx.find("sponsor_rebates", **match)
    return str(rows) if rows else f"No matching records found for {match}."


@tool(owner="agent", rw="read")
def find_sponsor_operations(ctx: ToolContext, sponsor_operation_id: str = "", sponsor_agreement_id: str = "", customer_id: str = "") -> str:
    """Look up a plan sponsor's eligibility file loads (records received and rejected, outcome)
    and claims audit findings (period audited and amount found). Every reference number below is
    optional; give whichever are known, and every record carrying all of them is returned. With
    none given, nothing is searched.

    Args:
        sponsor_operation_id: The reference number of one operations record; leave "" if unknown.
        sponsor_agreement_id: The reference number of the agreement; leave "" if unknown.
        customer_id: The customer reference number of the plan sponsor; leave "" if unknown.
    """
    match = {k: v for k, v in {"sponsor_operation_id": sponsor_operation_id, "sponsor_agreement_id": sponsor_agreement_id, "customer_id": customer_id}.items() if v}
    if not match:
        return "Error: give at least one reference number to look up sponsor operations."
    rows = ctx.find("sponsor_operations", **match)
    return str(rows) if rows else f"No matching records found for {match}."


@tool(owner="agent", rw="read")
def find_sponsor_service_requests(ctx: ToolContext, sponsor_service_request_id: str = "", sponsor_agreement_id: str = "", customer_id: str = "", disputed_invoice_id: str = "") -> str:
    """Look up a plan sponsor's service requests: termination notices and rescissions,
    implementation cancellations, audit requests, invoice disputes and rebate offset elections,
    with status and dates. Every reference number below is optional; give whichever are known,
    and every record carrying all of them is returned. With none given, nothing is searched.

    Args:
        sponsor_service_request_id: The reference number of one service request; leave "" if unknown.
        sponsor_agreement_id: The reference number of the agreement; leave "" if unknown.
        customer_id: The customer reference number of the plan sponsor; leave "" if unknown.
        disputed_invoice_id: The reference number of an invoice (returns the disputes or offset elections naming it); leave "" if unknown.
    """
    match = {k: v for k, v in {"sponsor_service_request_id": sponsor_service_request_id, "sponsor_agreement_id": sponsor_agreement_id, "customer_id": customer_id, "disputed_invoice_id": disputed_invoice_id}.items() if v}
    if not match:
        return "Error: give at least one reference number to look up sponsor service requests."
    rows = ctx.find("sponsor_service_requests", **match)
    return str(rows) if rows else f"No matching records found for {match}."


@tool(owner="agent", rw="read")
def find_identity_verifications(ctx: ToolContext, verification_id: str = "", customer_id: str = "") -> str:
    """Look up the identity verification outcome recorded for a customer on this call: whether
    verification has passed and when it was last attempted. Every reference number below is
    optional; give whichever are known, and every record carrying all of them is returned. With
    none given, nothing is searched.

    Args:
        verification_id: The reference number of the verification record; leave "" if unknown.
        customer_id: The customer reference number; leave "" if unknown.
    """
    match = {k: v for k, v in {"verification_id": verification_id, "customer_id": customer_id}.items() if v}
    if not match:
        return "Error: give at least one reference number to look up identity verifications."
    rows = ctx.find("identity_verifications", **match)
    return str(rows) if rows else f"No matching records found for {match}."


@tool(owner="agent", rw="read")
def find_handoffs(ctx: ToolContext, handoff_id: str = "", customer_id: str = "") -> str:
    """Look up transfers of a customer to a human representative: the reason recorded and when.
    Every reference number below is optional; give whichever are known, and every record
    carrying all of them is returned. With none given, nothing is searched.

    Args:
        handoff_id: The reference number of the transfer record; leave "" if unknown.
        customer_id: The customer reference number; leave "" if unknown.
    """
    match = {k: v for k, v in {"handoff_id": handoff_id, "customer_id": customer_id}.items() if v}
    if not match:
        return "Error: give at least one reference number to look up handoffs."
    rows = ctx.find("handoffs", **match)
    return str(rows) if rows else f"No matching records found for {match}."


@tool(owner="agent", rw="write")
def verify_customer_identity(ctx: ToolContext, customer_id: str, date_of_birth: str = "",
                             member_number: str = "", phone_number: str = "", email: str = "",
                             zip_code: str = "", tax_id_last4: str = "") -> str:
    """Verify the caller's identity and record the outcome. Identity must be verified before any
    account details are discussed or any business is transacted on a member's or plan sponsor's
    account. This tool performs the comparison itself: it checks each piece of identity
    information the caller states against the customer profile, counts how many match, and
    passes only when at least 2 match. The customer reference number only selects the profile
    and never counts as a match, and a name is not accepted as proof of identity. Callers usually
    give only some of these details, so pass exactly what the caller said and leave the rest
    empty. The outcome is recorded; if a first attempt falls short and a later attempt with more
    information passes, the account is recorded as verified.

    Args:
        customer_id: The customer reference number read from the customer profile lookup. Required; it selects the profile and is not counted as a match.
        date_of_birth: The member's date of birth as stated, written YYYY-MM-DD; leave "" if not stated.
        member_number: The member ID from the prescription card, as stated; leave "" if not stated.
        phone_number: The phone number on file, 10 digits, as stated; leave "" if not stated.
        email: The email address on file, as stated; leave "" if not stated.
        zip_code: The 5-digit ZIP code of the mailing address on file, as stated; leave "" if not stated.
        tax_id_last4: For a plan sponsor, the last four digits of its federal employer identification number, as stated; leave "" if not stated.
    """
    if not customer_id:
        return "Error: customer_id is required; look up the customer first and pass their reference number."
    rows = ctx.find("customers", customer_id=customer_id)
    if not rows:
        return f"Error: no customer {customer_id}; cannot verify."
    rec = rows[0]
    supplied = {"date_of_birth": date_of_birth, "member_number": member_number,
                "phone_number": phone_number, "email": email, "zip_code": zip_code,
                "tax_id_last4": tax_id_last4}
    matched = sum(1 for field, value in supplied.items()
                  if _norm(value) and _norm(value) == _norm(rec.get(field)))
    verified = matched >= 2
    rid = ctx.make_id("ver_", customer_id)
    # Store only the reproducible outcome; upsert and never downgrade a pass.
    prior = ctx.find("identity_verifications", verification_id=rid)
    verified = verified or bool(prior and prior[0].get("verified"))
    if prior:
        ctx.update("identity_verifications", rid, verified=verified, verified_at=ctx.now())
    else:
        ctx.create("identity_verifications", rid, verification_id=rid, customer_id=customer_id,
                   verified=verified, verified_at=ctx.now())
    if verified:
        return f"Identity verified for {customer_id} ({matched} detail(s) matched on this attempt)."
    return (f"Identity NOT verified for {customer_id}: only {matched} of the 2 required details matched. "
            "Ask the caller for another detail on file and try again.")


@tool(owner="agent", rw="write")
def transfer_to_human_agent(ctx: ToolContext, customer_id: str, reason: str) -> str:
    """Transfer the customer to a human representative and record the transfer and its reason.
    Use it in exactly two situations: when no Northbridge Rx policy can resolve what the
    customer is asking for, or when the customer has explicitly asked to speak with a human
    representative 2 times on this call.

    Args:
        customer_id: The customer reference number read from the customer profile lookup (the profile must exist).
        reason: Why the customer is being transferred; exactly one of POLICY_NOT_COVERED (no policy can resolve the request) or CUSTOMER_REQUESTED (the customer has explicitly asked for a human representative 2 times). Never free text.
    """
    allowed = {"POLICY_NOT_COVERED", "CUSTOMER_REQUESTED"}
    if reason not in allowed:
        return f"Error: unknown transfer reason '{reason}'. Valid: {', '.join(sorted(allowed))}."
    if not ctx.find("customers", customer_id=customer_id):
        return f"Error: no customer {customer_id}; cannot record the transfer."
    rid = ctx.make_id("hof_", customer_id, reason)
    ctx.create("handoffs", rid, handoff_id=rid, customer_id=customer_id, reason=reason,
               created_at=ctx.now())
    return f"Transfer to a human representative recorded for {customer_id} ({reason})."

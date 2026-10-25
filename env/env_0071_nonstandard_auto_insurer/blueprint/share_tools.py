"""Shared tools for env_0071_nonstandard_auto_insurer (Cardinal Point Insurance Company).
Path: env/env_0071_nonstandard_auto_insurer/blueprint/share_tools.py

Every tool here is a SHARE tool, always present in its owner's tool list:
  - one record finder per data table (the customers finder doubles as the identity entry);
  - verify_customer_identity: compares stated credentials to the profile, passes at K = 2 matches,
    stores only the verified outcome (upsert, never downgraded);
  - transfer_to_human_agent: the single handoff, reason POLICY_NOT_COVERED or CUSTOMER_REQUESTED
    (the latter once the customer has asked for a person R = 2 times).
Customer-only actions (signing forms, authorizing payments) are hidden task tools, not here.
"""

from erlbench import ToolContext, tool


@tool(owner="agent", rw="read")
def find_auto_policies(ctx: ToolContext, auto_policy_id: str = "", customer_id: str = "", prior_term_policy_id: str = "") -> str:
    """Look up Owner Auto Policy terms (one record per six- or twelve-month term, renewals included): package, garaging state, term dates, status, cancellation and notice details, reinstatement and lapse dates, filing type and premium totals.

    Every reference number is optional; supply whichever ones you hold and every record carrying
    all of them is returned in full. With no reference number at all, every such record is returned.
    When nothing matches, a short notice says so.

    Args:
        auto_policy_id: Id - the reference number of this record itself; leave "" if unknown.
        customer_id: Id - the customer reference number of the person concerned; leave "" if unknown.
        prior_term_policy_id: Id - a linked reference number: the immediately preceding term of the same policy number; leave "" if unknown.
    """
    match = {k: v for k, v in {"auto_policy_id": auto_policy_id, "customer_id": customer_id, "prior_term_policy_id": prior_term_policy_id}.items() if v}
    rows = ctx.find("auto_policies", **match)
    return str(rows) if rows else f"No auto_policies records for {match}."

@tool(owner="agent", rw="read")
def find_auto_premium_transactions(ctx: ToolContext, auto_premium_txn_id: str = "", auto_policy_id: str = "", customer_id: str = "", source_change_id: str = "", reversed_txn_id: str = "") -> str:
    """Look up premium and fee transactions of Owner Auto Policy terms: premium written, additional and return premium, policy fees, reinstatement fees and fee reversals, with their dates, reasons and amounts.

    Every reference number is optional; supply whichever ones you hold and every record carrying
    all of them is returned in full. With no reference number at all, every such record is returned.
    When nothing matches, a short notice says so.

    Args:
        auto_premium_txn_id: Id - the reference number of this record itself; leave "" if unknown.
        auto_policy_id: Id - the reference number of an Owner Auto Policy term; leave "" if unknown.
        customer_id: Id - the customer reference number of the person concerned; leave "" if unknown.
        source_change_id: Id - a linked reference number: driver or vehicle change the premium arises from; leave "" if unknown.
        reversed_txn_id: Id - a linked reference number: for a fee waiver: the fee transaction it reverses; leave "" if unknown.
    """
    match = {k: v for k, v in {"auto_premium_txn_id": auto_premium_txn_id, "auto_policy_id": auto_policy_id, "customer_id": customer_id, "source_change_id": source_change_id, "reversed_txn_id": reversed_txn_id}.items() if v}
    rows = ctx.find("auto_premium_transactions", **match)
    return str(rows) if rows else f"No auto_premium_transactions records for {match}."

@tool(owner="agent", rw="read")
def find_auto_policy_changes(ctx: ToolContext, auto_change_id: str = "", auto_policy_id: str = "", customer_id: str = "", signed_form_id: str = "") -> str:
    """Look up driver and vehicle changes endorsed on Owner Auto Policy terms: drivers added, excluded or removed and vehicles added or removed, with effective dates and premium shares.

    Every reference number is optional; supply whichever ones you hold and every record carrying
    all of them is returned in full. With no reference number at all, every such record is returned.
    When nothing matches, a short notice says so.

    Args:
        auto_change_id: Id - the reference number of this record itself; leave "" if unknown.
        auto_policy_id: Id - the reference number of an Owner Auto Policy term; leave "" if unknown.
        customer_id: Id - the customer reference number of the person concerned; leave "" if unknown.
        signed_form_id: Id - a linked reference number: signed Named Driver Exclusion form backing an exclusion; leave "" if unknown.
    """
    match = {k: v for k, v in {"auto_change_id": auto_change_id, "auto_policy_id": auto_policy_id, "customer_id": customer_id, "signed_form_id": signed_form_id}.items() if v}
    rows = ctx.find("auto_policy_changes", **match)
    return str(rows) if rows else f"No auto_policy_changes records for {match}."

@tool(owner="agent", rw="read")
def find_auto_policy_documents(ctx: ToolContext, auto_document_id: str = "", auto_policy_id: str = "", customer_id: str = "", unpaid_invoice_id: str = "") -> str:
    """Look up notices and signed forms on Owner Auto Policy terms: notices of cancellation for nonpayment, underwriting cancellation and nonrenewal notices, Statements of No Loss and Named Driver Exclusion forms.

    Every reference number is optional; supply whichever ones you hold and every record carrying
    all of them is returned in full. With no reference number at all, every such record is returned.
    When nothing matches, a short notice says so.

    Args:
        auto_document_id: Id - the reference number of this record itself; leave "" if unknown.
        auto_policy_id: Id - the reference number of an Owner Auto Policy term; leave "" if unknown.
        customer_id: Id - the customer reference number of the person concerned; leave "" if unknown.
        unpaid_invoice_id: Id - a linked reference number: for a notice of cancellation: the unpaid billing invoice it is issued for; leave "" if unknown.
    """
    match = {k: v for k, v in {"auto_document_id": auto_document_id, "auto_policy_id": auto_policy_id, "customer_id": customer_id, "unpaid_invoice_id": unpaid_invoice_id}.items() if v}
    rows = ctx.find("auto_policy_documents", **match)
    return str(rows) if rows else f"No auto_policy_documents records for {match}."

@tool(owner="agent", rw="read")
def find_auto_cancellation_requests(ctx: ToolContext, auto_cancel_request_id: str = "", customer_id: str = "", auto_policy_id: str = "") -> str:
    """Look up cancellation requests made by named insureds on Owner Auto Policy terms, with the dates requested and whether the insured has confirmed them.

    Every reference number is optional; supply whichever ones you hold and every record carrying
    all of them is returned in full. With no reference number at all, every such record is returned.
    When nothing matches, a short notice says so.

    Args:
        auto_cancel_request_id: Id - the reference number of this record itself; leave "" if unknown.
        customer_id: Id - the customer reference number of the person concerned; leave "" if unknown.
        auto_policy_id: Id - the reference number of an Owner Auto Policy term; leave "" if unknown.
    """
    match = {k: v for k, v in {"auto_cancel_request_id": auto_cancel_request_id, "customer_id": customer_id, "auto_policy_id": auto_policy_id}.items() if v}
    rows = ctx.find("auto_cancellation_requests", **match)
    return str(rows) if rows else f"No auto_cancellation_requests records for {match}."

@tool(owner="agent", rw="read")
def find_billing_plans(ctx: ToolContext, billing_plan_id: str = "", customer_id: str = "", auto_policy_id: str = "", nonowner_policy_id: str = "") -> str:
    """Look up installment payment plans: the plan type, the policy term billed, status, due day, recurring payment method, certified-funds restriction and current balance.

    Every reference number is optional; supply whichever ones you hold and every record carrying
    all of them is returned in full. With no reference number at all, every such record is returned.
    When nothing matches, a short notice says so.

    Args:
        billing_plan_id: Id - the reference number of this record itself; leave "" if unknown.
        customer_id: Id - the customer reference number of the person concerned; leave "" if unknown.
        auto_policy_id: Id - the reference number of an Owner Auto Policy term; leave "" if unknown.
        nonowner_policy_id: Id - the reference number of a Named Non-Owner Policy term; leave "" if unknown.
    """
    match = {k: v for k, v in {"billing_plan_id": billing_plan_id, "customer_id": customer_id, "auto_policy_id": auto_policy_id, "nonowner_policy_id": nonowner_policy_id}.items() if v}
    rows = ctx.find("billing_plans", **match)
    return str(rows) if rows else f"No billing_plans records for {match}."

@tool(owner="agent", rw="read")
def find_billing_transactions(ctx: ToolContext, billing_txn_id: str = "", billing_plan_id: str = "", customer_id: str = "", related_invoice_id: str = "", related_payment_txn_id: str = "", reversed_fee_txn_id: str = "", source_auto_txn_id: str = "", source_nonowner_txn_id: str = "") -> str:
    """Look up charges, payments and credits on payment plans: premium posted and credited, installment, late, NSF and agent-assisted fees, payments and returned payments, waivers, write-offs and refunds.

    Every reference number is optional; supply whichever ones you hold and every record carrying
    all of them is returned in full. With no reference number at all, every such record is returned.
    When nothing matches, a short notice says so.

    Args:
        billing_txn_id: Id - the reference number of this record itself; leave "" if unknown.
        billing_plan_id: Id - the reference number of an installment payment plan; leave "" if unknown.
        customer_id: Id - the customer reference number of the person concerned; leave "" if unknown.
        related_invoice_id: Id - a linked reference number: invoice a fee or payment relates to; leave "" if unknown.
        related_payment_txn_id: Id - a linked reference number: payment a return, NSF fee or agent-assisted fee relates to; leave "" if unknown.
        reversed_fee_txn_id: Id - a linked reference number: for a fee waiver: the fee transaction reversed; leave "" if unknown.
        source_auto_txn_id: Id - a linked reference number: owner-policy premium transaction posted or credited; leave "" if unknown.
        source_nonowner_txn_id: Id - a linked reference number: non-owner premium transaction posted or credited; leave "" if unknown.
    """
    match = {k: v for k, v in {"billing_txn_id": billing_txn_id, "billing_plan_id": billing_plan_id, "customer_id": customer_id, "related_invoice_id": related_invoice_id, "related_payment_txn_id": related_payment_txn_id, "reversed_fee_txn_id": reversed_fee_txn_id, "source_auto_txn_id": source_auto_txn_id, "source_nonowner_txn_id": source_nonowner_txn_id}.items() if v}
    rows = ctx.find("billing_transactions", **match)
    return str(rows) if rows else f"No billing_transactions records for {match}."

@tool(owner="agent", rw="read")
def find_billing_invoices(ctx: ToolContext, billing_invoice_id: str = "", billing_plan_id: str = "", customer_id: str = "") -> str:
    """Look up invoices issued on payment plans: installment bills, final bills and renewal bills with their due dates, amounts and minimum due.

    Every reference number is optional; supply whichever ones you hold and every record carrying
    all of them is returned in full. With no reference number at all, every such record is returned.
    When nothing matches, a short notice says so.

    Args:
        billing_invoice_id: Id - the reference number of this record itself; leave "" if unknown.
        billing_plan_id: Id - the reference number of an installment payment plan; leave "" if unknown.
        customer_id: Id - the customer reference number of the person concerned; leave "" if unknown.
    """
    match = {k: v for k, v in {"billing_invoice_id": billing_invoice_id, "billing_plan_id": billing_plan_id, "customer_id": customer_id}.items() if v}
    rows = ctx.find("billing_invoices", **match)
    return str(rows) if rows else f"No billing_invoices records for {match}."

@tool(owner="agent", rw="read")
def find_billing_authorizations(ctx: ToolContext, billing_authorization_id: str = "", billing_plan_id: str = "", customer_id: str = "") -> str:
    """Look up recurring bank-draft and card authorizations signed or revoked on payment plans.

    Every reference number is optional; supply whichever ones you hold and every record carrying
    all of them is returned in full. With no reference number at all, every such record is returned.
    When nothing matches, a short notice says so.

    Args:
        billing_authorization_id: Id - the reference number of this record itself; leave "" if unknown.
        billing_plan_id: Id - the reference number of an installment payment plan; leave "" if unknown.
        customer_id: Id - the customer reference number of the person concerned; leave "" if unknown.
    """
    match = {k: v for k, v in {"billing_authorization_id": billing_authorization_id, "billing_plan_id": billing_plan_id, "customer_id": customer_id}.items() if v}
    rows = ctx.find("billing_authorizations", **match)
    return str(rows) if rows else f"No billing_authorizations records for {match}."

@tool(owner="agent", rw="read")
def find_fr_filings(ctx: ToolContext, fr_filing_id: str = "", customer_id: str = "", auto_policy_id: str = "", nonowner_policy_id: str = "", prior_fr_filing_id: str = "") -> str:
    """Look up SR-22 and FR-44 certificate filings with the state: certificate type, filing state, the driver certified, the backing policy term, status, filing, rejection and SR-26 dates and the end of the requirement.

    Every reference number is optional; supply whichever ones you hold and every record carrying
    all of them is returned in full. With no reference number at all, every such record is returned.
    When nothing matches, a short notice says so.

    Args:
        fr_filing_id: Id - the reference number of this record itself; leave "" if unknown.
        customer_id: Id - the customer reference number of the person concerned; leave "" if unknown.
        auto_policy_id: Id - the reference number of an Owner Auto Policy term; leave "" if unknown.
        nonowner_policy_id: Id - the reference number of a Named Non-Owner Policy term; leave "" if unknown.
        prior_fr_filing_id: Id - a linked reference number: earlier filing this one replaces; leave "" if unknown.
    """
    match = {k: v for k, v in {"fr_filing_id": fr_filing_id, "customer_id": customer_id, "auto_policy_id": auto_policy_id, "nonowner_policy_id": nonowner_policy_id, "prior_fr_filing_id": prior_fr_filing_id}.items() if v}
    rows = ctx.find("fr_filings", **match)
    return str(rows) if rows else f"No fr_filings records for {match}."

@tool(owner="agent", rw="read")
def find_fr_filing_transactions(ctx: ToolContext, fr_filing_txn_id: str = "", fr_filing_id: str = "", customer_id: str = "", reversed_fee_txn_id: str = "") -> str:
    """Look up filing fees charged and reversed on SR-22 and FR-44 filings.

    Every reference number is optional; supply whichever ones you hold and every record carrying
    all of them is returned in full. With no reference number at all, every such record is returned.
    When nothing matches, a short notice says so.

    Args:
        fr_filing_txn_id: Id - the reference number of this record itself; leave "" if unknown.
        fr_filing_id: Id - the reference number of an SR-22 or FR-44 certificate filing; leave "" if unknown.
        customer_id: Id - the customer reference number of the person concerned; leave "" if unknown.
        reversed_fee_txn_id: Id - a linked reference number: for a reversal: the fee transaction reversed; leave "" if unknown.
    """
    match = {k: v for k, v in {"fr_filing_txn_id": fr_filing_txn_id, "fr_filing_id": fr_filing_id, "customer_id": customer_id, "reversed_fee_txn_id": reversed_fee_txn_id}.items() if v}
    rows = ctx.find("fr_filing_transactions", **match)
    return str(rows) if rows else f"No fr_filing_transactions records for {match}."

@tool(owner="agent", rw="read")
def find_fr_filing_documents(ctx: ToolContext, fr_document_id: str = "", fr_filing_id: str = "", customer_id: str = "") -> str:
    """Look up certificate copies sent and release requests made on SR-22 and FR-44 filings.

    Every reference number is optional; supply whichever ones you hold and every record carrying
    all of them is returned in full. With no reference number at all, every such record is returned.
    When nothing matches, a short notice says so.

    Args:
        fr_document_id: Id - the reference number of this record itself; leave "" if unknown.
        fr_filing_id: Id - the reference number of an SR-22 or FR-44 certificate filing; leave "" if unknown.
        customer_id: Id - the customer reference number of the person concerned; leave "" if unknown.
    """
    match = {k: v for k, v in {"fr_document_id": fr_document_id, "fr_filing_id": fr_filing_id, "customer_id": customer_id}.items() if v}
    rows = ctx.find("fr_filing_documents", **match)
    return str(rows) if rows else f"No fr_filing_documents records for {match}."

@tool(owner="agent", rw="read")
def find_nonowner_policies(ctx: ToolContext, nonowner_policy_id: str = "", customer_id: str = "", prior_nonowner_term_id: str = "", converted_to_auto_policy_id: str = "") -> str:
    """Look up Named Non-Owner Policy terms: package, residence state, term dates, status, cancellation and notice details, reinstatement and lapse dates, conversion to an owner policy and premium totals.

    Every reference number is optional; supply whichever ones you hold and every record carrying
    all of them is returned in full. With no reference number at all, every such record is returned.
    When nothing matches, a short notice says so.

    Args:
        nonowner_policy_id: Id - the reference number of this record itself; leave "" if unknown.
        customer_id: Id - the customer reference number of the person concerned; leave "" if unknown.
        prior_nonowner_term_id: Id - a linked reference number: immediately preceding term of the same policy number; leave "" if unknown.
        converted_to_auto_policy_id: Id - a linked reference number: Owner Auto Policy term that replaced this term; leave "" if unknown.
    """
    match = {k: v for k, v in {"nonowner_policy_id": nonowner_policy_id, "customer_id": customer_id, "prior_nonowner_term_id": prior_nonowner_term_id, "converted_to_auto_policy_id": converted_to_auto_policy_id}.items() if v}
    rows = ctx.find("nonowner_policies", **match)
    return str(rows) if rows else f"No nonowner_policies records for {match}."

@tool(owner="agent", rw="read")
def find_nonowner_premium_transactions(ctx: ToolContext, nonowner_premium_txn_id: str = "", nonowner_policy_id: str = "", customer_id: str = "", reversed_txn_id: str = "") -> str:
    """Look up premium and fee transactions of Named Non-Owner Policy terms.

    Every reference number is optional; supply whichever ones you hold and every record carrying
    all of them is returned in full. With no reference number at all, every such record is returned.
    When nothing matches, a short notice says so.

    Args:
        nonowner_premium_txn_id: Id - the reference number of this record itself; leave "" if unknown.
        nonowner_policy_id: Id - the reference number of a Named Non-Owner Policy term; leave "" if unknown.
        customer_id: Id - the customer reference number of the person concerned; leave "" if unknown.
        reversed_txn_id: Id - a linked reference number: for a fee waiver: the fee transaction reversed; leave "" if unknown.
    """
    match = {k: v for k, v in {"nonowner_premium_txn_id": nonowner_premium_txn_id, "nonowner_policy_id": nonowner_policy_id, "customer_id": customer_id, "reversed_txn_id": reversed_txn_id}.items() if v}
    rows = ctx.find("nonowner_premium_transactions", **match)
    return str(rows) if rows else f"No nonowner_premium_transactions records for {match}."

@tool(owner="agent", rw="read")
def find_nonowner_documents(ctx: ToolContext, nonowner_document_id: str = "", nonowner_policy_id: str = "", customer_id: str = "", unpaid_invoice_id: str = "") -> str:
    """Look up notices and signed statements on Named Non-Owner Policy terms: Non-Owner Statements, notices of cancellation, Statements of No Loss and nonrenewal notices.

    Every reference number is optional; supply whichever ones you hold and every record carrying
    all of them is returned in full. With no reference number at all, every such record is returned.
    When nothing matches, a short notice says so.

    Args:
        nonowner_document_id: Id - the reference number of this record itself; leave "" if unknown.
        nonowner_policy_id: Id - the reference number of a Named Non-Owner Policy term; leave "" if unknown.
        customer_id: Id - the customer reference number of the person concerned; leave "" if unknown.
        unpaid_invoice_id: Id - a linked reference number: notice of cancellation: the unpaid invoice; leave "" if unknown.
    """
    match = {k: v for k, v in {"nonowner_document_id": nonowner_document_id, "nonowner_policy_id": nonowner_policy_id, "customer_id": customer_id, "unpaid_invoice_id": unpaid_invoice_id}.items() if v}
    rows = ctx.find("nonowner_documents", **match)
    return str(rows) if rows else f"No nonowner_documents records for {match}."

@tool(owner="agent", rw="read")
def find_nonowner_cancellation_requests(ctx: ToolContext, nonowner_cancel_request_id: str = "", customer_id: str = "", nonowner_policy_id: str = "") -> str:
    """Look up cancellation requests made by named insureds on Named Non-Owner Policy terms.

    Every reference number is optional; supply whichever ones you hold and every record carrying
    all of them is returned in full. With no reference number at all, every such record is returned.
    When nothing matches, a short notice says so.

    Args:
        nonowner_cancel_request_id: Id - the reference number of this record itself; leave "" if unknown.
        customer_id: Id - the customer reference number of the person concerned; leave "" if unknown.
        nonowner_policy_id: Id - the reference number of a Named Non-Owner Policy term; leave "" if unknown.
    """
    match = {k: v for k, v in {"nonowner_cancel_request_id": nonowner_cancel_request_id, "customer_id": customer_id, "nonowner_policy_id": nonowner_policy_id}.items() if v}
    rows = ctx.find("nonowner_cancellation_requests", **match)
    return str(rows) if rows else f"No nonowner_cancellation_requests records for {match}."

@tool(owner="agent", rw="read")
def find_physdam_coverages(ctx: ToolContext, physdam_coverage_id: str = "", customer_id: str = "", auto_policy_id: str = "") -> str:
    """Look up comprehensive and collision coverages on insured vehicles: deductible package, vehicle, loss payee, inspection dates, status and totals.

    Every reference number is optional; supply whichever ones you hold and every record carrying
    all of them is returned in full. With no reference number at all, every such record is returned.
    When nothing matches, a short notice says so.

    Args:
        physdam_coverage_id: Id - the reference number of this record itself; leave "" if unknown.
        customer_id: Id - the customer reference number of the person concerned; leave "" if unknown.
        auto_policy_id: Id - the reference number of an Owner Auto Policy term; leave "" if unknown.
    """
    match = {k: v for k, v in {"physdam_coverage_id": physdam_coverage_id, "customer_id": customer_id, "auto_policy_id": auto_policy_id}.items() if v}
    rows = ctx.find("physdam_coverages", **match)
    return str(rows) if rows else f"No physdam_coverages records for {match}."

@tool(owner="agent", rw="read")
def find_physdam_premium_transactions(ctx: ToolContext, physdam_premium_txn_id: str = "", physdam_coverage_id: str = "", customer_id: str = "") -> str:
    """Look up premium charged and returned on comprehensive and collision coverages.

    Every reference number is optional; supply whichever ones you hold and every record carrying
    all of them is returned in full. With no reference number at all, every such record is returned.
    When nothing matches, a short notice says so.

    Args:
        physdam_premium_txn_id: Id - the reference number of this record itself; leave "" if unknown.
        physdam_coverage_id: Id - the reference number of a vehicle's comprehensive and collision coverage; leave "" if unknown.
        customer_id: Id - the customer reference number of the person concerned; leave "" if unknown.
    """
    match = {k: v for k, v in {"physdam_premium_txn_id": physdam_premium_txn_id, "physdam_coverage_id": physdam_coverage_id, "customer_id": customer_id}.items() if v}
    rows = ctx.find("physdam_premium_transactions", **match)
    return str(rows) if rows else f"No physdam_premium_transactions records for {match}."

@tool(owner="agent", rw="read")
def find_physdam_claim_events(ctx: ToolContext, physdam_claim_event_id: str = "", physdam_coverage_id: str = "", customer_id: str = "", auto_policy_id: str = "") -> str:
    """Look up claim file entries on comprehensive and collision claims: first reports, coverage decisions, estimates and supplements, and total loss declarations.

    Every reference number is optional; supply whichever ones you hold and every record carrying
    all of them is returned in full. With no reference number at all, every such record is returned.
    When nothing matches, a short notice says so.

    Args:
        physdam_claim_event_id: Id - the reference number of this record itself; leave "" if unknown.
        physdam_coverage_id: Id - the reference number of a vehicle's comprehensive and collision coverage; leave "" if unknown.
        customer_id: Id - the customer reference number of the person concerned; leave "" if unknown.
        auto_policy_id: Id - the reference number of an Owner Auto Policy term; leave "" if unknown.
    """
    match = {k: v for k, v in {"physdam_claim_event_id": physdam_claim_event_id, "physdam_coverage_id": physdam_coverage_id, "customer_id": customer_id, "auto_policy_id": auto_policy_id}.items() if v}
    rows = ctx.find("physdam_claim_events", **match)
    return str(rows) if rows else f"No physdam_claim_events records for {match}."

@tool(owner="agent", rw="read")
def find_physdam_claim_payments(ctx: ToolContext, physdam_payment_id: str = "", physdam_coverage_id: str = "", customer_id: str = "") -> str:
    """Look up payments and recoveries on comprehensive and collision claims: repair, total loss, towing and storage payments, deductible reimbursements, salvage and subrogation recoveries.

    Every reference number is optional; supply whichever ones you hold and every record carrying
    all of them is returned in full. With no reference number at all, every such record is returned.
    When nothing matches, a short notice says so.

    Args:
        physdam_payment_id: Id - the reference number of this record itself; leave "" if unknown.
        physdam_coverage_id: Id - the reference number of a vehicle's comprehensive and collision coverage; leave "" if unknown.
        customer_id: Id - the customer reference number of the person concerned; leave "" if unknown.
    """
    match = {k: v for k, v in {"physdam_payment_id": physdam_payment_id, "physdam_coverage_id": physdam_coverage_id, "customer_id": customer_id}.items() if v}
    rows = ctx.find("physdam_claim_payments", **match)
    return str(rows) if rows else f"No physdam_claim_payments records for {match}."

@tool(owner="agent", rw="read")
def find_rental_coverages(ctx: ToolContext, rental_coverage_id: str = "", customer_id: str = "", auto_policy_id: str = "", physdam_coverage_id: str = "") -> str:
    """Look up rental reimbursement coverages on insured vehicles: package, vehicle, status and totals.

    Every reference number is optional; supply whichever ones you hold and every record carrying
    all of them is returned in full. With no reference number at all, every such record is returned.
    When nothing matches, a short notice says so.

    Args:
        rental_coverage_id: Id - the reference number of this record itself; leave "" if unknown.
        customer_id: Id - the customer reference number of the person concerned; leave "" if unknown.
        auto_policy_id: Id - the reference number of an Owner Auto Policy term; leave "" if unknown.
        physdam_coverage_id: Id - the reference number of a vehicle's comprehensive and collision coverage; leave "" if unknown.
    """
    match = {k: v for k, v in {"rental_coverage_id": rental_coverage_id, "customer_id": customer_id, "auto_policy_id": auto_policy_id, "physdam_coverage_id": physdam_coverage_id}.items() if v}
    rows = ctx.find("rental_coverages", **match)
    return str(rows) if rows else f"No rental_coverages records for {match}."

@tool(owner="agent", rw="read")
def find_rental_premium_transactions(ctx: ToolContext, rental_premium_txn_id: str = "", rental_coverage_id: str = "", customer_id: str = "") -> str:
    """Look up premium charged and returned on rental reimbursement coverages.

    Every reference number is optional; supply whichever ones you hold and every record carrying
    all of them is returned in full. With no reference number at all, every such record is returned.
    When nothing matches, a short notice says so.

    Args:
        rental_premium_txn_id: Id - the reference number of this record itself; leave "" if unknown.
        rental_coverage_id: Id - the reference number of a vehicle's rental reimbursement coverage; leave "" if unknown.
        customer_id: Id - the customer reference number of the person concerned; leave "" if unknown.
    """
    match = {k: v for k, v in {"rental_premium_txn_id": rental_premium_txn_id, "rental_coverage_id": rental_coverage_id, "customer_id": customer_id}.items() if v}
    rows = ctx.find("rental_premium_transactions", **match)
    return str(rows) if rows else f"No rental_premium_transactions records for {match}."

@tool(owner="agent", rw="read")
def find_rental_benefit_transactions(ctx: ToolContext, rental_benefit_txn_id: str = "", rental_coverage_id: str = "", customer_id: str = "", rental_authorization_id: str = "", reversed_benefit_txn_id: str = "") -> str:
    """Look up rental benefits paid and reversed on claims.

    Every reference number is optional; supply whichever ones you hold and every record carrying
    all of them is returned in full. With no reference number at all, every such record is returned.
    When nothing matches, a short notice says so.

    Args:
        rental_benefit_txn_id: Id - the reference number of this record itself; leave "" if unknown.
        rental_coverage_id: Id - the reference number of a vehicle's rental reimbursement coverage; leave "" if unknown.
        customer_id: Id - the customer reference number of the person concerned; leave "" if unknown.
        rental_authorization_id: Id - a linked reference number: authorization the payment is for; leave "" if unknown.
        reversed_benefit_txn_id: Id - a linked reference number: for a reversal: the payment reversed; leave "" if unknown.
    """
    match = {k: v for k, v in {"rental_benefit_txn_id": rental_benefit_txn_id, "rental_coverage_id": rental_coverage_id, "customer_id": customer_id, "rental_authorization_id": rental_authorization_id, "reversed_benefit_txn_id": reversed_benefit_txn_id}.items() if v}
    rows = ctx.find("rental_benefit_transactions", **match)
    return str(rows) if rows else f"No rental_benefit_transactions records for {match}."

@tool(owner="agent", rw="read")
def find_rental_authorizations(ctx: ToolContext, rental_authorization_id: str = "", rental_coverage_id: str = "", customer_id: str = "") -> str:
    """Look up rental authorizations issued and closed on claims.

    Every reference number is optional; supply whichever ones you hold and every record carrying
    all of them is returned in full. With no reference number at all, every such record is returned.
    When nothing matches, a short notice says so.

    Args:
        rental_authorization_id: Id - the reference number of this record itself; leave "" if unknown.
        rental_coverage_id: Id - the reference number of a vehicle's rental reimbursement coverage; leave "" if unknown.
        customer_id: Id - the customer reference number of the person concerned; leave "" if unknown.
    """
    match = {k: v for k, v in {"rental_authorization_id": rental_authorization_id, "rental_coverage_id": rental_coverage_id, "customer_id": customer_id}.items() if v}
    rows = ctx.find("rental_authorizations", **match)
    return str(rows) if rows else f"No rental_authorizations records for {match}."

@tool(owner="agent", rw="read")
def find_towing_coverages(ctx: ToolContext, towing_coverage_id: str = "", customer_id: str = "", auto_policy_id: str = "") -> str:
    """Look up towing and labor coverages on insured vehicles: package, vehicle, status and totals.

    Every reference number is optional; supply whichever ones you hold and every record carrying
    all of them is returned in full. With no reference number at all, every such record is returned.
    When nothing matches, a short notice says so.

    Args:
        towing_coverage_id: Id - the reference number of this record itself; leave "" if unknown.
        customer_id: Id - the customer reference number of the person concerned; leave "" if unknown.
        auto_policy_id: Id - the reference number of an Owner Auto Policy term; leave "" if unknown.
    """
    match = {k: v for k, v in {"towing_coverage_id": towing_coverage_id, "customer_id": customer_id, "auto_policy_id": auto_policy_id}.items() if v}
    rows = ctx.find("towing_coverages", **match)
    return str(rows) if rows else f"No towing_coverages records for {match}."

@tool(owner="agent", rw="read")
def find_towing_premium_transactions(ctx: ToolContext, towing_premium_txn_id: str = "", towing_coverage_id: str = "", customer_id: str = "") -> str:
    """Look up premium charged and returned on towing and labor coverages.

    Every reference number is optional; supply whichever ones you hold and every record carrying
    all of them is returned in full. With no reference number at all, every such record is returned.
    When nothing matches, a short notice says so.

    Args:
        towing_premium_txn_id: Id - the reference number of this record itself; leave "" if unknown.
        towing_coverage_id: Id - the reference number of a vehicle's towing and labor coverage; leave "" if unknown.
        customer_id: Id - the customer reference number of the person concerned; leave "" if unknown.
    """
    match = {k: v for k, v in {"towing_premium_txn_id": towing_premium_txn_id, "towing_coverage_id": towing_coverage_id, "customer_id": customer_id}.items() if v}
    rows = ctx.find("towing_premium_transactions", **match)
    return str(rows) if rows else f"No towing_premium_transactions records for {match}."

@tool(owner="agent", rw="read")
def find_towing_service_events(ctx: ToolContext, towing_service_event_id: str = "", towing_coverage_id: str = "", customer_id: str = "") -> str:
    """Look up roadside dispatches and reimbursement requests on towing and labor coverages.

    Every reference number is optional; supply whichever ones you hold and every record carrying
    all of them is returned in full. With no reference number at all, every such record is returned.
    When nothing matches, a short notice says so.

    Args:
        towing_service_event_id: Id - the reference number of this record itself; leave "" if unknown.
        towing_coverage_id: Id - the reference number of a vehicle's towing and labor coverage; leave "" if unknown.
        customer_id: Id - the customer reference number of the person concerned; leave "" if unknown.
    """
    match = {k: v for k, v in {"towing_service_event_id": towing_service_event_id, "towing_coverage_id": towing_coverage_id, "customer_id": customer_id}.items() if v}
    rows = ctx.find("towing_service_events", **match)
    return str(rows) if rows else f"No towing_service_events records for {match}."

@tool(owner="agent", rw="read")
def find_towing_benefit_transactions(ctx: ToolContext, towing_benefit_txn_id: str = "", towing_coverage_id: str = "", customer_id: str = "", reversed_benefit_txn_id: str = "") -> str:
    """Look up towing and labor benefits paid and reversed.

    Every reference number is optional; supply whichever ones you hold and every record carrying
    all of them is returned in full. With no reference number at all, every such record is returned.
    When nothing matches, a short notice says so.

    Args:
        towing_benefit_txn_id: Id - the reference number of this record itself; leave "" if unknown.
        towing_coverage_id: Id - the reference number of a vehicle's towing and labor coverage; leave "" if unknown.
        customer_id: Id - the customer reference number of the person concerned; leave "" if unknown.
        reversed_benefit_txn_id: Id - a linked reference number: for a reversal: payment reversed; leave "" if unknown.
    """
    match = {k: v for k, v in {"towing_benefit_txn_id": towing_benefit_txn_id, "towing_coverage_id": towing_coverage_id, "customer_id": customer_id, "reversed_benefit_txn_id": reversed_benefit_txn_id}.items() if v}
    rows = ctx.find("towing_benefit_transactions", **match)
    return str(rows) if rows else f"No towing_benefit_transactions records for {match}."

@tool(owner="agent", rw="read")
def find_identity_verifications(ctx: ToolContext, verification_id: str = "", customer_id: str = "") -> str:
    """Look up identity verification outcomes recorded for customers.

    Every reference number is optional; supply whichever ones you hold and every record carrying
    all of them is returned in full. With no reference number at all, every such record is returned.
    When nothing matches, a short notice says so.

    Args:
        verification_id: Id - the reference number of this record itself; leave "" if unknown.
        customer_id: Id - the customer reference number of the person concerned; leave "" if unknown.
    """
    match = {k: v for k, v in {"verification_id": verification_id, "customer_id": customer_id}.items() if v}
    rows = ctx.find("identity_verifications", **match)
    return str(rows) if rows else f"No identity_verifications records for {match}."

@tool(owner="agent", rw="read")
def find_human_handoffs(ctx: ToolContext, handoff_id: str = "", customer_id: str = "") -> str:
    """Look up transfers of customers to a human representative and their reasons.

    Every reference number is optional; supply whichever ones you hold and every record carrying
    all of them is returned in full. With no reference number at all, every such record is returned.
    When nothing matches, a short notice says so.

    Args:
        handoff_id: Id - the reference number of this record itself; leave "" if unknown.
        customer_id: Id - the customer reference number of the person concerned; leave "" if unknown.
    """
    match = {k: v for k, v in {"handoff_id": handoff_id, "customer_id": customer_id}.items() if v}
    rows = ctx.find("human_handoffs", **match)
    return str(rows) if rows else f"No human_handoffs records for {match}."

@tool(owner="agent", rw="read")
def find_customers(ctx: ToolContext, customer_id: str = "", name: str = "", phone_number: str = "", email: str = "") -> str:
    """Look up a customer profile to establish whose account the call is about.

    Search by the customer reference number, or by what the caller can state: full name, phone
    number or email address. Every criterion is optional, but at least one is needed; spacing,
    punctuation and letter case in what the caller says do not matter. The profile returned shows
    the name, phone number, email, date of birth, last four characters of the driver's license,
    ZIP code, mailing address, home state and the date the profile was opened. Finding a profile
    does not verify the caller's identity; that is a separate step.

    Args:
        customer_id: Id - the customer reference number; leave "" if unknown.
        name: Verbatim - the caller's full name as they state it; leave "" if not given.
        phone_number: Fixed format - the phone number on the profile, 10 digits; leave "" if not given.
        email: Verbatim - the email address on the profile; leave "" if not given.
    """
    match = {k: v for k, v in {"customer_id": customer_id, "name": name,
                               "phone_number": phone_number, "email": email}.items() if v}
    if not match:
        return "Error: provide at least one id or attribute to find the customer."
    rows = ctx.fuzzy_find("customers", **match)
    if not rows:
        return f"No customer matches {match}."
    if len(rows) > 1:
        return f"Error: {len(rows)} customers match {match}; ask for one more attribute to disambiguate."
    return str(rows[0])


@tool(owner="agent", rw="write")
def verify_customer_identity(ctx: ToolContext, customer_id: str, phone_number: str = "", email: str = "",
                             date_of_birth: str = "", drivers_license_last4: str = "", zip_code: str = "") -> str:
    """Verify the caller's identity and record the outcome.

    Identity must be verified before any policy, billing, filing or claim business is looked into or
    transacted for the caller. This tool makes the comparison itself: it checks each piece of
    identity information the caller states against the customer profile, counts how many match, and
    passes only when at least 2 match. The customer reference number only retrieves the profile and
    never counts as a match. Callers usually state only some of these details, so pass exactly the
    values the caller gave, as given, and leave the rest empty. The outcome is recorded; if a first
    attempt fails and a later attempt with more information passes, the pass stands.

    Args:
        customer_id: Id - the customer reference number read from the customer profile lookup. Required; used only to retrieve the profile and not counted as a match.
        phone_number: Fixed format - the phone number on the profile as the caller states it, 10 digits; leave "" if not stated.
        email: Verbatim - the email address on the profile as the caller states it; leave "" if not stated.
        date_of_birth: Fixed format - the caller's date of birth, YYYY-MM-DD; leave "" if not stated.
        drivers_license_last4: Fixed format - the last four characters of the caller's driver's license number; leave "" if not stated.
        zip_code: Fixed format - the 5-digit ZIP code of the caller's residence address; leave "" if not stated.
    """
    if not customer_id:
        return "Error: customer_id is required; locate the customer first and pass their id."
    rows = ctx.find("customers", customer_id=customer_id)
    if not rows:
        return f"Error: no customer {customer_id}; cannot verify."
    rec = rows[0]
    # The tool owns the comparison; the locator customer_id is deliberately not a credential.
    supplied = {"phone_number": phone_number, "email": email, "date_of_birth": date_of_birth,
                "drivers_license_last4": drivers_license_last4, "zip_code": zip_code}
    matched = sum(1 for field, value in supplied.items()
                  if value and str(rec.get(field) or "").strip().lower() == str(value).strip().lower())
    verified = matched >= 2
    rid = ctx.make_id("ver_", customer_id)
    # Store only the reproducible outcome; upsert and never downgrade a prior pass.
    prior = ctx.find("identity_verifications", verification_id=rid)
    verified = verified or bool(prior and prior[0].get("verified"))
    if prior:
        ctx.update("identity_verifications", rid, verified=verified, verified_at=ctx.now())
    else:
        ctx.create("identity_verifications", rid, verification_id=rid, customer_id=customer_id,
                   verified=verified, verified_at=ctx.now())
    return (f"Identity verified for {customer_id} ({matched} detail(s) matched)." if verified
            else f"Identity NOT verified for {customer_id} (only {matched} of the required 2 details matched). "
                 "Ask the caller for another detail on file and call this tool again.")


@tool(owner="agent", rw="write")
def transfer_to_human_agent(ctx: ToolContext, customer_id: str, reason: str) -> str:
    """Hand the customer over to a human representative and record the handoff and its reason.

    Use it when no Cardinal Point rule lets the request be resolved here (reason POLICY_NOT_COVERED),
    or when the customer has explicitly asked to speak with a person at least 2 times
    (reason CUSTOMER_REQUESTED).

    Args:
        customer_id: Id - the customer reference number read from the customer profile lookup (the profile must exist).
        reason: Enum - exactly one of POLICY_NOT_COVERED or CUSTOMER_REQUESTED, never free text.
            POLICY_NOT_COVERED - no rule available to this desk resolves the request;
            CUSTOMER_REQUESTED - the customer has explicitly asked for a human representative at least 2 times.
    """
    allowed = {"POLICY_NOT_COVERED", "CUSTOMER_REQUESTED"}
    if reason not in allowed:
        return f"Error: unknown handoff reason '{reason}'. Valid: {', '.join(sorted(allowed))}."
    if not ctx.find("customers", customer_id=customer_id):
        return f"Error: no customer {customer_id}; cannot record handoff."
    rid = ctx.make_id("hof_", customer_id, reason)
    ctx.create("human_handoffs", rid, handoff_id=rid, customer_id=customer_id,
               reason=reason, created_at=ctx.now())
    return f"Handoff to a human representative recorded for {customer_id} ({reason})."

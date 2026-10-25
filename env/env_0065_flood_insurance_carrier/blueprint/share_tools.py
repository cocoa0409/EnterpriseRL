"""Shared tools for env_0065_flood_insurance_carrier (Tidemark Flood Insurance Company).

Every tool here is always available. The record finders cover every kind of record Tidemark keeps, the
customer finder doubles as the way to locate a caller's profile from what they can state, and the two
write tools record identity verification and transfers to a human representative.
"""

from erlbench import ToolContext, tool


@tool(owner="agent", rw="read")
def find_dwelling_policies(ctx: ToolContext, dwelling_policy_id: str = "", customer_id: str = "") -> str:
    """Look up NFIP Dwelling Form flood policies serviced by Tidemark. Each result shows the policy number,
    occupancy tier, status, insured address and flood zone, building and contents limits and
    deductibles, policy term and effective dates, the waiting-period basis, mortgagee and loan
    details, Elevation Certificate rating facts, the rated premium lines for the term, the current
    balance and any cancellation details. Every reference number below is optional; supply whichever
    are known and all matching records are returned, or a message saying none were found.

    Args:
        dwelling_policy_id: The reference number of the NFIP Dwelling Form policy; leave "" if unknown.
        customer_id: The customer reference number of the policyholder, lender or account holder; leave "" if unknown.
    """
    match = {k: v for k, v in {"dwelling_policy_id": dwelling_policy_id, "customer_id": customer_id}.items() if v}
    rows = ctx.find("dwelling_policies", **match)
    return str(rows) if rows else f"No dwelling_policies records for {match}."

@tool(owner="agent", rw="read")
def find_dwelling_billing(ctx: ToolContext, dwelling_billing_id: str = "", dwelling_policy_id: str = "", customer_id: str = "", reference_id: str = "") -> str:
    """Look up the premium account entries of NFIP Dwelling Form policies: each premium component booked
    for a term, payments received, credits from cancellations or re-rating, and refunds issued, with
    dates, amounts, references and payees. Every reference number below is optional; supply
    whichever are known and all matching records are returned, or a message saying none were found.

    Args:
        dwelling_billing_id: The reference number of this entry itself; leave "" if unknown.
        dwelling_policy_id: The reference number of the NFIP Dwelling Form policy; leave "" if unknown.
        customer_id: The customer reference number of the policyholder, lender or account holder; leave "" if unknown.
        reference_id: The reference number of the record that caused the entry (for example an endorsement, certificate review or cancellation request, or the policy itself); leave "" if unknown.
    """
    match = {k: v for k, v in {"dwelling_billing_id": dwelling_billing_id, "dwelling_policy_id": dwelling_policy_id, "customer_id": customer_id, "reference_id": reference_id}.items() if v}
    rows = ctx.find("dwelling_billing", **match)
    return str(rows) if rows else f"No dwelling_billing records for {match}."

@tool(owner="agent", rw="read")
def find_dwelling_claims(ctx: ToolContext, dwelling_claim_event_id: str = "", dwelling_policy_id: str = "", customer_id: str = "") -> str:
    """Look up the claim files of NFIP Dwelling Form policies: first notices of loss, adjuster reports with
    measured losses, proofs of loss received, claim payments and voided payments, and written
    denials, all tied together by claim number. Every reference number below is optional; supply
    whichever are known and all matching records are returned, or a message saying none were found.

    Args:
        dwelling_claim_event_id: The reference number of this entry itself; leave "" if unknown.
        dwelling_policy_id: The reference number of the NFIP Dwelling Form policy; leave "" if unknown.
        customer_id: The customer reference number of the policyholder, lender or account holder; leave "" if unknown.
    """
    match = {k: v for k, v in {"dwelling_claim_event_id": dwelling_claim_event_id, "dwelling_policy_id": dwelling_policy_id, "customer_id": customer_id}.items() if v}
    rows = ctx.find("dwelling_claims", **match)
    return str(rows) if rows else f"No dwelling_claims records for {match}."

@tool(owner="agent", rw="read")
def find_dwelling_changes(ctx: ToolContext, dwelling_change_id: str = "", dwelling_policy_id: str = "", customer_id: str = "") -> str:
    """Look up the servicing documents of NFIP Dwelling Form policies: endorsements with their effective
    dates and requested values, Elevation Certificates received and their certified elevations,
    renewal bills with the indicated premium, and notices sent to mortgagees. Every reference number
    below is optional; supply whichever are known and all matching records are returned, or a
    message saying none were found.

    Args:
        dwelling_change_id: The reference number of this entry itself; leave "" if unknown.
        dwelling_policy_id: The reference number of the NFIP Dwelling Form policy; leave "" if unknown.
        customer_id: The customer reference number of the policyholder, lender or account holder; leave "" if unknown.
    """
    match = {k: v for k, v in {"dwelling_change_id": dwelling_change_id, "dwelling_policy_id": dwelling_policy_id, "customer_id": customer_id}.items() if v}
    rows = ctx.find("dwelling_changes", **match)
    return str(rows) if rows else f"No dwelling_changes records for {match}."

@tool(owner="agent", rw="read")
def find_dwelling_requests(ctx: ToolContext, dwelling_request_id: str = "", customer_id: str = "", dwelling_policy_id: str = "", assignee_customer_id: str = "") -> str:
    """Look up cancellation and assignment requests on NFIP Dwelling Form policies, showing the requested
    reason and effective date, the supporting document and lender release on file, the buyer named
    in an assignment, and whether the request is awaiting signature, signed or withdrawn. Every
    reference number below is optional; supply whichever are known and all matching records are
    returned, or a message saying none were found.

    Args:
        dwelling_request_id: The reference number of this entry itself; leave "" if unknown.
        customer_id: The customer reference number of the policyholder, lender or account holder; leave "" if unknown.
        dwelling_policy_id: The reference number of the NFIP Dwelling Form policy; leave "" if unknown.
        assignee_customer_id: The customer reference number of the buyer named in an assignment request; leave "" if unknown.
    """
    match = {k: v for k, v in {"dwelling_request_id": dwelling_request_id, "customer_id": customer_id, "dwelling_policy_id": dwelling_policy_id, "assignee_customer_id": assignee_customer_id}.items() if v}
    rows = ctx.find("dwelling_requests", **match)
    return str(rows) if rows else f"No dwelling_requests records for {match}."

@tool(owner="agent", rw="read")
def find_identity_verifications(ctx: ToolContext, verification_id: str = "", customer_id: str = "") -> str:
    """Look up the outcome of identity verification recorded for a customer during this service contact,
    showing whether the caller has been verified and when. Every reference number below is optional;
    supply whichever are known and all matching records are returned, or a message saying none were
    found.

    Args:
        verification_id: The reference number of this entry itself; leave "" if unknown.
        customer_id: The customer reference number of the policyholder, lender or account holder; leave "" if unknown.
    """
    match = {k: v for k, v in {"verification_id": verification_id, "customer_id": customer_id}.items() if v}
    rows = ctx.find("identity_verifications", **match)
    return str(rows) if rows else f"No identity_verifications records for {match}."

@tool(owner="agent", rw="read")
def find_handoffs(ctx: ToolContext, handoff_id: str = "", customer_id: str = "") -> str:
    """Look up transfers of a customer to a human representative, with the reason recorded and the time of
    the transfer. Every reference number below is optional; supply whichever are known and all
    matching records are returned, or a message saying none were found.

    Args:
        handoff_id: The reference number of this entry itself; leave "" if unknown.
        customer_id: The customer reference number of the policyholder, lender or account holder; leave "" if unknown.
    """
    match = {k: v for k, v in {"handoff_id": handoff_id, "customer_id": customer_id}.items() if v}
    rows = ctx.find("handoffs", **match)
    return str(rows) if rows else f"No handoffs records for {match}."

@tool(owner="agent", rw="read")
def find_nfipcom_policies(ctx: ToolContext, nfipcom_policy_id: str = "", customer_id: str = "") -> str:
    """Look up NFIP General Property Form and Residential Condominium Building Association Policy (RCBAP)
    records serviced by Tidemark. Each result shows the policy number, form and occupancy tier,
    status, building address and flood zone, number of units, limits, deductibles, replacement cost
    value, terms and effective dates, mortgagee details, Elevation Certificate facts, rated premium
    lines, balance and any cancellation details. Every reference number below is optional; supply
    whichever are known and all matching records are returned, or a message saying none were found.

    Args:
        nfipcom_policy_id: The reference number of the General Property Form or RCBAP policy; leave "" if unknown.
        customer_id: The customer reference number of the policyholder, lender or account holder; leave "" if unknown.
    """
    match = {k: v for k, v in {"nfipcom_policy_id": nfipcom_policy_id, "customer_id": customer_id}.items() if v}
    rows = ctx.find("nfipcom_policies", **match)
    return str(rows) if rows else f"No nfipcom_policies records for {match}."

@tool(owner="agent", rw="read")
def find_nfipcom_billing(ctx: ToolContext, nfipcom_billing_id: str = "", nfipcom_policy_id: str = "", customer_id: str = "", reference_id: str = "") -> str:
    """Look up the premium account entries of General Property Form and RCBAP policies: components booked
    per term, payments, credits and refunds with their dates, amounts and references. Every
    reference number below is optional; supply whichever are known and all matching records are
    returned, or a message saying none were found.

    Args:
        nfipcom_billing_id: The reference number of this entry itself; leave "" if unknown.
        nfipcom_policy_id: The reference number of the General Property Form or RCBAP policy; leave "" if unknown.
        customer_id: The customer reference number of the policyholder, lender or account holder; leave "" if unknown.
        reference_id: The reference number of the record that caused the entry (for example an endorsement, certificate review or cancellation request, or the policy itself); leave "" if unknown.
    """
    match = {k: v for k, v in {"nfipcom_billing_id": nfipcom_billing_id, "nfipcom_policy_id": nfipcom_policy_id, "customer_id": customer_id, "reference_id": reference_id}.items() if v}
    rows = ctx.find("nfipcom_billing", **match)
    return str(rows) if rows else f"No nfipcom_billing records for {match}."

@tool(owner="agent", rw="read")
def find_nfipcom_claims(ctx: ToolContext, nfipcom_claim_event_id: str = "", nfipcom_policy_id: str = "", customer_id: str = "") -> str:
    """Look up the claim files of General Property Form and RCBAP policies: first notices, adjuster
    reports, proofs of loss, payments, voids and written denials by claim number. Every reference
    number below is optional; supply whichever are known and all matching records are returned, or a
    message saying none were found.

    Args:
        nfipcom_claim_event_id: The reference number of this entry itself; leave "" if unknown.
        nfipcom_policy_id: The reference number of the General Property Form or RCBAP policy; leave "" if unknown.
        customer_id: The customer reference number of the policyholder, lender or account holder; leave "" if unknown.
    """
    match = {k: v for k, v in {"nfipcom_claim_event_id": nfipcom_claim_event_id, "nfipcom_policy_id": nfipcom_policy_id, "customer_id": customer_id}.items() if v}
    rows = ctx.find("nfipcom_claims", **match)
    return str(rows) if rows else f"No nfipcom_claims records for {match}."

@tool(owner="agent", rw="read")
def find_nfipcom_changes(ctx: ToolContext, nfipcom_change_id: str = "", nfipcom_policy_id: str = "", customer_id: str = "") -> str:
    """Look up servicing documents of General Property Form and RCBAP policies: endorsements, Elevation
    Certificates, renewal bills and mortgagee notices. Every reference number below is optional;
    supply whichever are known and all matching records are returned, or a message saying none were
    found.

    Args:
        nfipcom_change_id: The reference number of this entry itself; leave "" if unknown.
        nfipcom_policy_id: The reference number of the General Property Form or RCBAP policy; leave "" if unknown.
        customer_id: The customer reference number of the policyholder, lender or account holder; leave "" if unknown.
    """
    match = {k: v for k, v in {"nfipcom_change_id": nfipcom_change_id, "nfipcom_policy_id": nfipcom_policy_id, "customer_id": customer_id}.items() if v}
    rows = ctx.find("nfipcom_changes", **match)
    return str(rows) if rows else f"No nfipcom_changes records for {match}."

@tool(owner="agent", rw="read")
def find_nfipcom_requests(ctx: ToolContext, nfipcom_request_id: str = "", customer_id: str = "", nfipcom_policy_id: str = "") -> str:
    """Look up cancellation requests on General Property Form and RCBAP policies, with the reason,
    requested effective date, supporting document, lender release and signature status. Every
    reference number below is optional; supply whichever are known and all matching records are
    returned, or a message saying none were found.

    Args:
        nfipcom_request_id: The reference number of this entry itself; leave "" if unknown.
        customer_id: The customer reference number of the policyholder, lender or account holder; leave "" if unknown.
        nfipcom_policy_id: The reference number of the General Property Form or RCBAP policy; leave "" if unknown.
    """
    match = {k: v for k, v in {"nfipcom_request_id": nfipcom_request_id, "customer_id": customer_id, "nfipcom_policy_id": nfipcom_policy_id}.items() if v}
    rows = ctx.find("nfipcom_requests", **match)
    return str(rows) if rows else f"No nfipcom_requests records for {match}."

@tool(owner="agent", rw="read")
def find_homeflood_policies(ctx: ToolContext, homeflood_policy_id: str = "", customer_id: str = "") -> str:
    """Look up HomeFlood private residential flood policies. Each result shows the policy number, tier,
    status, insured address and flood zone, dwelling and personal property limits, deductible,
    replacement cost value, terms and effective dates, waiting-period basis, mortgagee details and
    compliance aid status, payment plan, Elevation Certificate facts, credits applied, the term
    premium, balance and any cancellation or notice details. Every reference number below is
    optional; supply whichever are known and all matching records are returned, or a message saying
    none were found.

    Args:
        homeflood_policy_id: The reference number of the HomeFlood policy; leave "" if unknown.
        customer_id: The customer reference number of the policyholder, lender or account holder; leave "" if unknown.
    """
    match = {k: v for k, v in {"homeflood_policy_id": homeflood_policy_id, "customer_id": customer_id}.items() if v}
    rows = ctx.find("homeflood_policies", **match)
    return str(rows) if rows else f"No homeflood_policies records for {match}."

@tool(owner="agent", rw="read")
def find_homeflood_billing(ctx: ToolContext, homeflood_billing_id: str = "", homeflood_policy_id: str = "", customer_id: str = "", reference_id: str = "") -> str:
    """Look up the premium account entries of HomeFlood policies: term premiums, policy fees, installment
    fees and endorsement premiums booked, payments and installments received, credits and refunds.
    Every reference number below is optional; supply whichever are known and all matching records
    are returned, or a message saying none were found.

    Args:
        homeflood_billing_id: The reference number of this entry itself; leave "" if unknown.
        homeflood_policy_id: The reference number of the HomeFlood policy; leave "" if unknown.
        customer_id: The customer reference number of the policyholder, lender or account holder; leave "" if unknown.
        reference_id: The reference number of the record that caused the entry (for example an endorsement, certificate review or cancellation request, or the policy itself); leave "" if unknown.
    """
    match = {k: v for k, v in {"homeflood_billing_id": homeflood_billing_id, "homeflood_policy_id": homeflood_policy_id, "customer_id": customer_id, "reference_id": reference_id}.items() if v}
    rows = ctx.find("homeflood_billing", **match)
    return str(rows) if rows else f"No homeflood_billing records for {match}."

@tool(owner="agent", rw="read")
def find_homeflood_claims(ctx: ToolContext, homeflood_claim_event_id: str = "", homeflood_policy_id: str = "", customer_id: str = "") -> str:
    """Look up the claim files of HomeFlood policies: first notices, adjuster reports with the measured
    dwelling, other structures, personal property, basement, pool and loss-of-use amounts, proofs of
    loss, payments, voids and denials by claim number. Every reference number below is optional;
    supply whichever are known and all matching records are returned, or a message saying none were
    found.

    Args:
        homeflood_claim_event_id: The reference number of this entry itself; leave "" if unknown.
        homeflood_policy_id: The reference number of the HomeFlood policy; leave "" if unknown.
        customer_id: The customer reference number of the policyholder, lender or account holder; leave "" if unknown.
    """
    match = {k: v for k, v in {"homeflood_claim_event_id": homeflood_claim_event_id, "homeflood_policy_id": homeflood_policy_id, "customer_id": customer_id}.items() if v}
    rows = ctx.find("homeflood_claims", **match)
    return str(rows) if rows else f"No homeflood_claims records for {match}."

@tool(owner="agent", rw="read")
def find_homeflood_changes(ctx: ToolContext, homeflood_change_id: str = "", homeflood_policy_id: str = "", customer_id: str = "") -> str:
    """Look up servicing documents of HomeFlood policies: endorsements, Elevation Certificates and their
    review, renewal offers, and notices of cancellation or non-renewal mailed. Every reference
    number below is optional; supply whichever are known and all matching records are returned, or a
    message saying none were found.

    Args:
        homeflood_change_id: The reference number of this entry itself; leave "" if unknown.
        homeflood_policy_id: The reference number of the HomeFlood policy; leave "" if unknown.
        customer_id: The customer reference number of the policyholder, lender or account holder; leave "" if unknown.
    """
    match = {k: v for k, v in {"homeflood_change_id": homeflood_change_id, "homeflood_policy_id": homeflood_policy_id, "customer_id": customer_id}.items() if v}
    rows = ctx.find("homeflood_changes", **match)
    return str(rows) if rows else f"No homeflood_changes records for {match}."

@tool(owner="agent", rw="read")
def find_homeflood_requests(ctx: ToolContext, homeflood_request_id: str = "", customer_id: str = "", homeflood_policy_id: str = "") -> str:
    """Look up cancellation requests and statements of no loss on HomeFlood policies, with reason,
    effective date, supporting document and signature status. Every reference number below is
    optional; supply whichever are known and all matching records are returned, or a message saying
    none were found.

    Args:
        homeflood_request_id: The reference number of this entry itself; leave "" if unknown.
        customer_id: The customer reference number of the policyholder, lender or account holder; leave "" if unknown.
        homeflood_policy_id: The reference number of the HomeFlood policy; leave "" if unknown.
    """
    match = {k: v for k, v in {"homeflood_request_id": homeflood_request_id, "customer_id": customer_id, "homeflood_policy_id": homeflood_policy_id}.items() if v}
    rows = ctx.find("homeflood_requests", **match)
    return str(rows) if rows else f"No homeflood_requests records for {match}."

@tool(owner="agent", rw="read")
def find_excess_policies(ctx: ToolContext, excess_policy_id: str = "", customer_id: str = "") -> str:
    """Look up Excess Flood policies. Each result shows the policy number, tier, status, insured address
    and flood zone, excess limits and attachment points, the underlying primary policy on file,
    terms and effective dates, Elevation Certificate facts, the state surplus lines tax and stamping
    fee rates, the term premium, balance and any cancellation details. Every reference number below
    is optional; supply whichever are known and all matching records are returned, or a message
    saying none were found.

    Args:
        excess_policy_id: The reference number of the Excess Flood policy; leave "" if unknown.
        customer_id: The customer reference number of the policyholder, lender or account holder; leave "" if unknown.
    """
    match = {k: v for k, v in {"excess_policy_id": excess_policy_id, "customer_id": customer_id}.items() if v}
    rows = ctx.find("excess_policies", **match)
    return str(rows) if rows else f"No excess_policies records for {match}."

@tool(owner="agent", rw="read")
def find_excess_billing(ctx: ToolContext, excess_billing_id: str = "", excess_policy_id: str = "", customer_id: str = "", reference_id: str = "") -> str:
    """Look up the premium account entries of Excess Flood policies: term premium, policy fee, surplus
    lines tax, stamping fee and endorsement premium booked, payments, credits and refunds. Every
    reference number below is optional; supply whichever are known and all matching records are
    returned, or a message saying none were found.

    Args:
        excess_billing_id: The reference number of this entry itself; leave "" if unknown.
        excess_policy_id: The reference number of the Excess Flood policy; leave "" if unknown.
        customer_id: The customer reference number of the policyholder, lender or account holder; leave "" if unknown.
        reference_id: The reference number of the record that caused the entry (for example an endorsement, certificate review or cancellation request, or the policy itself); leave "" if unknown.
    """
    match = {k: v for k, v in {"excess_billing_id": excess_billing_id, "excess_policy_id": excess_policy_id, "customer_id": customer_id, "reference_id": reference_id}.items() if v}
    rows = ctx.find("excess_billing", **match)
    return str(rows) if rows else f"No excess_billing records for {match}."

@tool(owner="agent", rw="read")
def find_excess_claims(ctx: ToolContext, excess_claim_event_id: str = "", excess_policy_id: str = "", customer_id: str = "") -> str:
    """Look up the claim files of Excess Flood policies: first notices with the underlying claim number,
    adjuster reports of the whole covered loss, underlying settlement statements, proofs of loss,
    payments, voids and denials. Every reference number below is optional; supply whichever are
    known and all matching records are returned, or a message saying none were found.

    Args:
        excess_claim_event_id: The reference number of this entry itself; leave "" if unknown.
        excess_policy_id: The reference number of the Excess Flood policy; leave "" if unknown.
        customer_id: The customer reference number of the policyholder, lender or account holder; leave "" if unknown.
    """
    match = {k: v for k, v in {"excess_claim_event_id": excess_claim_event_id, "excess_policy_id": excess_policy_id, "customer_id": customer_id}.items() if v}
    rows = ctx.find("excess_claims", **match)
    return str(rows) if rows else f"No excess_claims records for {match}."

@tool(owner="agent", rw="read")
def find_excess_changes(ctx: ToolContext, excess_change_id: str = "", excess_policy_id: str = "", customer_id: str = "") -> str:
    """Look up servicing documents of Excess Flood policies: endorsements, declarations of the underlying
    policy received, renewal offers and notices mailed. Every reference number below is optional;
    supply whichever are known and all matching records are returned, or a message saying none were
    found.

    Args:
        excess_change_id: The reference number of this entry itself; leave "" if unknown.
        excess_policy_id: The reference number of the Excess Flood policy; leave "" if unknown.
        customer_id: The customer reference number of the policyholder, lender or account holder; leave "" if unknown.
    """
    match = {k: v for k, v in {"excess_change_id": excess_change_id, "excess_policy_id": excess_policy_id, "customer_id": customer_id}.items() if v}
    rows = ctx.find("excess_changes", **match)
    return str(rows) if rows else f"No excess_changes records for {match}."

@tool(owner="agent", rw="read")
def find_excess_requests(ctx: ToolContext, excess_request_id: str = "", customer_id: str = "", excess_policy_id: str = "") -> str:
    """Look up cancellation requests on Excess Flood policies, with reason, effective date, supporting
    document and signature status. Every reference number below is optional; supply whichever are
    known and all matching records are returned, or a message saying none were found.

    Args:
        excess_request_id: The reference number of this entry itself; leave "" if unknown.
        customer_id: The customer reference number of the policyholder, lender or account holder; leave "" if unknown.
        excess_policy_id: The reference number of the Excess Flood policy; leave "" if unknown.
    """
    match = {k: v for k, v in {"excess_request_id": excess_request_id, "customer_id": customer_id, "excess_policy_id": excess_policy_id}.items() if v}
    rows = ctx.find("excess_requests", **match)
    return str(rows) if rows else f"No excess_requests records for {match}."

@tool(owner="agent", rw="read")
def find_forceplaced_programs(ctx: ToolContext, forceplaced_program_id: str = "", customer_id: str = "") -> str:
    """Look up lender-placed flood master programs held by lenders and servicers, showing the master policy
    number, program tier, status, effective and term dates, the oldest unpaid statement due date,
    the account balance and any termination date. Every reference number below is optional; supply
    whichever are known and all matching records are returned, or a message saying none were found.

    Args:
        forceplaced_program_id: The reference number of the lender's master program; leave "" if unknown.
        customer_id: The customer reference number of the policyholder, lender or account holder; leave "" if unknown.
    """
    match = {k: v for k, v in {"forceplaced_program_id": forceplaced_program_id, "customer_id": customer_id}.items() if v}
    rows = ctx.find("forceplaced_programs", **match)
    return str(rows) if rows else f"No forceplaced_programs records for {match}."

@tool(owner="agent", rw="read")
def find_forceplaced_certificates(ctx: ToolContext, forceplaced_certificate_event_id: str = "", forceplaced_program_id: str = "", customer_id: str = "") -> str:
    """Look up the certificates of lender-placed flood coverage issued under a master program: issue,
    renewal and cancellation entries per certificate, with the loan, borrower, property, balances
    reported, required amount, limits, coverage dates, premium and any cancellation reason. Every
    reference number below is optional; supply whichever are known and all matching records are
    returned, or a message saying none were found.

    Args:
        forceplaced_certificate_event_id: The reference number of this entry itself; leave "" if unknown.
        forceplaced_program_id: The reference number of the lender's master program; leave "" if unknown.
        customer_id: The customer reference number of the policyholder, lender or account holder; leave "" if unknown.
    """
    match = {k: v for k, v in {"forceplaced_certificate_event_id": forceplaced_certificate_event_id, "forceplaced_program_id": forceplaced_program_id, "customer_id": customer_id}.items() if v}
    rows = ctx.find("forceplaced_certificates", **match)
    return str(rows) if rows else f"No forceplaced_certificates records for {match}."

@tool(owner="agent", rw="read")
def find_forceplaced_tracking(ctx: ToolContext, forceplaced_tracking_id: str = "", forceplaced_program_id: str = "", customer_id: str = "") -> str:
    """Look up flood tracking activity on a lender's loans: borrower notices mailed (first notice,
    reminder, renewal notice) and borrower evidence of coverage received with its policy details and
    review outcome. Every reference number below is optional; supply whichever are known and all
    matching records are returned, or a message saying none were found.

    Args:
        forceplaced_tracking_id: The reference number of this entry itself; leave "" if unknown.
        forceplaced_program_id: The reference number of the lender's master program; leave "" if unknown.
        customer_id: The customer reference number of the policyholder, lender or account holder; leave "" if unknown.
    """
    match = {k: v for k, v in {"forceplaced_tracking_id": forceplaced_tracking_id, "forceplaced_program_id": forceplaced_program_id, "customer_id": customer_id}.items() if v}
    rows = ctx.find("forceplaced_tracking", **match)
    return str(rows) if rows else f"No forceplaced_tracking records for {match}."

@tool(owner="agent", rw="read")
def find_forceplaced_billing(ctx: ToolContext, forceplaced_billing_id: str = "", forceplaced_program_id: str = "", customer_id: str = "", reference_id: str = "") -> str:
    """Look up a lender-placed program's account entries: certificate premiums billed, lender remittances,
    cancellation credits and refunds, by statement month. Every reference number below is optional;
    supply whichever are known and all matching records are returned, or a message saying none were
    found.

    Args:
        forceplaced_billing_id: The reference number of this entry itself; leave "" if unknown.
        forceplaced_program_id: The reference number of the lender's master program; leave "" if unknown.
        customer_id: The customer reference number of the policyholder, lender or account holder; leave "" if unknown.
        reference_id: The reference number of the record that caused the entry (for example an endorsement, certificate review or cancellation request, or the policy itself); leave "" if unknown.
    """
    match = {k: v for k, v in {"forceplaced_billing_id": forceplaced_billing_id, "forceplaced_program_id": forceplaced_program_id, "customer_id": customer_id, "reference_id": reference_id}.items() if v}
    rows = ctx.find("forceplaced_billing", **match)
    return str(rows) if rows else f"No forceplaced_billing records for {match}."

@tool(owner="agent", rw="read")
def find_forceplaced_claims(ctx: ToolContext, forceplaced_claim_event_id: str = "", forceplaced_program_id: str = "", customer_id: str = "") -> str:
    """Look up claim files under lender-placed flood certificates: first notices, adjuster reports,
    payments, voids and denials. Every reference number below is optional; supply whichever are
    known and all matching records are returned, or a message saying none were found.

    Args:
        forceplaced_claim_event_id: The reference number of this entry itself; leave "" if unknown.
        forceplaced_program_id: The reference number of the lender's master program; leave "" if unknown.
        customer_id: The customer reference number of the policyholder, lender or account holder; leave "" if unknown.
    """
    match = {k: v for k, v in {"forceplaced_claim_event_id": forceplaced_claim_event_id, "forceplaced_program_id": forceplaced_program_id, "customer_id": customer_id}.items() if v}
    rows = ctx.find("forceplaced_claims", **match)
    return str(rows) if rows else f"No forceplaced_claims records for {match}."

@tool(owner="agent", rw="read")
def find_forceplaced_requests(ctx: ToolContext, forceplaced_request_id: str = "", customer_id: str = "", forceplaced_program_id: str = "") -> str:
    """Look up a lender's requests on its master programs, such as termination notices, with the requested
    effective date and signature status. Every reference number below is optional; supply whichever
    are known and all matching records are returned, or a message saying none were found.

    Args:
        forceplaced_request_id: The reference number of this entry itself; leave "" if unknown.
        customer_id: The customer reference number of the policyholder, lender or account holder; leave "" if unknown.
        forceplaced_program_id: The reference number of the lender's master program; leave "" if unknown.
    """
    match = {k: v for k, v in {"forceplaced_request_id": forceplaced_request_id, "customer_id": customer_id, "forceplaced_program_id": forceplaced_program_id}.items() if v}
    rows = ctx.find("forceplaced_requests", **match)
    return str(rows) if rows else f"No forceplaced_requests records for {match}."

@tool(owner="agent", rw="read")
def find_bizflood_policies(ctx: ToolContext, bizflood_policy_id: str = "", customer_id: str = "") -> str:
    """Look up BizFlood commercial flood policies, showing the policy number, tier, status, number of
    scheduled locations and total insured value, deductible, payment plan, terms, surplus lines
    rates, the term premium, balance and any cancellation details. Every reference number below is
    optional; supply whichever are known and all matching records are returned, or a message saying
    none were found.

    Args:
        bizflood_policy_id: The reference number of the BizFlood policy; leave "" if unknown.
        customer_id: The customer reference number of the policyholder, lender or account holder; leave "" if unknown.
    """
    match = {k: v for k, v in {"bizflood_policy_id": bizflood_policy_id, "customer_id": customer_id}.items() if v}
    rows = ctx.find("bizflood_policies", **match)
    return str(rows) if rows else f"No bizflood_policies records for {match}."

@tool(owner="agent", rw="read")
def find_bizflood_billing(ctx: ToolContext, bizflood_billing_id: str = "", bizflood_policy_id: str = "", customer_id: str = "", reference_id: str = "") -> str:
    """Look up the premium account entries of BizFlood policies: premium, fees, installment fees, taxes and
    endorsement premiums booked, payments, credits and refunds. Every reference number below is
    optional; supply whichever are known and all matching records are returned, or a message saying
    none were found.

    Args:
        bizflood_billing_id: The reference number of this entry itself; leave "" if unknown.
        bizflood_policy_id: The reference number of the BizFlood policy; leave "" if unknown.
        customer_id: The customer reference number of the policyholder, lender or account holder; leave "" if unknown.
        reference_id: The reference number of the record that caused the entry (for example an endorsement, certificate review or cancellation request, or the policy itself); leave "" if unknown.
    """
    match = {k: v for k, v in {"bizflood_billing_id": bizflood_billing_id, "bizflood_policy_id": bizflood_policy_id, "customer_id": customer_id, "reference_id": reference_id}.items() if v}
    rows = ctx.find("bizflood_billing", **match)
    return str(rows) if rows else f"No bizflood_billing records for {match}."

@tool(owner="agent", rw="read")
def find_bizflood_claims(ctx: ToolContext, bizflood_claim_event_id: str = "", bizflood_policy_id: str = "", customer_id: str = "") -> str:
    """Look up the claim files of BizFlood policies by claim number and location: first notices, adjuster
    reports, payments, voids and denials. Every reference number below is optional; supply whichever
    are known and all matching records are returned, or a message saying none were found.

    Args:
        bizflood_claim_event_id: The reference number of this entry itself; leave "" if unknown.
        bizflood_policy_id: The reference number of the BizFlood policy; leave "" if unknown.
        customer_id: The customer reference number of the policyholder, lender or account holder; leave "" if unknown.
    """
    match = {k: v for k, v in {"bizflood_claim_event_id": bizflood_claim_event_id, "bizflood_policy_id": bizflood_policy_id, "customer_id": customer_id}.items() if v}
    rows = ctx.find("bizflood_claims", **match)
    return str(rows) if rows else f"No bizflood_claims records for {match}."

@tool(owner="agent", rw="read")
def find_bizflood_changes(ctx: ToolContext, bizflood_change_id: str = "", bizflood_policy_id: str = "", customer_id: str = "") -> str:
    """Look up BizFlood schedule documents: statements of values per location, location additions,
    deletions and revaluations, and renewal offers. Every reference number below is optional; supply
    whichever are known and all matching records are returned, or a message saying none were found.

    Args:
        bizflood_change_id: The reference number of this entry itself; leave "" if unknown.
        bizflood_policy_id: The reference number of the BizFlood policy; leave "" if unknown.
        customer_id: The customer reference number of the policyholder, lender or account holder; leave "" if unknown.
    """
    match = {k: v for k, v in {"bizflood_change_id": bizflood_change_id, "bizflood_policy_id": bizflood_policy_id, "customer_id": customer_id}.items() if v}
    rows = ctx.find("bizflood_changes", **match)
    return str(rows) if rows else f"No bizflood_changes records for {match}."

@tool(owner="agent", rw="read")
def find_bizflood_requests(ctx: ToolContext, bizflood_request_id: str = "", customer_id: str = "", bizflood_policy_id: str = "") -> str:
    """Look up cancellation requests on BizFlood policies, with reason, effective date and signature
    status. Every reference number below is optional; supply whichever are known and all matching
    records are returned, or a message saying none were found.

    Args:
        bizflood_request_id: The reference number of this entry itself; leave "" if unknown.
        customer_id: The customer reference number of the policyholder, lender or account holder; leave "" if unknown.
        bizflood_policy_id: The reference number of the BizFlood policy; leave "" if unknown.
    """
    match = {k: v for k, v in {"bizflood_request_id": bizflood_request_id, "customer_id": customer_id, "bizflood_policy_id": bizflood_policy_id}.items() if v}
    rows = ctx.find("bizflood_requests", **match)
    return str(rows) if rows else f"No bizflood_requests records for {match}."

@tool(owner="agent", rw="read")
def find_parametric_policies(ctx: ToolContext, parametric_policy_id: str = "", customer_id: str = "") -> str:
    """Look up FloodPay parametric flood policies, showing the policy number, tier, status, insured
    location and flood zone, the installed sensor and its activation date, any current sensor fault,
    terms, tax rate, premium, balance, remaining payout capacity and any cancellation details. Every
    reference number below is optional; supply whichever are known and all matching records are
    returned, or a message saying none were found.

    Args:
        parametric_policy_id: The reference number of the FloodPay policy; leave "" if unknown.
        customer_id: The customer reference number of the policyholder, lender or account holder; leave "" if unknown.
    """
    match = {k: v for k, v in {"parametric_policy_id": parametric_policy_id, "customer_id": customer_id}.items() if v}
    rows = ctx.find("parametric_policies", **match)
    return str(rows) if rows else f"No parametric_policies records for {match}."

@tool(owner="agent", rw="read")
def find_parametric_billing(ctx: ToolContext, parametric_billing_id: str = "", parametric_policy_id: str = "", customer_id: str = "", reference_id: str = "") -> str:
    """Look up the premium account entries of FloodPay policies: premium, installation and monitoring fees,
    taxes, payments, credits and refunds. Every reference number below is optional; supply whichever
    are known and all matching records are returned, or a message saying none were found.

    Args:
        parametric_billing_id: The reference number of this entry itself; leave "" if unknown.
        parametric_policy_id: The reference number of the FloodPay policy; leave "" if unknown.
        customer_id: The customer reference number of the policyholder, lender or account holder; leave "" if unknown.
        reference_id: The reference number of the record that caused the entry (for example an endorsement, certificate review or cancellation request, or the policy itself); leave "" if unknown.
    """
    match = {k: v for k, v in {"parametric_billing_id": parametric_billing_id, "parametric_policy_id": parametric_policy_id, "customer_id": customer_id, "reference_id": reference_id}.items() if v}
    rows = ctx.find("parametric_billing", **match)
    return str(rows) if rows else f"No parametric_billing records for {match}."

@tool(owner="agent", rw="read")
def find_parametric_events(ctx: ToolContext, parametric_event_row_id: str = "", parametric_policy_id: str = "", customer_id: str = "") -> str:
    """Look up FloodPay flood events and payout capacity: capacity booked for each term, recorded sensor
    triggers with peak depth and band reached, payouts issued and payouts declined. Every reference
    number below is optional; supply whichever are known and all matching records are returned, or a
    message saying none were found.

    Args:
        parametric_event_row_id: The reference number of this entry itself; leave "" if unknown.
        parametric_policy_id: The reference number of the FloodPay policy; leave "" if unknown.
        customer_id: The customer reference number of the policyholder, lender or account holder; leave "" if unknown.
    """
    match = {k: v for k, v in {"parametric_event_row_id": parametric_event_row_id, "parametric_policy_id": parametric_policy_id, "customer_id": customer_id}.items() if v}
    rows = ctx.find("parametric_events", **match)
    return str(rows) if rows else f"No parametric_events records for {match}."

@tool(owner="agent", rw="read")
def find_parametric_requests(ctx: ToolContext, parametric_request_id: str = "", customer_id: str = "", parametric_policy_id: str = "") -> str:
    """Look up cancellation requests on FloodPay policies, with reason, effective date and signature
    status. Every reference number below is optional; supply whichever are known and all matching
    records are returned, or a message saying none were found.

    Args:
        parametric_request_id: The reference number of this entry itself; leave "" if unknown.
        customer_id: The customer reference number of the policyholder, lender or account holder; leave "" if unknown.
        parametric_policy_id: The reference number of the FloodPay policy; leave "" if unknown.
    """
    match = {k: v for k, v in {"parametric_request_id": parametric_request_id, "customer_id": customer_id, "parametric_policy_id": parametric_policy_id}.items() if v}
    rows = ctx.find("parametric_requests", **match)
    return str(rows) if rows else f"No parametric_requests records for {match}."

@tool(owner="agent", rw="read")
def find_customers(ctx: ToolContext, customer_id: str = "", name: str = "", phone_number: str = "",
                   email: str = "") -> str:
    """Find the customer profile a call is about — a homeowner or renter, a business or landlord, a
    condominium association, or a mortgage lender or servicer. Search by the customer reference
    number, or by what the caller can tell you: the name on the profile, the registered phone number
    or the registered email address. Every criterion is optional; give whichever you have. The profile
    returned shows the kind of customer, name, contact details, mailing address and ZIP code, the
    last four digits of the tax identification number on file and the date the profile was opened.
    Finding a profile does not confirm that the caller is that customer; identity is confirmed
    separately.

    Args:
        customer_id: The customer reference number, when already known; leave "" if unknown.
        name: The full name of the person or entity as the caller states it; leave "" if not given.
        phone_number: The registered phone number as the caller states it (10 digits); leave "" if not given.
        email: The registered email address as the caller states it; leave "" if not given.
    """
    match = {k: v for k, v in {"customer_id": customer_id, "name": name,
                               "phone_number": phone_number, "email": email}.items() if v}
    if not match:
        return "Error: provide at least one reference number or detail to find the customer."
    rows = ctx.fuzzy_find("customers", **match)
    if not rows:
        return f"No customer matches {match}."
    if len(rows) > 1:
        return f"Error: {len(rows)} customers match {match}; ask the caller for one more detail."
    return str(rows[0])


@tool(owner="agent", rw="write")
def verify_customer_identity(ctx: ToolContext, customer_id: str, phone_number: str = "", email: str = "",
                             tax_id_last4: str = "", mailing_zip: str = "",
                             profile_opened_date: str = "") -> str:
    """Confirm that the caller is the customer on the profile and record the result. The caller must be
    confirmed before any policy, claim, billing or program account information is discussed or any
    change, payment or refund is handled. This tool makes the comparison itself: it checks each
    detail the caller gives against the profile on file, counts how many agree, and confirms the
    caller when at least 2 details agree. The customer reference number only identifies which profile
    to check and never counts as a matching detail. Pass exactly what the caller said for each detail
    they gave and leave the rest blank. The result is recorded; if a first attempt falls short and a
    later attempt with more details succeeds, the caller stays confirmed.

    Args:
        customer_id: The customer reference number of the profile being checked, taken from the customer profile lookup. Required.
        phone_number: The registered phone number the caller states, 10 digits with no punctuation; leave "" if not stated.
        email: The registered email address the caller states; leave "" if not stated.
        tax_id_last4: The last four digits of the Social Security number or Employer Identification Number on the profile, as the caller states them; leave "" if not stated.
        mailing_zip: The 5-digit ZIP code of the mailing address on the profile, as the caller states it; leave "" if not stated.
        profile_opened_date: The date the customer profile was opened with Tidemark, as YYYY-MM-DD; leave "" if not stated.
    """
    if not customer_id:
        return "Error: customer_id is required; find the customer profile first and pass its reference number."
    rows = ctx.find("customers", customer_id=customer_id)
    if not rows:
        return f"Error: no customer {customer_id}; cannot verify."
    rec = rows[0]
    # The locator customer_id is deliberately not a credential.
    supplied = {"phone_number": phone_number, "email": email, "tax_id_last4": tax_id_last4,
                "mailing_zip": mailing_zip, "profile_opened_date": profile_opened_date}
    matched = sum(1 for field, value in supplied.items()
                  if value and str(rec.get(field) or "").strip().lower() == str(value).strip().lower())
    verified = matched >= 2
    rid = ctx.make_id("ver_", customer_id)
    # Upsert, monotonic: a later pass is never overwritten by an earlier failure.
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
    """Transfer the customer to a human Tidemark representative and record why. Use it when no
    Tidemark rule or procedure available to you can resolve what the customer needs, or when the
    customer has explicitly asked for a human representative at least 2 times during the call.

    Args:
        customer_id: The customer reference number from the customer profile lookup; the profile must exist.
        reason: Why the customer is being transferred — exactly one of POLICY_NOT_COVERED (no available rule or procedure resolves the request) or CUSTOMER_REQUESTED (the customer has explicitly asked for a human representative at least 2 times).
    """
    allowed = {"POLICY_NOT_COVERED", "CUSTOMER_REQUESTED"}
    if reason not in allowed:
        return f"Error: unknown transfer reason '{reason}'. Valid: {', '.join(sorted(allowed))}."
    if not ctx.find("customers", customer_id=customer_id):
        return f"Error: no customer {customer_id}; cannot record the transfer."
    rid = ctx.make_id("hof_", customer_id, reason)
    ctx.create("handoffs", rid, handoff_id=rid, customer_id=customer_id, reason=reason, created_at=ctx.now())
    return f"Transfer to a human representative recorded for {customer_id} ({reason})."

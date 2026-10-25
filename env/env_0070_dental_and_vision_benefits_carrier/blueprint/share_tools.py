"""Shared tools for env_0070_dental_and_vision_benefits_carrier (Cascade Mutual Dental & Vision).

Share tools are always available. This file holds the record-lookup layer (one finder per
record type; the customer finder doubles as the identity entry), the identity-verification
write and the transfer-to-human write. Customer-originated actions live as hidden task tools
in each difficulty's task_tools.py.
"""

from erlbench import ToolContext, tool


@tool(owner="agent", rw="read")
def find_identity_verifications(ctx: ToolContext, verification_id: str = "", customer_id: str = "") -> str:
    """Look up the identity-verification outcome recorded for a customer on this contact: whether verification has passed and when it was last attempted.

    Every reference number below is optional; supply whichever you already hold, and every
    record matching all of them is returned. With none supplied, all such records are listed.

    Args:
        verification_id: The reference number of the identity-verification record itself; leave "" if unknown.
        customer_id: The customer reference number (member subscriber, employer or practice); leave "" if unknown.
    """
    match = {k: v for k, v in {"verification_id": verification_id, "customer_id": customer_id}.items() if v}
    rows = ctx.find("identity_verifications", **match)
    return str(rows) if rows else f"No identity_verifications records for {match}."

@tool(owner="agent", rw="read")
def find_human_handoffs(ctx: ToolContext, handoff_id: str = "", customer_id: str = "") -> str:
    """Look up transfers of a customer to a human representative, with the reason recorded and the time of the transfer.

    Every reference number below is optional; supply whichever you already hold, and every
    record matching all of them is returned. With none supplied, all such records are listed.

    Args:
        handoff_id: The reference number of the transfer record itself; leave "" if unknown.
        customer_id: The customer reference number (member subscriber, employer or practice); leave "" if unknown.
    """
    match = {k: v for k, v in {"handoff_id": handoff_id, "customer_id": customer_id}.items() if v}
    rows = ctx.find("human_handoffs", **match)
    return str(rows) if rows else f"No human_handoffs records for {match}."

@tool(owner="agent", rw="read")
def find_dental_plans(ctx: ToolContext, dental_plan_id: str = "", customer_id: str = "", billing_account_id: str = "", group_contract_id: str = "") -> str:
    """Look up dental PPO enrollments: one record per covered person, showing the plan held, enrollment status, market, coverage tier, the covered person's name, birth date and relationship, how and when coverage started, any plan change, documented prior coverage, the benefit-period reset day, termination details and other dental coverage on file for coordination of benefits.

    Every reference number below is optional; supply whichever you already hold, and every
    record matching all of them is returned. With none supplied, all such records are listed.

    Args:
        dental_plan_id: The reference number of a dental PPO enrollment (the record itself); leave "" if unknown.
        customer_id: The customer reference number (member subscriber, employer or practice); leave "" if unknown.
        billing_account_id: The reference number of a premium billing account; leave "" if unknown.
        group_contract_id: The reference number of an employer group contract; leave "" if unknown.
    """
    match = {k: v for k, v in {"dental_plan_id": dental_plan_id, "customer_id": customer_id, "billing_account_id": billing_account_id, "group_contract_id": group_contract_id}.items() if v}
    rows = ctx.find("dental_plans", **match)
    return str(rows) if rows else f"No dental_plans records for {match}."

@tool(owner="agent", rw="read")
def find_dental_claim_lines(ctx: ToolContext, dental_claim_line_id: str = "", dental_plan_id: str = "", customer_id: str = "", provider_agreement_id: str = "", original_claim_line_id: str = "", dental_appeal_id: str = "", dental_estimate_id: str = "") -> str:
    """Look up dental claim lines as shown on the Explanation of Benefits: claim number and line, treating practice and network, procedure code and benefit category, tooth, dates of service, receipt and decision, billed and allowed amounts, deductible, coinsurance, other-carrier payment, plan payment, patient share, remark code, and links to a replaced line, an appeal or an estimate.

    Every reference number below is optional; supply whichever you already hold, and every
    record matching all of them is returned. With none supplied, all such records are listed.

    Args:
        dental_claim_line_id: The reference number of a dental claim line (the record itself); leave "" if unknown.
        dental_plan_id: The reference number of a dental PPO enrollment; leave "" if unknown.
        customer_id: The customer reference number (member subscriber, employer or practice); leave "" if unknown.
        provider_agreement_id: The reference number of a network participation agreement; leave "" if unknown.
        original_claim_line_id: The reference number of an earlier dental claim line this line replaces or releases; leave "" if unknown.
        dental_appeal_id: The reference number of a dental appeal; leave "" if unknown.
        dental_estimate_id: The reference number of a pre-treatment estimate line; leave "" if unknown.
    """
    match = {k: v for k, v in {"dental_claim_line_id": dental_claim_line_id, "dental_plan_id": dental_plan_id, "customer_id": customer_id, "provider_agreement_id": provider_agreement_id, "original_claim_line_id": original_claim_line_id, "dental_appeal_id": dental_appeal_id, "dental_estimate_id": dental_estimate_id}.items() if v}
    rows = ctx.find("dental_claim_lines", **match)
    return str(rows) if rows else f"No dental_claim_lines records for {match}."

@tool(owner="agent", rw="read")
def find_dental_accumulator_postings(ctx: ToolContext, dental_accum_posting_id: str = "", dental_plan_id: str = "", customer_id: str = "", dental_claim_line_id: str = "") -> str:
    """Look up dental benefit accumulator postings: amounts counted toward or taken back from a person's annual maximum, deductible, rollover balance or pediatric out-of-pocket maximum, with the benefit year, the claim line that caused each posting and the posting date.

    Every reference number below is optional; supply whichever you already hold, and every
    record matching all of them is returned. With none supplied, all such records are listed.

    Args:
        dental_accum_posting_id: The reference number of the accumulator posting itself; leave "" if unknown.
        dental_plan_id: The reference number of a dental PPO enrollment; leave "" if unknown.
        customer_id: The customer reference number (member subscriber, employer or practice); leave "" if unknown.
        dental_claim_line_id: The reference number of a dental claim line; leave "" if unknown.
    """
    match = {k: v for k, v in {"dental_accum_posting_id": dental_accum_posting_id, "dental_plan_id": dental_plan_id, "customer_id": customer_id, "dental_claim_line_id": dental_claim_line_id}.items() if v}
    rows = ctx.find("dental_accumulator_postings", **match)
    return str(rows) if rows else f"No dental_accumulator_postings records for {match}."

@tool(owner="agent", rw="read")
def find_dental_pretreatment_estimates(ctx: ToolContext, dental_estimate_id: str = "", dental_plan_id: str = "", customer_id: str = "", provider_agreement_id: str = "", original_estimate_id: str = "") -> str:
    """Look up pre-treatment estimates and their voids: estimate number, practice and network, proposed procedure and tooth, request and issue dates, valid-through date, proposed fee, allowance used, estimated plan payment and patient cost, and the estimate remark.

    Every reference number below is optional; supply whichever you already hold, and every
    record matching all of them is returned. With none supplied, all such records are listed.

    Args:
        dental_estimate_id: The reference number of a pre-treatment estimate line (the record itself); leave "" if unknown.
        dental_plan_id: The reference number of a dental PPO enrollment; leave "" if unknown.
        customer_id: The customer reference number (member subscriber, employer or practice); leave "" if unknown.
        provider_agreement_id: The reference number of a network participation agreement; leave "" if unknown.
        original_estimate_id: The reference number of the estimate line a void cancels; leave "" if unknown.
    """
    match = {k: v for k, v in {"dental_estimate_id": dental_estimate_id, "dental_plan_id": dental_plan_id, "customer_id": customer_id, "provider_agreement_id": provider_agreement_id, "original_estimate_id": original_estimate_id}.items() if v}
    rows = ctx.find("dental_pretreatment_estimates", **match)
    return str(rows) if rows else f"No dental_pretreatment_estimates records for {match}."

@tool(owner="agent", rw="read")
def find_dental_appeals(ctx: ToolContext, dental_appeal_id: str = "", dental_plan_id: str = "", customer_id: str = "", dental_claim_line_id: str = "", dental_estimate_id: str = "", original_appeal_id: str = "") -> str:
    """Look up dental appeal filings and decisions: the claim line or estimate appealed, appeal type and level, who filed, filing date, decision due date, decision date and outcome.

    Every reference number below is optional; supply whichever you already hold, and every
    record matching all of them is returned. With none supplied, all such records are listed.

    Args:
        dental_appeal_id: The reference number of a dental appeal (the record itself); leave "" if unknown.
        dental_plan_id: The reference number of a dental PPO enrollment; leave "" if unknown.
        customer_id: The customer reference number (member subscriber, employer or practice); leave "" if unknown.
        dental_claim_line_id: The reference number of a dental claim line; leave "" if unknown.
        dental_estimate_id: The reference number of a pre-treatment estimate line; leave "" if unknown.
        original_appeal_id: The reference number of the appeal filing or decision this record follows; leave "" if unknown.
    """
    match = {k: v for k, v in {"dental_appeal_id": dental_appeal_id, "dental_plan_id": dental_plan_id, "customer_id": customer_id, "dental_claim_line_id": dental_claim_line_id, "dental_estimate_id": dental_estimate_id, "original_appeal_id": original_appeal_id}.items() if v}
    rows = ctx.find("dental_appeals", **match)
    return str(rows) if rows else f"No dental_appeals records for {match}."

@tool(owner="agent", rw="read")
def find_dental_coverage_requests(ctx: ToolContext, dental_request_id: str = "", customer_id: str = "", dental_plan_id: str = "") -> str:
    """Look up dental coverage-change requests made by subscribers (withdrawal, free-look cancellation, voluntary termination or plan change), with the requested plan, the effective date and the processing status.

    Every reference number below is optional; supply whichever you already hold, and every
    record matching all of them is returned. With none supplied, all such records are listed.

    Args:
        dental_request_id: The reference number of the dental coverage-change request itself; leave "" if unknown.
        customer_id: The customer reference number (member subscriber, employer or practice); leave "" if unknown.
        dental_plan_id: The reference number of a dental PPO enrollment; leave "" if unknown.
    """
    match = {k: v for k, v in {"dental_request_id": dental_request_id, "customer_id": customer_id, "dental_plan_id": dental_plan_id}.items() if v}
    rows = ctx.find("dental_coverage_requests", **match)
    return str(rows) if rows else f"No dental_coverage_requests records for {match}."

@tool(owner="agent", rw="read")
def find_ortho_riders(ctx: ToolContext, ortho_rider_id: str = "", customer_id: str = "", dental_plan_id: str = "", billing_account_id: str = "") -> str:
    """Look up orthodontic benefit riders: the rider plan, status, the covered person and the dental enrollment the rider is attached to, application and effective dates, documented prior orthodontic coverage, termination details and the orthodontic benefit paid to date.

    Every reference number below is optional; supply whichever you already hold, and every
    record matching all of them is returned. With none supplied, all such records are listed.

    Args:
        ortho_rider_id: The reference number of an orthodontic rider (the record itself); leave "" if unknown.
        customer_id: The customer reference number (member subscriber, employer or practice); leave "" if unknown.
        dental_plan_id: The reference number of a dental PPO enrollment; leave "" if unknown.
        billing_account_id: The reference number of a premium billing account; leave "" if unknown.
    """
    match = {k: v for k, v in {"ortho_rider_id": ortho_rider_id, "customer_id": customer_id, "dental_plan_id": dental_plan_id, "billing_account_id": billing_account_id}.items() if v}
    rows = ctx.find("ortho_riders", **match)
    return str(rows) if rows else f"No ortho_riders records for {match}."

@tool(owner="agent", rw="read")
def find_ortho_cases(ctx: ToolContext, ortho_case_event_id: str = "", ortho_rider_id: str = "", customer_id: str = "", provider_agreement_id: str = "", original_case_event_id: str = "") -> str:
    """Look up orthodontic case records (establishment, transfer to a new orthodontist, closure): case number, treating practice and network, new start or takeover, appliance type, banding date, planned and remaining treatment months, case fees, event date and closure reason.

    Every reference number below is optional; supply whichever you already hold, and every
    record matching all of them is returned. With none supplied, all such records are listed.

    Args:
        ortho_case_event_id: The reference number of an orthodontic case record (the record itself); leave "" if unknown.
        ortho_rider_id: The reference number of an orthodontic rider; leave "" if unknown.
        customer_id: The customer reference number (member subscriber, employer or practice); leave "" if unknown.
        provider_agreement_id: The reference number of a network participation agreement; leave "" if unknown.
        original_case_event_id: The reference number of the case establishment record a transfer or closure belongs to; leave "" if unknown.
    """
    match = {k: v for k, v in {"ortho_case_event_id": ortho_case_event_id, "ortho_rider_id": ortho_rider_id, "customer_id": customer_id, "provider_agreement_id": provider_agreement_id, "original_case_event_id": original_case_event_id}.items() if v}
    rows = ctx.find("ortho_cases", **match)
    return str(rows) if rows else f"No ortho_cases records for {match}."

@tool(owner="agent", rw="read")
def find_ortho_payments(ctx: ToolContext, ortho_payment_id: str = "", ortho_rider_id: str = "", customer_id: str = "", ortho_case_event_id: str = "", provider_agreement_id: str = "", original_ortho_payment_id: str = "") -> str:
    """Look up orthodontic benefit payments and reversals: case, schedule position, service period, payee, practice paid, amount and payment date.

    Every reference number below is optional; supply whichever you already hold, and every
    record matching all of them is returned. With none supplied, all such records are listed.

    Args:
        ortho_payment_id: The reference number of an orthodontic payment (the record itself); leave "" if unknown.
        ortho_rider_id: The reference number of an orthodontic rider; leave "" if unknown.
        customer_id: The customer reference number (member subscriber, employer or practice); leave "" if unknown.
        ortho_case_event_id: The reference number of an orthodontic case record; leave "" if unknown.
        provider_agreement_id: The reference number of a network participation agreement; leave "" if unknown.
        original_ortho_payment_id: The reference number of the orthodontic payment a reversal cancels; leave "" if unknown.
    """
    match = {k: v for k, v in {"ortho_payment_id": ortho_payment_id, "ortho_rider_id": ortho_rider_id, "customer_id": customer_id, "ortho_case_event_id": ortho_case_event_id, "provider_agreement_id": provider_agreement_id, "original_ortho_payment_id": original_ortho_payment_id}.items() if v}
    rows = ctx.find("ortho_payments", **match)
    return str(rows) if rows else f"No ortho_payments records for {match}."

@tool(owner="agent", rw="read")
def find_ortho_rider_requests(ctx: ToolContext, ortho_request_id: str = "", customer_id: str = "", ortho_rider_id: str = "") -> str:
    """Look up orthodontic rider change requests (application withdrawal or voluntary termination) with their effective date and processing status.

    Every reference number below is optional; supply whichever you already hold, and every
    record matching all of them is returned. With none supplied, all such records are listed.

    Args:
        ortho_request_id: The reference number of the rider change request itself; leave "" if unknown.
        customer_id: The customer reference number (member subscriber, employer or practice); leave "" if unknown.
        ortho_rider_id: The reference number of an orthodontic rider; leave "" if unknown.
    """
    match = {k: v for k, v in {"ortho_request_id": ortho_request_id, "customer_id": customer_id, "ortho_rider_id": ortho_rider_id}.items() if v}
    rows = ctx.find("ortho_rider_requests", **match)
    return str(rows) if rows else f"No ortho_rider_requests records for {match}."

@tool(owner="agent", rw="read")
def find_vision_plans(ctx: ToolContext, vision_plan_id: str = "", customer_id: str = "", billing_account_id: str = "", group_contract_id: str = "") -> str:
    """Look up vision enrollments: one record per covered person, showing the plan held, status, market, coverage tier, covered person, coverage and benefit-period dates, plan change and termination details.

    Every reference number below is optional; supply whichever you already hold, and every
    record matching all of them is returned. With none supplied, all such records are listed.

    Args:
        vision_plan_id: The reference number of a vision enrollment (the record itself); leave "" if unknown.
        customer_id: The customer reference number (member subscriber, employer or practice); leave "" if unknown.
        billing_account_id: The reference number of a premium billing account; leave "" if unknown.
        group_contract_id: The reference number of an employer group contract; leave "" if unknown.
    """
    match = {k: v for k, v in {"vision_plan_id": vision_plan_id, "customer_id": customer_id, "billing_account_id": billing_account_id, "group_contract_id": group_contract_id}.items() if v}
    rows = ctx.find("vision_plans", **match)
    return str(rows) if rows else f"No vision_plans records for {match}."

@tool(owner="agent", rw="read")
def find_vision_claims(ctx: ToolContext, vision_claim_id: str = "", vision_plan_id: str = "", customer_id: str = "", provider_agreement_id: str = "", original_vision_claim_id: str = "") -> str:
    """Look up vision claim services and reversals: claim number, provider and network channel, service dates, exam, lens and contact-lens details, lens options, retail charge, allowance, copays, overage discount, plan payment, member payment and remark.

    Every reference number below is optional; supply whichever you already hold, and every
    record matching all of them is returned. With none supplied, all such records are listed.

    Args:
        vision_claim_id: The reference number of a vision claim service (the record itself); leave "" if unknown.
        vision_plan_id: The reference number of a vision enrollment; leave "" if unknown.
        customer_id: The customer reference number (member subscriber, employer or practice); leave "" if unknown.
        provider_agreement_id: The reference number of a network participation agreement; leave "" if unknown.
        original_vision_claim_id: The reference number of the vision service a reversal cancels; leave "" if unknown.
    """
    match = {k: v for k, v in {"vision_claim_id": vision_claim_id, "vision_plan_id": vision_plan_id, "customer_id": customer_id, "provider_agreement_id": provider_agreement_id, "original_vision_claim_id": original_vision_claim_id}.items() if v}
    rows = ctx.find("vision_claims", **match)
    return str(rows) if rows else f"No vision_claims records for {match}."

@tool(owner="agent", rw="read")
def find_vision_coverage_requests(ctx: ToolContext, vision_request_id: str = "", customer_id: str = "", vision_plan_id: str = "") -> str:
    """Look up vision coverage-change requests (withdrawal, free-look cancellation, voluntary termination or plan change) with the requested plan, effective date and processing status.

    Every reference number below is optional; supply whichever you already hold, and every
    record matching all of them is returned. With none supplied, all such records are listed.

    Args:
        vision_request_id: The reference number of the vision coverage-change request itself; leave "" if unknown.
        customer_id: The customer reference number (member subscriber, employer or practice); leave "" if unknown.
        vision_plan_id: The reference number of a vision enrollment; leave "" if unknown.
    """
    match = {k: v for k, v in {"vision_request_id": vision_request_id, "customer_id": customer_id, "vision_plan_id": vision_plan_id}.items() if v}
    rows = ctx.find("vision_coverage_requests", **match)
    return str(rows) if rows else f"No vision_coverage_requests records for {match}."

@tool(owner="agent", rw="read")
def find_billing_accounts(ctx: ToolContext, billing_account_id: str = "", customer_id: str = "", group_contract_id: str = "") -> str:
    """Look up premium billing accounts: billing arrangement, status, opening and closing dates, payment method, advance premium tax credit, paid-through date, grace-period start and current balance.

    Every reference number below is optional; supply whichever you already hold, and every
    record matching all of them is returned. With none supplied, all such records are listed.

    Args:
        billing_account_id: The reference number of a premium billing account (the record itself); leave "" if unknown.
        customer_id: The customer reference number (member subscriber, employer or practice); leave "" if unknown.
        group_contract_id: The reference number of an employer group contract; leave "" if unknown.
    """
    match = {k: v for k, v in {"billing_account_id": billing_account_id, "customer_id": customer_id, "group_contract_id": group_contract_id}.items() if v}
    rows = ctx.find("billing_accounts", **match)
    return str(rows) if rows else f"No billing_accounts records for {match}."

@tool(owner="agent", rw="read")
def find_billing_transactions(ctx: ToolContext, billing_txn_id: str = "", billing_account_id: str = "", customer_id: str = "", original_billing_txn_id: str = "") -> str:
    """Look up billing ledger entries: invoices, payments, returned payments, returned-payment fees, premium credits and refunds, with invoice number, coverage months, product line, amount, date, payment method and reference, payment purpose and credit reason.

    Every reference number below is optional; supply whichever you already hold, and every
    record matching all of them is returned. With none supplied, all such records are listed.

    Args:
        billing_txn_id: The reference number of the billing entry itself; leave "" if unknown.
        billing_account_id: The reference number of a premium billing account; leave "" if unknown.
        customer_id: The customer reference number (member subscriber, employer or practice); leave "" if unknown.
        original_billing_txn_id: The reference number of the billing entry this entry follows (the payment returned, the return charged, or the credit refunded); leave "" if unknown.
    """
    match = {k: v for k, v in {"billing_txn_id": billing_txn_id, "billing_account_id": billing_account_id, "customer_id": customer_id, "original_billing_txn_id": original_billing_txn_id}.items() if v}
    rows = ctx.find("billing_transactions", **match)
    return str(rows) if rows else f"No billing_transactions records for {match}."

@tool(owner="agent", rw="read")
def find_billing_requests(ctx: ToolContext, billing_request_id: str = "", customer_id: str = "", billing_account_id: str = "") -> str:
    """Look up billing requests (account closure, payment-method change or refund request) with the requested payment method, effective date and processing status.

    Every reference number below is optional; supply whichever you already hold, and every
    record matching all of them is returned. With none supplied, all such records are listed.

    Args:
        billing_request_id: The reference number of the billing request itself; leave "" if unknown.
        customer_id: The customer reference number (member subscriber, employer or practice); leave "" if unknown.
        billing_account_id: The reference number of a premium billing account; leave "" if unknown.
    """
    match = {k: v for k, v in {"billing_request_id": billing_request_id, "customer_id": customer_id, "billing_account_id": billing_account_id}.items() if v}
    rows = ctx.find("billing_requests", **match)
    return str(rows) if rows else f"No billing_requests records for {match}."

@tool(owner="agent", rw="read")
def find_provider_agreements(ctx: ToolContext, provider_agreement_id: str = "", customer_id: str = "") -> str:
    """Look up network participation agreements held by dental and vision practices: agreement type, status, rendering provider and NPI, specialty, location type and state, fee schedule, panel status, credentialing dates, license and liability coverage on file, and termination notice details.

    Every reference number below is optional; supply whichever you already hold, and every
    record matching all of them is returned. With none supplied, all such records are listed.

    Args:
        provider_agreement_id: The reference number of a network participation agreement (the record itself); leave "" if unknown.
        customer_id: The customer reference number (member subscriber, employer or practice); leave "" if unknown.
    """
    match = {k: v for k, v in {"provider_agreement_id": provider_agreement_id, "customer_id": customer_id}.items() if v}
    rows = ctx.find("provider_agreements", **match)
    return str(rows) if rows else f"No provider_agreements records for {match}."

@tool(owner="agent", rw="read")
def find_provider_payment_events(ctx: ToolContext, provider_payment_event_id: str = "", provider_agreement_id: str = "", customer_id: str = "", dental_claim_line_id: str = "", vision_claim_id: str = "", ortho_payment_id: str = "", original_payment_event_id: str = "") -> str:
    """Look up provider payment and overpayment entries: remittances, overpayment notices, offsets, refunds received and reductions, with remittance and case numbers, the member claim an overpayment arose from, original payment date, amount and date.

    Every reference number below is optional; supply whichever you already hold, and every
    record matching all of them is returned. With none supplied, all such records are listed.

    Args:
        provider_payment_event_id: The reference number of a provider payment or overpayment entry (the record itself); leave "" if unknown.
        provider_agreement_id: The reference number of a network participation agreement; leave "" if unknown.
        customer_id: The customer reference number (member subscriber, employer or practice); leave "" if unknown.
        dental_claim_line_id: The reference number of a dental claim line; leave "" if unknown.
        vision_claim_id: The reference number of a vision claim service; leave "" if unknown.
        ortho_payment_id: The reference number of an orthodontic payment; leave "" if unknown.
        original_payment_event_id: The reference number of the overpayment an offset, refund or reduction settles; leave "" if unknown.
    """
    match = {k: v for k, v in {"provider_payment_event_id": provider_payment_event_id, "provider_agreement_id": provider_agreement_id, "customer_id": customer_id, "dental_claim_line_id": dental_claim_line_id, "vision_claim_id": vision_claim_id, "ortho_payment_id": ortho_payment_id, "original_payment_event_id": original_payment_event_id}.items() if v}
    rows = ctx.find("provider_payment_events", **match)
    return str(rows) if rows else f"No provider_payment_events records for {match}."

@tool(owner="agent", rw="read")
def find_provider_disputes(ctx: ToolContext, provider_dispute_id: str = "", provider_agreement_id: str = "", customer_id: str = "", provider_payment_event_id: str = "", original_dispute_id: str = "") -> str:
    """Look up provider disputes of overpayment notices: the overpayment disputed, the stated ground, filing and due dates, resolution date, outcome and the amount that stands.

    Every reference number below is optional; supply whichever you already hold, and every
    record matching all of them is returned. With none supplied, all such records are listed.

    Args:
        provider_dispute_id: The reference number of the provider dispute record itself; leave "" if unknown.
        provider_agreement_id: The reference number of a network participation agreement; leave "" if unknown.
        customer_id: The customer reference number (member subscriber, employer or practice); leave "" if unknown.
        provider_payment_event_id: The reference number of a provider payment or overpayment entry; leave "" if unknown.
        original_dispute_id: The reference number of the dispute filing a resolution decides; leave "" if unknown.
    """
    match = {k: v for k, v in {"provider_dispute_id": provider_dispute_id, "provider_agreement_id": provider_agreement_id, "customer_id": customer_id, "provider_payment_event_id": provider_payment_event_id, "original_dispute_id": original_dispute_id}.items() if v}
    rows = ctx.find("provider_disputes", **match)
    return str(rows) if rows else f"No provider_disputes records for {match}."

@tool(owner="agent", rw="read")
def find_provider_requests(ctx: ToolContext, provider_request_id: str = "", customer_id: str = "", provider_agreement_id: str = "") -> str:
    """Look up practice requests (termination notice, rescission of a notice, panel status change) with the requested panel status, effective date and processing status.

    Every reference number below is optional; supply whichever you already hold, and every
    record matching all of them is returned. With none supplied, all such records are listed.

    Args:
        provider_request_id: The reference number of the practice request itself; leave "" if unknown.
        customer_id: The customer reference number (member subscriber, employer or practice); leave "" if unknown.
        provider_agreement_id: The reference number of a network participation agreement; leave "" if unknown.
    """
    match = {k: v for k, v in {"provider_request_id": provider_request_id, "customer_id": customer_id, "provider_agreement_id": provider_agreement_id}.items() if v}
    rows = ctx.find("provider_requests", **match)
    return str(rows) if rows else f"No provider_requests records for {match}."

@tool(owner="agent", rw="read")
def find_dhmo_plans(ctx: ToolContext, dhmo_plan_id: str = "", customer_id: str = "", billing_account_id: str = "", group_contract_id: str = "", assigned_pcd_agreement_id: str = "") -> str:
    """Look up DHMO enrollments: plan (copay schedule), status, market, coverage tier, covered person, assigned primary care dentist and assignment date, coverage dates and termination details.

    Every reference number below is optional; supply whichever you already hold, and every
    record matching all of them is returned. With none supplied, all such records are listed.

    Args:
        dhmo_plan_id: The reference number of a DHMO enrollment (the record itself); leave "" if unknown.
        customer_id: The customer reference number (member subscriber, employer or practice); leave "" if unknown.
        billing_account_id: The reference number of a premium billing account; leave "" if unknown.
        group_contract_id: The reference number of an employer group contract; leave "" if unknown.
        assigned_pcd_agreement_id: The reference number of the primary care dentist agreement a DHMO member is assigned to; leave "" if unknown.
    """
    match = {k: v for k, v in {"dhmo_plan_id": dhmo_plan_id, "customer_id": customer_id, "billing_account_id": billing_account_id, "group_contract_id": group_contract_id, "assigned_pcd_agreement_id": assigned_pcd_agreement_id}.items() if v}
    rows = ctx.find("dhmo_plans", **match)
    return str(rows) if rows else f"No dhmo_plans records for {match}."

@tool(owner="agent", rw="read")
def find_dhmo_services(ctx: ToolContext, dhmo_service_id: str = "", dhmo_plan_id: str = "", customer_id: str = "", provider_agreement_id: str = "", referral_service_id: str = "") -> str:
    """Look up DHMO encounter lines, specialist referrals and out-of-area emergency reimbursements: reference and line, provider, procedure and schedule category, specialty, tooth, service date, member copay, metal upcharge, referral validity, emergency distance and reimbursement, and remark.

    Every reference number below is optional; supply whichever you already hold, and every
    record matching all of them is returned. With none supplied, all such records are listed.

    Args:
        dhmo_service_id: The reference number of the DHMO encounter line, referral or reimbursement itself; leave "" if unknown.
        dhmo_plan_id: The reference number of a DHMO enrollment; leave "" if unknown.
        customer_id: The customer reference number (member subscriber, employer or practice); leave "" if unknown.
        provider_agreement_id: The reference number of a network participation agreement; leave "" if unknown.
        referral_service_id: The reference number of the DHMO referral a specialist service was performed under; leave "" if unknown.
    """
    match = {k: v for k, v in {"dhmo_service_id": dhmo_service_id, "dhmo_plan_id": dhmo_plan_id, "customer_id": customer_id, "provider_agreement_id": provider_agreement_id, "referral_service_id": referral_service_id}.items() if v}
    rows = ctx.find("dhmo_services", **match)
    return str(rows) if rows else f"No dhmo_services records for {match}."

@tool(owner="agent", rw="read")
def find_group_contracts(ctx: ToolContext, group_contract_id: str = "", customer_id: str = "") -> str:
    """Look up employer group contracts: size segment, status, group number, situs state, contribution arrangement, plans offered, contracted rates, eligible employees, new-hire waiting period, effective, renewal and rate-guarantee dates, and termination details.

    Every reference number below is optional; supply whichever you already hold, and every
    record matching all of them is returned. With none supplied, all such records are listed.

    Args:
        group_contract_id: The reference number of an employer group contract (the record itself); leave "" if unknown.
        customer_id: The customer reference number (member subscriber, employer or practice); leave "" if unknown.
    """
    match = {k: v for k, v in {"group_contract_id": group_contract_id, "customer_id": customer_id}.items() if v}
    rows = ctx.find("group_contracts", **match)
    return str(rows) if rows else f"No group_contracts records for {match}."

@tool(owner="agent", rw="read")
def find_group_eligibility_events(ctx: ToolContext, group_eligibility_event_id: str = "", group_contract_id: str = "", customer_id: str = "", original_eligibility_event_id: str = "") -> str:
    """Look up group eligibility events reported by employers: member additions and terminations, continuation elections and census reports, with the employee, reason, coverage tier, event, effective and report dates, and census counts.

    Every reference number below is optional; supply whichever you already hold, and every
    record matching all of them is returned. With none supplied, all such records are listed.

    Args:
        group_eligibility_event_id: The reference number of the group eligibility event itself; leave "" if unknown.
        group_contract_id: The reference number of an employer group contract; leave "" if unknown.
        customer_id: The customer reference number (member subscriber, employer or practice); leave "" if unknown.
        original_eligibility_event_id: The reference number of the member termination a continuation election follows; leave "" if unknown.
    """
    match = {k: v for k, v in {"group_eligibility_event_id": group_eligibility_event_id, "group_contract_id": group_contract_id, "customer_id": customer_id, "original_eligibility_event_id": original_eligibility_event_id}.items() if v}
    rows = ctx.find("group_eligibility_events", **match)
    return str(rows) if rows else f"No group_eligibility_events records for {match}."

@tool(owner="agent", rw="read")
def find_savings_memberships(ctx: ToolContext, savings_membership_id: str = "", customer_id: str = "") -> str:
    """Look up dental and vision savings memberships (discount plans, not insurance): membership plan, status, billing frequency, household size, enrollment, activation, renewal and cancellation dates and the fee balance.

    Every reference number below is optional; supply whichever you already hold, and every
    record matching all of them is returned. With none supplied, all such records are listed.

    Args:
        savings_membership_id: The reference number of a savings membership (the record itself); leave "" if unknown.
        customer_id: The customer reference number (member subscriber, employer or practice); leave "" if unknown.
    """
    match = {k: v for k, v in {"savings_membership_id": savings_membership_id, "customer_id": customer_id}.items() if v}
    rows = ctx.find("savings_memberships", **match)
    return str(rows) if rows else f"No savings_memberships records for {match}."

@tool(owner="agent", rw="read")
def find_savings_transactions(ctx: ToolContext, savings_txn_id: str = "", savings_membership_id: str = "", customer_id: str = "", original_savings_txn_id: str = "", provider_agreement_id: str = "") -> str:
    """Look up savings membership fee entries and recorded discounted visits: fee component and period, amount, date, payment reference, credit reason, practice, service category, usual and discounted fees.

    Every reference number below is optional; supply whichever you already hold, and every
    record matching all of them is returned. With none supplied, all such records are listed.

    Args:
        savings_txn_id: The reference number of the savings fee entry or visit itself; leave "" if unknown.
        savings_membership_id: The reference number of a savings membership; leave "" if unknown.
        customer_id: The customer reference number (member subscriber, employer or practice); leave "" if unknown.
        original_savings_txn_id: The reference number of the savings fee entry a credit or refund follows; leave "" if unknown.
        provider_agreement_id: The reference number of a network participation agreement; leave "" if unknown.
    """
    match = {k: v for k, v in {"savings_txn_id": savings_txn_id, "savings_membership_id": savings_membership_id, "customer_id": customer_id, "original_savings_txn_id": original_savings_txn_id, "provider_agreement_id": provider_agreement_id}.items() if v}
    rows = ctx.find("savings_transactions", **match)
    return str(rows) if rows else f"No savings_transactions records for {match}."


@tool(owner="agent", rw="read")
def find_customers(ctx: ToolContext, customer_id: str = "", name: str = "", phone_number: str = "",
                   email: str = "", account_number: str = "") -> str:
    """Find the customer profile a contact is about: an individual member subscriber, an employer
    group, or a dental or vision practice. Search by the customer reference number, or by what the
    caller can naturally tell you: the name on the profile, the phone number, the email address, or
    the number on their own documents (the member ID on the ID card, the group number, or the Cascade
    provider number). Every criterion is optional; supply whichever you have.

    On a single match the profile is returned: customer type, name, the account number, phone
    number, email, date of birth (individuals), last four digits of the tax ID, ZIP code, state and
    the date the profile was opened. Finding a profile does not confirm that the caller is who they
    say they are; identity is confirmed separately.

    Args:
        customer_id: The customer reference number, if already known; leave "" otherwise.
        name: Full name of the subscriber, employer or practice as the caller states it; leave "" if not given.
        phone_number: Phone number as the caller states it (10 digits); leave "" if not given.
        email: Email address as the caller states it; leave "" if not given.
        account_number: Member ID from the ID card, group number, or Cascade provider number, exactly as read by the caller; leave "" if not given.
    """
    match = {k: v for k, v in {"customer_id": customer_id, "name": name, "phone_number": phone_number,
                               "email": email, "account_number": account_number}.items() if v}
    if not match:
        return "Error: provide at least one reference number or detail to find the customer."
    rows = ctx.fuzzy_find("customers", **match)
    if not rows:
        return f"No customer matches {match}."
    if len(rows) > 1:
        return f"Error: {len(rows)} customers match {match}; ask for one more detail to tell them apart."
    return str(rows[0])


@tool(owner="agent", rw="write")
def verify_customer_identity(ctx: ToolContext, customer_id: str, phone_number: str = "", email: str = "",
                             date_of_birth: str = "", tax_id_last4: str = "", postal_code: str = "") -> str:
    """Confirm the caller's identity and record the outcome; identity must be confirmed before any
    account information is discussed or any change is made. This tool performs the comparison
    itself: it compares each detail the caller states against the customer profile, counts the
    matches, and confirms identity only when at least 2 details match. The customer reference number
    only tells the tool which profile to compare against and never counts as a match.

    Callers usually give only some details, so pass only the values the caller actually stated,
    exactly as stated, and leave the rest empty. The outcome is recorded; if a first attempt fails
    and a later attempt with more details succeeds, the confirmation stands.

    Args:
        customer_id: The customer reference number taken from the customer profile lookup. Required; used only to retrieve the profile and not counted as a match.
        phone_number: Phone number on the profile as stated by the caller, 10 digits with no punctuation; leave "" if not stated.
        email: Email address on the profile as stated by the caller; leave "" if not stated.
        date_of_birth: The subscriber's date of birth as stated by the caller, YYYY-MM-DD (individual members only); leave "" if not stated.
        tax_id_last4: Last four digits of the SSN (individuals) or of the tax identification number (employers and practices) as stated by the caller; leave "" if not stated.
        postal_code: 5-digit ZIP code of the mailing address on the profile as stated by the caller; leave "" if not stated.
    """
    if not customer_id:
        return "Error: customer_id is required; find the customer profile first and pass its reference number."
    rows = ctx.find("customers", customer_id=customer_id)
    if not rows:
        return f"Error: no customer {customer_id}; cannot verify."
    rec = rows[0]
    # The locator customer_id is not part of `supplied`: fetching a profile is not proving identity.
    supplied = {"phone_number": phone_number, "email": email, "date_of_birth": date_of_birth,
                "tax_id_last4": tax_id_last4, "postal_code": postal_code}
    matched = sum(1 for field, value in supplied.items()
                  if value and rec.get(field) and str(rec.get(field)).strip().lower() == str(value).strip().lower())
    verified = matched >= 2
    rid = ctx.make_id("ver_", customer_id)
    # Store only the reproducible boolean; upsert and never downgrade True -> False.
    prior = ctx.find("identity_verifications", verification_id=rid)
    verified = verified or bool(prior and prior[0].get("verified"))
    if prior:
        ctx.update("identity_verifications", rid, verified=verified, verified_at=ctx.now())
    else:
        ctx.create("identity_verifications", rid, verification_id=rid, customer_id=customer_id,
                   verified=verified, verified_at=ctx.now())
    return (f"Identity confirmed for {customer_id} ({matched} detail(s) matched)." if verified
            else f"Identity NOT confirmed for {customer_id} (only {matched} of the required 2 details matched). Ask the caller for another detail on the profile and try again.")


@tool(owner="agent", rw="write")
def transfer_to_human_agent(ctx: ToolContext, customer_id: str, reason: str) -> str:
    """Transfer the customer to a human representative and record the transfer and its reason.
    Use it in one of two situations: when no Cascade rule lets you resolve what the customer is
    asking for, or when the customer has explicitly asked to speak with a human representative at
    least 2 times.

    Args:
        customer_id: The customer reference number taken from the customer profile lookup (the profile must exist).
        reason: Why the customer is transferred, exactly one of two values. POLICY_NOT_COVERED: no Cascade rule resolves the request. CUSTOMER_REQUESTED: the customer has explicitly asked for a human representative at least 2 times.
    """
    allowed = {"POLICY_NOT_COVERED", "CUSTOMER_REQUESTED"}
    if reason not in allowed:
        return f"Error: unknown transfer reason '{reason}'. Valid: {', '.join(sorted(allowed))}."
    if not ctx.find("customers", customer_id=customer_id):
        return f"Error: no customer {customer_id}; cannot record the transfer."
    rid = ctx.make_id("hof_", customer_id, reason)
    ctx.create("human_handoffs", rid, handoff_id=rid, customer_id=customer_id,
               reason=reason, created_at=ctx.now())
    return f"Transfer to a human representative recorded for {customer_id} ({reason})."

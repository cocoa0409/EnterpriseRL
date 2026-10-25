"""Shared tools for env_0079_property_restoration_contractor (Ridgecrest Restoration & Reconstruction).

One record-lookup tool per record type, the customer lookup that doubles as the identity entry,
the identity-verification write and the handoff to a human representative.
"""

from erlbench import ToolContext, tool

@tool(owner="agent", rw="read")
def find_verification_log(ctx: ToolContext, verification_id: str = "", customer_id: str = "") -> str:
    """Look up identity verification outcomes.

    Each record shows whether a customer's identity has been verified and when it was last checked. Search by any reference number already in hand; every
    criterion is optional and several may be combined. All matching records are returned, or a
    short notice when nothing matches.

    Args:
        verification_id: Reference number - the reference number of the identity verification record itself; leave "" if unknown.
        customer_id: Reference number - the customer reference number; leave "" if unknown.
    """
    match = {k: v for k, v in {"verification_id": verification_id, "customer_id": customer_id}.items() if v}
    rows = ctx.find("verification_log", **match)
    return str(rows) if rows else f"No identity verification outcomes found for {match}."


@tool(owner="agent", rw="read")
def find_handoff_log(ctx: ToolContext, handoff_id: str = "", customer_id: str = "") -> str:
    """Look up handoffs to a human representative.

    Each record shows the customer handed over, the reason and the moment of handoff. Search by any reference number already in hand; every
    criterion is optional and several may be combined. All matching records are returned, or a
    short notice when nothing matches.

    Args:
        handoff_id: Reference number - the reference number of the handoff record itself; leave "" if unknown.
        customer_id: Reference number - the customer reference number; leave "" if unknown.
    """
    match = {k: v for k, v in {"handoff_id": handoff_id, "customer_id": customer_id}.items() if v}
    rows = ctx.find("handoff_log", **match)
    return str(rows) if rows else f"No handoffs to a human representative found for {match}."


@tool(owner="agent", rw="read")
def find_water_jobs(ctx: ToolContext, water_job_id: str = "", customer_id: str = "", claim_file_id: str = "") -> str:
    """Look up water damage mitigation jobs.

    Each record shows tier, status, loss address and building details, water category and class, affected area, dispatch window and arrival time, linked claim file, funding source, key dates from dispatch to closing, invoice amount and current balance. Search by any reference number already in hand; every
    criterion is optional and several may be combined. All matching records are returned, or a
    short notice when nothing matches.

    Args:
        water_job_id: Reference number - the water mitigation job reference number; leave "" if unknown.
        customer_id: Reference number - the customer reference number; leave "" if unknown.
        claim_file_id: Reference number - the claim file reference number; leave "" if unknown.
    """
    match = {k: v for k, v in {"water_job_id": water_job_id, "customer_id": customer_id, "claim_file_id": claim_file_id}.items() if v}
    rows = ctx.find("water_jobs", **match)
    return str(rows) if rows else f"No water damage mitigation jobs found for {match}."


@tool(owner="agent", rw="read")
def find_water_charges(ctx: ToolContext, water_charge_id: str = "", water_job_id: str = "", customer_id: str = "", source_payment_id: str = "") -> str:
    """Look up charge lines on water mitigation jobs.

    Each record shows the service call, equipment days, mitigation services, monitoring visits, late fees and card surcharges, each with its date, quantity, rate and amount. Search by any reference number already in hand; every
    criterion is optional and several may be combined. All matching records are returned, or a
    short notice when nothing matches.

    Args:
        water_charge_id: Reference number - the reference number of a water job charge line; leave "" if unknown.
        water_job_id: Reference number - the water mitigation job reference number; leave "" if unknown.
        customer_id: Reference number - the customer reference number; leave "" if unknown.
        source_payment_id: Reference number - the reference number of the payment a refund or surcharge relates to; leave "" if unknown.
    """
    match = {k: v for k, v in {"water_charge_id": water_charge_id, "water_job_id": water_job_id, "customer_id": customer_id, "source_payment_id": source_payment_id}.items() if v}
    rows = ctx.find("water_charges", **match)
    return str(rows) if rows else f"No charge lines on water mitigation jobs found for {match}."


@tool(owner="agent", rw="read")
def find_water_payments(ctx: ToolContext, water_payment_id: str = "", water_job_id: str = "", customer_id: str = "", claim_payment_id: str = "", source_charge_id: str = "", source_payment_id: str = "") -> str:
    """Look up payments, insurance postings, credits and refunds on water mitigation jobs.

    Each record shows tender, reference numbers, the carrier payment or charge line each one relates to, posting date and amount. Search by any reference number already in hand; every
    criterion is optional and several may be combined. All matching records are returned, or a
    short notice when nothing matches.

    Args:
        water_payment_id: Reference number - the reference number of a water job payment, insurance posting, credit or refund line; leave "" if unknown.
        water_job_id: Reference number - the water mitigation job reference number; leave "" if unknown.
        customer_id: Reference number - the customer reference number; leave "" if unknown.
        claim_payment_id: Reference number - the reference number of a carrier payment; leave "" if unknown.
        source_charge_id: Reference number - the reference number of the charge line a credit corrects; leave "" if unknown.
        source_payment_id: Reference number - the reference number of the payment a refund or surcharge relates to; leave "" if unknown.
    """
    match = {k: v for k, v in {"water_payment_id": water_payment_id, "water_job_id": water_job_id, "customer_id": customer_id, "claim_payment_id": claim_payment_id, "source_charge_id": source_charge_id, "source_payment_id": source_payment_id}.items() if v}
    rows = ctx.find("water_payments", **match)
    return str(rows) if rows else f"No payments, insurance postings, credits and refunds on water mitigation jobs found for {match}."


@tool(owner="agent", rw="read")
def find_fire_jobs(ctx: ToolContext, fire_job_id: str = "", customer_id: str = "", claim_file_id: str = "") -> str:
    """Look up fire and smoke mitigation jobs.

    Each record shows tier, status, loss address and building details, smoke severity, occupancy during work, dispatch window and arrival time, linked claim file, funding source, key dates, invoice amount and current balance. Search by any reference number already in hand; every
    criterion is optional and several may be combined. All matching records are returned, or a
    short notice when nothing matches.

    Args:
        fire_job_id: Reference number - the fire and smoke job reference number; leave "" if unknown.
        customer_id: Reference number - the customer reference number; leave "" if unknown.
        claim_file_id: Reference number - the claim file reference number; leave "" if unknown.
    """
    match = {k: v for k, v in {"fire_job_id": fire_job_id, "customer_id": customer_id, "claim_file_id": claim_file_id}.items() if v}
    rows = ctx.find("fire_jobs", **match)
    return str(rows) if rows else f"No fire and smoke mitigation jobs found for {match}."


@tool(owner="agent", rw="read")
def find_fire_charges(ctx: ToolContext, fire_charge_id: str = "", fire_job_id: str = "", customer_id: str = "", source_payment_id: str = "") -> str:
    """Look up charge lines on fire and smoke jobs.

    Each record shows the service call, board-up, equipment days, cleaning services, late fees and card surcharges, each with its date, quantity, rate and amount. Search by any reference number already in hand; every
    criterion is optional and several may be combined. All matching records are returned, or a
    short notice when nothing matches.

    Args:
        fire_charge_id: Reference number - the reference number of a fire job charge line; leave "" if unknown.
        fire_job_id: Reference number - the fire and smoke job reference number; leave "" if unknown.
        customer_id: Reference number - the customer reference number; leave "" if unknown.
        source_payment_id: Reference number - the reference number of the payment a refund or surcharge relates to; leave "" if unknown.
    """
    match = {k: v for k, v in {"fire_charge_id": fire_charge_id, "fire_job_id": fire_job_id, "customer_id": customer_id, "source_payment_id": source_payment_id}.items() if v}
    rows = ctx.find("fire_charges", **match)
    return str(rows) if rows else f"No charge lines on fire and smoke jobs found for {match}."


@tool(owner="agent", rw="read")
def find_fire_payments(ctx: ToolContext, fire_payment_id: str = "", fire_job_id: str = "", customer_id: str = "", claim_payment_id: str = "", source_charge_id: str = "", source_payment_id: str = "") -> str:
    """Look up payments, insurance postings, credits and refunds on fire and smoke jobs.

    Each record shows tender, reference numbers, the carrier payment or charge line each one relates to, posting date and amount. Search by any reference number already in hand; every
    criterion is optional and several may be combined. All matching records are returned, or a
    short notice when nothing matches.

    Args:
        fire_payment_id: Reference number - the reference number of a fire job payment, insurance posting, credit or refund line; leave "" if unknown.
        fire_job_id: Reference number - the fire and smoke job reference number; leave "" if unknown.
        customer_id: Reference number - the customer reference number; leave "" if unknown.
        claim_payment_id: Reference number - the reference number of a carrier payment; leave "" if unknown.
        source_charge_id: Reference number - the reference number of the charge line a credit corrects; leave "" if unknown.
        source_payment_id: Reference number - the reference number of the payment a refund or surcharge relates to; leave "" if unknown.
    """
    match = {k: v for k, v in {"fire_payment_id": fire_payment_id, "fire_job_id": fire_job_id, "customer_id": customer_id, "claim_payment_id": claim_payment_id, "source_charge_id": source_charge_id, "source_payment_id": source_payment_id}.items() if v}
    rows = ctx.find("fire_payments", **match)
    return str(rows) if rows else f"No payments, insurance postings, credits and refunds on fire and smoke jobs found for {match}."


@tool(owner="agent", rw="read")
def find_mold_jobs(ctx: ToolContext, mold_job_id: str = "", customer_id: str = "", claim_file_id: str = "", water_job_id: str = "", prior_mold_job_id: str = "") -> str:
    """Look up mold remediation jobs.

    Each record shows tier, status, address, growth location and area, independent assessor and protocol, linked water job, earlier mold job and claim file, funding source, scheduled and actual dates through clearance and closing, invoice amount and current balance. Search by any reference number already in hand; every
    criterion is optional and several may be combined. All matching records are returned, or a
    short notice when nothing matches.

    Args:
        mold_job_id: Reference number - the mold remediation job reference number; leave "" if unknown.
        customer_id: Reference number - the customer reference number; leave "" if unknown.
        claim_file_id: Reference number - the claim file reference number; leave "" if unknown.
        water_job_id: Reference number - the water mitigation job reference number; leave "" if unknown.
        prior_mold_job_id: Reference number - the reference number of an earlier mold job this job re-remediates; leave "" if unknown.
    """
    match = {k: v for k, v in {"mold_job_id": mold_job_id, "customer_id": customer_id, "claim_file_id": claim_file_id, "water_job_id": water_job_id, "prior_mold_job_id": prior_mold_job_id}.items() if v}
    rows = ctx.find("mold_jobs", **match)
    return str(rows) if rows else f"No mold remediation jobs found for {match}."


@tool(owner="agent", rw="read")
def find_mold_charges(ctx: ToolContext, mold_charge_id: str = "", mold_job_id: str = "", customer_id: str = "", mold_test_id: str = "", source_payment_id: str = "") -> str:
    """Look up charge lines on mold remediation jobs.

    Each record shows remediation scope, equipment days, clearance fees, cancellation fees, late fees and card surcharges, each with its date, quantity, rate and amount. Search by any reference number already in hand; every
    criterion is optional and several may be combined. All matching records are returned, or a
    short notice when nothing matches.

    Args:
        mold_charge_id: Reference number - the reference number of a mold job charge line; leave "" if unknown.
        mold_job_id: Reference number - the mold remediation job reference number; leave "" if unknown.
        customer_id: Reference number - the customer reference number; leave "" if unknown.
        mold_test_id: Reference number - the reference number of a mold clearance test result; leave "" if unknown.
        source_payment_id: Reference number - the reference number of the payment a refund or surcharge relates to; leave "" if unknown.
    """
    match = {k: v for k, v in {"mold_charge_id": mold_charge_id, "mold_job_id": mold_job_id, "customer_id": customer_id, "mold_test_id": mold_test_id, "source_payment_id": source_payment_id}.items() if v}
    rows = ctx.find("mold_charges", **match)
    return str(rows) if rows else f"No charge lines on mold remediation jobs found for {match}."


@tool(owner="agent", rw="read")
def find_mold_payments(ctx: ToolContext, mold_payment_id: str = "", mold_job_id: str = "", customer_id: str = "", claim_payment_id: str = "", source_charge_id: str = "", source_payment_id: str = "") -> str:
    """Look up payments, insurance postings, credits and refunds on mold remediation jobs.

    Each record shows tender, reference numbers, the carrier payment or charge line each one relates to, posting date and amount. Search by any reference number already in hand; every
    criterion is optional and several may be combined. All matching records are returned, or a
    short notice when nothing matches.

    Args:
        mold_payment_id: Reference number - the reference number of a mold job payment, insurance posting, credit or refund line; leave "" if unknown.
        mold_job_id: Reference number - the mold remediation job reference number; leave "" if unknown.
        customer_id: Reference number - the customer reference number; leave "" if unknown.
        claim_payment_id: Reference number - the reference number of a carrier payment; leave "" if unknown.
        source_charge_id: Reference number - the reference number of the charge line a credit corrects; leave "" if unknown.
        source_payment_id: Reference number - the reference number of the payment a refund or surcharge relates to; leave "" if unknown.
    """
    match = {k: v for k, v in {"mold_payment_id": mold_payment_id, "mold_job_id": mold_job_id, "customer_id": customer_id, "claim_payment_id": claim_payment_id, "source_charge_id": source_charge_id, "source_payment_id": source_payment_id}.items() if v}
    rows = ctx.find("mold_payments", **match)
    return str(rows) if rows else f"No payments, insurance postings, credits and refunds on mold remediation jobs found for {match}."


@tool(owner="agent", rw="read")
def find_mold_clearance_tests(ctx: ToolContext, mold_test_id: str = "", mold_job_id: str = "", customer_id: str = "") -> str:
    """Look up mold clearance results.

    Each record shows the attempt number, test date, who established clearance and whether it passed. Search by any reference number already in hand; every
    criterion is optional and several may be combined. All matching records are returned, or a
    short notice when nothing matches.

    Args:
        mold_test_id: Reference number - the reference number of a mold clearance test result; leave "" if unknown.
        mold_job_id: Reference number - the mold remediation job reference number; leave "" if unknown.
        customer_id: Reference number - the customer reference number; leave "" if unknown.
    """
    match = {k: v for k, v in {"mold_test_id": mold_test_id, "mold_job_id": mold_job_id, "customer_id": customer_id}.items() if v}
    rows = ctx.find("mold_clearance_tests", **match)
    return str(rows) if rows else f"No mold clearance results found for {match}."


@tool(owner="agent", rw="read")
def find_rebuild_contracts(ctx: ToolContext, rebuild_contract_id: str = "", customer_id: str = "", claim_file_id: str = "", mitigation_job_id: str = "") -> str:
    """Look up reconstruction contracts.

    Each record shows tier, status, address, building details, linked claim file and mitigation job, contract amount, where and when it was signed, permit, construction, suspension and completion dates, invoice amount and current balance. Search by any reference number already in hand; every
    criterion is optional and several may be combined. All matching records are returned, or a
    short notice when nothing matches.

    Args:
        rebuild_contract_id: Reference number - the reconstruction contract reference number; leave "" if unknown.
        customer_id: Reference number - the customer reference number; leave "" if unknown.
        claim_file_id: Reference number - the claim file reference number; leave "" if unknown.
        mitigation_job_id: Reference number - the reference number of the water, fire or mold job that preceded the work at the same loss; leave "" if unknown.
    """
    match = {k: v for k, v in {"rebuild_contract_id": rebuild_contract_id, "customer_id": customer_id, "claim_file_id": claim_file_id, "mitigation_job_id": mitigation_job_id}.items() if v}
    rows = ctx.find("rebuild_contracts", **match)
    return str(rows) if rows else f"No reconstruction contracts found for {match}."


@tool(owner="agent", rw="read")
def find_rebuild_charges(ctx: ToolContext, rebuild_charge_id: str = "", rebuild_contract_id: str = "", customer_id: str = "", change_order_id: str = "", rebuild_draw_id: str = "", warranty_claim_id: str = "") -> str:
    """Look up charge lines on reconstruction contracts.

    Each record shows the contract price, change orders, permit and professional fees, cancellation, remobilization, overdue draw and warranty trip charges, each with its date and amount. Search by any reference number already in hand; every
    criterion is optional and several may be combined. All matching records are returned, or a
    short notice when nothing matches.

    Args:
        rebuild_charge_id: Reference number - the reference number of a reconstruction contract charge line; leave "" if unknown.
        rebuild_contract_id: Reference number - the reconstruction contract reference number; leave "" if unknown.
        customer_id: Reference number - the customer reference number; leave "" if unknown.
        change_order_id: Reference number - the change order reference number; leave "" if unknown.
        rebuild_draw_id: Reference number - the reference number of a draw request; leave "" if unknown.
        warranty_claim_id: Reference number - the reference number of a warranty report or warranty inspection; leave "" if unknown.
    """
    match = {k: v for k, v in {"rebuild_charge_id": rebuild_charge_id, "rebuild_contract_id": rebuild_contract_id, "customer_id": customer_id, "change_order_id": change_order_id, "rebuild_draw_id": rebuild_draw_id, "warranty_claim_id": warranty_claim_id}.items() if v}
    rows = ctx.find("rebuild_charges", **match)
    return str(rows) if rows else f"No charge lines on reconstruction contracts found for {match}."


@tool(owner="agent", rw="read")
def find_rebuild_draws(ctx: ToolContext, rebuild_draw_id: str = "", rebuild_contract_id: str = "", customer_id: str = "") -> str:
    """Look up draw requests on reconstruction contracts.

    Each record shows milestone, draw number, funding route, lien waiver, request and due dates and amount requested. Search by any reference number already in hand; every
    criterion is optional and several may be combined. All matching records are returned, or a
    short notice when nothing matches.

    Args:
        rebuild_draw_id: Reference number - the reference number of a draw request; leave "" if unknown.
        rebuild_contract_id: Reference number - the reconstruction contract reference number; leave "" if unknown.
        customer_id: Reference number - the customer reference number; leave "" if unknown.
    """
    match = {k: v for k, v in {"rebuild_draw_id": rebuild_draw_id, "rebuild_contract_id": rebuild_contract_id, "customer_id": customer_id}.items() if v}
    rows = ctx.find("rebuild_draws", **match)
    return str(rows) if rows else f"No draw requests on reconstruction contracts found for {match}."


@tool(owner="agent", rw="read")
def find_rebuild_payments(ctx: ToolContext, rebuild_payment_id: str = "", rebuild_contract_id: str = "", customer_id: str = "", rebuild_draw_id: str = "", claim_payment_id: str = "", change_order_id: str = "") -> str:
    """Look up draw payments, insurance postings and change order credits on reconstruction contracts.

    Each record shows the draw paid, tender, reference numbers, carrier payment or change order concerned, posting date and amount. Search by any reference number already in hand; every
    criterion is optional and several may be combined. All matching records are returned, or a
    short notice when nothing matches.

    Args:
        rebuild_payment_id: Reference number - the reference number of a draw payment, insurance posting or change order credit; leave "" if unknown.
        rebuild_contract_id: Reference number - the reconstruction contract reference number; leave "" if unknown.
        customer_id: Reference number - the customer reference number; leave "" if unknown.
        rebuild_draw_id: Reference number - the reference number of a draw request; leave "" if unknown.
        claim_payment_id: Reference number - the reference number of a carrier payment; leave "" if unknown.
        change_order_id: Reference number - the change order reference number; leave "" if unknown.
    """
    match = {k: v for k, v in {"rebuild_payment_id": rebuild_payment_id, "rebuild_contract_id": rebuild_contract_id, "customer_id": customer_id, "rebuild_draw_id": rebuild_draw_id, "claim_payment_id": claim_payment_id, "change_order_id": change_order_id}.items() if v}
    rows = ctx.find("rebuild_payments", **match)
    return str(rows) if rows else f"No draw payments, insurance postings and change order credits on reconstruction contracts found for {match}."


@tool(owner="agent", rw="read")
def find_rebuild_warranty_claims(ctx: ToolContext, warranty_claim_id: str = "", rebuild_contract_id: str = "", customer_id: str = "", source_warranty_claim_id: str = "") -> str:
    """Look up workmanship warranty reports and inspections.

    Each record shows defect category, report and inspection dates and the inspection finding. Search by any reference number already in hand; every
    criterion is optional and several may be combined. All matching records are returned, or a
    short notice when nothing matches.

    Args:
        warranty_claim_id: Reference number - the reference number of a warranty report or warranty inspection; leave "" if unknown.
        rebuild_contract_id: Reference number - the reconstruction contract reference number; leave "" if unknown.
        customer_id: Reference number - the customer reference number; leave "" if unknown.
        source_warranty_claim_id: Reference number - the reference number of the warranty report an inspection answers; leave "" if unknown.
    """
    match = {k: v for k, v in {"warranty_claim_id": warranty_claim_id, "rebuild_contract_id": rebuild_contract_id, "customer_id": customer_id, "source_warranty_claim_id": source_warranty_claim_id}.items() if v}
    rows = ctx.find("rebuild_warranty_claims", **match)
    return str(rows) if rows else f"No workmanship warranty reports and inspections found for {match}."


@tool(owner="agent", rw="read")
def find_rebuild_change_orders(ctx: ToolContext, change_order_id: str = "", rebuild_contract_id: str = "", customer_id: str = "", claim_request_id: str = "") -> str:
    """Look up change order proposals on reconstruction contracts.

    Each record shows number, type, priced line, quantity, unit price, linked supplement, amount, signature status and when it was written. Search by any reference number already in hand; every
    criterion is optional and several may be combined. All matching records are returned, or a
    short notice when nothing matches.

    Args:
        change_order_id: Reference number - the change order reference number; leave "" if unknown.
        rebuild_contract_id: Reference number - the reconstruction contract reference number; leave "" if unknown.
        customer_id: Reference number - the customer reference number; leave "" if unknown.
        claim_request_id: Reference number - the reference number of a supplement, endorsement, depreciation release or storage extension request; leave "" if unknown.
    """
    match = {k: v for k, v in {"change_order_id": change_order_id, "rebuild_contract_id": rebuild_contract_id, "customer_id": customer_id, "claim_request_id": claim_request_id}.items() if v}
    rows = ctx.find("rebuild_change_orders", **match)
    return str(rows) if rows else f"No change order proposals on reconstruction contracts found for {match}."


@tool(owner="agent", rw="read")
def find_contents_jobs(ctx: ToolContext, contents_job_id: str = "", customer_id: str = "", claim_file_id: str = "", mitigation_job_id: str = "") -> str:
    """Look up contents packout, cleaning and storage jobs.

    Each record shows tier, status, address, linked claim file and mitigation job, funding source, custody start, boxes and vaults, declared value, return dates, invoice amount and current balance. Search by any reference number already in hand; every
    criterion is optional and several may be combined. All matching records are returned, or a
    short notice when nothing matches.

    Args:
        contents_job_id: Reference number - the contents job reference number; leave "" if unknown.
        customer_id: Reference number - the customer reference number; leave "" if unknown.
        claim_file_id: Reference number - the claim file reference number; leave "" if unknown.
        mitigation_job_id: Reference number - the reference number of the water, fire or mold job that preceded the work at the same loss; leave "" if unknown.
    """
    match = {k: v for k, v in {"contents_job_id": contents_job_id, "customer_id": customer_id, "claim_file_id": claim_file_id, "mitigation_job_id": mitigation_job_id}.items() if v}
    rows = ctx.find("contents_jobs", **match)
    return str(rows) if rows else f"No contents packout, cleaning and storage jobs found for {match}."


@tool(owner="agent", rw="read")
def find_contents_charges(ctx: ToolContext, contents_charge_id: str = "", contents_job_id: str = "", customer_id: str = "", source_payment_id: str = "") -> str:
    """Look up charge lines on contents jobs.

    Each record shows packing, storage periods and who they are billed to, cleaning, pack-back, late fees and card surcharges, each with its date or period, quantity, rate and amount. Search by any reference number already in hand; every
    criterion is optional and several may be combined. All matching records are returned, or a
    short notice when nothing matches.

    Args:
        contents_charge_id: Reference number - the reference number of a contents job charge line; leave "" if unknown.
        contents_job_id: Reference number - the contents job reference number; leave "" if unknown.
        customer_id: Reference number - the customer reference number; leave "" if unknown.
        source_payment_id: Reference number - the reference number of the payment a refund or surcharge relates to; leave "" if unknown.
    """
    match = {k: v for k, v in {"contents_charge_id": contents_charge_id, "contents_job_id": contents_job_id, "customer_id": customer_id, "source_payment_id": source_payment_id}.items() if v}
    rows = ctx.find("contents_charges", **match)
    return str(rows) if rows else f"No charge lines on contents jobs found for {match}."


@tool(owner="agent", rw="read")
def find_contents_payments(ctx: ToolContext, contents_payment_id: str = "", contents_job_id: str = "", customer_id: str = "", claim_payment_id: str = "", source_charge_id: str = "", source_payment_id: str = "") -> str:
    """Look up payments, insurance postings, credits, custody compensation and refunds on contents jobs.

    Each record shows tender, reference numbers, the carrier payment, charge line or inventory tag each one relates to, posting date and amount. Search by any reference number already in hand; every
    criterion is optional and several may be combined. All matching records are returned, or a
    short notice when nothing matches.

    Args:
        contents_payment_id: Reference number - the reference number of a contents job payment, insurance posting, credit or refund line; leave "" if unknown.
        contents_job_id: Reference number - the contents job reference number; leave "" if unknown.
        customer_id: Reference number - the customer reference number; leave "" if unknown.
        claim_payment_id: Reference number - the reference number of a carrier payment; leave "" if unknown.
        source_charge_id: Reference number - the reference number of the charge line a credit corrects; leave "" if unknown.
        source_payment_id: Reference number - the reference number of the payment a refund or surcharge relates to; leave "" if unknown.
    """
    match = {k: v for k, v in {"contents_payment_id": contents_payment_id, "contents_job_id": contents_job_id, "customer_id": customer_id, "claim_payment_id": claim_payment_id, "source_charge_id": source_charge_id, "source_payment_id": source_payment_id}.items() if v}
    rows = ctx.find("contents_payments", **match)
    return str(rows) if rows else f"No payments, insurance postings, credits, custody compensation and refunds on contents jobs found for {match}."


@tool(owner="agent", rw="read")
def find_contents_disposal_authorizations(ctx: ToolContext, disposal_auth_id: str = "", contents_job_id: str = "", customer_id: str = "") -> str:
    """Look up disposal authorizations for non-salvageable contents.

    Each record shows the number of items listed, signature status and when the list was presented. Search by any reference number already in hand; every
    criterion is optional and several may be combined. All matching records are returned, or a
    short notice when nothing matches.

    Args:
        disposal_auth_id: Reference number - the reference number of a disposal authorization; leave "" if unknown.
        contents_job_id: Reference number - the contents job reference number; leave "" if unknown.
        customer_id: Reference number - the customer reference number; leave "" if unknown.
    """
    match = {k: v for k, v in {"disposal_auth_id": disposal_auth_id, "contents_job_id": contents_job_id, "customer_id": customer_id}.items() if v}
    rows = ctx.find("contents_disposal_authorizations", **match)
    return str(rows) if rows else f"No disposal authorizations for non-salvageable contents found for {match}."


@tool(owner="agent", rw="read")
def find_claims_files(ctx: ToolContext, claim_file_id: str = "", customer_id: str = "") -> str:
    """Look up insurance claim files.

    Each record shows billing arrangement, status, carrier and claim number, policy state and issue date, peril, loss and key dates, deductible, mold and ordinance or law limits, mortgagee, public adjuster, program referral, estimate, approved storage end date, carrier receivable and deductible still due. Search by any reference number already in hand; every
    criterion is optional and several may be combined. All matching records are returned, or a
    short notice when nothing matches.

    Args:
        claim_file_id: Reference number - the claim file reference number; leave "" if unknown.
        customer_id: Reference number - the customer reference number; leave "" if unknown.
    """
    match = {k: v for k, v in {"claim_file_id": claim_file_id, "customer_id": customer_id}.items() if v}
    rows = ctx.find("claims_files", **match)
    return str(rows) if rows else f"No insurance claim files found for {match}."


@tool(owner="agent", rw="read")
def find_claims_approvals(ctx: ToolContext, claim_approval_id: str = "", claim_file_id: str = "", customer_id: str = "", claim_request_id: str = "", source_approval_id: str = "") -> str:
    """Look up carrier approvals and write-offs on claim files.

    Each record shows approval type, the supplement decided, coverage, depreciation withheld, write-off reason, date and amount. Search by any reference number already in hand; every
    criterion is optional and several may be combined. All matching records are returned, or a
    short notice when nothing matches.

    Args:
        claim_approval_id: Reference number - the reference number of a carrier approval or write-off line; leave "" if unknown.
        claim_file_id: Reference number - the claim file reference number; leave "" if unknown.
        customer_id: Reference number - the customer reference number; leave "" if unknown.
        claim_request_id: Reference number - the reference number of a supplement, endorsement, depreciation release or storage extension request; leave "" if unknown.
        source_approval_id: Reference number - the reference number of the carrier approval line a write-off reduces; leave "" if unknown.
    """
    match = {k: v for k, v in {"claim_approval_id": claim_approval_id, "claim_file_id": claim_file_id, "customer_id": customer_id, "claim_request_id": claim_request_id, "source_approval_id": source_approval_id}.items() if v}
    rows = ctx.find("claims_approvals", **match)
    return str(rows) if rows else f"No carrier approvals and write-offs on claim files found for {match}."


@tool(owner="agent", rw="read")
def find_claims_payments(ctx: ToolContext, claim_payment_id: str = "", claim_file_id: str = "", customer_id: str = "") -> str:
    """Look up carrier payments on claim files.

    Each record shows payment type, coverage, how the payment was routed, check number, date received and amount. Search by any reference number already in hand; every
    criterion is optional and several may be combined. All matching records are returned, or a
    short notice when nothing matches.

    Args:
        claim_payment_id: Reference number - the reference number of a carrier payment; leave "" if unknown.
        claim_file_id: Reference number - the claim file reference number; leave "" if unknown.
        customer_id: Reference number - the customer reference number; leave "" if unknown.
    """
    match = {k: v for k, v in {"claim_payment_id": claim_payment_id, "claim_file_id": claim_file_id, "customer_id": customer_id}.items() if v}
    rows = ctx.find("claims_payments", **match)
    return str(rows) if rows else f"No carrier payments on claim files found for {match}."


@tool(owner="agent", rw="read")
def find_claims_deductibles(ctx: ToolContext, claim_deductible_id: str = "", claim_file_id: str = "", customer_id: str = "") -> str:
    """Look up deductible assessments and payments on claim files.

    Each record shows tender, reference number, installment number, date and amount. Search by any reference number already in hand; every
    criterion is optional and several may be combined. All matching records are returned, or a
    short notice when nothing matches.

    Args:
        claim_deductible_id: Reference number - the reference number of a deductible assessment or payment line; leave "" if unknown.
        claim_file_id: Reference number - the claim file reference number; leave "" if unknown.
        customer_id: Reference number - the customer reference number; leave "" if unknown.
    """
    match = {k: v for k, v in {"claim_deductible_id": claim_deductible_id, "claim_file_id": claim_file_id, "customer_id": customer_id}.items() if v}
    rows = ctx.find("claims_deductibles", **match)
    return str(rows) if rows else f"No deductible assessments and payments on claim files found for {match}."


@tool(owner="agent", rw="read")
def find_claims_requests(ctx: ToolContext, claim_request_id: str = "", claim_file_id: str = "", customer_id: str = "", related_job_id: str = "", claim_payment_id: str = "") -> str:
    """Look up requests submitted on claim files.

    Each record shows supplements with their number, reason, coverage and amount, check endorsements, depreciation release requests and storage extension requests, with the related job and dates. Search by any reference number already in hand; every
    criterion is optional and several may be combined. All matching records are returned, or a
    short notice when nothing matches.

    Args:
        claim_request_id: Reference number - the reference number of a supplement, endorsement, depreciation release or storage extension request; leave "" if unknown.
        claim_file_id: Reference number - the claim file reference number; leave "" if unknown.
        customer_id: Reference number - the customer reference number; leave "" if unknown.
        related_job_id: Reference number - the reference number of the job a request or credit concerns; leave "" if unknown.
        claim_payment_id: Reference number - the reference number of a carrier payment; leave "" if unknown.
    """
    match = {k: v for k, v in {"claim_request_id": claim_request_id, "claim_file_id": claim_file_id, "customer_id": customer_id, "related_job_id": related_job_id, "claim_payment_id": claim_payment_id}.items() if v}
    rows = ctx.find("claims_requests", **match)
    return str(rows) if rows else f"No requests submitted on claim files found for {match}."


@tool(owner="agent", rw="read")
def find_account_agreements(ctx: ToolContext, agreement_id: str = "", customer_id: str = "") -> str:
    """Look up commercial and property manager service agreements.

    Each record shows tier, status, term dates, renewal election, number of covered properties, key dates and current balance. Search by any reference number already in hand; every
    criterion is optional and several may be combined. All matching records are returned, or a
    short notice when nothing matches.

    Args:
        agreement_id: Reference number - the service agreement reference number; leave "" if unknown.
        customer_id: Reference number - the customer reference number; leave "" if unknown.
    """
    match = {k: v for k, v in {"agreement_id": agreement_id, "customer_id": customer_id}.items() if v}
    rows = ctx.find("account_agreements", **match)
    return str(rows) if rows else f"No commercial and property manager service agreements found for {match}."


@tool(owner="agent", rw="read")
def find_account_charges(ctx: ToolContext, account_charge_id: str = "", agreement_id: str = "", customer_id: str = "", source_payment_id: str = "") -> str:
    """Look up charges on service agreements.

    Each record shows term fees, site fees, surveys, training, reinstatement, termination, late fees and card surcharges with their term, dates, quantity and amount. Search by any reference number already in hand; every
    criterion is optional and several may be combined. All matching records are returned, or a
    short notice when nothing matches.

    Args:
        account_charge_id: Reference number - the reference number of a service agreement charge; leave "" if unknown.
        agreement_id: Reference number - the service agreement reference number; leave "" if unknown.
        customer_id: Reference number - the customer reference number; leave "" if unknown.
        source_payment_id: Reference number - the reference number of the payment a refund or surcharge relates to; leave "" if unknown.
    """
    match = {k: v for k, v in {"account_charge_id": account_charge_id, "agreement_id": agreement_id, "customer_id": customer_id, "source_payment_id": source_payment_id}.items() if v}
    rows = ctx.find("account_charges", **match)
    return str(rows) if rows else f"No charges on service agreements found for {match}."


@tool(owner="agent", rw="read")
def find_account_payments(ctx: ToolContext, account_payment_id: str = "", agreement_id: str = "", customer_id: str = "", related_job_id: str = "", source_payment_id: str = "") -> str:
    """Look up payments, credits and refunds on service agreements.

    Each record shows tender, reference numbers, the job an SLA credit concerns, the term a rebate or proration belongs to, date and amount. Search by any reference number already in hand; every
    criterion is optional and several may be combined. All matching records are returned, or a
    short notice when nothing matches.

    Args:
        account_payment_id: Reference number - the reference number of a service agreement payment, credit or refund line; leave "" if unknown.
        agreement_id: Reference number - the service agreement reference number; leave "" if unknown.
        customer_id: Reference number - the customer reference number; leave "" if unknown.
        related_job_id: Reference number - the reference number of the job a request or credit concerns; leave "" if unknown.
        source_payment_id: Reference number - the reference number of the payment a refund or surcharge relates to; leave "" if unknown.
    """
    match = {k: v for k, v in {"account_payment_id": account_payment_id, "agreement_id": agreement_id, "customer_id": customer_id, "related_job_id": related_job_id, "source_payment_id": source_payment_id}.items() if v}
    rows = ctx.find("account_payments", **match)
    return str(rows) if rows else f"No payments, credits and refunds on service agreements found for {match}."


@tool(owner="agent", rw="read")
def find_account_referrals(ctx: ToolContext, account_referral_id: str = "", agreement_id: str = "", customer_id: str = "") -> str:
    """Look up carrier referrals under preferred vendor agreements.

    Each record shows referral number, date, loss type and whether the contact commitment was met. Search by any reference number already in hand; every
    criterion is optional and several may be combined. All matching records are returned, or a
    short notice when nothing matches.

    Args:
        account_referral_id: Reference number - the reference number of a carrier referral; leave "" if unknown.
        agreement_id: Reference number - the service agreement reference number; leave "" if unknown.
        customer_id: Reference number - the customer reference number; leave "" if unknown.
    """
    match = {k: v for k, v in {"account_referral_id": account_referral_id, "agreement_id": agreement_id, "customer_id": customer_id}.items() if v}
    rows = ctx.find("account_referrals", **match)
    return str(rows) if rows else f"No carrier referrals under preferred vendor agreements found for {match}."


@tool(owner="agent", rw="read")
def find_customers(ctx: ToolContext, customer_id: str = "", name: str = "", phone: str = "", email: str = "", billing_zip: str = "") -> str:
    """Look up a customer profile to establish whose account this call is about.

    Search by the customer reference number, or by what the caller can naturally state: the name
    on the profile (a person's full name or the registered business or association name), the
    registered phone number, the registered email address or the billing ZIP code. Every criterion
    is optional; supply whichever are known. The profile shows the customer type, the contact
    person for an organization, contact details, billing address and the date the profile was
    opened. Finding a profile does not verify the caller's identity.

    Args:
        customer_id: Reference number - the customer reference number; leave "" if unknown.
        name: The name on the profile as the caller states it; leave "" if not provided.
        phone: The registered phone number, 10 digits; leave "" if not provided.
        email: The registered email address; leave "" if not provided.
        billing_zip: The 5-digit ZIP code of the billing address; leave "" if not provided.
    """
    match = {k: v for k, v in {"customer_id": customer_id, "name": name, "phone": phone,
                               "email": email, "billing_zip": billing_zip}.items() if v}
    if not match:
        return "Error: provide at least one reference number or profile detail to find the customer."
    rows = ctx.fuzzy_find("customers", **match)
    if not rows:
        return f"No customer matches {match}."
    if len(rows) > 1:
        return f"Error: {len(rows)} customers match {match}; ask for one more detail to tell them apart."
    return str(rows[0])


@tool(owner="agent", rw="write")
def verify_customer_identity(ctx: ToolContext, customer_id: str, phone: str = "", email: str = "", billing_zip: str = "") -> str:
    """Verify the caller's identity and record the outcome.

    Identity must be verified before any account details are discussed or any business is done
    on the customer's jobs, contracts, claim files or agreements. This tool performs the check
    itself: it compares each detail the caller states with the customer profile, counts the
    matches, and passes only when at least 2 of them match. The customer reference number only
    tells the tool which profile to compare against and never counts as a match. Callers often
    know only some details, so pass exactly what the caller said and leave the rest blank. The
    outcome is recorded; if an earlier attempt failed and a later attempt passes, the pass stands.

    Args:
        customer_id: Reference number - the customer reference number read from the customer profile lookup; required.
        phone: The registered phone number as the caller states it, 10 digits; leave "" if not stated.
        email: The registered email address as the caller states it; leave "" if not stated.
        billing_zip: The 5-digit billing ZIP code as the caller states it; leave "" if not stated.
    """
    if not customer_id:
        return "Error: customer_id is required; look the customer up first and pass their reference number."
    rows = ctx.find("customers", customer_id=customer_id)
    if not rows:
        return f"Error: no customer {customer_id}; cannot verify."
    rec = rows[0]
    supplied = {"phone": phone, "email": email, "billing_zip": billing_zip}
    matched = sum(1 for field, value in supplied.items() if value and str(rec.get(field, "")).strip().casefold() == str(value).strip().casefold())
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
            else f"Identity NOT verified for {customer_id} (only {matched} of the required 2 details matched). Ask the caller for another detail on file and try again.")


@tool(owner="agent", rw="write")
def transfer_to_human_agent(ctx: ToolContext, customer_id: str, reason: str) -> str:
    """Hand the customer over to a human representative and record the handoff with its reason.

    Use it when no company policy allows the request to be resolved here, or when the customer
    has explicitly asked for a human representative 2 times.

    Args:
        customer_id: Reference number - the customer reference number read from the customer profile lookup.
        reason: One of exactly two values, never free text. POLICY_NOT_COVERED - no company policy allows the request to be resolved; CUSTOMER_REQUESTED - the customer has explicitly asked for a human representative at least 2 times.
    """
    allowed = {"POLICY_NOT_COVERED", "CUSTOMER_REQUESTED"}
    if reason not in allowed:
        return f"Error: unknown handoff reason '{reason}'. Valid: {', '.join(sorted(allowed))}."
    if not ctx.find("customers", customer_id=customer_id):
        return f"Error: no customer {customer_id}; cannot record the handoff."
    rid = ctx.make_id("hof_", customer_id, reason)
    ctx.create("handoff_log", rid, handoff_id=rid, customer_id=customer_id, reason=reason, created_at=ctx.now())
    return f"Handoff to a human representative recorded for {customer_id} ({reason})."

"""Atomic storage accounting actions."""
from erlbench import ToolContext, tool

@tool(owner="agent", rw="write")
def record_capacity_entitlement_88579e54(ctx: ToolContext, storage_event_id: str, quantity: float) -> str:
    """Record a quantified shared-capacity entitlement for one storage source charge. The agent completes the selected entitlement with its GB-month quantity; the completed entitlement is visible immediately and the receipt confirms success.

    Args:
        storage_event_id: Id class — Identifier of the Storage entitlement reference copied from find_storage_events.
        quantity: Fixed-format class — Unit GB-month; schema format Decimal quantity to six decimal places. Entitled GB-month quantity as a decimal number with six decimal places; round half-up before submission, stored at six decimal places; empty is not allowed.

    Returns:
        A string reading Entitlement completed with the storage entitlement reference and recorded GB-month quantity; completed confirms the entitlement is available.
    """
    ctx.update("storage_events", storage_event_id, quantity=round(float(quantity), 6), status="completed")
    return f"Entitlement completed {storage_event_id}: {quantity:.6f} GB-month."

@tool(owner="agent", rw="write")
def record_storage_correction_review_dc2a1af3(ctx: ToolContext, storage_event_id: str, source_event_id: str, related_event_id: str, storage_holding_id: str, net_amount: float) -> str:
    """Complete an accountant's billing review of one storage charge using its authoritative source evidence. The selected review records its corrected net target, zero tax, an incorrect decision and approved status; the approved target becomes visible immediately on success.

    Args:
        storage_event_id: Id class — Identifier of the Billing review reference copied from find_storage_events.
        source_event_id: Id class — Identifier of the Original storage charge reference copied from the selected review returned by find_storage_events.
        related_event_id: Id class — Identifier of the Supporting storage export reference copied from the selected review returned by find_storage_events.
        storage_holding_id: Id class — Identifier of the Storage contract reference copied from find_storage_holdings.
        net_amount: Fixed-format class — Unit USD; format USD to two decimals. Corrected net target in USD, decimal format with two decimal places, half-up rounded before submission and stored at two decimals; empty is not allowed.

    Returns:
        A string reading Review approved with the billing review reference and corrected USD net target; approved confirms the review is completed.
    """
    ctx.update("storage_events", storage_event_id, source_event_id=source_event_id, related_event_id=related_event_id, storage_holding_id=storage_holding_id, net_amount=round(float(net_amount),2), tax_amount=0.0, decision="incorrect", status="approved")
    return f"Review approved {storage_event_id}: USD {net_amount:.2f} net."

@tool(owner="agent", rw="write")
def post_storage_correction_02018d1e(ctx: ToolContext, storage_event_id: str, storage_holding_id: str, source_event_id: str, related_event_id: str, customer_id: str, amount: float) -> str:
    """Post one signed correction credit against a storage source charge. The agent records an immediately visible receivable reduction with its original charge and approved review references, and the posted receipt confirms success.

    Args:
        storage_event_id: Id class — Identifier of the Approved billing review reference copied from find_storage_events or a completed review receipt.
        storage_holding_id: Id class — Identifier of the Storage contract reference copied from find_storage_holdings.
        source_event_id: Id class — Identifier of the Original storage charge reference copied from find_storage_events.
        related_event_id: Id class — Identifier of the Approved billing review reference copied from find_storage_events or the review completion receipt.
        customer_id: Id class — Identifier of the Enterprise profile reference copied from find_customers.
        amount: Fixed-format class — Unit USD; format USD to two decimals. Signed receivable reduction in USD, decimal number with two decimal places, half-up rounded before submission and stored at two decimals; empty is not allowed.

    Returns:
        A string reading Correction posted with the correction event reference and signed USD amount; posted confirms the receivable reduction is recorded.
    """
    rid=ctx.make_id("storage_correction",storage_event_id,storage_holding_id,source_event_id,related_event_id,customer_id,amount)
    ctx.create("storage_events",rid,storage_event_id=rid,storage_holding_id=storage_holding_id,source_event_id=source_event_id,related_event_id=related_event_id,customer_id=customer_id,event_type="storage_credit",source_subtype="correction",status="posted",amount=round(float(amount),2),net_amount=round(float(amount),2),tax_amount=0.0,occurred_at=ctx.now())
    return f"Correction posted {rid}: USD {amount:.2f}."


@tool(owner="user", rw="write")
def file_storage_outage_claim_6a92fd5d(ctx: ToolContext, storage_event_id: str, request_id: str, credited_amount: float) -> str:
    """The customer files one storage outage claim for the selected invoice. The claim becomes posted with the exact claimed USD amount and both notice and occurrence set to the current filing time; the receipt confirms submitted customer intent, without granting a system approval.

    Args:
        storage_event_id: Id class — Identifier of the selected storage evidence or assessment copied from find_storage_events, find_storage_holdings, find_customers or the corresponding completed action receipt.
        request_id: Id class — Identifier of the customer claim or refund authorization copied from find_storage_events, find_storage_holdings, find_customers or the corresponding completed action receipt.
        credited_amount: Fixed-format class — Unit USD; format USD to two decimals. Nonnegative claim or authorization amount as a decimal number, rounded half-up before submission and stored to two decimal places; empty is not allowed.

    Returns:
        A string reading Recorded with the storage business record identifier and the USD amount; Recorded confirms that the stated action completed successfully.
    """
    ctx.update("storage_events", request_id, request_id=request_id, credited_amount=round(float(credited_amount),2), status="posted", notice_at=ctx.now(), occurred_at=ctx.now())
    return f"Recorded {request_id}: USD {credited_amount:.2f}."


@tool(owner="agent", rw="write")
def assess_storage_outage_30bc4acc(ctx: ToolContext, storage_event_id: str, source_event_id: str, related_event_id: str, storage_holding_id: str, request_id: str, credited_amount: float) -> str:
    """The accountant completes one storage outage assessment against the existing incident report. The assessment becomes approved and eligible with its nonnegative USD concession; the approved receipt confirms assessment completion.

    Args:
        storage_event_id: Id class — Identifier of the selected storage evidence or assessment copied from find_storage_events, find_storage_holdings, find_customers or the corresponding completed action receipt.
        source_event_id: Id class — Identifier of the original invoice or completed payment copied from find_storage_events, find_storage_holdings, find_customers or the corresponding completed action receipt.
        related_event_id: Id class — Identifier of the linked incident, assessment or concession copied from find_storage_events, find_storage_holdings, find_customers or the corresponding completed action receipt.
        storage_holding_id: Id class — Identifier of the storage contract copied from find_storage_events, find_storage_holdings, find_customers or the corresponding completed action receipt.
        request_id: Id class — Identifier of the customer claim or refund authorization copied from find_storage_events, find_storage_holdings, find_customers or the corresponding completed action receipt.
        credited_amount: Fixed-format class — Unit USD; format USD to two decimals. Nonnegative claim or authorization amount as a decimal number, rounded half-up before submission and stored to two decimal places; empty is not allowed.

    Returns:
        A string reading Recorded with the storage business record identifier and the USD amount; Recorded confirms that the stated action completed successfully.
    """
    ctx.update("storage_events", storage_event_id, request_id=request_id, source_event_id=source_event_id, related_event_id=related_event_id, storage_holding_id=storage_holding_id, credited_amount=round(float(credited_amount),2), status="approved", decision="eligible")
    return f"Recorded {storage_event_id}: USD {credited_amount:.2f}."


@tool(owner="agent", rw="write")
def post_storage_service_concession_cfd2170f(ctx: ToolContext, storage_event_id: str, storage_holding_id: str, source_event_id: str, related_event_id: str, request_id: str, customer_id: str, amount: float) -> str:
    """Post one storage service concession against an original invoice. The agent records an immediately visible signed receivable reduction with the source invoice and approved assessment; the posted receipt confirms the financial credit.

    Args:
        storage_event_id: Id class — Identifier of the selected storage evidence or assessment copied from find_storage_events, find_storage_holdings, find_customers or the corresponding completed action receipt.
        storage_holding_id: Id class — Identifier of the storage contract copied from find_storage_events, find_storage_holdings, find_customers or the corresponding completed action receipt.
        source_event_id: Id class — Identifier of the original invoice or completed payment copied from find_storage_events, find_storage_holdings, find_customers or the corresponding completed action receipt.
        related_event_id: Id class — Identifier of the linked incident, assessment or concession copied from find_storage_events, find_storage_holdings, find_customers or the corresponding completed action receipt.
        request_id: Id class — Identifier of the customer claim or refund authorization copied from find_storage_events, find_storage_holdings, find_customers or the corresponding completed action receipt.
        customer_id: Id class — Identifier of the enterprise customer profile copied from find_storage_events, find_storage_holdings, find_customers or the corresponding completed action receipt.
        amount: Fixed-format class — Unit USD; format USD to two decimals. Signed financial receivable delta as a decimal number, rounded half-up before submission and stored to two decimal places; empty is not allowed.

    Returns:
        A string reading Recorded with the storage business record identifier and the USD amount; Recorded confirms that the stated action completed successfully.
    """
    rid=ctx.make_id("storage_credit", storage_event_id, storage_holding_id, source_event_id, related_event_id, request_id, customer_id, amount)
    ctx.create("storage_events",rid,storage_event_id=rid,storage_holding_id=storage_holding_id,source_event_id=source_event_id,request_id=request_id,customer_id=customer_id,event_type="storage_credit",source_subtype="service_credit",status="posted",amount=round(float(amount),2),occurred_at=ctx.now(), related_event_id=related_event_id, net_amount=round(float(amount),2), tax_amount=0.0)
    return f"Recorded {rid}: USD {amount:.2f}."


@tool(owner="user", rw="write")
def authorize_storage_refund_9b3e6afe(ctx: ToolContext, storage_event_id: str, request_id: str, source_event_id: str, related_event_id: str, storage_holding_id: str, credited_amount: float) -> str:
    """The customer authorizes one exact storage refund to its recorded original-payment destination. The selected refund authorization becomes posted with its consented cash amount and both notice and occurrence set to the current filing time; the receipt confirms customer consent is recorded without granting a system approval.

    Args:
        storage_event_id: Id class — Identifier of the refund authorization being updated, copied from storage_event_id of the selected refund request returned by find_storage_events; this is the same identifier supplied as request_id.
        request_id: Id class — Identifier recorded as this refund authorization's own request reference, copied from storage_event_id of the selected refund request returned by find_storage_events; this is the same identifier supplied as storage_event_id.
        source_event_id: Id class — Identifier of the original completed payment, copied from source_event_id of the selected refund request returned by find_storage_events.
        related_event_id: Id class — Identifier of the current posted service concession, copied from its actual posting receipt.
        storage_holding_id: Id class — Identifier of the storage contract copied from find_storage_events, find_storage_holdings, find_customers or the corresponding completed action receipt.
        credited_amount: Fixed-format class — Unit USD; format USD to two decimals. Nonnegative claim or authorization amount as a decimal number, rounded half-up before submission and stored to two decimal places; empty is not allowed.

    Returns:
        A string reading Recorded with the storage business record identifier and the USD amount; Recorded confirms that the stated action completed successfully.
    """
    ctx.update("storage_events", storage_event_id, request_id=request_id, source_event_id=source_event_id, related_event_id=related_event_id, storage_holding_id=storage_holding_id, credited_amount=round(float(credited_amount),2), status="posted", notice_at=ctx.now(), occurred_at=ctx.now())
    return f"Recorded {request_id}: USD {credited_amount:.2f}."


@tool(owner="agent", rw="write")
def refund_storage_overpayment_1b2c5ab5(ctx: ToolContext, storage_event_id: str, storage_holding_id: str, source_event_id: str, request_id: str, customer_id: str, amount: float) -> str:
    """Pay one authorized storage overpayment refund through the original ACH payment destination. The agent records an immediate positive receivable delta for cash returned; the posted receipt confirms the payout is complete.

    Args:
        storage_event_id: Id class — Identifier of the selected storage evidence or assessment copied from find_storage_events, find_storage_holdings, find_customers or the corresponding completed action receipt.
        storage_holding_id: Id class — Identifier of the storage contract copied from find_storage_events, find_storage_holdings, find_customers or the corresponding completed action receipt.
        source_event_id: Id class — Identifier of the original invoice or completed payment copied from find_storage_events, find_storage_holdings, find_customers or the corresponding completed action receipt.
        request_id: Id class — Identifier of the customer claim or refund authorization copied from find_storage_events, find_storage_holdings, find_customers or the corresponding completed action receipt.
        customer_id: Id class — Identifier of the enterprise customer profile copied from find_storage_events, find_storage_holdings, find_customers or the corresponding completed action receipt.
        amount: Fixed-format class — Unit USD; format USD to two decimals. Signed financial receivable delta as a decimal number, rounded half-up before submission and stored to two decimal places; empty is not allowed.

    Returns:
        A string reading Recorded with the storage business record identifier and the USD amount; Recorded confirms that the stated action completed successfully.
    """
    rid=ctx.make_id("storage_refund", storage_event_id, storage_holding_id, source_event_id, request_id, customer_id, amount)
    ctx.create("storage_events",rid,storage_event_id=rid,storage_holding_id=storage_holding_id,source_event_id=source_event_id,request_id=request_id,customer_id=customer_id,event_type="storage_refund",source_subtype="refund",status="posted",amount=round(float(amount),2),occurred_at=ctx.now(), method="ach")
    return f"Recorded {rid}: USD {amount:.2f}."

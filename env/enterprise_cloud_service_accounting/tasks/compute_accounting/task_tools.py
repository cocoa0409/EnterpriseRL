"""Atomic compute accounting actions."""
from erlbench import ToolContext, tool

@tool(owner="agent", rw="write")
def review_compute_line_e30849b6(ctx: ToolContext, compute_holding_id: str, customer_id: str, compute_event_id: str, source_event_id: str, related_event_id: str, net_amount: float) -> str:
    """Record an accountant arithmetic review for one primary invoice line against its provider export. The review records the corrected pretax amount and an incorrect decision; a successful receipt identifies the official completed review without moving money.

    Args:
        compute_holding_id: Id class — Identifier of the compute contract, copied from find_compute_events, find_compute_holdings or find_customers results, or the preceding successful consent receipt as applicable.
        customer_id: Id class — Identifier of the customer profile, copied from find_compute_events, find_compute_holdings or find_customers results, or the preceding successful consent receipt as applicable.
        compute_event_id: Id class — Identifier of the source-correlated evidence packet returned by find_compute_events: the compute service record with source_subtype review, source_event_id equal to the original primary charge, and related_event_id equal to that charge's provider export reference.
        source_event_id: Id class — Identifier of the original invoice line or payment being handled, copied from find_compute_events, find_compute_holdings or find_customers results, or the preceding successful consent receipt as applicable.
        related_event_id: Id class — Identifier of the related export or approved review, copied from find_compute_events, find_compute_holdings or find_customers results, or the preceding successful consent receipt as applicable.
        net_amount: Fixed-format class — The corrected pretax amount in units of USD to two decimals, supplied as a decimal number already rounded half-up to two decimal places at calculation completion; stored to two decimals, with no empty value.

    Returns:
        A string receipt saying "Recorded compute_review" followed by compute_event_id, the new internal event reference as a string. That receipt confirms successful approved registration and the business effect described above.
    """
    rid = ctx.make_id("review_compute_line", compute_holding_id, customer_id, compute_event_id, source_event_id, related_event_id, net_amount)
    ctx.create("compute_events", rid, compute_event_id=rid, compute_holding_id=compute_holding_id, customer_id=customer_id, source_event_id=source_event_id, related_event_id=related_event_id, external_reference='review_compute_line', event_type="compute_review", status="approved", occurred_at=ctx.now(), decision='incorrect', credited_amount=0.0, request_id='', source_subtype='correction', net_amount=round(float(net_amount),2), tax_amount=0.0)
    return f"Recorded compute_review {rid}."

@tool(owner="agent", rw="write")
def credit_compute_line_adb33dcc(ctx: ToolContext, compute_holding_id: str, customer_id: str, compute_event_id: str, source_event_id: str, related_event_id: str, amount: float) -> str:
    """Post a negative correction to one original primary invoice line. This decreases the contract receivable by the supplied amount and records the same untaxed net component; the returned reference identifies the posted credit.

    Args:
        compute_holding_id: Id class — Identifier of the compute contract, copied from find_compute_events, find_compute_holdings or find_customers results, or the preceding successful consent receipt as applicable.
        customer_id: Id class — Identifier of the customer profile, copied from find_compute_events, find_compute_holdings or find_customers results, or the preceding successful consent receipt as applicable.
        compute_event_id: Id class — Identifier of the approved incorrect arithmetic review for the original primary charge, copied from its successful review receipt or find_compute_events; use the identical review reference supplied in related_event_id.
        source_event_id: Id class — Identifier of the original invoice line or payment being handled, copied from find_compute_events, find_compute_holdings or find_customers results, or the preceding successful consent receipt as applicable.
        related_event_id: Id class — Identifier of the related export or approved review, copied from find_compute_events, find_compute_holdings or find_customers results, or the preceding successful consent receipt as applicable.
        amount: Fixed-format class — The signed financial amount in units of USD to two decimals, supplied as a decimal number already rounded half-up to two decimal places at calculation completion; stored to two decimals, with no empty value.

    Returns:
        A string receipt saying "Recorded compute_credit" followed by compute_event_id, the new internal event reference as a string. That receipt confirms successful posted registration and the business effect described above.
    """
    rid = ctx.make_id("credit_compute_line", compute_holding_id, customer_id, compute_event_id, source_event_id, related_event_id, amount)
    ctx.create("compute_events", rid, compute_event_id=rid, compute_holding_id=compute_holding_id, customer_id=customer_id, source_event_id=source_event_id, related_event_id=related_event_id, external_reference='credit_compute_line', event_type="compute_credit", status="posted", occurred_at=ctx.now(), source_subtype='correction', amount=round(float(amount),2), net_amount=round(float(amount),2), tax_amount=0.0, meter_code='primary', currency='USD')
    return f"Recorded compute_credit {rid}."

@tool(owner="agent", rw="write")
def authorize_compute_refund_4fb241f0(ctx: ToolContext, compute_holding_id: str, customer_id: str, compute_event_id: str, source_event_id: str, related_event_id: str, request_id: str, correction_event_id: str, credited_amount: float) -> str:
    """Record the accountant's numerical refund assessment for an existing customer request and original payment. This creates an approved eligible review containing the permitted immediate amount, linked to the posted correction; it moves no funds and does not replace the customer's consent. Its receipt identifies the completed assessment.

    Args:
        compute_holding_id: Id class — Identifier of the compute contract copied from find_compute_holdings or find_compute_events.
        customer_id: Id class — Identifier of the customer copied from find_customers.
        compute_event_id: Id class — Identifier of the existing pending customer refund request copied from find_compute_events; identical to request_id.
        source_event_id: Id class — Identifier of the original posted payment named by that request, copied from find_compute_events.
        related_event_id: Id class — Identifier of the original primary charge paid by that payment and named in the existing request's related_event_id, copied from find_compute_events.
        request_id: Id class — Identifier of the existing pending customer refund request copied from find_compute_events; identical to compute_event_id.
        correction_event_id: Id class — Identifier of the exact posted assisted correction for the original primary charge, copied from the preceding successful credit receipt or find_compute_events.
        credited_amount: Fixed-format class — The permitted immediate refund in units of USD to two decimals, supplied as a decimal number already rounded half-up to two decimal places at calculation completion; stored to two decimals, with no empty value.

    Returns:
        A string receipt saying "Recorded compute_review" followed by compute_event_id, the new internal assessment reference as a string. The successful receipt confirms the approved eligible numerical assessment without a cash disposition.
    """
    rid = ctx.make_id("authorize_compute_refund", compute_holding_id, customer_id, compute_event_id, source_event_id, related_event_id, request_id, correction_event_id, credited_amount)
    ctx.create("compute_events", rid, compute_event_id=rid, compute_holding_id=compute_holding_id, customer_id=customer_id, source_event_id=source_event_id, related_event_id=correction_event_id, request_id=request_id, external_reference='authorize_compute_refund', event_type="compute_review", status="approved", occurred_at=ctx.now(), source_subtype='refund', decision='eligible', credited_amount=round(float(credited_amount),2), net_amount=0.0, tax_amount=0.0)
    return f"Recorded compute_review {rid}."

@tool(owner="user", rw="write")
def refund_compute_payment_f0565a85(ctx: ToolContext, compute_holding_id: str, customer_id: str, compute_event_id: str, source_event_id: str, request_id: str, related_event_id: str, amount: float) -> str:
    """Execute the customer's own cash refund against the original payment after the desk hands over the numerical assessment. This returns funds to the original ACH destination represented by the source payment and records the positive receivable delta. The posted receipt confirms the cash disposition synchronously; only the customer invokes this action.

    Args:
        compute_holding_id: Id class — Identifier of the compute contract copied from find_compute_holdings or find_compute_events.
        customer_id: Id class — Identifier of the customer copied from find_customers.
        compute_event_id: Id class — Identifier of the existing pending customer refund request copied from find_compute_events; identical to request_id.
        source_event_id: Id class — Identifier of the original posted payment named by that request, copied from find_compute_events.
        request_id: Id class — Identifier of the existing pending customer refund request copied from find_compute_events; identical to compute_event_id.
        related_event_id: Id class — Identifier of the approved eligible refund assessment for this request and original payment, copied from the preceding successful assessment receipt or find_compute_events.
        amount: Fixed-format class — The positive financial amount in units of USD to two decimals, supplied as a decimal number already rounded half-up to two decimal places at calculation completion; stored to two decimals, with no empty value.

    Returns:
        A string receipt saying "Recorded compute_refund" followed by compute_event_id, the new internal refund reference as a string. The successful posted receipt confirms the customer's cash disposition and account entry.
    """
    rid = ctx.make_id("refund_compute_payment", compute_holding_id, customer_id, compute_event_id, source_event_id, request_id, related_event_id, amount)
    ctx.create("compute_events", rid, compute_event_id=rid, compute_holding_id=compute_holding_id, customer_id=customer_id, source_event_id=source_event_id, related_event_id=related_event_id, external_reference='refund_compute_payment', event_type="compute_refund", status="posted", occurred_at=ctx.now(), source_subtype='refund', amount=round(float(amount),2), net_amount=round(float(amount),2), tax_amount=0.0, method='ach', currency='USD', request_id=request_id)
    return f"Recorded compute_refund {rid}."

@tool(owner="agent", rw="write")
def allocate_compute_snapshot_3bc9aa3a(ctx: ToolContext, compute_holding_id: str, customer_id: str, compute_event_id: str, source_event_id: str, related_event_id: str, quantity: float) -> str:
    """Record the compute-attributable GB-month allocation of one shared snapshot export. This creates a completed nonfinancial entitlement record without changing raw meters or the account receivable. The returned event identifier confirms success.

    Args:
        compute_holding_id: Id class — Identifier of the compute contract, copied from find_compute_events, find_compute_holdings, find_customers or the preceding successful receipt.
        customer_id: Id class — Identifier of the customer profile, copied from find_compute_events, find_compute_holdings, find_customers or the preceding successful receipt.
        compute_event_id: Id class — Identifier of the source-correlated evidence packet returned by find_compute_events: the compute service record with source_subtype review, source_event_id equal to the original snapshot charge, and related_event_id equal to that charge's snapshot export reference.
        source_event_id: Id class — Identifier of the original snapshot invoice line, copied from find_compute_events, find_compute_holdings, find_customers or the preceding successful receipt.
        related_event_id: Id class — Identifier of the export, allocation or approved review, copied from find_compute_events, find_compute_holdings, find_customers or the preceding successful receipt.
        quantity: Fixed-format class — The quantity in units of GB-month, representation Decimal quantity to six decimal places; supplied already rounded half-up to six decimal places at calculation completion, with no empty value.

    Returns:
        String "Recorded compute_service_record" followed by compute_event_id, the new business event identifier as a string. This successful receipt confirms the completed accounting effect described above.
    """
    rid = ctx.make_id("allocate_compute_snapshot", compute_holding_id, customer_id, compute_event_id, source_event_id, related_event_id, quantity)
    ctx.create("compute_events", rid, compute_event_id=rid, compute_holding_id=compute_holding_id, customer_id=customer_id, source_event_id=source_event_id, related_event_id=related_event_id, external_reference="allocate_compute_snapshot", event_type="compute_service_record", status="completed", occurred_at=ctx.now(), quantity=round(float(quantity),6), quantity_unit='gb_month', source_subtype='supplemental', meter_code='snapshot')
    return f"Recorded compute_service_record {rid}."

@tool(owner="agent", rw="write")
def review_compute_snapshot_6efd32f0(ctx: ToolContext, compute_holding_id: str, customer_id: str, compute_event_id: str, source_event_id: str, related_event_id: str, net_amount: float) -> str:
    """Record an accountant review of one shared snapshot charge against its allocation evidence. This creates an approved incorrect review containing the corrected local subtotal without posting money. The returned event identifier confirms success.

    Args:
        compute_holding_id: Id class — Identifier of the compute contract, copied from find_compute_events, find_compute_holdings, find_customers or the preceding successful receipt.
        customer_id: Id class — Identifier of the customer profile, copied from find_compute_events, find_compute_holdings, find_customers or the preceding successful receipt.
        compute_event_id: Id class — Identifier of the completed compute-attributable snapshot allocation for the original charge, copied from its successful allocation receipt or find_compute_events; use the identical allocation reference supplied in related_event_id.
        source_event_id: Id class — Identifier of the original snapshot invoice line, copied from find_compute_events, find_compute_holdings, find_customers or the preceding successful receipt.
        related_event_id: Id class — Identifier of the export, allocation or approved review, copied from find_compute_events, find_compute_holdings, find_customers or the preceding successful receipt.
        net_amount: Fixed-format class — The net_amount in units of USD, representation USD to two decimals; supplied already rounded half-up to two decimal places at calculation completion, with no empty value.

    Returns:
        String "Recorded compute_review" followed by compute_event_id, the new business event identifier as a string. This successful receipt confirms the approved accounting effect described above.
    """
    rid = ctx.make_id("review_compute_snapshot", compute_holding_id, customer_id, compute_event_id, source_event_id, related_event_id, net_amount)
    ctx.create("compute_events", rid, compute_event_id=rid, compute_holding_id=compute_holding_id, customer_id=customer_id, source_event_id=source_event_id, related_event_id=related_event_id, external_reference="review_compute_snapshot", event_type="compute_review", status="approved", occurred_at=ctx.now(), net_amount=round(float(net_amount),2), tax_amount=0.0, credited_amount=0.0, decision='incorrect', source_subtype='supplemental', meter_code='snapshot')
    return f"Recorded compute_review {rid}."

@tool(owner="agent", rw="write")
def debit_compute_snapshot_133263fe(ctx: ToolContext, compute_holding_id: str, customer_id: str, compute_event_id: str, source_event_id: str, related_event_id: str, amount: float) -> str:
    """Post one positive upward correction against the original shared snapshot line. This increases the compute receivable by the supplied amount and records an equal untaxed net component. The returned event identifier confirms success.

    Args:
        compute_holding_id: Id class — Identifier of the compute contract, copied from find_compute_events, find_compute_holdings, find_customers or the preceding successful receipt.
        customer_id: Id class — Identifier of the customer profile, copied from find_compute_events, find_compute_holdings, find_customers or the preceding successful receipt.
        compute_event_id: Id class — Identifier of the approved incorrect snapshot arithmetic review for the original charge, copied from its successful review receipt or find_compute_events; use the identical review reference supplied in related_event_id.
        source_event_id: Id class — Identifier of the original snapshot invoice line, copied from find_compute_events, find_compute_holdings, find_customers or the preceding successful receipt.
        related_event_id: Id class — Identifier of the export, allocation or approved review, copied from find_compute_events, find_compute_holdings, find_customers or the preceding successful receipt.
        amount: Fixed-format class — The amount in units of USD, representation USD to two decimals; supplied already rounded half-up to two decimal places at calculation completion, with no empty value.

    Returns:
        String "Recorded compute_debit_adjustment" followed by compute_event_id, the new business event identifier as a string. This successful receipt confirms the posted accounting effect described above.
    """
    rid = ctx.make_id("debit_compute_snapshot", compute_holding_id, customer_id, compute_event_id, source_event_id, related_event_id, amount)
    ctx.create("compute_events", rid, compute_event_id=rid, compute_holding_id=compute_holding_id, customer_id=customer_id, source_event_id=source_event_id, related_event_id=related_event_id, external_reference="debit_compute_snapshot", event_type="compute_debit_adjustment", status="posted", occurred_at=ctx.now(), amount=round(float(amount),2), net_amount=round(float(amount),2), tax_amount=0.0, source_subtype='correction', meter_code='snapshot', currency='USD')
    return f"Recorded compute_debit_adjustment {rid}."

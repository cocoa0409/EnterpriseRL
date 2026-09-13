"""Atomic support accounting actions."""
from erlbench import ToolContext, tool

@tool(owner="agent", rw="write")
def recognize_support_spend_78bce399(ctx: ToolContext, customer_id: str, support_holding_id: str, support_event_id: str, source_event_id: str, quantity: float, period: str, interval_start: str, interval_end: str) -> str:
    """Record an agent's measured eligible-spending contribution for a support invoice source. The contract gains a posted primary consumption entry; success supplies its reference and recorded quantity, which are immediately visible in consumption history.

    Args:
        customer_id: Id class — enterprise customer reference number copied from the located customer profile.
        support_holding_id: Id class — support contract reference number copied from the contract lookup.
        support_event_id: Id class — review-designated official spending export reference number copied exactly from the selected latest billing review's related_event_id returned by support event lookup; this identifies the aggregate's evidence locator, and another export fragment's identifier is not a substitute.
        source_event_id: Id class — original support invoice-line reference number copied from the retrieved export.
        quantity: Fixed-format class — eligible spending in supported_usd, format Decimal quantity to six decimal places; unit as specified, rounded half up before submission; the submitted value is stored at six-place precision.
        period: Fixed-format class — service billing month in YYYY-MM format, UTC calendar month; an empty value is not allowed.
        interval_start: Fixed-format class — inclusive service start as format ISO timestamp or empty string in UTC, with second precision; an empty value is not allowed.
        interval_end: Fixed-format class — exclusive service end as format ISO timestamp or empty string in UTC, with second precision; an empty value is not allowed.

    Returns:
        A success string containing the created consumption reference as a string and the recorded supported_usd quantity as a six-place decimal; 'Spending recorded' confirms that the contribution is posted.
    """
    rid = ctx.make_id('support_spend', customer_id, support_holding_id, support_event_id, source_event_id, quantity, period, interval_start, interval_end)
    ctx.create('support_events', rid, support_event_id=rid, customer_id=customer_id, support_holding_id=support_holding_id, related_event_id=support_event_id, source_event_id=source_event_id, quantity=round(float(quantity),6), quantity_unit='supported_usd', event_type='support_meter', source_subtype='primary', meter_code='primary', status='posted', period=period, interval_start=interval_start, interval_end=interval_end, occurred_at=ctx.now())
    return f'Spending recorded: {rid}; quantity {quantity:.6f} supported_usd.'

@tool(owner="agent", rw="write")
def review_support_invoice_795b85b5(ctx: ToolContext, support_event_id: str, support_holding_id: str, source_event_id: str, related_event_id: str, net_amount: float, quantity: float) -> str:
    """Complete the agent accountant's support invoice review. The selected review becomes approved with an incorrect-billing decision, a corrected net fee, zero tax and reconciled physical quantity. The resulting review and its corrected fee become visible immediately; success confirms the saved review reference.

    Args:
        support_event_id: Id class — pending billing review reference number copied from support event lookup.
        support_holding_id: Id class — reviewed support contract reference number copied from that review.
        source_event_id: Id class — original invoice-line reference number copied from that review.
        related_event_id: Id class — supporting official export reference number copied from that review.
        net_amount: Fixed-format class — corrected pretax support fee in USD, format USD to two decimals; unit USD, rounded half up before submission; storage preserves cents.
        quantity: Fixed-format class — reconciled equivalent vcpu_hour quantity, format Decimal quantity to six decimal places; unit as specified, rounded half up before submission; storage preserves six-place precision.

    Returns:
        A success string with the reviewed reference as a string and corrected USD net fee as a two-place decimal; 'Review completed' confirms the approved incorrect-billing review is saved.
    """
    ctx.update('support_events', support_event_id, support_holding_id=support_holding_id, source_event_id=source_event_id, related_event_id=related_event_id, net_amount=round(float(net_amount),2), tax_amount=0.0, quantity=round(float(quantity),6), quantity_unit='vcpu_hour', status='approved', decision='incorrect', occurred_at=ctx.now())
    return f'Review completed: {support_event_id}; corrected net USD {net_amount:.2f}.'

@tool(owner="agent", rw="write")
def debit_support_invoice_804a8331(ctx: ToolContext, customer_id: str, support_holding_id: str, support_event_id: str, source_event_id: str, related_event_id: str, amount: float, period: str) -> str:
    """Post an agent's untaxed correction debit for an original support invoice line. The contract receivable increases by the submitted USD amount, with the same pretax component and zero tax. Success supplies the debit reference and the posted amount, immediately visible in accounting history.

    Args:
        customer_id: Id class — enterprise customer reference number copied from the located profile.
        support_holding_id: Id class — support contract reference number copied from the retrieved original invoice.
        support_event_id: Id class — approved review reference number copied from support event lookup or its completion receipt.
        source_event_id: Id class — original invoice-line reference number copied from that review.
        related_event_id: Id class — official source export reference number copied from that review.
        amount: Fixed-format class — positive receivable correction in USD, format USD to two decimals; unit USD, rounded half up before submission; storage preserves cents.
        period: Fixed-format class — source service billing month in YYYY-MM format, UTC calendar month; an empty value is not allowed.

    Returns:
        A success string giving the created debit reference as a string and posted USD amount as a two-place decimal; 'Debit posted' confirms that the receivable correction is saved.
    """
    rid = ctx.make_id('support_debit', customer_id, support_holding_id, support_event_id, source_event_id, related_event_id, amount, period)
    ctx.create('support_events', rid, support_event_id=rid, customer_id=customer_id, support_holding_id=support_holding_id, source_event_id=source_event_id, related_event_id=support_event_id, request_id='', amount=round(float(amount),2), net_amount=round(float(amount),2), tax_amount=0.0, period=period, status='posted', event_type='support_debit_adjustment', source_subtype='correction', occurred_at=ctx.now())
    return f'Debit posted: {rid}; USD {amount:.2f}.'

@tool(owner="agent", rw="write")
def review_support_overcharge_b721fa46(ctx: ToolContext, support_event_id: str, support_holding_id: str, source_event_id: str, related_event_id: str, net_amount: float) -> str:
    """Save the accountant's corrected support fee on an existing paid-invoice review. The review becomes approved with an incorrect-billing decision and zero tax; its corrected USD subtotal is visible immediately. The same review stores a reserved customer-request reference. Reserving this reference creates no refund request and gives no customer consent. Success confirms the reviewed reference, corrected fee and reserved request reference.

    Args:
        support_event_id: Id class — paid-invoice review reference number copied from support event lookup.
        support_holding_id: Id class — reviewed support contract reference number copied from that review.
        source_event_id: Id class — original paid invoice-line reference number copied from that review.
        related_event_id: Id class — official source-export reference number copied from that review.
        net_amount: Fixed-format class — corrected pretax fee, format USD to two decimals, unit USD; rounded half up before submission and stored at two-decimal precision.

    Returns:
        A success string with the reviewed reference as a string, corrected net USD fee as a two-decimal number and reserved request reference as a string; 'Paid review completed' confirms the approved incorrect-billing decision and reference reservation have been saved.
    """
    reserved_request_id = ctx.make_id('support_authorization', support_event_id, support_holding_id, source_event_id, related_event_id, net_amount)
    ctx.update('support_events', support_event_id, support_holding_id=support_holding_id, source_event_id=source_event_id, related_event_id=related_event_id, request_id=reserved_request_id, status='approved', decision='incorrect', net_amount=round(float(net_amount),2), tax_amount=0.0, occurred_at=ctx.now())
    return f'Paid review completed: {support_event_id}; corrected net USD {net_amount:.2f}; reserved request reference {reserved_request_id}.'

@tool(owner="agent", rw="write")
def credit_support_overcharge_7251caa0(ctx: ToolContext, customer_id: str, support_holding_id: str, support_event_id: str, source_event_id: str, related_event_id: str, amount: float, period: str) -> str:
    """Post an agent's untaxed support invoice correction credit. The submitted negative amount reduces the contract receivable, with the same net component and zero tax, while retaining the original invoice and review linkage. Success returns a credit reference and signed amount visible in accounting history.

    Args:
        customer_id: Id class — enterprise customer reference number copied from the located profile.
        support_holding_id: Id class — support contract reference number copied from its invoice review.
        support_event_id: Id class — approved incorrect-billing review reference number copied from event lookup or its completion receipt.
        source_event_id: Id class — original invoice-line reference number copied from that review.
        related_event_id: Id class — official source-export reference number copied from that review.
        amount: Fixed-format class — negative receivable credit, format USD to two decimals, unit USD; rounded half up before submission and stored at two-decimal precision.
        period: Fixed-format class — source service month in YYYY-MM format, UTC calendar month; empty is not allowed.

    Returns:
        A success string containing the created credit reference as a string and signed USD amount as a two-decimal number; 'Correction credit posted' confirms the receivable reduction is saved.
    """
    rid = ctx.make_id('support_credit', customer_id, support_holding_id, support_event_id, source_event_id, related_event_id, amount, period)
    ctx.create('support_events', rid, support_event_id=rid, customer_id=customer_id, support_holding_id=support_holding_id, source_event_id=source_event_id, related_event_id=support_event_id, request_id='', event_type='support_credit', status='posted', source_subtype='correction', amount=round(float(amount),2), net_amount=round(float(amount),2), tax_amount=0.0, period=period, occurred_at=ctx.now())
    return f'Correction credit posted: {rid}; USD {amount:.2f}.'

@tool(owner="user", rw="write")
def authorize_support_surplus_cef239e4(ctx: ToolContext, customer_id: str, support_holding_id: str, source_event_id: str, support_event_id: str, request_id: str, external_reference: str, amount: float) -> str:
    """File the customer's own authorization to return a specified support-payment surplus. A pending cash-refund request is created under the supplied reserved reference and records the chosen amount and the exact original payment and invoice; filing changes no accounting balance. Only this customer submission supplies consent; the reference reservation alone does not. Success returns the authorization reference and requested amount so the customer and desk can see what was submitted.

    Args:
        customer_id: Id class — enterprise customer reference number copied from the located profile.
        support_holding_id: Id class — support contract reference number copied from the retrieved payment.
        source_event_id: Id class — original completed payment reference number copied from support payment history.
        support_event_id: Id class — original support invoice-line reference number copied from that payment's source reference.
        request_id: Id class — reserved customer-request reference number copied from the paid-invoice review completion receipt or its request reference in support event lookup.
        external_reference: Verbatim class — use the request reference stated by the customer, copied character for character with original wording, digits and punctuation and without translation, normalisation, summarisation, addition or deletion (verbatim).
        amount: Fixed-format class — exact authorized cash refund, format USD to two decimals, unit USD; rounded half up before submission and stored at two-decimal precision.

    Returns:
        A success string giving the authorization reference as a string and requested USD amount as a two-decimal number; 'Refund authorization filed' confirms the pending request was saved and supplies its reference for subsequent customer dialogue.
    """
    rid = request_id
    ctx.create('support_events', rid, support_event_id=rid, customer_id=customer_id, support_holding_id=support_holding_id, source_event_id=source_event_id, related_event_id=support_event_id, request_id=rid, external_reference=external_reference, amount=round(float(amount),2), event_type='support_request', source_subtype='refund', status='pending', channel='portal', notice_at=ctx.now(), occurred_at=ctx.now())
    return f'Refund authorization filed: {rid}; requested USD {amount:.2f}.'

@tool(owner="agent", rw="write")
def refund_support_surplus_235c4f6f(ctx: ToolContext, customer_id: str, support_holding_id: str, support_event_id: str, request_id: str, source_event_id: str, amount: float, method: str) -> str:
    """Execute an agent's support surplus refund against the original payment. One positive receivable entry records the returned cash, original payment method and customer's authorization, with the refund reference immediately visible. Success confirms the posted USD amount and the refund reference.

    Args:
        customer_id: Id class — enterprise customer reference number copied from the located profile.
        support_holding_id: Id class — support contract reference number copied from the customer's refund authorization.
        support_event_id: Id class — cash-disposal authorization reference number copied from the paid-review reserved request reference and confirmed by the customer's filing receipt.
        request_id: Id class — exact refund request reference number copied from the paid-review reserved reference, the customer filing receipt or that authorization's request_id in event lookup.
        source_event_id: Id class — original completed payment reference number copied from that authorization.
        amount: Fixed-format class — positive returned cash receivable delta, format USD to two decimals, unit USD; rounded half up before submission and stored at two-decimal precision.
        method: Enum class — allowed values are none (a noncash accounting record), ach (cash returned to the original ACH payment destination), wire (cash returned to the original wire payment destination), and card (cash returned to the original card payment destination).

    Returns:
        A success string containing the created refund reference as a string and refunded USD amount as a two-decimal number; 'Support refund posted' confirms the cash return and receivable entry are saved.
    """
    rid = ctx.make_id('support_refund', customer_id, support_holding_id, support_event_id, request_id, source_event_id, amount, method)
    ctx.create('support_events', rid, support_event_id=rid, customer_id=customer_id, support_holding_id=support_holding_id, source_event_id=source_event_id, request_id=request_id, related_event_id=support_event_id, amount=round(float(amount),2), method=method, event_type='support_refund', source_subtype='refund', status='posted', occurred_at=ctx.now())
    return f'Support refund posted: {rid}; USD {amount:.2f}.'

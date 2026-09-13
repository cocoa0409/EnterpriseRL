"""Atomic network accounting actions."""
from erlbench import ToolContext, tool


@tool(owner="agent", rw="write")
def assess_network_f148f79a(ctx: ToolContext, network_holding_id: str, network_event_id: str, source_event_id: str, related_event_id: str, net_amount: float) -> dict:
    """The accountant completes the selected network billing review, recording its corrected net subtotal and an approved incorrect decision. The returned review receipt makes the completed assessment observable.

    Args:
        network_holding_id: Id class — Network contract identifier copied from find_network_holdings.
        network_event_id: Id class — Evidence event identifier copied from find_network_events.
        source_event_id: Id class — Exact original charge or payment identifier copied from find_network_events.
        related_event_id: Id class — Review identifier copied from find_network_events.
        net_amount: Fixed-format class — Corrected pretax subtotal in unit USD to two decimals, decimal number to two decimals; supplied after final half-up rounding, stored at two-decimal precision.

    Returns:
        A dictionary containing event_id (string business-event reference) and net_amount (USD decimal number to two decimals); receipt presence confirms the accounting action completed.
    """
    ctx.update("network_events", related_event_id, net_amount=round(float(net_amount), 2), status="approved", decision="incorrect")
    return {"event_id": related_event_id, "net_amount": round(float(net_amount), 2)}


@tool(owner="agent", rw="write")
def credit_network_4dd38821(ctx: ToolContext, customer_id: str, network_holding_id: str, network_event_id: str, source_event_id: str, related_event_id: str, amount: float) -> dict:
    """The accountant posts one network correction credit against its exact original charge and review. The negative receivable adjustment appears immediately in the account and its credit receipt confirms success.

    Args:
        customer_id: Id class — Customer profile identifier copied from find_customers.
        network_holding_id: Id class — Network contract identifier copied from find_network_holdings.
        network_event_id: Id class — Evidence event identifier copied from find_network_events.
        source_event_id: Id class — Exact original charge or payment identifier copied from find_network_events.
        related_event_id: Id class — Review identifier copied from find_network_events.
        amount: Fixed-format class — Signed receivable change in unit USD to two decimals, decimal number to two decimals; supplied after final half-up rounding, stored at two-decimal precision.

    Returns:
        A dictionary containing event_id (string business-event reference) and amount (USD decimal number to two decimals); receipt presence confirms the accounting action completed.
    """
    rid = ctx.make_id("network_credit", customer_id, network_holding_id, network_event_id, source_event_id, related_event_id, amount)
    ctx.create("network_events", rid, network_event_id=rid, customer_id=customer_id, network_holding_id=network_holding_id, source_event_id=source_event_id, related_event_id=related_event_id, event_type="network_credit", source_subtype="correction", status="posted", amount=round(float(amount), 2), net_amount=round(float(amount), 2), tax_amount=0.0, currency="USD", method="none", occurred_at=ctx.now())
    return {"event_id": rid, "amount": round(float(amount), 2)}


@tool(owner="agent", rw="write")
def refund_network_f88363e7(ctx: ToolContext, customer_id: str, network_holding_id: str, network_event_id: str, source_event_id: str, related_event_id: str, request_id: str, amount: float) -> dict:
    """The accountant pays out the authorized network overpayment to the original ACH payment destination, recording a positive receivable adjustment. The payout receipt identifies the completed refund.

    Args:
        customer_id: Id class — Customer profile identifier copied from find_customers.
        network_holding_id: Id class — Network contract identifier copied from find_network_holdings.
        network_event_id: Id class — Evidence event identifier copied from find_network_events.
        source_event_id: Id class — Exact original charge or payment identifier copied from find_network_events.
        related_event_id: Id class — Review identifier copied from find_network_events.
        request_id: Id class — Customer authorization identifier copied from find_network_events.
        amount: Fixed-format class — Signed receivable change in unit USD to two decimals, decimal number to two decimals; supplied after final half-up rounding, stored at two-decimal precision.

    Returns:
        A dictionary containing event_id (string business-event reference) and amount (USD decimal number to two decimals); receipt presence confirms the accounting action completed.
    """
    rid = ctx.make_id("network_refund", customer_id, network_holding_id, network_event_id, source_event_id, related_event_id, request_id, amount)
    ctx.create("network_events", rid, network_event_id=rid, customer_id=customer_id, network_holding_id=network_holding_id, source_event_id=source_event_id, related_event_id=related_event_id, request_id=request_id, event_type="network_refund", source_subtype="refund", status="posted", amount=round(float(amount), 2), net_amount=round(float(amount), 2), tax_amount=0.0, currency="USD", method="ach", occurred_at=ctx.now())
    return {"event_id": rid, "amount": round(float(amount), 2)}


@tool(owner="user", rw="write")
def authorize_network_11d4a76e(ctx: ToolContext, customer_id: str, network_holding_id: str, network_event_id: str, source_event_id: str, related_event_id: str, request_id: str, external_reference: str, net_amount: float) -> dict:
    """The customer signs the selected preexisting unsigned authorization form and files it as a network invoice-ceiling request, preserving its stable event identifier. The pending acceptance preserves their exact reference and maximum net amount without changing the account balance; the acceptance receipt confirms filing.

    Args:
        customer_id: Id class — Customer profile identifier copied from find_customers.
        network_holding_id: Id class — Network contract identifier copied from find_network_holdings.
        network_event_id: Id class — Authoritative source evidence event identifier copied from find_network_events.
        source_event_id: Id class — Exact export or net invoice identifier copied from find_network_events or the preceding invoice receipt.
        related_event_id: Id class — Pricing review identifier copied from find_network_events.
        request_id: Id class — Unsigned authorization form identifier copied from find_network_events; signing preserves this same identifier in the receipt.
        external_reference: Verbatim class — Copy the customer-stated authorization reference character for character, preserving wording, digits and punctuation, with no translation, normalization, summarization, addition or deletion (verbatim).
        net_amount: Fixed-format class — Accepted or assessed net subtotal in unit USD to two decimals, decimal number with two-decimal precision, supplied after final half-up rounding and stored at two decimals.

    Returns:
        A dictionary with event_id (string business-event identifier) and net_amount (USD decimal number to two decimals); this receipt confirms completion.
    """
    rid = request_id
    ctx.update("network_events", rid, network_event_id=rid, request_id=rid, customer_id=customer_id, network_holding_id=network_holding_id, source_event_id=source_event_id, related_event_id=related_event_id, occurred_at=ctx.now(), currency="USD", event_type="network_request", source_subtype="request", status="pending", notice_at=ctx.now(), channel="portal", external_reference=external_reference, net_amount=round(float(net_amount), 2), amount=0.0, tax_amount=0.0)
    return {"event_id": rid, "net_amount": round(float(net_amount), 2)}


@tool(owner="agent", rw="write")
def price_network_84b98f50(ctx: ToolContext, network_holding_id: str, network_event_id: str, source_event_id: str, related_event_id: str, request_id: str, net_amount: float) -> dict:
    """The accountant completes the network source pricing assessment under the selected customer acceptance, recording an approved correct net subtotal. Its assessment receipt confirms the reviewed price is available.

    Args:
        network_holding_id: Id class — Network contract identifier copied from find_network_holdings.
        network_event_id: Id class — Authoritative source evidence event identifier copied from find_network_events.
        source_event_id: Id class — Exact export or net invoice identifier copied from find_network_events or the preceding invoice receipt.
        related_event_id: Id class — Pricing review identifier copied from find_network_events.
        request_id: Id class — Customer acceptance identifier copied from the actual preceding authorization receipt.
        net_amount: Fixed-format class — Accepted or assessed net subtotal in unit USD to two decimals, decimal number with two-decimal precision, supplied after final half-up rounding and stored at two decimals.

    Returns:
        A dictionary with event_id (string business-event identifier) and net_amount (USD decimal number to two decimals); this receipt confirms completion.
    """
    ctx.update("network_events", related_event_id, net_amount=round(float(net_amount), 2), status="approved", decision="correct", request_id=request_id)
    return {"event_id": related_event_id, "net_amount": round(float(net_amount), 2)}


@tool(owner="agent", rw="write")
def invoice_network_9ee25cfe(ctx: ToolContext, customer_id: str, network_holding_id: str, network_event_id: str, source_event_id: str, related_event_id: str, request_id: str, meter_code: str, source_subtype: str, pricing_component: str, period: str, amount: float) -> dict:
    """The accountant issues a network net-service invoice for the selected source export and accepted assessment. One positive net receivable entry becomes visible immediately, and the invoice receipt confirms issuance.

    Args:
        customer_id: Id class — Customer profile identifier copied from find_customers.
        network_holding_id: Id class — Network contract identifier copied from find_network_holdings.
        network_event_id: Id class — Authoritative source evidence event identifier copied from find_network_events.
        source_event_id: Id class — Exact export or net invoice identifier copied from find_network_events or the preceding invoice receipt.
        related_event_id: Id class — Pricing review identifier copied from find_network_events.
        request_id: Id class — Customer acceptance identifier copied from the actual preceding authorization receipt.
        meter_code: Enum class — Allowed values: primary (the source uses the generic primary meter); internet_egress (traffic leaves the public internet interface); port_hours (a provisioned line port accrues hours); cross_zone (traffic crosses availability zones); cross_region (traffic crosses cloud regions); private_egress (traffic uses private interconnect); ingress (traffic enters the network); nat_gb (NAT processing is measured by GB); nat_hours (NAT provisioning is measured by hours); public_ipv4 (allocated IPv4 address-hours are measured); connection_setup (a new physical connection is completed); loadbalancer (load balancer capacity-unit-hours are measured); none (no measured source or pricing branch applies)
        source_subtype: Enum class — Allowed values: primary (the source uses the generic primary meter); supplemental (ancillary service is billed); setup (an activation setup fee is billed); termination (a resource exit liability is billed); resumption (a restoration fee is billed); return_fee (a failed remittance fee is billed); marketplace (a marketplace product charge is recorded); service_credit (an outage concession is recorded); correction (an erroneous invoice is adjusted); remittance (a payment receipt is allocated); refund (cash is returned to its source payment); incident (an operational outage is recorded); request (a customer authorization is filed); review (an accountant assessment is recorded); amendment (signed contract attributes are amended)
        pricing_component: Enum class — Allowed values: none (no measured source or pricing branch applies); negotiated (an approved negotiated rate applies); reservation (a signed commitment covers the quantity); promotion (an eligible campaign is selected); portfolio (the supported portfolio price is selected); standard (no preferential price applies); spot (spot capacity pricing applies)
        period: Fixed-format class — UTC billing month in YYYY-MM format; no empty value.
        amount: Fixed-format class — Positive receivable component in unit USD to two decimals, decimal number with two-decimal precision, supplied after final half-up rounding and stored at two decimals.

    Returns:
        A dictionary with event_id (string business-event identifier) and amount (USD decimal number to two decimals); this receipt confirms completion.
    """
    rid = ctx.make_id("network_invoice", customer_id, network_holding_id, network_event_id, source_event_id, related_event_id, request_id, meter_code, source_subtype, pricing_component, period, amount)
    ctx.create("network_events", rid, network_event_id=rid, customer_id=customer_id, network_holding_id=network_holding_id, source_event_id=source_event_id, related_event_id=related_event_id, occurred_at=ctx.now(), currency="USD", event_type="network_charge", status="posted", request_id=request_id, meter_code=meter_code, source_subtype=source_subtype, pricing_component=pricing_component, period=period, invoice_issued_at=ctx.now(), amount=round(float(amount), 2), net_amount=round(float(amount), 2), tax_amount=0.0)
    return {"event_id": rid, "amount": round(float(amount), 2)}


@tool(owner="agent", rw="write")
def tax_network_645ca35d(ctx: ToolContext, customer_id: str, network_holding_id: str, network_event_id: str, source_event_id: str, related_event_id: str, request_id: str, amount: float) -> dict:
    """The accountant posts the separate network tax debit against the exact net invoice. The positive tax receivable completes its tax component immediately; the tax receipt confirms posting.

    Args:
        customer_id: Id class — Customer profile identifier copied from find_customers.
        network_holding_id: Id class — Network contract identifier copied from find_network_holdings.
        network_event_id: Id class — Authoritative source evidence event identifier copied from find_network_events.
        source_event_id: Id class — Exact export or net invoice identifier copied from find_network_events or the preceding invoice receipt.
        related_event_id: Id class — Pricing review identifier copied from find_network_events.
        request_id: Id class — Customer acceptance identifier copied from the actual preceding authorization receipt.
        amount: Fixed-format class — Positive receivable component in unit USD to two decimals, decimal number with two-decimal precision, supplied after final half-up rounding and stored at two decimals.

    Returns:
        A dictionary with event_id (string business-event identifier) and amount (USD decimal number to two decimals); this receipt confirms completion.
    """
    rid = ctx.make_id("network_tax", customer_id, network_holding_id, network_event_id, source_event_id, related_event_id, request_id, amount)
    ctx.create("network_events", rid, network_event_id=rid, customer_id=customer_id, network_holding_id=network_holding_id, source_event_id=source_event_id, related_event_id=related_event_id, occurred_at=ctx.now(), currency="USD", event_type="network_debit_adjustment", source_subtype="supplemental", status="posted", request_id=request_id, amount=round(float(amount), 2), net_amount=0.0, tax_amount=round(float(amount), 2))
    return {"event_id": rid, "amount": round(float(amount), 2)}


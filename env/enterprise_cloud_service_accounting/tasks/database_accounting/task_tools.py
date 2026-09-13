from erlbench import ToolContext, tool


@tool(owner="agent", rw="write")
def record_external_retention_8927a6d4(ctx: ToolContext, database_event_id: str, quantity: float) -> str:
    """Record the externally protected portion of retained database storage. Replace the database retention assessment's quantity and set its status to completed. A completed receipt confirms that the corrected entitlement is recorded and available to account readers.

    Args:
        database_event_id: Id class — Identifier of a database retention assessment record, obtained from find_database_events.
        quantity: Fixed-format class — Assessed retained capacity; unit GB-month. Decimal quantity to six decimal places; round half-up once at submission, with no empty value.

    Returns:
        A string receipt containing database_event_id (assessment reference string), quantity (GB-month decimal with six places), and status=completed, confirming the assessment was updated.
    """
    ctx.update("database_events", database_event_id, quantity=round(float(quantity), 6), status="completed")
    return f"database_event_id={database_event_id} quantity={float(quantity):.6f} status=completed"


@tool(owner="agent", rw="write")
def record_native_retention_e94b4258(ctx: ToolContext, database_event_id: str, quantity: float) -> str:
    """Record native retention allocation for the database account. Replace the database retention assessment's quantity and set its status to completed. A completed receipt confirms that the corrected entitlement is recorded and available to account readers.

    Args:
        database_event_id: Id class — Identifier of a database retention assessment record, obtained from find_database_events.
        quantity: Fixed-format class — Assessed retained capacity; unit GB-month. Decimal quantity to six decimal places; round half-up once at submission, with no empty value.

    Returns:
        A string receipt containing database_event_id (assessment reference string), quantity (GB-month decimal with six places), and status=completed, confirming the assessment was updated.
    """
    ctx.update("database_events", database_event_id, quantity=round(float(quantity), 6), status="completed")
    return f"database_event_id={database_event_id} quantity={float(quantity):.6f} status=completed"


@tool(owner="agent", rw="write")
def record_retention_statement_3c3aee31(ctx: ToolContext, database_event_id: str, quantity: float) -> str:
    """Record retention statement reconciliation for the database account. Replace the database retention assessment's quantity and set its status to completed. A completed receipt confirms that the corrected entitlement is recorded and available to account readers.

    Args:
        database_event_id: Id class — Identifier of a database retention assessment record, obtained from find_database_events.
        quantity: Fixed-format class — Assessed retained capacity; unit GB-month. Decimal quantity to six decimal places; round half-up once at submission, with no empty value.

    Returns:
        A string receipt containing database_event_id (assessment reference string), quantity (GB-month decimal with six places), and status=completed, confirming the assessment was updated.
    """
    ctx.update("database_events", database_event_id, quantity=round(float(quantity), 6), status="completed")
    return f"database_event_id={database_event_id} quantity={float(quantity):.6f} status=completed"


@tool(owner="agent", rw="write")
def post_primary_average_31a3f059(ctx: ToolContext, database_event_id: str, quantity: float) -> str:
    """Complete the per-node database usage assessment by replacing its quantity and setting completed status. The resulting corrected usage assessment is immediately visible to account readers.

    Args:
        database_event_id: Id class — Identifier of the pending database usage assessment record obtained from find_database_events.
        quantity: Fixed-format class — Reconciled average node usage; unit node-hour. Decimal quantity to six decimal places, round half-up once at submission; no empty value.

    Returns:
        String receipt with database_event_id (assessment reference), quantity (node-hour decimal to six places) and status=completed, confirming the changed usage assessment.
    """
    ctx.update("database_events", database_event_id, quantity=round(float(quantity), 6), status="completed")
    return f"database_event_id={database_event_id} quantity={float(quantity):.6f} status=completed"


@tool(owner="agent", rw="write")
def post_primary_target_faf69343(ctx: ToolContext, database_event_id: str, database_holding_id: str, source_event_id: str, related_event_id: str, net_amount: float) -> str:
    """Record the accountant's corrected tax-exempt net invoice target in the specified database billing review. Replace its net_amount, set tax_amount to zero, status to approved and decision to incorrect. The approved review is authoritative evidence and changes no receivable balance.

    Args:
        database_event_id: Id class — Identifier of the database billing review record obtained from find_database_events.
        database_holding_id: Id class — Identifier of the reviewed database contract obtained from find_database_holdings.
        source_event_id: Id class — Identifier of the original invoice charge record obtained from find_database_events.
        related_event_id: Id class — Identifier of the usage evidence assessment record obtained from its completion receipt or find_database_events.
        net_amount: Fixed-format class — Corrected pretax target; unit USD. USD to two decimals, round half-up once at submission, no empty value.

    Returns:
        String receipt with database_event_id (review reference), net_amount (USD to two decimals), status=approved and decision=incorrect, confirming the corrected target has been recorded without posting money.
    """
    ctx.update("database_events", database_event_id, database_holding_id=database_holding_id, source_event_id=source_event_id, related_event_id=related_event_id, net_amount=round(float(net_amount), 2), tax_amount=0.0, status="approved", decision="incorrect")
    return f"database_event_id={database_event_id} net_amount={float(net_amount):.2f} status=approved decision=incorrect"


@tool(owner="user", rw="write")
def post_correction_consent_d1041c04(ctx: ToolContext, database_event_id: str, database_holding_id: str, customer_id: str, related_event_id: str, request_id: str, external_reference: str, quantity: float) -> str:
    """Personally file a database invoice correction authorization for the stated amount. Update the existing unsigned request in place, linking it to the original charge and billing review and recording the customer's exact existing reference, authorized amount and current filing time. The request authorizes the customer's own account correction and does not itself change the balance.

    Args:
        database_event_id: Id class — Identifier of the original database invoice charge record obtained from find_database_events.
        database_holding_id: Id class — Identifier of the database contract obtained from find_database_holdings.
        customer_id: Id class — Identifier of the verified enterprise customer profile obtained from find_customers.
        related_event_id: Id class — Identifier of the approved billing review record obtained from its receipt or find_database_events.
        request_id: Id class — Identifier of the existing unsigned request selected by the contract request_id, obtained from find_database_holdings and find_database_events.
        external_reference: Verbatim class — Copy the correction authorization reference supplied by the customer character for character, preserving wording, digits and punctuation with no translation, normalization, summarization, addition or deletion (verbatim).
        quantity: Fixed-format class — Personally authorized correction amount; unit USD. Decimal quantity to six decimal places; monetary USD value limited to two decimal places, round half-up once at submission, no empty value.

    Returns:
        String receipt with request_id (the existing request reference now personally signed), quantity (authorized USD amount to two decimals) and status=pending, confirming immediate filing by the customer.
    """
    ctx.update("database_events", request_id, database_holding_id=database_holding_id, customer_id=customer_id, source_event_id=database_event_id, request_id=request_id, related_event_id=related_event_id, external_reference=external_reference, quantity=round(float(quantity), 2), quantity_unit="usd", event_type="database_request", source_subtype="correction", meter_code="none", status="pending", notice_at=ctx.now(), occurred_at=ctx.now())
    return f"request_id={request_id} quantity={float(quantity):.2f} status=pending"


@tool(owner="agent", rw="write")
def post_primary_correction_900303b8(ctx: ToolContext, database_event_id: str, database_holding_id: str, customer_id: str, source_event_id: str, related_event_id: str, request_id: str, amount: float) -> str:
    """Post a tax-exempt database invoice correction credit. Create one posted credit with the supplied signed amount as both receivable change and pretax component, tax_amount zero, attached to the original charge, approved review and customer authorization. The negative receivable change is immediately visible on the account.

    Args:
        database_event_id: Id class — Identifier of the authoritative billing review record obtained from its approved review receipt or find_database_events.
        database_holding_id: Id class — Identifier of the database contract obtained from find_database_holdings.
        customer_id: Id class — Identifier of the verified enterprise profile obtained from find_customers.
        source_event_id: Id class — Identifier of the original invoice charge record obtained from find_database_events.
        related_event_id: Id class — Identifier of the approved billing review record to attach, obtained from its receipt or find_database_events.
        request_id: Id class — Identifier of the existing request obtained from find_database_events and confirmed as personally signed by the customer's filing receipt.
        amount: Fixed-format class — Signed receivable credit; unit USD. USD to two decimals, round half-up once at submission, no empty value.

    Returns:
        String receipt with database_event_id (new posted credit reference), amount (signed USD to two decimals) and status=posted, confirming the receivable credit is recorded.
    """
    rid = ctx.make_id("db_primary_credit", database_event_id, database_holding_id, customer_id, source_event_id, related_event_id, request_id, amount)
    ctx.create("database_events", rid, database_event_id=rid, database_holding_id=database_holding_id, customer_id=customer_id, source_event_id=source_event_id, related_event_id=related_event_id, request_id=request_id, event_type="database_credit", source_subtype="correction", amount=round(float(amount), 2), net_amount=round(float(amount), 2), tax_amount=0.0, currency="USD", status="posted", occurred_at=ctx.now())
    return f"database_event_id={rid} amount={float(amount):.2f} status=posted"

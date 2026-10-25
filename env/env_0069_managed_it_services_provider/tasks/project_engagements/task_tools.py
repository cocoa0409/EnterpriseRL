"""Hidden task tools for the project_engagements difficulty of env_0069 (Stratton Bay Technology Partners).

Each tool performs one atomic write on a Professional Services engagement and is reached through the
unlock_* -> call_* meta-tools. No tool checks a business precondition; the agent decides from policy.
"""

from erlbench import ToolContext, tool


class _Ref:
    """Reference-number helpers (format only)."""

    @staticmethod
    def invoice_number(row_id: str) -> str:
        digits = int(row_id.split("_")[-1], 16) % 1000000
        return "INV-" + str(digits).zfill(6)

    @staticmethod
    def billing_row(ctx: ToolContext, prefix: str, project_engagement_id: str, event_type: str, amount: float,
                     milestone_number: int = 0, change_order_number: str = "") -> tuple:
        """Shared field layout of a new engagement billing charge (values only; the caller writes)."""
        eng = ctx.find("project_engagements", project_engagement_id=project_engagement_id)
        customer_id = eng[0].get("customer_id") if eng else ""
        rid = ctx.make_id(prefix, project_engagement_id, event_type, milestone_number, change_order_number, amount)
        today = ctx.now()[:10]
        fields = dict(project_billing_entry_id=rid, project_engagement_id=project_engagement_id, customer_id=customer_id,
                      event_type=event_type, amount_usd=amount, invoice_number=_Ref.invoice_number(rid), posted_date=today,
                      billing_period=today[:7], milestone_number=milestone_number, change_order_number=change_order_number,
                      expense_reference="", expense_category="not_applicable", payment_reference="",
                      original_billing_entry_id=None, source_engagement_id=None)
        return rid, fields


@tool(owner="user", rw="write")
def sign_statement_of_work_96bc6bf1(ctx: ToolContext, customer_id: str, project_engagement_id: str,
                                    rate_discount_pct: float) -> str:
    """The client's authorized contact e-signs a statement of work that is open for signature. The
    engagement moves to signed status, the signature date is recorded as today's date, and the labor
    rate discount locked by the signature is written to the engagement; the signed statement of work
    then shows the signed status, the signature date and the locked discount.

    Args:
        customer_id: Id class — the client reference number of the organisation whose authorized
            contact is signing, as returned by the client profile lookup.
        project_engagement_id: Id class — the reference number of the project engagement whose
            statement of work is being signed, as returned by the project engagement lookup.
        rate_discount_pct: Fixed-format class — the labor rate discount locked at signature, in
            percent, as a non-negative decimal number with 1 decimal place.

    Returns:
        A confirmation string naming the client reference number, the engagement reference number, its
        new status (signed), the
        signature date in YYYY-MM-DD form and the locked rate discount in percent with one decimal
        place; that string indicates the signature was recorded.
    """
    signed_on = ctx.now()[:10]
    pct = round(float(rate_discount_pct), 1)
    ctx.update("project_engagements", project_engagement_id, status="signed", signed_date=signed_on,
               rate_discount_pct=pct)
    return (f"Statement of work signed for client {customer_id}: engagement {project_engagement_id}, status signed, "
            f"signed_date {signed_on}, rate_discount_pct {pct:.1f}.")


@tool(owner="agent", rw="write")
def post_deposit_invoice_06d795b1(ctx: ToolContext, project_engagement_id: str, amount_usd: float) -> str:
    """Post the deposit invoice of a signed statement of work to the engagement's billing. A new
    deposit charge is added to the engagement's billing with a newly assigned invoice number, today's
    date as its posting date and the current month as its billing month; the client can then see the
    deposit invoice and its amount on the engagement's billing.

    Args:
        project_engagement_id: Id class — the reference number of the project engagement the deposit
            belongs to, as returned by the project engagement lookup.
        amount_usd: Fixed-format class — the deposit amount in US dollars, a positive decimal number
            with 2 decimal places.

    Returns:
        A confirmation string giving the new billing entry reference, the invoice number (INV- followed
        by 6 digits), the engagement reference number, the deposit amount in US dollars with two decimal
        places and the posting date in YYYY-MM-DD form; that string indicates the deposit invoice was
        posted.
    """
    amount = round(float(amount_usd), 2)
    eng = ctx.find("project_engagements", project_engagement_id=project_engagement_id)
    customer_id = eng[0].get("customer_id") if eng else ""
    rid = ctx.make_id("pbe_", project_engagement_id, "project_deposit_invoice", amount)
    inv = _Ref.invoice_number(rid)
    today = ctx.now()[:10]
    ctx.create("project_billing", rid, project_billing_entry_id=rid, project_engagement_id=project_engagement_id,
               customer_id=customer_id, event_type="project_deposit_invoice", amount_usd=amount,
               invoice_number=inv, posted_date=today, billing_period=today[:7], milestone_number=0,
               change_order_number="", expense_reference="", expense_category="not_applicable",
               payment_reference="", original_billing_entry_id=None, source_engagement_id=None)
    return (f"Deposit invoice posted: entry {rid}, invoice {inv}, engagement {project_engagement_id}, "
            f"amount_usd {amount:.2f}, posted_date {today}.")



@tool(owner="agent", rw="write")
def post_milestone_invoice_79b8c922(ctx: ToolContext, project_engagement_id: str, milestone_number: int,
                                    amount_usd: float) -> str:
    """Post the invoice for a milestone of a fixed-fee engagement that has been recorded complete. A new
    milestone charge naming the milestone's position is added to the engagement's billing with a newly
    assigned invoice number, today's date as its posting date and the current month as its billing
    month; the client can then see the milestone invoice and its amount on the engagement's billing.

    Args:
        project_engagement_id: Id class — the reference number of the project engagement the milestone
            belongs to, as returned by the project engagement lookup.
        milestone_number: Fixed-format class — the milestone's position in the statement of work's
            milestone schedule, a whole number counted from 1 (integer).
        amount_usd: Fixed-format class — the milestone invoice amount in US dollars, a positive decimal
            number with 2 decimal places.

    Returns:
        A confirmation string giving the new billing entry reference, the invoice number (INV- followed
        by 6 digits), the engagement reference number, the milestone position, the amount in US dollars
        with two decimal places and the posting date in YYYY-MM-DD form; that string indicates the
        milestone invoice was posted.
    """
    amount = round(float(amount_usd), 2)
    pos = int(milestone_number)
    rid, fields = _Ref.billing_row(ctx, "pbm_", project_engagement_id, "project_milestone_invoice", amount, milestone_number=pos)
    ctx.create("project_billing", rid, **fields)
    return (f"Milestone invoice posted: entry {rid}, invoice {fields['invoice_number']}, engagement "
            f"{project_engagement_id}, milestone {pos}, amount_usd {amount:.2f}, posted_date {fields['posted_date']}.")


@tool(owner="user", rw="write")
def sign_restart_change_order_602c3012(ctx: ToolContext, customer_id: str, change_order_number: str,
                                       value_delta_usd: float) -> str:
    """The client's authorized contact e-signs a change order that is open for signature on a project
    engagement and that re-prices the remaining work of an engagement being restarted after a pause.
    The change order moves to signed status and carries the value change stated at signature, and the
    signed change is applied to its engagement: the engagement's current contract value moves by that
    value change and its count of signed change orders goes up by one. The signed change order then
    appears among the engagement's change orders with that value.

    Args:
        customer_id: Id class — the client reference number of the organisation whose authorized
            contact is signing, as returned by the client profile lookup.
        change_order_number: Fixed-format class — the number of the change order open for signature,
            CO- followed by the statement of work digits, a hyphen and 2 digits, as shown by the change
            order lookup.
        value_delta_usd: Fixed-format class — the change to the contract value in US dollars, a signed
            decimal number with 2 decimal places (positive for an increase).

    Returns:
        A confirmation string giving the change order number, the client reference number, the value
        change in US dollars with two decimal places, the status signed, the engagement reference number
        and the engagement's new contract value in US dollars with two decimal places; that string
        indicates the change order was signed and applied.
    """
    delta = round(float(value_delta_usd), 2)
    rows = ctx.find("project_change_orders", change_order_number=change_order_number)
    rid = rows[0].get("project_change_order_id") if rows else ctx.make_id("pco_", customer_id, change_order_number)
    eid = rows[0].get("project_engagement_id") if rows else ""
    eng = ctx.find("project_engagements", project_engagement_id=eid) if eid else []
    contract = round(float(eng[0].get("contract_value_usd") or 0) + delta, 2) if eng else 0.0
    count = int(eng[0].get("change_order_count") or 0) + 1 if eng else 0
    ctx.update("project_change_orders", rid, request_status="signed", value_delta_usd=delta)
    if eng:
        ctx.update("project_engagements", eid, contract_value_usd=contract, change_order_count=count)
    return (f"Change order signed: {change_order_number}, client {customer_id}, value_delta_usd {delta:.2f}, "
            f"status signed; engagement {eid} contract_value_usd {contract:.2f}.")


@tool(owner="agent", rw="write")
def post_change_order_fee_93724a4c(ctx: ToolContext, project_engagement_id: str, change_order_number: str,
                                   amount_usd: float) -> str:
    """Post the administration fee of a signed change order to the engagement's billing. A new change
    order fee charge naming the change order is added with a newly assigned invoice number, today's
    date as its posting date and the current month as its billing month; the client can then see the
    fee and the change order it relates to on the engagement's billing.

    Args:
        project_engagement_id: Id class — the reference number of the project engagement the change
            order belongs to, as returned by the project engagement lookup.
        change_order_number: Fixed-format class — the change order number as shown on the signed change
            order, CO- followed by the statement of work digits, a hyphen and 2 digits.
        amount_usd: Fixed-format class — the administration fee in US dollars, a positive decimal number
            with 2 decimal places.

    Returns:
        A confirmation string giving the new billing entry reference, the invoice number (INV- followed
        by 6 digits), the engagement reference number, the change order number, the fee in US dollars
        with two decimal places and the posting date in YYYY-MM-DD form; that string indicates the fee
        was posted.
    """
    amount = round(float(amount_usd), 2)
    rid, fields = _Ref.billing_row(ctx, "pbc_", project_engagement_id, "project_change_order_fee", amount,
                               change_order_number=change_order_number)
    ctx.create("project_billing", rid, **fields)
    return (f"Change order fee posted: entry {rid}, invoice {fields['invoice_number']}, engagement "
            f"{project_engagement_id}, change order {change_order_number}, amount_usd {amount:.2f}, "
            f"posted_date {fields['posted_date']}.")


@tool(owner="agent", rw="write")
def post_remobilization_fee_508d4151(ctx: ToolContext, project_engagement_id: str, amount_usd: float) -> str:
    """Post the remobilization fee of an engagement whose work has resumed after a pause. A new
    remobilization charge is added to the engagement's billing with a newly assigned invoice number,
    today's date as its posting date and the current month as its billing month; the client can then
    see the remobilization fee and its amount on the engagement's billing.

    Args:
        project_engagement_id: Id class — the reference number of the project engagement that resumed,
            as returned by the project engagement lookup.
        amount_usd: Fixed-format class — the remobilization fee in US dollars, a positive decimal number
            with 2 decimal places.

    Returns:
        A confirmation string giving the new billing entry reference, the invoice number (INV- followed
        by 6 digits), the engagement reference number, the fee in US dollars with two decimal places and
        the posting date in YYYY-MM-DD form; that string indicates the remobilization fee was posted.
    """
    amount = round(float(amount_usd), 2)
    rid, fields = _Ref.billing_row(ctx, "pbr_", project_engagement_id, "project_remobilization_fee", amount)
    ctx.create("project_billing", rid, **fields)
    return (f"Remobilization fee posted: entry {rid}, invoice {fields['invoice_number']}, engagement "
            f"{project_engagement_id}, amount_usd {amount:.2f}, posted_date {fields['posted_date']}.")

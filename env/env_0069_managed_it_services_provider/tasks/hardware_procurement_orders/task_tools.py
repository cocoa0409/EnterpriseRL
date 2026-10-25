"""Hidden task tools for hardware_procurement_orders (env_0069_managed_it_services_provider).

Each tool performs one atomic, already-decided business write on a hardware order and judges no
eligibility: every amount it books is passed in by the caller.
"""

from erlbench import ToolContext, tool


class _Refs:
    """Formatting helpers for business reference numbers (values only; no writes)."""

    @staticmethod
    def six_digits(ctx: ToolContext, prefix: str, *parts) -> str:
        return str(int(ctx.make_id(prefix, *parts)[-8:], 16) % 1000000).zfill(6)


@tool(owner="user", rw="write")
def sign_order_cancellation_55862425(ctx: ToolContext, customer_id: str, hardware_order_id: str, fee_usd: float) -> str:
    """The authorized contact e-signs the cancellation of their own hardware order whose distributor
    purchase order has already been placed and which has not shipped. One call records the signed
    cancellation request, moves the order to cancelled (cancelled after its purchase order, cancelled
    and closed today) and books the cancellation fee on the order's billing ledger as a new invoice,
    adding it to the amount the client owes on the order. The client sees the order shown as
    cancelled and a cancellation fee invoice for the amount signed.

    Args:
        customer_id: Id class — client reference number of the verified client signing, as returned by the client profile lookup.
        hardware_order_id: Id class — reference number of the client's hardware order being cancelled, as returned by the hardware order lookup for this client.
        fee_usd: Fixed-format class — the cancellation fee the client signs for, in USD, a positive amount rounded half up to 2 decimal places.

    Returns:
        A confirmation sentence (string) naming the signed request reference, the order reference, the
        order's new status cancelled, the cancellation fee invoice number (INV- followed by 6 digits) and
        the fee booked in USD with 2 decimal places; receiving it means the cancellation and its fee
        are on record.
    """
    order = ctx.find("hardware_orders", hardware_order_id=hardware_order_id)[0]
    today = ctx.now()[:10]
    fee = round(float(fee_usd), 2)
    rid = ctx.make_id("hcr_", hardware_order_id, "order_cancellation", fee)
    ctx.create("hardware_client_requests", rid, hardware_request_id=rid, customer_id=customer_id,
               hardware_order_id=hardware_order_id, request_type="order_cancellation",
               return_type="not_applicable", requested_qty=0, request_status="signed", created_at=ctx.now())
    ctx.update("hardware_orders", hardware_order_id, status="cancelled", cancellation_stage="after_po",
               cancelled_date=today, closed_date=today,
               balance_due_usd=round(float(order.get("balance_due_usd") or 0) + fee, 2))
    inv = "INV-" + _Refs.six_digits(ctx, "inv_", hardware_order_id, "cancellation_fee", fee)
    bid = ctx.make_id("hb_", hardware_order_id, "hardware_cancellation_fee", fee)
    ctx.create("hardware_billing", bid, hardware_billing_entry_id=bid, hardware_order_id=hardware_order_id,
               customer_id=customer_id, event_type="hardware_cancellation_fee", amount_usd=fee,
               invoice_number=inv, posted_date=today, billing_period=today[:7], rma_number="",
               payment_reference="")
    return (f"Cancellation signed (request {rid}): order {hardware_order_id} is now cancelled; "
            f"cancellation fee invoice {inv} for {fee:.2f} USD booked.")


@tool(owner="agent", rw="write")
def revise_staged_quote_eb003c71(ctx: ToolContext, hardware_order_id: str, source_order_id: str,
                                 quote_total_usd: float) -> str:
    """Revise a client's quoted Staged Endpoint Order so that it takes over the line of another hardware
    order of the same units. One call keeps the staged quote's number and quoted status, re-dates it to
    today so a new validity period starts, sets its unit price to the source order's unit price and
    replaces its quote total with the total passed in. The client sees the staged quote re-issued with
    today's date and the new total, ready to sign.

    Args:
        hardware_order_id: Id class — reference number of the quoted Staged Endpoint Order being revised, as returned by the hardware order lookup for this client.
        source_order_id: Id class — reference number of the hardware order whose line the staged quote takes over, as returned by the hardware order lookup for this client.
        quote_total_usd: Fixed-format class — the revised quote total in USD, rounded half up to 2 decimal places.

    Returns:
        A confirmation sentence (string) naming the revised order reference, its quote number (HQ-
        followed by 6 digits), its new quote date (YYYY-MM-DD), its unit price and its revised quote
        total in USD with 2 decimal places; receiving it means the revision is on record.
    """
    src = ctx.find("hardware_orders", hardware_order_id=source_order_id)[0]
    quote = ctx.find("hardware_orders", hardware_order_id=hardware_order_id)[0]
    total = round(float(quote_total_usd), 2)
    today = ctx.now()[:10]
    ctx.update("hardware_orders", hardware_order_id, quote_date=today, unit_price_usd=src["unit_price_usd"],
               quote_total_usd=total)
    return (f"Quote {quote['quote_number']} (order {hardware_order_id}) revised: quote date {today}, "
            f"unit price {float(src['unit_price_usd']):.2f} USD, quote total {total:.2f} USD.")


@tool(owner="user", rw="write")
def sign_quote_approval_0590c0d2(ctx: ToolContext, customer_id: str, hardware_order_id: str, deposit_usd: float) -> str:
    """The authorized contact e-signs approval of a hardware quote together with the deposit it
    states. One call records the signed approval request, moves the order from quoted to approved
    with today's approval date, marks whether a deposit applies, and, when the deposit is above zero,
    books the deposit invoice, due on receipt, adding it to the amount the client owes on the order.
    The client sees the order approved and, where a deposit applies, a deposit invoice.

    Args:
        customer_id: Id class — client reference number of the verified client signing, as returned by the client profile lookup.
        hardware_order_id: Id class — reference number of the quoted hardware order being approved, as returned by the hardware order lookup or by the quote issue receipt.
        deposit_usd: Fixed-format class — the deposit the approval states, in USD, rounded half up to 2 decimal places; 0 when no deposit applies.

    Returns:
        A confirmation sentence (string) naming the signed request reference, the order reference, its
        new status approved and, where a deposit applies, the deposit invoice number (INV- followed by
        6 digits) and the deposit in USD with 2 decimal places; receiving it means the approval and any
        deposit invoice are on record.
    """
    order = ctx.find("hardware_orders", hardware_order_id=hardware_order_id)[0]
    today = ctx.now()[:10]
    dep = round(float(deposit_usd), 2)
    rid = ctx.make_id("hcr_", hardware_order_id, "quote_approval", dep)
    ctx.create("hardware_client_requests", rid, hardware_request_id=rid, customer_id=customer_id,
               hardware_order_id=hardware_order_id, request_type="quote_approval", return_type="not_applicable",
               requested_qty=0, request_status="signed", created_at=ctx.now())
    ctx.update("hardware_orders", hardware_order_id, status="approved", approved_date=today,
               deposit_required=dep > 0, balance_due_usd=round(float(order.get("balance_due_usd") or 0) + dep, 2))
    if dep <= 0:
        return f"Approval signed (request {rid}): order {hardware_order_id} is now approved; no deposit applies."
    inv = "INV-" + _Refs.six_digits(ctx, "inv_", hardware_order_id, "deposit", dep)
    bid = ctx.make_id("hb_", hardware_order_id, "hardware_deposit_invoice", dep)
    ctx.create("hardware_billing", bid, hardware_billing_entry_id=bid, hardware_order_id=hardware_order_id,
               customer_id=customer_id, event_type="hardware_deposit_invoice", amount_usd=dep,
               invoice_number=inv, posted_date=today, billing_period=today[:7], rma_number="",
               payment_reference="")
    return (f"Approval signed (request {rid}): order {hardware_order_id} is now approved; "
            f"deposit invoice {inv} for {dep:.2f} USD booked, due on receipt.")


@tool(owner="user", rw="write")
def sign_infrastructure_cancellation_1779b7d3(ctx: ToolContext, customer_id: str, hardware_order_id: str,
                                              fee_usd: float) -> str:
    """The authorized contact e-signs the cancellation of their own network or server hardware order whose
    distributor purchase order has already been placed and which has not shipped. One call records the
    signed cancellation request, moves the order to cancelled (cancelled after its purchase order,
    cancelled and closed today) and books the cancellation fee on the order's billing ledger as a new
    invoice, adding it to the amount the client owes on the order. The client sees the order shown as
    cancelled and a cancellation fee invoice for the amount signed.

    Args:
        customer_id: Id class — client reference number of the verified client signing, as returned by the client profile lookup.
        hardware_order_id: Id class — reference number of the client's hardware order being cancelled, as returned by the hardware order lookup for this client.
        fee_usd: Fixed-format class — the cancellation fee the client signs for, in USD, a positive amount rounded half up to 2 decimal places.

    Returns:
        A confirmation sentence (string) naming the signed request reference, the order reference, the
        order's new status cancelled, the cancellation fee invoice number (INV- followed by 6 digits) and
        the fee booked in USD with 2 decimal places; receiving it means the cancellation and its fee
        are on record.
    """
    order = ctx.find("hardware_orders", hardware_order_id=hardware_order_id)[0]
    today = ctx.now()[:10]
    fee = round(float(fee_usd), 2)
    rid = ctx.make_id("hcr_", hardware_order_id, "order_cancellation", fee)
    ctx.create("hardware_client_requests", rid, hardware_request_id=rid, customer_id=customer_id,
               hardware_order_id=hardware_order_id, request_type="order_cancellation",
               return_type="not_applicable", requested_qty=0, request_status="signed", created_at=ctx.now())
    ctx.update("hardware_orders", hardware_order_id, status="cancelled", cancellation_stage="after_po",
               cancelled_date=today, closed_date=today,
               balance_due_usd=round(float(order.get("balance_due_usd") or 0) + fee, 2))
    inv = "INV-" + _Refs.six_digits(ctx, "inv_", hardware_order_id, "cancellation_fee", fee)
    bid = ctx.make_id("hb_", hardware_order_id, "hardware_cancellation_fee", fee)
    ctx.create("hardware_billing", bid, hardware_billing_entry_id=bid, hardware_order_id=hardware_order_id,
               customer_id=customer_id, event_type="hardware_cancellation_fee", amount_usd=fee,
               invoice_number=inv, posted_date=today, billing_period=today[:7], rma_number="",
               payment_reference="")
    return (f"Cancellation signed (request {rid}): order {hardware_order_id} is now cancelled; "
            f"cancellation fee invoice {inv} for {fee:.2f} USD booked.")


@tool(owner="agent", rw="write")
def post_deposit_credit_9245a342(ctx: ToolContext, hardware_order_id: str, invoice_number: str,
                                 credit_usd: float) -> str:
    """Book an order credit on a cancelled hardware order that returns the deposit the client paid on it.
    One call adds an order credit entry, dated today, against the order's deposit invoice and reduces the
    amount the client owes on the order by the credit (a negative balance is a credit the accounting team
    refunds or carries). The client sees the deposit credit on the order's ledger.

    Args:
        hardware_order_id: Id class — reference number of the cancelled hardware order, as returned by the hardware order lookup for this client.
        invoice_number: Fixed-format class — the deposit invoice the credit is booked against, INV- followed by 6 digits, as shown on the order's billing ledger.
        credit_usd: Fixed-format class — the order credit in USD, a positive amount rounded half up to 2 decimal places.

    Returns:
        A confirmation sentence (string) naming the order credit reference, the order reference, the
        deposit invoice credited (INV- followed by 6 digits), the credit in USD with 2 decimal places and
        the order's new balance in USD with 2 decimal places; receiving it means the credit is on record.
    """
    order = ctx.find("hardware_orders", hardware_order_id=hardware_order_id)[0]
    today = ctx.now()[:10]
    amt = round(float(credit_usd), 2)
    bid = ctx.make_id("hb_", hardware_order_id, "hardware_order_credit", invoice_number, amt)
    ctx.create("hardware_billing", bid, hardware_billing_entry_id=bid, hardware_order_id=hardware_order_id,
               customer_id=order["customer_id"], event_type="hardware_order_credit", amount_usd=amt,
               invoice_number=invoice_number, posted_date=today, billing_period=today[:7], rma_number="",
               payment_reference="")
    balance = round(float(order.get("balance_due_usd") or 0) - amt, 2)
    ctx.update("hardware_orders", hardware_order_id, balance_due_usd=balance)
    return (f"Order credit {bid} booked on order {hardware_order_id} against {invoice_number}: "
            f"{amt:.2f} USD; order balance now {balance:.2f} USD.")


@tool(owner="agent", rw="write")
def reissue_lapsed_quote_93c9a091(ctx: ToolContext, hardware_order_id: str, unit_price_usd: float,
                                  quote_total_usd: float) -> str:
    """Re-issue a client's unsigned hardware quote whose validity period has ended. One call keeps the
    quote's number, units and distributor unit cost and its quoted status, re-dates it to today so a new
    validity period starts, and replaces its unit price and quote total with the values passed in. The
    client sees the quote re-issued with today's date, the new unit price and the new total, ready to sign.

    Args:
        hardware_order_id: Id class — reference number of the quoted hardware order being re-issued, as returned by the hardware order lookup for this client.
        unit_price_usd: Fixed-format class — the re-issued sell price per unit in USD, rounded half up to 2 decimal places.
        quote_total_usd: Fixed-format class — the re-issued quote total in USD, rounded half up to 2 decimal places.

    Returns:
        A confirmation sentence (string) naming the quote number (HQ- followed by 6 digits), the order
        reference, its new quote date (YYYY-MM-DD), its re-issued unit price and its re-issued quote total,
        both in USD with 2 decimal places; receiving it means the re-issue is on record.
    """
    quote = ctx.find("hardware_orders", hardware_order_id=hardware_order_id)[0]
    price = round(float(unit_price_usd), 2)
    total = round(float(quote_total_usd), 2)
    today = ctx.now()[:10]
    ctx.update("hardware_orders", hardware_order_id, quote_date=today, unit_price_usd=price, quote_total_usd=total)
    return (f"Quote {quote['quote_number']} (order {hardware_order_id}) re-issued: quote date {today}, "
            f"unit price {price:.2f} USD, quote total {total:.2f} USD.")


@tool(owner="user", rw="write")
def sign_build_approval_1b1ae884(ctx: ToolContext, customer_id: str, hardware_order_id: str,
                                 deposit_usd: float) -> str:
    """The authorized contact e-signs approval of a network or server hardware quote together with the
    deposit it states. One call records the signed approval request, moves the order from quoted to
    approved with today's approval date, marks whether a deposit applies, and, when the deposit is above
    zero, books the deposit invoice, due on receipt, adding it to the amount the client owes on the
    order. The client sees the order approved and, where a deposit applies, a deposit invoice.

    Args:
        customer_id: Id class — client reference number of the verified client signing, as returned by the client profile lookup.
        hardware_order_id: Id class — reference number of the quoted hardware order being approved, as returned by the hardware order lookup or by the quote re-issue receipt.
        deposit_usd: Fixed-format class — the deposit the approval states, in USD, rounded half up to 2 decimal places; 0 when no deposit applies.

    Returns:
        A confirmation sentence (string) naming the signed request reference, the order reference, its
        new status approved and, where a deposit applies, the deposit invoice number (INV- followed by
        6 digits) and the deposit in USD with 2 decimal places; receiving it means the approval and any
        deposit invoice are on record.
    """
    order = ctx.find("hardware_orders", hardware_order_id=hardware_order_id)[0]
    today = ctx.now()[:10]
    dep = round(float(deposit_usd), 2)
    rid = ctx.make_id("hcr_", hardware_order_id, "quote_approval", dep)
    ctx.create("hardware_client_requests", rid, hardware_request_id=rid, customer_id=customer_id,
               hardware_order_id=hardware_order_id, request_type="quote_approval", return_type="not_applicable",
               requested_qty=0, request_status="signed", created_at=ctx.now())
    ctx.update("hardware_orders", hardware_order_id, status="approved", approved_date=today,
               deposit_required=dep > 0, balance_due_usd=round(float(order.get("balance_due_usd") or 0) + dep, 2))
    if dep <= 0:
        return f"Approval signed (request {rid}): order {hardware_order_id} is now approved; no deposit applies."
    inv = "INV-" + _Refs.six_digits(ctx, "inv_", hardware_order_id, "deposit", dep)
    bid = ctx.make_id("hb_", hardware_order_id, "hardware_deposit_invoice", dep)
    ctx.create("hardware_billing", bid, hardware_billing_entry_id=bid, hardware_order_id=hardware_order_id,
               customer_id=customer_id, event_type="hardware_deposit_invoice", amount_usd=dep,
               invoice_number=inv, posted_date=today, billing_period=today[:7], rma_number="",
               payment_reference="")
    return (f"Approval signed (request {rid}): order {hardware_order_id} is now approved; "
            f"deposit invoice {inv} for {dep:.2f} USD booked, due on receipt.")

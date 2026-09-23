"""Hidden task tools for the Belrose Design Studio commission desk.

Each function performs exactly one atomic write on a customer's commission file. The names
are discoverable only through the studio's own published rules, and every call is reached
through the unlock/call meta tools. Nothing here aggregates history, prices anything or
judges whether a rule is met: the figures are worked out by the person placing the call.
"""

from erlbench import ToolContext, tool


@tool(owner="user", rw="write")
def confirm_specification_change_363ec738(ctx: ToolContext, custom_order_id: str,
                                          change_order_reference: str,
                                          agreed_change_value: float,
                                          effective_date: str) -> str:
    """Let the customer put their own agreement to a change of their commission's specification on
    the design studio's request record. One call adds a request record standing as confirmed by the
    customer against the named change, carrying the sum the customer accepts for the work the change
    puts back on the bench and the date they wish the change to take effect from. Nothing else on
    the commission moves: the quoted total, the balance and the production stage are untouched, and
    what the customer sees afterwards is a confirmed change request on their file that the studio
    may act on. The call has completed when the confirmation text below comes back naming the new
    request record.

    Args:
        custom_order_id: Id class — the reference number of the commission record the change concerns, as read from the design studio's commission lookup for this customer.
        change_order_reference: Fixed-format class — the reference of the change being agreed, written as CH- followed by six digits, e.g. CH-208551; copy it from the change request already standing on the studio's request record for this commission.
        agreed_change_value: Fixed-format class — the sum the customer accepts for the work the change puts back on the bench, in USD, to 2 decimal places, rounded half up, with no thousands separator and no currency symbol.
        effective_date: Fixed-format class — the calendar date the customer wishes the change to take effect from, written as YYYY-MM-DD in the studio's own local time, never left empty.

    Returns:
        A single line of text confirming the request was taken. It names the new request record's
        reference number, the change order reference it concerns, the sum confirmed in USD to two
        decimal places and the effective date as YYYY-MM-DD. Receiving that line is what indicates
        the confirmation now stands on the studio's request record.
    """
    rid = ctx.make_id("creq_", custom_order_id, change_order_reference, agreed_change_value,
                      effective_date)
    ctx.create("custom_intake", rid, custom_request_id=rid, custom_order_id=custom_order_id,
               request_type="change_order", request_status="customer_confirmed",
               change_order_reference=change_order_reference,
               requested_amount=round(float(agreed_change_value), 2),
               effective_date=effective_date, created_at=ctx.now())
    return (f"Change {change_order_reference} confirmed by the customer on request {rid} at "
            f"{round(float(agreed_change_value), 2)} USD, effective {effective_date}.")


@tool(owner="agent", rw="write")
def charge_specification_change_ec6b5130(ctx: ToolContext, custom_order_id: str,
                                         commission_reference: str,
                                         change_order_reference: str,
                                         change_charge_amount: float) -> str:
    """Price an agreed change of specification onto a customer's commission. One call books a single
    charge entry against the commission for the named change, raising what the customer owes on that
    commission by the amount given and leaving the quoted total, the design revisions and the
    production stage exactly as they were. The customer sees the charge on their commission file
    against the change reference it prices, and the call has completed when the confirmation text
    below comes back naming the new entry.

    Args:
        custom_order_id: Id class — the reference number of the commission record the charge is booked against, as read from the design studio's commission lookup for this customer.
        commission_reference: Fixed-format class — the reference the customer is given for the commission being charged, written as CO- followed by six digits, e.g. CO-509314, exactly as it stands on the commission record.
        change_order_reference: Fixed-format class — the reference of the change this charge prices, written as CH- followed by six digits, e.g. CH-208551, exactly as it stands on the studio's request record.
        change_charge_amount: Fixed-format class — the amount booked against the commission for the change, in USD, to 2 decimal places, rounded half up, positive, with no thousands separator and no currency symbol.

    Returns:
        A single line of text confirming the charge was booked. It names the new commission entry's
        reference number, the commission reference it was booked to, the change order reference it
        prices and the amount booked in USD to two decimal places. Receiving that line is what
        indicates the commission now carries the charge.
    """
    rid = ctx.make_id("cchg_", custom_order_id, commission_reference, change_order_reference,
                      change_charge_amount)
    ctx.create("custom_ledger", rid, custom_entry_id=rid, custom_order_id=custom_order_id,
               event_type="custom_change_order_charged", posted_date=ctx.now()[:10],
               amount=round(float(change_charge_amount), 2),
               charge_reason="specification_change", milestone_code="not_applicable",
               revision_number=0, payment_stage="not_applicable",
               payment_channel="not_applicable",
               change_order_reference=change_order_reference, metal_price_per_gram=0.0,
               billing_period=ctx.now()[:7])
    return (f"Change {change_order_reference} priced onto commission {commission_reference} as "
            f"entry {rid} at {round(float(change_charge_amount), 2)} USD.")


@tool(owner="agent", rw="write")
def charge_metal_revaluation_a0bcb90e(ctx: ToolContext, custom_order_id: str,
                                      commission_reference: str,
                                      metal_adjustment_amount: float) -> str:
    """Book a repricing for a movement in the metal market against a customer's commission. One call
    adds a single adjustment entry to the commission under the metal market reason, raising what the
    customer owes on that commission by the amount given while the quoted total, the design revisions
    and the production stage stay exactly as they are. The customer sees the adjustment on their
    commission file, and the call has completed when the confirmation text below comes back naming
    the new entry.

    Args:
        custom_order_id: Id class — the reference number of the commission record the adjustment is booked against, as read from the design studio's commission lookup for this customer.
        commission_reference: Fixed-format class — the reference the customer is given for the commission being repriced, written as CO- followed by six digits, e.g. CO-509314, exactly as it stands on the commission record.
        metal_adjustment_amount: Fixed-format class — the amount booked against the commission for the movement in the metal market, in USD, to 2 decimal places, rounded half up, positive, with no thousands separator and no currency symbol.

    Returns:
        A single line of text confirming the adjustment was booked. It names the new commission
        entry's reference number, the commission reference it was booked to and the amount booked in
        USD to two decimal places. Receiving that line is what indicates the commission now carries
        the adjustment.
    """
    rid = ctx.make_id("cmkt_", custom_order_id, commission_reference, metal_adjustment_amount)
    ctx.create("custom_ledger", rid, custom_entry_id=rid, custom_order_id=custom_order_id,
               event_type="custom_price_adjustment_charged", posted_date=ctx.now()[:10],
               amount=round(float(metal_adjustment_amount), 2), charge_reason="metal_market",
               milestone_code="not_applicable", revision_number=0,
               payment_stage="not_applicable", payment_channel="not_applicable",
               change_order_reference="", billing_period=ctx.now()[:7])
    return (f"Metal market repricing booked to commission {commission_reference} as entry {rid} at "
            f"{round(float(metal_adjustment_amount), 2)} USD.")


@tool(owner="user", rw="write")
def confirm_commission_closure_3c2f355d(ctx: ToolContext, custom_order_id: str,
                                        customer_id: str,
                                        commission_reference: str,
                                        retained_amount: float,
                                        effective_date: str) -> str:
    """Let the customer close their own commission on the design studio's request record. One call adds
    a request record standing as confirmed by the customer against that commission and against the
    customer's own file, carrying the sum the customer accepts the studio will keep and the date they
    wish the closure to take effect from. The commission's own quoted total, balance and stage are
    untouched; what the customer sees afterwards is a confirmed closure request on their file that the
    studio may settle against. The call has completed when the confirmation text below comes back
    naming the new request record.

    Args:
        custom_order_id: Id class — the reference number of the commission record being closed, as read from the design studio's commission lookup for this customer.
        customer_id: Id class — the reference number of the customer closing the commission, as read from the customer lookup that found the caller.
        commission_reference: Fixed-format class — the reference the customer is given for the commission being closed, written as CO- followed by six digits, e.g. CO-509314, exactly as it stands on the commission record.
        retained_amount: Fixed-format class — the sum the customer accepts the studio will keep on the closure, in USD, to 2 decimal places, rounded half up, positive, with no thousands separator and no currency symbol.
        effective_date: Fixed-format class — the calendar date the customer wishes the closure to take effect from, written as YYYY-MM-DD in the studio's own local time, never left empty.

    Returns:
        A single line of text confirming the closure request was taken. It names the new request
        record's reference number, the commission reference it concerns, the sum confirmed in USD to
        two decimal places and the effective date as YYYY-MM-DD. Receiving that line is what indicates
        the confirmation now stands on the studio's request record.
    """
    rid = ctx.make_id("clos_", custom_order_id, customer_id, commission_reference, retained_amount,
                      effective_date)
    ctx.create("custom_intake", rid, custom_request_id=rid, customer_id=customer_id,
               custom_order_id=custom_order_id,
               request_type="cancellation", request_status="customer_confirmed",
               change_order_reference="",
               requested_amount=round(float(retained_amount), 2),
               effective_date=effective_date, created_at=ctx.now())
    return (f"Closure of commission {commission_reference} confirmed by the customer on request {rid}, "
            f"studio keeping {round(float(retained_amount), 2)} USD, effective {effective_date}.")


@tool(owner="agent", rw="write")
def issue_commission_refund_b90496cb(ctx: ToolContext, custom_order_id: str,
                                     commission_reference: str, source_entry_id: str,
                                     refund_amount: float) -> str:
    """Pay money back to a customer on a commission being closed. One call adds a single refund entry
    to the commission against the earlier payment being returned, reducing what the customer owes on
    that commission by the amount given and putting that money back to the customer on the studio's
    own refund run. The quoted total, the design revisions and the production stage stay exactly as
    they are. The customer sees the refund on their commission file against the payment it answers,
    and the call has completed when the confirmation text below comes back naming the new entry.

    Args:
        custom_order_id: Id class — the reference number of the commission record the refund is booked against, as read from the design studio's commission lookup for this customer.
        commission_reference: Fixed-format class — the reference the customer is given for the commission being refunded, written as CO- followed by six digits, e.g. CO-509314, exactly as it stands on the commission record.
        source_entry_id: Id class — the reference number of the earlier commission entry whose money is being returned, as read from the commission's own entry lookup.
        refund_amount: Fixed-format class — the amount returned to the customer, in USD, to 2 decimal places, rounded half up, positive, with no thousands separator and no currency symbol.

    Returns:
        A single line of text confirming the refund was booked. It names the new commission entry's
        reference number, the commission reference it was booked to, the earlier entry it answers and
        the amount returned in USD to two decimal places. Receiving that line is what indicates the
        money has been put back to the customer.
    """
    rid = ctx.make_id("cref_", custom_order_id, commission_reference, source_entry_id, refund_amount)
    ctx.create("custom_ledger", rid, custom_entry_id=rid, custom_order_id=custom_order_id,
               event_type="custom_refund_issued", posted_date=ctx.now()[:10],
               amount=-round(float(refund_amount), 2), charge_reason="not_applicable",
               milestone_code="not_applicable", revision_number=0, payment_stage="refund",
               payment_channel="bank_transfer", change_order_reference="",
               source_entry_id=source_entry_id, billing_period=ctx.now()[:7])
    return (f"Refund of {round(float(refund_amount), 2)} USD booked to commission "
            f"{commission_reference} as entry {rid}, answering entry {source_entry_id}.")

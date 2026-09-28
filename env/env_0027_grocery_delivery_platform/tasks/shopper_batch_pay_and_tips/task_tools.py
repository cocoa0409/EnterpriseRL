"""Hidden task tools of the shopper_batch_pay_and_tips difficulty (category batch, Cartwise Shopper Batches).

Each tool performs one atomic business write on a shopper batch, its earnings entries or the shopper's pay
disputes. The values passed in are worked out by the caller from the published pay rules; no tool computes a
pay figure, checks eligibility or refuses on a business condition.
"""

from erlbench import ToolContext, tool

@tool(owner="agent", rw="write")
def post_pay_component_6b97a1a8(ctx: ToolContext, batch_id: str, pay_component: str, order_id: str,
                                amount_usd: float) -> str:
    """Credit one pay component to a shopper batch on the shopper's behalf. One call books a single pay-component
    earnings entry on the named batch with today's posting date, and raises the batch's earnings (the shopper's
    earnings on the batch including tips) by the same amount; the new entry and the raised earnings are visible at
    once in the batch's earnings entries and in the shopper's pay breakdown. Success is confirmed by a receipt
    carrying the new entry's reference number.

    Args:
        batch_id: Id class — the batch number of the shopper batch being paid, as returned by the batch lookup for
            the verified shopper.
        pay_component: Enum class — which pay component the entry credits; exactly one of:
            batch_base — the fixed pay for completing the batch;
            per_order — the pay for one order carried beyond the first;
            per_item — the pay for the item units shopped;
            staging — the pay for an order staged for pickup or handoff;
            mileage — the pay for estimated route miles beyond the included miles;
            long_distance — the bonus for an estimated route beyond the long-distance threshold;
            heavy_pay — the pay for heavy units once heavy pay starts;
            wait_time — the pay for recorded waiting beyond the unpaid minutes;
            peak_boost — the boost shown on the accepted offer;
            quality_bonus — the bonus for an order rated five stars in time with no item refund;
            return_pay — the pay for an order returned to the store after the required contact attempts;
            minimum_topup — the amount that lifts the batch's pay before tips to its minimum;
            cancellation_pay — the pay for a batch whose every order was canceled after shopping started.
        order_id: Id class — the order number the component belongs to for a per-order component, as returned by
            the order lookup for the batch; pass an empty string "" for a batch-level component, which belongs to
            no single order.
        amount_usd: Fixed-format class — the amount credited, in USD, a positive number with 2 decimal places,
            already rounded to the cent by the caller; the tool stores it rounded to 2 decimal places.

    Returns:
        A text receipt of a dictionary with: batch_event_id (string, reference number of the new earnings entry),
        batch_id (string, the batch paid), pay_component (string, the component credited), amount_usd (number,
        USD with 2 decimal places, the amount credited), event_date (string, YYYY-MM-DD posting date) and
        batch_earnings_usd (number, USD with 2 decimal places, the batch's earnings once the credit is booked).
        Receiving the batch_event_id means the credit is booked.
    """
    amount = round(float(amount_usd), 2)
    batch = ctx.find("batches", batch_id=batch_id)
    rid = ctx.make_id("bev_", batch_id, pay_component, order_id, amount)
    ctx.create("batch_events", rid, batch_event_id=rid, batch_id=batch_id, customer_id=(batch[0].get("customer_id") if batch else None),
               event_type="batch_pay_posted", pay_component=pay_component, order_id=order_id or None,
               amount_usd=amount, event_date=ctx.now()[:10])
    total = round(float((batch[0].get("earnings_usd") if batch else 0) or 0) + amount, 2)
    ctx.update("batches", batch_id, earnings_usd=total)
    return str({"batch_event_id": rid, "batch_id": batch_id, "pay_component": pay_component,
                "amount_usd": amount, "event_date": ctx.now()[:10], "batch_earnings_usd": total})


@tool(owner="agent", rw="write")
def reverse_duplicate_pay_33b66c45(ctx: ToolContext, batch_id: str, source_event_id: str, amount_usd: float) -> str:
    """Take back pay that was credited twice on a shopper batch. One call books a single pay reversal on the named
    batch against the one pay entry it names, with the ground duplicate pay and today's date, and lowers the
    batch's earnings by the amount taken back; the reversal appears at once among the batch's earnings entries and
    in the shopper's pay breakdown. Success is confirmed by a receipt carrying the reversal's reference number.

    Args:
        batch_id: Id class — the batch number of the shopper batch the reversal is booked on, as returned by the
            batch lookup for the verified shopper.
        source_event_id: Id class — the reference number of the pay entry being taken back, as returned by the
            batch earnings-entry lookup for that batch.
        amount_usd: Fixed-format class — the amount taken back, in USD, a positive number with 2 decimal places,
            already rounded to the cent by the caller; the tool stores it rounded to 2 decimal places.

    Returns:
        A text receipt of a dictionary with: batch_event_id (string, reference number of the reversal entry),
        batch_id (string, the batch), source_event_id (string, the pay entry taken back), reversal_reason (string,
        always duplicate_pay), amount_usd (number, USD with 2 decimal places, the amount taken back), event_date
        (string, YYYY-MM-DD) and batch_earnings_usd (number, USD with 2 decimal places, the batch's earnings once
        the reversal is booked). Receiving the batch_event_id means the reversal is booked.
    """
    amount = round(float(amount_usd), 2)
    batch = ctx.find("batches", batch_id=batch_id)
    rid = ctx.make_id("bev_", batch_id, source_event_id, amount)
    ctx.create("batch_events", rid, batch_event_id=rid, batch_id=batch_id, customer_id=(batch[0].get("customer_id") if batch else None),
               event_type="batch_pay_reversed", reversal_reason="duplicate_pay", source_event_id=source_event_id,
               amount_usd=amount, event_date=ctx.now()[:10])
    total = round(float((batch[0].get("earnings_usd") if batch else 0) or 0) - amount, 2)
    ctx.update("batches", batch_id, earnings_usd=total)
    return str({"batch_event_id": rid, "batch_id": batch_id, "source_event_id": source_event_id,
                "reversal_reason": "duplicate_pay", "amount_usd": amount, "event_date": ctx.now()[:10],
                "batch_earnings_usd": total})


@tool(owner="user", rw="write")
def submit_pay_dispute_0c2b2ed2(ctx: ToolContext, batch_id: str, dispute_reason: str,
                                claimed_amount_usd: float) -> str:
    """The shopper submits a pay dispute on one of her own shopper batches. One call files a single dispute on the
    named batch with the reason and the amount the shopper claims, stamped with the current time and standing as
    submitted; the shopper sees the new dispute and its reference number among her pay disputes at once. Success is
    confirmed by a receipt carrying the dispute's reference number.

    Args:
        batch_id: Id class — the batch number of the shopper's own batch being disputed, as read out to the
            shopper from the batch lookup.
        dispute_reason: Enum class — what the shopper says is missing; exactly one of:
            shown_pay_shortfall — the batch paid less before tips than its accepted offer showed;
            mileage_underpaid — the miles driven exceeded the estimated route beyond the tolerance and mileage pay
            fell short;
            heavy_pay_missing — heavy pay for the batch's heavy units was not paid;
            wait_pay_missing — waiting-time pay for recorded waiting was not paid;
            boost_missing — the boost shown on the offer was not paid;
            cancellation_pay_missing — the pay owed for a batch canceled after shopping started was not paid;
            return_pay_missing — the pay for an order returned to the store was not paid.
        claimed_amount_usd: Fixed-format class — the amount the shopper claims is owed, in USD, a positive number
            with 2 decimal places; the tool stores it rounded to 2 decimal places.

    Returns:
        A text receipt of a dictionary with: batch_pay_dispute_id (string, reference number of the new dispute),
        batch_id (string, the batch disputed), dispute_reason (string, the reason filed), claimed_amount_usd
        (number, USD with 2 decimal places), dispute_status (string, always submitted) and created_at (string,
        YYYY-MM-DDTHH:MM:SS submission time). Receiving the batch_pay_dispute_id means the dispute is filed.
    """
    amount = round(float(claimed_amount_usd), 2)
    batch = ctx.find("batches", batch_id=batch_id)
    rid = ctx.make_id("bpd_", batch_id, dispute_reason, amount)
    ctx.create("batch_pay_disputes", rid, batch_pay_dispute_id=rid, customer_id=(batch[0].get("customer_id") if batch else None),
               batch_id=batch_id, dispute_reason=dispute_reason, claimed_amount_usd=amount,
               dispute_status="submitted", created_at=ctx.now()[:19].replace(" ", "T"))
    return str({"batch_pay_dispute_id": rid, "batch_id": batch_id, "dispute_reason": dispute_reason,
                "claimed_amount_usd": amount, "dispute_status": "submitted", "created_at": ctx.now()[:19].replace(" ", "T")})


@tool(owner="agent", rw="write")
def book_pay_adjustment_e97659e1(ctx: ToolContext, batch_id: str, shopper_account_id: str, batch_pay_dispute_id: str,
                                 adjustment_reason: str, amount_usd: float) -> str:
    """Approve a shopper's pay dispute on a completed batch by crediting a pay adjustment. One call books a single
    pay adjustment on the named batch with the reason given, today's date and the dispute it answers, marks that
    dispute approved, and raises the batch's earnings by the amount credited; the adjustment and the approved
    dispute are visible to the shopper at once. Success is confirmed by a receipt carrying the adjustment's
    reference number.

    Args:
        batch_id: Id class — the batch number of the shopper batch the adjustment is credited to, as returned by
            the batch lookup for the verified shopper.
        shopper_account_id: Id class — the shopper contractor account number the adjustment counts against, as
            returned by the shopper-account lookup and shown on the batch.
        batch_pay_dispute_id: Id class — the reference number of the shopper's pay dispute the adjustment answers,
            as returned when the dispute was filed or by the pay-dispute lookup.
        adjustment_reason: Enum class — the controlled reason of the adjustment; exactly one of:
            shown_pay_shortfall — pay before tips fell short of the pay shown on the accepted offer;
            mileage_underpaid — mileage pay fell short of the miles driven beyond the tolerance;
            heavy_pay_missing — heavy pay was owed and not paid;
            wait_pay_missing — waiting-time pay was owed and not paid;
            boost_missing — the boost shown on the offer was owed and not paid;
            cancellation_pay_missing — pay owed for a batch canceled after shopping started was not paid;
            return_pay_missing — pay for an order returned to the store was owed and not paid.
        amount_usd: Fixed-format class — the amount credited, in USD, a positive number with 2 decimal places,
            already rounded to the cent by the caller; the tool stores it rounded to 2 decimal places.

    Returns:
        A text receipt of a dictionary with: batch_event_id (string, reference number of the adjustment entry),
        batch_id (string, the batch), adjustment_reason (string, the reason booked), batch_pay_dispute_id (string,
        the dispute answered), dispute_status (string, always approved), amount_usd (number, USD with 2 decimal
        places, the amount credited), event_date (string, YYYY-MM-DD) and batch_earnings_usd (number, USD with 2
        decimal places, the batch's earnings once the credit is booked). Receiving the batch_event_id means the
        adjustment is booked and the dispute approved.
    """
    amount = round(float(amount_usd), 2)
    batch = ctx.find("batches", batch_id=batch_id)
    rid = ctx.make_id("bev_", batch_id, shopper_account_id, batch_pay_dispute_id, adjustment_reason, amount)
    ctx.create("batch_events", rid, batch_event_id=rid, batch_id=batch_id, customer_id=(batch[0].get("customer_id") if batch else None),
               event_type="batch_pay_adjusted", adjustment_reason=adjustment_reason,
               batch_pay_dispute_id=batch_pay_dispute_id, amount_usd=amount, event_date=ctx.now()[:10])
    ctx.update("batch_pay_disputes", batch_pay_dispute_id, dispute_status="approved")
    total = round(float((batch[0].get("earnings_usd") if batch else 0) or 0) + amount, 2)
    ctx.update("batches", batch_id, earnings_usd=total)
    return str({"batch_event_id": rid, "batch_id": batch_id, "adjustment_reason": adjustment_reason,
                "batch_pay_dispute_id": batch_pay_dispute_id, "dispute_status": "approved", "amount_usd": amount,
                "event_date": ctx.now()[:10], "batch_earnings_usd": total})


@tool(owner="agent", rw="write")
def reverse_undelivered_pay_ec14645c(ctx: ToolContext, batch_id: str, source_event_id: str, amount_usd: float) -> str:
    """Take back pay a shopper batch received for an order that was verified as not delivered. One call books a
    single pay reversal on the named batch against the one pay entry it names, with the ground order not delivered
    (verified) and today's date, and lowers the batch's earnings by the amount taken back; the reversal appears at
    once among the batch's earnings entries and in the shopper's pay breakdown. Success is confirmed by a receipt
    carrying the reversal's reference number.

    Args:
        batch_id: Id class — the batch number of the shopper batch the reversal is booked on, as returned by the
            batch lookup for the verified shopper.
        source_event_id: Id class — the reference number of the pay entry the amount is taken back from, as
            returned by the batch earnings-entry lookup for that batch.
        amount_usd: Fixed-format class — the amount taken back, in USD, a positive number with 2 decimal places,
            already rounded to the cent by the caller; the tool stores it rounded to 2 decimal places.

    Returns:
        A text receipt of a dictionary with: batch_event_id (string, reference number of the reversal entry),
        batch_id (string, the batch), source_event_id (string, the pay entry taken back from), reversal_reason
        (string, always order_not_delivered_verified), amount_usd (number, USD with 2 decimal places, the amount
        taken back), event_date (string, YYYY-MM-DD) and batch_earnings_usd (number, USD with 2 decimal places, the
        batch's earnings once the reversal is booked). Receiving the batch_event_id means the reversal is booked.
    """
    amount = round(float(amount_usd), 2)
    batch = ctx.find("batches", batch_id=batch_id)
    rid = ctx.make_id("bev_", batch_id, source_event_id, "order_not_delivered_verified", amount)
    ctx.create("batch_events", rid, batch_event_id=rid, batch_id=batch_id,
               customer_id=(batch[0].get("customer_id") if batch else None), event_type="batch_pay_reversed",
               reversal_reason="order_not_delivered_verified", source_event_id=source_event_id,
               amount_usd=amount, event_date=ctx.now()[:10])
    total = round(float((batch[0].get("earnings_usd") if batch else 0) or 0) - amount, 2)
    ctx.update("batches", batch_id, earnings_usd=total)
    return str({"batch_event_id": rid, "batch_id": batch_id, "source_event_id": source_event_id,
                "reversal_reason": "order_not_delivered_verified", "amount_usd": amount,
                "event_date": ctx.now()[:10], "batch_earnings_usd": total})


@tool(owner="user", rw="write")
def submit_mileage_claim_29030431(ctx: ToolContext, batch_id: str, claimed_amount_usd: float) -> str:
    """The shopper files a mileage dispute on one of her own completed shopper batches, saying the miles she drove
    ran beyond what her mileage pay covers. One call files a single pay dispute with the reason mileage underpaid on
    the named batch, carrying the amount the shopper claims, stamped with the current time and standing as
    submitted; the shopper sees the new dispute and its reference number among her pay disputes at once. Success is
    confirmed by a receipt carrying the dispute's reference number.

    Args:
        batch_id: Id class — the batch number of the shopper's own batch the mileage dispute is filed on, as read out
            to the shopper from the batch lookup.
        claimed_amount_usd: Fixed-format class — the amount the shopper claims is owed for mileage, in USD, a
            positive number with 2 decimal places; the tool stores it rounded to 2 decimal places.

    Returns:
        A text receipt of a dictionary with: batch_pay_dispute_id (string, reference number of the new dispute),
        batch_id (string, the batch disputed), dispute_reason (string, always mileage_underpaid),
        claimed_amount_usd (number, USD with 2 decimal places), dispute_status (string, always submitted) and
        created_at (string, YYYY-MM-DDTHH:MM:SS submission time). Receiving the batch_pay_dispute_id means the
        mileage dispute is filed.
    """
    amount = round(float(claimed_amount_usd), 2)
    batch = ctx.find("batches", batch_id=batch_id)
    rid = ctx.make_id("bpd_", batch_id, "mileage_underpaid", amount)
    ctx.create("batch_pay_disputes", rid, batch_pay_dispute_id=rid,
               customer_id=(batch[0].get("customer_id") if batch else None), batch_id=batch_id,
               dispute_reason="mileage_underpaid", claimed_amount_usd=amount, dispute_status="submitted",
               created_at=ctx.now()[:19].replace(" ", "T"))
    return str({"batch_pay_dispute_id": rid, "batch_id": batch_id, "dispute_reason": "mileage_underpaid",
                "claimed_amount_usd": amount, "dispute_status": "submitted",
                "created_at": ctx.now()[:19].replace(" ", "T")})


@tool(owner="agent", rw="write")
def book_mileage_adjustment_6fe9f3bb(ctx: ToolContext, batch_id: str, shopper_account_id: str,
                                     batch_pay_dispute_id: str, adjustment_reason: str, amount_usd: float) -> str:
    """Approve a shopper's mileage dispute on a completed batch by crediting a mileage pay adjustment. One call books
    a single pay adjustment on the named batch with the reason given, today's date and the dispute it answers,
    marks that dispute approved, and raises the batch's earnings by the amount credited; the adjustment and the
    approved dispute are visible to the shopper at once. Success is confirmed by a receipt carrying the adjustment's
    reference number.

    Args:
        batch_id: Id class — the batch number of the shopper batch the adjustment is credited to, as returned by
            the batch lookup for the verified shopper.
        shopper_account_id: Id class — the shopper contractor account number the adjustment counts against, as
            returned by the shopper-account lookup and shown on the batch.
        batch_pay_dispute_id: Id class — the reference number of the shopper's mileage dispute the adjustment
            answers, as returned when the dispute was filed or by the pay-dispute lookup.
        adjustment_reason: Enum class — the controlled reason of the adjustment; exactly one of:
            shown_pay_shortfall — pay before tips fell short of the pay shown on the accepted offer;
            mileage_underpaid — mileage pay fell short of the miles driven beyond the tolerance;
            heavy_pay_missing — heavy pay was owed and not paid;
            wait_pay_missing — waiting-time pay was owed and not paid;
            boost_missing — the boost shown on the offer was owed and not paid;
            cancellation_pay_missing — pay owed for a batch canceled after shopping started was not paid;
            return_pay_missing — pay for an order returned to the store was owed and not paid.
        amount_usd: Fixed-format class — the amount credited, in USD, a positive number with 2 decimal places,
            already rounded to the cent by the caller; the tool stores it rounded to 2 decimal places.

    Returns:
        A text receipt of a dictionary with: batch_event_id (string, reference number of the adjustment entry),
        batch_id (string, the batch), adjustment_reason (string, the reason booked), batch_pay_dispute_id (string,
        the dispute answered), dispute_status (string, always approved), amount_usd (number, USD with 2 decimal
        places, the amount credited), event_date (string, YYYY-MM-DD) and batch_earnings_usd (number, USD with 2
        decimal places, the batch's earnings once the credit is booked). Receiving the batch_event_id means the
        adjustment is booked and the dispute approved.
    """
    amount = round(float(amount_usd), 2)
    batch = ctx.find("batches", batch_id=batch_id)
    rid = ctx.make_id("bev_", batch_id, shopper_account_id, batch_pay_dispute_id, adjustment_reason, amount)
    ctx.create("batch_events", rid, batch_event_id=rid, batch_id=batch_id,
               customer_id=(batch[0].get("customer_id") if batch else None), event_type="batch_pay_adjusted",
               adjustment_reason=adjustment_reason, batch_pay_dispute_id=batch_pay_dispute_id, amount_usd=amount,
               event_date=ctx.now()[:10])
    ctx.update("batch_pay_disputes", batch_pay_dispute_id, dispute_status="approved")
    total = round(float((batch[0].get("earnings_usd") if batch else 0) or 0) + amount, 2)
    ctx.update("batches", batch_id, earnings_usd=total)
    return str({"batch_event_id": rid, "batch_id": batch_id, "adjustment_reason": adjustment_reason,
                "batch_pay_dispute_id": batch_pay_dispute_id, "dispute_status": "approved", "amount_usd": amount,
                "event_date": ctx.now()[:10], "batch_earnings_usd": total})

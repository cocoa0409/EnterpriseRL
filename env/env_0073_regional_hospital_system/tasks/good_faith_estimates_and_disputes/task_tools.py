"""Hidden task tools for good_faith_estimates_and_disputes (category estimate).

Each tool performs one atomic write on a Riverbend self-pay package estimate and is reached
only through the unlock_* -> call_* meta-tools; every tool name is registered as the
target_tool of one extended policy in estimate.extended.yaml.
"""

from erlbench import ToolContext, tool


class _Cents:
    """Half-up rounding of a non-negative dollar figure to the cent (an exact half cent goes up)."""

    @staticmethod
    def half_up(value) -> float:
        v = float(value)
        sign = -1 if v < 0 else 1
        return sign * int(abs(v) * 100 + 0.5 + 0.000001) / 100



@tool(owner="user", rw="write")
def pay_surgery_package_deposit_c16ec91c(ctx: ToolContext, estimate_id: str, amount: float) -> str:
    """The patient pays, in person and with their own card or bank account, the initial deposit on their
    Riverbend self-pay outpatient surgery package booking. One call records one initial-deposit payment
    against that booking: a new deposit collection of the stated amount is added to the booking's deposit
    activity under a newly issued payment confirmation number, and the deposits held on the booking rise by
    the same amount. The patient sees the confirmation number and the new deposits-held figure at once; the
    receipt line beginning "Payment accepted" is the sign that the payment was recorded.

    Args:
        estimate_id: Id class — the reference number of the patient's outpatient surgery package estimate,
            as listed by the estimate lookup for this patient.
        amount: Fixed-format class — the initial deposit the patient pays, in USD, 2 decimal places, positive
            magnitude (USD, 2 decimal places, positive magnitude); the value is rounded half-up to the cent when
            recorded, and an empty value is not accepted.

    Returns:
        A text receipt "Payment accepted: deposit_txn_id=..., payment_reference=..., deposit_stage=...,
        amount=..., deposit_held_usd=..." where deposit_txn_id is the reference number of the new deposit
        collection, payment_reference is the payment confirmation number issued for this payment (PMT- followed
        by 7 digits), deposit_stage is INITIAL_DEPOSIT, amount is the amount recorded in USD with 2 decimal
        places, and deposit_held_usd is the deposits now held on the booking in USD with 2 decimal places.
    """
    rid = ctx.make_id("edp_", estimate_id, "INITIAL_DEPOSIT", amount)
    reference = "PMT-55" + str(int(rid[-10:], 16) % 100000).zfill(5)
    est = ctx.find("price_estimates", estimate_id=estimate_id)
    customer_id = est[0].get("customer_id") if est else ""
    held = float(est[0].get("deposit_held_usd") or 0) if est else 0.0
    if amount is None or str(amount).strip() == "":
        return "Error: amount must be a positive USD figure with 2 decimal places."
    paid = _Cents.half_up(amount)
    if not est:
        return f"Error: no estimate {estimate_id}; pass the estimate reference number as listed by the estimate lookup."
    if paid <= 0:
        return "Error: amount must be a positive USD figure with 2 decimal places."
    ctx.create("estimate_transactions", rid, estimate_txn_id=rid, estimate_id=estimate_id, customer_id=customer_id,
               event_type="estimate_deposit_collected", deposit_stage="INITIAL_DEPOSIT", payment_reference=reference,
               amount=paid, posting_date=ctx.now()[:10])
    ctx.update("price_estimates", estimate_id, deposit_held_usd=round(held + paid, 2))
    return (f"Payment accepted: deposit_txn_id={rid}, payment_reference={reference}, deposit_stage=INITIAL_DEPOSIT, "
            f"amount={paid:.2f}, deposit_held_usd={round(held + paid, 2):.2f}")


@tool(owner="agent", rw="write")
def retain_late_change_fee_0cd5c1f6(ctx: ToolContext, estimate_id: str, source_estimate_txn_id: str, amount: float) -> str:
    """Keep the late-change fee on a Riverbend self-pay outpatient surgery package booking that the patient
    moved to a new date with short notice. One call records one retained-fee entry on the booking, drawn on
    the named deposit collection: the fee amount is taken out of the deposits held on the booking and kept
    by Riverbend, and the deposits held fall by that amount. The patient can be told the fee kept and the new
    deposits-held figure; the receipt line beginning "Fee retained" confirms the entry was recorded.

    Args:
        estimate_id: Id class — the reference number of the patient's outpatient surgery package estimate,
            as listed by the estimate lookup for this patient.
        source_estimate_txn_id: Id class — the reference number of the deposit collection on that booking the
            fee is drawn on, as listed in the booking's deposit activity.
        amount: Fixed-format class — the fee kept, in USD, 2 decimal places, positive magnitude (USD, 2 decimal
            places, positive magnitude); the value is rounded half-up to the cent when recorded, and an empty
            value is not accepted.

    Returns:
        A text receipt "Fee retained: fee_txn_id=..., source_estimate_txn_id=..., amount=...,
        deposit_held_usd=..." where fee_txn_id is the reference number of the new retained-fee entry,
        source_estimate_txn_id is the deposit collection it draws on, amount is the fee kept in USD with 2
        decimal places, and deposit_held_usd is the deposits still held on the booking in USD with 2 decimal
        places.
    """
    rid = ctx.make_id("efr_", estimate_id, source_estimate_txn_id, amount)
    est = ctx.find("price_estimates", estimate_id=estimate_id)
    customer_id = est[0].get("customer_id") if est else ""
    held = float(est[0].get("deposit_held_usd") or 0) if est else 0.0
    if amount is None or str(amount).strip() == "":
        return "Error: amount must be a positive USD figure with 2 decimal places."
    fee = _Cents.half_up(amount)
    if not est:
        return f"Error: no estimate {estimate_id}; pass the estimate reference number as listed by the estimate lookup."
    if fee <= 0:
        return "Error: amount must be a positive USD figure with 2 decimal places."
    src = ctx.find("estimate_transactions", estimate_txn_id=source_estimate_txn_id)
    if not src or src[0].get("estimate_id") != estimate_id or src[0].get("event_type") != "estimate_deposit_collected":
        return (f"Error: {source_estimate_txn_id} is not a deposit collection on estimate {estimate_id}; pass a deposit "
                "collection listed in that booking's deposit activity.")
    ctx.create("estimate_transactions", rid, estimate_txn_id=rid, estimate_id=estimate_id, customer_id=customer_id,
               event_type="estimate_cancellation_fee_retained", source_estimate_txn_id=source_estimate_txn_id,
               amount=fee, posting_date=ctx.now()[:10])
    ctx.update("price_estimates", estimate_id, deposit_held_usd=round(held - fee, 2))
    return (f"Fee retained: fee_txn_id={rid}, source_estimate_txn_id={source_estimate_txn_id}, amount={fee:.2f}, "
            f"deposit_held_usd={round(held - fee, 2):.2f}")


@tool(owner="user", rw="write")
def pay_surgery_package_balance_24461a4e(ctx: ToolContext, estimate_id: str, amount: float) -> str:
    """The patient pays, in person and with their own card or bank account, the pre-service balance on their
    Riverbend self-pay outpatient surgery package booking. One call records one pre-service-balance payment
    against that booking: a new deposit collection of the stated amount is added to the booking's deposit
    activity under a newly issued payment confirmation number, and the deposits held on the booking rise by
    the same amount. The patient sees the confirmation number and the new deposits-held figure at once; the
    receipt line beginning "Payment accepted" is the sign that the payment was recorded.

    Args:
        estimate_id: Id class — the reference number of the patient's outpatient surgery package estimate,
            as listed by the estimate lookup for this patient.
        amount: Fixed-format class — the pre-service balance the patient pays, in USD, 2 decimal places,
            positive magnitude (USD, 2 decimal places, positive magnitude); the value is rounded half-up to the
            cent when recorded, and an empty value is not accepted.

    Returns:
        A text receipt "Payment accepted: deposit_txn_id=..., payment_reference=..., deposit_stage=...,
        amount=..., deposit_held_usd=..." where deposit_txn_id is the reference number of the new deposit
        collection, payment_reference is the payment confirmation number issued for this payment (PMT- followed
        by 7 digits), deposit_stage is BALANCE_BEFORE_SERVICE, amount is the amount recorded in USD with 2
        decimal places, and deposit_held_usd is the deposits now held on the booking in USD with 2 decimal places.
    """
    rid = ctx.make_id("ebp_", estimate_id, "BALANCE_BEFORE_SERVICE", amount)
    reference = "PMT-55" + str(int(rid[-10:], 16) % 100000).zfill(5)
    est = ctx.find("price_estimates", estimate_id=estimate_id)
    customer_id = est[0].get("customer_id") if est else ""
    held = float(est[0].get("deposit_held_usd") or 0) if est else 0.0
    if amount is None or str(amount).strip() == "":
        return "Error: amount must be a positive USD figure with 2 decimal places."
    paid = _Cents.half_up(amount)
    if not est:
        return f"Error: no estimate {estimate_id}; pass the estimate reference number as listed by the estimate lookup."
    if paid <= 0:
        return "Error: amount must be a positive USD figure with 2 decimal places."
    ctx.create("estimate_transactions", rid, estimate_txn_id=rid, estimate_id=estimate_id, customer_id=customer_id,
               event_type="estimate_deposit_collected", deposit_stage="BALANCE_BEFORE_SERVICE", payment_reference=reference,
               amount=paid, posting_date=ctx.now()[:10])
    ctx.update("price_estimates", estimate_id, deposit_held_usd=round(held + paid, 2))
    return (f"Payment accepted: deposit_txn_id={rid}, payment_reference={reference}, deposit_stage=BALANCE_BEFORE_SERVICE, "
            f"amount={paid:.2f}, deposit_held_usd={round(held + paid, 2):.2f}")


@tool(owner="user", rw="write")
def pay_maternity_enrollment_deposit_610ee08c(ctx: ToolContext, estimate_id: str, amount: float) -> str:
    """The patient pays, in person and with their own card or bank account, the enrollment deposit on their
    Riverbend self-pay maternity and delivery package. One call records one enrollment-deposit payment against
    that package: a new deposit collection of the stated amount is added to the package's deposit activity
    under a newly issued payment confirmation number, and the deposits held on the package rise by the same
    amount. The patient sees the confirmation number and the new deposits-held figure at once; the receipt
    line beginning "Payment accepted" is the sign that the payment was recorded.

    Args:
        estimate_id: Id class — the reference number of the patient's maternity and delivery package estimate,
            as listed by the estimate lookup for this patient.
        amount: Fixed-format class — the enrollment deposit the patient pays, in USD, 2 decimal places, positive
            magnitude (USD, 2 decimal places, positive magnitude); the value is rounded half-up to the cent when
            recorded, and an empty value is not accepted.

    Returns:
        A text receipt "Payment accepted: deposit_txn_id=..., payment_reference=..., deposit_stage=...,
        amount=..., deposit_held_usd=..." where deposit_txn_id is the reference number of the new deposit
        collection, payment_reference is the payment confirmation number issued for this payment (PMT- followed
        by 7 digits), deposit_stage is INITIAL_DEPOSIT, amount is the amount recorded in USD with 2 decimal
        places, and deposit_held_usd is the deposits now held on the package in USD with 2 decimal places.
    """
    rid = ctx.make_id("emd_", estimate_id, "INITIAL_DEPOSIT", amount)
    reference = "PMT-55" + str(int(rid[-10:], 16) % 100000).zfill(5)
    est = ctx.find("price_estimates", estimate_id=estimate_id)
    customer_id = est[0].get("customer_id") if est else ""
    held = float(est[0].get("deposit_held_usd") or 0) if est else 0.0
    if amount is None or str(amount).strip() == "":
        return "Error: amount must be a positive USD figure with 2 decimal places."
    paid = _Cents.half_up(amount)
    if not est:
        return f"Error: no estimate {estimate_id}; pass the estimate reference number as listed by the estimate lookup."
    if paid <= 0:
        return "Error: amount must be a positive USD figure with 2 decimal places."
    ctx.create("estimate_transactions", rid, estimate_txn_id=rid, estimate_id=estimate_id, customer_id=customer_id,
               event_type="estimate_deposit_collected", deposit_stage="INITIAL_DEPOSIT", payment_reference=reference,
               amount=paid, posting_date=ctx.now()[:10])
    ctx.update("price_estimates", estimate_id, deposit_held_usd=round(held + paid, 2))
    return (f"Payment accepted: deposit_txn_id={rid}, payment_reference={reference}, deposit_stage=INITIAL_DEPOSIT, "
            f"amount={paid:.2f}, deposit_held_usd={round(held + paid, 2):.2f}")


@tool(owner="user", rw="write")
def pay_maternity_delivery_balance_fb9f749b(ctx: ToolContext, estimate_id: str, amount: float) -> str:
    """The patient pays, in person and with their own card or bank account, the pre-delivery balance on their
    Riverbend self-pay maternity and delivery package. One call records one pre-delivery-balance payment
    against that package: a new deposit collection of the stated amount is added to the package's deposit
    activity under a newly issued payment confirmation number, and the deposits held on the package rise by the
    same amount. The patient sees the confirmation number and the new deposits-held figure at once; the
    receipt line beginning "Payment accepted" is the sign that the payment was recorded.

    Args:
        estimate_id: Id class — the reference number of the patient's maternity and delivery package estimate,
            as listed by the estimate lookup for this patient.
        amount: Fixed-format class — the pre-delivery balance the patient pays, in USD, 2 decimal places,
            positive magnitude (USD, 2 decimal places, positive magnitude); the value is rounded half-up to the
            cent when recorded, and an empty value is not accepted.

    Returns:
        A text receipt "Payment accepted: deposit_txn_id=..., payment_reference=..., deposit_stage=...,
        amount=..., deposit_held_usd=..." where deposit_txn_id is the reference number of the new deposit
        collection, payment_reference is the payment confirmation number issued for this payment (PMT- followed
        by 7 digits), deposit_stage is BALANCE_BEFORE_SERVICE, amount is the amount recorded in USD with 2
        decimal places, and deposit_held_usd is the deposits now held on the package in USD with 2 decimal places.
    """
    rid = ctx.make_id("emb_", estimate_id, "BALANCE_BEFORE_SERVICE", amount)
    reference = "PMT-55" + str(int(rid[-10:], 16) % 100000).zfill(5)
    est = ctx.find("price_estimates", estimate_id=estimate_id)
    customer_id = est[0].get("customer_id") if est else ""
    held = float(est[0].get("deposit_held_usd") or 0) if est else 0.0
    if amount is None or str(amount).strip() == "":
        return "Error: amount must be a positive USD figure with 2 decimal places."
    paid = _Cents.half_up(amount)
    if not est:
        return f"Error: no estimate {estimate_id}; pass the estimate reference number as listed by the estimate lookup."
    if paid <= 0:
        return "Error: amount must be a positive USD figure with 2 decimal places."
    ctx.create("estimate_transactions", rid, estimate_txn_id=rid, estimate_id=estimate_id, customer_id=customer_id,
               event_type="estimate_deposit_collected", deposit_stage="BALANCE_BEFORE_SERVICE", payment_reference=reference,
               amount=paid, posting_date=ctx.now()[:10])
    ctx.update("price_estimates", estimate_id, deposit_held_usd=round(held + paid, 2))
    return (f"Payment accepted: deposit_txn_id={rid}, payment_reference={reference}, deposit_stage=BALANCE_BEFORE_SERVICE, "
            f"amount={paid:.2f}, deposit_held_usd={round(held + paid, 2):.2f}")

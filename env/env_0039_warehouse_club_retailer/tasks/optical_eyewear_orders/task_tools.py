"""Hidden task tools of the optical_eyewear_orders difficulty (Northgate Optical).

Each tool performs one atomic write on an eyewear job or its charge and credit ledger, taking the values
the agent has already worked out; none of them judges eligibility, ordering or amounts.
"""

from erlbench import ToolContext, tool


@tool(owner="agent", rw="write")
def post_switch_difference_credit_2fd39c69(ctx: ToolContext, optical_order_id: str, customer_id: str,
                                           source_txn_id: str, switch_credit_usd: float) -> str:
    """Post the price-difference credit owed to a member whose eyewear job was remade in a lens design
    priced below the design originally ordered. One call adds one refund credit against the job's original
    base-lens charge, with the amount given, dated today; the credit lowers what the member owes on the job
    and is returned to the member's original tender. The credit does not earn or take back Annual Reward.
    Success is a receipt naming the new credit's reference number and the amount booked.

    Args:
        optical_order_id: Id class — the reference number of the eyewear job the credit belongs to, read from the eyewear job lookup.
        customer_id: Id class — the customer reference number of the member who owns the eyewear job, read from the customer profile lookup.
        source_txn_id: Id class — the reference number of the job's original base-lens charge being credited, read from the job's charge and credit lookup.
        switch_credit_usd: Fixed-format class — the amount credited, in USD, 2 decimal places, >= 0; pass a plain number with no currency sign, which is rounded half-to-even to 2 decimal places on booking.

    Returns:
        A dictionary receipt: optical_txn_id (string, the reference number of the new credit), optical_order_id
        (string, the job credited), source_txn_id (string, the base-lens charge credited), amount (number, USD
        with 2 decimal places, the credit booked), credit_reason (string, always return_refund) and status
        (string, "posted" when the credit is on the job's ledger).
    """
    amount = round(float(switch_credit_usd), 2)
    rid = ctx.make_id("opt_", optical_order_id, customer_id, source_txn_id, amount, "switch")
    ctx.create("optical_transactions", rid, optical_txn_id=rid, optical_order_id=optical_order_id,
               customer_id=customer_id, event_type="optical_credit_posted", event_date=ctx.now()[:10],
               charge_component="base_lenses", amount=amount, remake_number=0,
               remake_reason="not_applicable", credit_reason="return_refund", source_txn_id=source_txn_id,
               reward_eligible=False)
    return str({"optical_txn_id": rid, "optical_order_id": optical_order_id, "source_txn_id": source_txn_id,
                "amount": amount, "credit_reason": "return_refund", "status": "posted"})


@tool(owner="agent", rw="write")
def waive_remake_overcharge_01693abf(ctx: ToolContext, optical_order_id: str, customer_id: str,
                                     source_txn_id: str, remake_number: int, remake_reason: str,
                                     waived_amount_usd: float) -> str:
    """Waive part or all of a remake charge already booked on an eyewear job. One call adds one waiver
    credit against the named remake charge, with the amount given, dated today; the credit lowers what the
    member owes for that remake and is returned to the member's original tender. The credit does not earn or
    take back Annual Reward. Success is a receipt naming the new credit's reference number and the amount
    waived.

    Args:
        optical_order_id: Id class — the reference number of the eyewear job that carries the remake charge, read from the eyewear job lookup.
        customer_id: Id class — the customer reference number of the member who owns the eyewear job, read from the customer profile lookup.
        source_txn_id: Id class — the reference number of the remake charge being waived, read from the job's charge and credit lookup.
        remake_number: Fixed-format class — the remake number shown on the remake charge being waived, a non-negative integer (1 for the first remake, 2 for the second, and so on).
        remake_reason: Enum class — the reason shown on the remake charge being waived, copied from that charge: non_adapt when the remake was opened because the patient could not adapt to the lens design; prescription_change when it was opened because the prescribing doctor changed the prescription; lab_defect when it was opened for a lens or coating defect made by the lab; frame_defect when it was opened for a manufacturing defect of the frame; accidental_damage when it was opened to replace eyewear the patient damaged by accident; not_applicable only for an entry that belongs to the original job rather than a remake.
        waived_amount_usd: Fixed-format class — the amount of the remake charge waived, in USD, 2 decimal places, >= 0; pass a plain number with no currency sign, which is rounded half-to-even to 2 decimal places on booking.

    Returns:
        A dictionary receipt: optical_txn_id (string, the reference number of the new waiver credit),
        optical_order_id (string, the job), source_txn_id (string, the remake charge waived), remake_number
        (integer, the remake the waiver belongs to), amount (number, USD with 2 decimal places, the amount
        waived), credit_reason (string, always remake_charge_waived) and status (string, "posted" when the
        waiver is on the job's ledger).
    """
    amount = round(float(waived_amount_usd), 2)
    rid = ctx.make_id("opt_", optical_order_id, customer_id, source_txn_id, remake_number, remake_reason,
                      amount, "waive")
    ctx.create("optical_transactions", rid, optical_txn_id=rid, optical_order_id=optical_order_id,
               customer_id=customer_id, event_type="optical_credit_posted", event_date=ctx.now()[:10],
               charge_component="remake_charge", amount=amount, remake_number=int(remake_number),
               remake_reason=remake_reason, credit_reason="remake_charge_waived", source_txn_id=source_txn_id,
               reward_eligible=False)
    return str({"optical_txn_id": rid, "optical_order_id": optical_order_id, "source_txn_id": source_txn_id,
                "remake_number": int(remake_number), "amount": amount, "credit_reason": "remake_charge_waived",
                "status": "posted"})


@tool(owner="user", rw="write")
def authorize_damage_replacement_0a7f54ae(ctx: ToolContext, optical_order_id: str, customer_id: str,
                                          remake_number: int, replacement_charge_usd: float) -> str:
    """The member authorizes the paid replacement of eyewear they damaged by accident and accepts its
    charge. One call opens the replacement on the member's eyewear job — the job goes to the lab as a remake
    and its remake count becomes the remake number given — and books the replacement charge, with the amount
    given and the reason accidental_damage, dated today, to be paid by the member. The charge does not earn
    Annual Reward. Success is a receipt naming the replacement charge's reference number, the remake number
    and the amount the member authorized.

    Args:
        optical_order_id: Id class — the reference number of the member's eyewear job being replaced, as the member services representative reads it to the member from the eyewear job lookup.
        customer_id: Id class — the member's customer reference number, as the member services representative reads it from the customer profile lookup.
        remake_number: Fixed-format class — the number this replacement takes among the remakes of the job, a non-negative integer (1 for the first remake, 2 for the second, and so on), as the member services representative states it.
        replacement_charge_usd: Fixed-format class — the replacement charge the member authorizes, in USD, 2 decimal places, >= 0, as the member services representative states it; pass a plain number with no currency sign, which is rounded half-to-even to 2 decimal places on booking.

    Returns:
        A dictionary receipt: optical_txn_id (string, the reference number of the replacement charge),
        optical_order_id (string, the job replaced), remake_number (integer, the remake opened), amount
        (number, USD with 2 decimal places, the charge authorized), remake_reason (string, always
        accidental_damage), job_status (string, remake_in_lab once the replacement is with the lab) and status
        (string, "authorized" when the replacement and its charge are recorded).
    """
    amount = round(float(replacement_charge_usd), 2)
    rid = ctx.make_id("opt_", optical_order_id, customer_id, remake_number, amount, "damage")
    ctx.update("optical_holdings", optical_order_id, status="remake_in_lab", remake_count=int(remake_number))
    ctx.create("optical_transactions", rid, optical_txn_id=rid, optical_order_id=optical_order_id,
               customer_id=customer_id, event_type="optical_charge_posted", event_date=ctx.now()[:10],
               charge_component="remake_charge", amount=amount, remake_number=int(remake_number),
               remake_reason="accidental_damage", credit_reason="not_applicable", source_txn_id="",
               reward_eligible=False)
    return str({"optical_txn_id": rid, "optical_order_id": optical_order_id, "remake_number": int(remake_number),
                "amount": amount, "remake_reason": "accidental_damage", "job_status": "remake_in_lab",
                "status": "authorized"})


@tool(owner="agent", rw="write")
def refund_lens_option_d067b0d2(ctx: ToolContext, optical_order_id: str, customer_id: str, source_txn_id: str,
                                option_component: str, option_refund_usd: float) -> str:
    """Refund a lens option charge of an eyewear job as a cancellation refund. One call books one cancellation
    refund credit against the named option charge, with the amount given, dated today, returned to the
    member's original tender; the rest of the option charge stays billed. The credit does not earn or take
    back Annual Reward. Success is a receipt naming the credit's reference number and the amount refunded.

    Args:
        optical_order_id: Id class — the reference number of the eyewear job that carries the option charge, read from the eyewear job lookup.
        customer_id: Id class — the customer reference number of the member who owns the eyewear job, read from the customer profile lookup.
        source_txn_id: Id class — the reference number of the option charge being refunded, read from the job's charge and credit lookup.
        option_component: Enum class — the component shown on the option charge being refunded, copied from that charge: anti_reflective_coating for an anti-reflective coating option; photochromic for the light-adaptive option; blue_light_filter for the blue-light filtering option; frame names the frame charge, which is not a lens option; base_lenses names the base-lens charge, not an option; material_upgrade names the lens material upgrade charge, not an option; remake_charge names a remake charge, not an option; vision_plan_allowance names a plan allowance entry, not an option; frame_allowance names a plan frame allowance entry, not an option — none of these six is ever passed to this refund.
        option_refund_usd: Fixed-format class — the amount of the option charge refunded, in USD, 2 decimal places, >= 0; pass a plain number with no currency sign, which is rounded half-to-even to 2 decimal places on booking.

    Returns:
        A dictionary receipt: optical_txn_id (string, the reference number of the option refund credit),
        optical_order_id (string, the job), source_txn_id (string, the option charge refunded), charge_component
        (string, the option refunded), amount (number, USD with 2 decimal places, the refund), credit_reason
        (string, always cancellation_refund) and status (string, "posted" when the refund is on the ledger).
    """
    amount = round(float(option_refund_usd), 2)
    rid = ctx.make_id("opt_", optical_order_id, customer_id, source_txn_id, option_component, amount, "cancel_opt")
    ctx.create("optical_transactions", rid, optical_txn_id=rid, optical_order_id=optical_order_id,
               customer_id=customer_id, event_type="optical_credit_posted", event_date=ctx.now()[:10],
               charge_component=option_component, amount=amount, remake_number=0, remake_reason="not_applicable",
               credit_reason="cancellation_refund", source_txn_id=source_txn_id, reward_eligible=False)
    return str({"optical_txn_id": rid, "optical_order_id": optical_order_id, "source_txn_id": source_txn_id,
                "charge_component": option_component, "amount": amount, "credit_reason": "cancellation_refund",
                "status": "posted"})


@tool(owner="agent", rw="write")
def refund_lens_material_ad7f47c2(ctx: ToolContext, optical_order_id: str, customer_id: str, source_txn_id: str,
                                  material_refund_usd: float) -> str:
    """Refund the lens material upgrade charge of an eyewear job as a cancellation refund. One call books one
    cancellation refund credit against the job's material upgrade charge, with the amount given, dated today,
    returned to the member's original tender; the rest of the material charge stays billed. The credit does
    not earn or take back Annual Reward. Success is a receipt naming the credit's reference number and the
    amount refunded.

    Args:
        optical_order_id: Id class — the reference number of the eyewear job that carries the material upgrade charge, read from the eyewear job lookup.
        customer_id: Id class — the customer reference number of the member who owns the eyewear job, read from the customer profile lookup.
        source_txn_id: Id class — the reference number of the material upgrade charge being refunded, read from the job's charge and credit lookup.
        material_refund_usd: Fixed-format class — the amount of the material upgrade charge refunded, in USD, 2 decimal places, >= 0; pass a plain number with no currency sign, which is rounded half-to-even to 2 decimal places on booking.

    Returns:
        A dictionary receipt: optical_txn_id (string, the reference number of the material refund credit),
        optical_order_id (string, the job), source_txn_id (string, the material upgrade charge refunded), amount
        (number, USD with 2 decimal places, the refund), credit_reason (string, always cancellation_refund) and
        status (string, "posted" when the refund is on the ledger).
    """
    amount = round(float(material_refund_usd), 2)
    rid = ctx.make_id("opt_", optical_order_id, customer_id, source_txn_id, amount, "cancel_mat")
    ctx.create("optical_transactions", rid, optical_txn_id=rid, optical_order_id=optical_order_id,
               customer_id=customer_id, event_type="optical_credit_posted", event_date=ctx.now()[:10],
               charge_component="material_upgrade", amount=amount, remake_number=0, remake_reason="not_applicable",
               credit_reason="cancellation_refund", source_txn_id=source_txn_id, reward_eligible=False)
    return str({"optical_txn_id": rid, "optical_order_id": optical_order_id, "source_txn_id": source_txn_id,
                "amount": amount, "credit_reason": "cancellation_refund", "status": "posted"})


@tool(owner="agent", rw="write")
def refund_frame_to_stock_fae456d1(ctx: ToolContext, optical_order_id: str, customer_id: str,
                                   source_txn_id: str, frame_refund_usd: float) -> str:
    """Book the refund of an eyewear job's frame when the frame goes back to stock. One call adds one
    cancellation refund credit against the job's frame charge, with the amount given, dated today, returned to
    the member's original tender; whatever is not refunded stays billed. The credit does not earn or take back
    Annual Reward. Success is a receipt naming the credit's reference number and the amount refunded.

    Args:
        optical_order_id: Id class — the reference number of the eyewear job whose frame is refunded, read from the eyewear job lookup.
        customer_id: Id class — the customer reference number of the member who owns the eyewear job, read from the customer profile lookup.
        source_txn_id: Id class — the reference number of the job's frame charge being refunded, read from the job's charge and credit lookup.
        frame_refund_usd: Fixed-format class — the amount of the frame charge refunded, in USD, 2 decimal places, >= 0; pass a plain number with no currency sign, which is rounded half-to-even to 2 decimal places on booking.

    Returns:
        A dictionary receipt: optical_txn_id (string, the reference number of the frame refund credit),
        optical_order_id (string, the job), source_txn_id (string, the frame charge refunded), amount (number, USD
        with 2 decimal places, the refund), credit_reason (string, always cancellation_refund) and status (string,
        "posted" when the refund is on the ledger).
    """
    amount = round(float(frame_refund_usd), 2)
    rid = ctx.make_id("opt_", optical_order_id, customer_id, source_txn_id, amount, "frame_stock")
    ctx.create("optical_transactions", rid, optical_txn_id=rid, optical_order_id=optical_order_id,
               customer_id=customer_id, event_type="optical_credit_posted", event_date=ctx.now()[:10],
               charge_component="frame", amount=amount, remake_number=0, remake_reason="not_applicable",
               credit_reason="cancellation_refund", source_txn_id=source_txn_id, reward_eligible=False)
    return str({"optical_txn_id": rid, "optical_order_id": optical_order_id, "source_txn_id": source_txn_id,
                "amount": amount, "credit_reason": "cancellation_refund", "status": "posted"})


@tool(owner="user", rw="write")
def confirm_eyewear_cancellation_51323feb(ctx: ToolContext, optical_order_id: str, customer_id: str,
                                          source_txn_id: str, lens_refund_usd: float) -> str:
    """The member confirms the cancellation of their own eyewear job and accepts the refund of its lenses.
    One call marks the job cancelled as of today and books one cancellation refund credit against the job's
    base-lens charge, with the amount given, returned to the member's original tender; whatever is not refunded
    stays billed. The credit does not earn or take back Annual Reward. Success is a receipt showing the job as
    cancelled, the lens refund's reference number and the amount refunded.

    Args:
        optical_order_id: Id class — the reference number of the member's eyewear job being cancelled, as the member services representative reads it to the member from the eyewear job lookup.
        customer_id: Id class — the member's customer reference number, as the member services representative reads it from the customer profile lookup.
        source_txn_id: Id class — the reference number of the job's base-lens charge being refunded, as the member services representative reads it from the job's charge and credit lookup.
        lens_refund_usd: Fixed-format class — the lens refund the member accepts, in USD, 2 decimal places, >= 0, as the member services representative states it; pass a plain number with no currency sign, which is rounded half-to-even to 2 decimal places on booking.

    Returns:
        A dictionary receipt: optical_order_id (string, the job cancelled), job_status (string, cancelled),
        closed_date (string, YYYY-MM-DD, the cancellation date), optical_txn_id (string, the reference number of
        the lens refund credit), source_txn_id (string, the base-lens charge refunded), amount (number, USD with 2
        decimal places, the lens refund), credit_reason (string, always cancellation_refund) and status (string,
        "confirmed" when the cancellation and the lens refund are recorded).
    """
    amount = round(float(lens_refund_usd), 2)
    today = ctx.now()[:10]
    rid = ctx.make_id("opt_", optical_order_id, customer_id, source_txn_id, amount, "cancel_lens")
    ctx.update("optical_holdings", optical_order_id, status="cancelled", closed_date=today)
    ctx.create("optical_transactions", rid, optical_txn_id=rid, optical_order_id=optical_order_id,
               customer_id=customer_id, event_type="optical_credit_posted", event_date=today,
               charge_component="base_lenses", amount=amount, remake_number=0, remake_reason="not_applicable",
               credit_reason="cancellation_refund", source_txn_id=source_txn_id, reward_eligible=False)
    return str({"optical_order_id": optical_order_id, "job_status": "cancelled", "closed_date": today,
                "optical_txn_id": rid, "source_txn_id": source_txn_id, "amount": amount,
                "credit_reason": "cancellation_refund", "status": "confirmed"})

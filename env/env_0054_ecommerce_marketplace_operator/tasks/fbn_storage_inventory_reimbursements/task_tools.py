"""Hidden task tools for the fbn_storage_inventory_reimbursements difficulty of
env_0054_ecommerce_marketplace_operator (Northloop Marketplace, Fulfilled by Northloop).

Each tool makes one atomic change to a seller's FBN reimbursement case and performs no
eligibility, ownership, status or arithmetic judgement of its own.
"""

from erlbench import ToolContext, tool


@tool(owner="user", rw="write")
def amend_lost_inventory_claim_06dd83f3(ctx: ToolContext, case_id: str, reimbursement_type: str,
                                        adjustment_ref: str, shipment_id: str, order_id: str,
                                        removal_order_id: str, sku: str, units_claimed: int) -> str:
    """The seller corrects the number of units claimed on their own open FBN warehouse-loss
    reimbursement case. One call rewrites the unit count the seller is claiming on that case and
    re-records the loss kind, source references and SKU the claim is about; the case stays open
    with its original opening moment, and nothing is approved or paid by this action. On success
    the seller's case shows the corrected units claimed. Success is a receipt naming the case and
    the units now claimed.

    Args:
        case_id: Id class — the reference number of the seller's open FBN reimbursement case being
            corrected, read from the seller's case list returned by the FBN case lookup.
        reimbursement_type: Enum class — the loss kind recorded on the case: lost_in_warehouse
            when units went missing inside a fulfillment center; damaged_in_warehouse when units
            were damaged inside a fulfillment center; inbound_shortage when an inbound shipment line
            was received short; customer_return_not_received when a refunded buyer return never
            arrived; removal_lost when a removal shipment to the seller was lost; not_applicable
            when the case is a fee dispute rather than a loss claim.
        adjustment_ref: Id class — the inventory adjustment reference number the case names, copied
            from the case record; pass an empty string when the case names no single adjustment.
        shipment_id: Id class — the inbound shipment number the case names, copied from the case
            record; pass an empty string when the case names no shipment.
        order_id: Id class — the marketplace order number the case names, copied from the case
            record; pass an empty string when the case names no order.
        removal_order_id: Id class — the removal order reference number the case names, copied from
            the case record; pass an empty string when the case names no removal order.
        sku: Verbatim class — the seller SKU the case is about, copied character for character from
            the case record with no change to letters, digits or punctuation (verbatim).
        units_claimed: Fixed-format class — the corrected number of units the seller claims on the
            case, given in integer units (a whole count of units, zero or more, with no fractional part).

    Returns:
        A dictionary receipt: case_id (string, the corrected case's reference number), sku (string,
        the SKU of the case), units_claimed (integer, the units now claimed on the case) and
        case_status (string, always submitted, meaning the case is still open awaiting a decision).
        A returned receipt means the correction is recorded.
    """
    ctx.update("fulfill_cases", case_id, reimbursement_type=reimbursement_type,
               adjustment_ref=adjustment_ref, shipment_id=shipment_id, order_id=order_id,
               removal_order_id=removal_order_id, sku=sku, units_claimed=int(units_claimed))
    return str({"case_id": case_id, "sku": sku, "units_claimed": int(units_claimed),
                "case_status": "submitted"})


@tool(owner="agent", rw="write")
def approve_lost_inventory_case_b95e2fef(ctx: ToolContext, case_id: str, reimbursement_type: str,
                                         adjustment_ref: str, shipment_id: str, order_id: str,
                                         removal_order_id: str, sku: str, units_approved: int) -> str:
    """The support desk records its decision approving a seller's open FBN warehouse-loss
    reimbursement case for a number of units. One call marks the case approved and sets the unit
    count on the case to the units Northloop accepts for reimbursement, re-recording the loss kind,
    source references and SKU of the decision; the reimbursement payment itself is issued separately by
    Northloop's reimbursement run and is not made by this action. On success the seller's case
    shows status approved and the approved units. Success is a receipt naming the case and the
    approved units.

    Args:
        case_id: Id class — the reference number of the seller's open FBN reimbursement case being
            decided, read from the seller's case list returned by the FBN case lookup.
        reimbursement_type: Enum class — the loss kind recorded on the case: lost_in_warehouse
            when units went missing inside a fulfillment center; damaged_in_warehouse when units
            were damaged inside a fulfillment center; inbound_shortage when an inbound shipment line
            was received short; customer_return_not_received when a refunded buyer return never
            arrived; removal_lost when a removal shipment to the seller was lost; not_applicable
            when the case is a fee dispute rather than a loss claim.
        adjustment_ref: Id class — the inventory adjustment reference number the case names, copied
            from the case record; pass an empty string when the case names no single adjustment.
        shipment_id: Id class — the inbound shipment number the case names, copied from the case
            record; pass an empty string when the case names no shipment.
        order_id: Id class — the marketplace order number the case names, copied from the case
            record; pass an empty string when the case names no order.
        removal_order_id: Id class — the removal order reference number the case names, copied from
            the case record; pass an empty string when the case names no removal order.
        sku: Verbatim class — the seller SKU the case is about, copied character for character from
            the case record with no change to letters, digits or punctuation (verbatim).
        units_approved: Fixed-format class — the number of units approved for reimbursement on the
            case, given in integer units (a whole count of units, zero or more, with no fractional part).

    Returns:
        A dictionary receipt: case_id (string, the decided case's reference number), sku (string,
        the SKU of the case), units_approved (integer, the units approved and now shown as the
        case's unit count) and case_status (string, always approved). A returned receipt means the
        approval is recorded.
    """
    ctx.update("fulfill_cases", case_id, reimbursement_type=reimbursement_type,
               adjustment_ref=adjustment_ref, shipment_id=shipment_id, order_id=order_id,
               removal_order_id=removal_order_id, sku=sku, units_claimed=int(units_approved),
               case_status="approved")
    return str({"case_id": case_id, "sku": sku, "units_approved": int(units_approved),
                "case_status": "approved"})


@tool(owner="user", rw="write")
def amend_inbound_shortage_claim_fdee09ae(ctx: ToolContext, case_id: str, reimbursement_type: str,
                                        adjustment_ref: str, shipment_id: str, order_id: str,
                                        removal_order_id: str, sku: str, units_claimed: int) -> str:
    """The seller corrects the number of units claimed on their own open FBN inbound-shortage
    reimbursement case, the claim for units of an inbound shipment line that were never received. One call rewrites the unit count the seller is claiming on that case and
    re-records the loss kind, source references and SKU the claim is about; the case stays open
    with its original opening moment, and nothing is approved or paid by this action. On success
    the seller's case shows the corrected units claimed. Success is a receipt naming the case and
    the units now claimed.

    Args:
        case_id: Id class — the reference number of the seller's open FBN reimbursement case being
            corrected, read from the seller's case list returned by the FBN case lookup.
        reimbursement_type: Enum class — the loss kind recorded on the case: lost_in_warehouse
            when units went missing inside a fulfillment center; damaged_in_warehouse when units
            were damaged inside a fulfillment center; inbound_shortage when an inbound shipment line
            was received short; customer_return_not_received when a refunded buyer return never
            arrived; removal_lost when a removal shipment to the seller was lost; not_applicable
            when the case is a fee dispute rather than a loss claim.
        adjustment_ref: Id class — the inventory adjustment reference number the case names, copied
            from the case record; pass an empty string when the case names no single adjustment.
        shipment_id: Id class — the inbound shipment number the case names, copied from the case
            record; pass an empty string when the case names no shipment.
        order_id: Id class — the marketplace order number the case names, copied from the case
            record; pass an empty string when the case names no order.
        removal_order_id: Id class — the removal order reference number the case names, copied from
            the case record; pass an empty string when the case names no removal order.
        sku: Verbatim class — the seller SKU the case is about, copied character for character from
            the case record with no change to letters, digits or punctuation (verbatim).
        units_claimed: Fixed-format class — the corrected number of units the seller claims on the
            case, given in integer units (a whole count of units, zero or more, with no fractional part).

    Returns:
        A dictionary receipt: case_id (string, the corrected case's reference number), sku (string,
        the SKU of the case), units_claimed (integer, the units now claimed on the case) and
        case_status (string, always submitted, meaning the case is still open awaiting a decision).
        A returned receipt means the correction is recorded.
    """
    ctx.update("fulfill_cases", case_id, reimbursement_type=reimbursement_type,
               adjustment_ref=adjustment_ref, shipment_id=shipment_id, order_id=order_id,
               removal_order_id=removal_order_id, sku=sku, units_claimed=int(units_claimed))
    return str({"case_id": case_id, "sku": sku, "units_claimed": int(units_claimed),
                "case_status": "submitted"})


@tool(owner="agent", rw="write")
def approve_inbound_shortage_case_dfebd527(ctx: ToolContext, case_id: str, reimbursement_type: str,
                                         adjustment_ref: str, shipment_id: str, order_id: str,
                                         removal_order_id: str, sku: str, units_approved: int) -> str:
    """The support desk records its decision approving a seller's open FBN inbound-shortage
    reimbursement case, the claim for units of an inbound shipment line that were never received, for a
    number of units. One call marks the case approved and sets the unit
    count on the case to the units Northloop accepts for reimbursement, re-recording the loss kind,
    source references and SKU of the decision; the reimbursement payment itself is issued separately by
    Northloop's reimbursement run and is not made by this action. On success the seller's case
    shows status approved and the approved units. Success is a receipt naming the case and the
    approved units.

    Args:
        case_id: Id class — the reference number of the seller's open FBN reimbursement case being
            decided, read from the seller's case list returned by the FBN case lookup.
        reimbursement_type: Enum class — the loss kind recorded on the case: lost_in_warehouse
            when units went missing inside a fulfillment center; damaged_in_warehouse when units
            were damaged inside a fulfillment center; inbound_shortage when an inbound shipment line
            was received short; customer_return_not_received when a refunded buyer return never
            arrived; removal_lost when a removal shipment to the seller was lost; not_applicable
            when the case is a fee dispute rather than a loss claim.
        adjustment_ref: Id class — the inventory adjustment reference number the case names, copied
            from the case record; pass an empty string when the case names no single adjustment.
        shipment_id: Id class — the inbound shipment number the case names, copied from the case
            record; pass an empty string when the case names no shipment.
        order_id: Id class — the marketplace order number the case names, copied from the case
            record; pass an empty string when the case names no order.
        removal_order_id: Id class — the removal order reference number the case names, copied from
            the case record; pass an empty string when the case names no removal order.
        sku: Verbatim class — the seller SKU the case is about, copied character for character from
            the case record with no change to letters, digits or punctuation (verbatim).
        units_approved: Fixed-format class — the number of units approved for reimbursement on the
            case, given in integer units (a whole count of units, zero or more, with no fractional part).

    Returns:
        A dictionary receipt: case_id (string, the decided case's reference number), sku (string,
        the SKU of the case), units_approved (integer, the units approved and now shown as the
        case's unit count) and case_status (string, always approved). A returned receipt means the
        approval is recorded.
    """
    ctx.update("fulfill_cases", case_id, reimbursement_type=reimbursement_type,
               adjustment_ref=adjustment_ref, shipment_id=shipment_id, order_id=order_id,
               removal_order_id=removal_order_id, sku=sku, units_claimed=int(units_approved),
               case_status="approved")
    return str({"case_id": case_id, "sku": sku, "units_approved": int(units_approved),
                "case_status": "approved"})


@tool(owner="agent", rw="write")
def approve_damaged_inventory_case_556f0f6d(ctx: ToolContext, case_id: str, reimbursement_type: str,
                                         adjustment_ref: str, shipment_id: str, order_id: str,
                                         removal_order_id: str, sku: str, units_approved: int) -> str:
    """The support desk records its decision approving a seller's open FBN warehouse-damage
    reimbursement case, the claim for units damaged inside a fulfillment center, for a number of units. One call marks the case approved and sets the unit
    count on the case to the units Northloop accepts for reimbursement, re-recording the loss kind,
    source references and SKU of the decision; the reimbursement payment itself is issued separately by
    Northloop's reimbursement run and is not made by this action. On success the seller's case
    shows status approved and the approved units. Success is a receipt naming the case and the
    approved units.

    Args:
        case_id: Id class — the reference number of the seller's open FBN reimbursement case being
            decided, read from the seller's case list returned by the FBN case lookup.
        reimbursement_type: Enum class — the loss kind recorded on the case: lost_in_warehouse
            when units went missing inside a fulfillment center; damaged_in_warehouse when units
            were damaged inside a fulfillment center; inbound_shortage when an inbound shipment line
            was received short; customer_return_not_received when a refunded buyer return never
            arrived; removal_lost when a removal shipment to the seller was lost; not_applicable
            when the case is a fee dispute rather than a loss claim.
        adjustment_ref: Id class — the inventory adjustment reference number the case names, copied
            from the case record; pass an empty string when the case names no single adjustment.
        shipment_id: Id class — the inbound shipment number the case names, copied from the case
            record; pass an empty string when the case names no shipment.
        order_id: Id class — the marketplace order number the case names, copied from the case
            record; pass an empty string when the case names no order.
        removal_order_id: Id class — the removal order reference number the case names, copied from
            the case record; pass an empty string when the case names no removal order.
        sku: Verbatim class — the seller SKU the case is about, copied character for character from
            the case record with no change to letters, digits or punctuation (verbatim).
        units_approved: Fixed-format class — the number of units approved for reimbursement on the
            case, given in integer units (a whole count of units, zero or more, with no fractional part).

    Returns:
        A dictionary receipt: case_id (string, the decided case's reference number), sku (string,
        the SKU of the case), units_approved (integer, the units approved and now shown as the
        case's unit count) and case_status (string, always approved). A returned receipt means the
        approval is recorded.
    """
    ctx.update("fulfill_cases", case_id, reimbursement_type=reimbursement_type,
               adjustment_ref=adjustment_ref, shipment_id=shipment_id, order_id=order_id,
               removal_order_id=removal_order_id, sku=sku, units_claimed=int(units_approved),
               case_status="approved")
    return str({"case_id": case_id, "sku": sku, "units_approved": int(units_approved),
                "case_status": "approved"})

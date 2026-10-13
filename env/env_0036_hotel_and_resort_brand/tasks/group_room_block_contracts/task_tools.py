"""Hidden task tools of the group_room_block_contracts difficulty (Group Room Blocks) of
env_0036_hotel_and_resort_brand. Each tool performs one atomic write the agent or the organiser has
already decided; none of them checks a policy condition, aggregates history or computes a figure.
Reached only through unlock_*_discoverable_tool -> call_*_discoverable_tool.
"""

from erlbench import ToolContext, tool


@tool(owner="agent", rw="write")
def implement_block_reduction_df5160bf(ctx: ToolContext, group_block_id: str, amendment_id: str,
                                       room_nights_removed: int) -> str:
    """Implement a signed room-night reduction addendum on a group room block: guest services
    records one reduction entry on the block's ledger that names the addendum and carries the room
    nights removed, and lowers both the block's contracted room nights and its held room nights by
    that same number, so the room nights leave the contract and return to the hotel's inventory.
    The block's group rate, dates and deposits are left unchanged. On success the block shows the
    lower contracted and held room nights and the ledger shows the new reduction entry dated today.

    Args:
        group_block_id: Id class — the reference number of the group room block being reduced, as returned by the group block lookup for the organiser's block.
        amendment_id: Id class — the reference number of the signed reduction addendum being implemented, as returned by the contract addendum lookup for that block.
        room_nights_removed: Fixed-format class — the number of room nights taken out of the block by this entry, a positive integer count in integer room nights (no fractions).

    Returns:
        A dictionary rendered as text with: status ("implemented" on success); group_entry_id
        (reference number of the new reduction ledger entry); group_block_id (the block reduced);
        amendment_id (the addendum implemented); room_nights_removed (integer room nights removed);
        contracted_room_nights (integer room nights contracted after the entry); held_room_nights
        (integer room nights held after the entry); entry_date (date of the entry, YYYY-MM-DD).
    """
    n = int(room_nights_removed)
    block = (ctx.find("group_blocks", group_block_id=group_block_id) or [{}])[0]
    contracted = int(block.get("contracted_room_nights") or 0) - n
    held = int(block.get("held_room_nights") or 0) - n
    today = ctx.now()[:10]
    rid = ctx.make_id("gle_", group_block_id, amendment_id, n)
    ctx.create("group_ledger", rid, group_entry_id=rid, group_block_id=group_block_id,
               customer_id=block.get("customer_id"), event_type="group_block_reduce", amount=0.0,
               room_nights=n, entry_date=today, entry_basis="signed_addendum", related_entry_id=None,
               amendment_id=amendment_id)
    ctx.update("group_blocks", group_block_id, contracted_room_nights=contracted, held_room_nights=held)
    return str({"status": "implemented", "group_entry_id": rid, "group_block_id": group_block_id,
                "amendment_id": amendment_id, "room_nights_removed": n,
                "contracted_room_nights": contracted, "held_room_nights": held, "entry_date": today})


@tool(owner="user", rw="write")
def pay_group_deposit_93013531(ctx: ToolContext, group_block_id: str, entry_basis: str,
                               deposit_amount: float) -> str:
    """The organiser pays a scheduled group deposit on their own group room block with the payment
    card on their profile. One deposit receipt is recorded on the block's ledger for the amount paid
    and the basis given, and the deposit the hotel holds for the block rises by that amount; the
    contract terms are not changed. On success the organiser receives a deposit receipt number and
    sees the new deposit held on the block.

    Args:
        group_block_id: Id class — the reference number of the organiser's group room block, which guest services reads from the group block lookup and gives to the organiser together with the amount.
        entry_basis: Enum class — which scheduled deposit is being paid. deposit_signing — the signing deposit due shortly after the proposal is issued; deposit_interim — the interim deposit due a set number of days before arrival; contract_block — room-night allocation, never a deposit, not used here; signed_addendum — addendum room-night change, not used here; cutoff_release — cut-off room release, not used here; contract_cancelled — release on cancellation, not used here; attrition — attrition charge, not used here; cancellation_damages — cancellation charge, not used here; master_billed_rooms — rooms billed to the master account, not used here; comp_rooms — complimentary room credit, not used here; organiser_payment — master account payment, not used here; deposit_applied — deposit applied after the event, not used here; deposit_refunded — deposit refund, not used here; deposit_forfeited — deposit retained toward damages, not used here.
        deposit_amount: Fixed-format class — the deposit being paid, in USD, 2 decimal places, a positive amount rounded to the cent.

    Returns:
        A dictionary rendered as text with: status ("received" on success); receipt_id (reference
        number of the deposit receipt); group_block_id (the block paid on); entry_basis (the
        deposit paid); amount_paid (USD, 2 decimal places); deposit_held (USD, 2 decimal places, the
        deposit held on the block after the payment); entry_date (date of the receipt, YYYY-MM-DD).
    """
    block = (ctx.find("group_blocks", group_block_id=group_block_id) or [{}])[0]
    amount = round(float(deposit_amount), 2)
    held = round(float(block.get("deposit_held") or 0) + amount, 2)
    today = ctx.now()[:10]
    rid = ctx.make_id("gle_", group_block_id, entry_basis, amount)
    ctx.create("group_ledger", rid, group_entry_id=rid, group_block_id=group_block_id,
               customer_id=block.get("customer_id"), event_type="group_deposit_receive", amount=amount,
               room_nights=0, entry_date=today, entry_basis=entry_basis, related_entry_id=None,
               amendment_id=None)
    ctx.update("group_blocks", group_block_id, deposit_held=held)
    return str({"status": "received", "receipt_id": rid, "group_block_id": group_block_id,
                "entry_basis": entry_basis, "amount_paid": amount, "deposit_held": held,
                "entry_date": today})


@tool(owner="agent", rw="write")
def implement_block_increase_5576c741(ctx: ToolContext, group_block_id: str, amendment_id: str,
                                      room_nights_added: int, committed_room_nights: int) -> str:
    """Implement a signed room-night increase addendum on a group room block: guest services records
    one increase entry on the block's ledger that names the addendum and carries the room nights
    added, raises the block's held room nights by those room nights, and raises the block's
    contracted (committed) room nights by the committed room nights given. The group rate and dates
    are left unchanged. On success the block shows the new held and contracted room nights and the
    ledger shows the new increase entry dated today.

    Args:
        group_block_id: Id class — the reference number of the group room block being increased, as returned by the group block lookup for the organiser's block.
        amendment_id: Id class — the reference number of the signed increase addendum being implemented, as returned by the contract addendum lookup for that block.
        room_nights_added: Fixed-format class — the room nights added to the rooms held for the group, a positive integer count in integer room nights.
        committed_room_nights: Fixed-format class — the part of the added room nights that enters the contracted commitment, a non-negative integer count in integer room nights, never more than the room nights added.

    Returns:
        A dictionary rendered as text with: status ("implemented" on success); group_entry_id
        (reference number of the new increase ledger entry); group_block_id (the block increased);
        amendment_id (the addendum implemented); room_nights_added (integer room nights added to the
        held rooms); committed_room_nights (integer room nights added to the contract);
        contracted_room_nights (integer room nights contracted after the entry); held_room_nights
        (integer room nights held after the entry); entry_date (date of the entry, YYYY-MM-DD).
    """
    added = int(room_nights_added)
    committed = int(committed_room_nights)
    block = (ctx.find("group_blocks", group_block_id=group_block_id) or [{}])[0]
    contracted = int(block.get("contracted_room_nights") or 0) + committed
    held = int(block.get("held_room_nights") or 0) + added
    today = ctx.now()[:10]
    rid = ctx.make_id("gle_", group_block_id, amendment_id, added, committed)
    ctx.create("group_ledger", rid, group_entry_id=rid, group_block_id=group_block_id,
               customer_id=block.get("customer_id"), event_type="group_block_increase", amount=0.0,
               room_nights=added, entry_date=today, entry_basis="signed_addendum", related_entry_id=None,
               amendment_id=amendment_id)
    ctx.update("group_blocks", group_block_id, contracted_room_nights=contracted, held_room_nights=held)
    return str({"status": "implemented", "group_entry_id": rid, "group_block_id": group_block_id,
                "amendment_id": amendment_id, "room_nights_added": added,
                "committed_room_nights": committed, "contracted_room_nights": contracted,
                "held_room_nights": held, "entry_date": today})


@tool(owner="agent", rw="write")
def record_cutoff_release_57832b69(ctx: ToolContext, group_block_id: str, room_nights_released: int) -> str:
    """Record the cut-off release of a group room block: guest services records one release entry on
    the block's ledger with the cut-off basis, dated the block's cut-off date, for the room nights
    returned to the hotel's general inventory, and lowers the block's held room nights by that
    number. The contracted room nights are not changed. On success the block shows the lower held
    room nights and the ledger shows the release entry.

    Args:
        group_block_id: Id class — the reference number of the group room block whose cut-off release is recorded, as returned by the group block lookup for the organiser's block.
        room_nights_released: Fixed-format class — the room nights returned to general inventory by the release, a non-negative integer count in integer room nights.

    Returns:
        A dictionary rendered as text with: status ("released" on success); group_entry_id
        (reference number of the release ledger entry); group_block_id (the block); room_nights_released
        (integer room nights released); held_room_nights (integer room nights still held after the
        release); entry_date (date the release is dated, the block's cut-off date, YYYY-MM-DD).
    """
    n = int(room_nights_released)
    block = (ctx.find("group_blocks", group_block_id=group_block_id) or [{}])[0]
    held = int(block.get("held_room_nights") or 0) - n
    dated = str(block.get("cutoff_date") or ctx.now()[:10])
    rid = ctx.make_id("gle_", group_block_id, "cutoff_release", n)
    ctx.create("group_ledger", rid, group_entry_id=rid, group_block_id=group_block_id,
               customer_id=block.get("customer_id"), event_type="group_cutoff_release", amount=0.0,
               room_nights=n, entry_date=dated, entry_basis="cutoff_release", related_entry_id=None,
               amendment_id=None)
    ctx.update("group_blocks", group_block_id, held_room_nights=held)
    return str({"status": "released", "group_entry_id": rid, "group_block_id": group_block_id,
                "room_nights_released": n, "held_room_nights": held, "entry_date": dated})


@tool(owner="user", rw="write")
def sign_group_cancellation_1ea1e1e5(ctx: ToolContext, group_block_id: str, damages_amount: float) -> str:
    """The organiser signs the written cancellation notice of their own definite group room block.
    The block becomes cancelled with today's date as its cancellation date; every room night still
    held is released to the hotel's inventory by one release entry with the cancellation basis; and
    the cancellation damages given are charged to the group master account by one damages entry on
    the block's ledger, which raises the master account balance by that amount. On success the
    organiser receives the cancellation and damages entry numbers and sees the block as cancelled.

    Args:
        group_block_id: Id class — the reference number of the organiser's group room block, which guest services reads from the group block lookup and gives to the organiser together with the damages amount.
        damages_amount: Fixed-format class — the cancellation damages being charged, in USD, 2 decimal places, a non-negative amount rounded to the cent.

    Returns:
        A dictionary rendered as text with: status ("cancelled" on success); group_block_id (the block
        cancelled); cancelled_date (YYYY-MM-DD); release_entry_id (reference number of the release
        entry); room_nights_released (integer room nights released on cancellation);
        damages_entry_id (reference number of the damages entry); damages_amount (USD, 2 decimal
        places); master_balance (USD, 2 decimal places, the master account balance after the charge).
    """
    block = (ctx.find("group_blocks", group_block_id=group_block_id) or [{}])[0]
    amount = round(float(damages_amount), 2)
    today = ctx.now()[:10]
    held = int(block.get("held_room_nights") or 0)
    contracted = int(block.get("contracted_room_nights") or 0)
    master = round(float(block.get("master_balance") or 0) + amount, 2)
    rel = ctx.make_id("gle_", group_block_id, "contract_cancelled", today)
    ctx.create("group_ledger", rel, group_entry_id=rel, group_block_id=group_block_id,
               customer_id=block.get("customer_id"), event_type="group_cutoff_release", amount=0.0,
               room_nights=held, entry_date=today, entry_basis="contract_cancelled", related_entry_id=None,
               amendment_id=None)
    dmg = ctx.make_id("gle_", group_block_id, "cancellation_damages", amount)
    ctx.create("group_ledger", dmg, group_entry_id=dmg, group_block_id=group_block_id,
               customer_id=block.get("customer_id"), event_type="group_cancellation_charge", amount=amount,
               room_nights=contracted, entry_date=today, entry_basis="cancellation_damages",
               related_entry_id=None, amendment_id=None)
    ctx.update("group_blocks", group_block_id, status="cancelled", cancelled_date=today,
               held_room_nights=0, master_balance=master)
    return str({"status": "cancelled", "group_block_id": group_block_id, "cancelled_date": today,
                "release_entry_id": rel, "room_nights_released": held, "damages_entry_id": dmg,
                "damages_amount": amount, "master_balance": master})

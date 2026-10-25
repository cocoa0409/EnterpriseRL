"""Hidden task tools for the prepaid_service_hours difficulty (TimeBank Prepaid Service Hours).

Each tool performs one atomic business write on TimeBank records with the values the caller
supplies; none of them checks eligibility, status, ownership or any policy precondition.
"""

from erlbench import ToolContext, tool


@tool(owner="user", rw="write")
def sign_repeat_block_order_5562f94d(ctx: ToolContext, customer_id: str, current_block_id: str,
                                     quoted_amount_usd: float) -> str:
    """The client's authorized contact e-signs an order form for one new TimeBank prepaid block of the
    same size as a block the client already holds, at the quoted price. Signing books the order form as
    signed, opens the new block awaiting payment (no hours granted yet, nothing owed beyond its own
    invoice) and posts the new block's invoice dated today for the quoted price. The contact sees the
    signed order form, the new block in pending-payment status and the new invoice on the account.

    Args:
        customer_id: Id class — the client reference number of the organisation placing the order, as returned by the client profile lookup.
        current_block_id: Id class — the reference number of the client's existing TimeBank block whose size the new block repeats, as returned by the TimeBank block lookup.
        quoted_amount_usd: Fixed-format class — the price quoted on the order form for the new block, in USD, 2 decimal places, a positive amount rounded half up to the cent before it is passed.

    Returns:
        A dict rendered as text with: order_reference (string, reference of the signed order form),
        new_block_reference (string, reference number of the new block), block_size (string, the official
        block size name copied from the existing block), quoted_amount_usd (number, USD with 2 decimal
        places, the signed price), invoice_number (string, INV- followed by 6 digits), invoice_posted_date
        (string, YYYY-MM-DD, today) and status (string, the new block's status, pending_payment). The
        presence of new_block_reference and invoice_number confirms that the order was signed and booked.
    """
    current = (ctx.find("timebank_blocks", timebank_block_id=current_block_id) or [{}])[0]
    size = current.get("variant_name") or ""
    hours = round(float(current.get("hours_purchased") or 0), 2)
    amount = round(float(quoted_amount_usd), 2)
    today = ctx.now()[:10]
    oid = ctx.make_id("tbo_", customer_id, current_block_id, amount)
    ctx.create("timebank_orders", oid, timebank_order_id=oid, customer_id=customer_id, timebank_block_id=None,
               request_type="new_block", requested_variant_name=size, requested_auto_replenish="unchanged",
               quoted_amount_usd=amount, request_status="signed", created_at=ctx.now())
    bid = ctx.make_id("tbb_", customer_id, current_block_id, amount)
    ctx.create("timebank_blocks", bid, timebank_block_id=bid, customer_id=customer_id, variant_name=size,
               status="pending_payment", order_date=today, activation_date="", expiry_date="",
               hours_purchased=hours, hours_balance=0.0, block_price_usd=amount, balance_due_usd=amount,
               auto_replenish=False, extension_count=0, rollover_source_block_id=None, depleted_date="",
               closed_date="")
    invoice = "INV-" + str(int(ctx.make_id("", bid), 16) % 900000 + 100000)
    lid = ctx.make_id("tbl_", bid, invoice)
    ctx.create("timebank_billing", lid, timebank_billing_entry_id=lid, timebank_block_id=bid,
               customer_id=customer_id, event_type="timebank_block_invoice", amount_usd=amount,
               invoice_number=invoice, posted_date=today, billing_period=today[:7], overage_hours=0.0,
               ticket_number="", sow_number="", payment_reference="")
    return str({"order_reference": oid, "new_block_reference": bid, "block_size": size,
                "quoted_amount_usd": amount, "invoice_number": invoice, "invoice_posted_date": today,
                "status": "pending_payment"})


@tool(owner="agent", rw="write")
def post_visit_travel_entry_8d0122c7(ctx: ToolContext, timebank_block_id: str, ticket_number: str,
                                     entry_date: str, time_band: str, hours: float) -> str:
    """Post the travel entry of one onsite date to a TimeBank prepaid block: one travel draw is added to
    the block's hours ledger, dated the given onsite date and booked to the given ticket, and the block's
    remaining hours go down by the travel hours. The client sees the travel line on the block's hours statement and the
    lower remaining balance.

    Args:
        timebank_block_id: Id class — the reference number of the TimeBank block the travel is drawn from, as returned by the TimeBank block lookup.
        ticket_number: Fixed-format class — the service desk ticket the trip is booked to, SB- followed by 7 digits, copied from an onsite-support draw of that date on the block.
        entry_date: Fixed-format class — the onsite date the trip belongs to, YYYY-MM-DD, US Eastern calendar date.
        time_band: Enum class — the band recorded on the travel entry: not_applicable is never used for a travel entry and is listed only because the ledger carries it for non-draw entries; business_hours records a trip drawn at a multiplier of one; after_hours records a trip drawn at the block's after-hours multiplier, which is also how a weekend or holiday trip is drawn and recorded; emergency records a trip drawn at the block's emergency multiplier; holiday is never used for a travel entry, a weekend or holiday trip being recorded after_hours.
        hours: Fixed-format class — the block hours the travel entry draws, hours, 2 decimal places, rounded half up before it is passed.

    Returns:
        A dict rendered as text with: ledger_entry_reference (string, reference of the new travel entry),
        block_reference (string, the block drawn from), ticket_number (string, SB- followed by 7 digits),
        entry_date (string, YYYY-MM-DD), hours (number, hours with 2 decimal places) and
        hours_balance_after (number, hours with 2 decimal places, the block's remaining hours after the
        entry). The ledger_entry_reference confirms that the travel entry was posted.
    """
    amount = round(float(hours), 2)
    lid = ctx.make_id("tbh_", timebank_block_id, ticket_number, entry_date, time_band, amount)
    block = (ctx.find("timebank_blocks", timebank_block_id=timebank_block_id) or [{}])[0]
    ctx.create("timebank_hours_ledger", lid, timebank_ledger_entry_id=lid, timebank_block_id=timebank_block_id,
               customer_id=block.get("customer_id") or "", event_type="timebank_hours_drawn", hours=amount,
               entry_date=entry_date, work_type="travel", time_band=time_band, resource_level="not_applicable",
               worked_minutes=0, ticket_number=ticket_number, sow_number="", original_ledger_entry_id=None,
               counterpart_block_id=None)
    after = round(float(block.get("hours_balance") or 0) - amount, 2)
    ctx.update("timebank_blocks", timebank_block_id, hours_balance=after)
    return str({"ledger_entry_reference": lid, "block_reference": timebank_block_id, "ticket_number": ticket_number,
                "entry_date": entry_date, "hours": amount, "hours_balance_after": after})


class _DrawMath:
    """Value-only helpers for the draw tools (no reads or writes of their own beyond the block lookup)."""

    @staticmethod
    def prep(ctx, prefix, timebank_block_id, ticket_number, sow_number, entry_date, time_band, resource_level,
             worked_minutes, hours):
        amount = round(float(hours), 2)
        lid = ctx.make_id(prefix, timebank_block_id, ticket_number, sow_number, entry_date, time_band,
                          resource_level, int(worked_minutes), amount)
        block = (ctx.find("timebank_blocks", timebank_block_id=timebank_block_id) or [{}])[0]
        after = round(float(block.get("hours_balance") or 0) - amount, 2)
        return lid, block, amount, after


@tool(owner="agent", rw="write")
def post_remote_session_draw_4c084c45(ctx: ToolContext, timebank_block_id: str, ticket_number: str, entry_date: str,
                                      time_band: str, resource_level: str, worked_minutes: int, hours: float) -> str:
    """Draw the block hours of one remote support session from a TimeBank prepaid block: one remote-support draw
    is added to the block's hours ledger for the given service desk ticket and date, and the block's remaining
    hours go down by the hours drawn. The client sees the session on the block's hours statement and the lower
    remaining balance.

    Args:
        timebank_block_id: Id class — the reference number of the TimeBank block the session is drawn from, as returned by the TimeBank block lookup.
        ticket_number: Fixed-format class — the service desk ticket the session was worked on, SB- followed by 7 digits, as shown on the ticket record.
        entry_date: Fixed-format class — the date of the session, YYYY-MM-DD, US Eastern calendar date.
        time_band: Enum class — the band the draw is recorded in: not_applicable is never used for a work draw and is listed only because the ledger carries it for other entries; business_hours records a draw priced at a multiplier of one; after_hours records a draw priced at the block's after-hours multiplier; emergency records an emergency call-out priced with the block's emergency multiplier; holiday records weekend or holiday work priced at the block's holiday multiplier.
        resource_level: Enum class — the level the session is drawn at: not_applicable is never used for a work draw; technician records a draw at the technician ratio; senior_engineer records a draw at the senior engineer ratio; architect records a draw at the solutions architect ratio.
        worked_minutes: Fixed-format class — the minutes the session is drawn for after rounding and any floor, integer minutes.
        hours: Fixed-format class — the block hours the session draws, hours, 2 decimal places, rounded half up before it is passed.

    Returns:
        A dict rendered as text with: ledger_entry_reference (string, reference of the new draw), block_reference
        (string, the block drawn from), ticket_number (string, SB- followed by 7 digits), entry_date (string,
        YYYY-MM-DD), hours (number, hours with 2 decimal places) and hours_balance_after (number, hours with 2
        decimal places, the block's remaining hours after the draw). The ledger_entry_reference confirms the draw.
    """
    lid, block, amount, after = _DrawMath.prep(ctx, "tbs_", timebank_block_id, ticket_number, "",
                                                entry_date, time_band, resource_level, worked_minutes, hours)
    ctx.create("timebank_hours_ledger", lid, timebank_ledger_entry_id=lid, timebank_block_id=timebank_block_id,
               customer_id=block.get("customer_id") or "", event_type="timebank_hours_drawn", hours=amount,
               entry_date=entry_date, work_type="remote_support", time_band=time_band, resource_level=resource_level,
               worked_minutes=int(worked_minutes), ticket_number=ticket_number, sow_number="",
               original_ledger_entry_id=None, counterpart_block_id=None)
    ctx.update("timebank_blocks", timebank_block_id, hours_balance=after)
    return str({"ledger_entry_reference": lid, "block_reference": timebank_block_id, "ticket_number": ticket_number,
                "entry_date": entry_date, "hours": amount, "hours_balance_after": after})


@tool(owner="agent", rw="write")
def post_install_visit_draw_14ae60a8(ctx: ToolContext, timebank_block_id: str, ticket_number: str, entry_date: str,
                                     time_band: str, resource_level: str, worked_minutes: int, hours: float) -> str:
    """Draw the block hours of one onsite installation visit from a TimeBank prepaid block: one onsite-support draw
    is added to the block's hours ledger for the given service desk ticket and visit date, and the block's
    remaining hours go down by the hours drawn. The client sees the visit on the block's hours statement and the
    lower remaining balance.

    Args:
        timebank_block_id: Id class — the reference number of the TimeBank block the visit is drawn from, as returned by the TimeBank block lookup.
        ticket_number: Fixed-format class — the service desk ticket the visit was made on, SB- followed by 7 digits, as shown on the ticket record.
        entry_date: Fixed-format class — the date of the visit, YYYY-MM-DD, US Eastern calendar date.
        time_band: Enum class — the band the draw is recorded in: not_applicable is never used for a work draw and is listed only because the ledger carries it for other entries; business_hours records a draw priced at a multiplier of one; after_hours records a draw priced at the block's after-hours multiplier; emergency records an emergency call-out priced with the block's emergency multiplier; holiday records weekend or holiday work priced at the block's holiday multiplier.
        resource_level: Enum class — the level the visit is drawn at: not_applicable is never used for a work draw; technician records a draw at the technician ratio; senior_engineer records a draw at the senior engineer ratio; architect records a draw at the solutions architect ratio.
        worked_minutes: Fixed-format class — the minutes the visit is drawn for, integer minutes.
        hours: Fixed-format class — the block hours the visit draws, hours, 2 decimal places, rounded half up before it is passed.

    Returns:
        A dict rendered as text with: ledger_entry_reference (string, reference of the new draw), block_reference
        (string, the block drawn from), ticket_number (string, SB- followed by 7 digits), entry_date (string,
        YYYY-MM-DD), hours (number, hours with 2 decimal places) and hours_balance_after (number, hours with 2
        decimal places, the block's remaining hours after the draw). The ledger_entry_reference confirms the draw.
    """
    lid, block, amount, after = _DrawMath.prep(ctx, "tbv_", timebank_block_id, ticket_number, "",
                                                entry_date, time_band, resource_level, worked_minutes, hours)
    ctx.create("timebank_hours_ledger", lid, timebank_ledger_entry_id=lid, timebank_block_id=timebank_block_id,
               customer_id=block.get("customer_id") or "", event_type="timebank_hours_drawn", hours=amount,
               entry_date=entry_date, work_type="onsite_support", time_band=time_band, resource_level=resource_level,
               worked_minutes=int(worked_minutes), ticket_number=ticket_number, sow_number="",
               original_ledger_entry_id=None, counterpart_block_id=None)
    ctx.update("timebank_blocks", timebank_block_id, hours_balance=after)
    return str({"ledger_entry_reference": lid, "block_reference": timebank_block_id, "ticket_number": ticket_number,
                "entry_date": entry_date, "hours": amount, "hours_balance_after": after})


@tool(owner="agent", rw="write")
def post_service_visit_draw_abd20ee9(ctx: ToolContext, timebank_block_id: str, ticket_number: str, entry_date: str,
                                     time_band: str, resource_level: str, worked_minutes: int, hours: float) -> str:
    """Draw the block hours of one onsite service visit (break-fix or support work at the client's site, not an equipment installation) from a TimeBank prepaid block: one onsite-support draw
    is added to the block's hours ledger for the given service desk ticket and visit date, and the block's
    remaining hours go down by the hours drawn. The client sees the visit on the block's hours statement and the
    lower remaining balance.

    Args:
        timebank_block_id: Id class — the reference number of the TimeBank block the visit is drawn from, as returned by the TimeBank block lookup.
        ticket_number: Fixed-format class — the service desk ticket the visit was made on, SB- followed by 7 digits, as shown on the ticket record.
        entry_date: Fixed-format class — the date of the visit, YYYY-MM-DD, US Eastern calendar date.
        time_band: Enum class — the band the draw is recorded in: not_applicable is never used for a work draw and is listed only because the ledger carries it for other entries; business_hours records a draw priced at a multiplier of one; after_hours records a draw priced at the block's after-hours multiplier; emergency records an emergency call-out priced with the block's emergency multiplier; holiday records weekend or holiday work priced at the block's holiday multiplier.
        resource_level: Enum class — the level the visit is drawn at: not_applicable is never used for a work draw; technician records a draw at the technician ratio; senior_engineer records a draw at the senior engineer ratio; architect records a draw at the solutions architect ratio.
        worked_minutes: Fixed-format class — the minutes the visit is drawn for, integer minutes.
        hours: Fixed-format class — the block hours the visit draws, hours, 2 decimal places, rounded half up before it is passed.

    Returns:
        A dict rendered as text with: ledger_entry_reference (string, reference of the new draw), block_reference
        (string, the block drawn from), ticket_number (string, SB- followed by 7 digits), entry_date (string,
        YYYY-MM-DD), hours (number, hours with 2 decimal places) and hours_balance_after (number, hours with 2
        decimal places, the block's remaining hours after the draw). The ledger_entry_reference confirms the draw.
    """
    lid, block, amount, after = _DrawMath.prep(ctx, "tbw_", timebank_block_id, ticket_number, "",
                                                entry_date, time_band, resource_level, worked_minutes, hours)
    ctx.create("timebank_hours_ledger", lid, timebank_ledger_entry_id=lid, timebank_block_id=timebank_block_id,
               customer_id=block.get("customer_id") or "", event_type="timebank_hours_drawn", hours=amount,
               entry_date=entry_date, work_type="onsite_support", time_band=time_band, resource_level=resource_level,
               worked_minutes=int(worked_minutes), ticket_number=ticket_number, sow_number="",
               original_ledger_entry_id=None, counterpart_block_id=None)
    ctx.update("timebank_blocks", timebank_block_id, hours_balance=after)
    return str({"ledger_entry_reference": lid, "block_reference": timebank_block_id, "ticket_number": ticket_number,
                "entry_date": entry_date, "hours": amount, "hours_balance_after": after})


@tool(owner="agent", rw="write")
def post_project_time_draw_e9603a55(ctx: ToolContext, timebank_block_id: str, sow_number: str, entry_date: str,
                                    time_band: str, resource_level: str, worked_minutes: int, hours: float) -> str:
    """Draw the block hours of one group of time-and-materials project time from a TimeBank prepaid block, a
    group being the logged lines of one statement of work, work date and level: one
    project-work draw is added to the block's hours ledger for the given statement of work, work date and level,
    and the block's remaining hours go down by the hours drawn. The client sees the project draw on the block's
    hours statement and the lower remaining balance.

    Args:
        timebank_block_id: Id class — the reference number of the TimeBank block the project time is drawn from, as returned by the TimeBank block lookup.
        sow_number: Fixed-format class — the statement of work the time was logged under, SOW- followed by 6 digits, as shown on the project time log.
        entry_date: Fixed-format class — the date the time was worked, YYYY-MM-DD, US Eastern calendar date.
        time_band: Enum class — the band the draw is recorded in: not_applicable is never used for a work draw and is listed only because the ledger carries it for other entries; business_hours records a draw priced at a multiplier of one; after_hours records a draw priced at the block's after-hours multiplier; emergency records an emergency call-out priced with the block's emergency multiplier; holiday records weekend or holiday work priced at the block's holiday multiplier.
        resource_level: Enum class — the level of the group drawn: not_applicable is never used for a work draw; technician records a draw at the technician ratio; senior_engineer records a draw at the senior engineer ratio; architect records a draw at the solutions architect ratio.
        worked_minutes: Fixed-format class — the minutes the group is drawn for, after any floor or whole-hour rounding the rule applies, integer minutes.
        hours: Fixed-format class — the block hours the group draws, hours, 2 decimal places, rounded half up before it is passed.

    Returns:
        A dict rendered as text with: ledger_entry_reference (string, reference of the new draw), block_reference
        (string, the block drawn from), sow_number (string, SOW- followed by 6 digits), entry_date (string,
        YYYY-MM-DD), hours (number, hours with 2 decimal places) and hours_balance_after (number, hours with 2
        decimal places, the block's remaining hours after the draw). The ledger_entry_reference confirms the draw.
    """
    lid, block, amount, after = _DrawMath.prep(ctx, "tbj_", timebank_block_id, "", sow_number,
                                                entry_date, time_band, resource_level, worked_minutes, hours)
    ctx.create("timebank_hours_ledger", lid, timebank_ledger_entry_id=lid, timebank_block_id=timebank_block_id,
               customer_id=block.get("customer_id") or "", event_type="timebank_hours_drawn", hours=amount,
               entry_date=entry_date, work_type="project_work", time_band=time_band, resource_level=resource_level,
               worked_minutes=int(worked_minutes), ticket_number="", sow_number=sow_number,
               original_ledger_entry_id=None, counterpart_block_id=None)
    ctx.update("timebank_blocks", timebank_block_id, hours_balance=after)
    return str({"ledger_entry_reference": lid, "block_reference": timebank_block_id, "sow_number": sow_number,
                "entry_date": entry_date, "hours": amount, "hours_balance_after": after})


@tool(owner="user", rw="write")
def sign_block_extension_cebc1113(ctx: ToolContext, customer_id: str, timebank_block_id: str, new_expiry_date: str,
                                  quoted_amount_usd: float) -> str:
    """The client's authorized contact e-signs an extension order form for one TimeBank prepaid block at the quoted
    fee. Signing books the extension form as signed, moves the block's expiry date to the new date, counts one more
    extension on the block and posts the extension fee invoice dated today. The contact sees the signed form, the
    later expiry date on the block and the fee invoice on the account.

    Args:
        customer_id: Id class — the client reference number of the organisation the block belongs to, as returned by the client profile lookup.
        timebank_block_id: Id class — the reference number of the TimeBank block being extended, as returned by the TimeBank block lookup.
        new_expiry_date: Fixed-format class — the block's last valid day after the extension, YYYY-MM-DD, US Eastern calendar date.
        quoted_amount_usd: Fixed-format class — the extension fee quoted on the form, in USD, 2 decimal places, a positive amount rounded half up to the cent before it is passed.

    Returns:
        A dict rendered as text with: order_reference (string, reference of the signed extension form),
        block_reference (string, the block extended), new_expiry_date (string, YYYY-MM-DD), extension_count (integer,
        extensions now applied to the block), quoted_amount_usd (number, USD with 2 decimal places), invoice_number
        (string, INV- followed by 6 digits) and invoice_posted_date (string, YYYY-MM-DD, today). The order_reference
        and invoice_number confirm the extension was signed and invoiced.
    """
    amount = round(float(quoted_amount_usd), 2)
    today = ctx.now()[:10]
    block = (ctx.find("timebank_blocks", timebank_block_id=timebank_block_id) or [{}])[0]
    count = int(block.get("extension_count") or 0) + 1
    oid = ctx.make_id("tbo_", customer_id, timebank_block_id, new_expiry_date, amount)
    ctx.create("timebank_orders", oid, timebank_order_id=oid, customer_id=customer_id,
               timebank_block_id=timebank_block_id, request_type="extension", requested_variant_name="not_applicable",
               requested_auto_replenish="unchanged", quoted_amount_usd=amount, request_status="signed",
               created_at=ctx.now())
    ctx.update("timebank_blocks", timebank_block_id, expiry_date=new_expiry_date, extension_count=count,
               balance_due_usd=round(float(block.get("balance_due_usd") or 0) + amount, 2))
    invoice = "INV-" + str(int(ctx.make_id("", oid), 16) % 900000 + 100000)
    lid = ctx.make_id("tbl_", oid, invoice)
    ctx.create("timebank_billing", lid, timebank_billing_entry_id=lid, timebank_block_id=timebank_block_id,
               customer_id=customer_id, event_type="timebank_extension_fee", amount_usd=amount,
               invoice_number=invoice, posted_date=today, billing_period=today[:7], overage_hours=0.0,
               ticket_number="", sow_number="", payment_reference="")
    return str({"order_reference": oid, "block_reference": timebank_block_id, "new_expiry_date": new_expiry_date,
                "extension_count": count, "quoted_amount_usd": amount, "invoice_number": invoice,
                "invoice_posted_date": today})

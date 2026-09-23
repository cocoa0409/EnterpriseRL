"""Hidden task tools for the grain storage desk of Prairie Ridge Cooperative Association.

Each tool performs one atomic write on the member's storage account. None of them computes a
figure, aggregates history or judges whether the write is due: the desk works that out from the
storage policies and the records, and passes the finished value in.
"""

from erlbench import ToolContext, tool


@tool(owner="agent", rw="write")
def charge_storage_accrual_0a686c89(ctx: ToolContext, agreement_id: str, invoice_number: str,
                                    period_start: str, period_end: str, bushels: float,
                                    amount: float) -> str:
    """Raise the storage rent for one closed billing period against a member's storage agreement.

    One call posts a single storage accrual line to the member's storage account: it names the
    period being billed, the bushels the period was billed on and the money charged, and bills it
    on the storage invoice given. The line is posted unpaid, so the money moves straight onto what
    the member owes the elevator and shows on the storage account from that moment. Nothing else on
    the agreement moves: the bushels on hand, the grade of record and the date storage is billed and
    paid through are all left as they stand.

    Args:
        agreement_id: Id class — the internal reference number of the storage agreement being
            billed, as returned by the storage agreement lookup for this member.
        invoice_number: Fixed-format class — the storage invoice this period's rent is billed on,
            written as SI- followed by six digits, e.g. SI-660014, and taken exactly as it appears
            on the storage account rows it is to join; an empty value is not accepted.
        period_start: Fixed-format class — the first day of the billing period being charged, as a
            calendar date in the form YYYY-MM-DD, with no time part and no time zone.
        period_end: Fixed-format class — the last day of the billing period being charged, counted
            inclusively, as a calendar date in the form YYYY-MM-DD, with no time part and no time
            zone.
        bushels: Fixed-format class — the quantity the period was billed on, expressed in bushels to
            2 decimal places, rounded half up at the second decimal, never blank.
        amount: Fixed-format class — the money charged for the period, expressed in USD to 2 decimal
            places, rounded half up at the cent, and always positive on a charge.

    Returns:
        A single line of confirmation text. It carries the new storage account line's own reference,
        the storage invoice the line was billed on, the period it covers as two YYYY-MM-DD dates,
        and the amount charged in USD to 2 decimal places. Receiving that line means the accrual is
        on the member's storage account and standing unpaid; no other line is written.
    """
    owner = ctx.find("storage_agreements", agreement_id=agreement_id)
    customer_id = owner[0].get("customer_id") if owner else ""
    rid = ctx.make_id("chg_", agreement_id, invoice_number, period_start, period_end,
                      bushels, amount)
    ctx.create("storage_charges", rid, charge_id=rid, agreement_id=agreement_id,
               customer_id=customer_id, event_type="storage_accrual_charged",
               charge_date=ctx.now()[:10], period_start=period_start, period_end=period_end,
               charge_type="storage_accrual", bushels=round(float(bushels), 2),
               amount=round(float(amount), 2), invoice_number=invoice_number,
               paid_flag=False, posted_date=ctx.now()[:10])
    return (f"Storage accrual {rid} raised on invoice {invoice_number} for {period_start} to "
            f"{period_end} on {round(float(bushels), 2)} bushels: {round(float(amount), 2)} USD, "
            "standing unpaid on the storage account.")


@tool(owner="user", rw="write")
def settle_storage_charges_68342e7f(ctx: ToolContext, agreement_id: str, invoice_number: str,
                                    amount: float) -> str:
    """Pay off a storage invoice on your own storage agreement and have the payment recorded.

    The member makes this payment themselves: one call clears the storage invoice named on the
    agreement given, recording the money handed over against that invoice and marking it settled, so
    the storage account shows the invoice cleared from that moment. The bushels on hand and the
    grade of record are untouched, and no other invoice on the account is affected.

    Args:
        agreement_id: Id class — the internal reference number of the member's storage agreement the
            invoice stands on, as returned by the storage agreement lookup.
        invoice_number: Fixed-format class — the storage invoice being paid off, written as SI-
            followed by six digits, e.g. SI-660014, exactly as it appears on the storage account
            rows being cleared; an empty value is not accepted.
        amount: Fixed-format class — the money handed over to clear the invoice, expressed in USD to
            2 decimal places, rounded half up at the cent, and always positive.

    Returns:
        A single line of confirmation text carrying the settlement line's own reference, the storage
        invoice cleared, and the amount applied in USD to 2 decimal places. Receiving that line means
        the payment is recorded on the storage account and the invoice named is marked settled.
    """
    owner = ctx.find("storage_agreements", agreement_id=agreement_id)
    customer_id = owner[0].get("customer_id") if owner else ""
    rid = ctx.make_id("stl_", agreement_id, invoice_number, amount)
    ctx.create("storage_charges", rid, charge_id=rid, agreement_id=agreement_id,
               customer_id=customer_id, event_type="storage_charge_settled",
               charge_date=ctx.now()[:10], charge_type="settlement",
               amount=round(float(amount), 2), invoice_number=invoice_number,
               paid_flag=True, posted_date=ctx.now()[:10])
    return (f"Settlement {rid} recorded against storage invoice {invoice_number}: "
            f"{round(float(amount), 2)} USD applied, invoice marked settled.")


@tool(owner="agent", rw="write")
def charge_drying_pass_a57b52cd(ctx: ToolContext, agreement_id: str, moisture_in_pct: float,
                                moisture_out_pct: float, points_removed: float, bushels: float,
                                amount: float) -> str:
    """Raise the conditioning charge for one pass of a member's stored grain through the dryer.

    One call posts a single drying line to the member's storage account, recording the moisture the
    grain went into the dryer at and came out at, the points of moisture taken out, the bushels the
    pass was run on and the money charged for it. The line is posted unpaid, so the charge joins what
    the member owes the elevator and shows on the storage account at once. Bushels on hand are not
    moved by this call and no shrink is taken by it; the grade of record and the standing of the
    agreement are left exactly as they are.

    Args:
        agreement_id: Id class — the internal reference number of the storage agreement the grain is
            held under, as returned by the storage agreement lookup for this member.
        moisture_in_pct: Fixed-format class — the moisture the grain stood at when the pass began,
            given as a percentage to 1 decimal place, rounded half up at the first decimal.
        moisture_out_pct: Fixed-format class — the moisture the grain was left at when the pass
            ended, given as a percentage to 1 decimal place, rounded half up at the first decimal.
        points_removed: Fixed-format class — the moisture taken out by this pass, in percentage
            points to 1 decimal place, rounded half up at the first decimal and never negative.
        bushels: Fixed-format class — the quantity the pass was run on, expressed in bushels to 2
            decimal places, rounded half up at the second decimal.
        amount: Fixed-format class — the money charged for the pass, expressed in USD to 2 decimal
            places, rounded half up at the cent, and always positive on a charge.

    Returns:
        A single line of confirmation text carrying the new storage account line's own reference, the
        moisture readings in and out, the points taken out, the bushels run and the amount charged in
        USD to 2 decimal places. Receiving that line means the conditioning charge stands on the
        member's storage account, unpaid, and that no other line was written.
    """
    owner = ctx.find("storage_agreements", agreement_id=agreement_id)
    customer_id = owner[0].get("customer_id") if owner else ""
    rid = ctx.make_id("dry_", agreement_id, moisture_in_pct, moisture_out_pct, points_removed,
                      bushels, amount)
    ctx.create("storage_charges", rid, charge_id=rid, agreement_id=agreement_id,
               customer_id=customer_id, event_type="storage_drying_charged",
               charge_date=ctx.now()[:10], charge_type="drying",
               billing_basis="per_point_per_bushel", bushels=round(float(bushels), 2),
               amount=round(float(amount), 2), moisture_in_pct=round(float(moisture_in_pct), 1),
               moisture_out_pct=round(float(moisture_out_pct), 1),
               points_removed=round(float(points_removed), 1), paid_flag=False,
               posted_date=ctx.now()[:10])
    return (f"Drying pass {rid} raised: {round(float(moisture_in_pct), 1)} percent in, "
            f"{round(float(moisture_out_pct), 1)} percent out, {round(float(points_removed), 1)} "
            f"points off {round(float(bushels), 2)} bushels, {round(float(amount), 2)} USD standing "
            "unpaid on the storage account.")


@tool(owner="agent", rw="write")
def record_conditioning_shrink_cafcaf64(ctx: ToolContext, agreement_id: str, bushels: float,
                                        points_removed: float, shrink_bushels: float) -> str:
    """Take the conditioning shrink owed on a member's storage agreement off the bushels in store.

    One call posts a single shrink line to the member's storage account: it names the bushels the
    shrink was worked out on, the points of moisture it covers and the bushels taken off, and those
    bushels come off what the account shows in store from that moment. No money moves, since shrink
    is a loss of grain rather than a charge, and the standing of the agreement and its grade of
    record are untouched.

    Args:
        agreement_id: Id class — the internal reference number of the storage agreement the bushels
            are held under, as returned by the storage agreement lookup for this member.
        bushels: Fixed-format class — the quantity the shrink was worked out on, expressed in bushels
            to 2 decimal places, rounded half up at the second decimal.
        points_removed: Fixed-format class — the moisture this shrink line covers, in percentage
            points to 1 decimal place, rounded half up at the first decimal and never negative.
        shrink_bushels: Fixed-format class — the quantity taken off what is held in store, expressed
            in bushels to 2 decimal places, rounded half up at the second decimal and never negative.

    Returns:
        A single line of confirmation text carrying the new storage account line's own reference, the
        bushels the shrink was worked out on, the points covered and the bushels taken off, all in
        bushels to 2 decimal places. Receiving that line means the shrink stands on the member's
        storage account and the bushels it names are off what the account shows in store.
    """
    owner = ctx.find("storage_agreements", agreement_id=agreement_id)
    customer_id = owner[0].get("customer_id") if owner else ""
    rid = ctx.make_id("shr_", agreement_id, bushels, points_removed, shrink_bushels)
    ctx.create("storage_charges", rid, charge_id=rid, agreement_id=agreement_id,
               customer_id=customer_id, event_type="storage_shrink_taken",
               charge_date=ctx.now()[:10], charge_type="shrink_adjustment",
               bushels=round(float(bushels), 2), points_removed=round(float(points_removed), 1),
               shrink_bushels=round(float(shrink_bushels), 2), posted_date=ctx.now()[:10])
    return (f"Shrink line {rid} taken: {round(float(shrink_bushels), 2)} bushels off, worked out on "
            f"{round(float(bushels), 2)} bushels over {round(float(points_removed), 1)} points.")


@tool(owner="user", rw="write")
def reduce_receipt_pledge_f1b6f4e9(ctx: ToolContext, agreement_number: str,
                                   warehouse_receipt_number: str, reserved_bushels: float) -> str:
    """Reduce the bushels you have standing pledged under your own warehouse receipt.

    The member does this themselves: one call rewrites the pledged figure on the storage agreement
    named, so that the receipt given stands against the bushels stated and the rest of the grain
    comes back to being free to move. The bushels in store, the grade of record and the standing of
    the agreement do not change; only what is pledged does, and the member can see the new figure on
    the agreement straight away.

    Args:
        agreement_number: Fixed-format class — the storage agreement number printed on the member's
            storage statements, written as SA- followed by six digits, e.g. SA-208114, and given
            exactly as it appears there; an empty value is not accepted.
        warehouse_receipt_number: Fixed-format class — the negotiable receipt the pledge stands
            under, written as WR- followed by six digits, e.g. WR-003318, copied exactly from the
            agreement it was issued against.
        reserved_bushels: Fixed-format class — the quantity that is to stand pledged once the receipt
            has been reduced, expressed in bushels to 2 decimal places, rounded half up at the second
            decimal and never negative.

    Returns:
        A single line of confirmation text carrying the storage agreement number, the receipt number
        and the pledged quantity now standing, in bushels to 2 decimal places. Receiving that line
        means the agreement carries the new pledged figure and the bushels released are free to move.
    """
    rows = ctx.find("storage_agreements", agreement_number=agreement_number)
    if not rows:
        return f"Error: no storage agreement {agreement_number}."
    key = rows[0].get("agreement_id")
    ctx.update("storage_agreements", key,
               reserved_bushels=round(float(reserved_bushels), 2),
               warehouse_receipt_number=warehouse_receipt_number)
    return (f"Warehouse receipt {warehouse_receipt_number} on agreement {agreement_number} now "
            f"stands against {round(float(reserved_bushels), 2)} bushels.")


@tool(owner="user", rw="write")
def release_loadout_bushels_2fb9cebd(ctx: ToolContext, agreement_id: str, request_id: str,
                                     bushels: float) -> str:
    """Take the grain you asked for out of store against your own signed load-out request.

    The member releases the order themselves: one call records the bushels moving out of store
    against the load-out request named, and those bushels come off what the storage account shows in
    store from that moment. The money side of the account is untouched, and the agreement keeps its
    standing, its grade of record and whatever remains pledged on it.

    Args:
        agreement_id: Id class — the internal reference number of the storage agreement the grain is
            coming out of, as returned by the storage agreement lookup for this member.
        request_id: Id class — the internal reference number of the signed load-out request the order
            is worked against, as returned by the storage service request lookup.
        bushels: Fixed-format class — the quantity actually moving out of store, expressed in bushels
            to 2 decimal places, rounded half up at the second decimal and never negative.

    Returns:
        A single line of confirmation text carrying the new storage account line's own reference, the
        load-out request it was worked against and the bushels moved, in bushels to 2 decimal places.
        Receiving that line means the grain is recorded as out of store and the bushels are off what
        the storage account shows in store.
    """
    owner = ctx.find("storage_agreements", agreement_id=agreement_id)
    customer_id = owner[0].get("customer_id") if owner else ""
    rid = ctx.make_id("lot_", agreement_id, request_id, bushels)
    ctx.create("storage_charges", rid, charge_id=rid, agreement_id=agreement_id,
               customer_id=customer_id, event_type="storage_loadout_recorded",
               charge_date=ctx.now()[:10], charge_type="loadout",
               bushels=round(float(bushels), 2), posted_date=ctx.now()[:10])
    return (f"Load-out {rid} recorded against request {request_id}: "
            f"{round(float(bushels), 2)} bushels out of store.")

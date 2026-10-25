"""Hidden task tools of the tire_treadwear_warranty difficulty (category: tires).

Each tool performs exactly one atomic business write on a Crestline tire set and its
activity history. The values passed in are worked out by the caller beforehand; no tool
checks eligibility, status, ownership, terms or prior entries.
"""

from erlbench import ToolContext, tool


class _Rows:
    """Row assembly helpers (no business logic)."""

    @staticmethod
    def event(ctx, rid, set_row, **fields):
        """Assemble a complete activity-history row with neutral defaults."""
        row = {
            "tire_event_id": rid, "tire_set_id": set_row.get("tire_set_id"),
            "customer_id": set_row.get("customer_id"), "event_type": "", "event_date": ctx.now()[:10],
            "store_id": "", "odometer": 0, "tire_position": "ALL", "appointment_date": "",
            "appointment_time": "", "service_code": "none", "min_tread_depth_32nds": 0,
            "wear_pattern": "none", "defect_code": "none", "current_selling_price": 0.0,
            "miles_driven": 0, "credit_pct": 0, "amount": 0.0, "charge_amount": 0.0,
            "source_tire_event_id": "", "ticket_number": "", "payment_method": "none",
            "refund_reason": "none",
        }
        row.update(fields)
        return row


@tool(owner="agent", rw="write")
def issue_treadwear_adjustment_f769c805(ctx: ToolContext, tire_set_id: str, source_tire_event_id: str,
                                        tire_position: str, current_selling_price: float, miles_driven: int,
                                        credit_pct: int, amount: float) -> str:
    """Issue a prorated treadwear adjustment credit on one wheel position of a customer's Crestline
    tire set, processed by the customer care desk. One call books one adjustment entry for the
    position, citing the tread inspection it rests on and carrying that inspection's odometer, the
    store's selling price of the same tire on the adjustment date, the miles driven, the granted
    percentage and the credit amount; the credit amount is added to the adjustment credit available
    on the set. Once booked, the set shows the higher credit balance and the history shows the new
    adjustment entry. The call succeeds when the receipt below is returned.

    Args:
        tire_set_id: Id class — reference number of the tire set the credit is issued on, as returned by the tire set lookup.
        source_tire_event_id: Id class — reference number of the tread inspection entry the adjustment rests on, as returned by the tire activity history lookup.
        tire_position: Enum class — wheel position adjusted: LF for the left front tire; RF for the right front tire; LR for the left rear tire; RR for the right rear tire; SP for a matching full-size spare that is part of the set; ALL is never an adjusted position and applies only to whole-set services.
        current_selling_price: Fixed-format class — the store's selling price of the same tire on the adjustment date, in USD, 2 decimal places.
        miles_driven: Fixed-format class — miles the adjusted tire has run, in integer miles.
        credit_pct: Fixed-format class — adjustment percentage granted, as an integer percent 0-100.
        amount: Fixed-format class — credit issued on the set for this position, in USD, 2 decimal places, rounded half up to the cent.

    Returns:
        dict with keys: tire_event_id (str, reference number of the new adjustment entry),
        tire_set_id (str), tire_position (str), credit_pct (int), amount (float, USD credit issued),
        adjustment_credit_balance (float, USD credit available on the set after the entry). A
        returned tire_event_id means the adjustment was booked.
    """
    set_row = (ctx.find("tire_sets", tire_set_id=tire_set_id) or [{}])[0]
    source = (ctx.find("tire_events", tire_event_id=source_tire_event_id) or [{}])[0]
    rid = ctx.make_id("tev_", tire_set_id, source_tire_event_id, tire_position, current_selling_price,
                      miles_driven, credit_pct, amount)
    ctx.create("tire_events", rid, **_Rows.event(
        ctx, rid, set_row, event_type="tires_treadwear_adjustment", odometer=int(source.get("odometer") or 0),
        tire_position=tire_position, current_selling_price=round(float(current_selling_price), 2),
        miles_driven=int(miles_driven), credit_pct=int(credit_pct), amount=round(float(amount), 2),
        source_tire_event_id=source_tire_event_id))
    balance = round(float(set_row.get("adjustment_credit_balance") or 0) + round(float(amount), 2), 2)
    ctx.update("tire_sets", tire_set_id, adjustment_credit_balance=balance)
    return str({"tire_event_id": rid, "tire_set_id": tire_set_id, "tire_position": tire_position,
                "credit_pct": int(credit_pct), "amount": round(float(amount), 2),
                "adjustment_credit_balance": balance})


@tool(owner="user", rw="write")
def apply_credit_to_replacement_ticket_eafdabc1(ctx: ToolContext, tire_set_id: str, source_tire_event_id: str,
                                                ticket_number: str, amount: float, balance_due: float) -> str:
    """The customer applies a treadwear adjustment credit of their tire set toward the tire price on a
    replacement tire ticket that is settled when the tire is mounted. One call books one
    credit-applied entry on the set that issued the credit, citing the adjustment that issued it and
    carrying the replacement ticket number, the credit applied and the pre-tax balance the customer
    pays on the replacement ticket's lines after the credit; the credit applied is taken off the
    adjustment credit available on the set. Once booked, the set shows the lower credit balance and
    the history shows the entry against the ticket. The call succeeds when the receipt below is
    returned.

    Args:
        tire_set_id: Id class — reference number of the tire set that holds the credit, as returned by the tire set lookup.
        source_tire_event_id: Id class — reference number of the treadwear adjustment entry that issued the credit, as returned by the tire activity history lookup.
        ticket_number: Fixed-format class — sales ticket number of the replacement tire purchase, T- followed by 8 digits, exactly as shown on that purchase.
        amount: Fixed-format class — credit applied toward the ticket's tire price, in USD, 2 decimal places, rounded half up to the cent.
        balance_due: Fixed-format class — pre-tax balance the customer pays on the replacement ticket's lines after the credit, in USD, 2 decimal places, rounded half up to the cent.

    Returns:
        dict with keys: tire_event_id (str, reference number of the credit-applied entry),
        tire_set_id (str), ticket_number (str), amount (float, USD applied), balance_due (float, USD
        pre-tax balance on the replacement ticket), adjustment_credit_balance (float, USD credit still
        available on the set). A returned tire_event_id means the credit was applied.
    """
    set_row = (ctx.find("tire_sets", tire_set_id=tire_set_id) or [{}])[0]
    rid = ctx.make_id("tev_", tire_set_id, source_tire_event_id, ticket_number, amount, balance_due)
    ctx.create("tire_events", rid, **_Rows.event(
        ctx, rid, set_row, event_type="tires_adjustment_credit_applied", amount=round(float(amount), 2),
        charge_amount=round(float(balance_due), 2), source_tire_event_id=source_tire_event_id,
        ticket_number=ticket_number))
    balance = round(float(set_row.get("adjustment_credit_balance") or 0) - round(float(amount), 2), 2)
    ctx.update("tire_sets", tire_set_id, adjustment_credit_balance=balance)
    return str({"tire_event_id": rid, "tire_set_id": tire_set_id, "ticket_number": ticket_number,
                "amount": round(float(amount), 2), "balance_due": round(float(balance_due), 2),
                "adjustment_credit_balance": balance})


@tool(owner="user", rw="write")
def apply_credit_to_workmanship_share_57ed5afc(ctx: ToolContext, tire_set_id: str, source_tire_event_id: str,
                                               tire_position: str, amount: float) -> str:
    """The customer applies part or all of a treadwear adjustment credit of their tire set toward the
    share they owe on a workmanship replacement made on the same set. One call books one
    credit-applied entry on the set, citing the adjustment that issued the credit and naming the
    wheel position of the workmanship replacement it settles; the amount is taken off the
    adjustment credit available on the set. Once booked, the set shows the lower credit balance and
    the history shows the entry against that position. The call succeeds when the receipt below is
    returned.

    Args:
        tire_set_id: Id class — reference number of the tire set that holds the credit, as returned by the tire set lookup.
        source_tire_event_id: Id class — reference number of the treadwear adjustment entry that issued the credit, as returned by the tire activity history lookup.
        tire_position: Enum class — wheel position of the workmanship replacement whose share is settled: LF for the left front tire; RF for the right front tire; LR for the left rear tire; RR for the right rear tire; SP for a matching full-size spare that is part of the set; ALL is never a workmanship position and applies only to whole-set services.
        amount: Fixed-format class — credit applied toward the workmanship share, in USD, 2 decimal places, rounded half up to the cent.

    Returns:
        dict with keys: tire_event_id (str, reference number of the credit-applied entry),
        tire_set_id (str), tire_position (str), amount (float, USD applied),
        adjustment_credit_balance (float, USD credit still available on the set). A returned
        tire_event_id means the credit was applied.
    """
    set_row = (ctx.find("tire_sets", tire_set_id=tire_set_id) or [{}])[0]
    rid = ctx.make_id("tev_", tire_set_id, source_tire_event_id, tire_position, amount)
    ctx.create("tire_events", rid, **_Rows.event(
        ctx, rid, set_row, event_type="tires_adjustment_credit_applied", tire_position=tire_position,
        amount=round(float(amount), 2), source_tire_event_id=source_tire_event_id))
    balance = round(float(set_row.get("adjustment_credit_balance") or 0) - round(float(amount), 2), 2)
    ctx.update("tire_sets", tire_set_id, adjustment_credit_balance=balance)
    return str({"tire_event_id": rid, "tire_set_id": tire_set_id, "tire_position": tire_position,
                "amount": round(float(amount), 2), "adjustment_credit_balance": balance})


@tool(owner="agent", rw="write")
def cancel_lapsed_tire_order_8987209f(ctx: ToolContext, tire_set_id: str, ticket_number: str, refund_reason: str,
                                      amount: float) -> str:
    """Cancel a customer's ordered tire set that was never mounted and pay its cancellation refund.
    One call moves the set from ordered to cancelled with today's date as its closing date and books
    one refund entry on the set for the refund reason given, carrying the original purchase
    ticket number given and returning the money to the tender that paid that ticket. Once booked, the set
    shows status cancelled and the history shows the refund entry. The call succeeds when the
    receipt below is returned.

    Args:
        tire_set_id: Id class — reference number of the ordered tire set to cancel, as returned by the tire set lookup.
        ticket_number: Fixed-format class — original purchase ticket number of the set being refunded, T- followed by 8 digits, exactly as shown on the set.
        refund_reason: Enum class — why the refund is paid: satisfaction_trial_return when the money is returned because the customer gives the set back under the satisfaction trial; order_cancellation when the money is returned because an ordered set that was never mounted is cancelled; none is never a refund reason and applies only to entries that return no money.
        amount: Fixed-format class — refund paid on the cancelled order, in USD, 2 decimal places, rounded half up to the cent.

    Returns:
        dict with keys: tire_set_id (str), status (str, the set's new status, cancelled),
        closed_date (str, YYYY-MM-DD), refund_event_id (str, reference number of the refund entry),
        ticket_number (str, original purchase ticket refunded), payment_method (str, tender the
        refund goes back to), amount (float, USD refunded). A returned refund_event_id means the
        cancellation and the refund were booked.
    """
    set_row = (ctx.find("tire_sets", tire_set_id=tire_set_id) or [{}])[0]
    today = ctx.now()[:10]
    ctx.update("tire_sets", tire_set_id, status="cancelled", closed_date=today)
    rid = ctx.make_id("tev_", tire_set_id, ticket_number, refund_reason, amount)
    tender = set_row.get("payment_method") or "none"
    ticket = ticket_number
    ctx.create("tire_events", rid, **_Rows.event(
        ctx, rid, set_row, event_type="tires_refund", store_id=set_row.get("store_id") or "",
        amount=round(float(amount), 2), ticket_number=ticket, payment_method=tender,
        refund_reason=refund_reason))
    return str({"tire_set_id": tire_set_id, "status": "cancelled", "closed_date": today,
                "refund_event_id": rid, "ticket_number": ticket, "payment_method": tender,
                "amount": round(float(amount), 2)})


@tool(owner="agent", rw="write")
def record_workmanship_replacement_cc1528ea(ctx: ToolContext, tire_set_id: str, source_tire_event_id: str,
                                            store_id: str, tire_position: str, defect_code: str,
                                            charge_amount: float) -> str:
    """Post to a customer's tire set the workmanship replacement of one defective tire that a Crestline
    store made at an inspection visit. One call books one workmanship replacement entry for the wheel
    position, dated the inspection visit, citing that inspection and carrying its odometer, the
    replacing store, the defect and the customer's share charged; the replacement tire stays on the
    same set. Once booked, the set's history shows the replacement entry with its share. The call
    succeeds when the receipt below is returned.

    Args:
        tire_set_id: Id class — reference number of the tire set the defective tire belongs to, as returned by the tire set lookup.
        source_tire_event_id: Id class — reference number of the tread inspection entry that found the defect, as returned by the tire activity history lookup.
        store_id: Id class — reference number of the Crestline store that replaced the tire, as returned by the store lookup.
        tire_position: Enum class — wheel position replaced: LF for the left front tire; RF for the right front tire; LR for the left rear tire; RR for the right rear tire; SP for a matching full-size spare that is part of the set; ALL is never a replaced position and applies only to whole-set services.
        defect_code: Enum class — manufacturing defect found on the tire: none is never recorded on a replacement and applies only to entries without a defect; tread_separation when the tread is separating from the casing; out_of_round when the tire is out of round; belt_shift when an internal belt has shifted; bead_leak when the bead will not seal on a sound wheel.
        charge_amount: Fixed-format class — share charged to the customer for the replacement, in USD, 2 decimal places, rounded half up to the cent; 0.00 when the replacement is free.

    Returns:
        dict with keys: tire_event_id (str, reference number of the replacement entry),
        tire_set_id (str), tire_position (str), defect_code (str), charge_amount (float, USD share
        charged). A returned tire_event_id means the replacement was posted.
    """
    set_row = (ctx.find("tire_sets", tire_set_id=tire_set_id) or [{}])[0]
    source = (ctx.find("tire_events", tire_event_id=source_tire_event_id) or [{}])[0]
    rid = ctx.make_id("tev_", tire_set_id, source_tire_event_id, store_id, tire_position, defect_code, charge_amount)
    ctx.create("tire_events", rid, **_Rows.event(
        ctx, rid, set_row, event_type="tires_workmanship_replacement", store_id=store_id,
        event_date=str(source.get("event_date") or ctx.now()[:10]), odometer=int(source.get("odometer") or 0),
        tire_position=tire_position, defect_code=defect_code, charge_amount=round(float(charge_amount), 2),
        source_tire_event_id=source_tire_event_id))
    return str({"tire_event_id": rid, "tire_set_id": tire_set_id, "tire_position": tire_position,
                "defect_code": defect_code, "charge_amount": round(float(charge_amount), 2)})


@tool(owner="user", rw="write")
def confirm_trial_return_33503dcd(ctx: ToolContext, tire_set_id: str, request_type: str, odometer: int,
                                  ticket_number: str, refund_reason: str, amount: float,
                                  share_ticket_number: str, share_payment_method: str,
                                  share_amount: float) -> str:
    """The customer confirms the satisfaction-trial return of their active tire set. One call records
    the customer's confirmed return request with the odometer they report, moves the set from active
    to returned with today's date as its closing date, and books one refund entry for the
    refund reason given on the set's original purchase ticket: money back goes to the tender that
    paid that ticket, and an exchange is paid as store credit. When a counter ticket on which a
    workmanship share of the set was paid is given, the same call books a second refund entry for that
    ticket, for the share amount given, to the tender given for that ticket. The call books only these
    tire refund entries and writes nothing on any card account; for a refund entry whose tender is the
    Crestline credit card, the card account's merchandise credit is posted by the refund event's card
    trigger, not by this call. Once booked, the set shows status returned and the history shows the refund
    entries. The call succeeds when the receipt below is returned.

    Args:
        tire_set_id: Id class — reference number of the tire set being returned, as returned by the tire set lookup.
        request_type: Enum class — what the customer takes for the return: satisfaction_refund when the customer wants the money back on the original tender; satisfaction_exchange when the customer wants the value as store credit toward another Crestline tire line.
        odometer: Fixed-format class — odometer reading the customer reports for the vehicle, in integer miles.
        ticket_number: Fixed-format class — original purchase ticket number of the set being refunded, T- followed by 8 digits, exactly as shown on the set.
        refund_reason: Enum class — why the refunds are paid: satisfaction_trial_return when the money is returned because the customer gives the set back under the satisfaction trial; order_cancellation when the money is returned because an ordered set that was never mounted is cancelled; none is never a refund reason and applies only to entries that return no money.
        amount: Fixed-format class — amount returned on the set's purchase ticket, in USD, 2 decimal places, rounded half up to the cent.
        share_ticket_number: Fixed-format class — counter ticket on which a workmanship share of the set was paid, T- followed by 8 digits for Crestline tickets, or M- followed by 10 digits for outside merchants, exactly as shown on the payment record; empty string when no share is refunded.
        share_payment_method: Enum class — tender that paid the share's counter ticket: crestline_card for the Crestline credit card; fleet_account for a fleet account; bank_card for a bank card; cash_or_debit for cash or a debit card; none when no share is refunded.
        share_amount: Fixed-format class — share refunded on that counter ticket, USD, 2 decimal places, positive; read only when share_ticket_number is given.

    Returns:
        dict with keys: tire_return_request_id (str, reference number of the confirmed request),
        tire_set_id (str), status (str, the set's new status, returned), closed_date (str,
        YYYY-MM-DD), refund_event_id (str, reference number of the refund entry on the set's ticket),
        payment_method (str, tender or store credit the amount goes to), amount (float, USD returned on
        the set's ticket), share_refund_event_id (str, reference number of the share refund entry, empty
        when none), share_amount (float, USD returned on the share's ticket). A returned refund_event_id
        means the return and its refunds were booked.
    """
    set_row = (ctx.find("tire_sets", tire_set_id=tire_set_id) or [{}])[0]
    today = ctx.now()[:10]
    qid = ctx.make_id("trq_", tire_set_id, request_type, odometer, amount)
    ctx.create("tire_return_requests", qid, tire_return_request_id=qid,
               customer_id=set_row.get("customer_id"), tire_set_id=tire_set_id, request_type=request_type,
               odometer=int(odometer), request_status="confirmed", created_at=ctx.now())
    ctx.update("tire_sets", tire_set_id, status="returned", closed_date=today)
    tender = "store_credit" if request_type == "satisfaction_exchange" else (set_row.get("payment_method") or "none")
    rid = ctx.make_id("tev_", tire_set_id, ticket_number, refund_reason, amount)
    ctx.create("tire_events", rid, **_Rows.event(
        ctx, rid, set_row, event_type="tires_refund", store_id=set_row.get("store_id") or "",
        amount=round(float(amount), 2), ticket_number=ticket_number,
        payment_method=tender, refund_reason=refund_reason))
    sid = ""
    if share_ticket_number:
        sid = ctx.make_id("tev_", tire_set_id, share_ticket_number, refund_reason, share_amount)
        ctx.create("tire_events", sid, **_Rows.event(
            ctx, sid, set_row, event_type="tires_refund", store_id=set_row.get("store_id") or "",
            amount=round(float(share_amount), 2), ticket_number=share_ticket_number,
            payment_method=share_payment_method, refund_reason=refund_reason))
    return str({"tire_return_request_id": qid, "tire_set_id": tire_set_id, "status": "returned",
                "closed_date": today, "refund_event_id": rid, "payment_method": tender,
                "amount": round(float(amount), 2), "share_refund_event_id": sid,
                "share_amount": round(float(share_amount), 2)})

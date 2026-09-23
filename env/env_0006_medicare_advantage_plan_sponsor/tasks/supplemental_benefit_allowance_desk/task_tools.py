"""Hidden task tools for the supplemental benefit allowance desk.

Each tool performs one atomic act on one allowance programme. None of them
aggregates history, works out an amount, or judges a business precondition:
the representative reads the card's own entries, the member's records and the
plan's published rules, works the figure out, and passes it in.
"""

from erlbench import ToolContext, tool


@tool(owner="agent", rw="write")
def post_dispute_credit_634307a6(ctx: ToolContext, allowance_program_id: str, customer_id: str,
                                 source_ledger_entry_id: str, credit_amount: float,
                                 benefit_period: str) -> str:
    """Put money back onto a member's Healthy Options card against one card transaction the plan
    has decided in the member's favour. One call books a single credit entry on that card's
    running record: the entry names the transaction it relates to, carries the credit as a
    settled amount, and is placed in the benefit period given, so the money returns to the
    allowance it was spent from. The spendable balance held on the programme is raised by the
    same amount, and the member can see the credit and the new balance on the card straight
    away. The call has completed when the confirmation carries the new entry's reference number
    and the balance the card now stands at.

    Args:
        allowance_program_id: Id class — the reference number of the allowance programme whose card
            is credited, as it is returned by a lookup of the member's allowance programmes.
        customer_id: Id class — the member reference number the programme belongs to, as it is
            returned by the member profile lookup.
        source_ledger_entry_id: Id class — the reference number of the single card transaction this
            credit relates to, as it is returned by a lookup of that card's own entries.
        credit_amount: Fixed-format class — the money put back onto the card, in USD to 2 decimal
            places, a positive figure; the direction is carried by the entry itself, so no minus
            sign is used, and an empty value is not accepted.
        benefit_period: Fixed-format class — the benefit period the credit is placed in, written as
            a benefit period as YYYY-Qn, e.g. 2026-Q2, with the quarter in upper case and no spaces.

    Returns:
        A single line of confirmation text. It carries the reference number of the credit entry
        created, the credited amount in USD to two decimal places, the benefit period the entry
        was placed in, and the spendable balance the programme stands at once the credit is on.
        A line carrying that reference number is what indicates the credit was booked.
    """
    rid = ctx.make_id("alw_", allowance_program_id, source_ledger_entry_id,
                      credit_amount, benefit_period)
    amount = round(float(credit_amount), 2)
    ctx.create("allowance_card_ledger", rid, allowance_ledger_entry_id=rid,
               allowance_program_id=allowance_program_id, customer_id=customer_id,
               event_type="allowance_purchase_refund", posted_date=ctx.now()[:10],
               amount=amount, benefit_period=benefit_period, entry_reason="dispute_credit",
               source_ledger_entry_id=source_ledger_entry_id, settlement_status="settled")
    rows = ctx.find("allowance_programs", allowance_program_id=allowance_program_id)
    balance = round(float(rows[0].get("current_balance") or 0) + amount, 2) if rows else amount
    ctx.update("allowance_programs", allowance_program_id, current_balance=balance)
    return (f"Credit {rid} booked on allowance programme {allowance_program_id}: "
            f"{amount:.2f} USD returned in benefit period {benefit_period}; "
            f"the card now stands at {balance:.2f} USD.")


@tool(owner="agent", rw="write")
def post_period_expiry_1d3932f1(ctx: ToolContext, allowance_program_id: str, customer_id: str,
                                source_ledger_entry_id: str, expiry_amount: float,
                                benefit_period: str) -> str:
    """Take an unspent allowance back off a member's Healthy Options card at the close of the
    benefit period it belonged to. One call books a single entry on that card's running record
    that names the load whose unspent part is being taken back, carries the amount taken off,
    and is placed in the benefit period whose allowance it ends. The spendable balance held on
    the programme falls by the same amount, and the member sees the entry and the reduced
    balance on their next statement and on the card. The call has completed when the
    confirmation carries the new entry's reference number and the balance the card now stands at.

    Args:
        allowance_program_id: Id class — the reference number of the allowance programme whose card
            the allowance is taken off, as it is returned by a lookup of the member's allowance
            programmes.
        customer_id: Id class — the member reference number the programme belongs to, as it is
            returned by the member profile lookup.
        source_ledger_entry_id: Id class — the reference number of the single load entry whose
            unspent part is being taken back, as it is returned by a lookup of that card's own
            entries.
        expiry_amount: Fixed-format class — the allowance taken off the card, in USD to 2 decimal
            places, a positive figure; the direction is carried by the entry itself, so no minus
            sign is used, and an empty value is not accepted.
        benefit_period: Fixed-format class — the benefit period whose allowance is being ended,
            written as a benefit period as YYYY-Qn, e.g. 2026-Q2, with the quarter in upper case
            and no spaces.

    Returns:
        A single line of confirmation text. It carries the reference number of the expiry entry
        created, the amount taken off in USD to two decimal places, the benefit period the entry
        was placed in, and the spendable balance the programme stands at once the allowance is
        off. A line carrying that reference number is what indicates the entry was booked.
    """
    rid = ctx.make_id("alw_", allowance_program_id, source_ledger_entry_id,
                      expiry_amount, benefit_period)
    amount = round(float(expiry_amount), 2)
    ctx.create("allowance_card_ledger", rid, allowance_ledger_entry_id=rid,
               allowance_program_id=allowance_program_id, customer_id=customer_id,
               event_type="allowance_period_expiry", posted_date=ctx.now()[:10],
               amount=amount, benefit_period=benefit_period, entry_reason="period_end_expiry",
               source_ledger_entry_id=source_ledger_entry_id, settlement_status="not_applicable")
    rows = ctx.find("allowance_programs", allowance_program_id=allowance_program_id)
    balance = round(float(rows[0].get("current_balance") or 0) - amount, 2) if rows else -amount
    ctx.update("allowance_programs", allowance_program_id, current_balance=balance)
    return (f"Expiry {rid} booked on allowance programme {allowance_program_id}: "
            f"{amount:.2f} USD taken off for benefit period {benefit_period}; "
            f"the card now stands at {balance:.2f} USD.")


@tool(owner="agent", rw="write")
def cancel_catalog_order_88277d51(ctx: ToolContext, allowance_program_id: str, customer_id: str,
                                  source_order_id: str, refund_amount: float,
                                  benefit_period: str, cancellation_reason: str) -> str:
    """Cancel one catalogue order standing against a member's Healthy Options card and put the
    money it took off the card back on. One call records the cancellation against the order
    named, marks that order as cancelled with the reason given, and books a credit entry on the
    card's running record carrying the money returned, placed in the benefit period the order was
    paid from. The spendable balance held on the programme is raised by that amount, the items
    are no longer sent, and the member can see the cancellation and the credit on the card. The
    call has completed when the confirmation carries the cancellation's reference number and the
    balance the card now stands at.

    Args:
        allowance_program_id: Id class — the reference number of the allowance programme the order
            sits on, as it is returned by a lookup of the member's allowance programmes.
        customer_id: Id class — the member reference number the programme belongs to, as it is
            returned by the member profile lookup.
        source_order_id: Id class — the reference number of the single catalogue order being
            cancelled, as it is returned by a lookup of that programme's catalogue orders.
        refund_amount: Fixed-format class — the money put back onto the card for the cancelled
            order, in USD to 2 decimal places, a positive figure; the direction is carried by the
            entry itself, so no minus sign is used, and an empty value is not accepted.
        benefit_period: Fixed-format class — the benefit period the returned money is placed in,
            written as a benefit period as YYYY-Qn, e.g. 2026-Q2, with the quarter in upper case
            and no spaces.
        cancellation_reason: Enum class — why the order is being cancelled, exactly one of:
            not_applicable, which is carried by an order that stands and is not being cancelled at
            all; member_request, where the member themselves asks for the order to be stopped;
            item_out_of_stock, where the plan cannot supply one of the items ordered;
            insufficient_allowance, where the card no longer holds enough to pay for the order;
            address_undeliverable, where the carrier cannot deliver to the address held for the
            member; programme_closed, where the allowance programme the order was paid from is no
            longer open.

    Returns:
        A single line of confirmation text. It carries the reference number of the cancellation
        record created, the reference number of the credit entry booked on the card, the money
        returned in USD to two decimal places, the benefit period it was placed in, and the
        spendable balance the programme stands at. A line carrying those reference numbers is what
        indicates the order was cancelled and the money returned.
    """
    amount = round(float(refund_amount), 2)
    cid = ctx.make_id("alo_", allowance_program_id, source_order_id, cancellation_reason)
    rid = ctx.make_id("alw_", allowance_program_id, source_order_id, refund_amount, benefit_period)
    orders = ctx.find("allowance_catalog_orders", allowance_order_id=source_order_id)
    order_total = round(float(orders[0].get("order_total") or 0), 2) if orders else 0.0
    ctx.create("allowance_catalog_orders", cid, allowance_order_id=cid,
               allowance_program_id=allowance_program_id, customer_id=customer_id,
               event_type="allowance_catalog_order_cancelled", order_date=ctx.now()[:10],
               order_total=order_total, order_status="cancelled",
               cancellation_reason=cancellation_reason, source_order_id=source_order_id)
    ctx.update("allowance_catalog_orders", source_order_id, order_status="cancelled",
               cancellation_reason=cancellation_reason)
    ctx.create("allowance_card_ledger", rid, allowance_ledger_entry_id=rid,
               allowance_program_id=allowance_program_id, customer_id=customer_id,
               event_type="allowance_purchase_refund", posted_date=ctx.now()[:10],
               amount=amount, benefit_period=benefit_period, entry_reason="merchant_refund",
               settlement_status="settled")
    rows = ctx.find("allowance_programs", allowance_program_id=allowance_program_id)
    balance = round(float(rows[0].get("current_balance") or 0) + amount, 2) if rows else amount
    ctx.update("allowance_programs", allowance_program_id, current_balance=balance)
    return (f"Cancellation {cid} recorded against catalogue order {source_order_id}; "
            f"credit {rid} returned {amount:.2f} USD in benefit period {benefit_period}; "
            f"the card now stands at {balance:.2f} USD.")


@tool(owner="user", rw="write")
def close_allowance_programme_5a9eaadb(ctx: ToolContext, allowance_program_id: str,
                                       allowance_benefit_request_id: str,
                                       forfeited_balance: float, program_end_date: str) -> str:
    """Close the member's own Healthy Options card programme and give up what is left on the card.
    One call, made by the member themselves, sets the programme to closed with the last day the
    allowance could be spent, books a single entry on the card's running record carrying the
    balance given up, and leaves the card holding nothing. The card stops working for further
    spending and the member can see the closing entry and a nil balance. The call has completed
    when the confirmation carries the closing entry's reference number and the programme's closed
    standing.

    Args:
        allowance_program_id: Id class — the reference number of the allowance programme being
            closed, which the representative reads out from the member's allowance programme
            record.
        allowance_benefit_request_id: Id class — the reference number of the service request the
            member raised asking for the programme to be closed, which the representative reads out
            from that request.
        forfeited_balance: Fixed-format class — the money still on the card that the member gives
            up, in USD to 2 decimal places, a positive figure; the direction is carried by the
            entry itself, so no minus sign is used, and an empty value is not accepted.
        program_end_date: Fixed-format class — the last day the allowance could be spent, written
            as YYYY-MM-DD in the plan's own service calendar, with no time of day.

    Returns:
        A single line of confirmation text. It carries the reference number of the closing entry
        created, the balance given up in USD to two decimal places, the last day the allowance
        could be spent, and the standing the programme now holds, which is closed. A line carrying
        that reference number and the closed standing is what indicates the programme was closed.
    """
    amount = round(float(forfeited_balance), 2)
    rid = ctx.make_id("alw_", allowance_program_id, allowance_benefit_request_id,
                      forfeited_balance, program_end_date)
    rows = ctx.find("allowance_programs", allowance_program_id=allowance_program_id)
    customer_id = rows[0].get("customer_id") if rows else ""
    closing_day = str(program_end_date)[:10]
    period = f"{closing_day[:4]}-Q{(int(closing_day[5:7]) - 1) // 3 + 1}"
    ctx.create("allowance_card_ledger", rid, allowance_ledger_entry_id=rid,
               allowance_program_id=allowance_program_id, customer_id=customer_id,
               event_type="allowance_balance_forfeiture", posted_date=program_end_date,
               amount=amount, benefit_period=period,
               entry_reason="disenrollment_forfeiture", settlement_status="not_applicable")
    ctx.update("allowance_programs", allowance_program_id, status="closed",
               program_end_date=program_end_date, current_balance=0.0)
    return (f"Allowance programme {allowance_program_id} closed on {program_end_date} against "
            f"request {allowance_benefit_request_id}; closing entry {rid} gave up "
            f"{amount:.2f} USD; the programme now stands at closed with a nil balance.")


@tool(owner="user", rw="write")
def activate_allowance_card_a5740baf(ctx: ToolContext, allowance_program_id: str,
                                     card_number_last_four: str, first_load_amount: float,
                                     benefit_period: str) -> str:
    """Bring a Healthy Options card into use, which only the member can do because only they can say
    the card reached them. One call, made by the member themselves, confirms the card in their hand,
    sets the programme to in use with that day recorded as the day the card was brought into use, and
    books a single load entry on the card's running record carrying the allowance made available,
    placed in the benefit period given. The spendable balance held on the programme rises by that
    amount and the card will work at the till from that moment. The call has completed when the
    confirmation carries the load entry's reference number and the balance the card now stands at.

    Args:
        allowance_program_id: Id class — the reference number of the allowance programme being brought
            into use, which the representative reads out from the member's allowance programme record.
        card_number_last_four: Fixed-format class — the last four digits printed on the card the member
            is holding, exactly four digits with no spaces or punctuation and no other part of the
            number; an empty value is not accepted.
        first_load_amount: Fixed-format class — the allowance made available on the card as it is
            brought into use, in USD to 2 decimal places, a positive figure; the direction is carried
            by the entry itself, so no minus sign is used, and an empty value is not accepted.
        benefit_period: Fixed-format class — the benefit period the allowance made available belongs
            to, written as a benefit period as YYYY-Qn, e.g. 2026-Q2, with the quarter in upper case
            and no spaces.

    Returns:
        A single line of confirmation text. It carries the reference number of the load entry created,
        the allowance made available in USD to two decimal places, the benefit period it was placed
        in, the last four digits of the card now in use, and the spendable balance the programme
        stands at. A line carrying that reference number and the card's last four digits is what
        indicates the card is in use and the allowance is on it.
    """
    amount = round(float(first_load_amount), 2)
    rid = ctx.make_id("alw_", allowance_program_id, card_number_last_four,
                      first_load_amount, benefit_period)
    rows = ctx.find("allowance_programs", allowance_program_id=allowance_program_id)
    customer_id = rows[0].get("customer_id") if rows else ""
    balance = round(float(rows[0].get("current_balance") or 0) + amount, 2) if rows else amount
    ctx.create("allowance_card_ledger", rid, allowance_ledger_entry_id=rid,
               allowance_program_id=allowance_program_id, customer_id=customer_id,
               event_type="allowance_quarterly_load", posted_date=ctx.now()[:10],
               amount=amount, benefit_period=benefit_period,
               entry_reason="enrollment_proration", settlement_status="not_applicable",
               purchase_channel="not_applicable")
    ctx.update("allowance_programs", allowance_program_id, status="active",
               card_activated_date=ctx.now()[:10], card_number_last_four=card_number_last_four,
               current_balance=balance)
    return (f"Card ending {card_number_last_four} on allowance programme {allowance_program_id} is "
            f"now in use; load {rid} made {amount:.2f} USD available in benefit period "
            f"{benefit_period}; the card now stands at {balance:.2f} USD.")


@tool(owner="agent", rw="write")
def post_catch_up_load_838eeda2(ctx: ToolContext, allowance_program_id: str, customer_id: str,
                                source_ledger_entry_id: str, catch_up_amount: float,
                                benefit_period: str) -> str:
    """Make available on a member's Healthy Options card the allowance still owed to them for benefit
    periods that have already gone by, as one extra load that names the load it puts right. One call
    books a single entry on that card's running record carrying the amount owed, naming the earlier
    load it corrects and placed in the benefit period given, and raises the spendable balance held on
    the programme by the same amount. The member can see the entry and the new balance on the card
    straight away. The call has completed when the confirmation carries the new entry's reference
    number and the balance the card now stands at.

    Args:
        allowance_program_id: Id class — the reference number of the allowance programme whose card is
            loaded, as it is returned by a lookup of the member's allowance programmes.
        customer_id: Id class — the member reference number the programme belongs to, as it is
            returned by the member profile lookup.
        source_ledger_entry_id: Id class — the reference number of the single earlier load entry this
            extra load puts right, as it is returned by a lookup of that card's own entries.
        catch_up_amount: Fixed-format class — the allowance still owed that is made available, in USD
            to 2 decimal places, a positive figure; the direction is carried by the entry itself, so
            no minus sign is used, and an empty value is not accepted.
        benefit_period: Fixed-format class — the benefit period the extra load is placed in, written
            as a benefit period as YYYY-Qn, e.g. 2026-Q2, with the quarter in upper case and no
            spaces.

    Returns:
        A single line of confirmation text. It carries the reference number of the extra load entry
        created, the amount made available in USD to two decimal places, the benefit period it was
        placed in, the reference number of the load it puts right, and the spendable balance the
        programme stands at. A line carrying that reference number is what indicates the allowance
        owed is on the card.
    """
    amount = round(float(catch_up_amount), 2)
    rid = ctx.make_id("alw_", allowance_program_id, source_ledger_entry_id,
                      catch_up_amount, benefit_period)
    ctx.create("allowance_card_ledger", rid, allowance_ledger_entry_id=rid,
               allowance_program_id=allowance_program_id, customer_id=customer_id,
               event_type="allowance_bonus_load", posted_date=ctx.now()[:10],
               amount=amount, benefit_period=benefit_period, entry_reason="load_correction",
               source_ledger_entry_id=source_ledger_entry_id, settlement_status="not_applicable",
               purchase_channel="not_applicable")
    rows = ctx.find("allowance_programs", allowance_program_id=allowance_program_id)
    balance = round(float(rows[0].get("current_balance") or 0) + amount, 2) if rows else amount
    ctx.update("allowance_programs", allowance_program_id, current_balance=balance)
    return (f"Extra load {rid} booked on allowance programme {allowance_program_id}: "
            f"{amount:.2f} USD made available in benefit period {benefit_period}, putting right "
            f"load {source_ledger_entry_id}; the card now stands at {balance:.2f} USD.")

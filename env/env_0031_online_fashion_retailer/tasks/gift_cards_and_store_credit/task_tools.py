"""Hidden task tools for the gift_cards_and_store_credit difficulty of env_0031_online_fashion_retailer.

Each tool performs one atomic write on the Gift Cards & Store Credit records (credit_instruments,
credit_transactions, credit_requests). They take the values the agent has already worked out from
the policy and the records, and never judge eligibility, ownership, status or timing themselves.
"""

from erlbench import ToolContext, tool


@tool(owner="agent", rw="write")
def claw_back_instrument_value_f010c427(ctx: ToolContext, instrument_id: str, clawback_reason: str,
                                        return_id: str, order_id: str, clawback_usd: float) -> str:
    """Take value back from one of the customer's stored-value instruments (a Return Store Credit or
    a Bonus Gift Card) because the event that justified that value has been undone. One call books a
    single clawback entry on the instrument for the amount given, tagged with its reason and with the
    return number or order number that caused it, and lowers the instrument's current balance by that
    amount; an instrument whose balance reaches 0.00 is shown as depleted. Afterwards the clawback
    entry appears in the instrument's balance history and the new balance shows on the instrument.

    Args:
        instrument_id: Id class — the reference number of the stored-value instrument the value is
            taken from, as shown by the stored-value instrument lookup for this customer.
        clawback_reason: Enum class — why the value is taken back, exactly one of:
            failed_return_inspection when the inspected return behind an instant Return Store Credit
            is owed less than the instant credit that was loaded;
            qualifying_purchase_refunded when the gift-card purchase that earned a Bonus Gift Card
            has been cancelled or refunded;
            not_applicable only describes balance entries that are not clawbacks and is never the
            reason of a clawback booked with this action.
        return_id: Id class — the return (RMA) number whose inspection caused the clawback, as shown
            by the return lookup; pass "" when the clawback is caused by a refunded gift-card purchase.
        order_id: Id class — the order number whose refunded gift-card purchase caused the clawback,
            as shown by the order lookup; pass "" when the clawback is caused by a return inspection.
        clawback_usd: Fixed-format class — the value taken back, a positive amount in USD with 2
            decimal places (for example 12.40); it is booked as a negative entry of the same size.

    Returns:
        A confirmation sentence naming the new clawback entry reference, the instrument reference,
        the reason, the amount taken back in USD with 2 decimal places, and the instrument's new
        balance in USD with 2 decimal places and its status (active, or depleted at 0.00); the
        presence of the entry reference means the clawback was booked.
    """
    amount = round(float(clawback_usd), 2)
    rows = ctx.find("credit_instruments", instrument_id=instrument_id)
    inst = rows[0] if rows else {}
    holder = inst.get("customer_id", "")
    new_balance = round(float(inst.get("balance_usd") or 0) - amount, 2)
    rid = ctx.make_id("ctx_", instrument_id, clawback_reason, return_id, order_id, amount)
    ctx.create("credit_transactions", rid, credit_txn_id=rid, instrument_id=instrument_id,
               customer_id=holder, event_type="credit_clawed_back", event_date=ctx.now()[:10],
               amount_usd=-amount, load_type="not_applicable", source_reference="",
               order_id=order_id, return_id=return_id, clawback_reason=clawback_reason,
               transfer_reason="not_applicable", counterpart_instrument_id="", cash_out_state="")
    status = inst.get("status", "")
    if new_balance <= 0 and status == "active":
        status = "depleted"
    ctx.update("credit_instruments", instrument_id, balance_usd=new_balance, status=status)
    return (f"Clawback {rid} booked on instrument {instrument_id} ({clawback_reason}): "
            f"{amount:.2f} USD taken back; new balance {new_balance:.2f} USD, status {status}.")


@tool(owner="user", rw="write")
def confirm_balance_cash_out_04a53640(ctx: ToolContext, instrument_id: str, cash_out_state: str,
                                      cash_out_usd: float) -> str:
    """The holder personally confirms that part or all of the balance on one of their own
    stored-value instruments is paid out to them by mailed check under their billing state's
    gift-card law. One call records the holder's confirmed cash-out request for that instrument,
    books a cash-out entry for the amount confirmed, and lowers the instrument's balance by it; when
    nothing is left on the instrument it is closed as cashed out, otherwise it stays active with the
    remaining balance. Afterwards the confirmed request, the cash-out entry and the new balance are
    visible on the account, and the check is mailed for the amount confirmed.

    Args:
        instrument_id: Id class — the reference number of the holder's stored-value instrument being
            cashed out, as read out to the holder from the stored-value instrument lookup.
        cash_out_state: Fixed-format class — the two-letter USPS state code (e.g. CA) of the holder's
            billing state whose gift-card law the cash-out applies, in capital letters.
        cash_out_usd: Fixed-format class — the amount paid out by check, a positive amount in USD
            with 2 decimal places (for example 4.75); it is booked as a negative entry of the same
            size on the instrument.

    Returns:
        A confirmation sentence naming the confirmed request reference, the cash-out entry
        reference, the instrument reference, the amount paid out in USD with 2 decimal places, the
        billing state applied, and the instrument's remaining balance in USD with 2 decimal places
        with its status (active, or closed when nothing remains); the presence of both references
        means the cash-out was confirmed and booked.
    """
    amount = round(float(cash_out_usd), 2)
    rows = ctx.find("credit_instruments", instrument_id=instrument_id)
    inst = rows[0] if rows else {}
    holder = inst.get("customer_id", "")
    new_balance = round(float(inst.get("balance_usd") or 0) - amount, 2)
    req = ctx.make_id("crq_", instrument_id, "cash_out", cash_out_state, amount)
    ctx.create("credit_requests", req, credit_request_id=req, customer_id=holder,
               instrument_id=instrument_id, request_type="cash_out", request_status="confirmed",
               created_at=ctx.now())
    rid = ctx.make_id("ctx_", instrument_id, "cash_out", cash_out_state, amount)
    ctx.create("credit_transactions", rid, credit_txn_id=rid, instrument_id=instrument_id,
               customer_id=holder, event_type="credit_cashed_out", event_date=ctx.now()[:10],
               amount_usd=-amount, load_type="not_applicable", source_reference="", order_id="",
               return_id="", clawback_reason="not_applicable", transfer_reason="not_applicable",
               counterpart_instrument_id="", cash_out_state=cash_out_state)
    if new_balance <= 0:
        ctx.update("credit_instruments", instrument_id, balance_usd=0.0, status="closed",
                   closed_date=ctx.now()[:10], close_reason="cashed_out")
        status = "closed"
    else:
        ctx.update("credit_instruments", instrument_id, balance_usd=new_balance)
        status = inst.get("status", "")
    return (f"Cash-out request {req} confirmed and entry {rid} booked on instrument {instrument_id}: "
            f"{amount:.2f} USD paid by mailed check under {cash_out_state} law; remaining balance "
            f"{max(new_balance, 0):.2f} USD, status {status}.")


@tool(owner="agent", rw="write")
def issue_card_replacement_8a64787f(ctx: ToolContext, instrument_id: str, customer_id: str,
                                    replacement_variant: str, replacement_usd: float) -> str:
    """Issue a replacement for one of the holder's locked stored-value cards. One call creates a new,
    active instrument of the replacement type for the holder, loaded with the replacement value
    given, books the transfer of that value out of the locked card (naming the new card as the
    receiving instrument) and lowers the locked card's balance by it; the locked card is closed as
    replaced when nothing is left on it, and otherwise stays locked holding the remaining value.
    Afterwards the new card, its opening load and the locked card's transfer entry are visible on
    the account.

    Args:
        instrument_id: Id class — the reference number of the locked card being replaced, as shown by
            the stored-value instrument lookup.
        customer_id: Id class — the customer reference number of the holder who receives the
            replacement, as shown by the customer lookup.
        replacement_variant: Enum class — the instrument type issued as the replacement, exactly
            one of the following values;
            Marlowe & Finch e-Gift Card when the locked card's type names the e-Gift Card as its
            replacement type (plastic and electronic gift cards);
            Return Store Credit when the locked card is a Return Store Credit;
            Marlowe & Finch Gift Card is a plastic gift card type that no card names as its
            replacement type, so it is never issued by this action;
            Marlowe Rewards Note is a loyalty reward type that is never replaced, so it is never
            issued by this action;
            Bonus Gift Card is a promotional type that is never replaced, so it is never issued by
            this action;
            Goodwill Credit is a service-recovery type that is never replaced, so it is never issued
            by this action.
        replacement_usd: Fixed-format class — the value loaded onto the replacement, a positive amount
            in USD with 2 decimal places (for example 85.20).

    Returns:
        A confirmation sentence naming the new replacement card reference, its type, the last four
        digits of its card number, the value loaded in USD with 2 decimal places, the transfer entry
        reference on the locked card, and the locked card's remaining balance in USD with 2 decimal
        places with its status (closed when nothing remains, otherwise locked); the presence of the
        new card reference means the replacement was issued.
    """
    amount = round(float(replacement_usd), 2)
    rows = ctx.find("credit_instruments", instrument_id=instrument_id)
    old = rows[0] if rows else {}
    today = ctx.now()[:10]
    new_id = ctx.make_id("ins_", instrument_id, customer_id, replacement_variant, amount)
    digits = int(ctx.make_id("l4_", new_id)[-6:], 16) % 1000
    last4 = "" if replacement_variant == "Return Store Credit" else f"3{digits:03d}"
    ctx.create("credit_instruments", new_id, instrument_id=new_id, customer_id=customer_id,
               variant_name=replacement_variant, status="active", issued_date=today, valid_from_date=today,
               expiry_date=old.get("expiry_date", ""), initial_value_usd=amount, balance_usd=amount,
               card_number_last4=last4, source_reference=instrument_id, registered_date="",
               lock_reason="none", locked_date="", closed_date="", close_reason="none")
    load = ctx.make_id("ctx_", new_id, "replacement_transfer_in", amount)
    ctx.create("credit_transactions", load, credit_txn_id=load, instrument_id=new_id, customer_id=customer_id,
               event_type="credit_loaded", event_date=today, amount_usd=amount,
               load_type="replacement_transfer_in", source_reference=instrument_id, order_id="", return_id="",
               clawback_reason="not_applicable", transfer_reason="not_applicable",
               counterpart_instrument_id="", cash_out_state="")
    out = ctx.make_id("ctx_", instrument_id, "replacement", new_id, amount)
    ctx.create("credit_transactions", out, credit_txn_id=out, instrument_id=instrument_id,
               customer_id=old.get("customer_id", customer_id), event_type="credit_transferred_out",
               event_date=today, amount_usd=-amount, load_type="not_applicable", source_reference="",
               order_id="", return_id="", clawback_reason="not_applicable", transfer_reason="replacement",
               counterpart_instrument_id=new_id, cash_out_state="")
    left = round(float(old.get("balance_usd") or 0) - amount, 2)
    if left <= 0:
        ctx.update("credit_instruments", instrument_id, balance_usd=0.0, status="closed", closed_date=today,
                   close_reason="replaced")
        status = "closed"
    else:
        ctx.update("credit_instruments", instrument_id, balance_usd=left)
        status = old.get("status", "")
    return (f"Replacement {new_id} ({replacement_variant}, card ending {last4 or 'n/a'}) issued with "
            f"{amount:.2f} USD; transfer {out} booked on {instrument_id}, which keeps {max(left, 0):.2f} USD "
            f"and is {status}.")


@tool(owner="user", rw="write")
def confirm_card_consolidation_106a95bf(ctx: ToolContext, source_instrument_id: str,
                                        receiving_instrument_id: str, consolidation_usd: float) -> str:
    """The holder personally confirms combining value from one of their own stored-value cards onto
    another of their own cards. One call records the holder's confirmed consolidation request for
    both cards, moves the amount confirmed off the source card (a transfer entry naming the
    receiving card) and onto the receiving card (a consolidation load naming the source card), and
    updates both balances; the source card is closed as consolidated when nothing is left on it,
    and otherwise stays active with the remaining value. Afterwards the confirmed requests, both
    entries and both new balances are visible on the account.

    Args:
        source_instrument_id: Id class — the reference number of the holder's card the value moves
            off, as read out to the holder from the stored-value instrument lookup.
        receiving_instrument_id: Id class — the reference number of the holder's card that receives
            the value, as read out to the holder from the stored-value instrument lookup.
        consolidation_usd: Fixed-format class — the amount moved between the two cards, a positive
            amount in USD with 2 decimal places (for example 64.10).

    Returns:
        A confirmation sentence naming the confirmed request references, the transfer entry and the
        consolidation load references, the amount moved in USD with 2 decimal places, and the new
        balances of the source and receiving cards in USD with 2 decimal places with the source
        card's status (closed when nothing remains, otherwise active); the presence of the load
        reference means the consolidation was confirmed and booked.
    """
    amount = round(float(consolidation_usd), 2)
    src_rows = ctx.find("credit_instruments", instrument_id=source_instrument_id)
    dst_rows = ctx.find("credit_instruments", instrument_id=receiving_instrument_id)
    src = src_rows[0] if src_rows else {}
    dst = dst_rows[0] if dst_rows else {}
    holder = src.get("customer_id", "")
    now, today = ctx.now(), ctx.now()[:10]
    reqs = []
    for inst in (source_instrument_id, receiving_instrument_id):
        req = ctx.make_id("crq_", inst, "consolidation", source_instrument_id, receiving_instrument_id, amount)
        ctx.create("credit_requests", req, credit_request_id=req, customer_id=holder, instrument_id=inst,
                   request_type="consolidation", request_status="confirmed", created_at=now)
        reqs.append(req)
    out = ctx.make_id("ctx_", source_instrument_id, "consolidation", receiving_instrument_id, amount)
    ctx.create("credit_transactions", out, credit_txn_id=out, instrument_id=source_instrument_id,
               customer_id=holder, event_type="credit_transferred_out", event_date=today, amount_usd=-amount,
               load_type="not_applicable", source_reference="", order_id="", return_id="",
               clawback_reason="not_applicable", transfer_reason="consolidation",
               counterpart_instrument_id=receiving_instrument_id, cash_out_state="")
    load = ctx.make_id("ctx_", receiving_instrument_id, "consolidation_transfer_in", source_instrument_id, amount)
    ctx.create("credit_transactions", load, credit_txn_id=load, instrument_id=receiving_instrument_id,
               customer_id=holder, event_type="credit_loaded", event_date=today, amount_usd=amount,
               load_type="consolidation_transfer_in", source_reference=source_instrument_id, order_id="",
               return_id="", clawback_reason="not_applicable", transfer_reason="not_applicable",
               counterpart_instrument_id="", cash_out_state="")
    src_left = round(float(src.get("balance_usd") or 0) - amount, 2)
    dst_new = round(float(dst.get("balance_usd") or 0) + amount, 2)
    ctx.update("credit_instruments", receiving_instrument_id, balance_usd=dst_new)
    if src_left <= 0:
        ctx.update("credit_instruments", source_instrument_id, balance_usd=0.0, status="closed",
                   closed_date=today, close_reason="consolidated")
        status = "closed"
    else:
        ctx.update("credit_instruments", source_instrument_id, balance_usd=src_left)
        status = src.get("status", "")
    return (f"Consolidation requests {reqs[0]} and {reqs[1]} confirmed; transfer {out} and load {load} "
            f"moved {amount:.2f} USD; source {source_instrument_id} now {max(src_left, 0):.2f} USD ({status}), "
            f"receiving {receiving_instrument_id} now {dst_new:.2f} USD.")

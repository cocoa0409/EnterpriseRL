"""Hidden task tools for the Granite Ridge equipment rental desk.

Each function performs exactly one atomic write on the rental records. None of them
aggregates history, works out an amount, or judges whether a policy condition holds:
the guest services agent reads the records, works the figure out from the collective's
published terms, and passes it in. The tools are absent from every tool list and are
reached only through the unlock/call meta tools.
"""

from erlbench import ToolContext, tool


@tool(owner="agent", rw="write")
def assess_returned_kit_damage_f0dbd642(ctx: ToolContext, rental_event_id: str,
                                        damage_charge_usd: float) -> str:
    """Put a figure on a technician's finding against one item of hire kit. A finding entered when
    kit was checked back in stands on the agreement's rental account at nil until it is assessed;
    one call writes the amount the guest is being asked to bear onto that finding entry and raises
    the amount still to be collected on the agreement the entry belongs to by the same figure. Two
    findings on one agreement are two separate calls. Once the call has gone through, the guest sees
    the figure against that finding on the agreement's rental account and the agreement's
    outstanding figure carries it.

    Args:
        rental_event_id: Id class — the reference number of the technician's finding entry on the
            rental account that is being assessed, read from the rental account entry lookup before
            the call; it identifies the one item and the fault found on it.
        damage_charge_usd: Fixed-format class — the amount the guest is being asked to bear for that
            finding, in USD to 2 decimal places, rounded half up at the last step only; pass 0.00
            where nothing is being asked of the guest.

    Returns:
        A plain-language confirmation string naming the finding entry that was assessed, the
        agreement it belongs to, the amount written onto it and the agreement's outstanding figure
        after the assessment. Receiving that confirmation is what indicates the assessment was
        written; the figure is then readable on the agreement's rental account.
    """
    amount = round(float(damage_charge_usd), 2)
    entries = ctx.find("rentals_ledger", rental_event_id=rental_event_id)
    entry = entries[0] if entries else {}
    rental_id = entry.get("rental_id")
    ctx.update("rentals_ledger", rental_event_id, amount_usd=amount, event_date=ctx.now()[:10])
    rows = ctx.find("rentals_holdings", rental_id=rental_id) if rental_id else []
    holding = rows[0] if rows else {}
    balance = round(float(holding.get("rental_balance_usd") or 0) + amount, 2)
    if rental_id:
        ctx.update("rentals_holdings", rental_id, rental_balance_usd=balance)
    return (f"Finding {rental_event_id} on agreement {rental_id} assessed at {amount:.2f} USD; the "
            f"agreement now shows {balance:.2f} USD still to be collected.")


@tool(owner="agent", rw="write")
def raise_late_handin_fee_417b2597(ctx: ToolContext, rental_id: str,
                                   late_fee_amount_usd: float) -> str:
    """Raise the shop's fee for kit handed in after the date written on the rental agreement. One
    call books a single late hand-in fee entry on that agreement's rental account for the amount
    given and raises the amount still to be collected on the agreement by the same figure. The
    agreement itself is not moved to another state by this call. Afterwards the guest sees the late
    hand-in fee and its amount on the agreement's rental account, and the agreement's outstanding
    figure carries it.

    Args:
        rental_id: Id class — the reference number of the rental agreement the fee is being raised
            against, read from the rental agreement lookup before the call.
        late_fee_amount_usd: Fixed-format class — the amount of the late hand-in fee, in USD to 2
            decimal places, rounded half up at the last step only; pass 0.00 where no fee is being
            raised.

    Returns:
        A plain-language confirmation string naming the reference number minted for the new fee
        entry, the agreement it was raised against, the amount booked and the agreement's
        outstanding figure after the entry. Receiving that confirmation is what indicates the fee
        was raised; the entry is then readable on the agreement's rental account.
    """
    rid = ctx.make_id("rlf_", rental_id, late_fee_amount_usd)
    amount = round(float(late_fee_amount_usd), 2)
    rows = ctx.find("rentals_holdings", rental_id=rental_id)
    holding = rows[0] if rows else {}
    balance = round(float(holding.get("rental_balance_usd") or 0) + amount, 2)
    ctx.create("rentals_ledger", rid, rental_event_id=rid, rental_id=rental_id,
               customer_id=holding.get("customer_id"), event_type="rentals_fee_charge",
               season_code=holding.get("season_code"), event_date=ctx.now()[:10],
               amount_usd=amount, charge_category="late_return_fee")
    ctx.update("rentals_holdings", rental_id, rental_balance_usd=balance)
    return (f"Late hand-in fee {rid} raised on agreement {rental_id} at {amount:.2f} USD; the "
            f"agreement now shows {balance:.2f} USD still to be collected.")


@tool(owner="user", rw="write")
def settle_rental_balance_at_counter_64bcc7e2(ctx: ToolContext, rental_id: str,
                                              payment_amount_usd: float) -> str:
    """Let the guest hand over money themselves against what their rental agreement still owes the
    shop, paying with the card they present at the counter. One call books a single payment entry on
    that agreement's rental account for the amount the guest hands over and lowers the amount still
    to be collected on the agreement by the same figure. Afterwards the guest sees the payment and
    its amount on the agreement's rental account and the agreement's outstanding figure drops by it.

    Args:
        rental_id: Id class — the reference number of the rental agreement the guest is paying
            against, read from the rental agreement lookup before the call.
        payment_amount_usd: Fixed-format class — the amount of money the guest hands over, in USD to
            2 decimal places, rounded half up at the last step only; pass 0.00 where the guest hands
            over nothing.

    Returns:
        A plain-language confirmation string naming the reference number minted for the new payment
        entry, the agreement it was taken against, the amount collected and the agreement's
        outstanding figure after the payment. Receiving that confirmation is what indicates the
        money was taken; the entry is then readable on the agreement's rental account.
    """
    rid = ctx.make_id("rpm_", rental_id, payment_amount_usd)
    amount = round(float(payment_amount_usd), 2)
    rows = ctx.find("rentals_holdings", rental_id=rental_id)
    holding = rows[0] if rows else {}
    balance = round(float(holding.get("rental_balance_usd") or 0) - amount, 2)
    ctx.create("rentals_ledger", rid, rental_event_id=rid, rental_id=rental_id,
               customer_id=holding.get("customer_id"), event_type="rentals_payment",
               season_code=holding.get("season_code"), event_date=ctx.now()[:10],
               amount_usd=amount, payment_method="card_at_desk")
    ctx.update("rentals_holdings", rental_id, rental_balance_usd=balance)
    return (f"Payment {rid} of {amount:.2f} USD taken at the counter against agreement "
            f"{rental_id}; the agreement now shows {balance:.2f} USD still to be collected.")


@tool(owner="agent", rw="write")
def release_rental_security_hold_9f65c28a(ctx: ToolContext, rental_id: str,
                                          release_amount_usd: float,
                                          deposit_status: str) -> str:
    """Give the guest back the security hold taken against their rental agreement, in whole or in
    part. One call books a single release entry on that agreement's rental account for the amount
    going back to the payment method the hold was placed on, notes where the hold stands afterwards,
    and lowers the security hold standing against the agreement by the amount released. Afterwards
    the guest sees the release and its amount on the agreement's rental account and the hold showing
    against their payment method drops by it.

    Args:
        rental_id: Id class — the reference number of the rental agreement whose security hold is
            being given back, read from the rental agreement lookup before the call.
        release_amount_usd: Fixed-format class — the amount going back to the guest, in USD to 2
            decimal places, rounded half up at the last step only; pass 0.00 where nothing is going
            back.
        deposit_status: Enum class — where the security hold stands once this entry is booked, and
            one of the following: none where the entry does not touch a security hold at all; held where the hold
            stands untouched in full against the agreement; released where the whole of the hold
            standing has gone back to the guest; partially_forfeited where part of the hold has gone
            back and the rest is kept against what the agreement still owes; forfeited where none of
            the hold has gone back and the whole of it is kept.

    Returns:
        A plain-language confirmation string naming the reference number minted for the new release
        entry, the agreement it was booked against, the amount going back, where the hold stands
        afterwards and the security hold still standing against the agreement. Receiving that
        confirmation is what indicates the release was booked; the entry is then readable on the
        agreement's rental account.
    """
    rid = ctx.make_id("rdr_", rental_id, release_amount_usd, deposit_status)
    amount = round(float(release_amount_usd), 2)
    rows = ctx.find("rentals_holdings", rental_id=rental_id)
    holding = rows[0] if rows else {}
    standing = round(float(holding.get("damage_deposit_usd") or 0) - amount, 2)
    ctx.create("rentals_ledger", rid, rental_event_id=rid, rental_id=rental_id,
               customer_id=holding.get("customer_id"), event_type="rentals_deposit_release",
               season_code=holding.get("season_code"), event_date=ctx.now()[:10],
               amount_usd=amount, deposit_status=deposit_status, payment_method="card_on_file")
    ctx.update("rentals_holdings", rental_id, damage_deposit_usd=standing)
    return (f"Release {rid} of {amount:.2f} USD booked against agreement {rental_id}; the hold now "
            f"stands at {standing:.2f} USD and is recorded as {deposit_status}.")


@tool(owner="agent", rw="write")
def raise_model_change_fee_b751c3b4(ctx: ToolContext, rental_id: str,
                                    change_fee_amount_usd: float) -> str:
    """Raise the shop's fee for a change of model or size already recorded on a rental agreement.
    One call books a single change-of-model fee entry on that agreement's rental account for the
    amount given and raises the amount still to be collected on the agreement by the same figure.
    The kit written on the agreement is not touched by this call, only the money owed for having
    changed it. Afterwards the guest sees the change-of-model fee and its amount on the agreement's
    rental account and the agreement's outstanding figure carries it.

    Args:
        rental_id: Id class — the reference number of the rental agreement whose change of model is
            being charged for, read from the rental agreement lookup before the call.
        change_fee_amount_usd: Fixed-format class — the amount of the change-of-model fee, in USD to
            2 decimal places, rounded half up at the last step only; pass 0.00 where no fee is being
            raised.

    Returns:
        A plain-language confirmation string naming the reference number minted for the new fee
        entry, the agreement it was raised against, the amount booked and the agreement's
        outstanding figure after the entry. Receiving that confirmation is what indicates the fee
        was raised; the entry is then readable on the agreement's rental account.
    """
    rid = ctx.make_id("rcf_", rental_id, change_fee_amount_usd)
    amount = round(float(change_fee_amount_usd), 2)
    rows = ctx.find("rentals_holdings", rental_id=rental_id)
    holding = rows[0] if rows else {}
    balance = round(float(holding.get("rental_balance_usd") or 0) + amount, 2)
    ctx.create("rentals_ledger", rid, rental_event_id=rid, rental_id=rental_id,
               customer_id=holding.get("customer_id"), event_type="rentals_fee_charge",
               season_code=holding.get("season_code"), event_date=ctx.now()[:10],
               amount_usd=amount, charge_category="swap_fee", quantity=1,
               item_serial=holding.get("item_serial"))
    ctx.update("rentals_holdings", rental_id, rental_balance_usd=balance)
    return (f"Change-of-model fee {rid} raised on agreement {rental_id} at {amount:.2f} USD; the "
            f"agreement now shows {balance:.2f} USD still to be collected.")


@tool(owner="agent", rw="write")
def raise_rental_rate_charge_fcd244c0(ctx: ToolContext, rental_id: str,
                                      rate_charge_amount_usd: float) -> str:
    """Put the hire rate for a rental agreement onto its rental account. One call books a single
    hire-rate entry on that agreement's rental account for the amount given, covering the days the
    agreement was written for, and raises the amount still to be collected on the agreement by the
    same figure. Add-ons the guest took are separate entries and are not touched by this call.
    Afterwards the guest sees the hire rate and its amount on the agreement's rental account and the
    agreement's outstanding figure carries it.

    Args:
        rental_id: Id class — the reference number of the rental agreement the hire rate is being
            put on, read from the rental agreement lookup before the call.
        rate_charge_amount_usd: Fixed-format class — the hire rate for the agreement, in USD to 2
            decimal places, rounded half up at the last step only; pass 0.00 where no hire rate is
            being raised.

    Returns:
        A plain-language confirmation string naming the reference number minted for the new hire
        rate entry, the agreement it was raised against, the amount booked, the number of days it
        covers and the agreement's outstanding figure after the entry. Receiving that confirmation
        is what indicates the hire rate was raised; the entry is then readable on the agreement's
        rental account.
    """
    rid = ctx.make_id("rrc_", rental_id, rate_charge_amount_usd)
    amount = round(float(rate_charge_amount_usd), 2)
    rows = ctx.find("rentals_holdings", rental_id=rental_id)
    holding = rows[0] if rows else {}
    days = int(float(holding.get("rental_days_booked") or 0))
    balance = round(float(holding.get("rental_balance_usd") or 0) + amount, 2)
    ctx.create("rentals_ledger", rid, rental_event_id=rid, rental_id=rental_id,
               customer_id=holding.get("customer_id"), event_type="rentals_rate_charge",
               season_code=holding.get("season_code"), event_date=ctx.now()[:10],
               amount_usd=amount, charge_category="rental_rate", quantity=days)
    ctx.update("rentals_holdings", rental_id, rental_balance_usd=balance)
    return (f"Hire rate {rid} raised on agreement {rental_id} at {amount:.2f} USD covering {days} "
            f"day(s); the agreement now shows {balance:.2f} USD still to be collected.")


@tool(owner="user", rw="write")
def confirm_rental_extension_b56bb368(ctx: ToolContext, rental_id: str, new_due_date: str,
                                      extension_charge_usd: float) -> str:
    """Let the guest themselves confirm keeping their hire kit longer. One call moves the date the
    kit is due back on their rental agreement out to the date given, widens the number of days the
    agreement covers by the days added, books a single extension entry on the agreement's rental
    account for the amount the guest is accepting, and raises the amount still to be collected on
    the agreement by that amount. Afterwards the guest sees the later due date on the agreement and
    the extension and its amount on the rental account.

    Args:
        rental_id: Id class — the reference number of the rental agreement the guest is keeping
            longer, read from the rental agreement lookup before the call.
        new_due_date: Fixed-format class — the date the kit is now due back, written as YYYY-MM-DD
            on the shop's local calendar, with no time of day and no empty-value convention; a date
            must always be given.
        extension_charge_usd: Fixed-format class — the amount the guest is accepting for keeping the
            kit longer, in USD to 2 decimal places, rounded half up at the last step only; pass 0.00
            where nothing is being charged.

    Returns:
        A plain-language confirmation string naming the reference number minted for the new
        extension entry, the agreement it was booked against, the date the kit is now due back, the
        number of days added, the amount booked and the agreement's outstanding figure after the
        entry. Receiving that confirmation is what indicates the extension was taken; the later due
        date and the entry are then readable on the agreement and its rental account.
    """
    rid = ctx.make_id("rxt_", rental_id, new_due_date, extension_charge_usd)
    amount = round(float(extension_charge_usd), 2)
    rows = ctx.find("rentals_holdings", rental_id=rental_id)
    holding = rows[0] if rows else {}
    def day_number(text):
        """Serial day number of a YYYY-MM-DD date, by civil-calendar arithmetic alone: no clock is
        read and no module is imported, so two dates can be subtracted deterministically."""
        parts = str(text)[:10].split("-")
        year, month, day = int(parts[0]), int(parts[1]), int(parts[2])
        year -= 1 if month <= 2 else 0
        era = (year if year >= 0 else year - 399) // 400
        year_of_era = year - era * 400
        day_of_year = (153 * (month + (-3 if month > 2 else 9)) + 2) // 5 + day - 1
        day_of_era = year_of_era * 365 + year_of_era // 4 - year_of_era // 100 + day_of_year
        return era * 146097 + day_of_era - 719468
    added = max(0, day_number(new_due_date) - day_number(holding.get("due_date") or new_due_date))
    booked = int(float(holding.get("rental_days_booked") or 0)) + added
    balance = round(float(holding.get("rental_balance_usd") or 0) + amount, 2)
    ctx.create("rentals_ledger", rid, rental_event_id=rid, rental_id=rental_id,
               customer_id=holding.get("customer_id"), event_type="rentals_fee_charge",
               season_code=holding.get("season_code"), event_date=ctx.now()[:10],
               amount_usd=amount, charge_category="extension_fee", quantity=added)
    ctx.update("rentals_holdings", rental_id, due_date=new_due_date,
               rental_days_booked=booked, rental_balance_usd=balance)
    return (f"Extension {rid} taken on agreement {rental_id}: the kit is now due back on "
            f"{new_due_date}, {added} day(s) added, {amount:.2f} USD booked, and the agreement now "
            f"shows {balance:.2f} USD still to be collected.")

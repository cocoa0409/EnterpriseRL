"""Hidden task tools for the Granite Ridge snowsports school desk.

Each function here performs one atomic school-account write with the values the agent has
already worked out from the published terms and the records. None of them aggregates history,
prices anything, or judges whether the write is due: those decisions belong to the agent.
"""

from erlbench import ToolContext, tool


@tool(owner="agent", rw="write")
def issue_weather_session_credit_1ce20aea(ctx: ToolContext, lesson_id: str,
                                          credit_amount_usd: float) -> str:
    """Put school credit on a snowsports school booking to make good a session the collective
    could not run because of weather or mountain conditions. One call writes a single credit
    entry on that booking's school account carrying the amount handed back and the note that it
    answers for a session lost to the mountain, and raises the school credit standing on the
    booking record by the same amount, so the household can see the credit sitting against the
    booking and spend it on school charges. The call has completed when the confirmation naming
    the new credit entry and the amount credited comes back.

    Args:
        lesson_id: Id class — the reference number of the snowsports school booking whose account
            the credit is put on, read from the school booking lookup for the household account.
        credit_amount_usd: Fixed-format class — the amount of school credit handed back, expressed
            in USD as a positive number carried to 2 decimal places and rounded half up at the
            cent; it is stored exactly as passed and an empty value is not accepted.

    Returns:
        A confirmation sentence carrying the reference number minted for the new school credit
        entry, the booking reference the entry sits on, the credited amount in USD to two decimal
        places, and the school credit total now standing on that booking in USD to two decimal
        places. The presence of that sentence is what indicates the credit entry was written.
    """
    rows = ctx.find("lessons_holdings", lesson_id=lesson_id)
    holding = rows[0] if rows else {}
    amount = round(float(credit_amount_usd), 2)
    rid = ctx.make_id("lsev_", lesson_id, credit_amount_usd)
    ctx.create("lessons_ledger", rid, lesson_event_id=rid, lesson_id=lesson_id,
               customer_id=holding.get("customer_id"), event_type="lessons_credit_issue",
               season_code=holding.get("season_code"), event_date=ctx.now()[:10],
               amount_usd=amount, credit_reason="weather_credit", payment_method="none")
    standing = round(float(holding.get("lesson_credit_usd") or 0) + amount, 2)
    ctx.update("lessons_holdings", lesson_id, lesson_credit_usd=standing)
    return (f"School credit entry {rid} written on booking {lesson_id}: {amount:.2f} USD credited; "
            f"school credit now standing on the booking is {standing:.2f} USD.")


@tool(owner="user", rw="write")
def settle_school_balance_78bdef11(ctx: ToolContext, lesson_id: str, payment_amount_usd: float,
                                   payment_method: str) -> str:
    """Hand money over against what a household owes the snowsports school on one of its bookings.
    One call writes a single payment entry on that booking's school account carrying the amount
    handed over and the way it was taken, and lowers the amount still to be collected on the
    booking record by the same amount, so the household can see the payment on the account and the
    smaller figure still outstanding. The call has completed when the confirmation naming the new
    payment entry and the remaining figure comes back.

    Args:
        lesson_id: Id class — the reference number of the snowsports school booking the money is
            paid against, read from the school booking lookup for the household account.
        payment_amount_usd: Fixed-format class — the amount handed over, expressed in USD as a
            positive number carried to 2 decimal places and rounded half up at the cent; it is
            stored exactly as passed and an empty value is not accepted.
        payment_method: Enum class — how the money is taken, exactly one of: card_on_file where it
            is taken from the payment card the household keeps registered with the collective;
            card_at_desk where the household presents a card in person at a desk or shop; bank_transfer
            where the household sends the money from a bank account; school_credit where school credit
            already standing is what settles the amount rather than new money; gift_card where a
            Granite Ridge gift card is redeemed for it; none where the entry moves no money at all.

    Returns:
        A confirmation sentence carrying the reference number minted for the new payment entry, the
        booking reference the entry sits on, the amount taken in USD to two decimal places, the way
        it was taken, and the amount still to be collected on that booking in USD to two decimal
        places. The presence of that sentence is what indicates the payment entry was written.
    """
    rows = ctx.find("lessons_holdings", lesson_id=lesson_id)
    holding = rows[0] if rows else {}
    amount = round(float(payment_amount_usd), 2)
    rid = ctx.make_id("lsev_", lesson_id, payment_amount_usd, payment_method)
    ctx.create("lessons_ledger", rid, lesson_event_id=rid, lesson_id=lesson_id,
               customer_id=holding.get("customer_id"), event_type="lessons_payment",
               season_code=holding.get("season_code"), event_date=ctx.now()[:10],
               amount_usd=amount, payment_method=payment_method, credit_reason="none")
    outstanding = round(float(holding.get("tuition_balance_usd") or 0) - amount, 2)
    ctx.update("lessons_holdings", lesson_id, tuition_balance_usd=outstanding)
    return (f"Payment entry {rid} written on booking {lesson_id}: {amount:.2f} USD taken by "
            f"{payment_method}; {outstanding:.2f} USD still to be collected on the booking.")


@tool(owner="agent", rw="write")
def raise_session_tuition_charge_38aef0d5(ctx: ToolContext, lesson_id: str,
                                          tuition_amount_usd: float) -> str:
    """Put the tuition due for a snowsports school booking onto that booking's school account. One
    call writes a single tuition entry carrying the amount the household is being asked for, and
    raises the amount still to be collected on the booking record by the same amount, so the tuition
    appears on the account and the household can be asked to pay it. The call has completed when the
    confirmation naming the new tuition entry and the amount still outstanding comes back.

    Args:
        lesson_id: Id class — the reference number of the snowsports school booking the tuition is
            put on, read from the school booking lookup for the household account.
        tuition_amount_usd: Fixed-format class — the amount of tuition being raised, expressed in USD
            as a positive number carried to 2 decimal places and rounded half up at the cent; it is
            stored exactly as passed and an empty value is not accepted.

    Returns:
        A confirmation sentence carrying the reference number minted for the new tuition entry, the
        booking reference the entry sits on, the tuition raised in USD to two decimal places, and the
        amount still to be collected on that booking in USD to two decimal places. The presence of
        that sentence is what indicates the tuition entry was written.
    """
    rows = ctx.find("lessons_holdings", lesson_id=lesson_id)
    holding = rows[0] if rows else {}
    amount = round(float(tuition_amount_usd), 2)
    rid = ctx.make_id("lsev_", lesson_id, tuition_amount_usd)
    ctx.create("lessons_ledger", rid, lesson_event_id=rid, lesson_id=lesson_id,
               customer_id=holding.get("customer_id"), event_type="lessons_tuition_charge",
               season_code=holding.get("season_code"), event_date=ctx.now()[:10],
               amount_usd=amount, charge_category="tuition", payment_method="card_on_file",
               credit_reason="none")
    outstanding = round(float(holding.get("tuition_balance_usd") or 0) + amount, 2)
    ctx.update("lessons_holdings", lesson_id, tuition_balance_usd=outstanding)
    return (f"Tuition entry {rid} written on booking {lesson_id}: {amount:.2f} USD raised; "
            f"{outstanding:.2f} USD still to be collected on the booking.")


@tool(owner="agent", rw="write")
def raise_lift_access_addon_aea17349(ctx: ToolContext, lesson_id: str, addon_charge_usd: float,
                                     session_date: str) -> str:
    """Put the lift access a lesson day needs onto a snowsports school booking as an add-on. One call
    writes a single add-on entry carrying the amount charged for the lift ticket and the session date
    it covers, and raises the amount still to be collected on the booking record by the same amount,
    so the participant can ride the lifts on that date and the household sees the extra on the school
    account. The call has completed when the confirmation naming the new add-on entry and the amount
    still outstanding comes back.

    Args:
        lesson_id: Id class — the reference number of the snowsports school booking the lift access
            is put on, read from the school booking lookup for the household account.
        addon_charge_usd: Fixed-format class — the amount charged for the lift access, expressed in
            USD as a positive number carried to 2 decimal places and rounded half up at the cent; it
            is stored exactly as passed and an empty value is not accepted.
        session_date: Fixed-format class — the lesson date the lift access covers, written as a
            calendar date in the form YYYY-MM-DD on the mountain's local calendar, with no time of
            day and no time zone; an empty value is not accepted.

    Returns:
        A confirmation sentence carrying the reference number minted for the new add-on entry, the
        booking reference the entry sits on, the session date the lift access covers, the amount
        charged in USD to two decimal places, and the amount still to be collected on that booking in
        USD to two decimal places. The presence of that sentence is what indicates the add-on entry
        was written.
    """
    rows = ctx.find("lessons_holdings", lesson_id=lesson_id)
    holding = rows[0] if rows else {}
    amount = round(float(addon_charge_usd), 2)
    rid = ctx.make_id("lsev_", lesson_id, addon_charge_usd, session_date)
    ctx.create("lessons_ledger", rid, lesson_event_id=rid, lesson_id=lesson_id,
               customer_id=holding.get("customer_id"), event_type="lessons_equipment_addon",
               season_code=holding.get("season_code"), event_date=ctx.now()[:10],
               session_date=session_date, amount_usd=amount, quantity=1,
               charge_category="lift_ticket_addon", payment_method="none", credit_reason="none")
    outstanding = round(float(holding.get("tuition_balance_usd") or 0) + amount, 2)
    ctx.update("lessons_holdings", lesson_id, tuition_balance_usd=outstanding)
    return (f"Add-on entry {rid} written on booking {lesson_id}: lift access for {session_date} at "
            f"{amount:.2f} USD; {outstanding:.2f} USD still to be collected on the booking.")


@tool(owner="user", rw="write")
def confirm_lesson_date_change_58e66cab(ctx: ToolContext, lesson_id: str, new_session_date: str,
                                        change_fee_usd: float) -> str:
    """Move a snowsports school booking to another date and take on the fee that the move costs. One
    call rewrites the date the booking's first session is due to run, counts the move against the
    booking's tally of moves, writes a single school fee entry for the change of date, and raises the
    amount still to be collected on the booking record by that fee, so the household sees the new
    lesson date on the booking and the fee on the school account. The call has completed when the
    confirmation naming the new date, the new fee entry and the amount still outstanding comes back.

    Args:
        lesson_id: Id class — the reference number of the snowsports school booking being moved, read
            from the school booking lookup for the household account.
        new_session_date: Fixed-format class — the date the first session is to run on instead,
            written as a calendar date in the form YYYY-MM-DD on the mountain's local calendar, with
            no time of day and no time zone; an empty value is not accepted.
        change_fee_usd: Fixed-format class — the fee the move costs, expressed in USD as a positive
            number carried to 2 decimal places and rounded half up at the cent; it is stored exactly
            as passed and an empty value is not accepted.

    Returns:
        A confirmation sentence carrying the booking reference, the date the first session is now due
        to run, how many times the booking has been moved once this move is counted, the reference
        number minted for the new school fee entry, the fee in USD to two decimal places, and the
        amount still to be collected on that booking in USD to two decimal places. The presence of
        that sentence is what indicates the move and the fee were written.
    """
    rows = ctx.find("lessons_holdings", lesson_id=lesson_id)
    holding = rows[0] if rows else {}
    fee = round(float(change_fee_usd), 2)
    rid = ctx.make_id("lsev_", lesson_id, new_session_date, change_fee_usd)
    ctx.create("lessons_ledger", rid, lesson_event_id=rid, lesson_id=lesson_id,
               customer_id=holding.get("customer_id"), event_type="lessons_fee_charge",
               season_code=holding.get("season_code"), event_date=ctx.now()[:10],
               amount_usd=fee, charge_category="reschedule_fee", payment_method="none",
               credit_reason="none")
    moves = int(float(holding.get("reschedule_count") or 0)) + 1
    outstanding = round(float(holding.get("tuition_balance_usd") or 0) + fee, 2)
    ctx.update("lessons_holdings", lesson_id, first_session_date=new_session_date,
               reschedule_count=moves, tuition_balance_usd=outstanding)
    return (f"Booking {lesson_id} now runs its first session on {new_session_date}; moves used: "
            f"{moves}. School fee entry {rid} written for {fee:.2f} USD; {outstanding:.2f} USD "
            "still to be collected on the booking.")

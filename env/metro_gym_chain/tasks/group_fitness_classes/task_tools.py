"""Hidden task tools for metro_gym_chain / group_fitness_classes.
Path: env/metro_gym_chain/tasks/group_fitness_classes/task_tools.py
Output of the erl-task-instantiate skill.
"""

from erlbench import ToolContext, tool


@tool(owner="agent", rw="write")
def log_class_no_show_ce445694(ctx: ToolContext, class_pass_id: str, class_session_id: str,
                                class_type: str, club_id: str, no_show_fee_usd: float) -> str:
    """Record that a member failed to attend a class they had booked against a class-credit pack,
    and charge the flat no-show fee for that missed class. The credit itself was already spent
    when the class was booked, so this action does not change the pack's credit balance; it only
    logs the miss and the fee against the pack's booking history. On success a new booking-history
    entry is created for this pack recording the no-show and the fee amount charged.

    Args:
        class_pass_id: Id class — the reference number of the class-credit pack the missed booking
            was made against; reachable by looking up the member's class-credit packs before the
            call.
        class_session_id: Id class — the reference number of the specific scheduled class session
            that was missed; reachable from the pack's booking history returned by looking up its
            booking history before the call.
        class_type: Enum class — the studio class type of the missed session; allowed values are
            exactly one of: yoga (the missed class was a yoga session), cycling (the missed class
            was a cycling session), hiit (the missed class was a hiit session), pilates (the
            missed class was a pilates session), strength (the missed class was a strength
            session), dance (the missed class was a dance session).
        club_id: Id class — the reference number of the club location the missed class was held
            at; reachable from the pack's booking history returned by looking up its booking
            history before the call, or from looking up club locations.
        no_show_fee_usd: Fixed-format class — the no-show fee to charge, in USD (a currency unit),
            rounded to exactly 2 decimal places, always zero or a positive amount.

    Returns:
        A string confirmation. On success it names the new booking-history entry's reference
        number, echoes the class_pass_id it was logged against, states credits_delta is 0 (no
        credit balance change), and states the amount_usd charged.
    """
    rid = ctx.make_id("cfe_", class_pass_id, class_session_id, "no_show")
    ctx.create("class_fitness_events", rid, event_id=rid, class_pass_id=class_pass_id,
               customer_id=(ctx.find("class_pass_holdings", class_pass_id=class_pass_id) or [{}])[0].get("customer_id", ""),
               event_type="class_no_show", event_timestamp=ctx.now(), credits_delta=0,
               amount_usd=round(float(no_show_fee_usd), 2), class_type=class_type, club_id=club_id,
               class_session_id=class_session_id)
    return (f"No-show logged as {rid} against pack {class_pass_id}: credits_delta=0, "
            f"amount_usd={round(float(no_show_fee_usd), 2):.2f} charged.")


@tool(owner="agent", rw="write")
def archive_class_pack_28917162(ctx: ToolContext, class_pass_id: str,
                                 reference_credit_value_usd: float) -> str:
    """Administratively archive an exhausted or expired class-credit pack, closing it out. This
    transitions the pack's lifecycle status to closed and records the date archived. No cash
    payment is made by this action; the reference value passed in is recorded only in the
    confirmation receipt for the member's records, not credited to any account.

    Args:
        class_pass_id: Id class — the reference number of the exhausted or expired class-credit
            pack being archived; reachable by looking up the member's class-credit packs before
            the call.
        reference_credit_value_usd: Fixed-format class — the reconciled per-credit dollar
            reference value being recorded for this archival, in USD (a currency unit), rounded to
            exactly 2 decimal places, always zero or a positive amount.

    Returns:
        A string confirmation. On success it names the pack now closed, the date it was closed
        (YYYY-MM-DD), and echoes the reference_credit_value_usd recorded for the member's records.
    """
    closed_date = ctx.now()[:10]
    ctx.update("class_pass_holdings", class_pass_id, status="closed", closed_date=closed_date)
    return (f"Pack {class_pass_id} archived to closed as of {closed_date}. Reference credit value "
            f"recorded for your records: ${round(float(reference_credit_value_usd), 2):.2f}.")


@tool(owner="user", rw="write")
def record_class_pack_refund_ca79a7d9(ctx: ToolContext, class_pass_id: str,
                                      refund_amount_usd: float, credits_removed: int) -> str:
    """Confirm and record the member's own refund of unused credits from a class-credit pack. This
    is the member's own decision, carried out only through the member's own confirmation. It logs
    the refund against the pack's booking history, removing the stated whole number of credits
    from the pack's reconciled balance, and pays out the stated dollar amount.

    Args:
        class_pass_id: Id class — the reference number of the class-credit pack being refunded;
            reachable by looking up the member's class-credit packs before the call.
        refund_amount_usd: Fixed-format class — the dollar amount being refunded to the member, in
            USD (a currency unit), rounded to exactly 2 decimal places, always zero or a positive
            amount.
        credits_removed: Fixed-format class — the whole number of class credits being removed from
            the pack's reconciled balance as part of this refund, a non-negative integer count
            where each unit represents one class credit.

    Returns:
        A string confirmation. On success it names the new booking-history entry's reference
        number, echoes the class_pass_id refunded, and states the credits_delta (the negative of
        credits_removed) and the amount_usd paid out.
    """
    rid = ctx.make_id("cfe_", class_pass_id, refund_amount_usd, credits_removed, "refund")
    customer_id = (ctx.find("class_pass_holdings", class_pass_id=class_pass_id) or [{}])[0].get("customer_id", "")
    delta = -abs(int(credits_removed))
    ctx.create("class_fitness_events", rid, event_id=rid, class_pass_id=class_pass_id,
               customer_id=customer_id, event_type="class_pack_refunded", event_timestamp=ctx.now(),
               credits_delta=delta, amount_usd=round(float(refund_amount_usd), 2), class_type="",
               club_id="", class_session_id="")
    return (f"Refund logged as {rid} for pack {class_pass_id}: credits_delta={delta}, "
            f"amount_usd={round(float(refund_amount_usd), 2):.2f} paid out.")


@tool(owner="agent", rw="write")
def log_class_no_show_ec16ff8d(ctx: ToolContext, class_pass_id: str, class_session_id: str,
                                class_type: str, club_id: str, no_show_fee_usd: float) -> str:
    """Record that a member failed to attend a class they had booked against a class-credit pack,
    and charge the flat no-show fee for that missed class. The credit itself was already spent
    when the class was booked, so this action does not change the pack's credit balance; it only
    logs the miss and the fee against the pack's booking history. On success a new booking-history
    entry is created for this pack recording the no-show and the fee amount charged.

    Args:
        class_pass_id: Id class — the reference number of the class-credit pack the missed booking
            was made against; reachable by looking up the member's class-credit packs before the
            call.
        class_session_id: Id class — the reference number of the specific scheduled class session
            that was missed; reachable from the pack's booking history returned by looking up its
            booking history before the call.
        class_type: Enum class — the studio class type of the missed session; allowed values are
            exactly one of: yoga (the missed class was a yoga session), cycling (the missed class
            was a cycling session), hiit (the missed class was a hiit session), pilates (the
            missed class was a pilates session), strength (the missed class was a strength
            session), dance (the missed class was a dance session).
        club_id: Id class — the reference number of the club location the missed class was held
            at; reachable from the pack's booking history returned by looking up its booking
            history before the call, or from looking up club locations.
        no_show_fee_usd: Fixed-format class — the no-show fee to charge, in USD (a currency unit),
            rounded to exactly 2 decimal places, always zero or a positive amount.

    Returns:
        A string confirmation. On success it names the new booking-history entry's reference
        number, echoes the class_pass_id it was logged against, states credits_delta is 0 (no
        credit balance change), and states the amount_usd charged.
    """
    rid = ctx.make_id("cfe_", class_pass_id, class_session_id, "no_show")
    ctx.create("class_fitness_events", rid, event_id=rid, class_pass_id=class_pass_id,
               customer_id=(ctx.find("class_pass_holdings", class_pass_id=class_pass_id) or [{}])[0].get("customer_id", ""),
               event_type="class_no_show", event_timestamp=ctx.now(), credits_delta=0,
               amount_usd=round(float(no_show_fee_usd), 2), class_type=class_type, club_id=club_id,
               class_session_id=class_session_id)
    return (f"No-show logged as {rid} against pack {class_pass_id}: credits_delta=0, "
            f"amount_usd={round(float(no_show_fee_usd), 2):.2f} charged.")


@tool(owner="agent", rw="write")
def archive_class_pack_bd5a6a26(ctx: ToolContext, class_pass_id: str,
                                 reference_credit_value_usd: float) -> str:
    """Administratively archive an exhausted or expired class-credit pack, closing it out. This
    transitions the pack's lifecycle status to closed and records the date archived. No cash
    payment is made by this action; the reference value passed in is recorded only in the
    confirmation receipt for the member's records, not credited to any account.

    Args:
        class_pass_id: Id class — the reference number of the exhausted or expired class-credit
            pack being archived; reachable by looking up the member's class-credit packs before
            the call.
        reference_credit_value_usd: Fixed-format class — the reconciled per-credit dollar
            reference value being recorded for this archival, in USD (a currency unit), rounded to
            exactly 2 decimal places, always zero or a positive amount.

    Returns:
        A string confirmation. On success it names the pack now closed, the date it was closed
        (YYYY-MM-DD), and echoes the reference_credit_value_usd recorded for the member's records.
    """
    closed_date = ctx.now()[:10]
    ctx.update("class_pass_holdings", class_pass_id, status="closed", closed_date=closed_date)
    return (f"Pack {class_pass_id} archived to closed as of {closed_date}. Reference credit value "
            f"recorded for your records: ${round(float(reference_credit_value_usd), 2):.2f}.")


@tool(owner="agent", rw="write")
def cancel_class_booking_in_window_11da7e9b(ctx: ToolContext, class_pass_id: str,
                                             class_session_id: str, class_type: str, club_id: str,
                                             credits_delta: int) -> str:
    """Record that a member cancelled a previously booked class with enough advance notice, and
    refund the credit that booking spent back to the pack's balance at no charge. On success a new
    booking-history entry is created for this pack recording the in-window cancellation and the
    number of credits refunded.

    Args:
        class_pass_id: Id class — the reference number of the class-credit pack the cancelled
            booking was made against; reachable by looking up the member's class-credit packs
            before the call.
        class_session_id: Id class — the reference number of the specific scheduled class session
            being cancelled; reachable from the pack's booking history returned by looking up its
            booking history before the call.
        class_type: Enum class — the studio class type of the cancelled session; allowed values
            are exactly one of: yoga (the cancelled class was a yoga session), cycling (the
            cancelled class was a cycling session), hiit (the cancelled class was a hiit session),
            pilates (the cancelled class was a pilates session), strength (the cancelled class was
            a strength session), dance (the cancelled class was a dance session).
        club_id: Id class — the reference number of the club location the cancelled class was held
            at; reachable from the pack's booking history returned by looking up its booking
            history before the call, or from looking up club locations.
        credits_delta: Fixed-format class — signed integer count of class credits being refunded
            back to the pack's balance by this cancellation (each unit representing one class
            credit), always a positive whole number matching the credits originally spent on the
            booking now being cancelled.

    Returns:
        A string confirmation. On success it names the new booking-history entry's reference
        number, echoes the class_pass_id refunded to, and states the credits_delta credited and
        that amount_usd charged is 0 (an in-window cancellation is free).
    """
    rid = ctx.make_id("cfe_", class_pass_id, class_session_id, "cancel_in_window")
    ctx.create("class_fitness_events", rid, event_id=rid, class_pass_id=class_pass_id,
               customer_id=(ctx.find("class_pass_holdings", class_pass_id=class_pass_id) or [{}])[0].get("customer_id", ""),
               event_type="class_booking_cancelled_in_window", event_timestamp=ctx.now(),
               credits_delta=abs(int(credits_delta)), amount_usd=0.0, class_type=class_type,
               club_id=club_id, class_session_id=class_session_id)
    return (f"In-window cancellation logged as {rid} against pack {class_pass_id}: "
            f"credits_delta={abs(int(credits_delta))}, amount_usd=0.00.")


@tool(owner="user", rw="write")
def confirm_class_pack_cancellation_d19c86a2(ctx: ToolContext, class_pass_id: str) -> str:
    """Confirm the member's own decision to cancel a class-credit pack. This is the member's own
    decision, carried out only through the member's own confirmation. It transitions the pack's
    lifecycle status to closed and records the date cancelled; it pays out no refund of its own —
    any unused-credit refund is recorded separately.

    Args:
        class_pass_id: Id class — the reference number of the class-credit pack being cancelled;
            reachable by looking up the member's class-credit packs before the call.

    Returns:
        A string confirmation. On success it names the pack now closed and the date it was closed
        (YYYY-MM-DD).
    """
    closed_date = ctx.now()[:10]
    ctx.update("class_pass_holdings", class_pass_id, status="closed", closed_date=closed_date)
    return f"Pack {class_pass_id} cancelled and closed as of {closed_date}."


@tool(owner="agent", rw="write")
def record_class_pack_refund_5f8777de(ctx: ToolContext, class_pass_id: str,
                                       refund_amount_usd: float, credits_removed: int) -> str:
    """Record the settlement of a member's refund of unused credits from a class-credit pack that
    has already been confirmed cancelled. It logs the refund against the pack's booking history,
    removing the stated whole number of credits from the pack's reconciled balance, and pays out
    the stated dollar amount.

    Args:
        class_pass_id: Id class — the reference number of the class-credit pack being refunded;
            reachable by looking up the member's class-credit packs before the call.
        refund_amount_usd: Fixed-format class — the dollar amount being refunded to the member, in
            USD (a currency unit), rounded to exactly 2 decimal places, always zero or a positive
            amount.
        credits_removed: Fixed-format class — the whole number of class credits being removed from
            the pack's reconciled balance as part of this refund, a non-negative integer count
            where each unit represents one class credit.

    Returns:
        A string confirmation. On success it names the new booking-history entry's reference
        number, echoes the class_pass_id refunded, and states the credits_delta (the negative of
        credits_removed) and the amount_usd paid out.
    """
    rid = ctx.make_id("cfe_", class_pass_id, refund_amount_usd, credits_removed, "refund2")
    customer_id = (ctx.find("class_pass_holdings", class_pass_id=class_pass_id) or [{}])[0].get("customer_id", "")
    delta = -abs(int(credits_removed))
    ctx.create("class_fitness_events", rid, event_id=rid, class_pass_id=class_pass_id,
               customer_id=customer_id, event_type="class_pack_refunded", event_timestamp=ctx.now(),
               credits_delta=delta, amount_usd=round(float(refund_amount_usd), 2), class_type="",
               club_id="", class_session_id="")
    return (f"Refund logged as {rid} for pack {class_pass_id}: credits_delta={delta}, "
            f"amount_usd={round(float(refund_amount_usd), 2):.2f} paid out.")

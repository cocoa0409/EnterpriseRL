"""Hidden task tools for metro_gym_chain / personal_training_packages.
Path: env/metro_gym_chain/tasks/personal_training_packages/task_tools.py

Each tool below is named <verb>_<object>_<uuid8> and is HIDDEN: it is never listed directly to
the agent, and is reached only through this difficulty's extended_policy target_tool / workflow
step, via unlock_agent_discoverable_tool / call_agent_discoverable_tool (or the user-owned pair).
Every tool performs exactly one atomic state change; none of them aggregate history, look up a
tier parameter, or judge a policy precondition on the agent's behalf -- the agent computes the
write parameter from policy + world state and passes it in as a fixed-format argument.
"""

from erlbench import ToolContext, tool


@tool(owner="agent", rw="write")
def redeem_pt_session_d7771acf(ctx: ToolContext, pt_holding_id: str, session_type: str,
                                trainer_name: str) -> str:
    """Log that the member attended a booked coaching session and redeem it against a personal-
    training package's session balance. This creates one ledger row on the package showing one
    session consumed, and reduces the package's sessions_remaining by 1. On success the member's
    remaining session count for that package is reduced by exactly one session.

    Args:
        pt_holding_id: Id class — the reference number of the personal-training package the
            session is redeemed against, reachable by looking up the member's packages before
            this call.
        session_type: Enum class — exactly one of: standard (an ordinary coaching session),
            specialty_nutrition (a nutrition-focused coaching session), specialty_rehab (a
            rehabilitation-focused coaching session). Use the kind of session the member actually
            attended.
        trainer_name: Verbatim class — the name of the trainer who led this session, copied
            character for character from what the caller or the package's own trainer-of-record
            states (verbatim).

    Returns:
        A confirmation string naming the new ledger entry's reference number and the package's
        session balance after the redemption. The presence of a new reference number indicates
        the redemption was recorded successfully.
    """
    rid = ctx.make_id("ptev_redeem_", pt_holding_id, session_type, trainer_name)
    rows = ctx.find("pt_holdings", pt_holding_id=pt_holding_id)
    if not rows:
        return f"Error: no personal-training package {pt_holding_id}."
    holding = rows[0]
    new_remaining = float(holding.get("sessions_remaining") or 0) - 1
    ctx.create("pt_events", rid, event_id=rid, pt_holding_id=pt_holding_id,
               customer_id=holding.get("customer_id"), event_type="pt_session_redeemed",
               event_timestamp=ctx.now(), sessions_delta=-1, amount_usd=0.00,
               session_type=session_type, trainer_name=trainer_name)
    ctx.update("pt_holdings", pt_holding_id, sessions_remaining=new_remaining)
    return f"Session redemption {rid} recorded; sessions_remaining is now {new_remaining}."


@tool(owner="agent", rw="write")
def log_late_cancellation_b8e4e034(ctx: ToolContext, pt_holding_id: str, session_type: str,
                                    trainer_name: str, cancellation_amount_usd: float) -> str:
    """Log that the member cancelled a scheduled coaching session within the package's late-
    cancellation window, forfeiting one session from the package's balance and charging the
    late-cancellation fee. This creates one ledger row on the package recording the forfeited
    session and the dollar amount charged, and reduces the package's sessions_remaining by 1. On
    success the member's remaining session count for that package is reduced by exactly one
    session and the stated fee is on record against the package.

    Args:
        pt_holding_id: Id class — the reference number of the personal-training package the
            late cancellation is logged against, reachable by looking up the member's packages
            before this call.
        session_type: Enum class — exactly one of: standard (an ordinary coaching session),
            specialty_nutrition (a nutrition-focused coaching session), specialty_rehab (a
            rehabilitation-focused coaching session). Use the kind of session that was cancelled.
        trainer_name: Verbatim class — the name of the trainer who was originally assigned to
            this session, copied character for character from what the caller or the package's
            own trainer-of-record states (verbatim).
        cancellation_amount_usd: Fixed-format class — the total amount to charge for this late
            cancellation, expressed in the currency unit US dollars and rounded to exactly 2
            decimal places (for example 15.0 or 40.0); pass the full amount to charge, already
            combining every applicable fee component.

    Returns:
        A confirmation string naming the new ledger entry's reference number, the amount charged,
        and the package's session balance after the forfeiture. The presence of a new reference
        number indicates the late cancellation was recorded successfully.
    """
    amt = round(float(cancellation_amount_usd), 2)
    rid = ctx.make_id("ptev_latecancel_", pt_holding_id, session_type, trainer_name, amt)
    rows = ctx.find("pt_holdings", pt_holding_id=pt_holding_id)
    if not rows:
        return f"Error: no personal-training package {pt_holding_id}."
    holding = rows[0]
    new_remaining = float(holding.get("sessions_remaining") or 0) - 1
    ctx.create("pt_events", rid, event_id=rid, pt_holding_id=pt_holding_id,
               customer_id=holding.get("customer_id"), event_type="pt_session_cancelled_late",
               event_timestamp=ctx.now(), sessions_delta=-1, amount_usd=amt,
               session_type=session_type, trainer_name=trainer_name)
    ctx.update("pt_holdings", pt_holding_id, sessions_remaining=new_remaining)
    return (f"Late cancellation {rid} recorded; charged ${amt:.2f}; "
            f"sessions_remaining is now {new_remaining}.")


@tool(owner="user", rw="write")
def confirm_package_cancellation_cc17b6f3(ctx: ToolContext, pt_holding_id: str) -> str:
    """Let the member confirm, in their own words and on their own authority, that they want to
    cancel their personal-training package and take a refund of its unused sessions. This
    transitions the package's own status to closed and sets its closed date to today. On success
    the package's status shows closed and its closed date is recorded.

    Args:
        pt_holding_id: Id class — the reference number of the personal-training package the
            member is cancelling, reachable by looking up the member's packages before this call.

    Returns:
        A confirmation string naming the package's reference number and its new status and closed
        date. The status reading "closed" indicates the cancellation was recorded successfully.
    """
    rows = ctx.find("pt_holdings", pt_holding_id=pt_holding_id)
    if not rows:
        return f"Error: no personal-training package {pt_holding_id}."
    closed_date = ctx.now()[:10]
    ctx.update("pt_holdings", pt_holding_id, status="closed", closed_date=closed_date)
    return f"Package {pt_holding_id} cancelled; status is now closed as of {closed_date}."


@tool(owner="agent", rw="write")
def record_package_refund_4aaf76ef(ctx: ToolContext, pt_holding_id: str,
                                    refund_amount_usd: float) -> str:
    """Record the refund of a cancelled personal-training package's unused-session value. This
    creates one ledger row on the package showing the dollar amount refunded, with the package's
    sessions_remaining zeroed out to reflect that no further sessions remain to redeem. On success
    the refunded dollar amount is on record against the package and its session balance reads 0.

    Args:
        pt_holding_id: Id class — the reference number of the personal-training package being
            refunded, reachable by looking up the member's packages before this call.
        refund_amount_usd: Fixed-format class — the total amount to refund, expressed in the
            currency unit US dollars and rounded to exactly 2 decimal places (for example 120.0 or
            45.5); pass the full computed refund amount.

    Returns:
        A confirmation string naming the new ledger entry's reference number and the amount
        refunded. The presence of a new reference number indicates the refund was recorded
        successfully.
    """
    amt = round(float(refund_amount_usd), 2)
    rid = ctx.make_id("ptev_refund_", pt_holding_id, amt)
    rows = ctx.find("pt_holdings", pt_holding_id=pt_holding_id)
    if not rows:
        return f"Error: no personal-training package {pt_holding_id}."
    holding = rows[0]
    ctx.create("pt_events", rid, event_id=rid, pt_holding_id=pt_holding_id,
               customer_id=holding.get("customer_id"), event_type="pt_package_refunded",
               event_timestamp=ctx.now(), sessions_delta=-float(holding.get("sessions_remaining") or 0),
               amount_usd=amt, session_type="", trainer_name="")
    ctx.update("pt_holdings", pt_holding_id, sessions_remaining=0)
    return f"Refund {rid} recorded for ${amt:.2f}; sessions_remaining is now 0."


@tool(owner="agent", rw="write")
def grant_bonus_session_f02d8384(ctx: ToolContext, pt_holding_id: str, sessions_delta: int) -> str:
    """Credit a complimentary goodwill bonus session to a member's personal-training package.
    This creates one ledger row on the package recording the number of sessions credited, and
    increases the package's sessions_remaining by that same count. On success the member's
    remaining session count for that package is increased by the stated number of sessions.

    Args:
        pt_holding_id: Id class — the reference number of the personal-training package being
            credited, reachable by looking up the member's packages before this call.
        sessions_delta: Fixed-format class — the whole number of bonus sessions to credit to the
            package, a non-negative integer whose unit is sessions (for example 0 or 1); pass the
            full number of sessions owed.

    Returns:
        A confirmation string naming the new ledger entry's reference number, the number of
        sessions credited, and the package's session balance afterward. The presence of a new
        reference number indicates the grant was recorded successfully.
    """
    delta = int(sessions_delta)
    rid = ctx.make_id("ptev_bonus_", pt_holding_id, delta)
    rows = ctx.find("pt_holdings", pt_holding_id=pt_holding_id)
    if not rows:
        return f"Error: no personal-training package {pt_holding_id}."
    holding = rows[0]
    new_remaining = float(holding.get("sessions_remaining") or 0) + delta
    ctx.create("pt_events", rid, event_id=rid, pt_holding_id=pt_holding_id,
               customer_id=holding.get("customer_id"), event_type="pt_bonus_session_granted",
               event_timestamp=ctx.now(), sessions_delta=delta, amount_usd=0.00,
               session_type="", trainer_name="")
    ctx.update("pt_holdings", pt_holding_id, sessions_remaining=new_remaining)
    return f"Bonus grant {rid} recorded for {delta} session(s); sessions_remaining is now {new_remaining}."


@tool(owner="agent", rw="write")
def reassign_trainer_0e491cd1(ctx: ToolContext, pt_holding_id: str, new_trainer_name: str,
                               reassignment_fee_usd: float) -> str:
    """Change the trainer assigned to a member's personal-training package. This creates one
    ledger row on the package recording the newly assigned trainer and any reassignment fee
    charged, and updates the package's own trainer-of-record to that same trainer. On success the
    package's trainer-of-record reads the new trainer's name and the stated fee, if any, is on
    record against the package.

    Args:
        pt_holding_id: Id class — the reference number of the personal-training package being
            reassigned, reachable by looking up the member's packages before this call.
        new_trainer_name: Verbatim class — the name of the trainer being newly assigned, copied
            character for character from what the caller states or from the trainer name the
            reassignment is being reconciled to (verbatim).
        reassignment_fee_usd: Fixed-format class — the amount to charge for this reassignment,
            expressed in the currency unit US dollars and rounded to exactly 2 decimal places (for
            example 0.0 or 30.0); pass 0.0 when the reassignment is free.

    Returns:
        A confirmation string naming the new ledger entry's reference number, the newly assigned
        trainer, and the fee charged. The presence of a new reference number indicates the
        reassignment was recorded successfully.
    """
    fee = round(float(reassignment_fee_usd), 2)
    rid = ctx.make_id("ptev_reassign_", pt_holding_id, new_trainer_name, fee)
    rows = ctx.find("pt_holdings", pt_holding_id=pt_holding_id)
    if not rows:
        return f"Error: no personal-training package {pt_holding_id}."
    holding = rows[0]
    ctx.create("pt_events", rid, event_id=rid, pt_holding_id=pt_holding_id,
               customer_id=holding.get("customer_id"), event_type="pt_trainer_reassigned",
               event_timestamp=ctx.now(), sessions_delta=0, amount_usd=fee,
               session_type="", trainer_name=new_trainer_name)
    ctx.update("pt_holdings", pt_holding_id, assigned_trainer_name=new_trainer_name)
    return f"Reassignment {rid} recorded to {new_trainer_name}; fee charged ${fee:.2f}."


@tool(owner="agent", rw="write")
def lapse_expire_package_bc252d9e(ctx: ToolContext, pt_holding_id: str,
                                   forfeited_sessions: int) -> str:
    """Administratively lapse a personal-training package whose expiration window has passed,
    and forfeit its unused sessions. This transitions the package's own status to expired and
    creates one ledger row recording the number of sessions forfeited, with the package's
    sessions_remaining reduced by that same count (down to zero). On success the package's status
    reads expired and its session balance reflects the forfeiture.

    Args:
        pt_holding_id: Id class — the reference number of the personal-training package being
            lapsed, reachable by looking up the member's packages before this call.
        forfeited_sessions: Fixed-format class — the whole number of sessions to forfeit from the
            package, a non-negative integer whose unit is sessions (for example 0 or 4); pass the
            package's own remaining session count at the moment of lapsing.

    Returns:
        A confirmation string naming the new ledger entry's reference number, the number of
        sessions forfeited, and the package's new status. The status reading "expired" indicates
        the lapse was recorded successfully.
    """
    delta = int(forfeited_sessions)
    rid = ctx.make_id("ptev_expire_", pt_holding_id, delta)
    rows = ctx.find("pt_holdings", pt_holding_id=pt_holding_id)
    if not rows:
        return f"Error: no personal-training package {pt_holding_id}."
    holding = rows[0]
    new_remaining = float(holding.get("sessions_remaining") or 0) - delta
    ctx.update("pt_holdings", pt_holding_id, status="expired", sessions_remaining=new_remaining)
    ctx.create("pt_events", rid, event_id=rid, pt_holding_id=pt_holding_id,
               customer_id=holding.get("customer_id"), event_type="pt_package_expired",
               event_timestamp=ctx.now(), sessions_delta=-delta, amount_usd=0.00,
               session_type="", trainer_name="")
    return f"Lapse {rid} recorded; {delta} session(s) forfeited; status is now expired."


@tool(owner="agent", rw="write")
def archive_pt_package_1350ea96(ctx: ToolContext, pt_holding_id: str, closed_date: str) -> str:
    """Administratively archive an exhausted or expired personal-training package. This
    transitions the package's own status to closed and sets its closed date to the stated date.
    On success the package's status reads closed and its closed date is recorded.

    Args:
        pt_holding_id: Id class — the reference number of the personal-training package being
            archived, reachable by looking up the member's packages before this call.
        closed_date: Fixed-format class — the date to record as the package's closed date,
            YYYY-MM-DD, matching the date format already on file for this package's other dates;
            pass the correct closing date for this archival.

    Returns:
        A confirmation string naming the package's reference number, its new status, and its
        closed date. The status reading "closed" indicates the archival was recorded successfully.
    """
    rows = ctx.find("pt_holdings", pt_holding_id=pt_holding_id)
    if not rows:
        return f"Error: no personal-training package {pt_holding_id}."
    ctx.update("pt_holdings", pt_holding_id, status="closed", closed_date=closed_date)
    return f"Package {pt_holding_id} archived; status is now closed as of {closed_date}."


@tool(owner="agent", rw="write")
def activate_pt_package_46fb321d(ctx: ToolContext, pt_holding_id: str, sessions_granted: int,
                                  expiration_date: str) -> str:
    """Activate a previously applied personal-training package, crediting it with the stated
    number of sessions and setting its expiration date. This transitions the package's own status
    to active and sets its session balance and expiration date to the stated values. On success
    the package's status reads active with the stated session balance and expiration date.

    Args:
        pt_holding_id: Id class — the reference number of the applied package being activated,
            reachable from the confirmation returned when the package was applied for.
        sessions_granted: Fixed-format class — the whole number of sessions to credit to the
            package at activation, a non-negative integer whose unit is sessions, or -1 to denote
            unlimited use (for example 5, 20 or -1); pass the full computed number of sessions
            owed.
        expiration_date: Fixed-format class — the date unused sessions in this package will
            expire, YYYY-MM-DD; pass the correct computed expiration date for this package.

    Returns:
        A confirmation string naming the package's reference number, its new status, its session
        balance, and its expiration date. The status reading "active" indicates the activation was
        recorded successfully.
    """
    granted = int(sessions_granted)
    rows = ctx.find("pt_holdings", pt_holding_id=pt_holding_id)
    if not rows:
        return f"Error: no personal-training package {pt_holding_id}."
    ctx.update("pt_holdings", pt_holding_id, status="active", sessions_remaining=granted,
               expiration_date=expiration_date)
    return (f"Package {pt_holding_id} activated; sessions_remaining={granted}; "
            f"expiration_date={expiration_date}.")

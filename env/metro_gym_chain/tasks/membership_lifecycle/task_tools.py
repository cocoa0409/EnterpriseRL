"""Hidden task tools for env/metro_gym_chain/tasks/membership_lifecycle.

Each tool performs exactly one atomic write against membership_holdings /
membership_events / membership_cancellation_requests. No tool aggregates
history, reads another category, or judges a policy precondition -- every
multi-factor calculation is done by the agent from the published policy and
the world, and passed in here as a single fixed-format argument.
"""

from erlbench import ToolContext, tool


@tool(owner="agent", rw="write")
def charge_enrollment_fee_91320c6d(ctx: ToolContext, membership_id: str, customer_id: str,
                                    amount_usd: float) -> str:
    """Post the one-time enrollment fee charge to a club membership contract's billing
    history. This records a new membership_dues_charge history entry of billing subtype
    enrollment_fee against the named membership contract and its owning member, in the
    exact dollar amount given, and adds that amount to the contract's running dues
    balance. Use this once for a given membership contract's enrollment fee; calling it
    again with a different amount posts a second, separate enrollment_fee entry rather
    than correcting the first.

    Args:
        membership_id: Id class — the reference number of the membership contract to
            bill, reachable by looking up the member's membership holdings before the
            call.
        customer_id: Id class — the reference number of the member who owns the
            membership contract being billed, reachable by looking up the member's
            profile or membership holdings before the call.
        amount_usd: Fixed-format class — the dollar amount to charge for this
            enrollment fee, in US dollars (the schema's currency unit), rounded to exactly 2 decimal places (e.g.
            49.00). No time zone or empty-value convention applies; this argument is
            always required and always a non-negative number.

    Returns:
        A string confirmation naming the new history entry's own reference number and
        restating the membership contract billed, the billing subtype (enrollment_fee),
        and the dollar amount posted. A membership contract that does not exist is
        reported back in the same string rather than raising, since this atomic action
        does not itself verify the contract's status or history.
    """
    amt = round(float(amount_usd), 2)
    eid = ctx.make_id("mbev_enrfee_", membership_id, amt, ctx.now())
    rows = ctx.find("membership_holdings", membership_id=membership_id)
    if not rows:
        return f"No membership contract {membership_id} on file; nothing charged."
    ctx.create("membership_events", eid, event_id=eid, membership_id=membership_id,
               customer_id=customer_id, event_type="membership_dues_charge",
               event_timestamp=ctx.now(), amount_usd=amt, charge_type="enrollment_fee",
               billing_cycle_month="", channel="phone", club_id="", guest_name="")
    new_balance = round(float(rows[0].get("dues_balance") or 0) + amt, 2)
    ctx.update("membership_holdings", membership_id, dues_balance=new_balance)
    return (f"Posted enrollment_fee charge {eid} of ${amt:.2f} to membership "
            f"{membership_id}; dues balance is now ${new_balance:.2f}.")


@tool(owner="agent", rw="write")
def charge_recurring_dues_93751e4d(ctx: ToolContext, membership_id: str, customer_id: str,
                                    amount_usd: float) -> str:
    """Post this billing cycle's recurring monthly dues charge to a club membership
    contract's billing history. This records a new membership_dues_charge history entry
    of billing subtype recurring_dues against the named membership contract and its
    owning member, in the exact dollar amount given, and adds that amount to the
    contract's running dues balance. Use this once per billing cycle for a given
    membership contract; calling it again for the same cycle posts a second, separate
    recurring_dues entry rather than correcting the first.

    Args:
        membership_id: Id class — the reference number of the membership contract to
            bill, reachable by looking up the member's membership holdings before the
            call.
        customer_id: Id class — the reference number of the member who owns the
            membership contract being billed, reachable by looking up the member's
            profile or membership holdings before the call.
        amount_usd: Fixed-format class — the dollar amount to charge for this billing
            cycle's recurring dues, in US dollars (the schema's currency unit), rounded to exactly 2 decimal places
            (e.g. 40.49). No time zone or empty-value convention applies; this argument
            is always required and always a non-negative number.

    Returns:
        A string confirmation naming the new history entry's own reference number and
        restating the membership contract billed, the billing subtype (recurring_dues),
        and the dollar amount posted. A membership contract that does not exist is
        reported back in the same string rather than raising, since this atomic action
        does not itself verify the contract's status or history.
    """
    amt = round(float(amount_usd), 2)
    eid = ctx.make_id("mbev_recdues_", membership_id, amt, ctx.now())
    rows = ctx.find("membership_holdings", membership_id=membership_id)
    if not rows:
        return f"No membership contract {membership_id} on file; nothing charged."
    ctx.create("membership_events", eid, event_id=eid, membership_id=membership_id,
               customer_id=customer_id, event_type="membership_dues_charge",
               event_timestamp=ctx.now(), amount_usd=amt, charge_type="recurring_dues",
               billing_cycle_month=ctx.now()[:7], channel="phone", club_id="", guest_name="")
    new_balance = round(float(rows[0].get("dues_balance") or 0) + amt, 2)
    ctx.update("membership_holdings", membership_id, dues_balance=new_balance)
    return (f"Posted recurring_dues charge {eid} of ${amt:.2f} to membership "
            f"{membership_id}; dues balance is now ${new_balance:.2f}.")


@tool(owner="agent", rw="write")
def waive_dues_medical_hold_6b86f7b6(ctx: ToolContext, membership_id: str, amount_usd: float) -> str:
    """Post a dues waiver against a club membership contract's running dues balance for
    a documented medical-hold freeze. This records a new membership_dues_waived history
    entry against the named membership contract, in the exact dollar amount given, and
    subtracts that amount from the contract's running dues balance. Use this once per
    medical-hold waiver decision; calling it again posts a second, separate waiver entry
    rather than correcting the first.

    Args:
        membership_id: Id class — the reference number of the membership contract
            whose balance is being waived, reachable by looking up the member's
            membership holdings before the call.
        amount_usd: Fixed-format class — the dollar amount to waive, in US dollars
            (the schema's currency unit), rounded to exactly 2 decimal places (e.g.
            36.44). No time zone or
            empty-value convention applies; this argument is always required and always
            a non-negative number.

    Returns:
        A string confirmation naming the new history entry's own reference number and
        restating the membership contract, the dollar amount waived, and the
        contract's dues balance after the waiver. A membership contract that does not
        exist is reported back in the same string rather than raising, since this
        atomic action does not itself verify the contract's status or history.
    """
    amt = round(float(amount_usd), 2)
    eid = ctx.make_id("mbev_waiver_", membership_id, amt, ctx.now())
    rows = ctx.find("membership_holdings", membership_id=membership_id)
    if not rows:
        return f"No membership contract {membership_id} on file; nothing waived."
    cust = rows[0].get("customer_id")
    ctx.create("membership_events", eid, event_id=eid, membership_id=membership_id,
               customer_id=cust, event_type="membership_dues_waived",
               event_timestamp=ctx.now(), amount_usd=amt, charge_type="",
               billing_cycle_month="", channel="", club_id="", guest_name="")
    new_balance = round(float(rows[0].get("dues_balance") or 0) - amt, 2)
    ctx.update("membership_holdings", membership_id, dues_balance=new_balance)
    return (f"Posted dues waiver {eid} of ${amt:.2f} on membership {membership_id}; "
            f"dues balance is now ${new_balance:.2f}.")


@tool(owner="agent", rw="write")
def charge_late_fee_8963437d(ctx: ToolContext, membership_id: str, customer_id: str,
                              amount_usd: float) -> str:
    """Post a late-fee charge to a club membership contract's billing history for a
    dues charge that failed to collect. This records a new membership_dues_charge
    history entry of billing subtype late_fee against the named membership contract and
    its owning member, in the exact dollar amount given, and adds that amount to the
    contract's running dues balance. Use this once per missed-payment event; calling it
    again posts a second, separate late_fee entry rather than correcting the first.

    Args:
        membership_id: Id class — the reference number of the membership contract to
            bill, reachable by looking up the member's membership holdings before the
            call.
        customer_id: Id class — the reference number of the member who owns the
            membership contract being billed, reachable by looking up the member's
            profile or membership holdings before the call.
        amount_usd: Fixed-format class — the dollar amount to charge for this late
            fee, in US dollars (the schema's currency unit), rounded to exactly 2 decimal places (e.g. 16.88). No
            time zone or empty-value convention applies; this argument is always
            required and always a non-negative number.

    Returns:
        A string confirmation naming the new history entry's own reference number and
        restating the membership contract billed, the billing subtype (late_fee), and
        the dollar amount posted. A membership contract that does not exist is
        reported back in the same string rather than raising, since this atomic action
        does not itself verify the contract's status or history.
    """
    amt = round(float(amount_usd), 2)
    eid = ctx.make_id("mbev_latefee_", membership_id, amt, ctx.now())
    rows = ctx.find("membership_holdings", membership_id=membership_id)
    if not rows:
        return f"No membership contract {membership_id} on file; nothing charged."
    ctx.create("membership_events", eid, event_id=eid, membership_id=membership_id,
               customer_id=customer_id, event_type="membership_dues_charge",
               event_timestamp=ctx.now(), amount_usd=amt, charge_type="late_fee",
               billing_cycle_month="", channel="phone", club_id="", guest_name="")
    new_balance = round(float(rows[0].get("dues_balance") or 0) + amt, 2)
    ctx.update("membership_holdings", membership_id, dues_balance=new_balance)
    return (f"Posted late_fee charge {eid} of ${amt:.2f} to membership {membership_id}; "
            f"dues balance is now ${new_balance:.2f}.")


@tool(owner="agent", rw="write")
def pay_reactivation_balance_4f725d24(ctx: ToolContext, membership_id: str, amount_usd: float) -> str:
    """Apply a payment toward reactivating a past_due club membership contract. This
    records a new membership_payment_received history entry against the named
    membership contract, in the exact dollar amount given, and subtracts that amount
    from the contract's running dues balance. Use this once for the reactivation
    payment; calling it again posts a second, separate payment entry rather than
    correcting the first.

    Args:
        membership_id: Id class — the reference number of the membership contract
            being paid down, reachable by looking up the member's membership holdings
            before the call.
        amount_usd: Fixed-format class — the dollar amount paid, in US dollars (the
            schema's currency unit), rounded to exactly 2 decimal places (e.g.
            149.05). No time zone or empty-value
            convention applies; this argument is always required and always a
            non-negative number.

    Returns:
        A string confirmation naming the new history entry's own reference number and
        restating the membership contract, the dollar amount paid, and the contract's
        dues balance after the payment. A membership contract that does not exist is
        reported back in the same string rather than raising, since this atomic action
        does not itself verify the contract's status or history.
    """
    amt = round(float(amount_usd), 2)
    eid = ctx.make_id("mbev_reactpay_", membership_id, amt, ctx.now())
    rows = ctx.find("membership_holdings", membership_id=membership_id)
    if not rows:
        return f"No membership contract {membership_id} on file; nothing paid."
    cust = rows[0].get("customer_id")
    ctx.create("membership_events", eid, event_id=eid, membership_id=membership_id,
               customer_id=cust, event_type="membership_payment_received",
               event_timestamp=ctx.now(), amount_usd=amt, charge_type="",
               billing_cycle_month="", channel="phone", club_id="", guest_name="")
    new_balance = round(float(rows[0].get("dues_balance") or 0) - amt, 2)
    ctx.update("membership_holdings", membership_id, dues_balance=new_balance)
    return (f"Posted payment {eid} of ${amt:.2f} on membership {membership_id}; dues "
            f"balance is now ${new_balance:.2f}.")


@tool(owner="agent", rw="write")
def reactivate_membership_73e153df(ctx: ToolContext, membership_id: str) -> str:
    """Bring a past_due club membership contract back to active standing. This changes
    the named membership contract's lifecycle status from past_due to active and clears
    its past-due-since date. It does not itself post any charge or payment; use the
    dedicated billing tools first if a balance still needs to be settled.

    Args:
        membership_id: Id class — the reference number of the membership contract to
            reactivate, reachable by looking up the member's membership holdings before
            the call.

    Returns:
        A string confirmation naming the membership contract and stating its lifecycle
        status is now active. A membership contract that does not exist is reported
        back in the same string rather than raising.
    """
    rows = ctx.find("membership_holdings", membership_id=membership_id)
    if not rows:
        return f"No membership contract {membership_id} on file; nothing reactivated."
    ctx.update("membership_holdings", membership_id, status="active", past_due_since_date="")
    return f"Membership {membership_id} is now active again (reactivated from past_due)."


@tool(owner="agent", rw="write")
def charge_early_termination_fee_74e8dbe7(ctx: ToolContext, membership_id: str, customer_id: str,
                                           amount_usd: float) -> str:
    """Post the early-termination fee charge to a club membership contract's billing
    history. This records a new membership_dues_charge history entry of billing
    subtype early_termination_fee against the named membership contract and its owning
    member, in the exact dollar amount given, and adds that amount to the contract's
    running dues balance. Use this once per cancellation notice; calling it again
    posts a second, separate early_termination_fee entry rather than correcting the
    first.

    Args:
        membership_id: Id class — the reference number of the membership contract to
            bill, reachable by looking up the member's membership holdings before the
            call.
        customer_id: Id class — the reference number of the member who owns the
            membership contract being billed, reachable by looking up the member's
            profile or membership holdings before the call.
        amount_usd: Fixed-format class — the dollar amount to charge for the early
            termination fee, in US dollars (the schema's currency unit), rounded to exactly 2 decimal places (e.g.
            110.20). No time zone or empty-value convention applies; this argument is
            always required and always a non-negative number.

    Returns:
        A string confirmation naming the new history entry's own reference number and
        restating the membership contract billed, the billing subtype
        (early_termination_fee), and the dollar amount posted. A membership contract
        that does not exist is reported back in the same string rather than raising,
        since this atomic action does not itself verify the contract's status or
        history.
    """
    amt = round(float(amount_usd), 2)
    eid = ctx.make_id("mbev_etf_", membership_id, amt, ctx.now())
    rows = ctx.find("membership_holdings", membership_id=membership_id)
    if not rows:
        return f"No membership contract {membership_id} on file; nothing charged."
    ctx.create("membership_events", eid, event_id=eid, membership_id=membership_id,
               customer_id=customer_id, event_type="membership_dues_charge",
               event_timestamp=ctx.now(), amount_usd=amt, charge_type="early_termination_fee",
               billing_cycle_month="", channel="phone", club_id="", guest_name="")
    new_balance = round(float(rows[0].get("dues_balance") or 0) + amt, 2)
    ctx.update("membership_holdings", membership_id, dues_balance=new_balance)
    return (f"Posted early_termination_fee charge {eid} of ${amt:.2f} to membership "
            f"{membership_id}; dues balance is now ${new_balance:.2f}.")


@tool(owner="user", rw="write")
def file_cancellation_notice_df814962(ctx: ToolContext, membership_id: str, requested_effective_date: str) -> str:
    """Let a member give their own notice of cancellation on a club membership
    contract. This creates a new cancellation-request record naming the membership
    contract and the requested effective date, and moves the contract's lifecycle
    status to cancel_pending. Use this once per cancellation notice for a given
    membership contract; calling it again for the same contract creates a second,
    separate cancellation request rather than correcting the first.

    Args:
        membership_id: Id class — the reference number of the membership contract the
            member is cancelling, reachable by looking up the member's membership
            holdings before the call.
        requested_effective_date: Fixed-format class — the calendar date the
            cancellation is to take effect, in YYYY-MM-DD format. No time zone or
            empty-value convention applies; this argument is always required.

    Returns:
        A string confirmation naming the new cancellation-request record's own
        reference number and restating the membership contract and the requested
        effective date. A membership contract that does not exist is reported back in
        the same string rather than raising.
    """
    rows = ctx.find("membership_holdings", membership_id=membership_id)
    if not rows:
        return f"No membership contract {membership_id} on file; no notice filed."
    cust = rows[0].get("customer_id")
    rid = ctx.make_id("mcr_", membership_id, requested_effective_date)
    ctx.create("membership_cancellation_requests", rid, cancellation_request_id=rid,
               customer_id=cust, membership_id=membership_id,
               requested_effective_date=requested_effective_date, outcome="pending",
               created_at=ctx.now())
    ctx.update("membership_holdings", membership_id, status="cancel_pending")
    return (f"Cancellation notice {rid} filed for membership {membership_id}, "
            f"effective {requested_effective_date}.")

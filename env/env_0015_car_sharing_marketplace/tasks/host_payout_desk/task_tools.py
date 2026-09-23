"""Hidden task tools for the Keyturn host payout desk.

Each tool performs one atomic write on a Keyturn Host Payout Account or on the running
ledger behind it. None of them aggregates history, decides eligibility or works out a
policy figure: the agent reads the account, the ledger and the records of the other
Keyturn products, works the figure out itself, and passes it in.
"""

from erlbench import ToolContext, tool


@tool(owner="user", rw="write")
def release_host_payout_draw_8e4fb8ab(ctx: ToolContext, payout_account_id: str,
                                      draw_amount: float) -> str:
    """Send money out of the host's own Keyturn Host Payout Account to the deposit account on
    file for it, as a standard bank transfer. One call books a single new transfer entry out of
    the account: the entry carries today's date, the sum sent, the payout-transfer basis, the
    standard bank transfer method and a bank reference the host can quote, and it is reported
    in the statement month the call is made in. The balance the host may draw falls by the sum
    sent and the money is on its way to their deposit account. The call has completed when the
    confirmation naming the new transfer entry's reference number and its bank reference comes
    back.

    Args:
        payout_account_id: Id class — the reference number of the host's own Keyturn Host Payout
            Account the money leaves, as returned by the payout account lookup for this host.
        draw_amount: Fixed-format class — the sum sent out to the deposit account on file, in USD,
            given as a positive number rounded half to even to 2 decimal places; there is no
            empty value and no currency conversion, the account settling in USD throughout.

    Returns:
        A single confirmation sentence in plain text. It carries the reference number of the new
        transfer entry (a string beginning "pyt_"), which is also the bank reference quotable
        against the deposit account, and the sum sent in USD to 2 decimal places. The presence of
        that transfer entry reference is what indicates the money has left the account.
    """
    rid = ctx.make_id("pyt_", payout_account_id, draw_amount)
    ctx.create("payouts_ledger", rid, ledger_id=rid, payout_account_id=payout_account_id,
               event_type="payouts_transfer_released", entry_date=ctx.now()[:10],
               entry_amount=-round(float(draw_amount), 2), entry_basis="payout_transfer",
               payout_method="ach_standard", hold_reason="none",
               settlement_reference=rid, statement_period=ctx.now()[:7])
    ctx.update("payouts_accounts", payout_account_id,
               available_balance=round(float((ctx.find("payouts_accounts",
                                          payout_account_id=payout_account_id)
                                 or [{}])[0].get("available_balance") or 0)
                                       - round(float(draw_amount), 2), 2))
    return (f"Transfer entry {rid} released from payout account {payout_account_id}: "
            f"{round(float(draw_amount), 2):.2f} USD sent to the deposit account on file, "
            f"bank reference {rid}.")


@tool(owner="agent", rw="write")
def post_recovery_correction_f20745c1(ctx: ToolContext, payout_account_id: str,
                                      source_ledger_id: str, correction_amount: float) -> str:
    """Put money back on a Keyturn Host Payout Account by booking a correcting entry against one
    earlier entry that was taken wrongly. One call books a single new correcting entry naming the
    earlier entry it corrects: the new entry carries today's date, the sum put back, the correction
    basis and a reference the host can quote, and it is reported in the statement month the call is
    made in. The earlier entry is left exactly as it stands, the account's balance rises by the sum
    put back, and the host sees both lines on their statement. The call has completed when the
    confirmation naming the new correcting entry's reference number comes back.

    Args:
        payout_account_id: Id class — the reference number of the Keyturn Host Payout Account the
            correcting entry is booked to, as returned by the payout account lookup for this host.
        source_ledger_id: Id class — the reference number of the earlier ledger entry being put
            right, as returned by the payout ledger lookup for this account.
        correction_amount: Fixed-format class — the sum put back on the account by this correcting
            entry, in USD, given as a positive number rounded half to even to 2 decimal places;
            there is no empty value and no currency conversion, the account settling in USD
            throughout.

    Returns:
        A single confirmation sentence in plain text. It carries the reference number of the new
        correcting entry (a string beginning "pyc_"), which is also the reference quotable for the
        correction, the reference number of the earlier entry it was booked against, and the sum put
        back in USD to 2 decimal places. The presence of that correcting entry reference is what
        indicates the money is back on the account.
    """
    rid = ctx.make_id("pyc_", payout_account_id, source_ledger_id, correction_amount)
    ctx.create("payouts_ledger", rid, ledger_id=rid, payout_account_id=payout_account_id,
               source_ledger_id=source_ledger_id, event_type="payouts_adjustment_posted",
               entry_date=ctx.now()[:10], entry_amount=round(float(correction_amount), 2),
               entry_basis="adjustment_correction", payout_method="none", hold_reason="none",
               settlement_reference=rid, statement_period=ctx.now()[:7])
    ctx.update("payouts_accounts", payout_account_id,
               available_balance=round(float((ctx.find("payouts_accounts",
                                          payout_account_id=payout_account_id)
                                 or [{}])[0].get("available_balance") or 0)
                                       + round(float(correction_amount), 2), 2))
    return (f"Correcting entry {rid} booked to payout account {payout_account_id} against entry "
            f"{source_ledger_id}: {round(float(correction_amount), 2):.2f} USD put back.")


@tool(owner="agent", rw="write")
def release_claim_reserve_fb50cb2e(ctx: ToolContext, payout_account_id: str,
                                   source_ledger_id: str, release_amount: float) -> str:
    """Free money that has been held back on a Keyturn Host Payout Account against an open
    exposure, so that the host may draw it again. One call books a single new release entry naming
    the reserve entry it frees: the new entry carries today's date, the sum freed, the release
    basis and no remaining ground of withholding, and it is reported in the statement month the
    call is made in. The account's reserve balance falls by the sum freed while the total credited
    stays as it was, so the host sees the same money move from held to drawable. The call has
    completed when the confirmation naming the new release entry's reference number comes back.

    Args:
        payout_account_id: Id class — the reference number of the Keyturn Host Payout Account the
            money is freed on, as returned by the payout account lookup for this host.
        source_ledger_id: Id class — the reference number of the reserve entry being freed, as
            returned by the payout ledger lookup for this account.
        release_amount: Fixed-format class — the sum freed out of that reserve entry, in USD, given
            as a positive number rounded half to even to 2 decimal places; there is no empty value
            and no currency conversion, the account settling in USD throughout.

    Returns:
        A single confirmation sentence in plain text. It carries the reference number of the new
        release entry (a string beginning "pyl_"), the reserve entry reference it was booked
        against, and the sum freed in USD to 2 decimal places. The presence of that release entry
        reference is what indicates the money is drawable again.
    """
    rid = ctx.make_id("pyl_", payout_account_id, source_ledger_id, release_amount)
    ctx.create("payouts_ledger", rid, ledger_id=rid, payout_account_id=payout_account_id,
               source_ledger_id=source_ledger_id, event_type="payouts_reserve_released",
               entry_date=ctx.now()[:10], entry_amount=-round(float(release_amount), 2),
               entry_basis="reserve_release", payout_method="none", hold_reason="none",
               statement_period=ctx.now()[:7])
    ctx.update("payouts_accounts", payout_account_id,
               reserve_balance=round(float((ctx.find("payouts_accounts",
                                          payout_account_id=payout_account_id)
                                 or [{}])[0].get("reserve_balance") or 0)
                                     - round(float(release_amount), 2), 2))
    return (f"Release entry {rid} booked on payout account {payout_account_id} against reserve "
            f"{source_ledger_id}: {round(float(release_amount), 2):.2f} USD freed.")


@tool(owner="agent", rw="write")
def post_balance_recovery_b10514b8(ctx: ToolContext, payout_account_id: str,
                                   source_ledger_id: str, recovery_amount: float) -> str:
    """Take money off a Keyturn Host Payout Account to clear what the host owes the marketplace
    after an earlier entry left the account short. One call books a single new deduction naming the
    entry it is taken against: the deduction carries today's date, the sum taken, the chargeback
    recovery basis and the statement month the call is made in, and it is booked as a debit so the
    balance free to be paid out falls by that sum. The earlier entry is left exactly as it stands
    and the host sees the recovery as its own line on the statement. The call has completed when the
    confirmation naming the new deduction's reference number comes back.

    Args:
        payout_account_id: Id class — the reference number of the Keyturn Host Payout Account the
            money is taken from, as returned by the payout account lookup for this host.
        source_ledger_id: Id class — the reference number of the earlier ledger entry the recovery is
            taken against, as returned by the payout ledger lookup for this account.
        recovery_amount: Fixed-format class — the sum taken off the account by this recovery, in USD,
            given as a positive number rounded half to even to 2 decimal places; there is no empty
            value and no currency conversion, the account settling in USD throughout.

    Returns:
        A single confirmation sentence in plain text. It carries the reference number of the new
        deduction (a string beginning "pyd_"), the reference number of the earlier entry it was taken
        against, and the sum taken in USD to 2 decimal places. The presence of that deduction
        reference is what indicates the money has been taken off the account.
    """
    rid = ctx.make_id("pyd_", payout_account_id, source_ledger_id, recovery_amount)
    ctx.create("payouts_ledger", rid, ledger_id=rid, payout_account_id=payout_account_id,
               source_ledger_id=source_ledger_id, event_type="payouts_deduction_posted",
               entry_date=ctx.now()[:10], entry_amount=-round(float(recovery_amount), 2),
               entry_basis="chargeback_recovery", payout_method="none", hold_reason="none",
               statement_period=ctx.now()[:7])
    ctx.update("payouts_accounts", payout_account_id,
               available_balance=round(float((ctx.find("payouts_accounts",
                                          payout_account_id=payout_account_id)
                                 or [{}])[0].get("available_balance") or 0)
                                       - round(float(recovery_amount), 2), 2))
    return (f"Recovery deduction {rid} booked to payout account {payout_account_id} against entry "
            f"{source_ledger_id}: {round(float(recovery_amount), 2):.2f} USD taken off.")


@tool(owner="user", rw="write")
def change_host_payout_schedule_75a33b7a(ctx: ToolContext, payout_account_id: str,
                                         payout_schedule_name: str) -> str:
    """Move the host's own Keyturn Host Payout Account onto a different payout schedule, which is
    the host's own decision about the rhythm their money is paid on. One call sets the schedule the
    account settles under to the one named: from then on the account is swept on that schedule's
    rhythm and carries that schedule's minimum, ceiling, fees and reserve terms, while everything
    already owed on the account stays exactly as it stands. The host sees the new schedule on the
    account summary. The call has completed when the confirmation naming the account and the
    schedule now in force comes back.

    Args:
        payout_account_id: Id class — the reference number of the host's own Keyturn Host Payout
            Account being moved, as returned by the payout account lookup for this host.
        payout_schedule_name: Enum class — the official full name of the schedule the account is
            moved onto, one of exactly six.
            Keyturn Standard Payout Schedule — the entry schedule, which sweeps as each trip
            completes and asks nothing of the host's trading record.
            Keyturn Weekly Batch Payout Schedule — one batched sweep a week, for a host with a
            modest settled trip count and a short time on the marketplace.
            Keyturn Express Payout Schedule — a daily sweep with a short transfer time, for a host
            whose trading record clears the express trip count, monthly earnings floor and tenure.
            Keyturn Instant Payout Schedule — money only when the host asks for it, for a host whose
            trading record clears the higher instant trip count, monthly earnings floor and tenure.
            Keyturn Fleet Settlement Schedule — one monthly settlement for a fleet operator whose
            trading record clears the fleet trip count, monthly earnings floor and tenure.
            Keyturn Reserve-Backed Settlement Schedule — one monthly settlement backed by a standing
            reserve, for the largest operators, whose trading record clears the highest trip count,
            monthly earnings floor and tenure.

    Returns:
        A single confirmation sentence in plain text. It carries the reference number of the payout
        account and the official full name of the schedule now in force on it. The presence of that
        schedule name in the confirmation is what indicates the account has been moved.
    """
    ctx.update("payouts_accounts", payout_account_id, payout_schedule_name=payout_schedule_name)
    return (f"Payout account {payout_account_id} now settles under the {payout_schedule_name}.")

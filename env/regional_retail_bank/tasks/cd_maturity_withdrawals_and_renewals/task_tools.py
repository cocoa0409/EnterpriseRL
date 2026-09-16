"""Hidden task tools for the certificate difficulty cd_maturity_withdrawals_and_renewals.

Each tool lands one atomic certificate action with the figures the agent has already worked out
from the published rules and the records. No tool aggregates history, grades a customer, judges
eligibility or refuses on a business ground.
"""

from erlbench import ToolContext, tool


@tool(owner="agent", rw="write")
def record_term_renewal_3666596b(ctx: ToolContext, certificate_id: str, new_variant_name: str,
                                 new_term_start_date: str, new_maturity_date: str,
                                 new_interest_rate: float, new_apy: float,
                                 jumbo_bonus_applied: bool,
                                 relationship_bonus_applied: bool) -> str:
    """Carry one certificate of deposit into a new term on the books of Piedmont Crescent Bank.

    One call rewrites the certificate as a certificate that is running again: its status becomes
    active, it is placed in the term tier given here, the first and last day of the new term and
    the rate and annual percentage yield the new term pays are written onto it, the two bonus
    markers are set to show which bonuses that rate includes, the one rate increase the term
    allows is made available again, and the count of terms the certificate has run through is
    raised by one. Nothing is paid out and the principal on the certificate is untouched. The
    owner sees a certificate that pays the stated rate until the stated maturity date, and the
    call has completed when the confirmation line naming the certificate, the tier, the two dates
    and the rate comes back.

    Args:
        certificate_id: Id class — the reference number of the certificate of deposit being carried
            into a new term, as returned by the certificate lookup for this customer.
        new_variant_name: Enum class — the official term tier the certificate runs in for the new
            term, exactly as spelled here. 6-Month Certificate applies when the new term is the
            bank's six month term. 11-Month No-Penalty Certificate applies when the new term is the
            eleven month term that charges no penalty after its opening days. 12-Month Certificate
            applies when the new term is the one year term. 18-Month Bump-Up Certificate applies
            when the new term is the eighteen month term that allows one rate increase. 36-Month
            Certificate applies when the new term is the three year term. 60-Month Certificate
            applies when the new term is the five year term.
        new_term_start_date: Fixed-format class — the first day of the new term, written as
            YYYY-MM-DD in the bank's local calendar with no time part.
        new_maturity_date: Fixed-format class — the last day of the new term, written as YYYY-MM-DD
            in the bank's local calendar with no time part.
        new_interest_rate: Fixed-format class — the annual interest rate the new term pays, as
            percent, 2 decimal places, e.g. 3.97, given as a number and not as a string, with the
            value already rounded to those two places before the call.
        new_apy: Fixed-format class — the annual percentage yield the new term shows, as percent, 2
            decimal places, e.g. 4.05, given as a number and not as a string, with the value already
            rounded to those two places before the call.
        jumbo_bonus_applied: Enum class — whether the rate written for the new term includes the
            jumbo bonus: true when the rate carries jumbo bonus points of any size, false when the
            rate carries none at all.
        relationship_bonus_applied: Enum class — whether the rate written for the new term includes
            the relationship bonus: true when the rate carries relationship bonus points of any
            size, false when the rate carries none at all.

    Returns:
        A single confirmation sentence in plain text. It repeats the certificate reference number,
        the official tier name the new term runs in, the first and last day of the new term as
        YYYY-MM-DD, the rate and the annual percentage yield as percentages with two decimals, and
        the count of terms the certificate has now run through as a whole number. Its arrival is
        what indicates the renewal was recorded; afterwards the certificate reads as active and
        pays the stated rate.
    """
    rows = ctx.find("cd_certificates", certificate_id=certificate_id)
    previous_terms = int(rows[0].get("renewal_count") or 0) if rows else 0
    terms_run = previous_terms + 1
    ctx.update("cd_certificates", certificate_id,
               status="active",
               variant_name=new_variant_name,
               term_start_date=new_term_start_date,
               maturity_date=new_maturity_date,
               interest_rate=round(float(new_interest_rate), 2),
               apy=round(float(new_apy), 2),
               jumbo_bonus_applied=jumbo_bonus_applied,
               relationship_bonus_applied=relationship_bonus_applied,
               bump_up_used=False,
               renewal_count=terms_run)
    return (f"Certificate {certificate_id} now runs as a {new_variant_name} from "
            f"{new_term_start_date} to {new_maturity_date} at {round(float(new_interest_rate), 2)}% "
            f"({round(float(new_apy), 2)}% APY); terms run through: {terms_run}.")


@tool(owner="user", rw="write")
def confirm_partial_withdrawal_44cc2957(ctx: ToolContext, certificate_id: str, withdrawal_amount: float,
                                        penalty_amount: float, penalty_days: int, rate_applied: float,
                                        destination: str) -> str:
    """Take part of the principal out of your own certificate of deposit before its term is over.

    One call is the owner's own instruction and carries it out at once: the sum named leaves the
    certificate and is paid out the way named here, the early withdrawal penalty named here is
    booked against the certificate with the days of interest and the rate it was worked out at, and
    the principal on the certificate drops by the sum taken out and by that penalty. The
    certificate stays open for the rest of its term. The owner sees two new entries on the
    certificate, a payment out and a penalty, a lower principal, and the confirmation line naming
    both entries, which is what indicates the withdrawal was carried out.

    Args:
        certificate_id: Id class — the reference number of the certificate of deposit the money is
            taken out of, as read out to the owner from the certificate lookup.
        withdrawal_amount: Fixed-format class — the sum of principal paid out to the owner, in USD,
            2 decimal places, always positive, given as a number rounded to the cent before the call.
        penalty_amount: Fixed-format class — the early withdrawal penalty booked against the
            certificate for this withdrawal, in USD, 2 decimal places, always positive, given as a
            number rounded to the cent before the call.
        penalty_days: Fixed-format class — the days of interest the penalty represents, written on
            the penalty entry as a non-negative integer, or empty string, and passed here as a whole
            integer number of days with no fraction.
        rate_applied: Fixed-format class — the annual rate the penalty was worked out at, written on
            the penalty entry as percent, 2 decimal places, or empty string, and passed here as a
            number already rounded to two decimal places.
        destination: Enum class — where the money paid out goes. none applies when no payment leaves
            the bank, which never holds for this action. checking applies when the proceeds are
            credited to the owner's Piedmont Crescent checking account. savings applies when they
            are credited to the owner's Piedmont Crescent savings or money market account.
            official_check applies when the bank draws an official check for the proceeds and mails
            it to the address on the owner's profile.

    Returns:
        A single confirmation sentence in plain text. It repeats the certificate reference number,
        the sum paid out and the penalty booked as USD amounts with two decimals, the way the money
        was paid out, and the principal now standing on the certificate as a USD amount with two
        decimals. Its arrival is what indicates the withdrawal and its penalty were both posted.
    """
    rows = ctx.find("cd_certificates", certificate_id=certificate_id)
    owner_id = rows[0].get("customer_id") if rows else ""
    balance_before = float(rows[0].get("principal_balance") or 0) if rows else 0.0
    posted = ctx.now()[:10]
    wid = ctx.make_id("cdw_", certificate_id, withdrawal_amount, penalty_amount, penalty_days,
                      rate_applied, destination)
    ctx.create("cd_transactions", wid, cd_txn_id=wid, certificate_id=certificate_id,
               customer_id=owner_id, event_type="cd_withdrawal",
               amount=round(float(withdrawal_amount), 2), posted_date=posted,
               deposit_kind="none", funding_source="none", trace_number="",
               counterparty_account_id="", interest_period="", rate_applied="",
               destination=destination, withdrawal_kind="early_partial", source_item_id="",
               penalty_days="", adjustment_reason="none")
    pid = ctx.make_id("cdp_", wid, penalty_amount, penalty_days, rate_applied)
    ctx.create("cd_transactions", pid, cd_txn_id=pid, certificate_id=certificate_id,
               customer_id=owner_id, event_type="cd_penalty",
               amount=round(float(penalty_amount), 2), posted_date=posted,
               deposit_kind="none", funding_source="none", trace_number="",
               counterparty_account_id="", interest_period="",
               rate_applied=round(float(rate_applied), 2), destination="none",
               withdrawal_kind="none", source_item_id=wid, penalty_days=int(penalty_days),
               adjustment_reason="none")
    balance_after = round(balance_before - float(withdrawal_amount) - float(penalty_amount), 2)
    ctx.update("cd_certificates", certificate_id, principal_balance=balance_after)
    return (f"Certificate {certificate_id}: {round(float(withdrawal_amount), 2)} paid out to "
            f"{destination} (entry {wid}) and a penalty of {round(float(penalty_amount), 2)} booked "
            f"(entry {pid}); principal now {balance_after}.")


@tool(owner="agent", rw="write")
def credit_mischarged_penalty_7001af6d(ctx: ToolContext, certificate_id: str, source_item_id: str,
                                       entry_amount: float, entry_days: int,
                                       adjustment_reason: str) -> str:
    """Book the early withdrawal charge a certificate of deposit is owed for principal already taken out of it.

    One call adds a new charge entry to the certificate's ledger, ties it to the withdrawal it belongs to,
    records the days of interest and the ground on which it is booked, and lowers the principal standing on
    the certificate by the same amount. Nothing is paid out and no other account is touched. The owner sees a
    new charge on the certificate dated today against the withdrawal it names, and a principal balance lower
    by that charge. The call has completed when the confirmation line naming the new entry, the withdrawal it
    is tied to and the principal now standing on the certificate comes back.

    Args:
        certificate_id: Id class — the reference number of the certificate of deposit the charge is booked
            against, as returned by the certificate lookup for this customer.
        source_item_id: Id class — the reference number of the single ledger entry this charge belongs to,
            namely the withdrawal that took the principal out; it is read from the certificate's ledger
            lookup, which returns each entry's own reference number.
        entry_amount: Fixed-format class — the amount of the charge, in USD, 2 decimal places, always
            positive, given as a number already rounded to the cent before the call.
        entry_days: Fixed-format class — the days of interest this charge stands for, written on the entry as
            a non-negative integer, or empty string, and passed here as a whole integer number of days with
            no fraction.
        adjustment_reason: Enum class — the ground recorded on the entry. none applies when the entry is an
            ordinary charge raised under the certificate's own terms rather than a correction of the bank's
            own records. bank_error applies when the entry is booked to put right something the bank itself
            got wrong, including a charge the bank failed to raise at the time. death_waiver applies only
            when estate services have confirmed the owner's death or adjudicated incompetence.

    Returns:
        A single confirmation sentence in plain text. It repeats the certificate reference number, the
        reference number minted for the new charge entry, the reference number of the withdrawal it is tied
        to, the amount as a USD figure with two decimals, the days of interest as a whole number, and the
        principal now standing on the certificate as a USD figure with two decimals. Its arrival is what
        indicates the charge was booked.
    """
    rows = ctx.find("cd_certificates", certificate_id=certificate_id)
    owner_id = rows[0].get("customer_id") if rows else ""
    balance_before = float(rows[0].get("principal_balance") or 0) if rows else 0.0
    rid = ctx.make_id("cdc_", certificate_id, source_item_id, entry_amount, entry_days, adjustment_reason)
    ctx.create("cd_transactions", rid, cd_txn_id=rid, certificate_id=certificate_id,
               customer_id=owner_id, event_type="cd_penalty",
               amount=round(float(entry_amount), 2), posted_date=ctx.now()[:10],
               deposit_kind="none", funding_source="none", trace_number="",
               counterparty_account_id="", interest_period="", rate_applied="",
               destination="none", withdrawal_kind="none", source_item_id=source_item_id,
               penalty_days=int(entry_days), adjustment_reason=adjustment_reason)
    balance_after = round(balance_before - float(entry_amount), 2)
    ctx.update("cd_certificates", certificate_id, principal_balance=balance_after)
    return (f"Certificate {certificate_id}: charge {rid} of {round(float(entry_amount), 2)} over "
            f"{int(entry_days)} day(s) booked against withdrawal {source_item_id}; principal now "
            f"{balance_after}.")


@tool(owner="user", rw="write")
def confirm_term_add_on_1e70ab4d(ctx: ToolContext, certificate_id: str, customer_id: str,
                                 deposit_amount: float, funding_source: str) -> str:
    """Put money of your own into your certificate of deposit while its term is running.

    One call is the owner's own deposit and lands it at once: the sum named is added to the certificate's
    ledger as an in-term add-on showing where the money came from, and the principal standing on the
    certificate rises by the same sum. The term dates and the rate the certificate pays are untouched, so the
    money earns the certificate's existing rate from today. The owner sees a new deposit entry dated today
    and a higher principal, and the call has completed when the confirmation line naming the new entry and
    the principal now standing on the certificate comes back.

    Args:
        certificate_id: Id class — the reference number of the certificate of deposit the money goes into,
            as read out to the owner from the certificate lookup.
        customer_id: Id class — the reference number of the customer profile the certificate belongs to,
            taken from the customer profile lookup made at the start of the call.
        deposit_amount: Fixed-format class — the sum of the owner's own money added to the certificate, in
            USD, 2 decimal places, always positive, given as a number already rounded to the cent before the
            call.
        funding_source: Enum class — where the money comes from. none applies when no money moves, which
            never holds for a deposit. pcb_checking applies when it is drawn from the owner's Piedmont
            Crescent checking account. pcb_savings applies when it is drawn from the owner's Piedmont
            Crescent savings or money market account. external_ach applies when it arrives by electronic
            transfer from an account at another bank. check applies when the owner deposits a paper check.
            cash applies when the owner hands cash over at a branch. wire applies when the money arrives by
            wire transfer.

    Returns:
        A single confirmation sentence in plain text. It repeats the certificate reference number, the
        reference number minted for the new deposit entry, the sum added as a USD figure with two decimals,
        where the money came from, and the principal now standing on the certificate as a USD figure with two
        decimals. Its arrival is what indicates the deposit was posted.
    """
    rows = ctx.find("cd_certificates", certificate_id=certificate_id)
    balance_before = float(rows[0].get("principal_balance") or 0) if rows else 0.0
    rid = ctx.make_id("cda_", certificate_id, customer_id, deposit_amount, funding_source)
    ctx.create("cd_transactions", rid, cd_txn_id=rid, certificate_id=certificate_id,
               customer_id=customer_id, event_type="cd_deposit",
               amount=round(float(deposit_amount), 2), posted_date=ctx.now()[:10],
               deposit_kind="term_add_on", funding_source=funding_source, trace_number="",
               counterparty_account_id="", interest_period="", rate_applied="",
               destination="none", withdrawal_kind="none", source_item_id="",
               penalty_days="", adjustment_reason="none")
    balance_after = round(balance_before + float(deposit_amount), 2)
    ctx.update("cd_certificates", certificate_id, principal_balance=balance_after)
    return (f"Certificate {certificate_id}: deposit {rid} of {round(float(deposit_amount), 2)} from "
            f"{funding_source} posted; principal now {balance_after}.")

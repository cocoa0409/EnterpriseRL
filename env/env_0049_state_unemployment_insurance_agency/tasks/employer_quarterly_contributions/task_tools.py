"""Hidden task tools for the employer_quarterly_contributions difficulty of
env_0049_state_unemployment_insurance_agency (Lakeland Department of Workforce Security).

Each tool performs one atomic write on an employer's unemployment insurance tax account and is
reached only through the unlock/call meta tools. The figures passed in are worked out by the agent
from the published policy and the account records; the tools record them as given and judge
nothing.
"""

from erlbench import ToolContext, tool


class _Records:
    """Plain record lookups shared by the tools below (not a tool)."""

    @staticmethod
    def account(ctx: ToolContext, employer_account_id: str) -> dict:
        rows = ctx.find("employer_accounts", employer_account_id=employer_account_id)
        return rows[0] if rows else {}


@tool(owner="agent", rw="write")
def book_estimated_assessment_54fbfb5a(ctx: ToolContext, employer_account_id: str, quarter: str,
                                       assessment_amount: float) -> str:
    """Book an estimated contribution assessment for one calendar quarter on an employer's unemployment insurance tax account.

    One call adds one contribution assessment entry for the quarter given, marked as resting on an
    estimate (not on a filed report), dated today, for the amount given, and recording the
    contribution rate currently on the account as the rate applied. The account's balance due rises
    by the same amount, so the employer sees the estimated contributions as owed for that quarter on
    its statement and in its online account; an estimate gives way to the real figures of a filed report. The entry reference
    returned identifies the booked assessment.

    Args:
        employer_account_id: Id class — the reference number of the employer's unemployment insurance tax account, as returned by the employer account lookup.
        quarter: Fixed-format class — the calendar quarter the estimate is for, written YYYY-Qn (for example the second quarter of 2026 is 2026-Q2); the stored format is "YYYY-Qn; empty when not quarter-specific", and an empty value is never used for an estimate.
        assessment_amount: Fixed-format class — the estimated contributions in US dollars, stored as USD, 2 decimal places, always positive; pass the figure already rounded to the cent (2 decimal places), it is recorded exactly as given.

    Returns:
        A confirmation sentence that starts with "Estimated assessment booked" and states the entry
        reference (an opaque reference beginning with "est_"), the quarter, the amount assessed in USD
        with 2 decimal places, the contribution rate recorded as applied (4 decimal places) and the
        account's new balance due in USD with 2 decimal places; that sentence means the assessment is
        on the account.
    """
    amount = round(float(assessment_amount), 2)
    acct = _Records.account(ctx, employer_account_id)
    rate = round(float(acct.get("contribution_rate") or 0), 4)
    rid = ctx.make_id("est_", employer_account_id, quarter, amount)
    today = ctx.now()[:10]
    ctx.create("employer_tax_ledger", rid, tax_entry_id=rid, employer_account_id=employer_account_id,
               customer_id=acct.get("customer_id", ""), event_type="taxacct_contribution_assessed",
               entry_date=today, quarter=quarter, component="contribution", amount=amount,
               assessment_basis="estimated_assessment", contribution_rate_applied=rate,
               penalty_type="not_applicable", payment_channel="not_applicable",
               adjustment_reason="not_applicable", credit_source="not_applicable")
    new_balance = round(float(acct.get("balance_due") or 0) + amount, 2)
    if acct:
        ctx.update("employer_accounts", employer_account_id, balance_due=new_balance)
    return (f"Estimated assessment booked: entry {rid} for {quarter}, {amount:.2f} USD at a recorded rate of "
            f"{rate:.4f}; balance due is now {new_balance:.2f} USD.")


@tool(owner="user", rw="write")
def request_credit_refund_f44db5b5(ctx: ToolContext, employer_account_id: str, credit_payment_entry_id: str,
                                   requested_amount: float) -> str:
    """Lodge the employer's own request to have the credit balance on its unemployment insurance tax account paid out as a refund.

    One call records one refund request in the employer's name on the account, dated today, asking
    for the amount given and citing the payment that created the credit. The request is received for
    processing: nothing is paid by this call, the credit remains on the account while the request
    is open and the refund is issued against it, and the employer can see the request and its status in its online
    account. The request reference returned identifies it.

    Args:
        employer_account_id: Id class — the reference number of the employer's unemployment insurance tax account, as returned by the employer account lookup.
        credit_payment_entry_id: Id class — the reference number of the balance-history entry of the payment that created the credit, as shown in the account's balance history.
        requested_amount: Fixed-format class — the refund amount asked for in US dollars, stored as USD, 2 decimal places; 0.00 when no amount; pass the figure already rounded to the cent (2 decimal places), it is recorded exactly as given.

    Returns:
        A confirmation sentence that starts with "Refund request received" and states the request
        reference (an opaque reference beginning with "acr_"), the amount asked for in USD with 2
        decimal places, the cited payment entry and the request status "received"; that sentence
        means the request is on the account awaiting the refund.
    """
    amount = round(float(requested_amount), 2)
    acct = _Records.account(ctx, employer_account_id)
    rid = ctx.make_id("acr_", employer_account_id, credit_payment_entry_id, amount)
    ctx.create("employer_account_requests", rid, account_request_id=rid, employer_account_id=employer_account_id,
               customer_id=acct.get("customer_id", ""), request_type="credit_refund",
               request_date=ctx.now()[:10], quarter="", requested_amount=amount,
               request_status="received", created_at=ctx.now())
    return (f"Refund request received: request {rid} for {amount:.2f} USD citing payment entry "
            f"{credit_payment_entry_id}; status received.")


@tool(owner="agent", rw="write")
def assess_late_report_penalty_9b2fdf0c(ctx: ToolContext, employer_account_id: str, quarter: str,
                                        penalty_amount: float) -> str:
    """Book a late report penalty for one calendar quarter on an employer's unemployment insurance tax account.

    One call adds one late report penalty entry for the quarter given, dated today, for the amount
    given, and raises the account's balance due by the same amount; the employer sees the penalty as
    owed for that quarter on its statement and in its online account. The entry reference returned
    identifies the booked penalty.

    Args:
        employer_account_id: Id class — the reference number of the employer's unemployment insurance tax account, as returned by the employer account lookup.
        quarter: Fixed-format class — the calendar quarter whose report the penalty is for, written YYYY-Qn (for example the second quarter of 2026 is 2026-Q2); the stored format is "YYYY-Qn; empty when not quarter-specific", and an empty value is never used for a penalty.
        penalty_amount: Fixed-format class — the penalty in US dollars, stored as USD, 2 decimal places, always positive; pass the figure already rounded to the cent (2 decimal places), it is recorded exactly as given.

    Returns:
        A confirmation sentence that starts with "Late report penalty booked" and states the entry
        reference (an opaque reference beginning with "ltp_"), the quarter, the penalty amount in USD
        with 2 decimal places and the account's new balance due in USD with 2 decimal places; that
        sentence means the penalty is on the account.
    """
    amount = round(float(penalty_amount), 2)
    acct = _Records.account(ctx, employer_account_id)
    rid = ctx.make_id("ltp_", employer_account_id, quarter, amount)
    ctx.create("employer_tax_ledger", rid, tax_entry_id=rid, employer_account_id=employer_account_id,
               customer_id=acct.get("customer_id", ""), event_type="taxacct_penalty_assessed",
               entry_date=ctx.now()[:10], quarter=quarter, component="penalty", amount=amount,
               assessment_basis="not_applicable", contribution_rate_applied=0.0, penalty_type="late_report",
               payment_channel="not_applicable", adjustment_reason="not_applicable", credit_source="not_applicable")
    new_balance = round(float(acct.get("balance_due") or 0) + amount, 2)
    if acct:
        ctx.update("employer_accounts", employer_account_id, balance_due=new_balance)
    return (f"Late report penalty booked: entry {rid} for {quarter}, {amount:.2f} USD; balance due is now "
            f"{new_balance:.2f} USD.")


@tool(owner="user", rw="write")
def request_penalty_relief_44d7156f(ctx: ToolContext, employer_account_id: str, penalty_entry_id: str, quarter: str,
                                    requested_amount: float) -> str:
    """Lodge the employer's own request for relief from a late report penalty it has already paid, asking for an amount to be refunded.

    One call records one penalty abatement request in the employer's name on the account for the
    quarter given, dated today, asking for the amount given to be refunded and citing the penalty
    entry concerned. The request is received for decision by the Department's tax review unit:
    nothing is credited or refunded by this call, and the employer can see the request and its status
    in its online account. The request reference returned identifies it.

    Args:
        employer_account_id: Id class — the reference number of the employer's unemployment insurance tax account, as returned by the employer account lookup.
        penalty_entry_id: Id class — the reference number of the balance-history entry of the late report penalty the relief is asked for, as shown in the account's balance history.
        quarter: Fixed-format class — the calendar quarter of that penalty, written YYYY-Qn (for example 2026-Q3); the stored format is "YYYY-Qn; empty when not quarter-specific", and an empty value is never used for a relief request.
        requested_amount: Fixed-format class — the amount of the paid penalty asked to be refunded, in US dollars, stored as USD, 2 decimal places; 0.00 when no amount; pass the figure already rounded to the cent (2 decimal places), it is recorded exactly as given.

    Returns:
        A confirmation sentence that starts with "Penalty relief request received" and states the
        request reference (an opaque reference beginning with "acr_"), the quarter, the cited penalty
        entry, the amount asked for in USD with 2 decimal places and the request status "received";
        that sentence means the request is on the account awaiting decision.
    """
    amount = round(float(requested_amount), 2)
    acct = _Records.account(ctx, employer_account_id)
    rid = ctx.make_id("acr_", employer_account_id, penalty_entry_id, quarter, amount)
    ctx.create("employer_account_requests", rid, account_request_id=rid, employer_account_id=employer_account_id,
               customer_id=acct.get("customer_id", ""), request_type="penalty_abatement",
               request_date=ctx.now()[:10], quarter=quarter, requested_amount=amount,
               request_status="received", created_at=ctx.now())
    return (f"Penalty relief request received: request {rid} for {quarter} citing penalty entry {penalty_entry_id}, "
            f"{amount:.2f} USD asked; status received.")

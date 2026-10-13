"""Hidden task tools of the host_standing_and_penalties difficulty (Roamhaven host accounts).

Each tool performs exactly one atomic business write on the Host Accounts records and is reached
only through the unlock/call meta-tools, by the name an extended policy of host.extended.yaml gives
as its target_tool. No tool checks a policy condition, aggregates history or computes a value:
every figure and choice is decided by the agent from the published policy and the records, and
passed in.
"""

from erlbench import ToolContext, tool


@tool(owner="agent", rw="write")
def apply_superhost_decision_f25b833f(ctx: ToolContext, host_account_id: str, assessment_event_id: str,
                                      assessment_outcome: str, tier_change: str, variant_name: str) -> str:
    """Record a Superhost decision on one quarterly Superhost assessment and set the host tier it gives.

    Support uses this to record the outcome of a decision taken on an individual host's Superhost
    assessment. One call writes the outcome and the tier effect onto that assessment record, and
    rewrites the host account's current tier to the tier passed in, stamping today's date as the
    account's latest tier change and setting the date Superhost status is counted from (today's
    date when the tier passed in is Superhost, empty for any other tier). Nothing else changes.
    Afterwards the assessment shows its outcome and tier effect, and the host account shows the new
    tier, its tier-change date and its Superhost start date. The call succeeds when the receipt
    below is returned.

    Args:
        host_account_id: Id class — the reference number of the host account the assessment belongs
            to, as returned by the host account lookup for the verified host.
        assessment_event_id: Id class — the reference number of the Superhost assessment record being
            decided, as returned by the host account history lookup.
        assessment_outcome: Enum class — the outcome recorded on the assessment, exactly one of: met
            when the decision meets the Superhost standards; not_met when it does not; none is never
            the outcome of a decision and is not used through this action.
        tier_change: Enum class — the tier effect recorded on the assessment, exactly one of: promoted
            when a met decision moves a Standard Host up to Superhost; demoted when a not-met decision
            moves a Superhost down to Standard Host; unchanged when the decision leaves the tier as it
            was; none is never the effect of a decision and is not used through this action.
        variant_name: Enum class — the host tier the decision leaves the account in, exactly one of:
            Superhost when the decision is met; Standard Host when it is not met; Starter Host never,
            since a Superhost decision does not move an account back to the entry programme; Professional
            Host never, since professional tiers are not decided by Superhost assessments; Professional
            Host Plus never, for the same reason; Enterprise Partner never, for the same reason.

    Returns:
        A one-line confirmation string naming the assessment record, the outcome and tier effect now
        on it, the host account, the tier now on the account, the tier-change date (YYYY-MM-DD,
        today's date) and the Superhost start date (YYYY-MM-DD, or "none" when the tier is not
        Superhost); its presence means the decision was recorded.
    """
    today = ctx.now()[:10]
    since = today if variant_name == "Superhost" else ""
    ctx.update("host_account_events", assessment_event_id, assessment_outcome=assessment_outcome,
               tier_change=tier_change)
    ctx.update("host_accounts", host_account_id, variant_name=variant_name, superhost_since=since,
               last_tier_change_date=today)
    return (f"Assessment {assessment_event_id} recorded as {assessment_outcome} ({tier_change}); host account "
            f"{host_account_id} now holds the {variant_name} tier; tier change dated {today}; "
            f"Superhost since {since or 'none'}.")


@tool(owner="user", rw="write")
def claim_superhost_travel_credit_0d8c95c2(ctx: ToolContext, host_account_id: str, assessment_quarter: str,
                                           amount: float) -> str:
    """Accept the Roamhaven Superhost travel credit earned by a completed run of assessments.

    The host uses this in person to accept the travel credit for one completed run of Superhost
    assessments onto their host account. One call books one travel credit record on the host
    account, dated today, carrying the quarter of the assessment that completed the run and the
    credit amount passed in. The credit is a Roamhaven travel credit, not cash, and is never paid to
    a payout method. Afterwards the host's account history shows the travel credit with its quarter,
    date and amount. The call succeeds when the receipt below is returned.

    Args:
        host_account_id: Id class — the reference number of the host's own host account, as read out
            by support from the host account lookup.
        assessment_quarter: Fixed-format class — the quarter of the Superhost assessment that completed
            the run, in the format YYYY-Qn, e.g. 2026-Q3 (four-digit year, a hyphen, the letter Q and
            the quarter number 1 to 4), exactly as the quarter is shown on that assessment.
        amount: Fixed-format class — the travel credit accepted, a USD amount, 2 decimal places,
            positive; a value with more decimals is rounded half to even to the cent before it is
            booked.

    Returns:
        A one-line confirmation string naming the travel credit record reference number, the host
        account, the quarter the credit is booked against, the booking date (YYYY-MM-DD, today's
        date) and the credit amount in USD to 2 decimal places; its presence means the credit is on
        the account.
    """
    acct = ctx.find("host_accounts", host_account_id=host_account_id)
    customer_id = acct[0].get("customer_id") if acct else ""
    value = round(float(amount), 2)
    today = ctx.now()[:10]
    rid = ctx.make_id("hev_", host_account_id, assessment_quarter, value)
    ctx.create("host_account_events", rid, host_event_id=rid, host_account_id=host_account_id,
               customer_id=customer_id, event_type="host_travel_credit_issued", event_date=today,
               stay_id="", amount=value, fee_base_amount=0.0, penalty_band="none", initiated_by="none",
               appeal_id="", waiver_reason="none", original_event_id="", strike_type="none",
               assessment_quarter=assessment_quarter, average_rating=0.0, response_rate_pct=0.0,
               cancellation_rate_pct=0.0, stays_12m=0, nights_12m=0, assessment_outcome="none",
               tier_change="none", tax_year="", transaction_count=0)
    return (f"Travel credit {rid} booked on host account {host_account_id} for {assessment_quarter} on {today}: "
            f"USD {value:.2f}.")


@tool(owner="user", rw="write")
def enroll_professional_tier_a874e389(ctx: ToolContext, host_account_id: str, variant_name: str) -> str:
    """Enroll a professional host account in the professional tier its records qualify it for.

    The host uses this in person to enroll their business host account, accepting the service
    commitments that come with the tier. One call rewrites the account's current host tier to the
    tier passed in, stamps today's date as the account's latest tier change, and clears the date
    Superhost status is counted from (a professional tier carries no Superhost status). Nothing else
    on the account changes. Afterwards the host account shows the new tier and its tier-change date
    to the host and to support. The call succeeds when the receipt below is returned.

    Args:
        host_account_id: Id class — the reference number of the host's own host account, as read out
            by support from the host account lookup.
        variant_name: Enum class — the professional tier the enrollment places the account in, exactly
            one of: Professional Host when the account's live listings and listing rating do not qualify
            it for the higher programme and it stays in the standard professional programme;
            Professional Host Plus when they qualify it for the higher programme; Starter Host never, since an enrollment does not leave
            the professional programmes; Standard Host never, for the same reason; Superhost never, for
            the same reason; Enterprise Partner never, since that tier rests on a signed partner
            agreement rather than an enrollment.

    Returns:
        A one-line confirmation string naming the host account reference number, the host tier now
        on the account and the tier-change date (YYYY-MM-DD, today's date); its presence means the
        enrollment was recorded.
    """
    today = ctx.now()[:10]
    ctx.update("host_accounts", host_account_id, variant_name=variant_name, superhost_since="",
               last_tier_change_date=today)
    return f"Host account {host_account_id} is enrolled in the {variant_name} tier as of {today}."


@tool(owner="agent", rw="write")
def refund_rerated_host_fee_9248fd19(ctx: ToolContext, host_account_id: str, stay_id: str, amount: float) -> str:
    """Refund the difference on one stay's host service fee after the fee was re-rated.

    Support uses this to give a host back part of the host service fee withheld on one stay, when
    that fee has been re-rated at a lower percentage. One call books one host service fee refund on
    the host account, dated today, tied to the stay, carrying the refund amount passed in; since no
    guest was refunded, the refund records no host-funded guest refund behind it. The refund reduces
    the host service fees the account has paid. Afterwards the host's account history shows the
    refund against the stay. The call succeeds when the receipt below is returned.

    Args:
        host_account_id: Id class — the reference number of the host account the stay was hosted
            under, as returned by the host account lookup for the verified host.
        stay_id: Id class — the reference number of the stay whose host service fee is re-rated, as
            returned by the stay lookup or shown on the host service fee record of that stay.
        amount: Fixed-format class — the host service fee refunded, a USD amount, 2 decimal places,
            positive; a value with more decimals is rounded half to even to the cent before it is
            booked.

    Returns:
        A one-line confirmation string naming the refund record reference number, the stay, the
        booking date (YYYY-MM-DD, today's date) and the refund amount in USD to 2 decimal places; its
        presence means the refund is on the account.
    """
    acct = ctx.find("host_accounts", host_account_id=host_account_id)
    customer_id = acct[0].get("customer_id") if acct else ""
    value = round(float(amount), 2)
    today = ctx.now()[:10]
    rid = ctx.make_id("hev_", host_account_id, stay_id, value)
    ctx.create("host_account_events", rid, host_event_id=rid, host_account_id=host_account_id,
               customer_id=customer_id, event_type="host_service_fee_refunded", event_date=today,
               stay_id=stay_id, amount=value, fee_base_amount=0.0, penalty_band="none", initiated_by="none",
               appeal_id="", waiver_reason="none", original_event_id="", strike_type="none",
               assessment_quarter="", average_rating=0.0, response_rate_pct=0.0, cancellation_rate_pct=0.0,
               stays_12m=0, nights_12m=0, assessment_outcome="none", tier_change="none", tax_year="",
               transaction_count=0)
    return f"Host service fee refund {rid} booked on {today} for stay {stay_id}: refund USD {value:.2f}."

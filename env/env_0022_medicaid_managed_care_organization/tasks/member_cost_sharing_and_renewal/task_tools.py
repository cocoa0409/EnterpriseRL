"""Hidden task tools for difficulty member_cost_sharing_and_renewal (category plan).
Output of erl-task-instantiate. Each tool is named <verb>_<object>_<uuid8>, is reached only through the
unlock_* -> call_* meta-tools, performs one atomic write on the plan category, and judges no eligibility.
"""

from erlbench import ToolContext, tool


@tool(owner="agent", rw="write")
def book_over_cap_refund_b068d625(ctx: ToolContext, membership_id: str, related_claim_number: str,
                                  cost_share_period: str, refund_amount: float) -> str:
    """Book an over-cap cost-sharing refund on a Prairie Ridge membership. One call adds one refund entry
    to the membership's claim ledger that returns the given amount of member copays to the member: the
    entry carries the refund as a negative member cost share, is marked refunded, points back to the
    medical claim it is booked against and to the cost-sharing period it belongs to, and is dated today.
    The member sees the refund as a credit line on the next explanation of benefits. The call succeeds when
    the receipt returns the new refund entry reference.

    Args:
        membership_id: Id class — the membership reference number of the Prairie Ridge membership the refund is booked on, as returned by the membership lookup.
        related_claim_number: Verbatim class — the claim number of the medical claim the refund entry is booked against, copied exactly as it appears in the claim history or on the explanation of benefits, character for character, with no change to letters, digits or hyphens (verbatim).
        cost_share_period: Fixed-format class — the cost-sharing period the refund belongs to, written exactly as the period label on the claim it is booked against, in the form YYYY-Qn for quarterly caps, YYYY for annual caps (for example 2026-Q2 or 2026); no other form is accepted.
        refund_amount: Fixed-format class — the refund amount in USD as a positive number with 2 decimal places, rounded half up to the cent before it is passed; it is booked as the negative of this amount.

    Returns:
        A confirmation string of the form "Refund entry <refund_entry_id> booked on membership <membership_id>: <refund_amount> USD against claim <related_claim_number> for period <cost_share_period>, status refunded, dated <YYYY-MM-DD>." where refund_entry_id is the new ledger entry reference (text starting "rfd_"), refund_amount is the amount returned with 2 decimals, and the date is today's booking date. A returned refund_entry_id means the refund is on the books.
    """
    rows = ctx.find("plan_memberships", membership_id=membership_id)
    customer_id = rows[0].get("customer_id") if rows else ""
    amount = round(float(refund_amount), 2)
    rid = ctx.make_id("rfd_", membership_id, related_claim_number, cost_share_period, amount)
    today = ctx.now()[:10]
    ctx.create("plan_claims", rid, plan_claim_id=rid, membership_id=membership_id, customer_id=customer_id,
               event_type="plan_cost_share_refund", claim_number="", related_claim_number=related_claim_number,
               service_date="", service_category="not_applicable", provider_npi="", billed_amount=0.0,
               plan_paid_amount=0.0, member_cost_share=round(-amount, 2), adjudication_status="refunded",
               denial_code="none", cost_share_period=cost_share_period, booked_date=today)
    return (f"Refund entry {rid} booked on membership {membership_id}: {amount:.2f} USD against claim "
            f"{related_claim_number} for period {cost_share_period}, status refunded, dated {today}.")


@tool(owner="user", rw="write")
def pay_past_due_premium_fdc43b6b(ctx: ToolContext, membership_id: str, coverage_month: str,
                                  payment_amount: float, payment_method: str) -> str:
    """Make the family's own CHIP premium payment for one coverage month of a Prairie Ridge membership. One
    call posts one payment entry for the given coverage month with the given amount and payment method,
    dated today, and settles that coverage month: the amount billed for the month leaves the premium balance
    shown on the membership (never below zero), whatever amount was paid. The family sees the payment and the
    settled month on the premium account at once and receives a payment confirmation number. The call
    succeeds when the receipt returns the confirmation number.

    Args:
        membership_id: Id class — the membership reference number of the CHIP membership whose premium is being paid, as returned by the membership lookup and read out by the representative.
        coverage_month: Fixed-format class — the coverage month the payment is for, in YYYY-MM format (for example 2026-08), exactly as the month is labelled on the premium account.
        payment_amount: Fixed-format class — the amount paid in USD as a positive number with 2 decimal places, rounded half up to the cent.
        payment_method: Enum class — how the family pays; exactly one of: online_portal when paying through the member portal website; phone_ivr when paying by card or bank draft over the phone payment line; mail_check when the payment is a mailed personal check; money_order when the payment is a mailed money order; not_applicable when no payment method applies, which is never the case for a payment the family makes.

    Returns:
        A confirmation string of the form "Payment <payment_entry_id> posted: <payment_amount> USD for coverage month <coverage_month> on membership <membership_id> by <payment_method>; confirmation number <payment_reference>; premium balance now <premium_balance> USD." where payment_entry_id is the new premium ledger entry reference (text starting "pay_"), payment_reference is the confirmation number (text starting "PRP-"), and premium_balance is the membership's remaining premium balance with 2 decimals. A returned confirmation number means the payment is posted.
    """
    amount = round(float(payment_amount), 2)
    rows = ctx.find("plan_memberships", membership_id=membership_id)
    customer_id = rows[0].get("customer_id") if rows else ""
    balance = round(float(rows[0].get("premium_balance") or 0), 2) if rows else 0.0
    pid = ctx.make_id("pay_", membership_id, coverage_month, amount, payment_method)
    reference = "PRP-" + ctx.make_id("", membership_id, coverage_month, amount, length=7).upper()
    ctx.create("plan_premiums", pid, plan_premium_id=pid, membership_id=membership_id, customer_id=customer_id,
               event_type="plan_premium_paid", coverage_month=coverage_month, amount=amount,
               payment_method=payment_method, payment_reference=reference, waiver_reason="not_applicable",
               posted_date=ctx.now()[:10])
    billed = sum(float(r.get("amount") or 0) for r in ctx.find("plan_premiums", membership_id=membership_id,
                                                              coverage_month=coverage_month,
                                                              event_type="plan_premium_billed"))
    new_balance = round(max(0.0, balance - billed), 2)
    if rows:
        ctx.update("plan_memberships", membership_id, premium_balance=new_balance)
    return (f"Payment {pid} posted: {amount:.2f} USD for coverage month {coverage_month} on membership "
            f"{membership_id} by {payment_method}; confirmation number {reference}; premium balance now "
            f"{new_balance:.2f} USD.")


@tool(owner="agent", rw="write")
def book_own_pcp_visit_rerating_ea94b99c(ctx: ToolContext, related_claim_number: str, reversal_amount: float) -> str:
    """Book the re-rating adjustment for visits a member's own primary care provider billed under the
    specialist visit copay. One call adds one adjustment entry to the member's claim ledger, booked against
    the named paid medical claim: the entry gets a new adjustment claim number, copies the named claim's
    membership, service date, copay category, billing provider and cost-sharing period, carries the given
    amount as a negative member cost share, is marked adjusted with reason none, and is dated today. The
    member sees the returned copay as a credit on the next explanation of benefits. The call succeeds when
    the receipt returns the new adjustment claim number.

    Args:
        related_claim_number: Verbatim class — the claim number of the paid medical claim the adjustment entry is booked against, copied exactly as it appears in the claim history, character for character, with no change to letters, digits or hyphens (verbatim).
        reversal_amount: Fixed-format class — the copay amount returned to the member in USD as a positive number with 2 decimal places, rounded half up to the cent; it is booked as the negative of this amount.

    Returns:
        A confirmation string of the form "Adjustment <adjustment_claim_number> (entry <adjustment_entry_id>) booked against claim <related_claim_number> on membership <membership_id>: copay reduced by <reversal_amount> USD, dated <YYYY-MM-DD>." where adjustment_claim_number is the new adjustment claim number (text starting "ADJ-"), adjustment_entry_id is the ledger entry reference (text starting "pcr_"), membership_id is the membership of the named claim, and reversal_amount has 2 decimals. A returned adjustment claim number means the adjustment is booked.
    """
    found = ctx.find("plan_claims", claim_number=related_claim_number, event_type="plan_claim_booked")
    original = found[0] if found else {}
    amount = round(float(reversal_amount), 2)
    rid = ctx.make_id("pcr_", related_claim_number, amount)
    number = "ADJ-" + ctx.make_id("", "pcr_", related_claim_number, amount, length=8).upper()
    ctx.create("plan_claims", rid, plan_claim_id=rid, membership_id=original.get("membership_id", ""),
               customer_id=original.get("customer_id", ""), event_type="plan_claim_adjusted", claim_number=number,
               related_claim_number=related_claim_number, service_date=original.get("service_date", ""),
               service_category=original.get("service_category", "not_applicable"),
               provider_npi=original.get("provider_npi", ""), billed_amount=0.0, plan_paid_amount=0.0,
               member_cost_share=round(-amount, 2), adjudication_status="adjusted", denial_code="none",
               cost_share_period=original.get("cost_share_period", ""), booked_date=ctx.now()[:10])
    return (f"Adjustment {number} (entry {rid}) booked against claim {related_claim_number} on membership "
            f"{original.get('membership_id', '')}: copay reduced by {amount:.2f} USD, dated {ctx.now()[:10]}.")


@tool(owner="agent", rw="write")
def book_office_visit_rerating_0e97c2c0(ctx: ToolContext, related_claim_number: str, reversal_amount: float) -> str:
    """Book the preventive re-rating adjustment for office visits a member's primary care providers billed
    under the primary care visit copay. One call adds one adjustment entry to the member's claim ledger,
    booked against the named paid office-visit claim: the entry gets a new adjustment claim number, copies
    the named claim's membership, service date, copay category, billing provider and cost-sharing period,
    carries the given amount as a negative member cost share, is marked adjusted with reason none, and is
    dated today. The member sees the returned copays as a credit on the next explanation of benefits. The
    call succeeds when the receipt returns the new adjustment claim number.

    Args:
        related_claim_number: Verbatim class — the claim number of the paid office-visit claim the adjustment entry is booked against, copied exactly as it appears in the claim history, character for character, with no change to letters, digits or hyphens (verbatim).
        reversal_amount: Fixed-format class — the copay amount returned to the member in USD as a positive number with 2 decimal places, rounded half up to the cent; it is booked as the negative of this amount.

    Returns:
        A confirmation string of the form "Office-visit adjustment <adjustment_claim_number> (entry <adjustment_entry_id>) booked against claim <related_claim_number> on membership <membership_id>: copays reduced by <reversal_amount> USD, dated <YYYY-MM-DD>." where adjustment_claim_number is the new adjustment claim number (text starting "ADJ-"), adjustment_entry_id is the ledger entry reference (text starting "ovr_"), membership_id is the membership of the named claim, and reversal_amount has 2 decimals. A returned adjustment claim number means the adjustment is booked.
    """
    found = ctx.find("plan_claims", claim_number=related_claim_number, event_type="plan_claim_booked")
    original = found[0] if found else {}
    amount = round(float(reversal_amount), 2)
    rid = ctx.make_id("ovr_", related_claim_number, amount)
    number = "ADJ-" + ctx.make_id("", "ovr_", related_claim_number, amount, length=8).upper()
    ctx.create("plan_claims", rid, plan_claim_id=rid, membership_id=original.get("membership_id", ""),
               customer_id=original.get("customer_id", ""), event_type="plan_claim_adjusted", claim_number=number,
               related_claim_number=related_claim_number, service_date=original.get("service_date", ""),
               service_category=original.get("service_category", "not_applicable"),
               provider_npi=original.get("provider_npi", ""), billed_amount=0.0, plan_paid_amount=0.0,
               member_cost_share=round(-amount, 2), adjudication_status="adjusted", denial_code="none",
               cost_share_period=original.get("cost_share_period", ""), booked_date=ctx.now()[:10])
    return (f"Office-visit adjustment {number} (entry {rid}) booked against claim {related_claim_number} on "
            f"membership {original.get('membership_id', '')}: copays reduced by {amount:.2f} USD, dated "
            f"{ctx.now()[:10]}.")


@tool(owner="agent", rw="write")
def book_therapy_course_rerating_7ffa3e71(ctx: ToolContext, related_claim_number: str, reversal_amount: float) -> str:
    """Book the course re-rating adjustment for the outpatient therapy visits of a member's approved
    rehabilitation therapy course. One call adds one adjustment entry to the member's claim ledger,
    booked against the named paid therapy-visit claim: the entry gets a new adjustment claim number, copies
    the named claim's membership, service date, copay category, billing provider and cost-sharing period,
    carries the given amount as a negative member cost share, is marked adjusted with reason none, and is
    dated today. The member sees the returned copays as a credit on the next explanation of benefits. The
    call succeeds when the receipt returns the new adjustment claim number.

    Args:
        related_claim_number: Verbatim class — the claim number of the paid therapy-visit claim the adjustment entry is booked against, copied exactly as it appears in the claim history, character for character, with no change to letters, digits or hyphens (verbatim).
        reversal_amount: Fixed-format class — the copay amount returned to the member in USD as a positive number with 2 decimal places, rounded half up to the cent; it is booked as the negative of this amount.

    Returns:
        A confirmation string of the form "Therapy course adjustment <adjustment_claim_number> (entry <adjustment_entry_id>) booked against claim <related_claim_number> on membership <membership_id>: copays reduced by <reversal_amount> USD, dated <YYYY-MM-DD>." where adjustment_claim_number is the new adjustment claim number (text starting "ADJ-"), adjustment_entry_id is the ledger entry reference (text starting "tcr_"), membership_id is the membership of the named claim, and reversal_amount has 2 decimals. A returned adjustment claim number means the adjustment is booked.
    """
    found = ctx.find("plan_claims", claim_number=related_claim_number, event_type="plan_claim_booked")
    original = found[0] if found else {}
    amount = round(float(reversal_amount), 2)
    rid = ctx.make_id("tcr_", related_claim_number, amount)
    number = "ADJ-" + ctx.make_id("", "tcr_", related_claim_number, amount, length=8).upper()
    ctx.create("plan_claims", rid, plan_claim_id=rid, membership_id=original.get("membership_id", ""),
               customer_id=original.get("customer_id", ""), event_type="plan_claim_adjusted", claim_number=number,
               related_claim_number=related_claim_number, service_date=original.get("service_date", ""),
               service_category=original.get("service_category", "not_applicable"),
               provider_npi=original.get("provider_npi", ""), billed_amount=0.0, plan_paid_amount=0.0,
               member_cost_share=round(-amount, 2), adjudication_status="adjusted", denial_code="none",
               cost_share_period=original.get("cost_share_period", ""), booked_date=ctx.now()[:10])
    return (f"Therapy course adjustment {number} (entry {rid}) booked against claim {related_claim_number} on "
            f"membership {original.get('membership_id', '')}: copays reduced by {amount:.2f} USD, dated "
            f"{ctx.now()[:10]}.")


@tool(owner="agent", rw="write")
def book_ambulance_transport_rerating_8b982fa6(ctx: ToolContext, related_claim_number: str, reversal_amount: float) -> str:
    """Book the transport re-rating adjustment for the ambulance claims of a member who depends on scheduled
    wheelchair or stretcher transport. One call adds one adjustment entry to the member's claim ledger,
    booked against the named paid ambulance claim: the entry gets a new adjustment claim number, copies
    the named claim's membership, service date, copay category, billing provider and cost-sharing period,
    carries the given amount as a negative member cost share, is marked adjusted with reason none, and is
    dated today. The member sees the returned copays as a credit on the next explanation of benefits. The
    call succeeds when the receipt returns the new adjustment claim number.

    Args:
        related_claim_number: Verbatim class — the claim number of the paid ambulance claim the adjustment entry is booked against, copied exactly as it appears in the claim history, character for character, with no change to letters, digits or hyphens (verbatim).
        reversal_amount: Fixed-format class — the copay amount returned to the member in USD as a positive number with 2 decimal places, rounded half up to the cent; it is booked as the negative of this amount.

    Returns:
        A confirmation string of the form "Ambulance adjustment <adjustment_claim_number> (entry <adjustment_entry_id>) booked against claim <related_claim_number> on membership <membership_id>: copays reduced by <reversal_amount> USD, dated <YYYY-MM-DD>." where adjustment_claim_number is the new adjustment claim number (text starting "ADJ-"), adjustment_entry_id is the ledger entry reference (text starting "atr_"), membership_id is the membership of the named claim, and reversal_amount has 2 decimals. A returned adjustment claim number means the adjustment is booked.
    """
    found = ctx.find("plan_claims", claim_number=related_claim_number, event_type="plan_claim_booked")
    original = found[0] if found else {}
    amount = round(float(reversal_amount), 2)
    rid = ctx.make_id("atr_", related_claim_number, amount)
    number = "ADJ-" + ctx.make_id("", "atr_", related_claim_number, amount, length=8).upper()
    ctx.create("plan_claims", rid, plan_claim_id=rid, membership_id=original.get("membership_id", ""),
               customer_id=original.get("customer_id", ""), event_type="plan_claim_adjusted", claim_number=number,
               related_claim_number=related_claim_number, service_date=original.get("service_date", ""),
               service_category=original.get("service_category", "not_applicable"),
               provider_npi=original.get("provider_npi", ""), billed_amount=0.0, plan_paid_amount=0.0,
               member_cost_share=round(-amount, 2), adjudication_status="adjusted", denial_code="none",
               cost_share_period=original.get("cost_share_period", ""), booked_date=ctx.now()[:10])
    return (f"Ambulance adjustment {number} (entry {rid}) booked against claim {related_claim_number} on "
            f"membership {original.get('membership_id', '')}: copays reduced by {amount:.2f} USD, dated "
            f"{ctx.now()[:10]}.")


@tool(owner="user", rw="write")
def pay_lockout_premium_balance_44198c5a(ctx: ToolContext, membership_id: str, coverage_month: str,
                                         payment_amount: float, payment_method: str) -> str:
    """Make the family's own lockout balance payment on a CHIP membership that ended for unpaid premiums,
    so the child can be re-enrolled while the lockout runs. One call posts one payment entry against the
    given coverage month with the given amount and payment method, dated today, and settles the ended
    membership's premium account: every billed month counts as settled and the premium balance shown on the
    membership becomes zero, whatever amount was paid. The family receives a payment confirmation number at
    once. The call succeeds when the receipt returns the confirmation number.

    Args:
        membership_id: Id class — the membership reference number of the ended CHIP membership whose lockout balance is being paid, as returned by the membership lookup and read out by the representative.
        coverage_month: Fixed-format class — the coverage month the payment entry is posted against, in YYYY-MM format (for example 2026-04), exactly as the month is labelled on the premium account.
        payment_amount: Fixed-format class — the amount paid in USD as a positive number with 2 decimal places, rounded half up to the cent.
        payment_method: Enum class — how the family pays; exactly one of: online_portal when paying through the member portal website; phone_ivr when paying by card or bank draft over the phone payment line; mail_check when the payment is a mailed personal check; money_order when the payment is a mailed money order; not_applicable when no payment method applies, which is never the case for a payment the family makes.

    Returns:
        A confirmation string of the form "Lockout payment <payment_entry_id> posted: <payment_amount> USD against coverage month <coverage_month> on membership <membership_id> by <payment_method>; confirmation number <payment_reference>; premium balance now 0.00 USD, every billed month settled." where payment_entry_id is the new premium ledger entry reference (text starting "lkp_"), payment_reference is the confirmation number (text starting "PRL-"), and payment_amount has 2 decimals. A returned confirmation number means the lockout balance is paid.
    """
    amount = round(float(payment_amount), 2)
    rows = ctx.find("plan_memberships", membership_id=membership_id)
    customer_id = rows[0].get("customer_id") if rows else ""
    pid = ctx.make_id("lkp_", membership_id, coverage_month, amount, payment_method)
    reference = "PRL-" + ctx.make_id("", membership_id, coverage_month, amount, length=7).upper()
    ctx.create("plan_premiums", pid, plan_premium_id=pid, membership_id=membership_id, customer_id=customer_id,
               event_type="plan_premium_paid", coverage_month=coverage_month, amount=amount,
               payment_method=payment_method, payment_reference=reference, waiver_reason="not_applicable",
               posted_date=ctx.now()[:10])
    if rows:
        ctx.update("plan_memberships", membership_id, premium_balance=0.0)
    return (f"Lockout payment {pid} posted: {amount:.2f} USD against coverage month {coverage_month} on membership "
            f"{membership_id} by {payment_method}; confirmation number {reference}; premium balance now 0.00 USD, "
            f"every billed month settled.")

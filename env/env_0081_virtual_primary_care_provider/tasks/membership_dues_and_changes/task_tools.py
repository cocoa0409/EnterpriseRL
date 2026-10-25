"""Hidden task tools of the membership_dues_and_changes difficulty (Larkspur Health, env_0081).

Each tool performs one atomic membership write with the values the agent has worked out; no tool
judges eligibility, prerequisites or amounts.
"""

from decimal import Decimal, ROUND_HALF_UP

from erlbench import ToolContext, tool


class _Cents:
    """Exact half-up rounding to the cent for every money value a tool books."""

    @staticmethod
    def half_up(value) -> float:
        return float(Decimal(str(value)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP))


@tool(owner="agent", rw="write")
def correct_superseded_tier_billing_563ffb83(ctx: ToolContext, membership_id: str, mem_charge_id: str,
                                             mem_request_id: str, new_variant_name: str,
                                             refund_amount: float) -> str:
    """Correct a Larkspur Membership dues line that was billed at a tier the membership should no longer hold.
    The support agent moves the membership to the tier named by the overdue change request, marks that change
    request as applied, and, when the stated refund is above 0.00, books one billing-error refund of that amount
    back to the original card, linked to the dues line being corrected and carrying that line's billing period and
    tier. When the stated refund is 0.00 no refund is booked and only the tier and the change request are updated.
    Afterwards the membership shows the new tier, the change request shows as applied, and the refund (if any)
    appears among the membership's billing lines as a negative amount.

    Args:
        membership_id: Id class — the membership reference number of the patient's Larkspur Membership, as returned by the membership lookup.
        mem_charge_id: Id class — the reference number of the dues billing line being corrected, as returned by the membership billing-line lookup.
        mem_request_id: Id class — the reference number of the overdue tier change request being applied, as returned by the membership change-request lookup.
        new_variant_name: Enum class — the tier the membership moves to, exactly one of: "Larkspur Access" when the change request names Larkspur Access; "Larkspur Essentials Monthly" when it names Larkspur Essentials Monthly; "Larkspur Essentials Annual" when it names Larkspur Essentials Annual; "Larkspur Plus Monthly" when it names Larkspur Plus Monthly; "Larkspur Plus Annual" when it names Larkspur Plus Annual; "Larkspur Premier Annual" when it names Larkspur Premier Annual.
        refund_amount: Fixed-format class — the billing-error refund returned to the original card, in USD as a non-negative number with at most 2 decimal places, rounded half up to the cent; 0.00 means no refund is booked.

    Returns:
        A confirmation string naming the membership reference number, the tier now held, the change request
        reference number now marked applied, and either the new refund line reference number with the refunded
        amount in USD (2 decimals) or the statement that no refund was booked. A string beginning "Error:" means
        nothing was changed because the membership was not found.
    """
    holding = ctx.find("membership_holdings", membership_id=membership_id)
    if not holding:
        return f"Error: no membership {membership_id}."
    original = ctx.find("membership_charges", mem_charge_id=mem_charge_id)
    amount = _Cents.half_up(refund_amount)
    ctx.update("membership_holdings", membership_id, variant_name=new_variant_name)
    ctx.update("membership_requests", mem_request_id, request_status="applied")
    if amount > 0:
        src = original[0] if original else {}
        rid = ctx.make_id("mch_", membership_id, mem_charge_id, mem_request_id, new_variant_name, amount)
        ctx.create("membership_charges", rid, mem_charge_id=rid, membership_id=membership_id,
                   customer_id=holding[0].get("customer_id"), event_type="membership_dues_refunded",
                   amount=-amount, charge_date=ctx.now()[:10], period_start=src.get("period_start"),
                   period_end=src.get("period_end"), tier_charged=src.get("tier_charged"), attempt_number=1,
                   original_charge_id=mem_charge_id, refund_reason="billing_error")
        return (f"Membership {membership_id} now on {new_variant_name}; change request {mem_request_id} applied; "
                f"billing-error refund {rid} of {amount:.2f} USD booked against line {mem_charge_id}.")
    return (f"Membership {membership_id} now on {new_variant_name}; change request {mem_request_id} applied; "
            "no refund booked.")


@tool(owner="user", rw="write")
def settle_membership_cancellation_8920d9b4(ctx: ToolContext, membership_id: str, mem_charge_id: str,
                                            refund_reason: str, refund_amount: float) -> str:
    """The patient personally ends their own Larkspur Membership and settles it. The call registers the patient's
    cancellation request as applied with today's date as both the request date and the effective date, closes the
    membership as cancelled today, and, when the stated refund is above 0.00, books one cancellation refund of that
    amount back to the original card, linked to the billing line it refunds and carrying that line's billing period,
    tier and the stated refund basis. When the stated refund is 0.00 no refund is booked. Afterwards the membership
    shows as cancelled with today's cancellation date and the refund (if any) appears among its billing lines as a
    negative amount.

    Args:
        membership_id: Id class — the membership reference number of the patient's Larkspur Membership, as returned by the membership lookup.
        mem_charge_id: Id class — the reference number of the billing line the refund is paid against, as returned by the membership billing-line lookup.
        refund_reason: Enum class — the refund basis, exactly one of: "full_refund_window" when the first paid period is refunded inside its full refund window; "renewal_refund_window" when a renewal charge is refunded inside its renewal refund window; "unused_months" when whole unused months are refunded; "sponsor_overlap" when the refund covers the days from the start of an active Larkspur at Work enrollment; "billing_error" when the refunded amount corrects an overcharge on the line rather than settling the cancellation; "none" when no refund basis applies and the stated refund is 0.00.
        refund_amount: Fixed-format class — the cancellation refund returned to the original card, in USD as a non-negative number with at most 2 decimal places, rounded half up to the cent; 0.00 means no refund is booked.

    Returns:
        A confirmation string naming the membership reference number, the cancellation request reference number,
        the cancellation date (YYYY-MM-DD), and either the new refund line reference number with the refunded amount
        in USD (2 decimals) and its basis or the statement that no refund was booked. A string beginning "Error:"
        means nothing was changed because the membership was not found.
    """
    holding = ctx.find("membership_holdings", membership_id=membership_id)
    if not holding:
        return f"Error: no membership {membership_id}."
    today = ctx.now()[:10]
    amount = _Cents.half_up(refund_amount)
    cust = holding[0].get("customer_id")
    req = ctx.make_id("mrq_", membership_id, "cancel", today)
    ctx.create("membership_requests", req, mem_request_id=req, customer_id=cust, membership_id=membership_id,
               request_type="cancel", requested_date=today, effective_date=today, target_variant_name="",
               pause_months=0, request_status="applied", created_at=ctx.now())
    ctx.update("membership_holdings", membership_id, status="cancelled", cancelled_date=today)
    if amount > 0:
        original = ctx.find("membership_charges", mem_charge_id=mem_charge_id)
        src = original[0] if original else {}
        rid = ctx.make_id("mch_", membership_id, mem_charge_id, refund_reason, amount)
        ctx.create("membership_charges", rid, mem_charge_id=rid, membership_id=membership_id, customer_id=cust,
                   event_type="membership_dues_refunded", amount=-amount, charge_date=today,
                   period_start=src.get("period_start"), period_end=src.get("period_end"),
                   tier_charged=src.get("tier_charged"), attempt_number=1, original_charge_id=mem_charge_id,
                   refund_reason=refund_reason)
        return (f"Membership {membership_id} cancelled on {today} (request {req}); refund {rid} of {amount:.2f} USD "
                f"booked against line {mem_charge_id} as {refund_reason}.")
    return f"Membership {membership_id} cancelled on {today} (request {req}); no refund booked."


class _Dates:
    """Calendar-month arithmetic on YYYY-MM-DD strings (month-end fallback), pure Python."""

    @staticmethod
    def add_months(day: str, months: int) -> str:
        y, m, d = int(day[0:4]), int(day[5:7]), int(day[8:10])
        total = (y * 12 + (m - 1)) + months
        ny, nm = total // 12, total % 12 + 1
        lengths = [31, 29 if (ny % 4 == 0 and (ny % 100 != 0 or ny % 400 == 0)) else 28, 31, 30, 31, 30,
                   31, 31, 30, 31, 30, 31]
        return f"{ny:04d}-{nm:02d}-{min(d, lengths[nm - 1]):02d}"


@tool(owner="agent", rw="write")
def issue_goodwill_credit_9ab1aff0(ctx: ToolContext, membership_id: str, related_visit_id: str,
                                   credit_amount: float) -> str:
    """Add a goodwill account credit to a Larkspur Membership to compensate one visit that Larkspur cancelled. When
    the stated amount is above 0.00 the support agent books one goodwill credit line dated today that names the
    cancelled visit, expires twelve calendar months later, and raises the membership's account credit balance by that
    amount; the credit is non-cash value usable only toward membership dues and upgrade charges. When the stated
    amount is 0.00 nothing is booked.

    Args:
        membership_id: Id class — the membership reference number of the patient's Larkspur Membership, as returned by the membership lookup.
        related_visit_id: Id class — the reference number of the visit appointment Larkspur cancelled that the credit compensates, as returned by the visit appointment lookup.
        credit_amount: Fixed-format class — the goodwill credit granted, in USD as a non-negative number with at most 2 decimal places, rounded half up to the cent; 0.00 means nothing is booked.

    Returns:
        A confirmation string naming the new credit line reference number, the amount in USD (2 decimals), the visit
        it compensates and the expiry date (YYYY-MM-DD), or the statement that nothing was booked. A string beginning
        "Error:" means nothing was changed because the membership was not found.
    """
    amount = _Cents.half_up(credit_amount)
    holding = ctx.find("membership_holdings", membership_id=membership_id)
    if not holding:
        return f"Error: no membership {membership_id}."
    if amount <= 0:
        return f"No goodwill credit booked for membership {membership_id}."
    today = ctx.now()[:10]
    exp = _Dates.add_months(today, 12)
    rid = ctx.make_id("mcr_", membership_id, "goodwill", related_visit_id, amount)
    ctx.create("membership_credits", rid, mem_credit_id=rid, membership_id=membership_id,
               customer_id=holding[0].get("customer_id"), event_type="membership_credit_issued", amount=amount,
               credit_date=today, credit_reason="goodwill", source_credit_id=None, applied_charge_id=None,
               referred_customer_id=None,
               related_visit_id=related_visit_id, expiry_date=exp)
    ctx.update("membership_holdings", membership_id,
               credit_balance=_Cents.half_up(float(holding[0].get("credit_balance") or 0) + amount))
    return (f"Goodwill credit {rid} of {amount:.2f} USD booked on membership {membership_id} for visit "
            f"{related_visit_id}; expires {exp}.")


@tool(owner="agent", rw="write")
def issue_referral_credit_f4907f54(ctx: ToolContext, membership_id: str, referred_customer_id: str,
                                   credit_amount: float) -> str:
    """Add a referral account credit to the referring member's Larkspur Membership for one referred patient whose
    membership names that member as referrer. When the stated amount is above 0.00 the support agent books one
    referral credit line dated today that names the referred patient, expires twelve calendar months later, and raises
    the membership's account credit balance by that amount; the credit is non-cash value usable only toward membership
    dues and upgrade charges. When the stated amount is 0.00 nothing is booked.

    Args:
        membership_id: Id class — the membership reference number of the referring member's Larkspur Membership, as returned by the membership lookup.
        referred_customer_id: Id class — the patient reference number of the referred patient, as shown in the referring-patient field of that patient's membership returned by the membership lookup.
        credit_amount: Fixed-format class — the referral credit granted, in USD as a non-negative number with at most 2 decimal places, rounded half up to the cent; 0.00 means nothing is booked.

    Returns:
        A confirmation string naming the new credit line reference number, the amount in USD (2 decimals), the
        referred patient and the expiry date (YYYY-MM-DD), or the statement that nothing was booked. A string beginning
        "Error:" means nothing was changed because the membership was not found.
    """
    amount = _Cents.half_up(credit_amount)
    holding = ctx.find("membership_holdings", membership_id=membership_id)
    if not holding:
        return f"Error: no membership {membership_id}."
    if amount <= 0:
        return f"No referral credit booked for membership {membership_id}."
    today = ctx.now()[:10]
    exp = _Dates.add_months(today, 12)
    rid = ctx.make_id("mcr_", membership_id, "referral", referred_customer_id, amount)
    ctx.create("membership_credits", rid, mem_credit_id=rid, membership_id=membership_id,
               customer_id=holding[0].get("customer_id"), event_type="membership_credit_issued", amount=amount,
               credit_date=today, credit_reason="referral", source_credit_id=None, applied_charge_id=None,
               referred_customer_id=referred_customer_id,
               related_visit_id=None, expiry_date=exp)
    ctx.update("membership_holdings", membership_id,
               credit_balance=_Cents.half_up(float(holding[0].get("credit_balance") or 0) + amount))
    return (f"Referral credit {rid} of {amount:.2f} USD booked on membership {membership_id} for referred patient "
            f"{referred_customer_id}; expires {exp}.")


@tool(owner="user", rw="write")
def pay_past_due_dues_3656db9c(ctx: ToolContext, membership_id: str, period_start: str, dues_amount: float,
                               card_amount: float) -> str:
    """The patient personally pays the unpaid dues of a past-due Larkspur Membership with a payment card the patient
    provides. The payment books the period's single dues line at the stated gross dues, draws the membership's open
    account credit against that line for the difference between the gross dues and the card amount (each credit drawn
    gets its own applied line, credits with the earliest expiry date drawn ahead of later ones), charges the stated
    card amount to the patient's card, and returns the membership to active for the same billing period. Afterwards
    the membership shows as active, the dues line appears among its billing lines and the account credit balance falls
    by the credit drawn.

    Args:
        membership_id: Id class — the membership reference number of the patient's Larkspur Membership, as returned by the membership lookup.
        period_start: Fixed-format class — the first day of the unpaid billing period, format YYYY-MM-DD, exactly as the current period start shown on the membership record.
        dues_amount: Fixed-format class — the gross dues of the unpaid billing period, in USD with 2 decimal places, as shown on the declined payment attempts of that period.
        card_amount: Fixed-format class — the amount charged to the patient's card, in USD as a non-negative number with at most 2 decimal places, rounded half up to the cent.

    Returns:
        A confirmation string naming the new dues line reference number, the gross dues and the card amount in USD
        (2 decimals), the total account credit drawn in USD (2 decimals) and the membership status now shown (active).
        A string beginning "Error:" means nothing was changed because the membership was not found.
    """
    holding = ctx.find("membership_holdings", membership_id=membership_id)
    if not holding:
        return f"Error: no membership {membership_id}."
    h = holding[0]
    today = ctx.now()[:10]
    gross = _Cents.half_up(dues_amount)
    card = _Cents.half_up(card_amount)
    lid = ctx.make_id("mch_", membership_id, period_start, gross, card)
    ctx.create("membership_charges", lid, mem_charge_id=lid, membership_id=membership_id,
               customer_id=h.get("customer_id"), event_type="membership_dues_charged", amount=gross,
               charge_date=today, period_start=period_start, period_end=h.get("current_period_end"),
               tier_charged=h.get("variant_name"), attempt_number=1, original_charge_id=None, refund_reason="none")
    left = _Cents.half_up(max(0.0, gross - card))
    lines = ctx.find("membership_credits", membership_id=membership_id)
    issued = sorted([r for r in lines if r.get("event_type") == "membership_credit_issued"],
                    key=lambda r: (str(r.get("expiry_date")), str(r.get("credit_date")), str(r.get("mem_credit_id"))))
    drawn_total = 0.0
    for cr in issued:
        if left <= 0:
            break
        used = sum(float(r.get("amount") or 0) for r in lines
                   if r.get("source_credit_id") == cr.get("mem_credit_id")
                   and r.get("event_type") in ("membership_credit_applied", "membership_credit_expired"))
        remaining = _Cents.half_up(float(cr.get("amount") or 0) - used)
        if remaining <= 0:
            continue
        take = _Cents.half_up(min(remaining, left))
        aid = ctx.make_id("mca_", cr.get("mem_credit_id"), lid, take)
        ctx.create("membership_credits", aid, mem_credit_id=aid, membership_id=membership_id,
                   customer_id=h.get("customer_id"), event_type="membership_credit_applied", amount=take,
                   credit_date=today, credit_reason=cr.get("credit_reason"), source_credit_id=cr.get("mem_credit_id"),
                   applied_charge_id=lid, referred_customer_id=None, related_visit_id=None,
                   expiry_date=cr.get("expiry_date"))
        left = _Cents.half_up(left - take)
        drawn_total = _Cents.half_up(drawn_total + take)
    ctx.update("membership_holdings", membership_id, status="active",
               credit_balance=_Cents.half_up(max(0.0, float(h.get("credit_balance") or 0) - drawn_total)))
    return (f"Dues line {lid} of {gross:.2f} USD booked for the period starting {period_start}; account credit drawn "
            f"{drawn_total:.2f} USD; card charged {card:.2f} USD; membership {membership_id} is active.")


_CYCLE_MONTHS = {"Larkspur Access": 1, "Larkspur Essentials Monthly": 1, "Larkspur Essentials Annual": 12,
                 "Larkspur Plus Monthly": 1, "Larkspur Plus Annual": 12, "Larkspur Premier Annual": 12}


@tool(owner="agent", rw="write")
def apply_tier_upgrade_8d7c34c0(ctx: ToolContext, membership_id: str, new_variant_name: str,
                                proration_amount: float) -> str:
    """Move an active Larkspur Membership up to a higher tier at once and book the upgrade charge. The support agent
    records the patient's upgrade request as applied today, moves the membership to the new tier with a new billing
    period that starts today and runs one billing cycle of the new tier, and books one upgrade proration line of the
    stated amount on the card on file for that new period. Afterwards the membership shows the new tier and the new
    period dates, and the upgrade charge appears among its billing lines.

    Args:
        membership_id: Id class — the membership reference number of the patient's Larkspur Membership, as returned by the membership lookup.
        new_variant_name: Enum class — the tier the patient is upgrading to, exactly one of: "Larkspur Access" when the patient chose Larkspur Access; "Larkspur Essentials Monthly" when the patient chose Larkspur Essentials Monthly; "Larkspur Essentials Annual" when the patient chose Larkspur Essentials Annual; "Larkspur Plus Monthly" when the patient chose Larkspur Plus Monthly; "Larkspur Plus Annual" when the patient chose Larkspur Plus Annual; "Larkspur Premier Annual" when the patient chose Larkspur Premier Annual.
        proration_amount: Fixed-format class — the upgrade charge for the new period, in USD as a non-negative number with at most 2 decimal places, rounded half up to the cent.

    Returns:
        A confirmation string naming the upgrade request reference number, the tier now held, the new period start and
        end dates (YYYY-MM-DD) and the upgrade charge line reference number with its amount in USD (2 decimals). A
        string beginning "Error:" means nothing was changed because the membership was not found.
    """
    holding = ctx.find("membership_holdings", membership_id=membership_id)
    if not holding:
        return f"Error: no membership {membership_id}."
    h = holding[0]
    today = ctx.now()[:10]
    amount = _Cents.half_up(proration_amount)
    end = _Dates.add_months(today, _CYCLE_MONTHS.get(new_variant_name, 12))
    req = ctx.make_id("mrq_", membership_id, "upgrade", new_variant_name, today)
    ctx.create("membership_requests", req, mem_request_id=req, customer_id=h.get("customer_id"),
               membership_id=membership_id, request_type="upgrade", requested_date=today, effective_date=today,
               target_variant_name=new_variant_name, pause_months=0, request_status="applied", created_at=ctx.now())
    ctx.update("membership_holdings", membership_id, variant_name=new_variant_name, current_period_start=today,
               current_period_end=end)
    lid = ctx.make_id("mch_", membership_id, new_variant_name, today, amount)
    ctx.create("membership_charges", lid, mem_charge_id=lid, membership_id=membership_id,
               customer_id=h.get("customer_id"), event_type="membership_upgrade_proration_charged", amount=amount,
               charge_date=today, period_start=today, period_end=end, tier_charged=new_variant_name,
               attempt_number=1, original_charge_id=None, refund_reason="none")
    return (f"Upgrade request {req} applied: membership {membership_id} is now {new_variant_name} for {today} to "
            f"{end}; upgrade charge {lid} of {amount:.2f} USD booked.")

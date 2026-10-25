"""Hidden task tools for business_allocation_changes_and_trueups (Small Business Community Solar Subscriptions).

Each tool performs one atomic write with the values the agent has worked out from the published rules and the
records; no tool aggregates history, judges eligibility or refuses on a business condition.
"""

from erlbench import ToolContext, tool


class _Money:
    """Pure-Python half-up rounding of non-negative amounts (no float banker's rounding)."""

    @staticmethod
    def half_up(value, places):
        scale = 10 ** places
        scaled = abs(float(value)) * scale
        whole = int(scaled)
        if scaled - whole >= 0.5 - 1e-9:
            whole += 1
        out = whole / scale
        return -out if float(value) < 0 else out


@tool(owner="agent", rw="write")
def complete_guarantee_trueup_bd5f1ac2(ctx: ToolContext, biz_sub_id: str, contract_year: int,
                                       period_start_month: str, period_end_month: str, credited_kwh_12m: int,
                                       usage_kwh_12m: int, guaranteed_kwh: int, shortfall_kwh: int,
                                       avg_credit_rate: float, resize_kw: float, outcome: str,
                                       guarantee_credit: float) -> str:
    """Record Meadowlark's completed annual true-up of one contract year of a Small Business Community Solar
    subscription. One call writes the true-up record of that contract year, dated today, with the figures
    supplied; when the guarantee credit supplied is above 0.00 it also posts that amount on the subscription's
    billing ledger as a billing credit for the production guarantee, dated today, which lowers the balance the
    subscriber owes. A guarantee credit of 0.00 posts no billing credit. The kW figure supplied is recorded on
    the true-up only; any allocation removal it calls for is filed separately in the allocation schedule. The
    subscriber can see the completed true-up and, when one was posted, the guarantee credit on their next
    statement.

    Args:
        biz_sub_id: Id class — the reference number of the Small Business Community Solar subscription whose
            contract year is closed, as returned by the subscription lookup.
        contract_year: Fixed-format class — the number of the contract year the true-up closes, an integer, 1 or
            more (year 1 ends on the first anniversary of the activation date).
        period_start_month: Fixed-format class — the first utility statement month covered by the true-up,
            written YYYY-MM.
        period_end_month: Fixed-format class — the last utility statement month covered by the true-up, written
            YYYY-MM; the guarantee billing credit is booked to this month.
        credited_kwh_12m: Fixed-format class — the net kWh credited over the period (postings less reversals), in
            kWh, whole number, 0 or more; an integer.
        usage_kwh_12m: Fixed-format class — the utility-reported consumption of the subscription's utility account
            over the same twelve months, in kWh, whole number; an integer.
        guaranteed_kwh: Fixed-format class — the kWh the plan's production guarantee assures for the contract
            year, in kWh, whole number, 0 or more; an integer, 0 on a plan without a guarantee.
        shortfall_kwh: Fixed-format class — the guaranteed kWh not met over the period, in kWh, whole number, 0 or
            more; an integer, 0 when there is no shortfall.
        avg_credit_rate: Fixed-format class — the net credit value of the period divided by its net credited kWh,
            in USD per kWh, 4 decimal places, rounded half up.
        resize_kw: Fixed-format class — the kW the true-up removes to right-size the share, in kW AC, 2 decimal
            places, 0.00 or more, rounded half up; 0.00 when no resize applies.
        outcome: Enum class — the result of the true-up, exactly one of: no_change when neither a guarantee credit
            nor a resize applies; resize_down when only a resize applies; guarantee_credit when only a guarantee
            credit is owed; resize_and_credit when both a resize and a guarantee credit apply.
        guarantee_credit: Fixed-format class — the production-guarantee credit owed by this true-up, in USD, 2
            decimal places, 0.00 or more, rounded half up; 0.00 when none is owed.

    Returns:
        A dictionary rendered as text with: status ("recorded" on success), biz_review_id (reference number of
        the true-up record written), contract_year (the contract year closed), guarantee_credit (the amount
        recorded, USD with 2 decimal places), billing_credit_id (reference number of the guarantee billing credit
        posted, or an empty string when the credit is 0.00) and review_date (today's date, YYYY-MM-DD).
    """
    credit = _Money.half_up(guarantee_credit, 2)
    rate = _Money.half_up(avg_credit_rate, 4)
    resize = _Money.half_up(resize_kw, 2)
    subs = ctx.find("biz_subscriptions", biz_sub_id=biz_sub_id)
    customer_id = subs[0].get("customer_id", "") if subs else ""
    billing_type = subs[0].get("billing_type", "") if subs else ""
    today = ctx.now()[:10]
    rid = ctx.make_id("brv_", biz_sub_id, contract_year, period_start_month, period_end_month, credited_kwh_12m,
                      usage_kwh_12m, guaranteed_kwh, shortfall_kwh, rate, resize, outcome, credit)
    ctx.create("biz_reviews", rid, biz_review_id=rid, biz_sub_id=biz_sub_id, customer_id=customer_id,
               event_type="biz_trueup_completed", contract_year=int(contract_year), review_date=today,
               period_start_month=period_start_month, period_end_month=period_end_month,
               credited_kwh_12m=int(credited_kwh_12m), usage_kwh_12m=int(usage_kwh_12m),
               guaranteed_kwh=int(guaranteed_kwh), shortfall_kwh=int(shortfall_kwh), avg_credit_rate=rate,
               guarantee_credit=credit, resize_kw=resize, outcome=outcome)
    credit_id = ""
    if credit > 0:
        credit_id = ctx.make_id("bbl_", rid, "production_guarantee", credit)
        ctx.create("biz_billing", credit_id, biz_bill_id=credit_id, biz_sub_id=biz_sub_id, customer_id=customer_id,
                   event_type="biz_billing_credited", amount=credit, bill_date=today,
                   billing_month=period_end_month, due_date="", biz_credit_id=None, biz_ref_bill_id=None,
                   charge_basis="not_applicable", billing_type=billing_type, payment_method="not_applicable",
                   credit_reason="production_guarantee")
    return str({"status": "recorded", "biz_review_id": rid, "contract_year": int(contract_year),
                "guarantee_credit": f"{credit:.2f}", "billing_credit_id": credit_id, "review_date": today})


@tool(owner="user", rw="write")
def accept_share_decrease_75e61509(ctx: ToolContext, biz_request_id: str, filing_month: str, effective_date: str,
                                   fee_due_date: str, excess_decrease_fee: float) -> str:
    """The subscriber accepts, in person, the decrease amendment for their own pending allocation-decrease
    request on a Small Business Community Solar subscription. One call records on that request the date the
    decrease takes effect and, when the excess-decrease fee supplied is above 0.00, bills that fee on the
    subscription's billing ledger, dated today, booked to the filing month supplied and due on the due date
    supplied, which raises the balance the subscriber owes. A fee of 0.00 bills nothing. The request itself stays
    open until Meadowlark files the decrease in the allocation schedule. The subscriber sees the accepted
    effective date and, when billed, the fee on their next statement.

    Args:
        biz_request_id: Id class — the reference number of the subscriber's pending allocation-decrease request
            being accepted, as returned by the request lookup.
        filing_month: Fixed-format class — the calendar month in which the decrease is submitted to the utility,
            written YYYY-MM.
        effective_date: Fixed-format class — the first day the utility applies the decrease, written YYYY-MM-DD.
        fee_due_date: Fixed-format class — the payment due date of the excess-decrease fee, written YYYY-MM-DD.
        excess_decrease_fee: Fixed-format class — the excess-decrease fee of the amendment, in USD, 2 decimal
            places, greater than 0.00 when billed, rounded half up; 0.00 when no fee applies.

    Returns:
        A dictionary rendered as text with: status ("accepted" on success), biz_request_id (the request
        accepted), effective_date (the effective date recorded, YYYY-MM-DD), fee_bill_id (reference number of
        the excess-decrease fee line billed, or an empty string when the fee is 0.00) and excess_decrease_fee
        (the fee billed, USD with 2 decimal places).
    """
    fee = _Money.half_up(excess_decrease_fee, 2)
    reqs = ctx.find("biz_requests", biz_request_id=biz_request_id)
    biz_sub_id = reqs[0].get("biz_sub_id", "") if reqs else ""
    customer_id = reqs[0].get("customer_id", "") if reqs else ""
    subs = ctx.find("biz_subscriptions", biz_sub_id=biz_sub_id) if biz_sub_id else []
    billing_type = subs[0].get("billing_type", "") if subs else ""
    ctx.update("biz_requests", biz_request_id, effective_date=effective_date)
    fee_id = ""
    if fee > 0:
        fee_id = ctx.make_id("bbl_", biz_request_id, filing_month, effective_date, fee_due_date, fee)
        ctx.create("biz_billing", fee_id, biz_bill_id=fee_id, biz_sub_id=biz_sub_id, customer_id=customer_id,
                   event_type="biz_change_fee_assessed", amount=fee, bill_date=ctx.now()[:10],
                   billing_month=filing_month, due_date=fee_due_date, biz_credit_id=None, biz_ref_bill_id=None,
                   charge_basis="not_applicable", billing_type=billing_type, payment_method="not_applicable",
                   credit_reason="not_applicable")
    return str({"status": "accepted", "biz_request_id": biz_request_id, "effective_date": effective_date,
                "fee_bill_id": fee_id, "excess_decrease_fee": f"{fee:.2f}"})


@tool(owner="agent", rw="write")
def bill_statement_estimate_b08e308f(ctx: ToolContext, biz_sub_id: str, billing_month: str, estimated_charge: float,
                                     due_date: str) -> str:
    """Bill Meadowlark's estimated subscription charge for one utility statement month of a Small Business Community
    Solar subscription whose bill credit the utility has not yet reported. One call writes one estimated charge on
    the subscription's billing ledger, invoiced today, for the statement month supplied, with no credit statement
    reference and the due date supplied; it raises the balance the subscriber owes and appears on the subscriber's
    next statement as an estimate. When the utility later reports that month's credit, the actual charge and the
    offset of this estimate are booked separately.

    Args:
        biz_sub_id: Id class — the reference number of the Small Business Community Solar subscription being billed,
            as returned by the subscription lookup.
        billing_month: Fixed-format class — the utility statement month the estimate stands in for, written YYYY-MM.
        estimated_charge: Fixed-format class — the estimated charge, in USD, 2 decimal places, greater than 0.00,
            rounded half up.
        due_date: Fixed-format class — the payment due date of the estimated charge, written YYYY-MM-DD.

    Returns:
        A dictionary rendered as text with: status ("billed" on success), biz_bill_id (reference number of the
        estimated charge written), billing_month (the statement month estimated, YYYY-MM), amount (the amount
        billed, USD with 2 decimal places), bill_date (today's date, YYYY-MM-DD) and due_date (YYYY-MM-DD).
    """
    amount = _Money.half_up(estimated_charge, 2)
    subs = ctx.find("biz_subscriptions", biz_sub_id=biz_sub_id)
    customer_id = subs[0].get("customer_id", "") if subs else ""
    billing_type = subs[0].get("billing_type", "") if subs else ""
    today = ctx.now()[:10]
    rid = ctx.make_id("bbl_", biz_sub_id, billing_month, amount, due_date)
    ctx.create("biz_billing", rid, biz_bill_id=rid, biz_sub_id=biz_sub_id, customer_id=customer_id,
               event_type="biz_charge_billed", amount=amount, bill_date=today, billing_month=billing_month,
               due_date=due_date, biz_credit_id=None, biz_ref_bill_id=None, charge_basis="estimated",
               billing_type=billing_type, payment_method="not_applicable", credit_reason="not_applicable")
    return str({"status": "billed", "biz_bill_id": rid, "billing_month": billing_month, "amount": f"{amount:.2f}",
                "bill_date": today, "due_date": due_date})


@tool(owner="user", rw="write")
def pay_increase_deposit_a318506d(ctx: ToolContext, biz_sub_id: str, payment_method: str,
                                  deposit_amount: float) -> str:
    """The business pays, in person through Meadowlark's secure payment portal or by mailed check, the security
    deposit its own pending allocation-increase request on a Small Business Community Solar subscription needs, on that subscription.
    One call records the deposit as received and held on that subscription, dated today, and raises the deposit
    held on the subscription by the amount paid; the deposit is not applied to monthly charges while the
    subscription is open. The business sees the deposit as held on its account.

    Args:
        biz_sub_id: Id class — the reference number of the Small Business Community Solar subscription whose
            pending allocation increase the deposit is paid for, as returned by the subscription lookup.
        payment_method: Enum class — how the business pays, exactly one of: ach when the business pays from its
            bank account through the secure payment portal; check when the business mails a check; card, which
            applies only to card payments of other balances and is never used for a security deposit;
            utility_remittance, which applies only to the utility's remittance under consolidated billing and is
            never used for a security deposit; not_applicable, which applies only to lines that are not payments
            and is never used for a security deposit.
        deposit_amount: Fixed-format class — the deposit paid, in USD, 2 decimal places, greater than 0.00, rounded
            half up.

    Returns:
        A dictionary rendered as text with: status ("held" on success), deposit_line_id (reference number of the
        deposit line recorded), amount (the deposit paid, USD with 2 decimal places), deposit_held_usd (the total
        deposit now held on the subscription, USD with 2 decimal places) and bill_date (today's date, YYYY-MM-DD).
    """
    amount = _Money.half_up(deposit_amount, 2)
    subs = ctx.find("biz_subscriptions", biz_sub_id=biz_sub_id)
    customer_id = subs[0].get("customer_id", "") if subs else ""
    billing_type = subs[0].get("billing_type", "") if subs else ""
    held = _Money.half_up(float(subs[0].get("deposit_held_usd") or 0) + amount, 2) if subs else amount
    today = ctx.now()[:10]
    rid = ctx.make_id("bbl_", biz_sub_id, payment_method, amount, today)
    ctx.create("biz_billing", rid, biz_bill_id=rid, biz_sub_id=biz_sub_id, customer_id=customer_id,
               event_type="biz_deposit_held", amount=amount, bill_date=today, billing_month=today[:7], due_date="",
               biz_credit_id=None, biz_ref_bill_id=None, charge_basis="not_applicable", billing_type=billing_type,
               payment_method=payment_method, credit_reason="not_applicable")
    if subs:
        ctx.update("biz_subscriptions", biz_sub_id, deposit_held_usd=held)
    return str({"status": "held", "deposit_line_id": rid, "amount": f"{amount:.2f}", "deposit_held_usd": f"{held:.2f}",
                "bill_date": today})

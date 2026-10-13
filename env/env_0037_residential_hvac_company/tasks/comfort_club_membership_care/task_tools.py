"""Hidden task tools for the comfort_club_membership_care difficulty of env_0037_residential_hvac_company.

Each tool performs one atomic Comfort Club business write with the values the agent has already
worked out from the published policy; none of them judges eligibility, aggregates history or
computes an amount. Reached only through unlock_* -> call_*.
"""

from erlbench import ToolContext, tool


@tool(owner="agent", rw="write")
def post_covered_repair_draw_a854dec6(ctx: ToolContext, agreement_id: str, ticket_id: str,
                                       source_line_id: str, draw_amount: float) -> str:
    """Post a Comfort Club covered-repair draw for one completed service call to a member's
    agreement. The draw is recorded once for the call, in the current term of the agreement,
    naming the call and the covered repair line with the lowest invoice position; the agreement's
    covered-repair benefit remaining for the term goes down by the drawn amount. The
    member's visit and coverage history shows the draw against that service call, and the
    agreement shows the reduced benefit remaining. Success is the receipt below with status
    posted.

    Args:
        agreement_id: Id class — reference number of the member's Comfort Club agreement, read from the agreement lookup.
        ticket_id: Id class — reference number of the completed service call whose repair the benefit pays, read from the service call lookup.
        source_line_id: Id class — reference number of the repair parts or repair labor line holding the lowest invoice position on that call, read from the invoice line lookup.
        draw_amount: Fixed-format class — covered-repair benefit drawn for the call, in USD, 2 decimal places, always positive, rounded to the cent by the caller.

    Returns:
        A dictionary rendered as text with: service_entry_id (reference number of the new draw
        entry), agreement_id (the agreement drawn on), ticket_id (the service call paid),
        term_start (YYYY-MM-DD, the term whose benefit was drawn), draw_amount (USD, 2 decimal
        places), repair_coverage_remaining (USD, 2 decimal places, the benefit left in the term
        once the draw is posted) and status (always "posted", meaning the draw is on the agreement).
    """
    agr = ctx.find("plan_agreements", agreement_id=agreement_id)
    agr = agr[0] if agr else {}
    amount = round(float(draw_amount), 2)
    term_start = agr.get("term_start", "")
    rid = ctx.make_id("pse_", agreement_id, ticket_id, source_line_id, amount)
    ctx.create("plan_service_entries", rid, service_entry_id=rid, agreement_id=agreement_id,
               customer_id=agr.get("customer_id", ""), event_type="plan_coverage_draw",
               entry_reason="covered_repair", term_start=term_start, equipment_id="", season="",
               visits=0, amount=amount, entry_date=ctx.now()[:10], ticket_id=ticket_id,
               source_line_id=source_line_id)
    remaining = round(float(agr.get("repair_coverage_remaining") or 0) - amount, 2)
    ctx.update("plan_agreements", agreement_id, repair_coverage_remaining=remaining)
    return str({"service_entry_id": rid, "agreement_id": agreement_id, "ticket_id": ticket_id,
                "term_start": term_start, "draw_amount": amount,
                "repair_coverage_remaining": remaining, "status": "posted"})


@tool(owner="user", rw="write")
def confirm_agreement_cancellation_08dfa488(ctx: ToolContext, agreement_id: str, plan_request_id: str,
                                            source_entry_id: str, proration_credit: float,
                                            cancellation_fee: float) -> str:
    """The member confirms, in person, their own pending request to cancel their Comfort Club
    agreement, accepting the cancellation credit they were quoted. The request becomes
    confirmed, the agreement becomes cancelled with today's date as its cancellation date, the
    quoted cancellation proration credit is posted to the dues balance naming the current term's
    dues charge it refunds, the cancellation fee given is billed as a cancellation fee charge (a
    fee of 0.00 posts no charge), and any maintenance visits and covered-repair benefit still
    available in the term are removed as closed. The member sees the agreement as cancelled and
    the credit on the dues history. Success is the receipt below with status cancelled.

    Args:
        agreement_id: Id class — reference number of the member's Comfort Club agreement being cancelled, as the agent reads it from the agreement lookup and gives it to the member.
        plan_request_id: Id class — reference number of the member's pending cancellation request, as the agent reads it from the change request lookup and gives it to the member.
        source_entry_id: Id class — reference number of the current term's dues charge the credit refunds, as the agent reads it from the dues history and gives it to the member.
        proration_credit: Fixed-format class — cancellation proration credit the member accepts, in USD, 2 decimal places, always positive or 0.00, rounded to the cent by the caller.
        cancellation_fee: Fixed-format class — cancellation fee the member accepts, in USD, 2 decimal places, 0.00 or positive, rounded to the cent by the caller.

    Returns:
        A dictionary rendered as text with: agreement_id (the agreement cancelled), plan_request_id
        (the request now confirmed), cancelled_date (YYYY-MM-DD, the date the cancellation took
        effect), credit_entry_id (reference number of the credit entry), proration_credit (USD, 2
        decimal places), fee_entry_id (reference number of the cancellation fee charge, empty when
        the fee is 0.00), dues_balance (USD, 2 decimal places, signed: positive means the member
        still owes, negative means Harbison owes the member) and status (always "cancelled").
    """
    agr = ctx.find("plan_agreements", agreement_id=agreement_id)
    agr = agr[0] if agr else {}
    today = ctx.now()[:10]
    credit = round(float(proration_credit), 2)
    cust = agr.get("customer_id", "")
    ctx.update("plan_change_requests", plan_request_id, request_status="confirmed")
    rid = ctx.make_id("pbe_", agreement_id, plan_request_id, source_entry_id, credit)
    ctx.create("plan_billing_entries", rid, billing_entry_id=rid, agreement_id=agreement_id,
               customer_id=cust, event_type="plan_dues_credit",
               line_type="cancellation_proration_credit", billing_period=today[:7], amount=credit,
               posted_date=today, payment_method="", payment_reference="",
               source_entry_id=source_entry_id, ticket_id="")
    fee = round(float(cancellation_fee), 2)
    fid = ""
    if fee > 0:
        fid = ctx.make_id("pbe_", agreement_id, plan_request_id, "cancellation_fee", fee)
        ctx.create("plan_billing_entries", fid, billing_entry_id=fid, agreement_id=agreement_id,
                   customer_id=cust, event_type="plan_dues_charge", line_type="cancellation_fee",
                   billing_period=today[:7], amount=fee, posted_date=today, payment_method="",
                   payment_reference="", source_entry_id="", ticket_id="")
    visits_left = int(agr.get("visits_remaining") or 0)
    if visits_left > 0:
        vid = ctx.make_id("pse_", agreement_id, "visit_closed", today)
        ctx.create("plan_service_entries", vid, service_entry_id=vid, agreement_id=agreement_id,
                   customer_id=cust, event_type="plan_visit_expiry", entry_reason="agreement_closed",
                   term_start=agr.get("term_start", ""), equipment_id="", season="",
                   visits=visits_left, amount=0.0, entry_date=today, ticket_id="", source_line_id="")
    cover_left = round(float(agr.get("repair_coverage_remaining") or 0), 2)
    if cover_left > 0:
        cid = ctx.make_id("pse_", agreement_id, "coverage_closed", today)
        ctx.create("plan_service_entries", cid, service_entry_id=cid, agreement_id=agreement_id,
                   customer_id=cust, event_type="plan_coverage_expiry", entry_reason="agreement_closed",
                   term_start=agr.get("term_start", ""), equipment_id="", season="",
                   visits=0, amount=cover_left, entry_date=today, ticket_id="", source_line_id="")
    balance = round(float(agr.get("dues_balance") or 0) - credit + fee, 2)
    ctx.update("plan_agreements", agreement_id, status="cancelled", cancelled_date=today,
               dues_balance=balance, visits_remaining=0, repair_coverage_remaining=0.0)
    return str({"agreement_id": agreement_id, "plan_request_id": plan_request_id,
                "cancelled_date": today, "credit_entry_id": rid, "proration_credit": credit,
                "fee_entry_id": fid, "dues_balance": balance, "status": "cancelled"})



@tool(owner="agent", rw="write")
def reinstate_lapsed_agreement_6e8e1b28(ctx: ToolContext, agreement_id: str, reinstatement_fee: float) -> str:
    """Reinstate a member's lapsed Comfort Club agreement. The agreement returns to active status
    with a new twelve-month term that starts the day after the lapsed term's last day, its count of
    consecutive terms rises by one, the new term receives the same maintenance-visit and
    covered-repair grants the lapsed term received at its start and for systems added during it,
    and the reinstatement fee given is posted to the dues balance as a reinstatement fee charge
    billed to the current month (a fee of 0.00 posts no charge). The locked rate on file and the
    dues of the new term are left as they are. The member sees the agreement active again with its
    new term dates and visits available. Success is the receipt below with status active.

    Args:
        agreement_id: Id class — reference number of the member's lapsed Comfort Club agreement, read from the agreement lookup.
        reinstatement_fee: Fixed-format class — reinstatement fee charged, in USD, 2 decimal places, 0.00 or positive, rounded to the cent by the caller.

    Returns:
        A dictionary rendered as text with: agreement_id (the agreement reinstated), term_start and
        term_end (YYYY-MM-DD, the new term), consecutive_terms (integer, the new count),
        visits_remaining (integer, visits granted for the new term), repair_coverage_remaining (USD,
        2 decimal places, covered-repair benefit granted for the new term),
        fee_entry_id (reference number of the reinstatement fee charge, empty when the fee is
        0.00), reinstatement_fee (USD, 2 decimal places), dues_balance (USD, 2 decimal places,
        signed) and status (always "active").
    """
    agr = ctx.find("plan_agreements", agreement_id=agreement_id)
    agr = agr[0] if agr else {}
    fee = round(float(reinstatement_fee), 2)
    def _month_len(year, month):
        if month == 2:
            return 29 if (year % 4 == 0 and (year % 100 != 0 or year % 400 == 0)) else 28
        return 30 if month in (4, 6, 9, 11) else 31

    ty, tm, td = (int(x) for x in str(agr.get("term_end") or ctx.now()[:10])[:10].split("-"))
    td += 1
    if td > _month_len(ty, tm):
        td, tm = 1, tm + 1
        if tm > 12:
            tm, ty = 1, ty + 1
    start = f"{ty:04d}-{tm:02d}-{td:02d}"
    ey, em = ty + 1, tm
    ed = min(td, _month_len(ey, em)) - 1
    if ed == 0:
        em -= 1
        if em == 0:
            em, ey = 12, ey - 1
        ed = _month_len(ey, em)
    end = f"{ey:04d}-{em:02d}-{ed:02d}"
    terms = int(agr.get("consecutive_terms") or 0) + 1
    rid = ""
    if fee > 0:
        rid = ctx.make_id("pbe_", agreement_id, "reinstatement_fee", start, fee)
        ctx.create("plan_billing_entries", rid, billing_entry_id=rid, agreement_id=agreement_id,
                   customer_id=agr.get("customer_id", ""), event_type="plan_dues_charge",
                   line_type="reinstatement_fee", billing_period=ctx.now()[:7], amount=fee,
                   posted_date=ctx.now()[:10], payment_method="", payment_reference="",
                   source_entry_id="", ticket_id="")
    old_start = str(agr.get("term_start") or "")
    visits, cover = 0, 0.0
    for g in ctx.find("plan_service_entries", agreement_id=agreement_id, term_start=old_start):
        if g.get("event_type") not in ("plan_visit_grant", "plan_coverage_grant"):
            continue
        if g.get("entry_reason") not in ("new_term", "renewal_term", "additional_system"):
            continue
        gid = ctx.make_id("pse_", agreement_id, "reinstated_grant", start, g.get("service_entry_id", ""))
        fields = dict(service_entry_id=gid, agreement_id=agreement_id, customer_id=agr.get("customer_id", ""),
                      event_type=g.get("event_type"), entry_reason="renewal_term", term_start=start,
                      season="", visits=int(g.get("visits") or 0), amount=round(float(g.get("amount") or 0), 2),
                      entry_date=ctx.now()[:10])
        if g.get("equipment_id"):
            fields["equipment_id"] = g.get("equipment_id")
        ctx.create("plan_service_entries", gid, **fields)
        visits += int(g.get("visits") or 0)
        cover += float(g.get("amount") or 0)
    balance = round(float(agr.get("dues_balance") or 0) + fee, 2)
    ctx.update("plan_agreements", agreement_id, status="active", term_start=start, term_end=end,
               consecutive_terms=terms, dues_balance=balance, visits_remaining=visits,
               repair_coverage_remaining=round(cover, 2))
    return str({"agreement_id": agreement_id, "term_start": start, "term_end": end,
                "consecutive_terms": terms, "visits_remaining": visits,
                "repair_coverage_remaining": round(cover, 2), "fee_entry_id": rid,
                "reinstatement_fee": fee, "dues_balance": balance, "status": "active"})


@tool(owner="agent", rw="write")
def set_reinstated_rate_lock_0c66ac3f(ctx: ToolContext, agreement_id: str, locked_annual_rate: float) -> str:
    """Record the price lock decided for the current term of a Comfort Club agreement: the
    agreement's locked first-system annual rate is replaced by the rate given, and that rate is
    the one the agreement shows as locked from now on. Nothing is charged. Success is the receipt
    below with status locked.

    Args:
        agreement_id: Id class — reference number of the member's Comfort Club agreement, read from the agreement lookup.
        locked_annual_rate: Fixed-format class — locked first-system annual rate, in USD, 2 decimal places, positive, rounded to the cent by the caller.

    Returns:
        A dictionary rendered as text with: agreement_id (the agreement updated),
        previous_locked_rate (USD, 2 decimal places, the figure replaced), locked_annual_rate (USD,
        2 decimal places, the figure now on the agreement) and status (always "locked").
    """
    agr = ctx.find("plan_agreements", agreement_id=agreement_id)
    agr = agr[0] if agr else {}
    rate = round(float(locked_annual_rate), 2)
    prev = round(float(agr.get("locked_annual_rate") or 0), 2)
    ctx.update("plan_agreements", agreement_id, locked_annual_rate=rate)
    return str({"agreement_id": agreement_id, "previous_locked_rate": prev,
                "locked_annual_rate": rate, "status": "locked"})


@tool(owner="agent", rw="write")
def post_missed_visit_fee_325d3ccb(ctx: ToolContext, agreement_id: str, billing_period: str,
                                   fee_amount: float) -> str:
    """Post a missed-appointment fee for a forfeited maintenance visit to a member's Comfort Club
    agreement. One missed-appointment fee charge is added to the dues history for the billing
    month given and the dues balance rises by the fee. The member sees the fee on the dues
    history. Success is the receipt below with status posted.

    Args:
        agreement_id: Id class — reference number of the member's Comfort Club agreement, read from the agreement lookup.
        billing_period: Fixed-format class — billing month the fee is charged to, in the format YYYY-MM.
        fee_amount: Fixed-format class — missed-appointment fee charged, in USD, 2 decimal places, positive, rounded to the cent by the caller.

    Returns:
        A dictionary rendered as text with: billing_entry_id (reference number of the fee charge),
        agreement_id (the agreement charged), billing_period (YYYY-MM), fee_amount (USD, 2 decimal
        places), dues_balance (USD, 2 decimal places, signed: positive means the member owes) and
        status (always "posted").
    """
    agr = ctx.find("plan_agreements", agreement_id=agreement_id)
    agr = agr[0] if agr else {}
    fee = round(float(fee_amount), 2)
    rid = ctx.make_id("pbe_", agreement_id, "missed_appointment_fee", billing_period, fee)
    ctx.create("plan_billing_entries", rid, billing_entry_id=rid, agreement_id=agreement_id,
               customer_id=agr.get("customer_id", ""), event_type="plan_dues_charge",
               line_type="missed_appointment_fee", billing_period=billing_period, amount=fee,
               posted_date=ctx.now()[:10], payment_method="", payment_reference="",
               source_entry_id="", ticket_id="")
    balance = round(float(agr.get("dues_balance") or 0) + fee, 2)
    ctx.update("plan_agreements", agreement_id, dues_balance=balance)
    return str({"billing_entry_id": rid, "agreement_id": agreement_id, "billing_period": billing_period,
                "fee_amount": fee, "dues_balance": balance, "status": "posted"})


@tool(owner="user", rw="write")
def pay_reinstated_term_dues_c2f743bd(ctx: ToolContext, agreement_id: str, payment_method: str,
                                      term_dues: float) -> str:
    """The member pays, in person, the dues of the current term of their Comfort Club agreement. The dues given
    are billed to the agreement as the renewal dues of its current term and the member's payment
    of the same amount is recorded with a processor confirmation number, so the dues balance is
    unchanged by the two entries together. The member receives the confirmation number. Success
    is the receipt below with status paid.

    Args:
        agreement_id: Id class — reference number of the member's Comfort Club agreement, as the agent reads it from the agreement lookup and gives it to the member.
        payment_method: Enum class — how the member pays: card_on_file when the member uses the card already stored on the account; ach_autopay when the member pays from the bank account set up for automatic drafts; card_by_phone when the member reads out a card during the call; check when the member pays by mailed check; original_payment_method when the payment returns to the method used originally, which applies only to payouts and never to a member's own payment.
        term_dues: Fixed-format class — dues of the agreement's current term billed and paid, in USD, 2 decimal places, positive, rounded to the cent by the caller.

    Returns:
        A dictionary rendered as text with: agreement_id (the agreement paid), charge_entry_id
        (reference number of the dues charge), payment_entry_id (reference number of the payment),
        payment_reference (processor confirmation number of the payment), term_dues (USD, 2
        decimal places), dues_balance (USD, 2 decimal places, signed) and status (always "paid").
    """
    agr = ctx.find("plan_agreements", agreement_id=agreement_id)
    agr = agr[0] if agr else {}
    dues = round(float(term_dues), 2)
    start = str(agr.get("term_start") or ctx.now()[:10])
    cust = agr.get("customer_id", "")
    cid = ctx.make_id("pbe_", agreement_id, "renewal_dues", start, dues)
    ctx.create("plan_billing_entries", cid, billing_entry_id=cid, agreement_id=agreement_id,
               customer_id=cust, event_type="plan_dues_charge", line_type="renewal_dues",
               billing_period=start[:7], amount=dues, posted_date=ctx.now()[:10], payment_method="",
               payment_reference="", source_entry_id="", ticket_id="")
    ref = ctx.make_id("CC", agreement_id, payment_method, dues, length=10).upper()
    pid = ctx.make_id("pbe_", agreement_id, "dues_payment", start, payment_method, dues)
    ctx.create("plan_billing_entries", pid, billing_entry_id=pid, agreement_id=agreement_id,
               customer_id=cust, event_type="plan_dues_payment", line_type="dues_payment",
               billing_period=ctx.now()[:7], amount=dues, posted_date=ctx.now()[:10],
               payment_method=payment_method, payment_reference=ref, source_entry_id="", ticket_id="")
    balance = round(float(agr.get("dues_balance") or 0), 2)
    return str({"agreement_id": agreement_id, "charge_entry_id": cid, "payment_entry_id": pid,
                "payment_reference": ref, "term_dues": dues, "dues_balance": balance, "status": "paid"})

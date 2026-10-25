"""Hidden task tools for the funding_and_disbursement_disputes difficulty (Larkspur Home Lending,
Closing and Funding). Each tool performs one atomic write on the closing's prepaid interest ledger
and keeps the closing's prepaid interest balance in step with the entry it books. The values the
tools receive are worked out by the agent from the published policies; the tools judge nothing.
"""

from erlbench import ToolContext, tool


class _LedgerCalendar:
    """Pure calendar arithmetic used to record the day span of an entry (both ends counted)."""

    @staticmethod
    def ordinal(stamp: str) -> int:
        y, m, d = (int(p) for p in str(stamp)[:10].split("-"))
        if m <= 2:
            y -= 1
            m += 12
        return 365 * y + y // 4 - y // 100 + y // 400 + (153 * (m - 3) + 2) // 5 + d

    @staticmethod
    def span_days(first: str, last: str) -> int:
        return _LedgerCalendar.ordinal(last) - _LedgerCalendar.ordinal(first) + 1


class _Money:
    """Cent rounding with halves rounded away from zero (half up for the positive amounts these tools book)."""

    @staticmethod
    def cents(value) -> float:
        v = float(value)
        sign = -1.0 if v < 0 else 1.0
        return sign * int(abs(v) * 100 + 0.5 + 1e-9) / 100.0


@tool(owner="agent", rw="write")
def refund_late_funding_interest_1de244fe(ctx: ToolContext, closing_id: str, source_interest_entry_id: str,
                                          interest_from_date: str, interest_through_date: str,
                                          daily_interest_amount: float, interest_amount: float) -> str:
    """Book a late-funding refund of prepaid interest on a closing: the agent returns to the borrower the
    prepaid interest collected for days on which the loan was not yet funded. One call adds one refund
    entry, marked as a refund for funding later than estimated, to the closing's prepaid interest ledger;
    the entry names the prepaid interest charge it corrects, records the earliest and latest refunded day, the
    number of refunded days (both ends counted), the per diem amount used and the refund amount (which
    includes any interest added because the refund is booked late), and is dated today. The closing's
    prepaid interest balance is reduced by the refund amount in the same step. The borrower can see the
    refund entry and the lower prepaid interest balance on the closing.

    Args:
        closing_id: Id class — reference number of the closing and funding engagement whose prepaid
            interest is refunded, as returned by the closing lookup.
        source_interest_entry_id: Id class — reference number of the prepaid interest charge entry this
            refund corrects, as returned by the prepaid interest ledger lookup for that closing.
        interest_from_date: Fixed-format class — earliest refunded day of interest, written as a calendar
            date in the format YYYY-MM-DD.
        interest_through_date: Fixed-format class — latest refunded day of interest, written as a calendar
            date in the format YYYY-MM-DD; the same as the earliest refunded day when a single day is refunded.
        daily_interest_amount: Fixed-format class — per diem amount at which each refunded day is
            returned, in USD with 2 decimal places, rounded half up to the cent.
        interest_amount: Fixed-format class — total refund amount, any interest added for a late booking
            included, in USD with 2 decimal places, a positive figure rounded half up to the cent.

    Returns:
        A confirmation string naming the new refund entry reference number, the closing reference
        number, the refunded period with its day count, the per diem amount, the refund amount and the
        closing's resulting prepaid interest balance; the presence of the new entry reference
        number indicates the refund was booked.
    """
    days = _LedgerCalendar.span_days(interest_from_date, interest_through_date)
    amount = _Money.cents(interest_amount)
    rid = ctx.make_id("fil_", closing_id, source_interest_entry_id, interest_from_date, interest_through_date,
                      daily_interest_amount, interest_amount)
    rows = ctx.find("closings", closing_id=closing_id)
    closing = rows[0] if rows else {}
    ctx.create("funding_interest_ledger", rid, interest_entry_id=rid, closing_id=closing_id,
               customer_id=closing.get("customer_id", ""), event_type="funding_per_diem_refunded",
               interest_from_date=interest_from_date, interest_through_date=interest_through_date,
               interest_days=days, daily_interest_amount=_Money.cents(daily_interest_amount),
               interest_amount=amount, entry_date=ctx.now()[:10], refund_reason="funding_later_than_estimated",
               source_interest_entry_id=source_interest_entry_id)
    balance = _Money.cents(float(closing.get("prepaid_interest_balance") or 0) - amount)
    ctx.update("closings", closing_id, prepaid_interest_balance=balance)
    return (f"Late-funding refund {rid} booked on closing {closing_id}: {interest_from_date} through "
            f"{interest_through_date} ({days} day(s)) at {_Money.cents(daily_interest_amount):.2f} per day, "
            f"refund {amount:.2f}; prepaid interest balance now {balance:.2f}.")


@tool(owner="user", rw="write")
def pay_prepaid_interest_shortfall_7376ee5f(ctx: ToolContext, closing_id: str, interest_from_date: str,
                                            interest_through_date: str, daily_interest_amount: float,
                                            interest_amount: float) -> str:
    """The borrower pays a prepaid interest shortfall on their own funded closing: one call adds one
    prepaid interest charge entry to the closing's prepaid interest ledger for the amount the borrower
    pays, recording the period of the prepaid interest charge being trued up, the number of days in that
    period (both ends counted), the per diem amount the true-up is priced at and the amount paid, dated
    today. The closing's prepaid interest balance rises by the amount paid in the same step. The borrower
    sees the new charge entry and the higher prepaid interest balance on the closing.

    Args:
        closing_id: Id class — reference number of the borrower's closing and funding engagement, as the
            agent reads it from the closing lookup and passes it on.
        interest_from_date: Fixed-format class — opening day of the prepaid interest charge period being
            trued up, written as a calendar date in the format YYYY-MM-DD.
        interest_through_date: Fixed-format class — closing day of the prepaid interest charge period being
            trued up, written as a calendar date in the format YYYY-MM-DD.
        daily_interest_amount: Fixed-format class — per diem amount the true-up is priced at, in USD with
            2 decimal places, rounded half up to the cent.
        interest_amount: Fixed-format class — amount the borrower pays, in USD with 2 decimal places, a
            positive figure rounded half up to the cent.

    Returns:
        A confirmation string naming the new charge entry reference number, the closing reference number,
        the period with its day count, the per diem amount, the amount paid and the closing's prepaid
        interest balance that results; the presence of the new entry reference number indicates the
        payment was recorded.
    """
    days = _LedgerCalendar.span_days(interest_from_date, interest_through_date)
    amount = _Money.cents(interest_amount)
    rid = ctx.make_id("fil_", closing_id, interest_from_date, interest_through_date, daily_interest_amount,
                      interest_amount)
    rows = ctx.find("closings", closing_id=closing_id)
    closing = rows[0] if rows else {}
    ctx.create("funding_interest_ledger", rid, interest_entry_id=rid, closing_id=closing_id,
               customer_id=closing.get("customer_id", ""), event_type="funding_per_diem_charged",
               interest_from_date=interest_from_date, interest_through_date=interest_through_date,
               interest_days=days, daily_interest_amount=_Money.cents(daily_interest_amount),
               interest_amount=amount, entry_date=ctx.now()[:10], refund_reason="none",
               source_interest_entry_id="")
    balance = _Money.cents(float(closing.get("prepaid_interest_balance") or 0) + amount)
    ctx.update("closings", closing_id, prepaid_interest_balance=balance)
    return (f"Prepaid interest payment {rid} recorded on closing {closing_id}: {interest_from_date} through "
            f"{interest_through_date} ({days} day(s)) priced at {_Money.cents(daily_interest_amount):.2f} per day, "
            f"amount paid {amount:.2f}; prepaid interest balance now {balance:.2f}.")


@tool(owner="agent", rw="write")
def refund_returned_wire_interest_891dcbc9(ctx: ToolContext, closing_id: str, source_interest_entry_id: str,
                                           interest_from_date: str, interest_through_date: str,
                                           daily_interest_amount: float, interest_amount: float) -> str:
    """Book a returned-wire interest refund on a closing: the agent returns to the borrower the prepaid
    interest collected for the lost days of a funding wire that came back for a Larkspur-side reason
    (Larkspur's wrong amount or Larkspur's recall). One call adds one refund entry, marked as a refund for a returned-wire delay, to the closing's
    prepaid interest ledger; the entry names the prepaid interest charge it corrects, records the earliest
    and latest refunded day, the number of refunded days (both ends counted), the per diem amount used and
    the refund amount, and is dated today. The closing's prepaid interest balance is reduced by the refund
    amount in the same step. The borrower can see the refund entry and the lower prepaid interest balance.

    Args:
        closing_id: Id class — reference number of the closing and funding engagement whose prepaid
            interest is refunded, as returned by the closing lookup.
        source_interest_entry_id: Id class — reference number of the prepaid interest charge entry this
            refund corrects, as returned by the prepaid interest ledger lookup for that closing.
        interest_from_date: Fixed-format class — earliest refunded day of interest, written as a calendar
            date in the format YYYY-MM-DD.
        interest_through_date: Fixed-format class — latest refunded day of interest, written as a calendar
            date in the format YYYY-MM-DD; the same as the earliest refunded day when a single day is refunded.
        daily_interest_amount: Fixed-format class — per diem amount at which each refunded day is
            returned, in USD with 2 decimal places, rounded half up to the cent.
        interest_amount: Fixed-format class — total refund amount, in USD with 2 decimal places, a
            positive figure rounded half up to the cent.

    Returns:
        A confirmation string naming the new refund entry reference number, the closing reference
        number, the refunded period with its day count, the per diem amount, the refund amount and the
        closing's resulting prepaid interest balance; the presence of the new entry reference number
        indicates the refund was booked.
    """
    days = _LedgerCalendar.span_days(interest_from_date, interest_through_date)
    amount = _Money.cents(interest_amount)
    rid = ctx.make_id("fil_", closing_id, source_interest_entry_id, interest_from_date, interest_through_date,
                      daily_interest_amount, interest_amount, "returned_wire_delay")
    rows = ctx.find("closings", closing_id=closing_id)
    closing = rows[0] if rows else {}
    ctx.create("funding_interest_ledger", rid, interest_entry_id=rid, closing_id=closing_id,
               customer_id=closing.get("customer_id", ""), event_type="funding_per_diem_refunded",
               interest_from_date=interest_from_date, interest_through_date=interest_through_date,
               interest_days=days, daily_interest_amount=_Money.cents(daily_interest_amount),
               interest_amount=amount, entry_date=ctx.now()[:10], refund_reason="returned_wire_delay",
               source_interest_entry_id=source_interest_entry_id)
    balance = _Money.cents(float(closing.get("prepaid_interest_balance") or 0) - amount)
    ctx.update("closings", closing_id, prepaid_interest_balance=balance)
    return (f"Returned-wire interest refund {rid} booked on closing {closing_id}: {interest_from_date} through "
            f"{interest_through_date} ({days} day(s)) at {_Money.cents(daily_interest_amount):.2f} per day, "
            f"refund {amount:.2f}; prepaid interest balance now {balance:.2f}.")


@tool(owner="user", rw="write")
def pay_funding_month_interest_3474c980(ctx: ToolContext, closing_id: str, interest_from_date: str,
                                        interest_through_date: str, daily_interest_amount: float,
                                        interest_amount: float) -> str:
    """The borrower pays the prepaid interest for the month in which their loan actually funded: one call
    adds one prepaid interest charge entry to the closing's prepaid interest ledger for the amount the
    borrower pays (which may be net of a setoff and include payment charges), recording the earliest and latest day of interest it covers, the number of those days
    (both ends counted), the per diem amount it is priced at and the amount paid, dated today. The
    closing's prepaid interest balance rises by the amount paid in the same step. The borrower sees the new
    charge entry and the higher prepaid interest balance on the closing.

    Args:
        closing_id: Id class — reference number of the borrower's closing and funding engagement, as the
            agent reads it from the closing lookup and passes it on.
        interest_from_date: Fixed-format class — earliest day of interest the payment covers, written as a
            calendar date in the format YYYY-MM-DD.
        interest_through_date: Fixed-format class — latest day of interest the payment covers, written as a
            calendar date in the format YYYY-MM-DD.
        daily_interest_amount: Fixed-format class — per diem amount the payment is priced at, in USD with
            2 decimal places, rounded half up to the cent.
        interest_amount: Fixed-format class — amount the borrower pays, in USD with 2 decimal places, a
            positive figure rounded half up to the cent.

    Returns:
        A confirmation string naming the new charge entry reference number, the closing reference number,
        the covered period with its day count, the per diem amount, the amount paid and the closing's
        resulting prepaid interest balance; the presence of the new entry reference number indicates the
        payment was recorded.
    """
    days = _LedgerCalendar.span_days(interest_from_date, interest_through_date)
    amount = _Money.cents(interest_amount)
    rid = ctx.make_id("fil_", closing_id, interest_from_date, interest_through_date, daily_interest_amount,
                      interest_amount)
    rows = ctx.find("closings", closing_id=closing_id)
    closing = rows[0] if rows else {}
    ctx.create("funding_interest_ledger", rid, interest_entry_id=rid, closing_id=closing_id,
               customer_id=closing.get("customer_id", ""), event_type="funding_per_diem_charged",
               interest_from_date=interest_from_date, interest_through_date=interest_through_date,
               interest_days=days, daily_interest_amount=_Money.cents(daily_interest_amount),
               interest_amount=amount, entry_date=ctx.now()[:10], refund_reason="none",
               source_interest_entry_id="")
    balance = _Money.cents(float(closing.get("prepaid_interest_balance") or 0) + amount)
    ctx.update("closings", closing_id, prepaid_interest_balance=balance)
    return (f"Funding-month interest payment {rid} recorded on closing {closing_id}: {interest_from_date} through "
            f"{interest_through_date} ({days} day(s)) priced at {_Money.cents(daily_interest_amount):.2f} per day, "
            f"amount paid {amount:.2f}; prepaid interest balance now {balance:.2f}.")


@tool(owner="agent", rw="write")
def decide_prepaid_interest_dispute_44bdf39e(ctx: ToolContext, source_dispute_id: str, disputed_entry_id: str,
                                             resolution: str, refund_amount: float) -> str:
    """Record Larkspur's decision on a borrower's funding dispute: one call adds one decision record that
    names the filing it decides and the prepaid interest charge it recomputed, carries over the filing's
    closing, dispute type and filing date, and records the outcome, today's decision date and the amount refunded. When the outcome
    is a refund, the same call also books the refund as a prepaid interest refund entry for that amount on
    the closing's prepaid interest ledger (marked as a calculation correction, naming the recomputed charge
    and recording that charge's daily amount) and lowers the closing's prepaid interest balance by it. The borrower can see the decision and, for a refund, the refund entry
    and the lower balance.

    Args:
        source_dispute_id: Id class — reference number of the pending dispute filing being decided, as
            returned by the funding dispute lookup for the closing.
        disputed_entry_id: Id class — reference number of the prepaid interest charge entry the decision
            recomputed, as returned by the prepaid interest ledger lookup for the closing.
        resolution: Enum class — the decision outcome, exactly one of: refund_issued when prepaid interest
            is refunded to the borrower; fee_reversed when a disputed closing fee is reversed;
            denied_correct_as_charged when the charge stands as charged; denied_untimely when the dispute
            was filed outside its window; pending marks a filing still awaiting decision and is never a
            decision outcome, so it is not passed here.
        refund_amount: Fixed-format class — amount refunded or reversed by the decision, in USD with 2
            decimal places, rounded half up to the cent; 0.00 when the dispute is denied.

    Returns:
        A confirmation string naming the decision record reference number, the filing it decides, the
        closing reference number, the outcome, the refund amount and, when a refund was booked, the refund
        entry reference number; the presence of the decision record reference number indicates the
        decision was recorded.
    """
    amount = _Money.cents(refund_amount)
    rows = ctx.find("funding_disputes", funding_dispute_id=source_dispute_id)
    filing = rows[0] if rows else {}
    closing_id = filing.get("closing_id", "")
    did = ctx.make_id("fdd_", source_dispute_id, disputed_entry_id, resolution, refund_amount)
    ctx.create("funding_disputes", did, funding_dispute_id=did, closing_id=closing_id,
               customer_id=filing.get("customer_id", ""), event_type="funding_dispute_resolved",
               dispute_type=filing.get("dispute_type", ""), filed_date=filing.get("filed_date", ""),
               disputed_entry_id=disputed_entry_id, resolution=resolution,
               resolved_date=ctx.now()[:10], refund_amount=amount, source_dispute_id=source_dispute_id)
    refund_note = ""
    if resolution == "refund_issued" and amount > 0:
        crow = ctx.find("closings", closing_id=closing_id)
        closing = crow[0] if crow else {}
        today = ctx.now()[:10]
        crows = ctx.find("funding_interest_ledger", interest_entry_id=disputed_entry_id)
        daily = _Money.cents((crows[0] if crows else {}).get("daily_interest_amount") or 0)
        fid = ctx.make_id("fil_", did, amount)
        ctx.create("funding_interest_ledger", fid, interest_entry_id=fid, closing_id=closing_id,
                   customer_id=filing.get("customer_id", ""), event_type="funding_per_diem_refunded",
                   interest_from_date=today, interest_through_date=today, interest_days=0,
                   daily_interest_amount=daily, interest_amount=amount, entry_date=today,
                   refund_reason="calculation_error", source_interest_entry_id=disputed_entry_id)
        balance = _Money.cents(float(closing.get("prepaid_interest_balance") or 0) - amount)
        ctx.update("closings", closing_id, prepaid_interest_balance=balance)
        refund_note = f"; refund entry {fid} booked, prepaid interest balance now {balance:.2f}"
    return (f"Dispute decision {did} recorded for filing {source_dispute_id} on closing {closing_id}: "
            f"{resolution}, refund {amount:.2f}{refund_note}.")


@tool(owner="agent", rw="write")
def refund_redraw_fee_excess_c6a6aba4(ctx: ToolContext, closing_id: str, source_fee_entry_id: str,
                                      amount: float) -> str:
    """Refund the part of a doc redraw fee that was charged above Larkspur's redraw schedule: the agent adds one
    reversal entry to the closing's closing fee ledger for the doc redraw fee code, naming the redraw fee charge
    it corrects, marked as a reversal of an amount outside the fee schedule, for the amount given and dated
    today, and lowers the closing's closing fee balance by that amount in the same step. The borrower can see
    the reversal entry and the lower closing fee balance on the closing.

    Args:
        closing_id: Id class — reference number of the closing and funding engagement whose redraw fee is
            refunded, as returned by the closing lookup.
        source_fee_entry_id: Id class — reference number of the doc redraw fee charge entry this refund
            corrects, as returned by the closing fee ledger lookup for that closing.
        amount: Fixed-format class — amount refunded, in USD with 2 decimal places, a positive figure
            rounded half up to the cent.

    Returns:
        A confirmation string naming the new reversal entry reference number, the closing reference number,
        the redraw fee charge corrected, the amount refunded and the closing's resulting closing fee
        balance; the presence of the new entry reference number indicates the refund was booked.
    """
    fee = _Money.cents(amount)
    eid = ctx.make_id("ffl_", closing_id, source_fee_entry_id, amount)
    rows = ctx.find("closings", closing_id=closing_id)
    closing = rows[0] if rows else {}
    ctx.create("funding_fee_ledger", eid, closing_fee_entry_id=eid, closing_id=closing_id,
               customer_id=closing.get("customer_id", ""), event_type="funding_fee_reversed",
               fee_code="doc_redraw_fee", amount=fee, entry_date=ctx.now()[:10],
               reversal_reason="not_in_fee_schedule", source_fee_entry_id=source_fee_entry_id)
    balance = _Money.cents(float(closing.get("closing_fee_balance") or 0) - fee)
    ctx.update("closings", closing_id, closing_fee_balance=balance)
    return (f"Redraw fee refund {eid} booked on closing {closing_id} against charge {source_fee_entry_id}: "
            f"{fee:.2f} refunded; closing fee balance now {balance:.2f}.")

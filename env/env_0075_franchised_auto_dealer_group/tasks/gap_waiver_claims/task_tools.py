"""Hidden task tools of the gap_waiver_claims difficulty (Kessler GAP Waiver Addenda).

Each tool performs one atomic business action on one GAP waiver and writes only gap tables.
No tool checks eligibility or prices anything; a tool refuses only a malformed value, a reference to a
record of the wrong kind, or a waiver on the other side of the record partition its docstring states,
and then writes nothing.
"""

from decimal import ROUND_HALF_UP, Decimal

from erlbench import ToolContext, tool


class _GapRecords:
    """Record and format helpers shared by the tools (not a tool)."""

    @staticmethod
    def waiver(ctx, gap_waiver_id):
        rows = ctx.find("gap_waivers", gap_waiver_id=gap_waiver_id)
        return rows[0] if rows else {}

    @staticmethod
    def cents(value):
        """Round a money amount half up to the cent with exact decimal arithmetic (a half cent goes up)."""
        return float(Decimal(str(value)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP))

    @staticmethod
    def is_date(text):
        s = str(text or "")
        if len(s) != 10 or s[4] != "-" or s[7] != "-":
            return False
        y, m, d = s[:4], s[5:7], s[8:]
        if not (y.isdigit() and m.isdigit() and d.isdigit()):
            return False
        year, month, day = int(y), int(m), int(d)
        if not 1 <= month <= 12:
            return False
        leap = (year % 4 == 0 and year % 100 != 0) or year % 400 == 0
        lengths = [31, 29 if leap else 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
        return 1 <= day <= lengths[month - 1]

    @staticmethod
    def entry(ctx, gap_waiver_id, entry_id, event_type):
        rows = ctx.find("gap_ledger", gap_entry_id=entry_id)
        if rows and rows[0].get("gap_waiver_id") == gap_waiver_id and rows[0].get("event_type") == event_type:
            return rows[0]
        return None


_EMPTY_CLAIM = {
    "claim_number": "", "benefit_line_type": "not_applicable", "loss_type": "not_applicable",
    "loss_date": "", "settlement_date": "", "payoff_at_loss": 0.0, "insurance_acv_settlement": 0.0,
    "insurance_deductible": 0.0, "past_due_amounts": 0.0, "late_fees_and_charges": 0.0,
    "deferred_payments": 0.0, "addon_refunds_credited": 0.0, "negative_equity_amount": 0.0,
    "salvage_retention_value": 0.0, "denial_reason": "not_applicable",
}


@tool(owner="user", rw="write")
def confirm_gap_cancellation_0d8763f7(ctx: ToolContext, gap_waiver_id: str, gap_cancel_request_id: str,
                                      effective_date: str, cancel_method: str, refund_amount: float) -> str:
    """The waiver holder personally confirms the signed cancellation request already on file for their Kessler GAP waiver, which cancels the waiver. On success the request is marked completed, the waiver moves to cancelled status with the given effective date as its closing date, a refund calculation entry for the given refund amount and refund basis is booked on the waiver's ledger dated on the effective date, and the waiver's refund due rises by that amount. The holder sees a confirmation naming the refund calculation entry. The request reference must name a request in submitted status recorded for this same waiver, the date must be a real calendar date in the stated form and the amount must not be negative; otherwise an Error line is returned and nothing is written.

    Args:
        gap_waiver_id: Id class — reference number of the GAP waiver being cancelled, as returned by the GAP waiver lookup for this holder.
        gap_cancel_request_id: Id class — reference number of the holder's signed cancellation request on file for this waiver in submitted status, as returned by the cancellation request lookup.
        effective_date: Fixed-format class — the date the cancellation takes effect, written YYYY-MM-DD (calendar date, no time or time zone); it becomes the waiver's closing date and the date of the refund calculation entry.
        cancel_method: Enum class — the basis of the refund, exactly one of: flat_free_look (the cancellation falls inside the free-look window and the full price comes back); flat_deal_unwound (the waiver's purchase deal was unwound and the full price comes back); pro_rata (any other cancellation, refunded for the unused part of the term); not_applicable (reserved for ledger entries that are not refund calculations, so it is never the basis of a cancellation refund and is refused here).
        refund_amount: Fixed-format class — the refund owed on the cancellation in USD (US dollars), a non-negative number with 2 decimal places, rounded half up to the cent (a half cent goes up); 0.00 when no refund is owed.

    Returns:
        On success a one-line confirmation string "Cancellation confirmed: waiver <gap_waiver_id> cancelled effective <effective_date>; refund calculation <entry id> booked for <amount> USD (<cancel_method>); request <gap_cancel_request_id> completed." where <entry id> is the new refund calculation entry's reference number and <amount> is the booked refund with 2 decimals. Receiving this line means the cancellation and its refund calculation are recorded; a line starting "Error:" means nothing was written.
    """
    reqs = ctx.find("gap_cancellation_requests", gap_cancel_request_id=gap_cancel_request_id)
    if not reqs or reqs[0].get("gap_waiver_id") != gap_waiver_id or reqs[0].get("request_status") != "submitted":
        return "Error: the request reference must name a submitted cancellation request recorded for this waiver."
    if not _GapRecords.is_date(effective_date):
        return "Error: effective_date must be a calendar date written YYYY-MM-DD."
    if cancel_method not in ("flat_free_look", "flat_deal_unwound", "pro_rata"):
        return "Error: cancel_method must be flat_free_look, flat_deal_unwound or pro_rata."
    if float(refund_amount) < 0:
        return "Error: refund_amount must not be negative."
    w = _GapRecords.waiver(ctx, gap_waiver_id)
    amount = _GapRecords.cents(refund_amount)
    eid = ctx.make_id("gle_", gap_waiver_id, gap_cancel_request_id, effective_date, cancel_method, amount)
    ctx.update("gap_cancellation_requests", gap_cancel_request_id, request_status="completed")
    ctx.update("gap_waivers", gap_waiver_id, status="cancelled", closed_date=effective_date,
               refund_due_balance=_GapRecords.cents(float(w.get("refund_due_balance") or 0) + amount))
    ctx.create("gap_ledger", eid, gap_entry_id=eid, gap_waiver_id=gap_waiver_id, customer_id=w.get("customer_id"),
               event_type="gap_refund_calculated", entry_date=effective_date, amount=amount,
               cancel_method=cancel_method, refund_payee="not_applicable", source_entry_id="", **_EMPTY_CLAIM)
    return (f"Cancellation confirmed: waiver {gap_waiver_id} cancelled effective {effective_date}; refund calculation "
            f"{eid} booked for {amount:.2f} USD ({cancel_method}); request {gap_cancel_request_id} completed.")


@tool(owner="agent", rw="write")
def release_refund_lienholder_c4427cd3(ctx: ToolContext, gap_waiver_id: str, source_entry_id: str,
                                       amount_paid: float) -> str:
    """Release the refund owed on a cancelled Kessler GAP waiver whose loan is still open (no loan payoff date on file) to the lienholder named on the waiver, as one payment that reduces the holder's loan. On success a refund payment entry dated today, payable to the lienholder and pointing at the refund calculation it pays, is booked on the waiver's ledger for the amount given, and the waiver's refund due is cleared to 0.00. The holder and the lienholder can see the payment on the waiver's history. A waiver with a loan payoff date on file is refused (its refund is released to the holder), the source reference must name a refund calculation entry of this same waiver and the amount must be above 0.00; otherwise an Error line is returned and nothing is written.

    Args:
        gap_waiver_id: Id class — reference number of the GAP waiver whose refund is released, as returned by the GAP waiver lookup.
        source_entry_id: Id class — reference number of the refund calculation entry being paid, as shown on the waiver's ledger lookup or in the cancellation confirmation.
        amount_paid: Fixed-format class — the total released to the lienholder in USD (US dollars), a positive number with 2 decimal places, rounded half up to the cent (a half cent goes up).

    Returns:
        On success a one-line confirmation string "Refund released to lienholder <lienholder name>: payment <entry id> for <amount> USD against refund calculation <source_entry_id> on waiver <gap_waiver_id>; refund due now 0.00." where <entry id> is the new payment entry's reference number and <amount> is the payment with 2 decimals. Receiving this line means the payment is recorded; a line starting "Error:" means nothing was written.
    """
    w = _GapRecords.waiver(ctx, gap_waiver_id)
    if w.get("loan_payoff_date"):
        return "Error: a waiver with a loan payoff date on file has its refund released to the holder."
    if not _GapRecords.entry(ctx, gap_waiver_id, source_entry_id, "gap_refund_calculated"):
        return "Error: source_entry_id must name a refund calculation entry of this waiver."
    if float(amount_paid) <= 0:
        return "Error: amount_paid must be above 0.00."
    amount = _GapRecords.cents(amount_paid)
    eid = ctx.make_id("gle_", gap_waiver_id, source_entry_id, "lienholder", amount)
    ctx.create("gap_ledger", eid, gap_entry_id=eid, gap_waiver_id=gap_waiver_id, customer_id=w.get("customer_id"),
               event_type="gap_refund_paid", entry_date=ctx.now()[:10], amount=amount, cancel_method="not_applicable",
               refund_payee="lienholder", source_entry_id=source_entry_id, **_EMPTY_CLAIM)
    ctx.update("gap_waivers", gap_waiver_id, refund_due_balance=0.0)
    return (f"Refund released to lienholder {w.get('lienholder_name')}: payment {eid} for {amount:.2f} USD against refund "
            f"calculation {source_entry_id} on waiver {gap_waiver_id}; refund due now 0.00.")


@tool(owner="agent", rw="write")
def pay_gap_balance_0b87221e(ctx: ToolContext, gap_waiver_id: str, claim_number: str, amount: float) -> str:
    """Pay the GAP balance benefit of a total-loss claim on a Kessler GAP waiver to the waiver's lienholder, which settles the waiver. On success a paid GAP balance line dated today is booked under the claim number, carrying over the loss and payoff figures already on file for that claim number, the waiver's benefits paid rise by the amount, and the waiver moves to claim_settled status with today as its closing date. The holder and the lienholder can see the paid line and the settled waiver. The claim number must already carry a GAP balance line on this waiver's ledger and the amount must not be negative; otherwise an Error line is returned and nothing is written.

    Args:
        gap_waiver_id: Id class — reference number of the GAP waiver the claim is under, as returned by the GAP waiver lookup.
        claim_number: Verbatim class — the GAP claim number exactly as it appears on the waiver's claim history, copied character for character with its prefix, hyphen and digits, with no translation, normalisation, summarisation, addition or deletion (verbatim).
        amount: Fixed-format class — the GAP balance benefit paid to the lienholder in USD (US dollars), a non-negative number with 2 decimal places, rounded half up to the cent (a half cent goes up).

    Returns:
        On success a one-line confirmation string "GAP balance paid: line <entry id> for <amount> USD on claim <claim_number> under waiver <gap_waiver_id>, paid to <lienholder name>; waiver now claim_settled." where <entry id> is the new paid line's reference number and <amount> is the payment with 2 decimals. Receiving this line means the benefit is paid and the waiver is settled; a line starting "Error:" means nothing was written.
    """
    on_file = sorted(ctx.find("gap_ledger", gap_waiver_id=gap_waiver_id, claim_number=claim_number,
                              benefit_line_type="gap_balance"), key=lambda r: str(r.get("entry_date")))
    if not on_file:
        return "Error: claim_number must already carry a GAP balance line on this waiver's ledger."
    if float(amount) < 0:
        return "Error: amount must not be negative."
    w = _GapRecords.waiver(ctx, gap_waiver_id)
    amount = _GapRecords.cents(amount)
    src = on_file[-1]
    figures = {k: src.get(k, v) for k, v in _EMPTY_CLAIM.items()}
    figures.update(claim_number=claim_number, benefit_line_type="gap_balance", denial_reason="not_applicable")
    eid = ctx.make_id("gle_", gap_waiver_id, claim_number, "gap_balance", amount)
    today = ctx.now()[:10]
    ctx.create("gap_ledger", eid, gap_entry_id=eid, gap_waiver_id=gap_waiver_id, customer_id=w.get("customer_id"),
               event_type="gap_benefit_paid", entry_date=today, amount=amount, cancel_method="not_applicable",
               refund_payee="not_applicable", source_entry_id="", **figures)
    ctx.update("gap_waivers", gap_waiver_id, status="claim_settled", closed_date=today,
               benefits_paid_total=_GapRecords.cents(float(w.get("benefits_paid_total") or 0) + amount))
    return (f"GAP balance paid: line {eid} for {amount:.2f} USD on claim {claim_number} under waiver {gap_waiver_id}, "
            f"paid to {w.get('lienholder_name')}; waiver now claim_settled.")


@tool(owner="agent", rw="write")
def recover_benefit_overpayment_99b30941(ctx: ToolContext, gap_waiver_id: str, source_entry_id: str, amount: float) -> str:
    """Reverse the overpaid part of a paid GAP balance line on a Kessler GAP waiver, recovering that part of the benefit. On success a benefit reversal entry dated today is booked on the waiver's ledger for the amount given, pointing at the paid line it reverses and carrying that line's claim number, and the waiver's benefits paid fall by that amount; the waiver's status is left unchanged. The holder can see the reversal on the waiver's claim history. The source reference must name a paid GAP balance line of this same waiver and the amount must be above 0.00; otherwise an Error line is returned and nothing is written.

    Args:
        gap_waiver_id: Id class — reference number of the GAP waiver whose paid line is reversed, as returned by the GAP waiver lookup.
        source_entry_id: Id class — reference number of the paid GAP balance line being reversed, as shown on the waiver's ledger lookup.
        amount: Fixed-format class — the part of the paid line reversed, in USD (US dollars), a positive number with 2 decimal places, rounded half up to the cent (a half cent goes up).

    Returns:
        On success a one-line confirmation string "Benefit reversal booked: entry <entry id> for <amount> USD against paid line <source_entry_id> on claim <claim number> under waiver <gap_waiver_id>; benefits paid now <total> USD." where <entry id> is the new reversal entry's reference number, <amount> is the reversed amount with 2 decimals and <total> is the waiver's benefits paid net of the reversal with 2 decimals. Receiving this line means the reversal is recorded; a line starting "Error:" means nothing was written.
    """
    src = _GapRecords.entry(ctx, gap_waiver_id, source_entry_id, "gap_benefit_paid")
    if not src or src.get("benefit_line_type") != "gap_balance":
        return "Error: source_entry_id must name a paid GAP balance line of this waiver."
    if float(amount) <= 0:
        return "Error: amount must be above 0.00."
    w = _GapRecords.waiver(ctx, gap_waiver_id)
    amount = _GapRecords.cents(amount)
    claim = src.get("claim_number") or ""
    eid = ctx.make_id("gle_", gap_waiver_id, source_entry_id, "reversal", amount)
    figures = dict(_EMPTY_CLAIM)
    figures.update(claim_number=claim)
    ctx.create("gap_ledger", eid, gap_entry_id=eid, gap_waiver_id=gap_waiver_id, customer_id=w.get("customer_id"),
               event_type="gap_benefit_reversed", entry_date=ctx.now()[:10], amount=amount,
               cancel_method="not_applicable", refund_payee="not_applicable", source_entry_id=source_entry_id, **figures)
    total = _GapRecords.cents(float(w.get("benefits_paid_total") or 0) - amount)
    ctx.update("gap_waivers", gap_waiver_id, benefits_paid_total=total)
    return (f"Benefit reversal booked: entry {eid} for {amount:.2f} USD against paid line {source_entry_id} on claim "
            f"{claim} under waiver {gap_waiver_id}; benefits paid now {total:.2f} USD.")


@tool(owner="user", rw="write")
def apply_replacement_allowance_cdefd282(ctx: ToolContext, gap_waiver_id: str, claim_number: str, credit_amount: float) -> str:
    """The waiver holder personally applies the replacement vehicle credit of their settled Kessler GAP Plus claim to the replacement vehicle they are buying from a Kessler store, assigning the credit to that store on their behalf. On success a paid replacement vehicle credit line dated today is booked under the claim number, carrying over the loss and payoff figures already on file for that claim number's GAP balance line, and the waiver's benefits paid rise by the credit amount; the waiver stays claim_settled. The holder sees a confirmation naming the credit line. The claim number must already carry a GAP balance line on this waiver's ledger and the amount must be above 0.00; otherwise an Error line is returned and nothing is written.

    Args:
        gap_waiver_id: Id class — reference number of the settled GAP waiver the claim is under, as returned by the GAP waiver lookup for this holder.
        claim_number: Verbatim class — the GAP claim number exactly as it appears on the waiver's claim history, copied character for character with its prefix, hyphen and digits, with no translation, normalisation, summarisation, addition or deletion (verbatim).
        credit_amount: Fixed-format class — the replacement vehicle credit applied, in USD (US dollars), a positive number with 2 decimal places, rounded half up to the cent (a half cent goes up).

    Returns:
        On success a one-line confirmation string "Replacement credit applied: line <entry id> for <amount> USD on claim <claim_number> under waiver <gap_waiver_id>; benefits paid now <total> USD." where <entry id> is the new credit line's reference number, <amount> is the credit with 2 decimals and <total> is the waiver's benefits paid including the credit with 2 decimals. Receiving this line means the credit is recorded; a line starting "Error:" means nothing was written.
    """
    on_file = sorted(ctx.find("gap_ledger", gap_waiver_id=gap_waiver_id, claim_number=claim_number,
                              benefit_line_type="gap_balance"), key=lambda r: str(r.get("entry_date")))
    if not on_file:
        return "Error: claim_number must already carry a GAP balance line on this waiver's ledger."
    if float(credit_amount) <= 0:
        return "Error: credit_amount must be above 0.00."
    w = _GapRecords.waiver(ctx, gap_waiver_id)
    amount = _GapRecords.cents(credit_amount)
    src = on_file[-1]
    figures = {k: src.get(k, v) for k, v in _EMPTY_CLAIM.items()}
    figures.update(claim_number=claim_number, benefit_line_type="replacement_vehicle_credit", denial_reason="not_applicable")
    eid = ctx.make_id("gle_", gap_waiver_id, claim_number, "replacement_vehicle_credit", amount)
    ctx.create("gap_ledger", eid, gap_entry_id=eid, gap_waiver_id=gap_waiver_id, customer_id=w.get("customer_id"),
               event_type="gap_benefit_paid", entry_date=ctx.now()[:10], amount=amount, cancel_method="not_applicable",
               refund_payee="not_applicable", source_entry_id="", **figures)
    total = _GapRecords.cents(float(w.get("benefits_paid_total") or 0) + amount)
    ctx.update("gap_waivers", gap_waiver_id, benefits_paid_total=total)
    return (f"Replacement credit applied: line {eid} for {amount:.2f} USD on claim {claim_number} under waiver "
            f"{gap_waiver_id}; benefits paid now {total:.2f} USD.")


@tool(owner="agent", rw="write")
def terminate_paid_off_waiver_88a68523(ctx: ToolContext, gap_waiver_id: str, effective_date: str, cancel_method: str,
                                       refund_amount: float) -> str:
    """Terminate a Kessler GAP waiver whose installment contract the lienholder has reported paid off or refinanced away, and book its termination refund. On success the waiver moves to terminated status with the given effective date as its closing date, a refund calculation entry for the given refund amount and refund basis is booked on the waiver's ledger dated on the effective date, and the waiver's refund due rises by that amount. The holder can see the terminated waiver and the refund due on it. The waiver must carry a loan payoff date reported by its lienholder and no cancellation request in submitted status, the date must be a real calendar date in the stated form and the amount must not be negative; otherwise an Error line is returned and nothing is written.

    Args:
        gap_waiver_id: Id class — reference number of the GAP waiver being terminated, as returned by the GAP waiver lookup.
        effective_date: Fixed-format class — the date the termination takes effect, written YYYY-MM-DD (calendar date, no time or time zone); it becomes the waiver's closing date and the date of the refund calculation entry.
        cancel_method: Enum class — the basis of the termination refund, exactly one of: pro_rata (the refund is the unused part of the term); flat_deal_unwound (the waiver's purchase deal was unwound and the full price comes back); flat_free_look (refused here: a free-look refund belongs to a holder's cancellation, never to a termination); not_applicable (refused here: reserved for ledger entries that are not refund calculations).
        refund_amount: Fixed-format class — the termination refund owed, in USD (US dollars), a non-negative number with 2 decimal places, rounded half up to the cent (a half cent goes up); 0.00 when no refund is owed.

    Returns:
        On success a one-line confirmation string "Waiver <gap_waiver_id> terminated effective <effective_date>; refund calculation <entry id> booked for <amount> USD (<cancel_method>); refund due now <due> USD." where <entry id> is the new refund calculation entry's reference number, <amount> is the booked refund with 2 decimals and <due> is the waiver's refund due with 2 decimals. Receiving this line means the termination and its refund calculation are recorded; a line starting "Error:" means nothing was written.
    """
    w = _GapRecords.waiver(ctx, gap_waiver_id)
    if not w or not w.get("loan_payoff_date"):
        return "Error: the waiver must carry a loan payoff date reported by its lienholder."
    if ctx.find("gap_cancellation_requests", gap_waiver_id=gap_waiver_id, request_status="submitted"):
        return "Error: a waiver carrying a submitted cancellation request ends by the holder's cancellation, not by termination."
    if not _GapRecords.is_date(effective_date):
        return "Error: effective_date must be a calendar date written YYYY-MM-DD."
    if cancel_method not in ("pro_rata", "flat_deal_unwound"):
        return "Error: cancel_method must be pro_rata or flat_deal_unwound."
    if float(refund_amount) < 0:
        return "Error: refund_amount must not be negative."
    amount = _GapRecords.cents(refund_amount)
    eid = ctx.make_id("gle_", gap_waiver_id, effective_date, "termination", cancel_method, amount)
    due = _GapRecords.cents(float(w.get("refund_due_balance") or 0) + amount)
    ctx.update("gap_waivers", gap_waiver_id, status="terminated", closed_date=effective_date, refund_due_balance=due)
    ctx.create("gap_ledger", eid, gap_entry_id=eid, gap_waiver_id=gap_waiver_id, customer_id=w.get("customer_id"),
               event_type="gap_refund_calculated", entry_date=effective_date, amount=amount,
               cancel_method=cancel_method, refund_payee="not_applicable", source_entry_id="", **_EMPTY_CLAIM)
    return (f"Waiver {gap_waiver_id} terminated effective {effective_date}; refund calculation {eid} booked for "
            f"{amount:.2f} USD ({cancel_method}); refund due now {due:.2f} USD.")


@tool(owner="agent", rw="write")
def release_refund_holder_bc39910a(ctx: ToolContext, gap_waiver_id: str, source_entry_id: str, amount_paid: float) -> str:
    """Release the refund owed on a terminated or cancelled Kessler GAP waiver whose lienholder has reported the loan paid off (a loan payoff date on file) to the waiver holder, as one payment. On success a refund payment entry dated today, payable to the holder and pointing at the refund calculation it pays, is booked on the waiver's ledger for the amount given, and the waiver's refund due is cleared to 0.00. The holder can see the payment on the waiver's history. A waiver with no loan payoff date on file is refused (its refund is released to the lienholder), the source reference must name a refund calculation entry of this same waiver and the amount must be above 0.00; otherwise an Error line is returned and nothing is written.

    Args:
        gap_waiver_id: Id class — reference number of the GAP waiver whose refund is released, as returned by the GAP waiver lookup.
        source_entry_id: Id class — reference number of the refund calculation entry being paid, as shown on the waiver's ledger lookup or in the termination confirmation.
        amount_paid: Fixed-format class — the total released to the holder in USD (US dollars), a positive number with 2 decimal places, rounded half up to the cent (a half cent goes up).

    Returns:
        On success a one-line confirmation string "Refund released to holder <holder name>: payment <entry id> for <amount> USD against refund calculation <source_entry_id> on waiver <gap_waiver_id>; refund due now 0.00." where <entry id> is the new payment entry's reference number and <amount> is the payment with 2 decimals. Receiving this line means the payment is recorded; a line starting "Error:" means nothing was written.
    """
    w = _GapRecords.waiver(ctx, gap_waiver_id)
    if not w.get("loan_payoff_date"):
        return "Error: a waiver with no loan payoff date on file has its refund released to the lienholder."
    if not _GapRecords.entry(ctx, gap_waiver_id, source_entry_id, "gap_refund_calculated"):
        return "Error: source_entry_id must name a refund calculation entry of this waiver."
    if float(amount_paid) <= 0:
        return "Error: amount_paid must be above 0.00."
    amount = _GapRecords.cents(amount_paid)
    holder = ctx.find("customers", customer_id=w.get("customer_id"))
    name = holder[0].get("name") if holder else ""
    eid = ctx.make_id("gle_", gap_waiver_id, source_entry_id, "customer", amount)
    ctx.create("gap_ledger", eid, gap_entry_id=eid, gap_waiver_id=gap_waiver_id, customer_id=w.get("customer_id"),
               event_type="gap_refund_paid", entry_date=ctx.now()[:10], amount=amount, cancel_method="not_applicable",
               refund_payee="customer", source_entry_id=source_entry_id, **_EMPTY_CLAIM)
    ctx.update("gap_waivers", gap_waiver_id, refund_due_balance=0.0)
    return (f"Refund released to holder {name}: payment {eid} for {amount:.2f} USD against refund calculation "
            f"{source_entry_id} on waiver {gap_waiver_id}; refund due now 0.00.")

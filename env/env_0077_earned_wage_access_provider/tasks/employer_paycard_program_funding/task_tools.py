"""Hidden task tools of the employer_paycard_program_funding difficulty (Paystride Payroll Card Program).

Each tool performs one atomic write on an employer's Payroll Card Program and its funding account; every
figure it books is passed in by the caller exactly as published, and no tool judges eligibility, status,
timing or any other policy condition.
"""

from decimal import Decimal, ROUND_HALF_UP

from erlbench import ToolContext, tool


class _Money:
    """Exact money handling shared by the tools below (not a tool)."""

    @staticmethod
    def cents(value) -> float:
        """Round a US dollar figure half up to the cent, exactly."""
        return float(Decimal(str(value)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP))

    @staticmethod
    def program(ctx: ToolContext, paycard_program_id: str) -> dict:
        rows = ctx.find("paycard_programs", paycard_program_id=paycard_program_id)
        return rows[0] if rows else {}


@tool(owner="user", rw="write")
def send_restoring_wire_ac37b9e9(ctx: ToolContext, paycard_program_id: str, amount_usd: float) -> str:
    """The authorized employer contact sends a wire from the employer's own bank account into the funding
    account of the employer's Payroll Card Program. The wire is received at once: one funding receipt is
    added to the program's funding account history with the funding method wire, today's date and the
    current Eastern Time of receipt, tied to no pay date, and the program's funding balance rises by the
    amount sent. The employer contact sees the receipt reference and the new funding balance; nothing else
    on the program changes.

    Args:
        paycard_program_id: Id class — the reference number of the employer's Payroll Card Program that
            receives the wire, as returned by the program lookup for this employer.
        amount_usd: Fixed-format class — the amount of the wire in US dollars, a positive number with 2
            decimal places; a value with more places is rounded half up to the cent before it is booked.

    Returns:
        A confirmation line naming the funding receipt reference (a text identifier), the amount received
        (US dollars, two decimal places), the receipt date (YYYY-MM-DD) and time (HH:MM Eastern Time), and
        the program's funding balance after the wire (US dollars, two decimal places); the line beginning
        "Wire received" indicates the wire was booked.
    """
    amount = _Money.cents(amount_usd)
    prog = _Money.program(ctx, paycard_program_id)
    if amount <= 0:
        return f"No wire sent: the amount {amount:.2f} USD is not a positive figure."
    stamp = ctx.now()
    rid = ctx.make_id("pfr_", paycard_program_id, amount, stamp)
    ctx.create("paycard_funding", rid, funding_entry_id=rid, paycard_program_id=paycard_program_id,
               customer_id=prog.get("customer_id", ""), event_type="paycard_funding_receipt",
               entry_date=stamp[:10], entry_time=stamp[11:16], pay_date="", amount=amount, card_count=1,
               batch_type="none", funding_method="wire", fee_type="none", credit_reason="none",
               billing_month="", related_entry_id=None, paycard_request_id=None, card_txn_id=None)
    balance = _Money.cents(float(prog.get("funding_balance") or 0) + amount)
    ctx.update("paycard_programs", paycard_program_id, funding_balance=balance)
    return (f"Wire received: funding receipt {rid} of {amount:.2f} USD on {stamp[:10]} at {stamp[11:16]} ET; "
            f"funding balance now {balance:.2f} USD.")


@tool(owner="agent", rw="write")
def debit_program_fee_609ed260(ctx: ToolContext, paycard_program_id: str, related_entry_id: str, fee_type: str,
                               fee_amount_usd: float) -> str:
    """Debit one program fee from the funding account of an employer's Payroll Card Program. One fee entry
    of the kind given is added to the program's funding account history, dated today, pointing to the
    funding account entry that incurred it and carrying that entry's pay date when it has one, and the
    program's funding balance falls by the fee. A fee of zero, or a call naming no fee kind, debits
    nothing and leaves the program unchanged. The employer sees the fee entry and the reduced funding
    balance in the funding history.

    Args:
        paycard_program_id: Id class — the reference number of the employer's Payroll Card Program, as
            returned by the program lookup for this employer.
        related_entry_id: Id class — the reference number of the funding account entry that incurred the
            fee (the payroll batch, funding receipt, kit order or funding return), as shown in the
            program's funding account history.
        fee_type: Enum class — the kind of fee debited, exactly one of: monthly_program — the flat monthly
            program fee of a billing month; active_card — the monthly fee for the cards loaded in a billing
            month; card_kit — the kit fee of an instant-issue card kit order; kit_shipping — the standard
            shipping of a kit order; expedited_kit_shipping — the expedited shipping of a kit order;
            late_funding — the fee on a payroll batch whose funds arrived after its funding deadline;
            returned_funding — the fee on a funding payment returned unpaid; off_cycle_load — the fee on an
            off-cycle batch beyond the month's free allowance; load_file_correction — the fee for correcting
            an accepted load file; load_reversal — the fee on a load reversal request; reinstatement — the
            fee on reinstating a suspended program; early_termination — the fee on terminating within the
            minimum term; none — no fee kind, which books nothing.
        fee_amount_usd: Fixed-format class — the fee in US dollars, zero or a positive number with 2
            decimal places; a value with more places is rounded half up to the cent before it is booked.

    Returns:
        A confirmation line naming the fee entry reference (a text identifier), the fee kind, the fee
        debited (US dollars, two decimal places), the source entry reference and its pay date (YYYY-MM-DD,
        empty when it has none), and the funding balance after the debit (US dollars, two decimal places);
        the line beginning "Program fee debited" indicates the fee was booked, and a line beginning "No
        program fee debited" reports a call that changed nothing.
    """
    fee = _Money.cents(fee_amount_usd)
    prog = _Money.program(ctx, paycard_program_id)
    source = ctx.find("paycard_funding", funding_entry_id=related_entry_id)
    pay_date = source[0].get("pay_date", "") if source else ""
    if fee <= 0 or fee_type == "none":
        return f"No program fee debited: {fee_type} of {fee:.2f} USD on entry {related_entry_id} books nothing."
    stamp = ctx.now()
    rid = ctx.make_id("pff_", paycard_program_id, related_entry_id, fee_type, fee)
    ctx.create("paycard_funding", rid, funding_entry_id=rid, paycard_program_id=paycard_program_id,
               customer_id=prog.get("customer_id", ""), event_type="paycard_fee_debit", entry_date=stamp[:10],
               entry_time="00:00", pay_date=pay_date, amount=fee, card_count=1, batch_type="none",
               funding_method="none", fee_type=fee_type, credit_reason="none", billing_month="",
               related_entry_id=related_entry_id, paycard_request_id=None, card_txn_id=None)
    balance = _Money.cents(float(prog.get("funding_balance") or 0) - fee)
    ctx.update("paycard_programs", paycard_program_id, funding_balance=balance)
    return (f"Program fee debited: fee entry {rid}, {fee_type}, {fee:.2f} USD on entry {related_entry_id} "
            f"(pay date {pay_date}); funding balance now {balance:.2f} USD.")


@tool(owner="agent", rw="write")
def reinstate_suspended_program_c7549ab9(ctx: ToolContext, paycard_program_id: str, related_entry_id: str,
                                         reinstatement_fee_usd: float) -> str:
    """Reinstate an employer's suspended Payroll Card Program and debit its reinstatement fee in the same step.
    The program's status becomes live, so payroll batches funded by any allowed method post again; when the
    fee is above zero, one fee entry of the reinstatement kind is added to the funding account history,
    dated today and pointing to the funding receipt that cured the account, and the funding balance falls by
    the fee. A fee of zero reinstates the program without a fee entry. The employer sees the program live
    again and, where charged, the fee in the funding history.

    Args:
        paycard_program_id: Id class — the reference number of the employer's Payroll Card Program to
            reinstate, as returned by the program lookup for this employer.
        related_entry_id: Id class — the reference number of the funding receipt that cured the account, as
            shown in the program's funding account history.
        reinstatement_fee_usd: Fixed-format class — the reinstatement fee in US dollars, zero or a positive
            number with 2 decimal places; a value with more places is rounded half up to the cent before it is
            booked.

    Returns:
        A confirmation line giving the program reference, its new status (live), the fee entry reference
        (a text identifier, or none when no fee was debited), the fee debited (US dollars, two decimal places)
        and the funding balance afterwards (US dollars, two decimal places); the line beginning "Program
        reinstated" indicates the reinstatement was booked.
    """
    fee = _Money.cents(reinstatement_fee_usd)
    prog = _Money.program(ctx, paycard_program_id)
    ctx.update("paycard_programs", paycard_program_id, status="live")
    balance = _Money.cents(float(prog.get("funding_balance") or 0))
    rid = "none"
    if fee > 0:
        stamp = ctx.now()
        rid = ctx.make_id("pff_", paycard_program_id, related_entry_id, "reinstatement", fee)
        ctx.create("paycard_funding", rid, funding_entry_id=rid, paycard_program_id=paycard_program_id,
                   customer_id=prog.get("customer_id", ""), event_type="paycard_fee_debit", entry_date=stamp[:10],
                   entry_time="00:00", pay_date="", amount=fee, card_count=1, batch_type="none",
                   funding_method="none", fee_type="reinstatement", credit_reason="none", billing_month="",
                   related_entry_id=related_entry_id, paycard_request_id=None, card_txn_id=None)
        balance = _Money.cents(balance - fee)
        ctx.update("paycard_programs", paycard_program_id, funding_balance=balance)
    return (f"Program reinstated: {paycard_program_id} is live; fee entry {rid}, reinstatement fee {fee:.2f} USD; "
            f"funding balance now {balance:.2f} USD.")


@tool(owner="user", rw="write")
def give_termination_notice_a65df371(ctx: ToolContext, paycard_program_id: str, requester_role: str,
                                     early_termination_fee_usd: float) -> str:
    """The authorized employer contact gives the employer's written termination notice for its Payroll Card
    Program, signing it in the employer portal. The notice is recorded today: a termination notice request
    is registered as scheduled under the contact's portal role, the program's termination notice date is set
    to today, and, when the early termination fee stated with the notice is above zero, one fee entry of the
    early termination kind is added to the funding account history pointing to the notice request and the
    funding balance falls by it. Workers keep their card accounts; the program stays live until its notice
    period ends. The contact sees the notice reference, the notice date and any fee debited.

    Args:
        paycard_program_id: Id class — the reference number of the employer's Payroll Card Program being
            terminated, as returned by the program lookup for this employer.
        requester_role: Enum class — the employer portal role of the contact signing the notice, exactly
            one of these: program_owner — the contact who owns the program for the employer; payroll_admin — a payroll
            administrator on the employer portal; hr_generalist — a human resources user of the portal;
            finance_viewer — a finance user with view-only access.
        early_termination_fee_usd: Fixed-format class — the early termination fee stated with the notice, in
            US dollars, zero or a positive number with 2 decimal places; a value with more places is rounded
            half up to the cent before it is booked.

    Returns:
        A confirmation line giving the notice request reference (a text identifier), the notice date
        (YYYY-MM-DD), the requester role, the early termination fee entry reference (or none when no fee was
        debited), the fee debited (US dollars, two decimal places) and the funding balance afterwards (US
        dollars, two decimal places); the line beginning "Termination notice recorded" indicates the notice
        was booked.
    """
    fee = _Money.cents(early_termination_fee_usd)
    prog = _Money.program(ctx, paycard_program_id)
    stamp = ctx.now()
    req = ctx.make_id("prq_", paycard_program_id, "termination_notice", requester_role, stamp)
    ctx.create("paycard_requests", req, paycard_request_id=req, paycard_program_id=paycard_program_id,
               customer_id=prog.get("customer_id", ""), request_type="termination_notice", card_txn_id=None,
               reversal_reason="none", requested_amount=0.0, requested_variant_name="none",
               requester_role=requester_role, request_status="scheduled", submitted_date=stamp[:10],
               created_at=stamp)
    ctx.update("paycard_programs", paycard_program_id, termination_notice_date=stamp[:10])
    balance = _Money.cents(float(prog.get("funding_balance") or 0))
    rid = "none"
    if fee > 0:
        rid = ctx.make_id("pff_", paycard_program_id, req, "early_termination", fee)
        ctx.create("paycard_funding", rid, funding_entry_id=rid, paycard_program_id=paycard_program_id,
                   customer_id=prog.get("customer_id", ""), event_type="paycard_fee_debit", entry_date=stamp[:10],
                   entry_time="00:00", pay_date="", amount=fee, card_count=1, batch_type="none",
                   funding_method="none", fee_type="early_termination", credit_reason="none", billing_month="",
                   related_entry_id=None, paycard_request_id=req, card_txn_id=None)
        balance = _Money.cents(balance - fee)
        ctx.update("paycard_programs", paycard_program_id, funding_balance=balance)
    return (f"Termination notice recorded: request {req} on {stamp[:10]} by {requester_role}; fee entry {rid}, "
            f"early termination fee {fee:.2f} USD; funding balance now {balance:.2f} USD.")

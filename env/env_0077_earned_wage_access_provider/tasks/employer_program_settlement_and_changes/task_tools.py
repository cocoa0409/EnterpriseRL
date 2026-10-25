"""Hidden task tools for employer_program_settlement_and_changes (category program).

Each tool lands exactly one atomic write on the employer's Earned Wage Access Program
Agreement records. Tools never compute policy amounts and never check policy conditions:
the amount, the line or item concerned and every other argument are worked out by the
agent from the published program rules and the records, and passed in as declared.
"""

from decimal import Decimal, ROUND_HALF_UP

from erlbench import ToolContext, tool


class _Fmt:
    """Formatting helpers shared by the tools (static methods, not tools)."""

    @staticmethod
    def usd(x) -> float:
        """Exact half-up rounding of a money amount to the cent."""
        return float(Decimal(str(x)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP))

    @staticmethod
    def employer_of(ctx: ToolContext, agreement_id: str) -> str:
        rows = ctx.find("program_agreements", agreement_id=agreement_id)
        return rows[0].get("customer_id", "") if rows else ""

    @staticmethod
    def receivable(ctx: ToolContext, agreement_id: str) -> float:
        rows = ctx.find("program_agreements", agreement_id=agreement_id)
        return float(rows[0].get("fee_receivable") or 0) if rows else 0.0


@tool(owner="agent", rw="write")
def credit_worker_fee_overbilling_e0c50836(ctx: ToolContext, agreement_id: str, related_entry_id: str,
                                           billing_month: str, credit_reason: str, credit_amount: float) -> str:
    """Book a billing-error credit memo against one per-worker fee line (the employer_paid_pepm
    line of a monthly program invoice) for the part of that line the employer was billed in
    excess. The desk performs this on behalf of a verified employer contact. One call creates
    one credit memo with the reason given that points to the per-worker fee line named,
    carries the billing month given, and lowers the program charges the employer currently
    owes on the agreement by the credited amount. The employer sees the credit on its program
    statement against that invoice line. A receipt line beginning with "Credited" means the
    credit memo is booked.

    Args:
        agreement_id: Id class — the reference number of the employer's Earned Wage Access
            Program Agreement, read from the agreement record returned by the program agreement
            finder.
        related_entry_id: Id class — the billing entry reference number of the per-worker fee
            invoice line being credited, read from the invoice line returned by the program
            billing finder.
        billing_month: Fixed-format class — the calendar month the credited line bills, written
            as four-digit year, hyphen, two-digit month (YYYY-MM), copied from that invoice
            line; never empty.
        credit_reason: Enum class — why the credit memo is booked, exactly one of: billing_error
            — the per-worker fee line was billed above the fee owed for that month and the excess
            is credited; sla_credit — the month's measured platform availability fell below the
            commitment; go_live_delay_credit — go-live came later than the committed target for
            reasons on Paystride's side; late_charge_waiver — a late charge is waived as a
            courtesy; none — the credit is booked without a stated reason.
        credit_amount: Fixed-format class — the amount credited, in US dollars, a
            number with 2 decimal places; any further decimals are rounded half up to
            the cent by the tool.

    Returns:
        A single text line: "Credited <amount> USD on line <related_entry_id> (<billing_month>)
        as credit memo <credit memo reference>; program charges owed now <amount> USD." The
        amounts are US dollars with two decimals, the credit memo reference is the new billing
        entry reference number, and the last figure is the agreement's program charges still
        owed with the credit applied.
    """
    amt = _Fmt.usd(credit_amount)
    rid = ctx.make_id("pbl_", agreement_id, related_entry_id, billing_month, credit_reason, amt)
    ctx.create("program_billing", rid, billing_entry_id=rid, agreement_id=agreement_id,
               customer_id=_Fmt.employer_of(ctx, agreement_id), event_type="program_credit_memo",
               entry_date=ctx.now()[:10], billing_month=billing_month, invoice_line="employer_paid_pepm",
               quantity=1, amount=amt, due_date="", related_entry_id=related_entry_id,
               credit_reason=credit_reason)
    owed = _Fmt.usd(_Fmt.receivable(ctx, agreement_id) - amt)
    ctx.update("program_agreements", agreement_id, fee_receivable=owed)
    return (f"Credited {amt:.2f} USD on line {related_entry_id} ({billing_month}) as credit memo {rid}; "
            f"program charges owed now {owed:.2f} USD.")


@tool(owner="user", rw="write")
def file_sla_credit_claim_b00aa839(ctx: ToolContext, agreement_id: str, related_entry_id: str,
                                   billing_month: str, credit_reason: str, credit_amount: float) -> str:
    """File the employer's own service level credit claim for one month of measured platform
    availability below the commitment. The authorized employer contact submits the claim
    personally; it lands as a service level credit carrying the reason given that points
    to the platform fee invoice line of the claimed month, carries that billing month, and
    lowers the program charges the employer currently owes on the agreement by the credited
    amount. The employer sees the credit on its program statement against that month's
    platform fee line. A receipt line beginning with "Claim filed" means the credit is booked.

    Args:
        agreement_id: Id class — the reference number of the employer's Earned Wage Access
            Program Agreement, as given to the employer contact by the support agent from the
            agreement record.
        related_entry_id: Id class — the billing entry reference number of the platform fee
            invoice line of the claimed month, as given to the employer contact by the support
            agent from the program billing records.
        billing_month: Fixed-format class — the claimed calendar month, written as four-digit
            year, hyphen, two-digit month (YYYY-MM); never empty.
        credit_reason: Enum class — the reason the claimed credit carries, exactly one of:
            sla_credit — the claimed month's measured platform availability fell below the
            commitment; billing_error — a line of that month was billed above the amount owed;
            go_live_delay_credit — go-live came later than the committed target for reasons on
            Paystride's side; late_charge_waiver — a late charge is waived as a courtesy; none —
            the credit is filed without a stated reason.
        credit_amount: Fixed-format class — the service level credit claimed, in US dollars, a
            number with 2 decimal places as quoted by the support agent; any
            further decimals are rounded half up to the cent by the tool.

    Returns:
        A single text line: "Claim filed: service level credit <amount> USD for <billing_month>
        on line <related_entry_id>, credit reference <credit reference>; program charges
        owed now <amount> USD." The amounts are US dollars with two decimals, the credit
        reference is the new billing entry reference number, and the last figure is the
        agreement's program charges still owed with the credit applied.
    """
    amt = _Fmt.usd(credit_amount)
    rid = ctx.make_id("pbl_", agreement_id, related_entry_id, billing_month, credit_reason, amt, "sla")
    ctx.create("program_billing", rid, billing_entry_id=rid, agreement_id=agreement_id,
               customer_id=_Fmt.employer_of(ctx, agreement_id), event_type="program_sla_credit",
               entry_date=ctx.now()[:10], billing_month=billing_month, invoice_line="platform_fee",
               quantity=1, amount=amt, due_date="", related_entry_id=related_entry_id,
               credit_reason=credit_reason)
    owed = _Fmt.usd(_Fmt.receivable(ctx, agreement_id) - amt)
    ctx.update("program_agreements", agreement_id, fee_receivable=owed)
    return (f"Claim filed: service level credit {amt:.2f} USD for {billing_month} on line {related_entry_id}, "
            f"credit reference {rid}; program charges owed now {owed:.2f} USD.")


@tool(owner="agent", rw="write")
def assess_shortfall_late_charge_82f1f096(ctx: ToolContext, agreement_id: str, related_entry_id: str,
                                          charge_amount: float, due_date: str) -> str:
    """Assess one late charge for the current late-charge period on an employer-liable shortfall
    notice of the employer's Earned Wage Access Program Agreement. The desk performs this for a
    verified employer contact. One call books one late charge, invoice line late_charge, that
    points to the shortfall notice named, bills the current calendar month, carries the due date
    given, and raises the program charges the employer currently owes on the agreement by the
    charge. The employer sees the late charge on its program statement. A receipt line
    beginning with "Late charge assessed" means the charge is booked.

    Args:
        agreement_id: Id class — the reference number of the employer's Earned Wage Access
            Program Agreement, read from the agreement record returned by the program agreement
            finder.
        related_entry_id: Id class — the settlement entry reference number of the employer-liable
            shortfall notice being charged, read from the settlement entries returned by the
            program settlement finder.
        charge_amount: Fixed-format class — the late charge, in US dollars, a number with 2
            decimal places; any further decimals are rounded half up to the cent by the tool.
        due_date: Fixed-format class — the date the late charge is due, written YYYY-MM-DD as a
            calendar date with no time or time zone; never empty.

    Returns:
        A single text line: "Late charge assessed: <amount> USD on shortfall notice
        <related_entry_id>, due <due_date>, charge reference <charge reference>; program charges
        owed now <amount> USD." The amounts are US dollars with two decimals, the charge
        reference is the new billing entry reference number, and the last figure is the
        agreement's program charges owed with the charge included.
    """
    amt = _Fmt.usd(charge_amount)
    rid = ctx.make_id("pbl_", agreement_id, related_entry_id, amt, due_date, "lcs")
    ctx.create("program_billing", rid, billing_entry_id=rid, agreement_id=agreement_id,
               customer_id=_Fmt.employer_of(ctx, agreement_id), event_type="program_late_charge",
               entry_date=ctx.now()[:10], billing_month=ctx.now()[:7], invoice_line="late_charge",
               quantity=1, amount=amt, due_date=due_date, related_entry_id=related_entry_id,
               credit_reason="none")
    owed = _Fmt.usd(_Fmt.receivable(ctx, agreement_id) + amt)
    ctx.update("program_agreements", agreement_id, fee_receivable=owed)
    return (f"Late charge assessed: {amt:.2f} USD on shortfall notice {related_entry_id}, due {due_date}, "
            f"charge reference {rid}; program charges owed now {owed:.2f} USD.")


@tool(owner="agent", rw="write")
def assess_return_late_charge_9954ff84(ctx: ToolContext, agreement_id: str, related_entry_id: str,
                                       charge_amount: float, due_date: str) -> str:
    """Assess one late charge for the current late-charge period on a deduction schedule of the
    employer's Earned Wage Access Program Agreement whose remittance came back unpaid. The desk
    performs this for a verified employer contact. One call books one late charge, invoice line
    late_charge, that points to the deduction schedule named, bills the current calendar month,
    carries the due date given, and raises the program charges the employer currently owes on
    the agreement by the charge. The employer sees the late charge on its program statement. A
    receipt line beginning with "Late charge assessed" means the charge is booked.

    Args:
        agreement_id: Id class — the reference number of the employer's Earned Wage Access
            Program Agreement, read from the agreement record returned by the program agreement
            finder.
        related_entry_id: Id class — the settlement entry reference number of the deduction
            schedule being charged, read from the settlement entries returned by the program
            settlement finder.
        charge_amount: Fixed-format class — the late charge, in US dollars, a number with 2
            decimal places; any further decimals are rounded half up to the cent by the tool.
        due_date: Fixed-format class — the date the late charge is due, written YYYY-MM-DD as a
            calendar date with no time or time zone; never empty.

    Returns:
        A single text line: "Late charge assessed: <amount> USD on deduction schedule
        <related_entry_id>, due <due_date>, charge reference <charge reference>; program charges
        owed now <amount> USD." The amounts are US dollars with two decimals, the charge
        reference is the new billing entry reference number, and the last figure is the
        agreement's program charges owed with the charge included.
    """
    amt = _Fmt.usd(charge_amount)
    rid = ctx.make_id("pbl_", agreement_id, related_entry_id, amt, due_date, "lcr")
    ctx.create("program_billing", rid, billing_entry_id=rid, agreement_id=agreement_id,
               customer_id=_Fmt.employer_of(ctx, agreement_id), event_type="program_late_charge",
               entry_date=ctx.now()[:10], billing_month=ctx.now()[:7], invoice_line="late_charge",
               quantity=1, amount=amt, due_date=due_date, related_entry_id=related_entry_id,
               credit_reason="none")
    owed = _Fmt.usd(_Fmt.receivable(ctx, agreement_id) + amt)
    ctx.update("program_agreements", agreement_id, fee_receivable=owed)
    return (f"Late charge assessed: {amt:.2f} USD on deduction schedule {related_entry_id}, due {due_date}, "
            f"charge reference {rid}; program charges owed now {owed:.2f} USD.")


@tool(owner="user", rw="write")
def sign_termination_notice_c67c1163(ctx: ToolContext, agreement_id: str, early_termination_fee: float,
                                     due_date: str) -> str:
    """Give the employer's own written notice to terminate its Earned Wage Access Program
    Agreement, signed by the authorized employer contact personally, accepting the early
    termination fee quoted for it. One call records today as the termination notice date, moves
    the agreement to terminating status, and bills the early termination fee as one invoice line
    early_termination_fee for the current calendar month with the due date given, raising the
    program charges the employer currently owes by that fee; a fee of zero is recorded with the
    notice and no fee line is billed. The employer sees the agreement as terminating and any fee on
    its program statement. A receipt line beginning with "Notice recorded" means the notice and any
    fee are booked.

    Args:
        agreement_id: Id class — the reference number of the employer's Earned Wage Access
            Program Agreement, as given to the employer contact by the support agent from the
            agreement record.
        early_termination_fee: Fixed-format class — the early termination fee accepted with the
            notice, in US dollars, a number with 2 decimal places as quoted by the support agent;
            any further decimals are rounded half up to the cent by the tool.
        due_date: Fixed-format class — the date the early termination fee is due, written
            YYYY-MM-DD as a calendar date with no time or time zone, as given by the support
            agent; never empty.

    Returns:
        A single text line: "Notice recorded <notice date>: agreement <agreement_id> is
        terminating; early termination fee <amount> USD billed as line <line reference>, due
        <due_date>; program charges owed now <amount> USD." When the fee is zero the line reads
        "Notice recorded <notice date>: agreement <agreement_id> is terminating; no early
        termination fee is billed; program charges owed now <amount> USD." The notice date is
        YYYY-MM-DD, the amounts are US dollars with two decimals, the line reference is the new
        billing entry reference number, and the last figure is the agreement's program charges
        owed with any fee included.
    """
    amt = _Fmt.usd(early_termination_fee)
    today = ctx.now()[:10]
    ctx.update("program_agreements", agreement_id, status="terminating", termination_notice_date=today)
    if amt == 0:
        owed = _Fmt.usd(_Fmt.receivable(ctx, agreement_id))
        return (f"Notice recorded {today}: agreement {agreement_id} is terminating; no early termination fee is billed; "
                f"program charges owed now {owed:.2f} USD.")
    rid = ctx.make_id("pbl_", agreement_id, amt, due_date, "etf")
    ctx.create("program_billing", rid, billing_entry_id=rid, agreement_id=agreement_id,
               customer_id=_Fmt.employer_of(ctx, agreement_id), event_type="program_invoice_line",
               entry_date=today, billing_month=ctx.now()[:7], invoice_line="early_termination_fee",
               quantity=1, amount=amt, due_date=due_date, related_entry_id=None, credit_reason="none")
    owed = _Fmt.usd(_Fmt.receivable(ctx, agreement_id) + amt)
    ctx.update("program_agreements", agreement_id, fee_receivable=owed)
    return (f"Notice recorded {today}: agreement {agreement_id} is terminating; early termination fee {amt:.2f} USD "
            f"billed as line {rid}, due {due_date}; program charges owed now {owed:.2f} USD.")

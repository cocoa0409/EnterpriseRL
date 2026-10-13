"""Hidden task tools for the prime_enrollment_fees_and_pcm difficulty of
env_0055_military_health_plan_administrator (Westbridge Military Health Services, TRICARE West Region).

Each tool performs one atomic posting on the enrollment-fee account of a fee-bearing TRICARE Prime
enrollment: an installment charge, a payment, a proration credit or a refund. Every posting also moves
the enrollment's running fee balance by the amount posted, so the balance stays equal to the account
entries. The values passed in are worked out by the caller from the published policies and the
records; no tool judges eligibility, ordering or amounts.
"""

from erlbench import ToolContext, tool


class _Account:
    """Read helpers and balance arithmetic shared by the tools below (not tools themselves); every write is made in the tool body."""

    @staticmethod
    def entry(ctx: ToolContext, prime_fee_entry_id: str) -> dict:
        """The fee-account entry with this reference number, or {} when none is found."""
        rows = ctx.find("prime_fee_ledger", prime_fee_entry_id=prime_fee_entry_id)
        return dict(rows[0]) if rows else {}

    @staticmethod
    def enrollment(ctx: ToolContext, prime_enrollment_id: str) -> dict:
        """The Prime enrollment with this reference number, or {} when none is found."""
        rows = ctx.find("prime_enrollments", prime_enrollment_id=prime_enrollment_id)
        return dict(rows[0]) if rows else {}

    @staticmethod
    def new_balance(enrollment: dict, delta: float) -> float:
        """The enrollment's running fee balance after adding delta (no write)."""
        return round(float(enrollment.get("fee_balance_due") or 0.0) + float(delta), 2)


@tool(owner="agent", rw="write")
def post_catch_up_installment_4baf2609(ctx: ToolContext, prime_enrollment_id: str, coverage_period_start: str,
                                       coverage_period_end: str, amount: float) -> dict:
    """Post a catch-up installment charge on the fee account of a fee-bearing TRICARE Prime enrollment
    whose restored coverage holds months that no installment ever billed. The agent posts it for the
    verified caller: one installment charge is added to the enrollment's fee account with the coverage
    period and amount given here, it takes the installment frequency of the enrollment's payment
    arrangement and today's posting date, and the enrollment's fee balance owed rises by the amount. The
    new charge then shows on the fee account as an open installment.

    Args:
        prime_enrollment_id: Id class — the reference number of the fee-bearing TRICARE Prime
            enrollment the catch-up is billed to, read from the Prime enrollment lookup for the
            beneficiary.
        coverage_period_start: Fixed-format class — the first day of the first month the catch-up
            bills, a calendar date written YYYY-MM-DD.
        coverage_period_end: Fixed-format class — the last day of the last month the catch-up bills, a
            calendar date written YYYY-MM-DD.
        amount: Fixed-format class — the catch-up charge, in USD (US dollars) as a plain number with 2
            decimal places (cents, rounded half up to the cent), 0.00 or more.

    Returns:
        A dict with: "posted" (bool, true when the charge was added), "prime_fee_entry_id" (str, the new
        charge's reference number, text starting "pfc_"), "prime_enrollment_id" (str, the enrollment
        billed), "coverage_period_start" and "coverage_period_end" (str, YYYY-MM-DD, the coverage
        period charged), "installment_frequency" (str, monthly, quarterly or annual, copied from the
        enrollment's payment arrangement), "amount" (float, USD with 2 decimals) and
        "fee_balance_due" (float, the enrollment's fee balance owed after the charge, USD with 2
        decimals; negative means a credit owed to the beneficiary).
    """
    enr = _Account.enrollment(ctx, prime_enrollment_id)
    amt = round(float(amount), 2)
    rid = ctx.make_id("pfc_", prime_enrollment_id, coverage_period_start, coverage_period_end, amount)
    freq = enr.get("payment_frequency", "not_applicable")
    ctx.create("prime_fee_ledger", rid, prime_fee_entry_id=rid, prime_enrollment_id=prime_enrollment_id,
               customer_id=enr.get("customer_id", ""), event_type="prime_fee_charge",
               coverage_period_start=coverage_period_start, coverage_period_end=coverage_period_end,
               installment_frequency=freq, amount=amt, posted_date=ctx.now()[:10],
               payment_method="not_applicable", adjustment_reason="not_applicable", related_fee_entry_id="")
    balance = _Account.new_balance(enr, amt)
    if enr:
        ctx.update("prime_enrollments", enr["prime_enrollment_id"], fee_balance_due=balance)
    return {"posted": True, "prime_fee_entry_id": rid, "prime_enrollment_id": prime_enrollment_id,
            "coverage_period_start": coverage_period_start, "coverage_period_end": coverage_period_end,
            "installment_frequency": freq, "amount": amt, "fee_balance_due": balance}


@tool(owner="agent", rw="write")
def refund_duplicate_payment_360f0d4a(ctx: ToolContext, related_fee_entry_id: str, amount: float) -> dict:
    """Refund part or all of a payment that was posted twice against one installment of a TRICARE
    Prime enrollment-fee account. The agent issues it for the verified caller: one refund is added to
    the fee account against the payment named here, it goes back through the same payment method that
    payment used and carries today's posting date, and the enrollment's fee balance owed rises by the
    amount refunded. The refund then shows on the fee account against that payment.

    Args:
        related_fee_entry_id: Id class — the reference number of the payment being refunded, read from
            the fee-account lookup for the enrollment (a payment entry, not the installment charge).
        amount: Fixed-format class — the amount refunded, in USD (US dollars) as a plain number with 2
            decimal places (cents, rounded half up to the cent), 0.00 or more.

    Returns:
        A dict with: "refunded" (bool, true when the refund was added), "prime_fee_entry_id" (str, the
        refund's reference number, text starting "pfr_"), "related_fee_entry_id" (str, the payment
        refunded), "payment_method" (str, the method the refund goes back through, copied from that
        payment), "amount" (float, USD with 2 decimals) and "fee_balance_due" (float, the enrollment's
        fee balance owed after the refund, USD with 2 decimals; negative means a credit owed to the
        beneficiary).
    """
    pay = _Account.entry(ctx, related_fee_entry_id)
    enr = _Account.enrollment(ctx, pay.get("prime_enrollment_id", ""))
    amt = round(float(amount), 2)
    method = pay.get("payment_method", "not_applicable")
    rid = ctx.make_id("pfr_", related_fee_entry_id, amount)
    ctx.create("prime_fee_ledger", rid, prime_fee_entry_id=rid, prime_enrollment_id=pay.get("prime_enrollment_id", ""),
               customer_id=pay.get("customer_id", ""), event_type="prime_fee_refund", coverage_period_start="",
               coverage_period_end="", installment_frequency="not_applicable", amount=amt,
               posted_date=ctx.now()[:10], payment_method=method, adjustment_reason="not_applicable",
               related_fee_entry_id=related_fee_entry_id)
    balance = _Account.new_balance(enr, amt)
    if enr:
        ctx.update("prime_enrollments", enr["prime_enrollment_id"], fee_balance_due=balance)
    return {"refunded": True, "prime_fee_entry_id": rid, "related_fee_entry_id": related_fee_entry_id,
            "payment_method": method, "amount": amt, "fee_balance_due": balance}


@tool(owner="user", rw="write")
def pay_current_installment_by_bank_draft_694809d0(ctx: ToolContext, prime_enrollment_id: str,
                                                   related_fee_entry_id: str, amount: float) -> dict:
    """The beneficiary authorizes a one-time bank draft (electronic funds transfer) that pays toward one
    installment charge on the fee account of their TRICARE Prime enrollment. One payment is added to the
    fee account against the installment named here, made by electronic funds transfer with today's
    posting date, and the enrollment's fee balance owed falls by the amount paid. The beneficiary sees
    the payment confirmation with its reference number.

    Args:
        prime_enrollment_id: Id class — the reference number of the beneficiary's fee-bearing TRICARE
            Prime enrollment whose account is paid, read by the agent from the Prime enrollment lookup
            and given to the beneficiary.
        related_fee_entry_id: Id class — the reference number of the installment charge being paid,
            read by the agent from the fee-account lookup for the enrollment and given to the
            beneficiary.
        amount: Fixed-format class — the amount paid, in USD (US dollars) as a plain number with 2
            decimal places (cents, rounded half up to the cent), greater than 0.00.

    Returns:
        A dict with: "paid" (bool, true when the payment was taken), "prime_fee_entry_id" (str, the
        payment's reference number, text starting "pfp_"), "related_fee_entry_id" (str, the installment
        charge paid), "payment_method" (str, always "electronic_funds_transfer"), "amount" (float, USD
        with 2 decimals) and "fee_balance_due" (float, the enrollment's fee balance owed after the
        payment, USD with 2 decimals; negative means a credit owed to the beneficiary).
    """
    enr = _Account.enrollment(ctx, prime_enrollment_id)
    amt = round(float(amount), 2)
    rid = ctx.make_id("pfp_", prime_enrollment_id, related_fee_entry_id, amount, "eft")
    ctx.create("prime_fee_ledger", rid, prime_fee_entry_id=rid, prime_enrollment_id=prime_enrollment_id,
               customer_id=enr.get("customer_id", ""), event_type="prime_fee_payment", coverage_period_start="",
               coverage_period_end="", installment_frequency="not_applicable", amount=amt,
               posted_date=ctx.now()[:10], payment_method="electronic_funds_transfer",
               adjustment_reason="not_applicable", related_fee_entry_id=related_fee_entry_id)
    balance = _Account.new_balance(enr, -amt)
    if enr:
        ctx.update("prime_enrollments", enr["prime_enrollment_id"], fee_balance_due=balance)
    return {"paid": True, "prime_fee_entry_id": rid, "related_fee_entry_id": related_fee_entry_id,
            "payment_method": "electronic_funds_transfer", "amount": amt, "fee_balance_due": balance}


@tool(owner="agent", rw="write")
def run_draft_on_file_method_99529347(ctx: ToolContext, prime_enrollment_id: str, related_fee_entry_id: str,
                                      amount: float) -> dict:
    """Draw a payment toward one installment charge of a TRICARE Prime enrollment-fee account through the
    payment method the enrollment keeps on file (its recurring card, electronic funds transfer account or
    allotment). The agent runs it for the verified caller: one payment is added to the fee account
    against the installment named here, made through the enrollment's payment method on file with
    today's posting date, and the enrollment's fee balance owed falls by the amount drawn. The draft then
    shows on the fee account against that installment.

    Args:
        prime_enrollment_id: Id class — the reference number of the fee-bearing TRICARE Prime
            enrollment whose payment method on file is drawn, read from the Prime enrollment lookup for
            the beneficiary.
        related_fee_entry_id: Id class — the reference number of the installment charge the draft pays
            toward, read from the fee-account lookup for the enrollment.
        amount: Fixed-format class — the amount drawn, in USD (US dollars) as a plain number with 2
            decimal places (cents, rounded half up to the cent), greater than 0.00.

    Returns:
        A dict with: "drawn" (bool, true when the draft was taken), "prime_fee_entry_id" (str, the
        payment's reference number, text starting "pfd_"), "related_fee_entry_id" (str, the installment
        charge paid toward), "payment_method" (str, the enrollment's payment method on file),
        "amount" (float, USD with 2 decimals) and "fee_balance_due" (float, the enrollment's fee balance
        owed after the draft, USD with 2 decimals; negative means a credit owed to the beneficiary).
    """
    enr = _Account.enrollment(ctx, prime_enrollment_id)
    amt = round(float(amount), 2)
    method = enr.get("payment_method", "not_applicable")
    rid = ctx.make_id("pfd_", prime_enrollment_id, related_fee_entry_id, amount)
    ctx.create("prime_fee_ledger", rid, prime_fee_entry_id=rid, prime_enrollment_id=prime_enrollment_id,
               customer_id=enr.get("customer_id", ""), event_type="prime_fee_payment", coverage_period_start="",
               coverage_period_end="", installment_frequency="not_applicable", amount=amt,
               posted_date=ctx.now()[:10], payment_method=method, adjustment_reason="not_applicable",
               related_fee_entry_id=related_fee_entry_id)
    balance = _Account.new_balance(enr, -amt)
    if enr:
        ctx.update("prime_enrollments", enr["prime_enrollment_id"], fee_balance_due=balance)
    return {"drawn": True, "prime_fee_entry_id": rid, "related_fee_entry_id": related_fee_entry_id,
            "payment_method": method, "amount": amt, "fee_balance_due": balance}


@tool(owner="agent", rw="write")
def post_unused_month_credit_3ad1a050(ctx: ToolContext, related_fee_entry_id: str, coverage_period_start: str,
                                      coverage_period_end: str, adjustment_reason: str, amount: float) -> dict:
    """Post a proration credit for unused months against a paid installment charge of a TRICARE Prime
    enrollment that has ended. The agent posts it for the verified caller: one credit is added to the
    enrollment's fee account against the installment charge named here, with the credited coverage
    period, credit reason and amount given here and today's posting date, and the enrollment's fee
    balance owed falls by the amount credited. The credit then shows on the fee account against that
    installment.

    Args:
        related_fee_entry_id: Id class — the reference number of the paid installment charge being
            credited, read from the fee-account lookup for the ended enrollment (an installment charge,
            not a payment).
        coverage_period_start: Fixed-format class — the first day of the first month credited, a
            calendar date written YYYY-MM-DD.
        coverage_period_end: Fixed-format class — the last day of the last month credited, a calendar
            date written YYYY-MM-DD.
        adjustment_reason: Enum class — why the enrollment's fee is credited, exactly one of:
            "beneficiary_disenrollment" (the beneficiary ended the enrollment),
            "loss_of_eligibility" (the beneficiary lost eligibility for the plan),
            "region_transfer" (the enrollment moved to another TRICARE region),
            "death_of_beneficiary" (the beneficiary died),
            "not_applicable" (no credit-eligible reason is recorded for the credit).
        amount: Fixed-format class — the credit, in USD (US dollars) as a plain number with 2 decimal
            places (cents, rounded half up to the cent), 0.00 or more.

    Returns:
        A dict with: "credited" (bool, true when the credit was added), "prime_fee_entry_id" (str, the
        credit's reference number, text starting "pfk_"), "related_fee_entry_id" (str, the installment
        charge credited), "coverage_period_start" and "coverage_period_end" (str, YYYY-MM-DD, the
        credited period), "adjustment_reason" (str, the credit reason given), "amount" (float, USD with 2
        decimals) and "fee_balance_due" (float, the enrollment's fee balance owed after the credit, USD
        with 2 decimals; negative means a credit owed to the beneficiary).
    """
    charge = _Account.entry(ctx, related_fee_entry_id)
    enr = _Account.enrollment(ctx, charge.get("prime_enrollment_id", ""))
    amt = round(float(amount), 2)
    rid = ctx.make_id("pfk_", related_fee_entry_id, coverage_period_start, coverage_period_end, adjustment_reason, amount)
    ctx.create("prime_fee_ledger", rid, prime_fee_entry_id=rid, prime_enrollment_id=charge.get("prime_enrollment_id", ""),
               customer_id=charge.get("customer_id", ""), event_type="prime_fee_credit",
               coverage_period_start=coverage_period_start, coverage_period_end=coverage_period_end,
               installment_frequency="not_applicable", amount=amt, posted_date=ctx.now()[:10],
               payment_method="not_applicable", adjustment_reason=adjustment_reason,
               related_fee_entry_id=related_fee_entry_id)
    balance = _Account.new_balance(enr, -amt)
    if enr:
        ctx.update("prime_enrollments", enr["prime_enrollment_id"], fee_balance_due=balance)
    return {"credited": True, "prime_fee_entry_id": rid, "related_fee_entry_id": related_fee_entry_id,
            "coverage_period_start": coverage_period_start, "coverage_period_end": coverage_period_end,
            "adjustment_reason": adjustment_reason, "amount": amt, "fee_balance_due": balance}


@tool(owner="agent", rw="write")
def refund_first_installment_duplicate_7d2e91c4(ctx: ToolContext, related_fee_entry_id: str, amount: float) -> dict:
    """Refund part or all of a payment that paid the first installment of a new TRICARE Prime enrollment a
    second time. The agent issues it for the verified caller: one refund is added to the enrollment's fee
    account against the payment named here, it goes back through the same payment method that payment
    used and carries today's posting date, and the enrollment's fee balance owed rises by the amount
    refunded. The refund then shows on the fee account against that payment.

    Args:
        related_fee_entry_id: Id class — the reference number of the payment being refunded, read from
            the fee-account lookup for the enrollment (a payment entry, not the installment charge).
        amount: Fixed-format class — the amount refunded, in USD (US dollars) as a plain number with 2
            decimal places (cents, rounded half up to the cent), 0.00 or more.

    Returns:
        A dict with: "refunded" (bool, true when the refund was added), "prime_fee_entry_id" (str, the
        refund's reference number, text starting "pfu_"), "related_fee_entry_id" (str, the payment
        refunded), "payment_method" (str, the method the refund goes back through, copied from that
        payment), "amount" (float, USD with 2 decimals) and "fee_balance_due" (float, the enrollment's
        fee balance owed after the refund, USD with 2 decimals; negative means a credit owed to the
        beneficiary).
    """
    pay = _Account.entry(ctx, related_fee_entry_id)
    enr = _Account.enrollment(ctx, pay.get("prime_enrollment_id", ""))
    amt = round(float(amount), 2)
    method = pay.get("payment_method", "not_applicable")
    rid = ctx.make_id("pfu_", related_fee_entry_id, amount)
    ctx.create("prime_fee_ledger", rid, prime_fee_entry_id=rid, prime_enrollment_id=pay.get("prime_enrollment_id", ""),
               customer_id=pay.get("customer_id", ""), event_type="prime_fee_refund", coverage_period_start="",
               coverage_period_end="", installment_frequency="not_applicable", amount=amt,
               posted_date=ctx.now()[:10], payment_method=method, adjustment_reason="not_applicable",
               related_fee_entry_id=related_fee_entry_id)
    balance = _Account.new_balance(enr, amt)
    if enr:
        ctx.update("prime_enrollments", enr["prime_enrollment_id"], fee_balance_due=balance)
    return {"refunded": True, "prime_fee_entry_id": rid, "related_fee_entry_id": related_fee_entry_id,
            "payment_method": method, "amount": amt, "fee_balance_due": balance}


@tool(owner="agent", rw="write")
def post_first_installment_supplement_bc87e2fc(ctx: ToolContext, prime_enrollment_id: str, coverage_period_start: str,
                                               coverage_period_end: str, amount: float) -> dict:
    """Post a supplement to the first installment on the fee account of a fee-bearing TRICARE Prime
    enrollment, billing months its first installment owes that its first installment charge does not
    cover. The agent posts it for the verified caller: one installment charge is added to the
    enrollment's fee account with the coverage period and amount given here, it takes the installment
    frequency of the enrollment's payment arrangement and today's posting date, and the enrollment's fee
    balance owed rises by the amount. The supplement then shows on the fee account as an open
    installment.

    Args:
        prime_enrollment_id: Id class — the reference number of the fee-bearing TRICARE Prime
            enrollment the supplement is billed to, read from the Prime enrollment lookup for the
            beneficiary.
        coverage_period_start: Fixed-format class — the first day of the first month the supplement
            bills, a calendar date written YYYY-MM-DD.
        coverage_period_end: Fixed-format class — the last day of the last month the supplement bills,
            a calendar date written YYYY-MM-DD.
        amount: Fixed-format class — the supplement charge, in USD (US dollars) as a plain number with 2
            decimal places (cents, rounded half up to the cent), 0.00 or more.

    Returns:
        A dict with: "posted" (bool, true when the charge was added), "prime_fee_entry_id" (str, the
        supplement's reference number, text starting "pfs_"), "prime_enrollment_id" (str, the
        enrollment billed), "coverage_period_start" and "coverage_period_end" (str, YYYY-MM-DD, the
        coverage period charged), "installment_frequency" (str, monthly, quarterly or annual, copied
        from the enrollment's payment arrangement), "amount" (float, USD with 2 decimals) and
        "fee_balance_due" (float, the enrollment's fee balance owed after the charge, USD with 2
        decimals; negative means a credit owed to the beneficiary).
    """
    enr = _Account.enrollment(ctx, prime_enrollment_id)
    amt = round(float(amount), 2)
    rid = ctx.make_id("pfs_", prime_enrollment_id, coverage_period_start, coverage_period_end, amount)
    freq = enr.get("payment_frequency", "not_applicable")
    ctx.create("prime_fee_ledger", rid, prime_fee_entry_id=rid, prime_enrollment_id=prime_enrollment_id,
               customer_id=enr.get("customer_id", ""), event_type="prime_fee_charge",
               coverage_period_start=coverage_period_start, coverage_period_end=coverage_period_end,
               installment_frequency=freq, amount=amt, posted_date=ctx.now()[:10],
               payment_method="not_applicable", adjustment_reason="not_applicable", related_fee_entry_id="")
    balance = _Account.new_balance(enr, amt)
    if enr:
        ctx.update("prime_enrollments", enr["prime_enrollment_id"], fee_balance_due=balance)
    return {"posted": True, "prime_fee_entry_id": rid, "prime_enrollment_id": prime_enrollment_id,
            "coverage_period_start": coverage_period_start, "coverage_period_end": coverage_period_end,
            "installment_frequency": freq, "amount": amt, "fee_balance_due": balance}


@tool(owner="user", rw="write")
def pay_first_installment_by_bank_draft_5f63627f(ctx: ToolContext, prime_enrollment_id: str,
                                                 related_fee_entry_id: str, amount: float) -> dict:
    """The beneficiary authorizes a one-time bank draft (electronic funds transfer) that pays toward the
    first installment of their TRICARE Prime enrollment. One payment is added to the enrollment's fee
    account against the installment charge named here, made by electronic funds transfer with today's
    posting date, and the enrollment's fee balance owed falls by the amount paid. The beneficiary sees
    the payment confirmation with its reference number.

    Args:
        prime_enrollment_id: Id class — the reference number of the beneficiary's fee-bearing TRICARE
            Prime enrollment whose account is paid, read by the agent from the Prime enrollment lookup
            and given to the beneficiary.
        related_fee_entry_id: Id class — the reference number of the installment charge the payment is
            posted against, read by the agent from the fee-account lookup for the enrollment or from the
            receipt of that charge's posting, and given to the beneficiary.
        amount: Fixed-format class — the amount paid, in USD (US dollars) as a plain number with 2
            decimal places (cents, rounded half up to the cent), greater than 0.00.

    Returns:
        A dict with: "paid" (bool, true when the payment was taken), "prime_fee_entry_id" (str, the
        payment's reference number, text starting "pfi_"), "related_fee_entry_id" (str, the installment
        charge paid against), "payment_method" (str, always "electronic_funds_transfer"), "amount"
        (float, USD with 2 decimals) and "fee_balance_due" (float, the enrollment's fee balance owed
        after the payment, USD with 2 decimals; negative means a credit owed to the beneficiary).
    """
    enr = _Account.enrollment(ctx, prime_enrollment_id)
    amt = round(float(amount), 2)
    rid = ctx.make_id("pfi_", prime_enrollment_id, related_fee_entry_id, amount, "eft")
    ctx.create("prime_fee_ledger", rid, prime_fee_entry_id=rid, prime_enrollment_id=prime_enrollment_id,
               customer_id=enr.get("customer_id", ""), event_type="prime_fee_payment", coverage_period_start="",
               coverage_period_end="", installment_frequency="not_applicable", amount=amt,
               posted_date=ctx.now()[:10], payment_method="electronic_funds_transfer",
               adjustment_reason="not_applicable", related_fee_entry_id=related_fee_entry_id)
    balance = _Account.new_balance(enr, -amt)
    if enr:
        ctx.update("prime_enrollments", enr["prime_enrollment_id"], fee_balance_due=balance)
    return {"paid": True, "prime_fee_entry_id": rid, "related_fee_entry_id": related_fee_entry_id,
            "payment_method": "electronic_funds_transfer", "amount": amt, "fee_balance_due": balance}

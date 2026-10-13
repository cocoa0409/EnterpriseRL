"""Hidden task tools of the cni_contract_care difficulty (Commercial and Industrial Electricity Contracts).

Each tool makes exactly one atomic write on a C&I contract's ledger with the values the caller passes.
No tool checks a contract's status, an earlier entry, a prerequisite or an amount: those judgements
belong to the person handling the call, from the published policy and the records.
"""

from erlbench import ToolContext, tool


@tool(owner="user", rw="write")
def post_termination_security_b7051944(ctx: ToolContext, cni_contract_id: str, amount_usd: float,
                                       credit_grade_basis: str) -> str:
    """The business's authorized signatory remits additional security on one commercial and
    industrial electricity contract from the business's own bank account, today. One call
    records one security deposit receipt of the stated dollar amount against that contract,
    dated today; the security Beacon Ridge holds on the contract rises by exactly that amount
    and the receipt then appears among the contract's security deposits. The receipt records
    no months of supply cost, because this security is not sized in months. Nothing else on
    the contract changes.

    Args:
        cni_contract_id: Id class — the commercial and industrial contract number of the
            contract the security is posted on, as shown on the contract record returned by the
            contract lookup.
        amount_usd: Fixed-format class — the dollar amount remitted, in USD, a positive number
            rounded half up to 2 decimal places; it is stored exactly as passed.
        credit_grade_basis: Enum class — the commercial credit grade written on the receipt,
            copied from the grade recorded on the contract's existing security deposit receipt:
            A when that receipt records grade A; B when it records grade B; C when it records
            grade C; not_rated when it records not_rated; "" (empty) only when the contract has
            no existing receipt to copy a grade from.

    Returns:
        A dict confirming the receipt: cni_deposit_id (str, the reference number of the new
        security deposit receipt), cni_contract_id (str, the contract secured), amount_usd
        (float, the amount recorded, 2 decimal places), posted_date (str, YYYY-MM-DD, today) and
        status (str, always "recorded", meaning the security now counts toward what Beacon
        Ridge holds on the contract).
    """
    found = ctx.find("cni_contracts", cni_contract_id=cni_contract_id)
    owner = found[0].get("customer_id") if found else None
    amount = round(float(amount_usd), 2)
    rid = ctx.make_id("cnd_", cni_contract_id, amount, credit_grade_basis)
    ctx.create("cni_deposits", rid, cni_deposit_id=rid, cni_contract_id=cni_contract_id,
               customer_id=owner, event_type="cni_deposit_post",
               amount_usd=amount, deposit_months=0, credit_grade_basis=credit_grade_basis,
               posted_date=ctx.now()[:10], source_deposit_id=None)
    return str({"cni_deposit_id": rid, "cni_contract_id": cni_contract_id, "amount_usd": amount,
                "posted_date": ctx.now()[:10], "status": "recorded"})


@tool(owner="agent", rw="write")
def bill_noticed_termination_damages_6fb56a64(ctx: ToolContext, cni_contract_id: str, amount_usd: float,
                                              etf_remaining_kwh: int) -> str:
    """Bill the liquidated damages for a commercial and industrial electricity contract whose
    authorized signatory gave written notice of early termination during the term. One call
    adds one early termination fee line to that contract's bill, dated today, carrying the
    dollar amount and the remaining contracted kWh passed; the net charges billed on the
    contract rise by that amount and the line then appears among the contract's bill lines.
    The contract's status and dates are not changed.

    Args:
        cni_contract_id: Id class — the commercial and industrial contract number of the
            terminating contract, as shown on the contract record returned by the contract
            lookup.
        amount_usd: Fixed-format class — the damages billed, in USD, a positive number rounded
            half up to 2 decimal places; it is stored exactly as passed.
        etf_remaining_kwh: Fixed-format class — the remaining contracted kWh the damages were
            measured on, an integer kWh count with no decimals.

    Returns:
        A dict confirming the line: cni_billing_id (str, the reference number of the new bill
        line), cni_contract_id (str, the contract billed), line_type (str, always
        "early_termination_fee"), amount_usd (float, 2 decimal places), etf_remaining_kwh (int)
        and posted_date (str, YYYY-MM-DD, today). A returned cni_billing_id means the line is
        on the contract's bill.
    """
    found = ctx.find("cni_contracts", cni_contract_id=cni_contract_id)
    owner = found[0].get("customer_id") if found else None
    amount = round(float(amount_usd), 2)
    kwh = int(etf_remaining_kwh)
    rid = ctx.make_id("cnb_", cni_contract_id, "noticed", amount, kwh)
    ctx.create("cni_billing", rid, cni_billing_id=rid, cni_contract_id=cni_contract_id,
               customer_id=owner, event_type="cni_etf_charge",
               line_type="early_termination_fee", billing_period_start="", billing_period_end="",
               billing_days=0, usage_kwh=0, rate_cents_kwh=0.0, tag_kw=0.0, tag_rate_usd_mw_day=0.0,
               amount_usd=amount, posted_date=ctx.now()[:10], source_billing_id=None,
               etf_remaining_kwh=kwh)
    return str({"cni_billing_id": rid, "cni_contract_id": cni_contract_id,
                "line_type": "early_termination_fee", "amount_usd": amount,
                "etf_remaining_kwh": kwh, "posted_date": ctx.now()[:10]})


@tool(owner="agent", rw="write")
def bill_preflow_termination_damages_230b7c5e(ctx: ToolContext, cni_contract_id: str, amount_usd: float,
                                              etf_remaining_kwh: int) -> str:
    """Bill the liquidated damages for a commercial and industrial electricity contract that was
    signed and then terminated by the business before Beacon Ridge supply ever started at the
    facility. One call adds one early termination fee line to that contract's bill, dated
    today, carrying the dollar amount and the contracted kWh passed; the net charges billed on
    the contract rise by that amount and the line then appears among the contract's bill
    lines. The contract's status and dates are not changed.

    Args:
        cni_contract_id: Id class — the commercial and industrial contract number of the
            contract terminated before supply, as shown on the contract record returned by the
            contract lookup.
        amount_usd: Fixed-format class — the damages billed, in USD, a positive number rounded
            half up to 2 decimal places; it is stored exactly as passed.
        etf_remaining_kwh: Fixed-format class — the contracted kWh the damages were measured
            on, an integer kWh count with no decimals.

    Returns:
        A dict confirming the line: cni_billing_id (str, the reference number of the new bill
        line), cni_contract_id (str, the contract billed), line_type (str, always
        "early_termination_fee"), amount_usd (float, 2 decimal places), etf_remaining_kwh (int)
        and posted_date (str, YYYY-MM-DD, today). A returned cni_billing_id means the line is
        on the contract's bill.
    """
    found = ctx.find("cni_contracts", cni_contract_id=cni_contract_id)
    owner = found[0].get("customer_id") if found else None
    amount = round(float(amount_usd), 2)
    kwh = int(etf_remaining_kwh)
    rid = ctx.make_id("cnb_", cni_contract_id, "preflow", amount, kwh)
    ctx.create("cni_billing", rid, cni_billing_id=rid, cni_contract_id=cni_contract_id,
               customer_id=owner, event_type="cni_etf_charge",
               line_type="early_termination_fee", billing_period_start="", billing_period_end="",
               billing_days=0, usage_kwh=0, rate_cents_kwh=0.0, tag_kw=0.0, tag_rate_usd_mw_day=0.0,
               amount_usd=amount, posted_date=ctx.now()[:10], source_billing_id=None,
               etf_remaining_kwh=kwh)
    return str({"cni_billing_id": rid, "cni_contract_id": cni_contract_id,
                "line_type": "early_termination_fee", "amount_usd": amount,
                "etf_remaining_kwh": kwh, "posted_date": ctx.now()[:10]})


@tool(owner="user", rw="write")
def remit_review_deposit_f4180914(ctx: ToolContext, cni_contract_id: str, amount_usd: float,
                                  deposit_months: int, credit_grade_basis: str) -> str:
    """The business's authorized signatory remits the additional security deposit requested by the
    anniversary review of one active commercial and industrial electricity contract, from the
    business's own bank account, today. One call records one security deposit receipt of the stated
    dollar amount against that contract, dated today, carrying the months of supply cost and the
    commercial credit grade it was sized on; the security Beacon Ridge holds on the contract rises
    by exactly that amount and the receipt then appears among the contract's security deposits.
    Nothing else on the contract changes.

    Args:
        cni_contract_id: Id class — the commercial and industrial contract number of the reviewed
            contract, as shown on the contract record returned by the contract lookup.
        amount_usd: Fixed-format class — the dollar amount remitted, in USD, a positive number
            rounded half up to 2 decimal places; it is stored exactly as passed.
        deposit_months: Fixed-format class — the months of estimated supply cost the reviewed
            security represents, an integer number of months.
        credit_grade_basis: Enum class — the commercial credit grade written on the receipt, copied
            from the grade recorded on the contract's existing security deposit receipt: A when
            that receipt records grade A; B when it records grade B; C when it records grade C;
            not_rated when it records not_rated; "" (empty) only when the contract has no existing
            receipt to copy a grade from.

    Returns:
        A dict confirming the receipt: cni_deposit_id (str, the reference number of the new
        security deposit receipt), cni_contract_id (str, the contract secured), amount_usd (float,
        2 decimal places), deposit_months (int), posted_date (str, YYYY-MM-DD, today) and status
        (str, always "recorded", meaning the deposit now counts toward the security held).
    """
    found = ctx.find("cni_contracts", cni_contract_id=cni_contract_id)
    owner = found[0].get("customer_id") if found else None
    amount = round(float(amount_usd), 2)
    months = int(deposit_months)
    rid = ctx.make_id("cnd_", cni_contract_id, "review", amount, months, credit_grade_basis)
    ctx.create("cni_deposits", rid, cni_deposit_id=rid, cni_contract_id=cni_contract_id, customer_id=owner,
               event_type="cni_deposit_post", amount_usd=amount, deposit_months=months,
               credit_grade_basis=credit_grade_basis, posted_date=ctx.now()[:10], source_deposit_id=None)
    return str({"cni_deposit_id": rid, "cni_contract_id": cni_contract_id, "amount_usd": amount,
                "deposit_months": months, "posted_date": ctx.now()[:10], "status": "recorded"})


@tool(owner="agent", rw="write")
def bill_contract_exit_damages_2ce88247(ctx: ToolContext, cni_contract_id: str, amount_usd: float,
                                        etf_remaining_kwh: int) -> str:
    """Bill the liquidated damages for a commercial and industrial electricity contract whose supply
    ended during its term because another supplier enrolled the facility or the utility
    final-billed it. One call adds one early termination fee line to that contract's bill, dated
    today, carrying the dollar amount and the remaining contracted kWh passed; the net charges
    billed on the contract rise by that amount and the line then appears among the contract's bill
    lines. The contract's status and dates are not changed.

    Args:
        cni_contract_id: Id class — the commercial and industrial contract number of the contract
            whose supply ended, as shown on the contract record returned by the contract lookup.
        amount_usd: Fixed-format class — the damages billed, in USD, a positive number rounded
            half up to 2 decimal places; it is stored exactly as passed.
        etf_remaining_kwh: Fixed-format class — the remaining contracted kWh the damages were
            measured on, an integer kWh count with no decimals.

    Returns:
        A dict confirming the line: cni_billing_id (str, the reference number of the new bill
        line), cni_contract_id (str, the contract billed), line_type (str, always
        "early_termination_fee"), amount_usd (float, 2 decimal places), etf_remaining_kwh (int)
        and posted_date (str, YYYY-MM-DD, today). A returned cni_billing_id means the line is on
        the contract's bill.
    """
    found = ctx.find("cni_contracts", cni_contract_id=cni_contract_id)
    owner = found[0].get("customer_id") if found else None
    amount = round(float(amount_usd), 2)
    kwh = int(etf_remaining_kwh)
    rid = ctx.make_id("cnb_", cni_contract_id, "exit", amount, kwh)
    ctx.create("cni_billing", rid, cni_billing_id=rid, cni_contract_id=cni_contract_id, customer_id=owner,
               event_type="cni_etf_charge", line_type="early_termination_fee", billing_period_start="",
               billing_period_end="", billing_days=0, usage_kwh=0, rate_cents_kwh=0.0, tag_kw=0.0,
               tag_rate_usd_mw_day=0.0, amount_usd=amount, posted_date=ctx.now()[:10],
               source_billing_id=None, etf_remaining_kwh=kwh)
    return str({"cni_billing_id": rid, "cni_contract_id": cni_contract_id,
                "line_type": "early_termination_fee", "amount_usd": amount,
                "etf_remaining_kwh": kwh, "posted_date": ctx.now()[:10]})


@tool(owner="agent", rw="write")
def credit_fixed_price_line_5b24cf0d(ctx: ToolContext, source_billing_id: str, amount_usd: float) -> str:
    """Post a rebill credit against one fixed-price energy bill line of a commercial and industrial
    electricity contract (a block energy line on a block and index contract, or a fixed energy
    line on a fixed structure) that the business disputes as billed above the price in force for
    its cycle. One call adds one rebill credit line, dated today, to the same contract's bill, tied
    to the disputed line and dated to that line's billing cycle; the net charges billed on the
    contract fall by the credited amount and the credit then appears among the contract's bill
    lines. The disputed line itself is not changed.

    Args:
        source_billing_id: Id class — the reference number of the disputed fixed-price energy bill
            line, as shown on the bill lines returned by the C&I bill lookup.
        amount_usd: Fixed-format class — the rebill credit, in USD, a negative number rounded half
            up to 2 decimal places; it is stored exactly as passed.

    Returns:
        A dict confirming the credit: cni_billing_id (str, the reference number of the new rebill
        credit line), source_billing_id (str, the line corrected), cni_contract_id (str, the
        contract credited), line_type (str, always "rebill_credit"), billing_period_start (str,
        YYYY-MM-DD, the corrected line's cycle), amount_usd (float, negative, 2 decimal places) and
        posted_date (str, YYYY-MM-DD, today).
    """
    src = ctx.find("cni_billing", cni_billing_id=source_billing_id)
    line = src[0] if src else {}
    amount = round(float(amount_usd), 2)
    rid = ctx.make_id("cnb_", source_billing_id, "fixed_price_credit", amount)
    ctx.create("cni_billing", rid, cni_billing_id=rid, cni_contract_id=line.get("cni_contract_id"),
               customer_id=line.get("customer_id"), event_type="cni_adjustment", line_type="rebill_credit",
               billing_period_start=line.get("billing_period_start", ""), billing_period_end="",
               billing_days=0, usage_kwh=0, rate_cents_kwh=0.0, tag_kw=0.0, tag_rate_usd_mw_day=0.0,
               amount_usd=amount, posted_date=ctx.now()[:10], source_billing_id=source_billing_id,
               etf_remaining_kwh=0)
    return str({"cni_billing_id": rid, "source_billing_id": source_billing_id,
                "cni_contract_id": line.get("cni_contract_id"), "line_type": "rebill_credit",
                "billing_period_start": line.get("billing_period_start", ""), "amount_usd": amount,
                "posted_date": ctx.now()[:10]})


@tool(owner="agent", rw="write")
def credit_index_line_725777e6(ctx: ToolContext, source_billing_id: str, amount_usd: float) -> str:
    """Post a rebill credit against one index energy bill line of a commercial and industrial
    electricity contract that the business disputes as billed above the index price its contract
    allows. One call adds one rebill credit line, dated today, to the same contract's bill, tied to
    the disputed line and dated to that line's billing cycle; the net charges billed on the
    contract fall by the credited amount and the credit then appears among the contract's bill
    lines. The disputed line itself is not changed.

    Args:
        source_billing_id: Id class — the reference number of the disputed index energy bill line,
            as shown on the bill lines returned by the C&I bill lookup.
        amount_usd: Fixed-format class — the rebill credit, in USD, a negative number rounded half
            up to 2 decimal places; it is stored exactly as passed.

    Returns:
        A dict confirming the credit: cni_billing_id (str, the reference number of the new rebill
        credit line), source_billing_id (str, the line corrected), cni_contract_id (str, the
        contract credited), line_type (str, always "rebill_credit"), billing_period_start (str,
        YYYY-MM-DD, the corrected line's cycle), amount_usd (float, negative, 2 decimal places) and
        posted_date (str, YYYY-MM-DD, today).
    """
    src = ctx.find("cni_billing", cni_billing_id=source_billing_id)
    line = src[0] if src else {}
    amount = round(float(amount_usd), 2)
    rid = ctx.make_id("cnb_", source_billing_id, "index_credit", amount)
    ctx.create("cni_billing", rid, cni_billing_id=rid, cni_contract_id=line.get("cni_contract_id"),
               customer_id=line.get("customer_id"), event_type="cni_adjustment", line_type="rebill_credit",
               billing_period_start=line.get("billing_period_start", ""), billing_period_end="",
               billing_days=0, usage_kwh=0, rate_cents_kwh=0.0, tag_kw=0.0, tag_rate_usd_mw_day=0.0,
               amount_usd=amount, posted_date=ctx.now()[:10], source_billing_id=source_billing_id,
               etf_remaining_kwh=0)
    return str({"cni_billing_id": rid, "source_billing_id": source_billing_id,
                "cni_contract_id": line.get("cni_contract_id"), "line_type": "rebill_credit",
                "billing_period_start": line.get("billing_period_start", ""), "amount_usd": amount,
                "posted_date": ctx.now()[:10]})

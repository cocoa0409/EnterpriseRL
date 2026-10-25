"""Hidden task tools for the setaside_property_charges_and_repairs difficulty of env_0064
(Cedarline Reverse Mortgage, LLC). Each tool performs one atomic write on a Summit Tax and
Insurance Reserve; every figure it records is worked out by the agent beforehand."""

from erlbench import ToolContext, tool


@tool(owner="agent", rw="write")
def update_reserve_tax_b755da65(ctx: ToolContext, setaside_id: str, setaside_request_id: str,
                                annual_property_tax: float) -> str:
    """Record a new annual property tax figure on a Summit Tax and Insurance Reserve after a review of
    the property tax bills on file. The servicing agent replaces the annual property tax held on the
    reserve with the figure supplied; the reserve balance, its ledger, the bills on file and the
    annual hazard and flood premiums are left unchanged. Afterwards the reserve shows the new annual
    property tax to anyone who looks it up. The receipt confirms the reserve, the bill relied on, the
    figure held before the update and the figure now held.

    Args:
        setaside_id: Id class — reference number of the Summit Tax and Insurance Reserve whose annual property tax is replaced, as returned by the set-aside account lookup for the borrower's loan.
        setaside_request_id: Id class — reference number of the property tax bill on file that the review relied on, as returned by the set-aside bills and requests lookup for that reserve.
        annual_property_tax: Fixed-format class — the annual property tax to hold on the reserve, in USD, 2 decimal places, a positive amount already rounded to the cent before the call.

    Returns:
        A dictionary rendered as text with: status — the literal "updated" when the figure was
        recorded; setaside_id — the reserve updated; setaside_request_id — the bill relied on;
        previous_annual_property_tax — the annual property tax held before the call, USD with 2
        decimal places; annual_property_tax — the annual property tax now held, USD with 2 decimal
        places.
    """
    rows = ctx.find("setaside_accounts", setaside_id=setaside_id)
    previous = round(float(rows[0].get("annual_property_tax") or 0), 2) if rows else 0.0
    new_value = round(float(annual_property_tax), 2)
    ctx.update("setaside_accounts", setaside_id, annual_property_tax=new_value)
    return str({"status": "updated", "setaside_id": setaside_id,
                "setaside_request_id": setaside_request_id,
                "previous_annual_property_tax": previous, "annual_property_tax": new_value})


@tool(owner="user", rw="write")
def return_tax_refund_0b9f20b8(ctx: ToolContext, setaside_id: str, source_txn_ref: str,
                               credit_amount: float) -> str:
    """Pay back into a Summit Tax and Insurance Reserve money from a property tax refund that the
    taxing authority mailed to the borrower. The payment the borrower makes with this call is credited to the reserve the same day as a refund credit that points at the
    reserve's original payment of the overpaid tax installment, and the reserve balance rises by that
    amount. Nothing is charged to or credited on the loan balance. The borrower sees the credit on the
    reserve at once; the receipt carries the new credit's reference number, the amount credited and
    the reserve balance after the credit.

    Args:
        setaside_id: Id class — reference number of the Summit Tax and Insurance Reserve that receives the money, as returned by the set-aside account lookup and read out to the borrower by the agent.
        source_txn_ref: Id class — reference number of the reserve's original tax payment transaction that the refund relates to, as returned by the set-aside transaction lookup and read out to the borrower by the agent.
        credit_amount: Fixed-format class — the amount the borrower pays into the reserve, in USD, 2 decimal places, a positive amount rounded to the cent.

    Returns:
        A dictionary rendered as text with: status — the literal "credited" when the money was
        received and credited; setaside_txn_id — reference number of the new refund credit;
        setaside_id — the reserve credited; source_txn_ref — the original tax payment the credit
        relates to; credit_amount — the amount credited, USD with 2 decimal places; effective_date —
        the date of the credit in YYYY-MM-DD form; setaside_balance — the reserve balance after the
        credit, USD with 2 decimal places.
    """
    amount = round(float(credit_amount), 2)
    rid = ctx.make_id("satx_", setaside_id, source_txn_ref, amount)
    rows = ctx.find("setaside_accounts", setaside_id=setaside_id)
    customer_id = rows[0].get("customer_id", "") if rows else ""
    balance = round(float(rows[0].get("setaside_balance") or 0) + amount, 2) if rows else amount
    today = ctx.now()[:10]
    ctx.create("setaside_transactions", rid, setaside_txn_id=rid, setaside_id=setaside_id,
               customer_id=customer_id, event_type="setaside_refund_credit", loan_program="summit",
               amount=amount, effective_date=today, accrual_period="", setaside_request_id=None,
               coverage_type="not_applicable", repair_draw_number=0, release_reason="not_applicable",
               rate_applied_pct="", source_txn_ref=source_txn_ref)
    ctx.update("setaside_accounts", setaside_id, setaside_balance=balance)
    return str({"status": "credited", "setaside_txn_id": rid, "setaside_id": setaside_id,
                "source_txn_ref": source_txn_ref, "credit_amount": amount,
                "effective_date": today, "setaside_balance": balance})


@tool(owner="agent", rw="write")
def update_reserve_hazard_5ea539e7(ctx: ToolContext, setaside_id: str, setaside_request_id: str,
                                   annual_hazard_premium: float) -> str:
    """Record a new annual hazard insurance premium on a Summit Tax and Insurance Reserve after a
    review of the hazard insurance bills on file. The servicing agent replaces the annual hazard
    premium held on the reserve with the figure supplied; the reserve balance, its ledger, the bills on
    file and the annual property tax and flood premium are left unchanged. Afterwards the reserve shows
    the new annual hazard premium to anyone who looks it up. The receipt confirms the reserve, the bill
    relied on, the figure held before the update and the figure now held.

    Args:
        setaside_id: Id class — reference number of the Summit Tax and Insurance Reserve whose annual hazard premium is replaced, as returned by the set-aside account lookup for the loan.
        setaside_request_id: Id class — reference number of the hazard insurance bill on file that the review relied on, as returned by the set-aside bills and requests lookup for that reserve.
        annual_hazard_premium: Fixed-format class — the annual hazard premium to hold on the reserve, in USD, 2 decimal places, a positive amount already rounded to the cent before the call.

    Returns:
        A dictionary rendered as text with: status — the literal "updated" when the figure was
        recorded; setaside_id — the reserve updated; setaside_request_id — the bill relied on;
        previous_annual_hazard_premium — the annual hazard premium held before the call, USD with 2
        decimal places; annual_hazard_premium — the annual hazard premium now held, USD with 2 decimal
        places.
    """
    rows = ctx.find("setaside_accounts", setaside_id=setaside_id)
    previous = round(float(rows[0].get("annual_hazard_premium") or 0), 2) if rows else 0.0
    new_value = round(float(annual_hazard_premium), 2)
    ctx.update("setaside_accounts", setaside_id, annual_hazard_premium=new_value)
    return str({"status": "updated", "setaside_id": setaside_id,
                "setaside_request_id": setaside_request_id,
                "previous_annual_hazard_premium": previous, "annual_hazard_premium": new_value})


@tool(owner="agent", rw="write")
def update_reserve_flood_ec384f8d(ctx: ToolContext, setaside_id: str, setaside_request_id: str,
                                  annual_flood_premium: float) -> str:
    """Record a new annual flood insurance premium on a Summit Tax and Insurance Reserve after a review
    of the flood insurance bills on file. The servicing agent replaces the annual flood premium held on
    the reserve with the figure supplied; the reserve balance, its ledger, the bills on file and the
    annual property tax and hazard premium are left unchanged. Afterwards the reserve shows the new
    annual flood premium to anyone who looks it up. The receipt confirms the reserve, the bill relied
    on, the figure held before the update and the figure now held.

    Args:
        setaside_id: Id class — reference number of the Summit Tax and Insurance Reserve whose annual flood premium is replaced, as returned by the set-aside account lookup for the loan.
        setaside_request_id: Id class — reference number of the flood insurance bill on file that the review relied on, as returned by the set-aside bills and requests lookup for that reserve.
        annual_flood_premium: Fixed-format class — the annual flood premium to hold on the reserve, in USD, 2 decimal places, a positive amount already rounded to the cent before the call.

    Returns:
        A dictionary rendered as text with: status — the literal "updated" when the figure was
        recorded; setaside_id — the reserve updated; setaside_request_id — the bill relied on;
        previous_annual_flood_premium — the annual flood premium held before the call, USD with 2
        decimal places; annual_flood_premium — the annual flood premium now held, USD with 2 decimal
        places.
    """
    rows = ctx.find("setaside_accounts", setaside_id=setaside_id)
    previous = round(float(rows[0].get("annual_flood_premium") or 0), 2) if rows else 0.0
    new_value = round(float(annual_flood_premium), 2)
    ctx.update("setaside_accounts", setaside_id, annual_flood_premium=new_value)
    return str({"status": "updated", "setaside_id": setaside_id,
                "setaside_request_id": setaside_request_id,
                "previous_annual_flood_premium": previous, "annual_flood_premium": new_value})


@tool(owner="user", rw="write")
def return_hazard_premium_b6a621c2(ctx: ToolContext, setaside_id: str, source_txn_ref: str,
                                   credit_amount: float) -> str:
    """Pay back into a Summit Tax and Insurance Reserve money from a hazard insurance premium that an
    insurer returned to the borrower or to the borrower's estate after a policy term the reserve had
    paid was cancelled. The payment the payer makes with this call is credited to
    the reserve the same day as a refund credit that points at the reserve's original payment of the
    cancelled hazard term, and the reserve balance rises by that amount. Nothing is charged to or
    credited on the loan balance. The credit shows on the reserve at once; the receipt carries the new
    credit's reference number, the amount credited and the reserve balance after the credit.

    Args:
        setaside_id: Id class — reference number of the Summit Tax and Insurance Reserve that receives the money, as returned by the set-aside account lookup and read out to the payer by the agent.
        source_txn_ref: Id class — reference number of the reserve's original hazard insurance payment transaction that the returned premium relates to, as returned by the set-aside transaction lookup and read out to the payer by the agent.
        credit_amount: Fixed-format class — the amount paid into the reserve, in USD, 2 decimal places, a positive amount rounded to the cent.

    Returns:
        A dictionary rendered as text with: status — the literal "credited" when the money was
        received and credited; setaside_txn_id — reference number of the new refund credit;
        setaside_id — the reserve credited; source_txn_ref — the original hazard payment the credit
        relates to; credit_amount — the amount credited, USD with 2 decimal places; effective_date —
        the date of the credit in YYYY-MM-DD form; setaside_balance — the reserve balance after the
        credit, USD with 2 decimal places.
    """
    amount = round(float(credit_amount), 2)
    rid = ctx.make_id("satx_", setaside_id, source_txn_ref, amount)
    rows = ctx.find("setaside_accounts", setaside_id=setaside_id)
    customer_id = rows[0].get("customer_id", "") if rows else ""
    balance = round(float(rows[0].get("setaside_balance") or 0) + amount, 2) if rows else amount
    today = ctx.now()[:10]
    ctx.create("setaside_transactions", rid, setaside_txn_id=rid, setaside_id=setaside_id,
               customer_id=customer_id, event_type="setaside_refund_credit", loan_program="summit",
               amount=amount, effective_date=today, accrual_period="", setaside_request_id=None,
               coverage_type="not_applicable", repair_draw_number=0, release_reason="not_applicable",
               rate_applied_pct="", source_txn_ref=source_txn_ref)
    ctx.update("setaside_accounts", setaside_id, setaside_balance=balance)
    return str({"status": "credited", "setaside_txn_id": rid, "setaside_id": setaside_id,
                "source_txn_ref": source_txn_ref, "credit_amount": amount,
                "effective_date": today, "setaside_balance": balance})


@tool(owner="user", rw="write")
def return_flood_premium_57ae44ac(ctx: ToolContext, setaside_id: str, source_txn_ref: str,
                                  credit_amount: float) -> str:
    """Pay back into a Summit Tax and Insurance Reserve money from a flood insurance premium that an
    insurer returned to the borrower or to the borrower's estate after a policy term the reserve had
    paid was cancelled. The payment the payer makes with this call is credited to
    the reserve the same day as a refund credit that points at the reserve's original payment of the
    cancelled flood term, and the reserve balance rises by that amount. Nothing is charged to or
    credited on the loan balance. The credit shows on the reserve at once; the receipt carries the new
    credit's reference number, the amount credited and the reserve balance after the credit.

    Args:
        setaside_id: Id class — reference number of the Summit Tax and Insurance Reserve that receives the money, as returned by the set-aside account lookup and read out to the payer by the agent.
        source_txn_ref: Id class — reference number of the reserve's original flood insurance payment transaction that the returned premium relates to, as returned by the set-aside transaction lookup and read out to the payer by the agent.
        credit_amount: Fixed-format class — the amount paid into the reserve, in USD, 2 decimal places, a positive amount rounded to the cent.

    Returns:
        A dictionary rendered as text with: status — the literal "credited" when the money was
        received and credited; setaside_txn_id — reference number of the new refund credit;
        setaside_id — the reserve credited; source_txn_ref — the original flood payment the credit
        relates to; credit_amount — the amount credited, USD with 2 decimal places; effective_date —
        the date of the credit in YYYY-MM-DD form; setaside_balance — the reserve balance after the
        credit, USD with 2 decimal places.
    """
    amount = round(float(credit_amount), 2)
    rid = ctx.make_id("satx_", setaside_id, source_txn_ref, amount)
    rows = ctx.find("setaside_accounts", setaside_id=setaside_id)
    customer_id = rows[0].get("customer_id", "") if rows else ""
    balance = round(float(rows[0].get("setaside_balance") or 0) + amount, 2) if rows else amount
    today = ctx.now()[:10]
    ctx.create("setaside_transactions", rid, setaside_txn_id=rid, setaside_id=setaside_id,
               customer_id=customer_id, event_type="setaside_refund_credit", loan_program="summit",
               amount=amount, effective_date=today, accrual_period="", setaside_request_id=None,
               coverage_type="not_applicable", repair_draw_number=0, release_reason="not_applicable",
               rate_applied_pct="", source_txn_ref=source_txn_ref)
    ctx.update("setaside_accounts", setaside_id, setaside_balance=balance)
    return str({"status": "credited", "setaside_txn_id": rid, "setaside_id": setaside_id,
                "source_txn_ref": source_txn_ref, "credit_amount": amount,
                "effective_date": today, "setaside_balance": balance})

"""Hidden task tools of the capital_credit_retirements difficulty (Capital Credits, Cedar Fork Electric Cooperative).

Each tool lands one atomic capital-credit write with the values the agent (or the member) has already
worked out from the published policy; no tool checks eligibility, status, approval, ordering or amounts.
"""

from erlbench import ToolContext, tool


@tool(owner="agent", rw="write")
def book_early_retirement_114ff464(ctx: ToolContext, capital_account_id: str, capital_request_id: str,
                                   allocation_year: str, gross_retired_amount: float, payable_amount: float) -> str:
    """Book the discounted early retirement of one distribution-margin allocation year of a former member's
    capital credit account under a board-approved discounted early retirement request. One call records a
    special retirement entry (retirement type discounted_early, source distribution_margin) for the gross
    allocated amount retired, records the matching payable entry for the amount owed to the member net of the
    present-value discount (the discount kept by the cooperative is the gross less the payable), lowers the
    account's unretired credits by the gross and raises its retired credits owed by the payable. The member
    can see the retired amount owed on the capital credit account; the call succeeded when status is booked.

    Args:
        capital_account_id: Id class — reference number of the member's capital credit account (one member in
            one patron class), read from the capital credit account lookup.
        capital_request_id: Id class — reference number of the board-approved discounted early retirement
            request, read from the capital credit request lookup.
        allocation_year: Fixed-format class — the patronage year of the allocation being retired, four digits
            YYYY exactly as it appears on the allocation entry of the ledger.
        gross_retired_amount: Fixed-format class — the allocated amount of that year still unretired and being
            retired now, in USD, 2 decimal places, rounded half up to the cent.
        payable_amount: Fixed-format class — the amount owed to the member for that row net of the discount and
            any charge, in USD, 2 decimal places, rounded half up to the cent.

    Returns:
        A dictionary rendered as text: status ("booked" on success), retirement_entry_id (reference of the
        special retirement entry), payable_entry_id (reference of the payable entry), allocation_year (YYYY),
        allocation_source (always distribution_margin), gross_retired_amount, discount_amount and
        payable_amount (USD, 2 decimals), and the account's new unretired_balance and payable_balance (USD,
        2 decimals).
    """
    acct_rows = ctx.find("capital_accounts", capital_account_id=capital_account_id)
    acct = acct_rows[0] if acct_rows else {}
    gross = round(float(gross_retired_amount), 2)
    payable = round(float(payable_amount), 2)
    discount = round(gross - payable, 2)
    day = ctx.now()[:10]
    cycle = ctx.now()[:4]
    rid = ctx.make_id("cret_", capital_account_id, capital_request_id, allocation_year, "distribution_margin", gross, payable)
    ctx.create("capital_ledger", rid, capital_entry_id=rid, capital_account_id=capital_account_id,
               customer_id=acct.get("customer_id"), event_type="capital_special_retirement", entry_date=day,
               allocation_year=str(allocation_year), allocation_source="distribution_margin", retirement_cycle=cycle,
               retirement_type="discounted_early", capital_request_id=capital_request_id, amount=gross, fee_amount=0.0)
    pid = ctx.make_id("cpay_", rid, payable)
    ctx.create("capital_ledger", pid, capital_entry_id=pid, capital_account_id=capital_account_id,
               customer_id=acct.get("customer_id"), event_type="capital_payable_accrual", entry_date=day,
               allocation_year=str(allocation_year), allocation_source="distribution_margin", retirement_cycle=cycle,
               retirement_type="discounted_early", capital_request_id=capital_request_id, gross_retired_amount=gross,
               discount_amount=discount, amount=payable, fee_amount=0.0)
    unretired = round(float(acct.get("unretired_balance") or 0) - gross, 2)
    owed = round(float(acct.get("payable_balance") or 0) + payable, 2)
    ctx.update("capital_accounts", capital_account_id, unretired_balance=unretired, payable_balance=owed)
    return str({"status": "booked", "retirement_entry_id": rid, "payable_entry_id": pid,
                "allocation_year": str(allocation_year), "allocation_source": "distribution_margin",
                "gross_retired_amount": gross, "discount_amount": discount, "payable_amount": payable,
                "unretired_balance": unretired, "payable_balance": owed})


@tool(owner="user", rw="write")
def elect_passthrough_early_retirement_2ee4171d(ctx: ToolContext, capital_account_id: str, capital_request_id: str,
                                                allocation_year: str, gross_retired_amount: float,
                                                payable_amount: float) -> str:
    """Record the former member's own election to have one wholesale-supplier pass-through allocation year of
    the capital credit account retired early at its discounted value under the member's approved discounted
    early retirement request. One call records a special retirement entry (retirement type discounted_early,
    source gt_allocation) for the gross allocated amount, records the matching payable entry for the amount
    the member accepts net of the discount, lowers the unretired credits by the gross and raises the retired
    credits owed by the payable. The member sees the accepted amount owed on the account; the call succeeded
    when status is elected.

    Args:
        capital_account_id: Id class — reference number of the member's capital credit account, as the agent
            reads it to the member from the capital credit account lookup.
        capital_request_id: Id class — reference number of the member's approved discounted early retirement
            request, as the agent reads it to the member from the capital credit request lookup.
        allocation_year: Fixed-format class — the patronage year of the pass-through allocation elected, four
            digits YYYY as on the allocation entry.
        gross_retired_amount: Fixed-format class — the allocated pass-through amount of that year being
            retired, in USD, 2 decimal places, rounded half up to the cent.
        payable_amount: Fixed-format class — the discounted amount the member accepts for that row, in USD,
            2 decimal places, rounded half up to the cent.

    Returns:
        A dictionary rendered as text: status ("elected" on success), retirement_entry_id, payable_entry_id,
        allocation_year (YYYY), allocation_source (always gt_allocation), gross_retired_amount,
        discount_amount and payable_amount (USD, 2 decimals), and the account's new unretired_balance and
        payable_balance (USD, 2 decimals).
    """
    acct_rows = ctx.find("capital_accounts", capital_account_id=capital_account_id)
    acct = acct_rows[0] if acct_rows else {}
    gross = round(float(gross_retired_amount), 2)
    payable = round(float(payable_amount), 2)
    discount = round(gross - payable, 2)
    day = ctx.now()[:10]
    cycle = ctx.now()[:4]
    rid = ctx.make_id("cret_", capital_account_id, capital_request_id, allocation_year, "gt_allocation", gross, payable)
    ctx.create("capital_ledger", rid, capital_entry_id=rid, capital_account_id=capital_account_id,
               customer_id=acct.get("customer_id"), event_type="capital_special_retirement", entry_date=day,
               allocation_year=str(allocation_year), allocation_source="gt_allocation", retirement_cycle=cycle,
               retirement_type="discounted_early", capital_request_id=capital_request_id, amount=gross, fee_amount=0.0)
    pid = ctx.make_id("cpay_", rid, payable)
    ctx.create("capital_ledger", pid, capital_entry_id=pid, capital_account_id=capital_account_id,
               customer_id=acct.get("customer_id"), event_type="capital_payable_accrual", entry_date=day,
               allocation_year=str(allocation_year), allocation_source="gt_allocation", retirement_cycle=cycle,
               retirement_type="discounted_early", capital_request_id=capital_request_id, gross_retired_amount=gross,
               discount_amount=discount, amount=payable, fee_amount=0.0)
    unretired = round(float(acct.get("unretired_balance") or 0) - gross, 2)
    owed = round(float(acct.get("payable_balance") or 0) + payable, 2)
    ctx.update("capital_accounts", capital_account_id, unretired_balance=unretired, payable_balance=owed)
    return str({"status": "elected", "retirement_entry_id": rid, "payable_entry_id": pid,
                "allocation_year": str(allocation_year), "allocation_source": "gt_allocation",
                "gross_retired_amount": gross, "discount_amount": discount, "payable_amount": payable,
                "unretired_balance": unretired, "payable_balance": owed})


@tool(owner="agent", rw="write")
def book_estate_later_allocation_bc10e318(ctx: ToolContext, capital_account_id: str, capital_request_id: str,
                                          allocation_year: str, gross_retired_amount: float,
                                          payable_amount: float) -> str:
    """Book the estate retirement of one distribution-margin allocation that was booked to a deceased member's
    capital credit account on a date later than the board approval of the estate's retirement. One call records a special retirement
    entry (retirement type estate, source distribution_margin) for the gross allocated amount, records the
    matching payable entry for the amount owed to the estate net of the present-value discount, lowers the
    account's unretired credits by the gross and raises its retired credits owed by the payable. The estate's
    claimant can see the amount owed to the estate; the call succeeded when status is booked.

    Args:
        capital_account_id: Id class — reference number of the deceased member's capital credit account, read
            from the capital credit account lookup.
        capital_request_id: Id class — reference number of the estate's board-approved estate retirement
            request, read from the capital credit request lookup.
        allocation_year: Fixed-format class — the patronage year of the later allocation, four digits YYYY as
            on the allocation entry.
        gross_retired_amount: Fixed-format class — the allocated amount being retired for the estate, in USD,
            2 decimal places, rounded half up to the cent.
        payable_amount: Fixed-format class — the amount owed to the estate for that row net of the discount, in
            USD, 2 decimal places, rounded half up to the cent.

    Returns:
        A dictionary rendered as text: status ("booked" on success), retirement_entry_id, payable_entry_id,
        allocation_year (YYYY), allocation_source (always distribution_margin), gross_retired_amount,
        discount_amount and payable_amount (USD, 2 decimals), and the account's new unretired_balance and
        payable_balance (USD, 2 decimals).
    """
    acct_rows = ctx.find("capital_accounts", capital_account_id=capital_account_id)
    acct = acct_rows[0] if acct_rows else {}
    gross = round(float(gross_retired_amount), 2)
    payable = round(float(payable_amount), 2)
    discount = round(gross - payable, 2)
    day = ctx.now()[:10]
    cycle = ctx.now()[:4]
    rid = ctx.make_id("cret_", capital_account_id, capital_request_id, allocation_year, "distribution_margin", gross, payable)
    ctx.create("capital_ledger", rid, capital_entry_id=rid, capital_account_id=capital_account_id,
               customer_id=acct.get("customer_id"), event_type="capital_special_retirement", entry_date=day,
               allocation_year=str(allocation_year), allocation_source="distribution_margin", retirement_cycle=cycle,
               retirement_type="estate", capital_request_id=capital_request_id, amount=gross, fee_amount=0.0)
    pid = ctx.make_id("cpay_", rid, payable)
    ctx.create("capital_ledger", pid, capital_entry_id=pid, capital_account_id=capital_account_id,
               customer_id=acct.get("customer_id"), event_type="capital_payable_accrual", entry_date=day,
               allocation_year=str(allocation_year), allocation_source="distribution_margin", retirement_cycle=cycle,
               retirement_type="estate", capital_request_id=capital_request_id, gross_retired_amount=gross,
               discount_amount=discount, amount=payable, fee_amount=0.0)
    unretired = round(float(acct.get("unretired_balance") or 0) - gross, 2)
    owed = round(float(acct.get("payable_balance") or 0) + payable, 2)
    ctx.update("capital_accounts", capital_account_id, unretired_balance=unretired, payable_balance=owed)
    return str({"status": "booked", "retirement_entry_id": rid, "payable_entry_id": pid,
                "allocation_year": str(allocation_year), "allocation_source": "distribution_margin",
                "gross_retired_amount": gross, "discount_amount": discount, "payable_amount": payable,
                "unretired_balance": unretired, "payable_balance": owed})


@tool(owner="user", rw="write")
def elect_estate_passthrough_retirement_e31dc75a(ctx: ToolContext, capital_account_id: str,
                                                 capital_request_id: str, allocation_year: str,
                                                 gross_retired_amount: float, payable_amount: float) -> str:
    """Record the estate claimant's own election to have one wholesale-supplier pass-through allocation, booked
    to the deceased member's capital credit account on a date later than the board approval of the estate's retirement, retired for
    the estate at its discounted value. One call records a special retirement entry (retirement type estate,
    source gt_allocation) for the gross allocated amount, records the matching payable entry for the amount the
    claimant accepts net of the discount, lowers the unretired credits by the gross and raises the retired
    credits owed by the payable. The claimant sees the accepted amount owed to the estate; the call succeeded
    when status is elected.

    Args:
        capital_account_id: Id class — reference number of the deceased member's capital credit account, as the
            agent reads it to the claimant from the capital credit account lookup.
        capital_request_id: Id class — reference number of the estate's approved estate retirement request, as
            the agent reads it to the claimant from the capital credit request lookup.
        allocation_year: Fixed-format class — the patronage year of the pass-through allocation elected, four
            digits YYYY as on the allocation entry.
        gross_retired_amount: Fixed-format class — the allocated pass-through amount being retired, in USD,
            2 decimal places, rounded half up to the cent.
        payable_amount: Fixed-format class — the discounted amount the claimant accepts for the estate, in USD,
            2 decimal places, rounded half up to the cent.

    Returns:
        A dictionary rendered as text: status ("elected" on success), retirement_entry_id, payable_entry_id,
        allocation_year (YYYY), allocation_source (always gt_allocation), gross_retired_amount,
        discount_amount and payable_amount (USD, 2 decimals), and the account's new unretired_balance and
        payable_balance (USD, 2 decimals).
    """
    acct_rows = ctx.find("capital_accounts", capital_account_id=capital_account_id)
    acct = acct_rows[0] if acct_rows else {}
    gross = round(float(gross_retired_amount), 2)
    payable = round(float(payable_amount), 2)
    discount = round(gross - payable, 2)
    day = ctx.now()[:10]
    cycle = ctx.now()[:4]
    rid = ctx.make_id("cret_", capital_account_id, capital_request_id, allocation_year, "gt_allocation", gross, payable)
    ctx.create("capital_ledger", rid, capital_entry_id=rid, capital_account_id=capital_account_id,
               customer_id=acct.get("customer_id"), event_type="capital_special_retirement", entry_date=day,
               allocation_year=str(allocation_year), allocation_source="gt_allocation", retirement_cycle=cycle,
               retirement_type="estate", capital_request_id=capital_request_id, amount=gross, fee_amount=0.0)
    pid = ctx.make_id("cpay_", rid, payable)
    ctx.create("capital_ledger", pid, capital_entry_id=pid, capital_account_id=capital_account_id,
               customer_id=acct.get("customer_id"), event_type="capital_payable_accrual", entry_date=day,
               allocation_year=str(allocation_year), allocation_source="gt_allocation", retirement_cycle=cycle,
               retirement_type="estate", capital_request_id=capital_request_id, gross_retired_amount=gross,
               discount_amount=discount, amount=payable, fee_amount=0.0)
    unretired = round(float(acct.get("unretired_balance") or 0) - gross, 2)
    owed = round(float(acct.get("payable_balance") or 0) + payable, 2)
    ctx.update("capital_accounts", capital_account_id, unretired_balance=unretired, payable_balance=owed)
    return str({"status": "elected", "retirement_entry_id": rid, "payable_entry_id": pid,
                "allocation_year": str(allocation_year), "allocation_source": "gt_allocation",
                "gross_retired_amount": gross, "discount_amount": discount, "payable_amount": payable,
                "unretired_balance": unretired, "payable_balance": owed})


@tool(owner="agent", rw="write")
def reissue_capital_check_624c80d7(ctx: ToolContext, capital_account_id: str, customer_id: str,
                                   original_entry_id: str, check_amount: float, fee_amount: float) -> str:
    """Issue a replacement capital credit check for a check payout that was voided, mailed to the mailing
    address on file. One call records a new check payout on the capital credit account that names the voided
    payout it replaces, carries the retirement year of that payout and the charges deducted, and lowers the
    account's retired credits owed by the check amount plus the charges. The member or estate sees a new check
    with its own check number; the call succeeded when status is issued.

    Args:
        capital_account_id: Id class — reference number of the capital credit account the voided payout belongs
            to, read from the capital credit account lookup.
        customer_id: Id class — customer reference number of the member (or deceased member) the check is paid
            for, read from the member profile lookup.
        original_entry_id: Id class — reference number of the voided check payout being replaced (the most
            recent payout in its chain), read from the capital credit ledger lookup.
        check_amount: Fixed-format class — face amount of the replacement check, in USD, 2 decimal places,
            rounded half up to the cent.
        fee_amount: Fixed-format class — total of the charges deducted from the replacement, in USD, 2 decimal
            places, rounded half up to the cent; 0.00 when none.

    Returns:
        A dictionary rendered as text: status ("issued" on success), capital_entry_id (reference of the new
        check payout), check_number (the printed check number, digits), original_entry_id (the voided payout
        replaced), retirement_cycle (YYYY of the payout replaced), check_amount and fee_amount (USD, 2
        decimals), and payable_balance (the account's retired credits still owed afterwards, USD, 2 decimals).
    """
    acct_rows = ctx.find("capital_accounts", capital_account_id=capital_account_id)
    acct = acct_rows[0] if acct_rows else {}
    orig = ctx.find("capital_ledger", capital_entry_id=original_entry_id)
    cycle = orig[0].get("retirement_cycle") if orig else None
    amount = round(float(check_amount), 2)
    fee = round(float(fee_amount), 2)
    rid = ctx.make_id("cdis_", capital_account_id, customer_id, original_entry_id, amount, fee)
    check_number = "43" + str(int(rid[-10:], 16))[-6:].zfill(6)
    ctx.create("capital_ledger", rid, capital_entry_id=rid, capital_account_id=capital_account_id,
               customer_id=customer_id, event_type="capital_disbursement", entry_date=ctx.now()[:10],
               retirement_cycle=cycle, disbursement_method="check", amount=amount, check_number=check_number,
               original_entry_id=original_entry_id, fee_amount=fee)
    owed = round(float(acct.get("payable_balance") or 0) - amount - fee, 2)
    ctx.update("capital_accounts", capital_account_id, payable_balance=owed)
    return str({"status": "issued", "capital_entry_id": rid, "check_number": check_number,
                "original_entry_id": original_entry_id, "retirement_cycle": cycle, "check_amount": amount,
                "fee_amount": fee, "payable_balance": owed})

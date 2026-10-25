"""Hidden task tools for gap_waiver_cancellations_and_claims (Harborline Acceptance Corporation).

Each tool records one figure of the GAP claim worksheet on the claim record of a reported
total-loss or theft loss (one field of that claim record per call). None of them creates a
decision, a refund, a cancellation or any record of the retail installment contract, the
insurance tracking program or the service contract.
"""

from erlbench import ToolContext, tool


@tool(owner="user", rw="write")
def claim_premier_deductible_reimbursement_7815b2b6(ctx: ToolContext, gap_activity_id: str,
                                                    deductible_covered_usd: float) -> str:
    """The borrower claims the deductible reimbursement of a GAP Waiver Premier 150 addendum on the
    reported total-loss or theft claim on the strength of the primary insurer's settlement documents
    the borrower holds. One call records only the reimbursement amount the borrower claims as the deductible covered on that claim
    record; the claim's other figures, the addendum's status and the contract stay as they are.
    The borrower can see the claim reference and the amount now recorded as covered.

    Args:
        gap_activity_id: Id class — the reference number of the claim record of the reported loss on the borrower's GAP waiver addendum, as returned by the GAP activity lookup for that addendum.
        deductible_covered_usd: Fixed-format class — the deductible reimbursement claimed, in US dollars, a number of 0.00 or more kept to 2 decimal places (rounded to the cent); 0.00 claims nothing.

    Returns:
        A confirmation text naming the claim reference number and the deductible covered now
        recorded on it, in US dollars with 2 decimal places. Receiving this text means the
        amount is recorded on the claim record.
    """
    amount = round(float(deductible_covered_usd), 2)
    ctx.update("gap_activities", gap_activity_id, deductible_covered_usd=amount)
    return f"Deductible reimbursement recorded on claim {gap_activity_id}: deductible covered {amount:.2f} USD."


@tool(owner="agent", rw="write")
def record_claim_balance_at_loss_15fb7d99(ctx: ToolContext, gap_activity_id: str,
                                          balance_at_loss_usd: float) -> str:
    """Record, on the GAP claim worksheet of a GAP Waiver Premier 150 addendum, the starting balance
    of a reported total-loss or theft claim: the balance on the date of loss that the benefit starts
    from. One call writes that
    figure to the claim record of the reported loss; the claim's other figures, the addendum's
    status and the contract stay as they are. The representative and the borrower can see
    the starting balance on the claim.

    Args:
        gap_activity_id: Id class — the reference number of the claim record of the reported loss on the borrower's GAP waiver addendum, as returned by the GAP activity lookup for that addendum.
        balance_at_loss_usd: Fixed-format class — the starting balance on the date of loss, in US dollars, a number of 0.00 or more kept to 2 decimal places (rounded to the cent).

    Returns:
        A confirmation text naming the claim reference number and the starting balance now
        recorded on it, in US dollars with 2 decimal places. Receiving this text means the
        figure is recorded on the claim record.
    """
    amount = round(float(balance_at_loss_usd), 2)
    ctx.update("gap_activities", gap_activity_id, balance_at_loss_usd=amount)
    return f"Starting balance recorded on claim {gap_activity_id}: balance at loss {amount:.2f} USD."


@tool(owner="agent", rw="write")
def record_premier_claim_exclusions_258c7293(ctx: ToolContext, gap_activity_id: str,
                                             excluded_amounts_usd: float) -> str:
    """Record, on the GAP claim worksheet of a GAP Waiver Premier 150 addendum, the itemized
    excluded amounts of a reported total-loss or theft claim: the total that the benefit does not
    cover and that stays owed by the borrower on the contract. One call writes that total to the
    claim record of the reported loss; the claim's other figures, the addendum's status and the
    contract stay as they are. The representative and the borrower can see the excluded total
    on the claim.

    Args:
        gap_activity_id: Id class — the reference number of the claim record of the reported loss on the borrower's GAP waiver addendum, as returned by the GAP activity lookup for that addendum.
        excluded_amounts_usd: Fixed-format class — the excluded total, in US dollars, a number of 0.00 or more kept to 2 decimal places (rounded to the cent).

    Returns:
        A confirmation text naming the claim reference number and the excluded total now recorded
        on it, in US dollars with 2 decimal places. Receiving this text means the total is
        recorded on the claim record.
    """
    amount = round(float(excluded_amounts_usd), 2)
    ctx.update("gap_activities", gap_activity_id, excluded_amounts_usd=amount)
    return f"Excluded amounts recorded on claim {gap_activity_id}: excluded total {amount:.2f} USD."


@tool(owner="agent", rw="write")
def record_claim_worksheet_benefit_931d4ebc(ctx: ToolContext, gap_activity_id: str,
                                            benefit_usd: float) -> str:
    """Record, on the GAP claim worksheet, the benefit a reported total-loss or theft claim works
    out to. One call writes that benefit figure to the claim record of the reported loss; it
    credits nothing to the contract, decides nothing and leaves the addendum's status, the claim's
    other figures and the contract as they are. The representative
    and the borrower can see the worksheet benefit on the claim.

    Args:
        gap_activity_id: Id class — the reference number of the claim record of the reported loss on the borrower's GAP waiver addendum, as returned by the GAP activity lookup for that addendum.
        benefit_usd: Fixed-format class — the worksheet benefit, in US dollars, a number of 0.00 or more kept to 2 decimal places (rounded to the cent).

    Returns:
        A confirmation text naming the claim reference number and the worksheet benefit now
        recorded on it, in US dollars with 2 decimal places. Receiving this text means the
        figure is recorded on the claim record.
    """
    amount = round(float(benefit_usd), 2)
    ctx.update("gap_activities", gap_activity_id, benefit_usd=amount)
    return f"Worksheet benefit recorded on claim {gap_activity_id}: benefit {amount:.2f} USD."


@tool(owner="agent", rw="write")
def record_plus_claim_balance_at_loss_c4d2a91e(ctx: ToolContext, gap_activity_id: str,
                                               balance_at_loss_usd: float) -> str:
    """Record, on the GAP claim worksheet of a GAP Waiver Plus 150 addendum, the starting balance
    of a reported total-loss or theft claim: the balance on the date of loss that the benefit starts
    from. One call writes that
    figure to the claim record of the reported loss; the claim's other figures, the addendum's
    status and the contract stay as they are. The representative and the borrower can see
    the starting balance on the claim.

    Args:
        gap_activity_id: Id class — the reference number of the claim record of the reported loss on the borrower's GAP waiver addendum, as returned by the GAP activity lookup for that addendum.
        balance_at_loss_usd: Fixed-format class — the starting balance on the date of loss, in US dollars, a number of 0.00 or more kept to 2 decimal places (rounded to the cent).

    Returns:
        A confirmation text naming the claim reference number and the starting balance now
        recorded on it, in US dollars with 2 decimal places. Receiving this text means the
        figure is recorded on the claim record.
    """
    amount = round(float(balance_at_loss_usd), 2)
    ctx.update("gap_activities", gap_activity_id, balance_at_loss_usd=amount)
    return f"Plus starting balance recorded on claim {gap_activity_id}: balance at loss {amount:.2f} USD."


@tool(owner="user", rw="write")
def accept_plus_claim_benefit_e7b3150d(ctx: ToolContext, gap_activity_id: str, benefit_usd: float) -> str:
    """The borrower accepts, on the GAP claim worksheet of a GAP Waiver Plus 150 addendum, the
    worksheet benefit of a reported total-loss or theft claim: the amount the GAP waiver covers on
    the claim after the amounts it does not cover. One call records that benefit on the claim
    record of the reported loss as the borrower accepts it; the claim's other figures, the
    addendum's status and the contract stay as they are. The borrower can see the claim reference
    and the worksheet benefit now recorded on it.

    Args:
        gap_activity_id: Id class — the reference number of the claim record of the reported loss on the borrower's GAP waiver addendum, as returned by the GAP activity lookup for that addendum.
        benefit_usd: Fixed-format class — the worksheet benefit, in US dollars, a number of 0.00 or more kept to 2 decimal places (rounded to the cent).

    Returns:
        A confirmation text naming the claim reference number and the worksheet benefit now
        recorded on it, in US dollars with 2 decimal places. Receiving this text means the benefit
        is recorded on the claim record.
    """
    amount = round(float(benefit_usd), 2)
    ctx.update("gap_activities", gap_activity_id, benefit_usd=amount)
    return f"Plus worksheet benefit recorded on claim {gap_activity_id}: benefit {amount:.2f} USD."

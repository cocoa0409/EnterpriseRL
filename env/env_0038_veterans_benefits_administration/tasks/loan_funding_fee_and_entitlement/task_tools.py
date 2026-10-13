"""Hidden task tools for the loan_funding_fee_and_entitlement difficulty of
env_0038_veterans_benefits_administration (VA Home Loan Guaranty).

Each tool performs one atomic write on a veteran's VA home loan record. None of them
checks eligibility, status, timing or prior entries: those judgements are made by the
representative from the published rules and the records before the call.
"""

from erlbench import ToolContext, tool


@tool(owner="agent", rw="write")
def refund_funding_fee_5c21eab8(ctx: ToolContext, loan_id: str, source_txn_id: str, amount: float,
                                refund_basis: str) -> str:
    """Book a VA funding fee refund against one funding fee charge on a veteran's VA home loan.

    The representative books the refund VA owes the veteran on a funding fee that was charged on the loan.
    One call adds one refund entry to the loan's money transactions, tied to the fee charge it settles and
    dated today, carrying the refunded amount and the ground for the refund; the loan's record of funding fee
    paid is reduced by that amount. Afterwards the refund appears among the loan's money transactions next to
    the fee charge it settles, and the receipt below confirms it was booked.

    Args:
        loan_id: Id class — the reference number of the veteran's VA home loan record on which the fee was
            charged, as returned by the loan lookup for this veteran.
        source_txn_id: Id class — the reference number of the funding fee charge entry being refunded, as
            returned by the loan money-transaction lookup for that loan.
        amount: Fixed-format class — the amount refunded to the veteran, in USD, 2 decimal places, a positive
            number rounded half up to the cent before it is passed.
        refund_basis: Enum class — the ground for the refund, exactly one of:
            retroactive_compensation_award = the veteran was later awarded disability compensation effective
            on or before the loan's closing date;
            purple_heart_after_closing = the veteran received the Purple Heart after the closing date while
            serving on active duty;
            fee_collected_in_error = the fee, or part of it, should not have been collected for any other reason;
            not_applicable = the entry is not a funding fee refund at all, so it never applies to a refund
            booked with this tool.

    Returns:
        A text rendering of a dict with these fields: loan_txn_id (str, reference number of the new refund
        entry), loan_id (str, the loan refunded), source_txn_id (str, the fee charge settled), amount (float,
        USD with 2 decimal places, the amount refunded), transaction_date (str, YYYY-MM-DD, today's date) and
        status (str, always "refund_booked" when the refund entry was written).
    """
    rid = ctx.make_id("lft_", loan_id, source_txn_id, amount, refund_basis)
    amt = round(float(amount), 2)
    day = ctx.now()[:10]
    ctx.create("loan_transactions", rid, loan_txn_id=rid, loan_id=loan_id, customer_id=(ctx.find("loan_guaranties", loan_id=loan_id) or [{}])[0].get("customer_id"),
               event_type="loan_funding_fee_refunded", amount=amt, transaction_date=day, fee_pct_applied=0.0,
               source_txn_id=source_txn_id, refund_basis=refund_basis, deficiency_created=False,
               claim_basis="not_applicable")
    return str({"loan_txn_id": rid, "loan_id": loan_id, "source_txn_id": source_txn_id, "amount": amt,
                "transaction_date": day, "status": "refund_booked"})


@tool(owner="user", rw="write")
def apply_entitlement_restoration_1db0e5c4(ctx: ToolContext, loan_id: str, entitlement_amount: float) -> str:
    """Let a veteran file their own signed request to have home loan entitlement restored on a VA loan that
    was liquidated with a guaranty claim, which restores entitlement on the spot.

    The veteran personally certifies and submits the request for the amount of entitlement the representative
    has told them can be restored on that liquidated loan. One call adds one restoration entry to the loan's
    entitlement history, dated today, on the ground that the loan ended in a guaranty claim, and the
    entitlement tied up in that loan is reduced by the amount restored, which becomes available for a future
    VA loan. The veteran sees the receipt below confirming the restoration.

    Args:
        loan_id: Id class — the reference number of the liquidated VA home loan record whose entitlement is
            being restored, as given to the veteran by the representative from the loan lookup.
        entitlement_amount: Fixed-format class — the amount of entitlement restored, in USD, 2 decimal
            places, a positive number rounded half up to the cent before it is passed.

    Returns:
        A text rendering of a dict with these fields: entitlement_action_id (str, reference number of the new
        restoration entry), loan_id (str, the loan whose entitlement was restored), entitlement_amount (float,
        USD with 2 decimal places, the amount restored), action_date (str, YYYY-MM-DD, today's date) and status
        (str, always "entitlement_restored" when the entry was written).
    """
    rid = ctx.make_id("lea_", loan_id, entitlement_amount)
    amt = round(float(entitlement_amount), 2)
    day = ctx.now()[:10]
    ctx.create("loan_entitlement_actions", rid, entitlement_action_id=rid, loan_id=loan_id,
               customer_id=(ctx.find("loan_guaranties", loan_id=loan_id) or [{}])[0].get("customer_id"), event_type="loan_entitlement_restored",
               entitlement_amount=amt, action_date=day, restoration_basis="debt_repaid_after_claim",
               substitute_customer_id=None)
    return str({"entitlement_action_id": rid, "loan_id": loan_id, "entitlement_amount": amt,
                "action_date": day, "status": "entitlement_restored"})


@tool(owner="agent", rw="write")
def record_partial_claim_d52e4f0e(ctx: ToolContext, loan_id: str, amount: float) -> str:
    """Book a VA partial claim paid to the servicer of a veteran's VA home loan that is in default.

    The representative books the partial claim VA pays to bring the loan current. One call adds one partial
    claim entry to the loan's money transactions, dated today, for the amount paid; the partial claim the
    veteran owes VA on that loan, secured by a subordinate lien, rises by that amount, and the loan is shown
    as current again (its default is cured). The receipt below confirms the entry and the new partial claim
    balance.

    Args:
        loan_id: Id class — the reference number of the veteran's VA home loan record in default, as returned
            by the loan lookup for this veteran.
        amount: Fixed-format class — the partial claim VA pays, in USD, 2 decimal places, a positive number
            rounded half up to the cent before it is passed.

    Returns:
        A text rendering of a dict with these fields: loan_txn_id (str, reference number of the new partial
        claim entry), loan_id (str, the loan concerned), amount (float, USD with 2 decimal places, the partial
        claim paid), partial_claim_balance (float, USD with 2 decimal places, the partial claim now owed on
        the loan), loan_status (str, always "active" once the default is cured) and transaction_date (str,
        YYYY-MM-DD, today's date).
    """
    rid = ctx.make_id("lpc_", loan_id, amount)
    amt = round(float(amount), 2)
    day = ctx.now()[:10]
    rows = ctx.find("loan_guaranties", loan_id=loan_id)
    prior = float(rows[0].get("partial_claim_balance") or 0) if rows else 0.0
    new_balance = round(prior + amt, 2)
    ctx.create("loan_transactions", rid, loan_txn_id=rid, loan_id=loan_id, customer_id=(ctx.find("loan_guaranties", loan_id=loan_id) or [{}])[0].get("customer_id"),
               event_type="loan_partial_claim_paid", amount=amt, transaction_date=day, fee_pct_applied=0.0,
               source_txn_id=None, refund_basis="not_applicable", deficiency_created=False,
               claim_basis="not_applicable")
    ctx.update("loan_guaranties", loan_id, partial_claim_balance=new_balance, status="active")
    return str({"loan_txn_id": rid, "loan_id": loan_id, "amount": amt, "partial_claim_balance": new_balance,
                "loan_status": "active", "transaction_date": day})


@tool(owner="user", rw="write")
def request_release_of_liability_741ed869(ctx: ToolContext, loan_id: str, guaranty_amount: float) -> str:
    """Let a veteran who is selling their home to a buyer assuming the VA loan request, in their own name,
    release from personal liability on that loan, which VA records on the spot.

    The veteran personally signs the request as the seller. One call marks the loan as released by
    assumption, records that the veteran is released from liability with today's date as the release date,
    and records the guaranty that stays in force on the loan for the assuming buyer, at the figure the
    representative has told the veteran. The veteran sees the receipt below confirming the release.

    Args:
        loan_id: Id class — the reference number of the VA home loan record being assumed, as given to the
            veteran by the representative from the loan lookup.
        guaranty_amount: Fixed-format class — the guaranty that stays in force on the loan after the
            release, in USD, 2 decimal places, a positive number rounded half up to the cent before it is
            passed.

    Returns:
        A text rendering of a dict with these fields: loan_id (str, the loan released), loan_status (str,
        always "released_by_assumption"), release_of_liability (bool, always True), release_date (str,
        YYYY-MM-DD, today's date) and guaranty_amount (float, USD with 2 decimal places, the guaranty
        recorded as in force).
    """
    amt = round(float(guaranty_amount), 2)
    day = ctx.now()[:10]
    ctx.update("loan_guaranties", loan_id, status="released_by_assumption", release_of_liability=True,
               closed_date=day, guaranty_amount=amt)
    return str({"loan_id": loan_id, "loan_status": "released_by_assumption", "release_of_liability": True,
                "release_date": day, "guaranty_amount": amt})


@tool(owner="agent", rw="write")
def restore_entitlement_by_substitution_1ad1d2fb(ctx: ToolContext, loan_id: str, assuming_veteran_name: str,
                                                 entitlement_amount: float) -> str:
    """Restore a selling veteran's home loan entitlement on a VA loan that a qualifying veteran buyer has
    assumed and for which the buyer substitutes their own entitlement.

    The representative books the restoration for the seller. One call adds one restoration entry to the
    loan's entitlement history, dated today, on the ground of substitution by the assuming veteran, and links
    the entry to the assuming veteran's VA profile found under the full name given; the seller's entitlement
    tied up in the loan is reduced by the amount restored, which becomes available to the seller for a future
    VA loan. The receipt below confirms the restoration.

    Args:
        loan_id: Id class — the reference number of the assumed VA home loan record, as returned by the loan
            lookup for the selling veteran.
        assuming_veteran_name: Verbatim class — the assuming veteran buyer's full name exactly as the selling
            veteran states it on the call, copied character for character with nothing added or dropped (verbatim).
        entitlement_amount: Fixed-format class — the amount of the seller's entitlement restored, in USD,
            2 decimal places, a positive number rounded half up to the cent before it is passed.

    Returns:
        A text rendering of a dict with these fields: entitlement_action_id (str, reference number of the new
        restoration entry), loan_id (str, the loan concerned), substitute_customer_id (str, the beneficiary
        reference number of the assuming veteran whose profile carries that full name, or None when no profile
        does), entitlement_amount (float, USD with 2 decimal places, the amount restored), action_date (str,
        YYYY-MM-DD, today's date) and status (str, always "entitlement_restored" when the entry was written).
    """
    buyer = ctx.find("customers", full_name=assuming_veteran_name)
    substitute_customer_id = buyer[0].get("customer_id") if buyer else None
    rid = ctx.make_id("les_", loan_id, assuming_veteran_name, entitlement_amount)
    amt = round(float(entitlement_amount), 2)
    day = ctx.now()[:10]
    ctx.create("loan_entitlement_actions", rid, entitlement_action_id=rid, loan_id=loan_id,
               customer_id=(ctx.find("loan_guaranties", loan_id=loan_id) or [{}])[0].get("customer_id"),
               event_type="loan_entitlement_restored", entitlement_amount=amt, action_date=day,
               restoration_basis="substitution_by_assuming_veteran", substitute_customer_id=substitute_customer_id)
    return str({"entitlement_action_id": rid, "loan_id": loan_id, "substitute_customer_id": substitute_customer_id,
                "entitlement_amount": amt, "action_date": day, "status": "entitlement_restored"})

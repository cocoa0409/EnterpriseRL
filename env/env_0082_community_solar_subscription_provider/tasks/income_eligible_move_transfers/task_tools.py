"""Hidden task tools of the income_eligible_move_transfers difficulty (Meadowlark Access Income-Eligible
Subscriptions). Each tool lands one atomic write the agent (or the household, for its own payment) has already
decided; no tool judges eligibility, ordering or amounts.
"""

from erlbench import ToolContext, tool


class _Cents:
    """Pure-Python half-up rounding to the cent or to two decimal places (no Decimal, no imports)."""

    @staticmethod
    def half_up(value) -> float:
        scaled = float(value) * 100.0
        whole = int(scaled + 0.5 + 1e-9) if scaled >= 0 else -int(-scaled + 0.5 + 1e-9)
        return whole / 100.0


@tool(owner="agent", rw="write")
def file_move_reassignment_5a7d54a1(ctx: ToolContext, access_sub_id: str, access_request_id: str, kw: float,
                                    filing_month: str, effective_date: str) -> str:
    """Files the move of a Meadowlark Access share to the new utility account named in its pending move
    transfer request. One call writes the reassignment filing line that carries the kept share to the new
    account, writes a move_resize removal line on the account being left for any part of the share on file
    that is not kept (no line when the whole share is kept), sets the share on file to the kept kW, and marks
    the move transfer request as filed with its effective date. The subscription stays in transfer_pending
    status until the utility applies the filing. Success is a receipt naming the new filing lines.

    Args:
        access_sub_id: Id class — the reference number of the Meadowlark Access subscription being moved, as
            returned by the Access subscription lookup.
        access_request_id: Id class — the reference number of the household's move transfer request, as
            returned by the Access request lookup.
        kw: Fixed-format class — the kW of share filed to the new utility account, in kW AC, 2 decimal places,
            always greater than 0.00; it is stored rounded half up to 2 decimal places.
        filing_month: Fixed-format class — the calendar month of the allocation schedule that carries the
            filing, written YYYY-MM.
        effective_date: Fixed-format class — the day from which the utility applies the filing, written YYYY-MM-DD.

    Returns:
        A dict with: status ("filed" when both writes landed); reassignment_line_id (reference of the new
        reassignment filing line); resize_line_id (reference of the move_resize removal line, or an empty
        string when the whole share is kept); kw_reassigned (the kept kW filed, 2 decimal places);
        kw_removed (the kW removed by the move_resize line, 2 decimal places, 0.0 when none);
        new_utility_account_id (reference of the receiving utility account); effective_date (YYYY-MM-DD).
    """
    sub = ctx.find("access_subscriptions", access_sub_id=access_sub_id)[0]
    kept = _Cents.half_up(kw)
    removed = _Cents.half_up(float(sub.get("allocation_kw") or 0) - kept)
    new_account = sub.get("pending_utility_account_id") or ""
    rid = ctx.make_id("aal_", access_sub_id, access_request_id, kept, filing_month, effective_date)
    ctx.create("access_allocations", rid, access_filing_id=rid, access_sub_id=access_sub_id,
               customer_id=sub.get("customer_id"), event_type="access_allocation_reassigned",
               utility_account_id=new_account, kw=kept, filing_month=filing_month,
               effective_date=effective_date, filing_reason="move_transfer", access_request_id=access_request_id)
    resize_id = ""
    if removed > 0:
        resize_id = ctx.make_id("aar_", access_sub_id, access_request_id, removed, filing_month, effective_date)
        ctx.create("access_allocations", resize_id, access_filing_id=resize_id, access_sub_id=access_sub_id,
                   customer_id=sub.get("customer_id"), event_type="access_allocation_reduced",
                   utility_account_id=sub.get("utility_account_id"), kw=removed, filing_month=filing_month,
                   effective_date=effective_date, filing_reason="move_resize", access_request_id="")
    ctx.update("access_subscriptions", access_sub_id, allocation_kw=kept)
    ctx.update("access_requests", access_request_id, outcome="filed", effective_date=effective_date)
    return str({"status": "filed", "reassignment_line_id": rid, "resize_line_id": resize_id,
                "kw_reassigned": kept, "kw_removed": removed if removed > 0 else 0.0,
                "new_utility_account_id": new_account, "effective_date": effective_date})


@tool(owner="user", rw="write")
def pay_move_settlement_0f5b0288(ctx: ToolContext, access_sub_id: str, amount: float, payment_method: str) -> str:
    """The household itself pays, through Meadowlark's secure payment portal, a settlement payment on a
    Meadowlark Access subscription that is awaiting its move to a new utility account. One call records the
    payment received on the subscription's billing ledger on today's date with the method the household used;
    no card or bank details pass through Meadowlark staff. Success is a payment receipt the household can quote.

    Args:
        access_sub_id: Id class — the reference number of the Meadowlark Access subscription being paid, as
            returned by the Access subscription lookup and given to the household by the agent.
        amount: Fixed-format class — the payment amount in USD, 2 decimal places, greater than 0.00; it is
            recorded rounded half up to the cent.
        payment_method: Enum class — how the household pays: ach when the household pays in the portal from a
            bank account by electronic transfer; card when the household pays in the portal with a debit or
            credit card; check when the household's mailed check is the payment being recorded;
            utility_remittance only for the utility's own remittance under consolidated billing, never a
            household payment; not_applicable is not a payment method and is never used for a payment.

    Returns:
        A dict with: status ("received" when the payment is recorded); payment_id (the payment receipt
        reference); amount (USD, 2 decimal places); payment_method (the method recorded); received_date
        (YYYY-MM-DD).
    """
    sub = ctx.find("access_subscriptions", access_sub_id=access_sub_id)[0]
    paid = _Cents.half_up(amount)
    today = ctx.now()[:10]
    rid = ctx.make_id("apy_", access_sub_id, paid, payment_method, today)
    ctx.create("access_billing", rid, access_bill_id=rid, access_sub_id=access_sub_id,
               customer_id=sub.get("customer_id"), event_type="access_payment_received", amount=paid,
               bill_date=today, billing_month=today[:7], due_date="", access_credit_id="", access_ref_bill_id="",
               charge_basis="not_applicable", billing_type=sub.get("billing_type"), payment_method=payment_method,
               credit_reason="not_applicable")
    return str({"status": "received", "payment_id": rid, "amount": paid, "payment_method": payment_method,
                "received_date": today})


@tool(owner="agent", rw="write")
def bill_pending_estimate_ff226895(ctx: ToolContext, access_sub_id: str, billing_month: str, amount: float,
                                   due_date: str, access_credit_id: str = "") -> str:
    """Bills an estimated subscription charge on a Meadowlark Access subscription awaiting its move, for a
    statement month whose utility credit statement has not been reported. One call writes one estimated charge
    line (no credit statement reference) dated today on the billing ledger, carrying the subscription's billing
    arrangement and the due date given. Success is a receipt naming the new charge line.

    Args:
        access_sub_id: Id class — the reference number of the Meadowlark Access subscription, as returned by the
            Access subscription lookup.
        billing_month: Fixed-format class — the statement month the estimate stands in for, written YYYY-MM.
        amount: Fixed-format class — the estimated charge in USD, 2 decimal places, greater than 0.00; it is
            recorded rounded half up to the cent.
        due_date: Fixed-format class — the date the estimated charge falls due, written YYYY-MM-DD.
        access_credit_id: Id class — the reference number of the credit statement line the charge prices, as
            returned by the Access credit statement lookup; an estimated charge prices no credit statement line,
            so it is passed as an empty string.

    Returns:
        A dict with: status ("billed" when the line is written); charge_id (reference of the estimated charge
        line); billing_month (YYYY-MM); amount (USD, 2 decimal places); bill_date (YYYY-MM-DD); due_date
        (YYYY-MM-DD).
    """
    sub = ctx.find("access_subscriptions", access_sub_id=access_sub_id)[0]
    value = _Cents.half_up(amount)
    today = ctx.now()[:10]
    rid = ctx.make_id("aes_", access_sub_id, billing_month, value, due_date)
    ctx.create("access_billing", rid, access_bill_id=rid, access_sub_id=access_sub_id,
               customer_id=sub.get("customer_id"), event_type="access_charge_billed", amount=value,
               bill_date=today, billing_month=billing_month, due_date=due_date, access_credit_id=access_credit_id,
               access_ref_bill_id="", charge_basis="estimated", billing_type=sub.get("billing_type"),
               payment_method="not_applicable", credit_reason="not_applicable")
    return str({"status": "billed", "charge_id": rid, "billing_month": billing_month, "amount": value,
                "bill_date": today, "due_date": due_date})


@tool(owner="agent", rw="write")
def credit_partial_reversal_7609dc6e(ctx: ToolContext, access_sub_id: str, access_ref_bill_id: str,
                                     access_credit_id: str, billing_month: str, amount: float) -> str:
    """Posts the reversal-correction billing credit on a Meadowlark Access subscription awaiting its move,
    for a credit statement the utility partly reversed once a subscription charge had priced it. One call writes
    one billing credit line dated today, with credit_reason credit_reversal_correction, that refers to the
    charge it offsets and carries the reversal line; it lowers the subscription's balance. Success is a receipt
    naming the new credit line.

    Args:
        access_sub_id: Id class — the reference number of the Meadowlark Access subscription, as returned by the
            Access subscription lookup.
        access_ref_bill_id: Id class — the reference number of the subscription charge line the correction
            offsets, as returned by the Access billing lookup.
        access_credit_id: Id class — the reference number of the utility's reversal line, as returned by the
            Access credit statement lookup.
        billing_month: Fixed-format class — the statement month of the reversed credit statement, written
            YYYY-MM.
        amount: Fixed-format class — the correction credit in USD, 2 decimal places, greater than 0.00; it is
            recorded rounded half up to the cent.

    Returns:
        A dict with: status ("credited" when the line is written); credit_id (reference of the billing credit
        line); amount (USD, 2 decimal places); refers_to (the charge line reference); reversal_line (the reversal
        line reference); posted_date (YYYY-MM-DD).
    """
    sub = ctx.find("access_subscriptions", access_sub_id=access_sub_id)[0]
    value = _Cents.half_up(amount)
    today = ctx.now()[:10]
    rid = ctx.make_id("arc_", access_sub_id, access_ref_bill_id, access_credit_id, billing_month, value)
    ctx.create("access_billing", rid, access_bill_id=rid, access_sub_id=access_sub_id,
               customer_id=sub.get("customer_id"), event_type="access_billing_credited", amount=value,
               bill_date=today, billing_month=billing_month, due_date="", access_credit_id=access_credit_id,
               access_ref_bill_id=access_ref_bill_id, charge_basis="not_applicable",
               billing_type=sub.get("billing_type"), payment_method="not_applicable",
               credit_reason="credit_reversal_correction")
    return str({"status": "credited", "credit_id": rid, "amount": value, "refers_to": access_ref_bill_id,
                "reversal_line": access_credit_id, "posted_date": today})


@tool(owner="user", rw="write")
def pay_closing_balance_ce594868(ctx: ToolContext, access_sub_id: str, amount: float, payment_method: str) -> str:
    """The household itself pays, through Meadowlark's secure payment portal, a closing payment on a
    Meadowlark Access subscription that has closed at a move. One call records the payment received on the
    closed subscription's billing ledger on today's date with the method the household used; no card or bank
    details pass through Meadowlark staff. Success is a payment receipt the household can quote.

    Args:
        access_sub_id: Id class — the reference number of the closed Meadowlark Access subscription, as returned
            by the Access subscription lookup and given to the household by the agent.
        amount: Fixed-format class — the payment amount in USD, 2 decimal places, greater than 0.00; it is
            recorded rounded half up to the cent.
        payment_method: Enum class — how the household pays: ach when the household pays in the portal from a
            bank account by electronic transfer; card when the household pays in the portal with a debit or
            credit card; check when the household's mailed check is the payment being recorded;
            utility_remittance only for the utility's own remittance under consolidated billing, never a
            household payment; not_applicable is not a payment method and is never used for a payment.

    Returns:
        A dict with: status ("received" when the payment is recorded); payment_id (the payment receipt
        reference); amount (USD, 2 decimal places); payment_method (the method recorded); received_date
        (YYYY-MM-DD).
    """
    sub = ctx.find("access_subscriptions", access_sub_id=access_sub_id)[0]
    paid = _Cents.half_up(amount)
    today = ctx.now()[:10]
    rid = ctx.make_id("apc_", access_sub_id, paid, payment_method, today)
    ctx.create("access_billing", rid, access_bill_id=rid, access_sub_id=access_sub_id,
               customer_id=sub.get("customer_id"), event_type="access_payment_received", amount=paid,
               bill_date=today, billing_month=today[:7], due_date="", access_credit_id="", access_ref_bill_id="",
               charge_basis="not_applicable", billing_type=sub.get("billing_type"), payment_method=payment_method,
               credit_reason="not_applicable")
    return str({"status": "received", "payment_id": rid, "amount": paid, "payment_method": payment_method,
                "received_date": today})


@tool(owner="agent", rw="write")
def bill_closing_estimate_4dff6268(ctx: ToolContext, access_sub_id: str, billing_month: str, amount: float,
                                   due_date: str, access_credit_id: str = "") -> str:
    """Bills an estimated subscription charge on a Meadowlark Access subscription that closed at a move,
    for a statement month of the share's service whose utility credit statement has not been reported. One call
    writes one estimated charge line (no credit statement reference) dated today on the closed subscription's
    billing ledger, carrying its billing arrangement and the due date given. Success is a receipt naming the new
    charge line.

    Args:
        access_sub_id: Id class — the reference number of the closed Meadowlark Access subscription, as returned
            by the Access subscription lookup.
        billing_month: Fixed-format class — the statement month the estimate stands in for, written YYYY-MM.
        amount: Fixed-format class — the estimated charge in USD, 2 decimal places, greater than 0.00; it is
            recorded rounded half up to the cent.
        due_date: Fixed-format class — the date the estimated charge falls due, written YYYY-MM-DD.
        access_credit_id: Id class — the reference number of the credit statement line the charge prices, as
            returned by the Access credit statement lookup; an estimated charge prices no credit statement line,
            so it is passed as an empty string.

    Returns:
        A dict with: status ("billed" when the line is written); charge_id (reference of the estimated charge
        line); billing_month (YYYY-MM); amount (USD, 2 decimal places); bill_date (YYYY-MM-DD); due_date
        (YYYY-MM-DD).
    """
    sub = ctx.find("access_subscriptions", access_sub_id=access_sub_id)[0]
    value = _Cents.half_up(amount)
    today = ctx.now()[:10]
    rid = ctx.make_id("acs_", access_sub_id, billing_month, value, due_date)
    ctx.create("access_billing", rid, access_bill_id=rid, access_sub_id=access_sub_id,
               customer_id=sub.get("customer_id"), event_type="access_charge_billed", amount=value,
               bill_date=today, billing_month=billing_month, due_date=due_date, access_credit_id=access_credit_id,
               access_ref_bill_id="", charge_basis="estimated", billing_type=sub.get("billing_type"),
               payment_method="not_applicable", credit_reason="not_applicable")
    return str({"status": "billed", "charge_id": rid, "billing_month": billing_month, "amount": value,
                "bill_date": today, "due_date": due_date})


@tool(owner="agent", rw="write")
def credit_closed_reversal_cc3dddf3(ctx: ToolContext, access_sub_id: str, access_ref_bill_id: str,
                                    access_credit_id: str, billing_month: str, amount: float) -> str:
    """Posts the reversal-correction billing credit on a Meadowlark Access subscription that closed at a
    move, for a credit statement the utility partly reversed once a subscription charge had priced it. One call
    writes one billing credit line dated today, with credit_reason credit_reversal_correction, that refers to the
    charge it offsets and carries the reversal line; it lowers the closed subscription's balance. Success is a
    receipt naming the new credit line.

    Args:
        access_sub_id: Id class — the reference number of the closed Meadowlark Access subscription, as returned
            by the Access subscription lookup.
        access_ref_bill_id: Id class — the reference number of the subscription charge line the correction
            offsets, as returned by the Access billing lookup.
        access_credit_id: Id class — the reference number of the utility's reversal line, as returned by the
            Access credit statement lookup.
        billing_month: Fixed-format class — the statement month of the reversed credit statement, written
            YYYY-MM.
        amount: Fixed-format class — the correction credit in USD, 2 decimal places, greater than 0.00; it is
            recorded rounded half up to the cent.

    Returns:
        A dict with: status ("credited" when the line is written); credit_id (reference of the billing credit
        line); amount (USD, 2 decimal places); refers_to (the charge line reference); reversal_line (the reversal
        line reference); posted_date (YYYY-MM-DD).
    """
    sub = ctx.find("access_subscriptions", access_sub_id=access_sub_id)[0]
    value = _Cents.half_up(amount)
    today = ctx.now()[:10]
    rid = ctx.make_id("acr_", access_sub_id, access_ref_bill_id, access_credit_id, billing_month, value)
    ctx.create("access_billing", rid, access_bill_id=rid, access_sub_id=access_sub_id,
               customer_id=sub.get("customer_id"), event_type="access_billing_credited", amount=value,
               bill_date=today, billing_month=billing_month, due_date="", access_credit_id=access_credit_id,
               access_ref_bill_id=access_ref_bill_id, charge_basis="not_applicable",
               billing_type=sub.get("billing_type"), payment_method="not_applicable",
               credit_reason="credit_reversal_correction")
    return str({"status": "credited", "credit_id": rid, "amount": value, "refers_to": access_ref_bill_id,
                "reversal_line": access_credit_id, "posted_date": today})

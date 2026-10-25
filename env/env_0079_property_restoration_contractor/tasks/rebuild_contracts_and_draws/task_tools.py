"""Hidden task tools for the rebuild_contracts_and_draws difficulty (Reconstruction contracts).

Each tool performs one atomic write the agent or the customer has already decided on; none of them
checks a business precondition or works out an amount.
"""

from decimal import Decimal, ROUND_HALF_UP

from erlbench import ToolContext, tool


class _Fmt:
    """Formatting helpers shared by the tools (exact cent rounding, half up)."""

    @staticmethod
    def cents(value) -> float:
        return float(Decimal(str(value)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP))


@tool(owner="user", rw="write")
def sign_change_order_7ffbf290(ctx: ToolContext, rebuild_contract_id: str, change_order_id: str, amount: float) -> str:
    """The customer signs an additive change order proposal (one that adds scope or cost) on their own
    reconstruction contract, and the signed
    change order is booked to the contract at the amount the customer signs for. One call marks that
    change order proposal as signed and records the signed amount on it, adds one change order charge
    line for that amount to the contract, dated today, and raises the contract balance by the same
    amount. Afterwards the change order shows as signed with its amount, the new charge line appears
    among the contract's charges, and the contract balance is higher by the amount signed.

    Args:
        rebuild_contract_id: Id class — the reference number of the customer's reconstruction contract
            the change order amends, as returned by the reconstruction contract lookup.
        change_order_id: Id class — the reference number of the change order proposal being signed, as
            returned by the change order lookup for that contract.
        amount: Fixed-format class — the change order amount the customer signs for, in US dollars, a
            number with exactly 2 decimal places; any further digits are rounded to the cent, half up,
            before booking.

    Returns:
        A one-line confirmation string naming the booked charge line reference (a text id beginning
        "rbc_"), the change order reference, the amount booked in US dollars with 2 decimals and the
        new contract balance in US dollars with 2 decimals; the presence of the charge line reference
        means the signature was recorded and the charge booked.
    """
    amt = _Fmt.cents(amount)
    rows = ctx.find("rebuild_contracts", rebuild_contract_id=rebuild_contract_id)
    contract = rows[0] if rows else {}
    today = ctx.now()[:10]
    ctx.update("rebuild_change_orders", change_order_id, co_status="signed", amount=amt)
    rid = ctx.make_id("rbc_", rebuild_contract_id, change_order_id, amt)
    ctx.create("rebuild_charges", rid, rebuild_charge_id=rid, rebuild_contract_id=rebuild_contract_id,
               customer_id=contract.get("customer_id", ""), event_type="rebuild_change_order_charge",
               charge_code="change_order", change_order_id=change_order_id, posted_date=today, amount=amt)
    new_balance = _Fmt.cents(float(contract.get("contract_balance") or 0) + amt)
    ctx.update("rebuild_contracts", rebuild_contract_id, contract_balance=new_balance)
    return (f"Change order {change_order_id} signed; charge line {rid} booked for {amt:.2f} USD; "
            f"contract balance now {new_balance:.2f} USD.")


@tool(owner="agent", rw="write")
def request_final_draw_345d01eb(ctx: ToolContext, rebuild_contract_id: str, draw_milestone: str, draw_number: int,
                                funding_route: str, lien_waiver_type: str, due_date: str, requested_amount: float) -> str:
    """Request a milestone draw, the final draw included, on a reconstruction contract. One call records a new
    draw request at the named milestone on that contract, dated today, carrying the draw's sequence number,
    who funds it, the lien waiver delivered with it, its due date and the amount requested.
    The contract balance does not change; the draw appears among the contract's draw requests and can then be
    paid or posted against.

    Args:
        rebuild_contract_id: Id class — the reference number of the reconstruction contract the draw is
            requested on, as returned by the reconstruction contract lookup.
        draw_milestone: Enum class — the contract milestone the draw bills, exactly one of: contract_signing
            (the deposit draw at signing); framing_complete (framing finished); rough_in_complete (rough-in
            finished); drywall_complete (drywall finished); finishes_complete (finishes installed);
            substantial_completion (the final draw after the final walkthrough); retainage_release (the
            release of amounts withheld or held back from earlier draws).
        draw_number: Fixed-format class — the sequence number of this draw on the contract, an integer
            counting every draw requested on the contract including this one, starting at 1.
        funding_route: Enum class — who funds the draw, exactly one of: customer (the owner pays the draw
            from their own funds); carrier_direct (the draw is paid from carrier payments that reached the
            company); mortgagee_release (the draw is released from the mortgagee's loss-draft account).
        lien_waiver_type: Enum class — the lien waiver delivered with the request, exactly one of: none (no
            lien waiver accompanies the request); conditional_progress (a conditional progress lien waiver
            accompanies an interim draw); conditional_final (a conditional final lien waiver accompanies the
            final draw).
        due_date: Fixed-format class — the date the draw is due, written YYYY-MM-DD in the company's local
            calendar, or an empty string when the draw carries no due date.
        requested_amount: Fixed-format class — the amount requested on the draw, in US dollars, a number
            with exactly 2 decimal places; any further digits are rounded to the cent, half up.

    Returns:
        A one-line confirmation string naming the new draw request reference (a text id beginning "rbd_"),
        the milestone billed, the draw number, the funding route and the amount requested in
        US dollars with 2 decimals; the presence of the draw reference means the request was recorded.
    """
    amt = _Fmt.cents(requested_amount)
    rows = ctx.find("rebuild_contracts", rebuild_contract_id=rebuild_contract_id)
    contract = rows[0] if rows else {}
    rid = ctx.make_id("rbd_", rebuild_contract_id, draw_milestone, draw_number, funding_route, lien_waiver_type, due_date, amt)
    ctx.create("rebuild_draws", rid, rebuild_draw_id=rid, rebuild_contract_id=rebuild_contract_id,
               customer_id=contract.get("customer_id", ""), event_type="rebuild_draw_request",
               draw_milestone=draw_milestone, draw_number=int(draw_number), funding_route=funding_route,
               lien_waiver_type=lien_waiver_type, request_date=ctx.now()[:10], due_date=due_date,
               requested_amount=amt)
    return (f"Draw {rid} requested at {draw_milestone} (draw {int(draw_number)}, {funding_route}) "
            f"for {amt:.2f} USD.")


@tool(owner="user", rw="write")
def sign_deductive_change_order_5bfd6b95(ctx: ToolContext, rebuild_contract_id: str, change_order_id: str, amount: float) -> str:
    """The customer signs a deductive change order proposal that removes scope from their own reconstruction
    contract, and the signed credit is posted to the contract. One call marks that deductive proposal as signed
    and records the credit amount on it, adds one change order credit line, dated today, naming that change
    order and carrying the credit, and lowers the contract balance by the same amount. Afterwards the change
    order shows as signed with its credit amount, the credit line appears among the contract's payments and
    credits, and the contract balance is lower by the credit.

    Args:
        rebuild_contract_id: Id class — the reference number of the customer's reconstruction contract the
            deductive change order amends, as returned by the reconstruction contract lookup.
        change_order_id: Id class — the reference number of the deductive change order proposal being signed,
            as returned by the change order lookup for that contract.
        amount: Fixed-format class — the credit amount the customer signs for, in US dollars, a number with
            exactly 2 decimal places; any further digits are rounded to the cent, half up.

    Returns:
        A one-line confirmation string naming the credit line reference (a text id beginning "rbp_"), the
        change order reference, the credit amount in US dollars with 2 decimals and the new contract balance in
        US dollars with 2 decimals; the presence of the credit line reference means the signature was recorded
        and the credit posted.
    """
    amt = _Fmt.cents(amount)
    rows = ctx.find("rebuild_contracts", rebuild_contract_id=rebuild_contract_id)
    contract = rows[0] if rows else {}
    ctx.update("rebuild_change_orders", change_order_id, co_status="signed", amount=amt)
    rid = ctx.make_id("rbp_", rebuild_contract_id, change_order_id, amt)
    ctx.create("rebuild_payments", rid, rebuild_payment_id=rid, rebuild_contract_id=rebuild_contract_id,
               customer_id=contract.get("customer_id", ""), event_type="rebuild_change_order_credit",
               rebuild_draw_id=None, payment_method=None, payment_reference=None, claim_payment_id=None,
               change_order_id=change_order_id, posted_date=ctx.now()[:10], amount=amt)
    new_balance = _Fmt.cents(float(contract.get("contract_balance") or 0) - amt)
    ctx.update("rebuild_contracts", rebuild_contract_id, contract_balance=new_balance)
    return (f"Deductive change order {change_order_id} signed; credit line {rid} posted for {amt:.2f} USD; "
            f"contract balance now {new_balance:.2f} USD.")


@tool(owner="agent", rw="write")
def post_overdue_draw_charge_f6859441(ctx: ToolContext, rebuild_contract_id: str, rebuild_draw_id: str,
                                      fee_period: str, amount: float) -> str:
    """Post an overdue draw charge for one monthly fee period on a past-due draw of a reconstruction contract.
    One call adds one overdue draw charge line, dated today, naming the draw and the fee period and carrying
    the charge amount, and raises the contract balance by the same amount. Afterwards the charge appears among
    the contract's charges and the contract balance is higher by the charge.

    Args:
        rebuild_contract_id: Id class — the reference number of the reconstruction contract, as returned by
            the reconstruction contract lookup.
        rebuild_draw_id: Id class — the reference number of the overdue draw the charge is assessed on, as
            returned by the draw lookup for that contract.
        fee_period: Fixed-format class — the calendar month fee period the charge is for, written YYYY-MM.
        amount: Fixed-format class — the charge amount in US dollars, a number with exactly 2 decimal places;
            any further digits are rounded to the cent, half up.

    Returns:
        A one-line confirmation string naming the new charge line reference (a text id beginning "rbo_"), the
        draw reference, the fee period, the charge amount in US dollars with 2 decimals and the new contract
        balance in US dollars with 2 decimals; the presence of the charge line reference means the charge was
        posted.
    """
    amt = _Fmt.cents(amount)
    period = str(fee_period).strip()[:7]
    rows = ctx.find("rebuild_contracts", rebuild_contract_id=rebuild_contract_id)
    contract = rows[0] if rows else {}
    rid = ctx.make_id("rbo_", rebuild_contract_id, rebuild_draw_id, period, amt)
    ctx.create("rebuild_charges", rid, rebuild_charge_id=rid, rebuild_contract_id=rebuild_contract_id,
               customer_id=contract.get("customer_id", ""), event_type="rebuild_overdue_draw_charge",
               charge_code="overdue_draw_charge", change_order_id=None, permit_type=None,
               rebuild_draw_id=rebuild_draw_id, warranty_claim_id=None, fee_period=period,
               posted_date=ctx.now()[:10], amount=amt)
    new_balance = _Fmt.cents(float(contract.get("contract_balance") or 0) + amt)
    ctx.update("rebuild_contracts", rebuild_contract_id, contract_balance=new_balance)
    return (f"Overdue draw charge {rid} posted on draw {rebuild_draw_id} for {period}: {amt:.2f} USD; "
            f"contract balance now {new_balance:.2f} USD.")


@tool(owner="user", rw="write")
def pay_past_due_draw_ec4ba96a(ctx: ToolContext, rebuild_contract_id: str, rebuild_draw_id: str,
                               payment_method: str, amount: float) -> str:
    """The customer pays toward a past-due draw on their own reconstruction contract through the company's
    secure payment channel. One call records one draw payment, dated today, naming the draw, the tender used
    and the amount, issues a confirmation number for it, and lowers the contract balance by the amount paid.
    Afterwards the payment appears among the contract's payments with its confirmation number and the contract
    balance is lower by the payment.

    Args:
        rebuild_contract_id: Id class — the reference number of the customer's reconstruction contract, as
            given to the customer by the representative from the reconstruction contract lookup.
        rebuild_draw_id: Id class — the reference number of the draw the payment pays, as given to the
            customer by the representative from the draw lookup for that contract.
        payment_method: Enum class — the tender used, exactly one of: debit_card (paid with the customer's
            debit card); ach (an electronic transfer from the customer's bank account); check (a paper check);
            wire (a bank wire transfer); mortgagee_check (a check issued by the mortgagee from its loss-draft
            account).
        amount: Fixed-format class — the amount paid in US dollars, a number with exactly 2 decimal places; any
            further digits are rounded to the cent, half up.

    Returns:
        A one-line confirmation string naming the payment confirmation number (a text id beginning "rpy_"), the
        draw reference, the tender, the amount paid in US dollars with 2 decimals and the new contract balance in
        US dollars with 2 decimals; the presence of the confirmation number means the payment was recorded.
    """
    amt = _Fmt.cents(amount)
    rows = ctx.find("rebuild_contracts", rebuild_contract_id=rebuild_contract_id)
    contract = rows[0] if rows else {}
    rid = ctx.make_id("rpy_", rebuild_contract_id, rebuild_draw_id, payment_method, amt)
    ctx.create("rebuild_payments", rid, rebuild_payment_id=rid, rebuild_contract_id=rebuild_contract_id,
               customer_id=contract.get("customer_id", ""), event_type="rebuild_draw_payment",
               rebuild_draw_id=rebuild_draw_id, payment_method=payment_method, payment_reference=rid,
               claim_payment_id=None, change_order_id=None, posted_date=ctx.now()[:10], amount=amt)
    new_balance = _Fmt.cents(float(contract.get("contract_balance") or 0) - amt)
    ctx.update("rebuild_contracts", rebuild_contract_id, contract_balance=new_balance)
    return (f"Payment {rid} recorded on draw {rebuild_draw_id} by {payment_method}: {amt:.2f} USD; "
            f"contract balance now {new_balance:.2f} USD.")

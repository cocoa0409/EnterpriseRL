"""Hidden task tools of the grain marketing desk (difficulty: grain_marketing_desk).

Each function performs one atomic write the desk records against a member's grain
marketing contract. The tools are never listed: an agent reaches them only through
unlock_agent_discoverable_tool / call_agent_discoverable_tool, or, where the act is the
member's own, unlock_user_discoverable_tool / call_user_discoverable_tool. None of them
computes a figure, aggregates ledger history or judges whether the write is due; the
agent works that out from the published policy and the member's records first.
"""

from erlbench import ToolContext, tool


@tool(owner="agent", rw="write")
def record_contract_delivery_balance_c52b7782(ctx: ToolContext, contract_id: str,
                                              bushels_still_owed: float) -> str:
    """Restate, on one grain marketing contract, the bushels the member still owes against it.

    The grain desk uses this when the loads standing on a member's grain ledger no longer agree
    with the balance printed on the contract. The call replaces the contract's bushels-still-owed
    figure with the one supplied and leaves everything else on the contract as it stands: the
    programme, the commodity, the crop year, the committed bushels, the delivery window and the
    contract's lifecycle standing are untouched. On success the member's contract record shows the
    new balance in place of the old one, and a confirmation naming the contract and the balance
    now standing is returned.

    Args:
        contract_id: Id class — the internal reference of the grain marketing contract whose
            balance is being restated; it identifies one contract record and is reachable from the
            grain contract lookup for the member before this call.
        bushels_still_owed: Fixed-format class — the bushels the member still owes on the contract
            after the restatement, expressed in bushels, whole number, with no thousands separator
            and no unit suffix; a value carrying a fractional part is stored rounded half to even
            to 2 decimal places, and zero is written as 0 rather than left blank.

    Returns:
        A single confirmation sentence in plain text. It names the contract reference the
        restatement landed on and repeats the bushels-still-owed figure now standing on that
        contract, in bushels to 2 decimal places; the presence of that sentence, rather than an
        error text, is what indicates the restatement was recorded.
    """
    ctx.update("grain_contracts", contract_id,
               open_bushels=round(float(bushels_still_owed), 2))
    return (f"Contract {contract_id} now shows {round(float(bushels_still_owed), 2)} "
            "bushels still owed.")


@tool(owner="agent", rw="write")
def book_delayed_price_carry_charge_ebb3e3fc(ctx: ToolContext, contract_id: str, customer_id: str,
                                             contract_number: str, settlement_number: str,
                                             carry_charge_amount_usd: float) -> str:
    """Book the delayed price carry charge owed on bushels that stood unpriced, onto a statement.

    The grain desk uses this to put the carry a member owes for holding bushels in the unpriced
    position onto the settlement statement those bushels were drawn onto. The call adds one charge
    line to the member's grain ledger against the named contract and statement, carrying the
    amount supplied as a delayed price service charge; no other line is touched, and a line already
    standing is left exactly as it is. On success the charge shows on the member's grain ledger
    under that statement number, and a confirmation naming the line reference and the amount booked
    is returned.

    Args:
        contract_id: Id class — the internal reference of the grain marketing contract the unpriced
            bushels belong to; it identifies one contract record and is reachable from the grain
            contract lookup for the member before this call.
        customer_id: Id class — the internal reference of the member whose ledger carries the
            charge; it identifies one membership record and is reachable from the membership
            profile lookup before this call.
        contract_number: Id class — the contract number the member quotes when hauling or pricing,
            which identifies the same marketing contract on paper; it is reachable from the grain
            contract lookup for the member before this call.
        settlement_number: Fixed-format class — the settlement statement the charge line is carried
            on, written as S- followed by six digits, e.g. S-551903, in upper case with the hyphen
            and with no spaces; it is never left blank.
        carry_charge_amount_usd: Fixed-format class — the money withheld on this charge line, in
            USD to 2 decimal places, as a positive number with no currency symbol and no thousands
            separator, rounded half away from zero at the cent when a longer value is supplied.

    Returns:
        A single confirmation sentence in plain text naming the ledger line reference minted for
        the charge, the settlement statement it was carried on, and the amount booked in USD to 2
        decimal places; that sentence, rather than an error text, is what indicates the charge line
        was added.
    """
    rid = ctx.make_id("gdp_", contract_id, customer_id, contract_number, settlement_number,
                      carry_charge_amount_usd)
    ctx.create("grain_ledger", rid, ledger_id=rid, contract_id=contract_id, customer_id=customer_id,
               event_type="grain_deduction_applied", deduction_type="dp_service_charge",
               settlement_number=settlement_number,
               amount=round(float(carry_charge_amount_usd), 2), posted_date=ctx.now()[:10])
    return (f"Carry charge line {rid} booked on statement {settlement_number} for "
            f"{round(float(carry_charge_amount_usd), 2)}.")


@tool(owner="user", rw="write")
def execute_futures_month_roll_2054762f(ctx: ToolContext, contract_id: str, customer_id: str,
                                        pricing_order_id: str, roll_charge_amount_usd: float) -> str:
    """Put through, as the member, the roll of a grain marketing contract's futures month.

    A roll disposes of the member's own grain position, so the member puts it through themselves
    against the roll instruction they have signed. The call writes one roll confirmation onto the
    member's grain ledger for the named contract, carrying the charge the roll costs them; the
    contract's programme, commodity, committed bushels and lifecycle standing are left as they
    stand. On success the roll confirmation shows on the member's grain ledger with that charge
    against it, so the charge stands to be collected with the member's grain money, and a
    confirmation naming the roll line reference and the charge carried is returned.

    Args:
        contract_id: Id class — the internal reference of the grain marketing contract being
            rolled; it identifies one contract record and is reachable from the grain contract
            lookup for the member before this call.
        customer_id: Id class — the internal reference of the member whose position is rolled; it
            identifies one membership record and is reachable from the membership profile lookup
            before this call.
        pricing_order_id: Id class — the internal reference of the signed roll instruction the
            member lodged with the grain desk; it identifies one instruction record and is
            reachable from the pricing instruction lookup for the member before this call.
        roll_charge_amount_usd: Fixed-format class — the charge the roll carries to the member, in
            USD to 2 decimal places, as a positive number with no currency symbol and no thousands
            separator, rounded half away from zero at the cent when a longer value is supplied.

    Returns:
        A single confirmation sentence in plain text naming the ledger line reference minted for
        the roll, the contract it was written against, and the charge carried in USD to 2 decimal
        places; that sentence, rather than an error text, is what indicates the roll was recorded.
    """
    rid = ctx.make_id("grl_", contract_id, customer_id, pricing_order_id, roll_charge_amount_usd)
    ctx.create("grain_ledger", rid, ledger_id=rid, contract_id=contract_id, customer_id=customer_id,
               event_type="grain_contract_rolled",
               amount=round(float(roll_charge_amount_usd), 2),
               roll_date=ctx.now()[:10], posted_date=ctx.now()[:10])
    return (f"Roll {rid} recorded on contract {contract_id} carrying "
            f"{round(float(roll_charge_amount_usd), 2)} in charges.")


@tool(owner="agent", rw="write")
def release_grain_settlement_payment_379b8a52(ctx: ToolContext, contract_id: str, customer_id: str,
                                              settlement_number: str, payment_method: str,
                                              payment_amount_usd: float) -> str:
    """Release the member's money on a grain settlement statement and record how it went out.

    The grain desk uses this to pay a member for grain drawn onto a settlement statement. The call
    writes one payment line onto the member's grain ledger against the named contract and
    statement, carrying the amount released and the way the member elected to be paid; the
    statement itself, its charge lines and the contract's standing are left as they are. On success
    the payment shows on the member's grain ledger against that statement, the money is out of the
    grain account, and a confirmation naming the payment line reference, the statement and the
    amount released is returned.

    Args:
        contract_id: Id class — the internal reference of the grain marketing contract the
            statement was drawn on; it identifies one contract record and is reachable from the
            grain contract lookup for the member before this call.
        customer_id: Id class — the internal reference of the member being paid; it identifies one
            membership record and is reachable from the membership profile lookup before this call.
        settlement_number: Fixed-format class — the settlement statement being paid, written as S-
            followed by six digits, e.g. S-551903, in upper case with the hyphen and with no
            spaces; it is never left blank.
        payment_method: Enum class — how the money reaches the member on this release, one of:
            check, used where the member is paid by a cheque drawn on the cooperative and mailed or
            held for collection; ach, used where the money is sent by direct deposit to the bank
            account the member has lodged; credit_to_input_account, used where the member has
            elected the whole of this money to be applied against their crop input account instead
            of being paid out; deferred_payment, used where the member has elected the payment to
            be held and released in a later tax year under a deferral their programme allows.
        payment_amount_usd: Fixed-format class — the money released to the member on this payment,
            in USD to 2 decimal places, as a positive number with no currency symbol and no
            thousands separator, rounded half away from zero at the cent when a longer value is
            supplied.

    Returns:
        A single confirmation sentence in plain text naming the ledger line reference minted for
        the payment, the settlement statement it was released against, the way it went out, and
        the amount in USD to 2 decimal places; that sentence, rather than an error text, is what
        indicates the money was released.
    """
    rid = ctx.make_id("gsp_", contract_id, customer_id, settlement_number, payment_method,
                      payment_amount_usd)
    ctx.create("grain_ledger", rid, ledger_id=rid, contract_id=contract_id, customer_id=customer_id,
               event_type="grain_settlement_paid", settlement_number=settlement_number,
               payment_method=payment_method,
               net_amount=round(float(payment_amount_usd), 2),
               paid_date=ctx.now()[:10], posted_date=ctx.now()[:10])
    return (f"Payment {rid} released on statement {settlement_number} by {payment_method} for "
            f"{round(float(payment_amount_usd), 2)}.")


@tool(owner="agent", rw="write")
def countersign_grain_contract_d95afc7d(ctx: ToolContext, contract_id: str,
                                        countersigned_bushels: float) -> str:
    """Countersign a grain marketing contract application and bind it for the bushels agreed.

    The grain desk uses this to turn an application the member has signed into a contract binding on
    both sides. The call moves the contract into active standing, stamps it with today's date as the
    day it took effect, and writes the bushels the cooperative countersigns for as both the committed
    bushels and the bushels still owed, which may be fewer than the member applied for. Nothing else
    on the contract changes: the programme, the commodity, the crop year, the price terms and the
    delivery window stand as written. On success the member's contract record reads active with that
    figure against it, so loads may be applied to it and instructions worked on it, and a
    confirmation naming the contract and the bushels bound is returned.

    Args:
        contract_id: Id class — the internal reference of the grain marketing contract application
            being countersigned; it identifies one contract record and is reachable from the grain
            contract lookup for the member before this call.
        countersigned_bushels: Fixed-format class — the bushels the cooperative binds itself to take
            under the contract, expressed in bushels, whole number, with no thousands separator and
            no unit suffix; a value carrying a fractional part is stored rounded half to even to 2
            decimal places, and zero is written as 0 rather than left blank.

    Returns:
        A single confirmation sentence in plain text naming the contract reference that was
        countersigned, the date it took effect as YYYY-MM-DD, and the bushels now committed in
        bushels to 2 decimal places; that sentence, rather than an error text, is what indicates the
        contract is binding.
    """
    bound = round(float(countersigned_bushels), 2)
    ctx.update("grain_contracts", contract_id, status="active", activated_date=ctx.now()[:10],
               contracted_bushels=bound, open_bushels=bound)
    return (f"Contract {contract_id} countersigned with effect from {ctx.now()[:10]} for "
            f"{bound} bushels.")


@tool(owner="agent", rw="write")
def register_contract_amendment_850dd44e(ctx: ToolContext, contract_id: str, contract_number: str,
                                         revised_delivery_end_date: str, amendment_count: int,
                                         revised_contracted_bushels: float) -> str:
    """Register a written amendment against a live grain marketing contract.

    The grain desk uses this to record an amendment the member has signed: it moves the last day of
    the contract's delivery window to the date supplied, restates the bushels the contract commits,
    and sets the running count of amendments the contract has taken. The programme, the commodity,
    the crop year, the delivery point, the bushels still owed and the contract's lifecycle standing
    are left as they are. On success the member's contract record shows the new last day and the
    revised commitment in place of the old ones, and a confirmation naming the contract, the revised
    window and the revised commitment is returned.

    Args:
        contract_id: Id class — the internal reference of the grain marketing contract the amendment
            is registered against; it identifies one contract record and is reachable from the grain
            contract lookup for the member before this call.
        contract_number: Id class — the contract number the member quotes when hauling or pricing,
            which identifies the same marketing contract on paper; it is reachable from the grain
            contract lookup for the member before this call.
        revised_delivery_end_date: Fixed-format class — the revised last day of the contracted
            delivery window, written as YYYY-MM-DD on the cooperative's local calendar, a delivery
            made on that day still counting as inside the window; it is never left blank.
        amendment_count: Fixed-format class — the running number of amendments the contract has
            taken once this one is registered, expressed as a whole number, count, with no
            separator; it is never left blank and is written as an integer.
        revised_contracted_bushels: Fixed-format class — the bushels the contract commits once the
            amendment is registered, expressed in bushels, whole number, with no thousands separator
            and no unit suffix; a value carrying a fractional part is stored rounded half to even to
            2 decimal places, and zero is written as 0 rather than left blank.

    Returns:
        A single confirmation sentence in plain text naming the contract number the amendment was
        registered against, the revised last day of the delivery window as YYYY-MM-DD, and the
        bushels the contract now commits in bushels to 2 decimal places; that sentence, rather than
        an error text, is what indicates the amendment is on the record.
    """
    ctx.update("grain_contracts", contract_id, delivery_end_date=revised_delivery_end_date,
               amendment_count=int(amendment_count),
               contracted_bushels=round(float(revised_contracted_bushels), 2))
    return (f"Amendment registered on contract {contract_number}: delivery window now runs to "
            f"{revised_delivery_end_date} with {round(float(revised_contracted_bushels), 2)} bushels committed.")


@tool(owner="user", rw="write")
def execute_contract_buyout_11de6ced(ctx: ToolContext, contract_id: str, customer_id: str,
                                     buyout_charge_usd: float) -> str:
    """Buy out, as the member, the undelivered balance of a grain marketing contract.

    Walking away from bushels the member has sold is the member's own act, so the member puts the
    buyout through themselves in person. The call closes the
    contract out: it books the buyout charge as a line on the member's grain ledger, moves the
    contract into cancelled standing, stamps today's date as the day it closed and takes the bushels
    still owed to zero, so no further delivery is expected and no default arises on it. On success
    the member's records show the contract closed with that charge standing against it, and a
    confirmation naming the charge line reference, the contract and the amount charged is returned.

    Args:
        contract_id: Id class — the internal reference of the grain marketing contract being bought
            out; it identifies one contract record and is reachable from the grain contract lookup
            for the member before this call.
        customer_id: Id class — the internal reference of the member buying the contract out; it
            identifies one membership record and is reachable from the membership profile lookup
            before this call.
        buyout_charge_usd: Fixed-format class — the charge the member pays to be released from the
            undelivered bushels, in USD to 2 decimal places, as a positive number with no currency
            symbol and no thousands separator, rounded half away from zero at the cent when a longer
            value is supplied.

    Returns:
        A single confirmation sentence in plain text naming the ledger line reference minted for the
        buyout charge, the contract that was closed out, and the amount charged in USD to 2 decimal
        places; that sentence, rather than an error text, is what indicates the contract is bought
        out.
    """
    rid = ctx.make_id("gbo_", contract_id, customer_id, buyout_charge_usd)
    ctx.create("grain_ledger", rid, ledger_id=rid, contract_id=contract_id, customer_id=customer_id,
               event_type="grain_deduction_applied", deduction_type="contract_buyout",
               amount=round(float(buyout_charge_usd), 2), posted_date=ctx.now()[:10])
    ctx.update("grain_contracts", contract_id, status="cancelled", closed_date=ctx.now()[:10],
               open_bushels=0.0)
    return (f"Buyout {rid} put through on contract {contract_id}: charge "
            f"{round(float(buyout_charge_usd), 2)} booked and the contract closed out.")

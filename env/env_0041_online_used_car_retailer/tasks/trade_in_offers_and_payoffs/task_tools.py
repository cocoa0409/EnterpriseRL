"""Hidden task tools of the trade_in_offers_and_payoffs difficulty (Kestrel Auto, Trade-In Agreements).

Each tool lands exactly one atomic entry on one trade-in agreement's ledger and moves the agreement's
undistributed trade equity by the same amount. No tool checks any business condition: the amount and the
target agreement are worked out by whoever calls it, and the tool simply records them.
"""

from erlbench import ToolContext, tool



@tool(owner="agent", rw="write")
def post_mileage_deduction_140e91ac(ctx: ToolContext, trade_in_id: str, deduction_amount: float) -> str:
    """Post a mileage overage deduction against the value of one picked-up trade-in vehicle.

    A Kestrel representative uses this to book, on the customer's trade-in agreement, the deduction taken because
    the odometer found at the pickup inspection is higher than the mileage the customer stated for the offer. One
    call books one mileage deduction entry dated today for the amount given and lowers the agreement's
    undistributed trade equity by that same amount; the entry shows in the agreement's history with the
    reason mileage_overage, and the lower equity is what the customer sees on the agreement.

    Args:
        trade_in_id: Id class — the reference number of the customer's trade-in agreement, as shown by the
            trade-in agreement lookup for this customer.
        deduction_amount: Fixed-format class — the mileage deduction to book, in USD, a positive amount given to
            2 decimal places (rounded to the nearest cent); 0.00 is not a meaningful entry.

    Returns:
        A text rendering of a dictionary receipt. Fields: 'entry_id' (string, reference number of the new
        deduction entry), 'trade_in_id' (string, the agreement it was booked on), 'adjustment_type' (string,
        always mileage_overage), 'amount' (number, USD with 2 decimal places, the deduction booked), 'posted_on'
        (string, YYYY-MM-DD, the date it posted) and 'equity_balance' (number, USD with 2 decimal places, the
        agreement's undistributed trade equity with the deduction booked). A receipt carrying an entry_id
        means the deduction is booked.
    """
    amount = round(float(deduction_amount), 2)
    entry_id = ctx.make_id("tdx_", trade_in_id, "mileage_overage", amount)
    rows = ctx.find("tradein_agreements", trade_in_id=trade_in_id)
    customer_id = rows[0].get("customer_id") if rows else ""
    ctx.create("tradein_transactions", entry_id, tradein_txn_id=entry_id, trade_in_id=trade_in_id,
               customer_id=customer_id, event_type="tradein_value_deducted", txn_date=ctx.now()[:10],
               amount=amount, adjustment_type="mileage_overage", payoff_good_through_date=None,
               per_diem_amount=0.0, quote_reference="", settlement_method="not_applicable",
               document_type="not_applicable", source_txn_id=None, linked_reference_id=None)
    balance = round(float(rows[0].get("equity_balance") or 0) - amount, 2) if rows else -amount
    if rows:
        ctx.update("tradein_agreements", trade_in_id, equity_balance=balance)
    return str({"entry_id": entry_id, "trade_in_id": trade_in_id, "adjustment_type": "mileage_overage",
                "amount": amount, "posted_on": ctx.now()[:10], "equity_balance": balance})


@tool(owner="agent", rw="write")
def record_negative_equity_rollin_4688789d(ctx: ToolContext, trade_in_id: str, purchase_order_id: str,
                                           rollin_amount: float) -> str:
    """Record on one trade-in agreement the part of its negative equity absorbed by the Kestrel Auto Finance
    contract of the purchase the trade is applied to.

    A Kestrel representative uses this to book a covering entry of the kind rolled_into_financing, dated today,
    that names the purchase order whose finance contract carries the amount. The entry raises the agreement's
    undistributed trade equity by the amount given, so the shortfall still open on the agreement drops by that
    amount; the entry shows in the agreement's history. The finance contract itself is not changed by
    this call.

    Args:
        trade_in_id: Id class — the reference number of the customer's trade-in agreement, as shown by the
            trade-in agreement lookup for this customer.
        purchase_order_id: Id class — the reference number of the purchase order the trade is applied to, as
            shown on the trade-in agreement and by the purchase order lookup.
        rollin_amount: Fixed-format class — the negative equity carried by the finance contract, in USD, a
            positive amount given to 2 decimal places (rounded to the nearest cent).

    Returns:
        A text rendering of a dictionary receipt. Fields: 'entry_id' (string, reference number of the new
        covering entry), 'trade_in_id' (string, the agreement it was booked on), 'settlement_method' (string,
        always rolled_into_financing), 'purchase_order_id' (string, the purchase order named on the entry),
        'amount' (number, USD with 2 decimal places, the amount recorded), 'posted_on' (string, YYYY-MM-DD) and
        'equity_balance' (number, USD with 2 decimal places, the undistributed trade equity with the entry
        booked; negative means a shortfall is still open). A receipt carrying an entry_id means the roll-in is
        recorded.
    """
    amount = round(float(rollin_amount), 2)
    entry_id = ctx.make_id("tdx_", trade_in_id, purchase_order_id, "rolled_into_financing", amount)
    rows = ctx.find("tradein_agreements", trade_in_id=trade_in_id)
    customer_id = rows[0].get("customer_id") if rows else ""
    ctx.create("tradein_transactions", entry_id, tradein_txn_id=entry_id, trade_in_id=trade_in_id,
               customer_id=customer_id, event_type="tradein_negative_equity_settled", txn_date=ctx.now()[:10],
               amount=amount, adjustment_type="not_applicable", payoff_good_through_date=None,
               per_diem_amount=0.0, quote_reference="", settlement_method="rolled_into_financing",
               document_type="not_applicable", source_txn_id=None, linked_reference_id=purchase_order_id)
    balance = round(float(rows[0].get("equity_balance") or 0) + amount, 2) if rows else amount
    if rows:
        ctx.update("tradein_agreements", trade_in_id, equity_balance=balance)
    return str({"entry_id": entry_id, "trade_in_id": trade_in_id, "settlement_method": "rolled_into_financing",
                "purchase_order_id": purchase_order_id, "amount": amount, "posted_on": ctx.now()[:10],
                "equity_balance": balance})


@tool(owner="user", rw="write")
def pay_trade_shortfall_d2aa4d28(ctx: ToolContext, trade_in_id: str, payment_amount: float) -> str:
    """Pay, as the vehicle owner, money of your own toward the shortfall standing between your old loan's payoff
    and your trade-in's value.

    The customer uses this to make one payment from their own funds by bank transfer onto their trade-in
    agreement. One call books a covering entry of the kind customer_payment, dated today, for the amount given
    and raises the agreement's undistributed trade equity by that amount; the payment shows in the
    agreement's history and the open shortfall drops by the amount paid.

    Args:
        trade_in_id: Id class — the reference number of your trade-in agreement, as read out to you by the
            Kestrel representative.
        payment_amount: Fixed-format class — the amount you pay, in USD, a positive amount given to 2 decimal
            places exactly as the representative quoted it.

    Returns:
        A text rendering of a dictionary receipt. Fields: 'payment_id' (string, reference number of your
        payment), 'trade_in_id' (string, the agreement paid on), 'settlement_method' (string, always
        customer_payment), 'amount' (number, USD with 2 decimal places, the amount received), 'paid_on'
        (string, YYYY-MM-DD) and 'equity_balance' (number, USD with 2 decimal places, the agreement's
        undistributed trade equity with the payment booked). A receipt carrying a payment_id means the
        payment is recorded.
    """
    amount = round(float(payment_amount), 2)
    entry_id = ctx.make_id("tdx_", trade_in_id, "payoff_shortfall_payment", amount)
    rows = ctx.find("tradein_agreements", trade_in_id=trade_in_id)
    customer_id = rows[0].get("customer_id") if rows else ""
    ctx.create("tradein_transactions", entry_id, tradein_txn_id=entry_id, trade_in_id=trade_in_id,
               customer_id=customer_id, event_type="tradein_negative_equity_settled", txn_date=ctx.now()[:10],
               amount=amount, adjustment_type="not_applicable", payoff_good_through_date=None,
               per_diem_amount=0.0, quote_reference="", settlement_method="customer_payment",
               document_type="not_applicable", source_txn_id=None, linked_reference_id=None)
    balance = round(float(rows[0].get("equity_balance") or 0) + amount, 2) if rows else amount
    if rows:
        ctx.update("tradein_agreements", trade_in_id, equity_balance=balance)
    return str({"payment_id": entry_id, "trade_in_id": trade_in_id, "settlement_method": "customer_payment",
                "amount": amount, "paid_on": ctx.now()[:10], "equity_balance": balance})


@tool(owner="agent", rw="write")
def send_lien_payoff_9460d1ba(ctx: ToolContext, trade_in_id: str, source_txn_id: str, payoff_amount: float) -> str:
    """Send the lien payoff for one picked-up trade-in vehicle to its lienholder and charge it against the
    customer's trade equity.

    A Kestrel representative uses this to release the payoff of the loan or lease on the traded vehicle, relying
    on one recorded payoff quote. One call books a lien payoff entry dated today that names the quote relied on,
    for the amount given, and lowers the agreement's undistributed trade equity by that same amount; the entry
    shows in the agreement's history as the payoff sent on the customer's old loan.

    Args:
        trade_in_id: Id class — the reference number of the customer's trade-in agreement, as shown by the
            trade-in agreement lookup for this customer.
        source_txn_id: Id class — the reference number of the payoff quote entry relied on, as shown in the
            agreement's history by the trade-in history lookup.
        payoff_amount: Fixed-format class — the payoff amount charged against the trade equity, in USD, a
            positive amount given to 2 decimal places (rounded to the nearest cent).

    Returns:
        A text rendering of a dictionary receipt. Fields: 'entry_id' (string, reference number of the payoff
        entry), 'trade_in_id' (string, the agreement), 'source_txn_id' (string, the quote entry relied on),
        'amount' (number, USD with 2 decimal places, the payoff amount booked), 'sent_on' (string, YYYY-MM-DD)
        and 'equity_balance' (number, USD with 2 decimal places, the undistributed trade equity with the payoff
        booked). A receipt carrying an entry_id means the payoff is sent and booked.
    """
    amount = round(float(payoff_amount), 2)
    entry_id = ctx.make_id("tdx_", trade_in_id, source_txn_id, "lien_payoff", amount)
    rows = ctx.find("tradein_agreements", trade_in_id=trade_in_id)
    customer_id = rows[0].get("customer_id") if rows else ""
    ctx.create("tradein_transactions", entry_id, tradein_txn_id=entry_id, trade_in_id=trade_in_id,
               customer_id=customer_id, event_type="tradein_lien_payoff_sent", txn_date=ctx.now()[:10],
               amount=amount, adjustment_type="not_applicable", payoff_good_through_date=None,
               per_diem_amount=0.0, quote_reference="", settlement_method="not_applicable",
               document_type="not_applicable", source_txn_id=source_txn_id, linked_reference_id=None)
    balance = round(float(rows[0].get("equity_balance") or 0) - amount, 2) if rows else -amount
    if rows:
        ctx.update("tradein_agreements", trade_in_id, equity_balance=balance)
    return str({"entry_id": entry_id, "trade_in_id": trade_in_id, "source_txn_id": source_txn_id,
                "amount": amount, "sent_on": ctx.now()[:10], "equity_balance": balance})


@tool(owner="agent", rw="write")
def post_towing_fee_7cb58a13(ctx: ToolContext, trade_in_id: str, towing_fee: float) -> str:
    """Post the towing fee deduction for one trade-in vehicle that Kestrel collected by tow truck.

    A Kestrel representative uses this to book, on the customer's trade-in agreement, the deduction for towing
    the vehicle in. One call books one deduction entry of the reason towing_fee, dated today, for the amount
    given and lowers the agreement's undistributed trade equity by that same amount; the entry shows in the
    agreement's history and the lower equity shows on the agreement.

    Args:
        trade_in_id: Id class — the reference number of the customer's trade-in agreement, as shown by the
            trade-in agreement lookup for this customer.
        towing_fee: Fixed-format class — the towing deduction to book, in USD, a positive amount given to 2
            decimal places (rounded to the nearest cent).

    Returns:
        A text rendering of a dictionary receipt. Fields: 'entry_id' (string, reference number of the new
        deduction entry), 'trade_in_id' (string, the agreement), 'adjustment_type' (string, always towing_fee),
        'amount' (number, USD with 2 decimal places, the deduction booked), 'posted_on' (string, YYYY-MM-DD) and
        'equity_balance' (number, USD with 2 decimal places, the undistributed trade equity with the deduction
        booked). A receipt carrying an entry_id means the towing deduction is booked.
    """
    amount = round(float(towing_fee), 2)
    entry_id = ctx.make_id("tdx_", trade_in_id, "towing_fee", amount)
    rows = ctx.find("tradein_agreements", trade_in_id=trade_in_id)
    customer_id = rows[0].get("customer_id") if rows else ""
    ctx.create("tradein_transactions", entry_id, tradein_txn_id=entry_id, trade_in_id=trade_in_id,
               customer_id=customer_id, event_type="tradein_value_deducted", txn_date=ctx.now()[:10],
               amount=amount, adjustment_type="towing_fee", payoff_good_through_date=None,
               per_diem_amount=0.0, quote_reference="", settlement_method="not_applicable",
               document_type="not_applicable", source_txn_id=None, linked_reference_id=None)
    balance = round(float(rows[0].get("equity_balance") or 0) - amount, 2) if rows else -amount
    if rows:
        ctx.update("tradein_agreements", trade_in_id, equity_balance=balance)
    return str({"entry_id": entry_id, "trade_in_id": trade_in_id, "adjustment_type": "towing_fee",
                "amount": amount, "posted_on": ctx.now()[:10], "equity_balance": balance})


@tool(owner="agent", rw="write")
def post_title_delay_chargeback_a143df45(ctx: ToolContext, trade_in_id: str, chargeback_amount: float) -> str:
    """Post a title-delay chargeback against the trade value of one picked-up trade-in vehicle whose
    transferable title has not been received.

    A Kestrel representative uses this to book the chargeback on the customer's trade-in agreement. One call
    books one deduction entry of the reason title_delay_chargeback, dated today, for the amount given and lowers
    the agreement's undistributed trade equity by that same amount; the entry shows in the agreement's
    history, and a balance below zero is a shortfall the customer owes.

    Args:
        trade_in_id: Id class — the reference number of the customer's trade-in agreement, as shown by the
            trade-in agreement lookup for this customer.
        chargeback_amount: Fixed-format class — the chargeback to book, in USD, a positive amount given to 2
            decimal places (rounded to the nearest cent).

    Returns:
        A text rendering of a dictionary receipt. Fields: 'entry_id' (string, reference number of the new
        chargeback entry), 'trade_in_id' (string, the agreement), 'adjustment_type' (string, always
        title_delay_chargeback), 'amount' (number, USD with 2 decimal places, the chargeback booked), 'posted_on'
        (string, YYYY-MM-DD) and 'equity_balance' (number, USD with 2 decimal places, the undistributed trade
        equity with the chargeback booked; negative means the customer owes a shortfall). A receipt carrying
        an entry_id means the chargeback is booked.
    """
    amount = round(float(chargeback_amount), 2)
    entry_id = ctx.make_id("tdx_", trade_in_id, "title_delay_chargeback", amount)
    rows = ctx.find("tradein_agreements", trade_in_id=trade_in_id)
    customer_id = rows[0].get("customer_id") if rows else ""
    ctx.create("tradein_transactions", entry_id, tradein_txn_id=entry_id, trade_in_id=trade_in_id,
               customer_id=customer_id, event_type="tradein_value_deducted", txn_date=ctx.now()[:10],
               amount=amount, adjustment_type="title_delay_chargeback", payoff_good_through_date=None,
               per_diem_amount=0.0, quote_reference="", settlement_method="not_applicable",
               document_type="not_applicable", source_txn_id=None, linked_reference_id=None)
    balance = round(float(rows[0].get("equity_balance") or 0) - amount, 2) if rows else -amount
    if rows:
        ctx.update("tradein_agreements", trade_in_id, equity_balance=balance)
    return str({"entry_id": entry_id, "trade_in_id": trade_in_id, "adjustment_type": "title_delay_chargeback",
                "amount": amount, "posted_on": ctx.now()[:10], "equity_balance": balance})


@tool(owner="user", rw="write")
def pay_chargeback_shortfall_4672c84f(ctx: ToolContext, trade_in_id: str, payment_amount: float) -> str:
    """Pay, as the former owner of a traded vehicle, money of your own toward the shortfall a title-delay
    chargeback left on your trade-in agreement.

    The customer uses this to make one payment from their own funds by bank transfer onto their trade-in
    agreement. One call books a covering entry of the kind customer_payment, dated today, for the amount given
    and raises the agreement's undistributed trade equity by that amount; the payment shows in the
    agreement's history and the amount still owed drops by the amount paid.

    Args:
        trade_in_id: Id class — the reference number of your trade-in agreement, as read out to you by the
            Kestrel representative.
        payment_amount: Fixed-format class — the amount you pay, in USD, a positive amount given to 2 decimal
            places exactly as the representative quoted it.

    Returns:
        A text rendering of a dictionary receipt. Fields: 'payment_id' (string, reference number of your
        payment), 'trade_in_id' (string, the agreement paid on), 'settlement_method' (string, always
        customer_payment), 'amount' (number, USD with 2 decimal places, the amount received), 'paid_on'
        (string, YYYY-MM-DD) and 'equity_balance' (number, USD with 2 decimal places, the agreement's
        undistributed trade equity with the payment booked). A receipt carrying a payment_id means the
        payment is recorded.
    """
    amount = round(float(payment_amount), 2)
    entry_id = ctx.make_id("tdx_", trade_in_id, "chargeback_shortfall_payment", amount)
    rows = ctx.find("tradein_agreements", trade_in_id=trade_in_id)
    customer_id = rows[0].get("customer_id") if rows else ""
    ctx.create("tradein_transactions", entry_id, tradein_txn_id=entry_id, trade_in_id=trade_in_id,
               customer_id=customer_id, event_type="tradein_negative_equity_settled", txn_date=ctx.now()[:10],
               amount=amount, adjustment_type="not_applicable", payoff_good_through_date=None,
               per_diem_amount=0.0, quote_reference="", settlement_method="customer_payment",
               document_type="not_applicable", source_txn_id=None, linked_reference_id=None)
    balance = round(float(rows[0].get("equity_balance") or 0) + amount, 2) if rows else amount
    if rows:
        ctx.update("tradein_agreements", trade_in_id, equity_balance=balance)
    return str({"payment_id": entry_id, "trade_in_id": trade_in_id, "settlement_method": "customer_payment",
                "amount": amount, "paid_on": ctx.now()[:10], "equity_balance": balance})

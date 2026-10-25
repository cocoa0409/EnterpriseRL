"""Hidden task tools for the window_contract_deposits_and_cancellations difficulty
(Ridgeline Window & Door, window replacement contracts).

Each tool lands exactly one entry on a window replacement contract's money record and
judges nothing: the amounts and dates are worked out by the agent from the published
policies and passed in as fixed-format values.
"""

from erlbench import ToolContext, tool


@tool(owner="user", rw="write")
def pay_final_balance_39e93918(ctx: ToolContext, window_contract_id: str, amount: float,
                               tender_type: str) -> str:
    """The customer pays money toward the remaining balance of their own window replacement
    contract once the windows are installed. One call records one final-balance payment of the
    stated amount on that contract, dated today, which raises the money the customer has paid
    toward the contract by that amount; the payment then shows on the contract's payment
    history as a final-balance payment made with the stated tender. The receipt confirms the
    payment reference, the contract, the amount, the tender and the date.

    Args:
        window_contract_id: Id class — the reference number of the customer's window
            replacement contract being paid, as returned by the window contract lookup for
            this customer.
        amount: Fixed-format class — the amount the customer pays now, in USD, a positive
            number with 2 decimal places, rounded to the cent.
        tender_type: Enum class — how the customer pays, exactly one of: card — the customer
            pays with a debit or credit card; ach — the customer pays by bank transfer from a
            checking or savings account; check — the customer pays with a paper check;
            lender_disbursement — reserved for money a financing lender sends on the
            customer's behalf, never the customer's own payment; not_applicable — reserved
            for entries that are not payments, never used for a payment.

    Returns:
        A text receipt of a dictionary with these fields: payment_reference (the new payment
        entry's reference number), window_contract_id (the contract paid), amount (USD with
        2 decimal places), tender_type (the tender recorded), payment_date (today's date as
        YYYY-MM-DD) and status ("recorded" when the payment is on the contract).
    """
    contract_rows = ctx.find("window_contracts", window_contract_id=window_contract_id)
    owner = contract_rows[0].get("customer_id", "") if contract_rows else ""
    rid = ctx.make_id("wtx_", window_contract_id, amount, tender_type, "final_balance")
    paid_on = ctx.now()[:10]
    ctx.create("window_transactions", rid, window_txn_id=rid, window_contract_id=window_contract_id,
               customer_id=owner,
               event_type="window_payment_received", txn_date=paid_on, amount=round(float(amount), 2),
               payment_kind="final_balance", tender_type=tender_type, refund_kind="not_applicable",
               source_window_txn_id=None, change_kind="not_applicable", credit_kind="not_applicable",
               fee_kind="not_applicable", openings_affected=0, visit_kind="not_applicable",
               visit_outcome="not_applicable", oversize_opening_count=0, factory_order_id=None,
               referred_contract_number="")
    return str({"payment_reference": rid, "window_contract_id": window_contract_id,
                "amount": round(float(amount), 2), "tender_type": tender_type,
                "payment_date": paid_on, "status": "recorded"})


@tool(owner="agent", rw="write")
def post_late_balance_charge_0f8afea0(ctx: ToolContext, window_contract_id: str, amount: float) -> str:
    """Book a late balance charge on an installed window replacement contract whose remaining
    balance is overdue. One call adds one late balance charge entry of the stated amount to the
    contract's fees, dated today, which raises what the customer owes on the contract by that
    amount; the charge then shows on the contract's history as a fee of kind
    late_balance_charge. The receipt confirms the charge reference, the contract, the amount
    and the date booked.

    Args:
        window_contract_id: Id class — the reference number of the window replacement contract
            the charge is booked on, as returned by the window contract lookup for this
            customer.
        amount: Fixed-format class — the late balance charge, in USD, a positive number with 2
            decimal places, rounded to the cent.

    Returns:
        A text receipt of a dictionary with these fields: charge_reference (the new fee entry's
        reference number), window_contract_id (the contract charged), fee_kind
        ("late_balance_charge"), amount (USD with 2 decimal places), charge_date (today's date
        as YYYY-MM-DD) and status ("booked" when the charge is on the contract).
    """
    contract_rows = ctx.find("window_contracts", window_contract_id=window_contract_id)
    owner = contract_rows[0].get("customer_id", "") if contract_rows else ""
    rid = ctx.make_id("wtx_", window_contract_id, amount, "late_balance_charge")
    booked_on = ctx.now()[:10]
    ctx.create("window_transactions", rid, window_txn_id=rid, window_contract_id=window_contract_id,
               customer_id=owner,
               event_type="window_fee_assessed", txn_date=booked_on, amount=round(float(amount), 2),
               payment_kind="not_applicable", tender_type="not_applicable", refund_kind="not_applicable",
               source_window_txn_id=None, change_kind="not_applicable", credit_kind="not_applicable",
               fee_kind="late_balance_charge", openings_affected=0, visit_kind="not_applicable",
               visit_outcome="not_applicable", oversize_opening_count=0, factory_order_id=None,
               referred_contract_number="")
    return str({"charge_reference": rid, "window_contract_id": window_contract_id,
                "fee_kind": "late_balance_charge", "amount": round(float(amount), 2),
                "charge_date": booked_on, "status": "booked"})


@tool(owner="agent", rw="write")
def post_change_order_fee_bcbd2cec(ctx: ToolContext, window_contract_id: str, amount: float,
                                   change_order_date: str) -> str:
    """Book the change-order fee for one customer change order on a window replacement
    contract. One call adds one fee entry of kind change_order_fee for the stated amount to the
    contract, dated the day that change order was written, which raises what the customer owes
    on the contract by that amount; the fee then shows on the contract's history under that
    date. The receipt confirms the fee reference, the contract, the amount and the fee date.

    Args:
        window_contract_id: Id class — the reference number of the window replacement contract
            the fee is booked on, as returned by the window contract lookup for this customer.
        amount: Fixed-format class — the change-order fee, in USD, a positive number with 2
            decimal places, rounded to the cent.
        change_order_date: Fixed-format class — the date the charged change order was written,
            as YYYY-MM-DD, copied from the change-order lines on the contract's history.

    Returns:
        A text receipt of a dictionary with these fields: fee_reference (the new fee entry's
        reference number), window_contract_id (the contract charged), fee_kind
        ("change_order_fee"), amount (USD with 2 decimal places), fee_date (the change order
        date as YYYY-MM-DD) and status ("booked" when the fee is on the contract).
    """
    contract_rows = ctx.find("window_contracts", window_contract_id=window_contract_id)
    owner = contract_rows[0].get("customer_id", "") if contract_rows else ""
    rid = ctx.make_id("wtx_", window_contract_id, amount, change_order_date, "change_order_fee")
    ctx.create("window_transactions", rid, window_txn_id=rid, window_contract_id=window_contract_id,
               customer_id=owner,
               event_type="window_fee_assessed", txn_date=change_order_date, amount=round(float(amount), 2),
               payment_kind="not_applicable", tender_type="not_applicable", refund_kind="not_applicable",
               source_window_txn_id=None, change_kind="not_applicable", credit_kind="not_applicable",
               fee_kind="change_order_fee", openings_affected=0, visit_kind="not_applicable",
               visit_outcome="not_applicable", oversize_opening_count=0, factory_order_id=None,
               referred_contract_number="")
    return str({"fee_reference": rid, "window_contract_id": window_contract_id,
                "fee_kind": "change_order_fee", "amount": round(float(amount), 2),
                "fee_date": change_order_date, "status": "booked"})


@tool(owner="agent", rw="write")
def post_remeasure_fee_bdabfe19(ctx: ToolContext, window_contract_id: str, amount: float,
                                remeasure_date: str) -> str:
    """Book the remeasure fee for one customer-requested remeasure visit on a window
    replacement contract. One call adds one fee entry of kind remeasure_fee for the stated
    amount to the contract, dated the day of that remeasure visit, which raises what the
    customer owes on the contract by that amount; the fee then shows on the contract's history
    under that date. The receipt confirms the fee reference, the contract, the amount and the
    fee date.

    Args:
        window_contract_id: Id class — the reference number of the window replacement contract
            the fee is booked on, as returned by the window contract lookup for this customer.
        amount: Fixed-format class — the remeasure fee, in USD, a positive number with 2
            decimal places, rounded to the cent.
        remeasure_date: Fixed-format class — the date of the charged remeasure visit, as
            YYYY-MM-DD, copied from that visit on the contract's history.

    Returns:
        A text receipt of a dictionary with these fields: fee_reference (the new fee entry's
        reference number), window_contract_id (the contract charged), fee_kind
        ("remeasure_fee"), amount (USD with 2 decimal places), fee_date (the remeasure date as
        YYYY-MM-DD) and status ("booked" when the fee is on the contract).
    """
    contract_rows = ctx.find("window_contracts", window_contract_id=window_contract_id)
    owner = contract_rows[0].get("customer_id", "") if contract_rows else ""
    rid = ctx.make_id("wtx_", window_contract_id, amount, remeasure_date, "remeasure_fee")
    ctx.create("window_transactions", rid, window_txn_id=rid, window_contract_id=window_contract_id,
               customer_id=owner,
               event_type="window_fee_assessed", txn_date=remeasure_date, amount=round(float(amount), 2),
               payment_kind="not_applicable", tender_type="not_applicable", refund_kind="not_applicable",
               source_window_txn_id=None, change_kind="not_applicable", credit_kind="not_applicable",
               fee_kind="remeasure_fee", openings_affected=0, visit_kind="not_applicable",
               visit_outcome="not_applicable", oversize_opening_count=0, factory_order_id=None,
               referred_contract_number="")
    return str({"fee_reference": rid, "window_contract_id": window_contract_id,
                "fee_kind": "remeasure_fee", "amount": round(float(amount), 2),
                "fee_date": remeasure_date, "status": "booked"})


@tool(owner="user", rw="write")
def pay_deposit_balance_19bfa79b(ctx: ToolContext, window_contract_id: str, amount: float,
                                 tender_type: str) -> str:
    """The customer pays money toward the booking deposit of their own window replacement
    contract that has not yet been released to the factory. One call records one booking-deposit
    payment of the stated amount on that contract, dated today, which raises the money the
    customer has paid toward the contract by that amount; the payment then shows on the
    contract's payment history as a booking deposit made with the stated tender. The receipt
    confirms the payment reference, the contract, the amount, the tender and the date.

    Args:
        window_contract_id: Id class — the reference number of the customer's window
            replacement contract the deposit is paid on, as returned by the window contract
            lookup for this customer.
        amount: Fixed-format class — the amount the customer pays now, in USD, a positive
            number with 2 decimal places, rounded to the cent.
        tender_type: Enum class — how the customer pays, exactly one of: card — the customer
            pays with a debit or credit card; ach — the customer pays by bank transfer from a
            checking or savings account; check — the customer pays with a paper check;
            lender_disbursement — reserved for money a financing lender sends on the
            customer's behalf, never the customer's own payment; not_applicable — reserved
            for entries that are not payments, never used for a payment.

    Returns:
        A text receipt of a dictionary with these fields: payment_reference (the new payment
        entry's reference number), window_contract_id (the contract paid), amount (USD with
        2 decimal places), tender_type (the tender recorded), payment_date (today's date as
        YYYY-MM-DD) and status ("recorded" when the payment is on the contract).
    """
    contract_rows = ctx.find("window_contracts", window_contract_id=window_contract_id)
    owner = contract_rows[0].get("customer_id", "") if contract_rows else ""
    rid = ctx.make_id("wtx_", window_contract_id, amount, tender_type, "booking_deposit")
    paid_on = ctx.now()[:10]
    ctx.create("window_transactions", rid, window_txn_id=rid, window_contract_id=window_contract_id,
               customer_id=owner,
               event_type="window_payment_received", txn_date=paid_on, amount=round(float(amount), 2),
               payment_kind="booking_deposit", tender_type=tender_type, refund_kind="not_applicable",
               source_window_txn_id=None, change_kind="not_applicable", credit_kind="not_applicable",
               fee_kind="not_applicable", openings_affected=0, visit_kind="not_applicable",
               visit_outcome="not_applicable", oversize_opening_count=0, factory_order_id=None,
               referred_contract_number="")
    return str({"payment_reference": rid, "window_contract_id": window_contract_id,
                "amount": round(float(amount), 2), "tender_type": tender_type,
                "payment_date": paid_on, "status": "recorded"})


@tool(owner="agent", rw="write")
def post_door_bundle_credit_ed16c33c(ctx: ToolContext, window_contract_id: str, door_contract_id: str,
                                     amount: float) -> str:
    """Grant the door bundle discount on a window replacement contract whose household also
    signed a Ridgeline door contract. One call adds one price credit entry of kind
    door_bundle_discount for the stated amount to the window contract, dated today, which lowers
    what the customer owes on that contract by that amount; the credit then shows on the
    contract's history. The door contract the credit is granted for is part of the credit's
    reference, so credits for different door contracts granted on the same day stay separate
    entries. The receipt confirms the credit reference, the window contract, the door contract,
    the amount and the date granted.

    Args:
        window_contract_id: Id class — the reference number of the window replacement contract
            the credit is granted on, as returned by the window contract lookup for this
            customer.
        door_contract_id: Id class — the reference number of the household's door contract this
            credit is granted for, as returned by the door contract lookup for this customer.
        amount: Fixed-format class — the door bundle discount credit, in USD, a positive number
            with 2 decimal places, rounded to the cent.

    Returns:
        A text receipt of a dictionary with these fields: credit_reference (the new credit
        entry's reference number), window_contract_id (the contract credited), door_contract_id
        (the door contract the credit is granted for), credit_kind ("door_bundle_discount"), amount (USD with 2 decimal places), credit_date (today's date
        as YYYY-MM-DD) and status ("granted" when the credit is on the contract).
    """
    contract_rows = ctx.find("window_contracts", window_contract_id=window_contract_id)
    owner = contract_rows[0].get("customer_id", "") if contract_rows else ""
    rid = ctx.make_id("wtx_", window_contract_id, door_contract_id, amount, "door_bundle_discount")
    granted_on = ctx.now()[:10]
    ctx.create("window_transactions", rid, window_txn_id=rid, window_contract_id=window_contract_id,
               customer_id=owner,
               event_type="window_price_credit", txn_date=granted_on, amount=round(float(amount), 2),
               payment_kind="not_applicable", tender_type="not_applicable", refund_kind="not_applicable",
               source_window_txn_id=None, change_kind="not_applicable", credit_kind="door_bundle_discount",
               fee_kind="not_applicable", openings_affected=0, visit_kind="not_applicable",
               visit_outcome="not_applicable", oversize_opening_count=0, factory_order_id=None,
               referred_contract_number="")
    return str({"credit_reference": rid, "window_contract_id": window_contract_id,
                "door_contract_id": door_contract_id, "credit_kind": "door_bundle_discount", "amount": round(float(amount), 2),
                "credit_date": granted_on, "status": "granted"})

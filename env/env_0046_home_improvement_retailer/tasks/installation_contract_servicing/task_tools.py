"""Hidden task tools of the installation_contract_servicing difficulty (Ridgeline Installation Services).

Each tool performs one atomic write on one installation contract with the value the agent has already
worked out from the published policy; no tool aggregates history, judges eligibility or refuses.
"""

from erlbench import ToolContext, tool


@tool(owner="agent", rw="write")
def post_reschedule_fee_05a0220d(ctx: ToolContext, install_contract_id: str, install_request_id: str,
                                 fee_amount: float) -> str:
    """Post a customer reschedule fee on one Ridgeline installation contract. One call adds one
    reschedule fee line to the contract's account, dated today and tied to the customer reschedule
    request it arises from, and raises the contract's balance due by the fee amount. The customer sees
    the reschedule fee on the contract's statement of charges and a higher balance due straight away.

    Args:
        install_contract_id: Id class — the reference number of the installation contract the fee is
            charged on, as returned by the installation contract lookup for this customer.
        install_request_id: Id class — the reference number of the customer reschedule request the fee
            arises from, as returned by the installation service request lookup for that contract.
        fee_amount: Fixed-format class — the reschedule fee charged, in USD, a positive amount written
            to 2 decimal places (cents); a value with more decimals is rounded half to even to the cent
            when it is recorded.

    Returns:
        A dictionary receipt: install_charge_id (string, the reference number of the new fee line),
        install_contract_id (string, the contract charged), contract_number (string, the contract number
        exactly as on the contract), fee_type (string, always reschedule_fee), amount (number in USD with 2
        decimal places, the fee posted), charge_date (string YYYY-MM-DD, today's posting date) and
        balance_due (number in USD with 2 decimal places, the contract's balance due after the fee).
        A receipt carrying an install_charge_id means the fee is on the contract.
    """
    contract = ctx.find("install_contracts", install_contract_id=install_contract_id)[0]
    amount = round(float(fee_amount), 2)
    today = ctx.now()[:10]
    rid = ctx.make_id("ich_", install_contract_id, install_request_id, fee_amount)
    ctx.create("install_charges", rid, install_charge_id=rid, install_contract_id=install_contract_id,
               customer_id=contract.get("customer_id"), event_type="install_fee_charged",
               contract_number=contract.get("contract_number"), charge_date=today, amount=amount,
               fee_type="reschedule_fee", change_order_number="", payment_method="not_applicable",
               payment_purpose="not_applicable", credit_type="not_applicable", refund_method="not_applicable",
               refund_reason="not_applicable", original_charge_id=None, install_request_id=install_request_id,
               visit_date="", visit_type="not_applicable", visit_outcome="not_applicable",
               warranty_status="not_applicable")
    balance = round(float(contract.get("balance_due") or 0) + amount, 2)
    ctx.update("install_contracts", install_contract_id, balance_due=balance)
    return str({"install_charge_id": rid, "install_contract_id": install_contract_id,
                "contract_number": contract.get("contract_number"), "fee_type": "reschedule_fee",
                "amount": amount, "charge_date": today, "balance_due": balance})


@tool(owner="user", rw="write")
def pay_final_balance_37ea441b(ctx: ToolContext, install_contract_id: str, payment_amount: float) -> str:
    """The customer authorizes a charge to their own bank card to settle the final payment on one of
    their completed Ridgeline installation contracts. One call records one payment toward that contract,
    dated today, with tender bank card and purpose final payment, and lowers the contract's balance due
    by the amount paid. The customer receives a payment confirmation and sees the lower balance due.

    Args:
        install_contract_id: Id class — the reference number of the installation contract being paid,
            as given to the customer by the agent from the installation contract lookup.
        payment_amount: Fixed-format class — the amount charged to the customer's bank card, in USD, a
            positive amount written to 2 decimal places (cents); a value with more decimals is rounded
            half to even to the cent when it is recorded.

    Returns:
        A dictionary receipt: install_charge_id (string, the reference number of the payment line),
        install_contract_id (string, the contract paid), contract_number (string, the contract number
        exactly as on the contract), payment_method (string, always bank_card), payment_purpose (string,
        always final_payment), amount (number in USD with 2 decimal places, the amount charged),
        charge_date (string YYYY-MM-DD, today's payment date) and balance_due (number in USD with 2
        decimal places, the contract's balance due after the payment). A receipt carrying an
        install_charge_id means the payment is recorded.
    """
    contract = ctx.find("install_contracts", install_contract_id=install_contract_id)[0]
    amount = round(float(payment_amount), 2)
    today = ctx.now()[:10]
    rid = ctx.make_id("ich_", install_contract_id, payment_amount, "final_payment")
    ctx.create("install_charges", rid, install_charge_id=rid, install_contract_id=install_contract_id,
               customer_id=contract.get("customer_id"), event_type="install_payment_received",
               contract_number=contract.get("contract_number"), charge_date=today, amount=amount,
               fee_type="not_applicable", change_order_number="", payment_method="bank_card",
               payment_purpose="final_payment", credit_type="not_applicable", refund_method="not_applicable",
               refund_reason="not_applicable", original_charge_id=None, install_request_id=None,
               visit_date="", visit_type="not_applicable", visit_outcome="not_applicable",
               warranty_status="not_applicable")
    balance = round(float(contract.get("balance_due") or 0) - amount, 2)
    ctx.update("install_contracts", install_contract_id, balance_due=balance)
    return str({"install_charge_id": rid, "install_contract_id": install_contract_id,
                "contract_number": contract.get("contract_number"), "payment_method": "bank_card",
                "payment_purpose": "final_payment", "amount": amount, "charge_date": today,
                "balance_due": balance})


@tool(owner="agent", rw="write")
def post_trip_charge_9239fb96(ctx: ToolContext, install_contract_id: str, visit_charge_id: str,
                              charge_amount: float) -> str:
    """Post a trip charge on one Ridgeline installation contract for a recorded installer visit that
    could not go ahead. One call adds one trip charge line to the contract's account, dated today and
    tied to the visit record it arises from, and raises the contract's balance due by the charge. The
    customer sees the trip charge on the contract's statement of charges and a higher balance due.

    Args:
        install_contract_id: Id class — the reference number of the installation contract the charge is
            posted on, as returned by the installation contract lookup for this customer.
        visit_charge_id: Id class — the reference number of the recorded visit line the charge arises
            from, as returned by the installation contract line lookup for that contract.
        charge_amount: Fixed-format class — the trip charge, in USD, a positive amount written to 2
            decimal places (cents); a value with more decimals is rounded half to even to the cent when
            it is recorded.

    Returns:
        A dictionary receipt: install_charge_id (string, the reference number of the new charge line),
        install_contract_id (string, the contract charged), contract_number (string, the contract number
        exactly as on the contract), fee_type (string, always trip_charge), original_charge_id (string, the
        visit line the charge refers to), amount (number in USD with 2 decimal places, the charge posted),
        charge_date (string YYYY-MM-DD, today's posting date) and balance_due (number in USD with 2 decimal
        places, the contract's balance due after the charge). A receipt carrying an install_charge_id
        means the charge is on the contract.
    """
    contract = ctx.find("install_contracts", install_contract_id=install_contract_id)[0]
    amount = round(float(charge_amount), 2)
    today = ctx.now()[:10]
    rid = ctx.make_id("ich_", install_contract_id, visit_charge_id, charge_amount)
    ctx.create("install_charges", rid, install_charge_id=rid, install_contract_id=install_contract_id,
               customer_id=contract.get("customer_id"), event_type="install_fee_charged",
               contract_number=contract.get("contract_number"), charge_date=today, amount=amount,
               fee_type="trip_charge", change_order_number="", payment_method="not_applicable",
               payment_purpose="not_applicable", credit_type="not_applicable", refund_method="not_applicable",
               refund_reason="not_applicable", original_charge_id=visit_charge_id, install_request_id=None,
               visit_date="", visit_type="not_applicable", visit_outcome="not_applicable",
               warranty_status="not_applicable")
    balance = round(float(contract.get("balance_due") or 0) + amount, 2)
    ctx.update("install_contracts", install_contract_id, balance_due=balance)
    return str({"install_charge_id": rid, "install_contract_id": install_contract_id,
                "contract_number": contract.get("contract_number"), "fee_type": "trip_charge",
                "original_charge_id": visit_charge_id, "amount": amount, "charge_date": today,
                "balance_due": balance})


@tool(owner="agent", rw="write")
def post_change_order_fee_b62b1022(ctx: ToolContext, install_contract_id: str, install_request_id: str,
                                   fee_amount: float) -> str:
    """Post a change order administration fee on one Ridgeline installation contract for a signed change
    order. One call adds one administration fee line to the contract's account, dated today and tied to
    the change order request it arises from, and raises the contract's balance due by the fee. The
    customer sees the administration fee on the contract's statement of charges and a higher balance due.

    Args:
        install_contract_id: Id class — the reference number of the installation contract the fee is
            charged on, as returned by the installation contract lookup for this customer.
        install_request_id: Id class — the reference number of the change order request the fee arises
            from, as returned by the installation service request lookup for that contract.
        fee_amount: Fixed-format class — the administration fee, in USD, a positive amount written to 2
            decimal places (cents); a value with more decimals is rounded half to even to the cent when it
            is recorded.

    Returns:
        A dictionary receipt: install_charge_id (string, the reference number of the new fee line),
        install_contract_id (string, the contract charged), contract_number (string, the contract number
        exactly as on the contract), fee_type (string, always change_order_admin_fee), amount (number in USD
        with 2 decimal places, the fee posted), charge_date (string YYYY-MM-DD, today's posting date) and
        balance_due (number in USD with 2 decimal places, the contract's balance due after the fee). A
        receipt carrying an install_charge_id means the fee is on the contract.
    """
    contract = ctx.find("install_contracts", install_contract_id=install_contract_id)[0]
    amount = round(float(fee_amount), 2)
    today = ctx.now()[:10]
    rid = ctx.make_id("ich_", install_contract_id, install_request_id, fee_amount, "change_order_admin_fee")
    ctx.create("install_charges", rid, install_charge_id=rid, install_contract_id=install_contract_id,
               customer_id=contract.get("customer_id"), event_type="install_fee_charged",
               contract_number=contract.get("contract_number"), charge_date=today, amount=amount,
               fee_type="change_order_admin_fee", change_order_number="", payment_method="not_applicable",
               payment_purpose="not_applicable", credit_type="not_applicable", refund_method="not_applicable",
               refund_reason="not_applicable", original_charge_id=None, install_request_id=install_request_id,
               visit_date="", visit_type="not_applicable", visit_outcome="not_applicable",
               warranty_status="not_applicable")
    balance = round(float(contract.get("balance_due") or 0) + amount, 2)
    ctx.update("install_contracts", install_contract_id, balance_due=balance)
    return str({"install_charge_id": rid, "install_contract_id": install_contract_id,
                "contract_number": contract.get("contract_number"), "fee_type": "change_order_admin_fee",
                "amount": amount, "charge_date": today, "balance_due": balance})


@tool(owner="agent", rw="write")
def post_permit_handling_fee_ee01a5f4(ctx: ToolContext, install_contract_id: str, fee_amount: float) -> str:
    """Post the permit handling fee on one Ridgeline installation contract whose permit has been issued.
    One call adds one permit handling fee line to the contract's account, dated today, and raises the
    contract's balance due by the fee. The customer sees the permit handling fee on the contract's
    statement of charges and a higher balance due.

    Args:
        install_contract_id: Id class — the reference number of the installation contract the fee is
            charged on, as returned by the installation contract lookup for this customer.
        fee_amount: Fixed-format class — the permit handling fee, in USD, a positive amount written to 2
            decimal places (cents); a value with more decimals is rounded half to even to the cent when it
            is recorded.

    Returns:
        A dictionary receipt: install_charge_id (string, the reference number of the new fee line),
        install_contract_id (string, the contract charged), contract_number (string, the contract number
        exactly as on the contract), fee_type (string, always permit_handling_fee), amount (number in USD
        with 2 decimal places, the fee posted), charge_date (string YYYY-MM-DD, today's posting date) and
        balance_due (number in USD with 2 decimal places, the contract's balance due after the fee). A
        receipt carrying an install_charge_id means the fee is on the contract.
    """
    contract = ctx.find("install_contracts", install_contract_id=install_contract_id)[0]
    amount = round(float(fee_amount), 2)
    today = ctx.now()[:10]
    rid = ctx.make_id("ich_", install_contract_id, fee_amount, "permit_handling_fee")
    ctx.create("install_charges", rid, install_charge_id=rid, install_contract_id=install_contract_id,
               customer_id=contract.get("customer_id"), event_type="install_fee_charged",
               contract_number=contract.get("contract_number"), charge_date=today, amount=amount,
               fee_type="permit_handling_fee", change_order_number="", payment_method="not_applicable",
               payment_purpose="not_applicable", credit_type="not_applicable", refund_method="not_applicable",
               refund_reason="not_applicable", original_charge_id=None, install_request_id=None,
               visit_date="", visit_type="not_applicable", visit_outcome="not_applicable",
               warranty_status="not_applicable")
    balance = round(float(contract.get("balance_due") or 0) + amount, 2)
    ctx.update("install_contracts", install_contract_id, balance_due=balance)
    return str({"install_charge_id": rid, "install_contract_id": install_contract_id,
                "contract_number": contract.get("contract_number"), "fee_type": "permit_handling_fee",
                "amount": amount, "charge_date": today, "balance_due": balance})


@tool(owner="user", rw="write")
def pay_progress_payment_cb1125dd(ctx: ToolContext, install_contract_id: str, payment_amount: float) -> str:
    """The customer authorizes a charge to their own bank card for the payment due when work starts on
    one of their Ridgeline installation contracts. One call records one payment toward that contract,
    dated today, with tender bank card and purpose progress payment, and lowers the contract's balance
    due by the amount paid. The customer receives a payment confirmation and sees the lower balance due.

    Args:
        install_contract_id: Id class — the reference number of the installation contract being paid,
            as given to the customer by the agent from the installation contract lookup.
        payment_amount: Fixed-format class — the amount charged to the customer's bank card, in USD, a
            positive amount written to 2 decimal places (cents); a value with more decimals is rounded
            half to even to the cent when it is recorded.

    Returns:
        A dictionary receipt: install_charge_id (string, the reference number of the payment line),
        install_contract_id (string, the contract paid), contract_number (string, the contract number
        exactly as on the contract), payment_method (string, always bank_card), payment_purpose (string,
        always progress_payment), amount (number in USD with 2 decimal places, the amount charged),
        charge_date (string YYYY-MM-DD, today's payment date) and balance_due (number in USD with 2
        decimal places, the contract's balance due after the payment). A receipt carrying an
        install_charge_id means the payment is recorded.
    """
    contract = ctx.find("install_contracts", install_contract_id=install_contract_id)[0]
    amount = round(float(payment_amount), 2)
    today = ctx.now()[:10]
    rid = ctx.make_id("ich_", install_contract_id, payment_amount, "progress_payment")
    ctx.create("install_charges", rid, install_charge_id=rid, install_contract_id=install_contract_id,
               customer_id=contract.get("customer_id"), event_type="install_payment_received",
               contract_number=contract.get("contract_number"), charge_date=today, amount=amount,
               fee_type="not_applicable", change_order_number="", payment_method="bank_card",
               payment_purpose="progress_payment", credit_type="not_applicable", refund_method="not_applicable",
               refund_reason="not_applicable", original_charge_id=None, install_request_id=None,
               visit_date="", visit_type="not_applicable", visit_outcome="not_applicable",
               warranty_status="not_applicable")
    balance = round(float(contract.get("balance_due") or 0) - amount, 2)
    ctx.update("install_contracts", install_contract_id, balance_due=balance)
    return str({"install_charge_id": rid, "install_contract_id": install_contract_id,
                "contract_number": contract.get("contract_number"), "payment_method": "bank_card",
                "payment_purpose": "progress_payment", "amount": amount, "charge_date": today,
                "balance_due": balance})

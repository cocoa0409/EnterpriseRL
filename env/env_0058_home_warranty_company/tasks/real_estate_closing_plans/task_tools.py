"""Hidden task tools for the real_estate_closing_plans difficulty (Bridgewell Real Estate Service Contracts).

Each tool lands exactly one atomic billing write on a real estate service contract. The value it books is
worked out by whoever calls it from the published rules and the contract's own records; the tool itself checks
no eligibility, order or status and never refuses because some other item is still open.
"""

from erlbench import ToolContext, tool


@tool(owner="agent", rw="write")
def bill_failed_sale_charge_3e9b31c4(ctx: ToolContext, realty_contract_id: str, amount: float, due_date: str) -> dict:
    """Bill the seller of a real estate plan for listing-period service on an order whose sale did not go through.
    One call posts one failed-sale charge invoice to the plan's billing history in the name of the seller who held
    the listing order, dated today, for the amount and due date given, and raises the plan's invoice balance by that
    amount. A new failed-sale invoice number is issued for the charge and returned in the receipt. The charge then
    shows in the plan's billing history as an open failed-sale charge.

    Args:
        realty_contract_id: Id class — the real estate contract (plan) number of the listing order being billed, as
            shown by the real estate contract lookup for the seller.
        amount: Fixed-format class — the failed-sale charge to bill, in USD, a positive amount with 2 decimal places
            (cents), already rounded to the cent; it is booked exactly as given.
        due_date: Fixed-format class — the date by which the seller must pay the charge, written as YYYY-MM-DD
            (calendar date, no time of day).

    Returns:
        A dictionary confirming the posted charge: status is "billed" when the charge was posted; invoice_number is
        the new failed-sale invoice number (text); realty_contract_id is the plan number billed; amount is the charge
        booked in USD with 2 decimal places; entry_date is today's billing date as YYYY-MM-DD; due_date is the payment
        due date as YYYY-MM-DD; invoice_balance is the plan's invoice balance after the charge in USD with 2 decimal
        places.
    """
    amt = round(float(amount), 2)
    today = ctx.now()[:10]
    rows = ctx.find("realty_contracts", realty_contract_id=realty_contract_id)
    holder = rows[0].get("customer_id") if rows else ""
    balance = round(float((rows[0].get("invoice_balance") if rows else 0) or 0) + amt, 2)
    invoice_number = ctx.make_id("FS-", realty_contract_id, amt, due_date, length=10).upper()
    rid = ctx.make_id("rbe_", realty_contract_id, amt, due_date)
    ctx.create("realty_billing_entries", rid, realty_billing_entry_id=rid, realty_contract_id=realty_contract_id,
               customer_id=holder, event_type="realty_seller_service_charge", entry_date=today, amount=amt,
               invoice_number=invoice_number, due_date=due_date)
    if rows:
        ctx.update("realty_contracts", realty_contract_id, invoice_balance=balance)
    return {"status": "billed", "invoice_number": invoice_number, "realty_contract_id": realty_contract_id,
            "amount": amt, "entry_date": today, "due_date": due_date, "invoice_balance": balance}


@tool(owner="user", rw="write")
def pay_failed_sale_charge_by_card_a1a6aa51(ctx: ToolContext, realty_contract_id: str, invoice_number: str,
                                             amount: float) -> dict:
    """Pay, as the seller, toward a failed-sale charge billed on your real estate plan by card. One call records
    one payment from the seller, with payment method card, against the failed-sale invoice named, dated today, for
    the amount given, and lowers the plan's invoice balance by that amount. A payment confirmation
    number is issued and returned; the payment then shows in the plan's billing history against that invoice.

    Args:
        realty_contract_id: Id class — the real estate contract (plan) number the failed-sale charge was billed on,
            as given to you by the Bridgewell representative.
        invoice_number: Id class — the failed-sale invoice number being paid, as shown on the failed-sale charge in
            the plan's billing history and given to you by the Bridgewell representative.
        amount: Fixed-format class — the amount to pay now, in USD, a positive amount with 2 decimal places (cents);
            it is recorded exactly as given.

    Returns:
        A dictionary confirming the payment: status is "paid" when the payment was recorded; payment_reference is
        the payment confirmation number (text); invoice_number is the failed-sale invoice paid; amount is the amount
        charged in USD with 2 decimal places; payment_method is "card"; entry_date is today's posting date as
        YYYY-MM-DD; invoice_balance is the plan's invoice balance after the payment in USD with 2 decimal places.
    """
    amt = round(float(amount), 2)
    today = ctx.now()[:10]
    rows = ctx.find("realty_contracts", realty_contract_id=realty_contract_id)
    payer = rows[0].get("customer_id") if rows else ""
    balance = round(float((rows[0].get("invoice_balance") if rows else 0) or 0) - amt, 2)
    reference = ctx.make_id("PAY-", realty_contract_id, invoice_number, amt, length=10).upper()
    rid = ctx.make_id("rbe_", realty_contract_id, invoice_number, amt)
    ctx.create("realty_billing_entries", rid, realty_billing_entry_id=rid, realty_contract_id=realty_contract_id,
               customer_id=payer, event_type="realty_payment", entry_date=today, amount=amt,
               payment_reference=reference, invoice_number=invoice_number, payer_role="seller",
               payment_method="card")
    if rows:
        ctx.update("realty_contracts", realty_contract_id, invoice_balance=balance)
    return {"status": "paid", "payment_reference": reference, "invoice_number": invoice_number, "amount": amt,
            "payment_method": "card", "entry_date": today, "invoice_balance": balance}


@tool(owner="agent", rw="write")
def reissue_plan_invoice_480f4e9f(ctx: ToolContext, realty_contract_id: str, amount: float) -> dict:
    """Issue a new plan premium invoice on a real estate plan that has not yet closed, for the plan now on the order.
    One call posts one plan invoice to the plan's billing history, dated today, for the premium given, payable at the
    expected closing date shown on the order, and raises the plan's invoice balance by that amount. A new plan
    invoice number is issued and returned; the invoice then shows in the plan's billing history as the open plan
    invoice.

    Args:
        realty_contract_id: Id class — the real estate contract (plan) number of the order being invoiced, as shown by
            the real estate contract lookup for the buyer.
        amount: Fixed-format class — the plan premium to invoice, in USD, a positive amount with 2 decimal places
            (cents), already rounded to the cent; it is booked exactly as given.

    Returns:
        A dictionary confirming the invoice: status is "invoiced" when the invoice was posted; invoice_number is the
        new plan invoice number (text); realty_contract_id is the plan number invoiced; amount is the premium invoiced
        in USD with 2 decimal places; entry_date is today's invoice date as YYYY-MM-DD; due_date is the payment due
        date (the expected closing date on the order) as YYYY-MM-DD; invoice_balance is the plan's invoice balance
        after the invoice in USD with 2 decimal places.
    """
    amt = round(float(amount), 2)
    today = ctx.now()[:10]
    rows = ctx.find("realty_contracts", realty_contract_id=realty_contract_id)
    holder = rows[0].get("customer_id") if rows else ""
    due = (rows[0].get("expected_closing_date") if rows else "") or ""
    balance = round(float((rows[0].get("invoice_balance") if rows else 0) or 0) + amt, 2)
    invoice_number = ctx.make_id("PI-", realty_contract_id, amt, length=10).upper()
    rid = ctx.make_id("rbe_", realty_contract_id, "invoice", amt)
    ctx.create("realty_billing_entries", rid, realty_billing_entry_id=rid, realty_contract_id=realty_contract_id,
               customer_id=holder, event_type="realty_invoice", entry_date=today, amount=amt,
               invoice_number=invoice_number, due_date=due)
    if rows:
        ctx.update("realty_contracts", realty_contract_id, invoice_balance=balance)
    return {"status": "invoiced", "invoice_number": invoice_number, "realty_contract_id": realty_contract_id,
            "amount": amt, "entry_date": today, "due_date": due, "invoice_balance": balance}


@tool(owner="user", rw="write")
def prepay_plan_invoice_by_card_13fdf553(ctx: ToolContext, realty_contract_id: str, invoice_number: str,
                                          amount: float) -> dict:
    """Pay, as the buyer, toward the plan premium invoice of your real estate plan before closing, by card; any
    part of the invoice not paid this way stays open on it. One call records one payment from the buyer, with
    payment method card, against the plan invoice named, dated today, for the amount given, and lowers the plan's
    invoice balance by that amount. A payment confirmation number is issued and returned; the payment then shows in the plan's billing
    history against that invoice.

    Args:
        realty_contract_id: Id class — the real estate contract (plan) number of your order, as given to you by the
            Bridgewell representative.
        invoice_number: Id class — the plan invoice number being paid, as shown on the open plan invoice in the plan's
            billing history and given to you by the Bridgewell representative.
        amount: Fixed-format class — the amount to pay now, in USD, a positive amount with 2 decimal places (cents);
            it is recorded exactly as given.

    Returns:
        A dictionary confirming the payment: status is "paid" when the payment was recorded; payment_reference is
        the payment confirmation number (text); invoice_number is the plan invoice paid; amount is the amount charged
        in USD with 2 decimal places; payment_method is "card"; entry_date is today's posting date as YYYY-MM-DD;
        invoice_balance is the plan's invoice balance after the payment in USD with 2 decimal places.
    """
    amt = round(float(amount), 2)
    today = ctx.now()[:10]
    rows = ctx.find("realty_contracts", realty_contract_id=realty_contract_id)
    payer = rows[0].get("customer_id") if rows else ""
    balance = round(float((rows[0].get("invoice_balance") if rows else 0) or 0) - amt, 2)
    reference = ctx.make_id("PAY-", realty_contract_id, invoice_number, "buyer", amt, length=10).upper()
    rid = ctx.make_id("rbe_", realty_contract_id, invoice_number, "buyer", amt)
    ctx.create("realty_billing_entries", rid, realty_billing_entry_id=rid, realty_contract_id=realty_contract_id,
               customer_id=payer, event_type="realty_payment", entry_date=today, amount=amt,
               payment_reference=reference, invoice_number=invoice_number, payer_role="buyer",
               payment_method="card")
    if rows:
        ctx.update("realty_contracts", realty_contract_id, invoice_balance=balance)
    return {"status": "paid", "payment_reference": reference, "invoice_number": invoice_number, "amount": amt,
            "payment_method": "card", "entry_date": today, "invoice_balance": balance}

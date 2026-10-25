"""Hidden task tools for the fleet_invoicing difficulty of env_0062_tire_and_auto_service_chain.

Each tool makes one atomic change on a Crestline Fleet Account's records. The tools take the
values the policy fixes as arguments and record them as given; they make no eligibility,
standing or amount judgement of their own.
"""

from erlbench import ToolContext, tool


@tool(owner="user", rw="write")
def file_fleet_overlimit_dispute_8d937b85(ctx: ToolContext, fleet_account_id: str, source_fleet_txn_id: str,
                                          disputed_amount: float) -> str:
    """The business's authorized fleet contact files, in person, a dispute contesting part of one fleet invoice as
    an unapproved over-limit ticket (work charged above the account's ticket approval limit without the fleet
    manager's approval). One call registers one new open dispute on that invoice, with the disputed amount given and
    the dispute reason recorded as an unauthorized purchase; nothing on the invoice or the account balance changes.
    Afterwards the dispute shows as open on the account's dispute list with its reference number.

    Args:
        fleet_account_id: Id class — reference number of the business's fleet account, as shown by the fleet
            account lookup and read out by the agent.
        source_fleet_txn_id: Id class — reference number of the fleet invoice being disputed, as shown by the fleet
            activity lookup and read out by the agent.
        disputed_amount: Fixed-format class — the part of the invoice placed in dispute, in USD, a number with 2
            decimal places (cents), positive; the value is recorded rounded to 2 decimal places.

    Returns:
        A text rendering of a receipt dictionary with these fields: dispute_id (string, reference number of the new
        dispute), fleet_account_id (string, the account disputed on), invoice_id (string, the invoice disputed),
        reason (string, always unauthorized_purchase), disputed_amount (number, USD with 2 decimal places as
        recorded), status (string, always open) and filed_at (string, the moment the dispute was registered). A
        receipt whose status is open means the dispute was registered.
    """
    accounts = ctx.find("fleet_accounts", fleet_account_id=fleet_account_id)
    customer_id = accounts[0].get("customer_id") if accounts else ""
    amount = round(float(disputed_amount), 2)
    rid = ctx.make_id("fdsp_", fleet_account_id, source_fleet_txn_id, amount)
    filed_at = ctx.now()
    ctx.create("fleet_invoice_disputes", rid, fleet_dispute_id=rid, customer_id=customer_id,
               fleet_account_id=fleet_account_id, fleet_txn_id=source_fleet_txn_id,
               dispute_reason="unauthorized_purchase", disputed_amount=amount, dispute_status="open",
               created_at=filed_at)
    return str({"dispute_id": rid, "fleet_account_id": fleet_account_id, "invoice_id": source_fleet_txn_id,
                "reason": "unauthorized_purchase", "disputed_amount": amount, "status": "open",
                "filed_at": filed_at})


@tool(owner="agent", rw="write")
def credit_fleet_early_pay_23cbfed3(ctx: ToolContext, fleet_account_id: str, source_fleet_txn_id: str,
                                    amount: float) -> str:
    """Customer care credits the early-pay discount on one fleet invoice. One call books one early-pay discount
    entry, dated today, against that invoice for the amount given, and lowers the fleet account's outstanding
    balance by the same amount; the invoice's open amount drops by it. Afterwards the discount appears in the
    account's activity as an early-pay discount applied to that invoice.

    Args:
        fleet_account_id: Id class — reference number of the business's fleet account, as shown by the fleet
            account lookup.
        source_fleet_txn_id: Id class — reference number of the fleet invoice the discount is credited on, as shown
            by the fleet activity lookup.
        amount: Fixed-format class — the early-pay discount credited, in USD, 2 decimal places, positive (a number
            with 2 decimal places, cents); the value is recorded rounded to 2 decimal places.

    Returns:
        A text rendering of a receipt dictionary with these fields: entry_id (string, reference number of the new
        discount entry), entry_type (string, always fleet_early_pay_discount), invoice_id (string, the invoice
        credited), amount (number, USD with 2 decimal places as booked), posted_on (string, YYYY-MM-DD date of the
        entry) and outstanding_balance (number, USD with 2 decimal places, the account balance after the credit). A
        receipt carrying entry_id means the discount was booked.
    """
    value = round(float(amount), 2)
    accounts = ctx.find("fleet_accounts", fleet_account_id=fleet_account_id)
    account = accounts[0] if accounts else {}
    rid = ctx.make_id("fepd_", fleet_account_id, source_fleet_txn_id, value)
    posted_on = ctx.now()[:10]
    ctx.create("fleet_transactions", rid, fleet_txn_id=rid, fleet_account_id=fleet_account_id,
               customer_id=account.get("customer_id", ""), event_type="fleet_early_pay_discount",
               txn_date=posted_on, invoice_number="", po_number="", vehicle_id=None, store_id=None,
               service_category="none", amount=value, discount_amount=0.0, due_date="", payment_reference="",
               source_fleet_txn_id=source_fleet_txn_id, statement_month="", credit_reason="none")
    balance = round(float(account.get("outstanding_balance") or 0) - value, 2)
    ctx.update("fleet_accounts", fleet_account_id, outstanding_balance=balance)
    return str({"entry_id": rid, "entry_type": "fleet_early_pay_discount", "invoice_id": source_fleet_txn_id,
                "amount": value, "posted_on": posted_on, "outstanding_balance": balance})


@tool(owner="user", rw="write")
def file_fleet_trip_fee_dispute_f6605125(ctx: ToolContext, fleet_account_id: str, source_fleet_txn_id: str,
                                         disputed_amount: float) -> str:
    """The business's authorized fleet contact files, in person, a dispute contesting part of the amount charged
    on a mobile service visit fee invoice. One call registers one new open dispute on that visit
    fee invoice with the disputed amount given, the dispute reason being recorded as a discount not applied; nothing on
    the invoice or the account balance changes. Afterwards the dispute shows as open on the account's dispute list with
    its reference number.

    Args:
        fleet_account_id: Id class — reference number of the business's fleet account, as shown by the fleet
            account lookup and read out by the agent.
        source_fleet_txn_id: Id class — reference number of the mobile service visit fee invoice being disputed, as
            shown by the fleet activity lookup and read out by the agent.
        disputed_amount: Fixed-format class — the part of the visit fee placed in dispute, in USD, a number with 2
            decimal places (cents), positive; the value is recorded rounded to 2 decimal places.

    Returns:
        A text rendering of a receipt dictionary with these fields: dispute_id (string, reference number of the new
        dispute), fleet_account_id (string, the account disputed on), invoice_id (string, the visit fee invoice
        disputed), reason (string, always discount_not_applied), disputed_amount (number, USD with 2 decimal places as
        recorded), status (string, always open) and filed_at (string, the moment the dispute was registered). A
        receipt whose status is open means the dispute was registered.
    """
    accounts = ctx.find("fleet_accounts", fleet_account_id=fleet_account_id)
    customer_id = accounts[0].get("customer_id") if accounts else ""
    amount = round(float(disputed_amount), 2)
    rid = ctx.make_id("fdsp_", fleet_account_id, source_fleet_txn_id, amount, "visit_fee")
    filed_at = ctx.now()
    ctx.create("fleet_invoice_disputes", rid, fleet_dispute_id=rid, customer_id=customer_id,
               fleet_account_id=fleet_account_id, fleet_txn_id=source_fleet_txn_id,
               dispute_reason="discount_not_applied", disputed_amount=amount, dispute_status="open",
               created_at=filed_at)
    return str({"dispute_id": rid, "fleet_account_id": fleet_account_id, "invoice_id": source_fleet_txn_id,
                "reason": "discount_not_applied", "disputed_amount": amount, "status": "open",
                "filed_at": filed_at})


@tool(owner="agent", rw="write")
def credit_fleet_tire_discount_840e1cf3(ctx: ToolContext, fleet_account_id: str, source_fleet_txn_id: str,
                                        amount: float) -> str:
    """Customer care issues a pricing correction credit memo on one fleet tire invoice. One call books one credit
    memo, dated today, against that tire invoice for the amount given, with the credit reason recorded as a pricing
    correction, and lowers the fleet account's outstanding balance by the same amount; the invoice's open amount drops
    by it. Afterwards the credit memo appears in the account's activity against that invoice.

    Args:
        fleet_account_id: Id class — reference number of the business's fleet account, as shown by the fleet
            account lookup.
        source_fleet_txn_id: Id class — reference number of the fleet tire invoice credited, as shown by the fleet
            activity lookup.
        amount: Fixed-format class — the credit issued, in USD, 2 decimal places, positive (a number with 2 decimal
            places, cents); the value is recorded rounded to 2 decimal places.

    Returns:
        A text rendering of a receipt dictionary with these fields: entry_id (string, reference number of the new
        credit memo), entry_type (string, always fleet_credit_memo), credit_reason (string, always pricing_correction),
        invoice_id (string, the invoice credited), amount (number, USD with 2 decimal places as booked), posted_on
        (string, YYYY-MM-DD date of the entry) and outstanding_balance (number, USD with 2 decimal places, the account
        balance after the credit). A receipt carrying entry_id means the credit memo was booked.
    """
    value = round(float(amount), 2)
    accounts = ctx.find("fleet_accounts", fleet_account_id=fleet_account_id)
    account = accounts[0] if accounts else {}
    rid = ctx.make_id("fcmt_", fleet_account_id, source_fleet_txn_id, value)
    posted_on = ctx.now()[:10]
    ctx.create("fleet_transactions", rid, fleet_txn_id=rid, fleet_account_id=fleet_account_id,
               customer_id=account.get("customer_id", ""), event_type="fleet_credit_memo", txn_date=posted_on,
               invoice_number="", po_number="", vehicle_id=None, store_id=None, service_category="none",
               amount=value, discount_amount=0.0, due_date="", payment_reference="",
               source_fleet_txn_id=source_fleet_txn_id, statement_month="", credit_reason="pricing_correction")
    balance = round(float(account.get("outstanding_balance") or 0) - value, 2)
    ctx.update("fleet_accounts", fleet_account_id, outstanding_balance=balance)
    return str({"entry_id": rid, "entry_type": "fleet_credit_memo", "credit_reason": "pricing_correction",
                "invoice_id": source_fleet_txn_id, "amount": value, "posted_on": posted_on,
                "outstanding_balance": balance})


@tool(owner="agent", rw="write")
def credit_fleet_brake_discount_3a9816af(ctx: ToolContext, fleet_account_id: str, source_fleet_txn_id: str,
                                         amount: float) -> str:
    """Customer care issues a pricing correction credit memo on one fleet brake invoice (a brake job charged to the
    account). One call books one credit memo, dated today, against that brake invoice for the amount given, with the
    credit reason recorded as a pricing correction, and lowers the fleet account's outstanding balance by the same
    amount; the invoice's open amount drops by it. Afterwards the credit memo appears in the account's activity
    against that invoice.

    Args:
        fleet_account_id: Id class — reference number of the business's fleet account, as shown by the fleet
            account lookup.
        source_fleet_txn_id: Id class — reference number of the fleet brake invoice credited, as shown by the fleet
            activity lookup.
        amount: Fixed-format class — the credit issued, in USD, 2 decimal places, positive (a number with 2 decimal
            places, cents); the value is recorded rounded to 2 decimal places.

    Returns:
        A text rendering of a receipt dictionary with these fields: entry_id (string, reference number of the new
        credit memo), entry_type (string, always fleet_credit_memo), credit_reason (string, always pricing_correction),
        invoice_id (string, the brake invoice credited), amount (number, USD with 2 decimal places as booked),
        posted_on (string, YYYY-MM-DD date of the entry) and outstanding_balance (number, USD with 2 decimal places, the
        account balance after the credit). A receipt carrying entry_id means the credit memo was booked.
    """
    value = round(float(amount), 2)
    accounts = ctx.find("fleet_accounts", fleet_account_id=fleet_account_id)
    account = accounts[0] if accounts else {}
    rid = ctx.make_id("fcmb_", fleet_account_id, source_fleet_txn_id, value)
    posted_on = ctx.now()[:10]
    ctx.create("fleet_transactions", rid, fleet_txn_id=rid, fleet_account_id=fleet_account_id,
               customer_id=account.get("customer_id", ""), event_type="fleet_credit_memo", txn_date=posted_on,
               invoice_number="", po_number="", vehicle_id=None, store_id=None, service_category="none",
               amount=value, discount_amount=0.0, due_date="", payment_reference="",
               source_fleet_txn_id=source_fleet_txn_id, statement_month="", credit_reason="pricing_correction")
    balance = round(float(account.get("outstanding_balance") or 0) - value, 2)
    ctx.update("fleet_accounts", fleet_account_id, outstanding_balance=balance)
    return str({"entry_id": rid, "entry_type": "fleet_credit_memo", "credit_reason": "pricing_correction",
                "invoice_id": source_fleet_txn_id, "amount": value, "posted_on": posted_on,
                "outstanding_balance": balance})


@tool(owner="agent", rw="write")
def assess_fleet_late_charge_341e13fe(ctx: ToolContext, fleet_account_id: str, statement_month: str,
                                      amount: float) -> str:
    """Customer care assesses the month-end late charge on a fleet account for one statement month. One call books one
    late charge entry, dated today, for the statement month and amount given, and raises the fleet account's
    outstanding balance by the same amount. Afterwards the late charge appears in the account's activity with its
    statement month.

    Args:
        fleet_account_id: Id class — reference number of the business's fleet account, as shown by the fleet
            account lookup.
        statement_month: Fixed-format class — the month-end statement the charge belongs to, written YYYY-MM.
        amount: Fixed-format class — the late charge assessed, in USD, 2 decimal places, positive (a number with 2
            decimal places, cents); the value is recorded rounded to 2 decimal places.

    Returns:
        A text rendering of a receipt dictionary with these fields: entry_id (string, reference number of the new late
        charge), entry_type (string, always fleet_late_charge), statement_month (string, YYYY-MM), amount (number, USD
        with 2 decimal places as booked), posted_on (string, YYYY-MM-DD date of the entry) and outstanding_balance
        (number, USD with 2 decimal places, the account balance after the charge). A receipt carrying entry_id means
        the late charge was booked.
    """
    value = round(float(amount), 2)
    accounts = ctx.find("fleet_accounts", fleet_account_id=fleet_account_id)
    account = accounts[0] if accounts else {}
    rid = ctx.make_id("flch_", fleet_account_id, statement_month, value)
    posted_on = ctx.now()[:10]
    ctx.create("fleet_transactions", rid, fleet_txn_id=rid, fleet_account_id=fleet_account_id,
               customer_id=account.get("customer_id", ""), event_type="fleet_late_charge", txn_date=posted_on,
               invoice_number="", po_number="", vehicle_id=None, store_id=None, service_category="none",
               amount=value, discount_amount=0.0, due_date="", payment_reference="", source_fleet_txn_id=None,
               statement_month=statement_month, credit_reason="none")
    balance = round(float(account.get("outstanding_balance") or 0) + value, 2)
    ctx.update("fleet_accounts", fleet_account_id, outstanding_balance=balance)
    return str({"entry_id": rid, "entry_type": "fleet_late_charge", "statement_month": statement_month,
                "amount": value, "posted_on": posted_on, "outstanding_balance": balance})

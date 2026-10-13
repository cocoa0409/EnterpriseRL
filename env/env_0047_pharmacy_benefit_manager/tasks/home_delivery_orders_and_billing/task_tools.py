"""Hidden task tools for the home_delivery_orders_and_billing difficulty (category mail) of
env_0047_pharmacy_benefit_manager (Northbridge Rx Home Delivery Pharmacy).

Every tool here is HIDDEN: it is named only by an extended policy's target_tool in
mail.extended.yaml and is reached through unlock_* -> call_*. Each tool performs one atomic
business write with the values it is given; it checks no eligibility, prerequisite or
amount, and it never computes a policy figure on the caller's behalf.
"""

from erlbench import ToolContext, tool


@tool(owner="agent", rw="write")
def book_expedited_fee_b4b37c53(ctx: ToolContext, mail_account_id: str, source_order_id: str,
                                shipping_method: str, shipping_fee: float) -> str:
    """Book an expedited shipping fee on one home delivery order of a member's Northbridge Rx Home
    Delivery account. One call records one shipping-fee charge against the named order, dated
    today, and adds the fee to the account's balance due, so the member owes that much more and
    the charge appears with the order and on the next balance statement. The call succeeds when
    the receipt returns the new charge's reference number and the updated balance due.

    Args:
        mail_account_id: Id class — the reference number of the member's home delivery account the fee is booked on, as returned by the home delivery account lookup.
        source_order_id: Id class — the reference number of the placed order the fee belongs to (the order reference that the shipment record of that order carries), as returned by the home delivery order lookup.
        shipping_method: Enum class — the expedited service the fee is for, written exactly as one of: two_day when the fee is for two-day delivery of the order; overnight when the fee is for overnight delivery of the order; standard when the fee is for the program's standard ground delivery; cold_chain when the fee is for refrigerated cold-chain packaging and carrier.
        shipping_fee: Fixed-format class — the fee amount charged to the member, in USD, a non-negative number with 2 decimal places, already rounded to the cent by the caller.

    Returns:
        A dictionary rendered as text with: fee_entry_id (string, the reference number of the new
        shipping-fee charge on the order), source_order_id (string, the order the fee was booked
        on), shipping_method (string, the service recorded), shipping_fee (number, USD with 2
        decimal places, the fee booked), balance_due (number, USD with 2 decimal places, the
        account's balance due after the fee) and status ("booked", meaning the charge now stands
        on the account).
    """
    fee = round(float(shipping_fee), 2)
    found = ctx.find("mail_accounts", mail_account_id=mail_account_id)
    acct = found[0] if found else {}
    rid = ctx.make_id("mfee_", mail_account_id, source_order_id, shipping_method, fee)
    ctx.create("mail_orders", rid, mail_order_id=rid, mail_account_id=mail_account_id,
               customer_id=acct.get("customer_id", ""), event_type="mail_shipping_charged",
               source_order_id=source_order_id, order_date=ctx.now()[:10],
               shipping_method=shipping_method, shipping_fee=fee)
    new_balance = round(float(acct.get("balance_due") or 0.0) + fee, 2)
    ctx.update("mail_accounts", mail_account_id, balance_due=new_balance)
    return str({"fee_entry_id": rid, "source_order_id": source_order_id,
                "shipping_method": shipping_method, "shipping_fee": fee,
                "balance_due": new_balance, "status": "booked"})


@tool(owner="agent", rw="write")
def credit_missed_delivery_02a65815(ctx: ToolContext, mail_account_id: str, source_order_id: str,
                                    amount: float) -> str:
    """Post a missed-delivery credit for one home delivery order to a member's Northbridge Rx Home
    Delivery account. One call records one credit against the named order, dated today, with the
    reason shipping fee waived, and lowers the account's balance due by the credited amount, so
    the member owes that much less and the credit appears on the next balance statement. The call
    succeeds when the receipt returns the new credit's reference number and the updated balance.

    Args:
        mail_account_id: Id class — the reference number of the member's home delivery account the credit is posted to, as returned by the home delivery account lookup.
        source_order_id: Id class — the reference number of the placed order whose shipment the credit concerns (the order reference carried by that order's shipment and replacement records), as returned by the home delivery order lookup.
        amount: Fixed-format class — the credit amount, in USD, a positive number with 2 decimal places, already rounded to the cent by the caller.

    Returns:
        A dictionary rendered as text with: credit_id (string, the reference number of the new
        credit), source_order_id (string, the order credited), amount (number, USD with 2 decimal
        places, the credit posted), credit_reason ("shipping_fee_waived"), balance_due (number,
        USD with 2 decimal places, the account's balance due after the credit) and status
        ("posted", meaning the credit now stands on the account).
    """
    amt = round(float(amount), 2)
    found = ctx.find("mail_accounts", mail_account_id=mail_account_id)
    acct = found[0] if found else {}
    rid = ctx.make_id("mcrd_", mail_account_id, source_order_id, amt)
    ctx.create("mail_payments", rid, mail_payment_id=rid, mail_account_id=mail_account_id,
               customer_id=acct.get("customer_id", ""), event_type="mail_credit_issued",
               source_order_id=source_order_id, payment_date=ctx.now()[:10], amount=amt,
               payment_method="not_applicable", credit_reason="shipping_fee_waived",
               installment_number=0, deductible_amount=0.0, accumulator_amount=0.0)
    new_balance = round(float(acct.get("balance_due") or 0.0) - amt, 2)
    ctx.update("mail_accounts", mail_account_id, balance_due=new_balance)
    return str({"credit_id": rid, "source_order_id": source_order_id, "amount": amt,
                "credit_reason": "shipping_fee_waived", "balance_due": new_balance,
                "status": "posted"})


@tool(owner="user", rw="write")
def pay_plan_down_payment_b796ac1b(ctx: ToolContext, mail_account_id: str, amount: float,
                                   payment_method: str) -> str:
    """Pay the down payment of a payment plan on your own Northbridge Rx Home Delivery account.
    One call charges the stated amount to the payment instrument you name, records it as a member
    payment dated today on the account, and lowers the account's balance due by that amount. The
    call succeeds when the receipt returns the payment confirmation number and the balance due
    left after the payment.

    Args:
        mail_account_id: Id class — the reference number of your home delivery account, as read to you by the representative from the home delivery account lookup.
        amount: Fixed-format class — the down payment you pay now, in USD, a positive number with 2 decimal places exactly as the representative quoted it.
        payment_method: Enum class — the instrument you pay with, written exactly as one of: credit_card when you pay with a credit card; debit_card when you pay with a debit card; hsa_fsa_card when you pay with a health savings or flexible spending account card; check when you mail a paper check; not_applicable is reserved for credits and is never correct for a payment.

    Returns:
        A dictionary rendered as text with: payment_id (string, the payment confirmation number),
        amount (number, USD with 2 decimal places, the amount paid), payment_method (string, the
        instrument charged), balance_due (number, USD with 2 decimal places, the balance left on
        the account) and status ("posted", meaning the payment has been applied to the balance).
    """
    amt = round(float(amount), 2)
    found = ctx.find("mail_accounts", mail_account_id=mail_account_id)
    acct = found[0] if found else {}
    rid = ctx.make_id("mpay_", mail_account_id, amt, payment_method, "down_payment")
    ctx.create("mail_payments", rid, mail_payment_id=rid, mail_account_id=mail_account_id,
               customer_id=acct.get("customer_id", ""), event_type="mail_payment_posted",
               source_order_id="", payment_date=ctx.now()[:10], amount=amt,
               payment_method=payment_method, credit_reason="not_applicable",
               installment_number=0, deductible_amount=0.0, accumulator_amount=0.0)
    new_balance = round(float(acct.get("balance_due") or 0.0) - amt, 2)
    ctx.update("mail_accounts", mail_account_id, balance_due=new_balance)
    return str({"payment_id": rid, "amount": amt, "payment_method": payment_method,
                "balance_due": new_balance, "status": "posted"})


@tool(owner="user", rw="write")
def confirm_payment_plan_4c427b9b(ctx: ToolContext, mail_account_id: str, plan_months: int,
                                  plan_monthly_amount: float) -> str:
    """Confirm a payment plan on your own Northbridge Rx Home Delivery account. One call records
    your confirmed payment plan as a completed payment-plan request dated today, carrying the
    number of monthly installments and the installment amount, and sets the plan length on the
    account, so the plan is in force and your monthly installments are scheduled. The call
    succeeds when the receipt returns the plan's reference number with the months and installment
    recorded.

    Args:
        mail_account_id: Id class — the reference number of your home delivery account, as read to you by the representative from the home delivery account lookup.
        plan_months: Fixed-format class — the number of monthly installments in the plan, an integer count of at least 1, exactly as the representative quoted it.
        plan_monthly_amount: Fixed-format class — the amount of each monthly installment, in USD, a positive number with 2 decimal places exactly as the representative quoted it.

    Returns:
        A dictionary rendered as text with: plan_request_id (string, the reference number of the
        confirmed payment plan), plan_months (integer, the installments in the plan),
        plan_monthly_amount (number, USD with 2 decimal places, each installment) and status
        ("completed", meaning the plan is confirmed and in force on the account).
    """
    months = int(plan_months)
    monthly = round(float(plan_monthly_amount), 2)
    found = ctx.find("mail_accounts", mail_account_id=mail_account_id)
    acct = found[0] if found else {}
    rid = ctx.make_id("mplan_", mail_account_id, months, monthly)
    ctx.create("mail_service_requests", rid, mail_service_request_id=rid,
               mail_account_id=mail_account_id, customer_id=acct.get("customer_id", ""),
               request_type="payment_plan", request_status="completed",
               request_date=ctx.now()[:10], drug_name="not_applicable", transfer_from_npi="",
               retail_rx_number="", plan_months=months, plan_monthly_amount=monthly)
    ctx.update("mail_accounts", mail_account_id, payment_plan_months=months)
    return str({"plan_request_id": rid, "plan_months": months,
                "plan_monthly_amount": monthly, "status": "completed"})


@tool(owner="agent", rw="write")
def credit_dispensing_delay_47b21103(ctx: ToolContext, mail_account_id: str, source_order_id: str,
                                     amount: float) -> str:
    """Post a dispensing-delay credit for one home delivery order to a member's Northbridge Rx
    Home Delivery account, for an expedited order the pharmacy dispensed late. One call records
    one credit against the named order, dated today, with the reason shipping fee waived, and
    lowers the account's balance due by the credited amount, so the member owes that much less
    and the credit appears on the next balance statement. The call succeeds when the receipt
    returns the new credit's reference number and the updated balance due.

    Args:
        mail_account_id: Id class — the reference number of the member's home delivery account the credit is posted to, as returned by the home delivery account lookup.
        source_order_id: Id class — the reference number of the placed order that was dispensed late (the order reference carried by that order's shipment record), as returned by the home delivery order lookup.
        amount: Fixed-format class — the credit amount, in USD, a positive number with 2 decimal places, already rounded to the cent by the caller.

    Returns:
        A dictionary rendered as text with: credit_id (string, the reference number of the new
        credit), source_order_id (string, the order credited), amount (number, USD with 2 decimal
        places, the credit posted), credit_reason ("shipping_fee_waived"), balance_due (number,
        USD with 2 decimal places, the account's balance due after the credit) and status
        ("posted", meaning the credit now stands on the account).
    """
    amt = round(float(amount), 2)
    found = ctx.find("mail_accounts", mail_account_id=mail_account_id)
    acct = found[0] if found else {}
    rid = ctx.make_id("mdly_", mail_account_id, source_order_id, amt)
    ctx.create("mail_payments", rid, mail_payment_id=rid, mail_account_id=mail_account_id,
               customer_id=acct.get("customer_id", ""), event_type="mail_credit_issued",
               source_order_id=source_order_id, payment_date=ctx.now()[:10], amount=amt,
               payment_method="not_applicable", credit_reason="shipping_fee_waived",
               installment_number=0, deductible_amount=0.0, accumulator_amount=0.0)
    new_balance = round(float(acct.get("balance_due") or 0.0) - amt, 2)
    ctx.update("mail_accounts", mail_account_id, balance_due=new_balance)
    return str({"credit_id": rid, "source_order_id": source_order_id, "amount": amt,
                "credit_reason": "shipping_fee_waived", "balance_due": new_balance,
                "status": "posted"})


@tool(owner="user", rw="write")
def pay_plan_installment_04171a93(ctx: ToolContext, mail_account_id: str, amount: float,
                                  installment_number: int, payment_method: str) -> str:
    """Pay installments of your own payment plan on your Northbridge Rx Home Delivery account.
    One call charges the stated amount to the payment instrument you name, records it as a plan
    installment payment dated today carrying the installment number it brings the plan through,
    and lowers the account's balance due by that amount. The call succeeds when the receipt
    returns the payment confirmation number, the installment number recorded and the balance left.

    Args:
        mail_account_id: Id class — the reference number of your home delivery account, as read to you by the representative from the home delivery account lookup.
        amount: Fixed-format class — the amount you pay now, in USD, a positive number with 2 decimal places exactly as the representative quoted it.
        installment_number: Fixed-format class — the number of the last plan installment this payment covers, an integer of at least 1 (installment sequence, 0 is never used here), exactly as the representative quoted it.
        payment_method: Enum class — the instrument you pay with, written exactly as one of: credit_card when you pay with a credit card; debit_card when you pay with a debit card; hsa_fsa_card when you pay with a health savings or flexible spending account card; check when you mail a paper check; not_applicable is reserved for credits and is never correct for a payment.

    Returns:
        A dictionary rendered as text with: payment_id (string, the payment confirmation number),
        amount (number, USD with 2 decimal places, the amount paid), installment_number (integer,
        the plan installment the payment brings the plan through), payment_method (string, the
        instrument charged), balance_due (number, USD with 2 decimal places, the balance left on
        the account) and status ("posted", meaning the installment payment has been applied).
    """
    amt = round(float(amount), 2)
    inst = int(installment_number)
    found = ctx.find("mail_accounts", mail_account_id=mail_account_id)
    acct = found[0] if found else {}
    rid = ctx.make_id("minst_", mail_account_id, amt, inst, payment_method)
    ctx.create("mail_payments", rid, mail_payment_id=rid, mail_account_id=mail_account_id,
               customer_id=acct.get("customer_id", ""), event_type="mail_payment_posted",
               source_order_id="", payment_date=ctx.now()[:10], amount=amt,
               payment_method=payment_method, credit_reason="not_applicable",
               installment_number=inst, deductible_amount=0.0, accumulator_amount=0.0)
    new_balance = round(float(acct.get("balance_due") or 0.0) - amt, 2)
    ctx.update("mail_accounts", mail_account_id, balance_due=new_balance)
    return str({"payment_id": rid, "amount": amt, "installment_number": inst,
                "payment_method": payment_method, "balance_due": new_balance, "status": "posted"})


@tool(owner="user", rw="write")
def pay_past_due_balance_de0abde8(ctx: ToolContext, mail_account_id: str, amount: float,
                                  payment_method: str) -> str:
    """Pay the past-due amount on your own Northbridge Rx Home Delivery account to bring it
    current. One call charges the stated amount to the payment instrument you name, records it as
    a member payment dated today that is not a plan installment, and lowers the account's balance
    due by that amount. The call succeeds when the receipt returns the payment confirmation number
    and the balance left after the payment.

    Args:
        mail_account_id: Id class — the reference number of your home delivery account, as read to you by the representative from the home delivery account lookup.
        amount: Fixed-format class — the amount you pay now, in USD, a positive number with 2 decimal places exactly as the representative quoted it.
        payment_method: Enum class — the instrument you pay with, written exactly as one of: credit_card when you pay with a credit card; debit_card when you pay with a debit card; hsa_fsa_card when you pay with a health savings or flexible spending account card; check when you mail a paper check; not_applicable is reserved for credits and is never correct for a payment.

    Returns:
        A dictionary rendered as text with: payment_id (string, the payment confirmation number),
        amount (number, USD with 2 decimal places, the amount paid), payment_method (string, the
        instrument charged), balance_due (number, USD with 2 decimal places, the balance left on
        the account) and status ("posted", meaning the payment has been applied to the balance).
    """
    amt = round(float(amount), 2)
    found = ctx.find("mail_accounts", mail_account_id=mail_account_id)
    acct = found[0] if found else {}
    rid = ctx.make_id("mpdue_", mail_account_id, amt, payment_method)
    ctx.create("mail_payments", rid, mail_payment_id=rid, mail_account_id=mail_account_id,
               customer_id=acct.get("customer_id", ""), event_type="mail_payment_posted",
               source_order_id="", payment_date=ctx.now()[:10], amount=amt,
               payment_method=payment_method, credit_reason="not_applicable",
               installment_number=0, deductible_amount=0.0, accumulator_amount=0.0)
    new_balance = round(float(acct.get("balance_due") or 0.0) - amt, 2)
    ctx.update("mail_accounts", mail_account_id, balance_due=new_balance)
    return str({"payment_id": rid, "amount": amt, "payment_method": payment_method,
                "balance_due": new_balance, "status": "posted"})

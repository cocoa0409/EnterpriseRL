"""Hidden task tools of the PrePay Power Enrollment and Balances difficulty
(env_0043_rural_electric_cooperative, category prepay).

Each tool performs one atomic write on a PrePay Power enrollment and takes the value the agent
(or the member, for a member-owned tool) has already worked out from the published PrePay Power
rules. No tool judges eligibility, checks a prerequisite or computes a policy amount.
"""

from erlbench import ToolContext, tool


@tool(owner="agent", rw="write")
def post_carried_credit_69e6c97d(ctx: ToolContext, prepay_account_id: str, service_account_id: str,
                                 carried_amount: float) -> str:
    """Carry a standard-billing credit balance of a member's service account into that account's PrePay
    Power enrollment. One call adds one credit-adjustment entry, dated today, to the enrollment's PrePay
    ledger with the reason carried-in standard-billing credit and the service account named as its source,
    and raises the enrollment's prepaid balance by the carried amount, so the member sees the credit and the
    new prepaid balance at once. Nothing is written on the service account itself.

    Args:
        prepay_account_id: Id class — the reference number of the PrePay Power enrollment that receives the credit, as returned by the PrePay enrollment lookup for the member.
        service_account_id: Id class — the reference number of the enrolled service account whose credit balance is carried in, as returned by the service account lookup for the member.
        carried_amount: Fixed-format class — the amount credited to the prepaid balance, in USD, a positive number with 2 decimal places (rounded to the cent); never empty.

    Returns:
        A text receipt of a dictionary with these fields: status ('posted' when the credit was booked);
        ledger_entry_id (reference number of the new credit-adjustment entry); prepay_account_id (the
        enrollment credited); adjustment_reason (always 'postpaid_credit_transfer'); source_reference_id
        (the service account the credit comes from); amount (the credited amount in USD, 2 decimal
        places); entry_date (posting date, YYYY-MM-DD); prepaid_balance (the enrollment's prepaid balance
        after the credit, in USD, 2 decimal places).
    """
    amount = round(float(carried_amount), 2)
    rows = ctx.find("prepay_accounts", prepay_account_id=prepay_account_id)
    acct = rows[0] if rows else {}
    rid = ctx.make_id("pct_", prepay_account_id, service_account_id, amount)
    day = ctx.now()[:10]
    ctx.create("prepay_ledger", rid, ledger_entry_id=rid, prepay_account_id=prepay_account_id,
               customer_id=acct.get("customer_id"), event_type="prepay_credit_adjustment", entry_date=day,
               adjustment_reason="postpaid_credit_transfer", amount=amount, source_reference_id=service_account_id)
    new_balance = round(float(acct.get("prepaid_balance") or 0) + amount, 2)
    ctx.update("prepay_accounts", prepay_account_id, prepaid_balance=new_balance)
    return str({"status": "posted", "ledger_entry_id": rid, "prepay_account_id": prepay_account_id,
                "adjustment_reason": "postpaid_credit_transfer", "source_reference_id": service_account_id,
                "amount": amount, "entry_date": day, "prepaid_balance": new_balance})


@tool(owner="user", rw="write")
def make_activation_payment_0416a855(ctx: ToolContext, prepay_account_id: str, gross_payment_amount: float) -> str:
    """The member pays the activation payment on their own PrePay Power enrollment that is awaiting
    activation, keying their card into the cooperative's phone payment line. One call posts one payment,
    dated today, through the phone card channel; the whole payment is credited to the prepaid balance with
    no part taken toward arrears, the enrollment's prepaid balance rises by the amount paid, and the
    payment line issues a confirmation number the member can quote.

    Args:
        prepay_account_id: Id class — the reference number of the member's PrePay Power enrollment being activated, as read to the member by the member services representative from the PrePay enrollment lookup.
        gross_payment_amount: Fixed-format class — the full amount the member pays, in USD, a positive number with 2 decimal places (rounded to the cent), exactly as quoted to the member; never empty.

    Returns:
        A text receipt of a dictionary with these fields: status ('paid' when the payment posted);
        payment_reference (the confirmation number issued by the phone payment line, nine digits
        beginning with 42); ledger_entry_id (reference number of the payment entry); prepay_account_id
        (the enrollment paid); gross_payment_amount (the amount paid in USD, 2 decimal places);
        credited_to_balance (the part credited to the prepaid balance, equal to the amount paid);
        entry_date (posting date, YYYY-MM-DD); prepaid_balance (the prepaid balance after the payment,
        in USD, 2 decimal places).
    """
    gross = round(float(gross_payment_amount), 2)
    rows = ctx.find("prepay_accounts", prepay_account_id=prepay_account_id)
    acct = rows[0] if rows else {}
    rid = ctx.make_id("ppy_", prepay_account_id, gross, "activation")
    reference = "42" + str(int(rid[-12:], 16) % 10_000_000).zfill(7)
    day = ctx.now()[:10]
    ctx.create("prepay_ledger", rid, ledger_entry_id=rid, prepay_account_id=prepay_account_id,
               customer_id=acct.get("customer_id"), event_type="prepay_payment", entry_date=day,
               payment_channel="phone_ivr_card", gross_payment_amount=gross, amount=gross,
               payment_reference=reference, debt_recovery_applies=False)
    new_balance = round(float(acct.get("prepaid_balance") or 0) + gross, 2)
    ctx.update("prepay_accounts", prepay_account_id, prepaid_balance=new_balance)
    return str({"status": "paid", "payment_reference": reference, "ledger_entry_id": rid,
                "prepay_account_id": prepay_account_id, "gross_payment_amount": gross,
                "credited_to_balance": gross, "entry_date": day, "prepaid_balance": new_balance})


@tool(owner="agent", rw="write")
def post_meter_error_refund_29b7beca(ctx: ToolContext, prepay_account_id: str, meter_test_id: str,
                                     refund_amount: float) -> str:
    """Credit a PrePay Power enrollment with the meter error refund owed after a meter test found the meter
    fast. One call adds one credit-adjustment entry, dated today, to the enrollment's PrePay ledger with the
    reason meter error refund and the meter test named as its source, and raises the enrollment's prepaid
    balance by the refunded amount; the member sees the refund line and the new prepaid balance at once.
    Nothing is written on the service account or on the meter test record.

    Args:
        prepay_account_id: Id class — the reference number of the PrePay Power enrollment that receives the refund, as returned by the PrePay enrollment lookup for the member.
        meter_test_id: Id class — the reference number of the meter test record that found the meter fast, as returned by the outage, trouble and meter test lookup for the enrolled service account.
        refund_amount: Fixed-format class — the amount credited to the prepaid balance, in USD, a positive number with 2 decimal places (rounded to the cent); never empty.

    Returns:
        A text receipt of a dictionary with these fields: status ('posted' when the refund was booked);
        ledger_entry_id (reference number of the new credit-adjustment entry); prepay_account_id (the
        enrollment credited); adjustment_reason (always 'meter_error_refund'); source_reference_id (the
        meter test the refund comes from); amount (the refund in USD, 2 decimal places); entry_date
        (posting date, YYYY-MM-DD); prepaid_balance (the prepaid balance after the refund, in USD, 2
        decimal places).
    """
    amount = round(float(refund_amount), 2)
    rows = ctx.find("prepay_accounts", prepay_account_id=prepay_account_id)
    acct = rows[0] if rows else {}
    rid = ctx.make_id("pca_", prepay_account_id, meter_test_id, amount)
    day = ctx.now()[:10]
    ctx.create("prepay_ledger", rid, ledger_entry_id=rid, prepay_account_id=prepay_account_id,
               customer_id=acct.get("customer_id"), event_type="prepay_credit_adjustment", entry_date=day,
               adjustment_reason="meter_error_refund", amount=amount, source_reference_id=meter_test_id)
    new_balance = round(float(acct.get("prepaid_balance") or 0) + amount, 2)
    ctx.update("prepay_accounts", prepay_account_id, prepaid_balance=new_balance)
    return str({"status": "posted", "ledger_entry_id": rid, "prepay_account_id": prepay_account_id,
                "adjustment_reason": "meter_error_refund", "source_reference_id": meter_test_id,
                "amount": amount, "entry_date": day, "prepaid_balance": new_balance})


@tool(owner="agent", rw="write")
def reset_low_balance_alert_c29238fa(ctx: ToolContext, prepay_account_id: str,
                                     low_balance_alert_amount: float) -> str:
    """Set the low-balance alert amount of a PrePay Power enrollment to a new figure. One call replaces the
    amount below which the member is sent a low-balance alert on that enrollment; the alert channel, the
    balances and every ledger entry stay as they are, and the next low-balance alert follows the new amount.

    Args:
        prepay_account_id: Id class — the reference number of the PrePay Power enrollment whose alert amount is reset, as returned by the PrePay enrollment lookup for the member.
        low_balance_alert_amount: Fixed-format class — the new low-balance alert amount, in USD, a positive number with 2 decimal places (rounded to the cent); never empty.

    Returns:
        A text receipt of a dictionary with these fields: status ('updated' when the new amount is on the
        enrollment); prepay_account_id (the enrollment changed); previous_alert_amount (the amount before
        the change, in USD, 2 decimal places); low_balance_alert_amount (the new amount, in USD, 2 decimal
        places); alert_channel (the unchanged channel the alerts go through).
    """
    amount = round(float(low_balance_alert_amount), 2)
    rows = ctx.find("prepay_accounts", prepay_account_id=prepay_account_id)
    acct = rows[0] if rows else {}
    ctx.update("prepay_accounts", prepay_account_id, low_balance_alert_amount=amount)
    return str({"status": "updated", "prepay_account_id": prepay_account_id,
                "previous_alert_amount": acct.get("low_balance_alert_amount"),
                "low_balance_alert_amount": amount, "alert_channel": acct.get("alert_channel")})


@tool(owner="user", rw="write")
def make_restore_payment_2eb3ad28(ctx: ToolContext, prepay_account_id: str, gross_payment_amount: float) -> str:
    """The member pays, on their own active or low-balance-disconnected PrePay Power enrollment that carries
    no arrears, the payment quoted to restore service, keying their card into the cooperative's phone
    payment line. One call posts one payment, dated today, through the phone card channel; the whole payment
    is credited to the prepaid balance with no part taken toward arrears, the prepaid balance rises by the
    amount paid, and the payment line issues a confirmation number the member can quote.

    Args:
        prepay_account_id: Id class — the reference number of the member's PrePay Power enrollment being paid, as read to the member by the member services representative from the PrePay enrollment lookup.
        gross_payment_amount: Fixed-format class — the full amount the member pays, in USD, a positive number with 2 decimal places (rounded to the cent), exactly as quoted to the member; never empty.

    Returns:
        A text receipt of a dictionary with these fields: status ('paid' when the payment posted);
        payment_reference (the confirmation number issued by the phone payment line, nine digits
        beginning with 42); ledger_entry_id (reference number of the payment entry); prepay_account_id
        (the enrollment paid); gross_payment_amount (the amount paid in USD, 2 decimal places);
        credited_to_balance (the part credited to the prepaid balance, equal to the amount paid);
        entry_date (posting date, YYYY-MM-DD); prepaid_balance (the prepaid balance after the payment,
        in USD, 2 decimal places).
    """
    gross = round(float(gross_payment_amount), 2)
    rows = ctx.find("prepay_accounts", prepay_account_id=prepay_account_id)
    acct = rows[0] if rows else {}
    rid = ctx.make_id("ppy_", prepay_account_id, gross, "restore")
    reference = "42" + str(int(rid[-12:], 16) % 10_000_000).zfill(7)
    day = ctx.now()[:10]
    ctx.create("prepay_ledger", rid, ledger_entry_id=rid, prepay_account_id=prepay_account_id,
               customer_id=acct.get("customer_id"), event_type="prepay_payment", entry_date=day,
               payment_channel="phone_ivr_card", gross_payment_amount=gross, amount=gross,
               payment_reference=reference, debt_recovery_applies=False)
    new_balance = round(float(acct.get("prepaid_balance") or 0) + gross, 2)
    ctx.update("prepay_accounts", prepay_account_id, prepaid_balance=new_balance)
    return str({"status": "paid", "payment_reference": reference, "ledger_entry_id": rid,
                "prepay_account_id": prepay_account_id, "gross_payment_amount": gross,
                "credited_to_balance": gross, "entry_date": day, "prepaid_balance": new_balance})

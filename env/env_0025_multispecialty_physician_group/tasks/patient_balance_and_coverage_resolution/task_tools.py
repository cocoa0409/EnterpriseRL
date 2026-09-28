"""Hidden task tools of difficulty patient_balance_and_coverage_resolution (category billing).
Path: env/env_0025_multispecialty_physician_group/tasks/patient_balance_and_coverage_resolution/task_tools.py

Each tool performs exactly one atomic write on the Patient Financial Account and its ledger with the
arguments it is given. No tool checks eligibility, prerequisites, ownership, status or amounts: every
business judgement is made by the agent from the published policy and the records it has read.
Tool names are registered only in billing.extended.yaml (extended_policies[].target_tool) and are
reached through the unlock_* -> call_* meta tools.
"""

from erlbench import ToolContext, tool


@tool(owner="agent", rw="write")
def charge_card_on_file_381e2993(ctx: ToolContext, billing_account_id: str, applies_to_txn_id: str,
                                 charge_amount_usd: float) -> str:
    """Charge the payment card the patient keeps on file with Linden Ridge for part or all of an
    encounter's post-adjudication balance, and post that card charge to the patient's financial account.

    One call records one card-on-file payment of exactly the amount given, posted against the ledger line
    named, carrying that line's encounter number, dated today and received through the card on file. The
    account's balance owed goes down by the amount charged. The patient sees the card charge on the
    account ledger and on the card statement; the call succeeds when the receipt below is returned.

    Args:
        applies_to_txn_id: Id class — reference number of the deductible or coinsurance ledger line the
            card charge is posted against, as read from the account ledger lookup.
        billing_account_id: Id class — reference number of the patient's financial account, as read from
            the financial account lookup.
        charge_amount_usd: Fixed-format class — amount charged to the card on file, in USD, 2 decimal
            places, positive (format USD, 2 decimal places, positive); rounded to the nearest cent; never
            empty.

    Returns:
        A dictionary receipt: billing_txn_id (reference number of the new card-on-file payment entry),
        billing_account_id (the account charged), applies_to_txn_id (the ledger line the charge was posted
        against), encounter_number (encounter of that line, ENC- followed by 8 digits), amount (USD
        charged, 2 decimals), payment_method (always card_on_file), txn_date (posting date, YYYY-MM-DD)
        and patient_balance (the account's balance owed once the charge is posted, USD, 2 decimals). The
        presence of billing_txn_id means the charge was posted.
    """
    rows = ctx.find("billing_accounts", billing_account_id=billing_account_id)
    account = rows[0] if rows else {}
    found = ctx.find("billing_transactions", billing_txn_id=applies_to_txn_id)
    line = found[0] if found else {}
    amount = round(float(charge_amount_usd), 2)
    rid = ctx.make_id("btx_", billing_account_id, applies_to_txn_id, charge_amount_usd, "card_on_file")
    ctx.create("billing_transactions", rid, billing_txn_id=rid, billing_account_id=billing_account_id,
                customer_id=account.get("customer_id", ""), txn_date=ctx.now()[:10], service_date="",
                estimate_amount=0.0, statement_sequence=0, source_category="billing", signed_waiver_date="",
                line_category="none", adjustment_code="none",
                event_type="billing_payment_posted", amount=amount, applies_to_txn_id=applies_to_txn_id,
                encounter_number=line.get("encounter_number", ""), payment_method="card_on_file", channel="phone")
    balance = round(float(account.get("patient_balance") or 0) - amount, 2)
    ctx.update("billing_accounts", billing_account_id, patient_balance=balance)
    return str({"billing_txn_id": rid, "billing_account_id": billing_account_id,
                "applies_to_txn_id": applies_to_txn_id, "encounter_number": line.get("encounter_number", ""),
                "amount": amount, "payment_method": "card_on_file", "txn_date": ctx.now()[:10],
                "patient_balance": balance})


@tool(owner="agent", rw="write")
def issue_account_statement_de3ca581(ctx: ToolContext, billing_account_id: str, statement_amount_usd: float,
                                     statement_sequence: int) -> str:
    """Issue a patient statement on a Linden Ridge financial account for the statement balance given.

    One call records one statement entry on the account ledger, dated today, carrying the statement
    balance and its number in the account's current unpaid series, sent by the account's statement
    channel (paperless accounts receive it in the MyLinden portal, mail accounts by post), and records
    today as the account's most recent statement date. The balance owed does not change. The patient can
    see the statement in the portal or in the mail; the call succeeds when the receipt below is returned.

    Args:
        billing_account_id: Id class — reference number of the patient's financial account, as read from
            the financial account lookup.
        statement_amount_usd: Fixed-format class — statement balance printed on the statement, in USD, 2
            decimal places, positive (format USD, 2 decimal places, positive); rounded to the nearest cent.
        statement_sequence: Fixed-format class — number of this statement in the account's current unpaid
            series, an integer >= 0 (1 for the first statement of a series); no decimals.

    Returns:
        A dictionary receipt: billing_txn_id (reference number of the new statement entry),
        billing_account_id (the account statemented), amount (statement balance, USD, 2 decimals),
        statement_sequence (integer number in the unpaid series), channel (system for portal delivery,
        mail for postal delivery) and txn_date (statement date, YYYY-MM-DD, also recorded as the
        account's most recent statement date). The presence of billing_txn_id means the statement was
        issued.
    """
    rows = ctx.find("billing_accounts", billing_account_id=billing_account_id)
    account = rows[0] if rows else {}
    amount = round(float(statement_amount_usd), 2)
    sequence = int(statement_sequence)
    channel = "mail" if account.get("statement_delivery") == "mail" else "system"
    rid = ctx.make_id("btx_", billing_account_id, statement_amount_usd, statement_sequence, "statement")
    ctx.create("billing_transactions", rid, billing_txn_id=rid, billing_account_id=billing_account_id,
                customer_id=account.get("customer_id", ""), txn_date=ctx.now()[:10], service_date="",
                estimate_amount=0.0, source_category="billing", signed_waiver_date="", line_category="none",
                adjustment_code="none", event_type="billing_statement_issued", amount=amount,
                statement_sequence=sequence, channel=channel, encounter_number="", payment_method="none",
                applies_to_txn_id="")
    ctx.update("billing_accounts", billing_account_id, last_statement_date=ctx.now()[:10])
    return str({"billing_txn_id": rid, "billing_account_id": billing_account_id, "amount": amount,
                "statement_sequence": sequence, "channel": channel, "txn_date": ctx.now()[:10]})


@tool(owner="user", rw="write")
def pay_final_notice_balance_8381dcc2(ctx: ToolContext, billing_account_id: str, applies_to_txn_id: str,
                                      payment_amount_usd: float) -> str:
    """Pay, by the patient's own payment card on the secure phone payment line, an amount toward a
    financial account that is in its final-notice period, and return that account to active standing.

    One call records one card payment of exactly the amount given, posted against the ledger charge named
    and dated today; the account's balance owed goes down by the amount paid, its status becomes active and
    its final-notice date is cleared. The patient hears the confirmation on the line and sees the payment
    and the active status on the account; the call succeeds when the receipt below is returned.

    Args:
        applies_to_txn_id: Id class — reference number of the ledger charge the payment is posted against,
            as the agent reads it from the account ledger lookup and passes it to the patient.
        billing_account_id: Id class — reference number of the patient's financial account, as the agent
            reads it from the financial account lookup and passes it to the patient.
        payment_amount_usd: Fixed-format class — amount the patient pays by card, in USD, 2 decimal places,
            positive (format USD, 2 decimal places, positive); rounded to the nearest cent.

    Returns:
        A dictionary receipt: billing_txn_id (reference number of the new payment entry),
        billing_account_id (the account paid), applies_to_txn_id (the charge the payment was posted
        against), amount (USD paid, 2 decimals), payment_method (always card), status (the account status
        now recorded, active), txn_date (payment date, YYYY-MM-DD) and patient_balance (balance owed once
        the payment is posted, USD, 2 decimals). The presence of billing_txn_id means the payment was
        taken.
    """
    rows = ctx.find("billing_accounts", billing_account_id=billing_account_id)
    account = rows[0] if rows else {}
    found = ctx.find("billing_transactions", billing_txn_id=applies_to_txn_id)
    charge = found[0] if found else {}
    amount = round(float(payment_amount_usd), 2)
    rid = ctx.make_id("btx_", billing_account_id, applies_to_txn_id, payment_amount_usd, "final_notice_payment")
    ctx.create("billing_transactions", rid, billing_txn_id=rid, billing_account_id=billing_account_id,
                customer_id=account.get("customer_id", ""), txn_date=ctx.now()[:10], service_date="",
                estimate_amount=0.0, statement_sequence=0, source_category="billing", signed_waiver_date="",
                line_category="none", adjustment_code="none",
                event_type="billing_payment_posted", amount=amount, applies_to_txn_id=applies_to_txn_id,
                encounter_number=charge.get("encounter_number", ""), payment_method="card", channel="phone")
    balance = round(float(account.get("patient_balance") or 0) - amount, 2)
    ctx.update("billing_accounts", billing_account_id, patient_balance=balance, status="active",
               final_notice_date="")
    return str({"billing_txn_id": rid, "billing_account_id": billing_account_id,
                "applies_to_txn_id": applies_to_txn_id, "amount": amount, "payment_method": "card",
                "status": "active", "txn_date": ctx.now()[:10], "patient_balance": balance})
@tool(owner="agent", rw="write")
def issue_credit_refund_942b7f9f(ctx: ToolContext, billing_account_id: str, applies_to_txn_id: str,
                                 refund_amount_usd: float) -> str:
    """Refund part or all of a credit balance on a Linden Ridge financial account to the payer of the
    payment that created it.

    One call records one refund entry of exactly the amount given, linked to the payment named and dated
    today, issued to that payment's own method (a cash payment is refunded by check). The account's
    balance moves up by the amount refunded (a credit shrinks toward zero). The patient sees the refund on
    the ledger and, once processed, on the original card or bank account; the call succeeds when the
    receipt below is returned.

    Args:
        applies_to_txn_id: Id class — reference number of the payment entry whose overpayment created the
            credit, as read from the account ledger lookup.
        billing_account_id: Id class — reference number of the patient's financial account, as read from
            the financial account lookup.
        refund_amount_usd: Fixed-format class — amount refunded, in USD, 2 decimal places, positive (format
            USD, 2 decimal places, positive); rounded to the nearest cent.

    Returns:
        A dictionary receipt: billing_txn_id (reference number of the new refund entry), billing_account_id
        (the account refunded from), applies_to_txn_id (the payment whose credit is refunded), amount (USD
        refunded, 2 decimals), payment_method (method the refund is issued to), txn_date (refund date,
        YYYY-MM-DD) and patient_balance (the account balance once the refund is posted, USD, 2 decimals,
        negative while a credit remains). The presence of billing_txn_id means the refund was issued.
    """
    rows = ctx.find("billing_accounts", billing_account_id=billing_account_id)
    account = rows[0] if rows else {}
    found = ctx.find("billing_transactions", billing_txn_id=applies_to_txn_id)
    payment = found[0] if found else {}
    method = payment.get("payment_method") or "check"
    method = "check" if method == "cash" else method
    amount = round(float(refund_amount_usd), 2)
    rid = ctx.make_id("btx_", billing_account_id, applies_to_txn_id, refund_amount_usd, "refund")
    ctx.create("billing_transactions", rid, billing_txn_id=rid, billing_account_id=billing_account_id,
                customer_id=account.get("customer_id", ""), txn_date=ctx.now()[:10], service_date="",
                estimate_amount=0.0, statement_sequence=0, source_category="billing", signed_waiver_date="",
                line_category="none", adjustment_code="none",
                event_type="billing_refund_issued", amount=amount, applies_to_txn_id=applies_to_txn_id,
                encounter_number="", payment_method=method, channel="system")
    balance = round(float(account.get("patient_balance") or 0) + amount, 2)
    ctx.update("billing_accounts", billing_account_id, patient_balance=balance)
    return str({"billing_txn_id": rid, "billing_account_id": billing_account_id,
                "applies_to_txn_id": applies_to_txn_id, "amount": amount, "payment_method": method,
                "txn_date": ctx.now()[:10], "patient_balance": balance})


@tool(owner="user", rw="write")
def pay_returned_payment_replacement_5bda38e8(ctx: ToolContext, billing_account_id: str, applies_to_txn_id: str,
                                              replacement_amount_usd: float) -> str:
    """Pay, by the patient's own payment card on the secure phone payment line, a replacement for check or
    ACH payments the bank returned unpaid, and post it to the patient's financial account.

    One call records one card payment of exactly the amount given, posted against the ledger charge named
    (carrying that charge's encounter number) and dated today; the account's balance owed goes down by the
    amount paid. The patient hears the confirmation on the line and sees the replacement payment on the
    ledger; the call succeeds when the receipt below is returned.

    Args:
        applies_to_txn_id: Id class — reference number of the ledger charge whose check or ACH payment was
            returned, as the agent reads it from the account ledger lookup and passes it to the patient.
        billing_account_id: Id class — reference number of the patient's financial account, as the agent
            reads it from the financial account lookup and passes it to the patient.
        replacement_amount_usd: Fixed-format class — amount the patient pays by card, in USD, 2 decimal
            places, positive (format USD, 2 decimal places, positive); rounded to the nearest cent.

    Returns:
        A dictionary receipt: billing_txn_id (reference number of the new payment entry),
        billing_account_id (the account paid), applies_to_txn_id (the charge the payment was posted
        against), encounter_number (encounter of that charge, ENC- followed by 8 digits), amount (USD paid,
        2 decimals), payment_method (always card), txn_date (payment date, YYYY-MM-DD) and patient_balance
        (balance owed once the payment is posted, USD, 2 decimals, negative when a credit remains). The
        presence of billing_txn_id means the payment was taken.
    """
    rows = ctx.find("billing_accounts", billing_account_id=billing_account_id)
    account = rows[0] if rows else {}
    found = ctx.find("billing_transactions", billing_txn_id=applies_to_txn_id)
    charge = found[0] if found else {}
    amount = round(float(replacement_amount_usd), 2)
    rid = ctx.make_id("btx_", billing_account_id, applies_to_txn_id, replacement_amount_usd, "replacement")
    ctx.create("billing_transactions", rid, billing_txn_id=rid, billing_account_id=billing_account_id,
                customer_id=account.get("customer_id", ""), txn_date=ctx.now()[:10], service_date="",
                estimate_amount=0.0, statement_sequence=0, source_category="billing", signed_waiver_date="",
                line_category="none", adjustment_code="none",
                event_type="billing_payment_posted", amount=amount, applies_to_txn_id=applies_to_txn_id,
                encounter_number=charge.get("encounter_number", ""), payment_method="card", channel="phone")
    balance = round(float(account.get("patient_balance") or 0) - amount, 2)
    ctx.update("billing_accounts", billing_account_id, patient_balance=balance)
    return str({"billing_txn_id": rid, "billing_account_id": billing_account_id,
                "applies_to_txn_id": applies_to_txn_id, "encounter_number": charge.get("encounter_number", ""),
                "amount": amount, "payment_method": "card", "txn_date": ctx.now()[:10],
                "patient_balance": balance})

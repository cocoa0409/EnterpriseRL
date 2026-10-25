"""Hidden task tools for d1_credit_account_billing_and_credits (Commercial Credit Account).

Each tool performs one atomic write on the customer's Commercial Credit Account records and is reached
only through the unlock/call meta tools. No tool checks eligibility, status, timing or any policy
prerequisite; every such judgement is the agent's, from the knowledge base and the records.
"""

from erlbench import ToolContext, tool


@tool(owner="agent", rw="write")
def book_cash_discount_2280b564(ctx: ToolContext, credit_account_id: str, applied_invoice_number: str,
                                payment_reference: str, payment_date: str, discount_amount: float) -> str:
    """Book a prompt-payment cash discount line on one invoice of a Commercial Credit Account, credited to the customer for a payment that earned it.

    One call records one discount line against the named invoice: the line carries the discount amount,
    the invoice it is applied to, the reference of the payment that earned it and that payment's
    received date, and the account's open receivable balance is reduced by the discount amount. The
    customer sees the discount as a credit on the invoice and a lower balance owed. The returned receipt
    carries the discount line reference and the account's new receivable balance.

    Args:
        credit_account_id: Id class — the reference number of the customer's Commercial Credit Account the discount is booked on, read from the credit account lookup.
        applied_invoice_number: Verbatim class — the invoice number the discount is applied to, copied exactly as it appears on that invoice in the account's receivable history, keeping its prefix, digits and punctuation unchanged (verbatim).
        payment_reference: Verbatim class — the reference of the customer payment that earned the discount, copied exactly as it appears on that payment in the account's receivable history, keeping every character unchanged (verbatim).
        payment_date: Fixed-format class — the date the earning payment was received, as recorded on that payment, written YYYY-MM-DD (calendar date, no time part).
        discount_amount: Fixed-format class — the cash discount credited on the invoice, in USD, 2 decimal places, positive, rounded half up to the cent.

    Returns:
        A text rendering of a dictionary with these fields: status — the word booked when the discount line is recorded; discount_reference — the reference of the new discount line (text, prefix CD-); applied_invoice_number — the invoice the discount is applied to; discount_amount — the amount credited in USD with 2 decimal places; ar_balance — the account's open receivable balance with the discount credited, in USD with 2 decimal places (negative means a credit balance).
    """
    amount = round(float(discount_amount), 2)
    rid = ctx.make_id("ctx_", credit_account_id, applied_invoice_number, payment_reference, payment_date, amount)
    ref = "CD-1" + str(int(rid[-10:], 16))[-7:].rjust(7, "0")
    acct = ctx.find("credit_accounts", credit_account_id=credit_account_id)
    cust = acct[0].get("customer_id") if acct else ""
    ctx.create("credit_transactions", rid, credit_txn_id=rid, credit_account_id=credit_account_id,
               customer_id=cust, event_type="credit_cash_discount_taken", document_number=ref,
               txn_date=payment_date, due_date="", amount=amount, merchandise_amount=0.0,
               freight_amount=0.0, tax_amount=0.0, source_type="customer_payment",
               source_reference=payment_reference, applied_invoice_number=applied_invoice_number,
               payment_method="none", charge_type="none", billing_period="")
    balance = round(float(acct[0].get("ar_balance") or 0) - amount, 2) if acct else 0.0
    ctx.update("credit_accounts", credit_account_id, ar_balance=balance)
    return str({"status": "booked", "discount_reference": ref, "applied_invoice_number": applied_invoice_number,
                "discount_amount": amount, "ar_balance": balance})


@tool(owner="user", rw="write")
def pay_by_bank_debit_4d9f44ce(ctx: ToolContext, credit_account_id: str, payment_amount: float) -> str:
    """The customer authorizes a one-time bank debit payment to its Commercial Credit Account, received on account without remittance detail.

    One call records one payment received today by ACH debit from the customer's bank account for the
    amount the customer authorizes; the payment is held on account, unapplied to any invoice, and the
    account's open receivable balance is reduced by the payment amount immediately. The customer sees the
    payment on the account with its own payment reference and a lower balance owed. The returned
    receipt carries that payment reference and the account's new receivable balance.

    Args:
        credit_account_id: Id class — the reference number of the customer's own Commercial Credit Account the payment is made to, as given by the representative from the credit account lookup.
        payment_amount: Fixed-format class — the amount the customer authorizes to be debited, in USD, 2 decimal places, positive, rounded half up to the cent.

    Returns:
        A text rendering of a dictionary with these fields: status — the word received when the payment is recorded; payment_reference — the reference of the bank debit payment (text, prefix ACH-); payment_amount — the amount received in USD with 2 decimal places; received_date — the date the payment is received, YYYY-MM-DD; ar_balance — the account's open receivable balance with the payment received, in USD with 2 decimal places (negative means a credit balance).
    """
    amount = round(float(payment_amount), 2)
    rid = ctx.make_id("ctx_", credit_account_id, amount)
    ref = "ACH-1" + str(int(rid[-10:], 16))[-7:].rjust(7, "0")
    today = ctx.now()[:10]
    acct = ctx.find("credit_accounts", credit_account_id=credit_account_id)
    cust = acct[0].get("customer_id") if acct else ""
    ctx.create("credit_transactions", rid, credit_txn_id=rid, credit_account_id=credit_account_id,
               customer_id=cust, event_type="credit_payment_received", document_number=ref,
               txn_date=today, due_date="", amount=amount, merchandise_amount=0.0,
               freight_amount=0.0, tax_amount=0.0, source_type="customer_payment", source_reference="",
               applied_invoice_number="ON-ACCOUNT", payment_method="ach_debit", charge_type="none",
               billing_period="")
    balance = round(float(acct[0].get("ar_balance") or 0) - amount, 2) if acct else 0.0
    ctx.update("credit_accounts", credit_account_id, ar_balance=balance)
    return str({"status": "received", "payment_reference": ref, "payment_amount": amount,
                "received_date": today, "ar_balance": balance})


@tool(owner="user", rw="write")
def submit_limit_request_dcbbb504(ctx: ToolContext, credit_account_id: str, change_type: str,
                                  requested_limit: float) -> str:
    """The customer submits its own credit limit increase request on its Commercial Credit Account, naming the credit limit it asks for.

    One call records one limit request dated today on the account, carrying the limit asked for and
    whether the increase sought is permanent or temporary; the request is recorded with its decision marked pending
    and changes nothing on the account itself. The customer sees a new pending request with
    its own review reference. The returned receipt carries that review reference and the request date.

    Args:
        credit_account_id: Id class — the reference number of the customer's own Commercial Credit Account the request is made on, as given by the representative from the credit account lookup.
        change_type: Enum class — the kind of increase asked for: permanent — a lasting change of the account's credit limit; temporary — a limited-time increase for a shutdown, turnaround or seasonal build.
        requested_limit: Fixed-format class — the total credit limit the customer asks for (not the increase alone), in USD, 2 decimal places, rounded half up to the cent.

    Returns:
        A text rendering of a dictionary with these fields: status — the word pending when the request is recorded; review_reference — the reference of the new limit request (text, prefix CLR-); request_date — the date of the request, YYYY-MM-DD; change_type — the kind of increase asked for; requested_limit — the credit limit asked for in USD with 2 decimal places.
    """
    limit = round(float(requested_limit), 2)
    rid = ctx.make_id("clr_", credit_account_id, change_type, limit)
    ref = "CLR-1" + str(int(rid[-10:], 16))[-6:].rjust(6, "0")
    today = ctx.now()[:10]
    acct = ctx.find("credit_accounts", credit_account_id=credit_account_id)
    cust = acct[0].get("customer_id") if acct else ""
    ctx.create("credit_limit_reviews", rid, credit_review_id=rid, credit_account_id=credit_account_id,
               customer_id=cust, event_type="credit_limit_review_requested", review_reference=ref,
               request_date=today, requested_limit=limit, change_type=change_type, decision="pending",
               approved_limit=0.0, expiry_date="")
    return str({"status": "pending", "review_reference": ref, "request_date": today,
                "change_type": change_type, "requested_limit": limit})


@tool(owner="agent", rw="write")
def decide_limit_request_85fdd39c(ctx: ToolContext, credit_account_id: str, review_reference: str,
                                  decision: str, approved_limit: float) -> str:
    """Record Corbett's decision on a permanent credit limit request of a Commercial Credit Account and, when approved, apply the new limit.

    One call records one decision dated today on the named request, carrying the outcome and the limit
    granted; the requested limit and the kind of increase are carried over from that request. When the
    outcome is approved or approved_reduced the account's credit limit becomes the limit granted and the
    decision date becomes the account's last credit review date; a declined or referred outcome leaves
    the account unchanged. The customer sees the decision on the request and, when approved, the new
    credit limit. The returned receipt carries the outcome, the limit granted and the account's limit.

    Args:
        credit_account_id: Id class — the reference number of the Commercial Credit Account the request belongs to, read from the credit account lookup.
        review_reference: Verbatim class — the review reference of the request being decided, copied exactly as it appears on that request in the account's limit review history or in the request receipt (verbatim).
        decision: Enum class — the outcome: approved — the limit asked for is granted in full; approved_reduced — a lower limit than asked for is granted because a cap applies; declined — no increase is granted; referred_to_committee — the increase exceeds the desk's approval authority and goes to the credit committee with no change now; pending — not used for a decision and never passed.
        approved_limit: Fixed-format class — the total credit limit granted, in USD, 2 decimal places, rounded half up to the cent; 0.00 when declined or referred.

    Returns:
        A text rendering of a dictionary with these fields: status — the word decided when the decision is recorded; review_reference — the request decided; decision — the outcome recorded; approved_limit — the limit granted in USD with 2 decimal places; credit_limit — the account's credit limit with the decision applied, in USD with 2 decimal places.
    """
    limit = round(float(approved_limit), 2)
    req = ctx.find("credit_limit_reviews", review_reference=review_reference,
                   event_type="credit_limit_review_requested")
    requested = req[0].get("requested_limit") if req else 0.0
    kind = req[0].get("change_type") if req else "permanent"
    rid = ctx.make_id("cld_", credit_account_id, review_reference, decision, limit)
    acct = ctx.find("credit_accounts", credit_account_id=credit_account_id)
    cust = acct[0].get("customer_id") if acct else ""
    today = ctx.now()[:10]
    ctx.create("credit_limit_reviews", rid, credit_review_id=rid, credit_account_id=credit_account_id,
               customer_id=cust, event_type="credit_limit_review_decided", review_reference=review_reference,
               request_date=today, requested_limit=requested, change_type=kind, decision=decision,
               approved_limit=limit, expiry_date="")
    current = acct[0].get("credit_limit") if acct else 0.0
    if decision in ("approved", "approved_reduced"):
        ctx.update("credit_accounts", credit_account_id, credit_limit=limit, last_review_date=today)
        current = limit
    return str({"status": "decided", "review_reference": review_reference, "decision": decision,
                "approved_limit": limit, "credit_limit": current})

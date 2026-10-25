"""Hidden task tools of the premium_billing_and_grace difficulty (Cascade Mutual Dental & Vision).

Each tool lands one atomic write on a premium billing account; the values it books are the ones
the agent has already worked out from the billing rules. No tool checks eligibility, status or
any prerequisite, and none computes an amount on the agent's behalf.
"""

from erlbench import ToolContext, tool


@tool(owner="agent", rw="write")
def book_vision_term_credit_956578a0(ctx: ToolContext, billing_account_id: str, coverage_month: str,
                                     months_covered: int, credit_amount: float) -> str:
    """Book a vision-line termination credit on a premium billing account: Cascade gives back vision
    premium that was billed for a vision plan unit whose coverage has ended. One call records one
    premium credit on the account's billing ledger, marked as a termination credit for the vision
    product line, dated today, carrying the coverage month of the invoice it is posted against, the number of coverage
    months it covers and the credit amount, and lowers the account's current balance by that amount.
    The account holder sees the credit on the billing ledger and a lower balance due. The call is
    complete when the receipt below comes back with the credit's ledger reference.

    Args:
        billing_account_id: Id class — the reference number of the premium billing account the credit is booked to, as returned by the billing-account lookup for the customer.
        coverage_month: Fixed-format class — the coverage month of the invoice the credit is posted against, written YYYY-MM (four-digit year, hyphen, two-digit month), no day part.
        months_covered: Fixed-format class — the number of coverage months the credit gives back, an integer number of months (whole number, no fraction).
        credit_amount: Fixed-format class — the amount credited back, in USD, a positive number with 2 decimal places; a value given with more places is rounded half up to the cent when booked.

    Returns:
        A dictionary rendered as text with these fields: billing_txn_id (text, the ledger reference of the new credit), billing_account_id (text, the account credited), product_line (text, always vision), credit_reason (text, always termination_unearned), coverage_month (text, YYYY-MM, the coverage month of the invoice the credit is posted against), months_covered (integer, the coverage months credited), amount (number, USD with 2 decimal places, the amount credited), txn_date (text, YYYY-MM-DD, the booking date) and balance_due (number, USD with 2 decimal places, the account's balance with the credit booked; negative means a credit balance). A receipt carrying billing_txn_id means the credit is on the ledger.
    """
    amount = round(float(credit_amount), 2)
    months = int(months_covered)
    accounts = ctx.find("billing_accounts", billing_account_id=billing_account_id)
    customer_id = accounts[0].get("customer_id", "") if accounts else ""
    rid = ctx.make_id("btx_", billing_account_id, coverage_month, months, amount)
    today = ctx.now()[:10]
    ctx.create("billing_transactions", rid, billing_txn_id=rid, billing_account_id=billing_account_id,
               customer_id=customer_id, event_type="billing_premium_credit", invoice_number="",
               coverage_month=coverage_month, months_covered=months, product_line="vision",
               amount=amount, txn_date=today, payment_method="not_applicable",
               payment_purpose="not_applicable", payment_reference="",
               credit_reason="termination_unearned", original_billing_txn_id=None)
    balance = None
    if accounts:
        balance = round(float(accounts[0].get("balance_due") or 0) - amount, 2)
        ctx.update("billing_accounts", billing_account_id, balance_due=balance)
    return str({"billing_txn_id": rid, "billing_account_id": billing_account_id, "product_line": "vision",
                "credit_reason": "termination_unearned", "coverage_month": coverage_month,
                "months_covered": months, "amount": amount, "txn_date": today, "balance_due": balance})


@tool(owner="user", rw="write")
def submit_grace_cure_payment_5521c4c8(ctx: ToolContext, billing_account_id: str, payment_amount: float) -> str:
    """Pay premium by card on your own premium billing account to bring it out of its grace period:
    the account holder authorizes a one-time card charge for the stated amount. One call records one
    payment received on the account's billing ledger, by card, taken as a grace-cure payment and dated
    today, and lowers the account's current balance by the amount paid. The holder receives a card
    confirmation number for the charge and sees the payment and the lower balance on the account. The
    call is complete when the receipt below comes back with the confirmation number.

    Args:
        billing_account_id: Id class — the reference number of your premium billing account, as the representative reads it to you from the billing-account lookup.
        payment_amount: Fixed-format class — the amount you authorize to be charged to your card, in USD, a positive number with 2 decimal places; a value given with more places is rounded half up to the cent when charged.

    Returns:
        A dictionary rendered as text with these fields: billing_txn_id (text, the ledger reference of the payment), payment_reference (text, the card confirmation number of the charge), amount (number, USD with 2 decimal places, the amount charged), payment_method (text, always card), payment_purpose (text, always grace_cure), txn_date (text, YYYY-MM-DD, the payment date) and balance_due (number, USD with 2 decimal places, the account's balance with the payment booked; negative means a credit balance). A receipt carrying payment_reference means the card charge is booked on the account.
    """
    amount = round(float(payment_amount), 2)
    accounts = ctx.find("billing_accounts", billing_account_id=billing_account_id)
    customer_id = accounts[0].get("customer_id", "") if accounts else ""
    rid = ctx.make_id("btx_", billing_account_id, "card", amount)
    reference = ctx.make_id("CNF74", billing_account_id, amount, length=8).upper()
    today = ctx.now()[:10]
    ctx.create("billing_transactions", rid, billing_txn_id=rid, billing_account_id=billing_account_id,
               customer_id=customer_id, event_type="billing_payment_received", invoice_number="",
               coverage_month="", months_covered=0, product_line="combined", amount=amount,
               txn_date=today, payment_method="card", payment_purpose="grace_cure",
               payment_reference=reference, credit_reason="not_applicable", original_billing_txn_id=None)
    balance = None
    if accounts:
        balance = round(float(accounts[0].get("balance_due") or 0) - amount, 2)
        ctx.update("billing_accounts", billing_account_id, balance_due=balance)
    return str({"billing_txn_id": rid, "payment_reference": reference, "amount": amount,
                "payment_method": "card", "payment_purpose": "grace_cure", "txn_date": today,
                "balance_due": balance})


@tool(owner="agent", rw="write")
def book_dental_tier_credit_2a6e4a9b(ctx: ToolContext, billing_account_id: str, coverage_month: str,
                                     months_covered: int, credit_amount: float) -> str:
    """Book a dental-line plan-change difference credit on a premium billing account: Cascade gives back
    the part of the dental premium that was billed at a coverage tier the household no longer has. One
    call records one premium credit on the account's billing ledger, marked as a plan-change difference
    credit for the dental product line, dated today, carrying the coverage month of the invoice it is posted against, the
    number of coverage months it covers and the credit amount, and lowers the account's current balance
    by that amount. The account holder sees the credit on the billing ledger and a lower balance due. The
    call is complete when the receipt below comes back with the credit's ledger reference.

    Args:
        billing_account_id: Id class — the reference number of the premium billing account the credit is booked to, as returned by the billing-account lookup for the customer.
        coverage_month: Fixed-format class — the coverage month of the invoice the credit is posted against, written YYYY-MM (four-digit year, hyphen, two-digit month), no day part.
        months_covered: Fixed-format class — the number of coverage months the credit gives back, an integer number of months (whole number, no fraction).
        credit_amount: Fixed-format class — the amount credited back, in USD, a positive number with 2 decimal places; a value given with more places is rounded half up to the cent when booked.

    Returns:
        A dictionary rendered as text with these fields: billing_txn_id (text, the ledger reference of the new credit), billing_account_id (text, the account credited), product_line (text, always dental_ppo), credit_reason (text, always plan_change_difference), coverage_month (text, YYYY-MM, the coverage month of the invoice the credit is posted against), months_covered (integer, the coverage months credited), amount (number, USD with 2 decimal places, the amount credited), txn_date (text, YYYY-MM-DD, the booking date) and balance_due (number, USD with 2 decimal places, the account's balance with the credit booked; negative means a credit balance). A receipt carrying billing_txn_id means the credit is on the ledger.
    """
    amount = round(float(credit_amount), 2)
    months = int(months_covered)
    accounts = ctx.find("billing_accounts", billing_account_id=billing_account_id)
    customer_id = accounts[0].get("customer_id", "") if accounts else ""
    rid = ctx.make_id("btx_", billing_account_id, "dental_ppo", coverage_month, months, amount)
    today = ctx.now()[:10]
    ctx.create("billing_transactions", rid, billing_txn_id=rid, billing_account_id=billing_account_id,
               customer_id=customer_id, event_type="billing_premium_credit", invoice_number="",
               coverage_month=coverage_month, months_covered=months, product_line="dental_ppo",
               amount=amount, txn_date=today, payment_method="not_applicable",
               payment_purpose="not_applicable", payment_reference="",
               credit_reason="plan_change_difference", original_billing_txn_id=None)
    balance = None
    if accounts:
        balance = round(float(accounts[0].get("balance_due") or 0) - amount, 2)
        ctx.update("billing_accounts", billing_account_id, balance_due=balance)
    return str({"billing_txn_id": rid, "billing_account_id": billing_account_id, "product_line": "dental_ppo",
                "credit_reason": "plan_change_difference", "coverage_month": coverage_month,
                "months_covered": months, "amount": amount, "txn_date": today, "balance_due": balance})


@tool(owner="agent", rw="write")
def book_rider_end_credit_fb22198c(ctx: ToolContext, billing_account_id: str, coverage_month: str,
                                   months_covered: int, credit_amount: float) -> str:
    """Book an orthodontic-rider termination credit on a premium billing account: Cascade gives back
    rider premium billed for months in which the household's orthodontic rider no longer covered anyone.
    One call records one premium credit on the account's billing ledger, marked as a termination credit
    for the orthodontic rider product line, dated today, carrying the coverage month of the invoice it is posted against, the
    number of coverage months it covers and the credit amount, and lowers the account's current balance
    by that amount. The account holder sees the credit on the billing ledger and a lower balance due. The
    call is complete when the receipt below comes back with the credit's ledger reference.

    Args:
        billing_account_id: Id class — the reference number of the premium billing account the credit is booked to, as returned by the billing-account lookup for the customer.
        coverage_month: Fixed-format class — the coverage month of the invoice the credit is posted against, written YYYY-MM (four-digit year, hyphen, two-digit month), no day part.
        months_covered: Fixed-format class — the number of coverage months the credit gives back, an integer number of months (whole number, no fraction).
        credit_amount: Fixed-format class — the amount credited back, in USD, a positive number with 2 decimal places; a value given with more places is rounded half up to the cent when booked.

    Returns:
        A dictionary rendered as text with these fields: billing_txn_id (text, the ledger reference of the new credit), billing_account_id (text, the account credited), product_line (text, always ortho_rider), credit_reason (text, always termination_unearned), coverage_month (text, YYYY-MM, the coverage month of the invoice the credit is posted against), months_covered (integer, the coverage months credited), amount (number, USD with 2 decimal places, the amount credited), txn_date (text, YYYY-MM-DD, the booking date) and balance_due (number, USD with 2 decimal places, the account's balance with the credit booked; negative means a credit balance). A receipt carrying billing_txn_id means the credit is on the ledger.
    """
    amount = round(float(credit_amount), 2)
    months = int(months_covered)
    accounts = ctx.find("billing_accounts", billing_account_id=billing_account_id)
    customer_id = accounts[0].get("customer_id", "") if accounts else ""
    rid = ctx.make_id("btx_", billing_account_id, "ortho_rider", coverage_month, months, amount)
    today = ctx.now()[:10]
    ctx.create("billing_transactions", rid, billing_txn_id=rid, billing_account_id=billing_account_id,
               customer_id=customer_id, event_type="billing_premium_credit", invoice_number="",
               coverage_month=coverage_month, months_covered=months, product_line="ortho_rider",
               amount=amount, txn_date=today, payment_method="not_applicable",
               payment_purpose="not_applicable", payment_reference="",
               credit_reason="termination_unearned", original_billing_txn_id=None)
    balance = None
    if accounts:
        balance = round(float(accounts[0].get("balance_due") or 0) - amount, 2)
        ctx.update("billing_accounts", billing_account_id, balance_due=balance)
    return str({"billing_txn_id": rid, "billing_account_id": billing_account_id, "product_line": "ortho_rider",
                "credit_reason": "termination_unearned", "coverage_month": coverage_month,
                "months_covered": months, "amount": amount, "txn_date": today, "balance_due": balance})


@tool(owner="user", rw="write")
def submit_renewal_payment_53926ce3(ctx: ToolContext, billing_account_id: str, payment_amount: float) -> str:
    """Pay the coming prepaid year on your own premium billing account by card: the account holder
    authorizes a one-time card charge for the stated amount toward next year's premium. One call records
    one payment received on the account's billing ledger, by card, taken as a regular premium payment and
    dated today, and lowers the account's current balance by the amount paid. The holder receives a card
    confirmation number for the charge and sees the payment and the lower balance on the account. The call
    is complete when the receipt below comes back with the confirmation number.

    Args:
        billing_account_id: Id class — the reference number of your premium billing account, as the representative reads it to you from the billing-account lookup.
        payment_amount: Fixed-format class — the amount you authorize to be charged to your card, in USD, a positive number with 2 decimal places; a value given with more places is rounded half up to the cent when charged.

    Returns:
        A dictionary rendered as text with these fields: billing_txn_id (text, the ledger reference of the payment), payment_reference (text, the card confirmation number of the charge), amount (number, USD with 2 decimal places, the amount charged), payment_method (text, always card), payment_purpose (text, always regular), txn_date (text, YYYY-MM-DD, the payment date) and balance_due (number, USD with 2 decimal places, the account's balance with the payment booked; negative means a credit balance). A receipt carrying payment_reference means the card charge is booked on the account.
    """
    amount = round(float(payment_amount), 2)
    accounts = ctx.find("billing_accounts", billing_account_id=billing_account_id)
    customer_id = accounts[0].get("customer_id", "") if accounts else ""
    rid = ctx.make_id("btx_", billing_account_id, "renewal_card", amount)
    reference = ctx.make_id("CNF74", billing_account_id, "renewal", amount, length=8).upper()
    today = ctx.now()[:10]
    ctx.create("billing_transactions", rid, billing_txn_id=rid, billing_account_id=billing_account_id,
               customer_id=customer_id, event_type="billing_payment_received", invoice_number="",
               coverage_month="", months_covered=0, product_line="combined", amount=amount,
               txn_date=today, payment_method="card", payment_purpose="regular",
               payment_reference=reference, credit_reason="not_applicable", original_billing_txn_id=None)
    balance = None
    if accounts:
        balance = round(float(accounts[0].get("balance_due") or 0) - amount, 2)
        ctx.update("billing_accounts", billing_account_id, balance_due=balance)
    return str({"billing_txn_id": rid, "payment_reference": reference, "amount": amount,
                "payment_method": "card", "payment_purpose": "regular", "txn_date": today,
                "balance_due": balance})

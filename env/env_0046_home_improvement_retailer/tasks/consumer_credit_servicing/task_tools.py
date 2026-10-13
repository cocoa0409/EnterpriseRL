"""Hidden task tools for the consumer_credit_servicing difficulty of env_0046_home_improvement_retailer
(Ridgeline Consumer Credit). Each tool performs one atomic write on a consumer credit account and is
reached only through unlock_* -> call_*; its name is published only as an extended policy's target_tool.
No tool judges eligibility, aggregates history or computes an amount: every value is passed in as
decided by the caller.
"""

from erlbench import ToolContext, tool


@tool(owner="agent", rw="write")
def post_refund_return_credit_59e816eb(ctx: ToolContext, card_account_id: str, original_transaction_id: str,
                                       merchant_reference: str, plan_code: str, amount: float) -> str:
    """Post one return credit to a Ridgeline Consumer Credit account for a refund that a Ridgeline selling
    program (special orders, installations, tool rental or orders) issued back to that account. The call
    adds one credit line to the account ledger, dated today and placed in today's statement period, that
    references the original purchase it credits, carries that purchase's financing plan and the order,
    contract or agreement number of the refund, and lowers the amount the cardholder owes by the credited
    amount. The cardholder sees the credit on the account right away and on the next statement.

    Args:
        card_account_id: Id class — the reference number of the consumer credit account (card or project loan) that paid for the original purchase, as returned by the account lookup for the verified customer.
        original_transaction_id: Id class — the reference number of the purchase line on that account that the refund credits, as returned by the account ledger lookup.
        merchant_reference: Verbatim class — the order, contract or agreement number of the refunded purchase exactly as it appears on the selling program's record of the refund and on the purchase line; copy it character for character, preserving letters, digits and hyphens, with no reformatting, addition or deletion (verbatim).
        plan_code: Enum class — the financing plan of the purchase being credited, exactly one of: revolving_standard for a purchase on the card's standard revolving balance; deferred_6 for a purchase on 6-month deferred-interest financing; deferred_12 for a purchase on 12-month deferred-interest financing; deferred_24 for a purchase on 24-month deferred-interest financing; fixed_apr_84 for a purchase on 84 fixed monthly payments at the reduced APR; loan_draw for a draw on a project loan; not_applicable only for a line that is tied to no purchase plan, which never applies to a return credit.
        amount: Fixed-format class — the credit amount in USD, a positive number with 2 decimal places, already rounded to the nearest cent; it is booked exactly as given.

    Returns:
        A text rendering of a dictionary with these fields: status — the word posted when the credit line was written; card_transaction_id — the reference number of the new credit line; card_account_id — the account credited; amount — the credited amount in USD with 2 decimal places; plan_code — the financing plan recorded on the credit; transaction_date — the posting date of the credit, YYYY-MM-DD; current_balance — the amount owed on the account once the credit is booked, USD with 2 decimal places (negative means a credit balance).
    """
    amt = round(float(amount), 2)
    found = ctx.find("card_accounts", card_account_id=card_account_id)
    acct = found[0] if found else {}
    today = ctx.now()[:10]
    rid = ctx.make_id("ctx_", card_account_id, original_transaction_id, merchant_reference, plan_code, amt)
    ctx.create("card_transactions", rid, card_transaction_id=rid, card_account_id=card_account_id,
               customer_id=acct.get("customer_id", ""), event_type="card_return_credit_posted",
               transaction_date=today, amount=amt, statement_period=today[:7], plan_code=plan_code,
               promo_end_date="", merchant_reference=merchant_reference, purchase_channel="not_applicable",
               payment_channel="not_applicable", funding_account_last4="", excess_allocation="not_applicable",
               original_transaction_id=original_transaction_id, return_reason="not_applicable",
               fee_type="not_applicable", interest_type="not_applicable", reversal_reason="not_applicable",
               card_request_id=None, statement_date="", due_date="", statement_balance=0.0,
               minimum_payment_due=0.0, past_due_amount=0.0, days_past_due=0)
    new_balance = round(float(acct.get("current_balance") or 0) - amt, 2)
    ctx.update("card_accounts", card_account_id, current_balance=new_balance)
    return str({"status": "posted", "card_transaction_id": rid, "card_account_id": card_account_id,
                "amount": amt, "plan_code": plan_code, "transaction_date": today,
                "current_balance": new_balance})


@tool(owner="user", rw="write")
def set_autopay_payoff_plan_7f80aff1(ctx: ToolContext, card_account_id: str, autopay_fixed_amount: float) -> str:
    """The cardholder personally instructs automatic payments on their own Ridgeline Consumer Credit card at
    a fixed draft amount. The call finds the card by the account number digits the cardholder holds, turns
    autopay on for it with the fixed-amount option and records the fixed draft amount, replacing any autopay
    choice on file; each automatic draft on a payment due date takes the greater of that fixed amount and the
    minimum payment due. The cardholder can see the new autopay setting and its amount on the account
    straight away; when no card carries the digits given, nothing is changed and the receipt says so.

    Args:
        card_account_id: Id class — the identifying number of the cardholder's own card account as the cardholder holds it: the last four digits of the account number printed on the card (4 digits, e.g. 0000), as the cardholder states it.
        autopay_fixed_amount: Fixed-format class — the fixed draft amount in USD, a positive number with 2 decimal places, already rounded to the nearest cent; it is recorded exactly as given.

    Returns:
        A text rendering of a dictionary with these fields: status — enrolled when the instruction was recorded, or not_found when no card carries those digits; card_account_id — the last four digits given; autopay_enrolled — True once autopay is on; autopay_option — fixed_amount; autopay_fixed_amount — the recorded draft amount in USD with 2 decimal places.
    """
    amt = round(float(autopay_fixed_amount), 2)
    rows = ctx.find("card_accounts", account_last4=card_account_id)
    if not rows:
        return str({"status": "not_found", "card_account_id": card_account_id, "autopay_enrolled": False,
                    "autopay_option": "none", "autopay_fixed_amount": amt})
    ctx.update("card_accounts", rows[0]["card_account_id"], autopay_enrolled=True, autopay_option="fixed_amount",
               autopay_fixed_amount=amt)
    return str({"status": "enrolled", "card_account_id": card_account_id, "autopay_enrolled": True,
                "autopay_option": "fixed_amount", "autopay_fixed_amount": amt})


@tool(owner="agent", rw="write")
def post_missed_payment_late_fee_0b17ca39(ctx: ToolContext, card_account_id: str, original_transaction_id: str,
                                          statement_period: str, amount: float) -> str:
    """Post the late fee owed on a Ridgeline Consumer Credit account for a statement whose minimum payment
    was not covered by its due date. The call adds one late-fee line to the account ledger, dated today,
    that references the statement it arises from and carries that statement's period, and raises the
    amount the cardholder owes by the fee. The cardholder sees the fee on the account right away and on the
    next statement.

    Args:
        card_account_id: Id class — the reference number of the consumer credit account the fee is charged to, as returned by the account lookup for the verified customer.
        original_transaction_id: Id class — the reference number of the statement line whose minimum went unpaid, as returned by the account ledger lookup.
        statement_period: Fixed-format class — the statement period of that statement, written YYYY-MM exactly as it appears on the statement line.
        amount: Fixed-format class — the fee amount in USD, a positive number with 2 decimal places, already rounded to the cent; it is booked exactly as given.

    Returns:
        A text rendering of a dictionary with these fields: status — the word posted when the fee line was written; card_transaction_id — the reference number of the new fee line; card_account_id — the account charged; fee_type — late_fee; statement_period — the period recorded, YYYY-MM; amount — the fee in USD with 2 decimal places; transaction_date — the posting date, YYYY-MM-DD; current_balance — the amount owed on the account once the fee is booked, USD with 2 decimal places.
    """
    amt = round(float(amount), 2)
    found = ctx.find("card_accounts", card_account_id=card_account_id)
    acct = found[0] if found else {}
    today = ctx.now()[:10]
    rid = ctx.make_id("ctx_", card_account_id, original_transaction_id, statement_period, amt)
    ctx.create("card_transactions", rid, card_transaction_id=rid, card_account_id=card_account_id,
               customer_id=acct.get("customer_id", ""), event_type="card_fee_assessed",
               transaction_date=today, amount=amt, statement_period=statement_period, plan_code="not_applicable",
               promo_end_date="", merchant_reference="", purchase_channel="not_applicable",
               payment_channel="not_applicable", funding_account_last4="", excess_allocation="not_applicable",
               original_transaction_id=original_transaction_id, return_reason="not_applicable",
               fee_type="late_fee", interest_type="not_applicable", reversal_reason="not_applicable",
               card_request_id=None, statement_date="", due_date="", statement_balance=0.0,
               minimum_payment_due=0.0, past_due_amount=0.0, days_past_due=0)
    new_balance = round(float(acct.get("current_balance") or 0) + amt, 2)
    ctx.update("card_accounts", card_account_id, current_balance=new_balance)
    return str({"status": "posted", "card_transaction_id": rid, "card_account_id": card_account_id,
                "fee_type": "late_fee", "statement_period": statement_period, "amount": amt,
                "transaction_date": today, "current_balance": new_balance})


@tool(owner="user", rw="write")
def authorize_phone_payment_1fdda3b1(ctx: ToolContext, card_account_id: str, funding_account_last4: str,
                                     excess_allocation: str, amount: float) -> str:
    """The cardholder personally authorizes a one-time payment to their own Ridgeline Consumer Credit card,
    drawn from the bank account they name, taken over the phone with a representative. The call finds the
    card by the account number digits the cardholder holds, credits one payment line dated today with the
    phone-representative channel, the bank account digits and the allocation basis for the part above the
    minimum, and lowers the amount owed by the payment. The cardholder sees the payment on the account right
    away; when no card carries the digits given, nothing is posted and the receipt says so.

    Args:
        card_account_id: Id class — the identifying number of the cardholder's own card account as the cardholder holds it: the last four digits of the account number printed on the card (4 digits, e.g. 0000), as the cardholder states it.
        funding_account_last4: Fixed-format class — the last four digits of the bank account the debit is drawn on, 4 digits exactly as the cardholder states them.
        excess_allocation: Enum class — the basis on which the part of the payment above the minimum is allocated, exactly one of: highest_apr_first when no deferred-interest balance is near its end and the cardholder makes no allocation request, so the excess goes to the highest-APR balance; promo_expiry_window when a deferred-interest balance ends within the expiry window, so the excess goes to that promotional balance; deferred_promo_requested when the cardholder asks, while paying, that the excess go to a deferred-interest balance they name; single_balance when the account is a project loan with one balance; not_applicable only for a line that is not a payment, which never applies here.
        amount: Fixed-format class — the payment amount in USD, a positive number with 2 decimal places, already rounded to the cent; it is credited exactly as given.

    Returns:
        A text rendering of a dictionary with these fields: status — posted when the payment was credited, or not_found when no card carries those digits; card_transaction_id — the reference number of the new payment line (empty when not found); card_account_id — the last four digits given; amount — the payment in USD with 2 decimal places; payment_channel — phone_agent; funding_account_last4 — the bank account digits recorded; excess_allocation — the allocation basis recorded; transaction_date — the credit date, YYYY-MM-DD; current_balance — the amount owed once the payment is credited, USD with 2 decimal places.
    """
    amt = round(float(amount), 2)
    today = ctx.now()[:10]
    rows = ctx.find("card_accounts", account_last4=card_account_id)
    if not rows:
        return str({"status": "not_found", "card_transaction_id": "", "card_account_id": card_account_id,
                    "amount": amt, "payment_channel": "phone_agent", "funding_account_last4": funding_account_last4,
                    "excess_allocation": excess_allocation, "transaction_date": today, "current_balance": 0.0})
    acct = rows[0]
    aid = acct["card_account_id"]
    rid = ctx.make_id("ctx_", aid, funding_account_last4, excess_allocation, amt, today)
    ctx.create("card_transactions", rid, card_transaction_id=rid, card_account_id=aid,
               customer_id=acct.get("customer_id", ""), event_type="card_payment_posted",
               transaction_date=today, amount=amt, statement_period=today[:7], plan_code="not_applicable",
               promo_end_date="", merchant_reference="", purchase_channel="not_applicable",
               payment_channel="phone_agent", funding_account_last4=funding_account_last4,
               excess_allocation=excess_allocation, original_transaction_id=None, return_reason="not_applicable",
               fee_type="not_applicable", interest_type="not_applicable", reversal_reason="not_applicable",
               card_request_id=None, statement_date="", due_date="", statement_balance=0.0,
               minimum_payment_due=0.0, past_due_amount=0.0, days_past_due=0)
    new_balance = round(float(acct.get("current_balance") or 0) - amt, 2)
    ctx.update("card_accounts", aid, current_balance=new_balance)
    return str({"status": "posted", "card_transaction_id": rid, "card_account_id": card_account_id,
                "amount": amt, "payment_channel": "phone_agent", "funding_account_last4": funding_account_last4,
                "excess_allocation": excess_allocation, "transaction_date": today, "current_balance": new_balance})

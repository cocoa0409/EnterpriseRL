"""Hidden task tools for difficulty card_billing_payments_and_disputes (Piedmont Crescent Bank).

Each tool performs exactly one atomic card-ledger or card-account posting with the values the
agent has already decided from the published card policies. Tools write only card records: a
deposit redemption is recorded on the card with its receiving checking account, and no tool posts
an entry on a checking or savings account's own ledger. No tool checks eligibility, status,
time windows, prerequisites or amounts; it books what it is given and returns a receipt.
Ledger postings also carry their effect onto the account's running balance or points balance,
because a posted credit or redemption is, by definition, a change of that balance.
"""

from erlbench import ToolContext, tool


# Month (YYYY-MM) of the next statement closing date on or after today: a posting convention only.
_open_cycle = lambda ctx, account: (
    ctx.now()[:7] if int(ctx.now()[8:10]) <= int(account.get("statement_closing_day") or 28)
    else (f"{int(ctx.now()[:4]) + 1:04d}-01" if ctx.now()[5:7] == "12"
          else f"{ctx.now()[:4]}-{int(ctx.now()[5:7]) + 1:02d}"))

# Every card ledger field at its neutral value, so a posting only sets what it means.
_blank_txn = lambda customer_id, card_account_id: {
    "card_account_id": card_account_id, "customer_id": customer_id, "amount": "",
    "transaction_date": "", "merchant": "", "merchant_category": "none",
    "foreign_transaction": False, "reference_number": "", "statement_date": "",
    "fee_code": "none", "source_item_id": "", "interest_type": "none",
    "payment_source": "none", "counterparty_account_id": "", "adjustment_reason": "none",
    "reward_points": "", "redemption_type": "none",
}


@tool(owner="agent", rw="write")
def reverse_autopay_late_fee_e77f172c(ctx: ToolContext, customer_id: str, card_account_id: str,
                                      source_item_id: str, amount: float,
                                      adjustment_reason: str) -> str:
    """Reverse one billed late payment fee on a credit card account in full and record the ground for the reversal.

    The agent uses this to take a late payment fee back off a cardholder's credit card. One call
    posts one fee-reversal credit entry on the card account, linked to the late fee it cancels and
    carrying the reversal ground, in the statement cycle that is open today; the card's current
    balance owed goes down by the reversed amount at once. The cardholder sees the reversal credit
    on the card activity immediately and on the next statement. The call is complete when the
    receipt below comes back with status "reversed".

    Args:
        customer_id: Id class — the customer reference number of the cardholder whose fee is reversed, as returned by the customer profile lookup.
        card_account_id: Id class — the reference number of the credit card account that was billed the fee, as returned by the card account lookup.
        source_item_id: Id class — the reference number of the late payment fee entry being reversed, as returned by the card activity lookup for that account.
        amount: Fixed-format class — the amount reversed; unit USD, written as USD, 2 decimal places, or empty string, never empty for this call, a positive number rounded half-up to 2 decimal places (for example 32.00).
        adjustment_reason: Enum class — the ground on which the fee is reversed; exactly one of these allowed values: bank_error (the fee was billed contrary to the card charter and is reversed without counting against any courtesy allowance), courtesy_waiver (the fee was billed correctly and is reversed as a courtesy that counts against the cardholder's rolling courtesy allowance), dispute_final (the fee was billed on a disputed charge whose billing dispute was resolved for the cardholder), none (no ground; never valid for a fee reversal and not to be used), dispute_provisional (a temporary billing-dispute credit ground; never valid for a fee reversal and not to be used), scra_benefit (a military rate cap interest ground; never valid for a fee reversal and not to be used).

    Returns:
        A text rendering of a dictionary with these keys: status (always "reversed" when the posting succeeded), card_txn_id (text reference number of the new fee-reversal entry), card_account_id (text reference number of the card account), reversed_fee_id (text reference number of the fee entry that was reversed), amount (number, USD with 2 decimal places, the credit posted), adjustment_reason (text, the ground recorded), statement_cycle (text in YYYY-MM form, the statement cycle the reversal posted in), posted_date (text in YYYY-MM-DD form, today's date), new_current_balance (number, USD with 2 decimal places, the card's balance owed after the reversal).
    """
    account = ctx.find("card_accounts", card_account_id=card_account_id)[0]
    credit = round(float(amount), 2)
    cycle = _open_cycle(ctx, account)
    rid = ctx.make_id("ctx_", customer_id, card_account_id, source_item_id, amount, adjustment_reason)
    row = _blank_txn(customer_id, card_account_id)
    row.update(card_txn_id=rid, event_type="card_fee_reversal", posted_date=ctx.now()[:10],
               statement_cycle=cycle)
    ctx.create("card_transactions", rid, **row)
    ctx.update("card_transactions", rid, amount=round(float(amount), 2), fee_code="late_payment",
               source_item_id=source_item_id, adjustment_reason=adjustment_reason)
    new_balance = round(float(account.get("current_balance") or 0) - credit, 2)
    ctx.update("card_accounts", card_account_id, current_balance=new_balance)
    return str({"status": "reversed", "card_txn_id": rid, "card_account_id": card_account_id,
                "reversed_fee_id": source_item_id, "amount": credit,
                "adjustment_reason": adjustment_reason, "statement_cycle": cycle,
                "posted_date": ctx.now()[:10], "new_current_balance": new_balance})


@tool(owner="user", rw="write")
def restore_overdrawn_checking_with_points_4e4b44ef(ctx: ToolContext, card_account_id: str,
                                                   checking_account_id: str, reward_points: int,
                                                   amount: float) -> str:
    """Redeem rewards points from the cardholder's own credit card as a cash deposit into one of the cardholder's Piedmont Crescent Bank checking accounts.

    The cardholder uses this to turn card rewards points into cash in a checking account. One call
    posts one redemption entry on the card account for the number of points given, records the
    receiving checking account and the cash value delivered, and lowers the card's unredeemed
    points balance by those points at once. The redemption entry on the card, naming the receiving
    checking account, is the record of the deposit; this tool does not itself post an entry on the
    checking account's own ledger. The cardholder sees the points leave the card's rewards balance
    immediately and the deposit described on the receipt. The call is complete when the receipt
    below comes back with status "redeemed".

    Args:
        card_account_id: Id class — the reference number of the credit card account whose points are redeemed, as returned by the card account lookup.
        checking_account_id: Id class — the reference number of the cardholder's checking account that receives the deposit, as returned by the checking account lookup.
        reward_points: Fixed-format class — how many points are redeemed; unit rewards points, written as a non-negative integer, or empty string, never empty for this call, a whole positive integer with no decimal part (for example 6500).
        amount: Fixed-format class — the cash value delivered to the checking account; unit USD, written as USD, 2 decimal places, or empty string, never empty for this call, a positive number rounded half-up to 2 decimal places (for example 65.00).

    Returns:
        A text rendering of a dictionary with these keys: status (always "redeemed" when the posting succeeded), card_txn_id (text reference number of the new redemption entry), card_account_id (text reference number of the card account), redemption_type (text, always "deposit_to_checking"), receiving_account_id (text reference number of the checking account credited), reward_points (integer, points redeemed), amount (number, USD with 2 decimal places, cash value delivered), posted_date (text in YYYY-MM-DD form, today's date), new_rewards_balance (integer, the card's unredeemed points after the redemption).
    """
    account = ctx.find("card_accounts", card_account_id=card_account_id)[0]
    points = int(reward_points)
    cycle = _open_cycle(ctx, account)
    rid = ctx.make_id("ctx_", card_account_id, checking_account_id, reward_points, amount, "deposit_to_checking")
    row = _blank_txn(account.get("customer_id"), card_account_id)
    row.update(card_txn_id=rid, event_type="card_rewards_redeem", posted_date=ctx.now()[:10],
               statement_cycle=cycle, redemption_type="deposit_to_checking")
    ctx.create("card_transactions", rid, **row)
    ctx.update("card_transactions", rid, reward_points=int(reward_points),
               amount=round(float(amount), 2), counterparty_account_id=checking_account_id)
    remaining = int(account.get("rewards_balance") or 0) - points
    ctx.update("card_accounts", card_account_id, rewards_balance=remaining)
    return str({"status": "redeemed", "card_txn_id": rid, "card_account_id": card_account_id,
                "redemption_type": "deposit_to_checking", "receiving_account_id": checking_account_id,
                "reward_points": points, "amount": round(float(amount), 2),
                "posted_date": ctx.now()[:10], "new_rewards_balance": remaining})


@tool(owner="user", rw="write")
def apply_points_to_card_balance_295c0528(ctx: ToolContext, card_account_id: str, reward_points: int,
                                          amount: float) -> str:
    """Redeem rewards points from the cardholder's own credit card as a statement credit that pays down that card's balance owed.

    The cardholder uses this to spend card rewards points against what they owe on the same card.
    One call posts the redemption entry for the number of points given together with the matching
    statement-credit entry for the cash value, lowers the card's unredeemed points balance by those
    points and lowers the card's current balance owed by that value, all at once. The cardholder
    sees both the points and the balance go down immediately. The call is complete when the receipt
    below comes back with status "credited".

    Args:
        card_account_id: Id class — the reference number of the credit card account whose points are redeemed and whose balance is credited, as returned by the card account lookup.
        reward_points: Fixed-format class — how many points are redeemed; unit rewards points, written as a non-negative integer, or empty string, never empty for this call, a whole positive integer with no decimal part (for example 21500).
        amount: Fixed-format class — the statement credit applied to the card balance; unit USD, written as USD, 2 decimal places, or empty string, never empty for this call, a positive number rounded half-up to 2 decimal places (for example 215.00).

    Returns:
        A text rendering of a dictionary with these keys: status (always "credited" when the posting succeeded), redemption_id (text reference number of the new redemption entry), credit_id (text reference number of the new statement-credit entry), card_account_id (text reference number of the card account), reward_points (integer, points redeemed), amount (number, USD with 2 decimal places, credit applied), posted_date (text in YYYY-MM-DD form, today's date), new_rewards_balance (integer, the card's unredeemed points afterwards), new_current_balance (number, USD with 2 decimal places, the card's balance owed afterwards).
    """
    account = ctx.find("card_accounts", card_account_id=card_account_id)[0]
    points = int(reward_points)
    credit = round(float(amount), 2)
    cycle = _open_cycle(ctx, account)
    customer_id = account.get("customer_id")
    rid = ctx.make_id("ctx_", card_account_id, reward_points, amount, "statement_credit")
    row = _blank_txn(customer_id, card_account_id)
    row.update(card_txn_id=rid, event_type="card_rewards_redeem", posted_date=ctx.now()[:10],
               statement_cycle=cycle, redemption_type="statement_credit")
    ctx.create("card_transactions", rid, **row)
    ctx.update("card_transactions", rid, reward_points=int(reward_points), amount=round(float(amount), 2))
    cid = ctx.make_id("ctx_", rid, "card_rewards_credit")
    crow = _blank_txn(customer_id, card_account_id)
    crow.update(card_txn_id=cid, event_type="card_rewards_credit", posted_date=ctx.now()[:10],
                statement_cycle=cycle, source_item_id=rid, amount=credit)
    ctx.create("card_transactions", cid, **crow)
    remaining = int(account.get("rewards_balance") or 0) - points
    new_balance = round(float(account.get("current_balance") or 0) - credit, 2)
    ctx.update("card_accounts", card_account_id, rewards_balance=remaining, current_balance=new_balance)
    return str({"status": "credited", "redemption_id": rid, "credit_id": cid,
                "card_account_id": card_account_id, "reward_points": points, "amount": credit,
                "posted_date": ctx.now()[:10], "new_rewards_balance": remaining,
                "new_current_balance": new_balance})


@tool(owner="agent", rw="write")
def refund_closing_annual_fee_cfb04f99(ctx: ToolContext, customer_id: str, card_account_id: str,
                                       source_item_id: str, amount: float, adjustment_reason: str) -> str:
    """Reverse one billed annual fee on a credit card account in full and record the ground for the reversal.

    The agent uses this to take an annual fee back off a cardholder's credit card. One call posts one
    fee-reversal credit entry on the card account, linked to the annual fee it cancels and carrying
    the reversal ground, in the statement cycle that is open today; the card's current balance owed
    goes down by the reversed amount at once. The cardholder sees the credit on the card activity
    immediately. The call is complete when the receipt below comes back with status "reversed".

    Args:
        customer_id: Id class — the customer reference number of the cardholder whose fee is reversed, as returned by the customer profile lookup.
        card_account_id: Id class — the reference number of the credit card account that was billed the annual fee, as returned by the card account lookup.
        source_item_id: Id class — the reference number of the annual fee entry being reversed, as returned by the card activity lookup for that account.
        amount: Fixed-format class — the amount reversed; unit USD, written as USD, 2 decimal places, or empty string, never empty for this call, a positive number rounded half-up to 2 decimal places (for example 95.00).
        adjustment_reason: Enum class — the ground on which the annual fee is reversed; exactly one of these allowed values: bank_error (the fee must not stand under the card charter, for example it is refunded because the card is closed inside the refund window or a waiver excluded it), courtesy_waiver (a courtesy reversal; never valid for an annual fee because courtesy reversals apply only to late payment fees), dispute_final (the fee was billed on a disputed charge resolved for the cardholder; never the case for an annual fee), none (no ground; never valid for a fee reversal and not to be used), dispute_provisional (a temporary billing-dispute credit ground; never valid for a fee reversal and not to be used), scra_benefit (a military rate cap interest ground; never valid for a fee reversal and not to be used).

    Returns:
        A text rendering of a dictionary with these keys: status (always "reversed" when the posting succeeded), card_txn_id (text reference number of the new fee-reversal entry), card_account_id (text reference number of the card account), reversed_fee_id (text reference number of the annual fee entry reversed), amount (number, USD with 2 decimal places, the credit posted), adjustment_reason (text, the ground recorded), statement_cycle (text in YYYY-MM form, the statement cycle the reversal posted in), posted_date (text in YYYY-MM-DD form, today's date), new_current_balance (number, USD with 2 decimal places, the card's balance owed after the reversal).
    """
    account = ctx.find("card_accounts", card_account_id=card_account_id)[0]
    credit = round(float(amount), 2)
    cycle = _open_cycle(ctx, account)
    rid = ctx.make_id("ctx_", customer_id, card_account_id, source_item_id, amount, adjustment_reason, "annual")
    row = _blank_txn(customer_id, card_account_id)
    row.update(card_txn_id=rid, event_type="card_fee_reversal", posted_date=ctx.now()[:10],
               statement_cycle=cycle)
    ctx.create("card_transactions", rid, **row)
    ctx.update("card_transactions", rid, amount=round(float(amount), 2), fee_code="annual",
               source_item_id=source_item_id, adjustment_reason=adjustment_reason)
    new_balance = round(float(account.get("current_balance") or 0) - credit, 2)
    ctx.update("card_accounts", card_account_id, current_balance=new_balance)
    return str({"status": "reversed", "card_txn_id": rid, "card_account_id": card_account_id,
                "reversed_fee_id": source_item_id, "amount": credit,
                "adjustment_reason": adjustment_reason, "statement_cycle": cycle,
                "posted_date": ctx.now()[:10], "new_current_balance": new_balance})


@tool(owner="user", rw="write")
def set_closing_card_autopay_dbe1c3a9(ctx: ToolContext, card_account_id: str, autopay_option: str,
                                      autopay_amount: float, autopay_source_account_id: str) -> str:
    """Record the cardholder's own automatic payment instruction on a credit card account, replacing whatever instruction was in force.

    The cardholder uses this to say how their card is paid automatically each due date. One call
    overwrites the card account's autopay option, fixed monthly amount and paying checking account
    with the values given; nothing else on the card changes. The cardholder sees the new instruction
    on the card at once. The call is complete when the receipt below comes back with status "set".

    Args:
        card_account_id: Id class — the reference number of the credit card account whose autopay instruction is recorded, as returned by the card account lookup.
        autopay_option: Enum class — which automatic payment is taken on each due date; exactly one of these allowed values: none (no automatic payment is taken), minimum_due (the minimum payment due on each statement is debited), statement_balance (the full statement balance is debited), fixed_amount (the fixed amount given in autopay_amount is debited, never more than the statement balance).
        autopay_amount: Fixed-format class — the fixed monthly amount debited when autopay_option is fixed_amount, and 0.00 for every other option; unit USD, written as USD, 2 decimal places, rounded half-up to 2 decimal places (for example 250.00).
        autopay_source_account_id: Id class — the reference number of the cardholder's PCB checking account that pays the card, as returned by the checking account lookup; empty text only when autopay_option is none.

    Returns:
        A text rendering of a dictionary with these keys: status (always "set" when the instruction was recorded), card_account_id (text reference number of the card account), autopay_option (text, the option now in force), autopay_amount (number, USD with 2 decimal places, the fixed amount now in force), autopay_source_account_id (text reference number of the paying checking account), recorded_at (text timestamp of the change, exactly today's clock reading).
    """
    ctx.update("card_accounts", card_account_id, autopay_option=autopay_option,
               autopay_amount=round(float(autopay_amount), 2),
               autopay_source_account_id=autopay_source_account_id)
    return str({"status": "set", "card_account_id": card_account_id, "autopay_option": autopay_option,
                "autopay_amount": round(float(autopay_amount), 2),
                "autopay_source_account_id": autopay_source_account_id, "recorded_at": ctx.now()})


@tool(owner="user", rw="write")
def cash_out_closing_card_points_6700a44f(ctx: ToolContext, card_account_id: str, checking_account_id: str,
                                          reward_points: int, amount: float) -> str:
    """Cash out rewards points from a credit card the cardholder is closing, as a deposit into the cardholder's PCB checking account.

    The cardholder uses this before a card closes so its points are not lost. One call posts one
    redemption entry on the card for the number of points given, records the receiving checking
    account and the cash value delivered, and lowers the card's unredeemed points balance by those
    points at once. The redemption entry on the card, naming the receiving checking account, is the
    record of the cash-out; this tool does not itself post an entry on the checking account's own
    ledger. The cardholder sees the points leave the card immediately. The call is complete when the
    receipt below comes back with status "cashed_out".

    Args:
        card_account_id: Id class — the reference number of the credit card account whose points are cashed out, as returned by the card account lookup.
        checking_account_id: Id class — the reference number of the cardholder's checking account that receives the cash, as returned by the checking account lookup or shown on the card's autopay instruction.
        reward_points: Fixed-format class — how many points are cashed out; unit rewards points, written as a non-negative integer, or empty string, never empty for this call, a whole positive integer with no decimal part (for example 12000).
        amount: Fixed-format class — the cash value deposited; unit USD, written as USD, 2 decimal places, or empty string, never empty for this call, a positive number rounded half-up to 2 decimal places (for example 120.00).

    Returns:
        A text rendering of a dictionary with these keys: status (always "cashed_out" when the posting succeeded), card_txn_id (text reference number of the new redemption entry), card_account_id (text reference number of the card account), receiving_account_id (text reference number of the checking account credited), reward_points (integer, points cashed out), amount (number, USD with 2 decimal places, cash value deposited), posted_date (text in YYYY-MM-DD form, today's date), new_rewards_balance (integer, the card's unredeemed points afterwards).
    """
    account = ctx.find("card_accounts", card_account_id=card_account_id)[0]
    points = int(reward_points)
    cycle = _open_cycle(ctx, account)
    rid = ctx.make_id("ctx_", card_account_id, checking_account_id, reward_points, amount, "closing_cash_out")
    row = _blank_txn(account.get("customer_id"), card_account_id)
    row.update(card_txn_id=rid, event_type="card_rewards_redeem", posted_date=ctx.now()[:10],
               statement_cycle=cycle, redemption_type="deposit_to_checking")
    ctx.create("card_transactions", rid, **row)
    ctx.update("card_transactions", rid, reward_points=int(reward_points),
               amount=round(float(amount), 2), counterparty_account_id=checking_account_id)
    remaining = int(account.get("rewards_balance") or 0) - points
    ctx.update("card_accounts", card_account_id, rewards_balance=remaining)
    return str({"status": "cashed_out", "card_txn_id": rid, "card_account_id": card_account_id,
                "receiving_account_id": checking_account_id, "reward_points": points,
                "amount": round(float(amount), 2), "posted_date": ctx.now()[:10],
                "new_rewards_balance": remaining})


@tool(owner="user", rw="write")
def confirm_card_closure_806ea607(ctx: ToolContext, card_account_id: str, autopay_option: str) -> str:
    """Confirm, as the cardholder, the closure of one of your own credit card accounts and state which automatic payment instruction stays on it.

    The cardholder uses this to close a card. One call sets the card account's status to closed with
    today's date as the closing date and sets its autopay option to the value given; any balance
    still owed stays payable, and the card can no longer be used. The cardholder sees the card as
    closed at once. The call is complete when the receipt below comes back with status "closed".

    Args:
        card_account_id: Id class — the reference number of the credit card account being closed, as returned by the card account lookup.
        autopay_option: Enum class — the automatic payment option that remains on the closed card; exactly one of these allowed values: none (no automatic payment continues after closure), minimum_due (the minimum payment keeps being debited until the balance is paid), statement_balance (the full statement balance keeps being debited until the balance is paid), fixed_amount (the fixed amount already on the card keeps being debited until the balance is paid).

    Returns:
        A text rendering of a dictionary with these keys: status (always "closed" when the closure was recorded), card_account_id (text reference number of the card account), closed_date (text in YYYY-MM-DD form, today's date), autopay_option (text, the automatic payment option left on the closed card).
    """
    ctx.update("card_accounts", card_account_id, status="closed", closed_date=ctx.now()[:10],
               autopay_option=autopay_option)
    return str({"status": "closed", "card_account_id": card_account_id, "closed_date": ctx.now()[:10],
                "autopay_option": autopay_option})

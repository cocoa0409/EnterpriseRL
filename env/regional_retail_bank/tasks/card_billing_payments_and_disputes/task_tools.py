"""Hidden task tools for the card_billing_payments_and_disputes difficulty.

Each tool performs one atomic write on a Piedmont Crescent Bank credit card record. The
names are discovered only through the published card knowledge base and are reached through
the unlock/call meta tools. No tool aggregates history, judges eligibility or computes a
policy amount: the agent works the figure out and passes it in.
"""

from erlbench import ToolContext, tool


@tool(owner="agent", rw="write")
def reverse_card_late_fee_4ff0f41c(ctx: ToolContext, card_account_id: str, customer_id: str,
                                   source_item_id: str, correction_amount: float) -> str:
    """Credit back part of a late payment fee that was billed to a Piedmont Crescent Bank credit card.

    One call books a single reversal entry on the card's ledger, marked as a late payment fee
    reversal booked as a bank error, tied to the exact fee entry it credits against, and dated
    the day of the call in that day's statement cycle. The same call lowers the
    balance owed on the card account by the credited amount. The cardholder sees the credit on
    the card's activity list straight away and a smaller balance owed; the entry's own
    reference number in the confirmation text is what shows the call completed.

    Args:
        card_account_id: Id class — the reference number of the credit card account whose ledger receives the credit and whose balance owed falls; read it from the card account lookup for this cardholder before the call.
        customer_id: Id class — the reference number identifying the cardholder profile the credited card account belongs to; read it from the customer profile lookup before the call.
        source_item_id: Id class — the reference number of the single late payment fee entry on that card's ledger the credit is booked against; read it from the card activity lookup before the call.
        correction_amount: Fixed-format class — the money credited back to the cardholder for that fee, expressed exactly as the ledger records a money amount, that is USD, 2 decimal places, or empty string, given here always as a positive number carried to 2 decimal places and rounded half-up; pass only the figure itself and never a percentage or a share.

    Returns:
        A confirmation sentence in plain text. It names the new ledger entry's own reference
        number, repeats the credited amount in US dollars to two decimals, names the card
        account reference number, and states the balance owed after the credit, also in US
        dollars to two decimals. A sentence of that shape means the entry was booked and the
        balance was lowered; anything beginning with Error means nothing was written.
    """
    account = ctx.find("card_accounts", card_account_id=card_account_id)
    if not account:
        return f"Error: no card account {card_account_id}."
    credited = round(float(correction_amount), 2)
    new_balance = round(float(account[0].get("current_balance") or 0) - credited, 2)
    rid = ctx.make_id("ctx_", card_account_id, customer_id, source_item_id, credited)
    ctx.create("card_transactions", rid, card_txn_id=rid, card_account_id=card_account_id,
               customer_id=customer_id, event_type="card_fee_reversal", amount=credited,
               posted_date=ctx.now()[:10], fee_code="late_payment", source_item_id=source_item_id,
               adjustment_reason="bank_error", statement_cycle=ctx.now()[:7],
               merchant="", merchant_category="none", foreign_transaction="False",
               reference_number="", transaction_date="", statement_date="", interest_type="none",
               payment_source="none", counterparty_account_id="", card_dispute_id="",
               reward_points="", redemption_type="none")
    ctx.update("card_accounts", card_account_id, current_balance=new_balance)
    return (f"Fee correction {rid} credited {credited:.2f} USD against fee {source_item_id} on card "
            f"account {card_account_id}; balance owed is now {new_balance:.2f} USD.")


@tool(owner="user", rw="write")
def redeem_card_points_9bfb7edb(ctx: ToolContext, card_account_id: str, customer_id: str,
                                points_redeemed: int) -> str:
    """Let the cardholder themselves cash in rewards points from their Piedmont Crescent Bank credit card as a statement credit.

    One call books a single redemption entry on the card's rewards ledger, recorded as a
    statement-credit redemption dated the day of the call in that day's statement cycle, and
    takes the redeemed points out of the unredeemed points standing on the card account. The
    cardholder sees the points come off their rewards total immediately and the statement
    credit follows on the card. The redemption entry's own reference number in the confirmation
    text is what shows the call completed.

    Args:
        card_account_id: Id class — the reference number of the credit card account whose rewards points are cashed in; read it from the card account lookup for this cardholder before the call.
        customer_id: Id class — the reference number identifying the cardholder profile that owns the points; read it from the customer profile lookup before the call.
        points_redeemed: Fixed-format class — how many rewards points are cashed in, counted in whole points exactly as the rewards ledger records a point count, that is non-negative integer, or empty string, so pass a whole integer with no decimal part, no thousands separator and no currency sign.

    Returns:
        A confirmation sentence in plain text. It names the new rewards ledger entry's own
        reference number, repeats the number of points cashed in as a whole number, names the
        card account reference number, and states the unredeemed points still standing on the
        account afterwards as a whole number. A sentence of that shape means the redemption was
        booked; anything beginning with Error means nothing was written.
    """
    account = ctx.find("card_accounts", card_account_id=card_account_id)
    if not account:
        return f"Error: no card account {card_account_id}."
    used = int(points_redeemed)
    remaining = int(float(account[0].get("rewards_balance") or 0)) - used
    rid = ctx.make_id("crd_", card_account_id, customer_id, used)
    ctx.create("card_transactions", rid, card_txn_id=rid, card_account_id=card_account_id,
               customer_id=customer_id, event_type="card_rewards_redeem", reward_points=used,
               redemption_type="statement_credit", posted_date=ctx.now()[:10],
               statement_cycle=ctx.now()[:7], amount="", merchant="", merchant_category="none",
               foreign_transaction="False", reference_number="", transaction_date="",
               statement_date="", fee_code="none", source_item_id="", interest_type="none",
               payment_source="none", counterparty_account_id="", adjustment_reason="none",
               card_dispute_id="")
    ctx.update("card_accounts", card_account_id, rewards_balance=remaining)
    return (f"Redemption {rid} cashed in {used} points on card account {card_account_id}; "
            f"{remaining} unredeemed points remain.")


@tool(owner="agent", rw="write")
def post_card_dispute_credit_83d80881(ctx: ToolContext, card_account_id: str, customer_id: str,
                                      card_dispute_id: str, source_item_id: str,
                                      provisional_credit_amount: float) -> str:
    """Put a temporary credit on a Piedmont Crescent Bank credit card while a billing dispute is being worked.

    One call books a single temporary credit entry on the card's ledger, marked as a provisional
    dispute credit, tied both to the dispute being worked and to the charge under dispute, and
    dated the day of the call in that day's statement cycle. The same call lowers the balance owed
    on the card account by the credited amount. The cardholder sees the credit on the card's
    activity list straight away and a smaller balance owed; the entry's own reference number in the
    confirmation text is what shows the call completed.

    Args:
        card_account_id: Id class — the reference number of the credit card account whose ledger receives the temporary credit and whose balance owed falls; read it from the card account lookup for this cardholder before the call.
        customer_id: Id class — the reference number identifying the cardholder profile the credited card account belongs to; read it from the customer profile lookup before the call.
        card_dispute_id: Id class — the reference number of the billing dispute this temporary credit belongs to; read it from the card dispute lookup before the call.
        source_item_id: Id class — the reference number of the single card ledger entry that is the charge under dispute; read it from the card dispute record or the card activity lookup before the call.
        provisional_credit_amount: Fixed-format class — the money credited to the cardholder while the dispute is worked, expressed exactly as the ledger records a money amount, that is USD, 2 decimal places, or empty string, given here always as a positive number carried to 2 decimal places and rounded half-up; pass only the figure itself and never a proportion or a share.

    Returns:
        A confirmation sentence in plain text. It names the new ledger entry's own reference number,
        repeats the credited amount in US dollars to two decimals, names the dispute reference
        number and the card account reference number, and states the balance owed after the credit,
        also in US dollars to two decimals. A sentence of that shape means the entry was booked and
        the balance was lowered; anything beginning with Error means nothing was written.
    """
    account = ctx.find("card_accounts", card_account_id=card_account_id)
    if not account:
        return f"Error: no card account {card_account_id}."
    credited = round(float(provisional_credit_amount), 2)
    new_balance = round(float(account[0].get("current_balance") or 0) - credited, 2)
    rid = ctx.make_id("cdc_", card_account_id, card_dispute_id, source_item_id, credited)
    ctx.create("card_transactions", rid, card_txn_id=rid, card_account_id=card_account_id,
               customer_id=customer_id, event_type="card_dispute_credit", amount=credited,
               posted_date=ctx.now()[:10], statement_cycle=ctx.now()[:7],
               source_item_id=source_item_id, card_dispute_id=card_dispute_id,
               adjustment_reason="dispute_provisional", fee_code="none", merchant="",
               merchant_category="none", foreign_transaction="False", reference_number="",
               transaction_date="", statement_date="", interest_type="none", payment_source="none",
               reward_points="", redemption_type="none")
    ctx.update("card_accounts", card_account_id, current_balance=new_balance)
    return (f"Temporary credit {rid} of {credited:.2f} USD posted for dispute {card_dispute_id} on card "
            f"account {card_account_id}; balance owed is now {new_balance:.2f} USD.")


@tool(owner="agent", rw="write")
def rebill_card_dispute_credit_f8e84f35(ctx: ToolContext, card_account_id: str, customer_id: str,
                                        card_dispute_id: str, source_item_id: str,
                                        rebill_amount: float) -> str:
    """Charge back onto a Piedmont Crescent Bank credit card a temporary credit the cardholder is no longer entitled to keep.

    One call books a single rebill entry on the card's ledger, tied both to the billing dispute it
    belongs to and to the temporary credit entry it takes back, and dated the day of the call in
    that day's statement cycle. The same call raises the balance owed on the card account by the
    rebilled amount. The cardholder sees the charge on the card's activity list straight away and a
    larger balance owed; the entry's own reference number in the confirmation text is what shows the
    call completed.

    Args:
        card_account_id: Id class — the reference number of the credit card account whose ledger receives the rebill and whose balance owed rises; read it from the card account lookup for this cardholder before the call.
        customer_id: Id class — the reference number identifying the cardholder profile the rebilled card account belongs to; read it from the customer profile lookup before the call.
        card_dispute_id: Id class — the reference number of the billing dispute this rebill belongs to; read it from the card dispute lookup before the call.
        source_item_id: Id class — the reference number of the single temporary credit entry on the card's ledger that is being taken back; read it from the card activity lookup before the call.
        rebill_amount: Fixed-format class — the money charged back to the cardholder, expressed exactly as the ledger records a money amount, that is USD, 2 decimal places, or empty string, given here always as a positive number carried to 2 decimal places and rounded half-up; pass only the figure itself and never a proportion or a share.

    Returns:
        A confirmation sentence in plain text. It names the new ledger entry's own reference number,
        repeats the rebilled amount in US dollars to two decimals, names the dispute reference
        number and the card account reference number, and states the balance owed after the rebill,
        also in US dollars to two decimals. A sentence of that shape means the entry was booked and
        the balance was raised; anything beginning with Error means nothing was written.
    """
    account = ctx.find("card_accounts", card_account_id=card_account_id)
    if not account:
        return f"Error: no card account {card_account_id}."
    charged = round(float(rebill_amount), 2)
    new_balance = round(float(account[0].get("current_balance") or 0) + charged, 2)
    rid = ctx.make_id("cdr_", card_account_id, card_dispute_id, source_item_id, charged)
    ctx.create("card_transactions", rid, card_txn_id=rid, card_account_id=card_account_id,
               customer_id=customer_id, event_type="card_dispute_rebill", amount=charged,
               posted_date=ctx.now()[:10], statement_cycle=ctx.now()[:7],
               source_item_id=source_item_id, card_dispute_id=card_dispute_id,
               adjustment_reason="none", fee_code="none", merchant="", merchant_category="none",
               foreign_transaction="False", reference_number="", transaction_date="",
               statement_date="", interest_type="none", payment_source="none", reward_points="",
               redemption_type="none")
    ctx.update("card_accounts", card_account_id, current_balance=new_balance)
    return (f"Rebill {rid} of {charged:.2f} USD posted for dispute {card_dispute_id} on card account "
            f"{card_account_id}; balance owed is now {new_balance:.2f} USD.")


@tool(owner="user", rw="write")
def set_card_autopay_amount_b2f02f74(ctx: ToolContext, card_account_id: str,
                                     autopay_source_account_id: str, autopay_amount: float) -> str:
    """Let the cardholder themselves put a standing monthly automatic payment of a fixed sum on their Piedmont Crescent Bank credit card.

    One call replaces whatever automatic payment instruction the card account carries with a fixed
    monthly sum, records the sum, and names the Piedmont Crescent Bank checking account the money
    will be taken from each month. The cardholder sees the instruction and its amount on the card
    account from then on, and the named checking account is what the monthly debit will come out of.
    The confirmation text repeating the fixed sum and the paying account is what shows the call
    completed.

    Args:
        card_account_id: Id class — the reference number of the credit card account the standing instruction is placed on; read it from the card account lookup for this cardholder before the call.
        autopay_source_account_id: Id class — the reference number of the Piedmont Crescent Bank checking account the monthly sum is taken from; read it from the checking account lookup for this cardholder before the call.
        autopay_amount: Fixed-format class — the fixed sum taken each month, expressed exactly as the card account records a money amount, that is USD, 2 decimal places, given here always as a positive number carried to 2 decimal places and rounded half-up; pass only the figure itself and never a share of a balance.

    Returns:
        A confirmation sentence in plain text. It names the card account reference number, states
        the standing instruction now in force as a fixed monthly sum, repeats that sum in US dollars
        to two decimals, and names the checking account reference number the money will come from. A
        sentence of that shape means the instruction is recorded; anything beginning with Error
        means nothing was written.
    """
    account = ctx.find("card_accounts", card_account_id=card_account_id)
    if not account:
        return f"Error: no card account {card_account_id}."
    monthly = round(float(autopay_amount), 2)
    ctx.update("card_accounts", card_account_id, autopay_option="fixed_amount",
               autopay_amount=monthly, autopay_source_account_id=autopay_source_account_id)
    return (f"Card account {card_account_id} now pays automatically by a fixed monthly amount of "
            f"{monthly:.2f} USD from checking account {autopay_source_account_id}.")

"""Hidden task tools of the shopper_payouts_and_cashouts difficulty (Cartwise shopper payouts).

Each tool performs one atomic write on the shopper's payout account and is reached through the
unlock_* -> call_* meta-tools once its name has been read from the payout charter.  A tool never
judges eligibility, never aggregates history and never computes the amount it books: the amount is
worked out beforehand from the charter and passed in.  Where a tool books money into or out of the
unpaid earnings balance or the card cashback balance, it keeps the balance figure shown on the
account in step with the entry it books.
"""

from erlbench import ToolContext, tool


@tool(owner="agent", rw="write")
def resend_returned_transfer_f902fe69(ctx: ToolContext, payout_account_id: str, returned_event_id: str,
                                      resend_usd: float) -> str:
    """Send again, as its own re-send deposit, money from a payout that the shopper's bank or card sent back.
    One call books one re-send deposit on the shopper payout account: the stated amount leaves the unpaid
    earnings balance and goes to the payout destination currently on file, and the deposit points to the
    returned-payout entry it answers, so the shopper can see which bounced payout is being sent again. The
    unpaid earnings balance shown on the account falls by the same amount. Success is a receipt naming the new
    re-send deposit and the balance that remains.

    Args:
        payout_account_id: Id class — the shopper payout account number the re-send is booked on, read from the payout account lookup.
        returned_event_id: Id class — the reference number of the returned-payout entry (the entry recording that a deposit or cashout came back) this re-send answers, read from the payout account's entries lookup.
        resend_usd: Fixed-format class — the amount sent again, in USD, a positive number with 2 decimal places (cents), booked exactly as given with no further rounding.

    Returns:
        A dictionary rendered as text with: status ("resent" when the deposit was booked); payout_event_id (the
        reference number of the new re-send deposit entry); returned_event_id (the returned-payout entry it answers);
        amount_usd (the amount sent, USD with 2 decimal places); event_date (booking date, YYYY-MM-DD);
        available_balance_usd (the unpaid earnings balance left on the account, USD with 2 decimal places).
    """
    acct = (ctx.find("payout_accounts", payout_account_id=payout_account_id) or [{}])[0]
    amount = round(float(resend_usd), 2)
    rid = ctx.make_id("pev_", payout_account_id, returned_event_id, resend_usd)
    ctx.create("payout_events", rid, payout_event_id=rid, payout_account_id=payout_account_id,
               customer_id=acct.get("customer_id"), event_type="payout_weekly_deposit",
               source_event_id=returned_event_id, amount_usd=amount, event_date=ctx.now()[:10])
    left = round(float(acct.get("available_balance_usd") or 0) - amount, 2)
    ctx.update("payout_accounts", payout_account_id, available_balance_usd=left)
    return str({"status": "resent", "payout_event_id": rid, "returned_event_id": returned_event_id,
                "amount_usd": amount, "event_date": ctx.now()[:10], "available_balance_usd": left})


@tool(owner="agent", rw="write")
def send_catchup_deposit_164755b4(ctx: ToolContext, payout_account_id: str, payout_period_end: str,
                                  amount_usd: float) -> str:
    """Send a single catch-up deposit for weekly deposits that could not go out while the shopper payout account
    was not active. One call books one deposit on the account: the stated amount leaves the unpaid earnings balance
    and goes to the payout destination on file, labelled with the last day of the weekly earnings period it
    closes. The unpaid earnings balance shown on the account falls by the same amount. Success is a receipt naming
    the new deposit and the balance that remains.

    Args:
        payout_account_id: Id class — the shopper payout account number the deposit is booked on, read from the payout account lookup.
        payout_period_end: Fixed-format class — the last day of the weekly earnings period the deposit closes, a calendar date written YYYY-MM-DD.
        amount_usd: Fixed-format class — the amount deposited, in USD, a positive number with 2 decimal places (cents), booked exactly as given with no further rounding.

    Returns:
        A dictionary rendered as text with: status ("deposited" when the deposit was booked); payout_event_id (the
        reference number of the new deposit entry); payout_period_end (the period end it carries, YYYY-MM-DD);
        amount_usd (the amount sent, USD with 2 decimal places); event_date (booking date, YYYY-MM-DD);
        available_balance_usd (the unpaid earnings balance left on the account, USD with 2 decimal places).
    """
    acct = (ctx.find("payout_accounts", payout_account_id=payout_account_id) or [{}])[0]
    amount = round(float(amount_usd), 2)
    rid = ctx.make_id("pev_", payout_account_id, payout_period_end, amount_usd)
    ctx.create("payout_events", rid, payout_event_id=rid, payout_account_id=payout_account_id,
               customer_id=acct.get("customer_id"), event_type="payout_weekly_deposit",
               payout_period_end=payout_period_end, amount_usd=amount, event_date=ctx.now()[:10])
    left = round(float(acct.get("available_balance_usd") or 0) - amount, 2)
    ctx.update("payout_accounts", payout_account_id, available_balance_usd=left)
    return str({"status": "deposited", "payout_event_id": rid, "payout_period_end": payout_period_end,
                "amount_usd": amount, "event_date": ctx.now()[:10], "available_balance_usd": left})


@tool(owner="agent", rw="write")
def move_off_card_plan_7a80b851(ctx: ToolContext, payout_account_id: str, new_variant_name: str,
                                statement_month: str, settlement_usd: float) -> str:
    """Move a shopper payout account from an Everyday Pay Card plan to the payout plan named, and pay the card's
    cashback settlement onto the card in the same step. One call changes the account's payout plan and records
    today as its plan-change date, books one cashback payment of the stated amount labelled with the statement
    month given, and clears the card cashback balance shown on the account, since any cashback the settlement does
    not pay lapses with the move. Success is a receipt showing the new plan and the settlement paid.

    Args:
        payout_account_id: Id class — the shopper payout account number being moved, read from the payout account lookup.
        new_variant_name: Enum class — the payout plan the account moves to, written exactly as one of: Weekly Direct Deposit — the shopper now receives payouts to a bank account; Instant Cashout — the shopper now receives payouts to an external debit card; Everyday Pay Card Blue — the account would stay on the card plans at the Blue tier, which is not a move off the card; Everyday Pay Card Gold — the account would stay on the card plans at the Gold tier, which is not a move off the card; Everyday Pay Card Platinum — the account would stay on the card plans at the Platinum tier, which is not a move off the card; Everyday Pay Card Diamond — the account would stay on the card plans at the Diamond tier, which is not a move off the card.
        statement_month: Fixed-format class — the statement month the cashback settlement is labelled with, written YYYY-MM.
        settlement_usd: Fixed-format class — the cashback settlement paid onto the card, in USD, a non-negative number with 2 decimal places (cents), booked exactly as given with no further rounding.

    Returns:
        A dictionary rendered as text with: status ("moved" when the plan change and settlement were booked);
        variant_name (the account's payout plan now in force); plan_changed_date (YYYY-MM-DD); payout_event_id (the
        reference number of the cashback payment entry); statement_month (YYYY-MM); amount_usd (the settlement paid,
        USD with 2 decimal places); cashback_balance_usd (the card cashback balance left, USD with 2 decimal places).
    """
    acct = (ctx.find("payout_accounts", payout_account_id=payout_account_id) or [{}])[0]
    amount = round(float(settlement_usd), 2)
    today = ctx.now()[:10]
    ctx.update("payout_accounts", payout_account_id, variant_name=new_variant_name, plan_changed_date=today,
               cashback_balance_usd=0.0)
    rid = ctx.make_id("pev_", payout_account_id, new_variant_name, statement_month, settlement_usd)
    ctx.create("payout_events", rid, payout_event_id=rid, payout_account_id=payout_account_id,
               customer_id=acct.get("customer_id"), event_type="payout_cashback_paid",
               statement_month=statement_month, amount_usd=amount, event_date=today)
    return str({"status": "moved", "variant_name": new_variant_name, "plan_changed_date": today,
                "payout_event_id": rid, "statement_month": statement_month, "amount_usd": amount,
                "cashback_balance_usd": 0.0})


@tool(owner="user", rw="write")
def cash_out_to_debit_card_0246d821(ctx: ToolContext, payout_account_id: str, amount_usd: float,
                                    fee_usd: float) -> str:
    """The shopper cashes out part of their unpaid earnings instantly to the external debit card on file. One call
    books one instant cashout of the stated amount and one cashout fee entry of the stated fee on the shopper's own
    payout account; both leave the unpaid earnings balance, the fee on top of the amount sent, and the cashout is
    numbered in sequence among the day's cashouts. The unpaid earnings balance shown on the account falls by the
    amount plus the fee. Success is a receipt with the cashout reference, the amount and fee, and the balance left.

    Args:
        payout_account_id: Id class — the shopper payout account number the cashout is drawn from, as the support agent reads it out from the payout account lookup.
        amount_usd: Fixed-format class — the amount sent to the debit card, in USD, a positive number with 2 decimal places (cents), as the support agent states it, booked exactly as given.
        fee_usd: Fixed-format class — the cashout fee taken from the balance on top of the amount sent, in USD, a non-negative number with 2 decimal places (cents), 0.00 when no fee applies, as the support agent states it.

    Returns:
        A dictionary rendered as text with: status ("cashed_out" when the cashout was booked); payout_event_id (the
        reference number of the cashout entry); fee_event_id (the reference number of the fee entry); cashout_number
        (the integer sequence of this cashout within the day); amount_usd and fee_usd (USD with 2 decimal places);
        event_date (YYYY-MM-DD); available_balance_usd (the unpaid earnings balance left, USD with 2 decimal places).
    """
    acct = (ctx.find("payout_accounts", payout_account_id=payout_account_id) or [{}])[0]
    amount = round(float(amount_usd), 2)
    fee = round(float(fee_usd), 2)
    today = ctx.now()[:10]
    number = len(ctx.find("payout_events", payout_account_id=payout_account_id,
                          event_type="payout_instant_cashout", event_date=today)) + 1
    rid = ctx.make_id("pev_", payout_account_id, amount_usd, fee_usd, today)
    ctx.create("payout_events", rid, payout_event_id=rid, payout_account_id=payout_account_id,
               customer_id=acct.get("customer_id"), event_type="payout_instant_cashout",
               cashout_number=number, amount_usd=amount, event_date=today)
    fid = ctx.make_id("pev_", rid, "fee", fee_usd)
    ctx.create("payout_events", fid, payout_event_id=fid, payout_account_id=payout_account_id,
               customer_id=acct.get("customer_id"), event_type="payout_cashout_fee_charged",
               source_event_id=rid, amount_usd=fee, event_date=today)
    left = round(float(acct.get("available_balance_usd") or 0) - amount - fee, 2)
    ctx.update("payout_accounts", payout_account_id, available_balance_usd=left)
    return str({"status": "cashed_out", "payout_event_id": rid, "fee_event_id": fid, "cashout_number": number,
                "amount_usd": amount, "fee_usd": fee, "event_date": today, "available_balance_usd": left})


@tool(owner="agent", rw="write")
def pay_statement_cashback_5d281cc6(ctx: ToolContext, payout_account_id: str, statement_month: str,
                                    amount_usd: float) -> str:
    """Pay Everyday Pay Card cashback onto the shopper's card as a statement payment. One call books one cashback
    payment of the stated amount on the shopper payout account, labelled with the statement month it carries, and the
    card cashback balance shown on the account falls by the same amount (never below zero). The shopper sees the
    payment on the card. Success is a receipt naming the payment, the month it carries and the cashback balance left.

    Args:
        payout_account_id: Id class — the shopper payout account number the cashback belongs to, read from the payout account lookup.
        statement_month: Fixed-format class — the statement month the payment carries, written YYYY-MM.
        amount_usd: Fixed-format class — the cashback paid onto the card, in USD, a positive number with 2 decimal places (cents), booked exactly as given with no further rounding.

    Returns:
        A dictionary rendered as text with: status ("paid" when the payment was booked); payout_event_id (the reference
        number of the cashback payment entry); statement_month (YYYY-MM); amount_usd (USD with 2 decimal places);
        event_date (YYYY-MM-DD); cashback_balance_usd (the card cashback balance left, USD with 2 decimal places).
    """
    acct = (ctx.find("payout_accounts", payout_account_id=payout_account_id) or [{}])[0]
    amount = round(float(amount_usd), 2)
    rid = ctx.make_id("pev_", payout_account_id, statement_month, amount_usd)
    ctx.create("payout_events", rid, payout_event_id=rid, payout_account_id=payout_account_id,
               customer_id=acct.get("customer_id"), event_type="payout_cashback_paid",
               statement_month=statement_month, amount_usd=amount, event_date=ctx.now()[:10])
    left = round(max(0.0, float(acct.get("cashback_balance_usd") or 0) - amount), 2)
    ctx.update("payout_accounts", payout_account_id, cashback_balance_usd=left)
    return str({"status": "paid", "payout_event_id": rid, "statement_month": statement_month, "amount_usd": amount,
                "event_date": ctx.now()[:10], "cashback_balance_usd": left})


@tool(owner="agent", rw="write")
def settle_closing_cashback_4e373fbf(ctx: ToolContext, payout_account_id: str, statement_month: str,
                                     amount_usd: float) -> str:
    """Pay a closing cashback settlement onto the shopper's Everyday Pay Card for a card-plan payout account. One
    call books one cashback payment of the stated amount on the shopper payout account, labelled with the statement
    month it settles, and the card cashback balance shown on the account falls by the same amount (never below zero).
    The shopper sees the settlement on the card. Success is a receipt naming the settlement and the cashback balance left.

    Args:
        payout_account_id: Id class — the shopper payout account number the settlement is paid on, read from the payout account lookup.
        statement_month: Fixed-format class — the statement month the settlement carries, written YYYY-MM.
        amount_usd: Fixed-format class — the settlement paid onto the card, in USD, a non-negative number with 2 decimal places (cents), booked exactly as given with no further rounding.

    Returns:
        A dictionary rendered as text with: status ("settled" when the settlement was booked); payout_event_id (the
        reference number of the cashback payment entry); statement_month (YYYY-MM); amount_usd (USD with 2 decimal
        places); event_date (YYYY-MM-DD); cashback_balance_usd (the card cashback balance left, USD with 2 decimal places).
    """
    acct = (ctx.find("payout_accounts", payout_account_id=payout_account_id) or [{}])[0]
    amount = round(float(amount_usd), 2)
    rid = ctx.make_id("pev_", payout_account_id, "closing", statement_month, amount_usd)
    ctx.create("payout_events", rid, payout_event_id=rid, payout_account_id=payout_account_id,
               customer_id=acct.get("customer_id"), event_type="payout_cashback_paid",
               statement_month=statement_month, amount_usd=amount, event_date=ctx.now()[:10])
    left = round(max(0.0, float(acct.get("cashback_balance_usd") or 0) - amount), 2)
    ctx.update("payout_accounts", payout_account_id, cashback_balance_usd=left)
    return str({"status": "settled", "payout_event_id": rid, "statement_month": statement_month, "amount_usd": amount,
                "event_date": ctx.now()[:10], "cashback_balance_usd": left})


@tool(owner="user", rw="write")
def cash_out_to_card_075a5c73(ctx: ToolContext, payout_account_id: str, amount_usd: float) -> str:
    """The shopper cashes out part of their unpaid earnings instantly onto their own Everyday Pay Card. One call books one
    instant cashout of the stated amount on the shopper's payout account, numbered in sequence among the day's cashouts,
    together with its cashout fee entry at 0.00 because card plans charge no cashout fee; the unpaid earnings balance
    shown on the account falls by the amount. Success is a receipt with the cashout reference, the amount and the
    balance left.

    Args:
        payout_account_id: Id class — the shopper payout account number the cashout is drawn from, as the support agent reads it out from the payout account lookup.
        amount_usd: Fixed-format class — the amount loaded onto the card, in USD, a positive number with 2 decimal places (cents), as the support agent states it, booked exactly as given.

    Returns:
        A dictionary rendered as text with: status ("cashed_out" when the cashout was booked); payout_event_id (the
        reference number of the cashout entry); fee_event_id (the reference number of its 0.00 fee entry);
        cashout_number (the integer sequence of this cashout within the day); amount_usd (USD with 2 decimal places);
        event_date (YYYY-MM-DD); available_balance_usd (the unpaid earnings balance left, USD with 2 decimal places).
    """
    acct = (ctx.find("payout_accounts", payout_account_id=payout_account_id) or [{}])[0]
    amount = round(float(amount_usd), 2)
    today = ctx.now()[:10]
    number = len(ctx.find("payout_events", payout_account_id=payout_account_id,
                          event_type="payout_instant_cashout", event_date=today)) + 1
    rid = ctx.make_id("pev_", payout_account_id, "card", amount_usd, today)
    ctx.create("payout_events", rid, payout_event_id=rid, payout_account_id=payout_account_id,
               customer_id=acct.get("customer_id"), event_type="payout_instant_cashout",
               cashout_number=number, amount_usd=amount, event_date=today)
    fid = ctx.make_id("pev_", rid, "fee")
    ctx.create("payout_events", fid, payout_event_id=fid, payout_account_id=payout_account_id,
               customer_id=acct.get("customer_id"), event_type="payout_cashout_fee_charged",
               source_event_id=rid, amount_usd=0.0, event_date=today)
    left = round(float(acct.get("available_balance_usd") or 0) - amount, 2)
    ctx.update("payout_accounts", payout_account_id, available_balance_usd=left)
    return str({"status": "cashed_out", "payout_event_id": rid, "fee_event_id": fid, "cashout_number": number,
                "amount_usd": amount, "event_date": today, "available_balance_usd": left})


@tool(owner="user", rw="write")
def close_payout_account_ca79a9a7(ctx: ToolContext, payout_account_id: str, final_disbursement_usd: float) -> str:
    """The shopper closes their own payout account. One call records the shopper's confirmed closing request, sets the
    account to closed with today's closing date and the reason that the shopper asked for it, books the final
    disbursement of the stated amount out of the unpaid earnings balance to the payout destination on file (labelled
    with today's date as the end of its earnings period), and sets the card cashback balance shown on the closed
    account to 0.00. Success is a receipt with the closing request, the final disbursement and the balance left.

    Args:
        payout_account_id: Id class — the shopper payout account number being closed, as the support agent reads it out from the payout account lookup.
        final_disbursement_usd: Fixed-format class — the final disbursement paid out at closing, in USD, a non-negative number with 2 decimal places (cents), as the support agent states it, booked exactly as given.

    Returns:
        A dictionary rendered as text with: status ("closed" when the account was closed); payout_request_id (the
        reference number of the confirmed closing request); payout_event_id (the reference number of the final
        disbursement entry); final_disbursement_usd (USD with 2 decimal places); closed_date (YYYY-MM-DD);
        available_balance_usd (the unpaid earnings balance left on the closed account, USD with 2 decimal places).
    """
    acct = (ctx.find("payout_accounts", payout_account_id=payout_account_id) or [{}])[0]
    amount = round(float(final_disbursement_usd), 2)
    today = ctx.now()[:10]
    qid = ctx.make_id("prq_", payout_account_id, "close_account")
    ctx.create("payout_requests", qid, payout_request_id=qid, customer_id=acct.get("customer_id"),
               payout_account_id=payout_account_id, request_type="close_account", request_status="confirmed",
               created_at=ctx.now())
    rid = ctx.make_id("pev_", payout_account_id, "final", final_disbursement_usd)
    ctx.create("payout_events", rid, payout_event_id=rid, payout_account_id=payout_account_id,
               customer_id=acct.get("customer_id"), event_type="payout_weekly_deposit",
               payout_period_end=today, amount_usd=amount, event_date=today)
    left = round(float(acct.get("available_balance_usd") or 0) - amount, 2)
    ctx.update("payout_accounts", payout_account_id, status="closed", closed_date=today,
               closure_reason="shopper_requested", available_balance_usd=left, cashback_balance_usd=0.0)
    return str({"status": "closed", "payout_request_id": qid, "payout_event_id": rid,
                "final_disbursement_usd": amount, "closed_date": today, "available_balance_usd": left})

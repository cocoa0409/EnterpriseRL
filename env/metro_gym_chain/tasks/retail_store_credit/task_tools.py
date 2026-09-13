"""Hidden atomic task tools for metro_gym_chain / retail_store_credit.
Path: env/metro_gym_chain/tasks/retail_store_credit/task_tools.py

Every tool here is HIDDEN: its name is discovered only through this difficulty's
retail.extended.yaml (an extended_policies[].target_tool or a workflow step), and is
reached through unlock_agent_discoverable_tool / call_agent_discoverable_tool (or the
user-owned pair) at runtime. Each tool performs exactly one atomic write; every derived
amount (a bonus, a refund, a fee, a reload amount, a redemption amount, a settlement
amount) is computed by the agent from policy, the ledger and the tier before the call,
and is simply landed here as a fixed-format parameter.
"""

from erlbench import ToolContext, tool


@tool(owner="agent", rw="write")
def apply_credit_topup_b1893e39(ctx: ToolContext, credit_account_id: str, credited_amount: float) -> str:
    """Credit a member's pro-shop store-credit account with a top-up that has already been
    priced (face value plus any bonus, capped at the tier's balance ceiling) by the
    representative. Records one top-up transaction on the account's transaction history and
    adds the credited amount to the account's current spendable balance.

    Args:
        credit_account_id: Id class — the store-credit account's own reference number, reachable
            by looking up the member's store-credit account before the call.
        credited_amount: Fixed-format class — the total dollar amount to add to the account's
            spendable balance for this top-up, denominated in USD as the unit, with exactly 2
            decimal places, already rounded to the cent and always zero or positive.

    Returns:
        A confirmation string naming the new transaction's own reference number and the exact
        dollar amount credited. The transaction reference number beginning with "topev_"
        indicates the top-up was recorded and the balance was increased by that amount.
    """
    rid = ctx.make_id("topev_", credit_account_id, credited_amount)
    amt = round(float(credited_amount), 2)
    ctx.create("retail_credit_events", rid, event_id=rid, credit_account_id=credit_account_id,
               customer_id=(ctx.find("retail_credit_accounts", credit_account_id=credit_account_id) or [{}])[0].get("customer_id", ""),
               event_type="retail_credit_topup", event_timestamp=ctx.now(), amount_usd=amt,
               purchase_item="", channel="phone")
    acct = (ctx.find("retail_credit_accounts", credit_account_id=credit_account_id) or [{}])[0]
    ctx.update("retail_credit_accounts", credit_account_id,
               credit_balance=round(float(acct.get("credit_balance", 0)) + amt, 2))
    return f"Top-up {rid} recorded; {amt:.2f} credited to account {credit_account_id}."


@tool(owner="agent", rw="write")
def refund_topup_amount_847aef7e(ctx: ToolContext, credit_account_id: str, refund_amount: float) -> str:
    """Refund a previously credited top-up off a member's pro-shop store-credit account, once
    the representative has already priced the refund from that specific top-up's transaction
    history. Records one refund transaction on the account's transaction history and removes
    the refunded amount from the account's current spendable balance.

    Args:
        credit_account_id: Id class — the store-credit account's own reference number, reachable
            by looking up the member's store-credit account before the call.
        refund_amount: Fixed-format class — the dollar amount to remove from the account's
            spendable balance for this refund, denominated in USD as the unit, with exactly 2
            decimal places, already rounded to the cent and always zero or positive (the tool
            itself subtracts it).

    Returns:
        A confirmation string naming the new transaction's own reference number and the exact
        dollar amount refunded. The transaction reference number beginning with "refev_"
        indicates the refund was recorded and the balance was decreased by that amount.
    """
    rid = ctx.make_id("refev_", credit_account_id, refund_amount)
    amt = round(float(refund_amount), 2)
    ctx.create("retail_credit_events", rid, event_id=rid, credit_account_id=credit_account_id,
               customer_id=(ctx.find("retail_credit_accounts", credit_account_id=credit_account_id) or [{}])[0].get("customer_id", ""),
               event_type="retail_credit_refund", event_timestamp=ctx.now(), amount_usd=-amt,
               purchase_item="", channel="phone")
    acct = (ctx.find("retail_credit_accounts", credit_account_id=credit_account_id) or [{}])[0]
    ctx.update("retail_credit_accounts", credit_account_id,
               credit_balance=round(float(acct.get("credit_balance", 0)) - amt, 2))
    return f"Refund {rid} recorded; {amt:.2f} refunded off account {credit_account_id}."


@tool(owner="agent", rw="write")
def reinstate_suspended_credit_account_88623c40(ctx: ToolContext, credit_account_id: str,
                                                 reinstatement_fee_amount: float) -> str:
    """Lift a fraud-review hold on a member's pro-shop store-credit account, returning it to
    active status, once the representative has already priced any reinstatement fee that
    applies. Changes the account's lifecycle status from suspended to active, and -- when the
    priced fee is greater than zero -- records one transaction on the account's transaction
    history and removes that fee from the account's current spendable balance.

    Args:
        credit_account_id: Id class — the store-credit account's own reference number, reachable
            by looking up the member's store-credit account before the call.
        reinstatement_fee_amount: Fixed-format class — the dollar amount of the reinstatement fee
            to charge, denominated in USD as the unit, with exactly 2 decimal places, already
            rounded to the cent; pass 0.00 when no fee applies.

    Returns:
        A confirmation string naming the account's reference number, its new status, and the fee
        amount charged (0.00 when none). A status of "active" in the confirmation indicates the
        hold was lifted; a fee transaction reference beginning with "rfev_" appears in the
        confirmation whenever the charged fee is greater than zero.
    """
    ctx.update("retail_credit_accounts", credit_account_id, status="active")
    amt = round(float(reinstatement_fee_amount), 2)
    note = ""
    if amt > 0:
        rid = ctx.make_id("rfev_", credit_account_id, amt)
        ctx.create("retail_credit_events", rid, event_id=rid, credit_account_id=credit_account_id,
                   customer_id=(ctx.find("retail_credit_accounts", credit_account_id=credit_account_id) or [{}])[0].get("customer_id", ""),
                   event_type="retail_credit_redeemed", event_timestamp=ctx.now(), amount_usd=-amt,
                   purchase_item="Account reinstatement fee", channel="phone")
        acct = (ctx.find("retail_credit_accounts", credit_account_id=credit_account_id) or [{}])[0]
        ctx.update("retail_credit_accounts", credit_account_id,
                   credit_balance=round(float(acct.get("credit_balance", 0)) - amt, 2))
        note = f" Fee transaction {rid} recorded."
    return f"Account {credit_account_id} reinstated; status active. Fee charged: {amt:.2f}.{note}"


@tool(owner="agent", rw="write")
def process_pending_auto_reload_c7cf4c5c(ctx: ToolContext, credit_account_id: str, reload_amount: float) -> str:
    """Post a store-credit account's automatic reload once the representative has already
    determined, from the tier's auto-reload rule and the account's own standing, whether an
    automatic reload is currently due and for how much. Records one automatic-reload
    transaction on the account's transaction history and adds the reload amount to the
    account's current spendable balance.

    Args:
        credit_account_id: Id class — the store-credit account's own reference number, reachable
            by looking up the member's store-credit account before the call.
        reload_amount: Fixed-format class — the dollar amount to add to the account's spendable
            balance for this automatic reload, denominated in USD as the unit, with exactly 2
            decimal places, already rounded to the cent; pass 0.00 when no reload is currently
            due.

    Returns:
        A confirmation string naming the new transaction's own reference number and the exact
        dollar amount added. The transaction reference number beginning with "arev_" indicates
        the automatic reload was recorded and the balance was increased by that amount (0.00
        leaves the balance unchanged but still logs the check).
    """
    rid = ctx.make_id("arev_", credit_account_id, reload_amount)
    amt = round(float(reload_amount), 2)
    ctx.create("retail_credit_events", rid, event_id=rid, credit_account_id=credit_account_id,
               customer_id=(ctx.find("retail_credit_accounts", credit_account_id=credit_account_id) or [{}])[0].get("customer_id", ""),
               event_type="retail_auto_reload_triggered", event_timestamp=ctx.now(), amount_usd=amt,
               purchase_item="", channel="auto")
    acct = (ctx.find("retail_credit_accounts", credit_account_id=credit_account_id) or [{}])[0]
    ctx.update("retail_credit_accounts", credit_account_id,
               credit_balance=round(float(acct.get("credit_balance", 0)) + amt, 2))
    return f"Automatic reload {rid} recorded; {amt:.2f} added to account {credit_account_id}."


@tool(owner="agent", rw="write")
def redeem_credit_for_purchase_aff0cdd0(ctx: ToolContext, credit_account_id: str, redemption_amount: float,
                                         purchase_item: str) -> str:
    """Redeem store credit off a member's pro-shop store-credit account toward a purchase, once
    the representative has already priced the amount available to redeem today from the
    account's balance and the tier's daily redemption limit. Records one redemption transaction
    on the account's transaction history, naming the purchased item(s), and removes the redeemed
    amount from the account's current spendable balance.

    Args:
        credit_account_id: Id class — the store-credit account's own reference number, reachable
            by looking up the member's store-credit account before the call.
        redemption_amount: Fixed-format class — the dollar amount to remove from the account's
            spendable balance for this redemption, denominated in USD as the unit, with exactly
            2 decimal places, already rounded to the cent and always zero or positive.
        purchase_item: Verbatim class — the pro-shop item or items the member names for this
            purchase, copied character for character from what the member said, preserving
            wording, digits and punctuation, with no translation, normalisation, summarisation,
            addition or deletion (verbatim).

    Returns:
        A confirmation string naming the new transaction's own reference number, the purchased
        item(s) recorded, and the exact dollar amount redeemed. The transaction reference number
        beginning with "rdev_" indicates the redemption was recorded and the balance was
        decreased by that amount.
    """
    rid = ctx.make_id("rdev_", credit_account_id, redemption_amount, purchase_item)
    amt = round(float(redemption_amount), 2)
    ctx.create("retail_credit_events", rid, event_id=rid, credit_account_id=credit_account_id,
               customer_id=(ctx.find("retail_credit_accounts", credit_account_id=credit_account_id) or [{}])[0].get("customer_id", ""),
               event_type="retail_credit_redeemed", event_timestamp=ctx.now(), amount_usd=-amt,
               purchase_item=purchase_item, channel="phone")
    acct = (ctx.find("retail_credit_accounts", credit_account_id=credit_account_id) or [{}])[0]
    ctx.update("retail_credit_accounts", credit_account_id,
               credit_balance=round(float(acct.get("credit_balance", 0)) - amt, 2))
    return f"Redemption {rid} recorded for '{purchase_item}'; {amt:.2f} deducted from account {credit_account_id}."


@tool(owner="user", rw="write")
def confirm_account_closure_988c79ea(ctx: ToolContext, credit_account_id: str) -> str:
    """Let the member themselves confirm, in their own voice, that they are closing their
    pro-shop store-credit account. Changes the account's lifecycle status from active to closed
    and records today's date as the account's closed date.

    Args:
        credit_account_id: Id class — the store-credit account's own reference number, reachable
            by looking up the member's store-credit account before the call.

    Returns:
        A confirmation string naming the account's reference number, its new status, and the
        closed date recorded. A status of "closed" in the confirmation indicates the closure was
        recorded.
    """
    today = ctx.now()[:10]
    ctx.update("retail_credit_accounts", credit_account_id, status="closed", closed_date=today)
    return f"Account {credit_account_id} closed as of {today}; status closed."


@tool(owner="agent", rw="write")
def issue_closure_refund_05905e3c(ctx: ToolContext, credit_account_id: str, settlement_amount: float) -> str:
    """Pay out (or forfeit) the remaining balance on a member's just-closed pro-shop store-credit
    account, once the representative has already priced the final settlement from the account's
    balance and closure policy. Records one refund transaction on the account's transaction
    history for the settled amount and removes that amount from the account's spendable balance.

    Args:
        credit_account_id: Id class — the store-credit account's own reference number, reachable
            by looking up the member's store-credit account before the call.
        settlement_amount: Fixed-format class — the dollar amount to remove from the account's
            spendable balance as the final closure settlement, denominated in USD as the unit,
            with exactly 2 decimal places, already rounded to the cent; pass 0.00 when nothing
            is refunded.

    Returns:
        A confirmation string naming the new transaction's own reference number and the exact
        dollar amount settled. The transaction reference number beginning with "clrev_"
        indicates the closure settlement was recorded and the balance was decreased by that
        amount (0.00 still logs the settlement with no balance change).
    """
    rid = ctx.make_id("clrev_", credit_account_id, settlement_amount)
    amt = round(float(settlement_amount), 2)
    ctx.create("retail_credit_events", rid, event_id=rid, credit_account_id=credit_account_id,
               customer_id=(ctx.find("retail_credit_accounts", credit_account_id=credit_account_id) or [{}])[0].get("customer_id", ""),
               event_type="retail_credit_refund", event_timestamp=ctx.now(), amount_usd=-amt,
               purchase_item="", channel="phone")
    acct = (ctx.find("retail_credit_accounts", credit_account_id=credit_account_id) or [{}])[0]
    ctx.update("retail_credit_accounts", credit_account_id,
               credit_balance=round(float(acct.get("credit_balance", 0)) - amt, 2))
    return f"Closure settlement {rid} recorded; {amt:.2f} settled off account {credit_account_id}."

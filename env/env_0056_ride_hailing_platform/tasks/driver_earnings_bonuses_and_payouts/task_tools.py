"""Hidden task tools for the driver_earnings_bonuses_and_payouts difficulty of
env_0056_ride_hailing_platform (Wayfare Mobility driver earnings and Wayfare Pro).

Each tool performs one atomic write on a driver's earnings account, its earnings statement or its
incentive offers. The tools never judge eligibility, never aggregate history and never compute an
amount: every amount is passed in already worked out, and the tool records it as given.
"""

from erlbench import ToolContext, tool


class _Calendar:
    """Helpers: pure calendar arithmetic on 'YYYY-MM-DD' strings and the earnings account read."""

    @staticmethod
    def ordinal(day: str) -> int:
        y, m, d = (int(part) for part in str(day)[:10].split("-"))
        month_days = [31, 29 if (y % 4 == 0 and (y % 100 != 0 or y % 400 == 0)) else 28,
                      31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
        prior = y - 1
        return prior * 365 + prior // 4 - prior // 100 + prior // 400 + sum(month_days[:m - 1]) + d

    @staticmethod
    def from_ordinal(n: int) -> str:
        y = max(1, (n * 400) // 146097)
        while _Calendar.ordinal(f"{y + 1:04d}-01-01") <= n:
            y += 1
        while _Calendar.ordinal(f"{y:04d}-01-01") > n:
            y -= 1
        leap = y % 4 == 0 and (y % 100 != 0 or y % 400 == 0)
        month_days = [31, 29 if leap else 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
        rest = n - _Calendar.ordinal(f"{y:04d}-01-01") + 1
        m = 1
        while rest > month_days[m - 1]:
            rest -= month_days[m - 1]
            m += 1
        return f"{y:04d}-{m:02d}-{rest:02d}"

    @staticmethod
    def monday_of(day: str) -> str:
        n = _Calendar.ordinal(day)
        # ordinal 1 (0001-01-01) is a Monday, so (n - 1) % 7 is the weekday with Monday = 0
        return _Calendar.from_ordinal(n - ((n - 1) % 7))

    @staticmethod
    def account(ctx: ToolContext, earnings_account_id: str) -> dict:
        rows = ctx.find("earnings_accounts", earnings_account_id=earnings_account_id)
        return rows[0] if rows else {}


@tool(owner="agent", rw="write")
def lift_payout_hold_7e61ef01(ctx: ToolContext, earnings_account_id: str, payout_amount: float) -> str:
    """Lift the payout hold on a driver's earnings account and send the hold-release payout.

    The agent uses this on a driver's earnings account that is on payout hold. One call sets the
    account back to active with no hold reason, so scheduled payouts and instant cashouts work
    again, and sends one hold-release payout of the stated amount to the payout method on file:
    the payout appears on the driver's earnings statement as a hold-release payout dated today,
    credited to the earnings week that contains today, and the available balance on the account
    goes down by the amount sent. When the stated amount is 0.00 the hold is lifted and no payout
    entry is written. Success is the receipt below with status "active".

    Args:
        earnings_account_id: Id class — the reference number of the driver's earnings account
            whose payout hold is being lifted, as shown by the earnings account lookup for the
            verified driver.
        payout_amount: Fixed-format class — the hold-release payout to send, in USD, a
            non-negative amount with 2 decimal places (rounded half up to the cent), for
            example 87.40; 0.00 sends nothing.

    Returns:
        A dictionary rendered as text with: "earnings_account_id" (the account reference
        number), "status" (the account status after the call, "active" on success),
        "payout_hold_reason" (now "none"), "payout_entry_id" (the reference number of the
        hold-release payout on the earnings statement, or "" when 0.00 was sent),
        "payout_amount" (the USD amount sent, 2 decimal places), "payout_week_start" (the
        Monday of the earnings week the payout is booked to, YYYY-MM-DD) and
        "available_balance" (the USD balance left on the account, 2 decimal places).
    """
    acc = _Calendar.account(ctx, earnings_account_id)
    amount = round(float(payout_amount), 2)
    now = ctx.now()
    today = now[:10]
    week_start = _Calendar.monday_of(today)
    balance = round(float(acc.get("available_balance") or 0) - amount, 2)
    ctx.update("earnings_accounts", earnings_account_id, status="active", payout_hold_reason="none",
               available_balance=round(float(acc.get("available_balance") or 0) - round(float(payout_amount), 2), 2))
    entry_id = ""
    if amount > 0:
        entry_id = ctx.make_id("ern_", earnings_account_id, payout_amount, "hold_release")
        ctx.create("earnings_ledger", entry_id, earnings_entry_id=entry_id,
                   earnings_account_id=earnings_account_id, customer_id=acc.get("customer_id"),
                   event_type="earnings_weekly_payout", entry_date=today, posted_at=now,
                   amount=-round(float(payout_amount), 2), points=0, trip_id=None,
                   damage_assessment_id=None, bonus_offer_id=None, rental_charge_id=None,
                   original_entry_id="", adjustment_reason="none", points_basis="none",
                   points_period_start="", payout_week_start=week_start,
                   payout_type="hold_release", cashout_channel="none")
    return str({"earnings_account_id": earnings_account_id, "status": "active",
                "payout_hold_reason": "none", "payout_entry_id": entry_id,
                "payout_amount": f"{amount:.2f}", "payout_week_start": week_start,
                "available_balance": f"{balance:.2f}"})


@tool(owner="user", rw="write")
def opt_in_to_guarantee_dc9f134f(ctx: ToolContext, earnings_account_id: str, bonus_offer_id: str,
                                 guaranteed_amount: float) -> str:
    """Opt the driver in to an earnings guarantee offer and record the guarantee locked for it.

    The driver uses this on one earnings guarantee offer made to their own earnings account. One
    call records the driver's opt-in to that offer, dated now, carrying the offer's market, window
    and required online time, together with the locked guarantee: the guaranteed amount the driver
    is held to for that window. The opt-in then shows among the driver's incentive offers and
    opt-ins. Success is the receipt below with status "opted_in".

    Args:
        earnings_account_id: Id class — the reference number of the driver's own earnings account
            the offer was made to, as shown by the earnings account lookup.
        bonus_offer_id: Id class — the reference number of the earnings guarantee offer being
            opted into, as shown by the incentive offer lookup for the driver's account.
        guaranteed_amount: Fixed-format class — the locked guarantee recorded on the opt-in, in
            USD, a positive amount with 2 decimal places (rounded half up to the cent), for
            example 215.30.

    Returns:
        A dictionary rendered as text with: "optin_id" (the reference number of the recorded
        opt-in), "source_offer_id" (the offer opted into), "status" ("opted_in" on success),
        "market" (the offer's market code), "window_start" and "window_end" (the offer's window,
        YYYY-MM-DD HH:MM:SS with zone) and "guaranteed_amount" (the locked guarantee in USD,
        2 decimal places).
    """
    acc = _Calendar.account(ctx, earnings_account_id)
    offers = ctx.find("bonus_offers", bonus_offer_id=bonus_offer_id)
    offer = offers[0] if offers else {}
    amount = round(float(guaranteed_amount), 2)
    optin_id = ctx.make_id("bof_", earnings_account_id, bonus_offer_id, guaranteed_amount)
    ctx.create("bonus_offers", optin_id, bonus_offer_id=optin_id, earnings_account_id=earnings_account_id,
               customer_id=acc.get("customer_id"), event_type="earnings_bonus_optin", issued_at=ctx.now(),
               incentive_type=offer.get("incentive_type", "earnings_guarantee"), market=offer.get("market", ""),
               window_start=offer.get("window_start", ""), window_end=offer.get("window_end", ""),
               target_trip_count=0, reward_amount=0.0, guaranteed_amount=round(float(guaranteed_amount), 2),
               required_online_minutes=int(offer.get("required_online_minutes") or 0),
               source_offer_id=bonus_offer_id, referred_customer_id=None)
    return str({"optin_id": optin_id, "source_offer_id": bonus_offer_id, "status": "opted_in",
                "market": offer.get("market", ""), "window_start": offer.get("window_start", ""),
                "window_end": offer.get("window_end", ""), "guaranteed_amount": f"{amount:.2f}"})


@tool(owner="agent", rw="write")
def credit_quest_reward_07fce82e(ctx: ToolContext, earnings_account_id: str, bonus_offer_id: str,
                                 amount: float) -> str:
    """Credit an earned quest reward to a driver's earnings statement.

    The agent uses this for one quest offer made to a driver's earnings account. One call posts a
    bonus entry for that offer, dated now, carrying the offer reference and the stated amount, and
    raises the available balance on the account by that amount; the bonus shows on the driver's
    earnings statement at once. Success is the receipt below with status "credited".

    Args:
        earnings_account_id: Id class — the reference number of the driver's earnings account the
            quest offer was made to, as shown by the earnings account lookup.
        bonus_offer_id: Id class — the reference number of the quest offer being paid, as shown
            by the incentive offer lookup for the driver's account.
        amount: Fixed-format class — the quest reward credited, in USD, a positive amount with 2
            decimal places (rounded half up to the cent), for example 88.40.

    Returns:
        A dictionary rendered as text with: "bonus_entry_id" (the reference number of the bonus
        entry on the earnings statement), "bonus_offer_id" (the offer paid), "status"
        ("credited" on success), "amount" (USD, 2 decimal places), "entry_date" (YYYY-MM-DD) and
        "available_balance" (the USD balance after the credit, 2 decimal places).
    """
    acc = _Calendar.account(ctx, earnings_account_id)
    credited = round(float(amount), 2)
    now = ctx.now()
    balance = round(float(acc.get("available_balance") or 0) + credited, 2)
    entry_id = ctx.make_id("ern_", earnings_account_id, bonus_offer_id, amount)
    ctx.create("earnings_ledger", entry_id, earnings_entry_id=entry_id, earnings_account_id=earnings_account_id,
               customer_id=acc.get("customer_id"), event_type="earnings_bonus_credit", entry_date=now[:10],
               posted_at=now, amount=round(float(amount), 2), points=0, trip_id=None, damage_assessment_id=None,
               bonus_offer_id=bonus_offer_id, rental_charge_id=None, original_entry_id="",
               adjustment_reason="none", points_basis="none", points_period_start="", payout_week_start="",
               payout_type="none", cashout_channel="none")
    ctx.update("earnings_accounts", earnings_account_id,
               available_balance=round(float(acc.get("available_balance") or 0) + round(float(amount), 2), 2))
    return str({"bonus_entry_id": entry_id, "bonus_offer_id": bonus_offer_id, "status": "credited",
                "amount": f"{credited:.2f}", "entry_date": now[:10], "available_balance": f"{balance:.2f}"})


@tool(owner="user", rw="write")
def cash_out_to_debit_card_82ffed45(ctx: ToolContext, earnings_account_id: str, amount: float,
                                    fee_amount: float) -> str:
    """Cash out driver earnings instantly to the driver's external debit card.

    The driver uses this on their own earnings account. One call makes one instant cashout of the
    stated amount to the external debit card on file and books its cashout fee: the earnings
    statement shows the cashout and its fee entry, both dated now and sent to the external debit
    card, and the available balance goes down by the amount plus the fee. Success is the receipt
    below with status "sent".

    Args:
        earnings_account_id: Id class — the reference number of the driver's own earnings account
            being cashed out from, as shown by the earnings account lookup.
        amount: Fixed-format class — the amount cashed out to the external debit card, in USD, a
            positive amount with 2 decimal places (rounded half up to the cent), for example 412.65.
        fee_amount: Fixed-format class — the cashout fee booked for this cashout, in USD, a
            non-negative amount with 2 decimal places (rounded half up to the cent); 0.00 when
            the cashout is free.

    Returns:
        A dictionary rendered as text with: "cashout_entry_id" (the reference number of the
        cashout on the earnings statement), "fee_entry_id" (the reference number of its fee
        entry), "status" ("sent" on success), "amount" and "fee_amount" (USD, 2 decimal places),
        "cashout_channel" ("external_debit_card") and "available_balance" (the USD balance
        after the cashout and fee, 2 decimal places).
    """
    acc = _Calendar.account(ctx, earnings_account_id)
    cash = round(float(amount), 2)
    fee = round(float(fee_amount), 2)
    now = ctx.now()
    balance = round(float(acc.get("available_balance") or 0) - cash - fee, 2)
    cash_id = ctx.make_id("ern_", earnings_account_id, amount, fee_amount, "cashout")
    fee_id = ctx.make_id("ern_", earnings_account_id, amount, fee_amount, "cashout_fee")
    ctx.create("earnings_ledger", cash_id, earnings_entry_id=cash_id, earnings_account_id=earnings_account_id,
               customer_id=acc.get("customer_id"), event_type="earnings_instant_cashout", entry_date=now[:10],
               posted_at=now, amount=-round(float(amount), 2), points=0, trip_id=None, damage_assessment_id=None,
               bonus_offer_id=None, rental_charge_id=None, original_entry_id="", adjustment_reason="none",
               points_basis="none", points_period_start="", payout_week_start="", payout_type="none",
               cashout_channel="external_debit_card")
    ctx.create("earnings_ledger", fee_id, earnings_entry_id=fee_id, earnings_account_id=earnings_account_id,
               customer_id=acc.get("customer_id"), event_type="earnings_instant_cashout_fee", entry_date=now[:10],
               posted_at=now, amount=-round(float(fee_amount), 2), points=0, trip_id=None,
               damage_assessment_id=None, bonus_offer_id=None, rental_charge_id=None, original_entry_id=cash_id,
               adjustment_reason="none", points_basis="none", points_period_start="", payout_week_start="",
               payout_type="none", cashout_channel="external_debit_card")
    ctx.update("earnings_accounts", earnings_account_id,
               available_balance=round(float(acc.get("available_balance") or 0) - round(float(amount), 2)
                                       - round(float(fee_amount), 2), 2))
    return str({"cashout_entry_id": cash_id, "fee_entry_id": fee_id, "status": "sent",
                "amount": f"{cash:.2f}", "fee_amount": f"{fee:.2f}", "cashout_channel": "external_debit_card",
                "available_balance": f"{balance:.2f}"})

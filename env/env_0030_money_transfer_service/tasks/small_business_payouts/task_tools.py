"""Hidden task tools of the small_business_payouts difficulty (Paloma Business accounts).

Each tool lands one atomic business write with the values the caller has already worked out; none of
them checks eligibility, prerequisites or amounts. Reached only through unlock_* -> call_*.
"""

from erlbench import ToolContext, tool


_LEDGER_DEFAULTS = {"allowance_units": 0, "fee_type": "none", "fee_refund_reason": "none",
                    "billing_period_start": "", "payout_reference": "", "deposit_method": "none",
                    "deposit_reference": "", "seq_in_period": 0, "credit_back_reason": "none",
                    "related_entry_id": ""}


@tool(owner="agent", rw="write")
def collect_overdue_subscription_325cf5bc(ctx: ToolContext, business_account_id: str, amount_usd: float) -> str:
    """Collect the subscription charge of the current billing period from a past-due Paloma Business
    account's balance and bring the account back into good standing. One call books one subscription
    fee entry for the account's current billing period with the amount given, takes that amount off
    the business balance, sets the account status to active and clears its past-due date. Afterwards
    the owner sees the subscription fee on the balance history and the account shown as active.

    Args:
        business_account_id: Id class — the Paloma Business account reference number of the account being
            brought back into good standing, as returned by the Paloma Business account lookup.
        amount_usd: Fixed-format class — the subscription charge being collected for the current billing
            period, in USD as a positive amount with 2 decimal places (already rounded half up to
            the cent).

    Returns:
        A text receipt of a dictionary with: ledger_entry_id (reference of the subscription fee entry
        booked), business_account_id (the account), billing_period_start (YYYY-MM-DD start of the period the
        fee was booked for), amount_usd (USD amount collected, 2 decimals), status (the resulting account
        status, active), balance_usd (resulting USD balance, 2 decimals). The presence of
        ledger_entry_id and status active indicates the collection completed.
    """
    found = ctx.find("business_accounts", business_account_id=business_account_id)
    acct = found[0] if found else {}
    amount = round(float(amount_usd), 2)
    period_start = acct.get("current_period_start", "")
    rid = ctx.make_id("bl_", business_account_id, amount_usd)
    row = dict(_LEDGER_DEFAULTS)
    row.update(fee_type="subscription_fee", billing_period_start=period_start)
    ctx.create("business_ledger", rid, ledger_entry_id=rid, business_account_id=business_account_id,
               customer_id=acct.get("customer_id", ""), event_type="business_fee_charged",
               entry_date=ctx.now()[:10], amount_usd=amount, **row)
    balance = round(float(acct.get("balance_usd") or 0) - amount, 2)
    ctx.update("business_accounts", business_account_id, status="active", past_due_since="",
               balance_usd=balance)
    return str({"ledger_entry_id": rid, "business_account_id": business_account_id,
                "billing_period_start": period_start, "amount_usd": amount,
                "status": "active", "balance_usd": balance})


@tool(owner="user", rw="write")
def schedule_plan_downgrade_6c5bcb1c(ctx: ToolContext, business_account_id: str, lower_plan: str,
                                     change_date: str, early_termination_fee_usd: float) -> str:
    """The business owner schedules their own Paloma Business account to move to a lower plan and pays
    the early termination charge for leaving the committed plan early. One call records the lower plan
    and the date it takes effect on the account, books one early termination fee entry for the current
    billing period with the amount given, and takes that amount off the business balance. Afterwards the
    owner sees the scheduled plan and change date on the account and the early termination fee on the
    balance history, and the lower plan applies from the change date.

    Args:
        business_account_id: Id class — the Paloma Business account reference number of the owner's
            account, as returned by the Paloma Business account lookup.
        lower_plan: Enum class — the official name of the lower plan the owner moves to, one of:
            Paloma Business Starter — the owner moves down to the Starter plan;
            Paloma Business Essentials — the owner moves down to the Essentials plan;
            Paloma Business Growth — the owner moves down to the Growth plan;
            Paloma Business Pro — the owner moves down to the Pro plan;
            Paloma Business Scale — the owner moves down to the Scale plan from Enterprise;
            Paloma Business Enterprise — never lower than another plan, so not used for a downgrade.
        change_date: Fixed-format class — the date the lower plan takes effect, in YYYY-MM-DD.
        early_termination_fee_usd: Fixed-format class — the early termination charge being paid, in USD as
            a non-negative amount with 2 decimal places (already rounded half up to the cent).

    Returns:
        A text receipt of a dictionary with: ledger_entry_id (reference of the early termination fee entry
        booked), business_account_id (the account), scheduled_plan (the lower plan now scheduled),
        scheduled_change_date (YYYY-MM-DD date it takes effect), early_termination_fee_usd (USD charged,
        2 decimals), balance_usd (resulting USD balance, 2 decimals). A scheduled_plan equal to the
        chosen plan indicates the downgrade is scheduled.
    """
    found = ctx.find("business_accounts", business_account_id=business_account_id)
    acct = found[0] if found else {}
    fee = round(float(early_termination_fee_usd), 2)
    plan_name = str(lower_plan).strip()
    effective = str(change_date)[:10]
    rid = ctx.make_id("bl_", business_account_id, lower_plan, change_date, early_termination_fee_usd)
    row = dict(_LEDGER_DEFAULTS)
    row.update(fee_type="early_termination_fee", billing_period_start=acct.get("current_period_start", ""))
    ctx.create("business_ledger", rid, ledger_entry_id=rid, business_account_id=business_account_id,
               customer_id=acct.get("customer_id", ""), event_type="business_fee_charged",
               entry_date=ctx.now()[:10], amount_usd=fee, **row)
    balance = round(float(acct.get("balance_usd") or 0) - fee, 2)
    ctx.update("business_accounts", business_account_id, scheduled_variant_name=plan_name,
               scheduled_change_date=effective, balance_usd=balance)
    return str({"ledger_entry_id": rid, "business_account_id": business_account_id,
                "scheduled_plan": plan_name, "scheduled_change_date": effective,
                "early_termination_fee_usd": fee, "balance_usd": balance})


@tool(owner="agent", rw="write")
def charge_extra_seats_0d292d98(ctx: ToolContext, business_account_id: str, seq_in_period: int,
                                amount_usd: float) -> str:
    """Charge a Paloma Business account for extra user seats in its current billing period. One call books
    one extra seat fee entry for the account's current billing period with the amount and in-period
    sequence number given, and takes that amount off the business balance. Afterwards the owner sees the
    extra seat fee on the balance history and a balance lowered by it.

    Args:
        business_account_id: Id class — the Paloma Business account reference number of the account being
            charged, as returned by the Paloma Business account lookup.
        seq_in_period: Fixed-format class — the sequence number of this mid-period seat charge within the
            current billing period, an integer count starting at 1.
        amount_usd: Fixed-format class — the extra seat charge, in USD as a non-negative amount with 2 decimal
            places (already rounded to the cent).

    Returns:
        A text receipt of a dictionary with: ledger_entry_id (reference of the extra seat fee entry booked),
        business_account_id (the account), billing_period_start (YYYY-MM-DD start of the period charged),
        seq_in_period (integer sequence in the period), amount_usd (USD charged, 2 decimals), balance_usd
        (resulting USD balance, 2 decimals). The presence of ledger_entry_id indicates the charge is booked.
    """
    found = ctx.find("business_accounts", business_account_id=business_account_id)
    acct = found[0] if found else {}
    amount = round(float(amount_usd), 2)
    seq = int(seq_in_period)
    period_start = acct.get("current_period_start", "")
    rid = ctx.make_id("bl_", business_account_id, seq_in_period, amount_usd)
    row = dict(_LEDGER_DEFAULTS)
    row.update(fee_type="extra_seat_fee", billing_period_start=period_start, seq_in_period=seq)
    ctx.create("business_ledger", rid, ledger_entry_id=rid, business_account_id=business_account_id,
               customer_id=acct.get("customer_id", ""), event_type="business_fee_charged",
               entry_date=ctx.now()[:10], amount_usd=amount, **row)
    balance = round(float(acct.get("balance_usd") or 0) - amount, 2)
    ctx.update("business_accounts", business_account_id, balance_usd=balance)
    return str({"ledger_entry_id": rid, "business_account_id": business_account_id,
                "billing_period_start": period_start, "seq_in_period": seq, "amount_usd": amount,
                "balance_usd": balance})


@tool(owner="agent", rw="write")
def settle_upgrade_proration_4280c277(ctx: ToolContext, business_account_id: str, amount_usd: float) -> str:
    """Settle the proration of a plan upgrade made inside a Paloma Business account's current billing
    period. One call books one proration charge entry for the account's current billing period with the
    amount given and takes that amount off the business balance. Afterwards the owner sees the proration
    charge on the balance history and a balance lowered by it.

    Args:
        business_account_id: Id class — the Paloma Business account reference number of the upgraded
            account, as returned by the Paloma Business account lookup.
        amount_usd: Fixed-format class — the proration charge being settled, in USD as a non-negative amount
            with 2 decimal places (already rounded half up to the cent).

    Returns:
        A text receipt of a dictionary with: ledger_entry_id (reference of the proration charge entry
        booked), business_account_id (the account), billing_period_start (YYYY-MM-DD start of the period
        settled), amount_usd (USD charged, 2 decimals), balance_usd (resulting USD balance, 2 decimals). The
        presence of ledger_entry_id indicates the proration is settled.
    """
    found = ctx.find("business_accounts", business_account_id=business_account_id)
    acct = found[0] if found else {}
    amount = round(float(amount_usd), 2)
    period_start = acct.get("current_period_start", "")
    rid = ctx.make_id("bl_", business_account_id, "proration", amount_usd)
    row = dict(_LEDGER_DEFAULTS)
    row.update(fee_type="proration_charge", billing_period_start=period_start)
    ctx.create("business_ledger", rid, ledger_entry_id=rid, business_account_id=business_account_id,
               customer_id=acct.get("customer_id", ""), event_type="business_fee_charged",
               entry_date=ctx.now()[:10], amount_usd=amount, **row)
    balance = round(float(acct.get("balance_usd") or 0) - amount, 2)
    ctx.update("business_accounts", business_account_id, balance_usd=balance)
    return str({"ledger_entry_id": rid, "business_account_id": business_account_id,
                "billing_period_start": period_start, "amount_usd": amount, "balance_usd": balance})


@tool(owner="agent", rw="write")
def charge_card_deposit_fee_e69fd8f7(ctx: ToolContext, business_account_id: str, deposit_reference: str,
                                     fee_usd: float) -> str:
    """Charge the deposit fee of one debit-card deposit on a Paloma Business account. One call books one
    deposit fee entry tied to the deposit reference given, for the account's current billing period, and
    takes the fee off the business balance. Afterwards the owner sees the deposit fee next to that deposit
    on the balance history and a balance lowered by it.

    Args:
        business_account_id: Id class — the Paloma Business account reference number of the account that
            received the deposit, as returned by the Paloma Business account lookup.
        deposit_reference: Verbatim class — the reference of the debit-card deposit exactly as the balance
            history shows it, copied character for character with no change (verbatim).
        fee_usd: Fixed-format class — the deposit fee, in USD as a non-negative amount with 2 decimal places
            (already rounded half up to the cent).

    Returns:
        A text receipt of a dictionary with: ledger_entry_id (reference of the deposit fee entry booked),
        business_account_id (the account), deposit_reference (the deposit the fee belongs to), fee_usd (USD
        charged, 2 decimals), balance_usd (resulting USD balance, 2 decimals). The presence of
        ledger_entry_id indicates the fee is booked.
    """
    found = ctx.find("business_accounts", business_account_id=business_account_id)
    acct = found[0] if found else {}
    fee = round(float(fee_usd), 2)
    rid = ctx.make_id("bl_", business_account_id, deposit_reference, fee_usd)
    row = dict(_LEDGER_DEFAULTS)
    row.update(fee_type="deposit_fee", billing_period_start=acct.get("current_period_start", ""),
               deposit_reference=deposit_reference)
    ctx.create("business_ledger", rid, ledger_entry_id=rid, business_account_id=business_account_id,
               customer_id=acct.get("customer_id", ""), event_type="business_fee_charged",
               entry_date=ctx.now()[:10], amount_usd=fee, **row)
    balance = round(float(acct.get("balance_usd") or 0) - fee, 2)
    ctx.update("business_accounts", business_account_id, balance_usd=balance)
    return str({"ledger_entry_id": rid, "business_account_id": business_account_id,
                "deposit_reference": deposit_reference, "fee_usd": fee, "balance_usd": balance})


@tool(owner="user", rw="write")
def withdraw_business_balance_ad66ed9d(ctx: ToolContext, business_account_id: str, seq_in_period: int,
                                       amount_usd: float) -> str:
    """The business owner withdraws money from their own Paloma Business balance to the business's
    verified US bank account. One call books one withdrawal for the account's current billing period with
    the amount and in-period sequence number given and takes that amount off the business balance.
    Afterwards the owner sees the withdrawal on the balance history and a balance lowered by it; the money
    is on its way to the business's verified US bank account.

    Args:
        business_account_id: Id class — the Paloma Business account reference number of the owner's
            account, as returned by the Paloma Business account lookup.
        seq_in_period: Fixed-format class — the sequence number of this withdrawal within the current billing
            period, an integer count starting at 1.
        amount_usd: Fixed-format class — the amount withdrawn, in USD as a positive amount with 2 decimal
            places (already rounded half up to the cent).

    Returns:
        A text receipt of a dictionary with: ledger_entry_id (reference of the withdrawal entry booked),
        business_account_id (the account), billing_period_start (YYYY-MM-DD start of the period),
        seq_in_period (integer sequence in the period), amount_usd (USD withdrawn, 2 decimals), balance_usd
        (resulting USD balance, 2 decimals). The presence of ledger_entry_id indicates the withdrawal is
        booked.
    """
    found = ctx.find("business_accounts", business_account_id=business_account_id)
    acct = found[0] if found else {}
    amount = round(float(amount_usd), 2)
    seq = int(seq_in_period)
    period_start = acct.get("current_period_start", "")
    rid = ctx.make_id("bl_", business_account_id, "withdrawal", seq_in_period, amount_usd)
    row = dict(_LEDGER_DEFAULTS)
    row.update(billing_period_start=period_start, seq_in_period=seq)
    ctx.create("business_ledger", rid, ledger_entry_id=rid, business_account_id=business_account_id,
               customer_id=acct.get("customer_id", ""), event_type="business_balance_withdrawn",
               entry_date=ctx.now()[:10], amount_usd=amount, **row)
    balance = round(float(acct.get("balance_usd") or 0) - amount, 2)
    ctx.update("business_accounts", business_account_id, balance_usd=balance)
    return str({"ledger_entry_id": rid, "business_account_id": business_account_id,
                "billing_period_start": period_start, "seq_in_period": seq, "amount_usd": amount,
                "balance_usd": balance})

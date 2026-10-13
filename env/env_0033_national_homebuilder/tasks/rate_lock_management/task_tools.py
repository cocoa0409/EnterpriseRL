"""Hidden task tools for rate_lock_management (Builder Extended Rate Lock, Calloway Home Mortgage).

Each tool performs exactly one atomic write on a rate lock or its ledger, taking values the agent has
already worked out from the lock charter. No tool checks a business precondition or computes a fee.
"""

from erlbench import ToolContext, tool


@tool(owner="agent", rw="write")
def relock_expired_lock_4b9eda82(ctx: ToolContext, lock_id: str, relock_fee: float, relocked_rate: float,
                                 new_expiration_date: str) -> str:
    """Relock a Builder Extended Rate Lock that has expired. One call puts the lock back in force: its
    status becomes locked, the relocked rate and the new last day of the lock are written, the number of
    relocks used goes up by one, and a relock fee charge is booked on the lock ledger with its own printed
    charge number and added to the lock charges owed. The buyer can see the lock as locked at
    the relocked rate through the new expiration date, with the relock fee among the charges collected at
    funding. The receipt below confirms the relock was written.

    Args:
        lock_id: Id class — the reference number of the expired Builder Extended Rate Lock being relocked, as returned by the rate lock finder for this buyer.
        relock_fee: Fixed-format class — the relock fee charged for this relock, in USD, a plain number rounded to 2 decimal places (half up, to the cent), no currency sign.
        relocked_rate: Fixed-format class — the interest rate the lock is relocked at, written as percent, 3 decimal places, e.g. 6.375 (no percent sign).
        new_expiration_date: Fixed-format class — the last calendar day the relocked lock is in force, written YYYY-MM-DD.

    Returns:
        A dictionary rendered as text with: status ("relocked" on success); lock_id (the lock reference
        number); locked_rate (percent, 3 decimal places); lock_expiration_date (YYYY-MM-DD);
        relocks_used (integer count including this relock); charge_reference (the printed charge number of the
        relock fee, e.g. LCK-CHG-4123); charge_amount (USD, 2 decimal places); charges_due (USD, 2 decimal
        places, lock charges owed including this fee).
    """
    lock = (ctx.find("rate_locks", lock_id=lock_id) or [{}])[0]
    fee = round(float(relock_fee), 2)
    rid = ctx.make_id("lev_", lock_id, "relock_fee", fee, relocked_rate, new_expiration_date)
    ref = f"LCK-CHG-4{int(rid[-6:], 16) % 1000:03d}"
    ctx.create("lock_events", rid, lock_event_id=rid, lock_id=lock_id, customer_id=lock.get("customer_id"),
               event_type="lock_charge_assessed", amount=fee, charge_type="relock_fee",
               charge_reference=ref, event_date=ctx.now()[:10])
    relocks = int(lock.get("relocks_used") or 0) + 1
    due = round(float(lock.get("charges_due") or 0) + fee, 2)
    ctx.update("rate_locks", lock_id, status="locked", locked_rate=round(float(relocked_rate), 3),
               lock_expiration_date=str(new_expiration_date), relocks_used=relocks, charges_due=due)
    return str({"status": "relocked", "lock_id": lock_id, "locked_rate": round(float(relocked_rate), 3),
                "lock_expiration_date": str(new_expiration_date), "relocks_used": relocks,
                "charge_reference": ref, "charge_amount": fee, "charges_due": due})


@tool(owner="user", rw="write")
def extend_rate_lock_1be9088d(ctx: ToolContext, lock_id: str, extension_days: int, increments: int) -> str:
    """The buyer extends their own Builder Extended Rate Lock. One call moves the lock's last day in force
    later by the extension days given, adds the increments to the extension increments used and adds the
    days to the extension days used on the lock. The buyer can see the new expiration date on
    the lock. The receipt below
    confirms the extension was written.

    Args:
        lock_id: Id class — the reference number of the buyer's Builder Extended Rate Lock, as the agent read it from the rate lock finder and passed to the buyer.
        extension_days: Fixed-format class — the calendar days this extension adds to the lock, an integer >= 0 (whole days, no decimals).
        increments: Fixed-format class — the number of extension increments this extension uses, an integer >= 0.

    Returns:
        A dictionary rendered as text with: status ("extended" on success); lock_id (the lock reference
        number); previous_expiration_date (YYYY-MM-DD, the date replaced) and lock_expiration_date (YYYY-MM-DD, the new date);
        extensions_used and extension_days_used (integer totals on the lock including this extension).
    """
    lock = (ctx.find("rate_locks", lock_id=lock_id) or [{}])[0]
    prev = str(lock.get("lock_expiration_date") or ctx.now()[:10])
    y, m, d = (int(x) for x in prev[:10].split("-"))
    y -= m <= 2
    era = y // 400
    yoe = y - era * 400
    doe = yoe * 365 + yoe // 4 - yoe // 100 + (153 * (m + (-3 if m > 2 else 9)) + 2) // 5 + d - 1
    n = era * 146097 + doe + int(extension_days)
    era = n // 146097
    doe = n - era * 146097
    yoe = (doe - doe // 1460 + doe // 36524 - doe // 146096) // 365
    doy = doe - (365 * yoe + yoe // 4 - yoe // 100)
    mp = (5 * doy + 2) // 153
    d = doy - (153 * mp + 2) // 5 + 1
    m = mp + (3 if mp < 10 else -9)
    y = yoe + era * 400 + (m <= 2)
    new = f"{y:04d}-{m:02d}-{d:02d}"
    used = int(lock.get("extensions_used") or 0) + int(increments)
    days = int(lock.get("extension_days_used") or 0) + int(extension_days)
    ctx.update("rate_locks", lock_id, lock_expiration_date=new, extensions_used=used, extension_days_used=days)
    return str({"status": "extended", "lock_id": lock_id, "previous_expiration_date": prev,
                "lock_expiration_date": new, "extensions_used": used, "extension_days_used": days})


@tool(owner="agent", rw="write")
def assess_extension_charge_644b0045(ctx: ToolContext, lock_id: str, amount: float, extension_days: int) -> str:
    """Book the extension fee charge for an extension on a Builder Extended Rate Lock. One call writes one
    extension fee charge on the lock ledger with its own printed charge number and the extension days it
    prices, and adds the amount to the lock charges owed. The buyer can see the charge number
    and amount among the lock charges. The receipt below confirms the charge was booked.

    Args:
        lock_id: Id class — the reference number of the Builder Extended Rate Lock the extension was written on, as returned by the rate lock finder.
        amount: Fixed-format class — the extension fee charged, in USD, a plain number rounded to 2 decimal places (half up, to the cent), no currency sign.
        extension_days: Fixed-format class — the calendar days of the extension this charge prices, an integer >= 0.

    Returns:
        A dictionary rendered as text with: status ("charge_booked" on success); lock_id (the lock
        reference number); charge_reference (the printed charge number, e.g. LCK-CHG-4123); amount (USD,
        2 decimal places); extension_days (integer); charges_due (USD, 2 decimal places, lock charges owed
        including the charge).
    """
    lock = (ctx.find("rate_locks", lock_id=lock_id) or [{}])[0]
    amt = round(float(amount), 2)
    rid = ctx.make_id("lev_", lock_id, "extension_fee", amt, extension_days)
    ref = f"LCK-CHG-4{int(rid[-6:], 16) % 1000:03d}"
    ctx.create("lock_events", rid, lock_event_id=rid, lock_id=lock_id, customer_id=lock.get("customer_id"),
               event_type="lock_charge_assessed", amount=amt, charge_type="extension_fee",
               charge_reference=ref, extension_days=int(extension_days), event_date=ctx.now()[:10])
    due = round(float(lock.get("charges_due") or 0) + amt, 2)
    ctx.update("rate_locks", lock_id, charges_due=due)
    return str({"status": "charge_booked", "lock_id": lock_id, "charge_reference": ref, "amount": amt,
                "extension_days": int(extension_days), "charges_due": due})


@tool(owner="agent", rw="write")
def waive_builder_delay_charge_21040a50(ctx: ToolContext, lock_id: str, source_charge_ref: str, amount: float) -> str:
    """Waive part or all of an extension fee charge on a Builder Extended Rate Lock because of a builder
    delay. One call writes one waiver on the lock ledger that names the charge number waived, records the
    reason as builder delay, and takes the waived amount off the lock charges owed. The buyer can
    see the waiver against that charge number. The receipt below confirms the waiver was
    booked.

    Args:
        lock_id: Id class — the reference number of the Builder Extended Rate Lock carrying the charge, as returned by the rate lock finder.
        source_charge_ref: Verbatim class — the printed charge number of the extension fee charge being waived, exactly as it appears on the lock ledger or on the receipt that booked it, copied character for character with no change (verbatim).
        amount: Fixed-format class — the amount waived, in USD, a plain number rounded to 2 decimal places (half up, to the cent), no currency sign.

    Returns:
        A dictionary rendered as text with: status ("waived" on success); lock_id (the lock reference
        number); source_charge_ref (the charge number waived); amount (USD, 2 decimal places);
        waiver_reason ("builder_delay"); charges_due (USD, 2 decimal places, lock charges owed net of the
        waiver).
    """
    lock = (ctx.find("rate_locks", lock_id=lock_id) or [{}])[0]
    amt = round(float(amount), 2)
    rid = ctx.make_id("lev_", lock_id, "waiver", source_charge_ref, amt)
    ctx.create("lock_events", rid, lock_event_id=rid, lock_id=lock_id, customer_id=lock.get("customer_id"),
               event_type="lock_charge_waived", amount=amt, charge_type="extension_fee",
               source_charge_ref=source_charge_ref, waiver_reason="builder_delay", event_date=ctx.now()[:10])
    due = round(float(lock.get("charges_due") or 0) - amt, 2)
    ctx.update("rate_locks", lock_id, charges_due=due)
    return str({"status": "waived", "lock_id": lock_id, "source_charge_ref": source_charge_ref, "amount": amt,
                "waiver_reason": "builder_delay", "charges_due": due})


@tool(owner="agent", rw="write")
def resize_lock_loan_amount_60b17697(ctx: ToolContext, lock_id: str, loan_amount: float, ltv_pct: float) -> str:
    """Lower the loan amount on a Builder Extended Rate Lock by a terms change. One call writes the new loan
    amount and the new loan-to-value percent on the lock; the loan program and the par rate stay as they
    are and no fee is booked. The buyer can see the new loan amount on the lock. The receipt
    below confirms the terms change was written.

    Args:
        lock_id: Id class — the reference number of the Builder Extended Rate Lock whose loan amount changes, as returned by the rate lock finder for this buyer.
        loan_amount: Fixed-format class — the new loan amount on the lock, in USD, a plain number with 2 decimal places, no currency sign or thousands separators.
        ltv_pct: Fixed-format class — the new loan-to-value of the lock, in percent, 2 decimal places, no percent sign.

    Returns:
        A dictionary rendered as text with: status ("terms_changed" on success); lock_id (the lock
        reference number); previous_loan_amount (USD, 2 decimal places, the amount replaced) and loan_amount (USD, 2 decimal places, the new amount);
        ltv_pct (percent, 2 decimal places); par_rate (percent, 3 decimal places, unchanged).
    """
    lock = (ctx.find("rate_locks", lock_id=lock_id) or [{}])[0]
    prev = lock.get("loan_amount")
    amt = round(float(loan_amount), 2)
    ctx.update("rate_locks", lock_id, loan_amount=amt, ltv_pct=round(float(ltv_pct), 2))
    return str({"status": "terms_changed", "lock_id": lock_id, "previous_loan_amount": prev, "loan_amount": amt,
                "ltv_pct": round(float(ltv_pct), 2), "par_rate": lock.get("par_rate")})


@tool(owner="user", rw="write")
def pay_upfront_lock_fee_77612280(ctx: ToolContext, lock_id: str, amount: float, payment_method: str) -> str:
    """The buyer pays the upfront lock fee on their own Builder Extended Rate Lock. One call posts one fee
    payment on the lock ledger with a printed Calloway Home Mortgage receipt number and adds the amount to
    the lock fee held on the lock. The buyer can see the receipt number and the fee held. The
    receipt below confirms the payment posted.

    Args:
        lock_id: Id class — the reference number of the buyer's Builder Extended Rate Lock, as the agent read it from the rate lock finder and passed to the buyer.
        amount: Fixed-format class — the amount paid, in USD, a plain number rounded to 2 decimal places (half up, to the cent), no currency sign.
        payment_method: Enum class — how the buyer pays: ach when the buyer pays by electronic transfer from a bank account; wire when the buyer sends a bank wire.

    Returns:
        A dictionary rendered as text with: status ("paid" on success); lock_id (the lock reference
        number); payment_reference (the printed receipt number, e.g. CHM-RCPT-41234); amount (USD, 2
        decimal places); payment_method (ach or wire); lock_fee_held (USD, 2 decimal places, fee held on the
        lock including the payment).
    """
    lock = (ctx.find("rate_locks", lock_id=lock_id) or [{}])[0]
    amt = round(float(amount), 2)
    rid = ctx.make_id("lev_", lock_id, "lock_fee_paid", amt, payment_method)
    ref = f"CHM-RCPT-4{int(rid[-6:], 16) % 10000:04d}"
    ctx.create("lock_events", rid, lock_event_id=rid, lock_id=lock_id, customer_id=lock.get("customer_id"),
               event_type="lock_fee_paid", amount=amt, payment_method=payment_method,
               payment_reference=ref, event_date=ctx.now()[:10])
    held = round(float(lock.get("lock_fee_held") or 0) + amt, 2)
    ctx.update("rate_locks", lock_id, lock_fee_held=held)
    return str({"status": "paid", "lock_id": lock_id, "payment_reference": ref, "amount": amt,
                "payment_method": payment_method, "lock_fee_held": held})


@tool(owner="agent", rw="write")
def confirm_rate_lock_90ad719f(ctx: ToolContext, lock_id: str, locked_rate: float, lock_expiration_date: str) -> str:
    """Confirm a requested Builder Extended Rate Lock at the lock desk. One call moves the lock from
    requested to locked, writes today as the lock date, and writes the locked rate and the last day the
    lock is in force. The buyer can see the lock as locked at that rate through that date. The
    receipt below confirms the lock was confirmed.

    Args:
        lock_id: Id class — the reference number of the requested Builder Extended Rate Lock, as returned by the rate lock finder for this buyer.
        locked_rate: Fixed-format class — the interest rate locked, written as percent, 3 decimal places, e.g. 6.375 (no percent sign).
        lock_expiration_date: Fixed-format class — the last calendar day the lock is in force, written YYYY-MM-DD.

    Returns:
        A dictionary rendered as text with: status ("locked" on success); lock_id (the lock reference
        number); lock_date (YYYY-MM-DD, today); locked_rate (percent, 3 decimal places);
        lock_expiration_date (YYYY-MM-DD).
    """
    rate = round(float(locked_rate), 3)
    ctx.update("rate_locks", lock_id, status="locked", lock_date=ctx.now()[:10], locked_rate=rate,
               lock_expiration_date=str(lock_expiration_date))
    return str({"status": "locked", "lock_id": lock_id, "lock_date": ctx.now()[:10], "locked_rate": rate,
                "lock_expiration_date": str(lock_expiration_date)})

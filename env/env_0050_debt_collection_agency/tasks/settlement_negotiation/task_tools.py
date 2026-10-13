"""Hidden task tools for the settlement_negotiation difficulty (Settlement Agreements).

Each tool performs one atomic settlement write with the values the agent has already worked out
from the published settlement policies; no tool judges eligibility, prerequisites or amounts.
Calendar arithmetic uses the proleptic Gregorian day count held in the _Calendar helper class.
"""

from erlbench import ToolContext, tool


class _Calendar:
    """Pure day-count helpers: 'YYYY-MM-DD' <-> serial day number (days since 0000-03-01)."""

    @staticmethod
    def to_serial(day: str) -> int:
        y, m, d = (int(p) for p in str(day)[:10].split("-"))
        y -= 1 if m <= 2 else 0
        era = y // 400
        yoe = y - era * 400
        doy = (153 * (m + (-3 if m > 2 else 9)) + 2) // 5 + d - 1
        doe = yoe * 365 + yoe // 4 - yoe // 100 + doy
        return era * 146097 + doe

    @staticmethod
    def from_serial(n: int) -> str:
        era = n // 146097
        doe = n - era * 146097
        yoe = (doe - doe // 1460 + doe // 36524 - doe // 146096) // 365
        y = yoe + era * 400
        doy = doe - (365 * yoe + yoe // 4 - yoe // 100)
        mp = (5 * doy + 2) // 153
        d = doy - (153 * mp + 2) // 5 + 1
        m = mp + (3 if mp < 10 else -9)
        y += 1 if m <= 2 else 0
        return f"{y:04d}-{m:02d}-{d:02d}"

    @staticmethod
    def add_days(day: str, n: int) -> str:
        return _Calendar.from_serial(_Calendar.to_serial(day) + int(n))


class _Offers:
    """Shared preparation of the offer tools: the fields of one offered settlement on the account."""

    @staticmethod
    def prepare(ctx, account_id, variant, balance_at_offer, settlement_pct, settlement_amount,
              payment_count, interval_days, first_window_days, validity_days, bundle_applied, prefix):
        today = ctx.now()[:10]
        acct = ctx.find("placed_accounts", account_id=account_id)
        customer_id = acct[0].get("customer_id") if acct else ""
        first_due = _Calendar.add_days(today, first_window_days)
        final_due = _Calendar.add_days(first_due, interval_days * (payment_count - 1))
        rid = ctx.make_id(prefix, account_id, variant, balance_at_offer, settlement_pct, settlement_amount,
                          payment_count, bundle_applied, today)
        fields = dict(settlement_id=rid, customer_id=customer_id,
                   account_id=account_id, approval_request_id=None, variant_name=variant, status="offered",
                   offer_date=today, offer_expiry_date=_Calendar.add_days(today, validity_days),
                   balance_at_offer=round(float(balance_at_offer), 2),
                   settlement_pct=round(float(settlement_pct), 1),
                   settlement_amount=round(float(settlement_amount), 2), payment_count=int(payment_count),
                   payment_interval_days=int(interval_days), first_payment_due_date=first_due,
                   final_payment_due_date=final_due, bundle_applied=bool(bundle_applied), accepted_date="",
                   acceptance_method="", due_date_extension_count=0, extension_days_total=0,
                   settlement_balance=0.0, closed_date="", waived_amount=0.0, withdrawal_reason="")
        return rid, fields, {"settlement_id": rid, "status": "offered", "variant_name": variant, "offer_date": today,
                "offer_expiry_date": _Calendar.add_days(today, validity_days),
                "settlement_pct": round(float(settlement_pct), 1),
                "settlement_amount": round(float(settlement_amount), 2), "payment_count": int(payment_count),
                "first_payment_due_date": first_due, "final_payment_due_date": final_due,
                "bundle_applied": bool(bundle_applied)}


class _Acceptance:
    """Shared preparation of the acceptance tools: the accepted fields and the scheduled-amount entry."""

    @staticmethod
    def prepare(ctx, settlement_id, first_payment_due_in_days, method, prefix):
        today = ctx.now()[:10]
        rows = ctx.find("settlement_agreements", settlement_id=settlement_id)
        offer = rows[0] if rows else {}
        count = int(offer.get("payment_count") or 1)
        interval = int(offer.get("payment_interval_days") or 0)
        amount = round(float(offer.get("settlement_amount") or 0), 2)
        first_due = _Calendar.add_days(today, int(first_payment_due_in_days))
        final_due = _Calendar.add_days(first_due, interval * (count - 1))
        upd = dict(status="accepted", accepted_date=today,
                   acceptance_method=method, first_payment_due_date=first_due,
                   final_payment_due_date=final_due, settlement_balance=amount)
        tid = ctx.make_id(prefix, settlement_id, int(first_payment_due_in_days), today)
        sched = dict(settle_txn_id=tid, settlement_id=settlement_id,
                   customer_id=offer.get("customer_id", ""), account_id=offer.get("account_id", ""),
                   event_type="settle_amount_scheduled", payment_number=None, due_date="", amount=amount,
                   txn_date=today, payment_channel="", payment_ref="", source_settle_txn_id=None,
                   return_reason="", release_reason="", letter_type="", delivery_channel="",
                   disclosure_variant="", tax_notice_included=None)
        return upd, tid, sched, {"settlement_id": settlement_id, "status": "accepted", "accepted_date": today,
                "acceptance_method": method, "first_payment_due_date": first_due,
                "final_payment_due_date": final_due, "amount_scheduled": amount, "schedule_entry_id": tid}


class _Extension:
    """Shared preparation of the extension tools: the fields one due-date extension changes."""

    @staticmethod
    def prepare(ctx, settlement_id, extension_days):
        rows = ctx.find("settlement_agreements", settlement_id=settlement_id)
        st = rows[0] if rows else {}
        days = int(extension_days)
        count = int(st.get("due_date_extension_count") or 0) + 1
        total = int(st.get("extension_days_total") or 0) + days
        final_due = _Calendar.add_days(st.get("final_payment_due_date") or ctx.now()[:10], days)
        next_due = _Calendar.add_days(st.get("first_payment_due_date") or ctx.now()[:10], total)
        upd = dict(due_date_extension_count=count,
                   extension_days_total=total, final_payment_due_date=final_due)
        return upd, {"settlement_id": settlement_id, "extension_days": days, "due_date_extension_count": count,
                "extension_days_total": total, "first_payment_due_date_with_extensions": next_due,
                "final_payment_due_date": final_due}


@tool(owner="agent", rw="write")
def issue_two_payment_settlement_offer_a21e4b5c(ctx: ToolContext, account_id: str, balance_at_offer: float,
                                                 settlement_pct: float, settlement_amount: float,
                                                 bundle_applied: bool) -> str:
    """Extend a written Two-Payment Settlement offer on one placed account on Ridgeline's own authority.
    One call opens a new settlement for the account in status offered, dated today, under the Two-Payment
    Settlement programme: two settlement payments 30 calendar days apart, the first falling due 15 calendar
    days after today if the consumer accepted today, and the offer open for acceptance through the 30th
    calendar day after today. The offer records the balance, percentage and amount given, carries no client
    approval, and books nothing to the settlement balance until it is accepted. The consumer and the agent
    can see the new offer, with its reference, expiry date and due dates, among the account's settlements.

    Args:
        account_id: Id class — the Ridgeline account reference number (account identifier) of the placed account the offer would
            settle, as returned by the placed-account lookup for the verified consumer.
        balance_at_offer: Fixed-format class — the account's balance due today, in USD to 2 decimal places,
            exactly as the placed-account lookup shows it; no rounding beyond the cent.
        settlement_pct: Fixed-format class — the settlement percentage offered, in percent to 1 decimal
            place (for example 62.5 means 62.5 percent of the balance).
        settlement_amount: Fixed-format class — the amount that settles the account in full, in USD to 2
            decimal places; the tool stores it as given, rounded only to the cent.
        bundle_applied: Enum class — whether the offer is part of a same-client bundle: true when the offer
            is extended as part of a bundle covering the consumer's accounts under one client agreement and
            the bundle reduction is in its percentage; false when the offer stands alone without any bundle
            reduction.

    Returns:
        A text rendering of a dictionary with: settlement_id (the new settlement reference, text);
        status (always "offered" on success); variant_name ("Two-Payment Settlement"); offer_date and
        offer_expiry_date (YYYY-MM-DD); settlement_pct (percent, 1 decimal); settlement_amount (USD, 2
        decimals); payment_count (integer 2); first_payment_due_date and final_payment_due_date
        (YYYY-MM-DD, assuming acceptance today); bundle_applied (true or false). A returned settlement_id
        means the offer was recorded.
    """
    rid, fields, receipt = _Offers.prepare(ctx, account_id, "Two-Payment Settlement", balance_at_offer, settlement_pct,
                             settlement_amount, 2, 30, 15, 30, bundle_applied, "stl2_")
    ctx.create("settlement_agreements", rid, **fields)
    return str(receipt)


@tool(owner="agent", rw="write")
def issue_three_payment_settlement_offer_bcdb6a79(ctx: ToolContext, account_id: str, balance_at_offer: float,
                                                   settlement_pct: float, settlement_amount: float,
                                                   bundle_applied: bool) -> str:
    """Extend a written Three-Payment Settlement offer on one placed account on Ridgeline's own authority.
    One call opens a new settlement for the account in status offered, dated today, under the Three-Payment
    Settlement programme: three settlement payments 30 calendar days apart, the first falling due 15
    calendar days after today if the consumer accepted today, and the offer open for acceptance through the
    30th calendar day after today. The offer records the balance, percentage and amount given, carries no
    client approval, and books nothing to the settlement balance until it is accepted. The consumer and the
    agent can see the new offer, with its reference, expiry date and due dates, among the account's
    settlements.

    Args:
        account_id: Id class — the Ridgeline account reference number (account identifier) of the placed account the offer would
            settle, as returned by the placed-account lookup for the verified consumer.
        balance_at_offer: Fixed-format class — the account's balance due today, in USD to 2 decimal places,
            exactly as the placed-account lookup shows it; no rounding beyond the cent.
        settlement_pct: Fixed-format class — the settlement percentage offered, in percent to 1 decimal
            place (for example 62.5 means 62.5 percent of the balance).
        settlement_amount: Fixed-format class — the amount that settles the account in full, in USD to 2
            decimal places; the tool stores it as given, rounded only to the cent.
        bundle_applied: Enum class — whether the offer is part of a same-client bundle: true when the offer
            is extended as part of a bundle covering the consumer's accounts under one client agreement and
            the bundle reduction is in its percentage; false when the offer stands alone without any bundle
            reduction.

    Returns:
        A text rendering of a dictionary with: settlement_id (the new settlement reference, text);
        status (always "offered" on success); variant_name ("Three-Payment Settlement"); offer_date and
        offer_expiry_date (YYYY-MM-DD); settlement_pct (percent, 1 decimal); settlement_amount (USD, 2
        decimals); payment_count (integer 3); first_payment_due_date and final_payment_due_date
        (YYYY-MM-DD, assuming acceptance today); bundle_applied (true or false). A returned settlement_id
        means the offer was recorded.
    """
    rid, fields, receipt = _Offers.prepare(ctx, account_id, "Three-Payment Settlement", balance_at_offer, settlement_pct,
                             settlement_amount, 3, 30, 15, 30, bundle_applied, "stl3_")
    ctx.create("settlement_agreements", rid, **fields)
    return str(receipt)


@tool(owner="user", rw="write")
def accept_settlement_offer_on_recorded_call_60e9ef1d(ctx: ToolContext, settlement_id: str,
                                                       first_payment_due_in_days: int) -> str:
    """The consumer accepts, on this recorded call, an open written settlement offer on one of their
    placed accounts. One call moves that settlement from offered to accepted with today as the acceptance
    date and a recorded call as the acceptance method, sets the first settlement payment due the given
    number of calendar days after today and the final payment due the offer's payment interval after it for
    each remaining payment, sets the amount still to pay under the settlement to the offer's settlement
    amount, and books that settlement amount to the settlement once as today's scheduled amount. The
    consumer can see the settlement as accepted with its new due dates.

    Args:
        settlement_id: Id class — the settlement reference number (settlement identifier) of the open offer being accepted, as returned by
            the settlement lookup.
        first_payment_due_in_days: Fixed-format class — the number of calendar days after today on which
            settlement payment 1 falls due, a whole integer of at least 1, as the agent states it to the
            consumer.

    Returns:
        A text rendering of a dictionary with: settlement_id (text); status (always "accepted" on
        success); accepted_date (YYYY-MM-DD, today); acceptance_method ("recorded_call");
        first_payment_due_date and final_payment_due_date (YYYY-MM-DD); amount_scheduled (USD, 2
        decimals, the settlement amount booked today); schedule_entry_id (reference of the booked
        scheduled-amount entry). A returned status of accepted means the acceptance is on record.
    """
    upd, tid, sched, receipt = _Acceptance.prepare(ctx, settlement_id, first_payment_due_in_days, "recorded_call", "sacc_")
    ctx.update("settlement_agreements", settlement_id, **upd)
    ctx.create("settlement_payments", tid, **sched)
    return str(receipt)


@tool(owner="agent", rw="write")
def extend_lump_sum_settlement_due_date_54e5e409(ctx: ToolContext, settlement_id: str, extension_days: int) -> str:
    """Grant one due-date extension on an accepted Lump-Sum Settlement. One call moves the settlement's single
    payment later by the given number of calendar days: it adds one to the settlement's extension count, adds
    the days to the settlement's total extension days, and moves the final payment due date later by the same
    days; the settlement amount and the amount still to pay are unchanged. The consumer and the agent can see the
    new due date on the settlement.

    Args:
        settlement_id: Id class — the settlement reference number (settlement identifier) of the accepted
            Lump-Sum Settlement, as returned by the settlement lookup.
        extension_days: Fixed-format class — the number of calendar days the extension adds, a whole integer of
            at least 1.

    Returns:
        A text rendering of a dictionary with: settlement_id (text); extension_days (integer, the days added by
        this call); due_date_extension_count (integer, extensions granted so far including this one);
        extension_days_total (integer, all days added by extensions); first_payment_due_date_with_extensions
        (YYYY-MM-DD, the payment's due date after all extensions); final_payment_due_date (YYYY-MM-DD). A
        returned extension count means the extension is on record.
    """
    upd, receipt = _Extension.prepare(ctx, settlement_id, extension_days)
    ctx.update("settlement_agreements", settlement_id, **upd)
    return str(receipt)


@tool(owner="agent", rw="write")
def issue_hardship_settlement_offer_9c740749(ctx: ToolContext, account_id: str, balance_at_offer: float,
                                             settlement_pct: float, settlement_amount: float,
                                             payment_count: int) -> str:
    """Extend a written Hardship Settlement offer on one placed account on Ridgeline's own authority. One call
    opens a new settlement for the account in status offered, dated today, under the Hardship Settlement
    programme: the given number of settlement payments 30 calendar days apart, the first falling due 30 calendar
    days after today if the consumer accepted today, and the offer open for acceptance through the 45th calendar
    day after today. The offer records the balance, percentage and amount given, carries no client approval and
    no same-client bundle, and books nothing to the settlement balance until it is accepted. The consumer and the
    agent can see the new offer, with its reference, expiry date and due dates, among the account's settlements.

    Args:
        account_id: Id class — the Ridgeline account reference number (account identifier) of the placed account
            the offer would settle, as returned by the placed-account lookup for the verified consumer.
        balance_at_offer: Fixed-format class — the account's balance due today, in USD to 2 decimal places,
            exactly as the placed-account lookup shows it; no rounding beyond the cent.
        settlement_pct: Fixed-format class — the settlement percentage offered, in percent to 1 decimal place
            (for example 62.5 means 62.5 percent of the balance).
        settlement_amount: Fixed-format class — the amount that settles the account in full, in USD to 2 decimal
            places; the tool stores it as given, rounded only to the cent.
        payment_count: Fixed-format class — the number of settlement payments the consumer chose, a positive
            integer from 1 to 3.

    Returns:
        A text rendering of a dictionary with: settlement_id (the new settlement reference, text); status
        (always "offered" on success); variant_name ("Hardship Settlement"); offer_date and offer_expiry_date
        (YYYY-MM-DD); settlement_pct (percent, 1 decimal); settlement_amount (USD, 2 decimals); payment_count
        (integer); first_payment_due_date and final_payment_due_date (YYYY-MM-DD, assuming acceptance today);
        bundle_applied (always false). A returned settlement_id means the offer was recorded.
    """
    rid, fields, receipt = _Offers.prepare(ctx, account_id, "Hardship Settlement", balance_at_offer, settlement_pct,
                             settlement_amount, int(payment_count), 30, 30, 45, False, "stlh_")
    ctx.create("settlement_agreements", rid, **fields)
    return str(receipt)


@tool(owner="user", rw="write")
def sign_settlement_offer_electronically_52f226cb(ctx: ToolContext, settlement_id: str,
                                                  first_payment_due_in_days: int) -> str:
    """The consumer signs, with an electronic signature, an open written settlement offer on one of their placed
    accounts. One call moves that settlement from offered to accepted with today as the acceptance date and an
    electronic signature as the acceptance method, sets the first settlement payment due the given number of
    calendar days after today and the final payment due the offer's payment interval after it for each remaining
    payment, sets the amount still to pay under the settlement to the offer's settlement amount, and books that
    settlement amount to the settlement once as today's scheduled amount. The consumer can see the settlement as
    accepted with its new due dates.

    Args:
        settlement_id: Id class — the settlement reference number (settlement identifier) of the open offer being
            signed, as returned by the settlement lookup.
        first_payment_due_in_days: Fixed-format class — the number of calendar days after today on which
            settlement payment 1 falls due, a whole integer of at least 1, as the agent states it to the consumer.

    Returns:
        A text rendering of a dictionary with: settlement_id (text); status (always "accepted" on success);
        accepted_date (YYYY-MM-DD, today); acceptance_method ("e_signature"); first_payment_due_date and
        final_payment_due_date (YYYY-MM-DD); amount_scheduled (USD, 2 decimals, the settlement amount booked
        today); schedule_entry_id (reference of the booked scheduled-amount entry). A returned status of accepted
        means the acceptance is on record.
    """
    upd, tid, sched, receipt = _Acceptance.prepare(ctx, settlement_id, first_payment_due_in_days, "e_signature", "sesg_")
    ctx.update("settlement_agreements", settlement_id, **upd)
    ctx.create("settlement_payments", tid, **sched)
    return str(receipt)


@tool(owner="agent", rw="write")
def extend_hardship_settlement_due_dates_12bdc2d4(ctx: ToolContext, settlement_id: str,
                                                  extension_days: int) -> str:
    """Grant one due-date extension on an accepted Hardship Settlement. One call moves the next unpaid settlement
    payment and every later one later by the given number of calendar days: it adds one to the settlement's
    extension count, adds the days to the settlement's total extension days, and moves the final payment due date
    later by the same days; the settlement amount and the amount still to pay are unchanged. The consumer and the
    agent can see the new due dates on the settlement.

    Args:
        settlement_id: Id class — the settlement reference number (settlement identifier) of the accepted Hardship
            Settlement, as returned by the settlement lookup.
        extension_days: Fixed-format class — the number of calendar days the extension adds, a whole integer of
            at least 1.

    Returns:
        A text rendering of a dictionary with: settlement_id (text); extension_days (integer, the days added by
        this call); due_date_extension_count (integer, extensions granted so far including this one);
        extension_days_total (integer, all days added by extensions); first_payment_due_date_with_extensions
        (YYYY-MM-DD, payment 1's due date after all extensions); final_payment_due_date (YYYY-MM-DD). A returned
        extension count means the extension is on record.
    """
    upd, receipt = _Extension.prepare(ctx, settlement_id, extension_days)
    ctx.update("settlement_agreements", settlement_id, **upd)
    return str(receipt)

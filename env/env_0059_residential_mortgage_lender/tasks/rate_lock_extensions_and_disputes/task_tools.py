"""Hidden task tools of the rate_lock_extensions_and_disputes difficulty (Larkspur Home Lending).

Each tool lands one atomic write on a Rate Lock Commitment record set (the lock, its request log,
its pricing entries and its disputes). The tools take the values the lock desk has already worked
out under the published lock policies and record them; they never judge eligibility, never
aggregate history and never refuse a write because another matter on the file is still open.
"""

from erlbench import ToolContext, tool


@tool(owner="user", rw="write")
def submit_lock_extension_request_8348adff(ctx: ToolContext, lock_id: str, requested_term_days: int) -> str:
    """The borrower submits, in the Larkspur borrower portal, a request asking the lock desk to extend
    an existing rate lock by a number of calendar days. One call logs exactly one time-stamped extension
    request in the lock's request log: the request is recorded as an extension request received through
    the borrower portal, stamped with today's date and the current US Eastern time, carrying the number of
    days asked for and the lock's currently locked note rate as the requested rate. Nothing is booked or
    charged by the request itself and the lock's expiration date does not move; the borrower sees the
    request in the portal's lock history. Success is indicated by status "logged" together with the new
    request reference number.

    Args:
        lock_id: Id class — the reference number of the borrower's rate lock commitment that the request
            asks to extend, as returned by the rate lock lookup and read out to the borrower before the call.
        requested_term_days: Fixed-format class — the number of calendar days the borrower asks the lock
            desk to add to the lock, in integer, days (a whole number of calendar days, 0 or more).

    Returns:
        A dictionary rendered as text with: lock_request_id (string, reference number of the logged
        request), lock_id (string, the lock the request concerns), request_type (always "extension"),
        request_channel (always "borrower_portal"), request_date (YYYY-MM-DD, the date the request was
        time-stamped), request_time (HH:MM, 24-hour US Eastern time stamp), requested_term_days (integer
        days asked for), requested_rate (percent with 3 decimal places, the locked note rate carried on the
        request) and status ("logged" when the request is on the lock's request log).
    """
    lock_rows = ctx.find("rate_locks", lock_id=lock_id)
    customer_id = lock_rows[0].get("customer_id") if lock_rows else ""
    locked_rate = lock_rows[0].get("locked_rate") if lock_rows else None
    stamp = ctx.now()
    rid = ctx.make_id("lrq_", lock_id, "extension", int(requested_term_days), stamp)
    ctx.create("lock_requests", rid, lock_request_id=rid, lock_id=lock_id, customer_id=customer_id,
               event_type="lock_request_logged", request_type="extension", request_channel="borrower_portal",
               request_date=stamp[:10], request_time=stamp[11:16], requested_term_days=int(requested_term_days),
               requested_rate=locked_rate)
    return str({"lock_request_id": rid, "lock_id": lock_id, "request_type": "extension",
                "request_channel": "borrower_portal", "request_date": stamp[:10], "request_time": stamp[11:16],
                "requested_term_days": int(requested_term_days), "requested_rate": locked_rate,
                "status": "logged"})


@tool(owner="agent", rw="write")
def decide_extension_charge_dispute_a9bc145e(ctx: ToolContext, lock_id: str, dispute_id: str, resolution: str,
                                             waived_points: float, waived_amount: float) -> str:
    """The lock desk records its decision on a dispute the borrower filed against an extension charge on a
    rate lock. One call writes one decision record that names the filed dispute, carries the same dispute
    reason, filing date and disputed extension entry as the filing, the chosen outcome and today's date as
    the decision date. When the outcome is that the extension cost is waived, the same call also books one
    waiver entry on the lock's pricing ledger that names the disputed extension entry, is borne by
    Larkspur, carries the waived points and waived dollars given here, and lowers the lock's outstanding
    lock cost balance by the waived dollars; any other outcome books no waiver and leaves the balance as it
    is. Afterwards the dispute shows as decided and, for a waiver, the borrower's lock costs show the
    reduction. Success is indicated by status "decided".

    Args:
        lock_id: Id class — the reference number of the rate lock commitment the dispute concerns, as
            returned by the rate lock lookup.
        dispute_id: Id class — the reference number of the dispute filing record being decided (the record
            whose outcome still reads pending), as returned by the lock dispute lookup.
        resolution: Enum class — the outcome recorded on the decision. extension_cost_waived — the lock
            desk relieves the disputed extension of part or all of its charge and books the waiver;
            denied_borrower_caused — the dispute was filed in time but no part of the charge is relieved;
            denied_untimely — the dispute was filed after its filing window closed; honored_claimed_terms —
            outcome of an upheld rate or lock-request dispute, never of an extension-charge dispute;
            denied_no_record — outcome of a rate or lock-request dispute with no matching logged request;
            denied_after_cutoff — outcome of a rate or lock-request dispute whose matching request was
            logged after the lock desk cutoff; pending — the state of an undecided filing, never a decision
            outcome.
        waived_points: Fixed-format class — the waived cost in points of the lock's loan amount at lock,
            points, 3 decimals (percent of the loan amount; positive is a cost to the borrower, negative a credit), given as a positive figure rounded to 3 decimal places; send 0.0 when nothing is waived.
        waived_amount: Fixed-format class — the waived cost in US dollars, USD, 2 decimal places (cents);
            send 0.0 when nothing is waived.

    Returns:
        A dictionary rendered as text with: lock_dispute_id (string, reference number of the decision
        record), source_dispute_id (string, the filing decided), resolution (the outcome recorded),
        resolved_date (YYYY-MM-DD, the decision date), waiver_entry_id (string reference number of the
        waiver entry booked, or "" when none was booked), waived_amount (USD with 2 decimals, 0.0 when none),
        lock_cost_balance (USD with 2 decimals, the lock's outstanding lock costs after the decision) and
        status ("decided" once the decision is on record).
    """
    filing = ctx.find("lock_disputes", lock_dispute_id=dispute_id)
    src = filing[0] if filing else {}
    lock_rows = ctx.find("rate_locks", lock_id=lock_id)
    balance = float(lock_rows[0].get("lock_cost_balance") or 0) if lock_rows else 0.0
    today = ctx.now()[:10]
    rid = ctx.make_id("ldr_", lock_id, dispute_id, resolution, round(float(waived_points), 3),
                      round(float(waived_amount), 2))
    ctx.create("lock_disputes", rid, lock_dispute_id=rid, lock_id=lock_id, customer_id=src.get("customer_id"),
               event_type="lock_dispute_resolved", dispute_reason=src.get("dispute_reason"),
               filed_date=src.get("filed_date"), claimed_request_date="", claimed_rate=None,
               disputed_pricing_id=src.get("disputed_pricing_id"), resolution=resolution, resolved_date=today,
               matched_request_id="", source_dispute_id=dispute_id)
    waiver_id = ""
    if resolution == "extension_cost_waived":
        waiver_id = ctx.make_id("lcw_", lock_id, dispute_id, round(float(waived_points), 3),
                                round(float(waived_amount), 2))
        ctx.create("lock_pricing_events", waiver_id, lock_pricing_id=waiver_id, lock_id=lock_id,
                   customer_id=src.get("customer_id"), event_type="lock_cost_waived", event_date=today,
                   extension_days=0, larkspur_borne_days=0, extension_seq=0,
                   cost_points=round(float(waived_points), 3), cost_amount=round(float(waived_amount), 2),
                   cost_bearer="larkspur", new_expiration_date="", new_rate=None,
                   source_pricing_id=src.get("disputed_pricing_id"))
        balance = round(balance - round(float(waived_amount), 2), 2)
        ctx.update("rate_locks", lock_id, lock_cost_balance=balance)
    return str({"lock_dispute_id": rid, "source_dispute_id": dispute_id, "resolution": resolution,
                "resolved_date": today, "waiver_entry_id": waiver_id,
                "waived_amount": round(float(waived_amount), 2) if waiver_id else 0.0,
                "lock_cost_balance": balance, "status": "decided"})


@tool(owner="agent", rw="write")
def book_lock_extension_178d685b(ctx: ToolContext, lock_id: str, loan_file_id: str, extension_seq: int,
                                 extension_days: int,
                                 larkspur_borne_days: int, cost_points: float, cost_amount: float,
                                 cost_bearer: str, new_expiration_date: str) -> str:
    """The lock desk books one extension of a rate lock commitment. One call writes one extension entry on
    the lock's pricing ledger, dated today, carrying the extension's place in the lock's sequence, the
    days it adds, the days whose cost Larkspur bears, its cost in points and in dollars and who bears it,
    and the expiration date it sets; the same call moves the lock's current expiration date to that new
    date and adds the dollar cost to the lock's outstanding lock cost balance, which is collected as a
    price adjustment at closing. Afterwards the borrower's lock shows the new expiration date and the
    added cost. Success is indicated by status "booked".

    Args:
        lock_id: Id class — the reference number of the rate lock commitment being extended, as returned by
            the rate lock lookup.
        loan_file_id: Id class — the reference number of the mortgage loan file the extended lock protects,
            as shown on the rate lock record and returned by the loan file lookup.
        extension_seq: Fixed-format class — the extension's position in the lock's sequence of extensions
            (1 for the first, 2 for the second, and so on), in integer, ordinal form.
        extension_days: Fixed-format class — the days the extension adds to the lock, in integer, calendar
            days, equal to one of the lock's sold extension lengths.
        larkspur_borne_days: Fixed-format class — how many of the added days Larkspur bears at no cost to
            the borrower, in integer, calendar days, from 0 up to the days added.
        cost_points: Fixed-format class — the extension's cost in points of the lock's loan amount at lock,
            points, 3 decimals (percent of the loan amount; positive is a cost to the borrower, negative a credit), rounded to 3 decimal places; 0.0 when the borrower is charged nothing.
        cost_amount: Fixed-format class — the extension's cost in US dollars, USD, 2 decimal places (cents);
            0.0 when the borrower is charged nothing.
        cost_bearer: Enum class — who bears the booked cost. borrower: the extension carries a charge to
            the borrower (a cost above 0.00). larkspur: every added day is borne by Larkspur and the entry
            books 0.00.
        new_expiration_date: Fixed-format class — the lock expiration date after this extension, as a
            calendar date in the format YYYY-MM-DD (US Eastern business calendar, already rolled forward to a
            business day where the lock rules require it).

    Returns:
        A dictionary rendered as text with: lock_pricing_id (string, reference number of the extension
        entry), lock_id (string), loan_file_id (string, the loan file the lock protects), extension_seq (integer), extension_days (integer), larkspur_borne_days
        (integer), cost_points (points with 3 decimals), cost_amount (USD with 2 decimals), cost_bearer
        (borrower or larkspur), lock_expiration_date (YYYY-MM-DD, the lock's expiration date after the
        booking), lock_cost_balance (USD with 2 decimals, outstanding lock costs after the booking) and
        status ("booked" once the extension is on the ledger).
    """
    lock_rows = ctx.find("rate_locks", lock_id=lock_id)
    customer_id = lock_rows[0].get("customer_id") if lock_rows else ""
    balance = float(lock_rows[0].get("lock_cost_balance") or 0) if lock_rows else 0.0
    today = ctx.now()[:10]
    rid = ctx.make_id("lex_", lock_id, loan_file_id, int(extension_seq), int(extension_days), int(larkspur_borne_days),
                      round(float(cost_points), 3), round(float(cost_amount), 2), cost_bearer, new_expiration_date)
    ctx.create("lock_pricing_events", rid, lock_pricing_id=rid, lock_id=lock_id, customer_id=customer_id,
               event_type="lock_extension_booked", event_date=today, extension_days=int(extension_days),
               larkspur_borne_days=int(larkspur_borne_days), extension_seq=int(extension_seq),
               cost_points=round(float(cost_points), 3), cost_amount=round(float(cost_amount), 2),
               cost_bearer=cost_bearer, new_expiration_date=new_expiration_date, new_rate=None,
               source_pricing_id="")
    balance = round(balance + round(float(cost_amount), 2), 2)
    ctx.update("rate_locks", lock_id, lock_expiration_date=new_expiration_date, lock_cost_balance=balance)
    return str({"lock_pricing_id": rid, "lock_id": lock_id, "loan_file_id": loan_file_id,
                "extension_seq": int(extension_seq),
                "extension_days": int(extension_days), "larkspur_borne_days": int(larkspur_borne_days),
                "cost_points": round(float(cost_points), 3), "cost_amount": round(float(cost_amount), 2),
                "cost_bearer": cost_bearer, "lock_expiration_date": new_expiration_date,
                "lock_cost_balance": balance, "status": "booked"})


@tool(owner="agent", rw="write")
def waive_extension_charge_02e9996e(ctx: ToolContext, lock_id: str, extension_entry_id: str, waived_points: float,
                                    waived_amount: float) -> str:
    """Larkspur waives, on its own initiative, part or all of the charge of one extension already booked on a
    rate lock. One call books one waiver entry on the lock's pricing ledger, dated today, that names the
    extension entry being relieved, is borne by Larkspur and carries the waived points and waived dollars
    given here; the same call lowers the lock's outstanding lock cost balance by the waived dollars. The
    original extension entry is left untouched. Afterwards the borrower's lock costs show the reduction and
    the extension shows a waiver against it. Success is indicated by status "waived".

    Args:
        lock_id: Id class — the reference number of the rate lock commitment carrying the extension, as
            returned by the rate lock lookup.
        extension_entry_id: Id class — the reference number of the extension entry on the lock's pricing
            ledger whose charge is waived, as returned by the lock pricing ledger lookup.
        waived_points: Fixed-format class — the waived cost in points of the lock's loan amount at lock,
            points, 3 decimals (percent of the loan amount; positive is a cost to the borrower, negative a credit),
            given as a positive figure rounded to 3 decimal places.
        waived_amount: Fixed-format class — the waived cost in US dollars, USD, 2 decimal places (cents).

    Returns:
        A dictionary rendered as text with: lock_pricing_id (string, reference number of the waiver entry),
        lock_id (string), source_pricing_id (string, the extension entry relieved), cost_points (points with
        3 decimals), cost_amount (USD with 2 decimals, the waived dollars), cost_bearer (always "larkspur"),
        lock_cost_balance (USD with 2 decimals, outstanding lock costs after the waiver) and status ("waived"
        once the waiver entry is on the ledger).
    """
    lock_rows = ctx.find("rate_locks", lock_id=lock_id)
    customer_id = lock_rows[0].get("customer_id") if lock_rows else ""
    balance = float(lock_rows[0].get("lock_cost_balance") or 0) if lock_rows else 0.0
    today = ctx.now()[:10]
    rid = ctx.make_id("lwv_", lock_id, extension_entry_id, round(float(waived_points), 3),
                      round(float(waived_amount), 2))
    ctx.create("lock_pricing_events", rid, lock_pricing_id=rid, lock_id=lock_id, customer_id=customer_id,
               event_type="lock_cost_waived", event_date=today, extension_days=0, larkspur_borne_days=0,
               extension_seq=0, cost_points=round(float(waived_points), 3), cost_amount=round(float(waived_amount), 2),
               cost_bearer="larkspur", new_expiration_date="", new_rate=None, source_pricing_id=extension_entry_id)
    balance = round(balance - round(float(waived_amount), 2), 2)
    ctx.update("rate_locks", lock_id, lock_cost_balance=balance)
    return str({"lock_pricing_id": rid, "lock_id": lock_id, "source_pricing_id": extension_entry_id,
                "cost_points": round(float(waived_points), 3), "cost_amount": round(float(waived_amount), 2),
                "cost_bearer": "larkspur", "lock_cost_balance": balance, "status": "waived"})


@tool(owner="agent", rw="write")
def relock_expired_rate_20a82baa(ctx: ToolContext, lock_id: str, relocked_rate: float, relocked_price_points: float,
                                 new_expiration_date: str) -> str:
    """The lock desk relocks an expired rate lock commitment within its relock window. One call puts the lock
    back in locked status and records on it the relocked note rate, the relocked net price and the new
    expiration date given here; the lock's term, loan amount at lock and deposit are untouched, and no fee is
    booked by this call. Afterwards the borrower's lock shows as locked again with the new rate, price and
    expiration date. Success is indicated by status "relocked".

    Args:
        lock_id: Id class — the reference number of the expired rate lock commitment being relocked, as
            returned by the rate lock lookup.
        relocked_rate: Fixed-format class — the note rate the relocked lock carries, percent, 3 decimal places
            (e.g. 6.875).
        relocked_price_points: Fixed-format class — the net price the relocked lock carries, points, 3 decimals
            (percent of the loan amount; positive is a cost to the borrower, negative a credit), rounded to 3
            decimal places.
        new_expiration_date: Fixed-format class — the relocked lock's expiration date, as a calendar date in the
            format YYYY-MM-DD (US Eastern business calendar).

    Returns:
        A dictionary rendered as text with: lock_id (string), status (the lock's lifecycle status, "locked"),
        locked_rate (percent with 3 decimals), lock_price_points (points with 3 decimals),
        lock_expiration_date (YYYY-MM-DD) and result ("relocked" once the lock is back in force).
    """
    ctx.update("rate_locks", lock_id, status="locked", locked_rate=round(float(relocked_rate), 3),
               lock_price_points=round(float(relocked_price_points), 3), lock_expiration_date=new_expiration_date)
    return str({"lock_id": lock_id, "status": "locked", "locked_rate": round(float(relocked_rate), 3),
                "lock_price_points": round(float(relocked_price_points), 3),
                "lock_expiration_date": new_expiration_date, "result": "relocked"})


@tool(owner="agent", rw="write")
def book_relock_fee_339fcee1(ctx: ToolContext, lock_id: str, cost_points: float, cost_amount: float) -> str:
    """The lock desk books the relock fee owed for a relock of a rate lock commitment. One call writes one
    relock fee entry on the lock's pricing ledger, dated today, borne by the borrower, carrying the fee in
    points and in dollars given here together with the expiration date and note rate the lock now carries;
    the same call adds the dollar fee to the lock's outstanding lock cost balance, which is collected as a
    price adjustment at closing. Afterwards the borrower's lock costs show the relock fee. Success is
    indicated by status "booked".

    Args:
        lock_id: Id class — the reference number of the relocked rate lock commitment, as returned by the rate
            lock lookup.
        cost_points: Fixed-format class — the relock fee in points of the lock's loan amount at lock, points, 3
            decimals (percent of the loan amount; positive is a cost to the borrower, negative a credit),
            rounded to 3 decimal places.
        cost_amount: Fixed-format class — the relock fee in US dollars, USD, 2 decimal places (cents).

    Returns:
        A dictionary rendered as text with: lock_pricing_id (string, reference number of the relock fee
        entry), lock_id (string), cost_points (points with 3 decimals), cost_amount (USD with 2 decimals),
        cost_bearer (always "borrower"), new_expiration_date (YYYY-MM-DD, the lock's expiration date after
        the relock), new_rate (percent with 3 decimals, the lock's note rate after the relock),
        lock_cost_balance (USD with 2 decimals) and status ("booked" once the fee is on the ledger).
    """
    lock_rows = ctx.find("rate_locks", lock_id=lock_id)
    lock = lock_rows[0] if lock_rows else {}
    balance = float(lock.get("lock_cost_balance") or 0)
    today = ctx.now()[:10]
    rid = ctx.make_id("lrf_", lock_id, round(float(cost_points), 3), round(float(cost_amount), 2), today)
    ctx.create("lock_pricing_events", rid, lock_pricing_id=rid, lock_id=lock_id, customer_id=lock.get("customer_id"),
               event_type="lock_relock_fee_booked", event_date=today, extension_days=0, larkspur_borne_days=0,
               extension_seq=0, cost_points=round(float(cost_points), 3), cost_amount=round(float(cost_amount), 2),
               cost_bearer="borrower", new_expiration_date=lock.get("lock_expiration_date"),
               new_rate=lock.get("locked_rate"), source_pricing_id="")
    balance = round(balance + round(float(cost_amount), 2), 2)
    ctx.update("rate_locks", lock_id, lock_cost_balance=balance)
    return str({"lock_pricing_id": rid, "lock_id": lock_id, "cost_points": round(float(cost_points), 3),
                "cost_amount": round(float(cost_amount), 2), "cost_bearer": "borrower",
                "new_expiration_date": lock.get("lock_expiration_date"), "new_rate": lock.get("locked_rate"),
                "lock_cost_balance": balance, "status": "booked"})


@tool(owner="user", rw="write")
def exercise_float_down_fc7d974d(ctx: ToolContext, lock_id: str, loan_file_id: str, new_rate: float,
                                 fee_points: float, fee_amount: float) -> str:
    """The borrower exercises, in person, the one-time float-down option of a locked rate lock commitment.
    One call books one float-down fee entry on the lock's pricing ledger, dated today, borne by the borrower,
    carrying the fee in points and in dollars and the new note rate given here, and reprices the lock: its
    locked note rate becomes the new rate, its float-down option is marked as used, its price and expiration
    date stay as they are, and the dollar fee is added to its outstanding lock cost balance, collected as a
    price adjustment at closing. Afterwards the borrower sees the lower locked rate on the lock. Success is
    indicated by status "floated".

    Args:
        lock_id: Id class — the reference number of the borrower's rate lock commitment, as returned by the rate
            lock lookup and read out to the borrower before the call.
        loan_file_id: Id class — the reference number of the mortgage loan file the lock protects, as shown on
            the rate lock record and read out to the borrower before the call.
        new_rate: Fixed-format class — the note rate the lock floats down to, in percent, 3 decimal places
            (e.g. 6.875), written like the locked rate on the lock record.
        fee_points: Fixed-format class — the float-down fee in points of the lock's loan amount at lock, points,
            3 decimals (percent of the loan amount; positive is a cost to the borrower, negative a credit),
            rounded to 3 decimal places.
        fee_amount: Fixed-format class — the float-down fee in US dollars, USD, 2 decimal places (cents).

    Returns:
        A dictionary rendered as text with: lock_pricing_id (string, reference number of the float-down fee
        entry), lock_id (string), loan_file_id (string), locked_rate (percent with 3 decimals, the rate after
        the float-down), float_down_used (always True after the call), cost_points (points with 3 decimals),
        cost_amount (USD with 2 decimals), lock_cost_balance (USD with 2 decimals) and status ("floated" once
        the lock carries the new rate).
    """
    lock_rows = ctx.find("rate_locks", lock_id=lock_id)
    lock = lock_rows[0] if lock_rows else {}
    balance = float(lock.get("lock_cost_balance") or 0)
    today = ctx.now()[:10]
    rid = ctx.make_id("lfd_", lock_id, loan_file_id, round(float(new_rate), 3), round(float(fee_points), 3),
                      round(float(fee_amount), 2))
    ctx.create("lock_pricing_events", rid, lock_pricing_id=rid, lock_id=lock_id, customer_id=lock.get("customer_id"),
               event_type="lock_float_down_fee_booked", event_date=today, extension_days=0, larkspur_borne_days=0,
               extension_seq=0, cost_points=round(float(fee_points), 3), cost_amount=round(float(fee_amount), 2),
               cost_bearer="borrower", new_expiration_date="", new_rate=round(float(new_rate), 3),
               source_pricing_id="")
    balance = round(balance + round(float(fee_amount), 2), 2)
    ctx.update("rate_locks", lock_id, locked_rate=round(float(new_rate), 3), float_down_used=True,
               lock_cost_balance=balance)
    return str({"lock_pricing_id": rid, "lock_id": lock_id, "loan_file_id": loan_file_id,
                "locked_rate": round(float(new_rate), 3), "float_down_used": True,
                "cost_points": round(float(fee_points), 3), "cost_amount": round(float(fee_amount), 2),
                "lock_cost_balance": balance, "status": "floated"})

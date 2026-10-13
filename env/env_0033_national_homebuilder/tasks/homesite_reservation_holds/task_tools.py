"""Hidden task tools of the homesite_reservation_holds difficulty (Calloway Homes).

Each tool performs one atomic write on a Homesite Reservation or its ledger with the values the
caller passes in; none of them checks a status, a window, a prerequisite or an amount. Hold terms
are passed as whole calendar days and written as the hold expiry date they produce.
"""

from erlbench import ToolContext, tool


class _Calendar:
    """Whole-day calendar arithmetic on 'YYYY-MM-DD' strings (no clock is read)."""

    @staticmethod
    def days_from_civil(y, m, d):
        y -= m <= 2
        era = (y if y >= 0 else y - 399) // 400
        yoe = y - era * 400
        doy = (153 * (m + (-3 if m > 2 else 9)) + 2) // 5 + d - 1
        doe = yoe * 365 + yoe // 4 - yoe // 100 + doy
        return era * 146097 + doe - 719468

    @staticmethod
    def civil_from_days(z):
        z += 719468
        era = (z if z >= 0 else z - 146096) // 146097
        doe = z - era * 146097
        yoe = (doe - doe // 1460 + doe // 36524 - doe // 146096) // 365
        y = yoe + era * 400
        doy = doe - (365 * yoe + yoe // 4 - yoe // 100)
        mp = (5 * doy + 2) // 153
        d = doy - (153 * mp + 2) // 5 + 1
        m = mp + (3 if mp < 10 else -9)
        return y + (m <= 2), m, d

    @classmethod
    def plus_days(cls, iso_date, days):
        """'YYYY-MM-DD' plus a whole number of calendar days, as 'YYYY-MM-DD'."""
        y, m, d = (int(part) for part in str(iso_date)[:10].split("-"))
        y2, m2, d2 = cls.civil_from_days(cls.days_from_civil(y, m, d) + int(days))
        return f"{y2:04d}-{m2:02d}-{d2:02d}"


@tool(owner="agent", rw="write")
def activate_homesite_hold_ab3aff61(ctx: ToolContext, reservation_id: str, reserved_date: str,
                                    total_hold_days: int) -> str:
    """Activate the hold on a Homesite Reservation whose required funds have been received, taking
    the homesite off the market for the buyer. One call moves the reservation from awaiting its
    deposit to held and writes its hold expiry date as the reservation date plus the hold term
    given; nothing is posted to the reservation ledger. Afterwards the reservation shows status held
    and the new hold expiry date, the last calendar day of the hold.

    Args:
        reservation_id: Id class — the reference number of the Homesite Reservation to activate, as returned by the Homesite Reservation lookup for the buyer.
        reserved_date: Fixed-format class — the reservation date shown on that same reservation record, written YYYY-MM-DD; it is the day the hold term is counted from, and it is copied unchanged from the record.
        total_hold_days: Fixed-format class — the hold term as a whole number of calendar days from the reservation date to the last day of the hold, an integer of at least 1, never a fraction; the hold expiry date written is the reservation date plus this many days.

    Returns:
        A text rendering of a dictionary with these fields: reservation_id (the reference number of
        the reservation activated), status (always "held" once the call completes) and
        hold_expiry_date (the hold expiry date now on the reservation, YYYY-MM-DD). A receipt with
        status "held" means the activation was recorded.
    """
    expiry = _Calendar.plus_days(reserved_date, total_hold_days)
    ctx.update("homesite_reservations", reservation_id, status="held", hold_expiry_date=expiry)
    return str({"reservation_id": reservation_id, "status": "held", "hold_expiry_date": expiry})


@tool(owner="user", rw="write")
def pay_hold_extension_fee_c522f05c(ctx: ToolContext, reservation_id: str, customer_id: str,
                                    amount: float, payment_method: str, source_payment_ref: str) -> str:
    """Pay, through the Calloway buyer portal, the extension fee for a hold extension on your own
    Homesite Reservation. One call posts one payment received from you to the reservation ledger,
    booked as the extension fee component, dated today, with a new Calloway receipt number; the
    money then shows among the funds held on the reservation. The hold itself is not changed by the
    payment.

    Args:
        reservation_id: Id class — the reference number of your Homesite Reservation that the extension fee is for, as read to you by the Calloway representative from the reservation record.
        customer_id: Id class — your customer reference number on the Calloway buyer profile, as read to you by the Calloway representative from the profile lookup.
        amount: Fixed-format class — the extension fee you are paying, in USD, a positive amount written to 2 decimal places (cents) and booked exactly as entered, with no further rounding.
        payment_method: Enum class — how you pay; exactly one of: card (you pay with a debit or credit card), ach (you pay by bank transfer drawn from your checking or savings account), check (you pay with a personal check), wire (you pay by a wire transfer from your bank), certified_funds (you pay with a cashier's check or other certified funds).
        source_payment_ref: Verbatim class — when this payment replaces a payment of yours that was returned unpaid, the receipt number of that returned payment exactly as it appears on the reservation ledger; an empty string when it replaces no returned payment (verbatim).

    Returns:
        A text rendering of a dictionary with these fields: homesite_event_id (the reference
        number of the ledger entry created), payment_reference (the new Calloway receipt number
        printed for this payment), deposit_component (always "extension_fee"), amount (the amount
        posted, USD with 2 decimal places) and event_date (the posting date, YYYY-MM-DD). A receipt
        carrying a payment_reference means the payment posted.
    """
    rid = ctx.make_id("hev_", reservation_id, customer_id, amount, payment_method, source_payment_ref,
                      "extension_fee")
    receipt = "RCPT-1" + rid[-6:].upper()
    posted = round(float(amount), 2)
    today = ctx.now()[:10]
    ctx.create("homesite_events", rid, homesite_event_id=rid, reservation_id=reservation_id,
               customer_id=customer_id, event_type="homesite_payment_received", amount=posted,
               deposit_component="extension_fee", payment_method=payment_method,
               payment_reference=receipt, source_payment_ref=source_payment_ref, event_date=today)
    return str({"homesite_event_id": rid, "payment_reference": receipt,
                "deposit_component": "extension_fee", "amount": posted, "event_date": today})


@tool(owner="agent", rw="write")
def extend_homesite_hold_1f65db7b(ctx: ToolContext, reservation_id: str, reserved_date: str,
                                  total_hold_days: int, extensions_used: int) -> str:
    """Write a hold extension on a Homesite Reservation, pushing its hold expiry date out. One
    call rewrites the reservation's hold expiry date as the reservation date plus the extended hold
    term given and records the new count of extensions used; nothing is posted to the reservation
    ledger. Afterwards the reservation shows the later hold expiry date and the updated extension
    count.

    Args:
        reservation_id: Id class — the reference number of the Homesite Reservation being extended, as returned by the Homesite Reservation lookup for the buyer.
        reserved_date: Fixed-format class — the reservation date shown on that same reservation record, written YYYY-MM-DD; it is the day the extended hold term is counted from, and it is copied unchanged from the record.
        total_hold_days: Fixed-format class — the extended hold term as a whole number of calendar days from the reservation date to the last day of the extended hold, an integer of at least 1, never a fraction; the hold expiry date written is the reservation date plus this many days.
        extensions_used: Fixed-format class — the number of extensions written on the reservation once this extension is counted, an integer >= 0 (the count on the record before this extension plus one).

    Returns:
        A text rendering of a dictionary with these fields: reservation_id (the reference number of
        the reservation extended), hold_expiry_date (the new hold expiry date, YYYY-MM-DD) and
        extensions_used (the extension count now on the reservation, an integer). A receipt with the
        new hold_expiry_date means the extension was recorded.
    """
    expiry = _Calendar.plus_days(reserved_date, total_hold_days)
    ctx.update("homesite_reservations", reservation_id, hold_expiry_date=expiry,
               extensions_used=int(extensions_used))
    return str({"reservation_id": reservation_id, "hold_expiry_date": expiry,
                "extensions_used": int(extensions_used)})


@tool(owner="agent", rw="write")
def record_reinstatement_fee_fa042025(ctx: ToolContext, reservation_id: str, customer_id: str,
                                      amount: float, payment_method: str, source_payment_ref: str) -> str:
    """Take the buyer's reinstatement fee payment over the phone and post it to the ledger of an
    expired Homesite Reservation. One call posts one payment received from the buyer, booked as the
    reinstatement fee component, dated today, with a new Calloway receipt number; the money then
    shows among the funds held on the reservation. The reservation's status and hold dates are not
    changed by the payment.

    Args:
        reservation_id: Id class — the reference number of the expired Homesite Reservation the fee is for, as returned by the Homesite Reservation lookup for the buyer.
        customer_id: Id class — the customer reference number of the paying buyer, as returned by the customer profile lookup.
        amount: Fixed-format class — the reinstatement fee taken, in USD, a positive amount written to 2 decimal places (cents) and booked exactly as entered, with no further rounding.
        payment_method: Enum class — how the buyer pays; exactly one of: card (the buyer pays with a debit or credit card), ach (the buyer pays by bank transfer drawn from a checking or savings account), check (the buyer pays with a personal check), wire (the buyer pays by a wire transfer from their bank), certified_funds (the buyer pays with a cashier's check or other certified funds).
        source_payment_ref: Verbatim class — when this payment replaces a payment of the buyer's that was returned unpaid, the receipt number of that returned payment exactly as it appears on the reservation ledger; an empty string when it replaces no returned payment (verbatim).

    Returns:
        A text rendering of a dictionary with these fields: homesite_event_id (the reference
        number of the ledger entry created), payment_reference (the new Calloway receipt number
        printed for this payment), deposit_component (always "reinstatement_fee"), amount (the amount
        posted, USD with 2 decimal places) and event_date (the posting date, YYYY-MM-DD). A receipt
        carrying a payment_reference means the payment posted.
    """
    rid = ctx.make_id("hev_", reservation_id, customer_id, amount, payment_method, source_payment_ref,
                      "reinstatement_fee")
    receipt = "RCPT-1" + rid[-6:].upper()
    posted = round(float(amount), 2)
    today = ctx.now()[:10]
    ctx.create("homesite_events", rid, homesite_event_id=rid, reservation_id=reservation_id,
               customer_id=customer_id, event_type="homesite_payment_received", amount=posted,
               deposit_component="reinstatement_fee", payment_method=payment_method,
               payment_reference=receipt, source_payment_ref=source_payment_ref, event_date=today)
    return str({"homesite_event_id": rid, "payment_reference": receipt,
                "deposit_component": "reinstatement_fee", "amount": posted, "event_date": today})


@tool(owner="user", rw="write")
def sign_homesite_release_13bc71ff(ctx: ToolContext, reservation_id: str, customer_id: str,
                                   deposit_receipt: str, deposit_refund: float, premium_fee_receipt: str,
                                   premium_fee_refund: float, premium_fee_retained: float,
                                   refund_method: str) -> str:
    """Sign, as the buyer, the written release of your own held Homesite Reservation together with
    the settlement lines printed on it. One call ends the reservation as released, dated today, and
    books the settlement on its ledger: a refund of the reservation deposit against its receipt, a
    refund of the premium holding fee against its receipt, and, when the amount kept is above zero,
    the share of the premium holding fee Calloway keeps. Afterwards the homesite returns to the
    market and the reservation shows status released with today's end date.

    Args:
        reservation_id: Id class — the reference number of your Homesite Reservation being released, as read to you by the Calloway representative from the reservation record.
        customer_id: Id class — your customer reference number on the Calloway buyer profile, as read to you by the Calloway representative from the profile lookup.
        deposit_receipt: Verbatim class — the receipt number of the payment that paid your reservation deposit, exactly as it appears on the reservation ledger and as read to you (verbatim).
        deposit_refund: Fixed-format class — the reservation deposit refunded to you, in USD, a positive amount written to 2 decimal places (cents) and booked exactly as entered.
        premium_fee_receipt: Verbatim class — the receipt number of the payment that paid your premium holding fee, exactly as it appears on the reservation ledger and as read to you (verbatim).
        premium_fee_refund: Fixed-format class — the part of the premium holding fee refunded to you, in USD, an amount of zero or more written to 2 decimal places (cents) and booked exactly as entered.
        premium_fee_retained: Fixed-format class — the part of the premium holding fee Calloway keeps, in USD, an amount of zero or more written to 2 decimal places (cents); 0.00 books no retained line.
        refund_method: Enum class — how the refunds are returned; exactly one of: original_method (each refund goes back to the account or card the payment came from), check (the refunds are mailed to you as a Calloway check).

    Returns:
        A text rendering of a dictionary with these fields: reservation_id (the reservation
        released), status (always "released" once the call completes), end_date (the release date,
        YYYY-MM-DD), deposit_refund_id and premium_refund_id (reference numbers of the two refund
        ledger entries) and retained_id (reference number of the retained-share ledger entry, or an
        empty string when nothing is kept). A receipt with status "released" means the release and
        its settlement were recorded.
    """
    today = ctx.now()[:10]
    ctx.update("homesite_reservations", reservation_id, status="released", end_date=today)
    dep_id = ctx.make_id("hev_", reservation_id, deposit_receipt, "reservation_deposit", "buyer_release")
    ctx.create("homesite_events", dep_id, homesite_event_id=dep_id, reservation_id=reservation_id,
               customer_id=customer_id, event_type="homesite_refund_issued",
               amount=round(float(deposit_refund), 2), deposit_component="reservation_deposit",
               source_payment_ref=deposit_receipt, refund_reason="buyer_release",
               refund_method=refund_method, event_date=today)
    prem_id = ctx.make_id("hev_", reservation_id, premium_fee_receipt, "premium_holding_fee", "buyer_release")
    ctx.create("homesite_events", prem_id, homesite_event_id=prem_id, reservation_id=reservation_id,
               customer_id=customer_id, event_type="homesite_refund_issued",
               amount=round(float(premium_fee_refund), 2), deposit_component="premium_holding_fee",
               source_payment_ref=premium_fee_receipt, refund_reason="buyer_release",
               refund_method=refund_method, event_date=today)
    kept_id = ""
    if round(float(premium_fee_retained), 2) > 0:
        kept_id = ctx.make_id("hev_", reservation_id, premium_fee_receipt, "premium_holding_fee", "retained")
        ctx.create("homesite_events", kept_id, homesite_event_id=kept_id, reservation_id=reservation_id,
                   customer_id=customer_id, event_type="homesite_funds_retained",
                   amount=round(float(premium_fee_retained), 2), deposit_component="premium_holding_fee",
                   source_payment_ref=premium_fee_receipt, retention_reason="premium_fee_after_window",
                   event_date=today)
    return str({"reservation_id": reservation_id, "status": "released", "end_date": today,
                "deposit_refund_id": dep_id, "premium_refund_id": prem_id, "retained_id": kept_id})


@tool(owner="agent", rw="write")
def reinstate_homesite_hold_f9d4ebfd(ctx: ToolContext, reservation_id: str, customer_id: str,
                                     hold_days: int, reinstatements_used: int) -> str:
    """Reinstate an expired Homesite Reservation on the same homesite, putting the homesite back on
    hold for the buyer. One call moves the reservation from expired to held, clears its end date,
    writes its hold expiry date as today plus the reinstated hold term given, and records the new
    count of reinstatements used; nothing is posted to the reservation ledger. Afterwards the
    reservation shows status held, the new hold expiry date and the updated reinstatement count.

    Args:
        reservation_id: Id class — the reference number of the expired Homesite Reservation to reinstate, as returned by the Homesite Reservation lookup for the buyer.
        customer_id: Id class — the customer reference number of the reserving buyer, as returned by the customer profile lookup; it is written back unchanged as the buyer on the reservation.
        hold_days: Fixed-format class — the reinstated hold term as a whole number of calendar days counted from today, an integer of at least 1, never a fraction; the hold expiry date written is today plus this many days.
        reinstatements_used: Fixed-format class — the number of reinstatements written on the reservation once this one is counted, an integer >= 0 (the count on the record before this reinstatement plus one).

    Returns:
        A text rendering of a dictionary with these fields: reservation_id (the reservation
        reinstated), status (always "held" once the call completes), hold_expiry_date (the new hold
        expiry date, YYYY-MM-DD) and reinstatements_used (the reinstatement count now on the
        reservation, an integer). A receipt with status "held" means the reinstatement was recorded.
    """
    expiry = _Calendar.plus_days(ctx.now()[:10], hold_days)
    ctx.update("homesite_reservations", reservation_id, customer_id=customer_id, status="held",
               hold_expiry_date=expiry, end_date="", reinstatements_used=int(reinstatements_used))
    return str({"reservation_id": reservation_id, "status": "held", "hold_expiry_date": expiry,
                "reinstatements_used": int(reinstatements_used)})

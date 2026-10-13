"""Hidden task tools of the warranty_rework_desk difficulty (Workmanship Warranties).

Each tool performs one atomic write on a warranty coverage's records with the values the caller
supplies. No tool aggregates history, works out an amount or checks a business precondition.
"""

from erlbench import ToolContext, tool


class _Records:
    """Internal record helpers (not a tool)."""

    @staticmethod
    def owner_of(ctx: ToolContext, warranty_coverage_id: str) -> str:
        rows = ctx.find("warranty_coverages", warranty_coverage_id=warranty_coverage_id)
        return rows[0].get("customer_id", "") if rows else ""


@tool(owner="user", rw="write")
def accept_calibration_diagnostic_charge_d9578b72(ctx: ToolContext, warranty_coverage_id: str,
                                                  concern_number: int, amount_usd: float) -> str:
    """The customer accepts the calibration diagnostic charge for a calibration-fault concern that a
    network inspection found not covered under their Calibration Workmanship Warranty. Accepting
    books one diagnostic charge for that concern on the coverage's customer charges account, dated
    today, so the amount becomes owed by the customer and shows on the coverage's money history as a
    diagnostic charge naming the concern. A receipt carrying the new charge entry's reference number
    confirms the charge is booked.

    Args:
        warranty_coverage_id: Id class — reference number of the Calibration Workmanship Warranty
            coverage the inspected concern belongs to, as returned by the warranty coverage lookup.
        concern_number: Fixed-format class — ordinal of the inspected concern on that coverage, an
            integer >= 1, exactly as shown on the concern's report and inspection entries.
        amount_usd: Fixed-format class — the diagnostic charge the customer accepts, in USD, 2 decimal
            places, positive (format: USD, 2 decimal places, positive); the tool stores it rounded to
            2 decimal places.

    Returns:
        A dictionary rendered as text with: status ("booked" on success), warranty_entry_id (the new
        charge entry's reference number, text), warranty_coverage_id (the coverage charged, text),
        concern_number (integer), amount_usd (the amount booked, number with 2 decimal places) and
        entry_date (the booking date, YYYY-MM-DD).
    """
    amount = round(float(amount_usd), 2)
    rid = ctx.make_id("wle_", warranty_coverage_id, concern_number, amount, "calibration_charge")
    entry_date = ctx.now()[:10]
    ctx.create("warranty_ledger", rid, warranty_entry_id=rid, warranty_coverage_id=warranty_coverage_id,
               customer_id=_Records.owner_of(ctx, warranty_coverage_id), event_type="warranty_charge",
               entry_date=entry_date, concern_number=int(concern_number), amount_usd=amount,
               source_entry_id=None)
    return str({"status": "booked", "warranty_entry_id": rid, "warranty_coverage_id": warranty_coverage_id,
                "concern_number": int(concern_number), "amount_usd": amount, "entry_date": entry_date})


@tool(owner="user", rw="write")
def accept_electrical_diagnostic_charge_607d2bcb(ctx: ToolContext, warranty_coverage_id: str,
                                                 concern_number: int, amount_usd: float) -> str:
    """The customer accepts the electrical diagnostic charge for an electrical-part concern that a
    network inspection found not covered under their collision or structural workmanship warranty.
    Accepting books one diagnostic charge for that concern on the coverage's customer charges
    account, dated today, so the amount becomes owed by the customer and shows on the coverage's
    money history as a diagnostic charge naming the concern. A receipt carrying the new charge
    entry's reference number confirms the charge is booked.

    Args:
        warranty_coverage_id: Id class — reference number of the warranty coverage the inspected
            electrical-part concern belongs to, as returned by the warranty coverage lookup.
        concern_number: Fixed-format class — ordinal of the inspected concern on that coverage, an
            integer >= 1, exactly as shown on the concern's report and inspection entries.
        amount_usd: Fixed-format class — the electrical diagnostic charge the customer accepts, in
            USD, 2 decimal places, positive (format: USD, 2 decimal places, positive); the tool stores
            it rounded to 2 decimal places.

    Returns:
        A dictionary rendered as text with: status ("booked" on success), warranty_entry_id (the new
        charge entry's reference number, text), warranty_coverage_id (the coverage charged, text),
        concern_number (integer), amount_usd (the amount booked, number with 2 decimal places) and
        entry_date (the booking date, YYYY-MM-DD).
    """
    amount = round(float(amount_usd), 2)
    rid = ctx.make_id("wle_", warranty_coverage_id, concern_number, amount, "electrical_charge")
    entry_date = ctx.now()[:10]
    ctx.create("warranty_ledger", rid, warranty_entry_id=rid, warranty_coverage_id=warranty_coverage_id,
               customer_id=_Records.owner_of(ctx, warranty_coverage_id), event_type="warranty_charge",
               entry_date=entry_date, concern_number=int(concern_number), amount_usd=amount,
               source_entry_id=None)
    return str({"status": "booked", "warranty_entry_id": rid, "warranty_coverage_id": warranty_coverage_id,
                "concern_number": int(concern_number), "amount_usd": amount, "entry_date": entry_date})


@tool(owner="user", rw="write")
def accept_mechanical_diagnostic_charge_d69f0d58(ctx: ToolContext, warranty_coverage_id: str,
                                                 concern_number: int, amount_usd: float) -> str:
    """The customer accepts the mechanical diagnostic charge for a mechanical-part concern that a
    network inspection found not covered under their collision or structural workmanship warranty.
    Accepting books one diagnostic charge for that concern on the coverage's customer charges
    account, dated today, so the amount becomes owed by the customer and shows on the coverage's
    money history as a diagnostic charge naming the concern. A receipt carrying the new charge
    entry's reference number confirms the charge is booked.

    Args:
        warranty_coverage_id: Id class — reference number of the warranty coverage the inspected
            mechanical-part concern belongs to, as returned by the warranty coverage lookup.
        concern_number: Fixed-format class — ordinal of the inspected concern on that coverage, an
            integer >= 1, exactly as shown on the concern's report and inspection entries.
        amount_usd: Fixed-format class — the mechanical diagnostic charge the customer accepts, in
            USD, 2 decimal places, positive (format: USD, 2 decimal places, positive); the tool stores
            it rounded to 2 decimal places.

    Returns:
        A dictionary rendered as text with: status ("booked" on success), warranty_entry_id (the new
        charge entry's reference number, text), warranty_coverage_id (the coverage charged, text),
        concern_number (integer), amount_usd (the amount booked, number with 2 decimal places) and
        entry_date (the booking date, YYYY-MM-DD).
    """
    amount = round(float(amount_usd), 2)
    rid = ctx.make_id("wle_", warranty_coverage_id, concern_number, amount, "mechanical_charge")
    entry_date = ctx.now()[:10]
    ctx.create("warranty_ledger", rid, warranty_entry_id=rid, warranty_coverage_id=warranty_coverage_id,
               customer_id=_Records.owner_of(ctx, warranty_coverage_id), event_type="warranty_charge",
               entry_date=entry_date, concern_number=int(concern_number), amount_usd=amount,
               source_entry_id=None)
    return str({"status": "booked", "warranty_entry_id": rid, "warranty_coverage_id": warranty_coverage_id,
                "concern_number": int(concern_number), "amount_usd": amount, "entry_date": entry_date})


@tool(owner="agent", rw="write")
def grant_calibration_goodwill_f9a2e5bf(ctx: ToolContext, warranty_coverage_id: str, source_entry_id: str,
                                        amount_usd: float) -> str:
    """Grant a goodwill reduction on one calibration diagnostic charge of a Calibration Workmanship
    Warranty coverage. One call books a goodwill waiver, dated today, against the named charge on
    the coverage's customer charges account, lowering what the customer owes on that charge by the
    amount given; the coverage's money history then shows a goodwill waiver naming the charge. A
    receipt carrying the waiver entry's reference number confirms the reduction is booked.

    Args:
        warranty_coverage_id: Id class — reference number of the Calibration Workmanship Warranty
            coverage that carries the charge, as returned by the warranty coverage lookup.
        source_entry_id: Id class — reference number of the diagnostic charge entry being reduced, as
            shown in the coverage's money history or on the receipt of the charge's booking.
        amount_usd: Fixed-format class — the goodwill reduction, in USD, 2 decimal places, positive
            (format: USD, 2 decimal places, positive); the tool stores it rounded to 2 decimal places.

    Returns:
        A dictionary rendered as text with: status ("waived" on success), warranty_entry_id (the new
        waiver entry's reference number, text), source_entry_id (the charge reduced, text),
        waiver_reason (always "goodwill"), amount_usd (number with 2 decimal places) and entry_date
        (the booking date, YYYY-MM-DD).
    """
    amount = round(float(amount_usd), 2)
    rid = ctx.make_id("wle_", warranty_coverage_id, source_entry_id, amount, "calibration_goodwill")
    entry_date = ctx.now()[:10]
    ctx.create("warranty_ledger", rid, warranty_entry_id=rid, warranty_coverage_id=warranty_coverage_id,
               customer_id=_Records.owner_of(ctx, warranty_coverage_id), event_type="warranty_charge_waiver",
               entry_date=entry_date, source_entry_id=source_entry_id, waiver_reason="goodwill",
               amount_usd=amount)
    return str({"status": "waived", "warranty_entry_id": rid, "source_entry_id": source_entry_id,
                "waiver_reason": "goodwill", "amount_usd": amount, "entry_date": entry_date})


@tool(owner="agent", rw="write")
def book_same_visit_courtesy_9d7b5f0e(ctx: ToolContext, warranty_coverage_id: str, source_entry_id: str,
                                      amount_usd: float) -> str:
    """Book the same-visit courtesy on a collision or structural workmanship warranty coverage: a
    goodwill waiver, dated today, against one parts diagnostic charge (electrical or mechanical) on
    the coverage's customer charges account, lowering what the customer owes on that charge by the
    amount given. The coverage's money history then shows a goodwill waiver naming the charge. A
    receipt carrying the waiver entry's reference number confirms the courtesy is booked.

    Args:
        warranty_coverage_id: Id class — reference number of the warranty coverage that carries the
            charge, as returned by the warranty coverage lookup.
        source_entry_id: Id class — reference number of the parts diagnostic charge entry the courtesy
            is booked against, as shown in the coverage's money history or on the receipt of the
            charge's booking.
        amount_usd: Fixed-format class — the courtesy amount, in USD, 2 decimal places, positive
            (format: USD, 2 decimal places, positive); the tool stores it rounded to 2 decimal places.

    Returns:
        A dictionary rendered as text with: status ("waived" on success), warranty_entry_id (the new
        waiver entry's reference number, text), source_entry_id (the charge the courtesy is booked
        against, text), waiver_reason (always "goodwill"), amount_usd (number with 2 decimal places)
        and entry_date (the booking date, YYYY-MM-DD).
    """
    amount = round(float(amount_usd), 2)
    rid = ctx.make_id("wle_", warranty_coverage_id, source_entry_id, amount, "same_visit_courtesy")
    entry_date = ctx.now()[:10]
    ctx.create("warranty_ledger", rid, warranty_entry_id=rid, warranty_coverage_id=warranty_coverage_id,
               customer_id=_Records.owner_of(ctx, warranty_coverage_id), event_type="warranty_charge_waiver",
               entry_date=entry_date, source_entry_id=source_entry_id, waiver_reason="goodwill",
               amount_usd=amount)
    return str({"status": "waived", "warranty_entry_id": rid, "source_entry_id": source_entry_id,
                "waiver_reason": "goodwill", "amount_usd": amount, "entry_date": entry_date})


@tool(owner="user", rw="write")
def sign_rework_authorization_70486d76(ctx: ToolContext, warranty_coverage_id: str, concern_number: int,
                                       rework_attempt: int, location_code: str,
                                       courtesy_rental_days: int) -> str:
    """The customer signs the authorization for a network rework of a covered concern on their
    workmanship warranty coverage, at a network center, for a rework that disturbs no
    driver-assistance sensor. Signing records one remedy authorization for that concern, dated
    today, as a network rework at the named center with the courtesy rental days the network pays;
    the coverage's concern history then shows the authorized remedy attempt. A receipt carrying the
    authorization's reference number confirms it is recorded.

    Args:
        warranty_coverage_id: Id class — reference number of the warranty coverage the covered concern
            belongs to, as returned by the warranty coverage lookup.
        concern_number: Fixed-format class — ordinal of the covered concern on that coverage, an
            integer >= 1, exactly as shown on the concern's report and inspection entries.
        rework_attempt: Fixed-format class — ordinal of this remedy attempt on the concern, an integer
            >= 1 (format: integer >= 1).
        location_code: Fixed-format class — code of the network center doing the rework, written as 3
            upper-case letters, hyphen, 4 digits (format: 3 upper-case letters, hyphen, 4 digits), as
            shown on the center's entries in the concern history.
        courtesy_rental_days: Fixed-format class — courtesy rental days the network pays with this
            rework, a whole number of rental days (format: integer days); 0 when none.

    Returns:
        A dictionary rendered as text with: status ("authorized" on success), warranty_event_id (the
        authorization's reference number, text), concern_number (integer), rework_attempt (integer),
        rework_kind (always "network_rework"), location_code (text), courtesy_rental_days (integer)
        and event_date (the authorization date, YYYY-MM-DD).
    """
    rid = ctx.make_id("wev_", warranty_coverage_id, concern_number, rework_attempt, location_code,
                      courtesy_rental_days)
    event_date = ctx.now()[:10]
    ctx.create("warranty_events", rid, warranty_event_id=rid, warranty_coverage_id=warranty_coverage_id,
               customer_id=_Records.owner_of(ctx, warranty_coverage_id), event_type="warranty_rework_authorize",
               event_date=event_date, concern_number=int(concern_number), rework_attempt=int(rework_attempt),
               rework_kind="network_rework", location_code=location_code,
               courtesy_rental_days=int(courtesy_rental_days), calibration_needed=False)
    return str({"status": "authorized", "warranty_event_id": rid, "concern_number": int(concern_number),
                "rework_attempt": int(rework_attempt), "rework_kind": "network_rework",
                "location_code": location_code, "courtesy_rental_days": int(courtesy_rental_days),
                "event_date": event_date})

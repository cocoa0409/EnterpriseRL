"""Hidden task tools of the cash_pickup_transfers difficulty (Paloma Remit, Cash Pickup).

Each tool performs one atomic write on a Cash Pickup transfer and takes every policy-decided
value as an argument: the tools judge no eligibility, compute no amount and refuse nothing.
"""

from erlbench import ToolContext, tool


class _Calendar:
    """Pure calendar arithmetic and reference minting shared by the tools (no clock, no randomness)."""

    @staticmethod
    def days_from_civil(y: int, m: int, d: int) -> int:
        y -= m <= 2
        era = (y if y >= 0 else y - 399) // 400
        yoe = y - era * 400
        doy = (153 * (m + (-3 if m > 2 else 9)) + 2) // 5 + d - 1
        doe = yoe * 365 + yoe // 4 - yoe // 100 + doy
        return era * 146097 + doe - 719468

    @staticmethod
    def civil_from_days(z: int) -> str:
        z += 719468
        era = (z if z >= 0 else z - 146096) // 146097
        doe = z - era * 146097
        yoe = (doe - doe // 1460 + doe // 36524 - doe // 146096) // 365
        y = yoe + era * 400
        doy = doe - (365 * yoe + yoe // 4 - yoe // 100)
        mp = (5 * doy + 2) // 153
        d = doy - (153 * mp + 2) // 5 + 1
        m = mp + (3 if mp < 10 else -9)
        y += m <= 2
        return f"{y:04d}-{m:02d}-{d:02d}"

    @staticmethod
    def add_days(ymd: str, days: int) -> str:
        y, m, d = (int(part) for part in str(ymd)[:10].split("-"))
        return _Calendar.civil_from_days(_Calendar.days_from_civil(y, m, d) + int(days))

    @staticmethod
    def pickup_number(seed: str) -> str:
        # A 10-digit Paloma Pickup Number starting with 3, derived from a deterministic row hash.
        digits = str(int(seed.split("_", 1)[1], 16)).rjust(9, "0")
        return "3" + digits[-9:]


@tool(owner="user", rw="write")
def choose_shortfall_reissue_92bb83b1(ctx: ToolContext, cash_transfer_id: str, related_case_id: str,
                                      reissue_window_days: int) -> str:
    """The customer records, in their own name, the choice to have the missing cash of a short Cash
    Pickup payout collected under a re-issue of the shortfall. One call records the choice
    (re-issue of the shortfall) on the customer's incorrect-amount error notice and re-issues the
    transfer at once: the transfer becomes ready for pickup again under a brand-new 10-digit Paloma
    Pickup Number that replaces the old one, it is collectable from today, its last day of
    collection is today plus the window days given, and its collection and closing dates are
    cleared. The recipient can collect with the new Pickup Number from today; the receipt shows the
    recorded choice and the new pickup details.

    Args:
        cash_transfer_id: Id class — the reference number of the Cash Pickup transfer whose payout
            was short, as returned by the Cash Pickup transfer lookup for this customer.
        related_case_id: Id class — the case reference number of the customer's incorrect-amount
            error notice on that transfer, as returned by the Cash Pickup case lookup (the notice
            the error-resolution finding answers).
        reissue_window_days: Fixed-format class — the number of calendar days in the pickup window
            of the re-issue, as a whole non-negative integer; the last day of collection becomes
            today's date plus this many days.

    Returns:
        A dictionary string with: status ("recorded" when the choice and re-issue were written);
        case_id (string, the case reference of the recorded remedy choice); remedy_choice (always
        "reissue_shortfall"); pickup_reference (string, the new 10-digit Paloma Pickup Number);
        available_date (YYYY-MM-DD, today); pickup_expiry_date (YYYY-MM-DD, the new last day of
        collection); transfer_status (always "ready_for_pickup").
    """
    rows = ctx.find("cash_transfers", cash_transfer_id=cash_transfer_id)
    customer_id = rows[0].get("customer_id") if rows else ""
    today = ctx.now()[:10]
    case_id = ctx.make_id("ccs_", cash_transfer_id, related_case_id, reissue_window_days)
    ctx.create("cash_cases", case_id, case_id=case_id, cash_transfer_id=cash_transfer_id,
               customer_id=customer_id, event_type="cash_remedy_chosen", case_date=today,
               case_type="none", refusal_reason="none", rfi_topic="none", correction_seq=0,
               related_case_id=related_case_id, case_outcome="not_applicable",
               remedy_choice="reissue_shortfall")
    pickup_reference = _Calendar.pickup_number(ctx.make_id("pkr_", cash_transfer_id, related_case_id))
    expiry = _Calendar.add_days(today, reissue_window_days)
    ctx.update("cash_transfers", cash_transfer_id, status="ready_for_pickup",
               pickup_reference=pickup_reference, available_date=today,
               pickup_expiry_date=expiry, paid_out_date="", closed_date="")
    return str({"status": "recorded", "case_id": case_id, "remedy_choice": "reissue_shortfall",
                "pickup_reference": pickup_reference, "available_date": today,
                "pickup_expiry_date": expiry, "transfer_status": "ready_for_pickup"})


@tool(owner="agent", rw="write")
def book_shortfall_credit_cb14652e(ctx: ToolContext, cash_transfer_id: str, related_entry_id: str,
                                   amount_usd: float) -> str:
    """Book Paloma's own money into a Cash Pickup transfer as a make-good credit for a short payout
    (credit reason: incorrect-amount shortfall). One call adds one credit entry dated today to the
    transfer's money movements, pointing at the cash payout that was short, and raises the principal
    Paloma holds for the transfer by the amount given. The credit then appears among the
    transfer's money movements and in the principal held.

    Args:
        cash_transfer_id: Id class — the reference number of the Cash Pickup transfer whose payout
            was short, as returned by the Cash Pickup transfer lookup.
        related_entry_id: Id class — the reference number of the cash payout movement the shortfall
            concerns, as returned by the Cash Pickup money-movement lookup for that transfer.
        amount_usd: Fixed-format class — the credit amount in USD, a positive number with 2 decimal
            places (cents), already rounded; it is stored exactly as given.

    Returns:
        A dictionary string with: status ("booked" when the credit was written); ledger_entry_id
        (string, the reference of the new credit movement); credit_reason (always
        "incorrect_amount_shortfall"); amount_usd (number, USD with 2 decimal places, the credit
        booked); principal_held_usd (number, USD with 2 decimal places, the principal Paloma now
        holds for the transfer).
    """
    rows = ctx.find("cash_transfers", cash_transfer_id=cash_transfer_id)
    row = rows[0] if rows else {}
    amount = round(float(amount_usd), 2)
    entry_id = ctx.make_id("cle_", cash_transfer_id, related_entry_id, amount)
    ctx.create("cash_ledger", entry_id, ledger_entry_id=entry_id, cash_transfer_id=cash_transfer_id,
               customer_id=row.get("customer_id", ""), event_type="cash_paloma_credit",
               entry_date=ctx.now()[:10], amount_usd=amount, fee_type="none", fee_seq=0,
               fee_refund_reason="none", payout_seq=0, payout_currency="none", refund_basis="none",
               credit_reason="incorrect_amount_shortfall", related_entry_id=related_entry_id)
    held = round(float(row.get("principal_held_usd") or 0) + amount, 2)
    ctx.update("cash_transfers", cash_transfer_id, principal_held_usd=held)
    return str({"status": "booked", "ledger_entry_id": entry_id,
                "credit_reason": "incorrect_amount_shortfall", "amount_usd": amount,
                "principal_held_usd": held})


@tool(owner="user", rw="write")
def pay_reactivation_fee_6d9bfacd(ctx: ToolContext, cash_transfer_id: str, fee_seq: int,
                                  amount_usd: float) -> str:
    """The customer authorises, in their own name, the card payment of the reactivation fee on one
    of their Cash Pickup transfers. One call collects one reactivation fee charge dated today on
    the transfer's money movements, numbered with the reactivation it pays for, and raises the
    fees Paloma holds for the transfer by the amount given. The charge then appears among the
    transfer's money movements and in the fees held; the pickup itself is not changed.

    Args:
        cash_transfer_id: Id class — the reference number of the Cash Pickup transfer the fee is
            paid on, as returned by the Cash Pickup transfer lookup for this customer.
        fee_seq: Fixed-format class — the number of the reactivation this fee pays for, a whole
            integer counting from 1 (the transfer's reactivation number that the fee pays for).
        amount_usd: Fixed-format class — the fee amount in USD, a non-negative number with 2
            decimal places (cents), already rounded; it is charged exactly as given.

    Returns:
        A dictionary string with: status ("paid" when the charge was written); ledger_entry_id
        (string, the reference of the new fee charge); fee_type (always "reactivation_fee");
        fee_seq (integer, the reactivation number paid for); amount_usd (number, USD with 2
        decimal places, the amount charged); fees_held_usd (number, USD with 2 decimal places, the
        fees Paloma now holds for the transfer).
    """
    rows = ctx.find("cash_transfers", cash_transfer_id=cash_transfer_id)
    row = rows[0] if rows else {}
    amount = round(float(amount_usd), 2)
    seq = int(fee_seq)
    entry_id = ctx.make_id("cle_", cash_transfer_id, "reactivation_fee", seq, amount)
    ctx.create("cash_ledger", entry_id, ledger_entry_id=entry_id, cash_transfer_id=cash_transfer_id,
               customer_id=row.get("customer_id", ""), event_type="cash_fee_charged",
               entry_date=ctx.now()[:10], amount_usd=amount, fee_type="reactivation_fee",
               fee_seq=seq, fee_refund_reason="none", payout_seq=0, payout_currency="none",
               refund_basis="none", credit_reason="none")
    held = round(float(row.get("fees_held_usd") or 0) + amount, 2)
    ctx.update("cash_transfers", cash_transfer_id, fees_held_usd=held)
    return str({"status": "paid", "ledger_entry_id": entry_id, "fee_type": "reactivation_fee",
                "fee_seq": seq, "amount_usd": amount, "fees_held_usd": held})


@tool(owner="agent", rw="write")
def reactivate_expired_pickup_d4e94bda(ctx: ToolContext, cash_transfer_id: str,
                                       pickup_window_days: int) -> str:
    """Make an expired Cash Pickup transfer collectable again with a new pickup window. One call
    returns the transfer to ready for pickup with the same Pickup Number, rate and cash amount,
    makes it collectable from today, sets its last day of collection to today plus the window days
    given, clears its expiry date and raises its reactivation count by one. The recipient can
    collect again from today with the same Pickup Number.

    Args:
        cash_transfer_id: Id class — the reference number of the expired Cash Pickup transfer, as
            returned by the Cash Pickup transfer lookup for this customer.
        pickup_window_days: Fixed-format class — the number of calendar days in the new pickup
            window, as a whole non-negative integer; the last day of collection becomes today's
            date plus this many days.

    Returns:
        A dictionary string with: status ("reactivated" when the transfer was made collectable);
        transfer_status (always "ready_for_pickup"); available_date (YYYY-MM-DD, today);
        pickup_expiry_date (YYYY-MM-DD, the new last day of collection); reactivation_count
        (integer, reactivations on the transfer including this one); pickup_reference (string, the
        unchanged 10-digit Pickup Number).
    """
    rows = ctx.find("cash_transfers", cash_transfer_id=cash_transfer_id)
    row = rows[0] if rows else {}
    today = ctx.now()[:10]
    expiry = _Calendar.add_days(today, pickup_window_days)
    count = int(row.get("reactivation_count") or 0) + 1
    ctx.update("cash_transfers", cash_transfer_id, status="ready_for_pickup", available_date=today,
               pickup_expiry_date=expiry, expired_date="", reactivation_count=count)
    return str({"status": "reactivated", "transfer_status": "ready_for_pickup",
                "available_date": today, "pickup_expiry_date": expiry,
                "reactivation_count": count, "pickup_reference": row.get("pickup_reference", "")})


@tool(owner="user", rw="write")
def pay_name_correction_fee_e426b8ef(ctx: ToolContext, cash_transfer_id: str, fee_seq: int,
                                     amount_usd: float) -> str:
    """The customer authorises, in their own name, the card payment of the name-correction fee on
    one of their Cash Pickup transfers. One call collects one name-correction fee charge dated today
    on the transfer's money movements, numbered with the correction it pays for, and raises the fees
    Paloma holds for the transfer by the amount given. The charge then appears among the transfer's
    money movements and in the fees held; the recipient name itself is not changed.

    Args:
        cash_transfer_id: Id class — the reference number of the Cash Pickup transfer the fee is
            paid on, as returned by the Cash Pickup transfer lookup for this customer.
        fee_seq: Fixed-format class — the number of the name correction this fee pays for, a whole
            integer counting from 1 (the transfer's correction number that the fee pays for).
        amount_usd: Fixed-format class — the fee amount in USD, a non-negative number with 2
            decimal places (cents), already rounded; it is charged exactly as given.

    Returns:
        A dictionary string with: status ("paid" when the charge was written); ledger_entry_id
        (string, the reference of the new fee charge); fee_type (always "name_correction_fee");
        fee_seq (integer, the correction number paid for); amount_usd (number, USD with 2 decimal
        places, the amount charged); fees_held_usd (number, USD with 2 decimal places, the fees
        Paloma now holds for the transfer).
    """
    rows = ctx.find("cash_transfers", cash_transfer_id=cash_transfer_id)
    row = rows[0] if rows else {}
    amount = round(float(amount_usd), 2)
    seq = int(fee_seq)
    entry_id = ctx.make_id("cle_", cash_transfer_id, "name_correction_fee", seq, amount)
    ctx.create("cash_ledger", entry_id, ledger_entry_id=entry_id, cash_transfer_id=cash_transfer_id,
               customer_id=row.get("customer_id", ""), event_type="cash_fee_charged",
               entry_date=ctx.now()[:10], amount_usd=amount, fee_type="name_correction_fee",
               fee_seq=seq, fee_refund_reason="none", payout_seq=0, payout_currency="none",
               refund_basis="none", credit_reason="none")
    held = round(float(row.get("fees_held_usd") or 0) + amount, 2)
    ctx.update("cash_transfers", cash_transfer_id, fees_held_usd=held)
    return str({"status": "paid", "ledger_entry_id": entry_id, "fee_type": "name_correction_fee",
                "fee_seq": seq, "amount_usd": amount, "fees_held_usd": held})


@tool(owner="agent", rw="write")
def record_name_correction_726c5192(ctx: ToolContext, cash_transfer_id: str, corrected_name: str,
                                    extension_days: int) -> str:
    """Record a spelling correction of the recipient name on a Cash Pickup transfer and move its
    last day of collection later. One call adds one name-correction case dated today (keeping the
    name it replaces and numbered as the next correction on the transfer), replaces the name the
    cash is released to with the corrected name at once, and moves the last day of collection later
    by the extension days given; the Pickup Number does not change. The recipient can then collect
    with an ID showing the corrected name.

    Args:
        cash_transfer_id: Id class — the reference number of the Cash Pickup transfer whose
            recipient name is corrected, as returned by the Cash Pickup transfer lookup.
        corrected_name: Verbatim class — the recipient's full name exactly as the customer spells it
            from the recipient's government ID, copied character for character with its accents,
            spacing and capitals, with no translation, normalisation, summarisation, addition or
            deletion (verbatim).
        extension_days: Fixed-format class — the number of calendar days by which the last day of
            collection moves later, as a whole non-negative integer (0 keeps it unchanged).

    Returns:
        A dictionary string with: status ("corrected" when the correction was recorded); case_id
        (string, the reference of the correction case); correction_seq (integer, the number of this
        correction on the transfer); previous_name (string, the name replaced); corrected_name
        (string, the name the cash is now released to); pickup_expiry_date (YYYY-MM-DD, the last day
        of collection including the extension).
    """
    rows = ctx.find("cash_transfers", cash_transfer_id=cash_transfer_id)
    row = rows[0] if rows else {}
    seq = len(ctx.find("cash_cases", cash_transfer_id=cash_transfer_id,
                       event_type="cash_name_corrected")) + 1
    previous = row.get("recipient_name_on_transfer", "")
    case_id = ctx.make_id("ccs_", cash_transfer_id, corrected_name, seq)
    ctx.create("cash_cases", case_id, case_id=case_id, cash_transfer_id=cash_transfer_id,
               customer_id=row.get("customer_id", ""), event_type="cash_name_corrected",
               case_date=ctx.now()[:10], case_type="none", refusal_reason="none", rfi_topic="none",
               previous_name=previous, corrected_name=corrected_name, correction_seq=seq,
               case_outcome="not_applicable", remedy_choice="not_applicable")
    expiry = _Calendar.add_days(row.get("pickup_expiry_date") or ctx.now()[:10], extension_days)
    ctx.update("cash_transfers", cash_transfer_id, recipient_name_on_transfer=corrected_name,
               pickup_expiry_date=expiry)
    return str({"status": "corrected", "case_id": case_id, "correction_seq": seq,
                "previous_name": previous, "corrected_name": corrected_name,
                "pickup_expiry_date": expiry})

"""Hidden task tools of the respite_and_trial_stays difficulty (Larkspur Senior Living).

Each tool performs one atomic posting on a respite or trial stay with the values the agent (or the
customer, for an owner=user tool) supplies; none of them checks a policy condition or computes an amount.
"""

from erlbench import ToolContext, tool



@tool(owner="agent", rw="write")
def credit_relevel_nights_cb1c5023(ctx: ToolContext, respite_stay_id: str, source_entry_id: str,
                                   credited_nights: int, credit_amount: float) -> str:
    """Post a level-change adjustment credit on a respite or trial stay account: the nights of an existing
    nightly charge segment that move to another care level are credited back against that segment. One call
    records one credit entry with the reason level_change_adjustment, dated today, referencing the segment
    credited and stating the nights credited, and lowers the stay balance by the credit amount. The guest
    sees the credit on the stay statement and a lower balance owed.

    Args:
        respite_stay_id: Id class — reference number of the respite or trial stay whose account is credited, as returned by the stay lookup.
        source_entry_id: Id class — reference number of the nightly charge segment entry being credited, as returned by the stay ledger lookup.
        credited_nights: Fixed-format class — number of nights credited back, an integer count of nights.
        credit_amount: Fixed-format class — amount of the credit in USD, a positive number with 2 decimal places, already rounded half up to the cent.

    Returns:
        A confirmation sentence naming the new credit entry reference number, the stay reference number, the
        nights credited, the credit amount in USD with 2 decimal places and the resulting stay balance;
        a returned entry reference number means the credit was posted.
    """
    stay = ctx.find("respite_stays", respite_stay_id=respite_stay_id)
    row = stay[0] if stay else {}
    amount = round(float(credit_amount), 2)
    rid = ctx.make_id("rsl_", respite_stay_id, source_entry_id, credited_nights, credit_amount)
    ctx.create("respite_ledger", rid, respite_entry_id=rid, respite_stay_id=respite_stay_id,
               customer_id=row.get("customer_id"), event_type="respite_credit", amount=amount,
               posting_date=ctx.now()[:10], credit_reason="level_change_adjustment",
               source_entry_id=source_entry_id, nights=int(credited_nights))
    balance = round(float(row.get("account_balance") or 0) - amount, 2)
    ctx.update("respite_stays", respite_stay_id, account_balance=balance)
    return (f"Level-change adjustment credit {rid} posted on stay {respite_stay_id}: {int(credited_nights)} nights, "
            f"{amount:.2f} USD; stay balance now {balance:.2f} USD.")


@tool(owner="agent", rw="write")
def charge_relevel_segment_3be81426(ctx: ToolContext, respite_stay_id: str, tier_billed: str,
                                    segment_start_date: str, segment_end_date: str, nights: int,
                                    segment_amount: float) -> str:
    """Post a level-change nightly charge segment on a respite or trial stay account: consecutive nights of the
    stay are charged at the care level a level change placed the guest in. One call records one nightly charge entry with the
    basis level_change, dated today, naming the stay type billed, the first and last night of the segment and
    its nights, and raises the stay balance by the segment amount. The guest sees the segment on the stay
    statement and a higher balance owed.

    Args:
        respite_stay_id: Id class — reference number of the respite or trial stay being charged, as returned by the stay lookup.
        tier_billed: Enum class — stay type whose nights the segment bills, exactly one of: Independent Living Trial Stay (the segment bills nights of an independent living trial stay); Assisted Living Respite Stay (Standard Care) (the segment bills nights at the standard assisted living respite care level); Assisted Living Respite Stay (Enhanced Care) (the segment bills nights at the enhanced assisted living respite care level); Assisted Living Respite Stay (Extensive Care) (the segment bills nights at the extensive assisted living respite care level); Memory Care Respite Stay (the segment bills nights of a memory care respite stay); Post-Hospital Recovery Stay (the segment bills nights of a post-hospital recovery stay).
        segment_start_date: Fixed-format class — first night of the segment, a calendar date written YYYY-MM-DD.
        segment_end_date: Fixed-format class — last night of the segment, a calendar date written YYYY-MM-DD.
        nights: Fixed-format class — number of nights in the segment, an integer count of nights.
        segment_amount: Fixed-format class — amount charged for the segment in USD, a positive number with 2 decimal places, already rounded half up to the cent.

    Returns:
        A confirmation sentence naming the new charge entry reference number, the stay reference number, the
        stay type billed, the first and last night (YYYY-MM-DD), the nights, the amount in USD with 2 decimal
        places and the resulting stay balance; a returned entry reference number means the segment was posted.
    """
    stay = ctx.find("respite_stays", respite_stay_id=respite_stay_id)
    row = stay[0] if stay else {}
    amount = round(float(segment_amount), 2)
    rid = ctx.make_id("rsl_", respite_stay_id, tier_billed, segment_start_date, segment_end_date, nights, segment_amount)
    ctx.create("respite_ledger", rid, respite_entry_id=rid, respite_stay_id=respite_stay_id,
               customer_id=row.get("customer_id"), event_type="respite_nightly_charge", amount=amount,
               posting_date=ctx.now()[:10], charge_basis="level_change", tier_billed=tier_billed,
               segment_start_date=segment_start_date, segment_end_date=segment_end_date, nights=int(nights))
    balance = round(float(row.get("account_balance") or 0) + amount, 2)
    ctx.update("respite_stays", respite_stay_id, account_balance=balance)
    return (f"Level-change segment {rid} posted on stay {respite_stay_id}: {tier_billed}, {segment_start_date} to "
            f"{segment_end_date}, {int(nights)} nights, {amount:.2f} USD; stay balance now {balance:.2f} USD.")


@tool(owner="user", rw="write")
def sign_stay_extension_37758bab(ctx: ToolContext, customer_id: str, respite_stay_id: str,
                                 respite_request_id: str, extension_charge: float) -> str:
    """Sign, as the guest or the guest's financial representative, an extension request that the desk has
    registered on a respite or trial stay, and book the added nights. One call marks the request signed, moves
    the stay's planned departure date to the date stated on the request, adds one to the stay's extension
    count, records one nightly charge entry with the basis extension covering the added nights (from the old
    planned departure date up to the new planned departure date, that date itself not included) at the stay type on record, and raises the
    stay balance by the extension charge. The signer sees the new departure date and the extension charge on
    the stay statement.

    Args:
        customer_id: Id class — reference number of the guest the stay belongs to, as returned by the customer lookup.
        respite_stay_id: Id class — reference number of the respite or trial stay being extended, as returned by the stay lookup.
        respite_request_id: Id class — reference number of the extension request awaiting signature, as returned by the stay request lookup.
        extension_charge: Fixed-format class — amount charged for the added nights in USD, a positive number with 2 decimal places, already rounded half up to the cent.

    Returns:
        A confirmation sentence naming the signed request reference number, the new extension charge entry
        reference number, the stay reference number, the new planned departure date (YYYY-MM-DD), the added
        nights, the extension charge in USD with 2 decimal places and the resulting stay balance; a
        returned entry reference number means the extension was signed and booked.
    """
    def _day_number(ymd: str) -> int:
        """Days since 0000-03-01 of a 'YYYY-MM-DD' calendar date (proleptic Gregorian, pure arithmetic)."""
        y, m, d = (int(part) for part in ymd[:10].split("-"))
        y -= m <= 2
        era = y // 400
        yoe = y - era * 400
        doy = (153 * (m + (-3 if m > 2 else 9)) + 2) // 5 + d - 1
        doe = yoe * 365 + yoe // 4 - yoe // 100 + doy
        return era * 146097 + doe

    def _ymd(day_number: int) -> str:
        """Inverse of _day_number: the 'YYYY-MM-DD' calendar date of a day number."""
        era = day_number // 146097
        doe = day_number - era * 146097
        yoe = (doe - doe // 1460 + doe // 36524 - doe // 146096) // 365
        doy = doe - (365 * yoe + yoe // 4 - yoe // 100)
        mp = (5 * doy + 2) // 153
        d = doy - (153 * mp + 2) // 5 + 1
        m = mp + (3 if mp < 10 else -9)
        y = yoe + era * 400 + (m <= 2)
        return f"{y:04d}-{m:02d}-{d:02d}"

    stay = ctx.find("respite_stays", respite_stay_id=respite_stay_id)
    row = stay[0] if stay else {}
    req = ctx.find("respite_requests", respite_request_id=respite_request_id)
    new_departure = (req[0].get("requested_date") if req else "") or ""
    old_departure = row.get("planned_departure_date") or ""
    first_night = _day_number(old_departure)
    last_night = _day_number(new_departure) - 1
    added = last_night - first_night + 1
    amount = round(float(extension_charge), 2)
    ctx.update("respite_requests", respite_request_id, request_status="signed")
    rid = ctx.make_id("rsl_", customer_id, respite_stay_id, respite_request_id, extension_charge)
    ctx.create("respite_ledger", rid, respite_entry_id=rid, respite_stay_id=respite_stay_id,
               customer_id=customer_id, event_type="respite_nightly_charge", amount=amount,
               posting_date=ctx.now()[:10], charge_basis="extension", tier_billed=row.get("variant_name"),
               segment_start_date=_ymd(first_night), segment_end_date=_ymd(last_night), nights=added)
    balance = round(float(row.get("account_balance") or 0) + amount, 2)
    ctx.update("respite_stays", respite_stay_id, planned_departure_date=new_departure,
               extensions_count=int(row.get("extensions_count") or 0) + 1, account_balance=balance)
    return (f"Extension request {respite_request_id} signed; extension segment {rid} posted on stay {respite_stay_id}: "
            f"new planned departure {new_departure}, {added} added nights, {amount:.2f} USD; "
            f"stay balance now {balance:.2f} USD.")


@tool(owner="agent", rw="write")
def post_returned_payment_fee_57d4cb7a(ctx: ToolContext, respite_stay_id: str, source_entry_id: str,
                                       fee_amount: float) -> str:
    """Post the returned-payment fee on a respite or trial stay account for one payment that the bank returned
    unpaid. One call records one add-on charge entry with the add-on code returned_payment, dated today,
    referencing the returned-payment entry it arises from, and raises the stay balance by the fee. The guest
    sees the fee on the stay statement and a higher balance owed.

    Args:
        respite_stay_id: Id class — reference number of the respite or trial stay being charged, as returned by the stay lookup.
        source_entry_id: Id class — reference number of the returned-payment entry the fee arises from, as returned by the stay ledger lookup.
        fee_amount: Fixed-format class — amount of the fee in USD, a positive number with 2 decimal places, already rounded half up to the cent.

    Returns:
        A confirmation sentence naming the new fee entry reference number, the stay reference number, the
        returned-payment entry referenced, the fee in USD with 2 decimal places and the resulting stay balance;
        a returned entry reference number means the fee was posted.
    """
    stay = ctx.find("respite_stays", respite_stay_id=respite_stay_id)
    row = stay[0] if stay else {}
    amount = round(float(fee_amount), 2)
    rid = ctx.make_id("rsl_", respite_stay_id, source_entry_id, fee_amount)
    ctx.create("respite_ledger", rid, respite_entry_id=rid, respite_stay_id=respite_stay_id,
               customer_id=row.get("customer_id"), event_type="respite_addon_charge", amount=amount,
               posting_date=ctx.now()[:10], addon_code="returned_payment", service_date=ctx.now()[:10],
               quantity=1, source_entry_id=source_entry_id)
    balance = round(float(row.get("account_balance") or 0) + amount, 2)
    ctx.update("respite_stays", respite_stay_id, account_balance=balance)
    return (f"Returned-payment fee {rid} posted on stay {respite_stay_id} for returned entry {source_entry_id}: "
            f"{amount:.2f} USD; stay balance now {balance:.2f} USD.")


@tool(owner="agent", rw="write")
def post_medication_setup_fee_0971281c(ctx: ToolContext, respite_stay_id: str, setup_amount: float) -> str:
    """Post the medication setup charge on a respite or trial stay account, covering the pharmacy packaging and
    the medication administration record for the stay. One call records one add-on charge entry with the
    add-on code medication_setup, dated today with today as the service date and a quantity of one, and raises
    the stay balance by the charge. The guest sees the charge on the stay statement and a higher balance owed.

    Args:
        respite_stay_id: Id class — reference number of the respite or trial stay being charged, as returned by the stay lookup.
        setup_amount: Fixed-format class — amount of the medication setup charge in USD, a positive number with 2 decimal places, already rounded half up to the cent.

    Returns:
        A confirmation sentence naming the new charge entry reference number, the stay reference number, the
        charge in USD with 2 decimal places and the resulting stay balance; a returned entry reference number
        means the charge was posted.
    """
    stay = ctx.find("respite_stays", respite_stay_id=respite_stay_id)
    row = stay[0] if stay else {}
    amount = round(float(setup_amount), 2)
    rid = ctx.make_id("rsl_", respite_stay_id, setup_amount)
    ctx.create("respite_ledger", rid, respite_entry_id=rid, respite_stay_id=respite_stay_id,
               customer_id=row.get("customer_id"), event_type="respite_addon_charge", amount=amount,
               posting_date=ctx.now()[:10], addon_code="medication_setup", service_date=ctx.now()[:10], quantity=1)
    balance = round(float(row.get("account_balance") or 0) + amount, 2)
    ctx.update("respite_stays", respite_stay_id, account_balance=balance)
    return (f"Medication setup charge {rid} posted on stay {respite_stay_id}: {amount:.2f} USD; "
            f"stay balance now {balance:.2f} USD.")


@tool(owner="user", rw="write")
def pay_stay_advance_b4214d09(ctx: ToolContext, respite_stay_id: str, payment_method: str, amount: float) -> str:
    """Pay, as the guest or the guest's financial representative, the advance on a booked respite or trial stay
    in one payment. One call records one payment entry from the guest or family, dated today, with the
    instrument used and a payment reference issued for the transaction, and lowers the stay balance by the
    amount paid. The payer sees the payment and its reference on the stay statement.

    Args:
        respite_stay_id: Id class — reference number of the respite or trial stay being paid, as given by the agent from the stay lookup.
        payment_method: Enum class — instrument the payment is made with, exactly one of: ach_one_time (a one-time debit from a bank account); check (a personal check); certified_check (a certified or cashier's check); credit_card (a credit card); debit_card (a debit card); insurer_eft (an electronic transfer from a long-term care insurer).
        amount: Fixed-format class — amount paid in USD, a positive number with 2 decimal places, already rounded half up to the cent.

    Returns:
        A confirmation sentence naming the new payment entry reference number, the payment reference issued,
        the stay reference number, the instrument, the amount in USD with 2 decimal places and the resulting
        stay balance; a returned entry reference number means the payment was recorded.
    """
    stay = ctx.find("respite_stays", respite_stay_id=respite_stay_id)
    row = stay[0] if stay else {}
    paid = round(float(amount), 2)
    rid = ctx.make_id("rsl_", respite_stay_id, payment_method, amount)
    reference = f"ADV-{rid[-8:].upper()}"
    ctx.create("respite_ledger", rid, respite_entry_id=rid, respite_stay_id=respite_stay_id,
               customer_id=row.get("customer_id"), event_type="respite_payment", amount=paid,
               posting_date=ctx.now()[:10], payment_reference=reference, payment_method=payment_method,
               payer_type="resident_or_family")
    balance = round(float(row.get("account_balance") or 0) - paid, 2)
    ctx.update("respite_stays", respite_stay_id, account_balance=balance)
    return (f"Payment {rid} recorded on stay {respite_stay_id}: reference {reference}, {payment_method}, "
            f"{paid:.2f} USD; stay balance now {balance:.2f} USD.")

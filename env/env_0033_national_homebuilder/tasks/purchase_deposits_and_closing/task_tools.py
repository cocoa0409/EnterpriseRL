"""Hidden task tools for the purchase_deposits_and_closing difficulty (Calloway Homes, Home Purchase
Agreement). Each tool lands one atomic write on a Home Purchase Agreement; every value it records is
passed in by the caller and no tool judges eligibility, order or amount.
"""

from erlbench import ToolContext, tool


@tool(owner="agent", rw="write")
def assess_closing_delay_per_diem_8d15ee11(ctx: ToolContext, purchase_id: str, period_start: str,
                                          period_end: str, amount: float) -> str:
    """Book one closing delay per diem charge on a Home Purchase Agreement for one period of buyer
    delay. One call adds a single charge line of type closing delay per diem to the agreement's buyer
    statement, recording the delay period's start date and end date and the amount charged, dated
    today, under a newly printed charge number; the agreement's fees-and-per-diem balance owed by the
    buyer rises by the same amount. The buyer sees the new charge line, with its charge number and
    period, on the statement.

    Args:
        purchase_id: Id class — the reference number identifying the Home Purchase Agreement being
            charged, as returned by the purchase agreement lookup for this buyer.
        period_start: Fixed-format class — the calendar date the charged delay period starts on,
            written YYYY-MM-DD (local calendar date, no time part).
        period_end: Fixed-format class — the calendar date the charged delay period ends on, written
            YYYY-MM-DD (local calendar date, no time part).
        amount: Fixed-format class — the per diem charged for the period, in USD, a positive number
            rounded to 2 decimal places.

    Returns:
        A dictionary rendered as text with the keys: status ("booked" when the charge line was
        written), purchase_event_id (reference number of the new charge line), charge_reference (the
        charge number printed on the buyer statement, CHG-HP- followed by four digits), purchase_id,
        period_start and period_end (YYYY-MM-DD), amount (USD, 2 decimal places) and
        buyer_charges_due (USD, 2 decimal places: the fees and per diem the buyer now owes on the
        agreement).
    """
    rows = ctx.find("purchase_agreements", purchase_id=purchase_id)
    if not rows:
        return f"Error: no Home Purchase Agreement {purchase_id}."
    agreement = rows[0]
    rid = ctx.make_id("pev_", purchase_id, "closing_delay_per_diem", period_start, period_end, amount)
    charge_reference = f"CHG-HP-2{int(rid[-8:], 16) % 1000:03d}"
    booked = round(float(amount), 2)
    ctx.create("purchase_events", rid, purchase_event_id=rid, purchase_id=purchase_id,
               customer_id=agreement.get("customer_id"), event_type="purchase_charge_assessed",
               amount=booked, charge_type="closing_delay_per_diem", charge_reference=charge_reference,
               period_start=str(period_start)[:10], period_end=str(period_end)[:10],
               event_date=ctx.now()[:10])
    owed = round(float(agreement.get("buyer_charges_due") or 0) + booked, 2)
    ctx.update("purchase_agreements", purchase_id, buyer_charges_due=owed)
    return str({"status": "booked", "purchase_event_id": rid, "charge_reference": charge_reference,
                "purchase_id": purchase_id, "period_start": str(period_start)[:10],
                "period_end": str(period_end)[:10], "amount": booked, "buyer_charges_due": owed})


@tool(owner="user", rw="write")
def sign_closing_extension_addendum_c0ddd0a3(ctx: ToolContext, purchase_id: str, extension_days: int) -> str:
    """The buyer signs a closing extension addendum on their own Home Purchase Agreement. One call
    moves the agreement's scheduled closing date later by the stated number of calendar days and
    counts one more buyer-requested closing extension on the agreement. The buyer sees the new
    scheduled closing date on the agreement and in the signed addendum receipt.

    Args:
        purchase_id: Id class — the reference number identifying the buyer's Home Purchase Agreement,
            as given to the buyer by the representative from the purchase agreement record.
        extension_days: Fixed-format class — how many calendar days later the scheduled closing date
            moves, counted from the current scheduled closing date; a positive integer number of days.

    Returns:
        A dictionary rendered as text with the keys: status ("signed" when the addendum took effect),
        purchase_id, previous_closing_date (YYYY-MM-DD, the scheduled closing date replaced),
        new_closing_date (YYYY-MM-DD, the scheduled closing date now in force) and
        closing_extensions_used (integer count of buyer-requested closing extensions now written on the
        agreement).
    """
    def serial(iso):
        y, m, d = (int(p) for p in str(iso)[:10].split("-"))
        y -= m <= 2
        era = (y if y >= 0 else y - 399) // 400
        yoe = y - era * 400
        doy = (153 * (m + (-3 if m > 2 else 9)) + 2) // 5 + d - 1
        return era * 146097 + yoe * 365 + yoe // 4 - yoe // 100 + doy - 719468

    def civil(z):
        z += 719468
        era = (z if z >= 0 else z - 146096) // 146097
        doe = z - era * 146097
        yoe = (doe - doe // 1460 + doe // 36524 - doe // 146096) // 365
        doy = doe - (365 * yoe + yoe // 4 - yoe // 100)
        mp = (5 * doy + 2) // 153
        d = doy - (153 * mp + 2) // 5 + 1
        m = mp + (3 if mp < 10 else -9)
        return f"{yoe + era * 400 + (m <= 2):04d}-{m:02d}-{d:02d}"

    rows = ctx.find("purchase_agreements", purchase_id=purchase_id)
    if not rows:
        return f"Error: no Home Purchase Agreement {purchase_id}."
    agreement = rows[0]
    previous = str(agreement.get("scheduled_closing_date") or "")[:10]
    if not previous:
        return f"Error: Home Purchase Agreement {purchase_id} has no scheduled closing date to move."
    moved = civil(serial(previous) + int(extension_days))
    used = int(agreement.get("closing_extensions_used") or 0) + 1
    ctx.update("purchase_agreements", purchase_id, scheduled_closing_date=moved, closing_extensions_used=used)
    return str({"status": "signed", "purchase_id": purchase_id, "previous_closing_date": previous,
                "new_closing_date": moved, "closing_extensions_used": used})


@tool(owner="agent", rw="write")
def assess_returned_payment_fee_3b45ee8d(ctx: ToolContext, purchase_id: str, source_payment_ref: str,
                                         amount: float) -> str:
    """Book the returned-payment fee for one deposit payment that the buyer's bank returned unpaid on a
    Home Purchase Agreement. One call adds a single charge line of type returned payment fee to the
    agreement's buyer statement, naming the receipt number of the returned payment and the amount
    charged, dated today, under a newly printed charge number; the agreement's fees-and-per-diem balance
    owed by the buyer rises by the same amount. The buyer sees the charge line on the statement.

    Args:
        purchase_id: Id class — the reference number identifying the Home Purchase Agreement the returned
            payment belonged to, as returned by the purchase agreement lookup for this buyer.
        source_payment_ref: Verbatim class — the receipt number of the returned deposit payment exactly as
            it appears on the returned-payment entry of the agreement ledger, copied character for
            character (verbatim).
        amount: Fixed-format class — the returned-payment fee charged, in USD, a positive number rounded to
            2 decimal places.

    Returns:
        A dictionary rendered as text with the keys: status ("booked" when the charge line was written),
        purchase_event_id (reference number of the new charge line), charge_reference (the charge number
        printed on the buyer statement, CHG-HP- followed by four digits), purchase_id, source_payment_ref
        (the returned payment's receipt number), amount (USD, 2 decimal places) and buyer_charges_due
        (USD, 2 decimal places: the fees and per diem the buyer now owes on the agreement).
    """
    rows = ctx.find("purchase_agreements", purchase_id=purchase_id)
    if not rows:
        return f"Error: no Home Purchase Agreement {purchase_id}."
    agreement = rows[0]
    rid = ctx.make_id("pev_", purchase_id, "returned_payment_fee", source_payment_ref, amount)
    charge_reference = f"CHG-HP-2{int(rid[-8:], 16) % 1000:03d}"
    booked = round(float(amount), 2)
    ctx.create("purchase_events", rid, purchase_event_id=rid, purchase_id=purchase_id,
               customer_id=agreement.get("customer_id"), event_type="purchase_charge_assessed",
               amount=booked, charge_type="returned_payment_fee", charge_reference=charge_reference,
               source_payment_ref=source_payment_ref, event_date=ctx.now()[:10])
    owed = round(float(agreement.get("buyer_charges_due") or 0) + booked, 2)
    ctx.update("purchase_agreements", purchase_id, buyer_charges_due=owed)
    return str({"status": "booked", "purchase_event_id": rid, "charge_reference": charge_reference,
                "purchase_id": purchase_id, "source_payment_ref": source_payment_ref, "amount": booked,
                "buyer_charges_due": owed})


@tool(owner="user", rw="write")
def wire_replacement_deposit_5b0eb18e(ctx: ToolContext, purchase_id: str, source_payment_ref: str,
                                      deposit_component: str, amount: float) -> str:
    """The buyer wires replacement funds from their own bank account for a deposit payment that was
    returned unpaid on their Home Purchase Agreement. One call posts a single deposit of the wired amount
    to the agreement under the stated deposit component, paid by wire and dated today, naming the
    receipt number of the returned payment it replaces; a new Calloway receipt number is printed for the
    wire, and the deposits Calloway holds on the agreement rise by the amount. The buyer sees the posted
    deposit and its receipt number.

    Args:
        purchase_id: Id class — the reference number identifying the buyer's Home Purchase Agreement, as
            given to the buyer by the representative from the purchase agreement record.
        source_payment_ref: Verbatim class — the receipt number of the returned payment being replaced,
            as the representative reads it out from the agreement ledger, copied character for character
            (verbatim).
        deposit_component: Enum class — the deposit the replacement funds belong to, the same deposit the
            returned payment had funded: initial_earnest_money when the returned payment funded the
            initial earnest money; additional_deposit when it funded the additional deposit due once
            construction started; lot_premium_deposit when it funded the lot premium deposit;
            contingency_deposit when it funded the extra deposit for a home-sale contingency;
            outside_lender_deposit when it funded the extra deposit for outside-lender or cash financing;
            concurrent_agreement_deposit when it funded the extra deposit owed for a second open agreement;
            reservation_transfer when it concerned money moved from a converted homesite reservation.
        amount: Fixed-format class — the replacement funds wired, in USD, a positive number rounded to 2
            decimal places.

    Returns:
        A dictionary rendered as text with the keys: status ("posted" when the deposit was recorded),
        purchase_event_id (reference number of the new deposit entry), payment_reference (the Calloway
        receipt number printed for the wire, RCPT-HP- followed by five digits), purchase_id,
        deposit_component, source_payment_ref, amount (USD, 2 decimal places) and earnest_money_held (USD,
        2 decimal places: the deposits Calloway now holds on the agreement).
    """
    rows = ctx.find("purchase_agreements", purchase_id=purchase_id)
    if not rows:
        return f"Error: no Home Purchase Agreement {purchase_id}."
    agreement = rows[0]
    rid = ctx.make_id("pev_", purchase_id, "replacement_wire", source_payment_ref, deposit_component, amount)
    payment_reference = f"RCPT-HP-2{int(rid[-8:], 16) % 10000:04d}"
    posted = round(float(amount), 2)
    ctx.create("purchase_events", rid, purchase_event_id=rid, purchase_id=purchase_id,
               customer_id=agreement.get("customer_id"), event_type="purchase_deposit_posted",
               amount=posted, deposit_component=deposit_component, payment_method="wire",
               payment_reference=payment_reference, source_payment_ref=source_payment_ref,
               event_date=ctx.now()[:10])
    held = round(float(agreement.get("earnest_money_held") or 0) + posted, 2)
    ctx.update("purchase_agreements", purchase_id, earnest_money_held=held)
    return str({"status": "posted", "purchase_event_id": rid, "payment_reference": payment_reference,
                "purchase_id": purchase_id, "deposit_component": deposit_component,
                "source_payment_ref": source_payment_ref, "amount": posted, "earnest_money_held": held})

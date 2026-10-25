"""Hidden task tools for the bed-hold and leave reservations difficulty (Keystone Ridge Health & Rehabilitation).

Each tool posts one bed-hold charge on a reservation's ledger and is reached through the unlock/call meta-tools; the
figures they land are worked out by the caller from the published charter.
"""

from decimal import Decimal, ROUND_HALF_UP

from erlbench import ToolContext, tool


class _BedholdFormat:
    """Format helpers shared by the bed-hold tools (pure Python, no tool of their own)."""

    @staticmethod
    def half_up_cents(value):
        try:
            number = Decimal(str(value))
        except Exception:
            return 0.0
        if not number.is_finite():
            return 0.0
        return float(number.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP))

    @staticmethod
    def whole_days(value):
        try:
            number = float(value)
        except (TypeError, ValueError):
            return -1
        if number != number or number in (float("inf"), float("-inf")):
            return -1
        return int(number) if number == int(number) else -1


@tool(owner="agent", rw="write")
def post_therapeutic_opening_charge_78fe9a0a(ctx: ToolContext, bedhold_reservation_id: str, days_entry_id: str, day_count: int, amount: float) -> str:
    """The business office posts the private bed-hold charge for the opening month of a private-pay resident's bed hold on a therapeutic (home or community) leave, pricing that month's booked resident-private held-days entry. The charge is recorded on the reservation's ledger, dated today, naming the held-days entry it prices and the number of held days it bills, and the reservation's bed-hold balance rises by the amount. The posted charge and its reference number show on the receipt.

    Args:
        bedhold_reservation_id: Id class — the reference number of the bed-hold reservation the charge belongs to, as shown on the reservation record returned by the reservation lookup.
        days_entry_id: Id class — the reference number of the booked resident-private held-days entry being charged, as shown on the reservation's ledger returned by the ledger lookup.
        day_count: Fixed-format class — the number of held days the charge bills, in integer days (a whole number of at least 1); it is recorded as the charge's day count, and a value that is not a whole number of at least 1 is refused with an error and nothing is posted.
        amount: Fixed-format class — the bed-hold charge, in US dollars, a positive number with 2 decimal places (cents); it is stored rounded half up to the cent, and a value that is not greater than zero is refused with an error and nothing is posted.

    Returns:
        A one-line text receipt of the form "Posted therapeutic opening charge <charge_ref> on reservation <reservation_ref> for held-days entry <days_entry_ref>: <day_count> days, <amount> USD posted <posting_date>; bed-hold balance now <balance> USD." where charge_ref is the posted charge's reference number (text), reservation_ref and days_entry_ref echo the references given, day_count is the number of held days billed (integer), amount is the charge in USD with two decimals, posting_date is YYYY-MM-DD, and balance is the reservation's bed-hold balance including the charge in USD with two decimals. A receipt in this form means the charge is posted.
    """
    days = _BedholdFormat.whole_days(day_count)
    if days < 1:
        return "Error: day_count must be a whole number of at least 1, in integer days; nothing was posted."
    amt = _BedholdFormat.half_up_cents(amount)
    if amt <= 0:
        return "Error: amount must be greater than zero, in USD with 2 decimal places; nothing was posted."
    rid = ctx.make_id("bto_", bedhold_reservation_id, days_entry_id, days, amount)
    rows = ctx.find("bedhold_reservations", bedhold_reservation_id=bedhold_reservation_id)
    res = rows[0] if rows else {}
    ent = ctx.find("bedhold_ledger", bedhold_entry_id=days_entry_id)
    e = ent[0] if ent else {}
    posted = ctx.now()[:10]
    ctx.create("bedhold_ledger", rid, bedhold_entry_id=rid, bedhold_reservation_id=bedhold_reservation_id,
               customer_id=res.get("customer_id", ""), event_type="bedhold_charge", entry_date=posted,
               days_entry_id=days_entry_id, service_month=e.get("service_month", ""), from_date=e.get("from_date", ""),
               day_count=days, amount=amt)
    bal = _BedholdFormat.half_up_cents(float(res.get("charge_balance") or 0) + amt)
    ctx.update("bedhold_reservations", bedhold_reservation_id, charge_balance=bal)
    return (f"Posted therapeutic opening charge {rid} on reservation {bedhold_reservation_id} for held-days entry "
            f"{days_entry_id}: {days} days, {amt:.2f} USD posted {posted}; bed-hold balance now {bal:.2f} USD.")


@tool(owner="user", rw="write")
def sign_hospital_stay_charge_56dfc7d9(ctx: ToolContext, bedhold_reservation_id: str, days_entry_id: str, day_count: int, amount: float) -> str:
    """The resident or the representative signs the private bed-hold charge agreement for the held days of a private-pay resident's hospital leave whose bed hold carried a single month of held days, accepting the charge for that leave's booked resident-private held-days entry. Signing posts the bed-hold charge on the reservation's ledger, dated today, naming the held-days entry it prices and the number of held days it bills, and the reservation's bed-hold balance rises by the amount signed. The signer sees the posted charge and its reference number on the receipt.

    Args:
        bedhold_reservation_id: Id class — the reference number of the bed-hold reservation the charge belongs to, as given by the business office from the reservation record.
        days_entry_id: Id class — the reference number of the booked resident-private held-days entry being charged, as given by the business office from the reservation's ledger.
        day_count: Fixed-format class — the number of held days the charge bills, in integer days (a whole number of at least 1), the figure stated by the business office; it is recorded as the charge's day count, and a value that is not a whole number of at least 1 is refused with an error and nothing is posted.
        amount: Fixed-format class — the bed-hold charge, in US dollars, a positive number with 2 decimal places (cents), the figure stated by the business office; it is stored rounded half up to the cent, and a value that is not greater than zero is refused with an error and nothing is posted.

    Returns:
        A one-line text receipt of the form "Signed hospital stay charge <charge_ref> on reservation <reservation_ref> for held-days entry <days_entry_ref>: <day_count> days, <amount> USD posted <posting_date>; bed-hold balance now <balance> USD." where charge_ref is the posted charge's reference number (text), reservation_ref and days_entry_ref echo the references given, day_count is the number of held days billed (integer), amount is the charge in USD with two decimals, posting_date is YYYY-MM-DD, and balance is the reservation's bed-hold balance including the charge in USD with two decimals. A receipt in this form means the charge is posted.
    """
    days = _BedholdFormat.whole_days(day_count)
    if days < 1:
        return "Error: day_count must be a whole number of at least 1, in integer days; nothing was posted."
    amt = _BedholdFormat.half_up_cents(amount)
    if amt <= 0:
        return "Error: amount must be greater than zero, in USD with 2 decimal places; nothing was posted."
    rid = ctx.make_id("bhs_", bedhold_reservation_id, days_entry_id, days, amount)
    rows = ctx.find("bedhold_reservations", bedhold_reservation_id=bedhold_reservation_id)
    res = rows[0] if rows else {}
    ent = ctx.find("bedhold_ledger", bedhold_entry_id=days_entry_id)
    e = ent[0] if ent else {}
    posted = ctx.now()[:10]
    ctx.create("bedhold_ledger", rid, bedhold_entry_id=rid, bedhold_reservation_id=bedhold_reservation_id,
               customer_id=res.get("customer_id", ""), event_type="bedhold_charge", entry_date=posted,
               days_entry_id=days_entry_id, service_month=e.get("service_month", ""), from_date=e.get("from_date", ""),
               day_count=days, amount=amt)
    bal = _BedholdFormat.half_up_cents(float(res.get("charge_balance") or 0) + amt)
    ctx.update("bedhold_reservations", bedhold_reservation_id, charge_balance=bal)
    return (f"Signed hospital stay charge {rid} on reservation {bedhold_reservation_id} for held-days entry "
            f"{days_entry_id}: {days} days, {amt:.2f} USD posted {posted}; bed-hold balance now {bal:.2f} USD.")


@tool(owner="user", rw="write")
def sign_therapeutic_closing_charge_194aeb06(ctx: ToolContext, bedhold_reservation_id: str, days_entry_id: str, day_count: int, amount: float) -> str:
    """The resident or the representative signs the private bed-hold charge agreement for the closing month of a private-pay resident's released bed hold on a therapeutic (home or community) leave, accepting the charge for that month's booked resident-private held-days entry. Signing posts the bed-hold charge on the reservation's ledger, dated today, naming the held-days entry it prices and the number of held days it bills, and the reservation's bed-hold balance rises by the amount signed. The signer sees the posted charge and its reference number on the receipt.

    Args:
        bedhold_reservation_id: Id class — the reference number of the bed-hold reservation the charge belongs to, as given by the business office from the reservation record.
        days_entry_id: Id class — the reference number of the booked resident-private held-days entry being charged, as given by the business office from the reservation's ledger.
        day_count: Fixed-format class — the number of held days the charge bills, in integer days (a whole number of at least 1), the figure stated by the business office; it is recorded as the charge's day count, and a value that is not a whole number of at least 1 is refused with an error and nothing is posted.
        amount: Fixed-format class — the bed-hold charge, in US dollars, a positive number with 2 decimal places (cents), the figure stated by the business office; it is stored rounded half up to the cent, and a value that is not greater than zero is refused with an error and nothing is posted.

    Returns:
        A one-line text receipt of the form "Signed therapeutic closing charge <charge_ref> on reservation <reservation_ref> for held-days entry <days_entry_ref>: <day_count> days, <amount> USD posted <posting_date>; bed-hold balance now <balance> USD." where charge_ref is the posted charge's reference number (text), reservation_ref and days_entry_ref echo the references given, day_count is the number of held days billed (integer), amount is the charge in USD with two decimals, posting_date is YYYY-MM-DD, and balance is the reservation's bed-hold balance including the charge in USD with two decimals. A receipt in this form means the charge is posted.
    """
    days = _BedholdFormat.whole_days(day_count)
    if days < 1:
        return "Error: day_count must be a whole number of at least 1, in integer days; nothing was posted."
    amt = _BedholdFormat.half_up_cents(amount)
    if amt <= 0:
        return "Error: amount must be greater than zero, in USD with 2 decimal places; nothing was posted."
    rid = ctx.make_id("btc_", bedhold_reservation_id, days_entry_id, days, amount)
    rows = ctx.find("bedhold_reservations", bedhold_reservation_id=bedhold_reservation_id)
    res = rows[0] if rows else {}
    ent = ctx.find("bedhold_ledger", bedhold_entry_id=days_entry_id)
    e = ent[0] if ent else {}
    posted = ctx.now()[:10]
    ctx.create("bedhold_ledger", rid, bedhold_entry_id=rid, bedhold_reservation_id=bedhold_reservation_id,
               customer_id=res.get("customer_id", ""), event_type="bedhold_charge", entry_date=posted,
               days_entry_id=days_entry_id, service_month=e.get("service_month", ""), from_date=e.get("from_date", ""),
               day_count=days, amount=amt)
    bal = _BedholdFormat.half_up_cents(float(res.get("charge_balance") or 0) + amt)
    ctx.update("bedhold_reservations", bedhold_reservation_id, charge_balance=bal)
    return (f"Signed therapeutic closing charge {rid} on reservation {bedhold_reservation_id} for held-days entry "
            f"{days_entry_id}: {days} days, {amt:.2f} USD posted {posted}; bed-hold balance now {bal:.2f} USD.")


@tool(owner="agent", rw="write")
def post_hospital_opening_charge_991dca72(ctx: ToolContext, bedhold_reservation_id: str, days_entry_id: str, day_count: int, amount: float) -> str:
    """The business office posts the private bed-hold charge for the opening month of a Medical Assistance resident's private bed-hold extension on a hospital leave, pricing that month's booked resident-private held-days entry. The charge is recorded on the reservation's ledger, dated today, naming the held-days entry it prices and the number of held days it bills, and the reservation's bed-hold balance rises by the amount. The posted charge and its reference number show on the receipt.

    Args:
        bedhold_reservation_id: Id class — the reference number of the bed-hold reservation the charge belongs to, as shown on the reservation record returned by the reservation lookup.
        days_entry_id: Id class — the reference number of the booked resident-private held-days entry being charged, as shown on the reservation's ledger returned by the ledger lookup.
        day_count: Fixed-format class — the number of held days the charge bills, in integer days (a whole number of at least 1); it is recorded as the charge's day count, and a value that is not a whole number of at least 1 is refused with an error and nothing is posted.
        amount: Fixed-format class — the bed-hold charge, in US dollars, a positive number with 2 decimal places (cents); it is stored rounded half up to the cent, and a value that is not greater than zero is refused with an error and nothing is posted.

    Returns:
        A one-line text receipt of the form "Posted hospital opening charge <charge_ref> on reservation <reservation_ref> for held-days entry <days_entry_ref>: <day_count> days, <amount> USD posted <posting_date>; bed-hold balance now <balance> USD." where charge_ref is the posted charge's reference number (text), reservation_ref and days_entry_ref echo the references given, day_count is the number of held days billed (integer), amount is the charge in USD with two decimals, posting_date is YYYY-MM-DD, and balance is the reservation's bed-hold balance including the charge in USD with two decimals. A receipt in this form means the charge is posted.
    """
    days = _BedholdFormat.whole_days(day_count)
    if days < 1:
        return "Error: day_count must be a whole number of at least 1, in integer days; nothing was posted."
    amt = _BedholdFormat.half_up_cents(amount)
    if amt <= 0:
        return "Error: amount must be greater than zero, in USD with 2 decimal places; nothing was posted."
    rid = ctx.make_id("bho_", bedhold_reservation_id, days_entry_id, days, amount)
    rows = ctx.find("bedhold_reservations", bedhold_reservation_id=bedhold_reservation_id)
    res = rows[0] if rows else {}
    ent = ctx.find("bedhold_ledger", bedhold_entry_id=days_entry_id)
    e = ent[0] if ent else {}
    posted = ctx.now()[:10]
    ctx.create("bedhold_ledger", rid, bedhold_entry_id=rid, bedhold_reservation_id=bedhold_reservation_id,
               customer_id=res.get("customer_id", ""), event_type="bedhold_charge", entry_date=posted,
               days_entry_id=days_entry_id, service_month=e.get("service_month", ""), from_date=e.get("from_date", ""),
               day_count=days, amount=amt)
    bal = _BedholdFormat.half_up_cents(float(res.get("charge_balance") or 0) + amt)
    ctx.update("bedhold_reservations", bedhold_reservation_id, charge_balance=bal)
    return (f"Posted hospital opening charge {rid} on reservation {bedhold_reservation_id} for held-days entry "
            f"{days_entry_id}: {days} days, {amt:.2f} USD posted {posted}; bed-hold balance now {bal:.2f} USD.")


@tool(owner="user", rw="write")
def sign_hospital_closing_charge_702d4c7f(ctx: ToolContext, bedhold_reservation_id: str, days_entry_id: str, day_count: int, amount: float) -> str:
    """The resident or the representative signs the private bed-hold charge agreement for the closing month of a Medical Assistance resident's private bed-hold extension on a hospital leave that has ended, accepting the charge for that month's booked resident-private held-days entry. Signing posts the bed-hold charge on the reservation's ledger, dated today, naming the held-days entry it prices and the number of held days it bills, and the reservation's bed-hold balance rises by the amount signed. The signer sees the posted charge and its reference number on the receipt.

    Args:
        bedhold_reservation_id: Id class — the reference number of the bed-hold reservation the charge belongs to, as given by the business office from the reservation record.
        days_entry_id: Id class — the reference number of the booked resident-private held-days entry being charged, as given by the business office from the reservation's ledger.
        day_count: Fixed-format class — the number of held days the charge bills, in integer days (a whole number of at least 1), the figure stated by the business office; it is recorded as the charge's day count, and a value that is not a whole number of at least 1 is refused with an error and nothing is posted.
        amount: Fixed-format class — the bed-hold charge, in US dollars, a positive number with 2 decimal places (cents), the figure stated by the business office; it is stored rounded half up to the cent, and a value that is not greater than zero is refused with an error and nothing is posted.

    Returns:
        A one-line text receipt of the form "Signed hospital closing charge <charge_ref> on reservation <reservation_ref> for held-days entry <days_entry_ref>: <day_count> days, <amount> USD posted <posting_date>; bed-hold balance now <balance> USD." where charge_ref is the posted charge's reference number (text), reservation_ref and days_entry_ref echo the references given, day_count is the number of held days billed (integer), amount is the charge in USD with two decimals, posting_date is YYYY-MM-DD, and balance is the reservation's bed-hold balance including the charge in USD with two decimals. A receipt in this form means the charge is posted.
    """
    days = _BedholdFormat.whole_days(day_count)
    if days < 1:
        return "Error: day_count must be a whole number of at least 1, in integer days; nothing was posted."
    amt = _BedholdFormat.half_up_cents(amount)
    if amt <= 0:
        return "Error: amount must be greater than zero, in USD with 2 decimal places; nothing was posted."
    rid = ctx.make_id("bhc_", bedhold_reservation_id, days_entry_id, days, amount)
    rows = ctx.find("bedhold_reservations", bedhold_reservation_id=bedhold_reservation_id)
    res = rows[0] if rows else {}
    ent = ctx.find("bedhold_ledger", bedhold_entry_id=days_entry_id)
    e = ent[0] if ent else {}
    posted = ctx.now()[:10]
    ctx.create("bedhold_ledger", rid, bedhold_entry_id=rid, bedhold_reservation_id=bedhold_reservation_id,
               customer_id=res.get("customer_id", ""), event_type="bedhold_charge", entry_date=posted,
               days_entry_id=days_entry_id, service_month=e.get("service_month", ""), from_date=e.get("from_date", ""),
               day_count=days, amount=amt)
    bal = _BedholdFormat.half_up_cents(float(res.get("charge_balance") or 0) + amt)
    ctx.update("bedhold_reservations", bedhold_reservation_id, charge_balance=bal)
    return (f"Signed hospital closing charge {rid} on reservation {bedhold_reservation_id} for held-days entry "
            f"{days_entry_id}: {days} days, {amt:.2f} USD posted {posted}; bed-hold balance now {bal:.2f} USD.")

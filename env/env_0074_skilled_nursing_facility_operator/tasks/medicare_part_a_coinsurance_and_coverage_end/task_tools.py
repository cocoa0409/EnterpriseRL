"""Hidden task tools for the medicare_part_a_coinsurance_and_coverage_end difficulty (env_0074).

Each tool performs one atomic posting on a Medicare Part A coverage episode and its ledger. Tools take
values the agent has already worked out from the published policy and write them as given; they judge no
eligibility, order or amount.
"""

from decimal import ROUND_HALF_UP, Decimal

from erlbench import ToolContext, tool


class _Fmt:
    """Format helpers shared by the tool bodies (not tools themselves)."""

    @staticmethod
    def cents(value):
        """Half-up rounding to the cent, as every amount docstring promises."""
        return float(Decimal(str(value)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP))

    @staticmethod
    def month_ok(value):
        text = str(value)
        return len(text) == 7 and text[4] == "-" and text[:4].isdigit() and text[5:].isdigit() and 1 <= int(text[5:]) <= 12


@tool(owner="agent", rw="write")
def post_coinsurance_charge_97c12690(ctx: ToolContext, medicare_coverage_id: str, days_entry_id: str, liable_party: str,
                                     service_month: str, day_count: int, daily_coinsurance_rate: float,
                                     amount: float) -> str:
    """Post one liable party's original coinsurance charge for one booked block of Part A coinsurance days on a coverage episode. The business office uses this to bill a share of the block to the resident (or the representative who pays for the resident), to the Medigap carrier, or to the state Medicaid crossover. One call adds one charge entry to the episode's Medicare billing history, dated today, naming the booked-days entry it prices and the party billed, and raises the episode's open coinsurance balance by the amount. The billed party's share shows on the account, and the receipt carries the reference number of the charge entry, which a payment or an adjustment names. It never records a rebill of a denied share.

    Args:
        medicare_coverage_id: Id class — the reference number of the Medicare Part A coverage episode being billed, as shown by the coverage episode lookup for the resident.
        days_entry_id: Id class — the reference number of the booked-days entry (the block of coinsurance days) this charge prices, as shown in the episode's Medicare billing history.
        liable_party: Enum class — the party this share is billed to: resident = the resident's own share, billed to the resident or the representative who pays for the resident; medigap_carrier = the share billed to the resident's Medigap insurance company named on the coverage; medicaid_crossover = the share billed to the state Medicaid program for a resident with verified QMB status.
        service_month: Fixed-format class — the calendar month in which the priced days were furnished, written YYYY-MM exactly as on the booked-days entry; no empty value.
        day_count: Fixed-format class — the number of coinsurance days the charge prices, an integer count of days (positive).
        daily_coinsurance_rate: Fixed-format class — the daily coinsurance rate applied to the priced days, in USD per day, 2 decimal places; pass it already rounded to the cent; it is stored at 2 decimal places.
        amount: Fixed-format class — the share being billed, in USD, 2 decimal places, positive; pass it already rounded to the cent; it is stored at 2 decimal places.

    Returns:
        A dictionary rendered as text with: status ("posted", meaning the charge entry now exists); charge_entry_id (string, the reference number of the new charge entry); days_entry_id (string, the booked-days entry it prices); liable_party (string, the party billed, one of the three values above); amount (number, USD with 2 decimal places, the amount billed); entry_date (string, YYYY-MM-DD, today's posting date); coinsurance_balance (number, USD with 2 decimal places, the episode's open coinsurance balance across every liable party including this charge).
    """
    amt = _Fmt.cents(amount)
    rate = _Fmt.cents(daily_coinsurance_rate)
    days = int(day_count)
    if amt <= 0 or rate <= 0 or days <= 0:
        return "Error: amount, daily_coinsurance_rate and day_count must be positive"
    if not _Fmt.month_ok(service_month):
        return "Error: service_month must be written YYYY-MM"
    today = ctx.now()[:10]
    rid = ctx.make_id("mlc_", medicare_coverage_id, days_entry_id, liable_party, service_month, days, rate, amt)
    cov = ctx.find("medicare_coverages", medicare_coverage_id=medicare_coverage_id)
    cust = cov[0].get("customer_id") if cov else ""
    ctx.create("medicare_ledger", rid, medicare_entry_id=rid, medicare_coverage_id=medicare_coverage_id,
               customer_id=cust, event_type="medicare_coinsurance_charge", entry_date=today,
               service_month=service_month, day_count=days, daily_coinsurance_rate=rate,
               liable_party=liable_party, amount=amt, days_entry_id=days_entry_id, charge_entry_id="")
    balance = _Fmt.cents(float((cov[0].get("coinsurance_balance") if cov else 0) or 0) + amt)
    ctx.update("medicare_coverages", medicare_coverage_id, coinsurance_balance=balance)
    return str({"status": "posted", "charge_entry_id": rid, "days_entry_id": days_entry_id, "liable_party": liable_party,
                "amount": amt, "entry_date": today, "coinsurance_balance": balance})


@tool(owner="user", rw="write")
def pay_coinsurance_by_card_ebeca5a6(ctx: ToolContext, medicare_coverage_id: str, charge_entry_id: str,
                                     amount: float) -> str:
    """The resident or the representative pays a resident coinsurance charge on a Medicare Part A coverage episode with their own credit or debit card during the call. One call records one card payment, dated today, applied to the one named charge, and lowers the episode's open coinsurance balance by the amount paid. The payer sees the payment on the resident's account immediately, and the receipt carries the reference number of the payment entry.

    Args:
        medicare_coverage_id: Id class — the reference number of the Medicare Part A coverage episode the charge belongs to, as the business office reads it from the resident's coverage episode.
        charge_entry_id: Id class — the reference number of the resident coinsurance charge entry being paid, as the business office reads it from the episode's Medicare billing history and gives it to the payer.
        amount: Fixed-format class — the amount paid by card, in USD, 2 decimal places, positive; pass it already rounded to the cent; it is stored at 2 decimal places.

    Returns:
        A dictionary rendered as text with: status ("paid", meaning the card payment now stands on the account); payment_entry_id (string, the reference number of the new payment entry); charge_entry_id (string, the charge the payment is applied to); payment_method (string, always "card"); amount (number, USD with 2 decimal places, the amount paid); entry_date (string, YYYY-MM-DD, today's date); coinsurance_balance (number, USD with 2 decimal places, the episode's open coinsurance balance across every liable party including this payment).
    """
    amt = _Fmt.cents(amount)
    if amt <= 0:
        return "Error: amount must be positive"
    today = ctx.now()[:10]
    rid = ctx.make_id("mlp_", medicare_coverage_id, charge_entry_id, amt, today)
    cov = ctx.find("medicare_coverages", medicare_coverage_id=medicare_coverage_id)
    cust = cov[0].get("customer_id") if cov else ""
    ctx.create("medicare_ledger", rid, medicare_entry_id=rid, medicare_coverage_id=medicare_coverage_id,
               customer_id=cust, event_type="medicare_coinsurance_payment", entry_date=today,
               charge_entry_id=charge_entry_id, liable_party="resident", payment_method="card", amount=amt)
    balance = _Fmt.cents(float((cov[0].get("coinsurance_balance") if cov else 0) or 0) - amt)
    ctx.update("medicare_coverages", medicare_coverage_id, coinsurance_balance=balance)
    return str({"status": "paid", "payment_entry_id": rid, "charge_entry_id": charge_entry_id, "payment_method": "card",
                "amount": amt, "entry_date": today, "coinsurance_balance": balance})


@tool(owner="agent", rw="write")
def correct_coinsurance_rate_feac0074(ctx: ToolContext, medicare_coverage_id: str, charge_entry_id: str, days_entry_id: str,
                                      service_month: str, amount: float) -> str:
    """Post a rate-year correction that reduces one coinsurance charge on a Medicare Part A coverage episode when the charge was billed at a daily coinsurance rate other than the rate of the year in which its days of service were furnished. One call adds one adjustment entry to the episode's Medicare billing history, dated today, with the reason rate_year_correction, naming the charge it reduces and the booked-days entry behind that charge, and lowers the episode's open coinsurance balance by the amount. The billed party's account shows the charge reduced by the correction, and the receipt carries the reference number of the adjustment entry.

    Args:
        medicare_coverage_id: Id class — the reference number of the Medicare Part A coverage episode the charge belongs to, as shown by the coverage episode lookup for the resident.
        charge_entry_id: Id class — the reference number of the coinsurance charge entry being corrected, as shown in the episode's Medicare billing history.
        days_entry_id: Id class — the reference number of the booked-days entry (the block of coinsurance days) the corrected charge prices, as shown on that charge in the episode's Medicare billing history.
        service_month: Fixed-format class — the calendar month in which the corrected charge's days were furnished, written YYYY-MM exactly as on the corrected charge; no empty value.
        amount: Fixed-format class — the reduction, in USD, 2 decimal places, positive; pass it already rounded to the cent; it is stored at 2 decimal places.

    Returns:
        A dictionary rendered as text with: status ("adjusted", meaning the correction entry now stands on the account); adjustment_entry_id (string, the reference number of the new adjustment entry); charge_entry_id (string, the charge reduced); adjustment_reason (string, always "rate_year_correction"); amount (number, USD with 2 decimal places, the reduction posted); entry_date (string, YYYY-MM-DD, today's posting date); coinsurance_balance (number, USD with 2 decimal places, the episode's open coinsurance balance across every liable party including this reduction).
    """
    amt = _Fmt.cents(amount)
    if amt <= 0:
        return "Error: amount must be positive"
    if not _Fmt.month_ok(service_month):
        return "Error: service_month must be written YYYY-MM"
    today = ctx.now()[:10]
    rid = ctx.make_id("mla_", medicare_coverage_id, charge_entry_id, days_entry_id, service_month, "rate_year_correction", amt)
    cov = ctx.find("medicare_coverages", medicare_coverage_id=medicare_coverage_id)
    cust = cov[0].get("customer_id") if cov else ""
    ctx.create("medicare_ledger", rid, medicare_entry_id=rid, medicare_coverage_id=medicare_coverage_id,
               customer_id=cust, event_type="medicare_coinsurance_adjustment", entry_date=today,
               charge_entry_id=charge_entry_id, days_entry_id=days_entry_id, service_month=service_month,
               adjustment_reason="rate_year_correction", amount=amt)
    balance = _Fmt.cents(float((cov[0].get("coinsurance_balance") if cov else 0) or 0) - amt)
    ctx.update("medicare_coverages", medicare_coverage_id, coinsurance_balance=balance)
    return str({"status": "adjusted", "adjustment_entry_id": rid, "charge_entry_id": charge_entry_id,
                "adjustment_reason": "rate_year_correction", "amount": amt, "entry_date": today, "coinsurance_balance": balance})


@tool(owner="agent", rw="write")
def reduce_coinsurance_for_reversed_days_0894f336(ctx: ToolContext, medicare_coverage_id: str, charge_entry_id: str,
                                                  reversal_entry_id: str, amount: float) -> str:
    """Post the reduction of one coinsurance charge on a Medicare Part A coverage episode for booked covered days that one day reversal took back. One call adds one adjustment entry to the episode's Medicare billing history, dated today, naming the charge it reduces, carrying over from the named day reversal its booked-days entry, its service month and its own reason, and lowers the episode's open coinsurance balance by the amount. The billed party's account shows the charge reduced for the reversed days, and the receipt carries the reference number of the adjustment entry and the reason recorded.

    Args:
        medicare_coverage_id: Id class — the reference number of the Medicare Part A coverage episode the charge belongs to, as shown by the coverage episode lookup for the resident.
        charge_entry_id: Id class — the reference number of the coinsurance charge entry being reduced, as shown in the episode's Medicare billing history.
        reversal_entry_id: Id class — the reference number of the day reversal entry whose reversed days the reduction is for, as shown in the episode's Medicare billing history.
        amount: Fixed-format class — the reduction, in USD, 2 decimal places, positive; pass it already rounded to the cent; it is stored at 2 decimal places.

    Returns:
        A dictionary rendered as text with: status ("adjusted", meaning the reduction entry now stands on the account); adjustment_entry_id (string, the reference number of the new adjustment entry); charge_entry_id (string, the charge reduced); adjustment_reason (string, the reason carried over from the day reversal); amount (number, USD with 2 decimal places, the reduction posted); entry_date (string, YYYY-MM-DD, today's posting date); coinsurance_balance (number, USD with 2 decimal places, the episode's open coinsurance balance across every liable party including this reduction).
    """
    amt = _Fmt.cents(amount)
    if amt <= 0:
        return "Error: amount must be positive"
    today = ctx.now()[:10]
    rid = ctx.make_id("mla_", medicare_coverage_id, charge_entry_id, reversal_entry_id, amt)
    rev = ctx.find("medicare_ledger", medicare_entry_id=reversal_entry_id)
    src = rev[0] if rev else {}
    reason = src.get("adjustment_reason") or ""
    cov = ctx.find("medicare_coverages", medicare_coverage_id=medicare_coverage_id)
    cust = cov[0].get("customer_id") if cov else ""
    ctx.create("medicare_ledger", rid, medicare_entry_id=rid, medicare_coverage_id=medicare_coverage_id,
               customer_id=cust, event_type="medicare_coinsurance_adjustment", entry_date=today,
               charge_entry_id=charge_entry_id, days_entry_id=src.get("days_entry_id") or "",
               service_month=src.get("service_month") or "", adjustment_reason=reason, amount=amt)
    balance = _Fmt.cents(float((cov[0].get("coinsurance_balance") if cov else 0) or 0) - amt)
    ctx.update("medicare_coverages", medicare_coverage_id, coinsurance_balance=balance)
    return str({"status": "adjusted", "adjustment_entry_id": rid, "charge_entry_id": charge_entry_id,
                "adjustment_reason": reason, "amount": amt, "entry_date": today, "coinsurance_balance": balance})


@tool(owner="user", rw="write")
def pay_coinsurance_by_bank_draft_32bb229d(ctx: ToolContext, medicare_coverage_id: str, charge_entry_id: str,
                                           amount: float) -> str:
    """The resident or the representative pays a resident coinsurance charge on a Medicare Part A coverage episode by authorizing a bank draft (an electronic debit, ACH) from their own checking or savings account during the call. One call records one bank-draft payment, dated today, applied to the one named charge, and lowers the episode's open coinsurance balance by the amount paid. The payer sees the payment on the resident's account immediately, and the receipt carries the reference number of the payment entry.

    Args:
        medicare_coverage_id: Id class — the reference number of the Medicare Part A coverage episode the charge belongs to, as the business office reads it from the resident's coverage episode.
        charge_entry_id: Id class — the reference number of the resident coinsurance charge entry being paid, as the business office reads it from the episode's Medicare billing history and gives it to the payer.
        amount: Fixed-format class — the amount drafted from the payer's account, in USD, 2 decimal places, positive; pass it already rounded to the cent; it is stored at 2 decimal places.

    Returns:
        A dictionary rendered as text with: status ("paid", meaning the bank-draft payment now stands on the account); payment_entry_id (string, the reference number of the new payment entry); charge_entry_id (string, the charge the payment is applied to); payment_method (string, always "ach"); amount (number, USD with 2 decimal places, the amount paid); entry_date (string, YYYY-MM-DD, today's date); coinsurance_balance (number, USD with 2 decimal places, the episode's open coinsurance balance across every liable party including this payment).
    """
    amt = _Fmt.cents(amount)
    if amt <= 0:
        return "Error: amount must be positive"
    today = ctx.now()[:10]
    rid = ctx.make_id("mlp_", medicare_coverage_id, charge_entry_id, "ach", amt, today)
    cov = ctx.find("medicare_coverages", medicare_coverage_id=medicare_coverage_id)
    cust = cov[0].get("customer_id") if cov else ""
    ctx.create("medicare_ledger", rid, medicare_entry_id=rid, medicare_coverage_id=medicare_coverage_id,
               customer_id=cust, event_type="medicare_coinsurance_payment", entry_date=today,
               charge_entry_id=charge_entry_id, liable_party="resident", payment_method="ach", amount=amt)
    balance = _Fmt.cents(float((cov[0].get("coinsurance_balance") if cov else 0) or 0) - amt)
    ctx.update("medicare_coverages", medicare_coverage_id, coinsurance_balance=balance)
    return str({"status": "paid", "payment_entry_id": rid, "charge_entry_id": charge_entry_id, "payment_method": "ach",
                "amount": amt, "entry_date": today, "coinsurance_balance": balance})

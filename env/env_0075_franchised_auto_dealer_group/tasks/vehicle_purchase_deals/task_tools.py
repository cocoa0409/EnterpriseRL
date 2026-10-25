"""Hidden task tools of the vehicle_purchase_deals difficulty (purchase category).

Each tool performs one atomic write on one purchase deal with the value the agent (or the buyer)
has already worked out; no tool checks a policy precondition or computes a policy amount. Each
tool enforces only the argument formats its docstring publishes (cents rounded half up, amounts
greater than zero, month format, whole days, the charge a reversal points at).
"""

from decimal import Decimal, ROUND_HALF_UP

from erlbench import ToolContext, tool


class _Money:
    """Half-up cent rounding on decimal strings (no binary floating-point ties)."""

    @staticmethod
    def cents(x) -> float:
        return float(Decimal(str(x)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP))


class _DealCalendar:
    """Pure calendar arithmetic on 'YYYY-MM-DD' strings (proleptic Gregorian ordinal days)."""

    @staticmethod
    def to_ordinal(d: str) -> int:
        y, m, day = int(d[0:4]), int(d[5:7]), int(d[8:10])
        y2 = y - 1
        n = y2 * 365 + y2 // 4 - y2 // 100 + y2 // 400
        cum = [0, 31, 59, 90, 120, 151, 181, 212, 243, 273, 304, 334]
        leap = (y % 4 == 0 and y % 100 != 0) or (y % 400 == 0)
        return n + cum[m - 1] + (1 if (leap and m > 2) else 0) + day

    @staticmethod
    def from_ordinal(n: int) -> str:
        y = (n - 1) // 366 + 1
        while _DealCalendar.to_ordinal(f"{y + 1:04d}-01-01") <= n:
            y += 1
        m = 1
        while m < 12 and _DealCalendar.to_ordinal(f"{y:04d}-{m + 1:02d}-01") <= n:
            m += 1
        day = n - _DealCalendar.to_ordinal(f"{y:04d}-{m:02d}-01") + 1
        return f"{y:04d}-{m:02d}-{day:02d}"

    @staticmethod
    def add_days(d: str, days: int) -> str:
        return _DealCalendar.from_ordinal(_DealCalendar.to_ordinal(d) + int(days))

    @staticmethod
    def is_month(s: str) -> bool:
        s = str(s)
        return len(s) == 7 and s[4] == "-" and s[:4].isdigit() and s[5:].isdigit() and 1 <= int(s[5:]) <= 12


@tool(owner="agent", rw="write")
def credit_fleet_incentive_b735a70c(ctx: ToolContext, customer_id: str, purchase_deal_id: str,
                                    incentive_amount: float) -> str:
    """Credit the manufacturer fleet incentive to one fleet vehicle purchase deal. The store books one
    payment credit with payment method manufacturer_incentive on the deal, dated the handling date, and
    the deal's balance due drops by the credited amount. The buyer sees the incentive credit on the deal
    statement and a lower balance due. The call has completed when the receipt shows the new credit
    reference and the updated balance due.

    Args:
        customer_id: Id class — the customer identifier (customer reference number) of the fleet buyer, as
            returned by the customer profile lookup.
        purchase_deal_id: Id class — the purchase deal identifier (deal reference number) of the fleet deal
            receiving the credit, as returned by the purchase deal lookup for the verified customer.
        incentive_amount: Fixed-format class — the incentive credited, in US dollars as a decimal number
            greater than zero with 2 decimal places (cents); any further digits are rounded half up to the
            cent, and the rounded amount is what is booked.

    Returns:
        A confirmation string with: the credit reference (text identifier of the new deal credit), the
        deal reference (text), the amount credited (US dollars, 2 decimals), the payment method
        manufacturer_incentive (text), the credit date (YYYY-MM-DD, the handling date) and the deal's new
        balance due (US dollars, 2 decimals). A string that starts with "Incentive credited" means the
        credit was booked; a string that starts with "Error:" means the amount was not greater than zero
        and nothing was booked.
    """
    amount = _Money.cents(incentive_amount)
    if amount <= 0:
        return "Error: incentive_amount must be greater than zero; nothing was booked."
    deal = (ctx.find("purchase_deals", purchase_deal_id=purchase_deal_id) or [{}])[0]
    today = ctx.now()[:10]
    rid = ctx.make_id("ptx_", customer_id, purchase_deal_id, amount)
    ctx.create("purchase_transactions", rid, purchase_txn_id=rid, purchase_deal_id=purchase_deal_id,
               customer_id=customer_id, event_type="purchase_payment_posted", txn_date=today,
               amount=amount, charge_code="not_applicable", payment_method="manufacturer_incentive",
               source_txn_id=None, billing_month=None, odometer_miles=None)
    new_balance = _Money.cents(Decimal(str(deal.get("balance_due") or 0)) - Decimal(str(amount)))
    ctx.update("purchase_deals", purchase_deal_id, balance_due=new_balance)
    return (f"Incentive credited: credit {rid} on deal {purchase_deal_id}, amount {amount:.2f}, "
            f"payment method manufacturer_incentive, dated {today}; balance due now {new_balance:.2f}.")


@tool(owner="agent", rw="write")
def reverse_fleet_delivery_fee_7a0a59bd(ctx: ToolContext, purchase_deal_id: str, source_txn_id: str,
                                        reversal_amount: float) -> str:
    """Reverse part of a home delivery fee charged on one fleet vehicle purchase deal. The store books one
    charge reversal with charge code home_delivery_fee on the deal, dated the handling date and pointing at
    the home delivery fee charge it corrects, and the deal's balance due drops by the amount reversed; the
    original charge stays on the deal. The buyer sees the delivery-fee reversal on the deal statement and a
    lower balance due. The call has completed when the receipt shows the new reversal reference, the charge
    it points at and the updated balance due.

    Args:
        purchase_deal_id: Id class — the purchase deal identifier (deal reference number) of the delivered
            fleet deal, as returned by the purchase deal lookup for the verified customer.
        source_txn_id: Id class — the transaction identifier of the home delivery fee charge being
            corrected, as returned by the purchase transaction lookup; it must identify a home delivery fee
            charge of that same deal.
        reversal_amount: Fixed-format class — the part of the charge reversed, in US dollars as a decimal
            number greater than zero with 2 decimal places (cents); any further digits are rounded half up to
            the cent, and the rounded amount is what is booked.

    Returns:
        A confirmation string with: the reversal reference (text identifier of the new reversal), the deal
        reference (text), the corrected charge reference (text), the charge code home_delivery_fee (text),
        the amount reversed (US dollars, 2 decimals), the reversal date (YYYY-MM-DD, the handling date) and
        the deal's new balance due (US dollars, 2 decimals). A string that starts with "Delivery fee
        reversed" means the reversal was booked; a string that starts with "Error:" means the amount was not
        greater than zero or the charge reference does not identify a home delivery fee charge of that deal,
        and nothing was booked.
    """
    amount = _Money.cents(reversal_amount)
    if amount <= 0:
        return "Error: reversal_amount must be greater than zero; nothing was booked."
    src = (ctx.find("purchase_transactions", purchase_txn_id=source_txn_id) or [None])[0]
    if (not src or src.get("purchase_deal_id") != purchase_deal_id or src.get("event_type") != "purchase_charge_posted"
            or src.get("charge_code") != "home_delivery_fee"):
        return "Error: source_txn_id must identify a home delivery fee charge of this deal; nothing was booked."
    deal = (ctx.find("purchase_deals", purchase_deal_id=purchase_deal_id) or [{}])[0]
    today = ctx.now()[:10]
    rid = ctx.make_id("ptx_", purchase_deal_id, source_txn_id, amount)
    ctx.create("purchase_transactions", rid, purchase_txn_id=rid, purchase_deal_id=purchase_deal_id,
               customer_id=deal.get("customer_id"), event_type="purchase_charge_reversed", txn_date=today,
               amount=amount, charge_code="home_delivery_fee", payment_method="not_applicable",
               source_txn_id=source_txn_id, billing_month=None, odometer_miles=None)
    new_balance = _Money.cents(Decimal(str(deal.get("balance_due") or 0)) - Decimal(str(amount)))
    ctx.update("purchase_deals", purchase_deal_id, balance_due=new_balance)
    return (f"Delivery fee reversed: reversal {rid} on deal {purchase_deal_id} against charge {source_txn_id}, "
            f"charge code home_delivery_fee, amount {amount:.2f}, dated {today}; balance due now {new_balance:.2f}.")


@tool(owner="agent", rw="write")
def post_fleet_late_fee_7ed43dd7(ctx: ToolContext, purchase_deal_id: str, billing_month: str,
                                 fee_amount: float) -> str:
    """Assess the late balance fee for one billing month on one delivered fleet vehicle purchase deal.
    The store books one charge with charge code late_balance_fee on the deal, carrying the billing month
    assessed and dated the handling date, and the deal's balance due rises by the fee. The buyer sees the
    late balance fee for that month on the deal statement. The call has completed when the receipt shows
    the new charge reference, the billing month and the updated balance due.

    Args:
        purchase_deal_id: Id class — the purchase deal identifier (deal reference number) of the delivered
            fleet deal, as returned by the purchase deal lookup for the verified customer.
        billing_month: Fixed-format class — the calendar month the fee is assessed for, written as YYYY-MM
            (4-digit year, hyphen, 2-digit month from 01 to 12), with no day part and no time zone.
        fee_amount: Fixed-format class — the late balance fee, in US dollars as a decimal number greater
            than zero with 2 decimal places (cents); any further digits are rounded half up to the cent,
            and the rounded amount is what is posted.

    Returns:
        A confirmation string with: the charge reference (text identifier of the new deal charge), the
        deal reference (text), the charge code late_balance_fee (text), the billing month (YYYY-MM), the
        amount (US dollars, 2 decimals), the charge date (YYYY-MM-DD, the handling date) and the deal's
        new balance due (US dollars, 2 decimals). A string that starts with "Late balance fee posted"
        means the charge was booked; a string that starts with "Error:" means the month was not in
        YYYY-MM form or the amount was not greater than zero, and nothing was booked.
    """
    if not _DealCalendar.is_month(billing_month):
        return "Error: billing_month must be written YYYY-MM; nothing was booked."
    amount = _Money.cents(fee_amount)
    if amount <= 0:
        return "Error: fee_amount must be greater than zero; nothing was booked."
    deal = (ctx.find("purchase_deals", purchase_deal_id=purchase_deal_id) or [{}])[0]
    today = ctx.now()[:10]
    rid = ctx.make_id("ptx_", purchase_deal_id, billing_month, amount)
    ctx.create("purchase_transactions", rid, purchase_txn_id=rid, purchase_deal_id=purchase_deal_id,
               customer_id=deal.get("customer_id"), event_type="purchase_charge_posted", txn_date=today,
               amount=amount, charge_code="late_balance_fee", payment_method="not_applicable",
               source_txn_id=None, billing_month=str(billing_month), odometer_miles=None)
    new_balance = _Money.cents(Decimal(str(deal.get("balance_due") or 0)) + Decimal(str(amount)))
    ctx.update("purchase_deals", purchase_deal_id, balance_due=new_balance)
    return (f"Late balance fee posted: charge {rid} on deal {purchase_deal_id}, charge code late_balance_fee, "
            f"billing month {billing_month}, amount {amount:.2f}, dated {today}; balance due now {new_balance:.2f}.")


@tool(owner="user", rw="write")
def pay_fleet_order_deposit_c9caca35(ctx: ToolContext, purchase_deal_id: str, deposit_amount: float) -> str:
    """The fleet buyer pays an added order deposit on their own reserved fleet vehicle purchase deal by
    ACH transfer from the business bank account. One deposit with payment method ach, dated the handling
    date, is received and held against the deal, and the deposit held on the deal rises by that amount.
    The buyer sees the deposit receipt and the new deposit held. The call has completed when the receipt
    shows the new deposit reference and the updated deposit held.

    Args:
        purchase_deal_id: Id class — the purchase deal identifier (deal reference number) of the buyer's
            reserved fleet deal, as the desk reads it from the purchase deal lookup and gives it to the buyer.
        deposit_amount: Fixed-format class — the deposit paid, in US dollars as a decimal number greater
            than zero with 2 decimal places (cents); any further digits are rounded half up to the cent,
            and the rounded amount is what is received.

    Returns:
        A confirmation string with: the deposit reference (text identifier of the new deposit), the deal
        reference (text), the amount received (US dollars, 2 decimals), the payment method ach (text),
        the date received (YYYY-MM-DD, the handling date) and the deal's new deposit held (US dollars, 2
        decimals). A string that starts with "Deposit received" means the deposit was taken; a string that
        starts with "Error:" means the amount was not greater than zero and nothing was received.
    """
    amount = _Money.cents(deposit_amount)
    if amount <= 0:
        return "Error: deposit_amount must be greater than zero; nothing was received."
    deal = (ctx.find("purchase_deals", purchase_deal_id=purchase_deal_id) or [{}])[0]
    today = ctx.now()[:10]
    rid = ctx.make_id("ptx_", purchase_deal_id, amount)
    ctx.create("purchase_transactions", rid, purchase_txn_id=rid, purchase_deal_id=purchase_deal_id,
               customer_id=deal.get("customer_id"), event_type="purchase_deposit_received", txn_date=today,
               amount=amount, charge_code="not_applicable", payment_method="ach",
               source_txn_id=None, billing_month=None, odometer_miles=None)
    new_held = _Money.cents(Decimal(str(deal.get("deposit_held_balance") or 0)) + Decimal(str(amount)))
    ctx.update("purchase_deals", purchase_deal_id, deposit_held_balance=new_held)
    return (f"Deposit received: deposit {rid} on deal {purchase_deal_id}, amount {amount:.2f}, payment method ach, "
            f"dated {today}; deposit held now {new_held:.2f}.")


@tool(owner="user", rw="write")
def pay_extension_deposit_9124466d(ctx: ToolContext, purchase_deal_id: str, deposit_amount: float) -> str:
    """The buyer pays an added deposit by debit card on their own reserved retail vehicle purchase deal to
    support a longer hold. One deposit with payment method debit_card, dated the handling date, is
    received and held against the deal, and the deposit held on the deal rises by that amount. The buyer
    sees the deposit receipt and the new deposit held. The call has completed when the receipt shows the
    new deposit reference and the updated deposit held.

    Args:
        purchase_deal_id: Id class — the purchase deal identifier (deal reference number) of the buyer's
            reserved deal, as the desk reads it from the purchase deal lookup and gives it to the buyer.
        deposit_amount: Fixed-format class — the deposit paid, in US dollars as a decimal number greater
            than zero with 2 decimal places (cents); any further digits are rounded half up to the cent,
            and the rounded amount is what is received.

    Returns:
        A confirmation string with: the deposit reference (text identifier of the new deposit), the deal
        reference (text), the amount received (US dollars, 2 decimals), the payment method debit_card
        (text), the date received (YYYY-MM-DD, the handling date) and the deal's new deposit held (US
        dollars, 2 decimals). A string that starts with "Deposit received" means the deposit was taken; a
        string that starts with "Error:" means the amount was not greater than zero and nothing was
        received.
    """
    amount = _Money.cents(deposit_amount)
    if amount <= 0:
        return "Error: deposit_amount must be greater than zero; nothing was received."
    deal = (ctx.find("purchase_deals", purchase_deal_id=purchase_deal_id) or [{}])[0]
    today = ctx.now()[:10]
    rid = ctx.make_id("ptx_", purchase_deal_id, amount)
    ctx.create("purchase_transactions", rid, purchase_txn_id=rid, purchase_deal_id=purchase_deal_id,
               customer_id=deal.get("customer_id"), event_type="purchase_deposit_received", txn_date=today,
               amount=amount, charge_code="not_applicable", payment_method="debit_card",
               source_txn_id=None, billing_month=None, odometer_miles=None)
    new_held = _Money.cents(Decimal(str(deal.get("deposit_held_balance") or 0)) + Decimal(str(amount)))
    ctx.update("purchase_deals", purchase_deal_id, deposit_held_balance=new_held)
    return (f"Deposit received: deposit {rid} on deal {purchase_deal_id}, amount {amount:.2f}, payment method "
            f"debit_card, dated {today}; deposit held now {new_held:.2f}.")


@tool(owner="agent", rw="write")
def extend_vehicle_hold_21e7c68f(ctx: ToolContext, purchase_deal_id: str, extension_days: int) -> str:
    """Extend the hold on one reserved vehicle purchase deal once. The store moves the deal's hold expiry
    date forward by the number of calendar days passed, counted from the hold expiry date currently on the
    deal, and raises the deal's count of hold extensions by one. The buyer sees the new last day of the
    hold. The call has completed when the receipt shows the new hold expiry date and the new extension
    count.

    Args:
        purchase_deal_id: Id class — the purchase deal identifier (deal reference number) of the reserved
            deal, as returned by the purchase deal lookup for the verified customer.
        extension_days: Fixed-format class — the number of calendar days added to the current hold expiry
            date, as a whole number (integer, no decimals, greater than zero).

    Returns:
        A confirmation string with: the deal reference (text), the previous hold expiry date (YYYY-MM-DD),
        the calendar days added (integer), the new hold expiry date (YYYY-MM-DD, the new last day of the
        hold) and the new extension count (integer). A string that starts with "Hold extended" means the
        extension was recorded; a string that starts with "Error:" means the days were not a whole number
        greater than zero and nothing was changed.
    """
    if isinstance(extension_days, bool) or float(extension_days) != int(float(extension_days)) or int(float(extension_days)) <= 0:
        return "Error: extension_days must be a whole number greater than zero; nothing was changed."
    days = int(float(extension_days))
    deal = (ctx.find("purchase_deals", purchase_deal_id=purchase_deal_id) or [{}])[0]
    old = str(deal.get("hold_expires_date") or ctx.now()[:10])[:10]
    new_date = _DealCalendar.add_days(old, days)
    count = int(deal.get("hold_extension_count") or 0) + 1
    ctx.update("purchase_deals", purchase_deal_id, hold_expires_date=new_date, hold_extension_count=count)
    return (f"Hold extended: deal {purchase_deal_id}, hold expiry {old} moved forward {days} day(s) to {new_date}; "
            f"extensions granted now {count}.")

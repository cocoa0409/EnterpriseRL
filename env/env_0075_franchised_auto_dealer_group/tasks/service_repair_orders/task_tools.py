"""Hidden task tools of the service_repair_orders difficulty (env_0075, Kessler Automotive Group).

Each tool performs one atomic write on a service account and its repair order ledger, with the
values the agent has already worked out from the published policies. No tool judges eligibility or
prerequisites, and no tool works out an amount: each one only enforces what its argument descriptions
state (number formats, rounding to the cent, amounts and points above zero, the closed sets of
concern lines, and the ledger row a credit must name), returning a string that starts with Error
when an argument breaks that description.
"""

from erlbench import ToolContext, tool


class _Fmt:
    """Format helpers the tools share: exact half-up rounding to the cent, number parsing and the month format."""

    LINES = ("A", "B", "C", "D", "E", "F", "G", "H")

    @staticmethod
    def _decimal(value):
        if isinstance(value, bool):
            return None
        if isinstance(value, (int, float)):
            text = repr(value)
        elif isinstance(value, str):
            text = value.strip()
        else:
            return None
        sign = ""
        if text[:1] in "+-":
            sign, text = text[0], text[1:]
        whole, _, frac = text.partition(".")
        if not whole.isdigit() or (frac and not frac.isdigit()) or (_ and not frac):
            return None
        return sign, whole, frac

    @staticmethod
    def cents(value):
        """Exact half-up rounding of a plain decimal number to whole cents, returned as a float of two places."""
        if isinstance(value, float):
            if value != value or value in (float("inf"), float("-inf")):
                raise ValueError("not a finite number")
            parts = _Fmt._decimal(format(value, ".10f"))
        else:
            parts = _Fmt._decimal(value)
        if parts is None:
            raise ValueError("not a plain decimal number")
        sign, whole, frac = parts
        frac = (frac + "000")[:3]
        n = int(whole) * 1000 + int(frac)
        c = (n + 5) // 10
        v = c / 100.0
        return -v if sign == "-" else v

    @staticmethod
    def money(value):
        """A finite plain decimal amount rounded half up to the cent, or None when the value is not one."""
        if _Fmt._decimal(value) is None:
            return None
        return _Fmt.cents(value)

    @staticmethod
    def whole(value):
        """A whole number given as an integer or a string of digits, or None."""
        if isinstance(value, bool):
            return None
        if isinstance(value, int):
            return value
        if isinstance(value, str) and value.isdigit():
            return int(value)
        return None

    @staticmethod
    def is_month(value):
        s = str(value)
        return (len(s) == 7 and s[4] == "-" and s[:4].isdigit() and s[5:].isdigit()
                and 1 <= int(s[5:]) <= 12)

@tool(owner="user", rw="write")
def redeem_owner_points_3e3ce956(ctx: ToolContext, service_account_id: str, repair_order_number: str,
                                 points: int, credit_amount: float) -> str:
    """The account holder redeems Owner Rewards points toward one of their own repair orders. One call books the redemption: the points are taken off the account's rewards points balance, and a rewards redemption credit for the stated dollar amount is applied to the named repair order, lowering what the holder owes on the account by that amount. The holder sees the new points balance and the lower amount owed. The redemption is complete when the receipt shows the redemption reference.

    Args:
        service_account_id: Id class — the reference number of the holder's service account, as returned by the service account lookup.
        repair_order_number: Verbatim class — the repair order number the points are applied to, copied character for character from the repair order lines returned by the ledger lookup, preserving its spacing, digits and punctuation, with no normalisation (verbatim).
        points: Fixed-format class — the number of Owner Rewards points redeemed, a whole number of points (integer, no decimals, no separators), greater than zero.
        credit_amount: Fixed-format class — the dollar credit the redeemed points apply to the repair order, in US dollars as a decimal number with 2 decimal places (cents), rounded half up to the cent (the tool rounds any further digits half up), greater than zero, written in plain decimal notation with no currency sign, separators or exponent.

    Returns:
        A one-line confirmation string naming the redemption reference (text id of the points redemption entry), the repair order number, the points redeemed (integer), the credit applied (US dollars, two decimals), the account's resulting points balance (integer) and the resulting amount owed on the account (US dollars, two decimals). A string starting with the word Redeemed indicates the redemption was booked.
    """
    acct = ctx.find("service_accounts", service_account_id=service_account_id)[0]
    day = ctx.now()[:10]
    pts = _Fmt.whole(points)
    if pts is None or pts <= 0:
        return "Error: points must be a whole number greater than zero."
    amt = _Fmt.money(credit_amount)
    if amt is None or amt <= 0:
        return "Error: credit_amount must be a plain decimal amount greater than zero after rounding to the cent."
    rid = ctx.make_id("srv_", "redeem", service_account_id, repair_order_number, pts, amt, day)
    ctx.create("service_ro_lines", rid, service_line_id=rid, service_account_id=service_account_id,
               customer_id=acct["customer_id"], event_type="service_points_redeemed", store_id=None,
               vehicle_id=None, repair_order_number=repair_order_number, line_letter="not_applicable",
               line_date=day, pay_type=None, labor_hours=0.0, labor_rate=0.0, list_amount=0.0, amount=amt,
               quantity=0, fee_code="not_applicable", credit_reason="not_applicable",
               payment_method="not_applicable", points=pts, odometer_in=None, source_line_id=None,
               billing_month=None)
    cid = ctx.make_id("srv_", "redeem_credit", rid)
    ctx.create("service_ro_lines", cid, service_line_id=cid, service_account_id=service_account_id,
               customer_id=acct["customer_id"], event_type="service_line_credited", store_id=None,
               vehicle_id=None, repair_order_number=repair_order_number, line_letter="not_applicable",
               line_date=day, pay_type=None, labor_hours=0.0, labor_rate=0.0, list_amount=0.0, amount=amt,
               quantity=0, fee_code="not_applicable", credit_reason="rewards_redemption",
               payment_method="not_applicable", points=0, odometer_in=None, source_line_id=None,
               billing_month=None)
    new_pts = int(acct["rewards_points_balance"]) - pts
    new_bal = _Fmt.cents(float(acct["open_balance"]) - amt)
    ctx.update("service_accounts", service_account_id, rewards_points_balance=new_pts, open_balance=new_bal)
    return (f"Redeemed: reference {rid}, repair order {repair_order_number}, {pts} points, credit {amt:.2f}, "
            f"points balance now {new_pts}, amount owed now {new_bal:.2f}.")


@tool(owner="agent", rw="write")
def credit_paid_ro_points_b77dd6a9(ctx: ToolContext, service_account_id: str, repair_order_number: str,
                                   points: int) -> str:
    """Credits Owner Rewards points earned on a paid repair order to the account holder's rewards balance. One call books one points-earned entry for the named repair order, dated today, and raises the account's rewards points balance by that number of points. The holder sees the higher points balance. The credit is complete when the receipt shows the points entry reference.

    Args:
        service_account_id: Id class — the reference number of the holder's service account, as returned by the service account lookup.
        repair_order_number: Verbatim class — the repair order number the points are earned on, copied character for character from the repair order lines returned by the ledger lookup, preserving its spacing, digits and punctuation, with no normalisation (verbatim).
        points: Fixed-format class — the number of points credited, a whole number of points (integer, no decimals, no separators), greater than zero.

    Returns:
        A one-line confirmation string naming the points entry reference (text id), the repair order number, the points credited (integer) and the account's resulting points balance (integer). A string starting with the word Credited indicates the points were booked.
    """
    acct = ctx.find("service_accounts", service_account_id=service_account_id)[0]
    day = ctx.now()[:10]
    pts = _Fmt.whole(points)
    if pts is None or pts <= 0:
        return "Error: points must be a whole number greater than zero."
    rid = ctx.make_id("srv_", "earn", service_account_id, repair_order_number, pts, day)
    ctx.create("service_ro_lines", rid, service_line_id=rid, service_account_id=service_account_id,
               customer_id=acct["customer_id"], event_type="service_points_earned", store_id=None,
               vehicle_id=None, repair_order_number=repair_order_number, line_letter="not_applicable",
               line_date=day, pay_type=None, labor_hours=0.0, labor_rate=0.0, list_amount=0.0, amount=0.0,
               quantity=0, fee_code="not_applicable", credit_reason="not_applicable",
               payment_method="not_applicable", points=pts, odometer_in=None, source_line_id=None,
               billing_month=None)
    new_pts = int(acct["rewards_points_balance"]) + pts
    ctx.update("service_accounts", service_account_id, rewards_points_balance=new_pts)
    return (f"Credited: reference {rid}, repair order {repair_order_number}, {pts} points, "
            f"points balance now {new_pts}.")


@tool(owner="agent", rw="write")
def credit_estimate_overage_3db3cf5c(ctx: ToolContext, service_account_id: str, repair_order_number: str,
                                     line_letter: str, source_line_id: str, credit_amount: float) -> str:
    """Credits back to the customer the part of a concern line's charges billed beyond the estimate the customer authorized. One call books one estimate overage credit against the named labor charge of the repair order, dated today, and lowers the amount owed on the service account by the credit. The customer sees the credit on the repair order and the lower amount owed. The credit is complete when the receipt shows the credit reference.

    Args:
        service_account_id: Id class — the reference number of the customer's service account, as returned by the service account lookup.
        repair_order_number: Verbatim class — the repair order number of the concern line, copied character for character from the repair order lines returned by the ledger lookup, preserving its spacing, digits and punctuation, with no normalisation (verbatim).
        line_letter: Enum class — the concern line credited, one of: A (the first concern line of the repair order), B (the second concern line), C (the third concern line), D (the fourth concern line), E (the fifth concern line), F (the sixth concern line), G (the seventh concern line), H (the eighth concern line), not_applicable (a charge that belongs to the repair order as a whole rather than to one concern line); it must be the concern line of the charge named by source_line_id, or the tool returns an error.
        source_line_id: Id class — the reference number of the labor charge the credit reduces, as returned for that charge by the repair order ledger lookup; it must be a labor charge row of the same service account and repair order, or the tool returns an error.
        credit_amount: Fixed-format class — the overage credit in US dollars as a decimal number with 2 decimal places (cents), rounded half up to the cent (the tool rounds any further digits half up), greater than zero, written in plain decimal notation with no currency sign, separators or exponent.

    Returns:
        A one-line confirmation string naming the credit reference (text id), the repair order number and concern line, the credit amount (US dollars, two decimals) and the resulting amount owed on the account (US dollars, two decimals). A string starting with the word Credited indicates the credit was booked.
    """
    acct = ctx.find("service_accounts", service_account_id=service_account_id)[0]
    day = ctx.now()[:10]
    amt = _Fmt.money(credit_amount)
    if amt is None or amt <= 0:
        return "Error: credit_amount must be a plain decimal amount greater than zero after rounding to the cent."
    if line_letter not in _Fmt.LINES + ("not_applicable",):
        return "Error: line_letter must be one of A to H or not_applicable."
    src = ctx.find("service_ro_lines", service_line_id=source_line_id, service_account_id=service_account_id,
                   event_type="service_labor_charged",
                   repair_order_number=repair_order_number)
    if not src:
        return "Error: source_line_id must name a labor charge row of this service account and repair order."
    if src[0]["line_letter"] != line_letter:
        return "Error: line_letter must be the concern line of the row named by source_line_id."
    rid = ctx.make_id("srv_", "overage", service_account_id, repair_order_number, line_letter, source_line_id, amt, day)
    ctx.create("service_ro_lines", rid, service_line_id=rid, service_account_id=service_account_id,
               customer_id=acct["customer_id"], event_type="service_line_credited", store_id=None,
               vehicle_id=None, repair_order_number=repair_order_number, line_letter=line_letter,
               line_date=day, pay_type=None, labor_hours=0.0, labor_rate=0.0, list_amount=0.0, amount=amt,
               quantity=0, fee_code="not_applicable", credit_reason="estimate_overage",
               payment_method="not_applicable", points=0, odometer_in=None, source_line_id=source_line_id,
               billing_month=None)
    new_bal = _Fmt.cents(float(acct["open_balance"]) - amt)
    ctx.update("service_accounts", service_account_id, open_balance=new_bal)
    return (f"Credited: reference {rid}, repair order {repair_order_number} line {line_letter}, "
            f"overage credit {amt:.2f}, amount owed now {new_bal:.2f}.")


@tool(owner="agent", rw="write")
def expire_owner_points_a6cb3dc9(ctx: ToolContext, service_account_id: str, billing_month: str,
                                 points: int) -> str:
    """Posts the month-end expiry of Owner Rewards points on a service account. One call books one points-expired entry for the stated month, dated today, and lowers the account's rewards points balance by the points expired. The account holder sees the lower points balance. The expiry is complete when the receipt shows the expiry reference.

    Args:
        service_account_id: Id class — the reference number of the holder's service account, as returned by the service account lookup.
        billing_month: Fixed-format class — the calendar month of the month-end run, written YYYY-MM (four-digit year, hyphen, two-digit month).
        points: Fixed-format class — the number of points expired, a whole number of points (integer, no decimals, no separators), greater than zero.

    Returns:
        A one-line confirmation string naming the expiry reference (text id), the month (YYYY-MM), the points expired (integer) and the account's resulting points balance (integer). A string starting with the word Expired indicates the expiry was booked.
    """
    acct = ctx.find("service_accounts", service_account_id=service_account_id)[0]
    day = ctx.now()[:10]
    pts = _Fmt.whole(points)
    if pts is None or pts <= 0:
        return "Error: points must be a whole number greater than zero."
    if not _Fmt.is_month(billing_month):
        return "Error: billing_month must be written YYYY-MM."
    rid = ctx.make_id("srv_", "expire", service_account_id, billing_month, pts, day)
    ctx.create("service_ro_lines", rid, service_line_id=rid, service_account_id=service_account_id,
               customer_id=acct["customer_id"], event_type="service_points_expired", store_id=None,
               vehicle_id=None, repair_order_number=None, line_letter="not_applicable",
               line_date=day, pay_type=None, labor_hours=0.0, labor_rate=0.0, list_amount=0.0, amount=0.0,
               quantity=0, fee_code="not_applicable", credit_reason="not_applicable",
               payment_method="not_applicable", points=pts, odometer_in=None, source_line_id=None,
               billing_month=billing_month)
    new_pts = int(acct["rewards_points_balance"]) - pts
    ctx.update("service_accounts", service_account_id, rewards_points_balance=new_pts)
    return (f"Expired: reference {rid}, month {billing_month}, {pts} points, points balance now {new_pts}.")


@tool(owner="user", rw="write")
def authorize_repair_estimate_690e2aa2(ctx: ToolContext, service_account_id: str, repair_order_number: str,
                                       line_letter: str, estimate_amount: float) -> str:
    """The account holder authorizes the written estimate for one diagnosed concern line of their repair order, at the stated customer-pay amount. One call records the customer's own decision as an authorized estimate decision for that line, dated today. No charge is posted by this call. The customer sees the authorization confirmed with its reference. The decision is recorded when the receipt shows the authorization reference.

    Args:
        service_account_id: Id class — the reference number of the customer's service account, as returned by the service account lookup.
        repair_order_number: Verbatim class — the repair order number of the diagnosed line, copied character for character from the repair order lines returned by the ledger lookup, preserving its spacing, digits and punctuation, with no normalisation (verbatim).
        line_letter: Enum class — the concern line authorized, one of: A (the first concern line of the repair order), B (the second concern line), C (the third concern line), D (the fourth concern line), E (the fifth concern line), F (the sixth concern line), G (the seventh concern line), H (the eighth concern line).
        estimate_amount: Fixed-format class — the customer-pay amount of the written estimate being authorized (labor and parts, excluding shop fees), in US dollars as a decimal number with 2 decimal places (cents), rounded half up to the cent (the tool rounds any further digits half up), greater than zero, written in plain decimal notation with no currency sign, separators or exponent.

    Returns:
        A one-line confirmation string naming the authorization reference (text id), the repair order number and concern line, the authorized estimate amount (US dollars, two decimals) and the decision date (YYYY-MM-DD). A string starting with the word Authorized indicates the decision was recorded.
    """
    acct = ctx.find("service_accounts", service_account_id=service_account_id)[0]
    day = ctx.now()[:10]
    amt = _Fmt.money(estimate_amount)
    if amt is None or amt <= 0:
        return "Error: estimate_amount must be a plain decimal amount greater than zero after rounding to the cent."
    if line_letter not in _Fmt.LINES:
        return "Error: line_letter must be one of A to H."
    rid = ctx.make_id("sra_", service_account_id, repair_order_number, line_letter, amt, day)
    ctx.create("service_repair_authorizations", rid, service_auth_id=rid, customer_id=acct["customer_id"],
               service_account_id=service_account_id, repair_order_number=repair_order_number,
               line_letter=line_letter, estimate_amount=amt, decision="authorized", decided_date=day,
               created_at=ctx.now())
    return (f"Authorized: reference {rid}, repair order {repair_order_number} line {line_letter}, "
            f"estimate {amt:.2f}, decided {day}.")


@tool(owner="agent", rw="write")
def credit_diagnostic_fee_eae01e67(ctx: ToolContext, service_account_id: str, repair_order_number: str,
                                   line_letter: str, source_line_id: str, credit_amount: float) -> str:
    """Credits part or all of the diagnostic fee charged on a diagnosed concern line back to the customer. One call books one diagnostic credit against the named diagnostic fee charge, dated today, and lowers the amount owed on the service account by the credit. The customer sees the credit on the repair order and the lower amount owed. The credit is complete when the receipt shows the credit reference.

    Args:
        service_account_id: Id class — the reference number of the customer's service account, as returned by the service account lookup.
        repair_order_number: Verbatim class — the repair order number of the diagnostic fee, copied character for character from the repair order lines returned by the ledger lookup, preserving its spacing, digits and punctuation, with no normalisation (verbatim).
        line_letter: Enum class — the concern line of the diagnostic fee, one of: A (the first concern line of the repair order), B (the second concern line), C (the third concern line), D (the fourth concern line), E (the fifth concern line), F (the sixth concern line), G (the seventh concern line), H (the eighth concern line), not_applicable (a charge that belongs to the repair order as a whole rather than to one concern line); it must be the concern line of the charge named by source_line_id, or the tool returns an error.
        source_line_id: Id class — the reference number of the diagnostic fee charge the credit reduces, as returned for that charge by the repair order ledger lookup; it must be a diagnostic fee charge row of the same service account and repair order, or the tool returns an error.
        credit_amount: Fixed-format class — the diagnostic credit in US dollars as a decimal number with 2 decimal places (cents), rounded half up to the cent (the tool rounds any further digits half up), greater than zero, written in plain decimal notation with no currency sign, separators or exponent.

    Returns:
        A one-line confirmation string naming the credit reference (text id), the repair order number and concern line, the credit amount (US dollars, two decimals) and the resulting amount owed on the account (US dollars, two decimals). A string starting with the word Credited indicates the credit was booked.
    """
    acct = ctx.find("service_accounts", service_account_id=service_account_id)[0]
    day = ctx.now()[:10]
    amt = _Fmt.money(credit_amount)
    if amt is None or amt <= 0:
        return "Error: credit_amount must be a plain decimal amount greater than zero after rounding to the cent."
    if line_letter not in _Fmt.LINES + ("not_applicable",):
        return "Error: line_letter must be one of A to H or not_applicable."
    src = ctx.find("service_ro_lines", service_line_id=source_line_id, service_account_id=service_account_id,
                   event_type="service_diagnostic_fee_charged",
                   repair_order_number=repair_order_number)
    if not src:
        return "Error: source_line_id must name a diagnostic fee row of this service account and repair order."
    if src[0]["line_letter"] != line_letter:
        return "Error: line_letter must be the concern line of the row named by source_line_id."
    rid = ctx.make_id("srv_", "diagcredit", service_account_id, repair_order_number, line_letter, source_line_id, amt, day)
    ctx.create("service_ro_lines", rid, service_line_id=rid, service_account_id=service_account_id,
               customer_id=acct["customer_id"], event_type="service_line_credited", store_id=None,
               vehicle_id=None, repair_order_number=repair_order_number, line_letter=line_letter,
               line_date=day, pay_type=None, labor_hours=0.0, labor_rate=0.0, list_amount=0.0, amount=amt,
               quantity=0, fee_code="not_applicable", credit_reason="diagnostic_applied_to_repair",
               payment_method="not_applicable", points=0, odometer_in=None, source_line_id=source_line_id,
               billing_month=None)
    new_bal = _Fmt.cents(float(acct["open_balance"]) - amt)
    ctx.update("service_accounts", service_account_id, open_balance=new_bal)
    return (f"Credited: reference {rid}, repair order {repair_order_number} line {line_letter}, "
            f"diagnostic credit {amt:.2f}, amount owed now {new_bal:.2f}.")


@tool(owner="agent", rw="write")
def credit_early_payment_discount_b0e7362c(ctx: ToolContext, service_account_id: str, repair_order_number: str,
                                           line_letter: str, source_line_id: str, credit_amount: float) -> str:
    """Credits the early-payment discount earned on a fleet invoice that was paid in full inside its discount window. One call books one early-payment discount credit against the named labor charge of the invoice's repair order, dated today, and lowers the amount owed on the service account by the credit. The customer sees the discount on the invoice and the lower amount owed. The credit is complete when the receipt shows the credit reference.

    Args:
        service_account_id: Id class — the reference number of the fleet customer's service account, as returned by the service account lookup.
        repair_order_number: Verbatim class — the repair order number of the invoice, copied character for character from the repair order lines returned by the ledger lookup, preserving its spacing, digits and punctuation, with no normalisation (verbatim).
        line_letter: Enum class — the concern line of the labor charge the discount is booked against, one of: A (the first concern line of the repair order), B (the second concern line), C (the third concern line), D (the fourth concern line), E (the fifth concern line), F (the sixth concern line), G (the seventh concern line), H (the eighth concern line), not_applicable (a charge that belongs to the repair order as a whole rather than to one concern line); it must be the concern line of the charge named by source_line_id, or the tool returns an error.
        source_line_id: Id class — the reference number of the invoice's labor charge the discount is booked against, as returned for that charge by the repair order ledger lookup; it must be a labor charge row of the same service account and repair order, or the tool returns an error.
        credit_amount: Fixed-format class — the early-payment discount in US dollars as a decimal number with 2 decimal places (cents), rounded half up to the cent (the tool rounds any further digits half up), greater than zero, written in plain decimal notation with no currency sign, separators or exponent.

    Returns:
        A one-line confirmation string naming the credit reference (text id), the repair order number and concern line, the discount amount (US dollars, two decimals) and the resulting amount owed on the account (US dollars, two decimals). A string starting with the word Credited indicates the discount was booked.
    """
    acct = ctx.find("service_accounts", service_account_id=service_account_id)[0]
    day = ctx.now()[:10]
    amt = _Fmt.money(credit_amount)
    if amt is None or amt <= 0:
        return "Error: credit_amount must be a plain decimal amount greater than zero after rounding to the cent."
    if line_letter not in _Fmt.LINES + ("not_applicable",):
        return "Error: line_letter must be one of A to H or not_applicable."
    src = ctx.find("service_ro_lines", service_line_id=source_line_id, service_account_id=service_account_id,
                   event_type="service_labor_charged",
                   repair_order_number=repair_order_number)
    if not src:
        return "Error: source_line_id must name a labor charge row of this service account and repair order."
    if src[0]["line_letter"] != line_letter:
        return "Error: line_letter must be the concern line of the row named by source_line_id."
    rid = ctx.make_id("srv_", "earlypay", service_account_id, repair_order_number, line_letter, source_line_id, amt, day)
    ctx.create("service_ro_lines", rid, service_line_id=rid, service_account_id=service_account_id,
               customer_id=acct["customer_id"], event_type="service_line_credited", store_id=None,
               vehicle_id=None, repair_order_number=repair_order_number, line_letter=line_letter,
               line_date=day, pay_type=None, labor_hours=0.0, labor_rate=0.0, list_amount=0.0, amount=amt,
               quantity=0, fee_code="not_applicable", credit_reason="early_payment_discount",
               payment_method="not_applicable", points=0, odometer_in=None, source_line_id=source_line_id,
               billing_month=None)
    new_bal = _Fmt.cents(float(acct["open_balance"]) - amt)
    ctx.update("service_accounts", service_account_id, open_balance=new_bal)
    return (f"Credited: reference {rid}, repair order {repair_order_number} line {line_letter}, "
            f"early-payment discount {amt:.2f}, amount owed now {new_bal:.2f}.")


@tool(owner="agent", rw="write")
def credit_comeback_labor_f15915d4(ctx: ToolContext, service_account_id: str, repair_order_number: str,
                                   line_letter: str, source_line_id: str, credit_amount: float) -> str:
    """Credits the labor of a repeat repair that the store's repair warranty covers as a comeback, together with any shop fees refunded with it. One call books one comeback credit against the named repeat labor charge, dated today, and lowers the amount owed on the service account by the credit. The customer sees the credit on the repair order and the lower amount owed. The credit is complete when the receipt shows the credit reference.

    Args:
        service_account_id: Id class — the reference number of the customer's service account, as returned by the service account lookup.
        repair_order_number: Verbatim class — the repair order number of the repeat repair, copied character for character from the repair order lines returned by the ledger lookup, preserving its spacing, digits and punctuation, with no normalisation (verbatim).
        line_letter: Enum class — the concern line of the repeat labor charge, one of: A (the first concern line of the repair order), B (the second concern line), C (the third concern line), D (the fourth concern line), E (the fifth concern line), F (the sixth concern line), G (the seventh concern line), H (the eighth concern line), not_applicable (a charge that belongs to the repair order as a whole rather than to one concern line); it must be the concern line of the charge named by source_line_id, or the tool returns an error.
        source_line_id: Id class — the reference number of the repeat labor charge the credit reduces, as returned for that charge by the repair order ledger lookup; it must be a labor charge row of the same service account and repair order, or the tool returns an error.
        credit_amount: Fixed-format class — the comeback credit in US dollars as a decimal number with 2 decimal places (cents), rounded half up to the cent (the tool rounds any further digits half up), greater than zero, written in plain decimal notation with no currency sign, separators or exponent.

    Returns:
        A one-line confirmation string naming the credit reference (text id), the repair order number and concern line, the credit amount (US dollars, two decimals) and the resulting amount owed on the account (US dollars, two decimals). A string starting with the word Credited indicates the credit was booked.
    """
    acct = ctx.find("service_accounts", service_account_id=service_account_id)[0]
    day = ctx.now()[:10]
    amt = _Fmt.money(credit_amount)
    if amt is None or amt <= 0:
        return "Error: credit_amount must be a plain decimal amount greater than zero after rounding to the cent."
    if line_letter not in _Fmt.LINES + ("not_applicable",):
        return "Error: line_letter must be one of A to H or not_applicable."
    src = ctx.find("service_ro_lines", service_line_id=source_line_id, service_account_id=service_account_id,
                   event_type="service_labor_charged",
                   repair_order_number=repair_order_number)
    if not src:
        return "Error: source_line_id must name a labor charge row of this service account and repair order."
    if src[0]["line_letter"] != line_letter:
        return "Error: line_letter must be the concern line of the row named by source_line_id."
    rid = ctx.make_id("srv_", "comeback", service_account_id, repair_order_number, line_letter, source_line_id, amt, day)
    ctx.create("service_ro_lines", rid, service_line_id=rid, service_account_id=service_account_id,
               customer_id=acct["customer_id"], event_type="service_line_credited", store_id=None,
               vehicle_id=None, repair_order_number=repair_order_number, line_letter=line_letter,
               line_date=day, pay_type=None, labor_hours=0.0, labor_rate=0.0, list_amount=0.0, amount=amt,
               quantity=0, fee_code="not_applicable", credit_reason="comeback_repair",
               payment_method="not_applicable", points=0, odometer_in=None, source_line_id=source_line_id,
               billing_month=None)
    new_bal = _Fmt.cents(float(acct["open_balance"]) - amt)
    ctx.update("service_accounts", service_account_id, open_balance=new_bal)
    return (f"Credited: reference {rid}, repair order {repair_order_number} line {line_letter}, "
            f"comeback credit {amt:.2f}, amount owed now {new_bal:.2f}.")

"""Hidden task tools for the private_pay_residency_billing difficulty of env_0074 (Keystone Ridge Health & Rehabilitation).

Each tool lands one atomic write on a private-pay admission agreement's ledger and keeps the agreement's running
balances in step with it. The figures are worked out by the caller from the published billing rules; the tools
take them as given and judge nothing.
"""

from erlbench import ToolContext, tool
from decimal import Decimal, ROUND_HALF_UP


class _Fmt:
    """Format helpers shared by the tools below: money to the cent rounded half up, and calendar date / month checks."""

    @staticmethod
    def cents(value):
        return float(Decimal(str(value)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP))

    @staticmethod
    def is_date(value):
        s = str(value)
        if len(s) != 10 or s[4] != "-" or s[7] != "-" or not (s[:4] + s[5:7] + s[8:]).isdigit():
            return False
        m, d = int(s[5:7]), int(s[8:])
        return 1 <= m <= 12 and 1 <= d <= 31

    @staticmethod
    def is_month(value):
        s = str(value)
        return len(s) == 7 and s[4] == "-" and (s[:4] + s[5:]).isdigit() and 1 <= int(s[5:]) <= 12


@tool(owner="agent", rw="write")
def credit_late_notice_days_45589810(ctx: ToolContext, private_agreement_id: str, charge_entry_id: str, adjustment_reason: str, from_date: str,
                                      day_count: int, amount: float) -> str:
    """Post a late-notice rate credit against one room-and-board charge of a private-pay admission agreement. The business office uses it when days on that charge were priced at a new private-pay rate that had not yet taken effect for the agreement because the written rate notice came late. One call books one credit entry naming the charge and the reason given, records its starting day and its day count, and lowers the agreement's private-pay balance by the credit amount; the credit shows on the resident's statement and ledger against that charge.

    Args:
        private_agreement_id: Id class — the reference number of the resident's private-pay admission agreement, as shown by the agreement lookup for the resident.
        charge_entry_id: Id class — the ledger reference number of the room-and-board charge being credited, as shown by the private-pay ledger lookup for the agreement.
        adjustment_reason: Enum class — why the charge is credited, one of: rate_notice_late (days on the charge were priced at a new rate that had not yet taken effect for the agreement); room_change_proration (days on an advance charge for a room the resident has moved out of); discharge_proration (days billed for after a discharge); death_proration (days billed for after the resident's death); payer_conversion_credit (days billed privately that another payer source covers); billing_error (an amount billed by mistake for any other reason).
        from_date: Fixed-format class — the calendar date of the earliest day the credit covers, written YYYY-MM-DD.
        day_count: Fixed-format class — the number of days the credit covers, a whole number of integer days.
        amount: Fixed-format class — the credit in USD, a positive amount to 2 decimal places, rounded half up to the cent.

    Returns:
        A text rendering of a dictionary with keys: status ("credited" when the entry was booked), private_entry_id (the new ledger reference number), charge_entry_id (the charge credited), adjustment_reason (the reason given), from_date (YYYY-MM-DD), day_count (integer days), amount (USD, 2 decimal places) and account_balance (the agreement's private-pay balance in USD to 2 decimal places once the credit is posted; negative means a credit balance).
    """
    amt = _Fmt.cents(amount)
    if amt <= 0:
        return "Error: amount must be a positive USD amount"
    if not _Fmt.is_date(from_date) or int(day_count) <= 0:
        return "Error: from_date must be YYYY-MM-DD and day_count a positive whole number of days"
    rid = ctx.make_id("pad_", private_agreement_id, charge_entry_id, adjustment_reason, from_date, day_count, amt)
    agr = ctx.find("private_agreements", private_agreement_id=private_agreement_id)[0]
    ctx.create("private_ledger", rid, private_entry_id=rid, private_agreement_id=private_agreement_id,
               customer_id=agr["customer_id"], event_type="private_adjustment", charge_entry_id=charge_entry_id,
               adjustment_reason=adjustment_reason, from_date=from_date, day_count=int(day_count), amount=amt,
               entry_date=ctx.now()[:10])
    bal = _Fmt.cents(float(agr.get("account_balance") or 0) - amt)
    ctx.update("private_agreements", private_agreement_id, account_balance=bal)
    return str({"status": "credited", "private_entry_id": rid, "charge_entry_id": charge_entry_id,
                "adjustment_reason": adjustment_reason, "from_date": from_date, "day_count": int(day_count),
                "amount": amt, "account_balance": bal})


@tool(owner="agent", rw="write")
def credit_room_change_days_09a50cb9(ctx: ToolContext, private_agreement_id: str, charge_entry_id: str, adjustment_reason: str, from_date: str,
                                     day_count: int, amount: float) -> str:
    """Post a room-change credit against the advance room-and-board charge billed for the room a resident left. The business office uses it when a resident has moved to a room of another tier inside a month already billed in advance for the old room. One call books one credit entry naming the charge and the reason given, records its starting day and its day count, and lowers the agreement's private-pay balance by the credit amount; the credit shows on the resident's statement and ledger against that charge.

    Args:
        private_agreement_id: Id class — the reference number of the resident's private-pay admission agreement, as shown by the agreement lookup for the resident.
        charge_entry_id: Id class — the ledger reference number of the room-and-board charge for the room the resident left, as shown by the private-pay ledger lookup for the agreement.
        adjustment_reason: Enum class — why the charge is credited, one of: rate_notice_late (days on the charge were priced at a new rate that had not yet taken effect for the agreement); room_change_proration (days on an advance charge for a room the resident has moved out of); discharge_proration (days billed for after a discharge); death_proration (days billed for after the resident's death); payer_conversion_credit (days billed privately that another payer source covers); billing_error (an amount billed by mistake for any other reason).
        from_date: Fixed-format class — the calendar date of the earliest day the credit takes off the charge, written YYYY-MM-DD.
        day_count: Fixed-format class — the number of days the credit takes off the charge, a whole number of integer days.
        amount: Fixed-format class — the credit in USD, a positive amount to 2 decimal places, rounded half up to the cent.

    Returns:
        A text rendering of a dictionary with keys: status ("credited" when the entry was booked), private_entry_id (the new ledger reference number), charge_entry_id (the charge credited), adjustment_reason (the reason given), from_date (YYYY-MM-DD), day_count (integer days), amount (USD, 2 decimal places) and account_balance (the agreement's private-pay balance in USD to 2 decimal places once the credit is posted; negative means a credit balance).
    """
    amt = _Fmt.cents(amount)
    if amt <= 0:
        return "Error: amount must be a positive USD amount"
    if not _Fmt.is_date(from_date) or int(day_count) <= 0:
        return "Error: from_date must be YYYY-MM-DD and day_count a positive whole number of days"
    rid = ctx.make_id("prc_", private_agreement_id, charge_entry_id, adjustment_reason, from_date, day_count, amt)
    agr = ctx.find("private_agreements", private_agreement_id=private_agreement_id)[0]
    ctx.create("private_ledger", rid, private_entry_id=rid, private_agreement_id=private_agreement_id,
               customer_id=agr["customer_id"], event_type="private_adjustment", charge_entry_id=charge_entry_id,
               adjustment_reason=adjustment_reason, from_date=from_date, day_count=int(day_count), amount=amt,
               entry_date=ctx.now()[:10])
    bal = _Fmt.cents(float(agr.get("account_balance") or 0) - amt)
    ctx.update("private_agreements", private_agreement_id, account_balance=bal)
    return str({"status": "credited", "private_entry_id": rid, "charge_entry_id": charge_entry_id,
                "adjustment_reason": adjustment_reason, "from_date": from_date, "day_count": int(day_count),
                "amount": amt, "account_balance": bal})


@tool(owner="agent", rw="write")
def post_new_room_span_526f1e53(ctx: ToolContext, private_agreement_id: str, service_month: str, from_date: str,
                                to_date: str, day_count: int, accommodation_tier: str, daily_rate: float,
                                charge_basis: str, amount: float) -> str:
    """Post one room-and-board span charge on a private-pay admission agreement for a stretch of one service month spent in a resident's new room. One call books one room-and-board charge entry for the given service month, span dates, chargeable days, tier, daily rate and charge basis, and raises the agreement's private-pay balance by the charge amount; the span appears on the resident's statement and ledger as its own charge line.

    Args:
        private_agreement_id: Id class — the reference number of the resident's private-pay admission agreement, as shown by the agreement lookup for the resident.
        service_month: Fixed-format class — the calendar month of service the span belongs to, written YYYY-MM.
        from_date: Fixed-format class — the calendar date of the earliest day of the span, written YYYY-MM-DD.
        to_date: Fixed-format class — the calendar date of the last day of the span, written YYYY-MM-DD.
        day_count: Fixed-format class — the chargeable days of the span, a whole number of integer days.
        accommodation_tier: Enum class — the accommodation tier whose daily rate prices the span, one of: Private Long-Term Care Room (a one-bed long-term care room off the secured unit); Private Secure Memory Care Room (a one-bed room on the secured memory care unit); Semi-Private Long-Term Care Room (a two-bed long-term care room off the secured unit); Semi-Private Secure Memory Care Room (a two-bed room on the secured memory care unit); Private Bariatric Care Room (the one-bed room equipped for bariatric care); Private Suite with Sitting Area (the one-bed suite with a separate sitting area).
        daily_rate: Fixed-format class — the daily rate applied to the span in USD per day, to 2 decimal places.
        charge_basis: Enum class — why the span is priced as it is, one of: standard (an ordinary span at the tier's own rate); first_month_partial (the admission month charged from the admission date); isolation_rate (a span priced at the isolation billing tier's rate while the center itself keeps the resident in the room for infection control); prior_rate_notice_hold (a span priced at the earlier scheduled rate because the written notice of the new rate has not yet run its notice period).
        amount: Fixed-format class — the charge in USD, a positive amount to 2 decimal places, rounded half up to the cent.

    Returns:
        A text rendering of a dictionary with keys: status ("charged" when the entry was booked), private_entry_id (the new ledger reference number), service_month (YYYY-MM), from_date and to_date (YYYY-MM-DD), day_count (integer days), accommodation_tier (official tier name), daily_rate (USD per day, 2 decimal places), charge_basis, amount (USD, 2 decimal places) and account_balance (the agreement's private-pay balance in USD to 2 decimal places once the charge is posted; negative means a credit balance).
    """
    amt = _Fmt.cents(amount)
    if amt <= 0:
        return "Error: amount must be a positive USD amount"
    rate = _Fmt.cents(daily_rate)
    if rate <= 0:
        return "Error: daily_rate must be a positive USD amount"
    if not (_Fmt.is_month(service_month) and _Fmt.is_date(from_date) and _Fmt.is_date(to_date)):
        return "Error: service_month must be YYYY-MM and from_date/to_date YYYY-MM-DD"
    if int(day_count) <= 0:
        return "Error: day_count must be a positive whole number of days"
    rid = ctx.make_id("prb_", private_agreement_id, service_month, from_date, to_date, day_count, accommodation_tier,
                      rate, charge_basis, amt)
    agr = ctx.find("private_agreements", private_agreement_id=private_agreement_id)[0]
    ctx.create("private_ledger", rid, private_entry_id=rid, private_agreement_id=private_agreement_id,
               customer_id=agr["customer_id"], event_type="private_room_board_charge", service_month=service_month,
               from_date=from_date, to_date=to_date, day_count=int(day_count), accommodation_tier=accommodation_tier,
               daily_rate=rate, charge_basis=charge_basis, amount=amt, entry_date=ctx.now()[:10])
    bal = _Fmt.cents(float(agr.get("account_balance") or 0) + amt)
    ctx.update("private_agreements", private_agreement_id, account_balance=bal)
    return str({"status": "charged", "private_entry_id": rid, "service_month": service_month, "from_date": from_date,
                "to_date": to_date, "day_count": int(day_count), "accommodation_tier": accommodation_tier,
                "daily_rate": rate, "charge_basis": charge_basis, "amount": amt, "account_balance": bal})


@tool(owner="user", rw="write")
def pay_additional_deposit_f9f00bc8(ctx: ToolContext, private_agreement_id: str, payment_method: str,
                                    amount: float) -> str:
    """Pay money into the refundable security deposit held on the resident's private-pay admission agreement. The resident or the representative makes this payment in person over their own account. One call books one deposit receipt for the amount paid by the chosen method and raises the agreement's security deposit balance by that amount; the receipt shows on the resident's ledger and the new deposit balance is returned.

    Args:
        private_agreement_id: Id class — the reference number of the resident's private-pay admission agreement, as read out by the business office from the agreement lookup.
        payment_method: Enum class — how the payer hands over the money, one of: check (a personal check); certified_check (a bank-certified or cashier's check); money_order (a money order); ach (an electronic transfer from the payer's bank account); card (a debit or credit card); deposit_application (funds already held by the center as a security deposit and moved into this deposit, never new money from the payer).
        amount: Fixed-format class — the deposit paid in USD, a positive amount to 2 decimal places, rounded half up to the cent.

    Returns:
        A text rendering of a dictionary with keys: status ("received" when the receipt was booked), private_entry_id (the deposit receipt's ledger reference number), payment_method, amount (USD, 2 decimal places) and deposit_balance (the agreement's security deposit balance in USD to 2 decimal places once the receipt is booked).
    """
    amt = _Fmt.cents(amount)
    if amt <= 0:
        return "Error: amount must be a positive USD amount"
    rid = ctx.make_id("pdr_", private_agreement_id, payment_method, amt)
    agr = ctx.find("private_agreements", private_agreement_id=private_agreement_id)[0]
    ctx.create("private_ledger", rid, private_entry_id=rid, private_agreement_id=private_agreement_id,
               customer_id=agr["customer_id"], event_type="private_deposit_received", payment_method=payment_method,
               amount=amt, entry_date=ctx.now()[:10])
    dep = _Fmt.cents(float(agr.get("deposit_balance") or 0) + amt)
    ctx.update("private_agreements", private_agreement_id, deposit_balance=dep)
    return str({"status": "received", "private_entry_id": rid, "payment_method": payment_method, "amount": amt,
                "deposit_balance": dep})


@tool(owner="agent", rw="write")
def credit_converted_days_12618703(ctx: ToolContext, private_agreement_id: str, charge_entry_id: str, adjustment_reason: str,
                                   from_date: str, day_count: int, amount: float) -> str:
    """Post a credit against an advance room-and-board charge of a private-pay admission agreement for days another payer source took over. The business office uses it when a month was billed in advance to the resident while Medicare Part A, Medicaid or hospice room and board covered part of it. One call books one credit entry naming the charge and the reason given, records its starting day and its day count, and lowers the agreement's private-pay balance by the credit amount; the credit shows on the resident's statement and ledger against that charge.

    Args:
        private_agreement_id: Id class — the reference number of the resident's private-pay admission agreement, as shown by the agreement lookup for the resident.
        charge_entry_id: Id class — the ledger reference number of the advance room-and-board charge being credited, as shown by the private-pay ledger lookup for the agreement.
        adjustment_reason: Enum class — why the charge is credited, one of: payer_conversion_credit (days on an advance charge that another payer source covers); rate_notice_late (days on the charge were priced at a new rate that had not yet taken effect for the agreement); room_change_proration (days on an advance charge for a room the resident has moved out of); discharge_proration (days billed for after a discharge); death_proration (days billed for after the resident's death); billing_error (an amount billed by mistake for any other reason).
        from_date: Fixed-format class — the calendar date of the earliest day the credit covers, written YYYY-MM-DD.
        day_count: Fixed-format class — the number of days the credit covers, a whole number of integer days.
        amount: Fixed-format class — the credit in USD, a positive amount to 2 decimal places, rounded half up to the cent.

    Returns:
        A text rendering of a dictionary with keys: status ("credited" when the entry was booked), private_entry_id (the new ledger reference number), charge_entry_id (the charge credited), adjustment_reason (the reason given), from_date (YYYY-MM-DD), day_count (integer days), amount (USD, 2 decimal places) and account_balance (the agreement's private-pay balance in USD to 2 decimal places once the credit is posted; negative means a credit balance).
    """
    amt = _Fmt.cents(amount)
    if amt <= 0:
        return "Error: amount must be a positive USD amount"
    if not _Fmt.is_date(from_date) or int(day_count) <= 0:
        return "Error: from_date must be YYYY-MM-DD and day_count a positive whole number of days"
    rid = ctx.make_id("pcc_", private_agreement_id, charge_entry_id, adjustment_reason, from_date, day_count, amt)
    agr = ctx.find("private_agreements", private_agreement_id=private_agreement_id)[0]
    ctx.create("private_ledger", rid, private_entry_id=rid, private_agreement_id=private_agreement_id,
               customer_id=agr["customer_id"], event_type="private_adjustment", charge_entry_id=charge_entry_id,
               adjustment_reason=adjustment_reason, from_date=from_date, day_count=int(day_count), amount=amt,
               entry_date=ctx.now()[:10])
    bal = _Fmt.cents(float(agr.get("account_balance") or 0) - amt)
    ctx.update("private_agreements", private_agreement_id, account_balance=bal)
    return str({"status": "credited", "private_entry_id": rid, "charge_entry_id": charge_entry_id,
                "adjustment_reason": adjustment_reason, "from_date": from_date, "day_count": int(day_count),
                "amount": amt, "account_balance": bal})


@tool(owner="agent", rw="write")
def post_resumed_recharge_e6f5843a(ctx: ToolContext, private_agreement_id: str, service_month: str, from_date: str,
                                   to_date: str, day_count: int, accommodation_tier: str, daily_rate: float,
                                   charge_basis: str, amount: float) -> str:
    """Post one room-and-board span charge on a private-pay admission agreement for days billed privately to a resident whose stay another payer source has stopped covering. One call books one room-and-board charge entry for the given service month, span dates, chargeable days, tier, daily rate and charge basis, and raises the agreement's private-pay balance by the charge amount; the span appears on the resident's statement and ledger as its own charge line.

    Args:
        private_agreement_id: Id class — the reference number of the resident's private-pay admission agreement, as shown by the agreement lookup for the resident.
        service_month: Fixed-format class — the calendar month of service the span belongs to, written YYYY-MM.
        from_date: Fixed-format class — the calendar date of the earliest day of the span, written YYYY-MM-DD.
        to_date: Fixed-format class — the calendar date of the last day of the span, written YYYY-MM-DD.
        day_count: Fixed-format class — the chargeable days of the span, a whole number of integer days.
        accommodation_tier: Enum class — the accommodation tier whose daily rate prices the span, one of: Private Long-Term Care Room (a one-bed long-term care room off the secured unit); Private Secure Memory Care Room (a one-bed room on the secured memory care unit); Semi-Private Long-Term Care Room (a two-bed long-term care room off the secured unit); Semi-Private Secure Memory Care Room (a two-bed room on the secured memory care unit); Private Bariatric Care Room (the one-bed room equipped for bariatric care); Private Suite with Sitting Area (the one-bed suite with a separate sitting area).
        daily_rate: Fixed-format class — the daily rate applied to the span in USD per day, to 2 decimal places.
        charge_basis: Enum class — why the span is priced as it is, one of: standard (an ordinary span at the tier's own rate); first_month_partial (the admission month charged from the admission date); isolation_rate (a span priced at the isolation billing tier's rate while the center itself keeps the resident in the room for infection control); prior_rate_notice_hold (a span priced at the earlier scheduled rate because the written notice of the new rate has not yet run its notice period).
        amount: Fixed-format class — the charge in USD, a positive amount to 2 decimal places, rounded half up to the cent.

    Returns:
        A text rendering of a dictionary with keys: status ("charged" when the entry was booked), private_entry_id (the new ledger reference number), service_month (YYYY-MM), from_date and to_date (YYYY-MM-DD), day_count (integer days), accommodation_tier (official tier name), daily_rate (USD per day, 2 decimal places), charge_basis, amount (USD, 2 decimal places) and account_balance (the agreement's private-pay balance in USD to 2 decimal places once the charge is posted; negative means a credit balance).
    """
    amt = _Fmt.cents(amount)
    if amt <= 0:
        return "Error: amount must be a positive USD amount"
    rate = _Fmt.cents(daily_rate)
    if rate <= 0:
        return "Error: daily_rate must be a positive USD amount"
    if not (_Fmt.is_month(service_month) and _Fmt.is_date(from_date) and _Fmt.is_date(to_date)):
        return "Error: service_month must be YYYY-MM and from_date/to_date YYYY-MM-DD"
    if int(day_count) <= 0:
        return "Error: day_count must be a positive whole number of days"
    rid = ctx.make_id("prr_", private_agreement_id, service_month, from_date, to_date, day_count, accommodation_tier,
                      rate, charge_basis, amt)
    agr = ctx.find("private_agreements", private_agreement_id=private_agreement_id)[0]
    ctx.create("private_ledger", rid, private_entry_id=rid, private_agreement_id=private_agreement_id,
               customer_id=agr["customer_id"], event_type="private_room_board_charge", service_month=service_month,
               from_date=from_date, to_date=to_date, day_count=int(day_count), accommodation_tier=accommodation_tier,
               daily_rate=rate, charge_basis=charge_basis, amount=amt, entry_date=ctx.now()[:10])
    bal = _Fmt.cents(float(agr.get("account_balance") or 0) + amt)
    ctx.update("private_agreements", private_agreement_id, account_balance=bal)
    return str({"status": "charged", "private_entry_id": rid, "service_month": service_month, "from_date": from_date,
                "to_date": to_date, "day_count": int(day_count), "accommodation_tier": accommodation_tier,
                "daily_rate": rate, "charge_basis": charge_basis, "amount": amt, "account_balance": bal})


@tool(owner="user", rw="write")
def pay_resumption_deposit_9c511f79(ctx: ToolContext, private_agreement_id: str, payment_method: str,
                                    amount: float) -> str:
    """Pay money into the refundable security deposit held on the resident's private-pay admission agreement of a resident billed privately again whose stay another payer source covered in part. The resident or the representative makes this payment in person over their own account. One call books one deposit receipt for the amount paid by the chosen method and raises the agreement's security deposit balance by that amount; the receipt shows on the resident's ledger and the new deposit balance is returned.

    Args:
        private_agreement_id: Id class — the reference number of the resident's private-pay admission agreement, as read out by the business office from the agreement lookup.
        payment_method: Enum class — how the payer hands over the money, one of: ach (an electronic transfer from the payer's bank account); card (a debit or credit card); check (a personal check); certified_check (a bank-certified or cashier's check); money_order (a money order); deposit_application (funds already held by the center as a security deposit and moved into this deposit, never new money from the payer).
        amount: Fixed-format class — the deposit paid in USD, a positive amount to 2 decimal places, rounded half up to the cent.

    Returns:
        A text rendering of a dictionary with keys: status ("received" when the receipt was booked), private_entry_id (the deposit receipt's ledger reference number), payment_method, amount (USD, 2 decimal places) and deposit_balance (the agreement's security deposit balance in USD to 2 decimal places once the receipt is booked).
    """
    amt = _Fmt.cents(amount)
    if amt <= 0:
        return "Error: amount must be a positive USD amount"
    rid = ctx.make_id("prd_", private_agreement_id, payment_method, amt)
    agr = ctx.find("private_agreements", private_agreement_id=private_agreement_id)[0]
    ctx.create("private_ledger", rid, private_entry_id=rid, private_agreement_id=private_agreement_id,
               customer_id=agr["customer_id"], event_type="private_deposit_received", payment_method=payment_method,
               amount=amt, entry_date=ctx.now()[:10])
    dep = _Fmt.cents(float(agr.get("deposit_balance") or 0) + amt)
    ctx.update("private_agreements", private_agreement_id, deposit_balance=dep)
    return str({"status": "received", "private_entry_id": rid, "payment_method": payment_method, "amount": amt,
                "deposit_balance": dep})

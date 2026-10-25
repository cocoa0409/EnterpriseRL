"""Hidden task tools for env_0066_captive_auto_finance_company / retail_payment_servicing.

Each tool performs one atomic servicing write on a Kestrel New Vehicle Retail Installment Sale
Contract with the values the caller supplies; none of them judges eligibility or works out an amount.
"""

from erlbench import ToolContext, tool


class _ScheduleDates:
    """Pure calendar arithmetic used by the extension booking (no clock and no external state)."""

    @staticmethod
    def add_months(date_text: str, months: int) -> str:
        if not date_text:
            return ""
        year, month, day = (int(part) for part in str(date_text)[:10].split("-"))
        total = year * 12 + (month - 1) + int(months)
        new_year, new_month = divmod(total, 12)
        new_month += 1
        month_days = [31, 29 if (new_year % 4 == 0 and (new_year % 100 != 0 or new_year % 400 == 0)) else 28,
                      31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
        new_day = min(day, month_days[new_month - 1])
        return f"{new_year:04d}-{new_month:02d}-{new_day:02d}"


class _PostingDay:
    """Posting-day arithmetic for payments: the Central Time cutoff, weekends and US federal holidays
    (pure calendar arithmetic, no clock and no external state)."""

    _OFFSETS = {"EST": -5, "EDT": -4, "CST": -6, "CDT": -5, "MST": -7, "MDT": -6, "PST": -8, "PDT": -7,
                "UTC": 0, "GMT": 0}

    @staticmethod
    def ordinal(y: int, m: int, d: int) -> int:
        y2 = y - 1 if m <= 2 else y
        era = y2 // 400
        yoe = y2 - era * 400
        doy = (153 * (m + (-3 if m > 2 else 9)) + 2) // 5 + d - 1
        doe = yoe * 365 + yoe // 4 - yoe // 100 + doy
        return era * 146097 + doe - 719468

    @staticmethod
    def civil(z: int) -> tuple:
        z = z + 719468
        era = z // 146097
        doe = z - era * 146097
        yoe = (doe - doe // 1460 + doe // 36524 - doe // 146096) // 365
        doy = doe - (365 * yoe + yoe // 4 - yoe // 100)
        mp = (5 * doy + 2) // 153
        d = doy - (153 * mp + 2) // 5 + 1
        m = mp + 3 if mp < 10 else mp - 9
        return (yoe + era * 400 + (1 if m <= 2 else 0), m, d)

    @staticmethod
    def weekday(z: int) -> int:
        return (z + 3) % 7          # 0 = Monday ... 6 = Sunday

    @staticmethod
    def nth_weekday(y: int, m: int, wd: int, n: int) -> int:
        first = _PostingDay.ordinal(y, m, 1)
        return first + (wd - _PostingDay.weekday(first)) % 7 + 7 * (n - 1)

    @staticmethod
    def last_weekday(y: int, m: int, wd: int) -> int:
        nxt = _PostingDay.ordinal(y + (1 if m == 12 else 0), 1 if m == 12 else m + 1, 1)
        last = nxt - 1
        return last - (_PostingDay.weekday(last) - wd) % 7

    @staticmethod
    def holidays(y: int) -> set:
        out = set()
        for (m, d) in [(1, 1), (6, 19), (7, 4), (11, 11), (12, 25)]:
            z = _PostingDay.ordinal(y, m, d)
            wd = _PostingDay.weekday(z)
            out.add(z - 1 if wd == 5 else (z + 1 if wd == 6 else z))
        out.add(_PostingDay.nth_weekday(y, 1, 0, 3))   # Martin Luther King Jr. Day
        out.add(_PostingDay.nth_weekday(y, 2, 0, 3))   # Washington's Birthday
        out.add(_PostingDay.last_weekday(y, 5, 0))     # Memorial Day
        out.add(_PostingDay.nth_weekday(y, 9, 0, 1))   # Labor Day
        out.add(_PostingDay.nth_weekday(y, 10, 0, 2))  # Columbus Day
        out.add(_PostingDay.nth_weekday(y, 11, 3, 4))  # Thanksgiving Day
        return out

    @staticmethod
    def business(z: int) -> bool:
        y = _PostingDay.civil(z)[0]
        hol = _PostingDay.holidays(y) | _PostingDay.holidays(y + 1)
        return _PostingDay.weekday(z) < 5 and z not in hol

    @staticmethod
    def posting_date(stamp: str) -> str:
        parts = str(stamp).split()
        y, m, d = (int(p) for p in parts[0].split("-"))
        hh, mm = (int(p) for p in parts[1].split(":")[:2])
        zone = parts[2] if len(parts) > 2 else "CDT"
        local = _PostingDay._OFFSETS.get(zone, -5)
        central = -5 if zone.endswith("DT") else -6
        minutes = hh * 60 + mm + (central - local) * 60
        z = _PostingDay.ordinal(y, m, d) + minutes // 1440
        minutes = minutes % 1440
        if minutes >= 20 * 60 or not _PostingDay.business(z):
            z += 1
            while not _PostingDay.business(z):
                z += 1
        yy, mo, dd = _PostingDay.civil(z)
        return f"{yy:04d}-{mo:02d}-{dd:02d}"


@tool(owner="agent", rw="write")
def grant_retail_extension_6a93006b(ctx: ToolContext, retail_contract_id: str, customer_id: str,
                                    retail_request_id: str, installment_due_date: str,
                                    installments_deferred: int, good_faith_amount: float,
                                    extension_fee: float) -> str:
    """Grant a payment extension on a customer's Kestrel new-vehicle retail installment contract and book
    its extension fee. One call records one extension: the named installment and as many following ones as
    are deferred move to the end of the term, the contract's next due date and maturity date each move one
    calendar month later per deferred installment (a day that does not exist in the target month falls back
    to that month's last day), the count of installments deferred over the life of the contract rises by the
    number deferred, the latest extension date becomes today, and the extension fee is added to the fees due
    on the contract. The customer can see the new next due date and maturity date on the account at once.

    Args:
        retail_contract_id: Id class — the reference number of the retail installment contract being extended, as returned by the retail contract lookup.
        customer_id: Id class — the reference number of the customer who holds the contract, as returned by the customer profile lookup.
        retail_request_id: Id class — the reference number of the customer's completed signed extension agreement for this contract, as returned by the signature request lookup.
        installment_due_date: Fixed-format class — the due date of the earliest installment being deferred, written YYYY-MM-DD as a calendar date with no time zone; never empty.
        installments_deferred: Fixed-format class — the number of installments being deferred, a non-negative integer.
        good_faith_amount: Fixed-format class — the good-faith payment received from the customer for this extension, in USD with 2 decimal places, rounded to the cent; 0.00 when none was received.
        extension_fee: Fixed-format class — the extension fee booked to fees due, in USD with 2 decimal places, rounded to the cent; 0.00 when no fee is charged.

    Returns:
        A confirmation sentence naming the extension reference (an opaque text identifier of the booked
        extension), the contract reference, the number of installments deferred, the new next due date and
        the new maturity date (both YYYY-MM-DD) and the extension fee booked in USD with 2 decimal places. A
        sentence that starts with "Extension granted" means the extension is in effect on the contract.
    """
    rows = ctx.find("retail_contracts", retail_contract_id=retail_contract_id)
    contract = rows[0] if rows else {}
    count = int(installments_deferred)
    fee = round(float(extension_fee), 2)
    good_faith = round(float(good_faith_amount), 2)
    new_maturity = _ScheduleDates.add_months(contract.get("maturity_date", ""), count)
    new_next_due = _ScheduleDates.add_months(installment_due_date, count)
    rid = ctx.make_id("rext_", retail_contract_id, customer_id, retail_request_id, installment_due_date,
                      count, good_faith, fee)
    today = ctx.now()[:10]
    ctx.create("retail_transactions", rid, retail_txn_id=rid, retail_contract_id=retail_contract_id,
               customer_id=customer_id, event_type="retail_extension", txn_date=today, amount=fee,
               installments_deferred=count, installment_due_date=installment_due_date,
               new_maturity_date=new_maturity, good_faith_amount=good_faith, fee_type="extension_fee")
    ctx.update("retail_contracts", retail_contract_id, next_due_date=new_next_due, maturity_date=new_maturity,
               extensions_used_lifetime=int(contract.get("extensions_used_lifetime") or 0) + count,
               last_extension_date=today,
               fees_due_balance=round(float(contract.get("fees_due_balance") or 0) + fee, 2))
    return (f"Extension granted: reference {rid} on contract {retail_contract_id}; {count} installment(s) "
            f"deferred; next due date {new_next_due}; maturity date {new_maturity}; extension fee {fee:.2f} USD.")


@tool(owner="user", rw="write")
def submit_extension_good_faith_payment_c7575c9b(ctx: ToolContext, retail_contract_id: str,
                                                 payment_amount: float, funding_account_last4: str) -> str:
    """The customer makes, in person on Kestrel's automated payment line, the good-faith payment for an
    extension of their own retail installment contract, drawn by ACH from their own bank account. One call
    posts one installment payment to the contract through the automated phone line with no channel fee,
    on its posting day, which is today when the payment is received earlier than 8:00 p.m. Central Time on a business
    day and otherwise the next business day (Saturdays, Sundays and US federal holidays, with a holiday that
    falls on a weekend observed on the nearest weekday, are not business days), recording its amount, channel and purpose, and the contract's last payment date becomes the
    posting day; the
    split of the payment across interest, principal and fees is applied by the nightly posting cycle, not by
    this call. The customer hears the payment confirmation
    number and the amount posted.

    Args:
        retail_contract_id: Id class — the reference number of the customer's retail installment contract, which the agent reads from the retail contract lookup and gives to the customer.
        payment_amount: Fixed-format class — the payment amount drawn from the customer's bank account, in USD with 2 decimal places, rounded to the cent.
        funding_account_last4: Fixed-format class — the last four digits of the customer's own bank account the payment is drawn from, written as 4 digits, or empty when not applicable.

    Returns:
        A confirmation sentence naming the payment confirmation number (an opaque text identifier), the
        contract reference, the amount posted in USD with 2 decimal places and the posting day
        (YYYY-MM-DD). A sentence that starts with "Payment posted" means the payment is on the contract.
    """
    rows = ctx.find("retail_contracts", retail_contract_id=retail_contract_id)
    contract = rows[0] if rows else {}
    amount = round(float(payment_amount), 2)
    rid = ctx.make_id("rgfp_", retail_contract_id, amount, funding_account_last4)
    today = _PostingDay.posting_date(ctx.now())
    ctx.create("retail_transactions", rid, retail_txn_id=rid, retail_contract_id=retail_contract_id,
               customer_id=contract.get("customer_id", ""), event_type="retail_payment", txn_date=today,
               amount=amount, payment_channel="phone_ivr_ach", funding_account_last4=funding_account_last4,
               payment_purpose="installment", convenience_fee=0.0, return_reason="not_applicable",
               fee_type="not_applicable")
    ctx.update("retail_contracts", retail_contract_id, last_payment_date=today)
    return (f"Payment posted: confirmation {rid} on contract {retail_contract_id}; amount {amount:.2f} USD; "
            f"posting date {today}.")


@tool(owner="agent", rw="write")
def post_arrears_payment_6321a7ae(ctx: ToolContext, retail_contract_id: str, payment_amount: float,
                                  funding_account_last4: str) -> str:
    """Post an arrears payment that a Kestrel agent takes by phone, with the customer's authorization, from
    the customer's bank account on the past-due installments of a retail installment contract. One call
    posts one installment payment to the contract through the agent-assisted ACH channel with no channel
    fee, on its posting day, which is today when the payment is received earlier than 8:00 p.m. Central Time on a business
    day and otherwise the next business day (Saturdays, Sundays and US federal holidays, with a holiday that
    falls on a weekend observed on the nearest weekday, are not business days), recording its amount, channel and purpose, and the contract's last payment date becomes
    the posting day; the split of the payment across interest, principal and fees is applied by the nightly posting
    cycle, not by this call. The customer can be told the payment
    confirmation number and the amount posted.

    Args:
        retail_contract_id: Id class — the reference number of the retail installment contract the payment posts to, as returned by the retail contract lookup.
        payment_amount: Fixed-format class — the payment amount drawn from the customer's bank account, in USD with 2 decimal places, rounded to the cent.
        funding_account_last4: Fixed-format class — the last four digits of the bank account the customer authorizes the payment from, written as 4 digits, or empty when not applicable.

    Returns:
        A confirmation sentence naming the payment confirmation number (an opaque text identifier), the
        contract reference, the amount posted in USD with 2 decimal places and the posting day
        (YYYY-MM-DD). A sentence that starts with "Payment posted" means the payment is on the contract.
    """
    rows = ctx.find("retail_contracts", retail_contract_id=retail_contract_id)
    contract = rows[0] if rows else {}
    amount = round(float(payment_amount), 2)
    rid = ctx.make_id("rarp_", retail_contract_id, amount, funding_account_last4)
    today = _PostingDay.posting_date(ctx.now())
    ctx.create("retail_transactions", rid, retail_txn_id=rid, retail_contract_id=retail_contract_id,
               customer_id=contract.get("customer_id", ""), event_type="retail_payment", txn_date=today,
               amount=amount, payment_channel="phone_agent_ach", funding_account_last4=funding_account_last4,
               payment_purpose="installment", convenience_fee=0.0, return_reason="not_applicable",
               fee_type="not_applicable")
    ctx.update("retail_contracts", retail_contract_id, last_payment_date=today)
    return (f"Payment posted: confirmation {rid} on contract {retail_contract_id}; amount {amount:.2f} USD; "
            f"posting date {today}.")


@tool(owner="user", rw="write")
def submit_catch_up_payment_af77047e(ctx: ToolContext, retail_contract_id: str, payment_amount: float,
                                     funding_account_last4: str) -> str:
    """The customer makes, in person on Kestrel's automated payment line, a catch-up payment on their own
    past-due retail installment contract, drawn by ACH from their own bank account. One call posts one
    installment payment to the contract through the automated phone line with no channel fee,
    on its posting day, which is today when the payment is received earlier than 8:00 p.m. Central Time on a business
    day and otherwise the next business day (Saturdays, Sundays and US federal holidays, with a holiday that
    falls on a weekend observed on the nearest weekday, are not business days), recording its amount, channel and purpose, and the contract's last payment date becomes the
    posting day; the split
    of the payment across interest, principal and fees is applied by the nightly posting cycle, not by this
    call. The customer hears the payment confirmation number and the
    amount posted.

    Args:
        retail_contract_id: Id class — the reference number of the customer's retail installment contract, which the agent reads from the retail contract lookup and gives to the customer.
        payment_amount: Fixed-format class — the payment amount drawn from the customer's bank account, in USD with 2 decimal places, rounded to the cent.
        funding_account_last4: Fixed-format class — the last four digits of the customer's own bank account the payment is drawn from, written as 4 digits, or empty when not applicable.

    Returns:
        A confirmation sentence naming the payment confirmation number (an opaque text identifier), the
        contract reference, the amount posted in USD with 2 decimal places and the posting day
        (YYYY-MM-DD). A sentence that starts with "Payment posted" means the payment is on the contract.
    """
    rows = ctx.find("retail_contracts", retail_contract_id=retail_contract_id)
    contract = rows[0] if rows else {}
    amount = round(float(payment_amount), 2)
    rid = ctx.make_id("rcup_", retail_contract_id, amount, funding_account_last4)
    today = _PostingDay.posting_date(ctx.now())
    ctx.create("retail_transactions", rid, retail_txn_id=rid, retail_contract_id=retail_contract_id,
               customer_id=contract.get("customer_id", ""), event_type="retail_payment", txn_date=today,
               amount=amount, payment_channel="phone_ivr_ach", funding_account_last4=funding_account_last4,
               payment_purpose="installment", convenience_fee=0.0, return_reason="not_applicable",
               fee_type="not_applicable")
    ctx.update("retail_contracts", retail_contract_id, last_payment_date=today)
    return (f"Payment posted: confirmation {rid} on contract {retail_contract_id}; amount {amount:.2f} USD; "
            f"posting date {today}.")


@tool(owner="agent", rw="write")
def assess_returned_installment_late_charge_34170c70(ctx: ToolContext, retail_contract_id: str, installment_due_date: str,
                                                     late_charge_amount: float) -> str:
    """Assess the late charge on an installment of a Kestrel new-vehicle retail installment contract that a
    returned payment has re-opened, the payment that had paid it having been dishonoured and reversed. One
    call books one late charge dated today against the named installment due date and adds it to the fees
    due on the contract; the customer can see the charge and the new fees-due balance on the account.

    Args:
        retail_contract_id: Id class — the reference number of the retail installment contract the late charge is assessed on, as returned by the retail contract lookup.
        installment_due_date: Fixed-format class — the due date of the installment the late charge relates to, written YYYY-MM-DD as a calendar date with no time zone; never empty.
        late_charge_amount: Fixed-format class — the late charge assessed, in USD with 2 decimal places, rounded to the cent.

    Returns:
        A confirmation sentence naming the late charge reference (an opaque text identifier), the contract
        reference, the installment due date (YYYY-MM-DD), the late charge in USD with 2 decimal places and
        the new fees-due balance in USD with 2 decimal places. A sentence that starts with "Late charge
        assessed" means the charge is on the contract.
    """
    rows = ctx.find("retail_contracts", retail_contract_id=retail_contract_id)
    contract = rows[0] if rows else {}
    amount = round(float(late_charge_amount), 2)
    rid = ctx.make_id("rlrp_", retail_contract_id, installment_due_date, amount)
    new_fees = round(float(contract.get("fees_due_balance") or 0) + amount, 2)
    ctx.create("retail_transactions", rid, retail_txn_id=rid, retail_contract_id=retail_contract_id,
               customer_id=contract.get("customer_id", ""), event_type="retail_late_charge",
               txn_date=ctx.now()[:10], amount=amount, installment_due_date=installment_due_date,
               fee_type="late_charge", payment_channel="not_applicable", payment_purpose="not_applicable",
               return_reason="not_applicable")
    ctx.update("retail_contracts", retail_contract_id, fees_due_balance=new_fees)
    return (f"Late charge assessed: reference {rid} on contract {retail_contract_id}; installment due "
            f"{installment_due_date}; late charge {amount:.2f} USD; fees due now {new_fees:.2f} USD.")


@tool(owner="agent", rw="write")
def assess_unpaid_installment_late_charge_51bb28dc(ctx: ToolContext, retail_contract_id: str, installment_due_date: str,
                                                   late_charge_amount: float) -> str:
    """Assess the late charge on an installment of a Kestrel new-vehicle retail installment contract that is
    still wholly or partly unpaid once its grace period has run out. One call books one late charge dated
    today against the named installment due date and adds it to the fees due on the contract; the customer
    can see the charge and the new fees-due balance on the account.

    Args:
        retail_contract_id: Id class — the reference number of the retail installment contract the late charge is assessed on, as returned by the retail contract lookup.
        installment_due_date: Fixed-format class — the due date of the installment the late charge relates to, written YYYY-MM-DD as a calendar date with no time zone; never empty.
        late_charge_amount: Fixed-format class — the late charge assessed, in USD with 2 decimal places, rounded to the cent.

    Returns:
        A confirmation sentence naming the late charge reference (an opaque text identifier), the contract
        reference, the installment due date (YYYY-MM-DD), the late charge in USD with 2 decimal places and
        the new fees-due balance in USD with 2 decimal places. A sentence that starts with "Late charge
        assessed" means the charge is on the contract.
    """
    rows = ctx.find("retail_contracts", retail_contract_id=retail_contract_id)
    contract = rows[0] if rows else {}
    amount = round(float(late_charge_amount), 2)
    rid = ctx.make_id("rlcu_", retail_contract_id, installment_due_date, amount)
    new_fees = round(float(contract.get("fees_due_balance") or 0) + amount, 2)
    ctx.create("retail_transactions", rid, retail_txn_id=rid, retail_contract_id=retail_contract_id,
               customer_id=contract.get("customer_id", ""), event_type="retail_late_charge",
               txn_date=ctx.now()[:10], amount=amount, installment_due_date=installment_due_date,
               fee_type="late_charge", payment_channel="not_applicable", payment_purpose="not_applicable",
               return_reason="not_applicable")
    ctx.update("retail_contracts", retail_contract_id, fees_due_balance=new_fees)
    return (f"Late charge assessed: reference {rid} on contract {retail_contract_id}; installment due "
            f"{installment_due_date}; late charge {amount:.2f} USD; fees due now {new_fees:.2f} USD.")


@tool(owner="agent", rw="write")
def assess_late_posted_installment_late_charge_04190f4f(ctx: ToolContext, retail_contract_id: str, installment_due_date: str,
                                                        late_charge_amount: float) -> str:
    """Assess the late charge on an installment of a Kestrel new-vehicle retail installment contract whose
    payment posted once its grace period had already run out and for which no late charge stands. One call
    books one late charge dated today against the named installment due date and adds it to the fees due on
    the contract; the customer can see the charge and the new fees-due balance on the account.

    Args:
        retail_contract_id: Id class — the reference number of the retail installment contract the late charge is assessed on, as returned by the retail contract lookup.
        installment_due_date: Fixed-format class — the due date of the installment the late charge relates to, written YYYY-MM-DD as a calendar date with no time zone; never empty.
        late_charge_amount: Fixed-format class — the late charge assessed, in USD with 2 decimal places, rounded to the cent.

    Returns:
        A confirmation sentence naming the late charge reference (an opaque text identifier), the contract
        reference, the installment due date (YYYY-MM-DD), the late charge in USD with 2 decimal places and
        the new fees-due balance in USD with 2 decimal places. A sentence that starts with "Late charge
        assessed" means the charge is on the contract.
    """
    rows = ctx.find("retail_contracts", retail_contract_id=retail_contract_id)
    contract = rows[0] if rows else {}
    amount = round(float(late_charge_amount), 2)
    rid = ctx.make_id("rlcp_", retail_contract_id, installment_due_date, amount)
    new_fees = round(float(contract.get("fees_due_balance") or 0) + amount, 2)
    ctx.create("retail_transactions", rid, retail_txn_id=rid, retail_contract_id=retail_contract_id,
               customer_id=contract.get("customer_id", ""), event_type="retail_late_charge",
               txn_date=ctx.now()[:10], amount=amount, installment_due_date=installment_due_date,
               fee_type="late_charge", payment_channel="not_applicable", payment_purpose="not_applicable",
               return_reason="not_applicable")
    ctx.update("retail_contracts", retail_contract_id, fees_due_balance=new_fees)
    return (f"Late charge assessed: reference {rid} on contract {retail_contract_id}; installment due "
            f"{installment_due_date}; late charge {amount:.2f} USD; fees due now {new_fees:.2f} USD.")

"""Hidden task tools of the sender_verification_and_limits difficulty (Personal Sender Account).

Each tool performs one atomic write on the Personal Sender Account records. Every value the
policy computes (a number of Paloma business days, a number of calendar months) is passed in by
the caller; the tools only land the corresponding date on Paloma's calendar, never a policy
judgement. They are reached through unlock_* -> call_* and named only by the extended policies.
"""

from erlbench import ToolContext, tool


class _PalomaCalendar:
    """Paloma's operations calendar: civil-date arithmetic and Paloma business days
    (Monday to Friday, excluding US Federal Reserve holidays). Pure arithmetic on
    YYYY-MM-DD strings; no clock is read here."""

    FED_HOLIDAYS = {
        "2026-01-01", "2026-01-19", "2026-02-16", "2026-05-25", "2026-06-19", "2026-09-07",
        "2026-10-12", "2026-11-11", "2026-11-26", "2026-12-25",
        "2027-01-01", "2027-01-18", "2027-02-15", "2027-05-31", "2027-07-05", "2027-09-06",
        "2027-10-11", "2027-11-11", "2027-11-25",
    }

    @staticmethod
    def to_days(date_text):
        y, m, d = (int(part) for part in str(date_text)[:10].split("-"))
        y -= 1 if m <= 2 else 0
        era = (y if y >= 0 else y - 399) // 400
        yoe = y - era * 400
        doy = (153 * (m + (-3 if m > 2 else 9)) + 2) // 5 + d - 1
        doe = yoe * 365 + yoe // 4 - yoe // 100 + doy
        return era * 146097 + doe - 719468

    @staticmethod
    def from_days(z):
        z += 719468
        era = (z if z >= 0 else z - 146096) // 146097
        doe = z - era * 146097
        yoe = (doe - doe // 1460 + doe // 36524 - doe // 146096) // 365
        y = yoe + era * 400
        doy = doe - (365 * yoe + yoe // 4 - yoe // 100)
        mp = (5 * doy + 2) // 153
        d = doy - (153 * mp + 2) // 5 + 1
        m = mp + (3 if mp < 10 else -9)
        y += 1 if m <= 2 else 0
        return f"{y:04d}-{m:02d}-{d:02d}"

    @classmethod
    def add_business_days(cls, start, count):
        z = cls.to_days(start)
        remaining = int(count)
        while remaining > 0:
            z += 1
            if (z + 3) % 7 < 5 and cls.from_days(z) not in cls.FED_HOLIDAYS:
                remaining -= 1
        return cls.from_days(z)

    @staticmethod
    def add_months(start, months):
        y, m, d = (int(part) for part in str(start)[:10].split("-"))
        total = y * 12 + (m - 1) + int(months)
        ny, nm = total // 12, total % 12 + 1
        month_days = [31, 29 if (ny % 4 == 0 and (ny % 100 != 0 or ny % 400 == 0)) else 28,
                      31, 30, 31, 30, 31, 31, 30, 31, 30, 31][nm - 1]
        return f"{ny:04d}-{nm:02d}-{min(d, month_days):02d}"


@tool(owner="user", rw="write")
def lodge_limit_review_54a88584(ctx: ToolContext, sender_account_id: str, requested_level: str,
                                decision_window_business_days: int) -> str:
    """Lodge the account holder's own request asking Paloma compliance to review their Personal
    Sender Account for a higher, review-gated verification level; the customer runs it in their own
    app session.

    One call records one new limit review request on the account history, dated today, naming the
    level requested and carrying the decision due date Paloma compliance commits to: the date
    reached by counting the given number of Paloma business days (Monday to Friday, excluding US
    Federal Reserve holidays) forward from today, today itself not counted. The request is recorded
    as lodged through the app and stays undecided while compliance has recorded no decision on it; no limit,
    level, document or transfer changes on this call. The customer sees the request, its reference
    number and its decision due date in the app.

    Args:
        sender_account_id: Id class — the Personal Sender Account reference number of the account
            the review is for, as returned by the Personal Sender Account lookup for this customer.
        requested_level: Enum class — the official name of the verification level the review asks
            for, exactly one of: Paloma Enhanced — the request asks compliance for the Enhanced level
            (level 4); Paloma Premier — the request asks for the Premier level (level 5); Paloma
            Private Client — the request asks for the Private Client level (level 6); Paloma Starter
            — names the entry level, which is held without any compliance review; Paloma Verified —
            names level 2, which is reached without a compliance review; Paloma Verified Plus — names
            level 3, which is reached without a compliance review; none — the marker the account
            history carries on entries that are not limit review requests, naming no level at all.
        decision_window_business_days: Fixed-format class — the decision window as a whole number of
            Paloma business days, an integer of 1 or more with no fractional part (the tool applies
            no rounding); the decision due date recorded is the date, in YYYY-MM-DD form on Paloma's
            operations calendar (US Central Time), reached by counting this many Paloma business days
            forward from today's date, today not counted.

    Returns:
        A text rendering of a dictionary with these fields: account_event_id (string, the reference
        number of the new limit review request), requested_level (string, the level named in the
        request), request_date (string, YYYY-MM-DD, today's date), decision_due_date (string,
        YYYY-MM-DD, the date by which compliance must decide), status (string, "lodged" when the
        request was recorded). A receipt with status "lodged" and an account_event_id means the
        undecided request now stands on the account history.
    """
    today = ctx.now()[:10]
    due = _PalomaCalendar.add_business_days(today, decision_window_business_days)
    accounts = ctx.find("sender_accounts", sender_account_id=sender_account_id)
    customer_id = accounts[0].get("customer_id", "") if accounts else ""
    rid = ctx.make_id("lrr_", sender_account_id, requested_level, decision_window_business_days)
    ctx.create("sender_account_events", rid, account_event_id=rid, sender_account_id=sender_account_id,
               customer_id=customer_id, event_type="account_limit_review_requested", event_date=today,
               requested_level=requested_level, decision_due_date=due, review_outcome="none",
               related_event_id="", rfi_topic="none", rfi_due_date="", recipient_id="", corridor="none",
               callback_topic="none", callback_due_date="", statement_period_start="",
               statement_period_end="", delivery_due_date="", channel="app")
    return str({"account_event_id": rid, "requested_level": requested_level, "request_date": today,
                "decision_due_date": due, "status": "lodged"})


@tool(owner="agent", rw="write")
def schedule_limits_callback_7588c2a7(ctx: ToolContext, sender_account_id: str,
                                      callback_window_business_days: int) -> str:
    """Book a callback from Paloma's limits and levels specialists to the holder of a Personal
    Sender Account, requested by the customer on this phone call.

    One call records one scheduled callback on the account history, dated today, on the topic
    limits and levels, with the callback due date: the date reached by counting the given number of
    Paloma business days (Monday to Friday, excluding US Federal Reserve holidays) forward from
    today, today itself not counted. The callback is recorded as requested by phone. Nothing else on
    the account, its level, its limits or its transfers changes. The customer can be told the
    callback reference number and the last business day by which the specialist will call.

    Args:
        sender_account_id: Id class — the Personal Sender Account reference number of the customer
            to be called back, as returned by the Personal Sender Account lookup for this customer.
        callback_window_business_days: Fixed-format class — the callback window as a whole number of
            Paloma business days, an integer of 1 or more with no fractional part (the tool applies
            no rounding); the callback due date recorded is the date, in YYYY-MM-DD form on Paloma's
            operations calendar (US Central Time), reached by counting this many Paloma business days
            forward from today's date, today not counted.

    Returns:
        A text rendering of a dictionary with these fields: account_event_id (string, the reference
        number of the scheduled callback), callback_topic (string, always "limits_and_levels"),
        request_date (string, YYYY-MM-DD, today's date), callback_due_date (string, YYYY-MM-DD, the
        last business day for the callback), status (string, "scheduled" when the callback was
        recorded). A receipt with status "scheduled" and an account_event_id means the callback now
        stands on the account history.
    """
    today = ctx.now()[:10]
    due = _PalomaCalendar.add_business_days(today, callback_window_business_days)
    accounts = ctx.find("sender_accounts", sender_account_id=sender_account_id)
    customer_id = accounts[0].get("customer_id", "") if accounts else ""
    rid = ctx.make_id("cbl_", sender_account_id, callback_window_business_days)
    ctx.create("sender_account_events", rid, account_event_id=rid, sender_account_id=sender_account_id,
               customer_id=customer_id, event_type="account_callback_scheduled", event_date=today,
               requested_level="none", decision_due_date="", review_outcome="none", related_event_id="",
               rfi_topic="none", rfi_due_date="", recipient_id="", corridor="none",
               callback_topic="limits_and_levels", callback_due_date=due, statement_period_start="",
               statement_period_end="", delivery_due_date="", channel="phone")
    return str({"account_event_id": rid, "callback_topic": "limits_and_levels", "request_date": today,
                "callback_due_date": due, "status": "scheduled"})


@tool(owner="agent", rw="write")
def apply_level_upgrade_725c1de1(ctx: ToolContext, sender_account_id: str, new_level: str,
                                 review_interval_months: int) -> str:
    """Move a customer's Personal Sender Account up to a higher verification level applied by the
    agent, and set the date its next periodic identity (KYC) review falls due.

    One call changes the account's verification level to the level named, records today as the date
    the new level took effect (its sending limits, funding methods and service entitlements apply to
    transfers booked from today), and sets the next periodic review due date to the date that many
    whole calendar months from today, on the same day of the month or on the last day of a shorter
    month. The account status, its documents and every transfer already booked stay as they are. The
    customer sees the new level and its limits in the app.

    Args:
        sender_account_id: Id class — the Personal Sender Account reference number of the account
            being moved up, as returned by the Personal Sender Account lookup for this customer.
        new_level: Enum class — the official name of the level the account moves to, exactly one of:
            Paloma Starter — the entry level (level 1), held from opening without documents; Paloma
            Verified — level 2, held with an accepted photo ID and selfie; Paloma Verified Plus —
            level 3, held with the further SSN or ITIN, address, occupation documents, account age
            and completed transfers it requires; Paloma Enhanced — level 4, granted only by an
            approved compliance limit review; Paloma Premier — level 5, granted only by an approved
            compliance limit review; Paloma Private Client — level 6, granted only by an approved
            compliance limit review.
        review_interval_months: Fixed-format class — the number of whole calendar months from today
            to the next periodic review, an integer of 1 or more with no fractional part (the tool
            applies no rounding); the next review due date recorded is in YYYY-MM-DD form on Paloma's
            operations calendar (US Central Time), the same day of the month that many months on, or
            the last day of that month when it is shorter.

    Returns:
        A text rendering of a dictionary with these fields: sender_account_id (string, the account
        moved up), level (string, the official name of the level now held), level_effective_date
        (string, YYYY-MM-DD, today's date), next_review_due_date (string, YYYY-MM-DD, the date the
        next periodic review falls due), status (string, "upgraded" when the change was recorded). A
        receipt with status "upgraded" means the account now holds the level named.
    """
    today = ctx.now()[:10]
    next_review = _PalomaCalendar.add_months(today, review_interval_months)
    ctx.update("sender_accounts", sender_account_id, variant_name=new_level, level_effective_date=today,
               next_review_due_date=next_review)
    return str({"sender_account_id": sender_account_id, "level": new_level, "level_effective_date": today,
                "next_review_due_date": next_review, "status": "upgraded"})


@tool(owner="user", rw="write")
def request_account_statement_ee1d8031(ctx: ToolContext, sender_account_id: str, statement_period_start: str,
                                       statement_period_end: str, delivery_window_business_days: int) -> str:
    """Request an account statement of the customer's personal transfer history for a period the
    customer chooses; the account holder runs it in their own app session.

    One call records one statement request on the account history, dated today, covering the period
    from the opening day to the closing day given, with the delivery due date by which the statement
    is emailed to the address on the customer profile: the date reached by counting the given number
    of Paloma business days (Monday to Friday, excluding US Federal Reserve holidays) forward from
    today, today itself not counted. The request is recorded as made through the app; statements are
    free of charge and nothing else on the account changes. The customer sees the request, its
    reference number and its delivery due date in the app.

    Args:
        sender_account_id: Id class — the Personal Sender Account reference number of the account
            whose history the statement covers, as returned by the Personal Sender Account lookup for
            this customer.
        statement_period_start: Fixed-format class — the opening day of the period the statement
            covers, the date the customer chooses, written as a calendar date in YYYY-MM-DD form, no
            time part.
        statement_period_end: Fixed-format class — the closing day of the period the statement covers,
            the date the customer chooses, written as a calendar date in YYYY-MM-DD form, no time
            part.
        delivery_window_business_days: Fixed-format class — the delivery window as a whole number of
            Paloma business days, an integer of 1 or more with no fractional part (the tool applies no
            rounding); the delivery due date recorded is the date, in YYYY-MM-DD form on Paloma's
            operations calendar (US Central Time), reached by counting this many Paloma business days
            forward from today's date, today not counted.

    Returns:
        A text rendering of a dictionary with these fields: account_event_id (string, the reference
        number of the statement request), statement_period_start (string, YYYY-MM-DD),
        statement_period_end (string, YYYY-MM-DD), request_date (string, YYYY-MM-DD, today's date),
        delivery_due_date (string, YYYY-MM-DD, the business day by which the statement is emailed),
        status (string, "requested" when the request was recorded). A receipt with status "requested"
        and an account_event_id means the statement request now stands on the account history.
    """
    today = ctx.now()[:10]
    due = _PalomaCalendar.add_business_days(today, delivery_window_business_days)
    accounts = ctx.find("sender_accounts", sender_account_id=sender_account_id)
    customer_id = accounts[0].get("customer_id", "") if accounts else ""
    rid = ctx.make_id("stm_", sender_account_id, statement_period_start, statement_period_end,
                      delivery_window_business_days)
    ctx.create("sender_account_events", rid, account_event_id=rid, sender_account_id=sender_account_id,
               customer_id=customer_id, event_type="account_statement_requested", event_date=today,
               requested_level="none", decision_due_date="", review_outcome="none", related_event_id="",
               rfi_topic="none", rfi_due_date="", recipient_id="", corridor="none", callback_topic="none",
               callback_due_date="", statement_period_start=statement_period_start,
               statement_period_end=statement_period_end, delivery_due_date=due, channel="app")
    return str({"account_event_id": rid, "statement_period_start": statement_period_start,
                "statement_period_end": statement_period_end, "request_date": today,
                "delivery_due_date": due, "status": "requested"})


@tool(owner="agent", rw="write")
def schedule_fees_callback_4571f432(ctx: ToolContext, sender_account_id: str,
                                    callback_window_business_days: int) -> str:
    """Book a callback from Paloma's refunds and fees specialists to the holder of a Personal Sender
    Account, requested by the customer on this phone call, to go through the fees and refunds on
    their transfers.

    One call records one scheduled callback on the account history, dated today, on the topic
    refunds and fees, with the callback due date: the date reached by counting the given number of
    Paloma business days (Monday to Friday, excluding US Federal Reserve holidays) forward from
    today, today itself not counted. The callback is recorded as requested by phone. Nothing else on
    the account, its level, its limits or its transfers changes. The customer can be told the
    callback reference number and the last business day by which the specialist will call.

    Args:
        sender_account_id: Id class — the Personal Sender Account reference number of the customer
            to be called back, as returned by the Personal Sender Account lookup for this customer.
        callback_window_business_days: Fixed-format class — the callback window as a whole number of
            Paloma business days, an integer of 1 or more with no fractional part (the tool applies
            no rounding); the callback due date recorded is the date, in YYYY-MM-DD form on Paloma's
            operations calendar (US Central Time), reached by counting this many Paloma business days
            forward from today's date, today not counted.

    Returns:
        A text rendering of a dictionary with these fields: account_event_id (string, the reference
        number of the scheduled callback), callback_topic (string, always "refunds_and_fees"),
        request_date (string, YYYY-MM-DD, today's date), callback_due_date (string, YYYY-MM-DD, the
        last business day for the callback), status (string, "scheduled" when the callback was
        recorded). A receipt with status "scheduled" and an account_event_id means the callback now
        stands on the account history.
    """
    today = ctx.now()[:10]
    due = _PalomaCalendar.add_business_days(today, callback_window_business_days)
    accounts = ctx.find("sender_accounts", sender_account_id=sender_account_id)
    customer_id = accounts[0].get("customer_id", "") if accounts else ""
    rid = ctx.make_id("cbf_", sender_account_id, callback_window_business_days)
    ctx.create("sender_account_events", rid, account_event_id=rid, sender_account_id=sender_account_id,
               customer_id=customer_id, event_type="account_callback_scheduled", event_date=today,
               requested_level="none", decision_due_date="", review_outcome="none", related_event_id="",
               rfi_topic="none", rfi_due_date="", recipient_id="", corridor="none",
               callback_topic="refunds_and_fees", callback_due_date=due, statement_period_start="",
               statement_period_end="", delivery_due_date="", channel="phone")
    return str({"account_event_id": rid, "callback_topic": "refunds_and_fees", "request_date": today,
                "callback_due_date": due, "status": "scheduled"})

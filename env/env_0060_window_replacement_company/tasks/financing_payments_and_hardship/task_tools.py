"""Hidden task tools for the financing_payments_and_hardship difficulty of env_0060
(Ridgeline Home Improvement Financing). Output of erl-task-instantiate.

Each tool performs one atomic write on a financing account or its records. The tools never
judge eligibility, never aggregate history and never compute an amount: every figure is
worked out by the agent from the published policy and passed in as a parameter.
"""

from erlbench import ToolContext, tool


@tool(owner="agent", rw="write")
def post_finance_late_fee_832dc831(ctx: ToolContext, finance_account_id: str, statement_period: str,
                                   amount: float) -> str:
    """Post a late fee to a Ridgeline Home Improvement Financing account for one statement period.
    The fee is booked on the account as a new late-fee charge dated the day it is posted and naming
    the statement period it belongs to; it raises the amount owed on the account by the fee and shows
    on the borrower's account history and next statement. A successful call returns a receipt naming
    the new charge.

    Args:
        finance_account_id: Id class — the reference number of the financing account the fee is charged
            to, as returned by the financing account lookup.
        statement_period: Fixed-format class — the monthly statement period the late fee belongs to (the
            month whose scheduled payment was late), written as YYYY-MM with a four-digit year and a
            two-digit month; never empty.
        amount: Fixed-format class — the late fee charged, in USD, a positive amount with 2 decimal places;
            the value is stored rounded to 2 decimal places.

    Returns:
        A text rendering of a dictionary with these fields: finance_txn_id (string, the reference number
        of the new late-fee charge), finance_account_id (string, the account charged), statement_period
        (string, YYYY-MM, the period the fee names), amount (number, USD with 2 decimal places, the fee
        booked), posted_on (string, YYYY-MM-DD, the posting date) and status (string, the word posted when
        the charge was booked).
    """
    acct = (ctx.find("finance_accounts", finance_account_id=finance_account_id) or [{}])[0]
    fee = round(float(amount), 2)
    rid = ctx.make_id("ftx_", finance_account_id, "late_fee", statement_period, fee)
    posted_on = ctx.now()[:10]
    ctx.create("finance_transactions", rid, finance_txn_id=rid, finance_account_id=finance_account_id,
               customer_id=acct.get("customer_id", ""), event_type="finance_fee_assessed",
               txn_date=posted_on, amount=fee, payment_channel="not_applicable",
               payment_kind="not_applicable", interest_kind="not_applicable", fee_kind="late_fee",
               statement_period=statement_period, source_finance_txn_id="", deferral_months=0,
               new_due_day=0)
    return str({"finance_txn_id": rid, "finance_account_id": finance_account_id,
                "statement_period": statement_period, "amount": fee, "posted_on": posted_on,
                "status": "posted"})


@tool(owner="user", rw="write")
def submit_finance_hardship_request_30b3e3a9(ctx: ToolContext, finance_account_id: str,
                                             hardship_reason: str, requested_months: int) -> str:
    """The borrower files their own hardship request on a Ridgeline Home Improvement Financing account,
    asking to defer scheduled payments. The request is recorded against the account with the reason the
    borrower gives and the number of months of payment deferral asked for, and it stands as a submitted
    request awaiting the lender's decision; the borrower can see it on the account at once. A successful
    call returns a receipt naming the new request.

    Args:
        finance_account_id: Id class — the reference number of the financing account the request concerns,
            as returned by the financing account lookup.
        hardship_reason: Enum class — the reason the borrower gives for the hardship, exactly one of:
            job_loss — the borrower or the household's earner has lost their job;
            medical — an illness, injury or medical treatment has stopped or cut the household's income;
            natural_disaster — a storm, flood, fire or other natural disaster has struck the home or the
            household's income;
            reduced_income — the household still works but its income has been cut, such as reduced hours
            or pay.
        requested_months: Fixed-format class — the months of payment deferral the borrower asks for, a
            non-negative integer count of whole months.

    Returns:
        A text rendering of a dictionary with these fields: finance_hardship_request_id (string, the
        reference number of the new hardship request), finance_account_id (string, the account it
        concerns), hardship_reason (string, the reason recorded), requested_months (integer, the months
        asked for) and request_status (string, the word submitted when the request has been recorded).
    """
    acct = (ctx.find("finance_accounts", finance_account_id=finance_account_id) or [{}])[0]
    months = int(requested_months)
    rid = ctx.make_id("fhr_", finance_account_id, hardship_reason, months)
    ctx.create("finance_hardship_requests", rid, finance_hardship_request_id=rid,
               customer_id=acct.get("customer_id", ""), finance_account_id=finance_account_id,
               hardship_reason=hardship_reason, requested_months=months, request_status="submitted",
               created_at=ctx.now())
    return str({"finance_hardship_request_id": rid, "finance_account_id": finance_account_id,
                "hardship_reason": hardship_reason, "requested_months": months,
                "request_status": "submitted"})


@tool(owner="agent", rw="write")
def post_finance_hardship_deferral_5a1cdd93(ctx: ToolContext, finance_account_id: str,
                                            finance_hardship_request_id: str, statement_period: str,
                                            deferral_months: int) -> str:
    """Grant a hardship deferral on a Ridgeline Home Improvement Financing account under a submitted
    hardship request. The deferral is booked on the account history dated the day it is granted, naming
    the first statement period deferred and the number of consecutive months deferred, with no amount
    charged; the hardship request it answers is marked approved. The borrower sees the deferral and the
    approved request on the account at once. A successful call returns a receipt naming the deferral.

    Args:
        finance_account_id: Id class — the reference number of the financing account the deferral is
            granted on, as returned by the financing account lookup.
        finance_hardship_request_id: Id class — the reference number of the hardship request the deferral
            answers, as returned by the hardship request lookup or by the filing of the request.
        statement_period: Fixed-format class — the first statement period the deferral covers, written as
            YYYY-MM with a four-digit year and a two-digit month; never empty.
        deferral_months: Fixed-format class — the consecutive months deferred, a non-negative integer count
            of whole months.

    Returns:
        A text rendering of a dictionary with these fields: finance_txn_id (string, the reference number
        of the deferral entry), finance_account_id (string, the account), finance_hardship_request_id
        (string, the request answered), statement_period (string, YYYY-MM, the first period deferred),
        deferral_months (integer, the months deferred), request_status (string, the word approved) and
        status (string, the word granted when the deferral was booked).
    """
    acct = (ctx.find("finance_accounts", finance_account_id=finance_account_id) or [{}])[0]
    months = int(deferral_months)
    rid = ctx.make_id("ftx_", finance_account_id, finance_hardship_request_id, statement_period, months)
    ctx.create("finance_transactions", rid, finance_txn_id=rid, finance_account_id=finance_account_id,
               customer_id=acct.get("customer_id", ""), event_type="finance_payment_deferred",
               txn_date=ctx.now()[:10], amount=0.0, payment_channel="not_applicable",
               payment_kind="not_applicable", interest_kind="not_applicable", fee_kind="not_applicable",
               statement_period=statement_period, source_finance_txn_id="", deferral_months=months,
               new_due_day=0)
    ctx.update("finance_hardship_requests", finance_hardship_request_id, request_status="approved")
    return str({"finance_txn_id": rid, "finance_account_id": finance_account_id,
                "finance_hardship_request_id": finance_hardship_request_id,
                "statement_period": statement_period, "deferral_months": months,
                "request_status": "approved", "status": "granted"})


@tool(owner="agent", rw="write")
def post_finance_period_interest_067abc59(ctx: ToolContext, finance_account_id: str, statement_period: str,
                                          amount: float) -> str:
    """Post the monthly interest for one statement period to a Ridgeline Home Improvement Financing
    account. The interest is booked on the account as a new monthly-interest charge dated the day it is
    posted and naming the statement period it is charged for; it raises the amount owed on the account by
    the interest and shows on the borrower's account history and statement. A successful call returns a
    receipt naming the new charge.

    Args:
        finance_account_id: Id class — the reference number of the financing account the interest is
            charged to, as returned by the financing account lookup.
        statement_period: Fixed-format class — the monthly statement period the interest is charged for,
            written as YYYY-MM with a four-digit year and a two-digit month; never empty.
        amount: Fixed-format class — the interest charged, in USD, a non-negative amount with 2 decimal
            places; the value is stored rounded to 2 decimal places.

    Returns:
        A text rendering of a dictionary with these fields: finance_txn_id (string, the reference number
        of the new monthly-interest charge), finance_account_id (string, the account charged),
        statement_period (string, YYYY-MM, the period charged), amount (number, USD with 2 decimal places,
        the interest booked), posted_on (string, YYYY-MM-DD, the posting date) and status (string, the word
        posted when the charge was booked).
    """
    acct = (ctx.find("finance_accounts", finance_account_id=finance_account_id) or [{}])[0]
    interest = round(float(amount), 2)
    rid = ctx.make_id("ftx_", finance_account_id, "monthly_interest", statement_period, interest)
    posted_on = ctx.now()[:10]
    ctx.create("finance_transactions", rid, finance_txn_id=rid, finance_account_id=finance_account_id,
               customer_id=acct.get("customer_id", ""), event_type="finance_interest_assessed",
               txn_date=posted_on, amount=interest, payment_channel="not_applicable",
               payment_kind="not_applicable", interest_kind="monthly_interest", fee_kind="not_applicable",
               statement_period=statement_period, source_finance_txn_id="", deferral_months=0,
               new_due_day=0)
    return str({"finance_txn_id": rid, "finance_account_id": finance_account_id,
                "statement_period": statement_period, "amount": interest, "posted_on": posted_on,
                "status": "posted"})


@tool(owner="agent", rw="write")
def post_finance_phone_fee_cbbb3871(ctx: ToolContext, finance_account_id: str, source_finance_txn_id: str,
                                    statement_period: str, posting_date: str, amount: float) -> str:
    """Charge the agent-assisted phone payment fee for one payment taken through a phone agent on a
    Ridgeline Home Improvement Financing account. The fee is booked on the account as a new phone-payment
    fee entry dated on the given posting date, naming the payment it concerns and its statement period; it
    raises the amount owed on the account by the fee and shows on the borrower's account history. A
    successful call returns a receipt naming the new charge.

    Args:
        finance_account_id: Id class — the reference number of the financing account the fee is charged to,
            as returned by the financing account lookup.
        source_finance_txn_id: Id class — the reference number of the payment taken through a phone agent
            that the fee concerns, as returned by the financing history lookup.
        statement_period: Fixed-format class — the statement period of the payment the fee concerns, written
            as YYYY-MM with a four-digit year and a two-digit month; never empty.
        posting_date: Fixed-format class — the date the fee is booked on, written as YYYY-MM-DD; it is the
            posting date of the payment the fee concerns; never empty.
        amount: Fixed-format class — the fee charged, in USD, a positive amount with 2 decimal places; the
            value is stored rounded to 2 decimal places.

    Returns:
        A text rendering of a dictionary with these fields: finance_txn_id (string, the reference number of
        the new fee entry), finance_account_id (string, the account charged), source_finance_txn_id (string,
        the payment named), statement_period (string, YYYY-MM), posted_on (string, YYYY-MM-DD, the booking
        date), amount (number, USD with 2 decimal places) and status (string, the word posted when the fee
        was booked).
    """
    acct = (ctx.find("finance_accounts", finance_account_id=finance_account_id) or [{}])[0]
    fee = round(float(amount), 2)
    rid = ctx.make_id("ftx_", finance_account_id, "phone_payment_fee", source_finance_txn_id, posting_date, fee)
    ctx.create("finance_transactions", rid, finance_txn_id=rid, finance_account_id=finance_account_id,
               customer_id=acct.get("customer_id", ""), event_type="finance_fee_assessed",
               txn_date=posting_date, amount=fee, payment_channel="not_applicable",
               payment_kind="not_applicable", interest_kind="not_applicable", fee_kind="phone_payment_fee",
               statement_period=statement_period, source_finance_txn_id=source_finance_txn_id,
               deferral_months=0, new_due_day=0)
    return str({"finance_txn_id": rid, "finance_account_id": finance_account_id,
                "source_finance_txn_id": source_finance_txn_id, "statement_period": statement_period,
                "posted_on": posting_date, "amount": fee, "status": "posted"})


@tool(owner="user", rw="write")
def submit_finance_portal_payment_b662a17f(ctx: ToolContext, finance_account_id: str, statement_period: str,
                                           amount: float) -> str:
    """The borrower makes a one-time payment themselves in the Ridgeline online portal toward the scheduled
    payments on a Ridgeline Home Improvement Financing account. The payment posts to the account the same
    day as a scheduled payment made through the online portal, credited to the statement period given, and
    lowers the amount owed by the amount paid; no phone payment fee applies. A successful call returns a
    receipt naming the posted payment.

    Args:
        finance_account_id: Id class — the reference number of the financing account being paid, as returned
            by the financing account lookup or read from the borrower's statement.
        statement_period: Fixed-format class — the statement period the payment is credited to, written as
            YYYY-MM with a four-digit year and a two-digit month; never empty.
        amount: Fixed-format class — the amount paid, in USD, a positive amount with 2 decimal places; the
            value is stored rounded to 2 decimal places.

    Returns:
        A text rendering of a dictionary with these fields: finance_txn_id (string, the confirmation number
        of the posted payment), finance_account_id (string, the account paid), statement_period (string,
        YYYY-MM, the period credited), amount (number, USD with 2 decimal places, the amount posted),
        posted_on (string, YYYY-MM-DD) and status (string, the word posted when the payment was taken).
    """
    acct = (ctx.find("finance_accounts", finance_account_id=finance_account_id) or [{}])[0]
    paid = round(float(amount), 2)
    rid = ctx.make_id("ftx_", finance_account_id, "portal_payment", statement_period, paid)
    posted_on = ctx.now()[:10]
    ctx.create("finance_transactions", rid, finance_txn_id=rid, finance_account_id=finance_account_id,
               customer_id=acct.get("customer_id", ""), event_type="finance_payment_posted",
               txn_date=posted_on, amount=paid, payment_channel="online_portal",
               payment_kind="scheduled_payment", interest_kind="not_applicable", fee_kind="not_applicable",
               statement_period=statement_period, source_finance_txn_id="", deferral_months=0, new_due_day=0)
    return str({"finance_txn_id": rid, "finance_account_id": finance_account_id,
                "statement_period": statement_period, "amount": paid, "posted_on": posted_on,
                "status": "posted"})

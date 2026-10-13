"""Hidden task tools for the member_equity_patronage difficulty of Cottonwood Plains Farm Credit, ACA.

Each tool performs one atomic write on a member's equity records with the values it is given.
It checks no business condition: which value to pass, and whether the write is due at all, is
settled beforehand from the published servicing rules and the member's records.
"""

from erlbench import ToolContext, tool


@tool(owner="agent", rw="write")
def book_preferred_dividend_reinvestment_5d71129c(ctx: ToolContext, equity_id: str, amount: float,
                                                   payment_date: str) -> str:
    """Book one quarter's Class H Preferred Stock dividend as reinvested in additional preferred shares.

    The association's servicing desk records, on the member's preferred stock holding, a dividend
    reinvested entry for the dividend amount given, effective on the dividend payment date given, and
    raises the holding's balance by the same amount (one share of 1.00 par per dollar reinvested).
    Afterwards the new entry appears in the holding's activity as a reinvested dividend and the
    holding shows the higher balance. The call succeeds when the receipt below is returned.

    Args:
        equity_id: Id class — the reference number of the member's Class H Preferred Stock holding, read from the member's equity holdings lookup.
        amount: Fixed-format class — the dividend reinvested, in USD, 2 decimal places, rounded half up to the cent before it is passed; a positive number.
        payment_date: Fixed-format class — the dividend payment date of the quarter being booked, written YYYY-MM-DD (calendar date, no time part).

    Returns:
        A dict: status ("booked" on success); eq_txn_id (reference of the new reinvested dividend
        entry, text); equity_id (the holding booked to, text); amount (USD reinvested, number with 2
        decimal places); effective_date (YYYY-MM-DD, the dividend payment date); new_balance (the
        holding's balance after the reinvestment, USD, number with 2 decimal places).
    """
    holding = ctx.find("equity_accounts", equity_id=equity_id)
    row = holding[0] if holding else {}
    amt = round(float(amount), 2)
    rid = ctx.make_id("eqt_", equity_id, amt, payment_date)
    ctx.create("equity_transactions", rid, eq_txn_id=rid, equity_id=equity_id,
               customer_id=row.get("customer_id", ""), event_type="equity_dividend_reinvested",
               amount=amt, effective_date=payment_date, patronage_year="", source_loan_id="",
               source_loan_line="none", eligible_adb="", patronage_rate_pct="",
               payment_method="reinvested", check_number="", retirement_reason="none", source_ref_id="")
    new_balance = round(float(row.get("balance") or 0) + amt, 2)
    ctx.update("equity_accounts", equity_id, balance=new_balance)
    return str({"status": "booked", "eq_txn_id": rid, "equity_id": equity_id, "amount": amt,
                "effective_date": payment_date, "new_balance": new_balance})


@tool(owner="agent", rw="write")
def pay_preferred_redemption_7befd982(ctx: ToolContext, equity_id: str, amount: float) -> str:
    """Pay out an approved Class H Preferred Stock redemption and record the shares retired at par.

    The association's servicing desk records, on the member's preferred stock holding, a retirement
    entry with reason redemption for the par amount given, effective today, paid by the payout method
    on the holding (direct deposit to the account on file, otherwise check). The holding's balance is
    lowered by that amount and the pending redemption request date is cleared; the holding returns to
    active status when a balance remains, or is closed as retired when the balance reaches zero. The
    member can then see the redemption entry and the new balance. The call succeeds when the receipt
    below is returned.

    Args:
        equity_id: Id class — the reference number of the member's Class H Preferred Stock holding, read from the member's equity holdings lookup.
        amount: Fixed-format class — the par value of the shares redeemed and paid, in USD, 2 decimal places, rounded half up to the cent before it is passed; a positive number.

    Returns:
        A dict: status ("paid" on success); eq_txn_id (reference of the new redemption entry, text);
        equity_id (the holding paid from, text); amount (USD redeemed at par, number with 2 decimal
        places); payment_method (how the proceeds were sent: direct_deposit or check); new_balance
        (the holding's balance afterwards, USD, number with 2 decimal places); holding_status (active
        when shares remain, retired when none remain).
    """
    holding = ctx.find("equity_accounts", equity_id=equity_id)
    row = holding[0] if holding else {}
    amt = round(float(amount), 2)
    method = "direct_deposit" if row.get("patronage_payment_method") == "direct_deposit" else "check"
    today = ctx.now()[:10]
    rid = ctx.make_id("eqt_", equity_id, amt, today, "redemption")
    ctx.create("equity_transactions", rid, eq_txn_id=rid, equity_id=equity_id,
               customer_id=row.get("customer_id", ""), event_type="equity_retirement",
               amount=amt, effective_date=today, patronage_year="", source_loan_id="",
               source_loan_line="none", eligible_adb="", patronage_rate_pct="",
               payment_method=method, check_number="", retirement_reason="redemption", source_ref_id="")
    new_balance = round(float(row.get("balance") or 0) - amt, 2)
    status = "active" if new_balance > 0 else "retired"
    ctx.update("equity_accounts", equity_id, balance=new_balance, status=status,
               retirement_requested_date="", retired_date=("" if status == "active" else today))
    return str({"status": "paid", "eq_txn_id": rid, "equity_id": equity_id, "amount": amt,
                "payment_method": method, "new_balance": new_balance, "holding_status": status})


@tool(owner="user", rw="write")
def submit_preferred_redemption_request_9710f0b7(ctx: ToolContext, equity_id: str,
                                                  requested_amount: float) -> str:
    """Submit the member's own written request to redeem part of their Class H Preferred Stock.

    The member signs and submits a preferred stock redemption request for the dollar amount given on
    their own preferred stock holding. A new request is registered as submitted, dated now, and the
    holding is marked as having a redemption requested, with today's date as the date the written
    request took effect. The member then sees the request reference and the request date. The call
    succeeds when the receipt below is returned.

    Args:
        equity_id: Id class — the reference number of the member's own Class H Preferred Stock holding, read to the member by the servicing agent from the equity holdings lookup.
        requested_amount: Fixed-format class — the dollar amount of preferred stock the member asks to redeem, in USD, 2 decimal places, rounded half up to the cent; a positive number.

    Returns:
        A dict: status ("submitted" on success); request_id (reference of the new redemption request,
        text); equity_id (the holding concerned, text); requested_amount (USD, number with 2 decimal
        places); request_date (YYYY-MM-DD, the date the written request took effect).
    """
    holding = ctx.find("equity_accounts", equity_id=equity_id)
    row = holding[0] if holding else {}
    amt = round(float(requested_amount), 2)
    rid = ctx.make_id("eqr_", equity_id, amt)
    ctx.create("equity_requests", rid, request_id=rid, customer_id=row.get("customer_id", ""),
               equity_id=equity_id, request_type="preferred_redemption", requested_amount=amt,
               request_status="submitted", created_at=ctx.now())
    today = ctx.now()[:10]
    ctx.update("equity_accounts", equity_id, status="retirement_requested", retirement_requested_date=today)
    return str({"status": "submitted", "request_id": rid, "equity_id": equity_id,
                "requested_amount": amt, "request_date": today})


class _Preferred:
    """Shared row builder (not a tool): the cancellation entry and the balance it leaves."""

    @staticmethod
    def cancellation(ctx: ToolContext, equity_id: str, amount: float, effective_date: str, paid: bool, tag: str) -> tuple:
        holding = ctx.find("equity_accounts", equity_id=equity_id)
        row = holding[0] if holding else {}
        amt = round(float(amount), 2)
        if paid:
            method = "direct_deposit" if row.get("patronage_payment_method") == "direct_deposit" else "check"
        else:
            method = "none"
        rid = ctx.make_id("eqt_", equity_id, amt, effective_date, tag)
        fields = dict(eq_txn_id=rid, equity_id=equity_id, customer_id=row.get("customer_id", ""),
                      event_type="equity_retirement", amount=amt, effective_date=effective_date,
                      patronage_year="", source_loan_id="", source_loan_line="none", eligible_adb="",
                      patronage_rate_pct="", payment_method=method, check_number="",
                      retirement_reason="subscription_cancelled", source_ref_id="")
        new_balance = round(float(row.get("balance") or 0) - amt, 2)
        return rid, fields, new_balance


@tool(owner="agent", rw="write")
def refund_preferred_quarter_excess_3d5c0453(ctx: ToolContext, equity_id: str, amount: float,
                                              effective_date: str) -> str:
    """Cancel and refund the part of a Class H Preferred Stock purchase that went over a calendar quarter's purchase limit.

    The association's servicing desk records, on the member's preferred stock holding, a cancellation
    entry for the par amount given, dated as of the date given, with the reason subscription cancelled;
    the money is sent back by the payout method on the holding (direct deposit to the account on file,
    otherwise check). The holding's balance is lowered by the same amount. Afterwards the member can see
    the cancellation entry and the lower balance. The call succeeds when the receipt below is returned.

    Args:
        equity_id: Id class — the reference number of the member's Class H Preferred Stock holding, read from the member's equity holdings lookup.
        amount: Fixed-format class — the par amount cancelled and refunded, in USD, 2 decimal places, rounded half up to the cent before it is passed; a positive number.
        effective_date: Fixed-format class — the date the cancellation takes effect as of, written YYYY-MM-DD (calendar date, no time part).

    Returns:
        A dict: status ("refunded" on success); eq_txn_id (reference of the cancellation entry, text);
        equity_id (the holding, text); amount (USD refunded, number with 2 decimal places);
        payment_method (how the refund was sent: direct_deposit or check); effective_date (YYYY-MM-DD);
        new_balance (the holding's balance afterwards, USD, number with 2 decimal places).
    """
    rid, fields, new_balance = _Preferred.cancellation(ctx, equity_id, amount, effective_date, True, "quarter_excess")
    ctx.create("equity_transactions", rid, **fields)
    ctx.update("equity_accounts", equity_id, balance=new_balance)
    out = {"eq_txn_id": rid, "amount": fields["amount"], "payment_method": fields["payment_method"], "new_balance": new_balance}
    return str({"status": "refunded", "eq_txn_id": out["eq_txn_id"], "equity_id": equity_id,
                "amount": out["amount"], "payment_method": out["payment_method"],
                "effective_date": effective_date, "new_balance": out["new_balance"]})


@tool(owner="agent", rw="write")
def refund_preferred_holding_excess_154bc05b(ctx: ToolContext, equity_id: str, amount: float,
                                              effective_date: str) -> str:
    """Cancel and refund the Class H Preferred Stock shares a holding carries above the largest balance a member may hold.

    The association's servicing desk records, on the member's preferred stock holding, a cancellation
    entry for the par amount given, dated as of the date given, with the reason subscription cancelled;
    the money is sent back by the payout method on the holding (direct deposit to the account on file,
    otherwise check). The holding's balance is lowered by the same amount. Afterwards the member can see
    the cancellation entry and the lower balance. The call succeeds when the receipt below is returned.

    Args:
        equity_id: Id class — the reference number of the member's Class H Preferred Stock holding, read from the member's equity holdings lookup.
        amount: Fixed-format class — the par amount of shares cancelled and refunded, in USD, 2 decimal places, rounded half up to the cent before it is passed; a positive number.
        effective_date: Fixed-format class — the date the cancellation takes effect as of, written YYYY-MM-DD (calendar date, no time part).

    Returns:
        A dict: status ("refunded" on success); eq_txn_id (reference of the cancellation entry, text);
        equity_id (the holding, text); amount (USD refunded, number with 2 decimal places);
        payment_method (how the refund was sent: direct_deposit or check); effective_date (YYYY-MM-DD);
        new_balance (the holding's balance afterwards, USD, number with 2 decimal places).
    """
    rid, fields, new_balance = _Preferred.cancellation(ctx, equity_id, amount, effective_date, True, "holding_excess")
    ctx.create("equity_transactions", rid, **fields)
    ctx.update("equity_accounts", equity_id, balance=new_balance)
    out = {"eq_txn_id": rid, "amount": fields["amount"], "payment_method": fields["payment_method"], "new_balance": new_balance}
    return str({"status": "refunded", "eq_txn_id": out["eq_txn_id"], "equity_id": equity_id,
                "amount": out["amount"], "payment_method": out["payment_method"],
                "effective_date": effective_date, "new_balance": out["new_balance"]})


@tool(owner="agent", rw="write")
def reverse_preferred_dividend_68f89242(ctx: ToolContext, equity_id: str, amount: float) -> str:
    """Reverse part of a reinvested Class H Preferred Stock dividend by cancelling the shares it bought.

    The association's servicing desk records, on the member's preferred stock holding, a cancellation
    entry for the par amount of reinvested dividend shares given, dated today, with the reason
    subscription cancelled and no money paid out. The holding's balance is lowered by the same amount.
    Afterwards the member can see the cancellation entry and the lower balance. The call succeeds when
    the receipt below is returned.

    Args:
        equity_id: Id class — the reference number of the member's Class H Preferred Stock holding, read from the member's equity holdings lookup.
        amount: Fixed-format class — the par amount of reinvested dividend shares cancelled, in USD, 2 decimal places, rounded half up to the cent before it is passed; a positive number.

    Returns:
        A dict: status ("reversed" on success); eq_txn_id (reference of the cancellation entry, text);
        equity_id (the holding, text); amount (USD of shares cancelled, number with 2 decimal places);
        effective_date (YYYY-MM-DD, today); new_balance (the holding's balance afterwards, USD, number
        with 2 decimal places).
    """
    today = ctx.now()[:10]
    rid, fields, new_balance = _Preferred.cancellation(ctx, equity_id, amount, today, False, "dividend_reversal")
    ctx.create("equity_transactions", rid, **fields)
    ctx.update("equity_accounts", equity_id, balance=new_balance)
    out = {"eq_txn_id": rid, "amount": fields["amount"], "payment_method": fields["payment_method"], "new_balance": new_balance}
    return str({"status": "reversed", "eq_txn_id": out["eq_txn_id"], "equity_id": equity_id,
                "amount": out["amount"], "effective_date": today, "new_balance": out["new_balance"]})


@tool(owner="user", rw="write")
def submit_preferred_purchase_895be76e(ctx: ToolContext, equity_id: str, amount: float) -> str:
    """Place the member's own purchase of additional Class H Preferred Stock on their preferred holding.

    The member authorizes and pays for a purchase of preferred shares at 1.00 par for the dollar amount
    given, paid by an electronic draw from the checking account recorded for direct deposit on the
    holding. A purchase entry dated today is recorded on the member's preferred stock
    holding and the holding's balance rises by the amount. The member then sees the purchase reference
    and the new balance. The call succeeds when the receipt below is returned.

    Args:
        equity_id: Id class — the reference number of the member's own Class H Preferred Stock holding, read to the member by the servicing agent from the equity holdings lookup.
        amount: Fixed-format class — the dollar amount of preferred stock bought, in USD, 2 decimal places, rounded half up to the cent; a positive number.

    Returns:
        A dict: status ("purchased" on success); eq_txn_id (reference of the purchase entry, text);
        equity_id (the holding, text); amount (USD bought, number with 2 decimal places); payment_method
        (always direct_deposit); effective_date (YYYY-MM-DD, today); new_balance (the holding's balance
        afterwards, USD, number with 2 decimal places).
    """
    holding = ctx.find("equity_accounts", equity_id=equity_id)
    row = holding[0] if holding else {}
    amt = round(float(amount), 2)
    today = ctx.now()[:10]
    payment_method = "direct_deposit"
    rid = ctx.make_id("eqt_", equity_id, amt, today, "purchase")
    ctx.create("equity_transactions", rid, eq_txn_id=rid, equity_id=equity_id,
               customer_id=row.get("customer_id", ""), event_type="equity_purchase",
               amount=amt, effective_date=today, patronage_year="", source_loan_id="",
               source_loan_line="none", eligible_adb="", patronage_rate_pct="",
               payment_method=payment_method, check_number="", retirement_reason="none", source_ref_id="")
    new_balance = round(float(row.get("balance") or 0) + amt, 2)
    ctx.update("equity_accounts", equity_id, balance=new_balance)
    return str({"status": "purchased", "eq_txn_id": rid, "equity_id": equity_id, "amount": amt,
                "payment_method": payment_method, "effective_date": today, "new_balance": new_balance})

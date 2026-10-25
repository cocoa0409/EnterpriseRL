"""Hidden task tools of the residential_bill_credits_and_charges difficulty (category home).

Each tool performs one atomic write on the residential subscription billing ledger; amounts and dates are worked out
by the caller from the published rules and passed in.
"""

from erlbench import ToolContext, tool


class _Money:
    """Pure-Python money helpers shared by the tools of this file."""

    @staticmethod
    def half_up(value) -> float:
        """Round a non-negative amount half up to the cent."""
        cents = int(float(value) * 100 + 0.5 + 0.000001)
        return cents / 100


@tool(owner="agent", rw="write")
def bill_estimated_charge_232393a8(ctx: ToolContext, home_sub_id: str, customer_id: str, billing_month: str,
                                   amount: float, due_date: str) -> str:
    """Bill an estimated subscription charge on a residential community solar subscription for a statement month whose
    utility bill credit has not been reported. One call adds one estimated charge line to that subscription's billing
    ledger: it is dated today as its invoice date, carries no credit statement reference, is marked as an estimate under
    dual billing, and raises the balance the subscriber owes by the amount given. The new charge line is visible
    immediately when the subscription's billing ledger is looked up; the call succeeds when the receipt returns the new
    line's reference with status billed.

    Args:
        home_sub_id: Id class — the reference number of the residential subscription the estimate is billed on, as
            returned by the residential subscription lookup.
        customer_id: Id class — the reference number of the customer who owns that subscription, as returned by the
            customer profile lookup.
        billing_month: Fixed-format class — the statement month the estimate stands in for, written YYYY-MM.
        amount: Fixed-format class — the estimated charge in USD, 2 decimal places, greater than 0.00; a value with more
            decimals is rounded half up to the cent before it is recorded.
        due_date: Fixed-format class — the payment due date of the estimated charge, written YYYY-MM-DD.

    Returns:
        A dictionary rendered as text with these fields: status (the text billed on success, or error
        when the amount is not greater than 0.00), home_bill_id (reference of the new estimated charge line),
        home_sub_id (the subscription billed), billing_month (statement month estimated, YYYY-MM), amount (USD booked,
        2 decimal places), bill_date (invoice date, YYYY-MM-DD, today) and due_date (YYYY-MM-DD).
    """
    booked = _Money.half_up(amount)
    if booked <= 0:
        return str({"status": "error", "home_bill_id": "", "home_sub_id": home_sub_id, "billing_month": billing_month,
                    "amount": booked, "bill_date": "", "due_date": due_date})
    rid = ctx.make_id("hbl_", home_sub_id, customer_id, billing_month, amount, due_date, "estimated")
    today = ctx.now()[:10]
    ctx.create("home_billing", rid, home_bill_id=rid, home_sub_id=home_sub_id, customer_id=customer_id,
               event_type="home_charge_billed", amount=booked, bill_date=today, billing_month=billing_month,
               due_date=due_date, home_credit_id=None, home_ref_bill_id=None, charge_basis="estimated",
               billing_type="dual", payment_method="not_applicable", credit_reason="not_applicable")
    return str({"status": "billed", "home_bill_id": rid, "home_sub_id": home_sub_id, "billing_month": billing_month,
                "amount": booked, "bill_date": today, "due_date": due_date})


@tool(owner="agent", rw="write")
def assess_overdue_charge_late_fee_df41ca22(ctx: ToolContext, home_sub_id: str, customer_id: str,
                                            home_ref_bill_id: str, billing_month: str, amount: float,
                                            due_date: str) -> str:
    """Assess a late fee on one overdue dual-billed subscription charge of a residential community solar subscription.
    One call adds one late fee line to that subscription's billing ledger, dated today, referring to the overdue charge
    it is assessed on, and raises the balance the subscriber owes by the fee given. The fee line is visible immediately
    when the subscription's billing ledger is looked up; the call succeeds when the receipt returns the new fee line's
    reference with status assessed.

    Args:
        home_sub_id: Id class — the reference number of the residential subscription, as returned by the residential
            subscription lookup.
        customer_id: Id class — the reference number of the customer who owns that subscription, as returned by the
            customer profile lookup.
        home_ref_bill_id: Id class — the billing ledger line number of the overdue subscription charge the fee is
            assessed on, as returned by the billing ledger lookup.
        billing_month: Fixed-format class — the statement month of that overdue charge, written YYYY-MM.
        amount: Fixed-format class — the late fee in USD, 2 decimal places, greater than 0.00; a value with more
            decimals is rounded half up to the cent before it is recorded.
        due_date: Fixed-format class — the payment due date of the late fee, written YYYY-MM-DD.

    Returns:
        A dictionary rendered as text with these fields: status (the text assessed on success, or error
        when the amount is not greater than 0.00), home_bill_id (reference of the new late fee line), home_sub_id,
        home_ref_bill_id (the overdue charge), amount (USD booked, 2 decimal places), bill_date (assessment date,
        YYYY-MM-DD, today) and due_date (YYYY-MM-DD).
    """
    booked = _Money.half_up(amount)
    if booked <= 0:
        return str({"status": "error", "home_bill_id": "", "home_sub_id": home_sub_id,
                    "home_ref_bill_id": home_ref_bill_id, "amount": booked, "bill_date": "", "due_date": due_date})
    rid = ctx.make_id("hlf_", home_sub_id, customer_id, home_ref_bill_id, billing_month, amount, due_date)
    today = ctx.now()[:10]
    ctx.create("home_billing", rid, home_bill_id=rid, home_sub_id=home_sub_id, customer_id=customer_id,
               event_type="home_late_fee_assessed", amount=booked, bill_date=today, billing_month=billing_month,
               due_date=due_date, home_credit_id=None, home_ref_bill_id=home_ref_bill_id, charge_basis="not_applicable",
               billing_type="dual", payment_method="not_applicable", credit_reason="not_applicable")
    return str({"status": "assessed", "home_bill_id": rid, "home_sub_id": home_sub_id,
                "home_ref_bill_id": home_ref_bill_id, "amount": booked, "bill_date": today, "due_date": due_date})


@tool(owner="user", rw="write")
def pay_final_balance_42abd449(ctx: ToolContext, home_sub_id: str, customer_id: str, billing_month: str,
        amount: float,
                               payment_method: str) -> str:
    """The subscriber personally pays, through Meadowlark's secure payment portal, an amount toward the balance of their
    own residential community solar subscription. One call records one payment received on that subscription's billing
    ledger, dated today, recorded against the statement month given, with dual billing as the arrangement, and lowers the
    balance owed by the amount paid. The payment is visible immediately when the billing ledger is looked up; the call
    succeeds when the receipt returns the payment line's reference with status received.

    Args:
        home_sub_id: Id class — the reference number of the subscriber's residential subscription, as read out to the
            subscriber from the residential subscription lookup.
        customer_id: Id class — the subscriber's customer reference number, as read out to the subscriber from the
            customer profile lookup.
        billing_month: Fixed-format class — the statement month the payment is recorded against, written YYYY-MM.
        amount: Fixed-format class — the amount paid in USD, 2 decimal places, greater than 0.00; a value with more
            decimals is rounded half up to the cent before it is recorded.
        payment_method: Enum class — how the subscriber pays in the portal: ach when the subscriber pays from a bank
            account they enter in the portal themselves; card when the subscriber pays with a debit or credit card they
            enter in the portal themselves; check is not taken by the portal (a mailed check is posted when it
            arrives), utility_remittance is not taken by the portal (it is the utility's own payment under consolidated
            billing) and not_applicable is not taken by the portal (it marks lines that are not payments).

    Returns:
        A dictionary rendered as text with these fields: status (the text received on success, or error when the amount
        is not greater than 0.00 or the method is not one the portal takes), home_bill_id (reference of the payment
        line), home_sub_id, amount (USD received, 2 decimal places), payment_method, bill_date (receipt date,
        YYYY-MM-DD, today) and billing_month (the statement month recorded, YYYY-MM).
    """
    booked = _Money.half_up(amount)
    today = ctx.now()[:10]
    if booked <= 0 or payment_method not in ("ach", "card"):
        return str({"status": "error", "home_bill_id": "", "home_sub_id": home_sub_id, "amount": booked,
                    "payment_method": payment_method, "bill_date": "", "billing_month": ""})
    rid = ctx.make_id("hpy_", home_sub_id, customer_id, billing_month, amount, payment_method, today)
    ctx.create("home_billing", rid, home_bill_id=rid, home_sub_id=home_sub_id, customer_id=customer_id,
               event_type="home_payment_received", amount=booked, bill_date=today, billing_month=billing_month,
               due_date="", home_credit_id=None, home_ref_bill_id=None, charge_basis="not_applicable",
               billing_type="dual", payment_method=payment_method, credit_reason="not_applicable")
    return str({"status": "received", "home_bill_id": rid, "home_sub_id": home_sub_id, "amount": booked,
                "payment_method": payment_method, "bill_date": today, "billing_month": billing_month})


@tool(owner="agent", rw="write")
def assess_returned_payment_fee_1f86a5ed(ctx: ToolContext, home_sub_id: str, customer_id: str, home_ref_bill_id: str,
                                         billing_month: str, amount: float, due_date: str) -> str:
    """Assess the returned-payment fee for one subscriber payment of a residential community solar subscription that the
    bank returned unpaid or the card issuer reversed. One call adds one returned-payment fee line to that subscription's
    billing ledger, dated today, referring to the payment that was returned, and raises the balance the subscriber owes
    by the fee given. The fee line is visible immediately when the subscription's billing ledger is looked up; the call
    succeeds when the receipt returns the new fee line's reference with status assessed.

    Args:
        home_sub_id: Id class — the reference number of the residential subscription, as returned by the residential
            subscription lookup.
        customer_id: Id class — the reference number of the customer who owns that subscription, as returned by the
            customer profile lookup.
        home_ref_bill_id: Id class — the billing ledger line number of the payment that was returned (the payment named
            on its returned-payment line), as returned by the billing ledger lookup.
        billing_month: Fixed-format class — the billing month recorded on that payment, written YYYY-MM.
        amount: Fixed-format class — the returned-payment fee in USD, 2 decimal places, greater than 0.00; a value with
            more decimals is rounded half up to the cent before it is recorded.
        due_date: Fixed-format class — the payment due date of the fee, written YYYY-MM-DD.

    Returns:
        A dictionary rendered as text with these fields: status (the text assessed on success, or error when the amount
        is not greater than 0.00), home_bill_id (reference of the new fee line), home_sub_id, home_ref_bill_id (the
        returned payment), amount (USD booked, 2 decimal places), bill_date (assessment date, YYYY-MM-DD, today) and
        due_date (YYYY-MM-DD).
    """
    booked = _Money.half_up(amount)
    if booked <= 0:
        return str({"status": "error", "home_bill_id": "", "home_sub_id": home_sub_id,
                    "home_ref_bill_id": home_ref_bill_id, "amount": booked, "bill_date": "", "due_date": due_date})
    rid = ctx.make_id("hrf_", home_sub_id, customer_id, home_ref_bill_id, billing_month, amount, due_date)
    today = ctx.now()[:10]
    ctx.create("home_billing", rid, home_bill_id=rid, home_sub_id=home_sub_id, customer_id=customer_id,
               event_type="home_returned_fee_assessed", amount=booked, bill_date=today, billing_month=billing_month,
               due_date=due_date, home_credit_id=None, home_ref_bill_id=home_ref_bill_id, charge_basis="not_applicable",
               billing_type="dual", payment_method="not_applicable", credit_reason="not_applicable")
    return str({"status": "assessed", "home_bill_id": rid, "home_sub_id": home_sub_id,
                "home_ref_bill_id": home_ref_bill_id, "amount": booked, "bill_date": today, "due_date": due_date})


@tool(owner="agent", rw="write")
def assess_reopened_charge_late_fee_2381e61d(ctx: ToolContext, home_sub_id: str, customer_id: str,
                                             home_ref_bill_id: str, billing_month: str, amount: float,
                                             due_date: str) -> str:
    """Assess a late fee on one dual-billed subscription charge of a residential community solar subscription that a
    returned or reversed payment has reopened. One call adds one late fee line to that subscription's billing ledger,
    dated today, referring to the reopened charge it is assessed on, and raises the balance the subscriber owes by the
    fee given. The fee line is visible immediately when the subscription's billing ledger is looked up; the call
    succeeds when the receipt returns the new fee line's reference with status assessed.

    Args:
        home_sub_id: Id class — the reference number of the residential subscription, as returned by the residential
            subscription lookup.
        customer_id: Id class — the reference number of the customer who owns that subscription, as returned by the
            customer profile lookup.
        home_ref_bill_id: Id class — the billing ledger line number of the reopened subscription charge the fee is
            assessed on, as returned by the billing ledger lookup.
        billing_month: Fixed-format class — the statement month of that reopened charge, written YYYY-MM.
        amount: Fixed-format class — the late fee in USD, 2 decimal places, greater than 0.00; a value with more
            decimals is rounded half up to the cent before it is recorded.
        due_date: Fixed-format class — the payment due date of the late fee, written YYYY-MM-DD.

    Returns:
        A dictionary rendered as text with these fields: status (the text assessed on success, or error when the amount
        is not greater than 0.00), home_bill_id (reference of the new late fee line), home_sub_id, home_ref_bill_id (the
        reopened charge), amount (USD booked, 2 decimal places), bill_date (assessment date, YYYY-MM-DD, today) and
        due_date (YYYY-MM-DD).
    """
    booked = _Money.half_up(amount)
    if booked <= 0:
        return str({"status": "error", "home_bill_id": "", "home_sub_id": home_sub_id,
                    "home_ref_bill_id": home_ref_bill_id, "amount": booked, "bill_date": "", "due_date": due_date})
    rid = ctx.make_id("hlr_", home_sub_id, customer_id, home_ref_bill_id, billing_month, amount, due_date)
    today = ctx.now()[:10]
    ctx.create("home_billing", rid, home_bill_id=rid, home_sub_id=home_sub_id, customer_id=customer_id,
               event_type="home_late_fee_assessed", amount=booked, bill_date=today, billing_month=billing_month,
               due_date=due_date, home_credit_id=None, home_ref_bill_id=home_ref_bill_id, charge_basis="not_applicable",
               billing_type="dual", payment_method="not_applicable", credit_reason="not_applicable")
    return str({"status": "assessed", "home_bill_id": rid, "home_sub_id": home_sub_id,
                "home_ref_bill_id": home_ref_bill_id, "amount": booked, "bill_date": today, "due_date": due_date})


@tool(owner="user", rw="write")
def pay_reversed_payment_replacement_378a2026(ctx: ToolContext, home_sub_id: str, customer_id: str, billing_month: str,
        amount: float,
                                              payment_method: str) -> str:
    """The subscriber personally pays, through Meadowlark's secure payment portal, an amount that makes good a payment of
    theirs on their own residential community solar subscription that came back unpaid or was reversed. One call records
    one payment received on that subscription's billing ledger, dated today, recorded against the statement month given, with
    dual billing as the arrangement, and lowers the balance owed by the amount paid. The payment is visible immediately
    when the billing ledger is looked up; the call succeeds when the receipt returns the payment line's reference with
    status received.

    Args:
        home_sub_id: Id class — the reference number of the subscriber's residential subscription, as read out to the
            subscriber from the residential subscription lookup.
        customer_id: Id class — the subscriber's customer reference number, as read out to the subscriber from the
            customer profile lookup.
        billing_month: Fixed-format class — the statement month the payment is recorded against, written YYYY-MM.
        amount: Fixed-format class — the amount paid in USD, 2 decimal places, greater than 0.00; a value with more
            decimals is rounded half up to the cent before it is recorded.
        payment_method: Enum class — how the subscriber pays in the portal: ach when the subscriber pays from a bank
            account they enter in the portal themselves; card when the subscriber pays with a debit or credit card they
            enter in the portal themselves; check is not taken by the portal (a mailed check is posted when it
            arrives), utility_remittance is not taken by the portal (it is the utility's own payment under consolidated
            billing) and not_applicable is not taken by the portal (it marks lines that are not payments).

    Returns:
        A dictionary rendered as text with these fields: status (the text received on success, or error when the amount
        is not greater than 0.00 or the method is not one the portal takes), home_bill_id (reference of the payment
        line), home_sub_id, amount (USD received, 2 decimal places), payment_method, bill_date (receipt date,
        YYYY-MM-DD, today) and billing_month (the statement month recorded, YYYY-MM).
    """
    booked = _Money.half_up(amount)
    today = ctx.now()[:10]
    if booked <= 0 or payment_method not in ("ach", "card"):
        return str({"status": "error", "home_bill_id": "", "home_sub_id": home_sub_id, "amount": booked,
                    "payment_method": payment_method, "bill_date": "", "billing_month": ""})
    rid = ctx.make_id("hrp_", home_sub_id, customer_id, billing_month, amount, payment_method, today)
    ctx.create("home_billing", rid, home_bill_id=rid, home_sub_id=home_sub_id, customer_id=customer_id,
               event_type="home_payment_received", amount=booked, bill_date=today, billing_month=billing_month,
               due_date="", home_credit_id=None, home_ref_bill_id=None, charge_basis="not_applicable",
               billing_type="dual", payment_method=payment_method, credit_reason="not_applicable")
    return str({"status": "received", "home_bill_id": rid, "home_sub_id": home_sub_id, "amount": booked,
                "payment_method": payment_method, "bill_date": today, "billing_month": billing_month})

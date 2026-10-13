"""Hidden task tools of the universal_life_account_service difficulty (Ashgrove universal life).

Each tool performs one atomic write on an Ashgrove universal life policy with the figure the agent
has already worked out from the published rules; no tool checks eligibility, prerequisites or
amounts, and none computes a value on the caller's behalf.
"""

from erlbench import ToolContext, tool


@tool(owner="agent", rw="write")
def settle_loan_interest_b95e2dd6(ctx: ToolContext, ul_policy_id: str, interest_amount: float) -> str:
    """Record the owner's cash settlement of the loan interest accrued on an Ashgrove universal life
    policy loan. One call books one loan-repayment entry in the policy's activity history that pays
    interest only (principal repaid 0.00, interest paid as given, paid by online bank payment on
    today's date) and moves the policy's loan interest paid-to date to today. The loan balance is
    not changed. Afterwards the policy shows the new paid-to date and the activity history shows the
    interest payment; the receipt carries the new entry's reference number.

    Args:
        ul_policy_id: Id class — the reference number of the universal life policy whose loan
            interest is being settled, read from the universal life policy lookup.
        interest_amount: Fixed-format class — the loan interest the owner pays in cash, in USD,
            2 decimal places, rounded half-up to the cent; it must be greater than zero.

    Returns:
        A dictionary rendered as text with: ul_txn_id (string, reference number of the new
        interest payment entry), ul_policy_id (string, the policy), interest_amount (number, USD
        with 2 decimal places, the interest booked), loan_interest_paid_to_date (string,
        YYYY-MM-DD, the new paid-to date), status (string "interest_settled" when the entry was
        booked).
    """
    today = ctx.now()[:10]
    rid = ctx.make_id("ulrp_", ul_policy_id, interest_amount)
    ctx.create("ul_transactions", rid, ul_txn_id=rid, ul_policy_id=ul_policy_id,
               event_type="ul_loan_repaid", transaction_date=today, amount=0.0,
               interest_amount=round(float(interest_amount), 2), payment_method="online_bank_payment")
    ctx.update("ul_holdings", ul_policy_id, loan_interest_paid_to_date=today)
    return str({"ul_txn_id": rid, "ul_policy_id": ul_policy_id,
                "interest_amount": round(float(interest_amount), 2),
                "loan_interest_paid_to_date": today, "status": "interest_settled"})


@tool(owner="agent", rw="write")
def assess_overloan_charge_72382565(ctx: ToolContext, ul_policy_id: str, overloan_charge: float) -> str:
    """Book the one-time overloan protection charge on an Ashgrove universal life policy. One call
    adds one overloan protection charge entry, dated today, to the policy's activity history with
    the charge as given; the entry is what the policy's account value is reduced by when the rider
    is carried out. Nothing else on the policy changes. The receipt carries the new entry's
    reference number and the amount booked.

    Args:
        ul_policy_id: Id class — the reference number of the universal life policy the charge is
            booked on, read from the universal life policy lookup.
        overloan_charge: Fixed-format class — the overloan protection charge to deduct, in USD,
            2 decimal places, rounded half-up to the cent; it must be greater than zero.

    Returns:
        A dictionary rendered as text with: ul_txn_id (string, reference number of the charge
        entry), ul_policy_id (string, the policy), overloan_charge (number, USD with 2 decimal
        places, the charge booked), transaction_date (string, YYYY-MM-DD, today), status (string
        "charge_booked" when the entry was added).
    """
    today = ctx.now()[:10]
    rid = ctx.make_id("ulop_", ul_policy_id, overloan_charge)
    ctx.create("ul_transactions", rid, ul_txn_id=rid, ul_policy_id=ul_policy_id,
               event_type="ul_overloan_protection_charged", transaction_date=today,
               amount=round(float(overloan_charge), 2))
    return str({"ul_txn_id": rid, "ul_policy_id": ul_policy_id,
                "overloan_charge": round(float(overloan_charge), 2),
                "transaction_date": today, "status": "charge_booked"})


@tool(owner="user", rw="write")
def exercise_overloan_protection_1091dc6b(ctx: ToolContext, ul_policy_id: str, ul_request_id: str,
                                          protected_face_amount: float) -> str:
    """The policy owner carries out their own approved overloan protection election on their
    Ashgrove universal life policy by confirming the protected face shown to them. One call turns
    the policy into overloan-protected paid-up coverage: the policy status becomes
    overloan_protected, the death benefit option becomes A, the face amount becomes the confirmed
    protected face, and the election request is marked completed. The election cannot be undone;
    afterwards the policy no longer accepts premiums, withdrawals or new loans. The receipt shows
    the new status and face amount.

    Args:
        ul_policy_id: Id class — the reference number of the owner's universal life policy, read
            from the universal life policy lookup.
        ul_request_id: Id class — the reference number of the owner's approved overloan protection
            election request, read from the universal life service request lookup.
        protected_face_amount: Fixed-format class — the protected face the owner confirms, in USD,
            2 decimal places, rounded half-up to the cent.

    Returns:
        A dictionary rendered as text with: ul_policy_id (string, the policy), ul_request_id
        (string, the election carried out), status (string, "overloan_protected" once carried
        out), death_benefit_option (string, "A"), face_amount (number, USD with 2 decimal places,
        the protected face now in force).
    """
    ctx.update("ul_holdings", ul_policy_id, status="overloan_protected", death_benefit_option="A",
               face_amount=round(float(protected_face_amount), 2))
    ctx.update("ul_service_requests", ul_request_id, request_status="completed",
               decision_date=ctx.now()[:10])
    return str({"ul_policy_id": ul_policy_id, "ul_request_id": ul_request_id,
                "status": "overloan_protected", "death_benefit_option": "A",
                "face_amount": round(float(protected_face_amount), 2)})


@tool(owner="agent", rw="write")
def assess_surrender_charge_840d0421(ctx: ToolContext, ul_policy_id: str, ul_request_id: str,
                                     surrender_charge: float) -> str:
    """Book the full-surrender charge on an Ashgrove universal life policy being surrendered. One
    call adds one surrender charge entry, dated today, to the policy's activity history with the
    reason full_surrender, tied to the owner's surrender request and carrying the charge as given;
    nothing else on the policy changes. The receipt carries the new entry's reference number and
    the amount booked.

    Args:
        ul_policy_id: Id class — the reference number of the universal life policy being
            surrendered, read from the universal life policy lookup.
        ul_request_id: Id class — the reference number of the owner's surrender request the charge
            belongs to, read from the universal life service request lookup.
        surrender_charge: Fixed-format class — the full-surrender charge to deduct, in USD,
            2 decimal places, rounded half-up to the cent; zero or greater.

    Returns:
        A dictionary rendered as text with: ul_txn_id (string, reference number of the charge
        entry), ul_policy_id (string, the policy), ul_request_id (string, the surrender request),
        surrender_charge (number, USD with 2 decimal places, the charge booked), status (string
        "charge_booked" when the entry was added).
    """
    rid = ctx.make_id("ulsc_", ul_policy_id, ul_request_id, surrender_charge)
    ctx.create("ul_transactions", rid, ul_txn_id=rid, ul_policy_id=ul_policy_id,
               event_type="ul_surrender_charge_assessed", transaction_date=ctx.now()[:10],
               amount=round(float(surrender_charge), 2), charge_reason="full_surrender",
               ul_request_id=ul_request_id)
    return str({"ul_txn_id": rid, "ul_policy_id": ul_policy_id, "ul_request_id": ul_request_id,
                "surrender_charge": round(float(surrender_charge), 2), "status": "charge_booked"})


@tool(owner="agent", rw="write")
def refund_guideline_excess_434d2811(ctx: ToolContext, ul_policy_id: str, source_txn_id: str,
                                     refund_amount: float) -> str:
    """Return to the payer the part of a premium payment that took an Ashgrove universal life
    policy over its guideline premium limit. One call adds one premium refund entry, dated today,
    to the policy's activity history with the reason guideline_excess, tied to the premium payment
    being partly returned and carrying the refund as given (the excess plus any earnings on it).
    Nothing else on the policy changes. The receipt carries the refund entry's reference number.

    Args:
        ul_policy_id: Id class — the reference number of the universal life policy, read from the
            universal life policy lookup.
        source_txn_id: Id class — the reference number of the premium payment entry being partly
            refunded, read from the universal life activity lookup.
        refund_amount: Fixed-format class — the total refunded, in USD, 2 decimal places, rounded
            half-up to the cent; greater than zero.

    Returns:
        A dictionary rendered as text with: ul_txn_id (string, reference number of the refund
        entry), ul_policy_id (string, the policy), source_txn_id (string, the premium payment
        refunded against), refund_amount (number, USD with 2 decimal places), refund_reason
        (string "guideline_excess"), status (string "refund_booked" when the entry was added).
    """
    rid = ctx.make_id("ulrf_", ul_policy_id, source_txn_id, refund_amount)
    ctx.create("ul_transactions", rid, ul_txn_id=rid, ul_policy_id=ul_policy_id,
               event_type="ul_premium_refunded", transaction_date=ctx.now()[:10],
               amount=round(float(refund_amount), 2), refund_reason="guideline_excess",
               source_txn_id=source_txn_id)
    return str({"ul_txn_id": rid, "ul_policy_id": ul_policy_id, "source_txn_id": source_txn_id,
                "refund_amount": round(float(refund_amount), 2), "refund_reason": "guideline_excess",
                "status": "refund_booked"})


@tool(owner="user", rw="write")
def surrender_policy_65d610d4(ctx: ToolContext, ul_policy_id: str, ul_request_id: str,
                              surrender_effective_date: str, net_paid_amount: float) -> str:
    """The policy owner completes the full surrender of their own Ashgrove universal life policy on
    their signed surrender request by confirming the net amount to be paid to them. One call ends
    the policy: its status becomes surrendered with the termination date set to the surrender's
    effective date, the surrender request is marked completed, and one surrender payment entry,
    dated today and paid by direct deposit, is added to the activity history with the confirmed
    net amount. The surrender cannot be undone. The receipt shows the new status and the amount
    paid.

    Args:
        ul_policy_id: Id class — the reference number of the owner's universal life policy, read
            from the universal life policy lookup.
        ul_request_id: Id class — the reference number of the owner's surrender request, read from
            the universal life service request lookup.
        surrender_effective_date: Fixed-format class — the date the surrender takes effect, the
            date the signed surrender request was received, as YYYY-MM-DD (calendar date, no time
            zone).
        net_paid_amount: Fixed-format class — the net amount paid to the owner, in USD,
            2 decimal places, rounded half-up to the cent.

    Returns:
        A dictionary rendered as text with: ul_txn_id (string, reference number of the surrender
        payment entry), ul_policy_id (string, the policy), status (string, "surrendered" once
        completed), termination_date (string, YYYY-MM-DD, the effective date), net_paid_amount
        (number, USD with 2 decimal places, the amount paid).
    """
    rid = ctx.make_id("ulsv_", ul_policy_id, ul_request_id, surrender_effective_date, net_paid_amount)
    ctx.update("ul_holdings", ul_policy_id, status="surrendered", termination_date=surrender_effective_date)
    ctx.update("ul_service_requests", ul_request_id, request_status="completed", decision_date=ctx.now()[:10])
    ctx.create("ul_transactions", rid, ul_txn_id=rid, ul_policy_id=ul_policy_id,
               event_type="ul_surrender_value_paid", transaction_date=ctx.now()[:10],
               net_paid_amount=round(float(net_paid_amount), 2), ul_request_id=ul_request_id,
               payout_method="direct_deposit")
    return str({"ul_txn_id": rid, "ul_policy_id": ul_policy_id, "status": "surrendered",
                "termination_date": surrender_effective_date,
                "net_paid_amount": round(float(net_paid_amount), 2)})

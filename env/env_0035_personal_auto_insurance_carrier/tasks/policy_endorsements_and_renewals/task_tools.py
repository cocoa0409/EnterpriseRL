"""Hidden task tools of the policy_endorsements_and_renewals difficulty (category auto).

Each tool is named by exactly one extended policy's target_tool in auto.extended.yaml and is
reached through the unlock/call meta tools. Every tool lands one business change as declared;
none of them checks eligibility, order, prerequisites or amounts — those are the agent's to decide
from the published policy and the records.
"""

from erlbench import ToolContext, tool



@tool(owner="agent", rw="write")
def book_vehicle_addition_premium_9393c661(ctx: ToolContext, addition_transaction_id: str,
                                          additional_premium: float) -> str:
    """Book the additional premium that belongs to a vehicle addition recorded on an auto
    policy. One call writes one additional premium entry for the amount given, tied to that vehicle
    addition (same policy, same vehicle, the addition's effective date and its full-term premiums
    before and after) and to the policy's current term. The policy's written premium for the term
    goes up by the amount, and the addition now shows its own additional premium entry in the
    transaction history.

    Args:
        addition_transaction_id: Id class — the reference number of the vehicle addition entry in
            the policy's transaction history, as returned by the auto transaction lookup.
        additional_premium: Fixed-format class — the additional premium to book, in USD, 2 decimal
            places, positive; the value is stored rounded half up to 2 decimal places.

    Returns:
        A text receipt holding a dictionary with additional_premium_transaction_id (reference
        number of the new entry), addition_transaction_id, policy_id, vehicle_id, effective_date
        (YYYY-MM-DD, the addition's effective date), additional_premium (USD, 2 decimal places)
        and status, which reads "booked" when the entry was written.
    """
    rows = ctx.find("auto_transactions", transaction_id=addition_transaction_id)
    add = rows[0] if rows else {}
    pol = (ctx.find("auto_policies", policy_id=add.get("policy_id", "")) or [{}])[0]
    amount = round(float(additional_premium), 2)
    aid = ctx.make_id("atx_", "vehicle_add_ap", addition_transaction_id, amount)
    ctx.create("auto_transactions", aid, transaction_id=aid, policy_id=add.get("policy_id", ""),
               customer_id=add.get("customer_id", ""), event_type="auto_additional_premium",
               vehicle_id=add.get("vehicle_id", ""), source_transaction_id=addition_transaction_id,
               effective_date=add.get("effective_date", ""),
               full_term_premium_before=add.get("full_term_premium_before"),
               full_term_premium_after=add.get("full_term_premium_after"), premium_amount=amount,
               reason_code=add.get("reason_code", ""),
               term_effective_date=pol.get("term_effective_date", ""), recorded_date=ctx.now()[:10])
    return str({"additional_premium_transaction_id": aid, "addition_transaction_id": addition_transaction_id,
                "policy_id": add.get("policy_id", ""), "vehicle_id": add.get("vehicle_id", ""),
                "effective_date": add.get("effective_date", ""), "additional_premium": amount,
                "status": "booked"})


@tool(owner="agent", rw="write")
def book_vehicle_removal_credit_524db3a4(ctx: ToolContext, removal_transaction_id: str,
                                        return_premium: float) -> str:
    """Book the return premium that belongs to a vehicle removal recorded on an auto
    policy. One call writes one return premium entry for the amount given, tied to that removal
    (same policy, same effective date and same removal reason) and to the policy's current term.
    The policy's written premium for the term goes down by the amount, and the removal now shows
    its own return premium entry in the transaction history.

    Args:
        removal_transaction_id: Id class — the reference number of the vehicle removal entry in
            the policy's transaction history, as returned by the auto transaction lookup.
        return_premium: Fixed-format class — the credit to book, in USD, 2 decimal places,
            positive; the value is stored rounded half up to 2 decimal places.

    Returns:
        A text receipt holding a dictionary with return_premium_transaction_id (reference number
        of the new return premium entry), removal_transaction_id, policy_id, effective_date
        (YYYY-MM-DD, the removal's effective date), return_premium (USD, 2 decimal places) and
        status, which reads "booked" when the entry was written.
    """
    rows = ctx.find("auto_transactions", transaction_id=removal_transaction_id)
    rem = rows[0] if rows else {}
    pol = (ctx.find("auto_policies", policy_id=rem.get("policy_id", "")) or [{}])[0]
    amount = round(float(return_premium), 2)
    rid = ctx.make_id("atx_", "removal_rp", removal_transaction_id, amount)
    ctx.create("auto_transactions", rid, transaction_id=rid, policy_id=rem.get("policy_id", ""),
               customer_id=rem.get("customer_id", ""), event_type="auto_return_premium",
               vehicle_id=rem.get("vehicle_id", ""), source_transaction_id=removal_transaction_id,
               effective_date=rem.get("effective_date", ""), premium_amount=amount,
               reason_code=rem.get("reason_code", ""),
               term_effective_date=pol.get("term_effective_date", ""),
               recorded_date=ctx.now()[:10])
    return str({"return_premium_transaction_id": rid, "removal_transaction_id": removal_transaction_id,
                "policy_id": rem.get("policy_id", ""), "effective_date": rem.get("effective_date", ""),
                "return_premium": amount, "status": "booked"})


@tool(owner="user", rw="write")
def sign_cancellation_request_695fb1aa(ctx: ToolContext, request_id: str,
                                       cancellation_effective_date: str,
                                       return_premium: float) -> str:
    """Sign, as the named insured, a cancellation request recorded on your auto policy. Signing
    carries out the cancellation: the request is marked signed today, the policy is cancelled at
    your request on the cancellation effective date given, and the return premium you were
    quoted is credited to the policy as one return premium entry for the current term. On success
    the policy shows as cancelled with that end date, and the credit shows in its history.

    Args:
        request_id: Id class — the reference number of the cancellation request waiting for your
            signature, as given to you by the representative from the change request lookup.
        cancellation_effective_date: Fixed-format class — the date the cancellation takes effect,
            format YYYY-MM-DD (calendar date, no time part), as given to you by the representative.
        return_premium: Fixed-format class — the return premium quoted to you for the
            cancellation, in USD, 2 decimal places, positive; the value is stored rounded half up
            to 2 decimal places.

    Returns:
        A text receipt holding a dictionary with request_id, request_status ("signed"),
        signed_date (YYYY-MM-DD, today), policy_id, policy_status ("cancelled"),
        cancellation_effective_date (YYYY-MM-DD),
        return_premium_transaction_id (reference number of the credit entry) and return_premium
        (USD, 2 decimal places); request_status "signed" with policy_status "cancelled" means the
        cancellation went through.
    """
    rows = ctx.find("auto_change_requests", request_id=request_id)
    req = rows[0] if rows else {}
    policy_id = req.get("policy_id", "")
    pol = (ctx.find("auto_policies", policy_id=policy_id) or [{}])[0]
    end = cancellation_effective_date
    today = ctx.now()[:10]
    amount = round(float(return_premium), 2)
    ctx.update("auto_change_requests", request_id, request_status="signed", signed_date=today)
    ctx.update("auto_policies", policy_id, status="cancelled", end_date=end,
               end_reason="insured_request")
    rid = ctx.make_id("atx_", "cancel_rp", policy_id, end, amount)
    ctx.create("auto_transactions", rid, transaction_id=rid, policy_id=policy_id,
               customer_id=req.get("customer_id", ""), event_type="auto_return_premium",
               source_transaction_id="", effective_date=end, premium_amount=amount,
               reason_code="insured_requested",
               term_effective_date=pol.get("term_effective_date", ""), recorded_date=today)
    return str({"request_id": request_id, "request_status": "signed", "signed_date": today,
                "policy_id": policy_id, "policy_status": "cancelled",
                "cancellation_effective_date": end, "return_premium_transaction_id": rid,
                "return_premium": amount})


@tool(owner="agent", rw="write")
def book_driver_addition_premium_cd2c8cbf(ctx: ToolContext, addition_transaction_id: str,
                                         additional_premium: float) -> str:
    """Book the additional premium that belongs to a driver addition recorded on an auto
    policy. One call writes one additional premium entry for the amount given, tied to that driver
    addition (same policy, same driver, the addition's effective date and its full-term premiums
    before and after) and to the policy's current term. The policy's written premium for the term
    goes up by the amount, and the addition now shows its own additional premium entry in the
    transaction history.

    Args:
        addition_transaction_id: Id class — the reference number of the driver addition entry in
            the policy's transaction history, as returned by the auto transaction lookup.
        additional_premium: Fixed-format class — the additional premium to book, in USD, 2 decimal
            places, positive; the value is stored rounded half up to 2 decimal places.

    Returns:
        A text receipt holding a dictionary with additional_premium_transaction_id (reference
        number of the new entry), addition_transaction_id, policy_id, driver_id, effective_date
        (YYYY-MM-DD, the addition's effective date), additional_premium (USD, 2 decimal places)
        and status, which reads "booked" when the entry was written.
    """
    rows = ctx.find("auto_transactions", transaction_id=addition_transaction_id)
    add = rows[0] if rows else {}
    pol = (ctx.find("auto_policies", policy_id=add.get("policy_id", "")) or [{}])[0]
    amount = round(float(additional_premium), 2)
    aid = ctx.make_id("atx_", "driver_add_ap", addition_transaction_id, amount)
    ctx.create("auto_transactions", aid, transaction_id=aid, policy_id=add.get("policy_id", ""),
               customer_id=add.get("customer_id", ""), event_type="auto_additional_premium",
               driver_id=add.get("driver_id", ""), source_transaction_id=addition_transaction_id,
               effective_date=add.get("effective_date", ""),
               full_term_premium_before=add.get("full_term_premium_before"),
               full_term_premium_after=add.get("full_term_premium_after"), premium_amount=amount,
               reason_code=add.get("reason_code", ""),
               term_effective_date=pol.get("term_effective_date", ""), recorded_date=ctx.now()[:10])
    return str({"additional_premium_transaction_id": aid, "addition_transaction_id": addition_transaction_id,
                "policy_id": add.get("policy_id", ""), "driver_id": add.get("driver_id", ""),
                "effective_date": add.get("effective_date", ""), "additional_premium": amount,
                "status": "booked"})


@tool(owner="user", rw="write")
def sign_named_driver_exclusion_c094ed6f(ctx: ToolContext, request_id: str, policy_id: str,
                                        effective_date: str, return_premium: float) -> str:
    """Sign, as the named insured, the named driver exclusion form recorded for a household member
    on your auto policy. Signing carries out the exclusion: the form is marked signed today, the
    named driver exclusion endorsement is written for that household member from the effective
    date given, and the return premium you were quoted is credited to the policy as one return
    premium entry for the current term. On success the household member shows as excluded in the
    policy's history and the credit shows beside it.

    Args:
        request_id: Id class — the reference number of the named driver exclusion form waiting for
            your signature, as given to you by the representative from the change request lookup.
        policy_id: Id class — the reference number of your auto policy the form belongs to, as
            given to you by the representative from the auto policy lookup.
        effective_date: Fixed-format class — the date the exclusion takes effect, format
            YYYY-MM-DD (calendar date, no time part), as given to you by the representative.
        return_premium: Fixed-format class — the return premium quoted to you for the exclusion,
            in USD, 2 decimal places, positive; the value is stored rounded half up to 2 decimal
            places.

    Returns:
        A text receipt holding a dictionary with request_id, request_status ("signed"),
        signed_date (YYYY-MM-DD, today), exclusion_transaction_id (reference number of the
        exclusion endorsement), driver_id, effective_date (YYYY-MM-DD),
        return_premium_transaction_id (reference number of the credit entry) and return_premium
        (USD, 2 decimal places); request_status "signed" with an exclusion_transaction_id means
        the exclusion is in place.
    """
    rows = ctx.find("auto_change_requests", request_id=request_id)
    req = rows[0] if rows else {}
    pol = (ctx.find("auto_policies", policy_id=policy_id) or [{}])[0]
    today = ctx.now()[:10]
    amount = round(float(return_premium), 2)
    ctx.update("auto_change_requests", request_id, request_status="signed", signed_date=today)
    xid = ctx.make_id("atx_", "driver_exclude", request_id, policy_id, effective_date)
    ctx.create("auto_transactions", xid, transaction_id=xid, policy_id=policy_id,
               customer_id=req.get("customer_id", ""), event_type="auto_driver_exclude",
               driver_id=req.get("driver_id", ""), request_id=request_id, effective_date=effective_date,
               premium_effect="return", reason_code="named_driver_exclusion",
               term_effective_date=pol.get("term_effective_date", ""), recorded_date=today)
    rid = ctx.make_id("atx_", "driver_exclude_rp", xid, amount)
    ctx.create("auto_transactions", rid, transaction_id=rid, policy_id=policy_id,
               customer_id=req.get("customer_id", ""), event_type="auto_return_premium",
               driver_id=req.get("driver_id", ""), source_transaction_id=xid, effective_date=effective_date,
               premium_amount=amount, reason_code="named_driver_exclusion",
               term_effective_date=pol.get("term_effective_date", ""), recorded_date=today)
    return str({"request_id": request_id, "request_status": "signed", "signed_date": today,
                "exclusion_transaction_id": xid, "driver_id": req.get("driver_id", ""),
                "effective_date": effective_date, "return_premium_transaction_id": rid,
                "return_premium": amount})

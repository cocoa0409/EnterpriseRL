"""Hidden task tools of the private_homeflood_rating_billing difficulty (HomeFlood rating and billing).

Each tool performs one atomic servicing write on a HomeFlood policy. No tool judges eligibility,
prerequisites or amounts: the values are worked out by the caller from the HomeFlood rules and passed in.
"""

from erlbench import ToolContext, tool


class _Calendar:
    """Pure calendar arithmetic on 'YYYY-MM-DD' strings (no clock, no libraries)."""

    @staticmethod
    def same_day_next_year(day: str) -> str:
        y, m, d = (int(p) for p in str(day)[:10].split("-"))
        y += 1
        leap = (y % 4 == 0 and y % 100 != 0) or y % 400 == 0
        if m == 2 and d == 29 and not leap:
            d = 28
        return f"{y:04d}-{m:02d}-{d:02d}"


@tool(owner="agent", rw="write")
def apply_certificate_review_8d563756(ctx: ToolContext, homeflood_policy_id: str, homeflood_change_id: str,
                                      revised_term_premium: float, credits_applied_pct: int,
                                      ec_applied: bool) -> str:
    """Complete the review of an Elevation Certificate received on a HomeFlood policy. The certificate
    entry is updated with the re-rated full-term premium and with whether the certificate is applied to
    the current term. When it is applied, the policy itself starts rating on the certificate: its
    certificate-on-file flag is set, the elevation difference and the certified flood openings are taken
    from the certificate entry, and the credit percent and the full-term premium are replaced by the
    values given; the certificate then takes effect from the date it was received. When it is not
    applied, only the certificate entry changes and it is held for the rating of the next term, taking
    effect on the current term's end date. No premium item, credit or payment is booked by this action.
    Success is shown by a receipt carrying the certificate entry and the values now recorded.

    Args:
        homeflood_policy_id: Id class — the reference number of the HomeFlood policy the certificate was received on, as returned by the HomeFlood policy lookup.
        homeflood_change_id: Id class — the reference number of the Elevation Certificate entry being reviewed, as returned by the HomeFlood servicing-document lookup for that policy.
        revised_term_premium: Fixed-format class — the full-term premium of the current term re-rated with the certificate, in USD, 2 decimal places, already rounded to the cent by the caller.
        credits_applied_pct: Fixed-format class — the total credit percent the re-rating used after the cap, in whole percent, an integer from 0 upward; it is written to the policy only when the certificate is applied.
        ec_applied: Enum class — true when the re-rated full-term premium is lower than the full-term premium in force, so the certificate is applied to the current term; false when it is not lower, so the certificate is kept on file for the next term's rating.

    Returns:
        A dict receipt: "status" is "certificate_review_recorded" on success; "homeflood_change_id" is the
        certificate entry reviewed; "ec_applied" is the boolean recorded; "change_effective_date" is the
        date (YYYY-MM-DD) the certificate takes effect; "revised_term_premium" is the re-rated full-term
        premium recorded (USD, 2 decimals); "policy_term_premium" is the full-term premium the policy now
        shows (USD, 2 decimals). A dict with "status" "not_found" is returned when the entry or the policy
        does not exist.
    """
    entries = ctx.find("homeflood_changes", homeflood_change_id=homeflood_change_id)
    policies = ctx.find("homeflood_policies", homeflood_policy_id=homeflood_policy_id)
    if not entries or not policies:
        return str({"status": "not_found", "homeflood_change_id": homeflood_change_id})
    entry, pol = entries[0], policies[0]
    amount = round(float(revised_term_premium), 2)
    effective = entry.get("recorded_date") if ec_applied else pol.get("term_end")
    ctx.update("homeflood_changes", homeflood_change_id, revised_term_premium=amount,
               ec_applied=bool(ec_applied), change_effective_date=effective)
    if ec_applied:
        ctx.update("homeflood_policies", homeflood_policy_id, ec_on_file=True,
                   elevation_difference_ft=entry.get("ec_elevation_difference_ft"),
                   flood_openings_certified=entry.get("ec_flood_openings"),
                   credits_applied_pct=int(credits_applied_pct), term_premium=amount)
    shown = amount if ec_applied else pol.get("term_premium")
    return str({"status": "certificate_review_recorded", "homeflood_change_id": homeflood_change_id,
                "ec_applied": bool(ec_applied), "change_effective_date": effective,
                "revised_term_premium": amount, "policy_term_premium": shown})


@tool(owner="agent", rw="write")
def book_rerate_credit_70dc8da2(ctx: ToolContext, homeflood_policy_id: str, homeflood_change_id: str,
                                credit_amount: float) -> str:
    """Book the premium credit owed on a HomeFlood policy because an applied Elevation Certificate
    lowered the term's premium. One credit entry of the term premium item is posted today to the term the
    policy currently shows, with the charge basis RERATE and the certificate entry as its reference, and
    the policy's premium balance is lowered by the amount. Nothing is paid out by this action; the credit
    stays on the account. Success is shown by a receipt carrying the new credit entry.

    Args:
        homeflood_policy_id: Id class — the reference number of the HomeFlood policy, as returned by the HomeFlood policy lookup.
        homeflood_change_id: Id class — the reference number of the applied Elevation Certificate entry the credit rests on, as returned by the HomeFlood servicing-document lookup.
        credit_amount: Fixed-format class — the credit to post, in USD, 2 decimal places, a positive amount already rounded to the cent by the caller.

    Returns:
        A dict receipt: "status" is "rerate_credit_booked" on success; "homeflood_billing_id" is the new
        credit entry; "term_start" is the term (YYYY-MM-DD) it is posted to; "amount" is the credit (USD,
        2 decimals); "premium_balance" is the policy's balance after the credit (USD, 2 decimals, negative
        meaning money held for the payor). A dict with "status" "not_found" and "homeflood_policy_id" (the reference
        given) is returned when the policy does not exist.
    """
    policies = ctx.find("homeflood_policies", homeflood_policy_id=homeflood_policy_id)
    if not policies:
        return str({"status": "not_found", "homeflood_policy_id": homeflood_policy_id})
    pol = policies[0]
    amount = round(float(credit_amount), 2)
    rid = ctx.make_id("hfb_", homeflood_policy_id, homeflood_change_id, credit_amount)
    ctx.create("homeflood_billing", rid, homeflood_billing_id=rid, homeflood_policy_id=homeflood_policy_id,
               customer_id=pol.get("customer_id"), event_type="homeflood_premium_credit",
               term_start=pol.get("term_start"), component="TERM_PREMIUM", charge_basis="RERATE",
               amount=amount, posted_date=ctx.now()[:10], reference_id=homeflood_change_id,
               installment_number=0, payment_ref="", payment_method="NONE", payee="NONE")
    balance = round(float(pol.get("premium_balance") or 0) - amount, 2)
    ctx.update("homeflood_policies", homeflood_policy_id, premium_balance=balance)
    return str({"status": "rerate_credit_booked", "homeflood_billing_id": rid, "term_start": pol.get("term_start"),
                "amount": amount, "premium_balance": balance})


@tool(owner="agent", rw="write")
def book_renewal_term_27983a73(ctx: ToolContext, homeflood_policy_id: str, renewal_term_premium: float,
                               policy_fee: float) -> str:
    """Book the renewal of a HomeFlood policy as its next term. The policy moves to the new term, which
    runs from the end date of the term it currently shows to the same calendar date one year later, and
    shows the renewal term premium given. Two premium items are posted today to the new term with the
    charge basis RENEWAL — the term premium and the policy fee — and the policy's premium balance rises by
    both. Payments already received for the new term stay where they are. Success is shown by a receipt
    carrying the new term dates and the two premium items.

    Args:
        homeflood_policy_id: Id class — the reference number of the HomeFlood policy being renewed, as returned by the HomeFlood policy lookup.
        renewal_term_premium: Fixed-format class — the full-term premium of the renewal term, in USD, 2 decimal places, already rounded to the cent by the caller.
        policy_fee: Fixed-format class — the annual policy fee booked for the renewal term, in USD, 2 decimal places.

    Returns:
        A dict receipt: "status" is "renewal_booked" on success; "term_start" and "term_end" are the new
        term's dates (YYYY-MM-DD); "term_premium_billing_id" and "policy_fee_billing_id" are the two new
        premium items; "term_premium" and "policy_fee" are the amounts booked (USD, 2 decimals);
        "premium_balance" is the policy's balance afterwards (USD, 2 decimals). A dict with "status"
        "not_found" and "homeflood_policy_id" (the reference given) is returned when the policy does not exist.
    """
    policies = ctx.find("homeflood_policies", homeflood_policy_id=homeflood_policy_id)
    if not policies:
        return str({"status": "not_found", "homeflood_policy_id": homeflood_policy_id})
    pol = policies[0]
    start = pol.get("term_end")
    end = _Calendar.same_day_next_year(start)
    premium = round(float(renewal_term_premium), 2)
    fee = round(float(policy_fee), 2)
    today = ctx.now()[:10]
    tid = ctx.make_id("hfb_", homeflood_policy_id, start, "TERM_PREMIUM", renewal_term_premium)
    fid = ctx.make_id("hfb_", homeflood_policy_id, start, "POLICY_FEE", policy_fee)
    ctx.create("homeflood_billing", tid, homeflood_billing_id=tid, homeflood_policy_id=homeflood_policy_id,
               customer_id=pol.get("customer_id"), event_type="homeflood_premium_charged", term_start=start,
               component="TERM_PREMIUM", charge_basis="RENEWAL", amount=premium, posted_date=today,
               reference_id="", installment_number=0, payment_ref="", payment_method="NONE", payee="NONE")
    ctx.create("homeflood_billing", fid, homeflood_billing_id=fid, homeflood_policy_id=homeflood_policy_id,
               customer_id=pol.get("customer_id"), event_type="homeflood_premium_charged", term_start=start,
               component="POLICY_FEE", charge_basis="RENEWAL", amount=fee, posted_date=today,
               reference_id="", installment_number=0, payment_ref="", payment_method="NONE", payee="NONE")
    balance = round(float(pol.get("premium_balance") or 0) + premium + fee, 2)
    ctx.update("homeflood_policies", homeflood_policy_id, term_start=start, term_end=end,
               term_premium=premium, premium_balance=balance)
    return str({"status": "renewal_booked", "term_start": start, "term_end": end,
                "term_premium_billing_id": tid, "policy_fee_billing_id": fid, "term_premium": premium,
                "policy_fee": fee, "premium_balance": balance})


@tool(owner="user", rw="write")
def pay_installment_4d782e9d(ctx: ToolContext, homeflood_policy_id: str, amount: float, installment_number: int,
                             payment_method: str) -> str:
    """The policyholder pays an installment of their HomeFlood premium. The payment is received today and
    applied to the term the policy currently shows, under the installment number given, and the policy's
    premium balance is lowered by the amount. A payment reference is issued for the payment at the moment
    it is made. Success is shown by a receipt carrying that reference and the payment entry.

    Args:
        homeflood_policy_id: Id class — the reference number of the HomeFlood policy being paid, as returned by the HomeFlood policy lookup and passed on by the agent.
        amount: Fixed-format class — the amount paid, in USD, 2 decimal places, a positive amount rounded to the cent.
        installment_number: Fixed-format class — the installment of the term this payment settles, an integer (1 for the down or annual payment, 2 and up for later installments).
        payment_method: Enum class — ACH when the policyholder pays from a bank account by electronic transfer; CHECK when they pay by paper check; CREDIT_CARD when they pay by credit or debit card; ESCROW_DISBURSEMENT when a mortgage lender pays out of the policyholder's escrow account; NONE is never used for a payment and stands only for entries that are not payments.

    Returns:
        A dict receipt: "status" is "payment_received" on success; "homeflood_billing_id" is the new
        payment entry; "payment_ref" is the reference issued for the payment; "term_start" is the term
        (YYYY-MM-DD) it is applied to; "installment_number" is the installment settled (integer);
        "amount" is the amount received (USD, 2 decimals); "premium_balance" is the policy's balance
        afterwards (USD, 2 decimals). A dict with "status" "not_found" and "homeflood_policy_id" (the reference
        given) is returned when the policy does not exist.
    """
    policies = ctx.find("homeflood_policies", homeflood_policy_id=homeflood_policy_id)
    if not policies:
        return str({"status": "not_found", "homeflood_policy_id": homeflood_policy_id})
    pol = policies[0]
    paid = round(float(amount), 2)
    rid = ctx.make_id("hfb_", homeflood_policy_id, amount, installment_number, payment_method)
    ref = "TM3" + rid[-8:].upper()
    ctx.create("homeflood_billing", rid, homeflood_billing_id=rid, homeflood_policy_id=homeflood_policy_id,
               customer_id=pol.get("customer_id"), event_type="homeflood_premium_payment",
               term_start=pol.get("term_start"), component="TOTAL", charge_basis="PAYMENT", amount=paid,
               posted_date=ctx.now()[:10], reference_id="", installment_number=int(installment_number),
               payment_ref=ref, payment_method=payment_method, payee="NONE")
    balance = round(float(pol.get("premium_balance") or 0) - paid, 2)
    ctx.update("homeflood_policies", homeflood_policy_id, premium_balance=balance)
    return str({"status": "payment_received", "homeflood_billing_id": rid, "payment_ref": ref,
                "term_start": pol.get("term_start"), "installment_number": int(installment_number),
                "amount": paid, "premium_balance": balance})


@tool(owner="agent", rw="write")
def process_cancellation_request_bf9010ee(ctx: ToolContext, homeflood_policy_id: str, homeflood_request_id: str,
                                          credit_amount: float) -> str:
    """Process the named insured's signed cancellation request on a HomeFlood policy. The policy becomes
    cancelled, carrying the reason and the effective date stated on the request and today's date as the
    date it was closed, and one credit entry of the term premium item is posted today to the term the
    policy shows, with the charge basis CANCELLATION and the request as its reference; the policy's
    premium balance is lowered by the credit. No refund is paid out by this action. Success is shown by a
    receipt carrying the cancellation details and the credit entry.

    Args:
        homeflood_policy_id: Id class — the reference number of the HomeFlood policy being cancelled, as returned by the HomeFlood policy lookup.
        homeflood_request_id: Id class — the reference number of the signed cancellation request on file, as returned by the HomeFlood request lookup for that policy.
        credit_amount: Fixed-format class — the return of premium to credit, in USD, 2 decimal places, zero or more, already rounded to the cent by the caller.

    Returns:
        A dict receipt: "status" is "cancellation_processed" on success; "cancellation_reason" and
        "cancellation_effective_date" (YYYY-MM-DD) are copied from the request; "closed_date" is the
        processing date (YYYY-MM-DD); "homeflood_billing_id" is the credit entry; "amount" is the credit
        (USD, 2 decimals); "premium_balance" is the policy's balance afterwards (USD, 2 decimals, negative
        meaning money held for the payor). A dict with "status" "not_found" and "homeflood_policy_id" (the
        reference given) is returned when the policy or the request does not exist.
    """
    policies = ctx.find("homeflood_policies", homeflood_policy_id=homeflood_policy_id)
    requests = ctx.find("homeflood_requests", homeflood_request_id=homeflood_request_id)
    if not policies or not requests:
        return str({"status": "not_found", "homeflood_policy_id": homeflood_policy_id})
    pol, req = policies[0], requests[0]
    amount = round(float(credit_amount), 2)
    today = ctx.now()[:10]
    rid = ctx.make_id("hfb_", homeflood_policy_id, homeflood_request_id, credit_amount)
    ctx.create("homeflood_billing", rid, homeflood_billing_id=rid, homeflood_policy_id=homeflood_policy_id,
               customer_id=pol.get("customer_id"), event_type="homeflood_premium_credit",
               term_start=pol.get("term_start"), component="TERM_PREMIUM", charge_basis="CANCELLATION",
               amount=amount, posted_date=today, reference_id=homeflood_request_id, installment_number=0,
               payment_ref="", payment_method="NONE", payee="NONE")
    balance = round(float(pol.get("premium_balance") or 0) - amount, 2)
    ctx.update("homeflood_policies", homeflood_policy_id, status="cancelled",
               cancellation_reason=req.get("cancellation_reason"),
               cancellation_effective_date=req.get("requested_effective_date"), closed_date=today,
               premium_balance=balance)
    return str({"status": "cancellation_processed", "cancellation_reason": req.get("cancellation_reason"),
                "cancellation_effective_date": req.get("requested_effective_date"), "closed_date": today,
                "homeflood_billing_id": rid, "amount": amount, "premium_balance": balance})


@tool(owner="user", rw="write")
def pay_closing_balance_b53536cf(ctx: ToolContext, homeflood_policy_id: str, amount: float,
                                 payment_method: str) -> str:
    """The policyholder pays the amount that settles a closed HomeFlood policy. The payment is received
    today and applied to the term the policy shows, not to any single installment, and the closed policy's
    account is marked settled: its premium balance is set to zero, any late charge or courtesy that the
    amount already reflects being taken as settled with it. A payment reference is issued for the payment at the moment
    it is made. Success is shown by a receipt carrying that reference and the payment entry.

    Args:
        homeflood_policy_id: Id class — the reference number of the HomeFlood policy being settled, as returned by the HomeFlood policy lookup and passed on by the agent.
        amount: Fixed-format class — the amount paid, in USD, 2 decimal places, a positive amount rounded to the cent.
        payment_method: Enum class — ACH when the policyholder pays from a bank account by electronic transfer; CHECK when they pay by paper check; CREDIT_CARD when they pay by credit or debit card; ESCROW_DISBURSEMENT when a mortgage lender pays out of the policyholder's escrow account; NONE is never used for a payment and stands only for entries that are not payments.

    Returns:
        A dict receipt: "status" is "payment_received" on success; "homeflood_billing_id" is the new
        payment entry; "payment_ref" is the reference issued for the payment; "term_start" is the term
        (YYYY-MM-DD) it is applied to; "amount" is the amount received (USD, 2 decimals);
        "premium_balance" is the policy's balance afterwards, 0.0 once settled (USD, 2 decimals). A dict with
        "status" "not_found" and "homeflood_policy_id" (the reference given) is returned when the policy does not exist.
    """
    policies = ctx.find("homeflood_policies", homeflood_policy_id=homeflood_policy_id)
    if not policies:
        return str({"status": "not_found", "homeflood_policy_id": homeflood_policy_id})
    pol = policies[0]
    paid = round(float(amount), 2)
    rid = ctx.make_id("hfb_", homeflood_policy_id, amount, payment_method, "closing")
    ref = "TM3" + rid[-8:].upper()
    ctx.create("homeflood_billing", rid, homeflood_billing_id=rid, homeflood_policy_id=homeflood_policy_id,
               customer_id=pol.get("customer_id"), event_type="homeflood_premium_payment",
               term_start=pol.get("term_start"), component="TOTAL", charge_basis="PAYMENT", amount=paid,
               posted_date=ctx.now()[:10], reference_id="", installment_number=0, payment_ref=ref,
               payment_method=payment_method, payee="NONE")
    ctx.update("homeflood_policies", homeflood_policy_id, premium_balance=0.0)
    return str({"status": "payment_received", "homeflood_billing_id": rid, "payment_ref": ref,
                "term_start": pol.get("term_start"), "amount": paid, "premium_balance": 0.0})

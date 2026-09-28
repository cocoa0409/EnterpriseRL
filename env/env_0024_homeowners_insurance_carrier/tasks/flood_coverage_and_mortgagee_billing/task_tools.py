"""Hidden task tools of the flood_coverage_and_mortgagee_billing difficulty (FloodGuard Private Flood Policy).

Each tool lands one atomic business write on a FloodGuard policy with the values the caller hands it.
None of them checks eligibility, ordering or amounts: every such judgement belongs to the agent.
"""

from erlbench import ToolContext, tool


# Named insured of a policy record, copied onto every premium account entry the tools post.
_customer_of = lambda ctx, flood_policy_id: next(
    (row.get("customer_id", "") for row in ctx.find("flood_policies", flood_policy_id=flood_policy_id)), "")


@tool(owner="agent", rw="write")
def record_flood_renewal_offer_81f1ff73(ctx: ToolContext, flood_policy_id: str, indicated_renewal_premium: float) -> str:
    """Record the renewal offer on one FloodGuard flood policy: the indicated premium the policy will carry for its
    upcoming twelve-month term is written onto the policy, where it is shown as the policy's indicated renewal
    premium. Nothing is billed and no other figure on the policy changes. The
    receipt echoes the policy reference and the indicated premium now on file; a receipt with status
    renewal_offer_recorded means the offer is on the policy.

    Args:
        flood_policy_id: Id class — the reference number of the FloodGuard flood policy record being offered for
            renewal, as returned by the flood policy lookup for the verified caller.
        indicated_renewal_premium: Fixed-format class — the indicated annual premium for the upcoming term,
            excluding the policy fee, in USD as a plain number with 2 decimal places (for example 1234.50); the
            value is stored rounded half-up to 2 decimal places.

    Returns:
        A dictionary rendered as text with: flood_policy_id (the policy reference number written to),
        indicated_renewal_premium (the premium now on file, USD with 2 decimal places) and status (the text
        renewal_offer_recorded, meaning the offer was written).
    """
    value = round(float(indicated_renewal_premium), 2)
    ctx.update("flood_policies", flood_policy_id, indicated_renewal_premium=value)
    return str({"flood_policy_id": flood_policy_id, "indicated_renewal_premium": value,
                "status": "renewal_offer_recorded"})


@tool(owner="agent", rw="write")
def renew_flood_policy_8cc307a9(ctx: ToolContext, flood_policy_id: str, new_effective_date: str,
                                new_expiration_date: str, term_premium: float, policy_fee: float, payer: str) -> str:
    """Renew one FloodGuard flood policy for a new twelve-month term. The policy's term start, term end and annual
    term premium are replaced with the new term's values and the indicated renewal premium on the policy is
    cleared; two charges are posted to the policy's premium account for the new term: the term premium as
    installment 1, due on the new term's start date and billed to the named payer, and the annual policy fee.
    The policy then shows the new term and its premium account shows both new charges. The receipt lists
    the new term and the reference numbers of both charges; status policy_renewed means the renewal was written.

    Args:
        flood_policy_id: Id class — the reference number of the FloodGuard flood policy record being renewed, as
            returned by the flood policy lookup for the verified caller.
        new_effective_date: Fixed-format class — the start date of the new term, written as YYYY-MM-DD.
        new_expiration_date: Fixed-format class — the end date of the new term, written as YYYY-MM-DD.
        term_premium: Fixed-format class — the annual premium of the new term, excluding the policy fee, in USD as a
            plain number with 2 decimal places; stored rounded half-up to 2 decimal places.
        policy_fee: Fixed-format class — the annual policy fee charged for the new term, in USD as a plain number
            with 2 decimal places; stored rounded half-up to 2 decimal places.
        payer: Enum class — who the new term's premium charge is billed to: insured when the named insured pays
            the premium directly (annual or two-pay billing); mortgagee when the premium is paid from the lender's
            escrow account (mortgagee escrow billing); none when the charge is billed to nobody in particular and
            no payer is named.

    Returns:
        A dictionary rendered as text with: flood_policy_id (the policy renewed), effective_date and
        expiration_date (the new term, YYYY-MM-DD), term_premium (USD with 2 decimal places),
        premium_charge_id and fee_charge_id (reference numbers of the two premium account entries posted) and
        status (the text policy_renewed).
    """
    premium = round(float(term_premium), 2)
    fee = round(float(policy_fee), 2)
    today = ctx.now()[:10]
    cust = _customer_of(ctx, flood_policy_id)
    ctx.update("flood_policies", flood_policy_id, effective_date=new_effective_date,
               expiration_date=new_expiration_date, term_premium=premium, indicated_renewal_premium="")
    pid = ctx.make_id("fbl_", flood_policy_id, new_effective_date, new_expiration_date, premium, fee, payer, "premium")
    ctx.create("flood_billing", pid, flood_billing_id=pid, flood_policy_id=flood_policy_id, customer_id=cust,
               event_type="flood_premium_billed", posted_date=today, term_effective_date=new_effective_date,
               installment_number=1, due_date=new_effective_date, amount=premium, fee_code="none", payer=payer,
               payment_method="none", payment_reference="", change_reason="none", effective_date="",
               credit_basis="none", source_billing_id="", source_endorsement_id="")
    fid = ctx.make_id("fbl_", flood_policy_id, new_effective_date, new_expiration_date, premium, fee, payer, "fee")
    ctx.create("flood_billing", fid, flood_billing_id=fid, flood_policy_id=flood_policy_id, customer_id=cust,
               event_type="flood_fee_assessed", posted_date=today, term_effective_date=new_effective_date,
               installment_number=1, due_date="", amount=fee, fee_code="policy_fee", payer="none",
               payment_method="none", payment_reference="", change_reason="none", effective_date="",
               credit_basis="none", source_billing_id="", source_endorsement_id="")
    return str({"flood_policy_id": flood_policy_id, "effective_date": new_effective_date,
                "expiration_date": new_expiration_date, "term_premium": premium,
                "premium_charge_id": pid, "fee_charge_id": fid, "status": "policy_renewed"})


@tool(owner="user", rw="write")
def pay_flood_renewal_premium_ad8d78a5(ctx: ToolContext, flood_policy_id: str, amount: float, payment_method: str) -> str:
    """The named insured pays money toward their own FloodGuard flood policy. One payment from the insured is
    received on the policy's premium account for the amount given, dated today, and a payment confirmation
    number is issued for it; the premium account then shows the payment and a lower amount owed. The receipt
    carries the confirmation number the insured keeps; status payment_received means the payment was taken.

    Args:
        flood_policy_id: Id class — the reference number of the FloodGuard flood policy record being paid, as
            read out by the representative from the flood policy lookup.
        amount: Fixed-format class — the amount paid, in USD as a plain number with 2 decimal places, as stated by
            the representative; stored rounded half-up to 2 decimal places.
        payment_method: Enum class — how the insured pays: eft when the money is drawn from the insured's bank
            account by electronic funds transfer; card when the insured pays with a debit or credit card; check
            when the insured sends a personal check; mortgagee_check when the lender pays from escrow by check,
            which an insured paying for themselves never uses; none when no method applies, which a real
            payment never uses.

    Returns:
        A dictionary rendered as text with: payment_reference (the confirmation number issued for this payment,
        a string starting with 5), flood_billing_id (reference number of the premium account entry), amount
        (USD with 2 decimal places), posted_date (YYYY-MM-DD) and status (the text payment_received).
    """
    paid = round(float(amount), 2)
    today = ctx.now()[:10]
    rid = ctx.make_id("fpy_", flood_policy_id, paid, payment_method)
    reference = "5" + str(int(rid[4:], 16))[-9:]
    ctx.create("flood_billing", rid, flood_billing_id=rid, flood_policy_id=flood_policy_id,
               customer_id=_customer_of(ctx, flood_policy_id), event_type="flood_payment_received",
               posted_date=today, term_effective_date="", installment_number=0, due_date="", amount=paid,
               fee_code="none", payer="insured", payment_method=payment_method, payment_reference=reference,
               change_reason="none", effective_date="", credit_basis="none", source_billing_id="",
               source_endorsement_id="")
    return str({"payment_reference": reference, "flood_billing_id": rid, "amount": paid, "posted_date": today,
                "status": "payment_received"})


@tool(owner="agent", rw="write")
def bill_flood_increase_premium_f099355d(ctx: ToolContext, flood_policy_id: str, flood_endorsement_id: str,
                                         attach_date: str, amount: float) -> str:
    """Charge the premium of one midterm limit increase on a FloodGuard flood policy. One additional-premium charge
    for the named limit increase is posted to the policy's premium account, dated today and marked as a coverage
    increase attaching on the given date; the premium account then shows the charge and a higher amount owed.
    The receipt carries the reference number of the new charge; status increase_premium_billed means it posted.

    Args:
        flood_policy_id: Id class — the reference number of the FloodGuard flood policy record charged, as
            returned by the flood policy lookup for the verified caller.
        flood_endorsement_id: Id class — the reference number of the limit-increase entry the charge belongs to,
            as returned by the flood endorsement lookup.
        attach_date: Fixed-format class — the date the limit increase attaches, written as YYYY-MM-DD.
        amount: Fixed-format class — the additional premium charged, in USD as a plain number with 2 decimal
            places; stored rounded half-up to 2 decimal places.

    Returns:
        A dictionary rendered as text with: flood_billing_id (reference number of the charge), flood_endorsement_id
        (the limit increase charged), amount (USD with 2 decimal places), posted_date (YYYY-MM-DD) and status
        (the text increase_premium_billed).
    """
    charged = round(float(amount), 2)
    today = ctx.now()[:10]
    rid = ctx.make_id("fad_", flood_policy_id, flood_endorsement_id, attach_date, charged)
    ctx.create("flood_billing", rid, flood_billing_id=rid, flood_policy_id=flood_policy_id,
               customer_id=_customer_of(ctx, flood_policy_id), event_type="flood_additional_premium",
               posted_date=today, term_effective_date="", installment_number=0, due_date="", amount=charged,
               fee_code="none", payer="none", payment_method="none", payment_reference="",
               change_reason="coverage_increase", effective_date=attach_date, credit_basis="none",
               source_billing_id="", source_endorsement_id=flood_endorsement_id)
    return str({"flood_billing_id": rid, "flood_endorsement_id": flood_endorsement_id, "amount": charged,
                "posted_date": today, "status": "increase_premium_billed"})


@tool(owner="user", rw="write")
def sign_flood_cancellation_83daa4cf(ctx: ToolContext, flood_policy_id: str, flood_request_id: str,
                                     cancellation_date: str, credit_basis: str, credit_amount: float) -> str:
    """The named insured signs the cancellation of their own FloodGuard flood policy on the cancellation request
    already on file. The request is marked completed, the policy becomes cancelled as of the given date with the
    request's stated reason as the ground, and the unearned-premium credit given is posted to the policy's
    premium account dated today. The policy then shows as cancelled and the premium account shows the
    credit. The receipt carries the reference number of the credit; status policy_cancelled means it was done.

    Args:
        flood_policy_id: Id class — the reference number of the FloodGuard flood policy record being cancelled,
            as read out by the representative from the flood policy lookup.
        flood_request_id: Id class — the reference number of the named insured's cancellation request on file, as
            read out by the representative from the request lookup.
        cancellation_date: Fixed-format class — the date the cancellation takes effect, written as YYYY-MM-DD.
        credit_basis: Enum class — the basis of the credit: pro_rata when the unearned share of the premium is
            returned for the days of the term beyond the cancellation date; flat when the whole term premium is returned
            because coverage is treated as never having started; none when no credit is posted because the
            premium is fully earned.
        credit_amount: Fixed-format class — the credit posted, in USD as a plain number with 2 decimal places, as
            stated by the representative; stored rounded half-up to 2 decimal places.

    Returns:
        A dictionary rendered as text with: flood_policy_id (the policy cancelled), closed_date (YYYY-MM-DD),
        credit_id (reference number of the credit entry), credit_amount (USD with 2 decimal places) and status
        (the text policy_cancelled).
    """
    credit = round(float(credit_amount), 2)
    today = ctx.now()[:10]
    reqs = ctx.find("flood_requests", flood_request_id=flood_request_id)
    reason = reqs[0].get("cancellation_reason", "none") if reqs else "none"
    ctx.update("flood_requests", flood_request_id, outcome="completed")
    ctx.update("flood_policies", flood_policy_id, status="cancelled", status_reason=reason,
               closed_date=cancellation_date, pending_action_date="")
    rid = ctx.make_id("frp_", flood_policy_id, flood_request_id, cancellation_date, credit_basis, credit)
    ctx.create("flood_billing", rid, flood_billing_id=rid, flood_policy_id=flood_policy_id,
               customer_id=_customer_of(ctx, flood_policy_id), event_type="flood_return_premium",
               posted_date=today, term_effective_date="", installment_number=0, due_date="", amount=credit,
               fee_code="none", payer="none", payment_method="none", payment_reference="",
               change_reason="cancellation", effective_date=cancellation_date, credit_basis=credit_basis,
               source_billing_id="", source_endorsement_id="")
    return str({"flood_policy_id": flood_policy_id, "closed_date": cancellation_date, "credit_id": rid,
                "credit_amount": credit, "status": "policy_cancelled"})


@tool(owner="agent", rw="write")
def issue_flood_refund_b526defb(ctx: ToolContext, flood_policy_id: str, payer: str, payment_method: str,
                                amount: float) -> str:
    """Refund money from the premium account of one FloodGuard flood policy. One refund to the named party is
    posted to the policy's premium account, dated today, for the amount given and by the method given; the
    account's credit balance falls by that amount. The receipt carries the reference number of the refund entry;
    status refund_issued means the refund was sent.

    Args:
        flood_policy_id: Id class — the reference number of the FloodGuard flood policy record refunded from, as
            returned by the flood policy lookup for the verified caller.
        payer: Enum class — who receives the refund: insured when the money goes back to the named insured;
            mortgagee when it goes back to the lender whose escrow payment created the credit; none when the
            refund names no recipient, which a real refund never uses.
        payment_method: Enum class — how the refund is sent: eft when it is returned to a bank account by
            electronic funds transfer; card when it is returned to the debit or credit card that paid; check
            when a paper check is mailed to the insured; mortgagee_check when a check is sent to the lender's
            escrow department; none when no method applies, which a real refund never uses.
        amount: Fixed-format class — the amount refunded, in USD as a plain number with 2 decimal places; stored
            rounded half-up to 2 decimal places.

    Returns:
        A dictionary rendered as text with: flood_billing_id (reference number of the refund entry), payer and
        payment_method (as given), amount (USD with 2 decimal places), posted_date (YYYY-MM-DD) and status (the
        text refund_issued).
    """
    refunded = round(float(amount), 2)
    today = ctx.now()[:10]
    rid = ctx.make_id("frf_", flood_policy_id, payer, payment_method, refunded)
    ctx.create("flood_billing", rid, flood_billing_id=rid, flood_policy_id=flood_policy_id,
               customer_id=_customer_of(ctx, flood_policy_id), event_type="flood_refund_issued",
               posted_date=today, term_effective_date="", installment_number=0, due_date="", amount=refunded,
               fee_code="none", payer=payer, payment_method=payment_method, payment_reference="",
               change_reason="none", effective_date="", credit_basis="none", source_billing_id="",
               source_endorsement_id="")
    return str({"flood_billing_id": rid, "payer": payer, "payment_method": payment_method, "amount": refunded,
                "posted_date": today, "status": "refund_issued"})

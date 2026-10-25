"""Hidden task tools of the nfip_dwelling_servicing difficulty (Tidemark NFIP Dwelling Form servicing).

Each tool performs one servicing transaction on one NFIP Dwelling Form policy with the figures the
desk has already worked out; it checks no eligibility, computes no premium and never refuses.
"""

from erlbench import ToolContext, tool


@tool(owner="agent", rw="write")
def bill_coverage_increase_e35332a0(ctx: ToolContext, dwelling_policy_id: str, dwelling_change_id: str,
                                    change_effective_date: str, risk_premium_charge: float,
                                    reserve_fund_charge: float, endorsed_risk_premium: float) -> str:
    """Put a recorded coverage-increase endorsement into effect on an NFIP Dwelling Form policy and bill its
    additional premium. The endorsement record is stamped with its effective date; the policy is updated to the
    building and contents limits and deductibles recorded on that endorsement and to the full-term risk premium
    stated for the policy as endorsed;
    and two endorsement charges are posted to the policy's premium account for the current term, one on the risk
    premium line and one on the reserve fund assessment line, each referencing the endorsement. Both charges
    raise the amount owed on the policy. Success is shown by the receipt line naming the two charge entries.

    Args:
        dwelling_policy_id: Id class — the reference number of the NFIP Dwelling Form policy being endorsed, as returned by the NFIP Dwelling Form policy lookup.
        dwelling_change_id: Id class — the reference number of the recorded coverage-increase endorsement, as returned by the servicing-document lookup for that policy.
        change_effective_date: Fixed-format class — the date the coverage increase takes effect, written YYYY-MM-DD (calendar date, no time zone).
        risk_premium_charge: Fixed-format class — the endorsement charge on the risk premium line, in US dollars as a positive number with 2 decimal places, already rounded half-up to the cent.
        reserve_fund_charge: Fixed-format class — the endorsement charge on the reserve fund assessment line, in US dollars as a positive number with 2 decimal places, already rounded half-up to the cent.
        endorsed_risk_premium: Fixed-format class — the full-term risk premium that stands on the policy once the increase is in effect, in USD (US dollars) with 2 decimal places.

    Returns:
        A text receipt: "Coverage increase <endorsement reference> effective <YYYY-MM-DD> on policy <policy
        reference>; building <limit>, contents <limit>; risk premium charge <entry reference> <amount> and reserve
        fund charge <entry reference> <amount> posted; balance now <amount>." where limits are whole US dollars,
        amounts are US dollars with 2 decimals and the balance is the amount owed on the policy afterwards.
    """
    pol = ctx.find("dwelling_policies", dwelling_policy_id=dwelling_policy_id)[0]
    end = ctx.find("dwelling_changes", dwelling_change_id=dwelling_change_id)[0]
    ctx.update("dwelling_changes", dwelling_change_id, change_effective_date=change_effective_date)
    ctx.update("dwelling_policies", dwelling_policy_id,
               building_coverage=end.get("new_building_coverage"), contents_coverage=end.get("new_contents_coverage"),
               building_deductible=end.get("new_building_deductible"),
               contents_deductible=end.get("new_contents_deductible"),
               rated_risk_premium=round(float(endorsed_risk_premium), 2))
    day = ctx.now()[:10]
    risk = round(float(risk_premium_charge), 2)
    fund = round(float(reserve_fund_charge), 2)
    rid = ctx.make_id("dbl_", dwelling_policy_id, dwelling_change_id, change_effective_date, risk, "RISK")
    fid = ctx.make_id("dbl_", dwelling_policy_id, dwelling_change_id, change_effective_date, fund, "RFA")
    common = dict(dwelling_policy_id=dwelling_policy_id, customer_id=pol.get("customer_id"),
                  event_type="dwelling_premium_charged", term_start=pol.get("term_start"), charge_basis="ENDORSEMENT",
                  posted_date=day, reference_id=dwelling_change_id, payment_ref="", payment_method="NONE",
                  payee="NONE")
    ctx.create("dwelling_billing", rid, dwelling_billing_id=rid, component="RISK_PREMIUM", amount=risk, **common)
    ctx.create("dwelling_billing", fid, dwelling_billing_id=fid, component="RESERVE_FUND_ASSESSMENT", amount=fund,
               **common)
    balance = round(float(pol.get("premium_balance") or 0) + risk + fund, 2)
    ctx.update("dwelling_policies", dwelling_policy_id, premium_balance=balance)
    return (f"Coverage increase {dwelling_change_id} effective {change_effective_date} on policy {dwelling_policy_id}; "
            f"building {end.get('new_building_coverage')}, contents {end.get('new_contents_coverage')}; "
            f"risk premium charge {rid} {risk:.2f} and reserve fund charge {fid} {fund:.2f} posted; "
            f"balance now {balance:.2f}.")


@tool(owner="agent", rw="write")
def bill_contents_increase_55716379(ctx: ToolContext, dwelling_policy_id: str, dwelling_change_id: str,
                                    change_effective_date: str, risk_premium_charge: float,
                                    reserve_fund_charge: float, endorsed_risk_premium: float) -> str:
    """Put a recorded contents-limit increase endorsement into effect on an NFIP Dwelling Form policy and bill its
    additional premium. The endorsement record is stamped with its effective date; the policy is updated to the
    building and contents limits and deductibles recorded on that endorsement and to the full-term risk premium
    stated for the policy as endorsed;
    and two endorsement charges are posted to the policy's premium account for the current term, one on the risk
    premium line and one on the reserve fund assessment line, each referencing the endorsement. Both charges
    raise the amount owed on the policy. Success is shown by the receipt line naming the two charge entries.

    Args:
        dwelling_policy_id: Id class — the reference number of the NFIP Dwelling Form policy being endorsed, as returned by the NFIP Dwelling Form policy lookup.
        dwelling_change_id: Id class — the reference number of the recorded contents-limit increase endorsement, as returned by the servicing-document lookup for that policy.
        change_effective_date: Fixed-format class — the date the contents-limit increase takes effect, written YYYY-MM-DD (calendar date, no time zone).
        risk_premium_charge: Fixed-format class — the endorsement charge on the risk premium line, in US dollars as a positive number with 2 decimal places, already rounded half-up to the cent.
        reserve_fund_charge: Fixed-format class — the endorsement charge on the reserve fund assessment line, in US dollars as a positive number with 2 decimal places, already rounded half-up to the cent.
        endorsed_risk_premium: Fixed-format class — the full-term risk premium that stands on the policy once the contents-limit increase is in effect, in USD (US dollars) with 2 decimal places.

    Returns:
        A text receipt: "Contents increase <endorsement reference> effective <YYYY-MM-DD> on policy <policy
        reference>; building <limit>, contents <limit>; risk premium charge <entry reference> <amount> and reserve
        fund charge <entry reference> <amount> posted; balance now <amount>." where limits are whole US dollars,
        amounts are US dollars with 2 decimals and the balance is the amount owed on the policy afterwards.
    """
    pol = ctx.find("dwelling_policies", dwelling_policy_id=dwelling_policy_id)[0]
    end = ctx.find("dwelling_changes", dwelling_change_id=dwelling_change_id)[0]
    ctx.update("dwelling_changes", dwelling_change_id, change_effective_date=change_effective_date)
    ctx.update("dwelling_policies", dwelling_policy_id,
               building_coverage=end.get("new_building_coverage"), contents_coverage=end.get("new_contents_coverage"),
               building_deductible=end.get("new_building_deductible"),
               contents_deductible=end.get("new_contents_deductible"),
               rated_risk_premium=round(float(endorsed_risk_premium), 2))
    day = ctx.now()[:10]
    risk = round(float(risk_premium_charge), 2)
    fund = round(float(reserve_fund_charge), 2)
    rid = ctx.make_id("dbl_", dwelling_policy_id, dwelling_change_id, change_effective_date, risk, "RISK")
    fid = ctx.make_id("dbl_", dwelling_policy_id, dwelling_change_id, change_effective_date, fund, "RFA")
    common = dict(dwelling_policy_id=dwelling_policy_id, customer_id=pol.get("customer_id"),
                  event_type="dwelling_premium_charged", term_start=pol.get("term_start"), charge_basis="ENDORSEMENT",
                  posted_date=day, reference_id=dwelling_change_id, payment_ref="", payment_method="NONE",
                  payee="NONE")
    ctx.create("dwelling_billing", rid, dwelling_billing_id=rid, component="RISK_PREMIUM", amount=risk, **common)
    ctx.create("dwelling_billing", fid, dwelling_billing_id=fid, component="RESERVE_FUND_ASSESSMENT", amount=fund,
               **common)
    balance = round(float(pol.get("premium_balance") or 0) + risk + fund, 2)
    ctx.update("dwelling_policies", dwelling_policy_id, premium_balance=balance)
    return (f"Contents increase {dwelling_change_id} effective {change_effective_date} on policy {dwelling_policy_id}; "
            f"building {end.get('new_building_coverage')}, contents {end.get('new_contents_coverage')}; "
            f"risk premium charge {rid} {risk:.2f} and reserve fund charge {fid} {fund:.2f} posted; "
            f"balance now {balance:.2f}.")


@tool(owner="agent", rw="write")
def bill_deductible_decrease_87aa0055(ctx: ToolContext, dwelling_policy_id: str, dwelling_change_id: str,
                                      change_effective_date: str, risk_premium_charge: float,
                                      reserve_fund_charge: float, endorsed_risk_premium: float) -> str:
    """Put a recorded deductible-decrease endorsement into effect on an NFIP Dwelling Form policy and bill its
    additional premium. The endorsement record is stamped with its effective date; the policy is updated to the
    building and contents limits and deductibles recorded on that endorsement and to the full-term risk premium
    stated for the policy as endorsed;
    and two endorsement charges are posted to the policy's premium account for the current term, one on the risk
    premium line and one on the reserve fund assessment line, each referencing the endorsement. Both charges
    raise the amount owed on the policy. Success is shown by the receipt line naming the two charge entries.

    Args:
        dwelling_policy_id: Id class — the reference number of the NFIP Dwelling Form policy being endorsed, as returned by the NFIP Dwelling Form policy lookup.
        dwelling_change_id: Id class — the reference number of the recorded deductible-decrease endorsement, as returned by the servicing-document lookup for that policy.
        change_effective_date: Fixed-format class — the date the deductible decrease takes effect, written YYYY-MM-DD (calendar date, no time zone).
        risk_premium_charge: Fixed-format class — the endorsement charge on the risk premium line, in US dollars as a positive number with 2 decimal places, already rounded half-up to the cent.
        reserve_fund_charge: Fixed-format class — the endorsement charge on the reserve fund assessment line, in US dollars as a positive number with 2 decimal places, already rounded half-up to the cent.
        endorsed_risk_premium: Fixed-format class — the full-term risk premium that stands on the policy once the deductible decrease is in effect, in USD (US dollars) with 2 decimal places.

    Returns:
        A text receipt: "Deductible decrease <endorsement reference> effective <YYYY-MM-DD> on policy <policy
        reference>; building deductible <amount>, contents deductible <amount>; risk premium charge <entry reference> <amount> and reserve
        fund charge <entry reference> <amount> posted; balance now <amount>." where deductibles are whole US dollars,
        amounts are US dollars with 2 decimals and the balance is the amount owed on the policy afterwards.
    """
    pol = ctx.find("dwelling_policies", dwelling_policy_id=dwelling_policy_id)[0]
    end = ctx.find("dwelling_changes", dwelling_change_id=dwelling_change_id)[0]
    ctx.update("dwelling_changes", dwelling_change_id, change_effective_date=change_effective_date)
    ctx.update("dwelling_policies", dwelling_policy_id,
               building_coverage=end.get("new_building_coverage"), contents_coverage=end.get("new_contents_coverage"),
               building_deductible=end.get("new_building_deductible"),
               contents_deductible=end.get("new_contents_deductible"),
               rated_risk_premium=round(float(endorsed_risk_premium), 2))
    day = ctx.now()[:10]
    risk = round(float(risk_premium_charge), 2)
    fund = round(float(reserve_fund_charge), 2)
    rid = ctx.make_id("dbl_", dwelling_policy_id, dwelling_change_id, change_effective_date, risk, "RISK")
    fid = ctx.make_id("dbl_", dwelling_policy_id, dwelling_change_id, change_effective_date, fund, "RFA")
    common = dict(dwelling_policy_id=dwelling_policy_id, customer_id=pol.get("customer_id"),
                  event_type="dwelling_premium_charged", term_start=pol.get("term_start"), charge_basis="ENDORSEMENT",
                  posted_date=day, reference_id=dwelling_change_id, payment_ref="", payment_method="NONE",
                  payee="NONE")
    ctx.create("dwelling_billing", rid, dwelling_billing_id=rid, component="RISK_PREMIUM", amount=risk, **common)
    ctx.create("dwelling_billing", fid, dwelling_billing_id=fid, component="RESERVE_FUND_ASSESSMENT", amount=fund,
               **common)
    balance = round(float(pol.get("premium_balance") or 0) + risk + fund, 2)
    ctx.update("dwelling_policies", dwelling_policy_id, premium_balance=balance)
    return (f"Deductible decrease {dwelling_change_id} effective {change_effective_date} on policy {dwelling_policy_id}; "
            f"building deductible {end.get('new_building_deductible')}, contents deductible {end.get('new_contents_deductible')}; "
            f"risk premium charge {rid} {risk:.2f} and reserve fund charge {fid} {fund:.2f} posted; "
            f"balance now {balance:.2f}.")


@tool(owner="user", rw="write")
def pay_renewal_premium_abaf74a5(ctx: ToolContext, dwelling_policy_id: str, payment_method: str,
                                 amount: float, residence_credit: float) -> str:
    """The named insured pays the renewal premium for the coming term of their NFIP Dwelling Form policy. One
    payment of the stated amount is received and applied to the policy for the term that starts on the current
    term's expiration date, and it lowers the amount owed on the policy. When a residence credit is stated, it is
    booked first as a re-rate credit on the HFIAA surcharge line of the current term, also lowering the amount
    owed. A payment reference is issued for the payment item. Success is shown by the receipt line carrying that
    payment reference.

    Args:
        dwelling_policy_id: Id class — the reference number of the NFIP Dwelling Form policy being renewed, as given to the insured by the representative from the NFIP Dwelling Form policy lookup.
        payment_method: Enum class — how the insured pays: CHECK when the insured pays by a check drawn on their bank account; ACH when the insured authorizes a one-time debit from their bank account by routing and account number; CREDIT_CARD when the insured pays with a credit or debit card; ESCROW_DISBURSEMENT only when the payment is a disbursement from the lender's escrow account rather than the insured's own funds; NONE only when no payment item exists, which never applies to a payment the insured makes.
        amount: Fixed-format class — the amount paid, in US dollars as a positive number with 2 decimal places.
        residence_credit: Fixed-format class — the credit on the current term's HFIAA surcharge line booked with the payment, in USD (US dollars) as a non-negative number with 2 decimal places, already rounded half-up to the cent; zero when no such credit is due.

    Returns:
        A text receipt: "Payment <payment reference> of <amount> by <method> received for policy <policy reference>,
        term starting <YYYY-MM-DD>; residence credit <amount>; balance now <amount>." where amounts are US dollars with 2 decimals, the payment
        reference identifies the payment item and the balance is the amount owed on the policy afterwards.
    """
    pol = ctx.find("dwelling_policies", dwelling_policy_id=dwelling_policy_id)[0]
    amt = round(float(amount), 2)
    credit = round(float(residence_credit), 2)
    balance = round(float(pol.get("premium_balance") or 0), 2)
    if credit > 0:
        cid = ctx.make_id("dbl_", dwelling_policy_id, pol.get("term_start"), credit, "RESIDENCE_CREDIT")
        ctx.create("dwelling_billing", cid, dwelling_billing_id=cid, dwelling_policy_id=dwelling_policy_id,
                   customer_id=pol.get("customer_id"), event_type="dwelling_premium_credit",
                   term_start=pol.get("term_start"), component="HFIAA_SURCHARGE", charge_basis="RERATE",
                   amount=credit, posted_date=ctx.now()[:10], reference_id=dwelling_policy_id, payment_ref="",
                   payment_method="NONE", payee="NONE")
        balance = round(balance - credit, 2)
    pid = ctx.make_id("dbl_", dwelling_policy_id, payment_method, amt, "RENEWAL_PAYMENT")
    ref = "1" + ctx.make_id("", dwelling_policy_id, payment_method, amt, length=9).upper()
    ctx.create("dwelling_billing", pid, dwelling_billing_id=pid, dwelling_policy_id=dwelling_policy_id,
               customer_id=pol.get("customer_id"), event_type="dwelling_premium_payment",
               term_start=pol.get("term_end"), component="TOTAL", charge_basis="PAYMENT", amount=amt,
               posted_date=ctx.now()[:10], reference_id="", payment_ref=ref, payment_method=payment_method,
               payee="NONE")
    balance = round(balance - amt, 2)
    ctx.update("dwelling_policies", dwelling_policy_id, premium_balance=balance)
    return (f"Payment {ref} of {amt:.2f} by {payment_method} received for policy {dwelling_policy_id}, term starting "
            f"{pol.get('term_end')}; residence credit {credit:.2f}; balance now {balance:.2f}.")


@tool(owner="user", rw="write")
def sign_cancellation_request_cbba569e(ctx: ToolContext, dwelling_policy_id: str, cancellation_reason: str,
                                       supporting_document: str, requested_effective_date: str) -> str:
    """The named insured signs a cancellation request for their NFIP Dwelling Form policy. One signed
    cancellation request is put on file for the policy, carrying the reason, the document the insured supplies
    with it and the date the cancellation is to take effect; the request is recorded as signed, with no lender
    release on file, and nothing on the policy itself changes. Success is shown by the receipt line carrying the
    request reference.

    Args:
        dwelling_policy_id: Id class — the reference number of the NFIP Dwelling Form policy to be cancelled, as given to the insured by the representative from the NFIP Dwelling Form policy lookup.
        cancellation_reason: Enum class — the reason on the request: BUILDING_SOLD when the insured building was sold; BUILDING_REMOVED_OR_DEMOLISHED when it was removed or demolished; CONTENTS_SOLD_OR_REMOVED when a contents-only policy's contents left the premises; DUPLICATE_NFIP_POLICY when another NFIP policy covers the same property; CLOSING_DID_NOT_OCCUR when the loan the policy was bought for never closed; REMOVED_FROM_SFHA_BY_LOMA_LOMR when a FEMA letter removed the building from the Special Flood Hazard Area; MORTGAGE_PAID_OFF when the loan requiring the coverage was paid off; VOLUNTARY_NOT_REQUIRED when the insured no longer wants coverage that no lender requires; REPLACED_BY_PRIVATE_FLOOD when a private flood policy replaced this policy; NO_INSURABLE_INTEREST when the insured never had an interest in the property; INELIGIBLE_PROPERTY when the property was never insurable; PREMIUM_PAYMENT_DISHONORED when the application premium was dishonored; NONE when no reason applies, which never applies to a signed cancellation.
        supporting_document: Enum class — the document supplied with the request: CLOSING_DISCLOSURE for a sale's closing disclosure or settlement statement; REMOVAL_EVIDENCE for proof the building was removed; OTHER_NFIP_DECLARATIONS for another NFIP policy's declarations; LENDER_LOAN_NOT_CLOSED_STATEMENT for the lender's statement that the loan did not close; LOMA_LOMR_LETTER for a FEMA letter of map amendment or revision; PAYOFF_LETTER for a loan payoff letter; PRIVATE_FLOOD_DECLARATIONS for the replacing private flood policy's declarations; NONE when no document is supplied.
        requested_effective_date: Fixed-format class — the date the cancellation takes effect, written YYYY-MM-DD (calendar date, no time zone).

    Returns:
        A text receipt: "Cancellation request <request reference> signed for policy <policy reference>: reason <reason>,
        document <document>, effective <YYYY-MM-DD>." where the request reference identifies the signed request on file.
    """
    pol = ctx.find("dwelling_policies", dwelling_policy_id=dwelling_policy_id)[0]
    rid = ctx.make_id("drq_", dwelling_policy_id, cancellation_reason, supporting_document, requested_effective_date)
    ctx.create("dwelling_requests", rid, dwelling_request_id=rid, customer_id=pol.get("customer_id"),
               dwelling_policy_id=dwelling_policy_id, request_type="CANCELLATION", cancellation_reason=cancellation_reason,
               requested_effective_date=requested_effective_date, supporting_document=supporting_document,
               lender_release_on_file=False, assignee_customer_id="", outcome="SIGNED", created_at=ctx.now())
    return (f"Cancellation request {rid} signed for policy {dwelling_policy_id}: reason {cancellation_reason}, "
            f"document {supporting_document}, effective {requested_effective_date}.")


@tool(owner="agent", rw="write")
def process_policy_cancellation_6794673f(ctx: ToolContext, dwelling_policy_id: str, dwelling_request_id: str,
                                         risk_premium_credit: float, reserve_fund_credit: float,
                                         hfiaa_credit: float, icc_credit: float, refund_amount: float,
                                         payee: str) -> str:
    """Process a signed cancellation request on an NFIP Dwelling Form policy, post its cancellation credits and pay
    out the refund. The policy is marked cancelled with the reason and effective date stated on the request and
    today's date as the processing date; cancellation credits are posted to the policy's premium account for the
    current term on the risk premium, reserve fund assessment, HFIAA surcharge and ICC premium lines, each
    referencing the request (a line whose credit is zero is not posted); and one refund payment of the stated amount is issued to
    the stated payee against the policy's premium account, referencing the request, with a refund check or ACH
    reference. The credits lower the amount owed on the policy and the refund raises it by the amount paid out.
    Success is shown by the receipt line naming the credit entries and the refund reference.

    Args:
        dwelling_policy_id: Id class — the reference number of the NFIP Dwelling Form policy being cancelled, as returned by the NFIP Dwelling Form policy lookup.
        dwelling_request_id: Id class — the reference number of the signed cancellation request, as returned when the insured signed it or by the request lookup for that policy.
        risk_premium_credit: Fixed-format class — the cancellation credit on the risk premium line, in US dollars as a non-negative number with 2 decimal places, already rounded half-up to the cent.
        reserve_fund_credit: Fixed-format class — the cancellation credit on the reserve fund assessment line, in US dollars as a non-negative number with 2 decimal places, already rounded half-up to the cent.
        hfiaa_credit: Fixed-format class — the cancellation credit on the HFIAA surcharge line, in US dollars as a non-negative number with 2 decimal places, already rounded half-up to the cent.
        icc_credit: Fixed-format class — the cancellation credit on the ICC premium line, in US dollars as a non-negative number with 2 decimal places, already rounded half-up to the cent; zero on a tier with no ICC coverage.
        refund_amount: Fixed-format class — the refund paid out with the cancellation, in US dollars as a non-negative number with 2 decimal places, already rounded half-up to the cent; when it is zero no refund payment is issued.
        payee: Enum class — who receives the refund: INSURED when the insured is the premium payor of record; LENDER_ESCROW when the lender paying from the borrower's escrow account is the premium payor of record; NONE when no refund is paid out.

    Returns:
        A text receipt: "Policy <policy reference> cancelled effective <YYYY-MM-DD> (<reason>); credits posted:
        <entry reference> <component> <amount>, ...; refund <refund reference> of <amount> to <payee>; balance now
        <amount>." where amounts are US dollars with 2 decimals and the balance is the amount owed afterwards.
    """
    pol = ctx.find("dwelling_policies", dwelling_policy_id=dwelling_policy_id)[0]
    req = ctx.find("dwelling_requests", dwelling_request_id=dwelling_request_id)[0]
    day = ctx.now()[:10]
    ctx.update("dwelling_policies", dwelling_policy_id, status="cancelled",
               cancellation_reason=req.get("cancellation_reason"),
               cancellation_effective_date=req.get("requested_effective_date"), closed_date=day)
    posted, total = [], 0.0
    for comp, amt in (("RISK_PREMIUM", risk_premium_credit), ("RESERVE_FUND_ASSESSMENT", reserve_fund_credit),
                      ("HFIAA_SURCHARGE", hfiaa_credit), ("ICC_PREMIUM", icc_credit)):
        amt = round(float(amt), 2)
        if amt <= 0:
            continue
        cid = ctx.make_id("dbl_", dwelling_policy_id, dwelling_request_id, comp, amt)
        ctx.create("dwelling_billing", cid, dwelling_billing_id=cid, dwelling_policy_id=dwelling_policy_id,
                   customer_id=pol.get("customer_id"), event_type="dwelling_premium_credit",
                   term_start=pol.get("term_start"), component=comp, charge_basis="CANCELLATION", amount=amt,
                   posted_date=day, reference_id=dwelling_request_id, payment_ref="", payment_method="NONE",
                   payee="NONE")
        posted.append(f"{cid} {comp} {amt:.2f}")
        total += amt
    balance = round(float(pol.get("premium_balance") or 0) - total, 2)
    paid = round(float(refund_amount), 2)
    ref = "none"
    if paid > 0:
        bid = ctx.make_id("dbl_", dwelling_policy_id, dwelling_request_id, payee, paid)
        ref = "1R" + ctx.make_id("", dwelling_policy_id, dwelling_request_id, paid, length=8).upper()
        ctx.create("dwelling_billing", bid, dwelling_billing_id=bid, dwelling_policy_id=dwelling_policy_id,
                   customer_id=pol.get("customer_id"), event_type="dwelling_refund_disbursed", term_start="",
                   component="TOTAL", charge_basis="REFUND", amount=paid, posted_date=day,
                   reference_id=dwelling_request_id, payment_ref=ref, payment_method="NONE", payee=payee)
        balance = round(balance + paid, 2)
    ctx.update("dwelling_policies", dwelling_policy_id, premium_balance=balance)
    return (f"Policy {dwelling_policy_id} cancelled effective {req.get('requested_effective_date')} "
            f"({req.get('cancellation_reason')}); credits posted: {', '.join(posted)}; refund {ref} of {paid:.2f} "
            f"to {payee}; balance now {balance:.2f}.")


@tool(owner="agent", rw="write")
def bill_insured_increase_9da169e7(ctx: ToolContext, dwelling_policy_id: str, dwelling_change_id: str,
                                   change_effective_date: str, risk_premium_charge: float,
                                   reserve_fund_charge: float, endorsed_risk_premium: float) -> str:
    """Put a pending coverage-increase request made by the insured into effect on an NFIP Dwelling Form policy and
    bill its additional premium. The request record is stamped with its effective date; the policy is updated to
    the limits and deductibles recorded on the request and to the full-term risk premium stated for the policy as
    endorsed; and two endorsement charges are posted to the policy's premium account for the current term, one on
    the risk premium line and one on the reserve fund assessment line, each referencing the request (a charge of
    zero is not posted). The charges raise the amount owed on the policy. Success is shown by the receipt line
    naming the charge entries.

    Args:
        dwelling_policy_id: Id class — the reference number of the NFIP Dwelling Form policy being endorsed, as returned by the NFIP Dwelling Form policy lookup.
        dwelling_change_id: Id class — the reference number of the pending coverage-increase request, as returned by the servicing-document lookup for that policy.
        change_effective_date: Fixed-format class — the date the coverage increase takes effect, written YYYY-MM-DD (calendar date, no time zone).
        risk_premium_charge: Fixed-format class — the endorsement charge on the risk premium line, in US dollars as a non-negative number with 2 decimal places, already rounded half-up to the cent.
        reserve_fund_charge: Fixed-format class — the endorsement charge on the reserve fund assessment line, in US dollars as a non-negative number with 2 decimal places, already rounded half-up to the cent.
        endorsed_risk_premium: Fixed-format class — the full-term risk premium that stands on the policy once the increase is in effect, in USD (US dollars) with 2 decimal places.

    Returns:
        A text receipt: "Coverage increase <request reference> effective <YYYY-MM-DD> on policy <policy reference>;
        contents <limit>; charges posted: <entry reference> <component> <amount>, ...; balance now <amount>." where
        limits are whole US dollars, amounts are US dollars with 2 decimals and the balance is the amount owed.
    """
    pol = ctx.find("dwelling_policies", dwelling_policy_id=dwelling_policy_id)[0]
    end = ctx.find("dwelling_changes", dwelling_change_id=dwelling_change_id)[0]
    ctx.update("dwelling_changes", dwelling_change_id, change_effective_date=change_effective_date)
    ctx.update("dwelling_policies", dwelling_policy_id,
               building_coverage=end.get("new_building_coverage"), contents_coverage=end.get("new_contents_coverage"),
               building_deductible=end.get("new_building_deductible"),
               contents_deductible=end.get("new_contents_deductible"),
               rated_risk_premium=round(float(endorsed_risk_premium), 2))
    day = ctx.now()[:10]
    posted, total = [], 0.0
    for comp, amt in (("RISK_PREMIUM", risk_premium_charge), ("RESERVE_FUND_ASSESSMENT", reserve_fund_charge)):
        amt = round(float(amt), 2)
        if amt <= 0:
            continue
        cid = ctx.make_id("dbl_", dwelling_policy_id, dwelling_change_id, change_effective_date, comp, amt)
        ctx.create("dwelling_billing", cid, dwelling_billing_id=cid, dwelling_policy_id=dwelling_policy_id,
                   customer_id=pol.get("customer_id"), event_type="dwelling_premium_charged",
                   term_start=pol.get("term_start"), component=comp, charge_basis="ENDORSEMENT", amount=amt,
                   posted_date=day, reference_id=dwelling_change_id, payment_ref="", payment_method="NONE",
                   payee="NONE")
        posted.append(f"{cid} {comp} {amt:.2f}")
        total += amt
    balance = round(float(pol.get("premium_balance") or 0) + total, 2)
    ctx.update("dwelling_policies", dwelling_policy_id, premium_balance=balance)
    return (f"Coverage increase {dwelling_change_id} effective {change_effective_date} on policy {dwelling_policy_id}; "
            f"contents {end.get('new_contents_coverage')}; charges posted: {', '.join(posted)}; "
            f"balance now {balance:.2f}.")

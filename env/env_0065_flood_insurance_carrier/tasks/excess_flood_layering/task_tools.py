"""Hidden task tools of the Excess Flood difficulty (env_0065, Tidemark Flood Insurance Company).

Each tool lands one atomic servicing action on an Excess Flood policy. The figures a tool books are the
figures handed to it; the only arithmetic a tool performs itself is the mechanical posting the charter
fixes at recorded values (the surplus lines tax and stamping fee at the rates recorded on the policy,
the fully earned policy fee, and calendar dates).
"""

from erlbench import ToolContext, tool


class _Cal:
    """Pure calendar arithmetic on 'YYYY-MM-DD' strings (proleptic Gregorian day numbers)."""

    @staticmethod
    def to_days(d):
        y, m, dd = int(d[0:4]), int(d[5:7]), int(d[8:10])
        y2 = y - (1 if m <= 2 else 0)
        era = (y2 if y2 >= 0 else y2 - 399) // 400
        yoe = y2 - era * 400
        mp = (m + 9) % 12
        doy = (153 * mp + 2) // 5 + dd - 1
        doe = yoe * 365 + yoe // 4 - yoe // 100 + doy
        return era * 146097 + doe - 719468

    @staticmethod
    def from_days(z):
        z = z + 719468
        era = (z if z >= 0 else z - 146096) // 146097
        doe = z - era * 146097
        yoe = (doe - doe // 1460 + doe // 36524 - doe // 146096) // 365
        y = yoe + era * 400
        doy = doe - (365 * yoe + yoe // 4 - yoe // 100)
        mp = (5 * doy + 2) // 153
        dd = doy - (153 * mp + 2) // 5 + 1
        m = mp + 3 if mp < 10 else mp - 9
        y = y + (1 if m <= 2 else 0)
        return "%04d-%02d-%02d" % (y, m, dd)

    @staticmethod
    def plus_one_year(d):
        y, m, dd = int(d[0:4]) + 1, int(d[5:7]), int(d[8:10])
        if m == 2 and dd == 29:
            dd = 28
        return "%04d-%02d-%02d" % (y, m, dd)


class _Post:
    """Mechanical ledger postings at values recorded on the policy."""

    POLICY_FEE = 150.0

    @staticmethod
    def levies(policy, taxable):
        tax = round(taxable * float(policy.get("surplus_lines_tax_pct") or 0) / 100, 2)
        stamp = round(taxable * float(policy.get("stamping_fee_pct") or 0) / 100, 2)
        return tax, stamp


@tool(owner="agent", rw="write")
def book_excess_renewal_30706efc(ctx: ToolContext, excess_policy_id: str, underlying_policy_number: str,
                                 term_premium: float) -> str:
    """Bind and book the next annual term of an Excess Flood policy whose renewal has been paid and whose
    underlying primary flood policy is on file. One call opens the new term on the policy record: the new
    term starts on the day the current term ends and runs one calendar year, the rated renewal premium
    becomes the policy's term premium, and the underlying policy the renewal is bound over is recorded on
    the policy. It books the renewal items of the new term on the premium account: the term premium
    given, the fully earned annual policy fee of 150.00, and the surplus lines tax and the stamping fee
    on the term premium plus the policy fee at the rates recorded on the policy (an item that comes to
    0.00 is not booked). The amount owed on the policy rises by the items booked, so a payment already
    received for the new term is set against them. Success is observable as the new term dates and term
    premium on the policy record and the renewal items on the premium account.

    Args:
        excess_policy_id: Id class — the reference number of the Excess Flood policy being renewed, as returned by the Excess Flood policy lookup.
        underlying_policy_number: Verbatim class — the policy number of the underlying primary flood policy the renewal is bound over, copied from the underlying declarations on file as returned by the Excess Flood servicing-document lookup, character for character with no reformatting (verbatim).
        term_premium: Fixed-format class — the rated full-term premium of the new term before the policy fee and taxes, in US dollars as a decimal number with 2 decimal places, already rounded to the cent.

    Returns:
        A confirmation sentence (string) on success, stating the policy reference number, the new term
        start and term end dates (YYYY-MM-DD), the term premium booked, the surplus lines tax and stamping
        fee booked (USD, 2 decimal places) and the amount owed on the policy after booking (USD, 2 decimal
        places; a negative figure is a credit standing in the insured's favour). If no Excess Flood
        policy has the reference number given, the string says so and nothing is booked.
    """
    rows = ctx.find("excess_policies", excess_policy_id=excess_policy_id)
    if not rows:
        return f"No Excess Flood policy {excess_policy_id}; nothing booked."
    pol = rows[0]
    start = pol.get("term_end")
    end = _Cal.plus_one_year(start)
    prem = round(float(term_premium), 2)
    fee = _Post.POLICY_FEE
    tax, stamp = _Post.levies(pol, prem + fee)
    today = ctx.now()[:10]
    items = [("TERM_PREMIUM", prem), ("POLICY_FEE", fee), ("SURPLUS_LINES_TAX", tax), ("STAMPING_FEE", stamp)]
    booked = 0.0
    for comp, amt in items:
        if amt <= 0:
            continue
        rid = ctx.make_id("xbl_", excess_policy_id, start, comp, "RENEWAL", prem)
        ctx.create("excess_billing", rid, excess_billing_id=rid, excess_policy_id=excess_policy_id,
                   customer_id=pol.get("customer_id"), event_type="excess_premium_charged", term_start=start,
                   component=comp, charge_basis="RENEWAL", amount=round(amt, 2), posted_date=today,
                   reference_id="", payment_ref="", payment_method="NONE", payee="NONE")
        booked += amt
    balance = round(float(pol.get("premium_balance") or 0) + booked, 2)
    ctx.update("excess_policies", excess_policy_id, term_start=start, term_end=end, term_premium=prem,
               underlying_policy_number=underlying_policy_number, premium_balance=balance)
    return (f"Renewal booked on {excess_policy_id}: term {start} to {end}, term premium {prem:.2f}, "
            f"surplus lines tax {tax:.2f}, stamping fee {stamp:.2f}; amount owed now {balance:.2f}.")


@tool(owner="user", rw="write")
def sign_excess_limit_increase_cddf0413(ctx: ToolContext, excess_policy_id: str, new_excess_building_limit: int,
                                        change_effective_date: str, additional_premium: float,
                                        revised_term_premium: float) -> str:
    """The named insured signs a request raising the excess dwelling limit of their Excess Flood policy,
    and the change is recorded as an endorsement. One call records the signed limit increase with its
    effective date, the new excess dwelling limit (the excess personal property limit is left as it is)
    and the full-term premium as endorsed; it updates the policy record to the new excess dwelling limit
    and the endorsed full-term premium; and it books on the premium account the additional premium given
    as an endorsement premium item for the current term, together with the surplus lines tax and the
    stamping fee on it at the rates recorded on the policy (an item that comes to 0.00 is not booked).
    The amount owed on the policy rises by the items booked, so a credit already standing on the policy
    is set against them. Success is observable as the endorsement on the servicing record, the new limit
    on the policy and the endorsement items on the premium account.

    Args:
        excess_policy_id: Id class — the reference number of the insured's Excess Flood policy, as returned by the Excess Flood policy lookup.
        new_excess_building_limit: Fixed-format class — the excess dwelling limit after the increase, in whole US dollars as an integer with no separators.
        change_effective_date: Fixed-format class — the date the increase takes effect, as a calendar date in the format YYYY-MM-DD.
        additional_premium: Fixed-format class — the additional premium charged for the increase before taxes, in US dollars as a decimal number with 2 decimal places, already rounded to the cent.
        revised_term_premium: Fixed-format class — the full-term premium of the policy as endorsed, in US dollars as a decimal number with 2 decimal places, already rounded to the cent.

    Returns:
        A confirmation sentence (string) on success, stating the endorsement reference number, the new
        excess dwelling limit (whole US dollars), the effective date (YYYY-MM-DD), the additional premium,
        surplus lines tax and stamping fee booked (USD, 2 decimal places) and the amount owed on the
        policy afterwards (USD, 2 decimal places; a negative figure is a credit standing in the insured's
        favour). If no Excess Flood policy has the reference number given, the string says so and nothing
        is recorded.
    """
    rows = ctx.find("excess_policies", excess_policy_id=excess_policy_id)
    if not rows:
        return f"No Excess Flood policy {excess_policy_id}; nothing recorded."
    pol = rows[0]
    today = ctx.now()[:10]
    limit = int(new_excess_building_limit)
    add = round(float(additional_premium), 2)
    revised = round(float(revised_term_premium), 2)
    eid = ctx.make_id("xch_", excess_policy_id, "LIMIT_INCREASE", change_effective_date, limit, add, revised)
    ctx.create("excess_changes", eid, excess_change_id=eid, excess_policy_id=excess_policy_id,
               customer_id=pol.get("customer_id"), event_type="excess_endorsement_issued",
               change_type="LIMIT_INCREASE", change_effective_date=change_effective_date, recorded_date=today,
               new_excess_building_limit=limit, new_excess_contents_limit=int(pol.get("excess_contents_limit") or 0),
               revised_term_premium=revised, underlying_type="NONE", underlying_carrier="",
               underlying_policy_number="", underlying_term_start="", underlying_expiration_date="",
               underlying_building_limit=0, underlying_contents_limit=0, renewal_term_start="",
               notice_reason="NONE", notice_effective_date="")
    tax, stamp = _Post.levies(pol, add)
    booked = 0.0
    for comp, amt in (("ENDORSEMENT_PREMIUM", add), ("SURPLUS_LINES_TAX", tax), ("STAMPING_FEE", stamp)):
        if amt <= 0:
            continue
        rid = ctx.make_id("xbl_", eid, comp)
        ctx.create("excess_billing", rid, excess_billing_id=rid, excess_policy_id=excess_policy_id,
                   customer_id=pol.get("customer_id"), event_type="excess_premium_charged",
                   term_start=pol.get("term_start"), component=comp, charge_basis="ENDORSEMENT",
                   amount=round(amt, 2), posted_date=today, reference_id=eid, payment_ref="",
                   payment_method="NONE", payee="NONE")
        booked += amt
    balance = round(float(pol.get("premium_balance") or 0) + booked, 2)
    ctx.update("excess_policies", excess_policy_id, excess_building_limit=limit, term_premium=revised,
               premium_balance=balance)
    return (f"Limit increase recorded as endorsement {eid}: excess dwelling limit {limit} effective "
            f"{change_effective_date}; additional premium {add:.2f}, surplus lines tax {tax:.2f}, stamping "
            f"fee {stamp:.2f}; amount owed now {balance:.2f}.")


@tool(owner="agent", rw="write")
def pay_excess_loss_of_use_f5cb8480(ctx: ToolContext, excess_policy_id: str, claim_number: str,
                                    payment_amount: float) -> str:
    """Issue one loss-of-use (additional living expense) payment to the insured on an Excess Flood claim.
    One call records on the claim file a payment item for the loss-of-use coverage of the claim named,
    payable to the insured, dated today and carrying the claim's date of loss as recorded at first notice;
    a check reference is assigned to the item. The net excess claim money issued on the policy rises by the
    amount. Success is observable as the new payment item on the claim file.

    Args:
        excess_policy_id: Id class — the reference number of the Excess Flood policy the claim is made under, as returned by the Excess Flood policy lookup.
        claim_number: Verbatim class — the excess claim number exactly as it appears on the claim file returned by the Excess Flood claim lookup, copied character for character with no reformatting (verbatim).
        payment_amount: Fixed-format class — the amount to issue, in US dollars as a positive decimal number with 2 decimal places, already rounded to the cent.

    Returns:
        A confirmation sentence (string) on success, stating the claim number, the coverage paid (loss of use),
        the amount issued (USD, 2 decimal places), the payee (the insured), the payment date (YYYY-MM-DD) and
        the check reference assigned (text). If no Excess Flood policy has the reference number given, the
        string says so and nothing is issued.
    """
    rows = ctx.find("excess_policies", excess_policy_id=excess_policy_id)
    if not rows:
        return f"No Excess Flood policy {excess_policy_id}; nothing issued."
    pol = rows[0]
    first = ctx.find("excess_claims", excess_policy_id=excess_policy_id, claim_number=claim_number,
                     event_type="excess_claim_reported")
    dol = first[0].get("date_of_loss") if first else ""
    today = ctx.now()[:10]
    amt = round(float(payment_amount), 2)
    rid = ctx.make_id("xcl_", excess_policy_id, claim_number, "LOSS_OF_USE", amt, today)
    ref = "XL-4" + rid[-7:].upper()
    ctx.create("excess_claims", rid, excess_claim_event_id=rid, excess_policy_id=excess_policy_id,
               customer_id=pol.get("customer_id"), event_type="excess_claim_paid", claim_number=claim_number,
               underlying_claim_number="", date_of_loss=dol, event_date=today, report_type="NONE",
               coverage_part="LOSS_OF_USE", building_covered_loss=0.0, contents_covered_loss=0.0,
               loss_of_use_incurred=0.0, underlying_paid_building=0.0, underlying_paid_contents=0.0,
               claimed_amount=0.0, payment_amount=amt, payment_ref=ref, payee="INSURED", denial_reason="NONE")
    return (f"Loss-of-use payment issued on claim {claim_number}: {amt:.2f} to the insured on {today}, "
            f"check reference {ref}.")


@tool(owner="user", rw="write")
def sign_excess_sale_cancellation_a26754a5(ctx: ToolContext, excess_policy_id: str, cancellation_effective_date: str,
                                           returned_premium: float) -> str:
    """The named insured signs the cancellation of their Excess Flood policy because the insured home was sold,
    with the settlement statement as the supporting document. One call records the signed cancellation request
    (reason: property sold), sets the policy to cancelled with the cancellation effective date given and today
    as the processing date, credits the returned premium given as a cancellation credit of the term premium of
    the current term together with the surplus lines tax and stamping fee on it at the rates recorded on the
    policy (an item that comes to 0.00 is not credited), and refunds the total credited to the insured with a
    refund reference. The amount owed on the policy falls by the credits and rises by the refund. Success is
    observable as the cancelled status, the signed request, the credit items and the refund on the account.

    Args:
        excess_policy_id: Id class — the reference number of the insured's Excess Flood policy, as returned by the Excess Flood policy lookup.
        cancellation_effective_date: Fixed-format class — the date the cancellation takes effect, as a calendar date in the format YYYY-MM-DD.
        returned_premium: Fixed-format class — the term premium returned on the cancellation before taxes, in US dollars as a decimal number with 2 decimal places, already rounded to the cent.

    Returns:
        A confirmation sentence (string) on success, stating the signed request's reference number, the policy
        status (cancelled), the effective date (YYYY-MM-DD), the returned premium, the surplus lines tax and
        stamping fee returned (USD, 2 decimal places), the total refunded to the insured (USD, 2 decimal
        places) and the refund reference (text). If no Excess Flood policy has the reference number given, the
        string says so and nothing is recorded.
    """
    rows = ctx.find("excess_policies", excess_policy_id=excess_policy_id)
    if not rows:
        return f"No Excess Flood policy {excess_policy_id}; nothing recorded."
    pol = rows[0]
    now = ctx.now()
    today = now[:10]
    ret = round(float(returned_premium), 2)
    qid = ctx.make_id("xrq_", excess_policy_id, "PROPERTY_SOLD", cancellation_effective_date, ret)
    ctx.create("excess_requests", qid, excess_request_id=qid, customer_id=pol.get("customer_id"),
               excess_policy_id=excess_policy_id, request_type="CANCELLATION", cancellation_reason="PROPERTY_SOLD",
               requested_effective_date=cancellation_effective_date, supporting_document="SETTLEMENT_STATEMENT",
               outcome="SIGNED", created_at=now)
    tax, stamp = _Post.levies(pol, ret)
    credited = 0.0
    for comp, amt in (("TERM_PREMIUM", ret), ("SURPLUS_LINES_TAX", tax), ("STAMPING_FEE", stamp)):
        if amt <= 0:
            continue
        cid = ctx.make_id("xbl_", qid, comp, "CANCELLATION")
        ctx.create("excess_billing", cid, excess_billing_id=cid, excess_policy_id=excess_policy_id,
                   customer_id=pol.get("customer_id"), event_type="excess_premium_credit",
                   term_start=pol.get("term_start"), component=comp, charge_basis="CANCELLATION",
                   amount=round(amt, 2), posted_date=today, reference_id=qid, payment_ref="",
                   payment_method="NONE", payee="NONE")
        credited += amt
    credited = round(credited, 2)
    fid = ctx.make_id("xbl_", qid, "REFUND")
    fref = "RF-4" + fid[-7:].upper()
    if credited > 0:
        ctx.create("excess_billing", fid, excess_billing_id=fid, excess_policy_id=excess_policy_id,
                   customer_id=pol.get("customer_id"), event_type="excess_refund_disbursed", term_start="",
                   component="TOTAL", charge_basis="REFUND", amount=credited, posted_date=today, reference_id=qid,
                   payment_ref=fref, payment_method="NONE", payee="INSURED")
    ctx.update("excess_policies", excess_policy_id, status="cancelled", cancellation_reason="PROPERTY_SOLD",
               cancellation_effective_date=cancellation_effective_date, closed_date=today)
    return (f"Cancellation request {qid} signed; policy {excess_policy_id} cancelled effective "
            f"{cancellation_effective_date}; returned premium {ret:.2f}, surplus lines tax {tax:.2f}, stamping fee "
            f"{stamp:.2f}; refunded {credited:.2f} to the insured, reference {fref}.")

"""Hidden task tools for renewals_transfers_and_early_exit (Lease Term Agreements).

Each tool performs one atomic write on the Lease Term Agreement records and is reached only through
unlock_* -> call_*; its name is published through the term charter's extended policies.
"""

from erlbench import ToolContext, tool


@tool(owner="agent", rw="write")
def reissue_renewal_offer_line_9239b766(ctx: ToolContext, term_id: str, offer_id: str, offered_rent: float,
                                        offer_expiration_date: str) -> str:
    """Re-issue one renewal offer line on an expiring Lease Term Agreement at a corrected monthly rent.

    A resident services agent uses this to replace a renewal offer line that was delivered at the wrong rent.
    One call delivers a new offer line on the same expiring term, for the same term program and the same term
    length as the line being replaced, dated today, carrying the monthly rent and the last acceptance date
    passed in. The replaced line stays on file unchanged as history. Afterwards the resident sees two lines for
    that term program on the expiring term, the newest one dated today at the rent passed in.

    Args:
        term_id: Id class — the reference number of the expiring Lease Term Agreement the offer is made on, as
            returned by the lease term lookup.
        offer_id: Id class — the reference number of the renewal offer line being replaced, as returned by the
            renewal offer lookup for that term.
        offered_rent: Fixed-format class — the corrected monthly base rent of the new offer line before any
            early renewal discount, in USD with 2 decimal places (for example 1875.40), already rounded to the
            cent; never empty.
        offer_expiration_date: Fixed-format class — the last date on which the new offer line may be accepted,
            written YYYY-MM-DD; never empty.

    Returns:
        A dictionary receipt: offer_id (str, the reference number of the newly delivered offer line), term_id
        (str, the expiring term), offered_variant (str, the term program of the line), offered_term_months (int,
        the term length of the line in months), offered_rent (float, USD with 2 decimal places, the rent booked
        on the line), offer_date (str, YYYY-MM-DD, today) and offer_expiration_date (str, YYYY-MM-DD, the last
        acceptance date). A receipt carrying the new offer_id means the corrected line was delivered.
    """
    old = ctx.find("term_offers", offer_id=offer_id)
    src = old[0] if old else {}
    today = ctx.now()[:10]
    rid = ctx.make_id("tof_", term_id, offer_id, offered_rent, offer_expiration_date)
    ctx.create("term_offers", rid, offer_id=rid, term_id=term_id, customer_id=src.get("customer_id"),
               event_type="term_renewal_offer", offered_variant=src.get("offered_variant"),
               offered_term_months=src.get("offered_term_months"), offered_rent=round(float(offered_rent), 2),
               offer_date=today, offer_expiration_date=offer_expiration_date)
    return str({"offer_id": rid, "term_id": term_id, "offered_variant": src.get("offered_variant"),
                "offered_term_months": src.get("offered_term_months"),
                "offered_rent": round(float(offered_rent), 2), "offer_date": today,
                "offer_expiration_date": offer_expiration_date})


@tool(owner="user", rw="write")
def sign_renewal_term_7151ccb7(ctx: ToolContext, lease_id: str, offer_id: str, term_start_date: str,
                               term_end_date: str, contracted_rent: float) -> str:
    """Sign a renewal of the resident's own apartment home lease by accepting one renewal offer line.

    The resident uses this to sign a renewal Lease Term Agreement on their lease. One call writes a new term
    agreement on the lease with origin renewal and status pending, on the term program and term length of the
    accepted offer line, running from the start date to the end date given, at the monthly contracted rent
    given, signed today. The expiring term is not changed by this call. Afterwards the resident has a signed,
    pending renewal term on file that takes effect on its start date.

    Args:
        lease_id: Id class — the reference number of the resident's apartment home lease, as returned by the
            lease lookup.
        offer_id: Id class — the reference number of the renewal offer line being accepted, as returned by the
            renewal offer lookup for the expiring term.
        term_start_date: Fixed-format class — the first day of the renewal term, written YYYY-MM-DD.
        term_end_date: Fixed-format class — the last day of the renewal term, written YYYY-MM-DD.
        contracted_rent: Fixed-format class — the monthly base rent agreed for the renewal term, in USD with 2
            decimal places, already rounded to the cent; never empty.

    Returns:
        A dictionary receipt: term_id (str, the reference number of the new renewal term), lease_id (str),
        variant_name (str, the term program signed), term_months (int, length in months), term_start_date and
        term_end_date (str, YYYY-MM-DD), contracted_rent (float, USD with 2 decimal places), signed_date (str,
        YYYY-MM-DD, today) and status (str, always pending). A receipt with status pending means the renewal
        was signed.
    """
    offer = (ctx.find("term_offers", offer_id=offer_id) or [{}])[0]
    lease = (ctx.find("leases", lease_id=lease_id) or [{}])[0]
    today = ctx.now()[:10]
    rid = ctx.make_id("trm_", lease_id, offer_id, term_start_date, term_end_date, contracted_rent)
    ctx.create("lease_terms", rid, term_id=rid, customer_id=lease.get("customer_id"), lease_id=lease_id,
               variant_name=offer.get("offered_variant"), status="pending", term_origin="renewal",
               term_start_date=term_start_date, term_end_date=term_end_date,
               term_months=offer.get("offered_term_months"), contracted_rent=round(float(contracted_rent), 2),
               signed_date=today, notice_to_vacate_date="", intended_move_out_date="", balance_due=0.0,
               closed_date="")
    return str({"term_id": rid, "lease_id": lease_id, "variant_name": offer.get("offered_variant"),
                "term_months": offer.get("offered_term_months"), "term_start_date": term_start_date,
                "term_end_date": term_end_date, "contracted_rent": round(float(contracted_rent), 2),
                "signed_date": today, "status": "pending"})


@tool(owner="agent", rw="write")
def book_concession_recapture_8b577669(ctx: ToolContext, term_id: str, request_id: str, amount: float) -> str:
    """Book a concession recapture charge on a Lease Term Agreement account for one early exit request.

    A resident services agent uses this to post the unearned part of the move-in concession that the resident owes
    back because the term ends early. One call adds one concession recapture charge line on the term account, tied
    to the exit request given and dated today, and raises the term's outstanding balance by the amount. Afterwards
    the resident's term account shows the recapture line and the higher balance.

    Args:
        term_id: Id class — the reference number of the Lease Term Agreement the charge posts to, as returned by the
            lease term lookup.
        request_id: Id class — the reference number of the early termination or lease break request the charge
            arises from, as returned by the term change request lookup.
        amount: Fixed-format class — the recapture amount charged, in USD with 2 decimal places, a positive figure
            already rounded to the cent; never empty.

    Returns:
        A dictionary receipt: term_charge_id (str, the reference number of the new charge line), term_id (str),
        request_id (str), fee_code (str, always concession_recapture), amount (float, USD with 2 decimal places),
        assessed_date (str, YYYY-MM-DD, today) and balance_due (float, USD with 2 decimal places, the term balance
        after the charge). A receipt carrying a term_charge_id means the charge was booked.
    """
    term = (ctx.find("lease_terms", term_id=term_id) or [{}])[0]
    today = ctx.now()[:10]
    rid = ctx.make_id("tch_", term_id, request_id, "concession_recapture", amount)
    ctx.create("term_charges", rid, term_charge_id=rid, term_id=term_id, customer_id=term.get("customer_id"),
               event_type="term_fee_assessment", fee_code="concession_recapture", amount=round(float(amount), 2),
               assessed_date=today, billing_period=today[:7], days_charged=0, request_id=request_id,
               source_term_charge_id=None, payment_method="not_applicable", payment_reference="")
    new_balance = round(float(term.get("balance_due") or 0) + float(amount), 2)
    ctx.update("lease_terms", term_id, balance_due=new_balance)
    return str({"term_charge_id": rid, "term_id": term_id, "request_id": request_id, "fee_code": "concession_recapture",
                "amount": round(float(amount), 2), "assessed_date": today, "balance_due": new_balance})


@tool(owner="agent", rw="write")
def book_exit_notice_charge_a2fdf71c(ctx: ToolContext, term_id: str, request_id: str, days_charged: int,
                                     amount: float) -> str:
    """Book an insufficient notice charge on a Lease Term Agreement account for one early exit request.

    A resident services agent uses this to post the charge for the days of notice an exit request falls short of.
    One call adds one insufficient notice charge line on the term account, tied to the exit request given, dated
    today, recording the number of days charged and the amount, and raises the term's outstanding balance by the
    amount. Afterwards the resident's term account shows the notice charge line and the higher balance.

    Args:
        term_id: Id class — the reference number of the Lease Term Agreement the charge posts to, as returned by the
            lease term lookup.
        request_id: Id class — the reference number of the early termination or lease break request the charge
            arises from, as returned by the term change request lookup.
        days_charged: Fixed-format class — the number of days of notice short that the charge bills, an integer count
            of days, zero or more.
        amount: Fixed-format class — the charge amount, in USD with 2 decimal places, a positive figure already
            rounded to the cent; never empty.

    Returns:
        A dictionary receipt: term_charge_id (str, the reference number of the new charge line), term_id (str),
        request_id (str), fee_code (str, always insufficient_notice_charge), days_charged (int), amount (float, USD
        with 2 decimal places), assessed_date (str, YYYY-MM-DD, today) and balance_due (float, USD with 2 decimal
        places, the term balance after the charge). A receipt carrying a term_charge_id means the charge was booked.
    """
    term = (ctx.find("lease_terms", term_id=term_id) or [{}])[0]
    today = ctx.now()[:10]
    rid = ctx.make_id("tch_", term_id, request_id, "insufficient_notice_charge", days_charged, amount)
    ctx.create("term_charges", rid, term_charge_id=rid, term_id=term_id, customer_id=term.get("customer_id"),
               event_type="term_fee_assessment", fee_code="insufficient_notice_charge",
               amount=round(float(amount), 2), assessed_date=today, billing_period=today[:7],
               days_charged=int(days_charged), request_id=request_id, source_term_charge_id=None,
               payment_method="not_applicable", payment_reference="")
    new_balance = round(float(term.get("balance_due") or 0) + float(amount), 2)
    ctx.update("lease_terms", term_id, balance_due=new_balance)
    return str({"term_charge_id": rid, "term_id": term_id, "request_id": request_id,
                "fee_code": "insufficient_notice_charge", "days_charged": int(days_charged),
                "amount": round(float(amount), 2), "assessed_date": today, "balance_due": new_balance})


@tool(owner="user", rw="write")
def sign_lease_break_agreement_f74cee5b(ctx: ToolContext, term_id: str, request_id: str, reletting_fee: float,
                                        quoted_amount: float) -> str:
    """Sign a lease break agreement that ends the resident's own Lease Term Agreement early.

    The resident uses this to sign the lease break they asked for. One call marks the exit request as signed with
    the total exit charges quoted, ends the term as terminated early with the termination date asked for on the
    request as its move-out date and today as its closing date, and adds one reletting fee charge line tied to the
    request on the term account, raising the term's outstanding balance by the reletting fee. Afterwards the
    resident sees a signed agreement, a term that is terminated early and the reletting fee on the term account.

    Args:
        term_id: Id class — the reference number of the Lease Term Agreement being ended, as returned by the lease
            term lookup.
        request_id: Id class — the reference number of the lease break request being signed, as returned by the term
            change request lookup.
        reletting_fee: Fixed-format class — the reletting fee charged for the lease break, in USD with 2 decimal
            places, a positive figure already rounded to the cent; never empty.
        quoted_amount: Fixed-format class — the total exit charges written on the signed agreement, in USD with 2
            decimal places, already rounded to the cent; never empty.

    Returns:
        A dictionary receipt: request_id (str), request_status (str, always signed), quoted_amount (float, USD with
        2 decimal places), term_id (str), term_status (str, always terminated_early), move_out_date (str, YYYY-MM-DD,
        the termination date on the request), reletting_fee_charge_id (str, the reference number of the reletting
        fee line) and balance_due (float, USD with 2 decimal places, the term balance after the fee). A receipt with
        request_status signed means the agreement was signed.
    """
    term = (ctx.find("lease_terms", term_id=term_id) or [{}])[0]
    req = (ctx.find("term_change_requests", request_id=request_id) or [{}])[0]
    today = ctx.now()[:10]
    rid = ctx.make_id("tch_", term_id, request_id, "reletting_fee", reletting_fee, quoted_amount)
    ctx.create("term_charges", rid, term_charge_id=rid, term_id=term_id, customer_id=term.get("customer_id"),
               event_type="term_fee_assessment", fee_code="reletting_fee", amount=round(float(reletting_fee), 2),
               assessed_date=today, billing_period=today[:7], days_charged=0, request_id=request_id,
               source_term_charge_id=None, payment_method="not_applicable", payment_reference="")
    ctx.update("term_change_requests", request_id, request_status="signed",
               quoted_amount=round(float(quoted_amount), 2))
    new_balance = round(float(term.get("balance_due") or 0) + float(reletting_fee), 2)
    ctx.update("lease_terms", term_id, status="terminated_early", intended_move_out_date=req.get("requested_date"),
               closed_date=today, balance_due=new_balance)
    return str({"request_id": request_id, "request_status": "signed", "quoted_amount": round(float(quoted_amount), 2),
                "term_id": term_id, "term_status": "terminated_early", "move_out_date": req.get("requested_date"),
                "reletting_fee_charge_id": rid, "balance_due": new_balance})

"""Hidden task tools of the small_business_electricity_care difficulty (Beacon Ridge Energy).

Each tool performs one atomic business write on a small business electricity agreement or on its
bill. Tools judge no eligibility, compute no amount, rate or date and validate no prerequisite: the
agent decides every value from the published policies and the records, and the tool lands it.
"""

from erlbench import ToolContext, tool


@tool(owner="user", rw="write")
def accept_renewal_offer_d4784688(ctx: ToolContext, bizpower_agreement_id: str, renewed_plan_name: str,
                                  term_months: int, renewal_rate_cents_kwh: float,
                                  new_term_start_date: str, new_contract_end_date: str) -> str:
    """The business's authorized representative explicitly accepts the renewal offer on one of its
    small business electricity agreements while its current term is still in force. The agreement keeps its
    agreement number and site and is set to continue into the renewed plan: the plan name, term
    length, renewal rate, start date of the renewed term and end date of the renewed term are
    recorded on the agreement, the renewal election is recorded as accepted with today's date, and
    the term is marked as explicitly accepted rather than automatically renewed. The representative
    sees the agreement continuing into the renewed plan at the accepted rate on the next statement.

    Args:
        bizpower_agreement_id: Id class — the agreement number of the small business electricity
            agreement being renewed, as shown on the agreement record returned by the agreement lookup.
        renewed_plan_name: Enum class — the official plan the agreement continues into, written exactly
            as one of: Beacon Ridge Business Monthly Variable (the month-to-month plan, used only when the
            offer being accepted names that plan); Beacon Ridge Business Fixed 12 (the offer being accepted
            names the 12-month fixed plan); Beacon Ridge Business Fixed 24 (the offer names the 24-month
            fixed plan); Beacon Ridge Business Fixed 36 (the offer names the 36-month fixed plan);
            Beacon Ridge Business Green 24 (the offer names the 24-month renewable plan); Beacon Ridge
            Business Green 36 (the offer names the 36-month renewable plan).
        term_months: Fixed-format class — the length of the renewed term in integer months, written without units or decimals (for example 36).
        renewal_rate_cents_kwh: Fixed-format class — the supply rate of the renewed term in cents per kWh,
            a decimal number with 2 decimal places (for example 8.75), already rounded half up to the cent.
        new_term_start_date: Fixed-format class — the start date of the renewed term, as a calendar date
            in the format YYYY-MM-DD.
        new_contract_end_date: Fixed-format class — the end date of the renewed term, as a calendar date
            in the format YYYY-MM-DD.

    Returns:
        A dictionary receipt: agreement_id (the agreement number renewed), status ("renewal_accepted"
        when the acceptance was recorded), plan (the plan now in force from the renewed term),
        term_months (integer months of the renewed term), rate_cents_kwh (the accepted rate, 2 decimals),
        term_start (YYYY-MM-DD start date of the renewed term), term_end (YYYY-MM-DD end date of the
        renewed term) and accepted_on (YYYY-MM-DD date the acceptance was recorded).
    """
    today = ctx.now()[:10]
    ctx.update("bizpower_agreements", bizpower_agreement_id, variant_name=renewed_plan_name,
               term_months=int(term_months), contract_rate_cents_kwh=round(float(renewal_rate_cents_kwh), 2),
               plan_change_date=new_term_start_date, contract_end_date=new_contract_end_date,
               renewal_election="accepted", renewal_election_date=today, auto_renewed=False)
    return str({"agreement_id": bizpower_agreement_id, "status": "renewal_accepted",
                "plan": renewed_plan_name, "term_months": int(term_months),
                "rate_cents_kwh": round(float(renewal_rate_cents_kwh), 2), "term_start": new_term_start_date,
                "term_end": new_contract_end_date, "accepted_on": today})


@tool(owner="agent", rw="write")
def post_multi_site_credit_fd52d0a7(ctx: ToolContext, bizpower_agreement_id: str, billing_period_start: str,
                                    credit_amount_usd: float) -> str:
    """Posts one multi-site bill credit on a small business electricity agreement for one billing
    cycle. A new credit line is added to the agreement's bill, tied to the billing cycle named, with
    the credit amount entered as a reduction of the amount billed and today's posting date. The
    business sees the multi-site credit on the statement of that cycle's account.

    Args:
        bizpower_agreement_id: Id class — the agreement number of the small business electricity
            agreement credited, as shown on the agreement record returned by the agreement lookup.
        billing_period_start: Fixed-format class — the start date of the billing cycle the credit belongs
            to, as a calendar date in the format YYYY-MM-DD, copied from that cycle's bill lines.
        credit_amount_usd: Fixed-format class — the size of the credit in USD as a positive number with
            2 decimal places (for example 12.40), already rounded half up to the cent; the tool records it
            as a reduction of the bill.

    Returns:
        A dictionary receipt: billing_line_id (the new credit line's reference), agreement_id (the
        agreement credited), line ("multi_site_credit"), cycle_start (YYYY-MM-DD cycle credited),
        amount_usd (the signed line amount, negative, 2 decimals) and posted_on (YYYY-MM-DD posting
        date). A receipt carrying a billing_line_id means the credit is on the bill.
    """
    amount = -round(float(credit_amount_usd), 2)
    rid = ctx.make_id("bpb_", bizpower_agreement_id, "multi_site_credit", billing_period_start, credit_amount_usd)
    today = ctx.now()[:10]
    ctx.create("bizpower_billing", rid, bizpower_billing_id=rid, bizpower_agreement_id=bizpower_agreement_id,
               customer_id=(ctx.find("bizpower_agreements", bizpower_agreement_id=bizpower_agreement_id) or [{}])[0].get("customer_id", ""), premise_id=None, event_type="bizpower_credit",
               line_type="multi_site_credit", billing_period_start=billing_period_start, billing_period_end="",
               usage_kwh=0, rate_cents_kwh=0.0, tax_rate_pct=0.0, taxable_amount_usd=0.0, amount_usd=amount,
               posted_date=today, source_billing_id="", etf_months_remaining=0, etf_remaining_kwh=0)
    return str({"billing_line_id": rid, "agreement_id": bizpower_agreement_id, "line": "multi_site_credit",
                "cycle_start": billing_period_start, "amount_usd": amount, "posted_on": today})


@tool(owner="agent", rw="write")
def post_early_termination_fee_113aa1f4(ctx: ToolContext, bizpower_agreement_id: str, premise_id: str,
                                        etf_months_remaining: int, etf_remaining_kwh: int,
                                        fee_amount_usd: float) -> str:
    """Bills the early termination fee on a small business electricity agreement whose cancellation
    is on record. A new fee line is added to the agreement's bill with the site supplied at
    termination, the remaining months and remaining kWh the fee was measured on, the fee amount and
    today's posting date. The business sees the early termination fee on its next statement.

    Args:
        bizpower_agreement_id: Id class — the agreement number of the cancelled small business
            electricity agreement, as shown on the agreement record returned by the agreement lookup.
        premise_id: Id class — the reference number of the site the agreement supplied at termination,
            as shown in the site field of that agreement record.
        etf_months_remaining: Fixed-format class — the remaining months the fee was measured on, in
            integer months, written without decimals.
        etf_remaining_kwh: Fixed-format class — the estimated remaining usage the fee was measured on, in
            integer kWh, written without decimals or separators.
        fee_amount_usd: Fixed-format class — the early termination fee in USD as a positive number with
            2 decimal places, already rounded half up to the cent.

    Returns:
        A dictionary receipt: billing_line_id (the new fee line's reference), agreement_id (the
        agreement charged), line ("early_termination_fee"), site_id (the site recorded on the fee),
        months_remaining (integer months), remaining_kwh (integer kWh), amount_usd (the fee, positive,
        2 decimals) and posted_on (YYYY-MM-DD). A receipt carrying a billing_line_id means the fee is
        billed.
    """
    amount = round(float(fee_amount_usd), 2)
    rid = ctx.make_id("bpb_", bizpower_agreement_id, "early_termination_fee", premise_id, etf_months_remaining,
                      etf_remaining_kwh, fee_amount_usd)
    today = ctx.now()[:10]
    ctx.create("bizpower_billing", rid, bizpower_billing_id=rid, bizpower_agreement_id=bizpower_agreement_id,
               customer_id=(ctx.find("bizpower_agreements", bizpower_agreement_id=bizpower_agreement_id) or [{}])[0].get("customer_id", ""), premise_id=premise_id,
               event_type="bizpower_fee_charge", line_type="early_termination_fee", billing_period_start="",
               billing_period_end="", usage_kwh=0, rate_cents_kwh=0.0, tax_rate_pct=0.0, taxable_amount_usd=0.0,
               amount_usd=amount, posted_date=today, source_billing_id="",
               etf_months_remaining=int(etf_months_remaining), etf_remaining_kwh=int(etf_remaining_kwh))
    return str({"billing_line_id": rid, "agreement_id": bizpower_agreement_id, "line": "early_termination_fee",
                "site_id": premise_id, "months_remaining": int(etf_months_remaining),
                "remaining_kwh": int(etf_remaining_kwh), "amount_usd": amount, "posted_on": today})


@tool(owner="agent", rw="write")
def post_renewal_loyalty_credit_e53d7f06(ctx: ToolContext, bizpower_agreement_id: str, billing_period_start: str,
                                         credit_amount_usd: float) -> str:
    """Posts the renewal loyalty bill credit on a small business electricity agreement. A new credit
    line is added to the agreement's bill, tied to the billing cycle named, with the credit amount
    entered as a reduction of the amount billed and today's posting date. The business sees the
    loyalty credit on the statement of that cycle.

    Args:
        bizpower_agreement_id: Id class — the agreement number of the renewed small business electricity
            agreement, as shown on the agreement record returned by the agreement lookup.
        billing_period_start: Fixed-format class — the start date of the billing cycle on whose bill the
            credit appears, as a calendar date in the format YYYY-MM-DD.
        credit_amount_usd: Fixed-format class — the size of the credit in USD as a positive number with
            2 decimal places, already rounded half up to the cent; the tool records it as a reduction of
            the bill.

    Returns:
        A dictionary receipt: billing_line_id (the new credit line's reference), agreement_id (the
        agreement credited), line ("renewal_loyalty_credit"), cycle_start (YYYY-MM-DD), amount_usd (the
        signed line amount, negative, 2 decimals) and posted_on (YYYY-MM-DD). A receipt carrying a
        billing_line_id means the credit is on the bill.
    """
    amount = -round(float(credit_amount_usd), 2)
    rid = ctx.make_id("bpb_", bizpower_agreement_id, "renewal_loyalty_credit", billing_period_start, credit_amount_usd)
    today = ctx.now()[:10]
    ctx.create("bizpower_billing", rid, bizpower_billing_id=rid, bizpower_agreement_id=bizpower_agreement_id,
               customer_id=(ctx.find("bizpower_agreements", bizpower_agreement_id=bizpower_agreement_id) or [{}])[0].get("customer_id", ""), premise_id=None, event_type="bizpower_credit",
               line_type="renewal_loyalty_credit", billing_period_start=billing_period_start, billing_period_end="",
               usage_kwh=0, rate_cents_kwh=0.0, tax_rate_pct=0.0, taxable_amount_usd=0.0, amount_usd=amount,
               posted_date=today, source_billing_id="", etf_months_remaining=0, etf_remaining_kwh=0)
    return str({"billing_line_id": rid, "agreement_id": bizpower_agreement_id, "line": "renewal_loyalty_credit",
                "cycle_start": billing_period_start, "amount_usd": amount, "posted_on": today})


@tool(owner="user", rw="write")
def accept_grace_period_renewal_906a45d5(ctx: ToolContext, bizpower_agreement_id: str, renewed_plan_name: str,
                                         term_months: int, renewal_rate_cents_kwh: float,
                                         new_term_start_date: str, new_contract_end_date: str) -> str:
    """The business's authorized representative accepts the renewal offer on a small business
    electricity agreement that has already rolled over to month-to-month supply, within the grace
    period that follows the rollover. The agreement keeps its agreement number and site and returns to
    a fixed term: the plan name, term length, renewal rate, start date and end date of the renewed term
    are recorded on it, the renewal election is recorded as accepted with today's date, and the term
    is marked as explicitly accepted rather than automatically renewed. The representative sees the
    agreement on the renewed fixed plan at the accepted rate from the renewed term's start date.

    Args:
        bizpower_agreement_id: Id class — the agreement number of the rolled-over small business
            electricity agreement, as shown on the agreement record returned by the agreement lookup.
        renewed_plan_name: Enum class — the official plan the agreement returns to, written exactly as
            one of these: Beacon Ridge Business Monthly Variable (the month-to-month plan, used only when the offer
            being accepted names that plan); Beacon Ridge Business Fixed 12 (the offer being accepted names
            the 12-month fixed plan); Beacon Ridge Business Fixed 24 (the offer names the 24-month fixed
            plan); Beacon Ridge Business Fixed 36 (the offer names the 36-month fixed plan); Beacon Ridge
            Business Green 24 (the offer names the 24-month renewable plan); Beacon Ridge Business Green 36
            (the offer names the 36-month renewable plan).
        term_months: Fixed-format class — the length of the renewed term in integer months, written
            without units or decimals (for example 12).
        renewal_rate_cents_kwh: Fixed-format class — the supply rate of the renewed term in cents per kWh,
            a decimal number with 2 decimal places (for example 8.75), already rounded half up to the cent.
        new_term_start_date: Fixed-format class — the start date of the renewed term, as a calendar date
            in the format YYYY-MM-DD.
        new_contract_end_date: Fixed-format class — the end date of the renewed term, as a calendar date
            in the format YYYY-MM-DD.

    Returns:
        A dictionary receipt: agreement_id (the agreement number renewed), status ("renewal_accepted"
        when the acceptance was recorded), plan (the plan now in force), term_months (integer months of
        the renewed term), rate_cents_kwh (the accepted rate, 2 decimals), term_start (YYYY-MM-DD start
        date of the renewed term), term_end (YYYY-MM-DD end date of the renewed term) and accepted_on
        (YYYY-MM-DD date the acceptance was recorded).
    """
    today = ctx.now()[:10]
    ctx.update("bizpower_agreements", bizpower_agreement_id, variant_name=renewed_plan_name,
               term_months=int(term_months), contract_rate_cents_kwh=round(float(renewal_rate_cents_kwh), 2),
               plan_change_date=new_term_start_date, contract_end_date=new_contract_end_date,
               renewal_election="accepted", renewal_election_date=today, auto_renewed=False)
    return str({"agreement_id": bizpower_agreement_id, "status": "renewal_accepted",
                "plan": renewed_plan_name, "term_months": int(term_months),
                "rate_cents_kwh": round(float(renewal_rate_cents_kwh), 2), "term_start": new_term_start_date,
                "term_end": new_contract_end_date, "accepted_on": today})


@tool(owner="agent", rw="write")
def transfer_agreement_site_58988442(ctx: ToolContext, bizpower_agreement_id: str, new_premise_id: str,
                                     site_transfer_date: str, transfer_fee_usd: float) -> str:
    """Moves a small business electricity agreement to another site of the same business when the
    business relocates, and bills the site transfer fee. The agreement keeps its agreement number,
    plan, rate and contract end date; its supplied site becomes the new site and the date the move
    takes effect is recorded on it. A site transfer fee line is added to the agreement's bill with the
    new site, the fee amount and today's posting date. The business sees its agreement listed at the
    new site and the transfer fee on its next statement.

    Args:
        bizpower_agreement_id: Id class — the agreement number of the small business electricity
            agreement being moved, as shown on the agreement record returned by the agreement lookup.
        new_premise_id: Id class — the reference number of the business's new site, as shown on that
            site's record returned by the site lookup.
        site_transfer_date: Fixed-format class — the date the move takes effect at the new site, as a
            calendar date in the format YYYY-MM-DD.
        transfer_fee_usd: Fixed-format class — the site transfer fee in USD as a positive number with 2
            decimal places, already rounded half up to the cent; 0.00 when no fee is billed.

    Returns:
        A dictionary receipt: agreement_id (the agreement moved), new_site_id (the site now supplied),
        effective_on (YYYY-MM-DD date the move takes effect), fee_line_id (the transfer fee line's
        reference), fee_usd (the fee billed, positive, 2 decimals) and posted_on (YYYY-MM-DD posting
        date of the fee). A receipt carrying a fee_line_id means the move and its fee are recorded.
    """
    today = ctx.now()[:10]
    fee = round(float(transfer_fee_usd), 2)
    ctx.update("bizpower_agreements", bizpower_agreement_id, premise_id=new_premise_id,
               site_transfer_date=site_transfer_date)
    rid = ctx.make_id("bpb_", bizpower_agreement_id, "site_transfer_fee", new_premise_id, site_transfer_date,
                      transfer_fee_usd)
    ctx.create("bizpower_billing", rid, bizpower_billing_id=rid, bizpower_agreement_id=bizpower_agreement_id,
               customer_id=(ctx.find("bizpower_agreements", bizpower_agreement_id=bizpower_agreement_id) or [{}])[0].get("customer_id", ""),
               premise_id=new_premise_id, event_type="bizpower_fee_charge", line_type="site_transfer_fee",
               billing_period_start="", billing_period_end="", usage_kwh=0, rate_cents_kwh=0.0, tax_rate_pct=0.0,
               taxable_amount_usd=0.0, amount_usd=fee, posted_date=today, source_billing_id="",
               etf_months_remaining=0, etf_remaining_kwh=0)
    return str({"agreement_id": bizpower_agreement_id, "new_site_id": new_premise_id, "effective_on": site_transfer_date,
                "fee_line_id": rid, "fee_usd": fee, "posted_on": today})

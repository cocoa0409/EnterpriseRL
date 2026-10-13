"""Hidden task tools of the commercial_gas_care difficulty (Beacon Ridge Energy, Commercial Natural
Gas Supply). Each tool performs one atomic write on the commercial gas records; it checks no policy,
computes no amount and judges no eligibility. Every name is registered only as an extended policy's
target_tool and is reached through the unlock -> call meta-tools.
"""

from erlbench import ToolContext, tool


@tool(owner="agent", rw="write")
def post_bizgas_swing_rebill_d99acf60(ctx: ToolContext, bizgas_agreement_id: str, source_billing_id: str,
                                      billing_period_start: str, rebill_amount_usd: float) -> str:
    """Post a rebill credit that returns money over-billed on one commercial gas swing excess bill
    line. One call adds one rebill_credit line to the commercial gas agreement's billing ledger, tied
    to the corrected swing excess line, dated today and carried as a negative amount, so the business
    sees the credit against that line on its next utility bill and the agreement's net billed charges
    fall by the credited amount. The credit is booked exactly as given.

    Args:
        bizgas_agreement_id: Id class — the commercial gas agreement number of the site whose swing
            excess line is corrected, as shown on the agreement record returned by the commercial gas
            agreement lookup.
        source_billing_id: Id class — the reference number of the swing excess bill line being
            corrected, as shown on that line in the commercial gas bill line lookup.
        billing_period_start: Fixed-format class — the first day of the billing cycle of the corrected
            line, written YYYY-MM-DD exactly as it appears on that line; no time zone.
        rebill_amount_usd: Fixed-format class — the amount being returned on the line, given as a
            positive number of US dollars rounded half up to 2 decimal places; it is booked on the
            ledger in the form USD, 2 decimal places, signed, as a negative credit.

    Returns:
        A text rendering of a dictionary with keys status (the literal "posted" when the credit was
        booked), bizgas_billing_id (the reference number of the new rebill credit line, text),
        source_billing_id (the corrected line's reference number, text), amount_usd (the signed
        credit booked, a negative number with 2 decimal places) and posted_date (today's date,
        YYYY-MM-DD).
    """
    rid = ctx.make_id("bgrb_", bizgas_agreement_id, source_billing_id, billing_period_start, rebill_amount_usd)
    amount = -round(float(rebill_amount_usd), 2)
    ctx.create("bizgas_billing", rid, bizgas_billing_id=rid, bizgas_agreement_id=bizgas_agreement_id,
               customer_id=(ctx.find("bizgas_agreements", bizgas_agreement_id=bizgas_agreement_id) or [{}])[0].get("customer_id", ""), event_type="bizgas_adjustment",
               line_type="rebill_credit", billing_period_start=billing_period_start, billing_period_end="",
               usage_therms=0, rate_usd_therm=0.0, tax_rate_pct=0.0, taxable_amount_usd=0.0,
               amount_usd=amount, posted_date=ctx.now()[:10], source_billing_id=source_billing_id,
               etf_remaining_therms=0)
    return str({"status": "posted", "bizgas_billing_id": rid, "source_billing_id": source_billing_id,
                "amount_usd": amount, "posted_date": ctx.now()[:10]})


@tool(owner="user", rw="write")
def accept_bizgas_renewal_offer_c0a82e44(ctx: ToolContext, bizgas_agreement_id: str, offered_variant_name: str,
                                         term_months: int, contract_rate_usd_therm: float,
                                         contract_annual_therms: int, new_term_start_date: str,
                                         new_contract_end_date: str, loyalty_credit_usd: float) -> str:
    """The business's authorized representative accepts, in person, the renewal offer on a commercial
    gas agreement whose current term has not yet ended. One call puts the renewed term on the
    agreement record (the plan, its term, the price per therm, the contracted annual volume, the
    first day and the last day of the new term) and books the renewal loyalty credit as one
    renewal_loyalty_credit line, carried as a negative amount on the bill of the new term's first
    cycle. Afterwards the agreement shows the renewed plan and end date, and the credit appears on
    the business's commercial gas bill lines.

    Args:
        bizgas_agreement_id: Id class — the commercial gas agreement number of the site being renewed,
            as read to the representative from the agreement record by the care agent.
        offered_variant_name: Enum class — the plan named in the renewal offer being accepted, exactly
            one of: Beacon Ridge Commercial Gas Monthly Index when the offer renews onto the
            month-to-month index plan; Beacon Ridge Commercial Gas Fixed Basis 12 when the offer is
            the twelve-month plan with the basis locked and NYMEX floating; Beacon Ridge Commercial
            Gas Fixed 12 when the offer is the twelve-month all-in fixed plan; Beacon Ridge Commercial
            Gas Fixed 24 when the offer is the twenty-four-month all-in fixed plan; Beacon Ridge
            Commercial Gas Fixed 36 when the offer is the thirty-six-month all-in fixed plan; Beacon
            Ridge Commercial Gas Carbon Neutral 24 when the offer is the twenty-four-month fixed plan
            with full carbon offsets.
        term_months: Fixed-format class — the length of the renewed term in integer months, as
            published for the offered plan; 0 only for a month-to-month plan.
        contract_rate_usd_therm: Fixed-format class — the renewal price per therm offered, in USD per
            therm, 4 decimal places, copied from the offer being accepted.
        contract_annual_therms: Fixed-format class — the contracted annual volume of the renewed term
            in integer therms.
        new_term_start_date: Fixed-format class — the first day of the renewed term, written
            YYYY-MM-DD; no time zone.
        new_contract_end_date: Fixed-format class — the last day of the renewed term, written
            YYYY-MM-DD; no time zone.
        loyalty_credit_usd: Fixed-format class — the renewal loyalty credit the care agent quoted,
            given as a positive number of US dollars rounded half up to 2 decimal places; it is
            booked on the ledger in the form USD, 2 decimal places, signed, as a negative credit.

    Returns:
        A text rendering of a dictionary with keys status (the literal "renewed" when the renewal was
        recorded), bizgas_agreement_id (the renewed agreement's number, text), variant_name (the plan
        now in force, text), contract_end_date (the renewed term's last day, YYYY-MM-DD),
        credit_billing_id (the reference number of the loyalty credit line, text) and
        credit_amount_usd (the signed credit booked, a negative number with 2 decimal places).
    """
    ctx.update("bizgas_agreements", bizgas_agreement_id, variant_name=offered_variant_name,
               term_months=int(term_months), contract_rate_usd_therm=round(float(contract_rate_usd_therm), 4),
               contract_annual_therms=int(contract_annual_therms), contract_end_date=new_contract_end_date,
               plan_change_date=new_term_start_date)
    cid = ctx.make_id("bglc_", bizgas_agreement_id, offered_variant_name, term_months, contract_rate_usd_therm,
                      contract_annual_therms, new_term_start_date, new_contract_end_date, loyalty_credit_usd)
    amount = -round(float(loyalty_credit_usd), 2)
    ctx.create("bizgas_billing", cid, bizgas_billing_id=cid, bizgas_agreement_id=bizgas_agreement_id,
               customer_id=(ctx.find("bizgas_agreements", bizgas_agreement_id=bizgas_agreement_id) or [{}])[0].get("customer_id", ""), event_type="bizgas_credit",
               line_type="renewal_loyalty_credit", billing_period_start=new_term_start_date,
               billing_period_end="", usage_therms=0, rate_usd_therm=0.0, tax_rate_pct=0.0,
               taxable_amount_usd=0.0, amount_usd=amount, posted_date=ctx.now()[:10], source_billing_id="",
               etf_remaining_therms=0)
    return str({"status": "renewed", "bizgas_agreement_id": bizgas_agreement_id, "variant_name": offered_variant_name,
                "contract_end_date": new_contract_end_date, "credit_billing_id": cid, "credit_amount_usd": amount})


@tool(owner="agent", rw="write")
def post_bizgas_shortfall_rebill_b4d87cc1(ctx: ToolContext, bizgas_agreement_id: str, source_billing_id: str,
                                          billing_period_start: str, rebill_amount_usd: float) -> str:
    """Post a rebill credit that returns money over-billed on one commercial gas swing shortfall bill
    line. One call adds one rebill_credit line to the commercial gas agreement's billing ledger, tied
    to the corrected swing shortfall line, dated today and carried as a negative amount, so the
    business sees the credit against that line on its next utility bill and the agreement's net
    billed charges fall by the credited amount. The credit is booked exactly as given.

    Args:
        bizgas_agreement_id: Id class — the commercial gas agreement number of the site whose swing
            shortfall line is corrected, as shown on the agreement record returned by the commercial
            gas agreement lookup.
        source_billing_id: Id class — the reference number of the swing shortfall bill line being
            corrected, as shown on that line in the commercial gas bill line lookup.
        billing_period_start: Fixed-format class — the first day of the billing cycle of the corrected
            line, written YYYY-MM-DD exactly as it appears on that line; no time zone.
        rebill_amount_usd: Fixed-format class — the amount being returned on the line, given as a
            positive number of US dollars rounded half up to 2 decimal places; it is booked on the
            ledger in the form USD, 2 decimal places, signed, as a negative credit.

    Returns:
        A text rendering of a dictionary with keys status (the literal "posted" when the credit was
        booked), bizgas_billing_id (the reference number of the new rebill credit line, text),
        source_billing_id (the corrected line's reference number, text), amount_usd (the signed
        credit booked, a negative number with 2 decimal places) and posted_date (today's date,
        YYYY-MM-DD).
    """
    rid = ctx.make_id("bgsf_", bizgas_agreement_id, source_billing_id, billing_period_start, rebill_amount_usd)
    amount = -round(float(rebill_amount_usd), 2)
    ctx.create("bizgas_billing", rid, bizgas_billing_id=rid, bizgas_agreement_id=bizgas_agreement_id,
               customer_id=(ctx.find("bizgas_agreements", bizgas_agreement_id=bizgas_agreement_id) or [{}])[0].get("customer_id", ""),
               event_type="bizgas_adjustment", line_type="rebill_credit", billing_period_start=billing_period_start,
               billing_period_end="", usage_therms=0, rate_usd_therm=0.0, tax_rate_pct=0.0, taxable_amount_usd=0.0,
               amount_usd=amount, posted_date=ctx.now()[:10], source_billing_id=source_billing_id,
               etf_remaining_therms=0)
    return str({"status": "posted", "bizgas_billing_id": rid, "source_billing_id": source_billing_id,
                "amount_usd": amount, "posted_date": ctx.now()[:10]})


@tool(owner="user", rw="write")
def accept_bizgas_lapsed_renewal_f259b0f9(ctx: ToolContext, bizgas_agreement_id: str, offered_variant_name: str,
                                          term_months: int, contract_rate_usd_therm: float,
                                          contract_annual_therms: int, new_contract_end_date: str) -> str:
    """The business's authorized representative accepts, in person, a renewal offer on a commercial gas
    agreement that has already rolled over to the month-to-month index plan. One call replaces the
    rolled-over terms on the agreement record with the renewed term: the plan, its term, the renewed
    price per therm, the contracted annual volume and the last day of the new term, and it records
    today's date as the first day of that term. No credit line is booked. Afterwards the agreement
    shows the renewed fixed plan, price and end date in place of the index plan.

    Args:
        bizgas_agreement_id: Id class — the commercial gas agreement number of the site being renewed,
            as read to the representative from the agreement record by the care agent.
        offered_variant_name: Enum class — the plan named in the renewal offer being accepted, exactly
            one of: Beacon Ridge Commercial Gas Monthly Index when the offer renews onto the
            month-to-month index plan; Beacon Ridge Commercial Gas Fixed Basis 12 when the offer is
            the twelve-month plan with the basis locked and NYMEX floating; Beacon Ridge Commercial
            Gas Fixed 12 when the offer is the twelve-month all-in fixed plan; Beacon Ridge Commercial
            Gas Fixed 24 when the offer is the twenty-four-month all-in fixed plan; Beacon Ridge
            Commercial Gas Fixed 36 when the offer is the thirty-six-month all-in fixed plan; Beacon
            Ridge Commercial Gas Carbon Neutral 24 when the offer is the twenty-four-month fixed plan
            with full carbon offsets.
        term_months: Fixed-format class — the length of the renewed term in integer months, as
            published for the offered plan; 0 only for a month-to-month plan.
        contract_rate_usd_therm: Fixed-format class — the renewed price per therm the care agent
            quoted, in USD per therm, 4 decimal places, rounded half up.
        contract_annual_therms: Fixed-format class — the contracted annual volume of the renewed term
            in integer therms.
        new_contract_end_date: Fixed-format class — the last day of the renewed term, written
            YYYY-MM-DD; no time zone.

    Returns:
        A text rendering of a dictionary with keys status (the literal "renewed" when the renewal was
        recorded), bizgas_agreement_id (the renewed agreement's number, text), variant_name (the plan
        now in force, text), contract_rate_usd_therm (the renewed price per therm, 4 decimal places),
        plan_change_date (today's date as the first day of the renewed term, YYYY-MM-DD) and
        contract_end_date (the renewed term's last day, YYYY-MM-DD).
    """
    start = ctx.now()[:10]
    rate = round(float(contract_rate_usd_therm), 4)
    ctx.update("bizgas_agreements", bizgas_agreement_id, variant_name=offered_variant_name, term_months=int(term_months),
               contract_rate_usd_therm=rate, contract_annual_therms=int(contract_annual_therms),
               contract_end_date=new_contract_end_date, plan_change_date=start)
    return str({"status": "renewed", "bizgas_agreement_id": bizgas_agreement_id, "variant_name": offered_variant_name,
                "contract_rate_usd_therm": rate, "plan_change_date": start, "contract_end_date": new_contract_end_date})

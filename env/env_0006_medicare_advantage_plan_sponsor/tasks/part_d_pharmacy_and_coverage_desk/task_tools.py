"""Hidden task tools for the part_d_pharmacy_and_coverage_desk difficulty.

Each tool performs one atomic write on a Ridgecrest stand-alone Part D record. None of them
aggregates history, judges eligibility or works out a policy figure: the agent reads the
member's records, applies the published rules and passes the finished value in.
"""

from erlbench import ToolContext, tool


@tool(owner="agent", rw="write")
def post_penalty_removal_e1c246c8(ctx: ToolContext, pdp_enrollment_id: str, customer_id: str,
                                  pdp_enrollment_request_id: str, source_premium_entry_id: str,
                                  billing_period: str, removal_amount: float) -> str:
    """Take an amount of late enrollment penalty back off a member's stand-alone drug plan premium
    account, recording it as a penalty removal against the one penalty charge it relieves and giving
    the reason as earlier creditable drug coverage proved. The entry stands on the premium account as
    a credit against the late enrollment penalty component of the coverage month named and appears on
    the member's next premium statement, so that what the account has charged in penalty less what it
    has taken back off is the penalty the member still owes; the running penalty figure carried on
    the enrollment record itself is not rewritten by this action. The call has completed when the
    confirmation carrying the new entry's reference number comes back.

    Args:
        pdp_enrollment_id: Id class — the reference number of the stand-alone Part D drug plan
            enrollment whose penalty is being relieved, read from the member's enrollment record.
        customer_id: Id class — the member reference number of the person whose penalty is being
            relieved, read from their member profile.
        pdp_enrollment_request_id: Id class — the reference number of the enrollment intake record
            that holds the plan's evidence of the member's earlier creditable drug coverage, read
            from the member's enrollment intake records; the removal entry is keyed to it.
        source_premium_entry_id: Id class — the reference number of the single late enrollment
            penalty charge this removal is set against, read from the member's premium account
            entries.
        billing_period: Fixed-format class — the coverage month whose penalty is relieved, written
            as YYYY-MM, in the plan's own billing calendar; never left empty.
        removal_amount: Fixed-format class — the amount of late enrollment penalty taken back off,
            in USD as a positive figure rounded to 2 decimal places, with half-up rounding applied
            at the point of posting; never left empty and never negative.

    Returns:
        A confirmation sentence in plain text. It carries the new penalty removal entry's reference
        number, the drug plan enrollment reference number it was posted on, the coverage month it
        relieves, the amount in USD taken back off, and the reference number of the penalty charge
        it was set against. A sentence of this shape means the entry is on the account; any other
        text means nothing was posted.
    """
    rid = ctx.make_id("pdprem_", pdp_enrollment_id, customer_id, pdp_enrollment_request_id,
                      source_premium_entry_id, billing_period, removal_amount)
    ctx.create("pdp_premium_ledger", rid,
               pdp_premium_entry_id=rid,
               pdp_enrollment_id=pdp_enrollment_id,
               customer_id=customer_id,
               event_type="pdp_penalty_removal",
               billing_period=billing_period,
               posted_date=ctx.now()[:10],
               amount=round(float(removal_amount), 2),
               charge_component="late_enrollment_penalty",
               payment_channel="not_applicable",
               source_premium_entry_id=source_premium_entry_id,
               adjustment_reason_code="creditable_coverage_proved")
    return (f"Penalty removal {rid} posted on drug plan enrollment {pdp_enrollment_id} for coverage "
            f"month {billing_period}: {round(float(removal_amount), 2)} USD of late enrollment "
            f"penalty taken back off, set against penalty charge {source_premium_entry_id}.")


@tool(owner="user", rw="write")
def authorize_arrears_payment_7dfec3b3(ctx: ToolContext, pdp_enrollment_id: str, customer_id: str,
                                       billing_period: str, payment_amount: float) -> str:
    """Let the member themselves authorise a telephone payment from their own funds against their
    stand-alone drug plan premium account, for the figure they have been quoted. The money is taken
    on the spot and posted to the account as a premium payment applied to the coverage month named,
    the member's premium receivable falls by the amount paid, the member hears the plan's own
    payment reference for their records, and the call has completed when the confirmation carrying
    that reference comes back.

    Args:
        pdp_enrollment_id: Id class — the reference number of the stand-alone Part D drug plan
            enrollment the money is paid onto, read from the member's enrollment record.
        customer_id: Id class — the member reference number of the person authorising the payment,
            read from their member profile.
        billing_period: Fixed-format class — the coverage month the money is applied to, written as
            YYYY-MM, in the plan's own billing calendar; never left empty.
        payment_amount: Fixed-format class — the sum the member authorises, in USD as a positive
            figure rounded to 2 decimal places, with half-up rounding applied at the point of
            posting; never left empty and never negative.

    Returns:
        A confirmation sentence in plain text. It carries the new premium payment entry's reference
        number, which doubles as the plan's payment reference for the member's own records, the drug
        plan enrollment reference number the money was posted on, the coverage month it was applied
        to, and the amount in USD taken. A sentence of this shape means the money has been taken and
        posted; any other text means no money was taken.
    """
    rid = ctx.make_id("pdppay_", pdp_enrollment_id, customer_id, billing_period, payment_amount)
    ctx.create("pdp_premium_ledger", rid,
               pdp_premium_entry_id=rid,
               pdp_enrollment_id=pdp_enrollment_id,
               customer_id=customer_id,
               event_type="pdp_premium_payment",
               billing_period=billing_period,
               posted_date=ctx.now()[:10],
               amount=round(float(payment_amount), 2),
               charge_component="not_applicable",
               payment_channel="telephone_payment",
               remittance_reference=rid)
    return (f"Premium payment {rid} taken and posted on drug plan enrollment {pdp_enrollment_id} "
            f"for coverage month {billing_period}: {round(float(payment_amount), 2)} USD received "
            f"by telephone; the plan's payment reference is {rid}.")


@tool(owner="agent", rw="write")
def restate_out_of_pocket_total_a40a5cef(ctx: ToolContext, pdp_enrollment_id: str,
                                         restated_out_of_pocket_total: float) -> str:
    """Bring the true out-of-pocket total held on a member's stand-alone drug plan enrollment into
    line with the contract year's pharmacy record, replacing the figure the enrollment carries with
    the one supplied. The enrollment then shows the new total, which is what every later question
    about the member's deductible and payment stage is measured against, and the member sees it on
    their next explanation of benefits. The call has completed when the confirmation carrying the
    enrollment reference and the new total comes back.

    Args:
        pdp_enrollment_id: Id class — the reference number of the stand-alone Part D drug plan
            enrollment whose out-of-pocket total is being restated, read from the member's
            enrollment record.
        restated_out_of_pocket_total: Fixed-format class — the true out-of-pocket total for the
            contract year that the enrollment is to carry, in USD as a figure of nothing or more
            rounded to 2 decimal places, with half-up rounding applied at the point of writing;
            never left empty.

    Returns:
        A confirmation sentence in plain text carrying the drug plan enrollment reference number and
        the out-of-pocket total the enrollment now holds, in USD. A sentence of this shape means the
        enrollment carries the new total; any other text means the enrollment was left as it was.
    """
    total = round(float(restated_out_of_pocket_total), 2)
    ctx.update("pdp_enrollments", pdp_enrollment_id, troop_accumulated=f"{total:.2f}")
    return (f"Drug plan enrollment {pdp_enrollment_id} now carries a true out-of-pocket total of "
            f"{total} USD for the contract year.")


@tool(owner="agent", rw="write")
def issue_exception_decision_dd13544d(ctx: ToolContext, pdp_enrollment_id: str, customer_id: str,
                                      pdp_determination_id: str, national_drug_code: str,
                                      approval_term_days: int) -> str:
    """Approve an open drug coverage request on a member's stand-alone drug plan and record the
    approval, fixing the run of days for which it holds good and the last day it stays good for. The
    member's coverage determination record gains an approval for the named product, the pharmacy may
    then dispense it, and the member is sent the approval notice. The call has completed when the
    confirmation carrying the new decision record's reference number and the last good day comes
    back.

    Args:
        pdp_enrollment_id: Id class — the reference number of the stand-alone Part D drug plan
            enrollment the request was made under, read from the member's enrollment record.
        customer_id: Id class — the member reference number of the person the request concerns, read
            from their member profile.
        pdp_determination_id: Id class — the reference number of the open drug coverage request this
            approval disposes of, read from the member's coverage determination records.
        national_drug_code: Fixed-format class — the product the approval covers, written in the
            schema's own form of an eleven-digit National Drug Code, no dashes, and no spaces
            either, copied from the request being approved; never left empty.
        approval_term_days: Fixed-format class — the run for which the approval holds good, as a
            whole number of calendar days counted from the day this approval is given, expressed as
            an integer with no decimal part and no unit suffix; never left empty and never zero or
            negative.

    Returns:
        A confirmation sentence in plain text carrying the new decision record's reference number,
        the drug plan enrollment reference number, the National Drug Code approved, the run in days
        the approval holds good for, and the last day it stays good for as YYYY-MM-DD. A sentence of
        this shape means the approval is on the member's record; any other text means no approval was
        recorded.
    """
    term = int(approval_term_days)
    # The last good day is the handling date advanced by the approved run, worked out from the
    # frozen clock with civil-calendar integer arithmetic so that no clock or calendar library is
    # consulted: the date is turned into a day count, the run is added, and the count is turned
    # back into a date.
    year, month, day = (int(part) for part in ctx.now()[:10].split("-"))
    shifted_year = year - (1 if month <= 2 else 0)
    era = (shifted_year if shifted_year >= 0 else shifted_year - 399) // 400
    year_of_era = shifted_year - era * 400
    day_of_year = (153 * (month - 3 if month > 2 else month + 9) + 2) // 5 + day - 1
    day_of_era = year_of_era * 365 + year_of_era // 4 - year_of_era // 100 + day_of_year
    day_count = era * 146097 + day_of_era + term
    through_era = (day_count if day_count >= 0 else day_count - 146096) // 146097
    through_day_of_era = day_count - through_era * 146097
    through_year_of_era = (through_day_of_era - through_day_of_era // 1460
                           + through_day_of_era // 36524 - through_day_of_era // 146096) // 365
    through_day_of_year = through_day_of_era - (365 * through_year_of_era
                                                + through_year_of_era // 4
                                                - through_year_of_era // 100)
    month_index = (5 * through_day_of_year + 2) // 153
    through_day = through_day_of_year - (153 * month_index + 2) // 5 + 1
    through_month = month_index + (3 if month_index < 10 else -9)
    through_year = through_year_of_era + through_era * 400 + (1 if through_month <= 2 else 0)
    through = f"{through_year:04d}-{through_month:02d}-{through_day:02d}"
    rid = ctx.make_id("pdpdec_", pdp_enrollment_id, customer_id, pdp_determination_id,
                      national_drug_code, term)
    ctx.create("pdp_coverage_determinations", rid,
               pdp_determination_id=rid,
               pdp_enrollment_id=pdp_enrollment_id,
               customer_id=customer_id,
               event_type="pdp_coverage_determination_decision",
               national_drug_code=national_drug_code,
               decision_date=ctx.now()[:10],
               decision_time=ctx.now()[11:16],
               decision_outcome="approved",
               decision_rationale_code="criteria_met",
               approved_through_date=through,
               source_determination_id=pdp_determination_id)
    return (f"Coverage determination decision {rid} recorded on drug plan enrollment "
            f"{pdp_enrollment_id}: product {national_drug_code} approved for {term} days, good "
            f"through {through}.")


@tool(owner="user", rw="write")
def settle_counter_fill_eaef344a(ctx: ToolContext, pdp_enrollment_id: str, customer_id: str,
                                 pdp_pharmacy_claim_id: str, pdp_determination_id: str,
                                 negotiated_price: float, member_paid_amount: float) -> str:
    """Let the member themselves pay for the prescription the pharmacy is holding, at the sum they
    have been quoted, so that the fill is priced and handed over. A priced fill is recorded against
    the drug plan enrollment showing what the member handed over and what the plan meets, carrying
    the reference of the held fill it settles and the reference of the coverage determination on the
    member's record that covers the product; the member walks away with the medicine and a till
    receipt. The call has completed when the confirmation carrying the new
    priced fill's reference number comes back.

    Args:
        pdp_enrollment_id: Id class — the reference number of the stand-alone Part D drug plan
            enrollment the fill is priced under, read from the member's enrollment record.
        customer_id: Id class — the member reference number of the person paying for the
            prescription, read from their member profile.
        pdp_pharmacy_claim_id: Id class — the reference number of the fill the pharmacy is holding
            and which this payment settles, read from the member's pharmacy claim records.
        pdp_determination_id: Id class — the reference number of the approved coverage determination
            on the member's coverage determination record that covers this product, read from the
            member's coverage determination records.
        negotiated_price: Fixed-format class — the price the plan has negotiated for this fill, in
            USD rounded to 2 decimal places with half-up rounding applied at the point of writing,
            copied from the held fill; never left empty.
        member_paid_amount: Fixed-format class — the sum the member hands over at the counter, in
            USD as a figure of nothing or more rounded to 2 decimal places, with half-up rounding
            applied at the point of writing; never left empty and never negative.

    Returns:
        A confirmation sentence in plain text carrying the new priced fill's reference number, the
        drug plan enrollment reference number, the amount in USD the member handed over, the amount
        in USD the plan meets, and the reference number of the held fill it settles. A sentence of
        this shape means the fill is priced and released; any other text means nothing was priced
        and no money was taken.
    """
    paid = round(float(member_paid_amount), 2)
    price = round(float(negotiated_price), 2)
    plan_meets = round(price - paid, 2)
    rid = ctx.make_id("pdpfill_", pdp_enrollment_id, customer_id, pdp_pharmacy_claim_id,
                      pdp_determination_id, negotiated_price, member_paid_amount)
    ctx.create("pdp_pharmacy_claims", rid,
               pdp_pharmacy_claim_id=rid,
               pdp_enrollment_id=pdp_enrollment_id,
               customer_id=customer_id,
               event_type="pdp_pharmacy_claim_adjudication",
               fill_date=ctx.now()[:10],
               negotiated_price=price,
               member_paid_amount=paid,
               plan_paid_amount=plan_meets,
               claim_status="paid",
               rejection_reason_code="not_applicable",
               determination_reference=pdp_determination_id,
               source_pharmacy_claim_id=pdp_pharmacy_claim_id,
               transition_fill_flag="not_a_transition_fill")
    return (f"Priced fill {rid} recorded on drug plan enrollment {pdp_enrollment_id}: member paid "
            f"{paid} USD, plan meets {plan_meets} USD, settling held fill {pdp_pharmacy_claim_id}.")

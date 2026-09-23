"""Hidden task tools for the optional rider benefit desk.

Each tool performs one atomic act on one optional supplemental benefit rider record, its
premium account or its benefit claim history. None of them aggregates history, works out a
benefit, an arrears figure or a credit for the caller, and none of them refuses on a business
ground: the figures are worked out by the representative from the plan's published rules and
the member's records, and are passed in already decided.
"""

from erlbench import ToolContext, tool


@tool(owner="agent", rw="write")
def settle_rider_benefit_line_e49937be(ctx: ToolContext, osb_rider_id: str,
                                       osb_benefit_claim_id: str, osb_rider_request_id: str,
                                       rider_paid_amount: float) -> str:
    """Settle a dental, vision or hearing claim line that a provider has submitted under a
    member's optional supplemental benefit rider and that is still awaiting a decision. The
    line is marked paid, the benefit stated is recorded against it as what the rider paid, the
    remainder of the line's allowed amount is recorded as what the member owes the provider, no
    denial reason is carried, and the settlement is dated with today's date. The same benefit is
    added to the benefit the rider has paid toward this benefit year's maximum, so the member's
    remaining maximum falls by that much. The settled line shows the member and the provider
    what the rider paid and what is left for the member to pay.

    Args:
        osb_rider_id: Id class — the reference number of the member's optional supplemental
            benefit rider the line is claimed under, as it stands in the member's rider
            records.
        osb_benefit_claim_id: Id class — the reference number of the single submitted claim line
            to be settled, as it stands in the member's rider benefit claim history.
        osb_rider_request_id: Id class — the reference number of the rider service request
            carrying the treatment plan the plan answered for this service, read from the
            member's rider service requests; pass an empty string where the
            service needed no treatment plan.
        rider_paid_amount: Fixed-format class — the benefit the rider pays on this line, in USD
            to 2 decimal places, as a plain positive number with no currency sign; it is stored
            rounded to 2 decimal places and an amount of zero is written as 0.00.

    Returns:
        A confirmation sentence naming the settled claim line's reference number, the benefit
        recorded as paid by the rider in USD, the amount left as the member's own, and the
        benefit the rider has now paid toward this benefit year's maximum. The sentence being
        returned at all is what indicates the line has been settled.
    """
    claim = ctx.find("osb_benefit_claims", osb_benefit_claim_id=osb_benefit_claim_id)[0]
    allowed = round(float(claim.get("allowed_amount") or 0), 2)
    paid = round(float(rider_paid_amount), 2)
    member = round(allowed - paid, 2)
    ctx.update("osb_benefit_claims", osb_benefit_claim_id,
               claim_status="paid", rider_paid_amount=paid, member_share=member,
               denial_reason_code="not_applicable", processed_date=ctx.now()[:10],
               predetermination_reference=osb_rider_request_id)
    rider = ctx.find("osb_riders", osb_rider_id=osb_rider_id)[0]
    used = round(float(rider.get("annual_maximum_used") or 0) + paid, 2)
    ctx.update("osb_riders", osb_rider_id, annual_maximum_used=used)
    return (f"Claim line {osb_benefit_claim_id} settled: rider paid {paid:.2f} USD, "
            f"member owes {member:.2f} USD, benefit used this benefit year now {used:.2f} USD.")


@tool(owner="agent", rw="write")
def reverse_rider_benefit_line_9daedfb7(ctx: ToolContext, source_claim_id: str,
                                        restated_member_share: float) -> str:
    """Back out a dental, vision or hearing claim line that the rider has settled, by
    posting a reversal of its own against that one line rather than altering it. The reversal
    carries over the line's date of service, benefit category, procedure, tooth, eye or ear
    reference, allowed amount and position in the submitted claim, carries the negative of the
    benefit that line paid, stands as reversed, names the line it applies to, and is dated with
    today's date. What the member is left owing on the line as it now stands is recorded on the
    reversal. The benefit backed out is taken off the benefit the rider has paid toward this
    benefit year's maximum, so the member's remaining maximum rises by that much.

    Args:
        source_claim_id: Id class — the reference number of the single settled claim
            line being backed out, as it stands in the member's rider benefit claim history.
        restated_member_share: Fixed-format class — what the member is left owing on that line
            as it now stands, in USD to 2 decimal places, as a plain positive number
            with no currency sign; it is stored rounded to 2 decimal places and an amount of zero
            is written as 0.00.

    Returns:
        A confirmation sentence naming the reversal's own newly created reference number, the
        claim line it was posted against, the benefit backed out in USD as a negative number,
        what the member is left owing, and the benefit the rider has now paid toward this
        benefit year's maximum. The sentence being returned at all is what indicates the
        reversal has been posted.
    """
    src = ctx.find("osb_benefit_claims", osb_benefit_claim_id=source_claim_id)[0]
    backed_out = round(-float(src.get("rider_paid_amount") or 0), 2)
    member = round(float(restated_member_share), 2)
    rid = ctx.make_id("obcr_", source_claim_id, restated_member_share)
    ctx.create("osb_benefit_claims", rid, osb_benefit_claim_id=rid,
               osb_rider_id=src.get("osb_rider_id"), customer_id=src.get("customer_id"),
               event_type="osb_benefit_claim_reversal", date_of_service=src.get("date_of_service"),
               processed_date=ctx.now()[:10], service_category=src.get("service_category"),
               procedure_code=src.get("procedure_code"),
               tooth_or_eye_reference=src.get("tooth_or_eye_reference"),
               allowed_amount=src.get("allowed_amount"), rider_paid_amount=backed_out,
               member_share=member, claim_status="reversed", source_claim_id=source_claim_id,
               line_sequence=src.get("line_sequence"))
    rider_id = src.get("osb_rider_id")
    rider = ctx.find("osb_riders", osb_rider_id=rider_id)[0]
    used = round(float(rider.get("annual_maximum_used") or 0) + backed_out, 2)
    ctx.update("osb_riders", rider_id, annual_maximum_used=used)
    return (f"Reversal {rid} posted against claim line {source_claim_id}: {backed_out:.2f} USD "
            f"of benefit backed out, member left owing {member:.2f} USD, benefit used this "
            f"benefit year now {used:.2f} USD.")


@tool(owner="user", rw="write")
def pay_rider_premium_by_telephone_9597e982(ctx: ToolContext, osb_rider_id: str,
                                            osb_rider_premium_entry_id: str,
                                            settlement_amount: float, balance_effect: str,
                                            remittance_reference: str) -> str:
    """Let the member pay money of their own toward their optional supplemental benefit rider
    premium on the call, and post it to that rider's premium account
    against the coverage month named. The money is recorded as received by telephone payment,
    and the rider premium the member still owes is restated: it falls by the money paid where
    the posting is stated to leave part of it standing, and falls to nothing where the posting
    is stated to clear it, in which case the rider stands in force again and pays for services
    from today. The plan gives the member a payment reference for the posting.

    Args:
        osb_rider_id: Id class — the reference number of the member's optional supplemental
            benefit rider whose premium account the money is being paid into, read from the
            member's rider records.
        osb_rider_premium_entry_id: Id class — the reference number of the rider premium charge
            entry the money is applied against, read from the member's rider premium account
            entries; the coverage month of that charge is the coverage month the
            money is booked to.
        settlement_amount: Fixed-format class — the money the member is paying, in USD to 2
            decimal places, as a plain positive number with no currency sign; it is stored
            rounded to 2 decimal places.
        balance_effect: Enum class — what this posting does to the rider premium the member
            owes, exactly one of: not_applicable, carried by entries that move nothing against
            that balance and never right on money actually received; partial_payment, where
            rider premium is still owing with this money posted; settles_balance, where
            this money clears the rider premium owed and nothing is left owing; overpayment,
            where this money comes to more than the rider premium owed and the excess stands to
            the member's credit.
        remittance_reference: Verbatim class — the payment reference printed on the rider premium
            bill the member is paying against, as the member reads it out, copied character for
            character with its original wording, digits and punctuation and with nothing
            translated, normalised, summarised, added or dropped (verbatim).

    Returns:
        A confirmation sentence naming the payment reference the plan has given the posting, the
        money received in USD, the coverage month it was applied to, the rider premium the
        member is left owing in USD, and what the posting did to that balance. The sentence being
        returned at all is what indicates the money has been taken and posted.
    """
    rider = ctx.find("osb_riders", osb_rider_id=osb_rider_id)[0]
    charge = ctx.find("osb_rider_premium_ledger",
                      osb_rider_premium_entry_id=osb_rider_premium_entry_id)[0]
    before = round(float(rider.get("rider_premium_balance_due") or 0), 2)
    paid = round(float(settlement_amount), 2)
    cleared = balance_effect == "settles_balance" or balance_effect == "overpayment"
    after = 0.0 if cleared else round(before - paid, 2)
    rid = ctx.make_id("orpl_", osb_rider_id, osb_rider_premium_entry_id, settlement_amount,
                      balance_effect, remittance_reference)
    ctx.create("osb_rider_premium_ledger", rid, osb_rider_premium_entry_id=rid,
               osb_rider_id=osb_rider_id, customer_id=rider.get("customer_id"),
               event_type="osb_rider_premium_payment",
               billing_period=charge.get("billing_period"),
               posted_date=ctx.now()[:10], amount=paid, payment_channel="telephone_payment",
               balance_effect=balance_effect, credit_reason_code="not_applicable",
               remittance_reference=remittance_reference)
    if cleared:
        ctx.update("osb_riders", osb_rider_id, rider_premium_balance_due=after, status="active")
    else:
        ctx.update("osb_riders", osb_rider_id, rider_premium_balance_due=after)
    return (f"Payment {rid} of {paid:.2f} USD posted to rider {osb_rider_id} against coverage "
            f"month {charge.get('billing_period')}; rider premium still owed {after:.2f} USD "
            f"({balance_effect}).")


@tool(owner="agent", rw="write")
def post_rider_premium_credit_050a58f6(ctx: ToolContext, osb_rider_id: str,
                                       source_premium_entry_id: str, credit_reason_code: str,
                                       credit_amount: float) -> str:
    """Post a credit to an optional supplemental benefit rider premium account against one named
    rider premium charge standing on it, relieving the member of part or all of that
    charge for the reason given. The credit is booked to the same coverage month as the charge
    it relieves, names that charge, is dated with today's date, and the rider premium the member
    still owes falls by the amount credited. The credit is recorded as having left part of that
    charge outstanding, relieved it exactly, or exceeded it, according to what the charge came
    to. The member's rider premium account shows the credit beside the charge it relieves and a
    lower balance owed.

    Args:
        osb_rider_id: Id class — the reference number of the member's optional supplemental
            benefit rider whose premium account the credit is posted to, read from the member's
            rider records.
        source_premium_entry_id: Id class — the reference number of the single rider premium
            charge the credit is posted against, read from the member's rider premium account
            entries.
        credit_reason_code: Enum class — why the plan is granting the credit, exactly one of:
            not_applicable, which is carried by entries that are not credits at all and is never
            right here; rider_cancelled_mid_month, where the rider ended part way through a
            coverage month that carries a charge; waiting_period_billing_error, where the charge was
            raised for a coverage month in which the rider was not yet in force at all;
            duplicate_payment_refund, where the member's own money reached the plan twice for the
            same coverage month and the duplicate is being returned; rate_correction, where the
            charge was raised at a rider premium rate other than the one the member's rider
            carries; medical_plan_ended, where the charge was raised for a coverage month
            falling beyond the day the medical plan the rider hangs on ended.
        credit_amount: Fixed-format class — the money being credited against that charge, in USD
            to 2 decimal places, as a plain positive number with no currency sign; it is stored
            rounded to 2 decimal places.

    Returns:
        A confirmation sentence naming the credit's own newly created reference number, the rider
        premium charge it was posted against, the coverage month it is booked to, the money
        credited in USD, the rider premium the member is left owing in USD, and whether the credit
        left part of that charge outstanding, relieved it exactly or exceeded it. The sentence
        being returned at all is what indicates the credit has been posted.
    """
    charge = ctx.find("osb_rider_premium_ledger",
                      osb_rider_premium_entry_id=source_premium_entry_id)[0]
    rider = ctx.find("osb_riders", osb_rider_id=osb_rider_id)[0]
    amount = round(float(credit_amount), 2)
    charged = round(float(charge.get("amount") or 0), 2)
    left = round(charged - amount, 2)
    effect = "settles_balance" if left == 0 else ("partial_payment" if left > 0 else "overpayment")
    after = round(float(rider.get("rider_premium_balance_due") or 0) - amount, 2)
    rid = ctx.make_id("orpl_", osb_rider_id, source_premium_entry_id, credit_reason_code,
                      credit_amount)
    ctx.create("osb_rider_premium_ledger", rid, osb_rider_premium_entry_id=rid,
               osb_rider_id=osb_rider_id, customer_id=charge.get("customer_id"),
               event_type="osb_rider_premium_credit",
               billing_period=charge.get("billing_period"), posted_date=ctx.now()[:10],
               amount=amount, payment_channel="not_applicable", balance_effect=effect,
               source_premium_entry_id=source_premium_entry_id,
               credit_reason_code=credit_reason_code, remittance_reference="")
    ctx.update("osb_riders", osb_rider_id, rider_premium_balance_due=after)
    return (f"Credit {rid} of {amount:.2f} USD posted against rider premium charge "
            f"{source_premium_entry_id} for coverage month {charge.get('billing_period')} "
            f"({credit_reason_code}); rider premium still owed {after:.2f} USD ({effect}).")


@tool(owner="agent", rw="write")
def post_rider_premium_charge_4237e97e(ctx: ToolContext, osb_rider_id: str, billing_period: str,
                                       charge_amount: float) -> str:
    """Raise the rider premium a member owes on their optional supplemental benefit rider for
    coverage the plan has not yet billed them for, and post it to that rider's premium account
    booked to the coverage month named. The charge is dated with today's date, carries no
    payment channel, no balance effect and no credit reason, and the rider premium the member
    still owes rises by the amount charged. The member's rider premium account shows the new
    charge and a higher balance owed, and the charge is carried on the bill for that coverage
    month.

    Args:
        osb_rider_id: Id class — the reference number of the member's optional supplemental
            benefit rider whose premium account the charge is raised on, read from the member's
            rider records.
        billing_period: Fixed-format class — the coverage month the charge is booked to, written
            as the billing month in YYYY-MM form, four digits for the year and two for the
            month; where a charge covers several coverage months it is booked to the earliest of
            them.
        charge_amount: Fixed-format class — the rider premium being charged, in USD to 2 decimal
            places, as a plain positive number with no currency sign; it is stored rounded to 2
            decimal places.

    Returns:
        A confirmation sentence naming the charge's own newly created reference number, the rider
        it was raised on, the coverage month it is booked to, the rider premium charged in USD,
        and the rider premium the member is left owing in USD. The sentence being returned at all
        is what indicates the charge has been raised.
    """
    rider = ctx.find("osb_riders", osb_rider_id=osb_rider_id)[0]
    amount = round(float(charge_amount), 2)
    after = round(float(rider.get("rider_premium_balance_due") or 0) + amount, 2)
    rid = ctx.make_id("orpl_", osb_rider_id, billing_period, charge_amount)
    ctx.create("osb_rider_premium_ledger", rid, osb_rider_premium_entry_id=rid,
               osb_rider_id=osb_rider_id, customer_id=rider.get("customer_id"),
               event_type="osb_rider_premium_charge", billing_period=billing_period,
               posted_date=ctx.now()[:10], amount=amount, payment_channel="not_applicable",
               balance_effect="not_applicable", credit_reason_code="not_applicable",
               remittance_reference="")
    ctx.update("osb_riders", osb_rider_id, rider_premium_balance_due=after)
    return (f"Rider premium charge {rid} of {amount:.2f} USD raised on rider {osb_rider_id} for "
            f"coverage month {billing_period}; rider premium still owed {after:.2f} USD.")


@tool(owner="agent", rw="write")
def suspend_rider_for_unpaid_premium_a0d6b513(ctx: ToolContext, osb_rider_id: str,
                                              osb_rider_premium_entry_id: str,
                                              arrears_at_suspension: float) -> str:
    """Record on an optional supplemental benefit rider that its premium has gone unpaid beyond
    the days of grace the rider allows, so that the rider stops paying for dental, vision and
    hearing services for as long as the money stands owing. The rider is put into premium
    suspension and the rider premium the member owes is restated to the arrears figure given.
    The member's medical plan and any other rider are untouched. The member's rider record
    shows the rider suspended for unpaid premium and the arrears standing against it.

    Args:
        osb_rider_id: Id class — the reference number of the member's optional supplemental
            benefit rider being put into premium suspension, as it stands in the member's rider
            records.
        osb_rider_premium_entry_id: Id class — the reference number of the earliest rider premium
            charge that went unpaid on that rider, read from the member's rider premium account
            entries.
        arrears_at_suspension: Fixed-format class — the rider premium standing owed on the rider
            as the suspension is recorded, in USD to 2 decimal places, as a plain positive number
            with no currency sign; it is stored rounded to 2 decimal places and an amount of zero
            is written as 0.00.

    Returns:
        A confirmation sentence naming the rider put into premium suspension, the rider premium
        now recorded as owed on it in USD, and the unpaid rider premium charge that figure was
        struck against. The sentence being returned at all is what indicates the suspension has
        been recorded.
    """
    arrears = round(float(arrears_at_suspension), 2)
    ctx.update("osb_riders", osb_rider_id, status="premium_suspended",
               rider_premium_balance_due=arrears)
    return (f"Rider {osb_rider_id} recorded as suspended for unpaid rider premium with "
            f"{arrears:.2f} USD standing owed, struck against unpaid rider premium charge "
            f"{osb_rider_premium_entry_id}.")


@tool(owner="user", rw="write")
def end_rider_at_member_request_09efad65(ctx: ToolContext, osb_rider_id: str,
                                         osb_rider_request_id: str, rider_end_date: str,
                                         closing_premium_balance: float) -> str:
    """Let the member themselves end the optional supplemental benefit rider they are paying for,
    on the call itself. The rider is closed as ended at the member's own request, the
    last day it pays for services is recorded as the date given, and the rider premium the member
    still owes is restated to the closing figure given. The member's medical plan, their
    allowance card and any other rider are untouched. The rider service request on which the
    member asked for the cancellation is closed as completed and dated with today's date, so
    the request no longer stands open. The member's rider record shows the rider ended at their
    request, the last day it covers them, and what is left to settle.

    Args:
        osb_rider_id: Id class — the reference number of the member's own optional supplemental
            benefit rider that they are ending, as it stands in the member's rider records.
        osb_rider_request_id: Id class — the reference number of the rider service request on
            which the member's own cancellation was recorded, read from the member's rider
            service requests.
        rider_end_date: Fixed-format class — the last day the rider pays for services, written as
            a calendar date in YYYY-MM-DD form.
        closing_premium_balance: Fixed-format class — the rider premium left owed on the rider
            as it closes, in USD to 2 decimal places, as a plain positive number with no
            currency sign; it is stored rounded to 2 decimal places and an amount of zero is
            written as 0.00.

    Returns:
        A confirmation sentence naming the rider that has been ended, the last day it pays for
        services, the rider service request that has been closed as completed, and the rider
        premium left owed in USD. The sentence being returned at all is what indicates the rider
        has been ended.
    """
    closing = round(float(closing_premium_balance), 2)
    ctx.update("osb_riders", osb_rider_id, status="terminated", rider_end_date=rider_end_date,
               termination_reason="member_request", rider_premium_balance_due=closing)
    ctx.update("osb_rider_requests", osb_rider_request_id, intake_status="completed",
               decision_date=ctx.now()[:10])
    return (f"Rider {osb_rider_id} ended at the member's own request with effect from "
            f"{rider_end_date}; rider service request {osb_rider_request_id} closed as completed; "
            f"{closing:.2f} USD of rider premium left owed.")

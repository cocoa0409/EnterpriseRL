"""Hidden task tools for the medicare_advantage_member_services difficulty.

Each function performs one atomic write on a Ridgecrest Medicare Advantage record. The
names are never listed to the agent: they are reached through the unlock/call meta tools
after the agent has read the plan's published rules.
"""

import calendar

from erlbench import ToolContext, tool


@tool(owner="agent", rw="write")
def post_premium_relief_credit_3acf64b3(ctx: ToolContext, advantage_enrollment_id: str,
                                        source_premium_entry_id: str, credit_amount: float,
                                        adjustment_reason_code: str) -> str:
    """Give money back on a member's Medicare Advantage plan premium account by posting one
    credit entry against a single plan premium charge already standing on that account. The
    representative posts it on the member's behalf. The credit is booked on the premium account
    for the coverage month of the charge it relieves and carries the reason it was granted; the
    charge itself is left standing at its full amount, and what the member owes becomes the
    charge less the credits posted against it. The entry records, from the size of the credit
    against the size of the charge, whether part of that charge is left outstanding, whether it
    is settled exactly, or whether the credit goes beyond it. On success the new credit is
    visible on the member's premium account and the member can be told the reference number of
    the entry and the amount given back.

    Args:
        advantage_enrollment_id: Id class — the reference number of the Medicare Advantage
            enrollment whose premium account is credited, read from the member's enrollment
            record before the call.
        source_premium_entry_id: Id class — the reference number of the single plan premium
            charge entry this credit relieves, read from the premium account of that enrollment
            before the call.
        credit_amount: Fixed-format class — the money given back on the premium account, in USD
            as a decimal number carried to 2 decimal places, rounded half away from zero to the
            nearest cent at the moment it is passed; it is never negative and an empty value is
            not accepted.
        adjustment_reason_code: Enum class — why the credit is being granted, exactly one of
            these literals.
            not_applicable - the entry is not a credit at all, so no reason is carried;
            retroactive_rate_change - the plan premium for coverage months already billed has
            been restated after the fact;
            duplicate_payment_refund - the member's money reached the plan twice for the same
            coverage month and the surplus is handed back;
            cms_retroactive_disenrollment - CMS has ended the coverage with effect from a date
            already billed;
            low_income_subsidy_premium_reduction - the member has been awarded a low income
            premium subsidy, so the subsidised part of the plan premium is given back;
            billing_error_correction - the plan raised the charge wrongly in the first place;
            part_b_premium_reduction - the entry carries a Part B premium reduction handled
            through Social Security.

    Returns:
        A confirmation sentence naming the reference number the plan has assigned to the new
        credit entry (a string beginning apc_), the amount credited written to two decimal places
        in USD, the coverage month the credit belongs to as YYYY-MM, and the reference number of
        the plan premium charge it relieves. The sentence is returned only when the entry has
        been booked on the premium account, so its presence is what indicates the call completed.
    """
    source_rows = ctx.find("advantage_premium_ledger",
                           advantage_premium_entry_id=source_premium_entry_id)
    charge = source_rows[0] if source_rows else {}
    charge_amount = round(float(charge.get("amount") or 0), 2)
    posted = round(float(credit_amount), 2)
    if posted > charge_amount:
        effect = "overpayment"
    elif posted == charge_amount:
        effect = "settles_balance"
    else:
        effect = "partial_payment"
    rid = ctx.make_id("apc_", advantage_enrollment_id, source_premium_entry_id,
                      credit_amount, adjustment_reason_code)
    ctx.create("advantage_premium_ledger", rid,
               advantage_premium_entry_id=rid,
               advantage_enrollment_id=advantage_enrollment_id,
               customer_id=charge.get("customer_id", ""),
               event_type="advantage_premium_credit_adjustment",
               billing_period=charge.get("billing_period", ""),
               posted_date=ctx.now()[:10],
               amount=round(float(credit_amount), 2),
               payment_channel="not_applicable",
               balance_effect=effect,
               source_premium_entry_id=source_premium_entry_id,
               adjustment_reason_code=adjustment_reason_code,
               remittance_reference="")
    return (f"Credit entry {rid} for {posted:.2f} USD posted to the premium account for coverage "
            f"month {charge.get('billing_period', '')}, relieving charge {source_premium_entry_id}.")


@tool(owner="user", rw="write")
def end_plan_membership_007ca425(ctx: ToolContext, advantage_enrollment_id: str,
                                 advantage_enrollment_request_id: str,
                                 closing_premium_balance: float) -> str:
    """Bring a member's own Medicare Advantage enrollment to an end, as the member themselves
    elects, and settle what they are left owing for plan premium. The enrollment is moved out of
    coverage and marked as ended by the member's own election, coverage is dated to the last day
    of the month the plan is handling the election in, the plan premium still owed is written on
    the enrollment as the member's closing balance, and the member's own recorded request to
    leave is marked as carried out. Afterwards the member is no longer covered by the plan from
    the day after that coverage end date, and the closing balance is the figure they will be
    billed for. Success is the confirmation the member receives naming the last day of their
    coverage and the balance left owing.

    Args:
        advantage_enrollment_id: Id class — the reference number of the member's Medicare
            Advantage enrollment that is being brought to an end, read from their enrollment
            record before the call.
        advantage_enrollment_request_id: Id class — the reference number of the member's own
            recorded request to leave the plan, read from their enrollment intake record before
            the call.
        closing_premium_balance: Fixed-format class — the plan premium the member is left owing,
            in USD as a decimal number carried to 2 decimal places, rounded half away from zero
            to the nearest cent at the moment it is passed; zero is written as 0.0 and an empty
            value is not accepted.

    Returns:
        A confirmation sentence naming the enrollment reference number that has been ended, the
        last day of coverage as YYYY-MM-DD, and the closing plan premium balance written to two
        decimal places in USD. The sentence is returned only once the enrollment has been moved
        out of coverage and the balance written on it, so its presence is what indicates the call
        completed.
    """
    today = ctx.now()[:10]
    year = int(today[:4])
    month = int(today[5:7])
    coverage_end = f"{year:04d}-{month:02d}-{calendar.monthrange(year, month)[1]:02d}"
    ctx.update("advantage_enrollments", advantage_enrollment_id,
               status="disenrolled",
               coverage_end_date=coverage_end,
               disenrollment_reason_code="voluntary_election",
               premium_balance_due=round(float(closing_premium_balance), 2))
    ctx.update("advantage_enrollment_requests", advantage_enrollment_request_id,
               intake_status="completed")
    return (f"Enrollment {advantage_enrollment_id} ended at the member's own election; coverage "
            f"runs to {coverage_end} and the closing plan premium balance is "
            f"{round(float(closing_premium_balance), 2):.2f} USD.")


@tool(owner="user", rw="write")
def withdraw_pending_election_40acc444(ctx: ToolContext, advantage_enrollment_id: str,
                                       advantage_enrollment_request_id: str,
                                       premium_standing_to_credit: float) -> str:
    """Take back a Medicare Advantage application the member has put in but whose coverage has not
    begun, as the member themselves elects, and settle the money standing on it. The application is
    closed off before it ever takes effect, the reason recorded against it is that it was taken back
    before the coverage was due to begin, the day coverage would have started is written up as the
    day the application closes, the money standing to the member's credit is written on the
    application record, and the member's own recorded request is marked as carried out. Afterwards
    the member never held that plan at all and the credit is the figure that will be handed back to
    them. Success is the confirmation the member receives naming the application and the credit.

    Args:
        advantage_enrollment_id: Id class — the reference number of the Medicare Advantage
            application the member is taking back, read from their enrollment record before the call.
        advantage_enrollment_request_id: Id class — the reference number of the member's own recorded
            request about that application, read from their enrollment intake record before the call.
        premium_standing_to_credit: Fixed-format class — the money standing to the member's credit on
            the application, in USD as a decimal number carried to 2 decimal places, rounded half
            away from zero to the nearest cent at the moment it is passed; zero is written as 0.0 and
            an empty value is not accepted.

    Returns:
        A confirmation sentence naming the application reference number that has been taken back, the
        day the application closes as YYYY-MM-DD, and the money standing to the member's credit
        written to two decimal places in USD. The sentence is returned only once the application has
        been closed off and the credit written on it, so its presence is what indicates the call
        completed.
    """
    rows = ctx.find("advantage_enrollments", advantage_enrollment_id=advantage_enrollment_id)
    closes_on = rows[0].get("coverage_effective_date", "") if rows else ""
    ctx.update("advantage_enrollments", advantage_enrollment_id,
               status="cancelled_before_effective",
               coverage_end_date=closes_on,
               disenrollment_reason_code="withdrawn_before_effective",
               premium_balance_due=round(float(premium_standing_to_credit), 2))
    ctx.update("advantage_enrollment_requests", advantage_enrollment_request_id,
               intake_status="completed")
    return (f"Application {advantage_enrollment_id} taken back before coverage began; it closes on "
            f"{closes_on} and {round(float(premium_standing_to_credit), 2):.2f} USD stands to the "
            "member's credit.")


@tool(owner="agent", rw="write")
def reinstate_terminated_coverage_2c8af1d8(ctx: ToolContext, advantage_enrollment_id: str,
                                           advantage_enrollment_request_id: str,
                                           restored_premium_balance: float) -> str:
    """Bring back a Medicare Advantage enrollment that was ended for non-payment, so that the member
    is covered again without a break. The representative does this on the plan's behalf. The
    enrollment is returned to cover, the end date that had been recorded on it is taken off so the
    coverage period runs unbroken from its original start, the reason the coverage had ended is
    cleared, the plan premium the member must pay for the months brought back is written on the
    enrollment as the balance owed, and the member's own recorded request is marked as carried out.
    Afterwards the member is covered again from the original start date and owes that balance.
    Success is the confirmation naming the enrollment and the balance now owed.

    Args:
        advantage_enrollment_id: Id class — the reference number of the Medicare Advantage enrollment
            being brought back, read from the member's enrollment record before the call.
        advantage_enrollment_request_id: Id class — the reference number of the member's recorded
            request about that enrollment, read from their enrollment intake record before the call.
        restored_premium_balance: Fixed-format class — the plan premium the member must pay for the
            coverage months brought back, in USD as a decimal number carried to 2 decimal places,
            rounded half away from zero to the nearest cent at the moment it is passed; zero is
            written as 0.0 and an empty value is not accepted.

    Returns:
        A confirmation sentence naming the enrollment reference number brought back, the original
        first day of coverage as YYYY-MM-DD, and the plan premium balance now owed written to two
        decimal places in USD. The sentence is returned only once the enrollment has been returned to
        cover and the balance written on it, so its presence is what indicates the call completed.
    """
    rows = ctx.find("advantage_enrollments", advantage_enrollment_id=advantage_enrollment_id)
    began_on = rows[0].get("coverage_effective_date", "") if rows else ""
    ctx.update("advantage_enrollments", advantage_enrollment_id,
               status="active",
               coverage_end_date="",
               disenrollment_reason_code="not_applicable",
               premium_balance_due=round(float(restored_premium_balance), 2))
    ctx.update("advantage_enrollment_requests", advantage_enrollment_request_id,
               intake_status="completed")
    return (f"Enrollment {advantage_enrollment_id} brought back into cover from {began_on} with no "
            f"break; {round(float(restored_premium_balance), 2):.2f} USD of plan premium is now owed.")


@tool(owner="agent", rw="write")
def post_corrected_claim_line_a6b381de(ctx: ToolContext, advantage_enrollment_id: str,
                                       customer_id: str, advantage_claim_id: str,
                                       advantage_service_request_id: str,
                                       member_cost_share: float) -> str:
    """Restate a medical claim line the plan has already settled, by putting a corrected line in its
    place on the member's claim history. The representative does this on the plan's behalf. The
    corrected line copies the date of service, the benefit category, the provider's contract standing
    on that date, the amount the plan recognises for the service, the provider and the line number
    from the line it replaces, records the money the member owes on it, marks the line as paid with
    no denial reason, and carries both the reference of the line it replaces and the reference of the
    coverage request that authorised the service. Afterwards the member's claim history shows the
    corrected line beside the line it replaces, and the money owed on the corrected line is what the
    member will be billed. Success is the confirmation naming the corrected line and what is owed.

    Args:
        advantage_enrollment_id: Id class — the reference number of the Medicare Advantage enrollment
            the service was given under, read from the member's enrollment record before the call.
        customer_id: Id class — the member reference number read from the member profile before the
            call.
        advantage_claim_id: Id class — the reference number of the settled claim line being restated,
            read from the member's claim history before the call.
        advantage_service_request_id: Id class — the reference number of the coverage request that
            authorised the service, read from the member's coverage requests before the call.
        member_cost_share: Fixed-format class — the money the member owes on the corrected line, in
            USD as a decimal number carried to 2 decimal places, rounded half away from zero to the
            nearest cent at the moment it is passed; zero is written as 0.0 and an empty value is not
            accepted.

    Returns:
        A confirmation sentence naming the reference number the plan has assigned to the corrected
        line (a string beginning acc_), the date of service it carries as YYYY-MM-DD, the money the
        member owes written to two decimal places in USD, and the reference number of the line it
        replaces. The sentence is returned only once the corrected line stands on the claim history,
        so its presence is what indicates the call completed.
    """
    rows = ctx.find("advantage_medical_claims", advantage_claim_id=advantage_claim_id)
    original = rows[0] if rows else {}
    rid = ctx.make_id("acc_", advantage_enrollment_id, advantage_claim_id,
                      advantage_service_request_id, member_cost_share)
    ctx.create("advantage_medical_claims", rid,
               advantage_claim_id=rid,
               advantage_enrollment_id=advantage_enrollment_id,
               customer_id=customer_id,
               event_type="advantage_claim_adjudication",
               date_of_service=original.get("date_of_service", ""),
               processed_date=ctx.now()[:10],
               service_category=original.get("service_category", ""),
               place_of_service=original.get("place_of_service", ""),
               network_status=original.get("network_status", ""),
               billed_amount=round(float(original.get("billed_amount") or 0), 2),
               plan_allowed_amount=round(float(original.get("plan_allowed_amount") or 0), 2),
               member_cost_share=round(float(member_cost_share), 2),
               claim_status="paid",
               denial_reason_code="not_applicable",
               provider_npi=original.get("provider_npi", ""),
               authorization_reference=advantage_service_request_id,
               source_claim_id=advantage_claim_id,
               line_sequence=original.get("line_sequence", "1"))
    return (f"Corrected line {rid} posted for service on {original.get('date_of_service', '')}; the "
            f"member owes {round(float(member_cost_share), 2):.2f} USD on it, replacing line "
            f"{advantage_claim_id}.")

"""Hidden task tools of the appeals_and_grievances difficulty (Westbridge Military Health Services,
TRICARE West Region). Each tool performs exactly one atomic write on the appeal records; every
value it books is passed in by the caller exactly as stated in its Args.
"""

from erlbench import ToolContext, tool


@tool(owner="user", rw="write")
def file_select_line_reconsideration_8918facf(ctx: ToolContext, customer_id: str, subject_claim_line_id: str,
                                              subject_referral_authorization_id: str, subject_enrollment_id: str,
                                              subject_claim_number: str, initial_determination_date: str,
                                              filed_by: str, amount_in_dispute: float) -> str:
    """The appellant opens, in their own name, a Claim Factual Reconsideration of one denied TRICARE
    Select claim line. One call opens one new reconsideration case on that single line: the case is
    recorded as received today on the standard review track with status filed, carrying the claim
    number, the determination date of the line, who is filing and the amount in dispute given here;
    no appointment of representative is marked as on file and no case reference exists until the
    region acknowledges the case. The appellant can follow the new case on the beneficiary web
    portal and through customer service from the moment it is opened.

    Args:
        customer_id: Id class — the beneficiary reference number of the patient the claim line belongs
            to, as returned by the beneficiary profile lookup.
        subject_claim_line_id: Id class — the reference number of the adjudicated TRICARE Select claim
            line being contested, as returned by the Select claim line lookup.
        subject_referral_authorization_id: Id class — the reference number of a denied authorization
            the case is about; a claim line case concerns no authorization, so pass the empty string
            "" (the authorization lookup returns no reference for it).
        subject_enrollment_id: Id class — the reference number of an enrollment ended for nonpayment
            the case is about; a claim line case concerns no enrollment, so pass the empty string ""
            (the enrollment lookup returns no reference for it).
        subject_claim_number: Verbatim class — the claim number of that line as printed on the
            Explanation of Benefits and shown on the claim line record returned by the Select claim
            line lookup, copied character for character with its letters, digits and hyphens, with
            no normalisation, addition or deletion (verbatim).
        initial_determination_date: Fixed-format class — the date of the determination being contested,
            written as YYYY-MM-DD (calendar date, no time or time zone).
        filed_by: Enum class — who is filing the case, one of: beneficiary (the patient files their
            own case); parent_or_guardian (a parent or legal guardian files for a minor or
            incapacitated patient); appointed_representative (a person the patient has appointed
            files on the patient's behalf); participating_provider (a participating provider files on
            its own denied claim).
        amount_in_dispute: Fixed-format class — the amount in dispute on the case in USD, 2 decimal
            places (cents), a non-negative number, rounded half up to the cent
            before it is passed.

    Returns:
        A one-line confirmation string of the form "Reconsideration <case_id> opened on claim line
        <subject_claim_line_id> (claim <subject_claim_number>): status filed, received <YYYY-MM-DD>,
        amount in dispute <amount> USD." where <case_id> is the new case reference number (text),
        the received date is today's date and <amount> is the booked amount with two decimals. The
        presence of the case reference number indicates the case was opened.
    """
    rid = ctx.make_id("apc_", customer_id, subject_claim_line_id, subject_referral_authorization_id,
                      subject_enrollment_id, subject_claim_number,
                      initial_determination_date, filed_by, amount_in_dispute)
    today = ctx.now()[:10]
    amt = round(float(amount_in_dispute), 2)
    ctx.create("appeal_cases", rid, appeal_case_id=rid, customer_id=customer_id,
               variant_name="Claim Factual Reconsideration", status="filed", appeal_reference="",
               filed_by=filed_by, representative_appointment_on_file=False, subject_kind="claim_line",
               subject_plan="tricare_select", subject_claim_line_id=subject_claim_line_id,
               subject_claim_number=subject_claim_number,
               subject_referral_authorization_id=subject_referral_authorization_id,
               subject_enrollment_id=subject_enrollment_id, initial_determination_date=initial_determination_date,
               filing_date=today, review_track="standard", amount_in_dispute=round(float(amount_in_dispute), 2),
               acknowledgment_date="", decision_date="", dismissal_reason="not_applicable",
               escalation_date="")
    return (f"Reconsideration {rid} opened on claim line {subject_claim_line_id} (claim {subject_claim_number}): "
            f"status filed, received {today}, amount in dispute {amt:.2f} USD.")


@tool(owner="user", rw="write")
def join_select_line_reconsideration_711ff8e9(ctx: ToolContext, customer_id: str, subject_claim_line_id: str,
                                              subject_referral_authorization_id: str, subject_enrollment_id: str,
                                              subject_claim_number: str, initial_determination_date: str,
                                              filed_by: str, amount_in_dispute: float) -> str:
    """The appellant joins, in their own name, a further denied line of a TRICARE Select claim to the
    Claim Factual Reconsideration already open on that claim. One call records the joining line as
    its own case record keeping its own line reference: it is recorded as received today on the
    standard review track with status filed, under the same claim number, with the line's own
    determination date, who is filing and the amount in dispute given here (the amount the case
    carries once this line has joined it); no appointment of representative is marked as on file.
    The appellant can follow the joined line with the rest of the case on the beneficiary web portal
    and through customer service.

    Args:
        customer_id: Id class — the beneficiary reference number of the patient the claim line belongs
            to, as returned by the beneficiary profile lookup.
        subject_claim_line_id: Id class — the reference number of the adjudicated TRICARE Select claim
            line that joins the open case, as returned by the Select claim line lookup.
        subject_referral_authorization_id: Id class — the reference number of a denied authorization
            the case is about; a claim line case concerns no authorization, so pass the empty string
            "" (the authorization lookup returns no reference for it).
        subject_enrollment_id: Id class — the reference number of an enrollment ended for nonpayment
            the case is about; a claim line case concerns no enrollment, so pass the empty string ""
            (the enrollment lookup returns no reference for it).
        subject_claim_number: Verbatim class — the claim number of that line as printed on the
            Explanation of Benefits and shown on the claim line record returned by the Select claim
            line lookup, copied character for character with its letters, digits and hyphens, with
            no normalisation, addition or deletion (verbatim).
        initial_determination_date: Fixed-format class — the date of the determination on the joining
            line, written as YYYY-MM-DD (calendar date, no time or time zone).
        filed_by: Enum class — who is filing, one of: beneficiary (the patient files their own case);
            parent_or_guardian (a parent or legal guardian files for a minor or incapacitated
            patient); appointed_representative (a person the patient has appointed files on the
            patient's behalf); participating_provider (a participating provider files on its own
            denied claim).
        amount_in_dispute: Fixed-format class — the amount in dispute recorded on the joining line in
            USD, 2 decimal places (cents), a non-negative number, rounded half
            up to the cent before it is passed.

    Returns:
        A one-line confirmation string of the form "Claim line <subject_claim_line_id> joined to the
        reconsideration on claim <subject_claim_number> as record <record_id>: status filed, received
        <YYYY-MM-DD>, amount in dispute <amount> USD." where <record_id> is the reference number of
        the joining line's case record (text), the received date is today's date and <amount> is the
        booked amount with two decimals. The presence of the record reference number indicates the
        line was joined.
    """
    rid = ctx.make_id("apj_", customer_id, subject_claim_line_id, subject_referral_authorization_id,
                      subject_enrollment_id, subject_claim_number,
                      initial_determination_date, filed_by, amount_in_dispute)
    today = ctx.now()[:10]
    amt = round(float(amount_in_dispute), 2)
    ctx.create("appeal_cases", rid, appeal_case_id=rid, customer_id=customer_id,
               variant_name="Claim Factual Reconsideration", status="filed", appeal_reference="",
               filed_by=filed_by, representative_appointment_on_file=False, subject_kind="claim_line",
               subject_plan="tricare_select", subject_claim_line_id=subject_claim_line_id,
               subject_claim_number=subject_claim_number,
               subject_referral_authorization_id=subject_referral_authorization_id,
               subject_enrollment_id=subject_enrollment_id, initial_determination_date=initial_determination_date,
               filing_date=today, review_track="standard", amount_in_dispute=round(float(amount_in_dispute), 2),
               acknowledgment_date="", decision_date="", dismissal_reason="not_applicable",
               escalation_date="")
    return (f"Claim line {subject_claim_line_id} joined to the reconsideration on claim {subject_claim_number} "
            f"as record {rid}: status filed, received {today}, amount in dispute {amt:.2f} USD.")


@tool(owner="user", rw="write")
def request_formal_review_d6793db3(ctx: ToolContext, appeal_case_id: str, amount_in_dispute: float) -> str:
    """The appellant asks, in their own name, for a formal review of a decided Claim Factual
    Reconsideration. One call moves that case to status escalated, records today as the date the
    next-level request was received and books the amount in dispute given here as the amount carried
    to the next level; the case file is then forwarded to the Defense Health Agency appeals division.
    The appellant can see the escalated status and the request date on the beneficiary web portal and
    through customer service.

    Args:
        appeal_case_id: Id class — the reference number of the decided reconsideration case, as
            returned by the appeal case lookup.
        amount_in_dispute: Fixed-format class — the amount in dispute carried to the next level in USD, 2
            decimal places (cents), a non-negative number, rounded half up
            to the cent before it is passed.

    Returns:
        A one-line confirmation string of the form "Formal review requested for case <appeal_case_id>:
        status escalated, request received <YYYY-MM-DD>, amount in dispute <amount> USD." where the
        date is today's date and <amount> is the booked amount with two decimals. A status of
        escalated indicates the request was recorded.
    """
    today = ctx.now()[:10]
    amt = round(float(amount_in_dispute), 2)
    ctx.update("appeal_cases", appeal_case_id, status="escalated", escalation_date=today,
               amount_in_dispute=round(float(amount_in_dispute), 2))
    return (f"Formal review requested for case {appeal_case_id}: status escalated, request received {today}, "
            f"amount in dispute {amt:.2f} USD.")


@tool(owner="user", rw="write")
def file_allowable_charge_review_fa2a3df4(ctx: ToolContext, customer_id: str, subject_claim_line_id: str,
                                          subject_referral_authorization_id: str, subject_enrollment_id: str,
                                          subject_claim_number: str, initial_determination_date: str,
                                          filed_by: str, amount_in_dispute: float) -> str:
    """The appellant opens, in their own name, an Allowable Charge Review of the allowed amount TRICARE
    set on one paid TRICARE Select claim line. One call opens one new review case on that single line:
    the case is recorded as received today on the standard review track with status filed, carrying
    the claim number, the determination date of the line, who is filing and the amount in dispute given
    here; no appointment of representative is marked as on file and no case reference exists until the
    region acknowledges the case. The appellant can follow the review on the beneficiary web portal and
    through customer service from the moment it is opened.

    Args:
        customer_id: Id class — the beneficiary reference number of the patient the claim line belongs
            to, as returned by the beneficiary profile lookup.
        subject_claim_line_id: Id class — the reference number of the paid TRICARE Select claim line
            whose allowed amount is contested, as returned by the Select claim line lookup.
        subject_referral_authorization_id: Id class — the reference number of a denied authorization
            the case is about; a review of an allowed amount concerns no authorization, so pass the
            empty string "" (the authorization lookup returns no reference for it).
        subject_enrollment_id: Id class — the reference number of an enrollment ended for nonpayment
            the case is about; a review of an allowed amount concerns no enrollment, so pass the empty
            string "" (the enrollment lookup returns no reference for it).
        subject_claim_number: Verbatim class — the claim number of that line as printed on the
            Explanation of Benefits and shown on the claim line record returned by the Select claim
            line lookup, copied character for character with its letters, digits and hyphens, with
            no normalisation, addition or deletion (verbatim).
        initial_determination_date: Fixed-format class — the date of the determination being contested,
            written as YYYY-MM-DD (calendar date, no time or time zone).
        filed_by: Enum class — who is filing the case, one of: beneficiary (the patient files their
            own case); parent_or_guardian (a parent or legal guardian files for a minor or
            incapacitated patient); appointed_representative (a person the patient has appointed
            files on the patient's behalf); participating_provider (a participating provider files on
            its own claim).
        amount_in_dispute: Fixed-format class — the amount in dispute on the case in USD, 2 decimal
            places (cents), a non-negative number, rounded half up to the cent before it is passed.

    Returns:
        A one-line confirmation string of the form "Allowable Charge Review <case_id> opened on claim
        line <subject_claim_line_id> (claim <subject_claim_number>): status filed, received
        <YYYY-MM-DD>, amount in dispute <amount> USD." where <case_id> is the new case reference number
        (text), the received date is today's date and <amount> is the booked amount with two decimals.
        The presence of the case reference number indicates the review was opened.
    """
    rid = ctx.make_id("acr_", customer_id, subject_claim_line_id, subject_referral_authorization_id,
                      subject_enrollment_id, subject_claim_number, initial_determination_date, filed_by,
                      amount_in_dispute)
    today = ctx.now()[:10]
    ctx.create("appeal_cases", rid, appeal_case_id=rid, customer_id=customer_id,
               variant_name="Allowable Charge Review", status="filed", appeal_reference="",
               filed_by=filed_by, representative_appointment_on_file=False, subject_kind="allowable_charge",
               subject_plan="tricare_select", subject_claim_line_id=subject_claim_line_id,
               subject_claim_number=subject_claim_number,
               subject_referral_authorization_id=subject_referral_authorization_id,
               subject_enrollment_id=subject_enrollment_id,
               initial_determination_date=initial_determination_date,
               filing_date=today, review_track="standard", amount_in_dispute=round(float(amount_in_dispute), 2),
               acknowledgment_date="", decision_date="", dismissal_reason="not_applicable",
               escalation_date="")
    return (f"Allowable Charge Review {rid} opened on claim line {subject_claim_line_id} (claim {subject_claim_number}): "
            f"status filed, received {today}, amount in dispute {round(float(amount_in_dispute), 2):.2f} USD.")


@tool(owner="user", rw="write")
def join_line_charge_review_4bed256c(ctx: ToolContext, customer_id: str, subject_claim_line_id: str,
                                     subject_referral_authorization_id: str, subject_enrollment_id: str,
                                     subject_claim_number: str, initial_determination_date: str,
                                     filed_by: str, amount_in_dispute: float) -> str:
    """The appellant joins, in their own name, a further paid line of a TRICARE Select claim to the
    Allowable Charge Review already open on that claim for the same allowed-amount dispute. One call
    records the joining line as its own review record keeping its own line reference: it is recorded
    as received today on the standard review track with status filed, under the same claim number,
    with the line's own determination date, who is filing and the amount in dispute given here (the
    amount the review carries once this line has joined it); no appointment of representative is
    marked as on file. The appellant can follow the joined line with the rest of the review on the
    beneficiary web portal and through customer service.

    Args:
        customer_id: Id class — the beneficiary reference number of the patient the claim line belongs
            to, as returned by the beneficiary profile lookup.
        subject_claim_line_id: Id class — the reference number of the paid TRICARE Select claim line
            that joins the open review, as returned by the Select claim line lookup.
        subject_referral_authorization_id: Id class — the reference number of a denied authorization
            the case is about; a review of an allowed amount concerns no authorization, so pass the
            empty string "" (the authorization lookup returns no reference for it).
        subject_enrollment_id: Id class — the reference number of an enrollment ended for nonpayment
            the case is about; a review of an allowed amount concerns no enrollment, so pass the empty
            string "" (the enrollment lookup returns no reference for it).
        subject_claim_number: Verbatim class — the claim number of that line as printed on the
            Explanation of Benefits and shown on the claim line record returned by the Select claim
            line lookup, copied character for character with its letters, digits and hyphens, with
            no normalisation, addition or deletion (verbatim).
        initial_determination_date: Fixed-format class — the date of the determination on the joining
            line, written as YYYY-MM-DD (calendar date, no time or time zone).
        filed_by: Enum class — who is filing, one of: beneficiary (the patient files their own case);
            parent_or_guardian (a parent or legal guardian files for a minor or incapacitated
            patient); appointed_representative (a person the patient has appointed files on the
            patient's behalf); participating_provider (a participating provider files on its own
            claim).
        amount_in_dispute: Fixed-format class — the amount in dispute recorded on the joining line in
            USD, 2 decimal places (cents), a non-negative number, rounded half up to the cent before
            it is passed.

    Returns:
        A one-line confirmation string of the form "Claim line <subject_claim_line_id> joined to the
        Allowable Charge Review on claim <subject_claim_number> as record <record_id>: status filed,
        received <YYYY-MM-DD>, amount in dispute <amount> USD." where <record_id> is the reference
        number of the joining line's review record (text), the received date is today's date and
        <amount> is the booked amount with two decimals. The presence of the record reference number
        indicates the line was joined.
    """
    rid = ctx.make_id("acj_", customer_id, subject_claim_line_id, subject_referral_authorization_id,
                      subject_enrollment_id, subject_claim_number, initial_determination_date, filed_by,
                      amount_in_dispute)
    today = ctx.now()[:10]
    ctx.create("appeal_cases", rid, appeal_case_id=rid, customer_id=customer_id,
               variant_name="Allowable Charge Review", status="filed", appeal_reference="",
               filed_by=filed_by, representative_appointment_on_file=False, subject_kind="allowable_charge",
               subject_plan="tricare_select", subject_claim_line_id=subject_claim_line_id,
               subject_claim_number=subject_claim_number,
               subject_referral_authorization_id=subject_referral_authorization_id,
               subject_enrollment_id=subject_enrollment_id,
               initial_determination_date=initial_determination_date,
               filing_date=today, review_track="standard", amount_in_dispute=round(float(amount_in_dispute), 2),
               acknowledgment_date="", decision_date="", dismissal_reason="not_applicable",
               escalation_date="")
    return (f"Claim line {subject_claim_line_id} joined to the Allowable Charge Review on claim {subject_claim_number} "
            f"as record {rid}: status filed, received {today}, amount in dispute "
            f"{round(float(amount_in_dispute), 2):.2f} USD.")


@tool(owner="user", rw="write")
def request_second_level_reconsideration_e1311ea5(ctx: ToolContext, appeal_case_id: str,
                                                  amount_in_dispute: float) -> str:
    """The appellant asks, in their own name, for a second-level reconsideration of a decided Medical
    Necessity Reconsideration. One call moves that case to status escalated, records today as the date
    the next-level request was received and books the amount in dispute given here as the amount
    carried to the next level; the case file is then forwarded to the national quality monitoring
    contractor. The appellant can see the escalated status and the request date on the beneficiary web
    portal and through customer service.

    Args:
        appeal_case_id: Id class — the reference number of the decided medical necessity
            reconsideration case, as returned by the appeal case lookup.
        amount_in_dispute: Fixed-format class — the amount in dispute carried to the next level in USD, 2
            decimal places (cents), a non-negative number, rounded half up to the cent before it is
            passed.

    Returns:
        A one-line confirmation string of the form "Second-level reconsideration requested for case
        <appeal_case_id>: status escalated, request received <YYYY-MM-DD>, amount in dispute <amount>
        USD." where the date is today's date and <amount> is the booked amount with two decimals. A
        status of escalated indicates the request was recorded.
    """
    today = ctx.now()[:10]
    ctx.update("appeal_cases", appeal_case_id, status="escalated", escalation_date=today,
               amount_in_dispute=round(float(amount_in_dispute), 2))
    return (f"Second-level reconsideration requested for case {appeal_case_id}: status escalated, request received "
            f"{today}, amount in dispute {round(float(amount_in_dispute), 2):.2f} USD.")


@tool(owner="agent", rw="write")
def take_expedited_reconsideration_1b494fd4(ctx: ToolContext, customer_id: str, subject_claim_line_id: str,
                                            subject_referral_authorization_id: str, subject_enrollment_id: str,
                                            initial_determination_date: str, filed_by: str,
                                            amount_in_dispute: float) -> str:
    """Customer service takes, by telephone, an Expedited Medical Necessity Reconsideration of one
    authorization request denied as not medically necessary. One call opens one new case on that
    authorization: it is recorded as received today on the expedited review track with status filed,
    carrying the authorization reference, the date of the denial, who is filing and the amount in
    dispute given here; no appointment of representative is marked as on file and no case reference
    exists until the region acknowledges the case. The caller can follow the case on the beneficiary
    web portal and through customer service from the moment it is taken.

    Args:
        customer_id: Id class — the beneficiary reference number of the patient the authorization was
            requested for, as returned by the beneficiary profile lookup.
        subject_claim_line_id: Id class — the reference number of a claim line the case is about; a
            reconsideration of an authorization denial concerns no claim line, so pass the empty string
            "" (the claim line lookup returns no reference for it).
        subject_referral_authorization_id: Id class — the reference number of the denied authorization
            request being reconsidered, as returned by the authorization lookup.
        subject_enrollment_id: Id class — the reference number of an enrollment ended for nonpayment
            the case is about; a reconsideration of an authorization denial concerns no enrollment, so
            pass the empty string "" (the enrollment lookup returns no reference for it).
        initial_determination_date: Fixed-format class — the date of the denial being reconsidered,
            written as YYYY-MM-DD (calendar date, no time or time zone).
        filed_by: Enum class — who is asking for the reconsideration, one of: beneficiary (the patient
            asks for their own case); parent_or_guardian (a parent or legal guardian asks for a minor
            or incapacitated patient); appointed_representative (a person the patient has appointed asks
            on the patient's behalf); participating_provider (a participating provider asks on its own
            request).
        amount_in_dispute: Fixed-format class — the amount in dispute on the case in USD, 2 decimal
            places (cents), a non-negative number, rounded half up to the cent before it is passed.

    Returns:
        A one-line confirmation string of the form "Expedited reconsideration <case_id> taken on
        authorization <subject_referral_authorization_id>: status filed, expedited track, received
        <YYYY-MM-DD>, amount in dispute <amount> USD." where <case_id> is the new case reference number
        (text), the received date is today's date and <amount> is the booked amount with two decimals.
        The presence of the case reference number indicates the case was taken.
    """
    rid = ctx.make_id("aex_", customer_id, subject_claim_line_id, subject_referral_authorization_id,
                      subject_enrollment_id, initial_determination_date, filed_by, amount_in_dispute)
    today = ctx.now()[:10]
    ctx.create("appeal_cases", rid, appeal_case_id=rid, customer_id=customer_id,
               variant_name="Expedited Medical Necessity Reconsideration", status="filed", appeal_reference="",
               filed_by=filed_by, representative_appointment_on_file=False, subject_kind="authorization_denial",
               subject_plan="not_applicable", subject_claim_line_id=subject_claim_line_id, subject_claim_number="",
               subject_referral_authorization_id=subject_referral_authorization_id,
               subject_enrollment_id=subject_enrollment_id,
               initial_determination_date=initial_determination_date,
               filing_date=today, review_track="expedited", amount_in_dispute=round(float(amount_in_dispute), 2),
               acknowledgment_date="", decision_date="", dismissal_reason="not_applicable",
               escalation_date="")
    return (f"Expedited reconsideration {rid} taken on authorization {subject_referral_authorization_id}: status filed, "
            f"expedited track, received {today}, amount in dispute {round(float(amount_in_dispute), 2):.2f} USD.")

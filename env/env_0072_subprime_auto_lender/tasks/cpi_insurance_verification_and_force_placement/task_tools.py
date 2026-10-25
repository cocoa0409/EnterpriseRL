"""Hidden task tools for the cpi_insurance_verification_and_force_placement difficulty.

Each tool performs one atomic write on an insurance tracking record and judges nothing:
the outcome of a proof re-review and the amount of a refund are worked out by the caller
from the published rules and passed in as fixed-format or enum values.
"""

from erlbench import ToolContext, tool


_PROOF_FIELDS = ("insurer_name", "policy_number", "policy_effective_date", "policy_expiration_date",
                 "comprehensive_deductible_usd", "collision_deductible_usd", "lienholder_listed",
                 "verification_source")


@tool(owner="agent", rw="write")
def rereview_feed_proof_7d2611c6(ctx: ToolContext, cpi_coverage_id: str, source_activity_id: str,
                                 proof_result: str) -> str:
    """Record the desk's re-review of a proof of the borrower's own insurance that reached the
    company through an insurer's electronic feed and is already on the insurance tracking
    record. One call adds one new proof-review entry to that tracking record, dated today,
    carrying the outcome passed in and every detail of the proof being re-reviewed (insurer,
    policy number, effective and expiration dates, comprehensive and collision deductibles,
    lienholder flag and arrival channel) copied unchanged from that proof's existing entry.
    The tracking record's status, plan, premium total and policy-on-file details are left as
    they are, and the earlier entry is kept unchanged. On success the new entry is visible in
    the record's tracking activity.

    Args:
        cpi_coverage_id: Id class — the reference number of the insurance tracking record the
            proof belongs to, as returned by the insurance tracking record lookup.
        source_activity_id: Id class — the reference number of the existing proof-review entry
            for the feed proof being re-reviewed, as returned by the tracking activity lookup.
        proof_result: Enum class — the re-review outcome, exactly one of:
            "accepted" — the proof meets every test the re-review applies;
            "rejected_no_physical_damage" — the proof does not show the required physical-damage coverages;
            "rejected_vin_mismatch" — the proof does not list the contract's exact VIN;
            "rejected_named_insured" — no named insured on the proof satisfies the named-insured rule;
            "rejected_no_lienholder" — the proof fails the lienholder and loss-payee test;
            "rejected_deductible_too_high" — a comprehensive or collision deductible is above its ceiling;
            "rejected_binder_term" — the proof is a binder whose period is longer than allowed;
            "rejected_expiring" — the proof fails the coverage-reach test on its expiration date;
            "not_applicable" — the record carries no proof of this arrival channel, so there is nothing to re-review.

    Returns:
        A confirmation string naming the new proof-review entry reference number (text), the
        tracking record reference number (text), the outcome recorded (text, one of the enum
        literals above) and the review date (YYYY-MM-DD). The presence of the entry reference
        number indicates the re-review was recorded.
    """
    src = ctx.find("cpi_activities", cpi_activity_id=source_activity_id)
    shown = {k: src[0].get(k) for k in _PROOF_FIELDS} if src else {}
    today = ctx.now()[:10]
    rid = ctx.make_id("cpa_", cpi_coverage_id, source_activity_id, proof_result, today)
    cov = ctx.find("cpi_coverages", cpi_coverage_id=cpi_coverage_id)
    ctx.create("cpi_activities", rid, cpi_activity_id=rid, cpi_coverage_id=cpi_coverage_id,
               contract_id=cov[0].get("contract_id") if cov else "",
               customer_id=cov[0].get("customer_id") if cov else "",
               event_type="cpi_proof_verified", activity_date=today,
               insurer_name=shown.get("insurer_name", ""), policy_number=shown.get("policy_number", ""),
               policy_effective_date=shown.get("policy_effective_date", ""),
               policy_expiration_date=shown.get("policy_expiration_date", ""),
               comprehensive_deductible_usd=round(float(shown.get("comprehensive_deductible_usd") or 0), 2),
               collision_deductible_usd=round(float(shown.get("collision_deductible_usd") or 0), 2),
               lienholder_listed=bool(shown.get("lienholder_listed", False)),
               verification_source=shown.get("verification_source", "insurer_edi_feed"),
               proof_result=proof_result, notice_type="not_applicable", billing_period_start="",
               billing_period_end="", amount_usd=0.0, billing_method="not_applicable", related_activity_id="",
               refund_basis="not_applicable", refund_disposition="not_applicable")
    return (f"Feed proof re-review recorded: entry {rid} on tracking record {cpi_coverage_id}, "
            f"outcome {proof_result}, review date {today}.")


@tool(owner="agent", rw="write")
def rereview_uploaded_proof_b3d9c591(ctx: ToolContext, cpi_coverage_id: str, source_activity_id: str,
                                     proof_result: str) -> str:
    """Record the desk's re-review of a declarations page or binder that the borrower uploaded
    as proof of their own insurance and that is already on the insurance tracking record. One
    call adds one new proof-review entry to that tracking record, dated today, carrying the
    outcome passed in and every detail of the uploaded proof (insurer, policy or binder number,
    effective and expiration dates, comprehensive and collision deductibles, lienholder flag and
    arrival channel) copied unchanged from the upload's existing entry. The tracking record's
    status, plan, premium total and policy-on-file details are left as they are, and the
    earlier entry is kept unchanged. On success the new entry is visible in the record's
    tracking activity.

    Args:
        cpi_coverage_id: Id class — the reference number of the insurance tracking record the
            upload belongs to, as returned by the insurance tracking record lookup.
        source_activity_id: Id class — the reference number of the existing proof-review entry
            for the uploaded proof being re-reviewed, as returned by the tracking activity lookup.
        proof_result: Enum class — the re-review outcome, exactly one of:
            "accepted" — the upload meets every test the re-review applies;
            "rejected_no_physical_damage" — the upload does not show the required physical-damage coverages;
            "rejected_vin_mismatch" — the upload does not list the contract's exact VIN;
            "rejected_named_insured" — no named insured on the upload satisfies the named-insured rule;
            "rejected_no_lienholder" — the upload fails the lienholder and loss-payee test;
            "rejected_deductible_too_high" — a comprehensive or collision deductible is above its ceiling;
            "rejected_binder_term" — the upload is a binder whose period is longer than allowed;
            "rejected_expiring" — the upload fails the coverage-reach test on its dates;
            "not_applicable" — the record carries no uploaded binder this re-review applies to, so there is nothing to re-review.

    Returns:
        A confirmation string naming the new proof-review entry reference number (text), the
        tracking record reference number (text), the outcome recorded (text, one of the enum
        literals above) and the review date (YYYY-MM-DD). The presence of the entry reference
        number indicates the re-review was recorded.
    """
    src = ctx.find("cpi_activities", cpi_activity_id=source_activity_id)
    shown = {k: src[0].get(k) for k in _PROOF_FIELDS} if src else {}
    today = ctx.now()[:10]
    rid = ctx.make_id("cpa_", cpi_coverage_id, source_activity_id, proof_result, today)
    cov = ctx.find("cpi_coverages", cpi_coverage_id=cpi_coverage_id)
    ctx.create("cpi_activities", rid, cpi_activity_id=rid, cpi_coverage_id=cpi_coverage_id,
               contract_id=cov[0].get("contract_id") if cov else "",
               customer_id=cov[0].get("customer_id") if cov else "",
               event_type="cpi_proof_verified", activity_date=today,
               insurer_name=shown.get("insurer_name", ""), policy_number=shown.get("policy_number", ""),
               policy_effective_date=shown.get("policy_effective_date", ""),
               policy_expiration_date=shown.get("policy_expiration_date", ""),
               comprehensive_deductible_usd=round(float(shown.get("comprehensive_deductible_usd") or 0), 2),
               collision_deductible_usd=round(float(shown.get("collision_deductible_usd") or 0), 2),
               lienholder_listed=bool(shown.get("lienholder_listed", False)),
               verification_source=shown.get("verification_source", "declarations_page_upload"),
               proof_result=proof_result, notice_type="not_applicable", billing_period_start="",
               billing_period_end="", amount_usd=0.0, billing_method="not_applicable", related_activity_id="",
               refund_basis="not_applicable", refund_disposition="not_applicable")
    return (f"Uploaded proof re-review recorded: entry {rid} on tracking record {cpi_coverage_id}, "
            f"outcome {proof_result}, review date {today}.")


@tool(owner="agent", rw="write")
def rereview_faxed_proof_fc99cba3(ctx: ToolContext, cpi_coverage_id: str, source_activity_id: str,
                                  proof_result: str) -> str:
    """Record the desk's re-review of a proof of the borrower's own insurance that the insurer
    faxed to the company and that is already on the insurance tracking record. One call adds
    one new proof-review entry to that tracking record, dated today, carrying the outcome
    passed in and every detail of the faxed proof (insurer, policy number, effective and
    expiration dates, comprehensive and collision deductibles, lienholder flag and arrival
    channel) copied unchanged from the fax's existing entry. The tracking record's status,
    plan, premium total and policy-on-file details are left as they are, and the earlier entry
    is kept unchanged. On success the new entry is visible in the record's tracking activity.

    Args:
        cpi_coverage_id: Id class — the reference number of the insurance tracking record the
            fax belongs to, as returned by the insurance tracking record lookup.
        source_activity_id: Id class — the reference number of the existing proof-review entry
            for the faxed proof being re-reviewed, as returned by the tracking activity lookup.
        proof_result: Enum class — the re-review outcome, exactly one of:
            "accepted" — the fax meets every test the re-review applies;
            "rejected_no_physical_damage" — the fax does not show the required physical-damage coverages;
            "rejected_vin_mismatch" — the fax does not list the contract's exact VIN;
            "rejected_named_insured" — no named insured on the fax satisfies the named-insured rule;
            "rejected_no_lienholder" — the fax fails the lienholder and loss-payee test;
            "rejected_deductible_too_high" — a comprehensive or collision deductible is above its ceiling;
            "rejected_binder_term" — the fax shows a binder whose period is longer than allowed;
            "rejected_expiring" — the fax fails the coverage-reach test on its expiration date;
            "not_applicable" — the record carries no proof of this arrival channel, so there is nothing to re-review.

    Returns:
        A confirmation string naming the new proof-review entry reference number (text), the
        tracking record reference number (text), the outcome recorded (text, one of the enum
        literals above) and the review date (YYYY-MM-DD). The presence of the entry reference
        number indicates the re-review was recorded.
    """
    src = ctx.find("cpi_activities", cpi_activity_id=source_activity_id)
    shown = {k: src[0].get(k) for k in _PROOF_FIELDS} if src else {}
    today = ctx.now()[:10]
    rid = ctx.make_id("cpa_", cpi_coverage_id, source_activity_id, proof_result, today)
    cov = ctx.find("cpi_coverages", cpi_coverage_id=cpi_coverage_id)
    ctx.create("cpi_activities", rid, cpi_activity_id=rid, cpi_coverage_id=cpi_coverage_id,
               contract_id=cov[0].get("contract_id") if cov else "",
               customer_id=cov[0].get("customer_id") if cov else "",
               event_type="cpi_proof_verified", activity_date=today,
               insurer_name=shown.get("insurer_name", ""), policy_number=shown.get("policy_number", ""),
               policy_effective_date=shown.get("policy_effective_date", ""),
               policy_expiration_date=shown.get("policy_expiration_date", ""),
               comprehensive_deductible_usd=round(float(shown.get("comprehensive_deductible_usd") or 0), 2),
               collision_deductible_usd=round(float(shown.get("collision_deductible_usd") or 0), 2),
               lienholder_listed=bool(shown.get("lienholder_listed", False)),
               verification_source=shown.get("verification_source", "insurer_fax"),
               proof_result=proof_result, notice_type="not_applicable", billing_period_start="",
               billing_period_end="", amount_usd=0.0, billing_method="not_applicable", related_activity_id="",
               refund_basis="not_applicable", refund_disposition="not_applicable")
    return (f"Faxed proof re-review recorded: entry {rid} on tracking record {cpi_coverage_id}, "
            f"outcome {proof_result}, review date {today}.")


@tool(owner="user", rw="write")
def mail_closing_month_refund_38a32c3f(ctx: ToolContext, related_activity_id: str, amount_usd: float,
                                       refund_basis: str) -> str:
    """The borrower requests, on their own paid-off contract, the refund check for one
    force-placed premium charge whose billing period ended on the day their insurance tracking
    record closed. One call adds one premium-refund entry for that charge to the tracking
    record, dated today, with the amount and refund basis passed in, marked as mailed to the
    borrower by check at the mailing address on file, and lowers the tracking record's net
    premium total by that amount. No contract, deficiency or other account is touched. On success the refund entry is visible in the
    record's tracking activity.

    Args:
        related_activity_id: Id class — the reference number of the premium-charge entry being
            refunded, as returned by the tracking activity lookup.
        amount_usd: Fixed-format class — the refund check amount in US dollars, a non-negative
            number with 2 decimal places (cents), rounded half-up to the cent.
        refund_basis: Enum class — how the refunded days were determined, exactly one of:
            "full_no_lapse" — the borrower's own coverage ran with no gap from the CPI coverage
            effective date, so every day of the charge's period is refunded;
            "pro_rata_from_proof_effective" — the refund counts the days the borrower's accepted
            proof covers together with the other days the rule counts for it;
            "pro_rata_from_closure" — only the days of the period after the record's closed date
            are refunded.
            "held_premium_release" — reserved for releasing a premium held pending proof review,
            which never reached the contract;
            "not_applicable" — reserved for activity entries that are not refunds.

    Returns:
        A confirmation string naming the new refund entry reference number (text), the premium
        charge refunded (text), the refund amount (USD, two decimals), the refund basis and
        destination (text) and the refund date (YYYY-MM-DD). The presence of the refund entry
        reference number indicates the check was issued.
    """
    amt = round(float(amount_usd), 2)
    charge = ctx.find("cpi_activities", cpi_activity_id=related_activity_id)
    row = charge[0] if charge else {}
    cov_id = row.get("cpi_coverage_id", "")
    today = ctx.now()[:10]
    rid = ctx.make_id("cpr_", related_activity_id, amt)
    ctx.create("cpi_activities", rid, cpi_activity_id=rid, cpi_coverage_id=cov_id,
               contract_id=row.get("contract_id", ""), customer_id=row.get("customer_id", ""),
               event_type="cpi_premium_refunded", activity_date=today, insurer_name="", policy_number="",
               policy_effective_date="", policy_expiration_date="", comprehensive_deductible_usd=0.0,
               collision_deductible_usd=0.0, lienholder_listed=False, verification_source="not_applicable",
               proof_result="not_applicable", notice_type="not_applicable", billing_period_start="",
               billing_period_end="", amount_usd=amt, billing_method="not_applicable",
               related_activity_id=related_activity_id, refund_basis=refund_basis,
               refund_disposition="mailed_to_borrower")
    cov = ctx.find("cpi_coverages", cpi_coverage_id=cov_id)
    if cov:
        ctx.update("cpi_coverages", cov_id,
                   premium_billed_usd=round(float(cov[0].get("premium_billed_usd") or 0) - amt, 2))
    return (f"Refund check issued: entry {rid} for premium charge {related_activity_id}, amount {amt:.2f} USD, "
            f"basis {refund_basis}, mailed_to_borrower, dated {today}.")


@tool(owner="user", rw="write")
def mail_closing_period_refund_6483f0cd(ctx: ToolContext, related_activity_id: str, amount_usd: float,
                                        refund_basis: str) -> str:
    """The borrower requests, on their own paid-off contract, the refund check for the one
    force-placed premium charge whose billing period was still running on the day their
    insurance tracking record closed. One call adds one premium-refund entry for that charge
    to the tracking record, dated today, with the amount and refund basis passed in, marked as
    mailed to the borrower by check at the mailing address on file, and lowers the tracking
    record's net premium total by that amount. No contract, deficiency or other account is
    touched. On success the refund entry is visible in the record's
    tracking activity.

    Args:
        related_activity_id: Id class — the reference number of the premium-charge entry being
            refunded, as returned by the tracking activity lookup.
        amount_usd: Fixed-format class — the refund check amount in US dollars, a non-negative
            number with 2 decimal places (cents), rounded half-up to the cent.
        refund_basis: Enum class — how the refunded days were determined, exactly one of:
            "full_no_lapse" — the borrower's own coverage ran with no gap from the CPI coverage
            effective date, so every day of the charge's period is refunded;
            "pro_rata_from_proof_effective" — the refund counts the days the borrower's accepted
            proof covers together with the other days the rule counts for it;
            "pro_rata_from_closure" — only the days of the period after the record's closed date
            are refunded.
            "held_premium_release" — reserved for releasing a premium held pending proof review,
            which never reached the contract;
            "not_applicable" — reserved for activity entries that are not refunds.

    Returns:
        A confirmation string naming the new refund entry reference number (text), the premium
        charge refunded (text), the refund amount (USD, two decimals), the refund basis and
        destination (text) and the refund date (YYYY-MM-DD). The presence of the refund entry
        reference number indicates the check was issued.
    """
    amt = round(float(amount_usd), 2)
    charge = ctx.find("cpi_activities", cpi_activity_id=related_activity_id)
    row = charge[0] if charge else {}
    cov_id = row.get("cpi_coverage_id", "")
    today = ctx.now()[:10]
    rid = ctx.make_id("cpr_", related_activity_id, amt)
    ctx.create("cpi_activities", rid, cpi_activity_id=rid, cpi_coverage_id=cov_id,
               contract_id=row.get("contract_id", ""), customer_id=row.get("customer_id", ""),
               event_type="cpi_premium_refunded", activity_date=today, insurer_name="", policy_number="",
               policy_effective_date="", policy_expiration_date="", comprehensive_deductible_usd=0.0,
               collision_deductible_usd=0.0, lienholder_listed=False, verification_source="not_applicable",
               proof_result="not_applicable", notice_type="not_applicable", billing_period_start="",
               billing_period_end="", amount_usd=amt, billing_method="not_applicable",
               related_activity_id=related_activity_id, refund_basis=refund_basis,
               refund_disposition="mailed_to_borrower")
    cov = ctx.find("cpi_coverages", cpi_coverage_id=cov_id)
    if cov:
        ctx.update("cpi_coverages", cov_id,
                   premium_billed_usd=round(float(cov[0].get("premium_billed_usd") or 0) - amt, 2))
    return (f"Refund check issued: entry {rid} for premium charge {related_activity_id}, amount {amt:.2f} USD, "
            f"basis {refund_basis}, mailed_to_borrower, dated {today}.")

"""Hidden task tools of difficulty home_claim_settlement (env_0024_homeowners_insurance_carrier).

Each tool performs one atomic claim-ledger write on a HomeGuard policy. The tools never judge
eligibility, prerequisites or amounts: every figure is worked out by the caller from the published
claim rules and passed in, and the tool records it as given.
"""

from erlbench import ToolContext, tool


@tool(owner="agent", rw="write")
def settle_denied_roof_surfacing_b6cb399f(ctx: ToolContext, home_policy_id: str, claim_number: str,
                                          source_entry_id: str, payment_type: str, roof_age_years: int,
                                          deductible_applied: float, amount: float, payee: str) -> str:
    """Issue the claim payment that replaces a below-deductible denial of roof surfacing damage on a
    HomeGuard homeowners claim. One call records one new roof surfacing payment on the dwelling coverage
    part of the named claim, carrying the replacement-cost value and depreciation of the denial it
    replaces, the roof age, the deductible this payment absorbs, the amount paid and the payee. When the
    payment kind is an actual-cash-value initial payment, the recorded depreciation is also withheld on
    the claim as recoverable depreciation in the same call. The claim's paid total rises by the amount;
    the insured sees a new roof payment on the claim file dated today.

    Args:
        home_policy_id: Id class — reference number of the HomeGuard policy the claim is made under, as returned by the home policy lookup for the verified customer.
        claim_number: Verbatim class — the claim number exactly as it appears on the claim's first-notice entry returned by the claim lookup, copied character for character (verbatim).
        source_entry_id: Id class — reference number of the below-deductible denial entry of the roof surfacing that this payment replaces, as returned by the claim lookup.
        payment_type: Enum class — the kind of roof payment: roof_schedule when the roof surfacing is paid on the roof payment schedule percentage; replacement_cost_full when it is paid at its full replacement-cost value with nothing withheld; acv_initial when it is paid at actual cash value with the depreciation withheld for later recovery.
        roof_age_years: Fixed-format class — roof age at the date of loss in integer years (whole years, no decimals).
        deductible_applied: Fixed-format class — part of the occurrence deductible absorbed by this payment, in USD, 2 decimal places, 0.00 when none.
        amount: Fixed-format class — amount paid on this roof surfacing payment, in USD, 2 decimal places, positive.
        payee: Enum class — who the payment is made out to: insured when the check is payable to the named insured alone; insured_and_mortgagee when the mortgagee on file is named as co-payee with the insured.

    Returns:
        A dict rendered as text with: status ("recorded" on success); payment_entry_id (reference
        number of the new roof payment entry); claim_number (the claim paid); payment_type (the kind
        recorded); amount (USD amount paid, 2 decimal places); deductible_applied (USD, 2 decimal
        places); payee (who the payment is made out to); holdback_entry_id (reference number of the
        recoverable depreciation withheld, or "" when nothing was withheld); entry_date (YYYY-MM-DD
        date of the payment).
    """
    denial = (ctx.find("home_claims", home_claim_entry_id=source_entry_id) or [{}])[0]
    report = (ctx.find("home_claims", home_policy_id=home_policy_id, claim_number=claim_number,
                       event_type="home_claim_reported") or [{}])[0]
    kind = {"roof_schedule": "roof_schedule", "replacement_cost_full": "replacement_cost_full",
            "acv_initial": "acv_initial"}.get(payment_type, payment_type)
    made_out = {"insured": "insured", "insured_and_mortgagee": "insured_and_mortgagee"}.get(payee, payee)
    today = ctx.now()[:10]
    rc = round(float(denial.get("replacement_cost_amount") or 0), 2)
    dep = round(float(denial.get("depreciation_amount") or 0), 2)
    rid = ctx.make_id("hcp_", home_policy_id, claim_number, source_entry_id, payment_type, roof_age_years,
                      deductible_applied, amount, payee)
    ctx.create("home_claims", rid, home_claim_entry_id=rid, home_policy_id=home_policy_id,
               customer_id=report.get("customer_id") or denial.get("customer_id"),
               event_type="home_claim_payment", claim_number=claim_number,
               loss_date=report.get("loss_date") or denial.get("loss_date"),
               entry_date=today, peril=report.get("peril") or denial.get("peril"),
               coverage_part="dwelling", property_class="roof_surfacing", payment_type=kind,
               replacement_cost_amount=rc, depreciation_amount=dep,
               deductible_applied=round(float(deductible_applied), 2), incurred_amount=0.0,
               amount=round(float(amount), 2), payee=made_out, roof_age_years=int(roof_age_years),
               denial_reason="none", source_entry_id=source_entry_id)
    hold_id = ""
    if kind == "acv_initial" and dep > 0:
        hold_id = ctx.make_id("hch_", rid)
        ctx.create("home_claims", hold_id, home_claim_entry_id=hold_id, home_policy_id=home_policy_id,
                   customer_id=report.get("customer_id") or denial.get("customer_id"),
                   event_type="home_holdback_withheld", claim_number=claim_number,
                   loss_date=report.get("loss_date") or denial.get("loss_date"),
                   entry_date=today, peril=report.get("peril") or denial.get("peril"),
                   coverage_part="dwelling", property_class="roof_surfacing", payment_type="none",
                   replacement_cost_amount=0.0, depreciation_amount=0.0, deductible_applied=0.0,
                   incurred_amount=0.0, amount=dep, payee="none", roof_age_years=0,
                   denial_reason="none", source_entry_id=rid)
    return str({"status": "recorded", "payment_entry_id": rid, "claim_number": claim_number,
                "payment_type": kind, "amount": round(float(amount), 2),
                "deductible_applied": round(float(deductible_applied), 2), "payee": made_out,
                "holdback_entry_id": hold_id, "entry_date": today})


@tool(owner="user", rw="write")
def accept_structure_supplemental_c73fec14(ctx: ToolContext, home_policy_id: str, claim_number: str,
                                           amount: float, payee: str) -> str:
    """The named insured accepts a supplemental settlement on the other-structures part (detached
    garage, shed, fence and the like) of their own HomeGuard claim, and the acceptance issues it. One call
    records one supplemental payment on the other-structures coverage part of the named claim for the
    accepted amount and payee, dated today; the claim's paid total rises by that amount and the insured
    sees the supplemental payment on their claim file.

    Args:
        home_policy_id: Id class — reference number of the HomeGuard policy the claim is made under, as the agent reads it from the home policy lookup and gives it to the insured.
        claim_number: Verbatim class — the claim number exactly as printed on the insured's claim letters and on the claim's first-notice entry, copied character for character (verbatim).
        amount: Fixed-format class — the supplemental amount being accepted, in USD, 2 decimal places, positive, exactly as the agent quotes it.
        payee: Enum class — who the supplemental check is made out to: insured when payable to the named insured alone; insured_and_mortgagee when the mortgagee on file is named as co-payee with the insured.

    Returns:
        A dict rendered as text with: status ("accepted" on success); payment_entry_id (reference
        number of the supplemental payment entry); claim_number (the claim); amount (USD accepted and
        issued, 2 decimal places); payee (who the check is made out to); entry_date (YYYY-MM-DD date
        issued).
    """
    report = (ctx.find("home_claims", home_policy_id=home_policy_id, claim_number=claim_number,
                       event_type="home_claim_reported") or [{}])[0]
    made_out = {"insured": "insured", "insured_and_mortgagee": "insured_and_mortgagee"}.get(payee, payee)
    today = ctx.now()[:10]
    rid = ctx.make_id("hcs_", home_policy_id, claim_number, amount, payee)
    ctx.create("home_claims", rid, home_claim_entry_id=rid, home_policy_id=home_policy_id,
               customer_id=report.get("customer_id"), event_type="home_claim_payment",
               claim_number=claim_number, loss_date=report.get("loss_date"), entry_date=today,
               peril=report.get("peril"), coverage_part="other_structures", property_class="general",
               payment_type="supplemental", replacement_cost_amount=0.0, depreciation_amount=0.0,
               deductible_applied=0.0, incurred_amount=0.0, amount=round(float(amount), 2),
               payee=made_out, roof_age_years=0, denial_reason="none", source_entry_id="")
    return str({"status": "accepted", "payment_entry_id": rid, "claim_number": claim_number,
                "amount": round(float(amount), 2), "payee": made_out, "entry_date": today})


@tool(owner="agent", rw="write")
def settle_denied_water_damage_028e176f(ctx: ToolContext, home_policy_id: str, claim_number: str,
                                        source_entry_id: str, payment_type: str, depreciation_withheld: float,
                                        deductible_applied: float, amount: float, payee: str) -> str:
    """Issue the claim payment that replaces a repeated-seepage denial of dwelling water damage on a
    HomeGuard homeowners claim. One call records one new dwelling payment (general property class) on the
    named claim, carrying the replacement-cost value of the denial it replaces, the depreciation recognized,
    the deductible this payment absorbs, the amount paid and the payee; when the payment kind is an
    actual-cash-value initial payment and depreciation is recognized, that depreciation is withheld on the
    claim as recoverable depreciation in the same call. The claim's paid total rises by the amount and the
    insured sees a new dwelling payment on the claim file dated today.

    Args:
        home_policy_id: Id class — reference number of the HomeGuard policy the claim is made under, as returned by the home policy lookup for the verified customer.
        claim_number: Verbatim class — the claim number exactly as it appears on the claim's first-notice entry returned by the claim lookup, copied character for character (verbatim).
        source_entry_id: Id class — reference number of the repeated-seepage denial entry of the dwelling damage that this payment replaces, as returned by the claim lookup.
        payment_type: Enum class — the kind of dwelling payment: replacement_cost_full when the damage is paid at its full replacement-cost value with nothing withheld; acv_initial when it is paid at actual cash value with the recognized depreciation withheld for later recovery.
        depreciation_withheld: Fixed-format class — depreciation recognized on this payment and withheld for recovery, in USD, 2 decimal places, 0.00 when nothing is withheld.
        deductible_applied: Fixed-format class — part of the occurrence deductible absorbed by this payment, in USD, 2 decimal places, 0.00 when none.
        amount: Fixed-format class — amount paid on this dwelling payment, in USD, 2 decimal places, positive.
        payee: Enum class — who the payment is made out to: insured when the check is payable to the named insured alone; insured_and_mortgagee when the mortgagee on file is named as co-payee with the insured.

    Returns:
        A dict rendered as text with: status ("recorded" on success); payment_entry_id (reference
        number of the new dwelling payment entry); claim_number (the claim paid); payment_type (the kind
        recorded); amount (USD amount paid, 2 decimal places); deductible_applied (USD, 2 decimal places);
        depreciation_withheld (USD, 2 decimal places); payee (who the payment is made out to);
        holdback_entry_id (reference number of the recoverable depreciation withheld, or "" when nothing
        was withheld); entry_date (YYYY-MM-DD date of the payment).
    """
    denial = (ctx.find("home_claims", home_claim_entry_id=source_entry_id) or [{}])[0]
    report = (ctx.find("home_claims", home_policy_id=home_policy_id, claim_number=claim_number,
                       event_type="home_claim_reported") or [{}])[0]
    kind = {"replacement_cost_full": "replacement_cost_full", "acv_initial": "acv_initial"}.get(payment_type, payment_type)
    made_out = {"insured": "insured", "insured_and_mortgagee": "insured_and_mortgagee"}.get(payee, payee)
    today = ctx.now()[:10]
    withheld = round(float(depreciation_withheld), 2)
    rid = ctx.make_id("hwp_", home_policy_id, claim_number, source_entry_id, payment_type, depreciation_withheld,
                      deductible_applied, amount, payee)
    ctx.create("home_claims", rid, home_claim_entry_id=rid, home_policy_id=home_policy_id,
               customer_id=report.get("customer_id") or denial.get("customer_id"),
               event_type="home_claim_payment", claim_number=claim_number,
               loss_date=report.get("loss_date") or denial.get("loss_date"), entry_date=today,
               peril=report.get("peril") or denial.get("peril"), coverage_part="dwelling", property_class="general",
               payment_type=kind, replacement_cost_amount=round(float(denial.get("replacement_cost_amount") or 0), 2),
               depreciation_amount=withheld, deductible_applied=round(float(deductible_applied), 2),
               incurred_amount=0.0, amount=round(float(amount), 2), payee=made_out, roof_age_years=0,
               denial_reason="none", source_entry_id=source_entry_id)
    hold_id = ""
    if kind == "acv_initial" and withheld > 0:
        hold_id = ctx.make_id("hwh_", rid)
        ctx.create("home_claims", hold_id, home_claim_entry_id=hold_id, home_policy_id=home_policy_id,
                   customer_id=report.get("customer_id") or denial.get("customer_id"),
                   event_type="home_holdback_withheld", claim_number=claim_number,
                   loss_date=report.get("loss_date") or denial.get("loss_date"), entry_date=today,
                   peril=report.get("peril") or denial.get("peril"), coverage_part="dwelling",
                   property_class="general", payment_type="none", replacement_cost_amount=0.0,
                   depreciation_amount=0.0, deductible_applied=0.0, incurred_amount=0.0, amount=withheld,
                   payee="none", roof_age_years=0, denial_reason="none", source_entry_id=rid)
    return str({"status": "recorded", "payment_entry_id": rid, "claim_number": claim_number, "payment_type": kind,
                "amount": round(float(amount), 2), "deductible_applied": round(float(deductible_applied), 2),
                "depreciation_withheld": withheld, "payee": made_out, "holdback_entry_id": hold_id,
                "entry_date": today})


@tool(owner="agent", rw="write")
def settle_denied_mold_remediation_0cacd0ff(ctx: ToolContext, home_policy_id: str, claim_number: str,
                                            source_entry_id: str, payment_type: str, amount: float,
                                            payee: str) -> str:
    """Issue the mold (fungi, wet rot and bacteria) remediation payment that replaces a repeated-seepage
    denial of the mold remediation on a HomeGuard homeowners claim. One call records one new payment on the
    mold coverage part of the named claim, carrying the replacement-cost value of the denial it replaces,
    the amount paid and the payee; nothing is withheld and no deductible is recorded on it. The claim's paid
    total rises by the amount and the insured sees a new mold payment on the claim file dated today.

    Args:
        home_policy_id: Id class — reference number of the HomeGuard policy the claim is made under, as returned by the home policy lookup for the verified customer.
        claim_number: Verbatim class — the claim number exactly as it appears on the claim's first-notice entry returned by the claim lookup, copied character for character (verbatim).
        source_entry_id: Id class — reference number of the repeated-seepage denial entry of the mold remediation that this payment replaces, as returned by the claim lookup.
        payment_type: Enum class — the kind of mold payment: replacement_cost_full when the remediation value is at or below the policy's no-holdback amount; acv_initial when it is above it (remediation carries no depreciation, so nothing is ever withheld).
        amount: Fixed-format class — amount paid on the mold remediation, in USD, 2 decimal places, positive.
        payee: Enum class — who the payment is made out to: insured when the check is payable to the named insured alone; insured_and_mortgagee when the mortgagee on file is named as co-payee with the insured.

    Returns:
        A dict rendered as text with: status ("recorded" on success); payment_entry_id (reference
        number of the new mold payment entry); claim_number (the claim paid); payment_type (the kind
        recorded); amount (USD amount paid, 2 decimal places); payee (who the payment is made out to);
        entry_date (YYYY-MM-DD date of the payment).
    """
    denial = (ctx.find("home_claims", home_claim_entry_id=source_entry_id) or [{}])[0]
    report = (ctx.find("home_claims", home_policy_id=home_policy_id, claim_number=claim_number,
                       event_type="home_claim_reported") or [{}])[0]
    kind = {"replacement_cost_full": "replacement_cost_full", "acv_initial": "acv_initial"}.get(payment_type, payment_type)
    made_out = {"insured": "insured", "insured_and_mortgagee": "insured_and_mortgagee"}.get(payee, payee)
    today = ctx.now()[:10]
    rid = ctx.make_id("hmp_", home_policy_id, claim_number, source_entry_id, payment_type, amount, payee)
    ctx.create("home_claims", rid, home_claim_entry_id=rid, home_policy_id=home_policy_id,
               customer_id=report.get("customer_id") or denial.get("customer_id"),
               event_type="home_claim_payment", claim_number=claim_number,
               loss_date=report.get("loss_date") or denial.get("loss_date"), entry_date=today,
               peril=report.get("peril") or denial.get("peril"), coverage_part="mold", property_class="general",
               payment_type=kind, replacement_cost_amount=round(float(denial.get("replacement_cost_amount") or 0), 2),
               depreciation_amount=0.0, deductible_applied=0.0, incurred_amount=0.0,
               amount=round(float(amount), 2), payee=made_out, roof_age_years=0, denial_reason="none",
               source_entry_id=source_entry_id)
    return str({"status": "recorded", "payment_entry_id": rid, "claim_number": claim_number, "payment_type": kind,
                "amount": round(float(amount), 2), "payee": made_out, "entry_date": today})


@tool(owner="user", rw="write")
def accept_contents_supplemental_dc7651d7(ctx: ToolContext, home_policy_id: str, claim_number: str,
                                          amount: float, payee: str) -> str:
    """The named insured accepts a supplemental settlement on the personal property (contents: furniture,
    rugs, clothing, household goods) part of their own HomeGuard claim, and the acceptance issues it. One
    call records one supplemental payment on the personal property coverage part of the named claim for the
    accepted amount and payee, dated today; the claim's paid total rises by that amount and the insured sees
    the contents supplemental on their claim file.

    Args:
        home_policy_id: Id class — reference number of the HomeGuard policy the claim is made under, as the agent reads it from the home policy lookup and gives it to the insured.
        claim_number: Verbatim class — the claim number exactly as printed on the insured's claim letters and on the claim's first-notice entry, copied character for character (verbatim).
        amount: Fixed-format class — the contents supplemental amount being accepted, in USD, 2 decimal places, positive, exactly as the agent quotes it.
        payee: Enum class — who the supplemental check is made out to: insured when payable to the named insured alone; insured_and_mortgagee when the mortgagee on file is named as co-payee with the insured.

    Returns:
        A dict rendered as text with: status ("accepted" on success); payment_entry_id (reference number
        of the contents supplemental entry); claim_number (the claim); amount (USD accepted and issued, 2
        decimal places); payee (who the check is made out to); entry_date (YYYY-MM-DD date issued).
    """
    report = (ctx.find("home_claims", home_policy_id=home_policy_id, claim_number=claim_number,
                       event_type="home_claim_reported") or [{}])[0]
    made_out = {"insured": "insured", "insured_and_mortgagee": "insured_and_mortgagee"}.get(payee, payee)
    today = ctx.now()[:10]
    rid = ctx.make_id("hcc_", home_policy_id, claim_number, amount, payee)
    ctx.create("home_claims", rid, home_claim_entry_id=rid, home_policy_id=home_policy_id,
               customer_id=report.get("customer_id"), event_type="home_claim_payment",
               claim_number=claim_number, loss_date=report.get("loss_date"), entry_date=today,
               peril=report.get("peril"), coverage_part="personal_property", property_class="general",
               payment_type="supplemental", replacement_cost_amount=0.0, depreciation_amount=0.0,
               deductible_applied=0.0, incurred_amount=0.0, amount=round(float(amount), 2),
               payee=made_out, roof_age_years=0, denial_reason="none", source_entry_id="")
    return str({"status": "accepted", "payment_entry_id": rid, "claim_number": claim_number,
                "amount": round(float(amount), 2), "payee": made_out, "entry_date": today})

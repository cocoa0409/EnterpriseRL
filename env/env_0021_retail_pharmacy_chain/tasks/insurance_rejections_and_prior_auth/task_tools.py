"""Hidden task tools for the insurance_rejections_and_prior_auth difficulty (Prescription Insurance on File).

Each tool performs one atomic write on the coverage ledgers with the arguments exactly as given. None of them
checks eligibility, prior steps or amounts: every business judgement is made before the call.
"""

from erlbench import ToolContext, tool


@tool(owner="user", rw="write")
def file_coverage_appeal_f21a07b8(ctx: ToolContext, customer_id: str, coverage_id: str, prescription_id: str,
                                  source_pa_id: str, review_type: str, decision_window_days: int) -> str:
    """The patient files their own appeal with their prescription plan against one prior authorization denial.

    One call records one appeal on the patient's insurance plan on file: a new appeal entry dated today that names the
    denial being appealed, the prescription concerned, the review speed, and the date by which the plan must decide,
    which is today's filing date plus the decision window given. Nothing else on the plan changes. The patient can see
    afterwards that an appeal is on file with the plan and the date its decision is due.

    Args:
        customer_id: Id class — the patient reference number of the person filing, as returned by the patient profile lookup.
        coverage_id: Id class — the reference number of the insurance plan on file whose denial is appealed, as returned by the insurance plan lookup.
        prescription_id: Id class — the reference number of the prescription the denied request was for, as shown on the prior authorization entries returned by the prior authorization lookup.
        source_pa_id: Id class — the reference number of the denial entry being appealed, as returned by the prior authorization lookup.
        review_type: Enum class — the review speed of the appeal: standard when the appeal is reviewed on an ordinary clock; expedited when the appeal is reviewed on the urgent clock.
        decision_window_days: Fixed-format class — the appeal decision window as a whole number of calendar days, an integer of at least 1, counted with today's filing date as day 0; the tool records the decision due date as today's date plus this many days, in YYYY-MM-DD form.

    Returns:
        A dictionary printed as text with keys: status ("appeal_filed" on success), pa_id (reference number of the new
        appeal entry), source_pa_id (the denial appealed), review_type (standard or expedited, as recorded),
        event_date (filing date, YYYY-MM-DD) and decision_due_date (date the plan must decide by, YYYY-MM-DD).
    """
    def _days_from_civil(y: int, m: int, d: int) -> int:
        """Days since 1970-01-01 of a proleptic Gregorian date (pure integer arithmetic)."""
        y -= m <= 2
        era = (y if y >= 0 else y - 399) // 400
        yoe = y - era * 400
        doy = (153 * (m + (-3 if m > 2 else 9)) + 2) // 5 + d - 1
        doe = yoe * 365 + yoe // 4 - yoe // 100 + doy
        return era * 146097 + doe - 719468


    def _civil_from_days(z: int) -> tuple:
        """Proleptic Gregorian (year, month, day) of a day count since 1970-01-01."""
        z += 719468
        era = (z if z >= 0 else z - 146096) // 146097
        doe = z - era * 146097
        yoe = (doe - doe // 1460 + doe // 36524 - doe // 146096) // 365
        doy = doe - (365 * yoe + yoe // 4 - yoe // 100)
        mp = (5 * doy + 2) // 153
        d = doy - (153 * mp + 2) // 5 + 1
        m = mp + (3 if mp < 10 else -9)
        return yoe + era * 400 + (m <= 2), m, d


    def _add_days(iso_date: str, days: int) -> str:
        """'YYYY-MM-DD' plus a whole number of calendar days, as 'YYYY-MM-DD'."""
        y, m, d = (int(p) for p in iso_date[:10].split("-"))
        y2, m2, d2 = _civil_from_days(_days_from_civil(y, m, d) + int(days))
        return f"{y2:04d}-{m2:02d}-{d2:02d}"

    today = ctx.now()[:10]
    due = _add_days(today, int(decision_window_days))
    rid = ctx.make_id("pa_", customer_id, coverage_id, prescription_id, source_pa_id, review_type,
                      int(decision_window_days))
    ctx.create("coverage_prior_auths", rid, pa_id=rid, coverage_id=coverage_id, customer_id=customer_id,
               event_type="coverage_appeal_filed", event_date=today, prescription_id=prescription_id,
               source_pa_id=source_pa_id, review_type=review_type, decision_due_date=due)
    return str({"status": "appeal_filed", "pa_id": rid, "source_pa_id": source_pa_id, "review_type": review_type,
                "event_date": today, "decision_due_date": due})


@tool(owner="agent", rw="write")
def bill_continuation_supply_837ca024(ctx: ToolContext, customer_id: str, coverage_id: str, prescription_id: str,
                                      claim_id: str, fill_id: str, days_supply_billed: int) -> str:
    """Bill the plan for a continuation supply of a drug whose prior authorization renewal the plan denied.

    One call records one paid claim dated today on the patient's insurance plan on file for the prescription, with the
    continuation basis (emergency_pa_supply), no override code and the days supply given; the claim carries no patient
    pay. The new claim entry is keyed to the earlier paid claim and the dispensing entry it continues from. Nothing
    else changes. Afterwards the plan's claim history shows the paid continuation claim with its days supply.

    Args:
        customer_id: Id class — the patient reference number, as returned by the patient profile lookup.
        coverage_id: Id class — the reference number of the insurance plan on file the continuation is billed to, as returned by the insurance plan lookup.
        prescription_id: Id class — the reference number of the prescription the continuation is for, as returned by the prescription lookup.
        claim_id: Id class — the reference number of the plan's most recent claim paid for this prescription under its approval, which the continuation carries forward, as returned by the claim history lookup.
        fill_id: Id class — the reference number of the dispensing entry that most recent approved claim paid for, as returned by the dispensing history lookup.
        days_supply_billed: Fixed-format class — the continuation's days supply, in integer days (a whole number of calendar days, an integer of at least 1).

    Returns:
        A dictionary printed as text with keys: status ("claim_paid" on success), claim_id (reference number of the new
        claim entry), claim_basis (always emergency_pa_supply), event_date (date of service, YYYY-MM-DD) and
        days_supply_billed (the days supply recorded, integer days).
    """
    today = ctx.now()[:10]
    rid = ctx.make_id("clm_", customer_id, coverage_id, prescription_id, claim_id, fill_id, int(days_supply_billed))
    ctx.create("coverage_claims", rid, claim_id=rid, coverage_id=coverage_id, customer_id=customer_id,
               event_type="coverage_claim_paid", event_date=today, prescription_id=prescription_id,
               claim_basis="emergency_pa_supply", submission_clarification_code="none",
               days_supply_billed=int(days_supply_billed))
    return str({"status": "claim_paid", "claim_id": rid, "claim_basis": "emergency_pa_supply", "event_date": today,
                "days_supply_billed": int(days_supply_billed)})


@tool(owner="agent", rw="write")
def rebill_corrected_claim_b015fa67(ctx: ToolContext, customer_id: str, coverage_id: str, prescription_id: str,
                                    claim_id: str, fill_id: str, fill_number: int, service_date: str,
                                    days_supply_billed: int, quantity_billed: int, patient_pay_usd: float) -> str:
    """Re-bill, as a corrected claim, a fill whose earlier paid claim was reversed to correct a billing mistake.

    One call records one paid claim on the patient's insurance plan on file with the re-bill basis (retro_rebill), no
    override code, the original date of service, the fill number, days supply, quantity and patient pay given, and the
    reference number of the reversed claim it replaces. Nothing else changes. Afterwards the plan's claim history shows
    the corrected claim naming the claim it replaces, with its patient pay.

    Args:
        customer_id: Id class — the patient reference number, as returned by the patient profile lookup.
        coverage_id: Id class — the reference number of the insurance plan on file the corrected claim is billed to, as returned by the insurance plan lookup.
        prescription_id: Id class — the reference number of the prescription the corrected claim is for, as shown on the reversed claim returned by the claim history lookup.
        claim_id: Id class — the reference number of the earlier paid claim that was reversed for the billing correction and that this corrected claim replaces, as returned by the claim history lookup; it is recorded on the corrected claim.
        fill_id: Id class — the reference number of the dispensing entry the corrected claim pays for, as returned by the dispensing history lookup.
        fill_number: Fixed-format class — the fill number of that dispensing entry, an integer (0 for an original fill, 1 upward for refills), exactly as shown on the dispensing entry.
        service_date: Fixed-format class — the original date of service of that dispensing entry, in YYYY-MM-DD form, exactly as shown on the dispensing entry.
        days_supply_billed: Fixed-format class — the days supply the corrected claim bills, in integer days, the days supply the dispensing entry actually supplied.
        quantity_billed: Fixed-format class — the quantity the corrected claim bills, in integer dosage units, the quantity the dispensing entry actually dispensed.
        patient_pay_usd: Fixed-format class — the patient pay of the corrected claim in USD, a positive amount with 2 decimal places, rounded to the cent.

    Returns:
        A dictionary printed as text with keys: status ("claim_paid" on success), claim_id (reference number of the new
        corrected claim), source_claim_id (the reversed claim it replaces), claim_basis (always retro_rebill),
        event_date (date of service, YYYY-MM-DD) and patient_pay_usd (USD, 2 decimal places).
    """
    pay = round(float(patient_pay_usd), 2)
    rid = ctx.make_id("clm_", customer_id, coverage_id, prescription_id, claim_id, fill_id, int(fill_number),
                      service_date, int(days_supply_billed), int(quantity_billed), pay)
    ctx.create("coverage_claims", rid, claim_id=rid, coverage_id=coverage_id, customer_id=customer_id,
               event_type="coverage_claim_paid", event_date=service_date, prescription_id=prescription_id,
               fill_number=int(fill_number), claim_basis="retro_rebill", submission_clarification_code="none",
               days_supply_billed=int(days_supply_billed), quantity_billed=int(quantity_billed),
               patient_pay_usd=pay, source_claim_id=claim_id)
    return str({"status": "claim_paid", "claim_id": rid, "source_claim_id": claim_id, "claim_basis": "retro_rebill",
                "event_date": service_date, "patient_pay_usd": pay})


@tool(owner="user", rw="write")
def submit_cash_fill_rebill_483f3c39(ctx: ToolContext, customer_id: str, coverage_id: str, prescription_id: str,
                                     claim_id: str, fill_id: str, fill_number: int, service_date: str,
                                     days_supply_billed: int, quantity_billed: int, patient_pay_usd: float) -> str:
    """The patient submits a fill they paid for in cash to their insurance plan on file for re-billing.

    One call, made by the patient, records one paid claim on the patient's insurance plan on file with the re-bill basis
    (retro_rebill), no override code, the cash fill's original date of service, fill number, days supply and quantity,
    and the patient pay given. The new claim entry is keyed to the cash-paid dispensing entry and to the earlier claim
    that was turned down for it. Nothing else changes. Afterwards the plan's claim history shows the re-billed claim
    and its patient pay, which the patient can compare with the cash they paid.

    Args:
        customer_id: Id class — the patient reference number, as returned by the patient profile lookup.
        coverage_id: Id class — the reference number of the insurance plan on file the cash fill is re-billed to, as returned by the insurance plan lookup.
        prescription_id: Id class — the reference number of the prescription the cash fill was for, as returned by the prescription lookup.
        claim_id: Id class — the reference number of the earlier claim for this fill that was turned down, after which the patient paid cash, as returned by the claim history lookup.
        fill_id: Id class — the reference number of the cash-paid dispensing entry, as returned by the dispensing history lookup.
        fill_number: Fixed-format class — the fill number of that dispensing entry, an integer (0 for an original fill, 1 upward for refills), exactly as shown on the dispensing entry.
        service_date: Fixed-format class — the date that dispensing entry was dispensed, in YYYY-MM-DD form, exactly as shown on the dispensing entry.
        days_supply_billed: Fixed-format class — the days supply the re-billed claim bills, in integer days, the days supply the cash fill supplied.
        quantity_billed: Fixed-format class — the quantity the re-billed claim bills, in integer dosage units, the quantity the cash fill dispensed.
        patient_pay_usd: Fixed-format class — the patient pay of the re-billed claim in USD, a positive amount with 2 decimal places, rounded to the cent.

    Returns:
        A dictionary printed as text with keys: status ("claim_paid" on success), claim_id (reference number of the new
        re-billed claim), claim_basis (always retro_rebill), event_date (date of service, YYYY-MM-DD) and patient_pay_usd
        (USD, 2 decimal places).
    """
    pay = round(float(patient_pay_usd), 2)
    rid = ctx.make_id("clm_", customer_id, coverage_id, prescription_id, claim_id, fill_id, int(fill_number),
                      service_date, int(days_supply_billed), int(quantity_billed), pay)
    ctx.create("coverage_claims", rid, claim_id=rid, coverage_id=coverage_id, customer_id=customer_id,
               event_type="coverage_claim_paid", event_date=service_date, prescription_id=prescription_id,
               fill_number=int(fill_number), claim_basis="retro_rebill", submission_clarification_code="none",
               days_supply_billed=int(days_supply_billed), quantity_billed=int(quantity_billed),
               patient_pay_usd=pay)
    return str({"status": "claim_paid", "claim_id": rid, "claim_basis": "retro_rebill", "event_date": service_date,
                "patient_pay_usd": pay})

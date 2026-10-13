"""Hidden task tools of the employer_charge_protests difficulty (category: charge).

Each tool performs exactly one atomic business write on an employer's chargeable position and
returns a receipt. No tool judges eligibility, timeliness, relief grounds or amounts: the
amounts and choices it receives are worked out by the caller from the published rules and the
records, and the tool books them as given.
"""

from erlbench import ToolContext, tool


@tool(owner="user", rw="write")
def file_charge_protest_73ec7ae2(ctx: ToolContext, charge_position_id: str, customer_id: str,
                                 charge_quarter: str, protest_ground: str,
                                 protested_amount: float) -> str:
    """Lodge, in the employer's own name, a written protest of the benefit charges that a quarterly
    statement of benefit charges lists for one claimant. One call records the protest as a
    submission received today on the employer's chargeable position for that claim, stating the
    statement quarter protested, the ground raised and the amount protested in dollars, and moves
    the position from chargeable to protest pending with today's date as its protest date and the
    ground as its protest ground. Nothing is credited by this call. The employer can afterwards see
    the protest among its submissions with status received and the position shown as protest
    pending; the receipt below confirms the protest was lodged.

    Args:
        charge_position_id: Id class — the reference number of the employer's chargeable position on the claim whose statement is protested, as returned by the charge position lookup.
        customer_id: Id class — the employer's customer reference number that owns the position, as returned by the customer profile lookup.
        charge_quarter: Fixed-format class — the calendar quarter of the statement of benefit charges being protested, written as YYYY-Qn; empty unless a protest, for example the quarter shown on the statement; never empty for this call.
        protest_ground: Enum class — the single ground the protest raises: none means no ground is stated and is not used for a real protest; voluntary_quit_without_good_cause means the claimant left this employer voluntarily without good cause attributable to it; discharge_misconduct means this employer discharged the claimant for misconduct connected with the work; refused_suitable_work means the claimant refused suitable work this employer offered; continuing_part_time means this employer still employs the claimant part time as in the base period; agency_error means the benefits charged were paid in error by the agency; not_base_period_employer means this employer paid the claimant no base-period wages; wrong_wages means the base-period wages charged to this employer are wrong; overpayment_recovered means a recovered overpayment on the charged weeks has not been credited.
        protested_amount: Fixed-format class — the amount the protest states as protested, in US dollars, rounded to 2 decimal places, as a plain number without a currency sign.

    Returns:
        A text rendering of a dictionary with these fields: protest_reference (string, the reference number of the protest submission just recorded), charge_position_id (string, the position protested), charge_quarter (string, YYYY-Qn of the statement protested), protest_ground (string, the ground recorded), protested_amount (number, the dollars stated as protested, 2 decimal places), received_date (string, YYYY-MM-DD, today's date as the date received), position_status (string, always protest_pending once lodged). A receipt carrying a protest_reference means the protest was lodged.
    """
    today = ctx.now()[:10]
    rid = ctx.make_id("cpr_", charge_position_id, customer_id, charge_quarter, protest_ground,
                      protested_amount)
    ctx.create("charge_requests", rid, charge_request_id=rid, charge_position_id=charge_position_id,
               customer_id=customer_id, request_type="charge_protest", submitted_date=today,
               charge_quarter=charge_quarter, separation_reason_reported="not_reported",
               protest_ground=protest_ground, request_status="received", created_at=ctx.now())
    ctx.update("charge_positions", charge_position_id, status="protest_pending", protest_date=today,
               protest_ground=protest_ground)
    return str({"protest_reference": rid, "charge_position_id": charge_position_id,
                "charge_quarter": charge_quarter, "protest_ground": protest_ground,
                "protested_amount": round(float(protested_amount), 2), "received_date": today,
                "position_status": "protest_pending"})


@tool(owner="agent", rw="write")
def grant_charge_protest_0f56e95e(ctx: ToolContext, charge_position_id: str, customer_id: str,
                                  source_charge_id: str, relief_basis: str,
                                  relief_credit_amount: float) -> str:
    """Decide a pending protest of benefit charges in the employer's favour and book the relief
    credit it carries. One call moves the employer's chargeable position from protest pending to
    relieved with the relief basis given, and posts one credit with credit reason relief_granted,
    dated today and counted in today's calendar quarter, against the single posted benefit charge
    named, for the dollar amount given; the position's total charged falls by that amount. The
    employer sees the position as relieved and the credit on its next statement or reimbursement
    bill; the receipt below confirms the decision and the credit.

    Args:
        charge_position_id: Id class — the reference number of the chargeable position whose pending protest is decided, as returned by the charge position lookup.
        customer_id: Id class — the employer's customer reference number that owns the position, as returned by the customer profile lookup.
        source_charge_id: Id class — the reference number of the posted benefit charge the relief credit reduces, as returned by the charge ledger lookup.
        relief_basis: Enum class — the ground on which relief is granted: none means no relief and is not used for a granted protest; voluntary_quit_without_good_cause means the claimant left this employer voluntarily without good cause attributable to it; discharge_misconduct means this employer discharged the claimant for misconduct connected with the work; refused_suitable_work means the claimant refused suitable work this employer offered; continuing_part_time means this employer still employs the claimant part time as in the base period; agency_error means the benefits were paid in error by the agency; not_base_period_employer means this employer paid no base-period wages or the wages charged to it are wrong; appeal_decision means an appeal decision relieved the employer and is not used for a protest.
        relief_credit_amount: Fixed-format class — the dollar amount of the relief credit booked against the named charge, in US dollars, rounded to 2 decimal places, as a plain positive number without a currency sign.

    Returns:
        A text rendering of a dictionary with these fields: credit_reference (string, the reference number of the relief credit just posted), charge_position_id (string, the position decided), source_charge_id (string, the posted charge credited), relief_basis (string, the basis recorded), relief_credit_amount (number, the dollars credited, 2 decimal places), credit_quarter (string, YYYY-Qn, the calendar quarter in which the credit is posted), total_charged_after (number, the position's total charged once the credit is booked, 2 decimal places), position_status (string, always relieved once decided). A receipt carrying a credit_reference means the protest was granted and the credit posted.
    """
    today = ctx.now()[:10]
    quarter = today[:4] + "-Q" + str((int(today[5:7]) - 1) // 3 + 1)
    amount = round(float(relief_credit_amount), 2)
    rid = ctx.make_id("crg_", charge_position_id, customer_id, source_charge_id, relief_basis,
                      relief_credit_amount)
    ctx.create("charge_ledger", rid, charge_entry_id=rid, charge_position_id=charge_position_id,
               customer_id=customer_id, event_type="charge_credit_reversed", entry_date=today,
               source_payment_id="", source_payment_amount=0.00, week_ending_date="",
               charge_quarter=quarter, amount=amount, source_charge_id=source_charge_id,
               credit_reason="relief_granted", statement_mailed_date="", protest_due_date="")
    rows = ctx.find("charge_positions", charge_position_id=charge_position_id)
    before = float((rows[0].get("total_charged") if rows else 0) or 0)
    after = round(before - amount, 2)
    ctx.update("charge_positions", charge_position_id, status="relieved", relief_basis=relief_basis,
               total_charged=after)
    return str({"credit_reference": rid, "charge_position_id": charge_position_id,
                "source_charge_id": source_charge_id, "relief_basis": relief_basis,
                "relief_credit_amount": amount, "credit_quarter": quarter,
                "total_charged_after": after, "position_status": "relieved"})


@tool(owner="user", rw="write")
def submit_separation_response_153a3a70(ctx: ToolContext, charge_position_id: str, customer_id: str,
                                        separation_reason_reported: str, response_timeliness: str,
                                        disputed_charge_amount: float) -> str:
    """Lodge, in the employer's own name, its separation response to a notice of claim. One call
    records the response as a submission received today on the employer's chargeable position for
    that claim, stating the separation reason the employer reports and the dollar amount of the
    benefits already charged that the response disputes, and moves the position from noticed to
    responded with today's date as its response date, the reported separation reason and the
    timeliness given. Nothing is credited by this call. The employer can afterwards see the
    response among its submissions with status received and the position shown as responded; the
    receipt below confirms the response was lodged.

    Args:
        charge_position_id: Id class — the reference number of the employer's chargeable position on the claim named in the notice of claim, as returned by the charge position lookup.
        customer_id: Id class — the employer's customer reference number that owns the position, as returned by the customer profile lookup.
        separation_reason_reported: Enum class — the separation reason the employer reports: not_reported means the employer states no reason and is not used for a real response; lack_of_work means the claimant was laid off for lack of work; voluntary_quit means the claimant left this employer of the claimant's own accord; discharge_misconduct means this employer discharged the claimant for misconduct connected with the work; discharge_other means this employer discharged the claimant for a reason other than misconduct; still_employed_part_time means this employer still employs the claimant part time; refused_offer_of_work means the claimant refused an offer of work from this employer.
        response_timeliness: Enum class — how the response stands against its due date: pending means no response has been received and is not used here; timely means the response is received no later than the response due date; late_good_cause means it is received after the due date with good cause shown; late means it is received after the due date without good cause; none means no response came at all and is not used here.
        disputed_charge_amount: Fixed-format class — the amount of benefits already charged that the response disputes, in US dollars, rounded to 2 decimal places, as a plain number without a currency sign; 0.00 when nothing is disputed.

    Returns:
        A text rendering of a dictionary with these fields: response_reference (string, the reference number of the response submission just recorded), charge_position_id (string, the position answered), separation_reason_reported (string, the reason recorded), response_timeliness (string, the timeliness recorded), disputed_charge_amount (number, the dollars stated as disputed, 2 decimal places), received_date (string, YYYY-MM-DD, today's date as the date received), position_status (string, always responded once lodged). A receipt carrying a response_reference means the response was lodged.
    """
    today = ctx.now()[:10]
    rid = ctx.make_id("csr_", charge_position_id, customer_id, separation_reason_reported,
                      response_timeliness, disputed_charge_amount)
    ctx.create("charge_requests", rid, charge_request_id=rid, charge_position_id=charge_position_id,
               customer_id=customer_id, request_type="separation_response", submitted_date=today,
               charge_quarter="", separation_reason_reported=separation_reason_reported,
               protest_ground="none", request_status="received", created_at=ctx.now())
    ctx.update("charge_positions", charge_position_id, status="responded", response_date=today,
               response_timeliness=response_timeliness,
               separation_reason_reported=separation_reason_reported)
    return str({"response_reference": rid, "charge_position_id": charge_position_id,
                "separation_reason_reported": separation_reason_reported,
                "response_timeliness": response_timeliness,
                "disputed_charge_amount": round(float(disputed_charge_amount), 2),
                "received_date": today, "position_status": "responded"})


@tool(owner="agent", rw="write")
def determine_charge_relief_e2b9af19(ctx: ToolContext, charge_position_id: str, customer_id: str,
                                     source_charge_id: str, relief_basis: str,
                                     relief_credit_amount: float) -> str:
    """Record the determination on an employer's separation response that grants the employer
    relief from benefit charges, and book the relief credit it carries. One call moves the
    employer's chargeable position from responded to relieved with the relief basis given, and
    posts one credit with credit reason relief_granted, dated today and counted in today's calendar
    quarter, against the single posted benefit charge named, for the dollar amount given; the
    position's total charged falls by that amount. The employer sees the position as relieved and
    the credit on its next statement; the receipt below confirms the determination and the credit.

    Args:
        charge_position_id: Id class — the reference number of the chargeable position whose separation response is determined, as returned by the charge position lookup.
        customer_id: Id class — the employer's customer reference number that owns the position, as returned by the customer profile lookup.
        source_charge_id: Id class — the reference number of the posted benefit charge the relief credit reduces, as returned by the charge ledger lookup.
        relief_basis: Enum class — the ground on which relief is granted: none means no relief and is not used for a grant; voluntary_quit_without_good_cause means the claimant left this employer voluntarily without good cause attributable to it; discharge_misconduct means this employer discharged the claimant for misconduct connected with the work; refused_suitable_work means the claimant refused suitable work this employer offered; continuing_part_time means this employer still employs the claimant part time as in the base period; agency_error means the benefits were paid in error by the agency; not_base_period_employer means this employer paid no base-period wages or the wages charged to it are wrong; appeal_decision means an appeal decision relieved the employer and is not used for a determination on a response.
        relief_credit_amount: Fixed-format class — the dollar amount of the relief credit booked against the named charge, in US dollars, rounded to 2 decimal places, as a plain positive number without a currency sign.

    Returns:
        A text rendering of a dictionary with these fields: credit_reference (string, the reference number of the relief credit just posted), charge_position_id (string, the position determined), source_charge_id (string, the posted charge credited), relief_basis (string, the basis recorded), relief_credit_amount (number, the dollars credited, 2 decimal places), credit_quarter (string, YYYY-Qn, the calendar quarter in which the credit is posted), total_charged_after (number, the position's total charged once the credit is booked, 2 decimal places), position_status (string, always relieved once determined). A receipt carrying a credit_reference means relief was granted and the credit posted.
    """
    today = ctx.now()[:10]
    quarter = today[:4] + "-Q" + str((int(today[5:7]) - 1) // 3 + 1)
    amount = round(float(relief_credit_amount), 2)
    rid = ctx.make_id("crd_", charge_position_id, customer_id, source_charge_id, relief_basis,
                      relief_credit_amount)
    ctx.create("charge_ledger", rid, charge_entry_id=rid, charge_position_id=charge_position_id,
               customer_id=customer_id, event_type="charge_credit_reversed", entry_date=today,
               source_payment_id="", source_payment_amount=0.00, week_ending_date="",
               charge_quarter=quarter, amount=amount, source_charge_id=source_charge_id,
               credit_reason="relief_granted", statement_mailed_date="", protest_due_date="")
    rows = ctx.find("charge_positions", charge_position_id=charge_position_id)
    before = float((rows[0].get("total_charged") if rows else 0) or 0)
    after = round(before - amount, 2)
    ctx.update("charge_positions", charge_position_id, status="relieved", relief_basis=relief_basis,
               total_charged=after)
    return str({"credit_reference": rid, "charge_position_id": charge_position_id,
                "source_charge_id": source_charge_id, "relief_basis": relief_basis,
                "relief_credit_amount": amount, "credit_quarter": quarter,
                "total_charged_after": after, "position_status": "relieved"})

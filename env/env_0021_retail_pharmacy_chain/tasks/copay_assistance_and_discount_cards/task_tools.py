"""Hidden task tools of the copay_assistance_and_discount_cards difficulty (Kestrel Pharmacy).

Each tool performs one atomic write on the Savings & Copay Assistance Programs records and is
reached only through the unlock/call meta tools; its name is registered in
copay.extended.yaml (extended_policies[].target_tool).
"""

from erlbench import ToolContext, tool


@tool(owner="agent", rw="write")
def apply_club_cash_price_c625f91d(ctx: ToolContext, enrollment_id: str, fill_id: str,
                                    usual_price_usd: float, patient_pay_after_usd: float) -> str:
    """Record the Kestrel Rx Savings Club price on one cash prescription fill of the member.

    The pharmacy agent uses this to price a fill that is not billed to insurance at the club
    price. One call books one club-price entry on the member's savings program: it names the
    fill priced, its prescription and days supply, the usual and customary price, the price the
    member pays and the savings off the usual price (usual price less the price paid, to the
    cent). The entry then shows in the member's program activity. The tool records the figures
    it is given and does not work out the price itself.

    Args:
        enrollment_id: Id class — reference number of the member's Kestrel Rx Savings Club enrollment, as returned by the program-enrollment lookup for the patient.
        fill_id: Id class — reference number of the dispensing entry being priced, as returned by the dispensing-history lookup for the prescription.
        usual_price_usd: Fixed-format class — the usual and customary cash price of that fill in USD, 2 decimal places, copied from the pay the dispensing history shows on that cash fill; rounded half up to the cent when stored.
        patient_pay_after_usd: Fixed-format class — the club price the member pays for the fill in USD, 2 decimal places, rounded half up to the cent when stored.

    Returns:
        A dictionary rendered as text with: status ("recorded" on success), activity_id (reference
        number of the new club-price entry), fill_id (the fill priced), usual_price_usd (USD,
        2 decimals), patient_pay_after_usd (price the member pays, USD, 2 decimals) and
        savings_usd (usual price less the price paid, USD, 2 decimals). An "Error:" text means no
        entry was recorded.
    """
    fills = ctx.find("rx_fills", fill_id=fill_id)
    if not fills:
        return f"Error: no dispensing entry {fill_id}."
    fill = fills[0]
    rows = ctx.find("copay_enrollments", enrollment_id=enrollment_id)
    if not rows:
        return f"Error: no program enrollment {enrollment_id}."
    usual = round(float(usual_price_usd), 2)
    after = round(float(patient_pay_after_usd), 2)
    savings = round(usual - after, 2)
    rid = ctx.make_id("cpa_", enrollment_id, fill_id, usual_price_usd, patient_pay_after_usd)
    ctx.create("copay_activity", rid, activity_id=rid, enrollment_id=enrollment_id,
               customer_id=rows[0].get("customer_id"), event_type="copay_discount_applied",
               event_date=ctx.now()[:10], prescription_id=fill.get("prescription_id"), fill_id=fill_id,
               days_supply=fill.get("days_supply_dispensed"), usual_price_usd=usual,
               amount_usd=savings, patient_pay_after_usd=after)
    return str({"status": "recorded", "activity_id": rid, "fill_id": fill_id, "usual_price_usd": usual,
                "patient_pay_after_usd": after, "savings_usd": savings})


@tool(owner="user", rw="write")
def pay_club_renewal_fee_425b5cbe(ctx: ToolContext, enrollment_id: str, amount_usd: float) -> str:
    """Pay, as the member, the renewal fee of a Kestrel Rx Savings Club membership for its current term.

    The member runs this themselves to pay the renewal fee that the automatic renewal could not
    collect. One call books one renewal-fee payment on the membership for the term it is now in
    (the term start shown on the membership) and adds the amount paid to the membership fees the
    member has paid. The member sees the payment on the membership's fee history and a receipt
    with its reference number.

    Args:
        enrollment_id: Id class — reference number of the member's Kestrel Rx Savings Club enrollment, as the pharmacy agent reads it out from the program-enrollment lookup.
        amount_usd: Fixed-format class — the renewal fee the member pays in USD, 2 decimal places, as the pharmacy agent states it; rounded half up to the cent when stored.

    Returns:
        A dictionary rendered as text with: status ("paid" on success), activity_id (reference
        number of the fee payment), term_start (YYYY-MM-DD, first day of the term the fee pays
        for), amount_usd (fee paid, USD, 2 decimals) and membership_fees_net_usd (membership fees
        paid less fees refunded after this payment, USD, 2 decimals). An "Error:" text means
        nothing was paid.
    """
    rows = ctx.find("copay_enrollments", enrollment_id=enrollment_id)
    if not rows:
        return f"Error: no program enrollment {enrollment_id}."
    enr = rows[0]
    amount = round(float(amount_usd), 2)
    term_start = enr.get("benefit_period_start")
    rid = ctx.make_id("cpf_", enrollment_id, term_start, "annual_renewal", amount_usd)
    ctx.create("copay_activity", rid, activity_id=rid, enrollment_id=enrollment_id,
               customer_id=enr.get("customer_id"), event_type="copay_membership_fee_charged",
               event_date=ctx.now()[:10], fee_type="annual_renewal", benefit_period_start=term_start,
               amount_usd=amount)
    net = round(float(enr.get("membership_fees_net_usd") or 0) + amount, 2)
    ctx.update("copay_enrollments", enrollment_id, membership_fees_net_usd=net)
    return str({"status": "paid", "activity_id": rid, "term_start": term_start, "amount_usd": amount,
                "membership_fees_net_usd": net})


@tool(owner="agent", rw="write")
def refund_club_membership_fee_7fa4dd89(ctx: ToolContext, enrollment_id: str, source_activity_id: str,
                                        refund_reason: str, amount_usd: float) -> str:
    """Refund one membership fee charge of a Kestrel Rx Savings Club membership to the member.

    The pharmacy agent uses this to pay back a fee charge that is owed back to the member. One call
    books one fee refund against the named fee charge, with the reason and the amount returned,
    and takes the amount off the membership fees the member has paid. The member sees the refund
    in the membership's fee history.

    Args:
        enrollment_id: Id class — reference number of the member's Kestrel Rx Savings Club enrollment, as returned by the program-enrollment lookup for the patient.
        source_activity_id: Id class — reference number of the fee charge being refunded, as returned by the program-activity lookup for the enrollment.
        refund_reason: Enum class — why the fee charge is refunded: within_refund_window when the charge is refunded because the member asked for it back inside the fee refund window; duplicate_charge when the charge is a second fee charge booked for a membership term that already carried one.
        amount_usd: Fixed-format class — the amount refunded to the member in USD, 2 decimal places, rounded half up to the cent when stored.

    Returns:
        A dictionary rendered as text with: status ("refunded" on success), activity_id (reference
        number of the refund entry), source_activity_id (the fee charge refunded), refund_reason
        (as given), amount_usd (amount refunded, USD, 2 decimals) and membership_fees_net_usd
        (membership fees paid less fees refunded after this refund, USD, 2 decimals). An "Error:"
        text means nothing was refunded.
    """
    rows = ctx.find("copay_enrollments", enrollment_id=enrollment_id)
    if not rows:
        return f"Error: no program enrollment {enrollment_id}."
    enr = rows[0]
    amount = round(float(amount_usd), 2)
    rid = ctx.make_id("cpr_", enrollment_id, source_activity_id, refund_reason, amount_usd)
    ctx.create("copay_activity", rid, activity_id=rid, enrollment_id=enrollment_id,
               customer_id=enr.get("customer_id"), event_type="copay_membership_fee_refunded",
               event_date=ctx.now()[:10], source_activity_id=source_activity_id,
               refund_reason=refund_reason, amount_usd=amount)
    net = round(float(enr.get("membership_fees_net_usd") or 0) - amount, 2)
    ctx.update("copay_enrollments", enrollment_id, membership_fees_net_usd=net)
    return str({"status": "refunded", "activity_id": rid, "source_activity_id": source_activity_id,
                "refund_reason": refund_reason, "amount_usd": amount, "membership_fees_net_usd": net})


@tool(owner="user", rw="write")
def submit_copay_card_reimbursement_c6a4b4a1(ctx: ToolContext, enrollment_id: str, fill_id: str,
                                             claim_id: str, amount_usd: float) -> str:
    """Submit, as the patient, a reimbursement request on a manufacturer copay card for a fill already paid.

    The patient runs this themselves to claim back, from their Manufacturer Copay Card, part of the
    patient pay they already paid in full on one prescription fill. One call books one card benefit on
    that fill and its insurance claim: it records the patient pay before the card, the amount the card
    pays back to the patient and the patient pay left after it, and takes the amount out of the card's
    benefit dollars. The patient sees the reimbursement on the card's activity and a receipt.

    Args:
        enrollment_id: Id class — reference number of the patient's Manufacturer Copay Card enrollment, as the pharmacy agent reads it out from the program-enrollment lookup.
        fill_id: Id class — reference number of the dispensing entry the patient paid in full, as the pharmacy agent reads it out from the dispensing-history lookup.
        claim_id: Id class — reference number of the paid insurance claim of that fill, as the pharmacy agent reads it out from the claim-history lookup.
        amount_usd: Fixed-format class — the amount the card pays back to the patient in USD, 2 decimal places, as the pharmacy agent states it; rounded half up to the cent when stored.

    Returns:
        A dictionary rendered as text with: status ("submitted" on success), activity_id (reference
        number of the card benefit entry), fill_id, claim_id, patient_pay_before_usd (the claim's
        patient pay, USD, 2 decimals), amount_usd (amount paid back, USD, 2 decimals),
        patient_pay_after_usd (patient pay left after the card, USD, 2 decimals) and
        benefit_remaining_usd (card dollars left in the current benefit period, USD, 2 decimals). An
        "Error:" text means nothing was submitted.
    """
    enr_rows = ctx.find("copay_enrollments", enrollment_id=enrollment_id)
    fill_rows = ctx.find("rx_fills", fill_id=fill_id)
    claim_rows = ctx.find("coverage_claims", claim_id=claim_id)
    if not enr_rows or not fill_rows or not claim_rows:
        return "Error: unknown enrollment, dispensing entry or claim reference."
    enr, fill, claim = enr_rows[0], fill_rows[0], claim_rows[0]
    amount = round(float(amount_usd), 2)
    before = round(float(claim.get("patient_pay_usd") or 0), 2)
    after = round(before - amount, 2)
    rid = ctx.make_id("cpb_", enrollment_id, fill_id, claim_id, amount_usd)
    ctx.create("copay_activity", rid, activity_id=rid, enrollment_id=enrollment_id,
               customer_id=enr.get("customer_id"), event_type="copay_benefit_applied",
               event_date=ctx.now()[:10], prescription_id=fill.get("prescription_id"), fill_id=fill_id,
               claim_id=claim_id, days_supply=fill.get("days_supply_dispensed"),
               patient_pay_before_usd=before, amount_usd=amount, patient_pay_after_usd=after)
    remaining = round(float(enr.get("benefit_remaining_usd") or 0) - amount, 2)
    ctx.update("copay_enrollments", enrollment_id, benefit_remaining_usd=remaining)
    return str({"status": "submitted", "activity_id": rid, "fill_id": fill_id, "claim_id": claim_id,
                "patient_pay_before_usd": before, "amount_usd": amount, "patient_pay_after_usd": after,
                "benefit_remaining_usd": remaining})


@tool(owner="agent", rw="write")
def apply_copay_card_benefit_5e8b0a9f(ctx: ToolContext, enrollment_id: str, fill_id: str,
                                      claim_id: str, amount_usd: float) -> str:
    """Apply a Manufacturer Copay Card benefit to the patient pay of a fill waiting at the counter.

    The pharmacy agent uses this to bill the patient's copay card on the patient pay of a paid
    insurance claim for a fill that the patient has not picked up and paid yet. One call books one card benefit on that fill and its paid
    insurance claim: it records the patient pay before the card, the amount the card pays and the
    patient pay left for the patient at pickup, and takes the amount out of the card's benefit
    dollars. The benefit then shows on the card's activity.

    Args:
        enrollment_id: Id class — reference number of the patient's Manufacturer Copay Card enrollment, as returned by the program-enrollment lookup for the patient.
        fill_id: Id class — reference number of the dispensing entry waiting for pickup, as returned by the dispensing-history lookup for the prescription.
        claim_id: Id class — reference number of the paid insurance claim of that fill, as returned by the claim-history lookup for the prescription.
        amount_usd: Fixed-format class — the amount the card pays on the fill in USD, 2 decimal places, rounded half up to the cent when stored.

    Returns:
        A dictionary rendered as text with: status ("applied" on success), activity_id (reference
        number of the card benefit entry), fill_id, claim_id, patient_pay_before_usd (the claim's
        patient pay, USD, 2 decimals), amount_usd (amount the card pays, USD, 2 decimals),
        patient_pay_after_usd (what the patient pays at pickup, USD, 2 decimals) and
        benefit_remaining_usd (card dollars left in the current benefit period, USD, 2 decimals). An
        "Error:" text means nothing was applied.
    """
    enr_rows = ctx.find("copay_enrollments", enrollment_id=enrollment_id)
    fill_rows = ctx.find("rx_fills", fill_id=fill_id)
    claim_rows = ctx.find("coverage_claims", claim_id=claim_id)
    if not enr_rows or not fill_rows or not claim_rows:
        return "Error: unknown enrollment, dispensing entry or claim reference."
    enr, fill, claim = enr_rows[0], fill_rows[0], claim_rows[0]
    amount = round(float(amount_usd), 2)
    before = round(float(claim.get("patient_pay_usd") or 0), 2)
    after = round(before - amount, 2)
    rid = ctx.make_id("cpc_", enrollment_id, fill_id, claim_id, amount_usd)
    ctx.create("copay_activity", rid, activity_id=rid, enrollment_id=enrollment_id,
               customer_id=enr.get("customer_id"), event_type="copay_benefit_applied",
               event_date=ctx.now()[:10], prescription_id=fill.get("prescription_id"), fill_id=fill_id,
               claim_id=claim_id, days_supply=fill.get("days_supply_dispensed"),
               patient_pay_before_usd=before, amount_usd=amount, patient_pay_after_usd=after)
    remaining = round(float(enr.get("benefit_remaining_usd") or 0) - amount, 2)
    ctx.update("copay_enrollments", enrollment_id, benefit_remaining_usd=remaining)
    return str({"status": "applied", "activity_id": rid, "fill_id": fill_id, "claim_id": claim_id,
                "patient_pay_before_usd": before, "amount_usd": amount, "patient_pay_after_usd": after,
                "benefit_remaining_usd": remaining})


@tool(owner="agent", rw="write")
def close_program_benefit_period_88a9291d(ctx: ToolContext, enrollment_id: str, amount_usd: float) -> str:
    """Book the closing entry of the current benefit period of a copay assistance program.

    The pharmacy agent uses this when a program's benefit period has ended. One call books one closing
    entry for the period the enrollment currently shows (its current period start), recording the
    benefit dollars that lapse, and takes that amount out of the program's benefit dollars; whatever
    is not lapsed stays on the program. The closing entry then shows on the program's activity.

    Args:
        enrollment_id: Id class — reference number of the program enrollment whose period is closed, as returned by the program-enrollment lookup for the patient.
        amount_usd: Fixed-format class — the benefit dollars that lapse at the close, in USD, 2 decimal places, rounded half up to the cent when stored.

    Returns:
        A dictionary rendered as text with: status ("closed" on success), activity_id (reference
        number of the closing entry), period_start (YYYY-MM-DD, first day of the period closed),
        amount_usd (dollars lapsed, USD, 2 decimals) and benefit_remaining_usd (program dollars left
        standing after the close, USD, 2 decimals). An "Error:" text means nothing was booked.
    """
    rows = ctx.find("copay_enrollments", enrollment_id=enrollment_id)
    if not rows:
        return f"Error: no program enrollment {enrollment_id}."
    enr = rows[0]
    amount = round(float(amount_usd), 2)
    start = enr.get("benefit_period_start")
    rid = ctx.make_id("cpx_", enrollment_id, start, amount_usd)
    ctx.create("copay_activity", rid, activity_id=rid, enrollment_id=enrollment_id,
               customer_id=enr.get("customer_id"), event_type="copay_benefit_period_closed",
               event_date=ctx.now()[:10], benefit_period_start=start, amount_usd=amount)
    remaining = round(float(enr.get("benefit_remaining_usd") or 0) - amount, 2)
    ctx.update("copay_enrollments", enrollment_id, benefit_remaining_usd=remaining)
    return str({"status": "closed", "activity_id": rid, "period_start": start, "amount_usd": amount,
                "benefit_remaining_usd": remaining})


@tool(owner="agent", rw="write")
def open_program_benefit_period_c8eb05d0(ctx: ToolContext, enrollment_id: str, benefit_period_start: str,
                                         benefit_period_end: str, amount_usd: float) -> str:
    """Open a new benefit period on a copay assistance program and credit its benefit dollars.

    The pharmacy agent uses this to start the program's next benefit period. One call books one
    period-opening entry that credits the new period's benefit dollars, moves the enrollment's
    current period to the dates given, and adds the credit to the program's benefit dollars. The new
    period and the dollars then show on the program.

    Args:
        enrollment_id: Id class — reference number of the program enrollment, as returned by the program-enrollment lookup for the patient.
        benefit_period_start: Fixed-format class — first day of the new benefit period, as YYYY-MM-DD (calendar date, no time zone).
        benefit_period_end: Fixed-format class — last day of the new benefit period, as YYYY-MM-DD (calendar date, no time zone).
        amount_usd: Fixed-format class — the benefit dollars credited to the new period in USD, 2 decimal places, rounded half up to the cent when stored.

    Returns:
        A dictionary rendered as text with: status ("opened" on success), activity_id (reference
        number of the opening entry), benefit_period_start and benefit_period_end (YYYY-MM-DD),
        amount_usd (dollars credited, USD, 2 decimals) and benefit_remaining_usd (program dollars
        available after the credit, USD, 2 decimals). An "Error:" text means nothing was opened.
    """
    rows = ctx.find("copay_enrollments", enrollment_id=enrollment_id)
    if not rows:
        return f"Error: no program enrollment {enrollment_id}."
    enr = rows[0]
    amount = round(float(amount_usd), 2)
    rid = ctx.make_id("cpo_", enrollment_id, benefit_period_start, benefit_period_end, amount_usd)
    ctx.create("copay_activity", rid, activity_id=rid, enrollment_id=enrollment_id,
               customer_id=enr.get("customer_id"), event_type="copay_benefit_period_opened",
               event_date=ctx.now()[:10], benefit_period_start=benefit_period_start, amount_usd=amount)
    remaining = round(float(enr.get("benefit_remaining_usd") or 0) + amount, 2)
    ctx.update("copay_enrollments", enrollment_id, benefit_period_start=benefit_period_start,
               benefit_period_end=benefit_period_end, benefit_remaining_usd=remaining)
    return str({"status": "opened", "activity_id": rid, "benefit_period_start": benefit_period_start,
                "benefit_period_end": benefit_period_end, "amount_usd": amount,
                "benefit_remaining_usd": remaining})

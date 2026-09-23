"""Hidden task tools for the Keyturn host protection and claims desk.

Every function here performs ONE atomic write on the host protection records. None of them
judges eligibility, checks a window, reconciles history or works out an amount: the desk
agent reads the enrolment, the claim records, the workshop and recovery history and the
marketplace's published terms, works the figure out, and passes it in.
"""

from erlbench import ToolContext, tool


@tool(owner="user", rw="write")
def lodge_damage_report_2cc23be4(ctx: ToolContext, enrollment_id: str, booking_id: str,
                                 damage_category: str, document_count: int) -> str:
    """Lodge a host's own report of damage to their protected vehicle onto the damage report
    register. The host performs this themselves: it puts a fresh report on the register for the
    named trip, marks it routed for the protection team with the stated number of photographs and
    documents attached to it, and stamps it with the moment it was lodged. The host can afterwards
    see the report and its reference on the register against that trip; the returned reference is
    what confirms the report was taken.

    Args:
        enrollment_id: Id class — the reference number of the host protection enrolment covering
            the damaged vehicle, read from the enrolment record retrieved for this host.
        booking_id: Id class — the reference number of the trip booking the damage is reported
            against, read from the trip record retrieved for that vehicle.
        damage_category: Enum class — the kind of loss the host is reporting, one of:
            exterior_body — dents, scrapes or paint damage to the outside of the vehicle;
            interior — damage to upholstery, trim or fittings inside the cabin;
            glass — a chipped, cracked or shattered windscreen, window or mirror glass;
            tyres_wheels — damage to tyres, rims or wheels;
            mechanical — a mechanical breakdown or driveline failure arising on the trip;
            theft_total_loss — the vehicle was stolen or is damaged beyond economic repair;
            missing_equipment — charge cables, seats, racks or other equipment removed from the vehicle;
            third_party_property — damage the guest caused to property belonging to someone else.
        document_count: Fixed-format class — how many photographs and supporting documents are
            attached to this report, as a whole number of items, counted as one per file lodged;
            zero is accepted and means nothing was attached.

    Returns:
        A confirmation line in plain text carrying the reference number the report was filed under
        on the register, the trip it was lodged against and the number of items attached. Receiving
        that line means the report now stands on the register and is routed to the protection team;
        no other output is produced.
    """
    rows = ctx.find("hostplan_enrollments", enrollment_id=enrollment_id)
    customer_id = rows[0].get("customer_id") if rows else ""
    rid = ctx.make_id("dmr_", enrollment_id, booking_id, damage_category, document_count)
    ctx.create("hostplan_claim_intake", rid, claim_intake_id=rid, customer_id=customer_id,
               enrollment_id=enrollment_id, booking_id=booking_id,
               damage_category=damage_category, intake_status="routed",
               reported_at=ctx.now(), evidence_count=int(document_count))
    return (f"Damage report {rid} lodged on the register for trip {booking_id} "
            f"with {int(document_count)} item(s) attached.")


@tool(owner="agent", rw="write")
def open_loss_claim_e6dccf7d(ctx: ToolContext, enrollment_id: str, booking_id: str,
                             damage_category: str, loss_date: str, settlement_reference: str,
                             claim_opened_amount: float) -> str:
    """Open a damage claim on a host protection enrolment for a loss that happened on a named
    trip. One call writes a new claim record against the enrolment carrying the day the loss
    happened, the kind of damage, the estimate reference the host quotes and the amount the claim
    is opened at, and stamps it with today's date and an undetermined liability finding. The host
    can afterwards see the claim and its reference standing against that trip, and the returned
    reference is what confirms the claim was opened.

    Args:
        enrollment_id: Id class — the reference number of the host protection enrolment the claim
            is made under, read from the enrolment record retrieved for this host.
        booking_id: Id class — the reference number of the trip booking the loss happened on, read
            from the trip record retrieved for that vehicle.
        damage_category: Enum class — the kind of loss being claimed, one of:
            exterior_body — dents, scrapes or paint damage to the outside of the vehicle;
            interior — damage to upholstery, trim or fittings inside the cabin;
            glass — a chipped, cracked or shattered windscreen, window or mirror glass;
            tyres_wheels — damage to tyres, rims or wheels;
            mechanical — a mechanical breakdown or driveline failure arising on the trip;
            theft_total_loss — the vehicle was stolen or is damaged beyond economic repair;
            missing_equipment — charge cables, seats, racks or other equipment removed from the vehicle;
            third_party_property — damage the guest caused to property belonging to someone else.
        loss_date: Fixed-format class — the calendar day the damage occurred, written as YYYY-MM-DD
            in the marketplace's own local dating with no time part; it is never left blank.
        settlement_reference: Verbatim class — the repair estimate, invoice or report reference the
            host reads out for this loss, copied character for character from what the host says,
            keeping the original wording, digits, letter case and punctuation, with nothing
            translated, normalised, summarised, added or removed (verbatim).
        claim_opened_amount: Fixed-format class — the amount the claim is opened at, in USD, 2
            decimal places, rounded half-up to the cent at the moment the claim is opened.

    Returns:
        A confirmation line in plain text carrying the reference number of the new claim record,
        the trip it belongs to and the amount it was opened at in USD to the cent. Receiving that
        line means the claim now stands on the enrolment; no other output is produced.
    """
    rows = ctx.find("hostplan_enrollments", enrollment_id=enrollment_id)
    customer_id = rows[0].get("customer_id") if rows else ""
    rid = ctx.make_id("clm_", enrollment_id, booking_id, damage_category, loss_date,
                      settlement_reference, claim_opened_amount)
    ctx.create("hostplan_claims", rid, claim_id=rid, enrollment_id=enrollment_id,
               customer_id=customer_id, booking_id=booking_id,
               event_type="hostplan_claim_filed", claim_date=ctx.now()[:10],
               loss_date=loss_date, damage_category=damage_category,
               claim_amount=round(float(claim_opened_amount), 2),
               settlement_reference=settlement_reference,
               liability_finding="undetermined", decision_channel="claims_specialist")
    return (f"Claim {rid} opened on enrolment {enrollment_id} for trip {booking_id} "
            f"at {round(float(claim_opened_amount), 2)} USD.")


@tool(owner="agent", rw="write")
def record_loss_appraisal_09001cb5(ctx: ToolContext, enrollment_id: str, source_claim_id: str,
                                   booking_id: str, damage_category: str, appraisal_channel: str,
                                   liability_finding: str, accepted_loss_amount: float) -> str:
    """Record the appraisal of an open damage claim and book what the marketplace accepts on it as
    money owed to the host. One call writes an appraisal record against the claim carrying how the
    loss was valued and who was found responsible, and raises the enrolment's balance owed to the
    host by the accepted figure. The host can afterwards see the appraisal against the claim and
    the higher amount owed to them on the enrolment; the returned reference is what confirms the
    appraisal was recorded.

    Args:
        enrollment_id: Id class — the reference number of the host protection enrolment the claim
            is made under, read from the enrolment record retrieved for this host.
        source_claim_id: Id class — the reference number of the open claim record this appraisal
            values, read from the claim records standing on that enrolment.
        booking_id: Id class — the reference number of the trip booking the loss happened on, read
            from the claim record being appraised.
        damage_category: Enum class — the kind of loss being appraised, one of:
            exterior_body — dents, scrapes or paint damage to the outside of the vehicle;
            interior — damage to upholstery, trim or fittings inside the cabin;
            glass — a chipped, cracked or shattered windscreen, window or mirror glass;
            tyres_wheels — damage to tyres, rims or wheels;
            mechanical — a mechanical breakdown or driveline failure arising on the trip;
            theft_total_loss — the vehicle was stolen or is damaged beyond economic repair;
            missing_equipment — charge cables, seats, racks or other equipment removed from the vehicle;
            third_party_property — damage the guest caused to property belonging to someone else.
        appraisal_channel: Enum class — how the loss was valued, one of:
            photo_estimate — valued from the photographs lodged with the report alone;
            in_person_adjuster — valued by an adjuster who inspected the vehicle in person;
            repair_shop_invoice — valued from the repair work a shop has invoiced on the vehicle;
            total_loss_valuation — valued as a write-off against the marketplace's valuation of the vehicle.
        liability_finding: Enum class — who the marketplace found responsible for the loss, one of:
            undetermined — responsibility has not been settled;
            guest_at_fault — the guest who had the vehicle caused the loss;
            host_at_fault — the host caused or contributed to the loss;
            third_party — someone outside the trip caused the loss;
            no_fault — the loss happened with nobody at fault.
        accepted_loss_amount: Fixed-format class — the amount the marketplace accepts on this loss
            and books as owed to the host, in USD, 2 decimal places, signed, passed as a positive
            figure rounded half-up to the cent.

    Returns:
        A confirmation line in plain text carrying the reference number of the appraisal record,
        the claim it values, the accepted amount in USD to the cent and the enrolment's new balance
        owed to the host. Receiving that line means the appraisal stands and the money is booked as
        owed; no other output is produced.
    """
    rows = ctx.find("hostplan_enrollments", enrollment_id=enrollment_id)
    customer_id = rows[0].get("customer_id") if rows else ""
    owed = round(float(rows[0].get("reimbursement_balance_due") or 0) +
                 round(float(accepted_loss_amount), 2), 2) if rows else 0.0
    rid = ctx.make_id("apr_", enrollment_id, source_claim_id, booking_id, damage_category,
                      appraisal_channel, liability_finding, accepted_loss_amount)
    ctx.create("hostplan_claims", rid, claim_id=rid, enrollment_id=enrollment_id,
               customer_id=customer_id, booking_id=booking_id, source_claim_id=source_claim_id,
               event_type="hostplan_claim_appraised", claim_date=ctx.now()[:10],
               damage_category=damage_category,
               appraisal_amount=round(float(accepted_loss_amount), 2),
               amount_delta=round(float(accepted_loss_amount), 2),
               liability_finding=liability_finding, appraisal_channel=appraisal_channel,
               decision_channel="senior_adjuster")
    if rows:
        ctx.update("hostplan_enrollments", enrollment_id, reimbursement_balance_due=owed)
    return (f"Appraisal {rid} recorded on claim {source_claim_id}: "
            f"{round(float(accepted_loss_amount), 2)} USD accepted, enrolment now owed {owed} USD.")


@tool(owner="agent", rw="write")
def raise_host_share_c19fa66d(ctx: ToolContext, enrollment_id: str, source_claim_id: str,
                              booking_id: str, damage_category: str, liability_finding: str,
                              host_share_amount: float) -> str:
    """Raise the host's own share of an accepted loss against their protection enrolment. One call
    writes a host-share record against the named claim and increases the amount the host owes on
    the enrolment by that figure. The host can afterwards see the charge against the claim and the
    higher amount owed by them on the enrolment; the returned reference is what confirms the charge
    was raised.

    Args:
        enrollment_id: Id class — the reference number of the host protection enrolment the share
            is raised on, read from the enrolment record retrieved for this host.
        source_claim_id: Id class — the reference number of the accepted claim record the share
            belongs to, read from the claim records standing on that enrolment.
        booking_id: Id class — the reference number of the trip booking the loss happened on, read
            from the claim record the share belongs to.
        damage_category: Enum class — the kind of loss the share belongs to, one of:
            exterior_body — dents, scrapes or paint damage to the outside of the vehicle;
            interior — damage to upholstery, trim or fittings inside the cabin;
            glass — a chipped, cracked or shattered windscreen, window or mirror glass;
            tyres_wheels — damage to tyres, rims or wheels;
            mechanical — a mechanical breakdown or driveline failure arising on the trip;
            theft_total_loss — the vehicle was stolen or is damaged beyond economic repair;
            missing_equipment — charge cables, seats, racks or other equipment removed from the vehicle;
            third_party_property — damage the guest caused to property belonging to someone else.
        liability_finding: Enum class — who the marketplace found responsible for the loss, one of:
            undetermined — responsibility has not been settled;
            guest_at_fault — the guest who had the vehicle caused the loss;
            host_at_fault — the host caused or contributed to the loss;
            third_party — someone outside the trip caused the loss;
            no_fault — the loss happened with nobody at fault.
        host_share_amount: Fixed-format class — the amount the host carries on this loss, in USD, 2
            decimal places, signed, passed as a positive figure rounded half-up to the cent.

    Returns:
        A confirmation line in plain text carrying the reference number of the host-share record,
        the claim it belongs to, the amount raised in USD to the cent and the enrolment's new
        amount owed by the host. Receiving that line means the share now stands against the host;
        no other output is produced.
    """
    rows = ctx.find("hostplan_enrollments", enrollment_id=enrollment_id)
    customer_id = rows[0].get("customer_id") if rows else ""
    owing = round(float(rows[0].get("liability_balance_due") or 0) +
                  round(float(host_share_amount), 2), 2) if rows else 0.0
    rid = ctx.make_id("ded_", enrollment_id, source_claim_id, booking_id, damage_category,
                      liability_finding, host_share_amount)
    ctx.create("hostplan_claims", rid, claim_id=rid, enrollment_id=enrollment_id,
               customer_id=customer_id, booking_id=booking_id, source_claim_id=source_claim_id,
               event_type="hostplan_deductible_charged", claim_date=ctx.now()[:10],
               damage_category=damage_category,
               amount_delta=round(float(host_share_amount), 2),
               liability_finding=liability_finding, decision_channel="claims_specialist")
    if rows:
        ctx.update("hostplan_enrollments", enrollment_id, liability_balance_due=owing)
    return (f"Host share {rid} raised on claim {source_claim_id}: "
            f"{round(float(host_share_amount), 2)} USD, enrolment now owes {owing} USD.")


@tool(owner="agent", rw="write")
def restore_protection_cover_3adbf459(ctx: ToolContext, enrollment_id: str,
                                      restoration_charge_amount: float) -> str:
    """Put a host protection enrolment whose cover has fallen away back into force. One call moves
    the enrolment back to active, clears the ground that was recorded against it, sets the day
    cover starts running again to today, and books the charge for restoring it to what the host
    owes on the enrolment. The host can afterwards see the enrolment live again from today with
    that charge added to what they owe; the returned confirmation line is what shows the cover is
    back in force.

    Args:
        enrollment_id: Id class — the reference number of the host protection enrolment being put
            back into force, read from the enrolment record retrieved for this host.
        restoration_charge_amount: Fixed-format class — the charge for putting the cover back into
            force, in USD, 2 decimal places, rounded half-up to the cent; zero is accepted and
            means nothing is charged for the restoration.

    Returns:
        A confirmation line in plain text carrying the enrolment reference, the day cover starts
        running again as YYYY-MM-DD, the charge booked in USD to the cent and the enrolment's new
        amount owed by the host. Receiving that line means the enrolment is active again; no other
        output is produced.
    """
    rows = ctx.find("hostplan_enrollments", enrollment_id=enrollment_id)
    owing = round(float(rows[0].get("liability_balance_due") or 0) +
                  round(float(restoration_charge_amount), 2), 2) if rows else 0.0
    if rows:
        ctx.update("hostplan_enrollments", enrollment_id, status="active",
                   suspension_reason="none", effective_date=ctx.now()[:10],
                   liability_balance_due=owing)
    return (f"Enrolment {enrollment_id} restored to active from {ctx.now()[:10]} with a charge of "
            f"{round(float(restoration_charge_amount), 2)} USD; the host now owes {owing} USD.")


@tool(owner="user", rw="write")
def withdraw_own_claim_4cdcc89b(ctx: ToolContext, enrollment_id: str, source_claim_id: str,
                                booking_id: str, damage_category: str,
                                released_amount: float) -> str:
    """Take a host's own claim back off the enrolment. The host performs this themselves: it writes
    a withdrawal record against the named claim and releases the money that was standing booked as
    owed to the host on it, reducing the enrolment's balance owed to the host by that figure. The
    host can afterwards see the claim closed by their withdrawal and the lower amount owed to them;
    the returned reference is what confirms the withdrawal was taken.

    Args:
        enrollment_id: Id class — the reference number of the host protection enrolment the claim
            was made under, read from the enrolment record retrieved for this host.
        source_claim_id: Id class — the reference number of the claim record being withdrawn, read
            from the claim records standing on that enrolment.
        booking_id: Id class — the reference number of the trip booking the withdrawn claim was
            made against, read from that claim record.
        damage_category: Enum class — the kind of loss the withdrawn claim covered, one of:
            exterior_body — dents, scrapes or paint damage to the outside of the vehicle;
            interior — damage to upholstery, trim or fittings inside the cabin;
            glass — a chipped, cracked or shattered windscreen, window or mirror glass;
            tyres_wheels — damage to tyres, rims or wheels;
            mechanical — a mechanical breakdown or driveline failure arising on the trip;
            theft_total_loss — the vehicle was stolen or is damaged beyond economic repair;
            missing_equipment — charge cables, seats, racks or other equipment removed from the vehicle;
            third_party_property — damage the guest caused to property belonging to someone else.
        released_amount: Fixed-format class — the money released back from what was booked as owed
            to the host on the withdrawn claim, in USD, 2 decimal places, signed, passed as a
            positive figure rounded half-up to the cent.

    Returns:
        A confirmation line in plain text carrying the reference number of the withdrawal record,
        the claim it closes, the amount released in USD to the cent and the enrolment's new balance
        owed to the host. Receiving that line means the claim is withdrawn; no other output is
        produced.
    """
    rows = ctx.find("hostplan_enrollments", enrollment_id=enrollment_id)
    customer_id = rows[0].get("customer_id") if rows else ""
    owed = round(float(rows[0].get("reimbursement_balance_due") or 0) -
                 round(float(released_amount), 2), 2) if rows else 0.0
    rid = ctx.make_id("wdr_", enrollment_id, source_claim_id, booking_id, damage_category,
                      released_amount)
    ctx.create("hostplan_claims", rid, claim_id=rid, enrollment_id=enrollment_id,
               customer_id=customer_id, booking_id=booking_id, source_claim_id=source_claim_id,
               event_type="hostplan_claim_withdrawn", claim_date=ctx.now()[:10],
               damage_category=damage_category,
               amount_delta=-round(float(released_amount), 2),
               decision_channel="claims_specialist")
    if rows:
        ctx.update("hostplan_enrollments", enrollment_id, reimbursement_balance_due=owed)
    return (f"Withdrawal {rid} recorded on claim {source_claim_id}: "
            f"{round(float(released_amount), 2)} USD released, enrolment now owed {owed} USD.")


@tool(owner="agent", rw="write")
def record_repair_supplement_1a6beabe(ctx: ToolContext, enrollment_id: str, source_claim_id: str,
                                      booking_id: str, damage_category: str,
                                      appraisal_channel: str, settlement_reference: str,
                                      supplement_amount: float) -> str:
    """Add further repair cost found after an appraisal to a claim that has already been accepted.
    One call writes a supplement record against the named appraised claim carrying the further cost
    accepted, how it was evidenced and the supplementary invoice reference, and raises the
    enrolment's balance owed to the host by that figure. The host can afterwards see the supplement
    against the claim and the higher amount owed to them; the returned reference is what confirms
    the supplement was accepted.

    Args:
        enrollment_id: Id class — the reference number of the host protection enrolment the claim
            is made under, read from the enrolment record retrieved for this host.
        source_claim_id: Id class — the reference number of the appraised claim record the further
            cost is added to, read from the claim records standing on that enrolment.
        booking_id: Id class — the reference number of the trip booking the loss happened on, read
            from the claim record the supplement is added to.
        damage_category: Enum class — the kind of loss the further cost belongs to, one of:
            exterior_body — dents, scrapes or paint damage to the outside of the vehicle;
            interior — damage to upholstery, trim or fittings inside the cabin;
            glass — a chipped, cracked or shattered windscreen, window or mirror glass;
            tyres_wheels — damage to tyres, rims or wheels;
            mechanical — a mechanical breakdown or driveline failure arising on the trip;
            theft_total_loss — the vehicle was stolen or is damaged beyond economic repair;
            missing_equipment — charge cables, seats, racks or other equipment removed from the vehicle;
            third_party_property — damage the guest caused to property belonging to someone else.
        appraisal_channel: Enum class — how the further cost was evidenced, one of:
            photo_estimate — evidenced from further photographs alone;
            in_person_adjuster — evidenced by an adjuster who re-inspected the vehicle;
            repair_shop_invoice — evidenced by a supplementary invoice from the repairing shop;
            total_loss_valuation — evidenced by a fresh write-off valuation of the vehicle.
        settlement_reference: Verbatim class — the supplementary invoice reference the host reads
            out, copied character for character from what the host says, keeping the original
            wording, digits, letter case and punctuation, with nothing translated, normalised,
            summarised, added or removed (verbatim).
        supplement_amount: Fixed-format class — the further cost accepted and added to what is owed
            to the host, in USD, 2 decimal places, signed, passed as a positive figure rounded
            half-up to the cent.

    Returns:
        A confirmation line in plain text carrying the reference number of the supplement record,
        the claim it adds to, the further cost accepted in USD to the cent and the enrolment's new
        balance owed to the host. Receiving that line means the supplement stands and the money is
        booked as owed; no other output is produced.
    """
    rows = ctx.find("hostplan_enrollments", enrollment_id=enrollment_id)
    customer_id = rows[0].get("customer_id") if rows else ""
    owed = round(float(rows[0].get("reimbursement_balance_due") or 0) +
                 round(float(supplement_amount), 2), 2) if rows else 0.0
    rid = ctx.make_id("sup_", enrollment_id, source_claim_id, booking_id, damage_category,
                      appraisal_channel, settlement_reference, supplement_amount)
    ctx.create("hostplan_claims", rid, claim_id=rid, enrollment_id=enrollment_id,
               customer_id=customer_id, booking_id=booking_id, source_claim_id=source_claim_id,
               event_type="hostplan_supplement_added", claim_date=ctx.now()[:10],
               damage_category=damage_category,
               appraisal_amount=round(float(supplement_amount), 2),
               amount_delta=round(float(supplement_amount), 2),
               appraisal_channel=appraisal_channel,
               settlement_reference=settlement_reference, decision_channel="senior_adjuster")
    if rows:
        ctx.update("hostplan_enrollments", enrollment_id, reimbursement_balance_due=owed)
    return (f"Supplement {rid} accepted on claim {source_claim_id}: "
            f"{round(float(supplement_amount), 2)} USD added, enrolment now owed {owed} USD.")


@tool(owner="agent", rw="write")
def release_claim_payment_a6ef5b4d(ctx: ToolContext, enrollment_id: str, source_claim_id: str,
                                   payout_account_id: str, released_payment_amount: float) -> str:
    """Release money the marketplace owes a host on an accepted claim and send it to their payout
    account. One call writes a payment record against the named accepted claim carrying the sum
    released and the reference the host can quote for it, and reduces the enrolment's balance owed
    to the host by that sum. The host can afterwards see the payment against the claim, the lower
    amount owed to them and the reference to quote to their bank; the returned reference is what
    confirms the payment was released.

    Args:
        enrollment_id: Id class — the reference number of the host protection enrolment the claim is
            made under, read from the enrolment record retrieved for this host.
        source_claim_id: Id class — the reference number of the accepted claim record the money is
            released against, read from the claim records standing on that enrolment.
        payout_account_id: Id class — the reference number of the host payout account the money is
            sent to, read from the payout account record retrieved for this host.
        released_payment_amount: Fixed-format class — the sum released to the host now, in USD, 2
            decimal places, signed, passed as a positive figure rounded half-up to the cent; a
            payment may be for part of what is owed, and zero is not released.

    Returns:
        A confirmation line in plain text carrying the reference number of the payment record, the
        claim it is released against, the payout account it was sent to, the sum released in USD to
        the cent and the enrolment's new balance owed to the host. Receiving that line means the
        money has left on that reference; no other output is produced.
    """
    rows = ctx.find("hostplan_enrollments", enrollment_id=enrollment_id)
    customer_id = rows[0].get("customer_id") if rows else ""
    booking = ""
    claim_rows = ctx.find("hostplan_claims", claim_id=source_claim_id)
    if claim_rows:
        booking = claim_rows[0].get("booking_id") or ""
    owed = round(float(rows[0].get("reimbursement_balance_due") or 0) -
                 round(float(released_payment_amount), 2), 2) if rows else 0.0
    rid = ctx.make_id("pay_", enrollment_id, source_claim_id, payout_account_id,
                      released_payment_amount)
    ctx.create("hostplan_claims", rid, claim_id=rid, enrollment_id=enrollment_id,
               customer_id=customer_id, booking_id=booking, source_claim_id=source_claim_id,
               event_type="hostplan_reimbursement_paid", claim_date=ctx.now()[:10],
               amount_delta=-round(float(released_payment_amount), 2),
               settlement_reference=rid, decision_channel="claims_specialist")
    if rows:
        ctx.update("hostplan_enrollments", enrollment_id, reimbursement_balance_due=owed)
    return (f"Payment {rid} released on claim {source_claim_id} to payout account "
            f"{payout_account_id}: {round(float(released_payment_amount), 2)} USD sent, "
            f"enrolment now owed {owed} USD.")

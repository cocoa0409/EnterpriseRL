"""Hidden task tools for the travel protection desk (category: care).

Each function performs one atomic write on a travel protection record. The tools are not
listed anywhere: a policy names one as its target_tool, and it is reached through the
unlock/call meta tools. None of them judges eligibility, aggregates history or works out a
policy figure; the caller works the figure out from the published terms and the records and
passes it in.
"""

from erlbench import ToolContext, tool

@tool(owner="agent", rw="write")
def book_benefit_recovery_c1be7196(ctx: ToolContext, care_policy_id: str, source_claim_id: str,
                                   claim_reference: str, claim_type: str,
                                   recovered_amount_usd: float) -> str:
    """Book money recovered from a liable third party against a settlement already paid under a
    travel protection policy, so that the benefit the settlement consumed is restored on that
    policy. One call adds a recovery row to the policy's claim record: it carries the recovered
    money as a negative movement of the benefit account, marks the claim recovered, stamps the
    date it was received and points at the payment it partly reverses. The decision already made
    on the claim is untouched and nothing is returned to or taken from the traveller; what the
    policyholder sees afterwards is that this much of the benefit stands available again on the
    policy for the rest of its term.

    Args:
        care_policy_id: Id class — the reference number of the travel protection policy whose
            benefit is restored, read from the policy record found for the traveller.
        source_claim_id: Id class — the reference number of the payment row this recovery
            partly reverses, read from the claim record of that policy.
        claim_reference: Verbatim class — the reference the insurer quoted for the claim the
            money was recovered on, copied character for character from the claim record, keeping
            the original wording, digits and punctuation, with no translation, normalisation,
            summarisation, addition or deletion (verbatim).
        claim_type: Enum class — the benefit the restored money was paid under; exactly one of the
            eleven heads below and never any other word: trip_cancellation applies where the journey was called off before it began;
            trip_interruption where a journey already begun was cut short or broken into;
            medical_emergency where the traveller was treated for illness or injury away from
            home; dental_emergency where the treatment was dental; evacuation where the
            traveller had to be moved or repatriated for medical reasons; baggage_delay where
            checked baggage reached the traveller late; baggage_loss where baggage or an article
            in it was lost or damaged outright; travel_delay where the traveller themselves was
            held up in transit; missed_connection where a late arrival caused an onward service
            to be missed; rental_damage where a hired vehicle was damaged; cancel_for_any_reason
            where the journey was called off for a reason no other head covers.
        recovered_amount_usd: Fixed-format class — the money recovered from the third party for
            that settled loss, given as a positive USD amount with 2 decimal places, rounded half
            up to the cent; the row itself carries it as a negative movement of the benefit
            account.

    Returns:
        A plain-text confirmation naming the reference number minted for the recovery row, the
        policy it was booked against and the recovered amount as it now stands on the claim
        record. Receiving that confirmation is what indicates the recovery has been booked and
        the benefit restored; nothing else is returned.
    """
    rid = ctx.make_id("care_clm_", care_policy_id, source_claim_id, claim_reference,
                      claim_type, recovered_amount_usd)
    ctx.create("care_claims", rid, care_claim_id=rid, care_policy_id=care_policy_id,
               event_type="care_claim_recovery", claim_reference=claim_reference,
               claim_type=claim_type,
               paid_amount_usd=-round(float(recovered_amount_usd), 2),
               decided_date=ctx.now()[:10], posted_at=ctx.now(), claim_status="recovered",
               source_claim_id=source_claim_id, reason_code="third_party_recovery")
    return (f"Recovery {rid} booked against payment {source_claim_id} on policy {care_policy_id}: "
            f"{round(float(recovered_amount_usd), 2):.2f} USD restored to the benefit.")


@tool(owner="user", rw="write")
def file_benefit_claim_dde0dff5(ctx: ToolContext, care_policy_id: str, customer_id: str,
                                claim_reference: str, claim_type: str, claimed_amount_usd: float,
                                incident_date: str, loss_location_country: str,
                                insured_sequence: int, supporting_document_reference: str) -> str:
    """File a claim in your own name against one benefit of your travel protection policy. One
    call opens a new claim on that policy's claim record: it states the benefit claimed against,
    the money claimed before any limit or deductible, the date the incident happened, the country
    it happened in, which insured traveller it belongs to and the evidence supplied, and it opens
    the claim as filed with today as its filing date. Nothing is assessed or paid by this step and
    no money moves; what you can see afterwards is the claim standing open on your policy with the
    reference the insurer quoted, ready for the insurer to decide.

    Args:
        care_policy_id: Id class — the reference number of the travel protection policy the claim
            is made under, read from the policy record.
        customer_id: Id class — the traveller reference number of the policyholder the claim
            belongs to, read from the traveller profile.
        claim_reference: Verbatim class — the reference the insurer quoted for this incident,
            copied character for character as the policyholder states it, keeping the original
            wording, digits and punctuation, with no translation, normalisation, summarisation,
            addition or deletion (verbatim).
        claim_type: Enum class — the benefit this claim is made against; exactly one of the
            eleven heads below and never any other word: trip_cancellation applies where the journey was called off before it began;
            trip_interruption where a journey already begun was cut short or broken into;
            medical_emergency where the traveller was treated for illness or injury away from
            home; dental_emergency where the treatment was dental; evacuation where the
            traveller had to be moved or repatriated for medical reasons; baggage_delay where
            checked baggage reached the traveller late; baggage_loss where baggage or an article
            in it was lost or damaged outright; travel_delay where the traveller themselves was
            held up in transit; missed_connection where a late arrival caused an onward service
            to be missed; rental_damage where a hired vehicle was damaged; cancel_for_any_reason
            where the journey was called off for a reason no other head covers.
        claimed_amount_usd: Fixed-format class — the money claimed before any limit or deductible
            is applied, given as a USD amount with 2 decimal places, rounded half up to the cent.
        incident_date: Fixed-format class — the calendar date YYYY-MM-DD on which the incident
            being claimed for happened.
        loss_location_country: Fixed-format class — where the incident happened, written as an
            ISO 3166-1 alpha-2 country code, uppercase.
        insured_sequence: Fixed-format class — which insured traveller on the certificate the
            claim belongs to, as a whole number starting at 1 in the order they are named.
        supporting_document_reference: Verbatim class — the reference of the evidence supplied
            with the claim, copied character for character as it is stated, keeping the original
            wording, digits and punctuation, with no translation, normalisation, summarisation,
            addition or deletion (verbatim).

    Returns:
        A plain-text confirmation naming the reference number minted for the new claim row, the
        policy it was opened on, the benefit claimed against and the amount claimed. Receiving
        that confirmation is what indicates the claim now stands filed; nothing else is returned.
    """
    rid = ctx.make_id("care_clm_", care_policy_id, claim_reference, claim_type,
                      claimed_amount_usd, incident_date)
    ctx.create("care_claims", rid, care_claim_id=rid, care_policy_id=care_policy_id,
               customer_id=customer_id, event_type="care_claim_file",
               claim_reference=claim_reference, claim_type=claim_type,
               claimed_amount_usd=round(float(claimed_amount_usd), 2), paid_amount_usd=0.0,
               deductible_applied_usd=0.0, incident_date=incident_date,
               filed_date=ctx.now()[:10], posted_at=ctx.now(), claim_status="filed",
               insured_sequence=int(insured_sequence),
               loss_location_country=loss_location_country,
               supporting_document_reference=supporting_document_reference,
               reason_code="insured_claim")
    return (f"Claim {rid} filed on policy {care_policy_id} under {claim_reference} for "
            f"{claim_type}: {round(float(claimed_amount_usd), 2):.2f} USD claimed.")


@tool(owner="agent", rw="write")
def release_claim_payment_9edda418(ctx: ToolContext, care_policy_id: str, source_claim_id: str,
                                   claim_reference: str, claim_type: str, paid_amount_usd: float,
                                   deductible_applied_usd: float) -> str:
    """Pay a decided travel protection claim to the policyholder. One call adds a payment row to
    the policy's claim record: it carries the money actually paid, the deductible withheld from
    it, the date the payment was authorised, the benefit it was paid under and the decision it
    settles, and it marks the claim paid. The money paid consumes that much of the policy's
    benefit for the rest of its term. What the policyholder sees afterwards is the settled amount
    standing paid against their claim reference, in the currency the premium was paid in.

    Args:
        care_policy_id: Id class — the reference number of the travel protection policy the
            payment is made under, read from the policy record found for the traveller.
        source_claim_id: Id class — the reference number of the decision row this payment
            settles, read from the claim record of that policy.
        claim_reference: Verbatim class — the reference the insurer quoted for the claim being
            paid, copied character for character from the claim record, keeping the original
            wording, digits and punctuation, with no translation, normalisation, summarisation,
            addition or deletion (verbatim).
        claim_type: Enum class — the benefit the payment is made under; exactly one of the
            eleven heads below and never any other word: trip_cancellation applies where the journey was called off before it began;
            trip_interruption where a journey already begun was cut short or broken into;
            medical_emergency where the traveller was treated for illness or injury away from
            home; dental_emergency where the treatment was dental; evacuation where the
            traveller had to be moved or repatriated for medical reasons; baggage_delay where
            checked baggage reached the traveller late; baggage_loss where baggage or an article
            in it was lost or damaged outright; travel_delay where the traveller themselves was
            held up in transit; missed_connection where a late arrival caused an onward service
            to be missed; rental_damage where a hired vehicle was damaged; cancel_for_any_reason
            where the journey was called off for a reason no other head covers.
        paid_amount_usd: Fixed-format class — the money actually paid to the policyholder on this
            settlement, given as a USD amount with 2 decimal places, rounded half up to the cent.
        deductible_applied_usd: Fixed-format class — the deductible withheld from this
            settlement, given as a USD amount with 2 decimal places, rounded half up to the cent;
            0.00 where nothing is withheld.

    Returns:
        A plain-text confirmation naming the reference number minted for the payment row, the
        policy and claim reference it settles, the amount paid and the deductible withheld.
        Receiving that confirmation is what indicates the payment has been made and the benefit
        consumed; nothing else is returned.
    """
    rid = ctx.make_id("care_clm_", care_policy_id, source_claim_id, claim_reference,
                      claim_type, paid_amount_usd, deductible_applied_usd)
    ctx.create("care_claims", rid, care_claim_id=rid, care_policy_id=care_policy_id,
               event_type="care_claim_payout", claim_reference=claim_reference,
               claim_type=claim_type, paid_amount_usd=round(float(paid_amount_usd), 2),
               deductible_applied_usd=round(float(deductible_applied_usd), 2),
               decided_date=ctx.now()[:10], posted_at=ctx.now(), claim_status="paid",
               source_claim_id=source_claim_id, reason_code="insurer_decision")
    return (f"Payment {rid} released on policy {care_policy_id} under {claim_reference}: "
            f"{round(float(paid_amount_usd), 2):.2f} USD paid, "
            f"{round(float(deductible_applied_usd), 2):.2f} USD deductible withheld.")


@tool(owner="agent", rw="write")
def correct_declared_trip_cost_b35383d2(ctx: ToolContext, care_policy_id: str, care_request_id: str,
                                        corrected_trip_cost_usd: float) -> str:
    """Correct the trip cost declared on a travel protection certificate to the figure the underwriting
    desk has approved for it. One call replaces the declared trip cost held on that policy record with
    the corrected figure, so every benefit measured as a share of the declared trip cost is measured
    against the new figure from that moment; nothing else on the certificate changes and no money moves.
    What the policyholder can see afterwards is the certificate carrying the corrected declared trip cost
    under the approval reference quoted back to them.

    Args:
        care_policy_id: Id class — the reference number of the travel protection policy whose certificate
            is corrected, read from the policy record found for the traveller.
        care_request_id: Id class — the reference number of the policy service request in which the
            underwriting desk recorded its approval of this correction, read from the request record held
            against that policy.
        corrected_trip_cost_usd: Fixed-format class — the trip cost the certificate is corrected to,
            given as a USD amount with 2 decimal places, rounded half up to the cent.

    Returns:
        A plain-text confirmation naming the policy corrected, the approval reference it was made under
        and the declared trip cost as it now stands on the certificate. Receiving that confirmation is
        what indicates the certificate has been corrected; nothing else is returned.
    """
    ctx.update("care_policies", care_policy_id,
               trip_cost_usd=round(float(corrected_trip_cost_usd), 2))
    return (f"Policy {care_policy_id} corrected under approval {care_request_id}: declared trip cost now "
            f"{round(float(corrected_trip_cost_usd), 2):.2f} USD.")


@tool(owner="agent", rw="write")
def raise_premium_rerating_6e8395e4(ctx: ToolContext, care_policy_id: str, customer_id: str,
                                    source_entry_id: str, rerating_amount_usd: float) -> str:
    """Charge a re-rating of the premium against an earlier premium line on a travel protection policy,
    because a declared particular of the risk has changed. One call adds a re-rating line to the policy's
    premium record: it carries the amount charged, the date it posted and the earlier premium line it
    adjusts, and it increases the net premium the policyholder has paid for the cover. What the
    policyholder can see afterwards is the re-rating standing on their premium record alongside the lines
    raised when the certificate was issued.

    Args:
        care_policy_id: Id class — the reference number of the travel protection policy being re-rated,
            read from the policy record found for the traveller.
        customer_id: Id class — the traveller reference number of the policyholder charged, read from the
            traveller profile.
        source_entry_id: Id class — the reference number of the earlier premium line this re-rating is
            raised against, read from the premium record of that policy.
        rerating_amount_usd: Fixed-format class — the amount the re-rating charges, given as a positive
            USD amount with 2 decimal places, rounded half up to the cent.

    Returns:
        A plain-text confirmation naming the reference number minted for the re-rating line, the policy
        and the earlier line it adjusts, and the amount charged. Receiving that confirmation is what
        indicates the re-rating has been raised; nothing else is returned.
    """
    rid = ctx.make_id("care_pre_", care_policy_id, source_entry_id, rerating_amount_usd)
    ctx.create("care_premium_entries", rid, care_premium_entry_id=rid, care_policy_id=care_policy_id,
               customer_id=customer_id, event_type="care_premium_adjustment",
               charge_category="premium_adjustment",
               amount_usd=round(float(rerating_amount_usd), 2), currency_charged="USD",
               posted_date=ctx.now()[:10], posted_at=ctx.now(), insured_sequence=0,
               payment_channel="call_centre", source_entry_id=source_entry_id,
               reason_code="rating_correction")
    return (f"Re-rating {rid} raised on policy {care_policy_id} against line {source_entry_id}: "
            f"{round(float(rerating_amount_usd), 2):.2f} USD charged.")


@tool(owner="user", rw="write")
def release_cover_and_return_premium_07b45938(ctx: ToolContext, care_policy_id: str, customer_id: str,
                                              source_entry_id: str,
                                              returned_premium_usd: float) -> str:
    """Give up your own travel protection cover and take back the premium returned with it. One call
    marks your policy cancelled from this moment, stamps the moment you confirmed it, and adds a returned
    premium line to the policy's premium record, carrying the reference of the earlier premium line you
    give it, so the net premium you have paid falls by the amount returned. Cover ends as you confirm it and no incident
    after that moment is covered. What you can see afterwards is your policy standing cancelled with the
    returned premium on its record, going back to the way you paid.

    Args:
        care_policy_id: Id class — the reference number of your travel protection policy, the cover being
            given up, read from the policy record.
        customer_id: Id class — your own traveller reference number as the policyholder, read from the
            traveller profile.
        source_entry_id: Id class — the reference number of the premium line the return is raised
            against, read from the premium record of that policy.
        returned_premium_usd: Fixed-format class — the premium returned to you, given as a positive USD
            amount with 2 decimal places, rounded half up to the cent; the line itself carries it as a
            negative movement of the premium account.

    Returns:
        A plain-text confirmation naming the policy now cancelled, the moment the cancellation was
        confirmed, the reference number minted for the returned premium line and the amount returned.
        Receiving that confirmation is what indicates the cover has been given up and the premium
        returned; nothing else is returned.
    """
    ctx.update("care_policies", care_policy_id, status="cancelled", cancelled_at=ctx.now())
    rid = ctx.make_id("care_pre_", care_policy_id, source_entry_id, returned_premium_usd)
    ctx.create("care_premium_entries", rid, care_premium_entry_id=rid, care_policy_id=care_policy_id,
               customer_id=customer_id, event_type="care_premium_refund",
               charge_category="premium_refund",
               amount_usd=-round(float(returned_premium_usd), 2), currency_charged="USD",
               posted_date=ctx.now()[:10], posted_at=ctx.now(), insured_sequence=0,
               source_entry_id=source_entry_id, reason_code="mid_term_cancellation")
    return (f"Policy {care_policy_id} cancelled at {ctx.now()}; returned premium line {rid} raised "
            f"against {source_entry_id} for {round(float(returned_premium_usd), 2):.2f} USD.")

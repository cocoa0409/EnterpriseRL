"""Hidden task tools for the travel protection desk (scenario: online_travel_agency).

Each tool performs one atomic write on the travel protection records. None of them is listed to the
agent: their names reach a rollout only through the extended policy that names them, and they are
reached through the unlock/call meta-tool pair.
"""

from erlbench import ToolContext, tool


@tool(owner="agent", rw="write")
def charge_destination_loading_6e26c317(ctx: ToolContext, care_policy_id: str, customer_id: str,
                                        amount_usd: float, payment_channel: str) -> str:
    """Raise the destination loading line on a travel protection certificate. One call posts a single
    premium line of the destination loading kind against the named certificate, charged to the named
    policyholder, for the amount given and through the channel given; the line is dated the day it is
    posted and is charged on the certificate as a whole rather than on any one insured traveller.
    Once the call completes, the certificate's premium record carries a destination loading line the
    policyholder can see on their premium statement, and the line stands as a routine issue charge.

    Args:
        care_policy_id: Id class — the reference number of the travel protection policy record the
            loading is charged to, as read from the policy record returned by the policy finder.
        customer_id: Id class — the reference number of the traveller profile the premium is charged
            to, as read from the traveller profile returned by the profile finder.
        amount_usd: Fixed-format class — the amount of the loading line, given as a USD amount with
            2 decimal places, always positive, rounded half to even at the cent; the figure is held
            in US dollars whatever currency it is presented in, and it is never left empty.
        payment_channel: Enum class — the channel the premium line is taken through; exactly one of the
            four channels set out below and never anything else.
            web — the policyholder settles the line themselves on the website;
            mobile_app — the policyholder settles the line themselves in the mobile application;
            call_centre — the line is taken by a desk representative during a telephone call;
            corporate_portal — the line is billed through the corporate travel programme portal
            rather than to the traveller directly.

    Returns:
        A single confirmation sentence, as a string. It names the reference number of the premium
        line created (a text reference beginning cpe_), the reference number of the certificate it
        was posted to, and the amount posted in US dollars to two decimal places. The presence of the
        new line reference in the sentence is what indicates the line was posted; there is no other
        success flag.
    """
    rid = ctx.make_id("cpe_", care_policy_id, customer_id, amount_usd, payment_channel)
    ctx.create("care_premium_entries", rid,
               care_premium_entry_id=rid, care_policy_id=care_policy_id, customer_id=customer_id,
               event_type="care_premium_charge", charge_category="destination_loading",
               amount_usd=round(float(amount_usd), 2), currency_charged="USD",
               posted_date=ctx.now()[:10], posted_at=ctx.now(), insured_sequence=0,
               payment_channel=payment_channel, source_entry_id="", reason_code="routine_issue")
    return (f"Destination loading line {rid} posted to certificate {care_policy_id} "
            f"for {round(float(amount_usd), 2):.2f} USD.")


@tool(owner="user", rw="write")
def declare_supplier_compensation_6de86425(ctx: ToolContext, care_policy_id: str, customer_id: str,
                                           source_claim_id: str, claim_reference: str,
                                           claim_type: str, insured_sequence: int,
                                           restored_amount_usd: float) -> str:
    """Let the policyholder declare, in their own name, money a travel supplier has paid them for a
    loss their travel protection certificate has already settled, and put that money back against the
    benefit the certificate has consumed. One call records a single recovery row against the named
    certificate, tied to the settled payment it reverses in part, for the benefit named and the
    insured traveller named. Once the call completes, the certificate's claim record shows the
    recovery standing as recovered, and the benefit consumed against the certificate is reduced by the
    amount declared, so the policyholder has that much more of the benefit available again.

    Args:
        care_policy_id: Id class — the reference number of the travel protection policy record the
            recovery belongs to, as read from the policy record returned by the policy finder.
        customer_id: Id class — the reference number of the traveller profile the recovery belongs
            to, as read from the traveller profile returned by the profile finder.
        source_claim_id: Id class — the reference number of the settled claim payment row this
            recovery reverses in part, as read from the claim records returned by the claims finder.
        claim_reference: Verbatim class — the claim reference the insurer quoted for the claim the
            recovery belongs to, taken unchanged from the claim record it is read on and copied
            character for character, keeping the original wording, digits, spacing and punctuation,
            with no translation, normalisation, summarisation, addition or deletion (verbatim).
        claim_type: Enum class — the benefit of the plan the recovery restores; exactly one of the
            eleven benefits set out below and never anything else.
            trip_cancellation — the journey was given up before it began;
            trip_interruption — the journey was cut short once it had begun;
            medical_emergency — the traveller needed emergency medical treatment away from home;
            dental_emergency — the traveller needed emergency dental treatment away from home;
            evacuation — the traveller had to be moved to care or repatriated;
            baggage_delay — the traveller's baggage arrived late and essentials had to be bought;
            baggage_loss — the traveller's baggage or an article in it was lost or damaged;
            travel_delay — a booked departure ran late and the traveller was out of pocket;
            missed_connection — a late arrival caused an onward booked service to be missed;
            rental_damage — a hired vehicle was damaged while the traveller held it;
            cancel_for_any_reason — the journey was given up for a reason the listed causes do not
            name, on a plan carrying that benefit.
        insured_sequence: Fixed-format class — which insured traveller named on the certificate the
            recovery belongs to, as a whole number starting at 1 counted in the order the travellers
            are named, with no decimal part and never left empty.
        restored_amount_usd: Fixed-format class — the amount put back against the benefit consumed,
            given as a USD amount with 2 decimal places, always negative, rounded half to even at the
            cent; it is held in US dollars whatever currency the supplier paid in, and it is never
            left empty.

    Returns:
        A single confirmation sentence, as a string. It names the reference number of the recovery row
        created (a text reference beginning ccr_), the reference number of the certificate it was
        recorded against, and the amount restored in US dollars to two decimal places. The presence of
        the new recovery reference in the sentence is what indicates the declaration was recorded;
        there is no other success flag.
    """
    rid = ctx.make_id("ccr_", care_policy_id, source_claim_id, claim_reference, restored_amount_usd)
    ctx.create("care_claims", rid,
               care_claim_id=rid, care_policy_id=care_policy_id, customer_id=customer_id,
               event_type="care_claim_recovery", claim_reference=claim_reference,
               claim_type=claim_type, claimed_amount_usd=0.0,
               paid_amount_usd=round(float(restored_amount_usd), 2), deductible_applied_usd=0.0,
               incident_date="", filed_date="", decided_date=ctx.now()[:10], posted_at=ctx.now(),
               claim_status="recovered", insured_sequence=int(insured_sequence),
               source_claim_id=source_claim_id, loss_location_country="",
               supporting_document_reference="", reason_code="third_party_recovery")
    return (f"Supplier compensation recorded as recovery {rid} against certificate {care_policy_id} "
            f"for {round(float(restored_amount_usd), 2):.2f} USD.")


@tool(owner="agent", rw="write")
def settle_benefit_payment_411249ab(ctx: ToolContext, care_policy_id: str, customer_id: str,
                                    source_claim_id: str, claim_reference: str, claim_type: str,
                                    insured_sequence: int, paid_amount_usd: float,
                                    deductible_applied_usd: float) -> str:
    """Pay out a claim the insurer has already decided on a travel protection certificate. One call
    records a single payment row against the named certificate, tied to the insurer's decision it
    settles, for the benefit named and the insured traveller named, stating the amount paid to the
    policyholder and the deductible held back from it. Once the call completes, the certificate's
    claim record shows that claim standing as paid, and the policyholder can see the payment and the
    amount held back on their claim statement.

    Args:
        care_policy_id: Id class — the reference number of the travel protection policy record the
            payment is made under, as read from the policy record returned by the policy finder.
        customer_id: Id class — the reference number of the traveller profile the payment is made to,
            as read from the traveller profile returned by the profile finder.
        source_claim_id: Id class — the reference number of the insurer's decision row this payment
            settles, as read from the claim records returned by the claims finder.
        claim_reference: Verbatim class — the claim reference the insurer quoted for the claim being
            paid, taken unchanged from the claim record it is read on and copied character for
            character, keeping the original wording, digits, spacing and punctuation, with no
            translation, normalisation, summarisation, addition or deletion (verbatim).
        claim_type: Enum class — the benefit of the plan the payment is made against; exactly one of
            the eleven benefits set out below and never anything else.
            trip_cancellation — the journey was given up before it began;
            trip_interruption — the journey was cut short once it had begun;
            medical_emergency — the traveller needed emergency medical treatment away from home;
            dental_emergency — the traveller needed emergency dental treatment away from home;
            evacuation — the traveller had to be moved to care or repatriated;
            baggage_delay — the traveller's baggage arrived late and essentials had to be bought;
            baggage_loss — the traveller's baggage or an article in it was lost or damaged;
            travel_delay — a booked departure ran late and the traveller was out of pocket;
            missed_connection — a late arrival caused an onward booked service to be missed;
            rental_damage — a hired vehicle was damaged while the traveller held it;
            cancel_for_any_reason — the journey was given up for a reason the listed causes do not
            name, on a plan carrying that benefit.
        insured_sequence: Fixed-format class — which insured traveller named on the certificate the
            payment belongs to, as a whole number starting at 1 counted in the order the travellers
            are named, with no decimal part and never left empty.
        paid_amount_usd: Fixed-format class — the amount actually paid to the policyholder, given as a
            USD amount with 2 decimal places, always positive, rounded half to even at the cent; it
            is held in US dollars whatever currency it is paid in, and it is never left empty.
        deductible_applied_usd: Fixed-format class — the amount held back from the payment, given as a
            USD amount with 2 decimal places, zero or positive, rounded half to even at the cent;
            where nothing is held back it is given as 0.00 rather than left empty.

    Returns:
        A single confirmation sentence, as a string. It names the reference number of the payment row
        created (a text reference beginning ccp_), the reference number of the certificate it was
        recorded against, the amount paid in US dollars to two decimal places and the amount held back
        in US dollars to two decimal places. The presence of the new payment reference in the sentence
        is what indicates the payment was recorded; there is no other success flag.
    """
    rid = ctx.make_id("ccp_", care_policy_id, source_claim_id, claim_reference, paid_amount_usd)
    ctx.create("care_claims", rid,
               care_claim_id=rid, care_policy_id=care_policy_id, customer_id=customer_id,
               event_type="care_claim_payout", claim_reference=claim_reference,
               claim_type=claim_type, claimed_amount_usd=0.0,
               paid_amount_usd=round(float(paid_amount_usd), 2),
               deductible_applied_usd=round(float(deductible_applied_usd), 2),
               incident_date="", filed_date="", decided_date=ctx.now()[:10], posted_at=ctx.now(),
               claim_status="paid", insured_sequence=int(insured_sequence),
               source_claim_id=source_claim_id, loss_location_country="",
               supporting_document_reference="", reason_code="insurer_decision")
    return (f"Claim payment {rid} recorded against certificate {care_policy_id} for "
            f"{round(float(paid_amount_usd), 2):.2f} USD paid with "
            f"{round(float(deductible_applied_usd), 2):.2f} USD held back.")


@tool(owner="agent", rw="write")
def restate_declared_trip_cost_4b2fbffa(ctx: ToolContext, care_policy_id: str, care_request_id: str,
                                        corrected_trip_cost_usd: float) -> str:
    """Restate the declared trip cost printed on a travel protection certificate. One call replaces
    the trip cost the certificate declares with the figure given, against the underwriting request
    that authorised the correction. Once the call completes, the certificate shows the new declared
    trip cost wherever it is read, and every benefit measured as a share of the declared trip cost is
    measured against the new figure from that moment on.

    Args:
        care_policy_id: Id class — the reference number of the travel protection policy record whose
            declared trip cost is being restated, as read from the policy record returned by the
            policy finder.
        care_request_id: Id class — the reference number of the underwriting desk request that
            authorised this correction, as read from the policy request records returned by the
            policy request finder.
        corrected_trip_cost_usd: Fixed-format class — the trip cost the certificate is to declare
            from now on, given as a USD amount with 2 decimal places, always positive, rounded half
            to even at the cent; it is held in US dollars whatever currency the journey was bought
            in, and it is never left empty.

    Returns:
        A single confirmation sentence, as a string. It names the reference number of the certificate
        restated and the trip cost it now declares, in US dollars to two decimal places. The
        appearance of the new figure in the sentence is what indicates the restatement was made;
        there is no other success flag.
    """
    ctx.update("care_policies", care_policy_id,
               trip_cost_usd=round(float(corrected_trip_cost_usd), 2))
    return (f"Certificate {care_policy_id} now declares a trip cost of "
            f"{round(float(corrected_trip_cost_usd), 2):.2f} USD under request {care_request_id}.")


@tool(owner="agent", rw="write")
def raise_rating_adjustment_56692b3c(ctx: ToolContext, care_policy_id: str, customer_id: str,
                                     source_entry_id: str, insured_sequence: int,
                                     adjustment_amount_usd: float) -> str:
    """Raise a re-rating adjustment against an earlier premium line on a travel protection
    certificate. One call posts a single premium line of the adjustment kind, tied to the earlier
    line it re-rates, for the amount given and for the insured traveller given; the line is dated the
    day it is posted and is raised as a rating correction. Once the call completes, the certificate's
    premium record carries the adjustment alongside the line it re-rates, and the policyholder can
    see both on their premium statement.

    Args:
        care_policy_id: Id class — the reference number of the travel protection policy record the
            adjustment is raised on, as read from the policy record returned by the policy finder.
        customer_id: Id class — the reference number of the traveller profile the adjustment is
            charged to, as read from the traveller profile returned by the profile finder.
        source_entry_id: Id class — the reference number of the earlier premium line this adjustment
            re-rates, as read from the premium lines returned by the premium entry finder.
        insured_sequence: Fixed-format class — which insured traveller named on the certificate the
            adjustment belongs to, as a whole number starting at 1 counted in the order the
            travellers are named, or 0 where it is raised on the certificate as a whole; it carries
            no decimal part and is never left empty.
        adjustment_amount_usd: Fixed-format class — the amount of the adjustment line, given as a USD
            amount with 2 decimal places, positive where further premium is charged and negative
            where premium is given back, rounded half to even at the cent; it is held in US dollars
            whatever currency it is presented in, and it is never left empty.

    Returns:
        A single confirmation sentence, as a string. It names the reference number of the adjustment
        line created (a text reference beginning cpa_), the reference number of the certificate it
        was posted to, the reference of the line it re-rates and the amount posted in US dollars to
        two decimal places. The presence of the new line reference in the sentence is what indicates
        the adjustment was posted; there is no other success flag.
    """
    rid = ctx.make_id("cpa_", care_policy_id, source_entry_id, adjustment_amount_usd)
    ctx.create("care_premium_entries", rid,
               care_premium_entry_id=rid, care_policy_id=care_policy_id, customer_id=customer_id,
               event_type="care_premium_adjustment", charge_category="premium_adjustment",
               amount_usd=round(float(adjustment_amount_usd), 2), currency_charged="USD",
               posted_date=ctx.now()[:10], posted_at=ctx.now(),
               insured_sequence=int(insured_sequence), payment_channel="call_centre",
               source_entry_id=source_entry_id, reason_code="rating_correction")
    return (f"Re-rating adjustment {rid} posted to certificate {care_policy_id} against line "
            f"{source_entry_id} for {round(float(adjustment_amount_usd), 2):.2f} USD.")


@tool(owner="user", rw="write")
def file_cancellation_claim_621a2df1(ctx: ToolContext, care_policy_id: str, customer_id: str,
                                     claim_reference: str, claim_type: str, incident_date: str,
                                     loss_location_country: str,
                                     supporting_document_reference: str, insured_sequence: int,
                                     claimed_amount_usd: float) -> str:
    """Let the traveller file a claim in their own name against one benefit of their travel
    protection certificate. One call opens a single claim record on the named certificate for the
    benefit named, the incident date given and the insured traveller named, recording the amount
    claimed before any limit or deductible and the evidence supplied. Once the call completes, the
    claim stands as filed with the insurer against that certificate, and the traveller can see it on
    their claim statement with the reference the insurer quoted.

    Args:
        care_policy_id: Id class — the reference number of the travel protection policy record the
            claim is made under, as read from the policy record returned by the policy finder.
        customer_id: Id class — the reference number of the traveller profile making the claim, as
            read from the traveller profile returned by the profile finder.
        claim_reference: Verbatim class — the claim reference the insurer quoted, taken from what the
            traveller reads out and copied character for character, keeping the original wording,
            digits, spacing and punctuation, with no translation, normalisation, summarisation,
            addition or deletion (verbatim).
        claim_type: Enum class — the benefit of the plan the claim is made against; exactly one of
            the eleven benefits set out below and never anything else.
            trip_cancellation — the journey was given up before it began;
            trip_interruption — the journey was cut short once it had begun;
            medical_emergency — the traveller needed emergency medical treatment away from home;
            dental_emergency — the traveller needed emergency dental treatment away from home;
            evacuation — the traveller had to be moved to care or repatriated;
            baggage_delay — the traveller's baggage arrived late and essentials had to be bought;
            baggage_loss — the traveller's baggage or an article in it was lost or damaged;
            travel_delay — a booked departure ran late and the traveller was out of pocket;
            missed_connection — a late arrival caused an onward booked service to be missed;
            rental_damage — a hired vehicle was damaged while the traveller held it;
            cancel_for_any_reason — the journey was given up for a reason the listed causes do not
            name, on a plan carrying that benefit.
        incident_date: Fixed-format class — the day the insured incident happened, as a calendar date
            YYYY-MM-DD in the traveller's own local calendar, with no time part and never left empty.
        loss_location_country: Fixed-format class — where the incident happened, given as an ISO 3166-1
            alpha-2 country code, uppercase, exactly two letters, and never left empty.
        supporting_document_reference: Verbatim class — the reference of the evidence the traveller
            supplies with the claim, taken from what the traveller reads out and copied character for
            character, keeping the original wording, digits, spacing and punctuation, with no
            translation, normalisation, summarisation, addition or deletion (verbatim).
        insured_sequence: Fixed-format class — which insured traveller named on the certificate the
            claim belongs to, as a whole number starting at 1 counted in the order the travellers are
            named, with no decimal part and never left empty.
        claimed_amount_usd: Fixed-format class — the amount being claimed before any limit or
            deductible is applied, given as a USD amount with 2 decimal places, always positive,
            rounded half to even at the cent; it is held in US dollars whatever currency the loss was
            suffered in, and it is never left empty.

    Returns:
        A single confirmation sentence, as a string. It names the reference number of the claim record
        opened (a text reference beginning ccf_), the reference number of the certificate it was
        opened on, the claim reference the insurer quoted and the amount claimed in US dollars to two
        decimal places. The presence of the new claim reference in the sentence is what indicates the
        claim was filed; there is no other success flag.
    """
    rid = ctx.make_id("ccf_", care_policy_id, claim_reference, claim_type, claimed_amount_usd)
    ctx.create("care_claims", rid,
               care_claim_id=rid, care_policy_id=care_policy_id, customer_id=customer_id,
               event_type="care_claim_file", claim_reference=claim_reference, claim_type=claim_type,
               claimed_amount_usd=round(float(claimed_amount_usd), 2), paid_amount_usd=0.0,
               deductible_applied_usd=0.0, incident_date=incident_date,
               filed_date=ctx.now()[:10], decided_date="", posted_at=ctx.now(),
               claim_status="filed", insured_sequence=int(insured_sequence), source_claim_id="",
               loss_location_country=loss_location_country,
               supporting_document_reference=supporting_document_reference,
               reason_code="insured_claim")
    return (f"Claim {rid} filed on certificate {care_policy_id} under reference {claim_reference} "
            f"for {round(float(claimed_amount_usd), 2):.2f} USD.")

"""Hidden task tools of the guest_cancellations_and_refunds difficulty (Stays category).

Each tool performs exactly one atomic write on a stay's money ledger (stay_transactions) with the values the
caller passes. No tool checks eligibility, order, ownership or amounts: every policy judgement is made before
the call, from the published rules and the records.
"""

from erlbench import ToolContext, tool



@tool(owner="user", rw="write")
def pay_notice_charge_caff8891(ctx: ToolContext, stay_id: str, installment_number: int, amount: float) -> str:
    """The guest pays, from their own payment method, the notice charge owed on a stay they cancelled
    while it was in progress (the nights the cancellation keeps that the stay's collections had not paid). One call records one collection on that stay's money ledger for the amount
    given, filed under the installment number given; the amount then shows as collected on the stay and
    the guest sees the payment on their reservation. The receipt confirms the collection.

    Args:
        stay_id: Id class — the reference number of the cancelled stay (reservation) the guest is paying the
            notice charge on, as returned by the stay lookup for that guest.
        installment_number: Fixed-format class — the installment the notice charge is filed under, a
            non-negative integer (whole number, no decimals): the number of the installment that covers the
            first unpaid night the cancellation keeps (1 when no installment was ever collected on the stay).
        amount: Fixed-format class — the notice charge the guest pays, a positive USD amount in US dollars
            with 2 decimal places; a value with more decimals is rounded half up to 2 decimal places when booked.

    Returns:
        A text rendering of a dictionary receipt: collection_reference (text, the reference number of the
        new collection record), stay_id (text, the stay paid on), installment_number (integer, the
        installment the collection is filed under), amount (number, USD with 2 decimal places, the amount
        collected), posted_at (text, YYYY-MM-DDTHH:MM:SS moment the collection was recorded) and status
        (text, always "collected" when the payment went through).
    """
    rows = ctx.find("stays", stay_id=stay_id)
    guest_id = rows[0].get("customer_id", "") if rows else ""
    rid = ctx.make_id("stx_", stay_id, installment_number, amount)
    posted_at = str(ctx.now())[:19].replace(" ", "T")
    ctx.create("stay_transactions", rid, stay_txn_id=rid, stay_id=stay_id, customer_id=guest_id,
               event_type="stay_payment_collected", posted_at=posted_at, amount=round(float(amount), 2),
               installment_number=int(installment_number), attempt_number=0, charge_component="none",
               refund_reason="none", funded_by="none", refund_stage="none", request_id="",
               reviewer_role="none", rating=0)
    return str({"collection_reference": rid, "stay_id": stay_id, "installment_number": int(installment_number),
                "amount": round(float(amount), 2), "posted_at": posted_at, "status": "collected"})


@tool(owner="agent", rw="write")
def refund_pet_fee_41a7068c(ctx: ToolContext, stay_id: str, charge_component: str, refund_reason: str,
                            request_id: str, funded_by: str, refund_stage: str, amount: float) -> str:
    """Issue a refund of part of a stay's pet fee to the guest's original payment method. One call
    records one refund on the stay's money ledger for the charge component, reason, funding side, payout
    stage and amount given; the refund then shows on the stay and reaches the guest's card within the
    card issuer's posting time. The receipt confirms the refund.

    Args:
        stay_id: Id class — the reference number of the stay (reservation) whose pet fee is refunded, as
            returned by the stay lookup for the guest.
        charge_component: Enum class — the charge component the refund is booked against: `nightly` for the price of the stay's nights; `cleaning_fee` for the cleaning fee (or short-stay
            cleaning fee) charged on the stay; `pet_fee` for the pet fee charged on the stay;
            `extra_guest_fee` for the fee charged for guests above the listing's included guest count;
            `guest_service_fee` for Roamhaven's guest service fee; `occupancy_tax` for the occupancy tax
            charged on the stay; `none` only for a record that refunds no charge component, which a
            refund never is.
        refund_reason: Enum class — why the refund is issued: `guest_cancellation` when it rests on the
            guest cancelling the stay; `host_cancellation` when the host cancelled the stay;
            `alteration` when an accepted date or guest-count change lowered the price; `travel_issue`
            when it rests on an approved travel-issue request; `major_disruptive_event` when it rests on an
            approved major-disruptive-event request; `none` only for a record that is no refund, which this
            never is.
        request_id: Id class — the reference number of the stay request the refund rests on, as returned by
            the stay request lookup; pass an empty value when the refund rests on no request.
        funded_by: Enum class — who bears the refund: `host` when it comes out of the host's earnings for
            the stay; `platform` when Roamhaven bears it; `none` only for a record that is no refund, which
            this never is.
        refund_stage: Enum class — the payout stage of the stay at the moment of the refund:
            `before_payout_release` when no release of the host's earnings for this stay is on record yet;
            `after_payout_release` when such a release is already on record; `none` only for a record that
            is no refund, which this never is.
        amount: Fixed-format class — the refund, a positive USD amount in US dollars with 2 decimal places;
            a value with more decimals is rounded half up to 2 decimal places when booked.

    Returns:
        A text rendering of a dictionary receipt: refund_reference (text, the reference number of the new
        refund record), stay_id (text), charge_component (text), refund_reason (text), amount (number, USD
        with 2 decimal places), funded_by (text), refund_stage (text), posted_at (text, YYYY-MM-DDTHH:MM:SS
        moment the refund was issued) and status (text, always "refund_issued" when the refund went out).
    """
    rows = ctx.find("stays", stay_id=stay_id)
    guest_id = rows[0].get("customer_id", "") if rows else ""
    rid = ctx.make_id("rpf_", stay_id, charge_component, refund_reason, request_id, funded_by, refund_stage,
                      amount)
    posted_at = str(ctx.now())[:19].replace(" ", "T")
    ctx.create("stay_transactions", rid, stay_txn_id=rid, stay_id=stay_id, customer_id=guest_id,
               event_type="stay_refund_issued", posted_at=posted_at, amount=round(float(amount), 2),
               installment_number=0, attempt_number=0, charge_component=charge_component,
               refund_reason=refund_reason, funded_by=funded_by, refund_stage=refund_stage,
               request_id=request_id, reviewer_role="none", rating=0)
    return str({"refund_reference": rid, "stay_id": stay_id, "charge_component": charge_component,
                "refund_reason": refund_reason, "amount": round(float(amount), 2), "funded_by": funded_by,
                "refund_stage": refund_stage, "posted_at": posted_at, "status": "refund_issued"})


@tool(owner="agent", rw="write")
def refund_extra_guest_fee_b492f389(ctx: ToolContext, stay_id: str, charge_component: str, refund_reason: str,
                                    request_id: str, funded_by: str, refund_stage: str, amount: float) -> str:
    """Issue a refund of part of a stay's extra-guest fee to the guest's original payment method. One
    call records one refund on the stay's money ledger for the charge component, reason, funding side,
    payout stage and amount given; the refund then shows on the stay and reaches the guest's card within
    the card issuer's posting time. The receipt confirms the refund.

    Args:
        stay_id: Id class — the reference number of the stay (reservation) whose extra-guest fee is
            refunded, as returned by the stay lookup for the guest.
        charge_component: Enum class — the charge component the refund is booked against: `nightly` for the price of the stay's nights; `cleaning_fee` for the cleaning fee (or short-stay
            cleaning fee) charged on the stay; `pet_fee` for the pet fee charged on the stay;
            `extra_guest_fee` for the fee charged for guests above the listing's included guest count;
            `guest_service_fee` for Roamhaven's guest service fee; `occupancy_tax` for the occupancy tax
            charged on the stay; `none` only for a record that refunds no charge component, which a
            refund never is.
        refund_reason: Enum class — why the refund is issued: `guest_cancellation` when it rests on the
            guest cancelling the stay; `host_cancellation` when the host cancelled the stay;
            `alteration` when an accepted date or guest-count change lowered the price; `travel_issue`
            when it rests on an approved travel-issue request; `major_disruptive_event` when it rests on an
            approved major-disruptive-event request; `none` only for a record that is no refund, which this
            never is.
        request_id: Id class — the reference number of the stay request the refund rests on, as returned by
            the stay request lookup; pass an empty value when the refund rests on no request.
        funded_by: Enum class — who bears the refund: `host` when it comes out of the host's earnings for
            the stay; `platform` when Roamhaven bears it; `none` only for a record that is no refund, which
            this never is.
        refund_stage: Enum class — the payout stage of the stay at the moment of the refund:
            `before_payout_release` when no release of the host's earnings for this stay is on record yet;
            `after_payout_release` when such a release is already on record; `none` only for a record that
            is no refund, which this never is.
        amount: Fixed-format class — the refund, a positive USD amount in US dollars with 2 decimal places;
            a value with more decimals is rounded half up to 2 decimal places when booked.

    Returns:
        A text rendering of a dictionary receipt: refund_reference (text, the reference number of the new
        refund record), stay_id (text), charge_component (text), refund_reason (text), amount (number, USD
        with 2 decimal places), funded_by (text), refund_stage (text), posted_at (text, YYYY-MM-DDTHH:MM:SS
        moment the refund was issued) and status (text, always "refund_issued" when the refund went out).
    """
    rows = ctx.find("stays", stay_id=stay_id)
    guest_id = rows[0].get("customer_id", "") if rows else ""
    rid = ctx.make_id("rxg_", stay_id, charge_component, refund_reason, request_id, funded_by, refund_stage,
                      amount)
    posted_at = str(ctx.now())[:19].replace(" ", "T")
    ctx.create("stay_transactions", rid, stay_txn_id=rid, stay_id=stay_id, customer_id=guest_id,
               event_type="stay_refund_issued", posted_at=posted_at, amount=round(float(amount), 2),
               installment_number=0, attempt_number=0, charge_component=charge_component,
               refund_reason=refund_reason, funded_by=funded_by, refund_stage=refund_stage,
               request_id=request_id, reviewer_role="none", rating=0)
    return str({"refund_reference": rid, "stay_id": stay_id, "charge_component": charge_component,
                "refund_reason": refund_reason, "amount": round(float(amount), 2), "funded_by": funded_by,
                "refund_stage": refund_stage, "posted_at": posted_at, "status": "refund_issued"})


@tool(owner="agent", rw="write")
def refund_service_fee_f4bed6e4(ctx: ToolContext, stay_id: str, charge_component: str, refund_reason: str,
                                request_id: str, funded_by: str, refund_stage: str, amount: float) -> str:
    """Issue a refund of part of Roamhaven's guest service fee on a stay the guest cancelled, to the
    guest's original payment method. One call records one refund on the stay's money ledger for the
    charge component, reason, funding side, payout stage and amount given; the refund then shows on the
    stay and reaches the guest's card within the card issuer's posting time. The receipt confirms it.

    Args:
        stay_id: Id class — the reference number of the stay (reservation) whose guest service fee is
            refunded, as returned by the stay lookup for the guest.
        charge_component: Enum class — the charge component the refund is booked against: `nightly` for the price of the stay's nights; `cleaning_fee` for the cleaning fee (or short-stay
            cleaning fee) charged on the stay; `pet_fee` for the pet fee charged on the stay;
            `extra_guest_fee` for the fee charged for guests above the listing's included guest count;
            `guest_service_fee` for Roamhaven's guest service fee; `occupancy_tax` for the occupancy tax
            charged on the stay; `none` only for a record that refunds no charge component, which a
            refund never is.
        refund_reason: Enum class — why the refund is issued: `guest_cancellation` when it rests on the
            guest cancelling the stay; `host_cancellation` when the host cancelled the stay;
            `alteration` when an accepted date or guest-count change lowered the price; `travel_issue`
            when it rests on an approved travel-issue request; `major_disruptive_event` when it rests on an
            approved major-disruptive-event request; `none` only for a record that is no refund, which this
            never is.
        request_id: Id class — the reference number of the stay request the refund rests on, as returned by
            the stay request lookup; pass an empty value when the refund rests on no request.
        funded_by: Enum class — who bears the refund: `host` when it comes out of the host's earnings for
            the stay; `platform` when Roamhaven bears it; `none` only for a record that is no refund, which
            this never is.
        refund_stage: Enum class — the payout stage of the stay at the moment of the refund:
            `before_payout_release` when no release of the host's earnings for this stay is on record yet;
            `after_payout_release` when such a release is already on record; `none` only for a record that
            is no refund, which this never is.
        amount: Fixed-format class — the refund, a positive USD amount in US dollars with 2 decimal places;
            a value with more decimals is rounded half up to 2 decimal places when booked.

    Returns:
        A text rendering of a dictionary receipt: refund_reference (text, the reference number of the new
        refund record), stay_id (text), charge_component (text), refund_reason (text), amount (number, USD
        with 2 decimal places), funded_by (text), refund_stage (text), posted_at (text, YYYY-MM-DDTHH:MM:SS
        moment the refund was issued) and status (text, always "refund_issued" when the refund went out).
    """
    rows = ctx.find("stays", stay_id=stay_id)
    guest_id = rows[0].get("customer_id", "") if rows else ""
    rid = ctx.make_id("rsf_", stay_id, charge_component, refund_reason, request_id, funded_by, refund_stage,
                      amount)
    posted_at = str(ctx.now())[:19].replace(" ", "T")
    ctx.create("stay_transactions", rid, stay_txn_id=rid, stay_id=stay_id, customer_id=guest_id,
               event_type="stay_refund_issued", posted_at=posted_at, amount=round(float(amount), 2),
               installment_number=0, attempt_number=0, charge_component=charge_component,
               refund_reason=refund_reason, funded_by=funded_by, refund_stage=refund_stage,
               request_id=request_id, reviewer_role="none", rating=0)
    return str({"refund_reference": rid, "stay_id": stay_id, "charge_component": charge_component,
                "refund_reason": refund_reason, "amount": round(float(amount), 2), "funded_by": funded_by,
                "refund_stage": refund_stage, "posted_at": posted_at, "status": "refund_issued"})


@tool(owner="agent", rw="write")
def refund_travel_nightly_d238de09(ctx: ToolContext, stay_id: str, charge_component: str, refund_reason: str,
                                   request_id: str, funded_by: str, refund_stage: str, amount: float) -> str:
    """Issue the nightly part of a refund that rests on an approved travel-issue request, to the
    guest's original payment method. One call records one refund on the stay's money ledger for the
    charge component, reason, request, funding side, payout stage and amount given; the refund then
    shows on the stay and reaches the guest's card within the card issuer's posting time. The receipt
    confirms the refund.

    Args:
        stay_id: Id class — the reference number of the stay (reservation) whose travel-issue nightly refund is booked, as
            returned by the stay lookup for the guest.
        charge_component: Enum class — the charge component the refund is booked against: `nightly` for the price of the stay's nights; `cleaning_fee` for the cleaning fee (or short-stay
            cleaning fee) charged on the stay; `pet_fee` for the pet fee charged on the stay;
            `extra_guest_fee` for the fee charged for guests above the listing's included guest count;
            `guest_service_fee` for Roamhaven's guest service fee; `occupancy_tax` for the occupancy tax
            charged on the stay; `none` only for a record that refunds no charge component, which a
            refund never is.
        refund_reason: Enum class — why the refund is issued: `guest_cancellation` when it rests on the
            guest cancelling the stay; `host_cancellation` when the host cancelled the stay;
            `alteration` when an accepted date or guest-count change lowered the price; `travel_issue`
            when it rests on an approved travel-issue request; `major_disruptive_event` when it rests on an
            approved major-disruptive-event request; `none` only for a record that is no refund, which this
            never is.
        request_id: Id class — the reference number of the stay request the refund rests on, as returned by
            the stay request lookup; pass an empty value when the refund rests on no request.
        funded_by: Enum class — who bears the refund: `host` when it comes out of the host's earnings for
            the stay; `platform` when Roamhaven bears it; `none` only for a record that is no refund, which
            this never is.
        refund_stage: Enum class — the payout stage of the stay at the moment of the refund:
            `before_payout_release` when no release of the host's earnings for this stay is on record yet;
            `after_payout_release` when such a release is already on record; `none` only for a record that
            is no refund, which this never is.
        amount: Fixed-format class — the refund, a positive USD amount in US dollars with 2 decimal places;
            a value with more decimals is rounded half up to 2 decimal places when booked.

    Returns:
        A text rendering of a dictionary receipt: refund_reference (text, the reference number of the new
        refund record), stay_id (text), charge_component (text), refund_reason (text), amount (number, USD
        with 2 decimal places), funded_by (text), refund_stage (text), posted_at (text, YYYY-MM-DDTHH:MM:SS
        moment the refund was issued) and status (text, always "refund_issued" when the refund went out).
    """
    rows = ctx.find("stays", stay_id=stay_id)
    guest_id = rows[0].get("customer_id", "") if rows else ""
    rid = ctx.make_id("rtn_", stay_id, charge_component, refund_reason, request_id, funded_by, refund_stage,
                      amount)
    posted_at = str(ctx.now())[:19].replace(" ", "T")
    ctx.create("stay_transactions", rid, stay_txn_id=rid, stay_id=stay_id, customer_id=guest_id,
               event_type="stay_refund_issued", posted_at=posted_at, amount=round(float(amount), 2),
               installment_number=0, attempt_number=0, charge_component=charge_component,
               refund_reason=refund_reason, funded_by=funded_by, refund_stage=refund_stage,
               request_id=request_id, reviewer_role="none", rating=0)
    return str({"refund_reference": rid, "stay_id": stay_id, "charge_component": charge_component,
                "refund_reason": refund_reason, "amount": round(float(amount), 2), "funded_by": funded_by,
                "refund_stage": refund_stage, "posted_at": posted_at, "status": "refund_issued"})


@tool(owner="agent", rw="write")
def refund_travel_service_fee_041715de(ctx: ToolContext, stay_id: str, charge_component: str, refund_reason: str,
                                       request_id: str, funded_by: str, refund_stage: str, amount: float) -> str:
    """Issue the part of Roamhaven's guest service fee that is refunded on an approved travel-issue
    request, to the guest's original payment method. One call records one refund on the stay's money
    ledger for the charge component, reason, request, funding side, payout stage and amount given; the
    refund then shows on the stay and reaches the guest's card within the card issuer's posting time.
    The receipt confirms the refund.

    Args:
        stay_id: Id class — the reference number of the stay (reservation) whose travel-issue service-fee refund is booked, as
            returned by the stay lookup for the guest.
        charge_component: Enum class — the charge component the refund is booked against: `nightly` for the price of the stay's nights; `cleaning_fee` for the cleaning fee (or short-stay
            cleaning fee) charged on the stay; `pet_fee` for the pet fee charged on the stay;
            `extra_guest_fee` for the fee charged for guests above the listing's included guest count;
            `guest_service_fee` for Roamhaven's guest service fee; `occupancy_tax` for the occupancy tax
            charged on the stay; `none` only for a record that refunds no charge component, which a
            refund never is.
        refund_reason: Enum class — why the refund is issued: `guest_cancellation` when it rests on the
            guest cancelling the stay; `host_cancellation` when the host cancelled the stay;
            `alteration` when an accepted date or guest-count change lowered the price; `travel_issue`
            when it rests on an approved travel-issue request; `major_disruptive_event` when it rests on an
            approved major-disruptive-event request; `none` only for a record that is no refund, which this
            never is.
        request_id: Id class — the reference number of the stay request the refund rests on, as returned by
            the stay request lookup; pass an empty value when the refund rests on no request.
        funded_by: Enum class — who bears the refund: `host` when it comes out of the host's earnings for
            the stay; `platform` when Roamhaven bears it; `none` only for a record that is no refund, which
            this never is.
        refund_stage: Enum class — the payout stage of the stay at the moment of the refund:
            `before_payout_release` when no release of the host's earnings for this stay is on record yet;
            `after_payout_release` when such a release is already on record; `none` only for a record that
            is no refund, which this never is.
        amount: Fixed-format class — the refund, a positive USD amount in US dollars with 2 decimal places;
            a value with more decimals is rounded half up to 2 decimal places when booked.

    Returns:
        A text rendering of a dictionary receipt: refund_reference (text, the reference number of the new
        refund record), stay_id (text), charge_component (text), refund_reason (text), amount (number, USD
        with 2 decimal places), funded_by (text), refund_stage (text), posted_at (text, YYYY-MM-DDTHH:MM:SS
        moment the refund was issued) and status (text, always "refund_issued" when the refund went out).
    """
    rows = ctx.find("stays", stay_id=stay_id)
    guest_id = rows[0].get("customer_id", "") if rows else ""
    rid = ctx.make_id("rts_", stay_id, charge_component, refund_reason, request_id, funded_by, refund_stage,
                      amount)
    posted_at = str(ctx.now())[:19].replace(" ", "T")
    ctx.create("stay_transactions", rid, stay_txn_id=rid, stay_id=stay_id, customer_id=guest_id,
               event_type="stay_refund_issued", posted_at=posted_at, amount=round(float(amount), 2),
               installment_number=0, attempt_number=0, charge_component=charge_component,
               refund_reason=refund_reason, funded_by=funded_by, refund_stage=refund_stage,
               request_id=request_id, reviewer_role="none", rating=0)
    return str({"refund_reference": rid, "stay_id": stay_id, "charge_component": charge_component,
                "refund_reason": refund_reason, "amount": round(float(amount), 2), "funded_by": funded_by,
                "refund_stage": refund_stage, "posted_at": posted_at, "status": "refund_issued"})


@tool(owner="user", rw="write")
def pay_first_installment_26275b3d(ctx: ToolContext, stay_id: str, amount: float) -> str:
    """The guest pays installment 1 of a stay from their own payment method when the automatic
    collection of that installment at confirmation was declined by their card. One call records one
    collection on the stay's money ledger, filed as installment 1, for the amount given; the amount then
    shows as collected on the stay and the guest sees the payment on their reservation. The receipt
    confirms the collection.

    Args:
        stay_id: Id class — the reference number of the stay (reservation) whose installment 1 the guest
            pays, as returned by the stay lookup for that guest.
        amount: Fixed-format class — the amount of installment 1 the guest pays, a positive USD amount in US
            dollars with 2 decimal places; a value with more decimals is rounded half up to 2 decimal places
            when booked.

    Returns:
        A text rendering of a dictionary receipt: collection_reference (text, the reference number of the
        new collection record), stay_id (text, the stay paid on), installment_number (integer, always 1),
        amount (number, USD with 2 decimal places, the amount collected), posted_at (text,
        YYYY-MM-DDTHH:MM:SS moment the collection was recorded) and status (text, always "collected" when
        the payment went through).
    """
    rows = ctx.find("stays", stay_id=stay_id)
    guest_id = rows[0].get("customer_id", "") if rows else ""
    rid = ctx.make_id("sti_", stay_id, amount)
    posted_at = str(ctx.now())[:19].replace(" ", "T")
    ctx.create("stay_transactions", rid, stay_txn_id=rid, stay_id=stay_id, customer_id=guest_id,
               event_type="stay_payment_collected", posted_at=posted_at, amount=round(float(amount), 2),
               installment_number=1, attempt_number=0, charge_component="none", refund_reason="none",
               funded_by="none", refund_stage="none", request_id="", reviewer_role="none", rating=0)
    return str({"collection_reference": rid, "stay_id": stay_id, "installment_number": 1,
                "amount": round(float(amount), 2), "posted_at": posted_at, "status": "collected"})

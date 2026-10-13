"""Hidden task tools of the damage_claims_and_protection difficulty (HostCover, category protect).

Each tool performs one atomic write on the HostCover ledger (protection_events). The settlement
figure is worked out by the caller from the published HostCover rules and the records; the tools
never compute, aggregate, judge eligibility or refuse.
"""

from erlbench import ToolContext, tool


@tool(owner="agent", rw="write")
def pay_theft_reimbursement_c380c173(ctx: ToolContext, claim_id: str, amount: float) -> str:
    """Book the HostCover reimbursement Roamhaven pays the host on one approved theft claim.

    One call records a single reimbursement entry on the HostCover ledger of the plan the theft
    claim was filed under: the entry carries the claim, the stay the theft arose from, the loss the
    claims team verified on the claim, today's date and the reimbursement amount passed in. The
    reimbursements account of the plan grows by that amount and the claim shows as reimbursed in
    the HostCover ledger from then on; the money is credited to the host's default payout method by
    the payout desk. Success is the receipt below; the entry is visible at once in the HostCover
    ledger lookup for the claim.

    Args:
        claim_id: Id class — the reference number of the approved theft claim being reimbursed, as
            returned by the damage-claim lookup for the host's HostCover plan.
        amount: Fixed-format class — the reimbursement Roamhaven pays on the claim, a positive USD
            amount with 2 decimal places (cents), already rounded to the cent; no currency symbol.

    Returns:
        A dict receipt: {"status": "reimbursement_booked" when the entry was written,
        "protection_event_id": the reference number of the new ledger entry (string),
        "claim_id": the theft claim reimbursed (string), "stay_id": the stay the claim arose from
        (string), "amount": the reimbursement booked in USD (number, 2 decimal places),
        "posted_date": the booking date YYYY-MM-DD}.
    """
    # Copy the linkage of the claim (plan, host, stay, verified loss) onto the ledger entry.
    rows = ctx.find("protection_claims", claim_id=claim_id)
    claim = rows[0] if rows else {}
    value = round(float(amount), 2)
    rid = ctx.make_id("pev_", "reimbursement", claim_id, value)
    posted = ctx.now()[:10]
    ctx.create("protection_events", rid, protection_event_id=rid,
               protection_plan_id=claim.get("protection_plan_id", ""),
               customer_id=claim.get("customer_id", ""), event_type="protect_reimbursement_paid",
               posted_date=posted, claim_id=claim_id, stay_id=claim.get("stay_id", ""),
               amount=value, premium_base_amount=0.0,
               verified_loss_amount=round(float(claim.get("verified_loss_amount") or 0), 2),
               guest_response="none", denial_reason="none")
    return str({"status": "reimbursement_booked", "protection_event_id": rid, "claim_id": claim_id,
                "stay_id": claim.get("stay_id", ""), "amount": value, "posted_date": posted})


@tool(owner="user", rw="write")
def accept_valuables_settlement_01cb0de3(ctx: ToolContext, claim_id: str, amount: float) -> str:
    """Accept, as the host, the settlement offered on your approved valuables claim.

    Art, jewellery and collectibles are settled only once the host accepts the settlement in
    person, because their value rests on the host's own appraisals, provenance and receipts.
    One call records your acceptance and books the settlement as a reimbursement entry on the
    HostCover ledger of the plan the valuables claim was filed under, with the claim, the stay the
    loss arose from, the loss the claims team verified, today's date and the settlement amount you
    accept. The plan's reimbursements account grows by that amount, the claim shows as reimbursed
    in the HostCover ledger, and the money is credited to your default payout method by the payout
    desk. Success is the receipt below.

    Args:
        claim_id: Id class — the reference number of your approved valuables claim, as the support
            agent reads it to you from the damage-claim records of your HostCover plan.
        amount: Fixed-format class — the settlement you accept on the claim, a positive USD amount
            with 2 decimal places (cents), exactly as the support agent states it; no currency
            symbol.

    Returns:
        A dict receipt: {"status": "settlement_accepted" when your acceptance was recorded and the
        settlement booked, "protection_event_id": the reference number of the new ledger entry
        (string), "claim_id": the valuables claim settled (string), "stay_id": the stay the loss
        arose from (string), "amount": the settlement booked in USD (number, 2 decimal places),
        "posted_date": the booking date YYYY-MM-DD}.
    """
    # Copy the linkage of the claim (plan, host, stay, verified loss) onto the ledger entry.
    rows = ctx.find("protection_claims", claim_id=claim_id)
    claim = rows[0] if rows else {}
    value = round(float(amount), 2)
    rid = ctx.make_id("pev_", "reimbursement", claim_id, value)
    posted = ctx.now()[:10]
    ctx.create("protection_events", rid, protection_event_id=rid,
               protection_plan_id=claim.get("protection_plan_id", ""),
               customer_id=claim.get("customer_id", ""), event_type="protect_reimbursement_paid",
               posted_date=posted, claim_id=claim_id, stay_id=claim.get("stay_id", ""),
               amount=value, premium_base_amount=0.0,
               verified_loss_amount=round(float(claim.get("verified_loss_amount") or 0), 2),
               guest_response="none", denial_reason="none")
    return str({"status": "settlement_accepted", "protection_event_id": rid, "claim_id": claim_id,
                "stay_id": claim.get("stay_id", ""), "amount": value, "posted_date": posted})


@tool(owner="agent", rw="write")
def pay_property_damage_reimbursement_941cbbf5(ctx: ToolContext, claim_id: str, amount: float) -> str:
    """Book the HostCover reimbursement Roamhaven pays the host on one approved property-damage claim.

    One call records a single reimbursement entry on the HostCover ledger of the plan the
    property-damage claim was filed under: the entry carries the claim, the stay the damage arose
    from, the loss the claims team verified on the claim, today's date and the reimbursement amount
    passed in. The plan's reimbursements account grows by that amount and the claim shows as
    reimbursed in the HostCover ledger from then on; the money is credited to the host's default
    payout method by the payout desk. Success is the receipt below; the entry is visible at once in
    the HostCover ledger lookup for the claim.

    Args:
        claim_id: Id class — the reference number of the approved property-damage claim being
            reimbursed, as returned by the damage-claim lookup for the host's HostCover plan.
        amount: Fixed-format class — the reimbursement Roamhaven pays on the claim, a positive USD
            amount with 2 decimal places (cents), already rounded to the cent; no currency symbol.

    Returns:
        A dict receipt: {"status": "reimbursement_booked" when the entry was written,
        "protection_event_id": the reference number of the new ledger entry (string),
        "claim_id": the property-damage claim reimbursed (string), "stay_id": the stay the claim
        arose from (string), "amount": the reimbursement booked in USD (number, 2 decimal places),
        "posted_date": the booking date YYYY-MM-DD}.
    """
    # Copy the linkage of the claim (plan, host, stay, verified loss) onto the ledger entry.
    rows = ctx.find("protection_claims", claim_id=claim_id)
    claim = rows[0] if rows else {}
    value = round(float(amount), 2)
    rid = ctx.make_id("pev_", "reimbursement", claim_id, value)
    posted = ctx.now()[:10]
    ctx.create("protection_events", rid, protection_event_id=rid,
               protection_plan_id=claim.get("protection_plan_id", ""),
               customer_id=claim.get("customer_id", ""), event_type="protect_reimbursement_paid",
               posted_date=posted, claim_id=claim_id, stay_id=claim.get("stay_id", ""),
               amount=value, premium_base_amount=0.0,
               verified_loss_amount=round(float(claim.get("verified_loss_amount") or 0), 2),
               guest_response="none", denial_reason="none")
    return str({"status": "reimbursement_booked", "protection_event_id": rid, "claim_id": claim_id,
                "stay_id": claim.get("stay_id", ""), "amount": value, "posted_date": posted})


@tool(owner="agent", rw="write")
def pay_pet_damage_reimbursement_a5391300(ctx: ToolContext, claim_id: str, amount: float) -> str:
    """Book the HostCover reimbursement Roamhaven pays the host on one approved pet-damage claim.

    One call records a single reimbursement entry on the HostCover ledger of the plan the pet-damage
    claim was filed under (damage by a guest's pet, a service animal included): the entry carries the
    claim, the stay the damage arose from, the loss the claims team verified on the claim, today's
    date and the reimbursement amount passed in. The plan's reimbursements account grows by that
    amount and the claim shows as reimbursed in the HostCover ledger; the money is credited to the
    host's default payout method by the payout desk. Success is the receipt below.

    Args:
        claim_id: Id class — the reference number of the approved pet-damage claim being reimbursed,
            as returned by the damage-claim lookup for the host's HostCover plan.
        amount: Fixed-format class — the reimbursement Roamhaven pays on the claim, a positive USD
            amount with 2 decimal places (cents), already rounded to the cent; no currency symbol.

    Returns:
        A dict receipt: {"status": "reimbursement_booked" when the entry was written,
        "protection_event_id": the reference number of the new ledger entry (string),
        "claim_id": the pet-damage claim reimbursed (string), "stay_id": the stay the claim arose
        from (string), "amount": the reimbursement booked in USD (number, 2 decimal places),
        "posted_date": the booking date YYYY-MM-DD}.
    """
    # Copy the linkage of the claim (plan, host, stay, verified loss) onto the ledger entry.
    rows = ctx.find("protection_claims", claim_id=claim_id)
    claim = rows[0] if rows else {}
    value = round(float(amount), 2)
    rid = ctx.make_id("pev_", "reimbursement", claim_id, value)
    posted = ctx.now()[:10]
    ctx.create("protection_events", rid, protection_event_id=rid,
               protection_plan_id=claim.get("protection_plan_id", ""),
               customer_id=claim.get("customer_id", ""), event_type="protect_reimbursement_paid",
               posted_date=posted, claim_id=claim_id, stay_id=claim.get("stay_id", ""),
               amount=value, premium_base_amount=0.0,
               verified_loss_amount=round(float(claim.get("verified_loss_amount") or 0), 2),
               guest_response="none", denial_reason="none")
    return str({"status": "reimbursement_booked", "protection_event_id": rid, "claim_id": claim_id,
                "stay_id": claim.get("stay_id", ""), "amount": value, "posted_date": posted})


@tool(owner="user", rw="write")
def accept_income_loss_settlement_ab094655(ctx: ToolContext, claim_id: str, amount: float) -> str:
    """Confirm, as the host, the bookings you had to cancel and accept the lost-income settlement on
    your approved income-loss claim.

    Lost-income settlements rest on the host's own cancelled bookings, so the host confirms them and
    accepts the settlement in person. One call records your confirmation and books the settlement as
    a reimbursement entry on the HostCover ledger of the plan the income-loss claim was filed under,
    with the claim, the stay whose damage caused the loss, the loss the claims team verified, today's
    date and the settlement amount you accept. The plan's reimbursements account grows by that
    amount, the claim shows as reimbursed in the HostCover ledger, and the money is credited to your
    default payout method by the payout desk. Success is the receipt below.

    Args:
        claim_id: Id class — the reference number of your approved income-loss claim, as the support
            agent reads it to you from the damage-claim records of your HostCover plan.
        amount: Fixed-format class — the lost-income settlement you accept, a positive USD amount with
            2 decimal places (cents), exactly as the support agent states it; no currency symbol.

    Returns:
        A dict receipt: {"status": "settlement_accepted" when your confirmation was recorded and the
        settlement booked, "protection_event_id": the reference number of the new ledger entry
        (string), "claim_id": the income-loss claim settled (string), "stay_id": the stay whose damage
        caused the loss (string), "amount": the settlement booked in USD (number, 2 decimal places),
        "posted_date": the booking date YYYY-MM-DD}.
    """
    # Copy the linkage of the claim (plan, host, stay, verified loss) onto the ledger entry.
    rows = ctx.find("protection_claims", claim_id=claim_id)
    claim = rows[0] if rows else {}
    value = round(float(amount), 2)
    rid = ctx.make_id("pev_", "reimbursement", claim_id, value)
    posted = ctx.now()[:10]
    ctx.create("protection_events", rid, protection_event_id=rid,
               protection_plan_id=claim.get("protection_plan_id", ""),
               customer_id=claim.get("customer_id", ""), event_type="protect_reimbursement_paid",
               posted_date=posted, claim_id=claim_id, stay_id=claim.get("stay_id", ""),
               amount=value, premium_base_amount=0.0,
               verified_loss_amount=round(float(claim.get("verified_loss_amount") or 0), 2),
               guest_response="none", denial_reason="none")
    return str({"status": "settlement_accepted", "protection_event_id": rid, "claim_id": claim_id,
                "stay_id": claim.get("stay_id", ""), "amount": value, "posted_date": posted})

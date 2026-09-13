"""Hidden task tools of the cargo_claims_desk difficulty (claims category).

Each tool performs exactly one atomic write on the claims records (cargo covers, the claims and
premium ledger, cargo claim files). None of them judges eligibility, status, time windows,
ownership or amounts: the caller decides those from the published rules and the records, and
passes the already-decided values in.
"""

from erlbench import ToolContext, tool


@tool(owner="agent", rw="write")
def approve_claim_settlement_060ed8c3(ctx: ToolContext, cover_id: str, claim_id: str, booking_id: str,
                                      container_number: str, amount_usd: float, liability_basis: str) -> str:
    """Approve one cargo claim for settlement at a stated amount and record which liability measure fixed that amount.

    The desk agent uses this on a claim file lodged under a cargo cover. One call books one settlement
    approval entry on the cover's premium and settlement account for the claim, dated today, marks the
    claim file as approved, and raises the cover's approved-but-unpaid settlement balance by the approved
    amount. Nothing is paid out by this call and the cover's status is left unchanged. On success the
    claimant can be told the approval reference, the amount approved and the recorded liability measure.

    Args:
        cover_id: Id class — cover reference number of the cargo liability or CargoCare cover the claim is lodged under, as returned by the cover lookup or the claim file lookup.
        claim_id: Id class — claim reference number of the claim file being approved, as returned by the claim file lookup.
        booking_id: Id class — booking reference number of the covered shipment the claim concerns, as returned by the booking lookup or shown on the cover.
        container_number: Fixed-format class — number of the container named in the claim file, in ISO 6346, 4 letters + 7 digits, written without spaces exactly as the claim file shows it.
        amount_usd: Fixed-format class — settlement amount approved for this claim, in USD, a non-negative number with 2 decimal places (the tool stores it rounded half-to-even to 2 decimal places); the unit is US dollars.
        liability_basis: Enum class — the liability measure that fixed the approved amount; one of package_limitation (the Hague-Visby per-package limit was the higher limit and capped the loss), weight_limitation (the Hague-Visby per-kilogram limit was the higher limit and capped the loss), declared_value (the declared value share of the affected packages capped the loss), proven_loss (no limit, share, cap or aggregate bound, so the approved amount is the proven loss after any uplift and deductible, including when the invoice value of the affected packages limited the proven loss), cover_limit (the product's per-container cover cap bound), delay_cap (a delay-loss cap bound), aggregate_limit (the annual aggregate still available on the cover reduced the amount), not_applicable (never correct for an approval; used only on premium and rejection entries).

    Returns:
        A dictionary with: status ("approved" when the approval entry was booked); approval_event_id (string reference of the new settlement approval entry); claim_id (the claim approved); cover_id (the cover charged with the settlement); booking_id (the booking of the covered shipment); container_number (the container of the claim, as given); amount_usd (number, USD with 2 decimal places, as booked); liability_basis (the recorded measure); settlement_payable_usd (number, USD with 2 decimal places, the cover's approved-but-unpaid settlement balance after this approval).
    """
    amount = round(float(amount_usd), 2)
    claim = (ctx.find("cargo_claims", claim_id=claim_id) or [{}])[0]
    cover = (ctx.find("cargo_covers", cover_id=cover_id) or [{}])[0]
    rid = ctx.make_id("cle_", cover_id, claim_id, booking_id, container_number, amount, liability_basis)
    ctx.create("claims_ledger", rid, claims_event_id=rid, cover_id=cover_id,
               customer_id=claim.get("customer_id", ""), event_type="claims_settlement_approved",
               event_date=ctx.now()[:10], amount_usd=amount, claim_id=claim_id,
               liability_basis=liability_basis, rejection_reason="not_applicable",
               payment_reference="", reference_event_id="")
    ctx.update("cargo_claims", claim_id, outcome="approved")
    payable = round(float(cover.get("settlement_payable_usd") or 0) + amount, 2)
    ctx.update("cargo_covers", cover_id, settlement_payable_usd=payable)
    return str({"status": "approved", "approval_event_id": rid, "claim_id": claim_id,
                "cover_id": cover_id, "booking_id": booking_id, "container_number": container_number,
                "amount_usd": amount, "liability_basis": liability_basis,
                "settlement_payable_usd": payable})


@tool(owner="agent", rw="write")
def close_cargo_claim_a3572c28(ctx: ToolContext, cover_id: str) -> str:
    """Close the decided claim that is open on a cargo cover, returning the cover from open-claim to closed-claim state.

    The desk agent uses this once a claim on the cover has been decided by settlement approval or by
    rejection. One call changes the cover's status to claim_closed; it books no money, changes no claim
    file and pays nothing. Afterwards the cover shows a closed claim and can take notice of a further loss
    on the same shipment.

    Args:
        cover_id: Id class — cover reference number of the cargo cover whose decided claim is being closed, as returned by the cover lookup.

    Returns:
        A dictionary with: status ("claim_closed" when the cover was updated); cover_id (the cover closed); cover_status (the cover's status after the call, claim_closed).
    """
    ctx.update("cargo_covers", cover_id, status="claim_closed")
    return str({"status": "claim_closed", "cover_id": cover_id, "cover_status": "claim_closed"})


@tool(owner="user", rw="write")
def lodge_cargo_claim_268664bf(ctx: ToolContext, cover_id: str, customer_id: str, container_number: str,
                               damage_type: str, damage_apparent_at_delivery: bool,
                               claimed_amount_usd: float, affected_package_count: int,
                               affected_weight_kg: float) -> str:
    """Lodge the claimant's own written notice of loss for one container under a cargo cover, opening a new claim file.

    The claimant uses this to give the line written notice of a loss. One call registers a new claim file
    under the cover for the named container, with the nature of the loss, whether it was apparent at
    delivery, the amount entered on the notice and the packages and weight affected; the notice is dated
    today and the file starts in the notice-registered state. The cover's status becomes claim_open. On
    success the claimant receives the claim reference to quote from now on.

    Args:
        cover_id: Id class — cover reference number of the cargo cover the notice is lodged under, as given to the claimant by the desk from the cover lookup.
        customer_id: Id class — customer reference number of the claimant lodging the notice, as given to the claimant by the desk from the customer profile lookup.
        container_number: Fixed-format class — number of the container in which the loss occurred, in ISO 6346, 4 letters + 7 digits, written without spaces, e.g. AHLU5123450.
        damage_type: Enum class — nature of the loss being notified; one of physical_damage (goods broken, crushed or otherwise physically damaged), wet_damage (goods damaged by water or moisture), temperature_damage (perishable goods damaged by the carrying temperature, such as thawed or warmed cargo), contamination (goods contaminated or tainted), shortage (packages missing from the container), total_loss (the whole container's goods lost), delay_loss (financial loss from late arrival of undamaged goods).
        damage_apparent_at_delivery: Enum class — whether the loss was visible when the cargo was delivered; one of true (the loss was apparent at delivery and noted on the delivery receipt), false (the loss was discovered only after delivery).
        claimed_amount_usd: Fixed-format class — amount entered on the notice as the loss claimed, in USD, a non-negative number with 2 decimal places (stored rounded half-to-even to 2 decimal places); the unit is US dollars.
        affected_package_count: Fixed-format class — number of packages lost or damaged, as an integer, packages (whole packages; the unit is packages).
        affected_weight_kg: Fixed-format class — gross weight of the lost or damaged goods, in decimal kilograms, 1 decimal place (stored rounded to 1 decimal place); the unit is kilograms.

    Returns:
        A dictionary with: status ("lodged" when the claim file was registered); claim_id (string claim reference of the new file); cover_id (the cover the claim sits under); notice_date (date the notice reached the line, YYYY-MM-DD); outcome (the file's state, notice_registered); cover_status (the cover's status after the call, claim_open).
    """
    amount = round(float(claimed_amount_usd), 2)
    weight = round(float(affected_weight_kg), 1)
    packages = int(affected_package_count)
    rid = ctx.make_id("ccl_", cover_id, customer_id, container_number, damage_type,
                      damage_apparent_at_delivery, amount, packages, weight)
    ctx.create("cargo_claims", rid, claim_id=rid, customer_id=customer_id, cover_id=cover_id,
               container_number=container_number, damage_type=damage_type,
               damage_apparent_at_delivery=bool(damage_apparent_at_delivery),
               notice_date=ctx.now()[:10], claimed_amount_usd=amount,
               affected_package_count=packages, affected_weight_kg=weight,
               outcome="notice_registered", created_at=ctx.now())
    ctx.update("cargo_covers", cover_id, status="claim_open")
    return str({"status": "lodged", "claim_id": rid, "cover_id": cover_id,
                "notice_date": ctx.now()[:10], "outcome": "notice_registered",
                "cover_status": "claim_open"})


@tool(owner="agent", rw="write")
def reject_cargo_claim_5f9631bd(ctx: ToolContext, cover_id: str, claim_id: str, rejection_reason: str) -> str:
    """Reject one cargo claim with a controlled reason, booking the rejection on the cover's claims account.

    The desk agent uses this to decide a claim by rejection. One call books one rejection entry of 0.00 USD
    on the cover's premium and settlement account for the claim, dated today, carrying the controlled
    reason and the claimant of the file, and marks the claim file as rejected. The cover's status is left
    unchanged. On success the claimant can be told the rejection reference and the reason.

    Args:
        cover_id: Id class — cover reference number of the cargo cover the claim is lodged under, as returned by the cover lookup or the claim file lookup.
        claim_id: Id class — claim reference number of the claim file being rejected, as returned by the claim file lookup or by the lodging receipt.
        rejection_reason: Enum class — controlled reason for the rejection; one of notice_out_of_time (written notice reached the line after the notice window for that kind of loss), claim_time_barred (notice reached the line after the claim time bar), excluded_peril (the survey found the claimant's insufficient packing or inherent vice caused the loss), not_covered_by_tier (the product does not pay this kind of loss, or temperature damage on a container whose reefer service rank is too low), no_logged_excursion (a temperature claim without the required logged excursion), misdeclared_cargo (the goods' dangerous-goods acceptance carries a misdeclaration penalty), below_minimum_claim (the amount is below the product's minimum claim), documents_not_submitted (the documents deadline passed without complete documents), claimant_not_entitled (the claimant is neither the cover holder nor an admitted named consignee), not_applicable (never correct for a rejection; used only on other entries).

    Returns:
        A dictionary with: status ("rejected" when the rejection entry was booked); rejection_event_id (string reference of the new rejection entry); claim_id (the claim rejected); cover_id (the cover); rejection_reason (the recorded reason); amount_usd (number, always 0.00 USD on a rejection).
    """
    claim = (ctx.find("cargo_claims", claim_id=claim_id) or [{}])[0]
    rid = ctx.make_id("cle_", cover_id, claim_id, rejection_reason)
    ctx.create("claims_ledger", rid, claims_event_id=rid, cover_id=cover_id,
               customer_id=claim.get("customer_id", ""), event_type="claims_claim_rejected",
               event_date=ctx.now()[:10], amount_usd=0.0, claim_id=claim_id,
               liability_basis="not_applicable", rejection_reason=rejection_reason,
               payment_reference="", reference_event_id="")
    ctx.update("cargo_claims", claim_id, outcome="rejected")
    return str({"status": "rejected", "rejection_event_id": rid, "claim_id": claim_id,
                "cover_id": cover_id, "rejection_reason": rejection_reason, "amount_usd": 0.0})


@tool(owner="agent", rw="write")
def bind_cargo_cover_f980fecc(ctx: ToolContext, cover_id: str, booking_id: str, customer_id: str,
                              insured_value_usd: float) -> str:
    """Bind a quoted cargo cover so that it attaches to the shipment, fixing the insured value it is bound for.

    The desk agent uses this on a cover still in the quoted state, at the cover holder's instruction. One call
    changes the cover's status from quoted to active, dates the binding today and records the insured value
    the cover is bound for, replacing the value carried on the quote. No premium is charged and nothing is
    paid by this call. On success the cover holder can be told the cover is in force, its binding date and
    the insured value bound.

    Args:
        cover_id: Id class — cover reference number of the quoted cover being bound, as returned by the cover lookup.
        booking_id: Id class — booking reference number of the shipment the cover attaches to, as returned by the booking lookup or shown on the cover.
        customer_id: Id class — customer reference number of the cover holder, as returned by the customer profile lookup.
        insured_value_usd: Fixed-format class — insured value the cover is bound for, in USD, a positive number with 2 decimal places (stored rounded to 2 decimal places); the unit is US dollars.

    Returns:
        A dictionary with: status ("bound" when the cover was updated); cover_id (the cover bound); cover_status (active); bound_date (binding date, YYYY-MM-DD); insured_value_usd (number, USD with 2 decimal places, the value bound).
    """
    value = round(float(insured_value_usd), 2)
    ctx.update("cargo_covers", cover_id, status="active", bound_date=ctx.now()[:10],
               insured_value_usd=value)
    return str({"status": "bound", "cover_id": cover_id, "cover_status": "active",
                "bound_date": ctx.now()[:10], "insured_value_usd": value})


@tool(owner="agent", rw="write")
def charge_cover_premium_8ce00127(ctx: ToolContext, cover_id: str, amount_usd: float) -> str:
    """Charge the premium of a bound cargo cover to the cover's premium account.

    The desk agent uses this to book the premium of a cover. One call books one premium charge entry on the
    cover's premium and settlement account, dated today, and raises the cover's unpaid premium balance by the
    amount charged. Nothing is paid and the cover's status is unchanged. On success the cover holder can be told
    the premium charged and the premium now due.

    Args:
        cover_id: Id class — cover reference number of the cover whose premium is charged, as returned by the cover lookup.
        amount_usd: Fixed-format class — premium charged, in USD, a non-negative number with 2 decimal places (stored rounded to 2 decimal places); the unit is US dollars.

    Returns:
        A dictionary with: status ("charged" when the premium entry was booked); premium_event_id (string reference of the new premium charge entry); cover_id (the cover charged); amount_usd (number, USD with 2 decimal places, as booked); premium_due_usd (number, USD with 2 decimal places, the cover's unpaid premium after the charge).
    """
    amount = round(float(amount_usd), 2)
    cover = (ctx.find("cargo_covers", cover_id=cover_id) or [{}])[0]
    rid = ctx.make_id("cle_", cover_id, "premium", amount)
    ctx.create("claims_ledger", rid, claims_event_id=rid, cover_id=cover_id,
               customer_id=cover.get("customer_id", ""), event_type="claims_premium_charged",
               event_date=ctx.now()[:10], amount_usd=amount, claim_id=None,
               liability_basis="not_applicable", rejection_reason="not_applicable",
               payment_reference="", reference_event_id=None)
    due = round(float(cover.get("premium_due_usd") or 0) + amount, 2)
    ctx.update("cargo_covers", cover_id, premium_due_usd=due)
    return str({"status": "charged", "premium_event_id": rid, "cover_id": cover_id,
                "amount_usd": amount, "premium_due_usd": due})


@tool(owner="user", rw="write")
def pay_cover_premium_9f1f968f(ctx: ToolContext, cover_id: str, amount_usd: float, payment_reference: str) -> str:
    """Pay premium owed on one's own cargo cover now, from the cover holder's account, quoting the holder's own remittance reference.

    The cover holder uses this to settle premium on its cover during the call. One call books one premium
    payment entry on the cover's premium and settlement account, dated today, carrying the holder's reference,
    and lowers the cover's unpaid premium balance by the amount paid. On success the holder receives the
    payment entry reference and the premium still due afterwards.

    Args:
        cover_id: Id class — cover reference number of the cover whose premium is paid, as given to the cover holder by the desk from the cover lookup.
        amount_usd: Fixed-format class — amount of premium paid, in USD, a positive number with 2 decimal places (stored rounded to 2 decimal places); the unit is US dollars.
        payment_reference: Verbatim class — the cover holder's own remittance reference for this payment, exactly as the holder states it; copy it character for character, keeping letters, digits, hyphens and case, with no translation, normalisation, summarising, adding or dropping of characters (verbatim).

    Returns:
        A dictionary with: status ("paid" when the payment entry was booked); payment_event_id (string reference of the new premium payment entry); cover_id (the cover paid); amount_usd (number, USD with 2 decimal places, as booked); payment_reference (the reference recorded); premium_due_usd (number, USD with 2 decimal places, the cover's unpaid premium after the payment).
    """
    amount = round(float(amount_usd), 2)
    cover = (ctx.find("cargo_covers", cover_id=cover_id) or [{}])[0]
    rid = ctx.make_id("cle_", cover_id, amount, payment_reference)
    ctx.create("claims_ledger", rid, claims_event_id=rid, cover_id=cover_id,
               customer_id=cover.get("customer_id", ""), event_type="claims_premium_paid",
               event_date=ctx.now()[:10], amount_usd=amount, claim_id=None,
               liability_basis="not_applicable", rejection_reason="not_applicable",
               payment_reference=payment_reference, reference_event_id=None)
    due = round(float(cover.get("premium_due_usd") or 0) - amount, 2)
    ctx.update("cargo_covers", cover_id, premium_due_usd=due)
    return str({"status": "paid", "payment_event_id": rid, "cover_id": cover_id, "amount_usd": amount,
                "payment_reference": payment_reference, "premium_due_usd": due})

"""Hidden task tools for the Wanderlane car rental desk (difficulty: car_rental_desk).

Each function below is a TASK tool: it never appears in a tool list, its name is registered
only in drive.extended.yaml as an extended policy's target_tool, and it is reached through the
unlock/call meta tools. Every tool performs one atomic write with the arguments as given and
makes no eligibility, ordering or entitlement judgement of its own.
"""

from erlbench import ToolContext, tool


@tool(owner="user", rw="write")
def confirm_cancellation_charge_358c6472(ctx: ToolContext, drive_rental_id: str, customer_id: str,
                                         source_entry_id: str, cancellation_charge_usd: float) -> str:
    """Record the renter's own confirmation of the charge the rate class keeps back for the car
    rental they have given up. One call books a single charge line on that rental for the amount
    confirmed, marks it as arising from the renter giving the rental up, and points it at the
    advance payment the money is held back from, so the rental's net charged total rises by the
    amount confirmed and the renter can see the charge standing against the rental. The renter
    runs this themselves; the money is kept back from what they have already paid rather than
    billed to them again.

    Args:
        drive_rental_id: Id class — the internal reference number of the car rental the charge is
            booked against, read from the rental record returned by the car rental lookup.
        customer_id: Id class — the traveller reference number of the renter the charge belongs to,
            read from the traveller profile returned by the profile lookup.
        source_entry_id: Id class — the reference number of the advance payment line on that rental
            that the charge is kept back from, read from the rental ledger lookup.
        cancellation_charge_usd: Fixed-format class — the amount kept back, as a US dollar amount
            with 2 decimal places, rounded half up to the cent at the moment it is booked; it is
            given as a positive figure and is never left empty.

    Returns:
        A confirmation sentence naming the reference number of the new charge line, the rental it
        was booked against and the amount kept back in US dollars to 2 decimal places. A sentence
        of that shape means the line is on the rental's ledger; any other reply means nothing was
        booked.
    """
    rid = ctx.make_id("dce_", drive_rental_id, customer_id, source_entry_id, cancellation_charge_usd)
    amount = round(float(cancellation_charge_usd), 2)
    ctx.create("drive_rental_entries", rid,
               drive_entry_id=rid,
               drive_rental_id=drive_rental_id,
               customer_id=customer_id,
               event_type="drive_cancellation_charge",
               charge_category="cancellation_fee",
               amount_usd=amount,
               currency_charged="USD",
               rental_day_sequence=0,
               driver_sequence=0,
               item_sequence=0,
               miles_delta=0,
               posted_date=ctx.now()[:10],
               posted_at=ctx.now(),
               payment_channel="call_centre",
               source_entry_id=source_entry_id,
               damage_reference="",
               toll_reference="",
               notice_reference="",
               reason_code="renter_cancellation")
    return (f"Cancellation charge line {rid} booked on rental {drive_rental_id} for "
            f"{amount:.2f} USD kept back from advance payment {source_entry_id}.")


@tool(owner="agent", rw="write")
def post_cancellation_refund_344e0f66(ctx: ToolContext, drive_rental_id: str, customer_id: str,
                                      source_entry_id: str, refund_amount_usd: float) -> str:
    """Return money to the card that paid for a car rental. One call books a single payout line on
    that rental against the earlier payment line being reversed, so the amount leaves the rental's
    net charged total and reaches the renter's original card, and the renter can see the payout
    standing on the rental alongside the payment it reverses. The desk performs this for the
    renter; the payout line is recorded as money going out, not as a further charge.

    Args:
        drive_rental_id: Id class — the internal reference number of the car rental the payout is
            booked against, read from the rental record returned by the car rental lookup.
        customer_id: Id class — the traveller reference number of the renter the money is returned
            to, read from the traveller profile returned by the profile lookup.
        source_entry_id: Id class — the reference number of the earlier payment line on that rental
            that this payout reverses, read from the rental ledger lookup.
        refund_amount_usd: Fixed-format class — the amount returned, as a US dollar amount with 2
            decimal places, rounded half up to the cent at the moment it is booked; it is given as
            a positive figure and recorded as money leaving the rental, and is never left empty.

    Returns:
        A confirmation sentence naming the reference number of the new payout line, the rental it
        was booked against, the amount returned in US dollars to 2 decimal places and the payment
        line it reverses. A sentence of that shape means the payout is on the rental's ledger; any
        other reply means nothing was returned.
    """
    rid = ctx.make_id("drf_", drive_rental_id, customer_id, source_entry_id, refund_amount_usd)
    amount = round(float(refund_amount_usd), 2)
    ctx.create("drive_rental_entries", rid,
               drive_entry_id=rid,
               drive_rental_id=drive_rental_id,
               customer_id=customer_id,
               event_type="drive_refund_payout",
               charge_category="refund_payout",
               amount_usd=-amount,
               currency_charged="USD",
               rental_day_sequence=0,
               driver_sequence=0,
               item_sequence=0,
               miles_delta=0,
               posted_date=ctx.now()[:10],
               posted_at=ctx.now(),
               payment_channel="call_centre",
               source_entry_id=source_entry_id,
               damage_reference="",
               toll_reference="",
               notice_reference="",
               reason_code="renter_cancellation")
    return (f"Refund payout line {rid} booked on rental {drive_rental_id} returning "
            f"{amount:.2f} USD to the card, against payment line {source_entry_id}.")


@tool(owner="agent", rw="write")
def post_damage_recharge_2d59c35f(ctx: ToolContext, drive_rental_id: str, customer_id: str,
                                  drive_review_id: str, damage_reference: str,
                                  damage_recharge_usd: float) -> str:
    """Recharge to the renter the damage the rental desk has assessed on a car rental. One call books
    a single damage line on that rental for the amount given, quoting the supplier's own reference for
    the incident it settles, so the rental's net charged total rises by that amount and the renter can
    see the damage standing against the rental with the reference it was assessed under. The desk does
    this for the renter; the line is a charge to the renter and not a payment by them.

    Args:
        drive_rental_id: Id class — the internal reference number of the car rental the damage is
            recharged against, read from the rental record returned by the car rental lookup.
        customer_id: Id class — the traveller reference number of the renter being recharged, read
            from the traveller profile returned by the profile lookup.
        drive_review_id: Id class — the reference number of the rental damage review the desk decided
            for this incident, read from the rental damage review lookup; one damage line is booked per
            review reference.
        damage_reference: Verbatim class — the supplier's own reference for the damaged vehicle as it
            is recorded on that rental damage review, copied character for character with the original
            wording, digits and punctuation kept, and nothing translated, tidied, shortened or added (verbatim).
        damage_recharge_usd: Fixed-format class — the amount recharged, as a US dollar amount with 2
            decimal places, rounded half up to the cent at the moment it is booked; it is given as a
            positive figure and is never left empty.

    Returns:
        A confirmation sentence naming the reference number of the new damage line, the rental it was
        booked against, the amount recharged in US dollars to 2 decimal places and the supplier
        reference it settles. A sentence of that shape means the line is on the rental's ledger; any
        other reply means nothing was recharged.
    """
    rid = ctx.make_id("ddc_", drive_rental_id, customer_id, drive_review_id, damage_recharge_usd)
    amount = round(float(damage_recharge_usd), 2)
    ctx.create("drive_rental_entries", rid,
               drive_entry_id=rid,
               drive_rental_id=drive_rental_id,
               customer_id=customer_id,
               event_type="drive_damage_charge",
               charge_category="damage_charge",
               amount_usd=amount,
               currency_charged="USD",
               rental_day_sequence=0,
               driver_sequence=0,
               item_sequence=0,
               miles_delta=0,
               posted_date=ctx.now()[:10],
               posted_at=ctx.now(),
               payment_channel="call_centre",
               source_entry_id="",
               damage_reference=damage_reference,
               toll_reference="",
               notice_reference="",
               reason_code="damage_assessment")
    return (f"Damage recharge line {rid} booked on rental {drive_rental_id} for {amount:.2f} USD "
            f"against supplier damage reference {damage_reference}.")


@tool(owner="user", rw="write")
def raise_recharge_dispute_65c619e1(ctx: ToolContext, drive_rental_id: str, customer_id: str,
                                    drive_review_id: str, evidence_reference: str,
                                    disputed_amount_usd: float) -> str:
    """Put a recharge on a car rental in dispute in the renter's own name. One call registers a fresh
    damage review against that rental in the renter's name, standing as submitted and undecided, with
    the amount the renter is challenging and the reference of the evidence they are relying on, so the
    rental desk has the challenge on its list and the renter can see it open against the rental while
    the amount stays on the ledger. The renter raises this themselves; it changes no charge and returns
    no money on its own.

    Args:
        drive_rental_id: Id class — the internal reference number of the car rental the challenge is
            raised against, read from the rental record returned by the car rental lookup.
        customer_id: Id class — the traveller reference number of the renter raising the challenge,
            read from the traveller profile returned by the profile lookup.
        drive_review_id: Id class — the reference number of the rental damage review the desk already
            decided on this incident, read from the rental damage review lookup; one challenge is
            registered per decided review reference.
        evidence_reference: Verbatim class — the reference of the evidence the renter is relying on,
            taken from what the renter reads out in this conversation and copied character for
            character with the original wording, digits, spacing and punctuation kept, and nothing
            translated, tidied, shortened or added (verbatim).
        disputed_amount_usd: Fixed-format class — the amount being challenged, as a US dollar amount
            with 2 decimal places, rounded half up to the cent at the moment it is registered; it is
            given as a positive figure and is never left empty.

    Returns:
        A confirmation sentence naming the reference number of the challenge registered, the rental it
        stands against, the amount challenged in US dollars to 2 decimal places and the evidence
        reference recorded with it. A sentence of that shape means the challenge is open with the
        rental desk; any other reply means nothing was registered.
    """
    rid = ctx.make_id("drv_", drive_rental_id, customer_id, drive_review_id, disputed_amount_usd)
    amount = round(float(disputed_amount_usd), 2)
    ctx.create("drive_damage_reviews", rid,
               drive_review_id=rid,
               customer_id=customer_id,
               drive_rental_id=drive_rental_id,
               review_type="damage_assessment",
               review_status="submitted",
               submitted_at=ctx.now(),
               decided_at="",
               disputed_amount_usd=amount,
               evidence_reference=evidence_reference)
    return (f"Challenge {rid} registered against rental {drive_rental_id} for {amount:.2f} USD, "
            f"recorded with evidence reference {evidence_reference}.")

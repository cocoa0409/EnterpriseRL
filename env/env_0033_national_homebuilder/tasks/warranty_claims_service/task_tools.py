"""Hidden task tools of the warranty_claims_service difficulty (Calloway Limited Home Warranty).

Each tool performs exactly one atomic write on one homeowner's warranty coverage: it books one
homeowner charge or one payout entry with the figure it is given, and keeps the coverage's running
balance of charges owed or payouts approved in step with that entry. No tool works out a figure,
reads history to judge eligibility, or refuses because of the state of the coverage; those
judgements belong to the warranty desk and the homeowner, never to the tools.
"""

from erlbench import ToolContext, tool


@tool(owner="agent", rw="write")
def assess_missed_appointment_charge_27486c7f(ctx: ToolContext, coverage_id: str, claim_item_ref: str,
                                               amount: float) -> str:
    """Book a missed-appointment charge on one homeowner's Calloway Limited Home Warranty coverage.
    One call records one homeowner charge of the kind "missed appointment fee", dated today and linked
    to the claim item whose appointment the homeowner missed, prints a new charge number for the
    homeowner invoice, and adds the charged amount to the warranty charges the homeowner owes on that
    coverage. The homeowner can then see the new charge, with its charge number and amount, on the
    warranty invoice and in the coverage's charge history. A receipt with status "charge_booked" means
    the charge is on the coverage.

    Args:
        coverage_id: Id class — the reference number of the homeowner's warranty coverage on the home,
            as returned by the warranty coverage lookup for this homeowner.
        claim_item_ref: Verbatim class — the service request item number of the claim item whose
            appointment was missed, copied character for character, digits and hyphens included, exactly
            as it is printed on the homeowner's service request and shown in the coverage's warranty
            history, with no reformatting (verbatim).
        amount: Fixed-format class — the charge amount in USD, a positive number with 2 decimal places
            (cents), already rounded to the nearest cent; no currency sign or thousands
            separator.

    Returns:
        A dictionary rendered as text with: status ("charge_booked" when the charge was recorded),
        warranty_event_id (reference number of the new charge entry), charge_reference (the charge
        number printed on the homeowner invoice, text such as WCH-51234), coverage_id (the coverage
        charged), claim_item_ref (the item the charge is linked to), charge_type (always
        missed_appointment_fee), amount (USD, 2 decimal places), event_date (the assessment date,
        YYYY-MM-DD) and charges_due (the homeowner's warranty charges owed on the coverage including this
        charge, USD, 2 decimal places).
    """
    amount = round(float(amount), 2)
    rid = ctx.make_id("wev_", "missed_appointment_fee", coverage_id, claim_item_ref, amount)
    ref = f"WCH-5{int(rid[-8:], 16) % 10000:04d}"
    cov = ctx.find("warranty_coverages", coverage_id=coverage_id)
    customer_id = cov[0].get("customer_id") if cov else None
    today = ctx.now()[:10]
    ctx.create("warranty_events", rid, warranty_event_id=rid, coverage_id=coverage_id,
               customer_id=customer_id, event_type="warranty_charge_assessed",
               charge_type="missed_appointment_fee", charge_reference=ref,
               claim_item_ref=claim_item_ref, amount=amount, event_date=today)
    due = round(float((cov[0].get("charges_due") if cov else 0) or 0) + amount, 2)
    if cov:
        ctx.update("warranty_coverages", coverage_id, charges_due=due)
    return str({"status": "charge_booked", "warranty_event_id": rid, "charge_reference": ref,
                "coverage_id": coverage_id, "claim_item_ref": claim_item_ref,
                "charge_type": "missed_appointment_fee", "amount": amount, "event_date": today,
                "charges_due": due})


@tool(owner="user", rw="write")
def accept_finish_item_cash_settlement_135d939d(ctx: ToolContext, coverage_id: str, claim_item_ref: str,
                                                amount: float) -> str:
    """Record the homeowner's own written acceptance of a cash settlement in place of Calloway repairing
    a covered finish (workmanship) claim item on their warranty coverage. One call records one approved
    payout of the kind "cash in lieu" for that claim item, dated today, prints a new payout number, and
    adds the accepted amount to the payouts Calloway owes the homeowner on that coverage; the item is
    thereby closed without repair. The homeowner can then see the approved payout, with its payout
    number and amount, in the coverage's payout history. A receipt with status "settlement_accepted"
    means the acceptance is on file.

    Args:
        coverage_id: Id class — the reference number of the homeowner's own warranty coverage on the home,
            as given to the homeowner by the warranty desk from the coverage lookup.
        claim_item_ref: Verbatim class — the service request item number of the finish item being
            settled, copied character for character, digits and hyphens included, exactly as it is printed
            on the homeowner's service request, with no reformatting (verbatim).
        amount: Fixed-format class — the cash settlement amount the homeowner accepts, in USD, a positive
            number with 2 decimal places (cents), already rounded to the nearest cent; no
            currency sign or thousands separator.

    Returns:
        A dictionary rendered as text with: status ("settlement_accepted" when the acceptance was
        recorded), warranty_event_id (reference number of the new payout entry), payout_reference (the
        payout number, text such as WPO-51234), coverage_id (the coverage the payout belongs to),
        claim_item_ref (the item settled and closed), payout_type (always cash_in_lieu), amount (USD,
        2 decimal places), event_date (the acceptance date, YYYY-MM-DD) and payouts_owed (approved
        payouts not yet paid on the coverage including this acceptance, USD, 2 decimal places).
    """
    amount = round(float(amount), 2)
    rid = ctx.make_id("wev_", "cash_in_lieu", coverage_id, claim_item_ref, amount)
    ref = f"WPO-5{int(rid[-8:], 16) % 10000:04d}"
    cov = ctx.find("warranty_coverages", coverage_id=coverage_id)
    customer_id = cov[0].get("customer_id") if cov else None
    today = ctx.now()[:10]
    ctx.create("warranty_events", rid, warranty_event_id=rid, coverage_id=coverage_id,
               customer_id=customer_id, event_type="warranty_payout_approved",
               payout_type="cash_in_lieu", payout_reference=ref,
               claim_item_ref=claim_item_ref, amount=amount, event_date=today)
    owed = round(float((cov[0].get("payouts_owed") if cov else 0) or 0) + amount, 2)
    if cov:
        ctx.update("warranty_coverages", coverage_id, payouts_owed=owed)
    return str({"status": "settlement_accepted", "warranty_event_id": rid, "payout_reference": ref,
                "coverage_id": coverage_id, "claim_item_ref": claim_item_ref,
                "payout_type": "cash_in_lieu", "amount": amount, "event_date": today,
                "payouts_owed": owed})


@tool(owner="agent", rw="write")
def assess_reinspection_charge_a99ab20e(ctx: ToolContext, coverage_id: str, claim_item_ref: str,
                                        amount: float) -> str:
    """Book a reinspection charge on one homeowner's Calloway Limited Home Warranty coverage for a
    re-reported crack item that the re-measurement found within tolerance again. One call records one
    homeowner charge of the kind "reinspection fee", dated today and linked to the re-reported claim item,
    prints a new charge number for the homeowner invoice, and adds the charged amount to the warranty
    charges the homeowner owes on that coverage. The homeowner can then see the new charge, with its
    charge number and amount, on the warranty invoice and in the coverage's charge history. A receipt with
    status "charge_booked" means the charge is on the coverage.

    Args:
        coverage_id: Id class — the reference number of the homeowner's warranty coverage on the home,
            as returned by the warranty coverage lookup for this homeowner.
        claim_item_ref: Verbatim class — the service request item number of the re-reported crack item
            that was re-measured, copied character for character, digits and hyphens included, exactly as
            it is shown in the coverage's warranty history, with no reformatting (verbatim).
        amount: Fixed-format class — the charge amount in USD, a positive number with 2 decimal places
            (cents), already rounded to the nearest cent; no currency sign or thousands separator.

    Returns:
        A dictionary rendered as text with: status ("charge_booked" when the charge was recorded),
        warranty_event_id (reference number of the new charge entry), charge_reference (the charge
        number printed on the homeowner invoice, text such as WCH-51234), coverage_id (the coverage
        charged), claim_item_ref (the item the charge is linked to), charge_type (always
        reinspection_fee), amount (USD, 2 decimal places), event_date (the assessment date, YYYY-MM-DD)
        and charges_due (the homeowner's warranty charges owed on the coverage including this charge, USD,
        2 decimal places).
    """
    amount = round(float(amount), 2)
    rid = ctx.make_id("wev_", "reinspection_fee", coverage_id, claim_item_ref, amount)
    ref = f"WCH-5{int(rid[-8:], 16) % 10000:04d}"
    cov = ctx.find("warranty_coverages", coverage_id=coverage_id)
    customer_id = cov[0].get("customer_id") if cov else None
    today = ctx.now()[:10]
    ctx.create("warranty_events", rid, warranty_event_id=rid, coverage_id=coverage_id,
               customer_id=customer_id, event_type="warranty_charge_assessed",
               charge_type="reinspection_fee", charge_reference=ref,
               claim_item_ref=claim_item_ref, amount=amount, event_date=today)
    due = round(float((cov[0].get("charges_due") if cov else 0) or 0) + amount, 2)
    if cov:
        ctx.update("warranty_coverages", coverage_id, charges_due=due)
    return str({"status": "charge_booked", "warranty_event_id": rid, "charge_reference": ref,
                "coverage_id": coverage_id, "claim_item_ref": claim_item_ref,
                "charge_type": "reinspection_fee", "amount": amount, "event_date": today,
                "charges_due": due})


@tool(owner="agent", rw="write")
def assess_emergency_dispatch_charge_91903470(ctx: ToolContext, coverage_id: str, claim_item_ref: str,
                                              amount: float) -> str:
    """Book an emergency dispatch charge on one homeowner's Calloway Limited Home Warranty coverage for a
    technician dispatch to an emergency item that was not a covered defect. One call records one homeowner
    charge of the kind "emergency dispatch fee", dated today and linked to the dispatched claim item, prints
    a new charge number for the homeowner invoice, and adds the charged amount to the warranty charges the
    homeowner owes on that coverage. The homeowner can then see the new charge, with its charge number and
    amount, on the warranty invoice and in the coverage's charge history. A receipt with status
    "charge_booked" means the charge is on the coverage.

    Args:
        coverage_id: Id class — the reference number of the homeowner's warranty coverage on the home,
            as returned by the warranty coverage lookup for this homeowner.
        claim_item_ref: Verbatim class — the service request item number of the emergency item the
            technician was dispatched to, copied character for character, digits and hyphens included,
            exactly as it is shown in the coverage's warranty history, with no reformatting (verbatim).
        amount: Fixed-format class — the charge amount in USD, a positive number with 2 decimal places
            (cents), already rounded to the nearest cent; no currency sign or thousands separator.

    Returns:
        A dictionary rendered as text with: status ("charge_booked" when the charge was recorded),
        warranty_event_id (reference number of the new charge entry), charge_reference (the charge
        number printed on the homeowner invoice, text such as WCH-51234), coverage_id (the coverage
        charged), claim_item_ref (the item the charge is linked to), charge_type (always
        emergency_dispatch_fee), amount (USD, 2 decimal places), event_date (the assessment date,
        YYYY-MM-DD) and charges_due (the homeowner's warranty charges owed on the coverage including this
        charge, USD, 2 decimal places).
    """
    amount = round(float(amount), 2)
    rid = ctx.make_id("wev_", "emergency_dispatch_fee", coverage_id, claim_item_ref, amount)
    ref = f"WCH-5{int(rid[-8:], 16) % 10000:04d}"
    cov = ctx.find("warranty_coverages", coverage_id=coverage_id)
    customer_id = cov[0].get("customer_id") if cov else None
    today = ctx.now()[:10]
    ctx.create("warranty_events", rid, warranty_event_id=rid, coverage_id=coverage_id,
               customer_id=customer_id, event_type="warranty_charge_assessed",
               charge_type="emergency_dispatch_fee", charge_reference=ref,
               claim_item_ref=claim_item_ref, amount=amount, event_date=today)
    due = round(float((cov[0].get("charges_due") if cov else 0) or 0) + amount, 2)
    if cov:
        ctx.update("warranty_coverages", coverage_id, charges_due=due)
    return str({"status": "charge_booked", "warranty_event_id": rid, "charge_reference": ref,
                "coverage_id": coverage_id, "claim_item_ref": claim_item_ref,
                "charge_type": "emergency_dispatch_fee", "amount": amount, "event_date": today,
                "charges_due": due})


@tool(owner="user", rw="write")
def accept_systems_item_cash_settlement_9ecd6f20(ctx: ToolContext, coverage_id: str, claim_item_ref: str,
                                                 amount: float) -> str:
    """Record the homeowner's own written acceptance of a cash settlement in place of Calloway repairing
    a covered systems (plumbing, electrical or hvac) claim item on their warranty coverage. One call
    records one approved payout of the kind "cash in lieu" for that claim item, dated today, prints a new
    payout number, and adds the accepted amount to the payouts Calloway owes the homeowner on that
    coverage; the item is thereby closed without repair. The homeowner can then see the approved payout,
    with its payout number and amount, in the coverage's payout history. A receipt with status
    "settlement_accepted" means the acceptance is on file.

    Args:
        coverage_id: Id class — the reference number of the homeowner's own warranty coverage on the home,
            as given to the homeowner by the warranty desk from the coverage lookup.
        claim_item_ref: Verbatim class — the service request item number of the systems item being
            settled, copied character for character, digits and hyphens included, exactly as it is printed
            on the homeowner's service request, with no reformatting (verbatim).
        amount: Fixed-format class — the cash settlement amount the homeowner accepts, in USD, a positive
            number with 2 decimal places (cents), already rounded to the nearest cent; no currency sign or
            thousands separator.

    Returns:
        A dictionary rendered as text with: status ("settlement_accepted" when the acceptance was
        recorded), warranty_event_id (reference number of the new payout entry), payout_reference (the
        payout number, text such as WPO-51234), coverage_id (the coverage the payout belongs to),
        claim_item_ref (the item settled and closed), payout_type (always cash_in_lieu), amount (USD,
        2 decimal places), event_date (the acceptance date, YYYY-MM-DD) and payouts_owed (approved
        payouts not yet paid on the coverage including this acceptance, USD, 2 decimal places).
    """
    amount = round(float(amount), 2)
    rid = ctx.make_id("wev_", "cash_in_lieu_systems", coverage_id, claim_item_ref, amount)
    ref = f"WPO-5{int(rid[-8:], 16) % 10000:04d}"
    cov = ctx.find("warranty_coverages", coverage_id=coverage_id)
    customer_id = cov[0].get("customer_id") if cov else None
    today = ctx.now()[:10]
    ctx.create("warranty_events", rid, warranty_event_id=rid, coverage_id=coverage_id,
               customer_id=customer_id, event_type="warranty_payout_approved",
               payout_type="cash_in_lieu", payout_reference=ref,
               claim_item_ref=claim_item_ref, amount=amount, event_date=today)
    owed = round(float((cov[0].get("payouts_owed") if cov else 0) or 0) + amount, 2)
    if cov:
        ctx.update("warranty_coverages", coverage_id, payouts_owed=owed)
    return str({"status": "settlement_accepted", "warranty_event_id": rid, "payout_reference": ref,
                "coverage_id": coverage_id, "claim_item_ref": claim_item_ref,
                "payout_type": "cash_in_lieu", "amount": amount, "event_date": today,
                "payouts_owed": owed})

"""Hidden task tools of the condo_coverage_changes difficulty (CondoGuard Unit-Owners Policy).

Each tool lands one midterm endorsement on a CondoGuard policy as one atomic business action: the
endorsement entry, the declarations change it makes, and the premium entry it posts to the premium
account. No tool checks eligibility, prerequisites or amounts; every figure is passed in as decided.
"""

from erlbench import ToolContext, tool


@tool(owner="agent", rw="write")
def raise_liability_limit_70984c5d(ctx: ToolContext, condo_policy_id: str, liability_limit: float,
                                   annual_premium_change: float, prorated_premium: float) -> dict:
    """Raise the personal liability limit on a CondoGuard unit-owners policy by a midterm liability
    endorsement effective today. One call records the liability endorsement (the new limit, its
    full-year premium effect and the premium charged for the rest of the term, marked as additional
    premium), sets the liability limit shown on the declarations to the new limit, and posts the
    charge as an additional-premium entry on the policy's premium account, raising the amount owed
    by that charge. On success the declarations show the new liability limit and the premium account
    shows the new charge. Success is a receipt whose status is "liability_raised".

    Args:
        condo_policy_id: Id class — the reference number of the CondoGuard policy being endorsed, as
            returned by the condo policy lookup for the verified customer.
        liability_limit: Fixed-format class — the new personal liability limit the declarations will
            show, in USD, 2 decimal places, stored exactly as passed.
        annual_premium_change: Fixed-format class — the full-year premium effect of the raise, in USD,
            2 decimal places, a positive amount; it is rounded half-up to the cent when stored.
        prorated_premium: Fixed-format class — the premium charged for the rest of the current term, in
            USD, 2 decimal places, a positive amount; it is rounded half-up to the cent when stored and
            posted as the additional-premium charge.

    Returns:
        A dict receipt: status (str, "liability_raised" when the endorsement landed),
        endorsement_id (str, reference number of the new endorsement entry), billing_id (str,
        reference number of the additional-premium entry), condo_policy_id (str, the policy endorsed),
        liability_limit (float, USD, the limit now on the declarations), effective_date (str,
        YYYY-MM-DD, today's date) and prorated_premium (float, USD, the charge posted).
    """
    today = ctx.now()[:10]
    rows = ctx.find("condo_policies", condo_policy_id=condo_policy_id)
    customer_id = rows[0].get("customer_id", "") if rows else ""
    term_start = rows[0].get("effective_date", "") if rows else ""
    balance = float(rows[0].get("premium_balance") or 0) if rows else 0.0
    eid = ctx.make_id("cgend_", condo_policy_id, "liability_change", liability_limit,
                      annual_premium_change, prorated_premium)
    ctx.create("condo_endorsements", eid, condo_endorsement_id=eid, condo_policy_id=condo_policy_id,
               customer_id=customer_id, event_type="condo_endorsement_added",
               endorsement_code="liability_change", request_date=today, effective_date=today,
               coverage_value=round(float(liability_limit), 2),
               annual_premium_change=round(float(annual_premium_change), 2),
               premium_direction="additional", prorated_premium=round(float(prorated_premium), 2))
    ctx.update("condo_policies", condo_policy_id, liability_limit=round(float(liability_limit), 2))
    bid = ctx.make_id("cgbill_", condo_policy_id, eid, "condo_additional_premium", prorated_premium)
    ctx.create("condo_billing", bid, condo_billing_id=bid, condo_policy_id=condo_policy_id,
               customer_id=customer_id, event_type="condo_additional_premium", posted_date=today,
               term_effective_date=term_start, installment_number=0, due_date="",
               amount=round(float(prorated_premium), 2), fee_code="none", payer="none",
               payment_method="none", payment_reference="", change_reason="endorsement",
               effective_date=today, credit_basis="none", source_billing_id="", source_endorsement_id=eid)
    ctx.update("condo_policies", condo_policy_id,
               premium_balance=round(balance + round(float(prorated_premium), 2), 2))
    return {"status": "liability_raised", "endorsement_id": eid, "billing_id": bid,
            "condo_policy_id": condo_policy_id, "liability_limit": round(float(liability_limit), 2),
            "effective_date": today, "prorated_premium": round(float(prorated_premium), 2)}


@tool(owner="user", rw="write")
def add_unit_rental_endorsement_60a857ee(ctx: ToolContext, condo_policy_id: str, annual_premium_change: float,
                                         prorated_premium: float) -> dict:
    """The named insured declares that their condominium unit is rented to others and signs the unit
    rental endorsement on their CondoGuard policy, effective today. One call records the unit rental
    endorsement (its full-year premium effect and the premium charged for the rest of the term, marked
    as additional premium), changes the occupancy shown on the declarations to rented to others, and
    posts the charge as an additional-premium entry on the policy's premium account, raising the
    amount owed by that charge. On success the declarations show the unit as rented to others with the
    rental endorsement in force. Success is a receipt whose status is "rental_endorsement_added".

    Args:
        condo_policy_id: Id class — the reference number of the insured's own CondoGuard policy, as the
            service representative reads it out from the policy record.
        annual_premium_change: Fixed-format class — the full-year premium of the unit rental endorsement
            as the representative quotes it, in USD, 2 decimal places, a positive amount; it is rounded
            half-up to the cent when stored.
        prorated_premium: Fixed-format class — the premium charged for the rest of the current term as
            the representative quotes it, in USD, 2 decimal places, a positive amount; it is rounded
            half-up to the cent when stored and posted as the additional-premium charge.

    Returns:
        A dict receipt: status (str, "rental_endorsement_added" when the endorsement landed),
        endorsement_id (str, reference number of the new endorsement entry), billing_id (str,
        reference number of the additional-premium entry), condo_policy_id (str, the policy endorsed),
        occupancy (str, "rented_to_others", the occupancy now on the declarations), effective_date
        (str, YYYY-MM-DD, today's date) and prorated_premium (float, USD, the charge posted).
    """
    today = ctx.now()[:10]
    rows = ctx.find("condo_policies", condo_policy_id=condo_policy_id)
    customer_id = rows[0].get("customer_id", "") if rows else ""
    term_start = rows[0].get("effective_date", "") if rows else ""
    balance = float(rows[0].get("premium_balance") or 0) if rows else 0.0
    eid = ctx.make_id("cgend_", condo_policy_id, "unit_rental", annual_premium_change, prorated_premium)
    ctx.create("condo_endorsements", eid, condo_endorsement_id=eid, condo_policy_id=condo_policy_id,
               customer_id=customer_id, event_type="condo_endorsement_added",
               endorsement_code="unit_rental", request_date=today, effective_date=today,
               coverage_value=0.00, annual_premium_change=round(float(annual_premium_change), 2),
               premium_direction="additional", prorated_premium=round(float(prorated_premium), 2))
    ctx.update("condo_policies", condo_policy_id, occupancy="rented_to_others")
    bid = ctx.make_id("cgbill_", condo_policy_id, eid, "condo_additional_premium", prorated_premium)
    ctx.create("condo_billing", bid, condo_billing_id=bid, condo_policy_id=condo_policy_id,
               customer_id=customer_id, event_type="condo_additional_premium", posted_date=today,
               term_effective_date=term_start, installment_number=0, due_date="",
               amount=round(float(prorated_premium), 2), fee_code="none", payer="none",
               payment_method="none", payment_reference="", change_reason="endorsement",
               effective_date=today, credit_basis="none", source_billing_id="", source_endorsement_id=eid)
    ctx.update("condo_policies", condo_policy_id,
               premium_balance=round(balance + round(float(prorated_premium), 2), 2))
    return {"status": "rental_endorsement_added", "endorsement_id": eid, "billing_id": bid,
            "condo_policy_id": condo_policy_id, "occupancy": "rented_to_others",
            "effective_date": today, "prorated_premium": round(float(prorated_premium), 2)}


@tool(owner="agent", rw="write")
def raise_coverage_a_minimum_ec3d8a44(ctx: ToolContext, condo_policy_id: str, coverage_a_limit: float,
                                      annual_premium_change: float, prorated_premium: float) -> dict:
    """Raise Coverage A (unit fixtures, improvements and betterments) on a CondoGuard unit-owners policy
    by a midterm Coverage A endorsement effective today. One call records the Coverage A endorsement
    (the new Coverage A limit, its full-year premium effect and the premium charged for the rest of
    the term, marked as additional premium), sets the Coverage A limit shown on the declarations to
    the new limit, and posts the charge as an additional-premium entry on the policy's premium
    account, raising the amount owed by that charge. On success the declarations show the new Coverage
    A limit and the premium account shows the new charge. Success is a receipt whose status is
    "coverage_a_raised".

    Args:
        condo_policy_id: Id class — the reference number of the CondoGuard policy being endorsed, as
            returned by the condo policy lookup for the verified customer.
        coverage_a_limit: Fixed-format class — the new Coverage A limit the declarations will show, in
            USD, 2 decimal places, stored exactly as passed.
        annual_premium_change: Fixed-format class — the full-year premium effect of the raise, in USD,
            2 decimal places, a positive amount; it is rounded half-up to the cent when stored.
        prorated_premium: Fixed-format class — the premium charged for the rest of the current term, in
            USD, 2 decimal places, a positive amount; it is rounded half-up to the cent when stored and
            posted as the additional-premium charge.

    Returns:
        A dict receipt: status (str, "coverage_a_raised" when the endorsement landed), endorsement_id
        (str, reference number of the new endorsement entry), billing_id (str, reference number of the
        additional-premium entry), condo_policy_id (str, the policy endorsed), coverage_a_limit (float,
        USD, the Coverage A now on the declarations), effective_date (str, YYYY-MM-DD, today's date)
        and prorated_premium (float, USD, the charge posted).
    """
    today = ctx.now()[:10]
    rows = ctx.find("condo_policies", condo_policy_id=condo_policy_id)
    customer_id = rows[0].get("customer_id", "") if rows else ""
    term_start = rows[0].get("effective_date", "") if rows else ""
    balance = float(rows[0].get("premium_balance") or 0) if rows else 0.0
    eid = ctx.make_id("cgend_", condo_policy_id, "coverage_a_change", coverage_a_limit,
                      annual_premium_change, prorated_premium)
    ctx.create("condo_endorsements", eid, condo_endorsement_id=eid, condo_policy_id=condo_policy_id,
               customer_id=customer_id, event_type="condo_endorsement_added",
               endorsement_code="coverage_a_change", request_date=today, effective_date=today,
               coverage_value=round(float(coverage_a_limit), 2),
               annual_premium_change=round(float(annual_premium_change), 2),
               premium_direction="additional", prorated_premium=round(float(prorated_premium), 2))
    ctx.update("condo_policies", condo_policy_id, coverage_a_limit=round(float(coverage_a_limit), 2))
    bid = ctx.make_id("cgbill_", condo_policy_id, eid, "condo_additional_premium", prorated_premium)
    ctx.create("condo_billing", bid, condo_billing_id=bid, condo_policy_id=condo_policy_id,
               customer_id=customer_id, event_type="condo_additional_premium", posted_date=today,
               term_effective_date=term_start, installment_number=0, due_date="",
               amount=round(float(prorated_premium), 2), fee_code="none", payer="none",
               payment_method="none", payment_reference="", change_reason="endorsement",
               effective_date=today, credit_basis="none", source_billing_id="", source_endorsement_id=eid)
    ctx.update("condo_policies", condo_policy_id,
               premium_balance=round(balance + round(float(prorated_premium), 2), 2))
    return {"status": "coverage_a_raised", "endorsement_id": eid, "billing_id": bid,
            "condo_policy_id": condo_policy_id, "coverage_a_limit": round(float(coverage_a_limit), 2),
            "effective_date": today, "prorated_premium": round(float(prorated_premium), 2)}


@tool(owner="user", rw="write")
def elect_deductible_raise_c9f31846(ctx: ToolContext, condo_policy_id: str, deductible: float,
                                    annual_premium_change: float, prorated_premium: float) -> dict:
    """The named insured signs an election raising the per-occurrence deductible on their own
    CondoGuard policy, effective today. One call records the deductible endorsement (the new
    deductible, its full-year premium effect and the premium credited for the rest of the term, marked
    as return premium), sets the deductible shown on the declarations to the new amount, and posts the
    credit as a pro-rata return-premium entry on the policy's premium account, lowering the amount
    owed by that credit. On success the declarations show the new deductible and the premium account
    shows the credit. Success is a receipt whose status is "deductible_raised".

    Args:
        condo_policy_id: Id class — the reference number of the insured's own CondoGuard policy, as the
            service representative reads it out from the policy record.
        deductible: Fixed-format class — the new per-occurrence deductible the insured elects, in USD,
            2 decimal places, stored exactly as passed.
        annual_premium_change: Fixed-format class — the full-year premium reduction of the higher
            deductible as the representative quotes it, in USD, 2 decimal places, a positive amount; it
            is rounded half-up to the cent when stored.
        prorated_premium: Fixed-format class — the premium credited for the rest of the current term as
            the representative quotes it, in USD, 2 decimal places, a positive amount; it is rounded
            half-up to the cent when stored and posted as the return-premium credit.

    Returns:
        A dict receipt: status (str, "deductible_raised" when the election landed), endorsement_id
        (str, reference number of the new endorsement entry), billing_id (str, reference number of the
        return-premium entry), condo_policy_id (str, the policy endorsed), deductible (float, USD, the
        deductible now on the declarations), effective_date (str, YYYY-MM-DD, today's date) and
        prorated_premium (float, USD, the credit posted).
    """
    today = ctx.now()[:10]
    rows = ctx.find("condo_policies", condo_policy_id=condo_policy_id)
    customer_id = rows[0].get("customer_id", "") if rows else ""
    term_start = rows[0].get("effective_date", "") if rows else ""
    balance = float(rows[0].get("premium_balance") or 0) if rows else 0.0
    eid = ctx.make_id("cgend_", condo_policy_id, "deductible_change", deductible,
                      annual_premium_change, prorated_premium)
    ctx.create("condo_endorsements", eid, condo_endorsement_id=eid, condo_policy_id=condo_policy_id,
               customer_id=customer_id, event_type="condo_endorsement_added",
               endorsement_code="deductible_change", request_date=today, effective_date=today,
               coverage_value=round(float(deductible), 2),
               annual_premium_change=round(float(annual_premium_change), 2),
               premium_direction="return", prorated_premium=round(float(prorated_premium), 2))
    ctx.update("condo_policies", condo_policy_id, deductible=round(float(deductible), 2))
    bid = ctx.make_id("cgbill_", condo_policy_id, eid, "condo_return_premium", prorated_premium)
    ctx.create("condo_billing", bid, condo_billing_id=bid, condo_policy_id=condo_policy_id,
               customer_id=customer_id, event_type="condo_return_premium", posted_date=today,
               term_effective_date=term_start, installment_number=0, due_date="",
               amount=round(float(prorated_premium), 2), fee_code="none", payer="none",
               payment_method="none", payment_reference="", change_reason="endorsement",
               effective_date=today, credit_basis="pro_rata", source_billing_id="", source_endorsement_id=eid)
    ctx.update("condo_policies", condo_policy_id,
               premium_balance=round(balance - round(float(prorated_premium), 2), 2))
    return {"status": "deductible_raised", "endorsement_id": eid, "billing_id": bid,
            "condo_policy_id": condo_policy_id, "deductible": round(float(deductible), 2),
            "effective_date": today, "prorated_premium": round(float(prorated_premium), 2)}

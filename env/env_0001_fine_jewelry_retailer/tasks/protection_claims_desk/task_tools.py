"""Hidden task tools for the Belrose protection and care desk.

Each function performs one atomic business action on a piece of protection coverage and is
reached only through the unlock/call meta tools; the names live in the desk's published
coverage rules, never in a tool list. Nothing here judges eligibility, aggregates history or
works out an amount: every figure arrives as an argument the agent has already worked out from
the coverage rules and the records.
"""

from erlbench import ToolContext, tool


@tool(owner="agent", rw="write")
def record_claim_settlement_8eb9093c(ctx: ToolContext, protection_plan_id: str, claim_reference: str,
                                     source_entry_id: str, benefit_amount: float,
                                     deductible_charged: float) -> str:
    """Accept a claim that stands open on a piece of protection coverage and book what it draws.

    One call answers one claim in full: a settlement entry is written against the coverage under
    the claim's own reference, carrying the benefit consumed as a movement out of the plan's
    benefit allowance, the out-of-pocket amount the customer bears on this claim, and a pointer
    back to the entry on which the loss was first entered, from which the piece, the kind of loss
    and the bench work order are carried over unchanged. The coverage's count of claims settled
    over its life goes up by one. Afterwards the customer can see the claim answered, the benefit
    drawn against it and what they are left to pay themselves.

    Args:
        protection_plan_id: Id class — the reference number of the coverage record the claim
            stands against, as returned by the protection coverage lookup.
        claim_reference: Fixed-format class — the reference the claim already carries, written as
            CL- followed by six digits, e.g. CL-330871; read it from the entry on which the loss
            was entered against this coverage.
        source_entry_id: Id class — the reference number of the coverage entry on which the loss
            was first entered, as returned by the coverage history lookup; the settlement is
            recorded as the answer to that entry.
        benefit_amount: Fixed-format class — the benefit this settlement consumes, given as a
            positive amount in USD to 2 decimal places, rounded half to even at the last step
            only; it is booked as a movement out of the benefit allowance.
        deductible_charged: Fixed-format class — what the customer pays out of pocket toward this
            settlement, in USD to 2 decimal places, rounded half to even; pass 0.00 where nothing
            is charged to them.

    Returns:
        A single confirmation line naming the reference number minted for the settlement entry,
        the claim reference it was booked under, the benefit consumed in USD and the out-of-pocket
        amount recorded, plus the coverage's new count of claims settled. The line being returned
        at all is what indicates the entry was written; afterwards the settlement appears in the
        coverage history under that claim reference.
    """
    filed = ctx.find("protection_ledger", protection_entry_id=source_entry_id)
    origin = filed[0] if filed else {}
    plans = ctx.find("protection_plans", protection_plan_id=protection_plan_id)
    plan = plans[0] if plans else {}
    settled_count = int(plan.get("claims_settled_count") or 0) + 1
    rid = ctx.make_id("psetl_", protection_plan_id, claim_reference, source_entry_id,
                      benefit_amount, deductible_charged)
    ctx.create("protection_ledger", rid, protection_entry_id=rid,
               protection_plan_id=protection_plan_id,
               customer_id=plan.get("customer_id", ""),
               event_type="protection_claim_settled",
               posted_date=ctx.now()[:10],
               amount=-round(float(benefit_amount), 2),
               claim_reference=claim_reference,
               claim_type=origin.get("claim_type", "not_applicable"),
               claim_outcome="settled_full",
               denial_reason_code="not_applicable",
               inspection_result="not_applicable",
               inspection_store_code="",
               deductible_charged=round(float(deductible_charged), 2),
               covered_item_sku=origin.get("covered_item_sku", ""),
               service_order_reference=origin.get("service_order_reference", ""),
               payment_channel="not_applicable",
               billing_period=ctx.now()[:7],
               source_entry_id=source_entry_id)
    ctx.update("protection_plans", protection_plan_id, claims_settled_count=settled_count)
    return (f"Settlement {rid} booked against claim {claim_reference}: benefit consumed "
            f"{round(float(benefit_amount), 2):.2f} USD, out of pocket "
            f"{round(float(deductible_charged), 2):.2f} USD; claims settled on this coverage: "
            f"{settled_count}.")


@tool(owner="user", rw="write")
def confirm_plan_cancellation_48603509(ctx: ToolContext, protection_plan_id: str, refund_amount: float,
                                       refund_channel: str) -> str:
    """Give up a piece of live protection coverage and take back the premium that is due.

    The customer runs this themselves, because ending cover they bought is theirs alone to do.
    One call closes the coverage as cancelled with today as its closing date, raises a
    cancellation on the protection desk's request record already marked as confirmed by the
    customer, and books the premium coming back as a movement out of what they have paid toward
    the plan, paid out on the channel they choose and pointed at the premium entry it gives back.
    Afterwards the coverage reads as cancelled, no further claim can be opened on it, and the
    money shows in the coverage history as premium returned.

    Args:
        protection_plan_id: Id class — the reference number of the coverage record being given
            up, as returned by the protection coverage lookup.
        refund_amount: Fixed-format class — the premium coming back to the customer, given as a
            positive amount in USD to 2 decimal places, rounded half to even at the last step
            only; pass 0.00 where nothing comes back.
        refund_channel: Enum class — how the customer wants the money returned, one of exactly
            these six values. Pass in_store where they will collect it at a Belrose counter;
            online_portal where it goes back to the card or account the customer manages on the
            Belrose website; phone_agent where it is taken back over the telephone on a card read
            out to the desk; mail_check where a cheque is posted to the address on the profile;
            autopay where it is credited to the standing arrangement the premium is collected on;
            and not_applicable where no money moves to the customer at all, which is the value to
            pass when the amount coming back is zero.

    Returns:
        A single confirmation line naming the coverage that was cancelled, the date it closed on,
        the reference number minted for the cancellation on the desk's request record, the
        reference number minted for the premium-returned entry, and the amount returned in USD.
        The line being returned at all is what indicates the cancellation took effect; afterwards
        the coverage record reads cancelled and the returned premium appears in its history.
    """
    plans = ctx.find("protection_plans", protection_plan_id=protection_plan_id)
    plan = plans[0] if plans else {}
    customer_id = plan.get("customer_id", "")
    amount = round(float(refund_amount), 2)
    premiums = ctx.find("protection_ledger", protection_plan_id=protection_plan_id,
                        event_type="protection_premium_paid")
    origin_entry = premiums[0].get("protection_entry_id", "") if premiums else ""
    request_id = ctx.make_id("preq_", protection_plan_id, "cancellation", amount)
    ctx.create("protection_intake", request_id, protection_request_id=request_id,
               customer_id=customer_id, protection_plan_id=protection_plan_id,
               request_type="cancellation", request_status="customer_confirmed",
               claim_reference="", effective_date=ctx.now()[:10], created_at=ctx.now())
    refund_id = ctx.make_id("pref_", protection_plan_id, amount, refund_channel)
    ctx.create("protection_ledger", refund_id, protection_entry_id=refund_id,
               protection_plan_id=protection_plan_id, customer_id=customer_id,
               event_type="protection_premium_refunded", posted_date=ctx.now()[:10],
               amount=-amount, claim_reference="", claim_type="not_applicable",
               claim_outcome="not_applicable", denial_reason_code="not_applicable",
               inspection_result="not_applicable", inspection_store_code="",
               deductible_charged=0.0, covered_item_sku=plan.get("covered_item_sku", ""),
               service_order_reference="", payment_channel=refund_channel,
               billing_period=ctx.now()[:7], source_entry_id=origin_entry)
    ctx.update("protection_plans", protection_plan_id, status="cancelled",
               closed_date=ctx.now()[:10],
               premium_paid_to_date=round(float(plan.get("premium_paid_to_date") or 0) - amount, 2))
    return (f"Coverage {protection_plan_id} cancelled on {ctx.now()[:10]}; cancellation "
            f"{request_id} confirmed by the customer and premium of {amount:.2f} USD returned on "
            f"entry {refund_id}.")


@tool(owner="agent", rw="write")
def record_claim_refusal_9dff8781(ctx: ToolContext, protection_plan_id: str, claim_reference: str,
                                  source_entry_id: str, refused_amount: float, claim_outcome: str,
                                  denial_reason_code: str) -> str:
    """Refuse a claim that stands open on a piece of protection coverage and record the ground for it.

    One call closes one claim without paying benefit: a refusal entry is written against the coverage under
    the claim's own reference, carrying the amount refused as a positive figure, the single ground the
    refusal rests on, the outcome the file is closed at, and a pointer back to the entry on which the loss
    was first entered, from which the piece and the kind of loss are carried over unchanged. No benefit
    allowance moves. Afterwards the customer can see the claim answered, the ground it was refused on, and
    the amount they are left to carry themselves.

    Args:
        protection_plan_id: Id class — the reference number of the coverage record the claim stands against,
            as returned by the protection coverage lookup.
        claim_reference: Fixed-format class — the reference the claim already carries, written as CL-
            followed by six digits, e.g. CL-330871; read it from the entry on which the loss was entered
            against this coverage.
        source_entry_id: Id class — the reference number of the coverage entry on which the loss was first
            entered, as returned by the coverage history lookup; the refusal is recorded as the answer to
            that entry.
        refused_amount: Fixed-format class — the amount being refused, given as a positive amount in USD to
            2 decimal places, rounded half to even at the last step only; pass 0.00 where nothing at all was
            being asked for.
        claim_outcome: Enum class — the outcome the claim is closed at, one of exactly these seven values.
            Pass settled_full where the claim was answered in full, or settled_partial where it was answered
            as far as the allowance reached, neither of which this refusal records; denied_exclusion where
            the peril claimed is one the coverage never answers for; denied_inspection_lapse where the loss
            fell in a spell when the coverage stood out of good standing for want of an inspection;
            denied_outside_term where the loss or the report of it fell outside the coverage's term;
            denied_allowance_exhausted where the plan's benefit allowance was already consumed; and
            not_applicable where the claim is still open and nothing has answered it.
        denial_reason_code: Enum class — the single ground recorded for refusing, one of exactly these six
            values. Pass excluded_peril where the coverage never answers for the peril claimed;
            inspection_lapse where the coverage stood out of good standing for a missed inspection when the
            loss happened; outside_term where the coverage's term had run out; allowance_exhausted where the
            benefit allowance was already consumed; no_proof_of_loss where the customer's account of the
            loss never came inside the window the coverage sets; and not_applicable where nothing is being
            refused at all.

    Returns:
        A single confirmation line naming the reference number minted for the refusal entry, the claim
        reference it was booked under, the amount refused in USD, the outcome recorded and the ground it
        rests on. The line being returned at all is what indicates the entry was written; afterwards the
        refusal appears in the coverage history under that claim reference.
    """
    filed = ctx.find("protection_ledger", protection_entry_id=source_entry_id)
    origin = filed[0] if filed else {}
    plans = ctx.find("protection_plans", protection_plan_id=protection_plan_id)
    plan = plans[0] if plans else {}
    rid = ctx.make_id("pden_", protection_plan_id, claim_reference, source_entry_id, refused_amount,
                      denial_reason_code)
    ctx.create("protection_ledger", rid, protection_entry_id=rid,
               protection_plan_id=protection_plan_id,
               customer_id=plan.get("customer_id", ""),
               event_type="protection_claim_denied",
               posted_date=ctx.now()[:10],
               amount=round(float(refused_amount), 2),
               claim_reference=claim_reference,
               claim_type=origin.get("claim_type", "not_applicable"),
               claim_outcome=claim_outcome,
               denial_reason_code=denial_reason_code,
               inspection_result="not_applicable",
               inspection_store_code="",
               deductible_charged=0.0,
               covered_item_sku=origin.get("covered_item_sku", ""),
               service_order_reference=origin.get("service_order_reference", ""),
               payment_channel="not_applicable",
               billing_period=ctx.now()[:7],
               source_entry_id=source_entry_id)
    return (f"Refusal {rid} booked against claim {claim_reference}: {round(float(refused_amount), 2):.2f} USD "
            f"refused, recorded as {claim_outcome} on the ground {denial_reason_code}.")


@tool(owner="agent", rw="write")
def reinstate_benefit_allowance_e0b143ff(ctx: ToolContext, protection_plan_id: str,
                                         allowance_amount: float) -> str:
    """Grant a coverage year's benefit allowance afresh on a piece of protection coverage.

    One call books one allowance entry against the coverage for the coverage year now running, carrying the
    benefit granted as a movement into the plan's benefit allowance and accounted to the period the grant is
    taken in. Nothing else on the coverage moves: no claim is answered and no premium changes. Afterwards
    the customer can see the year's benefit standing in the coverage history as an allowance reinstated.

    Args:
        protection_plan_id: Id class — the reference number of the coverage record the allowance is granted
            on, as returned by the protection coverage lookup.
        allowance_amount: Fixed-format class — the benefit granted for the coverage year, given as a
            positive amount in USD to 2 decimal places, rounded half to even at the last step only.

    Returns:
        A single confirmation line naming the reference number minted for the allowance entry, the coverage
        it was booked to, the amount granted in USD and the period it is accounted to. The line being
        returned at all is what indicates the entry was written; afterwards the grant appears in the
        coverage history.
    """
    plans = ctx.find("protection_plans", protection_plan_id=protection_plan_id)
    plan = plans[0] if plans else {}
    amount = round(float(allowance_amount), 2)
    rid = ctx.make_id("pgra_", protection_plan_id, amount)
    ctx.create("protection_ledger", rid, protection_entry_id=rid,
               protection_plan_id=protection_plan_id,
               customer_id=plan.get("customer_id", ""),
               event_type="protection_allowance_reinstated",
               posted_date=ctx.now()[:10],
               amount=amount,
               claim_reference="", claim_type="not_applicable", claim_outcome="not_applicable",
               denial_reason_code="not_applicable", inspection_result="not_applicable",
               inspection_store_code="", deductible_charged=0.0,
               covered_item_sku=plan.get("covered_item_sku", ""),
               service_order_reference="", payment_channel="not_applicable",
               billing_period=ctx.now()[:7], source_entry_id="")
    return (f"Allowance {rid} granted on coverage {protection_plan_id}: {amount:.2f} USD booked for the "
            f"coverage year, accounted to {ctx.now()[:7]}.")


@tool(owner="user", rw="write")
def confirm_coverage_transfer_42b50f64(ctx: ToolContext, protection_plan_id: str, new_owner_name: str,
                                       allowance_carried_across: float) -> str:
    """Pass a piece of live protection coverage, and the benefit standing on it, to a new owner.

    The customer runs this themselves, because giving away cover they paid for is theirs alone to do. One
    call closes the coverage as transferred with today as its closing date, writes the new owner onto the
    record, sets the benefit standing on it to the figure that goes across with the piece, and raises a
    transfer on the protection desk's request record already marked as confirmed by the customer.
    Afterwards the coverage reads as transferred, no further claim can be opened on it by the person handing
    it over, and the benefit that went across shows on the record.

    Args:
        protection_plan_id: Id class — the reference number of the coverage record being passed on, as
            returned by the protection coverage lookup.
        new_owner_name: Verbatim class — the full name of the person the coverage is being passed to, taken
            from what the customer says and copied character for character, keeping their wording, spelling
            and punctuation exactly, with nothing translated, shortened, tidied or added (verbatim).
        allowance_carried_across: Fixed-format class — the benefit that goes across with the piece, given as
            a positive amount in USD to 2 decimal places, rounded half to even at the last step only; pass
            0.00 where nothing goes across.

    Returns:
        A single confirmation line naming the coverage that was transferred, the person it went to, the date
        it closed on, the benefit carried across in USD and the reference number minted for the transfer on
        the desk's request record. The line being returned at all is what indicates the transfer took
        effect; afterwards the coverage record reads transferred and carries the new owner's name.
    """
    plans = ctx.find("protection_plans", protection_plan_id=protection_plan_id)
    plan = plans[0] if plans else {}
    carried = round(float(allowance_carried_across), 2)
    request_id = ctx.make_id("preq_", protection_plan_id, "transfer", new_owner_name)
    ctx.create("protection_intake", request_id, protection_request_id=request_id,
               customer_id=plan.get("customer_id", ""), protection_plan_id=protection_plan_id,
               request_type="transfer", request_status="customer_confirmed", claim_reference="",
               effective_date=ctx.now()[:10], created_at=ctx.now())
    ctx.update("protection_plans", protection_plan_id, status="transferred",
               transferred_to_name=new_owner_name, closed_date=ctx.now()[:10],
               remaining_benefit_allowance=carried)
    return (f"Coverage {protection_plan_id} transferred to {new_owner_name} on {ctx.now()[:10]} with "
            f"{carried:.2f} USD of benefit carried across; transfer {request_id} confirmed by the customer.")

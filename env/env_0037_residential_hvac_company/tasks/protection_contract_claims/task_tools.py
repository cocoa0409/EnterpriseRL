"""Hidden task tools of the protection_contract_claims difficulty (Harbison protection contracts).

Each tool lands exactly one atomic business write with the values the agent has already worked
out from the published policy; no tool checks a prerequisite, an eligibility rule or a status, and
none computes an amount on the agent's behalf. Reached only through unlock_* -> call_*.
"""

from erlbench import ToolContext, tool


@tool(owner="agent", rw="write")
def decide_labor_plan_claim_66c3e056(ctx: ToolContext, contract_id: str, claim_id: str, ticket_id: str,
                                     equipment_id: str, install_id: str, decision: str, denial_reason: str,
                                     approved_amount: float) -> str:
    """Post the original decision on a claim filed against a Harbison labor-only protection contract
    (Harbison 5-Year Labor Protection or Harbison 10-Year Labor Protection). One call records one
    decision entry, round 1, on the contract's claim history, dated today, carrying the outcome, the
    governing reason for any denied part and the approved amount. The contract's remaining claim
    benefit and the service invoice are not changed by this entry. The holder and the agent can see
    the decision in the contract's claim history right away.

    Args:
        contract_id: Id class — reference number of the protection contract the claim was filed
            against, read from the protection contract lookup.
        claim_id: Id class — reference number of the claim being decided (the claim-file entry's
            own reference number), read from the contract's claim history.
        ticket_id: Id class — reference number of the service call on which the failure was
            diagnosed and repaired, read from the claim-file entry or the service call lookup.
        equipment_id: Id class — reference number of the failed unit named on the claim, read from
            the claim-file entry or the equipment lookup.
        install_id: Id class — reference number of the Harbison installation of the covered
            equipment, read from the protection contract; it is echoed on the decision receipt.
        decision: Enum class — the outcome of the decision, exactly one of: approved — every tested
            part of the claim passes and the claim is paid as decided; partially_approved — part of
            the claim is refused, as when the manufacturer supplies the part, and the rest is paid;
            denied — the claim fails a coverage test and nothing is paid.
        denial_reason: Enum class — the governing reason for a denial or for the refused part of a
            partial approval, exactly one of: none — the claim is approved with nothing refused;
            component_not_covered — the failed component is not covered by the tier;
            outside_coverage_term — the failure date is outside the coverage dates;
            maintenance_not_documented — documented maintenance is not current;
            filed_after_deadline — the claim was filed after the filing deadline;
            waiting_period_not_elapsed — the failure came before coverage started after a waiting
            period; manufacturer_parts_coverage_applies — the manufacturer's parts warranty supplies
            the part; limit_exhausted — no claim benefit remains; excluded_cause — the failure stems
            from an excluded cause; contract_not_active — the contract was not active.
        approved_amount: Fixed-format class — the amount approved on the decision, in USD, 2 decimal
            places, positive, rounded to the cent half up; 0.00 on a denial.

    Returns:
        A dictionary rendered as text: claim_entry_id (reference number of the decision entry just
        posted), claim_id, contract_id, ticket_id, install_id, decision, denial_reason (empty when
        none), decision_round (always 1), approved_amount (USD, 2 decimals) and entry_date
        (YYYY-MM-DD, today). The presence of claim_entry_id means the decision is on record.
    """
    amount = round(float(approved_amount), 2)
    reason = "" if denial_reason == "none" else denial_reason
    rid = ctx.make_id("wcd_", contract_id, claim_id, ticket_id, equipment_id, install_id, decision,
                      denial_reason, amount)
    found = ctx.find("warranty_contracts", contract_id=contract_id)
    holder = found[0].get("customer_id") if found else None
    today = ctx.now()[:10]
    ctx.create("warranty_claim_entries", rid, claim_entry_id=rid, contract_id=contract_id,
               customer_id=holder, event_type="warranty_claim_decide", claim_id=claim_id,
               ticket_id=ticket_id, equipment_id=equipment_id, component="", failure_date="",
               entry_date=today, decision=decision, denial_reason=reason, decision_round=1,
               payout_component="", amount=amount, grant_reason="")
    return str({"claim_entry_id": rid, "claim_id": claim_id, "contract_id": contract_id,
                "ticket_id": ticket_id, "install_id": install_id, "decision": decision,
                "denial_reason": reason, "decision_round": 1, "approved_amount": amount,
                "entry_date": today})


@tool(owner="agent", rw="write")
def charge_claim_service_fee_b62a9756(ctx: ToolContext, contract_id: str, claim_id: str, ticket_id: str,
                                      fee_amount: float) -> str:
    """Charge the claim service fee for one service call on a Harbison protection contract. One call
    posts one claim service fee charge on the contract's billing history, dated today, naming one
    claim of that service call and the service call it is charged for, and raises the amount
    the holder owes on the contract by that fee. The holder can see the fee and the new balance owed
    on the contract right away.

    Args:
        contract_id: Id class — reference number of the protection contract the fee is charged on,
            read from the protection contract lookup.
        claim_id: Id class — reference number of the claim named on the fee (the claim-file
            entry's reference number of a claim on that service call), read from the contract's
            claim history.
        ticket_id: Id class — reference number of the service call the fee is charged for, read from
            the claim history or the service call lookup.
        fee_amount: Fixed-format class — the fee charged, in USD, 2 decimal places, always positive,
            rounded to the cent half up.

    Returns:
        A dictionary rendered as text: warranty_billing_id (reference number of the fee charge just
        posted), contract_id, claim_id, ticket_id, line_type (always claim_service_fee), fee_amount
        (USD, 2 decimals), posted_date (YYYY-MM-DD, today) and contract_balance (the amount now owed
        on the contract, USD, 2 decimals, signed). The presence of warranty_billing_id means the fee
        is on the contract.
    """
    fee = round(float(fee_amount), 2)
    rid = ctx.make_id("wbf_", contract_id, claim_id, ticket_id, fee)
    found = ctx.find("warranty_contracts", contract_id=contract_id)
    row = found[0] if found else {}
    today = ctx.now()[:10]
    ctx.create("warranty_billing_entries", rid, warranty_billing_id=rid, contract_id=contract_id,
               customer_id=row.get("customer_id"), event_type="warranty_charge",
               line_type="claim_service_fee", amount=fee, posted_date=today, claim_id=claim_id,
               ticket_id=ticket_id, payment_method="", payment_reference="", source_billing_id="")
    balance = round(float(row.get("contract_balance") or 0) + fee, 2)
    ctx.update("warranty_contracts", contract_id, contract_balance=balance)
    return str({"warranty_billing_id": rid, "contract_id": contract_id, "claim_id": claim_id,
                "ticket_id": ticket_id, "line_type": "claim_service_fee", "fee_amount": fee,
                "posted_date": today, "contract_balance": balance})


@tool(owner="user", rw="write")
def confirm_protection_cancellation_57f0aac4(ctx: ToolContext, warranty_request_id: str, contract_id: str,
                                             source_billing_id: str, refund_amount: float) -> str:
    """The holder confirms their own pending cancellation request on a Harbison protection contract.
    One call marks the request confirmed, closes the contract as cancelled effective today, posts
    the cancellation refund credit against the contract-price charge, and, where the credit leaves
    Harbison owing the holder money, pays that credit balance back to the original payment method so
    the contract balance ends at zero. The holder sees the contract cancelled, the refund credited
    and any payout issued right away.

    Args:
        warranty_request_id: Id class — reference number of the holder's pending cancellation
            request, read from the protection change request lookup.
        contract_id: Id class — reference number of the protection contract being cancelled, read
            from the protection contract lookup.
        source_billing_id: Id class — reference number of the contract-price charge the refund is
            credited against, read from the contract's billing history; pass an empty value where the
            tier was bought on the installation contract and no contract-price charge stands on the
            contract.
        refund_amount: Fixed-format class — the cancellation refund credited, in USD, 2 decimal
            places, always positive, rounded to the cent half up, as the agent stated it to the
            holder.

    Returns:
        A dictionary rendered as text: warranty_request_id, request_status (confirmed), contract_id,
        status (cancelled), closed_date (YYYY-MM-DD, today), credit_id (reference number of the
        refund credit), refund_amount (USD, 2 decimals), payout_id (reference number of the payout,
        empty when nothing is paid out), payout_amount (USD, 2 decimals), payout_reference (payout
        confirmation number, empty when nothing is paid out) and contract_balance (USD, 2 decimals,
        signed). status cancelled with a credit_id means the cancellation is recorded.
    """
    amount = round(float(refund_amount), 2)
    found = ctx.find("warranty_contracts", contract_id=contract_id)
    row = found[0] if found else {}
    holder = row.get("customer_id")
    today = ctx.now()[:10]
    ctx.update("warranty_change_requests", warranty_request_id, request_status="confirmed")
    credit_id = ctx.make_id("wbc_", warranty_request_id, contract_id, source_billing_id, amount)
    ctx.create("warranty_billing_entries", credit_id, warranty_billing_id=credit_id, contract_id=contract_id,
               customer_id=holder, event_type="warranty_credit", line_type="cancellation_refund_credit",
               amount=amount, posted_date=today, claim_id="", ticket_id=None, payment_method="",
               payment_reference="", source_billing_id=source_billing_id or None)
    balance = round(float(row.get("contract_balance") or 0) - amount, 2)
    payout_id, payout_amount, payout_ref = "", 0.0, ""
    if balance < 0:
        payout_amount = round(-balance, 2)
        payout_id = ctx.make_id("wbp_", credit_id, payout_amount)
        payout_ref = "HRP-" + payout_id[-8:].upper()
        ctx.create("warranty_billing_entries", payout_id, warranty_billing_id=payout_id, contract_id=contract_id,
                   customer_id=holder, event_type="warranty_refund_issued", line_type="refund_payout",
                   amount=payout_amount, posted_date=today, claim_id="", ticket_id=None,
                   payment_method="original_payment_method", payment_reference=payout_ref,
                   source_billing_id=credit_id)
        balance = 0.0
    ctx.update("warranty_contracts", contract_id, status="cancelled", closed_date=today,
               contract_balance=balance)
    return str({"warranty_request_id": warranty_request_id, "request_status": "confirmed",
                "contract_id": contract_id, "status": "cancelled", "closed_date": today,
                "credit_id": credit_id, "refund_amount": amount, "payout_id": payout_id,
                "payout_amount": payout_amount, "payout_reference": payout_ref,
                "contract_balance": balance})


@tool(owner="agent", rw="write")
def decide_parts_labor_claim_22401446(ctx: ToolContext, contract_id: str, claim_id: str, ticket_id: str,
                                      equipment_id: str, install_id: str, decision: str, denial_reason: str,
                                      approved_amount: float) -> str:
    """Post the original decision on a claim filed against a Harbison parts-and-labor protection
    contract (Harbison 10-Year Parts & Labor Protection, Harbison 12-Year Total Protection or Harbison
    12-Year Total Protection Plus). One call records one decision entry, round 1, on the contract's
    claim history, dated today, carrying the outcome, the governing reason for any refused part and
    the approved amount. The contract's remaining claim benefit and the service invoice are not
    changed by this entry. The holder and the agent can see the decision in the contract's claim
    history right away.

    Args:
        contract_id: Id class — reference number of the protection contract the claim was filed
            against, read from the protection contract lookup.
        claim_id: Id class — reference number of the claim being decided (the claim-file entry's
            own reference number), read from the contract's claim history.
        ticket_id: Id class — reference number of the service call on which the failure was
            diagnosed and repaired, read from the claim-file entry or the service call lookup.
        equipment_id: Id class — reference number of the failed unit named on the claim, read from
            the claim-file entry or the equipment lookup.
        install_id: Id class — reference number of the Harbison installation of the covered
            equipment, read from the protection contract; it is echoed on the decision receipt.
        decision: Enum class — the outcome of the decision, exactly one of: approved — every tested
            part of the claim passes and the claim is paid as decided; partially_approved — part of
            the claim is refused, as when the manufacturer supplies the part, and the rest is paid;
            denied — the claim fails a coverage test and nothing is paid.
        denial_reason: Enum class — the governing reason for a denial or for the refused part of a
            partial approval, exactly one of: none — the claim is approved with nothing refused;
            component_not_covered — the failed component is not covered by the tier;
            outside_coverage_term — the failure date is outside the coverage dates;
            maintenance_not_documented — documented maintenance is not current;
            filed_after_deadline — the claim was filed after the filing deadline;
            waiting_period_not_elapsed — the failure came before coverage started after a waiting
            period; manufacturer_parts_coverage_applies — the manufacturer's parts warranty supplies
            the part; limit_exhausted — no claim benefit remains; excluded_cause — the failure stems
            from an excluded cause; contract_not_active — the contract was not active.
        approved_amount: Fixed-format class — the amount approved on the decision, in USD, 2 decimal
            places, positive, rounded to the cent half up; 0.00 on a denial.

    Returns:
        A dictionary rendered as text: claim_entry_id (reference number of the decision entry just
        posted), claim_id, contract_id, ticket_id, install_id, decision, denial_reason (empty when
        none), decision_round (always 1), approved_amount (USD, 2 decimals) and entry_date
        (YYYY-MM-DD, today). The presence of claim_entry_id means the decision is on record.
    """
    amount = round(float(approved_amount), 2)
    reason = "" if denial_reason == "none" else denial_reason
    rid = ctx.make_id("wcp_", contract_id, claim_id, ticket_id, equipment_id, install_id, decision,
                      denial_reason, amount)
    found = ctx.find("warranty_contracts", contract_id=contract_id)
    holder = found[0].get("customer_id") if found else None
    today = ctx.now()[:10]
    ctx.create("warranty_claim_entries", rid, claim_entry_id=rid, contract_id=contract_id,
               customer_id=holder, event_type="warranty_claim_decide", claim_id=claim_id,
               ticket_id=ticket_id, equipment_id=equipment_id, component="", failure_date="",
               entry_date=today, decision=decision, denial_reason=reason, decision_round=1,
               payout_component="", amount=amount, grant_reason="")
    return str({"claim_entry_id": rid, "claim_id": claim_id, "contract_id": contract_id,
                "ticket_id": ticket_id, "install_id": install_id, "decision": decision,
                "denial_reason": reason, "decision_round": 1, "approved_amount": amount,
                "entry_date": today})


@tool(owner="user", rw="write")
def confirm_protection_transfer_64743e30(ctx: ToolContext, warranty_request_id: str, contract_id: str,
                                         buyer_customer_id: str, carried_benefit: float, transfer_fee: float) -> str:
    """The holder confirms their own pending home-sale transfer request on a Harbison protection
    contract. One call marks the request confirmed, closes the seller's contract as transferred
    effective today, issues the buyer named on the request a new active contract with the same tier,
    scope, units, installation and coverage dates and a price of 0.00, grants that new contract the
    carried claim benefit, and charges the buyer's contract the transfer fee where it is above 0.00.
    The holder sees the transfer recorded and the buyer's new contract reference right away.

    Args:
        warranty_request_id: Id class — reference number of the holder's pending transfer request,
            read from the protection change request lookup.
        contract_id: Id class — reference number of the seller's protection contract being
            transferred, read from the protection contract lookup.
        buyer_customer_id: Id class — customer reference number of the home buyer named on the
            transfer request, read from the protection change request lookup.
        carried_benefit: Fixed-format class — the claim benefit granted to the buyer's contract, in
            USD, 2 decimal places, rounded to the cent half up, as the agent stated it to the holder.
        transfer_fee: Fixed-format class — the transfer fee charged on the buyer's contract, in USD,
            2 decimal places, always positive, the tier's listed transfer fee; 0.00 where the tier
            charges none.

    Returns:
        A dictionary rendered as text: warranty_request_id, request_status (confirmed), contract_id
        and status (transferred) of the seller's contract, closed_date (YYYY-MM-DD, today),
        buyer_contract_id (reference number of the buyer's new contract), buyer_customer_id,
        carried_benefit (USD, 2 decimals), transfer_fee (USD, 2 decimals) and fee_entry_id (reference
        number of the transfer fee charge, empty when no fee). A buyer_contract_id with status
        transferred on the seller's contract means the transfer is recorded.
    """
    benefit = round(float(carried_benefit), 2)
    fee = round(float(transfer_fee), 2)
    today = ctx.now()[:10]
    buyer = buyer_customer_id
    found = ctx.find("warranty_contracts", contract_id=contract_id)
    seller = found[0] if found else {}
    ctx.update("warranty_change_requests", warranty_request_id, request_status="confirmed")
    ctx.update("warranty_contracts", contract_id, status="transferred", closed_date=today)
    new_id = ctx.make_id("wct_", warranty_request_id, contract_id, buyer_customer_id, benefit, fee)
    ctx.create("warranty_contracts", new_id, contract_id=new_id, customer_id=buyer,
               equipment_id=seller.get("equipment_id"), paired_equipment_id=seller.get("paired_equipment_id"),
               install_id=seller.get("install_id"), variant_name=seller.get("variant_name"), status="active",
               purchase_date=today, purchase_channel="transfer", equipment_scope=seller.get("equipment_scope"),
               coverage_start=seller.get("coverage_start"), coverage_end=seller.get("coverage_end"),
               contract_price=0.0, claim_limit_remaining=benefit, contract_balance=fee,
               transferred_from_contract_id=contract_id, closed_date=None)
    grant_id = ctx.make_id("wcg_", new_id, benefit)
    ctx.create("warranty_claim_entries", grant_id, claim_entry_id=grant_id, contract_id=new_id, customer_id=buyer,
               event_type="warranty_limit_grant", claim_id="", ticket_id=None, equipment_id=None, component="",
               failure_date="", entry_date=today, decision="", denial_reason="", decision_round=0,
               payout_component="", amount=benefit, grant_reason="transfer_carryover")
    fee_id = ""
    if fee > 0:
        fee_id = ctx.make_id("wbt_", new_id, fee)
        ctx.create("warranty_billing_entries", fee_id, warranty_billing_id=fee_id, contract_id=new_id,
                   customer_id=buyer, event_type="warranty_charge", line_type="transfer_fee", amount=fee,
                   posted_date=today, claim_id="", ticket_id=None, payment_method="", payment_reference="",
                   source_billing_id="")
    return str({"warranty_request_id": warranty_request_id, "request_status": "confirmed",
                "contract_id": contract_id, "status": "transferred", "closed_date": today,
                "buyer_contract_id": new_id, "buyer_customer_id": buyer, "carried_benefit": benefit,
                "transfer_fee": fee, "fee_entry_id": fee_id})

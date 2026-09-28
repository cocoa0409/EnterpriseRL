"""Hidden task tools of the renters_billing_and_cancellation difficulty (RentGuard renters policies).

Each tool performs one atomic posting on one RentGuard policy and its premium account; none of them
checks eligibility, prerequisites or amounts. Names are registered only in renters.extended.yaml
(extended_policies.target_tool) and are reached through unlock_* -> call_*.
"""

from erlbench import ToolContext, tool


@tool(owner="agent", rw="write")
def post_discount_stop_charge_d8b9b7f1(ctx: ToolContext, renters_policy_id: str, effective_date: str,
                                       restated_term_premium: float, amount: float) -> str:
    """Post the multi-policy discount stop on one RentGuard renters policy. One call records a single
    additional premium entry on the policy's premium account with the reason "multi-policy discount change",
    dated the effective date given, for the amount given; it raises the policy's premium balance by that
    amount and restates the policy's annual premium to the figure given. The caller can afterwards see the
    new charge on the premium account, the higher balance and the restated annual premium on the policy.

    Args:
        renters_policy_id: Id class — the reference number of the RentGuard renters policy record being
            charged, as returned by the renters policy lookup for this customer.
        effective_date: Fixed-format class — the date the discount change takes effect, written YYYY-MM-DD
            (calendar date, no time zone); it is recorded as the effective date of the charge.
        restated_term_premium: Fixed-format class — the annual premium the policy carries once the discount
            has stopped, in USD with 2 decimal places (a figure already rounded half-up to the cent).
        amount: Fixed-format class — the additional premium charged for the stop, in USD with 2 decimal
            places, a positive figure already rounded half-up to the cent.

    Returns:
        A confirmation sentence (str) naming the new premium account entry reference (text id), the amount
        charged in USD with 2 decimal places, its effective date (YYYY-MM-DD), the restated annual premium
        and the premium balance now owed (USD, 2 decimal places); receiving it means the charge is posted.
    """
    pol = (ctx.find("renters_policies", renters_policy_id=renters_policy_id) or [{}])[0]
    rid = ctx.make_id("rbl_", renters_policy_id, effective_date, restated_term_premium, amount)
    amt = round(float(amount), 2)
    ctx.create("renters_billing", rid, renters_billing_id=rid, renters_policy_id=renters_policy_id,
               customer_id=pol.get("customer_id", ""), event_type="renters_additional_premium",
               posted_date=ctx.now()[:10], term_effective_date=pol.get("effective_date", ""),
               installment_number=0, due_date="", amount=amt, fee_code="none", payment_method="none",
               payment_reference="", change_reason="multi_policy_discount_change",
               effective_date=effective_date, credit_basis="none", source_billing_id="")
    balance = round(float(pol.get("premium_balance") or 0) + amt, 2)
    ctx.update("renters_policies", renters_policy_id, term_premium=round(float(restated_term_premium), 2),
               premium_balance=balance)
    return (f"Discount-stop charge {rid} of {amt:.2f} USD posted effective {effective_date}; annual premium "
            f"restated to {round(float(restated_term_premium), 2):.2f} USD; premium balance now {balance:.2f} USD.")


@tool(owner="agent", rw="write")
def post_discount_restart_credit_e779526e(ctx: ToolContext, renters_policy_id: str, effective_date: str,
                                          restated_term_premium: float, amount: float) -> str:
    """Post the multi-policy discount restart on one RentGuard renters policy. One call records a single
    return premium entry on the policy's premium account with the reason "multi-policy discount change" on a
    pro-rata basis, dated the effective date given, for the amount given; it lowers the policy's premium
    balance by that amount and restates the policy's annual premium to the figure given. The caller can
    afterwards see the credit on the premium account, the lower balance and the restated annual premium.

    Args:
        renters_policy_id: Id class — the reference number of the RentGuard renters policy record being
            credited, as returned by the renters policy lookup for this customer.
        effective_date: Fixed-format class — the date the discount change takes effect, written YYYY-MM-DD
            (calendar date, no time zone); it is recorded as the effective date of the credit.
        restated_term_premium: Fixed-format class — the annual premium the policy carries once the discount
            has restarted, in USD with 2 decimal places (a figure already rounded half-up to the cent).
        amount: Fixed-format class — the return premium credited for the restart, in USD with 2 decimal
            places, a positive figure already rounded half-up to the cent.

    Returns:
        A confirmation sentence (str) naming the new premium account entry reference (text id), the amount
        credited in USD with 2 decimal places, its effective date (YYYY-MM-DD), the restated annual premium
        and the premium balance now standing (USD, 2 decimal places); receiving it means the credit is posted.
    """
    pol = (ctx.find("renters_policies", renters_policy_id=renters_policy_id) or [{}])[0]
    rid = ctx.make_id("rbl_", renters_policy_id, effective_date, restated_term_premium, amount)
    amt = round(float(amount), 2)
    ctx.create("renters_billing", rid, renters_billing_id=rid, renters_policy_id=renters_policy_id,
               customer_id=pol.get("customer_id", ""), event_type="renters_return_premium",
               posted_date=ctx.now()[:10], term_effective_date=pol.get("effective_date", ""),
               installment_number=0, due_date="", amount=amt, fee_code="none", payment_method="none",
               payment_reference="", change_reason="multi_policy_discount_change",
               effective_date=effective_date, credit_basis="pro_rata", source_billing_id="")
    balance = round(float(pol.get("premium_balance") or 0) - amt, 2)
    ctx.update("renters_policies", renters_policy_id, term_premium=round(float(restated_term_premium), 2),
               premium_balance=balance)
    return (f"Discount-restart credit {rid} of {amt:.2f} USD posted effective {effective_date}; annual premium "
            f"restated to {round(float(restated_term_premium), 2):.2f} USD; premium balance now {balance:.2f} USD.")


@tool(owner="agent", rw="write")
def assess_late_charge_664a192e(ctx: ToolContext, renters_policy_id: str, term_effective_date: str,
                                installment_number: int, amount: float) -> str:
    """Charge a late charge on one overdue installment of a RentGuard renters policy. One call records a
    single fee entry of type late fee on the policy's premium account for the term and installment given,
    dated today, for the amount given, and raises the policy's premium balance by that amount. The caller
    can afterwards see the late charge against that installment and the higher balance owed.

    Args:
        renters_policy_id: Id class — the reference number of the RentGuard renters policy record whose
            installment is overdue, as returned by the renters policy lookup for this customer.
        term_effective_date: Fixed-format class — the start date of the policy term the overdue installment
            belongs to, written YYYY-MM-DD, copied from that installment's billing entry.
        installment_number: Fixed-format class — the position of the overdue installment within its term,
            an integer 0-12 (1 = the opening installment of the term), copied from that installment's
            billing entry.
        amount: Fixed-format class — the late charge, in USD with 2 decimal places, a positive figure
            already rounded half-up to the cent.

    Returns:
        A confirmation sentence (str) naming the new fee entry reference (text id), the term start date
        (YYYY-MM-DD) and installment number it is charged against, the charge in USD with 2 decimal places
        and the premium balance now owed (USD, 2 decimal places); receiving it means the charge is posted.
    """
    pol = (ctx.find("renters_policies", renters_policy_id=renters_policy_id) or [{}])[0]
    rid = ctx.make_id("rbl_", renters_policy_id, term_effective_date, installment_number, amount)
    amt = round(float(amount), 2)
    ctx.create("renters_billing", rid, renters_billing_id=rid, renters_policy_id=renters_policy_id,
               customer_id=pol.get("customer_id", ""), event_type="renters_fee_assessed",
               posted_date=ctx.now()[:10], term_effective_date=term_effective_date,
               installment_number=int(installment_number), due_date="", amount=amt, fee_code="late_fee",
               payment_method="none", payment_reference="", change_reason="none", effective_date="",
               credit_basis="none", source_billing_id="")
    balance = round(float(pol.get("premium_balance") or 0) + amt, 2)
    ctx.update("renters_policies", renters_policy_id, premium_balance=balance)
    return (f"Late charge {rid} of {amt:.2f} USD posted on installment {int(installment_number)} of the term "
            f"starting {term_effective_date}; premium balance now {balance:.2f} USD.")


@tool(owner="user", rw="write")
def pay_catch_up_by_card_50a8e701(ctx: ToolContext, renters_policy_id: str, amount: float) -> str:
    """Pay a catch-up amount on your own RentGuard renters policy with your payment card. One call charges
    your card once for the amount given and records it as a single card payment received on the policy's
    premium account, dated today, lowering the policy's premium balance by that amount. You receive a
    payment confirmation number and can see the payment on the premium account.

    Args:
        renters_policy_id: Id class — the reference number of your RentGuard renters policy record, as read
            out to you by the representative from the renters policy lookup.
        amount: Fixed-format class — the amount to pay, in USD with 2 decimal places, a positive figure
            exactly as the representative tells you.

    Returns:
        A confirmation sentence (str) giving the payment confirmation number (text starting with 2), the
        amount paid in USD with 2 decimal places, the payment date (YYYY-MM-DD) and the premium balance now
        standing (USD, 2 decimal places); receiving it means the card payment is recorded.
    """
    pol = (ctx.find("renters_policies", renters_policy_id=renters_policy_id) or [{}])[0]
    rid = ctx.make_id("rbl_", renters_policy_id, amount)
    ref = ctx.make_id("2", renters_policy_id, amount, length=9)
    amt = round(float(amount), 2)
    ctx.create("renters_billing", rid, renters_billing_id=rid, renters_policy_id=renters_policy_id,
               customer_id=pol.get("customer_id", ""), event_type="renters_payment_received",
               posted_date=ctx.now()[:10], term_effective_date="", installment_number=0, due_date="",
               amount=amt, fee_code="none", payment_method="card", payment_reference=ref,
               change_reason="none", effective_date="", credit_basis="none", source_billing_id="")
    balance = round(float(pol.get("premium_balance") or 0) - amt, 2)
    ctx.update("renters_policies", renters_policy_id, premium_balance=balance)
    return (f"Card payment {ref} of {amt:.2f} USD received on {ctx.now()[:10]}; premium balance now "
            f"{balance:.2f} USD.")


@tool(owner="user", rw="write")
def pay_reinstatement_cure_5468a22a(ctx: ToolContext, renters_policy_id: str, amount: float) -> str:
    """Pay an amount on your own cancelled RentGuard renters policy with your payment card. One call charges
    your card once for the amount given and records it as a single card payment received on the policy's
    premium account, dated today, lowering the premium balance by that amount; nothing else on the policy
    changes. You receive a payment confirmation number and can see the payment on the premium account.

    Args:
        renters_policy_id: Id class — the reference number of your cancelled RentGuard renters policy record,
            as read out to you by the representative from the renters policy lookup.
        amount: Fixed-format class — the amount to pay, in USD with 2 decimal places, a positive figure
            exactly as the representative tells you.

    Returns:
        A confirmation sentence (str) giving the payment confirmation number (text starting with 2), the
        amount paid in USD with 2 decimal places, the payment date (YYYY-MM-DD) and the premium balance now
        standing (USD, 2 decimal places, negative when it is a credit); receiving it means the payment is
        recorded.
    """
    pol = (ctx.find("renters_policies", renters_policy_id=renters_policy_id) or [{}])[0]
    rid = ctx.make_id("rbl_", renters_policy_id, "cure", amount)
    ref = ctx.make_id("2", renters_policy_id, "cure", amount, length=9)
    amt = round(float(amount), 2)
    ctx.create("renters_billing", rid, renters_billing_id=rid, renters_policy_id=renters_policy_id,
               customer_id=pol.get("customer_id", ""), event_type="renters_payment_received",
               posted_date=ctx.now()[:10], term_effective_date="", installment_number=0, due_date="",
               amount=amt, fee_code="none", payment_method="card", payment_reference=ref,
               change_reason="none", effective_date="", credit_basis="none", source_billing_id="")
    balance = round(float(pol.get("premium_balance") or 0) - amt, 2)
    ctx.update("renters_policies", renters_policy_id, premium_balance=balance)
    return (f"Cure payment {ref} of {amt:.2f} USD received on {ctx.now()[:10]}; premium balance now "
            f"{balance:.2f} USD.")


@tool(owner="agent", rw="write")
def reinstate_lapsed_policy_e7e59896(ctx: ToolContext, renters_policy_id: str, renters_request_id: str,
                                     cancellation_credit_billing_id: str, reversal_amount: float,
                                     reinstatement_fee: float) -> str:
    """Reinstate one cancelled RentGuard renters policy without a lapse. One call returns the policy to in
    force with its cancellation reason, cancellation date and scheduled action date cleared, charges one
    reinstatement fee entry of the amount given, records one additional premium entry with the reason
    "reinstatement reversal" for the reversal amount given that references the cancellation credit, both
    dated today, raises the premium balance by the two amounts, and marks the signed statement of no loss
    completed. The caller can afterwards see the policy in force again, the two new entries on the premium
    account and the statement shown as completed.

    Args:
        renters_policy_id: Id class — the reference number of the cancelled RentGuard renters policy record,
            as returned by the renters policy lookup for this customer.
        renters_request_id: Id class — the reference number of the signed statement of no loss for this
            policy, as returned by the renters signature-request lookup.
        cancellation_credit_billing_id: Id class — the reference number of the premium account entry that
            credited the cancellation, as returned by the renters premium account lookup.
        reversal_amount: Fixed-format class — the amount of that cancellation credit, in USD with 2 decimal
            places, copied from the credit entry.
        reinstatement_fee: Fixed-format class — the reinstatement fee to charge, in USD with 2 decimal
            places, already rounded half-up to the cent (0.00 records no fee entry).

    Returns:
        A confirmation sentence (str) naming the policy reference now in force, the reinstatement fee entry
        reference (text id, or none when the fee is 0.00) and its amount, the reversal entry reference
        (text id) and its amount, all in USD with 2 decimal places, and the premium balance now standing;
        receiving it means the policy is reinstated.
    """
    pol = (ctx.find("renters_policies", renters_policy_id=renters_policy_id) or [{}])[0]
    fee = round(float(reinstatement_fee), 2)
    rev = round(float(reversal_amount), 2)
    fee_id = "none"
    if fee > 0:
        fee_id = ctx.make_id("rbl_", renters_policy_id, "reinstatement_fee", reinstatement_fee)
        ctx.create("renters_billing", fee_id, renters_billing_id=fee_id, renters_policy_id=renters_policy_id,
                   customer_id=pol.get("customer_id", ""), event_type="renters_fee_assessed",
                   posted_date=ctx.now()[:10], term_effective_date=pol.get("effective_date", ""),
                   installment_number=0, due_date="", amount=fee, fee_code="reinstatement_fee",
                   payment_method="none", payment_reference="", change_reason="none", effective_date="",
                   credit_basis="none", source_billing_id="")
    rev_id = ctx.make_id("rbl_", renters_policy_id, renters_request_id, cancellation_credit_billing_id, reversal_amount)
    ctx.create("renters_billing", rev_id, renters_billing_id=rev_id, renters_policy_id=renters_policy_id,
               customer_id=pol.get("customer_id", ""), event_type="renters_additional_premium",
               posted_date=ctx.now()[:10], term_effective_date=pol.get("effective_date", ""),
               installment_number=0, due_date="", amount=rev, fee_code="none", payment_method="none",
               payment_reference="", change_reason="reinstatement_reversal", effective_date=ctx.now()[:10],
               credit_basis="none", source_billing_id=cancellation_credit_billing_id)
    balance = round(float(pol.get("premium_balance") or 0) + fee + rev, 2)
    ctx.update("renters_policies", renters_policy_id, status="in_force", status_reason="none", closed_date="",
               pending_action_date="", premium_balance=balance)
    ctx.update("renters_requests", renters_request_id, outcome="completed")
    return (f"Policy {renters_policy_id} reinstated in force; reinstatement fee {fee_id} {fee:.2f} USD; "
            f"reversal {rev_id} {rev:.2f} USD; premium balance now {balance:.2f} USD.")

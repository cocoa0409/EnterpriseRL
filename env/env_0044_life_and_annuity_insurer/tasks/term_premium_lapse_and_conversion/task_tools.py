"""Hidden task tools for the term_premium_lapse_and_conversion difficulty (Ashgrove term life).

Each tool performs exactly one atomic service action on one term policy with the values the
agent has already worked out; none of them checks eligibility, status or any other policy
condition, and none of them computes an amount.
"""

from erlbench import ToolContext, tool


@tool(owner="agent", rw="write")
def convert_to_quarterly_billing_2bfb08af(ctx: ToolContext, term_policy_id: str, new_modal_premium: float) -> str:
    """Convert one Ashgrove term policy from monthly bank-draft billing to quarterly direct billing.

    The policy's premium mode becomes quarterly, its monthly bank-draft day is cleared, and its
    installment premium becomes the quarterly installment supplied. Nothing else on the policy
    changes. Afterwards the policy record shows the quarterly mode, no draft day and the new
    installment premium; the receipt below confirms the change.

    Args:
        term_policy_id: Id class — the reference number of the term policy being converted, read from the term policy lookup before the call.
        new_modal_premium: Fixed-format class — the quarterly installment premium to record, in USD, a non-negative amount with 2 decimal places (rounded half to even to the cent by the tool if more are given).

    Returns:
        A dictionary rendered as text with: status ("converted" on success); term_policy_id (the
        policy reference number); premium_mode (always "quarterly"); modal_premium (the recorded
        installment premium in USD with 2 decimal places); eft_draft_day (always None, the draft day
        having been cleared).
    """
    amount = round(float(new_modal_premium), 2)
    ctx.update("term_holdings", term_policy_id, premium_mode="quarterly", modal_premium=amount, eft_draft_day=None)
    return str({"status": "converted", "term_policy_id": term_policy_id, "premium_mode": "quarterly",
                "modal_premium": amount, "eft_draft_day": None})


@tool(owner="agent", rw="write")
def end_expired_waiver_rider_bcdc46e8(ctx: ToolContext, term_policy_id: str, new_modal_premium: float) -> str:
    """Detach the waiver of premium rider from one Ashgrove term policy and record its new installment.

    The policy's waiver of premium rider is marked as no longer attached and its installment
    premium becomes the amount supplied. Afterwards the policy record shows the rider detached
    and the new installment premium; the receipt below confirms the change.

    Args:
        term_policy_id: Id class — the reference number of the term policy whose waiver rider ends, read from the term policy lookup before the call.
        new_modal_premium: Fixed-format class — the installment premium to record once the rider is detached, in USD, a non-negative amount with 2 decimal places (rounded half to even to the cent by the tool if more are given).

    Returns:
        A dictionary rendered as text with: status ("rider_detached" on success); term_policy_id (the
        policy reference number); waiver_of_premium_rider (always False); modal_premium (the recorded
        installment premium in USD with 2 decimal places).
    """
    amount = round(float(new_modal_premium), 2)
    ctx.update("term_holdings", term_policy_id, waiver_of_premium_rider=False, modal_premium=amount)
    return str({"status": "rider_detached", "term_policy_id": term_policy_id,
                "waiver_of_premium_rider": False, "modal_premium": amount})


@tool(owner="user", rw="write")
def remit_grace_premium_a5ae3e41(ctx: ToolContext, term_policy_id: str, remittance_amount: float,
                                 payment_method: str, new_paid_to_date: str) -> str:
    """The owner pays a premium remittance on one Ashgrove term policy that is in its grace period.

    One remittance of the amount given is entered on the policy's activity history against the
    installment due on the policy's current paid-to date, the policy is shown in force again, its
    paid-to date becomes the date given and its outstanding premium becomes zero. The owner sees
    the payment confirmation below.

    Args:
        term_policy_id: Id class — the reference number of the owner's term policy, read from the term policy lookup and given to the owner by the representative.
        remittance_amount: Fixed-format class — the amount the owner pays, in USD, a positive amount with 2 decimal places (rounded half to even to the cent by the tool if more are given).
        payment_method: Enum class — how the owner pays: eft for a one-time draft from the owner's bank account; check for a mailed paper check; debit_card for a debit card payment taken over the telephone; online_bank_payment for a payment the owner sends from the bank's online bill pay.
        new_paid_to_date: Fixed-format class — the paid-to date the policy carries once the remittance is applied, as YYYY-MM-DD.

    Returns:
        A dictionary rendered as text with: status ("payment_applied" on success); payment_id (the
        reference number of the new remittance entry); term_policy_id; amount (USD with 2 decimal
        places); premium_due_date (YYYY-MM-DD, the installment the remittance was entered against);
        paid_to_date (YYYY-MM-DD, the new paid-to date); policy_status (always "in_force").
    """
    amount = round(float(remittance_amount), 2)
    holding = ctx.find("term_holdings", term_policy_id=term_policy_id)
    due = holding[0].get("paid_to_date") if holding else None
    owner = holding[0].get("customer_id") if holding else None
    rid = ctx.make_id("tpay_", term_policy_id, amount, payment_method, new_paid_to_date)
    ctx.create("term_transactions", rid, term_txn_id=rid, term_policy_id=term_policy_id, customer_id=owner,
               event_type="term_premium_paid", transaction_date=ctx.now()[:10], amount=amount,
               premium_due_date=due, payment_method=payment_method)
    ctx.update("term_holdings", term_policy_id, status="in_force", paid_to_date=new_paid_to_date,
               premium_outstanding=0.0)
    return str({"status": "payment_applied", "payment_id": rid, "term_policy_id": term_policy_id,
                "amount": amount, "premium_due_date": due, "paid_to_date": new_paid_to_date,
                "policy_status": "in_force"})


@tool(owner="agent", rw="write")
def apply_face_decrease_78b62126(ctx: ToolContext, term_policy_id: str, term_request_id: str,
                                 new_face_amount: float, new_modal_premium: float) -> str:
    """Apply an approved face decrease request to one Ashgrove term policy.

    The policy's face amount becomes the requested face, its installment premium becomes the
    amount supplied, and the face decrease request is marked completed. Afterwards the policy
    record shows the lower face and new installment and the request shows as completed.

    Args:
        term_policy_id: Id class — the reference number of the term policy being decreased, read from the term policy lookup before the call.
        term_request_id: Id class — the reference number of the face decrease request on file, read from the service request lookup before the call.
        new_face_amount: Fixed-format class — the face amount after the decrease, in USD, with 2 decimal places, copied from the request's requested face.
        new_modal_premium: Fixed-format class — the installment premium to record after the decrease, in USD, a non-negative amount with 2 decimal places (rounded half to even to the cent by the tool if more are given).

    Returns:
        A dictionary rendered as text with: status ("decrease_applied" on success); term_policy_id;
        term_request_id; face_amount (USD with 2 decimal places); modal_premium (USD with 2 decimal
        places); request_status (always "completed").
    """
    face = round(float(new_face_amount), 2)
    amount = round(float(new_modal_premium), 2)
    ctx.update("term_holdings", term_policy_id, face_amount=face, modal_premium=amount)
    ctx.update("term_service_requests", term_request_id, request_status="completed")
    return str({"status": "decrease_applied", "term_policy_id": term_policy_id, "term_request_id": term_request_id,
                "face_amount": face, "modal_premium": amount, "request_status": "completed"})


@tool(owner="agent", rw="write")
def bill_back_installment_903386f9(ctx: ToolContext, term_policy_id: str, premium_due_date: str, billed_amount: float) -> str:
    """Bill one premium installment on one Ashgrove term policy's activity history.

    A billed-installment entry is added to the policy's activity history for the due date and
    amount supplied, dated today. Nothing else on the policy changes. The new entry is visible in
    the policy's activity history and the receipt below confirms it.

    Args:
        term_policy_id: Id class — the reference number of the term policy being billed, read from the term policy lookup before the call.
        premium_due_date: Fixed-format class — the due date of the installment being billed, as YYYY-MM-DD.
        billed_amount: Fixed-format class — the installment amount billed, in USD, a positive amount with 2 decimal places (rounded half to even to the cent by the tool if more are given).

    Returns:
        A dictionary rendered as text with: status ("installment_billed" on success); billing_id (the
        reference number of the new billed-installment entry); term_policy_id; premium_due_date
        (YYYY-MM-DD); amount (USD with 2 decimal places).
    """
    amount = round(float(billed_amount), 2)
    holding = ctx.find("term_holdings", term_policy_id=term_policy_id)
    owner = holding[0].get("customer_id") if holding else None
    rid = ctx.make_id("tbil_", term_policy_id, premium_due_date, amount)
    ctx.create("term_transactions", rid, term_txn_id=rid, term_policy_id=term_policy_id, customer_id=owner,
               event_type="term_premium_billed", transaction_date=ctx.now()[:10], amount=amount,
               premium_due_date=premium_due_date)
    return str({"status": "installment_billed", "billing_id": rid, "term_policy_id": term_policy_id,
                "premium_due_date": premium_due_date, "amount": amount})


@tool(owner="user", rw="write")
def pay_reinstatement_amount_3f8d4404(ctx: ToolContext, term_policy_id: str, term_request_id: str, reinstatement_amount: float,
                                      payment_method: str, new_paid_to_date: str) -> str:
    """The owner pays the reinstatement amount on a lapsed Ashgrove term policy under an approved reinstatement application.

    One payment of the amount given is entered on the policy's activity history against the
    installment due on the policy's current paid-to date; the policy is shown in force again with
    today as its reinstatement date, its paid-to date becomes the date given, its outstanding
    premium becomes zero, and the reinstatement application is marked completed. The owner sees
    the confirmation below.

    Args:
        term_policy_id: Id class — the reference number of the owner's lapsed term policy, read from the term policy lookup and given to the owner by the representative.
        term_request_id: Id class — the reference number of the approved reinstatement application, read from the service request lookup and given to the owner by the representative.
        reinstatement_amount: Fixed-format class — the amount the owner pays, in USD, a positive amount with 2 decimal places (rounded half to even to the cent by the tool if more are given).
        payment_method: Enum class — how the owner pays: eft for a one-time draft from the owner's bank account; check for a mailed paper check; debit_card for a debit card payment taken over the telephone; online_bank_payment for a payment the owner sends from the bank's online bill pay.
        new_paid_to_date: Fixed-format class — the paid-to date the policy carries once the payment is applied, as YYYY-MM-DD.

    Returns:
        A dictionary rendered as text with: status ("policy_reinstated" on success); payment_id (the
        reference number of the new payment entry); term_policy_id; term_request_id; amount (USD with
        2 decimal places); reinstatement_date (YYYY-MM-DD, today); paid_to_date (YYYY-MM-DD);
        policy_status (always "in_force").
    """
    amount = round(float(reinstatement_amount), 2)
    holding = ctx.find("term_holdings", term_policy_id=term_policy_id)
    due = holding[0].get("paid_to_date") if holding else None
    owner = holding[0].get("customer_id") if holding else None
    today = ctx.now()[:10]
    rid = ctx.make_id("trin_", term_policy_id, term_request_id, amount, payment_method, new_paid_to_date)
    ctx.create("term_transactions", rid, term_txn_id=rid, term_policy_id=term_policy_id, customer_id=owner,
               event_type="term_premium_paid", transaction_date=today, amount=amount, premium_due_date=due,
               payment_method=payment_method, term_request_id=term_request_id)
    ctx.update("term_holdings", term_policy_id, status="in_force", reinstatement_date=today,
               paid_to_date=new_paid_to_date, premium_outstanding=0.0)
    ctx.update("term_service_requests", term_request_id, request_status="completed")
    return str({"status": "policy_reinstated", "payment_id": rid, "term_policy_id": term_policy_id,
                "term_request_id": term_request_id, "amount": amount, "reinstatement_date": today,
                "paid_to_date": new_paid_to_date, "policy_status": "in_force"})


@tool(owner="agent", rw="write")
def end_expired_adb_rider_b05b3f4a(ctx: ToolContext, term_policy_id: str, new_modal_premium: float) -> str:
    """Remove the accidental death benefit rider from one Ashgrove term policy and record its new installment.

    The policy's accidental death rider amount becomes zero and its installment premium becomes
    the amount supplied. Afterwards the policy record shows no accidental death rider and the new
    installment premium; the receipt below confirms the change.

    Args:
        term_policy_id: Id class — the reference number of the term policy whose accidental death rider ends, read from the term policy lookup before the call.
        new_modal_premium: Fixed-format class — the installment premium to record once the rider is removed, in USD, a non-negative amount with 2 decimal places (rounded half to even to the cent by the tool if more are given).

    Returns:
        A dictionary rendered as text with: status ("rider_removed" on success); term_policy_id;
        adb_rider_amount (always 0.0, USD); modal_premium (USD with 2 decimal places).
    """
    amount = round(float(new_modal_premium), 2)
    ctx.update("term_holdings", term_policy_id, adb_rider_amount=0.0, modal_premium=amount)
    return str({"status": "rider_removed", "term_policy_id": term_policy_id, "adb_rider_amount": 0.0,
                "modal_premium": amount})


@tool(owner="agent", rw="write")
def pay_accelerated_advance_7c43a05b(ctx: ToolContext, term_policy_id: str, term_request_id: str, lien_amount: float,
                                     payout_method: str) -> str:
    """Pay a terminal illness accelerated benefit advance on one Ashgrove term policy and place its lien.

    One advance entry carrying the lien amount supplied is added to the policy's activity history
    under the approved accelerated benefit claim, the policy's outstanding acceleration lien
    becomes that amount, and the claim is marked completed. The receipt below confirms it.

    Args:
        term_policy_id: Id class — the reference number of the term policy being accelerated, read from the term policy lookup before the call.
        term_request_id: Id class — the reference number of the approved accelerated benefit claim, read from the service request lookup before the call.
        lien_amount: Fixed-format class — the lien placed on the policy, in USD, a positive amount with 2 decimal places (rounded half to even to the cent by the tool if more are given).
        payout_method: Enum class — how the advance is paid to the owner: check for a mailed check; direct_deposit for a deposit to the owner's bank account; beneficiary_access_account for settlement into an Ashgrove Beneficiary Access Account.

    Returns:
        A dictionary rendered as text with: status ("advance_paid" on success); advance_id (the
        reference number of the new advance entry); term_policy_id; term_request_id; lien_amount (USD
        with 2 decimal places); payout_method (the method used); request_status (always "completed").
    """
    amount = round(float(lien_amount), 2)
    holding = ctx.find("term_holdings", term_policy_id=term_policy_id)
    owner = holding[0].get("customer_id") if holding else None
    rid = ctx.make_id("tadv_", term_policy_id, term_request_id, amount, payout_method)
    ctx.create("term_transactions", rid, term_txn_id=rid, term_policy_id=term_policy_id, customer_id=owner,
               event_type="term_tiadb_advance_paid", transaction_date=ctx.now()[:10], amount=amount,
               term_request_id=term_request_id, payout_method=payout_method)
    ctx.update("term_holdings", term_policy_id, tiadb_lien_balance=amount)
    ctx.update("term_service_requests", term_request_id, request_status="completed")
    return str({"status": "advance_paid", "advance_id": rid, "term_policy_id": term_policy_id,
                "term_request_id": term_request_id, "lien_amount": amount, "payout_method": payout_method,
                "request_status": "completed"})

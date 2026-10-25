"""Hidden task tools for nfip_commercial_rcbap_claims (Tidemark Flood — NFIP General Property Form and RCBAP).

Each tool performs one atomic write on a General Property Form or RCBAP policy's claim file or premium
account. Values are passed in exactly as worked out beforehand; the tools judge no eligibility and compute
no amounts.
"""

from erlbench import ToolContext, tool


@tool(owner="user", rw="write")
def sign_building_proof_of_loss_d76eab34(ctx: ToolContext, nfipcom_policy_id: str, claim_number: str,
                                         date_of_loss: str, claimed_amount: float) -> str:
    """The authorized signer of the named insured signs and swears a building proof of loss on a flood claim
    under a General Property Form or RCBAP policy, and the proof of loss is received into the claim file
    for the building coverage on today's date. One call records one building proof of loss for the stated
    amount; the claim file then shows the new building proof of loss with its received date and sworn
    amount. Nothing is paid by this action.

    Args:
        nfipcom_policy_id: Id class — the reference number of the General Property Form or RCBAP policy the claim is made under, as returned by the policy lookup for the customer.
        claim_number: Verbatim class — the claim number of the flood claim the proof of loss is sworn for, copied character for character exactly as the customer states it or as it appears on the claim file, preserving digits and punctuation (verbatim).
        date_of_loss: Fixed-format class — the date the flood loss occurred on that claim, written as YYYY-MM-DD.
        claimed_amount: Fixed-format class — the building amount sworn on this proof of loss, in USD, a positive amount with 2 decimal places (cents); it is stored rounded half-up to the cent.

    Returns:
        A dictionary receipt: proof_of_loss_id (text reference of the new claim-file entry), claim_number
        (the claim it was filed under), coverage_part (always BUILDING), claimed_amount (sworn amount in USD,
        2 decimal places) and received_date (YYYY-MM-DD, today). The presence of proof_of_loss_id means the
        proof of loss is on file.
    """
    policies = ctx.find("nfipcom_policies", nfipcom_policy_id=nfipcom_policy_id)
    customer_id = policies[0].get("customer_id") if policies else ""
    amount = round(float(claimed_amount), 2)
    rid = ctx.make_id("npol_", nfipcom_policy_id, claim_number, date_of_loss, amount)
    received = ctx.now()[:10]
    ctx.create("nfipcom_claims", rid, nfipcom_claim_event_id=rid, nfipcom_policy_id=nfipcom_policy_id,
               customer_id=customer_id, event_type="nfipcom_proof_of_loss_filed", claim_number=claim_number,
               date_of_loss=date_of_loss, event_date=received, report_type="NONE", coverage_part="BUILDING",
               building_rcv_loss=0.0, building_acv_loss=0.0, contents_acv_loss=0.0, claimed_amount=amount,
               payment_amount=0.0, payment_ref="", payee="NONE", denial_reason="NONE")
    return str({"proof_of_loss_id": rid, "claim_number": claim_number, "coverage_part": "BUILDING",
                "claimed_amount": amount, "received_date": received})


@tool(owner="agent", rw="write")
def issue_building_claim_payment_972d0779(ctx: ToolContext, nfipcom_policy_id: str, claim_number: str,
                                          date_of_loss: str, payment_amount: float, payee: str) -> str:
    """Issue one building claim payment item on a flood claim under a General Property Form or RCBAP policy.
    One call books one payment for the building coverage on the claim, dated today, with a newly assigned
    payment reference, and adds it to the net claim money paid on the policy; the customer can then be
    told the amount, the payee line and the payment reference.

    Args:
        nfipcom_policy_id: Id class — the reference number of the General Property Form or RCBAP policy the claim is made under, as returned by the policy lookup for the customer.
        claim_number: Verbatim class — the claim number the payment is issued under, copied character for character exactly as it appears on the claim file or as the customer states it, preserving digits and punctuation (verbatim).
        date_of_loss: Fixed-format class — the date the flood loss occurred on that claim, written as YYYY-MM-DD.
        payment_amount: Fixed-format class — the amount of this building payment item, in USD, a positive amount with 2 decimal places (cents); it is stored rounded half-up to the cent.
        payee: Enum class — the payee line printed on the payment: INSURED when no mortgagee of record is shown on the policy, so the named insured alone is paid; INSURED_AND_MORTGAGEE when a mortgagee of record is shown on the policy and the building payment names both; NONE is the marker used on claim entries that are not payments and is never the payee line of a payment item.

    Returns:
        A dictionary receipt: payment_id (text reference of the new claim-file entry), payment_ref (the
        newly assigned payment reference of the check or transfer), claim_number, coverage_part (always
        BUILDING), payment_amount (USD, 2 decimal places), payee (as passed) and issued_date (YYYY-MM-DD,
        today). The presence of payment_ref means the payment was issued.
    """
    policies = ctx.find("nfipcom_policies", nfipcom_policy_id=nfipcom_policy_id)
    customer_id = policies[0].get("customer_id") if policies else ""
    amount = round(float(payment_amount), 2)
    rid = ctx.make_id("npay_", nfipcom_policy_id, claim_number, date_of_loss, amount, payee)
    payment_ref = "CK" + rid[-8:].upper()
    issued = ctx.now()[:10]
    ctx.create("nfipcom_claims", rid, nfipcom_claim_event_id=rid, nfipcom_policy_id=nfipcom_policy_id,
               customer_id=customer_id, event_type="nfipcom_claim_paid", claim_number=claim_number,
               date_of_loss=date_of_loss, event_date=issued, report_type="NONE", coverage_part="BUILDING",
               building_rcv_loss=0.0, building_acv_loss=0.0, contents_acv_loss=0.0, claimed_amount=0.0,
               payment_amount=amount, payment_ref=payment_ref, payee=payee, denial_reason="NONE")
    return str({"payment_id": rid, "payment_ref": payment_ref, "claim_number": claim_number,
                "coverage_part": "BUILDING", "payment_amount": amount, "payee": payee, "issued_date": issued})


@tool(owner="user", rw="write")
def sign_contents_proof_of_loss_65413413(ctx: ToolContext, nfipcom_policy_id: str, claim_number: str,
                                         date_of_loss: str, claimed_amount: float) -> str:
    """The authorized signer of the named insured signs and swears a contents proof of loss on a flood claim
    under a General Property Form or RCBAP policy, and the proof of loss is received into the claim file
    for the contents coverage on today's date. One call records one contents proof of loss for the stated
    amount; the claim file then shows the new contents proof of loss with its received date and sworn
    amount. Nothing is paid by this action.

    Args:
        nfipcom_policy_id: Id class — the reference number of the General Property Form or RCBAP policy the claim is made under, as returned by the policy lookup for the customer.
        claim_number: Verbatim class — the claim number of the flood claim the proof of loss is sworn for, copied character for character exactly as the customer states it or as it appears on the claim file, preserving digits and punctuation (verbatim).
        date_of_loss: Fixed-format class — the date the flood loss occurred on that claim, written as YYYY-MM-DD.
        claimed_amount: Fixed-format class — the contents amount sworn on this proof of loss, in USD, a positive amount with 2 decimal places (cents); it is stored rounded half-up to the cent.

    Returns:
        A dictionary receipt: proof_of_loss_id (text reference of the new claim-file entry), claim_number
        (the claim it was filed under), coverage_part (always CONTENTS), claimed_amount (sworn amount in USD,
        2 decimal places) and received_date (YYYY-MM-DD, today). The presence of proof_of_loss_id means the
        proof of loss is on file.
    """
    policies = ctx.find("nfipcom_policies", nfipcom_policy_id=nfipcom_policy_id)
    customer_id = policies[0].get("customer_id") if policies else ""
    amount = round(float(claimed_amount), 2)
    rid = ctx.make_id("ncpol_", nfipcom_policy_id, claim_number, date_of_loss, amount)
    received = ctx.now()[:10]
    ctx.create("nfipcom_claims", rid, nfipcom_claim_event_id=rid, nfipcom_policy_id=nfipcom_policy_id,
               customer_id=customer_id, event_type="nfipcom_proof_of_loss_filed", claim_number=claim_number,
               date_of_loss=date_of_loss, event_date=received, report_type="NONE", coverage_part="CONTENTS",
               building_rcv_loss=0.0, building_acv_loss=0.0, contents_acv_loss=0.0, claimed_amount=amount,
               payment_amount=0.0, payment_ref="", payee="NONE", denial_reason="NONE")
    return str({"proof_of_loss_id": rid, "claim_number": claim_number, "coverage_part": "CONTENTS",
                "claimed_amount": amount, "received_date": received})


@tool(owner="agent", rw="write")
def issue_contents_claim_payment_a4dbf5ac(ctx: ToolContext, nfipcom_policy_id: str, claim_number: str,
                                          date_of_loss: str, payment_amount: float) -> str:
    """Issue one contents claim payment item to the named insured alone on a flood claim under a General
    Property Form or RCBAP policy. One call books one payment for the contents coverage on the claim, dated
    today, with a newly assigned payment reference, and adds it to the net claim money paid on the policy;
    the customer can then be told the amount and the payment reference.

    Args:
        nfipcom_policy_id: Id class — the reference number of the General Property Form or RCBAP policy the claim is made under, as returned by the policy lookup for the customer.
        claim_number: Verbatim class — the claim number the payment is issued under, copied character for character exactly as it appears on the claim file or as the customer states it, preserving digits and punctuation (verbatim).
        date_of_loss: Fixed-format class — the date the flood loss occurred on that claim, written as YYYY-MM-DD.
        payment_amount: Fixed-format class — the amount of this contents payment item, in USD, a positive amount with 2 decimal places (cents); it is stored rounded half-up to the cent.

    Returns:
        A dictionary receipt: payment_id (text reference of the new claim-file entry), payment_ref (the
        newly assigned payment reference), claim_number, coverage_part (always CONTENTS), payment_amount
        (USD, 2 decimal places), payee (always INSURED) and issued_date (YYYY-MM-DD, today). The presence of
        payment_ref means the payment was issued.
    """
    policies = ctx.find("nfipcom_policies", nfipcom_policy_id=nfipcom_policy_id)
    customer_id = policies[0].get("customer_id") if policies else ""
    amount = round(float(payment_amount), 2)
    rid = ctx.make_id("ncpay_", nfipcom_policy_id, claim_number, date_of_loss, amount)
    payment_ref = "CK" + rid[-8:].upper()
    issued = ctx.now()[:10]
    ctx.create("nfipcom_claims", rid, nfipcom_claim_event_id=rid, nfipcom_policy_id=nfipcom_policy_id,
               customer_id=customer_id, event_type="nfipcom_claim_paid", claim_number=claim_number,
               date_of_loss=date_of_loss, event_date=issued, report_type="NONE", coverage_part="CONTENTS",
               building_rcv_loss=0.0, building_acv_loss=0.0, contents_acv_loss=0.0, claimed_amount=0.0,
               payment_amount=amount, payment_ref=payment_ref, payee="INSURED", denial_reason="NONE")
    return str({"payment_id": rid, "payment_ref": payment_ref, "claim_number": claim_number,
                "coverage_part": "CONTENTS", "payment_amount": amount, "payee": "INSURED", "issued_date": issued})


@tool(owner="agent", rw="write")
def process_cancellation_a892a1e4(ctx: ToolContext, nfipcom_policy_id: str, nfipcom_request_id: str,
                                  cancellation_effective_date: str, risk_credit: float) -> str:
    """Process a signed cancellation request on a General Property Form or RCBAP policy. One call ends the
    policy (status cancelled, with the request's reason, the given cancellation effective date and today
    as the processing date), books the risk premium CANCELLATION credit referencing the request (not booked
    when zero) and, when the policy is mortgage-required, records the written notice of the cancellation
    sent today to the mortgagee of record. The policy's premium balance falls by the credit booked. No
    money is paid out by this action.

    Args:
        nfipcom_policy_id: Id class — the reference number of the policy being cancelled, as returned by the policy lookup for the customer.
        nfipcom_request_id: Id class — the reference number of the signed cancellation request on file for the policy, as returned by the cancellation request lookup.
        cancellation_effective_date: Fixed-format class — the date the cancellation takes effect, written as YYYY-MM-DD.
        risk_credit: Fixed-format class — the risk premium CANCELLATION credit, in USD with 2 decimal places (cents), zero or positive; stored rounded half-up to the cent.

    Returns:
        A dictionary receipt: policy_status (cancelled), cancellation_reason (copied from the request),
        cancellation_effective_date (YYYY-MM-DD), risk_credit (USD, 2 decimal places, the credit booked),
        mortgagee_notified (the mortgagee of record named on the notice, or an empty text when the policy is
        not mortgage-required) and premium_balance (USD, 2 decimal places, the policy balance after the credit;
        negative means money due back to the payor). A policy_status of cancelled means the processing is done.
    """
    policies = ctx.find("nfipcom_policies", nfipcom_policy_id=nfipcom_policy_id)
    policy = policies[0] if policies else {}
    requests = ctx.find("nfipcom_requests", nfipcom_request_id=nfipcom_request_id)
    reason = requests[0].get("cancellation_reason") if requests else "NONE"
    customer_id = policy.get("customer_id", "")
    today = ctx.now()[:10]
    amount = round(float(risk_credit), 2)
    if amount > 0:
        rid = ctx.make_id("nccr_", nfipcom_policy_id, nfipcom_request_id, "RISK_PREMIUM", amount)
        ctx.create("nfipcom_billing", rid, nfipcom_billing_id=rid, nfipcom_policy_id=nfipcom_policy_id,
                   customer_id=customer_id, event_type="nfipcom_premium_credit", term_start=policy.get("term_start", ""),
                   component="RISK_PREMIUM", charge_basis="CANCELLATION", amount=amount, posted_date=today,
                   reference_id=nfipcom_request_id, payment_ref="", payment_method="NONE", payee="NONE")
    else:
        amount = 0.0
    notified = ""
    if policy.get("mortgage_required") in (True, "True", "true"):
        notified = policy.get("mortgagee_name", "")
        nid = ctx.make_id("ncmn_", nfipcom_policy_id, nfipcom_request_id, today)
        ctx.create("nfipcom_changes", nid, nfipcom_change_id=nid, nfipcom_policy_id=nfipcom_policy_id,
                   customer_id=customer_id, event_type="nfipcom_mortgagee_notice", change_type="NONE",
                   change_effective_date="", recorded_date=today, new_building_coverage=0, new_contents_coverage=0,
                   new_building_deductible=0, new_contents_deductible=0, new_mortgagee_name=notified,
                   new_loan_number=policy.get("loan_number", ""), loan_closing_date="", rerated_risk_premium=0.0,
                   rerated_icc_premium=0.0, ec_survey_date="", ec_building_diagram="NONE", ec_first_floor_height_ft="",
                   ec_lowest_floor_elevation="", ec_base_flood_elevation="", ec_applied=False, renewal_term_start="",
                   indicated_risk_premium=0.0, notice_reason="CANCELLATION")
    balance = round(float(policy.get("premium_balance") or 0) - amount, 2)
    ctx.update("nfipcom_policies", nfipcom_policy_id, status="cancelled", cancellation_reason=reason,
               cancellation_effective_date=cancellation_effective_date, closed_date=today, premium_balance=balance)
    return str({"policy_status": "cancelled", "cancellation_reason": reason,
                "cancellation_effective_date": cancellation_effective_date, "risk_credit": amount,
                "mortgagee_notified": notified, "premium_balance": balance})


@tool(owner="agent", rw="write")
def disburse_cancellation_refund_941cdf13(ctx: ToolContext, nfipcom_policy_id: str, nfipcom_request_id: str,
                                          icc_credit: float, rfa_credit: float, hfiaa_credit: float,
                                          policy_fee_credit: float, probation_credit: float, refund_amount: float,
                                          payee: str) -> str:
    """Disburse the refund of a cancelled General Property Form or RCBAP policy. One call books the
    CANCELLATION credits for the ICC premium, the Reserve Fund Assessment, the HFIAA surcharge, the Federal
    Policy Fee and the probation surcharge, each referencing the cancellation request and none booked when
    zero, and issues one refund payment for the given amount to the given payee, referencing the request,
    with a newly assigned refund reference. The policy's premium balance falls by the credits and rises by
    the refund paid out. The customer can then be told the refund amount, payee and reference.

    Args:
        nfipcom_policy_id: Id class — the reference number of the cancelled policy, as returned by the policy lookup for the customer.
        nfipcom_request_id: Id class — the reference number of the signed cancellation request the refund settles, as returned by the cancellation request lookup.
        icc_credit: Fixed-format class — the ICC premium CANCELLATION credit, in USD with 2 decimal places (cents), zero or positive; stored rounded half-up to the cent.
        rfa_credit: Fixed-format class — the Reserve Fund Assessment CANCELLATION credit, in USD with 2 decimal places (cents), zero or positive; stored rounded half-up to the cent.
        hfiaa_credit: Fixed-format class — the HFIAA surcharge CANCELLATION credit, in USD with 2 decimal places (cents), zero or positive; stored rounded half-up to the cent.
        policy_fee_credit: Fixed-format class — the Federal Policy Fee CANCELLATION credit, in USD with 2 decimal places (cents), zero or positive; stored rounded half-up to the cent.
        probation_credit: Fixed-format class — the probation surcharge CANCELLATION credit, in USD with 2 decimal places (cents), zero or positive; stored rounded half-up to the cent.
        refund_amount: Fixed-format class — the refund paid out, in USD with 2 decimal places (cents), positive; stored rounded half-up to the cent.
        payee: Enum class — who receives the refund: INSURED when the named insured is the payor of record of the premium; LENDER_ESCROW when the lender paid the premium from the escrow account and is the payor of record; NONE is the marker used on ledger entries that are not refunds and is never the payee of a refund.

    Returns:
        A dictionary receipt: refund_id (text reference of the refund entry), payment_ref (the newly assigned
        refund check or transfer reference), refund_amount (USD, 2 decimal places), payee (as passed),
        credits_booked (USD, 2 decimal places, the total of the credits booked by this call) and
        premium_balance (USD, 2 decimal places, the policy balance after the credits and the refund). The
        presence of payment_ref means the refund was issued.
    """
    policies = ctx.find("nfipcom_policies", nfipcom_policy_id=nfipcom_policy_id)
    policy = policies[0] if policies else {}
    customer_id = policy.get("customer_id", "")
    today = ctx.now()[:10]
    booked = 0.0
    for component, value in (("ICC_PREMIUM", icc_credit), ("RESERVE_FUND_ASSESSMENT", rfa_credit),
                             ("HFIAA_SURCHARGE", hfiaa_credit), ("FEDERAL_POLICY_FEE", policy_fee_credit),
                             ("PROBATION_SURCHARGE", probation_credit)):
        credit = round(float(value), 2)
        if credit <= 0:
            continue
        cid = ctx.make_id("ncrf_", nfipcom_policy_id, nfipcom_request_id, component, credit)
        ctx.create("nfipcom_billing", cid, nfipcom_billing_id=cid, nfipcom_policy_id=nfipcom_policy_id,
                   customer_id=customer_id, event_type="nfipcom_premium_credit", term_start=policy.get("term_start", ""),
                   component=component, charge_basis="CANCELLATION", amount=credit, posted_date=today,
                   reference_id=nfipcom_request_id, payment_ref="", payment_method="NONE", payee="NONE")
        booked = round(booked + credit, 2)
    amount = round(float(refund_amount), 2)
    rid = ctx.make_id("ncrd_", nfipcom_policy_id, nfipcom_request_id, amount, payee)
    payment_ref = "RF" + rid[-8:].upper()
    ctx.create("nfipcom_billing", rid, nfipcom_billing_id=rid, nfipcom_policy_id=nfipcom_policy_id,
               customer_id=customer_id, event_type="nfipcom_refund_disbursed", term_start="", component="TOTAL",
               charge_basis="REFUND", amount=amount, posted_date=today, reference_id=nfipcom_request_id,
               payment_ref=payment_ref, payment_method="NONE", payee=payee)
    balance = round(float(policy.get("premium_balance") or 0) - booked + amount, 2)
    ctx.update("nfipcom_policies", nfipcom_policy_id, premium_balance=balance)
    return str({"refund_id": rid, "payment_ref": payment_ref, "refund_amount": amount, "payee": payee,
                "credits_booked": booked, "premium_balance": balance})

"""Shared tools for env_0059_residential_mortgage_lender (Larkspur Home Lending).

Always-on tools reused by every difficulty: one lookup per record type (the customer lookup doubles
as the identity entry), the identity-verification write and the transfer to a human representative.
Scenario operational constants live here: verification passes when at least 2 identity credentials
match (K = 2); a customer who has explicitly asked for a human 2 times is handed off as
CUSTOMER_REQUESTED (R = 2).
"""

from erlbench import ToolContext, tool


@tool(owner="agent", rw="read")
def find_customers(ctx: ToolContext, customer_id: str = "", phone_number: str = "", email: str = "",
                   full_name: str = "", re_license_number: str = "") -> str:
    """Find the customer profile that this call is about, for a borrower or for a real estate agent who works with Larkspur. Search by the customer reference number, or by what the caller can naturally tell you: phone number, email address, full name or, for an agent, the real estate license number. Every criterion is optional; give whichever you have. The profile returned shows the customer type, contact details, date of birth and last four SSN digits (borrowers), license number (agents), mailing ZIP code and the date the profile was opened. Finding a profile does not verify the caller's identity.

    Args:
        customer_id: Customer reference number; leave "" if unknown.
        phone_number: Phone number the caller gives, 10 digits; leave "" if not provided.
        email: Email address the caller gives; leave "" if not provided.
        full_name: Full name the caller gives; leave "" if not provided.
        re_license_number: Real estate license number an agent gives, exactly as stated (e.g. SAL.2019004871); leave "" if not provided.
    """
    match = {k: v for k, v in {"customer_id": customer_id, "phone_number": phone_number, "email": email,
                               "full_name": full_name, "re_license_number": re_license_number}.items() if v}
    if not match:
        return "Error: provide at least one reference number or detail to find the customer."
    rows = ctx.fuzzy_find("customers", **match)
    if not rows:
        return f"No customer matches {match}."
    if len(rows) > 1:
        return f"Error: {len(rows)} customers match {match}; ask the caller for one more detail."
    return str(rows[0])


@tool(owner="agent", rw="write")
def verify_customer_identity(ctx: ToolContext, customer_id: str, phone_number: str = "", email: str = "",
                             date_of_birth: str = "", ssn_last4: str = "", mailing_zip: str = "",
                             re_license_number: str = "") -> str:
    """Verify the caller's identity against the customer profile and record the outcome. Identity must be verified before any loan, lock, appraisal, credit, closing, pre-approval or buydown business is discussed or transacted for the customer. This tool makes the comparison itself: it checks each piece of identity information the caller states against the profile and passes only when at least 2 of them match. The customer reference number only selects the profile and never counts as a match. Pass exactly what the caller said for each item they gave and leave the rest blank. The result is recorded; if a first attempt fails and a later attempt with more information passes, the customer stays verified.

    Args:
        customer_id: Customer reference number from the customer lookup. Required; used only to open the profile and never counted as a match.
        phone_number: Phone number the caller states, 10 digits with no punctuation; leave "" if not stated.
        email: Email address the caller states; leave "" if not stated.
        date_of_birth: Date of birth the caller states, YYYY-MM-DD; leave "" if not stated.
        ssn_last4: Last four digits of the Social Security number the caller states; leave "" if not stated.
        mailing_zip: 5-digit ZIP code of the mailing address the caller states; leave "" if not stated.
        re_license_number: Real estate license number an agent states, exactly as given; leave "" if not stated.
    """
    if not customer_id:
        return "Error: customer_id is required; look the customer up first and pass their reference number."
    rows = ctx.find("customers", customer_id=customer_id)
    if not rows:
        return f"Error: no customer {customer_id}; cannot verify."
    rec = rows[0]
    supplied = {"phone_number": phone_number, "email": email, "date_of_birth": date_of_birth,
                "ssn_last4": ssn_last4, "mailing_zip": mailing_zip, "re_license_number": re_license_number}
    matched = sum(1 for field, value in supplied.items()
                  if value and rec.get(field) and str(rec.get(field)).strip().lower() == str(value).strip().lower())
    verified = matched >= 2
    rid = ctx.make_id("ver_", customer_id)
    prior = ctx.find("identity_verifications", verification_id=rid)
    verified = verified or bool(prior and prior[0].get("verified"))
    if prior:
        ctx.update("identity_verifications", rid, verified=verified, verified_at=ctx.now())
    else:
        ctx.create("identity_verifications", rid, verification_id=rid, customer_id=customer_id,
                   verified=verified, verified_at=ctx.now())
    return (f"Identity verified for {customer_id} ({matched} item(s) matched)." if verified
            else f"Identity NOT verified for {customer_id} (only {matched} of the required 2 items matched). Ask the caller for another detail on file and try again.")


@tool(owner="agent", rw="write")
def transfer_to_human_agent(ctx: ToolContext, customer_id: str, reason: str) -> str:
    """Hand the customer over to a human Larkspur representative and record the handoff with its reason. Use POLICY_NOT_COVERED when no Larkspur policy lets you resolve what the customer needs; use CUSTOMER_REQUESTED once the customer has explicitly asked for a human representative 2 times.

    Args:
        customer_id: Customer reference number from the customer lookup; the profile must exist.
        reason: Reason for the handoff, exactly one of POLICY_NOT_COVERED or CUSTOMER_REQUESTED (never free text).
    """
    allowed = {"POLICY_NOT_COVERED", "CUSTOMER_REQUESTED"}
    if reason not in allowed:
        return f"Error: unknown handoff reason '{reason}'. Valid: {', '.join(sorted(allowed))}."
    if not ctx.find("customers", customer_id=customer_id):
        return f"Error: no customer {customer_id}; cannot record the handoff."
    rid = ctx.make_id("hof_", customer_id, reason)
    ctx.create("handoff_log", rid, handoff_id=rid, customer_id=customer_id, reason=reason, created_at=ctx.now())
    return f"Handoff to a human representative recorded for {customer_id} ({reason})."


@tool(owner="agent", rw="read")
def find_loan_files(ctx: ToolContext, loan_file_id: str = "", customer_id: str = "", preapproval_id: str = "", agent_customer_id: str = "") -> str:
    """Look up mortgage loan files: the loan program, status, purpose, occupancy, property, loan amounts, credit and income facts, key TRID dates (application, intent to proceed, contract and scheduled closing), concessions, and the prepaid fee and tolerance cure balances. Every criterion is optional; supply whichever reference numbers you already hold and all matching records are returned, or a short note when nothing matches.

    Args:
        loan_file_id: Reference number of the mortgage loan file (one application for one property); leave "" if unknown.
        customer_id: Primary borrower who owns the file; leave "" if unknown.
        preapproval_id: Pre-approval the application was converted from; empty if none; leave "" if unknown.
        agent_customer_id: Buyer's real estate agent working with the borrower; empty if none; leave "" if unknown.
    """
    match = {k: v for k, v in {"loan_file_id": loan_file_id, "customer_id": customer_id, "preapproval_id": preapproval_id, "agent_customer_id": agent_customer_id}.items() if v}
    rows = ctx.find("loan_files", **match)
    return str(rows) if rows else f"No loan_files records for {match}."

@tool(owner="agent", rw="read")
def find_loan_fee_ledger(ctx: ToolContext, loan_fee_entry_id: str = "", loan_file_id: str = "", customer_id: str = "", original_fee_entry_id: str = "") -> str:
    """Look up the up-front fee history of a loan file: credit report fee charges, application fee collections, refunds and fees credited back at closing, with amounts, dates and payment methods. Every criterion is optional; supply whichever reference numbers you already hold and all matching records are returned, or a short note when nothing matches.

    Args:
        loan_fee_entry_id: Reference number of the fee ledger entry; leave "" if unknown.
        loan_file_id: Loan file the fee belongs to; leave "" if unknown.
        customer_id: Borrower who paid or is credited; leave "" if unknown.
        original_fee_entry_id: For a refund or closing application, the fee entry being refunded or applied; empty on charges; leave "" if unknown.
    """
    match = {k: v for k, v in {"loan_fee_entry_id": loan_fee_entry_id, "loan_file_id": loan_file_id, "customer_id": customer_id, "original_fee_entry_id": original_fee_entry_id}.items() if v}
    rows = ctx.find("loan_fee_ledger", **match)
    return str(rows) if rows else f"No loan_fee_ledger records for {match}."

@tool(owner="agent", rw="read")
def find_loan_disclosures(ctx: ToolContext, disclosure_id: str = "", loan_file_id: str = "", customer_id: str = "") -> str:
    """Look up the TRID disclosures of a loan file: Loan Estimates, revised Loan Estimates, intents to proceed, Closing Disclosures and corrected Closing Disclosures, with issue and receipt dates, delivery method, changed-circumstance reason, APR, rate and the disclosed cost totals. Every criterion is optional; supply whichever reference numbers you already hold and all matching records are returned, or a short note when nothing matches.

    Args:
        disclosure_id: Reference number of the disclosure record; leave "" if unknown.
        loan_file_id: Loan file disclosed; leave "" if unknown.
        customer_id: Borrower the disclosure was delivered to; leave "" if unknown.
    """
    match = {k: v for k, v in {"disclosure_id": disclosure_id, "loan_file_id": loan_file_id, "customer_id": customer_id}.items() if v}
    rows = ctx.find("loan_disclosures", **match)
    return str(rows) if rows else f"No loan_disclosures records for {match}."

@tool(owner="agent", rw="read")
def find_loan_conditions(ctx: ToolContext, condition_id: str = "", loan_file_id: str = "", customer_id: str = "", source_condition_id: str = "") -> str:
    """Look up underwriting conditions on a loan file: each condition issued, cleared or waived, with its class, due date, document date and resolution. Every criterion is optional; supply whichever reference numbers you already hold and all matching records are returned, or a short note when nothing matches.

    Args:
        condition_id: Reference number of the condition record; leave "" if unknown.
        loan_file_id: Loan file the condition is on; leave "" if unknown.
        customer_id: Borrower; leave "" if unknown.
        source_condition_id: On a cleared or waived record, the issued condition it resolves; empty on the issued record; leave "" if unknown.
    """
    match = {k: v for k, v in {"condition_id": condition_id, "loan_file_id": loan_file_id, "customer_id": customer_id, "source_condition_id": source_condition_id}.items() if v}
    rows = ctx.find("loan_conditions", **match)
    return str(rows) if rows else f"No loan_conditions records for {match}."

@tool(owner="agent", rw="read")
def find_loan_tolerance_cures(ctx: ToolContext, cure_entry_id: str = "", loan_file_id: str = "", customer_id: str = "", baseline_disclosure_id: str = "", final_disclosure_id: str = "", source_cure_entry_id: str = "") -> str:
    """Look up tolerance cures on a loan file: cures assessed for charges that exceeded their Loan Estimate tolerance and the payments that settled them. Every criterion is optional; supply whichever reference numbers you already hold and all matching records are returned, or a short note when nothing matches.

    Args:
        cure_entry_id: Reference number of the tolerance cure entry; leave "" if unknown.
        loan_file_id: Loan file; leave "" if unknown.
        customer_id: Borrower owed the cure; leave "" if unknown.
        baseline_disclosure_id: Loan Estimate whose amounts are the good-faith baseline; leave "" if unknown.
        final_disclosure_id: Closing Disclosure whose amounts exceeded the baseline; leave "" if unknown.
        source_cure_entry_id: On a payment entry, the assessed cure it pays; empty on the assessment; leave "" if unknown.
    """
    match = {k: v for k, v in {"cure_entry_id": cure_entry_id, "loan_file_id": loan_file_id, "customer_id": customer_id, "baseline_disclosure_id": baseline_disclosure_id, "final_disclosure_id": final_disclosure_id, "source_cure_entry_id": source_cure_entry_id}.items() if v}
    rows = ctx.find("loan_tolerance_cures", **match)
    return str(rows) if rows else f"No loan_tolerance_cures records for {match}."

@tool(owner="agent", rw="read")
def find_rate_locks(ctx: ToolContext, lock_id: str = "", customer_id: str = "", loan_file_id: str = "") -> str:
    """Look up rate lock commitments: the lock term, status, lock and expiration dates, locked rate and price, the loan amount the lock is priced on, float-down use, and the outstanding lock cost and deposit balances. Every criterion is optional; supply whichever reference numbers you already hold and all matching records are returned, or a short note when nothing matches.

    Args:
        lock_id: Reference number of the rate lock commitment; leave "" if unknown.
        customer_id: Borrower who holds the lock; leave "" if unknown.
        loan_file_id: Loan file the lock protects; leave "" if unknown.
    """
    match = {k: v for k, v in {"lock_id": lock_id, "customer_id": customer_id, "loan_file_id": loan_file_id}.items() if v}
    rows = ctx.find("rate_locks", **match)
    return str(rows) if rows else f"No rate_locks records for {match}."

@tool(owner="agent", rw="read")
def find_lock_requests(ctx: ToolContext, lock_request_id: str = "", lock_id: str = "", customer_id: str = "") -> str:
    """Look up the lock desk request log: every time-stamped lock, extension, relock, float-down, program change or cancellation request, with channel, date, time, requested rate and term, and the rate-sheet price at that moment. Every criterion is optional; supply whichever reference numbers you already hold and all matching records are returned, or a short note when nothing matches.

    Args:
        lock_request_id: Reference number of the logged lock desk request; leave "" if unknown.
        lock_id: Lock the request concerns; leave "" if unknown.
        customer_id: Borrower; leave "" if unknown.
    """
    match = {k: v for k, v in {"lock_request_id": lock_request_id, "lock_id": lock_id, "customer_id": customer_id}.items() if v}
    rows = ctx.find("lock_requests", **match)
    return str(rows) if rows else f"No lock_requests records for {match}."

@tool(owner="agent", rw="read")
def find_lock_pricing_events(ctx: ToolContext, lock_pricing_id: str = "", lock_id: str = "", customer_id: str = "", source_pricing_id: str = "") -> str:
    """Look up lock pricing entries: extensions, relock fees, float-down fees, waivers and closing settlements, with days, points, dollar cost, who bears it and the resulting expiration date or rate. Every criterion is optional; supply whichever reference numbers you already hold and all matching records are returned, or a short note when nothing matches.

    Args:
        lock_pricing_id: Reference number of the lock pricing entry; leave "" if unknown.
        lock_id: Lock priced; leave "" if unknown.
        customer_id: Borrower; leave "" if unknown.
        source_pricing_id: For a waiver or closing settlement, the pricing entry it offsets; empty otherwise; leave "" if unknown.
    """
    match = {k: v for k, v in {"lock_pricing_id": lock_pricing_id, "lock_id": lock_id, "customer_id": customer_id, "source_pricing_id": source_pricing_id}.items() if v}
    rows = ctx.find("lock_pricing_events", **match)
    return str(rows) if rows else f"No lock_pricing_events records for {match}."

@tool(owner="agent", rw="read")
def find_lock_deposits(ctx: ToolContext, lock_deposit_entry_id: str = "", lock_id: str = "", customer_id: str = "", source_deposit_entry_id: str = "") -> str:
    """Look up lock deposits for extended locks: deposits received and any credit at closing, refund or forfeiture. Every criterion is optional; supply whichever reference numbers you already hold and all matching records are returned, or a short note when nothing matches.

    Args:
        lock_deposit_entry_id: Reference number of the deposit entry; leave "" if unknown.
        lock_id: Lock the deposit secures; leave "" if unknown.
        customer_id: Borrower; leave "" if unknown.
        source_deposit_entry_id: For a credit, refund or forfeiture, the collected deposit entry it disposes of; empty on collection; leave "" if unknown.
    """
    match = {k: v for k, v in {"lock_deposit_entry_id": lock_deposit_entry_id, "lock_id": lock_id, "customer_id": customer_id, "source_deposit_entry_id": source_deposit_entry_id}.items() if v}
    rows = ctx.find("lock_deposits", **match)
    return str(rows) if rows else f"No lock_deposits records for {match}."

@tool(owner="agent", rw="read")
def find_lock_disputes(ctx: ToolContext, lock_dispute_id: str = "", lock_id: str = "", customer_id: str = "", disputed_pricing_id: str = "", matched_request_id: str = "", source_dispute_id: str = "") -> str:
    """Look up rate lock disputes: what was disputed, when it was filed, the claimed request date and rate, and the decision with the logged request relied on. Every criterion is optional; supply whichever reference numbers you already hold and all matching records are returned, or a short note when nothing matches.

    Args:
        lock_dispute_id: Reference number of the dispute record; leave "" if unknown.
        lock_id: Lock disputed; leave "" if unknown.
        customer_id: Borrower who disputes; leave "" if unknown.
        disputed_pricing_id: Pricing entry the dispute is about, for extension or relock disputes; empty otherwise; leave "" if unknown.
        matched_request_id: Logged lock request relied on by the decision; empty when none; leave "" if unknown.
        source_dispute_id: On a resolution record, the filing record it decides; empty on the filing record; leave "" if unknown.
    """
    match = {k: v for k, v in {"lock_dispute_id": lock_dispute_id, "lock_id": lock_id, "customer_id": customer_id, "disputed_pricing_id": disputed_pricing_id, "matched_request_id": matched_request_id, "source_dispute_id": source_dispute_id}.items() if v}
    rows = ctx.find("lock_disputes", **match)
    return str(rows) if rows else f"No lock_disputes records for {match}."

@tool(owner="agent", rw="read")
def find_appraisal_orders(ctx: ToolContext, appraisal_order_id: str = "", customer_id: str = "", loan_file_id: str = "") -> str:
    """Look up appraisal orders: report type, status, order reason, order and due dates, inspection, completion and delivery dates, appraised value, property size facts, seller acquisition history, timing waiver and the net appraisal charges paid. Every criterion is optional; supply whichever reference numbers you already hold and all matching records are returned, or a short note when nothing matches.

    Args:
        appraisal_order_id: Reference number of the appraisal order; leave "" if unknown.
        customer_id: Borrower on whose loan the appraisal is ordered; leave "" if unknown.
        loan_file_id: Loan file the appraisal supports; leave "" if unknown.
    """
    match = {k: v for k, v in {"appraisal_order_id": appraisal_order_id, "customer_id": customer_id, "loan_file_id": loan_file_id}.items() if v}
    rows = ctx.find("appraisal_orders", **match)
    return str(rows) if rows else f"No appraisal_orders records for {match}."

@tool(owner="agent", rw="read")
def find_appraisal_fee_ledger(ctx: ToolContext, appraisal_fee_entry_id: str = "", appraisal_order_id: str = "", customer_id: str = "", original_fee_entry_id: str = "") -> str:
    """Look up appraisal charges and refunds on an order, by component, amount, date and refund reason. Every criterion is optional; supply whichever reference numbers you already hold and all matching records are returned, or a short note when nothing matches.

    Args:
        appraisal_fee_entry_id: Reference number of the appraisal fee entry; leave "" if unknown.
        appraisal_order_id: Order charged; leave "" if unknown.
        customer_id: Borrower charged or refunded; leave "" if unknown.
        original_fee_entry_id: For a refund, the charge entry refunded; empty on charges; leave "" if unknown.
    """
    match = {k: v for k, v in {"appraisal_fee_entry_id": appraisal_fee_entry_id, "appraisal_order_id": appraisal_order_id, "customer_id": customer_id, "original_fee_entry_id": original_fee_entry_id}.items() if v}
    rows = ctx.find("appraisal_fee_ledger", **match)
    return str(rows) if rows else f"No appraisal_fee_ledger records for {match}."

@tool(owner="agent", rw="read")
def find_appraisal_reconsiderations(ctx: ToolContext, rov_id: str = "", appraisal_order_id: str = "", customer_id: str = "", source_rov_id: str = "") -> str:
    """Look up reconsideration of value requests on an appraisal and their outcomes. Every criterion is optional; supply whichever reference numbers you already hold and all matching records are returned, or a short note when nothing matches.

    Args:
        rov_id: Reference number of the reconsideration-of-value record; leave "" if unknown.
        appraisal_order_id: Order whose value is challenged; leave "" if unknown.
        customer_id: Borrower who requested the reconsideration; leave "" if unknown.
        source_rov_id: On a decision record, the submission it decides; empty on the submission; leave "" if unknown.
    """
    match = {k: v for k, v in {"rov_id": rov_id, "appraisal_order_id": appraisal_order_id, "customer_id": customer_id, "source_rov_id": source_rov_id}.items() if v}
    rows = ctx.find("appraisal_reconsiderations", **match)
    return str(rows) if rows else f"No appraisal_reconsiderations records for {match}."

@tool(owner="agent", rw="read")
def find_closing_credits(ctx: ToolContext, credit_award_id: str = "", customer_id: str = "", loan_file_id: str = "") -> str:
    """Look up closing cost credits reserved against loan files: the credit program, status, qualifying basis, reservation, verification and expiration dates, award amount, guarantee dates and the remaining credit balance. Every criterion is optional; supply whichever reference numbers you already hold and all matching records are returned, or a short note when nothing matches.

    Args:
        credit_award_id: Reference number of the closing cost credit award; leave "" if unknown.
        customer_id: Borrower who holds the credit; leave "" if unknown.
        loan_file_id: Loan file the credit is reserved against; leave "" if unknown.
    """
    match = {k: v for k, v in {"credit_award_id": credit_award_id, "customer_id": customer_id, "loan_file_id": loan_file_id}.items() if v}
    rows = ctx.find("closing_credits", **match)
    return str(rows) if rows else f"No closing_credits records for {match}."

@tool(owner="agent", rw="read")
def find_credit_ledger(ctx: ToolContext, credit_entry_id: str = "", credit_award_id: str = "", customer_id: str = "", disclosure_id: str = "", source_entry_id: str = "") -> str:
    """Look up the history of a closing cost credit: awards, guarantee payouts, amounts applied on the Closing Disclosure by cost category, reductions and forfeitures. Every criterion is optional; supply whichever reference numbers you already hold and all matching records are returned, or a short note when nothing matches.

    Args:
        credit_entry_id: Reference number of the credit ledger entry; leave "" if unknown.
        credit_award_id: Credit award the entry belongs to; leave "" if unknown.
        customer_id: Borrower; leave "" if unknown.
        disclosure_id: Closing Disclosure on which the credit was applied; empty on other entries; leave "" if unknown.
        source_entry_id: For an application, reduction or forfeiture, the award or payout entry it draws on; empty on awards and payouts; leave "" if unknown.
    """
    match = {k: v for k, v in {"credit_entry_id": credit_entry_id, "credit_award_id": credit_award_id, "customer_id": customer_id, "disclosure_id": disclosure_id, "source_entry_id": source_entry_id}.items() if v}
    rows = ctx.find("credit_ledger", **match)
    return str(rows) if rows else f"No credit_ledger records for {match}."

@tool(owner="agent", rw="read")
def find_closings(ctx: ToolContext, closing_id: str = "", customer_id: str = "", loan_file_id: str = "", lock_id: str = "") -> str:
    """Look up closing and funding engagements: closing method, status, settlement agent, scheduled and estimated funding dates, document draw and expiration dates, signing, rescission and disbursement dates, and the prepaid interest, funded and closing fee balances. Every criterion is optional; supply whichever reference numbers you already hold and all matching records are returned, or a short note when nothing matches.

    Args:
        closing_id: Reference number of the closing and funding engagement; leave "" if unknown.
        customer_id: Borrower; leave "" if unknown.
        loan_file_id: Loan file being closed; leave "" if unknown.
        lock_id: Rate lock the loan closes under; empty when floating; leave "" if unknown.
    """
    match = {k: v for k, v in {"closing_id": closing_id, "customer_id": customer_id, "loan_file_id": loan_file_id, "lock_id": lock_id}.items() if v}
    rows = ctx.find("closings", **match)
    return str(rows) if rows else f"No closings records for {match}."

@tool(owner="agent", rw="read")
def find_funding_wires(ctx: ToolContext, funding_wire_id: str = "", closing_id: str = "", customer_id: str = "", source_wire_id: str = "") -> str:
    """Look up funding wires sent to settlement agents and any returns, with amounts, dates, times and Fedwire references. Every criterion is optional; supply whichever reference numbers you already hold and all matching records are returned, or a short note when nothing matches.

    Args:
        funding_wire_id: Reference number of the wire entry; leave "" if unknown.
        closing_id: Closing funded; leave "" if unknown.
        customer_id: Borrower; leave "" if unknown.
        source_wire_id: For a return, the outgoing wire returned; empty otherwise; leave "" if unknown.
    """
    match = {k: v for k, v in {"funding_wire_id": funding_wire_id, "closing_id": closing_id, "customer_id": customer_id, "source_wire_id": source_wire_id}.items() if v}
    rows = ctx.find("funding_wires", **match)
    return str(rows) if rows else f"No funding_wires records for {match}."

@tool(owner="agent", rw="read")
def find_funding_interest_ledger(ctx: ToolContext, interest_entry_id: str = "", closing_id: str = "", customer_id: str = "", source_interest_entry_id: str = "") -> str:
    """Look up prepaid per diem interest charged at closing and any refunds, with the days covered and the daily amount. Every criterion is optional; supply whichever reference numbers you already hold and all matching records are returned, or a short note when nothing matches.

    Args:
        interest_entry_id: Reference number of the prepaid interest entry; leave "" if unknown.
        closing_id: Closing; leave "" if unknown.
        customer_id: Borrower; leave "" if unknown.
        source_interest_entry_id: For a refund, the charge entry corrected; empty on charges; leave "" if unknown.
    """
    match = {k: v for k, v in {"interest_entry_id": interest_entry_id, "closing_id": closing_id, "customer_id": customer_id, "source_interest_entry_id": source_interest_entry_id}.items() if v}
    rows = ctx.find("funding_interest_ledger", **match)
    return str(rows) if rows else f"No funding_interest_ledger records for {match}."

@tool(owner="agent", rw="read")
def find_funding_fee_ledger(ctx: ToolContext, closing_fee_entry_id: str = "", closing_id: str = "", customer_id: str = "", source_fee_entry_id: str = "") -> str:
    """Look up closing fees charged for a closing (closing method, after-hours, courier, wire, power of attorney review, document redraw) and any reversals. Every criterion is optional; supply whichever reference numbers you already hold and all matching records are returned, or a short note when nothing matches.

    Args:
        closing_fee_entry_id: Reference number of the closing fee entry; leave "" if unknown.
        closing_id: Closing; leave "" if unknown.
        customer_id: Borrower; leave "" if unknown.
        source_fee_entry_id: For a reversal, the fee entry reversed; empty on charges; leave "" if unknown.
    """
    match = {k: v for k, v in {"closing_fee_entry_id": closing_fee_entry_id, "closing_id": closing_id, "customer_id": customer_id, "source_fee_entry_id": source_fee_entry_id}.items() if v}
    rows = ctx.find("funding_fee_ledger", **match)
    return str(rows) if rows else f"No funding_fee_ledger records for {match}."

@tool(owner="agent", rw="read")
def find_funding_disputes(ctx: ToolContext, funding_dispute_id: str = "", closing_id: str = "", customer_id: str = "", disputed_entry_id: str = "", source_dispute_id: str = "") -> str:
    """Look up funding disputes and their decisions. Every criterion is optional; supply whichever reference numbers you already hold and all matching records are returned, or a short note when nothing matches.

    Args:
        funding_dispute_id: Reference number of the funding dispute record; leave "" if unknown.
        closing_id: Closing disputed; leave "" if unknown.
        customer_id: Borrower; leave "" if unknown.
        disputed_entry_id: Interest or fee entry disputed, when the dispute is about one entry; empty otherwise; leave "" if unknown.
        source_dispute_id: On a resolution record, the filing record it decides; empty on the filing record; leave "" if unknown.
    """
    match = {k: v for k, v in {"funding_dispute_id": funding_dispute_id, "closing_id": closing_id, "customer_id": customer_id, "disputed_entry_id": disputed_entry_id, "source_dispute_id": source_dispute_id}.items() if v}
    rows = ctx.find("funding_disputes", **match)
    return str(rows) if rows else f"No funding_disputes records for {match}."

@tool(owner="agent", rw="read")
def find_preapprovals(ctx: ToolContext, preapproval_id: str = "", customer_id: str = "", agent_customer_id: str = "") -> str:
    """Look up mortgage pre-approvals: level, status, target program, approved amounts, expiration, credit pull, the named real estate agent and sharing authorization, and any Lock & Shop rate hold. Every criterion is optional; supply whichever reference numbers you already hold and all matching records are returned, or a short note when nothing matches.

    Args:
        preapproval_id: Reference number of the pre-approval; leave "" if unknown.
        customer_id: Borrower the pre-approval is for; leave "" if unknown.
        agent_customer_id: Buyer's real estate agent named by the borrower; empty if none; leave "" if unknown.
    """
    match = {k: v for k, v in {"preapproval_id": preapproval_id, "customer_id": customer_id, "agent_customer_id": agent_customer_id}.items() if v}
    rows = ctx.find("preapprovals", **match)
    return str(rows) if rows else f"No preapprovals records for {match}."

@tool(owner="agent", rw="read")
def find_preapproval_letters(ctx: ToolContext, letter_id: str = "", preapproval_id: str = "", customer_id: str = "", recipient_agent_customer_id: str = "", source_letter_id: str = "") -> str:
    """Look up pre-approval letters issued or voided, with letter price, property, who asked and the agent it was sent to. Every criterion is optional; supply whichever reference numbers you already hold and all matching records are returned, or a short note when nothing matches.

    Args:
        letter_id: Reference number of the pre-approval letter; leave "" if unknown.
        preapproval_id: Pre-approval the letter is issued under; leave "" if unknown.
        customer_id: Borrower; leave "" if unknown.
        recipient_agent_customer_id: Agent the letter was sent to; empty when sent only to the borrower; leave "" if unknown.
        source_letter_id: On a void record, the letter voided; empty otherwise; leave "" if unknown.
    """
    match = {k: v for k, v in {"letter_id": letter_id, "preapproval_id": preapproval_id, "customer_id": customer_id, "recipient_agent_customer_id": recipient_agent_customer_id, "source_letter_id": source_letter_id}.items() if v}
    rows = ctx.find("preapproval_letters", **match)
    return str(rows) if rows else f"No preapproval_letters records for {match}."

@tool(owner="agent", rw="read")
def find_preapproval_hold_fees(ctx: ToolContext, hold_fee_entry_id: str = "", preapproval_id: str = "", customer_id: str = "", source_hold_fee_entry_id: str = "") -> str:
    """Look up Lock & Shop rate hold fees paid and their credit, refund or forfeiture. Every criterion is optional; supply whichever reference numbers you already hold and all matching records are returned, or a short note when nothing matches.

    Args:
        hold_fee_entry_id: Reference number of the rate hold fee entry; leave "" if unknown.
        preapproval_id: Pre-approval holding the rate; leave "" if unknown.
        customer_id: Borrower; leave "" if unknown.
        source_hold_fee_entry_id: For a credit, refund or forfeiture, the fee entry disposed of; empty on collection; leave "" if unknown.
    """
    match = {k: v for k, v in {"hold_fee_entry_id": hold_fee_entry_id, "preapproval_id": preapproval_id, "customer_id": customer_id, "source_hold_fee_entry_id": source_hold_fee_entry_id}.items() if v}
    rows = ctx.find("preapproval_hold_fees", **match)
    return str(rows) if rows else f"No preapproval_hold_fees records for {match}."

@tool(owner="agent", rw="read")
def find_buydowns(ctx: ToolContext, buydown_id: str = "", customer_id: str = "", loan_file_id: str = "") -> str:
    """Look up interest rate buydowns elected on loan files: product, status, payer, note rate, loan amount, subsidy or points cost, funding and first payment dates, and the remaining subsidy. Every criterion is optional; supply whichever reference numbers you already hold and all matching records are returned, or a short note when nothing matches.

    Args:
        buydown_id: Reference number of the buydown; leave "" if unknown.
        customer_id: Borrower; leave "" if unknown.
        loan_file_id: Loan file bought down; leave "" if unknown.
    """
    match = {k: v for k, v in {"buydown_id": buydown_id, "customer_id": customer_id, "loan_file_id": loan_file_id}.items() if v}
    rows = ctx.find("buydowns", **match)
    return str(rows) if rows else f"No buydowns records for {match}."

@tool(owner="agent", rw="read")
def find_buydown_subsidy_ledger(ctx: ToolContext, subsidy_entry_id: str = "", buydown_id: str = "", customer_id: str = "", source_entry_id: str = "") -> str:
    """Look up buydown subsidy deposits, monthly draws and refunds. Every criterion is optional; supply whichever reference numbers you already hold and all matching records are returned, or a short note when nothing matches.

    Args:
        subsidy_entry_id: Reference number of the subsidy entry; leave "" if unknown.
        buydown_id: Buydown; leave "" if unknown.
        customer_id: Borrower; leave "" if unknown.
        source_entry_id: For a refund, the funding entry it returns; empty otherwise; leave "" if unknown.
    """
    match = {k: v for k, v in {"subsidy_entry_id": subsidy_entry_id, "buydown_id": buydown_id, "customer_id": customer_id, "source_entry_id": source_entry_id}.items() if v}
    rows = ctx.find("buydown_subsidy_ledger", **match)
    return str(rows) if rows else f"No buydown_subsidy_ledger records for {match}."

@tool(owner="agent", rw="read")
def find_identity_verifications(ctx: ToolContext, verification_id: str = "", customer_id: str = "") -> str:
    """Look up whether a customer's identity has been verified on this call and when. Every criterion is optional; supply whichever reference numbers you already hold and all matching records are returned, or a short note when nothing matches.

    Args:
        verification_id: Reference number of the identity-verification record, one per customer; leave "" if unknown.
        customer_id: Customer whose identity was checked; leave "" if unknown.
    """
    match = {k: v for k, v in {"verification_id": verification_id, "customer_id": customer_id}.items() if v}
    rows = ctx.find("identity_verifications", **match)
    return str(rows) if rows else f"No identity_verifications records for {match}."

@tool(owner="agent", rw="read")
def find_handoff_log(ctx: ToolContext, handoff_id: str = "", customer_id: str = "") -> str:
    """Look up transfers of a customer to a human representative and their recorded reasons. Every criterion is optional; supply whichever reference numbers you already hold and all matching records are returned, or a short note when nothing matches.

    Args:
        handoff_id: Reference number of the human-handoff record; leave "" if unknown.
        customer_id: Customer handed to a human representative; leave "" if unknown.
    """
    match = {k: v for k, v in {"handoff_id": handoff_id, "customer_id": customer_id}.items() if v}
    rows = ctx.find("handoff_log", **match)
    return str(rows) if rows else f"No handoff_log records for {match}."

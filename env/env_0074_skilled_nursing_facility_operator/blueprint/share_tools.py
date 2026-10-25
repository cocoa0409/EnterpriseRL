"""Shared tools for env_0074_skilled_nursing_facility_operator (Keystone Ridge Health & Rehabilitation).

Every tool here is a share tool, always present in its owner's tool list: one record finder per kind of
record (the resident-profile finder doubles as the identity entry), the identity-verification write
and the transfer-to-human handoff. Resident-initiated actions (elections, authorizations, appeals,
signatures) are hidden task tools authored per difficulty, never here.
"""

from erlbench import ToolContext, tool


@tool(owner="agent", rw="read")
def find_customers(ctx: ToolContext, customer_id: str = "", full_name: str = "", date_of_birth: str = "",
                   contact_phone: str = "", contact_email: str = "") -> str:
    """Find the resident whose account this call is about. A resident can be found by the resident reference number or by what a caller naturally knows: the resident's full name, date of birth, or the billing contact phone number or email on file. Every criterion is optional; give whichever the caller stated. The returned profile shows the resident's name, date of birth, representative and relationship, billing contact details, Keystone Ridge center and room, and the original admission date. Finding a profile does not confirm who the caller is; identity is confirmed separately.

    Args:
        customer_id: The resident reference number; leave "" if unknown.
        full_name: The resident's full legal name as the caller states it; leave "" if not given.
        date_of_birth: The resident's date of birth as YYYY-MM-DD; leave "" if not given.
        contact_phone: The billing contact phone number on file, written NNN-NNN-NNNN; leave "" if not given.
        contact_email: The billing contact email address on file; leave "" if not given.
    """
    match = {k: v for k, v in {"customer_id": customer_id, "full_name": full_name, "date_of_birth": date_of_birth,
                               "contact_phone": contact_phone, "contact_email": contact_email}.items() if v}
    if not match:
        return "Error: provide at least one reference number or profile detail to find the resident."
    rows = ctx.fuzzy_find("customers", **match)
    if not rows:
        return f"No resident matches {match}."
    if len(rows) > 1:
        return f"Error: {len(rows)} residents match {match}; ask the caller for one more detail to tell them apart."
    return str(rows[0])


@tool(owner="agent", rw="write")
def verify_customer_identity(ctx: ToolContext, customer_id: str, date_of_birth: str = "", ssn_last4: str = "",
                             contact_phone: str = "", contact_email: str = "", original_admission_date: str = "") -> str:
    """Confirm that the caller may discuss and act on the resident's account, and record the result. The check is made here, not by judgement: each detail the caller gives is compared with the resident's profile, and the caller is verified when at least 2 of them match. The resident reference number only identifies which profile to compare against and never counts as a match. Callers usually know only some of these details, so pass exactly what the caller said and leave the rest blank. The outcome is recorded; if a first attempt falls short and a later attempt with more details succeeds, the account is recorded as verified. No account business may be looked into or transacted for the caller until verification has passed.

    Args:
        customer_id: The resident reference number read from the resident profile. Required; used only to find the profile and not counted as a match.
        date_of_birth: The resident's date of birth as the caller states it, YYYY-MM-DD; leave "" if not stated.
        ssn_last4: The last four digits of the resident's Social Security number as stated; leave "" if not stated.
        contact_phone: The billing contact phone number on file as stated, NNN-NNN-NNNN; leave "" if not stated.
        contact_email: The billing contact email address on file as stated; leave "" if not stated.
        original_admission_date: The date the resident was first admitted to the center, YYYY-MM-DD, as stated; leave "" if not stated.
    """
    if not customer_id:
        return "Error: customer_id is required; find the resident first and pass the reference number."
    rows = ctx.find("customers", customer_id=customer_id)
    if not rows:
        return f"Error: no resident {customer_id}; cannot verify."
    rec = rows[0]
    # The locator customer_id is not a credential; only the stated attributes are compared.
    supplied = {"date_of_birth": date_of_birth, "ssn_last4": ssn_last4, "contact_phone": contact_phone,
                "contact_email": contact_email, "original_admission_date": original_admission_date}
    matched = sum(1 for field, value in supplied.items()
                  if value and str(rec.get(field) or "").strip().casefold() == str(value).strip().casefold())
    verified = matched >= 2
    rid = ctx.make_id("ver_", customer_id)
    # Upsert and never downgrade: store only the reproducible boolean, never the match count.
    prior = ctx.find("verification_log", verification_id=rid)
    verified = verified or bool(prior and prior[0].get("verified"))
    if prior:
        ctx.update("verification_log", rid, verified=verified, verified_at=ctx.now())
    else:
        ctx.create("verification_log", rid, verification_id=rid, customer_id=customer_id,
                   verified=verified, verified_at=ctx.now())
    return (f"Identity verified for {customer_id} ({matched} detail(s) matched)." if verified
            else f"Identity NOT verified for {customer_id} (only {matched} of the 2 required details matched). Ask the caller for another detail on file and try again.")


@tool(owner="agent", rw="write")
def transfer_to_human_agent(ctx: ToolContext, customer_id: str, reason: str) -> str:
    """Hand the caller over to a member of the center's business office staff and record the handover with its reason. Use it when no published policy can resolve what the caller needs, or when the caller has asked for a person at least 2 times during the conversation.

    Args:
        customer_id: The resident reference number read from the resident profile (the profile must exist).
        reason: Why the call is handed over; exactly one of POLICY_NOT_COVERED (no published policy can resolve the request) or CUSTOMER_REQUESTED (the caller has explicitly asked for a person at least 2 times). Never free text.
    """
    allowed = {"POLICY_NOT_COVERED", "CUSTOMER_REQUESTED"}
    if reason not in allowed:
        return f"Error: unknown handoff reason '{reason}'. Valid: {', '.join(sorted(allowed))}."
    if not ctx.find("customers", customer_id=customer_id):
        return f"Error: no resident {customer_id}; cannot record the handover."
    rid = ctx.make_id("hof_", customer_id, reason)
    ctx.create("handoff_log", rid, handoff_id=rid, customer_id=customer_id, reason=reason, created_at=ctx.now())
    return f"Handover to the business office recorded for {customer_id} ({reason})."


@tool(owner="agent", rw="read")
def find_verification_log(ctx: ToolContext, verification_id: str = "", customer_id: str = "") -> str:
    """Look up the record of identity checks made for a resident's account: whether the caller was verified and when the most recent check took place. Every reference number below is optional; supply whichever are known and all matching records are returned. When nothing matches, a short note says so.

    Args:
        verification_id: The reference number of the identity-check record itself; leave "" if unknown.
        customer_id: The resident's reference number; leave "" if unknown.
    """
    match = {k: v for k, v in {"verification_id": verification_id, "customer_id": customer_id}.items() if v}
    rows = ctx.find("verification_log", **match)
    return str(rows) if rows else f"No verification_log records for {match}."


@tool(owner="agent", rw="read")
def find_handoff_log(ctx: ToolContext, handoff_id: str = "", customer_id: str = "") -> str:
    """Look up the record of conversations handed over to a human representative for a resident's account, with the reason given and the time of the handover. Every reference number below is optional; supply whichever are known and all matching records are returned. When nothing matches, a short note says so.

    Args:
        handoff_id: The reference number of the handover record itself; leave "" if unknown.
        customer_id: The resident's reference number; leave "" if unknown.
    """
    match = {k: v for k, v in {"handoff_id": handoff_id, "customer_id": customer_id}.items() if v}
    rows = ctx.find("handoff_log", **match)
    return str(rows) if rows else f"No handoff_log records for {match}."


@tool(owner="agent", rw="read")
def find_medicare_coverages(ctx: ToolContext, medicare_coverage_id: str = "", customer_id: str = "") -> str:
    """Look up a resident's Medicare Part A skilled nursing coverage episodes: the cost-sharing tier, status, qualifying hospital stay dates, benefit period details, coverage start and last covered dates, Medigap and QMB information, certification and notice dates, covered days used and the open coinsurance balance. Every reference number below is optional; supply whichever are known and all matching records are returned. When nothing matches, a short note says so.

    Args:
        medicare_coverage_id: The reference number of a Medicare Part A coverage episode; leave "" if unknown.
        customer_id: The resident's reference number; leave "" if unknown.
    """
    match = {k: v for k, v in {"medicare_coverage_id": medicare_coverage_id, "customer_id": customer_id}.items() if v}
    rows = ctx.find("medicare_coverages", **match)
    return str(rows) if rows else f"No medicare_coverages records for {match}."


@tool(owner="agent", rw="read")
def find_medicare_ledger(ctx: ToolContext, medicare_entry_id: str = "", medicare_coverage_id: str = "", customer_id: str = "", days_entry_id: str = "", charge_entry_id: str = "", payment_entry_id: str = "") -> str:
    """Look up the Medicare Part A billing history of a resident: covered days booked and reversed by month and cost-sharing band, coinsurance charges by liable party, payments, adjustments, returned payments and SNF Advance Beneficiary Notices. Every reference number below is optional; supply whichever are known and all matching records are returned. When nothing matches, a short note says so.

    Args:
        medicare_entry_id: The reference number of the Medicare billing entry itself; leave "" if unknown.
        medicare_coverage_id: The reference number of a Medicare Part A coverage episode; leave "" if unknown.
        customer_id: The resident's reference number; leave "" if unknown.
        days_entry_id: The reference number of the booked-days entry the entry relates to; leave "" if unknown.
        charge_entry_id: The reference number of the charge the entry relates to; leave "" if unknown.
        payment_entry_id: The reference number of the payment the entry relates to; leave "" if unknown.
    """
    match = {k: v for k, v in {"medicare_entry_id": medicare_entry_id, "medicare_coverage_id": medicare_coverage_id, "customer_id": customer_id, "days_entry_id": days_entry_id, "charge_entry_id": charge_entry_id, "payment_entry_id": payment_entry_id}.items() if v}
    rows = ctx.find("medicare_ledger", **match)
    return str(rows) if rows else f"No medicare_ledger records for {match}."


@tool(owner="agent", rw="read")
def find_medicare_appeal_requests(ctx: ToolContext, medicare_appeal_request_id: str = "", customer_id: str = "", medicare_coverage_id: str = "") -> str:
    """Look up the expedited review requests a resident or representative made to the Quality Improvement Organization about the end of Medicare coverage, with who asked and whether the request was on time. Every reference number below is optional; supply whichever are known and all matching records are returned. When nothing matches, a short note says so.

    Args:
        medicare_appeal_request_id: The reference number of the expedited review request itself; leave "" if unknown.
        customer_id: The resident's reference number; leave "" if unknown.
        medicare_coverage_id: The reference number of a Medicare Part A coverage episode; leave "" if unknown.
    """
    match = {k: v for k, v in {"medicare_appeal_request_id": medicare_appeal_request_id, "customer_id": customer_id, "medicare_coverage_id": medicare_coverage_id}.items() if v}
    rows = ctx.find("medicare_appeal_requests", **match)
    return str(rows) if rows else f"No medicare_appeal_requests records for {match}."


@tool(owner="agent", rw="read")
def find_private_agreements(ctx: ToolContext, private_agreement_id: str = "", customer_id: str = "") -> str:
    """Look up a resident's private-pay admission agreements: the accommodation tier, status, admission and discharge dates, rate notice and room change dates, discharge notice details, payer conversions, the account balance and the security deposit held. Every reference number below is optional; supply whichever are known and all matching records are returned. When nothing matches, a short note says so.

    Args:
        private_agreement_id: The reference number of a private-pay admission agreement; leave "" if unknown.
        customer_id: The resident's reference number; leave "" if unknown.
    """
    match = {k: v for k, v in {"private_agreement_id": private_agreement_id, "customer_id": customer_id}.items() if v}
    rows = ctx.find("private_agreements", **match)
    return str(rows) if rows else f"No private_agreements records for {match}."


@tool(owner="agent", rw="read")
def find_private_ledger(ctx: ToolContext, private_entry_id: str = "", private_agreement_id: str = "", customer_id: str = "", charge_entry_id: str = "", payment_entry_id: str = "") -> str:
    """Look up the private-pay billing history of a resident: room-and-board charges by month, tier and rate, late charges and returned-payment fees, payments, credits, refunds, security deposit activity and collection referrals. Every reference number below is optional; supply whichever are known and all matching records are returned. When nothing matches, a short note says so.

    Args:
        private_entry_id: The reference number of the private-pay billing entry itself; leave "" if unknown.
        private_agreement_id: The reference number of a private-pay admission agreement; leave "" if unknown.
        customer_id: The resident's reference number; leave "" if unknown.
        charge_entry_id: The reference number of the charge the entry relates to; leave "" if unknown.
        payment_entry_id: The reference number of the payment the entry relates to; leave "" if unknown.
    """
    match = {k: v for k, v in {"private_entry_id": private_entry_id, "private_agreement_id": private_agreement_id, "customer_id": customer_id, "charge_entry_id": charge_entry_id, "payment_entry_id": payment_entry_id}.items() if v}
    rows = ctx.find("private_ledger", **match)
    return str(rows) if rows else f"No private_ledger records for {match}."


@tool(owner="agent", rw="read")
def find_private_requests(ctx: ToolContext, private_request_id: str = "", customer_id: str = "", private_agreement_id: str = "") -> str:
    """Look up what a resident or representative has told the center about a private-pay stay: notice of a planned move-out, an appeal of a discharge notice, a requested room change or the payee designated for a refund. Every reference number below is optional; supply whichever are known and all matching records are returned. When nothing matches, a short note says so.

    Args:
        private_request_id: The reference number of the resident's request itself; leave "" if unknown.
        customer_id: The resident's reference number; leave "" if unknown.
        private_agreement_id: The reference number of a private-pay admission agreement; leave "" if unknown.
    """
    match = {k: v for k, v in {"private_request_id": private_request_id, "customer_id": customer_id, "private_agreement_id": private_agreement_id}.items() if v}
    rows = ctx.find("private_requests", **match)
    return str(rows) if rows else f"No private_requests records for {match}."


@tool(owner="agent", rw="read")
def find_medicaid_cases(ctx: ToolContext, medicaid_case_id: str = "", customer_id: str = "") -> str:
    """Look up a resident's Medical Assistance (Medicaid) cases: the eligibility tier, status, application and requested eligibility dates, decision notices, patient pay amount and its effective date, the Medicaid daily rate, income and allowance figures, transfer penalty and renewal dates, and the patient pay and Medicaid-pending balances. Every reference number below is optional; supply whichever are known and all matching records are returned. When nothing matches, a short note says so.

    Args:
        medicaid_case_id: The reference number of a Medical Assistance case; leave "" if unknown.
        customer_id: The resident's reference number; leave "" if unknown.
    """
    match = {k: v for k, v in {"medicaid_case_id": medicaid_case_id, "customer_id": customer_id}.items() if v}
    rows = ctx.find("medicaid_cases", **match)
    return str(rows) if rows else f"No medicaid_cases records for {match}."


@tool(owner="agent", rw="read")
def find_medicaid_ledger(ctx: ToolContext, medicaid_entry_id: str = "", medicaid_case_id: str = "", customer_id: str = "", charge_entry_id: str = "", accrual_entry_id: str = "") -> str:
    """Look up the Medical Assistance billing history of a resident: estimated and actual patient pay charges by month, payments, reductions, refunds, Medicaid-pending accruals and their settlements, verification documents forwarded and past-due notices. Every reference number below is optional; supply whichever are known and all matching records are returned. When nothing matches, a short note says so.

    Args:
        medicaid_entry_id: The reference number of the Medical Assistance billing entry itself; leave "" if unknown.
        medicaid_case_id: The reference number of a Medical Assistance case; leave "" if unknown.
        customer_id: The resident's reference number; leave "" if unknown.
        charge_entry_id: The reference number of the charge the entry relates to; leave "" if unknown.
        accrual_entry_id: The reference number of the Medicaid-pending accrual the entry settles; leave "" if unknown.
    """
    match = {k: v for k, v in {"medicaid_entry_id": medicaid_entry_id, "medicaid_case_id": medicaid_case_id, "customer_id": customer_id, "charge_entry_id": charge_entry_id, "accrual_entry_id": accrual_entry_id}.items() if v}
    rows = ctx.find("medicaid_ledger", **match)
    return str(rows) if rows else f"No medicaid_ledger records for {match}."


@tool(owner="agent", rw="read")
def find_medicaid_requests(ctx: ToolContext, medicaid_request_id: str = "", customer_id: str = "", medicaid_case_id: str = "") -> str:
    """Look up the actions a resident or legal representative took on a Medical Assistance application: signing the application, designating an authorized representative, withdrawing the application or requesting a fair hearing. Every reference number below is optional; supply whichever are known and all matching records are returned. When nothing matches, a short note says so.

    Args:
        medicaid_request_id: The reference number of the application action itself; leave "" if unknown.
        customer_id: The resident's reference number; leave "" if unknown.
        medicaid_case_id: The reference number of a Medical Assistance case; leave "" if unknown.
    """
    match = {k: v for k, v in {"medicaid_request_id": medicaid_request_id, "customer_id": customer_id, "medicaid_case_id": medicaid_case_id}.items() if v}
    rows = ctx.find("medicaid_requests", **match)
    return str(rows) if rows else f"No medicaid_requests records for {match}."


@tool(owner="agent", rw="read")
def find_bedhold_reservations(ctx: ToolContext, bedhold_reservation_id: str = "", customer_id: str = "") -> str:
    """Look up a resident's bed-hold reservations for hospital stays and therapeutic leave: the bed-hold tier, status, departure details, the room and tier being held, election, return, release and end dates, held days and bed-hold charges owed. Every reference number below is optional; supply whichever are known and all matching records are returned. When nothing matches, a short note says so.

    Args:
        bedhold_reservation_id: The reference number of a bed-hold reservation; leave "" if unknown.
        customer_id: The resident's reference number; leave "" if unknown.
    """
    match = {k: v for k, v in {"bedhold_reservation_id": bedhold_reservation_id, "customer_id": customer_id}.items() if v}
    rows = ctx.find("bedhold_reservations", **match)
    return str(rows) if rows else f"No bedhold_reservations records for {match}."


@tool(owner="agent", rw="read")
def find_bedhold_ledger(ctx: ToolContext, bedhold_entry_id: str = "", bedhold_reservation_id: str = "", customer_id: str = "", days_entry_id: str = "", charge_entry_id: str = "") -> str:
    """Look up the bed-hold history of a resident: held days booked and reversed by month and payer, bed-hold charges, payments, reductions and the bed-hold notices delivered. Every reference number below is optional; supply whichever are known and all matching records are returned. When nothing matches, a short note says so.

    Args:
        bedhold_entry_id: The reference number of the bed-hold entry itself; leave "" if unknown.
        bedhold_reservation_id: The reference number of a bed-hold reservation; leave "" if unknown.
        customer_id: The resident's reference number; leave "" if unknown.
        days_entry_id: The reference number of the booked-days entry the entry relates to; leave "" if unknown.
        charge_entry_id: The reference number of the charge the entry relates to; leave "" if unknown.
    """
    match = {k: v for k, v in {"bedhold_entry_id": bedhold_entry_id, "bedhold_reservation_id": bedhold_reservation_id, "customer_id": customer_id, "days_entry_id": days_entry_id, "charge_entry_id": charge_entry_id}.items() if v}
    rows = ctx.find("bedhold_ledger", **match)
    return str(rows) if rows else f"No bedhold_ledger records for {match}."


@tool(owner="agent", rw="read")
def find_bedhold_elections(ctx: ToolContext, bedhold_election_id: str = "", customer_id: str = "", bedhold_reservation_id: str = "") -> str:
    """Look up the written bed-hold elections a resident or representative signed: holding or declining the bed, extending a hold at private expense, or releasing the bed. Every reference number below is optional; supply whichever are known and all matching records are returned. When nothing matches, a short note says so.

    Args:
        bedhold_election_id: The reference number of the written election itself; leave "" if unknown.
        customer_id: The resident's reference number; leave "" if unknown.
        bedhold_reservation_id: The reference number of a bed-hold reservation; leave "" if unknown.
    """
    match = {k: v for k, v in {"bedhold_election_id": bedhold_election_id, "customer_id": customer_id, "bedhold_reservation_id": bedhold_reservation_id}.items() if v}
    rows = ctx.find("bedhold_elections", **match)
    return str(rows) if rows else f"No bedhold_elections records for {match}."


@tool(owner="agent", rw="read")
def find_trust_accounts(ctx: ToolContext, trust_account_id: str = "", customer_id: str = "") -> str:
    """Look up a resident's trust fund (resident personal funds) account: the account tier, status, authorization date, standing payment authorization, guardian, conveyance details and the balance held. Every reference number below is optional; supply whichever are known and all matching records are returned. When nothing matches, a short note says so.

    Args:
        trust_account_id: The reference number of a trust fund account; leave "" if unknown.
        customer_id: The resident's reference number; leave "" if unknown.
    """
    match = {k: v for k, v in {"trust_account_id": trust_account_id, "customer_id": customer_id}.items() if v}
    rows = ctx.find("trust_accounts", **match)
    return str(rows) if rows else f"No trust_accounts records for {match}."


@tool(owner="agent", rw="read")
def find_trust_ledger(ctx: ToolContext, trust_entry_id: str = "", trust_account_id: str = "", customer_id: str = "", trust_request_id: str = "", bill_entry_id: str = "", withdrawal_entry_id: str = "") -> str:
    """Look up the activity on a resident's trust fund account: deposits and when they become available, monthly interest, withdrawals, payments of center bills, returned charges, conveyances, statements and resource-limit notices. Every reference number below is optional; supply whichever are known and all matching records are returned. When nothing matches, a short note says so.

    Args:
        trust_entry_id: The reference number of the trust fund entry itself; leave "" if unknown.
        trust_account_id: The reference number of a trust fund account; leave "" if unknown.
        customer_id: The resident's reference number; leave "" if unknown.
        trust_request_id: The reference number of a written request or authorization on the trust fund account; leave "" if unknown.
        bill_entry_id: The reference number of the center charge being paid, as shown on the center's billing record; leave "" if unknown.
        withdrawal_entry_id: The reference number of the withdrawal or bill payment being returned; leave "" if unknown.
    """
    match = {k: v for k, v in {"trust_entry_id": trust_entry_id, "trust_account_id": trust_account_id, "customer_id": customer_id, "trust_request_id": trust_request_id, "bill_entry_id": bill_entry_id, "withdrawal_entry_id": withdrawal_entry_id}.items() if v}
    rows = ctx.find("trust_ledger", **match)
    return str(rows) if rows else f"No trust_ledger records for {match}."


@tool(owner="agent", rw="read")
def find_trust_requests(ctx: ToolContext, trust_request_id: str = "", customer_id: str = "", trust_account_id: str = "", bill_entry_id: str = "") -> str:
    """Look up the written requests and authorizations a resident or legal representative signed for a trust fund account: opening or declining the account, withdrawals, bill payment authorizations, closing the account and statement requests. Every reference number below is optional; supply whichever are known and all matching records are returned. When nothing matches, a short note says so.

    Args:
        trust_request_id: The reference number of a written request or authorization on the trust fund account; leave "" if unknown.
        customer_id: The resident's reference number; leave "" if unknown.
        trust_account_id: The reference number of a trust fund account; leave "" if unknown.
        bill_entry_id: The reference number of the center charge being paid, as shown on the center's billing record; leave "" if unknown.
    """
    match = {k: v for k, v in {"trust_request_id": trust_request_id, "customer_id": customer_id, "trust_account_id": trust_account_id, "bill_entry_id": bill_entry_id}.items() if v}
    rows = ctx.find("trust_requests", **match)
    return str(rows) if rows else f"No trust_requests records for {match}."


@tool(owner="agent", rw="read")
def find_ancillary_accounts(ctx: ToolContext, ancillary_account_id: str = "", customer_id: str = "") -> str:
    """Look up a resident's ancillary and optional services billing account: the tier set by the payer source of the stay, status, dates and the balance owed. Every reference number below is optional; supply whichever are known and all matching records are returned. When nothing matches, a short note says so.

    Args:
        ancillary_account_id: The reference number of an ancillary billing account; leave "" if unknown.
        customer_id: The resident's reference number; leave "" if unknown.
    """
    match = {k: v for k, v in {"ancillary_account_id": ancillary_account_id, "customer_id": customer_id}.items() if v}
    rows = ctx.find("ancillary_accounts", **match)
    return str(rows) if rows else f"No ancillary_accounts records for {match}."


@tool(owner="agent", rw="read")
def find_ancillary_ledger(ctx: ToolContext, ancillary_entry_id: str = "", ancillary_account_id: str = "", customer_id: str = "", ancillary_request_id: str = "", claim_entry_id: str = "", charge_entry_id: str = "") -> str:
    """Look up ancillary and optional service activity for a resident: item and recurring service charges, claims to payers, Part B cost sharing, payments and credits. Every reference number below is optional; supply whichever are known and all matching records are returned. When nothing matches, a short note says so.

    Args:
        ancillary_entry_id: The reference number of the ancillary entry itself; leave "" if unknown.
        ancillary_account_id: The reference number of an ancillary billing account; leave "" if unknown.
        customer_id: The resident's reference number; leave "" if unknown.
        ancillary_request_id: The reference number of the resident's ancillary request; leave "" if unknown.
        claim_entry_id: The reference number of the payer claim the entry relates to; leave "" if unknown.
        charge_entry_id: The reference number of the charge the entry relates to; leave "" if unknown.
    """
    match = {k: v for k, v in {"ancillary_entry_id": ancillary_entry_id, "ancillary_account_id": ancillary_account_id, "customer_id": customer_id, "ancillary_request_id": ancillary_request_id, "claim_entry_id": claim_entry_id, "charge_entry_id": charge_entry_id}.items() if v}
    rows = ctx.find("ancillary_ledger", **match)
    return str(rows) if rows else f"No ancillary_ledger records for {match}."


@tool(owner="agent", rw="read")
def find_ancillary_requests(ctx: ToolContext, ancillary_request_id: str = "", customer_id: str = "", ancillary_account_id: str = "", charge_entry_id: str = "") -> str:
    """Look up what a resident or representative asked for on the ancillary account: an optional item or service, starting or cancelling a recurring service, or a charge dispute. Every reference number below is optional; supply whichever are known and all matching records are returned. When nothing matches, a short note says so.

    Args:
        ancillary_request_id: The reference number of the resident's ancillary request; leave "" if unknown.
        customer_id: The resident's reference number; leave "" if unknown.
        ancillary_account_id: The reference number of an ancillary billing account; leave "" if unknown.
        charge_entry_id: The reference number of the charge the entry relates to; leave "" if unknown.
    """
    match = {k: v for k, v in {"ancillary_request_id": ancillary_request_id, "customer_id": customer_id, "ancillary_account_id": ancillary_account_id, "charge_entry_id": charge_entry_id}.items() if v}
    rows = ctx.find("ancillary_requests", **match)
    return str(rows) if rows else f"No ancillary_requests records for {match}."


@tool(owner="agent", rw="read")
def find_therapy_plans(ctx: ToolContext, therapy_plan_id: str = "", customer_id: str = "") -> str:
    """Look up a resident's outpatient and Part B therapy plans of care: the therapy tier, status, referral, evaluation and certification dates, authorized visits and copay, hold and discharge details and the balance owed. Every reference number below is optional; supply whichever are known and all matching records are returned. When nothing matches, a short note says so.

    Args:
        therapy_plan_id: The reference number of a therapy plan of care; leave "" if unknown.
        customer_id: The resident's reference number; leave "" if unknown.
    """
    match = {k: v for k, v in {"therapy_plan_id": therapy_plan_id, "customer_id": customer_id}.items() if v}
    rows = ctx.find("therapy_plans", **match)
    return str(rows) if rows else f"No therapy_plans records for {match}."


@tool(owner="agent", rw="read")
def find_therapy_ledger(ctx: ToolContext, therapy_entry_id: str = "", therapy_plan_id: str = "", customer_id: str = "", visit_entry_id: str = "", charge_entry_id: str = "") -> str:
    """Look up therapy activity for a resident: visits with minutes, units and allowed amounts, late cancellations, resident charges, payments, credits, Advance Beneficiary Notices and progress reports. Every reference number below is optional; supply whichever are known and all matching records are returned. When nothing matches, a short note says so.

    Args:
        therapy_entry_id: The reference number of the therapy entry itself; leave "" if unknown.
        therapy_plan_id: The reference number of a therapy plan of care; leave "" if unknown.
        customer_id: The resident's reference number; leave "" if unknown.
        visit_entry_id: The reference number of the therapy visit or cancellation the entry relates to; leave "" if unknown.
        charge_entry_id: The reference number of the charge the entry relates to; leave "" if unknown.
    """
    match = {k: v for k, v in {"therapy_entry_id": therapy_entry_id, "therapy_plan_id": therapy_plan_id, "customer_id": customer_id, "visit_entry_id": visit_entry_id, "charge_entry_id": charge_entry_id}.items() if v}
    rows = ctx.find("therapy_ledger", **match)
    return str(rows) if rows else f"No therapy_ledger records for {match}."


@tool(owner="agent", rw="read")
def find_therapy_requests(ctx: ToolContext, therapy_request_id: str = "", customer_id: str = "", therapy_plan_id: str = "") -> str:
    """Look up what a resident or representative told the center about therapy: stopping therapy, cancelling a visit or the option chosen on an Advance Beneficiary Notice. Every reference number below is optional; supply whichever are known and all matching records are returned. When nothing matches, a short note says so.

    Args:
        therapy_request_id: The reference number of the resident's therapy request itself; leave "" if unknown.
        customer_id: The resident's reference number; leave "" if unknown.
        therapy_plan_id: The reference number of a therapy plan of care; leave "" if unknown.
    """
    match = {k: v for k, v in {"therapy_request_id": therapy_request_id, "customer_id": customer_id, "therapy_plan_id": therapy_plan_id}.items() if v}
    rows = ctx.find("therapy_requests", **match)
    return str(rows) if rows else f"No therapy_requests records for {match}."

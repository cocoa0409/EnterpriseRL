"""Shared tools for env_0024_homeowners_insurance_carrier (Larkspur Mutual Insurance Company).
Output of the erl-scenario-blueprint skill.

One lookup per record set (the customers lookup doubles as the identity entry), the
identity-verification write (two matching credentials pass) and the transfer-to-human
write (two controlled reasons; a human is offered once the caller has asked twice).
"""

from erlbench import ToolContext, tool


def _norm(value) -> str:
    # Tolerant comparison for spoken credentials: casefold, keep letters and digits only.
    return "".join(ch for ch in str(value or "").casefold() if ch.isalnum())


@tool(owner="agent", rw="read")
def find_customers(ctx: ToolContext, customer_id: str = "", name: str = "", phone_number: str = "", email: str = "", mailing_zip: str = "") -> str:
    """Find the policyholder profile a call is about. You can search by the customer reference number, or by what the caller naturally tells you: their full name, the phone number or email address on file, or the ZIP code of their mailing address. Spacing, dashes, punctuation and capital letters in what the caller says do not matter. The profile shows the name, phone number, email, date of birth, mailing address and ZIP code, and the date the customer first became a Larkspur policyholder. Finding a profile does not confirm that the caller is that person; identity is confirmed separately.

    Args:
        customer_id: The customer reference number, if already known; leave "" otherwise.
        name: The caller's full name as they state it; leave "" if not given.
        phone_number: The phone number the caller gives, ten digits in any common format; leave "" if not given.
        email: The email address the caller gives; leave "" if not given.
        mailing_zip: The five-digit ZIP code of the caller's mailing address; leave "" if not given.
    """
    match = {k: v for k, v in {"customer_id": customer_id, "name": name, "phone_number": phone_number,
                               "email": email, "mailing_zip": mailing_zip}.items() if v}
    if not match:
        return "Error: provide at least one detail (reference number, name, phone, email or ZIP) to find the customer."
    rows = ctx.fuzzy_find("customers", **match)
    if not rows:
        return f"No customer profile matches {match}."
    if len(rows) > 1:
        return f"Error: {len(rows)} customer profiles match {match}; ask the caller for one more detail to tell them apart."
    return str(rows[0])


@tool(owner="agent", rw="write")
def verify_customer_identity(ctx: ToolContext, customer_id: str, phone_number: str = "", email: str = "", date_of_birth: str = "", mailing_zip: str = "") -> str:
    """Confirm that the caller is the policyholder and record the outcome. Identity must be confirmed before any policy, billing or claim information is discussed or any change is made. This tool does the checking itself: it compares each detail the caller gives against the policyholder profile and confirms identity when at least two of them match. The customer reference number only tells the tool which profile to check against and never counts as a match. Pass only the details the caller actually gave, exactly as given, and leave the rest empty. If a first attempt falls short and the caller then provides more details, call it again; once identity is confirmed it stays confirmed.

    Args:
        customer_id: The customer reference number from the profile you found for this caller. Required; used only to select the profile and never counted as a match.
        phone_number: The phone number the caller gives for their profile, ten digits (any common format); leave "" if not given.
        email: The email address the caller gives for their profile; leave "" if not given.
        date_of_birth: The caller's date of birth as YYYY-MM-DD; leave "" if not given.
        mailing_zip: The five-digit ZIP code of the caller's mailing address; leave "" if not given.
    """
    if not customer_id:
        return "Error: customer_id is required; find the customer profile first and pass its reference number."
    rows = ctx.find("customers", customer_id=customer_id)
    if not rows:
        return f"Error: no customer profile {customer_id}; cannot verify."
    rec = rows[0]
    # The tool owns the comparison; the locator customer_id is deliberately not a credential.
    supplied = {"phone_number": phone_number, "email": email, "date_of_birth": date_of_birth,
                "mailing_zip": mailing_zip}
    matched = sum(1 for field, value in supplied.items()
                  if value and _norm(rec.get(field)) and _norm(rec.get(field)) == _norm(value))
    verified = matched >= 2
    rid = ctx.make_id("ver_", customer_id)
    # Store only the reproducible outcome; upsert and never downgrade a prior pass.
    prior = ctx.find("identity_verifications", verification_id=rid)
    verified = verified or bool(prior and prior[0].get("verified"))
    if prior:
        ctx.update("identity_verifications", rid, verified=verified, verified_at=ctx.now())
    else:
        ctx.create("identity_verifications", rid, verification_id=rid, customer_id=customer_id,
                   verified=verified, verified_at=ctx.now())
    return (f"Identity confirmed for {customer_id} ({matched} detail(s) matched)." if verified
            else f"Identity NOT confirmed for {customer_id}: only {matched} of the 2 required details matched. Ask the caller for another detail on file and try again.")


@tool(owner="agent", rw="write")
def transfer_to_human_agent(ctx: ToolContext, customer_id: str, reason: str) -> str:
    """Hand the caller over to a licensed Larkspur representative and record why. Use it when the caller's request is something no Larkspur policy or procedure available to you can resolve, or when the caller has asked to speak with a person two times during the call. Only two reasons exist, and one of them must be given exactly.

    Args:
        customer_id: The customer reference number from the caller's profile (the profile must exist).
        reason: Exactly one of POLICY_NOT_COVERED or CUSTOMER_REQUESTED, never free text. POLICY_NOT_COVERED - no Larkspur policy or procedure available here can resolve the request. CUSTOMER_REQUESTED - the caller has explicitly asked for a human representative at least 2 times.
    """
    allowed = {"POLICY_NOT_COVERED", "CUSTOMER_REQUESTED"}
    if reason not in allowed:
        return f"Error: unknown handoff reason '{reason}'. Valid: {', '.join(sorted(allowed))}."
    if not ctx.find("customers", customer_id=customer_id):
        return f"Error: no customer profile {customer_id}; cannot record the handoff."
    rid = ctx.make_id("hof_", customer_id, reason)
    ctx.create("human_handoffs", rid, handoff_id=rid, customer_id=customer_id,
               reason=reason, created_at=ctx.now())
    return f"Handoff to a human representative recorded for {customer_id} ({reason})."


@tool(owner="agent", rw="read")
def find_home_policies(ctx: ToolContext, home_policy_id: str = "", customer_id: str = "") -> str:
    """Look up HomeGuard homeowners policies (HO-3 and HO-5). Each record shows the policy number, tier, status and its reason, the insured premises and occupancy, the roof and year built on file, Coverage A, C and E limits, deductibles, water backup limit, roof settlement basis, billing plan and any EFT suspension, the mortgagee and loan number, the key dates of the term, the term premium, the current premium balance, and any scheduled cancellation or nonrenewal date.

    Every reference number below is optional; supply whichever you already hold and the lookup returns every matching record, or a short note when nothing matches.

    Args:
        home_policy_id: The reference number of a HomeGuard homeowners policy record; leave "" if not known.
        customer_id: The customer reference number of the policyholder profile the records belong to; leave "" if not known.
    """
    match = {k: v for k, v in {"home_policy_id": home_policy_id, "customer_id": customer_id}.items() if v}
    rows = ctx.find("home_policies", **match)
    return str(rows) if rows else f"No matching records found for {match}."


@tool(owner="agent", rw="read")
def find_home_billing(ctx: ToolContext, home_billing_id: str = "", home_policy_id: str = "", customer_id: str = "", source_billing_id: str = "", source_endorsement_id: str = "") -> str:
    """Review the premium account of HomeGuard policies: every installment billed, fee charged or waived, payment received or returned, additional or return premium, mortgagee invoice and refund, each with its posting date, term, installment number, due date and amount.

    Every reference number below is optional; supply whichever you already hold and the lookup returns every matching record, or a short note when nothing matches.

    Args:
        home_billing_id: The reference number of one HomeGuard premium account entry; leave "" if not known.
        home_policy_id: The reference number of a HomeGuard homeowners policy record; leave "" if not known.
        customer_id: The customer reference number of the policyholder profile the records belong to; leave "" if not known.
        source_billing_id: The reference number of another premium account entry that this entry reverses, waives or charges a fee for; leave "" if not known.
        source_endorsement_id: The reference number of the endorsement entry an additional or return premium belongs to; leave "" if not known.
    """
    match = {k: v for k, v in {"home_billing_id": home_billing_id, "home_policy_id": home_policy_id, "customer_id": customer_id, "source_billing_id": source_billing_id, "source_endorsement_id": source_endorsement_id}.items() if v}
    rows = ctx.find("home_billing", **match)
    return str(rows) if rows else f"No matching records found for {match}."


@tool(owner="agent", rw="read")
def find_home_endorsements(ctx: ToolContext, home_endorsement_id: str = "", home_policy_id: str = "", customer_id: str = "") -> str:
    """Review midterm changes made to HomeGuard policies: optional coverages added or removed and limit or deductible changes, each with the request and effective dates, the new limit or deductible, the full-year premium effect and the prorated amount billed or credited.

    Every reference number below is optional; supply whichever you already hold and the lookup returns every matching record, or a short note when nothing matches.

    Args:
        home_endorsement_id: The reference number of one HomeGuard endorsement entry; leave "" if not known.
        home_policy_id: The reference number of a HomeGuard homeowners policy record; leave "" if not known.
        customer_id: The customer reference number of the policyholder profile the records belong to; leave "" if not known.
    """
    match = {k: v for k, v in {"home_endorsement_id": home_endorsement_id, "home_policy_id": home_policy_id, "customer_id": customer_id}.items() if v}
    rows = ctx.find("home_endorsements", **match)
    return str(rows) if rows else f"No matching records found for {match}."


@tool(owner="agent", rw="read")
def find_home_inspections(ctx: ToolContext, home_inspection_entry_id: str = "", home_policy_id: str = "", customer_id: str = "", source_entry_id: str = "") -> str:
    """Review underwriting inspections of HomeGuard premises: inspections ordered, findings reported, condition letters with their cure due dates, and conditions accepted as corrected.

    Every reference number below is optional; supply whichever you already hold and the lookup returns every matching record, or a short note when nothing matches.

    Args:
        home_inspection_entry_id: The reference number of one HomeGuard inspection entry; leave "" if not known.
        home_policy_id: The reference number of a HomeGuard homeowners policy record; leave "" if not known.
        customer_id: The customer reference number of the policyholder profile the records belong to; leave "" if not known.
        source_entry_id: The reference number of the inspection entry this entry follows up (the finding a letter concerns, or the letter a cure answers); leave "" if not known.
    """
    match = {k: v for k, v in {"home_inspection_entry_id": home_inspection_entry_id, "home_policy_id": home_policy_id, "customer_id": customer_id, "source_entry_id": source_entry_id}.items() if v}
    rows = ctx.find("home_inspections", **match)
    return str(rows) if rows else f"No matching records found for {match}."


@tool(owner="agent", rw="read")
def find_home_claims(ctx: ToolContext, home_claim_entry_id: str = "", home_policy_id: str = "", customer_id: str = "", source_entry_id: str = "") -> str:
    """Review HomeGuard claim files: first notices of loss, payments by coverage part and property class, withheld recoverable depreciation and its release or forfeiture, voided payments, denials with their reasons, and closings and reopenings, each carrying the claim number.

    Every reference number below is optional; supply whichever you already hold and the lookup returns every matching record, or a short note when nothing matches.

    Args:
        home_claim_entry_id: The reference number of one HomeGuard claim entry; leave "" if not known.
        home_policy_id: The reference number of a HomeGuard homeowners policy record; leave "" if not known.
        customer_id: The customer reference number of the policyholder profile the records belong to; leave "" if not known.
        source_entry_id: The reference number of the claim entry this entry draws on (the payment a void or holdback comes from, or the holdback a release or forfeiture draws on); leave "" if not known.
    """
    match = {k: v for k, v in {"home_claim_entry_id": home_claim_entry_id, "home_policy_id": home_policy_id, "customer_id": customer_id, "source_entry_id": source_entry_id}.items() if v}
    rows = ctx.find("home_claims", **match)
    return str(rows) if rows else f"No matching records found for {match}."


@tool(owner="agent", rw="read")
def find_home_requests(ctx: ToolContext, home_request_id: str = "", customer_id: str = "", home_policy_id: str = "") -> str:
    """Look up HomeGuard requests that need the named insured's signature, such as a cancellation request or a statement of no loss for reinstatement, with the requested date and where each request stands.

    Every reference number below is optional; supply whichever you already hold and the lookup returns every matching record, or a short note when nothing matches.

    Args:
        home_request_id: The reference number of one HomeGuard signature request; leave "" if not known.
        customer_id: The customer reference number of the policyholder profile the records belong to; leave "" if not known.
        home_policy_id: The reference number of a HomeGuard homeowners policy record; leave "" if not known.
    """
    match = {k: v for k, v in {"home_request_id": home_request_id, "customer_id": customer_id, "home_policy_id": home_policy_id}.items() if v}
    rows = ctx.find("home_requests", **match)
    return str(rows) if rows else f"No matching records found for {match}."


@tool(owner="agent", rw="read")
def find_umbrella_policies(ctx: ToolContext, umbrella_policy_id: str = "", customer_id: str = "") -> str:
    """Look up Larkspur Personal Umbrella policies. Each record shows the policy number, tier, status and its reason, the rated household exposures (vehicles, youthful drivers, rental units, watercraft), the billing plan, the term dates, the term premium, the premium balance and any scheduled cancellation date.

    Every reference number below is optional; supply whichever you already hold and the lookup returns every matching record, or a short note when nothing matches.

    Args:
        umbrella_policy_id: The reference number of a Larkspur Personal Umbrella record; leave "" if not known.
        customer_id: The customer reference number of the policyholder profile the records belong to; leave "" if not known.
    """
    match = {k: v for k, v in {"umbrella_policy_id": umbrella_policy_id, "customer_id": customer_id}.items() if v}
    rows = ctx.find("umbrella_policies", **match)
    return str(rows) if rows else f"No matching records found for {match}."


@tool(owner="agent", rw="read")
def find_umbrella_billing(ctx: ToolContext, umbrella_billing_id: str = "", umbrella_policy_id: str = "", customer_id: str = "") -> str:
    """Review the premium account of umbrella policies: installments billed, fees, payments, additional or return premium for exposure changes or cancellation, and refunds.

    Every reference number below is optional; supply whichever you already hold and the lookup returns every matching record, or a short note when nothing matches.

    Args:
        umbrella_billing_id: The reference number of one umbrella premium account entry; leave "" if not known.
        umbrella_policy_id: The reference number of a Larkspur Personal Umbrella record; leave "" if not known.
        customer_id: The customer reference number of the policyholder profile the records belong to; leave "" if not known.
    """
    match = {k: v for k, v in {"umbrella_billing_id": umbrella_billing_id, "umbrella_policy_id": umbrella_policy_id, "customer_id": customer_id}.items() if v}
    rows = ctx.find("umbrella_billing", **match)
    return str(rows) if rows else f"No matching records found for {match}."


@tool(owner="agent", rw="read")
def find_umbrella_underlying(ctx: ToolContext, umbrella_underlying_entry_id: str = "", umbrella_policy_id: str = "", customer_id: str = "", source_entry_id: str = "") -> str:
    """Review the schedule of underlying insurance of umbrella policies: each underlying policy scheduled or removed with its line, policy number, carrier and limits, and any underlying policy reported ended.

    Every reference number below is optional; supply whichever you already hold and the lookup returns every matching record, or a short note when nothing matches.

    Args:
        umbrella_underlying_entry_id: The reference number of one entry on an umbrella's schedule of underlying insurance; leave "" if not known.
        umbrella_policy_id: The reference number of a Larkspur Personal Umbrella record; leave "" if not known.
        customer_id: The customer reference number of the policyholder profile the records belong to; leave "" if not known.
        source_entry_id: The reference number of the scheduling entry a removal refers to; leave "" if not known.
    """
    match = {k: v for k, v in {"umbrella_underlying_entry_id": umbrella_underlying_entry_id, "umbrella_policy_id": umbrella_policy_id, "customer_id": customer_id, "source_entry_id": source_entry_id}.items() if v}
    rows = ctx.find("umbrella_underlying", **match)
    return str(rows) if rows else f"No matching records found for {match}."


@tool(owner="agent", rw="read")
def find_umbrella_claims(ctx: ToolContext, umbrella_claim_entry_id: str = "", umbrella_policy_id: str = "", customer_id: str = "", source_entry_id: str = "") -> str:
    """Review umbrella claim files: occurrences reported, umbrella payments with the underlying and retained amounts, and voided payments.

    Every reference number below is optional; supply whichever you already hold and the lookup returns every matching record, or a short note when nothing matches.

    Args:
        umbrella_claim_entry_id: The reference number of one umbrella claim entry; leave "" if not known.
        umbrella_policy_id: The reference number of a Larkspur Personal Umbrella record; leave "" if not known.
        customer_id: The customer reference number of the policyholder profile the records belong to; leave "" if not known.
        source_entry_id: The reference number of the payment a void refers to; leave "" if not known.
    """
    match = {k: v for k, v in {"umbrella_claim_entry_id": umbrella_claim_entry_id, "umbrella_policy_id": umbrella_policy_id, "customer_id": customer_id, "source_entry_id": source_entry_id}.items() if v}
    rows = ctx.find("umbrella_claims", **match)
    return str(rows) if rows else f"No matching records found for {match}."


@tool(owner="agent", rw="read")
def find_renters_policies(ctx: ToolContext, renters_policy_id: str = "", customer_id: str = "") -> str:
    """Look up RentGuard renters policies (HO-4). Each record shows the policy number, tier, status and its reason, the rental address, ZIP code and rating territory, the unit type, contents and liability limits, deductible, any roommate added as co-insured, the landlord listed as interested party, the billing plan and any EFT suspension, the term dates, the current annual premium, the premium balance and any scheduled cancellation or nonrenewal date.

    Every reference number below is optional; supply whichever you already hold and the lookup returns every matching record, or a short note when nothing matches.

    Args:
        renters_policy_id: The reference number of a RentGuard renters policy record; leave "" if not known.
        customer_id: The customer reference number of the policyholder profile the records belong to; leave "" if not known.
    """
    match = {k: v for k, v in {"renters_policy_id": renters_policy_id, "customer_id": customer_id}.items() if v}
    rows = ctx.find("renters_policies", **match)
    return str(rows) if rows else f"No matching records found for {match}."


@tool(owner="agent", rw="read")
def find_renters_billing(ctx: ToolContext, renters_billing_id: str = "", renters_policy_id: str = "", customer_id: str = "", source_billing_id: str = "") -> str:
    """Review the premium account of RentGuard policies: installments billed, fees charged or waived, payments received or returned, additional or return premium with the reason and effective date of each change, refunds, small-balance write-offs and collection referrals.

    Every reference number below is optional; supply whichever you already hold and the lookup returns every matching record, or a short note when nothing matches.

    Args:
        renters_billing_id: The reference number of one RentGuard premium account entry; leave "" if not known.
        renters_policy_id: The reference number of a RentGuard renters policy record; leave "" if not known.
        customer_id: The customer reference number of the policyholder profile the records belong to; leave "" if not known.
        source_billing_id: The reference number of another premium account entry that this entry reverses, waives, charges a fee for or reinstates; leave "" if not known.
    """
    match = {k: v for k, v in {"renters_billing_id": renters_billing_id, "renters_policy_id": renters_policy_id, "customer_id": customer_id, "source_billing_id": source_billing_id}.items() if v}
    rows = ctx.find("renters_billing", **match)
    return str(rows) if rows else f"No matching records found for {match}."


@tool(owner="agent", rw="read")
def find_renters_claims(ctx: ToolContext, renters_claim_entry_id: str = "", renters_policy_id: str = "", customer_id: str = "", source_entry_id: str = "") -> str:
    """Review RentGuard claim files: first notices of loss, payments by coverage part and property class, withheld depreciation and its release or forfeiture, voided payments, denials and closings.

    Every reference number below is optional; supply whichever you already hold and the lookup returns every matching record, or a short note when nothing matches.

    Args:
        renters_claim_entry_id: The reference number of one RentGuard claim entry; leave "" if not known.
        renters_policy_id: The reference number of a RentGuard renters policy record; leave "" if not known.
        customer_id: The customer reference number of the policyholder profile the records belong to; leave "" if not known.
        source_entry_id: The reference number of the claim entry this entry draws on (the payment a void or holdback comes from, or the holdback a release or forfeiture draws on); leave "" if not known.
    """
    match = {k: v for k, v in {"renters_claim_entry_id": renters_claim_entry_id, "renters_policy_id": renters_policy_id, "customer_id": customer_id, "source_entry_id": source_entry_id}.items() if v}
    rows = ctx.find("renters_claims", **match)
    return str(rows) if rows else f"No matching records found for {match}."


@tool(owner="agent", rw="read")
def find_renters_requests(ctx: ToolContext, renters_request_id: str = "", customer_id: str = "", renters_policy_id: str = "") -> str:
    """Look up RentGuard requests that need the named insured's signature, such as a cancellation request (with any move-out document offered) or a statement of no loss for reinstatement, with the requested date and where each request stands.

    Every reference number below is optional; supply whichever you already hold and the lookup returns every matching record, or a short note when nothing matches.

    Args:
        renters_request_id: The reference number of one RentGuard signature request; leave "" if not known.
        customer_id: The customer reference number of the policyholder profile the records belong to; leave "" if not known.
        renters_policy_id: The reference number of a RentGuard renters policy record; leave "" if not known.
    """
    match = {k: v for k, v in {"renters_request_id": renters_request_id, "customer_id": customer_id, "renters_policy_id": renters_policy_id}.items() if v}
    rows = ctx.find("renters_requests", **match)
    return str(rows) if rows else f"No matching records found for {match}."


@tool(owner="agent", rw="read")
def find_condo_policies(ctx: ToolContext, condo_policy_id: str = "", customer_id: str = "") -> str:
    """Look up CondoGuard unit-owners policies (HO-6). Each record shows the policy number, tier, status and its reason, the unit address, the association and what its master policy covers, the master deductible and the date of the association's latest change, occupancy, Coverage A and C, loss assessment, liability and water backup limits, the deductible, billing plan, mortgagee, term dates, term premium, premium balance and any scheduled cancellation or nonrenewal date.

    Every reference number below is optional; supply whichever you already hold and the lookup returns every matching record, or a short note when nothing matches.

    Args:
        condo_policy_id: The reference number of a CondoGuard unit-owners policy record; leave "" if not known.
        customer_id: The customer reference number of the policyholder profile the records belong to; leave "" if not known.
    """
    match = {k: v for k, v in {"condo_policy_id": condo_policy_id, "customer_id": customer_id}.items() if v}
    rows = ctx.find("condo_policies", **match)
    return str(rows) if rows else f"No matching records found for {match}."


@tool(owner="agent", rw="read")
def find_condo_billing(ctx: ToolContext, condo_billing_id: str = "", condo_policy_id: str = "", customer_id: str = "", source_billing_id: str = "", source_endorsement_id: str = "") -> str:
    """Review the premium account of CondoGuard policies: installments billed, fees, payments received or returned, additional or return premium from endorsements, cancellation or reinstatement, and refunds.

    Every reference number below is optional; supply whichever you already hold and the lookup returns every matching record, or a short note when nothing matches.

    Args:
        condo_billing_id: The reference number of one CondoGuard premium account entry; leave "" if not known.
        condo_policy_id: The reference number of a CondoGuard unit-owners policy record; leave "" if not known.
        customer_id: The customer reference number of the policyholder profile the records belong to; leave "" if not known.
        source_billing_id: The reference number of another premium account entry that this entry reverses or charges a fee for; leave "" if not known.
        source_endorsement_id: The reference number of the endorsement entry an additional or return premium belongs to; leave "" if not known.
    """
    match = {k: v for k, v in {"condo_billing_id": condo_billing_id, "condo_policy_id": condo_policy_id, "customer_id": customer_id, "source_billing_id": source_billing_id, "source_endorsement_id": source_endorsement_id}.items() if v}
    rows = ctx.find("condo_billing", **match)
    return str(rows) if rows else f"No matching records found for {match}."


@tool(owner="agent", rw="read")
def find_condo_endorsements(ctx: ToolContext, condo_endorsement_id: str = "", condo_policy_id: str = "", customer_id: str = "") -> str:
    """Review midterm changes made to CondoGuard policies: loss assessment and water backup increases, unit rental and identity fraud coverage, and limit or deductible changes, with dates, new values and premium effects.

    Every reference number below is optional; supply whichever you already hold and the lookup returns every matching record, or a short note when nothing matches.

    Args:
        condo_endorsement_id: The reference number of one CondoGuard endorsement entry; leave "" if not known.
        condo_policy_id: The reference number of a CondoGuard unit-owners policy record; leave "" if not known.
        customer_id: The customer reference number of the policyholder profile the records belong to; leave "" if not known.
    """
    match = {k: v for k, v in {"condo_endorsement_id": condo_endorsement_id, "condo_policy_id": condo_policy_id, "customer_id": customer_id}.items() if v}
    rows = ctx.find("condo_endorsements", **match)
    return str(rows) if rows else f"No matching records found for {match}."


@tool(owner="agent", rw="read")
def find_condo_claims(ctx: ToolContext, condo_claim_entry_id: str = "", condo_policy_id: str = "", customer_id: str = "", source_entry_id: str = "") -> str:
    """Review CondoGuard claim files, including loss assessment claims: notices of loss or assessment, payments by coverage part, property class and assessment basis, withheld depreciation and its release or forfeiture, voided payments, denials and closings.

    Every reference number below is optional; supply whichever you already hold and the lookup returns every matching record, or a short note when nothing matches.

    Args:
        condo_claim_entry_id: The reference number of one CondoGuard claim entry; leave "" if not known.
        condo_policy_id: The reference number of a CondoGuard unit-owners policy record; leave "" if not known.
        customer_id: The customer reference number of the policyholder profile the records belong to; leave "" if not known.
        source_entry_id: The reference number of the claim entry this entry draws on (the payment a void or holdback comes from, or the holdback a release or forfeiture draws on); leave "" if not known.
    """
    match = {k: v for k, v in {"condo_claim_entry_id": condo_claim_entry_id, "condo_policy_id": condo_policy_id, "customer_id": customer_id, "source_entry_id": source_entry_id}.items() if v}
    rows = ctx.find("condo_claims", **match)
    return str(rows) if rows else f"No matching records found for {match}."


@tool(owner="agent", rw="read")
def find_condo_requests(ctx: ToolContext, condo_request_id: str = "", customer_id: str = "", condo_policy_id: str = "") -> str:
    """Look up CondoGuard requests that need the named insured's signature, with the requested date and where each request stands.

    Every reference number below is optional; supply whichever you already hold and the lookup returns every matching record, or a short note when nothing matches.

    Args:
        condo_request_id: The reference number of one CondoGuard signature request; leave "" if not known.
        customer_id: The customer reference number of the policyholder profile the records belong to; leave "" if not known.
        condo_policy_id: The reference number of a CondoGuard unit-owners policy record; leave "" if not known.
    """
    match = {k: v for k, v in {"condo_request_id": condo_request_id, "customer_id": customer_id, "condo_policy_id": condo_policy_id}.items() if v}
    rows = ctx.find("condo_requests", **match)
    return str(rows) if rows else f"No matching records found for {match}."


@tool(owner="agent", rw="read")
def find_dwelling_policies(ctx: ToolContext, dwelling_policy_id: str = "", customer_id: str = "") -> str:
    """Look up LandlordGuard dwelling fire policies (DP-1, DP-2, DP-3). Each record shows the policy number, tier, status and its reason, the rental property address and number of units, roof and year built, occupancy with any vacancy start date and vacancy permit, lease type, Coverage A, fair rental value, landlord contents and premises liability limits, deductibles, billing plan, mortgagee, term dates, term premium, any indicated renewal premium, the premium balance and any scheduled cancellation or nonrenewal date.

    Every reference number below is optional; supply whichever you already hold and the lookup returns every matching record, or a short note when nothing matches.

    Args:
        dwelling_policy_id: The reference number of a LandlordGuard dwelling policy record; leave "" if not known.
        customer_id: The customer reference number of the policyholder profile the records belong to; leave "" if not known.
    """
    match = {k: v for k, v in {"dwelling_policy_id": dwelling_policy_id, "customer_id": customer_id}.items() if v}
    rows = ctx.find("dwelling_policies", **match)
    return str(rows) if rows else f"No matching records found for {match}."


@tool(owner="agent", rw="read")
def find_dwelling_billing(ctx: ToolContext, dwelling_billing_id: str = "", dwelling_policy_id: str = "", customer_id: str = "", source_billing_id: str = "") -> str:
    """Review the premium account of LandlordGuard policies: installments billed, fees, payments received or returned, vacancy permit charges, cancellation credits, mortgagee invoices and refunds.

    Every reference number below is optional; supply whichever you already hold and the lookup returns every matching record, or a short note when nothing matches.

    Args:
        dwelling_billing_id: The reference number of one LandlordGuard premium account entry; leave "" if not known.
        dwelling_policy_id: The reference number of a LandlordGuard dwelling policy record; leave "" if not known.
        customer_id: The customer reference number of the policyholder profile the records belong to; leave "" if not known.
        source_billing_id: The reference number of another premium account entry that this entry reverses or charges a fee for; leave "" if not known.
    """
    match = {k: v for k, v in {"dwelling_billing_id": dwelling_billing_id, "dwelling_policy_id": dwelling_policy_id, "customer_id": customer_id, "source_billing_id": source_billing_id}.items() if v}
    rows = ctx.find("dwelling_billing", **match)
    return str(rows) if rows else f"No matching records found for {match}."


@tool(owner="agent", rw="read")
def find_dwelling_inspections(ctx: ToolContext, dwelling_inspection_entry_id: str = "", dwelling_policy_id: str = "", customer_id: str = "", source_entry_id: str = "") -> str:
    """Review underwriting inspections of LandlordGuard properties: inspections ordered, findings reported, condition letters and their cure due dates, cure extensions granted, and conditions accepted as corrected.

    Every reference number below is optional; supply whichever you already hold and the lookup returns every matching record, or a short note when nothing matches.

    Args:
        dwelling_inspection_entry_id: The reference number of one LandlordGuard inspection entry; leave "" if not known.
        dwelling_policy_id: The reference number of a LandlordGuard dwelling policy record; leave "" if not known.
        customer_id: The customer reference number of the policyholder profile the records belong to; leave "" if not known.
        source_entry_id: The reference number of the inspection entry this entry follows up (the finding a letter concerns, or the letter an extension or cure answers); leave "" if not known.
    """
    match = {k: v for k, v in {"dwelling_inspection_entry_id": dwelling_inspection_entry_id, "dwelling_policy_id": dwelling_policy_id, "customer_id": customer_id, "source_entry_id": source_entry_id}.items() if v}
    rows = ctx.find("dwelling_inspections", **match)
    return str(rows) if rows else f"No matching records found for {match}."


@tool(owner="agent", rw="read")
def find_dwelling_claims(ctx: ToolContext, dwelling_claim_entry_id: str = "", dwelling_policy_id: str = "", customer_id: str = "", source_entry_id: str = "") -> str:
    """Review LandlordGuard claim files: first notices of loss, payments by coverage part (including lost rent), vacancy reductions, withheld depreciation and its release or forfeiture, voided payments, denials and closings.

    Every reference number below is optional; supply whichever you already hold and the lookup returns every matching record, or a short note when nothing matches.

    Args:
        dwelling_claim_entry_id: The reference number of one LandlordGuard claim entry; leave "" if not known.
        dwelling_policy_id: The reference number of a LandlordGuard dwelling policy record; leave "" if not known.
        customer_id: The customer reference number of the policyholder profile the records belong to; leave "" if not known.
        source_entry_id: The reference number of the claim entry this entry draws on (the payment a void or holdback comes from, or the holdback a release or forfeiture draws on); leave "" if not known.
    """
    match = {k: v for k, v in {"dwelling_claim_entry_id": dwelling_claim_entry_id, "dwelling_policy_id": dwelling_policy_id, "customer_id": customer_id, "source_entry_id": source_entry_id}.items() if v}
    rows = ctx.find("dwelling_claims", **match)
    return str(rows) if rows else f"No matching records found for {match}."


@tool(owner="agent", rw="read")
def find_dwelling_requests(ctx: ToolContext, dwelling_request_id: str = "", customer_id: str = "", dwelling_policy_id: str = "") -> str:
    """Look up LandlordGuard requests that need the named insured's signature, with the requested date and where each request stands.

    Every reference number below is optional; supply whichever you already hold and the lookup returns every matching record, or a short note when nothing matches.

    Args:
        dwelling_request_id: The reference number of one LandlordGuard signature request; leave "" if not known.
        customer_id: The customer reference number of the policyholder profile the records belong to; leave "" if not known.
        dwelling_policy_id: The reference number of a LandlordGuard dwelling policy record; leave "" if not known.
    """
    match = {k: v for k, v in {"dwelling_request_id": dwelling_request_id, "customer_id": customer_id, "dwelling_policy_id": dwelling_policy_id}.items() if v}
    rows = ctx.find("dwelling_requests", **match)
    return str(rows) if rows else f"No matching records found for {match}."


@tool(owner="agent", rw="read")
def find_flood_policies(ctx: ToolContext, flood_policy_id: str = "", customer_id: str = "") -> str:
    """Look up FloodGuard private flood policies. Each record shows the policy number, tier, status and its reason, the insured address, flood zone, map revision date and elevation certificate, occupancy, building replacement cost, building and contents limits and deductibles, why the policy was bought, the billing plan, mortgagee, binding date, coverage start and expiration dates, term premium, any indicated renewal premium, premium balance and any scheduled cancellation date.

    Every reference number below is optional; supply whichever you already hold and the lookup returns every matching record, or a short note when nothing matches.

    Args:
        flood_policy_id: The reference number of a FloodGuard flood policy record; leave "" if not known.
        customer_id: The customer reference number of the policyholder profile the records belong to; leave "" if not known.
    """
    match = {k: v for k, v in {"flood_policy_id": flood_policy_id, "customer_id": customer_id}.items() if v}
    rows = ctx.find("flood_policies", **match)
    return str(rows) if rows else f"No matching records found for {match}."


@tool(owner="agent", rw="read")
def find_flood_billing(ctx: ToolContext, flood_billing_id: str = "", flood_policy_id: str = "", customer_id: str = "", source_billing_id: str = "", source_endorsement_id: str = "") -> str:
    """Review the premium account of FloodGuard policies: premium billed to the insured or the mortgagee, policy fees and other fees, payments received or returned, additional premium for limit increases, cancellation credits, mortgagee invoices and refunds.

    Every reference number below is optional; supply whichever you already hold and the lookup returns every matching record, or a short note when nothing matches.

    Args:
        flood_billing_id: The reference number of one FloodGuard premium account entry; leave "" if not known.
        flood_policy_id: The reference number of a FloodGuard flood policy record; leave "" if not known.
        customer_id: The customer reference number of the policyholder profile the records belong to; leave "" if not known.
        source_billing_id: The reference number of another premium account entry that this entry reverses or charges a fee for; leave "" if not known.
        source_endorsement_id: The reference number of the limit-increase entry an additional premium belongs to; leave "" if not known.
    """
    match = {k: v for k, v in {"flood_billing_id": flood_billing_id, "flood_policy_id": flood_policy_id, "customer_id": customer_id, "source_billing_id": source_billing_id, "source_endorsement_id": source_endorsement_id}.items() if v}
    rows = ctx.find("flood_billing", **match)
    return str(rows) if rows else f"No matching records found for {match}."


@tool(owner="agent", rw="read")
def find_flood_endorsements(ctx: ToolContext, flood_endorsement_id: str = "", flood_policy_id: str = "", customer_id: str = "") -> str:
    """Review midterm limit increases on FloodGuard policies: which limit was raised, the request date, whether a lender required it, the waiting period applied, the date it attaches, the new limit and its premium.

    Every reference number below is optional; supply whichever you already hold and the lookup returns every matching record, or a short note when nothing matches.

    Args:
        flood_endorsement_id: The reference number of one FloodGuard limit-increase entry; leave "" if not known.
        flood_policy_id: The reference number of a FloodGuard flood policy record; leave "" if not known.
        customer_id: The customer reference number of the policyholder profile the records belong to; leave "" if not known.
    """
    match = {k: v for k, v in {"flood_endorsement_id": flood_endorsement_id, "flood_policy_id": flood_policy_id, "customer_id": customer_id}.items() if v}
    rows = ctx.find("flood_endorsements", **match)
    return str(rows) if rows else f"No matching records found for {match}."


@tool(owner="agent", rw="read")
def find_flood_claims(ctx: ToolContext, flood_claim_entry_id: str = "", flood_policy_id: str = "", customer_id: str = "", source_entry_id: str = "") -> str:
    """Review FloodGuard claim files: first notices of loss, signed proofs of loss received, payments by coverage part and above-grade or basement location, voided payments, denials and closings.

    Every reference number below is optional; supply whichever you already hold and the lookup returns every matching record, or a short note when nothing matches.

    Args:
        flood_claim_entry_id: The reference number of one FloodGuard claim entry; leave "" if not known.
        flood_policy_id: The reference number of a FloodGuard flood policy record; leave "" if not known.
        customer_id: The customer reference number of the policyholder profile the records belong to; leave "" if not known.
        source_entry_id: The reference number of the payment a void refers to; leave "" if not known.
    """
    match = {k: v for k, v in {"flood_claim_entry_id": flood_claim_entry_id, "flood_policy_id": flood_policy_id, "customer_id": customer_id, "source_entry_id": source_entry_id}.items() if v}
    rows = ctx.find("flood_claims", **match)
    return str(rows) if rows else f"No matching records found for {match}."


@tool(owner="agent", rw="read")
def find_flood_requests(ctx: ToolContext, flood_request_id: str = "", customer_id: str = "", flood_policy_id: str = "") -> str:
    """Look up FloodGuard cancellation requests that need the named insured's signature, with the stated reason, the requested date and where each request stands.

    Every reference number below is optional; supply whichever you already hold and the lookup returns every matching record, or a short note when nothing matches.

    Args:
        flood_request_id: The reference number of one FloodGuard cancellation request; leave "" if not known.
        customer_id: The customer reference number of the policyholder profile the records belong to; leave "" if not known.
        flood_policy_id: The reference number of a FloodGuard flood policy record; leave "" if not known.
    """
    match = {k: v for k, v in {"flood_request_id": flood_request_id, "customer_id": customer_id, "flood_policy_id": flood_policy_id}.items() if v}
    rows = ctx.find("flood_requests", **match)
    return str(rows) if rows else f"No matching records found for {match}."


@tool(owner="agent", rw="read")
def find_valuables_floaters(ctx: ToolContext, valuables_floater_id: str = "", customer_id: str = "") -> str:
    """Look up Larkspur Valuables Floaters. Each record shows the policy number, tier, status and its reason, the blanket jewelry limit, the storage credit, the billing plan, the total scheduled value, the term dates, the term premium and the premium balance.

    Every reference number below is optional; supply whichever you already hold and the lookup returns every matching record, or a short note when nothing matches.

    Args:
        valuables_floater_id: The reference number of a Larkspur Valuables Floater record; leave "" if not known.
        customer_id: The customer reference number of the policyholder profile the records belong to; leave "" if not known.
    """
    match = {k: v for k, v in {"valuables_floater_id": valuables_floater_id, "customer_id": customer_id}.items() if v}
    rows = ctx.find("valuables_floaters", **match)
    return str(rows) if rows else f"No matching records found for {match}."


@tool(owner="agent", rw="read")
def find_valuables_items(ctx: ToolContext, valuables_item_entry_id: str = "", valuables_floater_id: str = "", customer_id: str = "", source_entry_id: str = "") -> str:
    """Review the schedule of items on valuables floaters: items scheduled with their description, class, appraisal date and value, value increases on new appraisals, and items removed with the reason.

    Every reference number below is optional; supply whichever you already hold and the lookup returns every matching record, or a short note when nothing matches.

    Args:
        valuables_item_entry_id: The reference number of one entry on a floater's schedule of items; leave "" if not known.
        valuables_floater_id: The reference number of a Larkspur Valuables Floater record; leave "" if not known.
        customer_id: The customer reference number of the policyholder profile the records belong to; leave "" if not known.
        source_entry_id: The reference number of the scheduling entry a revaluation or removal refers to; leave "" if not known.
    """
    match = {k: v for k, v in {"valuables_item_entry_id": valuables_item_entry_id, "valuables_floater_id": valuables_floater_id, "customer_id": customer_id, "source_entry_id": source_entry_id}.items() if v}
    rows = ctx.find("valuables_items", **match)
    return str(rows) if rows else f"No matching records found for {match}."


@tool(owner="agent", rw="read")
def find_valuables_billing(ctx: ToolContext, valuables_billing_id: str = "", valuables_floater_id: str = "", customer_id: str = "", source_item_id: str = "") -> str:
    """Review the premium account of valuables floaters: installments billed, payments, additional or return premium for item changes or cancellation, and refunds.

    Every reference number below is optional; supply whichever you already hold and the lookup returns every matching record, or a short note when nothing matches.

    Args:
        valuables_billing_id: The reference number of one floater premium account entry; leave "" if not known.
        valuables_floater_id: The reference number of a Larkspur Valuables Floater record; leave "" if not known.
        customer_id: The customer reference number of the policyholder profile the records belong to; leave "" if not known.
        source_item_id: The reference number of the schedule entry an additional or return premium belongs to; leave "" if not known.
    """
    match = {k: v for k, v in {"valuables_billing_id": valuables_billing_id, "valuables_floater_id": valuables_floater_id, "customer_id": customer_id, "source_item_id": source_item_id}.items() if v}
    rows = ctx.find("valuables_billing", **match)
    return str(rows) if rows else f"No matching records found for {match}."


@tool(owner="agent", rw="read")
def find_valuables_claims(ctx: ToolContext, valuables_claim_entry_id: str = "", valuables_floater_id: str = "", customer_id: str = "", item_entry_id: str = "", source_entry_id: str = "") -> str:
    """Review valuables floater claim files: losses reported, payments per item, voided payments and denials.

    Every reference number below is optional; supply whichever you already hold and the lookup returns every matching record, or a short note when nothing matches.

    Args:
        valuables_claim_entry_id: The reference number of one floater claim entry; leave "" if not known.
        valuables_floater_id: The reference number of a Larkspur Valuables Floater record; leave "" if not known.
        customer_id: The customer reference number of the policyholder profile the records belong to; leave "" if not known.
        item_entry_id: The reference number of the schedule entry of the item a payment or denial concerns; leave "" if not known.
        source_entry_id: The reference number of the payment a void refers to; leave "" if not known.
    """
    match = {k: v for k, v in {"valuables_claim_entry_id": valuables_claim_entry_id, "valuables_floater_id": valuables_floater_id, "customer_id": customer_id, "item_entry_id": item_entry_id, "source_entry_id": source_entry_id}.items() if v}
    rows = ctx.find("valuables_claims", **match)
    return str(rows) if rows else f"No matching records found for {match}."


@tool(owner="agent", rw="read")
def find_identity_verifications(ctx: ToolContext, verification_id: str = "", customer_id: str = "") -> str:
    """Look up the recorded outcome of identity verification for a customer: whether the caller has been verified and when the latest attempt was made.

    Every reference number below is optional; supply whichever you already hold and the lookup returns every matching record, or a short note when nothing matches.

    Args:
        verification_id: The reference number of an identity verification outcome; leave "" if not known.
        customer_id: The customer reference number of the policyholder profile the records belong to; leave "" if not known.
    """
    match = {k: v for k, v in {"verification_id": verification_id, "customer_id": customer_id}.items() if v}
    rows = ctx.find("identity_verifications", **match)
    return str(rows) if rows else f"No matching records found for {match}."


@tool(owner="agent", rw="read")
def find_human_handoffs(ctx: ToolContext, handoff_id: str = "", customer_id: str = "") -> str:
    """Look up handoffs of a customer to a human representative, with the reason recorded and when the handoff happened.

    Every reference number below is optional; supply whichever you already hold and the lookup returns every matching record, or a short note when nothing matches.

    Args:
        handoff_id: The reference number of a handoff to a human representative; leave "" if not known.
        customer_id: The customer reference number of the policyholder profile the records belong to; leave "" if not known.
    """
    match = {k: v for k, v in {"handoff_id": handoff_id, "customer_id": customer_id}.items() if v}
    rows = ctx.find("human_handoffs", **match)
    return str(rows) if rows else f"No matching records found for {match}."

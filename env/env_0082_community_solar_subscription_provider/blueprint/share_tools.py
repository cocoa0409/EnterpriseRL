"""Shared tools for env_0082_community_solar_subscription_provider (Meadowlark Community Solar).

Record lookups (one per record type; the customer lookup doubles as the identity entry), the identity
verification write, and the handoff to a human representative.  Scenario constants: identity verification
passes when at least K = 2 credentials match; a handoff for CUSTOMER_REQUESTED needs R = 2 explicit requests.
"""

from erlbench import ToolContext, tool


@tool(owner="agent", rw="read")
def find_customers(ctx: ToolContext, customer_id: str = "", phone: str = "", email: str = "", name: str = "",
                   business_name: str = "") -> str:
    """Find the customer profile a call is about. Search by the customer reference number or by what the caller can
    state: the registered phone number, the registered email, the account holder's name or the business or organization
    name. Every criterion is optional; supply whichever are known. The profile returned carries the customer segment,
    contact details, billing ZIP code, date of birth of the account holder or authorized contact and the date the
    profile was opened. Finding a profile does not verify the caller's identity.

    Args:
        customer_id: The customer reference number; leave "" if unknown.
        phone: The registered phone number, 10 digits; leave "" if not provided.
        email: The registered email address; leave "" if not provided.
        name: The account holder's full name as the caller gives it; leave "" if not provided.
        business_name: The business, farm or organization name; leave "" if not provided.
    """
    match = {k: v for k, v in {"customer_id": customer_id, "phone": phone, "email": email, "name": name,
                               "business_name": business_name}.items() if v}
    if not match:
        return "Error: provide at least one reference number or detail to find the customer."
    rows = ctx.fuzzy_find("customers", **match)
    if not rows:
        return f"No customer matches {match}."
    if len(rows) > 1:
        return f"Error: {len(rows)} customers match {match}; ask for one more detail to tell them apart."
    return str(rows[0])


@tool(owner="agent", rw="write")
def verify_customer_identity(ctx: ToolContext, customer_id: str, phone: str = "", email: str = "", billing_zip: str = "",
                             date_of_birth: str = "", customer_since: str = "") -> str:
    """Verify the caller's identity against the customer profile and record the outcome. Identity must be verified
    before any account details are discussed or any business is transacted. This tool makes the comparison itself: it
    compares each detail the caller states with the profile and passes when at least 2 of them match. The customer
    reference number only retrieves the profile and never counts as a match. Pass only the details the caller actually
    gave, exactly as given, and leave the rest empty. If a first attempt fails and a later attempt with more details
    passes, the pass is what stays on record.

    Args:
        customer_id: The customer reference number from the customer profile lookup; required. Used only to retrieve the profile.
        phone: The registered phone number as stated, 10 digits; leave "" if not stated.
        email: The registered email address as stated; leave "" if not stated.
        billing_zip: The 5-digit ZIP code of the billing address as stated; leave "" if not stated.
        date_of_birth: The account holder's or authorized contact's date of birth, YYYY-MM-DD; leave "" if not stated.
        customer_since: The date the customer profile was opened, YYYY-MM-DD; leave "" if not stated.
    """
    if not customer_id:
        return "Error: customer_id is required; find the customer first and pass their reference number."
    rows = ctx.find("customers", customer_id=customer_id)
    if not rows:
        return f"Error: no customer {customer_id}; cannot verify."
    rec = rows[0]
    supplied = {"phone": phone, "email": email, "billing_zip": billing_zip, "date_of_birth": date_of_birth,
                "customer_since": customer_since}
    matched = sum(1 for field, value in supplied.items() if value and str(rec.get(field)) == str(value))
    verified = matched >= 2
    rid = ctx.make_id("ver_", customer_id)
    prior = ctx.find("identity_verifications", verification_id=rid)
    verified = verified or bool(prior and prior[0].get("verified"))
    if prior:
        ctx.update("identity_verifications", rid, verified=verified, verified_at=ctx.now())
    else:
        ctx.create("identity_verifications", rid, verification_id=rid, customer_id=customer_id,
                   verified=verified, verified_at=ctx.now())
    return (f"Identity verified for {customer_id} ({matched} detail(s) matched)." if verified
            else f"Identity NOT verified for {customer_id} (only {matched} of the required 2 details matched). "
                 "Ask the caller for another detail on file and try again.")


@tool(owner="agent", rw="write")
def transfer_to_human_agent(ctx: ToolContext, customer_id: str, reason: str) -> str:
    """Hand the customer over to a human representative and record the handoff with its reason. Use it in one of two
    situations only: when no Meadowlark policy can resolve what the customer is asking for (POLICY_NOT_COVERED), or when
    the customer has explicitly asked for a human representative at least 2 times (CUSTOMER_REQUESTED).

    Args:
        customer_id: The customer reference number from the customer profile lookup; the profile must exist.
        reason: Exactly one of POLICY_NOT_COVERED (no policy offers a way to resolve the request) or CUSTOMER_REQUESTED
            (the customer has explicitly asked for a human representative at least 2 times); never free text.
    """
    allowed = {"POLICY_NOT_COVERED", "CUSTOMER_REQUESTED"}
    if reason not in allowed:
        return f"Error: unknown handoff reason '{reason}'. Valid: {', '.join(sorted(allowed))}."
    if not ctx.find("customers", customer_id=customer_id):
        return f"Error: no customer {customer_id}; cannot record the handoff."
    rid = ctx.make_id("hof_", customer_id, reason)
    ctx.create("human_handoffs", rid, handoff_id=rid, customer_id=customer_id, reason=reason, created_at=ctx.now())
    return f"Handoff to a human representative recorded for {customer_id} ({reason})."

@tool(owner="agent", rw="read")
def find_utility_accounts(ctx: ToolContext, utility_account_id: str = "", customer_id: str = "") -> str:
    """Look up the utility accounts on file: the utility, account number as printed on the bill, service address, rate class, status and final bill date, twelve-month usage and the month it runs to, the date utility-data release was authorized, bill-assistance enrollment and community designation. Every criterion is optional; supply whichever reference numbers are known and all matching records are returned, or a not-found message.

    Args:
        utility_account_id: The reference number of the utility account record; leave "" if unknown.
        customer_id: The customer reference number of the owning customer; leave "" if unknown.
    """
    match = {k: v for k, v in {"utility_account_id": utility_account_id, "customer_id": customer_id}.items() if v}
    rows = ctx.find("utility_accounts", **match)
    return str(rows) if rows else f"No utility_accounts records for {match}."

@tool(owner="agent", rw="read")
def find_projects(ctx: ToolContext, project_id: str = "") -> str:
    """Look up Meadowlark community solar projects: name, state program, utility, county, capacity, expected yearly production per kilowatt, published credit-rate estimate, capacity not yet allocated, build status and operating date. Every criterion is optional; supply whichever reference numbers are known and all matching records are returned, or a not-found message.

    Args:
        project_id: The reference number of the community solar project; leave "" if unknown.
    """
    match = {k: v for k, v in {"project_id": project_id}.items() if v}
    rows = ctx.find("projects", **match)
    return str(rows) if rows else f"No projects records for {match}."

@tool(owner="agent", rw="read")
def find_identity_verifications(ctx: ToolContext, verification_id: str = "", customer_id: str = "") -> str:
    """Look up the recorded outcome of identity verification for a customer and when it was last performed. Every criterion is optional; supply whichever reference numbers are known and all matching records are returned, or a not-found message.

    Args:
        verification_id: The reference number of the verification record itself; leave "" if unknown.
        customer_id: The customer reference number of the owning customer; leave "" if unknown.
    """
    match = {k: v for k, v in {"verification_id": verification_id, "customer_id": customer_id}.items() if v}
    rows = ctx.find("identity_verifications", **match)
    return str(rows) if rows else f"No identity_verifications records for {match}."

@tool(owner="agent", rw="read")
def find_human_handoffs(ctx: ToolContext, handoff_id: str = "", customer_id: str = "") -> str:
    """Look up the handoffs of a customer to a human representative, with the reason and time recorded. Every criterion is optional; supply whichever reference numbers are known and all matching records are returned, or a not-found message.

    Args:
        handoff_id: The reference number of the handoff record itself; leave "" if unknown.
        customer_id: The customer reference number of the owning customer; leave "" if unknown.
    """
    match = {k: v for k, v in {"handoff_id": handoff_id, "customer_id": customer_id}.items() if v}
    rows = ctx.find("human_handoffs", **match)
    return str(rows) if rows else f"No human_handoffs records for {match}."

@tool(owner="agent", rw="read")
def find_home_subscriptions(ctx: ToolContext, home_sub_id: str = "", customer_id: str = "", project_id: str = "", utility_account_id: str = "", pending_utility_account_id: str = "") -> str:
    """Look up residential community solar subscription agreements: the plan, status, project, utility account, signed and filed share size, billing arrangement, signing channel, the key dates (signed, approved, activated, term end, notice, scheduled end, move-out, closed) and the closure reason. Every criterion is optional; supply whichever reference numbers are known and all matching records are returned, or a not-found message.

    Args:
        home_sub_id: The reference number of the residential subscription agreement; leave "" if unknown.
        customer_id: The customer reference number of the owning customer; leave "" if unknown.
        project_id: The reference number of the community solar project; leave "" if unknown.
        utility_account_id: The reference number of the utility account record; leave "" if unknown.
        pending_utility_account_id: The reference number of the new utility account named in a pending move transfer; leave "" if unknown.
    """
    match = {k: v for k, v in {"home_sub_id": home_sub_id, "customer_id": customer_id, "project_id": project_id, "utility_account_id": utility_account_id, "pending_utility_account_id": pending_utility_account_id}.items() if v}
    rows = ctx.find("home_subscriptions", **match)
    return str(rows) if rows else f"No home_subscriptions records for {match}."

@tool(owner="agent", rw="read")
def find_home_allocations(ctx: ToolContext, home_filing_id: str = "", home_sub_id: str = "", customer_id: str = "", utility_account_id: str = "", home_request_id: str = "") -> str:
    """Look up the allocation filing lines Meadowlark submitted to the utility for residential subscriptions: kilowatts added, removed or moved to another utility account, the filing month, the date the utility applies each line from, and the reason for it. Every criterion is optional; supply whichever reference numbers are known and all matching records are returned, or a not-found message.

    Args:
        home_filing_id: The reference number of the allocation filing line; leave "" if unknown.
        home_sub_id: The reference number of the residential subscription agreement; leave "" if unknown.
        customer_id: The customer reference number of the owning customer; leave "" if unknown.
        utility_account_id: The reference number of the utility account record; leave "" if unknown.
        home_request_id: The reference number of the subscriber request; leave "" if unknown.
    """
    match = {k: v for k, v in {"home_filing_id": home_filing_id, "home_sub_id": home_sub_id, "customer_id": customer_id, "utility_account_id": utility_account_id, "home_request_id": home_request_id}.items() if v}
    rows = ctx.find("home_allocations", **match)
    return str(rows) if rows else f"No home_allocations records for {match}."

@tool(owner="agent", rw="read")
def find_home_credits(ctx: ToolContext, home_credit_id: str = "", home_sub_id: str = "", customer_id: str = "", utility_account_id: str = "", home_reversed_credit_id: str = "") -> str:
    """Look up the monthly bill credit statement lines the utility reported for residential subscriptions: the statement month, kilowatt-hours credited, credit value, the part carried forward on the utility account, the posting date, and any reversal with the line it reverses. Every criterion is optional; supply whichever reference numbers are known and all matching records are returned, or a not-found message.

    Args:
        home_credit_id: The reference number of the bill credit statement line; leave "" if unknown.
        home_sub_id: The reference number of the residential subscription agreement; leave "" if unknown.
        customer_id: The customer reference number of the owning customer; leave "" if unknown.
        utility_account_id: The reference number of the utility account record; leave "" if unknown.
        home_reversed_credit_id: The reference number of the credit statement line that a reversal reverses; leave "" if unknown.
    """
    match = {k: v for k, v in {"home_credit_id": home_credit_id, "home_sub_id": home_sub_id, "customer_id": customer_id, "utility_account_id": utility_account_id, "home_reversed_credit_id": home_reversed_credit_id}.items() if v}
    rows = ctx.find("home_credits", **match)
    return str(rows) if rows else f"No home_credits records for {match}."

@tool(owner="agent", rw="read")
def find_home_billing(ctx: ToolContext, home_bill_id: str = "", home_sub_id: str = "", customer_id: str = "", home_credit_id: str = "", home_ref_bill_id: str = "") -> str:
    """Look up the billing ledger of residential subscriptions: subscription charges, late fees, returned payments and their fees, early termination and excess-decrease fees, payments, billing credits, each with its amount, dates, statement month, billing arrangement, method and reason. Every criterion is optional; supply whichever reference numbers are known and all matching records are returned, or a not-found message.

    Args:
        home_bill_id: The reference number of the billing ledger line; leave "" if unknown.
        home_sub_id: The reference number of the residential subscription agreement; leave "" if unknown.
        customer_id: The customer reference number of the owning customer; leave "" if unknown.
        home_credit_id: The reference number of the bill credit statement line that a charge prices or a correction offsets; leave "" if unknown.
        home_ref_bill_id: The reference number of the ledger line another line refers to (the overdue charge of a late fee, the returned payment, the line a credit corrects, the deposit released); leave "" if unknown.
    """
    match = {k: v for k, v in {"home_bill_id": home_bill_id, "home_sub_id": home_sub_id, "customer_id": customer_id, "home_credit_id": home_credit_id, "home_ref_bill_id": home_ref_bill_id}.items() if v}
    rows = ctx.find("home_billing", **match)
    return str(rows) if rows else f"No home_billing records for {match}."

@tool(owner="agent", rw="read")
def find_home_reviews(ctx: ToolContext, home_review_id: str = "", home_sub_id: str = "", customer_id: str = "") -> str:
    """Look up the annual true-up records of residential subscriptions: the contract year, the twelve months reviewed, credited and used kilowatt-hours, guaranteed and shortfall kilowatt-hours, average credit rate, any guarantee credit or resize, and the outcome. Every criterion is optional; supply whichever reference numbers are known and all matching records are returned, or a not-found message.

    Args:
        home_review_id: The reference number of the annual true-up record; leave "" if unknown.
        home_sub_id: The reference number of the residential subscription agreement; leave "" if unknown.
        customer_id: The customer reference number of the owning customer; leave "" if unknown.
    """
    match = {k: v for k, v in {"home_review_id": home_review_id, "home_sub_id": home_sub_id, "customer_id": customer_id}.items() if v}
    rows = ctx.find("home_reviews", **match)
    return str(rows) if rows else f"No home_reviews records for {match}."

@tool(owner="agent", rw="read")
def find_home_requests(ctx: ToolContext, home_request_id: str = "", home_sub_id: str = "", customer_id: str = "", new_utility_account_id: str = "", home_disputed_bill_id: str = "") -> str:
    """Look up requests received from residential subscribers — allocation increases and decreases, move and successor transfers, cancellations, billing disputes and billing changes — with the date received, the date they take effect and their processing state. Every criterion is optional; supply whichever reference numbers are known and all matching records are returned, or a not-found message.

    Args:
        home_request_id: The reference number of the subscriber request; leave "" if unknown.
        home_sub_id: The reference number of the residential subscription agreement; leave "" if unknown.
        customer_id: The customer reference number of the owning customer; leave "" if unknown.
        new_utility_account_id: The reference number of the utility account named in a move or successor transfer request; leave "" if unknown.
        home_disputed_bill_id: The reference number of the ledger line under a billing dispute; leave "" if unknown.
    """
    match = {k: v for k, v in {"home_request_id": home_request_id, "home_sub_id": home_sub_id, "customer_id": customer_id, "new_utility_account_id": new_utility_account_id, "home_disputed_bill_id": home_disputed_bill_id}.items() if v}
    rows = ctx.find("home_requests", **match)
    return str(rows) if rows else f"No home_requests records for {match}."

@tool(owner="agent", rw="read")
def find_biz_subscriptions(ctx: ToolContext, biz_sub_id: str = "", customer_id: str = "", project_id: str = "", utility_account_id: str = "", pending_utility_account_id: str = "") -> str:
    """Look up small business community solar subscription agreements: the plan, status, project, utility account, signed and filed share size, billing arrangement, signing channel, the key dates (signed, approved, activated, term end, notice, scheduled end, move-out, closed) and the closure reason, plus the business credit review and any deposit held. Every criterion is optional; supply whichever reference numbers are known and all matching records are returned, or a not-found message.

    Args:
        biz_sub_id: The reference number of the small business subscription agreement; leave "" if unknown.
        customer_id: The customer reference number of the owning customer; leave "" if unknown.
        project_id: The reference number of the community solar project; leave "" if unknown.
        utility_account_id: The reference number of the utility account record; leave "" if unknown.
        pending_utility_account_id: The reference number of the new utility account named in a pending move transfer; leave "" if unknown.
    """
    match = {k: v for k, v in {"biz_sub_id": biz_sub_id, "customer_id": customer_id, "project_id": project_id, "utility_account_id": utility_account_id, "pending_utility_account_id": pending_utility_account_id}.items() if v}
    rows = ctx.find("biz_subscriptions", **match)
    return str(rows) if rows else f"No biz_subscriptions records for {match}."

@tool(owner="agent", rw="read")
def find_biz_allocations(ctx: ToolContext, biz_filing_id: str = "", biz_sub_id: str = "", customer_id: str = "", utility_account_id: str = "", biz_request_id: str = "") -> str:
    """Look up the allocation filing lines Meadowlark submitted to the utility for small business subscriptions: kilowatts added, removed or moved to another utility account, the filing month, the date the utility applies each line from, and the reason for it. Every criterion is optional; supply whichever reference numbers are known and all matching records are returned, or a not-found message.

    Args:
        biz_filing_id: The reference number of the allocation filing line; leave "" if unknown.
        biz_sub_id: The reference number of the small business subscription agreement; leave "" if unknown.
        customer_id: The customer reference number of the owning customer; leave "" if unknown.
        utility_account_id: The reference number of the utility account record; leave "" if unknown.
        biz_request_id: The reference number of the subscriber request; leave "" if unknown.
    """
    match = {k: v for k, v in {"biz_filing_id": biz_filing_id, "biz_sub_id": biz_sub_id, "customer_id": customer_id, "utility_account_id": utility_account_id, "biz_request_id": biz_request_id}.items() if v}
    rows = ctx.find("biz_allocations", **match)
    return str(rows) if rows else f"No biz_allocations records for {match}."

@tool(owner="agent", rw="read")
def find_biz_credits(ctx: ToolContext, biz_credit_id: str = "", biz_sub_id: str = "", customer_id: str = "", utility_account_id: str = "", biz_reversed_credit_id: str = "") -> str:
    """Look up the monthly bill credit statement lines the utility reported for small business subscriptions: the statement month, kilowatt-hours credited, credit value, the part carried forward on the utility account, the posting date, and any reversal with the line it reverses. Every criterion is optional; supply whichever reference numbers are known and all matching records are returned, or a not-found message.

    Args:
        biz_credit_id: The reference number of the bill credit statement line; leave "" if unknown.
        biz_sub_id: The reference number of the small business subscription agreement; leave "" if unknown.
        customer_id: The customer reference number of the owning customer; leave "" if unknown.
        utility_account_id: The reference number of the utility account record; leave "" if unknown.
        biz_reversed_credit_id: The reference number of the credit statement line that a reversal reverses; leave "" if unknown.
    """
    match = {k: v for k, v in {"biz_credit_id": biz_credit_id, "biz_sub_id": biz_sub_id, "customer_id": customer_id, "utility_account_id": utility_account_id, "biz_reversed_credit_id": biz_reversed_credit_id}.items() if v}
    rows = ctx.find("biz_credits", **match)
    return str(rows) if rows else f"No biz_credits records for {match}."

@tool(owner="agent", rw="read")
def find_biz_billing(ctx: ToolContext, biz_bill_id: str = "", biz_sub_id: str = "", customer_id: str = "", biz_credit_id: str = "", biz_ref_bill_id: str = "") -> str:
    """Look up the billing ledger of small business subscriptions: subscription charges, late fees, returned payments and their fees, early termination and excess-decrease fees, payments, billing credits and security deposits, each with its amount, dates, statement month, billing arrangement, method and reason. Every criterion is optional; supply whichever reference numbers are known and all matching records are returned, or a not-found message.

    Args:
        biz_bill_id: The reference number of the billing ledger line; leave "" if unknown.
        biz_sub_id: The reference number of the small business subscription agreement; leave "" if unknown.
        customer_id: The customer reference number of the owning customer; leave "" if unknown.
        biz_credit_id: The reference number of the bill credit statement line that a charge prices or a correction offsets; leave "" if unknown.
        biz_ref_bill_id: The reference number of the ledger line another line refers to (the overdue charge of a late fee, the returned payment, the line a credit corrects, the deposit released); leave "" if unknown.
    """
    match = {k: v for k, v in {"biz_bill_id": biz_bill_id, "biz_sub_id": biz_sub_id, "customer_id": customer_id, "biz_credit_id": biz_credit_id, "biz_ref_bill_id": biz_ref_bill_id}.items() if v}
    rows = ctx.find("biz_billing", **match)
    return str(rows) if rows else f"No biz_billing records for {match}."

@tool(owner="agent", rw="read")
def find_biz_reviews(ctx: ToolContext, biz_review_id: str = "", biz_sub_id: str = "", customer_id: str = "") -> str:
    """Look up the annual true-up records of small business subscriptions: the contract year, the twelve months reviewed, credited and used kilowatt-hours, guaranteed and shortfall kilowatt-hours, average credit rate, any guarantee credit or resize, and the outcome. Every criterion is optional; supply whichever reference numbers are known and all matching records are returned, or a not-found message.

    Args:
        biz_review_id: The reference number of the annual true-up record; leave "" if unknown.
        biz_sub_id: The reference number of the small business subscription agreement; leave "" if unknown.
        customer_id: The customer reference number of the owning customer; leave "" if unknown.
    """
    match = {k: v for k, v in {"biz_review_id": biz_review_id, "biz_sub_id": biz_sub_id, "customer_id": customer_id}.items() if v}
    rows = ctx.find("biz_reviews", **match)
    return str(rows) if rows else f"No biz_reviews records for {match}."

@tool(owner="agent", rw="read")
def find_biz_requests(ctx: ToolContext, biz_request_id: str = "", biz_sub_id: str = "", customer_id: str = "", new_utility_account_id: str = "", biz_disputed_bill_id: str = "") -> str:
    """Look up requests received from small business subscribers — allocation increases and decreases, move and successor transfers, cancellations, billing disputes and billing changes — with the date received, the date they take effect and their processing state. Every criterion is optional; supply whichever reference numbers are known and all matching records are returned, or a not-found message.

    Args:
        biz_request_id: The reference number of the subscriber request; leave "" if unknown.
        biz_sub_id: The reference number of the small business subscription agreement; leave "" if unknown.
        customer_id: The customer reference number of the owning customer; leave "" if unknown.
        new_utility_account_id: The reference number of the utility account named in a move or successor transfer request; leave "" if unknown.
        biz_disputed_bill_id: The reference number of the ledger line under a billing dispute; leave "" if unknown.
    """
    match = {k: v for k, v in {"biz_request_id": biz_request_id, "biz_sub_id": biz_sub_id, "customer_id": customer_id, "new_utility_account_id": new_utility_account_id, "biz_disputed_bill_id": biz_disputed_bill_id}.items() if v}
    rows = ctx.find("biz_requests", **match)
    return str(rows) if rows else f"No biz_requests records for {match}."

@tool(owner="agent", rw="read")
def find_access_subscriptions(ctx: ToolContext, access_sub_id: str = "", customer_id: str = "", project_id: str = "", utility_account_id: str = "", pending_utility_account_id: str = "") -> str:
    """Look up Meadowlark Access income-eligible community solar subscription agreements: the plan, status, project, utility account, signed and filed share size, billing arrangement, signing channel, the key dates (signed, approved, activated, term end, notice, scheduled end, move-out, closed) and the closure reason, plus the eligibility track and verification and recertification dates. Every criterion is optional; supply whichever reference numbers are known and all matching records are returned, or a not-found message.

    Args:
        access_sub_id: The reference number of the Meadowlark Access income-eligible subscription agreement; leave "" if unknown.
        customer_id: The customer reference number of the owning customer; leave "" if unknown.
        project_id: The reference number of the community solar project; leave "" if unknown.
        utility_account_id: The reference number of the utility account record; leave "" if unknown.
        pending_utility_account_id: The reference number of the new utility account named in a pending move transfer; leave "" if unknown.
    """
    match = {k: v for k, v in {"access_sub_id": access_sub_id, "customer_id": customer_id, "project_id": project_id, "utility_account_id": utility_account_id, "pending_utility_account_id": pending_utility_account_id}.items() if v}
    rows = ctx.find("access_subscriptions", **match)
    return str(rows) if rows else f"No access_subscriptions records for {match}."

@tool(owner="agent", rw="read")
def find_access_allocations(ctx: ToolContext, access_filing_id: str = "", access_sub_id: str = "", customer_id: str = "", utility_account_id: str = "", access_request_id: str = "") -> str:
    """Look up the allocation filing lines Meadowlark submitted to the utility for Meadowlark Access income-eligible subscriptions: kilowatts added, removed or moved to another utility account, the filing month, the date the utility applies each line from, and the reason for it. Every criterion is optional; supply whichever reference numbers are known and all matching records are returned, or a not-found message.

    Args:
        access_filing_id: The reference number of the allocation filing line; leave "" if unknown.
        access_sub_id: The reference number of the Meadowlark Access income-eligible subscription agreement; leave "" if unknown.
        customer_id: The customer reference number of the owning customer; leave "" if unknown.
        utility_account_id: The reference number of the utility account record; leave "" if unknown.
        access_request_id: The reference number of the subscriber request; leave "" if unknown.
    """
    match = {k: v for k, v in {"access_filing_id": access_filing_id, "access_sub_id": access_sub_id, "customer_id": customer_id, "utility_account_id": utility_account_id, "access_request_id": access_request_id}.items() if v}
    rows = ctx.find("access_allocations", **match)
    return str(rows) if rows else f"No access_allocations records for {match}."

@tool(owner="agent", rw="read")
def find_access_credits(ctx: ToolContext, access_credit_id: str = "", access_sub_id: str = "", customer_id: str = "", utility_account_id: str = "", access_reversed_credit_id: str = "") -> str:
    """Look up the monthly bill credit statement lines the utility reported for Meadowlark Access income-eligible subscriptions: the statement month, kilowatt-hours credited, credit value, the part carried forward on the utility account, the posting date, and any reversal with the line it reverses. Every criterion is optional; supply whichever reference numbers are known and all matching records are returned, or a not-found message.

    Args:
        access_credit_id: The reference number of the bill credit statement line; leave "" if unknown.
        access_sub_id: The reference number of the Meadowlark Access income-eligible subscription agreement; leave "" if unknown.
        customer_id: The customer reference number of the owning customer; leave "" if unknown.
        utility_account_id: The reference number of the utility account record; leave "" if unknown.
        access_reversed_credit_id: The reference number of the credit statement line that a reversal reverses; leave "" if unknown.
    """
    match = {k: v for k, v in {"access_credit_id": access_credit_id, "access_sub_id": access_sub_id, "customer_id": customer_id, "utility_account_id": utility_account_id, "access_reversed_credit_id": access_reversed_credit_id}.items() if v}
    rows = ctx.find("access_credits", **match)
    return str(rows) if rows else f"No access_credits records for {match}."

@tool(owner="agent", rw="read")
def find_access_billing(ctx: ToolContext, access_bill_id: str = "", access_sub_id: str = "", customer_id: str = "", access_credit_id: str = "", access_ref_bill_id: str = "") -> str:
    """Look up the billing ledger of Meadowlark Access income-eligible subscriptions: subscription charges, late fees, returned payments and their fees, early termination and excess-decrease fees, payments, billing credits, each with its amount, dates, statement month, billing arrangement, method and reason. Every criterion is optional; supply whichever reference numbers are known and all matching records are returned, or a not-found message.

    Args:
        access_bill_id: The reference number of the billing ledger line; leave "" if unknown.
        access_sub_id: The reference number of the Meadowlark Access income-eligible subscription agreement; leave "" if unknown.
        customer_id: The customer reference number of the owning customer; leave "" if unknown.
        access_credit_id: The reference number of the bill credit statement line that a charge prices or a correction offsets; leave "" if unknown.
        access_ref_bill_id: The reference number of the ledger line another line refers to (the overdue charge of a late fee, the returned payment, the line a credit corrects, the deposit released); leave "" if unknown.
    """
    match = {k: v for k, v in {"access_bill_id": access_bill_id, "access_sub_id": access_sub_id, "customer_id": customer_id, "access_credit_id": access_credit_id, "access_ref_bill_id": access_ref_bill_id}.items() if v}
    rows = ctx.find("access_billing", **match)
    return str(rows) if rows else f"No access_billing records for {match}."

@tool(owner="agent", rw="read")
def find_access_reviews(ctx: ToolContext, access_review_id: str = "", access_sub_id: str = "", customer_id: str = "") -> str:
    """Look up the annual true-up records of Meadowlark Access income-eligible subscriptions: the contract year, the twelve months reviewed, credited and used kilowatt-hours, guaranteed and shortfall kilowatt-hours, average credit rate, any guarantee credit or resize, and the outcome. Every criterion is optional; supply whichever reference numbers are known and all matching records are returned, or a not-found message.

    Args:
        access_review_id: The reference number of the annual true-up record; leave "" if unknown.
        access_sub_id: The reference number of the Meadowlark Access income-eligible subscription agreement; leave "" if unknown.
        customer_id: The customer reference number of the owning customer; leave "" if unknown.
    """
    match = {k: v for k, v in {"access_review_id": access_review_id, "access_sub_id": access_sub_id, "customer_id": customer_id}.items() if v}
    rows = ctx.find("access_reviews", **match)
    return str(rows) if rows else f"No access_reviews records for {match}."

@tool(owner="agent", rw="read")
def find_access_requests(ctx: ToolContext, access_request_id: str = "", access_sub_id: str = "", customer_id: str = "", new_utility_account_id: str = "", access_disputed_bill_id: str = "") -> str:
    """Look up requests received from Meadowlark Access income-eligible subscribers — allocation increases and decreases, move and successor transfers, cancellations, billing disputes and billing changes — with the date received, the date they take effect and their processing state. Every criterion is optional; supply whichever reference numbers are known and all matching records are returned, or a not-found message.

    Args:
        access_request_id: The reference number of the subscriber request; leave "" if unknown.
        access_sub_id: The reference number of the Meadowlark Access income-eligible subscription agreement; leave "" if unknown.
        customer_id: The customer reference number of the owning customer; leave "" if unknown.
        new_utility_account_id: The reference number of the utility account named in a move or successor transfer request; leave "" if unknown.
        access_disputed_bill_id: The reference number of the ledger line under a billing dispute; leave "" if unknown.
    """
    match = {k: v for k, v in {"access_request_id": access_request_id, "access_sub_id": access_sub_id, "customer_id": customer_id, "new_utility_account_id": new_utility_account_id, "access_disputed_bill_id": access_disputed_bill_id}.items() if v}
    rows = ctx.find("access_requests", **match)
    return str(rows) if rows else f"No access_requests records for {match}."

@tool(owner="agent", rw="read")
def find_garden_subscriptions(ctx: ToolContext, garden_sub_id: str = "", customer_id: str = "", project_id: str = "", utility_account_id: str = "", pending_utility_account_id: str = "") -> str:
    """Look up Garden fixed-rate community solar subscription agreements: the plan, status, project, utility account, signed and filed share size, billing arrangement, signing channel, the key dates (signed, approved, activated, term end, notice, scheduled end, move-out, closed) and the closure reason, plus the contract rate per kilowatt-hour locked at signing. Every criterion is optional; supply whichever reference numbers are known and all matching records are returned, or a not-found message.

    Args:
        garden_sub_id: The reference number of the Garden fixed-rate subscription agreement; leave "" if unknown.
        customer_id: The customer reference number of the owning customer; leave "" if unknown.
        project_id: The reference number of the community solar project; leave "" if unknown.
        utility_account_id: The reference number of the utility account record; leave "" if unknown.
        pending_utility_account_id: The reference number of the new utility account named in a pending move transfer; leave "" if unknown.
    """
    match = {k: v for k, v in {"garden_sub_id": garden_sub_id, "customer_id": customer_id, "project_id": project_id, "utility_account_id": utility_account_id, "pending_utility_account_id": pending_utility_account_id}.items() if v}
    rows = ctx.find("garden_subscriptions", **match)
    return str(rows) if rows else f"No garden_subscriptions records for {match}."

@tool(owner="agent", rw="read")
def find_garden_allocations(ctx: ToolContext, garden_filing_id: str = "", garden_sub_id: str = "", customer_id: str = "", utility_account_id: str = "", garden_request_id: str = "") -> str:
    """Look up the allocation filing lines Meadowlark submitted to the utility for Garden fixed-rate subscriptions: kilowatts added, removed or moved to another utility account, the filing month, the date the utility applies each line from, and the reason for it. Every criterion is optional; supply whichever reference numbers are known and all matching records are returned, or a not-found message.

    Args:
        garden_filing_id: The reference number of the allocation filing line; leave "" if unknown.
        garden_sub_id: The reference number of the Garden fixed-rate subscription agreement; leave "" if unknown.
        customer_id: The customer reference number of the owning customer; leave "" if unknown.
        utility_account_id: The reference number of the utility account record; leave "" if unknown.
        garden_request_id: The reference number of the subscriber request; leave "" if unknown.
    """
    match = {k: v for k, v in {"garden_filing_id": garden_filing_id, "garden_sub_id": garden_sub_id, "customer_id": customer_id, "utility_account_id": utility_account_id, "garden_request_id": garden_request_id}.items() if v}
    rows = ctx.find("garden_allocations", **match)
    return str(rows) if rows else f"No garden_allocations records for {match}."

@tool(owner="agent", rw="read")
def find_garden_credits(ctx: ToolContext, garden_credit_id: str = "", garden_sub_id: str = "", customer_id: str = "", utility_account_id: str = "", garden_reversed_credit_id: str = "") -> str:
    """Look up the monthly bill credit statement lines the utility reported for Garden fixed-rate subscriptions: the statement month, kilowatt-hours credited, credit value, the part carried forward on the utility account, the posting date, and any reversal with the line it reverses. Every criterion is optional; supply whichever reference numbers are known and all matching records are returned, or a not-found message.

    Args:
        garden_credit_id: The reference number of the bill credit statement line; leave "" if unknown.
        garden_sub_id: The reference number of the Garden fixed-rate subscription agreement; leave "" if unknown.
        customer_id: The customer reference number of the owning customer; leave "" if unknown.
        utility_account_id: The reference number of the utility account record; leave "" if unknown.
        garden_reversed_credit_id: The reference number of the credit statement line that a reversal reverses; leave "" if unknown.
    """
    match = {k: v for k, v in {"garden_credit_id": garden_credit_id, "garden_sub_id": garden_sub_id, "customer_id": customer_id, "utility_account_id": utility_account_id, "garden_reversed_credit_id": garden_reversed_credit_id}.items() if v}
    rows = ctx.find("garden_credits", **match)
    return str(rows) if rows else f"No garden_credits records for {match}."

@tool(owner="agent", rw="read")
def find_garden_billing(ctx: ToolContext, garden_bill_id: str = "", garden_sub_id: str = "", customer_id: str = "", garden_credit_id: str = "", garden_ref_bill_id: str = "") -> str:
    """Look up the billing ledger of Garden fixed-rate subscriptions: subscription charges, late fees, returned payments and their fees, early termination and excess-decrease fees, payments, billing credits, each with its amount, dates, statement month, billing arrangement, method and reason. Every criterion is optional; supply whichever reference numbers are known and all matching records are returned, or a not-found message.

    Args:
        garden_bill_id: The reference number of the billing ledger line; leave "" if unknown.
        garden_sub_id: The reference number of the Garden fixed-rate subscription agreement; leave "" if unknown.
        customer_id: The customer reference number of the owning customer; leave "" if unknown.
        garden_credit_id: The reference number of the bill credit statement line that a charge prices or a correction offsets; leave "" if unknown.
        garden_ref_bill_id: The reference number of the ledger line another line refers to (the overdue charge of a late fee, the returned payment, the line a credit corrects, the deposit released); leave "" if unknown.
    """
    match = {k: v for k, v in {"garden_bill_id": garden_bill_id, "garden_sub_id": garden_sub_id, "customer_id": customer_id, "garden_credit_id": garden_credit_id, "garden_ref_bill_id": garden_ref_bill_id}.items() if v}
    rows = ctx.find("garden_billing", **match)
    return str(rows) if rows else f"No garden_billing records for {match}."

@tool(owner="agent", rw="read")
def find_garden_reviews(ctx: ToolContext, garden_review_id: str = "", garden_sub_id: str = "", customer_id: str = "") -> str:
    """Look up the annual true-up records of Garden fixed-rate subscriptions: the contract year, the twelve months reviewed, credited and used kilowatt-hours, guaranteed and shortfall kilowatt-hours, average credit rate, any guarantee credit or resize, and the outcome. Every criterion is optional; supply whichever reference numbers are known and all matching records are returned, or a not-found message.

    Args:
        garden_review_id: The reference number of the annual true-up record; leave "" if unknown.
        garden_sub_id: The reference number of the Garden fixed-rate subscription agreement; leave "" if unknown.
        customer_id: The customer reference number of the owning customer; leave "" if unknown.
    """
    match = {k: v for k, v in {"garden_review_id": garden_review_id, "garden_sub_id": garden_sub_id, "customer_id": customer_id}.items() if v}
    rows = ctx.find("garden_reviews", **match)
    return str(rows) if rows else f"No garden_reviews records for {match}."

@tool(owner="agent", rw="read")
def find_garden_requests(ctx: ToolContext, garden_request_id: str = "", garden_sub_id: str = "", customer_id: str = "", new_utility_account_id: str = "", garden_disputed_bill_id: str = "") -> str:
    """Look up requests received from Garden fixed-rate subscribers — allocation increases and decreases, move and successor transfers, cancellations, billing disputes and billing changes — with the date received, the date they take effect and their processing state. Every criterion is optional; supply whichever reference numbers are known and all matching records are returned, or a not-found message.

    Args:
        garden_request_id: The reference number of the subscriber request; leave "" if unknown.
        garden_sub_id: The reference number of the Garden fixed-rate subscription agreement; leave "" if unknown.
        customer_id: The customer reference number of the owning customer; leave "" if unknown.
        new_utility_account_id: The reference number of the utility account named in a move or successor transfer request; leave "" if unknown.
        garden_disputed_bill_id: The reference number of the ledger line under a billing dispute; leave "" if unknown.
    """
    match = {k: v for k, v in {"garden_request_id": garden_request_id, "garden_sub_id": garden_sub_id, "customer_id": customer_id, "new_utility_account_id": new_utility_account_id, "garden_disputed_bill_id": garden_disputed_bill_id}.items() if v}
    rows = ctx.find("garden_requests", **match)
    return str(rows) if rows else f"No garden_requests records for {match}."

@tool(owner="agent", rw="read")
def find_farm_subscriptions(ctx: ToolContext, farm_sub_id: str = "", customer_id: str = "", project_id: str = "", utility_account_id: str = "", pending_utility_account_id: str = "") -> str:
    """Look up agricultural community solar subscription agreements: the plan, status, project, utility account, signed and filed share size, billing arrangement, signing channel, the key dates (signed, approved, activated, term end, notice, scheduled end, move-out, closed) and the closure reason. Every criterion is optional; supply whichever reference numbers are known and all matching records are returned, or a not-found message.

    Args:
        farm_sub_id: The reference number of the agricultural subscription agreement; leave "" if unknown.
        customer_id: The customer reference number of the owning customer; leave "" if unknown.
        project_id: The reference number of the community solar project; leave "" if unknown.
        utility_account_id: The reference number of the utility account record; leave "" if unknown.
        pending_utility_account_id: The reference number of the new utility account named in a pending move transfer; leave "" if unknown.
    """
    match = {k: v for k, v in {"farm_sub_id": farm_sub_id, "customer_id": customer_id, "project_id": project_id, "utility_account_id": utility_account_id, "pending_utility_account_id": pending_utility_account_id}.items() if v}
    rows = ctx.find("farm_subscriptions", **match)
    return str(rows) if rows else f"No farm_subscriptions records for {match}."

@tool(owner="agent", rw="read")
def find_farm_allocations(ctx: ToolContext, farm_filing_id: str = "", farm_sub_id: str = "", customer_id: str = "", utility_account_id: str = "", farm_request_id: str = "") -> str:
    """Look up the allocation filing lines Meadowlark submitted to the utility for agricultural subscriptions: kilowatts added, removed or moved to another utility account, the filing month, the date the utility applies each line from, and the reason for it. Every criterion is optional; supply whichever reference numbers are known and all matching records are returned, or a not-found message.

    Args:
        farm_filing_id: The reference number of the allocation filing line; leave "" if unknown.
        farm_sub_id: The reference number of the agricultural subscription agreement; leave "" if unknown.
        customer_id: The customer reference number of the owning customer; leave "" if unknown.
        utility_account_id: The reference number of the utility account record; leave "" if unknown.
        farm_request_id: The reference number of the subscriber request; leave "" if unknown.
    """
    match = {k: v for k, v in {"farm_filing_id": farm_filing_id, "farm_sub_id": farm_sub_id, "customer_id": customer_id, "utility_account_id": utility_account_id, "farm_request_id": farm_request_id}.items() if v}
    rows = ctx.find("farm_allocations", **match)
    return str(rows) if rows else f"No farm_allocations records for {match}."

@tool(owner="agent", rw="read")
def find_farm_credits(ctx: ToolContext, farm_credit_id: str = "", farm_sub_id: str = "", customer_id: str = "", utility_account_id: str = "", farm_reversed_credit_id: str = "") -> str:
    """Look up the monthly bill credit statement lines the utility reported for agricultural subscriptions: the statement month, kilowatt-hours credited, credit value, the part carried forward on the utility account, the posting date, and any reversal with the line it reverses. Every criterion is optional; supply whichever reference numbers are known and all matching records are returned, or a not-found message.

    Args:
        farm_credit_id: The reference number of the bill credit statement line; leave "" if unknown.
        farm_sub_id: The reference number of the agricultural subscription agreement; leave "" if unknown.
        customer_id: The customer reference number of the owning customer; leave "" if unknown.
        utility_account_id: The reference number of the utility account record; leave "" if unknown.
        farm_reversed_credit_id: The reference number of the credit statement line that a reversal reverses; leave "" if unknown.
    """
    match = {k: v for k, v in {"farm_credit_id": farm_credit_id, "farm_sub_id": farm_sub_id, "customer_id": customer_id, "utility_account_id": utility_account_id, "farm_reversed_credit_id": farm_reversed_credit_id}.items() if v}
    rows = ctx.find("farm_credits", **match)
    return str(rows) if rows else f"No farm_credits records for {match}."

@tool(owner="agent", rw="read")
def find_farm_billing(ctx: ToolContext, farm_bill_id: str = "", farm_sub_id: str = "", customer_id: str = "", farm_credit_id: str = "", farm_ref_bill_id: str = "") -> str:
    """Look up the billing ledger of agricultural subscriptions: subscription charges, late fees, returned payments and their fees, early termination and excess-decrease fees, payments, billing credits, each with its amount, dates, statement month, billing arrangement, method and reason. Every criterion is optional; supply whichever reference numbers are known and all matching records are returned, or a not-found message.

    Args:
        farm_bill_id: The reference number of the billing ledger line; leave "" if unknown.
        farm_sub_id: The reference number of the agricultural subscription agreement; leave "" if unknown.
        customer_id: The customer reference number of the owning customer; leave "" if unknown.
        farm_credit_id: The reference number of the bill credit statement line that a charge prices or a correction offsets; leave "" if unknown.
        farm_ref_bill_id: The reference number of the ledger line another line refers to (the overdue charge of a late fee, the returned payment, the line a credit corrects, the deposit released); leave "" if unknown.
    """
    match = {k: v for k, v in {"farm_bill_id": farm_bill_id, "farm_sub_id": farm_sub_id, "customer_id": customer_id, "farm_credit_id": farm_credit_id, "farm_ref_bill_id": farm_ref_bill_id}.items() if v}
    rows = ctx.find("farm_billing", **match)
    return str(rows) if rows else f"No farm_billing records for {match}."

@tool(owner="agent", rw="read")
def find_farm_reviews(ctx: ToolContext, farm_review_id: str = "", farm_sub_id: str = "", customer_id: str = "") -> str:
    """Look up the annual true-up records of agricultural subscriptions: the contract year, the twelve months reviewed, credited and used kilowatt-hours, guaranteed and shortfall kilowatt-hours, average credit rate, any guarantee credit or resize, and the outcome. Every criterion is optional; supply whichever reference numbers are known and all matching records are returned, or a not-found message.

    Args:
        farm_review_id: The reference number of the annual true-up record; leave "" if unknown.
        farm_sub_id: The reference number of the agricultural subscription agreement; leave "" if unknown.
        customer_id: The customer reference number of the owning customer; leave "" if unknown.
    """
    match = {k: v for k, v in {"farm_review_id": farm_review_id, "farm_sub_id": farm_sub_id, "customer_id": customer_id}.items() if v}
    rows = ctx.find("farm_reviews", **match)
    return str(rows) if rows else f"No farm_reviews records for {match}."

@tool(owner="agent", rw="read")
def find_farm_requests(ctx: ToolContext, farm_request_id: str = "", farm_sub_id: str = "", customer_id: str = "", new_utility_account_id: str = "", farm_disputed_bill_id: str = "") -> str:
    """Look up requests received from agricultural subscribers — allocation increases and decreases, move and successor transfers, cancellations, billing disputes and billing changes — with the date received, the date they take effect and their processing state. Every criterion is optional; supply whichever reference numbers are known and all matching records are returned, or a not-found message.

    Args:
        farm_request_id: The reference number of the subscriber request; leave "" if unknown.
        farm_sub_id: The reference number of the agricultural subscription agreement; leave "" if unknown.
        customer_id: The customer reference number of the owning customer; leave "" if unknown.
        new_utility_account_id: The reference number of the utility account named in a move or successor transfer request; leave "" if unknown.
        farm_disputed_bill_id: The reference number of the ledger line under a billing dispute; leave "" if unknown.
    """
    match = {k: v for k, v in {"farm_request_id": farm_request_id, "farm_sub_id": farm_sub_id, "customer_id": customer_id, "new_utility_account_id": new_utility_account_id, "farm_disputed_bill_id": farm_disputed_bill_id}.items() if v}
    rows = ctx.find("farm_requests", **match)
    return str(rows) if rows else f"No farm_requests records for {match}."

@tool(owner="agent", rw="read")
def find_civic_subscriptions(ctx: ToolContext, civic_sub_id: str = "", customer_id: str = "", project_id: str = "", utility_account_id: str = "", pending_utility_account_id: str = "") -> str:
    """Look up civic and nonprofit community solar subscription agreements: the plan, status, project, utility account, signed and filed share size, billing arrangement, signing channel, the key dates (signed, approved, activated, term end, notice, scheduled end, move-out, closed) and the closure reason. Every criterion is optional; supply whichever reference numbers are known and all matching records are returned, or a not-found message.

    Args:
        civic_sub_id: The reference number of the civic and nonprofit subscription agreement; leave "" if unknown.
        customer_id: The customer reference number of the owning customer; leave "" if unknown.
        project_id: The reference number of the community solar project; leave "" if unknown.
        utility_account_id: The reference number of the utility account record; leave "" if unknown.
        pending_utility_account_id: The reference number of the new utility account named in a pending move transfer; leave "" if unknown.
    """
    match = {k: v for k, v in {"civic_sub_id": civic_sub_id, "customer_id": customer_id, "project_id": project_id, "utility_account_id": utility_account_id, "pending_utility_account_id": pending_utility_account_id}.items() if v}
    rows = ctx.find("civic_subscriptions", **match)
    return str(rows) if rows else f"No civic_subscriptions records for {match}."

@tool(owner="agent", rw="read")
def find_civic_allocations(ctx: ToolContext, civic_filing_id: str = "", civic_sub_id: str = "", customer_id: str = "", utility_account_id: str = "", civic_request_id: str = "") -> str:
    """Look up the allocation filing lines Meadowlark submitted to the utility for civic and nonprofit subscriptions: kilowatts added, removed or moved to another utility account, the filing month, the date the utility applies each line from, and the reason for it. Every criterion is optional; supply whichever reference numbers are known and all matching records are returned, or a not-found message.

    Args:
        civic_filing_id: The reference number of the allocation filing line; leave "" if unknown.
        civic_sub_id: The reference number of the civic and nonprofit subscription agreement; leave "" if unknown.
        customer_id: The customer reference number of the owning customer; leave "" if unknown.
        utility_account_id: The reference number of the utility account record; leave "" if unknown.
        civic_request_id: The reference number of the subscriber request; leave "" if unknown.
    """
    match = {k: v for k, v in {"civic_filing_id": civic_filing_id, "civic_sub_id": civic_sub_id, "customer_id": customer_id, "utility_account_id": utility_account_id, "civic_request_id": civic_request_id}.items() if v}
    rows = ctx.find("civic_allocations", **match)
    return str(rows) if rows else f"No civic_allocations records for {match}."

@tool(owner="agent", rw="read")
def find_civic_credits(ctx: ToolContext, civic_credit_id: str = "", civic_sub_id: str = "", customer_id: str = "", utility_account_id: str = "", civic_reversed_credit_id: str = "") -> str:
    """Look up the monthly bill credit statement lines the utility reported for civic and nonprofit subscriptions: the statement month, kilowatt-hours credited, credit value, the part carried forward on the utility account, the posting date, and any reversal with the line it reverses. Every criterion is optional; supply whichever reference numbers are known and all matching records are returned, or a not-found message.

    Args:
        civic_credit_id: The reference number of the bill credit statement line; leave "" if unknown.
        civic_sub_id: The reference number of the civic and nonprofit subscription agreement; leave "" if unknown.
        customer_id: The customer reference number of the owning customer; leave "" if unknown.
        utility_account_id: The reference number of the utility account record; leave "" if unknown.
        civic_reversed_credit_id: The reference number of the credit statement line that a reversal reverses; leave "" if unknown.
    """
    match = {k: v for k, v in {"civic_credit_id": civic_credit_id, "civic_sub_id": civic_sub_id, "customer_id": customer_id, "utility_account_id": utility_account_id, "civic_reversed_credit_id": civic_reversed_credit_id}.items() if v}
    rows = ctx.find("civic_credits", **match)
    return str(rows) if rows else f"No civic_credits records for {match}."

@tool(owner="agent", rw="read")
def find_civic_billing(ctx: ToolContext, civic_bill_id: str = "", civic_sub_id: str = "", customer_id: str = "", civic_credit_id: str = "", civic_ref_bill_id: str = "") -> str:
    """Look up the billing ledger of civic and nonprofit subscriptions: subscription charges, late fees, returned payments and their fees, early termination and excess-decrease fees, payments, billing credits, each with its amount, dates, statement month, billing arrangement, method and reason. Every criterion is optional; supply whichever reference numbers are known and all matching records are returned, or a not-found message.

    Args:
        civic_bill_id: The reference number of the billing ledger line; leave "" if unknown.
        civic_sub_id: The reference number of the civic and nonprofit subscription agreement; leave "" if unknown.
        customer_id: The customer reference number of the owning customer; leave "" if unknown.
        civic_credit_id: The reference number of the bill credit statement line that a charge prices or a correction offsets; leave "" if unknown.
        civic_ref_bill_id: The reference number of the ledger line another line refers to (the overdue charge of a late fee, the returned payment, the line a credit corrects, the deposit released); leave "" if unknown.
    """
    match = {k: v for k, v in {"civic_bill_id": civic_bill_id, "civic_sub_id": civic_sub_id, "customer_id": customer_id, "civic_credit_id": civic_credit_id, "civic_ref_bill_id": civic_ref_bill_id}.items() if v}
    rows = ctx.find("civic_billing", **match)
    return str(rows) if rows else f"No civic_billing records for {match}."

@tool(owner="agent", rw="read")
def find_civic_reviews(ctx: ToolContext, civic_review_id: str = "", civic_sub_id: str = "", customer_id: str = "") -> str:
    """Look up the annual true-up records of civic and nonprofit subscriptions: the contract year, the twelve months reviewed, credited and used kilowatt-hours, guaranteed and shortfall kilowatt-hours, average credit rate, any guarantee credit or resize, and the outcome. Every criterion is optional; supply whichever reference numbers are known and all matching records are returned, or a not-found message.

    Args:
        civic_review_id: The reference number of the annual true-up record; leave "" if unknown.
        civic_sub_id: The reference number of the civic and nonprofit subscription agreement; leave "" if unknown.
        customer_id: The customer reference number of the owning customer; leave "" if unknown.
    """
    match = {k: v for k, v in {"civic_review_id": civic_review_id, "civic_sub_id": civic_sub_id, "customer_id": customer_id}.items() if v}
    rows = ctx.find("civic_reviews", **match)
    return str(rows) if rows else f"No civic_reviews records for {match}."

@tool(owner="agent", rw="read")
def find_civic_requests(ctx: ToolContext, civic_request_id: str = "", civic_sub_id: str = "", customer_id: str = "", new_utility_account_id: str = "", civic_disputed_bill_id: str = "") -> str:
    """Look up requests received from civic and nonprofit subscribers — allocation increases and decreases, move and successor transfers, cancellations, billing disputes and billing changes — with the date received, the date they take effect and their processing state. Every criterion is optional; supply whichever reference numbers are known and all matching records are returned, or a not-found message.

    Args:
        civic_request_id: The reference number of the subscriber request; leave "" if unknown.
        civic_sub_id: The reference number of the civic and nonprofit subscription agreement; leave "" if unknown.
        customer_id: The customer reference number of the owning customer; leave "" if unknown.
        new_utility_account_id: The reference number of the utility account named in a move or successor transfer request; leave "" if unknown.
        civic_disputed_bill_id: The reference number of the ledger line under a billing dispute; leave "" if unknown.
    """
    match = {k: v for k, v in {"civic_request_id": civic_request_id, "civic_sub_id": civic_sub_id, "customer_id": customer_id, "new_utility_account_id": new_utility_account_id, "civic_disputed_bill_id": civic_disputed_bill_id}.items() if v}
    rows = ctx.find("civic_requests", **match)
    return str(rows) if rows else f"No civic_requests records for {match}."

@tool(owner="agent", rw="read")
def find_waitlist_reservations(ctx: ToolContext, wait_res_id: str = "", customer_id: str = "", utility_account_id: str = "", project_id: str = "") -> str:
    """Look up project waitlist reservations: the class, status, utility account, requested project, kilowatts and plan, the line it would convert into, partner code, submission, queue and reconfirmation dates, declines counted and closure details. Every criterion is optional; supply whichever reference numbers are known and all matching records are returned, or a not-found message.

    Args:
        wait_res_id: The reference number of the waitlist reservation; leave "" if unknown.
        customer_id: The customer reference number of the owning customer; leave "" if unknown.
        utility_account_id: The reference number of the utility account record; leave "" if unknown.
        project_id: The reference number of the community solar project; leave "" if unknown.
    """
    match = {k: v for k, v in {"wait_res_id": wait_res_id, "customer_id": customer_id, "utility_account_id": utility_account_id, "project_id": project_id}.items() if v}
    rows = ctx.find("waitlist_reservations", **match)
    return str(rows) if rows else f"No waitlist_reservations records for {match}."

@tool(owner="agent", rw="read")
def find_waitlist_offers(ctx: ToolContext, wait_offer_id: str = "", wait_res_id: str = "", customer_id: str = "", project_id: str = "") -> str:
    """Look up offers of capacity made to waitlist reservations: project, offer date, kilowatts and plan offered, first-year production and savings estimates, and the last day to accept. Every criterion is optional; supply whichever reference numbers are known and all matching records are returned, or a not-found message.

    Args:
        wait_offer_id: The reference number of the waitlist offer; leave "" if unknown.
        wait_res_id: The reference number of the waitlist reservation; leave "" if unknown.
        customer_id: The customer reference number of the owning customer; leave "" if unknown.
        project_id: The reference number of the community solar project; leave "" if unknown.
    """
    match = {k: v for k, v in {"wait_offer_id": wait_offer_id, "wait_res_id": wait_res_id, "customer_id": customer_id, "project_id": project_id}.items() if v}
    rows = ctx.find("waitlist_offers", **match)
    return str(rows) if rows else f"No waitlist_offers records for {match}."

@tool(owner="agent", rw="read")
def find_waitlist_notices(ctx: ToolContext, wait_notice_id: str = "", wait_res_id: str = "", customer_id: str = "") -> str:
    """Look up reconfirmation and queue-position notices sent for waitlist reservations. Every criterion is optional; supply whichever reference numbers are known and all matching records are returned, or a not-found message.

    Args:
        wait_notice_id: The reference number of the waitlist notice; leave "" if unknown.
        wait_res_id: The reference number of the waitlist reservation; leave "" if unknown.
        customer_id: The customer reference number of the owning customer; leave "" if unknown.
    """
    match = {k: v for k, v in {"wait_notice_id": wait_notice_id, "wait_res_id": wait_res_id, "customer_id": customer_id}.items() if v}
    rows = ctx.find("waitlist_notices", **match)
    return str(rows) if rows else f"No waitlist_notices records for {match}."

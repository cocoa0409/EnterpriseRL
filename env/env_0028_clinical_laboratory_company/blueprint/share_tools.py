"""Shared tools for env_0028_clinical_laboratory_company (Halverson Clinical Laboratories).

Every tool here is a SHARE tool: always present in its owner's tool list.
This module holds the complete record-lookup layer (one finder per table; the customers
finder doubles as the identity entry), the identity-verification write and the
transfer-to-human handoff. Customer-originated writes live in each difficulty's
task_tools.py as hidden user tools, never here.

Scenario-level operational constants built into these tools:
  K = 2   identity attributes that must match the profile to pass verification
  R = 2   explicit requests for a human after which a CUSTOMER_REQUESTED handoff applies
"""

from erlbench import ToolContext, tool


def _out(rows, label, match):
    # Code-level helper (not a tool): render a lookup result.
    return str(rows) if rows else f"No {label} found for {match}."


# ---------------------------------------------------------------- identity entry
@tool(owner="agent", rw="read")
def find_customers(ctx: ToolContext, customer_id: str = "", name: str = "", phone_number: str = "",
                   email: str = "", date_of_birth: str = "", zip_code: str = "") -> str:
    """Look up a customer profile at Halverson Clinical Laboratories to establish whose records this
    conversation is about. A profile belongs either to a patient or to a client organization (an
    ordering practice, health center, hospital outreach program or employer) and shows the name,
    date of birth, phone number, email, ZIP code, mailing address, the organization's NPI, the date
    the profile was opened, whether the patient uses the patient portal, and the customer reference
    number used on every other record. Search by the customer reference number or by whatever the
    caller naturally states; every criterion is optional, but at least one must be given. Finding a
    profile is not the same as verifying the caller's identity.

    Args:
        customer_id: The customer reference number, if already known; leave "" otherwise.
        name: The patient's or organization's name as the caller states it; leave "" if not given.
        phone_number: The phone number on the profile, 10 digits; leave "" if not given.
        email: The email address on the profile; leave "" if not given.
        date_of_birth: The patient's date of birth as YYYY-MM-DD; leave "" if not given.
        zip_code: The 5-digit ZIP code of the mailing address; leave "" if not given.

    Returns:
        The matching profile, a message that nothing matched, or a request for one more detail when
        several profiles match.
    """
    match = {k: v for k, v in {"customer_id": customer_id, "name": name, "phone_number": phone_number,
                               "email": email, "date_of_birth": date_of_birth,
                               "zip_code": zip_code}.items() if v}
    if not match:
        return "Error: provide at least one reference number or profile detail to find the customer."
    rows = ctx.fuzzy_find("customers", **match)
    if not rows:
        return f"No customer matches {match}."
    if len(rows) > 1:
        return f"Error: {len(rows)} customers match {match}; ask the caller for one more detail to tell them apart."
    return str(rows[0])


# ---------------------------------------------------------------- per-record finders
@tool(owner="agent", rw="read")
def find_orders(ctx: ToolContext, order_id: str = "", customer_id: str = "", coverage_id: str = "",
                client_account_id: str = "") -> str:
    """Look up laboratory test orders. Each order is one accession: the tests of one requisition
    that belong to one service class. It shows the service class, status, requisition number,
    how the order arrived, who is billed, the coverage and client account billed, the ordering
    physician's NPI, diagnosis, prior-authorization, ABN and consent status, any hold and its date,
    whether it is a standing order, the list-price total, any good faith estimate, and the order,
    collection, accession, result and cancellation dates. Every criterion is optional; supply any
    reference numbers already in hand.

    Args:
        order_id: The order reference number; leave "" if unknown.
        customer_id: The patient's customer reference number; leave "" if unknown.
        coverage_id: The reference number of the coverage billed for the order; leave "" if unknown.
        client_account_id: The reference number of the ordering practice's client account; leave "" if unknown.

    Returns:
        The matching orders, or a message that none were found.
    """
    match = {k: v for k, v in {"order_id": order_id, "customer_id": customer_id, "coverage_id": coverage_id,
                               "client_account_id": client_account_id}.items() if v}
    return _out(ctx.find("orders", **match), "orders", match)


@tool(owner="agent", rw="read")
def find_order_events(ctx: ToolContext, order_event_id: str = "", order_id: str = "", customer_id: str = "",
                      credited_event_id: str = "", rejected_event_id: str = "") -> str:
    """Look up the line-by-line history of test orders: test charges at list price (ordered, reflex,
    add-on, consumer oversight fee, cancellation handling fee), credits of those charges with their
    reason, specimen rejections with the specimen type and reason, recollection requests with their
    recollect-by date, corrected reports, and report-copy requests. Every criterion is optional.

    Args:
        order_event_id: The reference number of one history line; leave "" if unknown.
        order_id: The order reference number; leave "" if unknown.
        customer_id: The patient's customer reference number; leave "" if unknown.
        credited_event_id: The reference number of a charge line, to find the credit that reversed it; leave "" if unknown.
        rejected_event_id: The reference number of a rejection line, to find the recollection request that answers it; leave "" if unknown.

    Returns:
        The matching history lines, or a message that none were found.
    """
    match = {k: v for k, v in {"order_event_id": order_event_id, "order_id": order_id, "customer_id": customer_id,
                               "credited_event_id": credited_event_id,
                               "rejected_event_id": rejected_event_id}.items() if v}
    return _out(ctx.find("order_events", **match), "order history lines", match)


@tool(owner="agent", rw="read")
def find_visits(ctx: ToolContext, visit_id: str = "", customer_id: str = "", order_id: str = "") -> str:
    """Look up specimen collection visits: walk-in, scheduled, fasting, timed glucose tolerance and
    pediatric visits at Patient Service Centers, mobile in-home visits and facility bedside draws.
    Each visit shows its type, status, the order it collects and why, the site and service zone,
    booking channel and dates, appointment date and time, reschedule count, Medicare homebound
    status, additional household members, fasting statement, check-in, collection, incomplete or
    cancellation details, and any collection-service fee balance. Every criterion is optional.

    Args:
        visit_id: The visit reference number; leave "" if unknown.
        customer_id: The patient's customer reference number; leave "" if unknown.
        order_id: The reference number of the order the visit collects; leave "" if unknown.

    Returns:
        The matching visits, or a message that none were found.
    """
    match = {k: v for k, v in {"visit_id": visit_id, "customer_id": customer_id, "order_id": order_id}.items() if v}
    return _out(ctx.find("visits", **match), "visits", match)


@tool(owner="agent", rw="read")
def find_visit_events(ctx: ToolContext, visit_event_id: str = "", visit_id: str = "", customer_id: str = "",
                      assessed_event_id: str = "", paid_event_id: str = "") -> str:
    """Look up collection-service fee history on visits: fees assessed (trip, additional patient,
    weekend, late cancellation, no-show), waivers with their reason, card payments, and refunds.
    Every criterion is optional.

    Args:
        visit_event_id: The reference number of one fee line; leave "" if unknown.
        visit_id: The visit reference number; leave "" if unknown.
        customer_id: The patient's customer reference number; leave "" if unknown.
        assessed_event_id: The reference number of an assessed fee, to find its waiver or payment; leave "" if unknown.
        paid_event_id: The reference number of a fee payment, to find its refund; leave "" if unknown.

    Returns:
        The matching fee lines, or a message that none were found.
    """
    match = {k: v for k, v in {"visit_event_id": visit_event_id, "visit_id": visit_id, "customer_id": customer_id,
                               "assessed_event_id": assessed_event_id, "paid_event_id": paid_event_id}.items() if v}
    return _out(ctx.find("visit_events", **match), "visit fee lines", match)


@tool(owner="agent", rw="read")
def find_coverages(ctx: ToolContext, coverage_id: str = "", customer_id: str = "", member_id: str = "") -> str:
    """Look up the health-plan coverages a patient has on file: payer class, status, payer name,
    member ID and group number as printed on the card, relationship to the subscriber, payment
    order, employer-plan facts, and the effective, termination, verification and added dates. Every
    criterion is optional.

    Args:
        coverage_id: The coverage reference number; leave "" if unknown.
        customer_id: The patient's customer reference number; leave "" if unknown.
        member_id: The member ID exactly as printed on the insurance card; leave "" if unknown.

    Returns:
        The matching coverages, or a message that none were found.
    """
    match = {k: v for k, v in {"coverage_id": coverage_id, "customer_id": customer_id,
                               "member_id": member_id}.items() if v}
    return _out(ctx.find("coverages", **match), "coverages", match)


@tool(owner="agent", rw="read")
def find_claim_events(ctx: ToolContext, claim_event_id: str = "", coverage_id: str = "", customer_id: str = "",
                      order_id: str = "", source_claim_event_id: str = "") -> str:
    """Look up insurance claim history: eligibility checks, claims filed, corrected claims and
    reprocessing, payer payments, contractual adjustments, amounts assigned to the patient, denials
    with their denial code, and appeals filed and decided, each with its claim number, date and
    amount. Every criterion is optional.

    Args:
        claim_event_id: The reference number of one claim line; leave "" if unknown.
        coverage_id: The reference number of the coverage the claim was filed with; leave "" if unknown.
        customer_id: The patient's customer reference number; leave "" if unknown.
        order_id: The reference number of the order the claim bills; leave "" if unknown.
        source_claim_event_id: The reference number of a claim line, to find the lines that answer it (a remittance, a denial's correction or appeal, an appeal's decision); leave "" if unknown.

    Returns:
        The matching claim lines, or a message that none were found.
    """
    match = {k: v for k, v in {"claim_event_id": claim_event_id, "coverage_id": coverage_id,
                               "customer_id": customer_id, "order_id": order_id,
                               "source_claim_event_id": source_claim_event_id}.items() if v}
    return _out(ctx.find("claim_events", **match), "claim lines", match)


@tool(owner="agent", rw="read")
def find_invoices(ctx: ToolContext, invoice_id: str = "", customer_id: str = "", order_id: str = "",
                  coverage_id: str = "", plan_id: str = "") -> str:
    """Look up patient invoices. Each invoice bills what the patient owes for one order and shows
    its billing class, status, invoice number as printed on statements, the order and coverage it
    relates to, date of service, first statement date, balance due, any hold and its reason, the
    payment plan carrying it, any collection-agency placement, and its opened and closed dates.
    Every criterion is optional.

    Args:
        invoice_id: The invoice reference number; leave "" if unknown.
        customer_id: The patient's customer reference number; leave "" if unknown.
        order_id: The reference number of the order billed; leave "" if unknown.
        coverage_id: The reference number of the coverage that processed the order; leave "" if unknown.
        plan_id: The reference number of the payment plan carrying the invoice; leave "" if unknown.

    Returns:
        The matching invoices, or a message that none were found.
    """
    match = {k: v for k, v in {"invoice_id": invoice_id, "customer_id": customer_id, "order_id": order_id,
                               "coverage_id": coverage_id, "plan_id": plan_id}.items() if v}
    return _out(ctx.find("invoices", **match), "invoices", match)


@tool(owner="agent", rw="read")
def find_invoice_transactions(ctx: ToolContext, invoice_transaction_id: str = "", invoice_id: str = "",
                              customer_id: str = "", claim_event_id: str = "", assistance_case_id: str = "",
                              dispute_id: str = "", related_transaction_id: str = "",
                              target_invoice_id: str = "") -> str:
    """Look up the activity on patient invoices: amounts posted as owed, statements and final
    notices, payments with method and channel, adjustments with their type (prompt-pay discount,
    financial assistance, estimate-dispute settlement, billing-error correction, small-balance
    write-off, courtesy), returned or charged-back payments, returned-payment fees, and refunds or
    transfers of credit balances. Every criterion is optional.

    Args:
        invoice_transaction_id: The reference number of one invoice activity line; leave "" if unknown.
        invoice_id: The invoice reference number; leave "" if unknown.
        customer_id: The patient's customer reference number; leave "" if unknown.
        claim_event_id: The reference number of the claim line that assigned an amount to the patient; leave "" if unknown.
        assistance_case_id: The reference number of the assistance case behind a financial-assistance adjustment; leave "" if unknown.
        dispute_id: The reference number of a billing dispute; leave "" if unknown.
        related_transaction_id: The reference number of an activity line, to find the reversals, fees, refunds or transfers that act on it; leave "" if unknown.
        target_invoice_id: The reference number of an invoice that received a transferred credit; leave "" if unknown.

    Returns:
        The matching activity lines, or a message that none were found.
    """
    match = {k: v for k, v in {"invoice_transaction_id": invoice_transaction_id, "invoice_id": invoice_id,
                               "customer_id": customer_id, "claim_event_id": claim_event_id,
                               "assistance_case_id": assistance_case_id,
                               "dispute_id": dispute_id, "related_transaction_id": related_transaction_id,
                               "target_invoice_id": target_invoice_id}.items() if v}
    return _out(ctx.find("invoice_transactions", **match), "invoice activity lines", match)


@tool(owner="agent", rw="read")
def find_billing_disputes(ctx: ToolContext, dispute_id: str = "", customer_id: str = "", invoice_id: str = "") -> str:
    """Look up billing disputes a patient has filed on an invoice: what is disputed, its progress
    and outcome, the balance and any good faith estimate at filing, when it was filed and when it
    was decided. Every criterion is optional.

    Args:
        dispute_id: The dispute reference number; leave "" if unknown.
        customer_id: The patient's customer reference number; leave "" if unknown.
        invoice_id: The reference number of the disputed invoice; leave "" if unknown.

    Returns:
        The matching disputes, or a message that none were found.
    """
    match = {k: v for k, v in {"dispute_id": dispute_id, "customer_id": customer_id, "invoice_id": invoice_id}.items() if v}
    return _out(ctx.find("billing_disputes", **match), "billing disputes", match)


@tool(owner="agent", rw="read")
def find_payment_plans(ctx: ToolContext, plan_id: str = "", customer_id: str = "") -> str:
    """Look up patient payment plans: plan term, status, remaining plan balance, monthly installment,
    down payment, due day and first due date, automatic-payment setup, reinstatement and due-day
    change counts, and the offer, acceptance, default and closing dates. Every criterion is optional.

    Args:
        plan_id: The payment plan reference number; leave "" if unknown.
        customer_id: The patient's customer reference number; leave "" if unknown.

    Returns:
        The matching payment plans, or a message that none were found.
    """
    match = {k: v for k, v in {"plan_id": plan_id, "customer_id": customer_id}.items() if v}
    return _out(ctx.find("payment_plans", **match), "payment plans", match)


@tool(owner="agent", rw="read")
def find_plan_transactions(ctx: ToolContext, plan_transaction_id: str = "", plan_id: str = "", customer_id: str = "",
                           invoice_id: str = "") -> str:
    """Look up the activity on payment plans: invoices enrolled and their amounts, installments paid
    (with installment number, due date, payment type and method), installments missed or deferred,
    and balances released back to invoices with the reason. Every criterion is optional.

    Args:
        plan_transaction_id: The reference number of one plan activity line; leave "" if unknown.
        plan_id: The payment plan reference number; leave "" if unknown.
        customer_id: The patient's customer reference number; leave "" if unknown.
        invoice_id: The reference number of an invoice enrolled on or released from a plan; leave "" if unknown.

    Returns:
        The matching plan activity lines, or a message that none were found.
    """
    match = {k: v for k, v in {"plan_transaction_id": plan_transaction_id, "plan_id": plan_id,
                               "customer_id": customer_id, "invoice_id": invoice_id}.items() if v}
    return _out(ctx.find("plan_transactions", **match), "plan activity lines", match)


@tool(owner="agent", rw="read")
def find_assistance_cases(ctx: ToolContext, assistance_case_id: str = "", customer_id: str = "") -> str:
    """Look up financial-assistance cases: the tier assessed, status, application date and channel,
    household size and income, percent of the poverty guideline, insurance status, any presumptive
    enrollment, document request, due and completion dates, extensions, decision, award window,
    denial reason, discount granted so far, and closing date. Every criterion is optional.

    Args:
        assistance_case_id: The assistance case reference number; leave "" if unknown.
        customer_id: The applicant's customer reference number; leave "" if unknown.

    Returns:
        The matching cases, or a message that none were found.
    """
    match = {k: v for k, v in {"assistance_case_id": assistance_case_id, "customer_id": customer_id}.items() if v}
    return _out(ctx.find("assistance_cases", **match), "assistance cases", match)


@tool(owner="agent", rw="read")
def find_assistance_events(ctx: ToolContext, assistance_event_id: str = "", assistance_case_id: str = "",
                           customer_id: str = "", invoice_id: str = "", reversed_event_id: str = "") -> str:
    """Look up the activity on financial-assistance cases: documents received with their type and
    date, discounts applied to invoices, and discounts reversed with the reason. Every criterion is
    optional.

    Args:
        assistance_event_id: The reference number of one assistance activity line; leave "" if unknown.
        assistance_case_id: The assistance case reference number; leave "" if unknown.
        customer_id: The applicant's customer reference number; leave "" if unknown.
        invoice_id: The reference number of an invoice discounted under a case; leave "" if unknown.
        reversed_event_id: The reference number of a discount line, to find its reversal; leave "" if unknown.

    Returns:
        The matching activity lines, or a message that none were found.
    """
    match = {k: v for k, v in {"assistance_event_id": assistance_event_id, "assistance_case_id": assistance_case_id,
                               "customer_id": customer_id, "invoice_id": invoice_id,
                               "reversed_event_id": reversed_event_id}.items() if v}
    return _out(ctx.find("assistance_events", **match), "assistance activity lines", match)


@tool(owner="agent", rw="read")
def find_client_accounts(ctx: ToolContext, client_account_id: str = "", customer_id: str = "") -> str:
    """Look up client accounts of ordering organizations: account class, status, account number,
    location name, how the location orders, client balance, and the opened, activated, credit-hold
    and closed dates. Every criterion is optional.

    Args:
        client_account_id: The client account reference number; leave "" if unknown.
        customer_id: The organization's customer reference number; leave "" if unknown.

    Returns:
        The matching client accounts, or a message that none were found.
    """
    match = {k: v for k, v in {"client_account_id": client_account_id, "customer_id": customer_id}.items() if v}
    return _out(ctx.find("client_accounts", **match), "client accounts", match)


@tool(owner="agent", rw="read")
def find_client_transactions(ctx: ToolContext, client_transaction_id: str = "", client_account_id: str = "",
                             customer_id: str = "", order_id: str = "", credited_transaction_id: str = "") -> str:
    """Look up the activity on client accounts: client-billed tests with list and client price,
    payments, credit memos with their reason, late fees, supply orders and added courier pickups,
    each with its date and client invoice month. Every criterion is optional.

    Args:
        client_transaction_id: The reference number of one client activity line; leave "" if unknown.
        client_account_id: The client account reference number; leave "" if unknown.
        customer_id: The organization's customer reference number; leave "" if unknown.
        order_id: The reference number of an order whose test was client-billed; leave "" if unknown.
        credited_transaction_id: The reference number of a billed line, to find the credit memo that credited it; leave "" if unknown.

    Returns:
        The matching activity lines, or a message that none were found.
    """
    match = {k: v for k, v in {"client_transaction_id": client_transaction_id, "client_account_id": client_account_id,
                               "customer_id": customer_id, "order_id": order_id,
                               "credited_transaction_id": credited_transaction_id}.items() if v}
    return _out(ctx.find("client_transactions", **match), "client activity lines", match)


@tool(owner="agent", rw="read")
def find_identity_verifications(ctx: ToolContext, verification_id: str = "", customer_id: str = "") -> str:
    """Look up the identity-verification outcome recorded for a customer: whether the caller's
    identity has been verified and when it was last checked. Every criterion is optional.

    Args:
        verification_id: The verification reference number; leave "" if unknown.
        customer_id: The customer reference number; leave "" if unknown.

    Returns:
        The matching verification outcome, or a message that none was found.
    """
    match = {k: v for k, v in {"verification_id": verification_id, "customer_id": customer_id}.items() if v}
    return _out(ctx.find("identity_verifications", **match), "verification outcomes", match)


@tool(owner="agent", rw="read")
def find_handoff_requests(ctx: ToolContext, handoff_id: str = "", customer_id: str = "") -> str:
    """Look up transfers of a customer to a human representative: the reason recorded and when.
    Every criterion is optional.

    Args:
        handoff_id: The transfer reference number; leave "" if unknown.
        customer_id: The customer reference number; leave "" if unknown.

    Returns:
        The matching transfers, or a message that none were found.
    """
    match = {k: v for k, v in {"handoff_id": handoff_id, "customer_id": customer_id}.items() if v}
    return _out(ctx.find("handoff_requests", **match), "transfers to a representative", match)


# ---------------------------------------------------------------- verification write
@tool(owner="agent", rw="write")
def verify_customer_identity(ctx: ToolContext, customer_id: str, phone_number: str = "", email: str = "",
                             date_of_birth: str = "", zip_code: str = "", npi: str = "") -> str:
    """Verify the caller's identity against the customer profile and record the outcome. Identity must
    be verified before any record of the customer is discussed or changed. This tool performs the
    comparison itself: it compares each detail the caller states with the profile on file, counts
    how many match, and passes only when at least 2 match. The customer reference number only
    retrieves the profile and never counts as a match, and a name alone is never a proof of identity.
    Callers usually state only some details, so pass exactly the values the caller gave, as given,
    and leave the rest "". The outcome is recorded; if a first attempt fails and a later attempt with
    more details passes, the pass stands.

    Args:
        customer_id: The customer reference number read from the profile lookup. Required; it is used only to retrieve the profile and is not counted as a match.
        phone_number: The phone number the caller states, 10 digits with no punctuation; leave "" if not stated.
        email: The email address the caller states; leave "" if not stated.
        date_of_birth: The patient's date of birth the caller states, as YYYY-MM-DD; leave "" if not stated.
        zip_code: The 5-digit ZIP code of the mailing address the caller states; leave "" if not stated.
        npi: For a client organization, the organization's 10-digit NPI the caller states; leave "" if not stated.

    Returns:
        Whether the identity is verified and how many details matched.
    """
    if not customer_id:
        return "Error: customer_id is required; look up the customer profile first and pass its reference number."
    rows = ctx.find("customers", customer_id=customer_id)
    if not rows:
        return f"Error: no customer {customer_id}; cannot verify."
    rec = rows[0]
    supplied = {"phone_number": phone_number, "email": email, "date_of_birth": date_of_birth,
                "zip_code": zip_code, "npi": npi}
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
    if verified:
        return f"Identity verified for {customer_id} ({matched} detail(s) matched on this attempt)."
    return (f"Identity NOT verified for {customer_id}: only {matched} of the required 2 details matched. "
            "Ask the caller for another detail on file and try again.")


# ---------------------------------------------------------------- handoff write
@tool(owner="agent", rw="write")
def transfer_to_human_agent(ctx: ToolContext, customer_id: str, reason: str) -> str:
    """Transfer the customer to a human Patient Services representative and record the transfer and
    its reason. Use it in exactly two situations: when no Halverson policy can resolve what the
    customer is asking for, or when the customer has explicitly asked to speak with a person 2
    times in this conversation.

    Args:
        customer_id: The customer reference number read from the profile lookup; the profile must exist.
        reason: Exactly one of two values, never free text. POLICY_NOT_COVERED - no current policy offers a way to resolve the request. CUSTOMER_REQUESTED - the customer has explicitly asked for a human representative at least 2 times.

    Returns:
        Confirmation that the transfer was recorded, or an error for an unknown reason or customer.
    """
    allowed = {"POLICY_NOT_COVERED", "CUSTOMER_REQUESTED"}
    if reason not in allowed:
        return f"Error: unknown transfer reason '{reason}'. Valid: {', '.join(sorted(allowed))}."
    if not ctx.find("customers", customer_id=customer_id):
        return f"Error: no customer {customer_id}; cannot record the transfer."
    rid = ctx.make_id("hof_", customer_id, reason)
    ctx.create("handoff_requests", rid, handoff_id=rid, customer_id=customer_id,
               reason=reason, created_at=ctx.now())
    return f"Transfer to a human representative recorded for {customer_id} ({reason})."

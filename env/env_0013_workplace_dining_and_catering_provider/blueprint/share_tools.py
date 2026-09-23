"""Shared tools for env_0013_workplace_dining_and_catering_provider.

Every tool defined here is a SHARE tool: always present in its owner's tool list.
This module holds exactly three things — the complete record-lookup layer (one finder per
table, with the customers finder doubling as the identity entry), the identity-verification
write, and the transfer-to-human write.

Operational constants pinned by this scenario and built into the two writes below:
  K = 2  identity credentials must match before a caller is treated as verified
  R = 3  explicit requests for a human representative before CUSTOMER_REQUESTED applies
"""

from erlbench import ToolContext, tool


# --------------------------------------------------------------------------- customers

@tool(owner="agent", rw="read")
def find_customers(ctx: ToolContext, customer_id: str = "", full_name: str = "",
                   organization_name: str = "", phone_number: str = "",
                   email_address: str = "", employee_badge_number: str = "",
                   client_account_code: str = "") -> str:
    """Look up the dining profile this call is about — either a client organisation's account
    contact or an individual employee diner. Search by the profile reference number when the
    caller already has it, or by anything the caller naturally says: the company they call for,
    their own name, their direct line, their work email, the badge number on their card, or the
    client account code printed on their invoices. Every criterion is optional; supply whichever
    were given. A single matching profile is returned in full — contact details, the site and
    department it is attached to, the billing postal code and the day the profile was opened.
    When nothing matches, or when more than one profile matches, that is said plainly so another
    detail can be asked for. Finding a profile is not the same as verifying who is on the line.

    Args:
        customer_id: Id class — the profile reference number, when the caller or an earlier record already supplies it; leave "" if unknown.
        full_name: Verbatim class — the name on the profile, as the caller states it; leave "" if not given.
        organization_name: Verbatim class — the registered name of the client organisation, as the caller states it; leave "" if not given.
        phone_number: Fixed-format class — the direct telephone number on file, 10 digits with no separators; leave "" if not given.
        email_address: Verbatim class — the work email address on file; leave "" if not given.
        employee_badge_number: Fixed-format class — the 8-digit badge number printed on an employee's site badge; leave "" if not given.
        client_account_code: Fixed-format class — the client account code, written as CA- followed by 5 digits; leave "" if not given.
    """
    match = {k: v for k, v in {"customer_id": customer_id,
                               "full_name": full_name,
                               "organization_name": organization_name,
                               "phone_number": phone_number,
                               "email_address": email_address,
                               "employee_badge_number": employee_badge_number,
                               "client_account_code": client_account_code}.items() if v}
    if not match:
        return "Error: provide at least one reference number or detail to find the profile."
    rows = ctx.fuzzy_find("customers", **match)
    if not rows:
        return f"No dining profile matches {match}."
    if len(rows) > 1:
        return f"Error: {len(rows)} profiles match {match}; ask for one more detail to tell them apart."
    return str(rows[0])


# ----------------------------------------------------------- workplace cafe management

@tool(owner="agent", rw="read")
def find_cafe_contracts(ctx: ToolContext, cafe_contract_id: str = "", customer_id: str = "") -> str:
    """Retrieve the workplace cafe management contracts on file: the service model held, the site
    the cafe runs at, the state the contract is in, the term dates, the invoicing day and contact,
    the reported headcount, the suspension days already taken this contract year, and the current
    subsidy funding and unsettled invoice balances. Search by the contract reference number or by
    the client profile reference to see everything that client holds; both are optional.

    Args:
        cafe_contract_id: Id class — the cafe contract reference number; leave "" if unknown.
        customer_id: Id class — the client profile reference number, to list that client's cafe contracts; leave "" if unknown.
    """
    match = {k: v for k, v in {"cafe_contract_id": cafe_contract_id,
                               "customer_id": customer_id}.items() if v}
    rows = ctx.find("cafe_contracts", **match)
    return str(rows) if rows else f"No cafe management contracts for {match}."


@tool(owner="agent", rw="read")
def find_cafe_ledger(ctx: ToolContext, cafe_ledger_id: str = "", cafe_contract_id: str = "",
                     customer_id: str = "") -> str:
    """Retrieve the money postings made against a workplace cafe contract: management fee
    invoices, subsidy funding paid in by the client, subsidy drawn down by employee meals,
    payments received, service credits allowed and penalty charges raised. Each posting carries
    its billing subtype, amount, posting day, billing period, and the invoice, funding lot or
    originating record it relates to. Search by the posting reference, by the contract reference,
    or by the client profile reference; all are optional.

    Args:
        cafe_ledger_id: Id class — the reference number of a single posting; leave "" if unknown.
        cafe_contract_id: Id class — the cafe contract reference number, to list its postings; leave "" if unknown.
        customer_id: Id class — the client profile reference number; leave "" if unknown.
    """
    match = {k: v for k, v in {"cafe_ledger_id": cafe_ledger_id,
                               "cafe_contract_id": cafe_contract_id,
                               "customer_id": customer_id}.items() if v}
    rows = ctx.find("cafe_ledger", **match)
    return str(rows) if rows else f"No cafe ledger postings for {match}."


@tool(owner="agent", rw="read")
def find_cafe_service_requests(ctx: ToolContext, cafe_service_request_id: str = "",
                               customer_id: str = "", cafe_contract_id: str = "") -> str:
    """Retrieve the cafe service requests logged for a client — suspensions, resumptions, service
    model changes, notices of termination and service credit claims — together with what was asked
    for, the effective day requested, the service model requested where one applies, the record the
    request concerns, where the request has got to and when it was logged. Every criterion is
    optional.

    Args:
        cafe_service_request_id: Id class — the reference number of a single request; leave "" if unknown.
        customer_id: Id class — the client profile reference number; leave "" if unknown.
        cafe_contract_id: Id class — the cafe contract reference number the requests concern; leave "" if unknown.
    """
    match = {k: v for k, v in {"cafe_service_request_id": cafe_service_request_id,
                               "customer_id": customer_id,
                               "cafe_contract_id": cafe_contract_id}.items() if v}
    rows = ctx.find("cafe_service_requests", **match)
    return str(rows) if rows else f"No cafe service requests for {match}."


# ------------------------------------------------------------------ corporate catering

@tool(owner="agent", rw="read")
def find_catering_agreements(ctx: ToolContext, catering_agreement_id: str = "",
                             customer_id: str = "") -> str:
    """Retrieve the corporate catering service agreements on file: the service level held, the
    state of the agreement, the client account code it bills under, the term dates, the open-order
    credit allowed, the standing discount negotiated, the default delivery site, the invoicing
    contact and the current unsettled balance. Search by the agreement reference number or by the
    client profile reference; both are optional.

    Args:
        catering_agreement_id: Id class — the catering agreement reference number; leave "" if unknown.
        customer_id: Id class — the client profile reference number, to list that client's catering agreements; leave "" if unknown.
    """
    match = {k: v for k, v in {"catering_agreement_id": catering_agreement_id,
                               "customer_id": customer_id}.items() if v}
    rows = ctx.find("catering_agreements", **match)
    return str(rows) if rows else f"No catering agreements for {match}."


@tool(owner="agent", rw="read")
def find_catering_orders(ctx: ToolContext, catering_order_id: str = "",
                         catering_agreement_id: str = "", customer_id: str = "") -> str:
    """Retrieve the catering order history on an agreement: orders placed, amendments,
    cancellations, deliveries completed, invoices raised, cancellation fees charged, payments
    received and service credits allowed. Each row names the order it concerns, its billing
    subtype, its amount, the service day and start time, the guest count it was priced on, the
    menu package, the delivery site, the channel the instruction arrived through and, where one
    was given, the day notice was given. Every criterion is optional.

    Args:
        catering_order_id: Id class — the reference number of a single order row; leave "" if unknown.
        catering_agreement_id: Id class — the catering agreement reference number, to list its order history; leave "" if unknown.
        customer_id: Id class — the client profile reference number; leave "" if unknown.
    """
    match = {k: v for k, v in {"catering_order_id": catering_order_id,
                               "catering_agreement_id": catering_agreement_id,
                               "customer_id": customer_id}.items() if v}
    rows = ctx.find("catering_orders", **match)
    return str(rows) if rows else f"No catering order rows for {match}."


@tool(owner="agent", rw="read")
def find_catering_change_requests(ctx: ToolContext, catering_change_request_id: str = "",
                                  customer_id: str = "", catering_agreement_id: str = "") -> str:
    """Retrieve the change requests logged against catering orders — cancellations, guest count
    changes, date moves, menu changes and credit claims — showing the order each concerns, the
    service day and guest count asked for, where the request has got to and when it was logged.
    Every criterion is optional.

    Args:
        catering_change_request_id: Id class — the reference number of a single change request; leave "" if unknown.
        customer_id: Id class — the client profile reference number; leave "" if unknown.
        catering_agreement_id: Id class — the catering agreement reference number the requests concern; leave "" if unknown.
    """
    match = {k: v for k, v in {"catering_change_request_id": catering_change_request_id,
                               "customer_id": customer_id,
                               "catering_agreement_id": catering_agreement_id}.items() if v}
    rows = ctx.find("catering_change_requests", **match)
    return str(rows) if rows else f"No catering change requests for {match}."


# --------------------------------------------------------- private events and banquets

@tool(owner="agent", rw="read")
def find_banquet_agreements(ctx: ToolContext, banquet_agreement_id: str = "",
                            customer_id: str = "") -> str:
    """Retrieve the private event and banquet services agreements on file: the event package held,
    the venue it is written against, the state of the agreement, the term dates, the invoicing
    contact, and the client money currently held on deposit alongside the unsettled event balance.
    Search by the agreement reference number or by the client profile reference; both are optional.

    Args:
        banquet_agreement_id: Id class — the banquet agreement reference number; leave "" if unknown.
        customer_id: Id class — the client profile reference number, to list that client's event agreements; leave "" if unknown.
    """
    match = {k: v for k, v in {"banquet_agreement_id": banquet_agreement_id,
                               "customer_id": customer_id}.items() if v}
    rows = ctx.find("banquet_agreements", **match)
    return str(rows) if rows else f"No banquet agreements for {match}."


@tool(owner="agent", rw="read")
def find_banquet_ledger(ctx: ToolContext, banquet_ledger_id: str = "",
                        banquet_agreement_id: str = "", customer_id: str = "") -> str:
    """Retrieve everything recorded against a client's event bookings: events booked, deposits
    taken, guarantees confirmed, events delivered, invoices raised, deposits applied or refunded,
    cancellations, cancellation charges and payments received. Each row names the booking it
    concerns, its billing subtype and amount, the event day and venue, the room set-up, the
    guaranteed and actual guest counts, and the day notice was given where one was given. Every
    criterion is optional.

    Args:
        banquet_ledger_id: Id class — the reference number of a single event posting; leave "" if unknown.
        banquet_agreement_id: Id class — the banquet agreement reference number, to list its bookings and postings; leave "" if unknown.
        customer_id: Id class — the client profile reference number; leave "" if unknown.
    """
    match = {k: v for k, v in {"banquet_ledger_id": banquet_ledger_id,
                               "banquet_agreement_id": banquet_agreement_id,
                               "customer_id": customer_id}.items() if v}
    rows = ctx.find("banquet_ledger", **match)
    return str(rows) if rows else f"No banquet postings for {match}."


@tool(owner="agent", rw="read")
def find_banquet_event_intake(ctx: ToolContext, banquet_event_request_id: str = "",
                              customer_id: str = "", banquet_agreement_id: str = "") -> str:
    """Retrieve the event requests logged against bookings — cancellations, date moves, guarantee
    changes, venue changes and credit claims — showing the booking each concerns, the event day and
    guest count asked for, where the request has got to and when it was logged. Every criterion is
    optional.

    Args:
        banquet_event_request_id: Id class — the reference number of a single event request; leave "" if unknown.
        customer_id: Id class — the client profile reference number; leave "" if unknown.
        banquet_agreement_id: Id class — the banquet agreement reference number the requests concern; leave "" if unknown.
    """
    match = {k: v for k, v in {"banquet_event_request_id": banquet_event_request_id,
                               "customer_id": customer_id,
                               "banquet_agreement_id": banquet_agreement_id}.items() if v}
    rows = ctx.find("banquet_event_intake", **match)
    return str(rows) if rows else f"No banquet event requests for {match}."


# ------------------------------------------------------------ unattended micro markets

@tool(owner="agent", rw="read")
def find_market_agreements(ctx: ToolContext, market_agreement_id: str = "",
                           customer_id: str = "") -> str:
    """Retrieve the unattended micro market agreements on file: the market format held, the site
    and kiosk it runs on, the state of the agreement, the term and installation dates, the reported
    headcount, the invoicing contact, and the current subsidy funding and unsettled settlement
    balances. Search by the agreement reference number or by the client profile reference; both are
    optional.

    Args:
        market_agreement_id: Id class — the micro market agreement reference number; leave "" if unknown.
        customer_id: Id class — the client profile reference number, to list that client's markets; leave "" if unknown.
    """
    match = {k: v for k, v in {"market_agreement_id": market_agreement_id,
                               "customer_id": customer_id}.items() if v}
    rows = ctx.find("market_agreements", **match)
    return str(rows) if rows else f"No micro market agreements for {match}."


@tool(owner="agent", rw="read")
def find_market_ledger(ctx: ToolContext, market_ledger_id: str = "", market_agreement_id: str = "",
                       customer_id: str = "") -> str:
    """Retrieve the postings made against a micro market agreement: monthly settlement invoices,
    subsidy funding paid in, subsidy drawn down at the kiosk, settlement payments received,
    inventory shrink adjustments and service credits allowed. Each posting carries its billing
    subtype, amount, posting day, settlement period, kiosk, product group and the invoice or
    originating record it relates to. Every criterion is optional.

    Args:
        market_ledger_id: Id class — the reference number of a single posting; leave "" if unknown.
        market_agreement_id: Id class — the micro market agreement reference number, to list its postings; leave "" if unknown.
        customer_id: Id class — the client profile reference number; leave "" if unknown.
    """
    match = {k: v for k, v in {"market_ledger_id": market_ledger_id,
                               "market_agreement_id": market_agreement_id,
                               "customer_id": customer_id}.items() if v}
    rows = ctx.find("market_ledger", **match)
    return str(rows) if rows else f"No micro market postings for {match}."


@tool(owner="agent", rw="read")
def find_market_service_intake(ctx: ToolContext, market_service_request_id: str = "",
                               customer_id: str = "", market_agreement_id: str = "") -> str:
    """Retrieve the micro market service requests logged for a client — suspensions, resumptions,
    planogram changes, shrink disputes and service credit claims — showing what was asked for, the
    effective day requested, the record the request concerns, where it has got to and when it was
    logged. Every criterion is optional.

    Args:
        market_service_request_id: Id class — the reference number of a single request; leave "" if unknown.
        customer_id: Id class — the client profile reference number; leave "" if unknown.
        market_agreement_id: Id class — the micro market agreement reference number the requests concern; leave "" if unknown.
    """
    match = {k: v for k, v in {"market_service_request_id": market_service_request_id,
                               "customer_id": customer_id,
                               "market_agreement_id": market_agreement_id}.items() if v}
    rows = ctx.find("market_service_intake", **match)
    return str(rows) if rows else f"No micro market service requests for {match}."


# ----------------------------------------------------------- employee meal accounts

@tool(owner="agent", rw="read")
def find_meal_accounts(ctx: ToolContext, meal_account_id: str = "", customer_id: str = "") -> str:
    """Retrieve an employee's workplace meal accounts: the plan held, the state of the account, the
    badge it is tapped with, the site and employer programme funding it, the enrolment and
    activation days, the payroll cycle it is recovered on, and the current spendable balance,
    unspent employer allowance and payroll arrears. Search by the account reference number or by the
    employee profile reference; both are optional.

    Args:
        meal_account_id: Id class — the meal account reference number; leave "" if unknown.
        customer_id: Id class — the employee profile reference number, to list that employee's accounts; leave "" if unknown.
    """
    match = {k: v for k, v in {"meal_account_id": meal_account_id,
                               "customer_id": customer_id}.items() if v}
    rows = ctx.find("meal_accounts", **match)
    return str(rows) if rows else f"No employee meal accounts for {match}."


@tool(owner="agent", rw="read")
def find_meal_transactions(ctx: ToolContext, meal_transaction_id: str = "",
                           meal_account_id: str = "", customer_id: str = "") -> str:
    """Retrieve the activity on an employee meal account: meals rung at the till, value loaded onto
    the account, employer allowance granted and applied, refunds, payroll deductions, charges
    accrued for payroll recovery and overdraft charges. Each row carries its transaction subtype,
    amount, posting day, meal period, outlet, till reference, how it was tendered, the payroll
    period it is recovered in, the allowance lot it touched and, on a reversal or adjustment, the
    till transaction it relates back to. Every criterion is optional.

    Args:
        meal_transaction_id: Id class — the reference number of a single transaction row; leave "" if unknown.
        meal_account_id: Id class — the meal account reference number, to list its activity; leave "" if unknown.
        customer_id: Id class — the employee profile reference number; leave "" if unknown.
    """
    match = {k: v for k, v in {"meal_transaction_id": meal_transaction_id,
                               "meal_account_id": meal_account_id,
                               "customer_id": customer_id}.items() if v}
    rows = ctx.find("meal_transactions", **match)
    return str(rows) if rows else f"No meal account transactions for {match}."


@tool(owner="agent", rw="read")
def find_meal_closure_requests(ctx: ToolContext, meal_closure_request_id: str = "",
                               customer_id: str = "", meal_account_id: str = "") -> str:
    """Retrieve the requests an employee has logged on their meal account — closures, plan changes,
    refund requests, leave of absence and reviews of a spending restriction — showing the plan and
    effective day asked for, the record the request concerns, where the request has got to and when
    it was logged. Every criterion is optional.

    Args:
        meal_closure_request_id: Id class — the reference number of a single request; leave "" if unknown.
        customer_id: Id class — the employee profile reference number; leave "" if unknown.
        meal_account_id: Id class — the meal account reference number the requests concern; leave "" if unknown.
    """
    match = {k: v for k, v in {"meal_closure_request_id": meal_closure_request_id,
                               "customer_id": customer_id,
                               "meal_account_id": meal_account_id}.items() if v}
    rows = ctx.find("meal_closure_requests", **match)
    return str(rows) if rows else f"No meal account requests for {match}."


# ------------------------------------------------------------- pantry and beverage

@tool(owner="agent", rw="read")
def find_pantry_agreements(ctx: ToolContext, pantry_agreement_id: str = "",
                           customer_id: str = "") -> str:
    """Retrieve the office pantry and beverage programme agreements on file: the programme held,
    the site served, the state of the agreement, the term dates, the standing delivery weekday, the
    reported headcount, the invoicing contact and the current unsettled balance. Search by the
    agreement reference number or by the client profile reference; both are optional.

    Args:
        pantry_agreement_id: Id class — the pantry agreement reference number; leave "" if unknown.
        customer_id: Id class — the client profile reference number, to list that client's pantry programmes; leave "" if unknown.
    """
    match = {k: v for k, v in {"pantry_agreement_id": pantry_agreement_id,
                               "customer_id": customer_id}.items() if v}
    rows = ctx.find("pantry_agreements", **match)
    return str(rows) if rows else f"No pantry agreements for {match}."


@tool(owner="agent", rw="read")
def find_pantry_ledger(ctx: ToolContext, pantry_ledger_id: str = "", pantry_agreement_id: str = "",
                       customer_id: str = "") -> str:
    """Retrieve the postings made against a pantry programme: deliveries confirmed, programme fees
    invoiced, product overage charged above the allowance, payments received and service credits
    allowed. Each posting carries its billing subtype, amount, posting day, billing period, product
    group, delivery site and the delivery or invoice it relates to. Every criterion is optional.

    Args:
        pantry_ledger_id: Id class — the reference number of a single posting; leave "" if unknown.
        pantry_agreement_id: Id class — the pantry agreement reference number, to list its postings; leave "" if unknown.
        customer_id: Id class — the client profile reference number; leave "" if unknown.
    """
    match = {k: v for k, v in {"pantry_ledger_id": pantry_ledger_id,
                               "pantry_agreement_id": pantry_agreement_id,
                               "customer_id": customer_id}.items() if v}
    rows = ctx.find("pantry_ledger", **match)
    return str(rows) if rows else f"No pantry postings for {match}."


# ---------------------------------------------------------------- vending services

@tool(owner="agent", rw="read")
def find_vending_agreements(ctx: ToolContext, vending_agreement_id: str = "",
                            customer_id: str = "") -> str:
    """Retrieve the vending services agreements on file: the programme held, the site the machines
    stand at, how many machines are placed, the state of the agreement, the term and commencement
    dates, the statement contact, the commission accrued to the client but not yet paid out, and any
    unsettled balance. Search by the agreement reference number or by the client profile reference;
    both are optional.

    Args:
        vending_agreement_id: Id class — the vending agreement reference number; leave "" if unknown.
        customer_id: Id class — the client profile reference number, to list that client's vending programmes; leave "" if unknown.
    """
    match = {k: v for k, v in {"vending_agreement_id": vending_agreement_id,
                               "customer_id": customer_id}.items() if v}
    rows = ctx.find("vending_agreements", **match)
    return str(rows) if rows else f"No vending agreements for {match}."


@tool(owner="agent", rw="read")
def find_vending_ledger(ctx: ToolContext, vending_ledger_id: str = "",
                        vending_agreement_id: str = "", customer_id: str = "") -> str:
    """Retrieve the postings made against a vending agreement: commission accrued to the client,
    commission paid out, service calls logged against a machine, subsidy invoiced to the client and
    payments received. Each posting carries its billing subtype, amount, posting day, statement
    period, machine, product group and the statement or service call it relates to. Every criterion
    is optional.

    Args:
        vending_ledger_id: Id class — the reference number of a single posting; leave "" if unknown.
        vending_agreement_id: Id class — the vending agreement reference number, to list its postings; leave "" if unknown.
        customer_id: Id class — the client profile reference number; leave "" if unknown.
    """
    match = {k: v for k, v in {"vending_ledger_id": vending_ledger_id,
                               "vending_agreement_id": vending_agreement_id,
                               "customer_id": customer_id}.items() if v}
    rows = ctx.find("vending_ledger", **match)
    return str(rows) if rows else f"No vending postings for {match}."


# ------------------------------------------------------------------- service records

@tool(owner="agent", rw="read")
def find_verification_log(ctx: ToolContext, verification_id: str = "", customer_id: str = "") -> str:
    """Retrieve the identity verification record held for a profile: whether the caller on that
    profile has been verified and the moment of the most recent attempt. Search by the verification
    record reference or by the profile reference; both are optional.

    Args:
        verification_id: Id class — the verification record reference number; leave "" if unknown.
        customer_id: Id class — the profile reference number whose verification record is wanted; leave "" if unknown.
    """
    match = {k: v for k, v in {"verification_id": verification_id,
                               "customer_id": customer_id}.items() if v}
    rows = ctx.find("verification_log", **match)
    return str(rows) if rows else f"No verification record for {match}."


@tool(owner="agent", rw="read")
def find_handoff_log(ctx: ToolContext, handoff_id: str = "", customer_id: str = "") -> str:
    """Retrieve the record of calls passed to a human representative for a profile, with the reason
    recorded and the moment of the handoff. Search by the handoff record reference or by the profile
    reference; both are optional.

    Args:
        handoff_id: Id class — the handoff record reference number; leave "" if unknown.
        customer_id: Id class — the profile reference number whose handoffs are wanted; leave "" if unknown.
    """
    match = {k: v for k, v in {"handoff_id": handoff_id, "customer_id": customer_id}.items() if v}
    rows = ctx.find("handoff_log", **match)
    return str(rows) if rows else f"No handoff records for {match}."


# ------------------------------------------------------------------------- the writes

@tool(owner="agent", rw="write")
def verify_caller_identity(ctx: ToolContext, customer_id: str, phone_number: str = "",
                           email_address: str = "", employee_badge_number: str = "",
                           client_account_code: str = "", billing_zip_code: str = "",
                           profile_opened_date: str = "") -> str:
    """Verify who is on the line against the profile on file and record the outcome. Nothing may be
    quoted back about a dining account, and no money may be moved on one, until this has passed.
    The comparison is done here rather than judged in conversation: each detail the caller states is
    checked against the profile, and verification passes once at least 2 of them match. The profile
    reference number is used only to fetch the right profile and is never counted as one of the
    matching details. Callers usually remember only some of what is on file, so pass exactly what
    was said, word for word, and leave the rest empty. The outcome is kept on the profile; if a
    first attempt falls short and a later one succeeds with another detail, the pass stands.

    Args:
        customer_id: Id class — the profile reference number, read from the profile lookup. Required; used only to retrieve the profile and never counted toward the match.
        phone_number: Fixed-format class — the direct telephone number the caller gives, 10 digits with no separators; leave "" if not stated.
        email_address: Verbatim class — the work email address the caller gives, exactly as stated; leave "" if not stated.
        employee_badge_number: Fixed-format class — the badge number the caller reads off their site badge, 8 digits with no separators; leave "" if not stated.
        client_account_code: Fixed-format class — the client account code the caller reads off an invoice, written as CA- followed by 5 digits; leave "" if not stated.
        billing_zip_code: Fixed-format class — the postal code of the billing address, 5 digits; leave "" if not stated.
        profile_opened_date: Fixed-format class — the day the profile was opened, as YYYY-MM-DD; leave "" if not stated.
    """
    if not customer_id:
        return "Error: customer_id is required; locate the profile first and pass its reference."
    rows = ctx.find("customers", customer_id=customer_id)
    if not rows:
        return f"Error: no profile {customer_id}; cannot verify."
    rec = rows[0]
    # The locator is deliberately absent from `supplied`: fetching a profile is not proving identity.
    supplied = {"phone_number": phone_number,
                "email_address": email_address,
                "employee_badge_number": employee_badge_number,
                "client_account_code": client_account_code,
                "billing_zip_code": billing_zip_code,
                "profile_opened_date": profile_opened_date}
    matched = sum(1 for field, value in supplied.items()
                  if value and str(rec.get(field)) == str(value))
    verified = matched >= 2
    rid = ctx.make_id("ver_", customer_id)
    # Store only the reproducible boolean; the match count depends on which subset the caller happened
    # to state. Upsert and never downgrade: a later successful attempt must stand.
    prior = ctx.find("verification_log", verification_id=rid)
    verified = verified or bool(prior and prior[0].get("verified"))
    if prior:
        ctx.update("verification_log", rid, verified=verified, verified_at=ctx.now())
    else:
        ctx.create("verification_log", rid, verification_id=rid, customer_id=customer_id,
                   verified=verified, verified_at=ctx.now())
    return (f"Identity verified for {customer_id} ({matched} detail(s) matched)." if verified
            else f"Identity NOT verified for {customer_id} (only {matched} of the required 2 details "
                 "matched). Ask the caller for another detail held on the profile and try again.")


@tool(owner="agent", rw="write")
def transfer_to_human_agent(ctx: ToolContext, customer_id: str, reason: str) -> str:
    """Pass the call to a human dining services representative and record why it was passed on. Use
    it in two situations and no others: when nothing in the published policy can settle what the
    caller is asking for, and when the caller has asked outright for a human representative at least
    3 times.

    Args:
        customer_id: Id class — the profile reference number of the caller being passed on, read from the profile lookup; the profile must exist.
        reason: Enum class — one of POLICY_NOT_COVERED / CUSTOMER_REQUESTED, never free text.
            POLICY_NOT_COVERED — no published policy offers a way to resolve the request;
            CUSTOMER_REQUESTED — the caller has explicitly asked for a human representative at least 3 times.
    """
    allowed = {"POLICY_NOT_COVERED", "CUSTOMER_REQUESTED"}
    if reason not in allowed:
        return f"Error: unknown handoff reason '{reason}'. Valid: {', '.join(sorted(allowed))}."
    if not ctx.find("customers", customer_id=customer_id):
        return f"Error: no profile {customer_id}; cannot record handoff."
    rid = ctx.make_id("hof_", customer_id, reason)
    ctx.create("handoff_log", rid, handoff_id=rid, customer_id=customer_id,
               reason=reason, created_at=ctx.now())
    return f"Call passed to a human dining services representative for {customer_id} ({reason})."

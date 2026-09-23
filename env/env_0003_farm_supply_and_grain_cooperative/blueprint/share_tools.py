"""Shared member-services tools for Prairie Ridge Cooperative Association.

Everything defined here is always on the desk: the complete record-lookup layer over the
cooperative's books, the identity check that must clear before any account business is
transacted, and the single route to a human member-services representative.
"""

from erlbench import ToolContext, tool

# Scenario-level operational constants. These are service conventions of the cooperative,
# not product policy: they are built into the tools below and stated in their docstrings.
VERIFICATION_MATCH_THRESHOLD = 2   # K: profile details that must match before identity clears
HUMAN_REQUEST_THRESHOLD = 2        # R: explicit asks for a person before a handoff is warranted


@tool(owner="agent", rw="read")
def find_members(ctx: ToolContext, customer_id: str = "", member_number: str = "",
                 phone_number: str = "", email: str = "", name: str = "",
                 farm_name: str = "") -> str:
    """Look up the membership profile so you know whose account the call concerns.

    A caller rarely knows an internal reference, so this search accepts whatever they can
    naturally say: the membership number from a settlement sheet, the mobile number or email
    on file, their own name, or the name the farm trades under. Every criterion is optional —
    supply the ones you have, and supply more when the first search comes back with several
    possible members. A hit returns the whole profile: contact details, county, the last four
    digits of the taxpayer number, the date the membership was accepted, the home facility and
    the standing of the membership itself. Finding a member is not the same as proving who is
    on the line; identity is established separately before any account business is done.

    Args:
        customer_id: The member's internal reference number; leave "" if unknown.
        member_number: The membership number as printed on statements, of the form M- followed
            by five digits (e.g. M-04821); leave "" if not provided.
        phone_number: The mobile number on file, 10 digits with no separators; leave "" if not
            provided.
        email: The email address on file for statements and confirmations; leave "" if not
            provided.
        name: The member's name as it appears on the membership application; leave "" if not
            provided.
        farm_name: The farm or farming entity name the member trades under; leave "" if not
            provided.
    """
    match = {k: v for k, v in {"customer_id": customer_id, "member_number": member_number,
                               "phone_number": phone_number, "email": email,
                               "name": name, "farm_name": farm_name}.items() if v}
    if not match:
        return "Error: provide at least one detail to search the membership records by."
    rows = ctx.fuzzy_find("customers", **match)
    if not rows:
        return f"No member matches {match}."
    if len(rows) > 1:
        return f"Error: {len(rows)} members match {match}; ask for one more detail to narrow it down."
    return str(rows[0])


@tool(owner="agent", rw="read")
def find_grain_contracts(ctx: ToolContext, contract_id: str = "", customer_id: str = "") -> str:
    """Retrieve a member's grain marketing contracts.

    Each record states which programme the grain is sold under, the commodity and crop year,
    the bushels committed and the bushels still owed, any bushels sitting unpriced, the futures
    month and basis the price is referenced to, the delivery window and the facility the grain
    is called to, and where the contract stands in its life. Both criteria are optional: give
    the contract reference for one contract, or the member reference to see everything they
    have on the books.

    Args:
        contract_id: The internal reference of one grain marketing contract; leave "" if unknown.
        customer_id: The member's internal reference number, to list all of their contracts;
            leave "" if unknown.
    """
    match = {k: v for k, v in {"contract_id": contract_id, "customer_id": customer_id}.items() if v}
    rows = ctx.find("grain_contracts", **match)
    return str(rows) if rows else f"No grain marketing contracts for {match}."


@tool(owner="agent", rw="read")
def find_grain_ledger_entries(ctx: ToolContext, ledger_id: str = "", contract_id: str = "",
                              customer_id: str = "") -> str:
    """Retrieve the grain ledger: every load, pricing, roll, settlement, deduction and payment
    recorded against a member's grain business.

    Rows carry the scale ticket and its grade readings, the bushels applied, the date bushels
    entered an unpriced position, pricing confirmations with the futures level and basis behind
    them, roll confirmations with the months moved between, settlement statements with their
    gross and net, the deduction lines carried on those statements, and the payments released.
    Give a ledger reference for one row, a contract reference for one contract's history, or a
    member reference for everything in their name.

    Args:
        ledger_id: The internal reference of one grain ledger row; leave "" if unknown.
        contract_id: The internal reference of the grain marketing contract whose history is
            wanted; leave "" if unknown.
        customer_id: The member's internal reference number; leave "" if unknown.
    """
    match = {k: v for k, v in {"ledger_id": ledger_id, "contract_id": contract_id,
                               "customer_id": customer_id}.items() if v}
    rows = ctx.find("grain_ledger", **match)
    return str(rows) if rows else f"No grain ledger entries for {match}."


@tool(owner="agent", rw="read")
def find_grain_pricing_orders(ctx: ToolContext, pricing_order_id: str = "", customer_id: str = "",
                              contract_id: str = "") -> str:
    """Retrieve the pricing instructions a member has lodged with the grain desk.

    Each record shows what was asked for — pricing delayed-price bushels, fixing a basis, fixing
    futures, resting a target offer, or requesting a roll — together with the bushels and any
    level named, whether the member has signed the instruction, when the desk registered it, the
    trading day it is worked on, and how far it has progressed. Instructions that are only
    received or awaiting confirmation have moved no bushels.

    Args:
        pricing_order_id: The internal reference of one pricing instruction; leave "" if unknown.
        customer_id: The member's internal reference number; leave "" if unknown.
        contract_id: The internal reference of the grain marketing contract the instruction
            applies to; leave "" if unknown.
    """
    match = {k: v for k, v in {"pricing_order_id": pricing_order_id, "customer_id": customer_id,
                               "contract_id": contract_id}.items() if v}
    rows = ctx.find("grain_pricing_intake", **match)
    return str(rows) if rows else f"No pricing instructions for {match}."


@tool(owner="agent", rw="read")
def find_storage_agreements(ctx: ToolContext, agreement_id: str = "", customer_id: str = "") -> str:
    """Retrieve a member's grain storage agreements.

    Each record names the storage programme, the commodity and crop year in store, the facility
    holding it, the bushels on hand and how many of them are already pledged, the date grain
    first went in, the date storage is billed and paid through, the grade the grain was received
    on, any warehouse receipt issued against it, and where the agreement stands in its life.

    Args:
        agreement_id: The internal reference of one storage agreement; leave "" if unknown.
        customer_id: The member's internal reference number, to list all of their agreements;
            leave "" if unknown.
    """
    match = {k: v for k, v in {"agreement_id": agreement_id, "customer_id": customer_id}.items() if v}
    rows = ctx.find("storage_agreements", **match)
    return str(rows) if rows else f"No storage agreements for {match}."


@tool(owner="agent", rw="read")
def find_storage_charges(ctx: ToolContext, charge_id: str = "", agreement_id: str = "",
                         customer_id: str = "") -> str:
    """Retrieve the storage account activity: deposits, storage accruals, drying, shrink, grade
    discounts, handling, load-outs and the settlements that cleared them.

    Rows state the period an accrual covers, the basis the rate is quoted on, the bushels acted
    on, the moisture readings and points taken out on a drying pass, the bushels lost to shrink,
    the load-out order and scale tickets behind a movement, the invoice the charge was billed on
    and whether it has been paid.

    Args:
        charge_id: The internal reference of one storage account row; leave "" if unknown.
        agreement_id: The internal reference of the storage agreement whose activity is wanted;
            leave "" if unknown.
        customer_id: The member's internal reference number; leave "" if unknown.
    """
    match = {k: v for k, v in {"charge_id": charge_id, "agreement_id": agreement_id,
                               "customer_id": customer_id}.items() if v}
    rows = ctx.find("storage_charges", **match)
    return str(rows) if rows else f"No storage account activity for {match}."


@tool(owner="agent", rw="read")
def find_storage_requests(ctx: ToolContext, request_id: str = "", customer_id: str = "",
                          agreement_id: str = "") -> str:
    """Retrieve the service requests a member has lodged against stored grain.

    Each record shows what was asked for — a load-out, a transfer of stored bushels onto a
    marketing contract, issuance of a warehouse receipt, early termination of the agreement, or
    a quality recheck — with the bushels and date named, whether the member has signed it, when
    the elevator registered it, and how far it has progressed. Only a completed request has
    actually moved grain.

    Args:
        request_id: The internal reference of one storage service request; leave "" if unknown.
        customer_id: The member's internal reference number; leave "" if unknown.
        agreement_id: The internal reference of the storage agreement the request applies to;
            leave "" if unknown.
    """
    match = {k: v for k, v in {"request_id": request_id, "customer_id": customer_id,
                               "agreement_id": agreement_id}.items() if v}
    rows = ctx.find("storage_requests", **match)
    return str(rows) if rows else f"No storage service requests for {match}."


@tool(owner="agent", rw="read")
def find_agronomy_accounts(ctx: ToolContext, account_id: str = "", customer_id: str = "") -> str:
    """Retrieve a member's crop input purchasing accounts.

    Each record names the purchasing programme, the approved credit ceiling and the balance
    currently carried against it, any unspent prepay money held to the member's credit, the
    payment terms and statement day, the acres enrolled for the crop year, the date of the last
    credit review and the credit department's standing decision, whether a security interest is
    on file, and where the account stands in its life.

    Args:
        account_id: The internal reference of one crop input account; leave "" if unknown.
        customer_id: The member's internal reference number, to list all of their input
            accounts; leave "" if unknown.
    """
    match = {k: v for k, v in {"account_id": account_id, "customer_id": customer_id}.items() if v}
    rows = ctx.find("agronomy_accounts", **match)
    return str(rows) if rows else f"No crop input accounts for {match}."


@tool(owner="agent", rw="read")
def find_agronomy_invoices(ctx: ToolContext, invoice_id: str = "", account_id: str = "",
                           customer_id: str = "") -> str:
    """Retrieve crop input billing activity: invoices, prepay bookings and their drawdowns,
    payments, service charges on overdue balances, discounts and credit memos.

    Rows carry the invoice number and its date and due date, the input class and product as
    written on the delivery ticket, the quantity and unit price, any discount granted and on
    what footing, the money moved, the remittance reference and method behind a payment, the
    field the product went to, and the account balance immediately after the row posted.

    Args:
        invoice_id: The internal reference of one crop input billing row; leave "" if unknown.
        account_id: The internal reference of the crop input account whose activity is wanted;
            leave "" if unknown.
        customer_id: The member's internal reference number; leave "" if unknown.
    """
    match = {k: v for k, v in {"invoice_id": invoice_id, "account_id": account_id,
                               "customer_id": customer_id}.items() if v}
    rows = ctx.find("agronomy_invoices", **match)
    return str(rows) if rows else f"No crop input billing activity for {match}."


@tool(owner="agent", rw="read")
def find_agronomy_orders(ctx: ToolContext, order_id: str = "", customer_id: str = "",
                         account_id: str = "") -> str:
    """Retrieve the requests a member has lodged with the agronomy desk.

    Each record shows what was asked for — booking prepay, raising a credit ceiling, returning
    product, scheduling a delivery, or enrolling in a programme — with the money or limit named,
    the date asked for, whether the member has signed it, when the desk registered it, and how
    far it has progressed. Only an approved or fulfilled request has committed the cooperative.

    Args:
        order_id: The internal reference of one agronomy request; leave "" if unknown.
        customer_id: The member's internal reference number; leave "" if unknown.
        account_id: The internal reference of the crop input account the request applies to;
            leave "" if unknown.
    """
    match = {k: v for k, v in {"order_id": order_id, "customer_id": customer_id,
                               "account_id": account_id}.items() if v}
    rows = ctx.find("agronomy_orders", **match)
    return str(rows) if rows else f"No agronomy requests for {match}."


@tool(owner="agent", rw="read")
def find_patronage_memberships(ctx: ToolContext, membership_id: str = "", customer_id: str = "") -> str:
    """Retrieve a member's equity and patronage memberships.

    Each record names the membership class, the equity the cooperative holds for the member and
    how much of it has been allocated but not yet revolved, the common stock and voting rights
    the class carries, the year patronage was last allocated, the fiscal year the oldest
    unrevolved allocation becomes eligible under the revolvement cycle, the year of birth on the
    application, whether notice of death has been recorded, and how allocations are reported for
    tax.

    Args:
        membership_id: The internal reference of one equity membership; leave "" if unknown.
        customer_id: The member's internal reference number, to list every membership in their
            name; leave "" if unknown.
    """
    match = {k: v for k, v in {"membership_id": membership_id, "customer_id": customer_id}.items() if v}
    rows = ctx.find("patronage_memberships", **match)
    return str(rows) if rows else f"No equity memberships for {match}."


@tool(owner="agent", rw="read")
def find_patronage_ledger_entries(ctx: ToolContext, entry_id: str = "", membership_id: str = "",
                                  customer_id: str = "", transfer_counterparty_id: str = "") -> str:
    """Retrieve the equity ledger: qualifying business accrued, allocations declared by the
    board, cash portions paid, equity revolved back out, capital retained per unit, transfers
    between members and any later adjustment of an allocation.

    Rows carry the fiscal year, which stream of business the volume was earned on and at what
    declared rate, the amount allocated and how it split between cash and equity, the retain
    taken, the revolvement paid, the notice the allocation was reported on, the remittance
    reference and method of a payment, and the reason where an allocation was adjusted.

    Args:
        entry_id: The internal reference of one equity ledger row; leave "" if unknown.
        membership_id: The internal reference of the equity membership whose history is wanted;
            leave "" if unknown.
        customer_id: The member's internal reference number; leave "" if unknown.
        transfer_counterparty_id: The internal reference of the other member on a transfer, to
            find rows where equity moved to or from them; leave "" if unknown.
    """
    match = {k: v for k, v in {"entry_id": entry_id, "membership_id": membership_id,
                               "customer_id": customer_id,
                               "transfer_counterparty_id": transfer_counterparty_id}.items() if v}
    rows = ctx.find("patronage_ledger", **match)
    return str(rows) if rows else f"No equity ledger entries for {match}."


@tool(owner="agent", rw="read")
def find_patronage_requests(ctx: ToolContext, request_id: str = "", customer_id: str = "",
                            membership_id: str = "") -> str:
    """Retrieve the requests lodged with the equity desk by a member or their representative.

    Each record shows what was asked for — transferring equity, retiring equity on an estate or
    on age, changing where notices are mailed, or changing the tax election — with the equity
    named, the date asked, whether it carries a signature, when the desk registered it, and how
    far it has progressed. Only an approved or completed request has bound the board.

    Args:
        request_id: The internal reference of one equity request; leave "" if unknown.
        customer_id: The member's internal reference number; leave "" if unknown.
        membership_id: The internal reference of the membership the request applies to; leave ""
            if unknown.
    """
    match = {k: v for k, v in {"request_id": request_id, "customer_id": customer_id,
                               "membership_id": membership_id}.items() if v}
    rows = ctx.find("patronage_requests", **match)
    return str(rows) if rows else f"No equity requests for {match}."


@tool(owner="agent", rw="read")
def find_energy_accounts(ctx: ToolContext, energy_account_id: str = "", customer_id: str = "") -> str:
    """Retrieve a member's refined fuels and propane accounts.

    Each record names the delivery programme and the fuel it is set up for, the tank and who
    owns it, the gallons booked ahead and the price they draw at, any level monthly instalment
    agreed, the route the tank sits on, the date of the last delivery, when tank rent next falls
    due, whether the tank is on the automatic keep-full schedule, the gallons still owed out of
    a pre-buy, the balance carried, and where the account stands in its life.

    Args:
        energy_account_id: The internal reference of one energy account; leave "" if unknown.
        customer_id: The member's internal reference number, to list all of their energy
            accounts; leave "" if unknown.
    """
    match = {k: v for k, v in {"energy_account_id": energy_account_id,
                               "customer_id": customer_id}.items() if v}
    rows = ctx.find("energy_accounts", **match)
    return str(rows) if rows else f"No energy accounts for {match}."


@tool(owner="agent", rw="read")
def find_energy_deliveries(ctx: ToolContext, delivery_id: str = "", energy_account_id: str = "",
                           customer_id: str = "") -> str:
    """Retrieve energy account activity: deliveries made, contracted gallons drawn down, delivery
    and tank fees, budget instalments billed, payments posted and price-protection credits.

    Rows carry the delivery ticket the driver left, the fuel and how the stop was ordered, the
    gallons pumped with the meter readings and tank gauge before and after, the price billed,
    which fee a row carries, the invoice it was billed on, the remittance reference and method of
    a payment, and the budget month an instalment covers.

    Args:
        delivery_id: The internal reference of one energy account row; leave "" if unknown.
        energy_account_id: The internal reference of the energy account whose activity is
            wanted; leave "" if unknown.
        customer_id: The member's internal reference number; leave "" if unknown.
    """
    match = {k: v for k, v in {"delivery_id": delivery_id, "energy_account_id": energy_account_id,
                               "customer_id": customer_id}.items() if v}
    rows = ctx.find("energy_deliveries", **match)
    return str(rows) if rows else f"No energy account activity for {match}."


@tool(owner="agent", rw="read")
def find_energy_orders(ctx: ToolContext, energy_order_id: str = "", customer_id: str = "",
                       energy_account_id: str = "") -> str:
    """Retrieve the requests a member has lodged with the energy desk.

    Each record shows what was asked for — booking contract gallons, enrolling on a budget plan,
    setting or pulling a tank, calling for a delivery, or taking price protection — with the
    gallons and date named, whether the member has signed it, when the desk registered it, and
    how far it has progressed. Only a completed request has been carried out.

    Args:
        energy_order_id: The internal reference of one energy request; leave "" if unknown.
        customer_id: The member's internal reference number; leave "" if unknown.
        energy_account_id: The internal reference of the energy account the request applies to;
            leave "" if unknown.
    """
    match = {k: v for k, v in {"energy_order_id": energy_order_id, "customer_id": customer_id,
                               "energy_account_id": energy_account_id}.items() if v}
    rows = ctx.find("energy_orders", **match)
    return str(rows) if rows else f"No energy requests for {match}."


@tool(owner="agent", rw="read")
def find_custom_service_plans(ctx: ToolContext, plan_id: str = "", customer_id: str = "") -> str:
    """Retrieve a member's custom application service plans.

    Each record names the application programme, the crop year and the acres committed, the
    window in which the committed rates apply, the home field the plan is written around,
    whether a current prescription is on file, whether the licence covering restricted-use
    product has been verified, the acres worked so far, and where the plan stands in its life.

    Args:
        plan_id: The internal reference of one service plan; leave "" if unknown.
        customer_id: The member's internal reference number, to list all of their plans; leave
            "" if unknown.
    """
    match = {k: v for k, v in {"plan_id": plan_id, "customer_id": customer_id}.items() if v}
    rows = ctx.find("custom_service_plans", **match)
    return str(rows) if rows else f"No custom application plans for {match}."


@tool(owner="agent", rw="read")
def find_custom_workorders(ctx: ToolContext, workorder_id: str = "", plan_id: str = "",
                           customer_id: str = "") -> str:
    """Retrieve custom application work orders and their billing.

    Rows carry the work order number and the date worked, the operation run and the acres
    covered, the per-acre rate and the money billed, the product applied and the field it went
    on, the applicator who ran the pass, whether field conditions stopped it and why it was
    rescheduled, any surcharge carried, and the invoice it was billed on.

    Args:
        workorder_id: The internal reference of one work order row; leave "" if unknown.
        plan_id: The internal reference of the service plan whose work is wanted; leave "" if
            unknown.
        customer_id: The member's internal reference number; leave "" if unknown.
    """
    match = {k: v for k, v in {"workorder_id": workorder_id, "plan_id": plan_id,
                               "customer_id": customer_id}.items() if v}
    rows = ctx.find("custom_workorders", **match)
    return str(rows) if rows else f"No custom application work orders for {match}."


@tool(owner="agent", rw="read")
def find_feed_programs(ctx: ToolContext, program_id: str = "", customer_id: str = "") -> str:
    """Retrieve a member's feed and animal nutrition programmes.

    Each record names the feed programme, the species and head on feed, the formula code being
    run, how often the mill delivers, the bin serving the programme, the nutritionist assigned,
    whether a current veterinary feed directive is on file, the tons delivered so far, and where
    the programme stands in its life.

    Args:
        program_id: The internal reference of one feed programme; leave "" if unknown.
        customer_id: The member's internal reference number, to list all of their programmes;
            leave "" if unknown.
    """
    match = {k: v for k, v in {"program_id": program_id, "customer_id": customer_id}.items() if v}
    rows = ctx.find("feed_programs", **match)
    return str(rows) if rows else f"No feed programmes for {match}."


@tool(owner="agent", rw="read")
def find_feed_invoices(ctx: ToolContext, feed_invoice_id: str = "", program_id: str = "",
                       customer_id: str = "") -> str:
    """Retrieve feed programme activity: orders placed, loads delivered, invoices raised,
    payments posted, ration changes and credits.

    Rows carry the invoice number and date, the class of feed and the formula code run, the tons
    and price per ton, the mill delivery ticket, whether the ration carried a medicated additive
    and the veterinary feed directive it ran under, and the remittance reference and method of a
    payment.

    Args:
        feed_invoice_id: The internal reference of one feed programme row; leave "" if unknown.
        program_id: The internal reference of the feed programme whose activity is wanted; leave
            "" if unknown.
        customer_id: The member's internal reference number; leave "" if unknown.
    """
    match = {k: v for k, v in {"feed_invoice_id": feed_invoice_id, "program_id": program_id,
                               "customer_id": customer_id}.items() if v}
    rows = ctx.find("feed_invoices", **match)
    return str(rows) if rows else f"No feed programme activity for {match}."


@tool(owner="agent", rw="read")
def find_identity_verifications(ctx: ToolContext, verification_id: str = "",
                                customer_id: str = "") -> str:
    """Check whether the caller on a membership has already cleared identity on this call, and
    when that outcome was recorded.

    Args:
        verification_id: The internal reference of one identity check record; leave "" if
            unknown.
        customer_id: The member's internal reference number; leave "" if unknown.
    """
    match = {k: v for k, v in {"verification_id": verification_id,
                               "customer_id": customer_id}.items() if v}
    rows = ctx.find("identity_verifications", **match)
    return str(rows) if rows else f"No identity check on record for {match}."


@tool(owner="agent", rw="read")
def find_agent_handoffs(ctx: ToolContext, handoff_id: str = "", customer_id: str = "") -> str:
    """Check whether a member has already been passed to a human member-services representative,
    with the reason recorded and the moment it happened.

    Args:
        handoff_id: The internal reference of one handoff record; leave "" if unknown.
        customer_id: The member's internal reference number; leave "" if unknown.
    """
    match = {k: v for k, v in {"handoff_id": handoff_id, "customer_id": customer_id}.items() if v}
    rows = ctx.find("agent_handoffs", **match)
    return str(rows) if rows else f"No handoff on record for {match}."


@tool(owner="agent", rw="write")
def verify_member_identity(ctx: ToolContext, customer_id: str, member_number: str = "",
                           phone_number: str = "", email: str = "", tax_id_last4: str = "",
                           membership_since: str = "") -> str:
    """Establish that the caller is the member whose account is about to be discussed, and record
    the outcome.

    Identity must clear before anything is looked into or transacted on a member's grain,
    storage, input, equity or energy business. The comparison is made here rather than judged at
    the desk: each detail the caller offers is checked against the membership profile, and
    identity clears only when at least two of them agree with what is on file. The membership
    reference is used only to pull the right profile up and never counts as one of those
    matching details, and the member's own name is not accepted as a credential because it is
    too easily known by others. Callers seldom remember everything, so pass only what they
    actually say, exactly as they say it, and leave the rest blank. If a first attempt falls
    short and the caller then offers something further that clears the bar, the successful
    outcome stands.

    Args:
        customer_id: The member's internal reference number, taken from the membership profile
            lookup. Required and never blank; it is used only to pull up the profile and is not
            counted toward the matching details.
        member_number: The membership number the caller states, of the form M- followed by five
            digits (e.g. M-04821); leave "" if not stated.
        phone_number: The mobile number the caller states, 10 digits with no separators; leave ""
            if not stated.
        email: The email address the caller states; leave "" if not stated.
        tax_id_last4: The last four digits of the taxpayer number the caller states, exactly 4
            digits; leave "" if not stated.
        membership_since: The date the caller says the membership was accepted, as YYYY-MM-DD;
            leave "" if not stated.
    """
    if not customer_id:
        return "Error: customer_id is required; look the member up first and pass their reference."
    rows = ctx.find("customers", customer_id=customer_id)
    if not rows:
        return f"Error: no member {customer_id}; cannot verify."
    rec = rows[0]
    # The tool owns the comparison. The locator customer_id is deliberately absent from
    # `supplied` — pulling a profile up is not proof of identity.
    supplied = {"member_number": member_number, "phone_number": phone_number, "email": email,
                "tax_id_last4": tax_id_last4, "membership_since": membership_since}
    matched = sum(1 for field, value in supplied.items()
                  if value and str(rec.get(field)) == str(value))
    verified = matched >= VERIFICATION_MATCH_THRESHOLD
    rid = ctx.make_id("ver_", customer_id)
    # Store only the reproducible outcome, never the match count (which varies with whichever
    # valid subset of details a correct agent happened to collect). Upsert and never downgrade:
    # a caller who misses on a first attempt and clears on a second must end up recorded as
    # verified, which a plain idempotent create could never express.
    prior = ctx.find("identity_verifications", verification_id=rid)
    verified = verified or bool(prior and prior[0].get("verified"))
    if prior:
        ctx.update("identity_verifications", rid, verified=verified, verified_at=ctx.now())
    else:
        ctx.create("identity_verifications", rid, verification_id=rid, customer_id=customer_id,
                   verified=verified, verified_at=ctx.now())
    return (f"Identity confirmed for {customer_id} ({matched} detail(s) matched the profile)."
            if verified else
            f"Identity NOT confirmed for {customer_id} (only {matched} of the required "
            f"{VERIFICATION_MATCH_THRESHOLD} details matched). Ask the caller for another "
            "detail held on the profile and run this check again.")


@tool(owner="agent", rw="write")
def transfer_to_member_services_representative(ctx: ToolContext, customer_id: str, reason: str) -> str:
    """Pass the member to a human member-services representative and record why.

    Use it in exactly two situations. The first is when nothing in the cooperative's policies
    offers a way to resolve what the member is asking for, so no action at this desk could be
    the right one. The second is when the member has plainly asked to speak to a person at least
    twice on this call, whatever the subject.

    Args:
        customer_id: The member's internal reference number, taken from the membership profile
            lookup; the profile must exist.
        reason: Why the member is being passed on; one of POLICY_NOT_COVERED or
            CUSTOMER_REQUESTED, never free text. POLICY_NOT_COVERED — no cooperative policy
            offers a way to settle the request. CUSTOMER_REQUESTED — the member has explicitly
            asked for a human representative at least 2 times on this call.
    """
    allowed = {"POLICY_NOT_COVERED", "CUSTOMER_REQUESTED"}
    if reason not in allowed:
        return f"Error: unknown handoff reason '{reason}'. Valid: {', '.join(sorted(allowed))}."
    if not ctx.find("customers", customer_id=customer_id):
        return f"Error: no member {customer_id}; cannot record handoff."
    rid = ctx.make_id("hof_", customer_id, reason)
    ctx.create("agent_handoffs", rid, handoff_id=rid, customer_id=customer_id,
               reason=reason, created_at=ctx.now())
    return f"Handoff to a human member-services representative recorded for {customer_id} ({reason})."


@tool(owner="agent", rw="read")
def find_custom_service_requests(ctx: ToolContext, service_request_id: str = "", customer_id: str = "",
                                 plan_id: str = "") -> str:
    """Retrieve the requests a member has lodged with the custom application desk.

    Each record shows what was asked for — a pass across a field, a move to another day, a
    cancellation, a rework claim or a drift complaint — with the acres and date named, the field it
    concerns, whether the member has signed it, when the desk registered it, and how far it has
    progressed. Only a completed request has put equipment in the field.

    Args:
        service_request_id: The internal reference of one application request; leave "" if unknown.
        customer_id: The member's internal reference number; leave "" if unknown.
        plan_id: The internal reference of the service plan the request applies to; leave "" if
            unknown.
    """
    match = {k: v for k, v in {"service_request_id": service_request_id, "customer_id": customer_id,
                               "plan_id": plan_id}.items() if v}
    rows = ctx.find("custom_service_requests", **match)
    return str(rows) if rows else f"No custom application requests for {match}."


@tool(owner="agent", rw="read")
def find_feed_program_requests(ctx: ToolContext, feed_request_id: str = "", customer_id: str = "",
                               program_id: str = "") -> str:
    """Retrieve the requests a member has lodged with the feed mill.

    Each record shows what was asked for — a load of feed, a change of ration, a hold on deliveries,
    the filing of a veterinary feed directive or closing the programme — with the tons and date
    named, the formula code it concerns, whether the member has signed it, when the mill registered
    it, and how far it has progressed. Only a completed request has been run by the mill.

    Args:
        feed_request_id: The internal reference of one feed programme request; leave "" if unknown.
        customer_id: The member's internal reference number; leave "" if unknown.
        program_id: The internal reference of the feed programme the request applies to; leave "" if
            unknown.
    """
    match = {k: v for k, v in {"feed_request_id": feed_request_id, "customer_id": customer_id,
                               "program_id": program_id}.items() if v}
    rows = ctx.find("feed_program_requests", **match)
    return str(rows) if rows else f"No feed programme requests for {match}."

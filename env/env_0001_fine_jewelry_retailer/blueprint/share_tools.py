"""Shared tools for the Belrose Fine Jewelers customer care desk.

Everything defined here is always in its owner's tool list: the complete record-lookup
layer over the customer file and every product register, the identity check, and the
handover to a human representative. Customer-originated business writes are authored
per difficulty and are not placed here.
"""

from erlbench import ToolContext, tool

# Scenario operational constants. K is the number of profile details a caller must match
# before any account work is done; R is how many explicit requests for a human are treated
# as a request to hand the conversation over.
VERIFICATION_MATCH_THRESHOLD = 2
HUMAN_REQUEST_THRESHOLD = 2


@tool(owner="agent", rw="read")
def find_customers(ctx: ToolContext, customer_id: str = "", phone_number: str = "",
                   email: str = "", full_name: str = "", postal_code: str = "") -> str:
    """Look up the customer profile so you know whose account the call is about.

    Search by the customer reference number when you already have it, or by whatever the
    caller naturally says about themselves — the mobile number on file, the email address,
    the name as it appears on their identification, the postal code of their billing
    address. Every criterion is optional; give whichever you have. Spacing, capitalisation
    and stray punctuation are ignored in the comparison, so a number read aloud still
    matches. The profile that comes back carries the contact details, the last four digits
    of the identification on file, the date of birth, the date the profile was first
    opened, the customer's home store and their contact preference. Finding a profile is
    not the same as proving the caller is that person; identity is checked separately
    before any account work is done.

    Args:
        customer_id: The customer reference number; leave "" if you do not have it yet.
        phone_number: The mobile number on file, 10 digits with no punctuation, e.g. 4155550143; leave "" if not stated.
        email: The email address on file, exactly as the caller gives it; leave "" if not stated.
        full_name: The customer's full name as it appears on their identification; leave "" if not stated.
        postal_code: The 5-digit postal code of the billing address, e.g. 94110; leave "" if not stated.
    """
    match = {k: v for k, v in {"customer_id": customer_id, "phone_number": phone_number,
                               "email": email, "full_name": full_name,
                               "postal_code": postal_code}.items() if v}
    if not match:
        return "Error: provide at least one reference number or profile detail to find the customer."
    rows = ctx.fuzzy_find("customers", **match)
    if not rows:
        return f"No customer matches {match}."
    if len(rows) > 1:
        return f"Error: {len(rows)} customers match {match}; ask for one more detail to tell them apart."
    return str(rows[0])


@tool(owner="agent", rw="write")
def verify_customer_identity(ctx: ToolContext, customer_id: str, phone_number: str = "",
                             email: str = "", postal_code: str = "", date_of_birth: str = "",
                             identification_last_four: str = "", member_since: str = "",
                             mailing_address: str = "") -> str:
    """Check the caller against the profile on file and record the outcome of that check.

    This tool does the comparing itself. Pass the details the caller actually states, each
    exactly as they give it, and leave the rest blank; the tool measures each one against
    the profile and passes the caller only when at least two of them agree. The customer
    reference number is how the profile is fetched and is never counted as one of those
    agreeing details. Callers usually remember only some of what is on file, so a first
    attempt that falls short is not final: ask for one more detail and call again, and the
    later pass is what stands. Identity must be cleared before any money is moved, any
    agreement is changed and any record of the customer's is written.

    Args:
        customer_id: The customer reference number read from the customer profile lookup. Required; used only to fetch that profile.
        phone_number: The mobile number the caller gives, 10 digits with no punctuation, e.g. 4155550143; leave "" if not stated.
        email: The email address the caller gives, verbatim; leave "" if not stated.
        postal_code: The 5-digit postal code the caller gives for their billing address; leave "" if not stated.
        date_of_birth: The date of birth the caller gives, as YYYY-MM-DD; leave "" if not stated.
        identification_last_four: The last four digits of the identification the caller gives, e.g. 4417; leave "" if not stated.
        member_since: The date the caller says their profile was opened, as YYYY-MM-DD; leave "" if not stated.
        mailing_address: The single-line mailing address the caller gives, verbatim; leave "" if not stated.
    """
    if not customer_id:
        return "Error: customer_id is required; look the customer up first and pass their reference number."
    rows = ctx.find("customers", customer_id=customer_id)
    if not rows:
        return f"Error: no customer {customer_id}; cannot run the identity check."
    rec = rows[0]
    # The locator is deliberately absent from `supplied`: fetching a row proves nothing.
    supplied = {"phone_number": phone_number, "email": email, "postal_code": postal_code,
                "date_of_birth": date_of_birth, "identification_last_four": identification_last_four,
                "member_since": member_since, "mailing_address": mailing_address}
    matched = sum(1 for field, value in supplied.items() if value and str(rec.get(field)) == str(value))
    verified = matched >= VERIFICATION_MATCH_THRESHOLD
    rid = ctx.make_id("ver_", customer_id)
    # Store only the reproducible outcome, and never downgrade a pass that already stands.
    prior = ctx.find("identity_verifications", verification_id=rid)
    verified = verified or bool(prior and prior[0].get("verified"))
    if prior:
        ctx.update("identity_verifications", rid, verified=verified, verified_at=ctx.now())
    else:
        ctx.create("identity_verifications", rid, verification_id=rid, customer_id=customer_id,
                   verified=verified, verified_at=ctx.now())
    return (f"Identity confirmed for {customer_id} ({matched} detail(s) agreed with the profile)."
            if verified else
            f"Identity not confirmed for {customer_id} (only {matched} of the required "
            f"{VERIFICATION_MATCH_THRESHOLD} details agreed). Ask the caller for another detail on file and check again.")


@tool(owner="agent", rw="write")
def transfer_to_human_agent(ctx: ToolContext, customer_id: str, reason: str) -> str:
    """Pass the conversation to a human representative and record why it was passed on.

    Two situations call for this. The first is a request the published policy simply does
    not decide, so that no correct answer can be worked out from the rules and the records
    — that is POLICY_NOT_COVERED. The second is a caller who has asked to speak to a person
    twice or more in the same conversation, whatever the subject — that is
    CUSTOMER_REQUESTED. Nothing else belongs here.

    Args:
        customer_id: The customer reference number read from the customer profile lookup; the profile must exist.
        reason: One of POLICY_NOT_COVERED or CUSTOMER_REQUESTED, never free text.
            POLICY_NOT_COVERED — no published rule can resolve what the caller is asking for;
            CUSTOMER_REQUESTED — the caller has explicitly asked for a human representative at least 2 times.
    """
    allowed = {"POLICY_NOT_COVERED", "CUSTOMER_REQUESTED"}
    if reason not in allowed:
        return f"Error: unknown handover reason '{reason}'. Valid: {', '.join(sorted(allowed))}."
    if not ctx.find("customers", customer_id=customer_id):
        return f"Error: no customer {customer_id}; cannot record the handover."
    rid = ctx.make_id("hof_", customer_id, reason)
    ctx.create("agent_handoffs", rid, handoff_id=rid, customer_id=customer_id,
               reason=reason, created_at=ctx.now())
    return f"Conversation passed to a human representative for {customer_id} ({reason})."


@tool(owner="agent", rw="read")
def find_financing_plans(ctx: ToolContext, financing_plan_id: str = "", customer_id: str = "") -> str:
    """Retrieve the promotional financing plans a customer holds.

    Each plan record shows the promotional term it was written on, where it stands in its
    life from application through billing to settlement or write-off, the sale it finances,
    what was originally financed and what is still owed, the held-back interest, the
    scheduled payment and statement day, whether automatic payment is running, and the key
    dates: when the application was taken, when it was approved, when billing began, when
    the promotional term ends and when the plan closed. Pass the plan reference number for
    one plan, or the customer reference number for everything they hold; give both to
    narrow to one plan of one customer.

    Args:
        financing_plan_id: The reference number of the financing plan record itself; leave "" if unknown.
        customer_id: The reference number of the customer whose plans you want; leave "" if unknown.
    """
    match = {k: v for k, v in {"financing_plan_id": financing_plan_id,
                               "customer_id": customer_id}.items() if v}
    rows = ctx.find("financing_plans", **match)
    return str(rows) if rows else f"No financing plan records for {match}."


@tool(owner="agent", rw="read")
def find_financing_ledger(ctx: ToolContext, ledger_entry_id: str = "", financing_plan_id: str = "",
                          customer_id: str = "", source_entry_id: str = "") -> str:
    """Read the billing history of a promotional financing plan.

    Every movement on a plan is here in the order it was booked: the merchandise financed,
    payments and how they cleared, late fees and returned-payment fees, held-back interest
    accruing and being either billed or given back, merchandise return credits, amounts
    given back, and the statements themselves with their due dates. Each entry carries its
    posting date, its billing cycle, its signed amount, and — where it answers an earlier
    entry such as a fee being given back or a return crediting a purchase — the reference
    of that earlier entry. Ask by the entry reference, by the plan, by the customer, or by
    the earlier entry an answering entry points back to.

    Args:
        ledger_entry_id: The reference number of one billing entry; leave "" if unknown.
        financing_plan_id: The reference number of the financing plan whose history you want; leave "" if unknown.
        customer_id: The reference number of the customer whose billing entries you want; leave "" if unknown.
        source_entry_id: The reference number of an earlier entry, to find the entries that answer it; leave "" if unknown.
    """
    match = {k: v for k, v in {"ledger_entry_id": ledger_entry_id,
                               "financing_plan_id": financing_plan_id,
                               "customer_id": customer_id,
                               "source_entry_id": source_entry_id}.items() if v}
    rows = ctx.find("financing_ledger", **match)
    return str(rows) if rows else f"No financing billing entries for {match}."


@tool(owner="agent", rw="read")
def find_financing_intake(ctx: ToolContext, financing_request_id: str = "", customer_id: str = "",
                          financing_plan_id: str = "") -> str:
    """Retrieve the requests a customer has raised with the finance desk.

    These are the arrangements that are taken down first and only take effect once the
    customer confirms them: enrolling in a hardship schedule, changing automatic payment,
    asking for a payoff figure, moving a purchase to a different promotional term, and
    unwinding an application inside its cooling-off window. Each record shows what was
    asked for, how much it concerns, the date it was asked to take effect, whether it is
    still only recorded or has been confirmed, withdrawn or carried out, and the moment it
    was taken.

    Args:
        financing_request_id: The reference number of one finance desk request; leave "" if unknown.
        customer_id: The reference number of the customer whose requests you want; leave "" if unknown.
        financing_plan_id: The reference number of the financing plan the requests concern; leave "" if unknown.
    """
    match = {k: v for k, v in {"financing_request_id": financing_request_id,
                               "customer_id": customer_id,
                               "financing_plan_id": financing_plan_id}.items() if v}
    rows = ctx.find("financing_intake", **match)
    return str(rows) if rows else f"No finance desk requests for {match}."


@tool(owner="agent", rw="read")
def find_protection_plans(ctx: ToolContext, protection_plan_id: str = "", customer_id: str = "") -> str:
    """Retrieve the protection and care coverage a customer holds.

    One record covers one piece. It names the coverage, the piece and how it was described
    on the receipt, what the piece sold for, and where the coverage stands — quoted, in
    force, out of good standing for a missed inspection, suspended, exhausted, expired,
    cancelled or transferred away. It also carries the premium and what has been paid
    toward it, the benefit allowance still available, the deductible per accepted claim,
    the date of the last inspection and the date the next one falls due, the store that
    inspects it, how many claims have been settled, and the dates coverage began and ends.

    Args:
        protection_plan_id: The reference number of the coverage record itself; leave "" if unknown.
        customer_id: The reference number of the customer whose coverage you want; leave "" if unknown.
    """
    match = {k: v for k, v in {"protection_plan_id": protection_plan_id,
                               "customer_id": customer_id}.items() if v}
    rows = ctx.find("protection_plans", **match)
    return str(rows) if rows else f"No protection coverage records for {match}."


@tool(owner="agent", rw="read")
def find_protection_ledger(ctx: ToolContext, protection_entry_id: str = "", protection_plan_id: str = "",
                           customer_id: str = "", source_entry_id: str = "") -> str:
    """Read what has happened under a piece of protection coverage.

    Premiums received and refunded, the benefit allowance granted at the start and
    reinstated on each anniversary, claims as they were filed, what was settled against
    them and what was refused and on which single ground, and every inspection with the
    store that carried it out and what it found. Claim entries carry the claim reference
    that ties a filing, a settlement and a refusal together, the deductible the customer
    paid, and the bench work order where the piece went to the workshop.

    Args:
        protection_entry_id: The reference number of one coverage entry; leave "" if unknown.
        protection_plan_id: The reference number of the coverage whose history you want; leave "" if unknown.
        customer_id: The reference number of the customer whose coverage entries you want; leave "" if unknown.
        source_entry_id: The reference number of an earlier entry, to find the entries that answer it; leave "" if unknown.
    """
    match = {k: v for k, v in {"protection_entry_id": protection_entry_id,
                               "protection_plan_id": protection_plan_id,
                               "customer_id": customer_id,
                               "source_entry_id": source_entry_id}.items() if v}
    rows = ctx.find("protection_ledger", **match)
    return str(rows) if rows else f"No protection coverage entries for {match}."


@tool(owner="agent", rw="read")
def find_protection_intake(ctx: ToolContext, protection_request_id: str = "", customer_id: str = "",
                           protection_plan_id: str = "") -> str:
    """Retrieve the requests a customer has raised with the protection desk.

    Claims being taken down before they are decided, cancellations, transfers of coverage
    to a new owner, inspection bookings and renewals all appear here. Each record shows
    what was asked for, the claim it concerns where it concerns one, the date it is to take
    effect from, whether the customer has confirmed it yet, and when it was taken.

    Args:
        protection_request_id: The reference number of one protection desk request; leave "" if unknown.
        customer_id: The reference number of the customer whose requests you want; leave "" if unknown.
        protection_plan_id: The reference number of the coverage the requests concern; leave "" if unknown.
    """
    match = {k: v for k, v in {"protection_request_id": protection_request_id,
                               "customer_id": customer_id,
                               "protection_plan_id": protection_plan_id}.items() if v}
    rows = ctx.find("protection_intake", **match)
    return str(rows) if rows else f"No protection desk requests for {match}."


@tool(owner="agent", rw="read")
def find_service_orders(ctx: ToolContext, service_order_id: str = "", customer_id: str = "") -> str:
    """Retrieve the bench work orders a customer has at the workshop.

    A work order follows one piece from the counter to the bench and back: the service
    level it runs at, the piece and the metal it was confirmed to be in, the store that
    took it in, the value it was taken in at, whether a rush was asked for, the sizes a
    resizing runs between, and where it stands — taken in, priced, waiting on the
    customer's authorisation, at the bench, ready to collect, handed back, returned
    unrepaired, cancelled or abandoned. It also shows the estimate, the ceiling the
    customer authorised, what is still owed, the protection claim the work runs under, the
    date the piece was promised for, how long the chain stands behind its workmanship and
    how many times the piece has been back.

    Args:
        service_order_id: The reference number of the work order record itself; leave "" if unknown.
        customer_id: The reference number of the customer whose work orders you want; leave "" if unknown.
    """
    match = {k: v for k, v in {"service_order_id": service_order_id,
                               "customer_id": customer_id}.items() if v}
    rows = ctx.find("service_orders", **match)
    return str(rows) if rows else f"No workshop work order records for {match}."


@tool(owner="agent", rw="read")
def find_service_ledger(ctx: ToolContext, service_entry_id: str = "", service_order_id: str = "",
                        customer_id: str = "", source_entry_id: str = "") -> str:
    """Read the priced lines and payments on a bench work order.

    Labour by task, parts fitted, the surcharge for expedited handling, insured shipping,
    payments taken at the counter, amounts a protection claim answered for, amounts taken
    off as goodwill or under a member benefit, and the final checks with what they found
    and which jeweler carried them out. Every priced line names the task and the unit price
    it was built from; every credit points back to the priced line it was taken off.

    Args:
        service_entry_id: The reference number of one work order entry; leave "" if unknown.
        service_order_id: The reference number of the work order whose entries you want; leave "" if unknown.
        customer_id: The reference number of the customer whose work order entries you want; leave "" if unknown.
        source_entry_id: The reference number of a priced line, to find the credits taken off it; leave "" if unknown.
    """
    match = {k: v for k, v in {"service_entry_id": service_entry_id,
                               "service_order_id": service_order_id,
                               "customer_id": customer_id,
                               "source_entry_id": source_entry_id}.items() if v}
    rows = ctx.find("service_ledger", **match)
    return str(rows) if rows else f"No workshop work order entries for {match}."


@tool(owner="agent", rw="read")
def find_service_intake(ctx: ToolContext, service_request_id: str = "", customer_id: str = "",
                        service_order_id: str = "") -> str:
    """Retrieve the requests a customer has raised with the workshop desk.

    The customer's authorisation of an estimate and the ceiling they agreed to, requests to
    move a piece onto expedited handling, arrangements for collection, the release the
    chain needs before it works on stones it did not supply, and cancellations. Each record
    shows what was asked, the amount it carries, the date it is to take effect from,
    whether the customer has confirmed it, and when it was taken down.

    Args:
        service_request_id: The reference number of one workshop desk request; leave "" if unknown.
        customer_id: The reference number of the customer whose requests you want; leave "" if unknown.
        service_order_id: The reference number of the work order the requests concern; leave "" if unknown.
    """
    match = {k: v for k, v in {"service_request_id": service_request_id,
                               "customer_id": customer_id,
                               "service_order_id": service_order_id}.items() if v}
    rows = ctx.find("service_intake", **match)
    return str(rows) if rows else f"No workshop desk requests for {match}."


@tool(owner="agent", rw="read")
def find_custom_orders(ctx: ToolContext, custom_order_id: str = "", customer_id: str = "") -> str:
    """Retrieve the custom commissions a customer has placed with the design studio.

    A commission record holds the brief in the customer's own words, the programme it runs
    under, the designer carrying it, where the centre stone comes from and what it weighs,
    the metal settled on, and the stage the commission has reached — consultation, waiting
    on the customer's approval of a design, waiting on the deposit, in production, held up,
    waiting on the balance, ready to hand over, delivered or cancelled. It also carries the
    quoted total, the deposit, what is still owed, how many design revisions are left, the
    metal price the quote was built on, and the dates from the consultation through
    approval and production to delivery.

    Args:
        custom_order_id: The reference number of the commission record itself; leave "" if unknown.
        customer_id: The reference number of the customer whose commissions you want; leave "" if unknown.
    """
    match = {k: v for k, v in {"custom_order_id": custom_order_id,
                               "customer_id": customer_id}.items() if v}
    rows = ctx.find("custom_orders", **match)
    return str(rows) if rows else f"No custom commission records for {match}."


@tool(owner="agent", rw="read")
def find_custom_ledger(ctx: ToolContext, custom_entry_id: str = "", custom_order_id: str = "",
                       customer_id: str = "", source_entry_id: str = "") -> str:
    """Read the money and the milestones on a custom commission.

    The quote as it was booked, agreed changes to the specification and what each was
    priced at, repricings for a movement in the metal market or for expedited production,
    the deposit and the staged payments, refunds, the included design revisions as they
    were granted and drawn one by one, and each stage of production as the piece passed
    through it. Change entries carry the change order reference they price; revision
    entries carry the number of the revision; refunds point back to the payment they
    return.

    Args:
        custom_entry_id: The reference number of one commission entry; leave "" if unknown.
        custom_order_id: The reference number of the commission whose entries you want; leave "" if unknown.
        customer_id: The reference number of the customer whose commission entries you want; leave "" if unknown.
        source_entry_id: The reference number of an earlier entry, to find the entries that answer it; leave "" if unknown.
    """
    match = {k: v for k, v in {"custom_entry_id": custom_entry_id,
                               "custom_order_id": custom_order_id,
                               "customer_id": customer_id,
                               "source_entry_id": source_entry_id}.items() if v}
    rows = ctx.find("custom_ledger", **match)
    return str(rows) if rows else f"No custom commission entries for {match}."


@tool(owner="agent", rw="read")
def find_custom_intake(ctx: ToolContext, custom_request_id: str = "", customer_id: str = "",
                       custom_order_id: str = "") -> str:
    """Retrieve the requests a customer has raised with the design studio.

    Approvals of a design, changes to an agreed specification, cancellations, requests to
    expedite production, and the release the studio needs before it works with a stone the
    customer supplied. Each record names the change order it concerns where there is one,
    the revised total put to the customer, the date it is to take effect from, whether the
    customer has confirmed it, and when it was taken down.

    Args:
        custom_request_id: The reference number of one design studio request; leave "" if unknown.
        customer_id: The reference number of the customer whose requests you want; leave "" if unknown.
        custom_order_id: The reference number of the commission the requests concern; leave "" if unknown.
    """
    match = {k: v for k, v in {"custom_request_id": custom_request_id,
                               "customer_id": customer_id,
                               "custom_order_id": custom_order_id}.items() if v}
    rows = ctx.find("custom_intake", **match)
    return str(rows) if rows else f"No design studio requests for {match}."


@tool(owner="agent", rw="read")
def find_tradein_credits(ctx: ToolContext, tradein_credit_id: str = "", customer_id: str = "") -> str:
    """Retrieve the trade-in registrations and upgrade credits a customer holds.

    Each registration covers one piece traded in: the upgrade programme it runs under, the
    piece as the customer described it and what its principal stone weighs, the laboratory
    certificate presented for it, the original sale it came from and what it sold for then,
    and where the registration stands — registered, waiting on a valuation, credit issued,
    part spent, fully spent, expired or revoked. It also carries the appraised value, the
    credit issued and what is still available to spend, the condition grade the piece was
    found at, the least the customer must spend for the credit to be usable, and the dates
    it was registered, issued and closed.

    Args:
        tradein_credit_id: The reference number of the registration record itself; leave "" if unknown.
        customer_id: The reference number of the customer whose registrations you want; leave "" if unknown.
    """
    match = {k: v for k, v in {"tradein_credit_id": tradein_credit_id,
                               "customer_id": customer_id}.items() if v}
    rows = ctx.find("tradein_credits", **match)
    return str(rows) if rows else f"No trade-in registration records for {match}."


@tool(owner="agent", rw="read")
def find_tradein_ledger(ctx: ToolContext, tradein_entry_id: str = "", tradein_credit_id: str = "",
                        customer_id: str = "", source_entry_id: str = "") -> str:
    """Read what has happened to an upgrade credit.

    The credit as it was booked and on which basis, any later revaluation upward, each
    spend against a new piece with the till transaction and the merchandise line it was
    spent on, credit taken away and on which ground, the appraiser's valuations, and the
    condition inspections with the grade the piece was found at. Every valuation names the
    appraiser and the certificate it rests on.

    Args:
        tradein_entry_id: The reference number of one trade-in entry; leave "" if unknown.
        tradein_credit_id: The reference number of the registration whose entries you want; leave "" if unknown.
        customer_id: The reference number of the customer whose trade-in entries you want; leave "" if unknown.
        source_entry_id: The reference number of an earlier entry, to find the entries that answer it; leave "" if unknown.
    """
    match = {k: v for k, v in {"tradein_entry_id": tradein_entry_id,
                               "tradein_credit_id": tradein_credit_id,
                               "customer_id": customer_id,
                               "source_entry_id": source_entry_id}.items() if v}
    rows = ctx.find("tradein_ledger", **match)
    return str(rows) if rows else f"No trade-in entries for {match}."


@tool(owner="agent", rw="read")
def find_tradein_intake(ctx: ToolContext, tradein_request_id: str = "", customer_id: str = "",
                        tradein_credit_id: str = "") -> str:
    """Retrieve the requests a customer has raised with the upgrade desk.

    Bookings for a valuation, requests to spend a credit against a particular sale,
    withdrawals of a traded piece, certificates submitted after the event, and requests to
    extend a credit that is about to expire. Each record shows the amount it concerns, the
    date it is to take effect from, whether the customer has confirmed it, and when it was
    taken down.

    Args:
        tradein_request_id: The reference number of one upgrade desk request; leave "" if unknown.
        customer_id: The reference number of the customer whose requests you want; leave "" if unknown.
        tradein_credit_id: The reference number of the registration the requests concern; leave "" if unknown.
    """
    match = {k: v for k, v in {"tradein_request_id": tradein_request_id,
                               "customer_id": customer_id,
                               "tradein_credit_id": tradein_credit_id}.items() if v}
    rows = ctx.find("tradein_intake", **match)
    return str(rows) if rows else f"No upgrade desk requests for {match}."


@tool(owner="agent", rw="read")
def find_appraisal_orders(ctx: ToolContext, appraisal_order_id: str = "", customer_id: str = "") -> str:
    """Retrieve the appraisal engagements a customer has with the gemological desk.

    Each engagement names the appraisal service, the piece or pieces it covers and how many
    there are, the purpose the value is to be stated for, the appraiser carrying it, and
    where it stands — asked for, piece received, under examination, report drafted, signed,
    handed back, expired or cancelled. It also carries the value the report states, the fee
    quoted and what is still owed, the date the report was signed, the date it stops being
    treated as current, whether a rush was asked for, the outside laboratory used, and the
    value the piece was taken in at.

    Args:
        appraisal_order_id: The reference number of the engagement record itself; leave "" if unknown.
        customer_id: The reference number of the customer whose engagements you want; leave "" if unknown.
    """
    match = {k: v for k, v in {"appraisal_order_id": appraisal_order_id,
                               "customer_id": customer_id}.items() if v}
    rows = ctx.find("appraisal_orders", **match)
    return str(rows) if rows else f"No appraisal engagement records for {match}."


@tool(owner="agent", rw="read")
def find_appraisal_ledger(ctx: ToolContext, appraisal_entry_id: str = "", appraisal_order_id: str = "",
                          customer_id: str = "", source_entry_id: str = "") -> str:
    """Read the fees and the valuations on an appraisal engagement.

    The base fee and the per-item fees, the surcharge for expediting the report, an outside
    laboratory's fee where it was passed on, payments taken, fees given back and on which
    ground, and the value recorded for each piece with the approach it was arrived at and
    the laboratory whose grading it rests on.

    Args:
        appraisal_entry_id: The reference number of one appraisal entry; leave "" if unknown.
        appraisal_order_id: The reference number of the engagement whose entries you want; leave "" if unknown.
        customer_id: The reference number of the customer whose appraisal entries you want; leave "" if unknown.
        source_entry_id: The reference number of a fee line, to find the credits taken off it; leave "" if unknown.
    """
    match = {k: v for k, v in {"appraisal_entry_id": appraisal_entry_id,
                               "appraisal_order_id": appraisal_order_id,
                               "customer_id": customer_id,
                               "source_entry_id": source_entry_id}.items() if v}
    rows = ctx.find("appraisal_ledger", **match)
    return str(rows) if rows else f"No appraisal entries for {match}."


@tool(owner="agent", rw="read")
def find_circle_memberships(ctx: ToolContext, circle_membership_id: str = "", customer_id: str = "") -> str:
    """Retrieve a customer's membership of the Belrose Circle programme.

    The record shows the tier held and the membership number quoted at the till, where the
    membership stands — joined, earning, up for its annual review, lapsed, suspended or
    closed — the points balance, the qualifying spend since the current tier took effect
    and over the whole life of the membership, the date the tier took effect and the date
    it is next reviewed, the referral code, the store benefits default to, whether a named
    concierge looks after the member, and the month their anniversary benefits fall in.

    Args:
        circle_membership_id: The reference number of the membership record itself; leave "" if unknown.
        customer_id: The reference number of the customer whose membership you want; leave "" if unknown.
    """
    match = {k: v for k, v in {"circle_membership_id": circle_membership_id,
                               "customer_id": customer_id}.items() if v}
    rows = ctx.find("circle_memberships", **match)
    return str(rows) if rows else f"No membership records for {match}."


@tool(owner="agent", rw="read")
def find_circle_ledger(ctx: ToolContext, circle_entry_id: str = "", circle_membership_id: str = "",
                       customer_id: str = "", source_entry_id: str = "") -> str:
    """Read a member's points history.

    Points earned on each qualifying sale with the spend and the multiplier behind them,
    bonuses for joining, for a birthday, for an anniversary and for referrals, points taken
    back when merchandise was returned, points spent and what they were spent against,
    points that fell away and why, and the member benefits used that cost no points at all.
    A reversal points back to the earning entry it answers.

    Args:
        circle_entry_id: The reference number of one points entry; leave "" if unknown.
        circle_membership_id: The reference number of the membership whose history you want; leave "" if unknown.
        customer_id: The reference number of the customer whose points entries you want; leave "" if unknown.
        source_entry_id: The reference number of an earning entry, to find the reversals that answer it; leave "" if unknown.
    """
    match = {k: v for k, v in {"circle_entry_id": circle_entry_id,
                               "circle_membership_id": circle_membership_id,
                               "customer_id": customer_id,
                               "source_entry_id": source_entry_id}.items() if v}
    rows = ctx.find("circle_ledger", **match)
    return str(rows) if rows else f"No points entries for {match}."


@tool(owner="agent", rw="read")
def find_layaway_agreements(ctx: ToolContext, layaway_agreement_id: str = "", customer_id: str = "") -> str:
    """Retrieve the layaway agreements a customer holds.

    Each agreement names the layaway plan, the piece being held and the store holding it,
    the merchandise price, the deposit put down and what is still owed, how many pieces are
    set aside, how often a payment falls due and what each one asks for, how far past due
    anything is, the fee charged for holding the merchandise, the gift registry it belongs
    to where it belongs to one, and where the agreement stands — opened, current,
    delinquent, paused, completed, forfeited or cancelled — together with the dates it was
    opened, the first payment fell due, it must be paid up by and it closed.

    Args:
        layaway_agreement_id: The reference number of the agreement record itself; leave "" if unknown.
        customer_id: The reference number of the customer whose agreements you want; leave "" if unknown.
    """
    match = {k: v for k, v in {"layaway_agreement_id": layaway_agreement_id,
                               "customer_id": customer_id}.items() if v}
    rows = ctx.find("layaway_agreements", **match)
    return str(rows) if rows else f"No layaway agreement records for {match}."


@tool(owner="agent", rw="read")
def find_layaway_ledger(ctx: ToolContext, layaway_entry_id: str = "", layaway_agreement_id: str = "",
                        customer_id: str = "", source_entry_id: str = "") -> str:
    """Read the payments, charges and stockroom movements on a layaway agreement.

    The merchandise as it was booked, the fee for holding it, late fees against the
    scheduled payment they answer, payments as they were credited and on which channel,
    refunds and the ground they were paid on, each piece as it was set aside and as it left
    the stockroom, and the statements with the next payment date printed on them.

    Args:
        layaway_entry_id: The reference number of one layaway entry; leave "" if unknown.
        layaway_agreement_id: The reference number of the agreement whose entries you want; leave "" if unknown.
        customer_id: The reference number of the customer whose layaway entries you want; leave "" if unknown.
        source_entry_id: The reference number of a payment entry, to find the refunds that answer it; leave "" if unknown.
    """
    match = {k: v for k, v in {"layaway_entry_id": layaway_entry_id,
                               "layaway_agreement_id": layaway_agreement_id,
                               "customer_id": customer_id,
                               "source_entry_id": source_entry_id}.items() if v}
    rows = ctx.find("layaway_ledger", **match)
    return str(rows) if rows else f"No layaway entries for {match}."


@tool(owner="agent", rw="read")
def find_layaway_intake(ctx: ToolContext, layaway_request_id: str = "", customer_id: str = "",
                        layaway_agreement_id: str = "") -> str:
    """Retrieve the requests a customer has raised with the layaway desk.

    Cancellations, changes to a payment schedule, swapping the held piece for another,
    extending the term, and arrangements to collect. Each record shows the amount it
    carries, the date it is to take effect from, whether the customer has confirmed it, and
    when it was taken down.

    Args:
        layaway_request_id: The reference number of one layaway desk request; leave "" if unknown.
        customer_id: The reference number of the customer whose requests you want; leave "" if unknown.
        layaway_agreement_id: The reference number of the agreement the requests concern; leave "" if unknown.
    """
    match = {k: v for k, v in {"layaway_request_id": layaway_request_id,
                               "customer_id": customer_id,
                               "layaway_agreement_id": layaway_agreement_id}.items() if v}
    rows = ctx.find("layaway_intake", **match)
    return str(rows) if rows else f"No layaway desk requests for {match}."


@tool(owner="agent", rw="read")
def find_identity_verifications(ctx: ToolContext, verification_id: str = "", customer_id: str = "") -> str:
    """Check whether a caller has already cleared the identity check in this conversation.

    One record is kept per customer and shows whether the check has been passed and the
    moment of the most recent attempt. A pass, once recorded, stands for the rest of the
    conversation.

    Args:
        verification_id: The reference number of the identity check record itself; leave "" if unknown.
        customer_id: The reference number of the customer whose identity check you want; leave "" if unknown.
    """
    match = {k: v for k, v in {"verification_id": verification_id,
                               "customer_id": customer_id}.items() if v}
    rows = ctx.find("identity_verifications", **match)
    return str(rows) if rows else f"No identity check records for {match}."


@tool(owner="agent", rw="read")
def find_agent_handoffs(ctx: ToolContext, handoff_id: str = "", customer_id: str = "") -> str:
    """Retrieve the occasions this customer has been passed to a human representative.

    Each record shows the ground it was passed on — either that no published rule decided
    the request, or that the caller asked for a person — and the moment it was recorded.

    Args:
        handoff_id: The reference number of the handover record itself; leave "" if unknown.
        customer_id: The reference number of the customer whose handovers you want; leave "" if unknown.
    """
    match = {k: v for k, v in {"handoff_id": handoff_id, "customer_id": customer_id}.items() if v}
    rows = ctx.find("agent_handoffs", **match)
    return str(rows) if rows else f"No handover records for {match}."

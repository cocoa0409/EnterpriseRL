"""Shared tools for env_0020_national_network_airline (Crestline Airways reservations and Summit loyalty desk).

Every tool here is a SHARE tool: always present in its owner's tool list.
This module holds only the three foundations every difficulty reuses:
  - one record finder per table (the customers finder doubles as the identity entry),
  - the identity-verification write (the tool compares; it passes at 2 matching credentials),
  - the transfer-to-human write (exactly two reasons; a customer request counts after 2 explicit asks).
Customer-originated writes are hidden task tools authored per difficulty, never here.
"""

from erlbench import ToolContext, tool


def _crit(criteria: dict) -> dict:
    # Keep only the reference numbers actually supplied (exact match on ids read from records).
    return {k: v for k, v in criteria.items() if v}


def _norm(value) -> str:
    # Compare caller-stated credentials after normalisation (case-folded letters and digits only),
    # so punctuation or spacing in a phone number or date never decides a match.
    return "".join(ch for ch in str(value or "").casefold() if ch.isalnum())


def _report(rows: list, label: str) -> str:
    # Shared rendering of every finder's result.
    if not rows:
        return f"No {label} found for the reference numbers given."
    return str(rows)


# --------------------------------------------------------------------------- customers
@tool(owner="agent", rw="read")
def find_customers(ctx: ToolContext, customer_id: str = "", name: str = "", phone_number: str = "",
                   email: str = "") -> str:
    """Look up a Crestline customer profile to establish whose account this conversation is about.

    Search by the customer reference number, or by what the caller can tell you: the registered
    phone number, the registered email address or the full name on the profile. Every criterion is
    optional; supply whichever you have. The profile returned shows whether it belongs to an
    individual traveler or to a company, the name, contact details, date of birth, billing ZIP code
    and the date the profile was opened. When several profiles match, you are asked for one more
    detail. Finding a profile does not verify the caller's identity.

    Args:
        customer_id: Customer reference number, if already known; leave "" otherwise.
        name: Full name exactly as the caller states it (individual or registered company name); leave "" if not given.
        phone_number: Registered phone number, 10 digits, as the caller states it; leave "" if not given.
        email: Registered email address as the caller states it; leave "" if not given.
    """
    match = {k: v for k, v in {"customer_id": customer_id, "name": name,
                               "phone_number": phone_number, "email": email}.items() if v}
    if not match:
        return "Error: provide at least one of customer_id, name, phone_number or email."
    rows = ctx.fuzzy_find("customers", **match)
    if not rows:
        return f"No customer matches {match}."
    if len(rows) > 1:
        return f"Error: {len(rows)} customers match {match}; ask the caller for one more detail."
    return str(rows[0])


@tool(owner="agent", rw="write")
def verify_customer_identity(ctx: ToolContext, customer_id: str, phone_number: str = "", email: str = "",
                             date_of_birth: str = "", postal_code: str = "") -> str:
    """Verify the caller's identity against the customer profile and record the outcome.

    Identity must be verified before any account detail is discussed or any booking, credit,
    mileage, certificate or agreement is changed. This tool performs the comparison itself: it
    checks each detail the caller states against the profile, counts the matches and passes only
    when at least 2 details match. The customer reference number only selects the profile and never
    counts as a match, and a name alone is not accepted as proof of identity. Callers usually know
    only some of these details, so pass exactly what the caller said and leave the rest empty. The
    result is recorded; if a first attempt fails and a later attempt with more details passes, the
    customer is recorded as verified.

    Args:
        customer_id: Customer reference number taken from the profile lookup. Required; selects the profile only.
        phone_number: Registered phone number stated by the caller, 10 digits with no punctuation; leave "" if not stated.
        email: Registered email address stated by the caller; leave "" if not stated.
        date_of_birth: Date of birth stated by the caller, formatted YYYY-MM-DD; leave "" if not stated.
        postal_code: Billing ZIP code stated by the caller, 5 digits; leave "" if not stated.
    """
    if not customer_id:
        return "Error: customer_id is required; look the customer up first."
    rows = ctx.find("customers", customer_id=customer_id)
    if not rows:
        return f"Error: no customer {customer_id}; cannot verify."
    rec = rows[0]
    # The locator is not a credential; only caller-stated attributes are compared.
    supplied = {"phone_number": phone_number, "email": email,
                "date_of_birth": date_of_birth, "postal_code": postal_code}
    matched = sum(1 for field, value in supplied.items()
                  if _norm(value) and _norm(rec.get(field)) == _norm(value))
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


@tool(owner="agent", rw="write")
def transfer_to_human_agent(ctx: ToolContext, customer_id: str, reason: str) -> str:
    """Transfer the customer to a human Crestline representative and record the reason.

    Use this in exactly two situations. POLICY_NOT_COVERED: the customer's request cannot be
    resolved under any published Crestline policy, or it lies beyond what a support agent is
    authorized to do. CUSTOMER_REQUESTED: the customer has explicitly asked to speak with a human
    representative at least 2 times in this conversation.

    Args:
        customer_id: Customer reference number taken from the profile lookup; the profile must exist.
        reason: Reason for the transfer, exactly one of POLICY_NOT_COVERED or CUSTOMER_REQUESTED; never free text.
    """
    allowed = {"POLICY_NOT_COVERED", "CUSTOMER_REQUESTED"}
    if reason not in allowed:
        return f"Error: unknown reason '{reason}'. Use one of: {', '.join(sorted(allowed))}."
    if not ctx.find("customers", customer_id=customer_id):
        return f"Error: no customer {customer_id}; cannot record the transfer."
    rid = ctx.make_id("hof_", customer_id, reason)
    ctx.create("agent_handoffs", rid, handoff_id=rid, customer_id=customer_id,
               reason=reason, created_at=ctx.now())
    return f"Transfer to a human representative recorded for {customer_id} ({reason})."


# --------------------------------------------------------------------------- tickets
@tool(owner="agent", rw="read")
def find_ticket_holdings(ctx: ToolContext, ticket_id: str = "", customer_id: str = "", membership_id: str = "",
                         corporate_account_id: str = "") -> str:
    """Look up ticket and reservation records.

    Each record is one passenger's ticket: fare brand, status, booking reference, ticket number,
    passenger name, itinerary (origin, destination, route type, next departure), booking channel,
    fare paid, form of payment, remaining unused value, and the Summit membership and corporate
    agreement it is linked to. Every criterion is optional; supply any reference number you hold.
    Returns every matching ticket, or a not-found message.

    Args:
        ticket_id: Reference number of the ticket record itself; leave "" if unknown.
        customer_id: Customer reference number of the ticket holder; leave "" if unknown.
        membership_id: Reference number of the Summit membership the ticket credits; leave "" if unknown.
        corporate_account_id: Reference number of the corporate travel agreement the ticket was booked under; leave "" if unknown.
    """
    return _report(ctx.find("ticket_holdings", **_crit({"ticket_id": ticket_id, "customer_id": customer_id,
                                            "membership_id": membership_id,
                                            "corporate_account_id": corporate_account_id})), "tickets")


@tool(owner="agent", rw="read")
def find_ticket_transactions(ctx: ToolContext, transaction_id: str = "", ticket_id: str = "", customer_id: str = "",
                             source_disruption_id: str = "") -> str:
    """Look up the fare history of tickets.

    Entries cover fare collection at ticketing, exchanges with their new itinerary and fare
    comparison, add-collects, residuals, flown coupons (segment, flight, date, cabin), conversions to
    flight credit, refunds and forfeitures, each with its date and amount. Every criterion is
    optional. Returns every matching entry, or a not-found message.

    Args:
        transaction_id: Reference number of the fare entry itself; leave "" if unknown.
        ticket_id: Reference number of the ticket; leave "" if unknown.
        customer_id: Customer reference number of the ticket holder; leave "" if unknown.
        source_disruption_id: Reference number of the disruption record an involuntary refund rests on; leave "" if unknown.
    """
    return _report(ctx.find("ticket_transactions", **_crit({"transaction_id": transaction_id, "ticket_id": ticket_id,
                                                "customer_id": customer_id,
                                                "source_disruption_id": source_disruption_id})), "fare entries")


@tool(owner="agent", rw="read")
def find_ticket_services(ctx: ToolContext, service_id: str = "", ticket_id: str = "", customer_id: str = "",
                         related_transaction_id: str = "", refunded_service_id: str = "",
                         source_disruption_id: str = "") -> str:
    """Look up service fees charged on tickets and their refunds.

    Entries cover change fees, seat purchases, checked bags (with bag tag, weight, size and travel
    direction), paid upgrades and fee refunds, each with the segment, amount and sales channel.
    Every criterion is optional. Returns every matching entry, or a not-found message.

    Args:
        service_id: Reference number of the fee entry itself; leave "" if unknown.
        ticket_id: Reference number of the ticket; leave "" if unknown.
        customer_id: Customer reference number of the ticket holder; leave "" if unknown.
        related_transaction_id: Reference number of the exchange a change fee belongs to; leave "" if unknown.
        refunded_service_id: Reference number of the fee entry a refund reverses; leave "" if unknown.
        source_disruption_id: Reference number of the disruption record a fee refund rests on; leave "" if unknown.
    """
    return _report(ctx.find("ticket_services", **_crit({"service_id": service_id, "ticket_id": ticket_id,
                                            "customer_id": customer_id,
                                            "related_transaction_id": related_transaction_id,
                                            "refunded_service_id": refunded_service_id,
                                            "source_disruption_id": source_disruption_id})), "service fees")


@tool(owner="agent", rw="read")
def find_ticket_disruptions(ctx: ToolContext, disruption_id: str = "", ticket_id: str = "", customer_id: str = "",
                            source_disruption_id: str = "") -> str:
    """Look up irregular-operations records on tickets.

    Entries cover delays, cancellations, missed connections, schedule changes, denied boarding,
    involuntary downgrades and delayed bags with their cause classification and lateness, plus the
    rebookings and compensation given for them. Every criterion is optional. Returns every matching
    entry, or a not-found message.

    Args:
        disruption_id: Reference number of the entry itself; leave "" if unknown.
        ticket_id: Reference number of the ticket affected; leave "" if unknown.
        customer_id: Customer reference number of the ticket holder; leave "" if unknown.
        source_disruption_id: Reference number of the disruption a rebooking or compensation entry rests on; leave "" if unknown.
    """
    return _report(ctx.find("ticket_disruptions", **_crit({"disruption_id": disruption_id, "ticket_id": ticket_id,
                                               "customer_id": customer_id,
                                               "source_disruption_id": source_disruption_id})),
                   "irregular-operations records")


# --------------------------------------------------------------------------- credits
@tool(owner="agent", rw="read")
def find_credit_holdings(ctx: ToolContext, credit_id: str = "", customer_id: str = "", source_ticket_id: str = "",
                         source_disruption_id: str = "", source_credit_id: str = "") -> str:
    """Look up flight credits and travel vouchers.

    Each record shows the instrument, credit number, status, traveler name, why it was issued,
    issue and expiry dates, face value, remaining value, extension and reinstatement counts, and the
    ticket, disruption or earlier credit it came from. Every criterion is optional. Returns every
    matching record, or a not-found message.

    Args:
        credit_id: Reference number of the credit record itself; leave "" if unknown.
        customer_id: Customer reference number of the holder; leave "" if unknown.
        source_ticket_id: Reference number of the ticket the credit arose from; leave "" if unknown.
        source_disruption_id: Reference number of the disruption a voucher was issued for; leave "" if unknown.
        source_credit_id: Reference number of an earlier credit whose value was returned into this one; leave "" if unknown.
    """
    return _report(ctx.find("credit_holdings", **_crit({"credit_id": credit_id, "customer_id": customer_id,
                                            "source_ticket_id": source_ticket_id,
                                            "source_disruption_id": source_disruption_id,
                                            "source_credit_id": source_credit_id})), "credits")


@tool(owner="agent", rw="read")
def find_credit_ledger(ctx: ToolContext, credit_entry_id: str = "", credit_id: str = "", customer_id: str = "",
                       reversed_entry_id: str = "", related_entry_id: str = "") -> str:
    """Look up the value history of flight credits and vouchers.

    Entries cover value loaded at issue, redemptions (ticket paid, passenger, channel), reversals,
    forfeited remainders, expiry write-offs, reinstatement restores, cash refunds and service fees.
    Every criterion is optional. Returns every matching entry, or a not-found message.

    Args:
        credit_entry_id: Reference number of the entry itself; leave "" if unknown.
        credit_id: Reference number of the credit; leave "" if unknown.
        customer_id: Customer reference number of the holder; leave "" if unknown.
        reversed_entry_id: Reference number of the entry a reversal or fee refund undoes; leave "" if unknown.
        related_entry_id: Reference number of the redemption a forfeited remainder or telephone fee follows; leave "" if unknown.
    """
    return _report(ctx.find("credit_ledger", **_crit({"credit_entry_id": credit_entry_id, "credit_id": credit_id,
                                          "customer_id": customer_id, "reversed_entry_id": reversed_entry_id,
                                          "related_entry_id": related_entry_id})), "credit entries")


# --------------------------------------------------------------------------- loyalty
@tool(owner="agent", rw="read")
def find_loyalty_holdings(ctx: ToolContext, membership_id: str = "", customer_id: str = "") -> str:
    """Look up Summit loyalty memberships.

    Each record shows the Summit number, tier and how it was obtained, tier validity, status,
    mile balance, qualifying dollars this year, upgrade certificates, last activity date and any open
    status challenge. Every criterion is optional. Returns every matching membership, or a not-found
    message.

    Args:
        membership_id: Reference number of the membership record itself; leave "" if unknown.
        customer_id: Customer reference number of the member; leave "" if unknown.
    """
    return _report(ctx.find("loyalty_holdings", **_crit({"membership_id": membership_id, "customer_id": customer_id})),
                   "Summit memberships")


@tool(owner="agent", rw="read")
def find_loyalty_activity(ctx: ToolContext, loyalty_activity_id: str = "", membership_id: str = "",
                          customer_id: str = "", source_ticket_id: str = "", reversed_activity_id: str = "") -> str:
    """Look up Summit mileage, qualifying-dollar and certificate activity.

    Entries cover flight and partner accruals, retro credits, goodwill and bonus miles, purchases,
    transfers, award redemptions and redeposits, forfeitures and reinstatements, year-end resets,
    choice-benefit selections and upgrade certificate issues, uses and expiries. Every criterion is
    optional. Returns every matching entry, or a not-found message.

    Args:
        loyalty_activity_id: Reference number of the activity entry itself; leave "" if unknown.
        membership_id: Reference number of the membership; leave "" if unknown.
        customer_id: Customer reference number of the member; leave "" if unknown.
        source_ticket_id: Reference number of the Crestline ticket the entry relates to; leave "" if unknown.
        reversed_activity_id: Reference number of the entry a redeposit, reversal or reinstatement undoes; leave "" if unknown.
    """
    return _report(ctx.find("loyalty_activity", **_crit({"loyalty_activity_id": loyalty_activity_id,
                                             "membership_id": membership_id, "customer_id": customer_id,
                                             "source_ticket_id": source_ticket_id,
                                             "reversed_activity_id": reversed_activity_id})), "Summit activity")


@tool(owner="agent", rw="read")
def find_loyalty_upgrades(ctx: ToolContext, upgrade_id: str = "", membership_id: str = "", customer_id: str = "",
                          source_ticket_id: str = "", source_request_id: str = "") -> str:
    """Look up upgrade waitlist requests and clearances.

    Entries show the ticket and segment, the upgrade method (complimentary, certificate or miles),
    the cabin requested and, on clearance, the miles, certificates or co-pay charged. Every criterion
    is optional. Returns every matching entry, or a not-found message.

    Args:
        upgrade_id: Reference number of the upgrade entry itself; leave "" if unknown.
        membership_id: Reference number of the requesting membership; leave "" if unknown.
        customer_id: Customer reference number of the member; leave "" if unknown.
        source_ticket_id: Reference number of the ticket to be upgraded; leave "" if unknown.
        source_request_id: Reference number of the request a clearance fulfils; leave "" if unknown.
    """
    return _report(ctx.find("loyalty_upgrades", **_crit({"upgrade_id": upgrade_id, "membership_id": membership_id,
                                             "customer_id": customer_id, "source_ticket_id": source_ticket_id,
                                             "source_request_id": source_request_id})), "upgrade entries")


# --------------------------------------------------------------------------- companion
@tool(owner="agent", rw="read")
def find_companion_holdings(ctx: ToolContext, companion_id: str = "", customer_id: str = "",
                            membership_id: str = "") -> str:
    """Look up companion certificates and companion passes.

    Each record shows the product, certificate number, status, how it was issued, issue and book-by
    dates, companion trips remaining, the designated companion on a pass and any revocation reason.
    Every criterion is optional. Returns every matching record, or a not-found message.

    Args:
        companion_id: Reference number of the certificate or pass record itself; leave "" if unknown.
        customer_id: Customer reference number of the holder; leave "" if unknown.
        membership_id: Reference number of the holder's Summit membership; leave "" if unknown.
    """
    return _report(ctx.find("companion_holdings", **_crit({"companion_id": companion_id, "customer_id": customer_id,
                                               "membership_id": membership_id})), "companion products")


@tool(owner="agent", rw="read")
def find_companion_ledger(ctx: ToolContext, companion_entry_id: str = "", companion_id: str = "",
                          customer_id: str = "", reversed_entry_id: str = "") -> str:
    """Look up the trip and charge history of companion certificates and passes.

    Entries cover trips granted, companion bookings (companion ticket, holder ticket, companion
    name, travel date, channel), companion fares, taxes and fees charged, reinstatements, refunds and
    forfeitures. Every criterion is optional. Returns every matching entry, or a not-found message.

    Args:
        companion_entry_id: Reference number of the entry itself; leave "" if unknown.
        companion_id: Reference number of the certificate or pass; leave "" if unknown.
        customer_id: Customer reference number of the holder; leave "" if unknown.
        reversed_entry_id: Reference number of the entry a reinstatement or refund undoes; leave "" if unknown.
    """
    return _report(ctx.find("companion_ledger", **_crit({"companion_entry_id": companion_entry_id,
                                             "companion_id": companion_id, "customer_id": customer_id,
                                             "reversed_entry_id": reversed_entry_id})), "companion entries")


# --------------------------------------------------------------------------- business
@tool(owner="agent", rw="read")
def find_business_holdings(ctx: ToolContext, business_account_id: str = "", customer_id: str = "") -> str:
    """Look up corporate travel agreements.

    Each record shows the agreement number, tier, status, tour code, travel manager, application,
    approval and term dates, any open review or suspension, the company points balance, this
    agreement year's spend and the open invoice balance. Every criterion is optional. Returns every
    matching agreement, or a not-found message.

    Args:
        business_account_id: Reference number of the agreement record itself; leave "" if unknown.
        customer_id: Customer reference number of the company's business profile; leave "" if unknown.
    """
    return _report(ctx.find("business_holdings", **_crit({"business_account_id": business_account_id,
                                              "customer_id": customer_id})), "corporate agreements")


@tool(owner="agent", rw="read")
def find_business_activity(ctx: ToolContext, business_activity_id: str = "", business_account_id: str = "",
                           customer_id: str = "", source_ticket_id: str = "", traveler_customer_id: str = "") -> str:
    """Look up company points and spend activity on corporate agreements.

    Entries cover points and spend credited for flown segments, enrollment and milestone bonuses,
    redemptions for award tickets, upgrades and Summit status awards, point expiries and
    agreement-year resets. Every criterion is optional. Returns every matching entry, or a not-found
    message.

    Args:
        business_activity_id: Reference number of the entry itself; leave "" if unknown.
        business_account_id: Reference number of the agreement; leave "" if unknown.
        customer_id: Customer reference number of the company; leave "" if unknown.
        source_ticket_id: Reference number of the ticket flown or redeemed for; leave "" if unknown.
        traveler_customer_id: Customer reference number of the roster traveler involved; leave "" if unknown.
    """
    return _report(ctx.find("business_activity", **_crit({"business_activity_id": business_activity_id,
                                              "business_account_id": business_account_id,
                                              "customer_id": customer_id, "source_ticket_id": source_ticket_id,
                                              "traveler_customer_id": traveler_customer_id})),
                   "corporate points activity")


@tool(owner="agent", rw="read")
def find_business_roster(ctx: ToolContext, roster_entry_id: str = "", business_account_id: str = "",
                         customer_id: str = "", traveler_customer_id: str = "") -> str:
    """Look up traveler additions to and removals from corporate agreement rosters.

    Entries show the traveler, the role (employee, contractor or travel arranger), the effective
    date and, for removals, the reason. Every criterion is optional. Returns every matching entry,
    or a not-found message.

    Args:
        roster_entry_id: Reference number of the roster entry itself; leave "" if unknown.
        business_account_id: Reference number of the agreement; leave "" if unknown.
        customer_id: Customer reference number of the company; leave "" if unknown.
        traveler_customer_id: Customer reference number of the traveler; leave "" if unknown.
    """
    return _report(ctx.find("business_roster", **_crit({"roster_entry_id": roster_entry_id,
                                            "business_account_id": business_account_id,
                                            "customer_id": customer_id,
                                            "traveler_customer_id": traveler_customer_id})), "roster entries")


@tool(owner="agent", rw="read")
def find_business_invoices(ctx: ToolContext, invoice_entry_id: str = "", business_account_id: str = "",
                           customer_id: str = "", source_ticket_id: str = "") -> str:
    """Look up invoice charges, payments and late fees on corporate agreements.

    Entries show the invoice number, date, due date, amount, the ticket billed and the company's
    remittance reference on payments. Every criterion is optional. Returns every matching entry, or
    a not-found message.

    Args:
        invoice_entry_id: Reference number of the invoice entry itself; leave "" if unknown.
        business_account_id: Reference number of the agreement billed; leave "" if unknown.
        customer_id: Customer reference number of the company; leave "" if unknown.
        source_ticket_id: Reference number of the ticket billed; leave "" if unknown.
    """
    return _report(ctx.find("business_invoices", **_crit({"invoice_entry_id": invoice_entry_id,
                                              "business_account_id": business_account_id,
                                              "customer_id": customer_id, "source_ticket_id": source_ticket_id})),
                   "invoice entries")


# --------------------------------------------------------------------------- club
@tool(owner="agent", rw="read")
def find_club_holdings(ctx: ToolContext, club_membership_id: str = "", customer_id: str = "",
                       business_account_id: str = "") -> str:
    """Look up Summit Club lounge memberships.

    Each record shows the membership, membership number, status, how it was obtained, start and
    renewal dates, the auto-renew setting, guest passes remaining and, for corporate memberships,
    the paying agreement. Every criterion is optional. Returns every matching membership, or a
    not-found message.

    Args:
        club_membership_id: Reference number of the lounge membership record itself; leave "" if unknown.
        customer_id: Customer reference number of the member; leave "" if unknown.
        business_account_id: Reference number of the corporate agreement paying for it; leave "" if unknown.
    """
    return _report(ctx.find("club_holdings", **_crit({"club_membership_id": club_membership_id, "customer_id": customer_id,
                                          "business_account_id": business_account_id})), "lounge memberships")


@tool(owner="agent", rw="read")
def find_club_ledger(ctx: ToolContext, club_entry_id: str = "", club_membership_id: str = "", customer_id: str = "",
                     reversed_entry_id: str = "") -> str:
    """Look up lounge visits, guest passes and lounge charges.

    Entries cover club visits (date, airport, guests), guest pass grants, uses and expiries, and
    dues, guest fees, extra-visit fees and their refunds. Every criterion is optional. Returns every
    matching entry, or a not-found message.

    Args:
        club_entry_id: Reference number of the entry itself; leave "" if unknown.
        club_membership_id: Reference number of the lounge membership; leave "" if unknown.
        customer_id: Customer reference number of the member; leave "" if unknown.
        reversed_entry_id: Reference number of the charge a refund reverses; leave "" if unknown.
    """
    return _report(ctx.find("club_ledger", **_crit({"club_entry_id": club_entry_id, "club_membership_id": club_membership_id,
                                        "customer_id": customer_id, "reversed_entry_id": reversed_entry_id})),
                   "lounge entries")


# --------------------------------------------------------------------------- subscriptions
@tool(owner="agent", rw="read")
def find_pass_holdings(ctx: ToolContext, pass_id: str = "", customer_id: str = "") -> str:
    """Look up seat and bag subscriptions.

    Each record shows the subscription, subscription number, status, purchase date, current term
    dates, billing plan, companions covered and the auto-renew setting. Every criterion is optional.
    Returns every matching subscription, or a not-found message.

    Args:
        pass_id: Reference number of the subscription record itself; leave "" if unknown.
        customer_id: Customer reference number of the subscriber; leave "" if unknown.
    """
    return _report(ctx.find("pass_holdings", **_crit({"pass_id": pass_id, "customer_id": customer_id})), "subscriptions")


@tool(owner="agent", rw="read")
def find_pass_ledger(ctx: ToolContext, pass_entry_id: str = "", pass_id: str = "", customer_id: str = "",
                     reversed_entry_id: str = "", source_ticket_id: str = "") -> str:
    """Look up subscription charges, refunds and benefit uses.

    Entries cover term prices, monthly installments, companion add-ons, upgrade differences, early
    termination fees and refunds, and each covered bag direction or seat used on a ticket. Every
    criterion is optional. Returns every matching entry, or a not-found message.

    Args:
        pass_entry_id: Reference number of the entry itself; leave "" if unknown.
        pass_id: Reference number of the subscription; leave "" if unknown.
        customer_id: Customer reference number of the subscriber; leave "" if unknown.
        reversed_entry_id: Reference number of the charge a refund reverses; leave "" if unknown.
        source_ticket_id: Reference number of the ticket a benefit was used on; leave "" if unknown.
    """
    return _report(ctx.find("pass_ledger", **_crit({"pass_entry_id": pass_entry_id, "pass_id": pass_id,
                                        "customer_id": customer_id, "reversed_entry_id": reversed_entry_id,
                                        "source_ticket_id": source_ticket_id})), "subscription entries")


# --------------------------------------------------------------------------- service logs
@tool(owner="agent", rw="read")
def find_identity_verifications(ctx: ToolContext, verification_id: str = "", customer_id: str = "") -> str:
    """Look up the recorded outcome of identity verification for a customer.

    The record shows whether the customer's identity has been verified and when the latest attempt
    was made. Every criterion is optional. Returns the matching record, or a not-found message when
    no verification has been attempted.

    Args:
        verification_id: Reference number of the verification record itself; leave "" if unknown.
        customer_id: Customer reference number; leave "" if unknown.
    """
    return _report(ctx.find("identity_verifications", **_crit({"verification_id": verification_id,
                                                   "customer_id": customer_id})), "verification records")


@tool(owner="agent", rw="read")
def find_agent_handoffs(ctx: ToolContext, handoff_id: str = "", customer_id: str = "") -> str:
    """Look up transfers of a customer to a human representative.

    Each record shows the reason recorded and when the transfer was made. Every criterion is
    optional. Returns every matching record, or a not-found message.

    Args:
        handoff_id: Reference number of the transfer record itself; leave "" if unknown.
        customer_id: Customer reference number; leave "" if unknown.
    """
    return _report(ctx.find("agent_handoffs", **_crit({"handoff_id": handoff_id, "customer_id": customer_id})),
                   "transfer records")

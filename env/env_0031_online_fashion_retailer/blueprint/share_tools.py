"""Shared tools for env_0031_online_fashion_retailer (Marlowe & Finch customer care).

Every tool here is a SHARE tool: always present in its owner's tool list.
  - One lookup per record family (one finder per table), each taking every reference number the
    record carries as an optional criterion; the customer lookup doubles as the identity entry.
  - verify_customer_identity: compares caller-stated credentials with the profile (passes at 2 matches)
    and stores only the verified outcome.
  - transfer_to_human_agent: the single handoff, with exactly two reasons.
Customer-originated writes are hidden task tools in each difficulty's task_tools.py, never here.
"""

from erlbench import ToolContext, tool


def _given(criteria: dict) -> dict:
    # Keep only the criteria the agent actually supplied.
    return {k: v for k, v in criteria.items() if v}


def _report(label: str, match: dict, rows: list) -> str:
    # Return the records found, or say plainly that nothing matched.
    return str(rows) if rows else f"No {label} found for {match}."


# ----------------------------------------------------------------------------- customers & logs

@tool(owner="agent", rw="read")
def find_customers(ctx: ToolContext, customer_id: str = "", name: str = "", email: str = "",
                   phone_number: str = "") -> str:
    """Look up a Marlowe & Finch customer profile to establish whose account the conversation is about.

    Search by the customer reference number, or by what the caller naturally says: their full name,
    their sign-in email, or their mobile number. Every criterion is optional; give whichever you have,
    and add another when several profiles share the first. The profile returned shows the customer
    reference number, name, email, mobile number, date of birth, billing ZIP code and state, and the
    date the profile was opened. Finding a profile does not prove the caller is its owner — identity is
    confirmed separately.

    Args:
        customer_id: The customer reference number, if already known; leave "" otherwise.
        name: The caller's full name as they state it; leave "" if not given.
        email: The email address the caller signs in with; leave "" if not given.
        phone_number: The caller's mobile number, 10 digits; leave "" if not given.
    """
    match = {k: v for k, v in {"customer_id": customer_id, "name": name, "email": email,
                               "phone_number": phone_number}.items() if v}
    if not match:
        return "Error: provide at least one detail to find the customer."
    rows = ctx.fuzzy_find("customers", **match)
    if not rows:
        return f"No customer profile matches {match}."
    if len(rows) > 1:
        return f"Error: {len(rows)} profiles match {match}; ask the caller for one more detail."
    return str(rows[0])


@tool(owner="agent", rw="read")
def find_identity_verifications(ctx: ToolContext, verification_id: str = "", customer_id: str = "") -> str:
    """Check whether a customer's identity has already been confirmed in this contact, and when.

    Returns the verification record — whether the caller passed and the time of the latest attempt —
    found by its own reference or by the customer reference number. Every criterion is optional.

    Args:
        verification_id: Reference of the verification record; leave "" if unknown.
        customer_id: The customer reference number; leave "" if unknown.
    """
    match = _given({"verification_id": verification_id, "customer_id": customer_id})
    return _report("identity verification record", match, ctx.find("identity_verifications", **match))


@tool(owner="agent", rw="read")
def find_human_handoffs(ctx: ToolContext, handoff_id: str = "", customer_id: str = "") -> str:
    """See whether a customer has already been passed to a human representative, and why.

    Returns handoff records with their reason and time, found by the handoff reference or the
    customer reference number. Every criterion is optional.

    Args:
        handoff_id: Reference of the handoff record; leave "" if unknown.
        customer_id: The customer reference number; leave "" if unknown.
    """
    match = _given({"handoff_id": handoff_id, "customer_id": customer_id})
    return _report("handoff record", match, ctx.find("human_handoffs", **match))


# ----------------------------------------------------------------------------- Marlowe Rewards

@tool(owner="agent", rw="read")
def find_loyalty_memberships(ctx: ToolContext, membership_id: str = "", customer_id: str = "") -> str:
    """Look up a customer's Marlowe Rewards membership.

    Shows the tier held and when it started and stays valid until, the membership status and any
    suspension reason, the enrollment and closing dates, and the current points balance (pending and
    available together). Search by membership reference or customer reference number; every criterion
    is optional.

    Args:
        membership_id: Reference of the Marlowe Rewards membership; leave "" if unknown.
        customer_id: The customer reference number; leave "" if unknown.
    """
    match = _given({"membership_id": membership_id, "customer_id": customer_id})
    return _report("Marlowe Rewards membership", match, ctx.find("loyalty_memberships", **match))


@tool(owner="agent", rw="read")
def find_loyalty_ledger(ctx: ToolContext, loyalty_entry_id: str = "", membership_id: str = "",
                        customer_id: str = "", order_id: str = "", return_id: str = "") -> str:
    """Read the Marlowe Rewards points history: earnings, bonuses, reversals, conversions into Rewards Notes and forfeitures.

    Each entry shows its posting and availability dates, the signed points, the tier and multiplier
    applied, the qualifying or refunded spend, and the order, return, bonus or reward it concerns.
    Narrow by entry reference, membership, customer, order or return; every criterion is optional.

    Args:
        loyalty_entry_id: Reference of one points entry; leave "" if unknown.
        membership_id: Reference of the membership; leave "" if unknown.
        customer_id: The customer reference number; leave "" if unknown.
        order_id: An order number, to see the points it earned or lost; leave "" if unknown.
        return_id: A return (RMA) number, to see the reversal it caused; leave "" if unknown.
    """
    match = _given({"loyalty_entry_id": loyalty_entry_id, "membership_id": membership_id, "customer_id": customer_id, "order_id": order_id, "return_id": return_id})
    return _report("points entries", match, ctx.find("loyalty_ledger", **match))


@tool(owner="agent", rw="read")
def find_loyalty_requests(ctx: ToolContext, loyalty_request_id: str = "", customer_id: str = "",
                          membership_id: str = "") -> str:
    """Look up membership requests a member has made, such as a request to close their Marlowe Rewards membership, and whether they confirmed it.

    Args:
        loyalty_request_id: Reference of the request; leave "" if unknown.
        customer_id: The customer reference number; leave "" if unknown.
        membership_id: Reference of the membership concerned; leave "" if unknown.
    """
    match = _given({"loyalty_request_id": loyalty_request_id, "customer_id": customer_id, "membership_id": membership_id})
    return _report("membership request", match, ctx.find("loyalty_requests", **match))


# ----------------------------------------------------------------------------- Online Orders

@tool(owner="agent", rw="read")
def find_orders(ctx: ToolContext, order_id: str = "", customer_id: str = "") -> str:
    """Look up online orders.

    An order shows its delivery service and status, placed date and time, shipping address, whether it
    was marked as a gift, merchandise subtotal, discounts, shipping fee, surcharge, tax and total, the
    promotion code used, the delivery promise, dispatch, tracking and delivery details, and any
    cancellation or closing. Search by order number or customer reference number; every criterion is
    optional.

    Args:
        order_id: The order number; leave "" if unknown.
        customer_id: The customer reference number, to list that customer's orders; leave "" if unknown.
    """
    match = _given({"order_id": order_id, "customer_id": customer_id})
    return _report("order", match, ctx.find("orders", **match))


@tool(owner="agent", rw="read")
def find_order_lines(ctx: ToolContext, order_line_id: str = "", order_id: str = "", customer_id: str = "",
                     booked_line_id: str = "") -> str:
    """Read the lines of an order and what happened to them afterwards.

    Booking lines show the SKU, product, size, colour, merchandise class, units, unit price, price type,
    final-sale flag and allocated discount; later lines record cancellations, price adjustments and late
    promotion credits, each pointing to the booking line it acts on. Search by line reference, order
    number, customer, or the booking line a later entry refers to; every criterion is optional.

    Args:
        order_line_id: Reference of one line entry; leave "" if unknown.
        order_id: The order number; leave "" if unknown.
        customer_id: The customer reference number; leave "" if unknown.
        booked_line_id: Reference of a booking line, to find the cancellations or adjustments made to it; leave "" if unknown.
    """
    match = _given({"order_line_id": order_line_id, "order_id": order_id, "customer_id": customer_id, "booked_line_id": booked_line_id})
    return _report("order lines", match, ctx.find("order_lines", **match))


@tool(owner="agent", rw="read")
def find_order_payments(ctx: ToolContext, payment_id: str = "", order_id: str = "", customer_id: str = "",
                        instrument_id: str = "", booked_line_id: str = "") -> str:
    """Read how an order was paid and what was given back to each payment method at order level.

    Entries show each tender captured at dispatch (card or wallet, gift card, store credit, Goodwill
    Credit, Rewards Note) with its amount, and each order-level refund with its reason. Search by
    payment reference, order number, customer, stored-value instrument or booking line; every
    criterion is optional.

    Args:
        payment_id: Reference of one payment entry; leave "" if unknown.
        order_id: The order number; leave "" if unknown.
        customer_id: The customer reference number; leave "" if unknown.
        instrument_id: Reference of a gift card, store credit or Rewards Note used as payment; leave "" if unknown.
        booked_line_id: Reference of the booking line a line-level refund was for; leave "" if unknown.
    """
    match = _given({"payment_id": payment_id, "order_id": order_id, "customer_id": customer_id, "instrument_id": instrument_id, "booked_line_id": booked_line_id})
    return _report("payment entries", match, ctx.find("order_payments", **match))


# ----------------------------------------------------------------------------- Gift Cards & Store Credit

@tool(owner="agent", rw="read")
def find_credit_instruments(ctx: ToolContext, instrument_id: str = "", customer_id: str = "") -> str:
    """Look up gift cards, store credit, Goodwill Credit and Marlowe Rewards Notes.

    Each instrument shows its type, status, holder, issue, valid-from and expiry dates, initial value
    and current balance, the last four digits of a card number, what it was issued for, registration,
    any lock with its reason and date, and how and when it closed. Search by instrument reference or
    holder; every criterion is optional.

    Args:
        instrument_id: Reference of the instrument; leave "" if unknown.
        customer_id: The customer reference number of the holder; leave "" if unknown.
    """
    match = _given({"instrument_id": instrument_id, "customer_id": customer_id})
    return _report("stored-value instrument", match, ctx.find("credit_instruments", **match))


@tool(owner="agent", rw="read")
def find_credit_transactions(ctx: ToolContext, credit_txn_id: str = "", instrument_id: str = "",
                             customer_id: str = "", order_id: str = "", return_id: str = "",
                             counterpart_instrument_id: str = "") -> str:
    """Read the balance history of stored-value instruments.

    Entries show loads, spending on orders, refunds back to the instrument, clawbacks, transfers to a
    replacement or consolidated card, cash-outs and forfeitures, each with its date and signed amount.
    Search by entry reference, instrument, holder, order, return, or the instrument that received a
    transfer; every criterion is optional.

    Args:
        credit_txn_id: Reference of one entry; leave "" if unknown.
        instrument_id: Reference of the instrument; leave "" if unknown.
        customer_id: The customer reference number; leave "" if unknown.
        order_id: An order number the value was spent on or refunded from; leave "" if unknown.
        return_id: A return (RMA) number behind a refund or clawback; leave "" if unknown.
        counterpart_instrument_id: Reference of the instrument that received transferred value; leave "" if unknown.
    """
    match = _given({"credit_txn_id": credit_txn_id, "instrument_id": instrument_id, "customer_id": customer_id, "order_id": order_id, "return_id": return_id, "counterpart_instrument_id": counterpart_instrument_id})
    return _report("instrument entries", match, ctx.find("credit_transactions", **match))


@tool(owner="agent", rw="read")
def find_credit_requests(ctx: ToolContext, credit_request_id: str = "", customer_id: str = "",
                         instrument_id: str = "") -> str:
    """Look up a holder's cash-out or consolidation requests for their stored-value instruments, and whether the holder confirmed them.

    Args:
        credit_request_id: Reference of the request; leave "" if unknown.
        customer_id: The customer reference number; leave "" if unknown.
        instrument_id: Reference of the instrument concerned; leave "" if unknown.
    """
    match = _given({"credit_request_id": credit_request_id, "customer_id": customer_id, "instrument_id": instrument_id})
    return _report("instrument request", match, ctx.find("credit_requests", **match))


# ----------------------------------------------------------------------------- Returns & Exchanges

@tool(owner="agent", rw="read")
def find_return_cases(ctx: ToolContext, return_id: str = "", customer_id: str = "", order_id: str = "") -> str:
    """Look up return authorizations (RMAs).

    A return shows its type and status, the order it is against, the return method, the return-by date
    and extensions used, any defect-photo reference or exchange SKU, the return parcel's tracking and
    first scan, and its receipt, inspection, settlement or closing dates. Search by RMA number,
    customer or order; every criterion is optional.

    Args:
        return_id: The return (RMA) number; leave "" if unknown.
        customer_id: The customer reference number of the person returning; leave "" if unknown.
        order_id: The order number the return is against; leave "" if unknown.
    """
    match = _given({"return_id": return_id, "customer_id": customer_id, "order_id": order_id})
    return _report("return", match, ctx.find("return_cases", **match))


@tool(owner="agent", rw="read")
def find_return_lines(ctx: ToolContext, return_line_id: str = "", return_id: str = "", customer_id: str = "",
                      booked_line_id: str = "") -> str:
    """Read which order lines are on a return and how their units were graded.

    Authorization entries show the line, SKU, units, reason and any exchange SKU; inspection entries
    show the units found in each grade, the shoebox condition and the outcome. Search by entry
    reference, RMA number, customer, or the order booking line; every criterion is optional.

    Args:
        return_line_id: Reference of one entry; leave "" if unknown.
        return_id: The return (RMA) number; leave "" if unknown.
        customer_id: The customer reference number; leave "" if unknown.
        booked_line_id: Reference of the order booking line, to see every return it appears on; leave "" if unknown.
    """
    match = _given({"return_line_id": return_line_id, "return_id": return_id, "customer_id": customer_id, "booked_line_id": booked_line_id})
    return _report("return lines", match, ctx.find("return_lines", **match))


@tool(owner="agent", rw="read")
def find_return_settlements(ctx: ToolContext, settlement_id: str = "", return_id: str = "", customer_id: str = "",
                            order_id: str = "", booked_line_id: str = "", instrument_id: str = "",
                            exchange_order_id: str = "") -> str:
    """Read the money and goods side of a return.

    Entries show value credited for accepted units (merchandise, tax and any shipping share), fees
    withheld, refunds paid with their stage and payment method, instant-credit recoveries, exchange
    shipments and Instant Exchange card holds. Search by entry reference, RMA number, customer, order,
    booking line, stored-value instrument, or the order carrying an exchange; every criterion is
    optional.

    Args:
        settlement_id: Reference of one entry; leave "" if unknown.
        return_id: The return (RMA) number; leave "" if unknown.
        customer_id: The customer reference number; leave "" if unknown.
        order_id: The original order number; leave "" if unknown.
        booked_line_id: Reference of an order booking line; leave "" if unknown.
        instrument_id: Reference of a gift card, store credit or Rewards Note refunded or recovered from; leave "" if unknown.
        exchange_order_id: The order number that carried an exchange replacement; leave "" if unknown.
    """
    match = _given({"settlement_id": settlement_id, "return_id": return_id, "customer_id": customer_id, "order_id": order_id, "booked_line_id": booked_line_id, "instrument_id": instrument_id, "exchange_order_id": exchange_order_id})
    return _report("return settlement entries", match, ctx.find("return_settlements", **match))


# ----------------------------------------------------------------------------- Pre-Orders & Back-Orders

@tool(owner="agent", rw="read")
def find_reservations(ctx: ToolContext, reservation_id: str = "", customer_id: str = "",
                      fulfilment_order_id: str = "") -> str:
    """Look up pre-order and back-order reservations.

    A reservation shows its type and status, when it was made, the SKU, style, size, units and price,
    any deposit due, the original and current ship-by dates, delay notices sent and any consent
    deadline, personalisation and its confirmation, production, allocation and shipment, and any
    cancellation with its reason. Search by reservation number, customer, or the order that carried it;
    every criterion is optional.

    Args:
        reservation_id: The reservation number; leave "" if unknown.
        customer_id: The customer reference number; leave "" if unknown.
        fulfilment_order_id: The order number the reserved item shipped on; leave "" if unknown.
    """
    match = _given({"reservation_id": reservation_id, "customer_id": customer_id, "fulfilment_order_id": fulfilment_order_id})
    return _report("reservation", match, ctx.find("reservations", **match))


@tool(owner="agent", rw="read")
def find_reservation_events(ctx: ToolContext, reservation_event_id: str = "", reservation_id: str = "",
                            customer_id: str = "", fulfilment_order_id: str = "") -> str:
    """Read the history of a reservation: deposits charged, refunded, kept or applied, delay notices with their revised dates and consent terms, and card authorization renewals.

    Args:
        reservation_event_id: Reference of one entry; leave "" if unknown.
        reservation_id: The reservation number; leave "" if unknown.
        customer_id: The customer reference number; leave "" if unknown.
        fulfilment_order_id: The order number a deposit was applied to; leave "" if unknown.
    """
    match = _given({"reservation_event_id": reservation_event_id, "reservation_id": reservation_id, "customer_id": customer_id, "fulfilment_order_id": fulfilment_order_id})
    return _report("reservation entries", match, ctx.find("reservation_events", **match))


@tool(owner="agent", rw="read")
def find_reservation_requests(ctx: ToolContext, reservation_request_id: str = "", customer_id: str = "",
                              reservation_id: str = "") -> str:
    """Look up requests a customer made about a reservation, such as cancelling a made-to-order item already in production, and whether they confirmed it.

    Args:
        reservation_request_id: Reference of the request; leave "" if unknown.
        customer_id: The customer reference number; leave "" if unknown.
        reservation_id: The reservation number; leave "" if unknown.
    """
    match = _given({"reservation_request_id": reservation_request_id, "customer_id": customer_id, "reservation_id": reservation_id})
    return _report("reservation request", match, ctx.find("reservation_requests", **match))


# ----------------------------------------------------------------------------- Delivery Claims

@tool(owner="agent", rw="read")
def find_delivery_claims(ctx: ToolContext, claim_id: str = "", customer_id: str = "", order_id: str = "") -> str:
    """Look up delivery claims for late, undelivered, lost, damaged, short or wrong parcels.

    A claim shows its type and status, the order, the value claimed, any carrier trace with its
    reference and result, the decision date with the resolution or denial reason, appeals made, and
    its resolution or withdrawal date. Search by claim number, customer or order; every criterion is
    optional.

    Args:
        claim_id: The claim number; leave "" if unknown.
        customer_id: The customer reference number; leave "" if unknown.
        order_id: The order number the claim concerns; leave "" if unknown.
    """
    match = _given({"claim_id": claim_id, "customer_id": customer_id, "order_id": order_id})
    return _report("delivery claim", match, ctx.find("delivery_claims", **match))


@tool(owner="agent", rw="read")
def find_claim_events(ctx: ToolContext, claim_event_id: str = "", claim_id: str = "", customer_id: str = "",
                      booked_line_id: str = "", replacement_order_id: str = "") -> str:
    """Read the evidence and compensation recorded on delivery claims.

    Entries show each piece of evidence with its reference, each compensation given (reshipment,
    refund, shipping fee refund or Goodwill Credit) with units and value, and any value charged back.
    Search by entry reference, claim number, customer, order booking line, or the order carrying a
    reshipment; every criterion is optional.

    Args:
        claim_event_id: Reference of one entry; leave "" if unknown.
        claim_id: The claim number; leave "" if unknown.
        customer_id: The customer reference number; leave "" if unknown.
        booked_line_id: Reference of the order booking line concerned; leave "" if unknown.
        replacement_order_id: The order number that carried a reshipment; leave "" if unknown.
    """
    match = _given({"claim_event_id": claim_event_id, "claim_id": claim_id, "customer_id": customer_id, "booked_line_id": booked_line_id, "replacement_order_id": replacement_order_id})
    return _report("claim entries", match, ctx.find("claim_events", **match))


# ----------------------------------------------------------------------------- Marlowe & Finch Unlimited

@tool(owner="agent", rw="read")
def find_pass_memberships(ctx: ToolContext, pass_id: str = "", customer_id: str = "") -> str:
    """Look up a customer's Marlowe & Finch Unlimited membership.

    Shows the plan and status, enrollment and trial end dates, the current period, auto-renew, any
    student verification date, any plan change waiting for renewal, and the date it ended. Search by
    membership reference or customer; every criterion is optional.

    Args:
        pass_id: Reference of the Unlimited membership; leave "" if unknown.
        customer_id: The customer reference number; leave "" if unknown.
    """
    match = _given({"pass_id": pass_id, "customer_id": customer_id})
    return _report("Unlimited membership", match, ctx.find("pass_memberships", **match))


@tool(owner="agent", rw="read")
def find_pass_ledger(ctx: ToolContext, pass_entry_id: str = "", pass_id: str = "", customer_id: str = "",
                     order_id: str = "") -> str:
    """Read an Unlimited membership's billing and benefit history: fees charged and refunded, declined charges, renewal notices, and each order that shipped free or got a free return label.

    Args:
        pass_entry_id: Reference of one entry; leave "" if unknown.
        pass_id: Reference of the membership; leave "" if unknown.
        customer_id: The customer reference number; leave "" if unknown.
        order_id: An order number, to see the benefit it received; leave "" if unknown.
    """
    match = _given({"pass_entry_id": pass_entry_id, "pass_id": pass_id, "customer_id": customer_id, "order_id": order_id})
    return _report("Unlimited entries", match, ctx.find("pass_ledger", **match))


@tool(owner="agent", rw="read")
def find_pass_requests(ctx: ToolContext, pass_request_id: str = "", customer_id: str = "", pass_id: str = "") -> str:
    """Look up a member's requests to cancel their Unlimited membership, and whether they confirmed them.

    Args:
        pass_request_id: Reference of the request; leave "" if unknown.
        customer_id: The customer reference number; leave "" if unknown.
        pass_id: Reference of the membership concerned; leave "" if unknown.
    """
    match = _given({"pass_request_id": pass_request_id, "customer_id": customer_id, "pass_id": pass_id})
    return _report("Unlimited request", match, ctx.find("pass_requests", **match))


# ----------------------------------------------------------------------------- identity & handoff

def _norm(field: str, value) -> str:
    # Comparison form of a credential: digits only for the phone number, trimmed and case-folded otherwise.
    text = str(value or "").strip()
    if field == "phone_number":
        return "".join(ch for ch in text if ch.isdigit())
    return text.casefold()


@tool(owner="agent", rw="write")
def verify_customer_identity(ctx: ToolContext, customer_id: str, email: str = "", phone_number: str = "",
                             date_of_birth: str = "", billing_zip: str = "") -> str:
    """Confirm that the caller is the owner of a Marlowe & Finch profile, and record the outcome.

    Identity must be confirmed before any account details are discussed or anything is changed on the
    account. This tool does the comparison itself: it checks each detail the caller states against the
    profile, counts the details that match, and confirms the caller when at least 2 match. The
    customer reference number only tells the tool which profile to check — it never counts as a match.
    Callers usually know only some of their details, so pass exactly what the caller said and leave the
    rest blank. The outcome is recorded; if a first attempt falls short and a later attempt with more
    details succeeds, the caller stays confirmed.

    Args:
        customer_id: The customer reference number of the profile being checked, as shown by the customer lookup. Required.
        email: The sign-in email address the caller states; leave "" if not stated.
        phone_number: The mobile number the caller states, 10 digits; leave "" if not stated.
        date_of_birth: The date of birth the caller states, YYYY-MM-DD; leave "" if not stated.
        billing_zip: The 5-digit ZIP code of the caller's billing address; leave "" if not stated.
    """
    if not customer_id:
        return "Error: customer_id is required; look the customer up first and pass their reference number."
    rows = ctx.find("customers", customer_id=customer_id)
    if not rows:
        return f"Error: no customer profile {customer_id}; cannot verify."
    rec = rows[0]
    # The tool owns the comparison; the locator customer_id is deliberately not a credential.
    supplied = {"email": email, "phone_number": phone_number, "date_of_birth": date_of_birth,
                "billing_zip": billing_zip}
    matched = sum(1 for field, value in supplied.items()
                  if value and _norm(field, rec.get(field)) == _norm(field, value))
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
    if verified:
        return f"Identity confirmed for {customer_id} ({matched} detail(s) matched in this attempt)."
    return (f"Identity NOT confirmed for {customer_id}: only {matched} of the 2 required details matched. "
            "Ask the caller for another detail on the profile and try again.")


@tool(owner="agent", rw="write")
def transfer_to_human_agent(ctx: ToolContext, customer_id: str, reason: str) -> str:
    """Pass the customer to a human customer care representative and record why.

    Use it in one of two situations only: when no Marlowe & Finch policy lets you resolve what the
    customer needs, or when the customer has explicitly asked for a human representative at least 2
    times in the conversation.

    Args:
        customer_id: The customer reference number, as shown by the customer lookup.
        reason: Exactly one of POLICY_NOT_COVERED (no policy lets the request be resolved) or CUSTOMER_REQUESTED (the customer has asked for a human representative at least 2 times); never free text.
    """
    allowed = {"POLICY_NOT_COVERED", "CUSTOMER_REQUESTED"}
    if reason not in allowed:
        return f"Error: unknown handoff reason '{reason}'. Valid: {', '.join(sorted(allowed))}."
    if not ctx.find("customers", customer_id=customer_id):
        return f"Error: no customer profile {customer_id}; cannot record the handoff."
    rid = ctx.make_id("hof_", customer_id, reason)
    ctx.create("human_handoffs", rid, handoff_id=rid, customer_id=customer_id, reason=reason,
               created_at=ctx.now())
    return f"Customer {customer_id} handed to a human representative ({reason})."

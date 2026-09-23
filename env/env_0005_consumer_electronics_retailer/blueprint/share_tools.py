"""Shared tools for Northbeam Electronics customer care.

Everything here is always on the tool list: the complete record-lookup layer across the whole
customer world, the identity-verification write, and the transfer to a human representative.
Difficulty-specific business actions live in each difficulty's own task_tools.py.
"""

from erlbench import ToolContext, tool

# Scenario operational constants. K: identity credentials that must match before the caller is
# treated as verified. R: times a caller must explicitly ask for a person before the handoff is
# recorded as CUSTOMER_REQUESTED.
VERIFICATION_MATCH_THRESHOLD = 2
HUMAN_REQUEST_THRESHOLD = 2


@tool(owner="agent", rw="read")
def find_customers(ctx: ToolContext, customer_id: str = "", phone_number: str = "", email: str = "",
                   name: str = "", postal_code: str = "", business_name: str = "") -> str:
    """Look up the customer profile so you know whose account the call is about.

    Search by the customer reference number when the caller can quote it, or by what a caller
    naturally says out loud: the mobile number on the profile, the email address, the name,
    the postal code of the service address, or the registered name of a business. Every
    criterion is optional, matching ignores spacing, punctuation and capitalisation, and the
    profile that comes back carries the contact details, the last four digits of the card kept
    on file, the postal code, the day the profile was first opened, whether it is a household or
    a business profile, and the store it is attached to. Where nothing matches, or where more
    than one profile does, that is said plainly so you can ask for one more detail. Finding a
    profile is not the same as proving who is on the line; verifying identity is a separate step.

    Args:
        customer_id: The customer reference number; leave "" if the caller cannot quote it.
        phone_number: The mobile number on the profile, ten digits with no separators; leave "" if not given.
        email: The email address on the profile, exactly as the caller says it; leave "" if not given.
        name: The customer's full name as the caller gives it; leave "" if not given.
        postal_code: The postal code of the service address, five digits; leave "" if not given.
        business_name: The registered name of the business on a business profile; leave "" if not given.
    """
    match = {k: v for k, v in {"customer_id": customer_id, "phone_number": phone_number,
                               "email": email, "name": name, "postal_code": postal_code,
                               "business_name": business_name}.items() if v}
    if not match:
        return "Error: give at least one detail — a customer reference number, or something the caller can state."
    rows = ctx.fuzzy_find("customers", **match)
    if not rows:
        return f"No customer profile matches {match}."
    if len(rows) > 1:
        return f"Error: {len(rows)} profiles match {match}; ask for one more detail to tell them apart."
    return str(rows[0])


@tool(owner="agent", rw="read")
def find_membership_holdings(ctx: ToolContext, membership_id: str = "", customer_id: str = "") -> str:
    """Retrieve the Circle membership a customer holds.

    Pull it by the membership reference number, or by the customer reference number to see the
    membership on that profile. The record shows the tier held and the day it took effect, where
    the membership stands in its life, the day it was taken out and the day it was activated, the
    term now being billed and the next renewal day, the billing frequency and whether renewal is
    automatic, the reward point balance, the unspent benefit credit, the dues still owed, how many
    household or business seats are in use, the store it was opened at, and how often it has been
    put back after lapsing.

    Args:
        membership_id: The membership reference number; leave "" if unknown.
        customer_id: The customer reference number, read from the customer profile; leave "" if unknown.
    """
    match = {k: v for k, v in {"membership_id": membership_id, "customer_id": customer_id}.items() if v}
    rows = ctx.find("membership_holdings", **match)
    return str(rows) if rows else f"No Circle membership records for {match}."


@tool(owner="agent", rw="read")
def find_membership_events(ctx: ToolContext, membership_event_id: str = "", membership_id: str = "",
                           customer_id: str = "", source_order_id: str = "") -> str:
    """Read the history booked against a Circle membership.

    These are the dated entries behind the balances: dues and fees billed for a named billing
    period, payments applied to a period, reward points earned on a purchase or a plan, points
    redeemed as a certificate or a discount, points swept at the end of their life, benefit
    credits granted for a membership year, and benefit credits spent against a charge. Retrieve
    them by the entry reference, by the membership, by the customer, or by the purchase the points
    were earned on. Each entry carries its amount or point movement, the tier the membership stood
    at, the channel it came through and the day it happened.

    Args:
        membership_event_id: The reference number of one membership history entry; leave "" if unknown.
        membership_id: The membership reference number; leave "" if unknown.
        customer_id: The customer reference number; leave "" if unknown.
        source_order_id: The purchase, plan or work order reference the points were earned on; leave "" if unknown.
    """
    match = {k: v for k, v in {"membership_event_id": membership_event_id, "membership_id": membership_id,
                               "customer_id": customer_id, "source_order_id": source_order_id}.items() if v}
    rows = ctx.find("membership_events", **match)
    return str(rows) if rows else f"No membership history entries for {match}."


@tool(owner="agent", rw="read")
def find_membership_change_requests(ctx: ToolContext, membership_change_request_id: str = "",
                                    customer_id: str = "", membership_id: str = "") -> str:
    """Retrieve the change requests raised against a Circle membership.

    A request records what the customer asked to have done with their membership — ending it,
    stepping down a tier, switching automatic renewal off, or taking a seat off the household —
    together with the day they asked it to take effect, the tier asked for on a step down, and how
    far the request has got: waiting for the customer to confirm, confirmed by them, or withdrawn.
    Look it up by the request reference, by the customer, or by the membership it concerns.

    Args:
        membership_change_request_id: The reference number of the request; leave "" if unknown.
        customer_id: The customer reference number; leave "" if unknown.
        membership_id: The membership reference number; leave "" if unknown.
    """
    match = {k: v for k, v in {"membership_change_request_id": membership_change_request_id,
                               "customer_id": customer_id, "membership_id": membership_id}.items() if v}
    rows = ctx.find("membership_change_requests", **match)
    return str(rows) if rows else f"No membership change requests for {match}."


@tool(owner="agent", rw="read")
def find_protection_plans(ctx: ToolContext, plan_id: str = "", customer_id: str = "") -> str:
    """Retrieve the ShieldCare protection plans a customer holds.

    Pull a single plan by its reference number, or every plan on a profile by the customer
    reference number. Each plan names the cover bought and where it stands in its life, the item
    it covers by serial, department, price and the day that item was bought, the order the item
    came from, the length of term sold and how the premium is collected, the day the plan was
    taken out and activated, the days cover starts and ends, the coverage still available, the
    premium and any claim deductible still owed, how many claims have been filed and how many
    repairs have been authorised on the item, whether the plan may move to a new owner, and where
    the customer asked work to be carried out.

    Args:
        plan_id: The protection plan reference number; leave "" if unknown.
        customer_id: The customer reference number; leave "" if unknown.
    """
    match = {k: v for k, v in {"plan_id": plan_id, "customer_id": customer_id}.items() if v}
    rows = ctx.find("protection_plans", **match)
    return str(rows) if rows else f"No ShieldCare plans for {match}."


@tool(owner="agent", rw="read")
def find_protection_events(ctx: ToolContext, protection_event_id: str = "", plan_id: str = "",
                           customer_id: str = "") -> str:
    """Read everything booked against a ShieldCare plan.

    These entries are the plan's working history: the cover credited when the term opened and any
    cover put back at an anniversary, premiums and fees billed for a named period, premiums paid,
    premiums returned, each claim opened with the peril reported and the days the incident happened
    and was reported, each adjudication with its outcome and how it is to be settled, each payout
    with the form the settlement took and who did the work, and claim deductibles billed and
    settled. Retrieve them by the entry reference, by the plan, or by the customer.

    Args:
        protection_event_id: The reference number of one plan history entry; leave "" if unknown.
        plan_id: The protection plan reference number; leave "" if unknown.
        customer_id: The customer reference number; leave "" if unknown.
    """
    match = {k: v for k, v in {"protection_event_id": protection_event_id, "plan_id": plan_id,
                               "customer_id": customer_id}.items() if v}
    rows = ctx.find("protection_events", **match)
    return str(rows) if rows else f"No protection plan history entries for {match}."


@tool(owner="agent", rw="read")
def find_protection_claim_intakes(ctx: ToolContext, protection_claim_intake_id: str = "",
                                  customer_id: str = "", plan_id: str = "") -> str:
    """Retrieve what was taken down when a protection claim was first reported.

    The intake carries the claim reference issued at the report, the peril and the incident day as
    the customer stated them, whether the customer has signed the statement of loss the claim
    needs or declined to, and which supporting documents have actually arrived — proof of purchase,
    a police report, both or none. Look it up by the intake reference, by the customer, or by the
    plan the incident was reported against.

    Args:
        protection_claim_intake_id: The reference number of the intake record; leave "" if unknown.
        customer_id: The customer reference number; leave "" if unknown.
        plan_id: The protection plan reference number; leave "" if unknown.
    """
    match = {k: v for k, v in {"protection_claim_intake_id": protection_claim_intake_id,
                               "customer_id": customer_id, "plan_id": plan_id}.items() if v}
    rows = ctx.find("protection_claim_intakes", **match)
    return str(rows) if rows else f"No claim intake records for {match}."


@tool(owner="agent", rw="read")
def find_return_authorizations(ctx: ToolContext, return_authorization_id: str = "", customer_id: str = "",
                               order_line_reference: str = "") -> str:
    """Retrieve the return authorisations raised for a customer.

    An authorisation is the whole story of one line going back: the schedule it is handled under
    and where it stands, the order and the single order line it is against, the item by stock
    number and serial with its department, the days the item was bought and delivered, the price
    paid and the units coming back, the reason the customer gave and the way the item is to
    travel, the grade the inspection recorded, the refund still to pay and any restocking fee
    still outstanding, how the item was paid for and how the refund is to go back, and the place
    the item is to be restocked. Retrieve by the authorisation reference, by the customer, or by
    the order line.

    Args:
        return_authorization_id: The return authorisation reference number; leave "" if unknown.
        customer_id: The customer reference number; leave "" if unknown.
        order_line_reference: The reference of the single order line being returned; leave "" if unknown.
    """
    match = {k: v for k, v in {"return_authorization_id": return_authorization_id,
                               "customer_id": customer_id,
                               "order_line_reference": order_line_reference}.items() if v}
    rows = ctx.find("return_authorizations", **match)
    return str(rows) if rows else f"No return authorisations for {match}."


@tool(owner="agent", rw="read")
def find_return_events(ctx: ToolContext, return_event_id: str = "", return_authorization_id: str = "",
                       customer_id: str = "") -> str:
    """Read what has been booked against a return.

    These entries show how the return was worked: the condition the item was graded at with
    anything missing from the box and the deduction taken for it, restocking fees charged and
    waived with the ground for the waiver, each component of the original charge authorised for
    refund, money actually paid out and the way it went, amounts kept back to settle what the
    customer owed, an exchange item issued in place of a refund, and any prepaid label or
    collection booked with its carrier, tracking reference and last usable day. Retrieve by the
    entry reference, by the authorisation, or by the customer.

    Args:
        return_event_id: The reference number of one return history entry; leave "" if unknown.
        return_authorization_id: The return authorisation reference number; leave "" if unknown.
        customer_id: The customer reference number; leave "" if unknown.
    """
    match = {k: v for k, v in {"return_event_id": return_event_id,
                               "return_authorization_id": return_authorization_id,
                               "customer_id": customer_id}.items() if v}
    rows = ctx.find("return_events", **match)
    return str(rows) if rows else f"No return history entries for {match}."


@tool(owner="agent", rw="read")
def find_return_pickup_requests(ctx: ToolContext, return_pickup_request_id: str = "", customer_id: str = "",
                                return_authorization_id: str = "") -> str:
    """Retrieve the collection arrangements made for a return.

    A collection request records the day and the part of the day the customer asked for the item to
    be picked up, whether the customer has confirmed the slot or cancelled it, and how many times
    the collection has already been moved at their request. Look it up by the request reference, by
    the customer, or by the return authorisation it belongs to.

    Args:
        return_pickup_request_id: The reference number of the collection request; leave "" if unknown.
        customer_id: The customer reference number; leave "" if unknown.
        return_authorization_id: The return authorisation reference number; leave "" if unknown.
    """
    match = {k: v for k, v in {"return_pickup_request_id": return_pickup_request_id,
                               "customer_id": customer_id,
                               "return_authorization_id": return_authorization_id}.items() if v}
    rows = ctx.find("return_pickup_requests", **match)
    return str(rows) if rows else f"No collection requests for {match}."


@tool(owner="agent", rw="read")
def find_tradein_agreements(ctx: ToolContext, tradein_agreement_id: str = "", customer_id: str = "") -> str:
    """Retrieve the Renew trade-in agreements a customer holds.

    Each agreement carries the programme it was written under and where it stands, the day the
    quote was given and the last day it may be accepted, the days the customer accepted, the
    device arrived, the appraisal was recorded and the credit was issued, the device by make,
    model and serial with its kind and how many units the agreement covers, the condition the
    customer declared beside the condition the appraisal found, whether the device is locked, the
    amount quoted, the amount the appraisal supports and the amount finally credited, any
    guaranteed minimum written into the agreement, the credit still unspent and its last spendable
    day, any handling or freight fee still outstanding, how the device was to travel, how far data
    erasure has got, the purchase the trade is set against and the promotion it was written under.

    Args:
        tradein_agreement_id: The trade-in agreement reference number; leave "" if unknown.
        customer_id: The customer reference number; leave "" if unknown.
    """
    match = {k: v for k, v in {"tradein_agreement_id": tradein_agreement_id,
                               "customer_id": customer_id}.items() if v}
    rows = ctx.find("tradein_agreements", **match)
    return str(rows) if rows else f"No Renew trade-in agreements for {match}."


@tool(owner="agent", rw="read")
def find_tradein_events(ctx: ToolContext, tradein_event_id: str = "", tradein_agreement_id: str = "",
                        customer_id: str = "") -> str:
    """Read what has been booked against a Renew trade-in.

    These entries hold the working detail behind the figures: a revised offer with the amount it
    stands at and the reason it moved, credit issued and the form it was put into the customer's
    hands in, a promotional or membership uplift with the promotion it was paid under, credit spent
    against a named purchase, credit written off at the end of its life, handling and freight fees
    charged and waived, and the erasure of the data with the method used and the certificate
    issued. Retrieve by the entry reference, by the agreement, or by the customer.

    Args:
        tradein_event_id: The reference number of one trade-in history entry; leave "" if unknown.
        tradein_agreement_id: The trade-in agreement reference number; leave "" if unknown.
        customer_id: The customer reference number; leave "" if unknown.
    """
    match = {k: v for k, v in {"tradein_event_id": tradein_event_id,
                               "tradein_agreement_id": tradein_agreement_id,
                               "customer_id": customer_id}.items() if v}
    rows = ctx.find("tradein_events", **match)
    return str(rows) if rows else f"No trade-in history entries for {match}."


@tool(owner="agent", rw="read")
def find_tradein_shipping_requests(ctx: ToolContext, tradein_shipping_request_id: str = "",
                                   customer_id: str = "", tradein_agreement_id: str = "") -> str:
    """Retrieve how a traded device was arranged to reach the retailer.

    The request records the way the customer chose to send the device, the day they asked for it to
    be collected, how many units they said would be in the shipment, and whether they have
    consented to handing the device over and to having the data on it destroyed, or have withdrawn
    that consent. Look it up by the request reference, by the customer, or by the agreement.

    Args:
        tradein_shipping_request_id: The reference number of the shipping request; leave "" if unknown.
        customer_id: The customer reference number; leave "" if unknown.
        tradein_agreement_id: The trade-in agreement reference number; leave "" if unknown.
    """
    match = {k: v for k, v in {"tradein_shipping_request_id": tradein_shipping_request_id,
                               "customer_id": customer_id,
                               "tradein_agreement_id": tradein_agreement_id}.items() if v}
    rows = ctx.find("tradein_shipping_requests", **match)
    return str(rows) if rows else f"No trade-in shipping requests for {match}."


@tool(owner="agent", rw="read")
def find_service_agreements(ctx: ToolContext, service_agreement_id: str = "", customer_id: str = "") -> str:
    """Retrieve the TechWorks work orders and care agreements a customer holds.

    Each one names the service it is handled under and where the job stands, what the work is for,
    the item by stock number and serial with its department, the postal code the work is at, the
    order the item or the service was bought on, any protection plan the work is claimed under, the
    days the work was asked for, booked, started, held for parts, finished or called off, the
    technician or crew assigned, the visits still included, the service charges still outstanding,
    how often the slot has been moved, the last day an annual agreement runs, whether the job is in
    the priority queue and whether it is being done under cover rather than for a charge.

    Args:
        service_agreement_id: The work order or care agreement reference number; leave "" if unknown.
        customer_id: The customer reference number; leave "" if unknown.
    """
    match = {k: v for k, v in {"service_agreement_id": service_agreement_id,
                               "customer_id": customer_id}.items() if v}
    rows = ctx.find("service_agreements", **match)
    return str(rows) if rows else f"No TechWorks work orders for {match}."


@tool(owner="agent", rw="read")
def find_service_events(ctx: ToolContext, service_event_id: str = "", service_agreement_id: str = "",
                        customer_id: str = "") -> str:
    """Read what has been booked against a TechWorks job.

    These entries are the job's working record: included visits granted and the ground they were
    granted on, included visits used by a visit actually carried out, labour with the hours and the
    rate it was charged at, parts fitted by part number, trip charges, no-show fees, reschedule and
    cancellation fees, haul-away and diagnostic fees and surcharges, payments received, charges
    written off with the ground for the write-off, parts ordered with the day they are expected,
    what each diagnosis found, and any rework raised against work already signed off. Retrieve by
    the entry reference, by the job, or by the customer.

    Args:
        service_event_id: The reference number of one service history entry; leave "" if unknown.
        service_agreement_id: The work order reference number; leave "" if unknown.
        customer_id: The customer reference number; leave "" if unknown.
    """
    match = {k: v for k, v in {"service_event_id": service_event_id,
                               "service_agreement_id": service_agreement_id,
                               "customer_id": customer_id}.items() if v}
    rows = ctx.find("service_events", **match)
    return str(rows) if rows else f"No service history entries for {match}."


@tool(owner="agent", rw="read")
def find_service_appointment_requests(ctx: ToolContext, service_appointment_request_id: str = "",
                                      customer_id: str = "", service_agreement_id: str = "") -> str:
    """Retrieve the appointment arrangements made for a TechWorks job.

    The request records the day and the part of the day the customer asked for, whether they have
    confirmed the slot offered or cancelled it, whether they say the site is ready for the crew,
    and the access condition noted for the address — restricted parking, stairs only, a gated
    community, or a loading dock needed. Look it up by the request reference, by the customer, or
    by the job it belongs to.

    Args:
        service_appointment_request_id: The reference number of the appointment request; leave "" if unknown.
        customer_id: The customer reference number; leave "" if unknown.
        service_agreement_id: The work order reference number; leave "" if unknown.
    """
    match = {k: v for k, v in {"service_appointment_request_id": service_appointment_request_id,
                               "customer_id": customer_id,
                               "service_agreement_id": service_agreement_id}.items() if v}
    rows = ctx.find("service_appointment_requests", **match)
    return str(rows) if rows else f"No appointment requests for {match}."


@tool(owner="agent", rw="read")
def find_credit_accounts(ctx: ToolContext, credit_account_id: str = "", customer_id: str = "") -> str:
    """Retrieve the store credit and financing accounts a customer holds.

    Each account names the credit product held and where the account stands, the days it was
    applied for, opened and closed, the day it first fell behind if it ever did, the spending limit
    set, the amount owed, the unspent store credit sitting on it, the day of the month the
    statement closes, the day the current minimum payment falls due and what that payment is, any
    promotional financing plan running with the day it ends, whether payment is collected
    automatically, whether statements are electronic, and the day the last payment came in.

    Args:
        credit_account_id: The account reference number; leave "" if unknown.
        customer_id: The customer reference number; leave "" if unknown.
    """
    match = {k: v for k, v in {"credit_account_id": credit_account_id,
                               "customer_id": customer_id}.items() if v}
    rows = ctx.find("credit_accounts", **match)
    return str(rows) if rows else f"No store credit or financing accounts for {match}."


@tool(owner="agent", rw="read")
def find_credit_events(ctx: ToolContext, credit_event_id: str = "", credit_account_id: str = "",
                       customer_id: str = "") -> str:
    """Read the entries behind a store credit or financing account.

    These are the dated movements: amounts drawn by a purchase, a service charge or a premium with
    what they were spent on, payments received, interest charged for a statement period at the rate
    applied, late, annual, returned payment, over-limit and paper statement fees, refunds credited
    from a returned purchase, store credit posted with the reason it was posted, store credit spent
    against a purchase, store credit written off at the end of its life, and each statement closing
    with the least payment it asked for. Retrieve by the entry reference, by the account, or by the
    customer.

    Args:
        credit_event_id: The reference number of one account entry; leave "" if unknown.
        credit_account_id: The account reference number; leave "" if unknown.
        customer_id: The customer reference number; leave "" if unknown.
    """
    match = {k: v for k, v in {"credit_event_id": credit_event_id, "credit_account_id": credit_account_id,
                               "customer_id": customer_id}.items() if v}
    rows = ctx.find("credit_events", **match)
    return str(rows) if rows else f"No account entries for {match}."


@tool(owner="agent", rw="read")
def find_credit_limit_requests(ctx: ToolContext, credit_limit_request_id: str = "", customer_id: str = "",
                               credit_account_id: str = "") -> str:
    """Retrieve requests to change the spending limit on a credit account.

    Each request records the limit the customer asked for, the annual income they stated in support
    of it, whether they have consented to the credit check the request needs or have withdrawn that
    consent, and where the request has got to: still under review, approved, or declined. Look it up
    by the request reference, by the customer, or by the account it concerns.

    Args:
        credit_limit_request_id: The reference number of the request; leave "" if unknown.
        customer_id: The customer reference number; leave "" if unknown.
        credit_account_id: The account reference number; leave "" if unknown.
    """
    match = {k: v for k, v in {"credit_limit_request_id": credit_limit_request_id,
                               "customer_id": customer_id,
                               "credit_account_id": credit_account_id}.items() if v}
    rows = ctx.find("credit_limit_requests", **match)
    return str(rows) if rows else f"No limit change requests for {match}."


@tool(owner="agent", rw="read")
def find_purchase_orders(ctx: ToolContext, purchase_order_id: str = "", customer_id: str = "") -> str:
    """Retrieve the purchase orders a customer has placed.

    Each order names the fulfilment service chosen and where the order stands, the day it was
    placed and the day the goods were promised, the slot booked for delivery or collection and how
    often it has moved, the days the goods left and were handed over, the day the order was
    cancelled and the day it first went to awaiting stock, the main item by department, stock
    number and allocated serial, how many lines it carries, the total billed and the amount still
    unpaid, the postal code the goods are going to or the store holding them, how the order is
    being paid for, and whether haul-away and installation were bought with it.

    Args:
        purchase_order_id: The order reference number; leave "" if unknown.
        customer_id: The customer reference number; leave "" if unknown.
    """
    match = {k: v for k, v in {"purchase_order_id": purchase_order_id,
                               "customer_id": customer_id}.items() if v}
    rows = ctx.find("purchase_orders", **match)
    return str(rows) if rows else f"No purchase orders for {match}."


@tool(owner="agent", rw="read")
def find_order_events(ctx: ToolContext, order_event_id: str = "", purchase_order_id: str = "",
                      customer_id: str = "") -> str:
    """Read what has been booked against a purchase order.

    These entries show how the order was billed and how the goods travelled: merchandise lines with
    the shelf price and the units, the tax on them, delivery, installation, haul-away and recycling
    charges, reschedule, redelivery, storage, restock and pallet fees, money taken and the way it
    was taken, amounts credited back as a price match with the competitor and the price matched, as
    a promotional discount, a goodwill credit, a cancellation reversal, a late delivery credit or a
    damage allowance, notices that an item had gone out of stock with the day it was expected, each
    attempt at handing the goods over and how it ended, and what was taken away at delivery.

    Args:
        order_event_id: The reference number of one order entry; leave "" if unknown.
        purchase_order_id: The order reference number; leave "" if unknown.
        customer_id: The customer reference number; leave "" if unknown.
    """
    match = {k: v for k, v in {"order_event_id": order_event_id, "purchase_order_id": purchase_order_id,
                               "customer_id": customer_id}.items() if v}
    rows = ctx.find("order_events", **match)
    return str(rows) if rows else f"No order entries for {match}."


@tool(owner="agent", rw="read")
def find_order_change_requests(ctx: ToolContext, order_change_request_id: str = "", customer_id: str = "",
                               purchase_order_id: str = "") -> str:
    """Retrieve requests to change a purchase order.

    Each request records what the customer asked for — cancelling the order, moving the slot,
    changing the address, adding haul-away or adding installation — the day they asked it to take
    effect, the part of the day they wanted on a move, and whether they have confirmed the change
    or withdrawn it. Look it up by the request reference, by the customer, or by the order.

    Args:
        order_change_request_id: The reference number of the request; leave "" if unknown.
        customer_id: The customer reference number; leave "" if unknown.
        purchase_order_id: The order reference number; leave "" if unknown.
    """
    match = {k: v for k, v in {"order_change_request_id": order_change_request_id,
                               "customer_id": customer_id,
                               "purchase_order_id": purchase_order_id}.items() if v}
    rows = ctx.find("order_change_requests", **match)
    return str(rows) if rows else f"No order change requests for {match}."


@tool(owner="agent", rw="read")
def find_identity_verifications(ctx: ToolContext, verification_id: str = "", customer_id: str = "") -> str:
    """Check whether the caller on a profile has already been verified on this call.

    The record says whether identity verification has passed for that profile and the moment the
    most recent attempt was made. Once a profile has passed, it stays passed. Look it up by the
    verification reference or by the customer reference number.

    Args:
        verification_id: The reference number of the verification record; leave "" if unknown.
        customer_id: The customer reference number; leave "" if unknown.
    """
    match = {k: v for k, v in {"verification_id": verification_id, "customer_id": customer_id}.items() if v}
    rows = ctx.find("identity_verifications", **match)
    return str(rows) if rows else f"No verification records for {match}."


@tool(owner="agent", rw="read")
def find_human_handoffs(ctx: ToolContext, handoff_id: str = "", customer_id: str = "") -> str:
    """Check whether a customer has already been passed to a human representative.

    The record names the customer, the ground the handoff was recorded on, and the moment it was
    made. Look it up by the handoff reference or by the customer reference number.

    Args:
        handoff_id: The reference number of the handoff record; leave "" if unknown.
        customer_id: The customer reference number; leave "" if unknown.
    """
    match = {k: v for k, v in {"handoff_id": handoff_id, "customer_id": customer_id}.items() if v}
    rows = ctx.find("human_handoffs", **match)
    return str(rows) if rows else f"No handoff records for {match}."


@tool(owner="agent", rw="write")
def verify_customer_identity(ctx: ToolContext, customer_id: str, phone_number: str = "", email: str = "",
                             card_last4: str = "", postal_code: str = "", profile_opened_date: str = "") -> str:
    """Verify who is on the line and record the outcome, before anything is looked into or moved on
    the account.

    The comparison is done here rather than judged by you: each piece of information the caller
    states is set against the profile on file, and verification passes once at least two of them
    agree. The customer reference number only fetches the profile and never counts as one of the
    two. Callers usually remember only some of what is on file, so pass the values they actually
    give, word for word as they give them, and leave the rest empty. The outcome is kept on the
    profile, and where a first attempt fell short and a later one passes with more information, the
    pass stands.

    Args:
        customer_id: The customer reference number, read from the customer profile. Always required, and used only to fetch that profile.
        phone_number: The mobile number the caller states, ten digits with no separators; leave "" if not stated.
        email: The email address the caller states, exactly as given; leave "" if not stated.
        card_last4: The last four digits of the card on file, as the caller states them, exactly four digits; leave "" if not stated.
        postal_code: The postal code of the service address, five digits; leave "" if not stated.
        profile_opened_date: The day the caller says the profile was first opened, as YYYY-MM-DD; leave "" if not stated.
    """
    if not customer_id:
        return "Error: customer_id is required; find the customer profile first and pass its reference number."
    rows = ctx.find("customers", customer_id=customer_id)
    if not rows:
        return f"Error: no customer profile {customer_id}; cannot verify."
    rec = rows[0]
    # The locator is deliberately absent from `supplied`: fetching a profile is not proving identity.
    supplied = {"phone_number": phone_number, "email": email, "card_last4": card_last4,
                "postal_code": postal_code, "profile_opened_date": profile_opened_date}
    matched = sum(1 for field, value in supplied.items() if value and str(rec.get(field)) == str(value))
    verified = matched >= VERIFICATION_MATCH_THRESHOLD
    rid = ctx.make_id("ver_", customer_id)
    # Only the reproducible outcome is stored, never the match count. Upsert and never downgrade,
    # so a caller who fails once and then passes with more detail ends up recorded as verified.
    prior = ctx.find("identity_verifications", verification_id=rid)
    verified = verified or bool(prior and prior[0].get("verified"))
    if prior:
        ctx.update("identity_verifications", rid, verified=verified, verified_at=ctx.now())
    else:
        ctx.create("identity_verifications", rid, verification_id=rid, customer_id=customer_id,
                   verified=verified, verified_at=ctx.now())
    return (f"Identity verified for {customer_id} ({matched} detail(s) matched the profile)." if verified
            else f"Identity NOT verified for {customer_id} (only {matched} of the {VERIFICATION_MATCH_THRESHOLD} "
                 "required details matched). Ask the caller for another detail on file and try again.")


@tool(owner="agent", rw="write")
def transfer_to_human_agent(ctx: ToolContext, customer_id: str, reason: str) -> str:
    """Pass the customer to a human representative and record the handoff.

    There are two situations for this. Where the published rules give no way to settle what the
    customer is asking for — the request falls outside what any policy decides — record it as
    POLICY_NOT_COVERED. Where the customer has explicitly asked to speak to a person at least
    twice in the conversation, record it as CUSTOMER_REQUESTED and hand them over even if the
    matter could have been settled.

    Args:
        customer_id: The customer reference number, read from the customer profile, which must exist.
        reason: The ground for the handoff, one of POLICY_NOT_COVERED or CUSTOMER_REQUESTED, never anything else.
            POLICY_NOT_COVERED — no published rule can resolve the request;
            CUSTOMER_REQUESTED — the customer has asked for a person at least twice.
    """
    allowed = {"POLICY_NOT_COVERED", "CUSTOMER_REQUESTED"}
    if reason not in allowed:
        return f"Error: unknown handoff reason '{reason}'. Valid: {', '.join(sorted(allowed))}."
    if not ctx.find("customers", customer_id=customer_id):
        return f"Error: no customer profile {customer_id}; cannot record the handoff."
    rid = ctx.make_id("hof_", customer_id, reason)
    ctx.create("human_handoffs", rid, handoff_id=rid, customer_id=customer_id,
               reason=reason, created_at=ctx.now())
    return f"Handed over to a human representative for {customer_id} ({reason})."

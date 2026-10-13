"""Shared tools for env_0040_pet_supplies_retailer (Tailwise Pet Co. customer care).

Every tool in this file is a share tool: always present in its owner's tool list.
It holds the record-lookup layer (one finder per record type; the customer finder
doubles as the identity entry), the identity-verification write and the
transfer-to-human write. Customer-originated writes live in each difficulty's
task_tools.py as hidden user tools.

Scenario operational constants built in here:
  K = 2  identity credentials must match for verification to pass
         (registered mobile number, registered email, billing ZIP code,
          last four digits of the card on file, date the profile was opened);
  R = 2  explicit requests for a human representative before a
         CUSTOMER_REQUESTED transfer applies.
"""

from erlbench import ToolContext, tool


@tool(owner="agent", rw="read")
def find_customers(ctx: ToolContext, customer_id: str = "", name: str = "",
                   phone_number: str = "", email: str = "", home_store_id: str = "") -> str:
    """Look up a Tailwise customer profile to establish whose account this contact is about.

    You can search by the customer reference number, or by what the caller naturally tells
    you: the mobile number, the email address or the full name on the profile. Every
    criterion is optional; supply whichever you have, and add another one if more than one
    profile matches. The returned profile shows the contact details, billing ZIP code, last
    four digits of the card on file, the date the profile was opened, the shipping state,
    whether the shipping address is inside the refrigerated delivery zone and the preferred
    store. Finding a profile does not verify the caller's identity.

    Args:
        customer_id: The customer reference number, if already known; leave "" if unknown.
        name: The full name on the profile as the caller states it; leave "" if not provided.
        phone_number: The registered mobile number, 10 digits; leave "" if not provided.
        email: The registered email address; leave "" if not provided.
        home_store_id: The reference number of the customer's preferred store, to narrow a search; leave "" if unknown.
    """
    match = {k: v for k, v in {"customer_id": customer_id, "name": name,
                               "phone_number": phone_number, "email": email,
                               "home_store_id": home_store_id}.items() if v}
    if not match:
        return "Error: provide at least one reference number or profile detail to find the customer."
    rows = ctx.fuzzy_find("customers", **match)
    if not rows:
        return f"No customer matches {match}."
    if len(rows) > 1:
        return f"Error: {len(rows)} customers match {match}; ask for one more detail to tell them apart."
    return str(rows[0])


@tool(owner="agent", rw="read")
def find_pets(ctx: ToolContext, pet_id: str = "", customer_id: str = "", primary_vet_id: str = "") -> str:
    """Look up the pet profiles kept on a customer's account: species, breed, date of
    birth, latest weight and size band, coat type, behaviour flag, vaccination expiry
    dates and the veterinarian of record.

    Every criterion is optional; give whichever reference numbers you already hold.
    All matching records are returned with their full details, or a short notice when
    nothing matches.

    Args:
        pet_id: The pet profile reference number; leave "" if unknown.
        customer_id: The customer reference number; leave "" if unknown.
        primary_vet_id: The reference number of the pet's veterinarian of record; leave "" if unknown.
    """
    match = {k: v for k, v in {"pet_id": pet_id, "customer_id": customer_id, "primary_vet_id": primary_vet_id}.items() if v}
    rows = ctx.find("pets", **match)
    return str(rows) if rows else f"No pets records for {match}."


@tool(owner="agent", rw="read")
def find_veterinarians(ctx: ToolContext, vet_id: str = "") -> str:
    """Look up a veterinarian on file: practice name and phone, license state, DEA
    registration, and whether the veterinarian practises inside a Tailwise Vet Clinic.

    Every criterion is optional; give whichever reference numbers you already hold.
    All matching records are returned with their full details, or a short notice when
    nothing matches.

    Args:
        vet_id: The veterinarian reference number; leave "" if unknown.
    """
    match = {k: v for k, v in {"vet_id": vet_id}.items() if v}
    rows = ctx.find("veterinarians", **match)
    return str(rows) if rows else f"No veterinarians records for {match}."


@tool(owner="agent", rw="read")
def find_stores(ctx: ToolContext, store_id: str = "") -> str:
    """Look up a Tailwise store: name, city and state, and whether it has a grooming salon,
    a vet clinic and training classes.

    Every criterion is optional; give whichever reference numbers you already hold.
    All matching records are returned with their full details, or a short notice when
    nothing matches.

    Args:
        store_id: The store reference number; leave "" if unknown.
    """
    match = {k: v for k, v in {"store_id": store_id}.items() if v}
    rows = ctx.find("stores", **match)
    return str(rows) if rows else f"No stores records for {match}."


@tool(owner="agent", rw="read")
def find_autoship_subscriptions(ctx: ToolContext, autoship_id: str = "", customer_id: str = "", pet_id: str = "", rx_prescription_id: str = "") -> str:
    """Look up a customer's Autoship subscriptions: program, item, quantity, price,
    delivery frequency, next ship date, pause and cancellation dates, linked pet and
    prescription, and the net amount billed so far.

    Every criterion is optional; give whichever reference numbers you already hold.
    All matching records are returned with their full details, or a short notice when
    nothing matches.

    Args:
        autoship_id: The Autoship subscription reference number; leave "" if unknown.
        customer_id: The customer reference number; leave "" if unknown.
        pet_id: The pet profile reference number; leave "" if unknown.
        rx_prescription_id: The prescription reference number; leave "" if unknown.
    """
    match = {k: v for k, v in {"autoship_id": autoship_id, "customer_id": customer_id, "pet_id": pet_id, "rx_prescription_id": rx_prescription_id}.items() if v}
    rows = ctx.find("autoship_subscriptions", **match)
    return str(rows) if rows else f"No autoship subscriptions records for {match}."


@tool(owner="agent", rw="read")
def find_autoship_events(ctx: ToolContext, autoship_event_id: str = "", autoship_id: str = "", customer_id: str = "", original_event_id: str = "", rx_prescription_id: str = "") -> str:
    """Look up the Autoship history of a subscription: charged shipments with their
    discounts and fees, skips, payment declines, claim refunds and replacement
    shipments.

    Every criterion is optional; give whichever reference numbers you already hold.
    All matching records are returned with their full details, or a short notice when
    nothing matches.

    Args:
        autoship_event_id: The reference number of the Autoship history entry itself; leave "" if unknown.
        autoship_id: The Autoship subscription reference number; leave "" if unknown.
        customer_id: The customer reference number; leave "" if unknown.
        original_event_id: The reference number of the original entry (charge, fill, booking, visit, order line or fee) this entry refers to; leave "" if unknown.
        rx_prescription_id: The prescription reference number; leave "" if unknown.
    """
    match = {k: v for k, v in {"autoship_event_id": autoship_event_id, "autoship_id": autoship_id, "customer_id": customer_id, "original_event_id": original_event_id, "rx_prescription_id": rx_prescription_id}.items() if v}
    rows = ctx.find("autoship_events", **match)
    return str(rows) if rows else f"No autoship events records for {match}."


@tool(owner="agent", rw="read")
def find_rx_prescriptions(ctx: ToolContext, rx_prescription_id: str = "", customer_id: str = "", pet_id: str = "", vet_id: str = "", renewal_of_rx_id: str = "") -> str:
    """Look up the prescriptions on file with Tailwise Pharmacy: medication and strength,
    pet and prescribing veterinarian, class, how the prescription arrived, authorization
    and expiry dates, fills authorized and remaining, and any denial reason.

    Every criterion is optional; give whichever reference numbers you already hold.
    All matching records are returned with their full details, or a short notice when
    nothing matches.

    Args:
        rx_prescription_id: The prescription reference number; leave "" if unknown.
        customer_id: The customer reference number; leave "" if unknown.
        pet_id: The pet profile reference number; leave "" if unknown.
        vet_id: The veterinarian reference number; leave "" if unknown.
        renewal_of_rx_id: The reference number of the prescription being renewed; leave "" if unknown.
    """
    match = {k: v for k, v in {"rx_prescription_id": rx_prescription_id, "customer_id": customer_id, "pet_id": pet_id, "vet_id": vet_id, "renewal_of_rx_id": renewal_of_rx_id}.items() if v}
    rows = ctx.find("rx_prescriptions", **match)
    return str(rows) if rows else f"No rx prescriptions records for {match}."


@tool(owner="agent", rw="read")
def find_rx_events(ctx: ToolContext, rx_event_id: str = "", rx_prescription_id: str = "", customer_id: str = "", original_event_id: str = "") -> str:
    """Look up the pharmacy history of a prescription: dispensed fills with their charges,
    early-refill overrides, remakes and refunds for dispensing errors, returned diet
    products and restored fills.

    Every criterion is optional; give whichever reference numbers you already hold.
    All matching records are returned with their full details, or a short notice when
    nothing matches.

    Args:
        rx_event_id: The reference number of the pharmacy history entry itself; leave "" if unknown.
        rx_prescription_id: The prescription reference number; leave "" if unknown.
        customer_id: The customer reference number; leave "" if unknown.
        original_event_id: The reference number of the original entry (charge, fill, booking, visit, order line or fee) this entry refers to; leave "" if unknown.
    """
    match = {k: v for k, v in {"rx_event_id": rx_event_id, "rx_prescription_id": rx_prescription_id, "customer_id": customer_id, "original_event_id": original_event_id}.items() if v}
    rows = ctx.find("rx_events", **match)
    return str(rows) if rows else f"No rx events records for {match}."


@tool(owner="agent", rw="read")
def find_rx_authorization_requests(ctx: ToolContext, auth_request_id: str = "", customer_id: str = "", rx_prescription_id: str = "", vet_id: str = "") -> str:
    """Look up the authorization requests the pharmacy has sent to veterinarians or
    transferring pharmacies, with channel, attempt number, dates and outcome.

    Every criterion is optional; give whichever reference numbers you already hold.
    All matching records are returned with their full details, or a short notice when
    nothing matches.

    Args:
        auth_request_id: The reference number of the authorization request itself; leave "" if unknown.
        customer_id: The customer reference number; leave "" if unknown.
        rx_prescription_id: The prescription reference number; leave "" if unknown.
        vet_id: The veterinarian reference number; leave "" if unknown.
    """
    match = {k: v for k, v in {"auth_request_id": auth_request_id, "customer_id": customer_id, "rx_prescription_id": rx_prescription_id, "vet_id": vet_id}.items() if v}
    rows = ctx.find("rx_authorization_requests", **match)
    return str(rows) if rows else f"No rx authorization requests records for {match}."


@tool(owner="agent", rw="read")
def find_groom_passes(ctx: ToolContext, groom_pass_id: str = "", customer_id: str = "", pet_id: str = "", store_id: str = "") -> str:
    """Look up a customer's grooming passes: pass name, pet, size class at purchase, price
    paid and discount, purchase and expiry dates, monthly billing date for Groom Club
    Monthly, visits purchased and remaining, and whether the one-time extension was
    used.

    Every criterion is optional; give whichever reference numbers you already hold.
    All matching records are returned with their full details, or a short notice when
    nothing matches.

    Args:
        groom_pass_id: The grooming pass reference number; leave "" if unknown.
        customer_id: The customer reference number; leave "" if unknown.
        pet_id: The pet profile reference number; leave "" if unknown.
        store_id: The store reference number; leave "" if unknown.
    """
    match = {k: v for k, v in {"groom_pass_id": groom_pass_id, "customer_id": customer_id, "pet_id": pet_id, "store_id": store_id}.items() if v}
    rows = ctx.find("groom_passes", **match)
    return str(rows) if rows else f"No groom passes records for {match}."


@tool(owner="agent", rw="read")
def find_groom_events(ctx: ToolContext, groom_event_id: str = "", groom_pass_id: str = "", customer_id: str = "", pet_id: str = "", store_id: str = "", original_event_id: str = "") -> str:
    """Look up the salon history of a grooming pass: appointments booked and cancelled,
    completed visits with every surcharge and add-on, no-shows, late-cancellation fees
    and forfeits, redos, Groom Club monthly charges and declines, and refunds.

    Every criterion is optional; give whichever reference numbers you already hold.
    All matching records are returned with their full details, or a short notice when
    nothing matches.

    Args:
        groom_event_id: The reference number of the salon history entry itself; leave "" if unknown.
        groom_pass_id: The grooming pass reference number; leave "" if unknown.
        customer_id: The customer reference number; leave "" if unknown.
        pet_id: The pet profile reference number; leave "" if unknown.
        store_id: The store reference number; leave "" if unknown.
        original_event_id: The reference number of the original entry (charge, fill, booking, visit, order line or fee) this entry refers to; leave "" if unknown.
    """
    match = {k: v for k, v in {"groom_event_id": groom_event_id, "groom_pass_id": groom_pass_id, "customer_id": customer_id, "pet_id": pet_id, "store_id": store_id, "original_event_id": original_event_id}.items() if v}
    rows = ctx.find("groom_events", **match)
    return str(rows) if rows else f"No groom events records for {match}."


@tool(owner="agent", rw="read")
def find_groom_consents(ctx: ToolContext, consent_id: str = "", customer_id: str = "", groom_pass_id: str = "", pet_id: str = "", original_event_id: str = "") -> str:
    """Look up the owner consents recorded for grooming appointments, such as agreement to
    a shave-down or to muzzle handling, with the decision and when it was given.

    Every criterion is optional; give whichever reference numbers you already hold.
    All matching records are returned with their full details, or a short notice when
    nothing matches.

    Args:
        consent_id: The reference number of the consent record itself; leave "" if unknown.
        customer_id: The customer reference number; leave "" if unknown.
        groom_pass_id: The grooming pass reference number; leave "" if unknown.
        pet_id: The pet profile reference number; leave "" if unknown.
        original_event_id: The reference number of the original entry (charge, fill, booking, visit, order line or fee) this entry refers to; leave "" if unknown.
    """
    match = {k: v for k, v in {"consent_id": consent_id, "customer_id": customer_id, "groom_pass_id": groom_pass_id, "pet_id": pet_id, "original_event_id": original_event_id}.items() if v}
    rows = ctx.find("groom_consents", **match)
    return str(rows) if rows else f"No groom consents records for {match}."


@tool(owner="agent", rw="read")
def find_member_memberships(ctx: ToolContext, membership_id: str = "", customer_id: str = "") -> str:
    """Look up a customer's Pals Rewards membership: tier and status, when the tier took
    effect and why it last changed, paid term dates, next billing date and auto-renewal,
    trial and cancellation dates, points balance and perk credit balance.

    Every criterion is optional; give whichever reference numbers you already hold.
    All matching records are returned with their full details, or a short notice when
    nothing matches.

    Args:
        membership_id: The Pals Rewards membership reference number; leave "" if unknown.
        customer_id: The customer reference number; leave "" if unknown.
    """
    match = {k: v for k, v in {"membership_id": membership_id, "customer_id": customer_id}.items() if v}
    rows = ctx.find("member_memberships", **match)
    return str(rows) if rows else f"No member memberships records for {match}."


@tool(owner="agent", rw="read")
def find_member_events(ctx: ToolContext, member_event_id: str = "", membership_id: str = "", customer_id: str = "", source_event_id: str = "", pet_id: str = "", original_event_id: str = "") -> str:
    """Look up the rewards history of a membership: points earned, reversed, awarded as
    bonuses, converted to certificates and expired; certificates issued and reissued;
    membership fees charged, declined and refunded; and perk credits granted and used.

    Every criterion is optional; give whichever reference numbers you already hold.
    All matching records are returned with their full details, or a short notice when
    nothing matches.

    Args:
        member_event_id: The reference number of the rewards history entry itself; leave "" if unknown.
        membership_id: The Pals Rewards membership reference number; leave "" if unknown.
        customer_id: The customer reference number; leave "" if unknown.
        source_event_id: The reference number of the purchase that earned or reversed the points; leave "" if unknown.
        pet_id: The pet profile reference number; leave "" if unknown.
        original_event_id: The reference number of the original entry (charge, fill, booking, visit, order line or fee) this entry refers to; leave "" if unknown.
    """
    match = {k: v for k, v in {"member_event_id": member_event_id, "membership_id": membership_id, "customer_id": customer_id, "source_event_id": source_event_id, "pet_id": pet_id, "original_event_id": original_event_id}.items() if v}
    rows = ctx.find("member_events", **match)
    return str(rows) if rows else f"No member events records for {match}."


@tool(owner="agent", rw="read")
def find_orders(ctx: ToolContext, order_id: str = "", customer_id: str = "", store_id: str = "") -> str:
    """Look up a customer's retail orders: fulfillment method and status, order date,
    fulfilling store, promised and actual delivery or pickup, alternate pickup person,
    failed delivery attempts, pickup extension, substitution preference and net amount
    billed.

    Every criterion is optional; give whichever reference numbers you already hold.
    All matching records are returned with their full details, or a short notice when
    nothing matches.

    Args:
        order_id: The order number; leave "" if unknown.
        customer_id: The customer reference number; leave "" if unknown.
        store_id: The store reference number; leave "" if unknown.
    """
    match = {k: v for k, v in {"order_id": order_id, "customer_id": customer_id, "store_id": store_id}.items() if v}
    rows = ctx.find("orders", **match)
    return str(rows) if rows else f"No orders records for {match}."


@tool(owner="agent", rw="read")
def find_order_events(ctx: ToolContext, order_event_id: str = "", order_id: str = "", customer_id: str = "", original_event_id: str = "", rma_id: str = "") -> str:
    """Look up the line-by-line history of an order: items charged with coupons and
    certificates, fulfillment fees, cancellations, return refunds, damage and missing-
    item credits, fee refunds and replacements.

    Every criterion is optional; give whichever reference numbers you already hold.
    All matching records are returned with their full details, or a short notice when
    nothing matches.

    Args:
        order_event_id: The reference number of the order history entry itself; leave "" if unknown.
        order_id: The order number; leave "" if unknown.
        customer_id: The customer reference number; leave "" if unknown.
        original_event_id: The reference number of the original entry (charge, fill, booking, visit, order line or fee) this entry refers to; leave "" if unknown.
        rma_id: The return authorization number; leave "" if unknown.
    """
    match = {k: v for k, v in {"order_event_id": order_event_id, "order_id": order_id, "customer_id": customer_id, "original_event_id": original_event_id, "rma_id": rma_id}.items() if v}
    rows = ctx.find("order_events", **match)
    return str(rows) if rows else f"No order events records for {match}."


@tool(owner="agent", rw="read")
def find_order_return_requests(ctx: ToolContext, rma_id: str = "", customer_id: str = "", order_id: str = "", original_event_id: str = "") -> str:
    """Look up return authorizations: the order line and quantity, reason and return
    method, authorization date, progress and the date the item was received.

    Every criterion is optional; give whichever reference numbers you already hold.
    All matching records are returned with their full details, or a short notice when
    nothing matches.

    Args:
        rma_id: The return authorization number; leave "" if unknown.
        customer_id: The customer reference number; leave "" if unknown.
        order_id: The order number; leave "" if unknown.
        original_event_id: The reference number of the original entry (charge, fill, booking, visit, order line or fee) this entry refers to; leave "" if unknown.
    """
    match = {k: v for k, v in {"rma_id": rma_id, "customer_id": customer_id, "order_id": order_id, "original_event_id": original_event_id}.items() if v}
    rows = ctx.find("order_return_requests", **match)
    return str(rows) if rows else f"No order return requests records for {match}."


@tool(owner="agent", rw="read")
def find_vet_plans(ctx: ToolContext, vet_plan_id: str = "", customer_id: str = "", pet_id: str = "", store_id: str = "") -> str:
    """Look up the Tailwise Vet Clinic wellness plans on a customer's account: plan, pet,
    home clinic, payment mode, enrollment and term dates, next payment date, fees paid
    and list value of services used in the current term.

    Every criterion is optional; give whichever reference numbers you already hold.
    All matching records are returned with their full details, or a short notice when
    nothing matches.

    Args:
        vet_plan_id: The wellness plan reference number; leave "" if unknown.
        customer_id: The customer reference number; leave "" if unknown.
        pet_id: The pet profile reference number; leave "" if unknown.
        store_id: The store reference number; leave "" if unknown.
    """
    match = {k: v for k, v in {"vet_plan_id": vet_plan_id, "customer_id": customer_id, "pet_id": pet_id, "store_id": store_id}.items() if v}
    rows = ctx.find("vet_plans", **match)
    return str(rows) if rows else f"No vet plans records for {match}."


@tool(owner="agent", rw="read")
def find_vet_plan_events(ctx: ToolContext, vet_event_id: str = "", vet_plan_id: str = "", customer_id: str = "", original_event_id: str = "") -> str:
    """Look up the history of a wellness plan: monthly fees charged and declined, included
    services redeemed with their list value, discounts on other services, voided
    entries, refunds and cancellation settlements.

    Every criterion is optional; give whichever reference numbers you already hold.
    All matching records are returned with their full details, or a short notice when
    nothing matches.

    Args:
        vet_event_id: The reference number of the plan history entry itself; leave "" if unknown.
        vet_plan_id: The wellness plan reference number; leave "" if unknown.
        customer_id: The customer reference number; leave "" if unknown.
        original_event_id: The reference number of the original entry (charge, fill, booking, visit, order line or fee) this entry refers to; leave "" if unknown.
    """
    match = {k: v for k, v in {"vet_event_id": vet_event_id, "vet_plan_id": vet_plan_id, "customer_id": customer_id, "original_event_id": original_event_id}.items() if v}
    rows = ctx.find("vet_plan_events", **match)
    return str(rows) if rows else f"No vet plan events records for {match}."


@tool(owner="agent", rw="read")
def find_vet_cancellation_requests(ctx: ToolContext, cancel_request_id: str = "", customer_id: str = "", vet_plan_id: str = "") -> str:
    """Look up wellness plan cancellation requests with their date, reason and progress.

    Every criterion is optional; give whichever reference numbers you already hold.
    All matching records are returned with their full details, or a short notice when
    nothing matches.

    Args:
        cancel_request_id: The reference number of the cancellation request itself; leave "" if unknown.
        customer_id: The customer reference number; leave "" if unknown.
        vet_plan_id: The wellness plan reference number; leave "" if unknown.
    """
    match = {k: v for k, v in {"cancel_request_id": cancel_request_id, "customer_id": customer_id, "vet_plan_id": vet_plan_id}.items() if v}
    rows = ctx.find("vet_cancellation_requests", **match)
    return str(rows) if rows else f"No vet cancellation requests records for {match}."


@tool(owner="agent", rw="read")
def find_train_enrollments(ctx: ToolContext, train_enrollment_id: str = "", customer_id: str = "", pet_id: str = "", store_id: str = "", repeat_of_enrollment_id: str = "") -> str:
    """Look up a customer's training enrollments: course or private pack, dog, store,
    whether it was bought or is a guarantee repeat, class start date, price paid,
    enrollment and expiry dates, sessions remaining and transfers used.

    Every criterion is optional; give whichever reference numbers you already hold.
    All matching records are returned with their full details, or a short notice when
    nothing matches.

    Args:
        train_enrollment_id: The training enrollment reference number; leave "" if unknown.
        customer_id: The customer reference number; leave "" if unknown.
        pet_id: The pet profile reference number; leave "" if unknown.
        store_id: The store reference number; leave "" if unknown.
        repeat_of_enrollment_id: The reference number of the enrollment a free repeat is for; leave "" if unknown.
    """
    match = {k: v for k, v in {"train_enrollment_id": train_enrollment_id, "customer_id": customer_id, "pet_id": pet_id, "store_id": store_id, "repeat_of_enrollment_id": repeat_of_enrollment_id}.items() if v}
    rows = ctx.find("train_enrollments", **match)
    return str(rows) if rows else f"No train enrollments records for {match}."


@tool(owner="agent", rw="read")
def find_train_sessions(ctx: ToolContext, train_event_id: str = "", train_enrollment_id: str = "", customer_id: str = "", original_event_id: str = "") -> str:
    """Look up the session history of a training enrollment: sessions attended, excused and
    unexcused absences with the notice given, makeup credits and refunds.

    Every criterion is optional; give whichever reference numbers you already hold.
    All matching records are returned with their full details, or a short notice when
    nothing matches.

    Args:
        train_event_id: The reference number of the session history entry itself; leave "" if unknown.
        train_enrollment_id: The training enrollment reference number; leave "" if unknown.
        customer_id: The customer reference number; leave "" if unknown.
        original_event_id: The reference number of the original entry (charge, fill, booking, visit, order line or fee) this entry refers to; leave "" if unknown.
    """
    match = {k: v for k, v in {"train_event_id": train_event_id, "train_enrollment_id": train_enrollment_id, "customer_id": customer_id, "original_event_id": original_event_id}.items() if v}
    rows = ctx.find("train_sessions", **match)
    return str(rows) if rows else f"No train sessions records for {match}."


@tool(owner="agent", rw="read")
def find_livepet_guarantees(ctx: ToolContext, livepet_guarantee_id: str = "", customer_id: str = "", store_id: str = "") -> str:
    """Look up the live animal guarantees from a customer's purchases: guarantee, species,
    quantity and price, store, purchase date and time, remaining covered value and
    closing date.

    Every criterion is optional; give whichever reference numbers you already hold.
    All matching records are returned with their full details, or a short notice when
    nothing matches.

    Args:
        livepet_guarantee_id: The live animal guarantee reference number; leave "" if unknown.
        customer_id: The customer reference number; leave "" if unknown.
        store_id: The store reference number; leave "" if unknown.
    """
    match = {k: v for k, v in {"livepet_guarantee_id": livepet_guarantee_id, "customer_id": customer_id, "store_id": store_id}.items() if v}
    rows = ctx.find("livepet_guarantees", **match)
    return str(rows) if rows else f"No livepet guarantees records for {match}."


@tool(owner="agent", rw="read")
def find_livepet_events(ctx: ToolContext, livepet_event_id: str = "", livepet_guarantee_id: str = "", customer_id: str = "", original_event_id: str = "") -> str:
    """Look up the history of a live animal guarantee: water tests, free wellness exams,
    claims and the remedies given.

    Every criterion is optional; give whichever reference numbers you already hold.
    All matching records are returned with their full details, or a short notice when
    nothing matches.

    Args:
        livepet_event_id: The reference number of the guarantee history entry itself; leave "" if unknown.
        livepet_guarantee_id: The live animal guarantee reference number; leave "" if unknown.
        customer_id: The customer reference number; leave "" if unknown.
        original_event_id: The reference number of the original entry (charge, fill, booking, visit, order line or fee) this entry refers to; leave "" if unknown.
    """
    match = {k: v for k, v in {"livepet_event_id": livepet_event_id, "livepet_guarantee_id": livepet_guarantee_id, "customer_id": customer_id, "original_event_id": original_event_id}.items() if v}
    rows = ctx.find("livepet_events", **match)
    return str(rows) if rows else f"No livepet events records for {match}."


@tool(owner="agent", rw="read")
def find_verification_log(ctx: ToolContext, verification_id: str = "", customer_id: str = "") -> str:
    """Look up the identity-verification outcome recorded for a customer during support
    contacts, including whether it passed and when it was last attempted.

    Every criterion is optional; give whichever reference numbers you already hold.
    All matching records are returned with their full details, or a short notice when
    nothing matches.

    Args:
        verification_id: The reference number of the verification record itself; leave "" if unknown.
        customer_id: The customer reference number; leave "" if unknown.
    """
    match = {k: v for k, v in {"verification_id": verification_id, "customer_id": customer_id}.items() if v}
    rows = ctx.find("verification_log", **match)
    return str(rows) if rows else f"No verification log records for {match}."


@tool(owner="agent", rw="read")
def find_handoff_log(ctx: ToolContext, handoff_id: str = "", customer_id: str = "") -> str:
    """Look up the transfers to a human representative recorded for a customer, with the
    reason and the moment of each transfer.

    Every criterion is optional; give whichever reference numbers you already hold.
    All matching records are returned with their full details, or a short notice when
    nothing matches.

    Args:
        handoff_id: The reference number of the transfer record itself; leave "" if unknown.
        customer_id: The customer reference number; leave "" if unknown.
    """
    match = {k: v for k, v in {"handoff_id": handoff_id, "customer_id": customer_id}.items() if v}
    rows = ctx.find("handoff_log", **match)
    return str(rows) if rows else f"No handoff log records for {match}."


@tool(owner="agent", rw="write")
def verify_customer_identity(ctx: ToolContext, customer_id: str, phone_number: str = "",
                             email: str = "", billing_zip: str = "", card_last4: str = "",
                             member_since: str = "") -> str:
    """Verify the caller's identity against the customer profile and record the outcome.

    Identity must be verified before any account details are discussed or any order,
    subscription, prescription, appointment, membership or refund is handled. This tool
    performs the comparison itself: it checks each detail the caller gives against the
    profile, counts the matches, and passes only when at least 2 details match. The
    customer reference number is used only to open the profile and never counts as a match.
    Callers usually know only some of these details, so pass exactly what the caller said,
    unchanged, and leave the rest blank. The outcome is recorded; if a first attempt fails
    and a later attempt with more details passes, the pass stands.

    Args:
        customer_id: The customer reference number read from the customer profile lookup. Required; used only to open the profile.
        phone_number: The registered mobile number as stated by the caller, 10 digits; leave "" if not stated.
        email: The registered email address as stated by the caller; leave "" if not stated.
        billing_zip: The 5-digit ZIP code of the billing address on the card on file, as stated; leave "" if not stated.
        card_last4: The last four digits of the card on file, as stated; leave "" if not stated.
        member_since: The date the profile was opened, as YYYY-MM-DD; leave "" if not stated.
    """
    if not customer_id:
        return "Error: customer_id is required; look the customer up first and pass their reference number."
    rows = ctx.find("customers", customer_id=customer_id)
    if not rows:
        return f"Error: no customer {customer_id}; cannot verify."
    rec = rows[0]
    # The locator customer_id is deliberately not part of `supplied`.
    supplied = {"phone_number": phone_number, "email": email, "billing_zip": billing_zip,
                "card_last4": card_last4, "member_since": member_since}
    matched = sum(1 for field, value in supplied.items()
                  if value and str(rec.get(field)).strip().lower() == str(value).strip().lower())
    verified = matched >= 2
    rid = ctx.make_id("ver_", customer_id)
    prior = ctx.find("verification_log", verification_id=rid)
    verified = verified or bool(prior and prior[0].get("verified"))
    if prior:
        ctx.update("verification_log", rid, verified=verified, verified_at=ctx.now())
    else:
        ctx.create("verification_log", rid, verification_id=rid, customer_id=customer_id,
                   verified=verified, verified_at=ctx.now())
    return (f"Identity verified for {customer_id} ({matched} detail(s) matched)." if verified
            else f"Identity NOT verified for {customer_id} (only {matched} of the required 2 details matched). "
                 "Ask the caller for another detail on file and try again.")


@tool(owner="agent", rw="write")
def transfer_to_human_agent(ctx: ToolContext, customer_id: str, reason: str) -> str:
    """Transfer the customer to a human Tailwise care representative and record why.

    Use it in one of two situations only: when no Tailwise policy offers a way to resolve
    what the customer is asking for, or when the customer has explicitly asked for a human
    representative at least 2 times during the contact.

    Args:
        customer_id: The customer reference number read from the customer profile lookup (the profile must exist).
        reason: Why the customer is being transferred; exactly one of POLICY_NOT_COVERED (no policy can resolve the request) or CUSTOMER_REQUESTED (the customer explicitly asked for a human representative at least 2 times). Never free text.
    """
    allowed = {"POLICY_NOT_COVERED", "CUSTOMER_REQUESTED"}
    if reason not in allowed:
        return f"Error: unknown transfer reason '{reason}'. Valid: {', '.join(sorted(allowed))}."
    if not ctx.find("customers", customer_id=customer_id):
        return f"Error: no customer {customer_id}; cannot record the transfer."
    rid = ctx.make_id("hof_", customer_id, reason)
    ctx.create("handoff_log", rid, handoff_id=rid, customer_id=customer_id,
               reason=reason, created_at=ctx.now())
    return f"Transfer to a human representative recorded for {customer_id} ({reason})."

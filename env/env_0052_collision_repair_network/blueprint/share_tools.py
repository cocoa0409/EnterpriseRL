"""Shared tools for env_0052_collision_repair_network (Crestline Collision & Glass).

Every tool here is a share tool: always present in its owner's tool list. This module holds the
record-lookup layer (one finder per record kind; the customer finder doubles as the identity entry),
the identity-verification write and the handoff to a human representative. Customer-only actions
(signatures, consents, approvals, declinations) are hidden task tools authored per difficulty.

Implementation notes (not part of any tool description):
  - Every finder takes all reference-number fields of its record kind as optional arguments and
    requires at least one, so no lookup ever returns another customer's records wholesale.
  - Identity verification passes at K = 2 matching credentials (phone, email, ZIP code, account
    PIN); the customer reference number only locates the profile and never counts.
  - A handoff for CUSTOMER_REQUESTED is due once the caller has asked for a human R = 2 times.
"""

from erlbench import ToolContext, tool


# --------------------------------------------------------------------------- customers & vehicles

@tool(owner="agent", rw="read")
def find_customers(ctx: ToolContext, customer_id: str = "", name: str = "", phone_number: str = "",
                   email: str = "") -> str:
    """Look up a customer profile to establish whose account the conversation is about.

    Crestline holds one profile for each private vehicle owner, each insurance company account and
    each commercial fleet account. A profile can be found by its customer reference number or by
    what a caller can naturally state: the full name (or company name), the phone number on file, or
    the email address on file. Supply whichever are known; spacing, punctuation and letter case in
    what the caller says do not matter. A single match returns the profile, including the customer
    reference number, the kind of profile, contact details, ZIP code and the date the profile was
    opened. Finding a profile does not verify the caller's identity.

    Args:
        customer_id: The customer reference number, if already known; leave "" otherwise.
        name: Full name of the person, or the registered company name of an insurer or fleet, as the caller states it; leave "" if not given.
        phone_number: Phone number on the profile as the caller states it (10 digits); leave "" if not given.
        email: Email address on the profile as the caller states it; leave "" if not given.
    """
    match = {k: v for k, v in {"customer_id": customer_id, "name": name,
                               "phone_number": phone_number, "email": email}.items() if v}
    if not match:
        return "Error: provide at least one detail (reference number, name, phone or email) to find the customer."
    rows = ctx.fuzzy_find("customers", **match)
    if not rows:
        return f"No customer profile matches {match}."
    if len(rows) > 1:
        return f"Error: {len(rows)} customer profiles match {match}; ask the caller for one more detail."
    return str(rows[0])


@tool(owner="agent", rw="read")
def find_vehicles(ctx: ToolContext, vehicle_id: str = "", customer_id: str = "") -> str:
    """Look up vehicles on file: VIN, model year, make and model, body construction, powertrain, the
    driver-assistance sensors fitted at the factory, the state of registration, and whether the owner
    on file has reported selling the vehicle.

    Search by the vehicle reference number, or list every vehicle a customer owns by the customer
    reference number. Supply at least one.

    Args:
        vehicle_id: Reference number of the vehicle; leave "" if unknown.
        customer_id: Customer reference number of the owner, to list all of their vehicles; leave "" if unknown.
    """
    match = {k: v for k, v in {"vehicle_id": vehicle_id, "customer_id": customer_id}.items() if v}
    if not match:
        return "Error: provide at least one reference number to look up vehicles."
    rows = ctx.find("vehicles", **match)
    return str(rows) if rows else f"No vehicles found for {match}."


# --------------------------------------------------------------------------- estimates

@tool(owner="agent", rw="read")
def find_estimate_bookings(ctx: ToolContext, booking_id: str = "", customer_id: str = "", vehicle_id: str = "",
                           insurer_customer_id: str = "") -> str:
    """Look up damage estimate bookings: the estimate type, current status, payer (insurance claim or
    customer pay), insurer claim number, appointment date and slot, assigned repair center, the damage
    profile reported, and, once written, the estimate total, labor hours and key dates (check-in,
    estimate written, conversion, vehicle release, closing).

    Search by any reference number in hand; supply at least one.

    Args:
        booking_id: Reference number of the estimate booking; leave "" if unknown.
        customer_id: Customer reference number of the vehicle owner; leave "" if unknown.
        vehicle_id: Reference number of the vehicle estimated; leave "" if unknown.
        insurer_customer_id: Customer reference number of the insurer account on an insurance-claim booking; leave "" if unknown.
    """
    match = {k: v for k, v in {"booking_id": booking_id, "customer_id": customer_id, "vehicle_id": vehicle_id, "insurer_customer_id": insurer_customer_id}.items() if v}
    if not match:
        return "Error: provide at least one reference number to look up estimate bookings."
    rows = ctx.find("estimate_bookings", **match)
    return str(rows) if rows else f"No estimate bookings found for {match}."


@tool(owner="agent", rw="read")
def find_estimate_events(ctx: ToolContext, estimate_event_id: str = "", booking_id: str = "", customer_id: str = "",
                         charge_event_id: str = "") -> str:
    """Look up the history of an estimate booking: reschedules, estimate revisions, estimate-stage
    charges (teardown, scan, measurement, mobile trip, tow-in, storage) and the payments and waivers
    applied to each charge.

    Search by the entry's own reference number, the booking, the customer, or the charge a payment
    or waiver applies to; supply at least one.

    Args:
        estimate_event_id: Reference number of one history entry; leave "" if unknown.
        booking_id: Reference number of the estimate booking; leave "" if unknown.
        customer_id: Customer reference number; leave "" if unknown.
        charge_event_id: Reference number of a charge, to list the payments and waivers applied to it; leave "" if unknown.
    """
    match = {k: v for k, v in {"estimate_event_id": estimate_event_id, "booking_id": booking_id, "customer_id": customer_id, "charge_event_id": charge_event_id}.items() if v}
    if not match:
        return "Error: provide at least one reference number to look up estimate booking history entries."
    rows = ctx.find("estimate_events", **match)
    return str(rows) if rows else f"No estimate booking history entries found for {match}."


@tool(owner="agent", rw="read")
def find_estimate_requests(ctx: ToolContext, request_id: str = "", customer_id: str = "", booking_id: str = "") -> str:
    """Look up requests on an estimate booking that wait for the customer's own confirmation, such as a
    teardown authorization or a decision not to repair, with their status and confirmation date.

    Search by the request, the customer or the booking; supply at least one.

    Args:
        request_id: Reference number of the request; leave "" if unknown.
        customer_id: Customer reference number; leave "" if unknown.
        booking_id: Reference number of the estimate booking; leave "" if unknown.
    """
    match = {k: v for k, v in {"request_id": request_id, "customer_id": customer_id, "booking_id": booking_id}.items() if v}
    if not match:
        return "Error: provide at least one reference number to look up estimate booking requests."
    rows = ctx.find("estimate_requests", **match)
    return str(rows) if rows else f"No estimate booking requests found for {match}."


# --------------------------------------------------------------------------- insurance claim repairs

@tool(owner="agent", rw="read")
def find_claim_repairs(ctx: ToolContext, claim_repair_id: str = "", customer_id: str = "", vehicle_id: str = "",
                       booking_id: str = "", insurer_customer_id: str = "", carrier_agreement_id: str = "") -> str:
    """Look up insurance claim repair orders: the repair class, status, insurer and claim number,
    coverage type, deductible stated by the insurer, original estimate and labor hours, planned repair
    days, any hold and its reason, and the key dates from opening through authorization, drop-off,
    vehicle-ready, delivery, total loss or closing.

    Search by any reference number in hand; supply at least one. An insurer can list its own repair
    orders by its customer reference number or its program agreement.

    Args:
        claim_repair_id: Reference number of the repair order; leave "" if unknown.
        customer_id: Customer reference number of the vehicle owner; leave "" if unknown.
        vehicle_id: Reference number of the vehicle; leave "" if unknown.
        booking_id: Reference number of the estimate booking it came from; leave "" if unknown.
        insurer_customer_id: Customer reference number of the paying insurer; leave "" if unknown.
        carrier_agreement_id: Reference number of the insurer's program agreement; leave "" if unknown.
    """
    match = {k: v for k, v in {"claim_repair_id": claim_repair_id, "customer_id": customer_id, "vehicle_id": vehicle_id, "booking_id": booking_id, "insurer_customer_id": insurer_customer_id, "carrier_agreement_id": carrier_agreement_id}.items() if v}
    if not match:
        return "Error: provide at least one reference number to look up insurance claim repair orders."
    rows = ctx.find("claim_repairs", **match)
    return str(rows) if rows else f"No insurance claim repair orders found for {match}."


@tool(owner="agent", rw="read")
def find_claim_supplements(ctx: ToolContext, supplement_event_id: str = "", claim_repair_id: str = "",
                           customer_id: str = "", submission_event_id: str = "") -> str:
    """Look up supplements on insurance claim repair orders: each supplement as submitted (number,
    amount, labor hours, whether it adds structural work or sensor calibrations, expected betterment,
    approval route) and the decision on it (approved, partly approved or denied, the amount approved
    and the betterment applied).

    Search by the entry, the repair order, the customer, or the submission a decision answers; supply
    at least one.

    Args:
        supplement_event_id: Reference number of one supplement entry; leave "" if unknown.
        claim_repair_id: Reference number of the repair order; leave "" if unknown.
        customer_id: Customer reference number; leave "" if unknown.
        submission_event_id: Reference number of a submitted supplement, to find the decision on it; leave "" if unknown.
    """
    match = {k: v for k, v in {"supplement_event_id": supplement_event_id, "claim_repair_id": claim_repair_id, "customer_id": customer_id, "submission_event_id": submission_event_id}.items() if v}
    if not match:
        return "Error: provide at least one reference number to look up supplement entries."
    rows = ctx.find("claim_supplements", **match)
    return str(rows) if rows else f"No supplement entries found for {match}."


@tool(owner="agent", rw="read")
def find_claim_ledger(ctx: ToolContext, ledger_entry_id: str = "", claim_repair_id: str = "", customer_id: str = "",
                      consent_id: str = "", source_entry_id: str = "") -> str:
    """Look up the money history of insurance claim repair orders: insurer approvals, the customer's
    charges (deductible, betterment, customer-pay additions, withdrawal teardown, storage), the
    matching reductions of what the insurer owes, customer payments, refunds and credits, insurer
    remittances and adjustments.

    Search by the entry, the repair order, the customer, the signed consent a charge rests on, or the
    entry that a refund, credit, offset or adjustment refers to; supply at least one.

    Args:
        ledger_entry_id: Reference number of one entry; leave "" if unknown.
        claim_repair_id: Reference number of the repair order; leave "" if unknown.
        customer_id: Customer reference number; leave "" if unknown.
        consent_id: Reference number of a signed consent, to find the charge resting on it; leave "" if unknown.
        source_entry_id: Reference number of an entry, to find the refunds, credits, offsets or adjustments that refer to it; leave "" if unknown.
    """
    match = {k: v for k, v in {"ledger_entry_id": ledger_entry_id, "claim_repair_id": claim_repair_id, "customer_id": customer_id, "consent_id": consent_id, "source_entry_id": source_entry_id}.items() if v}
    if not match:
        return "Error: provide at least one reference number to look up repair order money entries."
    rows = ctx.find("claim_ledger", **match)
    return str(rows) if rows else f"No repair order money entries found for {match}."


@tool(owner="agent", rw="read")
def find_claim_consents(ctx: ToolContext, consent_id: str = "", customer_id: str = "", claim_repair_id: str = "") -> str:
    """Look up the forms on insurance claim repair orders that carry the customer's signature: repair
    authorization, direction to pay, non-original parts disclosure, customer-pay additions (with
    amount, labor hours and what they cover) and vehicle withdrawal, each with its status and signing
    date.

    Search by the form, the customer or the repair order; supply at least one.

    Args:
        consent_id: Reference number of the form; leave "" if unknown.
        customer_id: Customer reference number; leave "" if unknown.
        claim_repair_id: Reference number of the repair order; leave "" if unknown.
    """
    match = {k: v for k, v in {"consent_id": consent_id, "customer_id": customer_id, "claim_repair_id": claim_repair_id}.items() if v}
    if not match:
        return "Error: provide at least one reference number to look up repair order consent forms."
    rows = ctx.find("claim_consents", **match)
    return str(rows) if rows else f"No repair order consent forms found for {match}."


# --------------------------------------------------------------------------- customer-pay repairs

@tool(owner="agent", rw="read")
def find_retail_repairs(ctx: ToolContext, retail_repair_id: str = "", customer_id: str = "", vehicle_id: str = "",
                        booking_id: str = "") -> str:
    """Look up customer-pay repair orders: the service tier, status, quoted total, labor and labor
    hours, dents quoted, the discount program applied, and the dates from opening through drop-off,
    ready, delivery, cancellation or closing.

    Search by any reference number in hand; supply at least one.

    Args:
        retail_repair_id: Reference number of the customer-pay repair order; leave "" if unknown.
        customer_id: Customer reference number; leave "" if unknown.
        vehicle_id: Reference number of the vehicle; leave "" if unknown.
        booking_id: Reference number of the estimate booking it came from; leave "" if unknown.
    """
    match = {k: v for k, v in {"retail_repair_id": retail_repair_id, "customer_id": customer_id, "vehicle_id": vehicle_id, "booking_id": booking_id}.items() if v}
    if not match:
        return "Error: provide at least one reference number to look up customer-pay repair orders."
    rows = ctx.find("retail_repairs", **match)
    return str(rows) if rows else f"No customer-pay repair orders found for {match}."


@tool(owner="agent", rw="read")
def find_retail_ledger(ctx: ToolContext, retail_entry_id: str = "", retail_repair_id: str = "", customer_id: str = "",
                       approval_id: str = "", parts_event_id: str = "", source_entry_id: str = "") -> str:
    """Look up the money history of customer-pay repair orders: work charges, restocking and parts
    charges, storage, discounts, corrections and goodwill credits, deposits and payments, and refunds.

    Search by the entry, the repair order, the customer, the approved request or parts order a charge
    arises from, or the entry a credit or refund refers to; supply at least one.

    Args:
        retail_entry_id: Reference number of one entry; leave "" if unknown.
        retail_repair_id: Reference number of the customer-pay repair order; leave "" if unknown.
        customer_id: Customer reference number; leave "" if unknown.
        approval_id: Reference number of an approved additional-work request; leave "" if unknown.
        parts_event_id: Reference number of a parts order; leave "" if unknown.
        source_entry_id: Reference number of an entry, to find the credits or refunds that refer to it; leave "" if unknown.
    """
    match = {k: v for k, v in {"retail_entry_id": retail_entry_id, "retail_repair_id": retail_repair_id, "customer_id": customer_id, "approval_id": approval_id, "parts_event_id": parts_event_id, "source_entry_id": source_entry_id}.items() if v}
    if not match:
        return "Error: provide at least one reference number to look up customer-pay money entries."
    rows = ctx.find("retail_ledger", **match)
    return str(rows) if rows else f"No customer-pay money entries found for {match}."


@tool(owner="agent", rw="read")
def find_retail_parts(ctx: ToolContext, parts_event_id: str = "", retail_repair_id: str = "", customer_id: str = "",
                      source_parts_event_id: str = "") -> str:
    """Look up parts ordered for customer-pay repairs and parts returned to suppliers: supplier order
    number, parts amount and whether the supplier takes the parts back.

    Search by the parts entry, the repair order, the customer, or the order a return refers to;
    supply at least one.

    Args:
        parts_event_id: Reference number of one parts entry; leave "" if unknown.
        retail_repair_id: Reference number of the customer-pay repair order; leave "" if unknown.
        customer_id: Customer reference number; leave "" if unknown.
        source_parts_event_id: Reference number of a parts order, to find its return; leave "" if unknown.
    """
    match = {k: v for k, v in {"parts_event_id": parts_event_id, "retail_repair_id": retail_repair_id, "customer_id": customer_id, "source_parts_event_id": source_parts_event_id}.items() if v}
    if not match:
        return "Error: provide at least one reference number to look up parts entries."
    rows = ctx.find("retail_parts", **match)
    return str(rows) if rows else f"No parts entries found for {match}."


@tool(owner="agent", rw="read")
def find_retail_approvals(ctx: ToolContext, approval_id: str = "", customer_id: str = "",
                          retail_repair_id: str = "") -> str:
    """Look up requests on customer-pay repair orders that wait for the customer's decision: additional
    work beyond the quote (price and labor hours) and cancellation of the job, each with its status and
    decision date.

    Search by the request, the customer or the repair order; supply at least one.

    Args:
        approval_id: Reference number of the request; leave "" if unknown.
        customer_id: Customer reference number; leave "" if unknown.
        retail_repair_id: Reference number of the customer-pay repair order; leave "" if unknown.
    """
    match = {k: v for k, v in {"approval_id": approval_id, "customer_id": customer_id, "retail_repair_id": retail_repair_id}.items() if v}
    if not match:
        return "Error: provide at least one reference number to look up customer-pay requests."
    rows = ctx.find("retail_approvals", **match)
    return str(rows) if rows else f"No customer-pay requests found for {match}."


# --------------------------------------------------------------------------- auto glass

@tool(owner="agent", rw="read")
def find_glass_jobs(ctx: ToolContext, glass_job_id: str = "", customer_id: str = "", vehicle_id: str = "",
                    insurer_customer_id: str = "") -> str:
    """Look up auto glass jobs: the glass service, status, payer (glass claim, customer pay or fleet),
    insurer claim or referral number, full glass coverage and deductible, glass part type and price,
    chips to repair, mobile or in-shop service, appointment, installation and completion details, and
    whether a camera calibration is needed.

    Search by any reference number in hand; supply at least one.

    Args:
        glass_job_id: Reference number of the glass job; leave "" if unknown.
        customer_id: Customer reference number of the vehicle owner; leave "" if unknown.
        vehicle_id: Reference number of the vehicle; leave "" if unknown.
        insurer_customer_id: Customer reference number of the insurer on a glass claim; leave "" if unknown.
    """
    match = {k: v for k, v in {"glass_job_id": glass_job_id, "customer_id": customer_id, "vehicle_id": vehicle_id, "insurer_customer_id": insurer_customer_id}.items() if v}
    if not match:
        return "Error: provide at least one reference number to look up glass jobs."
    rows = ctx.find("glass_jobs", **match)
    return str(rows) if rows else f"No glass jobs found for {match}."


@tool(owner="agent", rw="read")
def find_glass_events(ctx: ToolContext, glass_event_id: str = "", glass_job_id: str = "", customer_id: str = "") -> str:
    """Look up reschedules of glass job appointments, with the cause (customer request or weather) and
    the new date and start.

    Search by the entry, the glass job or the customer; supply at least one.

    Args:
        glass_event_id: Reference number of one reschedule entry; leave "" if unknown.
        glass_job_id: Reference number of the glass job; leave "" if unknown.
        customer_id: Customer reference number; leave "" if unknown.
    """
    match = {k: v for k, v in {"glass_event_id": glass_event_id, "glass_job_id": glass_job_id, "customer_id": customer_id}.items() if v}
    if not match:
        return "Error: provide at least one reference number to look up glass job reschedules."
    rows = ctx.find("glass_events", **match)
    return str(rows) if rows else f"No glass job reschedules found for {match}."


@tool(owner="agent", rw="read")
def find_glass_ledger(ctx: ToolContext, glass_entry_id: str = "", glass_job_id: str = "", customer_id: str = "",
                      source_entry_id: str = "", warranty_coverage_id: str = "") -> str:
    """Look up the money history of glass jobs: customer charges (deductible, customer-pay service,
    original-equipment upgrade, late cancellation), customer payments and credits, and billings,
    remittances and repricing adjustments with the insurer's glass program.

    Search by the entry, the glass job, the customer, the entry a credit or adjustment refers to, or
    the warranty coverage behind a chip repair credit; supply at least one.

    Args:
        glass_entry_id: Reference number of one entry; leave "" if unknown.
        glass_job_id: Reference number of the glass job; leave "" if unknown.
        customer_id: Customer reference number; leave "" if unknown.
        source_entry_id: Reference number of an entry, to find credits or adjustments that refer to it; leave "" if unknown.
        warranty_coverage_id: Reference number of a Chip Repair Guarantee coverage used as a credit; leave "" if unknown.
    """
    match = {k: v for k, v in {"glass_entry_id": glass_entry_id, "glass_job_id": glass_job_id, "customer_id": customer_id, "source_entry_id": source_entry_id, "warranty_coverage_id": warranty_coverage_id}.items() if v}
    if not match:
        return "Error: provide at least one reference number to look up glass money entries."
    rows = ctx.find("glass_ledger", **match)
    return str(rows) if rows else f"No glass money entries found for {match}."


# --------------------------------------------------------------------------- sensor calibrations

@tool(owner="agent", rw="read")
def find_adas_orders(ctx: ToolContext, adas_order_id: str = "", customer_id: str = "", vehicle_id: str = "",
                     glass_job_id: str = "", claim_repair_id: str = "", retail_repair_id: str = "",
                     warranty_event_id: str = "") -> str:
    """Look up driver-assistance sensor calibration orders: the calibration tier, status, what made the
    calibration necessary and the job it belongs to, who pays, the systems to calibrate, the
    manufacturer procedure, whether it was on the insurer-authorized original estimate, and the
    precheck, dealer sublet, completion or cancellation details.

    Search by the order or by the vehicle, customer, glass job, repair order or warranty rework it
    belongs to; supply at least one.

    Args:
        adas_order_id: Reference number of the calibration order; leave "" if unknown.
        customer_id: Customer reference number; leave "" if unknown.
        vehicle_id: Reference number of the vehicle; leave "" if unknown.
        glass_job_id: Reference number of the glass job that required it; leave "" if unknown.
        claim_repair_id: Reference number of the insurance claim repair order that required it; leave "" if unknown.
        retail_repair_id: Reference number of the customer-pay repair order that required it; leave "" if unknown.
        warranty_event_id: Reference number of the warranty rework authorization that required it; leave "" if unknown.
    """
    match = {k: v for k, v in {"adas_order_id": adas_order_id, "customer_id": customer_id, "vehicle_id": vehicle_id, "glass_job_id": glass_job_id, "claim_repair_id": claim_repair_id, "retail_repair_id": retail_repair_id, "warranty_event_id": warranty_event_id}.items() if v}
    if not match:
        return "Error: provide at least one reference number to look up calibration orders."
    rows = ctx.find("adas_orders", **match)
    return str(rows) if rows else f"No calibration orders found for {match}."


@tool(owner="agent", rw="read")
def find_adas_events(ctx: ToolContext, adas_event_id: str = "", adas_order_id: str = "", customer_id: str = "") -> str:
    """Look up the work history of calibration orders: four-wheel alignment checks with their result and
    whether a correction was made, and each calibration attempt with its procedure, result and failure
    reason.

    Search by the entry, the calibration order or the customer; supply at least one.

    Args:
        adas_event_id: Reference number of one history entry; leave "" if unknown.
        adas_order_id: Reference number of the calibration order; leave "" if unknown.
        customer_id: Customer reference number; leave "" if unknown.
    """
    match = {k: v for k, v in {"adas_event_id": adas_event_id, "adas_order_id": adas_order_id, "customer_id": customer_id}.items() if v}
    if not match:
        return "Error: provide at least one reference number to look up calibration history entries."
    rows = ctx.find("adas_events", **match)
    return str(rows) if rows else f"No calibration history entries found for {match}."


@tool(owner="agent", rw="read")
def find_adas_ledger(ctx: ToolContext, adas_entry_id: str = "", adas_order_id: str = "", customer_id: str = "",
                     source_entry_id: str = "", claim_repair_id: str = "") -> str:
    """Look up the money history of calibration orders: calibration, dealer sublet, alignment and
    diagnostic charges, transfers onto insurance claim repair orders, payments by customers or glass
    programs, and write-offs.

    Search by the entry, the calibration order, the customer, the charge a transfer or write-off
    refers to, or the repair order a charge was transferred to; supply at least one.

    Args:
        adas_entry_id: Reference number of one entry; leave "" if unknown.
        adas_order_id: Reference number of the calibration order; leave "" if unknown.
        customer_id: Customer reference number; leave "" if unknown.
        source_entry_id: Reference number of a charge, to find transfers or write-offs that refer to it; leave "" if unknown.
        claim_repair_id: Reference number of an insurance claim repair order a charge was transferred to; leave "" if unknown.
    """
    match = {k: v for k, v in {"adas_entry_id": adas_entry_id, "adas_order_id": adas_order_id, "customer_id": customer_id, "source_entry_id": source_entry_id, "claim_repair_id": claim_repair_id}.items() if v}
    if not match:
        return "Error: provide at least one reference number to look up calibration money entries."
    rows = ctx.find("adas_ledger", **match)
    return str(rows) if rows else f"No calibration money entries found for {match}."


@tool(owner="agent", rw="read")
def find_adas_declinations(ctx: ToolContext, declination_id: str = "", customer_id: str = "",
                           adas_order_id: str = "") -> str:
    """Look up calibration declination forms, by which a customer declines a sensor calibration in
    writing, with their status and signing date.

    Search by the form, the customer or the calibration order; supply at least one.

    Args:
        declination_id: Reference number of the declination form; leave "" if unknown.
        customer_id: Customer reference number; leave "" if unknown.
        adas_order_id: Reference number of the calibration order; leave "" if unknown.
    """
    match = {k: v for k, v in {"declination_id": declination_id, "customer_id": customer_id, "adas_order_id": adas_order_id}.items() if v}
    if not match:
        return "Error: provide at least one reference number to look up calibration declination forms."
    rows = ctx.find("adas_declinations", **match)
    return str(rows) if rows else f"No calibration declination forms found for {match}."


# --------------------------------------------------------------------------- rental coordination

@tool(owner="agent", rw="read")
def find_rental_reservations(ctx: ToolContext, rental_reservation_id: str = "", customer_id: str = "",
                             vehicle_id: str = "", claim_repair_id: str = "", retail_repair_id: str = "",
                             warranty_coverage_id: str = "", insurer_customer_id: str = "") -> str:
    """Look up replacement rental reservations: the rental class, status, who covers the rental
    (the customer's own rental coverage, another driver's insurer, the customer, or a warranty
    courtesy), the insurer's daily cap and total limit, renter age, partner branch, pickup and return
    details, the last covered day and the settlement date.

    Search by the reservation or by the customer, vehicle, repair order, warranty coverage or insurer
    it belongs to; supply at least one.

    Args:
        rental_reservation_id: Reference number of the reservation; leave "" if unknown.
        customer_id: Customer reference number of the renter; leave "" if unknown.
        vehicle_id: Reference number of the customer's vehicle in repair; leave "" if unknown.
        claim_repair_id: Reference number of the insurance claim repair order; leave "" if unknown.
        retail_repair_id: Reference number of the customer-pay repair order; leave "" if unknown.
        warranty_coverage_id: Reference number of the warranty coverage behind a courtesy rental; leave "" if unknown.
        insurer_customer_id: Customer reference number of the insurer paying covered days; leave "" if unknown.
    """
    match = {k: v for k, v in {"rental_reservation_id": rental_reservation_id, "customer_id": customer_id, "vehicle_id": vehicle_id, "claim_repair_id": claim_repair_id, "retail_repair_id": retail_repair_id, "warranty_coverage_id": warranty_coverage_id, "insurer_customer_id": insurer_customer_id}.items() if v}
    if not match:
        return "Error: provide at least one reference number to look up rental reservations."
    rows = ctx.find("rental_reservations", **match)
    return str(rows) if rows else f"No rental reservations found for {match}."


@tool(owner="agent", rw="read")
def find_rental_events(ctx: ToolContext, rental_event_id: str = "", rental_reservation_id: str = "",
                       customer_id: str = "", claim_repair_id: str = "", retail_repair_id: str = "") -> str:
    """Look up repair status notices received for rentals (vehicle ready, repair cancelled, total loss)
    with their dates.

    Search by the notice, the reservation, the customer or the repair order that sent it; supply at
    least one.

    Args:
        rental_event_id: Reference number of one notice; leave "" if unknown.
        rental_reservation_id: Reference number of the reservation; leave "" if unknown.
        customer_id: Customer reference number; leave "" if unknown.
        claim_repair_id: Reference number of the insurance claim repair order that sent it; leave "" if unknown.
        retail_repair_id: Reference number of the customer-pay repair order that sent it; leave "" if unknown.
    """
    match = {k: v for k, v in {"rental_event_id": rental_event_id, "rental_reservation_id": rental_reservation_id, "customer_id": customer_id, "claim_repair_id": claim_repair_id, "retail_repair_id": retail_repair_id}.items() if v}
    if not match:
        return "Error: provide at least one reference number to look up rental repair notices."
    rows = ctx.find("rental_events", **match)
    return str(rows) if rows else f"No rental repair notices found for {match}."


@tool(owner="agent", rw="read")
def find_rental_ledger(ctx: ToolContext, rental_entry_id: str = "", rental_reservation_id: str = "",
                       customer_id: str = "", extension_request_id: str = "", source_entry_id: str = "") -> str:
    """Look up the day and money history of rentals: covered days authorized and extended, covered days
    used, the customer's charges, amounts billed to the insurer or the network, customer payments and
    credits.

    Search by the entry, the reservation, the customer, the extension request an authorization
    approved, or the charge a credit refers to; supply at least one.

    Args:
        rental_entry_id: Reference number of one entry; leave "" if unknown.
        rental_reservation_id: Reference number of the reservation; leave "" if unknown.
        customer_id: Customer reference number; leave "" if unknown.
        extension_request_id: Reference number of an extension request; leave "" if unknown.
        source_entry_id: Reference number of a charge, to find credits that refer to it; leave "" if unknown.
    """
    match = {k: v for k, v in {"rental_entry_id": rental_entry_id, "rental_reservation_id": rental_reservation_id, "customer_id": customer_id, "extension_request_id": extension_request_id, "source_entry_id": source_entry_id}.items() if v}
    if not match:
        return "Error: provide at least one reference number to look up rental day and money entries."
    rows = ctx.find("rental_ledger", **match)
    return str(rows) if rows else f"No rental day and money entries found for {match}."


@tool(owner="agent", rw="read")
def find_rental_extension_requests(ctx: ToolContext, extension_request_id: str = "", customer_id: str = "",
                                   rental_reservation_id: str = "", insurer_customer_id: str = "") -> str:
    """Look up requests to an insurer for more covered rental days: the ground of the request, days
    asked for, the insurer's answer, days approved and the decision date.

    Search by the request, the customer, the reservation or the insurer; supply at least one.

    Args:
        extension_request_id: Reference number of the extension request; leave "" if unknown.
        customer_id: Customer reference number of the renter; leave "" if unknown.
        rental_reservation_id: Reference number of the reservation; leave "" if unknown.
        insurer_customer_id: Customer reference number of the insurer asked; leave "" if unknown.
    """
    match = {k: v for k, v in {"extension_request_id": extension_request_id, "customer_id": customer_id, "rental_reservation_id": rental_reservation_id, "insurer_customer_id": insurer_customer_id}.items() if v}
    if not match:
        return "Error: provide at least one reference number to look up rental extension requests."
    rows = ctx.find("rental_extension_requests", **match)
    return str(rows) if rows else f"No rental extension requests found for {match}."


# --------------------------------------------------------------------------- warranties

@tool(owner="agent", rw="read")
def find_warranty_coverages(ctx: ToolContext, warranty_coverage_id: str = "", customer_id: str = "",
                            vehicle_id: str = "", claim_repair_id: str = "", retail_repair_id: str = "",
                            glass_job_id: str = "", adas_order_id: str = "") -> str:
    """Look up workmanship warranty coverages: the warranty plan, status, the work it covers, the issue
    date and odometer at issue, recorded exclusions (customer-supplied parts, declined calibrations)
    and, when no longer active, why and when it ended.

    Search by the coverage or by the customer, vehicle, or the repair order, glass job or calibration
    order it was issued on; supply at least one.

    Args:
        warranty_coverage_id: Reference number of the coverage; leave "" if unknown.
        customer_id: Customer reference number; leave "" if unknown.
        vehicle_id: Reference number of the vehicle; leave "" if unknown.
        claim_repair_id: Reference number of the insurance claim repair order it covers; leave "" if unknown.
        retail_repair_id: Reference number of the customer-pay repair order it covers; leave "" if unknown.
        glass_job_id: Reference number of the glass job it covers; leave "" if unknown.
        adas_order_id: Reference number of the calibration order it covers; leave "" if unknown.
    """
    match = {k: v for k, v in {"warranty_coverage_id": warranty_coverage_id, "customer_id": customer_id, "vehicle_id": vehicle_id, "claim_repair_id": claim_repair_id, "retail_repair_id": retail_repair_id, "glass_job_id": glass_job_id, "adas_order_id": adas_order_id}.items() if v}
    if not match:
        return "Error: provide at least one reference number to look up warranty coverages."
    rows = ctx.find("warranty_coverages", **match)
    return str(rows) if rows else f"No warranty coverages found for {match}."


@tool(owner="agent", rw="read")
def find_warranty_events(ctx: ToolContext, warranty_event_id: str = "", warranty_coverage_id: str = "",
                         customer_id: str = "") -> str:
    """Look up warranty concerns and what became of them: each reported concern (kind, discovery date,
    odometer), its inspection outcome and any exclusion applied, and every remedy authorized and
    completed (rework at a network center, outside-shop repair or chip repair credit, courtesy rental
    days, recalibration need, result).

    Search by the entry, the coverage or the customer; supply at least one.

    Args:
        warranty_event_id: Reference number of one concern entry; leave "" if unknown.
        warranty_coverage_id: Reference number of the warranty coverage; leave "" if unknown.
        customer_id: Customer reference number; leave "" if unknown.
    """
    match = {k: v for k, v in {"warranty_event_id": warranty_event_id, "warranty_coverage_id": warranty_coverage_id, "customer_id": customer_id}.items() if v}
    if not match:
        return "Error: provide at least one reference number to look up warranty concern entries."
    rows = ctx.find("warranty_events", **match)
    return str(rows) if rows else f"No warranty concern entries found for {match}."


@tool(owner="agent", rw="read")
def find_warranty_ledger(ctx: ToolContext, warranty_entry_id: str = "", warranty_coverage_id: str = "",
                         customer_id: str = "", source_entry_id: str = "") -> str:
    """Look up the money history of warranty coverages: diagnostic charges with their payments and
    waivers, and outside-shop reimbursements approved and paid.

    Search by the entry, the coverage, the customer, or the entry a payment, waiver or reimbursement
    payment refers to; supply at least one.

    Args:
        warranty_entry_id: Reference number of one entry; leave "" if unknown.
        warranty_coverage_id: Reference number of the warranty coverage; leave "" if unknown.
        customer_id: Customer reference number; leave "" if unknown.
        source_entry_id: Reference number of an entry, to find what refers to it; leave "" if unknown.
    """
    match = {k: v for k, v in {"warranty_entry_id": warranty_entry_id, "warranty_coverage_id": warranty_coverage_id, "customer_id": customer_id, "source_entry_id": source_entry_id}.items() if v}
    if not match:
        return "Error: provide at least one reference number to look up warranty money entries."
    rows = ctx.find("warranty_ledger", **match)
    return str(rows) if rows else f"No warranty money entries found for {match}."


# --------------------------------------------------------------------------- insurer program agreements

@tool(owner="agent", rw="read")
def find_carrier_agreements(ctx: ToolContext, carrier_agreement_id: str = "", customer_id: str = "") -> str:
    """Look up an insurer's program agreement with the network: the agreement tier, status, committed
    annual volume, signing, effective and renewal dates, any market labor rate set on it, and review,
    suspension or termination details.

    Search by the agreement or by the insurer's customer reference number; supply at least one.

    Args:
        carrier_agreement_id: Reference number of the program agreement; leave "" if unknown.
        customer_id: Customer reference number of the insurer account; leave "" if unknown.
    """
    match = {k: v for k, v in {"carrier_agreement_id": carrier_agreement_id, "customer_id": customer_id}.items() if v}
    if not match:
        return "Error: provide at least one reference number to look up program agreements."
    rows = ctx.find("carrier_agreements", **match)
    return str(rows) if rows else f"No program agreements found for {match}."


@tool(owner="agent", rw="read")
def find_carrier_events(ctx: ToolContext, carrier_event_id: str = "", carrier_agreement_id: str = "",
                        customer_id: str = "", source_event_id: str = "") -> str:
    """Look up the history of insurer program agreements: claim assignments and their withdrawal,
    quarterly performance scorecards, service-level credits and how they were settled.

    Search by the entry, the agreement, the insurer, or the assignment or credit a withdrawal or
    settlement refers to; supply at least one.

    Args:
        carrier_event_id: Reference number of one entry; leave "" if unknown.
        carrier_agreement_id: Reference number of the program agreement; leave "" if unknown.
        customer_id: Customer reference number of the insurer account; leave "" if unknown.
        source_event_id: Reference number of an assignment or credit, to find what refers to it; leave "" if unknown.
    """
    match = {k: v for k, v in {"carrier_event_id": carrier_event_id, "carrier_agreement_id": carrier_agreement_id, "customer_id": customer_id, "source_event_id": source_event_id}.items() if v}
    if not match:
        return "Error: provide at least one reference number to look up program agreement entries."
    rows = ctx.find("carrier_events", **match)
    return str(rows) if rows else f"No program agreement entries found for {match}."


# --------------------------------------------------------------------------- verification & handoff records

@tool(owner="agent", rw="read")
def find_identity_verifications(ctx: ToolContext, verification_id: str = "", customer_id: str = "") -> str:
    """Look up whether a customer's identity has been verified in this conversation, and when the last
    verification attempt was made.

    Search by the verification record or the customer reference number; supply at least one.

    Args:
        verification_id: Reference number of the verification record; leave "" if unknown.
        customer_id: Customer reference number; leave "" if unknown.
    """
    match = {k: v for k, v in {"verification_id": verification_id, "customer_id": customer_id}.items() if v}
    if not match:
        return "Error: provide at least one reference number to look up identity verification records."
    rows = ctx.find("identity_verifications", **match)
    return str(rows) if rows else f"No identity verification records found for {match}."


@tool(owner="agent", rw="read")
def find_handoff_log(ctx: ToolContext, handoff_id: str = "", customer_id: str = "") -> str:
    """Look up handoffs of a customer to a human representative, with the reason recorded.

    Search by the handoff record or the customer reference number; supply at least one.

    Args:
        handoff_id: Reference number of the handoff record; leave "" if unknown.
        customer_id: Customer reference number; leave "" if unknown.
    """
    match = {k: v for k, v in {"handoff_id": handoff_id, "customer_id": customer_id}.items() if v}
    if not match:
        return "Error: provide at least one reference number to look up handoff records."
    rows = ctx.find("handoff_log", **match)
    return str(rows) if rows else f"No handoff records found for {match}."


# --------------------------------------------------------------------------- writes

@tool(owner="agent", rw="write")
def verify_customer_identity(ctx: ToolContext, customer_id: str, phone_number: str = "", email: str = "",
                             postal_code: str = "", account_pin: str = "") -> str:
    """Verify the caller's identity against the customer profile and record the outcome. The identity
    must be verified before any business is transacted on the account.

    This tool does the comparison itself: each detail the caller states is checked against the
    profile, and verification passes only when at least two of them match. The customer reference
    number only tells the tool which profile to check and never counts as a match. Callers usually
    know only some of these details, so pass exactly what the caller said and leave the rest blank.
    If an attempt fails and the caller later gives more details, call again; once verification has
    passed it stays passed.

    Args:
        customer_id: Customer reference number from the customer profile lookup. Required; it locates the profile and is not counted as a match.
        phone_number: Phone number on file as the caller states it (10 digits); leave "" if not stated.
        email: Email address on file as the caller states it; leave "" if not stated.
        postal_code: ZIP code of the address on file as the caller states it (5 digits); leave "" if not stated.
        account_pin: Four-digit account PIN as the caller states it; leave "" if not stated.
    """
    if not customer_id:
        return "Error: customer_id is required; look up the customer profile first."
    rows = ctx.find("customers", customer_id=customer_id)
    if not rows:
        return f"Error: no customer profile {customer_id}; cannot verify."
    rec = rows[0]
    supplied = {"phone_number": phone_number, "email": email, "postal_code": postal_code,
                "account_pin": account_pin}

    def _norm(value):
        # compare letters and digits only, case-insensitively
        return "".join(ch for ch in str(value).casefold() if ch.isalnum())

    matched = sum(1 for field, value in supplied.items()
                  if value and rec.get(field) not in (None, "") and _norm(rec.get(field)) == _norm(value))
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
        return f"Identity verified for customer {customer_id}."
    return (f"Identity NOT verified for customer {customer_id}: {matched} of the 2 required details matched. "
            "Ask the caller for another detail on file and try again.")


@tool(owner="agent", rw="write")
def transfer_to_human_agent(ctx: ToolContext, customer_id: str, reason: str) -> str:
    """Hand the customer over to a human representative and record the handoff with its reason.

    Use it when no published policy can resolve what the customer needs, or when the customer has
    explicitly asked for a human representative twice.

    Args:
        customer_id: Customer reference number from the customer profile lookup; the profile must exist.
        reason: Exactly one of two values. POLICY_NOT_COVERED: no published policy can resolve the request. CUSTOMER_REQUESTED: the customer has explicitly asked for a human representative at least 2 times.
    """
    allowed = {"POLICY_NOT_COVERED", "CUSTOMER_REQUESTED"}
    if reason not in allowed:
        return f"Error: unknown handoff reason '{reason}'. Valid: {', '.join(sorted(allowed))}."
    if not ctx.find("customers", customer_id=customer_id):
        return f"Error: no customer profile {customer_id}; cannot record the handoff."
    rid = ctx.make_id("hof_", customer_id, reason)
    ctx.create("handoff_log", rid, handoff_id=rid, customer_id=customer_id, reason=reason, created_at=ctx.now())
    return f"Handoff to a human representative recorded for customer {customer_id} ({reason})."

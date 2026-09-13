"""Shared tools for global_container_shipping_line (Aurelia Hanse Line customer service desk).

Every tool here is a SHARE tool: always present in its owner's tool list and directly callable in
every task. The file holds exactly the three foundation utilities every difficulty reuses:
  - the record-lookup layer: one finder per table, each taking all of that table's id fields as
    optional criteria (the customers finder doubles as the identity entry and also accepts the
    attributes a caller can naturally state);
  - the identity-verification write (the tool itself compares the stated credentials against the
    profile, passes at K = 2 matches, and stores only the reproducible verified boolean);
  - the transfer-to-human write (reason closed at POLICY_NOT_COVERED / CUSTOMER_REQUESTED; the
    repeat-request threshold R = 2).
Customer-originated business writes (countersigning, surrendering originals, signing a declaration,
lodging a claim or dispute) are hidden task tools authored per difficulty, never here.
"""

from erlbench import ToolContext, tool


def _pick(**criteria):
    # keep only the criteria the caller actually supplied
    return {k: v for k, v in criteria.items() if v}


# ----------------------------------------------------------------------------------------------
# Customer profile — identity entry
# ----------------------------------------------------------------------------------------------
@tool(owner="agent", rw="read")
def find_customers(ctx: ToolContext, customer_id: str = "", phone_number: str = "", email: str = "",
                   customer_code: str = "", company_name: str = "", contact_name: str = "") -> str:
    """Look up the company profile a caller is speaking for, so you know whose shipments, contracts and invoices the conversation is about.

    You may search by the customer reference number or by anything the caller can naturally tell you:
    the registered phone number, the registered email address, the Aurelia Hanse Line customer code
    printed on invoices, the registered company name or the name of the registered contact person.
    Every criterion is optional; supply whichever you have and they are combined. A single match
    returns the full profile: company and contact names, phone, email, customer code, tax or customs
    registration number, the date the profile was opened, the commercial role (cargo owner, freight
    forwarder or NVOCC), country, credit standing and payment term, and whether the company is
    enrolled on the electronic bill of lading platform. Finding a profile does not prove the caller
    is who they claim to be; identity is confirmed separately.

    Args:
        customer_id: Customer reference number of the profile, if already known; leave "" otherwise.
        phone_number: Registered phone number in international form exactly as stated, e.g. +4940300512877; leave "" if not given.
        email: Registered email address exactly as stated; leave "" if not given.
        customer_code: Aurelia Hanse Line customer code, e.g. AHL-DE-204417; leave "" if not given.
        company_name: Registered company name exactly as stated; leave "" if not given.
        contact_name: Full name of the registered contact person exactly as stated; leave "" if not given.
    """
    match = _pick(customer_id=customer_id, phone_number=phone_number, email=email,
                  customer_code=customer_code, company_name=company_name, contact_name=contact_name)
    if not match:
        return "Error: provide at least one reference number or profile detail to find the customer."
    rows = ctx.find("customers", **match)
    if not rows:
        return f"No customer profile matches {match}."
    if len(rows) > 1:
        return (f"Error: {len(rows)} customer profiles match {match}; ask the caller for one more "
                "detail to tell them apart.")
    return str(rows[0])


@tool(owner="agent", rw="read")
def find_identity_verifications(ctx: ToolContext, verification_id: str = "", customer_id: str = "") -> str:
    """Show whether a customer's caller identity has already been confirmed in this service session, and when it was last checked.

    Args:
        verification_id: Reference number of the verification record, if known; leave "" otherwise.
        customer_id: Customer reference number whose verification outcome you want to see; leave "" if unknown.
    """
    match = _pick(verification_id=verification_id, customer_id=customer_id)
    rows = ctx.find("identity_verifications", **match)
    return str(rows) if rows else f"No identity verification on record for {match}."


@tool(owner="agent", rw="read")
def find_human_handoffs(ctx: ToolContext, handoff_id: str = "", customer_id: str = "") -> str:
    """List handovers of a customer to a human representative, with the recorded reason and time.

    Args:
        handoff_id: Reference number of a specific handover, if known; leave "" otherwise.
        customer_id: Customer reference number whose handovers you want to list; leave "" if unknown.
    """
    match = _pick(handoff_id=handoff_id, customer_id=customer_id)
    rows = ctx.find("human_handoffs", **match)
    return str(rows) if rows else f"No handover to a human representative on record for {match}."


# ----------------------------------------------------------------------------------------------
# Service contracts
# ----------------------------------------------------------------------------------------------
@tool(owner="agent", rw="read")
def find_service_contracts(ctx: ToolContext, contract_id: str = "", customer_id: str = "") -> str:
    """Retrieve service contracts: the contract tier, trade lane, minimum quantity commitment, rate basis, term dates, current status, volume lifted so far, unpaid shortfall and accrued volume rebate.

    Search by the contract reference or list every contract a customer holds.

    Args:
        contract_id: Contract reference number; leave "" if unknown.
        customer_id: Customer reference number of the contract holder; leave "" if unknown.
    """
    match = _pick(contract_id=contract_id, customer_id=customer_id)
    rows = ctx.find("service_contracts", **match)
    return str(rows) if rows else f"No service contracts found for {match}."


@tool(owner="agent", rw="read")
def find_contract_ledger(ctx: ToolContext, contract_event_id: str = "", contract_id: str = "",
                         customer_id: str = "", booking_id: str = "", reference_event_id: str = "") -> str:
    """Retrieve the contract account history: volume credited for each departed booking and its reversals, quarterly and end-of-term shortfall assessments, shortfall payments and waivers, volume rebate accruals and settlements, filed amendments and quarterly index adjustments.

    Each entry shows its date, amount, FEU volume, assessment period and, for payments, waivers,
    settlements and reversals, the reference of the original entry it relates to.

    Args:
        contract_event_id: Reference of one specific contract account entry; leave "" if unknown.
        contract_id: Contract reference number whose history you want; leave "" if unknown.
        customer_id: Customer reference number of the contract holder; leave "" if unknown.
        booking_id: Booking reference number whose volume credit or reversal you want; leave "" if unknown.
        reference_event_id: Reference of an original entry, to find the entries that pay, waive, settle or reverse it; leave "" if unknown.
    """
    match = _pick(contract_event_id=contract_event_id, contract_id=contract_id, customer_id=customer_id,
                  booking_id=booking_id, reference_event_id=reference_event_id)
    rows = ctx.find("contract_ledger", **match)
    return str(rows) if rows else f"No contract account entries found for {match}."


@tool(owner="agent", rw="read")
def find_contract_amendment_requests(ctx: ToolContext, request_id: str = "", customer_id: str = "",
                                     contract_id: str = "") -> str:
    """Retrieve requests to amend or terminate a service contract — commitment changes, term extensions, added named accounts and early terminations — with what was asked for and whether the customer has signed, withdrawn or been declined.

    Args:
        request_id: Reference number of the request; leave "" if unknown.
        customer_id: Customer reference number of the requesting contract holder; leave "" if unknown.
        contract_id: Contract reference number the request concerns; leave "" if unknown.
    """
    match = _pick(request_id=request_id, customer_id=customer_id, contract_id=contract_id)
    rows = ctx.find("contract_amendment_requests", **match)
    return str(rows) if rows else f"No contract amendment or termination requests found for {match}."


# ----------------------------------------------------------------------------------------------
# Bookings
# ----------------------------------------------------------------------------------------------
@tool(owner="agent", rw="read")
def find_bookings(ctx: ToolContext, booking_id: str = "", customer_id: str = "", contract_id: str = "",
                  booking_number: str = "") -> str:
    """Retrieve container bookings: the booking product, status, port pair and trade lane, allocated vessel and voyage, equipment type and quantity, cargo category, freight terms, booking channel, cut-off times and when shipping instructions and verified gross mass were received, departure date and the booking charges still outstanding.

    Search by the booking reference, by the booking number the customer quotes from the
    confirmation, by the service contract the booking is rated under, or list a customer's bookings.

    Args:
        booking_id: Booking reference number; leave "" if unknown.
        customer_id: Customer reference number of the booking party; leave "" if unknown.
        contract_id: Contract reference number, to list the bookings rated under that contract; leave "" if unknown.
        booking_number: Booking number exactly as printed on the booking confirmation, e.g. AHLU26HAM041872; leave "" if not given.
    """
    match = _pick(booking_id=booking_id, customer_id=customer_id, contract_id=contract_id,
                  booking_number=booking_number)
    rows = ctx.find("bookings", **match)
    return str(rows) if rows else f"No bookings found for {match}."


@tool(owner="agent", rw="read")
def find_booking_charges(ctx: ToolContext, booking_event_id: str = "", booking_id: str = "",
                         customer_id: str = "", reference_event_id: str = "") -> str:
    """Retrieve the charge history of a booking: freight and surcharges, cancellation and no-show fees, late shipping-instruction and late VGM fees, amendment fees, roll notices and roll compensation, payments received and waivers granted.

    Each entry shows its date, tariff code, amount, container count, equipment, vessel voyage and,
    for waivers and compensation, the reference of the original entry it relates to.

    Args:
        booking_event_id: Reference of one specific booking charge entry; leave "" if unknown.
        booking_id: Booking reference number whose charges you want; leave "" if unknown.
        customer_id: Customer reference number of the booking party; leave "" if unknown.
        reference_event_id: Reference of an original charge or roll entry, to find the waivers or compensation tied to it; leave "" if unknown.
    """
    match = _pick(booking_event_id=booking_event_id, booking_id=booking_id, customer_id=customer_id,
                  reference_event_id=reference_event_id)
    rows = ctx.find("booking_charges", **match)
    return str(rows) if rows else f"No booking charge entries found for {match}."


# ----------------------------------------------------------------------------------------------
# Bills of lading
# ----------------------------------------------------------------------------------------------
@tool(owner="agent", rw="read")
def find_bills_of_lading(ctx: ToolContext, bl_id: str = "", customer_id: str = "", booking_id: str = "",
                         bl_number: str = "") -> str:
    """Retrieve transport documents — sea waybills, electronic, straight, negotiable, combined transport and switch bills of lading — with their status, printed particulars (shipper, consignee, notify party, cargo description, packages, weight, ports and place of delivery), declared cargo value, issue and release dates, the set of originals in force, originals still outstanding and documentation charges due.

    Args:
        bl_id: Transport document reference number; leave "" if unknown.
        customer_id: Customer reference number of the documentation party; leave "" if unknown.
        booking_id: Booking reference number the document covers; leave "" if unknown.
        bl_number: Document number exactly as printed on the bill of lading or waybill, e.g. AHLU2604417790; leave "" if not given.
    """
    match = _pick(bl_id=bl_id, customer_id=customer_id, booking_id=booking_id, bl_number=bl_number)
    rows = ctx.find("bills_of_lading", **match)
    return str(rows) if rows else f"No transport documents found for {match}."


@tool(owner="agent", rw="read")
def find_bol_ledger(ctx: ToolContext, bol_event_id: str = "", bl_id: str = "", customer_id: str = "",
                    request_id: str = "", reference_event_id: str = "") -> str:
    """Retrieve the documentation history of a transport document: issuance, correction, release, switch and reissue fees, originals issued and surrendered (with the office where they were surrendered), the recorded basis of cargo release, payments and waivers.

    Args:
        bol_event_id: Reference of one specific documentation entry; leave "" if unknown.
        bl_id: Transport document reference number; leave "" if unknown.
        customer_id: Customer reference number of the documentation party; leave "" if unknown.
        request_id: Reference of a documentation service request, to see the entries it produced; leave "" if unknown.
        reference_event_id: Reference of an original fee entry, to find a waiver tied to it; leave "" if unknown.
    """
    match = _pick(bol_event_id=bol_event_id, bl_id=bl_id, customer_id=customer_id, request_id=request_id,
                  reference_event_id=reference_event_id)
    rows = ctx.find("bol_ledger", **match)
    return str(rows) if rows else f"No documentation entries found for {match}."


@tool(owner="agent", rw="read")
def find_bol_service_requests(ctx: ToolContext, request_id: str = "", customer_id: str = "", bl_id: str = "") -> str:
    """Retrieve documentation service requests — corrections, telex releases, switch bills, reissues of lost originals and releases against a letter of indemnity — with the particular and new wording requested, any bank guarantee amount, and whether the request awaits the customer, is completed, withdrawn or declined.

    Args:
        request_id: Reference number of the request; leave "" if unknown.
        customer_id: Customer reference number of the requesting party; leave "" if unknown.
        bl_id: Transport document reference number the request concerns; leave "" if unknown.
    """
    match = _pick(request_id=request_id, customer_id=customer_id, bl_id=bl_id)
    rows = ctx.find("bol_service_requests", **match)
    return str(rows) if rows else f"No documentation service requests found for {match}."


# ----------------------------------------------------------------------------------------------
# Demurrage and detention
# ----------------------------------------------------------------------------------------------
@tool(owner="agent", rw="read")
def find_dnd_free_time(ctx: ToolContext, dnd_id: str = "", customer_id: str = "", booking_id: str = "",
                       container_number: str = "") -> str:
    """Retrieve per-container free-time records for demurrage and detention: the free-time product applied, whether the import or export clock is running, accruing, stopped, invoiced or settled, the port, the equipment type, the recorded discharge, gate-out, empty-return, empty-pickup, gate-in and loading dates, and the balance still due.

    Args:
        dnd_id: Free-time record reference number; leave "" if unknown.
        customer_id: Customer reference number of the billed party; leave "" if unknown.
        booking_id: Booking reference number the container moves under; leave "" if unknown.
        container_number: Container number exactly as quoted, e.g. AHLU4417902; leave "" if not given.
    """
    match = _pick(dnd_id=dnd_id, customer_id=customer_id, booking_id=booking_id,
                  container_number=container_number)
    rows = ctx.find("dnd_free_time", **match)
    return str(rows) if rows else f"No free-time records found for {match}."


@tool(owner="agent", rw="read")
def find_dnd_ledger(ctx: ToolContext, dnd_event_id: str = "", dnd_id: str = "", customer_id: str = "",
                    reference_event_id: str = "", dispute_id: str = "") -> str:
    """Retrieve demurrage and detention account entries: invoices with their chargeable days and period, free-time extension purchases, payments, waivers and dispute credits.

    The reference of an invoice entry is the invoice reference customers quote.

    Args:
        dnd_event_id: Reference of one specific entry, such as an invoice reference; leave "" if unknown.
        dnd_id: Free-time record reference number; leave "" if unknown.
        customer_id: Customer reference number of the billed party; leave "" if unknown.
        reference_event_id: Reference of an invoice, to find the payments, waivers and credits applied to it; leave "" if unknown.
        dispute_id: Reference of a dispute, to find the credit that resolved it; leave "" if unknown.
    """
    match = _pick(dnd_event_id=dnd_event_id, dnd_id=dnd_id, customer_id=customer_id,
                  reference_event_id=reference_event_id, dispute_id=dispute_id)
    rows = ctx.find("dnd_ledger", **match)
    return str(rows) if rows else f"No demurrage and detention entries found for {match}."


@tool(owner="agent", rw="read")
def find_dnd_disputes(ctx: ToolContext, dispute_id: str = "", customer_id: str = "", dnd_id: str = "",
                      invoice_event_id: str = "") -> str:
    """Retrieve disputes lodged against demurrage and detention invoices, with the ground, the amount disputed, the outcome so far and when the dispute was lodged.

    Args:
        dispute_id: Dispute reference number; leave "" if unknown.
        customer_id: Customer reference number of the disputing party; leave "" if unknown.
        dnd_id: Free-time record reference number; leave "" if unknown.
        invoice_event_id: Invoice reference the dispute is lodged against; leave "" if unknown.
    """
    match = _pick(dispute_id=dispute_id, customer_id=customer_id, dnd_id=dnd_id,
                  invoice_event_id=invoice_event_id)
    rows = ctx.find("dnd_disputes", **match)
    return str(rows) if rows else f"No invoice disputes found for {match}."


# ----------------------------------------------------------------------------------------------
# Reefer services
# ----------------------------------------------------------------------------------------------
@tool(owner="agent", rw="read")
def find_reefer_services(ctx: ToolContext, reefer_id: str = "", customer_id: str = "", booking_id: str = "",
                         container_number: str = "") -> str:
    """Retrieve refrigerated-cargo service orders: the reefer service tier, status, commodity, carrying temperature, ventilation and humidity settings, plug-in and delivery dates and the reefer charges outstanding.

    Args:
        reefer_id: Reefer service reference number; leave "" if unknown.
        customer_id: Customer reference number of the ordering party; leave "" if unknown.
        booking_id: Booking reference number carrying the reefer; leave "" if unknown.
        container_number: Reefer container number exactly as quoted; leave "" if not given.
    """
    match = _pick(reefer_id=reefer_id, customer_id=customer_id, booking_id=booking_id,
                  container_number=container_number)
    rows = ctx.find("reefer_services", **match)
    return str(rows) if rows else f"No reefer service orders found for {match}."


@tool(owner="agent", rw="read")
def find_reefer_ledger(ctx: ToolContext, reefer_event_id: str = "", reefer_id: str = "", customer_id: str = "",
                       reference_event_id: str = "") -> str:
    """Retrieve the reefer service account: pre-trip inspection fees, terminal plug-in and monitoring days, special-service surcharges, set-point change fees, logged temperature excursions, excursion credits, payments and waivers.

    Args:
        reefer_event_id: Reference of one specific reefer entry; leave "" if unknown.
        reefer_id: Reefer service reference number; leave "" if unknown.
        customer_id: Customer reference number of the ordering party; leave "" if unknown.
        reference_event_id: Reference of an original entry, to find the credits or waivers tied to it; leave "" if unknown.
    """
    match = _pick(reefer_event_id=reefer_event_id, reefer_id=reefer_id, customer_id=customer_id,
                  reference_event_id=reference_event_id)
    rows = ctx.find("reefer_ledger", **match)
    return str(rows) if rows else f"No reefer account entries found for {match}."


# ----------------------------------------------------------------------------------------------
# Dangerous goods
# ----------------------------------------------------------------------------------------------
@tool(owner="agent", rw="read")
def find_dg_acceptances(ctx: ToolContext, dg_id: str = "", customer_id: str = "", booking_id: str = "") -> str:
    """Retrieve dangerous-goods acceptance records: the acceptance category, status, UN number, proper shipping name, IMDG class, packing group, marine-pollutant marking, containers and weight, trade lane, submission and approval dates and the dangerous-goods charges outstanding.

    Args:
        dg_id: Dangerous-goods acceptance reference number; leave "" if unknown.
        customer_id: Customer reference number of the applicant; leave "" if unknown.
        booking_id: Booking reference number the goods travel under; leave "" if unknown.
    """
    match = _pick(dg_id=dg_id, customer_id=customer_id, booking_id=booking_id)
    rows = ctx.find("dg_acceptances", **match)
    return str(rows) if rows else f"No dangerous-goods acceptance records found for {match}."


@tool(owner="agent", rw="read")
def find_dg_ledger(ctx: ToolContext, dg_event_id: str = "", dg_id: str = "", customer_id: str = "",
                   submission_id: str = "", reference_event_id: str = "") -> str:
    """Retrieve the dangerous-goods account: hazardous-cargo surcharges, late declaration and amendment fees, misdeclaration penalties, payments and waivers.

    Args:
        dg_event_id: Reference of one specific dangerous-goods entry; leave "" if unknown.
        dg_id: Dangerous-goods acceptance reference number; leave "" if unknown.
        customer_id: Customer reference number of the applicant; leave "" if unknown.
        submission_id: Reference of a declaration submission, to see the charges it produced; leave "" if unknown.
        reference_event_id: Reference of an original charge, to find a waiver tied to it; leave "" if unknown.
    """
    match = _pick(dg_event_id=dg_event_id, dg_id=dg_id, customer_id=customer_id, submission_id=submission_id,
                  reference_event_id=reference_event_id)
    rows = ctx.find("dg_ledger", **match)
    return str(rows) if rows else f"No dangerous-goods account entries found for {match}."


@tool(owner="agent", rw="read")
def find_dg_declaration_submissions(ctx: ToolContext, submission_id: str = "", customer_id: str = "",
                                    dg_id: str = "") -> str:
    """Retrieve the shipper's dangerous-goods declarations submitted for an acceptance — first declarations and amendments — with the UN number, class and packing group declared and whether each declaration is signed, awaiting signature, returned for correction or withdrawn.

    Args:
        submission_id: Declaration submission reference number; leave "" if unknown.
        customer_id: Customer reference number of the declaring shipper; leave "" if unknown.
        dg_id: Dangerous-goods acceptance reference number; leave "" if unknown.
    """
    match = _pick(submission_id=submission_id, customer_id=customer_id, dg_id=dg_id)
    rows = ctx.find("dg_declaration_submissions", **match)
    return str(rows) if rows else f"No dangerous-goods declarations found for {match}."


# ----------------------------------------------------------------------------------------------
# Cargo liability, CargoCare and claims
# ----------------------------------------------------------------------------------------------
@tool(owner="agent", rw="read")
def find_cargo_covers(ctx: ToolContext, cover_id: str = "", customer_id: str = "", bl_id: str = "",
                      booking_id: str = "") -> str:
    """Retrieve cargo liability and CargoCare covers attached to shipments: the liability regime or CargoCare product, status, insured value, packages, weight, containers, cargo category, binding and delivery dates, premium still due and approved settlements not yet paid.

    Args:
        cover_id: Cover reference number; leave "" if unknown.
        customer_id: Customer reference number of the cover holder; leave "" if unknown.
        bl_id: Transport document reference number the cover attaches to; leave "" if unknown.
        booking_id: Booking reference number of the covered shipment; leave "" if unknown.
    """
    match = _pick(cover_id=cover_id, customer_id=customer_id, bl_id=bl_id, booking_id=booking_id)
    rows = ctx.find("cargo_covers", **match)
    return str(rows) if rows else f"No cargo covers found for {match}."


@tool(owner="agent", rw="read")
def find_claims_ledger(ctx: ToolContext, claims_event_id: str = "", cover_id: str = "", customer_id: str = "",
                       claim_id: str = "", reference_event_id: str = "") -> str:
    """Retrieve the premium and claim settlement account of a cover: premiums charged, paid and refunded, settlements approved (with the cap that determined them) and paid out, and claim rejections with their controlled reason.

    Args:
        claims_event_id: Reference of one specific entry; leave "" if unknown.
        cover_id: Cover reference number; leave "" if unknown.
        customer_id: Customer reference number of the cover holder; leave "" if unknown.
        claim_id: Claim reference number, to see its settlement, payment or rejection; leave "" if unknown.
        reference_event_id: Reference of an original premium or settlement entry, to find the payment or refund tied to it; leave "" if unknown.
    """
    match = _pick(claims_event_id=claims_event_id, cover_id=cover_id, customer_id=customer_id,
                  claim_id=claim_id, reference_event_id=reference_event_id)
    rows = ctx.find("claims_ledger", **match)
    return str(rows) if rows else f"No premium or claim settlement entries found for {match}."


@tool(owner="agent", rw="read")
def find_cargo_claims(ctx: ToolContext, claim_id: str = "", customer_id: str = "", cover_id: str = "") -> str:
    """Retrieve cargo claim files: the container affected, the nature of the loss, whether it was apparent at delivery, the date notice reached the line, the amount, packages and weight claimed, and the adjudication state.

    Args:
        claim_id: Claim reference number; leave "" if unknown.
        customer_id: Customer reference number of the claimant; leave "" if unknown.
        cover_id: Cover reference number the claim is lodged under; leave "" if unknown.
    """
    match = _pick(claim_id=claim_id, customer_id=customer_id, cover_id=cover_id)
    rows = ctx.find("cargo_claims", **match)
    return str(rows) if rows else f"No cargo claim files found for {match}."


# ----------------------------------------------------------------------------------------------
# Identity verification (K = 2)
# ----------------------------------------------------------------------------------------------
@tool(owner="agent", rw="write")
def verify_customer_identity(ctx: ToolContext, customer_id: str, phone_number: str = "", email: str = "",
                             customer_code: str = "", tax_registration_number: str = "",
                             profile_opened_date: str = "") -> str:
    """Confirm that the caller is entitled to act for a company profile, and record the outcome; no account business may be transacted for a caller whose identity has not been confirmed.

    The comparison is made here, not by you: each detail the caller states is checked against the
    profile on file, and the caller is confirmed when at least 2 of the stated details match. The
    customer reference number only identifies which profile to check against and never counts as a
    matching detail, and neither does a company or contact name. Callers usually know only some of
    their details, so pass exactly the values the caller gave, copied as stated, and leave the rest
    empty. If a first attempt falls short and the caller later supplies further details that bring
    the matches to 2, the confirmation stands from then on.

    Args:
        customer_id: Customer reference number of the profile to check against, as returned by the customer profile lookup. Required; not counted as a matching detail.
        phone_number: Registered phone number as stated by the caller, in international form, e.g. +4940300512877; leave "" if not stated.
        email: Registered email address as stated by the caller; leave "" if not stated.
        customer_code: Aurelia Hanse Line customer code as stated by the caller, e.g. AHL-DE-204417; leave "" if not stated.
        tax_registration_number: Company tax or customs registration number (EORI, VAT, EIN or USCI) as stated by the caller; leave "" if not stated.
        profile_opened_date: Date the company profile was opened with the line, as YYYY-MM-DD; leave "" if not stated.
    """
    if not customer_id:
        return "Error: customer_id is required; look up the customer profile first and pass its reference number."
    rows = ctx.find("customers", customer_id=customer_id)
    if not rows:
        return f"Error: no customer profile {customer_id}; cannot verify."
    rec = rows[0]
    # The locator customer_id is deliberately not a credential; names are not credentials either.
    supplied = {"phone_number": phone_number, "email": email, "customer_code": customer_code,
                "tax_registration_number": tax_registration_number,
                "profile_opened_date": profile_opened_date}
    matched = sum(1 for field, value in supplied.items()
                  if value and str(rec.get(field, "")).strip() == str(value).strip())
    verified = matched >= 2
    rid = ctx.make_id("ver_", customer_id)
    # upsert, monotonic: a later pass must win over an earlier miss; never downgrade True -> False
    prior = ctx.find("identity_verifications", verification_id=rid)
    verified = verified or bool(prior and prior[0].get("verified"))
    if prior:
        ctx.update("identity_verifications", rid, verified=verified, verified_at=ctx.now())
    else:
        ctx.create("identity_verifications", rid, verification_id=rid, customer_id=customer_id,
                   verified=verified, verified_at=ctx.now())
    if verified:
        return f"Identity confirmed for customer {customer_id} ({matched} detail(s) matched in this attempt)."
    return (f"Identity NOT confirmed for customer {customer_id}: only {matched} of the 2 required details "
            "matched. Ask the caller for another detail on file and try again.")


# ----------------------------------------------------------------------------------------------
# Transfer to a human representative (R = 2)
# ----------------------------------------------------------------------------------------------
@tool(owner="agent", rw="write")
def transfer_to_human_agent(ctx: ToolContext, customer_id: str, reason: str) -> str:
    """Hand the customer over to a human representative of the Aurelia Hanse Line customer service desk, and record the handover with its reason.

    Use it in exactly two situations. The first is when no published rule of the line allows the
    request to be resolved at this desk. The second is when the customer has explicitly asked to
    speak to a human representative 2 times in this conversation.

    Args:
        customer_id: Customer reference number of the profile being handed over, as returned by the customer profile lookup.
        reason: Why the customer is handed over; exactly one of POLICY_NOT_COVERED (no published rule allows this request to be resolved here) or CUSTOMER_REQUESTED (the customer has explicitly asked for a human representative 2 times). Never free text.
    """
    allowed = {"POLICY_NOT_COVERED", "CUSTOMER_REQUESTED"}
    if reason not in allowed:
        return f"Error: unknown handover reason '{reason}'. Valid values: {', '.join(sorted(allowed))}."
    if not ctx.find("customers", customer_id=customer_id):
        return f"Error: no customer profile {customer_id}; cannot record the handover."
    rid = ctx.make_id("hof_", customer_id, reason)
    ctx.create("human_handoffs", rid, handoff_id=rid, customer_id=customer_id, reason=reason,
               created_at=ctx.now())
    return f"Handover to a human representative recorded for customer {customer_id} ({reason})."

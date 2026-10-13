"""Shared tools for env_0053_agricultural_lending_cooperative (Cottonwood Plains Farm Credit, ACA).

Every tool here is a SHARE tool: always present in its owner's tool list in every task.
It holds the three foundation utilities every difficulty reuses:
  - the record-lookup layer: one finder per table, each taking all of that table's reference-number
    (`_id`) fields as optional criteria; the customers finder doubles as the identity entry and also
    accepts what a caller can naturally state (name, phone number, email, membership number);
  - the identity-verification write (the tool compares the stated credentials with the membership
    record itself; K = 2 matching credentials are required; only the boolean outcome is stored);
  - the transfer-to-human write (exactly two reasons; R = 2 explicit requests for CUSTOMER_REQUESTED).
Customer-originated writes (consents, signatures, disposing of the member's own assets) are hidden
task tools authored per difficulty, never placed here.
"""

from erlbench import ToolContext, tool


def _criteria(values: dict) -> dict:
    # Shared helper (not a tool): keep only the reference numbers actually supplied.
    return {k: v for k, v in values.items() if v}


def _render(rows: list, match: dict, label: str) -> str:
    # Shared helper (not a tool): uniform hit / miss wording.
    return str(rows) if rows else f"No {label} found for {match}."


# ----------------------------------------------------------------------------- members
@tool(owner="agent", rw="read")
def find_customers(ctx: ToolContext, customer_id: str = "", name: str = "", phone_number: str = "",
                   email: str = "", member_number: str = "") -> str:
    """Look up a member's profile to establish whose accounts this conversation is about.

    A member can be found by the internal customer reference, or by what a caller can naturally tell you:
    the name on the membership, the phone number or email address on file, or the membership number
    printed on stock certificates, statements and patronage notices. Supply whichever are known; spacing,
    punctuation and capitalisation do not matter. The profile returned shows the member's legal name,
    whether the member is an individual, joint borrowers or a farm or agribusiness entity, the member's
    segment (farm operator, agribusiness or rural homeowner), contact details, the date the membership
    was opened, date of birth and first farming year where applicable. Finding a profile does not verify
    the caller's identity. If several members match, you are asked for one more detail.

    Args:
        customer_id: The internal customer reference number; leave "" if unknown.
        name: The member's name as the caller states it (an individual's full name, joint borrowers' names, or the entity's registered name); leave "" if not given.
        phone_number: The phone number on file as the caller states it, 10 digits; leave "" if not given.
        email: The email address on file as the caller states it; leave "" if not given.
        member_number: The membership number as the caller reads it, e.g. CPF-0418823; leave "" if not given.
    """
    match = {k: v for k, v in {"customer_id": customer_id, "name": name, "phone_number": phone_number,
                               "email": email, "member_number": member_number}.items() if v}
    if not match:
        return "Error: provide at least one detail to find the member."
    rows = ctx.fuzzy_find("customers", **match)
    if not rows:
        return f"No member matches {match}."
    if len(rows) > 1:
        return f"Error: {len(rows)} members match {match}; ask the caller for one more detail to tell them apart."
    return str(rows[0])


@tool(owner="agent", rw="read")
def find_verification_log(ctx: ToolContext, verification_id: str = "", customer_id: str = "") -> str:
    """Look up the outcome of identity verification for a member in this conversation.

    Shows whether the caller has passed identity verification for the member and when the latest check
    was made. Search by the member's customer reference or by the verification reference.

    Args:
        verification_id: Reference number of the verification record; leave "" if unknown.
        customer_id: Customer reference of the member checked; leave "" if unknown.
    """
    match = _criteria({"verification_id": verification_id, "customer_id": customer_id})
    if not match:
        return "Error: provide at least one reference number to look up identity verification records."
    return _render(ctx.find("verification_log", **match), match, "identity verification records")


@tool(owner="agent", rw="read")
def find_handoff_log(ctx: ToolContext, handoff_id: str = "", customer_id: str = "") -> str:
    """Look up transfers of a member to a human loan officer or servicing specialist.

    Shows each recorded transfer with its reason and time. Search by the member's customer reference or
    by the transfer reference.

    Args:
        handoff_id: Reference number of the transfer record; leave "" if unknown.
        customer_id: Customer reference of the member transferred; leave "" if unknown.
    """
    match = _criteria({"handoff_id": handoff_id, "customer_id": customer_id})
    if not match:
        return "Error: provide at least one reference number to look up transfer records."
    return _render(ctx.find("handoff_log", **match), match, "transfer records")


# ----------------------------------------------------------------------------- operating lines
@tool(owner="agent", rw="read")
def find_operating_lines(ctx: ToolContext, line_id: str = "", customer_id: str = "") -> str:
    """Look up a member's operating lines of credit and seasonal operating loans.

    Each line shows the product, its status (applied, active, suspended, matured, closed or declined),
    the commitment, outstanding principal, booked interest and fees not yet paid, the contract rate,
    AutoDraft enrolment, the crop year financed, the booking, maturity and advance cutoff dates, the last
    renewal and how many streamlined renewals have run, and why advances are frozen if they are.

    Args:
        line_id: Loan number of the operating line; leave "" if unknown.
        customer_id: Customer reference of the borrowing member, to list all of the member's lines; leave "" if unknown.
    """
    match = _criteria({"line_id": line_id, "customer_id": customer_id})
    if not match:
        return "Error: provide at least one reference number to look up operating lines."
    return _render(ctx.find("operating_lines", **match), match, "operating lines")


@tool(owner="agent", rw="read")
def find_operating_transactions(ctx: ToolContext, txn_id: str = "", line_id: str = "", customer_id: str = "",
                                source_txn_id: str = "") -> str:
    """Look up the transaction history of operating lines: advances, payments, interest bills and fees.

    Each entry shows its type, amount, effective date and channel; advances show how proceeds were
    delivered, interest bills show the period covered, the rate and the due date, fee entries show which
    fee, and payments, waivers and returned payments point to the bill, fee or payment they relate to.
    Search by the line, the member, a transaction reference, or the reference of a related transaction
    (for example, everything that relates to one interest bill).

    Args:
        txn_id: Reference number of one transaction; leave "" if unknown.
        line_id: Loan number of the operating line; leave "" if unknown.
        customer_id: Customer reference of the member; leave "" if unknown.
        source_txn_id: Reference of a transaction others relate to (a bill, fee, advance or payment), to find the entries tied to it; leave "" if unknown.
    """
    match = _criteria({"txn_id": txn_id, "line_id": line_id, "customer_id": customer_id, "source_txn_id": source_txn_id})
    if not match:
        return "Error: provide at least one reference number to look up operating line transactions."
    return _render(ctx.find("operating_transactions", **match), match, "operating line transactions")


@tool(owner="agent", rw="read")
def find_operating_borrowing_base(ctx: ToolContext, certificate_id: str = "", line_id: str = "",
                                  customer_id: str = "") -> str:
    """Look up borrowing base certificates delivered for a line.

    Each certificate shows its as-of date and the date it was received, the collateral values stated —
    unpriced and contracted stored grain, market livestock, eligible receivables, prepaid inputs and
    insured growing crops — the resulting borrowing base and how it was delivered.

    Args:
        certificate_id: Reference number of one certificate; leave "" if unknown.
        line_id: Loan number of the line the certificates support; leave "" if unknown.
        customer_id: Customer reference of the member; leave "" if unknown.
    """
    match = _criteria({"certificate_id": certificate_id, "line_id": line_id, "customer_id": customer_id})
    if not match:
        return "Error: provide at least one reference number to look up borrowing base certificates."
    return _render(ctx.find("operating_borrowing_base", **match), match, "borrowing base certificates")


@tool(owner="agent", rw="read")
def find_operating_requests(ctx: ToolContext, request_id: str = "", customer_id: str = "", line_id: str = "") -> str:
    """Look up renewal, commitment increase and line closure requests on operating lines.

    Each request shows what was asked, the amount requested, its status (submitted, approved, declined or
    withdrawn) and when it was registered.

    Args:
        request_id: Reference number of the request; leave "" if unknown.
        customer_id: Customer reference of the requesting member; leave "" if unknown.
        line_id: Loan number of the line concerned; leave "" if unknown.
    """
    match = _criteria({"request_id": request_id, "customer_id": customer_id, "line_id": line_id})
    if not match:
        return "Error: provide at least one reference number to look up operating line requests."
    return _render(ctx.find("operating_requests", **match), match, "operating line requests")


# ----------------------------------------------------------------------------- equipment loans
@tool(owner="agent", rw="read")
def find_equipment_loans(ctx: ToolContext, loan_id: str = "", customer_id: str = "") -> str:
    """Look up a member's equipment and vehicle loans.

    Each loan shows the product, its status (applied, active, deferred, nonaccrual, paid off or declined),
    original and current principal, billed interest and fees not yet paid, the pledged value of the
    units securing it, the rate and whether it is fixed or variable, the installment, its frequency, the
    next due date and maturity, deferrals used, autopay, the insurance on record, the originating dealer
    for a dealer contract, and the funding and closing dates.

    Args:
        loan_id: Loan number of the equipment loan; leave "" if unknown.
        customer_id: Customer reference of the borrowing member, to list all of the member's equipment loans; leave "" if unknown.
    """
    match = _criteria({"loan_id": loan_id, "customer_id": customer_id})
    if not match:
        return "Error: provide at least one reference number to look up equipment loans."
    return _render(ctx.find("equipment_loans", **match), match, "equipment loans")


@tool(owner="agent", rw="read")
def find_equipment_transactions(ctx: ToolContext, txn_id: str = "", loan_id: str = "", customer_id: str = "",
                                source_ref_id: str = "") -> str:
    """Look up the transaction history of equipment loans: installment bills, payments, fees and reversals.

    Each entry shows its type, amount, effective date and channel; installment bills show the period,
    rate and due date; principal payments show whether they were a scheduled share, a prepayment,
    collateral release proceeds or a payoff; fees show which fee; related entries point to the bill, fee,
    payment or collateral record they derive from.

    Args:
        txn_id: Reference number of one transaction; leave "" if unknown.
        loan_id: Loan number of the equipment loan; leave "" if unknown.
        customer_id: Customer reference of the member; leave "" if unknown.
        source_ref_id: Reference of a record other entries relate to (an installment bill, fee, payment or collateral record); leave "" if unknown.
    """
    match = _criteria({"txn_id": txn_id, "loan_id": loan_id, "customer_id": customer_id, "source_ref_id": source_ref_id})
    if not match:
        return "Error: provide at least one reference number to look up equipment loan transactions."
    return _render(ctx.find("equipment_transactions", **match), match, "equipment loan transactions")


@tool(owner="agent", rw="read")
def find_equipment_collateral(ctx: ToolContext, collateral_action_id: str = "", loan_id: str = "",
                              customer_id: str = "", source_action_id: str = "") -> str:
    """Look up the units pledged to equipment loans and the releases of those units.

    Each record shows the unit's description, serial number or VIN, model year, pledged value and the
    date of the pledge or release; a release shows its reason (payoff, sale, substitution or total loss)
    and points to the pledge it releases.

    Args:
        collateral_action_id: Reference number of one pledge or release record; leave "" if unknown.
        loan_id: Loan number of the equipment loan; leave "" if unknown.
        customer_id: Customer reference of the member; leave "" if unknown.
        source_action_id: Reference of a pledge (to find its release) or of a release (to find the unit pledged in its place); leave "" if unknown.
    """
    match = _criteria({"collateral_action_id": collateral_action_id, "loan_id": loan_id, "customer_id": customer_id, "source_action_id": source_action_id})
    if not match:
        return "Error: provide at least one reference number to look up equipment collateral records."
    return _render(ctx.find("equipment_collateral", **match), match, "equipment collateral records")


@tool(owner="agent", rw="read")
def find_equipment_requests(ctx: ToolContext, request_id: str = "", customer_id: str = "", loan_id: str = "") -> str:
    """Look up collateral release, collateral substitution, deferral and re-amortization requests on equipment loans.

    Each request shows what was asked, the unit concerned by serial number, the sale price or replacement
    value stated, its status and when it was registered.

    Args:
        request_id: Reference number of the request; leave "" if unknown.
        customer_id: Customer reference of the requesting member; leave "" if unknown.
        loan_id: Loan number of the equipment loan concerned; leave "" if unknown.
    """
    match = _criteria({"request_id": request_id, "customer_id": customer_id, "loan_id": loan_id})
    if not match:
        return "Error: provide at least one reference number to look up equipment loan requests."
    return _render(ctx.find("equipment_requests", **match), match, "equipment loan requests")


# ----------------------------------------------------------------------------- farm real estate loans
@tool(owner="agent", rw="read")
def find_farmland_loans(ctx: ToolContext, loan_id: str = "", customer_id: str = "") -> str:
    """Look up a member's farm real estate loans.

    Each loan shows the rate product, its status (applied, active, nonaccrual, paid off or declined),
    original and current principal, billed interest and fees not yet paid, the appraised value of the
    parcels still mortgaged, the current and initial rate, the end of the fixed-rate period and the next
    rate adjustment, the installment, its frequency, next due date and maturity, the last rate
    conversion, autopay, the latest tax year verified paid and any tax delinquency, and the key dates.

    Args:
        loan_id: Loan number of the farm real estate loan; leave "" if unknown.
        customer_id: Customer reference of the borrowing member, to list all of the member's farm real estate loans; leave "" if unknown.
    """
    match = _criteria({"loan_id": loan_id, "customer_id": customer_id})
    if not match:
        return "Error: provide at least one reference number to look up farm real estate loans."
    return _render(ctx.find("farmland_loans", **match), match, "farm real estate loans")


@tool(owner="agent", rw="read")
def find_farmland_transactions(ctx: ToolContext, txn_id: str = "", loan_id: str = "", customer_id: str = "",
                               source_ref_id: str = "") -> str:
    """Look up the transaction history of farm real estate loans.

    Each entry shows its type, amount, effective date and channel: installment interest bills (period,
    rate, whether at the contract or default rate, due date), payments (scheduled share, prepayment,
    release proceeds or payoff), protective advances for property taxes with the tax year, fees, waivers
    and returned payments, each pointing to the record it derives from.

    Args:
        txn_id: Reference number of one transaction; leave "" if unknown.
        loan_id: Loan number of the farm real estate loan; leave "" if unknown.
        customer_id: Customer reference of the member; leave "" if unknown.
        source_ref_id: Reference of a record other entries relate to (an installment bill, fee, payment, parcel release or protective advance); leave "" if unknown.
    """
    match = _criteria({"txn_id": txn_id, "loan_id": loan_id, "customer_id": customer_id, "source_ref_id": source_ref_id})
    if not match:
        return "Error: provide at least one reference number to look up farm real estate loan transactions."
    return _render(ctx.find("farmland_transactions", **match), match, "farm real estate loan transactions")


@tool(owner="agent", rw="read")
def find_farmland_parcels(ctx: ToolContext, parcel_action_id: str = "", loan_id: str = "", customer_id: str = "",
                          source_action_id: str = "") -> str:
    """Look up the parcels mortgaged to farm real estate loans and their releases.

    Each record shows the county parcel number, legal description, county, deeded acres, land use,
    appraised value and the recording or release date; a release shows its reason (payoff, sale,
    condemnation or farmstead split) and points to the mortgage record it releases.

    Args:
        parcel_action_id: Reference number of one mortgage or release record; leave "" if unknown.
        loan_id: Loan number of the farm real estate loan; leave "" if unknown.
        customer_id: Customer reference of the member; leave "" if unknown.
        source_action_id: Reference of a mortgage record, to find its release; leave "" if unknown.
    """
    match = _criteria({"parcel_action_id": parcel_action_id, "loan_id": loan_id, "customer_id": customer_id, "source_action_id": source_action_id})
    if not match:
        return "Error: provide at least one reference number to look up farm real estate parcel records."
    return _render(ctx.find("farmland_parcels", **match), match, "farm real estate parcel records")


@tool(owner="agent", rw="read")
def find_farmland_requests(ctx: ToolContext, request_id: str = "", customer_id: str = "", loan_id: str = "") -> str:
    """Look up partial release, rate conversion and assumption requests on farm real estate loans.

    Each request shows what was asked, the parcel number for a release, the product asked for in a
    conversion, any sale price or award stated, its status and when it was registered.

    Args:
        request_id: Reference number of the request; leave "" if unknown.
        customer_id: Customer reference of the requesting member; leave "" if unknown.
        loan_id: Loan number of the farm real estate loan concerned; leave "" if unknown.
    """
    match = _criteria({"request_id": request_id, "customer_id": customer_id, "loan_id": loan_id})
    if not match:
        return "Error: provide at least one reference number to look up farm real estate requests."
    return _render(ctx.find("farmland_requests", **match), match, "farm real estate requests")


# ----------------------------------------------------------------------------- rural home loans
@tool(owner="agent", rw="read")
def find_homeloan_loans(ctx: ToolContext, loan_id: str = "", customer_id: str = "") -> str:
    """Look up a member's Country Home (rural home) mortgage loans.

    Each loan shows the product, its status (applied, active, forbearance, nonaccrual, paid off or
    declined), original and current principal, billed interest and fees not yet paid, the escrow balance,
    the note rate and initial rate, the fixed period and next rate change, the monthly principal-and-
    interest payment and escrow deposit, the next due date and maturity, the original value, the home's
    address, parcel number and acreage, occupancy, flood zone, whether escrow is waived, mortgage
    insurance and its premium, the homeowner's insurance expiry, forbearance used, autopay and key dates.

    Args:
        loan_id: Loan number of the home loan; leave "" if unknown.
        customer_id: Customer reference of the borrowing member, to list all of the member's home loans; leave "" if unknown.
    """
    match = _criteria({"loan_id": loan_id, "customer_id": customer_id})
    if not match:
        return "Error: provide at least one reference number to look up home loans."
    return _render(ctx.find("homeloan_loans", **match), match, "home loans")


@tool(owner="agent", rw="read")
def find_homeloan_transactions(ctx: ToolContext, txn_id: str = "", loan_id: str = "", customer_id: str = "",
                               source_ref_id: str = "") -> str:
    """Look up the payment history of Country Home loans: monthly interest bills, payments, fees and reversals.

    Each entry shows its type, amount, effective date and channel; monthly bills show the due date and
    the note rate; principal payments show whether they were the scheduled share, an extra curtailment
    or the payoff; fee entries show which fee; related entries point to the monthly bill, fee or payment
    they derive from.

    Args:
        txn_id: Reference number of one transaction; leave "" if unknown.
        loan_id: Loan number of the home loan; leave "" if unknown.
        customer_id: Customer reference of the member; leave "" if unknown.
        source_ref_id: Reference of a record other entries relate to (a monthly bill, fee or payment); leave "" if unknown.
    """
    match = _criteria({"txn_id": txn_id, "loan_id": loan_id, "customer_id": customer_id, "source_ref_id": source_ref_id})
    if not match:
        return "Error: provide at least one reference number to look up home loan transactions."
    return _render(ctx.find("homeloan_transactions", **match), match, "home loan transactions")


@tool(owner="agent", rw="read")
def find_homeloan_escrow(ctx: ToolContext, escrow_txn_id: str = "", loan_id: str = "", customer_id: str = "",
                         source_ref_id: str = "") -> str:
    """Look up the escrow account activity of Country Home loans.

    Each entry shows deposits (initial, monthly or a lump-sum shortage payment), disbursements of property
    taxes, homeowner's, flood and mortgage insurance premiums with the payee and the tax year or policy
    term paid, refunds of surplus or of the balance at payoff, and reversals of returned deposits.

    Args:
        escrow_txn_id: Reference number of one escrow entry; leave "" if unknown.
        loan_id: Loan number of the home loan; leave "" if unknown.
        customer_id: Customer reference of the member; leave "" if unknown.
        source_ref_id: Reference of an entry others relate to (for example a deposit that was reversed); leave "" if unknown.
    """
    match = _criteria({"escrow_txn_id": escrow_txn_id, "loan_id": loan_id, "customer_id": customer_id,
                       "source_ref_id": source_ref_id})
    if not match:
        return "Error: provide at least one reference number to look up escrow activity."
    return _render(ctx.find("homeloan_escrow", **match), match, "escrow entries")


@tool(owner="agent", rw="read")
def find_homeloan_requests(ctx: ToolContext, request_id: str = "", customer_id: str = "", loan_id: str = "") -> str:
    """Look up mortgage insurance cancellation, escrow waiver, recast and forbearance requests on Country Home loans.

    Each request shows what was asked, the months asked for in a forbearance, its status and when it was
    registered.

    Args:
        request_id: Reference number of the request; leave "" if unknown.
        customer_id: Customer reference of the requesting member; leave "" if unknown.
        loan_id: Loan number of the home loan concerned; leave "" if unknown.
    """
    match = _criteria({"request_id": request_id, "customer_id": customer_id, "loan_id": loan_id})
    if not match:
        return "Error: provide at least one reference number to look up home loan requests."
    return _render(ctx.find("homeloan_requests", **match), match, "home loan requests")


# ----------------------------------------------------------------------------- construction loans
@tool(owner="agent", rw="read")
def find_construction_loans(ctx: ToolContext, construction_loan_id: str = "", customer_id: str = "",
                            converted_loan_id: str = "") -> str:
    """Look up a member's construction loans for country homes, farm buildings and livestock facilities.

    Each loan shows the product, its status (applied, active, extended, converting, converted, paid off or
    declined), the commitment and approved budget, principal disbursed, billed interest and fees not yet
    paid, retainage held back from the builder, the rate, the builder, the permanent financing it
    converts into, the construction end date, extensions granted, the completion date and, once
    converted, the permanent loan it became.

    Args:
        construction_loan_id: Loan number of the construction loan; leave "" if unknown.
        customer_id: Customer reference of the borrowing member; leave "" if unknown.
        converted_loan_id: Loan number of the permanent loan, to find the construction loan it came from; leave "" if unknown.
    """
    match = _criteria({"construction_loan_id": construction_loan_id, "customer_id": customer_id,
                       "converted_loan_id": converted_loan_id})
    if not match:
        return "Error: provide at least one reference number to look up construction loans."
    return _render(ctx.find("construction_loans", **match), match, "construction loans")


@tool(owner="agent", rw="read")
def find_construction_transactions(ctx: ToolContext, txn_id: str = "", construction_loan_id: str = "",
                                   customer_id: str = "", source_ref_id: str = "") -> str:
    """Look up the activity of construction loans: draws, retainage, interest bills, payments and fees.

    Each entry shows its type, amount and date; draws show the draw number, the percent complete found by
    the inspector and who was paid; interest bills show the month, rate and due date; fees show which fee.

    Args:
        txn_id: Reference number of one transaction; leave "" if unknown.
        construction_loan_id: Loan number of the construction loan; leave "" if unknown.
        customer_id: Customer reference of the member; leave "" if unknown.
        source_ref_id: Reference of a record other entries relate to (a draw, bill or fee); leave "" if unknown.
    """
    match = _criteria({"txn_id": txn_id, "construction_loan_id": construction_loan_id, "customer_id": customer_id,
                       "source_ref_id": source_ref_id})
    if not match:
        return "Error: provide at least one reference number to look up construction loan activity."
    return _render(ctx.find("construction_transactions", **match), match, "construction loan transactions")


@tool(owner="agent", rw="read")
def find_construction_draw_requests(ctx: ToolContext, request_id: str = "", customer_id: str = "",
                                    construction_loan_id: str = "") -> str:
    """Look up draw requests on construction loans.

    Each request shows the draw number, the amount requested, whether lien waivers for the previous draw
    have been received, its status (submitted, inspection ordered, approved, declined or withdrawn) and
    when it was registered.

    Args:
        request_id: Reference number of the draw request; leave "" if unknown.
        customer_id: Customer reference of the member; leave "" if unknown.
        construction_loan_id: Loan number of the construction loan; leave "" if unknown.
    """
    match = _criteria({"request_id": request_id, "customer_id": customer_id, "construction_loan_id": construction_loan_id})
    if not match:
        return "Error: provide at least one reference number to look up draw requests."
    return _render(ctx.find("construction_draw_requests", **match), match, "draw requests")


# ----------------------------------------------------------------------------- crop insurance
@tool(owner="agent", rw="read")
def find_cropins_policies(ctx: ToolContext, policy_id: str = "", customer_id: str = "", assigned_loan_id: str = "") -> str:
    """Look up a member's crop insurance policies written through the association's agency.

    Each policy covers one crop in one county for one crop year and shows the plan and coverage level,
    status (applied, active, cancelled, terminated or expired), the provider's policy number, practice,
    unit structure, approved yield, insured acres, projected and harvest prices, premium owed, indemnity
    not yet paid, whether the indemnity is assigned to the association and to which operating line,
    beginning farmer status and key dates.

    Args:
        policy_id: Reference number of the policy record; leave "" if unknown.
        customer_id: Customer reference of the insured member; leave "" if unknown.
        assigned_loan_id: Loan number of an operating line, to find the policies whose indemnity is assigned to it; leave "" if unknown.
    """
    match = _criteria({"policy_id": policy_id, "customer_id": customer_id, "assigned_loan_id": assigned_loan_id})
    if not match:
        return "Error: provide at least one reference number to look up crop insurance policies."
    return _render(ctx.find("cropins_policies", **match), match, "crop insurance policies")


@tool(owner="agent", rw="read")
def find_cropins_transactions(ctx: ToolContext, txn_id: str = "", policy_id: str = "", customer_id: str = "",
                              claim_id: str = "", source_ref_id: str = "") -> str:
    """Look up the premium and indemnity activity of crop insurance policies.

    Each entry shows its type, amount and date: premium and administrative fee billings, interest on
    unpaid premium, premium payments, indemnities determined, amounts withheld for unpaid premium, and
    indemnity payments with their payee.

    Args:
        txn_id: Reference number of one entry; leave "" if unknown.
        policy_id: Reference number of the policy record; leave "" if unknown.
        customer_id: Customer reference of the member; leave "" if unknown.
        claim_id: Reference number of a claim, to find its indemnity entries; leave "" if unknown.
        source_ref_id: Reference of an entry others relate to (an indemnity or offset); leave "" if unknown.
    """
    match = _criteria({"txn_id": txn_id, "policy_id": policy_id, "customer_id": customer_id, "claim_id": claim_id,
                       "source_ref_id": source_ref_id})
    if not match:
        return "Error: provide at least one reference number to look up crop insurance activity."
    return _render(ctx.find("cropins_transactions", **match), match, "crop insurance transactions")


@tool(owner="agent", rw="read")
def find_cropins_claims(ctx: ToolContext, claim_id: str = "", customer_id: str = "", policy_id: str = "") -> str:
    """Look up notices of loss filed on crop insurance policies.

    Each claim shows the cause of loss, the date damage was discovered, the production to count once the
    adjuster determines it, its status and when the notice was registered.

    Args:
        claim_id: Reference number of the claim; leave "" if unknown.
        customer_id: Customer reference of the member; leave "" if unknown.
        policy_id: Reference number of the policy record; leave "" if unknown.
    """
    match = _criteria({"claim_id": claim_id, "customer_id": customer_id, "policy_id": policy_id})
    if not match:
        return "Error: provide at least one reference number to look up crop insurance claims."
    return _render(ctx.find("cropins_claims", **match), match, "crop insurance claims")


# ----------------------------------------------------------------------------- member equities
@tool(owner="agent", rw="read")
def find_equity_accounts(ctx: ToolContext, equity_id: str = "", customer_id: str = "", apply_to_loan_id: str = "") -> str:
    """Look up a member's equity holdings: borrower stock or participation certificates, allocated surplus and preferred stock.

    Each holding shows the class, its status (subscribed, active, retirement requested, retired or
    cancelled), the balance held, cash patronage declared and not yet paid, the issue and retirement
    dates, any pending retirement or redemption request date, and how payouts are made — check, direct
    deposit to an account ending in given digits, or applied to a named loan — with the dividend option
    for preferred stock.

    Args:
        equity_id: Reference number of the equity holding; leave "" if unknown.
        customer_id: Customer reference of the member, to list all of the member's holdings; leave "" if unknown.
        apply_to_loan_id: Loan number of a loan, to find holdings whose cash patronage is applied to it; leave "" if unknown.
    """
    match = _criteria({"equity_id": equity_id, "customer_id": customer_id, "apply_to_loan_id": apply_to_loan_id})
    if not match:
        return "Error: provide at least one reference number to look up equity holdings."
    return _render(ctx.find("equity_accounts", **match), match, "equity holdings")


@tool(owner="agent", rw="read")
def find_equity_transactions(ctx: ToolContext, eq_txn_id: str = "", equity_id: str = "", customer_id: str = "",
                             source_loan_id: str = "", source_ref_id: str = "") -> str:
    """Look up the activity of member equity holdings: purchases, patronage, payouts, retirements and dividends.

    Each entry shows its type, amount and date; patronage entries show the patronage year, the loan that
    earned it with its eligible average daily balance and the rate; payouts show the method and check
    number; voids and reissues point to the payout they relate to; retirements show their reason and,
    for revolvements, the allocation year.

    Args:
        eq_txn_id: Reference number of one entry; leave "" if unknown.
        equity_id: Reference number of the equity holding; leave "" if unknown.
        customer_id: Customer reference of the member; leave "" if unknown.
        source_loan_id: Loan number of a loan, to find the patronage it earned or the payments applied to it; leave "" if unknown.
        source_ref_id: Reference of an entry others relate to (a payout or a void); leave "" if unknown.
    """
    match = _criteria({"eq_txn_id": eq_txn_id, "equity_id": equity_id, "customer_id": customer_id,
                       "source_loan_id": source_loan_id, "source_ref_id": source_ref_id})
    if not match:
        return "Error: provide at least one reference number to look up equity activity."
    return _render(ctx.find("equity_transactions", **match), match, "equity transactions")


@tool(owner="agent", rw="read")
def find_equity_requests(ctx: ToolContext, request_id: str = "", customer_id: str = "", equity_id: str = "") -> str:
    """Look up retirement, estate retirement, preferred stock redemption and check reissue requests.

    Each request shows what was asked, any amount asked to be redeemed, its status and when it was
    registered.

    Args:
        request_id: Reference number of the request; leave "" if unknown.
        customer_id: Customer reference of the requesting member; leave "" if unknown.
        equity_id: Reference number of the equity holding concerned; leave "" if unknown.
    """
    match = _criteria({"request_id": request_id, "customer_id": customer_id, "equity_id": equity_id})
    if not match:
        return "Error: provide at least one reference number to look up equity requests."
    return _render(ctx.find("equity_requests", **match), match, "equity requests")


# ----------------------------------------------------------------------------- identity verification
@tool(owner="agent", rw="write")
def verify_member_identity(ctx: ToolContext, customer_id: str, phone_number: str = "", email: str = "",
                           tax_id_last4: str = "", member_number: str = "", member_since: str = "") -> str:
    """Verify the caller's identity against the membership record and record the outcome.

    Identity must be verified before any account information is discussed or any transaction is made.
    This tool performs the comparison itself: it compares each piece of identity information the caller
    states with the member's profile, counts how many match, and passes the caller only when at least 2
    match. The customer reference is used solely to retrieve the profile and never counts as a match.
    Callers usually know only some of these details, so pass exactly what the caller said, word for word,
    and leave the rest blank. The outcome is recorded; if a first attempt fails and a later attempt with
    more details passes, the pass stands.

    Args:
        customer_id: The customer reference read from the member profile lookup. Required; used only to retrieve the profile and not counted as a match.
        phone_number: The phone number on file as the caller states it, 10 digits; leave "" if not stated.
        email: The email address on file as the caller states it; leave "" if not stated.
        tax_id_last4: The last four digits of the member's Social Security or employer identification number as the caller states them; leave "" if not stated.
        member_number: The membership number as the caller reads it from a certificate or statement, e.g. CPF-0418823; leave "" if not stated.
        member_since: The date the membership was opened as the caller states it, YYYY-MM-DD; leave "" if not stated.
    """
    if not customer_id:
        return "Error: customer_id is required; look the member up first and pass their customer reference."
    rows = ctx.find("customers", customer_id=customer_id)
    if not rows:
        return f"Error: no member {customer_id}; cannot verify."
    rec = rows[0]
    # The tool owns the comparison; the locator customer_id is deliberately not a credential.
    supplied = {"phone_number": phone_number, "email": email, "tax_id_last4": tax_id_last4,
                "member_number": member_number, "member_since": member_since}

    def _norm(v) -> str:
        return "".join(ch for ch in str(v).casefold() if ch.isalnum())

    matched = sum(1 for field, value in supplied.items()
                  if value and rec.get(field) not in (None, "") and _norm(rec.get(field)) == _norm(value))
    verified = matched >= 2
    rid = ctx.make_id("ver_", customer_id)
    # Store only the reproducible boolean; upsert and never downgrade a pass.
    prior = ctx.find("verification_log", verification_id=rid)
    verified = verified or bool(prior and prior[0].get("verified"))
    if prior:
        ctx.update("verification_log", rid, verified=verified, verified_at=ctx.now())
    else:
        ctx.create("verification_log", rid, verification_id=rid, customer_id=customer_id,
                   verified=verified, verified_at=ctx.now())
    return (f"Identity verified for {customer_id} ({matched} detail(s) matched)." if verified
            else f"Identity NOT verified for {customer_id} (only {matched} of the 2 required details matched). "
                 "Ask the caller for another detail on file and call this tool again.")


# ----------------------------------------------------------------------------- human handoff
@tool(owner="agent", rw="write")
def transfer_to_human_agent(ctx: ToolContext, customer_id: str, reason: str) -> str:
    """Transfer the member to a human loan officer or servicing specialist and record why.

    Use POLICY_NOT_COVERED when no published policy lets you resolve what the member needs — for example a
    decision only a credit officer can make, or a situation the servicing rules do not address. Use
    CUSTOMER_REQUESTED when the member has explicitly asked to speak with a person at least 2 times in this
    conversation.

    Args:
        customer_id: The customer reference read from the member profile lookup (the profile must exist).
        reason: Exactly one of POLICY_NOT_COVERED or CUSTOMER_REQUESTED, never free text. POLICY_NOT_COVERED — no published policy resolves the request; CUSTOMER_REQUESTED — the member has explicitly asked for a person at least 2 times.
    """
    allowed = {"POLICY_NOT_COVERED", "CUSTOMER_REQUESTED"}
    if reason not in allowed:
        return f"Error: unknown transfer reason '{reason}'. Valid: {', '.join(sorted(allowed))}."
    if not ctx.find("customers", customer_id=customer_id):
        return f"Error: no member {customer_id}; cannot record the transfer."
    rid = ctx.make_id("hof_", customer_id, reason)
    ctx.create("handoff_log", rid, handoff_id=rid, customer_id=customer_id, reason=reason, created_at=ctx.now())
    return f"Transfer to a human representative recorded for {customer_id} ({reason})."

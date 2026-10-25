"""Shared tools for env_0057_durable_medical_equipment_supplier (Summit Ridge Home Medical).

Every tool here is a share tool, always present in its owner's tool list:
  - one finder per record type of the scenario (the patient-profile finder doubles as the identity entry);
  - the identity-verification write (two matching credentials pass);
  - the transfer-to-human write (exactly two reason values).
Customer-originated writes live as hidden task tools in each difficulty's task_tools.py.
Finders take every reference-number field of their record type as an optional argument and match exactly;
the customers finder matches what the caller states after normalisation (ctx.fuzzy_find).
"""

from erlbench import ToolContext, tool


@tool(owner="agent", rw="read")
def find_customers(ctx: ToolContext, customer_id: str = "", name: str = "", phone_number: str = "",
                   email: str = "", date_of_birth: str = "", home_zip: str = "") -> str:
    """Look up a patient profile to establish whose account this call is about.

    Search by the patient reference number, or by what the caller naturally states: full name, phone
    number, email address, date of birth or home ZIP code. Every criterion is optional; supply whichever
    are known, and add another one when several patients match. The profile returned carries the
    patient reference number, name, date of birth, phone number, email, home ZIP code, service address
    and the date the patient first became a Summit Ridge patient. Finding a profile does not verify the
    caller's identity.

    Args:
        customer_id: The patient reference number, if already known; leave "" otherwise.
        name: The patient's full name as the caller states it; leave "" if not provided.
        phone_number: The phone number the caller gives, 10 digits; leave "" if not provided.
        email: The email address the caller gives; leave "" if not provided.
        date_of_birth: The patient's date of birth as YYYY-MM-DD; leave "" if not provided.
        home_zip: The 5-digit ZIP code of the patient's home; leave "" if not provided.
    """
    match = {k: v for k, v in {"customer_id": customer_id, "name": name, "phone_number": phone_number,
                               "email": email, "date_of_birth": date_of_birth,
                               "home_zip": home_zip}.items() if v}
    if not match:
        return "Error: provide at least one reference number or profile detail to find the patient."
    rows = ctx.fuzzy_find("customers", **match)
    if not rows:
        return f"No patient matches {match}."
    if len(rows) > 1:
        return f"Error: {len(rows)} patients match {match}; ask the caller for one more detail to tell them apart."
    return str(rows[0])


@tool(owner="agent", rw="read")
def find_coverage_holdings(ctx: ToolContext, coverage_id: str = "", customer_id: str = "", member_id: str = "") -> str:
    """Look up the insurance coverage records on a patient's account: payer class, priority
    (primary or secondary), member id and plan name as printed on the card, effective and
    termination dates, the latest eligibility check date, QMB status, the deductible and
    out-of-pocket amounts met this benefit year, the patient balance owed on that coverage, any
    monthly payment arrangement and any approved financial-hardship tier. Every reference number
    below is optional; supply whichever are known. Matching records are returned in full; when
    none match, the reply says so.

    Args:
        coverage_id: The insurance coverage reference; leave "" if unknown.
        customer_id: The patient reference number; leave "" if unknown.
        member_id: The member or beneficiary id exactly as printed on the insurance card; leave
            "" if unknown.
    """
    match = {k: v for k, v in {"coverage_id": coverage_id, "customer_id": customer_id, "member_id": member_id}.items() if v}
    if not match:
        return "Error: provide at least one reference number to search by."
    rows = ctx.find("coverage_holdings", **match)
    return str(rows) if rows else f"No matching records for {match}."


@tool(owner="agent", rw="read")
def find_coverage_ledger(ctx: ToolContext, ledger_entry_id: str = "", coverage_id: str = "", customer_id: str = "", source_bill_id: str = "", applied_to_entry_id: str = "", payer_coverage_id: str = "") -> str:
    """Look up entries on a patient's account ledger: eligibility responses, patient charges by
    component (deductible, coinsurance, copay, non-covered, upgrade, self-pay, repair,
    unreturned equipment), deductible and out-of-pocket accumulator postings and resets, patient
    payments, secondary-insurer payments, adjustments, refunds, statements and collection
    referrals, each with its posting date, amount and the claim line or entry it relates to.
    Every reference number below is optional; supply whichever are known. Matching records are
    returned in full; when none match, the reply says so.

    Args:
        ledger_entry_id: The patient-account ledger entry reference; leave "" if unknown.
        coverage_id: The insurance coverage reference; leave "" if unknown.
        customer_id: The patient reference number; leave "" if unknown.
        source_bill_id: The reference of the equipment or supply claim line the entry stems
            from; leave "" if unknown.
        applied_to_entry_id: The reference of the ledger entry this entry settles, adjusts or
            refunds; leave "" if unknown.
        payer_coverage_id: The coverage reference of the secondary insurer that paid; leave ""
            if unknown.
    """
    match = {k: v for k, v in {"ledger_entry_id": ledger_entry_id, "coverage_id": coverage_id, "customer_id": customer_id, "source_bill_id": source_bill_id, "applied_to_entry_id": applied_to_entry_id, "payer_coverage_id": payer_coverage_id}.items() if v}
    if not match:
        return "Error: provide at least one reference number to search by."
    rows = ctx.find("coverage_ledger", **match)
    return str(rows) if rows else f"No matching records for {match}."


@tool(owner="agent", rw="read")
def find_coverage_requests(ctx: ToolContext, coverage_request_id: str = "", customer_id: str = "", coverage_id: str = "") -> str:
    """Look up patient-account requests such as financial-hardship applications, payment-plan
    agreements, refund requests and coordination-of-benefits updates, with their status, amount
    and submission date. Every reference number below is optional; supply whichever are known.
    Matching records are returned in full; when none match, the reply says so.

    Args:
        coverage_request_id: The patient-account request reference; leave "" if unknown.
        customer_id: The patient reference number; leave "" if unknown.
        coverage_id: The insurance coverage reference; leave "" if unknown.
    """
    match = {k: v for k, v in {"coverage_request_id": coverage_request_id, "customer_id": customer_id, "coverage_id": coverage_id}.items() if v}
    if not match:
        return "Error: provide at least one reference number to search by."
    rows = ctx.find("coverage_requests", **match)
    return str(rows) if rows else f"No matching records for {match}."


@tool(owner="agent", rw="read")
def find_pap_holdings(ctx: ToolContext, pap_holding_id: str = "", customer_id: str = "", coverage_id: str = "") -> str:
    """Look up a patient's PAP (CPAP, bilevel or ASV) device records: device class, status, the
    coverage billed, ordering practitioner, qualifying sleep test, setup date, current rental
    period start, suspension, ownership and closing dates, serial number, humidifier, prescribed
    pressure and order date. Every reference number below is optional; supply whichever are
    known. Matching records are returned in full; when none match, the reply says so.

    Args:
        pap_holding_id: The PAP device record reference; leave "" if unknown.
        customer_id: The patient reference number; leave "" if unknown.
        coverage_id: The insurance coverage reference; leave "" if unknown.
    """
    match = {k: v for k, v in {"pap_holding_id": pap_holding_id, "customer_id": customer_id, "coverage_id": coverage_id}.items() if v}
    if not match:
        return "Error: provide at least one reference number to search by."
    rows = ctx.find("pap_holdings", **match)
    return str(rows) if rows else f"No matching records for {match}."


@tool(owner="agent", rw="read")
def find_pap_billing(ctx: ToolContext, pap_bill_id: str = "", pap_holding_id: str = "", customer_id: str = "", coverage_id: str = "", original_bill_id: str = "") -> str:
    """Look up PAP claim lines and self-pay sale lines: paid, denied and reversed rental months
    with their month number, modifier, service date, remittance date, allowed, paid and patient
    amounts, claim number and denial or reversal reason, as well as self-pay sales and refunds.
    Every reference number below is optional; supply whichever are known. Matching records are
    returned in full; when none match, the reply says so.

    Args:
        pap_bill_id: The PAP claim or sale line reference; leave "" if unknown.
        pap_holding_id: The PAP device record reference; leave "" if unknown.
        customer_id: The patient reference number; leave "" if unknown.
        coverage_id: The insurance coverage reference; leave "" if unknown.
        original_bill_id: The reference of the original line that this line reverses or refunds;
            leave "" if unknown.
    """
    match = {k: v for k, v in {"pap_bill_id": pap_bill_id, "pap_holding_id": pap_holding_id, "customer_id": customer_id, "coverage_id": coverage_id, "original_bill_id": original_bill_id}.items() if v}
    if not match:
        return "Error: provide at least one reference number to search by."
    rows = ctx.find("pap_billing", **match)
    return str(rows) if rows else f"No matching records for {match}."


@tool(owner="agent", rw="read")
def find_pap_service(ctx: ToolContext, pap_service_id: str = "", pap_holding_id: str = "", customer_id: str = "") -> str:
    """Look up PAP service history: deliveries and setups, compliance downloads with their usage
    window and result, practitioner re-evaluations, repairs with fault and cost assignment, and
    pickups with the condition found. Every reference number below is optional; supply whichever
    are known. Matching records are returned in full; when none match, the reply says so.

    Args:
        pap_service_id: The PAP service visit reference; leave "" if unknown.
        pap_holding_id: The PAP device record reference; leave "" if unknown.
        customer_id: The patient reference number; leave "" if unknown.
    """
    match = {k: v for k, v in {"pap_service_id": pap_service_id, "pap_holding_id": pap_holding_id, "customer_id": customer_id}.items() if v}
    if not match:
        return "Error: provide at least one reference number to search by."
    rows = ctx.find("pap_service", **match)
    return str(rows) if rows else f"No matching records for {match}."


@tool(owner="agent", rw="read")
def find_pap_requests(ctx: ToolContext, pap_request_id: str = "", customer_id: str = "", pap_holding_id: str = "", related_bill_id: str = "") -> str:
    """Look up PAP requests such as prior authorizations, return pickups, appeals, pressure-change
    orders and replacement requests, with their status and dates. Every reference number below
    is optional; supply whichever are known. Matching records are returned in full; when none
    match, the reply says so.

    Args:
        pap_request_id: The PAP request reference; leave "" if unknown.
        customer_id: The patient reference number; leave "" if unknown.
        pap_holding_id: The PAP device record reference; leave "" if unknown.
        related_bill_id: The reference of the denied claim line an appeal concerns; leave "" if
            unknown.
    """
    match = {k: v for k, v in {"pap_request_id": pap_request_id, "customer_id": customer_id, "pap_holding_id": pap_holding_id, "related_bill_id": related_bill_id}.items() if v}
    if not match:
        return "Error: provide at least one reference number to search by."
    rows = ctx.find("pap_requests", **match)
    return str(rows) if rows else f"No matching records for {match}."


@tool(owner="agent", rw="read")
def find_oxygen_holdings(ctx: ToolContext, oxygen_holding_id: str = "", customer_id: str = "", coverage_id: str = "") -> str:
    """Look up a patient's home oxygen records: system class, status, coverage billed, qualifying
    test and group, prescribed flow and usage pattern, mobility documentation, setup,
    payment-period start, cap, suspension and closing dates, order date and the stationary unit
    serial number. Every reference number below is optional; supply whichever are known.
    Matching records are returned in full; when none match, the reply says so.

    Args:
        oxygen_holding_id: The home oxygen record reference; leave "" if unknown.
        customer_id: The patient reference number; leave "" if unknown.
        coverage_id: The insurance coverage reference; leave "" if unknown.
    """
    match = {k: v for k, v in {"oxygen_holding_id": oxygen_holding_id, "customer_id": customer_id, "coverage_id": coverage_id}.items() if v}
    if not match:
        return "Error: provide at least one reference number to search by."
    rows = ctx.find("oxygen_holdings", **match)
    return str(rows) if rows else f"No matching records for {match}."


@tool(owner="agent", rw="read")
def find_oxygen_billing(ctx: ToolContext, oxygen_bill_id: str = "", oxygen_holding_id: str = "", customer_id: str = "", coverage_id: str = "", original_bill_id: str = "") -> str:
    """Look up oxygen claim lines: paid, denied and reversed equipment months and post-cap contents
    months with month number, flow modifier, service and remittance dates, allowed, portable
    add-on, paid and patient amounts, claim number and denial or reversal reason. Every
    reference number below is optional; supply whichever are known. Matching records are
    returned in full; when none match, the reply says so.

    Args:
        oxygen_bill_id: The oxygen claim line reference; leave "" if unknown.
        oxygen_holding_id: The home oxygen record reference; leave "" if unknown.
        customer_id: The patient reference number; leave "" if unknown.
        coverage_id: The insurance coverage reference; leave "" if unknown.
        original_bill_id: The reference of the original line that this line reverses or refunds;
            leave "" if unknown.
    """
    match = {k: v for k, v in {"oxygen_bill_id": oxygen_bill_id, "oxygen_holding_id": oxygen_holding_id, "customer_id": customer_id, "coverage_id": coverage_id, "original_bill_id": original_bill_id}.items() if v}
    if not match:
        return "Error: provide at least one reference number to search by."
    rows = ctx.find("oxygen_billing", **match)
    return str(rows) if rows else f"No matching records for {match}."


@tool(owner="agent", rw="read")
def find_oxygen_service(ctx: ToolContext, oxygen_service_id: str = "", oxygen_holding_id: str = "", customer_id: str = "") -> str:
    """Look up oxygen service history: setups, cylinder and liquid refills, travel supplies, swaps
    and backup deliveries, maintenance and outage visits, group II repeat tests and pickups.
    Every reference number below is optional; supply whichever are known. Matching records are
    returned in full; when none match, the reply says so.

    Args:
        oxygen_service_id: The oxygen service visit reference; leave "" if unknown.
        oxygen_holding_id: The home oxygen record reference; leave "" if unknown.
        customer_id: The patient reference number; leave "" if unknown.
    """
    match = {k: v for k, v in {"oxygen_service_id": oxygen_service_id, "oxygen_holding_id": oxygen_holding_id, "customer_id": customer_id}.items() if v}
    if not match:
        return "Error: provide at least one reference number to search by."
    rows = ctx.find("oxygen_service", **match)
    return str(rows) if rows else f"No matching records for {match}."


@tool(owner="agent", rw="read")
def find_oxygen_requests(ctx: ToolContext, oxygen_request_id: str = "", customer_id: str = "", oxygen_holding_id: str = "", related_bill_id: str = "") -> str:
    """Look up oxygen requests such as prior authorizations, return pickups, travel arrangements,
    system changes, appeals and replacement elections, with their status and dates, including
    travel dates. Every reference number below is optional; supply whichever are known. Matching
    records are returned in full; when none match, the reply says so.

    Args:
        oxygen_request_id: The oxygen request reference; leave "" if unknown.
        customer_id: The patient reference number; leave "" if unknown.
        oxygen_holding_id: The home oxygen record reference; leave "" if unknown.
        related_bill_id: The reference of the denied claim line an appeal concerns; leave "" if
            unknown.
    """
    match = {k: v for k, v in {"oxygen_request_id": oxygen_request_id, "customer_id": customer_id, "oxygen_holding_id": oxygen_holding_id, "related_bill_id": related_bill_id}.items() if v}
    if not match:
        return "Error: provide at least one reference number to search by."
    rows = ctx.find("oxygen_requests", **match)
    return str(rows) if rows else f"No matching records for {match}."


@tool(owner="agent", rw="read")
def find_mobility_holdings(ctx: ToolContext, mobility_holding_id: str = "", customer_id: str = "", coverage_id: str = "") -> str:
    """Look up a patient's wheelchair records: chair class and the class coverage pays for, status,
    signed notice, ordering practitioner, examination and evaluation dates, patient weight,
    delivery, rental period, suspension, ownership and closing dates, and serial number. Every
    reference number below is optional; supply whichever are known. Matching records are
    returned in full; when none match, the reply says so.

    Args:
        mobility_holding_id: The wheelchair record reference; leave "" if unknown.
        customer_id: The patient reference number; leave "" if unknown.
        coverage_id: The insurance coverage reference; leave "" if unknown.
    """
    match = {k: v for k, v in {"mobility_holding_id": mobility_holding_id, "customer_id": customer_id, "coverage_id": coverage_id}.items() if v}
    if not match:
        return "Error: provide at least one reference number to search by."
    rows = ctx.find("mobility_holdings", **match)
    return str(rows) if rows else f"No matching records for {match}."


@tool(owner="agent", rw="read")
def find_mobility_billing(ctx: ToolContext, mobility_bill_id: str = "", mobility_holding_id: str = "", customer_id: str = "", coverage_id: str = "", original_bill_id: str = "", related_service_id: str = "") -> str:
    """Look up wheelchair claim and sale lines: rental months, purchases and repairs paid, denied
    or reversed, with month number, modifier, dates, allowed, paid, patient and upgrade amounts,
    claim number and denial or reversal reason, plus self-pay sales and refunds. Every reference
    number below is optional; supply whichever are known. Matching records are returned in full;
    when none match, the reply says so.

    Args:
        mobility_bill_id: The wheelchair claim or sale line reference; leave "" if unknown.
        mobility_holding_id: The wheelchair record reference; leave "" if unknown.
        customer_id: The patient reference number; leave "" if unknown.
        coverage_id: The insurance coverage reference; leave "" if unknown.
        original_bill_id: The reference of the original line that this line reverses or refunds;
            leave "" if unknown.
        related_service_id: The reference of the repair job a repair claim line bills; leave ""
            if unknown.
    """
    match = {k: v for k, v in {"mobility_bill_id": mobility_bill_id, "mobility_holding_id": mobility_holding_id, "customer_id": customer_id, "coverage_id": coverage_id, "original_bill_id": original_bill_id, "related_service_id": related_service_id}.items() if v}
    if not match:
        return "Error: provide at least one reference number to search by."
    rows = ctx.find("mobility_billing", **match)
    return str(rows) if rows else f"No matching records for {match}."


@tool(owner="agent", rw="read")
def find_mobility_service(ctx: ToolContext, mobility_service_id: str = "", mobility_holding_id: str = "", customer_id: str = "") -> str:
    """Look up wheelchair service history: deliveries, in-home accessibility assessments, repairs
    with the component and cost assignment, and pickups. Every reference number below is
    optional; supply whichever are known. Matching records are returned in full; when none
    match, the reply says so.

    Args:
        mobility_service_id: The wheelchair service visit reference; leave "" if unknown.
        mobility_holding_id: The wheelchair record reference; leave "" if unknown.
        customer_id: The patient reference number; leave "" if unknown.
    """
    match = {k: v for k, v in {"mobility_service_id": mobility_service_id, "mobility_holding_id": mobility_holding_id, "customer_id": customer_id}.items() if v}
    if not match:
        return "Error: provide at least one reference number to search by."
    rows = ctx.find("mobility_service", **match)
    return str(rows) if rows else f"No matching records for {match}."


@tool(owner="agent", rw="read")
def find_mobility_requests(ctx: ToolContext, mobility_request_id: str = "", customer_id: str = "", mobility_holding_id: str = "", related_bill_id: str = "") -> str:
    """Look up wheelchair requests such as prior authorizations, purchase elections, repair
    estimates, return pickups, appeals and replacement requests, with their status and dates.
    Every reference number below is optional; supply whichever are known. Matching records are
    returned in full; when none match, the reply says so.

    Args:
        mobility_request_id: The wheelchair request reference; leave "" if unknown.
        customer_id: The patient reference number; leave "" if unknown.
        mobility_holding_id: The wheelchair record reference; leave "" if unknown.
        related_bill_id: The reference of the denied claim line an appeal concerns; leave "" if
            unknown.
    """
    match = {k: v for k, v in {"mobility_request_id": mobility_request_id, "customer_id": customer_id, "mobility_holding_id": mobility_holding_id, "related_bill_id": related_bill_id}.items() if v}
    if not match:
        return "Error: provide at least one reference number to search by."
    rows = ctx.find("mobility_requests", **match)
    return str(rows) if rows else f"No matching records for {match}."


@tool(owner="agent", rw="read")
def find_beds_holdings(ctx: ToolContext, beds_holding_id: str = "", customer_id: str = "", coverage_id: str = "") -> str:
    """Look up a patient's hospital bed records: bed class, status, coverage or private rental,
    ordering practitioner, patient weight, support surface, signed notice, hospice election,
    delivery, rental period, suspension, ownership and closing dates, and serial number. Every
    reference number below is optional; supply whichever are known. Matching records are
    returned in full; when none match, the reply says so.

    Args:
        beds_holding_id: The hospital bed record reference; leave "" if unknown.
        customer_id: The patient reference number; leave "" if unknown.
        coverage_id: The insurance coverage reference; leave "" if unknown.
    """
    match = {k: v for k, v in {"beds_holding_id": beds_holding_id, "customer_id": customer_id, "coverage_id": coverage_id}.items() if v}
    if not match:
        return "Error: provide at least one reference number to search by."
    rows = ctx.find("beds_holdings", **match)
    return str(rows) if rows else f"No matching records for {match}."


@tool(owner="agent", rw="read")
def find_beds_billing(ctx: ToolContext, beds_bill_id: str = "", beds_holding_id: str = "", customer_id: str = "", coverage_id: str = "", original_bill_id: str = "") -> str:
    """Look up hospital bed claim lines and private rental charges: paid, denied and reversed
    rental months with dates, allowed, surface, paid, patient and upgrade amounts, claim number
    and reasons, and private monthly rent charges. Every reference number below is optional;
    supply whichever are known. Matching records are returned in full; when none match, the
    reply says so.

    Args:
        beds_bill_id: The hospital bed claim or rental charge reference; leave "" if unknown.
        beds_holding_id: The hospital bed record reference; leave "" if unknown.
        customer_id: The patient reference number; leave "" if unknown.
        coverage_id: The insurance coverage reference; leave "" if unknown.
        original_bill_id: The reference of the original line that this line reverses or refunds;
            leave "" if unknown.
    """
    match = {k: v for k, v in {"beds_bill_id": beds_bill_id, "beds_holding_id": beds_holding_id, "customer_id": customer_id, "coverage_id": coverage_id, "original_bill_id": original_bill_id}.items() if v}
    if not match:
        return "Error: provide at least one reference number to search by."
    rows = ctx.find("beds_billing", **match)
    return str(rows) if rows else f"No matching records for {match}."


@tool(owner="agent", rw="read")
def find_beds_service(ctx: ToolContext, beds_service_id: str = "", beds_holding_id: str = "", customer_id: str = "") -> str:
    """Look up hospital bed service history: deliveries, maintenance and repair visits with the
    entrapment check, and pickups. Every reference number below is optional; supply whichever
    are known. Matching records are returned in full; when none match, the reply says so.

    Args:
        beds_service_id: The hospital bed service visit reference; leave "" if unknown.
        beds_holding_id: The hospital bed record reference; leave "" if unknown.
        customer_id: The patient reference number; leave "" if unknown.
    """
    match = {k: v for k, v in {"beds_service_id": beds_service_id, "beds_holding_id": beds_holding_id, "customer_id": customer_id}.items() if v}
    if not match:
        return "Error: provide at least one reference number to search by."
    rows = ctx.find("beds_service", **match)
    return str(rows) if rows else f"No matching records for {match}."


@tool(owner="agent", rw="read")
def find_beds_requests(ctx: ToolContext, beds_request_id: str = "", customer_id: str = "", beds_holding_id: str = "", related_bill_id: str = "") -> str:
    """Look up hospital bed requests such as prior authorizations, return pickups and appeals, with
    their status and dates. Every reference number below is optional; supply whichever are
    known. Matching records are returned in full; when none match, the reply says so.

    Args:
        beds_request_id: The hospital bed request reference; leave "" if unknown.
        customer_id: The patient reference number; leave "" if unknown.
        beds_holding_id: The hospital bed record reference; leave "" if unknown.
        related_bill_id: The reference of the denied claim line an appeal concerns; leave "" if
            unknown.
    """
    match = {k: v for k, v in {"beds_request_id": beds_request_id, "customer_id": customer_id, "beds_holding_id": beds_holding_id, "related_bill_id": related_bill_id}.items() if v}
    if not match:
        return "Error: provide at least one reference number to search by."
    rows = ctx.find("beds_requests", **match)
    return str(rows) if rows else f"No matching records for {match}."


@tool(owner="agent", rw="read")
def find_resupply_holdings(ctx: ToolContext, resupply_holding_id: str = "", customer_id: str = "", coverage_id: str = "", pap_holding_id: str = "") -> str:
    """Look up a patient's PAP supply enrollment: replacement schedule, status, coverage billed,
    the device served, mask style, humidifier and heated-tubing use, automatic-shipment choice,
    order and continued-use dates, enrollment date and any hold. Every reference number below is
    optional; supply whichever are known. Matching records are returned in full; when none
    match, the reply says so.

    Args:
        resupply_holding_id: The PAP supply enrollment reference; leave "" if unknown.
        customer_id: The patient reference number; leave "" if unknown.
        coverage_id: The insurance coverage reference; leave "" if unknown.
        pap_holding_id: The PAP device record reference; leave "" if unknown.
    """
    match = {k: v for k, v in {"resupply_holding_id": resupply_holding_id, "customer_id": customer_id, "coverage_id": coverage_id, "pap_holding_id": pap_holding_id}.items() if v}
    if not match:
        return "Error: provide at least one reference number to search by."
    rows = ctx.find("resupply_holdings", **match)
    return str(rows) if rows else f"No matching records for {match}."


@tool(owner="agent", rw="read")
def find_resupply_shipments(ctx: ToolContext, resupply_line_id: str = "", resupply_holding_id: str = "", customer_id: str = "", coverage_id: str = "", original_line_id: str = "") -> str:
    """Look up PAP supply lines: items shipped with quantity, ship date and the date the supply
    covers through, payer and patient amounts or self-pay charges, denials, reversals, no-charge
    replacements and shipping charges. Every reference number below is optional; supply
    whichever are known. Matching records are returned in full; when none match, the reply says
    so.

    Args:
        resupply_line_id: The PAP supply shipment line reference; leave "" if unknown.
        resupply_holding_id: The PAP supply enrollment reference; leave "" if unknown.
        customer_id: The patient reference number; leave "" if unknown.
        coverage_id: The insurance coverage reference; leave "" if unknown.
        original_line_id: The reference of the original shipment line that this line reverses or
            replaces; leave "" if unknown.
    """
    match = {k: v for k, v in {"resupply_line_id": resupply_line_id, "resupply_holding_id": resupply_holding_id, "customer_id": customer_id, "coverage_id": coverage_id, "original_line_id": original_line_id}.items() if v}
    if not match:
        return "Error: provide at least one reference number to search by."
    rows = ctx.find("resupply_shipments", **match)
    return str(rows) if rows else f"No matching records for {match}."


@tool(owner="agent", rw="read")
def find_resupply_contacts(ctx: ToolContext, resupply_contact_id: str = "", resupply_holding_id: str = "", customer_id: str = "") -> str:
    """Look up refill contacts for a PAP supply enrollment: the date and channel of each
    confirmation or decline, the items the patient asked for and the supply status the patient
    reported. Every reference number below is optional; supply whichever are known. Matching
    records are returned in full; when none match, the reply says so.

    Args:
        resupply_contact_id: The refill contact reference; leave "" if unknown.
        resupply_holding_id: The PAP supply enrollment reference; leave "" if unknown.
        customer_id: The patient reference number; leave "" if unknown.
    """
    match = {k: v for k, v in {"resupply_contact_id": resupply_contact_id, "resupply_holding_id": resupply_holding_id, "customer_id": customer_id}.items() if v}
    if not match:
        return "Error: provide at least one reference number to search by."
    rows = ctx.find("resupply_contacts", **match)
    return str(rows) if rows else f"No matching records for {match}."


@tool(owner="agent", rw="read")
def find_urology_holdings(ctx: ToolContext, urology_holding_id: str = "", customer_id: str = "", coverage_id: str = "") -> str:
    """Look up a patient's urological supply enrollment: catheter program, status, coverage billed,
    ordering practitioner, documented condition and permanence, catheterizations per day,
    criteria documentation, infection count, catheter size, order and continued-need dates, and
    any hold. Every reference number below is optional; supply whichever are known. Matching
    records are returned in full; when none match, the reply says so.

    Args:
        urology_holding_id: The urological supply enrollment reference; leave "" if unknown.
        customer_id: The patient reference number; leave "" if unknown.
        coverage_id: The insurance coverage reference; leave "" if unknown.
    """
    match = {k: v for k, v in {"urology_holding_id": urology_holding_id, "customer_id": customer_id, "coverage_id": coverage_id}.items() if v}
    if not match:
        return "Error: provide at least one reference number to search by."
    rows = ctx.find("urology_holdings", **match)
    return str(rows) if rows else f"No matching records for {match}."


@tool(owner="agent", rw="read")
def find_urology_shipments(ctx: ToolContext, urology_line_id: str = "", urology_holding_id: str = "", customer_id: str = "", coverage_id: str = "", original_line_id: str = "") -> str:
    """Look up urological supply lines: catheters and accessories shipped with quantity, ship date
    and covered-through date, payer and patient amounts or self-pay charges, denials, reversals,
    no-charge replacements and free samples. Every reference number below is optional; supply
    whichever are known. Matching records are returned in full; when none match, the reply says
    so.

    Args:
        urology_line_id: The urological shipment line reference; leave "" if unknown.
        urology_holding_id: The urological supply enrollment reference; leave "" if unknown.
        customer_id: The patient reference number; leave "" if unknown.
        coverage_id: The insurance coverage reference; leave "" if unknown.
        original_line_id: The reference of the original shipment line that this line reverses or
            replaces; leave "" if unknown.
    """
    match = {k: v for k, v in {"urology_line_id": urology_line_id, "urology_holding_id": urology_holding_id, "customer_id": customer_id, "coverage_id": coverage_id, "original_line_id": original_line_id}.items() if v}
    if not match:
        return "Error: provide at least one reference number to search by."
    rows = ctx.find("urology_shipments", **match)
    return str(rows) if rows else f"No matching records for {match}."


@tool(owner="agent", rw="read")
def find_urology_contacts(ctx: ToolContext, urology_contact_id: str = "", urology_holding_id: str = "", customer_id: str = "") -> str:
    """Look up refill contacts for a urological supply enrollment: date, channel, items asked for
    and reported supply status. Every reference number below is optional; supply whichever are
    known. Matching records are returned in full; when none match, the reply says so.

    Args:
        urology_contact_id: The urological refill contact reference; leave "" if unknown.
        urology_holding_id: The urological supply enrollment reference; leave "" if unknown.
        customer_id: The patient reference number; leave "" if unknown.
    """
    match = {k: v for k, v in {"urology_contact_id": urology_contact_id, "urology_holding_id": urology_holding_id, "customer_id": customer_id}.items() if v}
    if not match:
        return "Error: provide at least one reference number to search by."
    rows = ctx.find("urology_contacts", **match)
    return str(rows) if rows else f"No matching records for {match}."


@tool(owner="agent", rw="read")
def find_urology_requests(ctx: ToolContext, urology_request_id: str = "", customer_id: str = "", urology_holding_id: str = "") -> str:
    """Look up urological program requests such as prior authorizations and program-switch reviews,
    with their status and dates. Every reference number below is optional; supply whichever are
    known. Matching records are returned in full; when none match, the reply says so.

    Args:
        urology_request_id: The urological program request reference; leave "" if unknown.
        customer_id: The patient reference number; leave "" if unknown.
        urology_holding_id: The urological supply enrollment reference; leave "" if unknown.
    """
    match = {k: v for k, v in {"urology_request_id": urology_request_id, "customer_id": customer_id, "urology_holding_id": urology_holding_id}.items() if v}
    if not match:
        return "Error: provide at least one reference number to search by."
    rows = ctx.find("urology_requests", **match)
    return str(rows) if rows else f"No matching records for {match}."


@tool(owner="agent", rw="read")
def find_identity_verifications(ctx: ToolContext, verification_id: str = "", customer_id: str = "") -> str:
    """Look up the outcome of identity verification for a patient: whether the caller has been
    verified and when the latest attempt was made. Every reference number below is optional;
    supply whichever are known. Matching records are returned in full; when none match, the
    reply says so.

    Args:
        verification_id: The identity verification record reference; leave "" if unknown.
        customer_id: The patient reference number; leave "" if unknown.
    """
    match = {k: v for k, v in {"verification_id": verification_id, "customer_id": customer_id}.items() if v}
    if not match:
        return "Error: provide at least one reference number to search by."
    rows = ctx.find("identity_verifications", **match)
    return str(rows) if rows else f"No matching records for {match}."


@tool(owner="agent", rw="read")
def find_handoff_log(ctx: ToolContext, handoff_id: str = "", customer_id: str = "") -> str:
    """Look up transfers of a patient's call to a human representative, with the reason and the
    moment of the transfer. Every reference number below is optional; supply whichever are
    known. Matching records are returned in full; when none match, the reply says so.

    Args:
        handoff_id: The transfer-to-representative record reference; leave "" if unknown.
        customer_id: The patient reference number; leave "" if unknown.
    """
    match = {k: v for k, v in {"handoff_id": handoff_id, "customer_id": customer_id}.items() if v}
    if not match:
        return "Error: provide at least one reference number to search by."
    rows = ctx.find("handoff_log", **match)
    return str(rows) if rows else f"No matching records for {match}."


@tool(owner="agent", rw="write")
def verify_customer_identity(ctx: ToolContext, customer_id: str, date_of_birth: str = "",
                             phone_number: str = "", email: str = "", home_zip: str = "") -> str:
    """Verify the caller's identity and record the outcome; verification must pass before any account
    details are discussed or any business is transacted for the patient.

    This tool makes the comparison itself: it compares each piece of identity information the caller
    states with the patient profile, counts how many match, and passes only when at least 2 match. The
    patient reference number is used only to retrieve the profile and never counts as a match. Callers
    usually state only some of these details, so pass exactly the values the caller gave, in the
    format shown, and leave the rest "". The outcome is recorded; if a first attempt fails and a later
    attempt with more details passes, the pass stands.

    Args:
        customer_id: The patient reference number read from the patient profile lookup. Required; used
            only to retrieve the profile and not counted as a match.
        date_of_birth: The date of birth the caller states, as YYYY-MM-DD; leave "" if not stated.
        phone_number: The phone number the caller states, 10 digits without punctuation; leave "" if not stated.
        email: The email address the caller states, in lowercase; leave "" if not stated.
        home_zip: The 5-digit ZIP code of the home address the caller states; leave "" if not stated.
    """
    if not customer_id:
        return "Error: customer_id is required; look the patient up first and pass their reference number."
    rows = ctx.find("customers", customer_id=customer_id)
    if not rows:
        return f"Error: no patient {customer_id}; cannot verify."
    rec = rows[0]
    # The locator customer_id is deliberately not in `supplied`: fetching a profile is not proof.
    supplied = {"date_of_birth": date_of_birth, "phone_number": phone_number, "email": email,
                "home_zip": home_zip}
    matched = sum(1 for field, value in supplied.items() if value and str(rec.get(field)) == str(value))
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
    return (f"Identity verified for {customer_id} ({matched} detail(s) matched)." if verified
            else f"Identity NOT verified for {customer_id} (only {matched} of the required 2 details matched). "
                 "Ask the caller for another detail on file and try again.")


@tool(owner="agent", rw="write")
def transfer_to_human_agent(ctx: ToolContext, customer_id: str, reason: str) -> str:
    """Transfer the patient to a human patient-services representative and record the transfer with
    its reason.

    Use it in one of two situations only: when no Summit Ridge policy can resolve what the patient is
    asking for, or when the patient has explicitly asked to speak with a person at least 2 times during
    the call.

    Args:
        customer_id: The patient reference number read from the patient profile lookup.
        reason: Why the call is transferred; exactly one of POLICY_NOT_COVERED (no policy can resolve the
            request) or CUSTOMER_REQUESTED (the patient has explicitly asked for a person at least 2 times).
    """
    allowed = {"POLICY_NOT_COVERED", "CUSTOMER_REQUESTED"}
    if reason not in allowed:
        return f"Error: unknown transfer reason '{reason}'. Valid: {', '.join(sorted(allowed))}."
    if not ctx.find("customers", customer_id=customer_id):
        return f"Error: no patient {customer_id}; cannot record the transfer."
    rid = ctx.make_id("hof_", customer_id, reason)
    ctx.create("handoff_log", rid, handoff_id=rid, customer_id=customer_id, reason=reason,
               created_at=ctx.now())
    return f"Transfer to a human representative recorded for {customer_id} ({reason})."

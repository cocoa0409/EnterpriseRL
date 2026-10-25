"""Shared tools for env_0063_diabetes_and_medical_supply_company (Larkfield Medical Supply).

Every tool here is a share tool: always present in its owner's tool list. This module holds the
complete record-lookup layer (one finder per record type; the customer finder doubles as the
identity entry), the identity-verification write and the transfer-to-human handoff.
Scenario operational constants: identity verification passes when at least K = 2 credentials
match the profile; a human handoff for CUSTOMER_REQUESTED needs the customer to have asked for a
human R = 2 times.
"""

from erlbench import ToolContext, tool


@tool(owner="agent", rw="read")
def find_customers(ctx: ToolContext, customer_id: str = "", name: str = "", phone_number: str = "",
                   email: str = "", date_of_birth: str = "", zip_code: str = "") -> str:
    """Find the customer profile this conversation is about. Search by the customer reference
    number, or by what the caller can tell you - their name, registered phone number, email,
    date of birth or ZIP code; every criterion is optional, so supply whichever you have, and
    spacing, punctuation and capitalisation are ignored in the comparison. The profile returned
    carries the customer reference number, name, date of birth, phone number, email, shipping
    address, ZIP code, state and the date the profile was opened. Finding a profile does not
    verify the caller's identity.

    Args:
        customer_id: Reference number - the customer reference number; leave "" if unknown.
        name: The customer's full name as the caller states it; leave "" if not provided.
        phone_number: The registered phone number, 10 digits; leave "" if not provided.
        email: The registered email address; leave "" if not provided.
        date_of_birth: The date of birth, YYYY-MM-DD; leave "" if not provided.
        zip_code: The 5-digit ZIP code of the shipping address; leave "" if not provided.
    """
    match = {k: v for k, v in {"customer_id": customer_id, "name": name, "phone_number": phone_number,
                               "email": email, "date_of_birth": date_of_birth,
                               "zip_code": zip_code}.items() if v}
    if not match:
        return "Error: provide at least one reference number or profile detail to find the customer."
    rows = ctx.fuzzy_find("customers", **match)
    if not rows:
        return f"No customer matches {match}."
    if len(rows) > 1:
        return f"Error: {len(rows)} customers match {match}; ask for one more detail to tell them apart."
    return str(rows[0])

@tool(owner="agent", rw="read")
def find_coverages(ctx: ToolContext, coverage_id: str = "", customer_id: str = "", member_id: str = "") -> str:
    """Look up a customer's insurance coverage records on file: the payer or plan name, plan type,
    whether the coverage is primary or secondary, the member ID, whether it includes a drug benefit,
    its effective and termination dates, and the date Larkfield last verified eligibility with the
    payer. Every reference number below is optional; supply whichever you already hold, and all records matching every number supplied are returned. With no number supplied, every record of this kind is returned. When nothing matches, a short notice says so.

    Args:
        coverage_id: Reference number - the reference number of an insurance coverage record; leave "" if unknown.
        customer_id: Reference number - the customer reference number; leave "" if unknown.
        member_id: Reference number - member_id; leave "" if unknown.
    """
    match = {k: v for k, v in {"coverage_id": coverage_id, "customer_id": customer_id, "member_id": member_id}.items() if v}
    rows = ctx.find("coverages", **match)
    return str(rows) if rows else f"No coverages records for {match}."

@tool(owner="agent", rw="read")
def find_cgm_programs(ctx: ToolContext, cgm_program_id: str = "", customer_id: str = "", coverage_id: str = "") -> str:
    """Look up Continuous Glucose Monitoring Supply Program enrollments. Each enrollment shows its
    tier, its status, the insurance coverage it bills, enrollment, activation, hold and closing
    dates with their reasons, the treating prescriber's NPI, the product details on the newest
    written order, the billing units still authorized to ship and the customer's balance on the
    program. Every reference number below is optional; supply whichever you already hold, and all records matching every number supplied are returned. With no number supplied, every record of this kind is returned. When nothing matches, a short notice says so.

    Args:
        cgm_program_id: Reference number - the reference number of the Continuous Glucose Monitoring Supply Program enrollment itself; leave "" if unknown.
        customer_id: Reference number - the reference number of the customer who holds it; leave "" if unknown.
        coverage_id: Reference number - the reference number of the insurance coverage it bills; leave "" if unknown.
    """
    match = {k: v for k, v in {"cgm_program_id": cgm_program_id, "customer_id": customer_id, "coverage_id": coverage_id}.items() if v}
    rows = ctx.find("cgm_programs", **match)
    return str(rows) if rows else f"No cgm_programs records for {match}."

@tool(owner="agent", rw="read")
def find_cgm_orders(ctx: ToolContext, cgm_order_id: str = "", cgm_program_id: str = "", customer_id: str = "", related_cgm_order_id: str = "") -> str:
    """Look up the prescription and authorization file of Continuous Glucose Monitoring Supply Program
    enrollments: written orders received from prescribers, prior authorization requests,
    authorization grants with their approved units and valid dates, payer denials, clinical visit
    records received, and liability notices the customer signed. Every reference number below is optional; supply whichever you already hold, and all records matching every number supplied are returned. With no number supplied, every record of this kind is returned. When nothing matches, a short notice says so.

    Args:
        cgm_order_id: Reference number - the reference number of the order or authorization record itself; leave "" if unknown.
        cgm_program_id: Reference number - the reference number of the enrollment it belongs to; leave "" if unknown.
        customer_id: Reference number - the reference number of the customer; leave "" if unknown.
        related_cgm_order_id: Reference number - the reference number of the written order a request, grant or denial is based on; leave "" if unknown.
    """
    match = {k: v for k, v in {"cgm_order_id": cgm_order_id, "cgm_program_id": cgm_program_id, "customer_id": customer_id, "related_cgm_order_id": related_cgm_order_id}.items() if v}
    rows = ctx.find("cgm_orders", **match)
    return str(rows) if rows else f"No cgm_orders records for {match}."

@tool(owner="agent", rw="read")
def find_cgm_shipments(ctx: ToolContext, cgm_shipment_id: str = "", cgm_program_id: str = "", customer_id: str = "", cgm_order_id: str = "", original_cgm_shipment_id: str = "") -> str:
    """Look up the shipment history of Continuous Glucose Monitoring Supply Program enrollments: refill
    packages with their units, supply days, ship dates, shipping method and billing route,
    replacement packages, carrier proofs of delivery, return authorizations and accepted returns. Every reference number below is optional; supply whichever you already hold, and all records matching every number supplied are returned. With no number supplied, every record of this kind is returned. When nothing matches, a short notice says so.

    Args:
        cgm_shipment_id: Reference number - the reference number of the shipment record itself; leave "" if unknown.
        cgm_program_id: Reference number - the reference number of the enrollment it belongs to; leave "" if unknown.
        customer_id: Reference number - the reference number of the customer; leave "" if unknown.
        cgm_order_id: Reference number - the reference number of the authorization a refill draws on; leave "" if unknown.
        original_cgm_shipment_id: Reference number - the reference number of the original shipment a replacement, delivery proof or return concerns; leave "" if unknown.
    """
    match = {k: v for k, v in {"cgm_shipment_id": cgm_shipment_id, "cgm_program_id": cgm_program_id, "customer_id": customer_id, "cgm_order_id": cgm_order_id, "original_cgm_shipment_id": original_cgm_shipment_id}.items() if v}
    rows = ctx.find("cgm_shipments", **match)
    return str(rows) if rows else f"No cgm_shipments records for {match}."

@tool(owner="agent", rw="read")
def find_cgm_billing(ctx: ToolContext, cgm_ledger_id: str = "", cgm_program_id: str = "", customer_id: str = "", cgm_shipment_id: str = "", original_cgm_ledger_id: str = "") -> str:
    """Look up the billing history of Continuous Glucose Monitoring Supply Program enrollments: claims
    sent to payers, remittances with allowed, paid and patient-responsibility amounts, denials with
    their reason codes, appeals filed, patient charges, payments, balance adjustments and refunds. Every reference number below is optional; supply whichever you already hold, and all records matching every number supplied are returned. With no number supplied, every record of this kind is returned. When nothing matches, a short notice says so.

    Args:
        cgm_ledger_id: Reference number - the reference number of the billing record itself; leave "" if unknown.
        cgm_program_id: Reference number - the reference number of the enrollment it belongs to; leave "" if unknown.
        customer_id: Reference number - the reference number of the customer; leave "" if unknown.
        cgm_shipment_id: Reference number - the reference number of the shipment a claim or charge bills; leave "" if unknown.
        original_cgm_ledger_id: Reference number - the reference number of the billing record a remittance, denial, appeal, adjustment or refund answers; leave "" if unknown.
    """
    match = {k: v for k, v in {"cgm_ledger_id": cgm_ledger_id, "cgm_program_id": cgm_program_id, "customer_id": customer_id, "cgm_shipment_id": cgm_shipment_id, "original_cgm_ledger_id": original_cgm_ledger_id}.items() if v}
    rows = ctx.find("cgm_billing", **match)
    return str(rows) if rows else f"No cgm_billing records for {match}."

@tool(owner="agent", rw="read")
def find_cgm_requests(ctx: ToolContext, cgm_request_id: str = "", customer_id: str = "", cgm_program_id: str = "", cgm_shipment_id: str = "", cgm_ledger_id: str = "") -> str:
    """Look up customer requests logged on Continuous Glucose Monitoring Supply Program enrollments -
    program cancellations, payment plans, hardship applications and manufacturer warranty claims -
    with their status, the date they were logged and the details the customer asked for. Every reference number below is optional; supply whichever you already hold, and all records matching every number supplied are returned. With no number supplied, every record of this kind is returned. When nothing matches, a short notice says so.

    Args:
        cgm_request_id: Reference number - the reference number of the request itself; leave "" if unknown.
        customer_id: Reference number - the reference number of the customer; leave "" if unknown.
        cgm_program_id: Reference number - the reference number of the enrollment it concerns; leave "" if unknown.
        cgm_shipment_id: Reference number - the reference number of the shipment it concerns; leave "" if unknown.
        cgm_ledger_id: Reference number - the reference number of the billing record it concerns; leave "" if unknown.
    """
    match = {k: v for k, v in {"cgm_request_id": cgm_request_id, "customer_id": customer_id, "cgm_program_id": cgm_program_id, "cgm_shipment_id": cgm_shipment_id, "cgm_ledger_id": cgm_ledger_id}.items() if v}
    rows = ctx.find("cgm_requests", **match)
    return str(rows) if rows else f"No cgm_requests records for {match}."

@tool(owner="agent", rw="read")
def find_bgm_programs(ctx: ToolContext, bgm_program_id: str = "", customer_id: str = "", coverage_id: str = "") -> str:
    """Look up Blood Glucose Testing Supply Program enrollments. Each enrollment shows its tier, its
    status, the insurance coverage it bills, enrollment, activation, hold and closing dates with
    their reasons, the treating prescriber's NPI, the product details on the newest written order,
    the billing units still authorized to ship and the customer's balance on the program. Every reference number below is optional; supply whichever you already hold, and all records matching every number supplied are returned. With no number supplied, every record of this kind is returned. When nothing matches, a short notice says so.

    Args:
        bgm_program_id: Reference number - the reference number of the Blood Glucose Testing Supply Program enrollment itself; leave "" if unknown.
        customer_id: Reference number - the reference number of the customer who holds it; leave "" if unknown.
        coverage_id: Reference number - the reference number of the insurance coverage it bills; leave "" if unknown.
    """
    match = {k: v for k, v in {"bgm_program_id": bgm_program_id, "customer_id": customer_id, "coverage_id": coverage_id}.items() if v}
    rows = ctx.find("bgm_programs", **match)
    return str(rows) if rows else f"No bgm_programs records for {match}."

@tool(owner="agent", rw="read")
def find_bgm_orders(ctx: ToolContext, bgm_order_id: str = "", bgm_program_id: str = "", customer_id: str = "", related_bgm_order_id: str = "") -> str:
    """Look up the prescription and authorization file of Blood Glucose Testing Supply Program
    enrollments: written orders received from prescribers, prior authorization requests,
    authorization grants with their approved units and valid dates, payer denials, clinical visit
    records received, and liability notices the customer signed. Every reference number below is optional; supply whichever you already hold, and all records matching every number supplied are returned. With no number supplied, every record of this kind is returned. When nothing matches, a short notice says so.

    Args:
        bgm_order_id: Reference number - the reference number of the order or authorization record itself; leave "" if unknown.
        bgm_program_id: Reference number - the reference number of the enrollment it belongs to; leave "" if unknown.
        customer_id: Reference number - the reference number of the customer; leave "" if unknown.
        related_bgm_order_id: Reference number - the reference number of the written order a request, grant or denial is based on; leave "" if unknown.
    """
    match = {k: v for k, v in {"bgm_order_id": bgm_order_id, "bgm_program_id": bgm_program_id, "customer_id": customer_id, "related_bgm_order_id": related_bgm_order_id}.items() if v}
    rows = ctx.find("bgm_orders", **match)
    return str(rows) if rows else f"No bgm_orders records for {match}."

@tool(owner="agent", rw="read")
def find_bgm_shipments(ctx: ToolContext, bgm_shipment_id: str = "", bgm_program_id: str = "", customer_id: str = "", bgm_order_id: str = "", original_bgm_shipment_id: str = "") -> str:
    """Look up the shipment history of Blood Glucose Testing Supply Program enrollments: refill
    packages with their units, supply days, ship dates, shipping method and billing route,
    replacement packages, carrier proofs of delivery, return authorizations and accepted returns. Every reference number below is optional; supply whichever you already hold, and all records matching every number supplied are returned. With no number supplied, every record of this kind is returned. When nothing matches, a short notice says so.

    Args:
        bgm_shipment_id: Reference number - the reference number of the shipment record itself; leave "" if unknown.
        bgm_program_id: Reference number - the reference number of the enrollment it belongs to; leave "" if unknown.
        customer_id: Reference number - the reference number of the customer; leave "" if unknown.
        bgm_order_id: Reference number - the reference number of the authorization a refill draws on; leave "" if unknown.
        original_bgm_shipment_id: Reference number - the reference number of the original shipment a replacement, delivery proof or return concerns; leave "" if unknown.
    """
    match = {k: v for k, v in {"bgm_shipment_id": bgm_shipment_id, "bgm_program_id": bgm_program_id, "customer_id": customer_id, "bgm_order_id": bgm_order_id, "original_bgm_shipment_id": original_bgm_shipment_id}.items() if v}
    rows = ctx.find("bgm_shipments", **match)
    return str(rows) if rows else f"No bgm_shipments records for {match}."

@tool(owner="agent", rw="read")
def find_bgm_billing(ctx: ToolContext, bgm_ledger_id: str = "", bgm_program_id: str = "", customer_id: str = "", bgm_shipment_id: str = "", original_bgm_ledger_id: str = "") -> str:
    """Look up the billing history of Blood Glucose Testing Supply Program enrollments: claims sent to
    payers, remittances with allowed, paid and patient-responsibility amounts, denials with their
    reason codes, appeals filed, patient charges, payments, balance adjustments and refunds. Every reference number below is optional; supply whichever you already hold, and all records matching every number supplied are returned. With no number supplied, every record of this kind is returned. When nothing matches, a short notice says so.

    Args:
        bgm_ledger_id: Reference number - the reference number of the billing record itself; leave "" if unknown.
        bgm_program_id: Reference number - the reference number of the enrollment it belongs to; leave "" if unknown.
        customer_id: Reference number - the reference number of the customer; leave "" if unknown.
        bgm_shipment_id: Reference number - the reference number of the shipment a claim or charge bills; leave "" if unknown.
        original_bgm_ledger_id: Reference number - the reference number of the billing record a remittance, denial, appeal, adjustment or refund answers; leave "" if unknown.
    """
    match = {k: v for k, v in {"bgm_ledger_id": bgm_ledger_id, "bgm_program_id": bgm_program_id, "customer_id": customer_id, "bgm_shipment_id": bgm_shipment_id, "original_bgm_ledger_id": original_bgm_ledger_id}.items() if v}
    rows = ctx.find("bgm_billing", **match)
    return str(rows) if rows else f"No bgm_billing records for {match}."

@tool(owner="agent", rw="read")
def find_bgm_requests(ctx: ToolContext, bgm_request_id: str = "", customer_id: str = "", bgm_program_id: str = "", bgm_shipment_id: str = "", bgm_ledger_id: str = "") -> str:
    """Look up customer requests logged on Blood Glucose Testing Supply Program enrollments - program
    cancellations, payment plans, hardship applications and manufacturer warranty claims - with
    their status, the date they were logged and the details the customer asked for. Every reference number below is optional; supply whichever you already hold, and all records matching every number supplied are returned. With no number supplied, every record of this kind is returned. When nothing matches, a short notice says so.

    Args:
        bgm_request_id: Reference number - the reference number of the request itself; leave "" if unknown.
        customer_id: Reference number - the reference number of the customer; leave "" if unknown.
        bgm_program_id: Reference number - the reference number of the enrollment it concerns; leave "" if unknown.
        bgm_shipment_id: Reference number - the reference number of the shipment it concerns; leave "" if unknown.
        bgm_ledger_id: Reference number - the reference number of the billing record it concerns; leave "" if unknown.
    """
    match = {k: v for k, v in {"bgm_request_id": bgm_request_id, "customer_id": customer_id, "bgm_program_id": bgm_program_id, "bgm_shipment_id": bgm_shipment_id, "bgm_ledger_id": bgm_ledger_id}.items() if v}
    rows = ctx.find("bgm_requests", **match)
    return str(rows) if rows else f"No bgm_requests records for {match}."

@tool(owner="agent", rw="read")
def find_pump_programs(ctx: ToolContext, pump_program_id: str = "", customer_id: str = "", coverage_id: str = "") -> str:
    """Look up Insulin Pump Program enrollments. Each enrollment shows its tier, its status, the
    insurance coverage it bills, enrollment, activation, hold and closing dates with their reasons,
    the treating prescriber's NPI, the product details on the newest written order, the billing
    units still authorized to ship and the customer's balance on the program. Every reference number below is optional; supply whichever you already hold, and all records matching every number supplied are returned. With no number supplied, every record of this kind is returned. When nothing matches, a short notice says so.

    Args:
        pump_program_id: Reference number - the reference number of the Insulin Pump Program enrollment itself; leave "" if unknown.
        customer_id: Reference number - the reference number of the customer who holds it; leave "" if unknown.
        coverage_id: Reference number - the reference number of the insurance coverage it bills; leave "" if unknown.
    """
    match = {k: v for k, v in {"pump_program_id": pump_program_id, "customer_id": customer_id, "coverage_id": coverage_id}.items() if v}
    rows = ctx.find("pump_programs", **match)
    return str(rows) if rows else f"No pump_programs records for {match}."

@tool(owner="agent", rw="read")
def find_pump_orders(ctx: ToolContext, pump_order_id: str = "", pump_program_id: str = "", customer_id: str = "", related_pump_order_id: str = "") -> str:
    """Look up the prescription and authorization file of Insulin Pump Program enrollments: written
    orders received from prescribers, prior authorization requests, authorization grants with their
    approved units and valid dates, payer denials, clinical visit records received, and liability
    notices the customer signed. Every reference number below is optional; supply whichever you already hold, and all records matching every number supplied are returned. With no number supplied, every record of this kind is returned. When nothing matches, a short notice says so.

    Args:
        pump_order_id: Reference number - the reference number of the order or authorization record itself; leave "" if unknown.
        pump_program_id: Reference number - the reference number of the enrollment it belongs to; leave "" if unknown.
        customer_id: Reference number - the reference number of the customer; leave "" if unknown.
        related_pump_order_id: Reference number - the reference number of the written order a request, grant or denial is based on; leave "" if unknown.
    """
    match = {k: v for k, v in {"pump_order_id": pump_order_id, "pump_program_id": pump_program_id, "customer_id": customer_id, "related_pump_order_id": related_pump_order_id}.items() if v}
    rows = ctx.find("pump_orders", **match)
    return str(rows) if rows else f"No pump_orders records for {match}."

@tool(owner="agent", rw="read")
def find_pump_shipments(ctx: ToolContext, pump_shipment_id: str = "", pump_program_id: str = "", customer_id: str = "", pump_order_id: str = "", original_pump_shipment_id: str = "") -> str:
    """Look up the shipment history of Insulin Pump Program enrollments: refill packages with their
    units, supply days, ship dates, shipping method and billing route, replacement packages, carrier
    proofs of delivery, return authorizations and accepted returns. Every reference number below is optional; supply whichever you already hold, and all records matching every number supplied are returned. With no number supplied, every record of this kind is returned. When nothing matches, a short notice says so.

    Args:
        pump_shipment_id: Reference number - the reference number of the shipment record itself; leave "" if unknown.
        pump_program_id: Reference number - the reference number of the enrollment it belongs to; leave "" if unknown.
        customer_id: Reference number - the reference number of the customer; leave "" if unknown.
        pump_order_id: Reference number - the reference number of the authorization a refill draws on; leave "" if unknown.
        original_pump_shipment_id: Reference number - the reference number of the original shipment a replacement, delivery proof or return concerns; leave "" if unknown.
    """
    match = {k: v for k, v in {"pump_shipment_id": pump_shipment_id, "pump_program_id": pump_program_id, "customer_id": customer_id, "pump_order_id": pump_order_id, "original_pump_shipment_id": original_pump_shipment_id}.items() if v}
    rows = ctx.find("pump_shipments", **match)
    return str(rows) if rows else f"No pump_shipments records for {match}."

@tool(owner="agent", rw="read")
def find_pump_billing(ctx: ToolContext, pump_ledger_id: str = "", pump_program_id: str = "", customer_id: str = "", pump_shipment_id: str = "", original_pump_ledger_id: str = "") -> str:
    """Look up the billing history of Insulin Pump Program enrollments: claims sent to payers,
    remittances with allowed, paid and patient-responsibility amounts, denials with their reason
    codes, appeals filed, patient charges, payments, balance adjustments and refunds. Every reference number below is optional; supply whichever you already hold, and all records matching every number supplied are returned. With no number supplied, every record of this kind is returned. When nothing matches, a short notice says so.

    Args:
        pump_ledger_id: Reference number - the reference number of the billing record itself; leave "" if unknown.
        pump_program_id: Reference number - the reference number of the enrollment it belongs to; leave "" if unknown.
        customer_id: Reference number - the reference number of the customer; leave "" if unknown.
        pump_shipment_id: Reference number - the reference number of the shipment a claim or charge bills; leave "" if unknown.
        original_pump_ledger_id: Reference number - the reference number of the billing record a remittance, denial, appeal, adjustment or refund answers; leave "" if unknown.
    """
    match = {k: v for k, v in {"pump_ledger_id": pump_ledger_id, "pump_program_id": pump_program_id, "customer_id": customer_id, "pump_shipment_id": pump_shipment_id, "original_pump_ledger_id": original_pump_ledger_id}.items() if v}
    rows = ctx.find("pump_billing", **match)
    return str(rows) if rows else f"No pump_billing records for {match}."

@tool(owner="agent", rw="read")
def find_pump_requests(ctx: ToolContext, pump_request_id: str = "", customer_id: str = "", pump_program_id: str = "", pump_shipment_id: str = "", pump_ledger_id: str = "") -> str:
    """Look up customer requests logged on Insulin Pump Program enrollments - program cancellations,
    payment plans, hardship applications and manufacturer warranty claims - with their status, the
    date they were logged and the details the customer asked for. Every reference number below is optional; supply whichever you already hold, and all records matching every number supplied are returned. With no number supplied, every record of this kind is returned. When nothing matches, a short notice says so.

    Args:
        pump_request_id: Reference number - the reference number of the request itself; leave "" if unknown.
        customer_id: Reference number - the reference number of the customer; leave "" if unknown.
        pump_program_id: Reference number - the reference number of the enrollment it concerns; leave "" if unknown.
        pump_shipment_id: Reference number - the reference number of the shipment it concerns; leave "" if unknown.
        pump_ledger_id: Reference number - the reference number of the billing record it concerns; leave "" if unknown.
    """
    match = {k: v for k, v in {"pump_request_id": pump_request_id, "customer_id": customer_id, "pump_program_id": pump_program_id, "pump_shipment_id": pump_shipment_id, "pump_ledger_id": pump_ledger_id}.items() if v}
    rows = ctx.find("pump_requests", **match)
    return str(rows) if rows else f"No pump_requests records for {match}."

@tool(owner="agent", rw="read")
def find_insulin_programs(ctx: ToolContext, insulin_program_id: str = "", customer_id: str = "", coverage_id: str = "") -> str:
    """Look up Insulin and Injection Supply Pharmacy Program enrollments. Each enrollment shows its
    tier, its status, the insurance coverage it bills, enrollment, activation, hold and closing
    dates with their reasons, the treating prescriber's NPI, the product details on the newest
    written order, the billing units still authorized to ship and the customer's balance on the
    program. Every reference number below is optional; supply whichever you already hold, and all records matching every number supplied are returned. With no number supplied, every record of this kind is returned. When nothing matches, a short notice says so.

    Args:
        insulin_program_id: Reference number - the reference number of the Insulin and Injection Supply Pharmacy Program enrollment itself; leave "" if unknown.
        customer_id: Reference number - the reference number of the customer who holds it; leave "" if unknown.
        coverage_id: Reference number - the reference number of the insurance coverage it bills; leave "" if unknown.
    """
    match = {k: v for k, v in {"insulin_program_id": insulin_program_id, "customer_id": customer_id, "coverage_id": coverage_id}.items() if v}
    rows = ctx.find("insulin_programs", **match)
    return str(rows) if rows else f"No insulin_programs records for {match}."

@tool(owner="agent", rw="read")
def find_insulin_orders(ctx: ToolContext, insulin_order_id: str = "", insulin_program_id: str = "", customer_id: str = "", related_insulin_order_id: str = "") -> str:
    """Look up the prescription and authorization file of Insulin and Injection Supply Pharmacy Program
    enrollments: written orders received from prescribers, prior authorization requests,
    authorization grants with their approved units and valid dates, payer denials, clinical visit
    records received, and liability notices the customer signed. Every reference number below is optional; supply whichever you already hold, and all records matching every number supplied are returned. With no number supplied, every record of this kind is returned. When nothing matches, a short notice says so.

    Args:
        insulin_order_id: Reference number - the reference number of the order or authorization record itself; leave "" if unknown.
        insulin_program_id: Reference number - the reference number of the enrollment it belongs to; leave "" if unknown.
        customer_id: Reference number - the reference number of the customer; leave "" if unknown.
        related_insulin_order_id: Reference number - the reference number of the written order a request, grant or denial is based on; leave "" if unknown.
    """
    match = {k: v for k, v in {"insulin_order_id": insulin_order_id, "insulin_program_id": insulin_program_id, "customer_id": customer_id, "related_insulin_order_id": related_insulin_order_id}.items() if v}
    rows = ctx.find("insulin_orders", **match)
    return str(rows) if rows else f"No insulin_orders records for {match}."

@tool(owner="agent", rw="read")
def find_insulin_shipments(ctx: ToolContext, insulin_shipment_id: str = "", insulin_program_id: str = "", customer_id: str = "", insulin_order_id: str = "", original_insulin_shipment_id: str = "") -> str:
    """Look up the shipment history of Insulin and Injection Supply Pharmacy Program enrollments:
    refill packages with their units, supply days, ship dates, shipping method and billing route,
    replacement packages, carrier proofs of delivery, return authorizations and accepted returns. Every reference number below is optional; supply whichever you already hold, and all records matching every number supplied are returned. With no number supplied, every record of this kind is returned. When nothing matches, a short notice says so.

    Args:
        insulin_shipment_id: Reference number - the reference number of the shipment record itself; leave "" if unknown.
        insulin_program_id: Reference number - the reference number of the enrollment it belongs to; leave "" if unknown.
        customer_id: Reference number - the reference number of the customer; leave "" if unknown.
        insulin_order_id: Reference number - the reference number of the authorization a refill draws on; leave "" if unknown.
        original_insulin_shipment_id: Reference number - the reference number of the original shipment a replacement, delivery proof or return concerns; leave "" if unknown.
    """
    match = {k: v for k, v in {"insulin_shipment_id": insulin_shipment_id, "insulin_program_id": insulin_program_id, "customer_id": customer_id, "insulin_order_id": insulin_order_id, "original_insulin_shipment_id": original_insulin_shipment_id}.items() if v}
    rows = ctx.find("insulin_shipments", **match)
    return str(rows) if rows else f"No insulin_shipments records for {match}."

@tool(owner="agent", rw="read")
def find_insulin_billing(ctx: ToolContext, insulin_ledger_id: str = "", insulin_program_id: str = "", customer_id: str = "", insulin_shipment_id: str = "", original_insulin_ledger_id: str = "") -> str:
    """Look up the billing history of Insulin and Injection Supply Pharmacy Program enrollments: claims
    sent to payers, remittances with allowed, paid and patient-responsibility amounts, denials with
    their reason codes, appeals filed, patient charges, payments, balance adjustments and refunds. Every reference number below is optional; supply whichever you already hold, and all records matching every number supplied are returned. With no number supplied, every record of this kind is returned. When nothing matches, a short notice says so.

    Args:
        insulin_ledger_id: Reference number - the reference number of the billing record itself; leave "" if unknown.
        insulin_program_id: Reference number - the reference number of the enrollment it belongs to; leave "" if unknown.
        customer_id: Reference number - the reference number of the customer; leave "" if unknown.
        insulin_shipment_id: Reference number - the reference number of the shipment a claim or charge bills; leave "" if unknown.
        original_insulin_ledger_id: Reference number - the reference number of the billing record a remittance, denial, appeal, adjustment or refund answers; leave "" if unknown.
    """
    match = {k: v for k, v in {"insulin_ledger_id": insulin_ledger_id, "insulin_program_id": insulin_program_id, "customer_id": customer_id, "insulin_shipment_id": insulin_shipment_id, "original_insulin_ledger_id": original_insulin_ledger_id}.items() if v}
    rows = ctx.find("insulin_billing", **match)
    return str(rows) if rows else f"No insulin_billing records for {match}."

@tool(owner="agent", rw="read")
def find_insulin_requests(ctx: ToolContext, insulin_request_id: str = "", customer_id: str = "", insulin_program_id: str = "", insulin_shipment_id: str = "", insulin_ledger_id: str = "") -> str:
    """Look up customer requests logged on Insulin and Injection Supply Pharmacy Program enrollments -
    program cancellations, payment plans, hardship applications and manufacturer warranty claims -
    with their status, the date they were logged and the details the customer asked for. Every reference number below is optional; supply whichever you already hold, and all records matching every number supplied are returned. With no number supplied, every record of this kind is returned. When nothing matches, a short notice says so.

    Args:
        insulin_request_id: Reference number - the reference number of the request itself; leave "" if unknown.
        customer_id: Reference number - the reference number of the customer; leave "" if unknown.
        insulin_program_id: Reference number - the reference number of the enrollment it concerns; leave "" if unknown.
        insulin_shipment_id: Reference number - the reference number of the shipment it concerns; leave "" if unknown.
        insulin_ledger_id: Reference number - the reference number of the billing record it concerns; leave "" if unknown.
    """
    match = {k: v for k, v in {"insulin_request_id": insulin_request_id, "customer_id": customer_id, "insulin_program_id": insulin_program_id, "insulin_shipment_id": insulin_shipment_id, "insulin_ledger_id": insulin_ledger_id}.items() if v}
    rows = ctx.find("insulin_requests", **match)
    return str(rows) if rows else f"No insulin_requests records for {match}."

@tool(owner="agent", rw="read")
def find_ostomy_programs(ctx: ToolContext, ostomy_program_id: str = "", customer_id: str = "", coverage_id: str = "") -> str:
    """Look up Ostomy Supply Program enrollments. Each enrollment shows its tier, its status, the
    insurance coverage it bills, enrollment, activation, hold and closing dates with their reasons,
    the treating prescriber's NPI, the product details on the newest written order, the billing
    units still authorized to ship and the customer's balance on the program. Every reference number below is optional; supply whichever you already hold, and all records matching every number supplied are returned. With no number supplied, every record of this kind is returned. When nothing matches, a short notice says so.

    Args:
        ostomy_program_id: Reference number - the reference number of the Ostomy Supply Program enrollment itself; leave "" if unknown.
        customer_id: Reference number - the reference number of the customer who holds it; leave "" if unknown.
        coverage_id: Reference number - the reference number of the insurance coverage it bills; leave "" if unknown.
    """
    match = {k: v for k, v in {"ostomy_program_id": ostomy_program_id, "customer_id": customer_id, "coverage_id": coverage_id}.items() if v}
    rows = ctx.find("ostomy_programs", **match)
    return str(rows) if rows else f"No ostomy_programs records for {match}."

@tool(owner="agent", rw="read")
def find_ostomy_orders(ctx: ToolContext, ostomy_order_id: str = "", ostomy_program_id: str = "", customer_id: str = "", related_ostomy_order_id: str = "") -> str:
    """Look up the prescription and authorization file of Ostomy Supply Program enrollments: written
    orders received from prescribers, prior authorization requests, authorization grants with their
    approved units and valid dates, payer denials, clinical visit records received, and liability
    notices the customer signed. Every reference number below is optional; supply whichever you already hold, and all records matching every number supplied are returned. With no number supplied, every record of this kind is returned. When nothing matches, a short notice says so.

    Args:
        ostomy_order_id: Reference number - the reference number of the order or authorization record itself; leave "" if unknown.
        ostomy_program_id: Reference number - the reference number of the enrollment it belongs to; leave "" if unknown.
        customer_id: Reference number - the reference number of the customer; leave "" if unknown.
        related_ostomy_order_id: Reference number - the reference number of the written order a request, grant or denial is based on; leave "" if unknown.
    """
    match = {k: v for k, v in {"ostomy_order_id": ostomy_order_id, "ostomy_program_id": ostomy_program_id, "customer_id": customer_id, "related_ostomy_order_id": related_ostomy_order_id}.items() if v}
    rows = ctx.find("ostomy_orders", **match)
    return str(rows) if rows else f"No ostomy_orders records for {match}."

@tool(owner="agent", rw="read")
def find_ostomy_shipments(ctx: ToolContext, ostomy_shipment_id: str = "", ostomy_program_id: str = "", customer_id: str = "", ostomy_order_id: str = "", original_ostomy_shipment_id: str = "") -> str:
    """Look up the shipment history of Ostomy Supply Program enrollments: refill packages with their
    units, supply days, ship dates, shipping method and billing route, replacement packages, carrier
    proofs of delivery, return authorizations and accepted returns. Every reference number below is optional; supply whichever you already hold, and all records matching every number supplied are returned. With no number supplied, every record of this kind is returned. When nothing matches, a short notice says so.

    Args:
        ostomy_shipment_id: Reference number - the reference number of the shipment record itself; leave "" if unknown.
        ostomy_program_id: Reference number - the reference number of the enrollment it belongs to; leave "" if unknown.
        customer_id: Reference number - the reference number of the customer; leave "" if unknown.
        ostomy_order_id: Reference number - the reference number of the authorization a refill draws on; leave "" if unknown.
        original_ostomy_shipment_id: Reference number - the reference number of the original shipment a replacement, delivery proof or return concerns; leave "" if unknown.
    """
    match = {k: v for k, v in {"ostomy_shipment_id": ostomy_shipment_id, "ostomy_program_id": ostomy_program_id, "customer_id": customer_id, "ostomy_order_id": ostomy_order_id, "original_ostomy_shipment_id": original_ostomy_shipment_id}.items() if v}
    rows = ctx.find("ostomy_shipments", **match)
    return str(rows) if rows else f"No ostomy_shipments records for {match}."

@tool(owner="agent", rw="read")
def find_ostomy_billing(ctx: ToolContext, ostomy_ledger_id: str = "", ostomy_program_id: str = "", customer_id: str = "", ostomy_shipment_id: str = "", original_ostomy_ledger_id: str = "") -> str:
    """Look up the billing history of Ostomy Supply Program enrollments: claims sent to payers,
    remittances with allowed, paid and patient-responsibility amounts, denials with their reason
    codes, appeals filed, patient charges, payments, balance adjustments and refunds. Every reference number below is optional; supply whichever you already hold, and all records matching every number supplied are returned. With no number supplied, every record of this kind is returned. When nothing matches, a short notice says so.

    Args:
        ostomy_ledger_id: Reference number - the reference number of the billing record itself; leave "" if unknown.
        ostomy_program_id: Reference number - the reference number of the enrollment it belongs to; leave "" if unknown.
        customer_id: Reference number - the reference number of the customer; leave "" if unknown.
        ostomy_shipment_id: Reference number - the reference number of the shipment a claim or charge bills; leave "" if unknown.
        original_ostomy_ledger_id: Reference number - the reference number of the billing record a remittance, denial, appeal, adjustment or refund answers; leave "" if unknown.
    """
    match = {k: v for k, v in {"ostomy_ledger_id": ostomy_ledger_id, "ostomy_program_id": ostomy_program_id, "customer_id": customer_id, "ostomy_shipment_id": ostomy_shipment_id, "original_ostomy_ledger_id": original_ostomy_ledger_id}.items() if v}
    rows = ctx.find("ostomy_billing", **match)
    return str(rows) if rows else f"No ostomy_billing records for {match}."

@tool(owner="agent", rw="read")
def find_ostomy_requests(ctx: ToolContext, ostomy_request_id: str = "", customer_id: str = "", ostomy_program_id: str = "", ostomy_shipment_id: str = "", ostomy_ledger_id: str = "") -> str:
    """Look up customer requests logged on Ostomy Supply Program enrollments - program cancellations,
    payment plans, hardship applications and manufacturer warranty claims - with their status, the
    date they were logged and the details the customer asked for. Every reference number below is optional; supply whichever you already hold, and all records matching every number supplied are returned. With no number supplied, every record of this kind is returned. When nothing matches, a short notice says so.

    Args:
        ostomy_request_id: Reference number - the reference number of the request itself; leave "" if unknown.
        customer_id: Reference number - the reference number of the customer; leave "" if unknown.
        ostomy_program_id: Reference number - the reference number of the enrollment it concerns; leave "" if unknown.
        ostomy_shipment_id: Reference number - the reference number of the shipment it concerns; leave "" if unknown.
        ostomy_ledger_id: Reference number - the reference number of the billing record it concerns; leave "" if unknown.
    """
    match = {k: v for k, v in {"ostomy_request_id": ostomy_request_id, "customer_id": customer_id, "ostomy_program_id": ostomy_program_id, "ostomy_shipment_id": ostomy_shipment_id, "ostomy_ledger_id": ostomy_ledger_id}.items() if v}
    rows = ctx.find("ostomy_requests", **match)
    return str(rows) if rows else f"No ostomy_requests records for {match}."

@tool(owner="agent", rw="read")
def find_continence_programs(ctx: ToolContext, continence_program_id: str = "", customer_id: str = "", coverage_id: str = "") -> str:
    """Look up Urology and Continence Supply Program enrollments. Each enrollment shows its tier, its
    status, the insurance coverage it bills, enrollment, activation, hold and closing dates with
    their reasons, the treating prescriber's NPI, the product details on the newest written order,
    the billing units still authorized to ship and the customer's balance on the program. Every reference number below is optional; supply whichever you already hold, and all records matching every number supplied are returned. With no number supplied, every record of this kind is returned. When nothing matches, a short notice says so.

    Args:
        continence_program_id: Reference number - the reference number of the Urology and Continence Supply Program enrollment itself; leave "" if unknown.
        customer_id: Reference number - the reference number of the customer who holds it; leave "" if unknown.
        coverage_id: Reference number - the reference number of the insurance coverage it bills; leave "" if unknown.
    """
    match = {k: v for k, v in {"continence_program_id": continence_program_id, "customer_id": customer_id, "coverage_id": coverage_id}.items() if v}
    rows = ctx.find("continence_programs", **match)
    return str(rows) if rows else f"No continence_programs records for {match}."

@tool(owner="agent", rw="read")
def find_continence_orders(ctx: ToolContext, continence_order_id: str = "", continence_program_id: str = "", customer_id: str = "", related_continence_order_id: str = "") -> str:
    """Look up the prescription and authorization file of Urology and Continence Supply Program
    enrollments: written orders received from prescribers, prior authorization requests,
    authorization grants with their approved units and valid dates, payer denials, clinical visit
    records received, and liability notices the customer signed. Every reference number below is optional; supply whichever you already hold, and all records matching every number supplied are returned. With no number supplied, every record of this kind is returned. When nothing matches, a short notice says so.

    Args:
        continence_order_id: Reference number - the reference number of the order or authorization record itself; leave "" if unknown.
        continence_program_id: Reference number - the reference number of the enrollment it belongs to; leave "" if unknown.
        customer_id: Reference number - the reference number of the customer; leave "" if unknown.
        related_continence_order_id: Reference number - the reference number of the written order a request, grant or denial is based on; leave "" if unknown.
    """
    match = {k: v for k, v in {"continence_order_id": continence_order_id, "continence_program_id": continence_program_id, "customer_id": customer_id, "related_continence_order_id": related_continence_order_id}.items() if v}
    rows = ctx.find("continence_orders", **match)
    return str(rows) if rows else f"No continence_orders records for {match}."

@tool(owner="agent", rw="read")
def find_continence_shipments(ctx: ToolContext, continence_shipment_id: str = "", continence_program_id: str = "", customer_id: str = "", continence_order_id: str = "", original_continence_shipment_id: str = "") -> str:
    """Look up the shipment history of Urology and Continence Supply Program enrollments: refill
    packages with their units, supply days, ship dates, shipping method and billing route,
    replacement packages, carrier proofs of delivery, return authorizations and accepted returns. Every reference number below is optional; supply whichever you already hold, and all records matching every number supplied are returned. With no number supplied, every record of this kind is returned. When nothing matches, a short notice says so.

    Args:
        continence_shipment_id: Reference number - the reference number of the shipment record itself; leave "" if unknown.
        continence_program_id: Reference number - the reference number of the enrollment it belongs to; leave "" if unknown.
        customer_id: Reference number - the reference number of the customer; leave "" if unknown.
        continence_order_id: Reference number - the reference number of the authorization a refill draws on; leave "" if unknown.
        original_continence_shipment_id: Reference number - the reference number of the original shipment a replacement, delivery proof or return concerns; leave "" if unknown.
    """
    match = {k: v for k, v in {"continence_shipment_id": continence_shipment_id, "continence_program_id": continence_program_id, "customer_id": customer_id, "continence_order_id": continence_order_id, "original_continence_shipment_id": original_continence_shipment_id}.items() if v}
    rows = ctx.find("continence_shipments", **match)
    return str(rows) if rows else f"No continence_shipments records for {match}."

@tool(owner="agent", rw="read")
def find_continence_billing(ctx: ToolContext, continence_ledger_id: str = "", continence_program_id: str = "", customer_id: str = "", continence_shipment_id: str = "", original_continence_ledger_id: str = "") -> str:
    """Look up the billing history of Urology and Continence Supply Program enrollments: claims sent to
    payers, remittances with allowed, paid and patient-responsibility amounts, denials with their
    reason codes, appeals filed, patient charges, payments, balance adjustments and refunds. Every reference number below is optional; supply whichever you already hold, and all records matching every number supplied are returned. With no number supplied, every record of this kind is returned. When nothing matches, a short notice says so.

    Args:
        continence_ledger_id: Reference number - the reference number of the billing record itself; leave "" if unknown.
        continence_program_id: Reference number - the reference number of the enrollment it belongs to; leave "" if unknown.
        customer_id: Reference number - the reference number of the customer; leave "" if unknown.
        continence_shipment_id: Reference number - the reference number of the shipment a claim or charge bills; leave "" if unknown.
        original_continence_ledger_id: Reference number - the reference number of the billing record a remittance, denial, appeal, adjustment or refund answers; leave "" if unknown.
    """
    match = {k: v for k, v in {"continence_ledger_id": continence_ledger_id, "continence_program_id": continence_program_id, "customer_id": customer_id, "continence_shipment_id": continence_shipment_id, "original_continence_ledger_id": original_continence_ledger_id}.items() if v}
    rows = ctx.find("continence_billing", **match)
    return str(rows) if rows else f"No continence_billing records for {match}."

@tool(owner="agent", rw="read")
def find_continence_requests(ctx: ToolContext, continence_request_id: str = "", customer_id: str = "", continence_program_id: str = "", continence_shipment_id: str = "", continence_ledger_id: str = "") -> str:
    """Look up customer requests logged on Urology and Continence Supply Program enrollments - program
    cancellations, payment plans, hardship applications and manufacturer warranty claims - with
    their status, the date they were logged and the details the customer asked for. Every reference number below is optional; supply whichever you already hold, and all records matching every number supplied are returned. With no number supplied, every record of this kind is returned. When nothing matches, a short notice says so.

    Args:
        continence_request_id: Reference number - the reference number of the request itself; leave "" if unknown.
        customer_id: Reference number - the reference number of the customer; leave "" if unknown.
        continence_program_id: Reference number - the reference number of the enrollment it concerns; leave "" if unknown.
        continence_shipment_id: Reference number - the reference number of the shipment it concerns; leave "" if unknown.
        continence_ledger_id: Reference number - the reference number of the billing record it concerns; leave "" if unknown.
    """
    match = {k: v for k, v in {"continence_request_id": continence_request_id, "customer_id": customer_id, "continence_program_id": continence_program_id, "continence_shipment_id": continence_shipment_id, "continence_ledger_id": continence_ledger_id}.items() if v}
    rows = ctx.find("continence_requests", **match)
    return str(rows) if rows else f"No continence_requests records for {match}."

@tool(owner="agent", rw="read")
def find_wound_programs(ctx: ToolContext, wound_program_id: str = "", customer_id: str = "", coverage_id: str = "") -> str:
    """Look up Wound Care Supply Program enrollments. Each enrollment shows its tier, its status, the
    insurance coverage it bills, enrollment, activation, hold and closing dates with their reasons,
    the treating prescriber's NPI, the product details on the newest written order, the billing
    units still authorized to ship and the customer's balance on the program. Every reference number below is optional; supply whichever you already hold, and all records matching every number supplied are returned. With no number supplied, every record of this kind is returned. When nothing matches, a short notice says so.

    Args:
        wound_program_id: Reference number - the reference number of the Wound Care Supply Program enrollment itself; leave "" if unknown.
        customer_id: Reference number - the reference number of the customer who holds it; leave "" if unknown.
        coverage_id: Reference number - the reference number of the insurance coverage it bills; leave "" if unknown.
    """
    match = {k: v for k, v in {"wound_program_id": wound_program_id, "customer_id": customer_id, "coverage_id": coverage_id}.items() if v}
    rows = ctx.find("wound_programs", **match)
    return str(rows) if rows else f"No wound_programs records for {match}."

@tool(owner="agent", rw="read")
def find_wound_orders(ctx: ToolContext, wound_order_id: str = "", wound_program_id: str = "", customer_id: str = "", related_wound_order_id: str = "") -> str:
    """Look up the prescription and authorization file of Wound Care Supply Program enrollments:
    written orders received from prescribers, prior authorization requests, authorization grants
    with their approved units and valid dates, payer denials, clinical visit records received, and
    liability notices the customer signed. Every reference number below is optional; supply whichever you already hold, and all records matching every number supplied are returned. With no number supplied, every record of this kind is returned. When nothing matches, a short notice says so.

    Args:
        wound_order_id: Reference number - the reference number of the order or authorization record itself; leave "" if unknown.
        wound_program_id: Reference number - the reference number of the enrollment it belongs to; leave "" if unknown.
        customer_id: Reference number - the reference number of the customer; leave "" if unknown.
        related_wound_order_id: Reference number - the reference number of the written order a request, grant or denial is based on; leave "" if unknown.
    """
    match = {k: v for k, v in {"wound_order_id": wound_order_id, "wound_program_id": wound_program_id, "customer_id": customer_id, "related_wound_order_id": related_wound_order_id}.items() if v}
    rows = ctx.find("wound_orders", **match)
    return str(rows) if rows else f"No wound_orders records for {match}."

@tool(owner="agent", rw="read")
def find_wound_shipments(ctx: ToolContext, wound_shipment_id: str = "", wound_program_id: str = "", customer_id: str = "", wound_order_id: str = "", original_wound_shipment_id: str = "") -> str:
    """Look up the shipment history of Wound Care Supply Program enrollments: refill packages with
    their units, supply days, ship dates, shipping method and billing route, replacement packages,
    carrier proofs of delivery, return authorizations and accepted returns. Every reference number below is optional; supply whichever you already hold, and all records matching every number supplied are returned. With no number supplied, every record of this kind is returned. When nothing matches, a short notice says so.

    Args:
        wound_shipment_id: Reference number - the reference number of the shipment record itself; leave "" if unknown.
        wound_program_id: Reference number - the reference number of the enrollment it belongs to; leave "" if unknown.
        customer_id: Reference number - the reference number of the customer; leave "" if unknown.
        wound_order_id: Reference number - the reference number of the authorization a refill draws on; leave "" if unknown.
        original_wound_shipment_id: Reference number - the reference number of the original shipment a replacement, delivery proof or return concerns; leave "" if unknown.
    """
    match = {k: v for k, v in {"wound_shipment_id": wound_shipment_id, "wound_program_id": wound_program_id, "customer_id": customer_id, "wound_order_id": wound_order_id, "original_wound_shipment_id": original_wound_shipment_id}.items() if v}
    rows = ctx.find("wound_shipments", **match)
    return str(rows) if rows else f"No wound_shipments records for {match}."

@tool(owner="agent", rw="read")
def find_wound_billing(ctx: ToolContext, wound_ledger_id: str = "", wound_program_id: str = "", customer_id: str = "", wound_shipment_id: str = "", original_wound_ledger_id: str = "") -> str:
    """Look up the billing history of Wound Care Supply Program enrollments: claims sent to payers,
    remittances with allowed, paid and patient-responsibility amounts, denials with their reason
    codes, appeals filed, patient charges, payments, balance adjustments and refunds. Every reference number below is optional; supply whichever you already hold, and all records matching every number supplied are returned. With no number supplied, every record of this kind is returned. When nothing matches, a short notice says so.

    Args:
        wound_ledger_id: Reference number - the reference number of the billing record itself; leave "" if unknown.
        wound_program_id: Reference number - the reference number of the enrollment it belongs to; leave "" if unknown.
        customer_id: Reference number - the reference number of the customer; leave "" if unknown.
        wound_shipment_id: Reference number - the reference number of the shipment a claim or charge bills; leave "" if unknown.
        original_wound_ledger_id: Reference number - the reference number of the billing record a remittance, denial, appeal, adjustment or refund answers; leave "" if unknown.
    """
    match = {k: v for k, v in {"wound_ledger_id": wound_ledger_id, "wound_program_id": wound_program_id, "customer_id": customer_id, "wound_shipment_id": wound_shipment_id, "original_wound_ledger_id": original_wound_ledger_id}.items() if v}
    rows = ctx.find("wound_billing", **match)
    return str(rows) if rows else f"No wound_billing records for {match}."

@tool(owner="agent", rw="read")
def find_wound_requests(ctx: ToolContext, wound_request_id: str = "", customer_id: str = "", wound_program_id: str = "", wound_shipment_id: str = "", wound_ledger_id: str = "") -> str:
    """Look up customer requests logged on Wound Care Supply Program enrollments - program
    cancellations, payment plans, hardship applications and manufacturer warranty claims - with
    their status, the date they were logged and the details the customer asked for. Every reference number below is optional; supply whichever you already hold, and all records matching every number supplied are returned. With no number supplied, every record of this kind is returned. When nothing matches, a short notice says so.

    Args:
        wound_request_id: Reference number - the reference number of the request itself; leave "" if unknown.
        customer_id: Reference number - the reference number of the customer; leave "" if unknown.
        wound_program_id: Reference number - the reference number of the enrollment it concerns; leave "" if unknown.
        wound_shipment_id: Reference number - the reference number of the shipment it concerns; leave "" if unknown.
        wound_ledger_id: Reference number - the reference number of the billing record it concerns; leave "" if unknown.
    """
    match = {k: v for k, v in {"wound_request_id": wound_request_id, "customer_id": customer_id, "wound_program_id": wound_program_id, "wound_shipment_id": wound_shipment_id, "wound_ledger_id": wound_ledger_id}.items() if v}
    rows = ctx.find("wound_requests", **match)
    return str(rows) if rows else f"No wound_requests records for {match}."

@tool(owner="agent", rw="read")
def find_identity_verifications(ctx: ToolContext, verification_id: str = "", customer_id: str = "") -> str:
    """Look up the outcome of identity verification for a customer during this service contact -
    whether the caller's identity has been verified and when it was last checked. Every reference number below is optional; supply whichever you already hold, and all records matching every number supplied are returned. With no number supplied, every record of this kind is returned. When nothing matches, a short notice says so.

    Args:
        verification_id: Reference number - the reference number of an identity verification record; leave "" if unknown.
        customer_id: Reference number - the customer reference number; leave "" if unknown.
    """
    match = {k: v for k, v in {"verification_id": verification_id, "customer_id": customer_id}.items() if v}
    rows = ctx.find("identity_verifications", **match)
    return str(rows) if rows else f"No identity_verifications records for {match}."

@tool(owner="agent", rw="read")
def find_human_handoffs(ctx: ToolContext, handoff_id: str = "", customer_id: str = "") -> str:
    """Look up the handoffs to a human representative recorded for a customer, with the reason and
    moment of each. Every reference number below is optional; supply whichever you already hold, and all records matching every number supplied are returned. With no number supplied, every record of this kind is returned. When nothing matches, a short notice says so.

    Args:
        handoff_id: Reference number - the reference number of a handoff record; leave "" if unknown.
        customer_id: Reference number - the customer reference number; leave "" if unknown.
    """
    match = {k: v for k, v in {"handoff_id": handoff_id, "customer_id": customer_id}.items() if v}
    rows = ctx.find("human_handoffs", **match)
    return str(rows) if rows else f"No human_handoffs records for {match}."

@tool(owner="agent", rw="write")
def verify_customer_identity(ctx: ToolContext, customer_id: str, date_of_birth: str = "", phone_number: str = "",
                             email: str = "", zip_code: str = "") -> str:
    """Verify the caller's identity against the customer profile and record the outcome. The caller's
    identity must be verified before any enrollment, order, shipment or billing information is
    discussed or any change is made on the customer's account. This tool performs the comparison
    itself: it compares each identity detail the caller states with the profile on file, counts how
    many match, and passes only when at least 2 match. The customer reference number only retrieves
    the profile and never counts as a match. Callers often state only some details, so pass exactly
    the values the caller gave, verbatim, and leave the rest "". The outcome is recorded; when a first
    attempt fails and a later attempt with more details passes, the pass stands.

    Args:
        customer_id: Reference number - the customer reference number read from the customer profile lookup. Required; used only to retrieve the profile and not counted as a match.
        date_of_birth: The date of birth the caller states, YYYY-MM-DD; leave "" if not stated.
        phone_number: The registered phone number the caller states, 10 digits with no punctuation; leave "" if not stated.
        email: The registered email address the caller states; leave "" if not stated.
        zip_code: The 5-digit ZIP code of the shipping address the caller states; leave "" if not stated.
    """
    if not customer_id:
        return "Error: customer_id is required; find the customer profile first and pass its reference number."
    rows = ctx.find("customers", customer_id=customer_id)
    if not rows:
        return f"Error: no customer {customer_id}; cannot verify."
    rec = rows[0]
    # The tool owns the comparison; the locator customer_id is deliberately not a credential.
    supplied = {"date_of_birth": date_of_birth, "phone_number": phone_number, "email": email, "zip_code": zip_code}
    matched = sum(1 for field, value in supplied.items() if value and str(rec.get(field)) == str(value))
    verified = matched >= 2
    rid = ctx.make_id("ver_", customer_id)
    # Store only the reproducible boolean; upsert and never downgrade a prior pass.
    prior = ctx.find("identity_verifications", verification_id=rid)
    verified = verified or bool(prior and prior[0].get("verified"))
    if prior:
        ctx.update("identity_verifications", rid, verified=verified, verified_at=ctx.now())
    else:
        ctx.create("identity_verifications", rid, verification_id=rid, customer_id=customer_id,
                   verified=verified, verified_at=ctx.now())
    return (f"Identity verified for {customer_id} ({matched} detail(s) matched)." if verified
            else f"Identity NOT verified for {customer_id} (only {matched} of the required 2 details matched). "
                 "Ask the caller for another detail on file and call this tool again.")


@tool(owner="agent", rw="write")
def transfer_to_human_agent(ctx: ToolContext, customer_id: str, reason: str) -> str:
    """Hand the customer over to a human Larkfield patient-services representative and record the
    handoff with its reason. Use it when no Larkfield policy can resolve what the customer is asking
    for, or when the customer has explicitly asked to speak with a human representative 2 times.

    Args:
        customer_id: Reference number - the customer reference number read from the customer profile lookup; the profile must exist.
        reason: The reason for the handoff, exactly one of POLICY_NOT_COVERED or CUSTOMER_REQUESTED, never free text. POLICY_NOT_COVERED - no Larkfield policy offers a way to resolve the request. CUSTOMER_REQUESTED - the customer has explicitly asked for a human representative at least 2 times.
    """
    allowed = {"POLICY_NOT_COVERED", "CUSTOMER_REQUESTED"}
    if reason not in allowed:
        return f"Error: unknown handoff reason '{reason}'. Valid: {', '.join(sorted(allowed))}."
    if not ctx.find("customers", customer_id=customer_id):
        return f"Error: no customer {customer_id}; cannot record handoff."
    rid = ctx.make_id("hof_", customer_id, reason)
    ctx.create("human_handoffs", rid, handoff_id=rid, customer_id=customer_id,
               reason=reason, created_at=ctx.now())
    return f"Handoff to a human representative recorded for {customer_id} ({reason})."

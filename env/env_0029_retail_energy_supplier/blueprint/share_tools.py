"""Shared tools for env_0029_retail_energy_supplier (Beacon Ridge Energy customer care).

Path: env/env_0029_retail_energy_supplier/blueprint/share_tools.py

Every tool here is a share tool, always present in its owner's tool list: one finder per
table of the scenario (the customers finder doubles as the identity entry), the identity
verification write (passes at K = 2 matching credentials) and the handoff write (reason is
POLICY_NOT_COVERED or CUSTOMER_REQUESTED; a customer is handed off on request after asking
R = 2 times). Ordinary finders never encode business policy; they only look records up.
"""

from erlbench import ToolContext, tool


def _report(rows: list, label: str, match: dict) -> str:
    # Shared result wording of the per-table finders.
    if not rows:
        return f"No {label} found for {match or 'the request'}."
    return str(rows)


@tool(owner="agent", rw="read")
def find_customers(ctx: ToolContext, customer_id: str = "", name: str = "", phone_number: str = "",
                   email: str = "", business_name: str = "") -> str:
    """Find the customer profile a call is about.

    Search by the Beacon Ridge customer number, or by what the caller can naturally tell you:
    the account holder's name, the phone number or email address registered on the profile,
    or, for a business, its registered business name. Give whichever you have; spacing,
    punctuation and capital letters do not matter. The profile returned shows whether the
    customer is a household or a business, the contact details, the mailing address and ZIP
    code, the date the profile was opened, whether the utility has confirmed an assistance
    program enrollment, and a business's commercial credit grade. Finding a profile does not
    verify the caller's identity.

    Args:
        customer_id: The Beacon Ridge customer number; leave "" if unknown.
        name: The account holder's full name as the caller states it; leave "" if not given.
        phone_number: The registered phone number, 10 digits; leave "" if not given.
        email: The registered email address; leave "" if not given.
        business_name: The registered legal name of a business customer; leave "" if not given.
    """
    match = {k: v for k, v in {"customer_id": customer_id, "name": name, "phone_number": phone_number,
                               "email": email, "business_name": business_name}.items() if v}
    if not match:
        return "Error: provide at least one detail to find the customer."
    rows = ctx.fuzzy_find("customers", **match)
    if not rows:
        return f"No customer matches {match}."
    if len(rows) > 1:
        return f"Error: {len(rows)} customers match {match}; ask the caller for one more detail."
    return str(rows[0])


@tool(owner="agent", rw="read")
def find_premises(ctx: ToolContext, premise_id: str = "", customer_id: str = "") -> str:
    """Look up the service premises on file: the service address and state, the electric and gas
    utilities with their account numbers, the meter type, the next scheduled meter read date,
    any move-out final bill date, the historical annual electricity and gas usage, and the
    capacity and transmission tags of a large facility. Every premise a customer holds can be
    listed with the customer number alone.
    Every reference number below is optional; supply whichever you hold. All matching
    records are returned, or a plain message when none match.

    Args:
        premise_id: The reference number of the service premise (the address supplied); leave "" if unknown.
        customer_id: The Beacon Ridge customer number of the account holder; leave "" if unknown.
    """
    match = {k: v for k, v in {"premise_id": premise_id, "customer_id": customer_id}.items() if v}
    rows = ctx.find("premises", **match)
    return _report(rows, "premises records", match)


@tool(owner="agent", rw="read")
def find_price_offers(ctx: ToolContext, price_offer_id: str = "") -> str:
    """Look up Beacon Ridge's current and past price sheet: for each plan and utility territory,
    the rate offered for new enrollments, plan changes and renewals priced at the time, its
    unit, the first and last day it may be used and the printed offer code. Call it with no
    reference number to read the whole price sheet.
    Every reference number below is optional; supply whichever you hold. All matching
    records are returned, or a plain message when none match.

    Args:
        price_offer_id: The reference number of one price sheet entry; leave "" if unknown.
    """
    match = {k: v for k, v in {"price_offer_id": price_offer_id}.items() if v}
    rows = ctx.find("price_offers", **match)
    return _report(rows, "price offers records", match)


@tool(owner="agent", rw="read")
def find_identity_verifications(ctx: ToolContext, verification_id: str = "", customer_id: str = "") -> str:
    """Look up the outcome of identity verification for a caller's account: whether the caller has
    been verified and when the latest attempt took place.
    Every reference number below is optional; supply whichever you hold. All matching
    records are returned, or a plain message when none match.

    Args:
        verification_id: The reference number of an identity verification outcome; leave "" if unknown.
        customer_id: The Beacon Ridge customer number of the account holder; leave "" if unknown.
    """
    match = {k: v for k, v in {"verification_id": verification_id, "customer_id": customer_id}.items() if v}
    rows = ctx.find("identity_verifications", **match)
    return _report(rows, "identity verifications records", match)


@tool(owner="agent", rw="read")
def find_human_handoffs(ctx: ToolContext, handoff_id: str = "", customer_id: str = "") -> str:
    """Look up earlier handoffs of a customer to a human representative, with the reason recorded
    and the moment of the handoff.
    Every reference number below is optional; supply whichever you hold. All matching
    records are returned, or a plain message when none match.

    Args:
        handoff_id: The reference number of a handoff to a human representative; leave "" if unknown.
        customer_id: The Beacon Ridge customer number of the account holder; leave "" if unknown.
    """
    match = {k: v for k, v in {"handoff_id": handoff_id, "customer_id": customer_id}.items() if v}
    rows = ctx.find("human_handoffs", **match)
    return _report(rows, "human handoffs records", match)


@tool(owner="agent", rw="read")
def find_power_agreements(ctx: ToolContext, power_agreement_id: str = "", customer_id: str = "", premise_id: str = "", referred_by_customer_id: str = "") -> str:
    """Look up residential electricity agreements: the plan in force, the agreement status,
    enrollment date and channel, the utility's confirmation letter date, supply start date,
    term, contract rate and end date, any referral, pending or completed cancellation details,
    the latest plan change, renewal or rollover date, and any rescission or utility rejection. A
    customer's agreements across all premises can be listed with the customer number.
    Every reference number below is optional; supply whichever you hold. All matching
    records are returned, or a plain message when none match.

    Args:
        power_agreement_id: The residential electricity agreement number; leave "" if unknown.
        customer_id: The Beacon Ridge customer number of the account holder; leave "" if unknown.
        premise_id: The reference number of the service premise (the address supplied); leave "" if unknown.
        referred_by_customer_id: The customer number of the person who referred this customer; leave "" if unknown.
    """
    match = {k: v for k, v in {"power_agreement_id": power_agreement_id, "customer_id": customer_id, "premise_id": premise_id, "referred_by_customer_id": referred_by_customer_id}.items() if v}
    rows = ctx.find("power_agreements", **match)
    return _report(rows, "power agreements records", match)


@tool(owner="agent", rw="read")
def find_power_billing(ctx: ToolContext, power_billing_id: str = "", power_agreement_id: str = "", customer_id: str = "", source_billing_id: str = "", referred_customer_id: str = "") -> str:
    """Look up the Beacon Ridge electricity lines printed on a customer's utility bills: energy
    charges by cycle and time-of-use period with kWh and rate, monthly service fees, early
    termination fees with the months counted, sign-up, online, referral, dual-fuel and renewal
    loyalty credits, and rebill credits that point to the line they corrected.
    Every reference number below is optional; supply whichever you hold. All matching
    records are returned, or a plain message when none match.

    Args:
        power_billing_id: The reference number of one electricity bill line; leave "" if unknown.
        power_agreement_id: The residential electricity agreement number; leave "" if unknown.
        customer_id: The Beacon Ridge customer number of the account holder; leave "" if unknown.
        source_billing_id: The reference number of the original bill line that a rebill credit, refund or dispute concerns; leave "" if unknown.
        referred_customer_id: The customer number of a referred friend or neighbour named on a referral credit; leave "" if unknown.
    """
    match = {k: v for k, v in {"power_billing_id": power_billing_id, "power_agreement_id": power_agreement_id, "customer_id": customer_id, "source_billing_id": source_billing_id, "referred_customer_id": referred_customer_id}.items() if v}
    rows = ctx.find("power_billing", **match)
    return _report(rows, "power billing records", match)


@tool(owner="agent", rw="read")
def find_power_notices(ctx: ToolContext, power_notice_id: str = "", power_agreement_id: str = "", customer_id: str = "") -> str:
    """Look up the notices Beacon Ridge sent about a residential electricity agreement: initial
    renewal and final options notices with the offered plan, renewal rate and rollover rate, and
    variable rate change or regulatory pass-through notices with their notice and effective
    dates and delivery channel.
    Every reference number below is optional; supply whichever you hold. All matching
    records are returned, or a plain message when none match.

    Args:
        power_notice_id: The reference number of one electricity notice; leave "" if unknown.
        power_agreement_id: The residential electricity agreement number; leave "" if unknown.
        customer_id: The Beacon Ridge customer number of the account holder; leave "" if unknown.
    """
    match = {k: v for k, v in {"power_notice_id": power_notice_id, "power_agreement_id": power_agreement_id, "customer_id": customer_id}.items() if v}
    rows = ctx.find("power_notices", **match)
    return _report(rows, "power notices records", match)


@tool(owner="agent", rw="read")
def find_power_billing_disputes(ctx: ToolContext, power_dispute_id: str = "", customer_id: str = "", power_agreement_id: str = "", source_billing_id: str = "") -> str:
    """Look up residential electricity billing disputes referred to billing review, with the line
    disputed, the amount in question and the review status.
    Every reference number below is optional; supply whichever you hold. All matching
    records are returned, or a plain message when none match.

    Args:
        power_dispute_id: The reference number of an electricity billing dispute; leave "" if unknown.
        customer_id: The Beacon Ridge customer number of the account holder; leave "" if unknown.
        power_agreement_id: The residential electricity agreement number; leave "" if unknown.
        source_billing_id: The reference number of the original bill line that a rebill credit, refund or dispute concerns; leave "" if unknown.
    """
    match = {k: v for k, v in {"power_dispute_id": power_dispute_id, "customer_id": customer_id, "power_agreement_id": power_agreement_id, "source_billing_id": source_billing_id}.items() if v}
    rows = ctx.find("power_billing_disputes", **match)
    return _report(rows, "power billing disputes records", match)


@tool(owner="agent", rw="read")
def find_gas_agreements(ctx: ToolContext, gas_agreement_id: str = "", customer_id: str = "", premise_id: str = "") -> str:
    """Look up residential natural gas agreements: plan, status, enrollment details, the utility's
    confirmation date, supply start, term, rate per therm (which is also the ceiling of a capped
    plan), end date, the ship date of an included smart thermostat, cancellation details and the
    latest plan change, renewal or rollover.
    Every reference number below is optional; supply whichever you hold. All matching
    records are returned, or a plain message when none match.

    Args:
        gas_agreement_id: The residential natural gas agreement number; leave "" if unknown.
        customer_id: The Beacon Ridge customer number of the account holder; leave "" if unknown.
        premise_id: The reference number of the service premise (the address supplied); leave "" if unknown.
    """
    match = {k: v for k, v in {"gas_agreement_id": gas_agreement_id, "customer_id": customer_id, "premise_id": premise_id}.items() if v}
    rows = ctx.find("gas_agreements", **match)
    return _report(rows, "gas agreements records", match)


@tool(owner="agent", rw="read")
def find_gas_billing(ctx: ToolContext, gas_billing_id: str = "", gas_agreement_id: str = "", customer_id: str = "", source_billing_id: str = "") -> str:
    """Look up the Beacon Ridge gas lines on a customer's utility bills: therm charges and service
    fees by cycle, early termination and thermostat recovery fees, sign-up and renewal loyalty
    credits, and rebill credits linked to the line they corrected.
    Every reference number below is optional; supply whichever you hold. All matching
    records are returned, or a plain message when none match.

    Args:
        gas_billing_id: The reference number of one gas bill line; leave "" if unknown.
        gas_agreement_id: The residential natural gas agreement number; leave "" if unknown.
        customer_id: The Beacon Ridge customer number of the account holder; leave "" if unknown.
        source_billing_id: The reference number of the original bill line that a rebill credit, refund or dispute concerns; leave "" if unknown.
    """
    match = {k: v for k, v in {"gas_billing_id": gas_billing_id, "gas_agreement_id": gas_agreement_id, "customer_id": customer_id, "source_billing_id": source_billing_id}.items() if v}
    rows = ctx.find("gas_billing", **match)
    return _report(rows, "gas billing records", match)


@tool(owner="agent", rw="read")
def find_gas_notices(ctx: ToolContext, gas_notice_id: str = "", gas_agreement_id: str = "", customer_id: str = "") -> str:
    """Look up gas expiration notices with their renewal offers and rollover rates, and monthly
    variable or regulatory pass-through rate notices, each with notice and effective dates.
    Every reference number below is optional; supply whichever you hold. All matching
    records are returned, or a plain message when none match.

    Args:
        gas_notice_id: The reference number of one gas notice; leave "" if unknown.
        gas_agreement_id: The residential natural gas agreement number; leave "" if unknown.
        customer_id: The Beacon Ridge customer number of the account holder; leave "" if unknown.
    """
    match = {k: v for k, v in {"gas_notice_id": gas_notice_id, "gas_agreement_id": gas_agreement_id, "customer_id": customer_id}.items() if v}
    rows = ctx.find("gas_notices", **match)
    return _report(rows, "gas notices records", match)


@tool(owner="agent", rw="read")
def find_gas_billing_disputes(ctx: ToolContext, gas_dispute_id: str = "", customer_id: str = "", gas_agreement_id: str = "", source_billing_id: str = "") -> str:
    """Look up residential gas billing disputes referred to billing review and where each one
    stands.
    Every reference number below is optional; supply whichever you hold. All matching
    records are returned, or a plain message when none match.

    Args:
        gas_dispute_id: The reference number of a gas billing dispute; leave "" if unknown.
        customer_id: The Beacon Ridge customer number of the account holder; leave "" if unknown.
        gas_agreement_id: The residential natural gas agreement number; leave "" if unknown.
        source_billing_id: The reference number of the original bill line that a rebill credit, refund or dispute concerns; leave "" if unknown.
    """
    match = {k: v for k, v in {"gas_dispute_id": gas_dispute_id, "customer_id": customer_id, "gas_agreement_id": gas_agreement_id, "source_billing_id": source_billing_id}.items() if v}
    rows = ctx.find("gas_billing_disputes", **match)
    return _report(rows, "gas billing disputes records", match)


@tool(owner="agent", rw="read")
def find_bizpower_agreements(ctx: ToolContext, bizpower_agreement_id: str = "", customer_id: str = "", premise_id: str = "") -> str:
    """Look up small business electricity agreements site by site: plan, status, enrollment channel
    (including broker), utility confirmation, supply start, term, rate, end date, the renewal
    election and whether the current term renewed automatically, site transfers, sales tax
    exemption status, and cancellation or closing details. All of a business's sites can be
    listed with its customer number.
    Every reference number below is optional; supply whichever you hold. All matching
    records are returned, or a plain message when none match.

    Args:
        bizpower_agreement_id: The small business electricity agreement number for one site; leave "" if unknown.
        customer_id: The Beacon Ridge customer number of the account holder; leave "" if unknown.
        premise_id: The reference number of the service premise (the address supplied); leave "" if unknown.
    """
    match = {k: v for k, v in {"bizpower_agreement_id": bizpower_agreement_id, "customer_id": customer_id, "premise_id": premise_id}.items() if v}
    rows = ctx.find("bizpower_agreements", **match)
    return _report(rows, "bizpower agreements records", match)


@tool(owner="agent", rw="read")
def find_bizpower_billing(ctx: ToolContext, bizpower_billing_id: str = "", bizpower_agreement_id: str = "", customer_id: str = "", premise_id: str = "", source_billing_id: str = "") -> str:
    """Look up the business electricity lines on a site's utility bills: energy charges, service
    fees and sales tax by cycle with the rate and taxed base, early termination and site
    transfer fees, sign-up, multi-site and loyalty credits, and rebill credits linked to the
    line corrected.
    Every reference number below is optional; supply whichever you hold. All matching
    records are returned, or a plain message when none match.

    Args:
        bizpower_billing_id: The reference number of one business electricity bill line; leave "" if unknown.
        bizpower_agreement_id: The small business electricity agreement number for one site; leave "" if unknown.
        customer_id: The Beacon Ridge customer number of the account holder; leave "" if unknown.
        premise_id: The reference number of the site named on a site transfer or termination fee line; leave "" if unknown.
        source_billing_id: The reference number of the original bill line that a rebill credit, refund or dispute concerns; leave "" if unknown.
    """
    match = {k: v for k, v in {"bizpower_billing_id": bizpower_billing_id, "bizpower_agreement_id": bizpower_agreement_id, "customer_id": customer_id, "premise_id": premise_id, "source_billing_id": source_billing_id}.items() if v}
    rows = ctx.find("bizpower_billing", **match)
    return _report(rows, "bizpower billing records", match)


@tool(owner="agent", rw="read")
def find_bizpower_notices(ctx: ToolContext, bizpower_notice_id: str = "", bizpower_agreement_id: str = "", customer_id: str = "") -> str:
    """Look up business electricity notices: initial renewal and final options notices with the
    offered plan, renewal rate and rollover rate, and variable or pass-through rate notices.
    Every reference number below is optional; supply whichever you hold. All matching
    records are returned, or a plain message when none match.

    Args:
        bizpower_notice_id: The reference number of one business electricity notice; leave "" if unknown.
        bizpower_agreement_id: The small business electricity agreement number for one site; leave "" if unknown.
        customer_id: The Beacon Ridge customer number of the account holder; leave "" if unknown.
    """
    match = {k: v for k, v in {"bizpower_notice_id": bizpower_notice_id, "bizpower_agreement_id": bizpower_agreement_id, "customer_id": customer_id}.items() if v}
    rows = ctx.find("bizpower_notices", **match)
    return _report(rows, "bizpower notices records", match)


@tool(owner="agent", rw="read")
def find_bizpower_billing_disputes(ctx: ToolContext, bizpower_dispute_id: str = "", customer_id: str = "", bizpower_agreement_id: str = "", source_billing_id: str = "") -> str:
    """Look up business electricity billing disputes referred to billing review and their status.
    Every reference number below is optional; supply whichever you hold. All matching
    records are returned, or a plain message when none match.

    Args:
        bizpower_dispute_id: The reference number of a business electricity billing dispute; leave "" if unknown.
        customer_id: The Beacon Ridge customer number of the account holder; leave "" if unknown.
        bizpower_agreement_id: The small business electricity agreement number for one site; leave "" if unknown.
        source_billing_id: The reference number of the original bill line that a rebill credit, refund or dispute concerns; leave "" if unknown.
    """
    match = {k: v for k, v in {"bizpower_dispute_id": bizpower_dispute_id, "customer_id": customer_id, "bizpower_agreement_id": bizpower_agreement_id, "source_billing_id": source_billing_id}.items() if v}
    rows = ctx.find("bizpower_billing_disputes", **match)
    return _report(rows, "bizpower billing disputes records", match)


@tool(owner="agent", rw="read")
def find_bizgas_agreements(ctx: ToolContext, bizgas_agreement_id: str = "", customer_id: str = "", premise_id: str = "") -> str:
    """Look up commercial natural gas agreements: plan structure, status, enrollment and
    confirmation dates, supply start, term, the locked price component, contracted annual
    therms, end date, rollover or renewal start date, sales tax exemption and cancellation
    details.
    Every reference number below is optional; supply whichever you hold. All matching
    records are returned, or a plain message when none match.

    Args:
        bizgas_agreement_id: The commercial gas agreement number for one site; leave "" if unknown.
        customer_id: The Beacon Ridge customer number of the account holder; leave "" if unknown.
        premise_id: The reference number of the service premise (the address supplied); leave "" if unknown.
    """
    match = {k: v for k, v in {"bizgas_agreement_id": bizgas_agreement_id, "customer_id": customer_id, "premise_id": premise_id}.items() if v}
    rows = ctx.find("bizgas_agreements", **match)
    return _report(rows, "bizgas agreements records", match)


@tool(owner="agent", rw="read")
def find_bizgas_billing(ctx: ToolContext, bizgas_billing_id: str = "", bizgas_agreement_id: str = "", customer_id: str = "", source_billing_id: str = "") -> str:
    """Look up commercial gas bill lines: energy charges, swing excess and shortfall charges,
    service fees and sales tax by cycle, early termination damages with the therms counted,
    renewal loyalty credits and rebill credits linked to the line corrected.
    Every reference number below is optional; supply whichever you hold. All matching
    records are returned, or a plain message when none match.

    Args:
        bizgas_billing_id: The reference number of one commercial gas bill line; leave "" if unknown.
        bizgas_agreement_id: The commercial gas agreement number for one site; leave "" if unknown.
        customer_id: The Beacon Ridge customer number of the account holder; leave "" if unknown.
        source_billing_id: The reference number of the original bill line that a rebill credit, refund or dispute concerns; leave "" if unknown.
    """
    match = {k: v for k, v in {"bizgas_billing_id": bizgas_billing_id, "bizgas_agreement_id": bizgas_agreement_id, "customer_id": customer_id, "source_billing_id": source_billing_id}.items() if v}
    rows = ctx.find("bizgas_billing", **match)
    return _report(rows, "bizgas billing records", match)


@tool(owner="agent", rw="read")
def find_bizgas_notices(ctx: ToolContext, bizgas_notice_id: str = "", bizgas_agreement_id: str = "", customer_id: str = "") -> str:
    """Look up commercial gas notices: renewal offers, the monthly index and NYMEX settlement
    prices for each delivery month, and regulatory pass-throughs.
    Every reference number below is optional; supply whichever you hold. All matching
    records are returned, or a plain message when none match.

    Args:
        bizgas_notice_id: The reference number of one commercial gas notice; leave "" if unknown.
        bizgas_agreement_id: The commercial gas agreement number for one site; leave "" if unknown.
        customer_id: The Beacon Ridge customer number of the account holder; leave "" if unknown.
    """
    match = {k: v for k, v in {"bizgas_notice_id": bizgas_notice_id, "bizgas_agreement_id": bizgas_agreement_id, "customer_id": customer_id}.items() if v}
    rows = ctx.find("bizgas_notices", **match)
    return _report(rows, "bizgas notices records", match)


@tool(owner="agent", rw="read")
def find_bizgas_billing_disputes(ctx: ToolContext, bizgas_dispute_id: str = "", customer_id: str = "", bizgas_agreement_id: str = "", source_billing_id: str = "") -> str:
    """Look up commercial gas billing disputes referred to billing review and their status.
    Every reference number below is optional; supply whichever you hold. All matching
    records are returned, or a plain message when none match.

    Args:
        bizgas_dispute_id: The reference number of a commercial gas billing dispute; leave "" if unknown.
        customer_id: The Beacon Ridge customer number of the account holder; leave "" if unknown.
        bizgas_agreement_id: The commercial gas agreement number for one site; leave "" if unknown.
        source_billing_id: The reference number of the original bill line that a rebill credit, refund or dispute concerns; leave "" if unknown.
    """
    match = {k: v for k, v in {"bizgas_dispute_id": bizgas_dispute_id, "customer_id": customer_id, "bizgas_agreement_id": bizgas_agreement_id, "source_billing_id": source_billing_id}.items() if v}
    rows = ctx.find("bizgas_billing_disputes", **match)
    return _report(rows, "bizgas billing disputes records", match)


@tool(owner="agent", rw="read")
def find_cni_contracts(ctx: ToolContext, cni_contract_id: str = "", customer_id: str = "", premise_id: str = "", pricing_request_id: str = "") -> str:
    """Look up commercial and industrial electricity contracts: structure, status, the quote
    signed, signing and renewal dates, utility confirmation, supply and term start, term, quoted
    price or adder, block size, end date, holdover start, termination notice and effective
    dates, and closing details.
    Every reference number below is optional; supply whichever you hold. All matching
    records are returned, or a plain message when none match.

    Args:
        cni_contract_id: The commercial and industrial contract number; leave "" if unknown.
        customer_id: The Beacon Ridge customer number of the account holder; leave "" if unknown.
        premise_id: The reference number of the service premise (the address supplied); leave "" if unknown.
        pricing_request_id: The number of the quote signed for the current term; leave "" if unknown.
    """
    match = {k: v for k, v in {"cni_contract_id": cni_contract_id, "customer_id": customer_id, "premise_id": premise_id, "pricing_request_id": pricing_request_id}.items() if v}
    rows = ctx.find("cni_contracts", **match)
    return _report(rows, "cni contracts records", match)


@tool(owner="agent", rw="read")
def find_cni_billing(ctx: ToolContext, cni_billing_id: str = "", cni_contract_id: str = "", customer_id: str = "", source_billing_id: str = "") -> str:
    """Look up C&I bill lines: fixed, block and index energy charges with kWh and price, capacity
    and transmission pass-through charges with the tag, price and billing days used, early
    termination damages and rebill credits linked to the line corrected.
    Every reference number below is optional; supply whichever you hold. All matching
    records are returned, or a plain message when none match.

    Args:
        cni_billing_id: The reference number of one C&I bill line; leave "" if unknown.
        cni_contract_id: The commercial and industrial contract number; leave "" if unknown.
        customer_id: The Beacon Ridge customer number of the account holder; leave "" if unknown.
        source_billing_id: The reference number of the original bill line that a rebill credit, refund or dispute concerns; leave "" if unknown.
    """
    match = {k: v for k, v in {"cni_billing_id": cni_billing_id, "cni_contract_id": cni_contract_id, "customer_id": customer_id, "source_billing_id": source_billing_id}.items() if v}
    rows = ctx.find("cni_billing", **match)
    return _report(rows, "cni billing records", match)


@tool(owner="agent", rw="read")
def find_cni_deposits(ctx: ToolContext, cni_deposit_id: str = "", cni_contract_id: str = "", customer_id: str = "", source_deposit_id: str = "") -> str:
    """Look up security deposits received on C&I contracts, with the months and credit grade used
    to size them, and any refunds, each refund naming the deposit it returns.
    Every reference number below is optional; supply whichever you hold. All matching
    records are returned, or a plain message when none match.

    Args:
        cni_deposit_id: The reference number of one security deposit receipt or refund; leave "" if unknown.
        cni_contract_id: The commercial and industrial contract number; leave "" if unknown.
        customer_id: The Beacon Ridge customer number of the account holder; leave "" if unknown.
        source_deposit_id: The reference number of the deposit receipt that a refund returns; leave "" if unknown.
    """
    match = {k: v for k, v in {"cni_deposit_id": cni_deposit_id, "cni_contract_id": cni_contract_id, "customer_id": customer_id, "source_deposit_id": source_deposit_id}.items() if v}
    rows = ctx.find("cni_deposits", **match)
    return _report(rows, "cni deposits records", match)


@tool(owner="agent", rw="read")
def find_cni_notices(ctx: ToolContext, cni_notice_id: str = "", cni_contract_id: str = "", customer_id: str = "") -> str:
    """Look up C&I notices: monthly index prices, capacity prices by capacity year, transmission
    rates, regulatory pass-throughs and contract expiry notices, each with notice and effective
    dates.
    Every reference number below is optional; supply whichever you hold. All matching
    records are returned, or a plain message when none match.

    Args:
        cni_notice_id: The reference number of one C&I market or expiry notice; leave "" if unknown.
        cni_contract_id: The commercial and industrial contract number; leave "" if unknown.
        customer_id: The Beacon Ridge customer number of the account holder; leave "" if unknown.
    """
    match = {k: v for k, v in {"cni_notice_id": cni_notice_id, "cni_contract_id": cni_contract_id, "customer_id": customer_id}.items() if v}
    rows = ctx.find("cni_notices", **match)
    return _report(rows, "cni notices records", match)


@tool(owner="agent", rw="read")
def find_cni_pricing_requests(ctx: ToolContext, pricing_request_id: str = "", customer_id: str = "", premise_id: str = "", cni_contract_id: str = "") -> str:
    """Look up C&I pricing requests and quotes: the facility, structure and term requested, whether
    the request is for a new contract or a renewal, its status with the structuring desk, the
    quoted price and block, the quote date and the last day the quote may be signed.
    Every reference number below is optional; supply whichever you hold. All matching
    records are returned, or a plain message when none match.

    Args:
        pricing_request_id: The pricing request and quote number; leave "" if unknown.
        customer_id: The Beacon Ridge customer number of the account holder; leave "" if unknown.
        premise_id: The reference number of the service premise (the address supplied); leave "" if unknown.
        cni_contract_id: The contract number being renewed, for a renewal pricing request; leave "" if unknown.
    """
    match = {k: v for k, v in {"pricing_request_id": pricing_request_id, "customer_id": customer_id, "premise_id": premise_id, "cni_contract_id": cni_contract_id}.items() if v}
    rows = ctx.find("cni_pricing_requests", **match)
    return _report(rows, "cni pricing requests records", match)


@tool(owner="agent", rw="read")
def find_solar_subscriptions(ctx: ToolContext, solar_subscription_id: str = "", customer_id: str = "", premise_id: str = "", referred_by_customer_id: str = "") -> str:
    """Look up community solar subscriptions: plan, status, project, size, subscription and
    allocation dates, term end, referral, size changes, transfers, cancellation notice and
    effective dates, and closing details.
    Every reference number below is optional; supply whichever you hold. All matching
    records are returned, or a plain message when none match.

    Args:
        solar_subscription_id: The community solar subscription number; leave "" if unknown.
        customer_id: The Beacon Ridge customer number of the account holder; leave "" if unknown.
        premise_id: The reference number of the service premise (the address supplied); leave "" if unknown.
        referred_by_customer_id: The customer number of the person who referred this customer; leave "" if unknown.
    """
    match = {k: v for k, v in {"solar_subscription_id": solar_subscription_id, "customer_id": customer_id, "premise_id": premise_id, "referred_by_customer_id": referred_by_customer_id}.items() if v}
    rows = ctx.find("solar_subscriptions", **match)
    return _report(rows, "solar subscriptions records", match)


@tool(owner="agent", rw="read")
def find_solar_billing(ctx: ToolContext, solar_billing_id: str = "", solar_subscription_id: str = "", customer_id: str = "", referred_customer_id: str = "", source_billing_id: str = "") -> str:
    """Look up community solar invoice lines: monthly subscription fees with the utility credit
    value and discount used, cancellation fees, annual savings true-ups, sign-up and referral
    credits and rebill credits.
    Every reference number below is optional; supply whichever you hold. All matching
    records are returned, or a plain message when none match.

    Args:
        solar_billing_id: The reference number of one community solar invoice line; leave "" if unknown.
        solar_subscription_id: The community solar subscription number; leave "" if unknown.
        customer_id: The Beacon Ridge customer number of the account holder; leave "" if unknown.
        referred_customer_id: The customer number of a referred friend or neighbour named on a referral credit; leave "" if unknown.
        source_billing_id: The reference number of the original bill line that a rebill credit, refund or dispute concerns; leave "" if unknown.
    """
    match = {k: v for k, v in {"solar_billing_id": solar_billing_id, "solar_subscription_id": solar_subscription_id, "customer_id": customer_id, "referred_customer_id": referred_customer_id, "source_billing_id": source_billing_id}.items() if v}
    rows = ctx.find("solar_billing", **match)
    return _report(rows, "solar billing records", match)


@tool(owner="agent", rw="read")
def find_protect_plans(ctx: ToolContext, protect_plan_id: str = "", customer_id: str = "", premise_id: str = "", billing_agreement_id: str = "") -> str:
    """Look up home protection plans: plan, status, enrollment date and channel, coverage start,
    how the fee is billed and on which energy agreement, and any cancellation, reinstatement or
    move.
    Every reference number below is optional; supply whichever you hold. All matching
    records are returned, or a plain message when none match.

    Args:
        protect_plan_id: The home protection plan number; leave "" if unknown.
        customer_id: The Beacon Ridge customer number of the account holder; leave "" if unknown.
        premise_id: The reference number of the service premise (the address supplied); leave "" if unknown.
        billing_agreement_id: The electricity or gas agreement number whose bill carries the plan fee; leave "" if unknown.
    """
    match = {k: v for k, v in {"protect_plan_id": protect_plan_id, "customer_id": customer_id, "premise_id": premise_id, "billing_agreement_id": billing_agreement_id}.items() if v}
    rows = ctx.find("protect_plans", **match)
    return _report(rows, "protect plans records", match)


@tool(owner="agent", rw="read")
def find_protect_billing(ctx: ToolContext, protect_billing_id: str = "", protect_plan_id: str = "", customer_id: str = "", source_billing_id: str = "") -> str:
    """Look up protection plan fee lines: monthly fees, bundle credits, free-look refunds and
    rebill credits, each refund naming the fee line it returns.
    Every reference number below is optional; supply whichever you hold. All matching
    records are returned, or a plain message when none match.

    Args:
        protect_billing_id: The reference number of one protection plan fee line; leave "" if unknown.
        protect_plan_id: The home protection plan number; leave "" if unknown.
        customer_id: The Beacon Ridge customer number of the account holder; leave "" if unknown.
        source_billing_id: The reference number of the original bill line that a rebill credit, refund or dispute concerns; leave "" if unknown.
    """
    match = {k: v for k, v in {"protect_billing_id": protect_billing_id, "protect_plan_id": protect_plan_id, "customer_id": customer_id, "source_billing_id": source_billing_id}.items() if v}
    rows = ctx.find("protect_billing", **match)
    return _report(rows, "protect billing records", match)


@tool(owner="agent", rw="read")
def find_protect_claims(ctx: ToolContext, protect_claim_id: str = "", protect_plan_id: str = "", customer_id: str = "", repeat_of_claim_id: str = "") -> str:
    """Look up repair claims under protection plans: the system that failed, failure and filing
    dates, the kind of service, the unit's manufacture year, repair cost, amount paid, service
    fee and the claim outcome.
    Every reference number below is optional; supply whichever you hold. All matching
    records are returned, or a plain message when none match.

    Args:
        protect_claim_id: The repair claim number; leave "" if unknown.
        protect_plan_id: The home protection plan number; leave "" if unknown.
        customer_id: The Beacon Ridge customer number of the account holder; leave "" if unknown.
        repeat_of_claim_id: The claim number of an earlier repair that a return visit follows up; leave "" if unknown.
    """
    match = {k: v for k, v in {"protect_claim_id": protect_claim_id, "protect_plan_id": protect_plan_id, "customer_id": customer_id, "repeat_of_claim_id": repeat_of_claim_id}.items() if v}
    rows = ctx.find("protect_claims", **match)
    return _report(rows, "protect claims records", match)


@tool(owner="agent", rw="write")
def verify_customer_identity(ctx: ToolContext, customer_id: str, phone_number: str = "", email: str = "",
                             tax_id_last4: str = "", billing_zip: str = "", profile_opened_date: str = "") -> str:
    """Verify the caller's identity and record the outcome.

    The caller must pass verification before any account information is discussed or any
    change, charge or credit is made. This tool does the comparison itself: it checks each
    detail the caller states against the customer profile and passes only when at least 2
    details match exactly. The customer number only locates the profile and never counts as a
    match, and the name is not accepted as proof. Pass only the details the caller actually
    gave, exactly as given, and leave the rest blank. If a first attempt falls short, ask for
    another detail and call again; once a caller has passed, the pass stands.

    Args:
        customer_id: The Beacon Ridge customer number read from the customer profile; required.
        phone_number: The phone number the caller states, 10 digits without punctuation; leave "" if not stated.
        email: The email address the caller states; leave "" if not stated.
        tax_id_last4: The last four digits of the account holder's Social Security number, or of the business's federal EIN, as stated; leave "" if not stated.
        billing_zip: The 5-digit ZIP code of the mailing address, as stated; leave "" if not stated.
        profile_opened_date: The date the caller says the account was opened, as YYYY-MM-DD; leave "" if not stated.
    """
    if not customer_id:
        return "Error: customer_id is required; find the customer profile first."
    rows = ctx.find("customers", customer_id=customer_id)
    if not rows:
        return f"Error: no customer {customer_id}; cannot verify."
    rec = rows[0]
    # The locator customer_id is not a credential; only the stated details are compared.
    supplied = {"phone_number": phone_number, "email": email, "tax_id_last4": tax_id_last4,
                "billing_zip": billing_zip, "profile_opened_date": profile_opened_date}
    matched = sum(1 for field, value in supplied.items()
                  if value and str(rec.get(field, "")).strip().lower() == str(value).strip().lower())
    verified = matched >= 2
    rid = ctx.make_id("ver_", customer_id)
    # Upsert and never downgrade: a later pass after an earlier miss must end verified.
    prior = ctx.find("identity_verifications", verification_id=rid)
    verified = verified or bool(prior and prior[0].get("verified"))
    if prior:
        ctx.update("identity_verifications", rid, verified=verified, verified_at=ctx.now())
    else:
        ctx.create("identity_verifications", rid, verification_id=rid, customer_id=customer_id,
                   verified=verified, verified_at=ctx.now())
    if verified:
        return f"Identity verified for customer {customer_id}."
    return (f"Identity NOT verified for customer {customer_id}: only {matched} of the 2 required details matched. "
            "Ask the caller for another detail on file and try again.")


@tool(owner="agent", rw="write")
def transfer_to_human_agent(ctx: ToolContext, customer_id: str, reason: str) -> str:
    """Hand the customer over to a human representative and record why.

    Use POLICY_NOT_COVERED when no Beacon Ridge policy allows you to resolve what the customer
    is asking for. Use CUSTOMER_REQUESTED when the customer has explicitly asked for a human
    representative 2 times. The handoff is recorded with the moment it happened.

    Args:
        customer_id: The Beacon Ridge customer number read from the customer profile.
        reason: Exactly one of POLICY_NOT_COVERED or CUSTOMER_REQUESTED; never free text.
    """
    allowed = {"POLICY_NOT_COVERED", "CUSTOMER_REQUESTED"}
    if reason not in allowed:
        return f"Error: unknown handoff reason '{reason}'. Valid: {', '.join(sorted(allowed))}."
    if not ctx.find("customers", customer_id=customer_id):
        return f"Error: no customer {customer_id}; cannot record the handoff."
    rid = ctx.make_id("hof_", customer_id, reason)
    ctx.create("human_handoffs", rid, handoff_id=rid, customer_id=customer_id,
               reason=reason, created_at=ctx.now())
    return f"Handoff to a human representative recorded for customer {customer_id} ({reason})."

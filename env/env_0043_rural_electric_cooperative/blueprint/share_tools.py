"""Shared tools for env_0043_rural_electric_cooperative (Cedar Fork Electric Cooperative, Inc.).

Always-visible tools reused by every difficulty: one record finder per business record type (the
member-profile finder doubles as the identity entry), the identity verification write, and the
transfer-to-representative write. Ordinary finders encode no policy; every business decision is made
by the agent from the knowledge base and the records.
"""

from erlbench import ToolContext, tool

# Scenario-level operational constants (not product policy):
VERIFICATION_MATCHES_REQUIRED = 2   # K: credentials that must match the member profile
HUMAN_REQUEST_THRESHOLD = 2         # R: explicit requests for a human before a CUSTOMER_REQUESTED transfer


def _show(rows, what, match):
    return str(rows) if rows else f"No {what} found for {match}."


@tool(owner="agent", rw="read")
def find_customers(ctx: ToolContext, customer_id: str = "", name: str = "", phone_number: str = "",
                   email: str = "", member_number: str = "") -> str:
    """Find the member profile a call is about. Search by the customer reference number, or by what a caller
    can naturally tell you: the member name, the phone number on file, the email address on file, or the
    seven-digit membership number printed on every bill. Every criterion is optional; give whichever you
    have, and add another if more than one member matches. The profile returned shows the member name and
    legal form of membership, membership number, phone, email, mailing address, the last four digits of the
    Social Security or Employer Identification Number, the date the membership was accepted, and the date of
    death when a certified death certificate is on file. Finding a profile does not verify the caller.

    Args:
        customer_id: The customer reference number of the member, if already known; leave "" otherwise.
        name: The member name as the caller states it (a person, joint members, or a business or organization name); leave "" if not given.
        phone_number: The phone number the caller gives, ten digits; leave "" if not given.
        email: The email address the caller gives; leave "" if not given.
        member_number: The seven-digit membership number from the bill, leading zeros included (e.g. 0418237); leave "" if not given.
    """
    match = {k: v for k, v in {"customer_id": customer_id, "name": name, "phone_number": phone_number,
                               "email": email, "member_number": member_number}.items() if v}
    if not match:
        return "Error: provide at least one reference number or profile detail to find the member."
    rows = ctx.fuzzy_find("customers", **match)
    if not rows:
        return f"No member profile matches {match}."
    if len(rows) > 1:
        return f"Error: {len(rows)} member profiles match {match}; ask the caller for one more detail on file."
    return str(rows[0])

@tool(owner="agent", rw="read")
def find_identity_verifications(ctx: ToolContext, verification_id: str = "", customer_id: str = "") -> str:
    """Look up the identity verification outcome recorded for a member during this contact: whether the caller has passed verification and when it was last attempted. Every criterion is optional; supply whichever reference numbers you already hold (with none,
    every such record is returned). Returns all matching records, or a message that none was found.

    Args:
        verification_id: The reference number of an identity verification record; leave "" if unknown.
        customer_id: The member's customer reference number (the member whose records these are); leave "" if unknown.
    """
    match = {k: v for k, v in {"verification_id": verification_id, "customer_id": customer_id}.items() if v}
    rows = ctx.find("identity_verifications", **match)
    return _show(rows, "identity verifications records", match)

@tool(owner="agent", rw="read")
def find_handoffs(ctx: ToolContext, handoff_id: str = "", customer_id: str = "") -> str:
    """Look up transfers of a member's call to a human member services representative, with the reason recorded and when the transfer was made. Every criterion is optional; supply whichever reference numbers you already hold (with none,
    every such record is returned). Returns all matching records, or a message that none was found.

    Args:
        handoff_id: The reference number of a transfer-to-representative record; leave "" if unknown.
        customer_id: The member's customer reference number (the member whose records these are); leave "" if unknown.
    """
    match = {k: v for k, v in {"handoff_id": handoff_id, "customer_id": customer_id}.items() if v}
    rows = ctx.find("handoffs", **match)
    return _show(rows, "handoffs records", match)

@tool(owner="agent", rw="read")
def find_service_accounts(ctx: ToolContext, service_account_id: str = "", customer_id: str = "") -> str:
    """Look up a member's electric service accounts, one for each metered location. Each account shows its rate schedule, account number, service address, meter number and meter capability, phase, transformer size, billing cycle, how and when it was connected, when its rate schedule took effect, its current balance, any outstanding disconnect notice (date and amount demanded), the disconnect or seasonal idle date, medical certificate protection, cash-only status and the final read date. Every criterion is optional; supply whichever reference numbers you already hold (with none,
    every such record is returned). Returns all matching records, or a message that none was found.

    Args:
        service_account_id: The reference number of an electric service account (one metered location); leave "" if unknown.
        customer_id: The member's customer reference number (the member whose records these are); leave "" if unknown.
    """
    match = {k: v for k, v in {"service_account_id": service_account_id, "customer_id": customer_id}.items() if v}
    rows = ctx.find("service_accounts", **match)
    return _show(rows, "service accounts records", match)

@tool(owner="agent", rw="read")
def find_service_charges(ctx: ToolContext, charge_id: str = "", service_account_id: str = "", customer_id: str = "", source_reference_id: str = "") -> str:
    """Look up the lines billed on an electric service account: usage lines by billing period (facility, energy with kWh, demand with metered and billing kW, power cost adjustment, minimums, sales tax), late payment charges, service fees, charges billed on behalf of other programs, and bill credits with their reason and the record they come from. Every criterion is optional; supply whichever reference numbers you already hold (with none,
    every such record is returned). Returns all matching records, or a message that none was found.

    Args:
        charge_id: The reference number of one bill line, fee, program charge or bill credit; leave "" if unknown.
        service_account_id: The reference number of an electric service account (one metered location); leave "" if unknown.
        customer_id: The member's customer reference number (the member whose records these are); leave "" if unknown.
        source_reference_id: The reference number of the record a line, entry or credit comes from (for example a returned payment, trouble report, deposit entry, capital credit entry, prepay account, arrangement, light rental, or a connecting service account); leave "" if unknown.
    """
    match = {k: v for k, v in {"charge_id": charge_id, "service_account_id": service_account_id, "customer_id": customer_id, "source_reference_id": source_reference_id}.items() if v}
    rows = ctx.find("service_charges", **match)
    return _show(rows, "service charges records", match)

@tool(owner="agent", rw="read")
def find_service_payments(ctx: ToolContext, payment_id: str = "", service_account_id: str = "", customer_id: str = "", original_payment_id: str = "") -> str:
    """Look up payments posted to an electric service account with their date, channel, amount and confirmation number, returned payments with the bank's reason and the payment they reverse, and energy assistance pledges with the agency, amount and pledge number. Every criterion is optional; supply whichever reference numbers you already hold (with none,
    every such record is returned). Returns all matching records, or a message that none was found.

    Args:
        payment_id: The reference number of one payment, returned payment or energy assistance pledge; leave "" if unknown.
        service_account_id: The reference number of an electric service account (one metered location); leave "" if unknown.
        customer_id: The member's customer reference number (the member whose records these are); leave "" if unknown.
        original_payment_id: The reference number of the payment that a returned payment reverses; leave "" if unknown.
    """
    match = {k: v for k, v in {"payment_id": payment_id, "service_account_id": service_account_id, "customer_id": customer_id, "original_payment_id": original_payment_id}.items() if v}
    rows = ctx.find("service_payments", **match)
    return _show(rows, "service payments records", match)

@tool(owner="agent", rw="read")
def find_service_trouble_reports(ctx: ToolContext, trouble_report_id: str = "", service_account_id: str = "", customer_id: str = "", original_report_id: str = "") -> str:
    """Look up outage and trouble reports for a service location (date, time, channel, what was reported and the outage incident number), the crew's findings (cause, dispatch period and completion date), and member-requested meter tests with their results. Every criterion is optional; supply whichever reference numbers you already hold (with none,
    every such record is returned). Returns all matching records, or a message that none was found.

    Args:
        trouble_report_id: The reference number of one outage or trouble report, crew finding or meter test; leave "" if unknown.
        service_account_id: The reference number of an electric service account (one metered location); leave "" if unknown.
        customer_id: The member's customer reference number (the member whose records these are); leave "" if unknown.
        original_report_id: The reference number of the outage report that a crew finding resolves; leave "" if unknown.
    """
    match = {k: v for k, v in {"trouble_report_id": trouble_report_id, "service_account_id": service_account_id, "customer_id": customer_id, "original_report_id": original_report_id}.items() if v}
    rows = ctx.find("service_trouble_reports", **match)
    return _show(rows, "service trouble reports records", match)

@tool(owner="agent", rw="read")
def find_service_certificates(ctx: ToolContext, certificate_id: str = "", service_account_id: str = "", customer_id: str = "") -> str:
    """Look up medical certificates received for an electric service account, with the date received, the certifying practitioner and the last day of protection. Every criterion is optional; supply whichever reference numbers you already hold (with none,
    every such record is returned). Returns all matching records, or a message that none was found.

    Args:
        certificate_id: The reference number of one medical certificate record; leave "" if unknown.
        service_account_id: The reference number of an electric service account (one metered location); leave "" if unknown.
        customer_id: The member's customer reference number (the member whose records these are); leave "" if unknown.
    """
    match = {k: v for k, v in {"certificate_id": certificate_id, "service_account_id": service_account_id, "customer_id": customer_id}.items() if v}
    rows = ctx.find("service_certificates", **match)
    return _show(rows, "service certificates records", match)

@tool(owner="agent", rw="read")
def find_service_orders(ctx: ToolContext, service_order_id: str = "", customer_id: str = "", service_account_id: str = "") -> str:
    """Look up a member's service orders - stop service, seasonal idle, seasonal restore and rate schedule change requests - with the requested date and where each order stands. Every criterion is optional; supply whichever reference numbers you already hold (with none,
    every such record is returned). Returns all matching records, or a message that none was found.

    Args:
        service_order_id: The reference number of one member service order (stop service, seasonal idle or restore, rate change); leave "" if unknown.
        customer_id: The member's customer reference number (the member whose records these are); leave "" if unknown.
        service_account_id: The reference number of an electric service account (one metered location); leave "" if unknown.
    """
    match = {k: v for k, v in {"service_order_id": service_order_id, "customer_id": customer_id, "service_account_id": service_account_id}.items() if v}
    rows = ctx.find("service_orders", **match)
    return _show(rows, "service orders records", match)

@tool(owner="agent", rw="read")
def find_prepay_accounts(ctx: ToolContext, prepay_account_id: str = "", customer_id: str = "", service_account_id: str = "") -> str:
    """Look up PrePay Power enrollments: the tier, status, enrollment, activation and end dates, the current prepaid balance, the transferred arrears still being recovered, the low-balance alert amount and channel, and any current low-balance disconnection. Every criterion is optional; supply whichever reference numbers you already hold (with none,
    every such record is returned). Returns all matching records, or a message that none was found.

    Args:
        prepay_account_id: The reference number of a PrePay Power enrollment; leave "" if unknown.
        customer_id: The member's customer reference number (the member whose records these are); leave "" if unknown.
        service_account_id: The reference number of an electric service account (one metered location); leave "" if unknown.
    """
    match = {k: v for k, v in {"prepay_account_id": prepay_account_id, "customer_id": customer_id, "service_account_id": service_account_id}.items() if v}
    rows = ctx.find("prepay_accounts", **match)
    return _show(rows, "prepay accounts records", match)

@tool(owner="agent", rw="read")
def find_prepay_ledger(ctx: ToolContext, ledger_entry_id: str = "", prepay_account_id: str = "", customer_id: str = "", source_reference_id: str = "") -> str:
    """Look up the PrePay Power ledger of an enrollment: daily charges by service day and component, payments with the portion credited to the balance and any recovery portion, arrears transfers and recoveries, deposit credits, corrections, refunds and arrears returned to standard billing. Every criterion is optional; supply whichever reference numbers you already hold (with none,
    every such record is returned). Returns all matching records, or a message that none was found.

    Args:
        ledger_entry_id: The reference number of one PrePay Power ledger entry; leave "" if unknown.
        prepay_account_id: The reference number of a PrePay Power enrollment; leave "" if unknown.
        customer_id: The member's customer reference number (the member whose records these are); leave "" if unknown.
        source_reference_id: The reference number of the record a line, entry or credit comes from (for example a returned payment, trouble report, deposit entry, capital credit entry, prepay account, arrangement, light rental, or a connecting service account); leave "" if unknown.
    """
    match = {k: v for k, v in {"ledger_entry_id": ledger_entry_id, "prepay_account_id": prepay_account_id, "customer_id": customer_id, "source_reference_id": source_reference_id}.items() if v}
    rows = ctx.find("prepay_ledger", **match)
    return _show(rows, "prepay ledger records", match)

@tool(owner="agent", rw="read")
def find_prepay_notifications(ctx: ToolContext, notification_id: str = "", prepay_account_id: str = "", customer_id: str = "") -> str:
    """Look up the PrePay Power notifications sent for an enrollment - low balance, disconnect warning, disconnected, reconnected, weather hold and counseling referral - with when each was sent, the balance at that moment and the channel used. Every criterion is optional; supply whichever reference numbers you already hold (with none,
    every such record is returned). Returns all matching records, or a message that none was found.

    Args:
        notification_id: The reference number of one PrePay Power notification; leave "" if unknown.
        prepay_account_id: The reference number of a PrePay Power enrollment; leave "" if unknown.
        customer_id: The member's customer reference number (the member whose records these are); leave "" if unknown.
    """
    match = {k: v for k, v in {"notification_id": notification_id, "prepay_account_id": prepay_account_id, "customer_id": customer_id}.items() if v}
    rows = ctx.find("prepay_notifications", **match)
    return _show(rows, "prepay notifications records", match)

@tool(owner="agent", rw="read")
def find_prepay_requests(ctx: ToolContext, prepay_request_id: str = "", customer_id: str = "", prepay_account_id: str = "", service_account_id: str = "") -> str:
    """Look up a member's PrePay Power agreement signatures and requests to return to standard billing, with where each stands. Every criterion is optional; supply whichever reference numbers you already hold (with none,
    every such record is returned). Returns all matching records, or a message that none was found.

    Args:
        prepay_request_id: The reference number of one PrePay Power agreement or exit request; leave "" if unknown.
        customer_id: The member's customer reference number (the member whose records these are); leave "" if unknown.
        prepay_account_id: The reference number of a PrePay Power enrollment; leave "" if unknown.
        service_account_id: The reference number of an electric service account (one metered location); leave "" if unknown.
    """
    match = {k: v for k, v in {"prepay_request_id": prepay_request_id, "customer_id": customer_id, "prepay_account_id": prepay_account_id, "service_account_id": service_account_id}.items() if v}
    rows = ctx.find("prepay_requests", **match)
    return _show(rows, "prepay requests records", match)

@tool(owner="agent", rw="read")
def find_deposit_accounts(ctx: ToolContext, deposit_account_id: str = "", customer_id: str = "", service_account_id: str = "") -> str:
    """Look up security deposit records: the deposit tier, why it was assessed, the assessment date, the amount required and the number of installments, the cash held and interest accrued, the date it was paid in full, any waiver and its evidence, and the date the record was closed. Every criterion is optional; supply whichever reference numbers you already hold (with none,
    every such record is returned). Returns all matching records, or a message that none was found.

    Args:
        deposit_account_id: The reference number of a security deposit record; leave "" if unknown.
        customer_id: The member's customer reference number (the member whose records these are); leave "" if unknown.
        service_account_id: The reference number of an electric service account (one metered location); leave "" if unknown.
    """
    match = {k: v for k, v in {"deposit_account_id": deposit_account_id, "customer_id": customer_id, "service_account_id": service_account_id}.items() if v}
    rows = ctx.find("deposit_accounts", **match)
    return _show(rows, "deposit accounts records", match)

@tool(owner="agent", rw="read")
def find_deposit_ledger(ctx: ToolContext, deposit_entry_id: str = "", deposit_account_id: str = "", customer_id: str = "") -> str:
    """Look up the ledger of a security deposit: deposit payments and installments, interest accruals with their period, rate and days, interest payouts, refunds, and applications to a bill or to a PrePay Power balance. Every criterion is optional; supply whichever reference numbers you already hold (with none,
    every such record is returned). Returns all matching records, or a message that none was found.

    Args:
        deposit_entry_id: The reference number of one security deposit ledger entry; leave "" if unknown.
        deposit_account_id: The reference number of a security deposit record; leave "" if unknown.
        customer_id: The member's customer reference number (the member whose records these are); leave "" if unknown.
    """
    match = {k: v for k, v in {"deposit_entry_id": deposit_entry_id, "deposit_account_id": deposit_account_id, "customer_id": customer_id}.items() if v}
    rows = ctx.find("deposit_ledger", **match)
    return _show(rows, "deposit ledger records", match)

@tool(owner="agent", rw="read")
def find_arrangements(ctx: ToolContext, arrangement_id: str = "", customer_id: str = "", service_account_id: str = "") -> str:
    """Look up payment arrangements: the agreement tier and status, the offer, acceptance and end dates and how the member accepted, the past-due amount, down payment, arranged amount, installment count and amount, first installment period, the balance not yet billed back, and why an agreement was terminated. Every criterion is optional; supply whichever reference numbers you already hold (with none,
    every such record is returned). Returns all matching records, or a message that none was found.

    Args:
        arrangement_id: The reference number of a payment arrangement; leave "" if unknown.
        customer_id: The member's customer reference number (the member whose records these are); leave "" if unknown.
        service_account_id: The reference number of an electric service account (one metered location); leave "" if unknown.
    """
    match = {k: v for k, v in {"arrangement_id": arrangement_id, "customer_id": customer_id, "service_account_id": service_account_id}.items() if v}
    rows = ctx.find("arrangements", **match)
    return _show(rows, "arrangements records", match)

@tool(owner="agent", rw="read")
def find_arrange_ledger(ctx: ToolContext, arrange_entry_id: str = "", arrangement_id: str = "", customer_id: str = "") -> str:
    """Look up the ledger of a payment arrangement: the balance moved into it, each installment billed or missed with its billing period and number, and any balance billed back with the reason. Every criterion is optional; supply whichever reference numbers you already hold (with none,
    every such record is returned). Returns all matching records, or a message that none was found.

    Args:
        arrange_entry_id: The reference number of one payment arrangement ledger entry; leave "" if unknown.
        arrangement_id: The reference number of a payment arrangement; leave "" if unknown.
        customer_id: The member's customer reference number (the member whose records these are); leave "" if unknown.
    """
    match = {k: v for k, v in {"arrange_entry_id": arrange_entry_id, "arrangement_id": arrangement_id, "customer_id": customer_id}.items() if v}
    rows = ctx.find("arrange_ledger", **match)
    return _show(rows, "arrange ledger records", match)

@tool(owner="agent", rw="read")
def find_capital_accounts(ctx: ToolContext, capital_account_id: str = "", customer_id: str = "") -> str:
    """Look up a member's capital credit accounts, one per patron class: status, opening, inactive, estate application and closing dates, the allocated credits not yet retired, the retired credits still owed, and any donation election. Every criterion is optional; supply whichever reference numbers you already hold (with none,
    every such record is returned). Returns all matching records, or a message that none was found.

    Args:
        capital_account_id: The reference number of a capital credit account (one member in one patron class); leave "" if unknown.
        customer_id: The member's customer reference number (the member whose records these are); leave "" if unknown.
    """
    match = {k: v for k, v in {"capital_account_id": capital_account_id, "customer_id": customer_id}.items() if v}
    rows = ctx.find("capital_accounts", **match)
    return _show(rows, "capital accounts records", match)

@tool(owner="agent", rw="read")
def find_capital_ledger(ctx: ToolContext, capital_entry_id: str = "", capital_account_id: str = "", customer_id: str = "", capital_request_id: str = "", service_account_id: str = "", original_entry_id: str = "") -> str:
    """Look up the capital credit ledger of an account: allocations by patronage year and source with the revenue they are based on, general and special retirements, amounts made payable with any discount, payouts by bill credit, check, offset or donation, voided checks and escheats. Every criterion is optional; supply whichever reference numbers you already hold (with none,
    every such record is returned). Returns all matching records, or a message that none was found.

    Args:
        capital_entry_id: The reference number of one capital credit ledger entry; leave "" if unknown.
        capital_account_id: The reference number of a capital credit account (one member in one patron class); leave "" if unknown.
        customer_id: The member's customer reference number (the member whose records these are); leave "" if unknown.
        capital_request_id: The reference number of one capital credit request (estate retirement, discounted early retirement or check reissue); leave "" if unknown.
        service_account_id: The reference number of an electric service account (one metered location); leave "" if unknown.
        original_entry_id: The reference number of the capital credit check payout that a void, reissue or escheat refers to; leave "" if unknown.
    """
    match = {k: v for k, v in {"capital_entry_id": capital_entry_id, "capital_account_id": capital_account_id, "customer_id": customer_id, "capital_request_id": capital_request_id, "service_account_id": service_account_id, "original_entry_id": original_entry_id}.items() if v}
    rows = ctx.find("capital_ledger", **match)
    return _show(rows, "capital ledger records", match)

@tool(owner="agent", rw="read")
def find_capital_requests(ctx: ToolContext, capital_request_id: str = "", customer_id: str = "", capital_account_id: str = "", original_entry_id: str = "") -> str:
    """Look up capital credit requests - estate retirements, discounted early retirements and check reissues - with the claimant, the documents on file, where each request stands and any board approval date. Every criterion is optional; supply whichever reference numbers you already hold (with none,
    every such record is returned). Returns all matching records, or a message that none was found.

    Args:
        capital_request_id: The reference number of one capital credit request (estate retirement, discounted early retirement or check reissue); leave "" if unknown.
        customer_id: The member's customer reference number (the member whose records these are); leave "" if unknown.
        capital_account_id: The reference number of a capital credit account (one member in one patron class); leave "" if unknown.
        original_entry_id: The reference number of the capital credit check payout that a void, reissue or escheat refers to; leave "" if unknown.
    """
    match = {k: v for k, v in {"capital_request_id": capital_request_id, "customer_id": customer_id, "capital_account_id": capital_account_id, "original_entry_id": original_entry_id}.items() if v}
    rows = ctx.find("capital_requests", **match)
    return _show(rows, "capital requests records", match)

@tool(owner="agent", rw="read")
def find_budget_plans(ctx: ToolContext, budget_plan_id: str = "", customer_id: str = "", service_account_id: str = "") -> str:
    """Look up Budget Billing plans: the plan tier and status, enrollment and first budget period, anniversary month, current installment, latest recalculation, the deferred balance, and exit or end dates. Every criterion is optional; supply whichever reference numbers you already hold (with none,
    every such record is returned). Returns all matching records, or a message that none was found.

    Args:
        budget_plan_id: The reference number of a Budget Billing plan; leave "" if unknown.
        customer_id: The member's customer reference number (the member whose records these are); leave "" if unknown.
        service_account_id: The reference number of an electric service account (one metered location); leave "" if unknown.
    """
    match = {k: v for k, v in {"budget_plan_id": budget_plan_id, "customer_id": customer_id, "service_account_id": service_account_id}.items() if v}
    rows = ctx.find("budget_plans", **match)
    return _show(rows, "budget plans records", match)

@tool(owner="agent", rw="read")
def find_budget_ledger(ctx: ToolContext, budget_entry_id: str = "", budget_plan_id: str = "", customer_id: str = "") -> str:
    """Look up the ledger of a Budget Billing plan: the installment billed each period alongside the actual charges, the variances deferred, installments missed, and settle-ups with their reason and handling. Every criterion is optional; supply whichever reference numbers you already hold (with none,
    every such record is returned). Returns all matching records, or a message that none was found.

    Args:
        budget_entry_id: The reference number of one Budget Billing ledger entry; leave "" if unknown.
        budget_plan_id: The reference number of a Budget Billing plan; leave "" if unknown.
        customer_id: The member's customer reference number (the member whose records these are); leave "" if unknown.
    """
    match = {k: v for k, v in {"budget_entry_id": budget_entry_id, "budget_plan_id": budget_plan_id, "customer_id": customer_id}.items() if v}
    rows = ctx.find("budget_ledger", **match)
    return _show(rows, "budget ledger records", match)

@tool(owner="agent", rw="read")
def find_budget_requests(ctx: ToolContext, budget_request_id: str = "", customer_id: str = "", service_account_id: str = "", budget_plan_id: str = "") -> str:
    """Look up a member's Budget Billing enrollment, exit and tier-switch requests, with where each stands. Every criterion is optional; supply whichever reference numbers you already hold (with none,
    every such record is returned). Returns all matching records, or a message that none was found.

    Args:
        budget_request_id: The reference number of one Budget Billing enrollment, exit or tier-switch request; leave "" if unknown.
        customer_id: The member's customer reference number (the member whose records these are); leave "" if unknown.
        service_account_id: The reference number of an electric service account (one metered location); leave "" if unknown.
        budget_plan_id: The reference number of a Budget Billing plan; leave "" if unknown.
    """
    match = {k: v for k, v in {"budget_request_id": budget_request_id, "customer_id": customer_id, "service_account_id": service_account_id, "budget_plan_id": budget_plan_id}.items() if v}
    rows = ctx.find("budget_requests", **match)
    return _show(rows, "budget requests records", match)

@tool(owner="agent", rw="read")
def find_light_rentals(ctx: ToolContext, light_rental_id: str = "", customer_id: str = "", service_account_id: str = "") -> str:
    """Look up area and security light rentals: the fixture, status, the service account it is billed on, request, installation, repair and removal dates, the fixture number, additional poles, contract term and mounting location. Every criterion is optional; supply whichever reference numbers you already hold (with none,
    every such record is returned). Returns all matching records, or a message that none was found.

    Args:
        light_rental_id: The reference number of an area or security light rental; leave "" if unknown.
        customer_id: The member's customer reference number (the member whose records these are); leave "" if unknown.
        service_account_id: The reference number of an electric service account (one metered location); leave "" if unknown.
    """
    match = {k: v for k, v in {"light_rental_id": light_rental_id, "customer_id": customer_id, "service_account_id": service_account_id}.items() if v}
    rows = ctx.find("light_rentals", **match)
    return _show(rows, "light rentals records", match)

@tool(owner="agent", rw="read")
def find_light_events(ctx: ToolContext, light_event_id: str = "", light_rental_id: str = "", customer_id: str = "", report_event_id: str = "") -> str:
    """Look up the history of a rental light: monthly rentals billed, one-time charges with type and quantity, light-out reports, and outage credits with the days credited. Every criterion is optional; supply whichever reference numbers you already hold (with none,
    every such record is returned). Returns all matching records, or a message that none was found.

    Args:
        light_event_id: The reference number of one area light rental, charge, report or credit entry; leave "" if unknown.
        light_rental_id: The reference number of an area or security light rental; leave "" if unknown.
        customer_id: The member's customer reference number (the member whose records these are); leave "" if unknown.
        report_event_id: The reference number of the light report an outage credit is for; leave "" if unknown.
    """
    match = {k: v for k, v in {"light_event_id": light_event_id, "light_rental_id": light_rental_id, "customer_id": customer_id, "report_event_id": report_event_id}.items() if v}
    rows = ctx.find("light_events", **match)
    return _show(rows, "light events records", match)

@tool(owner="agent", rw="read")
def find_line_projects(ctx: ToolContext, line_project_id: str = "", customer_id: str = "", service_account_id: str = "") -> str:
    """Look up line extension and new service construction projects: the tier and status, the location, the pending service account, the estimate (footage, phase, transformer, cost, allowance and contribution), the signing, scheduling and energize dates, whether easements are on file, the amount still owed and any refundable advance remaining. Every criterion is optional; supply whichever reference numbers you already hold (with none,
    every such record is returned). Returns all matching records, or a message that none was found.

    Args:
        line_project_id: The reference number of a line extension or new service construction project; leave "" if unknown.
        customer_id: The member's customer reference number (the member whose records these are); leave "" if unknown.
        service_account_id: The reference number of an electric service account (one metered location); leave "" if unknown.
    """
    match = {k: v for k, v in {"line_project_id": line_project_id, "customer_id": customer_id, "service_account_id": service_account_id}.items() if v}
    rows = ctx.find("line_projects", **match)
    return _show(rows, "line projects records", match)

@tool(owner="agent", rw="read")
def find_line_ledger(ctx: ToolContext, line_entry_id: str = "", line_project_id: str = "", customer_id: str = "", source_reference_id: str = "") -> str:
    """Look up the ledger of a construction project: fees, the contribution billed and its type, advances recorded, the design fee credited, payments, write-offs, and advance refunds or forfeitures. Every criterion is optional; supply whichever reference numbers you already hold (with none,
    every such record is returned). Returns all matching records, or a message that none was found.

    Args:
        line_entry_id: The reference number of one construction project ledger entry; leave "" if unknown.
        line_project_id: The reference number of a line extension or new service construction project; leave "" if unknown.
        customer_id: The member's customer reference number (the member whose records these are); leave "" if unknown.
        source_reference_id: The reference number of the record a line, entry or credit comes from (for example a returned payment, trouble report, deposit entry, capital credit entry, prepay account, arrangement, light rental, or a connecting service account); leave "" if unknown.
    """
    match = {k: v for k, v in {"line_entry_id": line_entry_id, "line_project_id": line_project_id, "customer_id": customer_id, "source_reference_id": source_reference_id}.items() if v}
    rows = ctx.find("line_ledger", **match)
    return _show(rows, "line ledger records", match)

@tool(owner="agent", rw="write")
def verify_member_identity(ctx: ToolContext, customer_id: str, member_number: str = "", phone_number: str = "",
                           email: str = "", tax_id_last4: str = "", membership_date: str = "") -> str:
    """Verify that the caller is the member, or is authorized on the membership, and record the outcome.
    Identity must be verified before any account information is discussed or any change is made. This tool
    makes the comparison itself: it checks each piece of identifying information the caller states against
    the member profile and passes only when at least two of them match. The customer reference number only
    tells the tool which profile to compare against and never counts as a match. Callers usually know only
    some of these details, so pass exactly what the caller said, unchanged, and leave the rest blank. If a
    first attempt fails and the caller then gives more details that pass, the pass is what stays on record.

    Args:
        customer_id: The customer reference number of the profile being verified, taken from the member profile lookup. Required.
        member_number: The seven-digit membership number the caller states, leading zeros included; leave "" if not stated.
        phone_number: The phone number on file as the caller states it, ten digits with no punctuation; leave "" if not stated.
        email: The email address on file as the caller states it; leave "" if not stated.
        tax_id_last4: The last four digits of the Social Security number (or, for an organization, of its Employer Identification Number) as the caller states them; leave "" if not stated.
        membership_date: The date the membership began as the caller states it, YYYY-MM-DD; leave "" if not stated.
    """
    if not customer_id:
        return "Error: customer_id is required; find the member profile first and pass its reference number."
    rows = ctx.find("customers", customer_id=customer_id)
    if not rows:
        return f"Error: no member profile {customer_id}; cannot verify."
    rec = rows[0]
    supplied = {"member_number": member_number, "phone_number": phone_number, "email": email,
                "tax_id_last4": tax_id_last4, "membership_date": membership_date}
    matched = sum(1 for field, value in supplied.items()
                  if value and str(rec.get(field) or "").strip().lower() == str(value).strip().lower())
    verified = matched >= VERIFICATION_MATCHES_REQUIRED
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
    return (f"Identity NOT verified for {customer_id}: only {matched} of the {VERIFICATION_MATCHES_REQUIRED} "
            "required details matched. Ask the caller for another detail on file and try again.")


@tool(owner="agent", rw="write")
def transfer_to_member_services_rep(ctx: ToolContext, customer_id: str, reason: str) -> str:
    """Transfer the call to a human member services representative and record the transfer with its reason.
    Use it in exactly two situations: when no published Cedar Fork policy can resolve what the member is
    asking for, or when the member has explicitly asked to speak with a person at least two times during
    the call.

    Args:
        customer_id: The customer reference number of the member, taken from the member profile lookup.
        reason: Why the call is transferred; exactly one of POLICY_NOT_COVERED (no published policy can resolve the request) or CUSTOMER_REQUESTED (the member explicitly asked for a person at least two times). Never free text.
    """
    allowed = {"POLICY_NOT_COVERED", "CUSTOMER_REQUESTED"}
    if reason not in allowed:
        return f"Error: unknown transfer reason '{reason}'. Valid: {', '.join(sorted(allowed))}."
    if not ctx.find("customers", customer_id=customer_id):
        return f"Error: no member profile {customer_id}; cannot record the transfer."
    rid = ctx.make_id("hof_", customer_id, reason)
    ctx.create("handoffs", rid, handoff_id=rid, customer_id=customer_id, reason=reason, created_at=ctx.now())
    return f"Transfer to a member services representative recorded for {customer_id} ({reason})."

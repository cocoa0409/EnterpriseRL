"""Shared tools for env_0050_debt_collection_agency (Ridgeline Recovery Associates).

Always-visible share tools reused by every difficulty: one record finder per table of the
scenario (the customers finder doubles as the identity entry), the identity-verification write
(threshold K = 2 matching credentials) and the transfer-to-human write (repeat-request
threshold R = 2). Customer-originated writes live in each difficulty's task_tools.py.
"""

from erlbench import ToolContext, tool


def _report(rows: list, label: str, match: dict) -> str:
    # Shared formatting of every finder's answer (hit: the records; miss: a not-found message).
    return str(rows) if rows else f"No {label} found for {match or 'the criteria given'}."


# ---------------------------------------------------------------- identity entry
@tool(owner="agent", rw="read")
def find_customers(ctx: ToolContext, customer_id: str = "", phone_number: str = "",
                   email: str = "", name: str = "") -> str:
    """Look up a customer profile at Ridgeline Recovery Associates to establish whose account a call
    is about. Profiles exist both for consumers who owe placed debts and for creditor clients that
    place debts with Ridgeline. Search by the customer reference number, or by what the caller can
    naturally state: the telephone number on file, the email address on file or the full name.
    Every criterion is optional; give whichever are known. A match returns the whole profile —
    whether it is a consumer or a creditor client, name, telephone, email, date of birth and last
    four digits of the Social Security number (consumers), last four digits of the Employer
    Identification Number (creditor clients), mailing address, ZIP code and the date the profile was
    opened. Finding a profile does not verify the caller's identity.

    Args:
        customer_id: The customer reference number, if the caller or a record already gave it; leave "" if unknown.
        phone_number: The telephone number the caller gives, 10 digits; leave "" if not provided.
        email: The email address the caller gives; leave "" if not provided.
        name: The caller's full name, or the creditor client's business name; leave "" if not provided.
    """
    match = {k: v for k, v in {"customer_id": customer_id, "phone_number": phone_number,
                               "email": email, "name": name}.items() if v}
    if not match:
        return "Error: provide at least one reference number or profile detail to find the customer."
    rows = ctx.fuzzy_find("customers", **match)
    if not rows:
        return f"No customer matches {match}."
    if len(rows) > 1:
        return (f"Error: {len(rows)} customers match {match}; ask the caller for one more detail "
                "on file to tell them apart.")
    return str(rows[0])


# ---------------------------------------------------------------- consumer accounts
@tool(owner="agent", rw="read")
def find_placed_accounts(ctx: ToolContext, account_id: str = "", customer_id: str = "",
                         agreement_id: str = "") -> str:
    """Look up placed consumer accounts — the debts creditor clients have placed with Ridgeline for
    collection. Each account shows the consumer, the placing agreement, the placement stage, the
    status, the debt type, the original creditor and the client's account number, the placement,
    first-delinquency, charge-off and itemization dates, the placed balance and the balance due,
    prior agency placements, the statute-of-limitations date, the placement term end and
    extensions, the validation notice and validation period dates, and any closing date and reason.
    Every criterion is optional; give whichever reference numbers are known. Returns every matching
    account, or a not-found message.

    Args:
        account_id: The Ridgeline account reference of the placed account; leave "" if unknown.
        customer_id: The customer reference of the consumer who owes the debt; leave "" if unknown.
        agreement_id: The reference of the client placement agreement the debt was placed under; leave "" if unknown.
    """
    match = {k: v for k, v in {"account_id": account_id, "customer_id": customer_id, "agreement_id": agreement_id}.items() if v}
    rows = ctx.find("placed_accounts", **match)
    return _report(rows, "placed accounts", match)


@tool(owner="agent", rw="read")
def find_account_transactions(ctx: ToolContext, txn_id: str = "", account_id: str = "",
                              customer_id: str = "", agreement_id: str = "", source_txn_id: str = "",
                              plan_id: str = "", settlement_id: str = "") -> str:
    """Look up the money history of placed accounts: the placed balance, client supplemental
    additions, consumer payments, payments the consumer made directly to the client, returned
    payments, client credits, settlement waivers and overpayment refunds. Each entry shows its type,
    amount, date, payment channel and confirmation number, the payment it points back to for a
    return or refund, the reason for an addition, credit or return, the client's reference, and the
    plan or settlement a payment was made under. Every criterion is optional. Returns every matching
    entry, or a not-found message.

    Args:
        txn_id: The reference of one account money entry; leave "" if unknown.
        account_id: The Ridgeline account reference; leave "" if unknown.
        customer_id: The customer reference of the consumer; leave "" if unknown.
        agreement_id: The reference of the placing client agreement; leave "" if unknown.
        source_txn_id: The reference of the original payment a return or refund points back to; leave "" if unknown.
        plan_id: The reference of the payment plan a payment was made under; leave "" if unknown.
        settlement_id: The reference of the settlement a payment or waiver belongs to; leave "" if unknown.
    """
    match = {k: v for k, v in {"txn_id": txn_id, "account_id": account_id, "customer_id": customer_id,
                    "agreement_id": agreement_id, "source_txn_id": source_txn_id,
                    "plan_id": plan_id, "settlement_id": settlement_id}.items() if v}
    rows = ctx.find("account_transactions", **match)
    return _report(rows, "account money entries", match)


@tool(owner="agent", rw="read")
def find_account_case_events(ctx: ToolContext, case_event_id: str = "", account_id: str = "",
                             customer_id: str = "", related_case_event_id: str = "") -> str:
    """Look up the case history of placed accounts: validation information requests, disputes,
    verification mailings, credit bureau tradeline actions, contact restrictions, bankruptcy and
    deceased notices, and paid-in-full, settled-in-full and statement letters. Each entry shows its
    type, date and channel, and where relevant the dispute reason, the caller's reference number, the
    request a verification answers, the verification package, the tradeline action and reporting
    month, the restriction or notice type, and the letter type. Every criterion is optional. Returns
    every matching entry, or a not-found message.

    Args:
        case_event_id: The reference of one case entry; leave "" if unknown.
        account_id: The Ridgeline account reference; leave "" if unknown.
        customer_id: The customer reference of the consumer; leave "" if unknown.
        related_case_event_id: The reference of the dispute or request that a verification mailing answers; leave "" if unknown.
    """
    match = {k: v for k, v in {"case_event_id": case_event_id, "account_id": account_id,
                    "customer_id": customer_id, "related_case_event_id": related_case_event_id}.items() if v}
    rows = ctx.find("account_case_events", **match)
    return _report(rows, "account case entries", match)


# ---------------------------------------------------------------- payment arrangements
@tool(owner="agent", rw="read")
def find_payment_plans(ctx: ToolContext, plan_id: str = "", customer_id: str = "",
                       account_id: str = "") -> str:
    """Look up payment arrangements consumers have set up on placed accounts. Each arrangement
    shows its type and status, the creation and authorization dates and how it was authorized, the
    frequency, installment amount and count, any down payment, the schedule anchor and final due
    date, the payment method, the plan total and the amount still scheduled, any stated income from
    a budget review, suspension and break dates, reinstatements, and any closing date and reason.
    Every criterion is optional. Returns every matching arrangement, or a not-found message.

    Args:
        plan_id: The payment plan reference; leave "" if unknown.
        customer_id: The customer reference of the consumer; leave "" if unknown.
        account_id: The Ridgeline account reference the plan pays; leave "" if unknown.
    """
    match = {k: v for k, v in {"plan_id": plan_id, "customer_id": customer_id, "account_id": account_id}.items() if v}
    rows = ctx.find("payment_plans", **match)
    return _report(rows, "payment plans", match)


@tool(owner="agent", rw="read")
def find_plan_installments(ctx: ToolContext, plan_txn_id: str = "", plan_id: str = "",
                           customer_id: str = "", account_id: str = "",
                           source_plan_txn_id: str = "") -> str:
    """Look up the installment history of payment plans: the plan total booked, installments paid
    and returned, missed installments, released remainders, and recorded due-date changes,
    restructures, deferrals and payment-method changes. Each entry shows its type, installment
    number, due date, amount, date, channel and confirmation, the payment a return reverses, and the
    kind of change. Every criterion is optional. Returns every matching entry, or a not-found
    message.

    Args:
        plan_txn_id: The reference of one plan entry; leave "" if unknown.
        plan_id: The payment plan reference; leave "" if unknown.
        customer_id: The customer reference of the consumer; leave "" if unknown.
        account_id: The Ridgeline account reference; leave "" if unknown.
        source_plan_txn_id: The reference of the installment payment a return reverses; leave "" if unknown.
    """
    match = {k: v for k, v in {"plan_txn_id": plan_txn_id, "plan_id": plan_id, "customer_id": customer_id,
                    "account_id": account_id, "source_plan_txn_id": source_plan_txn_id}.items() if v}
    rows = ctx.find("plan_installments", **match)
    return _report(rows, "plan entries", match)


# ---------------------------------------------------------------- settlements
@tool(owner="agent", rw="read")
def find_settlement_agreements(ctx: ToolContext, settlement_id: str = "", customer_id: str = "",
                               account_id: str = "", approval_request_id: str = "") -> str:
    """Look up settlement offers and agreements on placed accounts. Each settlement shows its
    programme and status, the offer and expiry dates, the balance at offer, the settlement
    percentage and amount, the number of payments and their spacing, the first and final payment
    due dates, whether the same-client bundle reduction was used, the client approval relied on,
    the acceptance date and method, extensions, the amount still to pay, and any closing date,
    waived amount or withdrawal reason. Every criterion is optional. Returns every matching
    settlement, or a not-found message.

    Args:
        settlement_id: The settlement reference; leave "" if unknown.
        customer_id: The customer reference of the consumer; leave "" if unknown.
        account_id: The Ridgeline account reference being settled; leave "" if unknown.
        approval_request_id: The reference of the client approval an offer relied on; leave "" if unknown.
    """
    match = {k: v for k, v in {"settlement_id": settlement_id, "customer_id": customer_id,
                    "account_id": account_id, "approval_request_id": approval_request_id}.items() if v}
    rows = ctx.find("settlement_agreements", **match)
    return _report(rows, "settlements", match)


@tool(owner="agent", rw="read")
def find_settlement_payments(ctx: ToolContext, settle_txn_id: str = "", settlement_id: str = "",
                             customer_id: str = "", account_id: str = "",
                             source_settle_txn_id: str = "") -> str:
    """Look up the payment and letter history of settlements: the settlement amount booked on
    acceptance, settlement payments received and returned, released remainders, and the offer
    letter, acceptance confirmation and default notice. Each entry shows its type, payment number,
    due date, amount, date, channel and confirmation, the payment a return reverses, the release
    reason, and for a letter its type, delivery channel, disclosure wording and tax notice. Every
    criterion is optional. Returns every matching entry, or a not-found message.

    Args:
        settle_txn_id: The reference of one settlement entry; leave "" if unknown.
        settlement_id: The settlement reference; leave "" if unknown.
        customer_id: The customer reference of the consumer; leave "" if unknown.
        account_id: The Ridgeline account reference; leave "" if unknown.
        source_settle_txn_id: The reference of the settlement payment a return reverses; leave "" if unknown.
    """
    match = {k: v for k, v in {"settle_txn_id": settle_txn_id, "settlement_id": settlement_id,
                    "customer_id": customer_id, "account_id": account_id,
                    "source_settle_txn_id": source_settle_txn_id}.items() if v}
    rows = ctx.find("settlement_payments", **match)
    return _report(rows, "settlement entries", match)


@tool(owner="agent", rw="read")
def find_settlement_approval_requests(ctx: ToolContext, approval_request_id: str = "",
                                      customer_id: str = "", account_id: str = "",
                                      agreement_id: str = "") -> str:
    """Look up requests Ridgeline sent to creditor clients for approval of settlements below its
    own authority. Each request shows the account, the placing agreement, the programme, the
    percentage and amount requested, the request date, the client's answer (pending, approved,
    declined or lapsed), the decision date and the lowest percentage approved. Every criterion is
    optional. Returns every matching request, or a not-found message.

    Args:
        approval_request_id: The approval request reference; leave "" if unknown.
        customer_id: The customer reference of the consumer whose account it concerns; leave "" if unknown.
        account_id: The Ridgeline account reference; leave "" if unknown.
        agreement_id: The reference of the placing client agreement; leave "" if unknown.
    """
    match = {k: v for k, v in {"approval_request_id": approval_request_id, "customer_id": customer_id,
                    "account_id": account_id, "agreement_id": agreement_id}.items() if v}
    rows = ctx.find("settlement_approval_requests", **match)
    return _report(rows, "settlement approval requests", match)


# ---------------------------------------------------------------- hardship holds
@tool(owner="agent", rw="read")
def find_hardship_holds(ctx: ToolContext, hold_id: str = "", customer_id: str = "",
                        account_id: str = "") -> str:
    """Look up hardship and protective hold requests on placed accounts. Each hold shows its tier
    and status, the request date and channel, the reference the consumer gave for the qualifying
    event, the documentation and decision dates, the start and end dates, extensions, and any
    ending date and reason or denial reason. Every criterion is optional. Returns every matching
    hold, or a not-found message.

    Args:
        hold_id: The hold reference; leave "" if unknown.
        customer_id: The customer reference of the consumer; leave "" if unknown.
        account_id: The Ridgeline account reference the hold covers; leave "" if unknown.
    """
    match = {k: v for k, v in {"hold_id": hold_id, "customer_id": customer_id, "account_id": account_id}.items() if v}
    rows = ctx.find("hardship_holds", **match)
    return _report(rows, "hardship holds", match)


@tool(owner="agent", rw="read")
def find_hardship_hold_events(ctx: ToolContext, hold_event_id: str = "", hold_id: str = "",
                              customer_id: str = "", account_id: str = "") -> str:
    """Look up the history of hardship holds: documentation requested and received, extensions
    granted, status reviews, the client's financial assistance decisions, client notifications, and
    decision letters and end-of-hold notices. Each entry shows its type and date and, where
    relevant, the documentation type and reference, due date, channel, extension number and days,
    review outcome, assistance outcome and notice type. Every criterion is optional. Returns every
    matching entry, or a not-found message.

    Args:
        hold_event_id: The reference of one hold history entry; leave "" if unknown.
        hold_id: The hold reference; leave "" if unknown.
        customer_id: The customer reference of the consumer; leave "" if unknown.
        account_id: The Ridgeline account reference; leave "" if unknown.
    """
    match = {k: v for k, v in {"hold_event_id": hold_event_id, "hold_id": hold_id,
                    "customer_id": customer_id, "account_id": account_id}.items() if v}
    rows = ctx.find("hardship_hold_events", **match)
    return _report(rows, "hold history entries", match)


# ---------------------------------------------------------------- creditor clients
@tool(owner="agent", rw="read")
def find_client_agreements(ctx: ToolContext, agreement_id: str = "", customer_id: str = "") -> str:
    """Look up contingency placement agreements held by creditor clients. Each agreement shows its
    contingency tier and status, the client's line of business, the issue, signing, effective and
    term-end dates, the remittance basis and frequency, whether credit reporting is authorized, the
    next tier review date, any placement hold, termination and runoff dates, and the collections
    held in trust and fees owed. Every criterion is optional. Returns every matching agreement, or
    a not-found message.

    Args:
        agreement_id: The placement agreement reference; leave "" if unknown.
        customer_id: The customer reference of the creditor client; leave "" if unknown.
    """
    match = {k: v for k, v in {"agreement_id": agreement_id, "customer_id": customer_id}.items() if v}
    rows = ctx.find("client_agreements", **match)
    return _report(rows, "placement agreements", match)


@tool(owner="agent", rw="read")
def find_client_ledger(ctx: ToolContext, client_txn_id: str = "", agreement_id: str = "",
                       customer_id: str = "", account_id: str = "", source_txn_id: str = "",
                       service_request_id: str = "") -> str:
    """Look up the money history of client placement agreements: collections booked with their
    contingency rate and fee, reversals, retained fees, remittances, direct-pay fees, fee invoices,
    recall fees, late charges, early-termination fees, fee payments and credits. Each entry shows
    its type, amount, date, the account and account entry it follows, the remittance period,
    statement, trace, invoice and payment references, and the reversal or credit reason. Every
    criterion is optional. Returns every matching entry, or a not-found message.

    Args:
        client_txn_id: The reference of one client money entry; leave "" if unknown.
        agreement_id: The placement agreement reference; leave "" if unknown.
        customer_id: The customer reference of the creditor client; leave "" if unknown.
        account_id: The Ridgeline account reference the entry concerns; leave "" if unknown.
        source_txn_id: The reference of the account money entry the client entry follows; leave "" if unknown.
        service_request_id: The reference of the client service request a recall fee follows; leave "" if unknown.
    """
    match = {k: v for k, v in {"client_txn_id": client_txn_id, "agreement_id": agreement_id,
                    "customer_id": customer_id, "account_id": account_id,
                    "source_txn_id": source_txn_id, "service_request_id": service_request_id}.items() if v}
    rows = ctx.find("client_ledger", **match)
    return _report(rows, "client money entries", match)


@tool(owner="agent", rw="read")
def find_client_service_requests(ctx: ToolContext, service_request_id: str = "", customer_id: str = "",
                                 agreement_id: str = "", account_id: str = "") -> str:
    """Look up service requests from creditor clients: account recalls, termination and
    non-renewal notices, placement pauses and resumptions, remittance terms changes and credit
    reporting authorization changes. Each request shows its type, the agreement and any account, the
    recall reason or requested change, the requested effective date, the request date, the
    processing status and the processing date. Every criterion is optional. Returns every matching
    request, or a not-found message.

    Args:
        service_request_id: The service request reference; leave "" if unknown.
        customer_id: The customer reference of the creditor client; leave "" if unknown.
        agreement_id: The placement agreement reference; leave "" if unknown.
        account_id: The Ridgeline account reference of a recalled account; leave "" if unknown.
    """
    match = {k: v for k, v in {"service_request_id": service_request_id, "customer_id": customer_id,
                    "agreement_id": agreement_id, "account_id": account_id}.items() if v}
    rows = ctx.find("client_service_requests", **match)
    return _report(rows, "client service requests", match)


@tool(owner="agent", rw="read")
def find_flatfee_programs(ctx: ToolContext, program_id: str = "", customer_id: str = "",
                          agreement_id: str = "") -> str:
    """Look up flat-fee pre-collect letter programs bought by creditor clients. Each program shows
    the pack and status, the purchase, payment and expiry dates, the unit price, the invoice, the
    units still usable, the contingency agreement used for conversions and any closing date. Every
    criterion is optional. Returns every matching program, or a not-found message.

    Args:
        program_id: The pre-collect program reference; leave "" if unknown.
        customer_id: The customer reference of the creditor client; leave "" if unknown.
        agreement_id: The reference of the contingency agreement linked for conversions; leave "" if unknown.
    """
    match = {k: v for k, v in {"program_id": program_id, "customer_id": customer_id, "agreement_id": agreement_id}.items() if v}
    rows = ctx.find("flatfee_programs", **match)
    return _report(rows, "pre-collect programs", match)


@tool(owner="agent", rw="read")
def find_flatfee_unit_ledger(ctx: ToolContext, unit_txn_id: str = "", program_id: str = "",
                             customer_id: str = "", source_program_id: str = "") -> str:
    """Look up the unit and debtor history of pre-collect programs: units bought, rolled in, used,
    credited and lapsed, debtor status reports and conversions to contingency collection. Each
    entry shows its type, units, amount, date, invoice, the program units were rolled from, the
    debtor's reference, name and balance, the submission channel, and the credit, lapse or debtor
    status. Every criterion is optional. Returns every matching entry, or a not-found message.

    Args:
        unit_txn_id: The reference of one program entry; leave "" if unknown.
        program_id: The pre-collect program reference; leave "" if unknown.
        customer_id: The customer reference of the creditor client; leave "" if unknown.
        source_program_id: The reference of the program units were rolled in from; leave "" if unknown.
    """
    match = {k: v for k, v in {"unit_txn_id": unit_txn_id, "program_id": program_id,
                    "customer_id": customer_id, "source_program_id": source_program_id}.items() if v}
    rows = ctx.find("flatfee_unit_ledger", **match)
    return _report(rows, "pre-collect program entries", match)


@tool(owner="agent", rw="read")
def find_legal_agreements(ctx: ToolContext, legal_agreement_id: str = "", customer_id: str = "",
                          agreement_id: str = "") -> str:
    """Look up legal forwarding agreements held by creditor clients. Each agreement shows the
    forwarding programme and status, the linked contingency agreement, the issue and signing dates,
    any suspension date and reason, termination notice and termination dates, the cost deposit held
    and the costs not yet reimbursed. Every criterion is optional. Returns every matching agreement,
    or a not-found message.

    Args:
        legal_agreement_id: The legal forwarding agreement reference; leave "" if unknown.
        customer_id: The customer reference of the creditor client; leave "" if unknown.
        agreement_id: The reference of the linked contingency placement agreement; leave "" if unknown.
    """
    match = {k: v for k, v in {"legal_agreement_id": legal_agreement_id, "customer_id": customer_id,
                    "agreement_id": agreement_id}.items() if v}
    rows = ctx.find("legal_agreements", **match)
    return _report(rows, "legal forwarding agreements", match)


@tool(owner="agent", rw="read")
def find_legal_matter_events(ctx: ToolContext, matter_event_id: str = "", legal_agreement_id: str = "",
                             customer_id: str = "", account_id: str = "") -> str:
    """Look up the history of forwarded legal matters and their costs: deposits received, applied
    and refunded, costs paid and reimbursed, suit authorizations, suits filed, judgments,
    enforcement steps and matter closures. Each entry shows its type, date, the account and the
    attorney's matter number, amount, cost type, deposit and authorization references, court case
    number and court, judgment amount and type, enforcement type and outcome. Every criterion is
    optional. Returns every matching entry, or a not-found message.

    Args:
        matter_event_id: The reference of one matter entry; leave "" if unknown.
        legal_agreement_id: The legal forwarding agreement reference; leave "" if unknown.
        customer_id: The customer reference of the creditor client; leave "" if unknown.
        account_id: The Ridgeline account reference in the matter; leave "" if unknown.
    """
    match = {k: v for k, v in {"matter_event_id": matter_event_id, "legal_agreement_id": legal_agreement_id,
                    "customer_id": customer_id, "account_id": account_id}.items() if v}
    rows = ctx.find("legal_matter_events", **match)
    return _report(rows, "legal matter entries", match)


# ---------------------------------------------------------------- service logs
@tool(owner="agent", rw="read")
def find_identity_verifications(ctx: ToolContext, verification_id: str = "", customer_id: str = "") -> str:
    """Look up the identity verification outcome recorded for a customer: whether the caller's
    identity has been verified and when it was last checked. Every criterion is optional. Returns
    the matching record, or a not-found message when no verification has been attempted.

    Args:
        verification_id: The verification record reference; leave "" if unknown.
        customer_id: The customer reference; leave "" if unknown.
    """
    match = {k: v for k, v in {"verification_id": verification_id, "customer_id": customer_id}.items() if v}
    rows = ctx.find("identity_verifications", **match)
    return _report(rows, "identity verification records", match)


@tool(owner="agent", rw="read")
def find_human_handoffs(ctx: ToolContext, handoff_id: str = "", customer_id: str = "") -> str:
    """Look up transfers of a customer to a human representative, with the reason and the time of
    each transfer. Every criterion is optional. Returns every matching transfer, or a not-found
    message.

    Args:
        handoff_id: The transfer record reference; leave "" if unknown.
        customer_id: The customer reference; leave "" if unknown.
    """
    match = {k: v for k, v in {"handoff_id": handoff_id, "customer_id": customer_id}.items() if v}
    rows = ctx.find("human_handoffs", **match)
    return _report(rows, "transfers to a human representative", match)


# ---------------------------------------------------------------- verification and handoff
@tool(owner="agent", rw="write")
def verify_customer_identity(ctx: ToolContext, customer_id: str, phone_number: str = "",
                             email: str = "", date_of_birth: str = "", ssn_last4: str = "",
                             postal_code: str = "", tax_id_last4: str = "") -> str:
    """Verify the caller's identity and record the outcome. Because a collection agency may discuss
    a debt only with the person who owes it or with an authorized representative of a client, no
    account information is disclosed and no business is transacted until this verification has
    passed. This tool performs the comparison itself: it compares each detail the caller states
    against the customer profile, counts how many match, and passes only when at least 2 match. The
    customer reference number only retrieves the profile and never counts as a match. Callers
    usually state only some details, so pass exactly the values the caller gave, as given, and leave
    the rest blank. The outcome is recorded; if a first attempt fails and a later attempt with more
    details passes, the pass stands.

    Args:
        customer_id: The customer reference number read from the customer profile lookup. Required; used only to retrieve the profile and not counted as a match.
        phone_number: The telephone number the caller states, 10 digits with no punctuation; leave "" if not stated.
        email: The email address the caller states; leave "" if not stated.
        date_of_birth: The consumer's date of birth as stated, YYYY-MM-DD; leave "" if not stated.
        ssn_last4: The last four digits of the consumer's Social Security number, 4 digits; leave "" if not stated.
        postal_code: The 5-digit ZIP code of the mailing address on file, as stated; leave "" if not stated.
        tax_id_last4: For a creditor client, the last four digits of its Employer Identification Number, 4 digits; leave "" if not stated.
    """
    if not customer_id:
        return "Error: customer_id is required; look the customer up first and pass their reference."
    rows = ctx.find("customers", customer_id=customer_id)
    if not rows:
        return f"Error: no customer {customer_id}; cannot verify."
    rec = rows[0]
    supplied = {"phone_number": phone_number, "email": email, "date_of_birth": date_of_birth,
                "ssn_last4": ssn_last4, "postal_code": postal_code, "tax_id_last4": tax_id_last4}
    matched = sum(1 for field, value in supplied.items()
                  if value and rec.get(field) and str(rec.get(field)) == str(value))
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
        return f"Identity verified for {customer_id} ({matched} detail(s) matched this attempt)."
    return (f"Identity NOT verified for {customer_id} (only {matched} of the required 2 details "
            "matched). Ask the caller for another detail on file and try again.")


@tool(owner="agent", rw="write")
def transfer_to_human_agent(ctx: ToolContext, customer_id: str, reason: str) -> str:
    """Transfer the customer to a human representative and record the transfer and its reason. Use
    POLICY_NOT_COVERED when no Ridgeline policy can resolve what the customer is asking for, and
    CUSTOMER_REQUESTED when the customer has explicitly asked for a human representative at least 2
    times during the conversation.

    Args:
        customer_id: The customer reference number read from the customer profile lookup; the profile must exist.
        reason: The reason for the transfer, exactly one of POLICY_NOT_COVERED or CUSTOMER_REQUESTED; never free text.
    """
    allowed = {"POLICY_NOT_COVERED", "CUSTOMER_REQUESTED"}
    if reason not in allowed:
        return f"Error: unknown transfer reason '{reason}'. Valid: {', '.join(sorted(allowed))}."
    if not ctx.find("customers", customer_id=customer_id):
        return f"Error: no customer {customer_id}; cannot record the transfer."
    rid = ctx.make_id("hof_", customer_id, reason)
    ctx.create("human_handoffs", rid, handoff_id=rid, customer_id=customer_id,
               reason=reason, created_at=ctx.now())
    return f"Transfer to a human representative recorded for {customer_id} ({reason})."

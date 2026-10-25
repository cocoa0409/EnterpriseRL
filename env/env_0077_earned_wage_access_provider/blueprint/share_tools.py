"""Shared tools for env_0077_earned_wage_access_provider (Paystride, Inc.).

One record finder per business record set (the customers finder doubles as the identity entry),
the identity-verification write (pass threshold: 2 matching credentials) and the transfer-to-human
write (customer-requested handoff after 2 explicit requests).
"""

from erlbench import ToolContext, tool


@tool(owner="agent", rw="read")
def find_customers(ctx: ToolContext, customer_id: str = "", name: str = "", phone: str = "", email: str = "") -> str:
    """Find the customer profile this call is about, whether the caller is an employer client or an
    individual worker. Search by the customer reference number, or by what a caller can naturally
    state: the registered name (a worker's full legal name or an employer's legal business name), the
    registered 10-digit phone number, or the registered email address. Every criterion is optional;
    supply whichever are known. The profile returned shows whether the customer is an employer or a
    worker, their contact details, the last four digits of their tax identification number, a worker's
    date of birth, the ZIP code on file and the date the profile was opened. Finding a profile does not
    confirm who is calling; identity is confirmed separately.

    Args:
        customer_id: The customer reference number; leave "" if unknown.
        name: The registered name as the caller states it; leave "" if not provided.
        phone: The registered phone number, 10 digits; leave "" if not provided.
        email: The registered email address; leave "" if not provided.
    """
    match = {k: v for k, v in {"customer_id": customer_id, "name": name, "phone": phone, "email": email}.items() if v}
    if not match:
        return "Error: provide at least one reference number or profile detail to find the customer."
    rows = ctx.fuzzy_find("customers", **match)
    if not rows:
        return f"No customer matches {match}."
    if len(rows) > 1:
        return f"Error: {len(rows)} customers match {match}; ask for one more detail to tell them apart."
    return str(rows[0])


@tool(owner="agent", rw="read")
def find_program_agreements(ctx: ToolContext, agreement_id: str = "", customer_id: str = "") -> str:
    """Look up an employer's Earned Wage Access Program Agreement: its tier, status, signing, go-live
    and renewal dates, fee model, configured access percentage, headcount, payroll groups, payroll
    system, remittance method, any termination notice, and the remittances and program charges
    currently owed. Every reference number below is optional; supply whichever are known and every
    record carrying all of them is returned, or a note that nothing matched.

    Args:
        agreement_id: The reference number of an employer's Earned Wage Access Program Agreement; leave "" if unknown.
        customer_id: The customer reference number of the employer or worker the record belongs to; leave "" if unknown.
    """
    match = {k: v for k, v in {"agreement_id": agreement_id, "customer_id": customer_id}.items() if v}
    rows = ctx.find("program_agreements", **match)
    return str(rows) if rows else f"No program_agreements records for {match}."


@tool(owner="agent", rw="read")
def find_program_settlements(ctx: ToolContext, settlement_entry_id: str = "", agreement_id: str = "", customer_id: str = "", schedule_entry_id: str = "", related_entry_id: str = "") -> str:
    """Look up the payroll settlement history of an employer program: deduction schedules issued for
    each pay date and payroll group, remittances received or returned, shortfall notices with their
    reasons and who bears them, and shortfalls written off. Every reference number below is
    optional; supply whichever are known and every record carrying all of them is returned, or a
    note that nothing matched.

    Args:
        settlement_entry_id: The reference number of a settlement entry; leave "" if unknown.
        agreement_id: The reference number of an employer's Earned Wage Access Program Agreement; leave "" if unknown.
        customer_id: The customer reference number of the employer or worker the record belongs to; leave "" if unknown.
        schedule_entry_id: The reference number of the deduction schedule an entry settles or concerns; leave "" if unknown.
        related_entry_id: The reference number of the source entry this entry points back to (for example the transfer a fee belongs to, or the line a payment settles); leave "" if unknown.
    """
    match = {k: v for k, v in {"settlement_entry_id": settlement_entry_id, "agreement_id": agreement_id, "customer_id": customer_id, "schedule_entry_id": schedule_entry_id, "related_entry_id": related_entry_id}.items() if v}
    rows = ctx.find("program_settlements", **match)
    return str(rows) if rows else f"No program_settlements records for {match}."


@tool(owner="agent", rw="read")
def find_program_billing(ctx: ToolContext, billing_entry_id: str = "", agreement_id: str = "", customer_id: str = "", related_entry_id: str = "") -> str:
    """Look up the program billing history of an employer: monthly invoice lines, late charges,
    payments applied and credit memos, with billing months, amounts and due dates. Every reference
    number below is optional; supply whichever are known and every record carrying all of them is
    returned, or a note that nothing matched.

    Args:
        billing_entry_id: The reference number of a billing entry; leave "" if unknown.
        agreement_id: The reference number of an employer's Earned Wage Access Program Agreement; leave "" if unknown.
        customer_id: The customer reference number of the employer or worker the record belongs to; leave "" if unknown.
        related_entry_id: The reference number of the source entry this entry points back to (for example the transfer a fee belongs to, or the line a payment settles); leave "" if unknown.
    """
    match = {k: v for k, v in {"billing_entry_id": billing_entry_id, "agreement_id": agreement_id, "customer_id": customer_id, "related_entry_id": related_entry_id}.items() if v}
    rows = ctx.find("program_billing", **match)
    return str(rows) if rows else f"No program_billing records for {match}."


@tool(owner="agent", rw="read")
def find_program_census(ctx: ToolContext, census_entry_id: str = "", agreement_id: str = "", customer_id: str = "") -> str:
    """Look up the monthly census reports of an employer program: eligible headcount, workers with an
    active Access plan, and measured platform availability for each month. Every reference number
    below is optional; supply whichever are known and every record carrying all of them is returned,
    or a note that nothing matched.

    Args:
        census_entry_id: The reference number of a monthly census report; leave "" if unknown.
        agreement_id: The reference number of an employer's Earned Wage Access Program Agreement; leave "" if unknown.
        customer_id: The customer reference number of the employer or worker the record belongs to; leave "" if unknown.
    """
    match = {k: v for k, v in {"census_entry_id": census_entry_id, "agreement_id": agreement_id, "customer_id": customer_id}.items() if v}
    rows = ctx.find("program_census", **match)
    return str(rows) if rows else f"No program_census records for {match}."


@tool(owner="agent", rw="read")
def find_program_change_requests(ctx: ToolContext, change_request_id: str = "", agreement_id: str = "", customer_id: str = "") -> str:
    """Look up program change requests an employer has made: access percentage, fee model and payroll
    group changes and termination notices, with the requester's role, status and effective date.
    Every reference number below is optional; supply whichever are known and every record carrying
    all of them is returned, or a note that nothing matched.

    Args:
        change_request_id: The reference number of a program change request; leave "" if unknown.
        agreement_id: The reference number of an employer's Earned Wage Access Program Agreement; leave "" if unknown.
        customer_id: The customer reference number of the employer or worker the record belongs to; leave "" if unknown.
    """
    match = {k: v for k, v in {"change_request_id": change_request_id, "agreement_id": agreement_id, "customer_id": customer_id}.items() if v}
    rows = ctx.find("program_change_requests", **match)
    return str(rows) if rows else f"No program_change_requests records for {match}."


@tool(owner="agent", rw="read")
def find_paycard_programs(ctx: ToolContext, paycard_program_id: str = "", customer_id: str = "") -> str:
    """Look up an employer's Payroll Card Program: its package, status, signing, launch and closing
    dates, funding method, card kit inventory, any termination notice, and the current funding
    balance. Every reference number below is optional; supply whichever are known and every record
    carrying all of them is returned, or a note that nothing matched.

    Args:
        paycard_program_id: The reference number of an employer's Payroll Card Program; leave "" if unknown.
        customer_id: The customer reference number of the employer or worker the record belongs to; leave "" if unknown.
    """
    match = {k: v for k, v in {"paycard_program_id": paycard_program_id, "customer_id": customer_id}.items() if v}
    rows = ctx.find("paycard_programs", **match)
    return str(rows) if rows else f"No paycard_programs records for {match}."


@tool(owner="agent", rw="read")
def find_paycard_funding(ctx: ToolContext, funding_entry_id: str = "", paycard_program_id: str = "", customer_id: str = "", related_entry_id: str = "", paycard_request_id: str = "", card_txn_id: str = "") -> str:
    """Look up the funding account history of an employer's Payroll Card Program: funds received and
    returned, payroll batches loaded to cards, refused loads credited back, recovered load
    reversals, and program fees debited or credited. Every reference number below is optional;
    supply whichever are known and every record carrying all of them is returned, or a note that
    nothing matched.

    Args:
        funding_entry_id: The reference number of a funding account entry; leave "" if unknown.
        paycard_program_id: The reference number of an employer's Payroll Card Program; leave "" if unknown.
        customer_id: The customer reference number of the employer or worker the record belongs to; leave "" if unknown.
        related_entry_id: The reference number of the source entry this entry points back to (for example the transfer a fee belongs to, or the line a payment settles); leave "" if unknown.
        paycard_request_id: The reference number of an employer's Payroll Card Program request; leave "" if unknown.
        card_txn_id: The reference number of a payroll card transaction; leave "" if unknown.
    """
    match = {k: v for k, v in {"funding_entry_id": funding_entry_id, "paycard_program_id": paycard_program_id, "customer_id": customer_id, "related_entry_id": related_entry_id, "paycard_request_id": paycard_request_id, "card_txn_id": card_txn_id}.items() if v}
    rows = ctx.find("paycard_funding", **match)
    return str(rows) if rows else f"No paycard_funding records for {match}."


@tool(owner="agent", rw="read")
def find_paycard_kit_orders(ctx: ToolContext, kit_order_id: str = "", paycard_program_id: str = "", customer_id: str = "") -> str:
    """Look up instant-issue card kit orders an employer has placed: date, quantity, ship-to location
    and shipping speed. Every reference number below is optional; supply whichever are known and
    every record carrying all of them is returned, or a note that nothing matched.

    Args:
        kit_order_id: The reference number of a card kit order; leave "" if unknown.
        paycard_program_id: The reference number of an employer's Payroll Card Program; leave "" if unknown.
        customer_id: The customer reference number of the employer or worker the record belongs to; leave "" if unknown.
    """
    match = {k: v for k, v in {"kit_order_id": kit_order_id, "paycard_program_id": paycard_program_id, "customer_id": customer_id}.items() if v}
    rows = ctx.find("paycard_kit_orders", **match)
    return str(rows) if rows else f"No paycard_kit_orders records for {match}."


@tool(owner="agent", rw="read")
def find_paycard_requests(ctx: ToolContext, paycard_request_id: str = "", paycard_program_id: str = "", customer_id: str = "", card_txn_id: str = "") -> str:
    """Look up requests an employer has made on its Payroll Card Program: erroneous load reversals,
    package changes and termination notices, with the requester's role and status. Every reference
    number below is optional; supply whichever are known and every record carrying all of them is
    returned, or a note that nothing matched.

    Args:
        paycard_request_id: The reference number of an employer's Payroll Card Program request; leave "" if unknown.
        paycard_program_id: The reference number of an employer's Payroll Card Program; leave "" if unknown.
        customer_id: The customer reference number of the employer or worker the record belongs to; leave "" if unknown.
        card_txn_id: The reference number of a payroll card transaction; leave "" if unknown.
    """
    match = {k: v for k, v in {"paycard_request_id": paycard_request_id, "paycard_program_id": paycard_program_id, "customer_id": customer_id, "card_txn_id": card_txn_id}.items() if v}
    rows = ctx.find("paycard_requests", **match)
    return str(rows) if rows else f"No paycard_requests records for {match}."


@tool(owner="agent", rw="read")
def find_disburse_services(ctx: ToolContext, disburse_service_id: str = "", customer_id: str = "") -> str:
    """Look up an employer's Instant Pay Disbursement service: its tier, status, dates, funding method,
    automatic replenishment setting, alert level and current prefund balance. Every reference number
    below is optional; supply whichever are known and every record carrying all of them is returned,
    or a note that nothing matched.

    Args:
        disburse_service_id: The reference number of an employer's Instant Pay Disbursement service; leave "" if unknown.
        customer_id: The customer reference number of the employer or worker the record belongs to; leave "" if unknown.
    """
    match = {k: v for k, v in {"disburse_service_id": disburse_service_id, "customer_id": customer_id}.items() if v}
    rows = ctx.find("disburse_services", **match)
    return str(rows) if rows else f"No disburse_services records for {match}."


@tool(owner="agent", rw="read")
def find_disburse_ledger(ctx: ToolContext, disburse_entry_id: str = "", disburse_service_id: str = "", customer_id: str = "", payee_customer_id: str = "", related_entry_id: str = "") -> str:
    """Look up the activity of an employer's Instant Pay Disbursement service: deposits and returned
    deposits, payouts to workers with their destination and delivery, returned or recalled payouts,
    fees and fee credits, and withdrawals. Every reference number below is optional; supply
    whichever are known and every record carrying all of them is returned, or a note that nothing
    matched.

    Args:
        disburse_entry_id: The reference number of a disbursement service entry; leave "" if unknown.
        disburse_service_id: The reference number of an employer's Instant Pay Disbursement service; leave "" if unknown.
        customer_id: The customer reference number of the employer or worker the record belongs to; leave "" if unknown.
        payee_customer_id: The customer reference number of the worker a payout was sent to; leave "" if unknown.
        related_entry_id: The reference number of the source entry this entry points back to (for example the transfer a fee belongs to, or the line a payment settles); leave "" if unknown.
    """
    match = {k: v for k, v in {"disburse_entry_id": disburse_entry_id, "disburse_service_id": disburse_service_id, "customer_id": customer_id, "payee_customer_id": payee_customer_id, "related_entry_id": related_entry_id}.items() if v}
    rows = ctx.find("disburse_ledger", **match)
    return str(rows) if rows else f"No disburse_ledger records for {match}."


@tool(owner="agent", rw="read")
def find_disburse_requests(ctx: ToolContext, disburse_request_id: str = "", disburse_service_id: str = "", customer_id: str = "", disburse_entry_id: str = "") -> str:
    """Look up requests an employer has made on its Instant Pay Disbursement service: payout recalls
    and service closures, with the requester's role and status. Every reference number below is
    optional; supply whichever are known and every record carrying all of them is returned, or a
    note that nothing matched.

    Args:
        disburse_request_id: The reference number of a disbursement service request; leave "" if unknown.
        disburse_service_id: The reference number of an employer's Instant Pay Disbursement service; leave "" if unknown.
        customer_id: The customer reference number of the employer or worker the record belongs to; leave "" if unknown.
        disburse_entry_id: The reference number of a disbursement service entry; leave "" if unknown.
    """
    match = {k: v for k, v in {"disburse_request_id": disburse_request_id, "disburse_service_id": disburse_service_id, "customer_id": customer_id, "disburse_entry_id": disburse_entry_id}.items() if v}
    rows = ctx.find("disburse_requests", **match)
    return str(rows) if rows else f"No disburse_requests records for {match}."


@tool(owner="agent", rw="read")
def find_access_plans(ctx: ToolContext, access_plan_id: str = "", customer_id: str = "", agreement_id: str = "") -> str:
    """Look up a worker's Earned Wage Access Plans: tier, status, the employer program it belongs to,
    employee number and payroll group, hire date, employment status, pay frequency, next payday,
    outstanding balance, card recovery authorization and the date the current tier took effect.
    Every reference number below is optional; supply whichever are known and every record carrying
    all of them is returned, or a note that nothing matched.

    Args:
        access_plan_id: The reference number of a worker's Earned Wage Access Plan; leave "" if unknown.
        customer_id: The customer reference number of the employer or worker the record belongs to; leave "" if unknown.
        agreement_id: The reference number of an employer's Earned Wage Access Program Agreement; leave "" if unknown.
    """
    match = {k: v for k, v in {"access_plan_id": access_plan_id, "customer_id": customer_id, "agreement_id": agreement_id}.items() if v}
    rows = ctx.find("access_plans", **match)
    return str(rows) if rows else f"No access_plans records for {match}."


@tool(owner="agent", rw="read")
def find_access_ledger(ctx: ToolContext, access_entry_id: str = "", access_plan_id: str = "", customer_id: str = "", related_entry_id: str = "") -> str:
    """Look up the early pay history of an Access plan: transfers with speed, destination and delivery,
    transfer fees, payday recoveries, shortfalls and where they were carried, write-offs, returned
    transfers and fee reversals. Every reference number below is optional; supply whichever are
    known and every record carrying all of them is returned, or a note that nothing matched.

    Args:
        access_entry_id: The reference number of an Access plan ledger entry; leave "" if unknown.
        access_plan_id: The reference number of a worker's Earned Wage Access Plan; leave "" if unknown.
        customer_id: The customer reference number of the employer or worker the record belongs to; leave "" if unknown.
        related_entry_id: The reference number of the source entry this entry points back to (for example the transfer a fee belongs to, or the line a payment settles); leave "" if unknown.
    """
    match = {k: v for k, v in {"access_entry_id": access_entry_id, "access_plan_id": access_plan_id, "customer_id": customer_id, "related_entry_id": related_entry_id}.items() if v}
    rows = ctx.find("access_ledger", **match)
    return str(rows) if rows else f"No access_ledger records for {match}."


@tool(owner="agent", rw="read")
def find_access_earnings(ctx: ToolContext, earnings_entry_id: str = "", access_plan_id: str = "", customer_id: str = "") -> str:
    """Look up the earnings accrued to an Access plan from the employer's feed: each work date's hours,
    gross and net earnings by source, corrections, and payday period closes. Every reference number
    below is optional; supply whichever are known and every record carrying all of them is returned,
    or a note that nothing matched.

    Args:
        earnings_entry_id: The reference number of an earnings entry; leave "" if unknown.
        access_plan_id: The reference number of a worker's Earned Wage Access Plan; leave "" if unknown.
        customer_id: The customer reference number of the employer or worker the record belongs to; leave "" if unknown.
    """
    match = {k: v for k, v in {"earnings_entry_id": earnings_entry_id, "access_plan_id": access_plan_id, "customer_id": customer_id}.items() if v}
    rows = ctx.find("access_earnings", **match)
    return str(rows) if rows else f"No access_earnings records for {match}."


@tool(owner="agent", rw="read")
def find_access_closure_requests(ctx: ToolContext, closure_request_id: str = "", access_plan_id: str = "", customer_id: str = "") -> str:
    """Look up a worker's requests to close an Access plan, with their status and effective date. Every
    reference number below is optional; supply whichever are known and every record carrying all of
    them is returned, or a note that nothing matched.

    Args:
        closure_request_id: The reference number of an Access plan closure request; leave "" if unknown.
        access_plan_id: The reference number of a worker's Earned Wage Access Plan; leave "" if unknown.
        customer_id: The customer reference number of the employer or worker the record belongs to; leave "" if unknown.
    """
    match = {k: v for k, v in {"closure_request_id": closure_request_id, "access_plan_id": access_plan_id, "customer_id": customer_id}.items() if v}
    rows = ctx.find("access_closure_requests", **match)
    return str(rows) if rows else f"No access_closure_requests records for {match}."


@tool(owner="agent", rw="read")
def find_card_accounts(ctx: ToolContext, card_account_id: str = "", customer_id: str = "", paycard_program_id: str = "") -> str:
    """Look up a worker's Paystride Visa Payroll Card account: plan, status, the employer program it
    was opened under, issue, activation and closing dates, last four digits of the current card,
    wage-payment consent date, first deposit date, any block reason, and the current balance. Every
    reference number below is optional; supply whichever are known and every record carrying all of
    them is returned, or a note that nothing matched.

    Args:
        card_account_id: The reference number of a payroll card account; leave "" if unknown.
        customer_id: The customer reference number of the employer or worker the record belongs to; leave "" if unknown.
        paycard_program_id: The reference number of an employer's Payroll Card Program; leave "" if unknown.
    """
    match = {k: v for k, v in {"card_account_id": card_account_id, "customer_id": customer_id, "paycard_program_id": paycard_program_id}.items() if v}
    rows = ctx.find("card_accounts", **match)
    return str(rows) if rows else f"No card_accounts records for {match}."


@tool(owner="agent", rw="read")
def find_card_transactions(ctx: ToolContext, card_txn_id: str = "", card_account_id: str = "", customer_id: str = "", related_txn_id: str = "", source_ref_id: str = "", dispute_id: str = "") -> str:
    """Look up the transactions on a payroll card account: loads, purchases, ATM and teller
    withdrawals, transfers, fees, fee refunds and rebates, and dispute credits and their reversals,
    with dates, amounts and references. Every reference number below is optional; supply whichever
    are known and every record carrying all of them is returned, or a note that nothing matched.

    Args:
        card_txn_id: The reference number of a payroll card transaction; leave "" if unknown.
        card_account_id: The reference number of a payroll card account; leave "" if unknown.
        customer_id: The customer reference number of the employer or worker the record belongs to; leave "" if unknown.
        related_txn_id: The reference number of the card transaction or service order this transaction points back to (for example the fee a refund returns); leave "" if unknown.
        source_ref_id: The reference number of the originating record in another ledger (for example the early wage transfer a load came from); leave "" if unknown.
        dispute_id: The reference number of a card dispute; leave "" if unknown.
    """
    match = {k: v for k, v in {"card_txn_id": card_txn_id, "card_account_id": card_account_id, "customer_id": customer_id, "related_txn_id": related_txn_id, "source_ref_id": source_ref_id, "dispute_id": dispute_id}.items() if v}
    rows = ctx.find("card_transactions", **match)
    return str(rows) if rows else f"No card_transactions records for {match}."


@tool(owner="agent", rw="read")
def find_card_service_orders(ctx: ToolContext, service_order_id: str = "", card_account_id: str = "", customer_id: str = "") -> str:
    """Look up service orders on a payroll card account: replacement cards with their reason and
    shipping speed, and written account history requests. Every reference number below is optional;
    supply whichever are known and every record carrying all of them is returned, or a note that
    nothing matched.

    Args:
        service_order_id: The reference number of a card service order; leave "" if unknown.
        card_account_id: The reference number of a payroll card account; leave "" if unknown.
        customer_id: The customer reference number of the employer or worker the record belongs to; leave "" if unknown.
    """
    match = {k: v for k, v in {"service_order_id": service_order_id, "card_account_id": card_account_id, "customer_id": customer_id}.items() if v}
    rows = ctx.find("card_service_orders", **match)
    return str(rows) if rows else f"No card_service_orders records for {match}."


@tool(owner="agent", rw="read")
def find_card_disputes(ctx: ToolContext, dispute_id: str = "", card_account_id: str = "", customer_id: str = "", card_txn_id: str = "") -> str:
    """Look up disputes a cardholder has raised on payroll card transactions: the transaction disputed,
    reason, path, notice and confirmation dates, history access date, amount, status and resolution
    date. Every reference number below is optional; supply whichever are known and every record
    carrying all of them is returned, or a note that nothing matched.

    Args:
        dispute_id: The reference number of a card dispute; leave "" if unknown.
        card_account_id: The reference number of a payroll card account; leave "" if unknown.
        customer_id: The customer reference number of the employer or worker the record belongs to; leave "" if unknown.
        card_txn_id: The reference number of a payroll card transaction; leave "" if unknown.
    """
    match = {k: v for k, v in {"dispute_id": dispute_id, "card_account_id": card_account_id, "customer_id": customer_id, "card_txn_id": card_txn_id}.items() if v}
    rows = ctx.find("card_disputes", **match)
    return str(rows) if rows else f"No card_disputes records for {match}."


@tool(owner="agent", rw="read")
def find_card_closure_requests(ctx: ToolContext, card_closure_request_id: str = "", card_account_id: str = "", customer_id: str = "") -> str:
    """Look up a cardholder's requests to close a payroll card account, with their status and payout
    method. Every reference number below is optional; supply whichever are known and every record
    carrying all of them is returned, or a note that nothing matched.

    Args:
        card_closure_request_id: The reference number of a card account closure request; leave "" if unknown.
        card_account_id: The reference number of a payroll card account; leave "" if unknown.
        customer_id: The customer reference number of the employer or worker the record belongs to; leave "" if unknown.
    """
    match = {k: v for k, v in {"card_closure_request_id": card_closure_request_id, "card_account_id": card_account_id, "customer_id": customer_id}.items() if v}
    rows = ctx.find("card_closure_requests", **match)
    return str(rows) if rows else f"No card_closure_requests records for {match}."


@tool(owner="agent", rw="read")
def find_save_accounts(ctx: ToolContext, save_account_id: str = "", customer_id: str = "", card_account_id: str = "") -> str:
    """Look up a worker's Paystride Save account: tier, status, linked card account, dates, round-up
    and auto-save settings, savings goal and balance. Every reference number below is optional;
    supply whichever are known and every record carrying all of them is returned, or a note that
    nothing matched.

    Args:
        save_account_id: The reference number of a Paystride Save account; leave "" if unknown.
        customer_id: The customer reference number of the employer or worker the record belongs to; leave "" if unknown.
        card_account_id: The reference number of a payroll card account; leave "" if unknown.
    """
    match = {k: v for k, v in {"save_account_id": save_account_id, "customer_id": customer_id, "card_account_id": card_account_id}.items() if v}
    rows = ctx.find("save_accounts", **match)
    return str(rows) if rows else f"No save_accounts records for {match}."


@tool(owner="agent", rw="read")
def find_save_ledger(ctx: ToolContext, save_entry_id: str = "", save_account_id: str = "", customer_id: str = "", source_ref_id: str = "") -> str:
    """Look up the activity of a Paystride Save account: deposits by source, withdrawals, monthly
    interest, streak bonuses and bonus clawbacks. Every reference number below is optional; supply
    whichever are known and every record carrying all of them is returned, or a note that nothing
    matched.

    Args:
        save_entry_id: The reference number of a savings entry; leave "" if unknown.
        save_account_id: The reference number of a Paystride Save account; leave "" if unknown.
        customer_id: The customer reference number of the employer or worker the record belongs to; leave "" if unknown.
        source_ref_id: The reference number of the originating record in another ledger (for example the early wage transfer a load came from); leave "" if unknown.
    """
    match = {k: v for k, v in {"save_entry_id": save_entry_id, "save_account_id": save_account_id, "customer_id": customer_id, "source_ref_id": source_ref_id}.items() if v}
    rows = ctx.find("save_ledger", **match)
    return str(rows) if rows else f"No save_ledger records for {match}."


@tool(owner="agent", rw="read")
def find_save_requests(ctx: ToolContext, save_request_id: str = "", save_account_id: str = "", customer_id: str = "") -> str:
    """Look up a worker's requests to close a Paystride Save account, with their status. Every
    reference number below is optional; supply whichever are known and every record carrying all of
    them is returned, or a note that nothing matched.

    Args:
        save_request_id: The reference number of a savings closure request; leave "" if unknown.
        save_account_id: The reference number of a Paystride Save account; leave "" if unknown.
        customer_id: The customer reference number of the employer or worker the record belongs to; leave "" if unknown.
    """
    match = {k: v for k, v in {"save_request_id": save_request_id, "save_account_id": save_account_id, "customer_id": customer_id}.items() if v}
    rows = ctx.find("save_requests", **match)
    return str(rows) if rows else f"No save_requests records for {match}."


@tool(owner="agent", rw="read")
def find_loan_accounts(ctx: ToolContext, loan_account_id: str = "", customer_id: str = "", agreement_id: str = "") -> str:
    """Look up a worker's Paystride Payroll-Repaid Loans: tier, status, sponsoring employer program,
    dates, principal, APR, term, installment, next installment date, repayment method and balance.
    Every reference number below is optional; supply whichever are known and every record carrying
    all of them is returned, or a note that nothing matched.

    Args:
        loan_account_id: The reference number of a payroll-repaid loan; leave "" if unknown.
        customer_id: The customer reference number of the employer or worker the record belongs to; leave "" if unknown.
        agreement_id: The reference number of an employer's Earned Wage Access Program Agreement; leave "" if unknown.
    """
    match = {k: v for k, v in {"loan_account_id": loan_account_id, "customer_id": customer_id, "agreement_id": agreement_id}.items() if v}
    rows = ctx.find("loan_accounts", **match)
    return str(rows) if rows else f"No loan_accounts records for {match}."


@tool(owner="agent", rw="read")
def find_loan_ledger(ctx: ToolContext, loan_entry_id: str = "", loan_account_id: str = "", customer_id: str = "", related_entry_id: str = "") -> str:
    """Look up the history of a payroll-repaid loan: disbursement, monthly interest, payments by
    method, returned payments and any charge-off. Every reference number below is optional; supply
    whichever are known and every record carrying all of them is returned, or a note that nothing
    matched.

    Args:
        loan_entry_id: The reference number of a loan entry; leave "" if unknown.
        loan_account_id: The reference number of a payroll-repaid loan; leave "" if unknown.
        customer_id: The customer reference number of the employer or worker the record belongs to; leave "" if unknown.
        related_entry_id: The reference number of the source entry this entry points back to (for example the transfer a fee belongs to, or the line a payment settles); leave "" if unknown.
    """
    match = {k: v for k, v in {"loan_entry_id": loan_entry_id, "loan_account_id": loan_account_id, "customer_id": customer_id, "related_entry_id": related_entry_id}.items() if v}
    rows = ctx.find("loan_ledger", **match)
    return str(rows) if rows else f"No loan_ledger records for {match}."


@tool(owner="agent", rw="read")
def find_loan_requests(ctx: ToolContext, loan_request_id: str = "", loan_account_id: str = "", customer_id: str = "") -> str:
    """Look up a borrower's loan requests: offer acceptances and declines, hardship deferrals,
    deduction revocations and cancellations, with their status. Every reference number below is
    optional; supply whichever are known and every record carrying all of them is returned, or a
    note that nothing matched.

    Args:
        loan_request_id: The reference number of a loan request; leave "" if unknown.
        loan_account_id: The reference number of a payroll-repaid loan; leave "" if unknown.
        customer_id: The customer reference number of the employer or worker the record belongs to; leave "" if unknown.
    """
    match = {k: v for k, v in {"loan_request_id": loan_request_id, "loan_account_id": loan_account_id, "customer_id": customer_id}.items() if v}
    rows = ctx.find("loan_requests", **match)
    return str(rows) if rows else f"No loan_requests records for {match}."


@tool(owner="agent", rw="read")
def find_verification_log(ctx: ToolContext, verification_id: str = "", customer_id: str = "") -> str:
    """Look up the recorded outcome of identity verification for a customer on this call. Every
    reference number below is optional; supply whichever are known and every record carrying all of
    them is returned, or a note that nothing matched.

    Args:
        verification_id: The reference number of an identity verification record; leave "" if unknown.
        customer_id: The customer reference number of the employer or worker the record belongs to; leave "" if unknown.
    """
    match = {k: v for k, v in {"verification_id": verification_id, "customer_id": customer_id}.items() if v}
    rows = ctx.find("verification_log", **match)
    return str(rows) if rows else f"No verification_log records for {match}."


@tool(owner="agent", rw="read")
def find_handoff_log(ctx: ToolContext, handoff_id: str = "", customer_id: str = "") -> str:
    """Look up handoffs of a customer to a human representative, with their reason and time. Every
    reference number below is optional; supply whichever are known and every record carrying all of
    them is returned, or a note that nothing matched.

    Args:
        handoff_id: The reference number of a handoff record; leave "" if unknown.
        customer_id: The customer reference number of the employer or worker the record belongs to; leave "" if unknown.
    """
    match = {k: v for k, v in {"handoff_id": handoff_id, "customer_id": customer_id}.items() if v}
    rows = ctx.find("handoff_log", **match)
    return str(rows) if rows else f"No handoff_log records for {match}."


@tool(owner="agent", rw="write")
def verify_customer_identity(ctx: ToolContext, customer_id: str, phone: str = "", email: str = "",
                             tax_id_last4: str = "", date_of_birth: str = "", zip_code: str = "") -> str:
    """Confirm that the caller is the customer on file and record the outcome. Identity must be confirmed
    before any account information is discussed or any money is moved. This tool compares each piece of
    identity information the caller states against the customer profile, counts the matches itself, and
    confirms identity only when at least 2 of them match. The customer reference number only selects
    the profile to compare against and never counts as a match. Callers usually give only some details,
    so pass exactly what the caller said and leave the rest empty. The outcome is recorded; if a first
    attempt falls short and a later attempt with more details succeeds, the confirmation stands.

    Args:
        customer_id: The customer reference number read from the customer profile; required, and used only to select the profile.
        phone: The registered phone number as the caller states it, 10 digits with no punctuation; leave "" if not stated.
        email: The registered email address as the caller states it; leave "" if not stated.
        tax_id_last4: The last four digits of the worker's Social Security number or of the employer's Employer Identification Number, as stated; leave "" if not stated.
        date_of_birth: The worker's date of birth as YYYY-MM-DD; leave "" if not stated (employers have none on file).
        zip_code: The 5-digit ZIP code of the home or billing address on file, as stated; leave "" if not stated.
    """
    if not customer_id:
        return "Error: customer_id is required; find the customer profile first and pass its reference number."
    rows = ctx.find("customers", customer_id=customer_id)
    if not rows:
        return f"Error: no customer {customer_id}; cannot verify."
    rec = rows[0]
    # The tool owns the comparison; the locator customer_id is never counted.
    supplied = {"phone": phone, "email": email, "tax_id_last4": tax_id_last4,
                "date_of_birth": date_of_birth, "zip_code": zip_code}
    matched = sum(1 for field, value in supplied.items() if value and str(rec.get(field) or "").strip().casefold() == str(value).strip().casefold())
    verified = matched >= 2
    rid = ctx.make_id("ver_", customer_id)
    # Upsert and never downgrade: only the reproducible boolean is stored.
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
    """Hand the customer over to a human Paystride representative and record the handoff with its reason.
    Use it in one of two situations only: no Paystride policy offers a way to resolve what the customer
    is asking for, or the customer has explicitly asked to speak with a human representative at least
    2 times during the call.

    Args:
        customer_id: The customer reference number read from the customer profile; the profile must exist.
        reason: Why the customer is being handed over; exactly one of POLICY_NOT_COVERED (current policy offers no way to resolve the request) or CUSTOMER_REQUESTED (the customer has explicitly asked for a human representative at least 2 times); never free text.
    """
    allowed = {"POLICY_NOT_COVERED", "CUSTOMER_REQUESTED"}
    if reason not in allowed:
        return f"Error: unknown handoff reason '{reason}'. Valid: {', '.join(sorted(allowed))}."
    if not ctx.find("customers", customer_id=customer_id):
        return f"Error: no customer {customer_id}; cannot record the handoff."
    rid = ctx.make_id("hof_", customer_id, reason)
    ctx.create("handoff_log", rid, handoff_id=rid, customer_id=customer_id, reason=reason, created_at=ctx.now())
    return f"Handoff to a human representative recorded for {customer_id} ({reason})."

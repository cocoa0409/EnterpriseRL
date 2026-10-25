"""Shared tools for env_0067_online_personal_loan_lender (Larkspur Lending).
Output of the erl-scenario-blueprint skill. Path: env/env_0067_online_personal_loan_lender/blueprint/share_tools.py

Every tool here is a SHARE tool, always present in its owner's tool list:
  - one finder per table (the customers finder doubles as the identity entry);
  - verify_customer_identity (K = 3 matching credentials of phone, email, date of birth,
    SSN last four, ZIP code; stores only the verified boolean, upserted and monotonic);
  - transfer_to_human_agent (reason POLICY_NOT_COVERED or CUSTOMER_REQUESTED; the repeat-request
    threshold R = 2).
Customer-originated writes are hidden task tools in each difficulty's task_tools.py.
"""

from erlbench import ToolContext, tool


@tool(owner="agent", rw="read")
def find_customers(ctx: ToolContext, customer_id: str = "", phone_number: str = "", email: str = "", name: str = "") -> str:
    """Find the Larkspur customer profile a call is about.

    Search by the customer reference number, or by what the caller can tell you: the mobile number on file,
    the email address on file, or the full name. Supply whichever are known; every criterion is optional and is
    compared generously (spacing, punctuation and letter case are ignored). A hit returns the full profile:
    legal name, mobile number, email, date of birth, last four digits of the Social Security number, residential
    address with state and ZIP code, the date the profile was created and the preferred language. Finding a
    profile does not verify the caller's identity.

    Args:
        customer_id: Customer reference number; leave "" if unknown.
        phone_number: Mobile number the caller gives, 10 digits (e.g. 6125550148); leave "" if not provided.
        email: Email address the caller gives; leave "" if not provided.
        name: Full name the caller gives; leave "" if not provided.
    """
    match = {k: v for k, v in {"customer_id": customer_id, "phone_number": phone_number,
                               "email": email, "name": name}.items() if v}
    if not match:
        return "Error: provide at least one reference number or profile detail to find the customer."
    rows = ctx.fuzzy_find("customers", **match)
    if not rows:
        return f"No customer matches {match}."
    if len(rows) > 1:
        return f"Error: {len(rows)} customers match {match}; ask for one more detail to tell them apart."
    return str(rows[0])


@tool(owner="agent", rw="read")
def find_bank_accounts(ctx: ToolContext, bank_account_id: str = "", customer_id: str = "") -> str:
    """Look up the bank accounts a customer has linked for payments, AutoPay and disbursements.

    Each record shows the bank name, whether it is a checking or savings account, the last four digits of the
    account number, the routing number, the date it was linked and its ownership-verification status (verified,
    awaiting micro-deposit confirmation, failed, or closed after the bank reported it closed). Search by the
    linked-account reference or by the customer; every criterion is optional, and all matching accounts are
    returned.

    Args:
        bank_account_id: Reference number of the linked bank account itself. Leave "" if unknown.
        customer_id: Customer reference number of the account owner. Leave "" if unknown.
    """
    match = {k: v for k, v in {"bank_account_id": bank_account_id,
                               "customer_id": customer_id}.items() if v}
    rows = ctx.find("bank_accounts", **match)
    return str(rows) if rows else f"No linked bank accounts found for {match}."


@tool(owner="agent", rw="read")
def find_loans(ctx: ToolContext, loan_id: str = "", customer_id: str = "", autopay_bank_account_id: str = "", refinanced_from_loan_id: str = "") -> str:
    """Retrieve personal loan accounts with their full current terms and standing.

    A loan record carries its rate grade, lifecycle status, purpose, the state it was originated in, the key
    dates (application, approval, funding, maturity, closing), the term, the loan amount, origination fee and net
    proceeds, the base and current interest rates and APR, whether AutoPay and the direct-pay discount apply, the
    monthly installment and due day, the next due date, the date interest is paid through, and the unpaid
    principal, unpaid fees and amount past due. A refinance loan also names the loan it paid off. Search by the
    loan reference, the borrower, the AutoPay bank account, or the loan a refinance replaced; every criterion is
    optional and all matches are returned.

    Args:
        loan_id: Reference number of the personal loan. Leave "" if unknown.
        customer_id: Customer reference number of the borrower. Leave "" if unknown.
        autopay_bank_account_id: Reference number of the linked bank account that AutoPay debits. Leave "" if unknown.
        refinanced_from_loan_id: Reference number of the earlier loan that a refinance loan paid off. Leave "" if unknown.
    """
    match = {k: v for k, v in {"loan_id": loan_id,
                               "customer_id": customer_id,
                               "autopay_bank_account_id": autopay_bank_account_id,
                               "refinanced_from_loan_id": refinanced_from_loan_id}.items() if v}
    rows = ctx.find("loans", **match)
    return str(rows) if rows else f"No personal loans found for {match}."


@tool(owner="agent", rw="read")
def find_loan_transactions(ctx: ToolContext, loan_txn_id: str = "", loan_id: str = "", customer_id: str = "", bank_account_id: str = "", related_txn_id: str = "", source_txn_id: str = "") -> str:
    """List the money movements booked on personal loans.

    This covers disbursements at funding (deposit to the borrower, creditor direct payments, refinance payoff
    transfers and the withheld origination fee), payments with their interest and principal split, payment
    returns with their return code, late fees and returned-payment fees with the state fee schedule used, fee
    payments, and fee waivers with their basis. Search by the entry's own reference, the loan, the borrower, the
    bank account involved, the entry it acts on, or the payment that funded a fee payment; every criterion is
    optional and all matching entries are returned.

    Args:
        loan_txn_id: Reference number of the ledger entry itself. Leave "" if unknown.
        loan_id: Reference number of the personal loan. Leave "" if unknown.
        customer_id: Customer reference number of the borrower. Leave "" if unknown.
        bank_account_id: Reference number of the linked bank account debited or credited. Leave "" if unknown.
        related_txn_id: Reference number of the entry this entry acts on (for example the payment a return reverses, or the fee a waiver removes). Leave "" if unknown.
        source_txn_id: Reference number of the payment that funded a fee payment. Leave "" if unknown.
    """
    match = {k: v for k, v in {"loan_txn_id": loan_txn_id,
                               "loan_id": loan_id,
                               "customer_id": customer_id,
                               "bank_account_id": bank_account_id,
                               "related_txn_id": related_txn_id,
                               "source_txn_id": source_txn_id}.items() if v}
    rows = ctx.find("loan_transactions", **match)
    return str(rows) if rows else f"No loan ledger entries found for {match}."


@tool(owner="agent", rw="read")
def find_loan_servicing_events(ctx: ToolContext, loan_service_event_id: str = "", loan_id: str = "", customer_id: str = "", bank_account_id: str = "") -> str:
    """Review the servicing changes recorded on personal loans that do not move money.

    These are due-date changes (old and new due day and the first due date under the new day), AutoPay
    enrollments (with the bank account to be debited) and AutoPay cancellations (with the reason), each with the
    date and the channel the change came through. Search by the record's own reference, the loan, the borrower or
    the bank account; every criterion is optional and all matches are returned.

    Args:
        loan_service_event_id: Reference number of the servicing record itself. Leave "" if unknown.
        loan_id: Reference number of the personal loan. Leave "" if unknown.
        customer_id: Customer reference number of the borrower. Leave "" if unknown.
        bank_account_id: Reference number of the linked bank account named in an AutoPay enrollment. Leave "" if unknown.
    """
    match = {k: v for k, v in {"loan_service_event_id": loan_service_event_id,
                               "loan_id": loan_id,
                               "customer_id": customer_id,
                               "bank_account_id": bank_account_id}.items() if v}
    rows = ctx.find("loan_servicing_events", **match)
    return str(rows) if rows else f"No loan servicing records found for {match}."


@tool(owner="agent", rw="read")
def find_loan_payoff_quotes(ctx: ToolContext, payoff_quote_id: str = "", loan_id: str = "", customer_id: str = "") -> str:
    """Pull up payoff quotes previously issued on personal loans.

    Each quote shows the date issued, the good-through date, the principal, the interest accrued through the
    good-through date, unpaid fees, the total payoff amount, the daily (per diem) interest and the purpose of the
    quote (borrower payoff, Larkspur refinance or another lender's payoff). Search by the quote reference, the loan
    or the borrower; every criterion is optional.

    Args:
        payoff_quote_id: Reference number of the payoff quote. Leave "" if unknown.
        loan_id: Reference number of the personal loan. Leave "" if unknown.
        customer_id: Customer reference number of the borrower. Leave "" if unknown.
    """
    match = {k: v for k, v in {"payoff_quote_id": payoff_quote_id,
                               "loan_id": loan_id,
                               "customer_id": customer_id}.items() if v}
    rows = ctx.find("loan_payoff_quotes", **match)
    return str(rows) if rows else f"No payoff quotes found for {match}."


@tool(owner="agent", rw="read")
def find_hardship_plans(ctx: ToolContext, hardship_plan_id: str = "", customer_id: str = "", loan_id: str = "") -> str:
    """Look up hardship assistance requests and plans on personal loans.

    A plan record names the assistance program, its status, the hardship reported, the request, decision and
    acceptance dates, any decline reason, the first and last affected due dates, the number of plan months, the
    plan payment and rate, deferred installments, term extension, settlement amount, any FEMA declaration number
    or military service start date, and the closing date. Search by the plan reference, the borrower or the loan;
    every criterion is optional and all matches are returned.

    Args:
        hardship_plan_id: Reference number of the hardship plan or request. Leave "" if unknown.
        customer_id: Customer reference number of the borrower. Leave "" if unknown.
        loan_id: Reference number of the personal loan the plan applies to. Leave "" if unknown.
    """
    match = {k: v for k, v in {"hardship_plan_id": hardship_plan_id,
                               "customer_id": customer_id,
                               "loan_id": loan_id}.items() if v}
    rows = ctx.find("hardship_plans", **match)
    return str(rows) if rows else f"No hardship plans found for {match}."


@tool(owner="agent", rw="read")
def find_hardship_plan_events(ctx: ToolContext, hardship_event_id: str = "", hardship_plan_id: str = "", customer_id: str = "", loan_id: str = "", loan_txn_id: str = "") -> str:
    """See the detailed history of a hardship plan.

    Entries include supporting documents received (income statements, termination notices, medical bills,
    military orders, FEMA registrations and similar), each installment deferred to the end of the term, each
    plan installment scheduled, and each plan installment credited with the loan payment that satisfied it.
    Search by the entry reference, the plan, the borrower, the loan or the loan payment; every criterion is
    optional.

    Args:
        hardship_event_id: Reference number of the plan history entry. Leave "" if unknown.
        hardship_plan_id: Reference number of the hardship plan. Leave "" if unknown.
        customer_id: Customer reference number of the borrower. Leave "" if unknown.
        loan_id: Reference number of the personal loan. Leave "" if unknown.
        loan_txn_id: Reference number of the loan payment that satisfied a plan installment. Leave "" if unknown.
    """
    match = {k: v for k, v in {"hardship_event_id": hardship_event_id,
                               "hardship_plan_id": hardship_plan_id,
                               "customer_id": customer_id,
                               "loan_id": loan_id,
                               "loan_txn_id": loan_txn_id}.items() if v}
    rows = ctx.find("hardship_plan_events", **match)
    return str(rows) if rows else f"No hardship plan history entries found for {match}."


@tool(owner="agent", rw="read")
def find_pos_merchants(ctx: ToolContext, merchant_id: str = "") -> str:
    """Look up a PracticePay provider (the dental, veterinary, vision or other practice where patient financing is used).

    The record gives the practice name, specialty, state, enrollment status with Larkspur and the date it
    enrolled. Search by the provider reference; leave it blank to list every enrolled provider.

    Args:
        merchant_id: Reference number of the provider. Leave "" if unknown.
    """
    match = {k: v for k, v in {"merchant_id": merchant_id}.items() if v}
    rows = ctx.find("pos_merchants", **match)
    return str(rows) if rows else f"No PracticePay providers found for {match}."


@tool(owner="agent", rw="read")
def find_pos_plans(ctx: ToolContext, pos_plan_id: str = "", customer_id: str = "", merchant_id: str = "") -> str:
    """Retrieve PracticePay patient financing plans.

    A plan record shows the promotional plan, status, provider, application and approval dates, approval
    expiry and approved amount, the date of service and amount financed, the plan APR, the promotional end date,
    the number of payments, the monthly payment and due day, the next due date, the plan balance, any deferred
    interest accrued but not billed, the amount past due, AutoPay, and closing details. Search by the plan
    reference, the patient or the provider; every criterion is optional.

    Args:
        pos_plan_id: Reference number of the PracticePay plan. Leave "" if unknown.
        customer_id: Customer reference number of the patient-borrower. Leave "" if unknown.
        merchant_id: Reference number of the provider. Leave "" if unknown.
    """
    match = {k: v for k, v in {"pos_plan_id": pos_plan_id,
                               "customer_id": customer_id,
                               "merchant_id": merchant_id}.items() if v}
    rows = ctx.find("pos_plans", **match)
    return str(rows) if rows else f"No PracticePay plans found for {match}."


@tool(owner="agent", rw="read")
def find_pos_transactions(ctx: ToolContext, pos_txn_id: str = "", pos_plan_id: str = "", customer_id: str = "", merchant_id: str = "", bank_account_id: str = "", related_txn_id: str = "") -> str:
    """List the entries booked on PracticePay plans.

    Entries include the financed treatment charge, provider refunds (with the provider's refund reference),
    payments and returned payments, late and returned-payment fees, fee waivers, monthly interest, deferred
    interest accrued, billed or cleared, each with its date, amount and the entry it acts on. Search by the entry
    reference, the plan, the patient, the provider, the bank account or the entry acted on; every criterion is
    optional.

    Args:
        pos_txn_id: Reference number of the plan entry. Leave "" if unknown.
        pos_plan_id: Reference number of the PracticePay plan. Leave "" if unknown.
        customer_id: Customer reference number of the patient-borrower. Leave "" if unknown.
        merchant_id: Reference number of the provider. Leave "" if unknown.
        bank_account_id: Reference number of the linked bank account of a payment. Leave "" if unknown.
        related_txn_id: Reference number of the entry acted on (for example the charge a refund credits). Leave "" if unknown.
    """
    match = {k: v for k, v in {"pos_txn_id": pos_txn_id,
                               "pos_plan_id": pos_plan_id,
                               "customer_id": customer_id,
                               "merchant_id": merchant_id,
                               "bank_account_id": bank_account_id,
                               "related_txn_id": related_txn_id}.items() if v}
    rows = ctx.find("pos_transactions", **match)
    return str(rows) if rows else f"No PracticePay entries found for {match}."


@tool(owner="agent", rw="read")
def find_pos_billing_disputes(ctx: ToolContext, pos_dispute_id: str = "", customer_id: str = "", pos_plan_id: str = "", merchant_id: str = "", pos_txn_id: str = "") -> str:
    """Check billing disputes a patient has raised about a provider's financed charge.

    Each dispute shows the plan, provider and charge disputed, the filing date, the amount and reason disputed,
    the current outcome and the resolution date. Search by the dispute reference, the patient, the plan, the
    provider or the disputed charge; every criterion is optional.

    Args:
        pos_dispute_id: Reference number of the billing dispute. Leave "" if unknown.
        customer_id: Customer reference number of the patient-borrower. Leave "" if unknown.
        pos_plan_id: Reference number of the PracticePay plan. Leave "" if unknown.
        merchant_id: Reference number of the provider. Leave "" if unknown.
        pos_txn_id: Reference number of the financed charge disputed. Leave "" if unknown.
    """
    match = {k: v for k, v in {"pos_dispute_id": pos_dispute_id,
                               "customer_id": customer_id,
                               "pos_plan_id": pos_plan_id,
                               "merchant_id": merchant_id,
                               "pos_txn_id": pos_txn_id}.items() if v}
    rows = ctx.find("pos_billing_disputes", **match)
    return str(rows) if rows else f"No billing disputes found for {match}."


@tool(owner="agent", rw="read")
def find_credit_lines(ctx: ToolContext, credit_line_id: str = "", customer_id: str = "") -> str:
    """Retrieve FlexLine personal lines of credit.

    A line record shows the tier, status, application and opening dates, credit limit, current APR, the end of
    the draw period, the outstanding balance, the minimum payment and due day, the next due date, the amount past
    due, AutoPay, any freeze reason and closing details. Search by the line reference or the borrower; every
    criterion is optional.

    Args:
        credit_line_id: Reference number of the FlexLine. Leave "" if unknown.
        customer_id: Customer reference number of the borrower. Leave "" if unknown.
    """
    match = {k: v for k, v in {"credit_line_id": credit_line_id,
                               "customer_id": customer_id}.items() if v}
    rows = ctx.find("credit_lines", **match)
    return str(rows) if rows else f"No FlexLine accounts found for {match}."


@tool(owner="agent", rw="read")
def find_line_transactions(ctx: ToolContext, line_txn_id: str = "", credit_line_id: str = "", customer_id: str = "", bank_account_id: str = "", related_txn_id: str = "") -> str:
    """List the entries booked on FlexLine accounts.

    Entries include draws to a bank account and their draw fees, monthly interest, annual fees, payments and
    returned payments, late and returned-payment fees, and fee waivers, each with its date, amount, statement
    month or due date where relevant, and the entry it acts on. Search by the entry reference, the line, the
    borrower, the bank account or the entry acted on; every criterion is optional.

    Args:
        line_txn_id: Reference number of the FlexLine entry. Leave "" if unknown.
        credit_line_id: Reference number of the FlexLine. Leave "" if unknown.
        customer_id: Customer reference number of the borrower. Leave "" if unknown.
        bank_account_id: Reference number of the linked bank account involved. Leave "" if unknown.
        related_txn_id: Reference number of the entry acted on. Leave "" if unknown.
    """
    match = {k: v for k, v in {"line_txn_id": line_txn_id,
                               "credit_line_id": credit_line_id,
                               "customer_id": customer_id,
                               "bank_account_id": bank_account_id,
                               "related_txn_id": related_txn_id}.items() if v}
    rows = ctx.find("line_transactions", **match)
    return str(rows) if rows else f"No FlexLine entries found for {match}."


@tool(owner="agent", rw="read")
def find_line_limit_requests(ctx: ToolContext, limit_request_id: str = "", customer_id: str = "", credit_line_id: str = "") -> str:
    """Check requests to raise or lower a FlexLine credit limit.

    Each request shows the date, direction, the limit at the time, the limit asked for, the decision status,
    the limit granted and the decision date. Search by the request reference, the borrower or the line; every
    criterion is optional.

    Args:
        limit_request_id: Reference number of the limit request. Leave "" if unknown.
        customer_id: Customer reference number of the borrower. Leave "" if unknown.
        credit_line_id: Reference number of the FlexLine. Leave "" if unknown.
    """
    match = {k: v for k, v in {"limit_request_id": limit_request_id,
                               "customer_id": customer_id,
                               "credit_line_id": credit_line_id}.items() if v}
    rows = ctx.find("line_limit_requests", **match)
    return str(rows) if rows else f"No credit-limit requests found for {match}."


@tool(owner="agent", rw="read")
def find_builder_accounts(ctx: ToolContext, builder_account_id: str = "", customer_id: str = "", bank_account_id: str = "") -> str:
    """Retrieve Credit Builder accounts (a small installment loan whose proceeds are held in a locked savings certificate).

    An account record shows the plan, status, application and opening dates, loan amount, administration fee,
    APR, term, monthly payment and due day, next due date, unpaid loan balance, locked savings balance, unpaid
    fees, amount past due, AutoPay, the linked bank account, maturity date and closing details. Search by the
    account reference, the borrower or the linked bank account; every criterion is optional.

    Args:
        builder_account_id: Reference number of the Credit Builder account. Leave "" if unknown.
        customer_id: Customer reference number of the borrower. Leave "" if unknown.
        bank_account_id: Reference number of the linked bank account. Leave "" if unknown.
    """
    match = {k: v for k, v in {"builder_account_id": builder_account_id,
                               "customer_id": customer_id,
                               "bank_account_id": bank_account_id}.items() if v}
    rows = ctx.find("builder_accounts", **match)
    return str(rows) if rows else f"No Credit Builder accounts found for {match}."


@tool(owner="agent", rw="read")
def find_builder_transactions(ctx: ToolContext, builder_txn_id: str = "", builder_account_id: str = "", customer_id: str = "", bank_account_id: str = "", related_txn_id: str = "") -> str:
    """List the entries booked on Credit Builder accounts.

    Entries include the loan deposit into the savings certificate, the administration fee, payments with their
    interest and principal split, returned payments, late and returned-payment fees, fee waivers and fee
    payments, savings dividends, savings applied to the loan at closing and savings released to the borrower.
    Search by the entry reference, the account, the borrower, the bank account or the entry acted on; every
    criterion is optional.

    Args:
        builder_txn_id: Reference number of the Credit Builder entry. Leave "" if unknown.
        builder_account_id: Reference number of the Credit Builder account. Leave "" if unknown.
        customer_id: Customer reference number of the borrower. Leave "" if unknown.
        bank_account_id: Reference number of the linked bank account involved. Leave "" if unknown.
        related_txn_id: Reference number of the entry acted on. Leave "" if unknown.
    """
    match = {k: v for k, v in {"builder_txn_id": builder_txn_id,
                               "builder_account_id": builder_account_id,
                               "customer_id": customer_id,
                               "bank_account_id": bank_account_id,
                               "related_txn_id": related_txn_id}.items() if v}
    rows = ctx.find("builder_transactions", **match)
    return str(rows) if rows else f"No Credit Builder entries found for {match}."


@tool(owner="agent", rw="read")
def find_builder_closure_requests(ctx: ToolContext, builder_closure_id: str = "", customer_id: str = "", builder_account_id: str = "", bank_account_id: str = "") -> str:
    """Check early-closure requests on Credit Builder accounts.

    Each request shows the account, the date it was registered, where the remaining savings are to be released
    and whether the borrower has confirmed it, withdrawn it, or it is still awaiting confirmation. Search by the
    request reference, the borrower, the account or the release bank account; every criterion is optional.

    Args:
        builder_closure_id: Reference number of the closure request. Leave "" if unknown.
        customer_id: Customer reference number of the borrower. Leave "" if unknown.
        builder_account_id: Reference number of the Credit Builder account. Leave "" if unknown.
        bank_account_id: Reference number of the linked bank account for the release. Leave "" if unknown.
    """
    match = {k: v for k, v in {"builder_closure_id": builder_closure_id,
                               "customer_id": customer_id,
                               "builder_account_id": builder_account_id,
                               "bank_account_id": bank_account_id}.items() if v}
    rows = ctx.find("builder_closure_requests", **match)
    return str(rows) if rows else f"No Credit Builder closure requests found for {match}."


@tool(owner="agent", rw="read")
def find_protection_plans(ctx: ToolContext, protection_plan_id: str = "", customer_id: str = "", loan_id: str = "") -> str:
    """Look up Payment Protection plans attached to personal loans.

    A plan record shows the protection plan, status, enrollment and effective dates, the end of the free-look
    period, any jointly covered person, the covered borrower's birth date, and cancellation or termination
    details. Search by the plan reference, the borrower or the protected loan; every criterion is optional.

    Args:
        protection_plan_id: Reference number of the Payment Protection plan. Leave "" if unknown.
        customer_id: Customer reference number of the borrower. Leave "" if unknown.
        loan_id: Reference number of the protected personal loan. Leave "" if unknown.
    """
    match = {k: v for k, v in {"protection_plan_id": protection_plan_id,
                               "customer_id": customer_id,
                               "loan_id": loan_id}.items() if v}
    rows = ctx.find("protection_plans", **match)
    return str(rows) if rows else f"No Payment Protection plans found for {match}."


@tool(owner="agent", rw="read")
def find_protection_events(ctx: ToolContext, protection_event_id: str = "", protection_plan_id: str = "", customer_id: str = "", loan_id: str = "", related_event_id: str = "", protection_claim_id: str = "") -> str:
    """List the entries on a Payment Protection plan.

    Entries include monthly protection fees, fee refunds with their basis, benefits paid to the loan for a
    coverage month, benefit reversals, and claim documents received. Search by the entry reference, the plan, the
    borrower, the loan, the entry acted on or the claim; every criterion is optional.

    Args:
        protection_event_id: Reference number of the plan entry. Leave "" if unknown.
        protection_plan_id: Reference number of the Payment Protection plan. Leave "" if unknown.
        customer_id: Customer reference number of the borrower. Leave "" if unknown.
        loan_id: Reference number of the protected personal loan. Leave "" if unknown.
        related_event_id: Reference number of the entry acted on. Leave "" if unknown.
        protection_claim_id: Reference number of the benefit claim. Leave "" if unknown.
    """
    match = {k: v for k, v in {"protection_event_id": protection_event_id,
                               "protection_plan_id": protection_plan_id,
                               "customer_id": customer_id,
                               "loan_id": loan_id,
                               "related_event_id": related_event_id,
                               "protection_claim_id": protection_claim_id}.items() if v}
    rows = ctx.find("protection_events", **match)
    return str(rows) if rows else f"No Payment Protection entries found for {match}."


@tool(owner="agent", rw="read")
def find_protection_claims(ctx: ToolContext, protection_claim_id: str = "", customer_id: str = "", protection_plan_id: str = "") -> str:
    """Check benefit claims filed under Payment Protection plans.

    Each claim shows the type of loss, the loss date, the filing date, the claim status and any approved monthly
    benefit. Search by the claim reference, the borrower or the plan; every criterion is optional.

    Args:
        protection_claim_id: Reference number of the benefit claim. Leave "" if unknown.
        customer_id: Customer reference number of the borrower. Leave "" if unknown.
        protection_plan_id: Reference number of the Payment Protection plan. Leave "" if unknown.
    """
    match = {k: v for k, v in {"protection_claim_id": protection_claim_id,
                               "customer_id": customer_id,
                               "protection_plan_id": protection_plan_id}.items() if v}
    rows = ctx.find("protection_claims", **match)
    return str(rows) if rows else f"No Payment Protection claims found for {match}."


@tool(owner="agent", rw="read")
def find_card_accounts(ctx: ToolContext, card_account_id: str = "", customer_id: str = "") -> str:
    """Retrieve Larkspur credit card accounts.

    An account record shows the card product, status, application and opening dates, card number last four,
    credit limit and any security deposit, the purchase APR and whether the penalty APR applies, the balance,
    unredeemed cash-back rewards, the statement closing and payment due days, the minimum payment, the payment
    due date, the amount past due, AutoPay and closing details. Search by the account reference or the
    cardholder; every criterion is optional.

    Args:
        card_account_id: Reference number of the card account. Leave "" if unknown.
        customer_id: Customer reference number of the cardholder. Leave "" if unknown.
    """
    match = {k: v for k, v in {"card_account_id": card_account_id,
                               "customer_id": customer_id}.items() if v}
    rows = ctx.find("card_accounts", **match)
    return str(rows) if rows else f"No card accounts found for {match}."


@tool(owner="agent", rw="read")
def find_card_transactions(ctx: ToolContext, card_txn_id: str = "", card_account_id: str = "", customer_id: str = "", bank_account_id: str = "", related_txn_id: str = "") -> str:
    """List the entries posted to Larkspur credit card accounts.

    Entries include purchases and merchant credits (with the merchant descriptor and rewards category), cash
    advances, balance transfers and their promotional offer, interest, annual, late, returned-payment and
    foreign transaction fees, fee reversals, payments and returned payments, and rewards earned or redeemed.
    Search by the entry reference, the account, the cardholder, the bank account or the entry acted on; every
    criterion is optional.

    Args:
        card_txn_id: Reference number of the card entry. Leave "" if unknown.
        card_account_id: Reference number of the card account. Leave "" if unknown.
        customer_id: Customer reference number of the cardholder. Leave "" if unknown.
        bank_account_id: Reference number of the linked bank account of a payment. Leave "" if unknown.
        related_txn_id: Reference number of the entry acted on. Leave "" if unknown.
    """
    match = {k: v for k, v in {"card_txn_id": card_txn_id,
                               "card_account_id": card_account_id,
                               "customer_id": customer_id,
                               "bank_account_id": bank_account_id,
                               "related_txn_id": related_txn_id}.items() if v}
    rows = ctx.find("card_transactions", **match)
    return str(rows) if rows else f"No card entries found for {match}."


@tool(owner="agent", rw="read")
def find_identity_verifications(ctx: ToolContext, verification_id: str = "", customer_id: str = "") -> str:
    """Check whether a caller's identity has already been verified on this contact.

    The record shows whether verification passed and when the latest attempt was made. Search by the record
    reference or the customer; every criterion is optional.

    Args:
        verification_id: Reference number of the verification record. Leave "" if unknown.
        customer_id: Customer reference number. Leave "" if unknown.
    """
    match = {k: v for k, v in {"verification_id": verification_id,
                               "customer_id": customer_id}.items() if v}
    rows = ctx.find("identity_verifications", **match)
    return str(rows) if rows else f"No verification records found for {match}."


@tool(owner="agent", rw="read")
def find_agent_handoffs(ctx: ToolContext, handoff_id: str = "", customer_id: str = "") -> str:
    """See transfers of a customer to a human representative.

    Each record shows the reason recorded for the transfer and when it happened. Search by the transfer
    reference or the customer; every criterion is optional.

    Args:
        handoff_id: Reference number of the transfer record. Leave "" if unknown.
        customer_id: Customer reference number. Leave "" if unknown.
    """
    match = {k: v for k, v in {"handoff_id": handoff_id,
                               "customer_id": customer_id}.items() if v}
    rows = ctx.find("agent_handoffs", **match)
    return str(rows) if rows else f"No human-handoff records found for {match}."


@tool(owner="agent", rw="write")
def verify_customer_identity(ctx: ToolContext, customer_id: str, phone_number: str = "", email: str = "",
                             date_of_birth: str = "", ssn_last4: str = "", zip_code: str = "") -> str:
    """Verify the caller's identity against the customer profile and record the outcome.

    No account details may be discussed and no loan, payment or account change may be made until verification
    has passed. The comparison is done by this tool: each piece of identity information the caller states is
    checked against the profile, and verification passes only when at least 3 of them match. The customer
    reference number only identifies which profile to check against and never counts as a match. Callers usually
    give only some details, so pass exactly what the caller said and leave the rest blank. The outcome is kept on
    record; if an attempt fails and a later attempt with more details passes, the pass stands.

    Args:
        customer_id: Customer reference number read from the customer profile lookup. Required; used only to
            open that profile and never counted as a match.
        phone_number: Mobile number the caller states, 10 digits with no punctuation (e.g. 6125550148); leave "" if not stated.
        email: Email address the caller states, exactly as given; leave "" if not stated.
        date_of_birth: Date of birth the caller states, as YYYY-MM-DD; leave "" if not stated.
        ssn_last4: Last four digits of the Social Security number the caller states, 4 digits; leave "" if not stated.
        zip_code: ZIP code of the residential address the caller states, 5 digits; leave "" if not stated.
    """
    if not customer_id:
        return "Error: customer_id is required; find the customer profile first and pass its reference number."
    rows = ctx.find("customers", customer_id=customer_id)
    if not rows:
        return f"Error: no customer {customer_id}; cannot verify."
    rec = rows[0]
    # The tool owns the comparison; the locator customer_id is deliberately not a credential.
    supplied = {"phone_number": phone_number, "email": email, "date_of_birth": date_of_birth,
                "ssn_last4": ssn_last4, "zip_code": zip_code}
    matched = sum(1 for field, value in supplied.items()
                  if value and str(rec.get(field, "")).strip().lower() == str(value).strip().lower())
    verified = matched >= 3
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
            else f"Identity NOT verified for {customer_id} (only {matched} of the required 3 details matched). "
                 "Ask the caller for another detail on file and try again.")


@tool(owner="agent", rw="write")
def transfer_to_human_agent(ctx: ToolContext, customer_id: str, reason: str) -> str:
    """Transfer the customer to a human Larkspur representative and record why.

    Use this in exactly two situations: when no Larkspur policy can resolve what the customer is asking for,
    or when the customer has explicitly asked to speak with a person 2 times. The reason must be one of the two
    values below, never free text.

    Args:
        customer_id: Customer reference number read from the customer profile lookup (the profile must exist).
        reason: Why the customer is being transferred; exactly one of:
            POLICY_NOT_COVERED - no current policy offers a way to resolve the customer's request;
            CUSTOMER_REQUESTED - the customer has explicitly asked for a human representative at least 2 times.
    """
    allowed = {"POLICY_NOT_COVERED", "CUSTOMER_REQUESTED"}
    if reason not in allowed:
        return f"Error: unknown transfer reason '{reason}'. Valid: {', '.join(sorted(allowed))}."
    if not ctx.find("customers", customer_id=customer_id):
        return f"Error: no customer {customer_id}; cannot record the transfer."
    rid = ctx.make_id("hof_", customer_id, reason)
    ctx.create("agent_handoffs", rid, handoff_id=rid, customer_id=customer_id,
               reason=reason, created_at=ctx.now())
    return f"Transfer to a human representative recorded for {customer_id} ({reason})."

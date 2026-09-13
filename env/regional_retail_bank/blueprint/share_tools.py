"""Shared tools for regional_retail_bank (Piedmont Crescent Bank, N.A.).

Every tool here is a SHARE tool: always present in its owner's tool list and callable in every task.
This module holds exactly the three foundations every difficulty reuses:
  - the record-lookup layer: one finder per table in db_schema.json, each taking all of that table's
    `_id` fields as optional arguments; the customers finder doubles as the identity entry and also
    accepts the caller-stateable attributes phone_number, email and name;
  - the identity-verification write (verify_customer_identity), which compares the supplied
    credentials itself and passes at K = 3 matches, storing only the verified boolean;
  - the handoff write (transfer_to_human_agent), whose reason is closed at POLICY_NOT_COVERED and
    CUSTOMER_REQUESTED, with the repeat-request threshold R = 2.
Customer-initiated writes are hidden task tools in each difficulty's task_tools.py, never here.
Lookups never apply product policy; eligibility and state judgements stay with the agent.
"""

from erlbench import ToolContext, tool


def _found(rows, label, match):
    # Formatting helper only (no ctx access): uniform hit / miss wording.
    if rows:
        return str(rows)
    return f"No {label} found for {match}."


# --------------------------------------------------------------------------- identity entry

@tool(owner="agent", rw="read")
def find_customers(ctx: ToolContext, customer_id: str = "", phone_number: str = "",
                   email: str = "", name: str = "") -> str:
    """Look up a Piedmont Crescent Bank customer profile to establish whose relationship this conversation is about.

    Search by the customer reference number, or by what a caller can naturally tell you: the
    registered mobile number, the registered email address, or the full name. Every criterion is
    optional, but at least one must be given; when several are given, all of them must match. A hit
    returns the single matching profile, including the customer reference number, contact details,
    date of birth, the last four digits of the Social Security number, ZIP code, mailing address,
    state of residence, the date the profile was opened, military status and employee status. If
    more than one profile matches, ask the caller for another detail and search again. Finding a
    profile does not verify the caller's identity.

    Args:
        customer_id: The customer reference number, if already known; leave "" if unknown.
        phone_number: The registered mobile number as 10 digits with no spaces, dashes, parentheses or country code (for example 3365550142); leave "" if not provided.
        email: The registered email address exactly as the caller spells it, in lower case; leave "" if not provided.
        name: The customer's full name exactly as the caller states it (first and last name as on file); leave "" if not provided.
    """
    match = {k: v for k, v in {"customer_id": customer_id, "phone_number": phone_number,
                               "email": email, "name": name}.items() if v}
    if not match:
        return "Error: provide at least one of customer_id, phone_number, email or name to find the customer."
    rows = ctx.find("customers", **match)
    if not rows:
        return f"No customer profile matches {match}."
    if len(rows) > 1:
        return (f"Error: {len(rows)} customer profiles match {match}; ask the caller for one more "
                "detail (mobile number, email or full name) to tell them apart.")
    return str(rows[0])


# --------------------------------------------------------------------------- service logs

@tool(owner="agent", rw="read")
def find_verification_log(ctx: ToolContext, verification_id: str = "", customer_id: str = "") -> str:
    """Check whether a customer's identity has already been verified, and when the latest verification attempt was made.

    Returns the verification outcome kept for the customer: whether verification has passed and the
    moment of the most recent attempt. Search by the customer reference number or by the
    verification reference number; both are optional. If nothing is returned, no verification has
    been attempted for that customer yet.

    Args:
        verification_id: The verification reference number; leave "" if unknown.
        customer_id: The customer reference number whose verification status you want; leave "" if unknown.
    """
    match = {k: v for k, v in {"verification_id": verification_id, "customer_id": customer_id}.items() if v}
    return _found(ctx.find("verification_log", **match), "verification records", match)


@tool(owner="agent", rw="read")
def find_handoff_log(ctx: ToolContext, handoff_id: str = "", customer_id: str = "") -> str:
    """Review earlier transfers of a customer to a human representative.

    Returns each recorded handoff with its reason (POLICY_NOT_COVERED or CUSTOMER_REQUESTED) and
    when it happened. Search by the customer reference number or by a handoff reference number;
    both are optional.

    Args:
        handoff_id: The handoff reference number; leave "" if unknown.
        customer_id: The customer reference number; leave "" if unknown.
    """
    match = {k: v for k, v in {"handoff_id": handoff_id, "customer_id": customer_id}.items() if v}
    return _found(ctx.find("handoff_log", **match), "handoff records", match)


# --------------------------------------------------------------------------- personal checking

@tool(owner="agent", rw="read")
def find_checking_accounts(ctx: ToolContext, checking_account_id: str = "", customer_id: str = "",
                           overdraft_link_savings_account_id: str = "") -> str:
    """Look up personal checking accounts.

    Each account shows its tier (for example Everyday Checking or Premier Checking), status,
    last four digits of the account number, opening and closing dates, current ledger balance, the
    debit card overdraft election, the savings account linked for overdraft protection, the
    statement cycle day and delivery method, the date of the last customer-initiated activity, and
    the date the balance went negative if it is overdrawn. Use the customer reference number to
    list all of a customer's checking accounts, the account reference number for one account, or
    a savings account reference number to find the checking account it protects.

    Args:
        checking_account_id: The checking account reference number; leave "" if unknown.
        customer_id: The owner's customer reference number; leave "" if unknown.
        overdraft_link_savings_account_id: The reference number of a savings account, to find the checking account that uses it for overdraft protection; leave "" if unknown.
    """
    match = {k: v for k, v in {"checking_account_id": checking_account_id, "customer_id": customer_id,
                               "overdraft_link_savings_account_id": overdraft_link_savings_account_id}.items() if v}
    return _found(ctx.find("checking_accounts", **match), "checking accounts", match)


@tool(owner="agent", rw="read")
def find_checking_transactions(ctx: ToolContext, checking_txn_id: str = "", checking_account_id: str = "",
                               customer_id: str = "", source_item_id: str = "", checking_dispute_id: str = "",
                               counterparty_account_id: str = "") -> str:
    """Review the posted activity of checking accounts: deposits, debits, returned items, fees, refunds, interest, ATM rebates, overdraft transfers and dispute credits.

    Each entry shows its type, amount, posted date, channel, statement description, trace and check
    numbers, any ATM operator surcharge, the fee code, the statement cycle, the reason for a refund or
    credit, and the entry it relates to (for instance, the purchase that caused an overdraft fee, or
    the fee a refund reversed). Search by account or customer to see the history, by an entry's own
    reference number, by the reference number of a related entry to find what followed from it, by a
    dispute reference number, or by the other PCB account in an internal transfer.

    Args:
        checking_txn_id: The reference number of one checking entry; leave "" if unknown.
        checking_account_id: The checking account reference number; leave "" if unknown.
        customer_id: The owner's customer reference number; leave "" if unknown.
        source_item_id: The reference number of a related entry or service order, to find fees, refunds, rebates or credits that derive from it; leave "" if unknown.
        checking_dispute_id: The reference number of an electronic-transaction dispute, to find its provisional credit or reversal; leave "" if unknown.
        counterparty_account_id: The reference number of another PCB account (savings, certificate, card, loan or box rental) on the other side of a transfer; leave "" if unknown.
    """
    match = {k: v for k, v in {"checking_txn_id": checking_txn_id, "checking_account_id": checking_account_id,
                               "customer_id": customer_id, "source_item_id": source_item_id,
                               "checking_dispute_id": checking_dispute_id,
                               "counterparty_account_id": counterparty_account_id}.items() if v}
    return _found(ctx.find("checking_transactions", **match), "checking entries", match)


@tool(owner="agent", rw="read")
def find_checking_service_orders(ctx: ToolContext, service_order_id: str = "", checking_account_id: str = "",
                                 customer_id: str = "", related_order_id: str = "") -> str:
    """Look up stop payment orders, stop payment renewals and replacement debit card orders on checking accounts.

    A stop payment order shows the check number, the exact amount and payee as given by the customer,
    the order date and the date it lapses; a renewal also names the order it renewed. A card order
    shows the reason and delivery speed. Search by account, customer, an order's own reference
    number, or the reference number of an earlier order to find its renewals.

    Args:
        service_order_id: The reference number of one service order; leave "" if unknown.
        checking_account_id: The checking account reference number; leave "" if unknown.
        customer_id: The owner's customer reference number; leave "" if unknown.
        related_order_id: The reference number of an earlier stop payment order, to find renewals of it; leave "" if unknown.
    """
    match = {k: v for k, v in {"service_order_id": service_order_id, "checking_account_id": checking_account_id,
                               "customer_id": customer_id, "related_order_id": related_order_id}.items() if v}
    return _found(ctx.find("checking_service_orders", **match), "checking service orders", match)


@tool(owner="agent", rw="read")
def find_checking_disputes(ctx: ToolContext, checking_dispute_id: str = "", customer_id: str = "",
                           checking_account_id: str = "", disputed_txn_id: str = "") -> str:
    """Look up electronic-transaction disputes filed on checking accounts (debit card, ATM, ACH and Zelle claims).

    Each dispute shows the transaction disputed, the kind of error claimed, the amount claimed, the
    date the customer gave notice, its current status as maintained by the Dispute Resolution team,
    and when it was registered. Search by dispute, customer, account, or the reference number of the
    disputed transaction.

    Args:
        checking_dispute_id: The dispute reference number; leave "" if unknown.
        customer_id: The customer reference number of the person who filed it; leave "" if unknown.
        checking_account_id: The checking account reference number; leave "" if unknown.
        disputed_txn_id: The reference number of the checking entry being disputed; leave "" if unknown.
    """
    match = {k: v for k, v in {"checking_dispute_id": checking_dispute_id, "customer_id": customer_id,
                               "checking_account_id": checking_account_id,
                               "disputed_txn_id": disputed_txn_id}.items() if v}
    return _found(ctx.find("checking_disputes", **match), "checking disputes", match)


@tool(owner="agent", rw="read")
def find_checking_closure_requests(ctx: ToolContext, closure_request_id: str = "", customer_id: str = "",
                                   checking_account_id: str = "", destination_account_id: str = "") -> str:
    """Look up requests to close a checking account and how the closing balance is to be paid out.

    Each request shows the account, the payout method (official check by mail or transfer to another
    PCB account), the receiving account where there is one, whether it is awaiting the customer's
    confirmation, confirmed, completed or cancelled, and when it was registered.

    Args:
        closure_request_id: The closure request reference number; leave "" if unknown.
        customer_id: The customer reference number; leave "" if unknown.
        checking_account_id: The reference number of the checking account being closed; leave "" if unknown.
        destination_account_id: The reference number of the PCB account receiving the closing balance; leave "" if unknown.
    """
    match = {k: v for k, v in {"closure_request_id": closure_request_id, "customer_id": customer_id,
                               "checking_account_id": checking_account_id,
                               "destination_account_id": destination_account_id}.items() if v}
    return _found(ctx.find("checking_closure_requests", **match), "checking closure requests", match)


# --------------------------------------------------------------------------- savings & money market

@tool(owner="agent", rw="read")
def find_savings_accounts(ctx: ToolContext, savings_account_id: str = "", customer_id: str = "",
                          funding_checking_account_id: str = "") -> str:
    """Look up savings and money market accounts.

    Each account shows its tier (for example Statement Savings or Premier Money Market), status,
    last four digits of the account number, opening and closing dates, current balance, statement
    cycle day and delivery, date of last customer-initiated activity, any automatic monthly transfer
    and the checking account that funds it, and the end date of a new-money promotional rate. Search
    by customer, by account, or by a checking account to find the savings accounts it feeds by
    automatic transfer.

    Args:
        savings_account_id: The savings account reference number; leave "" if unknown.
        customer_id: The owner's customer reference number; leave "" if unknown.
        funding_checking_account_id: The reference number of a checking account that funds automatic transfers; leave "" if unknown.
    """
    match = {k: v for k, v in {"savings_account_id": savings_account_id, "customer_id": customer_id,
                               "funding_checking_account_id": funding_checking_account_id}.items() if v}
    return _found(ctx.find("savings_accounts", **match), "savings accounts", match)


@tool(owner="agent", rw="read")
def find_savings_transactions(ctx: ToolContext, savings_txn_id: str = "", savings_account_id: str = "",
                              customer_id: str = "", source_item_id: str = "",
                              counterparty_account_id: str = "") -> str:
    """Review the posted activity of savings and money market accounts: deposits, withdrawals, interest credits by component, fees and fee refunds.

    Each entry shows its type, amount, posted date, channel, description, trace and check numbers,
    fee code, statement cycle, interest component (base, relationship bonus, goal bonus or
    promotional), refund reason, and the entry or checking transfer it relates to. Search by account,
    customer, an entry's own reference number, a related entry, or the other PCB account in a
    transfer.

    Args:
        savings_txn_id: The reference number of one savings entry; leave "" if unknown.
        savings_account_id: The savings account reference number; leave "" if unknown.
        customer_id: The owner's customer reference number; leave "" if unknown.
        source_item_id: The reference number of a related entry (the withdrawal behind a fee, the fee behind a refund, or the checking overdraft transfer behind a withdrawal); leave "" if unknown.
        counterparty_account_id: The reference number of the other PCB account in a transfer; leave "" if unknown.
    """
    match = {k: v for k, v in {"savings_txn_id": savings_txn_id, "savings_account_id": savings_account_id,
                               "customer_id": customer_id, "source_item_id": source_item_id,
                               "counterparty_account_id": counterparty_account_id}.items() if v}
    return _found(ctx.find("savings_transactions", **match), "savings entries", match)


@tool(owner="agent", rw="read")
def find_savings_requests(ctx: ToolContext, savings_request_id: str = "", customer_id: str = "",
                          savings_account_id: str = "", destination_account_id: str = "") -> str:
    """Look up pending and past savings service requests: account closures and automatic transfer instructions.

    Each request shows its type, payout method and receiving account for a closure, the transfer
    amount and day for an automatic transfer instruction, its progress, and when it was registered.

    Args:
        savings_request_id: The request reference number; leave "" if unknown.
        customer_id: The customer reference number; leave "" if unknown.
        savings_account_id: The savings account reference number; leave "" if unknown.
        destination_account_id: The reference number of the PCB account receiving a closing balance; leave "" if unknown.
    """
    match = {k: v for k, v in {"savings_request_id": savings_request_id, "customer_id": customer_id,
                               "savings_account_id": savings_account_id,
                               "destination_account_id": destination_account_id}.items() if v}
    return _found(ctx.find("savings_requests", **match), "savings requests", match)


# --------------------------------------------------------------------------- certificates of deposit

@tool(owner="agent", rw="read")
def find_cd_certificates(ctx: ToolContext, certificate_id: str = "", customer_id: str = "",
                         payout_account_id: str = "") -> str:
    """Look up certificates of deposit.

    Each certificate shows its term tier (for example 12-Month Certificate or 18-Month Bump-Up
    Certificate), status (including the grace period after maturity), last four digits of the
    certificate number, opening and closing dates, principal balance, the rate and APY of the current
    term and whether jumbo or relationship bonuses are included, term start and maturity dates, the
    maturity instruction, where interest goes, the payout account, whether the bump-up has been used,
    and how many times it has renewed. Search by customer, certificate, or the account that receives
    its interest or proceeds.

    Args:
        certificate_id: The certificate reference number; leave "" if unknown.
        customer_id: The owner's customer reference number; leave "" if unknown.
        payout_account_id: The reference number of the checking or savings account receiving interest or proceeds; leave "" if unknown.
    """
    match = {k: v for k, v in {"certificate_id": certificate_id, "customer_id": customer_id,
                               "payout_account_id": payout_account_id}.items() if v}
    return _found(ctx.find("cd_certificates", **match), "certificates", match)


@tool(owner="agent", rw="read")
def find_cd_transactions(ctx: ToolContext, cd_txn_id: str = "", certificate_id: str = "", customer_id: str = "",
                         counterparty_account_id: str = "", source_item_id: str = "") -> str:
    """Review certificate activity: deposits and add-ons, interest compounded or paid out, withdrawals by kind, early withdrawal penalties and penalty reversals.

    Each entry shows its type, amount, date, deposit kind and funding source, the interest period
    and rate used, the withdrawal kind and destination, penalty days, and the entry it relates to
    (the withdrawal behind a penalty, or the penalty behind a reversal). Search by certificate,
    customer, an entry's own reference number, a related entry, or the PCB account funds came from or
    went to.

    Args:
        cd_txn_id: The reference number of one certificate entry; leave "" if unknown.
        certificate_id: The certificate reference number; leave "" if unknown.
        customer_id: The owner's customer reference number; leave "" if unknown.
        counterparty_account_id: The reference number of the checking or savings account on the other side; leave "" if unknown.
        source_item_id: The reference number of a related entry (a withdrawal to find its penalty, or a penalty to find its reversal); leave "" if unknown.
    """
    match = {k: v for k, v in {"cd_txn_id": cd_txn_id, "certificate_id": certificate_id, "customer_id": customer_id,
                               "counterparty_account_id": counterparty_account_id,
                               "source_item_id": source_item_id}.items() if v}
    return _found(ctx.find("cd_transactions", **match), "certificate entries", match)


@tool(owner="agent", rw="read")
def find_cd_requests(ctx: ToolContext, cd_request_id: str = "", customer_id: str = "", certificate_id: str = "",
                     destination_account_id: str = "") -> str:
    """Look up certificate service requests: early or grace-period withdrawals, renewal term changes, instruction changes and bump-up requests.

    Each request shows its type, the withdrawal kind and amount, where proceeds go, any tier asked
    for at renewal, whether it awaits the owner's confirmation or is confirmed, completed or
    cancelled, and when it was registered.

    Args:
        cd_request_id: The request reference number; leave "" if unknown.
        customer_id: The customer reference number; leave "" if unknown.
        certificate_id: The certificate reference number; leave "" if unknown.
        destination_account_id: The reference number of the PCB account receiving proceeds; leave "" if unknown.
    """
    match = {k: v for k, v in {"cd_request_id": cd_request_id, "customer_id": customer_id,
                               "certificate_id": certificate_id,
                               "destination_account_id": destination_account_id}.items() if v}
    return _found(ctx.find("cd_requests", **match), "certificate requests", match)


# --------------------------------------------------------------------------- credit cards

@tool(owner="agent", rw="read")
def find_card_accounts(ctx: ToolContext, card_account_id: str = "", customer_id: str = "",
                       autopay_source_account_id: str = "") -> str:
    """Look up personal credit card accounts.

    Each account shows its card (for example Cash Rewards Visa or Travel Rewards Visa Signature),
    status, last four digits of the card, opening and closing dates, credit limit and current balance,
    purchase and cash advance APRs, whether the penalty APR or the military rate cap applies, the
    balance transfer introductory end date, the latest statement's closing date, balance, minimum
    payment and due date, days past due, the autopay instruction and paying account, rewards points,
    any security deposit, and the date of the last credit limit increase. Search by customer, card
    account, or the checking account that pays it by autopay.

    Args:
        card_account_id: The card account reference number; leave "" if unknown.
        customer_id: The cardholder's customer reference number; leave "" if unknown.
        autopay_source_account_id: The reference number of the checking account paying the card automatically; leave "" if unknown.
    """
    match = {k: v for k, v in {"card_account_id": card_account_id, "customer_id": customer_id,
                               "autopay_source_account_id": autopay_source_account_id}.items() if v}
    return _found(ctx.find("card_accounts", **match), "card accounts", match)


@tool(owner="agent", rw="read")
def find_card_transactions(ctx: ToolContext, card_txn_id: str = "", card_account_id: str = "", customer_id: str = "",
                           source_item_id: str = "", counterparty_account_id: str = "",
                           card_dispute_id: str = "") -> str:
    """Review credit card activity: purchases, cash advances, balance transfers, fees, interest, payments, returned payments, merchant credits, reversals, dispute credits and rebills, and rewards earned, redeemed or forfeited.

    Each entry shows its type, amount, posted and transaction dates, merchant and merchant category,
    whether it was a foreign transaction, the reference number, statement cycle and statement date,
    fee code, interest balance type, payment source, adjustment reason, rewards points and
    redemption type, and the entry it relates to. Search by card account, customer, an entry's own
    reference number, a related entry (for example a purchase to find its fees or points), the PCB
    account that paid or received funds, or a dispute reference number.

    Args:
        card_txn_id: The reference number of one card entry; leave "" if unknown.
        card_account_id: The card account reference number; leave "" if unknown.
        customer_id: The cardholder's customer reference number; leave "" if unknown.
        source_item_id: The reference number of a related entry, to find what derives from it; leave "" if unknown.
        counterparty_account_id: The reference number of a PCB checking or savings account that paid the card or received a redemption; leave "" if unknown.
        card_dispute_id: The billing dispute reference number, to find its credits or rebill; leave "" if unknown.
    """
    match = {k: v for k, v in {"card_txn_id": card_txn_id, "card_account_id": card_account_id,
                               "customer_id": customer_id, "source_item_id": source_item_id,
                               "counterparty_account_id": counterparty_account_id,
                               "card_dispute_id": card_dispute_id}.items() if v}
    return _found(ctx.find("card_transactions", **match), "card entries", match)


@tool(owner="agent", rw="read")
def find_card_disputes(ctx: ToolContext, card_dispute_id: str = "", customer_id: str = "", card_account_id: str = "",
                       disputed_txn_id: str = "") -> str:
    """Look up credit card billing disputes.

    Each dispute shows the charge disputed, the kind of billing error claimed, the amount claimed,
    the date the cardholder gave notice, its status as maintained by the Card Disputes team, and
    when it was registered. Search by dispute, customer, card account or the disputed charge.

    Args:
        card_dispute_id: The dispute reference number; leave "" if unknown.
        customer_id: The cardholder's customer reference number; leave "" if unknown.
        card_account_id: The card account reference number; leave "" if unknown.
        disputed_txn_id: The reference number of the card entry being disputed; leave "" if unknown.
    """
    match = {k: v for k, v in {"card_dispute_id": card_dispute_id, "customer_id": customer_id,
                               "card_account_id": card_account_id, "disputed_txn_id": disputed_txn_id}.items() if v}
    return _found(ctx.find("card_disputes", **match), "card disputes", match)


@tool(owner="agent", rw="read")
def find_card_requests(ctx: ToolContext, card_request_id: str = "", customer_id: str = "",
                       card_account_id: str = "") -> str:
    """Look up credit card service requests: closures, credit limit increases and decreases, card product changes and autopay changes.

    Each request shows its type, the limit or card asked for, whether the cardholder consented to a
    credit inquiry, its progress and when it was registered.

    Args:
        card_request_id: The request reference number; leave "" if unknown.
        customer_id: The cardholder's customer reference number; leave "" if unknown.
        card_account_id: The card account reference number; leave "" if unknown.
    """
    match = {k: v for k, v in {"card_request_id": card_request_id, "customer_id": customer_id,
                               "card_account_id": card_account_id}.items() if v}
    return _found(ctx.find("card_requests", **match), "card requests", match)


# --------------------------------------------------------------------------- auto loans

@tool(owner="agent", rw="read")
def find_auto_loans(ctx: ToolContext, auto_loan_id: str = "", customer_id: str = "",
                    autopay_source_account_id: str = "") -> str:
    """Look up auto loans.

    Each loan shows its product (for example New Vehicle Loan or Auto Refinance Loan), status, last
    four digits of the loan number, application, funding and closing dates, amount financed, unpaid
    principal and fees, credit grade, APR and the discounts in it, term, monthly payment, due day,
    next due date, maturity date, last payment date, days past due, the vehicle's VIN, year and make
    and model, autopay enrollment and paying account, extensions used and the last extension date,
    the last due date change, GAP coverage and its charge and cancellation date, and the lien status.
    Search by customer, loan, or the checking account that pays it by autopay.

    Args:
        auto_loan_id: The auto loan reference number; leave "" if unknown.
        customer_id: The borrower's customer reference number; leave "" if unknown.
        autopay_source_account_id: The reference number of the checking account paying the loan automatically; leave "" if unknown.
    """
    match = {k: v for k, v in {"auto_loan_id": auto_loan_id, "customer_id": customer_id,
                               "autopay_source_account_id": autopay_source_account_id}.items() if v}
    return _found(ctx.find("auto_loans", **match), "auto loans", match)


@tool(owner="agent", rw="read")
def find_auto_transactions(ctx: ToolContext, auto_txn_id: str = "", auto_loan_id: str = "", customer_id: str = "",
                           counterparty_account_id: str = "", source_item_id: str = "") -> str:
    """Review auto loan activity: the funding disbursement, payments and how each was split among fees, interest and principal, fees assessed, fee settlements and waivers, returned payments, charge-offs and GAP refunds.

    Each entry shows its type, amount, date, payment channel and type, the fees, interest and
    principal portions, the installment it applies to, the reference number, fee code, waiver
    reason, refund destination, and the entry it relates to. Search by loan, customer, an entry's own
    reference number, a related entry (a payment to find its fee settlement or reversal, a fee to
    find its waiver), or the PCB account that paid or received funds.

    Args:
        auto_txn_id: The reference number of one loan entry; leave "" if unknown.
        auto_loan_id: The auto loan reference number; leave "" if unknown.
        customer_id: The borrower's customer reference number; leave "" if unknown.
        counterparty_account_id: The reference number of the PCB checking account that paid or received funds; leave "" if unknown.
        source_item_id: The reference number of a related entry, to find what derives from it; leave "" if unknown.
    """
    match = {k: v for k, v in {"auto_txn_id": auto_txn_id, "auto_loan_id": auto_loan_id, "customer_id": customer_id,
                               "counterparty_account_id": counterparty_account_id,
                               "source_item_id": source_item_id}.items() if v}
    return _found(ctx.find("auto_transactions", **match), "auto loan entries", match)


@tool(owner="agent", rw="read")
def find_auto_requests(ctx: ToolContext, auto_request_id: str = "", customer_id: str = "",
                       auto_loan_id: str = "") -> str:
    """Look up auto loan service requests: payment extensions, due date changes, payoff quotes, GAP cancellations and autopay changes.

    Each request shows its type, the due day or number of installments or payoff date asked for,
    whether it awaits the borrower's signature or confirmation, and when it was registered.

    Args:
        auto_request_id: The request reference number; leave "" if unknown.
        customer_id: The borrower's customer reference number; leave "" if unknown.
        auto_loan_id: The auto loan reference number; leave "" if unknown.
    """
    match = {k: v for k, v in {"auto_request_id": auto_request_id, "customer_id": customer_id,
                               "auto_loan_id": auto_loan_id}.items() if v}
    return _found(ctx.find("auto_requests", **match), "auto loan requests", match)


# --------------------------------------------------------------------------- home mortgages

@tool(owner="agent", rw="read")
def find_mortgage_loans(ctx: ToolContext, mortgage_loan_id: str = "", customer_id: str = "") -> str:
    """Look up home mortgage loans serviced by PCB.

    Each loan shows its program (for example Conventional 30-Year Fixed Mortgage or 7/6 SOFR
    Adjustable-Rate Mortgage), status, loan number digits, key dates, property address and occupancy,
    original amount and property value, unpaid principal, escrow balance and fees due, note rate,
    principal-and-interest and escrow payments, whether escrow was waived, mortgage insurance premium
    and status, next due and maturity dates, the next rate change date, days past due, forbearance
    dates and months used, and the last escrow analysis and recast dates.

    Args:
        mortgage_loan_id: The mortgage loan reference number; leave "" if unknown.
        customer_id: The borrower's customer reference number; leave "" if unknown.
    """
    match = {k: v for k, v in {"mortgage_loan_id": mortgage_loan_id, "customer_id": customer_id}.items() if v}
    return _found(ctx.find("mortgage_loans", **match), "mortgage loans", match)


@tool(owner="agent", rw="read")
def find_mortgage_transactions(ctx: ToolContext, mortgage_txn_id: str = "", mortgage_loan_id: str = "",
                               customer_id: str = "", counterparty_account_id: str = "",
                               source_item_id: str = "") -> str:
    """Review mortgage activity: the closing disbursement, payments split among interest, principal, escrow and fees, escrow deposits, tax and insurance disbursements, escrow refunds, fees and waivers.

    Each entry shows its type, amount, date, payment type and channel, the portions, the installment
    it applies to, the payee of an escrow disbursement, the reason and destination of an escrow
    refund, the fee code and waiver reason, and the entry it relates to.

    Args:
        mortgage_txn_id: The reference number of one mortgage entry; leave "" if unknown.
        mortgage_loan_id: The mortgage loan reference number; leave "" if unknown.
        customer_id: The borrower's customer reference number; leave "" if unknown.
        counterparty_account_id: The reference number of the PCB checking account that paid or received funds; leave "" if unknown.
        source_item_id: The reference number of a related entry, to find what derives from it; leave "" if unknown.
    """
    match = {k: v for k, v in {"mortgage_txn_id": mortgage_txn_id, "mortgage_loan_id": mortgage_loan_id,
                               "customer_id": customer_id, "counterparty_account_id": counterparty_account_id,
                               "source_item_id": source_item_id}.items() if v}
    return _found(ctx.find("mortgage_transactions", **match), "mortgage entries", match)


@tool(owner="agent", rw="read")
def find_mortgage_requests(ctx: ToolContext, mortgage_request_id: str = "", customer_id: str = "",
                           mortgage_loan_id: str = "") -> str:
    """Look up mortgage service requests: mortgage insurance cancellations, forbearance, recasts, payoff statements and escrow waivers.

    Each request shows its type, the hardship stated and months asked for in a forbearance request,
    its progress and when it was registered.

    Args:
        mortgage_request_id: The request reference number; leave "" if unknown.
        customer_id: The borrower's customer reference number; leave "" if unknown.
        mortgage_loan_id: The mortgage loan reference number; leave "" if unknown.
    """
    match = {k: v for k, v in {"mortgage_request_id": mortgage_request_id, "customer_id": customer_id,
                               "mortgage_loan_id": mortgage_loan_id}.items() if v}
    return _found(ctx.find("mortgage_requests", **match), "mortgage requests", match)


# --------------------------------------------------------------------------- safe deposit boxes

@tool(owner="agent", rw="read")
def find_safebox_rentals(ctx: ToolContext, safebox_rental_id: str = "", customer_id: str = "",
                         autopay_checking_account_id: str = "") -> str:
    """Look up safe deposit box reservations and leases.

    Each rental shows the box size (for example 3x10 Safe Deposit Box), status (waitlisted, active,
    past due, pending drilling or closed), branch, box number, reservation, offer, lease start and
    closing dates, the next rent due date, the amount due, keys issued and returned, the co-lessee
    and deputies on file, the checking account paying rent automatically, and the date of any
    drilling notice.

    Args:
        safebox_rental_id: The box rental reference number; leave "" if unknown.
        customer_id: The lessee's customer reference number; leave "" if unknown.
        autopay_checking_account_id: The reference number of the checking account paying rent automatically; leave "" if unknown.
    """
    match = {k: v for k, v in {"safebox_rental_id": safebox_rental_id, "customer_id": customer_id,
                               "autopay_checking_account_id": autopay_checking_account_id}.items() if v}
    return _found(ctx.find("safebox_rentals", **match), "safe deposit box rentals", match)


@tool(owner="agent", rw="read")
def find_safebox_transactions(ctx: ToolContext, safebox_txn_id: str = "", safebox_rental_id: str = "",
                              customer_id: str = "", counterparty_account_id: str = "",
                              source_item_id: str = "") -> str:
    """Review safe deposit box charges and payments: annual rent with the discount applied, payments, late fees, service fees and credits.

    Each entry shows its type, amount, date, the rental year it covers, the discount type and
    percent, the payment method and reference number, the service performed, the reason for a credit
    and where any refund went, and the charge a credit offsets.

    Args:
        safebox_txn_id: The reference number of one box rental entry; leave "" if unknown.
        safebox_rental_id: The box rental reference number; leave "" if unknown.
        customer_id: The lessee's customer reference number; leave "" if unknown.
        counterparty_account_id: The reference number of the PCB checking account that paid or received funds; leave "" if unknown.
        source_item_id: The reference number of a charge, to find the credits against it; leave "" if unknown.
    """
    match = {k: v for k, v in {"safebox_txn_id": safebox_txn_id, "safebox_rental_id": safebox_rental_id,
                               "customer_id": customer_id, "counterparty_account_id": counterparty_account_id,
                               "source_item_id": source_item_id}.items() if v}
    return _found(ctx.find("safebox_transactions", **match), "safe deposit box entries", match)


@tool(owner="agent", rw="read")
def find_safebox_access_log(ctx: ToolContext, access_id: str = "", safebox_rental_id: str = "",
                            customer_id: str = "") -> str:
    """Review the vault entry log of a safe deposit box: who opened the box, in what capacity, and when.

    Each entry shows the date and time of the visit, whether the person was the lessee, a co-lessee or
    a deputy, and the name exactly as on the identification presented.

    Args:
        access_id: The reference number of one vault entry; leave "" if unknown.
        safebox_rental_id: The box rental reference number; leave "" if unknown.
        customer_id: The lessee's customer reference number; leave "" if unknown.
    """
    match = {k: v for k, v in {"access_id": access_id, "safebox_rental_id": safebox_rental_id,
                               "customer_id": customer_id}.items() if v}
    return _found(ctx.find("safebox_access_log", **match), "vault entries", match)


@tool(owner="agent", rw="read")
def find_safebox_requests(ctx: ToolContext, safebox_request_id: str = "", customer_id: str = "",
                          safebox_rental_id: str = "") -> str:
    """Look up safe deposit box service requests: reservation cancellations, surrenders, access list changes, size changes, autopay changes and lost keys.

    Each request shows its type, any box size asked for, its progress and when it was registered.

    Args:
        safebox_request_id: The request reference number; leave "" if unknown.
        customer_id: The lessee's customer reference number; leave "" if unknown.
        safebox_rental_id: The box rental reference number; leave "" if unknown.
    """
    match = {k: v for k, v in {"safebox_request_id": safebox_request_id, "customer_id": customer_id,
                               "safebox_rental_id": safebox_rental_id}.items() if v}
    return _found(ctx.find("safebox_requests", **match), "safe deposit box requests", match)


# --------------------------------------------------------------------------- identity verification

@tool(owner="agent", rw="write")
def verify_customer_identity(ctx: ToolContext, customer_id: str, phone_number: str = "", email: str = "",
                             date_of_birth: str = "", ssn_last4: str = "", postal_code: str = "",
                             customer_since: str = "") -> str:
    """Verify the caller's identity against the customer profile and record the outcome; identity must be verified before any account information is discussed or any money is moved.

    This tool performs the comparison itself: it checks each piece of identifying information the
    caller has stated against the profile on file, counts how many match exactly, and verifies the
    caller only when at least 3 of them match. The customer reference number is used only to open the
    profile and never counts as a match, and a name alone is never accepted as proof of identity.
    Callers usually state only some of these details, so pass only the values the caller actually
    gave, exactly as given in the formats below, and leave the rest empty. The outcome is recorded;
    if a first attempt falls short and a later attempt with more details succeeds, the successful
    verification stands and is never undone.

    Args:
        customer_id: The customer reference number, taken from the customer profile lookup. Required; used only to open the profile and not counted as a match.
        phone_number: The registered mobile number stated by the caller, as 10 digits with no punctuation (for example 3365550142); leave "" if not stated.
        email: The registered email address stated by the caller, in lower case; leave "" if not stated.
        date_of_birth: The caller's date of birth in YYYY-MM-DD form (for example 1984-07-19); leave "" if not stated.
        ssn_last4: The last four digits of the caller's Social Security number, exactly four digits with leading zeros kept (for example 0417); leave "" if not stated.
        postal_code: The 5-digit ZIP code of the residential address on file; leave "" if not stated.
        customer_since: The date the caller first became a PCB customer, in YYYY-MM-DD form, as the caller states it; leave "" if not stated.
    """
    if not customer_id:
        return "Error: customer_id is required; look up the customer profile first and pass its customer reference number."
    rows = ctx.find("customers", customer_id=customer_id)
    if not rows:
        return f"Error: no customer profile {customer_id}; cannot verify."
    rec = rows[0]
    # The tool owns the comparison; the locator customer_id is deliberately not a credential.
    supplied = {"phone_number": phone_number, "email": email, "date_of_birth": date_of_birth,
                "ssn_last4": ssn_last4, "postal_code": postal_code, "customer_since": customer_since}
    matched = sum(1 for field, value in supplied.items() if value and str(rec.get(field)) == str(value))
    verified = matched >= 3
    rid = ctx.make_id("ver_", customer_id)
    # Store only the reproducible boolean; upsert keyed on the customer and never downgrade True -> False.
    prior = ctx.find("verification_log", verification_id=rid)
    verified = verified or bool(prior and prior[0].get("verified"))
    if prior:
        ctx.update("verification_log", rid, verified=verified, verified_at=ctx.now())
    else:
        ctx.create("verification_log", rid, verification_id=rid, customer_id=customer_id,
                   verified=verified, verified_at=ctx.now())
    if verified:
        return f"Identity verified for customer {customer_id} ({matched} detail(s) matched this attempt)."
    return (f"Identity NOT verified for customer {customer_id}: only {matched} of the required 3 details "
            "matched. Ask the caller for another detail on file and call this tool again.")


# --------------------------------------------------------------------------- human handoff

@tool(owner="agent", rw="write")
def transfer_to_human_agent(ctx: ToolContext, customer_id: str, reason: str) -> str:
    """Transfer the customer to a human Piedmont Crescent Bank representative and record why.

    Use this in exactly one of two situations. The first is when no published PCB policy provides a
    way to resolve what the customer is asking for. The second is when the customer has explicitly
    asked to speak with a human representative at least 2 times in this conversation. The customer
    is told a representative will continue the conversation.

    Args:
        customer_id: The customer reference number, taken from the customer profile lookup; the profile must exist.
        reason: Exactly one of two values, never free text. POLICY_NOT_COVERED means no current PCB policy offers a way to resolve the request; CUSTOMER_REQUESTED means the customer has explicitly asked for a human representative at least 2 times.
    """
    allowed = {"POLICY_NOT_COVERED", "CUSTOMER_REQUESTED"}
    if reason not in allowed:
        return f"Error: unknown handoff reason '{reason}'. Valid values: {', '.join(sorted(allowed))}."
    if not ctx.find("customers", customer_id=customer_id):
        return f"Error: no customer profile {customer_id}; cannot record the handoff."
    rid = ctx.make_id("hof_", customer_id, reason)
    ctx.create("handoff_log", rid, handoff_id=rid, customer_id=customer_id, reason=reason, created_at=ctx.now())
    return f"Handoff to a human representative recorded for customer {customer_id} ({reason})."

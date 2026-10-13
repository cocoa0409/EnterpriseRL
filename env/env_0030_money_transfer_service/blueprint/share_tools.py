"""Shared tools for env_0030_money_transfer_service (Paloma Remit customer care).
Output of the erl-scenario-blueprint skill.

Every tool here is a SHARE tool, always present for its owner in every task:
  - one lookup per record type (the customers lookup doubles as the identity entry, taking the
    attributes a caller can state);
  - the identity-verification write (compares the stated attributes itself; passes at 3 matches);
  - the transfer-to-human write (exactly two reasons; CUSTOMER_REQUESTED after 2 explicit requests).
Customer-only actions (booking, cancelling, choosing a remedy, closing, appealing) are hidden task
tools authored per difficulty, never here.
"""

from erlbench import ToolContext, tool


def _criteria(criteria: dict) -> dict:
    # Drop blank criteria so only the reference numbers actually supplied filter the search.
    return {k: v for k, v in criteria.items() if v}


def _report(rows: list, match: dict, what: str) -> str:
    return str(rows) if rows else f"No {what} found for {match}."


# ----------------------------------------------------------------------------- customers & world

@tool(owner="agent", rw="read")
def find_customers(ctx: ToolContext, customer_id: str = "", full_name: str = "", phone: str = "",
                   email: str = "") -> str:
    """Look up a Paloma customer profile to establish whose account this call is about.

    Search by the customer reference number, or by what a caller naturally states: their full
    name, registered mobile number or registered email address. Every criterion is optional;
    supply whichever you have, and add another one when several profiles match. The profile
    returned shows the customer reference number, full legal name, mobile number, email, date of
    birth, ZIP code, last four characters of the photo ID on file, state of residence and the date
    the profile was created. Finding a profile does not verify the caller's identity.

    Args:
        customer_id: Customer reference number, if already known; leave "" otherwise.
        full_name: The caller's full name as they state it; leave "" if not given.
        phone: Registered US mobile number as the caller states it (10 digits); leave "" if not given.
        email: Registered email address as the caller states it; leave "" if not given.
    """
    match = {k: v for k, v in {"customer_id": customer_id, "full_name": full_name,
                               "phone": phone, "email": email}.items() if v}
    if not match:
        return "Error: provide at least one reference number or attribute to find the customer."
    rows = ctx.fuzzy_find("customers", **match)
    if not rows:
        return f"No customer matches {match}."
    if len(rows) > 1:
        return (f"Error: {len(rows)} customers match {match}; ask the caller for one more "
                "attribute to tell them apart.")
    return str(rows[0])


@tool(owner="agent", rw="read")
def find_recipients(ctx: ToolContext, recipient_id: str = "", customer_id: str = "") -> str:
    """Look up the recipients a customer has saved for sending money abroad.

    Each saved recipient shows the recipient's name, destination corridor (country and payout
    currency), relationship to the sender, whether the recipient is active or removed, saved bank
    details, saved mobile wallet, phone, city and the date the recipient was added. Search by the
    recipient reference number or by the customer reference number to list everyone the customer
    has saved.

    Args:
        recipient_id: Recipient reference number; leave "" if unknown.
        customer_id: Reference number of the customer who saved the recipients; leave "" if unknown.
    """
    match = _criteria({"recipient_id": recipient_id, "customer_id": customer_id})
    if not match:
        return "Error: give at least one reference number to look up saved recipients."
    return _report(ctx.find("recipients", **match), match, "saved recipients")


@tool(owner="agent", rw="read")
def find_fx_rate_sheet(ctx: ToolContext, rate_id: str = "", corridor: str = "",
                       rate_date: str = "") -> str:
    """Read Paloma's daily rate sheet of mid-market exchange rates.

    Each line gives, for one corridor and one business date, the mid-market reference rate in
    payout-currency units per 1 US dollar, before any Paloma margin. Narrow the sheet by corridor
    and date; with no criteria the whole sheet is returned.

    Args:
        rate_id: Reference number of one rate line; leave "" if unknown.
        corridor: Corridor code such as MX-MXN or PH-PHP; leave "" for every corridor.
        rate_date: Business date in YYYY-MM-DD; leave "" for every date.
    """
    match = {k: v for k, v in {"rate_id": rate_id, "corridor": corridor,
                               "rate_date": rate_date}.items() if v}
    rows = ctx.find("fx_rate_sheet", **match)
    return str(rows) if rows else f"No rate-sheet lines found for {match}."


# ----------------------------------------------------------------- Personal Sender Account

@tool(owner="agent", rw="read")
def find_sender_accounts(ctx: ToolContext, sender_account_id: str = "", customer_id: str = "") -> str:
    """Look up a customer's Personal Sender Account.

    The account shows its verification level, its status (pending verification, active, locked,
    restricted, suspended or closed), the opening date, when the current level took effect, the
    next periodic review date, and any lock, restriction, suspension or closure details. Search by
    the account reference number or by the customer reference number.

    Args:
        sender_account_id: Personal Sender Account reference number; leave "" if unknown.
        customer_id: Customer reference number of the account holder; leave "" if unknown.
    """
    match = _criteria({"sender_account_id": sender_account_id, "customer_id": customer_id})
    if not match:
        return "Error: give at least one reference number to look up Personal Sender Accounts."
    return _report(ctx.find("sender_accounts", **match), match, "Personal Sender Accounts")


@tool(owner="agent", rw="read")
def find_sender_account_events(ctx: ToolContext, account_event_id: str = "", sender_account_id: str = "",
                               customer_id: str = "", related_event_id: str = "",
                               recipient_id: str = "") -> str:
    """Look up the history of a Personal Sender Account.

    The history covers limit review requests and compliance decisions on them, requests for
    information and their due dates, recipients added, scheduled callbacks, statement requests and
    suspension appeals, each with its date and details. A decision can be found from the request it
    answers by passing that request's reference as related_event_id.

    Args:
        account_event_id: Reference number of one history entry; leave "" if unknown.
        sender_account_id: Personal Sender Account reference number; leave "" if unknown.
        customer_id: Customer reference number; leave "" if unknown.
        related_event_id: Reference number of the request a decision answers; leave "" if unknown.
        recipient_id: Recipient reference number, to find when that recipient was added; leave "" if unknown.
    """
    match = _criteria({"account_event_id": account_event_id, "sender_account_id": sender_account_id, "customer_id": customer_id, "related_event_id": related_event_id, "recipient_id": recipient_id})
    if not match:
        return "Error: give at least one reference number to look up account history entries."
    return _report(ctx.find("sender_account_events", **match), match, "account history entries")


@tool(owner="agent", rw="read")
def find_sender_documents(ctx: ToolContext, document_id: str = "", sender_account_id: str = "",
                          customer_id: str = "", related_document_id: str = "") -> str:
    """Look up the verification documents logged on a Personal Sender Account and their reviews.

    Each received document shows its type, upload reference, the level it was submitted for, its
    issue and expiry dates and the date received; each review shows whether compliance accepted or
    rejected it and why. Find the reviews of one document by passing its reference as
    related_document_id.

    Args:
        document_id: Reference number of one document entry; leave "" if unknown.
        sender_account_id: Personal Sender Account reference number; leave "" if unknown.
        customer_id: Customer reference number; leave "" if unknown.
        related_document_id: Reference number of the received document a review concerns; leave "" if unknown.
    """
    match = _criteria({"document_id": document_id, "sender_account_id": sender_account_id, "customer_id": customer_id, "related_document_id": related_document_id})
    if not match:
        return "Error: give at least one reference number to look up verification documents."
    return _report(ctx.find("sender_documents", **match), match, "verification documents")


# ------------------------------------------------------------------------------- Bank Deposit

@tool(owner="agent", rw="read")
def find_bank_transfers(ctx: ToolContext, bank_transfer_id: str = "", customer_id: str = "",
                        sender_account_id: str = "", recipient_id: str = "") -> str:
    """Look up Bank Deposit transfers.

    Each transfer shows its tier, status, corridor, confirmation number, principal, fees, exchange
    rate, amount the recipient receives, funding method, purpose, beneficiary bank details, when it
    was booked, the disclosed date available, deposit, cancellation and closing dates, any hold, and
    the principal and fees Paloma currently holds for it. Search by the transfer reference number,
    the customer, the sender account or the recipient.

    Args:
        bank_transfer_id: Bank Deposit transfer reference number; leave "" if unknown.
        customer_id: Customer reference number of the sender; leave "" if unknown.
        sender_account_id: Personal Sender Account reference number; leave "" if unknown.
        recipient_id: Recipient reference number; leave "" if unknown.
    """
    match = _criteria({"bank_transfer_id": bank_transfer_id, "customer_id": customer_id, "sender_account_id": sender_account_id, "recipient_id": recipient_id})
    if not match:
        return "Error: give at least one reference number to look up Bank Deposit transfers."
    return _report(ctx.find("bank_transfers", **match), match, "Bank Deposit transfers")


@tool(owner="agent", rw="read")
def find_bank_ledger(ctx: ToolContext, ledger_entry_id: str = "", bank_transfer_id: str = "",
                     customer_id: str = "", related_entry_id: str = "") -> str:
    """Look up the money movements on Bank Deposit transfers.

    Movements include the customer's payment, fees charged and refunded, payouts to the beneficiary
    bank, funds that came back with their return reason and conversion rate, Paloma make-good
    credits and refunds to the customer, each with its date, amount and payout attempt. A refund or
    fee refund can be traced to the entry it pays back by passing that entry's reference as
    related_entry_id.

    Args:
        ledger_entry_id: Reference number of one money movement; leave "" if unknown.
        bank_transfer_id: Bank Deposit transfer reference number; leave "" if unknown.
        customer_id: Customer reference number; leave "" if unknown.
        related_entry_id: Reference number of the movement a refund or credit points back to; leave "" if unknown.
    """
    match = _criteria({"ledger_entry_id": ledger_entry_id, "bank_transfer_id": bank_transfer_id, "customer_id": customer_id, "related_entry_id": related_entry_id})
    if not match:
        return "Error: give at least one reference number to look up Bank Deposit money movements."
    return _report(ctx.find("bank_ledger", **match), match, "Bank Deposit money movements")


@tool(owner="agent", rw="read")
def find_bank_cases(ctx: ToolContext, case_id: str = "", bank_transfer_id: str = "",
                    customer_id: str = "", related_case_id: str = "") -> str:
    """Look up cases opened on Bank Deposit transfers.

    Cases include answers to requests for information, error notices with their resolution due
    dates and findings, the remedy the customer chose, and recall requests with their outcome.
    Findings, remedy choices and recall outcomes can be found from the notice or request they
    answer by passing its reference as related_case_id.

    Args:
        case_id: Case reference number; leave "" if unknown.
        bank_transfer_id: Bank Deposit transfer reference number; leave "" if unknown.
        customer_id: Customer reference number; leave "" if unknown.
        related_case_id: Reference number of the notice or request a later case answers; leave "" if unknown.
    """
    match = _criteria({"case_id": case_id, "bank_transfer_id": bank_transfer_id, "customer_id": customer_id, "related_case_id": related_case_id})
    if not match:
        return "Error: give at least one reference number to look up Bank Deposit cases."
    return _report(ctx.find("bank_cases", **match), match, "Bank Deposit cases")


# -------------------------------------------------------------------------------- Cash Pickup

@tool(owner="agent", rw="read")
def find_cash_transfers(ctx: ToolContext, cash_transfer_id: str = "", customer_id: str = "",
                        sender_account_id: str = "", recipient_id: str = "") -> str:
    """Look up Cash Pickup transfers.

    Each transfer shows its tier, status, corridor, confirmation number, Pickup Number, principal,
    fees, exchange rate and payout currency, cash amount, the recipient name the cash is released
    to, when it was booked, the disclosed date available, when it became collectable and until when,
    collection, expiry and cancellation dates, reactivations, any hold, and the principal and fees
    Paloma currently holds. Search by transfer reference, customer, sender account or recipient.

    Args:
        cash_transfer_id: Cash Pickup transfer reference number; leave "" if unknown.
        customer_id: Customer reference number of the sender; leave "" if unknown.
        sender_account_id: Personal Sender Account reference number; leave "" if unknown.
        recipient_id: Recipient reference number; leave "" if unknown.
    """
    match = _criteria({"cash_transfer_id": cash_transfer_id, "customer_id": customer_id, "sender_account_id": sender_account_id, "recipient_id": recipient_id})
    if not match:
        return "Error: give at least one reference number to look up Cash Pickup transfers."
    return _report(ctx.find("cash_transfers", **match), match, "Cash Pickup transfers")


@tool(owner="agent", rw="read")
def find_cash_ledger(ctx: ToolContext, ledger_entry_id: str = "", cash_transfer_id: str = "",
                     customer_id: str = "", related_entry_id: str = "") -> str:
    """Look up the money movements on Cash Pickup transfers.

    Movements include the customer's payment, fees charged and refunded (transfer, card, US-dollar
    payout, name correction and reactivation fees), the cash handed over at a payout location,
    Paloma make-good credits and refunds to the customer, each with its date and amount. Trace a
    refund to what it pays back by passing that movement's reference as related_entry_id.

    Args:
        ledger_entry_id: Reference number of one money movement; leave "" if unknown.
        cash_transfer_id: Cash Pickup transfer reference number; leave "" if unknown.
        customer_id: Customer reference number; leave "" if unknown.
        related_entry_id: Reference number of the movement a refund or credit points back to; leave "" if unknown.
    """
    match = _criteria({"ledger_entry_id": ledger_entry_id, "cash_transfer_id": cash_transfer_id, "customer_id": customer_id, "related_entry_id": related_entry_id})
    if not match:
        return "Error: give at least one reference number to look up Cash Pickup money movements."
    return _report(ctx.find("cash_ledger", **match), match, "Cash Pickup money movements")


@tool(owner="agent", rw="read")
def find_cash_cases(ctx: ToolContext, case_id: str = "", cash_transfer_id: str = "",
                    customer_id: str = "", related_case_id: str = "") -> str:
    """Look up cases opened on Cash Pickup transfers.

    Cases include pickups refused at a counter and why, recipient name corrections, answers to
    requests for information, error notices with their findings, and the remedy the customer chose.
    Find the finding or choice on a notice by passing the notice's reference as related_case_id.

    Args:
        case_id: Case reference number; leave "" if unknown.
        cash_transfer_id: Cash Pickup transfer reference number; leave "" if unknown.
        customer_id: Customer reference number; leave "" if unknown.
        related_case_id: Reference number of the notice a later case answers; leave "" if unknown.
    """
    match = _criteria({"case_id": case_id, "cash_transfer_id": cash_transfer_id, "customer_id": customer_id, "related_case_id": related_case_id})
    if not match:
        return "Error: give at least one reference number to look up Cash Pickup cases."
    return _report(ctx.find("cash_cases", **match), match, "Cash Pickup cases")


# ------------------------------------------------------------------------------ Mobile Wallet

@tool(owner="agent", rw="read")
def find_wallet_transfers(ctx: ToolContext, wallet_transfer_id: str = "", customer_id: str = "",
                          sender_account_id: str = "", recipient_id: str = "") -> str:
    """Look up Mobile Wallet transfers.

    Each transfer shows its tier, status, corridor, confirmation number, principal, fees, exchange
    rate, amount to be credited, the wallet provider, number and registered name it is addressed
    to, when it was booked, released, credited, failed or cancelled, the disclosed date available,
    any hold, and the principal and fees Paloma currently holds. Search by transfer reference,
    customer, sender account or recipient.

    Args:
        wallet_transfer_id: Mobile Wallet transfer reference number; leave "" if unknown.
        customer_id: Customer reference number of the sender; leave "" if unknown.
        sender_account_id: Personal Sender Account reference number; leave "" if unknown.
        recipient_id: Recipient reference number; leave "" if unknown.
    """
    match = _criteria({"wallet_transfer_id": wallet_transfer_id, "customer_id": customer_id, "sender_account_id": sender_account_id, "recipient_id": recipient_id})
    if not match:
        return "Error: give at least one reference number to look up Mobile Wallet transfers."
    return _report(ctx.find("wallet_transfers", **match), match, "Mobile Wallet transfers")


@tool(owner="agent", rw="read")
def find_wallet_ledger(ctx: ToolContext, ledger_entry_id: str = "", wallet_transfer_id: str = "",
                       customer_id: str = "", related_entry_id: str = "") -> str:
    """Look up the money movements on Mobile Wallet transfers.

    Movements include the customer's payment, fees charged and refunded (transfer, card, retry and
    redirect fees), each credit sent to the wallet provider, credits the provider rejected with the
    reason, Paloma make-good credits and refunds to the customer, each with its date, amount and
    credit attempt. Trace a refund to what it pays back by passing that movement's reference as
    related_entry_id.

    Args:
        ledger_entry_id: Reference number of one money movement; leave "" if unknown.
        wallet_transfer_id: Mobile Wallet transfer reference number; leave "" if unknown.
        customer_id: Customer reference number; leave "" if unknown.
        related_entry_id: Reference number of the movement a refund or credit points back to; leave "" if unknown.
    """
    match = _criteria({"ledger_entry_id": ledger_entry_id, "wallet_transfer_id": wallet_transfer_id, "customer_id": customer_id, "related_entry_id": related_entry_id})
    if not match:
        return "Error: give at least one reference number to look up Mobile Wallet money movements."
    return _report(ctx.find("wallet_ledger", **match), match, "Mobile Wallet money movements")


@tool(owner="agent", rw="read")
def find_wallet_cases(ctx: ToolContext, case_id: str = "", wallet_transfer_id: str = "",
                      customer_id: str = "", related_case_id: str = "") -> str:
    """Look up cases opened on Mobile Wallet transfers.

    Cases include redirects of a failed credit to another wallet, answers to requests for
    information, error notices with their findings, and the remedy the customer chose. Find the
    finding or choice on a notice by passing the notice's reference as related_case_id.

    Args:
        case_id: Case reference number; leave "" if unknown.
        wallet_transfer_id: Mobile Wallet transfer reference number; leave "" if unknown.
        customer_id: Customer reference number; leave "" if unknown.
        related_case_id: Reference number of the notice a later case answers; leave "" if unknown.
    """
    match = _criteria({"case_id": case_id, "wallet_transfer_id": wallet_transfer_id, "customer_id": customer_id, "related_case_id": related_case_id})
    if not match:
        return "Error: give at least one reference number to look up Mobile Wallet cases."
    return _report(ctx.find("wallet_cases", **match), match, "Mobile Wallet cases")


# ---------------------------------------------------------------------------- Paloma Business

@tool(owner="agent", rw="read")
def find_business_accounts(ctx: ToolContext, business_account_id: str = "", customer_id: str = "") -> str:
    """Look up Paloma Business accounts.

    Each account shows its plan, status (pending KYB, active, past due, suspended or closed), the
    business's legal name, legal form, last four EIN digits and formation date, application and KYB
    approval dates, billing cycle and current billing period, any scheduled plan change, commitment
    end, past-due and suspension details, the current balance and the free payouts left this
    period. Search by the business account reference number or by the owner's customer reference.

    Args:
        business_account_id: Paloma Business account reference number; leave "" if unknown.
        customer_id: Customer reference number of the owner; leave "" if unknown.
    """
    match = _criteria({"business_account_id": business_account_id, "customer_id": customer_id})
    if not match:
        return "Error: give at least one reference number to look up Paloma Business accounts."
    return _report(ctx.find("business_accounts", **match), match, "Paloma Business accounts")


@tool(owner="agent", rw="read")
def find_business_ledger(ctx: ToolContext, ledger_entry_id: str = "", business_account_id: str = "",
                         customer_id: str = "", related_entry_id: str = "") -> str:
    """Look up the balance and free-payout movements of a Paloma Business account.

    Movements include deposits, fees (subscription, proration, seats, payouts, deposits,
    withdrawals, cancellations, returns, early termination), fee refunds, proration credits, payout
    debits and money credited back, withdrawals, and free payouts granted, used, restored or
    lapsed, each with its billing period, payout or deposit reference and date. Trace a fee refund
    or proration credit to its charge by passing the charge's reference as related_entry_id.

    Args:
        ledger_entry_id: Reference number of one movement; leave "" if unknown.
        business_account_id: Paloma Business account reference number; leave "" if unknown.
        customer_id: Customer reference number of the owner; leave "" if unknown.
        related_entry_id: Reference number of the charge a refund or credit points back to; leave "" if unknown.
    """
    match = _criteria({"ledger_entry_id": ledger_entry_id, "business_account_id": business_account_id, "customer_id": customer_id, "related_entry_id": related_entry_id})
    if not match:
        return "Error: give at least one reference number to look up Paloma Business balance movements."
    return _report(ctx.find("business_ledger", **match), match, "Paloma Business balance movements")


@tool(owner="agent", rw="read")
def find_business_payouts(ctx: ToolContext, payout_event_id: str = "", business_account_id: str = "",
                          customer_id: str = "", payout_reference: str = "") -> str:
    """Look up the payouts of a Paloma Business account and what has happened to each.

    For every payout you see its submission (batch, channel, rail, corridor, beneficiary, invoice
    reference, principal, rate, amount received, fee, whether a free payout was used, requested
    release date) and its later approval, release, payment, cancellation or return. Search by the
    business account, the owner, or the payout reference the owner reads from the dashboard.

    Args:
        payout_event_id: Reference number of one payout entry; leave "" if unknown.
        business_account_id: Paloma Business account reference number; leave "" if unknown.
        customer_id: Customer reference number of the owner; leave "" if unknown.
        payout_reference: Payout reference exactly as shown on the dashboard (e.g. BP-26091-04417); leave "" if unknown.
    """
    match = _criteria({"payout_event_id": payout_event_id, "business_account_id": business_account_id, "customer_id": customer_id, "payout_reference": payout_reference})
    if not match:
        return "Error: give at least one reference number to look up Paloma Business payouts."
    return _report(ctx.find("business_payouts", **match), match, "Paloma Business payouts")


@tool(owner="agent", rw="read")
def find_business_events(ctx: ToolContext, business_event_id: str = "", business_account_id: str = "",
                         customer_id: str = "") -> str:
    """Look up the administrative history of a Paloma Business account.

    The history covers users added and removed with their roles, KYB documents received, statement
    requests and scheduled callbacks, each with its date.

    Args:
        business_event_id: Reference number of one history entry; leave "" if unknown.
        business_account_id: Paloma Business account reference number; leave "" if unknown.
        customer_id: Customer reference number of the owner; leave "" if unknown.
    """
    match = _criteria({"business_event_id": business_event_id, "business_account_id": business_account_id, "customer_id": customer_id})
    if not match:
        return "Error: give at least one reference number to look up Paloma Business account history entries."
    return _report(ctx.find("business_events", **match), match, "Paloma Business account history entries")


# ----------------------------------------------------------------------------- Paloma Rewards

@tool(owner="agent", rw="read")
def find_rewards_memberships(ctx: ToolContext, rewards_membership_id: str = "", customer_id: str = "",
                             referred_by_customer_id: str = "") -> str:
    """Look up Paloma Rewards memberships.

    A membership shows its tier, status, enrollment and closing dates, when the tier took effect,
    the next tier review and any grace period, the referral code used at sign-up and who referred
    the member, the most recent qualifying transfer date and the points balance. Search by
    membership, by member, or by the customer who referred them.

    Args:
        rewards_membership_id: Membership reference number; leave "" if unknown.
        customer_id: Customer reference number of the member; leave "" if unknown.
        referred_by_customer_id: Customer reference number of the referring member; leave "" if unknown.
    """
    match = _criteria({"rewards_membership_id": rewards_membership_id, "customer_id": customer_id, "referred_by_customer_id": referred_by_customer_id})
    if not match:
        return "Error: give at least one reference number to look up Paloma Rewards memberships."
    return _report(ctx.find("rewards_memberships", **match), match, "Paloma Rewards memberships")


@tool(owner="agent", rw="read")
def find_rewards_ledger(ctx: ToolContext, rewards_entry_id: str = "", rewards_membership_id: str = "",
                        customer_id: str = "", source_transfer_id: str = "",
                        related_entry_id: str = "") -> str:
    """Look up the points history of a Paloma Rewards membership.

    Entries show points earned (and on which transfer or order), bonuses, redemptions with their
    cash, donation or airtime value, points that expired or were forfeited, and reversals, each
    with its date. Find the points a given transfer earned by passing that transfer's reference.

    Args:
        rewards_entry_id: Reference number of one points entry; leave "" if unknown.
        rewards_membership_id: Membership reference number; leave "" if unknown.
        customer_id: Customer reference number of the member; leave "" if unknown.
        source_transfer_id: Reference number of the transfer or order that earned or lost points; leave "" if unknown.
        related_entry_id: Reference number of the earning a reversal takes back; leave "" if unknown.
    """
    match = _criteria({"rewards_entry_id": rewards_entry_id, "rewards_membership_id": rewards_membership_id, "customer_id": customer_id, "source_transfer_id": source_transfer_id, "related_entry_id": related_entry_id})
    if not match:
        return "Error: give at least one reference number to look up Paloma Rewards points entries."
    return _report(ctx.find("rewards_ledger", **match), match, "Paloma Rewards points entries")


# ----------------------------------------------------------------- Paloma Top-Up & Bill Pay

@tool(owner="agent", rw="read")
def find_topup_orders(ctx: ToolContext, topup_order_id: str = "", customer_id: str = "",
                      sender_account_id: str = "") -> str:
    """Look up Top-Up and Bill Pay orders.

    Each order shows the product, status, corridor, operator or biller, destination number and
    holder name, order reference, local value, USD value, fees, rate, payment method, when it was
    ordered, sent, delivered, failed or cancelled, any electricity token code, retries, and the
    money Paloma currently holds for it. Search by order reference number, customer or sender
    account.

    Args:
        topup_order_id: Order reference number; leave "" if unknown.
        customer_id: Customer reference number; leave "" if unknown.
        sender_account_id: Personal Sender Account reference number; leave "" if unknown.
    """
    match = _criteria({"topup_order_id": topup_order_id, "customer_id": customer_id, "sender_account_id": sender_account_id})
    if not match:
        return "Error: give at least one reference number to look up Top-Up and Bill Pay orders."
    return _report(ctx.find("topup_orders", **match), match, "Top-Up and Bill Pay orders")


@tool(owner="agent", rw="read")
def find_topup_ledger(ctx: ToolContext, topup_entry_id: str = "", topup_order_id: str = "",
                      customer_id: str = "", related_entry_id: str = "") -> str:
    """Look up the money movements on Top-Up and Bill Pay orders.

    Movements include the payment collected, fees charged and refunded, the value sent to the
    operator or biller on each attempt, values that came back with the rejection reason, and
    refunds, each with its date and amount.

    Args:
        topup_entry_id: Reference number of one movement; leave "" if unknown.
        topup_order_id: Order reference number; leave "" if unknown.
        customer_id: Customer reference number; leave "" if unknown.
        related_entry_id: Reference number of the fee charge a fee refund points back to; leave "" if unknown.
    """
    match = _criteria({"topup_entry_id": topup_entry_id, "topup_order_id": topup_order_id, "customer_id": customer_id, "related_entry_id": related_entry_id})
    if not match:
        return "Error: give at least one reference number to look up Top-Up and Bill Pay money movements."
    return _report(ctx.find("topup_ledger", **match), match, "Top-Up and Bill Pay money movements")


@tool(owner="agent", rw="read")
def find_topup_cases(ctx: ToolContext, topup_case_id: str = "", topup_order_id: str = "",
                     customer_id: str = "", related_case_id: str = "") -> str:
    """Look up cases on Top-Up and Bill Pay orders.

    Cases include destination corrections on failed orders, electricity token re-sends, and
    disputes with Paloma's finding. Find the finding on a dispute by passing the dispute's
    reference as related_case_id.

    Args:
        topup_case_id: Case reference number; leave "" if unknown.
        topup_order_id: Order reference number; leave "" if unknown.
        customer_id: Customer reference number; leave "" if unknown.
        related_case_id: Reference number of the dispute a decision answers; leave "" if unknown.
    """
    match = _criteria({"topup_case_id": topup_case_id, "topup_order_id": topup_order_id, "customer_id": customer_id, "related_case_id": related_case_id})
    if not match:
        return "Error: give at least one reference number to look up Top-Up and Bill Pay cases."
    return _report(ctx.find("topup_cases", **match), match, "Top-Up and Bill Pay cases")


# ------------------------------------------------------------------ verification and handoff

@tool(owner="agent", rw="read")
def find_identity_verifications(ctx: ToolContext, verification_id: str = "", customer_id: str = "") -> str:
    """Check whether a customer's identity has been verified on this call.

    The result shows whether verification passed and when it was last attempted. Search by the
    customer reference number or the verification reference number.

    Args:
        verification_id: Verification reference number; leave "" if unknown.
        customer_id: Customer reference number; leave "" if unknown.
    """
    match = _criteria({"verification_id": verification_id, "customer_id": customer_id})
    if not match:
        return "Error: give at least one reference number to look up identity verification results."
    return _report(ctx.find("identity_verifications", **match), match, "identity verification results")


@tool(owner="agent", rw="read")
def find_human_handoffs(ctx: ToolContext, handoff_id: str = "", customer_id: str = "") -> str:
    """Look up handovers of a customer to a human representative.

    Each handover shows its reason and when it happened. Search by the customer reference number or
    the handover reference number.

    Args:
        handoff_id: Handover reference number; leave "" if unknown.
        customer_id: Customer reference number; leave "" if unknown.
    """
    match = _criteria({"handoff_id": handoff_id, "customer_id": customer_id})
    if not match:
        return "Error: give at least one reference number to look up handovers to a human representative."
    return _report(ctx.find("human_handoffs", **match), match, "handovers to a human representative")


def _norm(field: str, value: str) -> str:
    # Formatting-insensitive comparison: digits only for the phone, case-insensitive for the email,
    # uppercase for the ID characters, trimmed everywhere.
    value = str(value or "").strip()
    if field == "phone":
        return "".join(ch for ch in value if ch.isdigit())
    if field == "email":
        return value.casefold()
    if field == "id_document_last4":
        return value.upper()
    return value


@tool(owner="agent", rw="write")
def verify_customer_identity(ctx: ToolContext, customer_id: str, phone: str = "", email: str = "",
                             date_of_birth: str = "", zip_code: str = "",
                             id_document_last4: str = "") -> str:
    """Verify the caller's identity against their Paloma profile and record the outcome.

    Identity must be verified before discussing or changing anything on a customer's accounts,
    transfers or orders. This tool does the comparison itself: it checks each piece of
    information the caller states against the profile on file and passes only when at least 3 of
    them match. The customer reference number only identifies which profile to compare against and
    never counts as a match, and the caller's name is not a verification item. Callers usually know
    only some items, so pass exactly what the caller said and leave the rest blank. The outcome is
    recorded; when a first attempt fails and a later attempt with more information passes, the pass
    stands.

    Args:
        customer_id: Customer reference number from the customer profile lookup. Required.
        phone: Registered US mobile number as the caller states it (10 digits); leave "" if not stated.
        email: Registered email address as the caller states it; leave "" if not stated.
        date_of_birth: Date of birth as the caller states it, in YYYY-MM-DD; leave "" if not stated.
        zip_code: 5-digit ZIP code of the residential address on file, as stated; leave "" if not stated.
        id_document_last4: Last four characters of the photo ID number on file, as stated; leave "" if not stated.
    """
    if not customer_id:
        return "Error: customer_id is required; look the customer up first and pass their reference number."
    rows = ctx.find("customers", customer_id=customer_id)
    if not rows:
        return f"Error: no customer {customer_id}; cannot verify."
    rec = rows[0]
    supplied = {"phone": phone, "email": email, "date_of_birth": date_of_birth,
                "zip_code": zip_code, "id_document_last4": id_document_last4}
    matched = sum(1 for field, value in supplied.items()
                  if value and _norm(field, value) == _norm(field, rec.get(field)))
    verified = matched >= 3
    rid = ctx.make_id("ver_", customer_id)
    # Upsert and never downgrade: a pass on a later attempt must stand.
    prior = ctx.find("identity_verifications", verification_id=rid)
    verified = verified or bool(prior and prior[0].get("verified"))
    if prior:
        ctx.update("identity_verifications", rid, verified=verified, verified_at=ctx.now())
    else:
        ctx.create("identity_verifications", rid, verification_id=rid, customer_id=customer_id,
                   verified=verified, verified_at=ctx.now())
    if verified:
        return f"Identity verified for {customer_id} ({matched} item(s) matched on this attempt)."
    return (f"Identity NOT verified for {customer_id}: only {matched} of the required 3 items "
            "matched. Ask the caller for another item on file and try again.")


@tool(owner="agent", rw="write")
def transfer_to_human_agent(ctx: ToolContext, customer_id: str, reason: str) -> str:
    """Hand the customer over to a human Paloma representative and record why.

    Use it in exactly two situations: when no Paloma policy can resolve what the customer needs
    (POLICY_NOT_COVERED), or when the customer has explicitly asked to speak with a human
    representative at least 2 times during the conversation (CUSTOMER_REQUESTED).

    Args:
        customer_id: Customer reference number from the customer profile lookup.
        reason: Exactly POLICY_NOT_COVERED or CUSTOMER_REQUESTED, never free text.
            POLICY_NOT_COVERED: no Paloma policy offers a way to resolve the request.
            CUSTOMER_REQUESTED: the customer explicitly asked for a human representative at least 2 times.
    """
    allowed = {"POLICY_NOT_COVERED", "CUSTOMER_REQUESTED"}
    if reason not in allowed:
        return f"Error: unknown handoff reason '{reason}'. Valid: {', '.join(sorted(allowed))}."
    if not ctx.find("customers", customer_id=customer_id):
        return f"Error: no customer {customer_id}; cannot record the handover."
    rid = ctx.make_id("hof_", customer_id, reason)
    ctx.create("human_handoffs", rid, handoff_id=rid, customer_id=customer_id,
               reason=reason, created_at=ctx.now())
    return f"Handover to a human representative recorded for {customer_id} ({reason})."

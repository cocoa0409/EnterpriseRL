"""Shared tools for env_0048_manufactured_home_community_operator (Hearthstone Communities resident desk).

Share tools are always present in their owner's tool list. This file holds only the three
foundations every difficulty reuses: one record finder per table (the customers finder doubles as
the identity entry), the identity-verification write, and the transfer to a human representative.
Customer-originated writes live as hidden task tools in each difficulty's task_tools.py.

Scenario operational constants built in here:
  K = 2  identity credentials that must match the profile for verification to pass
  R = 2  explicit requests for a human after which the handoff reason is CUSTOMER_REQUESTED
"""

from erlbench import ToolContext, tool


def _pick(**kw):
    # keep only the criteria actually supplied
    return {k: v for k, v in kw.items() if v}


# --------------------------------------------------------------------------- identity entry
@tool(owner="agent", rw="read")
def find_customers(ctx: ToolContext, customer_id: str = "", phone_number: str = "",
                   email: str = "", name: str = "") -> str:
    """Look up a resident's customer profile to establish whose account this call is about.

    Search by the customer reference number when it is known, or by what the caller naturally
    tells you: the phone number on the profile, the email address on the profile, or the full
    name as it appears on their lease or loan documents. Supply any one or more; spacing,
    punctuation and capital letters in what the caller says do not matter. A match returns the
    whole profile — name, phone number, email, date of birth, last four digits of the Social
    Security number, mailing address and the date the profile was opened — including the customer
    reference number used everywhere else. Finding a profile does not verify the caller's identity.

    Args:
        customer_id: The customer reference number, if already known; leave "" otherwise.
        phone_number: Phone number on the profile as the caller states it, e.g. "863-555-0142"; leave "" if not given.
        email: Email address on the profile as the caller states it, e.g. "d.okafor@example.com"; leave "" if not given.
        name: Full name as on the caller's lease or loan documents, e.g. "Darlene M. Okafor"; leave "" if not given.
    """
    match = _pick(customer_id=customer_id, phone_number=phone_number, email=email, name=name)
    if not match:
        return "Error: provide at least one reference number or profile detail to find the customer."
    rows = ctx.fuzzy_find("customers", **match)
    if not rows:
        return f"No customer profile matches {match}."
    if len(rows) > 1:
        return f"Error: {len(rows)} customer profiles match {match}; ask the caller for one more detail."
    return str(rows[0])


# --------------------------------------------------------------------------- verification
@tool(owner="agent", rw="write")
def verify_customer_identity(ctx: ToolContext, customer_id: str, phone_number: str = "",
                             email: str = "", date_of_birth: str = "", ssn_last4: str = "",
                             profile_opened_date: str = "") -> str:
    """Verify the caller's identity against their customer profile and record the outcome.

    Identity must be verified before any account information is discussed or any business is
    transacted. This tool does the comparison itself: it checks each detail the caller gives
    against the profile, counts the matches, and passes only when at least two match. The
    customer reference number only identifies which profile to check and never counts as a match.
    Pass only the details the caller actually stated, exactly as given, and leave the rest blank.
    The outcome is recorded; if a first attempt fails and a later attempt with more details
    passes, the identity stands verified.

    Args:
        customer_id: Customer reference number from the profile lookup; required.
        phone_number: Phone number the caller states, e.g. "863-555-0142" (digits are compared, separators ignored); "" if not stated.
        email: Email address the caller states (compared without regard to capital letters); "" if not stated.
        date_of_birth: Date of birth the caller states, written YYYY-MM-DD; "" if not stated.
        ssn_last4: Last four digits of the caller's Social Security number, exactly four digits; "" if not stated.
        profile_opened_date: Date the caller says they first became a Hearthstone customer, written YYYY-MM-DD; "" if not stated.
    """
    if not customer_id:
        return "Error: customer_id is required; look the customer up first and pass their reference number."
    rows = ctx.find("customers", customer_id=customer_id)
    if not rows:
        return f"Error: no customer {customer_id}; cannot verify."
    rec = rows[0]

    def digits(v):
        return "".join(ch for ch in str(v or "") if ch.isdigit())

    checks = [
        (phone_number, lambda v: digits(v) != "" and digits(v) == digits(rec.get("phone_number"))),
        (email, lambda v: str(v).strip().lower() == str(rec.get("email") or "").strip().lower()),
        (date_of_birth, lambda v: str(v).strip() == str(rec.get("date_of_birth") or "")),
        (ssn_last4, lambda v: str(v).strip() == str(rec.get("ssn_last4") or "")),
        (profile_opened_date, lambda v: str(v).strip() == str(rec.get("profile_opened_date") or "")),
    ]
    matched = sum(1 for value, same in checks if value and same(value))
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
        return f"Identity verified for {customer_id} ({matched} detail(s) matched on this attempt)."
    return (f"Identity NOT verified for {customer_id}: only {matched} of the required 2 details matched. "
            "Ask the caller for another detail on file and try again.")


# --------------------------------------------------------------------------- handoff
@tool(owner="agent", rw="write")
def transfer_to_human_agent(ctx: ToolContext, customer_id: str, reason: str) -> str:
    """Transfer the caller to a human representative at the community or finance office and record why.

    Use POLICY_NOT_COVERED when no Hearthstone policy lets the resident desk resolve what the
    caller needs. Use CUSTOMER_REQUESTED when the caller has explicitly asked for a person two
    times.

    Args:
        customer_id: Customer reference number from the profile lookup; the profile must exist.
        reason: Exactly one of POLICY_NOT_COVERED or CUSTOMER_REQUESTED.
    """
    allowed = {"POLICY_NOT_COVERED", "CUSTOMER_REQUESTED"}
    if reason not in allowed:
        return f"Error: unknown handoff reason '{reason}'. Valid: CUSTOMER_REQUESTED, POLICY_NOT_COVERED."
    if not ctx.find("customers", customer_id=customer_id):
        return f"Error: no customer {customer_id}; cannot record the transfer."
    rid = ctx.make_id("hof_", customer_id, reason)
    ctx.create("human_handoffs", rid, handoff_id=rid, customer_id=customer_id,
               reason=reason, created_at=ctx.now())
    return f"Transfer to a human representative recorded for {customer_id} ({reason})."


# --------------------------------------------------------------------------- desk logs
@tool(owner="agent", rw="read")
def find_identity_verifications(ctx: ToolContext, verification_id: str = "", customer_id: str = "") -> str:
    """Check whether a customer's identity has already been verified, and when.

    Args:
        verification_id: Reference number of the verification record; leave "" if unknown.
        customer_id: Customer reference number; leave "" if unknown.
    """
    match = _pick(verification_id=verification_id, customer_id=customer_id)
    if not match:
        return "Error: provide at least one reference number to search by."
    rows = ctx.find("identity_verifications", **match)
    return str(rows) if rows else f"No identity verification on record for {match}."


@tool(owner="agent", rw="read")
def find_human_handoffs(ctx: ToolContext, handoff_id: str = "", customer_id: str = "") -> str:
    """See whether a customer has already been transferred to a human representative, with the reason and time.

    Args:
        handoff_id: Reference number of the transfer record; leave "" if unknown.
        customer_id: Customer reference number; leave "" if unknown.
    """
    match = _pick(handoff_id=handoff_id, customer_id=customer_id)
    if not match:
        return "Error: provide at least one reference number to search by."
    rows = ctx.find("human_handoffs", **match)
    return str(rows) if rows else f"No transfer to a human representative on record for {match}."


# --------------------------------------------------------------------------- home-site lease
@tool(owner="agent", rw="read")
def find_lease_holdings(ctx: ToolContext, lease_id: str = "", customer_id: str = "") -> str:
    """Look up residency applications and home-site leases.

    Each record shows the community and site number, the lot class, the home on the site (section
    type, length, model year), the registered household, the term type and dates, the contracted
    monthly site rent, autopay and payment-restriction status, the vacate date of any pending
    notice, the current lease balance and the security deposit held, and where the lease stands.

    Args:
        lease_id: Lease reference number; leave "" if unknown.
        customer_id: Customer reference number of the leaseholder or applicant; leave "" if unknown.
    """
    match = _pick(lease_id=lease_id, customer_id=customer_id)
    if not match:
        return "Error: provide at least one reference number to search by."
    rows = ctx.find("lease_holdings", **match)
    return str(rows) if rows else f"No lease records for {match}."


@tool(owner="agent", rw="read")
def find_lease_ledger(ctx: ToolContext, lease_entry_id: str = "", lease_id: str = "",
                      customer_id: str = "", source_entry_id: str = "") -> str:
    """List the entries on a lease's rent ledger.

    Covers site-rent and occupant charges by billing month, application fees, late fees,
    returned-payment fees and early-termination fees, payments with their channel and reference,
    returned payments, rent credits, fee waivers, and security-deposit collections and
    dispositions. Entries that act on another entry (a waiver, a return, a credit) carry that
    entry's reference.

    Args:
        lease_entry_id: Reference number of one ledger entry; leave "" if unknown.
        lease_id: Lease reference number; leave "" if unknown.
        customer_id: Customer reference number of the leaseholder; leave "" if unknown.
        source_entry_id: Reference of an entry that other entries act on (to find its waiver, return or credit); leave "" if unknown.
    """
    match = _pick(lease_entry_id=lease_entry_id, lease_id=lease_id, customer_id=customer_id,
                  source_entry_id=source_entry_id)
    if not match:
        return "Error: provide at least one reference number to search by."
    rows = ctx.find("lease_ledger", **match)
    return str(rows) if rows else f"No lease ledger entries for {match}."


@tool(owner="agent", rw="read")
def find_lease_notices(ctx: ToolContext, lease_notice_id: str = "", lease_id: str = "", customer_id: str = "") -> str:
    """Look up notices and agreements on a lease: rent-increase notices, renewal offers, nonpayment notices and repayment agreements, with their dates, deadlines and amounts.

    Args:
        lease_notice_id: Reference number of one notice; leave "" if unknown.
        lease_id: Lease reference number; leave "" if unknown.
        customer_id: Customer reference number of the leaseholder; leave "" if unknown.
    """
    match = _pick(lease_notice_id=lease_notice_id, lease_id=lease_id, customer_id=customer_id)
    if not match:
        return "Error: provide at least one reference number to search by."
    rows = ctx.find("lease_notices", **match)
    return str(rows) if rows else f"No lease notices for {match}."


@tool(owner="agent", rw="read")
def find_lease_requests(ctx: ToolContext, lease_request_id: str = "", customer_id: str = "", lease_id: str = "") -> str:
    """Look up lease requests already taken by the resident desk — renewal elections, notices to vacate and withdrawals, autopay changes, occupant registrations and repayment agreements — and where each stands.

    Args:
        lease_request_id: Reference number of one request; leave "" if unknown.
        customer_id: Customer reference number; leave "" if unknown.
        lease_id: Lease reference number; leave "" if unknown.
    """
    match = _pick(lease_request_id=lease_request_id, customer_id=customer_id, lease_id=lease_id)
    if not match:
        return "Error: provide at least one reference number to search by."
    rows = ctx.find("lease_requests", **match)
    return str(rows) if rows else f"No lease requests for {match}."


# --------------------------------------------------------------------------- utilities
@tool(owner="agent", rw="read")
def find_utility_accounts(ctx: ToolContext, utility_account_id: str = "", customer_id: str = "", lease_id: str = "") -> str:
    """Look up the utility pass-through account of a leased site: its service schedule, meter number, service start and end dates, current utility balance and status.

    Args:
        utility_account_id: Utility account reference number; leave "" if unknown.
        customer_id: Customer reference number of the account holder; leave "" if unknown.
        lease_id: Lease reference number of the site served; leave "" if unknown.
    """
    match = _pick(utility_account_id=utility_account_id, customer_id=customer_id, lease_id=lease_id)
    if not match:
        return "Error: provide at least one reference number to search by."
    rows = ctx.find("utility_accounts", **match)
    return str(rows) if rows else f"No utility accounts for {match}."


@tool(owner="agent", rw="read")
def find_utility_ledger(ctx: ToolContext, utility_entry_id: str = "", utility_account_id: str = "",
                        customer_id: str = "", source_entry_id: str = "") -> str:
    """List the entries on a utility account: meter reads (opening, actual, estimated, re-read, final) with readings and consumption, usage and fixed charges by statement month and service, administration and late fees, payments, returned payments, adjustment credits, meter tests and their fees, and refunds.

    Args:
        utility_entry_id: Reference number of one entry; leave "" if unknown.
        utility_account_id: Utility account reference number; leave "" if unknown.
        customer_id: Customer reference number of the account holder; leave "" if unknown.
        source_entry_id: Reference of an entry other entries act on (the read a charge bills, the charge a credit adjusts); leave "" if unknown.
    """
    match = _pick(utility_entry_id=utility_entry_id, utility_account_id=utility_account_id,
                  customer_id=customer_id, source_entry_id=source_entry_id)
    if not match:
        return "Error: provide at least one reference number to search by."
    rows = ctx.find("utility_ledger", **match)
    return str(rows) if rows else f"No utility ledger entries for {match}."


@tool(owner="agent", rw="read")
def find_utility_service_requests(ctx: ToolContext, utility_request_id: str = "", customer_id: str = "", utility_account_id: str = "") -> str:
    """Look up utility service requests already taken — leak adjustments (with leak location and repair date), meter tests, high-bill reviews and meter-access appointments — and their status.

    Args:
        utility_request_id: Reference number of one request; leave "" if unknown.
        customer_id: Customer reference number; leave "" if unknown.
        utility_account_id: Utility account reference number; leave "" if unknown.
    """
    match = _pick(utility_request_id=utility_request_id, customer_id=customer_id, utility_account_id=utility_account_id)
    if not match:
        return "Error: provide at least one reference number to search by."
    rows = ctx.find("utility_service_requests", **match)
    return str(rows) if rows else f"No utility service requests for {match}."


# --------------------------------------------------------------------------- home financing
@tool(owner="agent", rw="read")
def find_loan_holdings(ctx: ToolContext, loan_id: str = "", customer_id: str = "", lease_id: str = "") -> str:
    """Look up home-purchase loan applications and loans with Hearthstone Home Finance.

    Each record shows the program, the financed home (serial number, condition, model year,
    section type), price and down payment, amount financed, note rate, term, monthly installment
    and escrow, due day, next due date, maturity, autopay, escrow and insurance status, deferments
    and due-day changes used, and the unpaid principal, escrow, fees and suspense balances.

    Args:
        loan_id: Loan number; leave "" if unknown.
        customer_id: Customer reference number of the borrower or applicant; leave "" if unknown.
        lease_id: Lease reference number of the site the home sits on; leave "" if unknown.
    """
    match = _pick(loan_id=loan_id, customer_id=customer_id, lease_id=lease_id)
    if not match:
        return "Error: provide at least one reference number to search by."
    rows = ctx.find("loan_holdings", **match)
    return str(rows) if rows else f"No loan records for {match}."


@tool(owner="agent", rw="read")
def find_loan_transactions(ctx: ToolContext, loan_txn_id: str = "", loan_id: str = "",
                           customer_id: str = "", source_txn_id: str = "") -> str:
    """List the transactions on a loan: funding, installment payments split into principal, interest and escrow, partial payments and suspense applications, escrow deposits, premium disbursements and refunds, late charges, returned-payment and deferment fees, fee payments and waivers, returned payments, curtailments, payoff and charge-off.

    Args:
        loan_txn_id: Reference number of one transaction; leave "" if unknown.
        loan_id: Loan number; leave "" if unknown.
        customer_id: Customer reference number of the borrower; leave "" if unknown.
        source_txn_id: Reference of a record other transactions act on (the payment returned, the fee waived); leave "" if unknown.
    """
    match = _pick(loan_txn_id=loan_txn_id, loan_id=loan_id, customer_id=customer_id, source_txn_id=source_txn_id)
    if not match:
        return "Error: provide at least one reference number to search by."
    rows = ctx.find("loan_transactions", **match)
    return str(rows) if rows else f"No loan transactions for {match}."


@tool(owner="agent", rw="read")
def find_loan_notices(ctx: ToolContext, loan_notice_id: str = "", loan_id: str = "", customer_id: str = "") -> str:
    """Look up notices and agreements on a loan: payoff statements, right-to-cure notices, insurance lapse notices, escrow analyses and deferment agreements, with their dates and amounts.

    Args:
        loan_notice_id: Reference number of one notice; leave "" if unknown.
        loan_id: Loan number; leave "" if unknown.
        customer_id: Customer reference number of the borrower; leave "" if unknown.
    """
    match = _pick(loan_notice_id=loan_notice_id, loan_id=loan_id, customer_id=customer_id)
    if not match:
        return "Error: provide at least one reference number to search by."
    rows = ctx.find("loan_notices", **match)
    return str(rows) if rows else f"No loan notices for {match}."


@tool(owner="agent", rw="read")
def find_loan_requests(ctx: ToolContext, loan_request_id: str = "", customer_id: str = "", loan_id: str = "") -> str:
    """Look up loan servicing requests already taken — payoff statements, deferments, due-day changes, autopay changes, proof of insurance and fee-waiver reviews — and where each stands.

    Args:
        loan_request_id: Reference number of one request; leave "" if unknown.
        customer_id: Customer reference number; leave "" if unknown.
        loan_id: Loan number; leave "" if unknown.
    """
    match = _pick(loan_request_id=loan_request_id, customer_id=customer_id, loan_id=loan_id)
    if not match:
        return "Error: provide at least one reference number to search by."
    rows = ctx.find("loan_requests", **match)
    return str(rows) if rows else f"No loan requests for {match}."


# --------------------------------------------------------------------------- in-place resale
@tool(owner="agent", rw="read")
def find_resale_listings(ctx: ToolContext, resale_id: str = "", customer_id: str = "",
                         lease_id: str = "", buyer_customer_id: str = "") -> str:
    """Look up in-place home resale files: the package, the seller's lease, lienholder, occupancy, asking price, listing dates and extensions, the buyer and price under contract, closing date, fees owed and status.

    Args:
        resale_id: Resale file number; leave "" if unknown.
        customer_id: Customer reference number of the seller; leave "" if unknown.
        lease_id: Lease reference number of the seller's site; leave "" if unknown.
        buyer_customer_id: Customer reference number of the buyer under contract; leave "" if unknown.
    """
    match = _pick(resale_id=resale_id, customer_id=customer_id, lease_id=lease_id, buyer_customer_id=buyer_customer_id)
    if not match:
        return "Error: provide at least one reference number to search by."
    rows = ctx.find("resale_listings", **match)
    return str(rows) if rows else f"No resale files for {match}."


@tool(owner="agent", rw="read")
def find_resale_ledger(ctx: ToolContext, resale_entry_id: str = "", resale_id: str = "",
                       customer_id: str = "", source_entry_id: str = "") -> str:
    """List the charges, payments, credits and closing deductions on a resale file, each charge showing what it is for.

    Args:
        resale_entry_id: Reference number of one entry; leave "" if unknown.
        resale_id: Resale file number; leave "" if unknown.
        customer_id: Customer reference number of the seller; leave "" if unknown.
        source_entry_id: Reference of a record an entry acts on (the inspection behind a fee, the charge credited); leave "" if unknown.
    """
    match = _pick(resale_entry_id=resale_entry_id, resale_id=resale_id, customer_id=customer_id, source_entry_id=source_entry_id)
    if not match:
        return "Error: provide at least one reference number to search by."
    rows = ctx.find("resale_ledger", **match)
    return str(rows) if rows else f"No resale ledger entries for {match}."


@tool(owner="agent", rw="read")
def find_resale_records(ctx: ToolContext, resale_record_id: str = "", resale_id: str = "",
                        customer_id: str = "", buyer_customer_id: str = "") -> str:
    """Look up the records of a resale file: pre-sale inspections and their results, appraisals, purchase agreements (buyer, price, earnest money, financing), cancellations and closing statements.

    Args:
        resale_record_id: Reference number of one record; leave "" if unknown.
        resale_id: Resale file number; leave "" if unknown.
        customer_id: Customer reference number of the seller; leave "" if unknown.
        buyer_customer_id: Customer reference number of a buyer; leave "" if unknown.
    """
    match = _pick(resale_record_id=resale_record_id, resale_id=resale_id, customer_id=customer_id, buyer_customer_id=buyer_customer_id)
    if not match:
        return "Error: provide at least one reference number to search by."
    rows = ctx.find("resale_records", **match)
    return str(rows) if rows else f"No resale records for {match}."


@tool(owner="agent", rw="read")
def find_resale_requests(ctx: ToolContext, resale_request_id: str = "", customer_id: str = "", resale_id: str = "") -> str:
    """Look up resale requests already taken — opening a file, listing signatures, price changes, extensions, withdrawals, offer acceptances, repair coordination, warranty purchases and occupancy reports — and their status.

    Args:
        resale_request_id: Reference number of one request; leave "" if unknown.
        customer_id: Customer reference number of the seller; leave "" if unknown.
        resale_id: Resale file number; leave "" if unknown.
    """
    match = _pick(resale_request_id=resale_request_id, customer_id=customer_id, resale_id=resale_id)
    if not match:
        return "Error: provide at least one reference number to search by."
    rows = ctx.find("resale_requests", **match)
    return str(rows) if rows else f"No resale requests for {match}."


# --------------------------------------------------------------------------- rules & site care
@tool(owner="agent", rw="read")
def find_rules_site_plans(ctx: ToolContext, rules_plan_id: str = "", customer_id: str = "", lease_id: str = "") -> str:
    """Look up the site-care plan record of a leased site: the plan in force and since when, registered pets, assistance animals and vehicles, the rules balance and status.

    Args:
        rules_plan_id: Plan record reference number; leave "" if unknown.
        customer_id: Customer reference number of the leaseholder; leave "" if unknown.
        lease_id: Lease reference number of the site; leave "" if unknown.
    """
    match = _pick(rules_plan_id=rules_plan_id, customer_id=customer_id, lease_id=lease_id)
    if not match:
        return "Error: provide at least one reference number to search by."
    rows = ctx.find("rules_site_plans", **match)
    return str(rows) if rows else f"No site-care plan records for {match}."


@tool(owner="agent", rw="read")
def find_rules_ledger(ctx: ToolContext, rules_entry_id: str = "", rules_plan_id: str = "", customer_id: str = "",
                      source_record_id: str = "", source_entry_id: str = "") -> str:
    """List the rules and site-care statement: plan fees, self-help maintenance charges with contractor cost, repeat-violation charges, pet registration and vehicle permit fees, payments and waivers.

    Args:
        rules_entry_id: Reference number of one entry; leave "" if unknown.
        rules_plan_id: Plan record reference number; leave "" if unknown.
        customer_id: Customer reference number of the leaseholder; leave "" if unknown.
        source_record_id: Reference of the violation notice behind a charge; leave "" if unknown.
        source_entry_id: Reference of a charge a waiver removes; leave "" if unknown.
    """
    match = _pick(rules_entry_id=rules_entry_id, rules_plan_id=rules_plan_id, customer_id=customer_id,
                  source_record_id=source_record_id, source_entry_id=source_entry_id)
    if not match:
        return "Error: provide at least one reference number to search by."
    rows = ctx.find("rules_ledger", **match)
    return str(rows) if rows else f"No rules ledger entries for {match}."


@tool(owner="agent", rw="read")
def find_rules_records(ctx: ToolContext, rules_record_id: str = "", rules_plan_id: str = "", customer_id: str = "",
                       source_record_id: str = "", appealed_entry_id: str = "") -> str:
    """Look up rules records for a site: violation notices with rule class and cure deadline, cure outcomes, plan elections, guest registrations and appeal decisions.

    Args:
        rules_record_id: Reference number of one record; leave "" if unknown.
        rules_plan_id: Plan record reference number; leave "" if unknown.
        customer_id: Customer reference number of the leaseholder; leave "" if unknown.
        source_record_id: Reference of the violation notice a cure outcome concerns; leave "" if unknown.
        appealed_entry_id: Reference of the charge an appeal decision concerns; leave "" if unknown.
    """
    match = _pick(rules_record_id=rules_record_id, rules_plan_id=rules_plan_id, customer_id=customer_id,
                  source_record_id=source_record_id, appealed_entry_id=appealed_entry_id)
    if not match:
        return "Error: provide at least one reference number to search by."
    rows = ctx.find("rules_records", **match)
    return str(rows) if rows else f"No rules records for {match}."


@tool(owner="agent", rw="read")
def find_rules_appeals(ctx: ToolContext, rules_appeal_id: str = "", customer_id: str = "",
                       rules_plan_id: str = "", appealed_entry_id: str = "") -> str:
    """Look up appeals of rules charges already taken, with the ground stated and where each stands.

    Args:
        rules_appeal_id: Reference number of one appeal; leave "" if unknown.
        customer_id: Customer reference number; leave "" if unknown.
        rules_plan_id: Plan record reference number; leave "" if unknown.
        appealed_entry_id: Reference of the charge appealed; leave "" if unknown.
    """
    match = _pick(rules_appeal_id=rules_appeal_id, customer_id=customer_id, rules_plan_id=rules_plan_id,
                  appealed_entry_id=appealed_entry_id)
    if not match:
        return "Error: provide at least one reference number to search by."
    rows = ctx.find("rules_appeals", **match)
    return str(rows) if rows else f"No rules appeals for {match}."


# --------------------------------------------------------------------------- storage
@tool(owner="agent", rw="read")
def find_storage_rentals(ctx: ToolContext, storage_id: str = "", customer_id: str = "", lease_id: str = "") -> str:
    """Look up RV and boat storage rentals: space class and number, the unit stored, reservation and move-in dates, monthly rent, autopay and electric hookup, balance, deposits held and status.

    Args:
        storage_id: Storage rental reference number; leave "" if unknown.
        customer_id: Customer reference number of the renter; leave "" if unknown.
        lease_id: Lease reference number of the renter's site; leave "" if unknown.
    """
    match = _pick(storage_id=storage_id, customer_id=customer_id, lease_id=lease_id)
    if not match:
        return "Error: provide at least one reference number to search by."
    rows = ctx.find("storage_rentals", **match)
    return str(rows) if rows else f"No storage rentals for {match}."


@tool(owner="agent", rw="read")
def find_storage_ledger(ctx: ToolContext, storage_entry_id: str = "", storage_id: str = "",
                        customer_id: str = "", source_entry_id: str = "") -> str:
    """List the entries on a storage rental: rent and electric fees by month, late fees, one-time fees, payments, returned payments, credits, deposits and rate notices.

    Args:
        storage_entry_id: Reference number of one entry; leave "" if unknown.
        storage_id: Storage rental reference number; leave "" if unknown.
        customer_id: Customer reference number of the renter; leave "" if unknown.
        source_entry_id: Reference of the payment a return or returned-payment fee refers to; leave "" if unknown.
    """
    match = _pick(storage_entry_id=storage_entry_id, storage_id=storage_id, customer_id=customer_id, source_entry_id=source_entry_id)
    if not match:
        return "Error: provide at least one reference number to search by."
    rows = ctx.find("storage_ledger", **match)
    return str(rows) if rows else f"No storage ledger entries for {match}."


# --------------------------------------------------------------------------- home insurance
@tool(owner="agent", rw="read")
def find_insurance_policies(ctx: ToolContext, policy_id: str = "", customer_id: str = "", lease_id: str = "") -> str:
    """Look up manufactured-home insurance quotes and policies: form, policy number, insured home, limits and deductible, payment plan, loss payee, premium, claims count, term dates, any pending cancellation, premium balance and status.

    Args:
        policy_id: Policy record reference number; leave "" if unknown.
        customer_id: Customer reference number of the named insured; leave "" if unknown.
        lease_id: Lease reference number of the insured home's site; leave "" if unknown.
    """
    match = _pick(policy_id=policy_id, customer_id=customer_id, lease_id=lease_id)
    if not match:
        return "Error: provide at least one reference number to search by."
    rows = ctx.find("insurance_policies", **match)
    return str(rows) if rows else f"No insurance policies for {match}."


@tool(owner="agent", rw="read")
def find_insurance_transactions(ctx: ToolContext, insurance_txn_id: str = "", policy_id: str = "",
                                customer_id: str = "", source_txn_id: str = "") -> str:
    """List premium transactions on a policy: installments, policy and installment fees, endorsement premium, payments, escrow remittances, return premium, refunds and returned payments.

    Args:
        insurance_txn_id: Reference number of one transaction; leave "" if unknown.
        policy_id: Policy record reference number; leave "" if unknown.
        customer_id: Customer reference number of the named insured; leave "" if unknown.
        source_txn_id: Reference of the payment a return refers to; leave "" if unknown.
    """
    match = _pick(insurance_txn_id=insurance_txn_id, policy_id=policy_id, customer_id=customer_id, source_txn_id=source_txn_id)
    if not match:
        return "Error: provide at least one reference number to search by."
    rows = ctx.find("insurance_transactions", **match)
    return str(rows) if rows else f"No insurance transactions for {match}."


@tool(owner="agent", rw="read")
def find_insurance_notices(ctx: ToolContext, insurance_notice_id: str = "", policy_id: str = "", customer_id: str = "") -> str:
    """Look up policy notices: nonpayment cancellation notices, renewal offers and non-renewal notices, with dates, amounts and reasons.

    Args:
        insurance_notice_id: Reference number of one notice; leave "" if unknown.
        policy_id: Policy record reference number; leave "" if unknown.
        customer_id: Customer reference number of the named insured; leave "" if unknown.
    """
    match = _pick(insurance_notice_id=insurance_notice_id, policy_id=policy_id, customer_id=customer_id)
    if not match:
        return "Error: provide at least one reference number to search by."
    rows = ctx.find("insurance_notices", **match)
    return str(rows) if rows else f"No insurance notices for {match}."

"""Shared tools for env_0026_peer_to_peer_payments_app (Pocketwire).

Share tools are always present in their owner's tool list. This module holds only the
three foundations every difficulty reuses: one record finder per stored record type (the
customer finder doubling as the identity entry), the caller identity verification, and the
handoff to a human representative. Customer-originated actions and product actions are
hidden task tools authored per difficulty.

Scenario operational constants built in here:
  K = 3  identity attributes must match for verification to pass.
  R = 2  explicit requests for a human before a CUSTOMER_REQUESTED handoff.
"""

from erlbench import ToolContext, tool


def _only_given(**criteria):
    # Keep only the criteria the caller actually supplied.
    return {k: v for k, v in criteria.items() if v}


def _digits(value):
    return "".join(ch for ch in str(value or "") if ch.isdigit())


# --------------------------------------------------------------------------- customers
@tool(owner="agent", rw="read")
def find_customers(ctx: ToolContext, customer_id: str = "", phone_number: str = "",
                   email: str = "", name: str = "", username: str = "") -> str:
    """Look up a Pocketwire customer profile to establish whose account this conversation is about.

    Search by the customer reference number, or by what a caller can naturally tell you: the
    registered mobile number, the registered email address, the full name or the public
    @username. Every criterion is optional; give whichever you have, and add another one when
    several profiles match. The profile returned shows the customer reference number, name,
    @username, mobile number, email, date of birth, last four digits of the Social Security
    number, home ZIP code and the date the profile was created. Finding a profile does not
    verify the caller; identity is confirmed separately.

    Args:
        customer_id: The customer reference number, if already known; leave "" otherwise.
        phone_number: The registered US mobile number as the caller states it (10 digits); leave "" if not given.
        email: The registered email address as the caller states it; leave "" if not given.
        name: The customer's full name as the caller states it; leave "" if not given.
        username: The public Pocketwire @username as the caller states it (for example @maya-okafor); leave "" if not given.
    """
    match = _only_given(customer_id=customer_id, phone_number=phone_number, email=email,
                        name=name, username=username)
    if not match:
        return "Error: provide at least one detail (reference number, mobile number, email, name or @username)."
    rows = ctx.fuzzy_find("customers", **match)
    if not rows:
        return f"No customer profile matches {match}."
    if len(rows) > 1:
        return f"Error: {len(rows)} customer profiles match {match}; ask the caller for one more detail."
    return str(rows[0])


@tool(owner="agent", rw="write")
def verify_customer_identity(ctx: ToolContext, customer_id: str, phone_number: str = "",
                             email: str = "", date_of_birth: str = "", ssn_last4: str = "",
                             home_zip: str = "") -> str:
    """Verify the caller's identity against the customer profile and record the outcome.

    Identity must be verified before any account information is discussed or any money,
    card, limit or account status is changed. This tool performs the comparison itself: it
    checks each detail the caller gives against the profile on file and passes only when at
    least 3 of them match. The customer reference number only tells the tool which profile to
    compare against and never counts as a match. Pass only details the caller actually said,
    exactly as said, and leave the others empty. If a first attempt does not pass, ask for
    another detail and call again with everything the caller has given; once a caller is
    verified the verification stands.

    Args:
        customer_id: The customer reference number from the customer profile lookup. Required; used only to find the profile, not counted as a match.
        phone_number: The registered mobile number the caller states (10 digits); leave "" if not stated.
        email: The registered email address the caller states; leave "" if not stated.
        date_of_birth: The caller's date of birth as YYYY-MM-DD; leave "" if not stated.
        ssn_last4: The last four digits of the caller's Social Security number; leave "" if not stated.
        home_zip: The 5-digit ZIP code of the home address on file; leave "" if not stated.
    """
    if not customer_id:
        return "Error: customer_id is required; look the customer up first and pass their reference number."
    rows = ctx.find("customers", customer_id=customer_id)
    if not rows:
        return f"Error: no customer profile {customer_id}; cannot verify."
    rec = rows[0]
    # The tool owns the comparison. customer_id is the locator and is deliberately not counted.
    checks = [
        (phone_number, lambda v: _digits(v) == _digits(rec.get("phone_number")) and _digits(v) != ""),
        (email, lambda v: str(v).strip().casefold() == str(rec.get("email") or "").strip().casefold()),
        (date_of_birth, lambda v: str(v).strip() == str(rec.get("date_of_birth") or "")),
        (ssn_last4, lambda v: _digits(v) == _digits(rec.get("ssn_last4")) and _digits(v) != ""),
        (home_zip, lambda v: _digits(v) == _digits(rec.get("home_zip")) and _digits(v) != ""),
    ]
    matched = sum(1 for value, same in checks if value and same(value))
    verified = matched >= 3
    rid = ctx.make_id("ver_", customer_id)
    # Store only the reproducible boolean; upsert and never downgrade a pass.
    prior = ctx.find("identity_verifications", verification_id=rid)
    verified = verified or bool(prior and prior[0].get("verified"))
    if prior:
        ctx.update("identity_verifications", rid, verified=verified, verified_at=ctx.now())
    else:
        ctx.create("identity_verifications", rid, verification_id=rid, customer_id=customer_id,
                   verified=verified, verified_at=ctx.now())
    if verified:
        return f"Identity verified for customer {customer_id}."
    return (f"Identity NOT verified for customer {customer_id}: only {matched} of the required 3 details "
            "matched. Ask the caller for another detail on file and try again.")


@tool(owner="agent", rw="write")
def transfer_to_human_agent(ctx: ToolContext, customer_id: str, reason: str) -> str:
    """Hand the customer over to a human Pocketwire representative and record why.

    Use this in exactly two situations. POLICY_NOT_COVERED: the customer's request is one that
    no Pocketwire policy lets you resolve. CUSTOMER_REQUESTED: the customer has explicitly asked
    to speak with a human representative at least 2 times in this conversation. The handoff is
    recorded with its reason and the time it was made.

    Args:
        customer_id: The customer reference number from the customer profile lookup; the profile must exist.
        reason: Exactly one of POLICY_NOT_COVERED or CUSTOMER_REQUESTED; no other wording is accepted.
    """
    allowed = {"POLICY_NOT_COVERED", "CUSTOMER_REQUESTED"}
    if reason not in allowed:
        return f"Error: unknown handoff reason '{reason}'. Valid: {', '.join(sorted(allowed))}."
    if not ctx.find("customers", customer_id=customer_id):
        return f"Error: no customer profile {customer_id}; cannot record the handoff."
    rid = ctx.make_id("hof_", customer_id, reason)
    ctx.create("support_handoffs", rid, handoff_id=rid, customer_id=customer_id,
               reason=reason, created_at=ctx.now())
    return f"Handoff to a human representative recorded for customer {customer_id} ({reason})."


@tool(owner="agent", rw="read")
def find_identity_verifications(ctx: ToolContext, verification_id: str = "", customer_id: str = "") -> str:
    """Look up the recorded outcome of identity verification for a customer.

    Shows whether the caller has already been verified on this contact and when the latest
    attempt was made. Search by the customer reference number or the verification reference.

    Args:
        verification_id: Reference number of a verification record; leave "" if unknown.
        customer_id: The customer reference number; leave "" if unknown.
    """
    match = _only_given(verification_id=verification_id, customer_id=customer_id)
    if not match:
        return "Error: provide a customer reference number or a verification reference."
    rows = ctx.find("identity_verifications", **match)
    return str(rows) if rows else f"No identity verification recorded for {match}."


@tool(owner="agent", rw="read")
def find_support_handoffs(ctx: ToolContext, handoff_id: str = "", customer_id: str = "") -> str:
    """Look up handoffs of a customer to a human representative.

    Shows each recorded handoff with its reason and time. Search by the customer reference
    number or the handoff reference.

    Args:
        handoff_id: Reference number of a handoff record; leave "" if unknown.
        customer_id: The customer reference number; leave "" if unknown.
    """
    match = _only_given(handoff_id=handoff_id, customer_id=customer_id)
    if not match:
        return "Error: provide a customer reference number or a handoff reference."
    rows = ctx.find("support_handoffs", **match)
    return str(rows) if rows else f"No handoff recorded for {match}."


# --------------------------------------------------------------------------- personal account
@tool(owner="agent", rw="read")
def find_wallet_accounts(ctx: ToolContext, wallet_id: str = "", customer_id: str = "") -> str:
    """Look up Pocketwire Personal Accounts.

    Returns the account's plan, status, identity verification status, opening and closing
    dates, plan billing cycle and renewal date, any scheduled plan downgrade, the ledger
    balance, any approved weekly send limit and the date of the last limit decision, and the
    reason and time of any limitation or security lock with the dates it was lifted or
    recovered. Search by the account reference number or the customer reference number.

    Args:
        wallet_id: The personal account reference number; leave "" if unknown.
        customer_id: The customer reference number of the account holder; leave "" if unknown.
    """
    match = _only_given(wallet_id=wallet_id, customer_id=customer_id)
    if not match:
        return "Error: provide an account or customer reference number."
    rows = ctx.find("wallet_accounts", **match)
    return str(rows) if rows else f"No personal account found for {match}."


@tool(owner="agent", rw="read")
def find_wallet_transactions(ctx: ToolContext, txn_id: str = "", wallet_id: str = "",
                             customer_id: str = "", source_txn_id: str = "") -> str:
    """Look up activity on a Pocketwire Personal Account.

    Covers payments sent and received, invitation payments claimed or refunded, top-ups,
    direct deposits, cash-outs and returned cash-outs, fees and fee refunds, claim credits and
    reversals, and transfers to or from other Pocketwire products. Each entry shows its type,
    date, amount, app reference, counterparty and the details that apply to it (payment type,
    funding source, transfer speed, fee type, billing period, related original entry).
    Search by any reference number you have; use the related-entry reference to find, for
    example, the fee or refund belonging to a payment.

    Args:
        txn_id: Reference number of one activity entry; leave "" if unknown.
        wallet_id: The personal account reference number, to list the account's activity; leave "" if unknown.
        customer_id: The customer reference number, to list the customer's activity; leave "" if unknown.
        source_txn_id: Reference number of an original entry, to find the entries derived from it; leave "" if unknown.
    """
    match = _only_given(txn_id=txn_id, wallet_id=wallet_id, customer_id=customer_id,
                        source_txn_id=source_txn_id)
    if not match:
        return "Error: provide at least one reference number."
    rows = ctx.find("wallet_transactions", **match)
    return str(rows) if rows else f"No personal account activity found for {match}."


@tool(owner="agent", rw="read")
def find_wallet_claims(ctx: ToolContext, wallet_claim_id: str = "", wallet_id: str = "",
                       customer_id: str = "", txn_id: str = "") -> str:
    """Look up unauthorized-payment and purchase protection claims on a personal account.

    Each record shows whether it is the filing or the outcome of a claim, the disputed
    payment, claim type, report date, amount claimed, the customer's liability, the outcome
    and its date, and whether provisional credit had been posted. Search by the claim record,
    the account, the customer, or the disputed payment's reference number.

    Args:
        wallet_claim_id: Reference number of a claim record; leave "" if unknown.
        wallet_id: The personal account reference number; leave "" if unknown.
        customer_id: The customer reference number; leave "" if unknown.
        txn_id: Reference number of the disputed payment; leave "" if unknown.
    """
    match = _only_given(wallet_claim_id=wallet_claim_id, wallet_id=wallet_id,
                        customer_id=customer_id, txn_id=txn_id)
    if not match:
        return "Error: provide at least one reference number."
    rows = ctx.find("wallet_claims", **match)
    return str(rows) if rows else f"No claim found for {match}."


@tool(owner="agent", rw="read")
def find_wallet_requests(ctx: ToolContext, request_id: str = "", customer_id: str = "",
                         wallet_id: str = "") -> str:
    """Look up service requests on a personal account.

    Covers weekly send limit increase requests, documents submitted against a limitation, and
    account recovery requests, each with the requested limit where relevant, its status
    (submitted, approved, declined or withdrawn), the decision date and when it was
    submitted. Search by the request, customer or account reference number.

    Args:
        request_id: Reference number of a service request; leave "" if unknown.
        customer_id: The customer reference number; leave "" if unknown.
        wallet_id: The personal account reference number; leave "" if unknown.
    """
    match = _only_given(request_id=request_id, customer_id=customer_id, wallet_id=wallet_id)
    if not match:
        return "Error: provide at least one reference number."
    rows = ctx.find("wallet_requests", **match)
    return str(rows) if rows else f"No service request found for {match}."


# --------------------------------------------------------------------------- debit cards
@tool(owner="agent", rw="read")
def find_card_accounts(ctx: ToolContext, card_id: str = "", customer_id: str = "",
                       wallet_id: str = "", replaces_card_id: str = "") -> str:
    """Look up Pocketwire Visa debit cards.

    Returns each card's tier, status, form (physical, virtual or single-use virtual), last
    four digits, issue, activation, block and closing dates, expiry month, delivery speed,
    custom design, why it was issued, the block reason, and the card it replaced. Search by
    the card reference number, the customer, the personal account it draws on, or the card
    it replaced (to find a replacement).

    Args:
        card_id: The card reference number; leave "" if unknown.
        customer_id: The customer reference number of the cardholder; leave "" if unknown.
        wallet_id: The personal account reference number the card draws on; leave "" if unknown.
        replaces_card_id: Reference number of an earlier card, to find the card that replaced it; leave "" if unknown.
    """
    match = _only_given(card_id=card_id, customer_id=customer_id, wallet_id=wallet_id,
                        replaces_card_id=replaces_card_id)
    if not match:
        return "Error: provide at least one reference number."
    rows = ctx.find("card_accounts", **match)
    return str(rows) if rows else f"No debit card found for {match}."


@tool(owner="agent", rw="read")
def find_card_transactions(ctx: ToolContext, card_txn_id: str = "", card_id: str = "",
                           customer_id: str = "", source_txn_id: str = "") -> str:
    """Look up debit card activity.

    Covers authorization holds and their releases, settled purchases, ATM withdrawals, card
    fees and fee refunds, ATM surcharge reimbursements, merchant refunds, and dispute credits
    and reversals. Each entry shows its type, date, amount, network reference, merchant and
    category, how the purchase was made, whether it was foreign, the ATM network and owner
    surcharge, the hold type, the fee type and the related original entry. Search by any
    reference number you have.

    Args:
        card_txn_id: Reference number of one card activity entry; leave "" if unknown.
        card_id: The card reference number, to list the card's activity; leave "" if unknown.
        customer_id: The customer reference number, to list activity on all of the customer's cards; leave "" if unknown.
        source_txn_id: Reference number of an original entry, to find the entries derived from it; leave "" if unknown.
    """
    match = _only_given(card_txn_id=card_txn_id, card_id=card_id, customer_id=customer_id,
                        source_txn_id=source_txn_id)
    if not match:
        return "Error: provide at least one reference number."
    rows = ctx.find("card_transactions", **match)
    return str(rows) if rows else f"No card activity found for {match}."


@tool(owner="agent", rw="read")
def find_card_disputes(ctx: ToolContext, card_dispute_id: str = "", card_id: str = "",
                       customer_id: str = "", card_txn_id: str = "") -> str:
    """Look up debit card disputes.

    Each record shows whether it is the filing or the outcome of a dispute, the disputed card
    transaction, the dispute reason, report date, disputed amount, the customer's liability,
    the outcome and its date, and whether provisional credit had been posted. Search by the
    dispute record, the card, the customer or the disputed transaction's reference number.

    Args:
        card_dispute_id: Reference number of a dispute record; leave "" if unknown.
        card_id: The card reference number; leave "" if unknown.
        customer_id: The customer reference number; leave "" if unknown.
        card_txn_id: Reference number of the disputed card transaction; leave "" if unknown.
    """
    match = _only_given(card_dispute_id=card_dispute_id, card_id=card_id,
                        customer_id=customer_id, card_txn_id=card_txn_id)
    if not match:
        return "Error: provide at least one reference number."
    rows = ctx.find("card_disputes", **match)
    return str(rows) if rows else f"No card dispute found for {match}."


# --------------------------------------------------------------------------- rewards
@tool(owner="agent", rw="read")
def find_rewards_memberships(ctx: ToolContext, membership_id: str = "", customer_id: str = "",
                             wallet_id: str = "") -> str:
    """Look up Pocketwire Rewards memberships.

    Returns the rewards tier, membership status, enrolment and closing dates, points
    balance, the date the tier was assigned and the next quarterly review date, how many
    reviews in a row fell below retention spend, and any suspension reason. Search by the
    membership, customer or personal account reference number.

    Args:
        membership_id: The rewards membership reference number; leave "" if unknown.
        customer_id: The customer reference number of the member; leave "" if unknown.
        wallet_id: The personal account reference number cash redemptions are paid into; leave "" if unknown.
    """
    match = _only_given(membership_id=membership_id, customer_id=customer_id, wallet_id=wallet_id)
    if not match:
        return "Error: provide at least one reference number."
    rows = ctx.find("rewards_memberships", **match)
    return str(rows) if rows else f"No rewards membership found for {match}."


@tool(owner="agent", rw="read")
def find_rewards_ledger(ctx: ToolContext, rewards_entry_id: str = "", membership_id: str = "",
                        customer_id: str = "", source_txn_id: str = "") -> str:
    """Look up Pocketwire Rewards points activity.

    Covers points earned on card purchases, boost activations and boost points, clawbacks,
    redemptions and their fulfilment or reversal, expiries, referral and milestone or
    anniversary bonuses, and courtesy credits. Each entry shows its type, date, points, the
    purchase or redemption it relates to, the spend and merchant category, the boost offer
    code, and redemption details. Search by any reference number you have; use a card
    purchase's reference number to see the points earned or clawed back on it.

    Args:
        rewards_entry_id: Reference number of one rewards entry; leave "" if unknown.
        membership_id: The rewards membership reference number, to list its activity; leave "" if unknown.
        customer_id: The customer reference number; leave "" if unknown.
        source_txn_id: Reference number of the card purchase or redemption an entry relates to; leave "" if unknown.
    """
    match = _only_given(rewards_entry_id=rewards_entry_id, membership_id=membership_id,
                        customer_id=customer_id, source_txn_id=source_txn_id)
    if not match:
        return "Error: provide at least one reference number."
    rows = ctx.find("rewards_ledger", **match)
    return str(rows) if rows else f"No rewards activity found for {match}."


# --------------------------------------------------------------------------- business
@tool(owner="agent", rw="read")
def find_business_profiles(ctx: ToolContext, business_id: str = "", customer_id: str = "",
                           wallet_id: str = "") -> str:
    """Look up Pocketwire Business Profiles.

    Returns the business name and legal form, business tier, status, opening and closing
    dates, business balance, any rolling reserve percentage and when it was set, the next
    monthly tier review, months below retention volume, and the reason and start time of any
    risk review. Search by the business profile, owner or owner's personal account reference
    number.

    Args:
        business_id: The business profile reference number; leave "" if unknown.
        customer_id: The customer reference number of the owner; leave "" if unknown.
        wallet_id: The owner's personal account reference number; leave "" if unknown.
    """
    match = _only_given(business_id=business_id, customer_id=customer_id, wallet_id=wallet_id)
    if not match:
        return "Error: provide at least one reference number."
    rows = ctx.find("business_profiles", **match)
    return str(rows) if rows else f"No business profile found for {match}."


@tool(owner="agent", rw="read")
def find_business_transactions(ctx: ToolContext, business_txn_id: str = "", business_id: str = "",
                               customer_id: str = "", source_txn_id: str = "") -> str:
    """Look up business profile activity.

    Covers sales, business fees and fee credits, refunds to buyers, chargebacks and their
    reversals, payouts and returned payouts, negative balance recoveries, holds on sale funds
    and their releases, and carrier delivery confirmations. Each entry shows its type, date,
    amount, app reference, buyer, sale channel and buyer region, fee type, payout method,
    hold type and release due date, tracking number and the related original entry. Search by
    any reference number you have; use a sale's reference number to find its fees, holds,
    refunds and delivery confirmation.

    Args:
        business_txn_id: Reference number of one business activity entry; leave "" if unknown.
        business_id: The business profile reference number, to list its activity; leave "" if unknown.
        customer_id: The customer reference number of the owner; leave "" if unknown.
        source_txn_id: Reference number of an original entry, to find the entries derived from it; leave "" if unknown.
    """
    match = _only_given(business_txn_id=business_txn_id, business_id=business_id,
                        customer_id=customer_id, source_txn_id=source_txn_id)
    if not match:
        return "Error: provide at least one reference number."
    rows = ctx.find("business_transactions", **match)
    return str(rows) if rows else f"No business activity found for {match}."


@tool(owner="agent", rw="read")
def find_business_claims(ctx: ToolContext, business_claim_id: str = "", business_id: str = "",
                         customer_id: str = "", sale_txn_id: str = "") -> str:
    """Look up buyer claims against a business profile's sales.

    Each record shows whether it is the opening, the seller's response or the outcome of a
    claim, the sale claimed against, the claim reason and amount, the opening date, the
    response type, date and tracking number, and the outcome and its date. Search by the
    claim record, business profile, owner, or the sale's reference number.

    Args:
        business_claim_id: Reference number of a claim record; leave "" if unknown.
        business_id: The business profile reference number; leave "" if unknown.
        customer_id: The customer reference number of the owner; leave "" if unknown.
        sale_txn_id: Reference number of the sale claimed against; leave "" if unknown.
    """
    match = _only_given(business_claim_id=business_claim_id, business_id=business_id,
                        customer_id=customer_id, sale_txn_id=sale_txn_id)
    if not match:
        return "Error: provide at least one reference number."
    rows = ctx.find("business_claims", **match)
    return str(rows) if rows else f"No buyer claim found for {match}."


@tool(owner="agent", rw="read")
def find_business_requests(ctx: ToolContext, request_id: str = "", customer_id: str = "",
                           business_id: str = "") -> str:
    """Look up service requests on a business profile.

    Covers documents submitted against a risk review and requests to reduce or remove a
    rolling reserve, each with the requested reserve where relevant, its status (submitted,
    approved, declined or withdrawn), the decision date and when it was submitted. Search by
    the request, owner or business profile reference number.

    Args:
        request_id: Reference number of a business service request; leave "" if unknown.
        customer_id: The customer reference number of the owner; leave "" if unknown.
        business_id: The business profile reference number; leave "" if unknown.
    """
    match = _only_given(request_id=request_id, customer_id=customer_id, business_id=business_id)
    if not match:
        return "Error: provide at least one reference number."
    rows = ctx.find("business_requests", **match)
    return str(rows) if rows else f"No business service request found for {match}."


# --------------------------------------------------------------------------- advances
@tool(owner="agent", rw="read")
def find_advance_lines(ctx: ToolContext, advance_line_id: str = "", customer_id: str = "",
                       wallet_id: str = "") -> str:
    """Look up Pocketwire Advance lines.

    Returns the advance tier, status, application and closing dates, the amount currently
    owed, the next monthly review date, on-time repayments in a row, months below the direct
    deposit requirement, and the dates the line became past due or was suspended. Search by
    the advance line, customer or linked personal account reference number.

    Args:
        advance_line_id: The advance line reference number; leave "" if unknown.
        customer_id: The customer reference number of the borrower; leave "" if unknown.
        wallet_id: The linked personal account reference number; leave "" if unknown.
    """
    match = _only_given(advance_line_id=advance_line_id, customer_id=customer_id, wallet_id=wallet_id)
    if not match:
        return "Error: provide at least one reference number."
    rows = ctx.find("advance_lines", **match)
    return str(rows) if rows else f"No advance line found for {match}."


@tool(owner="agent", rw="read")
def find_advance_ledger(ctx: ToolContext, advance_entry_id: str = "", advance_line_id: str = "",
                        customer_id: str = "", source_txn_id: str = "") -> str:
    """Look up Pocketwire Advance activity.

    Covers advances disbursed, fees, repayments, fee waivers, due-date extensions and
    write-offs. Each entry shows its type, date, amount, advance reference, the moment of
    disbursement, delivery destination and speed, due date and any new due date, the fee
    type and period, the repayment method and attempt, and the waiver reason. Search by any
    reference number you have; use an advance's reference number to see everything booked
    against it.

    Args:
        advance_entry_id: Reference number of one advance entry (for a disbursement, the advance itself); leave "" if unknown.
        advance_line_id: The advance line reference number, to list its activity; leave "" if unknown.
        customer_id: The customer reference number; leave "" if unknown.
        source_txn_id: Reference number of an advance or fee, to find the entries booked against it; leave "" if unknown.
    """
    match = _only_given(advance_entry_id=advance_entry_id, advance_line_id=advance_line_id,
                        customer_id=customer_id, source_txn_id=source_txn_id)
    if not match:
        return "Error: provide at least one reference number."
    rows = ctx.find("advance_ledger", **match)
    return str(rows) if rows else f"No advance activity found for {match}."


# --------------------------------------------------------------------------- savings
@tool(owner="agent", rw="read")
def find_savings_vaults(ctx: ToolContext, vault_id: str = "", customer_id: str = "",
                        wallet_id: str = "") -> str:
    """Look up Pocketwire Savings Vaults.

    Returns each vault's name, tier, status, opening and closing dates, balance, savings goal
    and when it was set, round-up multiplier, time-lock dates and any freeze reason. Search
    by the vault, customer or linked personal account reference number.

    Args:
        vault_id: The savings vault reference number; leave "" if unknown.
        customer_id: The customer reference number of the saver; leave "" if unknown.
        wallet_id: The linked personal account reference number; leave "" if unknown.
    """
    match = _only_given(vault_id=vault_id, customer_id=customer_id, wallet_id=wallet_id)
    if not match:
        return "Error: provide at least one reference number."
    rows = ctx.find("savings_vaults", **match)
    return str(rows) if rows else f"No savings vault found for {match}."


@tool(owner="agent", rw="read")
def find_savings_ledger(ctx: ToolContext, savings_entry_id: str = "", vault_id: str = "",
                        customer_id: str = "", source_txn_id: str = "") -> str:
    """Look up Pocketwire Savings Vault activity.

    Covers deposits, withdrawals, monthly interest, excess withdrawal fees, goal bonuses and
    forfeited time-lock bonuses. Each entry shows its type, date, amount, deposit source or
    withdrawal destination, withdrawal reference, interest month, and the goal or lock it
    relates to. Search by any reference number you have.

    Args:
        savings_entry_id: Reference number of one savings entry; leave "" if unknown.
        vault_id: The savings vault reference number, to list its activity; leave "" if unknown.
        customer_id: The customer reference number; leave "" if unknown.
        source_txn_id: Reference number of the originating purchase, deposit or withdrawal; leave "" if unknown.
    """
    match = _only_given(savings_entry_id=savings_entry_id, vault_id=vault_id,
                        customer_id=customer_id, source_txn_id=source_txn_id)
    if not match:
        return "Error: provide at least one reference number."
    rows = ctx.find("savings_ledger", **match)
    return str(rows) if rows else f"No savings activity found for {match}."


# --------------------------------------------------------------------------- pay in 4
@tool(owner="agent", rw="read")
def find_paylater_accounts(ctx: ToolContext, paylater_id: str = "", customer_id: str = "",
                           wallet_id: str = "") -> str:
    """Look up Pocketwire Pay in 4 accounts.

    Returns the Pay in 4 tier, status, application and closing dates, the amount currently
    owed, plans paid on time, the next review date and the date the account became past due.
    Search by the Pay in 4 account, customer or linked personal account reference number.

    Args:
        paylater_id: The Pay in 4 account reference number; leave "" if unknown.
        customer_id: The customer reference number; leave "" if unknown.
        wallet_id: The linked personal account reference number; leave "" if unknown.
    """
    match = _only_given(paylater_id=paylater_id, customer_id=customer_id, wallet_id=wallet_id)
    if not match:
        return "Error: provide at least one reference number."
    rows = ctx.find("paylater_accounts", **match)
    return str(rows) if rows else f"No Pay in 4 account found for {match}."


@tool(owner="agent", rw="read")
def find_paylater_ledger(ctx: ToolContext, paylater_entry_id: str = "", paylater_id: str = "",
                         customer_id: str = "", source_txn_id: str = "") -> str:
    """Look up Pocketwire Pay in 4 plans and their activity.

    Covers plans created, installments paid, late fees and waivers, merchant refund
    adjustments, schedule changes, disputes and write-offs. Each entry shows its type, date,
    amount, plan reference and merchant, installment number, payment method, new due date,
    and dispute reason or outcome. Search by any reference number you have; use a plan's
    reference number to see everything booked against it.

    Args:
        paylater_entry_id: Reference number of one Pay in 4 entry (for a plan, the plan itself); leave "" if unknown.
        paylater_id: The Pay in 4 account reference number, to list its activity; leave "" if unknown.
        customer_id: The customer reference number; leave "" if unknown.
        source_txn_id: Reference number of a plan, to find the entries booked against it; leave "" if unknown.
    """
    match = _only_given(paylater_entry_id=paylater_entry_id, paylater_id=paylater_id,
                        customer_id=customer_id, source_txn_id=source_txn_id)
    if not match:
        return "Error: provide at least one reference number."
    rows = ctx.find("paylater_ledger", **match)
    return str(rows) if rows else f"No Pay in 4 activity found for {match}."

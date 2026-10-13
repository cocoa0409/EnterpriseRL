"""Shared tools for env_0045_vacation_rental_platform (Roamhaven host and guest support).

Every tool here is a SHARE tool: always present in its owner's tool list. This module holds the
three foundation utilities every difficulty reuses: one finder per record type (the customer
finder doubling as the identity entry), the identity-verification write, and the hand-over to a
human representative. Customer-initiated writes and every business write live as hidden task tools
in each difficulty's task_tools.py.

Scenario operating constants (not business policy):
  - Identity verification passes when at least K = 2 of the stated credentials match the profile.
  - A caller who explicitly asks for a human representative R = 2 times is handed over as
    CUSTOMER_REQUESTED.
"""

from erlbench import ToolContext, tool


def _match(**kwargs) -> dict:
    # Keep only the criteria actually supplied.
    return {k: v for k, v in kwargs.items() if v}


# --------------------------------------------------------------------------- customers
@tool(owner="agent", rw="read")
def find_customers(ctx: ToolContext, customer_id: str = "", name: str = "", email: str = "",
                   phone_number: str = "") -> str:
    """Look up the Roamhaven customer profile a caller is speaking about.

    A profile belongs to one person, whether they travel as a guest, host as a host, or both. You
    can search by the customer reference number, or by what the caller naturally tells you: their
    full name, the email address on the profile, or the registered mobile number. Every criterion is
    optional; give whichever you have, and add another when more than one profile matches. The
    profile returned shows the customer reference number, name, contact details, date of birth, the
    last four characters of the identity document verified at sign-up, the date the profile was
    created and the country of residence. Finding a profile does not confirm who the caller is;
    identity is confirmed separately.

    Args:
        customer_id: The customer reference number, if already known; leave "" otherwise.
        name: The caller's full name as they state it; leave "" if not given.
        email: The email address the caller says is on the profile; leave "" if not given.
        phone_number: The mobile number the caller says is on the profile, 10 digits without the
            country code; leave "" if not given.
    """
    match = _match(customer_id=customer_id, name=name, email=email, phone_number=phone_number)
    if not match:
        return "Error: provide at least one reference number or profile detail to find the customer."
    rows = ctx.fuzzy_find("customers", **match)
    if not rows:
        return f"No customer profile matches {match}."
    if len(rows) > 1:
        return f"Error: {len(rows)} customer profiles match {match}; ask the caller for one more detail."
    return str(rows[0])


# --------------------------------------------------------------------------- stays
@tool(owner="agent", rw="read")
def find_stays(ctx: ToolContext, stay_id: str = "", customer_id: str = "", listing_id: str = "",
               host_account_id: str = "") -> str:
    """Look up guest reservations (stays).

    Each stay shows its cancellation policy, status, confirmation code, rate type, payment plan,
    booking channel, service-fee structure, booking moment, check-in and check-out dates, nights,
    guests and pets, the full price breakdown frozen at booking (nightly subtotal and discount,
    cleaning, pet and extra-guest fees, guest service fee, occupancy tax, total), the tax
    jurisdiction and, when cancelled, the cancellation moment. Search by the stay's own reference
    number, by the guest, by the listing, or by the host account; every criterion is optional and
    any combination narrows the result.

    Args:
        stay_id: The stay reference number; leave "" if unknown.
        customer_id: The guest's customer reference number, to list that guest's stays; leave "" if unknown.
        listing_id: The listing reference number, to list stays at that listing; leave "" if unknown.
        host_account_id: The host account reference number, to list stays hosted by it; leave "" if unknown.
    """
    match = _match(stay_id=stay_id, customer_id=customer_id, listing_id=listing_id,
                   host_account_id=host_account_id)
    rows = ctx.find("stays", **match)
    return str(rows) if rows else f"No stays found for {match}."


@tool(owner="agent", rw="read")
def find_stay_transactions(ctx: ToolContext, stay_txn_id: str = "", stay_id: str = "",
                           customer_id: str = "", request_id: str = "") -> str:
    """Look up the money and review history of stays.

    Returns every collection, failed payment attempt, refund and review recorded on stays: the kind
    of record, when it was posted, the amount, the installment and attempt numbers, and for refunds
    the charge component, the reason, who funded it, whether it came before or after the host's
    payout release, and the request it rests on; for reviews, who wrote it and the star rating.
    Search by the record's own reference number, by stay, by guest, or by the stay request it
    belongs to; every criterion is optional.

    Args:
        stay_txn_id: The reference number of one stay record; leave "" if unknown.
        stay_id: The stay reference number, to list everything recorded on that stay; leave "" if unknown.
        customer_id: The guest's customer reference number; leave "" if unknown.
        request_id: The stay request reference number a refund or collection rests on; leave "" if unknown.
    """
    match = _match(stay_txn_id=stay_txn_id, stay_id=stay_id, customer_id=customer_id,
                   request_id=request_id)
    rows = ctx.find("stay_transactions", **match)
    return str(rows) if rows else f"No stay records found for {match}."


@tool(owner="agent", rw="read")
def find_stay_requests(ctx: ToolContext, request_id: str = "", stay_id: str = "",
                       customer_id: str = "") -> str:
    """Look up requests made on stays: date changes, guest-count changes, travel issues and major
    disruptive event requests.

    Each request shows its kind, its outcome (submitted, accepted, declined, lapsed, approved,
    denied or withdrawn), when it was submitted and decided, the new dates or guest count asked for,
    and for travel issues the issue category and when the guest discovered it. Search by request,
    stay or guest; every criterion is optional.

    Args:
        request_id: The stay request reference number; leave "" if unknown.
        stay_id: The stay reference number, to list requests on that stay; leave "" if unknown.
        customer_id: The guest's customer reference number; leave "" if unknown.
    """
    match = _match(request_id=request_id, stay_id=stay_id, customer_id=customer_id)
    rows = ctx.find("stay_requests", **match)
    return str(rows) if rows else f"No stay requests found for {match}."


# --------------------------------------------------------------------------- listings
@tool(owner="agent", rw="read")
def find_listings(ctx: ToolContext, listing_id: str = "", customer_id: str = "",
                  host_account_id: str = "") -> str:
    """Look up host listings.

    Each listing shows its space type, status, title, jurisdiction and registration number, the
    cancellation policy it offers to new bookings, the host's current settings (nightly rate,
    cleaning and short-stay cleaning fees, pet fee, extra-guest fee and threshold, discounts,
    new-listing promotion, minimum stay, Instant Book), capacity, bedrooms and photo count, its
    creation and first-published dates, and any suspension reason and date or removal date. Search
    by listing, by the host's customer reference number, or by host account; every criterion is
    optional.

    Args:
        listing_id: The listing reference number; leave "" if unknown.
        customer_id: The host's customer reference number, to list that host's listings; leave "" if unknown.
        host_account_id: The host account reference number; leave "" if unknown.
    """
    match = _match(listing_id=listing_id, customer_id=customer_id, host_account_id=host_account_id)
    rows = ctx.find("listings", **match)
    return str(rows) if rows else f"No listings found for {match}."


@tool(owner="agent", rw="read")
def find_listing_events(ctx: ToolContext, listing_event_id: str = "", listing_id: str = "",
                        customer_id: str = "", stay_id: str = "") -> str:
    """Look up the history of listings: fee and rate changes, calendar blocks after host
    cancellations, quarterly quality assessments and jurisdiction registration notices.

    Each record shows its kind and date; fee changes show which setting changed with the old and new
    value; calendar blocks show the cancelled stay and the blocked nights; quality assessments show
    the quarter, average rating, review count and outcome; registration notices show the notice
    kind, the jurisdiction's notice reference and the cure deadline. Search by record, listing, host
    or the stay a block concerns; every criterion is optional.

    Args:
        listing_event_id: The reference number of one listing record; leave "" if unknown.
        listing_id: The listing reference number; leave "" if unknown.
        customer_id: The host's customer reference number; leave "" if unknown.
        stay_id: The stay reference number a calendar block concerns; leave "" if unknown.
    """
    match = _match(listing_event_id=listing_event_id, listing_id=listing_id,
                   customer_id=customer_id, stay_id=stay_id)
    rows = ctx.find("listing_events", **match)
    return str(rows) if rows else f"No listing records found for {match}."


@tool(owner="agent", rw="read")
def find_listing_reinstatement_requests(ctx: ToolContext, reinstatement_request_id: str = "",
                                        listing_id: str = "", customer_id: str = "") -> str:
    """Look up requests to reinstate suspended listings.

    Each request shows the suspension it seeks to lift, the listing review team's decision
    (submitted, approved or denied), when it was submitted and decided, and any registration number
    supplied with it. Search by request, listing or host; every criterion is optional.

    Args:
        reinstatement_request_id: The reinstatement request reference number; leave "" if unknown.
        listing_id: The listing reference number; leave "" if unknown.
        customer_id: The host's customer reference number; leave "" if unknown.
    """
    match = _match(reinstatement_request_id=reinstatement_request_id, listing_id=listing_id,
                   customer_id=customer_id)
    rows = ctx.find("listing_reinstatement_requests", **match)
    return str(rows) if rows else f"No reinstatement requests found for {match}."


# --------------------------------------------------------------------------- host accounts
@tool(owner="agent", rw="read")
def find_host_accounts(ctx: ToolContext, host_account_id: str = "", customer_id: str = "") -> str:
    """Look up host accounts.

    Each host account shows its host tier, status, opening, verification and closing dates, any
    registered business name, the taxpayer form on file and tax residency, the date Superhost was
    awarded, the last tier change, the end of any restriction and the date of any suspension. Search
    by the host account reference number or by the host's customer reference number; every
    criterion is optional.

    Args:
        host_account_id: The host account reference number; leave "" if unknown.
        customer_id: The host's customer reference number; leave "" if unknown.
    """
    match = _match(host_account_id=host_account_id, customer_id=customer_id)
    rows = ctx.find("host_accounts", **match)
    return str(rows) if rows else f"No host accounts found for {match}."


@tool(owner="agent", rw="read")
def find_host_account_events(ctx: ToolContext, host_event_id: str = "", host_account_id: str = "",
                             customer_id: str = "", stay_id: str = "", appeal_id: str = "",
                             original_event_id: str = "") -> str:
    """Look up the history of host accounts: host service fees and their refunds, host
    cancellations, cancellation penalties and waivers, policy strikes, Superhost assessments,
    Superhost travel credits and tax forms.

    Each record shows its kind and date and, as applicable, the stay, the amount and the base it was
    computed on, the cancellation timing band and who initiated the cancellation, the appeal and
    reason behind a waiver and the penalty it gives back, the strike type, the assessment quarter
    with its rating, response rate, cancellation rate, stays, nights, outcome and tier effect, and
    the tax year with its transaction count. Search by record, host account, host, stay, appeal, or
    the original record a waiver refers to; every criterion is optional.

    Args:
        host_event_id: The reference number of one host account record; leave "" if unknown.
        host_account_id: The host account reference number; leave "" if unknown.
        customer_id: The host's customer reference number; leave "" if unknown.
        stay_id: The stay reference number; leave "" if unknown.
        appeal_id: The host appeal reference number a waiver rests on; leave "" if unknown.
        original_event_id: The reference number of the penalty record a waiver gives back; leave "" if unknown.
    """
    match = _match(host_event_id=host_event_id, host_account_id=host_account_id,
                   customer_id=customer_id, stay_id=stay_id, appeal_id=appeal_id,
                   original_event_id=original_event_id)
    rows = ctx.find("host_account_events", **match)
    return str(rows) if rows else f"No host account records found for {match}."


@tool(owner="agent", rw="read")
def find_host_appeals(ctx: ToolContext, appeal_id: str = "", host_account_id: str = "",
                      customer_id: str = "", related_event_id: str = "") -> str:
    """Look up host appeals against suspensions, restrictions, policy strikes and cancellation
    penalties.

    Each appeal shows what it appeals, the strike or penalty it concerns, the documented reason
    claimed on a penalty appeal, the review team's decision (submitted, approved or denied), and
    when it was submitted and decided. Search by appeal, host account, host, or the strike or
    penalty record appealed; every criterion is optional.

    Args:
        appeal_id: The host appeal reference number; leave "" if unknown.
        host_account_id: The host account reference number; leave "" if unknown.
        customer_id: The host's customer reference number; leave "" if unknown.
        related_event_id: The reference number of the strike or penalty record appealed; leave "" if unknown.
    """
    match = _match(appeal_id=appeal_id, host_account_id=host_account_id, customer_id=customer_id,
                   related_event_id=related_event_id)
    rows = ctx.find("host_appeals", **match)
    return str(rows) if rows else f"No host appeals found for {match}."


# --------------------------------------------------------------------------- payouts
@tool(owner="agent", rw="read")
def find_payout_methods(ctx: ToolContext, payout_method_id: str = "", customer_id: str = "",
                        host_account_id: str = "", routed_listing_id: str = "") -> str:
    """Look up the payout methods a host receives earnings through.

    Each method shows its payout rail, status, the dates it was added, verified and removed, whether
    it is the default and since when, the last four characters of the account, card or receiver
    number, the payout currency, any listing routed to it, and why it is on hold if it is. Search by
    method, host, host account, or the listing routed to a method; every criterion is optional.

    Args:
        payout_method_id: The payout method reference number; leave "" if unknown.
        customer_id: The host's customer reference number; leave "" if unknown.
        host_account_id: The host account reference number; leave "" if unknown.
        routed_listing_id: The listing reference number whose earnings are routed to a method; leave "" if unknown.
    """
    match = _match(payout_method_id=payout_method_id, customer_id=customer_id,
                   host_account_id=host_account_id, routed_listing_id=routed_listing_id)
    rows = ctx.find("payout_methods", **match)
    return str(rows) if rows else f"No payout methods found for {match}."


@tool(owner="agent", rw="read")
def find_payout_transactions(ctx: ToolContext, payout_txn_id: str = "", payout_method_id: str = "",
                             customer_id: str = "", stay_id: str = "",
                             source_event_id: str = "") -> str:
    """Look up the payout ledger: earnings released for stays, transfers sent, rail fees, tax
    withholding, returned transfers, deductions, credits, and payout holds and their release.

    Each record shows its kind, date, amount and, as applicable, the stay and installment, the
    record that created it, the fee, deduction, credit, hold or return kind. Search by record,
    payout method, host, stay, or the originating record; every criterion is optional.

    Args:
        payout_txn_id: The reference number of one payout record; leave "" if unknown.
        payout_method_id: The payout method reference number; leave "" if unknown.
        customer_id: The host's customer reference number; leave "" if unknown.
        stay_id: The stay reference number; leave "" if unknown.
        source_event_id: The reference number of the record that created a payout record; leave "" if unknown.
    """
    match = _match(payout_txn_id=payout_txn_id, payout_method_id=payout_method_id,
                   customer_id=customer_id, stay_id=stay_id, source_event_id=source_event_id)
    rows = ctx.find("payout_transactions", **match)
    return str(rows) if rows else f"No payout records found for {match}."


# --------------------------------------------------------------------------- HostCover
@tool(owner="agent", rw="read")
def find_protection_plans(ctx: ToolContext, protection_plan_id: str = "", customer_id: str = "",
                          host_account_id: str = "", listing_id: str = "") -> str:
    """Look up HostCover damage protection plans held on listings.

    Each plan shows its HostCover level, status, the listing covered, the enrollment and effective
    dates, the start of the current plan year, the last level change and any cancellation or lapse
    date. Search by plan, host, host account or listing; every criterion is optional.

    Args:
        protection_plan_id: The HostCover plan reference number; leave "" if unknown.
        customer_id: The host's customer reference number; leave "" if unknown.
        host_account_id: The host account reference number; leave "" if unknown.
        listing_id: The listing reference number; leave "" if unknown.
    """
    match = _match(protection_plan_id=protection_plan_id, customer_id=customer_id,
                   host_account_id=host_account_id, listing_id=listing_id)
    rows = ctx.find("protection_plans", **match)
    return str(rows) if rows else f"No HostCover plans found for {match}."


@tool(owner="agent", rw="read")
def find_protection_events(ctx: ToolContext, protection_event_id: str = "",
                           protection_plan_id: str = "", customer_id: str = "", claim_id: str = "",
                           stay_id: str = "") -> str:
    """Look up the HostCover ledger: premiums and premium refunds, payment requests sent to guests,
    guest payments and reversals, reimbursements, recoveries and claim denials.

    Each record shows its kind, date, amount and, as applicable, the claim and stay, the premium
    base, the verified loss, the guest's response and the denial reason. Search by record, plan,
    host, claim or stay; every criterion is optional.

    Args:
        protection_event_id: The reference number of one HostCover record; leave "" if unknown.
        protection_plan_id: The HostCover plan reference number; leave "" if unknown.
        customer_id: The host's customer reference number; leave "" if unknown.
        claim_id: The damage claim reference number; leave "" if unknown.
        stay_id: The stay reference number; leave "" if unknown.
    """
    match = _match(protection_event_id=protection_event_id, protection_plan_id=protection_plan_id,
                   customer_id=customer_id, claim_id=claim_id, stay_id=stay_id)
    rows = ctx.find("protection_events", **match)
    return str(rows) if rows else f"No HostCover records found for {match}."


@tool(owner="agent", rw="read")
def find_protection_claims(ctx: ToolContext, claim_id: str = "", protection_plan_id: str = "",
                           customer_id: str = "", listing_id: str = "", stay_id: str = "") -> str:
    """Look up damage claims filed by hosts under HostCover.

    Each claim shows the damage category, the amount claimed, the age of the damaged item, when it
    was filed, when the guest's response window closes, when it was escalated, its stage, whether
    the claims team found the evidence complete, the loss the claims team verified, and when it was
    decided. Search by claim, plan, host, listing or stay; every criterion is optional.

    Args:
        claim_id: The damage claim reference number; leave "" if unknown.
        protection_plan_id: The HostCover plan reference number; leave "" if unknown.
        customer_id: The host's customer reference number; leave "" if unknown.
        listing_id: The listing reference number; leave "" if unknown.
        stay_id: The stay reference number; leave "" if unknown.
    """
    match = _match(claim_id=claim_id, protection_plan_id=protection_plan_id,
                   customer_id=customer_id, listing_id=listing_id, stay_id=stay_id)
    rows = ctx.find("protection_claims", **match)
    return str(rows) if rows else f"No damage claims found for {match}."


# --------------------------------------------------------------------------- Rewards
@tool(owner="agent", rw="read")
def find_rewards_memberships(ctx: ToolContext, rewards_membership_id: str = "",
                             customer_id: str = "") -> str:
    """Look up Roamhaven Rewards memberships.

    Each membership shows its Rewards tier, status, enrollment and closing dates, the last day the
    current tier is held and the date of the latest earning or redemption. Search by membership or
    by the guest's customer reference number; every criterion is optional.

    Args:
        rewards_membership_id: The Rewards membership reference number; leave "" if unknown.
        customer_id: The guest's customer reference number; leave "" if unknown.
    """
    match = _match(rewards_membership_id=rewards_membership_id, customer_id=customer_id)
    rows = ctx.find("rewards_memberships", **match)
    return str(rows) if rows else f"No Rewards memberships found for {match}."


@tool(owner="agent", rw="read")
def find_rewards_transactions(ctx: ToolContext, rewards_txn_id: str = "",
                              rewards_membership_id: str = "", customer_id: str = "",
                              stay_id: str = "", original_txn_id: str = "") -> str:
    """Look up Rewards credit history: credits earned, bonuses, redemptions, reinstatements,
    expiries and clawbacks.

    Each record shows its kind, date, credits moved and, as applicable, the stay, the eligible
    spend, the bonus kind, the original record it refers to and the expiry of reinstated credits.
    Search by record, membership, guest, stay, or the original record; every criterion is optional.

    Args:
        rewards_txn_id: The reference number of one credit record; leave "" if unknown.
        rewards_membership_id: The Rewards membership reference number; leave "" if unknown.
        customer_id: The guest's customer reference number; leave "" if unknown.
        stay_id: The stay reference number; leave "" if unknown.
        original_txn_id: The reference number of the credit record another one refers to; leave "" if unknown.
    """
    match = _match(rewards_txn_id=rewards_txn_id, rewards_membership_id=rewards_membership_id,
                   customer_id=customer_id, stay_id=stay_id, original_txn_id=original_txn_id)
    rows = ctx.find("rewards_transactions", **match)
    return str(rows) if rows else f"No Rewards credit records found for {match}."


# --------------------------------------------------------------------------- Trip Protection
@tool(owner="agent", rw="read")
def find_trip_protection_policies(ctx: ToolContext, trip_policy_id: str = "", customer_id: str = "",
                                  stay_id: str = "") -> str:
    """Look up trip protection policies guests bought for their stays.

    Each policy shows the plan, status, insured stay, purchase moment, insured trip cost, premium,
    the last day of coverage and any cancellation or voiding moment. Search by policy, guest or
    stay; every criterion is optional.

    Args:
        trip_policy_id: The trip protection policy reference number; leave "" if unknown.
        customer_id: The guest's customer reference number; leave "" if unknown.
        stay_id: The stay reference number; leave "" if unknown.
    """
    match = _match(trip_policy_id=trip_policy_id, customer_id=customer_id, stay_id=stay_id)
    rows = ctx.find("trip_protection_policies", **match)
    return str(rows) if rows else f"No trip protection policies found for {match}."


@tool(owner="agent", rw="read")
def find_trip_protection_transactions(ctx: ToolContext, trip_txn_id: str = "",
                                      trip_policy_id: str = "", customer_id: str = "",
                                      trip_claim_id: str = "", original_txn_id: str = "") -> str:
    """Look up trip protection money history: premiums, premium refunds, benefits paid, recoveries
    and claim denials.

    Each record shows its kind, date, amount and, as applicable, the claim, the benefit, the
    original payment a recovery reduces and the denial reason. Search by record, policy, guest,
    claim, or the original payment; every criterion is optional.

    Args:
        trip_txn_id: The reference number of one trip protection record; leave "" if unknown.
        trip_policy_id: The trip protection policy reference number; leave "" if unknown.
        customer_id: The guest's customer reference number; leave "" if unknown.
        trip_claim_id: The trip protection claim reference number; leave "" if unknown.
        original_txn_id: The reference number of the benefit payment a recovery reduces; leave "" if unknown.
    """
    match = _match(trip_txn_id=trip_txn_id, trip_policy_id=trip_policy_id, customer_id=customer_id,
                   trip_claim_id=trip_claim_id, original_txn_id=original_txn_id)
    rows = ctx.find("trip_protection_transactions", **match)
    return str(rows) if rows else f"No trip protection records found for {match}."


@tool(owner="agent", rw="read")
def find_trip_protection_claims(ctx: ToolContext, trip_claim_id: str = "", trip_policy_id: str = "",
                                customer_id: str = "") -> str:
    """Look up trip protection claims and the underwriter's decisions on them.

    Each claim shows the benefit claimed, the reason given, the amount claimed, the date of loss,
    when it was submitted, the claims team's decision, the amount approved and when it was decided.
    Search by claim, policy or guest; every criterion is optional.

    Args:
        trip_claim_id: The trip protection claim reference number; leave "" if unknown.
        trip_policy_id: The trip protection policy reference number; leave "" if unknown.
        customer_id: The guest's customer reference number; leave "" if unknown.
    """
    match = _match(trip_claim_id=trip_claim_id, trip_policy_id=trip_policy_id,
                   customer_id=customer_id)
    rows = ctx.find("trip_protection_claims", **match)
    return str(rows) if rows else f"No trip protection claims found for {match}."


# --------------------------------------------------------------------------- service logs
@tool(owner="agent", rw="read")
def find_identity_verifications(ctx: ToolContext, verification_id: str = "",
                                customer_id: str = "") -> str:
    """Look up the outcome of identity verification for a customer.

    Shows whether the customer's identity has been verified and when the latest attempt was made.
    Search by the verification reference number or by the customer reference number; every
    criterion is optional.

    Args:
        verification_id: The verification reference number; leave "" if unknown.
        customer_id: The customer reference number; leave "" if unknown.
    """
    match = _match(verification_id=verification_id, customer_id=customer_id)
    rows = ctx.find("identity_verifications", **match)
    return str(rows) if rows else f"No identity verification found for {match}."


@tool(owner="agent", rw="read")
def find_human_handoffs(ctx: ToolContext, handoff_id: str = "", customer_id: str = "") -> str:
    """Look up hand-overs of customers to human representatives.

    Shows each hand-over with its reason and when it was made. Search by the hand-over reference
    number or by the customer reference number; every criterion is optional.

    Args:
        handoff_id: The hand-over reference number; leave "" if unknown.
        customer_id: The customer reference number; leave "" if unknown.
    """
    match = _match(handoff_id=handoff_id, customer_id=customer_id)
    rows = ctx.find("human_handoffs", **match)
    return str(rows) if rows else f"No hand-overs found for {match}."


# --------------------------------------------------------------------------- verification
@tool(owner="agent", rw="write")
def verify_customer_identity(ctx: ToolContext, customer_id: str, phone_number: str = "",
                             email: str = "", date_of_birth: str = "",
                             government_id_last4: str = "", account_created_date: str = "") -> str:
    """Confirm that the caller is the customer whose profile you found, and record the outcome.

    Identity must be confirmed before you look into or act on anything in a customer's account —
    stays, listings, host account, payouts, damage protection, Rewards or trip protection. This tool
    does the comparison itself: it checks each piece of identity information the caller states
    against the profile and confirms the caller when at least 2 of them match. The customer
    reference number only tells the tool which profile to check and never counts as a match. Pass
    only what the caller actually said, exactly as they said it, and leave the rest blank. If a first
    attempt falls short, ask the caller for another detail on file and try again; once confirmed, the
    customer stays confirmed.

    Args:
        customer_id: The customer reference number from the profile lookup. Required; used only to
            find the profile, never counted as a match.
        phone_number: The registered mobile number the caller states, 10 digits without the country
            code; leave "" if not stated.
        email: The email address on the profile as the caller states it; leave "" if not stated.
        date_of_birth: The caller's date of birth, YYYY-MM-DD; leave "" if not stated.
        government_id_last4: The last four characters of the identity document the caller verified
            at sign-up; leave "" if not stated.
        account_created_date: The date the caller says they created their Roamhaven profile,
            YYYY-MM-DD; leave "" if not stated.
    """
    if not customer_id:
        return "Error: customer_id is required; find the customer profile first and pass its reference number."
    rows = ctx.find("customers", customer_id=customer_id)
    if not rows:
        return f"Error: no customer {customer_id}; cannot verify."
    rec = rows[0]
    # The tool owns the comparison; the locator customer_id is never part of `supplied`.
    supplied = {"phone_number": phone_number, "email": email, "date_of_birth": date_of_birth,
                "government_id_last4": government_id_last4,
                "account_created_date": account_created_date}
    matched = sum(1 for field, value in supplied.items()
                  if value and str(rec.get(field)).strip().lower() == str(value).strip().lower())
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
    if verified:
        return f"Identity confirmed for customer {customer_id}."
    return (f"Identity NOT confirmed for customer {customer_id}: only {matched} of the 2 required "
            "details matched. Ask the caller for another detail on file and try again.")


# --------------------------------------------------------------------------- hand-over
@tool(owner="agent", rw="write")
def transfer_to_human_agent(ctx: ToolContext, customer_id: str, reason: str) -> str:
    """Hand the customer over to a human Roamhaven representative and record why.

    Use it in exactly two situations. POLICY_NOT_COVERED: the customer's request is one that no
    Roamhaven policy lets you resolve. CUSTOMER_REQUESTED: the customer has explicitly asked to speak
    with a human representative 2 times. Once handed over, the representative takes the
    conversation from there.

    Args:
        customer_id: The customer reference number from the profile lookup.
        reason: Exactly one of POLICY_NOT_COVERED or CUSTOMER_REQUESTED, written in capitals as
            shown; no other wording is accepted.
    """
    allowed = {"POLICY_NOT_COVERED", "CUSTOMER_REQUESTED"}
    if reason not in allowed:
        return f"Error: unknown hand-over reason '{reason}'. Use one of: {', '.join(sorted(allowed))}."
    if not ctx.find("customers", customer_id=customer_id):
        return f"Error: no customer {customer_id}; cannot record the hand-over."
    rid = ctx.make_id("hof_", customer_id, reason)
    ctx.create("human_handoffs", rid, handoff_id=rid, customer_id=customer_id, reason=reason,
               created_at=ctx.now())
    return f"Hand-over to a human representative recorded for customer {customer_id} ({reason})."

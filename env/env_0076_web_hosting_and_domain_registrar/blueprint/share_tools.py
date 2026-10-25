"""Shared tools for env_0076_web_hosting_and_domain_registrar (Harborline Hosting & Domains).
Output of the erl-scenario-blueprint skill.

Every tool here is a SHARE tool: always present in its owner's tool list.
Contents: one record finder per table (the customers finder doubles as the identity entry),
the identity-verification write (K = 2 matching credentials) and the transfer-to-human handoff
(R = 2 explicit requests). Customer-originated writes live in each difficulty's task_tools.py.
"""

from erlbench import ToolContext, tool


def _pick(**kw):
    # keep only the criteria the caller actually supplied
    return {k: v for k, v in kw.items() if v}


# --------------------------------------------------------------------------- customers / identity

@tool(owner="agent", rw="read")
def find_customers(ctx: ToolContext, customer_id: str = "", name: str = "", email: str = "",
                   phone_number: str = "", company_name: str = "") -> str:
    """Look up a Harborline customer profile to establish whose account this conversation is about.

    Search by the customer reference number if you already have it, or by what the caller can
    naturally tell you: their name, the contact email on the profile, the contact phone number, or
    the registered business name. Every criterion is optional; supply whichever you have. Spacing,
    punctuation and letter case in what the caller says do not prevent a match. The profile returned
    shows the customer reference number, whether it is an individual or business profile, contact
    details, billing postal code and country, card ending, support PIN and the date the profile was
    opened. Finding a profile does not prove the caller is its owner; identity must still be
    verified before any account business.

    Args:
        customer_id: The customer reference number, if already known; leave "" otherwise.
        name: The account holder's full name as the caller states it; leave "" if not given.
        email: The contact email address the caller gives; leave "" if not given.
        phone_number: The contact phone number the caller gives, 10 digits; leave "" if not given.
        company_name: The registered business name for a business profile; leave "" if not given.
    """
    match = _pick(customer_id=customer_id, name=name, email=email, phone_number=phone_number,
                  company_name=company_name)
    if not match:
        return "Error: provide at least one reference number or profile detail to find the customer."
    rows = ctx.fuzzy_find("customers", **match)
    if not rows:
        return f"No customer matches {match}."
    if len(rows) > 1:
        return f"Error: {len(rows)} customers match {match}; ask the caller for one more detail to tell them apart."
    return str(rows[0])


@tool(owner="agent", rw="write")
def verify_customer_identity(ctx: ToolContext, customer_id: str, email: str = "", phone_number: str = "",
                             support_pin: str = "", card_last4: str = "", billing_zip: str = "",
                             account_opened_date: str = "") -> str:
    """Verify the caller's identity against the customer profile and record the outcome.

    Identity must be verified before any account information is discussed or any business is
    transacted on the account. This tool performs the comparison itself: each piece of identity
    information the caller states is compared with the profile, and verification passes when at
    least 2 of them match. The customer reference number only identifies which profile to check and
    never counts as a match. Callers usually know only some of these details, so pass exactly what
    the caller said for the details they gave and leave the rest blank. The outcome is recorded; if
    a first attempt fails and a later attempt with more details passes, the account stands verified.

    Args:
        customer_id: The customer reference number from the profile lookup. Required; used only to
            find the profile, never counted as a match.
        email: The contact email address on the profile, as the caller states it; "" if not stated.
        phone_number: The contact phone number on the profile, 10 digits without punctuation; "" if not stated.
        support_pin: The six-digit support PIN set in the account dashboard; "" if not stated.
        card_last4: The last four digits of the default payment card on file; "" if not stated.
        billing_zip: The billing postal code of the default payment method (5-digit US ZIP, or
            Canadian postal code in capitals without a space); "" if not stated.
        account_opened_date: The date the Harborline profile was opened, YYYY-MM-DD; "" if not stated.
    """
    if not customer_id:
        return "Error: customer_id is required; look the customer up first and pass their reference number."
    rows = ctx.find("customers", customer_id=customer_id)
    if not rows:
        return f"Error: no customer {customer_id}; cannot verify."
    rec = rows[0]
    supplied = {"email": email, "phone_number": phone_number, "support_pin": support_pin,
                "card_last4": card_last4, "billing_zip": billing_zip,
                "account_opened_date": account_opened_date}
    matched = sum(1 for field, value in supplied.items() if value and str(rec.get(field)) == str(value))
    verified = matched >= 2
    rid = ctx.make_id("ver_", customer_id)
    prior = ctx.find("identity_verifications", verification_id=rid)
    verified = verified or bool(prior and prior[0].get("verified"))
    if prior:
        ctx.update("identity_verifications", rid, verified=verified, verified_at=ctx.now())
    else:
        ctx.create("identity_verifications", rid, verification_id=rid, customer_id=customer_id,
                   verified=verified, verified_at=ctx.now())
    return (f"Identity verified for {customer_id} ({matched} detail(s) matched)." if verified
            else f"Identity NOT verified for {customer_id} (only {matched} of the required 2 details matched). "
                 "Ask the caller for another detail on file and try again.")


@tool(owner="agent", rw="write")
def transfer_to_human_agent(ctx: ToolContext, customer_id: str, reason: str) -> str:
    """Hand the customer over to a human Harborline support representative and record why.

    Use this in one of two situations only: when no Harborline policy offers a way to resolve what
    the customer needs, or when the customer has explicitly asked to speak with a human
    representative at least 2 times in this conversation.

    Args:
        customer_id: The customer reference number from the profile lookup (the profile must exist).
        reason: Exactly one of two values, never free text.
            POLICY_NOT_COVERED - no Harborline policy offers a way to resolve the request;
            CUSTOMER_REQUESTED - the customer has explicitly asked for a human representative at least 2 times.
    """
    allowed = {"POLICY_NOT_COVERED", "CUSTOMER_REQUESTED"}
    if reason not in allowed:
        return f"Error: unknown handoff reason '{reason}'. Valid: {', '.join(sorted(allowed))}."
    if not ctx.find("customers", customer_id=customer_id):
        return f"Error: no customer {customer_id}; cannot record handoff."
    rid = ctx.make_id("hof_", customer_id, reason)
    ctx.create("support_handoffs", rid, handoff_id=rid, customer_id=customer_id,
               reason=reason, created_at=ctx.now())
    return f"Handoff to a human representative recorded for {customer_id} ({reason})."


@tool(owner="agent", rw="read")
def find_identity_verifications(ctx: ToolContext, verification_id: str = "", customer_id: str = "") -> str:
    """Check whether a customer's identity has already been verified, and when.

    Returns the verification record showing whether verification passed and the moment of the latest
    attempt. Search by the customer reference number or by the verification reference number; both
    are optional.

    Args:
        verification_id: The reference number of the verification record; leave "" if unknown.
        customer_id: The customer reference number whose verification you want to see; leave "" if unknown.
    """
    match = _pick(verification_id=verification_id, customer_id=customer_id)
    rows = ctx.find("identity_verifications", **match)
    return str(rows) if rows else f"No verification records for {match}."


@tool(owner="agent", rw="read")
def find_support_handoffs(ctx: ToolContext, handoff_id: str = "", customer_id: str = "") -> str:
    """See earlier handoffs of a customer to a human representative.

    Each record shows the reason for the handoff and when it happened. Search by the customer
    reference number or by the handoff reference number; both are optional.

    Args:
        handoff_id: The reference number of the handoff record; leave "" if unknown.
        customer_id: The customer reference number; leave "" if unknown.
    """
    match = _pick(handoff_id=handoff_id, customer_id=customer_id)
    rows = ctx.find("support_handoffs", **match)
    return str(rows) if rows else f"No handoff records for {match}."


# --------------------------------------------------------------------------- domains

@tool(owner="agent", rw="read")
def find_domain_holdings(ctx: ToolContext, domain_id: str = "", customer_id: str = "",
                         bundled_hosting_id: str = "") -> str:
    """Look up the domain names a customer holds with Harborline.

    Each domain record shows the domain name and its TLD product, its current lifecycle state
    (pending, active, on hold, renewal grace, redemption, pending delete, deleted, transferred out or
    cancelled), how it was acquired, registration and expiry dates, auto-renew, WHOIS privacy,
    transfer lock and registry lock settings, nameservers, registrant name and organisation with
    their verification state, the dates of the last change of registrant, inbound transfer
    completion and entry into redemption, and the hosting plan whose free domain paid for it, if
    any. Search by the domain's reference number, by the customer reference number to list all of
    their domains, or by a hosting plan reference number to find the domain bundled with it.

    Args:
        domain_id: The reference number of the domain record; leave "" if unknown.
        customer_id: The customer reference number, to list every domain they hold; leave "" if unknown.
        bundled_hosting_id: A hosting plan reference number, to find the domain registered free with that plan; leave "" if unknown.
    """
    match = _pick(domain_id=domain_id, customer_id=customer_id, bundled_hosting_id=bundled_hosting_id)
    rows = ctx.find("domain_holdings", **match)
    return str(rows) if rows else f"No domain records for {match}."


@tool(owner="agent", rw="read")
def find_domain_charges(ctx: ToolContext, domain_charge_id: str = "", domain_id: str = "",
                        customer_id: str = "", original_domain_charge_id: str = "") -> str:
    """Review the billing history of domains: registrations, transfers, renewals, auto-renew charges,
    restores, registry lock fees and refunds.

    Each line shows what was billed, the amount (refunds appear as negative amounts), the years
    covered, the billing date, the order number, how it was paid and, for refunds, which charge was
    refunded and where the money went. Search by the line's own reference number, by domain, by
    customer, or by the reference of a refunded charge to see whether it has already been refunded.

    Args:
        domain_charge_id: The reference number of one billing line; leave "" if unknown.
        domain_id: The reference number of the domain, to list its billing; leave "" if unknown.
        customer_id: The customer reference number, to list all their domain billing; leave "" if unknown.
        original_domain_charge_id: The reference number of a charge, to find refunds made against it; leave "" if unknown.
    """
    match = _pick(domain_charge_id=domain_charge_id, domain_id=domain_id, customer_id=customer_id,
                  original_domain_charge_id=original_domain_charge_id)
    rows = ctx.find("domain_charges", **match)
    return str(rows) if rows else f"No domain billing lines for {match}."


@tool(owner="agent", rw="read")
def find_domain_events(ctx: ToolContext, domain_event_id: str = "", domain_id: str = "",
                       customer_id: str = "") -> str:
    """Read the service history of a domain: transfer authorisation codes issued, outbound transfer
    requests and their resolution, renewal reminders and post-expiry notices, declined auto-renew
    attempts and registrant verification confirmations.

    Each entry carries the moment it happened and the details that apply to it, such as the notice
    kind, the attempt number, the gaining registrar, the transfer decision or the last valid date of
    an authorisation code. Search by entry, by domain or by customer.

    Args:
        domain_event_id: The reference number of one service entry; leave "" if unknown.
        domain_id: The reference number of the domain; leave "" if unknown.
        customer_id: The customer reference number; leave "" if unknown.
    """
    match = _pick(domain_event_id=domain_event_id, domain_id=domain_id, customer_id=customer_id)
    rows = ctx.find("domain_events", **match)
    return str(rows) if rows else f"No domain service entries for {match}."


# --------------------------------------------------------------------------- customer accounts

@tool(owner="agent", rw="read")
def find_account_holdings(ctx: ToolContext, account_id: str = "", customer_id: str = "") -> str:
    """Open the customer's Harborline account record.

    It shows the account tier (Personal, Business or a Reseller level), the account state (unverified,
    active, recovery hold, locked or closed), the sign-in email and two-factor method, the current
    account credit balance, the sign-up date and the date the current tier took effect, the end of
    any recovery waiting period, the last security change date, any lock reason and the closure
    date. Search by the account reference number or the customer reference number.

    Args:
        account_id: The account reference number; leave "" if unknown.
        customer_id: The customer reference number; leave "" if unknown.
    """
    match = _pick(account_id=account_id, customer_id=customer_id)
    rows = ctx.find("account_holdings", **match)
    return str(rows) if rows else f"No account records for {match}."


@tool(owner="agent", rw="read")
def find_account_credit_ledger(ctx: ToolContext, credit_entry_id: str = "", account_id: str = "",
                               customer_id: str = "", original_credit_entry_id: str = "") -> str:
    """List movements of the customer's Harborline account credit.

    Entries cover deposits, refunds taken as credit, service credits, goodwill credits, credit spent
    on purchases, withdrawals back to a payment method and charge-back debits. Each shows the signed
    amount (additions positive, deductions negative), the date, what it represents, the external
    payment method involved, and the product category and charge or holding reference it relates
    to. Search by entry, account, customer, or by a deposit's reference to find withdrawals or
    charge-backs made against that deposit.

    Args:
        credit_entry_id: The reference number of one credit entry; leave "" if unknown.
        account_id: The account reference number; leave "" if unknown.
        customer_id: The customer reference number; leave "" if unknown.
        original_credit_entry_id: The reference number of a deposit, to find entries that reverse it; leave "" if unknown.
    """
    match = _pick(credit_entry_id=credit_entry_id, account_id=account_id, customer_id=customer_id,
                  original_credit_entry_id=original_credit_entry_id)
    rows = ctx.find("account_credit_ledger", **match)
    return str(rows) if rows else f"No account credit entries for {match}."


@tool(owner="agent", rw="read")
def find_account_events(ctx: ToolContext, account_event_id: str = "", account_id: str = "",
                        customer_id: str = "") -> str:
    """Read the account's security and review history: security notices sent, temporary sign-in
    lockouts and automatic tier review results.

    Each entry shows when it happened, the kind of notice, when a lockout ends, or the outcome of a
    tier review. Search by entry, account or customer.

    Args:
        account_event_id: The reference number of one entry; leave "" if unknown.
        account_id: The account reference number; leave "" if unknown.
        customer_id: The customer reference number; leave "" if unknown.
    """
    match = _pick(account_event_id=account_event_id, account_id=account_id, customer_id=customer_id)
    rows = ctx.find("account_events", **match)
    return str(rows) if rows else f"No account history entries for {match}."


@tool(owner="agent", rw="read")
def find_account_recovery_requests(ctx: ToolContext, recovery_request_id: str = "", customer_id: str = "",
                                   account_id: str = "") -> str:
    """Look up account recovery requests made for lost sign-in or two-factor access.

    Each request shows the evidence route used, what the recovery will reset, the new sign-in email
    requested where applicable, its current state (submitted, approved, rejected or withdrawn), when
    it was submitted and when Trust and Safety decided it. Search by request, customer or account.

    Args:
        recovery_request_id: The reference number of the recovery request; leave "" if unknown.
        customer_id: The customer reference number; leave "" if unknown.
        account_id: The account reference number; leave "" if unknown.
    """
    match = _pick(recovery_request_id=recovery_request_id, customer_id=customer_id, account_id=account_id)
    rows = ctx.find("account_recovery_requests", **match)
    return str(rows) if rows else f"No recovery requests for {match}."


# --------------------------------------------------------------------------- web hosting

@tool(owner="agent", rw="read")
def find_hosting_holdings(ctx: ToolContext, hosting_id: str = "", customer_id: str = "") -> str:
    """Look up a customer's web hosting plans.

    Each plan shows its tier, the primary domain it was set up for, its state (provisioning, active,
    suspended, cancellation scheduled, cancelled or terminated), the billing term and the dates of
    the current term, whether the current term is the introductory first term, auto-renew, the
    opening, activation, suspension and closing dates with any suspension cause, and the websites
    and storage currently in use. Search by plan reference number or customer reference number.

    Args:
        hosting_id: The hosting plan reference number; leave "" if unknown.
        customer_id: The customer reference number, to list all their plans; leave "" if unknown.
    """
    match = _pick(hosting_id=hosting_id, customer_id=customer_id)
    rows = ctx.find("hosting_holdings", **match)
    return str(rows) if rows else f"No hosting plans for {match}."


@tool(owner="agent", rw="read")
def find_hosting_charges(ctx: ToolContext, hosting_charge_id: str = "", hosting_id: str = "",
                         customer_id: str = "", original_hosting_charge_id: str = "") -> str:
    """Review hosting billing: first terms, setup fees, renewals, auto-renew charges, upgrade
    proration, backup restore and reactivation fees, refunds and uptime service credits.

    Each line shows the amount (refunds and credits negative), the months and period covered, the
    plan upgraded to where relevant, the billing date, order number and payment method, and for
    refunds the refunded charge, the rule applied and where the money went; uptime credits show the
    month credited. Search by line, plan, customer, or by a charge's reference to find refunds of it.

    Args:
        hosting_charge_id: The reference number of one billing line; leave "" if unknown.
        hosting_id: The hosting plan reference number; leave "" if unknown.
        customer_id: The customer reference number; leave "" if unknown.
        original_hosting_charge_id: The reference number of a charge, to find refunds made against it; leave "" if unknown.
    """
    match = _pick(hosting_charge_id=hosting_charge_id, hosting_id=hosting_id, customer_id=customer_id,
                  original_hosting_charge_id=original_hosting_charge_id)
    rows = ctx.find("hosting_charges", **match)
    return str(rows) if rows else f"No hosting billing lines for {match}."


@tool(owner="agent", rw="read")
def find_hosting_events(ctx: ToolContext, hosting_event_id: str = "", hosting_id: str = "",
                        customer_id: str = "") -> str:
    """Read a hosting plan's service history: declined auto-renew attempts, resource usage warnings
    and over-limit notices, monthly uptime reports and backup restores.

    Entries show when they happened and their details: attempt number, resource and measured usage,
    the month and measured uptime percentage, or the restore point used and who performed the
    restore. Search by entry, plan or customer.

    Args:
        hosting_event_id: The reference number of one entry; leave "" if unknown.
        hosting_id: The hosting plan reference number; leave "" if unknown.
        customer_id: The customer reference number; leave "" if unknown.
    """
    match = _pick(hosting_event_id=hosting_event_id, hosting_id=hosting_id, customer_id=customer_id)
    rows = ctx.find("hosting_events", **match)
    return str(rows) if rows else f"No hosting service entries for {match}."


@tool(owner="agent", rw="read")
def find_hosting_change_requests(ctx: ToolContext, hosting_request_id: str = "", customer_id: str = "",
                                 hosting_id: str = "") -> str:
    """Look up scheduled changes to a hosting plan's next renewal, such as a downgrade or a change of
    billing term.

    Each request shows what was asked for, the target plan and term, its state (scheduled, applied,
    withdrawn or declined), when it was recorded and the date it takes effect. Search by request,
    customer or plan.

    Args:
        hosting_request_id: The reference number of the change request; leave "" if unknown.
        customer_id: The customer reference number; leave "" if unknown.
        hosting_id: The hosting plan reference number; leave "" if unknown.
    """
    match = _pick(hosting_request_id=hosting_request_id, customer_id=customer_id, hosting_id=hosting_id)
    rows = ctx.find("hosting_change_requests", **match)
    return str(rows) if rows else f"No hosting change requests for {match}."


# --------------------------------------------------------------------------- SSL/TLS certificates

@tool(owner="agent", rw="read")
def find_ssl_holdings(ctx: ToolContext, certificate_id: str = "", customer_id: str = "",
                      domain_id: str = "", hosting_id: str = "") -> str:
    """Look up a customer's SSL/TLS certificate subscriptions.

    Each subscription shows the certificate product, the common name and number of extra names, its
    state (pending validation, active, expired, revoked or cancelled), the subscription years and
    start and end dates, the issue and expiry dates of the current certificate, the validation
    method with the dates domain control and organisation validation last completed, the Harborline
    domain and hosting plan linked to it, auto-renew, any revocation reason and the opening and
    closing dates. Search by certificate, customer, linked domain or linked hosting plan.

    Args:
        certificate_id: The certificate subscription reference number; leave "" if unknown.
        customer_id: The customer reference number; leave "" if unknown.
        domain_id: A Harborline domain reference number, to find certificates covering it; leave "" if unknown.
        hosting_id: A hosting plan reference number, to find certificates installed on it; leave "" if unknown.
    """
    match = _pick(certificate_id=certificate_id, customer_id=customer_id, domain_id=domain_id, hosting_id=hosting_id)
    rows = ctx.find("ssl_holdings", **match)
    return str(rows) if rows else f"No certificate subscriptions for {match}."


@tool(owner="agent", rw="read")
def find_ssl_charges(ctx: ToolContext, ssl_charge_id: str = "", certificate_id: str = "",
                     customer_id: str = "", original_ssl_charge_id: str = "") -> str:
    """Review certificate billing: new subscriptions, renewals, added names, installation fees and refunds.

    Each line shows the amount (refunds negative), years and names covered, the period, billing
    date, order number and payment method, and for refunds which charge was refunded and where the
    money went. Search by line, certificate, customer, or by a charge's reference to find refunds of it.

    Args:
        ssl_charge_id: The reference number of one billing line; leave "" if unknown.
        certificate_id: The certificate subscription reference number; leave "" if unknown.
        customer_id: The customer reference number; leave "" if unknown.
        original_ssl_charge_id: The reference number of a charge, to find refunds made against it; leave "" if unknown.
    """
    match = _pick(ssl_charge_id=ssl_charge_id, certificate_id=certificate_id, customer_id=customer_id,
                  original_ssl_charge_id=original_ssl_charge_id)
    rows = ctx.find("ssl_charges", **match)
    return str(rows) if rows else f"No certificate billing lines for {match}."


@tool(owner="agent", rw="read")
def find_ssl_events(ctx: ToolContext, ssl_event_id: str = "", certificate_id: str = "",
                    customer_id: str = "") -> str:
    """Read a certificate's service history: domain control validation checks and their results,
    every certificate issued (initial, reissue, automatic reissue or duplicate) with its expiry
    date, and expiry reminders sent.

    Search by entry, certificate subscription or customer.

    Args:
        ssl_event_id: The reference number of one entry; leave "" if unknown.
        certificate_id: The certificate subscription reference number; leave "" if unknown.
        customer_id: The customer reference number; leave "" if unknown.
    """
    match = _pick(ssl_event_id=ssl_event_id, certificate_id=certificate_id, customer_id=customer_id)
    rows = ctx.find("ssl_events", **match)
    return str(rows) if rows else f"No certificate service entries for {match}."


# --------------------------------------------------------------------------- professional email

@tool(owner="agent", rw="read")
def find_email_holdings(ctx: ToolContext, email_plan_id: str = "", customer_id: str = "",
                        domain_id: str = "") -> str:
    """Look up a customer's professional email subscriptions (Harborline Mail or Microsoft 365).

    Each subscription shows the product, the email domain, the licensed seats, the billing plan and
    the current term dates, renewal, any seat count or product scheduled for the next renewal, the
    linked Harborline domain, its state (provisioning, active, suspended, cancellation scheduled,
    expired or cancelled) and the opening, suspension, expiry and closing dates. Search by
    subscription, customer or linked domain.

    Args:
        email_plan_id: The email subscription reference number; leave "" if unknown.
        customer_id: The customer reference number; leave "" if unknown.
        domain_id: A Harborline domain reference number, to find the email subscription using it; leave "" if unknown.
    """
    match = _pick(email_plan_id=email_plan_id, customer_id=customer_id, domain_id=domain_id)
    rows = ctx.find("email_holdings", **match)
    return str(rows) if rows else f"No email subscriptions for {match}."


@tool(owner="agent", rw="read")
def find_email_charges(ctx: ToolContext, email_charge_id: str = "", email_plan_id: str = "",
                       customer_id: str = "", original_email_charge_id: str = "") -> str:
    """Review email billing: new subscriptions, renewals, monthly instalments, added seats, upgrade
    proration and refunds.

    Each line shows the amount (refunds negative), seats covered, the product upgraded to where
    relevant, the period, billing date, order number and payment method, and for refunds which
    charge was refunded and where the money went. Search by line, subscription, customer, or by a
    charge's reference to find refunds of it.

    Args:
        email_charge_id: The reference number of one billing line; leave "" if unknown.
        email_plan_id: The email subscription reference number; leave "" if unknown.
        customer_id: The customer reference number; leave "" if unknown.
        original_email_charge_id: The reference number of a charge, to find refunds made against it; leave "" if unknown.
    """
    match = _pick(email_charge_id=email_charge_id, email_plan_id=email_plan_id, customer_id=customer_id,
                  original_email_charge_id=original_email_charge_id)
    rows = ctx.find("email_charges", **match)
    return str(rows) if rows else f"No email billing lines for {match}."


@tool(owner="agent", rw="read")
def find_email_events(ctx: ToolContext, email_event_id: str = "", email_plan_id: str = "",
                      customer_id: str = "") -> str:
    """Read an email subscription's service history: declined charge attempts, mailbox deletions and
    mailbox restores.

    Entries show when they happened, the attempt number or the mailbox address concerned, and for a
    restore the moment the mailbox had been deleted. Search by entry, subscription or customer.

    Args:
        email_event_id: The reference number of one entry; leave "" if unknown.
        email_plan_id: The email subscription reference number; leave "" if unknown.
        customer_id: The customer reference number; leave "" if unknown.
    """
    match = _pick(email_event_id=email_event_id, email_plan_id=email_plan_id, customer_id=customer_id)
    rows = ctx.find("email_events", **match)
    return str(rows) if rows else f"No email service entries for {match}."


# --------------------------------------------------------------------------- VPS and dedicated servers

@tool(owner="agent", rw="read")
def find_server_holdings(ctx: ToolContext, server_id: str = "", customer_id: str = "") -> str:
    """Look up a customer's VPS and dedicated servers.

    Each server shows its product, hostname, state (provisioning, active, suspended, cancellation
    scheduled, cancelled or terminated), billing term and term dates, auto-renew, its add-ons (extra
    IPv4 addresses, backups, managed support, control panel licence), and the opening, hand-over,
    suspension, scheduled-cancellation and closing dates with any suspension cause. Search by server
    or customer.

    Args:
        server_id: The server reference number; leave "" if unknown.
        customer_id: The customer reference number; leave "" if unknown.
    """
    match = _pick(server_id=server_id, customer_id=customer_id)
    rows = ctx.find("server_holdings", **match)
    return str(rows) if rows else f"No servers for {match}."


@tool(owner="agent", rw="read")
def find_server_charges(ctx: ToolContext, server_charge_id: str = "", server_id: str = "",
                        customer_id: str = "", original_server_charge_id: str = "") -> str:
    """Review server billing: first terms, setup fees, renewals, add-ons, resizes, reactivation fees,
    bandwidth overage, refunds and uptime credits.

    Each line shows the amount (refunds and credits negative), months and period or month covered,
    billing date, order number and payment method, and for refunds which charge was refunded, the
    rule applied and where the money went. Search by line, server, customer, or by a charge's
    reference to find refunds of it.

    Args:
        server_charge_id: The reference number of one billing line; leave "" if unknown.
        server_id: The server reference number; leave "" if unknown.
        customer_id: The customer reference number; leave "" if unknown.
        original_server_charge_id: The reference number of a charge, to find refunds made against it; leave "" if unknown.
    """
    match = _pick(server_charge_id=server_charge_id, server_id=server_id, customer_id=customer_id,
                  original_server_charge_id=original_server_charge_id)
    rows = ctx.find("server_charges", **match)
    return str(rows) if rows else f"No server billing lines for {match}."


@tool(owner="agent", rw="read")
def find_server_events(ctx: ToolContext, server_event_id: str = "", server_id: str = "",
                       customer_id: str = "") -> str:
    """Read a server's service history: monthly transfer and downtime reports, abuse reports and
    declined renewal attempts.

    Entries show when they happened, the month with the transfer used and downtime minutes, or the
    kind and status of an abuse report. Search by entry, server or customer.

    Args:
        server_event_id: The reference number of one entry; leave "" if unknown.
        server_id: The server reference number; leave "" if unknown.
        customer_id: The customer reference number; leave "" if unknown.
    """
    match = _pick(server_event_id=server_event_id, server_id=server_id, customer_id=customer_id)
    rows = ctx.find("server_events", **match)
    return str(rows) if rows else f"No server service entries for {match}."


# --------------------------------------------------------------------------- website security

@tool(owner="agent", rw="read")
def find_security_holdings(ctx: ToolContext, security_plan_id: str = "", customer_id: str = "",
                           hosting_id: str = "") -> str:
    """Look up a customer's SiteGuard website security plans.

    Each plan shows its tier, the protected site's domain, the Harborline hosting plan the site runs
    on if any, its state (pending setup, active, cancellation scheduled, expired or cancelled), the
    billing term and term dates, auto-renew, and the opening, activation, expiry and closing dates.
    Search by plan, customer or hosting plan.

    Args:
        security_plan_id: The security plan reference number; leave "" if unknown.
        customer_id: The customer reference number; leave "" if unknown.
        hosting_id: A hosting plan reference number, to find security plans protecting sites on it; leave "" if unknown.
    """
    match = _pick(security_plan_id=security_plan_id, customer_id=customer_id, hosting_id=hosting_id)
    rows = ctx.find("security_holdings", **match)
    return str(rows) if rows else f"No security plans for {match}."


@tool(owner="agent", rw="read")
def find_security_charges(ctx: ToolContext, security_charge_id: str = "", security_plan_id: str = "",
                          customer_id: str = "", original_security_charge_id: str = "") -> str:
    """Review website security billing: new plans, renewals, upgrade proration, extra cleanups and refunds.

    Each line shows the amount (refunds negative), the months and period covered, the plan upgraded
    to where relevant, billing date, order number and payment method, and for refunds which charge
    was refunded and where the money went. Search by line, plan, customer, or by a charge's
    reference to find refunds of it.

    Args:
        security_charge_id: The reference number of one billing line; leave "" if unknown.
        security_plan_id: The security plan reference number; leave "" if unknown.
        customer_id: The customer reference number; leave "" if unknown.
        original_security_charge_id: The reference number of a charge, to find refunds made against it; leave "" if unknown.
    """
    match = _pick(security_charge_id=security_charge_id, security_plan_id=security_plan_id,
                  customer_id=customer_id, original_security_charge_id=original_security_charge_id)
    rows = ctx.find("security_charges", **match)
    return str(rows) if rows else f"No security billing lines for {match}."


@tool(owner="agent", rw="read")
def find_security_events(ctx: ToolContext, security_event_id: str = "", security_plan_id: str = "",
                         customer_id: str = "") -> str:
    """Read a security plan's history: malware and blacklist scan results, expert cleanups with the
    basis each was performed on (included, guarantee or paid), and PCI scan results.

    Search by entry, plan or customer.

    Args:
        security_event_id: The reference number of one entry; leave "" if unknown.
        security_plan_id: The security plan reference number; leave "" if unknown.
        customer_id: The customer reference number; leave "" if unknown.
    """
    match = _pick(security_event_id=security_event_id, security_plan_id=security_plan_id, customer_id=customer_id)
    rows = ctx.find("security_events", **match)
    return str(rows) if rows else f"No security service entries for {match}."

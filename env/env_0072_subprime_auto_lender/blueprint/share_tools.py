"""Shared tools for env_0072_subprime_auto_lender (Harborline Acceptance Corporation).

Every tool here is a share tool, always present in its owner's tool list:
  - one finder per record kind (the customers finder doubles as the identity entry);
  - the identity-verification write (compares the caller's statements itself, passes at 3 matches);
  - the transfer-to-human write (exactly two reasons; customer request threshold of 2 asks).
Customer-originated writes (signatures, acceptances, cancellations only the borrower can make)
are hidden task tools in each difficulty's task_tools.py, never here.
"""

from erlbench import ToolContext, tool


@tool(owner="agent", rw="read")
def find_customers(ctx: ToolContext, customer_id: str = "", phone_number: str = "", email: str = "", name: str = "") -> str:
    """Find the customer profile a call is about: a retail borrower or co-borrower, or a selling
    dealership. Search by the customer reference number, or by what the caller can tell you: the
    phone number on file, the email on file, or the full name (a person's legal name or the
    dealership's business name). Give whatever you have; spacing, punctuation and letter case in
    what the caller says do not matter.

    A match returns the full profile: customer type, name, phone, email, last four digits of the
    tax identification number, date of birth, ZIP code, mailing address and state, the date the
    profile was opened and any military service dates on file. Finding a profile only tells you
    whose account it is; it does not confirm that the caller is that person.

    Args:
        customer_id: The customer reference number, when you already have it; leave "" if unknown.
        phone_number: The phone number the caller gives, 10 digits; leave "" if not provided.
        email: The email address the caller gives; leave "" if not provided.
        name: The full name the caller gives (a person's legal name or a dealership's business name); leave "" if not provided.
    """
    match = {k: v for k, v in {"customer_id": customer_id, "phone_number": phone_number,
                               "email": email, "name": name}.items() if v}
    if not match:
        return "Error: provide at least one reference number or detail to find the customer."
    rows = ctx.fuzzy_find("customers", **match)
    if not rows:
        return f"No customer matches {match}."
    if len(rows) > 1:
        return f"Error: {len(rows)} customers match {match}; ask the caller for one more detail."
    return str(rows[0])


@tool(owner="agent", rw="read")
def find_verifications(ctx: ToolContext, verification_id: str = "", customer_id: str = "") -> str:
    """Look up the identity-verification outcome recorded for a caller, showing whether verification has passed and when it was last attempted.

    Every reference number below is optional; supply whichever you already hold and every
    matching record is returned in full. With no reference number at all, every record of this
    kind is returned. When nothing matches, a short note saying so is returned instead.

    Args:
        verification_id: The reference number of the verification record itself; leave "" if unknown.
        customer_id: The customer reference number of the borrower or dealership the record belongs to; leave "" if unknown.
    """
    match = {k: v for k, v in {"verification_id": verification_id, "customer_id": customer_id}.items() if v}
    rows = ctx.find("verifications", **match)
    return str(rows) if rows else f"No verifications records for {match}."


@tool(owner="agent", rw="read")
def find_handoffs(ctx: ToolContext, handoff_id: str = "", customer_id: str = "") -> str:
    """Look up the transfers to a human representative recorded for a customer, with the reason given and the moment of each transfer.

    Every reference number below is optional; supply whichever you already hold and every
    matching record is returned in full. With no reference number at all, every record of this
    kind is returned. When nothing matches, a short note saying so is returned instead.

    Args:
        handoff_id: The reference number of the transfer record itself; leave "" if unknown.
        customer_id: The customer reference number of the borrower or dealership the record belongs to; leave "" if unknown.
    """
    match = {k: v for k, v in {"handoff_id": handoff_id, "customer_id": customer_id}.items() if v}
    rows = ctx.find("handoffs", **match)
    return str(rows) if rows else f"No handoffs records for {match}."


@tool(owner="agent", rw="read")
def find_contracts(ctx: ToolContext, contract_id: str = "", customer_id: str = "", dealer_agreement_id: str = "") -> str:
    """Look up retail installment contracts: the credit tier, status, signing and payment dates, APR, scheduled payment and due day, next due date, principal and fees owed, the financed vehicle, the contract and title states, and repossession or closing details.

    Every reference number below is optional; supply whichever you already hold and every
    matching record is returned in full. With no reference number at all, every record of this
    kind is returned. When nothing matches, a short note saying so is returned instead.

    Args:
        contract_id: The reference number of the retail installment contract; leave "" if unknown.
        customer_id: The customer reference number of the borrower or dealership the record belongs to; leave "" if unknown.
        dealer_agreement_id: The reference number of the dealer retail agreement; leave "" if unknown.
    """
    match = {k: v for k, v in {"contract_id": contract_id, "customer_id": customer_id, "dealer_agreement_id": dealer_agreement_id}.items() if v}
    rows = ctx.find("contracts", **match)
    return str(rows) if rows else f"No contracts records for {match}."


@tool(owner="agent", rw="read")
def find_contract_transactions(ctx: ToolContext, contract_txn_id: str = "", contract_id: str = "", customer_id: str = "", related_txn_id: str = "", source_record_id: str = "") -> str:
    """Look up the money history of a retail installment contract: payments with their interest, principal and fee split, returned payments, fees charged, fee waivers and settlements, force-placed insurance charges, refund and benefit credits, and balance transfers to a deficiency account.

    Every reference number below is optional; supply whichever you already hold and every
    matching record is returned in full. With no reference number at all, every record of this
    kind is returned. When nothing matches, a short note saying so is returned instead.

    Args:
        contract_txn_id: The reference number of the contract money entry itself; leave "" if unknown.
        contract_id: The reference number of the retail installment contract; leave "" if unknown.
        customer_id: The customer reference number of the borrower or dealership the record belongs to; leave "" if unknown.
        related_txn_id: The reference number of the entry this one acts on (for example the payment a return reverses, or the fee a waiver removes); leave "" if unknown.
        source_record_id: The reference number of the originating record in another product (insurance, GAP or service-contract activity, an SCRA servicing record) or of the receiving deficiency account; leave "" if unknown.
    """
    match = {k: v for k, v in {"contract_txn_id": contract_txn_id, "contract_id": contract_id, "customer_id": customer_id, "related_txn_id": related_txn_id, "source_record_id": source_record_id}.items() if v}
    rows = ctx.find("contract_transactions", **match)
    return str(rows) if rows else f"No contract_transactions records for {match}."


@tool(owner="agent", rw="read")
def find_contract_servicing_events(ctx: ToolContext, servicing_event_id: str = "", contract_id: str = "", customer_id: str = "", service_request_id: str = "") -> str:
    """Look up servicing actions taken on a retail installment contract: due-date changes, payment extensions, Servicemembers Civil Relief Act rate changes, payoff quotes and lien releases, with their effective dates and resulting dates and amounts.

    Every reference number below is optional; supply whichever you already hold and every
    matching record is returned in full. With no reference number at all, every record of this
    kind is returned. When nothing matches, a short note saying so is returned instead.

    Args:
        servicing_event_id: The reference number of the servicing action itself; leave "" if unknown.
        contract_id: The reference number of the retail installment contract; leave "" if unknown.
        customer_id: The customer reference number of the borrower or dealership the record belongs to; leave "" if unknown.
        service_request_id: The reference number of the signed servicing request; leave "" if unknown.
    """
    match = {k: v for k, v in {"servicing_event_id": servicing_event_id, "contract_id": contract_id, "customer_id": customer_id, "service_request_id": service_request_id}.items() if v}
    rows = ctx.find("contract_servicing_events", **match)
    return str(rows) if rows else f"No contract_servicing_events records for {match}."


@tool(owner="agent", rw="read")
def find_contract_service_requests(ctx: ToolContext, service_request_id: str = "", customer_id: str = "", contract_id: str = "") -> str:
    """Look up a borrower's servicing requests that need a signature, such as extension agreements and SCRA rate-cap requests, with their status and when they were created and signed.

    Every reference number below is optional; supply whichever you already hold and every
    matching record is returned in full. With no reference number at all, every record of this
    kind is returned. When nothing matches, a short note saying so is returned instead.

    Args:
        service_request_id: The reference number of the signed servicing request; leave "" if unknown.
        customer_id: The customer reference number of the borrower or dealership the record belongs to; leave "" if unknown.
        contract_id: The reference number of the retail installment contract; leave "" if unknown.
    """
    match = {k: v for k, v in {"service_request_id": service_request_id, "customer_id": customer_id, "contract_id": contract_id}.items() if v}
    rows = ctx.find("contract_service_requests", **match)
    return str(rows) if rows else f"No contract_service_requests records for {match}."


@tool(owner="agent", rw="read")
def find_cpi_coverages(ctx: ToolContext, cpi_coverage_id: str = "", customer_id: str = "", contract_id: str = "") -> str:
    """Look up insurance tracking records for financed vehicles: the collateral protection plan, tracking status, the borrower's insurance on file, any lapse or force-placed coverage dates, and the net premium charged.

    Every reference number below is optional; supply whichever you already hold and every
    matching record is returned in full. With no reference number at all, every record of this
    kind is returned. When nothing matches, a short note saying so is returned instead.

    Args:
        cpi_coverage_id: The reference number of the insurance tracking record; leave "" if unknown.
        customer_id: The customer reference number of the borrower or dealership the record belongs to; leave "" if unknown.
        contract_id: The reference number of the retail installment contract; leave "" if unknown.
    """
    match = {k: v for k, v in {"cpi_coverage_id": cpi_coverage_id, "customer_id": customer_id, "contract_id": contract_id}.items() if v}
    rows = ctx.find("cpi_coverages", **match)
    return str(rows) if rows else f"No cpi_coverages records for {match}."


@tool(owner="agent", rw="read")
def find_cpi_activities(ctx: ToolContext, cpi_activity_id: str = "", cpi_coverage_id: str = "", contract_id: str = "", customer_id: str = "", related_activity_id: str = "") -> str:
    """Look up insurance tracking activity: proofs of insurance reviewed and their outcome, lapse and placement notices mailed, monthly force-placed premiums billed and premium refunds.

    Every reference number below is optional; supply whichever you already hold and every
    matching record is returned in full. With no reference number at all, every record of this
    kind is returned. When nothing matches, a short note saying so is returned instead.

    Args:
        cpi_activity_id: The reference number of the tracking activity itself; leave "" if unknown.
        cpi_coverage_id: The reference number of the insurance tracking record; leave "" if unknown.
        contract_id: The reference number of the retail installment contract; leave "" if unknown.
        customer_id: The customer reference number of the borrower or dealership the record belongs to; leave "" if unknown.
        related_activity_id: The reference number of the activity this one refers to (for example the premium a refund returns, the claim a decision settles or the expense a removal reverses); leave "" if unknown.
    """
    match = {k: v for k, v in {"cpi_activity_id": cpi_activity_id, "cpi_coverage_id": cpi_coverage_id, "contract_id": contract_id, "customer_id": customer_id, "related_activity_id": related_activity_id}.items() if v}
    rows = ctx.find("cpi_activities", **match)
    return str(rows) if rows else f"No cpi_activities records for {match}."


@tool(owner="agent", rw="read")
def find_recovery_cases(ctx: ToolContext, recovery_case_id: str = "", customer_id: str = "", contract_id: str = "") -> str:
    """Look up repossession cases: the collateral class, case status, how and when the vehicle was recovered, storage, sale results, recall reasons and recovery expenses outstanding.

    Every reference number below is optional; supply whichever you already hold and every
    matching record is returned in full. With no reference number at all, every record of this
    kind is returned. When nothing matches, a short note saying so is returned instead.

    Args:
        recovery_case_id: The reference number of the repossession case; leave "" if unknown.
        customer_id: The customer reference number of the borrower or dealership the record belongs to; leave "" if unknown.
        contract_id: The reference number of the retail installment contract; leave "" if unknown.
    """
    match = {k: v for k, v in {"recovery_case_id": recovery_case_id, "customer_id": customer_id, "contract_id": contract_id}.items() if v}
    rows = ctx.find("recovery_cases", **match)
    return str(rows) if rows else f"No recovery_cases records for {match}."


@tool(owner="agent", rw="read")
def find_recovery_activities(ctx: ToolContext, recovery_activity_id: str = "", recovery_case_id: str = "", contract_id: str = "", customer_id: str = "", related_activity_id: str = "") -> str:
    """Look up repossession case activity: right-to-cure and intent-to-sell notices, personal property notices, recovery expenses posted, removed or settled, reinstatement quotes, surplus payments and personal property releases.

    Every reference number below is optional; supply whichever you already hold and every
    matching record is returned in full. With no reference number at all, every record of this
    kind is returned. When nothing matches, a short note saying so is returned instead.

    Args:
        recovery_activity_id: The reference number of the case activity itself; leave "" if unknown.
        recovery_case_id: The reference number of the repossession case; leave "" if unknown.
        contract_id: The reference number of the retail installment contract; leave "" if unknown.
        customer_id: The customer reference number of the borrower or dealership the record belongs to; leave "" if unknown.
        related_activity_id: The reference number of the activity this one refers to (for example the premium a refund returns, the claim a decision settles or the expense a removal reverses); leave "" if unknown.
    """
    match = {k: v for k, v in {"recovery_activity_id": recovery_activity_id, "recovery_case_id": recovery_case_id, "contract_id": contract_id, "customer_id": customer_id, "related_activity_id": related_activity_id}.items() if v}
    rows = ctx.find("recovery_activities", **match)
    return str(rows) if rows else f"No recovery_activities records for {match}."


@tool(owner="agent", rw="read")
def find_deficiency_accounts(ctx: ToolContext, deficiency_account_id: str = "", customer_id: str = "", contract_id: str = "", recovery_case_id: str = "", arrangement_offer_id: str = "") -> str:
    """Look up deficiency balance accounts opened after a repossessed vehicle was sold: the resolution band, status, original and current balance, any arrangement in force, and the latest payment, referral or closing dates.

    Every reference number below is optional; supply whichever you already hold and every
    matching record is returned in full. With no reference number at all, every record of this
    kind is returned. When nothing matches, a short note saying so is returned instead.

    Args:
        deficiency_account_id: The reference number of the deficiency account; leave "" if unknown.
        customer_id: The customer reference number of the borrower or dealership the record belongs to; leave "" if unknown.
        contract_id: The reference number of the retail installment contract; leave "" if unknown.
        recovery_case_id: The reference number of the repossession case; leave "" if unknown.
        arrangement_offer_id: The reference number of the payment-plan or settlement offer; leave "" if unknown.
    """
    match = {k: v for k, v in {"deficiency_account_id": deficiency_account_id, "customer_id": customer_id, "contract_id": contract_id, "recovery_case_id": recovery_case_id, "arrangement_offer_id": arrangement_offer_id}.items() if v}
    rows = ctx.find("deficiency_accounts", **match)
    return str(rows) if rows else f"No deficiency_accounts records for {match}."


@tool(owner="agent", rw="read")
def find_deficiency_transactions(ctx: ToolContext, deficiency_txn_id: str = "", deficiency_account_id: str = "", customer_id: str = "", arrangement_offer_id: str = "", related_txn_id: str = "", source_record_id: str = "") -> str:
    """Look up the money history of a deficiency account: payments, returned payments, refund credits and settlement forgiveness.

    Every reference number below is optional; supply whichever you already hold and every
    matching record is returned in full. With no reference number at all, every record of this
    kind is returned. When nothing matches, a short note saying so is returned instead.

    Args:
        deficiency_txn_id: The reference number of the deficiency money entry itself; leave "" if unknown.
        deficiency_account_id: The reference number of the deficiency account; leave "" if unknown.
        customer_id: The customer reference number of the borrower or dealership the record belongs to; leave "" if unknown.
        arrangement_offer_id: The reference number of the payment-plan or settlement offer; leave "" if unknown.
        related_txn_id: The reference number of the entry this one acts on (for example the payment a return reverses, or the fee a waiver removes); leave "" if unknown.
        source_record_id: The reference number of the originating record in another product (insurance, GAP or service-contract activity, an SCRA servicing record) or of the receiving deficiency account; leave "" if unknown.
    """
    match = {k: v for k, v in {"deficiency_txn_id": deficiency_txn_id, "deficiency_account_id": deficiency_account_id, "customer_id": customer_id, "arrangement_offer_id": arrangement_offer_id, "related_txn_id": related_txn_id, "source_record_id": source_record_id}.items() if v}
    rows = ctx.find("deficiency_transactions", **match)
    return str(rows) if rows else f"No deficiency_transactions records for {match}."


@tool(owner="agent", rw="read")
def find_deficiency_arrangement_offers(ctx: ToolContext, arrangement_offer_id: str = "", customer_id: str = "", deficiency_account_id: str = "") -> str:
    """Look up payment-plan and settlement offers made on a deficiency account, with their terms, status, acceptance and any break date.

    Every reference number below is optional; supply whichever you already hold and every
    matching record is returned in full. With no reference number at all, every record of this
    kind is returned. When nothing matches, a short note saying so is returned instead.

    Args:
        arrangement_offer_id: The reference number of the payment-plan or settlement offer; leave "" if unknown.
        customer_id: The customer reference number of the borrower or dealership the record belongs to; leave "" if unknown.
        deficiency_account_id: The reference number of the deficiency account; leave "" if unknown.
    """
    match = {k: v for k, v in {"arrangement_offer_id": arrangement_offer_id, "customer_id": customer_id, "deficiency_account_id": deficiency_account_id}.items() if v}
    rows = ctx.find("deficiency_arrangement_offers", **match)
    return str(rows) if rows else f"No deficiency_arrangement_offers records for {match}."


@tool(owner="agent", rw="read")
def find_gap_addenda(ctx: ToolContext, gap_addendum_id: str = "", customer_id: str = "", contract_id: str = "") -> str:
    """Look up GAP waiver addenda attached to retail installment contracts: the plan, status, price, coverage dates, net charge and any cancellation details.

    Every reference number below is optional; supply whichever you already hold and every
    matching record is returned in full. With no reference number at all, every record of this
    kind is returned. When nothing matches, a short note saying so is returned instead.

    Args:
        gap_addendum_id: The reference number of the GAP waiver addendum; leave "" if unknown.
        customer_id: The customer reference number of the borrower or dealership the record belongs to; leave "" if unknown.
        contract_id: The reference number of the retail installment contract; leave "" if unknown.
    """
    match = {k: v for k, v in {"gap_addendum_id": gap_addendum_id, "customer_id": customer_id, "contract_id": contract_id}.items() if v}
    rows = ctx.find("gap_addenda", **match)
    return str(rows) if rows else f"No gap_addenda records for {match}."


@tool(owner="agent", rw="read")
def find_gap_activities(ctx: ToolContext, gap_activity_id: str = "", gap_addendum_id: str = "", contract_id: str = "", customer_id: str = "", related_activity_id: str = "", gap_request_id: str = "") -> str:
    """Look up GAP waiver activity: total-loss and theft claims with the insurer's settlement, claim decisions and benefits, and refunds of unearned charge.

    Every reference number below is optional; supply whichever you already hold and every
    matching record is returned in full. With no reference number at all, every record of this
    kind is returned. When nothing matches, a short note saying so is returned instead.

    Args:
        gap_activity_id: The reference number of the GAP activity itself; leave "" if unknown.
        gap_addendum_id: The reference number of the GAP waiver addendum; leave "" if unknown.
        contract_id: The reference number of the retail installment contract; leave "" if unknown.
        customer_id: The customer reference number of the borrower or dealership the record belongs to; leave "" if unknown.
        related_activity_id: The reference number of the activity this one refers to (for example the premium a refund returns, the claim a decision settles or the expense a removal reverses); leave "" if unknown.
        gap_request_id: The reference number of the GAP cancellation request; leave "" if unknown.
    """
    match = {k: v for k, v in {"gap_activity_id": gap_activity_id, "gap_addendum_id": gap_addendum_id, "contract_id": contract_id, "customer_id": customer_id, "related_activity_id": related_activity_id, "gap_request_id": gap_request_id}.items() if v}
    rows = ctx.find("gap_activities", **match)
    return str(rows) if rows else f"No gap_activities records for {match}."


@tool(owner="agent", rw="read")
def find_gap_cancellation_requests(ctx: ToolContext, gap_request_id: str = "", customer_id: str = "", gap_addendum_id: str = "") -> str:
    """Look up a borrower's GAP waiver cancellation requests, with their status and when they were created and signed.

    Every reference number below is optional; supply whichever you already hold and every
    matching record is returned in full. With no reference number at all, every record of this
    kind is returned. When nothing matches, a short note saying so is returned instead.

    Args:
        gap_request_id: The reference number of the GAP cancellation request; leave "" if unknown.
        customer_id: The customer reference number of the borrower or dealership the record belongs to; leave "" if unknown.
        gap_addendum_id: The reference number of the GAP waiver addendum; leave "" if unknown.
    """
    match = {k: v for k, v in {"gap_request_id": gap_request_id, "customer_id": customer_id, "gap_addendum_id": gap_addendum_id}.items() if v}
    rows = ctx.find("gap_cancellation_requests", **match)
    return str(rows) if rows else f"No gap_cancellation_requests records for {match}."


@tool(owner="agent", rw="read")
def find_service_contracts(ctx: ToolContext, service_contract_id: str = "", customer_id: str = "", contract_id: str = "") -> str:
    """Look up vehicle service contracts: the coverage plan, status, price, expiration date and odometer, transfers and cancellation details.

    Every reference number below is optional; supply whichever you already hold and every
    matching record is returned in full. With no reference number at all, every record of this
    kind is returned. When nothing matches, a short note saying so is returned instead.

    Args:
        service_contract_id: The reference number of the vehicle service contract; leave "" if unknown.
        customer_id: The customer reference number of the borrower or dealership the record belongs to; leave "" if unknown.
        contract_id: The reference number of the retail installment contract; leave "" if unknown.
    """
    match = {k: v for k, v in {"service_contract_id": service_contract_id, "customer_id": customer_id, "contract_id": contract_id}.items() if v}
    rows = ctx.find("service_contracts", **match)
    return str(rows) if rows else f"No service_contracts records for {match}."


@tool(owner="agent", rw="read")
def find_vsc_activities(ctx: ToolContext, vsc_activity_id: str = "", service_contract_id: str = "", contract_id: str = "", customer_id: str = "", vsc_request_id: str = "") -> str:
    """Look up vehicle service contract activity: repair claims authorized or denied with their amounts and deductibles, and refunds after cancellation.

    Every reference number below is optional; supply whichever you already hold and every
    matching record is returned in full. With no reference number at all, every record of this
    kind is returned. When nothing matches, a short note saying so is returned instead.

    Args:
        vsc_activity_id: The reference number of the service-contract activity itself; leave "" if unknown.
        service_contract_id: The reference number of the vehicle service contract; leave "" if unknown.
        contract_id: The reference number of the retail installment contract; leave "" if unknown.
        customer_id: The customer reference number of the borrower or dealership the record belongs to; leave "" if unknown.
        vsc_request_id: The reference number of the service-contract cancellation request; leave "" if unknown.
    """
    match = {k: v for k, v in {"vsc_activity_id": vsc_activity_id, "service_contract_id": service_contract_id, "contract_id": contract_id, "customer_id": customer_id, "vsc_request_id": vsc_request_id}.items() if v}
    rows = ctx.find("vsc_activities", **match)
    return str(rows) if rows else f"No vsc_activities records for {match}."


@tool(owner="agent", rw="read")
def find_vsc_cancellation_requests(ctx: ToolContext, vsc_request_id: str = "", customer_id: str = "", service_contract_id: str = "") -> str:
    """Look up a borrower's vehicle service contract cancellation requests, with the certified odometer, status and when they were created and signed.

    Every reference number below is optional; supply whichever you already hold and every
    matching record is returned in full. With no reference number at all, every record of this
    kind is returned. When nothing matches, a short note saying so is returned instead.

    Args:
        vsc_request_id: The reference number of the service-contract cancellation request; leave "" if unknown.
        customer_id: The customer reference number of the borrower or dealership the record belongs to; leave "" if unknown.
        service_contract_id: The reference number of the vehicle service contract; leave "" if unknown.
    """
    match = {k: v for k, v in {"vsc_request_id": vsc_request_id, "customer_id": customer_id, "service_contract_id": service_contract_id}.items() if v}
    rows = ctx.find("vsc_cancellation_requests", **match)
    return str(rows) if rows else f"No vsc_cancellation_requests records for {match}."


@tool(owner="agent", rw="read")
def find_dealer_agreements(ctx: ToolContext, dealer_agreement_id: str = "", customer_id: str = "") -> str:
    """Look up dealer retail agreements held by selling dealerships: the dealer program tier, status and its reason, dealer number and license state, tier review date, holdbacks withheld and net participation.

    Every reference number below is optional; supply whichever you already hold and every
    matching record is returned in full. With no reference number at all, every record of this
    kind is returned. When nothing matches, a short note saying so is returned instead.

    Args:
        dealer_agreement_id: The reference number of the dealer retail agreement; leave "" if unknown.
        customer_id: The customer reference number of the borrower or dealership the record belongs to; leave "" if unknown.
    """
    match = {k: v for k, v in {"dealer_agreement_id": dealer_agreement_id, "customer_id": customer_id}.items() if v}
    rows = ctx.find("dealer_agreements", **match)
    return str(rows) if rows else f"No dealer_agreements records for {match}."


@tool(owner="agent", rw="read")
def find_dealer_transactions(ctx: ToolContext, dealer_txn_id: str = "", dealer_agreement_id: str = "", customer_id: str = "", contract_id: str = "") -> str:
    """Look up a dealer's funding history: contracts funded with acquisition fees and holdbacks, holdback releases and forfeitures, titles received, participation and volume bonuses paid, and participation chargebacks.

    Every reference number below is optional; supply whichever you already hold and every
    matching record is returned in full. With no reference number at all, every record of this
    kind is returned. When nothing matches, a short note saying so is returned instead.

    Args:
        dealer_txn_id: The reference number of the dealer money entry itself; leave "" if unknown.
        dealer_agreement_id: The reference number of the dealer retail agreement; leave "" if unknown.
        customer_id: The customer reference number of the borrower or dealership the record belongs to; leave "" if unknown.
        contract_id: The reference number of the retail installment contract; leave "" if unknown.
    """
    match = {k: v for k, v in {"dealer_txn_id": dealer_txn_id, "dealer_agreement_id": dealer_agreement_id, "customer_id": customer_id, "contract_id": contract_id}.items() if v}
    rows = ctx.find("dealer_transactions", **match)
    return str(rows) if rows else f"No dealer_transactions records for {match}."


@tool(owner="agent", rw="write")
def verify_customer_identity(ctx: ToolContext, customer_id: str, phone_number: str = "", email: str = "",
                             tax_id_last4: str = "", date_of_birth: str = "", zip_code: str = "") -> str:
    """Confirm that the caller is the customer on the profile, and record the result. Identity must
    be confirmed before any account detail is discussed or any payment, fee, term or document
    action is taken on the customer's behalf.

    This tool makes the comparison itself: it checks each detail the caller states against the
    profile, counts how many agree, and confirms identity only when at least 3 agree. The customer
    reference number only tells the tool which profile to compare against and never counts as an
    agreeing detail. Callers often know only some of the details, so pass exactly what the caller
    said, unchanged, and leave the rest empty. Every attempt is recorded; once a caller has been
    confirmed, a later attempt never takes that confirmation away, and a caller who first falls
    short can try again with more details.

    Args:
        customer_id: The customer reference number of the profile found for this caller. Required; it selects the profile and does not count as a detail.
        phone_number: The phone number the caller states, 10 digits; leave "" if not stated.
        email: The email address the caller states; leave "" if not stated.
        tax_id_last4: The last four digits of the caller's Social Security number (or, for a dealership, of its Employer Identification Number), as stated; leave "" if not stated.
        date_of_birth: The caller's date of birth as YYYY-MM-DD; leave "" if not stated.
        zip_code: The 5-digit ZIP code of the mailing address the caller states; leave "" if not stated.
    """
    if not customer_id:
        return "Error: customer_id is required; find the customer profile first and pass its reference number."
    rows = ctx.find("customers", customer_id=customer_id)
    if not rows:
        return f"Error: no customer {customer_id}; cannot verify."
    rec = rows[0]
    # The locator customer_id is deliberately not part of `supplied`.
    supplied = {"phone_number": phone_number, "email": email, "tax_id_last4": tax_id_last4,
                "date_of_birth": date_of_birth, "zip_code": zip_code}
    matched = sum(1 for field, value in supplied.items()
                  if value and str(rec.get(field) or "").strip().lower() == str(value).strip().lower())
    verified = matched >= 3
    rid = ctx.make_id("ver_", customer_id)
    # Store only the reproducible boolean; upsert and never downgrade a prior pass.
    prior = ctx.find("verifications", verification_id=rid)
    verified = verified or bool(prior and prior[0].get("verified"))
    if prior:
        ctx.update("verifications", rid, verified=verified, verified_at=ctx.now())
    else:
        ctx.create("verifications", rid, verification_id=rid, customer_id=customer_id,
                   verified=verified, verified_at=ctx.now())
    return (f"Identity verified for {customer_id} ({matched} detail(s) matched)." if verified
            else f"Identity NOT verified for {customer_id} (only {matched} of the required 3 details matched). "
                 "Ask the caller for another detail on file and try again.")


@tool(owner="agent", rw="write")
def transfer_to_human_agent(ctx: ToolContext, customer_id: str, reason: str) -> str:
    """Hand the customer to a human representative and record the transfer with its reason.

    Use it in exactly two situations. When no Harborline policy can resolve what the customer
    needs, record POLICY_NOT_COVERED. When the customer has explicitly asked to speak with a
    human representative 2 times, record CUSTOMER_REQUESTED.

    Args:
        customer_id: The customer reference number of the caller's profile (the profile must exist).
        reason: Why the customer is transferred; exactly one of POLICY_NOT_COVERED (no policy can resolve the request) or CUSTOMER_REQUESTED (the customer has asked for a human representative 2 times). Never free text.
    """
    allowed = {"POLICY_NOT_COVERED", "CUSTOMER_REQUESTED"}
    if reason not in allowed:
        return f"Error: unknown transfer reason '{reason}'. Valid: {', '.join(sorted(allowed))}."
    if not ctx.find("customers", customer_id=customer_id):
        return f"Error: no customer {customer_id}; cannot record the transfer."
    rid = ctx.make_id("hof_", customer_id, reason)
    ctx.create("handoffs", rid, handoff_id=rid, customer_id=customer_id,
               reason=reason, created_at=ctx.now())
    return f"Transfer to a human representative recorded for {customer_id} ({reason})."

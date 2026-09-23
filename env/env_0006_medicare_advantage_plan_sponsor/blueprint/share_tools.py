"""Shared tools for env_0006_medicare_advantage_plan_sponsor (Ridgecrest Health Plans, Inc.).

Every tool defined here is a SHARE tool: always present in its owner's tool list and directly
callable in every task. Three kinds of utility live here and nowhere else — the complete
record-lookup layer (one finder per kind of record, with the customers finder doubling as the
identity entry), the identity-verification write, and the transfer-to-human write.
Member-initiated business writes are authored per difficulty as hidden task tools, never here.
"""

from erlbench import ToolContext, tool


@tool(owner="agent", rw="read")
def find_advantage_enrollments(ctx: ToolContext, advantage_enrollment_id: str = "", customer_id: str = "") -> str:
    """Look up a member's Medicare Advantage enrollments. Each record carries the plan the member holds, where it stands in its lifecycle, the contract year and CMS plan identifier, the election period it was accepted under, the coverage start and end dates, how the premium is paid and how often it is billed, the premium still owed and the cost share accumulated toward the annual maximum out-of-pocket.

    Every criterion is optional: supply whichever reference numbers are already in hand and the
    matching records come back, or a plain note saying that none were found.

    Args:
        advantage_enrollment_id: Id class - the reference number of a Medicare Advantage enrollment; leave "" if it is not known.
        customer_id: Id class - the member reference number that identifies whose account this is; leave "" if it is not known.
    """
    match = {k: v for k, v in {"advantage_enrollment_id": advantage_enrollment_id,
                               "customer_id": customer_id}.items() if v}
    rows = ctx.find("advantage_enrollments", **match)
    return str(rows) if rows else f"No matching records found for {match}."


@tool(owner="agent", rw="read")
def find_advantage_premium_ledger(ctx: ToolContext, advantage_premium_entry_id: str = "", advantage_enrollment_id: str = "", customer_id: str = "", source_premium_entry_id: str = "") -> str:
    """Retrieve the entries on a member's Medicare Advantage premium account: the monthly charges raised, the money received against them and the credits granted. Every entry carries the coverage month it belongs to, the date it posted, its amount, how any money arrived and what the posting did to the balance.

    Every criterion is optional: supply whichever reference numbers are already in hand and the
    matching records come back, or a plain note saying that none were found.

    Args:
        advantage_premium_entry_id: Id class - the reference number of a single Medicare Advantage premium account entry; leave "" if it is not known.
        advantage_enrollment_id: Id class - the reference number of a Medicare Advantage enrollment; leave "" if it is not known.
        customer_id: Id class - the member reference number that identifies whose account this is; leave "" if it is not known.
        source_premium_entry_id: Id class - the reference number of the account charge a credit, refund or removal was posted against; leave "" if it is not known.
    """
    match = {k: v for k, v in {"advantage_premium_entry_id": advantage_premium_entry_id,
                               "advantage_enrollment_id": advantage_enrollment_id,
                               "customer_id": customer_id,
                               "source_premium_entry_id": source_premium_entry_id}.items() if v}
    rows = ctx.find("advantage_premium_ledger", **match)
    return str(rows) if rows else f"No matching records found for {match}."


@tool(owner="agent", rw="read")
def find_advantage_medical_claims(ctx: ToolContext, advantage_claim_id: str = "", advantage_enrollment_id: str = "", customer_id: str = "", authorization_reference: str = "", source_claim_id: str = "") -> str:
    """Search the medical claim lines processed on a member's Medicare Advantage coverage. A line shows the date of service, the benefit category and place of service, whether the provider was in network, what was billed and what the plan allowed, the member's own liability, how the line was settled and, where it was not paid, the reason recorded.

    Every criterion is optional: supply whichever reference numbers are already in hand and the
    matching records come back, or a plain note saying that none were found.

    Args:
        advantage_claim_id: Id class - the reference number of a single processed medical claim line; leave "" if it is not known.
        advantage_enrollment_id: Id class - the reference number of a Medicare Advantage enrollment; leave "" if it is not known.
        customer_id: Id class - the member reference number that identifies whose account this is; leave "" if it is not known.
        authorization_reference: Id class - the reference number of the coverage request that authorised the service; leave "" if it is not known.
        source_claim_id: Id class - the reference number of the originally processed claim line a reversal or adjustment was posted against; leave "" if it is not known.
    """
    match = {k: v for k, v in {"advantage_claim_id": advantage_claim_id,
                               "advantage_enrollment_id": advantage_enrollment_id,
                               "customer_id": customer_id,
                               "authorization_reference": authorization_reference,
                               "source_claim_id": source_claim_id}.items() if v}
    rows = ctx.find("advantage_medical_claims", **match)
    return str(rows) if rows else f"No matching records found for {match}."


@tool(owner="agent", rw="read")
def find_advantage_service_requests(ctx: ToolContext, advantage_service_request_id: str = "", advantage_enrollment_id: str = "", customer_id: str = "", source_service_request_id: str = "") -> str:
    """Look up the coverage requests, decisions and reconsiderations on a member's Medicare Advantage coverage. Each record shows what was asked for, whether it was standard or expedited, when it arrived, when it was decided, the disposition and the reason recorded with it, and whether a deadline extension was taken.

    Every criterion is optional: supply whichever reference numbers are already in hand and the
    matching records come back, or a plain note saying that none were found.

    Args:
        advantage_service_request_id: Id class - the reference number of a coverage request, decision or reconsideration; leave "" if it is not known.
        advantage_enrollment_id: Id class - the reference number of a Medicare Advantage enrollment; leave "" if it is not known.
        customer_id: Id class - the member reference number that identifies whose account this is; leave "" if it is not known.
        source_service_request_id: Id class - the reference number of the earlier request or determination a decision or reconsideration was filed against; leave "" if it is not known.
    """
    match = {k: v for k, v in {"advantage_service_request_id": advantage_service_request_id,
                               "advantage_enrollment_id": advantage_enrollment_id,
                               "customer_id": customer_id,
                               "source_service_request_id": source_service_request_id}.items() if v}
    rows = ctx.find("advantage_service_requests", **match)
    return str(rows) if rows else f"No matching records found for {match}."


@tool(owner="agent", rw="read")
def find_advantage_enrollment_requests(ctx: ToolContext, advantage_enrollment_request_id: str = "", customer_id: str = "", advantage_enrollment_id: str = "") -> str:
    """Retrieve the enrollment intakes a member has raised on their Medicare Advantage coverage: new applications, plan changes, disenrollments, reinstatement requests and changes of payment method. Each shows what was asked for, the election period relied on, the attestation given, the date asked for and how far the request has got.

    Every criterion is optional: supply whichever reference numbers are already in hand and the
    matching records come back, or a plain note saying that none were found.

    Args:
        advantage_enrollment_request_id: Id class - the reference number of a Medicare Advantage enrollment intake; leave "" if it is not known.
        customer_id: Id class - the member reference number that identifies whose account this is; leave "" if it is not known.
        advantage_enrollment_id: Id class - the reference number of a Medicare Advantage enrollment; leave "" if it is not known.
    """
    match = {k: v for k, v in {"advantage_enrollment_request_id": advantage_enrollment_request_id,
                               "customer_id": customer_id,
                               "advantage_enrollment_id": advantage_enrollment_id}.items() if v}
    rows = ctx.find("advantage_enrollment_requests", **match)
    return str(rows) if rows else f"No matching records found for {match}."


@tool(owner="agent", rw="read")
def find_pdp_enrollments(ctx: ToolContext, pdp_enrollment_id: str = "", customer_id: str = "") -> str:
    """Look up a member's stand-alone Part D prescription drug plan enrollments. Each record carries the plan held, where it stands, the coverage dates, the payment stage the member is in, what they have paid out of pocket this year, any premium or late enrollment penalty still owed, the months CMS has counted without creditable coverage and the low-income subsidy in force.

    Every criterion is optional: supply whichever reference numbers are already in hand and the
    matching records come back, or a plain note saying that none were found.

    Args:
        pdp_enrollment_id: Id class - the reference number of a stand-alone Part D drug plan enrollment; leave "" if it is not known.
        customer_id: Id class - the member reference number that identifies whose account this is; leave "" if it is not known.
    """
    match = {k: v for k, v in {"pdp_enrollment_id": pdp_enrollment_id,
                               "customer_id": customer_id}.items() if v}
    rows = ctx.find("pdp_enrollments", **match)
    return str(rows) if rows else f"No matching records found for {match}."


@tool(owner="agent", rw="read")
def find_pdp_premium_ledger(ctx: ToolContext, pdp_premium_entry_id: str = "", pdp_enrollment_id: str = "", customer_id: str = "", source_premium_entry_id: str = "") -> str:
    """Retrieve the entries on a member's drug plan account: the basic and supplemental premium charges, the late enrollment penalty charged for each month, the money received and the credits and penalty removals granted. Each entry names the coverage month and the part of the bill it belongs to.

    Every criterion is optional: supply whichever reference numbers are already in hand and the
    matching records come back, or a plain note saying that none were found.

    Args:
        pdp_premium_entry_id: Id class - the reference number of a single drug plan premium account entry; leave "" if it is not known.
        pdp_enrollment_id: Id class - the reference number of a stand-alone Part D drug plan enrollment; leave "" if it is not known.
        customer_id: Id class - the member reference number that identifies whose account this is; leave "" if it is not known.
        source_premium_entry_id: Id class - the reference number of the account charge a credit, refund or removal was posted against; leave "" if it is not known.
    """
    match = {k: v for k, v in {"pdp_premium_entry_id": pdp_premium_entry_id,
                               "pdp_enrollment_id": pdp_enrollment_id,
                               "customer_id": customer_id,
                               "source_premium_entry_id": source_premium_entry_id}.items() if v}
    rows = ctx.find("pdp_premium_ledger", **match)
    return str(rows) if rows else f"No matching records found for {match}."


@tool(owner="agent", rw="read")
def find_pdp_pharmacy_claims(ctx: ToolContext, pdp_pharmacy_claim_id: str = "", pdp_enrollment_id: str = "", customer_id: str = "", determination_reference: str = "", source_pharmacy_claim_id: str = "") -> str:
    """Search the pharmacy fills priced on a member's drug coverage. A fill shows the date dispensed, the prescription and which refill it was, the exact product, its formulary tier, the days supply, the dispensing pharmacy's network standing, the negotiated price, what the member paid at the counter, what the plan paid and the payment stage at the time.

    Every criterion is optional: supply whichever reference numbers are already in hand and the
    matching records come back, or a plain note saying that none were found.

    Args:
        pdp_pharmacy_claim_id: Id class - the reference number of a single priced pharmacy fill; leave "" if it is not known.
        pdp_enrollment_id: Id class - the reference number of a stand-alone Part D drug plan enrollment; leave "" if it is not known.
        customer_id: Id class - the member reference number that identifies whose account this is; leave "" if it is not known.
        determination_reference: Id class - the reference number of the drug coverage determination that allowed the fill; leave "" if it is not known.
        source_pharmacy_claim_id: Id class - the reference number of the priced fill a reversal was posted against; leave "" if it is not known.
    """
    match = {k: v for k, v in {"pdp_pharmacy_claim_id": pdp_pharmacy_claim_id,
                               "pdp_enrollment_id": pdp_enrollment_id,
                               "customer_id": customer_id,
                               "determination_reference": determination_reference,
                               "source_pharmacy_claim_id": source_pharmacy_claim_id}.items() if v}
    rows = ctx.find("pdp_pharmacy_claims", **match)
    return str(rows) if rows else f"No matching records found for {match}."


@tool(owner="agent", rw="read")
def find_pdp_coverage_determinations(ctx: ToolContext, pdp_determination_id: str = "", pdp_enrollment_id: str = "", customer_id: str = "", source_determination_id: str = "") -> str:
    """Look up the drug coverage requests, exceptions, decisions and redeterminations on a member's drug coverage. Each record shows the product in question, when the request arrived, whether the prescriber's supporting statement is in hand, when it was decided, the outcome, the reason and how long an approval holds good.

    Every criterion is optional: supply whichever reference numbers are already in hand and the
    matching records come back, or a plain note saying that none were found.

    Args:
        pdp_determination_id: Id class - the reference number of a drug coverage request, decision or redetermination; leave "" if it is not known.
        pdp_enrollment_id: Id class - the reference number of a stand-alone Part D drug plan enrollment; leave "" if it is not known.
        customer_id: Id class - the member reference number that identifies whose account this is; leave "" if it is not known.
        source_determination_id: Id class - the reference number of the earlier drug request or denial a decision or redetermination was filed against; leave "" if it is not known.
    """
    match = {k: v for k, v in {"pdp_determination_id": pdp_determination_id,
                               "pdp_enrollment_id": pdp_enrollment_id,
                               "customer_id": customer_id,
                               "source_determination_id": source_determination_id}.items() if v}
    rows = ctx.find("pdp_coverage_determinations", **match)
    return str(rows) if rows else f"No matching records found for {match}."


@tool(owner="agent", rw="read")
def find_pdp_enrollment_requests(ctx: ToolContext, pdp_enrollment_request_id: str = "", customer_id: str = "", pdp_enrollment_id: str = "") -> str:
    """Retrieve the enrollment intakes a member has raised on their drug coverage: applications, plan changes, disenrollments, payment method changes and attestations of earlier creditable coverage, together with what the plan holds as evidence of that coverage.

    Every criterion is optional: supply whichever reference numbers are already in hand and the
    matching records come back, or a plain note saying that none were found.

    Args:
        pdp_enrollment_request_id: Id class - the reference number of a drug plan enrollment intake; leave "" if it is not known.
        customer_id: Id class - the member reference number that identifies whose account this is; leave "" if it is not known.
        pdp_enrollment_id: Id class - the reference number of a stand-alone Part D drug plan enrollment; leave "" if it is not known.
    """
    match = {k: v for k, v in {"pdp_enrollment_request_id": pdp_enrollment_request_id,
                               "customer_id": customer_id,
                               "pdp_enrollment_id": pdp_enrollment_id}.items() if v}
    rows = ctx.find("pdp_enrollment_requests", **match)
    return str(rows) if rows else f"No matching records found for {match}."


@tool(owner="agent", rw="read")
def find_allowance_programs(ctx: ToolContext, allowance_program_id: str = "", customer_id: str = "", linked_plan_reference: str = "") -> str:
    """Look up a member's supplemental benefit allowance card programmes. Each record shows the programme held, where it stands, the health plan it hangs on, the benefit year, the spendable balance right now, the last four digits of the card, when the card was posted and activated, the date of the last purchase and, where the card is stopped, why.

    Every criterion is optional: supply whichever reference numbers are already in hand and the
    matching records come back, or a plain note saying that none were found.

    Args:
        allowance_program_id: Id class - the reference number of a supplemental benefit allowance programme; leave "" if it is not known.
        customer_id: Id class - the member reference number that identifies whose account this is; leave "" if it is not known.
        linked_plan_reference: Id class - the reference number of the health plan enrollment the record hangs on; leave "" if it is not known.
    """
    match = {k: v for k, v in {"allowance_program_id": allowance_program_id,
                               "customer_id": customer_id,
                               "linked_plan_reference": linked_plan_reference}.items() if v}
    rows = ctx.find("allowance_programs", **match)
    return str(rows) if rows else f"No matching records found for {match}."


@tool(owner="agent", rw="read")
def find_allowance_card_ledger(ctx: ToolContext, allowance_ledger_entry_id: str = "", allowance_program_id: str = "", customer_id: str = "", source_ledger_entry_id: str = "") -> str:
    """Retrieve the entries on a member's allowance card: the scheduled and bonus loads, the purchases, the refunds and dispute credits, the period-end expiries and any forfeiture. Each entry names the benefit period it belongs to, the business reason it was posted, the retailer and spending category where there was one, and how far the card transaction got.

    Every criterion is optional: supply whichever reference numbers are already in hand and the
    matching records come back, or a plain note saying that none were found.

    Args:
        allowance_ledger_entry_id: Id class - the reference number of a single entry on the allowance card; leave "" if it is not known.
        allowance_program_id: Id class - the reference number of a supplemental benefit allowance programme; leave "" if it is not known.
        customer_id: Id class - the member reference number that identifies whose account this is; leave "" if it is not known.
        source_ledger_entry_id: Id class - the reference number of the card entry a refund, credit or expiry was posted against; leave "" if it is not known.
    """
    match = {k: v for k, v in {"allowance_ledger_entry_id": allowance_ledger_entry_id,
                               "allowance_program_id": allowance_program_id,
                               "customer_id": customer_id,
                               "source_ledger_entry_id": source_ledger_entry_id}.items() if v}
    rows = ctx.find("allowance_card_ledger", **match)
    return str(rows) if rows else f"No matching records found for {match}."


@tool(owner="agent", rw="read")
def find_allowance_catalog_orders(ctx: ToolContext, allowance_order_id: str = "", allowance_program_id: str = "", customer_id: str = "", source_order_id: str = "") -> str:
    """Search the catalogue orders a member has placed against their allowance, and the cancellations recorded against them. An order shows the date placed, the value of the items and the delivery charge, how many items it contains, the delivery service chosen, how far it has got, the tracking reference and the delivery date quoted.

    Every criterion is optional: supply whichever reference numbers are already in hand and the
    matching records come back, or a plain note saying that none were found.

    Args:
        allowance_order_id: Id class - the reference number of a catalogue order; leave "" if it is not known.
        allowance_program_id: Id class - the reference number of a supplemental benefit allowance programme; leave "" if it is not known.
        customer_id: Id class - the member reference number that identifies whose account this is; leave "" if it is not known.
        source_order_id: Id class - the reference number of the catalogue order a cancellation applies to; leave "" if it is not known.
    """
    match = {k: v for k, v in {"allowance_order_id": allowance_order_id,
                               "allowance_program_id": allowance_program_id,
                               "customer_id": customer_id,
                               "source_order_id": source_order_id}.items() if v}
    rows = ctx.find("allowance_catalog_orders", **match)
    return str(rows) if rows else f"No matching records found for {match}."


@tool(owner="agent", rw="read")
def find_allowance_benefit_requests(ctx: ToolContext, allowance_benefit_request_id: str = "", customer_id: str = "", allowance_program_id: str = "", disputed_ledger_entry_id: str = "") -> str:
    """Retrieve the allowance service requests a member has raised: card replacements, stops and releases, purchase disputes, statement reissues, eligibility reviews and programme closures. Each shows the amount in question, the statement the member made in support of it and how far the request has got.

    Every criterion is optional: supply whichever reference numbers are already in hand and the
    matching records come back, or a plain note saying that none were found.

    Args:
        allowance_benefit_request_id: Id class - the reference number of an allowance service request; leave "" if it is not known.
        customer_id: Id class - the member reference number that identifies whose account this is; leave "" if it is not known.
        allowance_program_id: Id class - the reference number of a supplemental benefit allowance programme; leave "" if it is not known.
        disputed_ledger_entry_id: Id class - the reference number of the card entry the member is disputing; leave "" if it is not known.
    """
    match = {k: v for k, v in {"allowance_benefit_request_id": allowance_benefit_request_id,
                               "customer_id": customer_id,
                               "allowance_program_id": allowance_program_id,
                               "disputed_ledger_entry_id": disputed_ledger_entry_id}.items() if v}
    rows = ctx.find("allowance_benefit_requests", **match)
    return str(rows) if rows else f"No matching records found for {match}."


@tool(owner="agent", rw="read")
def find_medigap_policies(ctx: ToolContext, medigap_policy_id: str = "", customer_id: str = "") -> str:
    """Look up a member's Medicare Supplement policies. Each record carries the standardised plan held, where it stands, the policy number on the certificate, the application and effective dates, the age and rating class the premium was built on, the right the policy was issued under, the premium still owed, and the discounts being applied.

    Every criterion is optional: supply whichever reference numbers are already in hand and the
    matching records come back, or a plain note saying that none were found.

    Args:
        medigap_policy_id: Id class - the reference number of a Medicare Supplement policy record; leave "" if it is not known.
        customer_id: Id class - the member reference number that identifies whose account this is; leave "" if it is not known.
    """
    match = {k: v for k, v in {"medigap_policy_id": medigap_policy_id,
                               "customer_id": customer_id}.items() if v}
    rows = ctx.find("medigap_policies", **match)
    return str(rows) if rows else f"No matching records found for {match}."


@tool(owner="agent", rw="read")
def find_medigap_premium_ledger(ctx: ToolContext, medigap_premium_entry_id: str = "", medigap_policy_id: str = "", customer_id: str = "", source_premium_entry_id: str = "") -> str:
    """Retrieve the entries on a policyholder's Medicare Supplement premium account: the charges raised for each billing span, the money received and the refunds paid. Each entry names the first month of the span, how many months of cover it pays for, which part of the rate calculation it came from and, on a refund, why it was paid.

    Every criterion is optional: supply whichever reference numbers are already in hand and the
    matching records come back, or a plain note saying that none were found.

    Args:
        medigap_premium_entry_id: Id class - the reference number of a single supplement premium account entry; leave "" if it is not known.
        medigap_policy_id: Id class - the reference number of a Medicare Supplement policy record; leave "" if it is not known.
        customer_id: Id class - the member reference number that identifies whose account this is; leave "" if it is not known.
        source_premium_entry_id: Id class - the reference number of the account charge a credit, refund or removal was posted against; leave "" if it is not known.
    """
    match = {k: v for k, v in {"medigap_premium_entry_id": medigap_premium_entry_id,
                               "medigap_policy_id": medigap_policy_id,
                               "customer_id": customer_id,
                               "source_premium_entry_id": source_premium_entry_id}.items() if v}
    rows = ctx.find("medigap_premium_ledger", **match)
    return str(rows) if rows else f"No matching records found for {match}."


@tool(owner="agent", rw="read")
def find_medigap_claim_crossovers(ctx: ToolContext, medigap_claim_id: str = "", medigap_policy_id: str = "", customer_id: str = "", source_claim_id: str = "") -> str:
    """Search the claims that crossed over from Medicare to a member's supplement policy. A line shows Medicare's own claim number, the date of service, the supplement benefit it falls under, what Medicare approved and paid, what the supplement paid, what the policyholder still owes, whether the provider accepted Medicare assignment and how the claim reached the plan.

    Every criterion is optional: supply whichever reference numbers are already in hand and the
    matching records come back, or a plain note saying that none were found.

    Args:
        medigap_claim_id: Id class - the reference number of a single processed supplement crossover line; leave "" if it is not known.
        medigap_policy_id: Id class - the reference number of a Medicare Supplement policy record; leave "" if it is not known.
        customer_id: Id class - the member reference number that identifies whose account this is; leave "" if it is not known.
        source_claim_id: Id class - the reference number of the originally processed claim line a reversal or adjustment was posted against; leave "" if it is not known.
    """
    match = {k: v for k, v in {"medigap_claim_id": medigap_claim_id,
                               "medigap_policy_id": medigap_policy_id,
                               "customer_id": customer_id,
                               "source_claim_id": source_claim_id}.items() if v}
    rows = ctx.find("medigap_claim_crossovers", **match)
    return str(rows) if rows else f"No matching records found for {match}."


@tool(owner="agent", rw="read")
def find_medigap_underwriting_files(ctx: ToolContext, medigap_underwriting_file_id: str = "", customer_id: str = "", medigap_policy_id: str = "") -> str:
    """Retrieve the supplement applications and underwriting files held for an applicant: what was applied for, how far the health questionnaire got, the underwriter's recorded decision and its date, what the plan holds to show earlier coverage, and how far the request has got. Cancellations and free look returns are recorded here too.

    Every criterion is optional: supply whichever reference numbers are already in hand and the
    matching records come back, or a plain note saying that none were found.

    Args:
        medigap_underwriting_file_id: Id class - the reference number of a supplement application and underwriting file; leave "" if it is not known.
        customer_id: Id class - the member reference number that identifies whose account this is; leave "" if it is not known.
        medigap_policy_id: Id class - the reference number of a Medicare Supplement policy record; leave "" if it is not known.
    """
    match = {k: v for k, v in {"medigap_underwriting_file_id": medigap_underwriting_file_id,
                               "customer_id": customer_id,
                               "medigap_policy_id": medigap_policy_id}.items() if v}
    rows = ctx.find("medigap_underwriting_files", **match)
    return str(rows) if rows else f"No matching records found for {match}."


@tool(owner="agent", rw="read")
def find_osb_riders(ctx: ToolContext, osb_rider_id: str = "", customer_id: str = "", linked_plan_reference: str = "") -> str:
    """Look up the optional supplemental benefit riders a member holds. Each record carries the rider held, where it stands, the medical plan it attaches to, the benefit year, the date the premium began and the date benefits became payable, why any waiting period is the length it is, the rider premium still owed and how much of the annual maximum has been used.

    Every criterion is optional: supply whichever reference numbers are already in hand and the
    matching records come back, or a plain note saying that none were found.

    Args:
        osb_rider_id: Id class - the reference number of an optional supplemental benefit rider; leave "" if it is not known.
        customer_id: Id class - the member reference number that identifies whose account this is; leave "" if it is not known.
        linked_plan_reference: Id class - the reference number of the health plan enrollment the record hangs on; leave "" if it is not known.
    """
    match = {k: v for k, v in {"osb_rider_id": osb_rider_id,
                               "customer_id": customer_id,
                               "linked_plan_reference": linked_plan_reference}.items() if v}
    rows = ctx.find("osb_riders", **match)
    return str(rows) if rows else f"No matching records found for {match}."


@tool(owner="agent", rw="read")
def find_osb_rider_premium_ledger(ctx: ToolContext, osb_rider_premium_entry_id: str = "", osb_rider_id: str = "", customer_id: str = "", source_premium_entry_id: str = "") -> str:
    """Retrieve the entries on a member's rider premium account: the monthly charges, the money received against them and the credits granted where a rider ended part way through a month or was billed in error. Each entry names the coverage month and what the posting did to the balance.

    Every criterion is optional: supply whichever reference numbers are already in hand and the
    matching records come back, or a plain note saying that none were found.

    Args:
        osb_rider_premium_entry_id: Id class - the reference number of a single rider premium account entry; leave "" if it is not known.
        osb_rider_id: Id class - the reference number of an optional supplemental benefit rider; leave "" if it is not known.
        customer_id: Id class - the member reference number that identifies whose account this is; leave "" if it is not known.
        source_premium_entry_id: Id class - the reference number of the account charge a credit, refund or removal was posted against; leave "" if it is not known.
    """
    match = {k: v for k, v in {"osb_rider_premium_entry_id": osb_rider_premium_entry_id,
                               "osb_rider_id": osb_rider_id,
                               "customer_id": customer_id,
                               "source_premium_entry_id": source_premium_entry_id}.items() if v}
    rows = ctx.find("osb_rider_premium_ledger", **match)
    return str(rows) if rows else f"No matching records found for {match}."


@tool(owner="agent", rw="read")
def find_osb_benefit_claims(ctx: ToolContext, osb_benefit_claim_id: str = "", osb_rider_id: str = "", customer_id: str = "", predetermination_reference: str = "", source_claim_id: str = "") -> str:
    """Search the dental, vision and hearing claim lines processed under a member's rider. A line shows the date of service, the benefit category and exact procedure, which tooth, eye or ear it was on, whether the provider was in network, what was charged and what was allowed, what the rider paid, what the member owes and, where nothing was paid, the reason.

    Every criterion is optional: supply whichever reference numbers are already in hand and the
    matching records come back, or a plain note saying that none were found.

    Args:
        osb_benefit_claim_id: Id class - the reference number of a single processed dental, vision or hearing claim line; leave "" if it is not known.
        osb_rider_id: Id class - the reference number of an optional supplemental benefit rider; leave "" if it is not known.
        customer_id: Id class - the member reference number that identifies whose account this is; leave "" if it is not known.
        predetermination_reference: Id class - the reference number of the predetermination that cleared the treatment in advance; leave "" if it is not known.
        source_claim_id: Id class - the reference number of the originally processed claim line a reversal or adjustment was posted against; leave "" if it is not known.
    """
    match = {k: v for k, v in {"osb_benefit_claim_id": osb_benefit_claim_id,
                               "osb_rider_id": osb_rider_id,
                               "customer_id": customer_id,
                               "predetermination_reference": predetermination_reference,
                               "source_claim_id": source_claim_id}.items() if v}
    rows = ctx.find("osb_benefit_claims", **match)
    return str(rows) if rows else f"No matching records found for {match}."


@tool(owner="agent", rw="read")
def find_osb_rider_requests(ctx: ToolContext, osb_rider_request_id: str = "", customer_id: str = "", osb_rider_id: str = "") -> str:
    """Retrieve the rider service requests a member has raised: new riders, rider changes, cancellations, predeterminations of a treatment plan, benefit appeals and provider changes. A predetermination also shows the treatment plan value, the answer given and the date it was given.

    Every criterion is optional: supply whichever reference numbers are already in hand and the
    matching records come back, or a plain note saying that none were found.

    Args:
        osb_rider_request_id: Id class - the reference number of a rider service request; leave "" if it is not known.
        customer_id: Id class - the member reference number that identifies whose account this is; leave "" if it is not known.
        osb_rider_id: Id class - the reference number of an optional supplemental benefit rider; leave "" if it is not known.
    """
    match = {k: v for k, v in {"osb_rider_request_id": osb_rider_request_id,
                               "customer_id": customer_id,
                               "osb_rider_id": osb_rider_id}.items() if v}
    rows = ctx.find("osb_rider_requests", **match)
    return str(rows) if rows else f"No matching records found for {match}."


@tool(owner="agent", rw="read")
def find_snp_enrollments(ctx: ToolContext, snp_enrollment_id: str = "", customer_id: str = "") -> str:
    """Look up a member's Special Needs Plan enrollments. Each record carries the plan held, where it stands, the special need it rests on, when that need was last confirmed, the Medicaid category the state last reported, the end of any deemed continued eligibility period, how far the individualised care plan has got, and the premium and state cost share still outstanding.

    Every criterion is optional: supply whichever reference numbers are already in hand and the
    matching records come back, or a plain note saying that none were found.

    Args:
        snp_enrollment_id: Id class - the reference number of a Special Needs Plan enrollment; leave "" if it is not known.
        customer_id: Id class - the member reference number that identifies whose account this is; leave "" if it is not known.
    """
    match = {k: v for k, v in {"snp_enrollment_id": snp_enrollment_id,
                               "customer_id": customer_id}.items() if v}
    rows = ctx.find("snp_enrollments", **match)
    return str(rows) if rows else f"No matching records found for {match}."


@tool(owner="agent", rw="read")
def find_snp_premium_ledger(ctx: ToolContext, snp_premium_entry_id: str = "", snp_enrollment_id: str = "", customer_id: str = "", source_premium_entry_id: str = "") -> str:
    """Retrieve the entries on a Special Needs Plan account: the premium and cost-share charges raised against the member, the money they paid, the credits granted, the cost share billed to the state Medicaid agency and the state's remittances against it. Each entry names who it is owed by and what it is for.

    Every criterion is optional: supply whichever reference numbers are already in hand and the
    matching records come back, or a plain note saying that none were found.

    Args:
        snp_premium_entry_id: Id class - the reference number of a single Special Needs Plan account entry; leave "" if it is not known.
        snp_enrollment_id: Id class - the reference number of a Special Needs Plan enrollment; leave "" if it is not known.
        customer_id: Id class - the member reference number that identifies whose account this is; leave "" if it is not known.
        source_premium_entry_id: Id class - the reference number of the account charge a credit, refund or removal was posted against; leave "" if it is not known.
    """
    match = {k: v for k, v in {"snp_premium_entry_id": snp_premium_entry_id,
                               "snp_enrollment_id": snp_enrollment_id,
                               "customer_id": customer_id,
                               "source_premium_entry_id": source_premium_entry_id}.items() if v}
    rows = ctx.find("snp_premium_ledger", **match)
    return str(rows) if rows else f"No matching records found for {match}."


@tool(owner="agent", rw="read")
def find_snp_care_records(ctx: ToolContext, snp_care_record_id: str = "", snp_enrollment_id: str = "", customer_id: str = "", source_care_record_id: str = "") -> str:
    """Search the care management records on a member's Special Needs Plan enrollment: health risk assessments, care plan reviews, transition reviews after a hospital stay and interdisciplinary team meetings. Each shows the date, how the activity ended, the risk band set, the care manager and when the next review falls due.

    Every criterion is optional: supply whichever reference numbers are already in hand and the
    matching records come back, or a plain note saying that none were found.

    Args:
        snp_care_record_id: Id class - the reference number of a care management assessment or review; leave "" if it is not known.
        snp_enrollment_id: Id class - the reference number of a Special Needs Plan enrollment; leave "" if it is not known.
        customer_id: Id class - the member reference number that identifies whose account this is; leave "" if it is not known.
        source_care_record_id: Id class - the reference number of the assessment a review follows on from; leave "" if it is not known.
    """
    match = {k: v for k, v in {"snp_care_record_id": snp_care_record_id,
                               "snp_enrollment_id": snp_enrollment_id,
                               "customer_id": customer_id,
                               "source_care_record_id": source_care_record_id}.items() if v}
    rows = ctx.find("snp_care_records", **match)
    return str(rows) if rows else f"No matching records found for {match}."


@tool(owner="agent", rw="read")
def find_snp_enrollment_requests(ctx: ToolContext, snp_enrollment_request_id: str = "", customer_id: str = "", snp_enrollment_id: str = "") -> str:
    """Retrieve the Special Needs Plan enrollment intakes a member has raised: applications, plan changes, disenrollments, eligibility reviews and care plan opt-outs, together with what the plan holds as evidence of the qualifying special need and how far the request has got.

    Every criterion is optional: supply whichever reference numbers are already in hand and the
    matching records come back, or a plain note saying that none were found.

    Args:
        snp_enrollment_request_id: Id class - the reference number of a Special Needs Plan enrollment intake; leave "" if it is not known.
        customer_id: Id class - the member reference number that identifies whose account this is; leave "" if it is not known.
        snp_enrollment_id: Id class - the reference number of a Special Needs Plan enrollment; leave "" if it is not known.
    """
    match = {k: v for k, v in {"snp_enrollment_request_id": snp_enrollment_request_id,
                               "customer_id": customer_id,
                               "snp_enrollment_id": snp_enrollment_id}.items() if v}
    rows = ctx.find("snp_enrollment_requests", **match)
    return str(rows) if rows else f"No matching records found for {match}."


@tool(owner="agent", rw="read")
def find_egwp_enrollments(ctx: ToolContext, egwp_enrollment_id: str = "", customer_id: str = "") -> str:
    """Look up a retiree's employer or union group plan enrollments. Each record carries the group plan held, where it stands, the group number and the sponsor that bought it, the sponsor's own reference for the retiree, who they are on the roster, when the sponsor's file named them, the coverage dates, who pays the premium, the retiree's own monthly share and how it is collected.

    Every criterion is optional: supply whichever reference numbers are already in hand and the
    matching records come back, or a plain note saying that none were found.

    Args:
        egwp_enrollment_id: Id class - the reference number of a group retiree enrollment; leave "" if it is not known.
        customer_id: Id class - the member reference number that identifies whose account this is; leave "" if it is not known.
    """
    match = {k: v for k, v in {"egwp_enrollment_id": egwp_enrollment_id,
                               "customer_id": customer_id}.items() if v}
    rows = ctx.find("egwp_enrollments", **match)
    return str(rows) if rows else f"No matching records found for {match}."


@tool(owner="agent", rw="read")
def find_egwp_premium_ledger(ctx: ToolContext, egwp_premium_entry_id: str = "", egwp_enrollment_id: str = "", customer_id: str = "", source_premium_entry_id: str = "") -> str:
    """Retrieve the entries on a group retiree's premium account, kept separately for the sponsor's share and the retiree's own contribution: the monthly charges, the money received whether by pension deduction, direct payment or a sponsor's bulk remittance, and the credits granted.

    Every criterion is optional: supply whichever reference numbers are already in hand and the
    matching records come back, or a plain note saying that none were found.

    Args:
        egwp_premium_entry_id: Id class - the reference number of a single group retiree account entry; leave "" if it is not known.
        egwp_enrollment_id: Id class - the reference number of a group retiree enrollment; leave "" if it is not known.
        customer_id: Id class - the member reference number that identifies whose account this is; leave "" if it is not known.
        source_premium_entry_id: Id class - the reference number of the account charge a credit, refund or removal was posted against; leave "" if it is not known.
    """
    match = {k: v for k, v in {"egwp_premium_entry_id": egwp_premium_entry_id,
                               "egwp_enrollment_id": egwp_enrollment_id,
                               "customer_id": customer_id,
                               "source_premium_entry_id": source_premium_entry_id}.items() if v}
    rows = ctx.find("egwp_premium_ledger", **match)
    return str(rows) if rows else f"No matching records found for {match}."


@tool(owner="agent", rw="read")
def find_egwp_group_change_log(ctx: ToolContext, egwp_group_change_id: str = "", egwp_enrollment_id: str = "", customer_id: str = "", source_change_id: str = "") -> str:
    """Search the changes recorded against a group retiree enrollment and the plan's own reconciliation findings. Each record shows what changed, who instructed it, the date it applies from, what the record said before and says now, which sponsor file cycle carried it and how it stands against the plan's reconciliation of the roster.

    Every criterion is optional: supply whichever reference numbers are already in hand and the
    matching records come back, or a plain note saying that none were found.

    Args:
        egwp_group_change_id: Id class - the reference number of a recorded group change or reconciliation finding; leave "" if it is not known.
        egwp_enrollment_id: Id class - the reference number of a group retiree enrollment; leave "" if it is not known.
        customer_id: Id class - the member reference number that identifies whose account this is; leave "" if it is not known.
        source_change_id: Id class - the reference number of the change record a reconciliation finding puts right; leave "" if it is not known.
    """
    match = {k: v for k, v in {"egwp_group_change_id": egwp_group_change_id,
                               "egwp_enrollment_id": egwp_enrollment_id,
                               "customer_id": customer_id,
                               "source_change_id": source_change_id}.items() if v}
    rows = ctx.find("egwp_group_change_log", **match)
    return str(rows) if rows else f"No matching records found for {match}."


@tool(owner="agent", rw="read")
def find_identity_verification_log(ctx: ToolContext, verification_id: str = "", customer_id: str = "") -> str:
    """Retrieve the record of identity checks already carried out on a member profile, showing whether the caller's identity was confirmed and when that outcome was last recorded.

    Every criterion is optional: supply whichever reference numbers are already in hand and the
    matching records come back, or a plain note saying that none were found.

    Args:
        verification_id: Id class - the reference number of an identity check already carried out; leave "" if it is not known.
        customer_id: Id class - the member reference number that identifies whose account this is; leave "" if it is not known.
    """
    match = {k: v for k, v in {"verification_id": verification_id,
                               "customer_id": customer_id}.items() if v}
    rows = ctx.find("identity_verification_log", **match)
    return str(rows) if rows else f"No matching records found for {match}."


@tool(owner="agent", rw="read")
def find_human_handoff_log(ctx: ToolContext, handoff_id: str = "", customer_id: str = "") -> str:
    """Retrieve the handovers to a human representative already recorded for a member, showing the reason each was made and when.

    Every criterion is optional: supply whichever reference numbers are already in hand and the
    matching records come back, or a plain note saying that none were found.

    Args:
        handoff_id: Id class - the reference number of a handover already recorded; leave "" if it is not known.
        customer_id: Id class - the member reference number that identifies whose account this is; leave "" if it is not known.
    """
    match = {k: v for k, v in {"handoff_id": handoff_id,
                               "customer_id": customer_id}.items() if v}
    rows = ctx.find("human_handoff_log", **match)
    return str(rows) if rows else f"No matching records found for {match}."


@tool(owner="agent", rw="read")
def find_customers(ctx: ToolContext, customer_id: str = "", medicare_beneficiary_identifier: str = "",
                   phone_number: str = "", email_address: str = "", full_name: str = "",
                   date_of_birth: str = "", residence_zip_code: str = "") -> str:
    """Find the member profile this call is about. The profile can be reached either by the member
    reference number, when that is already in hand, or by what a caller can naturally say: the
    identifier on their Medicare card, the telephone number or email address they gave the plan,
    their name, their date of birth, or the ZIP code where they live. Every criterion is optional,
    and what the caller says is matched after ordinary differences of spacing, punctuation and
    capitalisation are set aside, so a number read out with dashes still finds the profile.

    The profile that comes back carries the member's name and contact details, their Medicare
    identifier and the dates their Part A and Part B began, their Medicaid standing and
    prescription low-income subsidy level, the language and format they asked to be served in, the
    date the profile was opened, and anyone they have appointed in writing to act for them.

    Finding a profile is not the same as proving who is on the telephone: identity is established
    separately before any account business is discussed or transacted.

    Args:
        customer_id: Id class - the member reference number, when it is already in hand; leave "" if it is not known.
        medicare_beneficiary_identifier: Fixed-format class - the eleven-character identifier from the caller's Medicare card, uppercase letters and digits with no dashes; leave "" if not given.
        phone_number: Fixed-format class - the telephone number the caller gives, ten digits with no punctuation; leave "" if not given.
        email_address: Verbatim class - the email address the caller gives, exactly as stated; leave "" if not given.
        full_name: Verbatim class - the caller's name as it appears on their Medicare card, exactly as stated; leave "" if not given.
        date_of_birth: Fixed-format class - the caller's date of birth as YYYY-MM-DD; leave "" if not given.
        residence_zip_code: Fixed-format class - the five-digit ZIP code of the caller's permanent residence; leave "" if not given.
    """
    match = {k: v for k, v in {"customer_id": customer_id,
                               "medicare_beneficiary_identifier": medicare_beneficiary_identifier,
                               "phone_number": phone_number,
                               "email_address": email_address,
                               "full_name": full_name,
                               "date_of_birth": date_of_birth,
                               "residence_zip_code": residence_zip_code}.items() if v}
    if not match:
        return "Error: give at least one reference number or one piece of profile information to find the member."
    rows = ctx.fuzzy_find("customers", **match)
    if not rows:
        return f"No member profile matches {match}."
    if len(rows) > 1:
        return (f"Error: {len(rows)} member profiles match {match}; ask the caller for one more "
                "piece of information to tell them apart.")
    return str(rows[0])


@tool(owner="agent", rw="write")
def verify_member_identity(ctx: ToolContext, customer_id: str, medicare_beneficiary_identifier: str = "", date_of_birth: str = "", phone_number: str = "", email_address: str = "", residence_zip_code: str = "", part_b_effective_date: str = "", profile_opened_date: str = "") -> str:
    """Establish that the caller is the member whose account is about to be discussed, and record
    the outcome. This must pass before anything on the account is read out, changed or paid.

    The comparison is made here rather than judged by ear: each piece of information the caller
    offers is checked against the member profile, and the caller is verified once at least two of
    them match. The member reference number is used only to fetch the profile and never counts as
    one of the matches. Callers rarely remember everything, so pass only what they actually say,
    word for word as they say it, and leave the rest blank.

    A caller who does not pass at first may offer something further and be checked again; once they
    have passed, the pass stands for the rest of the call.

    Args:
        customer_id: Id class - the member reference number read from the member profile. Required, never blank; used only to fetch that profile and never counted toward the match.
        medicare_beneficiary_identifier: The eleven-character Medicare Beneficiary Identifier from the caller's red, white and blue Medicare card, uppercase letters and digits with no dashes, exactly as the caller states it; leave "" when they do not give it.
        date_of_birth: The caller's date of birth as YYYY-MM-DD, exactly as the caller states it; leave "" when they do not give it.
        phone_number: The telephone number the caller gives as the one on file, ten digits with no punctuation, exactly as the caller states it; leave "" when they do not give it.
        email_address: The email address the caller gives as the one on file, exactly as the caller states it; leave "" when they do not give it.
        residence_zip_code: The five-digit ZIP code of the caller's permanent residence, exactly as the caller states it; leave "" when they do not give it.
        part_b_effective_date: The date the caller's Medicare Part B enrolment began, as YYYY-MM-DD, exactly as the caller states it; leave "" when they do not give it.
        profile_opened_date: The date the caller first became a member of the plan, as YYYY-MM-DD, exactly as the caller states it; leave "" when they do not give it.
    """
    if not customer_id:
        return "Error: customer_id is required; find the member profile first and pass its reference number."
    rows = ctx.find("customers", customer_id=customer_id)
    if not rows:
        return f"Error: no member profile {customer_id}; identity cannot be established."
    profile = rows[0]
    supplied = {"medicare_beneficiary_identifier": medicare_beneficiary_identifier,
                "date_of_birth": date_of_birth,
                "phone_number": phone_number,
                "email_address": email_address,
                "residence_zip_code": residence_zip_code,
                "part_b_effective_date": part_b_effective_date,
                "profile_opened_date": profile_opened_date}
    matched = sum(1 for field, value in supplied.items()
                  if value and str(profile.get(field)) == str(value))
    verified = matched >= 2
    rid = ctx.make_id("ver_", customer_id)
    prior = ctx.find("identity_verification_log", verification_id=rid)
    verified = verified or bool(prior and prior[0].get("verified"))
    if prior:
        ctx.update("identity_verification_log", rid, verified=verified, verified_at=ctx.now())
    else:
        ctx.create("identity_verification_log", rid, verification_id=rid, customer_id=customer_id,
                   verified=verified, verified_at=ctx.now())
    if verified:
        return f"Identity established for {customer_id} ({matched} piece(s) of information matched the profile)."
    return (f"Identity NOT established for {customer_id} (only {matched} of the two required pieces "
            "of information matched). Ask the caller for something else held on their profile and try again.")


@tool(owner="agent", rw="write")
def transfer_to_human_representative(ctx: ToolContext, customer_id: str, reason: str) -> str:
    """Hand the member over to a human representative to carry on with them, and record that the
    handover was made and why.

    There are exactly two situations in which this is right. The first is where nothing in the
    plan's published rules can settle what the member is asking for, so no correct answer can be
    reached and the matter has to go to somebody who can take it further. The second is where the
    member has asked to speak to a person at least twice in the same conversation; at that point
    their wish is honoured rather than argued with.

    Args:
        customer_id: Id class - the member reference number read from the member profile, which must exist.
        reason: Enum class - why the handover is being made, one of POLICY_NOT_COVERED or CUSTOMER_REQUESTED, never anything else.
            POLICY_NOT_COVERED - no published rule of the plan can decide what the member is asking for;
            CUSTOMER_REQUESTED - the member has explicitly asked for a human representative at least twice.
    """
    allowed = {"POLICY_NOT_COVERED", "CUSTOMER_REQUESTED"}
    if reason not in allowed:
        return f"Error: unknown handover reason '{reason}'. Valid: {', '.join(sorted(allowed))}."
    if not ctx.find("customers", customer_id=customer_id):
        return f"Error: no member profile {customer_id}; the handover cannot be recorded."
    rid = ctx.make_id("hof_", customer_id, reason)
    ctx.create("human_handoff_log", rid, handoff_id=rid, customer_id=customer_id,
               reason=reason, created_at=ctx.now())
    return f"Handover to a human representative recorded for {customer_id} ({reason})."

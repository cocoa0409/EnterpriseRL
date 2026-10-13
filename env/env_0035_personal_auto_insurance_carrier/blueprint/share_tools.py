"""Shared tools for env_0035_personal_auto_insurance_carrier (Cardinal Mutual Insurance Company).
Output of the erl-scenario-blueprint skill.
Path: env/env_0035_personal_auto_insurance_carrier/blueprint/share_tools.py

Every tool here is a SHARE tool: always present in its owner's tool list.
  - one record finder per table (the customers finder doubles as the identity entry)
  - the identity-verification write (K = 2 matching credentials)
  - the transfer-to-human write (R = 2 explicit requests; reasons POLICY_NOT_COVERED / CUSTOMER_REQUESTED)
Customer-originated writes (signing, consenting, paying) are hidden task tools authored per difficulty.
Finders perform plain lookups only; every business decision stays with the agent.
"""

from erlbench import ToolContext, tool


def _criteria(values: dict) -> dict:
    # Shared helper (not a tool): keep only the criteria the caller actually supplied.
    return {k: v for k, v in values.items() if v}


def _render(rows: list, label: str, match: dict) -> str:
    # Shared helper (not a tool): format a lookup result; refuse an empty search.
    if not match:
        return "Error: provide at least one reference number to search by."
    return str(rows) if rows else f"No {label} found for {match}."


# --------------------------------------------------------------------------------------------
# Customer profile and household world records
# --------------------------------------------------------------------------------------------

@tool(owner="agent", rw="read")
def find_customers(ctx: ToolContext, customer_id: str = "", name: str = "",
                   phone_number: str = "", email: str = "") -> str:
    """Look up the policyholder profile to establish whose account this call is about.

    You can search by the customer reference number, or by what a caller naturally tells you:
    the phone number on file, the email address on file, or the full name. Supply whichever you
    have; at least one is needed. The profile shows the named insured's contact and mailing
    details, date of birth, the last four characters of the driver's license, the date the
    customer first joined Cardinal, months of prior insurance, and the homeowner, multi-policy and
    paperless indicators. Finding a profile does not verify the caller's identity.

    Args:
        customer_id: The customer reference number, if already known; leave "" otherwise.
        name: The caller's full name as they state it; leave "" if not given.
        phone_number: The phone number the caller gives, 10 digits; leave "" if not given.
        email: The email address the caller gives; leave "" if not given.
    """
    match = {k: v for k, v in {"customer_id": customer_id, "name": name,
                               "phone_number": phone_number, "email": email}.items() if v}
    if not match:
        return "Error: provide at least one of customer_id, name, phone_number or email."
    rows = ctx.fuzzy_find("customers", **match)
    if not rows:
        return f"No customer matches {match}."
    if len(rows) > 1:
        return f"Error: {len(rows)} customers match {match}; ask the caller for one more detail."
    return str(rows[0])


@tool(owner="agent", rw="read")
def find_vehicles(ctx: ToolContext, vehicle_id: str = "", customer_id: str = "") -> str:
    """List the vehicles a household owns or leases, as recorded from titles and bills of sale.

    Each vehicle record carries the VIN, year, make and model, body style, whether it is owned,
    financed or leased with the lienholder or lessor exactly as on the contract, the acquisition
    date and odometer at acquisition, whether it was bought new, and where it is garaged. Search
    by the vehicle reference number or by the customer to see the whole household's vehicles.
    Returns every matching vehicle, or a not-found message.

    Args:
        vehicle_id: The vehicle reference number; leave "" if unknown.
        customer_id: The customer reference number of the household; leave "" if unknown.
    """
    match = _criteria({"vehicle_id": vehicle_id, "customer_id": customer_id})
    return _render(ctx.find("vehicles", **match), "vehicles", match)


@tool(owner="agent", rw="read")
def find_drivers(ctx: ToolContext, driver_id: str = "", customer_id: str = "") -> str:
    """List the licensed and permit-holding members of a household.

    A driver record shows the full name and date of birth, relationship to the named insured,
    license state, number and current status, the date first licensed, the date the member became
    a licensed household driver, the good-student indicator and the latest defensive driving
    course date. Search by the driver reference number or by the customer for the whole household.

    Args:
        driver_id: The driver reference number; leave "" if unknown.
        customer_id: The customer reference number of the household; leave "" if unknown.
    """
    match = _criteria({"driver_id": driver_id, "customer_id": customer_id})
    return _render(ctx.find("drivers", **match), "drivers", match)


@tool(owner="agent", rw="read")
def find_driving_records(ctx: ToolContext, record_id: str = "", driver_id: str = "",
                         customer_id: str = "") -> str:
    """Retrieve motor vehicle report and loss history entries for household drivers.

    Each entry is one violation or accident: its class (major or minor violation, at-fault or
    not-at-fault accident, comprehensive loss), the specific description, the incident date, the
    amount any insurer paid on an accident, and where the entry came from. Search by the entry
    reference number, by driver, or by household.

    Args:
        record_id: The reference number of one entry; leave "" if unknown.
        driver_id: The driver reference number; leave "" if unknown.
        customer_id: The customer reference number of the household; leave "" if unknown.
    """
    match = _criteria({
        "record_id": record_id,
        "driver_id": driver_id,
        "customer_id": customer_id,
    })
    return _render(ctx.find("driving_records", **match), "driving records", match)


@tool(owner="agent", rw="read")
def find_rating_worksheets(ctx: ToolContext, worksheet_id: str = "", customer_id: str = "",
                           policy_id: str = "", vehicle_id: str = "") -> str:
    """Retrieve the rating worksheets produced for vehicles on a policy term.

    A worksheet gives, for one vehicle, one coverage package and one term, the full-term base
    premium for liability and the full-term base premium for collision and comprehensive at the
    reference deductible, together with the garaging ZIP code rated and the date produced. Search
    by worksheet, customer, policy or vehicle reference number.

    Args:
        worksheet_id: The worksheet reference number; leave "" if unknown.
        customer_id: The customer reference number; leave "" if unknown.
        policy_id: The policy reference number; leave "" if unknown.
        vehicle_id: The vehicle reference number; leave "" if unknown.
    """
    match = _criteria({
        "worksheet_id": worksheet_id,
        "customer_id": customer_id,
        "policy_id": policy_id,
        "vehicle_id": vehicle_id,
    })
    return _render(ctx.find("rating_worksheets", **match), "rating worksheets", match)


@tool(owner="agent", rw="read")
def find_state_orders(ctx: ToolContext, order_id: str = "", customer_id: str = "",
                      driver_id: str = "") -> str:
    """Retrieve state financial-responsibility orders on file for household drivers.

    An order shows the issuing state, whether an SR-22 or an FR-44 is required, the offense or
    event behind it, the state case number exactly as printed, the order date and the last day
    the state requires continuous proof of insurance. Search by order, household or driver.

    Args:
        order_id: The order reference number; leave "" if unknown.
        customer_id: The customer reference number of the household; leave "" if unknown.
        driver_id: The driver reference number; leave "" if unknown.
    """
    match = _criteria({
        "order_id": order_id,
        "customer_id": customer_id,
        "driver_id": driver_id,
    })
    return _render(ctx.find("state_orders", **match), "state orders", match)


# --------------------------------------------------------------------------------------------
# Personal auto policy
# --------------------------------------------------------------------------------------------

@tool(owner="agent", rw="read")
def find_auto_policies(ctx: ToolContext, policy_id: str = "", customer_id: str = "") -> str:
    """Look up a customer's Cardinal personal auto policies.

    A policy shows its printed policy number, coverage package, status, governing state, current
    term dates, original inception date, any pending or completed cancellation date, the date and
    reason coverage ended, and whether a financial-responsibility filing is carried. Search by the
    policy reference number or by the customer to see every policy they hold.

    Args:
        policy_id: The policy reference number; leave "" if unknown.
        customer_id: The customer reference number; leave "" if unknown.
    """
    match = _criteria({"policy_id": policy_id, "customer_id": customer_id})
    return _render(ctx.find("auto_policies", **match), "auto policies", match)


@tool(owner="agent", rw="read")
def find_auto_transactions(ctx: ToolContext, transaction_id: str = "", policy_id: str = "",
                           customer_id: str = "", vehicle_id: str = "",
                           replaced_vehicle_id: str = "", driver_id: str = "",
                           request_id: str = "", source_transaction_id: str = "") -> str:
    """Review the transaction history of an auto policy.

    The history holds every endorsement (vehicles added, replaced or removed, drivers added,
    excluded or removed, garaging and lienholder changes, rideshare and optional-coverage
    changes), every premium written (full-term, additional and return premium with the
    transaction that produced it), renewal offers and nonrenewal notices, each with its effective
    date and the premium before and after. Search by any reference number you hold.

    Args:
        transaction_id: The reference number of one transaction; leave "" if unknown.
        policy_id: The policy reference number; leave "" if unknown.
        customer_id: The customer reference number; leave "" if unknown.
        vehicle_id: A vehicle the transaction concerns; leave "" if unknown.
        replaced_vehicle_id: The vehicle that left the policy in a replacement; leave "" if unknown.
        driver_id: A driver the transaction concerns; leave "" if unknown.
        request_id: A signed request the transaction carried out; leave "" if unknown.
        source_transaction_id: The transaction or coverage record that gave rise to a premium
            entry or optional-coverage change; leave "" if unknown.
    """
    match = _criteria({
        "transaction_id": transaction_id,
        "policy_id": policy_id,
        "customer_id": customer_id,
        "vehicle_id": vehicle_id,
        "replaced_vehicle_id": replaced_vehicle_id,
        "driver_id": driver_id,
        "request_id": request_id,
        "source_transaction_id": source_transaction_id,
    })
    return _render(ctx.find("auto_transactions", **match), "auto transactions", match)


@tool(owner="agent", rw="read")
def find_auto_change_requests(ctx: ToolContext, request_id: str = "", customer_id: str = "",
                              policy_id: str = "", driver_id: str = "") -> str:
    """Check requests that need the named insured's signature, such as a cancellation request or a
    named driver exclusion.

    Each request shows its type, the effective date asked for, whether it is awaiting signature,
    signed, withdrawn or expired, and the signing date. Search by request, customer, policy or the
    driver an exclusion names.

    Args:
        request_id: The request reference number; leave "" if unknown.
        customer_id: The customer reference number; leave "" if unknown.
        policy_id: The policy reference number; leave "" if unknown.
        driver_id: The driver named on an exclusion request; leave "" if unknown.
    """
    match = _criteria({
        "request_id": request_id,
        "customer_id": customer_id,
        "policy_id": policy_id,
        "driver_id": driver_id,
    })
    return _render(ctx.find("auto_change_requests", **match), "change requests", match)


# --------------------------------------------------------------------------------------------
# Billing
# --------------------------------------------------------------------------------------------

@tool(owner="agent", rw="read")
def find_billing_accounts(ctx: ToolContext, billing_account_id: str = "", customer_id: str = "",
                          policy_id: str = "") -> str:
    """Look up the billing account behind an auto policy.

    The account shows its pay plan, status, current balance (positive when the customer owes, a
    credit when negative), the payment method on file, whether automatic payments are on, the
    installment due day, the term being billed and any certified-funds restriction. Search by the
    billing account, customer or policy reference number.

    Args:
        billing_account_id: The billing account reference number; leave "" if unknown.
        customer_id: The customer reference number; leave "" if unknown.
        policy_id: The policy reference number; leave "" if unknown.
    """
    match = _criteria({
        "billing_account_id": billing_account_id,
        "customer_id": customer_id,
        "policy_id": policy_id,
    })
    return _render(ctx.find("billing_accounts", **match), "billing accounts", match)


@tool(owner="agent", rw="read")
def find_billing_ledger(ctx: ToolContext, entry_id: str = "", billing_account_id: str = "",
                        customer_id: str = "", policy_id: str = "",
                        source_transaction_id: str = "", original_entry_id: str = "") -> str:
    """Review the billing history of an account, entry by entry.

    Entries cover premium received for scheduling, installments invoiced with their due dates,
    every fee charged or waived, payments with their confirmation numbers, method and channel,
    returned payments, immediate endorsement charges, credits, refunds, write-offs and notices of
    cancellation with their cancellation date and amount required to rescind. Search by any
    reference number you hold.

    Args:
        entry_id: The reference number of one entry; leave "" if unknown.
        billing_account_id: The billing account reference number; leave "" if unknown.
        customer_id: The customer reference number; leave "" if unknown.
        policy_id: The policy reference number; leave "" if unknown.
        source_transaction_id: The policy, filing or device transaction an entry is tied to;
            leave "" if unknown.
        original_entry_id: The entry another entry reverses, waives or is charged against;
            leave "" if unknown.
    """
    match = _criteria({
        "entry_id": entry_id,
        "billing_account_id": billing_account_id,
        "customer_id": customer_id,
        "policy_id": policy_id,
        "source_transaction_id": source_transaction_id,
        "original_entry_id": original_entry_id,
    })
    return _render(ctx.find("billing_ledger", **match), "billing entries", match)


@tool(owner="agent", rw="read")
def find_billing_reinstatement_requests(ctx: ToolContext, request_id: str = "",
                                        customer_id: str = "", billing_account_id: str = "",
                                        policy_id: str = "") -> str:
    """Check reinstatement requests waiting on the named insured's signed statement of no loss.

    Each request shows the first day without coverage and whether the statement is awaited,
    signed, declined because a loss was reported, or withdrawn. Search by request, customer,
    billing account or policy.

    Args:
        request_id: The request reference number; leave "" if unknown.
        customer_id: The customer reference number; leave "" if unknown.
        billing_account_id: The billing account reference number; leave "" if unknown.
        policy_id: The policy reference number; leave "" if unknown.
    """
    match = _criteria({
        "request_id": request_id,
        "customer_id": customer_id,
        "billing_account_id": billing_account_id,
        "policy_id": policy_id,
    })
    return _render(ctx.find("billing_reinstatement_requests", **match), "reinstatement requests", match)


# --------------------------------------------------------------------------------------------
# Physical damage coverage and claims
# --------------------------------------------------------------------------------------------

@tool(owner="agent", rw="read")
def find_physdmg_coverages(ctx: ToolContext, coverage_id: str = "", customer_id: str = "",
                           policy_id: str = "", vehicle_id: str = "") -> str:
    """Look up collision and comprehensive coverage on a customer's vehicles.

    Each coverage shows the deductible option, its status (pending inspection, active, in storage
    or removed), effective and end dates, inspection due and completion dates, the loan/lease
    payoff option, Deductible Rewards enrollment and credit balance, and the loss payee. Search by
    coverage, customer, policy or vehicle.

    Args:
        coverage_id: The physical damage coverage reference number; leave "" if unknown.
        customer_id: The customer reference number; leave "" if unknown.
        policy_id: The policy reference number; leave "" if unknown.
        vehicle_id: The vehicle reference number; leave "" if unknown.
    """
    match = _criteria({
        "coverage_id": coverage_id,
        "customer_id": customer_id,
        "policy_id": policy_id,
        "vehicle_id": vehicle_id,
    })
    return _render(ctx.find("physdmg_coverages", **match), "physical damage coverages", match)


@tool(owner="agent", rw="read")
def find_physdmg_claim_events(ctx: ToolContext, claim_event_id: str = "", coverage_id: str = "",
                              customer_id: str = "", driver_id: str = "") -> str:
    """Review the file of physical damage claims: loss reports, coverage decisions, fault findings,
    estimates and supplements, total-loss valuations, storage notices, closings and reopenings.

    Every entry carries its claim number, so the full story of one claim can be read in order.
    Search by entry, by the vehicle's coverage reference, by customer, or by the driver at the
    time of loss.

    Args:
        claim_event_id: The reference number of one claim entry; leave "" if unknown.
        coverage_id: The physical damage coverage reference number of the vehicle; leave "" if unknown.
        customer_id: The customer reference number; leave "" if unknown.
        driver_id: The driver at the time of loss; leave "" if unknown.
    """
    match = _criteria({
        "claim_event_id": claim_event_id,
        "coverage_id": coverage_id,
        "customer_id": customer_id,
        "driver_id": driver_id,
    })
    return _render(ctx.find("physdmg_claim_events", **match), "claim entries", match)


@tool(owner="agent", rw="read")
def find_physdmg_payments(ctx: ToolContext, payment_id: str = "", coverage_id: str = "",
                          customer_id: str = "", source_payment_id: str = "",
                          source_recovery_id: str = "") -> str:
    """Review money moved on physical damage claims and Deductible Rewards.

    Entries are claim payments by component and payee with the deductible taken, voided payments,
    recoveries from other insurers or salvage, and Deductible Rewards credits granted or used.
    Search by entry, coverage, customer, the payment a void reverses, or the recovery a
    deductible reimbursement came from.

    Args:
        payment_id: The reference number of one entry; leave "" if unknown.
        coverage_id: The physical damage coverage reference number; leave "" if unknown.
        customer_id: The customer reference number; leave "" if unknown.
        source_payment_id: The payment a void reverses; leave "" if unknown.
        source_recovery_id: The recovery a deductible reimbursement was paid from; leave "" if unknown.
    """
    match = _criteria({
        "payment_id": payment_id,
        "coverage_id": coverage_id,
        "customer_id": customer_id,
        "source_payment_id": source_payment_id,
        "source_recovery_id": source_recovery_id,
    })
    return _render(ctx.find("physdmg_payments", **match), "claim payment entries", match)


@tool(owner="agent", rw="read")
def find_physdmg_total_loss_settlements(ctx: ToolContext, settlement_id: str = "",
                                        customer_id: str = "", coverage_id: str = "") -> str:
    """Check total-loss settlement offers and where each stands.

    An offer shows the claim, whether the vehicle goes to Cardinal or is kept by the customer, the
    net settlement offered, the loss payee's payoff, the offer date, its status (offered, accepted,
    appraisal requested, withdrawn), the acceptance date and whether the signed title has arrived.

    Args:
        settlement_id: The settlement offer reference number; leave "" if unknown.
        customer_id: The customer reference number; leave "" if unknown.
        coverage_id: The physical damage coverage reference number; leave "" if unknown.
    """
    match = _criteria({
        "settlement_id": settlement_id,
        "customer_id": customer_id,
        "coverage_id": coverage_id,
    })
    return _render(ctx.find("physdmg_total_loss_settlements", **match), "settlement offers", match)


# --------------------------------------------------------------------------------------------
# Rental reimbursement
# --------------------------------------------------------------------------------------------

@tool(owner="agent", rw="read")
def find_rental_coverages(ctx: ToolContext, rental_coverage_id: str = "", customer_id: str = "",
                          policy_id: str = "", vehicle_id: str = "", coverage_id: str = "") -> str:
    """Look up rental reimbursement options carried on a customer's vehicles.

    Each option shows its daily limit and per-loss maximum (in its official name), status, the
    vehicle and the physical damage coverage it rides on, and its effective, change and end dates.

    Args:
        rental_coverage_id: The rental reimbursement reference number; leave "" if unknown.
        customer_id: The customer reference number; leave "" if unknown.
        policy_id: The policy reference number; leave "" if unknown.
        vehicle_id: The vehicle reference number; leave "" if unknown.
        coverage_id: The physical damage coverage reference number of the same vehicle; leave "" if unknown.
    """
    match = _criteria({
        "rental_coverage_id": rental_coverage_id,
        "customer_id": customer_id,
        "policy_id": policy_id,
        "vehicle_id": vehicle_id,
        "coverage_id": coverage_id,
    })
    return _render(ctx.find("rental_coverages", **match), "rental options", match)


@tool(owner="agent", rw="read")
def find_rental_ledger(ctx: ToolContext, rental_entry_id: str = "", rental_coverage_id: str = "",
                       customer_id: str = "", source_entry_id: str = "") -> str:
    """Review rentals on claims: authorizations, extensions, closings, transfers to the at-fault
    party's insurer, agency invoices paid, customer reimbursements and recoveries.

    Entries carry the claim number and authorization number, the days, rates and amounts paid, and
    what was left as the customer's responsibility. Search by entry, option, customer, or the
    payment a recovery was taken against.

    Args:
        rental_entry_id: The reference number of one entry; leave "" if unknown.
        rental_coverage_id: The rental reimbursement reference number; leave "" if unknown.
        customer_id: The customer reference number; leave "" if unknown.
        source_entry_id: The payment a recovery was taken against; leave "" if unknown.
    """
    match = _criteria({
        "rental_entry_id": rental_entry_id,
        "rental_coverage_id": rental_coverage_id,
        "customer_id": customer_id,
        "source_entry_id": source_entry_id,
    })
    return _render(ctx.find("rental_ledger", **match), "rental entries", match)


# --------------------------------------------------------------------------------------------
# Financial-responsibility filings
# --------------------------------------------------------------------------------------------

@tool(owner="agent", rw="read")
def find_sr22_filings(ctx: ToolContext, filing_id: str = "", customer_id: str = "",
                      policy_id: str = "", driver_id: str = "", order_id: str = "") -> str:
    """Look up SR-22 and FR-44 filings Cardinal maintains for household drivers.

    A filing shows its certificate type, status (requested, filed, accepted, rejected,
    cancel-notified, lapsed, released), the state receiving it, the request, certificate,
    acknowledgment and end dates, and any pending SR-26 effective date. Search by filing,
    customer, policy, driver or the state order it answers.

    Args:
        filing_id: The filing reference number; leave "" if unknown.
        customer_id: The customer reference number; leave "" if unknown.
        policy_id: The policy reference number; leave "" if unknown.
        driver_id: The driver reference number; leave "" if unknown.
        order_id: The state order reference number; leave "" if unknown.
    """
    match = _criteria({
        "filing_id": filing_id,
        "customer_id": customer_id,
        "policy_id": policy_id,
        "driver_id": driver_id,
        "order_id": order_id,
    })
    return _render(ctx.find("sr22_filings", **match), "filings", match)


@tool(owner="agent", rw="read")
def find_sr22_ledger(ctx: ToolContext, sr22_entry_id: str = "", filing_id: str = "",
                     customer_id: str = "", source_transaction_id: str = "") -> str:
    """Review the history of a filing with the state: fees assessed, documents transmitted with
    their confirmation numbers, state acknowledgments and rejection codes, and amendments.

    Args:
        sr22_entry_id: The reference number of one entry; leave "" if unknown.
        filing_id: The filing reference number; leave "" if unknown.
        customer_id: The customer reference number; leave "" if unknown.
        source_transaction_id: The policy endorsement that led to an amendment; leave "" if unknown.
    """
    match = _criteria({
        "sr22_entry_id": sr22_entry_id,
        "filing_id": filing_id,
        "customer_id": customer_id,
        "source_transaction_id": source_transaction_id,
    })
    return _render(ctx.find("sr22_ledger", **match), "filing entries", match)


# --------------------------------------------------------------------------------------------
# DriveSense and roadside assistance
# --------------------------------------------------------------------------------------------

@tool(owner="agent", rw="read")
def find_telematics_enrollments(ctx: ToolContext, enrollment_id: str = "", customer_id: str = "",
                                policy_id: str = "", vehicle_id: str = "",
                                driver_id: str = "") -> str:
    """Look up DriveSense enrollments.

    An enrollment shows the program, status, enrollment and first-trip dates, the final score and
    the earned discount or surcharge once scored, the device serial number for plug-in programs,
    and when and why it ended.

    Args:
        enrollment_id: The enrollment reference number; leave "" if unknown.
        customer_id: The customer reference number; leave "" if unknown.
        policy_id: The policy reference number; leave "" if unknown.
        vehicle_id: The vehicle reference number; leave "" if unknown.
        driver_id: The driver scored; leave "" if unknown.
    """
    match = _criteria({
        "enrollment_id": enrollment_id,
        "customer_id": customer_id,
        "policy_id": policy_id,
        "vehicle_id": vehicle_id,
        "driver_id": driver_id,
    })
    return _render(ctx.find("telematics_enrollments", **match), "DriveSense enrollments", match)


@tool(owner="agent", rw="read")
def find_telematics_events(ctx: ToolContext, telematics_event_id: str = "",
                           enrollment_id: str = "", customer_id: str = "",
                           source_event_id: str = "") -> str:
    """Review DriveSense activity: device shipments and returns, monthly scores and miles,
    device fees, and pay-per-mile charges and adjustments.

    Args:
        telematics_event_id: The reference number of one entry; leave "" if unknown.
        enrollment_id: The enrollment reference number; leave "" if unknown.
        customer_id: The customer reference number; leave "" if unknown.
        source_event_id: The mileage charge an adjustment corrects; leave "" if unknown.
    """
    match = _criteria({
        "telematics_event_id": telematics_event_id,
        "enrollment_id": enrollment_id,
        "customer_id": customer_id,
        "source_event_id": source_event_id,
    })
    return _render(ctx.find("telematics_events", **match), "DriveSense entries", match)


@tool(owner="agent", rw="read")
def find_roadside_coverages(ctx: ToolContext, roadside_id: str = "", customer_id: str = "",
                            policy_id: str = "", vehicle_id: str = "") -> str:
    """Look up roadside assistance options on a customer's vehicles, including the option level,
    status, effective and end dates, the current allowance period and the covered service calls
    left in it.

    Args:
        roadside_id: The roadside assistance reference number; leave "" if unknown.
        customer_id: The customer reference number; leave "" if unknown.
        policy_id: The policy reference number; leave "" if unknown.
        vehicle_id: The vehicle reference number; leave "" if unknown.
    """
    match = _criteria({
        "roadside_id": roadside_id,
        "customer_id": customer_id,
        "policy_id": policy_id,
        "vehicle_id": vehicle_id,
    })
    return _render(ctx.find("roadside_coverages", **match), "roadside options", match)


@tool(owner="agent", rw="read")
def find_roadside_events(ctx: ToolContext, roadside_event_id: str = "", roadside_id: str = "",
                         customer_id: str = "", source_event_id: str = "") -> str:
    """Review roadside service history: allowances granted, dispatches with service type and tow
    miles, calls restored, amounts the member paid the provider, out-of-network reimbursements and
    trip interruption payments.

    Args:
        roadside_event_id: The reference number of one entry; leave "" if unknown.
        roadside_id: The roadside assistance reference number; leave "" if unknown.
        customer_id: The customer reference number; leave "" if unknown.
        source_event_id: The dispatch a restored call refers to; leave "" if unknown.
    """
    match = _criteria({
        "roadside_event_id": roadside_event_id,
        "roadside_id": roadside_id,
        "customer_id": customer_id,
        "source_event_id": source_event_id,
    })
    return _render(ctx.find("roadside_events", **match), "roadside entries", match)


# --------------------------------------------------------------------------------------------
# Service records
# --------------------------------------------------------------------------------------------

@tool(owner="agent", rw="read")
def find_identity_verifications(ctx: ToolContext, verification_id: str = "",
                                customer_id: str = "") -> str:
    """See whether a customer's identity has been verified, and when it was last checked.

    Args:
        verification_id: The verification reference number; leave "" if unknown.
        customer_id: The customer reference number; leave "" if unknown.
    """
    match = _criteria({"verification_id": verification_id, "customer_id": customer_id})
    return _render(ctx.find("identity_verifications", **match), "identity verifications", match)


@tool(owner="agent", rw="read")
def find_human_handoffs(ctx: ToolContext, handoff_id: str = "", customer_id: str = "") -> str:
    """See whether a customer has already been handed to a human representative, with the reason
    and time.

    Args:
        handoff_id: The handoff reference number; leave "" if unknown.
        customer_id: The customer reference number; leave "" if unknown.
    """
    match = _criteria({"handoff_id": handoff_id, "customer_id": customer_id})
    return _render(ctx.find("human_handoffs", **match), "handoffs", match)


# --------------------------------------------------------------------------------------------
# Identity verification and handoff
# --------------------------------------------------------------------------------------------

@tool(owner="agent", rw="write")
def verify_customer_identity(ctx: ToolContext, customer_id: str, phone_number: str = "",
                             email: str = "", date_of_birth: str = "",
                             drivers_license_last4: str = "", mailing_zip: str = "") -> str:
    """Verify the caller's identity against the policyholder profile and record the outcome.

    Identity must be verified before any account detail is discussed or any change, payment,
    claim or filing is handled. This tool does the comparison itself: it checks each piece of
    identity information the caller gives against the profile and passes only when at least 2
    of them match exactly. The customer reference number only locates the profile and never
    counts as a match. Pass exactly what the caller said for the items they gave and leave the
    others blank. If a first attempt does not pass and the caller then gives more information, call
    again with everything they have given; once verified, the customer stays verified.

    Args:
        customer_id: The customer reference number from the profile lookup; required. It is used
            only to retrieve the profile and does not count toward the matches.
        phone_number: The phone number the caller gives, 10 digits without punctuation; leave ""
            if not given.
        email: The email address the caller gives, exactly as stated; leave "" if not given.
        date_of_birth: The caller's date of birth as YYYY-MM-DD; leave "" if not given.
        drivers_license_last4: The last four characters of the caller's driver's license number,
            as printed; leave "" if not given.
        mailing_zip: The 5-digit ZIP code of the caller's mailing address; leave "" if not given.
    """
    if not customer_id:
        return "Error: customer_id is required; look the customer up first and pass their reference number."
    rows = ctx.find("customers", customer_id=customer_id)
    if not rows:
        return f"Error: no customer {customer_id}; cannot verify."
    rec = rows[0]
    # The locator customer_id is not a credential; only the supplied attributes are compared.
    supplied = {"phone_number": phone_number, "email": email, "date_of_birth": date_of_birth,
                "drivers_license_last4": drivers_license_last4, "mailing_zip": mailing_zip}
    matched = sum(1 for field, value in supplied.items()
                  if value and str(rec.get(field, "")).strip().lower() == str(value).strip().lower())
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
        return f"Identity verified for customer {customer_id}."
    return (f"Identity NOT verified for customer {customer_id}: only {matched} of the 2 required "
            "items matched. Ask the caller for another item on file and try again.")


@tool(owner="agent", rw="write")
def transfer_to_human_agent(ctx: ToolContext, customer_id: str, reason: str) -> str:
    """Hand the customer over to a licensed Cardinal representative and record why.

    Use POLICY_NOT_COVERED when no Cardinal rule or procedure available to you can resolve what
    the customer needs. Use CUSTOMER_REQUESTED when the customer has explicitly asked for a human
    representative 2 times. Tell the customer they are being transferred.

    Args:
        customer_id: The customer reference number from the profile lookup.
        reason: Exactly one of POLICY_NOT_COVERED or CUSTOMER_REQUESTED; no other wording.
    """
    allowed = {"POLICY_NOT_COVERED", "CUSTOMER_REQUESTED"}
    if reason not in allowed:
        return f"Error: unknown handoff reason '{reason}'. Valid: {', '.join(sorted(allowed))}."
    if not ctx.find("customers", customer_id=customer_id):
        return f"Error: no customer {customer_id}; cannot record the handoff."
    rid = ctx.make_id("hof_", customer_id, reason)
    ctx.create("human_handoffs", rid, handoff_id=rid, customer_id=customer_id, reason=reason,
               created_at=ctx.now())
    return f"Transfer to a human representative recorded for customer {customer_id} ({reason})."

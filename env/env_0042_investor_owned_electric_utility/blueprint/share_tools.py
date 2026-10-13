"""Shared tools for env_0042_investor_owned_electric_utility (Lakeshore Power & Light Company).

Every tool here is a share tool, always available to its owner in every task: one record finder
per table (the customer finder doubles as the identity entry), the identity-verification write and
the transfer-to-human write. Customer-originated writes live in each difficulty's task_tools.py.
"""

from erlbench import ToolContext, tool


def _pick(**kwargs):
    # Keep only the criteria the caller actually supplied.
    return {k: v for k, v in kwargs.items() if v}


# --------------------------------------------------------------------------- customers & logs
@tool(owner="agent", rw="read")
def find_customers(ctx: ToolContext, customer_id: str = "", name: str = "", phone_number: str = "",
                   email: str = "") -> str:
    """Look up a customer profile to establish whose accounts the call is about.

    Search by the customer reference number, or by what the caller can tell you: the name on the
    account, the contact phone number or the contact email. Supply any one or more; matching
    ignores spacing, punctuation and capital letters. A match returns the full profile: customer
    reference number, name, residential or business class, phone, email, last four digits of the
    SSN or EIN, billing ZIP code, mailing address, date of birth (residential), the date the profile
    was opened, and the date through which any household income qualification remains valid.
    Finding a profile does not verify the caller's identity.

    Args:
        customer_id: Customer reference number (for example "cus_3f9a1c0e7b22"); leave "" if unknown.
        name: Full name of the account holder or registered business name, as the caller states it; leave "" if not given.
        phone_number: Contact phone number, 10 digits (separators are ignored); leave "" if not given.
        email: Contact email address; leave "" if not given.
    """
    match = _pick(customer_id=customer_id, name=name, phone_number=phone_number, email=email)
    if not match:
        return "Error: provide at least one of customer_id, name, phone_number or email to find the customer."
    rows = ctx.fuzzy_find("customers", **match)
    if not rows:
        return f"No customer matches {match}."
    if len(rows) > 1:
        return f"Error: {len(rows)} customers match {match}; ask the caller for one more detail to tell them apart."
    return str(rows[0])


@tool(owner="agent", rw="read")
def find_identity_verifications(ctx: ToolContext, verification_id: str = "", customer_id: str = "") -> str:
    """Check whether a customer's identity has already been verified in this conversation.

    Returns the verification outcome on file (verified true or false) and when it was last checked.

    Args:
        verification_id: Reference number of the verification outcome; leave "" if unknown.
        customer_id: Customer reference number whose verification you want to see; leave "" if unknown.
    """
    match = _pick(verification_id=verification_id, customer_id=customer_id)
    rows = ctx.find("identity_verifications", **match)
    return str(rows) if rows else f"No identity verification on file for {match or 'any customer'}."


@tool(owner="agent", rw="read")
def find_human_handoffs(ctx: ToolContext, handoff_id: str = "", customer_id: str = "") -> str:
    """List transfers of a customer to a human representative, with the reason and time of each.

    Args:
        handoff_id: Reference number of a transfer; leave "" if unknown.
        customer_id: Customer reference number; leave "" if unknown.
    """
    match = _pick(handoff_id=handoff_id, customer_id=customer_id)
    rows = ctx.find("human_handoffs", **match)
    return str(rows) if rows else f"No transfers to a human representative for {match or 'any customer'}."


# --------------------------------------------------------------------------- electric service
@tool(owner="agent", rw="read")
def find_service_accounts(ctx: ToolContext, service_account_id: str = "", customer_id: str = "") -> str:
    """Look up electric service agreements (service accounts).

    Each agreement shows the service address, the rate schedule in effect and when it took effect,
    its status (pending start, active, disconnection notice pending, disconnected or closed) and the
    date of the latest status change, the premise's space-heating source and delivery voltage, the
    registered electric vehicle for the EV schedule, start and stop dates, and the current balance
    (negative means a credit). Search by the service account number or by the customer reference
    number to list all of a customer's agreements.

    Args:
        service_account_id: Service account number; leave "" if unknown.
        customer_id: Customer reference number, to list that customer's agreements; leave "" if unknown.
    """
    match = _pick(service_account_id=service_account_id, customer_id=customer_id)
    rows = ctx.find("service_accounts", **match)
    return str(rows) if rows else f"No service agreements for {match or 'the whole register'}."


@tool(owner="agent", rw="read")
def find_service_bills(ctx: ToolContext, bill_id: str = "", service_account_id: str = "", customer_id: str = "") -> str:
    """Look up electricity bills.

    Each bill shows its bill date and due date, the billing period and pricing season, whether it is
    a regular or final bill and whether the reading was actual, estimated or customer-supplied, the
    kWh used by time-of-use period and in total, any medical baseline allowance applied, measured and
    billed demand, and the customer, energy, demand and Power Supply Cost Recovery charges with the
    total.

    Args:
        bill_id: Bill reference number; leave "" if unknown.
        service_account_id: Service account number, to list its bills; leave "" if unknown.
        customer_id: Customer reference number, to list bills on all of the customer's agreements; leave "" if unknown.
    """
    match = _pick(bill_id=bill_id, service_account_id=service_account_id, customer_id=customer_id)
    rows = ctx.find("service_bills", **match)
    return str(rows) if rows else f"No bills for {match or 'the whole register'}."


@tool(owner="agent", rw="read")
def find_service_charges(ctx: ToolContext, service_charge_id: str = "", service_account_id: str = "",
                         customer_id: str = "", bill_id: str = "", reversed_payment_id: str = "",
                         source_reference_id: str = "") -> str:
    """Look up fees and other charges posted to service agreements outside the monthly bill amount.

    Covers late payment charges (with the bill they were assessed on), reconnection charges (with the
    restoration method and timing), reversals of payments returned by the bank and the returned
    payment fees, connection charges, backbills, charges posted from payment, metering, generation,
    budget and demand response programs (with the program record they came from), and credit-balance
    refunds. Search by any reference number you hold.

    Args:
        service_charge_id: Reference number of the charge; leave "" if unknown.
        service_account_id: Service account number; leave "" if unknown.
        customer_id: Customer reference number; leave "" if unknown.
        bill_id: Bill a late payment charge was assessed on; leave "" if unknown.
        reversed_payment_id: Reference number of a returned payment, to find its reversal and fee; leave "" if unknown.
        source_reference_id: Reference number of the program record or closed agreement a charge came from; leave "" if unknown.
    """
    match = _pick(service_charge_id=service_charge_id, service_account_id=service_account_id, customer_id=customer_id,
                  bill_id=bill_id, reversed_payment_id=reversed_payment_id, source_reference_id=source_reference_id)
    rows = ctx.find("service_charges", **match)
    return str(rows) if rows else f"No charges for {match or 'the whole register'}."


@tool(owner="agent", rw="read")
def find_service_credits(ctx: ToolContext, service_credit_id: str = "", service_account_id: str = "",
                         customer_id: str = "", source_reference_id: str = "", outage_event_id: str = "") -> str:
    """Look up payments and credits on service agreements.

    Payments show the posting date, amount, payment channel and confirmation number. Credits show the
    kind of credit (outage credits, meter-error refunds, courtesy late-charge waivers, time-of-use
    bill protection, billing corrections, and credits from payment arrangements, deposits, net
    metering, budget billing, demand response or balance transfers) and the record they relate to.

    Args:
        service_credit_id: Reference number of the payment or credit; leave "" if unknown.
        service_account_id: Service account number; leave "" if unknown.
        customer_id: Customer reference number; leave "" if unknown.
        source_reference_id: Reference number of the record a credit relates to (for example a late payment charge waived); leave "" if unknown.
        outage_event_id: Outage reference number, to find outage credits granted for it; leave "" if unknown.
    """
    match = _pick(service_credit_id=service_credit_id, service_account_id=service_account_id, customer_id=customer_id,
                  source_reference_id=source_reference_id, outage_event_id=outage_event_id)
    rows = ctx.find("service_credits", **match)
    return str(rows) if rows else f"No payments or credits for {match or 'the whole register'}."


@tool(owner="agent", rw="read")
def find_service_notices(ctx: ToolContext, notice_id: str = "", service_account_id: str = "", customer_id: str = "") -> str:
    """Look up disconnection notices sent for nonpayment.

    Each notice shows whether it was the written notice or the final notice, the date and how it was
    delivered, the past-due amount stated, and the earliest date service could be disconnected.

    Args:
        notice_id: Notice reference number; leave "" if unknown.
        service_account_id: Service account number; leave "" if unknown.
        customer_id: Customer reference number; leave "" if unknown.
    """
    match = _pick(notice_id=notice_id, service_account_id=service_account_id, customer_id=customer_id)
    rows = ctx.find("service_notices", **match)
    return str(rows) if rows else f"No disconnection notices for {match or 'the whole register'}."


@tool(owner="agent", rw="read")
def find_service_outages(ctx: ToolContext, outage_event_id: str = "", service_account_id: str = "", customer_id: str = "") -> str:
    """Look up power outages recorded at a customer's service address.

    Each outage record shows when the interruption began and when power was restored, its length in
    hours, the recorded cause, and whether it began on a declared major event day.

    Args:
        outage_event_id: Outage reference number; leave "" if unknown.
        service_account_id: Service account number; leave "" if unknown.
        customer_id: Customer reference number; leave "" if unknown.
    """
    match = _pick(outage_event_id=outage_event_id, service_account_id=service_account_id, customer_id=customer_id)
    rows = ctx.find("service_outages", **match)
    return str(rows) if rows else f"No outage records for {match or 'the whole register'}."


@tool(owner="agent", rw="read")
def find_service_orders(ctx: ToolContext, service_order_id: str = "", customer_id: str = "", service_account_id: str = "") -> str:
    """Look up stop-service and start-cancellation orders and whether the customer has confirmed them.

    Args:
        service_order_id: Order reference number; leave "" if unknown.
        customer_id: Customer reference number; leave "" if unknown.
        service_account_id: Service account number; leave "" if unknown.
    """
    match = _pick(service_order_id=service_order_id, customer_id=customer_id, service_account_id=service_account_id)
    rows = ctx.find("service_orders", **match)
    return str(rows) if rows else f"No service orders for {match or 'the whole register'}."


# --------------------------------------------------------------------------- payment arrangements
@tool(owner="agent", rw="read")
def find_arrangement_plans(ctx: ToolContext, arrangement_id: str = "", customer_id: str = "", service_account_id: str = "") -> str:
    """Look up payment arrangements.

    Each arrangement shows its kind, status and the date of its latest status change, when and how it
    was set up, whether the account was disconnected at the time, the balance placed under it, the
    down payment (and whether it was waived) with its due date, the deferred amount, the number and
    amount of installments, and the balance still remaining.

    Args:
        arrangement_id: Arrangement reference number; leave "" if unknown.
        customer_id: Customer reference number; leave "" if unknown.
        service_account_id: Service account number; leave "" if unknown.
    """
    match = _pick(arrangement_id=arrangement_id, customer_id=customer_id, service_account_id=service_account_id)
    rows = ctx.find("arrangement_plans", **match)
    return str(rows) if rows else f"No payment arrangements for {match or 'the whole register'}."


@tool(owner="agent", rw="read")
def find_arrangement_ledger(ctx: ToolContext, arrangement_ledger_id: str = "", arrangement_id: str = "",
                            customer_id: str = "", service_account_id: str = "", bill_id: str = "") -> str:
    """Look up the history of payment arrangements: arrears deferred into the plan, installments billed,
    installments forgiven, installments recorded as missed, and balances returned to the account, each
    with its date, amount, installment number and the bill concerned.

    Args:
        arrangement_ledger_id: Reference number of a history entry; leave "" if unknown.
        arrangement_id: Arrangement reference number; leave "" if unknown.
        customer_id: Customer reference number; leave "" if unknown.
        service_account_id: Service account number; leave "" if unknown.
        bill_id: Bill reference number, to find installments billed, forgiven or missed on it; leave "" if unknown.
    """
    match = _pick(arrangement_ledger_id=arrangement_ledger_id, arrangement_id=arrangement_id, customer_id=customer_id,
                  service_account_id=service_account_id, bill_id=bill_id)
    rows = ctx.find("arrangement_ledger", **match)
    return str(rows) if rows else f"No arrangement history for {match or 'the whole register'}."


# --------------------------------------------------------------------------- security deposits
@tool(owner="agent", rw="read")
def find_deposit_accounts(ctx: ToolContext, deposit_id: str = "", customer_id: str = "", service_account_id: str = "") -> str:
    """Look up security deposits.

    Each deposit shows its kind, status, why and when it was required, the average bill used and the
    amount required, the number of installments allowed and the first due date, the form of security,
    any waiver basis, the date it became fully secured, the refund review date, and the cash and
    interest currently held.

    Args:
        deposit_id: Deposit reference number; leave "" if unknown.
        customer_id: Customer reference number; leave "" if unknown.
        service_account_id: Service account number; leave "" if unknown.
    """
    match = _pick(deposit_id=deposit_id, customer_id=customer_id, service_account_id=service_account_id)
    rows = ctx.find("deposit_accounts", **match)
    return str(rows) if rows else f"No security deposits for {match or 'the whole register'}."


@tool(owner="agent", rw="read")
def find_deposit_transactions(ctx: ToolContext, deposit_transaction_id: str = "", deposit_id: str = "",
                              customer_id: str = "", service_account_id: str = "") -> str:
    """Look up deposit payments, interest credited, refunds and applications to final bills, with dates,
    amounts, installment numbers and refund methods.

    Args:
        deposit_transaction_id: Reference number of a deposit transaction; leave "" if unknown.
        deposit_id: Deposit reference number; leave "" if unknown.
        customer_id: Customer reference number; leave "" if unknown.
        service_account_id: Service account number; leave "" if unknown.
    """
    match = _pick(deposit_transaction_id=deposit_transaction_id, deposit_id=deposit_id, customer_id=customer_id,
                  service_account_id=service_account_id)
    rows = ctx.find("deposit_transactions", **match)
    return str(rows) if rows else f"No deposit transactions for {match or 'the whole register'}."


# --------------------------------------------------------------------------- metering
@tool(owner="agent", rw="read")
def find_meter_installations(ctx: ToolContext, meter_installation_id: str = "", customer_id: str = "",
                             service_account_id: str = "") -> str:
    """Look up the meters installed or ordered at a customer's service addresses: meter type, meter
    number, status, why it was installed, and the order, installation and removal dates.

    Args:
        meter_installation_id: Meter installation reference number; leave "" if unknown.
        customer_id: Customer reference number; leave "" if unknown.
        service_account_id: Service account number; leave "" if unknown.
    """
    match = _pick(meter_installation_id=meter_installation_id, customer_id=customer_id, service_account_id=service_account_id)
    rows = ctx.find("meter_installations", **match)
    return str(rows) if rows else f"No meter installations for {match or 'the whole register'}."


@tool(owner="agent", rw="read")
def find_meter_reads(ctx: ToolContext, meter_read_id: str = "", meter_installation_id: str = "", customer_id: str = "") -> str:
    """Look up billing readings of a meter: reading date, whether actual, estimated or supplied by the
    customer, the register reading and the kWh since the previous reading.

    Args:
        meter_read_id: Reading reference number; leave "" if unknown.
        meter_installation_id: Meter installation reference number; leave "" if unknown.
        customer_id: Customer reference number; leave "" if unknown.
    """
    match = _pick(meter_read_id=meter_read_id, meter_installation_id=meter_installation_id, customer_id=customer_id)
    rows = ctx.find("meter_reads", **match)
    return str(rows) if rows else f"No meter readings for {match or 'the whole register'}."


@tool(owner="agent", rw="read")
def find_meter_tests(ctx: ToolContext, meter_test_id: str = "", meter_installation_id: str = "", customer_id: str = "",
                     test_request_id: str = "") -> str:
    """Look up meter accuracy test requests and test results.

    Requests show when and why the test was asked for, the scheduled date and whether the customer
    wants to witness it. Results show the request they answer, the test date and method, the
    registration percentage and whether the meter was within tolerance, fast, slow or not registering.

    Args:
        meter_test_id: Reference number of a test request or result; leave "" if unknown.
        meter_installation_id: Meter installation reference number; leave "" if unknown.
        customer_id: Customer reference number; leave "" if unknown.
        test_request_id: Reference number of a test request, to find its result; leave "" if unknown.
    """
    match = _pick(meter_test_id=meter_test_id, meter_installation_id=meter_installation_id, customer_id=customer_id,
                  test_request_id=test_request_id)
    rows = ctx.find("meter_tests", **match)
    return str(rows) if rows else f"No meter tests for {match or 'the whole register'}."


@tool(owner="agent", rw="read")
def find_meter_adjustments(ctx: ToolContext, meter_adjustment_id: str = "", meter_installation_id: str = "",
                           customer_id: str = "", meter_test_id: str = "") -> str:
    """Look up billing adjustments made after a meter test: refund or backbill, the adjustment period,
    the kWh and the amount.

    Args:
        meter_adjustment_id: Adjustment reference number; leave "" if unknown.
        meter_installation_id: Meter installation reference number; leave "" if unknown.
        customer_id: Customer reference number; leave "" if unknown.
        meter_test_id: Reference number of the test result adjusted; leave "" if unknown.
    """
    match = _pick(meter_adjustment_id=meter_adjustment_id, meter_installation_id=meter_installation_id,
                  customer_id=customer_id, meter_test_id=meter_test_id)
    rows = ctx.find("meter_adjustments", **match)
    return str(rows) if rows else f"No meter adjustments for {match or 'the whole register'}."


@tool(owner="agent", rw="read")
def find_meter_charges(ctx: ToolContext, meter_charge_id: str = "", meter_installation_id: str = "", customer_id: str = "",
                       meter_test_id: str = "", meter_field_order_id: str = "") -> str:
    """Look up metering charges: repeat test fees, smart meter opt-out setup and monthly fees, and
    tampering investigation charges, with their dates and amounts.

    Args:
        meter_charge_id: Charge reference number; leave "" if unknown.
        meter_installation_id: Meter installation reference number; leave "" if unknown.
        customer_id: Customer reference number; leave "" if unknown.
        meter_test_id: Test result a fee was charged for; leave "" if unknown.
        meter_field_order_id: Field investigation a charge was made for; leave "" if unknown.
    """
    match = _pick(meter_charge_id=meter_charge_id, meter_installation_id=meter_installation_id, customer_id=customer_id,
                  meter_test_id=meter_test_id, meter_field_order_id=meter_field_order_id)
    rows = ctx.find("meter_charges", **match)
    return str(rows) if rows else f"No metering charges for {match or 'the whole register'}."


@tool(owner="agent", rw="read")
def find_meter_field_orders(ctx: ToolContext, meter_field_order_id: str = "", meter_installation_id: str = "",
                            customer_id: str = "") -> str:
    """Look up field visits to a meter: tampering or diversion investigations and visits where the meter
    could not be reached, with the date, finding and any unregistered kWh.

    Args:
        meter_field_order_id: Field order reference number; leave "" if unknown.
        meter_installation_id: Meter installation reference number; leave "" if unknown.
        customer_id: Customer reference number; leave "" if unknown.
    """
    match = _pick(meter_field_order_id=meter_field_order_id, meter_installation_id=meter_installation_id, customer_id=customer_id)
    rows = ctx.find("meter_field_orders", **match)
    return str(rows) if rows else f"No meter field orders for {match or 'the whole register'}."


# --------------------------------------------------------------------------- net energy metering
@tool(owner="agent", rw="read")
def find_nem_agreements(ctx: ToolContext, nem_agreement_id: str = "", customer_id: str = "", service_account_id: str = "") -> str:
    """Look up net metering interconnection agreements: the rider, status, application, approval and
    permission-to-operate dates, system size, generator type and battery size, the true-up month, any
    rejection reason, and the export credit currently banked.

    Args:
        nem_agreement_id: Interconnection agreement reference number; leave "" if unknown.
        customer_id: Customer reference number; leave "" if unknown.
        service_account_id: Service account number; leave "" if unknown.
    """
    match = _pick(nem_agreement_id=nem_agreement_id, customer_id=customer_id, service_account_id=service_account_id)
    rows = ctx.find("nem_agreements", **match)
    return str(rows) if rows else f"No net metering agreements for {match or 'the whole register'}."


@tool(owner="agent", rw="read")
def find_nem_ledger(ctx: ToolContext, nem_ledger_id: str = "", nem_agreement_id: str = "", customer_id: str = "",
                    service_account_id: str = "", bill_id: str = "") -> str:
    """Look up net metering history: application fees, grid access charges, monthly export credits (kWh
    exported and rates applied), credit applied to bills, and true-up payouts or forfeitures.

    Args:
        nem_ledger_id: Reference number of a history entry; leave "" if unknown.
        nem_agreement_id: Interconnection agreement reference number; leave "" if unknown.
        customer_id: Customer reference number; leave "" if unknown.
        service_account_id: Service account number; leave "" if unknown.
        bill_id: Bill reference number, to find credit applied to it; leave "" if unknown.
    """
    match = _pick(nem_ledger_id=nem_ledger_id, nem_agreement_id=nem_agreement_id, customer_id=customer_id,
                  service_account_id=service_account_id, bill_id=bill_id)
    rows = ctx.find("nem_ledger", **match)
    return str(rows) if rows else f"No net metering history for {match or 'the whole register'}."


# --------------------------------------------------------------------------- budget billing
@tool(owner="agent", rw="read")
def find_budget_plans(ctx: ToolContext, budget_plan_id: str = "", customer_id: str = "", service_account_id: str = "") -> str:
    """Look up budget billing plans: plan, status, enrollment date, current installment, FlatBill
    predicted usage and term end, next review date and the deferred balance carried.

    Args:
        budget_plan_id: Budget plan reference number; leave "" if unknown.
        customer_id: Customer reference number; leave "" if unknown.
        service_account_id: Service account number; leave "" if unknown.
    """
    match = _pick(budget_plan_id=budget_plan_id, customer_id=customer_id, service_account_id=service_account_id)
    rows = ctx.find("budget_plans", **match)
    return str(rows) if rows else f"No budget billing plans for {match or 'the whole register'}."


@tool(owner="agent", rw="read")
def find_budget_ledger(ctx: ToolContext, budget_ledger_id: str = "", budget_plan_id: str = "", customer_id: str = "",
                       service_account_id: str = "", bill_id: str = "") -> str:
    """Look up budget billing history: monthly deferrals and recoveries against each bill, settle-ups,
    FlatBill term closeouts and missed installments.

    Args:
        budget_ledger_id: Reference number of a history entry; leave "" if unknown.
        budget_plan_id: Budget plan reference number; leave "" if unknown.
        customer_id: Customer reference number; leave "" if unknown.
        service_account_id: Service account number; leave "" if unknown.
        bill_id: Bill reference number; leave "" if unknown.
    """
    match = _pick(budget_ledger_id=budget_ledger_id, budget_plan_id=budget_plan_id, customer_id=customer_id,
                  service_account_id=service_account_id, bill_id=bill_id)
    rows = ctx.find("budget_ledger", **match)
    return str(rows) if rows else f"No budget billing history for {match or 'the whole register'}."


# --------------------------------------------------------------------------- medical protections
@tool(owner="agent", rw="read")
def find_medical_certifications(ctx: ToolContext, medical_certification_id: str = "", customer_id: str = "",
                                service_account_id: str = "") -> str:
    """Look up medical and life-support protections registered on service agreements: the protection,
    status, application, certification and expiration dates, certifying practitioner's license number,
    certified device count and any denial reason.

    Args:
        medical_certification_id: Protection reference number; leave "" if unknown.
        customer_id: Customer reference number; leave "" if unknown.
        service_account_id: Service account number; leave "" if unknown.
    """
    match = _pick(medical_certification_id=medical_certification_id, customer_id=customer_id, service_account_id=service_account_id)
    rows = ctx.find("medical_certifications", **match)
    return str(rows) if rows else f"No medical protections for {match or 'the whole register'}."


@tool(owner="agent", rw="read")
def find_medical_events(ctx: ToolContext, medical_event_id: str = "", medical_certification_id: str = "",
                        customer_id: str = "", service_account_id: str = "", notice_id: str = "", bill_id: str = "") -> str:
    """Look up activity under a medical protection: disconnection postponements (with the notice
    postponed and the dates), allowances applied to bills, recertification reminders, individual outage
    notifications, and personal contact attempts made before disconnection.

    Args:
        medical_event_id: Reference number of an activity entry; leave "" if unknown.
        medical_certification_id: Protection reference number; leave "" if unknown.
        customer_id: Customer reference number; leave "" if unknown.
        service_account_id: Service account number; leave "" if unknown.
        notice_id: Disconnection notice reference number; leave "" if unknown.
        bill_id: Bill reference number; leave "" if unknown.
    """
    match = _pick(medical_event_id=medical_event_id, medical_certification_id=medical_certification_id,
                  customer_id=customer_id, service_account_id=service_account_id, notice_id=notice_id, bill_id=bill_id)
    rows = ctx.find("medical_events", **match)
    return str(rows) if rows else f"No medical protection activity for {match or 'the whole register'}."


# --------------------------------------------------------------------------- demand response
@tool(owner="agent", rw="read")
def find_dr_enrollments(ctx: ToolContext, dr_enrollment_id: str = "", customer_id: str = "", service_account_id: str = "") -> str:
    """Look up demand response program enrollments: program, status, enrollment and activation dates,
    committed kW, device serial number, any removal reason and the incentives earned but not yet paid.

    Args:
        dr_enrollment_id: Enrollment reference number; leave "" if unknown.
        customer_id: Customer reference number; leave "" if unknown.
        service_account_id: Service account number; leave "" if unknown.
    """
    match = _pick(dr_enrollment_id=dr_enrollment_id, customer_id=customer_id, service_account_id=service_account_id)
    rows = ctx.find("dr_enrollments", **match)
    return str(rows) if rows else f"No demand response enrollments for {match or 'the whole register'}."


@tool(owner="agent", rw="read")
def find_dr_ledger(ctx: ToolContext, dr_ledger_id: str = "", dr_enrollment_id: str = "", customer_id: str = "",
                   service_account_id: str = "") -> str:
    """Look up demand response history: event participation (baseline, usage, delivered kW, opt-outs),
    bonuses and incentives earned, payouts, penalties, bonus clawbacks and negative balances billed.

    Args:
        dr_ledger_id: Reference number of a history entry; leave "" if unknown.
        dr_enrollment_id: Enrollment reference number; leave "" if unknown.
        customer_id: Customer reference number; leave "" if unknown.
        service_account_id: Service account number; leave "" if unknown.
    """
    match = _pick(dr_ledger_id=dr_ledger_id, dr_enrollment_id=dr_enrollment_id, customer_id=customer_id,
                  service_account_id=service_account_id)
    rows = ctx.find("dr_ledger", **match)
    return str(rows) if rows else f"No demand response history for {match or 'the whole register'}."


# --------------------------------------------------------------------------- identity & handoff
@tool(owner="agent", rw="write")
def verify_customer_identity(ctx: ToolContext, customer_id: str, phone_number: str = "", email: str = "",
                             tax_id_last4: str = "", billing_zip: str = "") -> str:
    """Verify the caller's identity and record the outcome.

    Before discussing or changing anything on a customer's accounts, the caller must pass this check.
    The tool itself compares each detail the caller gives with the customer profile and counts how many
    match; verification passes when at least 2 details match. The customer reference number only
    locates the profile and never counts as a match. Pass only the details the caller actually stated,
    exactly as stated, and leave the others empty. The outcome is recorded; if a first attempt fails and
    a later attempt with more details passes, the customer stays verified.

    Args:
        customer_id: Customer reference number from the customer profile lookup. Required; used only to find the profile.
        phone_number: Contact phone number the caller gives, 10 digits; leave "" if not stated.
        email: Contact email address the caller gives; leave "" if not stated.
        tax_id_last4: Last four digits of the SSN (residential) or EIN (business) the caller gives; leave "" if not stated.
        billing_zip: Five-digit ZIP code of the billing address the caller gives; leave "" if not stated.
    """
    if not customer_id:
        return "Error: customer_id is required; find the customer profile first and pass its reference number."
    rows = ctx.find("customers", customer_id=customer_id)
    if not rows:
        return f"Error: no customer {customer_id}; cannot verify."
    rec = rows[0]
    supplied = {"phone_number": phone_number, "email": email, "tax_id_last4": tax_id_last4, "billing_zip": billing_zip}
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
    if verified:
        return f"Identity verified for {customer_id}."
    return (f"Identity NOT verified for {customer_id}: only {matched} of the 2 required details matched. "
            "Ask the caller for another detail on file and try again.")


@tool(owner="agent", rw="write")
def transfer_to_human_agent(ctx: ToolContext, customer_id: str, reason: str) -> str:
    """Transfer the customer to a human customer care representative and record why.

    Use POLICY_NOT_COVERED when no Lakeshore Power & Light policy lets you resolve what the customer
    needs. Use CUSTOMER_REQUESTED when the customer has explicitly asked for a human representative 2
    times.

    Args:
        customer_id: Customer reference number from the customer profile lookup (the profile must exist).
        reason: Exactly one of POLICY_NOT_COVERED or CUSTOMER_REQUESTED; never free text.
    """
    allowed = {"POLICY_NOT_COVERED", "CUSTOMER_REQUESTED"}
    if reason not in allowed:
        return f"Error: unknown transfer reason '{reason}'. Valid: {', '.join(sorted(allowed))}."
    if not ctx.find("customers", customer_id=customer_id):
        return f"Error: no customer {customer_id}; cannot record the transfer."
    rid = ctx.make_id("hof_", customer_id, reason)
    ctx.create("human_handoffs", rid, handoff_id=rid, customer_id=customer_id, reason=reason, created_at=ctx.now())
    return f"Transfer to a human representative recorded for {customer_id} ({reason})."

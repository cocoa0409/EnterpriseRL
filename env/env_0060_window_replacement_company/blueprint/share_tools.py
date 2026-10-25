"""Shared tools for env_0060_window_replacement_company (Ridgeline Window & Door).
Output of the erl-scenario-blueprint skill.

One lookup per record type (each taking every reference number that record carries, all optional),
the customer lookup doubling as the identity entry, the identity-verification write (threshold K = 2
matching credentials) and the transfer-to-human write (repeat-request threshold R = 2).
Customer-originated writes live in each difficulty's task_tools.py, never here.
"""

from erlbench import ToolContext, tool


@tool(owner="agent", rw="read")
def find_window_contracts(ctx: ToolContext, window_contract_id: str = "", customer_id: str = "") -> str:
    """Look up window replacement contracts. Each contract shows the product series, its current stage (signed, measured, ordered, installed, closed or cancelled), the contract number, signing date and sales channel, the number of openings, the signed contract price, how it is paid, any discount program, the warranty plan chosen and the key dates of measurement, order release, completion, cancellation and closing.

    Every reference number below is optional; supply whichever you already hold and every matching
    entry is returned. With none supplied, every entry is returned. When nothing matches, a short
    message says so.

    Args:
        window_contract_id: Reference number — the reference of a window replacement contract; leave "" if unknown.
        customer_id: Reference number — the customer reference number; leave "" if unknown.
    """
    match = {k: v for k, v in {"window_contract_id": window_contract_id, "customer_id": customer_id}.items() if v}
    rows = ctx.find("window_contracts", **match)
    return str(rows) if rows else f"No window contracts found for {match}."

@tool(owner="agent", rw="read")
def find_window_transactions(ctx: ToolContext, window_txn_id: str = "", window_contract_id: str = "", customer_id: str = "", source_window_txn_id: str = "", factory_order_id: str = "") -> str:
    """Look up the money and appointment history of window replacement contracts: payments received, refunds, change orders, price credits, fees, and measure appointments with their outcomes. Each entry shows its date, amount, kind and, where it applies, the payment it refunds, the factory order behind a guarantee credit or the referred contract number.

    Every reference number below is optional; supply whichever you already hold and every matching
    entry is returned. With none supplied, every entry is returned. When nothing matches, a short
    message says so.

    Args:
        window_txn_id: Reference number — the reference of one window contract payment, refund, change order, credit, fee or measure appointment; leave "" if unknown.
        window_contract_id: Reference number — the reference of a window replacement contract; leave "" if unknown.
        customer_id: Reference number — the customer reference number; leave "" if unknown.
        source_window_txn_id: Reference number — for a refund, the reference of the window contract payment it returns money from; leave "" if unknown.
        factory_order_id: Reference number — the reference of a factory production order; leave "" if unknown.
    """
    match = {k: v for k, v in {"window_txn_id": window_txn_id, "window_contract_id": window_contract_id, "customer_id": customer_id, "source_window_txn_id": source_window_txn_id, "factory_order_id": factory_order_id}.items() if v}
    rows = ctx.find("window_transactions", **match)
    return str(rows) if rows else f"No window transactions found for {match}."

@tool(owner="agent", rw="read")
def find_window_cancellation_requests(ctx: ToolContext, window_cancel_request_id: str = "", customer_id: str = "", window_contract_id: str = "") -> str:
    """Look up written notices of cancellation given on window replacement contracts, with the notice date, how the notice was given and where the request stands.

    Every reference number below is optional; supply whichever you already hold and every matching
    entry is returned. With none supplied, every entry is returned. When nothing matches, a short
    message says so.

    Args:
        window_cancel_request_id: Reference number — the reference of a window contract cancellation request; leave "" if unknown.
        customer_id: Reference number — the customer reference number; leave "" if unknown.
        window_contract_id: Reference number — the reference of a window replacement contract; leave "" if unknown.
    """
    match = {k: v for k, v in {"window_cancel_request_id": window_cancel_request_id, "customer_id": customer_id, "window_contract_id": window_contract_id}.items() if v}
    rows = ctx.find("window_cancellation_requests", **match)
    return str(rows) if rows else f"No window cancellation requests found for {match}."

@tool(owner="agent", rw="read")
def find_door_contracts(ctx: ToolContext, door_contract_id: str = "", customer_id: str = "") -> str:
    """Look up entry and patio door contracts. Each contract shows the door series, its current stage (signed, measured, ordered, installed, closed or cancelled), the contract number, signing date and sales channel, the number of door units, the signed contract price, how it is paid, any discount program, the warranty plan chosen and the key dates of measurement, order release, completion, cancellation and closing.

    Every reference number below is optional; supply whichever you already hold and every matching
    entry is returned. With none supplied, every entry is returned. When nothing matches, a short
    message says so.

    Args:
        door_contract_id: Reference number — the reference of an entry or patio door contract; leave "" if unknown.
        customer_id: Reference number — the customer reference number; leave "" if unknown.
    """
    match = {k: v for k, v in {"door_contract_id": door_contract_id, "customer_id": customer_id}.items() if v}
    rows = ctx.find("door_contracts", **match)
    return str(rows) if rows else f"No door contracts found for {match}."

@tool(owner="agent", rw="read")
def find_door_transactions(ctx: ToolContext, door_txn_id: str = "", door_contract_id: str = "", customer_id: str = "", source_door_txn_id: str = "", factory_order_id: str = "") -> str:
    """Look up the money and appointment history of door contracts: payments received, refunds, change orders, price credits, fees, and measure appointments with their outcomes. Each entry shows its date, amount, kind and, where it applies, the payment it refunds, the factory order behind a guarantee credit or the referred contract number.

    Every reference number below is optional; supply whichever you already hold and every matching
    entry is returned. With none supplied, every entry is returned. When nothing matches, a short
    message says so.

    Args:
        door_txn_id: Reference number — the reference of one door contract payment, refund, change order, credit, fee or measure appointment; leave "" if unknown.
        door_contract_id: Reference number — the reference of an entry or patio door contract; leave "" if unknown.
        customer_id: Reference number — the customer reference number; leave "" if unknown.
        source_door_txn_id: Reference number — for a refund, the reference of the door contract payment it returns money from; leave "" if unknown.
        factory_order_id: Reference number — the reference of a factory production order; leave "" if unknown.
    """
    match = {k: v for k, v in {"door_txn_id": door_txn_id, "door_contract_id": door_contract_id, "customer_id": customer_id, "source_door_txn_id": source_door_txn_id, "factory_order_id": factory_order_id}.items() if v}
    rows = ctx.find("door_transactions", **match)
    return str(rows) if rows else f"No door transactions found for {match}."

@tool(owner="agent", rw="read")
def find_door_cancellation_requests(ctx: ToolContext, door_cancel_request_id: str = "", customer_id: str = "", door_contract_id: str = "") -> str:
    """Look up written notices of cancellation given on door contracts, with the notice date, how the notice was given and where the request stands.

    Every reference number below is optional; supply whichever you already hold and every matching
    entry is returned. With none supplied, every entry is returned. When nothing matches, a short
    message says so.

    Args:
        door_cancel_request_id: Reference number — the reference of a door contract cancellation request; leave "" if unknown.
        customer_id: Reference number — the customer reference number; leave "" if unknown.
        door_contract_id: Reference number — the reference of an entry or patio door contract; leave "" if unknown.
    """
    match = {k: v for k, v in {"door_cancel_request_id": door_cancel_request_id, "customer_id": customer_id, "door_contract_id": door_contract_id}.items() if v}
    rows = ctx.find("door_cancellation_requests", **match)
    return str(rows) if rows else f"No door cancellation requests found for {match}."

@tool(owner="agent", rw="read")
def find_factory_orders(ctx: ToolContext, factory_order_id: str = "", customer_id: str = "", window_contract_id: str = "", door_contract_id: str = "") -> str:
    """Look up factory production orders. Each order shows the build class, its stage (entered, on hold, in production, shipped, delivered, closed or cancelled), the order number, the number of units, the committed and current ship dates, and the dates of entry, production start, shipment, branch delivery, hold, cancellation and closing.

    Every reference number below is optional; supply whichever you already hold and every matching
    entry is returned. With none supplied, every entry is returned. When nothing matches, a short
    message says so.

    Args:
        factory_order_id: Reference number — the reference of a factory production order; leave "" if unknown.
        customer_id: Reference number — the customer reference number; leave "" if unknown.
        window_contract_id: Reference number — the reference of a window replacement contract; leave "" if unknown.
        door_contract_id: Reference number — the reference of an entry or patio door contract; leave "" if unknown.
    """
    match = {k: v for k, v in {"factory_order_id": factory_order_id, "customer_id": customer_id, "window_contract_id": window_contract_id, "door_contract_id": door_contract_id}.items() if v}
    rows = ctx.find("factory_orders", **match)
    return str(rows) if rows else f"No factory orders found for {match}."

@tool(owner="agent", rw="read")
def find_order_milestones(ctx: ToolContext, order_milestone_id: str = "", factory_order_id: str = "", customer_id: str = "", source_order_milestone_id: str = "", window_contract_id: str = "", door_contract_id: str = "") -> str:
    """Look up the production history of factory orders: checkpoints such as the signed acknowledgment, delay notices with their cause and revised ship date, remakes with their cause, order charges and waivers, and on-time guarantee credits earned and applied.

    Every reference number below is optional; supply whichever you already hold and every matching
    entry is returned. With none supplied, every entry is returned. When nothing matches, a short
    message says so.

    Args:
        order_milestone_id: Reference number — the reference of one factory order checkpoint, delay notice, remake, charge or guarantee credit; leave "" if unknown.
        factory_order_id: Reference number — the reference of a factory production order; leave "" if unknown.
        customer_id: Reference number — the customer reference number; leave "" if unknown.
        source_order_milestone_id: Reference number — for a waiver or a credit application, the reference of the order charge or guarantee credit it concerns; leave "" if unknown.
        window_contract_id: Reference number — the reference of a window replacement contract; leave "" if unknown.
        door_contract_id: Reference number — the reference of an entry or patio door contract; leave "" if unknown.
    """
    match = {k: v for k, v in {"order_milestone_id": order_milestone_id, "factory_order_id": factory_order_id, "customer_id": customer_id, "source_order_milestone_id": source_order_milestone_id, "window_contract_id": window_contract_id, "door_contract_id": door_contract_id}.items() if v}
    rows = ctx.find("order_milestones", **match)
    return str(rows) if rows else f"No order milestones found for {match}."

@tool(owner="agent", rw="read")
def find_install_jobs(ctx: ToolContext, install_job_id: str = "", customer_id: str = "", window_contract_id: str = "", door_contract_id: str = "", factory_order_id: str = "") -> str:
    """Look up installation jobs. Each job shows the installation method, its stage (opened, scheduled, in progress, completed, closed or cancelled), the job number, the units to install, the booked crew date and crew days, whether a permit is required, and the dates the job was opened, started, completed, closed or cancelled.

    Every reference number below is optional; supply whichever you already hold and every matching
    entry is returned. With none supplied, every entry is returned. When nothing matches, a short
    message says so.

    Args:
        install_job_id: Reference number — the reference of an installation job; leave "" if unknown.
        customer_id: Reference number — the customer reference number; leave "" if unknown.
        window_contract_id: Reference number — the reference of a window replacement contract; leave "" if unknown.
        door_contract_id: Reference number — the reference of an entry or patio door contract; leave "" if unknown.
        factory_order_id: Reference number — the reference of a factory production order; leave "" if unknown.
    """
    match = {k: v for k, v in {"install_job_id": install_job_id, "customer_id": customer_id, "window_contract_id": window_contract_id, "door_contract_id": door_contract_id, "factory_order_id": factory_order_id}.items() if v}
    rows = ctx.find("install_jobs", **match)
    return str(rows) if rows else f"No install jobs found for {match}."

@tool(owner="agent", rw="read")
def find_install_activities(ctx: ToolContext, install_activity_id: str = "", install_job_id: str = "", customer_id: str = "", source_install_activity_id: str = "") -> str:
    """Look up the history of installation jobs: crew days with arrival times, reschedules with who caused them and the notice given, job charges, credits and waivers, and punch items with their resolution.

    Every reference number below is optional; supply whichever you already hold and every matching
    entry is returned. With none supplied, every entry is returned. When nothing matches, a short
    message says so.

    Args:
        install_activity_id: Reference number — the reference of one installation crew day, reschedule, charge, credit or punch item; leave "" if unknown.
        install_job_id: Reference number — the reference of an installation job; leave "" if unknown.
        customer_id: Reference number — the customer reference number; leave "" if unknown.
        source_install_activity_id: Reference number — for a waiver, credit or punch resolution, the reference of the installation charge, crew day, reschedule or punch item it concerns; leave "" if unknown.
    """
    match = {k: v for k, v in {"install_activity_id": install_activity_id, "install_job_id": install_job_id, "customer_id": customer_id, "source_install_activity_id": source_install_activity_id}.items() if v}
    rows = ctx.find("install_activities", **match)
    return str(rows) if rows else f"No install activities found for {match}."

@tool(owner="agent", rw="read")
def find_warranty_registrations(ctx: ToolContext, warranty_registration_id: str = "", customer_id: str = "", window_contract_id: str = "", door_contract_id: str = "", install_job_id: str = "") -> str:
    """Look up warranty registrations. Each registration shows the warranty plan, whether it is active, pending transfer, transferred, expired or voided, the registration number, the coverage start date every term is counted from, whether it was issued to the original purchaser or by transfer, and the transfer dates.

    Every reference number below is optional; supply whichever you already hold and every matching
    entry is returned. With none supplied, every entry is returned. When nothing matches, a short
    message says so.

    Args:
        warranty_registration_id: Reference number — the reference of a warranty registration; leave "" if unknown.
        customer_id: Reference number — the customer reference number; leave "" if unknown.
        window_contract_id: Reference number — the reference of a window replacement contract; leave "" if unknown.
        door_contract_id: Reference number — the reference of an entry or patio door contract; leave "" if unknown.
        install_job_id: Reference number — the reference of an installation job; leave "" if unknown.
    """
    match = {k: v for k, v in {"warranty_registration_id": warranty_registration_id, "customer_id": customer_id, "window_contract_id": window_contract_id, "door_contract_id": door_contract_id, "install_job_id": install_job_id}.items() if v}
    rows = ctx.find("warranty_registrations", **match)
    return str(rows) if rows else f"No warranty registrations found for {match}."

@tool(owner="agent", rw="read")
def find_warranty_claims(ctx: ToolContext, warranty_claim_id: str = "", customer_id: str = "", warranty_registration_id: str = "") -> str:
    """Look up warranty claims, with the component claimed, the date the customer first noticed the problem, the units affected, when the claim was filed and where it stands.

    Every reference number below is optional; supply whichever you already hold and every matching
    entry is returned. With none supplied, every entry is returned. When nothing matches, a short
    message says so.

    Args:
        warranty_claim_id: Reference number — the reference of a warranty claim; leave "" if unknown.
        customer_id: Reference number — the customer reference number; leave "" if unknown.
        warranty_registration_id: Reference number — the reference of a warranty registration; leave "" if unknown.
    """
    match = {k: v for k, v in {"warranty_claim_id": warranty_claim_id, "customer_id": customer_id, "warranty_registration_id": warranty_registration_id}.items() if v}
    rows = ctx.find("warranty_claims", **match)
    return str(rows) if rows else f"No warranty claims found for {match}."

@tool(owner="agent", rw="read")
def find_warranty_transfer_requests(ctx: ToolContext, warranty_transfer_request_id: str = "", customer_id: str = "", warranty_registration_id: str = "") -> str:
    """Look up requests to transfer warranty coverage to the buyer of a home, with the buyer's name and email, the home sale closing date and where the request stands.

    Every reference number below is optional; supply whichever you already hold and every matching
    entry is returned. With none supplied, every entry is returned. When nothing matches, a short
    message says so.

    Args:
        warranty_transfer_request_id: Reference number — the reference of a warranty transfer request; leave "" if unknown.
        customer_id: Reference number — the customer reference number; leave "" if unknown.
        warranty_registration_id: Reference number — the reference of a warranty registration; leave "" if unknown.
    """
    match = {k: v for k, v in {"warranty_transfer_request_id": warranty_transfer_request_id, "customer_id": customer_id, "warranty_registration_id": warranty_registration_id}.items() if v}
    rows = ctx.find("warranty_transfer_requests", **match)
    return str(rows) if rows else f"No warranty transfer requests found for {match}."

@tool(owner="agent", rw="read")
def find_warranty_activities(ctx: ToolContext, warranty_activity_id: str = "", warranty_registration_id: str = "", customer_id: str = "", warranty_claim_id: str = "", source_warranty_activity_id: str = "") -> str:
    """Look up the handling history of warranty coverage: claim decisions, parts shipments, technician visits with their outcome and hours, charges and reversals.

    Every reference number below is optional; supply whichever you already hold and every matching
    entry is returned. With none supplied, every entry is returned. When nothing matches, a short
    message says so.

    Args:
        warranty_activity_id: Reference number — the reference of one warranty decision, shipment, service visit, charge or reversal; leave "" if unknown.
        warranty_registration_id: Reference number — the reference of a warranty registration; leave "" if unknown.
        customer_id: Reference number — the customer reference number; leave "" if unknown.
        warranty_claim_id: Reference number — the reference of a warranty claim; leave "" if unknown.
        source_warranty_activity_id: Reference number — for a reversal, the reference of the warranty charge it reverses; leave "" if unknown.
    """
    match = {k: v for k, v in {"warranty_activity_id": warranty_activity_id, "warranty_registration_id": warranty_registration_id, "customer_id": customer_id, "warranty_claim_id": warranty_claim_id, "source_warranty_activity_id": source_warranty_activity_id}.items() if v}
    rows = ctx.find("warranty_activities", **match)
    return str(rows) if rows else f"No warranty activities found for {match}."

@tool(owner="agent", rw="read")
def find_finance_accounts(ctx: ToolContext, finance_account_id: str = "", customer_id: str = "", window_contract_id: str = "", door_contract_id: str = "") -> str:
    """Look up financing accounts. Each account shows the financing plan, its stage (approved, active, delinquent, paid off, cancelled or charged off), the account number, the approved and financed amounts and dates, the promotional end date, the monthly payment due day, autopay status and the closing date.

    Every reference number below is optional; supply whichever you already hold and every matching
    entry is returned. With none supplied, every entry is returned. When nothing matches, a short
    message says so.

    Args:
        finance_account_id: Reference number — the reference of a financing account; leave "" if unknown.
        customer_id: Reference number — the customer reference number; leave "" if unknown.
        window_contract_id: Reference number — the reference of a window replacement contract; leave "" if unknown.
        door_contract_id: Reference number — the reference of an entry or patio door contract; leave "" if unknown.
    """
    match = {k: v for k, v in {"finance_account_id": finance_account_id, "customer_id": customer_id, "window_contract_id": window_contract_id, "door_contract_id": door_contract_id}.items() if v}
    rows = ctx.find("finance_accounts", **match)
    return str(rows) if rows else f"No finance accounts found for {match}."

@tool(owner="agent", rw="read")
def find_finance_transactions(ctx: ToolContext, finance_txn_id: str = "", finance_account_id: str = "", customer_id: str = "", source_finance_txn_id: str = "") -> str:
    """Look up the history of financing accounts: the funding, payments with their channel and kind, interest, fees, fee reversals, returned payments, hardship deferrals and due day changes, each with its posting date, amount and statement period.

    Every reference number below is optional; supply whichever you already hold and every matching
    entry is returned. With none supplied, every entry is returned. When nothing matches, a short
    message says so.

    Args:
        finance_txn_id: Reference number — the reference of one financing transaction (funding, payment, interest, fee, return, deferral or due day change); leave "" if unknown.
        finance_account_id: Reference number — the reference of a financing account; leave "" if unknown.
        customer_id: Reference number — the customer reference number; leave "" if unknown.
        source_finance_txn_id: Reference number — the reference of the financing payment or fee a return, fee or reversal concerns; leave "" if unknown.
    """
    match = {k: v for k, v in {"finance_txn_id": finance_txn_id, "finance_account_id": finance_account_id, "customer_id": customer_id, "source_finance_txn_id": source_finance_txn_id}.items() if v}
    rows = ctx.find("finance_transactions", **match)
    return str(rows) if rows else f"No finance transactions found for {match}."

@tool(owner="agent", rw="read")
def find_finance_hardship_requests(ctx: ToolContext, finance_hardship_request_id: str = "", customer_id: str = "", finance_account_id: str = "") -> str:
    """Look up hardship requests on financing accounts, with the reason given, the months requested and where the request stands.

    Every reference number below is optional; supply whichever you already hold and every matching
    entry is returned. With none supplied, every entry is returned. When nothing matches, a short
    message says so.

    Args:
        finance_hardship_request_id: Reference number — the reference of a financing hardship request; leave "" if unknown.
        customer_id: Reference number — the customer reference number; leave "" if unknown.
        finance_account_id: Reference number — the reference of a financing account; leave "" if unknown.
    """
    match = {k: v for k, v in {"finance_hardship_request_id": finance_hardship_request_id, "customer_id": customer_id, "finance_account_id": finance_account_id}.items() if v}
    rows = ctx.find("finance_hardship_requests", **match)
    return str(rows) if rows else f"No finance hardship requests found for {match}."

@tool(owner="agent", rw="read")
def find_service_plans(ctx: ToolContext, service_plan_id: str = "", customer_id: str = "") -> str:
    """Look up service accounts and CareLine plans. Each plan shows the plan name, whether it is active, past due, cancelled or expired, the plan number, the enrolled date, the current term's start and end dates, the openings covered, whether it renews automatically, and the cancellation or end date.

    Every reference number below is optional; supply whichever you already hold and every matching
    entry is returned. With none supplied, every entry is returned. When nothing matches, a short
    message says so.

    Args:
        service_plan_id: Reference number — the reference of a service account or CareLine plan; leave "" if unknown.
        customer_id: Reference number — the customer reference number; leave "" if unknown.
    """
    match = {k: v for k, v in {"service_plan_id": service_plan_id, "customer_id": customer_id}.items() if v}
    rows = ctx.find("service_plans", **match)
    return str(rows) if rows else f"No service plans found for {match}."

@tool(owner="agent", rw="read")
def find_service_calls(ctx: ToolContext, service_call_id: str = "", service_plan_id: str = "", customer_id: str = "", source_service_call_id: str = "") -> str:
    """Look up the history of service plans: visits with their kind, outcome, openings and hours, plan fees and visit charges, and credits or refunds, each with its date and plan year.

    Every reference number below is optional; supply whichever you already hold and every matching
    entry is returned. With none supplied, every entry is returned. When nothing matches, a short
    message says so.

    Args:
        service_call_id: Reference number — the reference of one service visit, charge or credit; leave "" if unknown.
        service_plan_id: Reference number — the reference of a service account or CareLine plan; leave "" if unknown.
        customer_id: Reference number — the customer reference number; leave "" if unknown.
        source_service_call_id: Reference number — for a credit, the reference of the service charge it waives or refunds; leave "" if unknown.
    """
    match = {k: v for k, v in {"service_call_id": service_call_id, "service_plan_id": service_plan_id, "customer_id": customer_id, "source_service_call_id": source_service_call_id}.items() if v}
    rows = ctx.find("service_calls", **match)
    return str(rows) if rows else f"No service calls found for {match}."

@tool(owner="agent", rw="read")
def find_identity_verifications(ctx: ToolContext, verification_id: str = "", customer_id: str = "") -> str:
    """Look up the recorded outcome of identity verification for a customer: whether verification has passed and when it was last attempted.

    Every reference number below is optional; supply whichever you already hold and every matching
    entry is returned. With none supplied, every entry is returned. When nothing matches, a short
    message says so.

    Args:
        verification_id: Reference number — the reference of an identity verification outcome; leave "" if unknown.
        customer_id: Reference number — the customer reference number; leave "" if unknown.
    """
    match = {k: v for k, v in {"verification_id": verification_id, "customer_id": customer_id}.items() if v}
    rows = ctx.find("identity_verifications", **match)
    return str(rows) if rows else f"No identity verifications found for {match}."

@tool(owner="agent", rw="read")
def find_handoff_records(ctx: ToolContext, handoff_id: str = "", customer_id: str = "") -> str:
    """Look up handoffs of a customer to a human representative, with the reason and the moment of the handoff.

    Every reference number below is optional; supply whichever you already hold and every matching
    entry is returned. With none supplied, every entry is returned. When nothing matches, a short
    message says so.

    Args:
        handoff_id: Reference number — the reference of a handoff to a human representative; leave "" if unknown.
        customer_id: Reference number — the customer reference number; leave "" if unknown.
    """
    match = {k: v for k, v in {"handoff_id": handoff_id, "customer_id": customer_id}.items() if v}
    rows = ctx.find("handoff_records", **match)
    return str(rows) if rows else f"No handoff records found for {match}."


@tool(owner="agent", rw="read")
def find_customers(ctx: ToolContext, customer_id: str = "", name: str = "", phone_number: str = "", email: str = "") -> str:
    """Find the customer profile a call is about. Search by the customer reference number, or by what the
    caller can state: the phone number on the profile, the email on the profile, or the full name. Every
    criterion is optional — supply whichever are known. The profile shows the customer's name, phone
    number, email, service address and ZIP code, date of birth, the date the profile was opened, the year
    the home was built and whether the home is owner-occupied or rented. Finding a profile does not verify
    the caller's identity.

    Args:
        customer_id: Reference number — the customer reference number; leave "" if unknown.
        name: The customer's full name as the caller states it; leave "" if not provided.
        phone_number: The phone number on the profile, 10 digits (punctuation and spaces are ignored); leave "" if not provided.
        email: The email address on the profile; leave "" if not provided.
    """
    match = {k: v for k, v in {"customer_id": customer_id, "name": name,
                               "phone_number": phone_number, "email": email}.items() if v}
    if not match:
        return "Error: provide at least one reference number or profile detail to find the customer."
    rows = ctx.fuzzy_find("customers", **match)
    if not rows:
        return f"No customer matches {match}."
    if len(rows) > 1:
        return f"Error: {len(rows)} customers match {match}; ask the caller for one more detail to tell them apart."
    return str(rows[0])


@tool(owner="agent", rw="write")
def verify_customer_identity(ctx: ToolContext, customer_id: str, phone_number: str = "", email: str = "",
                             service_zip: str = "", date_of_birth: str = "") -> str:
    """Verify the caller's identity and record the outcome. Identity must be verified before any contract,
    order, installation, warranty, financing or service plan business is discussed or carried out for the
    customer. This tool makes the comparison itself: it checks each detail the caller states against the
    customer profile, counts the details that match, and passes only when at least 2 of them match. The
    customer reference number only identifies which profile to compare against and never counts as a
    match. Callers usually state only some details, so pass exactly the values the caller gave, as given,
    and leave the rest empty. Once a verification has passed it stays passed; a caller who fails at first
    may be verified later with more details.

    Args:
        customer_id: Reference number — the customer reference number from the customer profile lookup. Required.
        phone_number: The phone number the caller states, 10 digits; leave "" if not stated.
        email: The email address the caller states; leave "" if not stated.
        service_zip: The 5-digit ZIP code of the service address the caller states; leave "" if not stated.
        date_of_birth: The caller's date of birth as YYYY-MM-DD; leave "" if not stated.
    """
    if not customer_id:
        return "Error: customer_id is required; find the customer profile first and pass its reference number."
    rows = ctx.find("customers", customer_id=customer_id)
    if not rows:
        return f"Error: no customer {customer_id}; cannot verify."
    rec = rows[0]
    # The locator customer_id is deliberately not a credential.
    supplied = {"phone_number": phone_number, "email": email,
                "service_zip": service_zip, "date_of_birth": date_of_birth}
    matched = sum(1 for field, value in supplied.items() if value and str(rec.get(field)) == str(value))
    verified = matched >= 2
    rid = ctx.make_id("ver_", customer_id)
    # Store only the reproducible outcome; upsert and never downgrade a pass.
    prior = ctx.find("identity_verifications", verification_id=rid)
    verified = verified or bool(prior and prior[0].get("verified"))
    if prior:
        ctx.update("identity_verifications", rid, verified=verified, verified_at=ctx.now())
    else:
        ctx.create("identity_verifications", rid, verification_id=rid, customer_id=customer_id,
                   verified=verified, verified_at=ctx.now())
    return (f"Identity verified for {customer_id} ({matched} detail(s) matched)." if verified
            else f"Identity NOT verified for {customer_id} (only {matched} of the required 2 details matched). "
                 "Ask the caller for another detail on the profile and try again.")


@tool(owner="agent", rw="write")
def transfer_to_human_agent(ctx: ToolContext, customer_id: str, reason: str) -> str:
    """Hand the customer over to a human Ridgeline representative and record the handoff with its reason.
    Use it when no published policy can resolve what the customer is asking for, or when the customer has
    explicitly asked for a human representative 2 times. Choose the reason from the two values below, never
    free text.

    Args:
        customer_id: Reference number — the customer reference number from the customer profile lookup.
        reason: Why the customer is handed over; exactly one of:
            POLICY_NOT_COVERED — no published policy can resolve the customer's request;
            CUSTOMER_REQUESTED — the customer has explicitly asked for a human representative 2 times.
    """
    allowed = {"POLICY_NOT_COVERED", "CUSTOMER_REQUESTED"}
    if reason not in allowed:
        return f"Error: unknown handoff reason '{reason}'. Valid: {', '.join(sorted(allowed))}."
    if not ctx.find("customers", customer_id=customer_id):
        return f"Error: no customer {customer_id}; cannot record the handoff."
    rid = ctx.make_id("hof_", customer_id, reason)
    ctx.create("handoff_records", rid, handoff_id=rid, customer_id=customer_id,
               reason=reason, created_at=ctx.now())
    return f"Handoff to a human representative recorded for {customer_id} ({reason})."

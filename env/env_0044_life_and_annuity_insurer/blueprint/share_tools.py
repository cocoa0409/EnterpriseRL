"""Shared tools for env_0044_life_and_annuity_insurer (Ashgrove Mutual Life Insurance Company).

Living in share_tools.py makes every tool here a SHARE tool: always present in its owner's tool list.
This module holds exactly the three foundations every difficulty reuses:
  * one record finder per table (the customers finder doubles as the identity entry),
  * the identity-verification write (K = 3 matching credentials; the locator never counts),
  * the transfer-to-human write (reasons POLICY_NOT_COVERED / CUSTOMER_REQUESTED; the repeat-request threshold R = 2).
Customer-initiated writes (signing forms, consents, elections) are hidden task tools authored per difficulty.
"""

from erlbench import ToolContext, tool


@tool(owner="agent", rw="read")
def find_customers(ctx: ToolContext, customer_id: str = "", full_name: str = "", phone_number: str = "",
                   email: str = "", date_of_birth: str = "") -> str:
    """Look up a customer profile to establish whose policies or contracts this call is about.

    Search by the customer reference number, or by what a caller can naturally tell you: their full
    name, telephone number, email address or date of birth. Every criterion is optional, but at least
    one must be given; when several profiles match, ask the caller for one more detail. The profile
    returned shows the person's name, date of birth, last four digits of the Social Security number,
    telephone number, email, mailing address with ZIP code, state of residence and the date the profile
    was opened. Finding a profile only tells you who the caller claims to be; it does not verify their
    identity.

    Args:
        customer_id: The customer reference number, if already known; leave "" otherwise.
        full_name: The caller's full name as they state it; leave "" if not given.
        phone_number: The caller's telephone number, 10 digits; leave "" if not given.
        email: The caller's email address; leave "" if not given.
        date_of_birth: The caller's date of birth, YYYY-MM-DD; leave "" if not given.
    """
    match = {k: v for k, v in {"customer_id": customer_id, "full_name": full_name,
                               "phone_number": phone_number, "email": email,
                               "date_of_birth": date_of_birth}.items() if v}
    if not match:
        return "Error: provide at least one reference number or profile detail to find the customer."
    rows = ctx.fuzzy_find("customers", **match)
    if not rows:
        return f"No customer matches {match}."
    if len(rows) > 1:
        return f"Error: {len(rows)} customers match {match}; ask for one more detail to tell them apart."
    return str(rows[0])


@tool(owner="agent", rw="read")
def find_term_policies(ctx: ToolContext, term_policy_id: str = "", customer_id: str = "") -> str:
    """Look up Ashgrove term life policies — the Annual Renewable Term and the Level Term 10 to 30 plans. Each policy shows its tier, status, insured, issue date and state, face amount, rate per thousand, premium mode and installment, paid-to date, riders, any outstanding premium or acceleration lien, and lapse, reinstatement or termination dates.

    Search by any reference number you already hold; every criterion is optional and several may be
    combined. With no criterion at all, every record is returned, so narrow the search whenever you can.
    All matching records are returned in full; when nothing matches, you are told so.

    Args:
        term_policy_id: Reference number — the reference number of the term policy itself; leave "" if unknown.
        customer_id: Reference number — the customer reference number of the person the record belongs to (for policies and contracts, the owner); leave "" if unknown.
    """
    match = {k: v for k, v in {"term_policy_id": term_policy_id, "customer_id": customer_id}.items() if v}
    rows = ctx.find("term_holdings", **match)
    return str(rows) if rows else f"No matching records for {match}."


@tool(owner="agent", rw="read")
def find_term_policy_activity(ctx: ToolContext, term_txn_id: str = "", term_policy_id: str = "", customer_id: str = "", source_txn_id: str = "", term_request_id: str = "") -> str:
    """Look up the activity history of Ashgrove term life policies: premiums billed, paid, returned, waived and refunded, beneficiary designation lines, terminal illness advances and lien settlements, and death benefit payments, each with its date, amount and related details.

    Search by any reference number you already hold; every criterion is optional and several may be
    combined. With no criterion at all, every record is returned, so narrow the search whenever you can.
    All matching records are returned in full; when nothing matches, you are told so.

    Args:
        term_txn_id: Reference number — the reference number of the term activity entry itself; leave "" if unknown.
        term_policy_id: Reference number — the reference number of the related term policy; leave "" if unknown.
        customer_id: Reference number — the customer reference number of the person the record belongs to (for policies and contracts, the owner); leave "" if unknown.
        source_txn_id: Reference number — the reference number of an earlier activity entry this entry reverses, refunds, recovers or relates to; leave "" if unknown.
        term_request_id: Reference number — the reference number of the related term service request or claim; leave "" if unknown.
    """
    match = {k: v for k, v in {"term_txn_id": term_txn_id, "term_policy_id": term_policy_id, "customer_id": customer_id, "source_txn_id": source_txn_id, "term_request_id": term_request_id}.items() if v}
    rows = ctx.find("term_transactions", **match)
    return str(rows) if rows else f"No matching records for {match}."


@tool(owner="agent", rw="read")
def find_term_service_requests(ctx: ToolContext, term_request_id: str = "", term_policy_id: str = "", customer_id: str = "") -> str:
    """Look up service requests and claims filed on Ashgrove term life policies — reinstatement and conversion applications, face decreases, rider and mode changes, beneficiary changes, cancellations, free-look returns, death claims, accelerated benefit claims and waiver of premium claims — with their dates, status and supporting details.

    Search by any reference number you already hold; every criterion is optional and several may be
    combined. With no criterion at all, every record is returned, so narrow the search whenever you can.
    All matching records are returned in full; when nothing matches, you are told so.

    Args:
        term_request_id: Reference number — the reference number of the term service request or claim itself; leave "" if unknown.
        term_policy_id: Reference number — the reference number of the related term policy; leave "" if unknown.
        customer_id: Reference number — the customer reference number of the person the record belongs to (for policies and contracts, the owner); leave "" if unknown.
    """
    match = {k: v for k, v in {"term_request_id": term_request_id, "term_policy_id": term_policy_id, "customer_id": customer_id}.items() if v}
    rows = ctx.find("term_service_requests", **match)
    return str(rows) if rows else f"No matching records for {match}."


@tool(owner="agent", rw="read")
def find_identity_verifications(ctx: ToolContext, verification_id: str = "", customer_id: str = "") -> str:
    """Look up the identity verification outcome recorded for a customer: whether verification has passed and when it was last attempted.

    Search by any reference number you already hold; every criterion is optional and several may be
    combined. With no criterion at all, every record is returned, so narrow the search whenever you can.
    All matching records are returned in full; when nothing matches, you are told so.

    Args:
        verification_id: Reference number — the reference number of the verification record itself; leave "" if unknown.
        customer_id: Reference number — the customer reference number of the person the record belongs to (for policies and contracts, the owner); leave "" if unknown.
    """
    match = {k: v for k, v in {"verification_id": verification_id, "customer_id": customer_id}.items() if v}
    rows = ctx.find("verification_log", **match)
    return str(rows) if rows else f"No matching records for {match}."


@tool(owner="agent", rw="read")
def find_human_handoffs(ctx: ToolContext, handoff_id: str = "", customer_id: str = "") -> str:
    """Look up the transfers to a human representative recorded for a customer, with the reason and the time of each.

    Search by any reference number you already hold; every criterion is optional and several may be
    combined. With no criterion at all, every record is returned, so narrow the search whenever you can.
    All matching records are returned in full; when nothing matches, you are told so.

    Args:
        handoff_id: Reference number — the reference number of the handoff record itself; leave "" if unknown.
        customer_id: Reference number — the customer reference number of the person the record belongs to (for policies and contracts, the owner); leave "" if unknown.
    """
    match = {k: v for k, v in {"handoff_id": handoff_id, "customer_id": customer_id}.items() if v}
    rows = ctx.find("handoff_log", **match)
    return str(rows) if rows else f"No matching records for {match}."


@tool(owner="agent", rw="read")
def find_whole_life_policies(ctx: ToolContext, whole_policy_id: str = "", customer_id: str = "", converted_from_term_policy_id: str = "") -> str:
    """Look up Ashgrove whole life policies — Final Expense, Paid-Up at 100, Paid-Up at 65, 20-Pay, 10-Pay and Single Premium plans. Each policy shows its tier, status, insured, face amount, premium and paid-to date, dividend option, automatic premium loan election, posted cash values, paid-up additions, dividend accumulations, loan balance and interest date, cost basis, nonforfeiture option and key dates.

    Search by any reference number you already hold; every criterion is optional and several may be
    combined. With no criterion at all, every record is returned, so narrow the search whenever you can.
    All matching records are returned in full; when nothing matches, you are told so.

    Args:
        whole_policy_id: Reference number — the reference number of the whole life policy itself; leave "" if unknown.
        customer_id: Reference number — the customer reference number of the person the record belongs to (for policies and contracts, the owner); leave "" if unknown.
        converted_from_term_policy_id: Reference number — the reference number of the Ashgrove term policy that was converted into this policy; leave "" if unknown.
    """
    match = {k: v for k, v in {"whole_policy_id": whole_policy_id, "customer_id": customer_id, "converted_from_term_policy_id": converted_from_term_policy_id}.items() if v}
    rows = ctx.find("whole_holdings", **match)
    return str(rows) if rows else f"No matching records for {match}."


@tool(owner="agent", rw="read")
def find_whole_life_policy_activity(ctx: ToolContext, whole_txn_id: str = "", whole_policy_id: str = "", customer_id: str = "", source_txn_id: str = "", whole_request_id: str = "") -> str:
    """Look up the activity history of Ashgrove whole life policies: premiums, loans, loan interest, repayments and offsets, dividends and how they were applied, accumulation interest and withdrawals, paid-up additions purchases and surrenders, cash value payments, beneficiary designation lines, acceleration advances and death benefit payments.

    Search by any reference number you already hold; every criterion is optional and several may be
    combined. With no criterion at all, every record is returned, so narrow the search whenever you can.
    All matching records are returned in full; when nothing matches, you are told so.

    Args:
        whole_txn_id: Reference number — the reference number of the whole life activity entry itself; leave "" if unknown.
        whole_policy_id: Reference number — the reference number of the related whole life policy; leave "" if unknown.
        customer_id: Reference number — the customer reference number of the person the record belongs to (for policies and contracts, the owner); leave "" if unknown.
        source_txn_id: Reference number — the reference number of an earlier activity entry this entry reverses, refunds, recovers or relates to; leave "" if unknown.
        whole_request_id: Reference number — the reference number of the related whole life service request or claim; leave "" if unknown.
    """
    match = {k: v for k, v in {"whole_txn_id": whole_txn_id, "whole_policy_id": whole_policy_id, "customer_id": customer_id, "source_txn_id": source_txn_id, "whole_request_id": whole_request_id}.items() if v}
    rows = ctx.find("whole_transactions", **match)
    return str(rows) if rows else f"No matching records for {match}."


@tool(owner="agent", rw="read")
def find_whole_life_service_requests(ctx: ToolContext, whole_request_id: str = "", whole_policy_id: str = "", customer_id: str = "") -> str:
    """Look up service requests and claims filed on Ashgrove whole life policies — loans, surrenders, paid-up additions surrenders, accumulation withdrawals, dividend option and automatic premium loan changes, reduced paid-up and nonforfeiture elections, reinstatements, beneficiary and mode changes, free-look returns and claims — with their dates, status and details.

    Search by any reference number you already hold; every criterion is optional and several may be
    combined. With no criterion at all, every record is returned, so narrow the search whenever you can.
    All matching records are returned in full; when nothing matches, you are told so.

    Args:
        whole_request_id: Reference number — the reference number of the whole life service request or claim itself; leave "" if unknown.
        whole_policy_id: Reference number — the reference number of the related whole life policy; leave "" if unknown.
        customer_id: Reference number — the customer reference number of the person the record belongs to (for policies and contracts, the owner); leave "" if unknown.
    """
    match = {k: v for k, v in {"whole_request_id": whole_request_id, "whole_policy_id": whole_policy_id, "customer_id": customer_id}.items() if v}
    rows = ctx.find("whole_service_requests", **match)
    return str(rows) if rows else f"No matching records for {match}."


@tool(owner="agent", rw="read")
def find_universal_life_policies(ctx: ToolContext, ul_policy_id: str = "", customer_id: str = "", converted_from_term_policy_id: str = "") -> str:
    """Look up Ashgrove universal life policies — Lifetime Guarantee, Protection, Accumulation and the three Indexed UL plans. Each policy shows its tier, status, insured, face amounts and death benefit option, premium targets and limits, indexed allocation, account value, latest monthly deduction, loan balance, grace period details, modified endowment status and key dates.

    Search by any reference number you already hold; every criterion is optional and several may be
    combined. With no criterion at all, every record is returned, so narrow the search whenever you can.
    All matching records are returned in full; when nothing matches, you are told so.

    Args:
        ul_policy_id: Reference number — the reference number of the universal life policy itself; leave "" if unknown.
        customer_id: Reference number — the customer reference number of the person the record belongs to (for policies and contracts, the owner); leave "" if unknown.
        converted_from_term_policy_id: Reference number — the reference number of the Ashgrove term policy that was converted into this policy; leave "" if unknown.
    """
    match = {k: v for k, v in {"ul_policy_id": ul_policy_id, "customer_id": customer_id, "converted_from_term_policy_id": converted_from_term_policy_id}.items() if v}
    rows = ctx.find("ul_holdings", **match)
    return str(rows) if rows else f"No matching records for {match}."


@tool(owner="agent", rw="read")
def find_universal_life_policy_activity(ctx: ToolContext, ul_txn_id: str = "", ul_policy_id: str = "", customer_id: str = "", source_txn_id: str = "", ul_request_id: str = "") -> str:
    """Look up the activity history of Ashgrove universal life policies: premiums received and refunded, monthly deductions, interest and index credits, withdrawals, surrender charges, loans, loan interest, repayments and offsets, surrender payments, overloan protection charges, beneficiary designation lines and death benefit payments.

    Search by any reference number you already hold; every criterion is optional and several may be
    combined. With no criterion at all, every record is returned, so narrow the search whenever you can.
    All matching records are returned in full; when nothing matches, you are told so.

    Args:
        ul_txn_id: Reference number — the reference number of the universal life activity entry itself; leave "" if unknown.
        ul_policy_id: Reference number — the reference number of the related universal life policy; leave "" if unknown.
        customer_id: Reference number — the customer reference number of the person the record belongs to (for policies and contracts, the owner); leave "" if unknown.
        source_txn_id: Reference number — the reference number of an earlier activity entry this entry reverses, refunds, recovers or relates to; leave "" if unknown.
        ul_request_id: Reference number — the reference number of the related universal life service request or claim; leave "" if unknown.
    """
    match = {k: v for k, v in {"ul_txn_id": ul_txn_id, "ul_policy_id": ul_policy_id, "customer_id": customer_id, "source_txn_id": source_txn_id, "ul_request_id": ul_request_id}.items() if v}
    rows = ctx.find("ul_transactions", **match)
    return str(rows) if rows else f"No matching records for {match}."


@tool(owner="agent", rw="read")
def find_universal_life_service_requests(ctx: ToolContext, ul_request_id: str = "", ul_policy_id: str = "", customer_id: str = "") -> str:
    """Look up service requests and claims filed on Ashgrove universal life policies — withdrawals, loans, surrenders, face and death benefit option changes, planned premium and allocation changes, modified endowment consents, overloan protection elections, reinstatements, beneficiary changes, free-look returns and death claims.

    Search by any reference number you already hold; every criterion is optional and several may be
    combined. With no criterion at all, every record is returned, so narrow the search whenever you can.
    All matching records are returned in full; when nothing matches, you are told so.

    Args:
        ul_request_id: Reference number — the reference number of the universal life service request or claim itself; leave "" if unknown.
        ul_policy_id: Reference number — the reference number of the related universal life policy; leave "" if unknown.
        customer_id: Reference number — the customer reference number of the person the record belongs to (for policies and contracts, the owner); leave "" if unknown.
    """
    match = {k: v for k, v in {"ul_request_id": ul_request_id, "ul_policy_id": ul_policy_id, "customer_id": customer_id}.items() if v}
    rows = ctx.find("ul_service_requests", **match)
    return str(rows) if rows else f"No matching records for {match}."


@tool(owner="agent", rw="read")
def find_fixed_annuity_contracts(ctx: ToolContext, fixed_contract_id: str = "", customer_id: str = "") -> str:
    """Look up Ashgrove deferred fixed annuity contracts — the Flexible Premium Deferred Annuity and the SecureRate 3 to 10 guarantees. Each contract shows its tier, status, owner and annuitant, tax registration, contract value, guaranteed rate and guarantee period end, surrender charge schedule start, cost basis, waiver riders, systematic withdrawal plan, posted minimum distribution and key dates.

    Search by any reference number you already hold; every criterion is optional and several may be
    combined. With no criterion at all, every record is returned, so narrow the search whenever you can.
    All matching records are returned in full; when nothing matches, you are told so.

    Args:
        fixed_contract_id: Reference number — the reference number of the deferred fixed annuity contract itself; leave "" if unknown.
        customer_id: Reference number — the customer reference number of the person the record belongs to (for policies and contracts, the owner); leave "" if unknown.
    """
    match = {k: v for k, v in {"fixed_contract_id": fixed_contract_id, "customer_id": customer_id}.items() if v}
    rows = ctx.find("fixed_holdings", **match)
    return str(rows) if rows else f"No matching records for {match}."


@tool(owner="agent", rw="read")
def find_fixed_annuity_activity(ctx: ToolContext, fixed_txn_id: str = "", fixed_contract_id: str = "", customer_id: str = "", fixed_request_id: str = "") -> str:
    """Look up the activity history of Ashgrove deferred fixed annuities: premiums, interest credits, withdrawals, surrender charges, surrender and annuitization payouts, death benefit payments, premium returns and beneficiary designation lines.

    Search by any reference number you already hold; every criterion is optional and several may be
    combined. With no criterion at all, every record is returned, so narrow the search whenever you can.
    All matching records are returned in full; when nothing matches, you are told so.

    Args:
        fixed_txn_id: Reference number — the reference number of the deferred annuity activity entry itself; leave "" if unknown.
        fixed_contract_id: Reference number — the reference number of the related deferred fixed annuity contract; leave "" if unknown.
        customer_id: Reference number — the customer reference number of the person the record belongs to (for policies and contracts, the owner); leave "" if unknown.
        fixed_request_id: Reference number — the reference number of the related deferred annuity service request or claim; leave "" if unknown.
    """
    match = {k: v for k, v in {"fixed_txn_id": fixed_txn_id, "fixed_contract_id": fixed_contract_id, "customer_id": customer_id, "fixed_request_id": fixed_request_id}.items() if v}
    rows = ctx.find("fixed_transactions", **match)
    return str(rows) if rows else f"No matching records for {match}."


@tool(owner="agent", rw="read")
def find_fixed_annuity_service_requests(ctx: ToolContext, fixed_request_id: str = "", fixed_contract_id: str = "", customer_id: str = "") -> str:
    """Look up service requests and claims filed on Ashgrove deferred fixed annuities — withdrawals, surrenders, systematic plan changes, annuitization and renewal elections, surrender charge waiver claims, beneficiary changes, free-look returns, additional premiums, death claims and spousal continuation elections.

    Search by any reference number you already hold; every criterion is optional and several may be
    combined. With no criterion at all, every record is returned, so narrow the search whenever you can.
    All matching records are returned in full; when nothing matches, you are told so.

    Args:
        fixed_request_id: Reference number — the reference number of the deferred annuity service request or claim itself; leave "" if unknown.
        fixed_contract_id: Reference number — the reference number of the related deferred fixed annuity contract; leave "" if unknown.
        customer_id: Reference number — the customer reference number of the person the record belongs to (for policies and contracts, the owner); leave "" if unknown.
    """
    match = {k: v for k, v in {"fixed_request_id": fixed_request_id, "fixed_contract_id": fixed_contract_id, "customer_id": customer_id}.items() if v}
    rows = ctx.find("fixed_service_requests", **match)
    return str(rows) if rows else f"No matching records for {match}."


@tool(owner="agent", rw="read")
def find_income_annuity_contracts(ctx: ToolContext, income_contract_id: str = "", customer_id: str = "", source_fixed_contract_id: str = "", source_indexed_contract_id: str = "", payee_customer_id: str = "") -> str:
    """Look up Ashgrove income annuity contracts — Life Only, Cash Refund, 10- and 20-Year Certain, and Joint 50% and 100% Survivor. Each contract shows its tier, status, annuitants, purchase amount and source, payment schedule and current installment, certain period end, payment instructions and address change date, withholding election, suspension and proof-of-life details, balances held or overpaid, and the person currently receiving payments.

    Search by any reference number you already hold; every criterion is optional and several may be
    combined. With no criterion at all, every record is returned, so narrow the search whenever you can.
    All matching records are returned in full; when nothing matches, you are told so.

    Args:
        income_contract_id: Reference number — the reference number of the income annuity contract itself; leave "" if unknown.
        customer_id: Reference number — the customer reference number of the person the record belongs to (for policies and contracts, the owner); leave "" if unknown.
        source_fixed_contract_id: Reference number — the reference number of the Ashgrove deferred fixed annuity that was annuitized into this contract; leave "" if unknown.
        source_indexed_contract_id: Reference number — the reference number of the Ashgrove fixed indexed annuity that was annuitized into this contract; leave "" if unknown.
        payee_customer_id: Reference number — the customer reference number of the survivor or beneficiary now receiving the payments; leave "" if unknown.
    """
    match = {k: v for k, v in {"income_contract_id": income_contract_id, "customer_id": customer_id, "source_fixed_contract_id": source_fixed_contract_id, "source_indexed_contract_id": source_indexed_contract_id, "payee_customer_id": payee_customer_id}.items() if v}
    rows = ctx.find("income_holdings", **match)
    return str(rows) if rows else f"No matching records for {match}."


@tool(owner="agent", rw="read")
def find_income_annuity_activity(ctx: ToolContext, income_txn_id: str = "", income_contract_id: str = "", customer_id: str = "", source_txn_id: str = "", income_request_id: str = "") -> str:
    """Look up the activity history of Ashgrove income annuities: purchase payments, installments issued, returned, held and released, overpayments and their recovery, cash refund and commuted value payments, purchase refunds and beneficiary designation lines.

    Search by any reference number you already hold; every criterion is optional and several may be
    combined. With no criterion at all, every record is returned, so narrow the search whenever you can.
    All matching records are returned in full; when nothing matches, you are told so.

    Args:
        income_txn_id: Reference number — the reference number of the income annuity activity entry itself; leave "" if unknown.
        income_contract_id: Reference number — the reference number of the related income annuity contract; leave "" if unknown.
        customer_id: Reference number — the customer reference number of the person the record belongs to (for policies and contracts, the owner); leave "" if unknown.
        source_txn_id: Reference number — the reference number of an earlier activity entry this entry reverses, refunds, recovers or relates to; leave "" if unknown.
        income_request_id: Reference number — the reference number of the related income annuity service request or claim; leave "" if unknown.
    """
    match = {k: v for k, v in {"income_txn_id": income_txn_id, "income_contract_id": income_contract_id, "customer_id": customer_id, "source_txn_id": source_txn_id, "income_request_id": income_request_id}.items() if v}
    rows = ctx.find("income_transactions", **match)
    return str(rows) if rows else f"No matching records for {match}."


@tool(owner="agent", rw="read")
def find_income_annuity_service_requests(ctx: ToolContext, income_request_id: str = "", income_contract_id: str = "", customer_id: str = "") -> str:
    """Look up service requests and claims filed on Ashgrove income annuities — bank and address changes, withholding elections, certificates of existence, beneficiary changes, free-look returns, death reports and claims, commutation elections and overpayment repayments — with their dates, status and details.

    Search by any reference number you already hold; every criterion is optional and several may be
    combined. With no criterion at all, every record is returned, so narrow the search whenever you can.
    All matching records are returned in full; when nothing matches, you are told so.

    Args:
        income_request_id: Reference number — the reference number of the income annuity service request or claim itself; leave "" if unknown.
        income_contract_id: Reference number — the reference number of the related income annuity contract; leave "" if unknown.
        customer_id: Reference number — the customer reference number of the person the record belongs to (for policies and contracts, the owner); leave "" if unknown.
    """
    match = {k: v for k, v in {"income_request_id": income_request_id, "income_contract_id": income_contract_id, "customer_id": customer_id}.items() if v}
    rows = ctx.find("income_service_requests", **match)
    return str(rows) if rows else f"No matching records for {match}."


@tool(owner="agent", rw="read")
def find_indexed_annuity_contracts(ctx: ToolContext, indexed_contract_id: str = "", customer_id: str = "") -> str:
    """Look up Ashgrove fixed indexed annuity contracts — the IndexEdge and IncomeShield plans. Each contract shows its tier, status, owner and annuitant, tax registration, contract value, lifetime withdrawal benefit base, strategy allocation, current crediting rates and next anniversary, lifetime income details, posted minimum distribution and key dates.

    Search by any reference number you already hold; every criterion is optional and several may be
    combined. With no criterion at all, every record is returned, so narrow the search whenever you can.
    All matching records are returned in full; when nothing matches, you are told so.

    Args:
        indexed_contract_id: Reference number — the reference number of the fixed indexed annuity contract itself; leave "" if unknown.
        customer_id: Reference number — the customer reference number of the person the record belongs to (for policies and contracts, the owner); leave "" if unknown.
    """
    match = {k: v for k, v in {"indexed_contract_id": indexed_contract_id, "customer_id": customer_id}.items() if v}
    rows = ctx.find("indexed_holdings", **match)
    return str(rows) if rows else f"No matching records for {match}."


@tool(owner="agent", rw="read")
def find_indexed_annuity_activity(ctx: ToolContext, indexed_txn_id: str = "", indexed_contract_id: str = "", customer_id: str = "", source_txn_id: str = "", indexed_request_id: str = "") -> str:
    """Look up the activity history of Ashgrove fixed indexed annuities: premiums and bonuses, fixed and index credits, withdrawals and guaranteed lifetime payments, rider fees, surrender charges and bonus recaptures, payouts, benefit base changes and beneficiary designation lines.

    Search by any reference number you already hold; every criterion is optional and several may be
    combined. With no criterion at all, every record is returned, so narrow the search whenever you can.
    All matching records are returned in full; when nothing matches, you are told so.

    Args:
        indexed_txn_id: Reference number — the reference number of the indexed annuity activity entry itself; leave "" if unknown.
        indexed_contract_id: Reference number — the reference number of the related fixed indexed annuity contract; leave "" if unknown.
        customer_id: Reference number — the customer reference number of the person the record belongs to (for policies and contracts, the owner); leave "" if unknown.
        source_txn_id: Reference number — the reference number of an earlier activity entry this entry reverses, refunds, recovers or relates to; leave "" if unknown.
        indexed_request_id: Reference number — the reference number of the related indexed annuity service request or claim; leave "" if unknown.
    """
    match = {k: v for k, v in {"indexed_txn_id": indexed_txn_id, "indexed_contract_id": indexed_contract_id, "customer_id": customer_id, "source_txn_id": source_txn_id, "indexed_request_id": indexed_request_id}.items() if v}
    rows = ctx.find("indexed_transactions", **match)
    return str(rows) if rows else f"No matching records for {match}."


@tool(owner="agent", rw="read")
def find_indexed_annuity_service_requests(ctx: ToolContext, indexed_request_id: str = "", indexed_contract_id: str = "", customer_id: str = "") -> str:
    """Look up service requests and claims filed on Ashgrove fixed indexed annuities — withdrawals, surrenders, reallocations, lifetime income and annuitization elections, waiver claims, beneficiary changes, free-look returns, additional premiums, death claims and spousal continuation elections.

    Search by any reference number you already hold; every criterion is optional and several may be
    combined. With no criterion at all, every record is returned, so narrow the search whenever you can.
    All matching records are returned in full; when nothing matches, you are told so.

    Args:
        indexed_request_id: Reference number — the reference number of the indexed annuity service request or claim itself; leave "" if unknown.
        indexed_contract_id: Reference number — the reference number of the related fixed indexed annuity contract; leave "" if unknown.
        customer_id: Reference number — the customer reference number of the person the record belongs to (for policies and contracts, the owner); leave "" if unknown.
    """
    match = {k: v for k, v in {"indexed_request_id": indexed_request_id, "indexed_contract_id": indexed_contract_id, "customer_id": customer_id}.items() if v}
    rows = ctx.find("indexed_service_requests", **match)
    return str(rows) if rows else f"No matching records for {match}."


@tool(owner="agent", rw="read")
def find_careassure_policies(ctx: ToolContext, ltc_policy_id: str = "", customer_id: str = "") -> str:
    """Look up Ashgrove CareAssure long-term care life policies. Each policy shows its tier, status, insured, specified amount and monthly maximum benefit, inflation and premium options, premium and paid-to date, remaining benefit pool, claim eligibility and elimination dates, lapse-notice designee and key dates.

    Search by any reference number you already hold; every criterion is optional and several may be
    combined. With no criterion at all, every record is returned, so narrow the search whenever you can.
    All matching records are returned in full; when nothing matches, you are told so.

    Args:
        ltc_policy_id: Reference number — the reference number of the CareAssure policy itself; leave "" if unknown.
        customer_id: Reference number — the customer reference number of the person the record belongs to (for policies and contracts, the owner); leave "" if unknown.
    """
    match = {k: v for k, v in {"ltc_policy_id": ltc_policy_id, "customer_id": customer_id}.items() if v}
    rows = ctx.find("ltc_holdings", **match)
    return str(rows) if rows else f"No matching records for {match}."


@tool(owner="agent", rw="read")
def find_careassure_policy_activity(ctx: ToolContext, ltc_txn_id: str = "", ltc_policy_id: str = "", customer_id: str = "", ltc_request_id: str = "") -> str:
    """Look up the activity history of Ashgrove CareAssure policies: premiums billed, paid, waived and refunded, the benefit pool and its inflation increases, long-term care and continuation benefits paid by month and care setting, surrender and death benefit payments and beneficiary designation lines.

    Search by any reference number you already hold; every criterion is optional and several may be
    combined. With no criterion at all, every record is returned, so narrow the search whenever you can.
    All matching records are returned in full; when nothing matches, you are told so.

    Args:
        ltc_txn_id: Reference number — the reference number of the CareAssure activity entry itself; leave "" if unknown.
        ltc_policy_id: Reference number — the reference number of the related CareAssure policy; leave "" if unknown.
        customer_id: Reference number — the customer reference number of the person the record belongs to (for policies and contracts, the owner); leave "" if unknown.
        ltc_request_id: Reference number — the reference number of the related CareAssure service request or claim; leave "" if unknown.
    """
    match = {k: v for k, v in {"ltc_txn_id": ltc_txn_id, "ltc_policy_id": ltc_policy_id, "customer_id": customer_id, "ltc_request_id": ltc_request_id}.items() if v}
    rows = ctx.find("ltc_transactions", **match)
    return str(rows) if rows else f"No matching records for {match}."


@tool(owner="agent", rw="read")
def find_careassure_service_requests(ctx: ToolContext, ltc_request_id: str = "", ltc_policy_id: str = "", customer_id: str = "") -> str:
    """Look up service requests and claims filed on Ashgrove CareAssure policies — long-term care claims, recertifications and expense submissions, surrenders, beneficiary and lapse-notice designee changes, mode changes, free-look returns, reinstatements and death claims.

    Search by any reference number you already hold; every criterion is optional and several may be
    combined. With no criterion at all, every record is returned, so narrow the search whenever you can.
    All matching records are returned in full; when nothing matches, you are told so.

    Args:
        ltc_request_id: Reference number — the reference number of the CareAssure service request or claim itself; leave "" if unknown.
        ltc_policy_id: Reference number — the reference number of the related CareAssure policy; leave "" if unknown.
        customer_id: Reference number — the customer reference number of the person the record belongs to (for policies and contracts, the owner); leave "" if unknown.
    """
    match = {k: v for k, v in {"ltc_request_id": ltc_request_id, "ltc_policy_id": ltc_policy_id, "customer_id": customer_id}.items() if v}
    rows = ctx.find("ltc_service_requests", **match)
    return str(rows) if rows else f"No matching records for {match}."


@tool(owner="agent", rw="write")
def verify_customer_identity(ctx: ToolContext, customer_id: str, date_of_birth: str = "", ssn_last4: str = "",
                             phone_number: str = "", email: str = "", zip_code: str = "") -> str:
    """Verify the caller's identity against the customer profile and record the outcome.

    Identity must be verified before any policy or contract information is discussed in detail and
    before any transaction is carried out. This tool makes the comparison itself: it checks each
    detail the caller gives against the profile on file, counts how many agree, and verification
    passes only when at least 3 details match. The customer reference number is used only to open the
    profile and never counts as a match. Callers usually know only some of these details, so pass
    exactly what the caller said, unchanged, and leave the rest empty. The outcome is recorded; if a
    first attempt falls short and a later attempt with more details passes, the pass stands.

    Args:
        customer_id: The customer reference number read from the customer profile lookup. Required; used only to open the profile.
        date_of_birth: The caller's date of birth as stated, YYYY-MM-DD; leave "" if not given.
        ssn_last4: The last four digits of the caller's Social Security number as stated; leave "" if not given.
        phone_number: The telephone number on file as stated by the caller, 10 digits; leave "" if not given.
        email: The email address on file as stated by the caller; leave "" if not given.
        zip_code: The ZIP code of the mailing address on file as stated by the caller, 5 digits; leave "" if not given.
    """
    if not customer_id:
        return "Error: customer_id is required; look up the customer profile first and pass its reference number."
    rows = ctx.find("customers", customer_id=customer_id)
    if not rows:
        return f"Error: no customer {customer_id}; cannot verify."
    rec = rows[0]
    # The tool owns the comparison; the locator customer_id is deliberately not a credential.
    supplied = {"date_of_birth": date_of_birth, "ssn_last4": ssn_last4, "phone_number": phone_number,
                "email": email, "zip_code": zip_code}
    matched = sum(1 for field, value in supplied.items()
                  if value and str(rec.get(field)).strip().lower() == str(value).strip().lower())
    verified = matched >= 3
    rid = ctx.make_id("ver_", customer_id)
    # Store only the reproducible boolean; upsert and never downgrade a prior pass.
    prior = ctx.find("verification_log", verification_id=rid)
    verified = verified or bool(prior and prior[0].get("verified"))
    if prior:
        ctx.update("verification_log", rid, verified=verified, verified_at=ctx.now())
    else:
        ctx.create("verification_log", rid, verification_id=rid, customer_id=customer_id,
                   verified=verified, verified_at=ctx.now())
    return (f"Identity verified for {customer_id} ({matched} detail(s) matched)." if verified
            else f"Identity NOT verified for {customer_id}: only {matched} of the required 3 details matched. "
                 "Ask the caller for another detail on file and try again.")


@tool(owner="agent", rw="write")
def transfer_to_human_agent(ctx: ToolContext, customer_id: str, reason: str) -> str:
    """Transfer the caller to a human representative and record the transfer and its reason.

    Use this in exactly two situations. When no Ashgrove policy rule provides a way to resolve what the
    caller is asking for, transfer with reason POLICY_NOT_COVERED. When the caller has explicitly asked
    to speak with a human representative at least 2 times during the call, transfer with reason
    CUSTOMER_REQUESTED.

    Args:
        customer_id: The customer reference number read from the customer profile lookup; the profile must exist.
        reason: Exactly one of POLICY_NOT_COVERED or CUSTOMER_REQUESTED, never free text.
            POLICY_NOT_COVERED — no policy rule can resolve the request;
            CUSTOMER_REQUESTED — the caller has asked for a human representative at least 2 times.
    """
    allowed = {"POLICY_NOT_COVERED", "CUSTOMER_REQUESTED"}
    if reason not in allowed:
        return f"Error: unknown transfer reason '{reason}'. Valid: {', '.join(sorted(allowed))}."
    if not ctx.find("customers", customer_id=customer_id):
        return f"Error: no customer {customer_id}; cannot record the transfer."
    rid = ctx.make_id("hof_", customer_id, reason)
    ctx.create("handoff_log", rid, handoff_id=rid, customer_id=customer_id,
               reason=reason, created_at=ctx.now())
    return f"Transfer to a human representative recorded for {customer_id} ({reason})."

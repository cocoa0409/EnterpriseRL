"""Shared tools for env_0046_home_improvement_retailer (Ridgeline Home Center Customer Care).
Output of the erl-scenario-blueprint skill.

Every tool here is a SHARE tool: always present in its owner's tool list.  This file holds exactly the
three foundations every difficulty reuses:
  - one record finder per table in db_schema.json (all `_id` fields optional), the customers finder
    doubling as the identity entry (phone, email, name, business name);
  - the identity-verification write (compares the stated credentials itself; K = 2 matches);
  - the transfer-to-human write (closed reason set; CUSTOMER_REQUESTED after R = 2 explicit asks).
Customer-originated writes and every business action live in each difficulty's task_tools.py.
"""

from erlbench import ToolContext, tool


@tool(owner="agent", rw="read")
def find_identity_verifications(ctx: ToolContext, verification_id: str = "", customer_id: str = "") -> str:
    """Look up the record of a customer's identity check: whether the caller has been verified for this profile and when the latest check took place.

    Supply any reference number you already hold — every criterion is optional, and records matching all
    of the numbers given are returned. With no criterion at all, every record of this kind is returned.
    When nothing matches, a short notice says so.

    Args:
        verification_id: The reference number of the identity check record itself; leave "" if unknown.
        customer_id: The customer reference number of the profile the records belong to; leave "" if unknown.
    """
    match = {k: v for k, v in {"verification_id": verification_id, "customer_id": customer_id}.items() if v}
    rows = ctx.find("identity_verifications", **match)
    return str(rows) if rows else f"No identity_verifications records for {match}."

@tool(owner="agent", rw="read")
def find_human_handoffs(ctx: ToolContext, handoff_id: str = "", customer_id: str = "") -> str:
    """Look up transfers of a customer to a human representative, with the reason recorded and the moment of the transfer.

    Supply any reference number you already hold — every criterion is optional, and records matching all
    of the numbers given are returned. With no criterion at all, every record of this kind is returned.
    When nothing matches, a short notice says so.

    Args:
        handoff_id: The reference number of the transfer record itself; leave "" if unknown.
        customer_id: The customer reference number of the profile the records belong to; leave "" if unknown.
    """
    match = {k: v for k, v in {"handoff_id": handoff_id, "customer_id": customer_id}.items() if v}
    rows = ctx.find("human_handoffs", **match)
    return str(rows) if rows else f"No human_handoffs records for {match}."

@tool(owner="agent", rw="read")
def find_card_accounts(ctx: ToolContext, card_account_id: str = "", customer_id: str = "") -> str:
    """Look up Ridgeline Consumer Credit accounts — the Consumer Credit Card (Classic, Preferred, Premier) and the Project Loan (66, 78, 84). Each account shows its tier, status, application and opening dates, credit line or loan amount and the date it last changed, current balance, last four digits, statement closing day, autopay settings, Project Loan draw period end date and number of authorized users.

    Supply any reference number you already hold — every criterion is optional, and records matching all
    of the numbers given are returned. With no criterion at all, every record of this kind is returned.
    When nothing matches, a short notice says so.

    Args:
        card_account_id: The reference number of a Ridgeline Consumer Credit account (revolving card or Project Loan); leave "" if unknown.
        customer_id: The customer reference number of the profile the records belong to; leave "" if unknown.
    """
    match = {k: v for k, v in {"card_account_id": card_account_id, "customer_id": customer_id}.items() if v}
    rows = ctx.find("card_accounts", **match)
    return str(rows) if rows else f"No card_accounts records for {match}."

@tool(owner="agent", rw="read")
def find_card_transactions(ctx: ToolContext, card_transaction_id: str = "", card_account_id: str = "", customer_id: str = "", original_transaction_id: str = "", card_request_id: str = "") -> str:
    """Look up the activity on Ridgeline Consumer Credit accounts: monthly statements (balance, minimum payment, due date, past-due amount, days past due), purchases and loan draws with their financing plan and promotion end date, payments with channel and bank account last four, returned payments, fees, interest, return credits, fee reversals, courtesy waivers, dispute credits and credit balance refunds.

    Supply any reference number you already hold — every criterion is optional, and records matching all
    of the numbers given are returned. With no criterion at all, every record of this kind is returned.
    When nothing matches, a short notice says so.

    Args:
        card_transaction_id: The reference number of one account activity line (statement, purchase, payment, fee, interest or credit); leave "" if unknown.
        card_account_id: The reference number of a Ridgeline Consumer Credit account (revolving card or Project Loan); leave "" if unknown.
        customer_id: The customer reference number of the profile the records belong to; leave "" if unknown.
        original_transaction_id: The reference number of the earlier activity line this line arises from or corrects (for example the payment that was returned or the fee that was reversed); leave "" if unknown.
        card_request_id: The reference number of a consumer credit service request (billing dispute, closure, credit line increase); leave "" if unknown.
    """
    match = {k: v for k, v in {"card_transaction_id": card_transaction_id, "card_account_id": card_account_id, "customer_id": customer_id, "original_transaction_id": original_transaction_id, "card_request_id": card_request_id}.items() if v}
    rows = ctx.find("card_transactions", **match)
    return str(rows) if rows else f"No card_transactions records for {match}."

@tool(owner="agent", rw="read")
def find_card_requests(ctx: ToolContext, card_request_id: str = "", customer_id: str = "", card_account_id: str = "", disputed_transaction_id: str = "") -> str:
    """Look up consumer credit service requests — billing disputes, account closures and credit line increase requests — with the amount disputed or requested, status, filing moment and resolution date.

    Supply any reference number you already hold — every criterion is optional, and records matching all
    of the numbers given are returned. With no criterion at all, every record of this kind is returned.
    When nothing matches, a short notice says so.

    Args:
        card_request_id: The reference number of a consumer credit service request (billing dispute, closure, credit line increase); leave "" if unknown.
        customer_id: The customer reference number of the profile the records belong to; leave "" if unknown.
        card_account_id: The reference number of a Ridgeline Consumer Credit account (revolving card or Project Loan); leave "" if unknown.
        disputed_transaction_id: The reference number of the activity line being disputed; leave "" if unknown.
    """
    match = {k: v for k, v in {"card_request_id": card_request_id, "customer_id": customer_id, "card_account_id": card_account_id, "disputed_transaction_id": disputed_transaction_id}.items() if v}
    rows = ctx.find("card_requests", **match)
    return str(rows) if rows else f"No card_requests records for {match}."

@tool(owner="agent", rw="read")
def find_trade_accounts(ctx: ToolContext, trade_account_id: str = "", customer_id: str = "") -> str:
    """Look up Ridgeline Pro Credit accounts — Pro Revolving Charge and Commercial Account tiers. Each account shows its tier, status and hold reason, application and opening dates, credit line and the date it last changed, current balance, purchase order requirement, number of authorized buyers, tax exemption certificate on file with its effective and expiry dates, and whether a personal guarantee is on file.

    Supply any reference number you already hold — every criterion is optional, and records matching all
    of the numbers given are returned. With no criterion at all, every record of this kind is returned.
    When nothing matches, a short notice says so.

    Args:
        trade_account_id: The reference number of a Ridgeline Pro Credit account; leave "" if unknown.
        customer_id: The customer reference number of the profile the records belong to; leave "" if unknown.
    """
    match = {k: v for k, v in {"trade_account_id": trade_account_id, "customer_id": customer_id}.items() if v}
    rows = ctx.find("trade_accounts", **match)
    return str(rows) if rows else f"No trade_accounts records for {match}."

@tool(owner="agent", rw="read")
def find_trade_transactions(ctx: ToolContext, trade_transaction_id: str = "", trade_account_id: str = "", customer_id: str = "", pro_quote_id: str = "", original_transaction_id: str = "", trade_request_id: str = "") -> str:
    """Look up the activity on Ridgeline Pro Credit accounts: statements, invoices (invoice number and date, due date, merchandise and sales tax amounts, job name, purchase order number, pricing basis and quote applied), payments and the invoice each part was applied to, returned payments, fees and late payment charges, interest, prompt-payment discounts, tax credits, return credits, waivers, corrections, dispute credits and credit balance refunds.

    Supply any reference number you already hold — every criterion is optional, and records matching all
    of the numbers given are returned. With no criterion at all, every record of this kind is returned.
    When nothing matches, a short notice says so.

    Args:
        trade_transaction_id: The reference number of one Pro Credit activity line (statement, invoice, payment, fee or credit); leave "" if unknown.
        trade_account_id: The reference number of a Ridgeline Pro Credit account; leave "" if unknown.
        customer_id: The customer reference number of the profile the records belong to; leave "" if unknown.
        pro_quote_id: The reference number of a ProBuild volume pricing quote; leave "" if unknown.
        original_transaction_id: The reference number of the earlier activity line this line arises from or corrects (for example the payment that was returned or the fee that was reversed); leave "" if unknown.
        trade_request_id: The reference number of a Pro Credit service request (invoice dispute, closure, credit line increase); leave "" if unknown.
    """
    match = {k: v for k, v in {"trade_transaction_id": trade_transaction_id, "trade_account_id": trade_account_id, "customer_id": customer_id, "pro_quote_id": pro_quote_id, "original_transaction_id": original_transaction_id, "trade_request_id": trade_request_id}.items() if v}
    rows = ctx.find("trade_transactions", **match)
    return str(rows) if rows else f"No trade_transactions records for {match}."

@tool(owner="agent", rw="read")
def find_trade_requests(ctx: ToolContext, trade_request_id: str = "", customer_id: str = "", trade_account_id: str = "", disputed_transaction_id: str = "") -> str:
    """Look up Pro Credit service requests — invoice disputes, account closures and credit line increase requests — with the disputed or requested amount, dispute category, status, filing moment and resolution date.

    Supply any reference number you already hold — every criterion is optional, and records matching all
    of the numbers given are returned. With no criterion at all, every record of this kind is returned.
    When nothing matches, a short notice says so.

    Args:
        trade_request_id: The reference number of a Pro Credit service request (invoice dispute, closure, credit line increase); leave "" if unknown.
        customer_id: The customer reference number of the profile the records belong to; leave "" if unknown.
        trade_account_id: The reference number of a Ridgeline Pro Credit account; leave "" if unknown.
        disputed_transaction_id: The reference number of the activity line being disputed; leave "" if unknown.
    """
    match = {k: v for k, v in {"trade_request_id": trade_request_id, "customer_id": customer_id, "trade_account_id": trade_account_id, "disputed_transaction_id": disputed_transaction_id}.items() if v}
    rows = ctx.find("trade_requests", **match)
    return str(rows) if rows else f"No trade_requests records for {match}."

@tool(owner="agent", rw="read")
def find_install_contracts(ctx: ToolContext, install_contract_id: str = "", customer_id: str = "", linked_special_order_id: str = "") -> str:
    """Look up installation contracts from the measure booking through completion: program, status, contract number, job address, measure appointment and completion, quote amount and expiry, signing date and channel, contract price, materials and permit status, original and current installation dates, reschedule count, completion and sign-off, cancellation details, balance due and any linked special order.

    Supply any reference number you already hold — every criterion is optional, and records matching all
    of the numbers given are returned. With no criterion at all, every record of this kind is returned.
    When nothing matches, a short notice says so.

    Args:
        install_contract_id: The reference number of an installation contract; leave "" if unknown.
        customer_id: The customer reference number of the profile the records belong to; leave "" if unknown.
        linked_special_order_id: The reference number of the special order supplying the job's materials; leave "" if unknown.
    """
    match = {k: v for k, v in {"install_contract_id": install_contract_id, "customer_id": customer_id, "linked_special_order_id": linked_special_order_id}.items() if v}
    rows = ctx.find("install_contracts", **match)
    return str(rows) if rows else f"No install_contracts records for {match}."

@tool(owner="agent", rw="read")
def find_install_charges(ctx: ToolContext, install_charge_id: str = "", install_contract_id: str = "", customer_id: str = "", original_charge_id: str = "", install_request_id: str = "") -> str:
    """Look up the lines of installation contracts: measure fees, contract billing, change orders, fees, payments with tender and purpose, credits, refunds, and the installer's recorded visits with their outcome and warranty status.

    Supply any reference number you already hold — every criterion is optional, and records matching all
    of the numbers given are returned. With no criterion at all, every record of this kind is returned.
    When nothing matches, a short notice says so.

    Args:
        install_charge_id: The reference number of one installation contract line (charge, payment, credit, refund or visit record); leave "" if unknown.
        install_contract_id: The reference number of an installation contract; leave "" if unknown.
        customer_id: The customer reference number of the profile the records belong to; leave "" if unknown.
        original_charge_id: The reference number of the earlier line this line arises from (for example the payment that was refunded); leave "" if unknown.
        install_request_id: The reference number of an installation service request (cancellation, reschedule, change order, workmanship claim, quote extension); leave "" if unknown.
    """
    match = {k: v for k, v in {"install_charge_id": install_charge_id, "install_contract_id": install_contract_id, "customer_id": customer_id, "original_charge_id": original_charge_id, "install_request_id": install_request_id}.items() if v}
    rows = ctx.find("install_charges", **match)
    return str(rows) if rows else f"No install_charges records for {match}."

@tool(owner="agent", rw="read")
def find_install_requests(ctx: ToolContext, install_request_id: str = "", customer_id: str = "", install_contract_id: str = "") -> str:
    """Look up installation service requests — cancellations, reschedules, change orders, workmanship claims and quote extensions — with the requested date or change order amount, cancellation basis, status, filing moment and resolution date.

    Supply any reference number you already hold — every criterion is optional, and records matching all
    of the numbers given are returned. With no criterion at all, every record of this kind is returned.
    When nothing matches, a short notice says so.

    Args:
        install_request_id: The reference number of an installation service request (cancellation, reschedule, change order, workmanship claim, quote extension); leave "" if unknown.
        customer_id: The customer reference number of the profile the records belong to; leave "" if unknown.
        install_contract_id: The reference number of an installation contract; leave "" if unknown.
    """
    match = {k: v for k, v in {"install_request_id": install_request_id, "customer_id": customer_id, "install_contract_id": install_contract_id}.items() if v}
    rows = ctx.find("install_requests", **match)
    return str(rows) if rows else f"No install_requests records for {match}."

@tool(owner="agent", rw="read")
def find_rental_agreements(ctx: ToolContext, rental_agreement_id: str = "", customer_id: str = "") -> str:
    """Look up tool rental agreements: equipment class, status, agreement number, rental center, equipment and asset tag, daily rate and replacement value, pickup, checkout, due-back and return times, damage protection and insurance certificate, deposit, delivery, fuel and hour meter readings, balance due and deposit held.

    Supply any reference number you already hold — every criterion is optional, and records matching all
    of the numbers given are returned. With no criterion at all, every record of this kind is returned.
    When nothing matches, a short notice says so.

    Args:
        rental_agreement_id: The reference number of a tool rental agreement; leave "" if unknown.
        customer_id: The customer reference number of the profile the records belong to; leave "" if unknown.
    """
    match = {k: v for k, v in {"rental_agreement_id": rental_agreement_id, "customer_id": customer_id}.items() if v}
    rows = ctx.find("rental_agreements", **match)
    return str(rows) if rows else f"No rental_agreements records for {match}."

@tool(owner="agent", rw="read")
def find_rental_charges(ctx: ToolContext, rental_charge_id: str = "", rental_agreement_id: str = "", customer_id: str = "", original_charge_id: str = "", rental_request_id: str = "") -> str:
    """Look up the lines of tool rental agreements: rental time by rate period, damage protection, fees, return inspections with their findings, ProBuild discounts, malfunction credits, charge adjustments, payments, deposits collected, applied or released, and refunds.

    Supply any reference number you already hold — every criterion is optional, and records matching all
    of the numbers given are returned. With no criterion at all, every record of this kind is returned.
    When nothing matches, a short notice says so.

    Args:
        rental_charge_id: The reference number of one rental agreement line (rental time, fee, deposit, payment, credit, refund or inspection); leave "" if unknown.
        rental_agreement_id: The reference number of a tool rental agreement; leave "" if unknown.
        customer_id: The customer reference number of the profile the records belong to; leave "" if unknown.
        original_charge_id: The reference number of the earlier line this line arises from (for example the payment that was refunded); leave "" if unknown.
        rental_request_id: The reference number of a rental service request (extension, cancellation, malfunction report, damage dispute); leave "" if unknown.
    """
    match = {k: v for k, v in {"rental_charge_id": rental_charge_id, "rental_agreement_id": rental_agreement_id, "customer_id": customer_id, "original_charge_id": original_charge_id, "rental_request_id": rental_request_id}.items() if v}
    rows = ctx.find("rental_charges", **match)
    return str(rows) if rows else f"No rental_charges records for {match}."

@tool(owner="agent", rw="read")
def find_rental_requests(ctx: ToolContext, rental_request_id: str = "", customer_id: str = "", rental_agreement_id: str = "", disputed_charge_id: str = "") -> str:
    """Look up tool rental service requests — extensions, cancellations, malfunction reports and damage disputes — with the requested due-back time, disputed charge, approved adjustment, status, filing moment and resolution date.

    Supply any reference number you already hold — every criterion is optional, and records matching all
    of the numbers given are returned. With no criterion at all, every record of this kind is returned.
    When nothing matches, a short notice says so.

    Args:
        rental_request_id: The reference number of a rental service request (extension, cancellation, malfunction report, damage dispute); leave "" if unknown.
        customer_id: The customer reference number of the profile the records belong to; leave "" if unknown.
        rental_agreement_id: The reference number of a tool rental agreement; leave "" if unknown.
        disputed_charge_id: The reference number of the rental charge line being disputed; leave "" if unknown.
    """
    match = {k: v for k, v in {"rental_request_id": rental_request_id, "customer_id": customer_id, "rental_agreement_id": rental_agreement_id, "disputed_charge_id": disputed_charge_id}.items() if v}
    rows = ctx.find("rental_requests", **match)
    return str(rows) if rows else f"No rental_requests records for {match}."

@tool(owner="agent", rw="read")
def find_special_orders(ctx: ToolContext, special_order_id: str = "", customer_id: str = "", pro_quote_id: str = "", linked_install_contract_id: str = "") -> str:
    """Look up special orders: program, status, order number, vendor and item, order moment, order total and pricing basis, fulfillment method and address, promised and estimated ready dates, who measured, template status, vendor milestones, ready, pickup, cancellation and return dates, cancellation reason, linked installation contract and balance due.

    Supply any reference number you already hold — every criterion is optional, and records matching all
    of the numbers given are returned. With no criterion at all, every record of this kind is returned.
    When nothing matches, a short notice says so.

    Args:
        special_order_id: The reference number of a special order; leave "" if unknown.
        customer_id: The customer reference number of the profile the records belong to; leave "" if unknown.
        pro_quote_id: The reference number of a ProBuild volume pricing quote; leave "" if unknown.
        linked_install_contract_id: The reference number of the installation contract the order supplies; leave "" if unknown.
    """
    match = {k: v for k, v in {"special_order_id": special_order_id, "customer_id": customer_id, "pro_quote_id": pro_quote_id, "linked_install_contract_id": linked_install_contract_id}.items() if v}
    rows = ctx.find("special_orders", **match)
    return str(rows) if rows else f"No special_orders records for {match}."

@tool(owner="agent", rw="read")
def find_special_order_events(ctx: ToolContext, special_order_event_id: str = "", special_order_id: str = "", customer_id: str = "", original_event_id: str = "", special_request_id: str = "") -> str:
    """Look up the lines of special orders: billing, payments with tender and purpose, fees, credits, refunds and condition inspections at store receipt or customer handover.

    Supply any reference number you already hold — every criterion is optional, and records matching all
    of the numbers given are returned. With no criterion at all, every record of this kind is returned.
    When nothing matches, a short notice says so.

    Args:
        special_order_event_id: The reference number of one special order line (billing, payment, fee, credit, refund or inspection); leave "" if unknown.
        special_order_id: The reference number of a special order; leave "" if unknown.
        customer_id: The customer reference number of the profile the records belong to; leave "" if unknown.
        original_event_id: The reference number of the payment line a refund goes back against; leave "" if unknown.
        special_request_id: The reference number of a special order service request (cancellation, return, damage claim, delivery change, delay remedy); leave "" if unknown.
    """
    match = {k: v for k, v in {"special_order_event_id": special_order_event_id, "special_order_id": special_order_id, "customer_id": customer_id, "original_event_id": original_event_id, "special_request_id": special_request_id}.items() if v}
    rows = ctx.find("special_order_events", **match)
    return str(rows) if rows else f"No special_order_events records for {match}."

@tool(owner="agent", rw="read")
def find_special_requests(ctx: ToolContext, special_request_id: str = "", customer_id: str = "", special_order_id: str = "") -> str:
    """Look up special order service requests — cancellations, returns, damage claims, delivery changes and delay remedies — with the remedy chosen, status, filing moment and resolution date.

    Supply any reference number you already hold — every criterion is optional, and records matching all
    of the numbers given are returned. With no criterion at all, every record of this kind is returned.
    When nothing matches, a short notice says so.

    Args:
        special_request_id: The reference number of a special order service request (cancellation, return, damage claim, delivery change, delay remedy); leave "" if unknown.
        customer_id: The customer reference number of the profile the records belong to; leave "" if unknown.
        special_order_id: The reference number of a special order; leave "" if unknown.
    """
    match = {k: v for k, v in {"special_request_id": special_request_id, "customer_id": customer_id, "special_order_id": special_order_id}.items() if v}
    rows = ctx.find("special_requests", **match)
    return str(rows) if rows else f"No special_requests records for {match}."

@tool(owner="agent", rw="read")
def find_pro_memberships(ctx: ToolContext, pro_membership_id: str = "", customer_id: str = "") -> str:
    """Look up ProBuild Rewards memberships: tier, status, member number, enrollment and tier dates, program year, year-to-date qualifying spend, perks points balance, number of authorized purchasers, and suspension or closure details.

    Supply any reference number you already hold — every criterion is optional, and records matching all
    of the numbers given are returned. With no criterion at all, every record of this kind is returned.
    When nothing matches, a short notice says so.

    Args:
        pro_membership_id: The reference number of a ProBuild Rewards membership; leave "" if unknown.
        customer_id: The customer reference number of the profile the records belong to; leave "" if unknown.
    """
    match = {k: v for k, v in {"pro_membership_id": pro_membership_id, "customer_id": customer_id}.items() if v}
    rows = ctx.find("pro_memberships", **match)
    return str(rows) if rows else f"No pro_memberships records for {match}."

@tool(owner="agent", rw="read")
def find_pro_activity(ctx: ToolContext, pro_activity_id: str = "", pro_membership_id: str = "", customer_id: str = "", pro_quote_id: str = "", original_activity_id: str = "") -> str:
    """Look up ProBuild Rewards membership activity: qualifying spend credited or reversed (with purchase reference, date, channel, pricing and tender), year-end resets, points earned with their basis and availability date, redemptions with perk reward codes, expirations and reversals.

    Supply any reference number you already hold — every criterion is optional, and records matching all
    of the numbers given are returned. With no criterion at all, every record of this kind is returned.
    When nothing matches, a short notice says so.

    Args:
        pro_activity_id: The reference number of one membership activity line (qualifying spend, points or redemption); leave "" if unknown.
        pro_membership_id: The reference number of a ProBuild Rewards membership; leave "" if unknown.
        customer_id: The customer reference number of the profile the records belong to; leave "" if unknown.
        pro_quote_id: The reference number of a ProBuild volume pricing quote; leave "" if unknown.
        original_activity_id: The reference number of the qualifying purchase line a reversal or points line refers to; leave "" if unknown.
    """
    match = {k: v for k, v in {"pro_activity_id": pro_activity_id, "pro_membership_id": pro_membership_id, "customer_id": customer_id, "pro_quote_id": pro_quote_id, "original_activity_id": original_activity_id}.items() if v}
    rows = ctx.find("pro_activity", **match)
    return str(rows) if rows else f"No pro_activity records for {match}."

@tool(owner="agent", rw="read")
def find_pro_quotes(ctx: ToolContext, pro_quote_id: str = "", customer_id: str = "", pro_membership_id: str = "") -> str:
    """Look up ProBuild volume pricing quotes: quote number, shelf-price total, discount and quoted total, number of lines, status, pricing and acceptance dates, last day to accept and number of revisions.

    Supply any reference number you already hold — every criterion is optional, and records matching all
    of the numbers given are returned. With no criterion at all, every record of this kind is returned.
    When nothing matches, a short notice says so.

    Args:
        pro_quote_id: The reference number of a ProBuild volume pricing quote; leave "" if unknown.
        customer_id: The customer reference number of the profile the records belong to; leave "" if unknown.
        pro_membership_id: The reference number of a ProBuild Rewards membership; leave "" if unknown.
    """
    match = {k: v for k, v in {"pro_quote_id": pro_quote_id, "customer_id": customer_id, "pro_membership_id": pro_membership_id}.items() if v}
    rows = ctx.find("pro_quotes", **match)
    return str(rows) if rows else f"No pro_quotes records for {match}."

@tool(owner="agent", rw="read")
def find_orders(ctx: ToolContext, order_id: str = "", customer_id: str = "") -> str:
    """Look up customer orders: fulfillment program, status, order number, order moment, merchandise total, delivery address, promised date and delivery window, haul-away, ready and pickup deadline dates, pickup or delivery moment, failed attempts and reschedules, cancellation details and balance due.

    Supply any reference number you already hold — every criterion is optional, and records matching all
    of the numbers given are returned. With no criterion at all, every record of this kind is returned.
    When nothing matches, a short notice says so.

    Args:
        order_id: The reference number of a customer order; leave "" if unknown.
        customer_id: The customer reference number of the profile the records belong to; leave "" if unknown.
    """
    match = {k: v for k, v in {"order_id": order_id, "customer_id": customer_id}.items() if v}
    rows = ctx.find("orders", **match)
    return str(rows) if rows else f"No orders records for {match}."

@tool(owner="agent", rw="read")
def find_order_events(ctx: ToolContext, order_event_id: str = "", order_id: str = "", customer_id: str = "", order_request_id: str = "", original_event_id: str = "") -> str:
    """Look up the lines of customer orders: billing, fees, payments, returns with receipt number, category, reason and channel, credits, refunds and delivery attempts with their outcome and arrival time.

    Supply any reference number you already hold — every criterion is optional, and records matching all
    of the numbers given are returned. With no criterion at all, every record of this kind is returned.
    When nothing matches, a short notice says so.

    Args:
        order_event_id: The reference number of one order line (billing, fee, payment, return, credit, refund or delivery attempt); leave "" if unknown.
        order_id: The reference number of a customer order; leave "" if unknown.
        customer_id: The customer reference number of the profile the records belong to; leave "" if unknown.
        order_request_id: The reference number of an order service request (cancellation, delivery reschedule, pickup extension, price adjustment, not-received claim, return); leave "" if unknown.
        original_event_id: The reference number of the payment line a refund goes back against; leave "" if unknown.
    """
    match = {k: v for k, v in {"order_event_id": order_event_id, "order_id": order_id, "customer_id": customer_id, "order_request_id": order_request_id, "original_event_id": original_event_id}.items() if v}
    rows = ctx.find("order_events", **match)
    return str(rows) if rows else f"No order_events records for {match}."

@tool(owner="agent", rw="read")
def find_order_requests(ctx: ToolContext, order_request_id: str = "", customer_id: str = "", order_id: str = "") -> str:
    """Look up order service requests — cancellations, delivery reschedules, pickup extensions, price adjustments, not-received claims and return authorizations — with status, filing moment and resolution date.

    Supply any reference number you already hold — every criterion is optional, and records matching all
    of the numbers given are returned. With no criterion at all, every record of this kind is returned.
    When nothing matches, a short notice says so.

    Args:
        order_request_id: The reference number of an order service request (cancellation, delivery reschedule, pickup extension, price adjustment, not-received claim, return); leave "" if unknown.
        customer_id: The customer reference number of the profile the records belong to; leave "" if unknown.
        order_id: The reference number of a customer order; leave "" if unknown.
    """
    match = {k: v for k, v in {"order_request_id": order_request_id, "customer_id": customer_id, "order_id": order_id}.items() if v}
    rows = ctx.find("order_requests", **match)
    return str(rows) if rows else f"No order_requests records for {match}."

@tool(owner="agent", rw="read")
def find_customers(ctx: ToolContext, customer_id: str = "", phone_number: str = "", email: str = "",
                   name: str = "", business_name: str = "") -> str:
    """Find the customer profile a call is about, either by its customer reference number or by what the
    caller can tell you: the phone number or email on the profile, the full name, or for a business
    customer the registered business name. Every criterion is optional; give whichever are known.
    The profile returned shows the customer reference number, name, phone number, email, billing ZIP code,
    date of birth, last four digits of the SSN or EIN, whether it is a consumer or a pro (business) profile,
    the business name, the date the profile was opened and the home store. Finding a profile does not
    confirm that the caller is the person on it — identity is confirmed separately.

    Args:
        customer_id: The customer reference number, when already known; leave "" if unknown.
        phone_number: The phone number the caller gives, 10 digits; leave "" if not provided.
        email: The email address the caller gives; leave "" if not provided.
        name: The caller's full name as given; leave "" if not provided.
        business_name: The registered business name the caller gives for a pro account; leave "" if not provided.
    """
    match = {k: v for k, v in {"customer_id": customer_id, "phone_number": phone_number, "email": email,
                               "name": name, "business_name": business_name}.items() if v}
    if not match:
        return "Error: provide at least one reference number or profile detail to find the customer."
    rows = ctx.fuzzy_find("customers", **match)
    if not rows:
        return f"No customer matches {match}."
    if len(rows) > 1:
        return f"Error: {len(rows)} customers match {match}; ask for one more detail to tell them apart."
    return str(rows[0])


@tool(owner="agent", rw="write")
def verify_customer_identity(ctx: ToolContext, customer_id: str, phone_number: str = "", email: str = "",
                             billing_zip: str = "", date_of_birth: str = "", tax_id_last4: str = "") -> str:
    """Confirm that the caller is the holder of a customer profile, and record the outcome. Account
    information is shared and any account, payment, refund or service action is taken only after
    the caller's identity is confirmed.

    This tool makes the comparison itself: it checks each piece of identity information the caller
    states against the profile on file, counts how many match, and confirms the caller only when at least
    2 match. The customer reference number only opens the profile and never counts as a match. Callers
    usually give only some of these details — pass exactly what the caller said and leave the rest blank.
    The outcome is recorded; if a first attempt falls short and a later attempt with more details
    succeeds, the confirmation stands.

    Args:
        customer_id: The customer reference number from the profile lookup. Required; it opens the profile and is not counted as a match.
        phone_number: The phone number the caller states, 10 digits; leave "" if not stated.
        email: The email address the caller states; leave "" if not stated.
        billing_zip: The 5-digit ZIP code of the billing address the caller states; leave "" if not stated.
        date_of_birth: The date of birth the caller states, as YYYY-MM-DD; leave "" if not stated.
        tax_id_last4: The last four digits of the SSN (consumer) or EIN (business) the caller states; leave "" if not stated.
    """
    if not customer_id:
        return "Error: customer_id is required; find the customer profile first and pass its reference number."
    rows = ctx.find("customers", customer_id=customer_id)
    if not rows:
        return f"Error: no customer {customer_id}; cannot verify."
    rec = rows[0]
    # The tool owns the comparison; the locator customer_id is deliberately not a credential.
    supplied = {"phone_number": phone_number, "email": email, "billing_zip": billing_zip,
                "date_of_birth": date_of_birth, "tax_id_last4": tax_id_last4}
    def norm(field, value):
        text = str(value or "").strip()
        return text.lower() if field == "email" else text
    matched = sum(1 for field, value in supplied.items()
                  if value and norm(field, rec.get(field)) == norm(field, value))
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
    return (f"Identity verified for {customer_id} ({matched} detail(s) matched)." if verified
            else f"Identity NOT verified for {customer_id} (only {matched} of the required 2 details matched). "
                 "Ask the caller for another detail on file and try again.")


@tool(owner="agent", rw="write")
def transfer_to_human_agent(ctx: ToolContext, customer_id: str, reason: str) -> str:
    """Transfer the customer to a human Ridgeline Customer Care representative and record the transfer
    with its reason. Use it in one of two situations only: when no Ridgeline policy provides a way to
    resolve what the customer is asking for, or when the customer has explicitly asked to speak with a
    human representative at least 2 times during the conversation.

    Args:
        customer_id: The customer reference number from the profile lookup (the profile must exist).
        reason: Why the customer is being transferred; exactly one of POLICY_NOT_COVERED (no policy offers a way to resolve the request) or CUSTOMER_REQUESTED (the customer explicitly asked for a human representative at least 2 times). Never free text.
    """
    allowed = {"POLICY_NOT_COVERED", "CUSTOMER_REQUESTED"}
    if reason not in allowed:
        return f"Error: unknown transfer reason '{reason}'. Valid: {', '.join(sorted(allowed))}."
    if not ctx.find("customers", customer_id=customer_id):
        return f"Error: no customer {customer_id}; cannot record the transfer."
    rid = ctx.make_id("hof_", customer_id, reason)
    ctx.create("human_handoffs", rid, handoff_id=rid, customer_id=customer_id,
               reason=reason, created_at=ctx.now())
    return f"Transfer to a human representative recorded for {customer_id} ({reason})."

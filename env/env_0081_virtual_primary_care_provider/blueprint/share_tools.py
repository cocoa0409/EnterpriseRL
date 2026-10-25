"""Shared tools for env_0081_virtual_primary_care_provider (Larkspur Health).

One record finder per business record type (the customers finder doubles as the identity entry),
the identity-verification write (two matching credentials required) and the transfer to a human
representative (two explicit requests for a human).
"""

from erlbench import ToolContext, tool


@tool(owner="agent", rw="read")
def find_membership_holdings(ctx: ToolContext, membership_id: str = "", customer_id: str = "", referred_by_customer_id: str = "") -> str:
    """Look up Larkspur Membership records: the tier held, membership status, enrollment and activation dates, trial end, current billing period and next billing date, membership year start, auto-renew setting, pause dates, cancellation and suspension dates, assigned primary clinician, account credit balance, enrollment channel and referring patient.

    Every reference number is optional; supply whichever are known. Returns every matching record, or a
    message that none was found.

    Args:
        membership_id: The membership reference number, exactly as shown on a record already looked up; leave "" if unknown.
        customer_id: The patient reference number, exactly as shown on a record already looked up; leave "" if unknown.
        referred_by_customer_id: The reference number of the patient who referred this member, exactly as shown on a record already looked up; leave "" if unknown.
    """
    match = {k: v for k, v in {"membership_id": membership_id, "customer_id": customer_id, "referred_by_customer_id": referred_by_customer_id}.items() if v}
    rows = ctx.find("membership_holdings", **match)
    return str(rows) if rows else f"No membership records found for {match}."


@tool(owner="agent", rw="read")
def find_membership_charges(ctx: ToolContext, mem_charge_id: str = "", membership_id: str = "", customer_id: str = "", original_charge_id: str = "") -> str:
    """Look up membership billing lines: dues charges, enrollment fees, upgrade proration charges, pause hold fees, refunds, card chargebacks and declined payment attempts, each with its amount, posting date, billing period, tier priced, attempt number and refund basis.

    Every reference number is optional; supply whichever are known. Returns every matching record, or a
    message that none was found.

    Args:
        mem_charge_id: The membership billing line reference number, exactly as shown on a record already looked up; leave "" if unknown.
        membership_id: The membership reference number, exactly as shown on a record already looked up; leave "" if unknown.
        customer_id: The patient reference number, exactly as shown on a record already looked up; leave "" if unknown.
        original_charge_id: The reference number of the billing line being refunded or reversed, exactly as shown on a record already looked up; leave "" if unknown.
    """
    match = {k: v for k, v in {"mem_charge_id": mem_charge_id, "membership_id": membership_id, "customer_id": customer_id, "original_charge_id": original_charge_id}.items() if v}
    rows = ctx.find("membership_charges", **match)
    return str(rows) if rows else f"No membership billing line records found for {match}."


@tool(owner="agent", rw="read")
def find_membership_credits(ctx: ToolContext, mem_credit_id: str = "", membership_id: str = "", customer_id: str = "", source_credit_id: str = "", applied_charge_id: str = "", referred_customer_id: str = "", related_visit_id: str = "") -> str:
    """Look up membership account-credit lines: referral and goodwill credits issued, credits applied to charges and credits that expired, with amounts, dates, expiry dates and what each credit is linked to.

    Every reference number is optional; supply whichever are known. Returns every matching record, or a
    message that none was found.

    Args:
        mem_credit_id: The account-credit line reference number, exactly as shown on a record already looked up; leave "" if unknown.
        membership_id: The membership reference number, exactly as shown on a record already looked up; leave "" if unknown.
        customer_id: The patient reference number, exactly as shown on a record already looked up; leave "" if unknown.
        source_credit_id: The reference number of the issued credit drawn down, exactly as shown on a record already looked up; leave "" if unknown.
        applied_charge_id: The reference number of the billing line a credit paid toward, exactly as shown on a record already looked up; leave "" if unknown.
        referred_customer_id: The reference number of the referred patient, exactly as shown on a record already looked up; leave "" if unknown.
        related_visit_id: The visit reference number a goodwill credit compensates, exactly as shown on a record already looked up; leave "" if unknown.
    """
    match = {k: v for k, v in {"mem_credit_id": mem_credit_id, "membership_id": membership_id, "customer_id": customer_id, "source_credit_id": source_credit_id, "applied_charge_id": applied_charge_id, "referred_customer_id": referred_customer_id, "related_visit_id": related_visit_id}.items() if v}
    rows = ctx.find("membership_credits", **match)
    return str(rows) if rows else f"No account-credit line records found for {match}."


@tool(owner="agent", rw="read")
def find_membership_notices(ctx: ToolContext, mem_notice_id: str = "", membership_id: str = "", customer_id: str = "") -> str:
    """Look up membership notices sent to a patient: annual renewal notices and free-trial reminders, with the date sent, the renewal or trial-end date announced and the channel used.

    Every reference number is optional; supply whichever are known. Returns every matching record, or a
    message that none was found.

    Args:
        mem_notice_id: The membership notice reference number, exactly as shown on a record already looked up; leave "" if unknown.
        membership_id: The membership reference number, exactly as shown on a record already looked up; leave "" if unknown.
        customer_id: The patient reference number, exactly as shown on a record already looked up; leave "" if unknown.
    """
    match = {k: v for k, v in {"mem_notice_id": mem_notice_id, "membership_id": membership_id, "customer_id": customer_id}.items() if v}
    rows = ctx.find("membership_notices", **match)
    return str(rows) if rows else f"No membership notice records found for {match}."


@tool(owner="agent", rw="read")
def find_membership_requests(ctx: ToolContext, mem_request_id: str = "", customer_id: str = "", membership_id: str = "") -> str:
    """Look up membership change requests: cancellations, pauses, upgrades, downgrades, billing-cycle switches and auto-renew changes, with the request date, effective date, target tier, pause length and outcome.

    Every reference number is optional; supply whichever are known. Returns every matching record, or a
    message that none was found.

    Args:
        mem_request_id: The membership change request reference number, exactly as shown on a record already looked up; leave "" if unknown.
        customer_id: The patient reference number, exactly as shown on a record already looked up; leave "" if unknown.
        membership_id: The membership reference number, exactly as shown on a record already looked up; leave "" if unknown.
    """
    match = {k: v for k, v in {"mem_request_id": mem_request_id, "customer_id": customer_id, "membership_id": membership_id}.items() if v}
    rows = ctx.find("membership_requests", **match)
    return str(rows) if rows else f"No membership change request records found for {match}."


@tool(owner="agent", rw="read")
def find_sponsor_enrollments(ctx: ToolContext, enrollment_id: str = "", customer_id: str = "", subscriber_customer_id: str = "") -> str:
    """Look up Larkspur at Work enrollments: the employer plan, enrollment status, employer and group number, relationship to the employee, registration, eligibility, coverage start and end dates, termination reason, plan year start, leave of absence and how contributions are collected.

    Every reference number is optional; supply whichever are known. Returns every matching record, or a
    message that none was found.

    Args:
        enrollment_id: The Larkspur at Work enrollment reference number, exactly as shown on a record already looked up; leave "" if unknown.
        customer_id: The patient reference number, exactly as shown on a record already looked up; leave "" if unknown.
        subscriber_customer_id: The reference number of the employee subscriber, exactly as shown on a record already looked up; leave "" if unknown.
    """
    match = {k: v for k, v in {"enrollment_id": enrollment_id, "customer_id": customer_id, "subscriber_customer_id": subscriber_customer_id}.items() if v}
    rows = ctx.find("sponsor_enrollments", **match)
    return str(rows) if rows else f"No Larkspur at Work enrollment records found for {match}."


@tool(owner="agent", rw="read")
def find_sponsor_contributions(ctx: ToolContext, contribution_id: str = "", enrollment_id: str = "", customer_id: str = "", original_contribution_id: str = "") -> str:
    """Look up Larkspur at Work contribution lines: monthly payroll or direct-bill contributions and their refunds, with the covered month, amount, posting date and method.

    Every reference number is optional; supply whichever are known. Returns every matching record, or a
    message that none was found.

    Args:
        contribution_id: The contribution line reference number, exactly as shown on a record already looked up; leave "" if unknown.
        enrollment_id: The Larkspur at Work enrollment reference number, exactly as shown on a record already looked up; leave "" if unknown.
        customer_id: The patient reference number, exactly as shown on a record already looked up; leave "" if unknown.
        original_contribution_id: The reference number of the contribution being refunded, exactly as shown on a record already looked up; leave "" if unknown.
    """
    match = {k: v for k, v in {"contribution_id": contribution_id, "enrollment_id": enrollment_id, "customer_id": customer_id, "original_contribution_id": original_contribution_id}.items() if v}
    rows = ctx.find("sponsor_contributions", **match)
    return str(rows) if rows else f"No contribution line records found for {match}."


@tool(owner="agent", rw="read")
def find_sponsor_eligibility_records(ctx: ToolContext, elig_record_id: str = "", enrollment_id: str = "", customer_id: str = "") -> str:
    """Look up the employer eligibility-file lines received for a patient: adds, terminations, reinstatements, plan changes, leaves and dependent adds, with the stated effective date, the file date and any qualifying life event.

    Every reference number is optional; supply whichever are known. Returns every matching record, or a
    message that none was found.

    Args:
        elig_record_id: The eligibility-file line reference number, exactly as shown on a record already looked up; leave "" if unknown.
        enrollment_id: The Larkspur at Work enrollment reference number, exactly as shown on a record already looked up; leave "" if unknown.
        customer_id: The patient reference number, exactly as shown on a record already looked up; leave "" if unknown.
    """
    match = {k: v for k, v in {"elig_record_id": elig_record_id, "enrollment_id": enrollment_id, "customer_id": customer_id}.items() if v}
    rows = ctx.find("sponsor_eligibility_records", **match)
    return str(rows) if rows else f"No eligibility-file line records found for {match}."


@tool(owner="agent", rw="read")
def find_sponsor_incentives(ctx: ToolContext, incentive_id: str = "", enrollment_id: str = "", customer_id: str = "", qualifying_visit_id: str = "", source_incentive_id: str = "") -> str:
    """Look up Larkspur at Work wellness-incentive lines: incentives earned for a qualifying visit, paid through payroll or forfeited, with amounts, dates and plan year.

    Every reference number is optional; supply whichever are known. Returns every matching record, or a
    message that none was found.

    Args:
        incentive_id: The wellness-incentive line reference number, exactly as shown on a record already looked up; leave "" if unknown.
        enrollment_id: The Larkspur at Work enrollment reference number, exactly as shown on a record already looked up; leave "" if unknown.
        customer_id: The patient reference number, exactly as shown on a record already looked up; leave "" if unknown.
        qualifying_visit_id: The visit reference number that earned the incentive, exactly as shown on a record already looked up; leave "" if unknown.
        source_incentive_id: The reference number of the earned incentive settled, exactly as shown on a record already looked up; leave "" if unknown.
    """
    match = {k: v for k, v in {"incentive_id": incentive_id, "enrollment_id": enrollment_id, "customer_id": customer_id, "qualifying_visit_id": qualifying_visit_id, "source_incentive_id": source_incentive_id}.items() if v}
    rows = ctx.find("sponsor_incentives", **match)
    return str(rows) if rows else f"No wellness-incentive line records found for {match}."


@tool(owner="agent", rw="read")
def find_pack_holdings(ctx: ToolContext, pack_id: str = "", customer_id: str = "", upgraded_from_pack_id: str = "", membership_id: str = "") -> str:
    """Look up Larkspur Visit Pack records: the pack held, its status, purchase and expiry dates, credits remaining, price paid, how it was bought, extensions used, auto-reload setting and any member discount applied.

    Every reference number is optional; supply whichever are known. Returns every matching record, or a
    message that none was found.

    Args:
        pack_id: The visit pack reference number, exactly as shown on a record already looked up; leave "" if unknown.
        customer_id: The patient reference number, exactly as shown on a record already looked up; leave "" if unknown.
        upgraded_from_pack_id: The reference number of the pack an upgrade replaced, exactly as shown on a record already looked up; leave "" if unknown.
        membership_id: The membership reference number, exactly as shown on a record already looked up; leave "" if unknown.
    """
    match = {k: v for k, v in {"pack_id": pack_id, "customer_id": customer_id, "upgraded_from_pack_id": upgraded_from_pack_id, "membership_id": membership_id}.items() if v}
    rows = ctx.find("pack_holdings", **match)
    return str(rows) if rows else f"No visit pack records found for {match}."


@tool(owner="agent", rw="read")
def find_pack_credit_ledger(ctx: ToolContext, pack_entry_id: str = "", pack_id: str = "", customer_id: str = "", visit_id: str = "", source_entry_id: str = "") -> str:
    """Look up visit-pack credit movements: credits granted, redeemed for a visit, reinstated, forfeited, expired or removed, with the number of credits, the date and the visit concerned.

    Every reference number is optional; supply whichever are known. Returns every matching record, or a
    message that none was found.

    Args:
        pack_entry_id: The pack credit movement reference number, exactly as shown on a record already looked up; leave "" if unknown.
        pack_id: The visit pack reference number, exactly as shown on a record already looked up; leave "" if unknown.
        customer_id: The patient reference number, exactly as shown on a record already looked up; leave "" if unknown.
        visit_id: The visit reference number, exactly as shown on a record already looked up; leave "" if unknown.
        source_entry_id: The reference number of the related earlier entry, exactly as shown on a record already looked up; leave "" if unknown.
    """
    match = {k: v for k, v in {"pack_entry_id": pack_entry_id, "pack_id": pack_id, "customer_id": customer_id, "visit_id": visit_id, "source_entry_id": source_entry_id}.items() if v}
    rows = ctx.find("pack_credit_ledger", **match)
    return str(rows) if rows else f"No pack credit movement records found for {match}."


@tool(owner="agent", rw="read")
def find_pack_payments(ctx: ToolContext, pack_payment_id: str = "", pack_id: str = "", customer_id: str = "", visit_id: str = "", original_payment_id: str = "") -> str:
    """Look up visit-pack payment lines: pack purchases, extension fees and refunds, with amounts, dates and refund basis.

    Every reference number is optional; supply whichever are known. Returns every matching record, or a
    message that none was found.

    Args:
        pack_payment_id: The pack payment line reference number, exactly as shown on a record already looked up; leave "" if unknown.
        pack_id: The visit pack reference number, exactly as shown on a record already looked up; leave "" if unknown.
        customer_id: The patient reference number, exactly as shown on a record already looked up; leave "" if unknown.
        visit_id: The visit reference number, exactly as shown on a record already looked up; leave "" if unknown.
        original_payment_id: The reference number of the purchase being refunded, exactly as shown on a record already looked up; leave "" if unknown.
    """
    match = {k: v for k, v in {"pack_payment_id": pack_payment_id, "pack_id": pack_id, "customer_id": customer_id, "visit_id": visit_id, "original_payment_id": original_payment_id}.items() if v}
    rows = ctx.find("pack_payments", **match)
    return str(rows) if rows else f"No pack payment line records found for {match}."


@tool(owner="agent", rw="read")
def find_visit_appointments(ctx: ToolContext, visit_id: str = "", customer_id: str = "", membership_id: str = "", enrollment_id: str = "", coverage_id: str = "", pack_id: str = "", converted_to_visit_id: str = "") -> str:
    """Look up virtual visit appointments: the visit type, status, booking date, scheduled start (US Eastern Time), where the patient said they would be, payment path, the membership, employer plan, insurance coverage or visit pack applied, clinician, reschedule count, cancellation moment, completion date and any consult conversion.

    Every reference number is optional; supply whichever are known. Returns every matching record, or a
    message that none was found.

    Args:
        visit_id: The visit reference number, exactly as shown on a record already looked up; leave "" if unknown.
        customer_id: The patient reference number, exactly as shown on a record already looked up; leave "" if unknown.
        membership_id: The membership reference number, exactly as shown on a record already looked up; leave "" if unknown.
        enrollment_id: The Larkspur at Work enrollment reference number, exactly as shown on a record already looked up; leave "" if unknown.
        coverage_id: The insurance coverage reference number, exactly as shown on a record already looked up; leave "" if unknown.
        pack_id: The visit pack reference number, exactly as shown on a record already looked up; leave "" if unknown.
        converted_to_visit_id: The reference number of the video visit that replaced a converted consult, exactly as shown on a record already looked up; leave "" if unknown.
    """
    match = {k: v for k, v in {"visit_id": visit_id, "customer_id": customer_id, "membership_id": membership_id, "enrollment_id": enrollment_id, "coverage_id": coverage_id, "pack_id": pack_id, "converted_to_visit_id": converted_to_visit_id}.items() if v}
    rows = ctx.find("visit_appointments", **match)
    return str(rows) if rows else f"No visit appointment records found for {match}."


@tool(owner="agent", rw="read")
def find_visit_charges(ctx: ToolContext, visit_charge_id: str = "", visit_id: str = "", customer_id: str = "", original_charge_id: str = "") -> str:
    """Look up visit billing lines: visit fees, after-hours surcharges, insurance cost-share collections, late-cancellation and no-show fees and refunds, with amounts, dates, the price each was based on and refund basis.

    Every reference number is optional; supply whichever are known. Returns every matching record, or a
    message that none was found.

    Args:
        visit_charge_id: The visit billing line reference number, exactly as shown on a record already looked up; leave "" if unknown.
        visit_id: The visit reference number, exactly as shown on a record already looked up; leave "" if unknown.
        customer_id: The patient reference number, exactly as shown on a record already looked up; leave "" if unknown.
        original_charge_id: The reference number of the billing line being refunded or reversed, exactly as shown on a record already looked up; leave "" if unknown.
    """
    match = {k: v for k, v in {"visit_charge_id": visit_charge_id, "visit_id": visit_id, "customer_id": customer_id, "original_charge_id": original_charge_id}.items() if v}
    rows = ctx.find("visit_charges", **match)
    return str(rows) if rows else f"No visit billing line records found for {match}."


@tool(owner="agent", rw="read")
def find_visit_estimates(ctx: ToolContext, gfe_id: str = "", visit_id: str = "", customer_id: str = "") -> str:
    """Look up Good Faith Estimates issued for visits, with the estimated amount, the delivery date and the scheduled start the estimate covers.

    Every reference number is optional; supply whichever are known. Returns every matching record, or a
    message that none was found.

    Args:
        gfe_id: The Good Faith Estimate reference number, exactly as shown on a record already looked up; leave "" if unknown.
        visit_id: The visit reference number, exactly as shown on a record already looked up; leave "" if unknown.
        customer_id: The patient reference number, exactly as shown on a record already looked up; leave "" if unknown.
    """
    match = {k: v for k, v in {"gfe_id": gfe_id, "visit_id": visit_id, "customer_id": customer_id}.items() if v}
    rows = ctx.find("visit_estimates", **match)
    return str(rows) if rows else f"No Good Faith Estimate records found for {match}."


@tool(owner="agent", rw="read")
def find_visit_fee_reviews(ctx: ToolContext, fee_review_id: str = "", customer_id: str = "", visit_id: str = "", visit_charge_id: str = "") -> str:
    """Look up fee review requests on late-cancellation and no-show fees, with the fee concerned, the reason given and the outcome.

    Every reference number is optional; supply whichever are known. Returns every matching record, or a
    message that none was found.

    Args:
        fee_review_id: The fee review request reference number, exactly as shown on a record already looked up; leave "" if unknown.
        customer_id: The patient reference number, exactly as shown on a record already looked up; leave "" if unknown.
        visit_id: The visit reference number, exactly as shown on a record already looked up; leave "" if unknown.
        visit_charge_id: The visit billing line reference number, exactly as shown on a record already looked up; leave "" if unknown.
    """
    match = {k: v for k, v in {"fee_review_id": fee_review_id, "customer_id": customer_id, "visit_id": visit_id, "visit_charge_id": visit_charge_id}.items() if v}
    rows = ctx.find("visit_fee_reviews", **match)
    return str(rows) if rows else f"No fee review request records found for {match}."


@tool(owner="agent", rw="read")
def find_rx_prescriptions(ctx: ToolContext, rx_id: str = "", customer_id: str = "", prescribing_visit_id: str = "", renewed_from_rx_id: str = "", coverage_id: str = "") -> str:
    """Look up prescriptions: drug and formulary level, status, written and expiration dates, days supply, fill units authorized and remaining, Larkspur Pharmacy or retail pharmacy, prescribing visit, renewal link, auto-refill, pharmacy-benefit or cash billing, hold reason and transfer date.

    Every reference number is optional; supply whichever are known. Returns every matching record, or a
    message that none was found.

    Args:
        rx_id: The prescription reference number, exactly as shown on a record already looked up; leave "" if unknown.
        customer_id: The patient reference number, exactly as shown on a record already looked up; leave "" if unknown.
        prescribing_visit_id: The reference number of the visit at which the prescription was written, exactly as shown on a record already looked up; leave "" if unknown.
        renewed_from_rx_id: The reference number of the prescription a renewal replaced, exactly as shown on a record already looked up; leave "" if unknown.
        coverage_id: The insurance coverage reference number, exactly as shown on a record already looked up; leave "" if unknown.
    """
    match = {k: v for k, v in {"rx_id": rx_id, "customer_id": customer_id, "prescribing_visit_id": prescribing_visit_id, "renewed_from_rx_id": renewed_from_rx_id, "coverage_id": coverage_id}.items() if v}
    rows = ctx.find("rx_prescriptions", **match)
    return str(rows) if rows else f"No prescription records found for {match}."


@tool(owner="agent", rw="read")
def find_rx_fills(ctx: ToolContext, rx_fill_id: str = "", rx_id: str = "", customer_id: str = "", source_fill_id: str = "") -> str:
    """Look up prescription fill movements: units authorized, fills dispensed and shipped, packages returned to stock and reships, with dates, days supply, shipping speed and early-refill use.

    Every reference number is optional; supply whichever are known. Returns every matching record, or a
    message that none was found.

    Args:
        rx_fill_id: The fill reference number, exactly as shown on a record already looked up; leave "" if unknown.
        rx_id: The prescription reference number, exactly as shown on a record already looked up; leave "" if unknown.
        customer_id: The patient reference number, exactly as shown on a record already looked up; leave "" if unknown.
        source_fill_id: The reference number of the dispensed fill concerned, exactly as shown on a record already looked up; leave "" if unknown.
    """
    match = {k: v for k, v in {"rx_fill_id": rx_fill_id, "rx_id": rx_id, "customer_id": customer_id, "source_fill_id": source_fill_id}.items() if v}
    rows = ctx.find("rx_fills", **match)
    return str(rows) if rows else f"No fill movement records found for {match}."


@tool(owner="agent", rw="read")
def find_rx_charges(ctx: ToolContext, rx_charge_id: str = "", rx_id: str = "", customer_id: str = "", rx_fill_id: str = "", original_charge_id: str = "") -> str:
    """Look up pharmacy billing lines: fill charges, shipping charges and refunds, with amounts, dates, the price basis and the pharmacy-benefit patient pay.

    Every reference number is optional; supply whichever are known. Returns every matching record, or a
    message that none was found.

    Args:
        rx_charge_id: The pharmacy billing line reference number, exactly as shown on a record already looked up; leave "" if unknown.
        rx_id: The prescription reference number, exactly as shown on a record already looked up; leave "" if unknown.
        customer_id: The patient reference number, exactly as shown on a record already looked up; leave "" if unknown.
        rx_fill_id: The fill reference number, exactly as shown on a record already looked up; leave "" if unknown.
        original_charge_id: The reference number of the billing line being refunded or reversed, exactly as shown on a record already looked up; leave "" if unknown.
    """
    match = {k: v for k, v in {"rx_charge_id": rx_charge_id, "rx_id": rx_id, "customer_id": customer_id, "rx_fill_id": rx_fill_id, "original_charge_id": original_charge_id}.items() if v}
    rows = ctx.find("rx_charges", **match)
    return str(rows) if rows else f"No pharmacy billing line records found for {match}."


@tool(owner="agent", rw="read")
def find_rx_requests(ctx: ToolContext, rx_request_id: str = "", customer_id: str = "", rx_id: str = "", rx_fill_id: str = "") -> str:
    """Look up pharmacy requests: renewals, transfers to another pharmacy, lost-package claims and early-refill overrides, with dates and outcomes.

    Every reference number is optional; supply whichever are known. Returns every matching record, or a
    message that none was found.

    Args:
        rx_request_id: The pharmacy request reference number, exactly as shown on a record already looked up; leave "" if unknown.
        customer_id: The patient reference number, exactly as shown on a record already looked up; leave "" if unknown.
        rx_id: The prescription reference number, exactly as shown on a record already looked up; leave "" if unknown.
        rx_fill_id: The fill reference number, exactly as shown on a record already looked up; leave "" if unknown.
    """
    match = {k: v for k, v in {"rx_request_id": rx_request_id, "customer_id": customer_id, "rx_id": rx_id, "rx_fill_id": rx_fill_id}.items() if v}
    rows = ctx.find("rx_requests", **match)
    return str(rows) if rows else f"No pharmacy request records found for {match}."


@tool(owner="agent", rw="read")
def find_lab_orders(ctx: ToolContext, lab_order_id: str = "", customer_id: str = "", ordering_visit_id: str = "", membership_id: str = "", enrollment_id: str = "", coverage_id: str = "", redraw_of_order_id: str = "") -> str:
    """Look up lab orders: the panel, status, order date, ordering visit, collection method, payment path and the membership, employer plan or coverage applied, requisition expiry, kit, collection, result and review dates, any specimen rejection and redraw link.

    Every reference number is optional; supply whichever are known. Returns every matching record, or a
    message that none was found.

    Args:
        lab_order_id: The lab order reference number, exactly as shown on a record already looked up; leave "" if unknown.
        customer_id: The patient reference number, exactly as shown on a record already looked up; leave "" if unknown.
        ordering_visit_id: The reference number of the visit the lab order came from, exactly as shown on a record already looked up; leave "" if unknown.
        membership_id: The membership reference number, exactly as shown on a record already looked up; leave "" if unknown.
        enrollment_id: The Larkspur at Work enrollment reference number, exactly as shown on a record already looked up; leave "" if unknown.
        coverage_id: The insurance coverage reference number, exactly as shown on a record already looked up; leave "" if unknown.
        redraw_of_order_id: The reference number of the rejected order a redraw replaces, exactly as shown on a record already looked up; leave "" if unknown.
    """
    match = {k: v for k, v in {"lab_order_id": lab_order_id, "customer_id": customer_id, "ordering_visit_id": ordering_visit_id, "membership_id": membership_id, "enrollment_id": enrollment_id, "coverage_id": coverage_id, "redraw_of_order_id": redraw_of_order_id}.items() if v}
    rows = ctx.find("lab_orders", **match)
    return str(rows) if rows else f"No lab order records found for {match}."


@tool(owner="agent", rw="read")
def find_lab_charges(ctx: ToolContext, lab_charge_id: str = "", lab_order_id: str = "", customer_id: str = "", original_charge_id: str = "") -> str:
    """Look up lab billing lines: panel charges, collection fees and refunds, with amounts, dates, price basis and refund basis.

    Every reference number is optional; supply whichever are known. Returns every matching record, or a
    message that none was found.

    Args:
        lab_charge_id: The lab billing line reference number, exactly as shown on a record already looked up; leave "" if unknown.
        lab_order_id: The lab order reference number, exactly as shown on a record already looked up; leave "" if unknown.
        customer_id: The patient reference number, exactly as shown on a record already looked up; leave "" if unknown.
        original_charge_id: The reference number of the billing line being refunded or reversed, exactly as shown on a record already looked up; leave "" if unknown.
    """
    match = {k: v for k, v in {"lab_charge_id": lab_charge_id, "lab_order_id": lab_order_id, "customer_id": customer_id, "original_charge_id": original_charge_id}.items() if v}
    rows = ctx.find("lab_charges", **match)
    return str(rows) if rows else f"No lab billing line records found for {match}."


@tool(owner="agent", rw="read")
def find_insurance_coverages(ctx: ToolContext, coverage_id: str = "", customer_id: str = "") -> str:
    """Look up insurance coverage records: plan type, verification status, payer, member and group numbers from the card, subscriber details, primary or secondary order, effective and termination dates, last verification, PCP of record, and the copay, deductible, coinsurance and out-of-pocket figures the payer reported.

    Every reference number is optional; supply whichever are known. Returns every matching record, or a
    message that none was found.

    Args:
        coverage_id: The insurance coverage reference number, exactly as shown on a record already looked up; leave "" if unknown.
        customer_id: The patient reference number, exactly as shown on a record already looked up; leave "" if unknown.
    """
    match = {k: v for k, v in {"coverage_id": coverage_id, "customer_id": customer_id}.items() if v}
    rows = ctx.find("insurance_coverages", **match)
    return str(rows) if rows else f"No insurance coverage records found for {match}."


@tool(owner="agent", rw="read")
def find_insurance_claims(ctx: ToolContext, claim_id: str = "", coverage_id: str = "", customer_id: str = "", visit_id: str = "", original_claim_id: str = "") -> str:
    """Look up insurance claims Larkspur filed: original and corrected submissions, with the visit, service date, procedure code, billed amount and submission date.

    Every reference number is optional; supply whichever are known. Returns every matching record, or a
    message that none was found.

    Args:
        claim_id: The claim reference number, exactly as shown on a record already looked up; leave "" if unknown.
        coverage_id: The insurance coverage reference number, exactly as shown on a record already looked up; leave "" if unknown.
        customer_id: The patient reference number, exactly as shown on a record already looked up; leave "" if unknown.
        visit_id: The visit reference number, exactly as shown on a record already looked up; leave "" if unknown.
        original_claim_id: The reference number of the claim a corrected claim replaced, exactly as shown on a record already looked up; leave "" if unknown.
    """
    match = {k: v for k, v in {"claim_id": claim_id, "coverage_id": coverage_id, "customer_id": customer_id, "visit_id": visit_id, "original_claim_id": original_claim_id}.items() if v}
    rows = ctx.find("insurance_claims", **match)
    return str(rows) if rows else f"No claim submission records found for {match}."


@tool(owner="agent", rw="read")
def find_claim_remittances(ctx: ToolContext, remit_id: str = "", coverage_id: str = "", customer_id: str = "", claim_id: str = "") -> str:
    """Look up payer remittances for claims: adjudications and denials, with the allowed amount, payer payment, deductible, copay, coinsurance, patient responsibility and denial reason.

    Every reference number is optional; supply whichever are known. Returns every matching record, or a
    message that none was found.

    Args:
        remit_id: The remittance reference number, exactly as shown on a record already looked up; leave "" if unknown.
        coverage_id: The insurance coverage reference number, exactly as shown on a record already looked up; leave "" if unknown.
        customer_id: The patient reference number, exactly as shown on a record already looked up; leave "" if unknown.
        claim_id: The claim reference number, exactly as shown on a record already looked up; leave "" if unknown.
    """
    match = {k: v for k, v in {"remit_id": remit_id, "coverage_id": coverage_id, "customer_id": customer_id, "claim_id": claim_id}.items() if v}
    rows = ctx.find("claim_remittances", **match)
    return str(rows) if rows else f"No remittance records found for {match}."


@tool(owner="agent", rw="read")
def find_patient_balance_entries(ctx: ToolContext, balance_entry_id: str = "", coverage_id: str = "", customer_id: str = "", claim_id: str = "", visit_id: str = "", source_entry_id: str = "") -> str:
    """Look up patient balance entries on insurance-billed visits: patient responsibility and self-pay rebills posted, booking collections applied, payments, prompt-pay discounts, small-balance and hardship adjustments, credit transfers and credit refunds.

    Every reference number is optional; supply whichever are known. Returns every matching record, or a
    message that none was found.

    Args:
        balance_entry_id: The patient balance entry reference number, exactly as shown on a record already looked up; leave "" if unknown.
        coverage_id: The insurance coverage reference number, exactly as shown on a record already looked up; leave "" if unknown.
        customer_id: The patient reference number, exactly as shown on a record already looked up; leave "" if unknown.
        claim_id: The claim reference number, exactly as shown on a record already looked up; leave "" if unknown.
        visit_id: The visit reference number, exactly as shown on a record already looked up; leave "" if unknown.
        source_entry_id: The reference number of the related earlier entry, exactly as shown on a record already looked up; leave "" if unknown.
    """
    match = {k: v for k, v in {"balance_entry_id": balance_entry_id, "coverage_id": coverage_id, "customer_id": customer_id, "claim_id": claim_id, "visit_id": visit_id, "source_entry_id": source_entry_id}.items() if v}
    rows = ctx.find("patient_balance_entries", **match)
    return str(rows) if rows else f"No patient balance entry records found for {match}."


@tool(owner="agent", rw="read")
def find_patient_statements(ctx: ToolContext, statement_id: str = "", coverage_id: str = "", customer_id: str = "", claim_id: str = "") -> str:
    """Look up patient statements issued for claim balances, with the statement number, date, amount due and due date.

    Every reference number is optional; supply whichever are known. Returns every matching record, or a
    message that none was found.

    Args:
        statement_id: The patient statement reference number, exactly as shown on a record already looked up; leave "" if unknown.
        coverage_id: The insurance coverage reference number, exactly as shown on a record already looked up; leave "" if unknown.
        customer_id: The patient reference number, exactly as shown on a record already looked up; leave "" if unknown.
        claim_id: The claim reference number, exactly as shown on a record already looked up; leave "" if unknown.
    """
    match = {k: v for k, v in {"statement_id": statement_id, "coverage_id": coverage_id, "customer_id": customer_id, "claim_id": claim_id}.items() if v}
    rows = ctx.find("patient_statements", **match)
    return str(rows) if rows else f"No patient statement records found for {match}."


@tool(owner="agent", rw="read")
def find_claim_billing_requests(ctx: ToolContext, billing_request_id: str = "", customer_id: str = "", coverage_id: str = "", claim_id: str = "") -> str:
    """Look up billing requests: payment plans, hardship reviews, records for a patient's own appeal and superbills, with dates, plan terms and outcomes.

    Every reference number is optional; supply whichever are known. Returns every matching record, or a
    message that none was found.

    Args:
        billing_request_id: The billing request reference number, exactly as shown on a record already looked up; leave "" if unknown.
        customer_id: The patient reference number, exactly as shown on a record already looked up; leave "" if unknown.
        coverage_id: The insurance coverage reference number, exactly as shown on a record already looked up; leave "" if unknown.
        claim_id: The claim reference number, exactly as shown on a record already looked up; leave "" if unknown.
    """
    match = {k: v for k, v in {"billing_request_id": billing_request_id, "customer_id": customer_id, "coverage_id": coverage_id, "claim_id": claim_id}.items() if v}
    rows = ctx.find("claim_billing_requests", **match)
    return str(rows) if rows else f"No billing request records found for {match}."


@tool(owner="agent", rw="read")
def find_referrals(ctx: ToolContext, referral_id: str = "", customer_id: str = "", referring_visit_id: str = "", coverage_id: str = "") -> str:
    """Look up in-person care referrals: referral type, status, referral date, referring visit, specialty, imaging modality, urgency, receiving provider and network status, governing coverage, authorization number, visits remaining, validity, appointment date and reissues.

    Every reference number is optional; supply whichever are known. Returns every matching record, or a
    message that none was found.

    Args:
        referral_id: The referral reference number, exactly as shown on a record already looked up; leave "" if unknown.
        customer_id: The patient reference number, exactly as shown on a record already looked up; leave "" if unknown.
        referring_visit_id: The reference number of the visit the referral came from, exactly as shown on a record already looked up; leave "" if unknown.
        coverage_id: The insurance coverage reference number, exactly as shown on a record already looked up; leave "" if unknown.
    """
    match = {k: v for k, v in {"referral_id": referral_id, "customer_id": customer_id, "referring_visit_id": referring_visit_id, "coverage_id": coverage_id}.items() if v}
    rows = ctx.find("referrals", **match)
    return str(rows) if rows else f"No referral records found for {match}."


@tool(owner="agent", rw="read")
def find_referral_authorizations(ctx: ToolContext, referral_auth_id: str = "", referral_id: str = "", customer_id: str = "") -> str:
    """Look up referral authorization lines: requests, approvals, denials, extensions and outside visits reported, with visits, dates and validity.

    Every reference number is optional; supply whichever are known. Returns every matching record, or a
    message that none was found.

    Args:
        referral_auth_id: The referral authorization line reference number, exactly as shown on a record already looked up; leave "" if unknown.
        referral_id: The referral reference number, exactly as shown on a record already looked up; leave "" if unknown.
        customer_id: The patient reference number, exactly as shown on a record already looked up; leave "" if unknown.
    """
    match = {k: v for k, v in {"referral_auth_id": referral_auth_id, "referral_id": referral_id, "customer_id": customer_id}.items() if v}
    rows = ctx.find("referral_authorizations", **match)
    return str(rows) if rows else f"No referral authorization line records found for {match}."


@tool(owner="agent", rw="read")
def find_referral_coordination(ctx: ToolContext, coordination_id: str = "", referral_id: str = "", customer_id: str = "") -> str:
    """Look up referral coordination records: referral packets sent, navigator follow-up contacts and consult reports received.

    Every reference number is optional; supply whichever are known. Returns every matching record, or a
    message that none was found.

    Args:
        coordination_id: The referral coordination record reference number, exactly as shown on a record already looked up; leave "" if unknown.
        referral_id: The referral reference number, exactly as shown on a record already looked up; leave "" if unknown.
        customer_id: The patient reference number, exactly as shown on a record already looked up; leave "" if unknown.
    """
    match = {k: v for k, v in {"coordination_id": coordination_id, "referral_id": referral_id, "customer_id": customer_id}.items() if v}
    rows = ctx.find("referral_coordination", **match)
    return str(rows) if rows else f"No referral coordination record records found for {match}."


@tool(owner="agent", rw="read")
def find_identity_verifications(ctx: ToolContext, verification_id: str = "", customer_id: str = "") -> str:
    """Look up the identity-verification record of a patient, showing whether identity verification has passed and when it was last attempted.

    Every reference number is optional; supply whichever are known. Returns every matching record, or a
    message that none was found.

    Args:
        verification_id: The identity-verification record reference number, exactly as shown on a record already looked up; leave "" if unknown.
        customer_id: The patient reference number, exactly as shown on a record already looked up; leave "" if unknown.
    """
    match = {k: v for k, v in {"verification_id": verification_id, "customer_id": customer_id}.items() if v}
    rows = ctx.find("identity_verifications", **match)
    return str(rows) if rows else f"No identity-verification record records found for {match}."


@tool(owner="agent", rw="read")
def find_human_handoffs(ctx: ToolContext, handoff_id: str = "", customer_id: str = "") -> str:
    """Look up records of conversations handed over to a human representative, with the reason and the moment of the handoff.

    Every reference number is optional; supply whichever are known. Returns every matching record, or a
    message that none was found.

    Args:
        handoff_id: The handoff record reference number, exactly as shown on a record already looked up; leave "" if unknown.
        customer_id: The patient reference number, exactly as shown on a record already looked up; leave "" if unknown.
    """
    match = {k: v for k, v in {"handoff_id": handoff_id, "customer_id": customer_id}.items() if v}
    rows = ctx.find("human_handoffs", **match)
    return str(rows) if rows else f"No handoff record records found for {match}."

@tool(owner="agent", rw="read")
def find_customers(ctx: ToolContext, customer_id: str = "", patient_number: str = "", full_name: str = "", phone: str = "",
                   email: str = "", date_of_birth: str = "") -> str:
    """Look up a Larkspur Health patient profile to establish whose account this conversation is about. Search by the
    patient reference number, or by what the caller can tell you: their Larkspur patient number, full name, mobile
    number, email address or date of birth. Every criterion is optional; supply whichever are known, and add another
    one when several patients match. The profile returned shows the patient reference number, full name, patient
    number, date of birth, registered mobile number and email, home ZIP code and state, and the date the profile was
    opened. Finding a profile does not verify the caller's identity.

    Args:
        customer_id: The patient reference number, exactly as shown on a record already looked up; leave "" if unknown.
        patient_number: The Larkspur patient number the caller reads from the app or a statement, format LH- followed by 7 digits (e.g. LH-4829137); leave "" if not provided.
        full_name: The patient's full name as the caller states it; leave "" if not provided.
        phone: The registered mobile number, 10 digits (e.g. 6175550142); leave "" if not provided.
        email: The registered email address; leave "" if not provided.
        date_of_birth: The patient's date of birth, YYYY-MM-DD; leave "" if not provided.
    """
    match = {k: v for k, v in {"customer_id": customer_id, "patient_number": patient_number, "full_name": full_name,
                               "phone": phone, "email": email, "date_of_birth": date_of_birth}.items() if v}
    if not match:
        return "Error: provide at least one reference number or profile detail to find the patient."
    rows = ctx.fuzzy_find("customers", **match)
    if not rows:
        return f"No patient profile matches {match}."
    if len(rows) > 1:
        return f"Error: {len(rows)} patient profiles match {match}; ask the caller for one more detail to tell them apart."
    return str(rows[0])


@tool(owner="agent", rw="write")
def verify_patient_identity(ctx: ToolContext, customer_id: str, patient_number: str = "", date_of_birth: str = "",
                            phone: str = "", email: str = "", home_zip: str = "") -> str:
    """Verify the caller's identity against the patient profile and record the outcome. Identity must be verified
    before any account information is discussed or any change, charge or refund is made. This tool does the
    comparison itself: it checks each detail the caller states against the profile on file, counts the details that
    match, and passes only when at least 2 of them match. The patient reference number only identifies which profile
    to check and never counts as a match. Callers usually give only some details, so pass exactly the values the
    caller stated and leave the others blank. The outcome is recorded; if an attempt fails and a later attempt with
    more details passes, the patient is recorded as verified.

    Args:
        customer_id: The patient reference number from the profile lookup. Required; used only to find the profile and not counted as a match.
        patient_number: The Larkspur patient number the caller states, format LH- followed by 7 digits; leave "" if not stated.
        date_of_birth: The date of birth the caller states, YYYY-MM-DD; leave "" if not stated.
        phone: The mobile number the caller states, 10 digits with no punctuation; leave "" if not stated.
        email: The email address the caller states; leave "" if not stated.
        home_zip: The 5-digit home ZIP code the caller states; leave "" if not stated.
    """
    if not customer_id:
        return "Error: customer_id is required; look up the patient profile first and pass its reference number."
    rows = ctx.find("customers", customer_id=customer_id)
    if not rows:
        return f"Error: no patient profile {customer_id}; cannot verify."
    rec = rows[0]
    # The tool owns the comparison; the locator customer_id is never counted.
    supplied = {"patient_number": patient_number, "date_of_birth": date_of_birth, "phone": phone,
                "email": email, "home_zip": home_zip}

    def norm(field, value):
        s = str(value).strip()
        if field == "email" or field == "patient_number":
            return s.lower()
        if field == "phone":
            return "".join(ch for ch in s if ch.isdigit())
        return s

    matched = sum(1 for field, value in supplied.items()
                  if value and rec.get(field) is not None and norm(field, rec.get(field)) == norm(field, value))
    verified = matched >= 2
    rid = ctx.make_id("ver_", customer_id)
    prior = ctx.find("identity_verifications", verification_id=rid)
    verified = verified or bool(prior and prior[0].get("verified"))
    if prior:
        ctx.update("identity_verifications", rid, verified=verified, verified_at=ctx.now())
    else:
        ctx.create("identity_verifications", rid, verification_id=rid, customer_id=customer_id,
                   verified=verified, verified_at=ctx.now())
    return (f"Identity verified for patient {customer_id} ({matched} detail(s) matched)." if verified
            else f"Identity NOT verified for patient {customer_id} (only {matched} of the required 2 details matched). "
                 "Ask the caller for another detail on file and try again.")


@tool(owner="agent", rw="write")
def transfer_to_human_agent(ctx: ToolContext, customer_id: str, reason: str) -> str:
    """Hand the conversation over to a human Larkspur Health representative and record the handoff with its reason.
    Use it when no Larkspur policy can resolve what the patient is asking for, or when the patient has explicitly
    asked to speak with a human representative at least 2 times.

    Args:
        customer_id: The patient reference number from the profile lookup; the profile must exist.
        reason: Why the conversation is handed over; exactly one of POLICY_NOT_COVERED (no Larkspur policy can resolve the request) or CUSTOMER_REQUESTED (the patient has explicitly asked for a human representative at least 2 times). Never free text.
    """
    allowed = {"POLICY_NOT_COVERED", "CUSTOMER_REQUESTED"}
    if reason not in allowed:
        return f"Error: unknown handoff reason '{reason}'. Valid: {', '.join(sorted(allowed))}."
    if not ctx.find("customers", customer_id=customer_id):
        return f"Error: no patient profile {customer_id}; cannot record the handoff."
    rid = ctx.make_id("hof_", customer_id, reason)
    ctx.create("human_handoffs", rid, handoff_id=rid, customer_id=customer_id, reason=reason, created_at=ctx.now())
    return f"Handoff to a human representative recorded for patient {customer_id} ({reason})."

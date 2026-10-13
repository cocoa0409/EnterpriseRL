"""Shared tools for env_0041_online_used_car_retailer (Kestrel Auto). Output of the erl-scenario-blueprint skill.

Every tool here is a SHARE tool: always present in its owner's tool list.
  - one record finder per table (the customers finder doubles as the identity entry),
  - the identity-verification write (compares the stated credentials itself; passes at 3 matches),
  - the transfer-to-human write (two reasons; CUSTOMER_REQUESTED after 2 explicit requests).
Customer-originated writes are difficulty task tools, never share tools.
"""

from erlbench import ToolContext, tool


def _criteria(**kwargs):
    # Keep only the criteria the caller actually supplied.
    return {k: v for k, v in kwargs.items() if v}


# --------------------------------------------------------------------------- identity entry
@tool(owner="agent", rw="read")
def find_customers(ctx: ToolContext, customer_id: str = "", phone_number: str = "", email: str = "",
                   name: str = "") -> str:
    """Look up a Kestrel Auto customer profile to establish whose account this conversation is about.

    You can search by the customer reference number, or by what the caller can naturally tell you: the
    mobile number on the profile, the sign-in email, or the full name. Supply whichever you have; every
    criterion is optional, but at least one is needed. Spacing, punctuation and letter case in what the
    caller says do not prevent a match. A single match returns the full profile: name, mobile number,
    email, date of birth, last four digits of the Social Security number, residential ZIP code and state,
    and the date the profile was opened. When several profiles match you are asked for one more detail.
    Finding a profile does not verify the caller's identity.

    Args:
        customer_id: The customer reference number, if already known; leave "" if unknown.
        phone_number: The mobile number the caller gives, 10 digits; leave "" if not provided.
        email: The email address the caller gives; leave "" if not provided.
        name: The caller's full name as they state it; leave "" if not provided.
    """
    match = _criteria(customer_id=customer_id, phone_number=phone_number, email=email, name=name)
    if not match:
        return "Error: provide at least one reference number or profile detail to find the customer."
    rows = ctx.fuzzy_find("customers", **match)
    if not rows:
        return f"No customer profile matches {match}."
    if len(rows) > 1:
        return f"Error: {len(rows)} customer profiles match {match}; ask the caller for one more detail."
    return str(rows[0])


# --------------------------------------------------------------------------- purchase
@tool(owner="agent", rw="read")
def find_purchase_orders(ctx: ToolContext, purchase_order_id: str = "", customer_id: str = "",
                         exchange_source_order_id: str = "") -> str:
    """Look up vehicle purchase orders: the reserved, signed, delivered, returned or completed purchase of
    one vehicle by one buyer.

    Each order shows the vehicle program, the VIN and description, model year, listing and handover
    odometer readings, the agreed vehicle price, how the purchase is being paid, the selling and registration
    states, transport distance, whether insurance has been verified, the reservation and hold dates, signing
    and handover dates, the return odometer, the order's current status and closure reason, the amount still
    owed on the order and any reservation deposit held. Search by any reference number you have; all are
    optional but at least one is needed. Returns every matching order, or a not-found message.

    Args:
        purchase_order_id: The purchase order reference number; leave "" if unknown.
        customer_id: The buyer's customer reference number, to list all of their orders; leave "" if unknown.
        exchange_source_order_id: The reference number of a returned order, to find the replacement order of a 7-day exchange; leave "" if unknown.
    """
    match = _criteria(purchase_order_id=purchase_order_id, customer_id=customer_id,
                      exchange_source_order_id=exchange_source_order_id)
    if not match:
        return "Error: provide at least one reference number."
    rows = ctx.find("purchase_orders", **match)
    return str(rows) if rows else f"No purchase orders for {match}."


@tool(owner="agent", rw="read")
def find_purchase_transactions(ctx: ToolContext, purchase_txn_id: str = "", purchase_order_id: str = "",
                               customer_id: str = "", source_txn_id: str = "",
                               linked_reference_id: str = "") -> str:
    """Look up the money history of a purchase order: reservation deposits paid, applied or refunded,
    charges posted or reversed, payments received and refunds issued.

    Each entry shows its type, posting date, amount, the charge type, payment source and payment channel,
    the refund type and reason where they apply, the earlier entry it relates to, and the outside record
    behind it (for example the finance contract that funded the order or the trade-in that supplied equity).
    Search by any reference number; all are optional but at least one is needed. Returns every matching entry,
    or a not-found message.

    Args:
        purchase_txn_id: The reference number of one ledger entry; leave "" if unknown.
        purchase_order_id: The purchase order reference number, to list its whole history; leave "" if unknown.
        customer_id: The buyer's customer reference number; leave "" if unknown.
        source_txn_id: The reference number of an earlier entry, to find the entries that reverse, apply or refund it; leave "" if unknown.
        linked_reference_id: The reference number of a finance contract, trade-in agreement or return request, to find the order entries it produced; leave "" if unknown.
    """
    match = _criteria(purchase_txn_id=purchase_txn_id, purchase_order_id=purchase_order_id,
                      customer_id=customer_id, source_txn_id=source_txn_id,
                      linked_reference_id=linked_reference_id)
    if not match:
        return "Error: provide at least one reference number."
    rows = ctx.find("purchase_transactions", **match)
    return str(rows) if rows else f"No purchase order history for {match}."


@tool(owner="agent", rw="read")
def find_purchase_limited_warranty_claims(ctx: ToolContext, limited_warranty_claim_id: str = "",
                                          purchase_order_id: str = "", customer_id: str = "") -> str:
    """Look up decisions on repairs requested under the Kestrel limited warranty included with a purchase.

    Each decision shows the repair facility's repair order number, the failure date and decision date, the
    odometer on the repair order, the vehicle system involved, whether it was approved or why it was denied,
    the repair estimate, the amount Kestrel pays, the deductible, and any rental or towing reimbursement.
    Search by any reference number; all are optional but at least one is needed.

    Args:
        limited_warranty_claim_id: The reference number of one claim decision; leave "" if unknown.
        purchase_order_id: The purchase order whose limited warranty the repairs fall under; leave "" if unknown.
        customer_id: The buyer's customer reference number; leave "" if unknown.
    """
    match = _criteria(limited_warranty_claim_id=limited_warranty_claim_id,
                      purchase_order_id=purchase_order_id, customer_id=customer_id)
    if not match:
        return "Error: provide at least one reference number."
    rows = ctx.find("purchase_limited_warranty_claims", **match)
    return str(rows) if rows else f"No limited warranty claims for {match}."


@tool(owner="agent", rw="read")
def find_purchase_return_requests(ctx: ToolContext, return_request_id: str = "", customer_id: str = "",
                                  purchase_order_id: str = "") -> str:
    """Look up Kestrel 7-Day Return requests.

    Each request shows the order it concerns, the date it was made, whether the customer wants a refund or an
    exchange, whether the vehicle comes back by home pickup or hub drop-off, the odometer the customer reported,
    and its progress (awaiting the customer's signed authorization, confirmed, withdrawn or completed). Search
    by any reference number; all are optional but at least one is needed.

    Args:
        return_request_id: The return request reference number; leave "" if unknown.
        customer_id: The buyer's customer reference number; leave "" if unknown.
        purchase_order_id: The purchase order the return was requested on; leave "" if unknown.
    """
    match = _criteria(return_request_id=return_request_id, customer_id=customer_id,
                      purchase_order_id=purchase_order_id)
    if not match:
        return "Error: provide at least one reference number."
    rows = ctx.find("purchase_return_requests", **match)
    return str(rows) if rows else f"No return requests for {match}."


# --------------------------------------------------------------------------- delivery
@tool(owner="agent", rw="read")
def find_delivery_orders(ctx: ToolContext, delivery_order_id: str = "", customer_id: str = "",
                         purchase_order_id: str = "") -> str:
    """Look up delivery and pickup appointments for purchased vehicles.

    Each appointment shows the fulfillment method, the delivery or hub ZIP code and distance, the current and
    originally booked dates and time window, how many times the customer has rescheduled, missed attempts and
    the cause of the latest one, the completion date, the status, and delivery fees still outstanding. Search
    by any reference number; all are optional but at least one is needed.

    Args:
        delivery_order_id: The appointment reference number; leave "" if unknown.
        customer_id: The buyer's customer reference number; leave "" if unknown.
        purchase_order_id: The purchase order the vehicle is being handed over for; leave "" if unknown.
    """
    match = _criteria(delivery_order_id=delivery_order_id, customer_id=customer_id,
                      purchase_order_id=purchase_order_id)
    if not match:
        return "Error: provide at least one reference number."
    rows = ctx.find("delivery_orders", **match)
    return str(rows) if rows else f"No delivery or pickup appointments for {match}."


@tool(owner="agent", rw="read")
def find_delivery_charges(ctx: ToolContext, delivery_txn_id: str = "", delivery_order_id: str = "",
                          customer_id: str = "", source_txn_id: str = "") -> str:
    """Look up the fee and report history of a delivery or pickup appointment: delivery, reschedule and
    missed-appointment fees, how each was paid, waived or refunded, Fly & Drive travel reimbursements, and
    handover condition reports.

    Each entry shows its type, date, amount, fee type, settlement type, reimbursement type and receipt number,
    condition finding and the appointment date it relates to. Search by any reference number; all are optional
    but at least one is needed.

    Args:
        delivery_txn_id: The reference number of one entry; leave "" if unknown.
        delivery_order_id: The appointment reference number, to list its whole history; leave "" if unknown.
        customer_id: The buyer's customer reference number; leave "" if unknown.
        source_txn_id: The reference number of a fee entry, to find how it was settled; leave "" if unknown.
    """
    match = _criteria(delivery_txn_id=delivery_txn_id, delivery_order_id=delivery_order_id,
                      customer_id=customer_id, source_txn_id=source_txn_id)
    if not match:
        return "Error: provide at least one reference number."
    rows = ctx.find("delivery_charges", **match)
    return str(rows) if rows else f"No delivery fee or report history for {match}."


# --------------------------------------------------------------------------- tradein
@tool(owner="agent", rw="read")
def find_tradein_agreements(ctx: ToolContext, trade_in_id: str = "", customer_id: str = "",
                            purchase_order_id: str = "") -> str:
    """Look up trade-in agreements: Kestrel's written offer on a customer's vehicle and its progress through
    acceptance, pickup, lien payoff and title.

    Each agreement shows the condition grade, the traded vehicle's VIN and description, the original and current
    offer amounts, the offer, expiration and acceptance dates, the mileage the customer stated and the mileage
    found at inspection, keys declared, the lienholder and loan account number, pickup and title-received dates,
    the status, and the trade equity not yet distributed. Search by any reference number; all are optional but at
    least one is needed.

    Args:
        trade_in_id: The trade-in agreement reference number; leave "" if unknown.
        customer_id: The owner's customer reference number; leave "" if unknown.
        purchase_order_id: The purchase order the trade is applied to; leave "" if unknown.
    """
    match = _criteria(trade_in_id=trade_in_id, customer_id=customer_id, purchase_order_id=purchase_order_id)
    if not match:
        return "Error: provide at least one reference number."
    rows = ctx.find("tradein_agreements", **match)
    return str(rows) if rows else f"No trade-in agreements for {match}."


@tool(owner="agent", rw="read")
def find_tradein_transactions(ctx: ToolContext, tradein_txn_id: str = "", trade_in_id: str = "",
                              customer_id: str = "", source_txn_id: str = "",
                              linked_reference_id: str = "") -> str:
    """Look up the history of a trade-in agreement: value credited at pickup, inspection deductions, lienholder
    payoff quotes, the lien payoff sent, negative equity covered, equity applied to a purchase or paid out, and
    title documents received.

    Each entry shows its type, date, amount, deduction reason, the payoff quote's good-through date, per-diem
    amount and reference, how equity was settled, the title document type, and related entries or purchase
    orders. Search by any reference number; all are optional but at least one is needed.

    Args:
        tradein_txn_id: The reference number of one entry; leave "" if unknown.
        trade_in_id: The trade-in agreement reference number, to list its whole history; leave "" if unknown.
        customer_id: The owner's customer reference number; leave "" if unknown.
        source_txn_id: The reference number of an earlier entry (such as a payoff quote), to find the entries that rely on it; leave "" if unknown.
        linked_reference_id: A purchase order reference number, to find equity applied to it; leave "" if unknown.
    """
    match = _criteria(tradein_txn_id=tradein_txn_id, trade_in_id=trade_in_id, customer_id=customer_id,
                      source_txn_id=source_txn_id, linked_reference_id=linked_reference_id)
    if not match:
        return "Error: provide at least one reference number."
    rows = ctx.find("tradein_transactions", **match)
    return str(rows) if rows else f"No trade-in history for {match}."


# --------------------------------------------------------------------------- finance
@tool(owner="agent", rw="read")
def find_finance_contracts(ctx: ToolContext, finance_contract_id: str = "", customer_id: str = "",
                           purchase_order_id: str = "") -> str:
    """Look up Kestrel Auto Finance approvals and retail installment contracts.

    Each record shows the credit tier, decision and approval expiration dates, the amount financed, APR, term,
    monthly payment, contract date, first, next and final due dates, the due day of the month, the date interest
    last stopped accruing (last payment), autopay enrollment, whether pre-signing verifications are complete,
    deferrals and due-date changes used, the status, the unpaid principal and the fees due. Search by any
    reference number; all are optional but at least one is needed.

    Args:
        finance_contract_id: The finance contract or approval reference number; leave "" if unknown.
        customer_id: The borrower's customer reference number; leave "" if unknown.
        purchase_order_id: The purchase order the contract finances; leave "" if unknown.
    """
    match = _criteria(finance_contract_id=finance_contract_id, customer_id=customer_id,
                      purchase_order_id=purchase_order_id)
    if not match:
        return "Error: provide at least one reference number."
    rows = ctx.find("finance_contracts", **match)
    return str(rows) if rows else f"No finance contracts for {match}."


@tool(owner="agent", rw="read")
def find_finance_transactions(ctx: ToolContext, finance_txn_id: str = "", finance_contract_id: str = "",
                              customer_id: str = "", source_txn_id: str = "",
                              linked_reference_id: str = "") -> str:
    """Look up the loan history of a finance contract: funding, payments and how each was split between interest,
    fees and principal, returned payments, principal credits, fees assessed, paid or waived, payoff quotes and
    payment deferrals.

    Each entry shows its type, posting date, amount, the full payment received and its interest, fee and principal
    portions, the payment channel and type, fee type and how it was cleared, the source of a principal credit, the
    installment due date it relates to, and a payoff quote's good-through date and per diem. Search by any
    reference number; all are optional but at least one is needed.

    Args:
        finance_txn_id: The reference number of one entry; leave "" if unknown.
        finance_contract_id: The finance contract reference number, to list its whole history; leave "" if unknown.
        customer_id: The borrower's customer reference number; leave "" if unknown.
        source_txn_id: The reference number of an earlier entry (a payment or a fee), to find what reversed or cleared it; leave "" if unknown.
        linked_reference_id: The reference number of a cancelled service contract, GAP waiver, maintenance plan or purchase order, to find the principal credit it produced; leave "" if unknown.
    """
    match = _criteria(finance_txn_id=finance_txn_id, finance_contract_id=finance_contract_id,
                      customer_id=customer_id, source_txn_id=source_txn_id,
                      linked_reference_id=linked_reference_id)
    if not match:
        return "Error: provide at least one reference number."
    rows = ctx.find("finance_transactions", **match)
    return str(rows) if rows else f"No loan history for {match}."


# --------------------------------------------------------------------------- title
@tool(owner="agent", rw="read")
def find_title_orders(ctx: ToolContext, title_order_id: str = "", customer_id: str = "",
                      purchase_order_id: str = "") -> str:
    """Look up title and registration orders for purchased vehicles.

    Each order shows the registration service type, registration state, lienholder to be recorded, the opening
    date, the temporary tag currently on the vehicle with its expiration date and how many extension tags have
    been issued, submission date and state receipt number, registration date and plate number, completion date,
    the status, and state fees collected and not yet remitted or refunded. Search by any reference number; all
    are optional but at least one is needed.

    Args:
        title_order_id: The title and registration order reference number; leave "" if unknown.
        customer_id: The buyer's customer reference number; leave "" if unknown.
        purchase_order_id: The purchase order the vehicle was bought on; leave "" if unknown.
    """
    match = _criteria(title_order_id=title_order_id, customer_id=customer_id,
                      purchase_order_id=purchase_order_id)
    if not match:
        return "Error: provide at least one reference number."
    rows = ctx.find("title_orders", **match)
    return str(rows) if rows else f"No title and registration orders for {match}."


@tool(owner="agent", rw="read")
def find_title_transactions(ctx: ToolContext, title_txn_id: str = "", title_order_id: str = "",
                            customer_id: str = "", source_txn_id: str = "") -> str:
    """Look up the history of a title and registration order: state fees collected, remitted or refunded,
    documents received from the customer, temporary tags issued, state rejections, and reimbursements paid.

    Each entry shows its type, date, amount, fee type, document type with the form it arrived in and the date
    printed on it, the tag sequence, number and expiration, the state's rejection reason, the reimbursement reason
    and citation or notice number, and the fee entry it settles. Search by any reference number; all are optional
    but at least one is needed.

    Args:
        title_txn_id: The reference number of one entry; leave "" if unknown.
        title_order_id: The title and registration order reference number, to list its whole history; leave "" if unknown.
        customer_id: The buyer's customer reference number; leave "" if unknown.
        source_txn_id: The reference number of a collected fee, to find how it was remitted or refunded; leave "" if unknown.
    """
    match = _criteria(title_txn_id=title_txn_id, title_order_id=title_order_id, customer_id=customer_id,
                      source_txn_id=source_txn_id)
    if not match:
        return "Error: provide at least one reference number."
    rows = ctx.find("title_transactions", **match)
    return str(rows) if rows else f"No title and registration history for {match}."


# --------------------------------------------------------------------------- warranty
@tool(owner="agent", rw="read")
def find_service_contracts(ctx: ToolContext, service_contract_id: str = "", customer_id: str = "",
                           purchase_order_id: str = "", finance_contract_id: str = "") -> str:
    """Look up KestrelCare vehicle service contracts.

    Each contract shows the plan, covered VIN, price, term in months and miles, deductible, sale date, whether it
    was sold with the vehicle, the odometer at sale, when coverage starts by date and odometer, when it ends by date
    and odometer, whether the price was financed and in which finance contract, transfers so far, the status, and
    the coverage still available for repair claims. Search by any reference number; all are optional but at least
    one is needed.

    Args:
        service_contract_id: The service contract reference number; leave "" if unknown.
        customer_id: The contract holder's customer reference number; leave "" if unknown.
        purchase_order_id: The purchase order of the covered vehicle; leave "" if unknown.
        finance_contract_id: The finance contract the price was financed in; leave "" if unknown.
    """
    match = _criteria(service_contract_id=service_contract_id, customer_id=customer_id,
                      purchase_order_id=purchase_order_id, finance_contract_id=finance_contract_id)
    if not match:
        return "Error: provide at least one reference number."
    rows = ctx.find("service_contracts", **match)
    return str(rows) if rows else f"No service contracts for {match}."


@tool(owner="agent", rw="read")
def find_service_contract_transactions(ctx: ToolContext, warranty_txn_id: str = "", service_contract_id: str = "",
                                       customer_id: str = "", source_txn_id: str = "") -> str:
    """Look up the history of a KestrelCare service contract: the coverage limit opened, repair claim decisions,
    claim payments and recoveries, rental, towing and trip interruption reimbursements, cancellation refunds and
    transfer fees.

    Each entry shows its type, date, amount, the repair order number, failure date and odometer, the vehicle
    system, the decision, the estimate and deductible, the facility type, the benefit type and days, the refund
    basis and who received the refund. Search by any reference number; all are optional but at least one is needed.

    Args:
        warranty_txn_id: The reference number of one entry; leave "" if unknown.
        service_contract_id: The service contract reference number, to list its whole history; leave "" if unknown.
        customer_id: The holder's customer reference number; leave "" if unknown.
        source_txn_id: The reference number of a claim decision or payment, to find the payment or recovery tied to it; leave "" if unknown.
    """
    match = _criteria(warranty_txn_id=warranty_txn_id, service_contract_id=service_contract_id,
                      customer_id=customer_id, source_txn_id=source_txn_id)
    if not match:
        return "Error: provide at least one reference number."
    rows = ctx.find("service_contract_transactions", **match)
    return str(rows) if rows else f"No service contract history for {match}."


@tool(owner="agent", rw="read")
def find_service_contract_cancellations(ctx: ToolContext, cancellation_request_id: str = "",
                                        customer_id: str = "", service_contract_id: str = "") -> str:
    """Look up requests to cancel a KestrelCare service contract.

    Each request shows the contract, the request date, the odometer the holder reported, the reason given and its
    progress (awaiting the holder's signed cancellation form, confirmed or withdrawn). Search by any reference
    number; all are optional but at least one is needed.

    Args:
        cancellation_request_id: The cancellation request reference number; leave "" if unknown.
        customer_id: The holder's customer reference number; leave "" if unknown.
        service_contract_id: The service contract the request concerns; leave "" if unknown.
    """
    match = _criteria(cancellation_request_id=cancellation_request_id, customer_id=customer_id,
                      service_contract_id=service_contract_id)
    if not match:
        return "Error: provide at least one reference number."
    rows = ctx.find("service_contract_cancellations", **match)
    return str(rows) if rows else f"No service contract cancellation requests for {match}."


# --------------------------------------------------------------------------- maintenance
@tool(owner="agent", rw="read")
def find_maintenance_plans(ctx: ToolContext, maintenance_plan_id: str = "", customer_id: str = "",
                           purchase_order_id: str = "") -> str:
    """Look up KestrelCare prepaid maintenance plans.

    Each plan shows the plan level, covered VIN, price, sale date and odometer, the date and odometer after which
    visits can no longer be used, whether it was financed, the status, and the prepaid visits still available.
    Search by any reference number; all are optional but at least one is needed.

    Args:
        maintenance_plan_id: The maintenance plan reference number; leave "" if unknown.
        customer_id: The holder's customer reference number; leave "" if unknown.
        purchase_order_id: The purchase order of the covered vehicle; leave "" if unknown.
    """
    match = _criteria(maintenance_plan_id=maintenance_plan_id, customer_id=customer_id,
                      purchase_order_id=purchase_order_id)
    if not match:
        return "Error: provide at least one reference number."
    rows = ctx.find("maintenance_plans", **match)
    return str(rows) if rows else f"No maintenance plans for {match}."


@tool(owner="agent", rw="read")
def find_maintenance_transactions(ctx: ToolContext, maintenance_txn_id: str = "", maintenance_plan_id: str = "",
                                  customer_id: str = "", source_txn_id: str = "") -> str:
    """Look up the visit history of a prepaid maintenance plan: visits credited, redeemed, voided or forfeited,
    out-of-network reimbursements and cancellation refunds.

    Each entry shows its type, date, visits, amount, repair order number, odometer, facility type, refund payee
    and the entry it relates to. Search by any reference number; all are optional but at least one is needed.

    Args:
        maintenance_txn_id: The reference number of one entry; leave "" if unknown.
        maintenance_plan_id: The maintenance plan reference number, to list its whole history; leave "" if unknown.
        customer_id: The holder's customer reference number; leave "" if unknown.
        source_txn_id: The reference number of a redemption, to find its void or reimbursement; leave "" if unknown.
    """
    match = _criteria(maintenance_txn_id=maintenance_txn_id, maintenance_plan_id=maintenance_plan_id,
                      customer_id=customer_id, source_txn_id=source_txn_id)
    if not match:
        return "Error: provide at least one reference number."
    rows = ctx.find("maintenance_transactions", **match)
    return str(rows) if rows else f"No maintenance plan history for {match}."


# --------------------------------------------------------------------------- gap
@tool(owner="agent", rw="read")
def find_gap_waivers(ctx: ToolContext, gap_waiver_id: str = "", customer_id: str = "",
                     finance_contract_id: str = "") -> str:
    """Look up Kestrel GAP waiver addenda attached to finance contracts.

    Each waiver shows the waiver level, the finance contract it belongs to, its price, sale date, term, the vehicle
    cash price and amount financed at sale, and its status. Search by any reference number; all are optional but
    at least one is needed.

    Args:
        gap_waiver_id: The GAP waiver reference number; leave "" if unknown.
        customer_id: The borrower's customer reference number; leave "" if unknown.
        finance_contract_id: The finance contract the waiver is attached to; leave "" if unknown.
    """
    match = _criteria(gap_waiver_id=gap_waiver_id, customer_id=customer_id,
                      finance_contract_id=finance_contract_id)
    if not match:
        return "Error: provide at least one reference number."
    rows = ctx.find("gap_waivers", **match)
    return str(rows) if rows else f"No GAP waivers for {match}."


@tool(owner="agent", rw="read")
def find_gap_transactions(ctx: ToolContext, gap_txn_id: str = "", gap_waiver_id: str = "",
                          customer_id: str = "", source_txn_id: str = "") -> str:
    """Look up the history of a GAP waiver: claims filed, claim documents received, decisions, benefits paid and
    cancellation refunds.

    Each entry shows its type, date, amount, loss date and type, the insurer settlement and loan payoff at the loss,
    the document type, the decision, the refund payee and the entry it relates to. Search by any reference number;
    all are optional but at least one is needed.

    Args:
        gap_txn_id: The reference number of one entry; leave "" if unknown.
        gap_waiver_id: The GAP waiver reference number, to list its whole history; leave "" if unknown.
        customer_id: The borrower's customer reference number; leave "" if unknown.
        source_txn_id: The reference number of a decision, to find the benefit payment for it; leave "" if unknown.
    """
    match = _criteria(gap_txn_id=gap_txn_id, gap_waiver_id=gap_waiver_id, customer_id=customer_id,
                      source_txn_id=source_txn_id)
    if not match:
        return "Error: provide at least one reference number."
    rows = ctx.find("gap_transactions", **match)
    return str(rows) if rows else f"No GAP waiver history for {match}."


# --------------------------------------------------------------------------- logs
@tool(owner="agent", rw="read")
def find_identity_verifications(ctx: ToolContext, verification_id: str = "", customer_id: str = "") -> str:
    """Look up whether a customer's identity has been verified in this conversation, and when the most recent
    verification attempt was made. Search by either reference number; at least one is needed.

    Args:
        verification_id: The verification record reference number; leave "" if unknown.
        customer_id: The customer reference number; leave "" if unknown.
    """
    match = _criteria(verification_id=verification_id, customer_id=customer_id)
    if not match:
        return "Error: provide at least one reference number."
    rows = ctx.find("identity_verifications", **match)
    return str(rows) if rows else f"No identity verification on record for {match}."


@tool(owner="agent", rw="read")
def find_human_handoffs(ctx: ToolContext, handoff_id: str = "", customer_id: str = "") -> str:
    """Look up transfers of a customer to a human representative, with the reason and time of each. Search by
    either reference number; at least one is needed.

    Args:
        handoff_id: The handoff record reference number; leave "" if unknown.
        customer_id: The customer reference number; leave "" if unknown.
    """
    match = _criteria(handoff_id=handoff_id, customer_id=customer_id)
    if not match:
        return "Error: provide at least one reference number."
    rows = ctx.find("human_handoffs", **match)
    return str(rows) if rows else f"No handoffs on record for {match}."


# --------------------------------------------------------------------------- verification
def _digits(value: str) -> str:
    return "".join(ch for ch in str(value or "") if ch.isdigit())


@tool(owner="agent", rw="write")
def verify_customer_identity(ctx: ToolContext, customer_id: str, phone_number: str = "", email: str = "",
                             date_of_birth: str = "", ssn_last4: str = "", residential_zip: str = "") -> str:
    """Verify the caller's identity against their Kestrel Auto profile and record the outcome. Identity must be
    verified before any account information is discussed or any order, contract, payment, refund or document is
    acted on.

    This tool makes the comparison itself: it checks each piece of identity information the caller gives against
    the profile, counts how many match, and verifies the caller only when at least 3 match. The customer reference
    number only tells the tool which profile to check and never counts as a match. Callers usually know only some
    of these details, so pass exactly what the caller said and leave the rest empty. If a first attempt falls short
    and a later attempt with more details succeeds, the caller stands verified; a verification once passed is never
    undone.

    Args:
        customer_id: The customer reference number from the customer profile lookup. Required.
        phone_number: The mobile number the caller states, 10 digits; leave "" if not stated.
        email: The email address the caller states; leave "" if not stated.
        date_of_birth: The caller's date of birth as YYYY-MM-DD; leave "" if not stated.
        ssn_last4: The last four digits of the caller's Social Security number; leave "" if not stated.
        residential_zip: The 5-digit ZIP code of the caller's home address; leave "" if not stated.
    """
    if not customer_id:
        return "Error: customer_id is required; look up the customer profile first."
    rows = ctx.find("customers", customer_id=customer_id)
    if not rows:
        return f"Error: no customer profile {customer_id}; cannot verify."
    rec = rows[0]
    # The tool owns the comparison; customer_id is the locator and never counts as a credential.
    checks = [
        (phone_number, lambda v: _digits(v) != "" and _digits(v) == _digits(rec.get("phone_number"))),
        (email, lambda v: str(v).strip().lower() == str(rec.get("email") or "").strip().lower()),
        (date_of_birth, lambda v: str(v).strip() == str(rec.get("date_of_birth") or "").strip()),
        (ssn_last4, lambda v: _digits(v) != "" and _digits(v) == _digits(rec.get("ssn_last4"))),
        (residential_zip, lambda v: _digits(v) != "" and _digits(v) == _digits(rec.get("residential_zip"))),
    ]
    matched = sum(1 for value, ok in checks if value and ok(value))
    verified = matched >= 3
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
        return f"Identity verified for customer {customer_id} ({matched} detail(s) matched on this attempt)."
    return (f"Identity NOT verified for customer {customer_id}: only {matched} of the required 3 details matched. "
            "Ask the caller for another detail on the profile and try again.")


# --------------------------------------------------------------------------- handoff
@tool(owner="agent", rw="write")
def transfer_to_human_agent(ctx: ToolContext, customer_id: str, reason: str) -> str:
    """Transfer the customer to a human Kestrel Auto representative and record the transfer and its reason.

    Use it in one of two situations only: when no Kestrel policy lets you resolve what the customer is asking for,
    or when the customer has explicitly asked to speak with a human representative 2 times.

    Args:
        customer_id: The customer reference number from the customer profile lookup.
        reason: Why the customer is being transferred; exactly one of POLICY_NOT_COVERED (no policy resolves the request) or CUSTOMER_REQUESTED (the customer has explicitly asked for a human representative at least 2 times).
    """
    allowed = {"POLICY_NOT_COVERED", "CUSTOMER_REQUESTED"}
    if reason not in allowed:
        return f"Error: unknown transfer reason '{reason}'. Valid: {', '.join(sorted(allowed))}."
    if not ctx.find("customers", customer_id=customer_id):
        return f"Error: no customer profile {customer_id}; cannot record the transfer."
    rid = ctx.make_id("hof_", customer_id, reason)
    ctx.create("human_handoffs", rid, handoff_id=rid, customer_id=customer_id, reason=reason,
               created_at=ctx.now())
    return f"Transfer to a human representative recorded for customer {customer_id} ({reason})."

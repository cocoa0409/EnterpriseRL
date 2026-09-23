"""Hidden task tools for the service_dispatch_desk difficulty of
Halvorsen Mechanical & Controls, Inc. (category: service).

Each function lands one atomic change on the demand service records. None of them
aggregates the ledger, prices anything or judges whether the company's terms allow the
write: the desk works the figure out from the published terms and the records, and passes
it in. The tools are hidden — their names reach the agent only through the published
demand service terms, and they are run through the unlock/call pair.
"""

from erlbench import ToolContext, tool


@tool(owner="agent", rw="write")
def charge_demand_labor_invoice_877d69f1(ctx: ToolContext, program_id: str,
                                         work_order_ref: str,
                                         labor_charge_usd: float) -> str:
    """Put the technician labor for one closed demand service call on the owner's account as an
    invoiced labor line against the rate program. One call books exactly one labor line: a new
    demand service charge entry of the labor kind is opened on the program, carrying the work
    order the labor was worked under, the money amount billed for that labor and the billing
    month it falls in, and from that moment the owner owes that amount on the demand service
    account and can see the labor line on the work order. The call has completed when the
    confirmation names the new charge entry and the amount that was billed.

    Args:
        program_id: Id class — the reference number of the demand service rate program the
            labor is billed under, read from the rate program lookup on the account.
        work_order_ref: Fixed-format class — the work order number the labor was worked under,
            written as WO- followed by 7 digits, exactly as it stands on the call record in the
            demand service history.
        labor_charge_usd: Fixed-format class — the money amount billed for the technician labor
            on that work order, in USD to 2 decimal places, rounded half up at the cent and
            never negative.

    Returns:
        A confirmation line of plain text. It carries the reference number of the new demand
        service charge entry, the work order number the labor line was raised against and the
        amount in USD to 2 decimal places that now stands on the owner's demand service
        account. A line that names the charge entry reference is the receipt that the labor
        line was booked.
    """
    rid = ctx.make_id("sevt_", program_id, work_order_ref, labor_charge_usd)
    rows = ctx.find("service_programs", program_id=program_id)
    customer_id = rows[0].get("customer_id") if rows else ""
    ctx.create("service_events", rid, event_id=rid, program_id=program_id,
               customer_id=customer_id, event_type="service_invoice_charged",
               charge_type="labor", work_order_ref=work_order_ref,
               amount_usd=round(float(labor_charge_usd), 2),
               billing_period=ctx.now()[:7], due_date="")
    return (f"Labor line {rid} raised on work order {work_order_ref} for "
            f"{round(float(labor_charge_usd), 2):.2f} USD.")


@tool(owner="agent", rw="write")
def charge_overdue_late_fee_58988cf8(ctx: ToolContext, program_id: str,
                                     late_fee_amount_usd: float) -> str:
    """Put this month's late fee for overdue demand service invoicing on the owner's account as
    one charge line against the rate program. A single call opens exactly one demand service
    charge entry of the late fee kind on the program, carrying the money amount of the fee and
    the billing month it belongs to, so the owner owes that fee on the demand service account
    and sees it as its own line rather than buried in another charge. The call has completed
    when the confirmation names the new charge entry and the fee amount it carries.

    Args:
        program_id: Id class — the reference number of the demand service rate program the fee
            is charged against, read from the rate program lookup on the account.
        late_fee_amount_usd: Fixed-format class — the money amount of the late fee charged, in
            USD to 2 decimal places, rounded half up at the cent and never negative.

    Returns:
        A confirmation line of plain text naming the reference number of the new demand service
        charge entry, the billing month the fee belongs to and the fee amount in USD to 2
        decimal places now standing on the owner's demand service account. The named charge
        entry reference is the receipt that the fee line was booked.
    """
    rid = ctx.make_id("sevt_", program_id, late_fee_amount_usd)
    rows = ctx.find("service_programs", program_id=program_id)
    customer_id = rows[0].get("customer_id") if rows else ""
    ctx.create("service_events", rid, event_id=rid, program_id=program_id,
               customer_id=customer_id, event_type="service_invoice_charged",
               charge_type="late_fee", amount_usd=round(float(late_fee_amount_usd), 2),
               billing_period=ctx.now()[:7], due_date="")
    return (f"Late fee line {rid} raised for billing period {ctx.now()[:7]} at "
            f"{round(float(late_fee_amount_usd), 2):.2f} USD.")


@tool(owner="agent", rw="write")
def credit_missed_response_9859bc76(ctx: ToolContext, program_id: str, work_order_ref: str,
                                    credit_amount_usd: float) -> str:
    """Give the owner money back on the demand service account for a response commitment that
    was not kept on one call. One call opens exactly one demand service credit entry on the
    rate program, marked as a missed response credit, carrying the work order of the call it
    arises from, the money amount credited and the day it was issued; that amount comes off
    what the owner owes on the demand service account and shows on the work order as a credit.
    The call has completed when the confirmation names the new credit entry and its amount.

    Args:
        program_id: Id class — the reference number of the demand service rate program the
            credit is issued on, read from the rate program lookup on the account.
        work_order_ref: Fixed-format class — the work order number of the call the credit
            arises from, written as WO- followed by 7 digits, exactly as it stands on the call
            record in the demand service history.
        credit_amount_usd: Fixed-format class — the money amount credited to the owner, in USD
            to 2 decimal places, rounded half up at the cent and never negative.

    Returns:
        A confirmation line of plain text naming the reference number of the new demand service
        credit entry, the work order it was issued against and the credited amount in USD to 2
        decimal places. The named credit entry reference is the receipt that the credit was
        issued.
    """
    rid = ctx.make_id("sevt_", program_id, work_order_ref, credit_amount_usd)
    rows = ctx.find("service_programs", program_id=program_id)
    customer_id = rows[0].get("customer_id") if rows else ""
    ctx.create("service_events", rid, event_id=rid, program_id=program_id,
               customer_id=customer_id, event_type="service_credit_issued",
               credit_reason="missed_response", work_order_ref=work_order_ref,
               amount_usd=round(float(credit_amount_usd), 2),
               issued_date=ctx.now()[:10])
    return (f"Credit entry {rid} issued on work order {work_order_ref} for "
            f"{round(float(credit_amount_usd), 2):.2f} USD.")


@tool(owner="user", rw="write")
def record_account_payment_d97a44a1(ctx: ToolContext, program_id: str, payment_amount_usd: float,
                                    payment_method: str) -> str:
    """Pay money off the demand service account yourself as the building owner. One call opens
    exactly one payment entry on the rate program, carrying the money amount paid, how it was
    paid and the day the office received it, and that amount comes off what is owed on the
    demand service account straight away. The call has completed when the confirmation names
    the new payment entry, the amount taken and the way it was paid.

    Args:
        program_id: Id class — the reference number of the demand service rate program the
            money is paid against, as the desk states it when handing this over.
        payment_amount_usd: Fixed-format class — the money amount paid, in USD to 2 decimal
            places, rounded half up at the cent and never negative.
        payment_method: Enum class — how the money is paid, one of exactly four values.
            check — a paper cheque is being sent or handed to the office; ach — the money is
            pushed from the owner's bank account by direct debit or bank transfer through the
            clearing system; credit_card — a company credit or debit card is being charged on
            the spot; wire — the money is sent as a same-day bank wire.

    Returns:
        A confirmation line of plain text naming the reference number of the new payment entry,
        the amount paid in USD to 2 decimal places and the way it was paid. The named payment
        entry reference is the receipt that the money was taken.
    """
    rid = ctx.make_id("sevt_", program_id, payment_amount_usd, payment_method)
    rows = ctx.find("service_programs", program_id=program_id)
    customer_id = rows[0].get("customer_id") if rows else ""
    ctx.create("service_events", rid, event_id=rid, program_id=program_id,
               customer_id=customer_id, event_type="service_payment_received",
               amount_usd=round(float(payment_amount_usd), 2),
               payment_method=payment_method, received_date=ctx.now()[:10])
    return (f"Payment entry {rid} recorded for {round(float(payment_amount_usd), 2):.2f} USD "
            f"by {payment_method}.")


@tool(owner="agent", rw="write")
def set_program_credit_ceiling_aca954d3(ctx: ToolContext, program_id: str,
                                        credit_limit_usd: float) -> str:
    """Write a reviewed open balance ceiling onto the demand service rate program. One call changes
    exactly one term of the live program: the ceiling above which further work on the account waits for
    an office release is replaced by the figure given, the program is stamped as having had its credit
    ceiling changed, and the day of the change is recorded, so from that moment the account's headroom
    is measured against the new ceiling and the owner sees the new ceiling on the program. The call has
    completed when the confirmation names the program and the ceiling now standing on it.

    Args:
        program_id: Id class — the reference number of the demand service rate program whose ceiling is
            being written, read from the rate program lookup on the account.
        credit_limit_usd: Fixed-format class — the open balance ceiling to stand on the program, in USD
            to 2 decimal places, rounded half up at the cent and never negative.

    Returns:
        A confirmation line of plain text naming the rate program reference, the ceiling now standing on
        it in USD to 2 decimal places and the day the change took effect. A line naming the new ceiling
        is the receipt that the program term was changed.
    """
    ctx.update("service_programs", program_id,
               credit_limit_usd=round(float(credit_limit_usd), 2),
               last_change_type="credit_limit_changed", last_change_date=ctx.now()[:10])
    return (f"Rate program {program_id} now carries an open balance ceiling of "
            f"{round(float(credit_limit_usd), 2):.2f} USD, changed {ctx.now()[:10]}.")


@tool(owner="user", rw="write")
def purchase_hour_block_a465dc68(ctx: ToolContext, program_id: str, block_hours: float,
                                 purchase_amount_usd: float) -> str:
    """Buy a block of prepaid technician hours on the demand service rate program yourself, as the
    building owner. One call opens exactly one block purchase entry on the program, carrying the hours
    bought, the day they were bought and the price paid; the hours are credited to the program's prepaid
    balance and can be drawn by later calls, and the price stands as the amount for that purchase. The
    call has completed when the confirmation names the new purchase entry, the hours credited and the
    price.

    Args:
        program_id: Id class — the reference number of the demand service rate program the hours are
            credited to, as the desk states it when handing this over.
        block_hours: Fixed-format class — the quantity of prepaid technician hours bought, in decimal
            hours to 1 decimal place, never negative.
        purchase_amount_usd: Fixed-format class — the price paid for the block, in USD to 2 decimal
            places, rounded half up at the cent and never negative.

    Returns:
        A confirmation line of plain text naming the reference number of the new block purchase entry,
        the hours credited in decimal hours to 1 decimal place and the price in USD to 2 decimal places.
        The named purchase entry reference is the receipt that the hours were credited.
    """
    rid = ctx.make_id("sevt_", program_id, block_hours, purchase_amount_usd)
    rows = ctx.find("service_programs", program_id=program_id)
    customer_id = rows[0].get("customer_id") if rows else ""
    ctx.create("service_events", rid, event_id=rid, program_id=program_id,
               customer_id=customer_id, event_type="service_block_hours_purchased",
               block_hours=round(float(block_hours), 1),
               amount_usd=round(float(purchase_amount_usd), 2), purchased_date=ctx.now()[:10])
    return (f"Block purchase {rid} recorded: {round(float(block_hours), 1):.1f} hours credited for "
            f"{round(float(purchase_amount_usd), 2):.2f} USD.")

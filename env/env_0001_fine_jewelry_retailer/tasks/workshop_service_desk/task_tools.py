"""Hidden task tools for the Belrose workshop service desk.

Each function lands one atomic write on the workshop's own records. None of them
reads policy, aggregates history or judges whether a write may be made: the desk
agent works the figure out from the published rules and the records first, then
passes it in. The tools are not listed anywhere; their names reach an agent only
through the workshop's published policy, and they are reached through the
unlock/call pair.
"""

from erlbench import ToolContext, tool


@tool(owner="agent", rw="write")
def apply_claim_coverage_f28c459e(ctx: ToolContext, service_order_id: str, customer_id: str,
                                  protection_claim_reference: str, source_entry_id: str,
                                  covered_amount: float) -> str:
    """Take the amount a protection claim answers for off a bench work order.

    One call books a single credit entry against the named work order, recorded under the
    claim that answered and pointed at the one priced line it answers for. The credit is
    written as a negative movement on the order, so what the customer still owes on the
    order falls by that amount the moment the entry lands, and the entry is stamped with
    today's date and accounting period. The customer sees the amount come off their bench
    bill and the claim reference printed beside it. The call has done its work when the
    confirmation names the new credit entry and the amount taken off.

    Args:
        service_order_id: Id class — the reference number of the bench work order record the credit is booked to, as returned by the work order lookup.
        customer_id: Id class — the reference number of the customer profile the work order belongs to, as returned by the customer profile lookup.
        protection_claim_reference: Fixed-format class — the claim the amount is recorded under, written as CL- followed by six digits, e.g. CL-330871; upper case, no spaces, copied exactly as it stands on the records that carry it.
        source_entry_id: Id class — the reference number of the single priced line on that work order this credit answers for, as returned by the work order entry lookup.
        covered_amount: Fixed-format class — the amount the claim answers for, as a positive figure in USD, 2 decimal places, rounded half to even at the cent and never signed; the tool books it as a credit itself.

    Returns:
        A one-line confirmation string naming the new credit entry's reference number, the
        work order it was booked to, the claim reference it was recorded under and the
        amount taken off in USD to two decimal places. A returned line that names the entry
        reference is the receipt that the credit now stands on the order.
    """
    rid = ctx.make_id("sle_", service_order_id, customer_id, protection_claim_reference,
                      source_entry_id, covered_amount)
    amount = -round(float(covered_amount), 2)
    ctx.create("service_ledger", rid, service_entry_id=rid, service_order_id=service_order_id,
               customer_id=customer_id, event_type="service_coverage_applied",
               posted_date=ctx.now()[:10], amount=amount, charge_code="not_applicable",
               service_task="not_applicable", quantity=1, unit_price=0.0,
               payment_channel="not_applicable",
               protection_claim_reference=protection_claim_reference,
               discount_reason_code="protection_plan_covered",
               quality_check_result="not_applicable", technician_code="",
               billing_period=ctx.now()[:7], source_entry_id=source_entry_id)
    return (f"Coverage entry {rid} booked to work order {service_order_id} under claim "
            f"{protection_claim_reference}: {round(float(covered_amount), 2):.2f} USD taken off.")


@tool(owner="user", rw="write")
def confirm_authorized_ceiling_b1b9df84(ctx: ToolContext, service_order_id: str, customer_id: str,
                                        authorized_ceiling: float) -> str:
    """Commit in person to the figure the bench may run a work order up to.

    One call puts a confirmed authorisation on the workshop desk's request record for the
    named work order, carrying the ceiling agreed and taking effect from today. The record
    is written as an authorisation the customer has confirmed rather than one merely taken
    down, so the ceiling standing on the request record becomes the figure the bench works
    to from that moment. The customer can see the figure they agreed and the date it runs
    from on their own copy of the request. The call has done its work when the confirmation
    names the new request record and the figure agreed.

    Args:
        service_order_id: Id class — the reference number of the bench work order record the authorisation is given on, as returned by the work order lookup.
        customer_id: Id class — the reference number of the customer profile giving the authorisation, as returned by the customer profile lookup.
        authorized_ceiling: Fixed-format class — the figure being agreed as the ceiling, in USD, 2 decimal places, rounded half to even at the cent, always positive and never abbreviated to whole dollars.

    Returns:
        A one-line confirmation string naming the new request record's reference number, the
        work order it was taken on, the ceiling agreed in USD to two decimal places and the
        date it takes effect from. A returned line naming the request reference is the
        receipt that the confirmed authorisation now stands.
    """
    rid = ctx.make_id("sir_", service_order_id, customer_id, authorized_ceiling)
    ctx.create("service_intake", rid, service_request_id=rid, customer_id=customer_id,
               service_order_id=service_order_id, request_type="estimate_authorization",
               request_status="customer_confirmed",
               authorized_amount=round(float(authorized_ceiling), 2),
               effective_date=ctx.now()[:10], created_at=ctx.now())
    return (f"Authorisation {rid} confirmed on work order {service_order_id}: ceiling "
            f"{round(float(authorized_ceiling), 2):.2f} USD effective {ctx.now()[:10]}.")


@tool(owner="agent", rw="write")
def charge_expedite_surcharge_af83d9eb(ctx: ToolContext, service_order_id: str, customer_id: str,
                                       surcharge_amount: float) -> str:
    """Price the charge for expedited handling onto a bench work order.

    One call books a single expedited-handling line against the named work order under the
    rush charge code, stamped with today's date and accounting period. The line is written
    as a positive movement, so what the customer owes on the order rises by that amount as
    soon as it lands, and the piece is thereafter handled on the shortened promise the
    charge pays for. The customer sees the expedited line on their bench bill alongside the
    priced work. The call has done its work when the confirmation names the new line and
    the amount charged.

    Args:
        service_order_id: Id class — the reference number of the bench work order record the expedited line is charged to, as returned by the work order lookup.
        customer_id: Id class — the reference number of the customer profile the work order belongs to, as returned by the customer profile lookup.
        surcharge_amount: Fixed-format class — the charge for handling the piece ahead of the queue, as a positive figure in USD, 2 decimal places, rounded half to even at the cent.

    Returns:
        A one-line confirmation string naming the new priced line's reference number, the
        work order it was charged to and the amount charged in USD to two decimal places. A
        returned line naming the entry reference is the receipt that the expedited charge
        now stands on the order.
    """
    rid = ctx.make_id("sle_", service_order_id, customer_id, surcharge_amount)
    ctx.create("service_ledger", rid, service_entry_id=rid, service_order_id=service_order_id,
               customer_id=customer_id, event_type="service_rush_fee_charged",
               posted_date=ctx.now()[:10], amount=round(float(surcharge_amount), 2),
               charge_code="rush_surcharge", service_task="not_applicable", quantity=1,
               unit_price=0.0, payment_channel="not_applicable", protection_claim_reference="",
               discount_reason_code="not_applicable", quality_check_result="not_applicable",
               technician_code="", billing_period=ctx.now()[:7], source_entry_id="")
    return (f"Expedited handling line {rid} charged to work order {service_order_id}: "
            f"{round(float(surcharge_amount), 2):.2f} USD.")


@tool(owner="user", rw="write")
def confirm_stone_release_3a8d360e(ctx: ToolContext, service_order_id: str, customer_id: str,
                                   carried_value: float) -> str:
    """Sign in person the release the workshop needs for handling a piece, naming the value it is held at.

    One call marks the release as signed on the named work order and writes onto that same order
    the value the piece is held at while the chain has it, replacing whatever figure was taken
    down over the counter. The order thereafter shows a signed release and the agreed figure, and
    the customer can see both on their own copy of the work order. The call has done its work when
    the confirmation names the work order and repeats the figure now standing on it.

    Args:
        service_order_id: Id class — the reference number of the bench work order record the release is signed against, as returned by the work order lookup.
        customer_id: Id class — the reference number of the customer profile signing the release, as returned by the customer profile lookup.
        carried_value: Fixed-format class — the value the piece is held at while the chain has it, in USD, 2 decimal places, rounded half to even at the cent, always positive and never abbreviated to whole dollars.

    Returns:
        A one-line confirmation string naming the work order the release was signed against and the
        value now standing on it in USD to two decimal places. A returned line that repeats that
        figure is the receipt that the release stands signed and the order carries the agreed value.
    """
    value = round(float(carried_value), 2)
    ctx.update("service_orders", service_order_id, stone_release_signed=True, declared_value=value)
    return (f"Release signed on work order {service_order_id} by {customer_id}: the piece is now "
            f"held at {value:.2f} USD while the chain has it.")


@tool(owner="agent", rw="write")
def charge_insured_shipping_16f801d8(ctx: ToolContext, service_order_id: str, customer_id: str,
                                     work_order_reference: str, shipping_amount: float) -> str:
    """Price an insured postage leg for a piece onto a bench work order.

    One call books a single insured-shipping line against the named work order under the insured
    shipping charge code, stamped with today's date and accounting period, and written as a
    positive movement so what the customer owes on the order rises by that amount at once. From
    that point the piece is set to travel insured to the customer rather than be collected over the
    counter, and the customer sees the postage line on their bench bill. The call has done its work
    when the confirmation names the new line and the amount charged.

    Args:
        service_order_id: Id class — the reference number of the bench work order record the postage line is charged to, as returned by the work order lookup.
        customer_id: Id class — the reference number of the customer profile the work order belongs to, as returned by the customer profile lookup.
        work_order_reference: Fixed-format class — the reference the customer is given for the work order the postage line is raised against, written as WO- followed by six digits, e.g. WO-772140; upper case, no spaces, copied exactly as it stands on the work order.
        shipping_amount: Fixed-format class — the charge for sending the piece insured, as a positive figure in USD, 2 decimal places, rounded half to even at the cent.

    Returns:
        A one-line confirmation string naming the new priced line's reference number, the work order
        reference it was raised against and the amount charged in USD to two decimal places. A returned line
        naming the entry reference is the receipt that the postage charge now stands on the order.
    """
    rid = ctx.make_id("sle_", service_order_id, customer_id, work_order_reference, shipping_amount)
    ctx.create("service_ledger", rid, service_entry_id=rid, service_order_id=service_order_id,
               customer_id=customer_id, event_type="service_shipping_charged",
               posted_date=ctx.now()[:10], amount=round(float(shipping_amount), 2),
               charge_code="shipping_insured", service_task="not_applicable", quantity=1,
               unit_price=0.0, payment_channel="not_applicable", protection_claim_reference="",
               discount_reason_code="not_applicable", quality_check_result="not_applicable",
               technician_code="", billing_period=ctx.now()[:7], source_entry_id="")
    return (f"Insured postage line {rid} charged to work order {work_order_reference}: "
            f"{round(float(shipping_amount), 2):.2f} USD.")

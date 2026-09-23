"""Hidden task tools for the catering order desk of Larkspur Table Workplace Dining Group.

Each tool performs one atomic write on the corporate catering records. None of them
aggregates history, derives an amount or judges whether the policy admits the write:
the figures are worked out by the agent from the published catering rules and the
records, and arrive here as ordinary arguments.
"""

from erlbench import ToolContext, tool


@tool(owner="agent", rw="write")
def raise_catering_invoice_cb57dc9d(ctx: ToolContext, catering_agreement_id: str, customer_id: str,
                                    order_reference: str, service_date: str,
                                    invoice_amount_usd: float) -> str:
    """Bill a catering order that has been served. One call raises the invoice for that single
    order on the client's corporate catering service agreement: an invoice entry is written into
    the agreement's order history against the order reference given, carrying the amount billed
    and the service day it covers, and the agreement's unsettled catering balance is increased by
    that same amount. The client sees the order on their next statement as an invoice awaiting
    payment, and the invoice number the entry was filed under is confirmed back on success.

    Args:
        catering_agreement_id: Id class — the reference number of the corporate catering service
            agreement being billed, as returned by the catering agreement lookup.
        customer_id: Id class — the reference number of the client organisation profile the
            agreement belongs to, as returned by the dining profile lookup.
        order_reference: Fixed-format class — the catering order being billed, written as the
            order reference it carries throughout its history, in the form CO- followed by 6 digits.
        service_date: Fixed-format class — the day the catering was served, written as YYYY-MM-DD
            in the site's own calendar; it is never left empty.
        invoice_amount_usd: Fixed-format class — the amount billed for this order, in USD, to 2
            decimal places, rounded half to even at the point it is booked and never carried to a
            finer precision; no time zone applies and it is never left empty.

    Returns:
        A confirmation sentence naming the invoice number the entry was filed under, the order
        reference billed and the amount booked in USD to two decimal places. The presence of the
        invoice number in the sentence is what indicates the invoice was raised; afterwards the
        order history shows one further invoice entry and the agreement's unsettled catering
        balance stands higher by the amount booked.
    """
    amount = round(float(invoice_amount_usd), 2)
    rid = ctx.make_id("cti_", catering_agreement_id, customer_id, order_reference, service_date, amount)
    inv_ref = "INV-CT-" + str(int(rid[-6:], 16) % 1000000).zfill(6)
    ctx.create("catering_orders", rid,
               catering_order_id=rid,
               catering_agreement_id=catering_agreement_id,
               customer_id=customer_id,
               event_type="catering_order_invoiced",
               order_reference=order_reference,
               charge_code="invoice",
               amount_usd=amount,
               posted_date=ctx.now()[:10],
               service_date=service_date,
               invoice_reference=inv_ref,
               payment_channel="not_applicable")
    rows = ctx.find("catering_agreements", catering_agreement_id=catering_agreement_id)
    if rows:
        ctx.update("catering_agreements", catering_agreement_id,
                   receivable_balance_usd=round(float(rows[0].get("receivable_balance_usd") or 0) + amount, 2))
    return f"Invoice {inv_ref} raised for catering order {order_reference}: {amount:.2f} USD billed."


@tool(owner="user", rw="write")
def confirm_agreement_closure_1e20ba9d(ctx: ToolContext, catering_agreement_id: str,
                                       closing_settlement_usd: float) -> str:
    """End your own corporate catering service agreement and accept the figure it closes on. One
    call by the client closes the named agreement: its state becomes closed, the day it closed is
    stamped on it, no further catering orders are taken under it, and the amount left standing on
    it to settle is set to the figure confirmed here, which is what the final catering statement
    will ask for. The client sees the agreement marked closed with that closing figure against it,
    and the closing day is confirmed back on success.

    Args:
        catering_agreement_id: Id class — the reference number of the corporate catering service
            agreement the client is ending, as the desk reads it off the client's agreement record.
        closing_settlement_usd: Fixed-format class — the figure the agreement closes on, in USD, to
            2 decimal places, rounded half to even at the point it is booked and never carried to a
            finer precision; no time zone applies and it is never left empty.

    Returns:
        A confirmation sentence naming the agreement reference that was closed, the day it closed
        written as YYYY-MM-DD, and the closing figure in USD to two decimal places. The presence of
        the closing day in the sentence is what indicates the agreement is closed; afterwards the
        agreement reads as closed and shows that figure as the amount left to settle.
    """
    amount = round(float(closing_settlement_usd), 2)
    closed_on = ctx.now()[:10]
    ctx.update("catering_agreements", catering_agreement_id,
               status="closed",
               closed_date=closed_on,
               receivable_balance_usd=amount)
    return (f"Catering agreement {catering_agreement_id} closed on {closed_on}; "
            f"closing figure {amount:.2f} USD left to settle.")


@tool(owner="user", rw="write")
def register_order_cancellation_69ffeeb0(ctx: ToolContext, catering_agreement_id: str, customer_id: str,
                                         order_reference: str, service_date: str, headcount: int,
                                         order_channel: str, standing_order_value_usd: float) -> str:
    """Pull your own catering order off the kitchen's list. One call by the client registers the
    cancellation of that single order on their corporate catering service agreement: a cancellation
    entry is written into the agreement's order history against the order reference given, stamped
    with today as the day notice was given, and carrying the guest count the order stood on, the day
    it was to have been served and the value it held at that moment. The kitchen stops work on it and
    the client sees the order struck from the agreement with that value recorded against it; the
    reference the cancellation was filed under is confirmed back on success.

    Args:
        catering_agreement_id: Id class — the reference number of the corporate catering service
            agreement the order sits under, as the desk reads it off the client's agreement record.
        customer_id: Id class — the reference number of the client organisation profile the agreement
            belongs to, as the desk reads it off the client's dining profile.
        order_reference: Fixed-format class — the catering order being pulled, written as the order
            reference it carries throughout its history, in the form CO- followed by 6 digits.
        service_date: Fixed-format class — the day the catering was to have been served, written as
            YYYY-MM-DD in the site's own calendar; it is never left empty.
        headcount: Fixed-format class — the guest count the order stood on when it was pulled, as a
            whole number of guests, an integer with no decimal part and never left empty.
        order_channel: Enum class — the route by which this cancellation instruction reached Larkspur
            Table, which is a fact about how the client passed the instruction on rather than about the
            medium of any one conversation. online_portal when the client entered the instruction
            themselves in the client ordering portal; account_manager when the client gave the
            instruction to the named catering account manager looking after them rather than to the
            client services desk; phone when the client spoke the instruction to the client services
            desk on the telephone and passed it through no one else; email when the client sent the
            instruction in writing to the desk's mailbox.
        standing_order_value_usd: Fixed-format class — the value the order held at the moment notice
            was given, in USD, to 2 decimal places, rounded half to even at the point it is booked and
            never carried to a finer precision; no time zone applies and it is never left empty.

    Returns:
        A confirmation sentence naming the cancellation reference the entry was filed under, the order
        reference pulled, the day notice was given written as YYYY-MM-DD and the value recorded in USD
        to two decimal places. The presence of the cancellation reference is what indicates the
        cancellation was registered; afterwards the order history shows one further cancellation entry
        against that order.
    """
    amount = round(float(standing_order_value_usd), 2)
    guests = int(headcount)
    notice_on = ctx.now()[:10]
    rid = ctx.make_id("ctx_", catering_agreement_id, customer_id, order_reference, service_date,
                      guests, order_channel, amount)
    ctx.create("catering_orders", rid,
               catering_order_id=rid,
               catering_agreement_id=catering_agreement_id,
               customer_id=customer_id,
               event_type="catering_order_cancelled",
               order_reference=order_reference,
               charge_code="cancellation_fee",
               amount_usd=amount,
               posted_date=notice_on,
               service_date=service_date,
               headcount=guests,
               notice_given_date=notice_on,
               order_channel=order_channel,
               payment_channel="not_applicable")
    return (f"Cancellation {rid} registered for catering order {order_reference} on {notice_on}; "
            f"value recorded {amount:.2f} USD.")


@tool(owner="agent", rw="write")
def post_cancellation_charge_b7aa0639(ctx: ToolContext, catering_agreement_id: str, customer_id: str,
                                      order_reference: str, service_date: str,
                                      cancellation_charge_usd: float) -> str:
    """Raise the charge that a pulled catering order carries. One call books the cancellation charge
    for that single order on the client's corporate catering service agreement: a charge entry is
    written into the agreement's order history against the order reference given, stamped with today
    as the day notice was given and with the day the catering was to have been served, and the
    agreement's unsettled catering balance is increased by the amount charged. The client sees the
    charge on their next statement, and the invoice number it was filed under is confirmed back on
    success.

    Args:
        catering_agreement_id: Id class — the reference number of the corporate catering service
            agreement being charged, as returned by the catering agreement lookup.
        customer_id: Id class — the reference number of the client organisation profile the agreement
            belongs to, as returned by the dining profile lookup.
        order_reference: Fixed-format class — the pulled catering order the charge answers, written as
            the order reference it carries throughout its history, in the form CO- followed by 6 digits.
        service_date: Fixed-format class — the day the catering was to have been served, written as
            YYYY-MM-DD in the site's own calendar; it is never left empty.
        cancellation_charge_usd: Fixed-format class — the amount charged for the cancellation, in USD,
            to 2 decimal places, rounded half to even at the point it is booked and never carried to a
            finer precision; no time zone applies and it is never left empty.

    Returns:
        A confirmation sentence naming the invoice number the charge was filed under, the order
        reference charged and the amount booked in USD to two decimal places. The presence of the
        invoice number is what indicates the charge was raised; afterwards the order history shows one
        further cancellation charge entry and the agreement's unsettled catering balance stands higher
        by the amount booked.
    """
    amount = round(float(cancellation_charge_usd), 2)
    rid = ctx.make_id("ctc_", catering_agreement_id, customer_id, order_reference, service_date, amount)
    inv_ref = "INV-CT-" + str(int(rid[-6:], 16) % 1000000).zfill(6)
    ctx.create("catering_orders", rid,
               catering_order_id=rid,
               catering_agreement_id=catering_agreement_id,
               customer_id=customer_id,
               event_type="catering_cancellation_fee_posted",
               order_reference=order_reference,
               charge_code="cancellation_fee",
               amount_usd=amount,
               posted_date=ctx.now()[:10],
               service_date=service_date,
               notice_given_date=ctx.now()[:10],
               invoice_reference=inv_ref,
               payment_channel="not_applicable")
    rows = ctx.find("catering_agreements", catering_agreement_id=catering_agreement_id)
    if rows:
        ctx.update("catering_agreements", catering_agreement_id,
                   receivable_balance_usd=round(float(rows[0].get("receivable_balance_usd") or 0) + amount, 2))
    return f"Cancellation charge filed under {inv_ref} for catering order {order_reference}: {amount:.2f} USD."

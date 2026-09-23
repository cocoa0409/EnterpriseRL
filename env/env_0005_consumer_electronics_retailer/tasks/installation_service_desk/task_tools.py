"""Hidden task tools for the Northbeam TechWorks installation and repair desk.

Each function lands exactly one atomic entry on a TechWorks job and keeps that job's running
quantity in step with it. None of them works out an amount, a rate, a window or an entitlement:
the agent reads the job, its history, the customer's other Northbeam lines and the published
rules, works the figure out itself, and passes it in. They are reached only through the
unlock/call pair, never listed directly.
"""

from erlbench import ToolContext, tool


@tool(owner="agent", rw="write")
def bill_out_of_hours_surcharge_9a215bff(ctx: ToolContext, service_agreement_id: str, customer_id: str,
                                         work_order_line_reference: str, visit_date: str,
                                         surcharge_amount: float) -> str:
    """Bill the surcharge that an attendance carried out outside ordinary service hours adds to a
    TechWorks job, against the line of work that attendance belongs to.

    One call books one surcharge entry on that job for that attendance and raises the job's
    outstanding service charges by the amount booked, so the customer's next statement of the job
    shows the surcharge alongside the labour it was worked out from. The entry is dated the day it
    is booked and is taken as a telephone entry. On success the job carries one more charge and a
    higher outstanding figure, and the customer can be told the surcharge is now on the bill.

    Args:
        service_agreement_id: Id class — the reference number of the TechWorks work order or care
            agreement the surcharge belongs to, read from the work orders held on the customer's
            profile before the call.
        customer_id: Id class — the reference number of the customer profile being billed, read
            from that profile before the call.
        work_order_line_reference: Id class — the reference number of the single line of work the
            surcharge is settled against, read from the entries already booked on that job before
            the call.
        visit_date: Fixed-format class — the day the attendance the surcharge arose on took place,
            as YYYY-MM-DD, in the retailer's own local calendar; never left empty.
        surcharge_amount: Fixed-format class — the surcharge to bill, in USD to 2 decimal places,
            rounded half up to the cent before it is passed; pass the figure itself and never a
            rate or a percentage.

    Returns:
        A one-line confirmation string naming the surcharge entry reference that was created, the
        job it was booked on, the amount booked in USD to two decimal places and the job's new
        outstanding service charges in USD to two decimal places. The presence of that entry
        reference in the reply is what shows the surcharge was booked.
    """
    rid = ctx.make_id("sev_", service_agreement_id, customer_id, work_order_line_reference,
                      visit_date, surcharge_amount)
    ctx.create("service_events", rid, service_event_id=rid,
               service_agreement_id=service_agreement_id, customer_id=customer_id,
               event_type="service_fee_charge", charge_kind="after_hours_surcharge",
               charge_amount=round(float(surcharge_amount), 2), visit_date=visit_date,
               event_date=ctx.now()[:10], work_order_line_reference=work_order_line_reference,
               channel="phone")
    booked = round(float(surcharge_amount), 2)
    rows = ctx.find("service_agreements", service_agreement_id=service_agreement_id)
    outstanding = round(float((rows[0].get("service_charges_outstanding") or 0) if rows else 0) + booked, 2)
    if rows:
        ctx.update("service_agreements", service_agreement_id, service_charges_outstanding=outstanding)
    return (f"Out-of-hours surcharge {rid} booked on job {service_agreement_id} for the attendance of "
            f"{visit_date}: {booked:.2f} USD. Outstanding service charges on the job are now "
            f"{outstanding:.2f} USD.")


@tool(owner="agent", rw="write")
def writeoff_service_charge_816a24da(ctx: ToolContext, service_agreement_id: str, customer_id: str,
                                     work_order_line_reference: str, waiver_amount: float,
                                     waiver_reason: str) -> str:
    """Write a billed TechWorks service charge off against one recognised ground, on the line of work
    it was billed on.

    One call books one write-off entry on that job naming the ground it was granted on, and lowers
    the job's outstanding service charges by the amount written off, so the customer is relieved of
    that much of the bill and the original charge stays on file for the history. The entry is dated
    the day it is granted and is taken as a telephone entry. On success the job carries one more
    entry and a lower outstanding figure, and the customer can be told how much has come off the
    bill and on what ground.

    Args:
        service_agreement_id: Id class — the reference number of the TechWorks work order or care
            agreement the relieved charge sits on, read from the work orders held on the customer's
            profile before the call.
        customer_id: Id class — the reference number of the customer profile being relieved of the
            charge, read from that profile before the call.
        work_order_line_reference: Id class — the reference number of the single line of work the
            write-off is granted against, read from the entries already booked on that job before
            the call.
        waiver_amount: Fixed-format class — the amount to write off, in USD to 2 decimal places,
            rounded half up to the cent before it is passed, always positive.
        waiver_reason: Enum class — the ground the write-off is recorded on, exactly one of:
            protection_plan_covered when a ShieldCare plan authorises the work that was charged;
            manufacturer_warranty when the manufacturer's warranty covers that work;
            membership_benefit when a Circle membership benefit or its service credit meets the
            charge; retailer_error when the retailer's own mistake caused the charge; goodwill when
            the retailer chooses to relieve the charge for the inconvenience it caused; contract_term
            when a term of the customer's business contract requires the charge to be relieved;
            none when the entry records no ground at all.

    Returns:
        A one-line confirmation string naming the write-off entry reference that was created, the
        job it was booked on, the ground recorded, the amount written off in USD to two decimal
        places and the job's new outstanding service charges in USD to two decimal places. The
        presence of that entry reference in the reply is what shows the write-off was granted.
    """
    rid = ctx.make_id("sev_", service_agreement_id, customer_id, work_order_line_reference,
                      waiver_amount, waiver_reason)
    ctx.create("service_events", rid, service_event_id=rid,
               service_agreement_id=service_agreement_id, customer_id=customer_id,
               event_type="service_waiver", waiver_amount=round(float(waiver_amount), 2),
               waiver_reason=waiver_reason, event_date=ctx.now()[:10],
               work_order_line_reference=work_order_line_reference, channel="phone")
    relieved = round(float(waiver_amount), 2)
    rows = ctx.find("service_agreements", service_agreement_id=service_agreement_id)
    outstanding = round(float((rows[0].get("service_charges_outstanding") or 0) if rows else 0) - relieved, 2)
    if rows:
        ctx.update("service_agreements", service_agreement_id, service_charges_outstanding=outstanding)
    return (f"Write-off {rid} booked on job {service_agreement_id} on the ground {waiver_reason}: "
            f"{relieved:.2f} USD. Outstanding service charges on the job are now {outstanding:.2f} USD.")


@tool(owner="user", rw="write")
def settle_service_bill_ea31a412(ctx: ToolContext, service_agreement_id: str, customer_id: str,
                                 payment_amount: float, payment_method: str) -> str:
    """Let the customer settle the service charges standing on one of their TechWorks jobs and record
    how the money came in.

    One call books one payment entry on that job for the amount the customer pays and lowers the
    job's outstanding service charges by it, so the customer can see the bill cleared down to what
    is left. The entry is dated the day the money is taken and is taken as a telephone entry. On
    success the job carries one more entry and a lower outstanding figure, and the customer has a
    payment reference to quote.

    Args:
        service_agreement_id: Id class — the reference number of the TechWorks work order or care
            agreement whose charges are being settled, as the agent hands it over before the call.
        customer_id: Id class — the reference number of the paying customer's profile, as the agent
            hands it over before the call.
        payment_amount: Fixed-format class — the amount being paid, in USD to 2 decimal places,
            rounded half up to the cent before it is passed, always positive.
        payment_method: Enum class — how the money is coming in, exactly one of: card_on_file when
            the card kept on the profile is charged; store_credit when a store credit balance is
            spent instead of money; bank_transfer when the customer sends the money from their bank;
            in_store_cash when the customer pays cash at a store counter; business_invoice when the
            amount is put on a business account's invoice to be settled on its terms.

    Returns:
        A one-line confirmation string naming the payment entry reference that was created, the job
        it was booked on, the amount received in USD to two decimal places, the way it was taken and
        the job's new outstanding service charges in USD to two decimal places. The presence of that
        entry reference in the reply is what shows the payment was recorded.
    """
    rid = ctx.make_id("sev_", service_agreement_id, customer_id, payment_amount, payment_method)
    ctx.create("service_events", rid, service_event_id=rid,
               service_agreement_id=service_agreement_id, customer_id=customer_id,
               event_type="service_payment", payment_amount=round(float(payment_amount), 2),
               payment_method=payment_method, event_date=ctx.now()[:10], channel="phone")
    received = round(float(payment_amount), 2)
    rows = ctx.find("service_agreements", service_agreement_id=service_agreement_id)
    outstanding = round(float((rows[0].get("service_charges_outstanding") or 0) if rows else 0) - received, 2)
    if rows:
        ctx.update("service_agreements", service_agreement_id, service_charges_outstanding=outstanding)
    return (f"Payment {rid} recorded on job {service_agreement_id}: {received:.2f} USD taken by "
            f"{payment_method}. Outstanding service charges on the job are now {outstanding:.2f} USD.")


@tool(owner="agent", rw="write")
def credit_contract_relief_ce7af535(ctx: ToolContext, service_agreement_id: str, customer_id: str,
                                    work_order_line_reference: str, relief_amount: float,
                                    relief_ground: str) -> str:
    """Relieve a business customer of part of what a TechWorks job has billed them, on the ground the
    retailer records for it, against the line of work the charges sit on.

    One call books one write-off entry on that job naming the ground it rests on, and lowers the job's
    outstanding service charges by the amount relieved, so the invoice the business owes on that job
    comes down while the original charges stay on file. The entry is dated the day it is granted and
    is taken as a business desk entry. On success the job carries one more entry and a lower
    outstanding figure, and the business can be told how much has come off its invoice and why.

    Args:
        service_agreement_id: Id class — the reference number of the TechWorks work order or care
            agreement whose charges are being relieved, read from the work orders held on the
            customer's profile before the call.
        customer_id: Id class — the reference number of the business profile being relieved of the
            charges, read from that profile before the call.
        work_order_line_reference: Id class — the reference number of the single line of work the
            relief is granted against, read from the entries already booked on that job before the
            call.
        relief_amount: Fixed-format class — the amount to relieve, in USD to 2 decimal places,
            rounded half up to the cent before it is passed, always positive.
        relief_ground: Enum class — the ground the relief rests on, exactly one of:
            protection_plan_covered when a ShieldCare plan authorises the work that was charged;
            manufacturer_warranty when the manufacturer's warranty covers that work;
            membership_benefit when a Circle membership benefit or its service credit meets the
            charge; retailer_error when the retailer's own mistake caused the charge; goodwill when
            the retailer chooses to relieve the charge for the inconvenience it caused; contract_term
            when a term of the customer's business contract requires the charge to be relieved; none
            when the entry records no ground at all.

    Returns:
        A one-line confirmation string naming the relief entry reference that was created, the job it
        was booked on, the ground recorded, the amount relieved in USD to two decimal places and the
        job's new outstanding service charges in USD to two decimal places. The presence of that
        entry reference in the reply is what shows the relief was granted.
    """
    rid = ctx.make_id("sev_", service_agreement_id, customer_id, work_order_line_reference,
                      relief_amount, relief_ground)
    ctx.create("service_events", rid, service_event_id=rid,
               service_agreement_id=service_agreement_id, customer_id=customer_id,
               event_type="service_waiver", waiver_amount=round(float(relief_amount), 2),
               waiver_reason=relief_ground, event_date=ctx.now()[:10],
               work_order_line_reference=work_order_line_reference, channel="business_desk")
    relieved = round(float(relief_amount), 2)
    rows = ctx.find("service_agreements", service_agreement_id=service_agreement_id)
    outstanding = round(float((rows[0].get("service_charges_outstanding") or 0) if rows else 0) - relieved, 2)
    if rows:
        ctx.update("service_agreements", service_agreement_id, service_charges_outstanding=outstanding)
    return (f"Contract relief {rid} booked on job {service_agreement_id} on the ground {relief_ground}: "
            f"{relieved:.2f} USD. Outstanding service charges on the job are now {outstanding:.2f} USD.")


@tool(owner="agent", rw="write")
def bill_uncovered_device_labour_51108cc0(ctx: ToolContext, service_agreement_id: str, customer_id: str,
                                          work_order_line_reference: str, visit_date: str,
                                          labour_hours: float, hourly_rate: float,
                                          labour_amount: float) -> str:
    """Bill the chargeable labour of an attendance on a TechWorks job, against the line of work it
    belongs to, with the hours and the rate it was charged at kept on the entry.

    One call books one labour entry on that job for that attendance and raises the job's outstanding
    service charges by the amount billed, so the customer's statement of the job shows the labour,
    the hours behind it and the rate they were charged at. The entry is dated the day it is booked.
    On success the job carries one more charge and a higher outstanding figure, and the customer can
    be told what the labour on that attendance comes to.

    Args:
        service_agreement_id: Id class — the reference number of the TechWorks work order or care
            agreement the labour was carried out under, read from the work orders held on the
            customer's profile before the call.
        customer_id: Id class — the reference number of the customer profile being billed, read from
            that profile before the call.
        work_order_line_reference: Id class — the reference number of the single line of work the
            labour is billed on, read from the entries already booked on that job before the call.
        visit_date: Fixed-format class — the day the attendance the labour was carried out on took
            place, as YYYY-MM-DD, in the retailer's own local calendar; never left empty.
        labour_hours: Fixed-format class — the chargeable labour recorded on the entry, in hours to
            one decimal place, rounded half up at that one decimal place before it is passed.
        hourly_rate: Fixed-format class — the rate the labour on this entry is charged at, in USD to
            2 decimal places, rounded half up to the cent before it is passed.
        labour_amount: Fixed-format class — the labour to bill, in USD to 2 decimal places, rounded
            half up to the cent before it is passed, always positive.

    Returns:
        A one-line confirmation string naming the labour entry reference that was created, the job it
        was booked on, the attendance day, the chargeable hours to one decimal place, the rate in USD
        to two decimal places, the amount billed in USD to two decimal places and the job's new
        outstanding service charges in USD to two decimal places. The presence of that entry
        reference in the reply is what shows the labour was billed.
    """
    rid = ctx.make_id("sev_", service_agreement_id, customer_id, work_order_line_reference,
                      visit_date, labour_hours, hourly_rate, labour_amount)
    ctx.create("service_events", rid, service_event_id=rid,
               service_agreement_id=service_agreement_id, customer_id=customer_id,
               event_type="service_labour_charge", charge_kind="labour",
               charge_amount=round(float(labour_amount), 2),
               labour_hours=round(float(labour_hours), 1), hourly_rate=round(float(hourly_rate), 2),
               visit_date=visit_date, event_date=ctx.now()[:10],
               work_order_line_reference=work_order_line_reference)
    billed = round(float(labour_amount), 2)
    rows = ctx.find("service_agreements", service_agreement_id=service_agreement_id)
    outstanding = round(float((rows[0].get("service_charges_outstanding") or 0) if rows else 0) + billed, 2)
    if rows:
        ctx.update("service_agreements", service_agreement_id, service_charges_outstanding=outstanding)
    return (f"Labour {rid} booked on job {service_agreement_id} for the attendance of {visit_date}: "
            f"{round(float(labour_hours), 1)} hours at {round(float(hourly_rate), 2):.2f} USD an hour, "
            f"{billed:.2f} USD. Outstanding service charges on the job are now {outstanding:.2f} USD.")


@tool(owner="user", rw="write")
def settle_deployment_invoice_642fded5(ctx: ToolContext, service_agreement_id: str, customer_id: str,
                                       payment_amount: float, payment_method: str) -> str:
    """Let a business customer settle the service charges invoiced on one of their TechWorks jobs and
    record the way the money was sent.

    One call books one payment entry on that job for the amount the business pays and lowers the
    job's outstanding service charges by it, so the invoice on that job is cleared down to what is
    left. The entry is dated the day the money is taken and is taken as a business desk entry. On
    success the job carries one more entry and a lower outstanding figure, and the business has a
    payment reference to put against its own invoice.

    Args:
        service_agreement_id: Id class — the reference number of the TechWorks work order or care
            agreement whose invoiced charges are being settled, as the agent hands it over before the
            call.
        customer_id: Id class — the reference number of the paying business profile, as the agent
            hands it over before the call.
        payment_amount: Fixed-format class — the amount being paid, in USD to 2 decimal places,
            rounded half up to the cent before it is passed, always positive.
        payment_method: Enum class — how the money is being sent, exactly one of: card_on_file when
            the card kept on the profile is charged; store_credit when a store credit balance is
            spent instead of money; bank_transfer when the business sends the money from its bank
            account; in_store_cash when someone pays cash at a store counter; business_invoice when
            the amount is left on the business account's invoice to be settled on its terms.

    Returns:
        A one-line confirmation string naming the payment entry reference that was created, the job it
        was booked on, the amount received in USD to two decimal places, the way it was sent and the
        job's new outstanding service charges in USD to two decimal places. The presence of that entry
        reference in the reply is what shows the payment was recorded.
    """
    rid = ctx.make_id("sev_", service_agreement_id, customer_id, payment_amount, payment_method)
    ctx.create("service_events", rid, service_event_id=rid,
               service_agreement_id=service_agreement_id, customer_id=customer_id,
               event_type="service_payment", payment_amount=round(float(payment_amount), 2),
               payment_method=payment_method, event_date=ctx.now()[:10], channel="business_desk")
    received = round(float(payment_amount), 2)
    rows = ctx.find("service_agreements", service_agreement_id=service_agreement_id)
    outstanding = round(float((rows[0].get("service_charges_outstanding") or 0) if rows else 0) - received, 2)
    if rows:
        ctx.update("service_agreements", service_agreement_id, service_charges_outstanding=outstanding)
    return (f"Payment {rid} recorded on job {service_agreement_id}: {received:.2f} USD sent by "
            f"{payment_method}. Outstanding service charges on the job are now {outstanding:.2f} USD.")

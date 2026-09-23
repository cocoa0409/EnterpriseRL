"""Hidden task tools for the Northbeam Renew trade-in appraisal desk.

Each tool performs one atomic write on the trade-in records. None of them judges eligibility,
reconciles history or works a figure out for the agent: every amount, count and date they take is
worked out by the agent from the published rules and the records, and passed in as declared.
"""

from erlbench import ToolContext, tool


@tool(owner="user", rw="write")
def confirm_handover_units_5801b6db(ctx: ToolContext, tradein_agreement_id: str, customer_id: str,
                                    requested_collection_date: str, units_declared: int) -> str:
    """Let the customer consent, in person, to handing machines over on a Renew trade-in agreement already
    accepted, for a palletised freight collection, and put the run on record.

    The customer is the owner of the machines, so this consent is theirs to give: it records that they
    agree to hand the stated number of machines to the retailer's freight carrier on the day they name,
    and that they agree to the data on those machines being destroyed once the machines are in the
    retailer's hands. A fresh collection record is opened against the agreement carrying the day asked
    for, the machines the consent covers, freight collection as the way the machines travel, and the
    consent itself marked as given by the customer; the agreement is also set to travel by freight
    collection, which is the choice the customer is making here. Once it is on record the customer can
    see the run listed against the agreement with the count they consented to and the agreement showing
    freight collection as the way the machines will travel, and the carrier can be sent for those
    machines.

    Args:
        tradein_agreement_id: Id class — the reference number of the Renew trade-in agreement the machines
            are traded under, read from the trade-in agreement record found for the customer profile.
        customer_id: Id class — the customer reference number of the profile trading the machines in, read
            from the customer profile record.
        requested_collection_date: Fixed-format class — the day the customer asks for the machines to be
            collected, written as YYYY-MM-DD in the retailer's local calendar date, with no time part; it
            is never left empty.
        units_declared: Fixed-format class — how many machines the customer consents to hand over on this
            run, as a whole count of machines with no decimal part and never below zero.

    Returns:
        A confirmation line in plain text naming the collection record opened, the agreement it belongs to,
        the day asked for, the whole count of machines the consent covers and the way the machines will
        travel. The line being returned is what shows the consent is on record; the run can then be read
        back on the agreement's collection records.
    """
    rid = ctx.make_id("tsr_", tradein_agreement_id, customer_id, requested_collection_date, units_declared)
    ctx.create("tradein_shipping_requests", rid, tradein_shipping_request_id=rid,
               customer_id=customer_id, tradein_agreement_id=tradein_agreement_id,
               requested_shipment_method="freight_collection",
               requested_collection_date=requested_collection_date,
               customer_consent="consented_by_customer", units_declared=int(units_declared),
               created_at=ctx.now())
    ctx.update("tradein_agreements", tradein_agreement_id, shipment_method="freight_collection")
    return (f"Collection {rid} recorded on agreement {tradein_agreement_id}: {int(units_declared)} machine(s) "
            f"consented for freight collection on {requested_collection_date}; the agreement now travels by "
            f"freight collection.")


@tool(owner="agent", rw="write")
def charge_collection_freight_530ef4f1(ctx: ToolContext, tradein_agreement_id: str, customer_id: str,
                                       handling_fee_amount: float) -> str:
    """Raise the collection charge for a palletised freight run on a Renew trade-in agreement and put it on
    the profile's trade-in account.

    One entry is booked against the agreement recording what the retailer charges the customer for sending
    the carrier to collect the machines, and the freight and handling still owed on the agreement is
    increased by that amount. The customer sees the charge listed against the trade-in agreement and
    carried on their account until it is settled or waived.

    Args:
        tradein_agreement_id: Id class — the reference number of the Renew trade-in agreement the collection
            is run under, read from the trade-in agreement record found for the customer profile.
        customer_id: Id class — the customer reference number of the profile being charged, read from the
            customer profile record.
        handling_fee_amount: Fixed-format class — the amount charged for the collection, in USD to 2 decimal
            places, rounded half up at the cent when it is booked, and never negative.

    Returns:
        A confirmation line in plain text naming the charge entry booked, the agreement it was booked
        against, the amount charged in USD and the freight and handling now outstanding on the agreement.
        The line being returned is what shows the charge is booked; it can then be read back among the
        agreement's trade-in history entries.
    """
    amount = round(float(handling_fee_amount), 2)
    rid = ctx.make_id("tie_", tradein_agreement_id, customer_id, handling_fee_amount)
    agreements = ctx.find("tradein_agreements", tradein_agreement_id=tradein_agreement_id)
    agreement = agreements[0] if agreements else {}
    ctx.create("tradein_events", rid, tradein_event_id=rid, tradein_agreement_id=tradein_agreement_id,
               customer_id=customer_id, event_type="tradein_handling_fee_charge",
               handling_fee_amount=amount, event_date=ctx.now()[:10], channel="business_desk",
               device_serial=agreement.get("device_serial", ""),
               tier_at_event=agreement.get("variant_name", ""))
    outstanding = round(float(agreement.get("handling_fee_outstanding") or 0) + amount, 2)
    ctx.update("tradein_agreements", tradein_agreement_id, handling_fee_outstanding=outstanding)
    return (f"Collection charge {rid} booked on agreement {tradein_agreement_id} at {amount:.2f} USD; "
            f"freight and handling outstanding is now {outstanding:.2f} USD.")


@tool(owner="agent", rw="write")
def put_revised_offer_f86761c2(ctx: ToolContext, tradein_agreement_id: str, customer_id: str,
                               revised_amount: float, revision_reason: str) -> str:
    """Put a revised offer to the customer on a Renew trade-in agreement whose appraisal came back other than the
    condition declared, and record it against the agreement.

    One entry is written into the agreement's trade-in history holding the amount the offer now stands at, the ground
    the offer moved on and the condition the appraisal found, so the customer has the retailer's new figure in writing
    and can answer it. The agreement's own state is left where it stands; what changes is that the revised offer is on
    record against it and can be read back on the trade-in history.

    Args:
        tradein_agreement_id: Id class — the reference number of the Renew trade-in agreement the offer is revised on,
            read from the trade-in agreement record found for the customer profile.
        customer_id: Id class — the customer reference number of the profile the offer is put to, read from the customer
            profile record.
        revised_amount: Fixed-format class — the amount the revised offer stands at, in USD to 2 decimal places, rounded
            half up at the cent when it is recorded, and never negative.
        revision_reason: Enum class — the ground the offer moved on, exactly one of:
            condition_worse_than_declared — the appraisal found the goods in a poorer condition than the customer declared;
            model_mismatch — the goods that arrived are a different model from the one quoted;
            device_locked — the goods arrived still locked to a carrier or an account;
            missing_accessories — the charger, stylus or other accessory that should have come with the goods was absent;
            market_price_change — the price the retailer can resell the goods at has moved since the quote was given;
            no_power — the goods will not power on;
            water_damage_found — the appraisal found liquid ingress in the goods.

    Returns:
        A confirmation line in plain text naming the trade-in history entry written, the agreement it belongs to, the
        amount the revised offer stands at in USD and the ground recorded for it. The line being returned is what shows
        the revised offer is on record; it can then be read back among the agreement's trade-in history entries.
    """
    amount = round(float(revised_amount), 2)
    rid = ctx.make_id("tie_", tradein_agreement_id, customer_id, revised_amount, revision_reason)
    agreements = ctx.find("tradein_agreements", tradein_agreement_id=tradein_agreement_id)
    agreement = agreements[0] if agreements else {}
    ctx.create("tradein_events", rid, tradein_event_id=rid, tradein_agreement_id=tradein_agreement_id,
               customer_id=customer_id, event_type="tradein_quote_revise", revised_amount=amount,
               revision_reason=revision_reason, appraised_condition=agreement.get("appraised_condition", ""),
               device_serial=agreement.get("device_serial", ""), event_date=ctx.now()[:10],
               channel="business_desk", tier_at_event=agreement.get("variant_name", ""))
    return (f"Revised offer {rid} recorded on agreement {tradein_agreement_id} at {amount:.2f} USD "
            f"({revision_reason}).")


@tool(owner="agent", rw="write")
def credit_batch_settlement_af2cb6f5(ctx: ToolContext, tradein_agreement_id: str, customer_id: str,
                                     final_credit_amount: float, settlement_method: str,
                                     credit_expiry_date: str) -> str:
    """Close a Renew trade-in agreement out by crediting the customer the amount settled on the batch.

    The agreement is moved to credited with today as the day the credit was issued, the amount credited and the last day
    that credit may be spent written onto it, and a matching entry is added to the trade-in history recording the credit
    in the form the customer takes it, with the trade-in credit the customer holds increased by that amount. Afterwards
    the customer can see the agreement closed out and the credit standing on the profile to spend up to that last day.

    Args:
        tradein_agreement_id: Id class — the reference number of the Renew trade-in agreement being closed out, read
            from the trade-in agreement record found for the customer profile.
        customer_id: Id class — the customer reference number of the profile being credited, read from the customer
            profile record.
        final_credit_amount: Fixed-format class — the amount credited to the customer, in USD to 2 decimal places,
            rounded half up at the cent when it is booked, and never negative.
        credit_expiry_date: Fixed-format class — the last day the credit issued here may be spent, written as
            YYYY-MM-DD in the retailer's local calendar date, with no time part; it is never left empty.
        settlement_method: Enum class — the form the credit is put into the customer's hands in, exactly one of:
            store_credit — credit held on the customer's profile to spend on merchandise;
            gift_card — credit loaded onto a gift card handed or sent to the customer;
            instant_checkout_discount — credit taken straight off a purchase the customer is making at the till;
            business_invoice_credit — credit raised against the business account's invoice;
            bank_transfer — money paid out to the business's bank account.

    Returns:
        A confirmation line in plain text naming the agreement closed out, the amount credited in USD, the form the
        credit was issued in, the last day that credit may be spent and the trade-in credit now standing unspent on the
        agreement. The line being returned is what shows the credit is issued; the agreement then reads as credited with
        the amount and the last spendable day on it.
    """
    amount = round(float(final_credit_amount), 2)
    agreements = ctx.find("tradein_agreements", tradein_agreement_id=tradein_agreement_id)
    agreement = agreements[0] if agreements else {}
    ctx.update("tradein_agreements", tradein_agreement_id, status="credited", credited_date=ctx.now()[:10],
               final_credit_amount=amount, credit_expiry_date=credit_expiry_date,
               credit_outstanding=round(float(agreement.get("credit_outstanding") or 0) + amount, 2))
    rid = ctx.make_id("tie_", tradein_agreement_id, customer_id, final_credit_amount, settlement_method,
                      credit_expiry_date)
    ctx.create("tradein_events", rid, tradein_event_id=rid, tradein_agreement_id=tradein_agreement_id,
               customer_id=customer_id, event_type="tradein_credit_issue", credit_amount=amount,
               settlement_method=settlement_method, device_serial=agreement.get("device_serial", ""),
               event_date=ctx.now()[:10], channel="business_desk",
               tier_at_event=agreement.get("variant_name", ""))
    return (f"Agreement {tradein_agreement_id} credited {amount:.2f} USD as {settlement_method} (entry {rid}), "
            f"spendable up to {credit_expiry_date}; trade-in credit unspent is now "
            f"{round(float(agreement.get('credit_outstanding') or 0) + amount, 2):.2f} USD.")


@tool(owner="user", rw="write")
def confirm_refresh_wave_units_923c3678(ctx: ToolContext, tradein_agreement_id: str, customer_id: str,
                                        requested_collection_date: str, units_declared: int) -> str:
    """Let the customer accept a quoted Renew refresh schedule in person and release the machines of its first wave.

    Accepting the quote and releasing machines are the customer's own acts, because the machines are theirs: this moves
    the schedule from quoted to accepted with today as the day it was accepted, and opens a collection record against it
    carrying the day the customer names, the machines the release covers, freight collection as the way the machines
    travel, and the consent marked as given by the customer. Afterwards the customer can see the schedule standing
    accepted and the wave listed against it with the count they agreed to.

    Args:
        tradein_agreement_id: Id class — the reference number of the Renew refresh schedule the machines are traded
            under, read from the trade-in agreement record found for the customer profile.
        customer_id: Id class — the customer reference number of the profile trading the machines in, read from the
            customer profile record.
        requested_collection_date: Fixed-format class — the day the customer asks for the wave to be collected, written
            as YYYY-MM-DD in the retailer's local calendar date, with no time part; it is never left empty.
        units_declared: Fixed-format class — how many machines the customer consents to release on this wave, as a whole
            count of machines with no decimal part and never below zero.

    Returns:
        A confirmation line in plain text naming the schedule now accepted, the day it was accepted, the collection
        record opened for the first wave, the day asked for and the whole count of machines the release covers. The line
        being returned is what shows the acceptance and the wave are on record; both can then be read back on the
        schedule and its collection records.
    """
    rid = ctx.make_id("tsr_", tradein_agreement_id, customer_id, requested_collection_date, units_declared)
    ctx.update("tradein_agreements", tradein_agreement_id, status="accepted", accepted_date=ctx.now()[:10])
    ctx.create("tradein_shipping_requests", rid, tradein_shipping_request_id=rid,
               customer_id=customer_id, tradein_agreement_id=tradein_agreement_id,
               requested_shipment_method="freight_collection",
               requested_collection_date=requested_collection_date,
               customer_consent="consented_by_customer", units_declared=int(units_declared),
               created_at=ctx.now())
    return (f"Schedule {tradein_agreement_id} accepted on {ctx.now()[:10]}; wave {rid} recorded on it: "
            f"{int(units_declared)} machine(s) released for freight collection on {requested_collection_date}.")

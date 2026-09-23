"""Hidden task tools for the vehicle_listing_desk difficulty of env_0015_car_sharing_marketplace.

Each function performs exactly one atomic write against a Keyturn Vehicle Listing or its
condition record. None of them aggregates history, judges eligibility or computes a figure on
the agent's behalf: every quantitative argument is worked out by the agent from the published
policy and the records, and is landed here as it is given.
"""

from erlbench import ToolContext, tool


@tool(owner="agent", rw="write")
def log_vehicle_fault_a3e017f7(ctx: ToolContext, vehicle_id: str, customer_id: str,
                               source_inspection_id: str, defect_code: str,
                               inspection_channel: str, attached_photo_count: int) -> str:
    """Open a fault record against a Keyturn Vehicle Listing so the marketplace holds the fault on
    the vehicle's condition history. One call adds a single dated fault record carrying the fault
    that was found, who found it, the condition record the fault was carried across from, and the
    number of photographs filed with it. The listing's own lifecycle state is untouched; what the
    host and the desk can see afterwards is a new fault entry on the vehicle's condition record,
    dated today, which every later reading of that vehicle's fault history includes.

    Args:
        vehicle_id: Id class — the listing reference number of the vehicle the fault belongs to,
            read from the vehicle listing lookup before the call.
        customer_id: Id class — the member reference number of the host who owns that listing,
            read from the member profile lookup before the call.
        source_inspection_id: Id class — the reference number of the earlier condition record the
            fault is carried across from, read from the vehicle condition record lookup before the
            call.
        defect_code: Enum class — the fault this record registers, exactly one of:
            none — nothing was found and the record registers no fault at all;
            tyre_tread — a tyre is worn to or past its tread limit;
            brake_wear — brake pads, discs or fluid are worn past their service limit;
            windscreen_chip — the glass is chipped, starred or cracked;
            warning_light — a dashboard warning lamp is lit on the vehicle;
            body_damage — the bodywork, bumpers or panels are damaged;
            missing_equipment — equipment the class requires is absent from the vehicle;
            open_recall — the manufacturer has an unperformed safety recall on the vehicle.
        inspection_channel: Enum class — who produced the report, exactly one of:
            self_photo — the host photographed the vehicle themselves;
            partner_shop — a partner workshop found it while the vehicle was with them;
            mobile_inspector — a marketplace inspector attending the vehicle found it;
            telematics_report — the fitted telematics unit reported it.
        attached_photo_count: Fixed-format class — how many photographs are filed with this fault
            record, as a whole number of photographs with no decimal part, no unit suffix and no
            thousands separator; zero means no photograph is filed.

    Returns:
        A confirmation sentence naming the reference number minted for the new fault record, the
        listing it was opened against, the fault registered and the number of photographs filed
        with it. The presence of that reference number in the sentence is what indicates the fault
        record now stands on the vehicle's condition history.
    """
    rid = ctx.make_id("dfr_", vehicle_id, customer_id, source_inspection_id, defect_code,
                      inspection_channel, attached_photo_count)
    ctx.create("listings_inspections", rid, inspection_id=rid, vehicle_id=vehicle_id,
               customer_id=customer_id, source_inspection_id=source_inspection_id,
               event_type="listings_defect_reported", record_date=ctx.now()[:10],
               defect_code=defect_code, inspection_channel=inspection_channel,
               inspection_outcome="not_applicable", photo_count=int(attached_photo_count))
    return (f"Fault record {rid} opened on listing {vehicle_id}: {defect_code} reported through "
            f"{inspection_channel} with {int(attached_photo_count)} photograph(s) on file.")


@tool(owner="agent", rw="write")
def record_vehicle_valuation_559b4236(ctx: ToolContext, vehicle_id: str, customer_id: str,
                                      odometer_reading: int, assessed_value_amount: float,
                                      value_class_assessed: str, inspection_channel: str) -> str:
    """Record a marketplace valuation of a Keyturn Vehicle Listing on the vehicle's condition
    record. One call files a single dated valuation carrying the odometer the valuation was made
    on, the money figure the marketplace has put on the vehicle, the value class that figure falls
    in and how the valuation was produced. Nothing on the listing itself moves: the vehicle keeps
    the class and the value it already carries, and what becomes visible is a fresh valuation entry
    that later readings of the vehicle's valuation history return.

    Args:
        vehicle_id: Id class — the listing reference number of the vehicle being valued, read from
            the vehicle listing lookup before the call.
        customer_id: Id class — the member reference number of the host who owns that listing, read
            from the member profile lookup before the call.
        odometer_reading: Fixed-format class — the odometer the valuation was made on, in whole
            miles as an integer, with no decimal part, no unit suffix and no thousands separator.
        assessed_value_amount: Fixed-format class — the money figure the marketplace has put on the
            vehicle, in USD to 2 decimal places, rounded half away from zero at the point it is
            filed; an amount of 0.00 means no figure was established.
        value_class_assessed: Enum class — the value class the filed figure places the vehicle in,
            exactly one of:
            unassessed — the record establishes no class for the vehicle;
            Keyturn Economy Class Listing — the figure falls in the entry value band;
            Keyturn Standard Class Listing — the figure falls in the standard value band;
            Keyturn Premium Class Listing — the figure falls in the premium value band;
            Keyturn Luxury Class Listing — the figure falls in the luxury value band;
            Keyturn Exotic Class Listing — the figure falls in the exotic value band;
            Keyturn Commercial Van Class Listing — the vehicle is a commercially plated van and the
            figure falls in the commercial van value band.
        inspection_channel: Enum class — how the valuation was produced, exactly one of:
            self_photo — from photographs the host supplied;
            partner_shop — from a partner workshop's assessment of the vehicle;
            mobile_inspector — from a marketplace inspector who attended the vehicle;
            telematics_report — from the data the fitted telematics unit returns.

    Returns:
        A confirmation sentence naming the reference number minted for the new valuation record,
        the listing it was filed against, the money figure recorded to 2 decimal places and the
        value class that figure falls in. The presence of that reference number in the sentence is
        what indicates the valuation now stands on the vehicle's condition record.
    """
    rid = ctx.make_id("val_", vehicle_id, customer_id, odometer_reading, assessed_value_amount,
                      value_class_assessed, inspection_channel)
    ctx.create("listings_inspections", rid, inspection_id=rid, vehicle_id=vehicle_id,
               customer_id=customer_id, event_type="listings_valuation_reassessed",
               record_date=ctx.now()[:10], odometer_reading=int(odometer_reading),
               assessed_value_amount=round(float(assessed_value_amount), 2),
               value_class_assessed=value_class_assessed, inspection_channel=inspection_channel,
               inspection_outcome="not_applicable")
    return (f"Valuation {rid} filed on listing {vehicle_id}: "
            f"{round(float(assessed_value_amount), 2)} USD, placed in {value_class_assessed}.")


@tool(owner="agent", rw="write")
def reassign_value_class_4bb6b10c(ctx: ToolContext, vehicle_id: str, value_class_name: str,
                                  governing_value_amount: float) -> str:
    """Move a Keyturn Vehicle Listing into the value class the marketplace has settled on, and put
    the money figure that governs the listing onto the record at the same time. One call rewrites
    the class the listing sits in and the vehicle value carried on it; the listing keeps its
    lifecycle state, its price and its condition history untouched. Afterwards the host sees the
    vehicle showing the new class and the new governing value wherever the listing is displayed.

    Args:
        vehicle_id: Id class — the listing reference number of the vehicle being moved, read from
            the vehicle listing lookup before the call.
        value_class_name: Enum class — the value class the listing is moved into, exactly one of:
            Keyturn Economy Class Listing — the entry class for the lowest value band;
            Keyturn Standard Class Listing — the class for mid value band vehicles;
            Keyturn Premium Class Listing — the class for the premium value band;
            Keyturn Luxury Class Listing — the class for high value passenger vehicles;
            Keyturn Exotic Class Listing — the class for the highest value vehicles;
            Keyturn Commercial Van Class Listing — the class for commercially plated vans.
        governing_value_amount: Fixed-format class — the vehicle value that governs the listing from
            now on, in USD to 2 decimal places, rounded half away from zero at the point it is
            written; an amount of 0.00 means no value governs the listing.

    Returns:
        A confirmation sentence naming the listing that was moved, the value class it now sits in
        and the governing value written onto it to 2 decimal places. A sentence naming the listing
        is what indicates the class and the value now stand on the record; a report that the
        listing could not be found means nothing was written.
    """
    if not ctx.update("listings_vehicles", vehicle_id,
                      value_class_name=value_class_name,
                      market_value_amount=round(float(governing_value_amount), 2)):
        return f"No listing {vehicle_id} was found, so nothing was written."
    return (f"Listing {vehicle_id} now sits in {value_class_name} with a governing value of "
            f"{round(float(governing_value_amount), 2)} USD.")


@tool(owner="user", rw="write")
def set_daily_price_59fd8a00(ctx: ToolContext, vehicle_id: str, daily_price_amount: float) -> str:
    """Set what a host asks per day for their own Keyturn Vehicle Listing. One call rewrites the
    daily price carried on that listing; nothing else about the vehicle moves, and bookings already
    confirmed keep the price locked in at their own confirmation. Afterwards the host sees the new
    daily price on the listing, and guests searching the marketplace are quoted from it.

    Args:
        vehicle_id: Id class — the listing reference number of the host's own vehicle whose price is
            being set, taken from what the desk has read back from the vehicle listing lookup.
        daily_price_amount: Fixed-format class — the daily price the host asks from now on, in USD
            to 2 decimal places, rounded half away from zero at the point it is written; an amount
            of 0.00 means no price is asked.

    Returns:
        A confirmation sentence naming the listing and the daily price now carried on it to 2
        decimal places. A sentence naming the listing is what indicates the new price stands; a
        report that the listing could not be found means nothing was written.
    """
    if not ctx.update("listings_vehicles", vehicle_id,
                      daily_price_amount=round(float(daily_price_amount), 2)):
        return f"No listing {vehicle_id} was found, so nothing was written."
    return (f"Listing {vehicle_id} now asks {round(float(daily_price_amount), 2)} USD per day.")


@tool(owner="agent", rw="write")
def verify_listing_document_28456ce9(ctx: ToolContext, vehicle_id: str, customer_id: str,
                                     document_kind: str, inspection_channel: str,
                                     verification_image_count: int) -> str:
    """Record that a document a Keyturn Vehicle Listing depends on has been checked by the
    marketplace and found good. One call files a single dated verification record on the vehicle's
    condition record, naming the document checked, who checked it and how many images of it the
    marketplace now holds on file, and every such record is filed as passed. The listing's own
    lifecycle state, class and price are untouched; what the host and the desk see afterwards is a
    verification entry dated today that later readings of the vehicle's document history return.

    Args:
        vehicle_id: Id class — the listing reference number of the vehicle the document belongs to,
            read from the vehicle listing lookup before the call.
        customer_id: Id class — the member reference number of the host who owns that listing, read
            from the member profile lookup before the call.
        document_kind: Enum class — the document this record verifies, exactly one of:
            none — the record verifies no document at all;
            registration — the vehicle's state or provincial registration certificate;
            title — the ownership title document for the vehicle;
            lienholder_consent — the written consent of the finance company or lessor named on the title;
            insurance_certificate — the certificate of the host's own motor insurance;
            recall_clearance — a workshop's confirmation that a safety recall has been carried out.
        inspection_channel: Enum class — who carried the check out, exactly one of:
            self_photo — the host supplied photographs of the document themselves;
            partner_shop — a partner workshop confirmed the document while holding the vehicle;
            mobile_inspector — a marketplace inspector checked the document against the vehicle;
            telematics_report — the fitted telematics unit supplied the evidence.
        verification_image_count: Fixed-format class — how many images of the document the
            marketplace holds on file once this check is recorded, as a whole number of images with
            no decimal part, no unit suffix and no thousands separator; zero means no image is held.

    Returns:
        A confirmation sentence naming the reference number minted for the new verification record,
        the listing it was filed against, the document checked and the number of images held on
        file. The presence of that reference number in the sentence is what indicates the
        verification now stands on the vehicle's condition record.
    """
    rid = ctx.make_id("doc_", vehicle_id, customer_id, document_kind, inspection_channel,
                      verification_image_count)
    ctx.create("listings_inspections", rid, inspection_id=rid, vehicle_id=vehicle_id,
               customer_id=customer_id, event_type="listings_document_verified",
               record_date=ctx.now()[:10], document_kind=document_kind,
               inspection_channel=inspection_channel, inspection_outcome="passed",
               photo_count=int(verification_image_count))
    return (f"Verification {rid} filed on listing {vehicle_id}: {document_kind} checked through "
            f"{inspection_channel}, {int(verification_image_count)} image(s) held on file.")


@tool(owner="agent", rw="write")
def record_vehicle_inspection_59fe0be1(ctx: ToolContext, vehicle_id: str, customer_id: str,
                                       odometer_reading: int, inspection_outcome: str,
                                       inspection_channel: str,
                                       interval_miles_granted: int) -> str:
    """File a completed marketplace inspection of a Keyturn Vehicle Listing on the vehicle's
    condition record and grant it a fresh mileage interval. One call adds a single dated inspection
    entry carrying the odometer the vehicle was inspected at, what the inspection found, how it was
    carried out and the miles of interval it grants, and that same figure is booked to the vehicle's
    inspection mileage credit as the interval the entry adds. The listing's class, price and
    lifecycle state are untouched; what the host sees afterwards is an inspection entry dated today
    with the interval it granted.

    Args:
        vehicle_id: Id class — the listing reference number of the vehicle inspected, read from the
            vehicle listing lookup before the call.
        customer_id: Id class — the member reference number of the host who owns that listing, read
            from the member profile lookup before the call.
        odometer_reading: Fixed-format class — the odometer the vehicle was inspected at, in whole
            miles as an integer, with no decimal part, no unit suffix and no thousands separator.
        inspection_outcome: Enum class — what the inspection found, exactly one of:
            not_applicable — the record is not an inspection and reaches no finding;
            passed — the vehicle met every standard checked with nothing to note;
            passed_with_advisories — the vehicle met every standard but something was noted for the host to watch;
            failed — the vehicle did not meet a standard checked.
        inspection_channel: Enum class — how the inspection was carried out, exactly one of:
            self_photo — the host photographed the vehicle against the checklist themselves;
            partner_shop — a partner workshop inspected the vehicle on its premises;
            mobile_inspector — a marketplace inspector attended the vehicle and inspected it;
            telematics_report — the fitted telematics unit supplied the inspection evidence.
        interval_miles_granted: Fixed-format class — the mileage interval this inspection grants
            before the next one falls due, in whole miles as an integer, with no decimal part, no
            unit suffix and no thousands separator; it is booked to the vehicle's inspection mileage
            credit as whole miles, signed, a positive addition of the same size.

    Returns:
        A confirmation sentence naming the reference number minted for the new inspection record,
        the listing it was filed against, what the inspection found and the mileage interval
        granted. The presence of that reference number in the sentence is what indicates the
        inspection and its interval now stand on the vehicle's condition record.
    """
    rid = ctx.make_id("insp_", vehicle_id, customer_id, odometer_reading, inspection_outcome,
                      inspection_channel, interval_miles_granted)
    ctx.create("listings_inspections", rid, inspection_id=rid, vehicle_id=vehicle_id,
               customer_id=customer_id, event_type="listings_inspection_completed",
               record_date=ctx.now()[:10], odometer_reading=int(odometer_reading),
               miles_delta=int(interval_miles_granted), next_due_miles=int(interval_miles_granted),
               inspection_outcome=inspection_outcome, inspection_channel=inspection_channel)
    return (f"Inspection {rid} filed on listing {vehicle_id}: {inspection_outcome} at "
            f"{int(odometer_reading)} miles, {int(interval_miles_granted)} miles of interval granted.")


@tool(owner="agent", rw="write")
def record_booked_mileage_82af4bea(ctx: ToolContext, vehicle_id: str, customer_id: str,
                                   source_inspection_id: str, odometer_reading: int,
                                   inspection_channel: str, booked_miles_consumed: int) -> str:
    """Book an odometer reading the marketplace has taken on a Keyturn Vehicle Listing against that
    vehicle's inspection mileage credit. One call adds a single dated odometer entry carrying the
    reading, where the reading came from, the condition record it was taken from, and the miles that
    reading takes off the interval, which are booked to the vehicle's inspection mileage credit as a
    deduction of that size. The listing's class, price and lifecycle state are untouched; what the
    desk and the host see afterwards is an odometer entry dated today with the miles it consumed.

    Args:
        vehicle_id: Id class — the listing reference number of the vehicle the reading belongs to,
            read from the vehicle listing lookup before the call.
        customer_id: Id class — the member reference number of the host who owns that listing, read
            from the member profile lookup before the call.
        source_inspection_id: Id class — the reference number of the condition record the reading is
            taken from; that reference number is carried on the record itself and is repeated in any
            receipt that reports it.
        odometer_reading: Fixed-format class — the odometer being booked, in whole miles as an
            integer, with no decimal part, no unit suffix and no thousands separator.
        inspection_channel: Enum class — where the reading came from, exactly one of:
            self_photo — the host photographed the odometer themselves;
            partner_shop — a partner workshop read the odometer while holding the vehicle;
            mobile_inspector — a marketplace inspector read the odometer at the vehicle;
            telematics_report — the fitted telematics unit reported the odometer.
        booked_miles_consumed: Fixed-format class — the miles this reading takes off the vehicle's
            inspection interval, in whole miles as an integer, with no decimal part, no unit suffix
            and no thousands separator; it is booked to the inspection mileage credit as whole
            miles, signed, a negative deduction of the same size, and zero means the reading
            consumes nothing.

    Returns:
        A confirmation sentence naming the reference number minted for the new odometer record, the
        listing it was booked against, the reading recorded and the miles taken off the interval.
        The presence of that reference number in the sentence is what indicates the reading now
        stands on the vehicle's condition record.
    """
    rid = ctx.make_id("odo_", vehicle_id, customer_id, source_inspection_id, odometer_reading,
                      inspection_channel, booked_miles_consumed)
    ctx.create("listings_inspections", rid, inspection_id=rid, vehicle_id=vehicle_id,
               customer_id=customer_id, source_inspection_id=source_inspection_id,
               event_type="listings_odometer_reported", record_date=ctx.now()[:10],
               odometer_reading=int(odometer_reading),
               miles_delta=-int(booked_miles_consumed), inspection_channel=inspection_channel,
               inspection_outcome="not_applicable")
    return (f"Odometer record {rid} booked on listing {vehicle_id}: {int(odometer_reading)} miles "
            f"recorded, {int(booked_miles_consumed)} mile(s) taken off the inspection interval.")


@tool(owner="user", rw="write")
def report_vehicle_mileage_90a8825c(ctx: ToolContext, vehicle_id: str, customer_id: str,
                                    odometer_reading: int, reported_miles_consumed: int) -> str:
    """Report the odometer on a host's own Keyturn Vehicle Listing, which is the periodic reading
    the marketplace asks every host for. One call adds a single dated odometer entry in the host's
    own name carrying the reading they give and the miles it takes off the vehicle's inspection
    interval, which are booked to the inspection mileage credit as a deduction of that size.
    Nothing else about the listing moves. Afterwards the host can see their reading standing on the
    vehicle's condition record with the miles it consumed.

    Args:
        vehicle_id: Id class — the listing reference number of the host's own vehicle the reading is
            for, taken from what the desk has read back from the vehicle listing lookup.
        customer_id: Id class — the member reference number of the host giving the reading, taken
            from what the desk has read back from the member profile lookup.
        odometer_reading: Fixed-format class — the odometer the host reads off the vehicle, in whole
            miles as an integer, with no decimal part, no unit suffix and no thousands separator.
        reported_miles_consumed: Fixed-format class — the miles this reading takes off the vehicle's
            inspection interval, in whole miles as an integer, with no decimal part, no unit suffix
            and no thousands separator; it is booked to the inspection mileage credit as whole
            miles, signed, a negative deduction of the same size, and zero means the reading
            consumes nothing.

    Returns:
        A confirmation sentence naming the reference number minted for the host's odometer record,
        the listing it was reported against, the reading given and the miles taken off the
        inspection interval. The presence of that reference number in the sentence is what
        indicates the reading now stands on the vehicle's condition record.
    """
    rid = ctx.make_id("hodo_", vehicle_id, customer_id, odometer_reading, reported_miles_consumed)
    ctx.create("listings_inspections", rid, inspection_id=rid, vehicle_id=vehicle_id,
               customer_id=customer_id, event_type="listings_odometer_reported",
               record_date=ctx.now()[:10], odometer_reading=int(odometer_reading),
               miles_delta=-int(reported_miles_consumed), inspection_channel="self_photo",
               inspection_outcome="not_applicable")
    return (f"Odometer record {rid} reported on listing {vehicle_id}: {int(odometer_reading)} miles "
            f"given by the host, {int(reported_miles_consumed)} mile(s) taken off the inspection interval.")

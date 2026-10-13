"""Hidden task tools of the tire_center_services difficulty (Northgate Tire Center).

Each tool performs one atomic write on a Tire Center installation package and is reached only through
unlock_* -> call_*; its name is published only as an extended policy's target_tool. No tool checks a
policy condition, aggregates history or computes an amount: the caller passes the settled values.
"""

from erlbench import ToolContext, tool



@tool(owner="agent", rw="write")
def post_claim_fitting_charge_0bdb2547(ctx: ToolContext, tire_service_id: str, tire_position: str,
                                       service_date: str, odometer_miles: int, source_event_id: str,
                                       amount: float) -> str:
    """Book the fitting charge for one wheel whose tire was replaced under a treadwear mileage warranty claim.

    Member services uses this to post, on a Tire Center installation package, the charge for mounting,
    balancing and fitting the replacement tire on one wheel, dated on the claim's work order and linked to
    the treadwear claim entry the replacement came from. One call adds exactly one installation-package
    charge entry for that wheel to the package's Tire Center charges; the package's balance of Tire Center
    charges rises by the amount, and the entry then appears with the package's other charges and credits.
    Nothing else on the package changes.

    Args:
        tire_service_id: Id class — the installation package reference number of the tire set, read from the Tire Center package lookup before the call.
        tire_position: Enum class — the wheel the replacement tire was fitted on, exactly one of: left_front when the fitted wheel is the driver-side front wheel; right_front when it is the passenger-side front wheel; left_rear when it is the driver-side rear wheel; right_rear when it is the passenger-side rear wheel; spare when the fitted tire is the full-size spare; all_positions when one charge covers every wheel of the set at once.
        service_date: Fixed-format class — the date of the claim work order the fitting belongs to, written YYYY-MM-DD as on that work order entry (no time, no time zone).
        odometer_miles: Fixed-format class — the vehicle odometer on that claim work order, an integer in integer miles with no separators or decimals.
        source_event_id: Id class — the reference number of the treadwear claim entry the replacement tire came from, read from the package's Tire Center work history before the call.
        amount: Fixed-format class — the fitting charge to book, in USD, 2 decimal places, >= 0 (pass the value already worked out to the cent; it is booked at 2 decimal places as given).

    Returns:
        A dictionary rendered as text: tire_event_id is the reference number of the new charge entry (text);
        tire_service_id is the package charged (text); charge_component is always installation_package;
        tire_position is the wheel charged; service_date is the work order date (YYYY-MM-DD); amount is the
        charge booked in USD with 2 decimal places; status is "booked" when the entry was added. A receipt with
        status "booked" means the charge now stands on the package.
    """
    amt = round(float(amount), 2)
    rid = ctx.make_id("tsv_", tire_service_id, tire_position, service_date, int(odometer_miles),
                      source_event_id, amt)
    ctx.create("tire_services", rid, tire_event_id=rid, tire_service_id=tire_service_id,
               customer_id=(ctx.find("tire_holdings", tire_service_id=tire_service_id) or [{}])[0].get("customer_id", ""),
               event_type="tire_service_charged", service_date=service_date, odometer_miles=int(odometer_miles),
               tire_position=tire_position, charge_component="installation_package", amount=amt,
               remaining_tread_32nds=0, damage_cause="not_applicable", source_event_id=source_event_id)
    return str({"tire_event_id": rid, "tire_service_id": tire_service_id, "charge_component": "installation_package",
                "tire_position": tire_position, "service_date": service_date, "amount": amt, "status": "booked"})


@tool(owner="agent", rw="write")
def post_treadwear_credit_0e44552f(ctx: ToolContext, tire_service_id: str, tire_position: str,
                                   source_event_id: str, amount: float) -> str:
    """Book a treadwear warranty credit for one wheel against the treadwear claim entry it settles.

    Member services uses this to post, on a Tire Center installation package, the pro-rata credit for a tire
    that wore out before its manufacturer's treadwear mileage, linked to that tire's treadwear claim entry.
    One call adds exactly one treadwear credit entry, dated today, for the wheel; the package's balance of
    Tire Center charges falls by the amount, and the credit then appears with the package's other charges
    and credits as applied toward that wheel's replacement. Nothing else on the package changes.

    Args:
        tire_service_id: Id class — the installation package reference number of the tire set, read from the Tire Center package lookup before the call.
        tire_position: Enum class — the wheel the credit is for, exactly one of: left_front when the worn tire was on the driver-side front wheel; right_front when it was on the passenger-side front wheel; left_rear when it was on the driver-side rear wheel; right_rear when it was on the passenger-side rear wheel; spare when the worn tire is the full-size spare; all_positions when one credit covers every wheel of the set at once.
        source_event_id: Id class — the reference number of the treadwear claim entry being credited, read from the package's Tire Center work history before the call.
        amount: Fixed-format class — the credit to book, in USD, 2 decimal places, >= 0 (pass the value already worked out to the cent; it is booked at 2 decimal places as given).

    Returns:
        A dictionary rendered as text: tire_event_id is the reference number of the new credit entry (text);
        tire_service_id is the package credited (text); charge_component is always treadwear_credit;
        tire_position is the wheel credited; service_date is today's date (YYYY-MM-DD); amount is the credit
        booked in USD with 2 decimal places; status is "booked" when the entry was added. A receipt with status
        "booked" means the credit now stands on the package.
    """
    amt = round(float(amount), 2)
    today = ctx.now()[:10]
    rid = ctx.make_id("tsv_", tire_service_id, tire_position, source_event_id, amt, today)
    ctx.create("tire_services", rid, tire_event_id=rid, tire_service_id=tire_service_id,
               customer_id=(ctx.find("tire_holdings", tire_service_id=tire_service_id) or [{}])[0].get("customer_id", ""),
               event_type="tire_service_credited", service_date=today, odometer_miles=0,
               tire_position=tire_position, charge_component="treadwear_credit", amount=amt,
               remaining_tread_32nds=0, damage_cause="not_applicable", source_event_id=source_event_id)
    return str({"tire_event_id": rid, "tire_service_id": tire_service_id, "charge_component": "treadwear_credit",
                "tire_position": tire_position, "service_date": today, "amount": amt, "status": "booked"})


@tool(owner="user", rw="write")
def accept_road_hazard_credit_d64b14f0(ctx: ToolContext, tire_service_id: str, tire_position: str,
                                       source_event_id: str, amount: float) -> str:
    """Accept, as the member, the road hazard credit offered for a tire replaced under road hazard protection.

    The member uses this to accept the road hazard adjustment member services has worked out for one wheel of
    their Tire Center installation package, linked to the road hazard replacement entry of that wheel. One call
    adds exactly one road hazard credit entry, dated today, for the wheel; the package's balance of Tire Center
    charges falls by the amount, and the accepted credit then appears with the package's other charges and
    credits as applied toward that wheel's replacement. Nothing else on the package changes.

    Args:
        tire_service_id: Id class — the installation package reference number of the member's tire set, as given to the member by member services.
        tire_position: Enum class — the wheel the credit is for, exactly one of: left_front when the damaged tire was on the driver-side front wheel; right_front when it was on the passenger-side front wheel; left_rear when it was on the driver-side rear wheel; right_rear when it was on the passenger-side rear wheel; spare when the damaged tire is the full-size spare; all_positions when one credit covers every wheel of the set at once.
        source_event_id: Id class — the reference number of the road hazard replacement entry being credited, as given to the member by member services.
        amount: Fixed-format class — the credit the member accepts, in USD, 2 decimal places, >= 0 (pass the value already worked out to the cent; it is booked at 2 decimal places as given).

    Returns:
        A dictionary rendered as text: tire_event_id is the reference number of the accepted credit entry (text);
        tire_service_id is the package credited (text); charge_component is always road_hazard_credit;
        tire_position is the wheel credited; service_date is today's date (YYYY-MM-DD); amount is the credit
        accepted in USD with 2 decimal places; status is "accepted" when the entry was added. A receipt with
        status "accepted" means the credit now stands on the package.
    """
    amt = round(float(amount), 2)
    today = ctx.now()[:10]
    rid = ctx.make_id("tsv_", tire_service_id, tire_position, source_event_id, amt, today, "rh")
    ctx.create("tire_services", rid, tire_event_id=rid, tire_service_id=tire_service_id,
               customer_id=(ctx.find("tire_holdings", tire_service_id=tire_service_id) or [{}])[0].get("customer_id", ""),
               event_type="tire_service_credited", service_date=today, odometer_miles=0,
               tire_position=tire_position, charge_component="road_hazard_credit", amount=amt,
               remaining_tread_32nds=0, damage_cause="not_applicable", source_event_id=source_event_id)
    return str({"tire_event_id": rid, "tire_service_id": tire_service_id, "charge_component": "road_hazard_credit",
                "tire_position": tire_position, "service_date": today, "amount": amt, "status": "accepted"})


@tool(owner="user", rw="write")
def authorize_rotation_charge_d4760d29(ctx: ToolContext, tire_service_id: str, service_date: str,
                                       odometer_miles: int, amount: float) -> str:
    """Authorise, as the member, the charge for a paid rotation visit on their Tire Center installation package.

    The member uses this to approve the rotation-and-balancing charge for one rotation work order on a package
    whose rotations are not free. One call adds exactly one rotation-and-balancing charge entry for the whole
    set, dated on that work order; the package's balance of Tire Center charges rises by the amount, and the
    authorised charge then appears with the package's other charges and credits. Nothing else on the package
    changes.

    Args:
        tire_service_id: Id class — the installation package reference number of the member's tire set, as given to the member by member services.
        service_date: Fixed-format class — the date of the rotation work order being authorised, written YYYY-MM-DD as given by member services (no time, no time zone).
        odometer_miles: Fixed-format class — the vehicle odometer on that rotation work order, an integer in integer miles with no separators or decimals.
        amount: Fixed-format class — the charge the member authorises, in USD, 2 decimal places, >= 0 (pass the value already worked out to the cent; it is booked at 2 decimal places as given).

    Returns:
        A dictionary rendered as text: tire_event_id is the reference number of the authorised charge entry (text);
        tire_service_id is the package charged (text); charge_component is always rotation_balance; tire_position is
        always all_positions; service_date is the work order date (YYYY-MM-DD); amount is the charge in USD with 2
        decimal places; status is "authorised" when the entry was added. A receipt with status "authorised" means the
        charge now stands on the package.
    """
    amt = round(float(amount), 2)
    rid = ctx.make_id("tsv_", tire_service_id, service_date, int(odometer_miles), amt, "rotation")
    ctx.create("tire_services", rid, tire_event_id=rid, tire_service_id=tire_service_id,
               customer_id=(ctx.find("tire_holdings", tire_service_id=tire_service_id) or [{}])[0].get("customer_id", ""),
               event_type="tire_service_charged", service_date=service_date, odometer_miles=int(odometer_miles),
               tire_position="all_positions", charge_component="rotation_balance", amount=amt,
               remaining_tread_32nds=0, damage_cause="not_applicable", source_event_id="")
    return str({"tire_event_id": rid, "tire_service_id": tire_service_id, "charge_component": "rotation_balance",
                "tire_position": "all_positions", "service_date": service_date, "amount": amt, "status": "authorised"})


@tool(owner="agent", rw="write")
def post_flat_repair_charge_9a2582c0(ctx: ToolContext, tire_service_id: str, tire_position: str, service_date: str,
                                     odometer_miles: int, amount: float) -> str:
    """Book the charge for a flat repair performed on one wheel of a Tire Center installation package.

    Member services uses this to post the charge for plugging and patching a repairable puncture in one tire,
    dated on the repair's work order. One call adds exactly one flat-repair charge entry for that wheel; the
    package's balance of Tire Center charges rises by the amount, and the entry then appears with the
    package's other charges and credits. Nothing else on the package changes.

    Args:
        tire_service_id: Id class — the installation package reference number of the tire set, read from the Tire Center package lookup before the call.
        tire_position: Enum class — the wheel whose tire was repaired, exactly one of: left_front when the repaired tire is on the driver-side front wheel; right_front when it is on the passenger-side front wheel; left_rear when it is on the driver-side rear wheel; right_rear when it is on the passenger-side rear wheel; spare when the repaired tire is the full-size spare; all_positions when one charge covers repairs on every wheel of the set at once.
        service_date: Fixed-format class — the date of the repair work order, written YYYY-MM-DD as on that work order entry (no time, no time zone).
        odometer_miles: Fixed-format class — the vehicle odometer on that repair work order, an integer in integer miles with no separators or decimals.
        amount: Fixed-format class — the charge to book, in USD, 2 decimal places, >= 0 (pass the value already worked out to the cent; it is booked at 2 decimal places as given).

    Returns:
        A dictionary rendered as text: tire_event_id is the reference number of the new charge entry (text);
        tire_service_id is the package charged (text); charge_component is always flat_repair; tire_position is the
        wheel charged; service_date is the work order date (YYYY-MM-DD); amount is the charge in USD with 2 decimal
        places; status is "booked" when the entry was added. A receipt with status "booked" means the charge now
        stands on the package.
    """
    amt = round(float(amount), 2)
    rid = ctx.make_id("tsv_", tire_service_id, tire_position, service_date, int(odometer_miles), amt, "flat")
    ctx.create("tire_services", rid, tire_event_id=rid, tire_service_id=tire_service_id,
               customer_id=(ctx.find("tire_holdings", tire_service_id=tire_service_id) or [{}])[0].get("customer_id", ""),
               event_type="tire_service_charged", service_date=service_date, odometer_miles=int(odometer_miles),
               tire_position=tire_position, charge_component="flat_repair", amount=amt,
               remaining_tread_32nds=0, damage_cause="not_applicable", source_event_id="")
    return str({"tire_event_id": rid, "tire_service_id": tire_service_id, "charge_component": "flat_repair",
                "tire_position": tire_position, "service_date": service_date, "amount": amt, "status": "booked"})

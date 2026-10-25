"""Hidden task tools of the prepaid_maintenance_plans difficulty (Kessler Care Prepaid Maintenance Plans).

Each tool performs one atomic write on the maintenance records with the values the caller passes;
none of them checks a business condition, computes a price or refund, or refuses a call.
"""

from erlbench import ToolContext, tool


_RETAIL_VISITS = {
    "Kessler Care Essentials 2-Visit": 2,
    "Kessler Care Essentials 4-Visit": 4,
    "Kessler Care Plus 6-Visit": 6,
    "Kessler Care Plus 8-Visit": 8,
    "Kessler Care Premium 10-Visit": 10,
}

class _Fmt:
    """Format helpers shared by the tools below (half-up rounding without binary floating-point rounding)."""

    @staticmethod
    def _half_up(value, places):
        text = str(value).strip()
        if "e" in text or "E" in text:
            text = "%.12f" % float(text)
        negative = text.startswith("-")
        text = text.lstrip("+-")
        whole, _, frac = text.partition(".")
        frac = frac + "0" * (places + 1)
        scaled = int(whole or "0") * (10 ** places) + int(frac[:places] or "0")
        if frac[places] >= "5":
            scaled += 1
        return -scaled if negative else scaled

    @staticmethod
    def money(value):
        cents = _Fmt._half_up(value, 2)
        return cents / 100.0

    @staticmethod
    def miles(value):
        return _Fmt._half_up(value, 0)

    @staticmethod
    def day(value):
        return str(value).strip()[:10]


@tool(owner="user", rw="write")
def sign_fleet_care_addendum_ac106112(ctx: ToolContext, customer_id: str, vehicle_id: str, selling_store_id: str,
                                      odometer_at_sale: int, expiration_date: str, expiration_odometer: int,
                                      purchase_price: float) -> str:
    """The fleet customer signs a Kessler Care Fleet 12-Visit plan addendum for one of its units, buying the plan on its own (not on a vehicle purchase deal, not financed, no lienholder). Signing opens a new active Fleet 12-Visit plan on that unit dated today, with a plan contract number, the term end date and term end odometer and the price given, and loads the plan's twelve included visits. Success is the receipt below with status active and twelve visits remaining; the new plan then appears among the customer's maintenance plans.

    Args:
        customer_id: Id class — the reference number of the fleet customer's profile that holds the new plan, as returned by the customer lookup.
        vehicle_id: Id class — the reference number of the unit the plan covers, as returned by the vehicle lookup for this customer.
        selling_store_id: Id class — the reference number of the store the plan is written for, as returned by the store lookup.
        odometer_at_sale: Fixed-format class — the unit's odometer reading at signing, in integer miles (whole miles, no separators).
        expiration_date: Fixed-format class — the last calendar day of the plan term, written YYYY-MM-DD.
        expiration_odometer: Fixed-format class — the odometer reading at which the plan term ends, in integer miles (whole miles, no separators).
        purchase_price: Fixed-format class — the price the customer pays for the plan, in US dollars to 2 decimal places, rounded half up to the cent.

    Returns:
        A text receipt listing: maintenance_plan_id (reference number of the new plan), plan_number (plan contract number printed on the certificate), variant_name (always Kessler Care Fleet 12-Visit), status (active on success), sale_date (YYYY-MM-DD, today), expiration_date (YYYY-MM-DD), expiration_odometer (whole miles), purchase_price (USD, two decimals) and visits_remaining (integer visits loaded, twelve).
    """
    sale_date = ctx.now()[:10]
    price = _Fmt.money(purchase_price)
    expiration_date = _Fmt.day(expiration_date)
    odometer_at_sale = _Fmt.miles(odometer_at_sale)
    expiration_odometer = _Fmt.miles(expiration_odometer)
    pid = ctx.make_id("mp_", customer_id, vehicle_id, selling_store_id, odometer_at_sale, expiration_date,
                      expiration_odometer, price)
    plan_number = "KC-3" + str(int(pid[-10:], 16))[-6:].zfill(6)
    ctx.create("maintenance_plans", pid, maintenance_plan_id=pid, customer_id=customer_id, vehicle_id=vehicle_id,
               selling_store_id=selling_store_id, purchase_deal_id=None, variant_name="Kessler Care Fleet 12-Visit",
               status="active", plan_number=plan_number, sale_date=sale_date, expiration_date=expiration_date,
               odometer_at_sale=int(odometer_at_sale), expiration_odometer=int(expiration_odometer),
               purchase_price=price, financed_on_contract="false", lienholder_name="", visits_remaining=12,
               refund_due_balance=0.0, closed_date="")
    eid = ctx.make_id("me_", pid, "maintenance_visits_loaded", sale_date)
    ctx.create("maintenance_plan_ledger", eid, maintenance_entry_id=eid, maintenance_plan_id=pid,
               customer_id=customer_id, event_type="maintenance_visits_loaded", entry_date=sale_date, visits=12,
               amount=0.0, visit_number=0, repair_order_number="", store_id=None, odometer="", source_entry_id=None,
               cancel_reason="not_applicable", refund_payee="not_applicable")
    return (f"maintenance_plan_id={pid}; plan_number={plan_number}; variant_name=Kessler Care Fleet 12-Visit; "
            f"status=active; sale_date={sale_date}; expiration_date={expiration_date}; "
            f"expiration_odometer={int(expiration_odometer)}; purchase_price={price:.2f}; visits_remaining=12")


@tool(owner="user", rw="write")
def sign_care_plan_contract_c0d53aa0(ctx: ToolContext, customer_id: str, vehicle_id: str, selling_store_id: str,
                                     variant_name: str, odometer_at_sale: int, expiration_date: str,
                                     expiration_odometer: int, purchase_price: float) -> str:
    """The individual customer signs a Kessler Care retail plan contract (Essentials, Plus or Premium) for a vehicle they own, buying the plan on its own (not on a vehicle purchase deal, not financed, no lienholder). Signing opens a new active plan of the chosen name on that vehicle dated today, with a plan contract number, the term end date and term end odometer and the price given, and loads the visits that plan includes. Success is the receipt below with status active; the new plan then appears among the customer's maintenance plans.

    Args:
        customer_id: Id class — the reference number of the customer's profile that holds the new plan, as returned by the customer lookup.
        vehicle_id: Id class — the reference number of the vehicle the plan covers, as returned by the vehicle lookup for this customer.
        selling_store_id: Id class — the reference number of the store the plan is written for, as returned by the store lookup.
        variant_name: Enum class — the plan the customer buys, written as its official name: Kessler Care Essentials 2-Visit when the customer chooses the two-visit Essentials plan; Kessler Care Essentials 4-Visit when the customer chooses the four-visit Essentials plan; Kessler Care Plus 6-Visit when the customer chooses the six-visit Plus plan; Kessler Care Plus 8-Visit when the customer chooses the eight-visit Plus plan; Kessler Care Premium 10-Visit when the customer chooses the ten-visit Premium plan; Kessler Care Fleet 12-Visit only when the buyer is a fleet business, which a retail contract never is, so an individual customer's contract never takes it.
        odometer_at_sale: Fixed-format class — the vehicle's odometer reading at signing, in integer miles (whole miles, no separators).
        expiration_date: Fixed-format class — the last calendar day of the plan term, written YYYY-MM-DD.
        expiration_odometer: Fixed-format class — the odometer reading at which the plan term ends, in integer miles (whole miles, no separators).
        purchase_price: Fixed-format class — the price the customer pays for the plan, in US dollars to 2 decimal places, rounded half up to the cent.

    Returns:
        A text receipt listing: maintenance_plan_id (reference number of the new plan), plan_number (plan contract number printed on the certificate), variant_name (the plan name signed), status (active on success), sale_date (YYYY-MM-DD, today), expiration_date (YYYY-MM-DD), expiration_odometer (whole miles), purchase_price (USD, two decimals) and visits_remaining (integer visits loaded for that plan).
    """
    sale_date = ctx.now()[:10]
    price = _Fmt.money(purchase_price)
    expiration_date = _Fmt.day(expiration_date)
    odometer_at_sale = _Fmt.miles(odometer_at_sale)
    expiration_odometer = _Fmt.miles(expiration_odometer)
    visits = _RETAIL_VISITS.get(variant_name, 0)
    pid = ctx.make_id("mp_", customer_id, vehicle_id, selling_store_id, variant_name, odometer_at_sale,
                      expiration_date, expiration_odometer, price)
    plan_number = "KC-3" + str(int(pid[-10:], 16))[-6:].zfill(6)
    ctx.create("maintenance_plans", pid, maintenance_plan_id=pid, customer_id=customer_id, vehicle_id=vehicle_id,
               selling_store_id=selling_store_id, purchase_deal_id=None, variant_name=variant_name, status="active",
               plan_number=plan_number, sale_date=sale_date, expiration_date=expiration_date,
               odometer_at_sale=int(odometer_at_sale), expiration_odometer=int(expiration_odometer),
               purchase_price=price, financed_on_contract="false", lienholder_name="", visits_remaining=visits,
               refund_due_balance=0.0, closed_date="")
    eid = ctx.make_id("me_", pid, "maintenance_visits_loaded", sale_date)
    ctx.create("maintenance_plan_ledger", eid, maintenance_entry_id=eid, maintenance_plan_id=pid,
               customer_id=customer_id, event_type="maintenance_visits_loaded", entry_date=sale_date, visits=visits,
               amount=0.0, visit_number=0, repair_order_number="", store_id=None, odometer="", source_entry_id=None,
               cancel_reason="not_applicable", refund_payee="not_applicable")
    return (f"maintenance_plan_id={pid}; plan_number={plan_number}; variant_name={variant_name}; status=active; "
            f"sale_date={sale_date}; expiration_date={expiration_date}; expiration_odometer={int(expiration_odometer)}; "
            f"purchase_price={price:.2f}; visits_remaining={visits}")


@tool(owner="agent", rw="write")
def process_fleet_plan_cancellation_44bd9d69(ctx: ToolContext, maintenance_plan_id: str,
                                             maintenance_cancel_request_id: str, refund_amount: float) -> str:
    """Process the holder's signed cancellation request on a Kessler Care Fleet 12-Visit plan cancelled for a reason other than a total loss. The plan becomes cancelled with its closing date set to the request date; its unused visits are removed in one cancellation entry carrying the request's reason; one refund calculation entry records the refund amount given, dated the request date with the request's reason and certified odometer; the plan's refund due rises by that amount; and the request is marked completed. Success is the receipt below with status cancelled.

    Args:
        maintenance_plan_id: Id class — the reference number of the fleet plan being cancelled, as returned by the maintenance plan lookup.
        maintenance_cancel_request_id: Id class — the reference number of the holder's signed cancellation request for that plan, as returned by the cancellation request lookup.
        refund_amount: Fixed-format class — the cancellation refund due on the plan, in US dollars to 2 decimal places, rounded half up to the cent, 0.00 when nothing is refunded.

    Returns:
        A text receipt listing: maintenance_plan_id, status (cancelled on success), closed_date (YYYY-MM-DD, the request date), visits_cancelled (integer visits removed), refund_entry_id (reference number of the refund calculation entry), refund_amount (USD, two decimals), refund_due_balance (USD, two decimals, the plan's refund now due) and request_status (completed).
    """
    req = (ctx.find("maintenance_cancellation_requests", maintenance_cancel_request_id=maintenance_cancel_request_id)
           or [{}])[0]
    plan = (ctx.find("maintenance_plans", maintenance_plan_id=maintenance_plan_id) or [{}])[0]
    reason = req.get("cancel_reason") or "customer_request"
    eff = req.get("request_date") or ctx.now()[:10]
    odo = req.get("odometer_at_request", "")
    visits = int(plan.get("visits_remaining") or 0)
    amount = _Fmt.money(refund_amount)
    due = _Fmt.money(_Fmt._half_up(plan.get("refund_due_balance") or 0, 2) / 100.0 + amount)
    ctx.update("maintenance_plans", maintenance_plan_id, status="cancelled", closed_date=eff, visits_remaining=0,
               refund_due_balance=due)
    cid = ctx.make_id("me_", maintenance_plan_id, "maintenance_visits_cancelled", eff)
    ctx.create("maintenance_plan_ledger", cid, maintenance_entry_id=cid, maintenance_plan_id=maintenance_plan_id,
               customer_id=plan.get("customer_id", ""), event_type="maintenance_visits_cancelled", entry_date=eff,
               visits=visits, amount=0.0, visit_number=0, repair_order_number="", store_id=None, odometer="",
               source_entry_id=None, cancel_reason=reason, refund_payee="not_applicable")
    rid = ctx.make_id("me_", maintenance_plan_id, "maintenance_refund_calculated", eff, amount)
    ctx.create("maintenance_plan_ledger", rid, maintenance_entry_id=rid, maintenance_plan_id=maintenance_plan_id,
               customer_id=plan.get("customer_id", ""), event_type="maintenance_refund_calculated", entry_date=eff,
               visits=0, amount=amount, visit_number=0, repair_order_number="", store_id=None, odometer=odo,
               source_entry_id=None, cancel_reason=reason, refund_payee="not_applicable")
    ctx.update("maintenance_cancellation_requests", maintenance_cancel_request_id, request_status="completed")
    return (f"maintenance_plan_id={maintenance_plan_id}; status=cancelled; closed_date={eff}; visits_cancelled={visits}; "
            f"refund_entry_id={rid}; refund_amount={amount:.2f}; refund_due_balance={due:.2f}; request_status=completed")


@tool(owner="agent", rw="write")
def process_total_loss_cancellation_8f67308a(ctx: ToolContext, maintenance_plan_id: str,
                                             maintenance_cancel_request_id: str, refund_amount: float) -> str:
    """Process the holder's signed cancellation request on any Kessler Care plan whose vehicle is a total loss. The plan becomes cancelled with its closing date set to the request date; its unused visits are removed in one cancellation entry carrying the request's reason; one refund calculation entry records the refund amount given, dated the request date with the request's reason and certified odometer; the plan's refund due rises by that amount; and the request is marked completed. Success is the receipt below with status cancelled.

    Args:
        maintenance_plan_id: Id class — the reference number of the plan being cancelled, as returned by the maintenance plan lookup.
        maintenance_cancel_request_id: Id class — the reference number of the holder's signed total-loss cancellation request for that plan, as returned by the cancellation request lookup.
        refund_amount: Fixed-format class — the cancellation refund due on the plan, in US dollars to 2 decimal places, rounded half up to the cent, 0.00 when nothing is refunded.

    Returns:
        A text receipt listing: maintenance_plan_id, status (cancelled on success), closed_date (YYYY-MM-DD, the request date), visits_cancelled (integer visits removed), refund_entry_id (reference number of the refund calculation entry), refund_amount (USD, two decimals), refund_due_balance (USD, two decimals, the plan's refund now due) and request_status (completed).
    """
    req = (ctx.find("maintenance_cancellation_requests", maintenance_cancel_request_id=maintenance_cancel_request_id)
           or [{}])[0]
    plan = (ctx.find("maintenance_plans", maintenance_plan_id=maintenance_plan_id) or [{}])[0]
    reason = req.get("cancel_reason") or "total_loss"
    eff = req.get("request_date") or ctx.now()[:10]
    odo = req.get("odometer_at_request", "")
    visits = int(plan.get("visits_remaining") or 0)
    amount = _Fmt.money(refund_amount)
    due = _Fmt.money(_Fmt._half_up(plan.get("refund_due_balance") or 0, 2) / 100.0 + amount)
    ctx.update("maintenance_plans", maintenance_plan_id, status="cancelled", closed_date=eff, visits_remaining=0,
               refund_due_balance=due)
    cid = ctx.make_id("me_", maintenance_plan_id, "maintenance_visits_cancelled", eff)
    ctx.create("maintenance_plan_ledger", cid, maintenance_entry_id=cid, maintenance_plan_id=maintenance_plan_id,
               customer_id=plan.get("customer_id", ""), event_type="maintenance_visits_cancelled", entry_date=eff,
               visits=visits, amount=0.0, visit_number=0, repair_order_number="", store_id=None, odometer="",
               source_entry_id=None, cancel_reason=reason, refund_payee="not_applicable")
    rid = ctx.make_id("me_", maintenance_plan_id, "maintenance_refund_calculated", eff, amount)
    ctx.create("maintenance_plan_ledger", rid, maintenance_entry_id=rid, maintenance_plan_id=maintenance_plan_id,
               customer_id=plan.get("customer_id", ""), event_type="maintenance_refund_calculated", entry_date=eff,
               visits=0, amount=amount, visit_number=0, repair_order_number="", store_id=None, odometer=odo,
               source_entry_id=None, cancel_reason=reason, refund_payee="not_applicable")
    ctx.update("maintenance_cancellation_requests", maintenance_cancel_request_id, request_status="completed")
    return (f"maintenance_plan_id={maintenance_plan_id}; status=cancelled; closed_date={eff}; visits_cancelled={visits}; "
            f"refund_entry_id={rid}; refund_amount={amount:.2f}; refund_due_balance={due:.2f}; request_status=completed")


@tool(owner="agent", rw="write")
def process_care_plan_cancellation_e800fe25(ctx: ToolContext, maintenance_plan_id: str,
                                            maintenance_cancel_request_id: str, refund_amount: float) -> str:
    """Process the holder's signed cancellation request on a Kessler Care Essentials, Plus or Premium plan cancelled for a reason other than a total loss. The plan becomes cancelled with its closing date set to the request date; its unused visits are removed in one cancellation entry carrying the request's reason; one refund calculation entry records the refund amount given, dated the request date with the request's reason and certified odometer; the plan's refund due rises by that amount; and the request is marked completed. Success is the receipt below with status cancelled.

    Args:
        maintenance_plan_id: Id class — the reference number of the retail plan being cancelled, as returned by the maintenance plan lookup.
        maintenance_cancel_request_id: Id class — the reference number of the holder's signed cancellation request for that plan, as returned by the cancellation request lookup.
        refund_amount: Fixed-format class — the cancellation refund due on the plan, in US dollars to 2 decimal places, rounded half up to the cent, 0.00 when nothing is refunded.

    Returns:
        A text receipt listing: maintenance_plan_id, status (cancelled on success), closed_date (YYYY-MM-DD, the request date), visits_cancelled (integer visits removed), refund_entry_id (reference number of the refund calculation entry), refund_amount (USD, two decimals), refund_due_balance (USD, two decimals, the plan's refund now due) and request_status (completed).
    """
    req = (ctx.find("maintenance_cancellation_requests", maintenance_cancel_request_id=maintenance_cancel_request_id)
           or [{}])[0]
    plan = (ctx.find("maintenance_plans", maintenance_plan_id=maintenance_plan_id) or [{}])[0]
    reason = req.get("cancel_reason") or "customer_request"
    eff = req.get("request_date") or ctx.now()[:10]
    odo = req.get("odometer_at_request", "")
    visits = int(plan.get("visits_remaining") or 0)
    amount = _Fmt.money(refund_amount)
    due = _Fmt.money(_Fmt._half_up(plan.get("refund_due_balance") or 0, 2) / 100.0 + amount)
    ctx.update("maintenance_plans", maintenance_plan_id, status="cancelled", closed_date=eff, visits_remaining=0,
               refund_due_balance=due)
    cid = ctx.make_id("me_", maintenance_plan_id, "maintenance_visits_cancelled", eff)
    ctx.create("maintenance_plan_ledger", cid, maintenance_entry_id=cid, maintenance_plan_id=maintenance_plan_id,
               customer_id=plan.get("customer_id", ""), event_type="maintenance_visits_cancelled", entry_date=eff,
               visits=visits, amount=0.0, visit_number=0, repair_order_number="", store_id=None, odometer="",
               source_entry_id=None, cancel_reason=reason, refund_payee="not_applicable")
    rid = ctx.make_id("me_", maintenance_plan_id, "maintenance_refund_calculated", eff, amount)
    ctx.create("maintenance_plan_ledger", rid, maintenance_entry_id=rid, maintenance_plan_id=maintenance_plan_id,
               customer_id=plan.get("customer_id", ""), event_type="maintenance_refund_calculated", entry_date=eff,
               visits=0, amount=amount, visit_number=0, repair_order_number="", store_id=None, odometer=odo,
               source_entry_id=None, cancel_reason=reason, refund_payee="not_applicable")
    ctx.update("maintenance_cancellation_requests", maintenance_cancel_request_id, request_status="completed")
    return (f"maintenance_plan_id={maintenance_plan_id}; status=cancelled; closed_date={eff}; visits_cancelled={visits}; "
            f"refund_entry_id={rid}; refund_amount={amount:.2f}; refund_due_balance={due:.2f}; request_status=completed")


@tool(owner="agent", rw="write")
def move_fleet_plan_badb11fe(ctx: ToolContext, maintenance_plan_id: str, replacement_vehicle_id: str,
                             expiration_odometer: int) -> str:
    """Move an active Kessler Care Fleet 12-Visit plan from a unit the fleet has retired onto the unit that replaced it. The plan's covered vehicle becomes the replacement unit and its term end odometer becomes the reading given; its sale date, term end date, visits remaining and price stay as they are. Success is the receipt below showing the replacement unit as the covered vehicle.

    Args:
        maintenance_plan_id: Id class — the reference number of the fleet plan being moved, as returned by the maintenance plan lookup.
        replacement_vehicle_id: Id class — the reference number of the replacement unit, as returned by the vehicle lookup for this customer.
        expiration_odometer: Fixed-format class — the odometer reading on the replacement unit at which the plan term ends, in integer miles (whole miles, no separators).

    Returns:
        A text receipt listing: maintenance_plan_id, previous_vehicle_id (the retired unit's reference number), vehicle_id (the replacement unit now covered), expiration_odometer (whole miles) and status (unchanged, normally active).
    """
    plan = (ctx.find("maintenance_plans", maintenance_plan_id=maintenance_plan_id) or [{}])[0]
    previous = plan.get("vehicle_id", "")
    expiration_odometer = _Fmt.miles(expiration_odometer)
    ctx.update("maintenance_plans", maintenance_plan_id, vehicle_id=replacement_vehicle_id,
               expiration_odometer=int(expiration_odometer))
    return (f"maintenance_plan_id={maintenance_plan_id}; previous_vehicle_id={previous}; "
            f"vehicle_id={replacement_vehicle_id}; expiration_odometer={int(expiration_odometer)}; "
            f"status={plan.get('status', '')}")

"""Hidden task tools for the autoship_subscription_care difficulty of env_0040_pet_supplies_retailer.

Each tool performs one atomic change on a Tailwise Autoship subscription. The agent reaches an
agent-owned tool through unlock_agent_discoverable_tool -> call_agent_discoverable_tool; the
customer runs a user-owned tool after the agent unlocks it with unlock_user_discoverable_tool and
hands it over. No tool judges eligibility, timing or the value it is given: every value is worked
out by the agent from the Autoship policies and the customer's records before the call.
"""

from erlbench import ToolContext, tool


@tool(owner="agent", rw="write")
def set_rx_shipment_packages_d23afb64(ctx: ToolContext, autoship_id: str, quantity: int) -> str:
    """Set how many packages each shipment of a prescription Autoship (Autoship Pharmacy or
    Autoship Compounded Pharmacy) carries. The care agent performs this on one existing
    subscription; on success the subscription's units per shipment become the number given, every
    shipment processed from then on carries that many packages of the linked prescription, and the
    item, delivery frequency, next ship date and linked prescription stay unchanged. The customer
    sees the new package count on the subscription right away.

    Args:
        autoship_id: Id class — the reference number of the prescription Autoship subscription whose
            package count is set, read from the customer's Autoship subscriptions lookup.
        quantity: Fixed-format class — the packages each shipment carries from now on, a value in the format
            integer, units (whole packages, no decimals).

    Returns:
        A text rendering of a dictionary with three fields: "autoship_id" (string, the subscription
        reference number that was updated), "quantity" (integer, the packages per shipment now on
        the subscription) and "status" (string, always "updated" when the change was saved). The
        presence of status "updated" is the success receipt.
    """
    ctx.update("autoship_subscriptions", autoship_id, quantity=int(quantity))
    return str({"autoship_id": autoship_id, "quantity": int(quantity), "status": "updated"})


@tool(owner="agent", rw="write")
def set_rx_shipment_interval_b175142c(ctx: ToolContext, autoship_id: str, frequency_weeks: int) -> str:
    """Set the delivery frequency, in weeks between shipments, of a prescription Autoship (Autoship
    Pharmacy or Autoship Compounded Pharmacy). The care agent performs this on one existing
    subscription; on success the subscription's frequency becomes the number of weeks given and
    every shipment after the upcoming one is scheduled that many weeks after the previous one,
    while the packages per shipment, the item, the linked prescription and the already scheduled
    next ship date stay unchanged. The customer sees the new frequency on the subscription right
    away.

    Args:
        autoship_id: Id class — the reference number of the prescription Autoship subscription whose
            frequency is set, read from the customer's Autoship subscriptions lookup.
        frequency_weeks: Fixed-format class — the number of weeks between shipments from now on, a value in the
            format integer, weeks (whole weeks, no decimals).

    Returns:
        A text rendering of a dictionary with three fields: "autoship_id" (string, the subscription
        reference number that was updated), "frequency_weeks" (integer, the weeks between shipments
        now on the subscription) and "status" (string, always "updated" when the change was saved).
        The presence of status "updated" is the success receipt.
    """
    ctx.update("autoship_subscriptions", autoship_id, frequency_weeks=int(frequency_weeks))
    return str({"autoship_id": autoship_id, "frequency_weeks": int(frequency_weeks), "status": "updated"})


@tool(owner="agent", rw="write")
def set_shipment_interval_36e38cde(ctx: ToolContext, autoship_id: str, frequency_weeks: int) -> str:
    """Set the delivery frequency, in weeks between shipments, of a non-prescription Autoship
    (Autoship Everyday, Autoship Litter & Bulk, Autoship Fresh & Frozen or Autoship Custom Meal
    Plan). The care agent performs this on one existing subscription; on success the subscription's
    frequency becomes the number of weeks given and every shipment after the upcoming one is
    scheduled that many weeks after the previous one, while the units per shipment, the item and
    the already scheduled next ship date stay unchanged. The customer sees the new frequency on the
    subscription right away.

    Args:
        autoship_id: Id class — the reference number of the non-prescription Autoship subscription
            whose frequency is set, read from the customer's Autoship subscriptions lookup.
        frequency_weeks: Fixed-format class — the number of weeks between shipments from now on, a value in the
            format integer, weeks (whole weeks, no decimals).

    Returns:
        A text rendering of a dictionary with three fields: "autoship_id" (string, the subscription
        reference number that was updated), "frequency_weeks" (integer, the weeks between shipments
        now on the subscription) and "status" (string, always "updated" when the change was saved).
        The presence of status "updated" is the success receipt.
    """
    ctx.update("autoship_subscriptions", autoship_id, frequency_weeks=int(frequency_weeks))
    return str({"autoship_id": autoship_id, "frequency_weeks": int(frequency_weeks), "status": "updated"})


@tool(owner="agent", rw="write")
def set_shipment_quantity_8a323a9d(ctx: ToolContext, autoship_id: str, quantity: int) -> str:
    """Set how many units of the item each shipment of a non-prescription Autoship (Autoship
    Everyday, Autoship Litter & Bulk, Autoship Fresh & Frozen or Autoship Custom Meal Plan) carries.
    The care agent performs this on one existing subscription; on success the subscription's units
    per shipment become the number given and every shipment processed from then on carries that
    many units, while the item, the delivery frequency and the next ship date stay unchanged. The
    customer sees the new quantity on the subscription right away.

    Args:
        autoship_id: Id class — the reference number of the non-prescription Autoship subscription
            whose quantity is set, read from the customer's Autoship subscriptions lookup.
        quantity: Fixed-format class — the units of the item each shipment carries from now on, a value in the
            format integer, units (whole units, no decimals).

    Returns:
        A text rendering of a dictionary with three fields: "autoship_id" (string, the subscription
        reference number that was updated), "quantity" (integer, the units per shipment now on the
        subscription) and "status" (string, always "updated" when the change was saved). The
        presence of status "updated" is the success receipt.
    """
    ctx.update("autoship_subscriptions", autoship_id, quantity=int(quantity))
    return str({"autoship_id": autoship_id, "quantity": int(quantity), "status": "updated"})


@tool(owner="user", rw="write")
def enroll_rx_autoship_732fccd3(ctx: ToolContext, customer_id: str, pet_id: str, rx_prescription_id: str, sku: str,
                                item_description: str, unit_price_usd: float, quantity: int, frequency_weeks: int,
                                next_ship_date: str) -> str:
    """Open a new Autoship Pharmacy subscription in the customer's own name for one prescription
    item kept on file for one of their pets. The customer runs this themselves to authorize the
    recurring charges on their card; on success a new subscription is created in status
    pending_first_shipment, linked to the pet and to the prescription, carrying the item number,
    description and price per package given, the packages per shipment, the weeks between
    shipments and the first ship date given, with nothing billed yet. The customer can see the new
    subscription and its reference number at once; the first shipment is charged on the first ship
    date.

    Args:
        customer_id: Id class — the customer reference number of the account the subscription is
            opened on, read from the customer profile lookup.
        pet_id: Id class — the reference number of the pet the prescription is written for, read
            from the pet profiles lookup.
        rx_prescription_id: Id class — the reference number of the prescription kept on file that
            the subscription fills, read from the prescriptions lookup.
        sku: Fixed-format class — the item number of the package dispensed under the prescription,
            written as TW- followed by 6 digits, exactly as the prescription record shows it.
        item_description: Verbatim class — the medication or diet name exactly as the prescription
            record shows it in its medication field, copied character for character with no
            translation, normalisation, summarisation, addition or deletion (verbatim).
        unit_price_usd: Fixed-format class — the catalog price of one package in USD, a number with
            2 decimal places exactly as the prescription record shows it (no rounding applied by
            this action).
        quantity: Fixed-format class — the packages each shipment carries, a value in the format integer, units
            (whole packages, no decimals).
        frequency_weeks: Fixed-format class — the number of weeks between shipments, a value in the format
            integer, weeks (whole weeks, no decimals).
        next_ship_date: Fixed-format class — the first ship date the customer chose, as a calendar
            date in YYYY-MM-DD format (store-local date, no time part).

    Returns:
        A text rendering of a dictionary with six fields: "autoship_id" (string, the reference
        number of the new subscription), "variant_name" (string, always "Autoship Pharmacy"),
        "status" (string, always "pending_first_shipment"), "quantity" (integer, packages per
        shipment), "frequency_weeks" (integer, weeks between shipments) and "next_ship_date"
        (string, YYYY-MM-DD, the first ship date). A returned autoship_id with status
        "pending_first_shipment" is the success receipt.
    """
    rid = ctx.make_id("as_", customer_id, pet_id, rx_prescription_id, sku, item_description, unit_price_usd, quantity,
                      frequency_weeks, next_ship_date)
    ctx.create("autoship_subscriptions", rid, autoship_id=rid, customer_id=customer_id, pet_id=pet_id,
               variant_name="Autoship Pharmacy", status="pending_first_shipment", sku=sku, item_description=item_description,
               quantity=int(quantity), unit_price_usd=round(float(unit_price_usd), 2), frequency_weeks=int(frequency_weeks),
               next_ship_date=next_ship_date, enrolled_on=ctx.now()[:10], rx_prescription_id=rx_prescription_id,
               billed_total_usd=0.0)
    return str({"autoship_id": rid, "variant_name": "Autoship Pharmacy", "status": "pending_first_shipment",
                "quantity": int(quantity), "frequency_weeks": int(frequency_weeks), "next_ship_date": next_ship_date})


@tool(owner="user", rw="write")
def enroll_everyday_autoship_7ae73b8d(ctx: ToolContext, customer_id: str, pet_id: str, rx_prescription_id: str, sku: str,
                                      item_description: str, unit_price_usd: float, item_weight_lb: float, quantity: int,
                                      frequency_weeks: int, next_ship_date: str) -> str:
    """Open a new Autoship Everyday subscription in the customer's own name for one standard
    catalog item for one of their pets. The customer runs this themselves to authorize the
    recurring charges on their card; on success a new subscription is created in status
    pending_first_shipment, linked to the pet, carrying the item number, description, price and
    shipping weight per unit given, the units per shipment, the weeks between shipments and the
    first ship date given, with nothing billed yet. The customer can see the new subscription and
    its reference number at once; the first shipment is charged on the first ship date.

    Args:
        customer_id: Id class — the customer reference number of the account the subscription is
            opened on, read from the customer profile lookup.
        pet_id: Id class — the reference number of the pet the item is for, read from the pet
            profiles lookup.
        rx_prescription_id: Id class — the reference number of a linked prescription; standard
            catalog items carry none, so it is the empty value the household's existing Autoship of
            the item shows for its linked prescription in the Autoship subscriptions lookup.
        sku: Fixed-format class — the item number, written as TW- followed by 6 digits, exactly as
            the household's existing Autoship of the item shows it.
        item_description: Verbatim class — the catalog description of the item exactly as the
            household's existing Autoship of the item shows it, copied character for character with
            no translation, normalisation, summarisation, addition or deletion (verbatim).
        unit_price_usd: Fixed-format class — the catalog price of one unit in USD, a number with 2
            decimal places exactly as the existing Autoship of the item shows it (no rounding
            applied by this action).
        item_weight_lb: Fixed-format class — the shipping weight of one unit in pounds, a number with
            1 decimal place exactly as the existing Autoship of the item shows it.
        quantity: Fixed-format class — the units of the item each shipment carries, a value in the format
            integer, units (whole units, no decimals).
        frequency_weeks: Fixed-format class — the number of weeks between shipments, a value in the format
            integer, weeks (whole weeks, no decimals).
        next_ship_date: Fixed-format class — the first ship date the customer chose, as a calendar
            date in YYYY-MM-DD format (store-local date, no time part).

    Returns:
        A text rendering of a dictionary with six fields: "autoship_id" (string, the reference
        number of the new subscription), "variant_name" (string, always "Autoship Everyday"),
        "status" (string, always "pending_first_shipment"), "quantity" (integer, units per
        shipment), "frequency_weeks" (integer, weeks between shipments) and "next_ship_date"
        (string, YYYY-MM-DD, the first ship date). A returned autoship_id with status
        "pending_first_shipment" is the success receipt.
    """
    rid = ctx.make_id("as_", customer_id, pet_id, rx_prescription_id, sku, item_description, unit_price_usd, item_weight_lb,
                      quantity, frequency_weeks, next_ship_date)
    ctx.create("autoship_subscriptions", rid, autoship_id=rid, customer_id=customer_id, pet_id=pet_id,
               variant_name="Autoship Everyday", status="pending_first_shipment", sku=sku, item_description=item_description,
               quantity=int(quantity), unit_price_usd=round(float(unit_price_usd), 2), item_weight_lb=round(float(item_weight_lb), 1),
               frequency_weeks=int(frequency_weeks), next_ship_date=next_ship_date, enrolled_on=ctx.now()[:10],
               rx_prescription_id=rx_prescription_id or None, billed_total_usd=0.0)
    return str({"autoship_id": rid, "variant_name": "Autoship Everyday", "status": "pending_first_shipment",
                "quantity": int(quantity), "frequency_weeks": int(frequency_weeks), "next_ship_date": next_ship_date})

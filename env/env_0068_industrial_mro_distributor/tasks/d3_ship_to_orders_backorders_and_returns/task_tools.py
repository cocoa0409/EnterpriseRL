"""Hidden task tools of d3_ship_to_orders_backorders_and_returns (Ship-To Fulfillment Account).

Each tool performs one atomic write on the ship-to ledger with the values the caller supplies;
none of them checks a business precondition or works out a value for the caller.
"""

from erlbench import ToolContext, tool


@tool(owner="agent", rw="write")
def record_anniversary_review_a2ef3cef(ctx: ToolContext, ship_to_id: str, variant_name: str) -> str:
    """Record the anniversary service-level review of one Ship-To Fulfillment Account. The call sets
    the service level the delivery location holds from today to the level supplied and stamps today's
    date as the location's most recent review date; nothing else on the location, its orders or its
    returns changes. Once stored, the ship-to lookup shows the new service level and review date.

    Args:
        ship_to_id: Id class — the internal identifier of the ship-to (delivery location) being
            reviewed, as returned by the ship-to account lookup for the customer.
        variant_name: Enum class — the service level the location holds once the review is recorded,
            spelled exactly as one of: Corbett Parcel Ship-To when the location is to hold the parcel
            level; Corbett Standard Ship-To when it is to hold the standard level; Corbett Priority
            Ship-To when it is to hold the priority level; Corbett Route Delivery Ship-To when it is to
            hold the route delivery level; Corbett Premier Route Ship-To when it is to hold the premier
            route level; Corbett Dedicated Delivery Ship-To when it is to hold the dedicated delivery level.

    Returns:
        A dictionary receipt: status is the word recorded when the review was stored; ship_to_id is
        the location reviewed; variant_name is the service level now held, spelled as supplied;
        last_review_date is the review date stamped, in YYYY-MM-DD format.
    """
    review_date = ctx.now()[:10]
    ctx.update("ship_to_accounts", ship_to_id, variant_name=variant_name, last_review_date=review_date)
    return str({"status": "recorded", "ship_to_id": ship_to_id, "variant_name": variant_name,
                "last_review_date": review_date})


@tool(owner="user", rw="write")
def submit_stock_rotation_return_550cd403(ctx: ToolContext, ship_to_id: str, order_number: str, line_number: int,
                                          sku: str, quantity: int, unit_price: float) -> str:
    """Submit, on the customer's own account, a stock-rotation return for one shipped order line of a
    Ship-To Fulfillment Account. The call issues one return material authorization (RMA) line for the
    item, marked as a no-longer-needed return of an unopened stocked standard item that the customer
    ships back, for the quantity and unit price supplied; no credit, fee or receipt is booked by this
    call. Once stored, the return lookup for the ship-to shows the new authorized RMA line.

    Args:
        ship_to_id: Id class — the internal identifier of the ship-to the goods were shipped to, as
            returned by the ship-to account lookup for the customer.
        order_number: Verbatim class — the sales order number of the shipped line being returned,
            format SO-NNNNNNN, copied character for character from the order or return lookup (verbatim).
        line_number: Fixed-format class — the line number of the shipped line on that sales order,
            an integer >= 1, as shown on the order lookup.
        sku: Verbatim class — the Corbett item number of the item being returned, copied character for
            character from the order or return lookup (verbatim).
        quantity: Fixed-format class — the number of units authorized for return, an integer in
            integer selling units, never negative.
        unit_price: Fixed-format class — the invoiced unit price of the shipped line, in USD with
            4 decimal places, rounded half up at the fourth decimal.

    Returns:
        A dictionary receipt: status is the word authorized when the RMA line was stored; rma_number
        is the RMA number issued, format RMA-NNNNNN; ship_to_id, order_number, line_number and sku echo
        the line returned; quantity is the integer quantity authorized; unit_price is the unit price
        recorded, in USD to 4 decimal places; event_date is the RMA date, in YYYY-MM-DD format.
    """
    rid = ctx.make_id("ret_", ship_to_id, order_number, line_number, sku, quantity, unit_price)
    rma_number = "RMA-3" + str(int(rid[-10:], 16) % 100000).zfill(5)
    ship_to = (ctx.find("ship_to_accounts", ship_to_id=ship_to_id) or [{}])[0]
    event_date = ctx.now()[:10]
    price = round(float(unit_price), 4)
    ctx.create("order_returns", rid, return_line_id=rid, ship_to_id=ship_to_id,
               customer_id=ship_to.get("customer_id", ""), event_type="order_return_authorized",
               rma_number=rma_number, order_number=order_number, line_number=int(line_number), sku=sku,
               item_class="standard", stock_status="stocked", quantity=int(quantity), unit_price=price,
               return_reason="no_longer_needed", return_method="customer_shipped", decline_reason="none",
               item_condition="none", close_reason="none", restocking_fee=0.0, label_fee=0.0,
               credit_amount=0.0, event_date=event_date)
    return str({"status": "authorized", "rma_number": rma_number, "ship_to_id": ship_to_id,
                "order_number": order_number, "line_number": int(line_number), "sku": sku,
                "quantity": int(quantity), "unit_price": price, "event_date": event_date})


@tool(owner="agent", rw="write")
def reactivate_ship_to_971b9440(ctx: ToolContext, ship_to_id: str, variant_name: str) -> str:
    """Reactivate one suspended Ship-To Fulfillment Account at the customer's request. The call sets
    the delivery location's status to active, so it takes orders again, and sets the service level it
    holds on reactivation to the level supplied; its order history, returns, dates and programs are
    left unchanged. Once stored, the ship-to lookup shows the location as active at that level.

    Args:
        ship_to_id: Id class — the internal identifier of the suspended ship-to (delivery location) to
            reactivate, as returned by the ship-to account lookup for the customer.
        variant_name: Enum class — the service level the location holds on reactivation, spelled
            exactly as one of: Corbett Parcel Ship-To when it is to hold the parcel level; Corbett
            Standard Ship-To when it is to hold the standard level; Corbett Priority Ship-To when it is
            to hold the priority level; Corbett Route Delivery Ship-To when it is to hold the route
            delivery level; Corbett Premier Route Ship-To when it is to hold the premier route level;
            Corbett Dedicated Delivery Ship-To when it is to hold the dedicated delivery level.

    Returns:
        A dictionary receipt: status is the word reactivated when the change was stored; ship_to_id is
        the location reactivated; ship_to_status is its lifecycle status now, the word active;
        variant_name is the service level it now holds, spelled as supplied.
    """
    ctx.update("ship_to_accounts", ship_to_id, status="active", variant_name=variant_name)
    return str({"status": "reactivated", "ship_to_id": ship_to_id, "ship_to_status": "active",
                "variant_name": variant_name})


@tool(owner="user", rw="write")
def elect_service_level_move_6cd24a6d(ctx: ToolContext, ship_to_id: str, variant_name: str) -> str:
    """Record, on the customer's own election, the service level one Ship-To Fulfillment Account moves
    to on a requested move up. The call sets the level the delivery location holds to the level
    supplied and stamps today's date as its most recent service level change; its status, orders,
    returns and programs are left unchanged. Once stored, the ship-to lookup shows the level and date.

    Args:
        ship_to_id: Id class — the internal identifier of the ship-to (delivery location) whose level
            the customer elects, as returned by the ship-to account lookup for the customer.
        variant_name: Enum class — the service level the location holds once the election is stored,
            spelled exactly as one of: Corbett Parcel Ship-To when it is to hold the parcel level;
            Corbett Standard Ship-To when it is to hold the standard level; Corbett Priority Ship-To when
            it is to hold the priority level; Corbett Route Delivery Ship-To when it is to hold the
            route delivery level; Corbett Premier Route Ship-To when it is to hold the premier route
            level; Corbett Dedicated Delivery Ship-To when it is to hold the dedicated delivery level.

    Returns:
        A dictionary receipt: status is the word elected when the level was stored; ship_to_id is the
        location changed; variant_name is the service level now held, spelled as supplied;
        last_review_date is the change date stamped, in YYYY-MM-DD format.
    """
    change_date = ctx.now()[:10]
    ctx.update("ship_to_accounts", ship_to_id, variant_name=variant_name, last_review_date=change_date)
    return str({"status": "elected", "ship_to_id": ship_to_id, "variant_name": variant_name,
                "last_review_date": change_date})

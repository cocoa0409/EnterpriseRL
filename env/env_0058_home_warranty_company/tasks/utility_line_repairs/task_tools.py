"""Hidden task tools for the utility_line_repairs difficulty (Bridgewell Utility Line Protection Plans).

Each tool performs one atomic write on a line protection plan's claim record and is reached only through
the unlock/call meta-tools after its name is found in the published knowledge base. The tools record what
the caller passes; they judge no eligibility and compute no amount.
"""

from erlbench import ToolContext, tool


@tool(owner="agent", rw="write")
def authorize_slab_access_payment_bcc8b3fe(ctx: ToolContext, customer_id: str, lineplan_contract_id: str,
                                           lineplan_service_request_id: str, line_type: str,
                                           payment_amount: float) -> str:
    """Book Bridgewell's slab access payment on one line service request: a new allowance authorization of
    type slab access is added to the request's claim history under a newly issued authorization number,
    carrying the line named, the method not_applicable, today's date, and the amount given as both the
    cost of the item and the amount Bridgewell pays. The amount counts toward the occurrence's benefit
    from that moment, and the authorization appears in the plan's claim history. Success is the receipt
    below naming the new authorization number.

    Args:
        customer_id: Id class — the customer reference number of the plan holder, as returned by the
            customer profile lookup.
        lineplan_contract_id: Id class — the line protection plan number the service request belongs to,
            as returned by the plan lookup.
        lineplan_service_request_id: Id class — the line service request number the payment is booked on,
            as returned by the service request lookup.
        line_type: Enum class — the line named on that service request, copied from the request record:
            water_service_line — the exterior water service line from the utility connection to the home;
            sewer_lateral — the exterior sewer lateral from the home to the public sewer connection;
            septic_line — the exterior line from the home to the septic tank;
            electrical_service_line — the exterior electrical service line and meter base;
            interior_supply_line — water supply piping inside the home or beneath its slab;
            interior_drain_line — drain and waste piping inside the home or beneath its slab;
            gas_service_line — the exterior gas service line;
            well_line — the line from a private well to the home.
        payment_amount: Fixed-format class — the slab access payment Bridgewell authorizes, in USD, a
            non-negative number rounded to 2 decimal places; the same figure is recorded as the item's
            cost and as the amount paid.

    Returns:
        A confirmation sentence (string) stating the new authorization number (an identifier beginning
        with 5), the service request it was booked on, the allowance type slab_access and the amount in USD
        with 2 decimal places; receiving it means the authorization is on file.
    """
    amount = round(float(payment_amount), 2)
    auth_no = ctx.make_id("5", customer_id, lineplan_contract_id, lineplan_service_request_id, line_type,
                          amount, "slab_access")
    rid = ctx.make_id("lce_", customer_id, lineplan_contract_id, lineplan_service_request_id, line_type,
                      amount, "slab_access")
    ctx.create("lineplan_claim_events", rid, lineplan_claim_event_id=rid, lineplan_contract_id=lineplan_contract_id,
               customer_id=customer_id, event_type="lineplan_repair_authorization",
               lineplan_service_request_id=lineplan_service_request_id, event_date=ctx.now()[:10],
               line_type=line_type, authorization_number=auth_no, resolution_type="allowance",
               allowance_type="slab_access", repair_method="not_applicable", invoice_amount=amount, amount=amount)
    return (f"Slab access payment authorized: authorization {auth_no} on service request "
            f"{lineplan_service_request_id}, allowance slab_access, amount {amount:.2f} USD.")


@tool(owner="user", rw="write")
def approve_interior_line_work_4d5cfcfa(ctx: ToolContext, customer_id: str, lineplan_contract_id: str,
                                        lineplan_service_request_id: str, line_type: str, resolution_type: str,
                                        repair_method: str, contractor_quote: float,
                                        bridgewell_payment: float) -> str:
    """The customer approves permanent work on an interior supply or drain line whose contractor quote is
    above what Bridgewell pays: a new repair authorization is added to the service request's claim history
    under a newly issued authorization number, recording the line, the kind of work, the method, the
    contractor's quoted cost and the amount Bridgewell pays, dated today. By approving, the customer accepts
    paying the contractor directly any part of the quote above Bridgewell's payment. The authorization then
    appears in the plan's claim history; success is the receipt below naming the new authorization number.

    Args:
        customer_id: Id class — the customer reference number of the plan holder, as read out to the
            customer by the representative from the customer profile lookup.
        lineplan_contract_id: Id class — the line protection plan number the service request belongs to,
            as read out by the representative from the plan lookup.
        lineplan_service_request_id: Id class — the line service request number the work is approved on,
            as read out by the representative from the service request lookup.
        line_type: Enum class — the line named on that service request, copied from the request record:
            water_service_line — the exterior water service line from the utility connection to the home;
            sewer_lateral — the exterior sewer lateral from the home to the public sewer connection;
            septic_line — the exterior line from the home to the septic tank;
            electrical_service_line — the exterior electrical service line and meter base;
            interior_supply_line — water supply piping inside the home or beneath its slab;
            interior_drain_line — drain and waste piping inside the home or beneath its slab;
            gas_service_line — the exterior gas service line;
            well_line — the line from a private well to the home.
        resolution_type: Enum class — the kind of work being approved:
            section_repair — the failed section alone is repaired;
            full_line_replacement — the whole line run is replaced or rerouted;
            temporary_repair — a stop-gap repair that only restores service;
            allowance — a restoration or access allowance rather than repair work.
        repair_method: Enum class — how the work reaches the line:
            open_trench — the line is dug up along the run being worked on;
            trenchless — the line is bored, burst or lined without digging along its run;
            not_applicable — the work involves no excavation of a buried run, such as work inside the home.
        contractor_quote: Fixed-format class — the contractor's quoted cost for the approved work, in USD,
            rounded to 2 decimal places, exactly as the contractor quoted it.
        bridgewell_payment: Fixed-format class — the amount Bridgewell pays toward the approved work, in USD,
            a non-negative number rounded to 2 decimal places.

    Returns:
        A confirmation sentence (string) stating the new authorization number (an identifier beginning
        with 5), the service request, the kind of work, the contractor's quoted cost and Bridgewell's payment
        in USD with 2 decimal places, and the share the customer pays the contractor; receiving it means the
        approval is on file.
    """
    quote = round(float(contractor_quote), 2)
    pay = round(float(bridgewell_payment), 2)
    auth_no = ctx.make_id("5", customer_id, lineplan_contract_id, lineplan_service_request_id, line_type,
                          resolution_type, repair_method, quote, pay)
    rid = ctx.make_id("lce_", customer_id, lineplan_contract_id, lineplan_service_request_id, line_type,
                      resolution_type, repair_method, quote, pay)
    ctx.create("lineplan_claim_events", rid, lineplan_claim_event_id=rid, lineplan_contract_id=lineplan_contract_id,
               customer_id=customer_id, event_type="lineplan_repair_authorization",
               lineplan_service_request_id=lineplan_service_request_id, event_date=ctx.now()[:10],
               line_type=line_type, authorization_number=auth_no, resolution_type=resolution_type,
               repair_method=repair_method, invoice_amount=quote, amount=pay)
    return (f"Work approved: authorization {auth_no} on service request {lineplan_service_request_id} "
            f"({resolution_type}, {repair_method}); contractor quote {quote:.2f} USD, Bridgewell pays "
            f"{pay:.2f} USD, customer pays the contractor {max(0.0, quote - pay):.2f} USD.")


@tool(owner="agent", rw="write")
def authorize_public_way_restoration_c5bbe6ee(ctx: ToolContext, customer_id: str, lineplan_contract_id: str,
                                              lineplan_service_request_id: str, line_type: str,
                                              payment_amount: float) -> str:
    """Book Bridgewell's public-way restoration payment on one line service request: a new allowance
    authorization of type public way restoration (cutting and restoring a public sidewalk, curb or street)
    is added to the request's claim history under a newly issued authorization number, carrying the line
    named, the method not_applicable, today's date, and the amount given as both the cost of the item and
    the amount Bridgewell pays. The amount counts toward the occurrence's benefit from that moment, and the
    authorization appears in the plan's claim history. Success is the receipt below naming the new
    authorization number.

    Args:
        customer_id: Id class — the customer reference number of the plan holder, as returned by the
            customer profile lookup.
        lineplan_contract_id: Id class — the line protection plan number the service request belongs to,
            as returned by the plan lookup.
        lineplan_service_request_id: Id class — the line service request number the payment is booked on,
            as returned by the service request lookup.
        line_type: Enum class — the line named on that service request, copied from the request record:
            water_service_line — the exterior water service line from the utility connection to the home;
            sewer_lateral — the exterior sewer lateral from the home to the public sewer connection;
            septic_line — the exterior line from the home to the septic tank;
            electrical_service_line — the exterior electrical service line and meter base;
            interior_supply_line — water supply piping inside the home or beneath its slab;
            interior_drain_line — drain and waste piping inside the home or beneath its slab;
            gas_service_line — the exterior gas service line;
            well_line — the line from a private well to the home.
        payment_amount: Fixed-format class — the public-way restoration payment Bridgewell authorizes, in
            USD, a non-negative number rounded to 2 decimal places; the same figure is recorded as the item's
            cost and as the amount paid.

    Returns:
        A confirmation sentence (string) stating the new authorization number (an identifier beginning
        with 5), the service request it was booked on, the allowance type public_way_restoration and the
        amount in USD with 2 decimal places; receiving it means the authorization is on file.
    """
    amount = round(float(payment_amount), 2)
    auth_no = ctx.make_id("5", customer_id, lineplan_contract_id, lineplan_service_request_id, line_type,
                          amount, "public_way_restoration")
    rid = ctx.make_id("lce_", customer_id, lineplan_contract_id, lineplan_service_request_id, line_type,
                      amount, "public_way_restoration")
    ctx.create("lineplan_claim_events", rid, lineplan_claim_event_id=rid, lineplan_contract_id=lineplan_contract_id,
               customer_id=customer_id, event_type="lineplan_repair_authorization",
               lineplan_service_request_id=lineplan_service_request_id, event_date=ctx.now()[:10],
               line_type=line_type, authorization_number=auth_no, resolution_type="allowance",
               allowance_type="public_way_restoration", repair_method="not_applicable", invoice_amount=amount,
               amount=amount)
    return (f"Public-way restoration payment authorized: authorization {auth_no} on service request "
            f"{lineplan_service_request_id}, allowance public_way_restoration, amount {amount:.2f} USD.")


@tool(owner="agent", rw="write")
def authorize_lawn_restoration_4590e15f(ctx: ToolContext, customer_id: str, lineplan_contract_id: str,
                                        lineplan_service_request_id: str, line_type: str,
                                        payment_amount: float) -> str:
    """Book Bridgewell's lawn restoration payment on one line service request: a new allowance authorization
    of type landscaping restoration (backfill, seed and straw over the excavated yard) is added to the
    request's claim history under a newly issued authorization number, carrying the line named, the method
    not_applicable, today's date, and the amount given as both the cost of the item and the amount
    Bridgewell pays. The amount counts toward the occurrence's benefit from that moment, and the
    authorization appears in the plan's claim history. Success is the receipt below naming the new
    authorization number.

    Args:
        customer_id: Id class — the customer reference number of the plan holder, as returned by the
            customer profile lookup.
        lineplan_contract_id: Id class — the line protection plan number the service request belongs to,
            as returned by the plan lookup.
        lineplan_service_request_id: Id class — the line service request number the payment is booked on,
            as returned by the service request lookup.
        line_type: Enum class — the line named on that service request, copied from the request record:
            water_service_line — the exterior water service line from the utility connection to the home;
            sewer_lateral — the exterior sewer lateral from the home to the public sewer connection;
            septic_line — the exterior line from the home to the septic tank;
            electrical_service_line — the exterior electrical service line and meter base;
            interior_supply_line — water supply piping inside the home or beneath its slab;
            interior_drain_line — drain and waste piping inside the home or beneath its slab;
            gas_service_line — the exterior gas service line;
            well_line — the line from a private well to the home.
        payment_amount: Fixed-format class — the lawn restoration payment Bridgewell authorizes, in USD, a
            non-negative number rounded to 2 decimal places; the same figure is recorded as the item's cost
            and as the amount paid.

    Returns:
        A confirmation sentence (string) stating the new authorization number (an identifier beginning
        with 5), the service request it was booked on, the allowance type landscaping_restoration and the
        amount in USD with 2 decimal places; receiving it means the authorization is on file.
    """
    amount = round(float(payment_amount), 2)
    auth_no = ctx.make_id("5", customer_id, lineplan_contract_id, lineplan_service_request_id, line_type,
                          amount, "landscaping_restoration")
    rid = ctx.make_id("lce_", customer_id, lineplan_contract_id, lineplan_service_request_id, line_type,
                      amount, "landscaping_restoration")
    ctx.create("lineplan_claim_events", rid, lineplan_claim_event_id=rid, lineplan_contract_id=lineplan_contract_id,
               customer_id=customer_id, event_type="lineplan_repair_authorization",
               lineplan_service_request_id=lineplan_service_request_id, event_date=ctx.now()[:10],
               line_type=line_type, authorization_number=auth_no, resolution_type="allowance",
               allowance_type="landscaping_restoration", repair_method="not_applicable", invoice_amount=amount,
               amount=amount)
    return (f"Lawn restoration payment authorized: authorization {auth_no} on service request "
            f"{lineplan_service_request_id}, allowance landscaping_restoration, amount {amount:.2f} USD.")


@tool(owner="user", rw="write")
def approve_exterior_line_work_7ea09e9b(ctx: ToolContext, customer_id: str, lineplan_contract_id: str,
                                        lineplan_service_request_id: str, line_type: str, resolution_type: str,
                                        repair_method: str, contractor_quote: float,
                                        bridgewell_payment: float) -> str:
    """The customer approves permanent work on an exterior service line whose contractor quote is above what
    Bridgewell pays: a new repair authorization is added to the service request's claim history under a
    newly issued authorization number, recording the line, the kind of work, the method, the contractor's
    quoted cost and the amount Bridgewell pays, dated today. By approving, the customer accepts paying the
    contractor directly any part of the quote above Bridgewell's payment. The authorization then appears in
    the plan's claim history; success is the receipt below naming the new authorization number.

    Args:
        customer_id: Id class — the customer reference number of the plan holder, as read out to the
            customer by the representative from the customer profile lookup.
        lineplan_contract_id: Id class — the line protection plan number the service request belongs to,
            as read out by the representative from the plan lookup.
        lineplan_service_request_id: Id class — the line service request number the work is approved on,
            as read out by the representative from the service request lookup.
        line_type: Enum class — the line named on that service request, copied from the request record:
            water_service_line — the exterior water service line from the utility connection to the home;
            sewer_lateral — the exterior sewer lateral from the home to the public sewer connection;
            septic_line — the exterior line from the home to the septic tank;
            electrical_service_line — the exterior electrical service line and meter base;
            interior_supply_line — water supply piping inside the home or beneath its slab;
            interior_drain_line — drain and waste piping inside the home or beneath its slab;
            gas_service_line — the exterior gas service line;
            well_line — the line from a private well to the home.
        resolution_type: Enum class — the kind of work being approved:
            section_repair — the failed section alone is repaired;
            full_line_replacement — the whole line from the connection point to the home is replaced;
            temporary_repair — a stop-gap repair that only restores service;
            allowance — a restoration or access allowance rather than repair work.
        repair_method: Enum class — how the work reaches the line:
            open_trench — the line is dug up along the run being worked on;
            trenchless — the line is bored, burst or lined without digging along its run;
            not_applicable — the work involves no excavation of a buried run.
        contractor_quote: Fixed-format class — the contractor's quoted cost for the approved work, in USD,
            rounded to 2 decimal places, exactly as the contractor quoted it.
        bridgewell_payment: Fixed-format class — the amount Bridgewell pays toward the approved work, in USD,
            a non-negative number rounded to 2 decimal places.

    Returns:
        A confirmation sentence (string) stating the new authorization number (an identifier beginning
        with 5), the service request, the kind of work, the contractor's quoted cost and Bridgewell's payment
        in USD with 2 decimal places, and the share the customer pays the contractor; receiving it means the
        approval is on file.
    """
    quote = round(float(contractor_quote), 2)
    pay = round(float(bridgewell_payment), 2)
    auth_no = ctx.make_id("5", customer_id, lineplan_contract_id, lineplan_service_request_id, line_type,
                          resolution_type, repair_method, quote, pay)
    rid = ctx.make_id("lce_", customer_id, lineplan_contract_id, lineplan_service_request_id, line_type,
                      resolution_type, repair_method, quote, pay)
    ctx.create("lineplan_claim_events", rid, lineplan_claim_event_id=rid, lineplan_contract_id=lineplan_contract_id,
               customer_id=customer_id, event_type="lineplan_repair_authorization",
               lineplan_service_request_id=lineplan_service_request_id, event_date=ctx.now()[:10],
               line_type=line_type, authorization_number=auth_no, resolution_type=resolution_type,
               repair_method=repair_method, invoice_amount=quote, amount=pay)
    return (f"Work approved: authorization {auth_no} on service request {lineplan_service_request_id} "
            f"({resolution_type}, {repair_method}); contractor quote {quote:.2f} USD, Bridgewell pays "
            f"{pay:.2f} USD, customer pays the contractor {max(0.0, quote - pay):.2f} USD.")

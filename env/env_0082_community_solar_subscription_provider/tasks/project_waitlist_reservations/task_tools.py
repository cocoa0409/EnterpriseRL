"""Hidden task tools of project_waitlist_reservations (env_0082, Meadowlark Community Solar).

Each tool performs one atomic write on a waitlist reservation or on its offer record; no tool checks
eligibility, queue order, prerequisites or any figure the agent passes in beyond the formats its own
docstring states.
"""

from erlbench import ToolContext, tool


class _Fmt:
    """Formatting helpers used by the tools (pure arithmetic and format checks, no business judgement)."""

    @staticmethod
    def half_up(value, places):
        scale = 10 ** places
        v = float(value)
        if v >= 0:
            return int(v * scale + 0.5 + 0.000000001) / scale
        return -int(-v * scale + 0.5 + 0.000000001) / scale

    @staticmethod
    def is_whole(value):
        v = float(value)
        return v == int(v)

    @staticmethod
    def is_ymd(text):
        s = str(text)
        if len(s) != 10 or s[4] != "-" or s[7] != "-":
            return False
        y, m, d = s[:4], s[5:7], s[8:]
        if not (y.isdigit() and m.isdigit() and d.isdigit()):
            return False
        return 1 <= int(m) <= 12 and 1 <= int(d) <= 31


@tool(owner="agent", rw="write")
def extend_relocation_offer_f94b15ad(ctx: ToolContext, wait_res_id: str, project_id: str, offered_kw: float, offered_plan: str,
        estimated_annual_kwh: int, estimated_annual_savings: float, respond_by_date: str) -> str:
    """Extend an offer of project capacity to a Relocation Priority waitlist reservation and issue the written offer.
    One call moves the reservation to offered status and records one written offer dated today that states the
    project, the share size offered, the plan offered, the first-year kWh and savings estimates and the last day the
    customer may accept. The call's effect is visible at once: the reservation's status reads offered and the new
    offer is on the customer's offer records with today's offer date. The figures are recorded as passed in, after
    the rounding stated below; a call whose figures break a stated format is refused and writes nothing.

    Args:
        wait_res_id: Id class — the reservation number of the Relocation Priority reservation being offered capacity, as returned
            by the waitlist reservation lookup for this customer.
        project_id: Id class — the project number of the community solar project whose capacity is offered, as
            returned by the project lookup or shown on the reservation.
        offered_kw: Fixed-format class — share size offered, kW AC, 2 decimal places, greater than 0.00; the value is
            rounded half up to 2 decimal places when recorded, and a value that is not greater than 0.00 once rounded
            is refused.
        offered_plan: Enum class — the plan the offer is made on, written exactly as the official plan name:
            one of Meadowlark Flex 5 — the offer is made on that plan; Meadowlark Standard 10 — the offer is
            made on that plan; Meadowlark Commit 3 — the offer is made on that plan; Meadowlark Commit 5 — the
            offer is made on that plan; Meadowlark Commit 10 — the offer is made on that plan; Meadowlark Commit
            20 — the offer is made on that plan; Meadowlark Business Starter — the offer is made on that plan;
            Meadowlark Business Standard — the offer is made on that plan; Meadowlark Business Plus — the offer
            is made on that plan; Meadowlark Business Pro — the offer is made on that plan; Meadowlark Business
            Premier — the offer is made on that plan; Meadowlark Business Multi-Site — the offer is made on that
            plan; Meadowlark Access 15 — the offer is made on that plan; Meadowlark Access 20 — the offer is
            made on that plan; Meadowlark Access 25 — the offer is made on that plan; Meadowlark Access Housing
            20 — the offer is made on that plan; Meadowlark Access Neighborhood 15 — the offer is made on that
            plan; Meadowlark Access Solar for All 50 — the offer is made on that plan; Garden Fixed 10 — the
            offer is made on that plan; Garden Fixed 15 — the offer is made on that plan; Garden Fixed 20 — the
            offer is made on that plan; Garden Fixed 25 — the offer is made on that plan; Garden Business Fixed
            15 — the offer is made on that plan; Garden Business Fixed 25 — the offer is made on that plan;
            Meadowlark Farm Flex — the offer is made on that plan; Meadowlark Farm 5 — the offer is made on that
            plan; Meadowlark Farm 10 — the offer is made on that plan; Meadowlark Farm 20 — the offer is made on
            that plan; Meadowlark Farm Irrigation 10 — the offer is made on that plan; Meadowlark Farm Co-op 20
            — the offer is made on that plan; Meadowlark Civic Flex — the offer is made on that plan; Meadowlark
            Civic 5 — the offer is made on that plan; Meadowlark Civic 10 — the offer is made on that plan;
            Meadowlark Civic 20 — the offer is made on that plan; Meadowlark Faith Community 10 — the offer is
            made on that plan; Meadowlark Public Agency 20 — the offer is made on that plan;
        estimated_annual_kwh: Fixed-format class — estimated first-year credited kWh of the offered share, kWh, whole
            number, passed as an integer; a value that is not a whole number of 0 or more is refused.
        estimated_annual_savings: Fixed-format class — estimated first-year savings of the offered share, USD, 2
            decimal places, 0.00 or more; the value is rounded half up to 2 decimal places when recorded, and a value
            below 0.00 is refused.
        respond_by_date: Fixed-format class — last calendar day on which the customer may accept the offer, written
            YYYY-MM-DD; a value in any other form is refused.

    Returns:
        A dictionary receipt rendered as text. On success its fields are: wait_offer_id (text, the new offer's
        reference number), wait_res_id (text, the reservation offered), status (text, always offered), offer_date
        (YYYY-MM-DD, today's date), offered_kw (number, 2 decimals), offered_plan (text), estimated_annual_kwh
        (integer), estimated_annual_savings (number, 2 decimals) and respond_by_date (YYYY-MM-DD); a receipt carrying a
        wait_offer_id means the offer was issued and the reservation is offered. A refused call returns a receipt
        with the single field error (text naming the argument whose format was broken) and changes nothing.
    """
    kw = _Fmt.half_up(offered_kw, 2)
    if not kw > 0:
        return str({"error": "offered_kw must be greater than 0.00"})
    if not _Fmt.is_whole(estimated_annual_kwh) or float(estimated_annual_kwh) < 0:
        return str({"error": "estimated_annual_kwh must be a whole number of 0 or more"})
    savings = _Fmt.half_up(estimated_annual_savings, 2)
    if savings < 0:
        return str({"error": "estimated_annual_savings must be 0.00 or more"})
    if not _Fmt.is_ymd(respond_by_date):
        return str({"error": "respond_by_date must be written YYYY-MM-DD"})
    kwh = int(float(estimated_annual_kwh))
    res = ctx.find("waitlist_reservations", wait_res_id=wait_res_id)
    customer_id = res[0].get("customer_id") if res else ""
    today = ctx.now()[:10]
    ctx.update("waitlist_reservations", wait_res_id, status="offered")
    oid = ctx.make_id("woff_", wait_res_id, project_id, offered_kw, offered_plan, estimated_annual_kwh,
                      estimated_annual_savings, respond_by_date)
    ctx.create("waitlist_offers", oid, wait_offer_id=oid, wait_res_id=wait_res_id, customer_id=customer_id,
               event_type="waitlist_offer_made", project_id=project_id, offer_date=today, offered_kw=kw,
               offered_plan=offered_plan, estimated_annual_kwh=kwh, estimated_annual_savings=savings,
               respond_by_date=respond_by_date)
    return str({"wait_offer_id": oid, "wait_res_id": wait_res_id, "status": "offered", "offer_date": today,
                "offered_kw": kw, "offered_plan": offered_plan, "estimated_annual_kwh": kwh,
                "estimated_annual_savings": savings, "respond_by_date": respond_by_date})


@tool(owner="user", rw="write")
def set_relocation_request_cdb5c762(ctx: ToolContext, wait_res_id: str, requested_kw: float) -> str:
    """Submit the customer's own change to the share size requested on their Relocation Priority waitlist reservation.
    One call replaces the reservation's requested kW with the size given; the reservation keeps its class,
    project, utility account, status and queue date, and the new requested kW shows on the reservation record at
    once. The size is recorded as passed in, after the rounding stated below; a size that breaks the stated format
    is refused and writes nothing.

    Args:
        wait_res_id: Id class — the reservation number of the customer's Relocation Priority reservation, as the representative
            reads it from the reservation record and gives it to the customer.
        requested_kw: Fixed-format class — the share size the customer now requests, kW AC, 2 decimal places,
            greater than 0.00; the value is rounded half up to 2 decimal places when recorded, and a value that is
            not greater than 0.00 once rounded is refused.

    Returns:
        A dictionary receipt rendered as text. On success its fields are: wait_res_id (text, the reservation
        changed), requested_kw (number, 2 decimals, the size now on the reservation) and changed_on (YYYY-MM-DD,
        today's date); a receipt carrying the new requested_kw means the change is in place. A refused call returns
        a receipt with the single field error (text) and changes nothing.
    """
    kw = _Fmt.half_up(requested_kw, 2)
    if not kw > 0:
        return str({"error": "requested_kw must be greater than 0.00"})
    ctx.update("waitlist_reservations", wait_res_id, requested_kw=kw)
    return str({"wait_res_id": wait_res_id, "requested_kw": kw, "changed_on": ctx.now()[:10]})


@tool(owner="user", rw="write")
def fit_standard_request_b636e3b6(ctx: ToolContext, wait_res_id: str, requested_kw: float) -> str:
    """Submit the customer's own change to the share size requested on their Residential Standard waitlist reservation.
    One call replaces the reservation's requested kW with the size given; the reservation keeps its class,
    project, utility account, status and queue date, and the new requested kW shows on the reservation record at
    once. The size is recorded as passed in, after the rounding stated below; a size that breaks the stated format
    is refused and writes nothing.

    Args:
        wait_res_id: Id class — the reservation number of the customer's Residential Standard reservation, as the representative
            reads it from the reservation record and gives it to the customer.
        requested_kw: Fixed-format class — the share size the customer now requests, kW AC, 2 decimal places,
            greater than 0.00; the value is rounded half up to 2 decimal places when recorded, and a value that is
            not greater than 0.00 once rounded is refused.

    Returns:
        A dictionary receipt rendered as text. On success its fields are: wait_res_id (text, the reservation
        changed), requested_kw (number, 2 decimals, the size now on the reservation) and changed_on (YYYY-MM-DD,
        today's date); a receipt carrying the new requested_kw means the change is in place. A refused call returns
        a receipt with the single field error (text) and changes nothing.
    """
    kw = _Fmt.half_up(requested_kw, 2)
    if not kw > 0:
        return str({"error": "requested_kw must be greater than 0.00"})
    ctx.update("waitlist_reservations", wait_res_id, requested_kw=kw)
    return str({"wait_res_id": wait_res_id, "requested_kw": kw, "changed_on": ctx.now()[:10]})


@tool(owner="agent", rw="write")
def extend_standard_offer_cf280a13(ctx: ToolContext, wait_res_id: str, project_id: str, offered_kw: float, offered_plan: str,
        estimated_annual_kwh: int, estimated_annual_savings: float, respond_by_date: str) -> str:
    """Extend an offer of project capacity to a Residential Standard waitlist reservation and issue the written offer.
    One call moves the reservation to offered status and records one written offer dated today that states the
    project, the share size offered, the plan offered, the first-year kWh and savings estimates and the last day the
    customer may accept. The call's effect is visible at once: the reservation's status reads offered and the new
    offer is on the customer's offer records with today's offer date. The figures are recorded as passed in, after
    the rounding stated below; a call whose figures break a stated format is refused and writes nothing.

    Args:
        wait_res_id: Id class — the reservation number of the Residential Standard reservation being offered capacity, as returned
            by the waitlist reservation lookup for this customer.
        project_id: Id class — the project number of the community solar project whose capacity is offered, as
            returned by the project lookup or shown on the reservation.
        offered_kw: Fixed-format class — share size offered, kW AC, 2 decimal places, greater than 0.00; the value is
            rounded half up to 2 decimal places when recorded, and a value that is not greater than 0.00 once rounded
            is refused.
        offered_plan: Enum class — the plan the offer is made on, written exactly as the official plan name:
            one of Meadowlark Flex 5 — the offer is made on that plan; Meadowlark Standard 10 — the offer is
            made on that plan; Meadowlark Commit 3 — the offer is made on that plan; Meadowlark Commit 5 — the
            offer is made on that plan; Meadowlark Commit 10 — the offer is made on that plan; Meadowlark Commit
            20 — the offer is made on that plan; Meadowlark Business Starter — the offer is made on that plan;
            Meadowlark Business Standard — the offer is made on that plan; Meadowlark Business Plus — the offer
            is made on that plan; Meadowlark Business Pro — the offer is made on that plan; Meadowlark Business
            Premier — the offer is made on that plan; Meadowlark Business Multi-Site — the offer is made on that
            plan; Meadowlark Access 15 — the offer is made on that plan; Meadowlark Access 20 — the offer is
            made on that plan; Meadowlark Access 25 — the offer is made on that plan; Meadowlark Access Housing
            20 — the offer is made on that plan; Meadowlark Access Neighborhood 15 — the offer is made on that
            plan; Meadowlark Access Solar for All 50 — the offer is made on that plan; Garden Fixed 10 — the
            offer is made on that plan; Garden Fixed 15 — the offer is made on that plan; Garden Fixed 20 — the
            offer is made on that plan; Garden Fixed 25 — the offer is made on that plan; Garden Business Fixed
            15 — the offer is made on that plan; Garden Business Fixed 25 — the offer is made on that plan;
            Meadowlark Farm Flex — the offer is made on that plan; Meadowlark Farm 5 — the offer is made on that
            plan; Meadowlark Farm 10 — the offer is made on that plan; Meadowlark Farm 20 — the offer is made on
            that plan; Meadowlark Farm Irrigation 10 — the offer is made on that plan; Meadowlark Farm Co-op 20
            — the offer is made on that plan; Meadowlark Civic Flex — the offer is made on that plan; Meadowlark
            Civic 5 — the offer is made on that plan; Meadowlark Civic 10 — the offer is made on that plan;
            Meadowlark Civic 20 — the offer is made on that plan; Meadowlark Faith Community 10 — the offer is
            made on that plan; Meadowlark Public Agency 20 — the offer is made on that plan;
        estimated_annual_kwh: Fixed-format class — estimated first-year credited kWh of the offered share, kWh, whole
            number, passed as an integer; a value that is not a whole number of 0 or more is refused.
        estimated_annual_savings: Fixed-format class — estimated first-year savings of the offered share, USD, 2
            decimal places, 0.00 or more; the value is rounded half up to 2 decimal places when recorded, and a value
            below 0.00 is refused.
        respond_by_date: Fixed-format class — last calendar day on which the customer may accept the offer, written
            YYYY-MM-DD; a value in any other form is refused.

    Returns:
        A dictionary receipt rendered as text. On success its fields are: wait_offer_id (text, the new offer's
        reference number), wait_res_id (text, the reservation offered), status (text, always offered), offer_date
        (YYYY-MM-DD, today's date), offered_kw (number, 2 decimals), offered_plan (text), estimated_annual_kwh
        (integer), estimated_annual_savings (number, 2 decimals) and respond_by_date (YYYY-MM-DD); a receipt carrying a
        wait_offer_id means the offer was issued and the reservation is offered. A refused call returns a receipt
        with the single field error (text naming the argument whose format was broken) and changes nothing.
    """
    kw = _Fmt.half_up(offered_kw, 2)
    if not kw > 0:
        return str({"error": "offered_kw must be greater than 0.00"})
    if not _Fmt.is_whole(estimated_annual_kwh) or float(estimated_annual_kwh) < 0:
        return str({"error": "estimated_annual_kwh must be a whole number of 0 or more"})
    savings = _Fmt.half_up(estimated_annual_savings, 2)
    if savings < 0:
        return str({"error": "estimated_annual_savings must be 0.00 or more"})
    if not _Fmt.is_ymd(respond_by_date):
        return str({"error": "respond_by_date must be written YYYY-MM-DD"})
    kwh = int(float(estimated_annual_kwh))
    res = ctx.find("waitlist_reservations", wait_res_id=wait_res_id)
    customer_id = res[0].get("customer_id") if res else ""
    today = ctx.now()[:10]
    ctx.update("waitlist_reservations", wait_res_id, status="offered")
    oid = ctx.make_id("wofs_", wait_res_id, project_id, offered_kw, offered_plan, estimated_annual_kwh,
                      estimated_annual_savings, respond_by_date)
    ctx.create("waitlist_offers", oid, wait_offer_id=oid, wait_res_id=wait_res_id, customer_id=customer_id,
               event_type="waitlist_offer_made", project_id=project_id, offer_date=today, offered_kw=kw,
               offered_plan=offered_plan, estimated_annual_kwh=kwh, estimated_annual_savings=savings,
               respond_by_date=respond_by_date)
    return str({"wait_offer_id": oid, "wait_res_id": wait_res_id, "status": "offered", "offer_date": today,
                "offered_kw": kw, "offered_plan": offered_plan, "estimated_annual_kwh": kwh,
                "estimated_annual_savings": savings, "respond_by_date": respond_by_date})


@tool(owner="user", rw="write")
def fit_addon_request_598035d1(ctx: ToolContext, wait_res_id: str, requested_kw: float) -> str:
    """Submit the customer's own change to the share size requested on their Residential Add-On waitlist reservation.
    One call replaces the reservation's requested kW with the size given; the reservation keeps its class,
    project, utility account, status and queue date, and the new requested kW shows on the reservation record at
    once. The size is recorded as passed in, after the rounding stated below; a size that breaks the stated format
    is refused and writes nothing.

    Args:
        wait_res_id: Id class — the reservation number of the customer's Residential Add-On reservation, as the representative
            reads it from the reservation record and gives it to the customer.
        requested_kw: Fixed-format class — the share size the customer now requests, kW AC, 2 decimal places,
            greater than 0.00; the value is rounded half up to 2 decimal places when recorded, and a value that is
            not greater than 0.00 once rounded is refused.

    Returns:
        A dictionary receipt rendered as text. On success its fields are: wait_res_id (text, the reservation
        changed), requested_kw (number, 2 decimals, the size now on the reservation) and changed_on (YYYY-MM-DD,
        today's date); a receipt carrying the new requested_kw means the change is in place. A refused call returns
        a receipt with the single field error (text) and changes nothing.
    """
    kw = _Fmt.half_up(requested_kw, 2)
    if not kw > 0:
        return str({"error": "requested_kw must be greater than 0.00"})
    ctx.update("waitlist_reservations", wait_res_id, requested_kw=kw)
    return str({"wait_res_id": wait_res_id, "requested_kw": kw, "changed_on": ctx.now()[:10]})


@tool(owner="agent", rw="write")
def extend_addon_offer_d026003c(ctx: ToolContext, wait_res_id: str, project_id: str, offered_kw: float, offered_plan: str,
        estimated_annual_kwh: int, estimated_annual_savings: float, respond_by_date: str) -> str:
    """Extend an offer of project capacity to a Residential Add-On waitlist reservation and issue the written offer.
    One call moves the reservation to offered status and records one written offer dated today that states the
    project, the share size offered, the plan offered, the first-year kWh and savings estimates and the last day the
    customer may accept. The call's effect is visible at once: the reservation's status reads offered and the new
    offer is on the customer's offer records with today's offer date. The figures are recorded as passed in, after
    the rounding stated below; a call whose figures break a stated format is refused and writes nothing.

    Args:
        wait_res_id: Id class — the reservation number of the Residential Add-On reservation being offered capacity, as returned
            by the waitlist reservation lookup for this customer.
        project_id: Id class — the project number of the community solar project whose capacity is offered, as
            returned by the project lookup or shown on the reservation.
        offered_kw: Fixed-format class — share size offered, kW AC, 2 decimal places, greater than 0.00; the value is
            rounded half up to 2 decimal places when recorded, and a value that is not greater than 0.00 once rounded
            is refused.
        offered_plan: Enum class — the plan the offer is made on, written exactly as the official plan name:
            one of Meadowlark Flex 5 — the offer is made on that plan; Meadowlark Standard 10 — the offer is
            made on that plan; Meadowlark Commit 3 — the offer is made on that plan; Meadowlark Commit 5 — the
            offer is made on that plan; Meadowlark Commit 10 — the offer is made on that plan; Meadowlark Commit
            20 — the offer is made on that plan; Meadowlark Business Starter — the offer is made on that plan;
            Meadowlark Business Standard — the offer is made on that plan; Meadowlark Business Plus — the offer
            is made on that plan; Meadowlark Business Pro — the offer is made on that plan; Meadowlark Business
            Premier — the offer is made on that plan; Meadowlark Business Multi-Site — the offer is made on that
            plan; Meadowlark Access 15 — the offer is made on that plan; Meadowlark Access 20 — the offer is
            made on that plan; Meadowlark Access 25 — the offer is made on that plan; Meadowlark Access Housing
            20 — the offer is made on that plan; Meadowlark Access Neighborhood 15 — the offer is made on that
            plan; Meadowlark Access Solar for All 50 — the offer is made on that plan; Garden Fixed 10 — the
            offer is made on that plan; Garden Fixed 15 — the offer is made on that plan; Garden Fixed 20 — the
            offer is made on that plan; Garden Fixed 25 — the offer is made on that plan; Garden Business Fixed
            15 — the offer is made on that plan; Garden Business Fixed 25 — the offer is made on that plan;
            Meadowlark Farm Flex — the offer is made on that plan; Meadowlark Farm 5 — the offer is made on that
            plan; Meadowlark Farm 10 — the offer is made on that plan; Meadowlark Farm 20 — the offer is made on
            that plan; Meadowlark Farm Irrigation 10 — the offer is made on that plan; Meadowlark Farm Co-op 20
            — the offer is made on that plan; Meadowlark Civic Flex — the offer is made on that plan; Meadowlark
            Civic 5 — the offer is made on that plan; Meadowlark Civic 10 — the offer is made on that plan;
            Meadowlark Civic 20 — the offer is made on that plan; Meadowlark Faith Community 10 — the offer is
            made on that plan; Meadowlark Public Agency 20 — the offer is made on that plan;
        estimated_annual_kwh: Fixed-format class — estimated first-year credited kWh of the offered share, kWh, whole
            number, passed as an integer; a value that is not a whole number of 0 or more is refused.
        estimated_annual_savings: Fixed-format class — estimated first-year savings of the offered share, USD, 2
            decimal places, 0.00 or more; the value is rounded half up to 2 decimal places when recorded, and a value
            below 0.00 is refused.
        respond_by_date: Fixed-format class — last calendar day on which the customer may accept the offer, written
            YYYY-MM-DD; a value in any other form is refused.

    Returns:
        A dictionary receipt rendered as text. On success its fields are: wait_offer_id (text, the new offer's
        reference number), wait_res_id (text, the reservation offered), status (text, always offered), offer_date
        (YYYY-MM-DD, today's date), offered_kw (number, 2 decimals), offered_plan (text), estimated_annual_kwh
        (integer), estimated_annual_savings (number, 2 decimals) and respond_by_date (YYYY-MM-DD); a receipt carrying a
        wait_offer_id means the offer was issued and the reservation is offered. A refused call returns a receipt
        with the single field error (text naming the argument whose format was broken) and changes nothing.
    """
    kw = _Fmt.half_up(offered_kw, 2)
    if not kw > 0:
        return str({"error": "offered_kw must be greater than 0.00"})
    if not _Fmt.is_whole(estimated_annual_kwh) or float(estimated_annual_kwh) < 0:
        return str({"error": "estimated_annual_kwh must be a whole number of 0 or more"})
    savings = _Fmt.half_up(estimated_annual_savings, 2)
    if savings < 0:
        return str({"error": "estimated_annual_savings must be 0.00 or more"})
    if not _Fmt.is_ymd(respond_by_date):
        return str({"error": "respond_by_date must be written YYYY-MM-DD"})
    kwh = int(float(estimated_annual_kwh))
    res = ctx.find("waitlist_reservations", wait_res_id=wait_res_id)
    customer_id = res[0].get("customer_id") if res else ""
    today = ctx.now()[:10]
    ctx.update("waitlist_reservations", wait_res_id, status="offered")
    oid = ctx.make_id("wofa_", wait_res_id, project_id, offered_kw, offered_plan, estimated_annual_kwh,
                      estimated_annual_savings, respond_by_date)
    ctx.create("waitlist_offers", oid, wait_offer_id=oid, wait_res_id=wait_res_id, customer_id=customer_id,
               event_type="waitlist_offer_made", project_id=project_id, offer_date=today, offered_kw=kw,
               offered_plan=offered_plan, estimated_annual_kwh=kwh, estimated_annual_savings=savings,
               respond_by_date=respond_by_date)
    return str({"wait_offer_id": oid, "wait_res_id": wait_res_id, "status": "offered", "offer_date": today,
                "offered_kw": kw, "offered_plan": offered_plan, "estimated_annual_kwh": kwh,
                "estimated_annual_savings": savings, "respond_by_date": respond_by_date})

"""Hidden task tools of the pharmacy_coverage_and_exceptions difficulty (category rx).

Each tool performs one atomic write on the member's pharmacy benefit and takes the value the agent
has worked out from the published policy; no tool judges eligibility, timing or any prerequisite.
"""

from erlbench import ToolContext, tool


# --------------------------------------------------------------------------- over-the-counter allowance
@tool(owner="agent", rw="write")
def forfeit_otc_quarter_0e0fa26e(ctx: ToolContext, rx_coverage_id: str, benefit_quarter: str,
                                 forfeit_amount: float) -> str:
    """Book the forfeiture of unused over-the-counter allowance for one closed benefit quarter on a
    member's pharmacy coverage. One call adds one forfeiture entry to the coverage's allowance
    activity, tagged with the quarter and dated today, and lowers the coverage's current allowance
    balance by the forfeited amount. Afterwards the member's allowance activity shows the forfeiture
    and the balance no longer includes that money; whatever part of the quarter's unused allowance
    was not forfeited stays on the balance.

    Args:
        rx_coverage_id: Id class — the reference number of the member's pharmacy coverage record, as
            returned by the pharmacy coverage lookup for the verified member.
        benefit_quarter: Fixed-format class — the closed calendar quarter the forfeiture belongs to,
            written YYYY-Qn (for example 2026-Q1), exactly as the allowance activity tags that
            quarter's load.
        forfeit_amount: Fixed-format class — the allowance forfeited, in USD, a positive amount with
            2 decimal places; a value with more places is rounded to 2 decimal places.

    Returns:
        A dictionary rendered as text with: rx_otc_id (string, the reference number of the new
        forfeiture entry), benefit_quarter (string, YYYY-Qn), forfeit_amount (number, USD with 2
        decimal places), otc_balance (number, the allowance balance in USD with 2 decimal places
        after the forfeiture) and status (the text "forfeited", which confirms the entry was booked).
    """
    amount = round(float(forfeit_amount), 2)
    rid = ctx.make_id("otc_", rx_coverage_id, "forfeit", benefit_quarter, amount)
    customer = ctx.find("rx_coverages", rx_coverage_id=rx_coverage_id)
    customer_id = customer[0].get("customer_id") if customer else ""
    ctx.create("rx_otc_ledger", rid, rx_otc_id=rid, rx_coverage_id=rx_coverage_id, customer_id=customer_id,
               event_type="rx_otc_forfeit", benefit_quarter=benefit_quarter, amount=amount,
               order_channel="not_applicable", order_number="", posted_date=ctx.now()[:10])
    new_balance = round(float((ctx.find("rx_coverages", rx_coverage_id=rx_coverage_id) or [{}])[0].get("otc_balance") or 0) - amount, 2)
    ctx.update("rx_coverages", rx_coverage_id, otc_balance=new_balance)
    return str({"rx_otc_id": rid, "benefit_quarter": benefit_quarter, "forfeit_amount": amount,
                "otc_balance": new_balance, "status": "forfeited"})


@tool(owner="agent", rw="write")
def load_otc_quarter_30ec28e6(ctx: ToolContext, rx_coverage_id: str, benefit_quarter: str,
                              load_amount: float) -> str:
    """Load the over-the-counter allowance of one benefit quarter onto a member's pharmacy coverage.
    One call adds one load entry to the coverage's allowance activity, tagged with the quarter and
    dated today, and raises the coverage's current allowance balance by the loaded amount.
    Afterwards the member can see the quarter's load in the allowance activity and spend the new
    balance on catalog items.

    Args:
        rx_coverage_id: Id class — the reference number of the member's pharmacy coverage record, as
            returned by the pharmacy coverage lookup for the verified member.
        benefit_quarter: Fixed-format class — the calendar quarter being loaded, written YYYY-Qn (for
            example 2026-Q3).
        load_amount: Fixed-format class — the allowance loaded for the quarter, in USD, a positive
            amount with 2 decimal places; a value with more places is rounded to 2 decimal
            places.

    Returns:
        A dictionary rendered as text with: rx_otc_id (string, the reference number of the new load
        entry), benefit_quarter (string, YYYY-Qn), load_amount (number, USD with 2 decimal places),
        otc_balance (number, the allowance balance in USD with 2 decimal places after the load) and
        status (the text "loaded", which confirms the load was booked).
    """
    amount = round(float(load_amount), 2)
    rid = ctx.make_id("otc_", rx_coverage_id, "load", benefit_quarter, amount)
    customer = ctx.find("rx_coverages", rx_coverage_id=rx_coverage_id)
    customer_id = customer[0].get("customer_id") if customer else ""
    ctx.create("rx_otc_ledger", rid, rx_otc_id=rid, rx_coverage_id=rx_coverage_id, customer_id=customer_id,
               event_type="rx_otc_load", benefit_quarter=benefit_quarter, amount=amount,
               order_channel="not_applicable", order_number="", posted_date=ctx.now()[:10])
    new_balance = round(float((ctx.find("rx_coverages", rx_coverage_id=rx_coverage_id) or [{}])[0].get("otc_balance") or 0) + amount, 2)
    ctx.update("rx_coverages", rx_coverage_id, otc_balance=new_balance)
    return str({"rx_otc_id": rid, "benefit_quarter": benefit_quarter, "load_amount": amount,
                "otc_balance": new_balance, "status": "loaded"})


@tool(owner="agent", rw="write")
def post_otc_receipt_a5c098d1(ctx: ToolContext, rx_coverage_id: str, rx_otc_id: str,
                              allowance_charged: float) -> str:
    """Post a retail pharmacy register receipt that the pharmacy transmitted against a member's
    over-the-counter allowance but that has not been posted yet. One call sets the receipt's charge
    to the allowance to the amount given, dates the posting today, and lowers the coverage's current
    allowance balance by that charge. Afterwards the receipt shows in the allowance activity as a
    posted retail purchase with its allowance charge, and the balance reflects it.

    Args:
        rx_coverage_id: Id class — the reference number of the member's pharmacy coverage record the
            receipt was transmitted against, as returned by the pharmacy coverage lookup.
        rx_otc_id: Id class — the reference number of the transmitted, not yet posted retail receipt
            entry, as returned by the allowance activity lookup for the coverage.
        allowance_charged: Fixed-format class — the part of the receipt charged to the allowance, in
            USD, a positive amount with 2 decimal places; a value with more places is rounded to 2 decimal places.

    Returns:
        A dictionary rendered as text with: rx_otc_id (string, the reference number of the posted
        receipt entry), allowance_charged (number, USD with 2 decimal places), posted_date (string,
        YYYY-MM-DD, the posting date), otc_balance (number, the allowance balance in USD with 2
        decimal places after posting) and status (the text "posted", which confirms the posting).
    """
    amount = round(float(allowance_charged), 2)
    posted = ctx.now()[:10]
    ctx.update("rx_otc_ledger", rx_otc_id, amount=amount, posted_date=posted)
    new_balance = round(float((ctx.find("rx_coverages", rx_coverage_id=rx_coverage_id) or [{}])[0].get("otc_balance") or 0) - amount, 2)
    ctx.update("rx_coverages", rx_coverage_id, otc_balance=new_balance)
    return str({"rx_otc_id": rx_otc_id, "allowance_charged": amount, "posted_date": posted,
                "otc_balance": new_balance, "status": "posted"})


@tool(owner="user", rw="write")
def place_otc_catalog_order_ca6274ae(ctx: ToolContext, rx_coverage_id: str, benefit_quarter: str,
                                     allowance_amount: float) -> str:
    """Place the member's own mail catalog order paid from her over-the-counter allowance. One call
    records one mail catalog purchase on the member's pharmacy coverage, tagged with the quarter and
    dated today, issues an order number, and lowers the coverage's current allowance balance by the
    allowance amount applied to the order; the catalog items beyond that amount are the member's own
    cost. Afterwards the member has an order number and sees the order in her allowance activity.

    Args:
        rx_coverage_id: Id class — the reference number of the member's pharmacy coverage record, as
            the member services representative reads it from the pharmacy coverage lookup.
        benefit_quarter: Fixed-format class — the calendar quarter the order is charged to, written
            YYYY-Qn (for example 2026-Q3).
        allowance_amount: Fixed-format class — the allowance applied to the order, in USD, a positive
            amount with 2 decimal places; a value with more places is rounded to 2 decimal
            places.

    Returns:
        A dictionary rendered as text with: order_number (string, the catalog order number issued),
        rx_otc_id (string, the reference number of the purchase entry), allowance_amount (number, USD
        with 2 decimal places), otc_balance (number, the allowance balance in USD with 2 decimal
        places after the order) and status (the text "ordered", which confirms the order was placed).
    """
    amount = round(float(allowance_amount), 2)
    rid = ctx.make_id("otc_", rx_coverage_id, "catalog", benefit_quarter, amount)
    order_number = "OTC-" + rid[-8:].upper()
    customer = ctx.find("rx_coverages", rx_coverage_id=rx_coverage_id)
    customer_id = customer[0].get("customer_id") if customer else ""
    ctx.create("rx_otc_ledger", rid, rx_otc_id=rid, rx_coverage_id=rx_coverage_id, customer_id=customer_id,
               event_type="rx_otc_purchase", benefit_quarter=benefit_quarter, amount=amount,
               order_channel="mail_catalog", order_number=order_number, posted_date=ctx.now()[:10])
    new_balance = round(float((ctx.find("rx_coverages", rx_coverage_id=rx_coverage_id) or [{}])[0].get("otc_balance") or 0) - amount, 2)
    ctx.update("rx_coverages", rx_coverage_id, otc_balance=new_balance)
    return str({"order_number": order_number, "rx_otc_id": rid, "allowance_amount": amount,
                "otc_balance": new_balance, "status": "ordered"})


# --------------------------------------------------------------------------- dispensing days
@tool(owner="agent", rw="write")
def record_emergency_supply_c348acc4(ctx: ToolContext, rx_coverage_id: str, rejected_fill_id: str,
                                     exception_number: str, days_supply: int) -> str:
    """Authorize an emergency supply of a drug that was turned away at the pharmacy counter while its
    prior authorization or formulary exception request is still undecided. One call adds one emergency
    supply dispensing to the member's pharmacy claims, dated today, for the same prescription, drug,
    NDC, pharmacy and prescriber as the counter rejection, carrying no copay and naming the pending
    request it bridges. Afterwards the pharmacy can hand the member that many days of the drug and the
    member's pharmacy claims show the emergency supply.

    Args:
        rx_coverage_id: Id class — the reference number of the member's pharmacy coverage record, as
            returned by the pharmacy coverage lookup for the verified member.
        rejected_fill_id: Id class — the reference number of the counter rejection the supply answers,
            as returned by the pharmacy claims lookup for the coverage.
        exception_number: Verbatim class — the request number of the pending prior authorization or
            exception request the supply bridges, copied character for character from the request
            shown by the pharmacy requests lookup (verbatim).
        days_supply: Fixed-format class — the days of the drug dispensed, a positive integer number of
            integer days.

    Returns:
        A dictionary rendered as text with: rx_fill_id (string, the reference number of the emergency
        supply claim), rx_number (string, the prescription number), drug_name (string), days_supply
        (integer days), fill_date (string, YYYY-MM-DD) and status (the text "dispensed", which confirms
        the emergency supply was recorded).
    """
    days = int(days_supply)
    rej = ctx.find("rx_fills", rx_fill_id=rejected_fill_id)
    src = rej[0] if rej else {}
    rid = ctx.make_id("rxf_", rx_coverage_id, rejected_fill_id, exception_number, days)
    today = ctx.now()[:10]
    ctx.create("rx_fills", rid, rx_fill_id=rid, rx_coverage_id=rx_coverage_id, customer_id=src.get("customer_id", ""),
               event_type="rx_emergency_supply", rx_number=src.get("rx_number", ""), fill_date=today,
               ndc=src.get("ndc", ""), drug_name=src.get("drug_name", ""),
               controlled_schedule=src.get("controlled_schedule", "none"),
               formulary_status=src.get("formulary_status", "not_applicable"), days_supply=days,
               quantity=float(src.get("quantity") or 0), pharmacy_npi=src.get("pharmacy_npi", ""),
               prescriber_npi=src.get("prescriber_npi", ""), fill_type="emergency_supply", member_copay=0.0,
               plan_paid_amount=0.0, copay_exempt_class="none", exception_number=exception_number,
               reject_code="none", reversal_date="")
    return str({"rx_fill_id": rid, "rx_number": src.get("rx_number", ""), "drug_name": src.get("drug_name", ""),
                "days_supply": days, "fill_date": today, "status": "dispensed"})


@tool(owner="agent", rw="write")
def book_transition_fill_6c1f1c97(ctx: ToolContext, rx_coverage_id: str, rejected_fill_id: str,
                                  days_supply: int) -> str:
    """Pay the one transition fill of a non-formulary drug a newly enrolled member was already taking
    and that was turned away at the pharmacy counter. One call adds one paid transition fill to the
    member's pharmacy claims, dated today, for the same prescription, drug, NDC, pharmacy and prescriber
    as the counter rejection, with no copay. Afterwards the pharmacy can dispense that many days of the
    drug and the member's pharmacy claims show the transition fill.

    Args:
        rx_coverage_id: Id class — the reference number of the member's pharmacy coverage record, as
            returned by the pharmacy coverage lookup for the verified member.
        rejected_fill_id: Id class — the reference number of the counter rejection the transition fill
            answers, as returned by the pharmacy claims lookup for the coverage.
        days_supply: Fixed-format class — the days of the drug the transition fill covers, a positive
            integer number of integer days.

    Returns:
        A dictionary rendered as text with: rx_fill_id (string, the reference number of the transition
        fill claim), rx_number (string, the prescription number), drug_name (string), days_supply
        (integer days), fill_date (string, YYYY-MM-DD) and status (the text "paid", which confirms the
        transition fill was recorded).
    """
    days = int(days_supply)
    rej = ctx.find("rx_fills", rx_fill_id=rejected_fill_id)
    src = rej[0] if rej else {}
    rid = ctx.make_id("rxf_", rx_coverage_id, rejected_fill_id, "transition", days)
    today = ctx.now()[:10]
    ctx.create("rx_fills", rid, rx_fill_id=rid, rx_coverage_id=rx_coverage_id, customer_id=src.get("customer_id", ""),
               event_type="rx_fill", rx_number=src.get("rx_number", ""), fill_date=today, ndc=src.get("ndc", ""),
               drug_name=src.get("drug_name", ""), controlled_schedule=src.get("controlled_schedule", "none"),
               formulary_status=src.get("formulary_status", "non_preferred"), days_supply=days,
               quantity=float(src.get("quantity") or 0), pharmacy_npi=src.get("pharmacy_npi", ""),
               prescriber_npi=src.get("prescriber_npi", ""), fill_type="transition_fill", member_copay=0.0,
               plan_paid_amount=0.0, copay_exempt_class="none", exception_number="", reject_code="none",
               reversal_date="")
    return str({"rx_fill_id": rid, "rx_number": src.get("rx_number", ""), "drug_name": src.get("drug_name", ""),
                "days_supply": days, "fill_date": today, "status": "paid"})


@tool(owner="agent", rw="write")
def release_vacation_supply_4890f9e9(ctx: ToolContext, rx_coverage_id: str, rx_exception_id: str,
                                     days_supply: int, member_copay: float) -> str:
    """Release the early vacation supply that a granted vacation override allows. One call adds one paid
    fill of the overridden prescription to the member's pharmacy claims, dated today, marked as a
    vacation override fill, with the days supply and copay given. Afterwards the pharmacy can dispense
    the released days ahead of the ordinary refill date and the member's pharmacy claims show the
    vacation fill.

    Args:
        rx_coverage_id: Id class — the reference number of the member's pharmacy coverage record, as
            returned by the pharmacy coverage lookup for the verified member.
        rx_exception_id: Id class — the reference number of the granted vacation override entry, as
            returned by the pharmacy requests lookup for the coverage.
        days_supply: Fixed-format class — the days of the drug released, a positive integer number of
            integer days.
        member_copay: Fixed-format class — the copay assessed on the vacation fill, in USD, signed, with
            2 decimal places (0.00 where the plan sets no copay).

    Returns:
        A dictionary rendered as text with: rx_fill_id (string, the reference number of the vacation
        fill claim), rx_number (string, the prescription number), drug_name (string), days_supply
        (integer days), member_copay (number, USD with 2 decimal places) and status (the text
        "released", which confirms the vacation supply was recorded).
    """
    days = int(days_supply)
    copay = round(float(member_copay), 2)
    ovr = ctx.find("rx_exceptions", rx_exception_id=rx_exception_id)
    src = ovr[0] if ovr else {}
    rid = ctx.make_id("rxf_", rx_coverage_id, rx_exception_id, "vacation", days, copay)
    ctx.create("rx_fills", rid, rx_fill_id=rid, rx_coverage_id=rx_coverage_id, customer_id=src.get("customer_id", ""),
               event_type="rx_fill", rx_number=src.get("rx_number", ""), fill_date=ctx.now()[:10],
               drug_name=src.get("drug_name", ""), days_supply=days, fill_type="vacation_override",
               member_copay=copay, copay_exempt_class="none", exception_number="", reject_code="none",
               reversal_date="")
    return str({"rx_fill_id": rid, "rx_number": src.get("rx_number", ""), "drug_name": src.get("drug_name", ""),
                "days_supply": days, "member_copay": copay, "status": "released"})


@tool(owner="user", rw="write")
def request_replacement_fill_14de4074(ctx: ToolContext, rx_coverage_id: str, rx_number: str,
                                      police_report_number: str, days_supply: int, member_copay: float) -> str:
    """File the member's own lost or stolen supply request for one prescription and receive the
    replacement fill. One call records a lost or stolen early refill override for the prescription,
    dated today and carrying the police report number the member gives, and adds one paid replacement
    fill of that prescription to the member's pharmacy claims with the days supply and copay given.
    Afterwards the pharmacy can dispense the replacement and the member's pharmacy requests and claims
    show the override and the replacement fill.

    Args:
        rx_coverage_id: Id class — the reference number of the member's pharmacy coverage record, as the
            member services representative reads it from the pharmacy coverage lookup.
        rx_number: Verbatim class — the prescription number printed on the label, copied character for
            character as the member reads it (verbatim).
        police_report_number: Verbatim class — the police report number the member gives for the loss
            or theft, copied character for character as the member states it (verbatim).
        days_supply: Fixed-format class — the days of the drug in the replacement fill, a positive
            integer number of integer days.
        member_copay: Fixed-format class — the copay assessed on the replacement fill, in USD, signed,
            with 2 decimal places (0.00 where the plan sets no copay).

    Returns:
        A dictionary rendered as text with: rx_exception_id (string, the reference number of the lost or
        stolen override), rx_fill_id (string, the reference number of the replacement fill claim),
        rx_number (string), days_supply (integer days), member_copay (number, USD with 2 decimal places)
        and status (the text "replaced", which confirms the override and the replacement were recorded).
    """
    days = int(days_supply)
    copay = round(float(member_copay), 2)
    prior = ctx.find("rx_fills", rx_coverage_id=rx_coverage_id, rx_number=rx_number, event_type="rx_fill")
    src = prior[0] if prior else {}
    today = ctx.now()[:10]
    oid = ctx.make_id("rxe_", rx_coverage_id, rx_number, "lost_stolen", police_report_number)
    ctx.create("rx_exceptions", oid, rx_exception_id=oid, rx_coverage_id=rx_coverage_id,
               customer_id=src.get("customer_id", ""), event_type="rx_refill_override", exception_number="",
               request_type="lost_stolen_override", lock_in_change_reason="not_applicable",
               drug_name=src.get("drug_name", ""), ndc=src.get("ndc", ""), rx_number=rx_number,
               requested_by="member", event_date=today, approved_through="", denial_reason="not_applicable",
               police_report_number=police_report_number)
    fid = ctx.make_id("rxf_", rx_coverage_id, rx_number, "replacement", days, copay)
    ctx.create("rx_fills", fid, rx_fill_id=fid, rx_coverage_id=rx_coverage_id, customer_id=src.get("customer_id", ""),
               event_type="rx_fill", rx_number=rx_number, fill_date=today, ndc=src.get("ndc", ""),
               drug_name=src.get("drug_name", ""), controlled_schedule=src.get("controlled_schedule", "none"),
               formulary_status=src.get("formulary_status", "not_applicable"), days_supply=days,
               pharmacy_npi=src.get("pharmacy_npi", ""), prescriber_npi=src.get("prescriber_npi", ""),
               fill_type="lost_stolen_override", member_copay=copay, copay_exempt_class="none",
               exception_number="", reject_code="none", reversal_date="")
    return str({"rx_exception_id": oid, "rx_fill_id": fid, "rx_number": rx_number, "days_supply": days,
                "member_copay": copay, "status": "replaced"})

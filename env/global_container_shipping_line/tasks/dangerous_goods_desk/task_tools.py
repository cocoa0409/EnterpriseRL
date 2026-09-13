"""Hidden task tools of the dangerous_goods_desk difficulty (category dg).

Each tool performs one atomic write on a dangerous-goods acceptance record, its account or its
declaration file. The tools never judge eligibility and never compute a charge: every amount and
decision is decided by the agent from the published rules and the records, and passed in as a
fixed-format, enum, id or verbatim argument. One particular is resolved by a tool itself: the
amendment-fee action attaches its charge to the acceptance's most recently signed amendment that no
amendment-fee charge references yet, a deterministic look-up of the declaration file that the
policy prescribes and that involves no amount, eligibility or prerequisite. A repeated identical
call of a charging or payment action writes nothing further and leaves the balance unchanged.
"""
from erlbench import ToolContext, tool


@tool(owner="user", rw="write")
def sign_amended_dg_declaration_eb5287cf(ctx: ToolContext, dg_id: str, customer_id: str, booking_id: str,
                                         vessel_voyage: str, gross_weight_kg: float) -> str:
    """The shipper signs an amended dangerous-goods declaration that changes the declared gross weight of one acceptance.

    Only the shipper can sign its own declaration, so this action is carried out by the customer
    in person. One call files a new amendment declaration for the acceptance, marked as signed by
    the shipper and carrying the UN number, class and packing group already declared, and replaces
    the gross weight declared on the acceptance with the signed figure. Afterwards the acceptance
    shows the new gross weight and its declaration file lists the signed amendment with its own
    declaration reference. The call has succeeded when the receipt shows outcome signed together
    with the new declaration reference.

    Args:
        dg_id: Id class — reference number of the dangerous-goods acceptance being amended, as shown by the dangerous-goods acceptance lookup for the customer's booking.
        customer_id: Id class — customer reference number of the shipper signing the amendment, as returned by the customer profile lookup.
        booking_id: Id class — reference number of the booking the goods travel under, as shown on the acceptance record and by the booking lookup.
        vessel_voyage: Id class — identifier of the sailing the booking is currently allocated to (vessel name and voyage number), copied exactly as shown by the booking lookup.
        gross_weight_kg: Fixed-format class — the new total gross weight of the dangerous goods the shipper signs for, in decimal kilograms, given to 1 decimal place (unit: kilograms); it replaces the previously declared weight.

    Returns:
        A dictionary rendered as text with: submission_id (text reference of the new signed amendment declaration), dg_id (text reference of the acceptance amended), gross_weight_kg (number, the declared gross weight now on the acceptance, 1 decimal place), outcome (text, always signed when the amendment was filed).
    """
    acc = (ctx.find("dg_acceptances", dg_id=dg_id) or [{}])[0]
    sid = ctx.make_id("dgs_", dg_id, customer_id, booking_id, vessel_voyage, gross_weight_kg)
    weight = round(float(gross_weight_kg), 1)
    ctx.create("dg_declaration_submissions", sid, submission_id=sid, customer_id=customer_id, dg_id=dg_id,
               submission_type="amendment", un_number=acc.get("un_number", ""),
               imdg_class=acc.get("imdg_class", ""), packing_group=acc.get("packing_group", ""),
               outcome="signed", created_at=ctx.now())
    ctx.update("dg_acceptances", dg_id, gross_weight_kg=weight)
    return str({"submission_id": sid, "dg_id": dg_id, "gross_weight_kg": weight, "outcome": "signed"})


@tool(owner="agent", rw="write")
def book_dg_late_declaration_fee_00f931c0(ctx: ToolContext, dg_id: str, booking_id: str, submission_id: str,
                                          amount_usd: float) -> str:
    """Book the late declaration fee for a shipper's declaration that was signed after the lead time but accepted for the sailing.

    One call writes one late-declaration charge on the acceptance's dangerous-goods account, tied to
    the declaration it charges, and adds the amount to the charges the acceptance owes. Afterwards
    the account shows the late declaration fee dated today and the higher outstanding balance. The
    call has succeeded when the receipt returns the new charge reference and the booked amount. A
    repeated identical call writes nothing further and leaves the balance unchanged.

    Args:
        dg_id: Id class — reference number of the dangerous-goods acceptance whose declaration was late, as shown by the dangerous-goods acceptance lookup.
        booking_id: Id class — reference number of the booking the goods travel under, as shown on the acceptance record.
        submission_id: Id class — reference number of the late signed declaration being charged, as listed by the declaration lookup for the acceptance.
        amount_usd: Fixed-format class — the late declaration fee to book, in USD, 2 decimal places (unit: US dollars, rounded half up to the cent before the call).

    Returns:
        A dictionary rendered as text with: dg_event_id (text reference of the new charge), dg_id (text reference of the acceptance), charge_code (text, late_declaration_fee), amount_usd (number, the fee booked, 2 decimal places), charges_due_usd (number, the acceptance's outstanding dangerous-goods charges after the fee, 2 decimal places).
    """
    acc = (ctx.find("dg_acceptances", dg_id=dg_id) or [{}])[0]
    amt = round(float(amount_usd), 2)
    rid = ctx.make_id("dgl_", dg_id, booking_id, submission_id, "late_declaration_fee", amount_usd)
    repeat = bool(ctx.find("dg_ledger", dg_event_id=rid))
    ctx.create("dg_ledger", rid, dg_event_id=rid, dg_id=dg_id, customer_id=acc.get("customer_id", ""),
               event_type="dg_late_declaration_fee_charged", event_date=ctx.now()[:10],
               charge_code="late_declaration_fee", amount_usd=amt, container_count=acc.get("container_count", 0),
               submission_id=submission_id, payment_reference="", reference_event_id="")
    due = round(float(acc.get("charges_due_usd") or 0) + (0 if repeat else amt), 2)
    ctx.update("dg_acceptances", dg_id, charges_due_usd=due)
    return str({"dg_event_id": rid, "dg_id": dg_id, "charge_code": "late_declaration_fee", "amount_usd": amt,
                "charges_due_usd": due})


@tool(owner="agent", rw="write")
def book_dg_amendment_fee_40feddd0(ctx: ToolContext, dg_id: str, booking_id: str, amount_usd: float) -> str:
    """Book the amendment fee on a dangerous-goods acceptance for its latest signed amendment declaration that has no amendment-fee charge yet.

    One call writes one amendment-fee charge on the acceptance's dangerous-goods account and adds
    the amount to the charges the acceptance owes. The charge is attached by this action to the
    most recently signed amendment declaration of the acceptance that no amendment-fee charge
    references yet (between two signed at the same moment, the one with the higher declaration
    reference), whose declaration reference it records on the charge and returns in the receipt;
    declarations awaiting signature, returned for correction or withdrawn are never attached. A
    call whose charge already exists (same acceptance, booking, attached declaration and amount)
    writes nothing further and leaves the balance unchanged. Afterwards the account shows the
    amendment fee dated today and the higher outstanding balance. The call has succeeded when the
    receipt returns the new charge reference, the declaration it is attached to and the booked
    amount.

    Args:
        dg_id: Id class — reference number of the dangerous-goods acceptance whose declaration was amended, as shown by the dangerous-goods acceptance lookup.
        booking_id: Id class — reference number of the booking the goods travel under, as shown on the acceptance record.
        amount_usd: Fixed-format class — the amendment fee to book, in USD, 2 decimal places (unit: US dollars, rounded half up to the cent before the call).

    Returns:
        A dictionary rendered as text with: dg_event_id (text reference of the new charge), dg_id (text reference of the acceptance), submission_id (text reference of the signed amendment declaration the charge is attached to; empty when every signed amendment already has a charge), charge_code (text, amendment_fee), amount_usd (number, the fee booked, 2 decimal places), charges_due_usd (number, the acceptance's outstanding dangerous-goods charges after the fee, 2 decimal places).
    """
    acc = (ctx.find("dg_acceptances", dg_id=dg_id) or [{}])[0]
    charged = {row.get("submission_id") for row in ctx.find("dg_ledger", dg_id=dg_id, charge_code="amendment_fee")}
    signed = [row for row in ctx.find("dg_declaration_submissions", dg_id=dg_id, submission_type="amendment",
                                      outcome="signed") if row.get("submission_id") not in charged]
    latest = max(signed, key=lambda row: (str(row.get("created_at") or ""), str(row.get("submission_id") or ""))) if signed else {}
    sub_id = latest.get("submission_id", "")
    amt = round(float(amount_usd), 2)
    rid = ctx.make_id("dgl_", dg_id, booking_id, sub_id, amount_usd)
    repeat = bool(ctx.find("dg_ledger", dg_event_id=rid))
    ctx.create("dg_ledger", rid, dg_event_id=rid, dg_id=dg_id, customer_id=acc.get("customer_id", ""),
               event_type="dg_amendment_fee_charged", event_date=ctx.now()[:10], charge_code="amendment_fee",
               amount_usd=amt, container_count=acc.get("container_count", 0), submission_id=sub_id,
               payment_reference="", reference_event_id="")
    due = round(float(acc.get("charges_due_usd") or 0) + (0 if repeat else amt), 2)
    ctx.update("dg_acceptances", dg_id, charges_due_usd=due)
    return str({"dg_event_id": rid, "dg_id": dg_id, "submission_id": sub_id, "charge_code": "amendment_fee",
                "amount_usd": amt, "charges_due_usd": due})


@tool(owner="agent", rw="write")
def record_dg_review_decision_9aa03de9(ctx: ToolContext, dg_id: str, decision: str, admin_fee_usd: float) -> str:
    """Record the line's decision on a dangerous-goods acceptance that is under review, and book the administration fee that goes with an approval.

    One call closes the review. An approval marks the acceptance approved with today's date as the
    approval date and, when the administration fee passed is not 0.00, writes one
    administration-fee charge dated today on the acceptance's dangerous-goods account, adding it
    to the charges the acceptance owes; an approval passed with 0.00 writes no charge. A rejection marks the
    acceptance rejected with today's date as the rejection date and writes no charge. The call has
    succeeded when the receipt shows the new status and, for an approval, the fee booked. A
    repeated identical approval writes no second charge.

    Args:
        dg_id: Id class — reference number of the dangerous-goods acceptance under review, as shown by the dangerous-goods acceptance lookup.
        decision: Enum class — the outcome of the review; accepts only one of: approved (the line accepts the goods for the booking's current sailing), rejected (the line refuses the goods and nothing is charged).
        admin_fee_usd: Fixed-format class — the administration fee booked with this decision, in USD, 2 decimal places (unit: US dollars); 0.00 means no administration-fee charge is written, and a rejection always writes none.

    Returns:
        A dictionary rendered as text with: dg_id (text reference of the acceptance), status (text, approved or rejected as recorded), decision_date (text, YYYY-MM-DD date of the decision), admin_fee_usd (number, the administration fee booked, 2 decimal places; 0.00 for a rejection), charges_due_usd (number, the acceptance's outstanding dangerous-goods charges after the decision, 2 decimal places).
    """
    acc = (ctx.find("dg_acceptances", dg_id=dg_id) or [{}])[0]
    today = ctx.now()[:10]
    fee = round(float(admin_fee_usd), 2)
    due = round(float(acc.get("charges_due_usd") or 0), 2)
    if decision == "approved":
        ctx.update("dg_acceptances", dg_id, status="approved", approved_date=today)
    if decision == "approved" and fee != 0:
        rid = ctx.make_id("dgl_", dg_id, decision, admin_fee_usd)
        repeat = bool(ctx.find("dg_ledger", dg_event_id=rid))
        ctx.create("dg_ledger", rid, dg_event_id=rid, dg_id=dg_id, customer_id=acc.get("customer_id", ""),
                   event_type="dg_surcharge_charged", event_date=today, charge_code="dg_admin_fee",
                   amount_usd=fee, container_count=acc.get("container_count", 0), submission_id="",
                   payment_reference="", reference_event_id="")
        due = round(due + (0 if repeat else fee), 2)
        ctx.update("dg_acceptances", dg_id, charges_due_usd=due)
    if decision == "approved":
        status = "approved"
    else:
        ctx.update("dg_acceptances", dg_id, status="rejected", rejected_date=today)
        status = "rejected"
    booked = fee if decision == "approved" else 0.0
    return str({"dg_id": dg_id, "status": status, "decision_date": today, "admin_fee_usd": booked,
                "charges_due_usd": due})


@tool(owner="agent", rw="write")
def book_dg_loading_surcharge_44d311b2(ctx: ToolContext, dg_id: str, charge_code: str, container_count: int,
                                       amount_usd: float) -> str:
    """Book the hazardous-cargo surcharge row that falls due when the goods of a dangerous-goods acceptance are loaded on board.

    One call writes one surcharge charge dated today on the acceptance's dangerous-goods account,
    stating the containers it is computed on, and adds the amount to the charges the acceptance
    owes. Afterwards the account shows the surcharge and the higher outstanding balance. The call
    has succeeded when the receipt returns the new charge reference and the booked amount. A
    repeated identical call writes nothing further and leaves the balance unchanged.

    Args:
        dg_id: Id class — reference number of the dangerous-goods acceptance whose goods were loaded, as shown by the dangerous-goods acceptance lookup.
        charge_code: Enum class — tariff code of the row this action books; accepts only one value: dg_surcharge (the per-acceptance hazardous-cargo surcharge written when the goods are loaded). The marine-pollutant row and every other dangerous-goods charge are never booked with this action.
        container_count: Fixed-format class — number of containers the surcharge is computed on, integer, containers (unit: containers).
        amount_usd: Fixed-format class — the surcharge amount to book, in USD, 2 decimal places (unit: US dollars, rounded half up to the cent before the call).

    Returns:
        A dictionary rendered as text with: dg_event_id (text reference of the new charge), dg_id (text reference of the acceptance), charge_code (text, always dg_surcharge), container_count (integer, containers charged), amount_usd (number, the amount booked, 2 decimal places), charges_due_usd (number, the acceptance's outstanding dangerous-goods charges after the charge, 2 decimal places).
    """
    acc = (ctx.find("dg_acceptances", dg_id=dg_id) or [{}])[0]
    amt = round(float(amount_usd), 2)
    rid = ctx.make_id("dgl_", dg_id, charge_code, container_count, amount_usd)
    repeat = bool(ctx.find("dg_ledger", dg_event_id=rid))
    ctx.create("dg_ledger", rid, dg_event_id=rid, dg_id=dg_id, customer_id=acc.get("customer_id", ""),
               event_type="dg_surcharge_charged", event_date=ctx.now()[:10], charge_code="dg_surcharge",
               amount_usd=amt, container_count=int(container_count), submission_id="",
               payment_reference="", reference_event_id="")
    due = round(float(acc.get("charges_due_usd") or 0) + (0 if repeat else amt), 2)
    ctx.update("dg_acceptances", dg_id, charges_due_usd=due)
    return str({"dg_event_id": rid, "dg_id": dg_id, "charge_code": "dg_surcharge",
                "container_count": int(container_count), "amount_usd": amt, "charges_due_usd": due})


@tool(owner="agent", rw="write")
def book_dg_marine_pollutant_surcharge_a7ecff71(ctx: ToolContext, dg_id: str, charge_code: str,
                                                container_count: int, amount_usd: float) -> str:
    """Book the marine-pollutant surcharge row that falls due when goods declared as marine pollutant are loaded on board.

    One call writes one marine-pollutant charge dated today on the acceptance's dangerous-goods
    account, stating the containers it is computed on, and adds the amount to the charges the
    acceptance owes. Afterwards the account shows the charge and the higher outstanding balance.
    The call has succeeded when the receipt returns the new charge reference and the booked amount. A
    repeated identical call writes nothing further and leaves the balance unchanged.

    Args:
        dg_id: Id class — reference number of the dangerous-goods acceptance whose marine-pollutant goods were loaded, as shown by the dangerous-goods acceptance lookup.
        charge_code: Enum class — tariff code of the row this action books; accepts only one value: marine_pollutant_surcharge (the second loading row for goods marked marine pollutant). The per-acceptance dg_surcharge row and every other dangerous-goods charge are never booked with this action.
        container_count: Fixed-format class — number of containers the charge is computed on, integer, containers (unit: containers).
        amount_usd: Fixed-format class — the marine-pollutant surcharge to book, in USD, 2 decimal places (unit: US dollars, rounded half up to the cent before the call).

    Returns:
        A dictionary rendered as text with: dg_event_id (text reference of the new charge), dg_id (text reference of the acceptance), charge_code (text, always marine_pollutant_surcharge), container_count (integer, containers charged), amount_usd (number, the amount booked, 2 decimal places), charges_due_usd (number, the acceptance's outstanding dangerous-goods charges after the charge, 2 decimal places).
    """
    acc = (ctx.find("dg_acceptances", dg_id=dg_id) or [{}])[0]
    amt = round(float(amount_usd), 2)
    rid = ctx.make_id("dgl_", dg_id, charge_code, container_count, amount_usd)
    repeat = bool(ctx.find("dg_ledger", dg_event_id=rid))
    ctx.create("dg_ledger", rid, dg_event_id=rid, dg_id=dg_id, customer_id=acc.get("customer_id", ""),
               event_type="dg_surcharge_charged", event_date=ctx.now()[:10], charge_code="marine_pollutant_surcharge",
               amount_usd=amt, container_count=int(container_count), submission_id="",
               payment_reference="", reference_event_id="")
    due = round(float(acc.get("charges_due_usd") or 0) + (0 if repeat else amt), 2)
    ctx.update("dg_acceptances", dg_id, charges_due_usd=due)
    return str({"dg_event_id": rid, "dg_id": dg_id, "charge_code": "marine_pollutant_surcharge",
                "container_count": int(container_count), "amount_usd": amt, "charges_due_usd": due})


@tool(owner="agent", rw="write")
def record_dg_payment_ee299820(ctx: ToolContext, dg_id: str, payment_reference: str, amount_usd: float) -> str:
    """Apply a customer's bank remittance to the dangerous-goods account of one acceptance.

    One call writes one payment dated today on the acceptance's dangerous-goods account with the
    remittance reference and the amount applied, and reduces the charges the acceptance owes by
    that amount. Afterwards the account shows the payment and the lower outstanding balance. The
    call has succeeded when the receipt returns the new payment reference and the amount applied. A
    repeated identical call writes nothing further and leaves the balance unchanged.

    Args:
        dg_id: Id class — reference number of the dangerous-goods acceptance the remittance is applied to, as shown by the dangerous-goods acceptance lookup.
        payment_reference: Verbatim class — the bank remittance reference exactly as the customer quotes it; copy it character for character, keeping every letter, digit, hyphen and space, with no translation, normalisation, summarising, addition or deletion (verbatim).
        amount_usd: Fixed-format class — the amount of the remittance applied to this acceptance, in USD, 2 decimal places (unit: US dollars, rounded half up to the cent before the call).

    Returns:
        A dictionary rendered as text with: dg_event_id (text reference of the new payment entry), dg_id (text reference of the acceptance), payment_reference (text, the remittance reference as recorded), amount_usd (number, the amount applied, 2 decimal places), charges_due_usd (number, the acceptance's outstanding dangerous-goods charges after the payment, 2 decimal places).
    """
    acc = (ctx.find("dg_acceptances", dg_id=dg_id) or [{}])[0]
    amt = round(float(amount_usd), 2)
    rid = ctx.make_id("dgp_", dg_id, payment_reference, amount_usd)
    repeat = bool(ctx.find("dg_ledger", dg_event_id=rid))
    ctx.create("dg_ledger", rid, dg_event_id=rid, dg_id=dg_id, customer_id=acc.get("customer_id", ""),
               event_type="dg_payment_received", event_date=ctx.now()[:10], charge_code="payment",
               amount_usd=amt, container_count=acc.get("container_count", 0), submission_id="",
               payment_reference=payment_reference, reference_event_id="")
    due = round(float(acc.get("charges_due_usd") or 0) - (0 if repeat else amt), 2)
    ctx.update("dg_acceptances", dg_id, charges_due_usd=due)
    return str({"dg_event_id": rid, "dg_id": dg_id, "payment_reference": payment_reference, "amount_usd": amt,
                "charges_due_usd": due})

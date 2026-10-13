"""Hidden task tools of the community_rules_and_site_care_charges difficulty
(Hearthstone Communities — Community Rules & Site Care).

Each tool lands one atomic posting on a site-care plan record's statement and keeps the
record's running statement balance in step with it. No tool judges eligibility, ownership,
timing or amounts: every value is decided by the agent from the published policy and the
records, and passed in as declared. Reached only through unlock_* -> call_*.
"""

from erlbench import ToolContext, tool


@tool(owner="agent", rw="write")
def post_vehicle_permit_fee_c6960799(ctx: ToolContext, rules_plan_id: str, billing_period: str,
                                     entry_date: str, permit_count: int, amount: float) -> str:
    """Post the monthly extra-vehicle permit fee for one billing month on a site-care plan record's
    rules and site-care statement, on the resident desk's behalf.

    One call adds one vehicle permit fee charge for the stated month to the statement of the named
    plan record, carrying the number of permits charged and the fee amount, and raises the record's
    statement balance by that amount. The resident sees the charge on their rules and site-care
    statement for that month. Success is the receipt below with status "posted".

    Args:
        rules_plan_id: Id class — the reference number of the site-care plan record whose statement
            is charged, as returned by the site-care plan record lookup for the resident.
        billing_period: Fixed-format class — the calendar month the permit fee covers, written
            YYYY-MM (four-digit year, hyphen, two-digit month), for example 2026-03.
        entry_date: Fixed-format class — the charge date shown on the statement for that month,
            written YYYY-MM-DD (calendar date, no time of day, no time zone).
        permit_count: Fixed-format class — the number of registered vehicles charged a permit for
            the month, a whole non-negative integer.
        amount: Fixed-format class — the permit fee for the month in US dollars (USD), a positive
            number with 2 decimal places (cents); any further digits are rounded half up to the cent.

    Returns:
        A dictionary receipt: "rules_entry_id" (string, the statement reference of the new charge),
        "rules_plan_id" (string, the plan record charged), "event_type" (string, always
        "rules_vehicle_permit_fee"), "billing_period" (string, YYYY-MM), "entry_date" (string,
        YYYY-MM-DD), "permit_count" (integer), "amount" (number, USD with 2 decimal places),
        "rules_balance" (number, the plan record's statement balance in USD with 2 decimal places
        once the charge is on it) and "status" (string, "posted" when the charge is on the statement).
    """
    plan = ctx.find("rules_site_plans", rules_plan_id=rules_plan_id)
    customer_id = plan[0].get("customer_id") if plan else ""
    prior = float(plan[0].get("rules_balance") or 0) if plan else 0.0
    amt = round(float(amount), 2)
    rid = ctx.make_id("rle_", rules_plan_id, billing_period, entry_date, permit_count, amt)
    ctx.create("rules_ledger", rid, rules_entry_id=rid, rules_plan_id=rules_plan_id,
               customer_id=customer_id, event_type="rules_vehicle_permit_fee",
               entry_date=entry_date, billing_period=billing_period,
               permit_count=int(permit_count), amount=amt)
    balance = round(prior + amt, 2)
    ctx.update("rules_site_plans", rules_plan_id, rules_balance=balance)
    return str({"rules_entry_id": rid, "rules_plan_id": rules_plan_id,
                "event_type": "rules_vehicle_permit_fee", "billing_period": billing_period,
                "entry_date": entry_date, "permit_count": int(permit_count), "amount": amt,
                "rules_balance": balance, "status": "posted"})


@tool(owner="agent", rw="write")
def post_pet_registration_fee_a0279ba6(ctx: ToolContext, rules_plan_id: str, pet_name: str,
                                       registration_year: int, entry_date: str, amount: float) -> str:
    """Post the registration-year fee of one registered pet on a site-care plan record's rules and
    site-care statement, on the resident desk's behalf.

    One call adds one pet registration fee charge, for one named pet and one calendar registration
    year, to the statement of the named plan record and raises the record's statement balance by
    that amount. The resident sees the fee, with the pet's name and the year it covers, on their
    rules and site-care statement. Success is the receipt below with status "posted".

    Args:
        rules_plan_id: Id class — the reference number of the site-care plan record whose statement
            is charged, as returned by the site-care plan record lookup for the resident.
        pet_name: Verbatim class — the pet's name exactly as it is registered, copied character for
            character from the pet name shown on the pet's earlier registration fees on the
            statement, keeping spelling, capitals and punctuation, with no translation, normalisation,
            abbreviation, addition or deletion (verbatim).
        registration_year: Fixed-format class — the calendar year the registration covers, written
            YYYY as a four-digit integer year, for example 2026.
        entry_date: Fixed-format class — the charge date shown on the statement for the fee, written
            YYYY-MM-DD (calendar date, no time of day, no time zone).
        amount: Fixed-format class — the registration fee in US dollars (USD), a positive number with
            2 decimal places (cents); any further digits are rounded half up to the cent.

    Returns:
        A dictionary receipt: "rules_entry_id" (string, the statement reference of the new fee),
        "rules_plan_id" (string, the plan record charged), "event_type" (string, always
        "rules_pet_registration_fee"), "pet_name" (string, as registered), "registration_year"
        (integer, YYYY), "entry_date" (string, YYYY-MM-DD), "amount" (number, USD with 2 decimal
        places), "rules_balance" (number, the plan record's statement balance in USD with 2 decimal
        places once the fee is on it) and "status" (string, "posted" when the fee is on the statement).
    """
    plan = ctx.find("rules_site_plans", rules_plan_id=rules_plan_id)
    customer_id = plan[0].get("customer_id") if plan else ""
    prior = float(plan[0].get("rules_balance") or 0) if plan else 0.0
    amt = round(float(amount), 2)
    rid = ctx.make_id("rle_", rules_plan_id, pet_name, registration_year, entry_date, amt)
    ctx.create("rules_ledger", rid, rules_entry_id=rid, rules_plan_id=rules_plan_id,
               customer_id=customer_id, event_type="rules_pet_registration_fee",
               entry_date=entry_date, registration_year=int(registration_year),
               pet_name=pet_name, amount=amt)
    balance = round(prior + amt, 2)
    ctx.update("rules_site_plans", rules_plan_id, rules_balance=balance)
    return str({"rules_entry_id": rid, "rules_plan_id": rules_plan_id,
                "event_type": "rules_pet_registration_fee", "pet_name": pet_name,
                "registration_year": int(registration_year), "entry_date": entry_date,
                "amount": amt, "rules_balance": balance, "status": "posted"})


@tool(owner="user", rw="write")
def pay_site_care_past_due_0b8b512f(ctx: ToolContext, rules_plan_id: str, amount: float,
                                    payment_channel: str) -> str:
    """The resident pays, in person through the resident portal, the past-due amount on the rules
    and site-care statement of their own site-care plan record.

    One call records one payment received today from the resident on the statement of the named
    plan record, through the channel the resident uses, and lowers the record's statement balance
    by the amount paid. The payment processor issues a confirmation number, which the resident sees
    in the receipt below together with the new statement balance. Success is the receipt with
    status "received".

    Args:
        rules_plan_id: Id class — the reference number of the resident's site-care plan record whose
            statement the payment names, as given to the resident by the representative from the
            site-care plan record lookup.
        amount: Fixed-format class — the amount the resident pays in US dollars (USD), a positive
            number with 2 decimal places (cents); any further digits are rounded half up to the cent.
        payment_channel: Enum class — how the payment reaches Hearthstone, exactly one of:
            ach_autopay — a recurring automatic bank draft the resident has authorised runs the
            payment; online_portal_ach — the resident pays from a checking or savings account through
            the resident portal; online_portal_card — the resident pays with a debit or credit card
            through the resident portal; office_money_order — a money order is handed in at the
            community office; office_cashiers_check — a cashier's check is handed in at the community
            office; office_personal_check — a personal check is handed in at the community office.

    Returns:
        A dictionary receipt: "rules_entry_id" (string, the statement reference of the payment),
        "rules_plan_id" (string, the plan record credited), "event_type" (string, always
        "rules_payment"), "entry_date" (string, YYYY-MM-DD, the day received), "amount" (number, USD
        with 2 decimal places), "payment_channel" (string, as passed), "payment_ref" (string, the
        processor confirmation number), "rules_balance" (number, the statement balance in USD with
        2 decimal places once the payment is applied) and "status" (string, "received" when the
        payment is on the statement).
    """
    plan = ctx.find("rules_site_plans", rules_plan_id=rules_plan_id)
    customer_id = plan[0].get("customer_id") if plan else ""
    prior = float(plan[0].get("rules_balance") or 0) if plan else 0.0
    amt = round(float(amount), 2)
    rid = ctx.make_id("rlp_", rules_plan_id, amt, payment_channel)
    ref = "HCP-" + rid[-8:].upper()
    ctx.create("rules_ledger", rid, rules_entry_id=rid, rules_plan_id=rules_plan_id,
               customer_id=customer_id, event_type="rules_payment", entry_date=ctx.now()[:10],
               amount=amt, payment_channel=payment_channel, payment_ref=ref)
    balance = round(prior - amt, 2)
    ctx.update("rules_site_plans", rules_plan_id, rules_balance=balance)
    return str({"rules_entry_id": rid, "rules_plan_id": rules_plan_id, "event_type": "rules_payment",
                "entry_date": ctx.now()[:10], "amount": amt, "payment_channel": payment_channel,
                "payment_ref": ref, "rules_balance": balance, "status": "received"})


@tool(owner="agent", rw="write")
def post_self_help_charge_892a63af(ctx: ToolContext, rules_plan_id: str, source_record_id: str,
                                   entry_date: str, contractor_cost: float, amount: float) -> str:
    """Post the self-help maintenance charge for a violation notice the community cured itself on a
    site-care plan record's rules and site-care statement, on the resident desk's behalf.

    One call adds one self-help charge, referenced to the violation notice that was cured, carrying
    the contractor's cost for the work and the total charged, to the statement of the named plan
    record, and raises the record's statement balance by the total. The resident sees the charge,
    dated the day of the work, on their rules and site-care statement. Success is the receipt below
    with status "posted".

    Args:
        rules_plan_id: Id class — the reference number of the site-care plan record whose statement
            is charged, as returned by the site-care plan record lookup for the resident.
        source_record_id: Id class — the reference number of the violation notice the community
            cured, as returned by the rules records lookup for the plan record.
        entry_date: Fixed-format class — the date the community's contractor performed the cure,
            written YYYY-MM-DD (calendar date, no time of day, no time zone).
        contractor_cost: Fixed-format class — the contractor's cost for the work in US dollars (USD),
            a non-negative number with 2 decimal places (cents); further digits are rounded half up.
        amount: Fixed-format class — the total self-help charge in US dollars (USD), a positive number
            with 2 decimal places (cents); any further digits are rounded half up to the cent.

    Returns:
        A dictionary receipt: "rules_entry_id" (string, the statement reference of the new charge),
        "rules_plan_id" (string, the plan record charged), "event_type" (string, always
        "rules_self_help_charge"), "source_record_id" (string, the notice cured), "entry_date"
        (string, YYYY-MM-DD), "contractor_cost" (number, USD with 2 decimal places), "amount" (number,
        USD with 2 decimal places), "rules_balance" (number, the statement balance in USD with 2
        decimal places once the charge is on it) and "status" (string, "posted" when the charge is on
        the statement).
    """
    plan = ctx.find("rules_site_plans", rules_plan_id=rules_plan_id)
    customer_id = plan[0].get("customer_id") if plan else ""
    prior = float(plan[0].get("rules_balance") or 0) if plan else 0.0
    cost = round(float(contractor_cost), 2)
    amt = round(float(amount), 2)
    rid = ctx.make_id("rle_", rules_plan_id, source_record_id, entry_date, cost, amt)
    ctx.create("rules_ledger", rid, rules_entry_id=rid, rules_plan_id=rules_plan_id,
               customer_id=customer_id, event_type="rules_self_help_charge", entry_date=entry_date,
               source_record_id=source_record_id, contractor_cost=cost, amount=amt)
    balance = round(prior + amt, 2)
    ctx.update("rules_site_plans", rules_plan_id, rules_balance=balance)
    return str({"rules_entry_id": rid, "rules_plan_id": rules_plan_id,
                "event_type": "rules_self_help_charge", "source_record_id": source_record_id,
                "entry_date": entry_date, "contractor_cost": cost, "amount": amt,
                "rules_balance": balance, "status": "posted"})


@tool(owner="agent", rw="write")
def post_repeat_violation_charge_7b5daab9(ctx: ToolContext, rules_plan_id: str, source_record_id: str,
                                          entry_date: str, violation_sequence: int, amount: float) -> str:
    """Post the repeat-violation charge for a repeat violation notice on a site-care plan record's rules
    and site-care statement, on the resident desk's behalf.

    One call adds one repeat-violation charge, referenced to the repeat notice and carrying that
    notice's place in its class sequence, to the statement of the named plan record, and raises the
    record's statement balance by the amount. The resident sees the charge, dated the day the notice
    was served, on their rules and site-care statement. Success is the receipt below with status
    "posted".

    Args:
        rules_plan_id: Id class — the reference number of the site-care plan record whose statement
            is charged, as returned by the site-care plan record lookup for the resident.
        source_record_id: Id class — the reference number of the repeat violation notice charged, as
            returned by the rules records lookup for the plan record.
        entry_date: Fixed-format class — the date the repeat notice was served, written YYYY-MM-DD
            (calendar date, no time of day, no time zone).
        violation_sequence: Fixed-format class — the notice's place among the notices of its rule
            class in the window, a whole positive integer.
        amount: Fixed-format class — the repeat-violation charge in US dollars (USD), a positive number
            with 2 decimal places (cents); any further digits are rounded half up to the cent.

    Returns:
        A dictionary receipt: "rules_entry_id" (string, the statement reference of the new charge),
        "rules_plan_id" (string, the plan record charged), "event_type" (string, always
        "rules_repeat_violation_charge"), "source_record_id" (string, the repeat notice),
        "entry_date" (string, YYYY-MM-DD), "violation_sequence" (integer), "amount" (number, USD with
        2 decimal places), "rules_balance" (number, the statement balance in USD with 2 decimal
        places once the charge is on it) and "status" (string, "posted" when the charge is on the
        statement).
    """
    plan = ctx.find("rules_site_plans", rules_plan_id=rules_plan_id)
    customer_id = plan[0].get("customer_id") if plan else ""
    prior = float(plan[0].get("rules_balance") or 0) if plan else 0.0
    amt = round(float(amount), 2)
    rid = ctx.make_id("rle_", rules_plan_id, source_record_id, entry_date, violation_sequence, amt)
    ctx.create("rules_ledger", rid, rules_entry_id=rid, rules_plan_id=rules_plan_id,
               customer_id=customer_id, event_type="rules_repeat_violation_charge",
               entry_date=entry_date, source_record_id=source_record_id,
               violation_sequence=int(violation_sequence), amount=amt)
    balance = round(prior + amt, 2)
    ctx.update("rules_site_plans", rules_plan_id, rules_balance=balance)
    return str({"rules_entry_id": rid, "rules_plan_id": rules_plan_id,
                "event_type": "rules_repeat_violation_charge", "source_record_id": source_record_id,
                "entry_date": entry_date, "violation_sequence": int(violation_sequence), "amount": amt,
                "rules_balance": balance, "status": "posted"})


@tool(owner="user", rw="write")
def pay_plan_reinstatement_3e360d67(ctx: ToolContext, rules_plan_id: str, amount: float,
                                    payment_channel: str) -> str:
    """The resident pays, in person through the resident portal, the reinstatement payment on the rules
    and site-care statement of their own site-care plan record whose plan services are suspended.

    One call records one payment received today from the resident on the statement of the named
    plan record, through the channel the resident uses, and lowers the record's statement balance
    by the amount paid. The payment processor issues a confirmation number, which the resident sees
    in the receipt below together with the new statement balance. Success is the receipt with
    status "received".

    Args:
        rules_plan_id: Id class — the reference number of the resident's site-care plan record whose
            statement the payment names, as given to the resident by the representative from the
            site-care plan record lookup.
        amount: Fixed-format class — the amount the resident pays in US dollars (USD), a positive
            number with 2 decimal places (cents); any further digits are rounded half up to the cent.
        payment_channel: Enum class — how the payment reaches Hearthstone, exactly one of:
            ach_autopay — a recurring automatic bank draft the resident has authorised runs the
            payment; online_portal_ach — the resident pays from a checking or savings account through
            the resident portal; online_portal_card — the resident pays with a debit or credit card
            through the resident portal; office_money_order — a money order is handed in at the
            community office; office_cashiers_check — a cashier's check is handed in at the community
            office; office_personal_check — a personal check is handed in at the community office.

    Returns:
        A dictionary receipt: "rules_entry_id" (string, the statement reference of the payment),
        "rules_plan_id" (string, the plan record credited), "event_type" (string, always
        "rules_payment"), "entry_date" (string, YYYY-MM-DD, the day received), "amount" (number, USD
        with 2 decimal places), "payment_channel" (string, as passed), "payment_ref" (string, the
        processor confirmation number), "rules_balance" (number, the statement balance in USD with
        2 decimal places once the payment is applied) and "status" (string, "received" when the
        payment is on the statement).
    """
    plan = ctx.find("rules_site_plans", rules_plan_id=rules_plan_id)
    customer_id = plan[0].get("customer_id") if plan else ""
    prior = float(plan[0].get("rules_balance") or 0) if plan else 0.0
    amt = round(float(amount), 2)
    rid = ctx.make_id("rlr_", rules_plan_id, amt, payment_channel)
    ref = "HCR-" + rid[-8:].upper()
    ctx.create("rules_ledger", rid, rules_entry_id=rid, rules_plan_id=rules_plan_id,
               customer_id=customer_id, event_type="rules_payment", entry_date=ctx.now()[:10],
               amount=amt, payment_channel=payment_channel, payment_ref=ref)
    balance = round(prior - amt, 2)
    ctx.update("rules_site_plans", rules_plan_id, rules_balance=balance)
    return str({"rules_entry_id": rid, "rules_plan_id": rules_plan_id, "event_type": "rules_payment",
                "entry_date": ctx.now()[:10], "amount": amt, "payment_channel": payment_channel,
                "payment_ref": ref, "rules_balance": balance, "status": "received"})

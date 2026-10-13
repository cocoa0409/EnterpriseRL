"""Hidden task tools of the personal_services_packages difficulty (category services).

Each tool performs one atomic write on the personal services account and is reached only through
unlock_* -> call_*. No tool checks a policy condition, computes a policy amount or refuses a call:
the agent decides every value from the published policies and the records, and passes it in.
"""

from erlbench import ToolContext, tool


@tool(owner="user", rw="write")
def sign_services_suspension_89d6021d(ctx: ToolContext, services_plan_id: str, first_suspended_month: str,
                                      suspended_months: int) -> str:
    """Sign, as the resident or the resident's financial agent, a suspension of a personal services plan for a
    run of whole calendar months. The signed suspension is recorded on the plan: its suspension start becomes
    the first day of the first suspended month and its suspension end becomes the last day of the last
    suspended month, so that no package fee is charged and no hours are granted for those months. The plan's
    status itself is unchanged by signing; the suspension takes hold on its start date. The receipt confirms
    the plan and the suspension window now on record.

    Args:
        services_plan_id: Id class — the reference number of the personal services plan being suspended, as
            returned by the personal services plan lookup for this resident.
        first_suspended_month: Fixed-format class — the first day of the first calendar month to be suspended,
            written YYYY-MM-DD with the day always 01, local community date; never empty.
        suspended_months: Fixed-format class — the number of whole calendar months suspended, counted from
            and including the first suspended month, a positive integer with no fraction and no unit text.

    Returns:
        A dictionary rendered as text with the keys status ("suspension_signed" when the suspension is on
        record), services_plan_id (the plan reference number), suspension_start_date (YYYY-MM-DD, first day
        of the first suspended month), suspension_end_date (YYYY-MM-DD, last day of the last suspended month)
        and suspended_months (the integer number of months recorded).
    """
    index = int(first_suspended_month[:4]) * 12 + int(first_suspended_month[5:7]) - 1 + int(suspended_months) - 1
    end_year, end_month = index // 12, index % 12 + 1
    month_days = (31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31)[end_month - 1]
    if end_month == 2 and end_year % 4 == 0 and (end_year % 100 != 0 or end_year % 400 == 0):
        month_days = 29
    end_date = f"{end_year:04d}-{end_month:02d}-{month_days:02d}"
    ctx.update("services_plans", services_plan_id, suspension_start_date=first_suspended_month,
               suspension_end_date=end_date)
    return str({"status": "suspension_signed", "services_plan_id": services_plan_id,
                "suspension_start_date": first_suspended_month, "suspension_end_date": end_date,
                "suspended_months": int(suspended_months)})


@tool(owner="agent", rw="write")
def post_services_visit_credit_5ef485c2(ctx: ToolContext, services_plan_id: str, source_entry_id: str,
                                        credit_reason: str, billing_period: str, amount: float) -> str:
    """Post a money credit on a personal services account against one earlier charge entry. One call books
    one credit entry dated today that references the charge it corrects, carries its reason and billing
    month, and lowers the amount owed on the plan by the credited amount; the plan's hours are not touched.
    The resident sees the credit on the next personal services statement. The receipt returns the new credit
    entry's reference number and the plan's amount owed after the credit.

    Args:
        services_plan_id: Id class — the reference number of the personal services plan whose account is
            credited, as returned by the personal services plan lookup.
        source_entry_id: Id class — the reference number of the personal services ledger entry being
            credited, as returned by the personal services ledger lookup.
        credit_reason: Enum class — why the charge is credited, exactly one of: service_dispute when a charge
            is corrected because the service was not delivered, was delivered short, or was billed twice;
            billing_error when a charge was posted against the wrong plan or at the wrong rate;
            residency_end_proration when the package fee for the days after a residency's end is returned.
        billing_period: Fixed-format class — the plan month the credit relates to, written YYYY-MM, the month
            of the charge being credited.
        amount: Fixed-format class — the credit in USD, a positive amount to 2 decimal places, rounded half up
            to the cent.

    Returns:
        A dictionary rendered as text with the keys status ("credit_posted" on success), services_entry_id
        (reference number of the new credit entry), source_entry_id (the charge entry credited), amount (the
        credit in USD, 2 decimal places), posting_date (YYYY-MM-DD, today) and account_balance (the plan's
        amount owed in USD after the credit, 2 decimal places).
    """
    plan = (ctx.find("services_plans", services_plan_id=services_plan_id) or [{}])[0]
    value = round(float(amount), 2)
    rid = ctx.make_id("sle_", services_plan_id, source_entry_id, credit_reason, billing_period, value)
    today = ctx.now()[:10]
    ctx.create("services_ledger", rid, services_entry_id=rid, services_plan_id=services_plan_id,
               customer_id=plan.get("customer_id"), event_type="services_credit", amount=value,
               posting_date=today, credit_reason=credit_reason, source_entry_id=source_entry_id,
               billing_period=billing_period)
    balance = round(float(plan.get("account_balance") or 0) - value, 2)
    ctx.update("services_plans", services_plan_id, account_balance=balance)
    return str({"status": "credit_posted", "services_entry_id": rid, "source_entry_id": source_entry_id,
                "amount": value, "posting_date": today, "account_balance": balance})


@tool(owner="user", rw="write")
def sign_services_package_change_2a41e92a(ctx: ToolContext, services_plan_id: str, target_variant_name: str,
                                          pending_change_date: str) -> str:
    """Sign, as the resident or the resident's financial agent, a change of a personal services plan to another
    package. The signed change is recorded on the plan as a scheduled change: the package the plan will move
    to and the first day of the month from which the new package's fee and monthly hours apply. The package
    currently in effect is not altered by signing; any change already scheduled is replaced by this one. The
    receipt confirms the plan, the package scheduled and the date it takes effect.

    Args:
        services_plan_id: Id class — the reference number of the personal services plan being changed, as
            returned by the personal services plan lookup for this resident.
        target_variant_name: Enum class — the package the plan changes to, exactly one of:
            Personal Services Pay-As-You-Go Plan when the resident moves to paying by the hour with no monthly
            package; Personal Services Essentials Package when the resident moves to the 4-hour package;
            Personal Services Companion Package when the resident moves to the 8-hour package;
            Personal Services Comfort Package when the resident moves to the 12-hour package;
            Personal Services Premier Package when the resident moves to the 20-hour package;
            Personal Services Concierge Package when the resident moves to the 30-hour package;
            none when a change already scheduled is withdrawn and no new package is scheduled.
        pending_change_date: Fixed-format class — the first day of the month from which the new package
            applies, written YYYY-MM-DD with the day always 01, local community date; never empty.

    Returns:
        A dictionary rendered as text with the keys status ("change_scheduled" when the change is on record),
        services_plan_id (the plan reference number), pending_variant_name (the package scheduled, as its
        full official name) and pending_change_date (YYYY-MM-DD, the date the change takes effect).
    """
    ctx.update("services_plans", services_plan_id, pending_variant_name=target_variant_name,
               pending_change_date=pending_change_date)
    return str({"status": "change_scheduled", "services_plan_id": services_plan_id,
                "pending_variant_name": target_variant_name, "pending_change_date": pending_change_date})


@tool(owner="agent", rw="write")
def post_services_order_hours_8d682fe6(ctx: ToolContext, services_plan_id: str, order_reference: str,
                                       draw_basis: str, event_type: str, billing_period: str, hours: float,
                                       amount: float) -> str:
    """Post the personal service hours owed for one service order on a personal services account. One call
    books one entry dated today against the order: either hours taken from the plan's available hours, which
    lowers the hours available on the plan, or hours billed at the package's hourly rate because no hours
    remain, which raises the amount owed. The entry carries the order number, why the hours are owed and the
    billing month of the service date. The receipt returns the new entry's reference number and the plan's
    hours available and amount owed after it.

    Args:
        services_plan_id: Id class — the reference number of the personal services plan the order belongs to,
            as returned by the personal services plan lookup.
        order_reference: Verbatim class — the service order number exactly as shown on the order in the
            service order lookup, copied character for character with no change (verbatim).
        draw_basis: Enum class — why hours are owed for the order, exactly one of: service_delivered when the
            visit took place; late_cancellation when the resident cancelled the visit too late; no_show when
            staff arrived and the resident declined the service or was absent.
        event_type: Enum class — the kind of entry posted for the order, exactly one of:
            services_hours_draw when the hours are taken from the plan's available hours;
            services_hourly_charge when the hours are billed at the package's hourly rate because no available
            hours remain. The account's other entry kinds belong to other actions and are not meant for an
            order's hours: services_package_fee_charge is a monthly package fee; services_hours_grant is a
            monthly allotment; services_hours_rollover is hours carried into a month; services_hours_expire is
            hours lapsing; services_hours_restore is hours given back after a dispute;
            services_alacarte_charge is a separately priced service; services_fee_charge is a late or returned
            payment fee; services_payment is money received; services_payment_return is a payment reinstated
            unpaid; services_credit is a money credit.
        billing_period: Fixed-format class — the month of the service date, written YYYY-MM.
        hours: Fixed-format class — the hours owed, decimal hours to 2 decimal places, a positive number.
        amount: Fixed-format class — for an hours charge the money billed in USD to 2 decimal places, rounded
            half up to the cent; 0.00 when the entry takes hours from the plan's available hours.

    Returns:
        A dictionary rendered as text with the keys status ("hours_posted" on success), services_entry_id
        (reference number of the new entry), event_type (the kind of entry booked), hours (2 decimal places),
        amount (USD, 2 decimal places, 0.00 for hours taken from the plan), hours_available (hours on the plan
        after the entry, 2 decimal places) and account_balance (amount owed in USD after the entry, 2 decimal
        places).
    """
    plan = (ctx.find("services_plans", services_plan_id=services_plan_id) or [{}])[0]
    hrs = round(float(hours), 2)
    value = round(float(amount), 2)
    rid = ctx.make_id("sle_", services_plan_id, order_reference, draw_basis, event_type, billing_period, hrs, value)
    available = round(float(plan.get("hours_available") or 0), 2)
    balance = round(float(plan.get("account_balance") or 0), 2)
    if event_type == "services_hourly_charge":
        ctx.create("services_ledger", rid, services_entry_id=rid, services_plan_id=services_plan_id,
                   customer_id=plan.get("customer_id"), event_type=event_type, hours=hrs, amount=value,
                   posting_date=ctx.now()[:10], billing_period=billing_period, order_reference=order_reference,
                   draw_basis=draw_basis)
        balance = round(balance + value, 2)
    else:
        ctx.create("services_ledger", rid, services_entry_id=rid, services_plan_id=services_plan_id,
                   customer_id=plan.get("customer_id"), event_type=event_type, hours=hrs,
                   posting_date=ctx.now()[:10], billing_period=billing_period, order_reference=order_reference,
                   draw_basis=draw_basis)
        available = round(available - hrs, 2)
    ctx.update("services_plans", services_plan_id, hours_available=available, account_balance=balance)
    return str({"status": "hours_posted", "services_entry_id": rid, "event_type": event_type, "hours": hrs,
                "amount": value, "hours_available": available, "account_balance": balance})

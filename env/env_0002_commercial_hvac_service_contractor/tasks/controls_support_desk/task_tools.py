"""Hidden task tools for the controls support desk (Building Automation Service Plans).

Each function performs one atomic business write on an automation service plan. The
names are discoverable only through the extended charter's target_tool entries and are
reached at runtime through the unlock/call meta tools.
"""

from erlbench import ToolContext, tool


@tool(owner="agent", rw="write")
def charge_controls_support_overage_c0d5009e(ctx: ToolContext, plan_id: str, site_id: str,
                                             charge_amount_usd: float) -> str:
    """Invoice a building owner for controls support work on their automation service plan that
    the plan year's included support pool does not cover. One call raises one support overage
    line on a new office invoice against the named plan: the amount is added to what the owner
    owes under that plan, so the plan's outstanding balance rises by exactly that amount and the
    new charge appears in the plan's billing history at the building named, periodised to the
    calendar month in which it is raised. The owner sees the charge on the invoice number quoted
    back in the confirmation.

    Args:
        plan_id: Id class — the reference number of the automation service plan the charge is
            raised against, read from the automation service plan lookup before the call.
        site_id: Id class — the reference number of the building whose controls system the work
            concerned, read from the building lookup or from the plan record before the call.
        charge_amount_usd: Fixed-format class — the money the owner is being invoiced for the
            uncovered support work, in USD, recorded positive and to 2 decimal places; give the
            settled figure only, never a range, and never an expression.

    Returns:
        A confirmation sentence in plain text naming the booked history entry's reference, the
        invoice number the line was raised on, the amount in USD to two decimal places, the
        calendar month the line is periodised to, the plan it was charged to and the balance now
        owed under the plan. The sentence being returned at
        all is what indicates the charge was booked; no separate status flag is sent back.
    """
    rid = ctx.make_id("cev_", plan_id, site_id, charge_amount_usd)
    amount = round(float(charge_amount_usd), 2)
    plan = (ctx.find("controls_plans", plan_id=plan_id) or [{}])[0]
    _digits = "".join(c for c in rid if c.isdigit()) or "0"
    inv = f"INV-{int(_digits[-8:]) % 100000000:08d}"
    period = ctx.now()[:7]
    ctx.create("controls_events", rid, event_id=rid, plan_id=plan_id,
               customer_id=plan.get("customer_id"), site_id=site_id,
               event_type="controls_invoice_charged", invoice_ref=inv,
               charge_type="support_overage", amount_usd=amount,
               billing_period=period)
    balance = round(float(plan.get("balance_due") or 0) + amount, 2)
    ctx.update("controls_plans", plan_id, balance_due=balance)
    return (f"Support overage {rid} booked on invoice {inv} for {amount:.2f} USD, periodised to "
            f"{period}, against plan {plan_id}; balance now owed under the plan is {balance:.2f} USD.")


@tool(owner="user", rw="write")
def record_controls_plan_payment_09134fd7(ctx: ToolContext, plan_id: str,
                                          payment_amount_usd: float,
                                          payment_method: str) -> str:
    """Put a payment through against a building automation service plan. The building owner makes
    this payment themselves: one call applies one payment of their own money to the named plan,
    reduces what they owe under that plan by exactly that amount, and files the payment in the
    plan's billing history under today's office date. The owner can see the payment and the
    reduced balance on the plan from that moment.

    Args:
        plan_id: Id class — the reference number of the automation service plan the money is being
            paid against, read from the automation service plan lookup before the call.
        payment_amount_usd: Fixed-format class — the money actually being paid, in USD, recorded
            positive and to 2 decimal places.
        payment_method: Enum class — how the owner is sending the money, one of exactly four
            settled values. The value check applies when the owner is posting or hand-delivering a
            paper cheque drawn on the company account. The value ach applies when the owner is
            pushing the money from their own bank by electronic transfer through the automated
            clearing house. The value credit_card applies when the owner is putting the payment on
            a company card over the telephone or through the portal. The value wire applies when
            the owner is sending same-day cleared funds by bank wire.

    Returns:
        A confirmation sentence in plain text naming the filed payment entry's reference, the
        amount paid in USD to two decimal places, the plan it was applied to, the method it came
        in by and the balance still owed under the plan afterwards. The sentence being returned at
        all is what indicates the payment was applied; no separate status flag is sent back.
    """
    rid = ctx.make_id("cev_", plan_id, payment_amount_usd, payment_method)
    amount = round(float(payment_amount_usd), 2)
    plan = (ctx.find("controls_plans", plan_id=plan_id) or [{}])[0]
    ctx.create("controls_events", rid, event_id=rid, plan_id=plan_id,
               customer_id=plan.get("customer_id"), site_id=plan.get("site_id"),
               event_type="controls_payment_received", amount_usd=amount,
               payment_method=payment_method, received_date=ctx.now()[:10])
    balance = round(float(plan.get("balance_due") or 0) - amount, 2)
    ctx.update("controls_plans", plan_id, balance_due=balance)
    return (f"Payment {rid} of {amount:.2f} USD applied to plan {plan_id} by {payment_method}; "
            f"balance still owed under the plan is {balance:.2f} USD.")


@tool(owner="agent", rw="write")
def reinstate_controls_plan_58d0efe4(ctx: ToolContext, plan_id: str,
                                     reinstatement_charge_usd: float) -> str:
    """Restore remote access and alarm monitoring on a building automation service plan that is
    standing withdrawn, and raise the reinstatement charge that goes with restoring it. One call
    moves the named plan back to live standing, stamps today's office date as the day service was
    restored, and books the reinstatement charge on a new office invoice so that what the owner
    owes under the plan rises by that amount. From then on the owner's engineers can connect to
    the site again and the monitoring desk watches the site's alarms.

    Args:
        plan_id: Id class — the reference number of the automation service plan being put back
            into service, read from the automation service plan lookup before the call.
        reinstatement_charge_usd: Fixed-format class — the money charged for putting the plan back
            into service, in USD, recorded positive and to 2 decimal places.

    Returns:
        A confirmation sentence in plain text naming the plan restored, the day service was
        restored, the reference of the booked charge entry, the invoice number it was raised on,
        the charge in USD to two decimal places and the balance now owed under the plan. The
        sentence being returned at all is what indicates the plan is live again; no separate
        status flag is sent back.
    """
    rid = ctx.make_id("cev_", plan_id, reinstatement_charge_usd)
    amount = round(float(reinstatement_charge_usd), 2)
    plan = (ctx.find("controls_plans", plan_id=plan_id) or [{}])[0]
    _digits = "".join(c for c in rid if c.isdigit()) or "0"
    inv = f"INV-{int(_digits[-8:]) % 100000000:08d}"
    ctx.create("controls_events", rid, event_id=rid, plan_id=plan_id,
               customer_id=plan.get("customer_id"), site_id=plan.get("site_id"),
               event_type="controls_invoice_charged", invoice_ref=inv,
               charge_type="reinstatement", amount_usd=amount)
    balance = round(float(plan.get("balance_due") or 0) + amount, 2)
    ctx.update("controls_plans", plan_id, status="active",
               reinstatement_date=ctx.now()[:10], balance_due=balance)
    return (f"Plan {plan_id} restored to service on {ctx.now()[:10]}; reinstatement {rid} booked "
            f"on invoice {inv} for {amount:.2f} USD; balance now owed under the plan is "
            f"{balance:.2f} USD.")


@tool(owner="agent", rw="write")
def issue_controls_alarm_credit_7b85e02f(ctx: ToolContext, plan_id: str,
                                         credit_amount_usd: float) -> str:
    """Put a credit on a building automation service plan for monitored alarms the monitoring desk
    failed to acknowledge, that is, for a missed acknowledgement target. One call files one credit
    entry against the named plan, marked as a missed-acknowledgement credit and periodised to the
    calendar month in which it is filed, and reduces what the owner owes under that plan by exactly
    that amount. The owner sees the credit in the plan's billing history and the lower balance
    straight away.

    Args:
        plan_id: Id class — the reference number of the automation service plan being credited,
            read from the automation service plan lookup before the call.
        credit_amount_usd: Fixed-format class — the money being put on the plan for the missed
            acknowledgements, in USD, recorded positive and to 2 decimal places.

    Returns:
        A confirmation sentence in plain text naming the filed credit entry's reference, the
        amount credited in USD to two decimal places, the plan it was applied to, the calendar
        month it is periodised to and the balance owed under the plan afterwards. The sentence
        being returned at all is what indicates the credit was filed; no separate status flag is
        sent back.
    """
    rid = ctx.make_id("cev_", plan_id, credit_amount_usd)
    amount = round(float(credit_amount_usd), 2)
    plan = (ctx.find("controls_plans", plan_id=plan_id) or [{}])[0]
    period = ctx.now()[:7]
    ctx.create("controls_events", rid, event_id=rid, plan_id=plan_id,
               customer_id=plan.get("customer_id"), site_id=plan.get("site_id"),
               event_type="controls_credit_issued", credit_reason="missed_acknowledgement",
               amount_usd=amount, billing_period=period)
    balance = round(float(plan.get("balance_due") or 0) - amount, 2)
    ctx.update("controls_plans", plan_id, balance_due=balance)
    return (f"Missed-acknowledgement credit {rid} of {amount:.2f} USD filed against plan {plan_id}, "
            f"periodised to {period}; balance owed under the plan is now {balance:.2f} USD.")


@tool(owner="user", rw="write")
def authorise_controls_upgrade_c5086d5b(ctx: ToolContext, plan_id: str, site_id: str,
                                        authorised_labor_usd: float) -> str:
    """Let a building owner authorise, in person, the labor price of a controls software upgrade
    at one of their buildings. One call files the owner's written authorisation against the named
    plan and building, marks it confirmed, and books the authorised labor on a new office invoice,
    periodised to the calendar month in which it is booked, so that what the owner owes under the
    plan rises by exactly that amount. The owner has then committed the money and can see both the
    filed authorisation and the invoice line on the plan.

    Args:
        plan_id: Id class — the reference number of the automation service plan whose controls
            software is being upgraded, read from the automation service plan lookup before the
            call.
        site_id: Id class — the reference number of the building whose controls system is being
            upgraded, read from the building lookup or from the plan record before the call.
        authorised_labor_usd: Fixed-format class — the labor money the owner is committing to for
            the upgrade, in USD, recorded positive and to 2 decimal places; give the settled
            figure only, never a range, and never an expression.

    Returns:
        A confirmation sentence in plain text naming the filed authorisation's reference, the
        reference of the booked charge entry, the invoice number it was raised on, the labor
        amount in USD to two decimal places, the calendar month it is periodised to, the plan and
        the balance now owed under the plan. The
        sentence being returned at all is what indicates the authorisation was filed and the labor
        committed; no separate status flag is sent back.
    """
    req = ctx.make_id("crq_", plan_id, authorised_labor_usd)
    rid = ctx.make_id("cev_", plan_id, site_id, authorised_labor_usd)
    amount = round(float(authorised_labor_usd), 2)
    plan = (ctx.find("controls_plans", plan_id=plan_id) or [{}])[0]
    _digits = "".join(c for c in rid if c.isdigit()) or "0"
    inv = f"INV-{int(_digits[-8:]) % 100000000:08d}"
    period = ctx.now()[:7]
    ctx.create("controls_requests", req, request_id=req, customer_id=plan.get("customer_id"),
               plan_id=plan_id, site_id=site_id, request_type="upgrade_authorization",
               outcome="confirmed", requested_date=ctx.now()[:10], created_at=ctx.now())
    ctx.create("controls_events", rid, event_id=rid, plan_id=plan_id,
               customer_id=plan.get("customer_id"), site_id=site_id,
               event_type="controls_invoice_charged", invoice_ref=inv,
               charge_type="upgrade_labor", amount_usd=amount, billing_period=period)
    balance = round(float(plan.get("balance_due") or 0) + amount, 2)
    ctx.update("controls_plans", plan_id, balance_due=balance)
    return (f"Upgrade authorisation {req} filed for plan {plan_id}; labor {rid} booked on invoice "
            f"{inv} for {amount:.2f} USD, periodised to {period}; balance now owed under the plan "
            f"is {balance:.2f} USD.")

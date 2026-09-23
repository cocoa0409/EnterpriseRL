"""Hidden task tools for the energy services desk of Halvorsen Mechanical & Controls, Inc.

Each tool lands one atomic write on the energy monitoring records. No tool aggregates
history, prices anything, or judges whether a policy condition is met: the client services
agent reads the subscription, its ledger and the building's other cover, works the figure
out from the published terms, and passes it in.
"""

from erlbench import ToolContext, tool


@tool(owner="agent", rw="write")
def charge_analyst_overage_446fe12a(ctx: ToolContext, subscription_id: str, customer_id: str,
                                    billing_period: str, due_date: str, amount_usd: float) -> str:
    """Invoice a building owner for energy analyst work drawn beyond the hours their subscription
    year includes, entering it as one charge line on that subscription's account.

    The line is entered on the owner's energy monitoring subscription as an analyst overage charge
    for the period named, raising the amount the subscription owes by the amount entered and
    appearing on the subscription's invoice history from the moment it is accepted. The office
    allocates the invoice number itself, so the same charge entered twice with the same details
    lands once. Success is the confirmation text below, which carries the invoice number the charge
    was billed on.

    Args:
        subscription_id: Id class — the reference number of the energy monitoring subscription the
            charge is entered on, read from the subscription lookup for this building owner.
        customer_id: Id class — the reference number of the building owner's account the charge is
            billed to, read from the account lookup.
        billing_period: Fixed-format class — the period the charge covers, written as YYYY-MM for a
            monthly period, YYYY-Qn for a quarterly period, or YYYY for a whole subscription year;
            no other spelling is accepted and the value is never left empty.
        due_date: Fixed-format class — the day the invoice carrying this charge falls due, written
            as YYYY-MM-DD in the office's local calendar, never left empty.
        amount_usd: Fixed-format class — the money amount of the charge in USD, recorded positive
            and to 2 decimal places, rounded half up to the cent as it is entered.

    Returns:
        A confirmation sentence in plain text stating the invoice number allocated to the charge
        (INV- followed by 8 digits), the subscription it was entered on, the period it covers and
        the amount billed in USD to two decimal places. Any sentence of that shape means the charge
        now stands on the subscription's invoice history.
    """
    rid = ctx.make_id("eovg_", subscription_id, customer_id, billing_period, due_date, amount_usd)
    invoice_ref = "INV-" + f"{int(rid[-6:], 16) % 100000000:08d}"
    ctx.create("energy_events", rid, event_id=rid, subscription_id=subscription_id,
               customer_id=customer_id, event_type="energy_invoice_charged",
               charge_type="analyst_overage", invoice_ref=invoice_ref,
               amount_usd=round(float(amount_usd), 2), billing_period=billing_period,
               due_date=due_date)
    return (f"Analyst overage billed on {invoice_ref} against subscription {subscription_id} "
            f"for {billing_period}: USD {round(float(amount_usd), 2):.2f}.")


@tool(owner="user", rw="write")
def settle_subscription_balance_535836bf(ctx: ToolContext, subscription_id: str, customer_id: str,
                                         invoice_ref: str, payment_method: str,
                                         amount_usd: float) -> str:
    """Pay money into an energy monitoring subscription account, clearing what it owes, with the
    payment recorded against the invoice the owner names.

    The building owner makes this payment themselves. It is entered on the subscription's payment
    history with the day it was received, reduces the amount the subscription owes by the amount
    paid, and is visible to the owner on the account and on the next statement. The same payment
    entered twice with the same details lands once. Success is the confirmation text below, which
    repeats the amount taken and the invoice it was applied to.

    Args:
        subscription_id: Id class — the reference number of the energy monitoring subscription the
            payment is entered on, as the client services agent states it when handing the payment
            over.
        customer_id: Id class — the reference number of the building owner's account making the
            payment, as the client services agent states it when handing the payment over.
        invoice_ref: Fixed-format class — the invoice number the payment is applied to, written
            exactly as INV- followed by 8 digits, copied from the invoice history of this
            subscription; never left empty.
        payment_method: Enum class — how the money is being paid, one of exactly four values.
            check — the owner is posting or hand-delivering a paper cheque drawn on their own bank.
            ach — the owner authorises an electronic debit from the bank account already held on
            their file. credit_card — the owner is paying on a company card taken over the phone.
            wire — the owner is sending a same-day bank wire transfer from their treasury.
        amount_usd: Fixed-format class — the money amount paid in USD, recorded positive and to 2
            decimal places, rounded half up to the cent as it is entered.

    Returns:
        A confirmation sentence in plain text naming the subscription the payment was entered on,
        the invoice number it was applied to, the amount taken in USD to two decimal places and the
        way it was paid. Any sentence of that shape means the payment now stands on the
        subscription's payment history.
    """
    rid = ctx.make_id("epay_", subscription_id, customer_id, invoice_ref, payment_method, amount_usd)
    ctx.create("energy_events", rid, event_id=rid, subscription_id=subscription_id,
               customer_id=customer_id, event_type="energy_payment_received",
               invoice_ref=invoice_ref, amount_usd=round(float(amount_usd), 2),
               payment_method=payment_method, received_date=ctx.now()[:10])
    return (f"Payment of USD {round(float(amount_usd), 2):.2f} received on subscription "
            f"{subscription_id} against {invoice_ref} by {payment_method}.")


@tool(owner="user", rw="write")
def authorise_meter_coverage_01d41e30(ctx: ToolContext, subscription_id: str, meters_covered: int,
                                      annual_fee_usd: float) -> str:
    """Take the metered points a building actually meters onto the owner's energy monitoring
    subscription at the annual fee stated, on the owner's own authority.

    The building owner authorises this themselves, because it commits them to a higher annual fee.
    The subscription's covered point count is set to the number given, its annual fee is set to the
    figure given, and the change is stamped on the subscription as a points addition dated the day it
    is made, so the owner sees the new coverage and the new fee on the account at once. Success is the
    confirmation text below, which repeats both figures.

    Args:
        subscription_id: Id class — the reference number of the energy monitoring subscription whose
            coverage is being authorised, as the client services agent states it when handing the
            authorisation over.
        meters_covered: Fixed-format class — the number of metered points the subscription is to
            cover after the authorisation, expressed exactly as the record holds it: integer, meters;
            never blank and never carrying a fractional part.
        annual_fee_usd: Fixed-format class — the annual fee the subscription is to carry after the
            authorisation, in USD and to 2 decimal places, rounded half up to the cent as it is
            entered.

    Returns:
        A confirmation sentence in plain text naming the subscription, the number of metered points it
        now covers and the annual fee in USD to two decimal places now standing on it. Any sentence of
        that shape means the coverage and the fee on the account have both been changed.
    """
    ctx.update("energy_subscriptions", subscription_id, meters_covered=int(meters_covered),
               annual_subscription_fee_usd=round(float(annual_fee_usd), 2),
               last_change_type="meters_added", last_change_date=ctx.now()[:10])
    return (f"Subscription {subscription_id} now covers {int(meters_covered)} metered points at an "
            f"annual fee of USD {round(float(annual_fee_usd), 2):.2f}.")


@tool(owner="agent", rw="write")
def reset_performance_baseline_0e66b991(ctx: ToolContext, subscription_id: str,
                                        baseline_kwh: int) -> str:
    """Restate the performance baseline an energy monitoring subscription measures against, setting it
    to the annual electricity figure given.

    The subscription's baseline is replaced with the figure entered and the change is stamped on the
    subscription as a baseline reset dated the day it is made, so every later comparison of the
    building's use is made against the new figure and the owner sees it on the account. Success is the
    confirmation text below, which repeats the baseline now standing.

    Args:
        subscription_id: Id class — the reference number of the energy monitoring subscription whose
            baseline is being restated, read from the subscription lookup for this building owner.
        baseline_kwh: Fixed-format class — the baseline annual electricity use to stand on the
            subscription, expressed exactly as the record holds it: integer, kilowatt hours per year;
            never blank and never carrying a decimal part.

    Returns:
        A confirmation sentence in plain text naming the subscription and the baseline annual
        electricity use in kilowatt hours now standing on it. Any sentence of that shape means the
        baseline on the account has been replaced.
    """
    ctx.update("energy_subscriptions", subscription_id, baseline_kwh=int(baseline_kwh),
               last_change_type="baseline_reset", last_change_date=ctx.now()[:10])
    return (f"Baseline on subscription {subscription_id} restated to {int(baseline_kwh)} kilowatt "
            f"hours a year.")


@tool(owner="agent", rw="write")
def verify_period_savings_a6d7fa6e(ctx: ToolContext, subscription_id: str, customer_id: str,
                                   site_id: str, billing_period: str, verified_savings_usd: float,
                                   guaranteed_savings_usd: float, weather_normalized: str) -> str:
    """Sign off the measured savings of a true-up period on an energy monitoring subscription, entering
    the savings measured against the baseline and the savings guaranteed for that period.

    The verification is entered on the subscription's record for the period named, dated the day it is
    signed off, and the owner sees both figures on the true-up for that period. The same verification
    entered twice with the same details lands once.
    Success is the confirmation text below, which repeats both figures.

    Args:
        subscription_id: Id class — the reference number of the energy monitoring subscription being
            verified, read from the subscription lookup for this building owner.
        customer_id: Id class — the reference number of the building owner's account the verification
            belongs to, read from the account lookup.
        site_id: Id class — the reference number of the building whose use was measured, read from the
            subscription record or the building lookup.
        billing_period: Fixed-format class — the true-up period being verified, written as YYYY-MM for
            a monthly period, YYYY-Qn for a quarterly period, or YYYY for a whole subscription year;
            no other spelling is accepted and the value is never left empty.
        verified_savings_usd: Fixed-format class — the savings measured against the baseline for the
            period, in USD and to 2 decimal places, recorded positive and rounded half up to the cent.
        guaranteed_savings_usd: Fixed-format class — the savings guaranteed for the same period, in
            USD and to 2 decimal places, recorded positive and rounded half up to the cent.
        weather_normalized: Enum class — whether the comparison was weather normalised, one of exactly
            two values. true — the period's use and the baseline were adjusted for the weather before
            they were compared. false — they were compared as recorded, with no weather adjustment.

    Returns:
        A confirmation sentence in plain text naming the subscription, the period verified, the savings
        measured in USD to two decimal places and the savings guaranteed in USD to two decimal places.
        Any sentence of that shape means the verification now stands on the subscription's record.
    """
    rid = ctx.make_id("evrf_", subscription_id, billing_period, verified_savings_usd,
                      guaranteed_savings_usd)
    ctx.create("energy_events", rid, event_id=rid, subscription_id=subscription_id,
               customer_id=customer_id, site_id=site_id, event_type="energy_savings_verified",
               billing_period=billing_period, verified_date=ctx.now()[:10],
               verified_savings_usd=round(float(verified_savings_usd), 2),
               guaranteed_savings_usd=round(float(guaranteed_savings_usd), 2),
               weather_normalized=weather_normalized)
    return (f"True-up for {billing_period} on subscription {subscription_id} verified: measured "
            f"savings USD {round(float(verified_savings_usd), 2):.2f} against guaranteed savings USD "
            f"{round(float(guaranteed_savings_usd), 2):.2f}.")


@tool(owner="agent", rw="write")
def pay_savings_shortfall_2f1bc21a(ctx: ToolContext, subscription_id: str, customer_id: str,
                                   billing_period: str, amount_usd: float) -> str:
    """Pay a building owner against the savings guarantee on their energy monitoring subscription for a
    true-up period that fell short.

    The payment is entered on the subscription's guarantee record for the period named, dated the day
    it is made; it draws the amount paid from the guarantee standing behind the subscription year and
    the owner sees it as money paid out to them on the account. The same payment entered twice with the
    same details lands once. Success is the confirmation text below, which repeats the amount paid.

    Args:
        subscription_id: Id class — the reference number of the energy monitoring subscription the
            payment is made against, read from the subscription lookup for this building owner.
        customer_id: Id class — the reference number of the building owner's account being paid, read
            from the account lookup.
        billing_period: Fixed-format class — the true-up period the payment settles, written as
            YYYY-MM for a monthly period, YYYY-Qn for a quarterly period, or YYYY for a whole
            subscription year; no other spelling is accepted and the value is never left empty.
        amount_usd: Fixed-format class — the money amount paid to the owner, in USD and to 2 decimal
            places, recorded positive and rounded half up to the cent as it is entered.

    Returns:
        A confirmation sentence in plain text naming the subscription, the period settled and the
        amount paid in USD to two decimal places. Any sentence of that shape means the payment now
        stands on the subscription's guarantee record.
    """
    rid = ctx.make_id("eshf_", subscription_id, billing_period, amount_usd)
    ctx.create("energy_events", rid, event_id=rid, subscription_id=subscription_id,
               customer_id=customer_id, event_type="energy_shortfall_paid",
               billing_period=billing_period, amount_usd=round(float(amount_usd), 2),
               paid_date=ctx.now()[:10])
    return (f"Shortfall payment of USD {round(float(amount_usd), 2):.2f} made to {customer_id} on "
            f"subscription {subscription_id} for {billing_period}.")

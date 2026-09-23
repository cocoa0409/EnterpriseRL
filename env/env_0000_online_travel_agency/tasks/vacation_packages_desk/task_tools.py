"""Hidden task tools for the Wanderlane vacation packages desk (difficulty: vacation_packages_desk).

Each function lands exactly one atomic write on a vacation package that has already been worked
out from the published terms, the package record and the party's ledger. None of them aggregates
history, prices anything for the caller or judges whether the write is due: the money value is
worked out by whoever calls them and handed in as a fixed-format argument.
"""

from erlbench import ToolContext, tool


@tool(owner="agent", rw="write")
def charge_package_amendment_6b64f72d(ctx: ToolContext, bundle_package_id: str,
                                      amendment_charge_usd: float) -> str:
    """Enter, on a vacation package, the amendment charge the party owes for a change made to their
    booking. One call adds a single amendment-charge line to that package's ledger for the party as
    a whole, carrying the money charged, the calendar date it posted and the reason that the party's
    particulars were changed, and raises the net money standing against the package by that amount,
    so the party's package statement shows the amendment itemised alongside their deposit and
    instalments. The confirmation sentence quoting the new ledger line reference is what comes back
    on completion.

    Args:
        bundle_package_id: Id class — the internal reference number of the vacation package the
            amendment charge is being entered on, as carried on the package record returned by the
            vacation package lookup.
        amendment_charge_usd: Fixed-format class — the money charged to the party for the
            amendment, given as a USD amount with 2 decimal places, rounded half up to the cent,
            with no currency symbol, thousands separator or sign; it is always a positive money
            value.

    Returns:
        A plain confirmation sentence naming the new package ledger line reference, the package the
        charge was entered on and the amount in US dollars to two decimal places. That sentence,
        carrying a ledger line reference, is what indicates the charge was entered; no other value
        is returned.
    """
    owner = ctx.find("bundle_packages", bundle_package_id=bundle_package_id)
    customer_id = owner[0].get("customer_id") if owner else ""
    rid = ctx.make_id("bam_", bundle_package_id, amendment_charge_usd)
    ctx.create("bundle_ledger_entries", rid,
               bundle_entry_id=rid,
               bundle_package_id=bundle_package_id,
               customer_id=customer_id,
               event_type="bundle_penalty_charge",
               charge_category="amendment_fee",
               amount_usd=round(float(amendment_charge_usd), 2),
               currency_charged="USD",
               posted_date=ctx.now()[:10],
               posted_at=ctx.now(),
               traveller_sequence=0,
               room_sequence=0,
               component_sequence=0,
               instalment_sequence=0,
               payment_channel="call_centre",
               reason_code="party_amendment")
    return (f"Amendment charge of {round(float(amendment_charge_usd), 2):.2f} USD entered on package "
            f"{bundle_package_id} as ledger line {rid}.")


@tool(owner="user", rw="write")
def settle_package_instalment_b6602c09(ctx: ToolContext, bundle_package_id: str,
                                       instalment_amount_usd: float) -> str:
    """Pay the money now called on your own vacation package from the card the package was booked
    with. One call puts a single balance-payment line on that package's ledger for the amount you
    release, dated the day it is taken, and raises the net money standing to your package by that
    amount, so the outstanding figure on your package statement falls by the same amount. The
    confirmation sentence quoting the new ledger line reference is your receipt for the payment.

    Args:
        bundle_package_id: Id class — the internal reference number identifying which of your
            vacation packages the money is being paid against, as carried on the package record the
            desk reads out to you.
        instalment_amount_usd: Fixed-format class — the money you release on this occasion, given
            as a USD amount with 2 decimal places, rounded half up to the cent, with no currency
            symbol, thousands separator or sign; it is always a positive money value.

    Returns:
        A plain confirmation sentence naming the new package ledger line reference, the package paid
        against and the amount taken in US dollars to two decimal places. That sentence, carrying a
        ledger line reference, is what indicates the payment was taken; no other value is returned.
    """
    owner = ctx.find("bundle_packages", bundle_package_id=bundle_package_id)
    customer_id = owner[0].get("customer_id") if owner else ""
    rid = ctx.make_id("bpi_", bundle_package_id, instalment_amount_usd)
    ctx.create("bundle_ledger_entries", rid,
               bundle_entry_id=rid,
               bundle_package_id=bundle_package_id,
               customer_id=customer_id,
               event_type="bundle_final_payment_charge",
               charge_category="final_payment",
               amount_usd=round(float(instalment_amount_usd), 2),
               currency_charged="USD",
               posted_date=ctx.now()[:10],
               posted_at=ctx.now(),
               traveller_sequence=0,
               room_sequence=0,
               component_sequence=0,
               payment_channel="call_centre",
               reason_code="final_payment_due")
    return (f"Payment of {round(float(instalment_amount_usd), 2):.2f} USD taken on package "
            f"{bundle_package_id}; ledger line {rid} is your receipt.")


@tool(owner="agent", rw="write")
def withhold_cancellation_penalty_6c06e997(ctx: ToolContext, bundle_package_id: str,
                                           cancellation_penalty_usd: float) -> str:
    """Withhold, on a cancelled vacation package, the money the party forfeits for giving up their
    places. One call adds a single cancellation-penalty line to that package's ledger for the party as
    a whole, carrying the money withheld and the calendar date it posted, and raises the net money
    standing against the package by that amount so that it is no longer money the party can have back.
    The party's package statement then shows the forfeited sum itemised as a cancellation penalty. The
    confirmation sentence quoting the new ledger line reference is what comes back on completion.

    Args:
        bundle_package_id: Id class — the internal reference number of the cancelled vacation package
            the penalty is being withheld on, as carried on the package record returned by the
            vacation package lookup.
        cancellation_penalty_usd: Fixed-format class — the money withheld from the party, given as a
            USD amount with 2 decimal places, rounded half up to the cent, with no currency symbol,
            thousands separator or sign; it is always a positive money value.

    Returns:
        A plain confirmation sentence naming the new package ledger line reference, the package the
        penalty was withheld on and the amount in US dollars to two decimal places. That sentence,
        carrying a ledger line reference, is what indicates the penalty was withheld; no other value
        is returned.
    """
    owner = ctx.find("bundle_packages", bundle_package_id=bundle_package_id)
    customer_id = owner[0].get("customer_id") if owner else ""
    rid = ctx.make_id("bcp_", bundle_package_id, cancellation_penalty_usd)
    ctx.create("bundle_ledger_entries", rid,
               bundle_entry_id=rid,
               bundle_package_id=bundle_package_id,
               customer_id=customer_id,
               event_type="bundle_penalty_charge",
               charge_category="cancellation_penalty",
               amount_usd=round(float(cancellation_penalty_usd), 2),
               currency_charged="USD",
               posted_date=ctx.now()[:10],
               posted_at=ctx.now(),
               traveller_sequence=0,
               room_sequence=0,
               component_sequence=0,
               instalment_sequence=0,
               payment_channel="call_centre",
               reason_code="traveller_cancellation")
    return (f"Cancellation penalty of {round(float(cancellation_penalty_usd), 2):.2f} USD withheld on "
            f"package {bundle_package_id} as ledger line {rid}.")


@tool(owner="user", rw="write")
def release_package_refund_313c063d(ctx: ToolContext, bundle_package_id: str,
                                    refund_amount_usd: float) -> str:
    """Take back, to the card your vacation package was paid from, the money that package still owes
    you. One call puts a single payout line on that package's ledger for the amount you release,
    dated the day it is raised, and reduces the net money standing to your package by that amount, so
    your package statement shows the money leaving the package and coming back to you. The
    confirmation sentence quoting the new ledger line reference is your record of what was returned.

    Args:
        bundle_package_id: Id class — the internal reference number identifying which of your
            vacation packages the money is being returned from, as carried on the package record the
            desk reads out to you.
        refund_amount_usd: Fixed-format class — the money coming back to your card, given as a
            positive USD amount with 2 decimal places, rounded half up to the cent, with no currency
            symbol, thousands separator or sign; the payout line itself carries it as money leaving
            the package.

    Returns:
        A plain confirmation sentence naming the new package ledger line reference, the package the
        money was returned from and the amount in US dollars to two decimal places. That sentence,
        carrying a ledger line reference, is what indicates the money was released; no other value is
        returned.
    """
    owner = ctx.find("bundle_packages", bundle_package_id=bundle_package_id)
    customer_id = owner[0].get("customer_id") if owner else ""
    rid = ctx.make_id("brf_", bundle_package_id, refund_amount_usd)
    ctx.create("bundle_ledger_entries", rid,
               bundle_entry_id=rid,
               bundle_package_id=bundle_package_id,
               customer_id=customer_id,
               event_type="bundle_refund_payout",
               charge_category="refund_payout",
               amount_usd=-round(float(refund_amount_usd), 2),
               currency_charged="USD",
               posted_date=ctx.now()[:10],
               posted_at=ctx.now(),
               traveller_sequence=0,
               room_sequence=0,
               component_sequence=0,
               instalment_sequence=0,
               payment_channel="call_centre",
               reason_code="traveller_cancellation")
    return (f"Refund of {round(float(refund_amount_usd), 2):.2f} USD released on package "
            f"{bundle_package_id}; ledger line {rid} is your record.")

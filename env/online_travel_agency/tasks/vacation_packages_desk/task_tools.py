"""Hidden task tools for the vacation packages desk (scenario: online_travel_agency).

Each tool performs one atomic write on a vacation package or its ledger. None of them
aggregates history, prices anything, or judges whether the write ought to be made: the
figures they receive are worked out by the desk from the published package terms and the
records before the call is made.
"""

from erlbench import ToolContext, tool


@tool(owner="agent", rw="write")
def price_package_surcharge_8a2d0e07(ctx: ToolContext, bundle_package_id: str,
                                     surcharge_amount_usd: float, currency_charged: str,
                                     notice_reference: str) -> str:
    """Price an operator surcharge onto a vacation package so the party is billed for it.
    One call adds a single surcharge line to the named package's ledger for the amount given,
    in the currency the party is presented with, quoting the operator notice the charge answers.
    The line posts on the current business date, is charged against the party as a whole rather
    than any one traveller, and raises what the party owes on the package by that amount; the
    party sees the surcharge on the package statement from that moment. The reference of the
    new line comes back as confirmation that it posted.

    Args:
        bundle_package_id: Id class — the internal reference number of the vacation package the
            surcharge is billed to, read from the package record returned by the package lookup.
        surcharge_amount_usd: Fixed-format class — the amount billed to the party for the
            surcharge, expressed as a USD amount with 2 decimal places, rounded half up to the
            nearest cent, and never negative; it is the total for the whole party rather than a
            figure per traveller.
        currency_charged: Fixed-format class — the currency the party is presented with for this
            line, written as an ISO 4217 currency code, 3 uppercase letters, in upper case and
            with no spaces; it records presentation only and never converts the amount given.
        notice_reference: Verbatim class — the operator notice reference quoted on the notice this
            surcharge answers, taken from that notice line on the package ledger and copied
            character for character, keeping its original wording, digits and punctuation, with no
            translation, normalisation, summarisation, addition or deletion (verbatim).

    Returns:
        A one-line confirmation string. It contains the reference number of the ledger line
        created (a string beginning bnx_), the amount posted in US dollars to two decimal places,
        and the package reference number it was billed to. A string of this shape means the
        surcharge line is now standing on the package; any other outcome means nothing posted.
    """
    rid = ctx.make_id("bnx_", bundle_package_id, surcharge_amount_usd, currency_charged,
                      notice_reference)
    ctx.create("bundle_ledger_entries", rid, bundle_entry_id=rid,
               bundle_package_id=bundle_package_id,
               event_type="bundle_component_charge", charge_category="fuel_surcharge",
               amount_usd=round(float(surcharge_amount_usd), 2),
               currency_charged=currency_charged, posted_date=ctx.now()[:10],
               posted_at=ctx.now(), traveller_sequence=0, room_sequence=0,
               component_sequence=0, instalment_sequence=0, payment_channel="call_centre",
               notice_reference=notice_reference, reason_code="surcharge_notice")
    return (f"Surcharge line {rid} posted to package {bundle_package_id} for "
            f"{round(float(surcharge_amount_usd), 2)} USD.")


@tool(owner="user", rw="write")
def settle_package_balance_32304520(ctx: ToolContext, bundle_package_id: str,
                                    balance_due_usd: float, currency_charged: str,
                                    instalment_sequence: int) -> str:
    """Pay money toward the balance of your own vacation package. One call puts a single payment
    of the amount you give onto that package's ledger, in the currency you are presented with,
    recorded as the numbered instalment of the payment schedule it settles. The payment posts on
    the current business date, is credited to the package as a whole rather than to any one
    traveller, and reduces what is still outstanding on it by that amount; you see the payment on
    the package statement straight away. The reference of the new payment comes back as your
    receipt.

    Args:
        bundle_package_id: Id class — the internal reference number of the vacation package the
            money is paid toward, read from the package record returned by the package lookup.
        balance_due_usd: Fixed-format class — the amount paid, expressed as a USD amount with 2
            decimal places, rounded half up to the nearest cent, and never negative.
        currency_charged: Fixed-format class — the currency you are presented with for this
            payment, written as an ISO 4217 currency code, 3 uppercase letters, in upper case and
            with no spaces; it records presentation only and never converts the amount given.
        instalment_sequence: Fixed-format class — which numbered instalment of the package payment
            schedule this payment settles, as a whole number starting at 1, counted in the order
            the instalments fall due.

    Returns:
        A one-line receipt string. It contains the reference number of the payment line created
        (a string beginning bnp_), the amount paid in US dollars to two decimal places, and the
        package reference number it was credited to. A string of this shape means the payment is
        now standing on the package; any other outcome means nothing was taken.
    """
    rid = ctx.make_id("bnp_", bundle_package_id, balance_due_usd, currency_charged,
                      instalment_sequence)
    ctx.create("bundle_ledger_entries", rid, bundle_entry_id=rid,
               bundle_package_id=bundle_package_id,
               event_type="bundle_final_payment_charge", charge_category="final_payment",
               amount_usd=round(float(balance_due_usd), 2),
               currency_charged=currency_charged, posted_date=ctx.now()[:10],
               posted_at=ctx.now(), traveller_sequence=0, room_sequence=0,
               component_sequence=0, instalment_sequence=int(instalment_sequence),
               payment_channel="call_centre", reason_code="final_payment_due")
    return (f"Payment {rid} of {round(float(balance_due_usd), 2)} USD received toward package "
            f"{bundle_package_id}.")


@tool(owner="agent", rw="write")
def withhold_amendment_charge_5474525c(ctx: ToolContext, bundle_package_id: str,
                                       amendment_charge_usd: float, currency_charged: str,
                                       source_entry_id: str) -> str:
    """Withhold an amendment charge from a party against their vacation package. One call adds a
    single amendment charge line to the named package's ledger for the amount given, in the currency
    the party is presented with, and ties it to the payment line the charge is withheld against. The
    charge posts on the current business date, is raised against the party as a whole rather than
    any one traveller, and raises what the party has been charged on the package by that amount; the
    party sees the amendment charge on the package statement from that moment. The reference of the
    new line comes back as confirmation that it was withheld.

    Args:
        bundle_package_id: Id class — the internal reference number of the vacation package the
            amendment charge is raised against, read from the package record returned by the package
            lookup.
        amendment_charge_usd: Fixed-format class — the amount withheld from the party for the
            amendment, expressed as a USD amount with 2 decimal places, rounded half up to the
            nearest cent, and never negative; it is the total for the whole party rather than a
            figure per traveller.
        currency_charged: Fixed-format class — the currency the party is presented with for this
            charge, written as an ISO 4217 currency code, 3 uppercase letters, in upper case and
            with no spaces; it records presentation only and never converts the amount given.
        source_entry_id: Id class — the reference number of the payment line already standing on the
            package that this charge is withheld against, read from the ledger lookup for that
            package.

    Returns:
        A one-line confirmation string. It contains the reference number of the ledger line created
        (a string beginning bna_), the amount withheld in US dollars to two decimal places, and the
        package reference number it was raised against. A string of this shape means the amendment
        charge is now standing on the package; any other outcome means nothing was withheld.
    """
    rid = ctx.make_id("bna_", bundle_package_id, amendment_charge_usd, currency_charged,
                      source_entry_id)
    ctx.create("bundle_ledger_entries", rid, bundle_entry_id=rid,
               bundle_package_id=bundle_package_id,
               event_type="bundle_penalty_charge", charge_category="amendment_fee",
               amount_usd=round(float(amendment_charge_usd), 2),
               currency_charged=currency_charged, posted_date=ctx.now()[:10],
               posted_at=ctx.now(), traveller_sequence=0, room_sequence=0,
               component_sequence=0, instalment_sequence=0, payment_channel="call_centre",
               source_entry_id=source_entry_id, reason_code="party_amendment")
    return (f"Amendment charge {rid} of {round(float(amendment_charge_usd), 2)} USD withheld on "
            f"package {bundle_package_id}.")


@tool(owner="user", rw="write")
def confirm_places_given_up_9aa48f75(ctx: ToolContext, bundle_package_id: str,
                                     bundle_request_id: str, remaining_adults: int,
                                     remaining_children: int,
                                     revised_package_price_usd: float) -> str:
    """Give up places on your own vacation package and set the booking to the party that is actually
    travelling. One call rewrites the named package's record to show the adults and the children who
    remain and the price the package now carries for them, quoting the operations desk request the
    change answers. Afterwards the booking shows the smaller party and the new price, and everything
    the operator does for the rest of the holiday is done for that party; nothing else on the booking
    moves. A confirmation naming the package and the party now travelling comes back as your receipt.

    Args:
        bundle_package_id: Id class — the internal reference number of the vacation package the
            places are given up on, read from the package record returned by the package lookup.
        bundle_request_id: Id class — the reference number of the change request the operations desk
            has recorded for this package, read from the change request lookup.
        remaining_adults: Fixed-format class — how many adults are still travelling once the places
            are given up, as a whole number of adults, at least 1, counted as heads and not as
            fares.
        remaining_children: Fixed-format class — how many children are still travelling once the
            places are given up, as a whole number of children, zero or more, counted as heads and
            not as fares.
        revised_package_price_usd: Fixed-format class — the price the package carries for the party
            now travelling, expressed as a USD amount with 2 decimal places, rounded half up to the
            nearest cent, and never negative.

    Returns:
        A one-line receipt string. It contains the package reference number, the adults and children
        now shown on the booking, and the price the package now carries in US dollars to two decimal
        places. A string of this shape means the booking has been rewritten; any other outcome means
        the party and the price are unchanged.
    """
    ctx.update("bundle_packages", bundle_package_id,
               party_adults=int(remaining_adults), party_children=int(remaining_children),
               package_price_usd=round(float(revised_package_price_usd), 2))
    return (f"Package {bundle_package_id} now shows {int(remaining_adults)} adult(s) and "
            f"{int(remaining_children)} child(ren) at {round(float(revised_package_price_usd), 2)} "
            f"USD, against request {bundle_request_id}.")

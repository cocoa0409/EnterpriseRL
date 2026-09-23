"""Hidden task tools for the Belrose upgrade desk (trade_up_desk).

Each function performs one atomic write on the trade-in register or its entry ledger.
None of them weighs a policy condition, aggregates history or works a figure out for the
caller: the amounts arrive already reasoned out, and the tool simply lands the entry.
"""

from erlbench import ToolContext, tool


@tool(owner="agent", rw="write")
def apply_credit_revaluation_37908854(ctx: ToolContext, credit_reference: str,
                                      revaluation_amount: float, appraiser_code: str,
                                      source_entry_id: str) -> str:
    """Book an upward revaluation of an upgrade credit onto the trade-in registration it belongs to.

    One call adds a single revaluation entry to the registration's running entries and raises the
    credit available to spend on that registration by the same figure. The entry is stamped with the
    appraiser who revalued the piece, points back at the credit entry it revalues, and is dated the
    day it is booked. After the call the registration shows a larger credit still available to spend,
    and the new entry stands in the registration's history alongside the original credit.

    Args:
        credit_reference: Id class — the reference number of the trade-in registration whose credit
            is being revalued, written on the customer's upgrade paperwork as TU- followed by six
            digits; read it from the trade-in registration lookup.
        revaluation_amount: Fixed-format class — the increase in credit being booked, in USD to 2
            decimal places, always a positive figure, given as a plain number with no currency
            symbol and no thousands separator; the tool stores it rounded to 2 decimal places by
            half-up arithmetic at the moment of the call.
        appraiser_code: Fixed-format class — the appraiser who revalued the piece, written as APR-
            followed by three digits, e.g. APR-042, in upper case with the hyphen kept and no
            spaces; it is never left empty on a revaluation and is read from the appraisal
            engagement the revaluation rests on.
        source_entry_id: Id class — the reference number of the earlier entry on this registration
            that booked the credit now being revalued; read it from the registration's entry history.

    Returns:
        A one-line confirmation string naming the registration reference, the reference number of the
        revaluation entry just created, the increase booked in USD to 2 decimal places and the credit
        now available to spend in USD to 2 decimal places. A string beginning "Error" means nothing
        was written; any other string means the entry stands and the registration has been raised.
    """
    rows = ctx.find("tradein_credits", credit_reference=credit_reference)
    if not rows:
        return f"Error: no trade-in registration {credit_reference}."
    reg = rows[0]
    amount = round(float(revaluation_amount), 2)
    rid = ctx.make_id("tie_", credit_reference, amount, appraiser_code, source_entry_id)
    posted = ctx.now()[:10]
    ctx.create("tradein_ledger", rid, tradein_entry_id=rid,
               tradein_credit_id=reg["tradein_credit_id"], customer_id=reg["customer_id"],
               event_type="tradein_credit_revaluation_applied", posted_date=posted,
               amount=amount, valuation_basis="current_market_appraisal",
               condition_grade="not_applicable", appraiser_code=appraiser_code,
               redemption_receipt_number="", redeemed_item_sku="", certificate_number="",
               forfeit_reason_code="not_applicable", billing_period=posted[:7],
               source_entry_id=source_entry_id)
    remaining = round(float(reg.get("remaining_credit") or 0) + amount, 2)
    ctx.update("tradein_credits", reg["tradein_credit_id"], remaining_credit=remaining)
    return (f"Registration {credit_reference}: revaluation entry {rid} booked for {amount:.2f} USD; "
            f"credit now available to spend {remaining:.2f} USD.")


@tool(owner="agent", rw="write")
def update_upgrade_minimum_spend_70148cfb(ctx: ToolContext, credit_reference: str,
                                          upgrade_minimum_spend: float) -> str:
    """Record on a trade-in registration the least the customer must spend for its credit to be usable.

    One call replaces the figure printed on that registration as the smallest amount a new piece may
    cost for the credit standing on it to be put toward that piece. Nothing else on the
    registration moves: the credit available, the status and the dates are left exactly as they were.
    Afterwards the registration, and the paperwork the customer is shown, carry the new figure.

    Args:
        credit_reference: Id class — the reference number of the trade-in registration being
            corrected, written on the customer's upgrade paperwork as TU- followed by six digits;
            read it from the trade-in registration lookup.
        upgrade_minimum_spend: Fixed-format class — the smallest price a new piece may carry for this
            registration's credit to be spendable against it, in USD to 2 decimal places, a plain
            positive number with no currency symbol and no thousands separator; the tool stores it
            rounded to 2 decimal places by half-up arithmetic at the moment of the call.

    Returns:
        A one-line confirmation string naming the registration reference and the least the customer
        must spend as it now stands, in USD to 2 decimal places. A string beginning "Error" means
        nothing was written; any other string means the registration now carries that figure.
    """
    rows = ctx.find("tradein_credits", credit_reference=credit_reference)
    if not rows:
        return f"Error: no trade-in registration {credit_reference}."
    reg = rows[0]
    figure = round(float(upgrade_minimum_spend), 2)
    ctx.update("tradein_credits", reg["tradein_credit_id"], upgrade_minimum_spend=figure)
    return (f"Registration {credit_reference}: the least the customer must spend now reads "
            f"{figure:.2f} USD.")


@tool(owner="user", rw="write")
def spend_upgrade_credit_c2e2bb76(ctx: ToolContext, credit_reference: str,
                                  credit_applied_amount: float,
                                  redemption_receipt_number: str,
                                  redeemed_item_sku: str) -> str:
    """Put upgrade credit toward a new piece, as the customer whose credit it is.

    One call spends the stated amount of the credit standing on a trade-in registration against one
    till transaction and one merchandise line on it. It adds a spend entry to the registration's
    running entries, lowers the credit still available by that amount, records the till transaction
    the credit went to, and moves the registration to part spent, or to fully spent where nothing is
    left. The customer sees that much taken off the new piece at the till and the rest of the credit,
    if any, still standing on their registration.

    Args:
        credit_reference: Id class — the reference number of the trade-in registration the credit is
            being spent from, written on the customer's upgrade paperwork as TU- followed by six
            digits; read it from the trade-in registration lookup.
        credit_applied_amount: Fixed-format class — how much credit is being put toward the new
            piece, in USD to 2 decimal places, a plain positive number with no currency symbol and no
            thousands separator; the tool stores it rounded to 2 decimal places by half-up arithmetic
            at the moment of the call and books it as a reduction of the credit.
        redemption_receipt_number: Fixed-format class — the till transaction the credit is being put
            toward, written as BR- followed by a four-digit year, a hyphen and six digits, e.g.
            BR-2025-118406; it is taken from the paperwork for the new sale.
        redeemed_item_sku: Fixed-format class — the merchandise line on that till transaction the
            credit is applied to, written as four letters, a hyphen and five digits, e.g. RING-40218;
            it is taken from the paperwork for the new sale.

    Returns:
        A one-line confirmation string naming the registration reference, the reference number of the
        spend entry just created, the credit put toward the new piece in USD to 2 decimal places, the
        credit still available afterwards in USD to 2 decimal places and the registration's standing
        after the spend. A string beginning "Error" means nothing was written; any other string means
        the credit has been applied to that till transaction.
    """
    rows = ctx.find("tradein_credits", credit_reference=credit_reference)
    if not rows:
        return f"Error: no trade-in registration {credit_reference}."
    reg = rows[0]
    applied = round(float(credit_applied_amount), 2)
    rid = ctx.make_id("tie_", credit_reference, applied, redemption_receipt_number, redeemed_item_sku)
    posted = ctx.now()[:10]
    ctx.create("tradein_ledger", rid, tradein_entry_id=rid,
               tradein_credit_id=reg["tradein_credit_id"], customer_id=reg["customer_id"],
               event_type="tradein_credit_redeemed", posted_date=posted, amount=-applied,
               valuation_basis="not_applicable", condition_grade="not_applicable",
               appraiser_code="", redemption_receipt_number=redemption_receipt_number,
               redeemed_item_sku=redeemed_item_sku, certificate_number="",
               forfeit_reason_code="not_applicable", billing_period=posted[:7], source_entry_id="")
    remaining = round(float(reg.get("remaining_credit") or 0) - applied, 2)
    standing = "redeemed" if remaining <= 0 else "partially_redeemed"
    fields = {"remaining_credit": remaining, "status": standing,
              "redemption_receipt_number": redemption_receipt_number}
    if standing == "redeemed":
        fields["closed_date"] = posted
    ctx.update("tradein_credits", reg["tradein_credit_id"], **fields)
    return (f"Registration {credit_reference}: spend entry {rid} applied {applied:.2f} USD to till "
            f"transaction {redemption_receipt_number}; credit still available {remaining:.2f} USD; "
            f"registration now {standing}.")


@tool(owner="agent", rw="write")
def log_item_valuation_6ae79dd2(ctx: ToolContext, credit_reference: str, valuation_amount: float,
                                appraiser_code: str, valuation_basis: str) -> str:
    """Record the appraiser's valuation of a traded piece against the trade-in registration it was taken in on.

    One call adds a single valuation entry to that registration's running entries, carrying the figure the
    piece was valued at, the appraiser who arrived at it, the basis it was struck on and the certificate
    standing on the registration, dated the day it is recorded. Nothing about the registration's own
    standing moves: the valuation is a record of what the piece is worth, and what the customer is
    offered for it is settled separately. Afterwards the registration's history shows the valuation and
    the figure it names.

    Args:
        credit_reference: Id class — the reference number of the trade-in registration the piece was
            taken in on, written on the customer's upgrade paperwork as TU- followed by six digits; read
            it from the trade-in registration lookup.
        valuation_amount: Fixed-format class — the figure the piece is valued at, in USD to 2 decimal
            places, a plain positive number with no currency symbol and no thousands separator; the tool
            stores it rounded to 2 decimal places by half-up arithmetic at the moment of the call.
        appraiser_code: Fixed-format class — the appraiser who arrived at the figure, written as APR-
            followed by three digits, e.g. APR-042, in upper case with the hyphen kept and no spaces; it
            is never left empty on a valuation and is read from the appraisal engagement it was made on.
        valuation_basis: Enum class — which basis the figure was struck on, one of exactly these five
            values. original_purchase_price applies where the figure is the price the piece itself
            originally sold for. current_market_appraisal applies where it is what the piece would fetch
            today, as an appraisal of its market value states. certified_lab_value applies where it is
            the value a laboratory's own grading report states for the stone. published_scrap_rate
            applies where the piece is valued for its metal content at the published rate rather than as
            a piece of jewellery. not_applicable applies where the entry values nothing at all.

    Returns:
        A one-line confirmation string naming the registration reference, the reference number of the
        valuation entry just created, the figure recorded in USD to 2 decimal places and the basis it was
        struck on. A string beginning "Error" means nothing was written; any other string means the
        valuation entry stands in the registration's history.
    """
    rows = ctx.find("tradein_credits", credit_reference=credit_reference)
    if not rows:
        return f"Error: no trade-in registration {credit_reference}."
    reg = rows[0]
    amount = round(float(valuation_amount), 2)
    rid = ctx.make_id("tie_", credit_reference, amount, appraiser_code, valuation_basis)
    posted = ctx.now()[:10]
    ctx.create("tradein_ledger", rid, tradein_entry_id=rid,
               tradein_credit_id=reg["tradein_credit_id"], customer_id=reg["customer_id"],
               event_type="tradein_item_valuation_logged", posted_date=posted, amount=amount,
               valuation_basis=valuation_basis, condition_grade="not_applicable",
               appraiser_code=appraiser_code, redemption_receipt_number="", redeemed_item_sku="",
               certificate_number=reg.get("certificate_number") or "",
               forfeit_reason_code="not_applicable", billing_period=posted[:7], source_entry_id="")
    return (f"Registration {credit_reference}: valuation entry {rid} recorded at {amount:.2f} USD on the "
            f"{valuation_basis} basis.")


@tool(owner="agent", rw="write")
def issue_upgrade_credit_f63e5226(ctx: ToolContext, credit_reference: str,
                                  issued_credit_amount: float, appraised_value: float) -> str:
    """Issue the upgrade credit on a trade-in registration that has been waiting on its valuation.

    One call moves the registration from waiting on a valuation to credit issued, writes the credit it is
    issued with and the value the piece was appraised at for it, makes the whole of that credit available
    to spend, dates the issue on the day of the call, and books the credit as a matching entry in the
    registration's running entries. Afterwards the
    customer has a credit they can put toward a new piece, and the registration and its entries agree on
    what that credit is.

    Args:
        credit_reference: Id class — the reference number of the trade-in registration the credit is
            issued on, written on the customer's upgrade paperwork as TU- followed by six digits; read it
            from the trade-in registration lookup.
        issued_credit_amount: Fixed-format class — the credit being issued against the traded piece, in
            USD to 2 decimal places, a plain positive number with no currency symbol and no thousands
            separator; the tool stores it rounded to 2 decimal places by half-up arithmetic at the moment
            of the call and makes the same figure available to spend.
        appraised_value: Fixed-format class — the value the traded piece was appraised at, as recorded
            against the registration and now written onto it, in USD to 2 decimal places, a plain positive
            number with no currency symbol and no thousands separator; the tool stores it rounded to 2
            decimal places by half-up arithmetic at the moment of the call.

    Returns:
        A one-line confirmation string naming the registration reference, the credit issued in USD to 2
        decimal places, the appraised value written onto the registration in USD to 2 decimal places, the
        reference number of the credit entry just booked and the registration's
        standing afterwards. A string beginning "Error" means nothing was written; any other string means
        the credit is issued and available to spend.
    """
    rows = ctx.find("tradein_credits", credit_reference=credit_reference)
    if not rows:
        return f"Error: no trade-in registration {credit_reference}."
    reg = rows[0]
    amount = round(float(issued_credit_amount), 2)
    appraised = round(float(appraised_value), 2)
    posted = ctx.now()[:10]
    rid = ctx.make_id("tie_", credit_reference, amount, appraised, "issue")
    ctx.update("tradein_credits", reg["tradein_credit_id"], status="credit_issued",
               issued_credit_amount=amount, remaining_credit=amount, issued_date=posted,
               appraised_value=appraised)
    ctx.create("tradein_ledger", rid, tradein_entry_id=rid,
               tradein_credit_id=reg["tradein_credit_id"], customer_id=reg["customer_id"],
               event_type="tradein_credit_granted", posted_date=posted, amount=amount,
               valuation_basis="current_market_appraisal", condition_grade="not_applicable",
               appraiser_code="", redemption_receipt_number="", redeemed_item_sku="",
               certificate_number=reg.get("certificate_number") or "",
               forfeit_reason_code="not_applicable", billing_period=posted[:7], source_entry_id="")
    return (f"Registration {credit_reference}: credit of {amount:.2f} USD issued against an appraised value of "
            f"{appraised:.2f} USD and booked as entry {rid}; the registration now stands at credit issued "
            f"with {amount:.2f} USD available to spend.")


@tool(owner="user", rw="write")
def confirm_custody_declaration_bb764f94(ctx: ToolContext, credit_reference: str,
                                         declared_custody_value: float,
                                         appraisal_reference: str) -> str:
    """Put the value on record that you, the customer, are handing your piece over at, and name the appraisal it rests on.

    One call takes your confirmed declaration onto the upgrade desk's request record for that trade-in
    registration, carrying the value you are putting the piece in at while it is in the chain's care, and
    writes onto the registration itself the appraisal the declaration rests on. The request stands as
    confirmed by you from the moment of the call, and the desk can see both the figure you declared and
    the appraisal behind it.

    Args:
        credit_reference: Id class — the reference number of the trade-in registration your piece was
            taken in on, written on your upgrade paperwork as TU- followed by six digits; the desk reads
            it from the registration lookup.
        declared_custody_value: Fixed-format class — the value you are putting the piece in at, in USD to
            2 decimal places, a plain positive number with no currency symbol and no thousands separator;
            the tool stores it rounded to 2 decimal places by half-up arithmetic at the moment of the call.
        appraisal_reference: Fixed-format class — the appraisal the declaration rests on, written as AP-
            followed by six digits, e.g. AP-660412, in upper case with the hyphen kept and no spaces; it
            is taken from the appraisal engagement carried out on the piece.

    Returns:
        A one-line confirmation string naming the registration reference, the reference number of the
        request record just taken, the value declared in USD to 2 decimal places and the appraisal it
        rests on. A string beginning "Error" means nothing was written; any other string means your
        declaration stands confirmed on the record.
    """
    rows = ctx.find("tradein_credits", credit_reference=credit_reference)
    if not rows:
        return f"Error: no trade-in registration {credit_reference}."
    reg = rows[0]
    value = round(float(declared_custody_value), 2)
    rid = ctx.make_id("tir_", credit_reference, value, appraisal_reference)
    ctx.create("tradein_intake", rid, tradein_request_id=rid, customer_id=reg["customer_id"],
               tradein_credit_id=reg["tradein_credit_id"], request_type="valuation_booking",
               request_status="customer_confirmed", requested_amount=value,
               effective_date=ctx.now()[:10], created_at=ctx.now())
    ctx.update("tradein_credits", reg["tradein_credit_id"], appraisal_reference=appraisal_reference)
    return (f"Registration {credit_reference}: request record {rid} confirmed, declaring the piece at "
            f"{value:.2f} USD and resting on appraisal {appraisal_reference}.")

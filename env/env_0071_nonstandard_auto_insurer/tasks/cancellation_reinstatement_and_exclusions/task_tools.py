"""Hidden task tools for env_0071_nonstandard_auto_insurer / cancellation_reinstatement_and_exclusions.

Category: auto (Owner Auto Policy). Every tool performs one atomic business write on an Owner Auto
Policy term with the values the caller has already worked out; no tool checks a business
precondition, aggregates history or computes a policy amount.
"""

from erlbench import ToolContext, tool


@tool(owner="agent", rw="write")
def cancel_term_for_nonpayment_77de57b0(ctx: ToolContext, auto_policy_id: str, closed_date: str,
                                        return_premium: float, returned_days: int) -> str:
    """Cancel an Owner Auto Policy term for nonpayment of premium and book the premium returned on it.

    The desk uses this on one policy term whose notice of cancellation for nonpayment has run out.
    One call sets the term's status to cancelled with cancellation reason nonpayment and the given
    closed date, books one return premium transaction on the term when the amount is above zero (transaction reason
    cancellation_nonpayment, effective on the closed date, carrying the amount and the number of days
    returned; a 0.00 return is not booked), and lowers the term's net written premium by that amount. Once the call completes, the term shows
    as cancelled for nonpayment and the return premium appears among the term's premium and fee
    transactions.

    Args:
        auto_policy_id: Id class — the reference number of the Owner Auto Policy term being cancelled, read from the policy term lookup.
        closed_date: Fixed-format class — the date coverage under the term ended (the cancellation effective date stated on the notice), written YYYY-MM-DD.
        return_premium: Fixed-format class — the premium returned on the cancellation, in USD, 2 decimal places, rounded half up to the cent; 0.00 or more, a 0.00 amount booking no premium transaction.
        returned_days: Fixed-format class — the number of days of the term the returned premium covers, an integer >= 0, calendar days.

    Returns:
        A confirmation sentence (string) naming the term reference number, the new status cancelled,
        the closed date (YYYY-MM-DD), the booked return premium transaction reference number, its
        amount in USD with 2 decimal places and its returned days; the presence of the transaction
        reference number means the cancellation and the return premium were recorded.
    """
    rows = ctx.find("auto_policies", auto_policy_id=auto_policy_id)
    term = rows[0] if rows else {}
    amount = round(float(return_premium), 2)
    days = int(returned_days)
    txn_id = ctx.make_id("apt_", auto_policy_id, "cancellation_nonpayment", closed_date, amount, days)
    ctx.update("auto_policies", auto_policy_id, status="cancelled", cancellation_reason="nonpayment",
               closed_date=closed_date,
               term_written_premium=round(float(term.get("term_written_premium") or 0) - amount, 2))
    if amount > 0:
        ctx.create("auto_premium_transactions", txn_id, auto_premium_txn_id=txn_id, auto_policy_id=auto_policy_id,
                   customer_id=term.get("customer_id", ""), event_type="auto_return_premium",
                   transaction_date=ctx.now()[:10], effective_date=closed_date, amount=amount,
                   transaction_reason="cancellation_nonpayment", premium_days=days,
                   source_change_id="", reversed_txn_id="")
    return (f"Term {auto_policy_id} is now cancelled for nonpayment, closed {closed_date}; return premium "
            f"transaction {txn_id} booked for {amount:.2f} USD covering {days} days.")


@tool(owner="agent", rw="write")
def reinstate_lapsed_term_12128c9a(ctx: ToolContext, auto_policy_id: str, auto_document_id: str, reinstatement_date: str,
                                   lapse_start_date: str, lapse_end_date: str, rewritten_premium: float,
                                   rewritten_days: int, reinstatement_fee: float) -> str:
    """Reinstate an Owner Auto Policy term cancelled for nonpayment with a lapse in coverage.

    One call puts the cancelled term back in force as a reinstatement with lapse: the term's status
    becomes in_force, the reinstatement date, the reinstatement type with_lapse and the first and last
    days of the lapse are recorded, and the closed date is cleared. It books one additional premium
    transaction on the term when the re-written amount is above zero (transaction reason reinstatement, effective on the reinstatement date,
    carrying the re-written amount and the days it covers) and one reinstatement fee transaction
    (effective on the reinstatement date), and raises the term's net written premium and net fees by
    those amounts. Once the call completes, the term shows in force with its lapse dates, and both transactions
    appear among its premium and fee transactions.

    Args:
        auto_policy_id: Id class — the reference number of the Owner Auto Policy term being reinstated, read from the policy term lookup.
        auto_document_id: Id class — the reference number of the signed Statement of No Loss the reinstatement rests on, read from the lookup of the term's notices and signed forms; it is quoted on the reinstatement receipt and identifies the transactions it books.
        reinstatement_date: Fixed-format class — the date coverage resumes at 12:01 a.m., written YYYY-MM-DD.
        lapse_start_date: Fixed-format class — the first day without coverage in the lapse, written YYYY-MM-DD.
        lapse_end_date: Fixed-format class — the last day without coverage in the lapse, written YYYY-MM-DD.
        rewritten_premium: Fixed-format class — the premium re-written on the reinstatement, in USD, 2 decimal places, rounded half up to the cent; 0.00 or more, a 0.00 amount booking no premium transaction.
        rewritten_days: Fixed-format class — the number of days of the term the re-written premium covers, an integer >= 0, calendar days.
        reinstatement_fee: Fixed-format class — the fully earned reinstatement fee charged, in USD, 2 decimal places.

    Returns:
        A confirmation sentence (string) naming the term reference number, the new status in_force,
        the Statement of No Loss reference number, the reinstatement date and the lapse dates (YYYY-MM-DD), the additional premium transaction
        reference number with its amount in USD with 2 decimal places and its days, and the
        reinstatement fee transaction reference number with its amount; the presence of both
        transaction reference numbers means the reinstatement was recorded.
    """
    rows = ctx.find("auto_policies", auto_policy_id=auto_policy_id)
    term = rows[0] if rows else {}
    amount = round(float(rewritten_premium), 2)
    days = int(rewritten_days)
    fee = round(float(reinstatement_fee), 2)
    prem_id = ctx.make_id("apt_", auto_policy_id, auto_document_id, "reinstatement_premium", reinstatement_date, amount, days,
                          lapse_start_date, lapse_end_date)
    fee_id = ctx.make_id("apt_", auto_policy_id, auto_document_id, "reinstatement_fee", reinstatement_date, fee)
    ctx.update("auto_policies", auto_policy_id, status="in_force", reinstatement_date=reinstatement_date,
               reinstatement_type="with_lapse", lapse_start_date=lapse_start_date, lapse_end_date=lapse_end_date,
               closed_date="",
               term_written_premium=round(float(term.get("term_written_premium") or 0) + amount, 2),
               term_fees_charged=round(float(term.get("term_fees_charged") or 0) + fee, 2))
    if amount > 0:
        ctx.create("auto_premium_transactions", prem_id, auto_premium_txn_id=prem_id, auto_policy_id=auto_policy_id,
                   customer_id=term.get("customer_id", ""), event_type="auto_additional_premium",
                   transaction_date=ctx.now()[:10], effective_date=reinstatement_date, amount=amount,
                   transaction_reason="reinstatement", premium_days=days, source_change_id="", reversed_txn_id="")
    ctx.create("auto_premium_transactions", fee_id, auto_premium_txn_id=fee_id, auto_policy_id=auto_policy_id,
               customer_id=term.get("customer_id", ""), event_type="auto_reinstatement_fee",
               transaction_date=ctx.now()[:10], effective_date=reinstatement_date, amount=fee,
               transaction_reason="reinstatement", premium_days=0, source_change_id="", reversed_txn_id="")
    return (f"Term {auto_policy_id} is in_force again from {reinstatement_date} on Statement of No Loss {auto_document_id} "
            f"(lapse {lapse_start_date} to "
            f"{lapse_end_date}); additional premium transaction {prem_id} for {amount:.2f} USD covering {days} days "
            f"and reinstatement fee transaction {fee_id} for {fee:.2f} USD booked.")


@tool(owner="user", rw="write")
def confirm_cancellation_request_98c044dc(ctx: ToolContext, auto_cancel_request_id: str, auto_policy_id: str,
                                          cancellation_effective_date: str, return_premium: float,
                                          returned_days: int) -> str:
    """Sign and confirm your own request to cancel your Owner Auto Policy term, so that the cancellation takes effect.

    The named insured uses this personally on a cancellation request already registered for the
    term. One call marks the request confirmed_by_insured, sets the term's status to cancelled with
    cancellation reason insured_request, records the given cancellation effective date as both the
    cancellation effective date and the closed date, books one return premium transaction on the term
    when the amount is above zero (transaction reason cancellation_insured_request, effective on that date, carrying the amount and
    the days returned), and lowers the term's net written premium by that amount. Once the call completes, the
    request shows as confirmed and the term as cancelled at the insured's request.

    Args:
        auto_cancel_request_id: Id class — the reference number of the registered cancellation request being signed, given to you by the representative from the cancellation request lookup.
        auto_policy_id: Id class — the reference number of the Owner Auto Policy term the request cancels, given to you by the representative from the policy term lookup.
        cancellation_effective_date: Fixed-format class — the date the cancellation takes effect at 12:01 a.m., written YYYY-MM-DD, as the representative states it.
        return_premium: Fixed-format class — the premium returned on the cancellation as the representative states it, in USD, 2 decimal places, rounded half up to the cent.
        returned_days: Fixed-format class — the number of days of the term the returned premium covers as the representative states it, an integer >= 0, calendar days.

    Returns:
        A confirmation sentence (string) naming the request reference number now confirmed, the term
        reference number now cancelled at your request, the cancellation effective date (YYYY-MM-DD),
        and the return premium transaction reference number with its amount in USD with 2 decimal
        places and its days; the presence of the transaction reference number means the cancellation
        took effect.
    """
    rows = ctx.find("auto_policies", auto_policy_id=auto_policy_id)
    term = rows[0] if rows else {}
    amount = round(float(return_premium), 2)
    days = int(returned_days)
    txn_id = ctx.make_id("apt_", auto_policy_id, "cancellation_insured_request", cancellation_effective_date,
                         auto_cancel_request_id, amount, days)
    ctx.update("auto_cancellation_requests", auto_cancel_request_id, request_status="confirmed_by_insured")
    ctx.update("auto_policies", auto_policy_id, status="cancelled", cancellation_reason="insured_request",
               cancellation_effective_date=cancellation_effective_date, closed_date=cancellation_effective_date,
               term_written_premium=round(float(term.get("term_written_premium") or 0) - amount, 2))
    if amount > 0:
        ctx.create("auto_premium_transactions", txn_id, auto_premium_txn_id=txn_id, auto_policy_id=auto_policy_id,
                   customer_id=term.get("customer_id", ""), event_type="auto_return_premium",
                   transaction_date=ctx.now()[:10], effective_date=cancellation_effective_date, amount=amount,
                   transaction_reason="cancellation_insured_request", premium_days=days,
                   source_change_id="", reversed_txn_id="")
    return (f"Request {auto_cancel_request_id} confirmed; term {auto_policy_id} cancelled at your request effective "
            f"{cancellation_effective_date}; return premium transaction {txn_id} booked for {amount:.2f} USD "
            f"covering {days} days.")


class _DriverEntries:
    """Carries a driver's date of birth, relationship and points from the driver's most recent entry."""

    @staticmethod
    def latest(rows: list) -> dict:
        ordered = sorted(rows, key=lambda r: str(r.get("change_effective_date") or ""))
        return ordered[-1] if ordered else {}


@tool(owner="agent", rw="write")
def exclude_reported_resident_5c3e91a4(ctx: ToolContext, auto_policy_id: str, signed_form_id: str, driver_name: str,
                                       listing_effective_date: str, change_effective_date: str,
                                       driver_term_premium: float, listing_premium: float, listing_days: int) -> str:
    """Endorse a named driver exclusion for a household resident reported operating while unlisted, rating the resident for the listing period first.

    The desk uses this for one household member named on a Named Driver Exclusion form the named
    insured has signed. One call records two changes on the term: a driver-added change (prior driver
    status unlisted, effective on the given listing date, with the given full-term premium share) and
    a driver-excluded change (prior driver status rated, effective on the given exclusion date, with
    the same share and the signed form it rests on), both carrying the driver's date of birth,
    relationship and violation points from that driver's most recent entry on the term. When the
    listing premium is above zero it books one additional premium transaction (transaction reason
    driver_added, effective on the listing date, carrying the amount and days charged, linked to the
    driver-added change) and raises the term's net written premium by that amount; a 0.00 listing
    premium books no premium transaction. Once the call completes, the driver shows as a named excluded
    driver on the term.

    Args:
        auto_policy_id: Id class — the reference number of the Owner Auto Policy term, read from the policy term lookup.
        signed_form_id: Id class — the reference number of the signed Named Driver Exclusion form the exclusion rests on, read from the lookup of the term's notices and signed forms.
        driver_name: Verbatim class — the excluded driver's full name copied character for character from the signed Named Driver Exclusion form, with no change in spelling, order or punctuation (verbatim).
        listing_effective_date: Fixed-format class — the date the resident's listing as a rated driver takes effect at 12:01 a.m., written YYYY-MM-DD.
        change_effective_date: Fixed-format class — the date the exclusion takes effect at 12:01 a.m., written YYYY-MM-DD.
        driver_term_premium: Fixed-format class — the full-term premium share the rating attributes to the resident as a rated driver, in USD, 2 decimal places.
        listing_premium: Fixed-format class — the premium charged for the listing period, in USD, 2 decimal places, rounded half up to the cent; 0.00 or more, a 0.00 amount booking no premium transaction.
        listing_days: Fixed-format class — the number of days of the term the listing premium covers, an integer >= 0, calendar days.

    Returns:
        A confirmation sentence (string) naming the driver now excluded, the term reference number, the
        driver-added and driver-excluded change reference numbers with their effective dates
        (YYYY-MM-DD), and the additional premium transaction reference number with its amount in USD
        with 2 decimal places and its days; the presence of both change reference numbers means the
        listing and the exclusion were recorded.
    """
    prior = _DriverEntries.latest(ctx.find("auto_policy_changes", auto_policy_id=auto_policy_id, driver_name=driver_name))
    rows = ctx.find("auto_policies", auto_policy_id=auto_policy_id)
    term = rows[0] if rows else {}
    share = round(float(driver_term_premium), 2)
    amount = round(float(listing_premium), 2)
    days = int(listing_days)
    add_id = ctx.make_id("apc_", auto_policy_id, signed_form_id, driver_name, "listing", listing_effective_date, share)
    exc_id = ctx.make_id("apc_", auto_policy_id, signed_form_id, driver_name, "exclusion", change_effective_date, share)
    txn_id = ctx.make_id("apt_", add_id, "driver_added", amount, days)
    ctx.create("auto_policy_changes", add_id, auto_change_id=add_id, auto_policy_id=auto_policy_id,
               customer_id=term.get("customer_id", ""), event_type="auto_driver_added",
               change_effective_date=listing_effective_date, driver_name=driver_name,
               driver_date_of_birth=prior.get("driver_date_of_birth", ""),
               driver_relationship=prior.get("driver_relationship", ""), prior_driver_status="unlisted",
               driver_violation_points=prior.get("driver_violation_points", 0), driver_term_premium=share,
               vehicle_vin="", vehicle_description="", vehicle_acquired_date="", vehicle_term_premium=0.0,
               signed_form_id="")
    ctx.create("auto_policy_changes", exc_id, auto_change_id=exc_id, auto_policy_id=auto_policy_id,
               customer_id=term.get("customer_id", ""), event_type="auto_driver_excluded",
               change_effective_date=change_effective_date, driver_name=driver_name,
               driver_date_of_birth=prior.get("driver_date_of_birth", ""),
               driver_relationship=prior.get("driver_relationship", ""), prior_driver_status="rated",
               driver_violation_points=prior.get("driver_violation_points", 0), driver_term_premium=share,
               vehicle_vin="", vehicle_description="", vehicle_acquired_date="", vehicle_term_premium=0.0,
               signed_form_id=signed_form_id)
    if amount > 0:
        ctx.create("auto_premium_transactions", txn_id, auto_premium_txn_id=txn_id, auto_policy_id=auto_policy_id,
                   customer_id=term.get("customer_id", ""), event_type="auto_additional_premium",
                   transaction_date=ctx.now()[:10], effective_date=listing_effective_date, amount=amount,
                   transaction_reason="driver_added", premium_days=days, source_change_id=add_id, reversed_txn_id="")
        ctx.update("auto_policies", auto_policy_id,
                   term_written_premium=round(float(term.get("term_written_premium") or 0) + amount, 2))
    return (f"{driver_name} is listed from {listing_effective_date} (change {add_id}) and a named excluded driver on "
            f"term {auto_policy_id} from {change_effective_date} (change {exc_id}); additional premium transaction "
            f"{txn_id} for {amount:.2f} USD covering {days} days.")


@tool(owner="agent", rw="write")
def relist_household_resident_37288c8c(ctx: ToolContext, auto_policy_id: str, driver_name: str,
                                       change_effective_date: str, driver_term_premium: float,
                                       additional_premium: float, added_days: int) -> str:
    """List a household resident again as a rated driver on an Owner Auto Policy term and charge the additional premium.

    The desk uses this for one household member who was previously listed on the term and is again
    living in the household. One call records a driver-added change on the term (prior driver status
    unlisted, the given change effective date and full-term premium share, with the driver's date of
    birth, relationship and violation points carried from that driver's most recent entry on the
    term), books one additional premium transaction when the amount is above zero (transaction reason driver_added, effective on the
    change date, carrying the amount and days charged, linked to the change) and raises the term's net
    written premium by that amount. Once the call completes, the resident shows as a rated driver.

    Args:
        auto_policy_id: Id class — the reference number of the Owner Auto Policy term, read from the policy term lookup.
        driver_name: Verbatim class — the resident's full name copied character for character from the record that names the resident on the term, with no change in spelling, order or punctuation (verbatim).
        change_effective_date: Fixed-format class — the date the listing takes effect at 12:01 a.m., written YYYY-MM-DD.
        driver_term_premium: Fixed-format class — the full-term premium share the rating attributes to the resident as a rated driver, in USD, 2 decimal places.
        additional_premium: Fixed-format class — the additional premium charged for the listing, in USD, 2 decimal places, rounded half up to the cent.
        added_days: Fixed-format class — the number of days of the term the additional premium covers, an integer >= 0, calendar days.

    Returns:
        A confirmation sentence (string) naming the resident now rated, the term reference number, the
        change reference number, the change effective date (YYYY-MM-DD), and the additional premium
        transaction reference number with its amount in USD with 2 decimal places and its days; the
        presence of both reference numbers means the listing was recorded.
    """
    prior = _DriverEntries.latest(ctx.find("auto_policy_changes", auto_policy_id=auto_policy_id, driver_name=driver_name))
    rows = ctx.find("auto_policies", auto_policy_id=auto_policy_id)
    term = rows[0] if rows else {}
    share = round(float(driver_term_premium), 2)
    amount = round(float(additional_premium), 2)
    days = int(added_days)
    chg_id = ctx.make_id("apc_", auto_policy_id, "relist", driver_name, change_effective_date, share)
    txn_id = ctx.make_id("apt_", chg_id, "driver_added", amount, days)
    ctx.create("auto_policy_changes", chg_id, auto_change_id=chg_id, auto_policy_id=auto_policy_id,
               customer_id=term.get("customer_id", ""), event_type="auto_driver_added",
               change_effective_date=change_effective_date, driver_name=driver_name,
               driver_date_of_birth=prior.get("driver_date_of_birth", ""),
               driver_relationship=prior.get("driver_relationship", ""), prior_driver_status="unlisted",
               driver_violation_points=prior.get("driver_violation_points", 0), driver_term_premium=share,
               vehicle_vin="", vehicle_description="", vehicle_acquired_date="", vehicle_term_premium=0.0,
               signed_form_id="")
    if amount > 0:
        ctx.create("auto_premium_transactions", txn_id, auto_premium_txn_id=txn_id, auto_policy_id=auto_policy_id,
                   customer_id=term.get("customer_id", ""), event_type="auto_additional_premium",
                   transaction_date=ctx.now()[:10], effective_date=change_effective_date, amount=amount,
                   transaction_reason="driver_added", premium_days=days, source_change_id=chg_id, reversed_txn_id="")
    ctx.update("auto_policies", auto_policy_id,
               term_written_premium=round(float(term.get("term_written_premium") or 0) + amount, 2))
    return (f"{driver_name} is listed as a rated driver on term {auto_policy_id} from {change_effective_date} "
            f"(change {chg_id}); additional premium transaction {txn_id} booked for {amount:.2f} USD covering {days} days.")


@tool(owner="user", rw="write")
def lift_driver_exclusion_0b127d81(ctx: ToolContext, auto_policy_id: str, driver_name: str,
                                   change_effective_date: str, driver_term_premium: float,
                                   additional_premium: float, added_days: int) -> str:
    """Sign your own request to lift the named driver exclusion of a member of your household, so that person is covered again as a rated driver on your Owner Auto Policy term.

    The named insured uses this personally. One call records a driver-added change on the term (prior
    driver status excluded, the given change effective date and full-term premium share, with the
    driver's date of birth, relationship and violation points carried from that driver's most recent
    entry on the term), books one additional premium transaction when the amount is above zero (transaction reason driver_added,
    effective on the change date, carrying the amount and days charged, linked to the change) and
    raises the term's net written premium by that amount. Once the call completes, the person is no
    longer excluded and shows as a rated driver.

    Args:
        auto_policy_id: Id class — the reference number of your Owner Auto Policy term, given to you by the representative from the policy term lookup.
        driver_name: Verbatim class — the full name of the household member whose exclusion you are lifting, exactly as you state it, with no change in spelling, order or punctuation (verbatim).
        change_effective_date: Fixed-format class — the date the person is covered again from 12:01 a.m., written YYYY-MM-DD, as the representative states it.
        driver_term_premium: Fixed-format class — the full-term premium share for the person as a rated driver as the representative states it, in USD, 2 decimal places.
        additional_premium: Fixed-format class — the additional premium charged for lifting the exclusion as the representative states it, in USD, 2 decimal places, rounded half up to the cent.
        added_days: Fixed-format class — the number of days of the term the additional premium covers as the representative states it, an integer >= 0, calendar days.

    Returns:
        A confirmation sentence (string) naming the person now rated, the term reference number, the
        change reference number, the change effective date (YYYY-MM-DD), and the additional premium
        transaction reference number with its amount in USD with 2 decimal places and its days; the
        presence of both reference numbers means the exclusion was lifted.
    """
    prior = _DriverEntries.latest(ctx.find("auto_policy_changes", auto_policy_id=auto_policy_id, driver_name=driver_name))
    rows = ctx.find("auto_policies", auto_policy_id=auto_policy_id)
    term = rows[0] if rows else {}
    share = round(float(driver_term_premium), 2)
    amount = round(float(additional_premium), 2)
    days = int(added_days)
    chg_id = ctx.make_id("apc_", auto_policy_id, "lift", driver_name, change_effective_date, share)
    txn_id = ctx.make_id("apt_", chg_id, "driver_added", amount, days)
    ctx.create("auto_policy_changes", chg_id, auto_change_id=chg_id, auto_policy_id=auto_policy_id,
               customer_id=term.get("customer_id", ""), event_type="auto_driver_added",
               change_effective_date=change_effective_date, driver_name=driver_name,
               driver_date_of_birth=prior.get("driver_date_of_birth", ""),
               driver_relationship=prior.get("driver_relationship", ""), prior_driver_status="excluded",
               driver_violation_points=prior.get("driver_violation_points", 0), driver_term_premium=share,
               vehicle_vin="", vehicle_description="", vehicle_acquired_date="", vehicle_term_premium=0.0,
               signed_form_id="")
    if amount > 0:
        ctx.create("auto_premium_transactions", txn_id, auto_premium_txn_id=txn_id, auto_policy_id=auto_policy_id,
                   customer_id=term.get("customer_id", ""), event_type="auto_additional_premium",
                   transaction_date=ctx.now()[:10], effective_date=change_effective_date, amount=amount,
                   transaction_reason="driver_added", premium_days=days, source_change_id=chg_id, reversed_txn_id="")
    ctx.update("auto_policies", auto_policy_id,
               term_written_premium=round(float(term.get("term_written_premium") or 0) + amount, 2))
    return (f"The exclusion of {driver_name} on term {auto_policy_id} is lifted from {change_effective_date} "
            f"(change {chg_id}); additional premium transaction {txn_id} booked for {amount:.2f} USD covering {days} days.")

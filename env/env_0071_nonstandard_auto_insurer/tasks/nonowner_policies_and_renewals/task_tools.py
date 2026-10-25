"""Hidden task tools of the nonowner_policies_and_renewals difficulty (Named Non-Owner Policy).

Each tool performs one atomic business change on a Named Non-Owner Policy term with the values the
caller has already worked out; no tool judges eligibility, prerequisites or amounts.
"""

from erlbench import ToolContext, tool


@tool(owner="agent", rw="write")
def book_renewal_written_premium_ed68a083(ctx: ToolContext, nonowner_policy_id: str, written_amount: float,
                                          effective_date: str, premium_days: int) -> str:
    """Book the premium written for an accepted renewal term of a Named Non-Owner Policy.

    The service desk records one premium-written entry with the reason renewal on the renewal term
    named, carrying the amount, the coverage date the charge applies from and the number of days it
    covers, stamped with today's processing date. The term's net written premium rises by the amount
    booked, and the entry shows in the term's premium and fee history. A receipt with the new
    entry's reference number confirms the booking.

    Args:
        nonowner_policy_id: Id class — the reference number of the Named Non-Owner Policy renewal term
            the premium is written on, as returned by the non-owner policy lookup for the caller.
        written_amount: Fixed-format class — the premium written on the renewal term, in US dollars,
            a positive number with exactly 2 decimal places, already rounded half up to the cent.
        effective_date: Fixed-format class — the coverage date the written premium applies from,
            written YYYY-MM-DD as a calendar date with no time or time zone.
        premium_days: Fixed-format class — the number of calendar days of the term the written premium
            covers, an integer of 0 or more counted at a precision of one whole day, with no decimals.

    Returns:
        A one-line confirmation string naming the new premium entry reference number (prefix npw_),
        the term reference number, the amount booked in US dollars with 2 decimals, the coverage date
        in YYYY-MM-DD, the days covered as a whole number, and the term's net written premium in US
        dollars with 2 decimals once the entry is counted. The presence of the entry reference number
        means the premium was booked.
    """
    amount = round(float(written_amount), 2)
    days = int(premium_days)
    terms = ctx.find("nonowner_policies", nonowner_policy_id=nonowner_policy_id)
    term = terms[0] if terms else {}
    rid = ctx.make_id("npw_", nonowner_policy_id, amount, effective_date, days)
    ctx.create("nonowner_premium_transactions", rid, nonowner_premium_txn_id=rid,
               nonowner_policy_id=nonowner_policy_id, customer_id=term.get("customer_id", ""),
               event_type="nonowner_premium_written", transaction_date=ctx.now()[:10],
               effective_date=effective_date, amount=amount, transaction_reason="renewal",
               premium_days=days, reversed_txn_id=None)
    net = round(float(term.get("term_written_premium") or 0) + amount, 2)
    ctx.update("nonowner_policies", nonowner_policy_id, term_written_premium=net)
    return (f"Premium written booked: entry {rid} on term {nonowner_policy_id}, amount {amount:.2f} USD, "
            f"coverage from {effective_date}, {days} days; term net written premium now {net:.2f} USD.")


@tool(owner="user", rw="write")
def cancel_nonowner_term_6aabad38(ctx: ToolContext, nonowner_policy_id: str, nonowner_cancel_request_id: str,
                                  cancellation_effective_date: str, return_amount: float, premium_days: int) -> str:
    """Put into effect the named insured's own signed request to cancel their Named Non-Owner Policy term.

    The named insured cancels the term named on the strength of the signed cancellation request on
    file: the term's status becomes cancelled with the reason insured request, its cancellation
    effective date and closing date are set to the date given, and, when the amount given is above
    zero, one return-premium entry with the reason insured-request cancellation is booked for the
    amount and days given, dated from that cancellation date; a zero amount books no return entry.
    The term's net written premium falls by the amount returned. The insured sees the term as
    cancelled and any return as credited to the term, confirmed by the receipt.

    Args:
        nonowner_policy_id: Id class — the reference number of the Named Non-Owner Policy term being
            cancelled, as returned by the non-owner policy lookup for the caller.
        nonowner_cancel_request_id: Id class — the reference number of the named insured's signed
            cancellation request for that term, as returned by the cancellation request lookup.
        cancellation_effective_date: Fixed-format class — the date the cancellation takes effect at
            12:01 a.m., written YYYY-MM-DD as a calendar date with no time or time zone.
        return_amount: Fixed-format class — the premium returned on the cancellation, in US dollars,
            a number of zero or more with exactly 2 decimal places, already rounded half up to the
            cent; zero when nothing is returned.
        premium_days: Fixed-format class — the number of calendar days of unearned coverage the
            returned premium stands for, an integer of 0 or more counted at a precision of one whole day, with no decimals.

    Returns:
        A one-line confirmation string naming the term reference number, the signed request
        reference number, the new status cancelled with the reason insured request, the cancellation
        effective date in YYYY-MM-DD, the return entry reference number (prefix nrt_) or a note that
        no return entry was booked, the amount returned in US dollars with 2 decimals, the days it
        stands for as a whole number, and the term's net written premium in US dollars with 2
        decimals once the return is counted. The presence of the cancelled status means the
        cancellation took effect.
    """
    amount = round(float(return_amount), 2)
    days = int(premium_days)
    terms = ctx.find("nonowner_policies", nonowner_policy_id=nonowner_policy_id)
    term = terms[0] if terms else {}
    net = round(float(term.get("term_written_premium") or 0) - amount, 2)
    ctx.update("nonowner_policies", nonowner_policy_id, status="cancelled", cancellation_reason="insured_request",
               cancellation_effective_date=cancellation_effective_date, closed_date=cancellation_effective_date,
               term_written_premium=net)
    entry = "no return entry booked"
    if amount > 0:
        rid = ctx.make_id("nrt_", nonowner_policy_id, nonowner_cancel_request_id, cancellation_effective_date, amount, days)
        ctx.create("nonowner_premium_transactions", rid, nonowner_premium_txn_id=rid,
                   nonowner_policy_id=nonowner_policy_id, customer_id=term.get("customer_id", ""),
                   event_type="nonowner_return_premium", transaction_date=ctx.now()[:10],
                   effective_date=cancellation_effective_date, amount=amount,
                   transaction_reason="cancellation_insured_request", premium_days=days, reversed_txn_id=None)
        entry = f"return entry {rid}"
    return (f"Term {nonowner_policy_id} cancelled at the insured's request {nonowner_cancel_request_id}: status "
            f"cancelled (insured request), effective {cancellation_effective_date}; {entry} for "
            f"{amount:.2f} USD over {days} days; term net written premium now {net:.2f} USD.")



@tool(owner="agent", rw="write")
def issue_nonowner_renewal_offer_23563ff0(ctx: ToolContext, nonowner_policy_id: str, variant_name: str,
                                          renewal_full_term_premium: float, effective_date: str,
                                          expiration_date: str, term_days: int) -> str:
    """Issue the renewal offer of an expiring Named Non-Owner Policy term as a new renewal term.

    The service desk creates the renewal term of the expiring term named: it keeps the policy number,
    named insured, residence state, term length, violation points and certificate backed of the
    expiring term, carries the term number one higher, points back to the expiring term, and is stamped
    with today's issue date and the status renewal offered, carrying the package, full-term premium,
    opening day, closing boundary and number of days given, with no premium or fees yet booked. The insured
    has a renewal offer on file, accepted by paying the renewal bill. A receipt with the new
    renewal term's reference number confirms the issue.

    Args:
        nonowner_policy_id: Id class — the reference number of the expiring Named Non-Owner Policy
            term being renewed, as returned by the non-owner policy lookup for the caller.
        variant_name: Enum class — the package the renewal term carries, exactly one of:
            "Cardinal Point Non-Owner Minimum Limits" when the renewal carries the residence state's
            minimum limits without uninsured motorist cover beyond what the state mandates;
            "Cardinal Point Non-Owner Minimum Limits with UM" when it carries the state minimum limits
            with uninsured motorist cover equal to them;
            "Cardinal Point Non-Owner 50/100/50" when it carries 50,000/100,000/50,000 limits;
            "Cardinal Point Non-Owner 100/200/50" when it carries 100,000/200,000/50,000 limits;
            "Cardinal Point Non-Owner 100/300/50" when it carries 100,000/300,000/50,000 limits;
            "Cardinal Point Non-Owner 250/500/100" when it carries 250,000/500,000/100,000 limits.
        renewal_full_term_premium: Fixed-format class — the full-term premium of the renewal term in
            US dollars, a positive number with exactly 2 decimal places, already rounded half up to
            the cent.
        effective_date: Fixed-format class — the opening day of the renewal term, written YYYY-MM-DD
            as a calendar date with no time or time zone.
        expiration_date: Fixed-format class — the date coverage under the renewal term ends at
            12:01 a.m., written YYYY-MM-DD as a calendar date with no time or time zone.
        term_days: Fixed-format class — the calendar days of the renewal term, an integer of 1 or
            more counted at a precision of one whole day, with no decimals.

    Returns:
        A one-line confirmation string naming the new renewal term reference number (prefix nrn_),
        the expiring term reference number it renews, the policy number, the term number as a whole
        number, the package, the full-term premium in US dollars with 2 decimals, the opening day and
        the expiration date in YYYY-MM-DD, the term days as a whole number and the status
        renewal_offered. The presence of the new term reference number means the offer was issued.
    """
    terms = ctx.find("nonowner_policies", nonowner_policy_id=nonowner_policy_id)
    old = terms[0] if terms else {}
    premium = round(float(renewal_full_term_premium), 2)
    days = int(term_days)
    number = int(old.get("term_number") or 0) + 1
    rid = ctx.make_id("nrn_", nonowner_policy_id, variant_name, premium, effective_date, expiration_date, days)
    ctx.create("nonowner_policies", rid, nonowner_policy_id=rid, customer_id=old.get("customer_id", ""),
               variant_name=variant_name, status="renewal_offered", policy_number=old.get("policy_number", ""),
               resident_state=old.get("resident_state", ""), term_months=old.get("term_months"),
               term_number=number, prior_nonowner_term_id=nonowner_policy_id, opened_date=ctx.now()[:10],
               effective_date=effective_date, expiration_date=expiration_date, term_days=days, closed_date="",
               violation_points=old.get("violation_points"),
               financial_responsibility_filing=old.get("financial_responsibility_filing", ""),
               full_term_premium=premium, cancellation_notice_date="", cancellation_effective_date="",
               minimum_due_on_notice=0.00, cancellation_reason="", converted_to_auto_policy_id=None,
               reinstatement_date="", reinstatement_type="", lapse_start_date="", lapse_end_date="",
               term_written_premium=0.00, term_fees_charged=0.00)
    return (f"Renewal offer issued: term {rid} renewing {nonowner_policy_id}, policy {old.get('policy_number', '')} "
            f"term {number}, package {variant_name}, full-term premium {premium:.2f} USD, {effective_date} to "
            f"{expiration_date} ({days} days), status renewal_offered.")


@tool(owner="user", rw="write")
def change_nonowner_package_67dc97ad(ctx: ToolContext, nonowner_policy_id: str, new_variant_name: str,
                                     rerated_full_term_premium: float) -> str:
    """Put into effect the named insured's own election of a new package on their in-force Named Non-Owner Policy term.

    The named insured moves the term named onto the package they elect, and the term's full-term
    premium is set to the re-rated figure given for that package; the term's dates, points and
    certificate backed stay as they are, and no premium entry is booked by this change. The insured
    sees the new package and full-term premium on the term, confirmed by the receipt.

    Args:
        nonowner_policy_id: Id class — the reference number of the in-force Named Non-Owner Policy
            term whose package is changed, as returned by the non-owner policy lookup for the caller.
        new_variant_name: Enum class — the package the term moves to, exactly one of:
            "Cardinal Point Non-Owner Minimum Limits" when the term is to carry the residence state's
            minimum limits without uninsured motorist cover beyond what the state mandates;
            "Cardinal Point Non-Owner Minimum Limits with UM" when it is to carry the state minimum
            limits with uninsured motorist cover equal to them;
            "Cardinal Point Non-Owner 50/100/50" when it is to carry 50,000/100,000/50,000 limits;
            "Cardinal Point Non-Owner 100/200/50" when it is to carry 100,000/200,000/50,000 limits;
            "Cardinal Point Non-Owner 100/300/50" when it is to carry 100,000/300,000/50,000 limits;
            "Cardinal Point Non-Owner 250/500/100" when it is to carry 250,000/500,000/100,000 limits.
        rerated_full_term_premium: Fixed-format class — the full-term premium of the term on the new
            package in US dollars, a positive number with exactly 2 decimal places, already rounded
            half up to the cent.

    Returns:
        A one-line confirmation string naming the term reference number, the previous package, the
        new package and the new full-term premium in US dollars with 2 decimals. The appearance of
        the new package in the confirmation means the change took effect.
    """
    terms = ctx.find("nonowner_policies", nonowner_policy_id=nonowner_policy_id)
    old = terms[0] if terms else {}
    premium = round(float(rerated_full_term_premium), 2)
    ctx.update("nonowner_policies", nonowner_policy_id, variant_name=new_variant_name, full_term_premium=premium)
    return (f"Package changed on term {nonowner_policy_id}: {old.get('variant_name', '')} -> {new_variant_name}; "
            f"full-term premium now {premium:.2f} USD.")


@tool(owner="agent", rw="write")
def book_package_increase_premium_8b98e0ec(ctx: ToolContext, nonowner_policy_id: str, additional_amount: float,
                                           effective_date: str, premium_days: int, change_direction: str) -> str:
    """Book the additional premium charged for a package change during a Named Non-Owner Policy term.

    The service desk records one additional-premium entry with the limits-change reason given on the term
    named, carrying the amount, the coverage date the charge applies from and the number of days it
    covers, stamped with today's processing date. The term's net written premium rises by the amount
    booked, and the entry shows in the term's premium and fee history. A receipt with the new entry's
    reference number confirms the booking.

    Args:
        nonowner_policy_id: Id class — the reference number of the Named Non-Owner Policy term the
            increase is charged on, as returned by the non-owner policy lookup for the caller.
        additional_amount: Fixed-format class — the additional premium charged, in US dollars, a
            positive number with exactly 2 decimal places, already rounded half up to the cent.
        effective_date: Fixed-format class — the coverage date the charge applies from, written
            YYYY-MM-DD as a calendar date with no time or time zone.
        premium_days: Fixed-format class — the calendar days of the term the charge covers, an
            integer of 0 or more counted at a precision of one whole day, with no decimals.
        change_direction: Enum class — the direction of the package change the charge is for, exactly
            one of: "higher_base_rate" when the term moved to a package with a higher six-month base rate,
            recorded with the reason limits increase; "lower_base_rate" when it moved to a package with a
            lower six-month base rate, recorded with the reason limits decrease.

    Returns:
        A one-line confirmation string naming the new entry reference number (prefix nli_), the term
        reference number, the reason recorded, the amount in US dollars with 2 decimals, the coverage date in YYYY-MM-DD,
        the days covered as a whole number and the term's net written premium in US dollars with 2
        decimals once the entry is counted. The presence of the entry reference number means the
        charge was booked.
    """
    amount = round(float(additional_amount), 2)
    days = int(premium_days)
    reason = "limits_decrease" if change_direction == "lower_base_rate" else "limits_increase"
    terms = ctx.find("nonowner_policies", nonowner_policy_id=nonowner_policy_id)
    term = terms[0] if terms else {}
    rid = ctx.make_id("nli_", nonowner_policy_id, amount, effective_date, days)
    ctx.create("nonowner_premium_transactions", rid, nonowner_premium_txn_id=rid,
               nonowner_policy_id=nonowner_policy_id, customer_id=term.get("customer_id", ""),
               event_type="nonowner_additional_premium", transaction_date=ctx.now()[:10],
               effective_date=effective_date, amount=amount, transaction_reason=reason,
               premium_days=days, reversed_txn_id=None)
    net = round(float(term.get("term_written_premium") or 0) + amount, 2)
    ctx.update("nonowner_policies", nonowner_policy_id, term_written_premium=net)
    return (f"Increase premium booked: entry {rid} on term {nonowner_policy_id}, reason {reason}, amount {amount:.2f} USD, "
            f"coverage from {effective_date}, {days} days; term net written premium now {net:.2f} USD.")


@tool(owner="agent", rw="write")
def book_reinstatement_rewritten_premium_bf43cbc7(ctx: ToolContext, nonowner_policy_id: str, rewritten_amount: float,
                                                  effective_date: str, premium_days: int) -> str:
    """Book the premium re-written on a Named Non-Owner Policy term reinstated from a nonpayment cancellation.

    The service desk records one additional-premium entry with the reason reinstatement on the term
    named, carrying the amount, the coverage date the re-written premium applies from and the number
    of days it covers, stamped with today's processing date. The term's net written premium rises by
    the amount booked, and the entry shows in the term's premium and fee history. A receipt with the
    new entry's reference number confirms the booking.

    Args:
        nonowner_policy_id: Id class — the reference number of the reinstated Named Non-Owner Policy
            term, as returned by the non-owner policy lookup for the caller.
        rewritten_amount: Fixed-format class — the re-written premium in US dollars, a positive number
            with exactly 2 decimal places, already rounded half up to the cent.
        effective_date: Fixed-format class — the coverage date the re-written premium applies from,
            written YYYY-MM-DD as a calendar date with no time or time zone.
        premium_days: Fixed-format class — the calendar days of the term the re-written premium
            covers, an integer of 0 or more counted at a precision of one whole day, with no decimals.

    Returns:
        A one-line confirmation string naming the new entry reference number (prefix nrw_), the term
        reference number, the amount in US dollars with 2 decimals, the coverage date in YYYY-MM-DD,
        the days covered as a whole number and the term's net written premium in US dollars with 2
        decimals once the entry is counted. The presence of the entry reference number means the
        re-written premium was booked.
    """
    amount = round(float(rewritten_amount), 2)
    days = int(premium_days)
    terms = ctx.find("nonowner_policies", nonowner_policy_id=nonowner_policy_id)
    term = terms[0] if terms else {}
    rid = ctx.make_id("nrw_", nonowner_policy_id, amount, effective_date, days)
    ctx.create("nonowner_premium_transactions", rid, nonowner_premium_txn_id=rid,
               nonowner_policy_id=nonowner_policy_id, customer_id=term.get("customer_id", ""),
               event_type="nonowner_additional_premium", transaction_date=ctx.now()[:10],
               effective_date=effective_date, amount=amount, transaction_reason="reinstatement",
               premium_days=days, reversed_txn_id=None)
    net = round(float(term.get("term_written_premium") or 0) + amount, 2)
    ctx.update("nonowner_policies", nonowner_policy_id, term_written_premium=net)
    return (f"Re-written premium booked: entry {rid} on term {nonowner_policy_id}, amount {amount:.2f} USD, "
            f"coverage from {effective_date}, {days} days; term net written premium now {net:.2f} USD.")

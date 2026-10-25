"""Hidden task tools of the sr22_fr44_filings difficulty (category fr).

Each tool performs one atomic write on an SR-22 / FR-44 filing record with the values the agent (or
the customer at the agent's hand-over) has already worked out; no tool judges eligibility or derives
a policy figure.
"""

from erlbench import ToolContext, tool


class _CalendarDays:
    """Pure calendar arithmetic on 'YYYY-MM-DD' strings (civil-day ordinals)."""

    @staticmethod
    def _to_ordinal(y, m, d):
        y2 = y - (1 if m <= 2 else 0)
        era = (y2 if y2 >= 0 else y2 - 399) // 400
        yoe = y2 - era * 400
        doy = (153 * (m + (-3 if m > 2 else 9)) + 2) // 5 + d - 1
        doe = yoe * 365 + yoe // 4 - yoe // 100 + doy
        return era * 146097 + doe

    @staticmethod
    def _from_ordinal(z):
        era = (z if z >= 0 else z - 146096) // 146097
        doe = z - era * 146097
        yoe = (doe - doe // 1460 + doe // 36524 - doe // 146096) // 365
        y = yoe + era * 400
        doy = doe - (365 * yoe + yoe // 4 - yoe // 100)
        mp = (5 * doy + 2) // 153
        d = doy - (153 * mp + 2) // 5 + 1
        m = mp + (3 if mp < 10 else -9)
        return y + (1 if m <= 2 else 0), m, d

    @staticmethod
    def add_days(day: str, count: int) -> str:
        y, m, d = (int(x) for x in str(day)[:10].split("-"))
        y2, m2, d2 = _CalendarDays._from_ordinal(_CalendarDays._to_ordinal(y, m, d) + int(count))
        return f"{y2:04d}-{m2:02d}-{d2:02d}"


@tool(owner="agent", rw="write")
def transmit_lapse_sr26_2b138773(ctx: ToolContext, fr_filing_id: str, runoff_days: int) -> str:
    """Transmit to the state the SR-26 cancellation notice for an SR-22 or FR-44 certificate whose
    backing policy term (an Owner Auto Policy term or a Named Non-Owner term) was cancelled and has
    since been reinstated with a lapse.

    The certificate filing record is moved to the cancellation-filed state: today's date is recorded
    as its SR-26 date, policy_cancelled is recorded as the SR-26 reason, and its certificate end date
    is set to the SR-26 date plus the run-off days given. The state treats the driver as
    certified only through that certificate end date. The receipt confirms the notice was
    transmitted; nothing is charged or reversed by this action.

    Args:
        fr_filing_id: Id class — the reference number of the SR-22 or FR-44 certificate filing the
            notice is for, as returned by the filing lookup for the customer.
        runoff_days: Fixed-format class — the run-off of the notice, a whole number of calendar days
            (integer, zero or more, no fraction) counted from today's SR-26 date to the certificate end
            date.

    Returns:
        A one-line confirmation string naming the filing reference number, its new status
        cancellation_filed, the SR-26 date (YYYY-MM-DD, today), the SR-26 reason policy_cancelled and
        the certificate end date (YYYY-MM-DD). The presence of the status cancellation_filed in the
        confirmation indicates the notice was transmitted.
    """
    today = ctx.now()[:10]
    end_date = _CalendarDays.add_days(today, int(runoff_days))
    ctx.update("fr_filings", fr_filing_id, status="cancellation_filed", sr26_date=today,
               sr26_reason="policy_cancelled", certificate_end_date=end_date)
    return (f"SR-26 transmitted for filing {fr_filing_id}: status cancellation_filed, sr26_date {today}, "
            f"sr26_reason policy_cancelled, certificate_end_date {end_date}.")


@tool(owner="user", rw="write")
def order_refiled_certificate_bf9cb0f2(ctx: ToolContext, customer_id: str, fr_filing_id: str, auto_policy_id: str,
                                       nonowner_policy_id: str, filing_fee: float) -> str:
    """The filed driver personally orders a new SR-22 or FR-44 certificate filing that replaces their
    certificate which received an SR-26 for a cancellation of its since-reinstated backing policy term,
    and accepts the filing fee for it.

    A new certificate filing record is opened in the requested state with filing reason
    reinstatement_refiling for the customer and backing policy term given; it carries over from the
    replaced certificate the certificate form and type, the filing state, the filed driver's name,
    license number and date of birth, the state case number and the requirement end date, and names
    the replaced certificate as the filing it replaces. One filing fee charge for the amount given is
    recorded on the new filing's fee ledger with today's date, and the new filing's fees total equals
    that amount; nothing else is posted by this action. The replaced certificate itself is not
    changed. The receipt shows the new filing reference number, which the customer can quote to the
    desk.

    Args:
        customer_id: Id class — the customer reference number of the caller, as the agent reads it
            from the customer profile lookup and gives it to the customer.
        fr_filing_id: Id class — the reference number of the customer's certificate filing being
            replaced, as the agent reads it from the filing lookup and gives it to the customer.
        auto_policy_id: Id class — the reference number of the Owner Auto Policy term the replaced certificate names
            as its backing, as shown by the filing lookup; empty when the replaced certificate names
            none (an Operator certificate).
        nonowner_policy_id: Id class — the reference number of the Named Non-Owner Policy term the replaced
            certificate names as its backing, as shown by the filing lookup; empty when it names none.
        filing_fee: Fixed-format class — the filing fee for the new filing as the agent states it, in
            US dollars, a non-negative amount with 2 decimal places (precision 0.01), rounded to the cent half up.

    Returns:
        A one-line confirmation string naming the new filing reference number, its status requested,
        its filing reason reinstatement_refiling, the replaced filing reference number, the request
        date (YYYY-MM-DD, today), the fee transaction reference number and the fee booked in US dollars
        with two decimals. The presence of a new filing reference number with status requested
        indicates the order was placed.
    """
    rows = ctx.find("fr_filings", fr_filing_id=fr_filing_id)
    src = rows[0] if rows else {}
    today = ctx.now()[:10]
    fee = round(float(filing_fee), 2)
    new_id = ctx.make_id("frf_", customer_id, fr_filing_id, auto_policy_id, nonowner_policy_id, fee)
    ctx.create("fr_filings", new_id, fr_filing_id=new_id, customer_id=customer_id,
               auto_policy_id=auto_policy_id or None, nonowner_policy_id=nonowner_policy_id or None,
               variant_name=src.get("variant_name", ""), status="requested",
               filing_state=src.get("filing_state", ""), filed_driver_name=src.get("filed_driver_name", ""),
               filed_driver_license_number=src.get("filed_driver_license_number", ""),
               filed_driver_date_of_birth=src.get("filed_driver_date_of_birth", ""),
               dmv_case_number=src.get("dmv_case_number", ""), filing_reason="reinstatement_refiling",
               requested_date=today, opened_date=today, filed_date="", filing_effective_date="",
               required_through_date=src.get("required_through_date", ""), rejected_date="",
               rejection_reason="", sr26_date="", sr26_reason="", certificate_end_date="",
               prior_fr_filing_id=fr_filing_id, closed_date="", fees_charged_total=fee)
    txn_id = ctx.make_id("frt_", new_id, fee)
    ctx.create("fr_filing_transactions", txn_id, fr_filing_txn_id=txn_id, fr_filing_id=new_id,
               customer_id=customer_id, event_type="fr_filing_fee_assessed",
               posted_date=today, amount=fee, fee_reason="reinstatement_refiling",
               reversed_fee_txn_id=None, waiver_reason="")
    return (f"Refiled certificate ordered: filing {new_id} status requested, filing_reason reinstatement_refiling, "
            f"replaces {fr_filing_id}, requested {today}; fee transaction {txn_id} booked {fee:.2f} USD.")


@tool(owner="agent", rw="write")
def transmit_cancellation_sr26_eaec830f(ctx: ToolContext, fr_filing_id: str, auto_policy_id: str, runoff_days: int) -> str:
    """Transmit to the state the SR-26 cancellation notice for an SR-22 or FR-44 certificate whose
    backing policy term (an Owner Auto Policy term or a Named Non-Owner term) was cancelled and has
    not been reinstated.

    The certificate filing record is moved to the cancellation-filed state: today's date is recorded
    as its SR-26 date, policy_cancelled is recorded as the SR-26 reason, and its certificate end date
    is set to the SR-26 date plus the run-off days given. The state treats the driver as certified
    only through that certificate end date. The backing policy term itself is not changed and nothing
    is charged or reversed by this action.

    Args:
        fr_filing_id: Id class — the reference number of the SR-22 or FR-44 certificate filing the
            notice is for, as returned by the filing lookup for the customer.
        auto_policy_id: Id class — the reference number of the Owner Auto Policy term the certificate
            names as its backing, as shown by the filing lookup; an empty string when the certificate
            names a Named Non-Owner term as its backing.
        runoff_days: Fixed-format class — the run-off of the notice, a whole number of calendar days
            (integer, zero or more, no fraction) counted from today's SR-26 date to the certificate end
            date.

    Returns:
        A one-line confirmation string naming the filing reference number, the Owner Auto Policy term
        reference number given (empty for a Named Non-Owner backing), the new status cancellation_filed,
        the SR-26 date (YYYY-MM-DD, today), the SR-26 reason policy_cancelled and the certificate end
        date (YYYY-MM-DD). The presence of the status cancellation_filed in the confirmation indicates
        the notice was transmitted.
    """
    today = ctx.now()[:10]
    end_date = _CalendarDays.add_days(today, int(runoff_days))
    ctx.update("fr_filings", fr_filing_id, status="cancellation_filed", sr26_date=today,
               sr26_reason="policy_cancelled", certificate_end_date=end_date)
    return (f"SR-26 transmitted for filing {fr_filing_id} (owner backing term {auto_policy_id}): status cancellation_filed, "
            f"sr26_date {today}, sr26_reason policy_cancelled, certificate_end_date {end_date}.")


@tool(owner="agent", rw="write")
def post_unbilled_filing_fee_f14427ed(ctx: ToolContext, fr_filing_id: str, fee_amount: float) -> str:
    """Charge again, on an existing SR-22 or FR-44 certificate filing, the filing fee whose charges were
    all reversed in full as charged in error, so that one fee stands on the request.

    One filing fee charge for the amount given is recorded on the filing's fee ledger with today's
    posting date, using the filing's own filing reason as the fee reason, and the filing's fees total
    is raised by that amount; nothing else is posted by this action. The certificate's status and
    dates are not changed. The receipt shows the fee transaction reference number and the new fees
    total of the filing.

    Args:
        fr_filing_id: Id class — the reference number of the certificate filing the fee belongs to, as
            returned by the filing lookup for the customer.
        fee_amount: Fixed-format class — the filing fee to charge, in US dollars, a non-negative amount
            with 2 decimal places (precision 0.01), rounded to the cent half up.

    Returns:
        A one-line confirmation string naming the fee transaction reference number, the filing reference
        number, the posting date (YYYY-MM-DD, today), the fee reason, the fee charged and the filing's new
        fees total, both in US dollars with two decimals. The presence of a fee transaction reference
        number indicates the fee was recorded.
    """
    rows = ctx.find("fr_filings", fr_filing_id=fr_filing_id)
    src = rows[0] if rows else {}
    today = ctx.now()[:10]
    fee = round(float(fee_amount), 2)
    reason = src.get("filing_reason", "")
    txn_id = ctx.make_id("frt_", fr_filing_id, fee, today)
    ctx.create("fr_filing_transactions", txn_id, fr_filing_txn_id=txn_id, fr_filing_id=fr_filing_id,
               customer_id=src.get("customer_id", ""), event_type="fr_filing_fee_assessed",
               posted_date=today, amount=fee, fee_reason=reason, reversed_fee_txn_id=None, waiver_reason="")
    total = round(float(src.get("fees_charged_total") or 0) + fee, 2)
    ctx.update("fr_filings", fr_filing_id, fees_charged_total=total)
    return (f"Filing fee charged: transaction {txn_id} on filing {fr_filing_id}, posted {today}, fee_reason {reason}, "
            f"amount {fee:.2f} USD; fees total now {total:.2f} USD.")


@tool(owner="user", rw="write")
def order_moved_certificate_231455f7(ctx: ToolContext, customer_id: str, fr_filing_id: str, auto_policy_id: str,
                                     nonowner_policy_id: str, filing_fee: float) -> str:
    """The named insured personally orders their SR-22 or FR-44 certificate refiled on their new
    backing policy term after moving, the term that backed it having been cancelled and not reinstated,
    and accepts the filing fee for it.

    A new certificate filing record is opened in the requested state with filing reason state_change
    for the customer and the new backing policy term given; it carries over from the replaced
    certificate the certificate form and type, the filing state, the filed driver's name, license
    number and date of birth, the state case number and the requirement end date, and names the
    replaced certificate as the filing it replaces. One filing fee charge for the amount given is
    recorded on the new filing's fee ledger with today's date, and the new filing's fees total equals
    that amount; nothing else is posted by this action. The replaced certificate itself is not
    changed. The receipt shows the new filing reference number.

    Args:
        customer_id: Id class — the customer reference number of the named insured, as the agent reads
            it from the customer profile lookup and gives it to the customer.
        fr_filing_id: Id class — the reference number of the customer's certificate filing being
            replaced, as the agent reads it from the filing lookup and gives it to the customer.
        auto_policy_id: Id class — the reference number of the new Owner Auto Policy term the new
            certificate rests on, as shown by the policy lookup and given by the agent; empty when the new
            backing is a Named Non-Owner term.
        nonowner_policy_id: Id class — the reference number of the new Named Non-Owner Policy term the new
            certificate rests on, as shown by the policy lookup; empty when the new backing is an Owner Auto
            Policy term.
        filing_fee: Fixed-format class — the filing fee for the new filing as the agent states it, in
            US dollars, a non-negative amount with 2 decimal places (precision 0.01), rounded to the cent
            half up.

    Returns:
        A one-line confirmation string naming the new filing reference number, its status requested,
        its filing reason state_change, the replaced filing reference number, the request date
        (YYYY-MM-DD, today), the fee transaction reference number and the fee recorded in US dollars with
        two decimals. The presence of a new filing reference number with status requested indicates the
        order was placed.
    """
    rows = ctx.find("fr_filings", fr_filing_id=fr_filing_id)
    src = rows[0] if rows else {}
    today = ctx.now()[:10]
    fee = round(float(filing_fee), 2)
    new_id = ctx.make_id("frf_", customer_id, fr_filing_id, auto_policy_id, nonowner_policy_id, fee)
    ctx.create("fr_filings", new_id, fr_filing_id=new_id, customer_id=customer_id,
               auto_policy_id=auto_policy_id or None, nonowner_policy_id=nonowner_policy_id or None,
               variant_name=src.get("variant_name", ""), status="requested",
               filing_state=src.get("filing_state", ""), filed_driver_name=src.get("filed_driver_name", ""),
               filed_driver_license_number=src.get("filed_driver_license_number", ""),
               filed_driver_date_of_birth=src.get("filed_driver_date_of_birth", ""),
               dmv_case_number=src.get("dmv_case_number", ""), filing_reason="state_change",
               requested_date=today, opened_date=today, filed_date="", filing_effective_date="",
               required_through_date=src.get("required_through_date", ""), rejected_date="",
               rejection_reason="", sr26_date="", sr26_reason="", certificate_end_date="",
               prior_fr_filing_id=fr_filing_id, closed_date="", fees_charged_total=fee)
    txn_id = ctx.make_id("frt_", new_id, fee)
    ctx.create("fr_filing_transactions", txn_id, fr_filing_txn_id=txn_id, fr_filing_id=new_id,
               customer_id=customer_id, event_type="fr_filing_fee_assessed", posted_date=today, amount=fee,
               fee_reason="state_change", reversed_fee_txn_id=None, waiver_reason="")
    return (f"Moved certificate ordered: filing {new_id} status requested, filing_reason state_change, "
            f"replaces {fr_filing_id}, requested {today}; fee transaction {txn_id} recorded {fee:.2f} USD.")

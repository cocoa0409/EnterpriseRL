"""Hidden task tools for the maintenance agreement desk of Halvorsen Mechanical & Controls, Inc.

Each function performs one atomic write on a preventive maintenance agreement and its ledger.
The names are registered only in maintenance.extended.yaml (extended_policies.target_tool) and are
reached at runtime through the unlock/call meta tools.
"""

from erlbench import ToolContext, tool


@tool(owner="agent", rw="write")
def charge_late_fee_06bbd225(ctx: ToolContext, agreement_id: str, invoice_ref: str,
                             fee_amount_usd: float) -> str:
    """Add a charge for instalments left unpaid to a preventive maintenance agreement.

    One call books a single charge of that kind against the named agreement, attaches it to the
    invoice the owner was already billed on, stamps it with the current billing month, and raises the
    amount the owner owes under the agreement by the amount booked. Afterwards the charge appears in
    the agreement's history and the agreement's outstanding balance is higher by exactly that amount.

    Args:
        agreement_id: Id class — the reference number of the preventive maintenance agreement record
            the charge is booked against, read from the maintenance agreement lookup before the call.
        invoice_ref: Fixed-format class — the invoice number the charge is attached to, written as
            INV- followed by 8 digits, copied from the instalment entry it belongs to in the
            agreement's history; the office raises no new invoice number for this charge.
        fee_amount_usd: Fixed-format class — the money amount booked, in USD, to 2 decimal places,
            rounded half up at the cent; an amount of zero is accepted and books a zero charge.

    Returns:
        A one-line confirmation string naming the reference number of the charge entry created, the
        agreement it was booked against, the invoice it was attached to and the amount booked in USD
        to two decimal places. The returned line is issued only when the charge has been written and
        the agreement's outstanding balance has been raised; that line is the receipt of completion.
    """
    rid = ctx.make_id("mev_", agreement_id, invoice_ref, fee_amount_usd, "late_fee")
    rows = ctx.find("maintenance_agreements", agreement_id=agreement_id)
    if not rows:
        return f"Error: no maintenance agreement {agreement_id}."
    amount = round(float(fee_amount_usd), 2)
    ctx.create("maintenance_events", rid, event_id=rid, agreement_id=agreement_id,
               customer_id=rows[0].get("customer_id"), event_type="maintenance_fee_charged",
               charge_type="late_fee", invoice_ref=invoice_ref, amount_usd=amount,
               billing_period=ctx.now()[:7])
    ctx.update("maintenance_agreements", agreement_id,
               balance_due=round(float(rows[0].get("balance_due") or 0) + amount, 2))
    return (f"Charge {rid} booked on agreement {agreement_id} against invoice {invoice_ref} "
            f"for {amount:.2f} USD.")


@tool(owner="agent", rw="write")
def issue_visit_credit_1d93f422(ctx: ToolContext, agreement_id: str, work_order_ref: str,
                                invoice_ref: str, credit_amount_usd: float) -> str:
    """Credit a building owner for a booked maintenance visit that was never performed.

    One call books a single credit of that kind against the named agreement, ties it to the work
    order the visit was booked under, sets it against the invoice the owner is to take it off,
    stamps it with the current billing month, and lowers the amount the owner owes under the
    agreement by the amount credited. Afterwards the credit appears in the agreement's history and
    the agreement's outstanding balance is lower by exactly that amount.

    Args:
        agreement_id: Id class — the reference number of the preventive maintenance agreement record
            the credit is booked against, read from the maintenance agreement lookup before the call.
        work_order_ref: Fixed-format class — the work order number the unperformed visit was booked
            under, written as WO- followed by 7 digits, copied from the booking entry in the
            agreement's history.
        invoice_ref: Fixed-format class — the invoice number the credit is set against, written as
            INV- followed by 8 digits, copied from the instalment entry it is to be taken off in the
            agreement's history.
        credit_amount_usd: Fixed-format class — the money amount credited, in USD, to 2 decimal
            places, rounded half up at the cent; an amount of zero is accepted and books a zero credit.

    Returns:
        A one-line confirmation string naming the reference number of the credit entry created, the
        agreement it was booked against, the work order it was tied to, the invoice it was set
        against and the amount credited in USD to two decimal places. The returned line is issued
        only when the credit has been written and the agreement's outstanding balance has been
        lowered; that line is the receipt of completion.
    """
    rid = ctx.make_id("mev_", agreement_id, work_order_ref, invoice_ref, credit_amount_usd)
    rows = ctx.find("maintenance_agreements", agreement_id=agreement_id)
    if not rows:
        return f"Error: no maintenance agreement {agreement_id}."
    amount = round(float(credit_amount_usd), 2)
    ctx.create("maintenance_events", rid, event_id=rid, agreement_id=agreement_id,
               customer_id=rows[0].get("customer_id"), event_type="maintenance_credit_issued",
               credit_reason="missed_visit", work_order_ref=work_order_ref,
               invoice_ref=invoice_ref, amount_usd=amount, billing_period=ctx.now()[:7])
    ctx.update("maintenance_agreements", agreement_id,
               balance_due=round(float(rows[0].get("balance_due") or 0) - amount, 2))
    return (f"Credit {rid} issued on agreement {agreement_id} for work order {work_order_ref}, "
            f"set against invoice {invoice_ref}, for {amount:.2f} USD.")


@tool(owner="agent", rw="write")
def charge_extra_visit_764307e1(ctx: ToolContext, agreement_id: str, work_order_ref: str,
                                invoice_ref: str, charge_amount_usd: float) -> str:
    """Bill a building owner for a maintenance visit performed beyond the visits their term carried.

    One call books a single charge of that kind against the named agreement, ties it to the work
    order the visit was performed under, attaches it to the invoice the owner is billed on, stamps it
    with the current billing month, and raises the amount the owner owes under the agreement by the
    amount booked. Afterwards the charge appears in the agreement's history and the agreement's
    outstanding balance is higher by exactly that amount.

    Args:
        agreement_id: Id class — the reference number of the preventive maintenance agreement record
            the charge is booked against, read from the maintenance agreement lookup before the call.
        work_order_ref: Fixed-format class — the work order number the visit was performed under,
            written as WO- followed by 7 digits, copied from the completion entry in the agreement's
            history.
        invoice_ref: Fixed-format class — the invoice number the charge is attached to, written as
            INV- followed by 8 digits, copied from the instalment entry it belongs to in the
            agreement's history; the office raises no new invoice number for this charge.
        charge_amount_usd: Fixed-format class — the money amount billed, in USD, to 2 decimal places,
            rounded half up at the cent; an amount of zero is accepted and books a zero charge.

    Returns:
        A one-line confirmation string naming the reference number of the charge entry created, the
        agreement it was booked against, the work order it was tied to, the invoice it was attached
        to and the amount billed in USD to two decimal places. The returned line is issued only when
        the charge has been written and the agreement's outstanding balance has been raised; that
        line is the receipt of completion.
    """
    rid = ctx.make_id("mev_", agreement_id, work_order_ref, invoice_ref, charge_amount_usd,
                      "extra_visit")
    rows = ctx.find("maintenance_agreements", agreement_id=agreement_id)
    if not rows:
        return f"Error: no maintenance agreement {agreement_id}."
    amount = round(float(charge_amount_usd), 2)
    ctx.create("maintenance_events", rid, event_id=rid, agreement_id=agreement_id,
               customer_id=rows[0].get("customer_id"), event_type="maintenance_fee_charged",
               charge_type="extra_visit", work_order_ref=work_order_ref, invoice_ref=invoice_ref,
               amount_usd=amount, billing_period=ctx.now()[:7])
    ctx.update("maintenance_agreements", agreement_id,
               balance_due=round(float(rows[0].get("balance_due") or 0) + amount, 2))
    return (f"Charge {rid} booked on agreement {agreement_id} for work order {work_order_ref}, "
            f"attached to invoice {invoice_ref}, for {amount:.2f} USD.")


@tool(owner="user", rw="write")
def record_agreement_settlement_0349d2fc(ctx: ToolContext, agreement_id: str, invoice_ref: str,
                                         settlement_amount_usd: float,
                                         payment_method: str) -> str:
    """Pay a preventive maintenance agreement account off, as the building owner, in one payment.

    One call books a single payment from the owner against the named agreement, applies it to the
    invoice they name, records how the money was sent, stamps it with today as the day the office
    received it, and lowers the amount owed under the agreement by the amount paid. Afterwards the
    payment appears in the agreement's history and the owner can see the agreement's outstanding
    balance reduced by exactly that amount.

    Args:
        agreement_id: Id class — the reference number of the preventive maintenance agreement record
            the payment is applied to, read from the maintenance agreement lookup before the call.
        invoice_ref: Fixed-format class — the invoice number the payment is applied to, written as
            INV- followed by 8 digits, copied from an instalment entry in the agreement's history.
        settlement_amount_usd: Fixed-format class — the money amount the owner pays, in USD, to 2
            decimal places, rounded half up at the cent; an amount of zero is accepted and books a
            zero payment.
        payment_method: Enum class — how the owner sent the money, one of exactly these four values.
            check — the owner has posted or handed over a paper cheque drawn on the company account.
            ach — the owner has pushed the money by bank transfer from their own bank.
            credit_card — the owner has put the payment on a company credit card.
            wire — the owner has sent the money by same-day wire transfer.

    Returns:
        A one-line confirmation string naming the reference number of the payment entry created, the
        agreement it was applied to, the invoice it was applied against, the amount paid in USD to
        two decimal places and the way the money was sent. The returned line is issued only when the
        payment has been written and the agreement's outstanding balance has been lowered; that line
        is the owner's receipt of completion.
    """
    rid = ctx.make_id("mev_", agreement_id, invoice_ref, settlement_amount_usd, payment_method)
    rows = ctx.find("maintenance_agreements", agreement_id=agreement_id)
    if not rows:
        return f"Error: no maintenance agreement {agreement_id}."
    amount = round(float(settlement_amount_usd), 2)
    ctx.create("maintenance_events", rid, event_id=rid, agreement_id=agreement_id,
               customer_id=rows[0].get("customer_id"), event_type="maintenance_payment_received",
               invoice_ref=invoice_ref, amount_usd=amount, payment_method=payment_method,
               received_date=ctx.now()[:10])
    ctx.update("maintenance_agreements", agreement_id,
               balance_due=round(float(rows[0].get("balance_due") or 0) - amount, 2))
    return (f"Payment {rid} received on agreement {agreement_id} against invoice {invoice_ref} "
            f"for {amount:.2f} USD by {payment_method}.")


@tool(owner="user", rw="write")
def clear_agreement_arrears_489edb92(ctx: ToolContext, agreement_id: str,
                                     clearance_amount_usd: float, payment_method: str) -> str:
    """Clear the arrears standing on a preventive maintenance agreement, as the building owner, in one payment.

    One call books a single payment from the owner against the named agreement as one figure for the whole
    account rather than against a named invoice, records how the money was sent, stamps it with today as
    the day the office received it, and lowers the amount owed under the agreement by the amount paid.
    Afterwards the payment appears in the agreement's history and the owner can see the agreement's
    outstanding balance reduced by exactly that amount.

    Args:
        agreement_id: Id class — the reference number of the preventive maintenance agreement record the
            payment is applied to, read from the maintenance agreement lookup before the call.
        clearance_amount_usd: Fixed-format class — the money amount the owner pays to clear the arrears, in
            USD, to 2 decimal places, rounded half up at the cent; an amount of zero is accepted and books
            a zero payment.
        payment_method: Enum class — how the owner sent the money, one of exactly these four values.
            check — the owner has posted or handed over a paper cheque drawn on the company account.
            ach — the owner has pushed the money by bank transfer from their own bank.
            credit_card — the owner has put the payment on a company credit card.
            wire — the owner has sent the money by same-day wire transfer.

    Returns:
        A one-line confirmation string naming the reference number of the payment entry created, the
        agreement the payment was applied to, the amount paid in USD to two decimal places and the way the
        money was sent. The returned line is issued only when the payment has been written and the
        agreement's outstanding balance has been lowered; that line is the owner's receipt of completion.
    """
    rid = ctx.make_id("mev_", agreement_id, clearance_amount_usd, payment_method, "clearance")
    rows = ctx.find("maintenance_agreements", agreement_id=agreement_id)
    if not rows:
        return f"Error: no maintenance agreement {agreement_id}."
    amount = round(float(clearance_amount_usd), 2)
    ctx.create("maintenance_events", rid, event_id=rid, agreement_id=agreement_id,
               customer_id=rows[0].get("customer_id"), event_type="maintenance_payment_received",
               amount_usd=amount, payment_method=payment_method, received_date=ctx.now()[:10])
    ctx.update("maintenance_agreements", agreement_id,
               balance_due=round(float(rows[0].get("balance_due") or 0) - amount, 2))
    return (f"Payment {rid} received on agreement {agreement_id} clearing {amount:.2f} USD "
            f"by {payment_method}.")


@tool(owner="agent", rw="write")
def reinstate_agreement_coverage_5877576a(ctx: ToolContext, agreement_id: str,
                                          reinstatement_charge_usd: float) -> str:
    """Put withdrawn coverage on a preventive maintenance agreement back in force and charge for doing it.

    One call moves the named agreement out of its withdrawn standing and back into the renewal window it
    was withdrawn from, stamps today as the day coverage was restored, books the charge for restoring it
    against the agreement and raises the amount the owner owes by that charge. Afterwards visits may be
    booked again on the agreement, the charge appears in its history and its outstanding balance is higher
    by exactly the charge booked.

    Args:
        agreement_id: Id class — the reference number of the preventive maintenance agreement record whose
            coverage is restored, read from the maintenance agreement lookup before the call.
        reinstatement_charge_usd: Fixed-format class — the money amount charged for restoring coverage, in
            USD, to 2 decimal places, rounded half up at the cent; an amount of zero is accepted and books
            a zero charge.

    Returns:
        A one-line confirmation string naming the agreement restored, the standing it now carries, the
        reference number of the charge entry created and the amount charged in USD to two decimal places.
        The returned line is issued only when the standing has been changed, the charge written and the
        outstanding balance raised; that line is the receipt of completion.
    """
    rid = ctx.make_id("mev_", agreement_id, reinstatement_charge_usd, "reinstatement")
    rows = ctx.find("maintenance_agreements", agreement_id=agreement_id)
    if not rows:
        return f"Error: no maintenance agreement {agreement_id}."
    amount = round(float(reinstatement_charge_usd), 2)
    ctx.create("maintenance_events", rid, event_id=rid, agreement_id=agreement_id,
               customer_id=rows[0].get("customer_id"), event_type="maintenance_fee_charged",
               charge_type="reinstatement", amount_usd=amount, billing_period=ctx.now()[:7])
    ctx.update("maintenance_agreements", agreement_id, status="pending_renewal",
               reinstatement_date=ctx.now()[:10],
               balance_due=round(float(rows[0].get("balance_due") or 0) + amount, 2))
    return (f"Coverage on agreement {agreement_id} is back in force and stands in its renewal window; "
            f"charge {rid} booked for {amount:.2f} USD.")


@tool(owner="agent", rw="write")
def renew_agreement_term_748887d3(ctx: ToolContext, agreement_id: str,
                                  renewed_annual_price_usd: float) -> str:
    """Record a further term on a preventive maintenance agreement at the price settled for it.

    One call rolls the named agreement into a further term of the same length as the one just ending: the
    new term starts the day after the current term's last day and runs for the same number of days, the
    annual price in force is replaced by the price given, and the agreement's standing moves back to active
    for the new term. Afterwards the owner sees the new term dates and the new annual price on the
    agreement, and coverage runs on without a break.

    Args:
        agreement_id: Id class — the reference number of the preventive maintenance agreement record rolled
            into a further term, read from the maintenance agreement lookup before the call.
        renewed_annual_price_usd: Fixed-format class — the annual price in force for the further term, in
            USD, to 2 decimal places, rounded half up at the cent; an amount of zero is accepted and records
            a zero price.

    Returns:
        A one-line confirmation string naming the agreement rolled over, the first and last day of the
        further term as YYYY-MM-DD, the annual price now in force in USD to two decimal places and the
        standing the agreement now carries. The returned line is issued only when the term dates, the price
        and the standing have all been written; that line is the receipt of completion.
    """
    rows = ctx.find("maintenance_agreements", agreement_id=agreement_id)
    if not rows:
        return f"Error: no maintenance agreement {agreement_id}."
    row = rows[0]
    # Whole-day arithmetic on the two term dates already written on the record, done with the
    # proleptic Gregorian days-from-civil identities. No clock is consulted: the only inputs are
    # the record's own term_start_date and term_end_date.
    day_numbers = []
    for stamp in (str(row.get("term_start_date"))[:10], str(row.get("term_end_date"))[:10]):
        year, month, day = int(stamp[0:4]), int(stamp[5:7]), int(stamp[8:10])
        year -= 1 if month <= 2 else 0
        era = (year if year >= 0 else year - 399) // 400
        year_of_era = year - era * 400
        day_of_year = (153 * (month + (-3 if month > 2 else 9)) + 2) // 5 + day - 1
        day_of_era = year_of_era * 365 + year_of_era // 4 - year_of_era // 100 + day_of_year
        day_numbers.append(era * 146097 + day_of_era - 719468)
    span = day_numbers[1] - day_numbers[0]
    term_dates = []
    for day_number in (day_numbers[1] + 1, day_numbers[1] + 1 + span):
        shifted = day_number + 719468
        era = (shifted if shifted >= 0 else shifted - 146096) // 146097
        day_of_era = shifted - era * 146097
        year_of_era = (day_of_era - day_of_era // 1460 + day_of_era // 36524
                       - day_of_era // 146096) // 365
        year = year_of_era + era * 400
        day_of_year = day_of_era - (365 * year_of_era + year_of_era // 4 - year_of_era // 100)
        month_index = (5 * day_of_year + 2) // 153
        day = day_of_year - (153 * month_index + 2) // 5 + 1
        month = month_index + (3 if month_index < 10 else -9)
        year += 1 if month <= 2 else 0
        term_dates.append(f"{year:04d}-{month:02d}-{day:02d}")
    new_start, new_end = term_dates[0], term_dates[1]
    price = round(float(renewed_annual_price_usd), 2)
    ctx.update("maintenance_agreements", agreement_id, status="active",
               term_start_date=new_start, term_end_date=new_end,
               annual_price_usd=price)
    return (f"Agreement {agreement_id} renewed for a further term running {new_start} to "
            f"{new_end} at {price:.2f} USD a year; it now stands active.")

"""Hidden task tools for the managed_services_agreements difficulty (ClearPath Managed IT Services).

Each tool performs one atomic change on a ClearPath agreement record set and is reached only through the
unlock/call meta-tools; the values it records are worked out by the caller under the published charter.
"""

from erlbench import ToolContext, tool


class _Ledger:
    """Pure helpers for receipt formatting (no policy logic)."""

    @staticmethod
    def invoice_number(row_id):
        digits = int(row_id[-8:], 16) % 10000
        return "INV-01" + str(digits).zfill(4)

    @staticmethod
    def month_of(stamp):
        return str(stamp)[:7]


@tool(owner="agent", rw="write")
def record_renewal_term_69c0d348(ctx: ToolContext, managed_agreement_id: str, seat_rate_usd: float,
                                 contracted_seats: int, term_start_date: str, term_end_date: str,
                                 term_months: int) -> str:
    """Record the automatic renewal of a ClearPath agreement into its next term.

    The service desk rolls the agreement into the renewal term: the agreement's current term start and end
    dates, term length, per-seat rate and seat commitment are replaced by those of the renewal term, and its
    renewal count goes up by one. Status, seats covered, notices and balance are left as they are. On success
    the agreement shows the renewal term in force.

    Args:
        managed_agreement_id: Id class — the reference number of the ClearPath agreement being renewed, as returned by the agreement lookup for the verified client.
        seat_rate_usd: Fixed-format class — the per-seat monthly rate for the renewal term in US dollars, a decimal number with 2 decimal places (cents); the value is stored rounded to the cent.
        contracted_seats: Fixed-format class — the seat commitment for the renewal term, in integer seats (a whole number, no decimals).
        term_start_date: Fixed-format class — the first day of the renewal term, a calendar date written YYYY-MM-DD (US Eastern business date).
        term_end_date: Fixed-format class — the last day of the renewal term, a calendar date written YYYY-MM-DD (US Eastern business date).
        term_months: Fixed-format class — the length of the renewal term, an integer number of months.

    Returns:
        A confirmation string naming the agreement reference, the renewal term dates (YYYY-MM-DD), the term
        length in months, the renewal per-seat rate in US dollars with 2 decimals, the seat commitment and the new
        renewal count; it begins with "Renewal recorded" when the renewal term is in force on the agreement.
    """
    rows = ctx.find("managed_agreements", managed_agreement_id=managed_agreement_id)
    count = int((rows[0].get("renewal_count") if rows else 0) or 0) + 1
    rate = round(float(seat_rate_usd), 2)
    ctx.update("managed_agreements", managed_agreement_id, term_start_date=term_start_date,
               term_end_date=term_end_date, term_months=int(term_months), seat_rate_usd=rate,
               contracted_seats=int(contracted_seats), renewal_count=count)
    return (f"Renewal recorded on agreement {managed_agreement_id}: term {term_start_date} to {term_end_date} "
            f"({int(term_months)} months), seat rate {rate:.2f} USD, contracted seats {int(contracted_seats)}, "
            f"renewal count {count}.")


@tool(owner="agent", rw="write")
def post_monthly_fee_19cc11da(ctx: ToolContext, managed_agreement_id: str, billing_period: str,
                              amount_usd: float) -> str:
    """Invoice the monthly ClearPath seat fee of one service month on an agreement.

    The service desk posts one monthly fee charge for the service month on a new monthly invoice dated today;
    the amount is added to what the client owes on the agreement. On success the billing ledger carries the
    monthly fee with its invoice number and the agreement balance increases by the amount.

    Args:
        managed_agreement_id: Id class — the reference number of the ClearPath agreement billed, as returned by the agreement lookup for the verified client.
        billing_period: Fixed-format class — the service month the fee is for, written YYYY-MM (calendar month, US Eastern).
        amount_usd: Fixed-format class — the monthly fee in US dollars, a positive decimal number with 2 decimal places (cents); the value is stored rounded to the cent.

    Returns:
        A confirmation string with the new invoice number (INV- followed by 6 digits), the service month
        (YYYY-MM), the fee in US dollars with 2 decimals, the posting date (YYYY-MM-DD) and the agreement's new
        balance due in US dollars with 2 decimals; it begins with "Monthly fee posted" when the charge is on the
        ledger.
    """
    rows = ctx.find("managed_agreements", managed_agreement_id=managed_agreement_id)
    agr = rows[0] if rows else {}
    amount = round(float(amount_usd), 2)
    rid = ctx.make_id("mbl_", managed_agreement_id, "managed_monthly_fee", billing_period, amount)
    inv = _Ledger.invoice_number(rid)
    today = ctx.now()[:10]
    ctx.create("managed_billing", rid, managed_billing_entry_id=rid, managed_agreement_id=managed_agreement_id,
               customer_id=agr.get("customer_id", ""), event_type="managed_monthly_fee", amount_usd=amount,
               invoice_number=inv, billing_period=billing_period, posted_date=today, managed_seat_change_id=None,
               ticket_number="", labor_class="not_applicable", billable_minutes=0, payment_reference="",
               payment_method="not_applicable", original_billing_entry_id=None)
    balance = round(float(agr.get("balance_due_usd") or 0) + amount, 2)
    ctx.update("managed_agreements", managed_agreement_id, balance_due_usd=balance)
    return (f"Monthly fee posted on {inv} for {billing_period}: {amount:.2f} USD, posted {today}; "
            f"balance due {balance:.2f} USD.")


@tool(owner="agent", rw="write")
def record_reinstatement_be1b3a76(ctx: ToolContext, managed_agreement_id: str, reinstatement_fee_usd: float) -> str:
    """Reinstate a ClearPath agreement suspended for non-payment and invoice its reinstatement fee.

    The service desk returns the agreement to active service as of today, records today as the reinstatement
    date, and posts the reinstatement fee on a new invoice dated today, adding it to what the client owes. On
    success the agreement status reads active, support resumes, and the billing ledger carries the fee.

    Args:
        managed_agreement_id: Id class — the reference number of the suspended ClearPath agreement, as returned by the agreement lookup for the verified client.
        reinstatement_fee_usd: Fixed-format class — the reinstatement fee in US dollars, a positive decimal number with 2 decimal places (cents); the value is stored rounded to the cent.

    Returns:
        A confirmation string with the agreement reference, the new status (active), the reinstatement date
        (YYYY-MM-DD), the fee invoice number (INV- followed by 6 digits), the fee in US dollars with 2 decimals and
        the agreement's new balance due in US dollars with 2 decimals; it begins with "Agreement reinstated" when
        the change is recorded.
    """
    rows = ctx.find("managed_agreements", managed_agreement_id=managed_agreement_id)
    agr = rows[0] if rows else {}
    fee = round(float(reinstatement_fee_usd), 2)
    today = ctx.now()[:10]
    rid = ctx.make_id("mbl_", managed_agreement_id, "managed_reinstatement_fee", today, fee)
    inv = _Ledger.invoice_number(rid)
    ctx.update("managed_agreements", managed_agreement_id, status="active", reinstated_date=today)
    ctx.create("managed_billing", rid, managed_billing_entry_id=rid, managed_agreement_id=managed_agreement_id,
               customer_id=agr.get("customer_id", ""), event_type="managed_reinstatement_fee", amount_usd=fee,
               invoice_number=inv, billing_period=_Ledger.month_of(today), posted_date=today,
               managed_seat_change_id=None, ticket_number="", labor_class="not_applicable", billable_minutes=0,
               payment_reference="", payment_method="not_applicable", original_billing_entry_id=None)
    balance = round(float(agr.get("balance_due_usd") or 0) + fee, 2)
    ctx.update("managed_agreements", managed_agreement_id, balance_due_usd=balance)
    return (f"Agreement reinstated: {managed_agreement_id} is active as of {today}; reinstatement fee "
            f"{fee:.2f} USD on {inv}; balance due {balance:.2f} USD.")


@tool(owner="user", rw="write")
def sign_early_termination_notice_6477ae2a(ctx: ToolContext, customer_id: str, managed_agreement_id: str,
                                           managed_request_id: str, termination_effective_date: str,
                                           early_termination_fee_usd: float) -> str:
    """E-sign, as the client's authorized contact, the early termination notice awaiting your signature.

    Your signature marks the early termination request signed and puts the notice on the ClearPath agreement it
    concerns: the agreement moves to notice given, with early termination as the notice type, today as the date
    the signed notice was received and the stated termination effective date. The early termination fee stated
    on the notice is invoiced today on a new invoice and added to what the agreement owes. On success the
    agreement shows the notice on file and the fee appears on the billing ledger.

    Args:
        customer_id: Id class — your organisation's client reference number, as read out to you by the agent from the client profile lookup.
        managed_agreement_id: Id class — the reference number of your ClearPath agreement the notice ends, as read out to you by the agent from the agreement lookup.
        managed_request_id: Id class — the reference number of the contract change request record (the early termination request awaiting your signature), as read out to you by the agent from the change-request lookup.
        termination_effective_date: Fixed-format class — the date the termination takes effect as stated on the notice, a calendar date written YYYY-MM-DD (US Eastern business date).
        early_termination_fee_usd: Fixed-format class — the early termination fee stated on the notice in US dollars, a decimal number with 2 decimal places (cents); the value is stored rounded to the cent.

    Returns:
        A confirmation string with the request reference and its new status (signed), the agreement reference,
        the notice received date and termination effective date (YYYY-MM-DD), the fee invoice number (INV-
        followed by 6 digits), the fee in US dollars with 2 decimals and the agreement's new balance due in US
        dollars with 2 decimals; it begins with "Early termination notice signed" when the notice is on file.
    """
    agr_id = managed_agreement_id
    rows = ctx.find("managed_agreements", managed_agreement_id=agr_id)
    agr = rows[0] if rows else {}
    fee = round(float(early_termination_fee_usd), 2)
    today = ctx.now()[:10]
    ctx.update("managed_service_requests", managed_request_id, request_status="signed")
    ctx.update("managed_agreements", agr_id, status="notice_given", notice_type="early_termination",
               notice_received_date=today, termination_effective_date=termination_effective_date)
    rid = ctx.make_id("mbl_", agr_id, "managed_early_termination_fee", managed_request_id, fee)
    inv = _Ledger.invoice_number(rid)
    ctx.create("managed_billing", rid, managed_billing_entry_id=rid, managed_agreement_id=agr_id,
               customer_id=customer_id, event_type="managed_early_termination_fee", amount_usd=fee,
               invoice_number=inv, billing_period=_Ledger.month_of(today), posted_date=today,
               managed_seat_change_id=None, ticket_number="", labor_class="not_applicable", billable_minutes=0,
               payment_reference="", payment_method="not_applicable", original_billing_entry_id=None)
    balance = round(float(agr.get("balance_due_usd") or 0) + fee, 2)
    ctx.update("managed_agreements", agr_id, balance_due_usd=balance)
    return (f"Early termination notice signed: request {managed_request_id} is signed; agreement {agr_id} notice "
            f"received {today}, effective {termination_effective_date}; early termination fee {fee:.2f} USD on "
            f"{inv}; balance due {balance:.2f} USD.")


@tool(owner="agent", rw="write")
def post_remote_after_hours_labor_c0dca9e8(ctx: ToolContext, managed_agreement_id: str, ticket_number: str,
                                           invoice_number: str, billing_period: str, billable_minutes: int,
                                           amount_usd: float) -> str:
    """Bill the remote after-hours labor of one resolved service desk ticket on a ClearPath invoice.

    The service desk posts one remote after-hours labor charge for the ticket onto the named monthly invoice,
    recording the billable minutes and the amount, and adds the amount to what the client owes on the agreement.
    On success the billing ledger shows the labor line on that invoice and the agreement balance increases.

    Args:
        managed_agreement_id: Id class — the reference number of the ClearPath agreement the ticket is logged under, as returned by the agreement lookup for the verified client.
        ticket_number: Fixed-format class — the service desk ticket the labor was performed on, written SB- followed by 7 digits, exactly as shown in the ticket history.
        invoice_number: Fixed-format class — the monthly invoice the charge is billed on, written INV- followed by 6 digits, exactly as shown on the billing ledger.
        billing_period: Fixed-format class — the month the work was performed, written YYYY-MM (calendar month, US Eastern).
        billable_minutes: Fixed-format class — the minutes billed for the labor, in integer minutes.
        amount_usd: Fixed-format class — the labor amount in US dollars, a positive decimal number with 2 decimal places (cents); the value is stored rounded to the cent.

    Returns:
        A confirmation string with the ticket number, the invoice number, the service month (YYYY-MM), the billable
        minutes, the amount in US dollars with 2 decimals and the agreement's new balance due in US dollars with 2
        decimals; it begins with "Remote after-hours labor posted" when the charge is on the ledger.
    """
    rows = ctx.find("managed_agreements", managed_agreement_id=managed_agreement_id)
    agr = rows[0] if rows else {}
    amount = round(float(amount_usd), 2)
    rid = ctx.make_id("mbl_", managed_agreement_id, "managed_billable_labor", ticket_number, "remote_after_hours")
    ctx.create("managed_billing", rid, managed_billing_entry_id=rid, managed_agreement_id=managed_agreement_id,
               customer_id=agr.get("customer_id", ""), event_type="managed_billable_labor", amount_usd=amount,
               invoice_number=invoice_number, billing_period=billing_period, posted_date=ctx.now()[:10],
               managed_seat_change_id=None, ticket_number=ticket_number, labor_class="remote_after_hours",
               billable_minutes=int(billable_minutes), payment_reference="", payment_method="not_applicable",
               original_billing_entry_id=None)
    balance = round(float(agr.get("balance_due_usd") or 0) + amount, 2)
    ctx.update("managed_agreements", managed_agreement_id, balance_due_usd=balance)
    return (f"Remote after-hours labor posted for {ticket_number} on {invoice_number} ({billing_period}): "
            f"{int(billable_minutes)} minutes, {amount:.2f} USD; balance due {balance:.2f} USD.")


@tool(owner="agent", rw="write")
def post_onsite_visit_labor_c7936621(ctx: ToolContext, managed_agreement_id: str, ticket_number: str,
                                     invoice_number: str, billing_period: str, billable_minutes: int,
                                     amount_usd: float) -> str:
    """Bill the onsite business-hours visit of one resolved service desk ticket on a ClearPath invoice.

    The service desk posts one onsite business-hours labor charge for the visit, including any trip charge, onto the
    named monthly invoice, recording the billable minutes and the amount, and adds the amount to what the client owes
    on the agreement. On success the billing ledger shows the visit line on that invoice and the agreement balance
    increases.

    Args:
        managed_agreement_id: Id class — the reference number of the ClearPath agreement the ticket is logged under, as returned by the agreement lookup for the verified client.
        ticket_number: Fixed-format class — the service desk ticket the visit was made on, written SB- followed by 7 digits, exactly as shown in the ticket history.
        invoice_number: Fixed-format class — the monthly invoice the charge is billed on, written INV- followed by 6 digits, exactly as shown on the billing ledger.
        billing_period: Fixed-format class — the month the visit was made, written YYYY-MM (calendar month, US Eastern).
        billable_minutes: Fixed-format class — the minutes billed for the visit, in integer minutes.
        amount_usd: Fixed-format class — the visit amount in US dollars including any trip charge, a positive decimal number with 2 decimal places (cents); the value is stored rounded to the cent.

    Returns:
        A confirmation string with the ticket number, the invoice number, the service month (YYYY-MM), the billable
        minutes, the amount in US dollars with 2 decimals and the agreement's new balance due in US dollars with 2
        decimals; it begins with "Onsite visit labor posted" when the charge is on the ledger.
    """
    rows = ctx.find("managed_agreements", managed_agreement_id=managed_agreement_id)
    agr = rows[0] if rows else {}
    amount = round(float(amount_usd), 2)
    rid = ctx.make_id("mbl_", managed_agreement_id, "managed_billable_labor", ticket_number, "onsite_business_hours")
    ctx.create("managed_billing", rid, managed_billing_entry_id=rid, managed_agreement_id=managed_agreement_id,
               customer_id=agr.get("customer_id", ""), event_type="managed_billable_labor", amount_usd=amount,
               invoice_number=invoice_number, billing_period=billing_period, posted_date=ctx.now()[:10],
               managed_seat_change_id=None, ticket_number=ticket_number, labor_class="onsite_business_hours",
               billable_minutes=int(billable_minutes), payment_reference="", payment_method="not_applicable",
               original_billing_entry_id=None)
    balance = round(float(agr.get("balance_due_usd") or 0) + amount, 2)
    ctx.update("managed_agreements", managed_agreement_id, balance_due_usd=balance)
    return (f"Onsite visit labor posted for {ticket_number} on {invoice_number} ({billing_period}): "
            f"{int(billable_minutes)} minutes, {amount:.2f} USD; balance due {balance:.2f} USD.")


@tool(owner="agent", rw="write")
def post_late_fee_96a9eef8(ctx: ToolContext, managed_agreement_id: str, invoice_number: str, billing_period: str,
                           amount_usd: float) -> str:
    """Assess one late fee on a past-due ClearPath invoice.

    The service desk posts a late fee against the named past-due invoice for the month of assessment and adds it to
    what the client owes on the agreement. On success the billing ledger shows the late fee on that invoice and the
    agreement balance increases by the fee.

    Args:
        managed_agreement_id: Id class — the reference number of the ClearPath agreement the invoice belongs to, as returned by the agreement lookup for the verified client.
        invoice_number: Fixed-format class — the past-due invoice the fee is assessed on, written INV- followed by 6 digits, exactly as shown on the billing ledger.
        billing_period: Fixed-format class — the month of assessment, written YYYY-MM (calendar month, US Eastern).
        amount_usd: Fixed-format class — the late fee in US dollars, a positive decimal number with 2 decimal places (cents); the value is stored rounded to the cent.

    Returns:
        A confirmation string with the invoice number, the month of assessment (YYYY-MM), the late fee in US dollars
        with 2 decimals, the posting date (YYYY-MM-DD) and the agreement's new balance due in US dollars with 2
        decimals; it begins with "Late fee assessed" when the fee is on the ledger.
    """
    rows = ctx.find("managed_agreements", managed_agreement_id=managed_agreement_id)
    agr = rows[0] if rows else {}
    amount = round(float(amount_usd), 2)
    today = ctx.now()[:10]
    rid = ctx.make_id("mbl_", managed_agreement_id, "managed_late_fee", invoice_number, billing_period)
    ctx.create("managed_billing", rid, managed_billing_entry_id=rid, managed_agreement_id=managed_agreement_id,
               customer_id=agr.get("customer_id", ""), event_type="managed_late_fee", amount_usd=amount,
               invoice_number=invoice_number, billing_period=billing_period, posted_date=today,
               managed_seat_change_id=None, ticket_number="", labor_class="not_applicable", billable_minutes=0,
               payment_reference="", payment_method="not_applicable", original_billing_entry_id=None)
    balance = round(float(agr.get("balance_due_usd") or 0) + amount, 2)
    ctx.update("managed_agreements", managed_agreement_id, balance_due_usd=balance)
    return (f"Late fee assessed on {invoice_number} for {billing_period}: {amount:.2f} USD, posted {today}; "
            f"balance due {balance:.2f} USD.")


@tool(owner="user", rw="write")
def sign_tier_upgrade_933f385b(ctx: ToolContext, customer_id: str, managed_agreement_id: str, new_variant_name: str,
                               seat_rate_usd: float, tier_change_effective_date: str) -> str:
    """E-sign, as the client's authorized contact, the amendment moving your ClearPath agreement to a higher tier.

    Your signature records the tier change on the agreement: the agreement's tier becomes the new tier, its per-seat
    rate becomes the rate stated on the amendment, and the date the new tier takes effect is recorded. The term,
    seat commitment, seats covered and balance are left as they are. On success the agreement shows the new tier,
    rate and effective date.

    Args:
        customer_id: Id class — your organisation's client reference number, as read out to you by the agent from the client profile lookup.
        managed_agreement_id: Id class — the reference number of your ClearPath agreement being amended, as read out to you by the agent from the agreement lookup.
        new_variant_name: Enum class — the tier the agreement moves to, written exactly as one of: "ClearPath Monitor" (the monitoring-only tier), "ClearPath Essentials" (the entry help desk tier), "ClearPath Standard" (the tier adding vendor management, included onsite hours and security awareness training), "ClearPath Professional" (the tier adding a named client success manager), "ClearPath Premier" (the 24x7 coverage tier requiring an active Sentinel subscription), "ClearPath Enterprise" (the top tier with a technical account manager).
        seat_rate_usd: Fixed-format class — the new per-seat monthly rate stated on the amendment in US dollars, a decimal number with 2 decimal places (cents); the value is stored rounded to the cent.
        tier_change_effective_date: Fixed-format class — the date the new tier takes effect as stated on the amendment, a calendar date written YYYY-MM-DD (US Eastern business date).

    Returns:
        A confirmation string with the agreement reference, the new tier name, the new per-seat rate in US dollars
        with 2 decimals and the effective date (YYYY-MM-DD); it begins with "Tier upgrade signed" when the change is
        recorded on the agreement.
    """
    rate = round(float(seat_rate_usd), 2)
    ctx.update("managed_agreements", managed_agreement_id, variant_name=new_variant_name, seat_rate_usd=rate,
               tier_change_effective_date=tier_change_effective_date)
    return (f"Tier upgrade signed: agreement {managed_agreement_id} for client {customer_id} moves to "
            f"{new_variant_name} at {rate:.2f} USD per seat, effective {tier_change_effective_date}.")

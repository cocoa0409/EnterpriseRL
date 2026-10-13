"""Hidden task tools of the entrance_fee_contracts_and_refunds difficulty (Entrance Fee Agreements).

Each tool performs one atomic business write on an Entrance Fee Agreement. The tools never check
eligibility, status, timing or any other policy condition and never compute an amount: the figure
passed in is entered exactly as given.
"""

from erlbench import ToolContext, tool


@tool(owner="user", rw="write")
def sign_pre_occupancy_cancellation_25852637(ctx: ToolContext, customer_id: str, entrance_agreement_id: str,
                                              entrance_request_id: str, processing_fee: float) -> str:
    """The resident (or the resident's financial agent) electronically signs the cancellation of an
    Entrance Fee Agreement before occupancy. Signing marks the cancellation request awaiting signature
    as signed, moves the agreement to cancelled status with today's date as its termination date, the
    termination reason pre_occupancy_cancellation and the resident as refund payee, and enters the
    processing fee given here as one processing fee retention entry on the agreement's ledger, lowering
    the refundable balance by that amount. The customer can see the agreement as cancelled and the
    processing fee retained; the receipt confirms both.

    Args:
        customer_id: Id class — the customer reference number of the resident who holds the agreement, read from the customer profile lookup.
        entrance_agreement_id: Id class — the reference number of the Entrance Fee Agreement being cancelled, read from the entrance fee agreement lookup.
        entrance_request_id: Id class — the reference number of the pre-occupancy cancellation request awaiting the customer's signature on that agreement, read from the entrance fee request lookup.
        processing_fee: Fixed-format class — the processing fee retained on this cancellation, in USD, a non-negative amount with 2 decimal places (entered rounded half up to the cent).

    Returns:
        A dictionary rendered as text with: status ("signed"); customer_id (the resident); entrance_agreement_id (the agreement, now cancelled); entrance_request_id (the request, now signed); entrance_entry_id (reference number of the processing fee retention entry); processing_fee (the amount retained, USD with 2 decimal places); refundable_balance (the agreement's refundable balance after the retention, USD with 2 decimal places); termination_date (the cancellation date, YYYY-MM-DD).
    """
    fee = round(float(processing_fee), 2)
    today = ctx.now()[:10]
    agreement = ctx.find("entrance_agreements", entrance_agreement_id=entrance_agreement_id)
    current = float((agreement[0].get("refundable_balance") if agreement else 0) or 0)
    new_balance = round(current - fee, 2)
    ctx.update("entrance_requests", entrance_request_id, request_status="signed")
    ctx.update("entrance_agreements", entrance_agreement_id, status="cancelled", termination_date=today,
               termination_reason="pre_occupancy_cancellation", refund_payee_type="resident",
               refundable_balance=new_balance)
    eid = ctx.make_id("enl_", customer_id, entrance_agreement_id, entrance_request_id, fee)
    ctx.create("entrance_ledger", eid, entrance_entry_id=eid, entrance_agreement_id=entrance_agreement_id,
               customer_id=customer_id, event_type="entrance_processing_fee_retention", amount=fee,
               posting_date=today)
    return str({"status": "signed", "customer_id": customer_id, "entrance_agreement_id": entrance_agreement_id,
                "entrance_request_id": entrance_request_id, "entrance_entry_id": eid,
                "processing_fee": fee, "refundable_balance": new_balance, "termination_date": today})


@tool(owner="agent", rw="write")
def pay_pre_occupancy_refund_45806fa1(ctx: ToolContext, entrance_agreement_id: str, refund_amount: float) -> str:
    """Pay the refund of an Entrance Fee Agreement that was cancelled or rescinded before occupancy.
    One refund payment entry for the amount given is entered on the agreement's ledger, dated today,
    paid by refund check to the payee recorded on the agreement and mailed to the address on file, and
    the refundable balance falls by that amount. The check number is issued by this call and returned
    in the receipt, which the customer can quote when the check arrives.

    Args:
        entrance_agreement_id: Id class — the reference number of the cancelled or rescinded Entrance Fee Agreement being refunded, read from the entrance fee agreement lookup.
        refund_amount: Fixed-format class — the refund paid, in USD, a positive amount with 2 decimal places (entered rounded half up to the cent).

    Returns:
        A dictionary rendered as text with: status ("refund_paid"); entrance_agreement_id; entrance_entry_id (reference number of the refund payment entry); refund_amount (USD with 2 decimal places); payment_reference (the refund check number issued); payment_method ("check"); refund_payee_type (resident or estate, as recorded on the agreement); refundable_balance (the balance left on the agreement, USD with 2 decimal places).
    """
    amount = round(float(refund_amount), 2)
    today = ctx.now()[:10]
    agreement = ctx.find("entrance_agreements", entrance_agreement_id=entrance_agreement_id)
    row = agreement[0] if agreement else {}
    current = float(row.get("refundable_balance") or 0)
    payee = row.get("refund_payee_type") or "resident"
    new_balance = round(current - amount, 2)
    eid = ctx.make_id("enl_", entrance_agreement_id, amount)
    reference = "RFCK-" + eid[-6:].upper()
    ctx.create("entrance_ledger", eid, entrance_entry_id=eid, entrance_agreement_id=entrance_agreement_id,
               customer_id=row.get("customer_id", ""), event_type="entrance_refund_payment", amount=amount,
               posting_date=today, payment_reference=reference, payment_method="check",
               refund_payee_type=payee)
    ctx.update("entrance_agreements", entrance_agreement_id, refundable_balance=new_balance)
    return str({"status": "refund_paid", "entrance_agreement_id": entrance_agreement_id,
                "entrance_entry_id": eid, "refund_amount": amount, "payment_reference": reference,
                "payment_method": "check", "refund_payee_type": payee, "refundable_balance": new_balance})


@tool(owner="agent", rw="write")
def book_final_period_amortization_cad149c9(ctx: ToolContext, entrance_agreement_id: str, amortization_month: int,
                                            month_start_date: str, amortization_amount: float) -> str:
    """Enter one amortization entry on an Entrance Fee Agreement for a month of occupancy that has no
    amortization entry yet. The entry carries the month's sequence number and its first day as the
    posting date, and the refundable balance of the agreement falls by the amount given; the agreement's
    status is left as it is. The receipt shows the new entry and the balance after it.

    Args:
        entrance_agreement_id: Id class — the reference number of the Entrance Fee Agreement amortized, read from the entrance fee agreement lookup.
        amortization_month: Fixed-format class — the sequence number of the month of occupancy amortized, an integer counted from 1 for the month beginning on the occupancy date.
        month_start_date: Fixed-format class — the first day of that month of occupancy, in YYYY-MM-DD format, entered as the posting date.
        amortization_amount: Fixed-format class — the amount amortized, in USD, a non-negative amount with 2 decimal places (entered rounded half up to the cent).

    Returns:
        A dictionary rendered as text with: status ("amortized"); entrance_agreement_id; entrance_entry_id (reference number of the amortization entry); amortization_month (integer); posting_date (YYYY-MM-DD); amount (USD with 2 decimal places); refundable_balance (the balance after the entry, USD with 2 decimal places).
    """
    amount = round(float(amortization_amount), 2)
    month = int(amortization_month)
    agreement = ctx.find("entrance_agreements", entrance_agreement_id=entrance_agreement_id)
    row = agreement[0] if agreement else {}
    new_balance = round(float(row.get("refundable_balance") or 0) - amount, 2)
    eid = ctx.make_id("enl_", entrance_agreement_id, month, month_start_date, amount)
    ctx.create("entrance_ledger", eid, entrance_entry_id=eid, entrance_agreement_id=entrance_agreement_id,
               customer_id=row.get("customer_id", ""), event_type="entrance_amortization", amount=amount,
               posting_date=month_start_date, amortization_month=month)
    ctx.update("entrance_agreements", entrance_agreement_id, refundable_balance=new_balance)
    return str({"status": "amortized", "entrance_agreement_id": entrance_agreement_id, "entrance_entry_id": eid,
                "amortization_month": month, "posting_date": month_start_date, "amount": amount,
                "refundable_balance": new_balance})


@tool(owner="agent", rw="write")
def issue_annual_tax_letter_ce10c97a(ctx: ToolContext, entrance_agreement_id: str, tax_year: str,
                                     medical_expense_amount: float) -> str:
    """Issue the annual tax letter of an Entrance Fee Agreement for one tax year. One tax letter entry
    stating the medical expense amount given is entered on the agreement's ledger, dated today and
    marked with the tax year; the refundable balance is not changed. The letter is sent to the mailing
    address on file and the receipt confirms what it states.

    Args:
        entrance_agreement_id: Id class — the reference number of the Entrance Fee Agreement the letter is issued for, read from the entrance fee agreement lookup.
        tax_year: Fixed-format class — the tax year the letter covers, four digits in YYYY format.
        medical_expense_amount: Fixed-format class — the medical expense amount the letter states, in USD, a non-negative amount with 2 decimal places (entered rounded half up to the cent).

    Returns:
        A dictionary rendered as text with: status ("letter_issued"); entrance_agreement_id; entrance_entry_id (reference number of the tax letter entry); tax_year (YYYY); medical_expense_amount (USD with 2 decimal places); issue_date (YYYY-MM-DD).
    """
    amount = round(float(medical_expense_amount), 2)
    today = ctx.now()[:10]
    agreement = ctx.find("entrance_agreements", entrance_agreement_id=entrance_agreement_id)
    row = agreement[0] if agreement else {}
    eid = ctx.make_id("enl_", entrance_agreement_id, tax_year, amount)
    ctx.create("entrance_ledger", eid, entrance_entry_id=eid, entrance_agreement_id=entrance_agreement_id,
               customer_id=row.get("customer_id", ""), event_type="entrance_tax_letter", amount=amount,
               posting_date=today, tax_year=str(tax_year))
    return str({"status": "letter_issued", "entrance_agreement_id": entrance_agreement_id, "entrance_entry_id": eid,
                "tax_year": str(tax_year), "medical_expense_amount": amount, "issue_date": today})


@tool(owner="agent", rw="write")
def issue_closing_year_tax_letter_050bd78c(ctx: ToolContext, entrance_agreement_id: str, tax_year: str,
                                           medical_expense_amount: float) -> str:
    """Issue the closing-year tax letter of an Entrance Fee Agreement that ended, for the tax year in
    which it ended. One tax letter entry stating the medical expense amount given is entered on the
    agreement's ledger, dated today and marked with that tax year; the refundable balance is not changed.
    The letter is sent to the mailing address on file and the receipt confirms what it states.

    Args:
        entrance_agreement_id: Id class — the reference number of the ended Entrance Fee Agreement the letter is issued for, read from the entrance fee agreement lookup.
        tax_year: Fixed-format class — the tax year in which the agreement ended, four digits in YYYY format.
        medical_expense_amount: Fixed-format class — the medical expense amount the letter states, in USD, a non-negative amount with 2 decimal places (entered rounded half up to the cent).

    Returns:
        A dictionary rendered as text with: status ("closing_letter_issued"); entrance_agreement_id; entrance_entry_id (reference number of the tax letter entry); tax_year (YYYY); medical_expense_amount (USD with 2 decimal places); issue_date (YYYY-MM-DD).
    """
    amount = round(float(medical_expense_amount), 2)
    today = ctx.now()[:10]
    agreement = ctx.find("entrance_agreements", entrance_agreement_id=entrance_agreement_id)
    row = agreement[0] if agreement else {}
    eid = ctx.make_id("enl_", entrance_agreement_id, tax_year, amount, "closing")
    ctx.create("entrance_ledger", eid, entrance_entry_id=eid, entrance_agreement_id=entrance_agreement_id,
               customer_id=row.get("customer_id", ""), event_type="entrance_tax_letter", amount=amount,
               posting_date=today, tax_year=str(tax_year))
    return str({"status": "closing_letter_issued", "entrance_agreement_id": entrance_agreement_id,
                "entrance_entry_id": eid, "tax_year": str(tax_year), "medical_expense_amount": amount,
                "issue_date": today})


@tool(owner="user", rw="write")
def release_estate_refund_4b5e42b1(ctx: ToolContext, entrance_agreement_id: str, refund_amount: float) -> str:
    """The estate's personal representative electronically signs the refund release of an Entrance Fee
    Agreement whose refund is scheduled. Signing releases one refund payment for the amount given, paid
    by check to the estate in care of the mailing address on file and entered on the agreement's ledger
    dated today; the refundable balance falls by that amount and the agreement is closed with today's
    date. The receipt carries the refund check number.

    Args:
        entrance_agreement_id: Id class — the reference number of the Entrance Fee Agreement whose refund is released, read from the entrance fee agreement lookup.
        refund_amount: Fixed-format class — the refund released to the estate, in USD, a positive amount with 2 decimal places (entered rounded half up to the cent).

    Returns:
        A dictionary rendered as text with: status ("released"); entrance_agreement_id; entrance_entry_id (reference number of the refund payment entry); refund_amount (USD with 2 decimal places); payment_reference (the refund check number issued); payment_method ("check"); refund_payee_type ("estate"); refundable_balance (the balance after the payment, USD with 2 decimal places); closed_date (YYYY-MM-DD).
    """
    amount = round(float(refund_amount), 2)
    today = ctx.now()[:10]
    agreement = ctx.find("entrance_agreements", entrance_agreement_id=entrance_agreement_id)
    row = agreement[0] if agreement else {}
    new_balance = round(float(row.get("refundable_balance") or 0) - amount, 2)
    eid = ctx.make_id("enl_", entrance_agreement_id, amount, "estate")
    reference = "RFCK-" + eid[-6:].upper()
    ctx.create("entrance_ledger", eid, entrance_entry_id=eid, entrance_agreement_id=entrance_agreement_id,
               customer_id=row.get("customer_id", ""), event_type="entrance_refund_payment", amount=amount,
               posting_date=today, payment_reference=reference, payment_method="check", refund_payee_type="estate")
    ctx.update("entrance_agreements", entrance_agreement_id, refundable_balance=new_balance, status="closed",
               closed_date=today)
    return str({"status": "released", "entrance_agreement_id": entrance_agreement_id, "entrance_entry_id": eid,
                "refund_amount": amount, "payment_reference": reference, "payment_method": "check",
                "refund_payee_type": "estate", "refundable_balance": new_balance, "closed_date": today})

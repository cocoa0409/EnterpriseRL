"""Hidden task tools of the rental_reimbursement_claims difficulty (Cardinal Rental Reimbursement).
Path: env/env_0035_personal_auto_insurance_carrier/tasks/rental_reimbursement_claims/task_tools.py

Each tool performs one atomic write on the rental claim ledger of one rental reimbursement option and never
judges eligibility, prerequisites or amounts: every figure it receives was worked out by the caller.
"""

from erlbench import ToolContext, tool


@tool(owner="agent", rw="write")
def extend_rental_authorization_97458fea(ctx: ToolContext, rental_coverage_id: str, customer_id: str,
                                         claim_number: str, authorization_number: str,
                                         extension_sequence: int, authorized_days: int,
                                         extension_reason: str) -> str:
    """Add rental days to a rental authorization that is already open on a physical damage claim. One call
    records one extension of that authorization on the rental claim ledger of the customer's rental
    reimbursement option, with the number of days added, its sequence number on the authorization and the
    reason it was granted; the days added become part of the days authorized for that rental from the moment
    the extension is recorded, and the rental agency and the customer can be told the new covered period.

    Args:
        rental_coverage_id: Id class — the reference number of the rental reimbursement option the rental is
            paid under, as shown by the rental option lookup for the damaged vehicle.
        customer_id: Id class — the customer reference number of the named insured, as returned by the
            customer profile lookup.
        claim_number: Id class — the physical damage claim number of the loss (for example the number shown on
            the claim entries and rental entries of that loss), read from the claim or rental ledger lookup.
        authorization_number: Id class — the rental authorization number of the open rental being extended, as
            shown on its authorization entry in the rental ledger lookup or on the receipt that recorded it.
        extension_sequence: Fixed-format class — the sequence number of this extension on the authorization:
            1 for the first extension of that authorization, then 2, 3 and so on; integer >= 1.
        authorized_days: Fixed-format class — the number of rental days this extension adds to the
            authorization, as a whole number; integer days.
        extension_reason: Enum class — why the extension is granted:
            shop_new_completion_date when the repair shop has confirmed a new completion date for the repair;
            parts_delay when the repair shop has documented that parts for the repair are delayed or backordered.

    Returns:
        A text rendering of a dictionary with these fields: status — the word "extended" when the extension was
        recorded; rental_entry_id — the reference number of the new extension entry on the rental ledger;
        authorization_number — the authorization that was extended; extension_sequence — the sequence number
        recorded (integer); authorized_days — the days added (integer); entry_date — the date the extension was
        recorded, YYYY-MM-DD.
    """
    rid = ctx.make_id("rle_", rental_coverage_id, customer_id, claim_number, authorization_number,
                      extension_sequence, authorized_days, extension_reason)
    ctx.create("rental_ledger", rid, rental_entry_id=rid, rental_coverage_id=rental_coverage_id,
               customer_id=customer_id, event_type="rental_extension", claim_number=claim_number,
               authorization_number=authorization_number, extension_sequence=int(extension_sequence),
               authorized_days=int(authorized_days), extension_reason=extension_reason,
               entry_date=ctx.now()[:10])
    return str({"status": "extended", "rental_entry_id": rid, "authorization_number": authorization_number,
                "extension_sequence": int(extension_sequence), "authorized_days": int(authorized_days),
                "entry_date": ctx.now()[:10]})


@tool(owner="user", rw="write")
def accept_upgraded_rental_aa4639f2(ctx: ToolContext, rental_coverage_id: str, customer_id: str,
                                    claim_number: str, vehicle_class: str, start_date: str,
                                    daily_rate: float, authorized_days: int) -> str:
    """The named insured personally accepts a partner-agency rental car of a larger class than the one Cardinal
    reserves under direct billing, agreeing to pay the agency the difference above what the option pays. One
    call records the rental authorization of that car on the claim's rental ledger as a Cardinal partner
    direct-bill rental, with the car class taken, the pickup date, the agency's daily rate and the number of
    rental days authorized, and issues a new rental authorization number that the customer and the agency
    use for that rental from then on.

    Args:
        rental_coverage_id: Id class — the reference number of the rental reimbursement option the rental is
            paid under, as given to the customer by the representative from the rental option lookup.
        customer_id: Id class — the customer reference number of the named insured, as given to the customer
            by the representative from the profile lookup.
        claim_number: Id class — the physical damage claim number of the loss the rental is for, as given to
            the customer by the representative from the claim lookup.
        vehicle_class: Enum class — the car class the customer is taking from the partner agency:
            economy for an economy car; compact for a compact car; intermediate for an intermediate car;
            standard for a standard-size car; full_size for a full-size car; standard_suv for a standard SUV;
            minivan for a minivan; premium for a premium car.
        start_date: Fixed-format class — the date the customer picked the rental car up from the agency, as
            printed on the rental agreement, written YYYY-MM-DD.
        daily_rate: Fixed-format class — the agency's daily rate for the car taken, taxes and fees included, as
            printed on the rental agreement; USD, 2 decimal places.
        authorized_days: Fixed-format class — the number of rental days the authorization covers, as a whole
            number; integer days.

    Returns:
        A text rendering of a dictionary with these fields: status — the word "accepted" when the authorization
        was recorded; authorization_number — the new rental authorization number issued for this rental;
        rental_entry_id — the reference number of the authorization entry on the rental ledger; vehicle_class —
        the class recorded; start_date — the pickup date recorded, YYYY-MM-DD; daily_rate — the agency daily rate
        recorded, USD with 2 decimal places; authorized_days — the days authorized (integer).
    """
    auth_no = "RA-" + ctx.make_id("", rental_coverage_id, claim_number, vehicle_class, start_date,
                                  round(float(daily_rate), 2), authorized_days, length=8).upper()
    rid = ctx.make_id("rla_", rental_coverage_id, customer_id, claim_number, vehicle_class, start_date,
                      round(float(daily_rate), 2), authorized_days)
    ctx.create("rental_ledger", rid, rental_entry_id=rid, rental_coverage_id=rental_coverage_id,
               customer_id=customer_id, event_type="rental_authorization", claim_number=claim_number,
               authorization_number=auth_no, vendor_type="partner_direct_bill", vehicle_class=vehicle_class,
               start_date=start_date, authorized_days=int(authorized_days),
               daily_rate=round(float(daily_rate), 2), entry_date=ctx.now()[:10])
    return str({"status": "accepted", "authorization_number": auth_no, "rental_entry_id": rid,
                "vehicle_class": vehicle_class, "start_date": start_date,
                "daily_rate": round(float(daily_rate), 2), "authorized_days": int(authorized_days)})


@tool(owner="agent", rw="write")
def pay_partner_rental_invoice_bf34992c(ctx: ToolContext, rental_coverage_id: str, customer_id: str,
                                        claim_number: str, authorization_number: str, invoice_number: str,
                                        days_billed: int, daily_rate: float, amount: float) -> str:
    """Pay a Cardinal partner rental agency's direct-bill invoice for a rental on a physical damage claim. One
    call records one agency payment on the claim's rental ledger for the given invoice: the invoice number,
    the rental days and the daily rate the invoice bills, and the amount Cardinal pays the agency; the paid
    amount is added to the rental benefit paid on the option, and the agency can be told the invoice is paid.

    Args:
        rental_coverage_id: Id class — the reference number of the rental reimbursement option the rental is
            paid under, as shown by the rental option lookup for the damaged vehicle.
        customer_id: Id class — the customer reference number of the named insured, as returned by the
            customer profile lookup.
        claim_number: Id class — the physical damage claim number of the loss, read from the claim or rental
            ledger lookup.
        authorization_number: Id class — the rental authorization number the invoice bills, as shown on that
            authorization's entries in the rental ledger lookup.
        invoice_number: Verbatim class — the agency invoice number exactly as printed on the invoice or on the
            closing copy the customer reads out; copy it character for character, keeping every letter, digit
            and hyphen, with no reformatting (verbatim).
        days_billed: Fixed-format class — the number of rental days the invoice bills, as printed on it;
            integer days.
        daily_rate: Fixed-format class — the daily rate the invoice bills, taxes and fees included, as printed
            on it; USD, 2 decimal places.
        amount: Fixed-format class — the amount Cardinal pays the agency on this invoice; USD, 2 decimal
            places, positive.

    Returns:
        A text rendering of a dictionary with these fields: status — the word "paid" when the payment was
        recorded; rental_entry_id — the reference number of the agency payment entry; invoice_number — the
        invoice paid; amount — the amount paid, USD with 2 decimal places; entry_date — the payment date,
        YYYY-MM-DD.
    """
    rid = ctx.make_id("rlv_", rental_coverage_id, customer_id, claim_number, authorization_number,
                      invoice_number, days_billed, round(float(daily_rate), 2), round(float(amount), 2))
    ctx.create("rental_ledger", rid, rental_entry_id=rid, rental_coverage_id=rental_coverage_id,
               customer_id=customer_id, event_type="rental_vendor_payment", claim_number=claim_number,
               authorization_number=authorization_number, invoice_number=invoice_number,
               days_billed=int(days_billed), daily_rate=round(float(daily_rate), 2),
               amount=round(float(amount), 2), entry_date=ctx.now()[:10])
    return str({"status": "paid", "rental_entry_id": rid, "invoice_number": invoice_number,
                "amount": round(float(amount), 2), "entry_date": ctx.now()[:10]})


@tool(owner="user", rw="write")
def submit_rideshare_receipts_3a988a26(ctx: ToolContext, rental_coverage_id: str, customer_id: str,
                                       claim_number: str, authorization_number: str,
                                       receipt_reference: str, days_billed: int, amount: float) -> str:
    """The named insured personally submits the rideshare, taxi or transit receipts they paid for during a
    rideshare authorization on a physical damage claim and accepts the reimbursement quoted for them. One
    call records one reimbursement to the customer on the claim's rental ledger for that submission, with
    the receipt reference, the number of days the receipts cover and the amount reimbursed; the amount is
    added to the rental benefit paid on the option and the customer is told the reimbursement is issued.

    Args:
        rental_coverage_id: Id class — the reference number of the rental reimbursement option, as given to the
            customer by the representative from the rental option lookup.
        customer_id: Id class — the customer reference number of the named insured, as given to the customer
            by the representative from the profile lookup.
        claim_number: Id class — the physical damage claim number of the loss, as given to the customer by the
            representative from the claim lookup.
        authorization_number: Id class — the rideshare authorization number the receipts fall under, as given
            to the customer by the representative from the rental ledger lookup.
        receipt_reference: Verbatim class — the reference printed on the customer's receipt summary for this
            submission, exactly as the customer reads it out; copy it character for character, keeping every
            letter, digit and hyphen, with no reformatting (verbatim).
        days_billed: Fixed-format class — the number of days the submitted receipts cover, as counted on the
            customer's receipts; integer days.
        amount: Fixed-format class — the reimbursement amount quoted to the customer for this submission; USD,
            2 decimal places, positive.

    Returns:
        A text rendering of a dictionary with these fields: status — the word "reimbursed" when the
        reimbursement was recorded; rental_entry_id — the reference number of the reimbursement entry;
        receipt_reference — the receipt reference recorded; amount — the amount reimbursed, USD with 2 decimal
        places; entry_date — the reimbursement date, YYYY-MM-DD.
    """
    rid = ctx.make_id("rlr_", rental_coverage_id, customer_id, claim_number, authorization_number,
                      receipt_reference, days_billed, round(float(amount), 2))
    ctx.create("rental_ledger", rid, rental_entry_id=rid, rental_coverage_id=rental_coverage_id,
               customer_id=customer_id, event_type="rental_reimbursement_payment", claim_number=claim_number,
               authorization_number=authorization_number, receipt_reference=receipt_reference,
               vendor_type="rideshare_taxi_transit", days_billed=int(days_billed),
               amount=round(float(amount), 2), entry_date=ctx.now()[:10])
    return str({"status": "reimbursed", "rental_entry_id": rid, "receipt_reference": receipt_reference,
                "amount": round(float(amount), 2), "entry_date": ctx.now()[:10]})


@tool(owner="agent", rw="write")
def record_agency_overbilling_credit_d02c6cb6(ctx: ToolContext, rental_coverage_id: str, customer_id: str,
                                              claim_number: str, source_entry_id: str, amount: float) -> str:
    """Record a credit a Cardinal partner rental agency gives back against one agency payment it overbilled on a
    physical damage claim. One call records one agency-credit recovery on the claim's rental ledger, tied to the
    agency payment it is taken against; the credited amount is taken off the rental benefit paid on the option
    and given back to the claim's per-loss benefit, and the agency's account shows the credit.

    Args:
        rental_coverage_id: Id class — the reference number of the rental reimbursement option the payment was
            made under, as shown by the rental option lookup for the damaged vehicle.
        customer_id: Id class — the customer reference number of the named insured, as returned by the
            customer profile lookup.
        claim_number: Id class — the physical damage claim number of the loss, read from the claim or rental
            ledger lookup.
        source_entry_id: Id class — the reference number of the agency payment entry the credit is taken
            against, as shown on that payment in the rental ledger lookup.
        amount: Fixed-format class — the amount the agency credits back; USD, 2 decimal places, positive.

    Returns:
        A text rendering of a dictionary with these fields: status — the word "credited" when the credit was
        recorded; rental_entry_id — the reference number of the credit entry; source_entry_id — the agency
        payment it is taken against; amount — the amount credited, USD with 2 decimal places; entry_date — the
        date recorded, YYYY-MM-DD.
    """
    rid = ctx.make_id("rlc_", rental_coverage_id, customer_id, claim_number, source_entry_id,
                      round(float(amount), 2))
    ctx.create("rental_ledger", rid, rental_entry_id=rid, rental_coverage_id=rental_coverage_id,
               customer_id=customer_id, event_type="rental_payment_recovery", claim_number=claim_number,
               source_entry_id=source_entry_id, recovery_source="vendor_credit",
               amount=round(float(amount), 2), entry_date=ctx.now()[:10])
    return str({"status": "credited", "rental_entry_id": rid, "source_entry_id": source_entry_id,
                "amount": round(float(amount), 2), "entry_date": ctx.now()[:10]})


@tool(owner="user", rw="write")
def submit_own_rental_receipts_258c32b3(ctx: ToolContext, rental_coverage_id: str, customer_id: str,
                                        claim_number: str, authorization_number: str,
                                        receipt_reference: str, days_billed: int, amount: float) -> str:
    """The named insured personally submits the receipts of a rental car they arranged and paid for themselves at
    an agency outside Cardinal's partner network on a physical damage claim, and accepts the reimbursement
    quoted for them. One call records one reimbursement to the customer on the claim's rental ledger for that
    submission, with the receipt reference, the number of rental days on the receipts and the amount
    reimbursed; the amount is added to the rental benefit paid on the option and the customer is told the
    reimbursement is issued.

    Args:
        rental_coverage_id: Id class — the reference number of the rental reimbursement option, as given to the
            customer by the representative from the rental option lookup.
        customer_id: Id class — the customer reference number of the named insured, as given to the customer
            by the representative from the profile lookup.
        claim_number: Id class — the physical damage claim number of the loss, as given to the customer by the
            representative from the claim lookup.
        authorization_number: Id class — the authorization number of the rental the customer arranged, as given
            to the customer by the representative from the rental ledger lookup.
        receipt_reference: Verbatim class — the rental agreement or receipt number printed on the agency's
            receipt, exactly as the customer reads it out; copy it character for character, keeping every letter,
            digit and hyphen, with no reformatting (verbatim).
        days_billed: Fixed-format class — the number of rental days the agency's receipt bills, as printed on
            it; integer days.
        amount: Fixed-format class — the reimbursement amount quoted to the customer for this submission; USD,
            2 decimal places, positive.

    Returns:
        A text rendering of a dictionary with these fields: status — the word "reimbursed" when the
        reimbursement was recorded; rental_entry_id — the reference number of the reimbursement entry;
        receipt_reference — the receipt reference recorded; amount — the amount reimbursed, USD with 2 decimal
        places; entry_date — the reimbursement date, YYYY-MM-DD.
    """
    rid = ctx.make_id("rlo_", rental_coverage_id, customer_id, claim_number, authorization_number,
                      receipt_reference, days_billed, round(float(amount), 2))
    ctx.create("rental_ledger", rid, rental_entry_id=rid, rental_coverage_id=rental_coverage_id,
               customer_id=customer_id, event_type="rental_reimbursement_payment", claim_number=claim_number,
               authorization_number=authorization_number, receipt_reference=receipt_reference,
               vendor_type="other_agency", days_billed=int(days_billed),
               amount=round(float(amount), 2), entry_date=ctx.now()[:10])
    return str({"status": "reimbursed", "rental_entry_id": rid, "receipt_reference": receipt_reference,
                "amount": round(float(amount), 2), "entry_date": ctx.now()[:10]})

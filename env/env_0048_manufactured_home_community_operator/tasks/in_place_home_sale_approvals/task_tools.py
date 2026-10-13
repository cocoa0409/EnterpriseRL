"""Hidden task tools for the in_place_home_sale_approvals difficulty (category: resale).

Each tool performs one atomic posting on an in-place resale file and is reached only through
the unlock/call meta-tools; its name is published solely as an extended policy's target tool.
No tool judges eligibility, prerequisites or amounts: the caller passes the values the
published policies fix, and the tool lands them as given.
"""

from erlbench import ToolContext, tool


@tool(owner="agent", rw="write")
def post_inspection_fee_534473a1(ctx: ToolContext, resale_id: str, inspection_record_id: str,
                                 charge_date: str, amount: float) -> str:
    """Post the charge for a resale file's initial pre-sale community-standards inspection.

    The resident desk uses this to bill the seller for one initial inspection already recorded on
    the file. One call adds one inspection-fee charge to the file's ledger, tied to that inspection
    record and dated as given, and raises the fees the seller owes on the file by the amount. The
    seller sees the inspection fee among the file's charges and a higher fees-owed figure.

    Args:
        resale_id: Id class — the resale file number of the home being sold, as shown on the seller's
            resale file in the in-place resale file lookup.
        inspection_record_id: Id class — the reference number of the initial inspection record being
            billed, as listed among the file's records in the resale record lookup.
        charge_date: Fixed-format class — the date the charge is dated on the file, written
            YYYY-MM-DD (calendar date, no time part, no time zone).
        amount: Fixed-format class — the inspection fee charged, in USD as a positive number with
            2 decimal places, already rounded half up to the cent; it is stored exactly as passed.

    Returns:
        A dictionary rendered as text with these fields: status (the text "posted" when the
        charge was added), resale_entry_id (reference number of the new ledger charge, text),
        resale_id (the file charged, text), charge_type (always "inspection_fee"),
        source_entry_id (the inspection record the charge is tied to, text), entry_date (the
        charge date, YYYY-MM-DD), amount (the charge in USD with 2 decimal places) and
        fees_balance (the fees owed on the file including this charge, USD with 2 decimal places).
    """
    amt = round(float(amount), 2)
    listing = (ctx.find("resale_listings", resale_id=resale_id) or [{}])[0]
    rid = ctx.make_id("rsl_", resale_id, inspection_record_id, charge_date, amt)
    ctx.create("resale_ledger", rid, resale_entry_id=rid, resale_id=resale_id,
               customer_id=listing.get("customer_id"), event_type="resale_fee_charge",
               entry_date=charge_date, charge_type="inspection_fee",
               source_entry_id=inspection_record_id, amount=amt)
    balance = round(float(listing.get("fees_balance") or 0) + amt, 2)
    ctx.update("resale_listings", resale_id, fees_balance=balance)
    return str({"status": "posted", "resale_entry_id": rid, "resale_id": resale_id,
                "charge_type": "inspection_fee", "source_entry_id": inspection_record_id,
                "entry_date": charge_date, "amount": amt, "fees_balance": balance})


@tool(owner="agent", rw="write")
def post_vacant_home_check_55c2c08b(ctx: ToolContext, resale_id: str, billing_period: str,
                                    charge_date: str, amount: float) -> str:
    """Post the vacant-home check charge for one calendar month on a resale file.

    The resident desk uses this to bill the seller for the required check of a home standing
    vacant while it is for sale. One call adds one vacant-home check charge for the month given to
    the file's ledger, dated as given, and raises the fees the seller owes on the file by the
    amount. The seller sees that month's check among the file's charges and a higher
    fees-owed figure.

    Args:
        resale_id: Id class — the resale file number of the home being sold, as shown on the seller's
            resale file in the in-place resale file lookup.
        billing_period: Fixed-format class — the calendar month the check covers, written YYYY-MM
            (four-digit year, two-digit month).
        charge_date: Fixed-format class — the date the charge is dated on the file, written
            YYYY-MM-DD (calendar date, no time part, no time zone).
        amount: Fixed-format class — the month's check charge, in USD as a positive number with
            2 decimal places, already rounded half up to the cent; it is stored exactly as passed.

    Returns:
        A dictionary rendered as text with these fields: status (the text "posted" when the
        charge was added), resale_entry_id (reference number of the new ledger charge, text),
        resale_id (the file charged, text), charge_type (always "vacant_home_check"),
        billing_period (the month covered, YYYY-MM), entry_date (the charge date, YYYY-MM-DD),
        amount (the charge in USD with 2 decimal places) and fees_balance (the fees owed on the
        file including this charge, USD with 2 decimal places).
    """
    amt = round(float(amount), 2)
    listing = (ctx.find("resale_listings", resale_id=resale_id) or [{}])[0]
    rid = ctx.make_id("rsl_", resale_id, billing_period, charge_date, amt)
    ctx.create("resale_ledger", rid, resale_entry_id=rid, resale_id=resale_id,
               customer_id=listing.get("customer_id"), event_type="resale_fee_charge",
               entry_date=charge_date, charge_type="vacant_home_check",
               billing_period=billing_period, amount=amt)
    balance = round(float(listing.get("fees_balance") or 0) + amt, 2)
    ctx.update("resale_listings", resale_id, fees_balance=balance)
    return str({"status": "posted", "resale_entry_id": rid, "resale_id": resale_id,
                "charge_type": "vacant_home_check", "billing_period": billing_period,
                "entry_date": charge_date, "amount": amt, "fees_balance": balance})


@tool(owner="user", rw="write")
def pay_reinspection_booking_26088ed0(ctx: ToolContext, resale_id: str, amount: float,
                                      payment_channel: str) -> str:
    """Pay, as the seller, the payment that books a re-inspection of the home on a resale file.

    The seller uses this to make a payment on their own resale file on the spot. One call records
    one payment received today on the file's ledger through the channel chosen, issues a
    processor confirmation number for it, and lowers the fees owed on the file by the amount (a
    figure below zero is a credit held on the file). The seller sees the payment and its
    confirmation number on the file.

    Args:
        resale_id: Id class — the resale file number of the seller's home, as read to the seller
            from the in-place resale file lookup.
        amount: Fixed-format class — the payment amount, in USD as a positive number with 2 decimal
            places, already rounded half up to the cent; it is recorded exactly as passed.
        payment_channel: Enum class — how the payment is made, one of: online_portal_ach when the
            seller pays from a bank account through the resident portal; online_portal_card when
            the seller pays with a debit or credit card through the resident portal;
            office_money_order when the seller hands a money order to the community office;
            office_cashiers_check when the seller hands a cashier's check to the community office;
            office_personal_check when the seller hands a personal check to the community office.

    Returns:
        A dictionary rendered as text with these fields: status (the text "paid" when the
        payment was recorded), resale_entry_id (reference number of the new ledger payment,
        text), resale_id (the file credited, text), entry_date (date received, YYYY-MM-DD),
        amount (the payment in USD with 2 decimal places), payment_channel (the channel used),
        payment_ref (the processor confirmation number issued for this payment, text) and
        fees_balance (the fees owed on the file net of this payment, USD with 2 decimal places;
        below zero means a credit is held).
    """
    amt = round(float(amount), 2)
    listing = (ctx.find("resale_listings", resale_id=resale_id) or [{}])[0]
    today = ctx.now()[:10]
    rid = ctx.make_id("rsl_", resale_id, amt, payment_channel, today)
    ref = "HHS" + ctx.make_id("", resale_id, amt, payment_channel, today, length=10).upper()
    ctx.create("resale_ledger", rid, resale_entry_id=rid, resale_id=resale_id,
               customer_id=listing.get("customer_id"), event_type="resale_fee_payment",
               entry_date=today, amount=amt, payment_channel=payment_channel, payment_ref=ref)
    balance = round(float(listing.get("fees_balance") or 0) - amt, 2)
    ctx.update("resale_listings", resale_id, fees_balance=balance)
    return str({"status": "paid", "resale_entry_id": rid, "resale_id": resale_id,
                "entry_date": today, "amount": amt, "payment_channel": payment_channel,
                "payment_ref": ref, "fees_balance": balance})


@tool(owner="agent", rw="write")
def post_appraisal_fee_5faa8f88(ctx: ToolContext, resale_id: str, appraisal_record_id: str,
                                charge_date: str, amount: float) -> str:
    """Post the charge for an independent appraisal recorded on a guaranteed-program resale file.

    The resident desk uses this to bill the seller for one appraisal already recorded on the file.
    One call adds one appraisal-fee charge to the file's ledger, tied to that appraisal record and
    dated as given, and raises the fees the seller owes on the file by the amount. The seller
    sees the appraisal fee among the file's charges and a higher fees-owed figure.

    Args:
        resale_id: Id class — the resale file number of the home being sold, as shown on the seller's
            resale file in the in-place resale file lookup.
        appraisal_record_id: Id class — the reference number of the appraisal record being billed,
            as listed among the file's records in the resale record lookup.
        charge_date: Fixed-format class — the date the charge is dated on the file, written
            YYYY-MM-DD (calendar date, no time part, no time zone).
        amount: Fixed-format class — the appraisal fee charged, in USD as a positive number with
            2 decimal places, already rounded half up to the cent; it is stored exactly as passed.

    Returns:
        A dictionary rendered as text with these fields: status (the text "posted" when the
        charge was added), resale_entry_id (reference number of the new ledger charge, text),
        resale_id (the file charged, text), charge_type (always "appraisal_fee"),
        source_entry_id (the appraisal record the charge is tied to, text), entry_date (the
        charge date, YYYY-MM-DD), amount (the charge in USD with 2 decimal places) and
        fees_balance (the fees owed on the file including this charge, USD with 2 decimal places).
    """
    amt = round(float(amount), 2)
    listing = (ctx.find("resale_listings", resale_id=resale_id) or [{}])[0]
    rid = ctx.make_id("rsl_", resale_id, appraisal_record_id, charge_date, amt)
    ctx.create("resale_ledger", rid, resale_entry_id=rid, resale_id=resale_id,
               customer_id=listing.get("customer_id"), event_type="resale_fee_charge",
               entry_date=charge_date, charge_type="appraisal_fee",
               source_entry_id=appraisal_record_id, amount=amt)
    balance = round(float(listing.get("fees_balance") or 0) + amt, 2)
    ctx.update("resale_listings", resale_id, fees_balance=balance)
    return str({"status": "posted", "resale_entry_id": rid, "resale_id": resale_id,
                "charge_type": "appraisal_fee", "source_entry_id": appraisal_record_id,
                "entry_date": charge_date, "amount": amt, "fees_balance": balance})


@tool(owner="user", rw="write")
def set_asking_price_9cfe4b28(ctx: ToolContext, resale_id: str, new_list_price: float) -> str:
    """Change, as the seller, the asking price of the home listed on a resale file.

    The seller uses this to sign a new asking price for their own listed home on the spot. One call
    replaces the file's current asking price with the new one; the listing dates, the term and
    everything else on the file stay as they were. The seller sees the new asking price on
    the file and on the listing.

    Args:
        resale_id: Id class — the resale file number of the seller's listed home, as read to the
            seller from the in-place resale file lookup.
        new_list_price: Fixed-format class — the new asking price, in USD as a positive number with
            2 decimal places; it is recorded exactly as passed.

    Returns:
        A dictionary rendered as text with these fields: status (the text "price_changed" when
        the new price was recorded), resale_id (the file changed, text), previous_list_price
        (the asking price replaced, USD with 2 decimal places) and list_price (the asking price
        now on the file, USD with 2 decimal places).
    """
    price = round(float(new_list_price), 2)
    listing = (ctx.find("resale_listings", resale_id=resale_id) or [{}])[0]
    previous = listing.get("list_price")
    ctx.update("resale_listings", resale_id, list_price=price)
    return str({"status": "price_changed", "resale_id": resale_id,
                "previous_list_price": previous, "list_price": price})

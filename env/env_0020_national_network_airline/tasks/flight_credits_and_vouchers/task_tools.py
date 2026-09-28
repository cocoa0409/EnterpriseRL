"""Hidden task tools for flight_credits_and_vouchers (Crestline Flight Credits and Travel Vouchers).

Every tool here performs one atomic write on one credit with the values the caller supplies. No tool
checks eligibility, prerequisites, status or amounts; those judgements belong to the policy and the
agent. Row ids come from ctx.make_id over every argument, money is rounded to the cent, and the only
clock is ctx.now().
"""

from erlbench import ToolContext, tool


@tool(owner="agent", rw="write")
def reinstate_credit_8e2d0d7d(ctx: ToolContext, credit_id: str, writeoff_entry_id: str, restored_value: float,
                              validity_months: int) -> str:
    """Reinstate an expired Crestline flight credit or travel voucher so its value can be used again.

    One call makes the credit usable again: its status becomes active, its reinstatement count goes up by
    one, its closing date is cleared, its new expiry date is set to today's date plus the number of whole
    calendar months supplied (same day of the month, or the last day of that month when the day does not
    exist), and the value given is booked back onto the credit as one restore entry that points at the
    expiry write-off entry it undoes; the credit's remaining value rises by that amount. The customer then
    sees the credit as active with the new expiry date and the restored balance. Success is the receipt
    below with status "reinstated".

    Args:
        credit_id: Id class — reference number of the credit record being reinstated, as returned by the
            credit lookup for this customer.
        writeoff_entry_id: Id class — reference number of the expiry write-off entry on that credit which the
            restore undoes, as returned by the credit value-history lookup.
        restored_value: Fixed-format class — the value booked back onto the credit, in USD, a non-negative
            amount with 2 decimal places (rounded to the nearest cent on receipt).
        validity_months: Fixed-format class — the new term of validity as a whole number of calendar months,
            an integer of at least 1; the new expiry date is today's date moved forward by that many months.

    Returns:
        A text rendering of a dictionary with the keys status (the word "reinstated" on success), credit_id
        (the credit reinstated), restore_entry_id (reference number of the new restore entry), restored_value
        (the amount booked back, USD with 2 decimal places), new_expiry_date (the new expiry date, YYYY-MM-DD),
        reinstatement_count (the credit's reinstatement count after this call, an integer) and remaining_value
        (the credit's remaining value after the restore, USD with 2 decimal places).
    """
    rows = ctx.find("credit_holdings", credit_id=credit_id)
    cur = rows[0] if rows else {}
    today = ctx.now()[:10]
    year, month, day = int(today[0:4]), int(today[5:7]), int(today[8:10])
    total = month - 1 + int(validity_months)
    new_year, new_month = year + total // 12, total % 12 + 1
    leap = new_year % 4 == 0 and (new_year % 100 != 0 or new_year % 400 == 0)
    month_days = [31, 29 if leap else 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31][new_month - 1]
    new_expiry = f"{new_year:04d}-{new_month:02d}-{min(day, month_days):02d}"
    amount = round(float(restored_value), 2)
    count = int(cur.get("reinstatement_count") or 0) + 1
    remaining = round(float(cur.get("remaining_value") or 0) + amount, 2)
    ctx.update("credit_holdings", credit_id, status="active", expiry_date=new_expiry,
               reinstatement_count=count, remaining_value=remaining, closed_date=None)
    rid = ctx.make_id("crs_", credit_id, writeoff_entry_id, amount, int(validity_months))
    ctx.create("credit_ledger", rid, credit_entry_id=rid, credit_id=credit_id, customer_id=cur.get("customer_id"),
               event_type="credit_reinstatement_restore", entry_date=today, amount=amount,
               reversed_entry_id=writeoff_entry_id)
    return str({"status": "reinstated", "credit_id": credit_id, "restore_entry_id": rid,
                "restored_value": amount, "new_expiry_date": new_expiry,
                "reinstatement_count": count, "remaining_value": remaining})


@tool(owner="user", rw="write")
def pay_credit_reinstatement_fee_177d2025(ctx: ToolContext, credit_id: str, fee_amount: float) -> str:
    """The credit holder pays, by card, the reinstatement fee on one of their own Crestline credits.

    One call books the payment as a reinstatement fee entry on that credit, dated today, for the amount
    given; the credit's value, status and expiry date do not change. The holder sees the fee on the
    credit's fee history and receives the fee entry number as the payment receipt. Success is the receipt
    below with status "fee_paid".

    Args:
        credit_id: Id class — reference number of the credit the fee is paid on, as given to the holder by
            the agent from the credit lookup.
        fee_amount: Fixed-format class — the fee paid, in USD, a non-negative amount with 2 decimal places
            (rounded to the nearest cent on receipt).

    Returns:
        A text rendering of a dictionary with the keys status (the word "fee_paid" on success), credit_id (the
        credit the fee was paid on), fee_entry_id (reference number of the new fee entry, the payment
        receipt), fee_type (always "reinstatement_fee"), fee_amount (the amount paid, USD with 2 decimal
        places) and entry_date (the payment date, YYYY-MM-DD).
    """
    rows = ctx.find("credit_holdings", credit_id=credit_id)
    cur = rows[0] if rows else {}
    amount = round(float(fee_amount), 2)
    today = ctx.now()[:10]
    rid = ctx.make_id("cfr_", credit_id, amount)
    ctx.create("credit_ledger", rid, credit_entry_id=rid, credit_id=credit_id, customer_id=cur.get("customer_id"),
               event_type="credit_service_fee", entry_date=today, amount=amount, fee_type="reinstatement_fee")
    return str({"status": "fee_paid", "credit_id": credit_id, "fee_entry_id": rid, "fee_type": "reinstatement_fee",
                "fee_amount": amount, "entry_date": today})


@tool(owner="agent", rw="write")
def charge_credit_phone_fee_f43f310b(ctx: ToolContext, credit_id: str, redemption_entry_id: str,
                                    fee_amount: float) -> str:
    """Charge the telephone booking fee for one redemption of a Crestline credit made through reservations.

    One call books a telephone redemption fee entry on the credit, dated today, for the amount given, linked
    to the redemption entry it belongs to; the credit's value, status and expiry date do not change. The
    fee then appears on the credit's fee history next to that redemption, and the new fee entry number is
    the receipt. Success is the receipt below with status "fee_charged".

    Args:
        credit_id: Id class — reference number of the credit the redemption was made from, as returned by the
            credit lookup for this customer.
        redemption_entry_id: Id class — reference number of the redemption entry the fee belongs to, as returned
            by the credit value-history lookup.
        fee_amount: Fixed-format class — the fee charged, in USD, a non-negative amount with 2 decimal places
            (rounded to the nearest cent on receipt).

    Returns:
        A text rendering of a dictionary with the keys status (the word "fee_charged" on success), credit_id (the
        credit charged), fee_entry_id (reference number of the new fee entry), fee_type (always
        "phone_redemption_fee"), related_entry_id (the redemption entry the fee is linked to), fee_amount (the
        amount charged, USD with 2 decimal places) and entry_date (the date booked, YYYY-MM-DD).
    """
    rows = ctx.find("credit_holdings", credit_id=credit_id)
    cur = rows[0] if rows else {}
    amount = round(float(fee_amount), 2)
    today = ctx.now()[:10]
    rid = ctx.make_id("cfp_", credit_id, redemption_entry_id, amount)
    ctx.create("credit_ledger", rid, credit_entry_id=rid, credit_id=credit_id, customer_id=cur.get("customer_id"),
               event_type="credit_service_fee", entry_date=today, amount=amount, fee_type="phone_redemption_fee",
               related_entry_id=redemption_entry_id)
    return str({"status": "fee_charged", "credit_id": credit_id, "fee_entry_id": rid,
                "fee_type": "phone_redemption_fee", "related_entry_id": redemption_entry_id,
                "fee_amount": amount, "entry_date": today})


@tool(owner="user", rw="write")
def pay_credit_extension_fee_5a6cc7fd(ctx: ToolContext, credit_id: str, fee_amount: float) -> str:
    """The credit holder pays, by card, the extension fee on one of their own Crestline credits.

    One call books the payment as an extension fee entry on that credit, dated today, for the amount given;
    the credit's value, status and expiry date do not change. The holder sees the fee on the credit's fee
    history and receives the fee entry number as the payment receipt. Success is the receipt below with
    status "fee_paid".

    Args:
        credit_id: Id class — reference number of the credit the fee is paid on, as given to the holder by the
            agent from the credit lookup.
        fee_amount: Fixed-format class — the fee paid, in USD, a non-negative amount with 2 decimal places
            (rounded to the nearest cent on receipt).

    Returns:
        A text rendering of a dictionary with the keys status (the word "fee_paid" on success), credit_id (the
        credit the fee was paid on), fee_entry_id (reference number of the new fee entry, the payment receipt),
        fee_type (always "extension_fee"), fee_amount (the amount paid, USD with 2 decimal places) and entry_date
        (the payment date, YYYY-MM-DD).
    """
    rows = ctx.find("credit_holdings", credit_id=credit_id)
    cur = rows[0] if rows else {}
    amount = round(float(fee_amount), 2)
    today = ctx.now()[:10]
    rid = ctx.make_id("cfx_", credit_id, amount)
    ctx.create("credit_ledger", rid, credit_entry_id=rid, credit_id=credit_id, customer_id=cur.get("customer_id"),
               event_type="credit_service_fee", entry_date=today, amount=amount, fee_type="extension_fee")
    return str({"status": "fee_paid", "credit_id": credit_id, "fee_entry_id": rid, "fee_type": "extension_fee",
                "fee_amount": amount, "entry_date": today})


@tool(owner="agent", rw="write")
def extend_credit_f94665bb(ctx: ToolContext, credit_id: str, extension_months: int) -> str:
    """Extend the expiry date of an active Crestline flight credit or travel voucher.

    One call moves the credit's expiry date forward by the number of whole calendar months given, counted
    from the expiry date the credit currently shows (same day of the month, or the last day of that month
    when the day does not exist), and raises the credit's extension count by one; the credit's value and
    status do not change. The customer then sees the credit with its new expiry date. Success is the receipt
    below with status "extended".

    Args:
        credit_id: Id class — reference number of the credit being extended, as returned by the credit lookup
            for this customer.
        extension_months: Fixed-format class — the length of the extension as a whole number of calendar months,
            an integer of at least 1.

    Returns:
        A text rendering of a dictionary with the keys status (the word "extended" on success), credit_id (the
        credit extended), previous_expiry_date (the expiry date before the call, YYYY-MM-DD), new_expiry_date (the
        expiry date after the call, YYYY-MM-DD) and extension_count (the credit's extension count after this
        call, an integer).
    """
    rows = ctx.find("credit_holdings", credit_id=credit_id)
    cur = rows[0] if rows else {}
    old = str(cur.get("expiry_date") or ctx.now()[:10])[:10]
    year, month, day = int(old[0:4]), int(old[5:7]), int(old[8:10])
    total = month - 1 + int(extension_months)
    new_year, new_month = year + total // 12, total % 12 + 1
    leap = new_year % 4 == 0 and (new_year % 100 != 0 or new_year % 400 == 0)
    month_days = [31, 29 if leap else 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31][new_month - 1]
    new_expiry = f"{new_year:04d}-{new_month:02d}-{min(day, month_days):02d}"
    count = int(cur.get("extension_count") or 0) + 1
    ctx.update("credit_holdings", credit_id, expiry_date=new_expiry, extension_count=count)
    return str({"status": "extended", "credit_id": credit_id, "previous_expiry_date": old,
                "new_expiry_date": new_expiry, "extension_count": count})

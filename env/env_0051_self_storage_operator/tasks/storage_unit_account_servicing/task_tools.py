"""Hidden task tools for the storage_unit_account_servicing difficulty (Bluegate storage unit rental agreements).

Each tool performs one atomic write on a storage unit rental agreement's records with the values the agent (or, for an
owner=user tool, the tenant) passes in. No tool computes a fee, a payment or a rent, and no tool checks a business
precondition: the policy decides, the tool lands the write.
"""

from erlbench import ToolContext, tool


class _LedgerRow:
    """Shared shape of one unit ledger entry (not a tool)."""

    FIELDS = ("event_type", "amount", "entry_date", "period_start", "period_end", "fee_type", "credit_type",
              "reference_entry_id", "payment_method", "payment_channel", "autopay_draft_id", "reversal_reason",
              "refund_method", "release_type")

    @staticmethod
    def others(rid, rental, given, **fixed):
        """The entry's identity, its fixed values, and every field neither fixed nor in `given`, left empty."""
        row = {"entry_id": rid, "rental_id": rental.get("rental_id"), "customer_id": rental.get("customer_id")}
        row.update(fixed)
        for name in _LedgerRow.FIELDS:
            if name not in row and name not in given:
                row[name] = None if name == "autopay_draft_id" else ""
        return row


@tool(owner="agent", rw="write")
def assess_unit_late_fee_4b513073(ctx: ToolContext, rental_id: str, reference_entry_id: str, period_start: str,
                                  fee_type: str, amount: float) -> dict:
    """Post a late fee on a storage unit rental agreement's tenant ledger for one billing period whose rent is unpaid.

    One call adds one late-fee entry to the agreement's ledger, dated today, tied to the unpaid rent charge it arises
    from and to that billing period's due date, and raises the agreement's balance due by the amount posted. The tenant
    sees the fee on the agreement's ledger and statement and in the new balance due. The call succeeds when the receipt
    returns the new ledger entry number.

    Args:
        rental_id: Id class — the storage unit rental agreement number, read from the rental agreement lookup.
        reference_entry_id: Id class — the ledger entry number of the unpaid rent charge the late fee arises from, read
            from the agreement's ledger lookup.
        period_start: Fixed-format class — the due date (first day) of the billing period the late fee is for, in
            YYYY-MM-DD form, exactly as that rent charge shows it on the ledger.
        fee_type: Enum class — the kind of fee posted: late_fee for the late fee of a billing period whose rent is
            still unpaid after its grace days.
        amount: Fixed-format class — the late fee to post, in USD, 2 decimal places, always positive; a value with more
            places is rounded to the cent.

    Returns:
        A dictionary receipt: entry_id (string, the new ledger entry number), rental_id (string, the agreement
        charged), fee_type (string, the kind of fee posted), period_start (string, YYYY-MM-DD, the period the fee is
        for), amount (number, USD to 2 decimal places, the fee posted), entry_date (string, YYYY-MM-DD, the posting
        date, today) and balance_due (number, USD to 2 decimal places, the agreement's balance due after the fee).
    """
    rental = ctx.find("unit_rentals", rental_id=rental_id)[0]
    rid = ctx.make_id("ulf_", rental_id, reference_entry_id, period_start, fee_type, amount)
    today = ctx.now()[:10]
    given = ("amount", "entry_date", "period_start", "reference_entry_id")
    ctx.create("unit_ledger", rid, **_LedgerRow.others(rid, rental, given, event_type="unit_fee_charge",
                                                       fee_type=fee_type),
               amount=round(float(amount), 2), entry_date=today, period_start=period_start,
               reference_entry_id=reference_entry_id)
    balance = round(float(rental.get("balance_due") or 0) + round(float(amount), 2), 2)
    ctx.update("unit_rentals", rental_id, balance_due=balance)
    return {"entry_id": rid, "rental_id": rental_id, "fee_type": fee_type, "period_start": period_start,
            "amount": round(float(amount), 2), "entry_date": today, "balance_due": balance}


@tool(owner="agent", rw="write")
def post_unit_returned_payment_fee_fb0d77c5(ctx: ToolContext, rental_id: str, reference_entry_id: str,
                                            period_start: str, fee_type: str, amount: float) -> dict:
    """Post a returned-payment fee on a storage unit rental agreement's tenant ledger against one payment the bank returned.

    One call adds one returned-payment fee entry to the agreement's ledger, dated today, tied to the returned payment it
    arises from and to the due date of the billing period that payment was for, and raises the agreement's balance due
    by the amount posted. The tenant sees the fee on the agreement's ledger and statement and in the new balance due.
    The call succeeds when the receipt returns the new ledger entry number.

    Args:
        rental_id: Id class — the storage unit rental agreement number, read from the rental agreement lookup.
        reference_entry_id: Id class — the ledger entry number of the payment the bank returned (the payment entry the
            reversal points at), read from the agreement's ledger lookup.
        period_start: Fixed-format class — the due date (first day) of the billing period the returned payment was for,
            in YYYY-MM-DD form, exactly as that period's rent charge shows it on the ledger.
        fee_type: Enum class — the kind of fee posted: returned_payment_fee for the fee charged when the bank returns a
            payment unpaid.
        amount: Fixed-format class — the returned-payment fee to post, in USD, 2 decimal places, always positive; a value
            with more places is rounded to the cent.

    Returns:
        A dictionary receipt: entry_id (string, the new ledger entry number), rental_id (string, the agreement
        charged), fee_type (string, the kind of fee posted), reference_entry_id (string, the returned payment the fee is
        posted against), amount (number, USD to 2 decimal places, the fee posted), entry_date (string, YYYY-MM-DD, the
        posting date, today) and balance_due (number, USD to 2 decimal places, the agreement's balance due after the fee).
    """
    rental = ctx.find("unit_rentals", rental_id=rental_id)[0]
    rid = ctx.make_id("urf_", rental_id, reference_entry_id, period_start, fee_type, amount)
    today = ctx.now()[:10]
    given = ("amount", "entry_date", "period_start", "reference_entry_id")
    ctx.create("unit_ledger", rid, **_LedgerRow.others(rid, rental, given, event_type="unit_fee_charge",
                                                       fee_type=fee_type),
               amount=round(float(amount), 2), entry_date=today, period_start=period_start,
               reference_entry_id=reference_entry_id)
    balance = round(float(rental.get("balance_due") or 0) + round(float(amount), 2), 2)
    ctx.update("unit_rentals", rental_id, balance_due=balance)
    return {"entry_id": rid, "rental_id": rental_id, "fee_type": fee_type, "reference_entry_id": reference_entry_id,
            "amount": round(float(amount), 2), "entry_date": today, "balance_due": balance}


@tool(owner="user", rw="write")
def pay_unit_returned_balance_f137f581(ctx: ToolContext, rental_id: str, reference_entry_id: str,
                                       payment_method: str, amount: float) -> dict:
    """The tenant pays, over the phone, to replace a payment the bank returned on their storage unit rental agreement.

    One call records one payment from the tenant's own card or bank account on the agreement's tenant ledger, dated
    today, taken through the care center phone line and tied to the returned payment it replaces, and lowers the
    agreement's balance due by the amount paid; any part of the payment above the balance due stays on the agreement as
    a credit balance. The tenant sees the payment and the new balance on the agreement's ledger and statement. The call
    succeeds when the receipt returns the new payment entry number.

    Args:
        rental_id: Id class — the storage unit rental agreement number the payment is for, as the agent reads it from
            the rental agreement lookup and passes it to the tenant.
        reference_entry_id: Id class — the ledger entry number of the payment the bank returned that this payment
            replaces, as the agent reads it from the agreement's ledger lookup.
        payment_method: Enum class — how the tenant pays: credit_card for a credit card the tenant reads out; debit_card
            for a debit card the tenant reads out; ach_bank_account for a one-time debit from a bank account the tenant
            reads out; cash for cash, which is handed over only at a facility office; money_order for a money order,
            which is handed over only at a facility office; prepaid_rent_plan for a month applied from a Bluegate
            prepaid rent plan, which is never a phone payment.
        amount: Fixed-format class — the amount the tenant pays, in USD, 2 decimal places, always positive; a value with
            more places is rounded to the cent.

    Returns:
        A dictionary receipt: entry_id (string, the new payment entry number), rental_id (string, the agreement paid),
        payment_method (string, how the tenant paid), reference_entry_id (string, the returned payment replaced), amount
        (number, USD to 2 decimal places, the amount paid), entry_date (string, YYYY-MM-DD, the payment date, today) and
        balance_due (number, USD to 2 decimal places, the agreement's balance due after the payment; negative means a
        credit balance).
    """
    rental = ctx.find("unit_rentals", rental_id=rental_id)[0]
    rid = ctx.make_id("upr_", rental_id, reference_entry_id, payment_method, amount)
    today = ctx.now()[:10]
    given = ("amount", "entry_date", "payment_method", "reference_entry_id")
    ctx.create("unit_ledger", rid, **_LedgerRow.others(rid, rental, given, event_type="unit_payment",
                                                       payment_channel="care_center_phone"),
               amount=round(float(amount), 2), entry_date=today, payment_method=payment_method,
               reference_entry_id=reference_entry_id)
    balance = round(float(rental.get("balance_due") or 0) - round(float(amount), 2), 2)
    ctx.update("unit_rentals", rental_id, balance_due=balance)
    return {"entry_id": rid, "rental_id": rental_id, "payment_method": payment_method,
            "reference_entry_id": reference_entry_id, "amount": round(float(amount), 2), "entry_date": today,
            "balance_due": balance}


@tool(owner="user", rw="write")
def restore_unit_good_standing_afa2c723(ctx: ToolContext, rental_id: str, payment_method: str, amount: float) -> dict:
    """The tenant pays, over the phone, to bring a delinquent storage unit rental agreement back to good standing.

    One call records one payment from the tenant's own card or bank account on the agreement's tenant ledger, dated
    today and taken through the care center phone line, lowers the agreement's balance due by the amount paid, returns
    the agreement to active status and clears its delinquency date; any part of the payment above the balance due stays
    on the agreement as a credit balance toward the next rent. The tenant sees the payment, the new balance and the
    active standing on the agreement's ledger and statement. The call succeeds when the receipt returns the new payment
    entry number.

    Args:
        rental_id: Id class — the storage unit rental agreement number the payment is for, as the agent reads it from
            the rental agreement lookup and passes it to the tenant.
        payment_method: Enum class — how the tenant pays: credit_card for a credit card the tenant reads out; debit_card
            for a debit card the tenant reads out; ach_bank_account for a one-time debit from a bank account the tenant
            reads out; cash for cash, which is handed over only at a facility office; money_order for a money order,
            which is handed over only at a facility office; prepaid_rent_plan for a month applied from a Bluegate
            prepaid rent plan, which is never a phone payment.
        amount: Fixed-format class — the amount the tenant pays, in USD, 2 decimal places, always positive; a value with
            more places is rounded to the cent.

    Returns:
        A dictionary receipt: entry_id (string, the new payment entry number), rental_id (string, the agreement paid),
        payment_method (string, how the tenant paid), amount (number, USD to 2 decimal places, the amount paid),
        entry_date (string, YYYY-MM-DD, the payment date, today), balance_due (number, USD to 2 decimal places, the
        agreement's balance due after the payment; negative means a credit balance) and status (string, the agreement's
        standing after the payment, active).
    """
    rental = ctx.find("unit_rentals", rental_id=rental_id)[0]
    rid = ctx.make_id("ugs_", rental_id, payment_method, amount)
    today = ctx.now()[:10]
    given = ("amount", "entry_date", "payment_method")
    ctx.create("unit_ledger", rid, **_LedgerRow.others(rid, rental, given, event_type="unit_payment",
                                                       payment_channel="care_center_phone"),
               amount=round(float(amount), 2), entry_date=today, payment_method=payment_method)
    balance = round(float(rental.get("balance_due") or 0) - round(float(amount), 2), 2)
    ctx.update("unit_rentals", rental_id, balance_due=balance, status="active", delinquent_since="")
    return {"entry_id": rid, "rental_id": rental_id, "payment_method": payment_method,
            "amount": round(float(amount), 2), "entry_date": today, "balance_due": balance, "status": "active"}


class _RateNotice:
    """Shared write of one noticed rent change that modifies an earlier increase notice (not a tool)."""

    @staticmethod
    def write(ctx, prefix, reason, rental_id, source_rate_change_id, new_rent):
        rental = ctx.find("unit_rentals", rental_id=rental_id)[0]
        source = ctx.find("unit_rate_changes", rate_change_id=source_rate_change_id)[0]
        rid = ctx.make_id(prefix, rental_id, source_rate_change_id, new_rent)
        today = ctx.now()[:10]
        ctx.create("unit_rate_changes", rid, rate_change_id=rid, rental_id=rental_id,
                   customer_id=rental.get("customer_id"), event_type="unit_rate_change_notice", change_reason=reason,
                   previous_rent=source.get("previous_rent"), notice_date=today,
                   effective_date=source.get("effective_date"))
        return rid, today, source


@tool(owner="agent", rw="write")
def reduce_unit_rate_increase_85726890(ctx: ToolContext, rental_id: str, source_rate_change_id: str,
                                       new_rent: float) -> dict:
    """Notice a reduction of an existing-customer rent increase on a storage unit rental agreement, cutting it back.

    One call records one rent change notice, dated today, that points at the increase notice it reduces, keeps that
    increase's effective date and its rent-before-change, and carries the reduced monthly rent as the new rent from that
    effective date; the agreement's current rent is not changed by the call. The tenant sees the reduced rent on the
    agreement's rent change history and in the notice sent. The call succeeds when the receipt returns the new rent
    change number.

    Args:
        rental_id: Id class — the storage unit rental agreement number, read from the rental agreement lookup.
        source_rate_change_id: Id class — the rent change number of the existing-customer increase notice being
            reduced, read from the agreement's rent change lookup.
        new_rent: Fixed-format class — the reduced monthly rent from the increase's effective date, in USD, 2 decimal
            places; a value with more places is rounded to the cent.

    Returns:
        A dictionary receipt: rate_change_id (string, the new rent change number), rental_id (string, the agreement),
        source_rate_change_id (string, the increase notice reduced), change_reason (string, increase_rescinded),
        previous_rent (number, USD to 2 decimal places, the rent before the increase), new_rent (number, USD to 2
        decimal places, the reduced rent), notice_date (string, YYYY-MM-DD, today) and effective_date (string,
        YYYY-MM-DD, the increase's effective date).
    """
    rid, today, source = _RateNotice.write(ctx, "urr_", "increase_rescinded", rental_id, source_rate_change_id,
                                           new_rent)
    ctx.update("unit_rate_changes", rid, new_rent=round(float(new_rent), 2), source_rate_change_id=source_rate_change_id)
    return {"rate_change_id": rid, "rental_id": rental_id, "source_rate_change_id": source_rate_change_id,
            "change_reason": "increase_rescinded", "previous_rent": source.get("previous_rent"),
            "new_rent": round(float(new_rent), 2), "notice_date": today, "effective_date": source.get("effective_date")}


@tool(owner="agent", rw="write")
def grant_unit_retention_concession_f9ae06a9(ctx: ToolContext, rental_id: str, source_rate_change_id: str,
                                             new_rent: float) -> dict:
    """Grant a retention concession on a noticed rent increase of a storage unit rental agreement.

    One call records one retention concession notice, dated today, that points at the increase notice it gives part of
    back, keeps that increase's effective date and its rent-before-change, and carries the conceded monthly rent as the
    new rent from that effective date; the agreement's current rent is not changed by the call. The tenant sees the
    conceded rent on the agreement's rent change history and in the confirmation sent. The call succeeds when the
    receipt returns the new rent change number.

    Args:
        rental_id: Id class — the storage unit rental agreement number, read from the rental agreement lookup.
        source_rate_change_id: Id class — the rent change number of the existing-customer increase notice the
            concession applies to, read from the agreement's rent change lookup.
        new_rent: Fixed-format class — the conceded monthly rent from the increase's effective date, in USD, 2 decimal
            places; a value with more places is rounded to the cent.

    Returns:
        A dictionary receipt: rate_change_id (string, the new rent change number), rental_id (string, the agreement),
        source_rate_change_id (string, the increase notice the concession applies to), change_reason (string,
        retention_concession), previous_rent (number, USD to 2 decimal places, the rent before the increase), new_rent
        (number, USD to 2 decimal places, the conceded rent), notice_date (string, YYYY-MM-DD, today) and
        effective_date (string, YYYY-MM-DD, the increase's effective date).
    """
    rid, today, source = _RateNotice.write(ctx, "urc_", "retention_concession", rental_id, source_rate_change_id,
                                           new_rent)
    ctx.update("unit_rate_changes", rid, new_rent=round(float(new_rent), 2), source_rate_change_id=source_rate_change_id)
    return {"rate_change_id": rid, "rental_id": rental_id, "source_rate_change_id": source_rate_change_id,
            "change_reason": "retention_concession", "previous_rent": source.get("previous_rent"),
            "new_rent": round(float(new_rent), 2), "notice_date": today, "effective_date": source.get("effective_date")}

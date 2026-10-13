"""Hidden task tools of the net_energy_metering difficulty (Lakeshore Power & Light Company).

Each tool performs one atomic write on the net metering records and is reached only through the
unlock/call meta-tools after its name is read from the extended charter. No tool checks a policy
precondition or computes a policy value: the caller passes values already worked out.
"""

from erlbench import ToolContext, tool


@tool(owner="agent", rw="write")
def revalue_export_credit_a4b62fb5(ctx: ToolContext, nem_agreement_id: str, nem_ledger_id: str, credit_rate_on_peak: float,
                                   credit_rate_off_peak: float, revalued_credit_usd: float) -> dict:
    """Revalue one export credit already banked in a customer's net metering history.

    The representative replaces the two per-kWh rates and the dollar amount recorded on one existing
    export credit entry with the revalued rates and the revalued amount; the export kWh recorded on the
    entry are left unchanged. The banked credit of the net metering agreement that owns the entry moves
    by the difference between the revalued amount and the amount previously recorded, so a higher
    revalued amount raises the bank and a lower one lowers it. Afterwards the history shows the entry
    with its new rates and amount and the agreement shows the adjusted bank. The receipt below with
    status "revalued" means the change was saved.

    Args:
        nem_agreement_id: Id class — reference number of the net metering agreement (interconnection
            application number) that owns the entry, read from the net metering agreement lookup before the call.
        nem_ledger_id: Id class — reference number of the export credit entry being revalued, read from the
            net metering history lookup of that agreement before the call.
        credit_rate_on_peak: Fixed-format class — revalued rate applied to the entry's on-peak export kWh, in
            USD per kWh, a decimal number with 5 decimal places (rounded half up to 5 decimal places before it
            is passed); pass 0.00000 when no on-peak rate applies.
        credit_rate_off_peak: Fixed-format class — revalued rate applied to the entry's off-peak export kWh, in
            USD per kWh, a decimal number with 5 decimal places (rounded half up to 5 decimal places before it
            is passed).
        revalued_credit_usd: Fixed-format class — revalued dollar amount of the export credit, in USD, a
            positive decimal number with 2 decimal places (rounded to the cent before it is passed).

    Returns:
        A dict receipt: "status" is "revalued" on success; "nem_ledger_id" is the entry revalued;
        "nem_agreement_id" echoes the agreement whose bank moved; "previous_amount" and "revalued_amount" are
        the old and new entry amounts in USD with 2 decimals; "credit_rate_on_peak" and
        "credit_rate_off_peak" echo the stored rates in USD per kWh with 5 decimals; "credit_bank_balance"
        is the agreement's banked credit in USD with 2 decimals after the change.
    """
    entry = ctx.find("nem_ledger", nem_ledger_id=nem_ledger_id)[0]
    agreement_id = nem_agreement_id
    agreement = ctx.find("nem_agreements", nem_agreement_id=agreement_id)[0]
    previous = round(float(entry.get("amount") or 0), 2)
    new_amount = round(float(revalued_credit_usd), 2)
    rate_on = round(float(credit_rate_on_peak), 5)
    rate_off = round(float(credit_rate_off_peak), 5)
    ctx.update("nem_ledger", nem_ledger_id, credit_rate_on_peak=rate_on, credit_rate_off_peak=rate_off,
               amount=new_amount)
    bank = round(float(agreement.get("credit_bank_balance") or 0) - previous + new_amount, 2)
    ctx.update("nem_agreements", agreement_id, credit_bank_balance=bank)
    return {"status": "revalued", "nem_ledger_id": nem_ledger_id, "nem_agreement_id": agreement_id,
            "previous_amount": previous, "revalued_amount": new_amount, "credit_rate_on_peak": rate_on,
            "credit_rate_off_peak": rate_off, "credit_bank_balance": bank}


@tool(owner="agent", rw="write")
def book_estimated_export_credit_93ce1e35(ctx: ToolContext, nem_agreement_id: str, billing_period_end: str,
                                          export_kwh_on_peak: int, export_kwh_off_peak: int,
                                          credit_rate_on_peak: float, credit_rate_off_peak: float,
                                          estimated_credit_usd: float) -> dict:
    """Bank an estimated export credit for one billing period of a net metering agreement.

    The representative adds one export credit entry to the agreement's net metering history for a
    billing period that has none, recording the estimated on-peak and off-peak export kWh, the two
    per-kWh rates used and the dollar amount, dated to the billing period end; the agreement's banked
    credit rises by that amount. Afterwards the history lists the new export credit for that period and
    the agreement shows the larger bank. The receipt below with status "banked" means the entry was saved.

    Args:
        nem_agreement_id: Id class — reference number of the net metering agreement (interconnection
            application number), read from the net metering agreement lookup before the call.
        billing_period_end: Fixed-format class — last day of the billing period the credit belongs to, in
            YYYY-MM-DD format, copied from the billing period end printed on the service bill for that period.
        export_kwh_on_peak: Fixed-format class — estimated kWh exported in on-peak hours, in kWh, a
            non-negative integer (whole kWh); pass 0 when none.
        export_kwh_off_peak: Fixed-format class — estimated kWh exported in all other hours, in kWh, a
            non-negative integer (whole kWh).
        credit_rate_on_peak: Fixed-format class — rate applied to the on-peak kWh, in USD per kWh, a decimal
            number with 5 decimal places.
        credit_rate_off_peak: Fixed-format class — rate applied to the off-peak kWh, in USD per kWh, a decimal
            number with 5 decimal places.
        estimated_credit_usd: Fixed-format class — dollar amount of the estimated export credit, in USD, a
            positive decimal number with 2 decimal places (rounded to the cent before it is passed).

    Returns:
        A dict receipt: "status" is "banked" on success; "nem_ledger_id" is the reference number of the new
        export credit entry; "nem_agreement_id" echoes the agreement; "billing_period_end" is the period
        end in YYYY-MM-DD; "amount" is the credit in USD with 2 decimals; "credit_bank_balance" is the
        agreement's banked credit in USD with 2 decimals after the entry.
    """
    agreement = ctx.find("nem_agreements", nem_agreement_id=nem_agreement_id)[0]
    amount = round(float(estimated_credit_usd), 2)
    rid = ctx.make_id("nml_", nem_agreement_id, billing_period_end, export_kwh_on_peak, export_kwh_off_peak,
                      credit_rate_on_peak, credit_rate_off_peak, estimated_credit_usd)
    ctx.create("nem_ledger", rid, nem_ledger_id=rid, nem_agreement_id=nem_agreement_id,
               customer_id=agreement["customer_id"], service_account_id=agreement["service_account_id"],
               event_type="nem_export_credit", fee_date="", billing_period_end=billing_period_end, bill_id=None,
               export_kwh_on_peak=int(export_kwh_on_peak), export_kwh_off_peak=int(export_kwh_off_peak),
               credit_rate_on_peak=round(float(credit_rate_on_peak), 5),
               credit_rate_off_peak=round(float(credit_rate_off_peak), 5), settlement_date="",
               settlement_kind="not_applicable", payout_method="not_applicable", amount=amount)
    bank = round(float(agreement.get("credit_bank_balance") or 0) + amount, 2)
    ctx.update("nem_agreements", nem_agreement_id, credit_bank_balance=bank)
    return {"status": "banked", "nem_ledger_id": rid, "nem_agreement_id": nem_agreement_id,
            "billing_period_end": billing_period_end, "amount": amount, "credit_bank_balance": bank}


@tool(owner="user", rw="write")
def end_net_metering_at_move_out_41499158(ctx: ToolContext, nem_agreement_id: str, payout_usd: float,
                                          surrendered_usd: float) -> dict:
    """End your own net metering agreement because you are stopping electric service at the address.

    The customer ends their operating net metering agreement: the agreement becomes terminated as of
    today, the move-out payout is recorded as a termination settlement paid by check, any part of the bank
    not paid is recorded as surrendered at termination, and the agreement's banked credit becomes 0.00.
    Afterwards the agreement shows terminated status and the history shows the check payout (and the
    surrendered amount when it is above zero). The receipt below with status "terminated" means the
    agreement was ended and settled.

    Args:
        nem_agreement_id: Id class — reference number of the customer's net metering agreement, as given to
            the customer by the representative from the agreement lookup.
        payout_usd: Fixed-format class — move-out payout to be sent by check, in USD, a positive decimal
            number with 2 decimal places, exactly as the representative states it.
        surrendered_usd: Fixed-format class — part of the bank that is not paid and is surrendered, in USD, a
            decimal number with 2 decimal places, exactly as the representative states it; 0.00 when nothing
            is surrendered.

    Returns:
        A dict receipt: "status" is "terminated" on success; "nem_agreement_id" echoes the agreement;
        "termination_date" is today's date in YYYY-MM-DD; "payout_reference" is the reference number of the
        check payout entry; "payout_amount" and "surrendered_amount" are in USD with 2 decimals;
        "credit_bank_balance" is 0.00 after settlement.
    """
    agreement = ctx.find("nem_agreements", nem_agreement_id=nem_agreement_id)[0]
    today = ctx.now()[:10]
    payout = round(float(payout_usd), 2)
    surrendered = round(float(surrendered_usd), 2)
    pid = ctx.make_id("nml_", nem_agreement_id, "termination_payout", payout_usd, surrendered_usd)
    ctx.create("nem_ledger", pid, nem_ledger_id=pid, nem_agreement_id=nem_agreement_id,
               customer_id=agreement["customer_id"], service_account_id=agreement["service_account_id"],
               event_type="nem_true_up_payout", fee_date="", billing_period_end="", bill_id=None,
               export_kwh_on_peak=0, export_kwh_off_peak=0, credit_rate_on_peak=0.0, credit_rate_off_peak=0.0,
               settlement_date=today, settlement_kind="termination", payout_method="check", amount=payout)
    if surrendered > 0:
        fid = ctx.make_id("nml_", nem_agreement_id, "termination_surrender", payout_usd, surrendered_usd)
        ctx.create("nem_ledger", fid, nem_ledger_id=fid, nem_agreement_id=nem_agreement_id,
                   customer_id=agreement["customer_id"], service_account_id=agreement["service_account_id"],
                   event_type="nem_true_up_forfeiture", fee_date="", billing_period_end="", bill_id=None,
                   export_kwh_on_peak=0, export_kwh_off_peak=0, credit_rate_on_peak=0.0, credit_rate_off_peak=0.0,
                   settlement_date=today, settlement_kind="termination", payout_method="not_applicable",
                   amount=surrendered)
    ctx.update("nem_agreements", nem_agreement_id, status="terminated", status_date=today, credit_bank_balance=0.0)
    return {"status": "terminated", "nem_agreement_id": nem_agreement_id, "termination_date": today,
            "payout_reference": pid, "payout_amount": payout, "surrendered_amount": surrendered,
            "credit_bank_balance": 0.0}


@tool(owner="agent", rw="write")
def expire_carried_credit_d622768b(ctx: ToolContext, nem_agreement_id: str, expired_credit_usd: float) -> dict:
    """Book the expiry of carried export credit at an agreement's anniversary true-up.

    The representative records, dated today, one anniversary forfeiture entry in the agreement's net
    metering history for the stated amount of carried credit that has expired, and the agreement's banked
    credit falls by that amount. Afterwards the history shows the forfeiture with settlement kind
    anniversary and the agreement shows the smaller bank. The receipt below with status "expired" means
    the entry was saved.

    Args:
        nem_agreement_id: Id class — reference number of the net metering agreement (interconnection
            application number), read from the net metering agreement lookup before the call.
        expired_credit_usd: Fixed-format class — dollar amount of carried credit that expires, in USD, a
            positive decimal number with 2 decimal places (rounded to the cent before it is passed).

    Returns:
        A dict receipt: "status" is "expired" on success; "nem_ledger_id" is the reference number of the
        forfeiture entry; "nem_agreement_id" echoes the agreement; "settlement_date" is today's date in
        YYYY-MM-DD; "amount" is the expired credit in USD with 2 decimals; "credit_bank_balance" is the
        agreement's banked credit in USD with 2 decimals after the entry.
    """
    agreement = ctx.find("nem_agreements", nem_agreement_id=nem_agreement_id)[0]
    today = ctx.now()[:10]
    amount = round(float(expired_credit_usd), 2)
    rid = ctx.make_id("nml_", nem_agreement_id, "anniversary_expiry", today, expired_credit_usd)
    ctx.create("nem_ledger", rid, nem_ledger_id=rid, nem_agreement_id=nem_agreement_id,
               customer_id=agreement["customer_id"], service_account_id=agreement["service_account_id"],
               event_type="nem_true_up_forfeiture", fee_date="", billing_period_end="", bill_id=None,
               export_kwh_on_peak=0, export_kwh_off_peak=0, credit_rate_on_peak=0.0, credit_rate_off_peak=0.0,
               settlement_date=today, settlement_kind="anniversary", payout_method="not_applicable", amount=amount)
    bank = round(float(agreement.get("credit_bank_balance") or 0) - amount, 2)
    ctx.update("nem_agreements", nem_agreement_id, credit_bank_balance=bank)
    return {"status": "expired", "nem_ledger_id": rid, "nem_agreement_id": nem_agreement_id,
            "settlement_date": today, "amount": amount, "credit_bank_balance": bank}


@tool(owner="agent", rw="write")
def settle_anniversary_cash_out_8d85c400(ctx: ToolContext, nem_agreement_id: str, payout_usd: float) -> dict:
    """Pay an agreement's anniversary true-up cash-out by check.

    The representative records, dated today, one anniversary payout entry paid by check in the agreement's
    net metering history for the stated amount, and the agreement's banked credit falls by that amount;
    whatever credit remains stays banked. Afterwards the history shows the check payout with settlement
    kind anniversary and the agreement shows the remaining bank. The receipt below with status "paid"
    means the payout was saved.

    Args:
        nem_agreement_id: Id class — reference number of the net metering agreement (interconnection
            application number), read from the net metering agreement lookup before the call.
        payout_usd: Fixed-format class — anniversary cash-out paid by check, in USD, a positive decimal number
            with 2 decimal places (rounded to the cent before it is passed).

    Returns:
        A dict receipt: "status" is "paid" on success; "nem_ledger_id" is the reference number of the payout
        entry; "nem_agreement_id" echoes the agreement; "settlement_date" is today's date in YYYY-MM-DD;
        "payout_method" is "check"; "amount" is the payout in USD with 2 decimals; "credit_bank_balance" is the
        agreement's banked credit in USD with 2 decimals after the payout.
    """
    agreement = ctx.find("nem_agreements", nem_agreement_id=nem_agreement_id)[0]
    today = ctx.now()[:10]
    amount = round(float(payout_usd), 2)
    rid = ctx.make_id("nml_", nem_agreement_id, "anniversary_payout", today, payout_usd)
    ctx.create("nem_ledger", rid, nem_ledger_id=rid, nem_agreement_id=nem_agreement_id,
               customer_id=agreement["customer_id"], service_account_id=agreement["service_account_id"],
               event_type="nem_true_up_payout", fee_date="", billing_period_end="", bill_id=None,
               export_kwh_on_peak=0, export_kwh_off_peak=0, credit_rate_on_peak=0.0, credit_rate_off_peak=0.0,
               settlement_date=today, settlement_kind="anniversary", payout_method="check", amount=amount)
    bank = round(float(agreement.get("credit_bank_balance") or 0) - amount, 2)
    ctx.update("nem_agreements", nem_agreement_id, credit_bank_balance=bank)
    return {"status": "paid", "nem_ledger_id": rid, "nem_agreement_id": nem_agreement_id, "settlement_date": today,
            "payout_method": "check", "amount": amount, "credit_bank_balance": bank}


@tool(owner="user", rw="write")
def end_net_metering_on_request_fe4f3e33(ctx: ToolContext, nem_agreement_id: str, payout_usd: float,
                                         surrendered_usd: float) -> dict:
    """End your own net metering agreement while keeping electric service at the address.

    The customer ends their operating net metering agreement: the agreement becomes terminated as of today,
    the termination payout is recorded as a termination settlement paid by check, any part of the bank not
    paid is recorded as surrendered at termination, and the agreement's banked credit becomes 0.00. The
    electric service itself is not changed. Afterwards the agreement shows terminated status and the
    history shows the check payout (and the surrendered amount when it is above zero). The receipt below
    with status "terminated" means the agreement was ended and settled.

    Args:
        nem_agreement_id: Id class — reference number of the customer's net metering agreement, as given to
            the customer by the representative from the agreement lookup.
        payout_usd: Fixed-format class — termination payout to be sent by check, in USD, a positive decimal
            number with 2 decimal places, exactly as the representative states it.
        surrendered_usd: Fixed-format class — part of the bank that is not paid and is surrendered, in USD, a
            decimal number with 2 decimal places, exactly as the representative states it; 0.00 when nothing is
            surrendered.

    Returns:
        A dict receipt: "status" is "terminated" on success; "nem_agreement_id" echoes the agreement;
        "termination_date" is today's date in YYYY-MM-DD; "payout_reference" is the reference number of the
        check payout entry; "payout_amount" and "surrendered_amount" are in USD with 2 decimals;
        "credit_bank_balance" is 0.00 after settlement.
    """
    agreement = ctx.find("nem_agreements", nem_agreement_id=nem_agreement_id)[0]
    today = ctx.now()[:10]
    payout = round(float(payout_usd), 2)
    surrendered = round(float(surrendered_usd), 2)
    pid = ctx.make_id("nml_", nem_agreement_id, "requested_termination_payout", payout_usd, surrendered_usd)
    ctx.create("nem_ledger", pid, nem_ledger_id=pid, nem_agreement_id=nem_agreement_id,
               customer_id=agreement["customer_id"], service_account_id=agreement["service_account_id"],
               event_type="nem_true_up_payout", fee_date="", billing_period_end="", bill_id=None,
               export_kwh_on_peak=0, export_kwh_off_peak=0, credit_rate_on_peak=0.0, credit_rate_off_peak=0.0,
               settlement_date=today, settlement_kind="termination", payout_method="check", amount=payout)
    if surrendered > 0:
        fid = ctx.make_id("nml_", nem_agreement_id, "requested_termination_surrender", payout_usd, surrendered_usd)
        ctx.create("nem_ledger", fid, nem_ledger_id=fid, nem_agreement_id=nem_agreement_id,
                   customer_id=agreement["customer_id"], service_account_id=agreement["service_account_id"],
                   event_type="nem_true_up_forfeiture", fee_date="", billing_period_end="", bill_id=None,
                   export_kwh_on_peak=0, export_kwh_off_peak=0, credit_rate_on_peak=0.0, credit_rate_off_peak=0.0,
                   settlement_date=today, settlement_kind="termination", payout_method="not_applicable",
                   amount=surrendered)
    ctx.update("nem_agreements", nem_agreement_id, status="terminated", status_date=today, credit_bank_balance=0.0)
    return {"status": "terminated", "nem_agreement_id": nem_agreement_id, "termination_date": today,
            "payout_reference": pid, "payout_amount": payout, "surrendered_amount": surrendered,
            "credit_bank_balance": 0.0}

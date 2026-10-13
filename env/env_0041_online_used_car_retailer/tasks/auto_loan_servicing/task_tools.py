"""Hidden task tools of the auto_loan_servicing difficulty (category finance) of env_0041_online_used_car_retailer.

Each tool performs one atomic write on a Kestrel Auto Finance retail installment contract and its loan
ledger. Every amount, date and identifier it books is supplied by the caller; the tool decides nothing.
"""

from erlbench import ToolContext, tool


@tool(owner="agent", rw="write")
def assess_late_fee_56686208(ctx: ToolContext, finance_contract_id: str, installment_due_date: str,
                             late_fee_amount: float) -> str:
    """Charge a late fee on one installment of a Kestrel Auto Finance retail installment contract.

    The representative books one late-fee charge on the borrower's loan ledger, dated today and tied to the
    installment named, and the contract's fees due rise by the same amount. The borrower sees the late fee
    listed on the loan history and included in the fees due. A receipt naming the new ledger entry confirms
    the charge was booked.

    Args:
        finance_contract_id: Id class — the reference number of the finance contract being charged, as returned
            by the finance contract lookup for this borrower.
        installment_due_date: Fixed-format class — the due date of the installment the late fee is charged on,
            written YYYY-MM-DD exactly as the contract or loan history shows it; no time zone applies.
        late_fee_amount: Fixed-format class — the late fee being charged, in USD, a positive amount with 2
            decimal places (already rounded to the cent).

    Returns:
        A dict with: status ("late_fee_assessed" when the charge is booked); finance_txn_id (str, the reference
        number of the new late-fee ledger entry); installment_due_date (str, YYYY-MM-DD, the installment charged);
        late_fee_amount (float, USD with 2 decimals, the fee booked); fees_due (float, USD with 2 decimals, the
        contract's fees due including this fee).
    """
    amount = round(float(late_fee_amount), 2)
    rid = ctx.make_id("ftx_", finance_contract_id, installment_due_date, amount, "late_fee")
    c = (ctx.find("finance_contracts", finance_contract_id=finance_contract_id) or [{}])[0]
    ctx.create("finance_transactions", rid, finance_txn_id=rid, finance_contract_id=finance_contract_id,
               customer_id=c.get("customer_id"), event_type="finance_fee_assessed", txn_date=ctx.now()[:10],
               amount=amount, total_received=0.0, interest_portion=0.0, fee_portion=0.0,
               payment_channel="not_applicable", payment_type="not_applicable", fee_type="late_fee",
               clearance_type="not_applicable", credit_source="not_applicable",
               installment_due_date=installment_due_date, good_through_date="", per_diem_interest=0.0,
               source_txn_id=None, linked_reference_id=None)
    fees_due = round(float(c.get("fees_due") or 0) + amount, 2)
    ctx.update("finance_contracts", finance_contract_id, fees_due=fees_due)
    return str({"status": "late_fee_assessed", "finance_txn_id": rid, "installment_due_date": installment_due_date,
                "late_fee_amount": amount, "fees_due": fees_due})


@tool(owner="agent", rw="write")
def assess_returned_payment_fee_ca20439d(ctx: ToolContext, finance_contract_id: str, returned_payment_id: str,
                                         installment_due_date: str, returned_fee_amount: float) -> str:
    """Charge the returned-payment fee for a borrower payment that the borrower's bank sent back unpaid.

    The representative books one returned-payment fee on the Kestrel Auto Finance loan ledger, dated today,
    naming the payment the bank returned and the installment that payment was made for; the contract's fees
    due rise by the same amount. The borrower sees the fee on the loan history and in the fees due. A receipt
    naming the new ledger entry confirms the charge was booked.

    Args:
        finance_contract_id: Id class — the reference number of the finance contract being charged, as returned
            by the finance contract lookup for this borrower.
        returned_payment_id: Id class — the ledger reference number of the borrower payment the bank returned,
            as shown on the original payment entry in the loan history lookup.
        installment_due_date: Fixed-format class — the due date of the installment the returned payment was made
            for, written YYYY-MM-DD exactly as the loan history shows it; no time zone applies.
        returned_fee_amount: Fixed-format class — the returned-payment fee being charged, in USD, a positive
            amount with 2 decimal places (already rounded to the cent).

    Returns:
        A dict with: status ("returned_payment_fee_assessed" when the charge is booked); finance_txn_id (str,
        the reference number of the new fee entry); returned_payment_id (str, the payment the fee is for);
        returned_fee_amount (float, USD with 2 decimals, the fee booked); fees_due (float, USD with 2 decimals,
        the contract's fees due including this fee).
    """
    amount = round(float(returned_fee_amount), 2)
    rid = ctx.make_id("ftx_", finance_contract_id, returned_payment_id, installment_due_date, amount, "returned")
    c = (ctx.find("finance_contracts", finance_contract_id=finance_contract_id) or [{}])[0]
    ctx.create("finance_transactions", rid, finance_txn_id=rid, finance_contract_id=finance_contract_id,
               customer_id=c.get("customer_id"), event_type="finance_fee_assessed", txn_date=ctx.now()[:10],
               amount=amount, total_received=0.0, interest_portion=0.0, fee_portion=0.0,
               payment_channel="not_applicable", payment_type="not_applicable", fee_type="returned_payment_fee",
               clearance_type="not_applicable", credit_source="not_applicable",
               installment_due_date=installment_due_date, good_through_date="", per_diem_interest=0.0,
               source_txn_id=returned_payment_id, linked_reference_id=None)
    fees_due = round(float(c.get("fees_due") or 0) + amount, 2)
    ctx.update("finance_contracts", finance_contract_id, fees_due=fees_due)
    return str({"status": "returned_payment_fee_assessed", "finance_txn_id": rid,
                "returned_payment_id": returned_payment_id, "returned_fee_amount": amount, "fees_due": fees_due})


@tool(owner="user", rw="write")
def pay_deferral_qualifying_amount_eaa14a46(ctx: ToolContext, finance_contract_id: str, total_received: float,
                                            interest_portion: float, fee_portion: float,
                                            principal_portion: float) -> str:
    """Make a one-time partial payment on your own Kestrel Auto Finance loan from your bank account through the
    Kestrel app.

    The payment posts today as a partial payment by online bank transfer and is split exactly as entered between
    interest, fees and principal: the contract's fees due fall by the fee part (recorded as fees paid), its
    principal balance falls by the principal part, and the date interest last stopped accruing becomes today.
    A partial payment never moves the next due date. A receipt naming the payment's ledger entry confirms it
    posted, and the payment appears on the loan history.

    Args:
        finance_contract_id: Id class — the reference number of your finance contract, as the representative
            reads it to you from the contract record.
        total_received: Fixed-format class — the full payment, in USD, a positive amount with 2 decimal places.
        interest_portion: Fixed-format class — the part of the payment applied to interest, in USD with 2 decimal
            places; 0.00 when none.
        fee_portion: Fixed-format class — the part of the payment applied to fees, in USD with 2 decimal places;
            0.00 when none.
        principal_portion: Fixed-format class — the part of the payment applied to principal, in USD with 2
            decimal places; 0.00 when none.

    Returns:
        A dict with: status ("payment_posted" when the payment posts); finance_txn_id (str, the reference number
        of the payment entry); total_received (float, USD with 2 decimals); principal_balance (float, USD with 2
        decimals, the principal remaining); fees_due (float, USD with 2 decimals, the fees remaining);
        last_payment_date (str, YYYY-MM-DD, today).
    """
    total = round(float(total_received), 2)
    interest = round(float(interest_portion), 2)
    fee = round(float(fee_portion), 2)
    principal = round(float(principal_portion), 2)
    today = ctx.now()[:10]
    rid = ctx.make_id("ftx_", finance_contract_id, total, interest, fee, principal, "partial")
    c = (ctx.find("finance_contracts", finance_contract_id=finance_contract_id) or [{}])[0]
    ctx.create("finance_transactions", rid, finance_txn_id=rid, finance_contract_id=finance_contract_id,
               customer_id=c.get("customer_id"), event_type="finance_payment_posted", txn_date=today,
               amount=principal, total_received=total, interest_portion=interest, fee_portion=fee,
               payment_channel="online_ach", payment_type="partial_payment", fee_type="not_applicable",
               clearance_type="not_applicable", credit_source="not_applicable", installment_due_date="",
               good_through_date="", per_diem_interest=0.0, source_txn_id=None, linked_reference_id=None)
    if fee > 0:
        cid = ctx.make_id("ftx_", rid, "fee_paid")
        ctx.create("finance_transactions", cid, finance_txn_id=cid, finance_contract_id=finance_contract_id,
                   customer_id=c.get("customer_id"), event_type="finance_fee_cleared", txn_date=today,
                   amount=fee, total_received=0.0, interest_portion=0.0, fee_portion=0.0,
                   payment_channel="not_applicable", payment_type="not_applicable", fee_type="not_applicable",
                   clearance_type="paid", credit_source="not_applicable", installment_due_date="",
                   good_through_date="", per_diem_interest=0.0, source_txn_id=rid, linked_reference_id=None)
    balance = round(float(c.get("principal_balance") or 0) - principal, 2)
    fees_due = round(float(c.get("fees_due") or 0) - fee, 2)
    ctx.update("finance_contracts", finance_contract_id, principal_balance=balance, fees_due=fees_due,
               last_payment_date=today)
    return str({"status": "payment_posted", "finance_txn_id": rid, "total_received": total,
                "principal_balance": balance, "fees_due": fees_due, "last_payment_date": today})


@tool(owner="agent", rw="write")
def grant_payment_deferral_f4f9e9cb(ctx: ToolContext, finance_contract_id: str, installment_due_date: str,
                                    next_due_date: str, maturity_date: str, deferral_fee: float) -> str:
    """Grant a payment deferral on a Kestrel Auto Finance retail installment contract, moving one installment
    to the end of the contract.

    The representative books the deferral of the installment named, dated today, sets the contract's next due
    date and final due date to the dates given, adds one to the deferrals used, and, when the deferral fee
    given is above zero, books that fee as a deferral-fee charge for the deferred installment and adds it to
    the fees due. The borrower sees the new due dates on the contract and the deferral on the loan history.
    A receipt naming the deferral entry confirms the deferral was granted.

    Args:
        finance_contract_id: Id class — the reference number of the finance contract, as returned by the finance
            contract lookup for this borrower.
        installment_due_date: Fixed-format class — the due date of the installment being deferred, written
            YYYY-MM-DD exactly as the contract shows it; no time zone applies.
        next_due_date: Fixed-format class — the contract's next due date with the deferral in place, written
            YYYY-MM-DD; no time zone applies.
        maturity_date: Fixed-format class — the due date of the contract's final installment with the deferral
            in place, written YYYY-MM-DD; no time zone applies.
        deferral_fee: Fixed-format class — the deferral fee, in USD with 2 decimal places; 0.00 books no fee.

    Returns:
        A dict with: status ("deferral_granted" when the deferral is booked); finance_txn_id (str, the reference
        number of the deferral entry); installment_due_date (str, YYYY-MM-DD, the installment deferred);
        next_due_date (str, YYYY-MM-DD); maturity_date (str, YYYY-MM-DD); deferral_fee (float, USD with 2
        decimals); deferrals_used (int, deferrals granted over the life of the contract); fees_due (float, USD
        with 2 decimals).
    """
    fee = round(float(deferral_fee), 2)
    today = ctx.now()[:10]
    rid = ctx.make_id("ftx_", finance_contract_id, installment_due_date, next_due_date, maturity_date, fee)
    c = (ctx.find("finance_contracts", finance_contract_id=finance_contract_id) or [{}])[0]
    ctx.create("finance_transactions", rid, finance_txn_id=rid, finance_contract_id=finance_contract_id,
               customer_id=c.get("customer_id"), event_type="finance_deferral_granted", txn_date=today,
               amount=0.0, total_received=0.0, interest_portion=0.0, fee_portion=0.0,
               payment_channel="not_applicable", payment_type="not_applicable", fee_type="not_applicable",
               clearance_type="not_applicable", credit_source="not_applicable",
               installment_due_date=installment_due_date, good_through_date="", per_diem_interest=0.0,
               source_txn_id=None, linked_reference_id=None)
    fees_due = round(float(c.get("fees_due") or 0), 2)
    if fee > 0:
        fid = ctx.make_id("ftx_", rid, "deferral_fee")
        ctx.create("finance_transactions", fid, finance_txn_id=fid, finance_contract_id=finance_contract_id,
                   customer_id=c.get("customer_id"), event_type="finance_fee_assessed", txn_date=today,
                   amount=fee, total_received=0.0, interest_portion=0.0, fee_portion=0.0,
                   payment_channel="not_applicable", payment_type="not_applicable", fee_type="deferral_fee",
                   clearance_type="not_applicable", credit_source="not_applicable",
                   installment_due_date=installment_due_date, good_through_date="", per_diem_interest=0.0,
                   source_txn_id=None, linked_reference_id=None)
        fees_due = round(fees_due + fee, 2)
    used = int(c.get("deferrals_used") or 0) + 1
    ctx.update("finance_contracts", finance_contract_id, next_due_date=next_due_date, maturity_date=maturity_date,
               deferrals_used=used, fees_due=fees_due)
    return str({"status": "deferral_granted", "finance_txn_id": rid, "installment_due_date": installment_due_date,
                "next_due_date": next_due_date, "maturity_date": maturity_date, "deferral_fee": fee,
                "deferrals_used": used, "fees_due": fees_due})


@tool(owner="user", rw="write")
def pay_past_due_installment_fb9b9167(ctx: ToolContext, finance_contract_id: str, installment_due_date: str,
                                      next_due_date: str, total_received: float, interest_portion: float,
                                      fee_portion: float, principal_portion: float) -> str:
    """Pay a past-due installment of your own Kestrel Auto Finance loan from your bank account through the
    Kestrel app.

    The payment posts today as a scheduled-installment payment by online bank transfer for the installment
    named and is split exactly as entered between interest, fees and principal: the contract's fees due fall by
    the fee part (recorded as fees paid), its principal balance falls by the principal part, the date interest
    last stopped accruing becomes today, and the next due date becomes the date entered. A receipt naming the
    payment's ledger entry confirms it posted, and the payment appears on the loan history.

    Args:
        finance_contract_id: Id class — the reference number of your finance contract, as the representative
            reads it to you from the contract record.
        installment_due_date: Fixed-format class — the due date of the installment this payment satisfies,
            written YYYY-MM-DD; no time zone applies.
        next_due_date: Fixed-format class — the contract's next due date with this payment in place, written
            YYYY-MM-DD; no time zone applies.
        total_received: Fixed-format class — the full payment, in USD, a positive amount with 2 decimal places.
        interest_portion: Fixed-format class — the part of the payment applied to interest, in USD with 2 decimal
            places; 0.00 when none.
        fee_portion: Fixed-format class — the part of the payment applied to fees, in USD with 2 decimal places;
            0.00 when none.
        principal_portion: Fixed-format class — the part of the payment applied to principal, in USD with 2
            decimal places; 0.00 when none.

    Returns:
        A dict with: status ("payment_posted" when the payment posts); finance_txn_id (str, the reference number
        of the payment entry); total_received (float, USD with 2 decimals); principal_balance (float, USD with 2
        decimals, the principal remaining); fees_due (float, USD with 2 decimals, the fees remaining);
        next_due_date (str, YYYY-MM-DD); last_payment_date (str, YYYY-MM-DD, today).
    """
    total = round(float(total_received), 2)
    interest = round(float(interest_portion), 2)
    fee = round(float(fee_portion), 2)
    principal = round(float(principal_portion), 2)
    today = ctx.now()[:10]
    rid = ctx.make_id("ftx_", finance_contract_id, installment_due_date, next_due_date, total, interest, fee,
                      principal)
    c = (ctx.find("finance_contracts", finance_contract_id=finance_contract_id) or [{}])[0]
    ctx.create("finance_transactions", rid, finance_txn_id=rid, finance_contract_id=finance_contract_id,
               customer_id=c.get("customer_id"), event_type="finance_payment_posted", txn_date=today,
               amount=principal, total_received=total, interest_portion=interest, fee_portion=fee,
               payment_channel="online_ach", payment_type="scheduled_installment", fee_type="not_applicable",
               clearance_type="not_applicable", credit_source="not_applicable",
               installment_due_date=installment_due_date, good_through_date="", per_diem_interest=0.0,
               source_txn_id=None, linked_reference_id=None)
    if fee > 0:
        cid = ctx.make_id("ftx_", rid, "fee_paid")
        ctx.create("finance_transactions", cid, finance_txn_id=cid, finance_contract_id=finance_contract_id,
                   customer_id=c.get("customer_id"), event_type="finance_fee_cleared", txn_date=today,
                   amount=fee, total_received=0.0, interest_portion=0.0, fee_portion=0.0,
                   payment_channel="not_applicable", payment_type="not_applicable", fee_type="not_applicable",
                   clearance_type="paid", credit_source="not_applicable", installment_due_date="",
                   good_through_date="", per_diem_interest=0.0, source_txn_id=rid, linked_reference_id=None)
    balance = round(float(c.get("principal_balance") or 0) - principal, 2)
    fees_due = round(float(c.get("fees_due") or 0) - fee, 2)
    ctx.update("finance_contracts", finance_contract_id, principal_balance=balance, fees_due=fees_due,
               last_payment_date=today, next_due_date=next_due_date)
    return str({"status": "payment_posted", "finance_txn_id": rid, "total_received": total,
                "principal_balance": balance, "fees_due": fees_due, "next_due_date": next_due_date,
                "last_payment_date": today})


@tool(owner="agent", rw="write")
def credit_goodwill_late_fee_132adaff(ctx: ToolContext, finance_contract_id: str, late_fee_entry_id: str,
                                      credit_amount: float) -> str:
    """Give goodwill relief on a late fee charged on a Kestrel Auto Finance retail installment contract, as a
    credit to the contract's principal.

    The representative books one principal credit dated today as a billing correction that names the late-fee
    entry it relieves, and the contract's principal balance falls by the credit. The credit does not count as a
    payment toward any due date. The borrower sees the credit on the loan history and the lower principal on the
    contract. A receipt naming the credit entry confirms it was booked.

    Args:
        finance_contract_id: Id class — the reference number of the finance contract, as returned by the finance
            contract lookup for this borrower.
        late_fee_entry_id: Id class — the ledger reference number of the late-fee entry being relieved, as shown in
            the loan history lookup.
        credit_amount: Fixed-format class — the goodwill credit, in USD, a positive amount with 2 decimal places
            (already rounded to the cent).

    Returns:
        A dict with: status ("goodwill_credit_posted" when the credit is booked); finance_txn_id (str, the
        reference number of the credit entry); late_fee_entry_id (str, the late fee relieved); credit_amount
        (float, USD with 2 decimals); principal_balance (float, USD with 2 decimals, the principal remaining).
    """
    amount = round(float(credit_amount), 2)
    rid = ctx.make_id("ftx_", finance_contract_id, late_fee_entry_id, amount, "goodwill")
    c = (ctx.find("finance_contracts", finance_contract_id=finance_contract_id) or [{}])[0]
    ctx.create("finance_transactions", rid, finance_txn_id=rid, finance_contract_id=finance_contract_id,
               customer_id=c.get("customer_id"), event_type="finance_principal_credited", txn_date=ctx.now()[:10],
               amount=amount, total_received=0.0, interest_portion=0.0, fee_portion=0.0,
               payment_channel="not_applicable", payment_type="not_applicable", fee_type="not_applicable",
               clearance_type="not_applicable", credit_source="billing_correction", installment_due_date="",
               good_through_date="", per_diem_interest=0.0, source_txn_id=late_fee_entry_id,
               linked_reference_id=None)
    balance = round(float(c.get("principal_balance") or 0) - amount, 2)
    ctx.update("finance_contracts", finance_contract_id, principal_balance=balance)
    return str({"status": "goodwill_credit_posted", "finance_txn_id": rid, "late_fee_entry_id": late_fee_entry_id,
                "credit_amount": amount, "principal_balance": balance})

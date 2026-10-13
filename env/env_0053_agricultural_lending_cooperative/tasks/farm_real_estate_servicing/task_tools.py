"""Hidden task tools for farm_real_estate_servicing (Cottonwood Plains Farm Credit, ACA).

Each tool performs one atomic write on a farm real estate loan with the values the caller has
already worked out; none of them judges eligibility, aggregates history or computes an amount.
"""

from erlbench import ToolContext, tool


@tool(owner="agent", rw="write")
def book_default_interest_ef623284(ctx: ToolContext, loan_id: str, period_start: str, period_end: str,
                                   rate_applied: float, amount: float) -> str:
    """Book a default-rate interest entry on a farm real estate loan and add it to the billed interest owed.

    The servicing desk records one interest entry at the default rate covering the stretch of days given,
    dated and billed today, and the loan's billed-interest-not-yet-paid balance rises by the amount. After the
    call the loan's transaction history shows the new entry marked as default-rate interest with its period,
    rate and amount, and the loan shows the higher billed interest owed. The entry is booked exactly as given.

    Args:
        loan_id: Id class — the loan number of the member's farm real estate loan, read from the farm real estate loan lookup before the call.
        period_start: Fixed-format class — first day the default-rate entry covers, inclusive, written YYYY-MM-DD (format: YYYY-MM-DD; empty when not periodic — never empty here).
        period_end: Fixed-format class — last day the default-rate entry covers, inclusive, written YYYY-MM-DD (format: YYYY-MM-DD; empty when not periodic — never empty here).
        rate_applied: Fixed-format class — the annual rate the entry is figured at, in percent, as annual percentage rate, 3 decimal places; empty when no rate applies (never empty here).
        amount: Fixed-format class — the interest booked, in USD, 2 decimal places, always positive; the value is rounded half-up to cents as received.

    Returns:
        A confirmation sentence naming the new entry reference (an id beginning dfi_), the loan number, the
        period covered, the rate and the amount booked, and the loan's new billed interest owed in USD with
        2 decimal places; the presence of the entry reference means the entry was recorded.
    """
    loans = ctx.find("farmland_loans", loan_id=loan_id)
    customer_id = loans[0].get("customer_id") if loans else ""
    owed = round(float((loans[0].get("accrued_interest") if loans else 0) or 0) + round(float(amount), 2), 2)
    rid = ctx.make_id("dfi_", loan_id, period_start, period_end, rate_applied, amount)
    today = ctx.now()[:10]
    ctx.create("farmland_transactions", rid, txn_id=rid, loan_id=loan_id, customer_id=customer_id,
               event_type="farmland_interest_accrual", amount=round(float(amount), 2), effective_date=today,
               channel="system", payment_purpose="none", fee_code="none", period_start=period_start,
               period_end=period_end, due_date=today, rate_applied=round(float(rate_applied), 3),
               rate_basis="default_rate", tax_year="", source_ref_id="", waiver_basis="none", return_reason="none")
    ctx.update("farmland_loans", loan_id, accrued_interest=owed)
    return (f"Default-rate interest entry {rid} booked on loan {loan_id} for {period_start} through {period_end} "
            f"at {round(float(rate_applied), 3):.3f}%: {round(float(amount), 2):.2f} USD; billed interest owed now {owed:.2f} USD.")


@tool(owner="user", rw="write")
def authorize_installment_autodebit_3b801ea5(ctx: ToolContext, loan_id: str, account_last4: str,
                                             interest_rate: float) -> str:
    """The member authorises automatic debit of the installments on their own farm real estate loan.

    Running this records the member's own instruction that every installment on the loan is debited from the
    checking account they identify, switches automatic debit on for the loan, and sets the contract rate the
    loan carries from today to the rate given. Afterwards the loan shows automatic debit enrolled, the last
    four digits of the debited account and the new contract rate; the receipt confirms all three.

    Args:
        loan_id: Id class — the loan number of the member's farm real estate loan, as the servicing desk read it from the loan lookup and handed it over.
        account_last4: Fixed-format class — the last four digits of the member's checking account to be debited, exactly 4 digits as the member gives them (format: 4 digits; empty when not enrolled — never empty here).
        interest_rate: Fixed-format class — the contract rate the loan carries from today as the servicing desk states it, in annual percentage rate, 3 decimal places.

    Returns:
        A confirmation sentence naming the loan number, stating that automatic debit is now on from the account
        ending in the four digits given, and stating the contract rate now in force as a percentage with 3
        decimal places; the sentence beginning "Automatic debit authorised" means the change was recorded.
    """
    ctx.update("farmland_loans", loan_id, autopay_enrolled=True, autopay_account_last4=str(account_last4),
               interest_rate=round(float(interest_rate), 3))
    return (f"Automatic debit authorised on loan {loan_id} from the account ending {account_last4}; "
            f"contract rate now {round(float(interest_rate), 3):.3f}%.")


@tool(owner="agent", rw="write")
def assess_late_charge_e3cbcc6c(ctx: ToolContext, loan_id: str, source_ref_id: str, amount: float) -> str:
    """Assess a late charge on one installment of a farm real estate loan and add it to the fees owed.

    The servicing desk records one late-charge fee against the installment bill named, dated today, and the
    loan's fees-not-yet-collected balance rises by the amount. Afterwards the loan's transaction history shows
    the late charge pointing to that installment bill, and the loan shows the higher fees owed. The charge is
    recorded exactly as given.

    Args:
        loan_id: Id class — the loan number of the member's farm real estate loan, read from the farm real estate loan lookup before the call.
        source_ref_id: Id class — the reference number of the installment bill the late charge is assessed on, read from the loan's transaction history (the interest bill entry whose period ends on that installment's due date).
        amount: Fixed-format class — the late charge in USD, 2 decimal places, always positive; the value is rounded half-up to cents as received.

    Returns:
        A confirmation sentence naming the new fee reference (an id beginning lcf_), the loan number, the
        installment bill it is charged on, the amount in USD with 2 decimal places and the loan's new fees owed;
        the presence of the fee reference means the charge was recorded.
    """
    loans = ctx.find("farmland_loans", loan_id=loan_id)
    customer_id = loans[0].get("customer_id") if loans else ""
    owed = round(float((loans[0].get("fees_due") if loans else 0) or 0) + round(float(amount), 2), 2)
    rid = ctx.make_id("lcf_", loan_id, source_ref_id, amount)
    ctx.create("farmland_transactions", rid, txn_id=rid, loan_id=loan_id, customer_id=customer_id,
               event_type="farmland_fee_assessed", amount=round(float(amount), 2), effective_date=ctx.now()[:10],
               channel="system", payment_purpose="none", fee_code="late_charge", period_start="", period_end="",
               due_date="", rate_applied="", rate_basis="none", tax_year="", source_ref_id=source_ref_id,
               waiver_basis="none", return_reason="none")
    ctx.update("farmland_loans", loan_id, fees_due=owed)
    return (f"Late charge {rid} assessed on loan {loan_id} against installment bill {source_ref_id}: "
            f"{round(float(amount), 2):.2f} USD; fees owed now {owed:.2f} USD.")


@tool(owner="user", rw="write")
def authorize_principal_paydown_4d1911cd(ctx: ToolContext, loan_id: str, account_last4: str, amount: float) -> str:
    """The member authorises a one-time debit of their own checking account to pay principal down on their farm loan.

    Running this records the member's own instruction to take the amount given from the checking account they
    identify today and apply all of it to the loan's principal as a prepayment; the loan's principal balance
    falls by the amount. Afterwards the loan's history shows the principal prepayment received today by phone
    and the loan shows the lower principal balance; the receipt confirms both.

    Args:
        loan_id: Id class — the loan number of the member's farm real estate loan, as the servicing desk read it from the loan lookup and handed it over.
        account_last4: Fixed-format class — the last four digits of the member's checking account to be debited once, exactly 4 digits as the member gives them.
        amount: Fixed-format class — the principal paid down as the servicing desk states it, in USD, 2 decimal places, always positive.

    Returns:
        A confirmation sentence beginning "Principal paydown authorised" naming the payment reference (an id
        beginning ppd_), the loan number, the account ending in the four digits given, the amount in USD with 2
        decimal places and the loan's new principal balance; it means the paydown was applied.
    """
    loans = ctx.find("farmland_loans", loan_id=loan_id)
    customer_id = loans[0].get("customer_id") if loans else ""
    new_bal = round(float((loans[0].get("principal_balance") if loans else 0) or 0) - round(float(amount), 2), 2)
    rid = ctx.make_id("ppd_", loan_id, account_last4, amount)
    ctx.create("farmland_transactions", rid, txn_id=rid, loan_id=loan_id, customer_id=customer_id,
               event_type="farmland_principal_payment", amount=round(float(amount), 2), effective_date=ctx.now()[:10],
               channel="phone", payment_purpose="prepayment", fee_code="none", period_start="", period_end="",
               due_date="", rate_applied="", rate_basis="none", tax_year="", source_ref_id="",
               waiver_basis="none", return_reason="none")
    ctx.update("farmland_loans", loan_id, principal_balance=new_bal)
    return (f"Principal paydown authorised: payment {rid} on loan {loan_id} from the account ending {account_last4}, "
            f"{round(float(amount), 2):.2f} USD applied to principal; principal balance now {new_bal:.2f} USD.")


@tool(owner="agent", rw="write")
def release_farmstead_parcel_0569f2e2(ctx: ToolContext, loan_id: str, source_action_id: str, release_price: float,
                                      release_fee: float) -> str:
    """Release one mortgaged homesite parcel from a farm real estate loan as a farmstead split.

    The servicing desk records the release of the parcel named by its mortgage record, dated today, with the
    release reason farmstead split and the parcel's recorded details carried over; applies the release price
    to the loan's principal as release proceeds; and assesses the release fee. Afterwards the parcel shows as
    released, the loan's principal balance falls by the release price, the appraised value still mortgaged
    falls by the parcel's value, the fees owed rise by the release fee, and the history shows the release-
    proceeds payment and the fee, both pointing to the release record.

    Args:
        loan_id: Id class — the loan number of the member's farm real estate loan, read from the farm real estate loan lookup before the call.
        source_action_id: Id class — the reference number of the mortgage record of the homesite parcel to be released, read from the parcel lookup for the loan.
        release_price: Fixed-format class — the release price applied to principal as release proceeds, in USD, 2 decimal places, always positive.
        release_fee: Fixed-format class — the partial release fee the product carries for a release on sale or farmstead split, in USD, 2 decimal places, always positive.

    Returns:
        A confirmation sentence naming the release record reference (an id beginning rel_), the parcel number,
        the loan number, the release price applied and the release fee in USD with 2 decimal places, and the
        loan's new principal balance and appraised value still mortgaged; the release reference means the parcel
        is released.
    """
    loans = ctx.find("farmland_loans", loan_id=loan_id)
    loan = loans[0] if loans else {}
    parcels = ctx.find("farmland_parcels", parcel_action_id=source_action_id)
    parcel = parcels[0] if parcels else {}
    today = ctx.now()[:10]
    price = round(float(release_price), 2)
    fee = round(float(release_fee), 2)
    rid = ctx.make_id("rel_", loan_id, source_action_id, release_price, release_fee)
    ctx.create("farmland_parcels", rid, parcel_action_id=rid, loan_id=loan_id, customer_id=loan.get("customer_id", ""),
               event_type="farmland_parcel_released", parcel_number=parcel.get("parcel_number", ""),
               legal_description=parcel.get("legal_description", ""), county=parcel.get("county", ""),
               acres=parcel.get("acres", 0.0), land_use=parcel.get("land_use", ""),
               appraised_value=parcel.get("appraised_value", 0.0), action_date=today, source_action_id=source_action_id,
               release_reason="farmstead_split")
    pay_id = ctx.make_id("rpp_", rid)
    ctx.create("farmland_transactions", pay_id, txn_id=pay_id, loan_id=loan_id, customer_id=loan.get("customer_id", ""),
               event_type="farmland_principal_payment", amount=price, effective_date=today, channel="system",
               payment_purpose="release_proceeds", fee_code="none", period_start="", period_end="", due_date="",
               rate_applied="", rate_basis="none", tax_year="", source_ref_id=rid, waiver_basis="none", return_reason="none")
    fee_id = ctx.make_id("rlf_", rid)
    ctx.create("farmland_transactions", fee_id, txn_id=fee_id, loan_id=loan_id, customer_id=loan.get("customer_id", ""),
               event_type="farmland_fee_assessed", amount=fee, effective_date=today, channel="system",
               payment_purpose="none", fee_code="partial_release", period_start="", period_end="", due_date="",
               rate_applied="", rate_basis="none", tax_year="", source_ref_id=rid, waiver_basis="none", return_reason="none")
    new_bal = round(float(loan.get("principal_balance") or 0) - price, 2)
    new_coll = round(float(loan.get("collateral_value") or 0) - float(parcel.get("appraised_value") or 0), 2)
    new_fees = round(float(loan.get("fees_due") or 0) + fee, 2)
    ctx.update("farmland_loans", loan_id, principal_balance=new_bal, collateral_value=new_coll, fees_due=new_fees)
    return (f"Parcel {parcel.get('parcel_number', '')} released from loan {loan_id} as a farmstead split (release {rid}); "
            f"release price {price:.2f} USD applied to principal, release fee {fee:.2f} USD assessed; principal balance "
            f"now {new_bal:.2f} USD, appraised value still mortgaged {new_coll:.2f} USD.")

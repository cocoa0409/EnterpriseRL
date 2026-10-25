"""Hidden task tools of the medicaid_pending_and_patient_pay difficulty (Medical Assistance
nursing facility coverage). Each tool lands one atomic write on the Medical Assistance case
ledger and keeps the case's patient pay balance in step with it."""
from decimal import Decimal, ROUND_HALF_UP

from erlbench import ToolContext, tool


class _Ledger:
    @staticmethod
    def cents(value) -> float:
        """Exact half-up rounding to the cent on the decimal value written."""
        return float(Decimal(str(value)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP))

    @staticmethod
    def text(value) -> str:
        return "%.2f" % _Ledger.cents(value)

    @staticmethod
    def case_row(ctx: ToolContext, medicaid_case_id: str) -> dict:
        rows = ctx.find("medicaid_cases", medicaid_case_id=medicaid_case_id)
        return rows[0] if rows else {}

    @staticmethod
    def charge_month(ctx: ToolContext, charge_entry_id: str) -> str:
        rows = ctx.find("medicaid_ledger", medicaid_entry_id=charge_entry_id)
        return (rows[0].get("service_month") or "") if rows else ""


@tool(owner="agent", rw="write")
def post_cost_of_care_reduction_89ef8a19(ctx: ToolContext, medicaid_case_id: str, charge_entry_id: str, adjustment_reason: str,
                                         amount: float) -> str:
    """Posts a reduction against one patient pay charge billed on the County Assistance Office notice on a Medical Assistance case: the business office
    lowers what the named charge asks of the resident by the amount given and records the reduction, with
    the reason given, on the case's billing record for the same service month as the charge. The case's
    patient pay balance falls by the same amount, so a charge that was already paid leaves a credit the
    resident or representative can see on the case. The call is complete when the receipt below comes back
    with status posted; an amount that is not a positive figure is refused with an error and nothing is
    recorded.

    Args:
        medicaid_case_id: Id class — the reference number of the resident's Medical Assistance case whose
            charge is reduced, as returned by the case lookup.
        charge_entry_id: Id class — the reference number of the patient pay charge being reduced, as
            returned by the case billing-record lookup for that case.
        adjustment_reason: Enum class — the controlled reason recorded on the reduction, one of:
            trueup_decrease — an estimate billed during the pending period is lowered to the month's
            reconciled actual patient pay; patient_pay_redetermined — a charge is lowered because a County
            Assistance Office redetermination set a lower patient pay for that month; not_eligible_month — an
            estimate for a month outside the eligibility period is taken off; cost_of_care_cap — a month's
            patient pay is lowered to the month's cost of care; billing_error — a charge billed in a wrong
            amount is corrected.
        amount: Fixed-format class — the reduction in US dollars, a positive number with 2 decimal places
            (cents), rounded half up to the cent; no currency symbol and no thousands separator.

    Returns:
        A text rendering of a receipt dictionary with these fields: entry_id (string, reference number of
        the new reduction entry), medicaid_case_id (string, the case), charge_entry_id (string, the charge
        reduced), service_month (string YYYY-MM, the charge's service month), adjustment_reason (string, the
        reason recorded), amount (string, US dollars with two decimals), entry_date (string YYYY-MM-DD, the
        posting date), patient_pay_balance (string, the case's patient pay balance in US dollars with two
        decimals with the reduction posted; a leading minus sign means a credit) and status (string,
        posted when the reduction is on the record).
    """
    amt = _Ledger.cents(amount)
    if amt <= 0:
        return "Error: amount must be a positive US dollar figure with two decimals."
    case = _Ledger.case_row(ctx, medicaid_case_id)
    rid = ctx.make_id("mcl_", medicaid_case_id, charge_entry_id, adjustment_reason, amt)
    month = _Ledger.charge_month(ctx, charge_entry_id)
    entry_date = ctx.now()[:10]
    ctx.create("medicaid_ledger", rid, medicaid_entry_id=rid, medicaid_case_id=medicaid_case_id,
               customer_id=case.get("customer_id", ""), event_type="medicaid_patient_pay_adjustment",
               entry_date=entry_date, service_month=month, charge_entry_id=charge_entry_id,
               adjustment_reason=adjustment_reason, amount=amt)
    balance = _Ledger.cents(float(case.get("patient_pay_balance") or 0) - amt)
    ctx.update("medicaid_cases", medicaid_case_id, patient_pay_balance=balance)
    return str({"entry_id": rid, "medicaid_case_id": medicaid_case_id, "charge_entry_id": charge_entry_id,
                "service_month": month, "adjustment_reason": adjustment_reason, "amount": _Ledger.text(amt),
                "entry_date": entry_date, "patient_pay_balance": _Ledger.text(balance), "status": "posted"})


@tool(owner="agent", rw="write")
def post_trueup_decrease_6ec57e06(ctx: ToolContext, medicaid_case_id: str, charge_entry_id: str, adjustment_reason: str,
                                  amount: float) -> str:
    """Posts a reduction against one estimated patient pay charge of an approved case on a Medical Assistance case: the business office
    lowers what the named charge asks of the resident by the amount given and records the reduction, with
    the reason given, on the case's billing record for the same service month as the charge. The case's
    patient pay balance falls by the same amount, so a charge that was already paid leaves a credit the
    resident or representative can see on the case. The call is complete when the receipt below comes back
    with status posted; an amount that is not a positive figure is refused with an error and nothing is
    recorded.

    Args:
        medicaid_case_id: Id class — the reference number of the resident's Medical Assistance case whose
            charge is reduced, as returned by the case lookup.
        charge_entry_id: Id class — the reference number of the estimated patient pay charge being reduced, as
            returned by the case billing-record lookup for that case.
        adjustment_reason: Enum class — the controlled reason recorded on the reduction, one of:
            trueup_decrease — an estimate billed during the pending period is lowered to the month's
            reconciled actual patient pay; patient_pay_redetermined — a charge is lowered because a County
            Assistance Office redetermination set a lower patient pay for that month; not_eligible_month — an
            estimate for a month outside the eligibility period is taken off; cost_of_care_cap — a month's
            patient pay is lowered to the month's cost of care; billing_error — a charge billed in a wrong
            amount is corrected.
        amount: Fixed-format class — the reduction in US dollars, a positive number with 2 decimal places
            (cents), rounded half up to the cent; no currency symbol and no thousands separator.

    Returns:
        A text rendering of a receipt dictionary with these fields: entry_id (string, reference number of
        the new reduction entry), medicaid_case_id (string, the case), charge_entry_id (string, the charge
        reduced), service_month (string YYYY-MM, the charge's service month), adjustment_reason (string, the
        reason recorded), amount (string, US dollars with two decimals), entry_date (string YYYY-MM-DD, the
        posting date), patient_pay_balance (string, the case's patient pay balance in US dollars with two
        decimals with the reduction posted; a leading minus sign means a credit) and status (string,
        posted when the reduction is on the record).
    """
    amt = _Ledger.cents(amount)
    if amt <= 0:
        return "Error: amount must be a positive US dollar figure with two decimals."
    case = _Ledger.case_row(ctx, medicaid_case_id)
    rid = ctx.make_id("mcl_", medicaid_case_id, charge_entry_id, adjustment_reason, amt)
    month = _Ledger.charge_month(ctx, charge_entry_id)
    entry_date = ctx.now()[:10]
    ctx.create("medicaid_ledger", rid, medicaid_entry_id=rid, medicaid_case_id=medicaid_case_id,
               customer_id=case.get("customer_id", ""), event_type="medicaid_patient_pay_adjustment",
               entry_date=entry_date, service_month=month, charge_entry_id=charge_entry_id,
               adjustment_reason=adjustment_reason, amount=amt)
    balance = _Ledger.cents(float(case.get("patient_pay_balance") or 0) - amt)
    ctx.update("medicaid_cases", medicaid_case_id, patient_pay_balance=balance)
    return str({"entry_id": rid, "medicaid_case_id": medicaid_case_id, "charge_entry_id": charge_entry_id,
                "service_month": month, "adjustment_reason": adjustment_reason, "amount": _Ledger.text(amt),
                "entry_date": entry_date, "patient_pay_balance": _Ledger.text(balance), "status": "posted"})


@tool(owner="user", rw="write")
def pay_patient_pay_advance_e93eb0b7(ctx: ToolContext, medicaid_case_id: str, amount: float) -> str:
    """Sends a payment by ACH toward the coming month's patient pay on a Medical Assistance case whose eligibility is approved:
    the resident or representative pays now for a month whose charge does not exist on the record. The
    payment is recorded on the case's billing record as a patient pay payment by ACH that is applied to no
    charge, and the case's patient pay balance falls by the amount paid. The payer sees a confirmation
    number and the new balance; the call is complete when the receipt below comes back with status
    received; an amount that is not a positive figure is refused with an error and nothing is recorded.

    Args:
        medicaid_case_id: Id class — the reference number of the resident's Medical Assistance case the
            payment is made on, as the business office gives it to the payer from the case record.
        amount: Fixed-format class — the payment in US dollars, a positive number with 2 decimal places
            (cents), rounded half up to the cent; no currency symbol and no thousands separator.

    Returns:
        A text rendering of a receipt dictionary with these fields: confirmation_number (string, reference
        number of the payment entry), medicaid_case_id (string, the case paid on), payment_method (string,
        always ach), amount (string, US dollars with two decimals), entry_date (string YYYY-MM-DD, the date
        received), applied_to_charge (string, empty because the payment names no charge),
        patient_pay_balance (string, the case's patient pay balance in US dollars with two decimals with the
        payment posted; a leading minus sign means a credit) and status (string, received when the
        payment is on the record).
    """
    amt = _Ledger.cents(amount)
    if amt <= 0:
        return "Error: amount must be a positive US dollar figure with two decimals."
    case = _Ledger.case_row(ctx, medicaid_case_id)
    rid = ctx.make_id("mcl_", medicaid_case_id, "advance_ach", amt)
    entry_date = ctx.now()[:10]
    ctx.create("medicaid_ledger", rid, medicaid_entry_id=rid, medicaid_case_id=medicaid_case_id,
               customer_id=case.get("customer_id", ""), event_type="medicaid_patient_pay_payment",
               entry_date=entry_date, payment_method="ach", amount=amt)
    balance = _Ledger.cents(float(case.get("patient_pay_balance") or 0) - amt)
    ctx.update("medicaid_cases", medicaid_case_id, patient_pay_balance=balance)
    return str({"confirmation_number": rid, "medicaid_case_id": medicaid_case_id, "payment_method": "ach",
                "amount": _Ledger.text(amt), "entry_date": entry_date, "applied_to_charge": "",
                "patient_pay_balance": _Ledger.text(balance), "status": "received"})


@tool(owner="agent", rw="write")
def post_pending_cost_of_care_reduction_7ee4a52a(ctx: ToolContext, medicaid_case_id: str, charge_entry_id: str, adjustment_reason: str,
                                                 amount: float) -> str:
    """Posts a reduction against one estimated patient pay charge of a case whose application is pending on a Medical Assistance case: the business office
    lowers what the named charge asks of the resident by the amount given and records the reduction, with
    the reason given, on the case's billing record for the same service month as the charge. The case's
    patient pay balance falls by the same amount, so a charge that was already paid leaves a credit the
    resident or representative can see on the case. The call is complete when the receipt below comes back
    with status posted; an amount that is not a positive figure is refused with an error and nothing is
    recorded.

    Args:
        medicaid_case_id: Id class — the reference number of the resident's Medical Assistance case whose
            charge is reduced, as returned by the case lookup.
        charge_entry_id: Id class — the reference number of the estimated patient pay charge being reduced, as
            returned by the case billing-record lookup for that case.
        adjustment_reason: Enum class — the controlled reason recorded on the reduction, one of:
            trueup_decrease — an estimate billed during the pending period is lowered to the month's
            reconciled actual patient pay; patient_pay_redetermined — a charge is lowered because a County
            Assistance Office redetermination set a lower patient pay for that month; not_eligible_month — an
            estimate for a month outside the eligibility period is taken off; cost_of_care_cap — a month's
            patient pay is lowered to the month's cost of care; billing_error — a charge billed in a wrong
            amount is corrected.
        amount: Fixed-format class — the reduction in US dollars, a positive number with 2 decimal places
            (cents), rounded half up to the cent; no currency symbol and no thousands separator.

    Returns:
        A text rendering of a receipt dictionary with these fields: entry_id (string, reference number of
        the new reduction entry), medicaid_case_id (string, the case), charge_entry_id (string, the charge
        reduced), service_month (string YYYY-MM, the charge's service month), adjustment_reason (string, the
        reason recorded), amount (string, US dollars with two decimals), entry_date (string YYYY-MM-DD, the
        posting date), patient_pay_balance (string, the case's patient pay balance in US dollars with two
        decimals with the reduction posted; a leading minus sign means a credit) and status (string,
        posted when the reduction is on the record).
    """
    amt = _Ledger.cents(amount)
    if amt <= 0:
        return "Error: amount must be a positive US dollar figure with two decimals."
    case = _Ledger.case_row(ctx, medicaid_case_id)
    rid = ctx.make_id("mcl_", medicaid_case_id, charge_entry_id, adjustment_reason, amt)
    month = _Ledger.charge_month(ctx, charge_entry_id)
    entry_date = ctx.now()[:10]
    ctx.create("medicaid_ledger", rid, medicaid_entry_id=rid, medicaid_case_id=medicaid_case_id,
               customer_id=case.get("customer_id", ""), event_type="medicaid_patient_pay_adjustment",
               entry_date=entry_date, service_month=month, charge_entry_id=charge_entry_id,
               adjustment_reason=adjustment_reason, amount=amt)
    balance = _Ledger.cents(float(case.get("patient_pay_balance") or 0) - amt)
    ctx.update("medicaid_cases", medicaid_case_id, patient_pay_balance=balance)
    return str({"entry_id": rid, "medicaid_case_id": medicaid_case_id, "charge_entry_id": charge_entry_id,
                "service_month": month, "adjustment_reason": adjustment_reason, "amount": _Ledger.text(amt),
                "entry_date": entry_date, "patient_pay_balance": _Ledger.text(balance), "status": "posted"})


@tool(owner="user", rw="write")
def pay_pending_patient_pay_advance_fe3c809e(ctx: ToolContext, medicaid_case_id: str, amount: float) -> str:
    """Sends a payment by ACH toward the coming month's patient pay on a Medical Assistance case whose application is pending:
    the resident or representative pays now for a month whose charge does not exist on the record. The
    payment is recorded on the case's billing record as a patient pay payment by ACH that is applied to no
    charge, and the case's patient pay balance falls by the amount paid. The payer sees a confirmation
    number and the new balance; the call is complete when the receipt below comes back with status
    received; an amount that is not a positive figure is refused with an error and nothing is recorded.

    Args:
        medicaid_case_id: Id class — the reference number of the resident's Medical Assistance case the
            payment is made on, as the business office gives it to the payer from the case record.
        amount: Fixed-format class — the payment in US dollars, a positive number with 2 decimal places
            (cents), rounded half up to the cent; no currency symbol and no thousands separator.

    Returns:
        A text rendering of a receipt dictionary with these fields: confirmation_number (string, reference
        number of the payment entry), medicaid_case_id (string, the case paid on), payment_method (string,
        always ach), amount (string, US dollars with two decimals), entry_date (string YYYY-MM-DD, the date
        received), applied_to_charge (string, empty because the payment names no charge),
        patient_pay_balance (string, the case's patient pay balance in US dollars with two decimals with the
        payment posted; a leading minus sign means a credit) and status (string, received when the
        payment is on the record).
    """
    amt = _Ledger.cents(amount)
    if amt <= 0:
        return "Error: amount must be a positive US dollar figure with two decimals."
    case = _Ledger.case_row(ctx, medicaid_case_id)
    rid = ctx.make_id("mcl_", medicaid_case_id, "pending_advance_ach", amt)
    entry_date = ctx.now()[:10]
    ctx.create("medicaid_ledger", rid, medicaid_entry_id=rid, medicaid_case_id=medicaid_case_id,
               customer_id=case.get("customer_id", ""), event_type="medicaid_patient_pay_payment",
               entry_date=entry_date, payment_method="ach", amount=amt)
    balance = _Ledger.cents(float(case.get("patient_pay_balance") or 0) - amt)
    ctx.update("medicaid_cases", medicaid_case_id, patient_pay_balance=balance)
    return str({"confirmation_number": rid, "medicaid_case_id": medicaid_case_id, "payment_method": "ach",
                "amount": _Ledger.text(amt), "entry_date": entry_date, "applied_to_charge": "",
                "patient_pay_balance": _Ledger.text(balance), "status": "received"})

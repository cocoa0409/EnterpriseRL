"""Hidden task tools of the hospital_account_billing difficulty (Riverbend Regional Health, Patient
Financial Services). Each tool performs one atomic posting on one hospital account with the values
the caller supplies; none of them checks eligibility, order or any policy condition.
"""

from erlbench import ToolContext, tool


class _Ledger:
    """Shared bookkeeping helpers (static, so they are not exposed as tools)."""

    @staticmethod
    def payment_reference(seed_id: str) -> str:
        digits = str(int(seed_id[-12:], 16) % 10000000).zfill(7)
        return "PMT-" + digits

    @staticmethod
    def cents(value) -> float:
        """Round a USD amount half-up to the cent (a tie at half a cent goes away from zero)."""
        x = float(value)
        sign = -1.0 if x < 0 else 1.0
        return sign * int(abs(x) * 100 + 0.5 + 1e-9) / 100


@tool(owner="agent", rw="write")
def post_noncovered_line_discount_93cdc726(ctx: ToolContext, customer_id: str, encounter_id: str,
                                           source_txn_id: str, amount: float) -> str:
    """Post the uninsured discount on the non-covered amount an insurer released to the patient on one
    insured hospital account. One call books one discount adjustment of kind UNINSURED_DISCOUNT on the
    account, dated today and pointing back to the non-covered patient-liability posting it discounts,
    and lowers the account's patient balance by the amount given. The patient sees the discount on the
    account activity and a correspondingly lower balance; the receipt below confirms the posting.

    Args:
        customer_id: Id class — the patient reference number of the account holder, as returned by the
            patient profile lookup.
        encounter_id: Id class — the hospital account (HAR) number of the account receiving the
            discount, as returned by the hospital-account lookup for this patient.
        source_txn_id: Id class — the reference number of the non-covered patient-liability posting
            being discounted, as shown in that account's activity list.
        amount: Fixed-format class — the discount in USD, a positive amount with 2 decimal places;
            the value is stored rounded half-up to the cent exactly as given.

    Returns:
        A confirmation string with these fields: adjustment reference (the new activity reference
        number), account (the hospital account number), source (the liability posting discounted),
        amount (USD with 2 decimal places), posted (today's date, YYYY-MM-DD), and new balance (the
        account's patient balance in USD with 2 decimal places after this discount). A returned
        adjustment reference means the discount is on the account.
    """
    acct = ctx.find("encounter_accounts", encounter_id=encounter_id)[0]
    amt = _Ledger.cents(amount)
    day = ctx.now()[:10]
    rid = ctx.make_id("etx_", customer_id, encounter_id, source_txn_id, "UNINSURED_DISCOUNT", amt)
    ctx.create("encounter_transactions", rid, encounter_txn_id=rid, encounter_id=encounter_id,
               customer_id=customer_id, event_type="encounter_adjustment_posted",
               adjustment_code="UNINSURED_DISCOUNT", source_txn_id=source_txn_id, amount=amt, posting_date=day)
    new_balance = round(float(acct.get("patient_balance") or 0) - amt, 2)
    ctx.update("encounter_accounts", encounter_id, patient_balance=new_balance)
    return (f"adjustment reference: {rid}; account: {encounter_id}; source: {source_txn_id}; amount: {amt:.2f}; "
            f"posted: {day}; new balance: {new_balance:.2f}")


@tool(owner="user", rw="write")
def pay_insured_balance_in_full_a10a8aeb(ctx: ToolContext, customer_id: str, encounter_id: str,
                                         payment_channel: str, amount: float) -> str:
    """The patient pays off one insured hospital account in full, in their own name and with their own
    payment method. One call posts the patient's payment of the amount given to that account, dated
    today, with a newly issued payment confirmation number; whatever patient balance remains on the
    account after that payment is posted as the account's prompt-pay discount pointing back to the
    payment, and an account left at a zero balance is closed today. The patient sees the payment, the
    discount and the closed account; the receipt below confirms the payment.

    Args:
        customer_id: Id class — the patient reference number of the patient paying, as returned by the
            patient profile lookup and told to the patient by the representative.
        encounter_id: Id class — the hospital account (HAR) number being paid off, as returned by the
            hospital-account lookup and told to the patient by the representative.
        payment_channel: Enum class — how the patient is paying, exactly one of: PORTAL_CARD when the
            patient pays by card through the patient portal; PHONE_CARD when the patient reads a card
            over the phone; ACH_BANK_DRAFT when the patient pays from a checking or savings account by
            bank draft; MAILED_CHECK when the patient's paper check is being applied; POINT_OF_SERVICE
            when the patient pays in person at a Riverbend registration or cashier desk;
            PAYMENT_PLAN_INSTALLMENT when the money is a Riverbend payment plan installment;
            PREPAYMENT_DEPOSIT_APPLIED when the money is a deposit held on an estimate.
        amount: Fixed-format class — the payment in USD, a positive amount with 2 decimal places; the
            value is stored rounded half-up to the cent exactly as given.

    Returns:
        A confirmation string with these fields: payment reference (the newly issued confirmation
        number, PMT- followed by 7 digits), account (the hospital account number), amount paid (USD
        with 2 decimal places), channel (the payment channel), prompt-pay discount (USD with 2 decimal
        places, 0.00 when nothing remained), new balance (USD with 2 decimal places) and status (the
        account's billing status after the payment). A returned payment reference means the payment
        is on the account.
    """
    acct = ctx.find("encounter_accounts", encounter_id=encounter_id)[0]
    amt = _Ledger.cents(amount)
    day = ctx.now()[:10]
    pid = ctx.make_id("etx_", customer_id, encounter_id, "PAYMENT", payment_channel, amt, day)
    ref = _Ledger.payment_reference(pid)
    ctx.create("encounter_transactions", pid, encounter_txn_id=pid, encounter_id=encounter_id,
               customer_id=customer_id, event_type="encounter_payment_posted",
               payment_channel=payment_channel, payment_reference=ref, amount=amt, posting_date=day)
    remaining = round(float(acct.get("patient_balance") or 0) - amt, 2)
    discount = 0.0
    if remaining > 0:
        discount = remaining
        did = ctx.make_id("etx_", encounter_id, pid, "PROMPT_PAY_DISCOUNT", discount)
        ctx.create("encounter_transactions", did, encounter_txn_id=did, encounter_id=encounter_id,
                   customer_id=customer_id, event_type="encounter_adjustment_posted",
                   adjustment_code="PROMPT_PAY_DISCOUNT", source_txn_id=pid, amount=discount, posting_date=day)
        remaining = 0.0
    status = acct.get("status")
    if remaining == 0:
        status = "closed"
        ctx.update("encounter_accounts", encounter_id, patient_balance=0.0, status="closed", closed_date=day)
    else:
        ctx.update("encounter_accounts", encounter_id, patient_balance=remaining)
    return (f"payment reference: {ref}; account: {encounter_id}; amount paid: {amt:.2f}; channel: {payment_channel}; "
            f"prompt-pay discount: {discount:.2f}; new balance: {remaining:.2f}; status: {status}")


@tool(owner="agent", rw="write")
def post_terminated_coverage_discount_f939a41d(ctx: ToolContext, customer_id: str, encounter_id: str,
                                               source_txn_id: str, amount: float) -> str:
    """Post the uninsured discount on the balance a payer released to the patient as coverage terminated,
    on one hospital account whose financial class is now SELF_PAY. One call books one discount
    adjustment of kind UNINSURED_DISCOUNT on the account, dated today and pointing back to the
    coverage-terminated patient-liability posting it discounts, and lowers the account's patient
    balance by the amount given. The patient sees the discount on the account activity and a lower
    balance; the receipt below confirms the posting.

    Args:
        customer_id: Id class — the patient reference number of the account holder, as returned by the
            patient profile lookup.
        encounter_id: Id class — the hospital account (HAR) number of the account receiving the
            discount, as returned by the hospital-account lookup for this patient.
        source_txn_id: Id class — the reference number of the coverage-terminated patient-liability
            posting being discounted, as shown in that account's activity list.
        amount: Fixed-format class — the discount in USD, a positive amount with 2 decimal places;
            the value is stored rounded half-up to the cent exactly as given.

    Returns:
        A confirmation string with these fields: adjustment reference (the new activity reference
        number), account (the hospital account number), source (the liability posting discounted),
        amount (USD with 2 decimal places), posted (today's date, YYYY-MM-DD), and new balance (the
        account's patient balance in USD with 2 decimal places after this discount). A returned
        adjustment reference means the discount is on the account.
    """
    acct = ctx.find("encounter_accounts", encounter_id=encounter_id)[0]
    amt = _Ledger.cents(amount)
    day = ctx.now()[:10]
    rid = ctx.make_id("etx_", customer_id, encounter_id, source_txn_id, "UNINSURED_DISCOUNT", amt)
    ctx.create("encounter_transactions", rid, encounter_txn_id=rid, encounter_id=encounter_id,
               customer_id=customer_id, event_type="encounter_adjustment_posted",
               adjustment_code="UNINSURED_DISCOUNT", source_txn_id=source_txn_id, amount=amt, posting_date=day)
    new_balance = round(float(acct.get("patient_balance") or 0) - amt, 2)
    ctx.update("encounter_accounts", encounter_id, patient_balance=new_balance)
    return (f"adjustment reference: {rid}; account: {encounter_id}; source: {source_txn_id}; amount: {amt:.2f}; "
            f"posted: {day}; new balance: {new_balance:.2f}")


@tool(owner="agent", rw="write")
def post_service_recovery_courtesy_69e36558(ctx: ToolContext, customer_id: str, encounter_id: str,
                                            source_txn_id: str, amount: float) -> str:
    """Post a service-recovery courtesy adjustment on one hospital account for a documented billing
    failure. One call books one adjustment of kind SERVICE_RECOVERY_COURTESY on the account, dated
    today and pointing back to the account record that documents the service failure, and lowers the
    account's patient balance by the amount given. The patient sees the courtesy on the account
    activity and a lower balance; the receipt below confirms the posting.

    Args:
        customer_id: Id class — the patient reference number of the account holder, as returned by the
            patient profile lookup.
        encounter_id: Id class — the hospital account (HAR) number of the account receiving the
            courtesy, as returned by the hospital-account lookup for this patient.
        source_txn_id: Id class — the reference number of the account activity record that documents
            the service failure, as shown in that account's activity list.
        amount: Fixed-format class — the courtesy in USD, a positive amount with 2 decimal places; the
            value is stored rounded half-up to the cent exactly as given.

    Returns:
        A confirmation string with these fields: adjustment reference (the new activity reference
        number), account (the hospital account number), source (the activity record named), amount (USD
        with 2 decimal places), posted (today's date, YYYY-MM-DD), and new balance (the account's
        patient balance in USD with 2 decimal places after this courtesy). A returned adjustment reference
        means the courtesy is on the account.
    """
    acct = ctx.find("encounter_accounts", encounter_id=encounter_id)[0]
    amt = _Ledger.cents(amount)
    day = ctx.now()[:10]
    rid = ctx.make_id("etx_", customer_id, encounter_id, source_txn_id, "SERVICE_RECOVERY_COURTESY", amt)
    ctx.create("encounter_transactions", rid, encounter_txn_id=rid, encounter_id=encounter_id,
               customer_id=customer_id, event_type="encounter_adjustment_posted",
               adjustment_code="SERVICE_RECOVERY_COURTESY", source_txn_id=source_txn_id, amount=amt, posting_date=day)
    new_balance = round(float(acct.get("patient_balance") or 0) - amt, 2)
    ctx.update("encounter_accounts", encounter_id, patient_balance=new_balance)
    return (f"adjustment reference: {rid}; account: {encounter_id}; source: {source_txn_id}; amount: {amt:.2f}; "
            f"posted: {day}; new balance: {new_balance:.2f}")


@tool(owner="user", rw="write")
def pay_self_pay_balance_in_full_3917aa11(ctx: ToolContext, customer_id: str, encounter_id: str,
                                          payment_channel: str, amount: float) -> str:
    """The patient pays off one self-pay hospital account in full, in their own name and with their own
    payment method. One call posts the patient's payment of the amount given to that account, dated
    today, with a newly issued payment confirmation number; whatever patient balance remains on the
    account after that payment is posted as the account's prompt-pay discount pointing back to the
    payment, and an account left at a zero balance is closed today. The patient sees the payment, the
    discount and the closed account; the receipt below confirms the payment.

    Args:
        customer_id: Id class — the patient reference number of the patient paying, as returned by the
            patient profile lookup and told to the patient by the representative.
        encounter_id: Id class — the hospital account (HAR) number being paid off, as returned by the
            hospital-account lookup and told to the patient by the representative.
        payment_channel: Enum class — how the patient is paying, exactly one of: PORTAL_CARD when the
            patient pays by card through the patient portal; PHONE_CARD when the patient reads a card
            over the phone; ACH_BANK_DRAFT when the patient pays from a checking or savings account by
            bank draft; MAILED_CHECK when the patient's paper check is being applied; POINT_OF_SERVICE
            when the patient pays in person at a Riverbend registration or cashier desk;
            PAYMENT_PLAN_INSTALLMENT when the money is a Riverbend payment plan installment;
            PREPAYMENT_DEPOSIT_APPLIED when the money is a deposit held on an estimate.
        amount: Fixed-format class — the payment in USD, a positive amount with 2 decimal places; the
            value is stored rounded half-up to the cent exactly as given.

    Returns:
        A confirmation string with these fields: payment reference (the newly issued confirmation
        number, PMT- followed by 7 digits), account (the hospital account number), amount paid (USD
        with 2 decimal places), channel (the payment channel), prompt-pay discount (USD with 2 decimal
        places, 0.00 when nothing remained), new balance (USD with 2 decimal places) and status (the
        account's billing status after the payment). A returned payment reference means the payment
        is on the account.
    """
    acct = ctx.find("encounter_accounts", encounter_id=encounter_id)[0]
    amt = _Ledger.cents(amount)
    day = ctx.now()[:10]
    pid = ctx.make_id("etx_", customer_id, encounter_id, "PAYMENT", payment_channel, amt, day)
    ref = _Ledger.payment_reference(pid)
    ctx.create("encounter_transactions", pid, encounter_txn_id=pid, encounter_id=encounter_id,
               customer_id=customer_id, event_type="encounter_payment_posted",
               payment_channel=payment_channel, payment_reference=ref, amount=amt, posting_date=day)
    remaining = round(float(acct.get("patient_balance") or 0) - amt, 2)
    discount = 0.0
    if remaining > 0:
        discount = remaining
        did = ctx.make_id("etx_", encounter_id, pid, "PROMPT_PAY_DISCOUNT", discount)
        ctx.create("encounter_transactions", did, encounter_txn_id=did, encounter_id=encounter_id,
                   customer_id=customer_id, event_type="encounter_adjustment_posted",
                   adjustment_code="PROMPT_PAY_DISCOUNT", source_txn_id=pid, amount=discount, posting_date=day)
        remaining = 0.0
    status = acct.get("status")
    if remaining == 0:
        status = "closed"
        ctx.update("encounter_accounts", encounter_id, patient_balance=0.0, status="closed", closed_date=day)
    else:
        ctx.update("encounter_accounts", encounter_id, patient_balance=remaining)
    return (f"payment reference: {ref}; account: {encounter_id}; amount paid: {amt:.2f}; channel: {payment_channel}; "
            f"prompt-pay discount: {discount:.2f}; new balance: {remaining:.2f}; status: {status}")


@tool(owner="agent", rw="write")
def post_observation_rate_discount_cc1ec28d(ctx: ToolContext, customer_id: str, encounter_id: str,
                                            source_txn_id: str, amount: float) -> str:
    """Post Riverbend's self-pay observation-rate discount on one self-pay hospital account that carries
    observation-hour charges. One call books one discount adjustment of kind UNINSURED_DISCOUNT on the
    account, dated today and pointing back to the observation-hour charge line it is figured on, and
    lowers the account's patient balance by the amount given. The patient sees the discount on the
    account activity and a lower balance; the receipt below confirms the posting.

    Args:
        customer_id: Id class — the patient reference number of the account holder, as returned by the
            patient profile lookup.
        encounter_id: Id class — the hospital account (HAR) number of the account receiving the
            discount, as returned by the hospital-account lookup for this patient.
        source_txn_id: Id class — the reference number of the observation-hour charge line the discount
            points to, as shown in that account's activity list.
        amount: Fixed-format class — the discount in USD, a positive amount with 2 decimal places; the
            value is stored rounded half-up to the cent exactly as given.

    Returns:
        A confirmation string with these fields: adjustment reference (the new activity reference
        number), account (the hospital account number), source (the charge line named), amount (USD
        with 2 decimal places), posted (today's date, YYYY-MM-DD), and new balance (the account's
        patient balance in USD with 2 decimal places after this discount). A returned adjustment
        reference means the discount is on the account.
    """
    acct = ctx.find("encounter_accounts", encounter_id=encounter_id)[0]
    amt = _Ledger.cents(amount)
    day = ctx.now()[:10]
    rid = ctx.make_id("etx_", customer_id, encounter_id, source_txn_id, "UNINSURED_DISCOUNT_OBS", amt)
    ctx.create("encounter_transactions", rid, encounter_txn_id=rid, encounter_id=encounter_id,
               customer_id=customer_id, event_type="encounter_adjustment_posted",
               adjustment_code="UNINSURED_DISCOUNT", source_txn_id=source_txn_id, amount=amt, posting_date=day)
    new_balance = round(float(acct.get("patient_balance") or 0) - amt, 2)
    ctx.update("encounter_accounts", encounter_id, patient_balance=new_balance)
    return (f"adjustment reference: {rid}; account: {encounter_id}; source: {source_txn_id}; amount: {amt:.2f}; "
            f"posted: {day}; new balance: {new_balance:.2f}")

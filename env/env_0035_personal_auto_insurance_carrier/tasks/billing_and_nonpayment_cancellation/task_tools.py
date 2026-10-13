"""Hidden task tools for the billing_and_nonpayment_cancellation difficulty of
env_0035_personal_auto_insurance_carrier (Cardinal Billing Account).

Each tool performs one atomic write on a billing account and its ledger, with the values the
caller has already worked out. No tool checks eligibility, prior steps or amounts.
"""

from erlbench import ToolContext, tool


@tool(owner="agent", rw="write")
def charge_late_fee_8c3b3141(ctx: ToolContext, billing_account_id: str, installment_number: int,
                             amount: float) -> str:
    """Charge a late fee on one installment of the term a Cardinal billing account is currently
    billing. One call posts a single late fee entry on the account's billing history, tied to the
    installment named, dated today, and raises the account balance (what the customer owes) by the
    fee. The customer sees the late fee as a new charge on the account. The receipt confirms the
    entry reference and the new balance.

    Args:
        billing_account_id: Id class — the billing account reference number, as returned by the
            billing account lookup for the customer's policy.
        installment_number: Fixed-format class — the number of the installment of the current term
            the fee is charged on, exactly as shown on that installment's invoice entry in the
            billing history (1 is the down payment); stored format integer >= 1, empty if none,
            and never empty for this charge.
        amount: Fixed-format class — the late fee charged, in USD, a positive amount with 2 decimal
            places, already rounded to the cent.

    Returns:
        A dictionary rendered as text with: entry_id (string, reference of the new late fee entry),
        billing_account_id (string, the account charged), fee_type (always "late_fee"),
        installment_number (integer, the installment charged), amount (number, USD with 2 decimal
        places, the fee posted), posted_date (YYYY-MM-DD, today's date) and account_balance (number,
        USD with 2 decimal places, the resulting balance; positive means the customer owes).
        A returned entry_id means the fee is posted.
    """
    acct = ctx.find("billing_accounts", billing_account_id=billing_account_id)[0]
    fee = round(float(amount), 2)
    eid = ctx.make_id("led_", billing_account_id, "late_fee", installment_number, fee)
    today = ctx.now()[:10]
    ctx.create("billing_ledger", eid, entry_id=eid, billing_account_id=billing_account_id,
               customer_id=acct["customer_id"], policy_id=acct["policy_id"],
               event_type="billing_fee_charged", fee_type="late_fee", amount=fee,
               term_effective_date=acct["term_effective_date"],
               installment_number=int(installment_number), posted_date=today)
    balance = round(float(acct["account_balance"]) + fee, 2)
    ctx.update("billing_accounts", billing_account_id, account_balance=balance)
    return str({"entry_id": eid, "billing_account_id": billing_account_id, "fee_type": "late_fee",
                "installment_number": int(installment_number), "amount": fee,
                "posted_date": today, "account_balance": balance})


@tool(owner="agent", rw="write")
def bill_renewal_down_payment_49af2eee(ctx: ToolContext, billing_account_id: str,
                                       term_effective_date: str, amount: float,
                                       policy_fee: float) -> str:
    """Issue the down payment invoice of a policy's renewal term on its Cardinal billing account.
    One call posts installment 1 of the renewal term (invoiced today, due on the renewal term's first
    day) together with the auto package's policy fee for that term, and raises the account balance
    by both. The customer sees a new renewal down payment invoice and policy fee on the account. The
    receipt confirms both entry references, the due date and the new balance.

    Args:
        billing_account_id: Id class — the billing account reference number, as returned by the
            billing account lookup for the customer's policy.
        term_effective_date: Fixed-format class — the first day of the renewal term being invoiced,
            in YYYY-MM-DD format, which is also the invoice's due date.
        amount: Fixed-format class — the premium portion of the renewal down payment (installment
            1), in USD, a positive amount with 2 decimal places, already rounded to the cent.
        policy_fee: Fixed-format class — the auto package's policy fee for the renewal term, in USD,
            an amount with 2 decimal places (0.00 when the package carries none).

    Returns:
        A dictionary rendered as text with: entry_id (string, reference of the installment 1
        invoice entry), fee_entry_id (string, reference of the policy fee entry, empty when the fee
        is 0.00), billing_account_id (string), term_effective_date (YYYY-MM-DD, the renewal term),
        installment_number (always 1), amount (number, USD with 2 decimal places, the premium
        invoiced), policy_fee (number, USD with 2 decimal places), due_date (YYYY-MM-DD) and
        account_balance (number, USD with 2 decimal places, the resulting balance). A
        returned entry_id means the invoice is issued.
    """
    acct = ctx.find("billing_accounts", billing_account_id=billing_account_id)[0]
    prem = round(float(amount), 2)
    fee = round(float(policy_fee), 2)
    today = ctx.now()[:10]
    eid = ctx.make_id("led_", billing_account_id, "renewal_down", term_effective_date, prem)
    ctx.create("billing_ledger", eid, entry_id=eid, billing_account_id=billing_account_id,
               customer_id=acct["customer_id"], policy_id=acct["policy_id"],
               event_type="billing_installment_billed", term_effective_date=term_effective_date,
               installment_number=1, invoice_date=today, due_date=term_effective_date,
               amount=prem, posted_date=today)
    fid = ""
    if fee > 0:
        fid = ctx.make_id("led_", billing_account_id, "policy_fee", term_effective_date, fee)
        ctx.create("billing_ledger", fid, entry_id=fid, billing_account_id=billing_account_id,
                   customer_id=acct["customer_id"], policy_id=acct["policy_id"],
                   event_type="billing_fee_charged", fee_type="policy_fee", amount=fee,
                   term_effective_date=term_effective_date, posted_date=today)
    balance = round(float(acct["account_balance"]) + prem + fee, 2)
    ctx.update("billing_accounts", billing_account_id, account_balance=balance)
    return str({"entry_id": eid, "fee_entry_id": fid, "billing_account_id": billing_account_id,
                "term_effective_date": term_effective_date, "installment_number": 1,
                "amount": prem, "policy_fee": fee, "due_date": term_effective_date,
                "account_balance": balance})


@tool(owner="agent", rw="write")
def bill_additional_premium_a7869908(ctx: ToolContext, billing_account_id: str,
                                     source_transaction_id: str, amount: float,
                                     due_date: str) -> str:
    """Bill an additional premium at once on a Cardinal billing account, outside the installment
    schedule. One call posts a single additional-premium bill entry tied to the policy's additional
    premium transaction, dated today with the due date given, and raises the account balance by the
    amount billed. The customer sees a new bill for the policy change on the account. The receipt
    confirms the entry reference, the amount, the due date and the new balance.

    Args:
        billing_account_id: Id class — the billing account reference number, as returned by the
            billing account lookup for the customer's policy.
        source_transaction_id: Id class — the reference number of the policy's additional premium
            transaction being billed, as shown on the premium-received entry of the billing history
            (its source transaction) or in the policy's transaction history.
        amount: Fixed-format class — the total amount billed, in USD, a positive amount with 2
            decimal places, already rounded to the cent.
        due_date: Fixed-format class — the date the bill falls due, in YYYY-MM-DD format.

    Returns:
        A dictionary rendered as text with: entry_id (string, reference of the new bill entry),
        billing_account_id (string), source_transaction_id (string, the additional premium
        transaction billed), amount (number, USD with 2 decimal places), due_date (YYYY-MM-DD),
        posted_date (YYYY-MM-DD, today's date) and account_balance (number, USD with 2 decimal
        places, the resulting balance). A returned entry_id means the bill is posted.
    """
    acct = ctx.find("billing_accounts", billing_account_id=billing_account_id)[0]
    amt = round(float(amount), 2)
    today = ctx.now()[:10]
    eid = ctx.make_id("led_", billing_account_id, "ap_bill", source_transaction_id, amt, due_date)
    ctx.create("billing_ledger", eid, entry_id=eid, billing_account_id=billing_account_id,
               customer_id=acct["customer_id"], policy_id=acct["policy_id"],
               event_type="billing_endorsement_charge", source_transaction_id=source_transaction_id,
               amount=amt, due_date=due_date, term_effective_date=acct["term_effective_date"],
               posted_date=today)
    balance = round(float(acct["account_balance"]) + amt, 2)
    ctx.update("billing_accounts", billing_account_id, account_balance=balance)
    return str({"entry_id": eid, "billing_account_id": billing_account_id,
                "source_transaction_id": source_transaction_id, "amount": amt,
                "due_date": due_date, "posted_date": today, "account_balance": balance})


@tool(owner="user", rw="write")
def pay_balance_by_phone_6aa6e134(ctx: ToolContext, billing_account_id: str, amount: float,
                                  representative_fee: float, payment_method: str) -> str:
    """The named insured authorizes, with a Cardinal representative on the line, a one-time
    payment from their own card or bank account to their billing account. One call posts the payment
    (channel: phone representative) and, when the representative payment fee is above 0.00, the fee
    tied to that payment; the account balance falls by the payment and rises by the fee. The
    customer receives a payment confirmation number. The receipt confirms the confirmation number,
    the amounts and the new balance.

    Args:
        billing_account_id: Id class — the billing account reference number the payment is applied
            to, as given by the representative from the billing account lookup.
        amount: Fixed-format class — the total charged to the customer's card or bank account, in
            USD, a positive amount with 2 decimal places, already rounded to the cent.
        representative_fee: Fixed-format class — the representative payment fee included in that
            total, in USD, an amount with 2 decimal places (0.00 when no fee applies).
        payment_method: Enum class — how the customer pays: check_or_money_order when paying by
            check or money order; credit_card when paying with a credit card; debit_card when
            paying with a debit card; bank_eft when paying straight from a checking or savings
            account; cashiers_check when paying with a cashier's check.

    Returns:
        A dictionary rendered as text with: entry_id (string, reference of the payment entry),
        payment_reference (string, the confirmation number given to the customer),
        fee_entry_id (string, reference of the representative fee entry, empty when the fee is
        0.00), billing_account_id (string), amount (number, USD with 2 decimal places, the amount
        paid), representative_fee (number, USD with 2 decimal places), payment_method (string),
        posted_date (YYYY-MM-DD, today's date) and account_balance (number, USD with 2 decimal
        places, the resulting balance; 0.00 means nothing is owed). A returned
        payment_reference means the payment is posted.
    """
    acct = ctx.find("billing_accounts", billing_account_id=billing_account_id)[0]
    amt = round(float(amount), 2)
    fee = round(float(representative_fee), 2)
    today = ctx.now()[:10]
    eid = ctx.make_id("led_", billing_account_id, "phone_payment", amt, fee, payment_method, today)
    ref = ctx.make_id("CNF-", billing_account_id, amt, payment_method, today, length=10).upper()
    ctx.create("billing_ledger", eid, entry_id=eid, billing_account_id=billing_account_id,
               customer_id=acct["customer_id"], policy_id=acct["policy_id"],
               event_type="billing_payment_received", payment_reference=ref,
               payment_method=payment_method, payment_channel="phone_representative",
               amount=amt, term_effective_date=acct["term_effective_date"], posted_date=today)
    fid = ""
    if fee > 0:
        fid = ctx.make_id("led_", billing_account_id, "phone_payment_fee", eid, fee)
        ctx.create("billing_ledger", fid, entry_id=fid, billing_account_id=billing_account_id,
                   customer_id=acct["customer_id"], policy_id=acct["policy_id"],
                   event_type="billing_fee_charged", fee_type="phone_payment_fee", amount=fee,
                   original_entry_id=eid, term_effective_date=acct["term_effective_date"],
                   posted_date=today)
    balance = round(float(acct["account_balance"]) - amt + fee, 2)
    ctx.update("billing_accounts", billing_account_id, account_balance=balance)
    return str({"entry_id": eid, "payment_reference": ref, "fee_entry_id": fid,
                "billing_account_id": billing_account_id, "amount": amt,
                "representative_fee": fee, "payment_method": payment_method,
                "posted_date": today, "account_balance": balance})


@tool(owner="agent", rw="write")
def invoice_installment_259ff7d9(ctx: ToolContext, billing_account_id: str, installment_number: int,
                                 due_date: str, premium_amount: float, installment_fee: float) -> str:
    """Issue the invoice of one installment of the term a Cardinal billing account is currently
    billing. One call posts the installment (invoiced today, due on the date given) and, when the
    installment charge is above 0.00, that charge tied to the same installment, and raises the
    account balance by both. The customer sees a new installment invoice on the account. The receipt
    confirms both entry references, the amounts, the due date and the new balance.

    Args:
        billing_account_id: Id class — the billing account reference number, as returned by the
            billing account lookup for the customer's policy.
        installment_number: Fixed-format class — the number of the installment of the current term
            being invoiced (1 is the down payment); stored format integer >= 1, empty if none, and
            never empty for an invoice.
        due_date: Fixed-format class — the installment's due date, in YYYY-MM-DD format.
        premium_amount: Fixed-format class — the premium portion of the installment, in USD, a
            positive amount with 2 decimal places, already rounded to the cent.
        installment_fee: Fixed-format class — the installment charge added to this invoice, in USD,
            an amount with 2 decimal places, already rounded to the cent (0.00 when none).

    Returns:
        A dictionary rendered as text with: entry_id (string, reference of the installment invoice
        entry), fee_entry_id (string, reference of the installment charge entry, empty when the
        charge is 0.00), billing_account_id (string), installment_number (integer), premium_amount
        (number, USD with 2 decimal places), installment_fee (number, USD with 2 decimal places),
        due_date (YYYY-MM-DD), invoice_date (YYYY-MM-DD, today's date) and account_balance (number,
        USD with 2 decimal places, the resulting balance). A returned entry_id means the
        invoice is issued.
    """
    acct = ctx.find("billing_accounts", billing_account_id=billing_account_id)[0]
    prem = round(float(premium_amount), 2)
    fee = round(float(installment_fee), 2)
    today = ctx.now()[:10]
    term = acct["term_effective_date"]
    eid = ctx.make_id("led_", billing_account_id, "installment", term, installment_number, prem)
    ctx.create("billing_ledger", eid, entry_id=eid, billing_account_id=billing_account_id,
               customer_id=acct["customer_id"], policy_id=acct["policy_id"],
               event_type="billing_installment_billed", term_effective_date=term,
               installment_number=int(installment_number), invoice_date=today, due_date=due_date,
               amount=prem, posted_date=today)
    fid = ""
    if fee > 0:
        fid = ctx.make_id("led_", billing_account_id, "installment_fee", term, installment_number, fee)
        ctx.create("billing_ledger", fid, entry_id=fid, billing_account_id=billing_account_id,
                   customer_id=acct["customer_id"], policy_id=acct["policy_id"],
                   event_type="billing_fee_charged", fee_type="installment_fee", amount=fee,
                   term_effective_date=term, installment_number=int(installment_number),
                   posted_date=today)
    balance = round(float(acct["account_balance"]) + prem + fee, 2)
    ctx.update("billing_accounts", billing_account_id, account_balance=balance)
    return str({"entry_id": eid, "fee_entry_id": fid, "billing_account_id": billing_account_id,
                "installment_number": int(installment_number), "premium_amount": prem,
                "installment_fee": fee, "due_date": due_date, "invoice_date": today,
                "account_balance": balance})


@tool(owner="user", rw="write")
def pay_term_payoff_2a94a5fa(ctx: ToolContext, billing_account_id: str, amount: float,
                             payment_method: str) -> str:
    """The named insured, on Cardinal's automated payment line, pays off the current term of their
    billing account in advance from their own card or bank account. One call posts the payment
    (channel: automated phone line, no fee) and lowers the account balance by the amount paid; any
    part above the balance stays on the account as a credit for the installments still to come. The
    customer receives a payment confirmation number. The receipt confirms the confirmation number, the
    amount and the new balance.

    Args:
        billing_account_id: Id class — the billing account reference number the payoff is applied
            to, as given by the representative from the billing account lookup.
        amount: Fixed-format class — the payoff amount charged to the customer's card or bank
            account, in USD, a positive amount with 2 decimal places, already rounded to the cent.
        payment_method: Enum class — how the customer pays: check_or_money_order when paying by
            check or money order; credit_card when paying with a credit card; debit_card when
            paying with a debit card; bank_eft when paying straight from a checking or savings
            account; cashiers_check when paying with a cashier's check.

    Returns:
        A dictionary rendered as text with: entry_id (string, reference of the payment entry),
        payment_reference (string, the confirmation number given to the customer),
        billing_account_id (string), amount (number, USD with 2 decimal places, the amount paid),
        payment_method (string), posted_date (YYYY-MM-DD, today's date) and account_balance (number,
        USD with 2 decimal places, the resulting balance; negative means a credit held for
        the installments still to come). A returned payment_reference means the payoff is posted.
    """
    acct = ctx.find("billing_accounts", billing_account_id=billing_account_id)[0]
    amt = round(float(amount), 2)
    today = ctx.now()[:10]
    eid = ctx.make_id("led_", billing_account_id, "term_payoff", amt, payment_method, today)
    ref = ctx.make_id("CNF-", billing_account_id, "payoff", amt, today, length=10).upper()
    ctx.create("billing_ledger", eid, entry_id=eid, billing_account_id=billing_account_id,
               customer_id=acct["customer_id"], policy_id=acct["policy_id"],
               event_type="billing_payment_received", payment_reference=ref,
               payment_method=payment_method, payment_channel="automated_phone", amount=amt,
               term_effective_date=acct["term_effective_date"], posted_date=today)
    balance = round(float(acct["account_balance"]) - amt, 2)
    ctx.update("billing_accounts", billing_account_id, account_balance=balance)
    return str({"entry_id": eid, "payment_reference": ref, "billing_account_id": billing_account_id,
                "amount": amt, "payment_method": payment_method, "posted_date": today,
                "account_balance": balance})

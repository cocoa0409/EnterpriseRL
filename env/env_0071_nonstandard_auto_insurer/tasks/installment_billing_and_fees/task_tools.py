"""Hidden task tools for env_0071_nonstandard_auto_insurer / installment_billing_and_fees (category billing).

Each tool lands one atomic billing action on one installment payment plan; it judges no eligibility, timing or
prerequisite and computes no policy amount. Every amount is passed in already worked out.
"""

from erlbench import ToolContext, tool


class _Ledger:
    """Shared bookkeeping helpers (not tools)."""

    @staticmethod
    def plan_row(ctx, billing_plan_id):
        rows = ctx.find("billing_plans", billing_plan_id=billing_plan_id)
        return rows[0] if rows else {}

    @staticmethod
    def confirmation(row_id):
        digits = int(row_id.split("_")[-1], 16) % 1000000000
        return "PMT-1" + str(digits).zfill(9)


@tool(owner="agent", rw="write")
def issue_draft_notice_1682239d(ctx: ToolContext, billing_plan_id: str, installment_number: int, due_date: str,
                                premium_amount: float, fee_amount: float, past_due_amount: float,
                                minimum_due: float) -> str:
    """Issue the installment invoice (the draft notice on an automatic-draft plan) for one installment of an
    installment payment plan, dated today, and charge that invoice's installment fee to the plan. On success a new
    installment invoice stands on the plan for the stated installment with the stated due date, premium, fee,
    carried amount and minimum due; a matching installment fee charge for the invoice is posted today; and the
    plan's account balance rises by the fee. The customer sees the invoice and its minimum due on the plan.

    Args:
        billing_plan_id: Id class — the reference number of the installment payment plan being invoiced, read
            from the plan record returned by the plan lookup.
        installment_number: Fixed-format class — the number of the installment this invoice bills, an integer >= 0
            (installments are counted from 1 for the plan's earliest installment), no padding.
        due_date: Fixed-format class — the date the invoiced amount is due, written YYYY-MM-DD as a calendar
            date with no time and no time zone.
        premium_amount: Fixed-format class — the premium portion the invoice bills, in USD with 2 decimal places (a
            decimal number), already rounded to the cent.
        fee_amount: Fixed-format class — the installment fee the invoice bills and the fee charge posted with
            it, in USD with 2 decimal places, already rounded to the cent.
        past_due_amount: Fixed-format class — the amount carried onto the invoice from the plan's earlier
            billing, in USD with 2 decimal places, already rounded to the cent; a credit
            held on the plan is written as a negative amount and nothing carried as 0.00.
        minimum_due: Fixed-format class — the amount due by the due date, in USD with 2 decimal places, already rounded to the cent.

    Returns:
        A confirmation sentence (string) stating the new invoice reference number, the installment fee charge
        reference number, the installment number, the due date (YYYY-MM-DD), the premium, fee, carried amount
        and minimum due (US dollars, two decimals) and the plan's account balance after the fee (US dollars,
        two decimals). The presence of both reference numbers indicates the invoice was issued and its fee
        charged.
    """
    plan = _Ledger.plan_row(ctx, billing_plan_id)
    today = ctx.now()[:10]
    inv = ctx.make_id("binv_", billing_plan_id, installment_number, due_date, premium_amount, fee_amount,
                      past_due_amount, minimum_due)
    ctx.create("billing_invoices", inv, billing_invoice_id=inv, billing_plan_id=billing_plan_id,
               customer_id=plan.get("customer_id", ""), event_type="billing_installment_billed",
               invoice_date=today, due_date=due_date, installment_number=int(installment_number),
               premium_amount=round(float(premium_amount), 2), fee_amount=round(float(fee_amount), 2),
               past_due_amount=round(float(past_due_amount), 2), minimum_due=round(float(minimum_due), 2))
    fee = ctx.make_id("btx_", inv, "installment_fee", fee_amount)
    ctx.create("billing_transactions", fee, billing_txn_id=fee, billing_plan_id=billing_plan_id,
               customer_id=plan.get("customer_id", ""), event_type="billing_installment_fee", posted_date=today,
               amount=round(float(fee_amount), 2), installment_number=int(installment_number),
               related_invoice_id=inv)
    balance = round(float(plan.get("account_balance") or 0) + round(float(fee_amount), 2), 2)
    if plan:
        ctx.update("billing_plans", billing_plan_id, account_balance=balance)
    return (f"Installment invoice {inv} issued for installment {int(installment_number)}, due {due_date}: premium "
            f"{round(float(premium_amount), 2):.2f}, fee {round(float(fee_amount), 2):.2f}, carried "
            f"{round(float(past_due_amount), 2):.2f}, minimum due {round(float(minimum_due), 2):.2f}. Installment fee "
            f"charge {fee} posted; plan balance now {balance:.2f}.")


@tool(owner="user", rw="write")
def authorize_endorsement_deposit_3483f9bd(ctx: ToolContext, billing_plan_id: str, source_auto_txn_id: str,
                                           payment_method: str, amount: float) -> str:
    """The named insured personally authorizes a one-time payment, taken today by a representative over the
    phone, toward the additional premium of an endorsement on the owner auto term the plan bills. On success a
    payment for the authorized amount is posted to the plan today through the representative phone channel,
    linked to that additional premium transaction and to no invoice, the plan's account balance falls by the
    amount, and a payment confirmation number is issued to the customer.

    Args:
        billing_plan_id: Id class — the reference number of the installment payment plan that receives the
            payment, read from the plan record returned by the plan lookup.
        source_auto_txn_id: Id class — the reference number of the additional premium transaction of the owner
            auto term that the payment goes toward, read from the owner term's premium transaction lookup.
        payment_method: Enum class — how the customer pays, exactly one of:
            debit_card — the customer pays with a debit card they hold and state;
            credit_card — the customer pays with a credit card they hold and state;
            bank_ach — the customer pays from a checking or savings account they hold, by routing and account number;
            personal_check — a paper check the customer has mailed or handed in, never one taken over the phone;
            money_order — a money order the customer has mailed or handed in, never one taken over the phone;
            cashiers_check — a cashier's check the customer has mailed or handed in, never one taken over the phone;
            cash — cash handed in at an agent office, never one taken over the phone.
        amount: Fixed-format class — the amount the customer authorizes, in USD with 2 decimal places (a
            decimal number), already rounded to the cent.

    Returns:
        A confirmation sentence (string) stating the payment confirmation number (PMT- followed by ten digits),
        the payment reference number, the amount (US dollars, two decimals), the method, the posting date
        (YYYY-MM-DD) and the plan's account balance after the payment (US dollars, two decimals). The
        confirmation number indicates the payment was accepted and posted.
    """
    plan = _Ledger.plan_row(ctx, billing_plan_id)
    today = ctx.now()[:10]
    pid = ctx.make_id("btx_", billing_plan_id, source_auto_txn_id, payment_method, amount, "endorsement_deposit")
    conf = _Ledger.confirmation(pid)
    ctx.create("billing_transactions", pid, billing_txn_id=pid, billing_plan_id=billing_plan_id,
               customer_id=plan.get("customer_id", ""), event_type="billing_payment_received", posted_date=today,
               amount=round(float(amount), 2), installment_number=0, related_invoice_id=None,
               source_auto_txn_id=source_auto_txn_id, payment_method=payment_method,
               payment_channel="agent_phone", confirmation_number=conf)
    balance = round(float(plan.get("account_balance") or 0) - round(float(amount), 2), 2)
    if plan:
        ctx.update("billing_plans", billing_plan_id, account_balance=balance)
    return (f"Payment {conf} accepted: {round(float(amount), 2):.2f} by {payment_method} posted {today} as payment "
            f"{pid} toward additional premium {source_auto_txn_id}; plan balance now {balance:.2f}.")


@tool(owner="user", rw="write")
def authorize_makeup_payment_1af63ac0(ctx: ToolContext, billing_plan_id: str, related_invoice_id: str,
                                      related_payment_txn_id: str, payment_method: str, amount: float) -> str:
    """The named insured personally authorizes a one-time payment, taken today by a representative over the phone,
    that makes good a payment the bank returned on an installment payment plan. On success a payment for the
    authorized amount is posted to the plan today through the representative phone channel, linked to the invoice the
    returned payment had paid and referencing the returned payment it makes good, the plan's account balance falls by the
    amount, and a payment confirmation number is issued to the customer.

    Args:
        billing_plan_id: Id class — the reference number of the installment payment plan that receives the payment,
            read from the plan record returned by the plan lookup.
        related_invoice_id: Id class — the reference number of the installment invoice the returned payment had paid,
            read from the plan's invoice and ledger lookups.
        related_payment_txn_id: Id class — the reference number of the original payment the bank returned, which this
            payment makes good, read from the plan ledger lookup.
        payment_method: Enum class — how the customer pays, exactly one of:
            debit_card — the customer pays with a debit card they hold and state;
            credit_card — the customer pays with a credit card they hold and state;
            bank_ach — the customer pays from a checking or savings account they hold, by routing and account number;
            personal_check — a paper check the customer has mailed or handed in, never one taken over the phone;
            money_order — a money order the customer has mailed or handed in, never one taken over the phone;
            cashiers_check — a cashier's check the customer has mailed or handed in, never one taken over the phone;
            cash — cash handed in at an agent office, never one taken over the phone.
        amount: Fixed-format class — the amount the customer authorizes, in USD with 2 decimal places, already
            rounded to the cent.

    Returns:
        A confirmation sentence (string) stating the payment confirmation number (PMT- followed by ten digits), the
        payment reference number, the amount (USD, two decimals), the method, the posting date (YYYY-MM-DD) and the
        plan's account balance after the payment (USD, two decimals). The confirmation number indicates the payment
        was accepted and posted.
    """
    plan = _Ledger.plan_row(ctx, billing_plan_id)
    today = ctx.now()[:10]
    pid = ctx.make_id("btx_", billing_plan_id, related_invoice_id, related_payment_txn_id, payment_method, amount, "makeup")
    conf = _Ledger.confirmation(pid)
    ctx.create("billing_transactions", pid, billing_txn_id=pid, billing_plan_id=billing_plan_id,
               customer_id=plan.get("customer_id", ""), event_type="billing_payment_received", posted_date=today,
               amount=round(float(amount), 2), installment_number=0, related_invoice_id=related_invoice_id,
               related_payment_txn_id=related_payment_txn_id, payment_method=payment_method, payment_channel="agent_phone",
               confirmation_number=conf)
    balance = round(float(plan.get("account_balance") or 0) - round(float(amount), 2), 2)
    if plan:
        ctx.update("billing_plans", billing_plan_id, account_balance=balance)
    return (f"Payment {conf} accepted: {round(float(amount), 2):.2f} by {payment_method} posted {today} as payment "
            f"{pid} against invoice {related_invoice_id}; plan balance now {balance:.2f}.")


@tool(owner="user", rw="write")
def authorize_switch_down_payment_5d76e7dc(ctx: ToolContext, billing_plan_id: str, installment_number: int,
                                           payment_method: str, amount: float) -> str:
    """The named insured personally authorizes a one-time payment, taken today by a representative over the phone,
    that pays the down payment a move of the installment payment plan to another payment plan requires. On success a
    payment for the authorized amount is posted to the plan today through the representative phone channel, recorded
    toward the stated installment and linked to no invoice and to no endorsement, the plan's account balance falls by
    the amount, and a payment confirmation number is issued to the customer.

    Args:
        billing_plan_id: Id class — the reference number of the installment payment plan that receives the payment,
            read from the plan record returned by the plan lookup.
        installment_number: Fixed-format class — the number of the first installment not yet invoiced on the plan,
            toward which the payment is recorded, an integer >= 0 (installments are counted from 1 for the plan's
            earliest installment), no padding.
        payment_method: Enum class — how the customer pays, exactly one of:
            debit_card — the customer pays with a debit card they hold and state;
            credit_card — the customer pays with a credit card they hold and state;
            bank_ach — the customer pays from a checking or savings account they hold, by routing and account number;
            personal_check — a paper check the customer has mailed or handed in, never one taken over the phone;
            money_order — a money order the customer has mailed or handed in, never one taken over the phone;
            cashiers_check — a cashier's check the customer has mailed or handed in, never one taken over the phone;
            cash — cash handed in at an agent office, never one taken over the phone.
        amount: Fixed-format class — the amount the customer authorizes, in USD with 2 decimal places, already
            rounded to the cent.

    Returns:
        A confirmation sentence (string) stating the payment confirmation number (PMT- followed by ten digits), the
        payment reference number, the amount (USD, two decimals), the method, the posting date (YYYY-MM-DD) and the
        plan's account balance after the payment (USD, two decimals). The confirmation number indicates the payment
        was accepted and posted.
    """
    plan = _Ledger.plan_row(ctx, billing_plan_id)
    today = ctx.now()[:10]
    pid = ctx.make_id("btx_", billing_plan_id, installment_number, payment_method, amount, "switch_down_payment")
    conf = _Ledger.confirmation(pid)
    ctx.create("billing_transactions", pid, billing_txn_id=pid, billing_plan_id=billing_plan_id,
               customer_id=plan.get("customer_id", ""), event_type="billing_payment_received", posted_date=today,
               amount=round(float(amount), 2), installment_number=int(installment_number), related_invoice_id=None,
               source_auto_txn_id=None, payment_method=payment_method, payment_channel="agent_phone",
               confirmation_number=conf)
    balance = round(float(plan.get("account_balance") or 0) - round(float(amount), 2), 2)
    if plan:
        ctx.update("billing_plans", billing_plan_id, account_balance=balance)
    return (f"Payment {conf} accepted: {round(float(amount), 2):.2f} by {payment_method} posted {today} as payment "
            f"{pid} toward installment {int(installment_number)}; plan balance now {balance:.2f}.")


@tool(owner="agent", rw="write")
def switch_to_direct_bill_b1ddc0c4(ctx: ToolContext, billing_plan_id: str, account_last4: str, installment_number: int,
                                   due_date: str, premium_amount: float, fee_amount: float, past_due_amount: float,
                                   minimum_due: float) -> str:
    """Move an installment payment plan that bills by automatic draft to the Cardinal Point Six-Pay Direct Bill Plan
    today, record the customer's revocation of the plan's recurring payment authorization, and issue the plan's first
    invoice after the move, dated today, charging that invoice's fee to the plan. On success the plan bills as the
    Six-Pay Direct Bill Plan with no recurring payment method on file and one more plan switch counted; a revocation of
    the recurring authorization for the stated account or card stands on the plan, dated today, for the method the
    plan had on file; a new installment invoice stands for the stated installment with the stated due date, premium,
    fee, carried amount and minimum due; a matching installment fee charge is posted today; and the plan's account
    balance rises by the fee. The customer sees the new plan and the invoice on the account.

    Args:
        billing_plan_id: Id class — the reference number of the installment payment plan being moved, read from the
            plan record returned by the plan lookup.
        account_last4: Fixed-format class — the last four digits of the bank account or card whose recurring
            authorization is revoked, exactly 4 digits as recorded on the plan's authorization.
        installment_number: Fixed-format class — the number of the installment the first invoice bills, an integer >= 0
            (installments are counted from 1 for the plan's earliest installment), no padding.
        due_date: Fixed-format class — the date the invoiced amount is due, written YYYY-MM-DD as a calendar date
            with no time and no time zone.
        premium_amount: Fixed-format class — the premium portion the invoice bills, in USD with 2 decimal places,
            already rounded to the cent.
        fee_amount: Fixed-format class — the fee the invoice bills and the fee charge posted with it, in USD with 2
            decimal places, already rounded to the cent.
        past_due_amount: Fixed-format class — the amount carried onto the invoice from the plan's earlier billing, in
            USD with 2 decimal places, already rounded to the cent; a credit held on the plan is written as a negative
            amount and nothing carried as 0.00.
        minimum_due: Fixed-format class — the amount due by the due date, in USD with 2 decimal places, already rounded
            to the cent.

    Returns:
        A confirmation sentence (string) stating the new plan name, the revocation reference number, the new invoice
        reference number, the installment fee charge reference number, the installment number, the due date
        (YYYY-MM-DD), the premium, fee, carried amount and minimum due (USD, two decimals) and the plan's account
        balance after the fee (USD, two decimals). The presence of the three reference numbers indicates the plan was
        moved, the authorization revoked and the invoice issued.
    """
    plan = _Ledger.plan_row(ctx, billing_plan_id)
    today = ctx.now()[:10]
    method = plan.get("payment_method_on_file") or "bank_ach"
    rev = ctx.make_id("bauth_", billing_plan_id, account_last4, "revoked")
    ctx.create("billing_authorizations", rev, billing_authorization_id=rev, billing_plan_id=billing_plan_id,
               customer_id=plan.get("customer_id", ""), event_type="billing_recurring_payment_revoked",
               authorization_date=today, recurring_method=method, account_last4=str(account_last4))
    inv = ctx.make_id("binv_", billing_plan_id, installment_number, due_date, premium_amount, fee_amount,
                      past_due_amount, minimum_due, "direct_bill")
    ctx.create("billing_invoices", inv, billing_invoice_id=inv, billing_plan_id=billing_plan_id,
               customer_id=plan.get("customer_id", ""), event_type="billing_installment_billed",
               invoice_date=today, due_date=due_date, installment_number=int(installment_number),
               premium_amount=round(float(premium_amount), 2), fee_amount=round(float(fee_amount), 2),
               past_due_amount=round(float(past_due_amount), 2), minimum_due=round(float(minimum_due), 2))
    fee = ctx.make_id("btx_", inv, "installment_fee", fee_amount)
    ctx.create("billing_transactions", fee, billing_txn_id=fee, billing_plan_id=billing_plan_id,
               customer_id=plan.get("customer_id", ""), event_type="billing_installment_fee", posted_date=today,
               amount=round(float(fee_amount), 2), installment_number=int(installment_number),
               related_invoice_id=inv)
    balance = round(float(plan.get("account_balance") or 0) + round(float(fee_amount), 2), 2)
    used = int(plan.get("plan_switches_used") or 0) + 1
    if plan:
        ctx.update("billing_plans", billing_plan_id, variant_name="Cardinal Point Six-Pay Direct Bill Plan",
                   payment_method_on_file="none", plan_switches_used=used, account_balance=balance)
    return (f"Plan moved to Cardinal Point Six-Pay Direct Bill Plan; authorization revocation {rev} recorded. "
            f"Installment invoice {inv} issued for installment {int(installment_number)}, due {due_date}: premium "
            f"{round(float(premium_amount), 2):.2f}, fee {round(float(fee_amount), 2):.2f}, carried "
            f"{round(float(past_due_amount), 2):.2f}, minimum due {round(float(minimum_due), 2):.2f}. Installment fee "
            f"charge {fee} posted; plan balance now {balance:.2f}.")

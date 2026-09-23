"""Hidden task tools for the employee meal account desk (category: meal).

Every tool here performs exactly one atomic write on an employee's workplace meal account or
on that account's transaction ledger. None of them aggregates history, judges eligibility or
checks whether anything else has been settled first: the agent reads the account, the ledger
and the published rules, works the figure out, and passes it in.
"""

from erlbench import ToolContext, tool


@tool(owner="agent", rw="write")
def post_payroll_recovery_c9e76aa9(ctx: ToolContext, meal_account_id: str,
                                   recovered_amount_usd: float, pay_period: str) -> str:
    """Remit one payroll period's recovery against an employee meal account. The call books a
    recovery entry on the account's transaction ledger for the amount stated, marks it with the
    payroll period it is remitted for and the day it was remitted, and takes the charges awaiting
    payroll recovery down on the account by the same amount, so the employee sees a smaller
    outstanding figure and a new line on their statement immediately. The call has completed when
    the confirmation names the recovery entry it booked and the outstanding figure left standing.

    Args:
        meal_account_id: Id class — the reference number of the employee meal account the recovery
            is remitted against; read it from the meal account lookup before this call.
        recovered_amount_usd: Fixed-format class — the value recovered from the employee's pay in
            this remittance, in USD, recorded to 2 decimal places and rounded half to even at that
            precision; it is stored as a positive magnitude and an empty value is not accepted.
        pay_period: Fixed-format class — the payroll period this remittance is made for, written as
            YYYY-MM-P followed by one digit for the half of the month, exactly as it is printed on
            the charges being recovered; an empty value is not accepted.

    Returns:
        A plain confirmation sentence naming the reference of the recovery entry booked, the value
        recovered in USD to two decimal places, the payroll period it was booked against and the
        charges awaiting payroll recovery still standing on the account after it. The presence of
        that entry reference is what indicates the remittance completed.
    """
    rid = ctx.make_id("mtx_rec_", meal_account_id, recovered_amount_usd, pay_period)
    amount = round(float(recovered_amount_usd), 2)
    rows = ctx.find("meal_accounts", meal_account_id=meal_account_id)
    owner = rows[0].get("customer_id") if rows else ""
    standing = round(float(rows[0].get("payroll_arrears_usd") or 0.0), 2) if rows else 0.0
    left = round(standing - amount, 2)
    ctx.create("meal_transactions", rid,
               meal_transaction_id=rid,
               meal_account_id=meal_account_id,
               customer_id=owner,
               event_type="meal_payroll_deduction_posted",
               transaction_code="payroll_deduction",
               amount_usd=amount,
               posted_date=ctx.now()[:10],
               meal_period="not_applicable",
               venue_code="",
               pos_reference=f"POS-{int(rid[-8:], 16) % 100000000:08d}",
               original_pos_reference="",
               payment_channel="payroll_deduction",
               pay_period=pay_period,
               subsidy_lot_reference="",
               item_count="")
    if rows:
        ctx.update("meal_accounts", meal_account_id, payroll_arrears_usd=left)
    return (f"Recovery {rid} booked for {amount:.2f} USD against payroll period {pay_period}; "
            f"charges awaiting payroll recovery now stand at {left:.2f} USD.")


@tool(owner="user", rw="write")
def load_arrears_paydown_ff1c695b(ctx: ToolContext, meal_account_id: str,
                                  paydown_amount_usd: float) -> str:
    """Put money onto your own workplace meal account from the card you hold, so the value stands
    to your credit against what you owe. The call books a load entry on the account's transaction
    ledger for the amount you give and raises the spendable stored value on the account by the same
    amount, which you can see at the till straight away. It is your own payment: nobody else may
    make it for you. The call has completed when the confirmation names the load entry it booked
    and the new spendable value.

    Args:
        meal_account_id: Id class — the reference number of your workplace meal account, as the
            dining services desk reads it out to you before you make the payment.
        paydown_amount_usd: Fixed-format class — the value you are putting onto the account in this
            payment, in USD, recorded to 2 decimal places and rounded half to even at that
            precision; it is stored as a positive magnitude and an empty value is not accepted.

    Returns:
        A plain confirmation sentence naming the reference of the load entry booked, the value paid
        in USD to two decimal places and the spendable stored value standing on the account
        afterwards. The presence of that entry reference is what indicates the payment completed.
    """
    rid = ctx.make_id("mtx_lod_", meal_account_id, paydown_amount_usd)
    amount = round(float(paydown_amount_usd), 2)
    rows = ctx.find("meal_accounts", meal_account_id=meal_account_id)
    owner = rows[0].get("customer_id") if rows else ""
    balance = round(float(rows[0].get("meal_balance_usd") or 0.0), 2) if rows else 0.0
    new_balance = round(balance + amount, 2)
    ctx.create("meal_transactions", rid,
               meal_transaction_id=rid,
               meal_account_id=meal_account_id,
               customer_id=owner,
               event_type="meal_account_load_posted",
               transaction_code="account_load",
               amount_usd=amount,
               posted_date=ctx.now()[:10],
               meal_period="not_applicable",
               venue_code="",
               pos_reference=f"POS-{int(rid[-8:], 16) % 100000000:08d}",
               original_pos_reference="",
               payment_channel="credit_card",
               pay_period="",
               subsidy_lot_reference="",
               item_count="")
    if rows:
        ctx.update("meal_accounts", meal_account_id, meal_balance_usd=new_balance)
    return (f"Load {rid} booked for {amount:.2f} USD from your card; spendable stored value on the "
            f"account now stands at {new_balance:.2f} USD.")


@tool(owner="agent", rw="write")
def lift_meal_account_restriction_a306574a(ctx: ToolContext, meal_account_id: str,
                                           arrears_carried_usd: float) -> str:
    """Take a spending restriction off an employee meal account and restate what the account still
    owes. The call moves the account back into the active state, clears the day the restriction
    began, sets the charges awaiting payroll recovery to the figure stated, and books a settlement
    entry on the account's transaction ledger for the movement that restatement makes. Payroll
    tender works again at the till from that moment and the employee sees the restated figure on
    the account. The call has completed when the confirmation names the account, the state it now
    stands in and the restated figure.

    Args:
        meal_account_id: Id class — the reference number of the employee meal account whose
            restriction is being taken off; read it from the meal account lookup before this call.
        arrears_carried_usd: Fixed-format class — the charges awaiting payroll recovery the account
            carries forward once the restriction is off, in USD, recorded to 2 decimal places and
            rounded half to even at that precision; it is stored as a positive magnitude and an
            empty value is not accepted.

    Returns:
        A plain confirmation sentence naming the meal account reference, the state the account now
        stands in, the charges awaiting payroll recovery carried forward in USD to two decimal
        places, and the reference of the settlement entry booked for the movement. The named active
        state is what indicates the restriction has been taken off.
    """
    carried = round(float(arrears_carried_usd), 2)
    rid = ctx.make_id("mtx_stl_", meal_account_id, arrears_carried_usd)
    rows = ctx.find("meal_accounts", meal_account_id=meal_account_id)
    owner = rows[0].get("customer_id") if rows else ""
    standing = round(float(rows[0].get("payroll_arrears_usd") or 0.0), 2) if rows else 0.0
    ctx.create("meal_transactions", rid,
               meal_transaction_id=rid,
               meal_account_id=meal_account_id,
               customer_id=owner,
               event_type="meal_payroll_deduction_posted",
               transaction_code="balance_adjustment",
               amount_usd=round(abs(standing - carried), 2),
               posted_date=ctx.now()[:10],
               meal_period="not_applicable",
               venue_code="",
               pos_reference=f"POS-{int(rid[-8:], 16) % 100000000:08d}",
               original_pos_reference="",
               payment_channel="payroll_deduction",
               pay_period="",
               subsidy_lot_reference="",
               item_count="")
    if rows:
        ctx.update("meal_accounts", meal_account_id,
                   status="active", restriction_start_date="",
                   payroll_arrears_usd=carried)
    return (f"Meal account {meal_account_id} now stands active with no restriction; charges "
            f"awaiting payroll recovery carried forward are {carried:.2f} USD, settlement entry "
            f"{rid}.")


@tool(owner="agent", rw="write")
def grant_daily_allowance_lot_ed948b99(ctx: ToolContext, meal_account_id: str,
                                       granted_amount_usd: float) -> str:
    """Place an employer meal allowance lot on an employee meal account. The call books an allowance
    grant entry on the account's transaction ledger for the value stated, mints the allowance lot
    reference that entry is traced under, and raises the unspent employer allowance standing on the
    account by the same value, so the employee can spend it at the counter straight away. The call
    has completed when the confirmation names the lot reference it minted and the unspent allowance
    now standing.

    Args:
        meal_account_id: Id class — the reference number of the employee meal account the allowance
            lot is placed on; read it from the meal account lookup before this call.
        granted_amount_usd: Fixed-format class — the employer allowance placed on the account in this
            lot, in USD, recorded to 2 decimal places and rounded half to even at that precision; it
            is stored as a positive magnitude and an empty value is not accepted.

    Returns:
        A plain confirmation sentence naming the allowance lot reference minted for this grant, the
        value granted in USD to two decimal places and the unspent employer allowance standing on the
        account afterwards. The presence of that lot reference is what indicates the grant completed.
    """
    rid = ctx.make_id("mtx_grt_", meal_account_id, granted_amount_usd)
    amount = round(float(granted_amount_usd), 2)
    rows = ctx.find("meal_accounts", meal_account_id=meal_account_id)
    owner = rows[0].get("customer_id") if rows else ""
    standing = round(float(rows[0].get("subsidy_allowance_usd") or 0.0), 2) if rows else 0.0
    lot = f"SL-{int(rid[-6:], 16) % 1000000:06d}"
    ctx.create("meal_transactions", rid,
               meal_transaction_id=rid,
               meal_account_id=meal_account_id,
               customer_id=owner,
               event_type="meal_subsidy_granted",
               transaction_code="subsidy_grant",
               amount_usd=amount,
               posted_date=ctx.now()[:10],
               meal_period="not_applicable",
               venue_code="",
               pos_reference=f"POS-{int(rid[-8:], 16) % 100000000:08d}",
               original_pos_reference="",
               payment_channel="subsidy",
               pay_period="",
               subsidy_lot_reference=lot,
               item_count="")
    if rows:
        ctx.update("meal_accounts", meal_account_id,
                   subsidy_allowance_usd=round(standing + amount, 2))
    return (f"Allowance lot {lot} granted for {amount:.2f} USD; unspent employer allowance on the "
            f"account now stands at {round(standing + amount, 2):.2f} USD.")


@tool(owner="agent", rw="write")
def apply_allowance_to_ticket_3fbfdeca(ctx: ToolContext, meal_account_id: str,
                                       applied_amount_usd: float,
                                       original_pos_reference: str) -> str:
    """Spend employer meal allowance against one till transaction already rung on an employee meal
    account. The call books an allowance application entry on the account's transaction ledger for
    the value stated, marks it with the till transaction it meets, and takes the unspent employer
    allowance standing on the account down by the same value, so the employee sees that meal part
    met by the employer rather than by them. The call has completed when the confirmation names the
    application entry it booked, the till transaction it was applied to and the allowance left.

    Args:
        meal_account_id: Id class — the reference number of the employee meal account whose allowance
            is being spent; read it from the meal account lookup before this call.
        applied_amount_usd: Fixed-format class — the employer allowance spent against that till
            transaction, in USD, recorded to 2 decimal places and rounded half to even at that
            precision; it is stored as a positive magnitude and an empty value is not accepted.
        original_pos_reference: Fixed-format class — the till transaction the allowance is applied
            to, written as POS- followed by 8 digits exactly as it is printed on that transaction in
            the account's activity; an empty value is not accepted.

    Returns:
        A plain confirmation sentence naming the reference of the allowance application booked, the
        value applied in USD to two decimal places, the till transaction it was applied to and the
        unspent employer allowance left standing. The presence of that application reference is what
        indicates the allowance was spent.
    """
    rid = ctx.make_id("mtx_app_", meal_account_id, applied_amount_usd, original_pos_reference)
    amount = round(float(applied_amount_usd), 2)
    rows = ctx.find("meal_accounts", meal_account_id=meal_account_id)
    owner = rows[0].get("customer_id") if rows else ""
    standing = round(float(rows[0].get("subsidy_allowance_usd") or 0.0), 2) if rows else 0.0
    ctx.create("meal_transactions", rid,
               meal_transaction_id=rid,
               meal_account_id=meal_account_id,
               customer_id=owner,
               event_type="meal_subsidy_applied",
               transaction_code="subsidy_application",
               amount_usd=amount,
               posted_date=ctx.now()[:10],
               meal_period="lunch",
               venue_code="",
               pos_reference=f"POS-{int(rid[-8:], 16) % 100000000:08d}",
               original_pos_reference=original_pos_reference,
               payment_channel="subsidy",
               pay_period="",
               subsidy_lot_reference="",
               item_count="")
    if rows:
        ctx.update("meal_accounts", meal_account_id,
                   subsidy_allowance_usd=round(standing - amount, 2))
    return (f"Allowance application {rid} booked for {amount:.2f} USD against till transaction "
            f"{original_pos_reference}; unspent employer allowance left is "
            f"{round(standing - amount, 2):.2f} USD.")


@tool(owner="user", rw="write")
def confirm_payroll_charge_accrual_6d54e4b8(ctx: ToolContext, meal_account_id: str,
                                            accrued_amount_usd: float, pay_period: str) -> str:
    """Give your own consent for the meals you have charged at the counter to be carried to your pay.
    The call books a charge entry on your meal account's transaction ledger for the value stated,
    marks it with the payroll period your pay office will recover it in, and raises the charges
    awaiting payroll recovery on the account by the same value, so the amount shows on your account
    and reaches that pay packet. It is your own consent: nobody else may give it for you. The call
    has completed when the confirmation names the charge entry it booked and the charges now
    awaiting recovery.

    Args:
        meal_account_id: Id class — the reference number of your workplace meal account, as the
            dining services desk reads it out to you before you give your consent.
        accrued_amount_usd: Fixed-format class — the value you are consenting to have carried to your
            pay, in USD, recorded to 2 decimal places and rounded half to even at that precision; it
            is stored as a positive magnitude and an empty value is not accepted.
        pay_period: Fixed-format class — the payroll period the charge is to be recovered in, written
            as YYYY-MM-P followed by one digit for the half of the month, exactly as the desk reads
            it out from your account's activity; an empty value is not accepted.

    Returns:
        A plain confirmation sentence naming the reference of the charge entry booked, the value
        consented to in USD to two decimal places, the payroll period it will be recovered in and the
        charges awaiting payroll recovery standing on the account afterwards. The presence of that
        entry reference is what indicates your consent was recorded.
    """
    rid = ctx.make_id("mtx_acr_", meal_account_id, accrued_amount_usd, pay_period)
    amount = round(float(accrued_amount_usd), 2)
    rows = ctx.find("meal_accounts", meal_account_id=meal_account_id)
    owner = rows[0].get("customer_id") if rows else ""
    standing = round(float(rows[0].get("payroll_arrears_usd") or 0.0), 2) if rows else 0.0
    ctx.create("meal_transactions", rid,
               meal_transaction_id=rid,
               meal_account_id=meal_account_id,
               customer_id=owner,
               event_type="meal_charge_accrued",
               transaction_code="charge_accrual",
               amount_usd=amount,
               posted_date=ctx.now()[:10],
               meal_period="not_applicable",
               venue_code="",
               pos_reference=f"POS-{int(rid[-8:], 16) % 100000000:08d}",
               original_pos_reference="",
               payment_channel="payroll_deduction",
               pay_period=pay_period,
               subsidy_lot_reference="",
               item_count="")
    if rows:
        ctx.update("meal_accounts", meal_account_id,
                   payroll_arrears_usd=round(standing + amount, 2))
    return (f"Charge {rid} booked for {amount:.2f} USD against payroll period {pay_period}; charges "
            f"awaiting payroll recovery now stand at {round(standing + amount, 2):.2f} USD.")

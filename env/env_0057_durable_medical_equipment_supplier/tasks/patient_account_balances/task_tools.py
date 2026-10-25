"""Hidden task tools of the patient_account_balances difficulty (Summit Ridge Home Medical).

Each tool performs one atomic change on a patient's coverage account and is reached only through
the unlock/call meta-tools. No tool judges eligibility, ordering or amounts: the value passed in is
the value booked.
"""

from erlbench import ToolContext, tool


@tool(owner="agent", rw="write")
def apply_hardship_discount_c60f16b6(ctx: ToolContext, coverage_id: str, applied_to_entry_id: str,
                                     amount: float) -> str:
    """Book a financial-hardship discount against one patient charge on a coverage account.

    The patient-services agent uses this to reduce one open patient charge by the hardship discount
    the patient's approved financial-assistance tier earns. One call writes one hardship-discount
    adjustment entry dated today that points at the charge, and lowers the account's patient
    balance by the same amount; the patient sees the discount as a credit line under that charge on
    the account history. The receipt confirms the adjustment reference,
    the charge it reduces, the amount booked and the account balance that results.

    Args:
        coverage_id: Id class — the reference number of the coverage account (the insurance coverage
            record on the patient's file) that carries the charge, as returned by the coverage lookup.
        applied_to_entry_id: Id class — the reference number of the patient charge entry being
            discounted, as returned by the patient-account ledger lookup for that account.
        amount: Fixed-format class — the hardship discount to book on the charge, in USD, a positive
            figure with 2 decimal places (cents); it is stored exactly as given, rounded half up to
            the cent.

    Returns:
        A text rendering of a dictionary with these fields: adjustment_id (string, the reference of
        the new hardship-discount entry), coverage_id (string, the account adjusted),
        applied_to_entry_id (string, the charge reduced), amount (number in USD with 2 decimals, the
        discount booked), posting_date (string YYYY-MM-DD, today's date), patient_balance (number in
        USD with 2 decimals, the account balance once the discount is booked) and status (the string
        "booked"). A receipt whose status is "booked" means the discount is on the account.
    """
    holding = ctx.find("coverage_holdings", coverage_id=coverage_id)[0]
    rid = ctx.make_id("led_", coverage_id, applied_to_entry_id, "hardship_discount", amount)
    ctx.create("coverage_ledger", rid, ledger_entry_id=rid, coverage_id=coverage_id,
               customer_id=holding["customer_id"], event_type="coverage_adjustment",
               posting_date=ctx.now()[:10], amount=round(float(amount), 2), line_allowed_amount=0.0,
               source_category="none", source_bill_id="", responsibility_type="none",
               applied_to_entry_id=applied_to_entry_id, payer_coverage_id="", payment_method="none",
               payment_reference="", adjustment_reason="hardship_discount", benefit_year="",
               eligibility_result="none", statement_cycle=0, balance_due=0.0)
    new_balance = round(float(holding["patient_balance"]) - round(float(amount), 2), 2)
    ctx.update("coverage_holdings", coverage_id, patient_balance=new_balance)
    return str({"adjustment_id": rid, "coverage_id": coverage_id, "applied_to_entry_id": applied_to_entry_id,
                "amount": round(float(amount), 2), "posting_date": ctx.now()[:10],
                "patient_balance": new_balance, "status": "booked"})


@tool(owner="agent", rw="write")
def apply_prompt_pay_discount_12f1a0eb(ctx: ToolContext, coverage_id: str, applied_to_entry_id: str,
                                       amount: float) -> str:
    """Book a prompt-pay discount against one patient charge that the patient paid in full.

    The patient-services agent uses this to credit the prompt-pay discount Summit Ridge grants on a
    charge the patient settled quickly. One call writes one prompt-pay-discount adjustment entry
    dated today that points at the charge, and lowers the account's patient balance by the same
    amount; the patient sees the discount as a credit line under that charge on the account
    history. The receipt confirms the adjustment reference, the charge it
    credits, the amount booked and the account balance that results.

    Args:
        coverage_id: Id class — the reference number of the coverage account (the insurance coverage
            record on the patient's file) that carries the charge, as returned by the coverage lookup.
        applied_to_entry_id: Id class — the reference number of the patient charge entry the discount
            belongs to, as returned by the patient-account ledger lookup for that account.
        amount: Fixed-format class — the prompt-pay discount to book on the charge, in USD, a positive
            figure with 2 decimal places (cents); it is stored exactly as given, rounded half up to
            the cent.

    Returns:
        A text rendering of a dictionary with these fields: adjustment_id (string, the reference of
        the new prompt-pay-discount entry), coverage_id (string, the account adjusted),
        applied_to_entry_id (string, the charge credited), amount (number in USD with 2 decimals, the
        discount booked), posting_date (string YYYY-MM-DD, today's date), patient_balance (number in
        USD with 2 decimals, the account balance once the discount is booked) and status (the string
        "booked"). A receipt whose status is "booked" means the discount is on the account.
    """
    holding = ctx.find("coverage_holdings", coverage_id=coverage_id)[0]
    rid = ctx.make_id("led_", coverage_id, applied_to_entry_id, "prompt_pay_discount", amount)
    ctx.create("coverage_ledger", rid, ledger_entry_id=rid, coverage_id=coverage_id,
               customer_id=holding["customer_id"], event_type="coverage_adjustment",
               posting_date=ctx.now()[:10], amount=round(float(amount), 2), line_allowed_amount=0.0,
               source_category="none", source_bill_id="", responsibility_type="none",
               applied_to_entry_id=applied_to_entry_id, payer_coverage_id="", payment_method="none",
               payment_reference="", adjustment_reason="prompt_pay_discount", benefit_year="",
               eligibility_result="none", statement_cycle=0, balance_due=0.0)
    new_balance = round(float(holding["patient_balance"]) - round(float(amount), 2), 2)
    ctx.update("coverage_holdings", coverage_id, patient_balance=new_balance)
    return str({"adjustment_id": rid, "coverage_id": coverage_id, "applied_to_entry_id": applied_to_entry_id,
                "amount": round(float(amount), 2), "posting_date": ctx.now()[:10],
                "patient_balance": new_balance, "status": "booked"})


@tool(owner="user", rw="write")
def pay_arrangement_deposit_e794f585(ctx: ToolContext, coverage_id: str, applied_to_entry_id: str,
                                     payment_method: str, amount: float) -> str:
    """Pay, in person, the deposit that opens a monthly payment arrangement on a coverage account.

    The patient (or the person paying for them) uses this to pay the arrangement deposit on the spot
    with their own card or bank account. One call takes the payment, writes one patient-payment entry
    dated today against the named open charge with the confirmation code the payment network issues,
    and lowers the account's patient balance by the amount paid. The patient sees the payment on the
    account history straight away. The receipt carries the confirmation code to keep for their
    records, the charge the money settles, the amount and method, and the resulting balance.

    Args:
        coverage_id: Id class — the reference number of the coverage account (the insurance coverage
            record on the patient's file) the deposit is paid on, as given to the patient by the agent
            from the coverage lookup.
        applied_to_entry_id: Id class — the reference number of the open patient charge the deposit is
            applied to, as given to the patient by the agent from the patient-account ledger lookup.
        payment_method: Enum class — how the patient pays, exactly one of: card (a credit or debit card
            the patient holds, keyed in now); ach (a bank-account transfer authorised now from the
            patient's checking or savings account); check (a paper check the patient has handed over at
            a Summit Ridge branch counter today); hsa_fsa_card (a health savings or flexible spending
            account card); none (no money moves at all, which never applies to a deposit actually paid).
        amount: Fixed-format class — the deposit paid, in USD, a positive figure with 2 decimal places
            (cents); it is stored exactly as given, rounded half up to the cent.

    Returns:
        A text rendering of a dictionary with these fields: payment_entry_id (string, the reference of
        the new payment entry), confirmation_code (string, the code the payment network issued for this
        payment), coverage_id (string, the account paid on), applied_to_entry_id (string, the charge
        the money settles), payment_method (string, the method used), amount (number in USD with 2
        decimals, the deposit paid), posting_date (string YYYY-MM-DD, today's date), patient_balance
        (number in USD with 2 decimals, the account balance once the deposit is posted) and status
        (the string "paid"). A receipt whose status is "paid" means the deposit is on the account.
    """
    holding = ctx.find("coverage_holdings", coverage_id=coverage_id)[0]
    rid = ctx.make_id("led_", coverage_id, applied_to_entry_id, payment_method, amount, "deposit")
    code = ctx.make_id("SRP", coverage_id, applied_to_entry_id, payment_method, amount, length=10).upper()
    ctx.create("coverage_ledger", rid, ledger_entry_id=rid, coverage_id=coverage_id,
               customer_id=holding["customer_id"], event_type="coverage_payment",
               posting_date=ctx.now()[:10], amount=round(float(amount), 2), line_allowed_amount=0.0,
               source_category="none", source_bill_id="", responsibility_type="none",
               applied_to_entry_id=applied_to_entry_id, payer_coverage_id="", payment_method=payment_method,
               payment_reference=code, adjustment_reason="none", benefit_year="",
               eligibility_result="none", statement_cycle=0, balance_due=0.0)
    new_balance = round(float(holding["patient_balance"]) - round(float(amount), 2), 2)
    ctx.update("coverage_holdings", coverage_id, patient_balance=new_balance)
    return str({"payment_entry_id": rid, "confirmation_code": code, "coverage_id": coverage_id,
                "applied_to_entry_id": applied_to_entry_id, "payment_method": payment_method,
                "amount": round(float(amount), 2), "posting_date": ctx.now()[:10],
                "patient_balance": new_balance, "status": "paid"})


@tool(owner="user", rw="write")
def set_payment_arrangement_62cec67a(ctx: ToolContext, coverage_id: str, monthly_amount: float,
                                     start_date: str) -> str:
    """Put a new monthly payment arrangement in force on a coverage account, as the patient's own act.

    The patient uses this to start the monthly arrangement they have agreed to. One call marks the
    account's payment arrangement as active and records the agreed monthly installment and the date
    the installments begin falling due; the account's arrangement fields then carry that
    installment and due date. The receipt confirms the account, the arrangement status, the
    installment and the opening due date.

    Args:
        coverage_id: Id class — the reference number of the coverage account (the insurance coverage
            record on the patient's file) the arrangement is set on, as given to the patient by the
            agent from the coverage lookup.
        monthly_amount: Fixed-format class — the agreed monthly installment, in USD, a positive figure
            with 2 decimal places (cents); it is stored exactly as given, rounded half up to the cent.
        start_date: Fixed-format class — the calendar date the installments begin falling due, written
            YYYY-MM-DD (local calendar date, no time part); installments then fall due on the same day
            of each later month.

    Returns:
        A text rendering of a dictionary with these fields: coverage_id (string, the account the
        arrangement is set on), payment_plan_status (the string "active"), monthly_amount (number in
        USD with 2 decimals, the installment recorded), start_date (string YYYY-MM-DD, the opening due
        date recorded) and status (the string "arrangement_active"). A receipt whose status is
        "arrangement_active" means the arrangement is in force.
    """
    ctx.update("coverage_holdings", coverage_id, payment_plan_status="active",
               payment_plan_monthly_amount=round(float(monthly_amount), 2), payment_plan_start_date=start_date)
    return str({"coverage_id": coverage_id, "payment_plan_status": "active",
                "monthly_amount": round(float(monthly_amount), 2), "start_date": start_date,
                "status": "arrangement_active"})


@tool(owner="agent", rw="write")
def post_crossover_payment_b661a2ed(ctx: ToolContext, coverage_id: str, applied_to_entry_id: str,
                                    payer_coverage_id: str, amount: float) -> str:
    """Post a secondary payer's crossover payment against one patient charge on the primary coverage account.

    The patient-services agent uses this to record the amount a secondary coverage (such as a Medicaid
    record behind Medicare) pays on the patient's share of a claim line the primary payer adjudicated.
    One call writes one secondary-payment entry dated today on the primary account, naming the charge it
    settles and the secondary coverage that paid, carrying the claim line's allowed amount and origin from
    that charge, and lowers the primary account's patient balance by the amount. The patient sees the
    secondary payment under that charge on the account history. The receipt confirms the entry, the
    charge, the paying coverage, the amount and the resulting balance.

    Args:
        coverage_id: Id class — the reference number of the primary coverage account that carries the
            charge, as returned by the coverage lookup.
        applied_to_entry_id: Id class — the reference number of the patient charge entry the secondary
            payment settles, as returned by the patient-account ledger lookup for the primary account.
        payer_coverage_id: Id class — the reference number of the secondary coverage record that paid, as
            returned by the coverage lookup.
        amount: Fixed-format class — the secondary payment applied to the charge, in USD, a figure of zero
            or more with 2 decimal places (cents); it is stored exactly as given, rounded half up to the cent.

    Returns:
        A text rendering of a dictionary with these fields: secondary_payment_id (string, the reference of
        the new entry), coverage_id (string, the primary account), applied_to_entry_id (string, the charge
        settled), payer_coverage_id (string, the secondary coverage that paid), amount (number in USD with 2
        decimals), posting_date (string YYYY-MM-DD, today's date), patient_balance (number in USD with 2
        decimals, the primary account balance once the payment is posted) and status (the string
        "posted"). A receipt whose status is "posted" means the payment is on the account.
    """
    holding = ctx.find("coverage_holdings", coverage_id=coverage_id)[0]
    charge = ctx.find("coverage_ledger", ledger_entry_id=applied_to_entry_id)[0]
    rid = ctx.make_id("led_", coverage_id, applied_to_entry_id, payer_coverage_id, amount)
    ctx.create("coverage_ledger", rid, ledger_entry_id=rid, coverage_id=coverage_id,
               customer_id=holding["customer_id"], event_type="coverage_secondary_payment",
               posting_date=ctx.now()[:10], amount=round(float(amount), 2),
               line_allowed_amount=charge["line_allowed_amount"], source_category=charge["source_category"],
               source_bill_id=charge["source_bill_id"], responsibility_type="none",
               applied_to_entry_id=applied_to_entry_id, payer_coverage_id=payer_coverage_id, payment_method="none",
               payment_reference="", adjustment_reason="none", benefit_year="", eligibility_result="none",
               statement_cycle=0, balance_due=0.0)
    new_balance = round(float(holding["patient_balance"]) - round(float(amount), 2), 2)
    ctx.update("coverage_holdings", coverage_id, patient_balance=new_balance)
    return str({"secondary_payment_id": rid, "coverage_id": coverage_id, "applied_to_entry_id": applied_to_entry_id,
                "payer_coverage_id": payer_coverage_id, "amount": round(float(amount), 2),
                "posting_date": ctx.now()[:10], "patient_balance": new_balance, "status": "posted"})


@tool(owner="user", rw="write")
def revise_payment_arrangement_5f5b46f9(ctx: ToolContext, coverage_id: str, monthly_amount: float) -> str:
    """Change the monthly installment of the payment arrangement already in force on a coverage account,
    as the patient's own act.

    The patient uses this to accept a re-figured installment on their existing monthly arrangement. One
    call records the new monthly installment on the account's arrangement and changes nothing else: the
    arrangement keeps its status and its original due day of the month, and the account's arrangement
    fields carry the new installment. The receipt confirms the account, the arrangement status as it stands and
    the new installment.

    Args:
        coverage_id: Id class — the reference number of the coverage account whose arrangement is changed,
            as given to the patient by the agent from the coverage lookup.
        monthly_amount: Fixed-format class — the new monthly installment, in USD, a positive figure with 2
            decimal places (cents); it is stored exactly as given, rounded half up to the cent.

    Returns:
        A text rendering of a dictionary with these fields: coverage_id (string, the account changed),
        payment_plan_status (string, the arrangement's status as recorded on the account, unchanged by this
        call), monthly_amount (number in USD with 2 decimals, the new
        installment recorded) and status (the string "arrangement_revised"). A receipt whose status is
        "arrangement_revised" means the new installment is in force.
    """
    holding = ctx.find("coverage_holdings", coverage_id=coverage_id)[0]
    ctx.update("coverage_holdings", coverage_id, payment_plan_monthly_amount=round(float(monthly_amount), 2))
    return str({"coverage_id": coverage_id, "payment_plan_status": holding["payment_plan_status"],
                "monthly_amount": round(float(monthly_amount), 2), "status": "arrangement_revised"})

"""Hidden task tools of the payment_plan_servicing difficulty (Patient Payment Plans).
Path: env/env_0025_multispecialty_physician_group/tasks/payment_plan_servicing/task_tools.py

Each tool performs one atomic write on the Patient Payment Plans line and nothing else: it neither checks
eligibility nor computes any amount for the caller. Every name is registered as an extended policy's
target_tool and is reached through unlock_* -> call_*.
"""

from erlbench import ToolContext, tool


@tool(owner="agent", rw="write")
def enroll_setup_fee_08ffaf93(ctx: ToolContext, payment_plan_id: str, amount: float) -> str:
    """Book the one-time signing setup fee of a payment plan into that plan's balance, as one fee entry of the
    plan's ledger.

    One call adds one plan ledger entry of kind "balance enrolled" with enrollment reason setup_fee, dated
    today and carrying no financial-account charge reference, and raises the plan's remaining balance by the
    amount given. On success the plan's ledger lists the setup-fee entry and the plan's remaining balance
    includes it; the returned reference identifies the new entry.

    Args:
        payment_plan_id: Id class — reference number of the payment plan whose balance is charged, as shown by
            the payment plan lookup for the patient.
        amount: Fixed-format class — the setup fee booked into the plan balance, in USD, 2 decimal places,
            positive; the value is stored exactly as given, rounded half up to 2 decimal places.

    Returns:
        A confirmation sentence (string) naming the new plan ledger entry reference (text beginning "ppt_"),
        the payment plan reference, the setup fee booked in USD with 2 decimal places, and the plan's remaining
        balance including the entry in USD with 2 decimal places; receiving this sentence means the entry is booked.
    """
    fee = round(float(amount), 2)
    rows = ctx.find("payment_plans", payment_plan_id=payment_plan_id)
    plan = rows[0] if rows else {}
    rid = ctx.make_id("ppt_", payment_plan_id, fee, "setup_fee")
    ctx.create("payplan_transactions", rid, payplan_txn_id=rid, payment_plan_id=payment_plan_id,
               customer_id=plan.get("customer_id"), event_type="payplan_balance_enrolled",
               txn_date=ctx.now()[:10], amount=fee, billing_txn_id=None, enroll_reason="setup_fee",
               installment_number=0, payment_method="none", channel="phone", autopay=False,
               extra_kind="none", adjustment_reason="none", release_reason="none")
    new_balance = round(float(plan.get("remaining_balance") or 0) + fee, 2)
    ctx.update("payment_plans", payment_plan_id, remaining_balance=new_balance)
    return (f"Setup fee entry {rid} booked on payment plan {payment_plan_id}: {fee:.2f} USD; "
            f"plan remaining balance now {new_balance:.2f} USD.")


@tool(owner="agent", rw="write")
def enroll_encounter_charge_372696d1(ctx: ToolContext, payment_plan_id: str, billing_txn_id: str,
                                     amount: float) -> str:
    """Enroll one financial-account charge on a payment plan that is still a proposal, as an initial enrollment
    of that charge.

    One call adds one plan ledger entry of kind "balance enrolled" with enrollment reason initial_enrollment,
    dated today and pointing at the charge, and raises the plan's remaining balance by the amount given. The
    charge itself on the financial account is not changed. On success a lookup of the plan ledger by the charge
    reference shows the enrollment, and the plan's remaining balance includes it; the returned reference
    identifies the new entry.

    Args:
        payment_plan_id: Id class — reference number of the proposed payment plan the charge is enrolled on, as
            shown by the payment plan lookup for the patient.
        billing_txn_id: Id class — reference number of the financial-account charge being enrolled, as shown by
            the financial account ledger lookup.
        amount: Fixed-format class — the amount of the charge enrolled on the plan, in USD, 2 decimal places,
            positive; the value is stored exactly as given, rounded half up to 2 decimal places.

    Returns:
        A confirmation sentence (string) naming the new plan ledger entry reference (text beginning "ppt_"),
        the charge reference, the payment plan reference, the amount enrolled in USD with 2 decimal places and
        the plan's remaining balance including the entry in USD with 2 decimal places; receiving this sentence means
        the enrollment is booked.
    """
    amt = round(float(amount), 2)
    rows = ctx.find("payment_plans", payment_plan_id=payment_plan_id)
    plan = rows[0] if rows else {}
    rid = ctx.make_id("ppt_", payment_plan_id, billing_txn_id, amt, "initial_enrollment")
    ctx.create("payplan_transactions", rid, payplan_txn_id=rid, payment_plan_id=payment_plan_id,
               customer_id=plan.get("customer_id"), event_type="payplan_balance_enrolled",
               txn_date=ctx.now()[:10], amount=amt, billing_txn_id=billing_txn_id,
               enroll_reason="initial_enrollment", installment_number=0, payment_method="none",
               channel="phone", autopay=False, extra_kind="none", adjustment_reason="none",
               release_reason="none")
    new_balance = round(float(plan.get("remaining_balance") or 0) + amt, 2)
    ctx.update("payment_plans", payment_plan_id, remaining_balance=new_balance)
    return (f"Charge {billing_txn_id} enrolled on payment plan {payment_plan_id} as entry {rid}: "
            f"{amt:.2f} USD; plan remaining balance now {new_balance:.2f} USD.")


@tool(owner="user", rw="write")
def sign_installment_agreement_b4bb7ade(ctx: ToolContext, payment_plan_id: str, installment_amount: float,
                                        down_payment_usd: float, first_due_date: str) -> str:
    """The patient signs the installment agreement of a proposed payment plan in their own name, accepting the
    monthly installment, the down payment and the due date of installment 1 written into it.

    One call turns the proposed plan into an active plan: its status becomes active, today becomes its signing
    date, and the installment, down payment and installment-1 due date given are written onto the plan. No payment is
    taken by this signature. On success the plan shows status active with the signed terms; the returned
    sentence confirms the signature.

    Args:
        payment_plan_id: Id class — reference number of the proposed payment plan being signed, as read to the
            patient from the payment plan lookup.
        installment_amount: Fixed-format class — the monthly installment written into the agreement, in USD,
            2 decimal places, positive; stored exactly as given, rounded half up to 2 decimal places.
        down_payment_usd: Fixed-format class — the down payment written into the agreement, in USD, 2 decimal
            places, 0.00 when none is due; stored exactly as given, rounded half up to 2 decimal places.
        first_due_date: Fixed-format class — the due date of installment 1, as a calendar date in the format
            YYYY-MM-DD (Eastern time calendar day), stored exactly as given.

    Returns:
        A confirmation sentence (string) naming the payment plan reference, its new status active, the signing
        date (YYYY-MM-DD), the monthly installment and the down payment in USD with 2 decimal places, and the
        due date of installment 1 (YYYY-MM-DD); receiving this sentence means the agreement is signed and in force.
    """
    inst = round(float(installment_amount), 2)
    down = round(float(down_payment_usd), 2)
    signed = ctx.now()[:10]
    ctx.update("payment_plans", payment_plan_id, status="active", agreement_signed_date=signed,
               first_due_date=first_due_date, installment_amount=inst, down_payment_usd=down)
    return (f"Payment plan {payment_plan_id} signed on {signed}; status active; installment {inst:.2f} USD; "
            f"down payment {down:.2f} USD; installment 1 due {first_due_date}.")


@tool(owner="agent", rw="write")
def enroll_add_on_charge_102110ed(ctx: ToolContext, payment_plan_id: str, billing_txn_id: str, amount: float) -> str:
    """Add one financial-account charge to a signed, active payment plan as an add-on entry of that plan.

    One call adds one plan ledger entry of kind "balance enrolled" with enrollment reason add_on, dated today
    and pointing at the charge, and raises the plan's remaining balance by the amount given. The charge itself
    on the financial account is not changed, and the plan's installment and term are not changed by this call.
    On success a lookup of the plan ledger by the charge reference shows the add-on, and the plan's remaining
    balance includes it; the returned reference identifies the new entry.

    Args:
        payment_plan_id: Id class — reference number of the active payment plan receiving the add-on, as shown by
            the payment plan lookup for the patient.
        billing_txn_id: Id class — reference number of the financial-account charge being added, as shown by the
            financial account ledger lookup.
        amount: Fixed-format class — the amount of the charge added to the plan, in USD, 2 decimal places,
            positive; the value is stored exactly as given, rounded half up to 2 decimal places.

    Returns:
        A confirmation sentence (string) naming the new plan ledger entry reference (text beginning "ppt_"),
        the charge reference, the payment plan reference, the amount added in USD with 2 decimal places and the
        plan's remaining balance including the add-on in USD with 2 decimal places; receiving this sentence means
        the add-on is booked.
    """
    amt = round(float(amount), 2)
    rows = ctx.find("payment_plans", payment_plan_id=payment_plan_id)
    plan = rows[0] if rows else {}
    rid = ctx.make_id("ppt_", payment_plan_id, billing_txn_id, amt, "add_on")
    ctx.create("payplan_transactions", rid, payplan_txn_id=rid, payment_plan_id=payment_plan_id,
               customer_id=plan.get("customer_id"), event_type="payplan_balance_enrolled",
               txn_date=ctx.now()[:10], amount=amt, billing_txn_id=billing_txn_id, enroll_reason="add_on",
               installment_number=0, payment_method="none", channel="phone", autopay=False,
               extra_kind="none", adjustment_reason="none", release_reason="none")
    new_balance = round(float(plan.get("remaining_balance") or 0) + amt, 2)
    ctx.update("payment_plans", payment_plan_id, remaining_balance=new_balance)
    return (f"Charge {billing_txn_id} added to payment plan {payment_plan_id} as entry {rid}: {amt:.2f} USD; "
            f"plan remaining balance now {new_balance:.2f} USD.")


@tool(owner="agent", rw="write")
def enroll_add_on_fee_792da8e6(ctx: ToolContext, payment_plan_id: str, amount: float) -> str:
    """Book an add-on fee of an active payment plan into that plan's balance, as one fee entry of the plan's ledger.

    One call adds one plan ledger entry of kind "balance enrolled" with enrollment reason setup_fee, dated
    today and carrying no financial-account charge reference, and raises the plan's remaining balance by the
    amount given. On success the plan's ledger lists the fee entry and the plan's remaining balance includes
    it; the returned reference identifies the new entry.

    Args:
        payment_plan_id: Id class — reference number of the active payment plan whose balance is charged, as
            shown by the payment plan lookup for the patient.
        amount: Fixed-format class — the add-on fee booked into the plan balance, in USD, 2 decimal places,
            positive; the value is stored exactly as given, rounded half up to 2 decimal places.

    Returns:
        A confirmation sentence (string) naming the new plan ledger entry reference (text beginning "ppt_"),
        the payment plan reference, the fee booked in USD with 2 decimal places and the plan's remaining balance
        including the fee in USD with 2 decimal places; receiving this sentence means the fee is booked.
    """
    fee = round(float(amount), 2)
    rows = ctx.find("payment_plans", payment_plan_id=payment_plan_id)
    plan = rows[0] if rows else {}
    rid = ctx.make_id("ppt_", payment_plan_id, fee, ctx.now()[:10], "add_on_fee")
    ctx.create("payplan_transactions", rid, payplan_txn_id=rid, payment_plan_id=payment_plan_id,
               customer_id=plan.get("customer_id"), event_type="payplan_balance_enrolled",
               txn_date=ctx.now()[:10], amount=fee, billing_txn_id=None, enroll_reason="setup_fee",
               installment_number=0, payment_method="none", channel="phone", autopay=False,
               extra_kind="none", adjustment_reason="none", release_reason="none")
    new_balance = round(float(plan.get("remaining_balance") or 0) + fee, 2)
    ctx.update("payment_plans", payment_plan_id, remaining_balance=new_balance)
    return (f"Add-on fee entry {rid} booked on payment plan {payment_plan_id}: {fee:.2f} USD; "
            f"plan remaining balance now {new_balance:.2f} USD.")


@tool(owner="agent", rw="write")
def extend_plan_term_6d1d2771(ctx: ToolContext, payment_plan_id: str, extension_months: int) -> str:
    """Lengthen the term of an active payment plan by a number of monthly installments.

    One call records one modification of the plan: the plan's term (number of monthly installments) and its
    total months of term extension used both grow by the months given, and its modification count grows by
    one. The installment amount and the plan balance are not changed by this call. On success the plan lookup
    shows the longer term; the returned sentence confirms the new figures.

    Args:
        payment_plan_id: Id class — reference number of the active payment plan whose term is lengthened, as
            shown by the payment plan lookup for the patient.
        extension_months: Fixed-format class — the number of monthly installments added to the term, an integer
            count of months, 0 or more.

    Returns:
        A confirmation sentence (string) naming the payment plan reference, the months added (integer), the new
        term in months (integer), the total extension months used (integer) and the new modification count
        (integer); receiving this sentence means the term change is recorded.
    """
    months = int(extension_months)
    rows = ctx.find("payment_plans", payment_plan_id=payment_plan_id)
    plan = rows[0] if rows else {}
    new_term = int(plan.get("term_months") or 0) + months
    new_used = int(plan.get("term_extension_months_used") or 0) + months
    new_mods = int(plan.get("modification_count") or 0) + 1
    ctx.update("payment_plans", payment_plan_id, term_months=new_term, term_extension_months_used=new_used,
               modification_count=new_mods)
    return (f"Payment plan {payment_plan_id} term lengthened by {months} month(s): term now {new_term} months, "
            f"extension months used {new_used}, modifications {new_mods}.")


@tool(owner="user", rw="write")
def accept_add_on_installment_27cdd630(ctx: ToolContext, payment_plan_id: str, installment_amount: float) -> str:
    """The patient accepts, in their own name, a re-spread monthly installment of their active payment plan,
    taking on the changed payment obligation.

    One call records one modification of the plan: the plan's monthly installment becomes the amount given and
    its modification count grows by one. The plan balance and term are not changed by this call, and no
    payment is taken. On success the plan lookup shows the new installment; the returned sentence confirms the
    acceptance.

    Args:
        payment_plan_id: Id class — reference number of the patient's active payment plan, as read to the patient
            from the payment plan lookup.
        installment_amount: Fixed-format class — the new monthly installment the patient accepts, in USD, 2
            decimal places, positive; the value is stored exactly as given, rounded half up to 2 decimal places.

    Returns:
        A confirmation sentence (string) naming the payment plan reference, the new monthly installment in USD
        with 2 decimal places and the new modification count (integer); receiving this sentence means the new
        installment is in force.
    """
    inst = round(float(installment_amount), 2)
    rows = ctx.find("payment_plans", payment_plan_id=payment_plan_id)
    plan = rows[0] if rows else {}
    new_mods = int(plan.get("modification_count") or 0) + 1
    ctx.update("payment_plans", payment_plan_id, installment_amount=inst, modification_count=new_mods)
    return (f"Payment plan {payment_plan_id}: new monthly installment {inst:.2f} USD accepted; "
            f"modifications {new_mods}.")

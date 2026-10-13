"""Hidden task tools for env_0047_pharmacy_benefit_manager / specialty_enrollment_and_assistance.

Each tool performs one atomic business write on a member's specialty enrollment. They are reached
only through unlock_* -> call_* with the name an extended policy's target_tool gives. No tool checks
a policy condition or computes an amount: the figures are worked out by the agent from the policy
and passed in.
"""

from erlbench import ToolContext, tool


@tool(owner="agent", rw="write")
def apply_card_assistance_5ca6ac5a(ctx: ToolContext, specialty_enrollment_id: str, specialty_fill_id: str,
                                    program_name: str, program_year: str, amount: float,
                                    deductible_portion: float) -> str:
    """Apply a manufacturer copay card payment to one shipped specialty fill on the member's
    specialty enrollment. One call books the copay card payment on that fill: it records the
    assistance applied (not backed out of the plan accumulators), posts the matching payment from
    the manufacturer program against the same fill, lowers the enrollment's remaining manufacturer
    assistance by the amount and lowers the member's balance due on the enrollment by the same
    amount. Afterwards the fill shows the card payment in the enrollment's assistance and payment
    history and the member owes that much less. The receipt below confirms the booking.

    Args:
        specialty_enrollment_id: Id class — the reference number of the member's specialty therapy enrollment the fill belongs to, read from the specialty enrollment lookup.
        specialty_fill_id: Id class — the reference number of the shipped fill the card payment is applied to, read from the specialty fill lookup (a shipment entry, not a scheduled one).
        program_name: Verbatim class — the name of the manufacturer copay program exactly as it appears on the program's benefit load entry in the enrollment's assistance history, copied character for character with its original wording, digits and punctuation, no translation, normalisation, summarisation, addition or deletion (verbatim).
        program_year: Fixed-format class — the program year of the manufacturer benefit being drawn on, written as a four-digit year in the format YYYY, exactly as on that benefit load entry.
        amount: Fixed-format class — the card payment applied to the fill, in USD, a positive amount to 2 decimal places (rounded to the nearest cent).
        deductible_portion: Fixed-format class — the part of the card payment that pays the fill's deductible portion, in USD to 2 decimal places (0.00 when none of it pays a deductible portion).

    Returns:
        A dictionary rendered as text with: status ("applied" when the booking succeeded);
        assistance_entry_id (reference number of the assistance-applied entry); payment_entry_id
        (reference number of the matching manufacturer-program payment entry); specialty_fill_id
        (the fill paid); amount (USD, 2 decimal places, the card payment booked);
        assistance_balance (USD, 2 decimal places, the enrollment's remaining manufacturer
        assistance after the booking); balance_due (USD, 2 decimal places, the member's balance due
        on the enrollment after the booking).
    """
    amt = round(float(amount), 2)
    ded = round(float(deductible_portion), 2)
    day = ctx.now()[:10]
    row = (ctx.find("specialty_enrollments", specialty_enrollment_id=specialty_enrollment_id) or [{}])[0]
    cust = row.get("customer_id") or ""
    aid = ctx.make_id("sla_", specialty_enrollment_id, specialty_fill_id, program_name, program_year, amt, ded)
    ctx.create("specialty_ledger", aid, specialty_ledger_id=aid, specialty_enrollment_id=specialty_enrollment_id,
               customer_id=cust, event_type="specialty_assistance_applied",
               specialty_fill_id=specialty_fill_id, entry_date=day, amount=amt, program_name=program_name,
               program_year=program_year, payment_source="not_applicable", payment_method="not_applicable",
               deductible_portion=ded, accumulator_adjusted=False)
    pid = ctx.make_id("slp_", aid)
    ctx.create("specialty_ledger", pid, specialty_ledger_id=pid, specialty_enrollment_id=specialty_enrollment_id,
               customer_id=cust, event_type="specialty_payment_posted",
               specialty_fill_id=specialty_fill_id, entry_date=day, amount=amt, program_name=program_name,
               program_year=program_year, payment_source="manufacturer_assistance", payment_method="copay_card",
               deductible_portion=0.0, accumulator_adjusted=False)
    new_assist = round(float(row.get("assistance_balance") or 0) - amt, 2)
    new_due = round(float(row.get("balance_due") or 0) - amt, 2)
    ctx.update("specialty_enrollments", specialty_enrollment_id, assistance_balance=new_assist, balance_due=new_due)
    return str({"status": "applied", "assistance_entry_id": aid, "payment_entry_id": pid,
                "specialty_fill_id": specialty_fill_id, "amount": amt,
                "assistance_balance": new_assist, "balance_due": new_due})


@tool(owner="user", rw="write")
def pay_fill_balance_998729ec(ctx: ToolContext, specialty_enrollment_id: str, specialty_fill_id: str,
                              amount: float, payment_method: str) -> str:
    """The member pays, with their own payment instrument, toward the member cost share of one
    shipped specialty fill on their specialty enrollment. One call posts the member's payment
    against that fill and lowers the member's balance due on the enrollment by the amount paid.
    Afterwards the payment appears in the enrollment's payment history against that fill and the
    balance due shows the reduction. The receipt below confirms the payment.

    Args:
        specialty_enrollment_id: Id class — the reference number of the member's specialty therapy enrollment, as the agent reads it out from the specialty enrollment lookup.
        specialty_fill_id: Id class — the reference number of the shipped fill being paid, as the agent reads it out from the specialty fill lookup.
        amount: Fixed-format class — the amount the member pays now, in USD, a positive amount to 2 decimal places (rounded to the nearest cent).
        payment_method: Enum class — the instrument the member pays with: credit_card when the member pays with a credit card; debit_card when the member pays with a bank debit card; hsa_fsa_card when the member pays with a health savings account or flexible spending account card; check when the member pays from a checking account by electronic check; copay_card is reserved for manufacturer program payments and is never the instrument of a member's own payment; not_applicable is reserved for entries that are not payments and is never the instrument of a member's own payment.

    Returns:
        A dictionary rendered as text with: status ("posted" when the payment succeeded);
        payment_entry_id (reference number of the member payment entry); specialty_fill_id (the
        fill paid); amount (USD, 2 decimal places, the amount paid); payment_method (the
        instrument recorded); balance_due (USD, 2 decimal places, the member's balance due on the
        enrollment after the payment).
    """
    amt = round(float(amount), 2)
    day = ctx.now()[:10]
    row = (ctx.find("specialty_enrollments", specialty_enrollment_id=specialty_enrollment_id) or [{}])[0]
    cust = row.get("customer_id") or ""
    pid = ctx.make_id("smp_", specialty_enrollment_id, specialty_fill_id, amt, payment_method)
    ctx.create("specialty_ledger", pid, specialty_ledger_id=pid, specialty_enrollment_id=specialty_enrollment_id,
               customer_id=cust, event_type="specialty_payment_posted",
               specialty_fill_id=specialty_fill_id, entry_date=day, amount=amt, program_name="",
               program_year="", payment_source="member", payment_method=payment_method,
               deductible_portion=0.0, accumulator_adjusted=False)
    new_due = round(float(row.get("balance_due") or 0) - amt, 2)
    ctx.update("specialty_enrollments", specialty_enrollment_id, balance_due=new_due)
    return str({"status": "posted", "payment_entry_id": pid, "specialty_fill_id": specialty_fill_id,
                "amount": amt, "payment_method": payment_method, "balance_due": new_due})



@tool(owner="agent", rw="write")
def apply_maximizer_draw_3be5be4a(ctx: ToolContext, specialty_enrollment_id: str, specialty_fill_id: str,
                                  program_name: str, program_year: str, amount: float,
                                  deductible_portion: float) -> str:
    """Apply a maximizer program draw to one shipped specialty fill on the member's specialty
    enrollment. One call books the manufacturer program's draw on that fill: it records the
    assistance applied with the part of it that pays the fill's deductible portion (not backed out
    of the plan accumulators), posts the matching payment from the manufacturer program against the same fill,
    lowers the enrollment's remaining manufacturer assistance by the amount and lowers the member's
    balance due on the enrollment by the same amount. Afterwards the fill shows the program draw in
    the enrollment's assistance and payment history and the member owes that much less. The
    receipt below confirms the booking.

    Args:
        specialty_enrollment_id: Id class — the reference number of the member's specialty therapy enrollment the fill belongs to, read from the specialty enrollment lookup.
        specialty_fill_id: Id class — the reference number of the shipped fill the program draw is applied to, read from the specialty fill lookup (a shipment entry, not a scheduled one).
        program_name: Verbatim class — the name of the manufacturer program exactly as it appears on the program's benefit load entry in the enrollment's assistance history, copied character for character with its original wording, digits and punctuation, no translation, normalisation, summarisation, addition or deletion (verbatim).
        program_year: Fixed-format class — the program year of the benefit being drawn on, written as a four-digit year in the format YYYY, exactly as on that benefit load entry.
        amount: Fixed-format class — the program draw applied to the fill, in USD, a positive amount to 2 decimal places (rounded to the nearest cent).
        deductible_portion: Fixed-format class — the part of the program draw that pays the fill's deductible portion, in USD to 2 decimal places (0.00 when none of it pays a deductible portion).

    Returns:
        A dictionary rendered as text with: status ("applied" when the booking succeeded);
        assistance_entry_id (reference number of the assistance-applied entry); payment_entry_id
        (reference number of the matching manufacturer-program payment entry); specialty_fill_id
        (the fill paid); amount (USD, 2 decimal places, the draw booked); assistance_balance (USD,
        2 decimal places, the enrollment's remaining manufacturer assistance after the booking);
        balance_due (USD, 2 decimal places, the member's balance due on the enrollment after the
        booking).
    """
    amt = round(float(amount), 2)
    ded = round(float(deductible_portion), 2)
    day = ctx.now()[:10]
    row = (ctx.find("specialty_enrollments", specialty_enrollment_id=specialty_enrollment_id) or [{}])[0]
    cust = row.get("customer_id") or ""
    aid = ctx.make_id("smd_", specialty_enrollment_id, specialty_fill_id, program_name, program_year, amt, ded)
    ctx.create("specialty_ledger", aid, specialty_ledger_id=aid, specialty_enrollment_id=specialty_enrollment_id,
               customer_id=cust, event_type="specialty_assistance_applied", specialty_fill_id=specialty_fill_id,
               entry_date=day, amount=amt, program_name=program_name, program_year=program_year,
               payment_source="not_applicable", payment_method="not_applicable", deductible_portion=ded,
               accumulator_adjusted=False)
    pid = ctx.make_id("smq_", aid)
    ctx.create("specialty_ledger", pid, specialty_ledger_id=pid, specialty_enrollment_id=specialty_enrollment_id,
               customer_id=cust, event_type="specialty_payment_posted", specialty_fill_id=specialty_fill_id,
               entry_date=day, amount=amt, program_name=program_name, program_year=program_year,
               payment_source="manufacturer_assistance", payment_method="copay_card", deductible_portion=0.0,
               accumulator_adjusted=False)
    new_assist = round(float(row.get("assistance_balance") or 0) - amt, 2)
    new_due = round(float(row.get("balance_due") or 0) - amt, 2)
    ctx.update("specialty_enrollments", specialty_enrollment_id, assistance_balance=new_assist, balance_due=new_due)
    return str({"status": "applied", "assistance_entry_id": aid, "payment_entry_id": pid,
                "specialty_fill_id": specialty_fill_id, "amount": amt,
                "assistance_balance": new_assist, "balance_due": new_due})


@tool(owner="user", rw="write")
def pay_hold_release_166e6883(ctx: ToolContext, specialty_enrollment_id: str, specialty_fill_id: str,
                              amount: float, payment_method: str) -> str:
    """The member pays, with their own payment instrument, the amount needed to lift a hold placed
    on their specialty enrollment for an overdue balance. One call posts the member's payment
    against the shipped fill it is applied to and lowers the member's balance due on the enrollment
    by the amount paid; it does not itself change the enrollment's hold status. Afterwards the
    payment appears in the enrollment's payment history against that fill and the balance due shows
    the reduction. The receipt below confirms the payment.

    Args:
        specialty_enrollment_id: Id class — the reference number of the member's held specialty therapy enrollment, as the agent reads it out from the specialty enrollment lookup.
        specialty_fill_id: Id class — the reference number of the shipped fill the payment is applied to, as the agent reads it out from the specialty fill lookup.
        amount: Fixed-format class — the amount the member pays now, in USD, a positive amount to 2 decimal places (rounded to the nearest cent).
        payment_method: Enum class — the instrument the member pays with: credit_card when the member pays with a credit card; debit_card when the member pays with a bank debit card; hsa_fsa_card when the member pays with a health savings account or flexible spending account card; check when the member pays from a checking account by electronic check; copay_card is reserved for manufacturer program payments and is never the instrument of a member's own payment; not_applicable is reserved for entries that are not payments and is never the instrument of a member's own payment.

    Returns:
        A dictionary rendered as text with: status ("posted" when the payment succeeded);
        payment_entry_id (reference number of the member payment entry); specialty_fill_id (the
        fill paid); amount (USD, 2 decimal places, the amount paid); payment_method (the
        instrument recorded); balance_due (USD, 2 decimal places, the member's balance due on the
        enrollment after the payment).
    """
    amt = round(float(amount), 2)
    day = ctx.now()[:10]
    row = (ctx.find("specialty_enrollments", specialty_enrollment_id=specialty_enrollment_id) or [{}])[0]
    cust = row.get("customer_id") or ""
    pid = ctx.make_id("shr_", specialty_enrollment_id, specialty_fill_id, amt, payment_method)
    ctx.create("specialty_ledger", pid, specialty_ledger_id=pid, specialty_enrollment_id=specialty_enrollment_id,
               customer_id=cust, event_type="specialty_payment_posted", specialty_fill_id=specialty_fill_id,
               entry_date=day, amount=amt, program_name="", program_year="", payment_source="member",
               payment_method=payment_method, deductible_portion=0.0, accumulator_adjusted=False)
    new_due = round(float(row.get("balance_due") or 0) - amt, 2)
    ctx.update("specialty_enrollments", specialty_enrollment_id, balance_due=new_due)
    return str({"status": "posted", "payment_entry_id": pid, "specialty_fill_id": specialty_fill_id,
                "amount": amt, "payment_method": payment_method, "balance_due": new_due})

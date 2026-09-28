"""Hidden task tools of the dwelling_underwriting_and_renewal difficulty (LandlordGuard Dwelling Fire Policy).

Each tool performs one atomic write on the landlord's dwelling policy or its premium ledger. None of
them checks a business precondition or computes a figure: the amount, the dates and the choices
passed in are worked out by the caller from the published rules and the policy records.
"""

from erlbench import ToolContext, tool


@tool(owner="agent", rw="write")
def issue_vacancy_permit_2309bb3c(ctx: ToolContext, dwelling_policy_id: str, permit_start: str,
                                  permit_expiration: str, charge: float) -> str:
    """Issue a vacancy permit on one LandlordGuard dwelling policy and post its charge. One call writes
    the permit's first and last day onto the policy, so the vacancy permit shows on the policy from that
    moment, and posts one additional-premium entry for the vacancy permit, dated the permit's first
    day, that raises the policy's premium balance by the charge. Success is the receipt below; the
    permit dates and the new charge are then visible on the policy and on its premium account.

    Args:
        dwelling_policy_id: Id class — the reference id of the landlord dwelling policy record the permit is issued on, as returned by the dwelling policy lookup for the verified caller.
        permit_start: Fixed-format class — the first day the permit covers, written YYYY-MM-DD as a calendar date in the policy's local time zone; never empty.
        permit_expiration: Fixed-format class — the last day the permit covers (the permit covers this day), written YYYY-MM-DD as a calendar date in the policy's local time zone; never empty.
        charge: Fixed-format class — the vacancy permit charge in USD, a positive amount given to 2 decimal places; a value with more places is rounded half-up to 2 decimal places when posted.

    Returns:
        A one-line confirmation string "Vacancy permit issued: entry <entry_id> on policy <dwelling_policy_id>, permit <permit_start> to <permit_expiration>, charge <charge> USD posted <posted_date>." where entry_id is the new premium-ledger entry reference id, dwelling_policy_id echoes the policy, permit_start and permit_expiration are YYYY-MM-DD dates, charge is the USD amount posted to 2 decimal places and posted_date is today's YYYY-MM-DD date. Receiving this line means the permit and its charge are recorded.
    """
    amount = round(float(charge), 2)
    rid = ctx.make_id("dvp_", dwelling_policy_id, permit_start, permit_expiration, amount)
    today = ctx.now()[:10]
    policy = (ctx.find("dwelling_policies", dwelling_policy_id=dwelling_policy_id) or [{}])[0]
    ctx.update("dwelling_policies", dwelling_policy_id, vacancy_permit_start=permit_start,
               vacancy_permit_expiration=permit_expiration)
    ctx.create("dwelling_billing", rid, dwelling_billing_id=rid, dwelling_policy_id=dwelling_policy_id,
               customer_id=policy.get("customer_id", ""), event_type="dwelling_additional_premium",
               posted_date=today, term_effective_date="", installment_number=0, due_date="",
               amount=amount, fee_code="none", payer="none", payment_method="none", payment_reference="",
               change_reason="vacancy_permit", effective_date=permit_start, credit_basis="none",
               source_billing_id="")
    ctx.update("dwelling_policies", dwelling_policy_id,
               premium_balance=round(float(policy.get("premium_balance") or 0) + amount, 2))
    return (f"Vacancy permit issued: entry {rid} on policy {dwelling_policy_id}, permit {permit_start} to "
            f"{permit_expiration}, charge {amount:.2f} USD posted {today}.")


@tool(owner="agent", rw="write")
def record_renewal_indication_d716047a(ctx: ToolContext, dwelling_policy_id: str,
                                       indicated_renewal_premium: float) -> str:
    """Record the renewal offer's indicated premium on one LandlordGuard dwelling policy. One call writes
    the premium indicated for the upcoming twelve-month term onto the policy record, replacing any
    indication already shown there; nothing is billed and the current term is not changed. Success is
    the receipt below, and the indicated renewal premium is then visible on the policy.

    Args:
        dwelling_policy_id: Id class — the reference id of the landlord dwelling policy record being offered for renewal, as returned by the dwelling policy lookup for the verified caller.
        indicated_renewal_premium: Fixed-format class — the indicated annual premium for the upcoming term in USD, a positive amount given to 2 decimal places; a value with more places is rounded half-up to 2 decimal places when recorded.

    Returns:
        A one-line confirmation string "Renewal indication recorded on policy <dwelling_policy_id>: indicated renewal premium <indicated_renewal_premium> USD." where dwelling_policy_id echoes the policy and indicated_renewal_premium is the recorded USD amount to 2 decimal places. Receiving this line means the indication is on the policy.
    """
    amount = round(float(indicated_renewal_premium), 2)
    ctx.update("dwelling_policies", dwelling_policy_id, indicated_renewal_premium=amount)
    return f"Renewal indication recorded on policy {dwelling_policy_id}: indicated renewal premium {amount:.2f} USD."


@tool(owner="user", rw="write")
def pay_renewal_premium_4100e9a3(ctx: ToolContext, dwelling_policy_id: str, term_effective_date: str,
                                 amount: float, payment_method: str) -> str:
    """Pay the whole renewal term premium of one LandlordGuard dwelling policy in a single payment by the
    named insured. One call records one premium payment from the insured against the upcoming term,
    lowers the policy's premium balance by the amount paid and issues a payment confirmation number.
    Success is the receipt below; the payment and its confirmation number are then visible on the
    policy's premium account.

    Args:
        dwelling_policy_id: Id class — the reference id of the landlord dwelling policy record being paid, as given to the insured by the representative from the dwelling policy lookup.
        term_effective_date: Fixed-format class — the first day of the upcoming term the payment is for, written YYYY-MM-DD as a calendar date in the policy's local time zone; never empty.
        amount: Fixed-format class — the payment amount in USD, a positive amount given to 2 decimal places; a value with more places is rounded half-up to 2 decimal places when recorded.
        payment_method: Enum class — how the insured pays: eft when paying from a bank account by electronic funds transfer; card when paying by debit or credit card; check when mailing or handing over a personal check; mortgagee_check when the mortgage lender pays from escrow by its own check; none when no payment method applies, which never fits a payment the insured makes.

    Returns:
        A one-line confirmation string "Payment received: entry <entry_id>, confirmation <payment_reference>, <amount> USD by <payment_method> for the term starting <term_effective_date>, posted <posted_date>." where entry_id is the new premium-ledger entry reference id, payment_reference is the confirmation number issued for this payment, amount is the USD amount to 2 decimal places, payment_method echoes the method, term_effective_date is the YYYY-MM-DD term start and posted_date is today's YYYY-MM-DD date. Receiving this line means the payment is recorded.
    """
    paid = round(float(amount), 2)
    rid = ctx.make_id("drp_", dwelling_policy_id, term_effective_date, paid, payment_method)
    reference = "4" + rid[-9:].upper()
    today = ctx.now()[:10]
    policy = (ctx.find("dwelling_policies", dwelling_policy_id=dwelling_policy_id) or [{}])[0]
    ctx.create("dwelling_billing", rid, dwelling_billing_id=rid, dwelling_policy_id=dwelling_policy_id,
               customer_id=policy.get("customer_id", ""), event_type="dwelling_payment_received",
               posted_date=today, term_effective_date=term_effective_date, installment_number=0, due_date="",
               amount=paid, fee_code="none", payer="insured", payment_method=payment_method,
               payment_reference=reference, change_reason="none", effective_date="", credit_basis="none",
               source_billing_id="")
    ctx.update("dwelling_policies", dwelling_policy_id,
               premium_balance=round(float(policy.get("premium_balance") or 0) - paid, 2))
    return (f"Payment received: entry {rid}, confirmation {reference}, {paid:.2f} USD by {payment_method} "
            f"for the term starting {term_effective_date}, posted {today}.")


@tool(owner="agent", rw="write")
def assess_installment_fee_8325e06b(ctx: ToolContext, dwelling_policy_id: str, term_effective_date: str,
                                    installment_number: int, amount: float) -> str:
    """Charge the installment service fee for one billed installment of a LandlordGuard dwelling policy. One
    call posts one installment-fee entry on the policy's premium account for the named term and installment
    and raises the premium balance by the fee. Success is the receipt below; the fee then shows on the
    premium account.

    Args:
        dwelling_policy_id: Id class — the reference id of the landlord dwelling policy record, as returned by the dwelling policy lookup for the verified caller.
        term_effective_date: Fixed-format class — the start date of the policy term the installment belongs to, written YYYY-MM-DD as on the billed installment; never empty.
        installment_number: Fixed-format class — the position of the billed installment within its term, an integer 0-4 as shown on the billed installment (1 is the opening installment).
        amount: Fixed-format class — the fee in USD, a positive amount given to 2 decimal places; a value with more places is rounded half-up to 2 decimal places when posted.

    Returns:
        A one-line confirmation string "Installment fee posted: entry <entry_id> on policy <dwelling_policy_id>, term <term_effective_date> installment <installment_number>, <amount> USD on <posted_date>." where entry_id is the new premium-ledger entry reference id, dwelling_policy_id echoes the policy, term_effective_date is YYYY-MM-DD, installment_number is the integer position, amount is the USD fee to 2 decimal places and posted_date is today's YYYY-MM-DD date. Receiving this line means the fee is posted.
    """
    fee = round(float(amount), 2)
    rid = ctx.make_id("dif_", dwelling_policy_id, "installment_fee", term_effective_date, installment_number, "", fee)
    today = ctx.now()[:10]
    policy = (ctx.find("dwelling_policies", dwelling_policy_id=dwelling_policy_id) or [{}])[0]
    ctx.create("dwelling_billing", rid, dwelling_billing_id=rid, dwelling_policy_id=dwelling_policy_id,
               customer_id=policy.get("customer_id", ""), event_type="dwelling_fee_assessed", posted_date=today,
               term_effective_date=term_effective_date, installment_number=int(installment_number), due_date="",
               amount=fee, fee_code="installment_fee", payer="none", payment_method="none", payment_reference="",
               change_reason="none", effective_date="", credit_basis="none", source_billing_id="")
    ctx.update("dwelling_policies", dwelling_policy_id,
               premium_balance=round(float(policy.get("premium_balance") or 0) + fee, 2))
    return (f"Installment fee posted: entry {rid} on policy {dwelling_policy_id}, term {term_effective_date} "
            f"installment {int(installment_number)}, {fee:.2f} USD on {today}.")


@tool(owner="agent", rw="write")
def assess_late_fee_984fd113(ctx: ToolContext, dwelling_policy_id: str, term_effective_date: str,
                             installment_number: int, amount: float) -> str:
    """Charge the late fee for one unpaid installment of a LandlordGuard dwelling policy. One call posts one
    late-fee entry on the policy's premium account for the named term and installment and raises the
    premium balance by the fee. Success is the receipt below; the late fee then shows on the premium
    account.

    Args:
        dwelling_policy_id: Id class — the reference id of the landlord dwelling policy record, as returned by the dwelling policy lookup for the verified caller.
        term_effective_date: Fixed-format class — the start date of the policy term the late installment belongs to, written YYYY-MM-DD as on the billed installment; never empty.
        installment_number: Fixed-format class — the position of the late installment within its term, an integer 0-4 as shown on the billed installment (1 is the opening installment).
        amount: Fixed-format class — the late fee in USD, a positive amount given to 2 decimal places; a value with more places is rounded half-up to 2 decimal places when posted.

    Returns:
        A one-line confirmation string "Late fee posted: entry <entry_id> on policy <dwelling_policy_id>, term <term_effective_date> installment <installment_number>, <amount> USD on <posted_date>." where entry_id is the new premium-ledger entry reference id, dwelling_policy_id echoes the policy, term_effective_date is YYYY-MM-DD, installment_number is the integer position, amount is the USD fee to 2 decimal places and posted_date is today's YYYY-MM-DD date. Receiving this line means the late fee is posted.
    """
    fee = round(float(amount), 2)
    rid = ctx.make_id("dlf_", dwelling_policy_id, "late_fee", term_effective_date, installment_number, "", fee)
    today = ctx.now()[:10]
    policy = (ctx.find("dwelling_policies", dwelling_policy_id=dwelling_policy_id) or [{}])[0]
    ctx.create("dwelling_billing", rid, dwelling_billing_id=rid, dwelling_policy_id=dwelling_policy_id,
               customer_id=policy.get("customer_id", ""), event_type="dwelling_fee_assessed", posted_date=today,
               term_effective_date=term_effective_date, installment_number=int(installment_number), due_date="",
               amount=fee, fee_code="late_fee", payer="none", payment_method="none", payment_reference="",
               change_reason="none", effective_date="", credit_basis="none", source_billing_id="")
    ctx.update("dwelling_policies", dwelling_policy_id,
               premium_balance=round(float(policy.get("premium_balance") or 0) + fee, 2))
    return (f"Late fee posted: entry {rid} on policy {dwelling_policy_id}, term {term_effective_date} "
            f"installment {int(installment_number)}, {fee:.2f} USD on {today}.")


@tool(owner="agent", rw="write")
def assess_returned_payment_fee_55a26ad1(ctx: ToolContext, dwelling_policy_id: str, source_billing_id: str,
                                         amount: float) -> str:
    """Charge the returned-payment fee for one returned payment on a LandlordGuard dwelling policy. One call
    posts one returned-payment fee entry on the policy's premium account that points at the returned
    payment it is charged for, and raises the premium balance by the fee. Success is the receipt below;
    the fee then shows on the premium account next to the returned payment.

    Args:
        dwelling_policy_id: Id class — the reference id of the landlord dwelling policy record, as returned by the dwelling policy lookup for the verified caller.
        source_billing_id: Id class — the reference id of the returned-payment entry on the premium account the fee is charged for, as returned by the premium ledger lookup.
        amount: Fixed-format class — the returned-payment fee in USD, a positive amount given to 2 decimal places; a value with more places is rounded half-up to 2 decimal places when posted.

    Returns:
        A one-line confirmation string "Returned-payment fee posted: entry <entry_id> on policy <dwelling_policy_id> for returned payment <source_billing_id>, <amount> USD on <posted_date>." where entry_id is the new premium-ledger entry reference id, dwelling_policy_id and source_billing_id echo the inputs, amount is the USD fee to 2 decimal places and posted_date is today's YYYY-MM-DD date. Receiving this line means the fee is posted.
    """
    fee = round(float(amount), 2)
    rid = ctx.make_id("drf_", dwelling_policy_id, "returned_payment_fee", "", 0, source_billing_id, fee)
    today = ctx.now()[:10]
    policy = (ctx.find("dwelling_policies", dwelling_policy_id=dwelling_policy_id) or [{}])[0]
    ctx.create("dwelling_billing", rid, dwelling_billing_id=rid, dwelling_policy_id=dwelling_policy_id,
               customer_id=policy.get("customer_id", ""), event_type="dwelling_fee_assessed", posted_date=today,
               term_effective_date="", installment_number=int(0), due_date="",
               amount=fee, fee_code="returned_payment_fee", payer="none", payment_method="none", payment_reference="",
               change_reason="none", effective_date="", credit_basis="none", source_billing_id=source_billing_id)
    ctx.update("dwelling_policies", dwelling_policy_id,
               premium_balance=round(float(policy.get("premium_balance") or 0) + fee, 2))
    return (f"Returned-payment fee posted: entry {rid} on policy {dwelling_policy_id} for returned payment "
            f"{source_billing_id}, {fee:.2f} USD on {today}.")


@tool(owner="user", rw="write")
def pay_off_term_premium_a09f99f1(ctx: ToolContext, dwelling_policy_id: str, amount: float,
                                  payment_method: str) -> str:
    """Pay off the current term of one LandlordGuard dwelling policy in a single payment by the named insured.
    One call records one premium payment from the insured against the current term, lowers the policy's
    premium balance by the amount paid and issues a payment confirmation number. Success is the receipt
    below; the payment and its confirmation number are then visible on the premium account.

    Args:
        dwelling_policy_id: Id class — the reference id of the landlord dwelling policy record being paid, as given to the insured by the representative from the dwelling policy lookup.
        amount: Fixed-format class — the payment amount in USD, a positive amount given to 2 decimal places; a value with more places is rounded half-up to 2 decimal places when recorded.
        payment_method: Enum class — how the insured pays: eft when paying from a bank account by electronic funds transfer; card when paying by debit or credit card; check when mailing or handing over a personal check; mortgagee_check when the mortgage lender pays from escrow by its own check; none when no payment method applies, which never fits a payment the insured makes.

    Returns:
        A one-line confirmation string "Pay-off received: entry <entry_id>, confirmation <payment_reference>, <amount> USD by <payment_method> for the current term starting <term_effective_date>, posted <posted_date>." where entry_id is the new premium-ledger entry reference id, payment_reference is the confirmation number issued for this payment, amount is the USD amount to 2 decimal places, payment_method echoes the method, term_effective_date is the YYYY-MM-DD start of the current term and posted_date is today's YYYY-MM-DD date. Receiving this line means the pay-off is recorded.
    """
    paid = round(float(amount), 2)
    rid = ctx.make_id("dpo_", dwelling_policy_id, paid, payment_method)
    reference = "4" + rid[-9:].upper()
    today = ctx.now()[:10]
    policy = (ctx.find("dwelling_policies", dwelling_policy_id=dwelling_policy_id) or [{}])[0]
    term = policy.get("effective_date", "")
    ctx.create("dwelling_billing", rid, dwelling_billing_id=rid, dwelling_policy_id=dwelling_policy_id,
               customer_id=policy.get("customer_id", ""), event_type="dwelling_payment_received",
               posted_date=today, term_effective_date=term, installment_number=0, due_date="",
               amount=paid, fee_code="none", payer="insured", payment_method=payment_method,
               payment_reference=reference, change_reason="none", effective_date="", credit_basis="none",
               source_billing_id="")
    ctx.update("dwelling_policies", dwelling_policy_id,
               premium_balance=round(float(policy.get("premium_balance") or 0) - paid, 2))
    return (f"Pay-off received: entry {rid}, confirmation {reference}, {paid:.2f} USD by {payment_method} "
            f"for the current term starting {term}, posted {today}.")

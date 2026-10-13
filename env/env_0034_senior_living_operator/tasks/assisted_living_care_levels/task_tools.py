"""Hidden task tools of the assisted_living_care_levels difficulty (Larkspur Senior Living).

Each tool performs exactly one atomic write on an Assisted Living Residency and Care Agreement
with the values the caller supplies; none of them looks anything up, judges eligibility or
works out an amount. They are reached only through the unlock/call meta-tools.
"""

from erlbench import ToolContext, tool


@tool(owner="agent", rw="write")
def post_absence_care_credit_bb749fc3(ctx: ToolContext, assisted_residency_id: str, source_entry_id: str,
                                      absence_start_date: str, billing_period: str, amount: float) -> str:
    """Post an absence care credit on an assisted living resident's account: one credit that relieves part of
    the care fee charged for a billing month during which the resident was away from the community. The
    credit is written to the resident's ledger as a credit of the absence-care kind, tied to the care fee
    charge it relieves and to the start date of the absence, and the amount owed on the residency account
    goes down by the amount credited. Once posted the credit shows on the resident's statement for that
    month and the residency balance is lower by the same amount.

    Args:
        assisted_residency_id: Id class — reference number of the assisted living residency whose account is credited, as returned by the assisted living residency lookup.
        source_entry_id: Id class — reference number of the ledger entry of the care fee charge being relieved, as returned by the assisted living ledger lookup.
        absence_start_date: Fixed-format class — the date the absence began, exactly as recorded on the residency, written YYYY-MM-DD in the community's local calendar.
        billing_period: Fixed-format class — the billing month the credit relates to, written YYYY-MM (for example the month of the care fee charge relieved).
        amount: Fixed-format class — the credit amount in USD, a positive number with 2 decimal places, already rounded to the cent; it is posted exactly as given.

    Returns:
        A dictionary rendered as text with keys: "status" ("posted" when the credit was written), "entry_id"
        (the reference number of the new ledger credit), "assisted_residency_id" (the residency credited),
        "amount" (the USD amount credited, 2 decimal places) and "account_balance" (the residency balance in
        USD after the credit, 2 decimal places; negative means a credit balance).
    """
    found = ctx.find("assisted_residencies", assisted_residency_id=assisted_residency_id)
    res = found[0] if found else {}
    rid = ctx.make_id("acc_", assisted_residency_id, source_entry_id, absence_start_date, billing_period, amount)
    value = round(float(amount), 2)
    ctx.create("assisted_ledger", rid, assisted_entry_id=rid, assisted_residency_id=assisted_residency_id,
               customer_id=res.get("customer_id"), event_type="assisted_credit", amount=value,
               posting_date=ctx.now()[:10], billing_period=billing_period, credit_reason="absence_care_credit",
               source_entry_id=source_entry_id, absence_start_date=absence_start_date)
    balance = round(float(res.get("account_balance") or 0) - value, 2)
    ctx.update("assisted_residencies", assisted_residency_id, account_balance=balance)
    return str({"status": "posted", "entry_id": rid, "assisted_residency_id": assisted_residency_id,
                "amount": value, "account_balance": balance})


@tool(owner="agent", rw="write")
def assess_late_fee_246a7744(ctx: ToolContext, assisted_residency_id: str, billing_period: str,
                             amount: float) -> str:
    """Assess a late fee on an assisted living resident's account for one billing month that was left unpaid
    after its grace period. The fee is written to the resident's ledger as a late fee charge for that billing
    month and the amount owed on the residency account goes up by the fee. Once assessed the fee appears on
    the resident's statement and in the residency balance.

    Args:
        assisted_residency_id: Id class — reference number of the assisted living residency charged, as returned by the assisted living residency lookup.
        billing_period: Fixed-format class — the billing month left unpaid that the late fee is assessed for, written YYYY-MM.
        amount: Fixed-format class — the late fee in USD, a positive number with 2 decimal places, already rounded to the cent; it is charged exactly as given.

    Returns:
        A dictionary rendered as text with keys: "status" ("assessed" when the fee was written), "entry_id"
        (the reference number of the new late fee charge), "billing_period" (the month it is assessed for,
        YYYY-MM), "amount" (the USD fee, 2 decimal places) and "account_balance" (the residency balance in
        USD after the fee, 2 decimal places).
    """
    found = ctx.find("assisted_residencies", assisted_residency_id=assisted_residency_id)
    res = found[0] if found else {}
    rid = ctx.make_id("alf_", assisted_residency_id, billing_period, amount)
    value = round(float(amount), 2)
    ctx.create("assisted_ledger", rid, assisted_entry_id=rid, assisted_residency_id=assisted_residency_id,
               customer_id=res.get("customer_id"), event_type="assisted_late_fee_charge", amount=value,
               posting_date=ctx.now()[:10], billing_period=billing_period)
    balance = round(float(res.get("account_balance") or 0) + value, 2)
    ctx.update("assisted_residencies", assisted_residency_id, account_balance=balance)
    return str({"status": "assessed", "entry_id": rid, "billing_period": billing_period,
                "amount": value, "account_balance": balance})


@tool(owner="agent", rw="write")
def post_level_increase_care_charge_9f33663f(ctx: ToolContext, assisted_residency_id: str, care_level_billed: str,
                                             service_from_date: str, service_to_date: str, days_billed: int,
                                             amount: float) -> str:
    """Post the care fee charge that bills a care level increase for the rest of a month the resident was
    already billed for at the earlier level. The charge is written to the resident's ledger as a care fee
    charge on the prorated level change basis, for the care level and the span of days given, in the billing
    month of the first day covered, and the amount owed on the residency account goes up by the charge. Once
    posted the charge appears on the resident's statement for that month.

    Args:
        assisted_residency_id: Id class — reference number of the assisted living residency charged, as returned by the assisted living residency lookup.
        care_level_billed: Enum class — the care level whose increase this charge bills, one of: Assisted Living Care Level 1 when the residency now carries care level 1; Assisted Living Care Level 2 when it now carries care level 2; Assisted Living Care Level 3 when it now carries care level 3; Assisted Living Care Level 4 when it now carries care level 4; Assisted Living Care Level 5 when it now carries care level 5; Assisted Living Care Level 6 when it now carries care level 6.
        service_from_date: Fixed-format class — first day covered by the charge, written YYYY-MM-DD; the billing month of the charge is the month of this day.
        service_to_date: Fixed-format class — last day covered by the charge, written YYYY-MM-DD, in the same month as the first day.
        days_billed: Fixed-format class — number of days covered, an integer counting both the first and the last day.
        amount: Fixed-format class — the charge in USD, a positive number with 2 decimal places, already rounded to the cent; it is charged exactly as given.

    Returns:
        A dictionary rendered as text with keys: "status" ("posted" when the charge was written), "entry_id"
        (the reference number of the new care fee charge), "care_level_billed" (the care level billed),
        "billing_period" (the month charged, YYYY-MM), "amount" (the USD charge, 2 decimal places) and
        "account_balance" (the residency balance in USD after the charge, 2 decimal places).
    """
    found = ctx.find("assisted_residencies", assisted_residency_id=assisted_residency_id)
    res = found[0] if found else {}
    rid = ctx.make_id("alc_", assisted_residency_id, care_level_billed, service_from_date, service_to_date,
                      days_billed, amount)
    value = round(float(amount), 2)
    period = str(service_from_date)[:7]
    ctx.create("assisted_ledger", rid, assisted_entry_id=rid, assisted_residency_id=assisted_residency_id,
               customer_id=res.get("customer_id"), event_type="assisted_care_fee_charge", amount=value,
               posting_date=ctx.now()[:10], billing_period=period, charge_basis="prorated_level_change",
               care_level_billed=care_level_billed, service_from_date=service_from_date,
               service_to_date=service_to_date, days_billed=int(days_billed))
    balance = round(float(res.get("account_balance") or 0) + value, 2)
    ctx.update("assisted_residencies", assisted_residency_id, account_balance=balance)
    return str({"status": "posted", "entry_id": rid, "care_level_billed": care_level_billed,
                "billing_period": period, "amount": value, "account_balance": balance})


@tool(owner="user", rw="write")
def sign_apartment_change_e633e519(ctx: ToolContext, assisted_residency_id: str, apartment_type: str,
                                   apartment_number: str, monthly_base_rent: float, rent_effective_date: str,
                                   transfer_fee: float) -> str:
    """Sign, as the resident or the resident's financial representative, the agreement that moves an assisted
    living resident to another assisted living apartment in the same community. Signing changes the
    residency to the new apartment type and apartment number with the new monthly rent from the date of
    possession, and charges the apartment transfer fee to the resident's ledger as an apartment change
    add-on in the billing month of possession, raising the amount owed on the residency account by that fee.
    The signer sees the confirmed apartment, rent, possession date and fee.

    Args:
        assisted_residency_id: Id class — reference number of the assisted living residency that moves, as given by the representative who handed over this signature.
        apartment_type: Enum class — the apartment type moved into, one of: AL Studio when the new apartment is a studio; AL One-Bedroom when the new apartment is a one-bedroom; AL Companion Suite when the new apartment is a shared companion suite.
        apartment_number: Verbatim class — the number of the new apartment exactly as the resident's family stated it, copied character for character with no change to letters, digits or punctuation (verbatim).
        monthly_base_rent: Fixed-format class — the monthly rent of the new apartment in USD, with 2 decimal places, as confirmed to the signer.
        rent_effective_date: Fixed-format class — the date of possession of the new apartment, from which the new rent applies, written YYYY-MM-DD.
        transfer_fee: Fixed-format class — the apartment transfer fee in USD, a positive number with 2 decimal places, already rounded to the cent, as confirmed to the signer.

    Returns:
        A dictionary rendered as text with keys: "status" ("signed" when the change was recorded),
        "assisted_residency_id" (the residency moved), "apartment_type" and "apartment_number" (the new
        apartment), "monthly_base_rent" (USD, 2 decimal places), "rent_effective_date" (YYYY-MM-DD),
        "fee_entry_id" (the reference number of the transfer fee charge), "transfer_fee" (USD, 2 decimal
        places) and "account_balance" (the residency balance in USD after the fee, 2 decimal places).
    """
    found = ctx.find("assisted_residencies", assisted_residency_id=assisted_residency_id)
    res = found[0] if found else {}
    rent = round(float(monthly_base_rent), 2)
    fee = round(float(transfer_fee), 2)
    ctx.update("assisted_residencies", assisted_residency_id, apartment_type=apartment_type,
               apartment_number=apartment_number, monthly_base_rent=rent, rent_effective_date=rent_effective_date)
    rid = ctx.make_id("aac_", assisted_residency_id, apartment_type, apartment_number, monthly_base_rent,
                      rent_effective_date, transfer_fee)
    day = str(rent_effective_date)
    ctx.create("assisted_ledger", rid, assisted_entry_id=rid, assisted_residency_id=assisted_residency_id,
               customer_id=res.get("customer_id"), event_type="assisted_addon_charge", amount=fee,
               posting_date=ctx.now()[:10], addon_code="apartment_change", billing_period=day[:7],
               service_date=day, quantity=1)
    balance = round(float(res.get("account_balance") or 0) + fee, 2)
    ctx.update("assisted_residencies", assisted_residency_id, account_balance=balance)
    return str({"status": "signed", "assisted_residency_id": assisted_residency_id,
                "apartment_type": apartment_type, "apartment_number": apartment_number,
                "monthly_base_rent": rent, "rent_effective_date": rent_effective_date,
                "fee_entry_id": rid, "transfer_fee": fee, "account_balance": balance})


@tool(owner="agent", rw="write")
def post_returned_payment_fee_036f277a(ctx: ToolContext, assisted_residency_id: str, source_entry_id: str,
                                       billing_period: str, amount: float) -> str:
    """Charge the returned payment fee on an assisted living resident's account for one payment that the bank
    returned unpaid. The fee is written to the resident's ledger as a returned-payment add-on charge tied to
    the reinstated returned payment entry, dated the day it is charged, and the amount owed on the residency
    account goes up by the fee. Once charged the fee appears on the resident's statement for the billing
    month given.

    Args:
        assisted_residency_id: Id class — reference number of the assisted living residency charged, as returned by the assisted living residency lookup.
        source_entry_id: Id class — reference number of the ledger entry that reinstated the returned payment, as returned by the assisted living ledger lookup.
        billing_period: Fixed-format class — the billing month the fee is charged in, written YYYY-MM.
        amount: Fixed-format class — the fee in USD, a positive number with 2 decimal places, already rounded to the cent; it is charged exactly as given.

    Returns:
        A dictionary rendered as text with keys: "status" ("charged" when the fee was written), "entry_id"
        (the reference number of the new fee charge), "source_entry_id" (the returned payment entry it refers
        to), "amount" (the USD fee, 2 decimal places) and "account_balance" (the residency balance in USD
        after the fee, 2 decimal places).
    """
    found = ctx.find("assisted_residencies", assisted_residency_id=assisted_residency_id)
    res = found[0] if found else {}
    rid = ctx.make_id("arf_", assisted_residency_id, source_entry_id, billing_period, amount)
    value = round(float(amount), 2)
    ctx.create("assisted_ledger", rid, assisted_entry_id=rid, assisted_residency_id=assisted_residency_id,
               customer_id=res.get("customer_id"), event_type="assisted_addon_charge", amount=value,
               posting_date=ctx.now()[:10], addon_code="returned_payment", billing_period=billing_period,
               service_date=ctx.now()[:10], quantity=1, source_entry_id=source_entry_id)
    balance = round(float(res.get("account_balance") or 0) + value, 2)
    ctx.update("assisted_residencies", assisted_residency_id, account_balance=balance)
    return str({"status": "charged", "entry_id": rid, "source_entry_id": source_entry_id,
                "amount": value, "account_balance": balance})


@tool(owner="user", rw="write")
def submit_advance_payment_8dbe3a8d(ctx: ToolContext, assisted_residency_id: str, amount: float) -> str:
    """Pay, as the resident or the resident's financial representative, an amount by credit card toward an
    assisted living resident's account. The card is charged the amount given and the payment is written to
    the resident's ledger as a payment from the resident or family by credit card, with a card authorization
    code issued on the spot; the amount owed on the residency account goes down by the payment, and an amount
    beyond what is owed stays on the account as a credit balance for the coming statements. The payer sees
    the authorization code and the new balance.

    Args:
        assisted_residency_id: Id class — reference number of the assisted living residency paid toward, as given by the representative who handed over this payment.
        amount: Fixed-format class — the payment amount in USD, a positive number with 2 decimal places, as confirmed to the payer.

    Returns:
        A dictionary rendered as text with keys: "status" ("paid" when the card payment was posted),
        "payment_reference" (the card authorization code issued for this payment), "amount" (the USD amount
        paid, 2 decimal places) and "account_balance" (the residency balance in USD after the payment,
        2 decimal places; negative means a credit balance held for coming statements).
    """
    found = ctx.find("assisted_residencies", assisted_residency_id=assisted_residency_id)
    res = found[0] if found else {}
    value = round(float(amount), 2)
    rid = ctx.make_id("apy_", assisted_residency_id, amount)
    auth = "AUTH-" + rid[-6:].upper()
    ctx.create("assisted_ledger", rid, assisted_entry_id=rid, assisted_residency_id=assisted_residency_id,
               customer_id=res.get("customer_id"), event_type="assisted_payment", amount=value,
               posting_date=ctx.now()[:10], payment_reference=auth, payment_method="credit_card",
               payer_type="resident_or_family", billing_period="")
    balance = round(float(res.get("account_balance") or 0) - value, 2)
    ctx.update("assisted_residencies", assisted_residency_id, account_balance=balance)
    return str({"status": "paid", "payment_reference": auth, "amount": value, "account_balance": balance})

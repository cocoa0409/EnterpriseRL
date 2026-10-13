"""Hidden task tools of the folio_charges_and_adjustments difficulty (Guest Folios, Ashbury Hotels & Resorts).

Every tool performs exactly one atomic write on one guest folio and keeps the folio balance equal to
its lines; none of them judges eligibility, computes an amount or checks what else stands on the folio.
"""

from erlbench import ToolContext, tool


@tool(owner="agent", rw="write")
def post_breakfast_credit_af6b7bed(ctx: ToolContext, folio_id: str, loyalty_member_id: str,
                                   related_posting_id: str, credit_amount: float) -> str:
    """Guest services posts the Ashbury Rewards elite breakfast credit that the breakfast outlet did not
    apply, against one breakfast charge on an open guest folio. One call books one elite breakfast credit
    line that names the breakfast charge it offsets, dated to that breakfast's morning, recorded as posted
    by guest services today with the reason that the elite benefit was not applied, and it lowers the
    folio balance by the credited amount. The guest sees the credit printed under the breakfast charge on
    the bill.

    Args:
        folio_id: Id class — the reference number of the guest folio of the stay, read from the folio lookup.
        loyalty_member_id: Id class — the reference number of the Ashbury Rewards membership credited for the
            stay, read from the folio or membership lookup.
        related_posting_id: Id class — the reference number of the breakfast charge line being offset, read
            from the folio line lookup.
        credit_amount: Fixed-format class — the credit to book, in USD, 2 decimal places, always positive
            (rounded half up to the cent before booking).

    Returns:
        A dictionary receipt: posting_id (text, reference number of the new credit line), folio_id (text),
        related_posting_id (text, the breakfast charge offset), amount (number, USD to 2 decimal places, the
        credit booked), business_date (text, YYYY-MM-DD, the breakfast's morning), balance_due (number, USD to
        2 decimal places, the folio balance after the credit) and status ("posted" when the credit stands).
    """
    folios = ctx.find("folio_accounts", folio_id=folio_id)
    folio = folios[0] if folios else {}
    lines = ctx.find("folio_postings", posting_id=related_posting_id)
    line = lines[0] if lines else {}
    amount = round(float(credit_amount) + 1e-9, 2)
    rid = ctx.make_id("fpo_", folio_id, loyalty_member_id, related_posting_id, amount)
    ctx.create("folio_postings", rid, posting_id=rid, folio_id=folio_id,
               customer_id=folio.get("customer_id", ""), event_type="folio_breakfast_benefit_credit",
               charge_code="elite_breakfast_credit", amount=amount,
               business_date=line.get("business_date", ""), posted_date=ctx.now()[:10],
               posting_sequence=0, related_posting_id=related_posting_id,
               adjustment_reason="elite_benefit_not_applied")
    balance = round(float(folio.get("balance_due") or 0) - amount, 2)
    ctx.update("folio_accounts", folio_id, balance_due=balance)
    return str({"posting_id": rid, "folio_id": folio_id, "related_posting_id": related_posting_id,
                "amount": amount, "business_date": line.get("business_date", ""),
                "balance_due": balance, "status": "posted"})


@tool(owner="user", rw="write")
def apply_dining_allowance_ccaea779(ctx: ToolContext, folio_id: str, loyalty_member_id: str,
                                    related_posting_id: str, carry_amount: float) -> str:
    """The Ashbury Rewards member applies, in person, the unused part of their daily elite dining allowance
    to one food and beverage charge on the open folio of their current stay. One call books one elite
    dining credit line in the member's own name that names the food and beverage charge it offsets, dated
    to that charge's business day, and lowers the folio balance by the amount applied. The member sees the
    credit printed under that charge on the bill.

    Args:
        folio_id: Id class — the reference number of the guest folio of the stay, as given by the desk.
        loyalty_member_id: Id class — the reference number of the member's Ashbury Rewards membership, as
            given by the desk.
        related_posting_id: Id class — the reference number of the food and beverage charge line the member
            applies the allowance to, as given by the desk.
        carry_amount: Fixed-format class — the allowance applied, in USD, 2 decimal places, always positive
            (rounded half up to the cent before booking).

    Returns:
        A dictionary receipt: posting_id (text, reference number of the new credit line), folio_id (text),
        related_posting_id (text, the charge offset), amount (number, USD to 2 decimal places, the allowance
        applied), business_date (text, YYYY-MM-DD, the charge's business day), balance_due (number, USD to 2
        decimal places, the folio balance afterwards) and status ("applied" when the credit stands).
    """
    folios = ctx.find("folio_accounts", folio_id=folio_id)
    folio = folios[0] if folios else {}
    lines = ctx.find("folio_postings", posting_id=related_posting_id)
    line = lines[0] if lines else {}
    amount = round(float(carry_amount) + 1e-9, 2)
    rid = ctx.make_id("fpo_", folio_id, loyalty_member_id, related_posting_id, amount)
    ctx.create("folio_postings", rid, posting_id=rid, folio_id=folio_id,
               customer_id=folio.get("customer_id", ""), event_type="folio_breakfast_benefit_credit",
               charge_code="elite_breakfast_credit", amount=amount,
               business_date=line.get("business_date", ""), posted_date=ctx.now()[:10],
               posting_sequence=0, related_posting_id=related_posting_id,
               adjustment_reason="not_applicable")
    balance = round(float(folio.get("balance_due") or 0) - amount, 2)
    ctx.update("folio_accounts", folio_id, balance_due=balance)
    return str({"posting_id": rid, "folio_id": folio_id, "related_posting_id": related_posting_id,
                "amount": amount, "business_date": line.get("business_date", ""),
                "balance_due": balance, "status": "applied"})


@tool(owner="agent", rw="write")
def correct_self_parking_29958fbc(ctx: ToolContext, folio_id: str, customer_id: str,
                                  related_posting_id: str, savings_amount: float) -> str:
    """Guest services posts, on an open guest folio, the Ashbury Rewards parking savings the stay's
    self-parking charges are owed, as one correction against one self-parking charge line. One call books
    one adjustment line that names that self-parking charge, carries its charge code and business date,
    is recorded as posted by guest services today with the reason that the elite benefit was not applied,
    and lowers the folio balance by the amount taken off. The guest sees the correction printed under that
    parking charge on the bill.

    Args:
        folio_id: Id class — the reference number of the guest folio of the stay, read from the folio lookup.
        customer_id: Id class — the reference number of the guest's profile, read from the profile lookup.
        related_posting_id: Id class — the reference number of the self-parking charge line the correction
            is posted against, read from the folio line lookup.
        savings_amount: Fixed-format class — the amount taken off, in USD, 2 decimal places, always positive
            (rounded half up to the cent before booking).

    Returns:
        A dictionary receipt: posting_id (text, reference number of the new correction line), folio_id (text),
        related_posting_id (text, the parking charge corrected), charge_code (text, the corrected line's
        code), amount (number, USD to 2 decimal places, the amount taken off), balance_due (number, USD to 2
        decimal places, the folio balance afterwards) and status ("posted" when the correction stands).
    """
    folios = ctx.find("folio_accounts", folio_id=folio_id)
    folio = folios[0] if folios else {}
    lines = ctx.find("folio_postings", posting_id=related_posting_id)
    line = lines[0] if lines else {}
    amount = round(float(savings_amount) + 1e-9, 2)
    rid = ctx.make_id("fpo_", folio_id, customer_id, related_posting_id, amount)
    ctx.create("folio_postings", rid, posting_id=rid, folio_id=folio_id, customer_id=customer_id,
               event_type="folio_adjustment", charge_code=line.get("charge_code", ""), amount=amount,
               business_date=line.get("business_date", ""), posted_date=ctx.now()[:10],
               posting_sequence=0, related_posting_id=related_posting_id,
               adjustment_reason="elite_benefit_not_applied")
    balance = round(float(folio.get("balance_due") or 0) - amount, 2)
    ctx.update("folio_accounts", folio_id, balance_due=balance)
    return str({"posting_id": rid, "folio_id": folio_id, "related_posting_id": related_posting_id,
                "charge_code": line.get("charge_code", ""), "amount": amount, "balance_due": balance,
                "status": "posted"})


@tool(owner="agent", rw="write")
def correct_valet_parking_0a0ec721(ctx: ToolContext, folio_id: str, customer_id: str,
                                   related_posting_id: str, savings_amount: float) -> str:
    """Guest services posts, on an open guest folio, the Ashbury Rewards valet savings the stay's valet
    parking charges are owed, as one correction against one valet parking charge line. One call books one
    adjustment line that names that valet charge, carries its charge code and business date, is recorded
    as posted by guest services today with the reason that the elite benefit was not applied, and lowers
    the folio balance by the amount taken off. The guest sees the correction printed under that valet
    charge on the bill.

    Args:
        folio_id: Id class — the reference number of the guest folio of the stay, read from the folio lookup.
        customer_id: Id class — the reference number of the guest's profile, read from the profile lookup.
        related_posting_id: Id class — the reference number of the valet parking charge line the correction
            is posted against, read from the folio line lookup.
        savings_amount: Fixed-format class — the amount taken off, in USD, 2 decimal places, always positive
            (rounded half up to the cent before booking).

    Returns:
        A dictionary receipt: posting_id (text, reference number of the new correction line), folio_id (text),
        related_posting_id (text, the valet charge corrected), charge_code (text, the corrected line's code),
        amount (number, USD to 2 decimal places, the amount taken off), balance_due (number, USD to 2
        decimal places, the folio balance afterwards) and status ("posted" when the correction stands).
    """
    folios = ctx.find("folio_accounts", folio_id=folio_id)
    folio = folios[0] if folios else {}
    lines = ctx.find("folio_postings", posting_id=related_posting_id)
    line = lines[0] if lines else {}
    amount = round(float(savings_amount) + 1e-9, 2)
    rid = ctx.make_id("fpo_", folio_id, customer_id, related_posting_id, amount)
    ctx.create("folio_postings", rid, posting_id=rid, folio_id=folio_id, customer_id=customer_id,
               event_type="folio_adjustment", charge_code=line.get("charge_code", ""), amount=amount,
               business_date=line.get("business_date", ""), posted_date=ctx.now()[:10],
               posting_sequence=0, related_posting_id=related_posting_id,
               adjustment_reason="elite_benefit_not_applied")
    balance = round(float(folio.get("balance_due") or 0) - amount, 2)
    ctx.update("folio_accounts", folio_id, balance_due=balance)
    return str({"posting_id": rid, "folio_id": folio_id, "related_posting_id": related_posting_id,
                "charge_code": line.get("charge_code", ""), "amount": amount, "balance_due": balance,
                "status": "posted"})


@tool(owner="user", rw="write")
def elect_weekly_parking_5ade5692(ctx: ToolContext, folio_id: str, customer_id: str,
                                  related_posting_id: str, excess_amount: float) -> str:
    """The guest elects, in person, the weekly parking maximum for the parking of their current stay, and
    the parking charged above that maximum is taken off one parking charge line of the open folio. One
    call books one adjustment line in the guest's own election that names that parking charge, carries its
    charge code and business date, is recorded with the reason that the stay's parking was charged above
    the applicable rate, and lowers the folio balance by the amount taken off. The guest sees the
    correction printed under that parking charge on the bill.

    Args:
        folio_id: Id class — the reference number of the guest folio of the stay, as given by the desk.
        customer_id: Id class — the reference number of the guest's profile, as given by the desk.
        related_posting_id: Id class — the reference number of the parking charge line the excess is taken
            off, as given by the desk.
        excess_amount: Fixed-format class — the parking charged above the weekly maximum, in USD, 2 decimal
            places, always positive (rounded half up to the cent before booking).

    Returns:
        A dictionary receipt: posting_id (text, reference number of the new correction line), folio_id (text),
        related_posting_id (text, the parking charge corrected), charge_code (text, the corrected line's
        code), amount (number, USD to 2 decimal places, the amount taken off), balance_due (number, USD to 2
        decimal places, the folio balance afterwards) and status ("elected" when the correction stands).
    """
    folios = ctx.find("folio_accounts", folio_id=folio_id)
    folio = folios[0] if folios else {}
    lines = ctx.find("folio_postings", posting_id=related_posting_id)
    line = lines[0] if lines else {}
    amount = round(float(excess_amount) + 1e-9, 2)
    rid = ctx.make_id("fpo_", folio_id, customer_id, related_posting_id, amount)
    ctx.create("folio_postings", rid, posting_id=rid, folio_id=folio_id, customer_id=customer_id,
               event_type="folio_adjustment", charge_code=line.get("charge_code", ""), amount=amount,
               business_date=line.get("business_date", ""), posted_date=ctx.now()[:10],
               posting_sequence=0, related_posting_id=related_posting_id,
               adjustment_reason="incorrect_rate")
    balance = round(float(folio.get("balance_due") or 0) - amount, 2)
    ctx.update("folio_accounts", folio_id, balance_due=balance)
    return str({"posting_id": rid, "folio_id": folio_id, "related_posting_id": related_posting_id,
                "charge_code": line.get("charge_code", ""), "amount": amount, "balance_due": balance,
                "status": "elected"})

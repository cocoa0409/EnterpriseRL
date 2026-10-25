"""Hidden task tools for the closing_cost_credits difficulty (Larkspur Home Lending closing cost credits).

Each tool performs one atomic change on one closing cost credit and is reached through the
unlock/call meta-tools by the name an extended policy gives as its target_tool.
"""

from erlbench import ToolContext, tool


@tool(owner="user", rw="write")
def certify_grant_occupancy_149507f1(ctx: ToolContext, credit_award_id: str, award_amount: float) -> str:
    """The borrower signs, in their own name, the twelve-month owner-occupancy certification for a reserved Neighborhood Access Grant, and the certification states the grant amount being awarded. Signing moves the grant from reserved to verified, records today's date as the verification date, fixes the award amount on the grant at the figure stated, books one award entry for that amount on the grant's ledger and raises the grant's available balance by the same amount. On success the borrower and the desk can see the grant as verified with its award amount and available balance, and the new award entry on the ledger. The call succeeds when the receipt below is returned.

    Args:
        credit_award_id: Id class — reference number of the borrower's reserved closing cost credit (the grant) being certified, as shown by the closing credit lookup for the borrower's loan file.
        award_amount: Fixed-format class — grant amount stated on the certification, in US dollars as a plain number with exactly 2 decimal places (cents), no currency sign or thousands separators; the value is stored as given, rounded to 2 decimal places.

    Returns:
        A one-line confirmation string: "Certification signed: credit <credit_award_id> verified on <YYYY-MM-DD> with award <amount>; award entry <entry_id> booked; available balance <balance>." where <YYYY-MM-DD> is the verification date, <amount> and <balance> are US dollars with 2 decimals and <entry_id> is the reference number of the award entry on the grant's ledger. Receiving this line means the grant is verified and the award is available to apply.
    """
    amount = round(float(award_amount), 2)
    stamp_day = ctx.now()[:10]
    rows = ctx.find("closing_credits", credit_award_id=credit_award_id)
    prior = float(rows[0].get("credit_balance") or 0) if rows else 0.0
    balance = round(prior + amount, 2)
    entry_id = ctx.make_id("cle_", credit_award_id, amount, "award")
    ctx.update("closing_credits", credit_award_id, status="verified", verified_date=stamp_day,
               award_amount=amount, credit_balance=balance)
    ctx.create("credit_ledger", entry_id, credit_entry_id=entry_id, credit_award_id=credit_award_id,
               customer_id=(rows[0].get("customer_id") if rows else ""), event_type="credit_award_booked",
               entry_amount=amount, entry_date=stamp_day, cost_category="none", disclosure_id="",
               reduction_reason="none", source_entry_id="")
    return (f"Certification signed: credit {credit_award_id} verified on {stamp_day} with award {amount:.2f}; "
            f"award entry {entry_id} booked; available balance {balance:.2f}.")


@tool(owner="agent", rw="write")
def post_down_payment_credit_64b83335(ctx: ToolContext, credit_award_id: str, disclosure_id: str,
                                     source_entry_id: str, entry_amount: float) -> str:
    """Book the part of a verified closing cost credit that pays the borrower's down payment on a Closing Disclosure. One call books one application entry for the down payment cost category against the named Closing Disclosure, drawing on the named award entry of the same credit, and lowers the credit's available balance by the amount booked. On success the credit's ledger shows the down payment application entry and the reduced available balance. The call succeeds when the receipt below is returned.

    Args:
        credit_award_id: Id class — reference number of the verified closing cost credit being applied, as shown by the closing credit lookup for the loan file.
        disclosure_id: Id class — reference number of the Closing Disclosure the down payment is paid on, as shown by the loan disclosure lookup for the same loan file.
        source_entry_id: Id class — reference number of the award entry on this credit's ledger that the application draws on, as shown by the credit ledger lookup for the credit.
        entry_amount: Fixed-format class — amount of the credit applied to the down payment, in US dollars as a plain positive number with exactly 2 decimal places (cents), no currency sign or thousands separators; stored as given, rounded to 2 decimal places.

    Returns:
        A one-line confirmation string: "Down payment application <entry_id> booked: <amount> of credit <credit_award_id> on disclosure <disclosure_id>; available balance <balance>." where <entry_id> is the reference number of the new application entry and <amount> and <balance> are US dollars with 2 decimals. Receiving this line means the application is on the credit's ledger.
    """
    amount = round(float(entry_amount), 2)
    stamp_day = ctx.now()[:10]
    rows = ctx.find("closing_credits", credit_award_id=credit_award_id)
    prior = float(rows[0].get("credit_balance") or 0) if rows else 0.0
    balance = round(prior - amount, 2)
    entry_id = ctx.make_id("cle_", credit_award_id, disclosure_id, source_entry_id, amount, "down_payment")
    ctx.create("credit_ledger", entry_id, credit_entry_id=entry_id, credit_award_id=credit_award_id,
               customer_id=(rows[0].get("customer_id") if rows else ""), event_type="credit_applied_at_closing",
               entry_amount=amount, entry_date=stamp_day, cost_category="down_payment", disclosure_id=disclosure_id,
               reduction_reason="none", source_entry_id=source_entry_id)
    ctx.update("closing_credits", credit_award_id, credit_balance=balance)
    return (f"Down payment application {entry_id} booked: {amount:.2f} of credit {credit_award_id} on disclosure "
            f"{disclosure_id}; available balance {balance:.2f}.")


@tool(owner="agent", rw="write")
def post_closing_cost_credit_e81a44da(ctx: ToolContext, credit_award_id: str, disclosure_id: str,
                                     source_entry_id: str, entry_amount: float) -> str:
    """Book the part of a verified closing cost credit that pays the borrower's nonrecurring closing costs on a Closing Disclosure. One call books one application entry for the nonrecurring closing costs category against the named Closing Disclosure, drawing on the named award entry of the same credit, and lowers the credit's available balance by the amount booked. On success the credit's ledger shows the closing cost application entry and the reduced available balance. The call succeeds when the receipt below is returned.

    Args:
        credit_award_id: Id class — reference number of the verified closing cost credit being applied, as shown by the closing credit lookup for the loan file.
        disclosure_id: Id class — reference number of the Closing Disclosure whose nonrecurring closing costs are paid, as shown by the loan disclosure lookup for the same loan file.
        source_entry_id: Id class — reference number of the award entry on this credit's ledger that the application draws on, as shown by the credit ledger lookup for the credit.
        entry_amount: Fixed-format class — amount of the credit applied to nonrecurring closing costs, in US dollars as a plain positive number with exactly 2 decimal places (cents), no currency sign or thousands separators; stored as given, rounded to 2 decimal places.

    Returns:
        A one-line confirmation string: "Closing cost application <entry_id> booked: <amount> of credit <credit_award_id> on disclosure <disclosure_id>; available balance <balance>." where <entry_id> is the reference number of the new application entry and <amount> and <balance> are US dollars with 2 decimals. Receiving this line means the application is on the credit's ledger.
    """
    amount = round(float(entry_amount), 2)
    stamp_day = ctx.now()[:10]
    rows = ctx.find("closing_credits", credit_award_id=credit_award_id)
    prior = float(rows[0].get("credit_balance") or 0) if rows else 0.0
    balance = round(prior - amount, 2)
    entry_id = ctx.make_id("cle_", credit_award_id, disclosure_id, source_entry_id, amount, "nonrecurring")
    ctx.create("credit_ledger", entry_id, credit_entry_id=entry_id, credit_award_id=credit_award_id,
               customer_id=(rows[0].get("customer_id") if rows else ""), event_type="credit_applied_at_closing",
               entry_amount=amount, entry_date=stamp_day, cost_category="nonrecurring_closing_costs",
               disclosure_id=disclosure_id, reduction_reason="none", source_entry_id=source_entry_id)
    ctx.update("closing_credits", credit_award_id, credit_balance=balance)
    return (f"Closing cost application {entry_id} booked: {amount:.2f} of credit {credit_award_id} on disclosure "
            f"{disclosure_id}; available balance {balance:.2f}.")


class _CalendarDays:
    """Pure calendar arithmetic on YYYY-MM-DD strings (proleptic Gregorian ordinal days)."""

    @staticmethod
    def to_ordinal(day: str) -> int:
        y, m, d = (int(p) for p in str(day)[:10].split("-"))
        cum = [0, 31, 59, 90, 120, 151, 181, 212, 243, 273, 304, 334]
        leap = (y % 4 == 0 and y % 100 != 0) or y % 400 == 0
        yy = y - 1
        return yy * 365 + yy // 4 - yy // 100 + yy // 400 + cum[m - 1] + (1 if leap and m > 2 else 0) + d

    @staticmethod
    def from_ordinal(n: int) -> str:
        y = (n * 400) // 146097 + 1
        while _CalendarDays.to_ordinal(f"{y:04d}-01-01") > n:
            y -= 1
        while _CalendarDays.to_ordinal(f"{y + 1:04d}-01-01") <= n:
            y += 1
        m = 1
        while m < 12 and _CalendarDays.to_ordinal(f"{y:04d}-{m + 1:02d}-01") <= n:
            m += 1
        d = n - _CalendarDays.to_ordinal(f"{y:04d}-{m:02d}-01") + 1
        return f"{y:04d}-{m:02d}-{d:02d}"


@tool(owner="user", rw="write")
def recertify_hero_occupation_0487fd94(ctx: ToolContext, credit_award_id: str, basis_loan_amount: float,
                                       award_increase: float) -> str:
    """The borrower re-certifies, in their own name, the qualifying occupation on a verified Hometown Heroes Credit whose loan file has been re-tested, and the re-certification states the base loan amount the award is now fixed on and the amount by which the award rises. Signing records today's date as the credit's verification date and the stated base loan amount as the credit's basis, books one further award entry for the stated increase on the credit's ledger and raises the credit's available balance by the same amount; the credit stays verified. On success the borrower and the desk can see the new verification date and basis on the credit and the further award entry on its ledger. The call succeeds when the receipt below is returned.

    Args:
        credit_award_id: Id class — reference number of the borrower's verified Hometown Heroes Credit being re-certified, as shown by the closing credit lookup for the borrower's loan file.
        basis_loan_amount: Fixed-format class — base loan amount the re-certified award is fixed on, in US dollars as a plain number with exactly 2 decimal places (cents), no currency sign or thousands separators; stored as given, rounded to 2 decimal places.
        award_increase: Fixed-format class — amount by which the award rises on re-certification, in US dollars as a plain positive number with exactly 2 decimal places (cents), no currency sign or thousands separators; stored as given, rounded to 2 decimal places.

    Returns:
        A one-line confirmation string: "Occupation re-certified: credit <credit_award_id> re-verified on <YYYY-MM-DD> on basis <basis>; award entry <entry_id> of <amount> booked; available balance <balance>." where <YYYY-MM-DD> is the re-verification date, <basis>, <amount> and <balance> are US dollars with 2 decimals and <entry_id> is the reference number of the further award entry. Receiving this line means the re-certification is recorded and the increase is available.
    """
    basis = round(float(basis_loan_amount), 2)
    amount = round(float(award_increase), 2)
    stamp_day = ctx.now()[:10]
    rows = ctx.find("closing_credits", credit_award_id=credit_award_id)
    prior = float(rows[0].get("credit_balance") or 0) if rows else 0.0
    balance = round(prior + amount, 2)
    entry_id = ctx.make_id("cle_", credit_award_id, basis, amount, "recertified_award")
    ctx.update("closing_credits", credit_award_id, verified_date=stamp_day, basis_loan_amount=basis,
               credit_balance=balance)
    ctx.create("credit_ledger", entry_id, credit_entry_id=entry_id, credit_award_id=credit_award_id,
               customer_id=(rows[0].get("customer_id") if rows else ""), event_type="credit_award_booked",
               entry_amount=amount, entry_date=stamp_day, cost_category="none", disclosure_id="",
               reduction_reason="none", source_entry_id="")
    return (f"Occupation re-certified: credit {credit_award_id} re-verified on {stamp_day} on basis {basis:.2f}; "
            f"award entry {entry_id} of {amount:.2f} booked; available balance {balance:.2f}.")


@tool(owner="agent", rw="write")
def extend_credit_validity_45c9966f(ctx: ToolContext, credit_award_id: str, extension_days: int) -> str:
    """Grant one validity extension on a closing cost credit that has not yet been applied. One call adds the stated number of calendar days to the credit's current expiration date, records the new expiration date on the credit and raises the credit's count of granted extensions by one; nothing else on the credit or its ledger changes. On success the desk and the borrower can see the later expiration date and the higher extension count on the credit. The call succeeds when the receipt below is returned.

    Args:
        credit_award_id: Id class — reference number of the closing cost credit whose validity is extended, as shown by the closing credit lookup for the loan file.
        extension_days: Fixed-format class — number of calendar days added to the current expiration date, a whole positive integer count of days with no decimals, no unit text and no sign; the new expiration date is the current expiration date plus this many calendar days.

    Returns:
        A one-line confirmation string: "Validity extended: credit <credit_award_id> now expires <YYYY-MM-DD> (was <YYYY-MM-DD>); extensions granted <count>." where the dates are calendar dates in YYYY-MM-DD and <count> is the new whole-number extension count. Receiving this line means the new expiration date is in force.
    """
    days = int(extension_days)
    rows = ctx.find("closing_credits", credit_award_id=credit_award_id)
    current = str(rows[0].get("expiration_date") or ctx.now()[:10]) if rows else ctx.now()[:10]
    count = int(rows[0].get("extension_count") or 0) + 1 if rows else 1
    new_date = _CalendarDays.from_ordinal(_CalendarDays.to_ordinal(current) + days)
    ctx.update("closing_credits", credit_award_id, expiration_date=new_date, extension_count=count)
    return (f"Validity extended: credit {credit_award_id} now expires {new_date} (was {current}); "
            f"extensions granted {count}.")


@tool(owner="agent", rw="write")
def reduce_unusable_credit_facd0be5(ctx: ToolContext, credit_award_id: str, source_entry_id: str,
                                   entry_amount: float) -> str:
    """Book a reduction that takes off a verified closing cost credit the part of its balance the borrower's eligible costs cannot use. One call books one reduction entry with the reason that the credit exceeds the eligible costs, drawing on the named award entry of the same credit, and lowers the credit's available balance by the amount reduced; the reduced amount is never paid to the borrower. On success the credit's ledger shows the reduction entry and the lower available balance. The call succeeds when the receipt below is returned.

    Args:
        credit_award_id: Id class — reference number of the verified closing cost credit being reduced, as shown by the closing credit lookup for the loan file.
        source_entry_id: Id class — reference number of the award entry on this credit's ledger that the reduction draws on, as shown by the credit ledger lookup for the credit.
        entry_amount: Fixed-format class — amount taken off the credit, in US dollars as a plain positive number with exactly 2 decimal places (cents), no currency sign or thousands separators; stored as given, rounded to 2 decimal places.

    Returns:
        A one-line confirmation string: "Reduction <entry_id> booked: <amount> taken off credit <credit_award_id> as exceeding eligible costs; available balance <balance>." where <entry_id> is the reference number of the new reduction entry and <amount> and <balance> are US dollars with 2 decimals. Receiving this line means the reduction is on the credit's ledger.
    """
    amount = round(float(entry_amount), 2)
    stamp_day = ctx.now()[:10]
    rows = ctx.find("closing_credits", credit_award_id=credit_award_id)
    prior = float(rows[0].get("credit_balance") or 0) if rows else 0.0
    balance = round(prior - amount, 2)
    entry_id = ctx.make_id("cle_", credit_award_id, source_entry_id, amount, "exceeds_eligible_costs")
    ctx.create("credit_ledger", entry_id, credit_entry_id=entry_id, credit_award_id=credit_award_id,
               customer_id=(rows[0].get("customer_id") if rows else ""), event_type="credit_reduced",
               entry_amount=amount, entry_date=stamp_day, cost_category="none", disclosure_id="",
               reduction_reason="exceeds_eligible_costs", source_entry_id=source_entry_id)
    ctx.update("closing_credits", credit_award_id, credit_balance=balance)
    return (f"Reduction {entry_id} booked: {amount:.2f} taken off credit {credit_award_id} as exceeding eligible costs; "
            f"available balance {balance:.2f}.")

"""Hidden task tools for the balloon_maturity_and_title difficulty of env_0066_captive_auto_finance_company.

Each tool performs one atomic write on a Kestrel Advantage Balloon Retail Installment Sale Contract and
takes every computed value as an argument; no tool evaluates policy, eligibility or prerequisites.
"""

from erlbench import ToolContext, tool


class _Posting:
    """Value helpers only; every write happens in the tool bodies."""

    @staticmethod
    def contract(ctx: ToolContext, balloon_contract_id: str) -> dict:
        rows = ctx.find("balloon_contracts", balloon_contract_id=balloon_contract_id)
        return rows[0] if rows else {}

    @staticmethod
    def add_months(iso_date: str, months: int) -> str:
        y, m, d = (int(x) for x in iso_date[:10].split("-"))
        total = (y * 12 + (m - 1)) + int(months)
        ny, nm = divmod(total, 12)
        mdays = [31, 29 if (ny % 4 == 0 and (ny % 100 != 0 or ny % 400 == 0)) else 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
        return f"{ny:04d}-{nm + 1:02d}-{min(d, mdays[nm]):02d}"


@tool(owner="agent", rw="write")
def bill_excess_mileage_charge_7a491561(ctx: ToolContext, balloon_contract_id: str, amount: float) -> str:
    """Bill the excess mileage charge on a Kestrel Advantage balloon contract whose vehicle came back under the
    return option. One call books one return charge entry of type excess_mileage_charge, dated today, for the
    amount given, and adds that amount to the contract's fees due; the charge shows in the contract's
    posting history and in its fees due balance.

    Args:
        balloon_contract_id: Id class — the reference number of the balloon contract being billed, as returned by the balloon contract lookup for the verified customer.
        amount: Fixed-format class — the excess mileage charge to bill, in USD, a decimal number with 2 decimal places (cents), already rounded to the cent; no currency symbol; booked exactly as given.

    Returns:
        A confirmation sentence (string) stating the new charge entry reference (an id string), the charge type
        excess_mileage_charge, the amount billed in USD with 2 decimal places, the billing date in YYYY-MM-DD form
        and the contract's fees due balance in USD with 2 decimal places including the charge; receiving it means the
        charge is booked.
    """
    rec = _Posting.contract(ctx, balloon_contract_id)
    amt = round(float(amount), 2)
    rid = ctx.make_id("brc_", balloon_contract_id, "excess_mileage_charge", amt)
    ctx.create("balloon_transactions", rid, balloon_txn_id=rid, balloon_contract_id=balloon_contract_id,
               customer_id=rec.get("customer_id", ""), event_type="balloon_return_charge", txn_date=ctx.now()[:10],
               amount=amt, fee_type="excess_mileage_charge", payment_channel="not_applicable", payment_purpose="not_applicable")
    new_fees = round(float(rec.get("fees_due_balance") or 0) + amt, 2)
    ctx.update("balloon_contracts", balloon_contract_id, fees_due_balance=new_fees)
    return (f"Excess mileage charge booked: entry {rid}, type excess_mileage_charge, amount {amt:.2f} USD, "
            f"billed {ctx.now()[:10]}; fees due on contract {balloon_contract_id} now {new_fees:.2f} USD.")


@tool(owner="agent", rw="write")
def bill_excess_wear_charge_ce1b5dd4(ctx: ToolContext, balloon_contract_id: str, amount: float) -> str:
    """Bill the excess wear charge on a Kestrel Advantage balloon contract whose vehicle came back under the
    return option. One call books one return charge entry of type excess_wear_charge, dated today, for the
    amount given, and adds that amount to the contract's fees due; the charge shows in the contract's
    posting history and in its fees due balance.

    Args:
        balloon_contract_id: Id class — the reference number of the balloon contract being billed, as returned by the balloon contract lookup for the verified customer.
        amount: Fixed-format class — the excess wear charge to bill, in USD, a decimal number with 2 decimal places (cents), already rounded to the cent; no currency symbol; booked exactly as given.

    Returns:
        A confirmation sentence (string) stating the new charge entry reference (an id string), the charge type
        excess_wear_charge, the amount billed in USD with 2 decimal places, the billing date in YYYY-MM-DD form and
        the contract's fees due balance in USD with 2 decimal places including the charge; receiving it means the
        charge is booked.
    """
    rec = _Posting.contract(ctx, balloon_contract_id)
    amt = round(float(amount), 2)
    rid = ctx.make_id("brc_", balloon_contract_id, "excess_wear_charge", amt)
    ctx.create("balloon_transactions", rid, balloon_txn_id=rid, balloon_contract_id=balloon_contract_id,
               customer_id=rec.get("customer_id", ""), event_type="balloon_return_charge", txn_date=ctx.now()[:10],
               amount=amt, fee_type="excess_wear_charge", payment_channel="not_applicable", payment_purpose="not_applicable")
    new_fees = round(float(rec.get("fees_due_balance") or 0) + amt, 2)
    ctx.update("balloon_contracts", balloon_contract_id, fees_due_balance=new_fees)
    return (f"Excess wear charge booked: entry {rid}, type excess_wear_charge, amount {amt:.2f} USD, "
            f"billed {ctx.now()[:10]}; fees due on contract {balloon_contract_id} now {new_fees:.2f} USD.")


@tool(owner="agent", rw="write")
def bill_return_fee_2252d2f2(ctx: ToolContext, balloon_contract_id: str, amount: float) -> str:
    """Bill the return fee on a Kestrel Advantage balloon contract whose vehicle came back under the return
    option. One call books one return charge entry of type return_fee, dated today, for the amount given, and
    adds that amount to the contract's fees due; the fee shows in the contract's posting history and in
    its fees due balance.

    Args:
        balloon_contract_id: Id class — the reference number of the balloon contract being billed, as returned by the balloon contract lookup for the verified customer.
        amount: Fixed-format class — the return fee to bill, in USD, a decimal number with 2 decimal places (cents), already rounded to the cent; no currency symbol; booked exactly as given.

    Returns:
        A confirmation sentence (string) stating the new charge entry reference (an id string), the charge type
        return_fee, the amount billed in USD with 2 decimal places, the billing date in YYYY-MM-DD form and the
        contract's fees due balance in USD with 2 decimal places including the fee; receiving it means the fee is
        booked.
    """
    rec = _Posting.contract(ctx, balloon_contract_id)
    amt = round(float(amount), 2)
    rid = ctx.make_id("brc_", balloon_contract_id, "return_fee", amt)
    ctx.create("balloon_transactions", rid, balloon_txn_id=rid, balloon_contract_id=balloon_contract_id,
               customer_id=rec.get("customer_id", ""), event_type="balloon_return_charge", txn_date=ctx.now()[:10],
               amount=amt, fee_type="return_fee", payment_channel="not_applicable", payment_purpose="not_applicable")
    new_fees = round(float(rec.get("fees_due_balance") or 0) + amt, 2)
    ctx.update("balloon_contracts", balloon_contract_id, fees_due_balance=new_fees)
    return (f"Return fee booked: entry {rid}, type return_fee, amount {amt:.2f} USD, "
            f"billed {ctx.now()[:10]}; fees due on contract {balloon_contract_id} now {new_fees:.2f} USD.")


@tool(owner="user", rw="write")
def pay_return_balance_installment_2f123e0a(ctx: ToolContext, balloon_contract_id: str, amount: float,
                                            funding_account_last4: str) -> str:
    """The customer pays, through Kestrel's automated phone payment line, a return balance payment on their own
    balloon contract whose vehicle came back under the return option, drawn by ACH from their own bank account.
    One call posts one payment dated today on the phone_ivr_ach channel with purpose installment, applies the
    whole amount to the contract's fees due (books the matching fee payment entry) and lowers the fees due
    balance by that amount; no convenience fee is collected on this channel.

    Args:
        balloon_contract_id: Id class — the reference number of the customer's balloon contract being paid, as read out by the agent from the balloon contract lookup.
        amount: Fixed-format class — the payment amount, in USD, a decimal number with 2 decimal places (cents), already rounded to the cent; no currency symbol; drawn and posted exactly as given.
        funding_account_last4: Fixed-format class — the last four digits of the customer's own bank account the payment is drawn from, in the format 4 digits, or empty (never empty for this payment), exactly as the customer states them.

    Returns:
        A confirmation sentence (string) stating the payment reference (an id string), the amount posted in USD with
        2 decimal places, the posting date in YYYY-MM-DD form, the channel phone_ivr_ach, the last four digits of the
        bank account drawn, and the contract's remaining fees due in USD with 2 decimal places; receiving it means
        the payment is posted.
    """
    rec = _Posting.contract(ctx, balloon_contract_id)
    amt = round(float(amount), 2)
    today = ctx.now()[:10]
    pid = ctx.make_id("bpy_", balloon_contract_id, amt, funding_account_last4)
    ctx.create("balloon_transactions", pid, balloon_txn_id=pid, balloon_contract_id=balloon_contract_id,
               customer_id=rec.get("customer_id", ""), event_type="balloon_payment", txn_date=today, amount=amt,
               payment_channel="phone_ivr_ach", funding_account_last4=str(funding_account_last4),
               payment_purpose="installment", interest_applied=0.0, principal_applied=0.0, fees_applied=amt,
               convenience_fee=0.0, fee_type="not_applicable")
    fid = ctx.make_id("bfp_", pid)
    ctx.create("balloon_transactions", fid, balloon_txn_id=fid, balloon_contract_id=balloon_contract_id,
               customer_id=rec.get("customer_id", ""), event_type="balloon_fee_payment", txn_date=today, amount=amt,
               payment_txn_id=pid, payment_channel="not_applicable", payment_purpose="not_applicable")
    left = round(float(rec.get("fees_due_balance") or 0) - amt, 2)
    ctx.update("balloon_contracts", balloon_contract_id, fees_due_balance=left, last_payment_date=today)
    return (f"Payment posted: reference {pid}, amount {amt:.2f} USD, posted {today}, channel phone_ivr_ach, "
            f"account ending {funding_account_last4}; fees due remaining on contract {balloon_contract_id} {left:.2f} USD.")


@tool(owner="agent", rw="write")
def issue_payoff_quote_72ecc9f3(ctx: ToolContext, balloon_contract_id: str, quote_good_through_date: str,
                                per_diem: float, amount: float) -> str:
    """Issue a customer payoff quote on a Kestrel Advantage balloon contract. One call books one payoff quote
    entry dated today, with purpose customer_payoff, recording the payoff amount, the good-through date and the
    per diem given; the contract's balances are not changed. The quote shows in the contract's posting
    history, where it can be read back.

    Args:
        balloon_contract_id: Id class — the reference number of the balloon contract being quoted, as returned by the balloon contract lookup for the verified customer.
        quote_good_through_date: Fixed-format class — the last date on which the quoted amount is honoured, in YYYY-MM-DD form (calendar date, no time zone).
        per_diem: Fixed-format class — the per diem the quote states, that is the daily simple interest at the contract's own APR, in USD, a decimal number with 2 decimal places (cents), already rounded to the cent; no currency symbol.
        amount: Fixed-format class — the payoff amount as of the good-through date, in USD, a decimal number with 2 decimal places (cents), already rounded to the cent; no currency symbol.

    Returns:
        A confirmation sentence (string) stating the quote entry reference (an id string), the quote date in
        YYYY-MM-DD form, the purpose customer_payoff, the payoff amount in USD with 2 decimal places, the
        good-through date in YYYY-MM-DD form and the per diem in USD with 2 decimal places; receiving it means the
        quote is on file.
    """
    rec = _Posting.contract(ctx, balloon_contract_id)
    amt = round(float(amount), 2)
    pdm = round(float(per_diem), 2)
    today = ctx.now()[:10]
    qid = ctx.make_id("bpq_", balloon_contract_id, quote_good_through_date, pdm, amt)
    ctx.create("balloon_transactions", qid, balloon_txn_id=qid, balloon_contract_id=balloon_contract_id,
               customer_id=rec.get("customer_id", ""), event_type="balloon_payoff_quote", txn_date=today, amount=amt,
               quote_good_through_date=str(quote_good_through_date)[:10], per_diem=pdm, quote_purpose="customer_payoff",
               payment_channel="not_applicable", payment_purpose="not_applicable")
    return (f"Payoff quote issued: entry {qid}, dated {today}, purpose customer_payoff, payoff {amt:.2f} USD "
            f"good through {str(quote_good_through_date)[:10]}, per diem {pdm:.2f} USD.")


@tool(owner="user", rw="write")
def pay_refinance_precondition_amount_08a17076(ctx: ToolContext, balloon_contract_id: str, amount: float,
                                               funding_account_last4: str) -> str:
    """The customer pays, through Kestrel's automated phone payment line, an amount on their own Kestrel
    Advantage balloon contract that is held on the contract unapplied, drawn by ACH from their own bank account.
    One call posts one payment dated today on the phone_ivr_ach channel with purpose installment; nothing is
    applied to interest, principal or fees (each applied portion is recorded as 0.00) and the contract's last
    payment date becomes today; no convenience fee is collected on this channel.

    Args:
        balloon_contract_id: Id class — the reference number of the customer's balloon contract being paid, as read out by the agent from the balloon contract lookup.
        amount: Fixed-format class — the payment amount, in USD, a decimal number with 2 decimal places (cents), already rounded to the cent; no currency symbol; drawn and posted exactly as given.
        funding_account_last4: Fixed-format class — the last four digits of the customer's own bank account the payment is drawn from, in the format 4 digits, or empty (never empty for this payment), exactly as the customer states them.

    Returns:
        A confirmation sentence (string) stating the payment reference (an id string), the amount posted in USD with
        2 decimal places, the posting date in YYYY-MM-DD form, the channel phone_ivr_ach, the last four digits of the
        bank account drawn, and that the funds are held on the contract unapplied; receiving it means the payment is
        posted.
    """
    rec = _Posting.contract(ctx, balloon_contract_id)
    amt = round(float(amount), 2)
    today = ctx.now()[:10]
    pid = ctx.make_id("bph_", balloon_contract_id, amt, funding_account_last4)
    ctx.create("balloon_transactions", pid, balloon_txn_id=pid, balloon_contract_id=balloon_contract_id,
               customer_id=rec.get("customer_id", ""), event_type="balloon_payment", txn_date=today, amount=amt,
               payment_channel="phone_ivr_ach", funding_account_last4=str(funding_account_last4),
               payment_purpose="installment", interest_applied=0.0, principal_applied=0.0, fees_applied=0.0,
               convenience_fee=0.0, fee_type="not_applicable")
    ctx.update("balloon_contracts", balloon_contract_id, last_payment_date=today)
    return (f"Payment posted: reference {pid}, amount {amt:.2f} USD, posted {today}, channel phone_ivr_ach, "
            f"account ending {funding_account_last4}; funds held on contract {balloon_contract_id} unapplied.")


@tool(owner="agent", rw="write")
def complete_balloon_refinance_14b47e8c(ctx: ToolContext, balloon_contract_id: str, amount: float,
                                        refinance_term_months: int, refinance_apr: float,
                                        refinance_monthly_payment: float) -> str:
    """Book the refinance of the balloon on a Kestrel Advantage balloon contract. One call books one balloon
    refinance entry dated today and re-amortizes the contract: principal_balance becomes the amount refinanced,
    interest is paid to today, any fees due are cleared (booked as one fee payment entry for the fees standing,
    linked to the most recent payment dated today when there is one) so fees due become 0.00, apr and
    monthly_payment are replaced by the refinance APR and installment,
    balloon_amount becomes 0.00, refinance_date becomes today, the elected maturity option is recorded as
    refinance, nothing is past due, the next installment falls due one month from today and maturity_date moves
    to today plus the refinance term in months.

    Args:
        balloon_contract_id: Id class — the reference number of the balloon contract being refinanced, as returned by the balloon contract lookup for the verified customer.
        amount: Fixed-format class — the amount refinanced, in USD, a decimal number with 2 decimal places (cents), already rounded to the cent; no currency symbol.
        refinance_term_months: Fixed-format class — the refinance term as a whole number of monthly installments (an integer, months).
        refinance_apr: Fixed-format class — the refinance annual percentage rate, in percent, a decimal number with 2 decimal places written without the % sign.
        refinance_monthly_payment: Fixed-format class — the new level monthly installment, in USD, a decimal number with 2 decimal places (cents), already rounded to the cent; no currency symbol.

    Returns:
        A confirmation sentence (string) stating the refinance entry reference (an id string), the amount refinanced
        in USD with 2 decimal places, the term in months (integer), the APR in percent with 2 decimal places, the
        monthly installment in USD with 2 decimal places, the fees cleared in USD with 2 decimal places, the next due
        date and the new maturity date in YYYY-MM-DD form; receiving it means the refinance is booked.
    """
    amt = round(float(amount), 2)
    term = int(refinance_term_months)
    apr = round(float(refinance_apr), 2)
    pay = round(float(refinance_monthly_payment), 2)
    today = ctx.now()[:10]
    rid = ctx.make_id("brf_", balloon_contract_id, amt, term, apr, pay)
    rec = _Posting.contract(ctx, balloon_contract_id)
    ctx.create("balloon_transactions", rid, balloon_txn_id=rid, balloon_contract_id=balloon_contract_id,
               customer_id=rec.get("customer_id", ""), event_type="balloon_refinance", txn_date=today, amount=amt,
               refinance_term_months=term, refinance_apr=apr, refinance_monthly_payment=pay,
               payment_channel="not_applicable", payment_purpose="not_applicable")
    fees_cleared = round(float(rec.get("fees_due_balance") or 0), 2)
    if fees_cleared:
        paid_today = [r for r in ctx.find("balloon_transactions", balloon_contract_id=balloon_contract_id,
                                          event_type="balloon_payment", txn_date=today)]
        link = paid_today[-1].get("balloon_txn_id", "") if paid_today else ""
        fpid = ctx.make_id("bfp_", rid)
        ctx.create("balloon_transactions", fpid, balloon_txn_id=fpid, balloon_contract_id=balloon_contract_id,
                   customer_id=rec.get("customer_id", ""), event_type="balloon_fee_payment", txn_date=today,
                   amount=fees_cleared, payment_txn_id=link, payment_channel="not_applicable",
                   payment_purpose="not_applicable")
    next_due = _Posting.add_months(today, 1)
    new_maturity = _Posting.add_months(today, term)
    ctx.update("balloon_contracts", balloon_contract_id, principal_balance=amt, fees_due_balance=0.0,
               interest_paid_to_date=today, apr=apr, monthly_payment=pay, balloon_amount=0.0, refinance_date=today,
               maturity_option_elected="refinance", past_due_amount=0.0, days_past_due=0, next_due_date=next_due,
               maturity_date=new_maturity)
    return (f"Refinance booked: entry {rid}, amount {amt:.2f} USD over {term} months at {apr:.2f}% APR, "
            f"installment {pay:.2f} USD; fees cleared {fees_cleared:.2f} USD; next due {next_due}, maturity {new_maturity}.")

"""Hidden task tools for the home_loan_servicing difficulty of env_0048_manufactured_home_community_operator.

Each tool performs one atomic write on a Hearthstone Home Finance loan record (loan_holdings,
loan_transactions, loan_notices) with values the agent has already worked out from the loan
charter. No tool checks eligibility, ordering or prerequisites, and none computes a policy value.
"""

from erlbench import ToolContext, tool


class _Calendar:
    """Pure calendar arithmetic on 'YYYY-MM-DD' strings (no clock, no randomness)."""

    @staticmethod
    def add_months(day: str, months: int) -> str:
        y, m, d = (int(p) for p in str(day)[:10].split("-"))
        total = (y * 12 + (m - 1)) + int(months)
        ny, nm = total // 12, total % 12 + 1
        leap = ny % 4 == 0 and (ny % 100 != 0 or ny % 400 == 0)
        last = [31, 29 if leap else 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31][nm - 1]
        return f"{ny:04d}-{nm:02d}-{min(d, last):02d}"

    @staticmethod
    def next_due_after(day: str, due_day: int) -> str:
        y, m, d = (int(p) for p in str(day)[:10].split("-"))
        if d < int(due_day):
            return f"{y:04d}-{m:02d}-{int(due_day):02d}"
        return _Calendar.add_months(f"{y:04d}-{m:02d}-{int(due_day):02d}", 1)


@tool(owner="agent", rw="write")
def issue_escrow_analysis_2b6c143e(ctx: ToolContext, loan_id: str, new_monthly_escrow: float,
                                   shortage_amount: float, surplus_amount: float) -> str:
    """Issue the escrow analysis for a Hearthstone Home Finance loan and reset its monthly escrow deposit.

    Records one escrow analysis notice dated today on the loan, stating the shortage or surplus
    found and the new monthly escrow deposit, effective from the first installment that falls due
    after today; at the same moment the loan's current monthly escrow deposit is changed to the new
    amount, so the next installment requested from the borrower includes it. The loan's principal,
    escrow, fee and suspense balances are not moved. Success is the receipt returned with the
    analysis reference.

    Args:
        loan_id: Id class — the loan number of the Hearthstone Home Finance loan being analyzed, as
            returned by the loan lookup for the verified borrower.
        new_monthly_escrow: Fixed-format class — the new monthly escrow deposit in USD, a positive
            amount written with 2 decimal places (rounded half up to the cent).
        shortage_amount: Fixed-format class — the escrow shortage the analysis found, in USD with 2
            decimal places; 0.00 when the analysis finds no shortage.
        surplus_amount: Fixed-format class — the escrow surplus the analysis found, in USD with 2
            decimal places; 0.00 when the analysis finds no surplus.

    Returns:
        A dictionary rendered as text with: status ("issued" on success); loan_notice_id (reference
        of the escrow analysis notice); loan_id; notice_date (YYYY-MM-DD, today); new_monthly_escrow,
        shortage_amount and surplus_amount (USD, 2 decimal places, as recorded); and
        effective_due_date (YYYY-MM-DD, the first installment due date the new deposit applies to).
    """
    today = ctx.now()[:10]
    loan = ctx.find("loan_holdings", loan_id=loan_id)
    due_day = int((loan[0].get("payment_due_day") if loan else 1) or 1)
    effective = _Calendar.next_due_after(today, due_day)
    nid = ctx.make_id("lnt_", loan_id, new_monthly_escrow, shortage_amount, surplus_amount, today)
    new_dep = round(float(new_monthly_escrow), 2)
    ctx.create("loan_notices", nid, loan_notice_id=nid, loan_id=loan_id,
               customer_id=(loan[0].get("customer_id") if loan else ""),
               event_type="loan_escrow_analysis", notice_date=today,
               new_monthly_escrow=new_dep, shortage_amount=round(float(shortage_amount), 2),
               surplus_amount=round(float(surplus_amount), 2), effective_due_date=effective)
    ctx.update("loan_holdings", loan_id, monthly_escrow_amount=new_dep)
    return str({"status": "issued", "loan_notice_id": nid, "loan_id": loan_id, "notice_date": today,
                "new_monthly_escrow": new_dep, "shortage_amount": round(float(shortage_amount), 2),
                "surplus_amount": round(float(surplus_amount), 2), "effective_due_date": effective})


@tool(owner="agent", rw="write")
def assess_returned_payment_fee_86f751f1(ctx: ToolContext, loan_id: str, source_txn_id: str,
                                         amount: float) -> str:
    """Charge the returned-payment fee on a Hearthstone Home Finance loan for one payment the bank returned.

    Books one returned-payment fee dated today against the returned payment it is charged for and
    adds the fee to the fees the borrower owes on the loan; the fee then shows in the loan's
    transactions and in its fees balance. Nothing else on the loan changes. Success is the receipt
    returned with the fee reference.

    Args:
        loan_id: Id class — the loan number of the Hearthstone Home Finance loan, as returned by the
            loan lookup for the verified borrower.
        source_txn_id: Id class — the transaction id (reference number) of the installment payment the
            bank returned, as shown in the loan's transaction list (the payment the return record points to).
        amount: Fixed-format class — the returned-payment fee in USD, a positive amount with 2 decimal
            places (rounded half up to the cent).

    Returns:
        A dictionary rendered as text with: status ("charged" on success); loan_txn_id (reference of
        the fee transaction); loan_id; source_txn_id (the returned payment); txn_date (YYYY-MM-DD,
        today); amount (USD, 2 decimal places); and fees_balance (USD, 2 decimal places, the fees owed
        on the loan after the fee).
    """
    today = ctx.now()[:10]
    loan = ctx.find("loan_holdings", loan_id=loan_id)
    fee = round(float(amount), 2)
    tid = ctx.make_id("ltx_", loan_id, source_txn_id, fee, today)
    ctx.create("loan_transactions", tid, loan_txn_id=tid, loan_id=loan_id,
               customer_id=(loan[0].get("customer_id") if loan else ""),
               event_type="loan_nsf_fee", txn_date=today, source_txn_id=source_txn_id, amount=fee)
    balance = round(float((loan[0].get("fees_balance") if loan else 0) or 0) + fee, 2)
    ctx.update("loan_holdings", loan_id, fees_balance=balance)
    return str({"status": "charged", "loan_txn_id": tid, "loan_id": loan_id, "source_txn_id": source_txn_id,
                "txn_date": today, "amount": fee, "fees_balance": balance})


@tool(owner="user", rw="write")
def make_good_faith_payment_f58b4303(ctx: ToolContext, loan_id: str, amount: float) -> str:
    """Make a good-faith partial payment on your own Hearthstone Home Finance loan by phone from your bank account.

    The borrower authorizes a one-time phone ACH payment of the stated amount on their loan. The
    payment is recorded today as a partial payment and held in the loan's suspense balance until
    suspense funds add up to a full installment; no installment is marked paid by it. Success is
    the receipt returned with a payment confirmation number.

    Args:
        loan_id: Id class — the loan number of your Hearthstone Home Finance loan, as the agent reads
            it to you from the loan record.
        amount: Fixed-format class — the payment amount in USD, a positive amount with 2 decimal places
            (rounded half up to the cent), as the agent tells it to you.

    Returns:
        A dictionary rendered as text with: status ("received" on success); loan_txn_id (reference of
        the payment transaction); payment_ref (the payment confirmation number to keep); loan_id;
        txn_date (YYYY-MM-DD, today); amount (USD, 2 decimal places); payment_channel ("phone_ach");
        and suspense_balance (USD, 2 decimal places, funds held unapplied after the payment).
    """
    today = ctx.now()[:10]
    loan = ctx.find("loan_holdings", loan_id=loan_id)
    paid = round(float(amount), 2)
    tid = ctx.make_id("ltx_", loan_id, paid, today, "good_faith")
    ref = "PH" + ctx.make_id("", loan_id, paid, today, length=8).upper()
    ctx.create("loan_transactions", tid, loan_txn_id=tid, loan_id=loan_id,
               customer_id=(loan[0].get("customer_id") if loan else ""),
               event_type="loan_partial_payment", txn_date=today, amount=paid,
               payment_channel="phone_ach", payment_ref=ref)
    held = round(float((loan[0].get("suspense_balance") if loan else 0) or 0) + paid, 2)
    ctx.update("loan_holdings", loan_id, suspense_balance=held)
    return str({"status": "received", "loan_txn_id": tid, "payment_ref": ref, "loan_id": loan_id,
                "txn_date": today, "amount": paid, "payment_channel": "phone_ach", "suspense_balance": held})


@tool(owner="user", rw="write")
def sign_deferment_agreement_a442f6a7(ctx: ToolContext, loan_id: str, deferred_months: int,
                                      deferment_fee: float) -> str:
    """Sign a deferment agreement on your own Hearthstone Home Finance loan, moving unpaid installments to the end of the loan.

    The borrower signs, today, an agreement deferring the stated number of the oldest unpaid
    installments, unchanged, to follow the maturity date. On signing, the agreement is recorded on
    the loan; the due date of the oldest unpaid installment and the maturity date each move forward
    by that many months; the installments deferred over the life of the loan increase by the same
    number; and the deferment fee is charged and added to the fees owed on the loan. Success is the
    receipt returned with the agreement reference.

    Args:
        loan_id: Id class — the loan number of your Hearthstone Home Finance loan, as the agent reads
            it to you from the loan record.
        deferred_months: Fixed-format class — the number of installments deferred, a positive integer,
            as the agent tells it to you.
        deferment_fee: Fixed-format class — the deferment fee in USD, a positive amount with 2 decimal
            places (rounded half up to the cent), as the agent tells it to you.

    Returns:
        A dictionary rendered as text with: status ("signed" on success); loan_notice_id (reference of
        the deferment agreement); fee_txn_id (reference of the deferment fee transaction); loan_id;
        notice_date (YYYY-MM-DD, today); deferred_months (integer); effective_due_date (YYYY-MM-DD, the
        oldest unpaid installment due date after the deferment); new_maturity_date (YYYY-MM-DD);
        deferment_fee (USD, 2 decimal places); and fees_balance (USD, 2 decimal places, fees owed after
        the fee).
    """
    today = ctx.now()[:10]
    loan = ctx.find("loan_holdings", loan_id=loan_id)
    rec = loan[0] if loan else {}
    months = int(deferred_months)
    fee = round(float(deferment_fee), 2)
    effective = _Calendar.add_months(rec.get("next_due_date") or today, months)
    maturity = _Calendar.add_months(rec.get("maturity_date") or today, months)
    nid = ctx.make_id("lnt_", loan_id, months, fee, today)
    ctx.create("loan_notices", nid, loan_notice_id=nid, loan_id=loan_id, customer_id=rec.get("customer_id", ""),
               event_type="loan_deferment_agreement", notice_date=today, deferred_months=months,
               effective_due_date=effective, new_maturity_date=maturity)
    fid = ctx.make_id("ltx_", loan_id, nid, fee)
    ctx.create("loan_transactions", fid, loan_txn_id=fid, loan_id=loan_id, customer_id=rec.get("customer_id", ""),
               event_type="loan_deferment_fee", txn_date=today, source_txn_id=nid, amount=fee)
    balance = round(float(rec.get("fees_balance") or 0) + fee, 2)
    ctx.update("loan_holdings", loan_id, next_due_date=effective, maturity_date=maturity,
               deferred_months_total=int(rec.get("deferred_months_total") or 0) + months,
               fees_balance=balance)
    return str({"status": "signed", "loan_notice_id": nid, "fee_txn_id": fid, "loan_id": loan_id,
                "notice_date": today, "deferred_months": months, "effective_due_date": effective,
                "new_maturity_date": maturity, "deferment_fee": fee, "fees_balance": balance})


@tool(owner="agent", rw="write")
def issue_payoff_statement_6569642c(ctx: ToolContext, loan_id: str, good_through_date: str,
                                    payoff_amount: float) -> str:
    """Issue a payoff statement on a Hearthstone Home Finance loan, dated today.

    Records one payoff statement on the loan stating the amount that pays the loan in full and the
    last day that figure is good; the statement then appears among the loan's notices and can be
    given to the borrower or the closing agent. Balances on the loan are not changed. Success is
    the receipt returned with the statement reference.

    Args:
        loan_id: Id class — the loan number of the Hearthstone Home Finance loan, as returned by the
            loan lookup for the verified borrower.
        good_through_date: Fixed-format class — the last day the payoff figure is good, written
            YYYY-MM-DD (a calendar date, no time of day).
        payoff_amount: Fixed-format class — the amount that pays the loan in full on or before the
            good-through date, in USD with 2 decimal places (rounded half up to the cent).

    Returns:
        A dictionary rendered as text with: status ("issued" on success); loan_notice_id (reference of
        the payoff statement); loan_id; notice_date (YYYY-MM-DD, today); good_through_date (YYYY-MM-DD);
        and payoff_amount (USD, 2 decimal places).
    """
    today = ctx.now()[:10]
    loan = ctx.find("loan_holdings", loan_id=loan_id)
    amt = round(float(payoff_amount), 2)
    nid = ctx.make_id("lnt_", loan_id, good_through_date, amt, today)
    ctx.create("loan_notices", nid, loan_notice_id=nid, loan_id=loan_id,
               customer_id=(loan[0].get("customer_id") if loan else ""), event_type="loan_payoff_statement",
               notice_date=today, good_through_date=str(good_through_date)[:10], payoff_amount=amt)
    return str({"status": "issued", "loan_notice_id": nid, "loan_id": loan_id, "notice_date": today,
                "good_through_date": str(good_through_date)[:10], "payoff_amount": amt})


@tool(owner="agent", rw="write")
def assess_late_charge_8f52dfa4(ctx: ToolContext, loan_id: str, installment_due_date: str,
                                amount: float) -> str:
    """Assess a late charge on a Hearthstone Home Finance loan for one installment, dated today.

    Books one late charge against the installment named by its due date and adds it to the fees the
    borrower owes on the loan; the charge then shows in the loan's transactions and in its fees
    balance. Nothing else on the loan changes. Success is the receipt returned with the charge
    reference.

    Args:
        loan_id: Id class — the loan number of the Hearthstone Home Finance loan, as returned by the
            loan lookup for the verified borrower.
        installment_due_date: Fixed-format class — the due date of the installment the late charge is
            for, written YYYY-MM-DD.
        amount: Fixed-format class — the late charge in USD, a positive amount with 2 decimal places
            (rounded half up to the cent).

    Returns:
        A dictionary rendered as text with: status ("assessed" on success); loan_txn_id (reference of
        the late charge); loan_id; installment_due_date (YYYY-MM-DD); txn_date (YYYY-MM-DD, today);
        amount (USD, 2 decimal places); and fees_balance (USD, 2 decimal places, fees owed after the
        charge).
    """
    today = ctx.now()[:10]
    loan = ctx.find("loan_holdings", loan_id=loan_id)
    fee = round(float(amount), 2)
    tid = ctx.make_id("ltx_", loan_id, installment_due_date, fee, today)
    ctx.create("loan_transactions", tid, loan_txn_id=tid, loan_id=loan_id,
               customer_id=(loan[0].get("customer_id") if loan else ""), event_type="loan_late_charge",
               txn_date=today, installment_due_date=str(installment_due_date)[:10], amount=fee)
    balance = round(float((loan[0].get("fees_balance") if loan else 0) or 0) + fee, 2)
    ctx.update("loan_holdings", loan_id, fees_balance=balance)
    return str({"status": "assessed", "loan_txn_id": tid, "loan_id": loan_id,
                "installment_due_date": str(installment_due_date)[:10], "txn_date": today, "amount": fee,
                "fees_balance": balance})


@tool(owner="user", rw="write")
def make_principal_paydown_1606199b(ctx: ToolContext, loan_id: str, amount: float) -> str:
    """Pay down the principal of your own Hearthstone Home Finance loan by phone from your bank account.

    The borrower authorizes a one-time phone ACH payment designated to principal. It is recorded
    today as an extra principal payment that lowers the loan's unpaid principal by the amount paid;
    it does not move the next installment's due date and is not applied to fees. Success is the
    receipt returned with a payment confirmation number.

    Args:
        loan_id: Id class — the loan number of your Hearthstone Home Finance loan, as the agent reads
            it to you from the loan record.
        amount: Fixed-format class — the principal payment in USD, a positive amount with 2 decimal
            places (rounded half up to the cent), as the agent tells it to you.

    Returns:
        A dictionary rendered as text with: status ("received" on success); loan_txn_id (reference of
        the principal payment); payment_ref (the payment confirmation number to keep); loan_id;
        txn_date (YYYY-MM-DD, today); amount (USD, 2 decimal places); payment_channel ("phone_ach");
        and principal_balance (USD, 2 decimal places, unpaid principal after the payment).
    """
    today = ctx.now()[:10]
    loan = ctx.find("loan_holdings", loan_id=loan_id)
    paid = round(float(amount), 2)
    tid = ctx.make_id("ltx_", loan_id, paid, today, "paydown")
    ref = "PH" + ctx.make_id("", loan_id, paid, today, "paydown", length=8).upper()
    ctx.create("loan_transactions", tid, loan_txn_id=tid, loan_id=loan_id,
               customer_id=(loan[0].get("customer_id") if loan else ""), event_type="loan_curtailment",
               txn_date=today, amount=paid, payment_channel="phone_ach", payment_ref=ref)
    principal = round(float((loan[0].get("principal_balance") if loan else 0) or 0) - paid, 2)
    ctx.update("loan_holdings", loan_id, principal_balance=principal)
    return str({"status": "received", "loan_txn_id": tid, "payment_ref": ref, "loan_id": loan_id,
                "txn_date": today, "amount": paid, "payment_channel": "phone_ach",
                "principal_balance": principal})

"""Hidden task tools of the personal_loan_servicing difficulty (Larkspur Lending personal loans).

Each tool performs exactly one atomic write with the values it is given. A tool never works out an amount,
never checks eligibility and never refuses because of a business condition; every judgement belongs to the
caller, from the published policy and the records.
"""

from erlbench import ToolContext, tool


@tool(owner="agent", rw="write")
def issue_payoff_quote_88f1b45e(ctx: ToolContext, loan_id: str, customer_id: str, quote_purpose: str,
                                good_through_date: str, payoff_amount: float) -> str:
    """Issue a payoff quote on a Larkspur personal loan.

    Records one payoff quote for the loan, dated today, with the given purpose, stating the single amount that
    pays the loan in full if received by the good-through date. The loan itself, its balances and its schedule
    are not changed. On success the quote can be seen among the loan's payoff quotes with the stated purpose,
    amount and good-through date.

    Args:
        loan_id: Id class — reference number of the personal loan being quoted, as returned by the loan lookup.
        customer_id: Id class — reference number of the borrower who owns that loan, as returned by the customer
            profile lookup.
        quote_purpose: Enum class — why the quote is issued, exactly one of:
                borrower_payoff - the borrower will pay the loan off directly;
                refinance - a Larkspur refinance loan will pay the loan off by internal transfer;
                third_party_lender - another lender will pay the loan off, on the borrower's authorization.
        good_through_date: Fixed-format class — last calendar date on which the quoted amount is valid, written
            as YYYY-MM-DD in Eastern Time; no empty value.
        payoff_amount: Fixed-format class — the quoted payoff amount in US dollars, a decimal number with 2
            decimal places (cents); the value is stored rounded to the cent.

    Returns:
        A one-line confirmation string of the form "Payoff quote <quote id> issued on loan <loan id> for
        <purpose>: quote date <YYYY-MM-DD>, good through <YYYY-MM-DD>, payoff amount <USD with 2 decimals>."
        The quote id is the reference number of the new quote; the quote date is today; the presence of the
        quote id means the quote was recorded.
    """
    amount = round(float(payoff_amount) , 2)
    rid = ctx.make_id("lpq_", loan_id, customer_id, quote_purpose, good_through_date, amount)
    today = ctx.now()[:10]
    ctx.create("loan_payoff_quotes", rid, payoff_quote_id=rid, loan_id=loan_id, customer_id=customer_id,
               event_type="loan_payoff_quote_issued", quote_date=today, good_through_date=good_through_date,
               payoff_amount=amount, quote_purpose=quote_purpose)
    return (f"Payoff quote {rid} issued on loan {loan_id} for {quote_purpose}: quote date {today}, "
            f"good through {good_through_date}, payoff amount {amount:.2f}.")


@tool(owner="user", rw="write")
def submit_refinance_application_9ec5cb64(ctx: ToolContext, customer_id: str, refinanced_from_loan_id: str,
                                          variant_name: str, origination_state: str, term_months: int,
                                          amount_financed: float) -> str:
    """Submit, as the borrower, an application for a Larkspur refinance loan that pays off an existing loan.

    The borrower consents to the refinance by submitting this application. It records one new personal loan
    application in applied status with the loan purpose refinance_existing_loan, dated today, naming the loan
    it will pay off, the prequalification grade, the state of residence, the term and the amount financed
    requested. The existing loan is not changed. On success the borrower sees the new application among their
    loans, in applied status, awaiting the underwriting decision.

    Args:
        customer_id: Id class — reference number of the applying borrower, as returned by the customer profile
            lookup.
        refinanced_from_loan_id: Id class — reference number of the existing Larkspur loan the refinance will pay
            off, as returned by the loan lookup.
        variant_name: Enum class — prequalification rate grade of the application, exactly one of:
                Personal Loan Grade A - the application is prequalified at Grade A;
                Personal Loan Grade B - the application is prequalified at Grade B;
                Personal Loan Grade C - the application is prequalified at Grade C;
                Personal Loan Grade D - the application is prequalified at Grade D;
                Personal Loan Grade E - the application is prequalified at Grade E;
                Personal Loan Grade F - the application is prequalified at Grade F;
                Personal Loan Grade G - the application is prequalified at Grade G.
        origination_state: Enum class — two-letter code of the borrower's state of residence on the application,
            exactly one of:
                AL - the state of residence on the borrower's profile is Alabama;
                AK - the state of residence on the borrower's profile is Alaska;
                AZ - the state of residence on the borrower's profile is Arizona;
                AR - the state of residence on the borrower's profile is Arkansas;
                CA - the state of residence on the borrower's profile is California;
                CO - the state of residence on the borrower's profile is Colorado;
                CT - the state of residence on the borrower's profile is Connecticut;
                DE - the state of residence on the borrower's profile is Delaware;
                DC - the state of residence on the borrower's profile is the District of Columbia;
                FL - the state of residence on the borrower's profile is Florida;
                GA - the state of residence on the borrower's profile is Georgia;
                HI - the state of residence on the borrower's profile is Hawaii;
                ID - the state of residence on the borrower's profile is Idaho;
                IL - the state of residence on the borrower's profile is Illinois;
                IN - the state of residence on the borrower's profile is Indiana;
                IA - the state of residence on the borrower's profile is Iowa;
                KS - the state of residence on the borrower's profile is Kansas;
                KY - the state of residence on the borrower's profile is Kentucky;
                LA - the state of residence on the borrower's profile is Louisiana;
                ME - the state of residence on the borrower's profile is Maine;
                MD - the state of residence on the borrower's profile is Maryland;
                MA - the state of residence on the borrower's profile is Massachusetts;
                MI - the state of residence on the borrower's profile is Michigan;
                MN - the state of residence on the borrower's profile is Minnesota;
                MS - the state of residence on the borrower's profile is Mississippi;
                MO - the state of residence on the borrower's profile is Missouri;
                MT - the state of residence on the borrower's profile is Montana;
                NE - the state of residence on the borrower's profile is Nebraska;
                NV - the state of residence on the borrower's profile is Nevada;
                NH - the state of residence on the borrower's profile is New Hampshire;
                NJ - the state of residence on the borrower's profile is New Jersey;
                NM - the state of residence on the borrower's profile is New Mexico;
                NY - the state of residence on the borrower's profile is New York;
                NC - the state of residence on the borrower's profile is North Carolina;
                ND - the state of residence on the borrower's profile is North Dakota;
                OH - the state of residence on the borrower's profile is Ohio;
                OK - the state of residence on the borrower's profile is Oklahoma;
                OR - the state of residence on the borrower's profile is Oregon;
                PA - the state of residence on the borrower's profile is Pennsylvania;
                RI - the state of residence on the borrower's profile is Rhode Island;
                SC - the state of residence on the borrower's profile is South Carolina;
                SD - the state of residence on the borrower's profile is South Dakota;
                TN - the state of residence on the borrower's profile is Tennessee;
                TX - the state of residence on the borrower's profile is Texas;
                UT - the state of residence on the borrower's profile is Utah;
                VT - the state of residence on the borrower's profile is Vermont;
                VA - the state of residence on the borrower's profile is Virginia;
                WA - the state of residence on the borrower's profile is Washington;
                WV - the state of residence on the borrower's profile is West Virginia;
                WI - the state of residence on the borrower's profile is Wisconsin;
                WY - the state of residence on the borrower's profile is Wyoming;
        term_months: Fixed-format class — repayment term the borrower chooses for the new loan, a whole number of
            months written as an integer, one of 24, 36, 48, 60 or 72; no empty value.
        amount_financed: Fixed-format class — loan amount requested on the application in US dollars, origination
            fee included, a decimal number with 2 decimal places (cents); the value is stored rounded to
            the cent.

    Returns:
        A one-line confirmation string of the form "Refinance application <new loan id> submitted on <YYYY-MM-DD>:
        status applied, pays off loan <existing loan id>, <grade>, <state>, <term> months, amount financed <USD
        with 2 decimals>." The new loan id is the reference number of the application; the status applied means
        it was recorded.
    """
    amount = round(float(amount_financed) , 2)
    term = int(term_months)
    rid = ctx.make_id("loan_", customer_id, refinanced_from_loan_id, variant_name, origination_state, term, amount)
    today = ctx.now()[:10]
    ctx.create("loans", rid, loan_id=rid, customer_id=customer_id, variant_name=variant_name, status="applied",
               loan_purpose="refinance_existing_loan", origination_state=origination_state, application_date=today,
               term_months=term, amount_financed=amount, refinanced_from_loan_id=refinanced_from_loan_id)
    return (f"Refinance application {rid} submitted on {today}: status applied, pays off loan "
            f"{refinanced_from_loan_id}, {variant_name}, {origination_state}, {term} months, "
            f"amount financed {amount:.2f}.")


@tool(owner="agent", rw="write")
def assess_late_fee_8eb98004(ctx: ToolContext, loan_id: str, customer_id: str, installment_due_date: str,
                             fee_schedule: str, amount: float) -> str:
    """Charge a late fee on one installment of a Larkspur personal loan.

    Records one late fee line on the loan, dated today, for the installment named by its due date, under the
    named state fee schedule, and adds the fee to the loan's unpaid fees. Nothing else on the loan changes. On
    success the fee appears in the loan's ledger and the loan's unpaid fees are higher by the fee amount.

    Args:
        loan_id: Id class — reference number of the personal loan charged, as returned by the loan lookup.
        customer_id: Id class — reference number of the borrower who owns that loan, as returned by the customer
            profile lookup.
        installment_due_date: Fixed-format class — due date of the installment the fee is charged for, written as
            YYYY-MM-DD; no empty value.
        fee_schedule: Enum class — state fee schedule the fee is charged under, exactly one of:
                schedule_a - the loan's origination state uses fee schedule A;
                schedule_b - the loan's origination state uses fee schedule B;
                schedule_c - the loan's origination state uses fee schedule C.
        amount: Fixed-format class — the late fee in USD, a decimal number with 2 decimal places (cents); the value
            is stored rounded to the cent.

    Returns:
        A one-line confirmation string of the form "Late fee <ledger line id> charged on loan <loan id> for the
        installment due <YYYY-MM-DD>: <USD with 2 decimals> under <schedule>; unpaid fees now <USD with 2
        decimals>." The ledger line id is the reference number of the new fee; its presence means the fee was
        recorded.
    """
    amt = round(float(amount) , 2)
    rid = ctx.make_id("ltx_", loan_id, customer_id, installment_due_date, fee_schedule, amt)
    today = ctx.now()[:10]
    ctx.create("loan_transactions", rid, loan_txn_id=rid, loan_id=loan_id, customer_id=customer_id,
               event_type="loan_late_fee_assessed", txn_date=today, amount=amt,
               installment_due_date=installment_due_date, fee_schedule=fee_schedule)
    loan = (ctx.find("loans", loan_id=loan_id) or [{}])[0]
    fees = round(float(loan.get("fees_balance") or 0) + amt, 2)
    ctx.update("loans", loan_id, fees_balance=fees)
    return (f"Late fee {rid} charged on loan {loan_id} for the installment due {installment_due_date}: "
            f"{amt:.2f} under {fee_schedule}; unpaid fees now {fees:.2f}.")


@tool(owner="agent", rw="write")
def assess_returned_payment_fee_e467aa52(ctx: ToolContext, loan_id: str, customer_id: str, related_txn_id: str,
                                         fee_schedule: str, amount: float) -> str:
    """Charge a returned-payment fee for one returned payment on a Larkspur personal loan.

    Records one returned-payment fee line on the loan, dated today, pointing at the returned-payment line it is
    charged for, under the named state fee schedule, and adds the fee to the loan's unpaid fees. Nothing else on
    the loan changes. On success the fee appears in the loan's ledger and the loan's unpaid fees are higher by the
    fee amount.

    Args:
        loan_id: Id class — reference number of the personal loan charged, as returned by the loan lookup.
        customer_id: Id class — reference number of the borrower who owns that loan, as returned by the customer
            profile lookup.
        related_txn_id: Id class — reference number of the returned-payment ledger line the fee is charged for, as
            returned by the loan ledger lookup.
        fee_schedule: Enum class — state fee schedule the fee is charged under, exactly one of:
                schedule_a - the loan's origination state uses fee schedule A;
                schedule_b - the loan's origination state uses fee schedule B;
                schedule_c - the loan's origination state uses fee schedule C.
        amount: Fixed-format class — the returned-payment fee in USD, a decimal number with 2 decimal places
            (cents); the value is stored rounded to the cent.

    Returns:
        A one-line confirmation string of the form "Returned-payment fee <ledger line id> charged on loan <loan id>
        for return <returned line id>: <USD with 2 decimals> under <schedule>; unpaid fees now <USD with 2
        decimals>." The ledger line id is the reference number of the new fee; its presence means the fee was
        recorded.
    """
    amt = round(float(amount) , 2)
    rid = ctx.make_id("ltx_", loan_id, customer_id, related_txn_id, fee_schedule, amt)
    today = ctx.now()[:10]
    ctx.create("loan_transactions", rid, loan_txn_id=rid, loan_id=loan_id, customer_id=customer_id,
               event_type="loan_returned_payment_fee_assessed", txn_date=today, amount=amt,
               related_txn_id=related_txn_id, fee_schedule=fee_schedule)
    loan = (ctx.find("loans", loan_id=loan_id) or [{}])[0]
    fees = round(float(loan.get("fees_balance") or 0) + amt, 2)
    ctx.update("loans", loan_id, fees_balance=fees)
    return (f"Returned-payment fee {rid} charged on loan {loan_id} for return {related_txn_id}: {amt:.2f} "
            f"under {fee_schedule}; unpaid fees now {fees:.2f}.")


@tool(owner="user", rw="write")
def enroll_autopay_4dda8507(ctx: ToolContext, loan_id: str, customer_id: str, bank_account_id: str,
                            current_interest_rate: float) -> str:
    """Authorize, as the borrower, recurring AutoPay debits on a Larkspur personal loan.

    The borrower authorizes Larkspur to debit the scheduled installment from the named linked bank account on each
    due date. Records one AutoPay enrollment on the loan, dated today, by phone, and sets the loan's AutoPay on,
    its AutoPay account to the named account and its current interest rate to the rate given. On success the
    borrower sees AutoPay on for the loan, debiting that account, with the new rate in force.

    Args:
        loan_id: Id class — reference number of the personal loan, as returned by the loan lookup.
        customer_id: Id class — reference number of the borrower, as returned by the customer profile lookup.
        bank_account_id: Id class — reference number of the borrower's linked bank account to be debited, as
            returned by the linked bank account lookup.
        current_interest_rate: Fixed-format class — the interest rate in force on the loan from today, an annual
            rate in percent with 2 decimal places, written as a plain number of percent; no empty value.

    Returns:
        A one-line confirmation string of the form "AutoPay enrollment <servicing record id> recorded on loan
        <loan id>: AutoPay on, debiting account <bank account id>, rate in force <percent with 2 decimals>." The
        servicing record id is the reference number of the enrollment; its presence means AutoPay is on.
    """
    rate = round(float(current_interest_rate) , 2)
    rid = ctx.make_id("lse_", loan_id, customer_id, bank_account_id, rate)
    today = ctx.now()[:10]
    ctx.create("loan_servicing_events", rid, loan_service_event_id=rid, loan_id=loan_id, customer_id=customer_id,
               event_type="loan_autopay_enrolled", event_date=today, request_channel="phone",
               bank_account_id=bank_account_id)
    ctx.update("loans", loan_id, autopay_enrolled=True, autopay_bank_account_id=bank_account_id,
               current_interest_rate=rate)
    return (f"AutoPay enrollment {rid} recorded on loan {loan_id}: AutoPay on, debiting account "
            f"{bank_account_id}, rate in force {rate:.2f}.")


@tool(owner="agent", rw="write")
def waive_fee_courtesy_87326602(ctx: ToolContext, loan_id: str, customer_id: str, related_txn_id: str,
                                amount: float) -> str:
    """Waive, as a courtesy, all or part of one fee on a Larkspur personal loan.

    Records one fee waiver line on the loan, dated today, with the basis courtesy, pointing at the fee it waives,
    and takes the waived amount off the loan's unpaid fees. Nothing else on the loan changes. On success the waiver
    appears in the loan's ledger and the loan's unpaid fees are lower by the amount waived.

    Args:
        loan_id: Id class — reference number of the personal loan, as returned by the loan lookup.
        customer_id: Id class — reference number of the borrower, as returned by the customer profile lookup.
        related_txn_id: Id class — reference number of the fee ledger line being waived, as shown for that fee in
            the loan ledger.
        amount: Fixed-format class — the amount waived in USD, a decimal number with 2 decimal places (cents); the
            value is stored rounded to the cent.

    Returns:
        A one-line confirmation string of the form "Courtesy waiver <ledger line id> recorded on loan <loan id>
        against fee <fee line id>: <USD with 2 decimals> waived; unpaid fees now <USD with 2 decimals>." The ledger
        line id is the reference number of the waiver; its presence means the waiver was recorded.
    """
    amt = round(float(amount) , 2)
    rid = ctx.make_id("ltx_", loan_id, customer_id, related_txn_id, amt)
    today = ctx.now()[:10]
    ctx.create("loan_transactions", rid, loan_txn_id=rid, loan_id=loan_id, customer_id=customer_id,
               event_type="loan_fee_waived", txn_date=today, amount=amt, related_txn_id=related_txn_id,
               waiver_reason="courtesy")
    loan = (ctx.find("loans", loan_id=loan_id) or [{}])[0]
    fees = round(float(loan.get("fees_balance") or 0) - amt, 2)
    ctx.update("loans", loan_id, fees_balance=fees)
    return (f"Courtesy waiver {rid} recorded on loan {loan_id} against fee {related_txn_id}: {amt:.2f} waived; "
            f"unpaid fees now {fees:.2f}.")

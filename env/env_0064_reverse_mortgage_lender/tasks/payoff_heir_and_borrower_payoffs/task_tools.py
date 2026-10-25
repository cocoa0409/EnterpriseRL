"""Hidden task tools for the payoff_heir_and_borrower_payoffs difficulty of env_0064_reverse_mortgage_lender.

Each tool performs one atomic write on a payoff case, its ledger or its submissions. Every value a tool
records is passed in by the caller; the tools check no eligibility and compute no figure.
"""

from erlbench import ToolContext, tool


@tool(owner="agent", rw="write")
def record_payoff_daily_accrual_16b003bd(ctx: ToolContext, payoff_case_id: str, payoff_request_id: str,
                                         maturity_case_id: str, per_diem_amount: float) -> str:
    """Record the daily accrual (per diem) on a borrower's payoff case for a loan that has been called due.

    The case's daily accrual is replaced by the amount passed in; its status and every other figure on the case
    stay as they are, and the statement request and maturity case named are quoted back in the receipt. On success
    the case shows the new daily accrual, which can be quoted to the borrower.

    Args:
        payoff_case_id: Id class — the reference number of the payoff case, as returned by the payoff case lookup.
        payoff_request_id: Id class — the reference number of the payoff statement request on file that this write
            answers, as returned by the payoff submission lookup.
        maturity_case_id: Id class — the reference number of the loan's maturity case, as returned by the maturity
            case lookup.
        per_diem_amount: Fixed-format class — the daily accrual to record, in USD with 2 decimal places, rounded
            half up to the cent.

    Returns:
        A confirmation string naming the payoff case, statement request and maturity case reference numbers and the
        daily accrual now recorded (USD, 2 decimal places); the words "daily accrual recorded" indicate the write
        completed.
    """
    amt = round(float(per_diem_amount), 2)
    ctx.update("payoff_cases", payoff_case_id, per_diem_amount=amt)
    return (f"Payoff case {payoff_case_id} (request {payoff_request_id}, maturity case {maturity_case_id}): "
            f"daily accrual recorded at {amt:.2f}.")


@tool(owner="agent", rw="write")
def issue_retention_payoff_statement_a856e53a(ctx: ToolContext, payoff_case_id: str, payoff_request_id: str,
                                              maturity_case_id: str, statement_good_through_date: str,
                                              statement_balance: float) -> str:
    """Issue the payoff statement on a borrower's payoff case for a loan that has been called due, moving the case
    from opened to terms_issued.

    The statement is dated today. The case records the statement date, the good-through date and the statement
    balance passed in, and its required payoff amount is set equal to that statement balance. The daily accrual,
    appraised value basis, contract figures, funds held and the statement request named are left unchanged; the
    request and maturity case are quoted back in the receipt. On success the case shows status terms_issued with
    these statement figures.

    Args:
        payoff_case_id: Id class — the reference number of the payoff case the statement is issued on, as returned
            by the payoff case lookup.
        payoff_request_id: Id class — the reference number of the payoff statement request on file that this write
            answers, as returned by the payoff submission lookup.
        maturity_case_id: Id class — the reference number of the loan's maturity case, as returned by the maturity
            case lookup.
        statement_good_through_date: Fixed-format class — the last calendar day the statement's figures are good,
            written YYYY-MM-DD in the servicer's local calendar.
        statement_balance: Fixed-format class — the loan balance projected to the good-through date, in USD with 2
            decimal places, rounded half up to the cent.

    Returns:
        A confirmation string naming the payoff case, statement request and maturity case reference numbers, the
        status terms_issued, the statement date and good-through date (YYYY-MM-DD) and the statement balance and
        required payoff amount (USD, 2 decimal places). The status terms_issued in the receipt indicates the
        statement was issued.
    """
    today = ctx.now()[:10]
    bal = round(float(statement_balance), 2)
    ctx.update("payoff_cases", payoff_case_id, status="terms_issued", statement_date=today,
               statement_good_through_date=statement_good_through_date, statement_balance=bal,
               required_payoff_amount=bal)
    return (f"Payoff case {payoff_case_id} (request {payoff_request_id}, maturity case {maturity_case_id}): "
            f"status terms_issued; statement date {today}, good through "
            f"{statement_good_through_date}; statement balance {bal:.2f}; required payoff amount {bal:.2f}.")


@tool(owner="agent", rw="write")
def approve_appraisal_based_payoff_a02ac9a5(ctx: ToolContext, payoff_case_id: str, payoff_request_id: str,
                                            maturity_case_id: str, appraised_value_basis: float,
                                            required_payoff_amount: float) -> str:
    """Approve the payoff amount on a borrower's payoff case for a loan that has been called due, replacing the
    case's required payoff amount and recording the appraised value it relies on.

    The case keeps its status, statement date, good-through date, statement balance and daily accrual; only the
    appraised value basis and the required payoff amount are replaced by the values passed in, and the statement
    request and maturity case named are quoted back in the receipt. On success the case shows the approved required
    payoff amount, which is the figure the borrower is told will pay off the loan.

    Args:
        payoff_case_id: Id class — the reference number of the payoff case, as returned by the payoff case lookup.
        payoff_request_id: Id class — the reference number of the payoff statement request on file that this write
            answers, as returned by the payoff submission lookup.
        maturity_case_id: Id class — the reference number of the loan's maturity case whose appraisal the approval
            relies on, as returned by the maturity case lookup.
        appraised_value_basis: Fixed-format class — the as-is appraised value the approval relies on, in USD with
            2 decimal places, rounded half up to the cent.
        required_payoff_amount: Fixed-format class — the approved amount that pays off the loan, in USD with 2
            decimal places, rounded half up to the cent.

    Returns:
        A confirmation string naming the payoff case, statement request and maturity case reference numbers, the
        appraised value basis and the approved required payoff amount (USD, 2 decimal places); the word "approved"
        indicates the write completed.
    """
    basis = round(float(appraised_value_basis), 2)
    req = round(float(required_payoff_amount), 2)
    ctx.update("payoff_cases", payoff_case_id, appraised_value_basis=basis, required_payoff_amount=req)
    return (f"Payoff case {payoff_case_id} (request {payoff_request_id}, maturity case {maturity_case_id}): "
            f"payoff approved; appraised value basis {basis:.2f}; "
            f"required payoff amount {req:.2f}.")


@tool(owner="user", rw="write")
def remit_borrower_payoff_funds_17f1493b(ctx: ToolContext, payoff_case_id: str, remittance_method: str,
                                         remitter_name: str, amount: float) -> str:
    """Send payoff funds in the customer's own name to their payoff case, recorded as one receipt that the case
    holds until the loan is paid off.

    The receipt is dated today, carries the method, sender name and amount given, and receives a newly issued
    remittance reference. The amount is added to the funds the case holds. On success the customer can see the
    receipt on the case and quote its remittance reference.

    Args:
        payoff_case_id: Id class — the reference number of the payoff case the funds are sent to, as given by the
            servicer.
        remittance_method: Enum class — how the funds are sent: wire (a bank wire transfer to the servicer's payoff
            account); cashiers_check (a cashier's check delivered to the servicer); check (a check the servicer itself
            issues when it pays money out, never used for funds a customer sends); not_applicable (an entry where no
            cash moves, never used for funds a customer sends).
        remitter_name: Verbatim class — the sender's full name exactly as the customer states it for the funds, copied
            character for character (verbatim).
        amount: Fixed-format class — the amount sent, in USD with 2 decimal places, rounded half up to the cent.

    Returns:
        A confirmation string naming the payoff case reference number, the receipt reference number, the issued
        remittance reference (text), the method, the sender name and the amount (USD, 2 decimal places), and the
        funds now held on the case (USD, 2 decimal places); the word "received" indicates the funds were recorded.
    """
    amt = round(float(amount), 2)
    case = ctx.find("payoff_cases", payoff_case_id=payoff_case_id)
    cust = case[0].get("customer_id", "") if case else ""
    held = round(float(case[0].get("funds_held") or 0) + amt, 2) if case else amt
    rid = ctx.make_id("ptx_", payoff_case_id, remittance_method, remitter_name, amt)
    ref = "CRM-" + rid[-8:].upper()
    today = ctx.now()[:10]
    ctx.create("payoff_transactions", rid, payoff_txn_id=rid, payoff_case_id=payoff_case_id, customer_id=cust,
               event_type="payoff_funds_received", amount=amt, effective_date=today,
               remittance_method=remittance_method, remittance_reference=ref, remitter_name=remitter_name,
               source_txn_ref="")
    ctx.update("payoff_cases", payoff_case_id, funds_held=held)
    return (f"Payoff case {payoff_case_id}: funds received, receipt {rid}, remittance reference {ref}, "
            f"{remittance_method} from {remitter_name}, amount {amt:.2f}; funds held {held:.2f}.")


@tool(owner="agent", rw="write")
def record_sale_daily_accrual_1c6aaad4(ctx: ToolContext, payoff_case_id: str, payoff_request_id: str,
                                         maturity_case_id: str, per_diem_amount: float) -> str:
    """Record the daily accrual (per diem) on a borrower's short-sale payoff case.

    The case's daily accrual is replaced by the amount passed in; its status and every other figure on the case
    stay as they are, and the statement request and maturity case named are quoted back in the receipt. On success
    the case shows the new daily accrual, which can be quoted to the borrower.

    Args:
        payoff_case_id: Id class — the reference number of the payoff case, as returned by the payoff case lookup.
        payoff_request_id: Id class — the reference number of the payoff statement request on file that this write
            answers, as returned by the payoff submission lookup.
        maturity_case_id: Id class — the reference number of the loan's maturity case, as returned by the maturity
            case lookup.
        per_diem_amount: Fixed-format class — the daily accrual to record, in USD with 2 decimal places, rounded
            half up to the cent.

    Returns:
        A confirmation string naming the payoff case, statement request and maturity case reference numbers and the
        daily accrual now recorded (USD, 2 decimal places); the words "daily accrual recorded" indicate the write
        completed.
    """
    amt = round(float(per_diem_amount), 2)
    ctx.update("payoff_cases", payoff_case_id, per_diem_amount=amt)
    return (f"Payoff case {payoff_case_id} (request {payoff_request_id}, maturity case {maturity_case_id}): "
            f"daily accrual recorded at {amt:.2f}.")


@tool(owner="agent", rw="write")
def issue_sale_payoff_statement_764045f1(ctx: ToolContext, payoff_case_id: str, payoff_request_id: str,
                                         maturity_case_id: str, statement_good_through_date: str,
                                         statement_balance: float) -> str:
    """Issue the payoff statement on a borrower's short-sale payoff case, moving the case from opened to
    terms_issued.

    The statement is dated today. The case records the statement date, the good-through date and the statement
    balance passed in. The daily accrual, required payoff amount, contract price, allowed closing costs, appraised
    value basis and funds held are left unchanged; the statement request and maturity case named are quoted back in
    the receipt. On success the case shows status terms_issued with the statement figures.

    Args:
        payoff_case_id: Id class — the reference number of the payoff case the statement is issued on, as returned
            by the payoff case lookup.
        payoff_request_id: Id class — the reference number of the payoff statement request on file that this write
            answers, as returned by the payoff submission lookup.
        maturity_case_id: Id class — the reference number of the loan's maturity case, as returned by the maturity
            case lookup.
        statement_good_through_date: Fixed-format class — the last calendar day the statement's figures are good,
            written YYYY-MM-DD in the servicer's local calendar.
        statement_balance: Fixed-format class — the loan balance projected to the good-through date, in USD with 2
            decimal places, rounded half up to the cent.

    Returns:
        A confirmation string naming the payoff case, statement request and maturity case reference numbers, the
        status terms_issued, the statement date and good-through date (YYYY-MM-DD) and the statement balance (USD,
        2 decimal places). The status terms_issued in the receipt indicates the statement was issued.
    """
    today = ctx.now()[:10]
    bal = round(float(statement_balance), 2)
    ctx.update("payoff_cases", payoff_case_id, status="terms_issued", statement_date=today,
               statement_good_through_date=statement_good_through_date, statement_balance=bal)
    return (f"Payoff case {payoff_case_id} (request {payoff_request_id}, maturity case {maturity_case_id}): "
            f"status terms_issued; statement date {today}, good through {statement_good_through_date}; "
            f"statement balance {bal:.2f}.")


@tool(owner="agent", rw="write")
def approve_sale_closing_costs_11c6cfd9(ctx: ToolContext, payoff_case_id: str, payoff_request_id: str,
                                        maturity_case_id: str, contract_price: float,
                                        allowed_closing_costs: float, required_payoff_amount: float,
                                        appraised_value_basis: float) -> str:
    """Approve the short-sale terms on a borrower's short-sale payoff case from the purchase contract submission
    named: the submission is marked accepted and the case records the contract price, the allowed closing costs,
    the required payoff amount and the appraised value basis passed in.

    The case's status, statement date, good-through date, statement balance, daily accrual and funds held are left
    unchanged. On success the case shows the approved contract figures and the amount the sale must deliver, and
    the submission shows status accepted.

    Args:
        payoff_case_id: Id class — the reference number of the payoff case, as returned by the payoff case lookup.
        payoff_request_id: Id class — the reference number of the purchase contract submission being approved, as
            returned by the payoff submission lookup.
        maturity_case_id: Id class — the reference number of the loan's maturity case whose appraisal the terms rely
            on, as returned by the maturity case lookup.
        contract_price: Fixed-format class — the purchase price on the approved contract, in USD with 2 decimal
            places, rounded half up to the cent.
        allowed_closing_costs: Fixed-format class — the seller closing costs approved to come out of the price, in
            USD with 2 decimal places, rounded half up to the cent.
        required_payoff_amount: Fixed-format class — the amount the sale must deliver to satisfy the loan, in USD
            with 2 decimal places, rounded half up to the cent.
        appraised_value_basis: Fixed-format class — the as-is appraised value the terms rely on, in USD with 2
            decimal places, rounded half up to the cent.

    Returns:
        A confirmation string naming the payoff case, submission and maturity case reference numbers, the
        submission status accepted, the contract price, the allowed closing costs, the required payoff amount and
        the appraised value basis (USD, 2 decimal places); the word "approved" indicates the write completed.
    """
    price = round(float(contract_price), 2)
    allowed = round(float(allowed_closing_costs), 2)
    req = round(float(required_payoff_amount), 2)
    basis = round(float(appraised_value_basis), 2)
    ctx.update("payoff_requests", payoff_request_id, request_status="accepted")
    ctx.update("payoff_cases", payoff_case_id, contract_price=price, allowed_closing_costs=allowed,
               required_payoff_amount=req, appraised_value_basis=basis)
    return (f"Payoff case {payoff_case_id} (submission {payoff_request_id} accepted, maturity case "
            f"{maturity_case_id}): short sale approved at contract price {price:.2f} with allowed closing costs "
            f"{allowed:.2f}; required payoff amount {req:.2f}; appraised value basis {basis:.2f}.")


@tool(owner="user", rw="write")
def remit_seller_closing_shortfall_d501bd8d(ctx: ToolContext, payoff_case_id: str, remittance_method: str,
                                         remitter_name: str, amount: float) -> str:
    """Send the seller's own closing contribution, in the customer's own name, to the payoff case of a home being
    sold, recorded as one receipt that the case holds until the loan is satisfied.

    The receipt is dated today, carries the method, sender name and amount given, and receives a newly issued
    remittance reference. The amount is added to the funds the case holds. On success the customer can see the
    receipt on the case and quote its remittance reference.

    Args:
        payoff_case_id: Id class — the reference number of the payoff case the funds are sent to, as given by the
            servicer.
        remittance_method: Enum class — how the funds are sent: wire (a bank wire transfer to the servicer's payoff
            account); cashiers_check (a cashier's check delivered to the servicer); check (a check the servicer itself
            issues when it pays money out, never used for funds a customer sends); not_applicable (an entry where no
            cash moves, never used for funds a customer sends).
        remitter_name: Verbatim class — the sender's full name exactly as the customer states it for the funds, copied
            character for character (verbatim).
        amount: Fixed-format class — the amount sent, in USD with 2 decimal places, rounded half up to the cent.

    Returns:
        A confirmation string naming the payoff case reference number, the receipt reference number, the issued
        remittance reference (text), the method, the sender name and the amount (USD, 2 decimal places), and the
        funds now held on the case (USD, 2 decimal places); the word "received" indicates the funds were recorded.
    """
    amt = round(float(amount), 2)
    case = ctx.find("payoff_cases", payoff_case_id=payoff_case_id)
    cust = case[0].get("customer_id", "") if case else ""
    held = round(float(case[0].get("funds_held") or 0) + amt, 2) if case else amt
    rid = ctx.make_id("ptx_", payoff_case_id, remittance_method, remitter_name, amt)
    ref = "CSS-" + rid[-8:].upper()
    today = ctx.now()[:10]
    ctx.create("payoff_transactions", rid, payoff_txn_id=rid, payoff_case_id=payoff_case_id, customer_id=cust,
               event_type="payoff_funds_received", amount=amt, effective_date=today,
               remittance_method=remittance_method, remittance_reference=ref, remitter_name=remitter_name,
               source_txn_ref="")
    ctx.update("payoff_cases", payoff_case_id, funds_held=held)
    return (f"Payoff case {payoff_case_id}: funds received, receipt {rid}, remittance reference {ref}, "
            f"{remittance_method} from {remitter_name}, amount {amt:.2f}; funds held {held:.2f}.")

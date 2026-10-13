"""Hidden task tools of the whole_life_loans_dividends_and_values difficulty (Ashgrove whole life).

Each tool performs exactly one atomic write already decided by the agent (or, for an owner=user
tool, by the policy owner at the agent's hand-over). No tool validates eligibility, prerequisites
or amounts: every value passed in is the one the published policy computes.
"""

from erlbench import ToolContext, tool


@tool(owner="agent", rw="write")
def capitalize_loan_interest_55a34971(ctx: ToolContext, whole_policy_id: str, interest_period_end: str,
                                      interest_amount: float) -> str:
    """Capitalize the unpaid policy loan interest of one Ashgrove whole life policy into its loan principal for the interest period that a policy anniversary closes. One call books a single capitalization entry dated that anniversary on the policy's activity history and raises the policy's loan balance by exactly the interest amount given; the interest paid-to date shown on the policy is left as it stands. On success the new entry appears in the policy activity and the higher loan balance on the policy record. The call has succeeded when the receipt below comes back with a capitalization reference.

    Args:
        whole_policy_id: Id class — the reference number of the whole life policy whose loan interest is capitalized, as returned by the whole life policy lookup for the verified owner.
        interest_period_end: Fixed-format class — the policy anniversary that closes the interest period being capitalized, written YYYY-MM-DD (a calendar date, no time or time zone); it also becomes the date of the entry.
        interest_amount: Fixed-format class — the unpaid loan interest added to the loan principal, in USD, 2 decimal places, rounded half up to the cent before it is passed.

    Returns:
        A dictionary rendered as text with: capitalization_id (text, the reference of the new capitalization entry), whole_policy_id (text, the policy reference), interest_period_end (YYYY-MM-DD, the anniversary capitalized), interest_capitalized (USD, 2 decimal places, the amount added to principal) and loan_balance_after (USD, 2 decimal places, the policy loan balance including the capitalized interest). A receipt carrying a capitalization_id means the entry was booked.
    """
    amount = round(float(interest_amount), 2)
    rid = ctx.make_id("wcap_", whole_policy_id, interest_period_end, amount)
    ctx.create("whole_transactions", rid, whole_txn_id=rid, whole_policy_id=whole_policy_id,
               event_type="whole_loan_interest_capitalized", transaction_date=interest_period_end,
               amount=amount, interest_period_end=interest_period_end)
    rows = ctx.find("whole_holdings", whole_policy_id=whole_policy_id)
    balance = round(float((rows[0].get("loan_balance") if rows else 0) or 0) + amount, 2)
    if rows:
        ctx.update("whole_holdings", whole_policy_id, loan_balance=balance)
    return str({"capitalization_id": rid, "whole_policy_id": whole_policy_id,
                "interest_period_end": interest_period_end, "interest_capitalized": amount,
                "loan_balance_after": balance})


@tool(owner="agent", rw="write")
def extinguish_policy_loan_1349795c(ctx: ToolContext, whole_policy_id: str, offset_reason: str,
                                    principal_amount: float, interest_amount: float) -> str:
    """Extinguish the policy loan of one Ashgrove whole life policy against the policy's own values on the occasion that ends or converts the coverage. One call books a single loan offset entry dated today that records the loan principal and the accrued loan interest extinguished together, and lowers the policy's loan balance by the principal extinguished. On success the offset entry appears in the policy activity and the reduced loan balance on the policy record. The call has succeeded when the receipt below comes back with an offset reference.

    Args:
        whole_policy_id: Id class — the reference number of the whole life policy whose loan is extinguished, as returned by the whole life policy lookup for the verified owner.
        offset_reason: Enum class — the occasion of the offset, exactly one of: surrender — a loan extinguished when the policy is surrendered for cash, an occasion Ashgrove now settles inside the surrender payment, so the value appears only on older entries; death_claim — the settlement of a death claim on the insured; nonforfeiture — the policy going onto reduced paid-up or extended term insurance, by default or by the owner's election; loan_default — the termination of the policy because indebtedness reached its cash value.
        principal_amount: Fixed-format class — the loan principal extinguished, which is the whole loan balance shown on the policy including capitalized interest, in USD, 2 decimal places.
        interest_amount: Fixed-format class — the loan interest accrued and unpaid that is extinguished with the principal, in USD, 2 decimal places, rounded half up to the cent before it is passed.

    Returns:
        A dictionary rendered as text with: offset_id (text, the reference of the new offset entry), whole_policy_id (text, the policy reference), offset_reason (text, the occasion recorded), principal_extinguished (USD, 2 decimal places), interest_extinguished (USD, 2 decimal places), offset_date (YYYY-MM-DD, the date of the entry) and loan_balance_after (USD, 2 decimal places, the loan balance left on the policy). A receipt carrying an offset_id means the offset was booked.
    """
    principal = round(float(principal_amount), 2)
    interest = round(float(interest_amount), 2)
    today = ctx.now()[:10]
    rid = ctx.make_id("woff_", whole_policy_id, offset_reason, principal, interest)
    ctx.create("whole_transactions", rid, whole_txn_id=rid, whole_policy_id=whole_policy_id,
               event_type="whole_loan_offset", transaction_date=today, amount=principal,
               interest_amount=interest, offset_reason=offset_reason)
    rows = ctx.find("whole_holdings", whole_policy_id=whole_policy_id)
    balance = round(float((rows[0].get("loan_balance") if rows else 0) or 0) - principal, 2)
    if rows:
        ctx.update("whole_holdings", whole_policy_id, loan_balance=balance)
    return str({"offset_id": rid, "whole_policy_id": whole_policy_id, "offset_reason": offset_reason,
                "principal_extinguished": principal, "interest_extinguished": interest,
                "offset_date": today, "loan_balance_after": balance})


@tool(owner="agent", rw="write")
def withdraw_election_accumulations_2818c877(ctx: ToolContext, whole_policy_id: str,
                                             withdrawal_amount: float) -> str:
    """Withdraw the whole dividend accumulation deposit of one Ashgrove whole life policy so that it is applied, together with the policy's cash value, to the reduced paid-up insurance the owner is electing. One call books a single accumulation withdrawal entry dated today for the amount given and closes the policy's dividend accumulation balance to zero; no money is sent to the owner. On success the withdrawal entry appears in the policy activity and the policy record shows no dividend accumulations. The call has succeeded when the receipt below comes back with a withdrawal reference.

    Args:
        whole_policy_id: Id class — the reference number of the whole life policy whose accumulation deposit is withdrawn, as returned by the whole life policy lookup for the verified owner.
        withdrawal_amount: Fixed-format class — the total withdrawn from the accumulation deposit, including any interest for the part of the policy year it carries, in USD, 2 decimal places, rounded half up to the cent before it is passed.

    Returns:
        A dictionary rendered as text with: withdrawal_id (text, the reference of the new withdrawal entry), whole_policy_id (text, the policy reference), amount_withdrawn (USD, 2 decimal places), withdrawal_date (YYYY-MM-DD) and accumulation_balance_after (USD, 2 decimal places, always 0.00 once the deposit is closed). A receipt carrying a withdrawal_id means the withdrawal was booked.
    """
    amount = round(float(withdrawal_amount), 2)
    today = ctx.now()[:10]
    rid = ctx.make_id("wacw_", whole_policy_id, amount)
    ctx.create("whole_transactions", rid, whole_txn_id=rid, whole_policy_id=whole_policy_id,
               event_type="whole_accumulation_withdrawn", transaction_date=today, amount=amount)
    ctx.update("whole_holdings", whole_policy_id, dividend_accumulation_balance=0.00)
    return str({"withdrawal_id": rid, "whole_policy_id": whole_policy_id, "amount_withdrawn": amount,
                "withdrawal_date": today, "accumulation_balance_after": 0.00})


@tool(owner="user", rw="write")
def elect_reduced_paid_up_64725b60(ctx: ToolContext, whole_policy_id: str, effective_date: str,
                                   reduced_face_amount: float) -> str:
    """Record the policy owner's own election to stop paying premiums on their Ashgrove whole life policy and keep it as reduced paid-up insurance. One call, made by the owner, changes the policy from premium-paying to reduced paid-up status, sets the policy's face amount to the reduced paid-up face given, records reduced paid-up as the nonforfeiture option in effect and records the effective date of the election. On success the policy record shows the reduced paid-up status, the new face amount and the effective date, and no further premium is billed. The call has succeeded when the receipt below comes back with an election reference.

    Args:
        whole_policy_id: Id class — the reference number of the owner's whole life policy being converted to reduced paid-up insurance, which the agent reads to the owner from the whole life policy lookup.
        effective_date: Fixed-format class — the date the reduced paid-up insurance takes effect, written YYYY-MM-DD (a calendar date, no time or time zone).
        reduced_face_amount: Fixed-format class — the face amount of the reduced paid-up insurance, in USD, 2 decimal places (a whole-dollar face is written with .00).

    Returns:
        A dictionary rendered as text with: election_id (text, the reference of the recorded election), whole_policy_id (text, the policy reference), status (text, reduced_paid_up once recorded), reduced_face_amount (USD, 2 decimal places) and effective_date (YYYY-MM-DD). A receipt carrying an election_id and status reduced_paid_up means the election took effect.
    """
    face = round(float(reduced_face_amount), 2)
    rid = ctx.make_id("wrpu_", whole_policy_id, effective_date, face)
    ctx.update("whole_holdings", whole_policy_id, status="reduced_paid_up", face_amount=face,
               nonforfeiture_option="reduced_paid_up", default_date=effective_date)
    return str({"election_id": rid, "whole_policy_id": whole_policy_id, "status": "reduced_paid_up",
                "reduced_face_amount": face, "effective_date": effective_date})


@tool(owner="agent", rw="write")
def credit_accumulation_interest_b6da2e99(ctx: ToolContext, whole_policy_id: str, interest_period_end: str,
                                          interest_amount: float) -> str:
    """Credit the interest earned by the dividend accumulation deposit of one Ashgrove whole life policy for the policy year that a policy anniversary closes. One call books a single accumulation interest credit entry dated that anniversary on the policy's activity history and raises the policy's dividend accumulation balance by exactly the interest amount given. On success the credit entry appears in the policy activity and the higher accumulation balance on the policy record. The call has succeeded when the receipt below comes back with a credit reference.

    Args:
        whole_policy_id: Id class — the reference number of the whole life policy whose accumulation deposit earns the interest, as returned by the whole life policy lookup for the verified owner.
        interest_period_end: Fixed-format class — the policy anniversary closing the policy year the interest is for, written YYYY-MM-DD (a calendar date, no time or time zone); it also becomes the date of the entry.
        interest_amount: Fixed-format class — the interest credited to the accumulation deposit, in USD, 2 decimal places, rounded half up to the cent before it is passed.

    Returns:
        A dictionary rendered as text with: credit_id (text, the reference of the new credit entry), whole_policy_id (text, the policy reference), interest_period_end (YYYY-MM-DD), interest_credited (USD, 2 decimal places) and accumulation_balance_after (USD, 2 decimal places, the deposit including the credit). A receipt carrying a credit_id means the credit was booked.
    """
    amount = round(float(interest_amount), 2)
    rid = ctx.make_id("waic_", whole_policy_id, interest_period_end, amount)
    ctx.create("whole_transactions", rid, whole_txn_id=rid, whole_policy_id=whole_policy_id,
               event_type="whole_accumulation_interest_credited", transaction_date=interest_period_end,
               amount=amount, interest_period_end=interest_period_end)
    rows = ctx.find("whole_holdings", whole_policy_id=whole_policy_id)
    balance = round(float((rows[0].get("dividend_accumulation_balance") if rows else 0) or 0) + amount, 2)
    if rows:
        ctx.update("whole_holdings", whole_policy_id, dividend_accumulation_balance=balance)
    return str({"credit_id": rid, "whole_policy_id": whole_policy_id, "interest_period_end": interest_period_end,
                "interest_credited": amount, "accumulation_balance_after": balance})


@tool(owner="agent", rw="write")
def deposit_anniversary_dividend_704bd37e(ctx: ToolContext, whole_policy_id: str, anniversary_date: str,
                                          dividend_year: int, deposit_amount: float) -> str:
    """Place the anniversary dividend of one Ashgrove whole life policy on deposit with Ashgrove under the accumulate-at-interest dividend option. One call books a single dividend deposit entry dated the anniversary for the policy year given and raises the policy's dividend accumulation balance by exactly the deposit amount given; nothing is paid to the owner. On success the deposit entry appears in the policy activity and the higher accumulation balance on the policy record. The call has succeeded when the receipt below comes back with a deposit reference.

    Args:
        whole_policy_id: Id class — the reference number of the whole life policy whose dividend is placed on deposit, as returned by the whole life policy lookup for the verified owner.
        anniversary_date: Fixed-format class — the policy anniversary on which the dividend was declared, written YYYY-MM-DD (a calendar date, no time or time zone); it becomes the date of the entry.
        dividend_year: Fixed-format class — the policy year the dividend is paid for, an integer policy year counted from the issue date.
        deposit_amount: Fixed-format class — the amount placed on deposit, in USD, 2 decimal places, rounded half up to the cent before it is passed.

    Returns:
        A dictionary rendered as text with: deposit_id (text, the reference of the new deposit entry), whole_policy_id (text, the policy reference), dividend_year (integer policy year), amount_deposited (USD, 2 decimal places) and accumulation_balance_after (USD, 2 decimal places, the deposit balance including this dividend). A receipt carrying a deposit_id means the deposit was booked.
    """
    amount = round(float(deposit_amount), 2)
    rid = ctx.make_id("wdep_", whole_policy_id, anniversary_date, int(dividend_year), amount)
    ctx.create("whole_transactions", rid, whole_txn_id=rid, whole_policy_id=whole_policy_id,
               event_type="whole_dividend_accumulated", transaction_date=anniversary_date, amount=amount,
               dividend_year=int(dividend_year))
    rows = ctx.find("whole_holdings", whole_policy_id=whole_policy_id)
    balance = round(float((rows[0].get("dividend_accumulation_balance") if rows else 0) or 0) + amount, 2)
    if rows:
        ctx.update("whole_holdings", whole_policy_id, dividend_accumulation_balance=balance)
    return str({"deposit_id": rid, "whole_policy_id": whole_policy_id, "dividend_year": int(dividend_year),
                "amount_deposited": amount, "accumulation_balance_after": balance})


@tool(owner="user", rw="write")
def complete_policy_surrender_23994b0e(ctx: ToolContext, whole_policy_id: str, whole_request_id: str,
                                       effective_date: str, payout_method: str, net_amount: float) -> str:
    """Record the policy owner's own confirmation that releases their signed full surrender request on their Ashgrove whole life policy, ending the coverage and paying out the net cash surrender value. One call, made by the owner, changes the policy to surrendered status with the surrender effective date as its termination date, closes the dividend accumulation deposit to zero because it is paid out with the surrender, and books a single cash value payment entry for the net amount, linked to the surrender request and paid by the method given. On success the policy record shows the surrendered status and the payment entry appears in the policy activity. The call has succeeded when the receipt below comes back with a payment reference.

    Args:
        whole_policy_id: Id class — the reference number of the owner's whole life policy being surrendered, which the agent reads to the owner from the whole life policy lookup.
        whole_request_id: Id class — the reference number of the owner's signed surrender request on file, which the agent reads to the owner from the whole life service request lookup.
        effective_date: Fixed-format class — the date the surrender takes effect, written YYYY-MM-DD (a calendar date, no time or time zone).
        payout_method: Enum class — how the net amount is paid, exactly one of: check — a paper check mailed to the owner's address on file; direct_deposit — an electronic deposit to the owner's bank account on file; beneficiary_access_account — an Ashgrove Beneficiary Access Account, which applies to death proceeds only.
        net_amount: Fixed-format class — the net cash surrender value paid to the owner after any loan and tax withholding, in USD, 2 decimal places, rounded half up to the cent before it is passed.

    Returns:
        A dictionary rendered as text with: payment_id (text, the reference of the cash value payment entry), whole_policy_id (text, the policy reference), status (text, surrendered once recorded), effective_date (YYYY-MM-DD), payout_method (text, the method recorded) and net_amount_paid (USD, 2 decimal places). A receipt carrying a payment_id and status surrendered means the surrender was completed.
    """
    amount = round(float(net_amount), 2)
    rid = ctx.make_id("wsur_", whole_policy_id, whole_request_id, effective_date, payout_method, amount)
    ctx.update("whole_holdings", whole_policy_id, status="surrendered", termination_date=effective_date,
               dividend_accumulation_balance=0.00)
    ctx.create("whole_transactions", rid, whole_txn_id=rid, whole_policy_id=whole_policy_id,
               event_type="whole_cash_value_paid", transaction_date=ctx.now()[:10], amount=amount,
               distribution_reason="surrender", payout_method=payout_method, whole_request_id=whole_request_id)
    return str({"payment_id": rid, "whole_policy_id": whole_policy_id, "status": "surrendered",
                "effective_date": effective_date, "payout_method": payout_method, "net_amount_paid": amount})

"""Hidden task tools for regional_retail_bank / cd_maturity_withdrawals_and_renewals.

Each tool performs exactly one atomic certificate write with the values the caller supplies.
No tool checks a policy prerequisite, computes a policy amount or refuses on business grounds.
"""

from erlbench import ToolContext, tool


# Ledger fields that stay at their empty value unless an entry type uses them.
LEDGER_DEFAULTS = {"deposit_kind": "none", "funding_source": "none", "trace_number": "",
                   "counterparty_account_id": "", "interest_period": "", "rate_applied": "",
                   "destination": "none", "withdrawal_kind": "none", "source_item_id": "",
                   "penalty_days": "", "adjustment_reason": "none"}


@tool(owner="agent", rw="write")
def reverse_penalty_error_2ccc5de3(ctx: ToolContext, certificate_id: str, source_item_id: str,
                                   amount: float) -> str:
    """Credit an early withdrawal penalty back to a certificate of deposit as a bank-error correction.

    The agent posts one penalty reversal entry on the certificate, dated today, that points to the
    penalty entry being reversed and carries the adjustment reason bank_error. The amount credited
    is added to the certificate's principal balance at once, so the owner sees the credit in the
    certificate's activity and a higher principal balance right away. A successful call returns the
    receipt below; nothing else about the certificate changes.

    Args:
        certificate_id: Id class — the certificate reference number of the certificate that carries
            the penalty, as returned by the certificate lookup for this customer.
        source_item_id: Id class — the entry reference number of the early withdrawal penalty entry
            being credited back, as returned by the certificate activity lookup.
        amount: Fixed-format class — the amount credited back to principal; unit USD, 2 decimal
            places, a positive number rounded half-up to the cent.

    Returns:
        A dictionary rendered as text with: reversal_id (entry reference number of the new penalty
        reversal entry), certificate_id (the certificate credited), source_item_id (the penalty
        entry it reverses), amount (USD credited, 2 decimal places), posted_date (YYYY-MM-DD, today)
        and principal_balance (the certificate's new principal in USD, 2 decimal places). A receipt
        carrying a reversal_id means the credit is posted.
    """
    cert = ctx.find("cd_certificates", certificate_id=certificate_id)[0]
    amt = round(float(amount), 2)
    rid = ctx.make_id("cdr_", certificate_id, source_item_id, amt)
    posted = ctx.now()[:10]
    ctx.create("cd_transactions", rid, **{**LEDGER_DEFAULTS, **dict(
        cd_txn_id=rid, certificate_id=certificate_id, customer_id=cert["customer_id"],
        event_type="cd_penalty_reversal", amount=amt, posted_date=posted,
        source_item_id=source_item_id, adjustment_reason="bank_error")})
    new_balance = round(float(cert["principal_balance"]) + amt, 2)
    ctx.update("cd_certificates", certificate_id, principal_balance=new_balance)
    return str({"reversal_id": rid, "certificate_id": certificate_id, "source_item_id": source_item_id,
                "amount": amt, "posted_date": posted, "principal_balance": new_balance})


@tool(owner="agent", rw="write")
def update_maturity_instruction_96ab509d(ctx: ToolContext, certificate_id: str, renewal_instruction: str,
                                         payout_account_id: str) -> str:
    """Record a new maturity instruction and payout account on a certificate of deposit.

    The agent replaces what the certificate does when its grace period ends (renew automatically,
    pay the balance to checking or savings, or mail an official check) and the PCB account named as
    the certificate's payout account. The certificate's interest disposition is left as it is. The
    change is visible at once on the certificate record. A successful call returns the receipt below.

    Args:
        certificate_id: Id class — the certificate reference number whose instruction changes, as
            returned by the certificate lookup for this customer.
        renewal_instruction: Enum class — the new maturity instruction; one of: auto_renew (the
            certificate renews into its renewal tier when the grace period ends), pay_out_to_checking
            (the whole balance is paid to the payout checking account when the grace period ends),
            pay_out_to_savings (the whole balance is paid to the payout savings account when the
            grace period ends), mail_check (the whole balance is paid by official check mailed to the
            address on file when the grace period ends).
        payout_account_id: Id class — the account reference number of the customer's own PCB
            checking or savings account to record as the payout account, as returned by the
            checking or savings account lookup.

    Returns:
        A dictionary rendered as text with: certificate_id (the certificate updated),
        renewal_instruction (the instruction now on record), payout_account_id (the payout account
        now on record) and recorded_at (the moment of the change, exactly as the system clock reads).
        A receipt echoing the new instruction means the change is recorded.
    """
    ctx.update("cd_certificates", certificate_id, renewal_instruction=renewal_instruction,
               payout_account_id=payout_account_id)
    return str({"certificate_id": certificate_id, "renewal_instruction": renewal_instruction,
                "payout_account_id": payout_account_id, "recorded_at": ctx.now()})


@tool(owner="agent", rw="write")
def renew_certificate_term_21cb639a(ctx: ToolContext, certificate_id: str, variant_name: str,
                                    term_start_date: str, maturity_date: str, interest_rate: float,
                                    apy: float, jumbo_bonus_applied: bool,
                                    relationship_bonus_applied: bool) -> str:
    """Book a new term on a certificate of deposit that has reached maturity.

    The agent starts the certificate's next term: the certificate becomes active again in the tier
    given, with the new term's start and maturity dates, the rate and APY fixed for the new term,
    and the two bonus markers for that term. The one bump-up allowed per term is made available
    again and the certificate's renewal count goes up by one. The principal balance is not touched.
    The new term shows on the certificate record at once. A successful call returns the receipt
    below.

    Args:
        certificate_id: Id class — the certificate reference number being renewed, as returned by
            the certificate lookup for this customer.
        variant_name: Enum class — the tier of the new term; one of: 6-Month Certificate (the new
            term is a 6-Month Certificate), 11-Month No-Penalty Certificate (the new term is an
            11-Month No-Penalty Certificate), 12-Month Certificate (the new term is a 12-Month
            Certificate), 18-Month Bump-Up Certificate (the new term is an 18-Month Bump-Up
            Certificate), 36-Month Certificate (the new term is a 36-Month Certificate), 60-Month
            Certificate (the new term is a 60-Month Certificate).
        term_start_date: Fixed-format class — first day of the new term, as a calendar date in the
            form YYYY-MM-DD (never empty).
        maturity_date: Fixed-format class — the maturity date of the new term, the calendar date on
            which the new term matures, in the form YYYY-MM-DD (never empty).
        interest_rate: Fixed-format class — the annual interest rate of the new term, bonuses
            included; unit percent, 2 decimal places, e.g. 3.97 means 3.97 percent.
        apy: Fixed-format class — the annual percentage yield of the new term, bonuses included;
            unit percent, 2 decimal places, e.g. 4.05 means 4.05 percent.
        jumbo_bonus_applied: Enum class — whether the jumbo bonus is part of the new term's rate;
            allowed values are true (the new term's rate includes the jumbo bonus) and false (the
            new term's rate does not include the jumbo bonus).
        relationship_bonus_applied: Enum class — whether the relationship bonus is part of the new
            term's rate; one of: true (the new term's rate includes the relationship bonus), false
            (the new term's rate does not include the relationship bonus).

    Returns:
        A dictionary rendered as text with: certificate_id (the certificate renewed), status (active),
        variant_name (tier of the new term), term_start_date and maturity_date (YYYY-MM-DD),
        interest_rate and apy (percent, 2 decimal places), jumbo_bonus_applied and
        relationship_bonus_applied (true or false) and renewal_count (the certificate's renewal count
        after this renewal, an integer). A receipt with status active means the new term is booked.
    """
    cert = ctx.find("cd_certificates", certificate_id=certificate_id)[0]
    count = int(cert.get("renewal_count") or 0) + 1
    rate, yld = round(float(interest_rate), 2), round(float(apy), 2)
    ctx.update("cd_certificates", certificate_id, status="active", variant_name=variant_name,
               term_start_date=term_start_date, maturity_date=maturity_date, interest_rate=rate,
               apy=yld, jumbo_bonus_applied=bool(jumbo_bonus_applied),
               relationship_bonus_applied=bool(relationship_bonus_applied), bump_up_used=False,
               renewal_count=count)
    return str({"certificate_id": certificate_id, "status": "active", "variant_name": variant_name,
                "term_start_date": term_start_date, "maturity_date": maturity_date, "interest_rate": rate,
                "apy": yld, "jumbo_bonus_applied": bool(jumbo_bonus_applied),
                "relationship_bonus_applied": bool(relationship_bonus_applied), "renewal_count": count})


@tool(owner="user", rw="write")
def add_term_deposit_5f936ecf(ctx: ToolContext, customer_id: str, certificate_id: str, amount: float,
                              funding_source: str, counterparty_account_id: str) -> str:
    """Add new principal to an active certificate of deposit during its term, on the owner's own instruction.

    The owner moves money into the certificate as an in-term add-on deposit dated today. One add-on
    deposit entry is posted on the certificate with its funding source and a newly assigned
    15-digit posting trace number, and the amount is added to the certificate's principal balance
    at once; the maturity date and the rate of the term stay as they are. A successful call returns
    the receipt below.

    Args:
        customer_id: Id class — the customer reference number of the certificate's owner, as the
            agent read it from the customer profile lookup and passed it on.
        certificate_id: Id class — the certificate reference number receiving the add-on, as the
            agent read it from the certificate lookup and passed it on.
        amount: Fixed-format class — the amount deposited; unit USD, 2 decimal places, always
            positive.
        funding_source: Enum class — where the money comes from; one of: none (not used for a
            deposit), pcb_checking (an internal transfer from the owner's PCB checking account),
            pcb_savings (an internal transfer from the owner's PCB savings or money market account),
            external_ach (an ACH transfer from an account at another bank), check (a check deposited
            to the certificate), cash (cash deposited at a branch), wire (an incoming wire transfer).
        counterparty_account_id: Id class — the account reference number of the owner's PCB checking
            or savings account the money comes from for an internal transfer, as returned by the
            checking or savings account lookup; empty string for any other funding source.

    Returns:
        A dictionary rendered as text with: deposit_id (entry reference number of the add-on
        deposit), certificate_id (the certificate credited), amount (USD, 2 decimal places),
        posted_date (YYYY-MM-DD, today), trace_number (the 15-digit posting trace number) and
        principal_balance (the certificate's new principal in USD, 2 decimal places). A receipt
        carrying a deposit_id means the add-on is posted.
    """
    cert = ctx.find("cd_certificates", certificate_id=certificate_id)[0]
    amt = round(float(amount), 2)
    rid = ctx.make_id("cdd_", customer_id, certificate_id, amt, funding_source, counterparty_account_id)
    trace = "3" + str(int(ctx.make_id("", rid, length=16), 16))[:14].rjust(14, "0")
    posted = ctx.now()[:10]
    ctx.create("cd_transactions", rid, **{**LEDGER_DEFAULTS, **dict(
        cd_txn_id=rid, certificate_id=certificate_id, customer_id=customer_id,
        event_type="cd_deposit", amount=amt, posted_date=posted, deposit_kind="term_add_on",
        funding_source=funding_source, trace_number=trace,
        counterparty_account_id=counterparty_account_id)})
    new_balance = round(float(cert["principal_balance"]) + amt, 2)
    ctx.update("cd_certificates", certificate_id, principal_balance=new_balance)
    return str({"deposit_id": rid, "certificate_id": certificate_id, "amount": amt, "posted_date": posted,
                "trace_number": trace, "principal_balance": new_balance})


@tool(owner="agent", rw="write")
def reverse_grace_penalty_e6d62385(ctx: ToolContext, certificate_id: str, source_item_id: str,
                                   amount: float) -> str:
    """Credit back to a certificate of deposit a penalty that was charged on money taken out during a grace period.

    The agent posts one penalty reversal entry on the certificate, dated today, that points to the
    penalty entry being credited back and carries the adjustment reason bank_error. The amount is
    added to the certificate's principal balance at once, so the owner sees the credit in the
    certificate's activity and a higher principal balance right away. A successful call returns the
    receipt below; nothing else about the certificate changes.

    Args:
        certificate_id: Id class — the certificate reference number of the certificate that carries
            the penalty, as returned by the certificate lookup for this customer.
        source_item_id: Id class — the entry reference number of the penalty entry being credited
            back, as returned by the certificate activity lookup.
        amount: Fixed-format class — the amount credited back to principal; unit USD, 2 decimal
            places, a positive number rounded half-up to the cent.

    Returns:
        A dictionary rendered as text with: reversal_id (entry reference number of the new penalty
        reversal entry), certificate_id (the certificate credited), source_item_id (the penalty
        entry credited back), amount (USD credited, 2 decimal places), posted_date (YYYY-MM-DD,
        today) and principal_balance (the certificate's new principal in USD, 2 decimal places). A
        receipt carrying a reversal_id means the credit is posted.
    """
    cert = ctx.find("cd_certificates", certificate_id=certificate_id)[0]
    amt = round(float(amount), 2)
    rid = ctx.make_id("cdg_", certificate_id, source_item_id, amt)
    posted = ctx.now()[:10]
    ctx.create("cd_transactions", rid, **{**LEDGER_DEFAULTS, **dict(
        cd_txn_id=rid, certificate_id=certificate_id, customer_id=cert["customer_id"],
        event_type="cd_penalty_reversal", amount=amt, posted_date=posted,
        source_item_id=source_item_id, adjustment_reason="bank_error")})
    new_balance = round(float(cert["principal_balance"]) + amt, 2)
    ctx.update("cd_certificates", certificate_id, principal_balance=new_balance)
    return str({"reversal_id": rid, "certificate_id": certificate_id, "source_item_id": source_item_id,
                "amount": amt, "posted_date": posted, "principal_balance": new_balance})


@tool(owner="agent", rw="write")
def update_interest_disposition_67b383bc(ctx: ToolContext, certificate_id: str, interest_disposition: str,
                                        payout_account_id: str) -> str:
    """Record where a certificate of deposit's credited interest goes and which PCB account receives it.

    The agent replaces the certificate's interest disposition and the PCB account named as its
    payout account. The maturity instruction is left as it is. The change takes effect from the
    next interest crediting date and is visible on the certificate record at once. A successful
    call returns the receipt below.

    Args:
        certificate_id: Id class — the certificate reference number whose interest disposition
            changes, as returned by the certificate lookup for this customer.
        interest_disposition: Enum class — where credited interest goes; one of: compound (interest
            is added to the certificate's principal), pay_to_checking (interest is paid to the
            payout checking account), pay_to_savings (interest is paid to the payout savings
            account).
        payout_account_id: Id class — the account reference number of the customer's own PCB
            checking or savings account to record as the payout account, as returned by the
            checking or savings account lookup.

    Returns:
        A dictionary rendered as text with: certificate_id (the certificate updated),
        interest_disposition (the disposition now on record), payout_account_id (the payout account
        now on record) and recorded_at (the moment of the change, exactly as the system clock reads).
        A receipt echoing the new disposition means the change is recorded.
    """
    ctx.update("cd_certificates", certificate_id, interest_disposition=interest_disposition,
               payout_account_id=payout_account_id)
    return str({"certificate_id": certificate_id, "interest_disposition": interest_disposition,
                "payout_account_id": payout_account_id, "recorded_at": ctx.now()})


@tool(owner="user", rw="write")
def add_grace_deposit_522b16cc(ctx: ToolContext, customer_id: str, certificate_id: str, amount: float,
                               funding_source: str, counterparty_account_id: str) -> str:
    """Add new principal to a matured certificate of deposit during its grace period, on the owner's own instruction.

    The owner moves money into the certificate as a grace-period add-on deposit dated today. One
    grace add-on deposit entry is posted on the certificate with its funding source and a newly
    assigned 15-digit posting trace number, and the amount is added to the certificate's principal
    balance at once; the certificate stays in its grace period. A successful call returns the
    receipt below.

    Args:
        customer_id: Id class — the customer reference number of the certificate's owner, as the
            agent read it from the customer profile lookup and passed it on.
        certificate_id: Id class — the certificate reference number receiving the add-on, as the
            agent read it from the certificate lookup and passed it on.
        amount: Fixed-format class — the amount deposited; unit USD, 2 decimal places, always
            positive.
        funding_source: Enum class — where the money comes from; one of: none (not used for a
            deposit), pcb_checking (an internal transfer from the owner's PCB checking account),
            pcb_savings (an internal transfer from the owner's PCB savings or money market account),
            external_ach (an ACH transfer from an account at another bank), check (a check deposited
            to the certificate), cash (cash deposited at a branch), wire (an incoming wire transfer).
        counterparty_account_id: Id class — the account reference number of the owner's PCB checking
            or savings account the money comes from for an internal transfer, as returned by the
            checking or savings account lookup; empty string for any other funding source.

    Returns:
        A dictionary rendered as text with: deposit_id (entry reference number of the grace add-on
        deposit), certificate_id (the certificate credited), amount (USD, 2 decimal places),
        posted_date (YYYY-MM-DD, today), trace_number (the 15-digit posting trace number) and
        principal_balance (the certificate's new principal in USD, 2 decimal places). A receipt
        carrying a deposit_id means the add-on is posted.
    """
    cert = ctx.find("cd_certificates", certificate_id=certificate_id)[0]
    amt = round(float(amount), 2)
    rid = ctx.make_id("cdga_", customer_id, certificate_id, amt, funding_source, counterparty_account_id)
    trace = "3" + str(int(ctx.make_id("", rid, length=16), 16))[:14].rjust(14, "0")
    posted = ctx.now()[:10]
    ctx.create("cd_transactions", rid, **{**LEDGER_DEFAULTS, **dict(
        cd_txn_id=rid, certificate_id=certificate_id, customer_id=customer_id,
        event_type="cd_deposit", amount=amt, posted_date=posted, deposit_kind="grace_add_on",
        funding_source=funding_source, trace_number=trace,
        counterparty_account_id=counterparty_account_id)})
    new_balance = round(float(cert["principal_balance"]) + amt, 2)
    ctx.update("cd_certificates", certificate_id, principal_balance=new_balance)
    return str({"deposit_id": rid, "certificate_id": certificate_id, "amount": amt, "posted_date": posted,
                "trace_number": trace, "principal_balance": new_balance})

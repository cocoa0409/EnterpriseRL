"""Hidden task tools for env_0066_captive_auto_finance_company / preowned_repossession_recovery.

Each tool performs one atomic write on a Kestrel Pre-Owned Retail Installment Sale Contract. Tools take
the figures the servicing agent has worked out and record them as given; they judge no eligibility.
"""

from erlbench import ToolContext, tool


class _Cal:
    """Pure calendar arithmetic on 'YYYY-MM-DD' strings (proleptic Gregorian ordinal days)."""

    @staticmethod
    def to_ordinal(day: str) -> int:
        y, m, d = (int(x) for x in str(day)[:10].split("-"))
        y2 = y - 1
        days_before_year = y2 * 365 + y2 // 4 - y2 // 100 + y2 // 400
        cum = [0, 31, 59, 90, 120, 151, 181, 212, 243, 273, 304, 334]
        leap = (y % 4 == 0 and y % 100 != 0) or (y % 400 == 0)
        return days_before_year + cum[m - 1] + (1 if (leap and m > 2) else 0) + d

    @staticmethod
    def from_ordinal(n: int) -> str:
        y = 1
        while _Cal.to_ordinal(f"{y + 400:04d}-01-01") <= n:
            y += 400
        while _Cal.to_ordinal(f"{y + 1:04d}-01-01") <= n:
            y += 1
        m = 1
        while m < 12 and _Cal.to_ordinal(f"{y:04d}-{m + 1:02d}-01") <= n:
            m += 1
        d = n - _Cal.to_ordinal(f"{y:04d}-{m:02d}-01") + 1
        return f"{y:04d}-{m:02d}-{d:02d}"

    @staticmethod
    def add_days(day: str, n: int) -> str:
        return _Cal.from_ordinal(_Cal.to_ordinal(day) + int(n))

    @staticmethod
    def weekday(day: str) -> int:
        """0 = Monday ... 6 = Sunday."""
        return (_Cal.to_ordinal(day) - 1) % 7

    @staticmethod
    def posting_date(day: str) -> str:
        """The business day a payment received on `day` posts: a Saturday or Sunday moves to the Monday."""
        wd = _Cal.weekday(day)
        return _Cal.add_days(day, 7 - wd) if wd >= 5 else str(day)[:10]

    @staticmethod
    def add_months(day: str, n: int) -> str:
        y, m, d = (int(x) for x in str(day)[:10].split("-"))
        k = (y * 12 + (m - 1)) + int(n)
        return f"{k // 12:04d}-{k % 12 + 1:02d}-{min(d, 28):02d}"


@tool(owner="agent", rw="write")
def book_recovery_transport_6b5d55b7(ctx: ToolContext, preowned_contract_id: str, amount: float,
                                     service_date: str) -> str:
    """Book the transport charge for an involuntary recovery of a vehicle financed under a Kestrel Pre-Owned Retail
    Installment Sale Contract: one repossession expense of the transport kind, dated with the stated service date. On
    success the contract's posting history gains one transport charge for the stated amount and the contract's fees
    due balance rises by that amount; the customer sees the charge on the account and in any figure that includes fees
    due. The charge is recorded exactly as given.

    Args:
        preowned_contract_id: Id class — the reference number of the pre-owned contract the charge is booked to, as returned by the pre-owned contract lookup for this customer.
        amount: Fixed-format class — the transport charge in US dollars, a positive number with 2 decimal places, rounded half-up to the cent.
        service_date: Fixed-format class — the date the charge is dated with, in the format YYYY-MM-DD.

    Returns:
        A confirmation string naming the new transaction reference (an opaque id beginning with "ptx_"), the contract
        reference, the booked amount in US dollars with 2 decimals, the date the charge is dated with (YYYY-MM-DD) and
        the new fees due balance in US dollars with 2 decimals; the presence of the transaction reference indicates the
        charge was booked.
    """
    rows = ctx.find("preowned_contracts", preowned_contract_id=preowned_contract_id)
    contract = rows[0] if rows else {}
    amt = round(float(amount), 2)
    dated = str(service_date)[:10]
    rid = ctx.make_id("ptx_", preowned_contract_id, amount, service_date)
    ctx.create("preowned_transactions", rid, preowned_txn_id=rid, preowned_contract_id=preowned_contract_id,
               customer_id=contract.get("customer_id", ""), event_type="preowned_repo_expense", txn_date=dated,
               amount=amt, fee_type="transport_fee", service_days=0, payment_channel="not_applicable",
               payment_purpose="not_applicable", return_reason="not_applicable", waiver_reason="not_applicable",
               quote_purpose="not_applicable", release_method="not_applicable", release_recipient="not_applicable",
               mailing_address_type="not_applicable", notice_type="not_applicable",
               property_release_type="not_applicable")
    new_fees = round(float(contract.get("fees_due_balance") or 0) + amt, 2)
    ctx.update("preowned_contracts", preowned_contract_id, fees_due_balance=new_fees)
    return (f"Transport charge {rid} booked to contract {preowned_contract_id}: {amt:.2f} USD dated {dated}; "
            f"fees due balance now {new_fees:.2f} USD.")


@tool(owner="agent", rw="write")
def quote_deficiency_balance_4c162eac(ctx: ToolContext, preowned_contract_id: str, amount: float) -> str:
    """Issue a deficiency payoff quote to the customer on a Kestrel Pre-Owned Retail Installment Sale Contract whose
    repossessed vehicle has been sold. On success one payoff quote for the customer is recorded on the contract, dated
    today, with the stated amount and a good-through date ten calendar days from today; balances and status do not
    change. The customer can be told the quoted amount and the good-through date from the receipt.

    Args:
        preowned_contract_id: Id class — the reference number of the pre-owned contract being quoted, as returned by the pre-owned contract lookup for this customer.
        amount: Fixed-format class — the quoted deficiency amount in US dollars, a positive number with 2 decimal places, rounded half-up to the cent.

    Returns:
        A confirmation string naming the quote reference (an opaque id beginning with "pqt_"), the contract reference,
        the quoted amount in US dollars with 2 decimals, the quote date and the good-through date (both YYYY-MM-DD); the
        presence of the quote reference indicates the quote was recorded.
    """
    rows = ctx.find("preowned_contracts", preowned_contract_id=preowned_contract_id)
    contract = rows[0] if rows else {}
    amt = round(float(amount), 2)
    today = ctx.now()[:10]
    good_through = _Cal.add_days(today, 10)
    rid = ctx.make_id("pqt_", preowned_contract_id, amount)
    ctx.create("preowned_transactions", rid, preowned_txn_id=rid, preowned_contract_id=preowned_contract_id,
               customer_id=contract.get("customer_id", ""), event_type="preowned_payoff_quote", txn_date=today,
               amount=amt, quote_good_through_date=good_through, per_diem=0.0, quote_purpose="customer_payoff",
               payment_channel="not_applicable", payment_purpose="not_applicable", return_reason="not_applicable",
               fee_type="not_applicable", waiver_reason="not_applicable", release_method="not_applicable",
               release_recipient="not_applicable", mailing_address_type="not_applicable",
               notice_type="not_applicable", property_release_type="not_applicable", service_days=0)
    return (f"Deficiency quote {rid} on contract {preowned_contract_id}: {amt:.2f} USD, quoted {today}, "
            f"good through {good_through}.")



@tool(owner="user", rw="write")
def remit_deficiency_settlement_2e6b8900(ctx: ToolContext, preowned_contract_id: str, amount: float,
                                         funding_account_last4: str) -> str:
    """Pay a lump-sum deficiency settlement on your own Kestrel Pre-Owned Retail Installment Sale Contract from your
    own bank account by bank wire transfer. On success one settlement payment is posted to the contract for the stated
    amount, dated with the posting date (the day the wire is sent, or the Monday when it is sent on a Saturday or
    Sunday), split in the contract's payment allocation order into the simple interest accrued through the posting
    date, principal and fees due, and the contract is marked paid in full as of the posting date, with the principal
    and fees due it no longer owes closed to zero. You see the payment reference and the paid-in-full status on the receipt.

    Args:
        preowned_contract_id: Id class — the reference number of your pre-owned contract, as given to you by the servicing agent from the contract lookup.
        amount: Fixed-format class — the settlement amount in US dollars, a positive number with 2 decimal places, rounded half-up to the cent, exactly as the agent states it.
        funding_account_last4: Fixed-format class — the last four digits of the bank account the payment is drawn from, in the format 4 digits, or empty (never empty for this payment), as printed on your own bank records.

    Returns:
        A confirmation string naming the payment reference (an opaque id beginning with "ppm_"), the contract reference,
        the amount paid in US dollars with 2 decimals, the interest, principal and fees portions in US dollars with 2
        decimals, the channel "wire", the posting date (YYYY-MM-DD), the funding account's last four digits and the contract status
        "paid_in_full"; the presence of the payment reference indicates the payment posted.
    """
    rows = ctx.find("preowned_contracts", preowned_contract_id=preowned_contract_id)
    contract = rows[0] if rows else {}
    amt = round(float(amount), 2)
    today = _Cal.posting_date(ctx.now()[:10])
    principal = float(contract.get("principal_balance") or 0)
    fees = float(contract.get("fees_due_balance") or 0)
    paid_to = str(contract.get("interest_paid_to_date") or today)[:10]
    days = max(0, _Cal.to_ordinal(today) - _Cal.to_ordinal(paid_to))
    interest = min(amt, round(principal * float(contract.get("apr") or 0) / 100 / 365 * days, 2))
    installments_due = float(contract.get("past_due_amount") or 0)
    fee_part = round(min(fees, max(0.0, amt - max(interest, installments_due))), 2)
    principal_part = round(amt - interest - fee_part, 2)
    rid = ctx.make_id("ppm_", preowned_contract_id, amount, funding_account_last4)
    ctx.create("preowned_transactions", rid, preowned_txn_id=rid, preowned_contract_id=preowned_contract_id,
               customer_id=contract.get("customer_id", ""), event_type="preowned_payment", txn_date=today,
               amount=amt, payment_channel="wire", funding_account_last4=str(funding_account_last4),
               payment_purpose="deficiency", interest_applied=interest, principal_applied=principal_part,
               fees_applied=fee_part, convenience_fee=0.0, return_reason="not_applicable", fee_type="not_applicable",
               waiver_reason="not_applicable", quote_purpose="not_applicable", release_method="not_applicable",
               release_recipient="not_applicable", mailing_address_type="not_applicable",
               notice_type="not_applicable", property_release_type="not_applicable", service_days=0)
    ctx.update("preowned_contracts", preowned_contract_id, status="paid_in_full", paid_in_full_date=today,
               principal_balance=0.0, fees_due_balance=0.0, interest_paid_to_date=today, last_payment_date=today,
               past_due_amount=0.0, days_past_due=0)
    return (f"Settlement payment {rid} posted to contract {preowned_contract_id}: {amt:.2f} USD by wire on {today} from account "
            f"ending {funding_account_last4} (interest {interest:.2f}, principal {principal_part:.2f}, fees "
            f"{fee_part:.2f}); contract status paid_in_full.")


@tool(owner="agent", rw="write")
def bill_lot_storage_d761f3de(ctx: ToolContext, preowned_contract_id: str, amount: float, service_days: int) -> str:
    """Bill the storage-lot charge for a repossessed vehicle financed under a Kestrel Pre-Owned Retail Installment Sale
    Contract, as one repossession expense of the storage kind dated today that records the billable storage days it
    covers. On success the contract's posting history gains one storage charge for the stated amount and days, and the
    contract's fees due balance rises by that amount; the customer sees the charge on the account and in any figure that
    includes fees due. The charge is recorded exactly as given.

    Args:
        preowned_contract_id: Id class — the reference number of the pre-owned contract the storage is billed to, as returned by the pre-owned contract lookup for this customer.
        amount: Fixed-format class — the storage charge in US dollars, a non-negative number with 2 decimal places, rounded half-up to the cent.
        service_days: Fixed-format class — the number of billable storage days the charge covers, a non-negative integer.

    Returns:
        A confirmation string naming the new transaction reference (an opaque id beginning with "pst_"), the contract
        reference, the billed amount in US dollars with 2 decimals, the billable days as an integer, the posting date
        (YYYY-MM-DD) and the new fees due balance in US dollars with 2 decimals; the presence of the transaction
        reference indicates the charge was billed.
    """
    rows = ctx.find("preowned_contracts", preowned_contract_id=preowned_contract_id)
    contract = rows[0] if rows else {}
    amt = round(float(amount), 2)
    days = int(service_days)
    today = ctx.now()[:10]
    rid = ctx.make_id("pst_", preowned_contract_id, amount, service_days)
    ctx.create("preowned_transactions", rid, preowned_txn_id=rid, preowned_contract_id=preowned_contract_id,
               customer_id=contract.get("customer_id", ""), event_type="preowned_repo_expense", txn_date=today,
               amount=amt, fee_type="storage_fee", service_days=days, payment_channel="not_applicable",
               payment_purpose="not_applicable", return_reason="not_applicable", waiver_reason="not_applicable",
               quote_purpose="not_applicable", release_method="not_applicable", release_recipient="not_applicable",
               mailing_address_type="not_applicable", notice_type="not_applicable",
               property_release_type="not_applicable")
    new_fees = round(float(contract.get("fees_due_balance") or 0) + amt, 2)
    ctx.update("preowned_contracts", preowned_contract_id, fees_due_balance=new_fees)
    return (f"Storage charge {rid} billed to contract {preowned_contract_id}: {amt:.2f} USD for {days} day(s) on {today}; "
            f"fees due balance now {new_fees:.2f} USD.")



@tool(owner="agent", rw="write")
def quote_redemption_amount_aa560e9a(ctx: ToolContext, preowned_contract_id: str, amount: float,
                                     good_through_days: int) -> str:
    """Issue a redemption quote on a Kestrel Pre-Owned Retail Installment Sale Contract whose vehicle has been
    repossessed: the amount the customer must pay to get the vehicle back by paying the contract off. On success one
    payoff quote for the redemption purpose is recorded on the contract, dated today, with the stated amount and a
    good-through date the stated number of calendar days from today; balances and status do not change. The quoted
    amount and good-through date can be told to the customer from the receipt.

    Args:
        preowned_contract_id: Id class — the reference number of the pre-owned contract being quoted, as returned by the pre-owned contract lookup for this customer.
        amount: Fixed-format class — the redemption amount in US dollars, a positive number with 2 decimal places, rounded half-up to the cent.
        good_through_days: Fixed-format class — the number of calendar days from today to the good-through date, a non-negative integer.

    Returns:
        A confirmation string naming the quote reference (an opaque id beginning with "prq_"), the contract reference,
        the quoted amount in US dollars with 2 decimals, the quote date and the good-through date (both YYYY-MM-DD); the
        presence of the quote reference indicates the quote was recorded.
    """
    rows = ctx.find("preowned_contracts", preowned_contract_id=preowned_contract_id)
    contract = rows[0] if rows else {}
    amt = round(float(amount), 2)
    today = ctx.now()[:10]
    good_through = _Cal.add_days(today, int(good_through_days))
    rid = ctx.make_id("prq_", preowned_contract_id, amount, good_through_days)
    ctx.create("preowned_transactions", rid, preowned_txn_id=rid, preowned_contract_id=preowned_contract_id,
               customer_id=contract.get("customer_id", ""), event_type="preowned_payoff_quote", txn_date=today,
               amount=amt, quote_good_through_date=good_through, per_diem=0.0, quote_purpose="redemption",
               payment_channel="not_applicable", payment_purpose="not_applicable", return_reason="not_applicable",
               fee_type="not_applicable", waiver_reason="not_applicable", release_method="not_applicable",
               release_recipient="not_applicable", mailing_address_type="not_applicable",
               notice_type="not_applicable", property_release_type="not_applicable", service_days=0)
    return (f"Redemption quote {rid} on contract {preowned_contract_id}: {amt:.2f} USD, quoted {today}, "
            f"good through {good_through}.")


@tool(owner="agent", rw="write")
def mail_sale_notice_3d21c42f(ctx: ToolContext, preowned_contract_id: str, days_to_sale: int) -> str:
    """Mail the notice of intent to sell for a repossessed vehicle financed under a Kestrel Pre-Owned Retail
    Installment Sale Contract and schedule its sale. On success one notice of the intent-to-sell kind, dated today, is
    recorded in the contract's posting history, and the contract records today as the notice mailing date and, as the
    scheduled sale date, the date that lies the stated number of calendar days from today. The customer can be told
    the mailing date and the scheduled sale date from the receipt.

    Args:
        preowned_contract_id: Id class — the reference number of the pre-owned contract the notice is mailed for, as returned by the pre-owned contract lookup for this customer.
        days_to_sale: Fixed-format class — the number of calendar days from today to the scheduled sale date, a positive integer.

    Returns:
        A confirmation string naming the notice reference (an opaque id beginning with "pnt_"), the contract reference,
        the mailing date and the scheduled sale date (both YYYY-MM-DD); the presence of the notice reference indicates
        the notice was mailed and the sale scheduled.
    """
    rows = ctx.find("preowned_contracts", preowned_contract_id=preowned_contract_id)
    contract = rows[0] if rows else {}
    today = ctx.now()[:10]
    sale_date = _Cal.add_days(today, int(days_to_sale))
    rid = ctx.make_id("pnt_", preowned_contract_id, days_to_sale)
    ctx.create("preowned_transactions", rid, preowned_txn_id=rid, preowned_contract_id=preowned_contract_id,
               customer_id=contract.get("customer_id", ""), event_type="preowned_notice_mailed", txn_date=today,
               amount=0.0, notice_type="notice_of_intent_to_sell", payment_channel="not_applicable",
               payment_purpose="not_applicable", return_reason="not_applicable", fee_type="not_applicable",
               waiver_reason="not_applicable", quote_purpose="not_applicable", release_method="not_applicable",
               release_recipient="not_applicable", mailing_address_type="not_applicable",
               property_release_type="not_applicable", service_days=0)
    ctx.update("preowned_contracts", preowned_contract_id, nois_mailed_date=today, scheduled_sale_date=sale_date)
    return (f"Notice of intent to sell {rid} mailed for contract {preowned_contract_id} on {today}; "
            f"sale scheduled for {sale_date}.")



@tool(owner="user", rw="write")
def remit_reinstatement_funds_62601f54(ctx: ToolContext, customer_id: str, preowned_contract_id: str, amount: float) -> str:
    """Send your own certified funds by bank wire transfer to reinstate your repossessed Kestrel Pre-Owned Retail
    Installment Sale Contract. On success one reinstatement payment for the stated amount is posted to the contract,
    dated with the posting date (the day the wire is sent, or the Monday when it is sent on a Saturday or Sunday). The
    amount is split in the contract's payment allocation order into the simple interest accrued through the posting
    date, principal up to the past-due amount, fees due, and any remainder to principal. The contract returns to active
    status with its reinstatement count increased by one, its past-due amount and days past due cleared, interest paid
    through the posting date, and its next due date and installments satisfied moved by one month and one installment
    for each whole monthly installment the interest and principal portions cover. You see the payment reference and
    the active status on the receipt.

    Args:
        customer_id: Id class — your customer reference number, as given to you by the servicing agent from the customer profile lookup.
        preowned_contract_id: Id class — the reference number of your pre-owned contract, as given to you by the servicing agent from the contract lookup.
        amount: Fixed-format class — the reinstatement amount in US dollars, a positive number with 2 decimal places, rounded half-up to the cent, exactly as the agent states it.

    Returns:
        A confirmation string naming the payment reference (an opaque id beginning with "prp_"), the contract reference,
        the amount in US dollars with 2 decimals, the channel "wire", the posting date (YYYY-MM-DD), the interest,
        principal and fees portions in US dollars with 2 decimals, the new next due date (YYYY-MM-DD) and the contract
        status "active"; the presence of the payment reference indicates the payment posted and the contract was
        reinstated.
    """
    rows = ctx.find("preowned_contracts", preowned_contract_id=preowned_contract_id)
    contract = rows[0] if rows else {}
    amt = round(float(amount), 2)
    posted = _Cal.posting_date(ctx.now()[:10])
    principal = float(contract.get("principal_balance") or 0)
    fees = float(contract.get("fees_due_balance") or 0)
    paid_to = str(contract.get("interest_paid_to_date") or posted)[:10]
    days = max(0, _Cal.to_ordinal(posted) - _Cal.to_ordinal(paid_to))
    interest = min(amt, round(principal * float(contract.get("apr") or 0) / 100 / 365 * days, 2))
    installments_due = float(contract.get("past_due_amount") or 0)
    fee_part = round(min(fees, max(0.0, amt - max(interest, installments_due))), 2)
    principal_part = round(amt - interest - fee_part, 2)
    monthly = float(contract.get("monthly_payment") or 0)
    covered = int((interest + principal_part + 1e-9) // monthly) if monthly > 0 else 0
    next_due = _Cal.add_months(str(contract.get("next_due_date") or posted), covered)
    rid = ctx.make_id("prp_", customer_id, preowned_contract_id, amount)
    ctx.create("preowned_transactions", rid, preowned_txn_id=rid, preowned_contract_id=preowned_contract_id,
               customer_id=customer_id, event_type="preowned_payment", txn_date=posted,
               amount=amt, payment_channel="wire", funding_account_last4="", payment_purpose="reinstatement",
               interest_applied=interest, principal_applied=principal_part, fees_applied=fee_part, convenience_fee=0.0,
               return_reason="not_applicable", fee_type="not_applicable", waiver_reason="not_applicable",
               quote_purpose="not_applicable", release_method="not_applicable", release_recipient="not_applicable",
               mailing_address_type="not_applicable", notice_type="not_applicable",
               property_release_type="not_applicable", service_days=0)
    ctx.update("preowned_contracts", preowned_contract_id, status="active",
               reinstatements_used=int(contract.get("reinstatements_used") or 0) + 1, past_due_amount=0.0,
               days_past_due=0, fees_due_balance=round(fees - fee_part, 2),
               principal_balance=round(principal - principal_part, 2), interest_paid_to_date=posted,
               next_due_date=next_due, payments_made_count=int(contract.get("payments_made_count") or 0) + covered,
               last_payment_date=posted)
    return (f"Reinstatement payment {rid} posted to contract {preowned_contract_id}: {amt:.2f} USD by wire on {posted} "
            f"(interest {interest:.2f}, principal {principal_part:.2f}, fees {fee_part:.2f}); next due date {next_due}; "
            f"contract status active.")

"""Hidden task tools of the deferred_annuity_withdrawals_and_death_benefits difficulty (category fixed).

Each tool performs one atomic, already-decided change on an Ashgrove deferred fixed annuity contract.
The figures they book are worked out by the agent from the published rules and passed in; the tools
check no eligibility, aggregate no history and compute no policy amount.
"""

from erlbench import ToolContext, tool


@tool(owner="agent", rw="write")
def assess_missed_withdrawal_charge_e9f9c059(ctx: ToolContext, fixed_contract_id: str, fixed_request_id: str,
                                             charge_amount: float) -> str:
    """Book a corrected partial-withdrawal surrender charge on an Ashgrove deferred fixed annuity contract.

    Records, dated today, one surrender charge entry for a partial withdrawal that was paid earlier
    under the named withdrawal request, and deducts that charge from the contract's current
    contract value. The withdrawal itself and the money already paid to the owner are not touched.
    Afterwards the contract's activity history shows the charge entry tied to the withdrawal
    request, and the contract shows the lowered contract value.

    Args:
        fixed_contract_id: Id class — the reference number of the deferred fixed annuity contract the
            charge is booked on, read from the contract lookup.
        fixed_request_id: Id class — the reference number of the signed partial withdrawal request the
            earlier withdrawal was paid under, read from the contract's activity history or its service
            requests.
        charge_amount: Fixed-format class — the corrected charge in US dollars, a positive amount with
            exactly 2 decimal places (rounded half up to the cent before it is passed); it is
            deducted from the contract value as given.

    Returns:
        A one-line confirmation string: "Charge <entry reference> booked on contract <contract
        reference>: <amount> deducted for request <request reference>; contract value now <value>."
        <entry reference> is the new charge entry's reference number, <amount> and <value> are US
        dollar amounts with 2 decimal places. Receiving this line means the charge entry exists and
        the contract value has been lowered by the amount.
    """
    amount = round(float(charge_amount), 2)
    rid = ctx.make_id("fxc_", fixed_contract_id, fixed_request_id, amount)
    contract = ctx.find("fixed_holdings", fixed_contract_id=fixed_contract_id)
    owner = contract[0].get("customer_id") if contract else ""
    old_value = float(contract[0].get("contract_value") or 0) if contract else 0.0
    new_value = round(old_value - amount, 2)
    ctx.create("fixed_transactions", rid, fixed_txn_id=rid, fixed_contract_id=fixed_contract_id,
               customer_id=owner, event_type="fixed_surrender_charge_assessed",
               transaction_date=ctx.now()[:10], amount=amount, charge_reason="partial_withdrawal",
               fixed_request_id=fixed_request_id)
    ctx.update("fixed_holdings", fixed_contract_id, contract_value=new_value)
    return (f"Charge {rid} booked on contract {fixed_contract_id}: {amount:.2f} deducted for request "
            f"{fixed_request_id}; contract value now {new_value:.2f}.")


@tool(owner="agent", rw="write")
def credit_surrender_interest_88d8dad0(ctx: ToolContext, fixed_contract_id: str, interest_amount: float) -> str:
    """Credit the part-year interest that closes an Ashgrove deferred fixed annuity contract's interest for
    its surrender.

    Records, dated today, one interest credit entry on the contract and adds the interest to the
    contract's current contract value. Afterwards the contract's activity history shows the new
    interest credit entry and the contract shows the raised contract value.

    Args:
        fixed_contract_id: Id class — the reference number of the deferred fixed annuity contract the
            interest is credited to, read from the contract lookup.
        interest_amount: Fixed-format class — the interest credited in US dollars, a positive amount
            with exactly 2 decimal places (rounded half up to the cent before it is passed); it is
            added to the contract value as given.

    Returns:
        A one-line confirmation string: "Interest <entry reference> credited to contract <contract
        reference>: <amount>; contract value now <value>." <entry reference> is the new interest entry's
        reference number, <amount> and <value> are US dollar amounts with 2 decimal places. Receiving
        this line means the interest entry exists and the contract value has been raised by the amount.
    """
    amount = round(float(interest_amount), 2)
    rid = ctx.make_id("fxi_", fixed_contract_id, amount)
    contract = ctx.find("fixed_holdings", fixed_contract_id=fixed_contract_id)
    owner = contract[0].get("customer_id") if contract else ""
    old_value = float(contract[0].get("contract_value") or 0) if contract else 0.0
    new_value = round(old_value + amount, 2)
    ctx.create("fixed_transactions", rid, fixed_txn_id=rid, fixed_contract_id=fixed_contract_id,
               customer_id=owner, event_type="fixed_interest_credited",
               transaction_date=ctx.now()[:10], amount=amount)
    ctx.update("fixed_holdings", fixed_contract_id, contract_value=new_value)
    return (f"Interest {rid} credited to contract {fixed_contract_id}: {amount:.2f}; "
            f"contract value now {new_value:.2f}.")


@tool(owner="user", rw="write")
def confirm_full_surrender_fa1c6fc8(ctx: ToolContext, fixed_contract_id: str, fixed_request_id: str,
                                     cash_surrender_value: float, payout_method: str) -> str:
    """Confirm, as the contract owner, the full surrender of your Ashgrove deferred fixed annuity
    contract for the cash surrender value you were quoted.

    Closes the contract as surrendered today, records the payment of the cash surrender value to
    you by the payout method you choose, brings the contract value to zero and marks your signed
    surrender request as completed. Afterwards the contract shows the status surrendered with
    today's termination date, and its activity history shows the surrender payment.

    Args:
        fixed_contract_id: Id class — the reference number of the contract being surrendered, as the
            representative reads it to you from the contract record.
        fixed_request_id: Id class — the reference number of your signed full surrender request on
            file, as the representative reads it to you from the service request record.
        cash_surrender_value: Fixed-format class — the cash surrender value in US dollars that the
            representative quoted to you, a positive amount with exactly 2 decimal places (rounded
            half up to the cent); it is recorded as paid exactly as given.
        payout_method: Enum class — how the cash surrender value is paid to you, one of:
            "check" — a paper check mailed to the address on file;
            "direct_deposit" — an electronic deposit to your bank account;
            "company_transfer" — a transfer sent directly to another financial company.

    Returns:
        A one-line confirmation string: "Contract <contract reference> surrendered on <date>; surrender
        payment <entry reference> of <amount> by <payout method>; request <request reference>
        completed." <date> is YYYY-MM-DD, <amount> is a US dollar amount with 2 decimal places and
        <entry reference> is the surrender payment entry's reference number. Receiving this line means
        the contract is surrendered and the payment is recorded.
    """
    amount = round(float(cash_surrender_value), 2)
    today = ctx.now()[:10]
    rid = ctx.make_id("fxs_", fixed_contract_id, fixed_request_id, amount, payout_method)
    contract = ctx.find("fixed_holdings", fixed_contract_id=fixed_contract_id)
    owner = contract[0].get("customer_id") if contract else ""
    ctx.update("fixed_holdings", fixed_contract_id, status="surrendered", termination_date=today,
               contract_value=0.0, swp_amount=0.0, swp_frequency="none", swp_next_date="")
    ctx.create("fixed_transactions", rid, fixed_txn_id=rid, fixed_contract_id=fixed_contract_id,
               customer_id=owner, event_type="fixed_surrender_paid", transaction_date=today,
               amount=amount, fixed_request_id=fixed_request_id, payout_method=payout_method)
    ctx.update("fixed_service_requests", fixed_request_id, request_status="completed", decision_date=today)
    return (f"Contract {fixed_contract_id} surrendered on {today}; surrender payment {rid} of {amount:.2f} "
            f"by {payout_method}; request {fixed_request_id} completed.")


@tool(owner="agent", rw="write")
def renew_guarantee_period_14f04954(ctx: ToolContext, fixed_contract_id: str, renewal_rate: float) -> str:
    """Record the renewal by default of an Ashgrove SecureRate contract's guarantee period into a new
    period of the same length.

    Sets the contract's guaranteed rate to the renewal rate given, starts the new guarantee period
    and a new surrender charge schedule on the day after the current guarantee period end date,
    and moves the guarantee period end date forward by the length of the contract's SecureRate
    period (3, 5, 6, 7 or 10 years, as in the contract's tier name). The contract value and the
    activity history are not touched. Afterwards the contract shows the new guaranteed rate, the
    new guarantee period end date and the new surrender charge schedule start date.

    Args:
        fixed_contract_id: Id class — the reference number of the SecureRate contract whose guarantee
            period renews, read from the contract lookup.
        renewal_rate: Fixed-format class — the annual effective rate guaranteed for the new period, a
            decimal fraction with exactly 4 decimal places (for example 0.0525 means 5.25 percent),
            rounded half up to the fourth decimal place before it is passed.

    Returns:
        A one-line confirmation string: "Contract <contract reference> renewed: rate <rate> from <start
        date> to <end date>." <rate> is the decimal rate with 4 decimal places and both dates are
        YYYY-MM-DD. Receiving this line means the new guarantee period is recorded on the contract.
    """
    rate = round(float(renewal_rate), 4)
    rows = ctx.find("fixed_holdings", fixed_contract_id=fixed_contract_id)
    row = rows[0] if rows else {}
    end = str(row.get("guarantee_period_end_date") or "")
    tier = str(row.get("variant_name") or "")
    years = int(tier.split()[-1]) if tier.split() and tier.split()[-1].isdigit() else 1
    y, m, d = (int(p) for p in (end or ctx.now()[:10])[:10].split("-"))

    def _month_days(year: int, month: int) -> int:
        leap = year % 4 == 0 and (year % 100 != 0 or year % 400 == 0)
        return [31, 29 if leap else 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31][month - 1]

    sy, sm, sd = y, m, d + 1
    if sd > _month_days(sy, sm):
        sy, sm, sd = (sy + 1, 1, 1) if sm == 12 else (sy, sm + 1, 1)
    ey = y + years
    ed = min(d, _month_days(ey, m))
    start_iso = f"{sy:04d}-{sm:02d}-{sd:02d}"
    end_iso = f"{ey:04d}-{m:02d}-{ed:02d}"
    ctx.update("fixed_holdings", fixed_contract_id, guaranteed_rate=rate,
               guarantee_period_end_date=end_iso, sc_schedule_start_date=start_iso)
    return (f"Contract {fixed_contract_id} renewed: rate {rate:.4f} from {start_iso} "
            f"to {end_iso}.")


@tool(owner="agent", rw="write")
def credit_death_valuation_interest_0cf0ffa2(ctx: ToolContext, fixed_contract_id: str, interest_amount: float,
                                            valuation_date: str) -> str:
    """Credit the interest that values an Ashgrove deferred fixed annuity contract's death benefit.

    Records, dated today, one interest credit entry on a contract whose owner has died, marks the
    entry's interest period as ending on the valuation date given, and adds the interest to the
    contract's current contract value. Afterwards the contract's activity history shows the new
    interest credit entry with its period end, and the contract shows the raised contract value.

    Args:
        fixed_contract_id: Id class — the reference number of the deceased owner's deferred fixed
            annuity contract, read from the contract lookup.
        interest_amount: Fixed-format class — the interest credited in US dollars, a positive amount
            with exactly 2 decimal places (rounded half up to the cent before it is passed); it is
            added to the contract value as given.
        valuation_date: Fixed-format class — the date the death benefit is valued on, which closes the
            interest period, written YYYY-MM-DD (calendar date, no time or time zone).

    Returns:
        A one-line confirmation string: "Valuation interest <entry reference> credited to contract
        <contract reference>: <amount>; contract value now <value>." <entry reference> is the new
        interest entry's reference number, <amount> and <value> are US dollar amounts with 2 decimal
        places. Receiving this line means the interest entry exists and the contract value has been
        raised by the amount.
    """
    amount = round(float(interest_amount), 2)
    rid = ctx.make_id("fxv_", fixed_contract_id, amount, valuation_date)
    contract = ctx.find("fixed_holdings", fixed_contract_id=fixed_contract_id)
    owner = contract[0].get("customer_id") if contract else ""
    old_value = float(contract[0].get("contract_value") or 0) if contract else 0.0
    new_value = round(old_value + amount, 2)
    ctx.create("fixed_transactions", rid, fixed_txn_id=rid, fixed_contract_id=fixed_contract_id,
               customer_id=owner, event_type="fixed_interest_credited",
               transaction_date=ctx.now()[:10], amount=amount, interest_period_end=str(valuation_date)[:10])
    ctx.update("fixed_holdings", fixed_contract_id, contract_value=new_value)
    return (f"Valuation interest {rid} credited to contract {fixed_contract_id}: {amount:.2f}; "
            f"contract value now {new_value:.2f}.")


@tool(owner="user", rw="write")
def settle_death_benefit_share_569ae0ca(ctx: ToolContext, fixed_contract_id: str, fixed_request_id: str,
                                        payee_name: str, share_amount: float, claim_interest: float,
                                        payout_method: str) -> str:
    """Elect, as a beneficiary, to take your share of an Ashgrove deferred fixed annuity death benefit
    as a lump sum, and accept its payment.

    Records your lump-sum settlement election on your death claim, records today the payment to you
    of your share of the death benefit together with the death-claim interest on it, by the payout
    method you choose, and takes your share out of the contract value. The shares of any other
    beneficiaries stay on the contract. Afterwards your claim shows the lump-sum election and the
    contract's activity history shows the payment made to you.

    Args:
        fixed_contract_id: Id class — the reference number of the deceased owner's contract, as the
            representative reads it to you from the contract record.
        fixed_request_id: Id class — the reference number of your approved death claim, as the
            representative reads it to you from the claim record.
        payee_name: Verbatim class — your name exactly as it appears on the beneficiary designation,
            as the representative reads it to you; copy it character for character, preserving the
            original wording, digits and punctuation, with no translation, normalisation,
            summarisation, addition or deletion (verbatim).
        share_amount: Fixed-format class — your share of the death benefit in US dollars, excluding
            interest, a positive amount with exactly 2 decimal places (rounded half up to the cent);
            it is paid and taken out of the contract value as given.
        claim_interest: Fixed-format class — the death-claim interest paid with your share in US
            dollars, an amount of zero or more with exactly 2 decimal places (rounded half up to the
            cent); it is paid as given.
        payout_method: Enum class — how the payment reaches you, one of:
            "check" — a paper check mailed to you;
            "direct_deposit" — an electronic deposit to your bank account;
            "company_transfer" — a transfer sent directly to another financial company.

    Returns:
        A one-line confirmation string: "Death benefit payment <entry reference> to <payee>: share
        <share>, interest <interest>, by <payout method>; contract value now <value>." <share>,
        <interest> and <value> are US dollar amounts with 2 decimal places and <entry reference> is
        the payment entry's reference number. Receiving this line means your election and your
        payment are recorded.
    """
    share = round(float(share_amount), 2)
    interest = round(float(claim_interest), 2)
    today = ctx.now()[:10]
    rid = ctx.make_id("fxd_", fixed_contract_id, fixed_request_id, payee_name, share, interest, payout_method)
    contract = ctx.find("fixed_holdings", fixed_contract_id=fixed_contract_id)
    owner = contract[0].get("customer_id") if contract else ""
    old_value = float(contract[0].get("contract_value") or 0) if contract else 0.0
    new_value = round(old_value - share, 2)
    ctx.create("fixed_transactions", rid, fixed_txn_id=rid, fixed_contract_id=fixed_contract_id,
               customer_id=owner, event_type="fixed_death_benefit_paid", transaction_date=today,
               amount=share, interest_amount=interest, payee_name=payee_name,
               payout_method=payout_method, fixed_request_id=fixed_request_id)
    ctx.update("fixed_holdings", fixed_contract_id, contract_value=new_value)
    ctx.update("fixed_service_requests", fixed_request_id, settlement_option="lump_sum",
               disbursement_method=payout_method)
    return (f"Death benefit payment {rid} to {payee_name}: share {share:.2f}, interest {interest:.2f}, "
            f"by {payout_method}; contract value now {new_value:.2f}.")

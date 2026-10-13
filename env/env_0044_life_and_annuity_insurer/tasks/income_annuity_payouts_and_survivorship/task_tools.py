"""Hidden task tools for the income_annuity_payouts_and_survivorship difficulty of
env_0044_life_and_annuity_insurer (Ashgrove Mutual Life Insurance Company, Income Annuities).

Each tool performs one atomic write on an Ashgrove income annuity contract with the values the
agent has already worked out from the published rules; no tool checks eligibility, status,
ordering or any other policy condition, and none computes an amount on the agent's behalf.
"""

from erlbench import ToolContext, tool


@tool(owner="agent", rw="write")
def pay_beneficiary_arrears_076c3375(ctx: ToolContext, income_contract_id: str, payment_due_date: str,
                                     payee_name: str, payment_method: str, gross_amount: float,
                                     net_paid_amount: float) -> str:
    """Pay one certain installment that fell due on an Ashgrove period-certain income annuity after
    the annuitant's death and was never paid, to the beneficiary now receiving the payments. One
    call books one paid installment on the contract's activity history for the stated payment date,
    with its gross amount and the amount actually sent after tax withholding and any interest, and
    lowers the contract's unreturned purchase amount by the gross amount. The beneficiary sees the
    payment on the contract's activity history at once; the receipt confirms the booking.

    Args:
        income_contract_id: Id class — the reference number of the income annuity contract the
            installment belongs to, read from the income annuity contract lookup.
        payment_due_date: Fixed-format class — the scheduled payment date of the unpaid certain
            installment being paid, in YYYY-MM-DD format.
        payee_name: Verbatim class — the beneficiary's full name exactly as the customer profile
            lookup shows it for the person receiving the payments, copied character for character
            with no change (verbatim).
        payment_method: Enum class — how the money is sent: direct_deposit when the payment goes to
            the deposit account on the contract's payment instructions; check when a paper check is
            mailed to the mailing address on the contract.
        gross_amount: Fixed-format class — the gross installment paid for that payment date, before
            any tax withholding, in USD rounded to 2 decimal places.
        net_paid_amount: Fixed-format class — the amount actually sent to the beneficiary after
            federal and state tax withholding and including any interest paid with the installment,
            in USD rounded to 2 decimal places.

    Returns:
        A receipt string confirming the payment, carrying the new activity entry reference number,
        the contract reference number, the payment date covered, the gross amount and the net amount
        sent (USD, 2 decimal places). The receipt text starting with "Paid" means the installment is
        booked as issued.
    """
    gross = round(float(gross_amount), 2)
    net = round(float(net_paid_amount), 2)
    rid = ctx.make_id("itx_", income_contract_id, payment_due_date, payee_name, payment_method, gross, net)
    holding = ctx.find("income_holdings", income_contract_id=income_contract_id)
    owner = holding[0].get("customer_id") if holding else None
    ctx.create("income_transactions", rid, income_txn_id=rid, income_contract_id=income_contract_id,
               customer_id=owner, event_type="income_payment_issued", transaction_date=ctx.now()[:10],
               amount=gross, payment_due_date=payment_due_date, payee_name=payee_name,
               payment_method=payment_method, net_paid_amount=net)
    if holding:
        balance = round(float(holding[0].get("unreturned_premium") or 0) - gross, 2)
        ctx.update("income_holdings", income_contract_id, unreturned_premium=balance)
    return (f"Paid installment of {payment_due_date} on contract {income_contract_id}: entry {rid}, "
            f"gross {gross:.2f} USD, net sent {net:.2f} USD.")


@tool(owner="user", rw="write")
def elect_commuted_value_be644418(ctx: ToolContext, income_contract_id: str, income_request_id: str,
                                  payee_customer_id: str, commuted_value: float,
                                  requested_withholding_pct: float, disbursement_method: str) -> str:
    """The beneficiary receiving the remaining certain installments of an Ashgrove period-certain
    income annuity signs, in person, an election to take the commuted value of those installments
    in one sum instead of continuing payments. One call files the signed election on the contract
    as an approved commutation election carrying the commuted value accepted, the federal
    withholding rate the beneficiary chose for the lump sum and how the beneficiary wants to be
    paid, linked to the approved death claim. The beneficiary can see the filed election at once;
    the receipt gives its reference number.

    Args:
        income_contract_id: Id class — the reference number of the income annuity contract whose
            remaining certain installments are commuted, read from the income annuity contract lookup.
        income_request_id: Id class — the reference number of the approved death claim on that
            contract, read from the income annuity service request lookup.
        payee_customer_id: Id class — the customer reference number of the beneficiary signing the
            election, read from the customer profile lookup.
        commuted_value: Fixed-format class — the commuted value of the remaining certain installments
            that the beneficiary accepts, in USD rounded to 2 decimal places.
        requested_withholding_pct: Fixed-format class — the federal income tax withholding rate the
            beneficiary chooses for the lump sum, as a decimal with 2 decimal places (0.20 for 20
            percent, 0.00 for no withholding).
        disbursement_method: Enum class — how the beneficiary wants the lump sum paid: check when a
            paper check is to be mailed; direct_deposit when it is to go to the deposit account on the
            contract's payment instructions.

    Returns:
        A receipt string confirming the signed election, carrying the new election reference number,
        the contract reference number, the commuted value
        accepted (USD, 2 decimal places) and the withholding rate chosen. The receipt text starting
        with "Election filed" means the election stands approved on the contract.
    """
    value = round(float(commuted_value), 2)
    pct = round(float(requested_withholding_pct), 2)
    rid = ctx.make_id("ireq_", income_contract_id, income_request_id, payee_customer_id, value, pct,
                      disbursement_method)
    today = ctx.now()[:10]
    ctx.create("income_service_requests", rid, income_request_id=rid, income_contract_id=income_contract_id,
               customer_id=payee_customer_id, request_type="commutation_election", request_status="approved",
               received_date=today, signed_date=today, signature_verified=True, decision_date=today,
               requested_amount=value, requested_withholding_pct=pct, disbursement_method=disbursement_method)
    return (f"Election filed: commutation election {rid} on contract {income_contract_id} for "
            f"{value:.2f} USD, federal withholding {pct:.2f}.")


@tool(owner="agent", rw="write")
def pay_commuted_value_cb4f45b9(ctx: ToolContext, income_contract_id: str, income_request_id: str,
                                payee_name: str, payment_method: str, commuted_amount: float,
                                net_paid_amount: float) -> str:
    """Pay the commuted value of the remaining certain installments of an Ashgrove period-certain
    income annuity to the beneficiary who elected it. One call books the lump-sum payment on the
    contract's activity history against the beneficiary's commutation election, with the gross
    commuted value and the amount actually sent after federal and state tax withholding, and lowers
    the contract's unreturned purchase amount by the gross amount. The beneficiary sees the payment
    at once; the receipt confirms the booking.

    Args:
        income_contract_id: Id class — the reference number of the income annuity contract, read
            from the income annuity contract lookup.
        income_request_id: Id class — the reference number of the beneficiary's approved commutation
            election on the contract, as shown on the election's receipt or in the income annuity service
            request lookup.
        payee_name: Verbatim class — the beneficiary's full name exactly as the customer profile
            lookup shows it, copied character for character with no change (verbatim).
        payment_method: Enum class — how the lump sum is sent: check when a paper check is mailed;
            direct_deposit when it goes to the deposit account on the contract's payment instructions.
        commuted_amount: Fixed-format class — the gross commuted value paid, before any tax
            withholding, in USD rounded to 2 decimal places.
        net_paid_amount: Fixed-format class — the amount actually sent after federal and state tax
            withholding, in USD rounded to 2 decimal places.

    Returns:
        A receipt string confirming the lump-sum payment, carrying the new activity entry reference
        number, the contract and election reference numbers, the gross commuted value and the net
        amount sent (USD, 2 decimal places). The receipt text starting with "Paid commuted value"
        means the payment is booked.
    """
    gross = round(float(commuted_amount), 2)
    net = round(float(net_paid_amount), 2)
    rid = ctx.make_id("itx_", income_contract_id, income_request_id, payee_name, payment_method, gross, net)
    holding = ctx.find("income_holdings", income_contract_id=income_contract_id)
    owner = holding[0].get("customer_id") if holding else None
    ctx.create("income_transactions", rid, income_txn_id=rid, income_contract_id=income_contract_id,
               customer_id=owner, event_type="income_commuted_value_paid", transaction_date=ctx.now()[:10],
               amount=gross, payee_name=payee_name, income_request_id=income_request_id,
               payment_method=payment_method, net_paid_amount=net)
    if holding:
        balance = round(float(holding[0].get("unreturned_premium") or 0) - gross, 2)
        ctx.update("income_holdings", income_contract_id, unreturned_premium=balance)
    return (f"Paid commuted value on contract {income_contract_id} under election {income_request_id}: "
            f"entry {rid}, gross {gross:.2f} USD, net sent {net:.2f} USD.")


@tool(owner="agent", rw="write")
def reissue_returned_installment_7c2be31a(ctx: ToolContext, income_contract_id: str, payment_due_date: str,
                                          payee_name: str, payment_method: str, gross_amount: float,
                                          net_paid_amount: float) -> str:
    """Reissue an Ashgrove income annuity installment that came back returned and has been held in
    suspense since. One call books the held installment as released and paid for its payment date, books
    the reissued payment with its gross amount and the amount actually sent after tax withholding and
    any interest, and lowers both the contract's balance held in suspense and its unreturned purchase
    amount by the gross amount. The payee sees the reissued payment on the contract's activity history at
    once; the receipt confirms the reissue.

    Args:
        income_contract_id: Id class — the reference number of the income annuity contract holding the
            returned installment, read from the income annuity contract lookup.
        payment_due_date: Fixed-format class — the scheduled payment date of the returned installment, in
            YYYY-MM-DD format, as shown on its held entry.
        payee_name: Verbatim class — the full name of the person the reissued payment is made out to,
            exactly as the customer profile lookup shows it, copied character for character with no change
            (verbatim).
        payment_method: Enum class — how the reissued payment is sent: check when a paper check is mailed
            to the mailing address on the contract; direct_deposit when it goes to the deposit account on
            the contract's payment instructions.
        gross_amount: Fixed-format class — the gross installment reissued, before any tax withholding, in
            USD rounded to 2 decimal places.
        net_paid_amount: Fixed-format class — the amount actually sent after federal and state tax
            withholding and including any interest paid with it, in USD rounded to 2 decimal places.

    Returns:
        A receipt string confirming the reissue, carrying the reference numbers of the release entry and of
        the reissued payment entry, the payment date, the gross amount and the net amount sent (USD, 2
        decimal places). The receipt text starting with "Reissued" means both entries are booked.
    """
    gross = round(float(gross_amount), 2)
    net = round(float(net_paid_amount), 2)
    rel = ctx.make_id("itx_", income_contract_id, payment_due_date, payee_name, payment_method, gross, net, "released")
    pay = ctx.make_id("itx_", income_contract_id, payment_due_date, payee_name, payment_method, gross, net, "reissued")
    holding = ctx.find("income_holdings", income_contract_id=income_contract_id)
    owner = holding[0].get("customer_id") if holding else None
    today = ctx.now()[:10]
    ctx.create("income_transactions", rel, income_txn_id=rel, income_contract_id=income_contract_id,
               customer_id=owner, event_type="income_held_payment_released", transaction_date=today,
               amount=gross, payment_due_date=payment_due_date, release_outcome="paid")
    ctx.create("income_transactions", pay, income_txn_id=pay, income_contract_id=income_contract_id,
               customer_id=owner, event_type="income_payment_issued", transaction_date=today, amount=gross,
               payment_due_date=payment_due_date, payee_name=payee_name, payment_method=payment_method,
               net_paid_amount=net)
    if holding:
        held = round(float(holding[0].get("suspense_held_balance") or 0) - gross, 2)
        unret = round(float(holding[0].get("unreturned_premium") or 0) - gross, 2)
        ctx.update("income_holdings", income_contract_id, suspense_held_balance=held, unreturned_premium=unret)
    return (f"Reissued {gross:.2f} USD held for {payment_due_date} on contract {income_contract_id}: release "
            f"entry {rel}, payment entry {pay}, net sent {net:.2f} USD.")


@tool(owner="user", rw="write")
def settle_post_death_deposit_f655a739(ctx: ToolContext, income_contract_id: str, source_txn_id: str,
                                       payment_due_date: str, overpaid_amount: float,
                                       repayment_amount: float) -> str:
    """The payee who received an Ashgrove income annuity deposit that was too large after an annuitant's
    death settles, in person, what is owed back on it. One call records on the contract's activity
    history the overpayment owed on that deposit and the payee's own repayment toward it, both linked to
    the deposit; any part of the overpayment not repaid stays owed on the contract. The payee sees both
    entries at once; the receipt confirms the repayment.

    Args:
        income_contract_id: Id class — the reference number of the income annuity contract the deposit
            was paid from, read from the income annuity contract lookup.
        source_txn_id: Id class — the reference number of the deposit concerned, as shown on its entry in
            the contract's activity history.
        payment_due_date: Fixed-format class — the scheduled payment date of that deposit, in YYYY-MM-DD
            format, as shown on its activity entry.
        overpaid_amount: Fixed-format class — the overpayment owed back on the deposit, in USD rounded to 2
            decimal places.
        repayment_amount: Fixed-format class — the amount the payee repays now, in USD rounded to 2
            decimal places.

    Returns:
        A receipt string confirming the settlement, carrying the reference numbers of the overpayment
        entry and of the repayment entry, the deposit concerned, the overpayment owed and the amount repaid
        (USD, 2 decimal places). The receipt text starting with "Repayment recorded" means both entries
        are booked.
    """
    owed = round(float(overpaid_amount), 2)
    amount = round(float(repayment_amount), 2)
    oid = ctx.make_id("itx_", income_contract_id, source_txn_id, payment_due_date, owed, "owed")
    rid = ctx.make_id("itx_", income_contract_id, source_txn_id, payment_due_date, amount, "repaid")
    holding = ctx.find("income_holdings", income_contract_id=income_contract_id)
    owner = holding[0].get("customer_id") if holding else None
    today = ctx.now()[:10]
    ctx.create("income_transactions", oid, income_txn_id=oid, income_contract_id=income_contract_id,
               customer_id=owner, event_type="income_overpayment_identified", transaction_date=today,
               amount=owed, payment_due_date=payment_due_date, source_txn_id=source_txn_id)
    ctx.create("income_transactions", rid, income_txn_id=rid, income_contract_id=income_contract_id,
               customer_id=owner, event_type="income_overpayment_recovered", transaction_date=today,
               amount=amount, recovery_method="direct_repayment", source_txn_id=source_txn_id)
    if holding:
        receivable = round(float(holding[0].get("overpayment_receivable_balance") or 0) + owed - amount, 2)
        ctx.update("income_holdings", income_contract_id, overpayment_receivable_balance=receivable)
    return (f"Repayment recorded on contract {income_contract_id} for deposit {source_txn_id}: overpayment "
            f"entry {oid} of {owed:.2f} USD, repayment entry {rid} of {amount:.2f} USD.")


@tool(owner="agent", rw="write")
def release_survivor_share_80ea435e(ctx: ToolContext, income_contract_id: str, payment_due_date: str,
                                    payee_name: str, payment_method: str, gross_amount: float,
                                    forfeited_amount: float, offset_amount: float, offset_source_txn_id: str,
                                    net_paid_amount: float) -> str:
    """Settle an installment held in suspense on an Ashgrove income annuity after the first death on a
    joint contract: release the survivor's share to the surviving payee and forfeit the rest back to the
    contract, applying any part of the survivor's share that recovers an overpayment still owed. One call
    books the forfeited part and the released survivor share for the stated payment date, books the paid
    installment with its gross amount and the amount actually sent, books the recovery of the amount
    applied to the overpayment against the deposit it came from (none when that amount is zero), and
    lowers the contract's balance held in suspense, its unreturned purchase amount and its overpayment
    owed accordingly. The survivor sees the payment at once; the receipt confirms the settlement.

    Args:
        income_contract_id: Id class — the reference number of the income annuity contract holding the
            installment, read from the income annuity contract lookup.
        payment_due_date: Fixed-format class — the scheduled payment date of the held installment, in
            YYYY-MM-DD format, as shown on its held entry.
        payee_name: Verbatim class — the survivor's full name exactly as the customer profile lookup shows
            it, copied character for character with no change (verbatim).
        payment_method: Enum class — how the money is sent: direct_deposit when it goes to the deposit
            account on the contract's payment instructions; check when a paper check is mailed to the
            mailing address on the contract.
        gross_amount: Fixed-format class — the gross survivor share released, before any withholding or
            recovery, in USD rounded to 2 decimal places.
        forfeited_amount: Fixed-format class — the part of the held installment forfeited back to the
            contract, in USD rounded to 2 decimal places.
        offset_amount: Fixed-format class — the part of the survivor share applied to an overpayment still
            owed on the contract, in USD rounded to 2 decimal places; 0.00 when none is applied.
        offset_source_txn_id: Id class — the reference number of the deposit whose overpayment the applied
            amount recovers, as shown on its entry in the contract's activity history; empty string when
            nothing is applied.
        net_paid_amount: Fixed-format class — the amount actually sent after federal and state tax
            withholding and after the amount applied to the overpayment, in USD rounded to 2 decimal
            places.

    Returns:
        A receipt string confirming the settlement, carrying the reference numbers of the forfeiture,
        release and paid installment entries, the payment date, the gross share released, the amount
        applied to the overpayment and the net amount sent (USD, 2 decimal places). The receipt text
        starting with "Released" means the entries are booked.
    """
    gross = round(float(gross_amount), 2)
    forfeited = round(float(forfeited_amount), 2)
    offset = round(float(offset_amount), 2)
    net = round(float(net_paid_amount), 2)
    key = (income_contract_id, payment_due_date, payee_name, payment_method, gross, forfeited, offset, net)
    fof = ctx.make_id("itx_", *key, "forfeited")
    rel = ctx.make_id("itx_", *key, "released")
    pay = ctx.make_id("itx_", *key, "paid")
    holding = ctx.find("income_holdings", income_contract_id=income_contract_id)
    owner = holding[0].get("customer_id") if holding else None
    today = ctx.now()[:10]
    ctx.create("income_transactions", fof, income_txn_id=fof, income_contract_id=income_contract_id,
               customer_id=owner, event_type="income_held_payment_released", transaction_date=today,
               amount=forfeited, payment_due_date=payment_due_date, release_outcome="forfeited")
    ctx.create("income_transactions", rel, income_txn_id=rel, income_contract_id=income_contract_id,
               customer_id=owner, event_type="income_held_payment_released", transaction_date=today,
               amount=gross, payment_due_date=payment_due_date, release_outcome="paid")
    ctx.create("income_transactions", pay, income_txn_id=pay, income_contract_id=income_contract_id,
               customer_id=owner, event_type="income_payment_issued", transaction_date=today, amount=gross,
               payment_due_date=payment_due_date, payee_name=payee_name, payment_method=payment_method,
               net_paid_amount=net)
    if offset > 0:
        off = ctx.make_id("itx_", *key, offset_source_txn_id, "offset")
        ctx.create("income_transactions", off, income_txn_id=off, income_contract_id=income_contract_id,
                   customer_id=owner, event_type="income_overpayment_recovered", transaction_date=today,
                   amount=offset, recovery_method="payment_offset", source_txn_id=offset_source_txn_id)
    if holding:
        h = holding[0]
        ctx.update("income_holdings", income_contract_id,
                   suspense_held_balance=round(float(h.get("suspense_held_balance") or 0) - gross - forfeited, 2),
                   unreturned_premium=round(float(h.get("unreturned_premium") or 0) - gross, 2),
                   overpayment_receivable_balance=round(float(h.get("overpayment_receivable_balance") or 0) - offset, 2))
    return (f"Released {gross:.2f} USD of the installment held for {payment_due_date} on contract "
            f"{income_contract_id} (forfeited {forfeited:.2f}, applied to the overpayment {offset:.2f}): entries "
            f"{fof}, {rel}, {pay}; net sent {net:.2f} USD.")

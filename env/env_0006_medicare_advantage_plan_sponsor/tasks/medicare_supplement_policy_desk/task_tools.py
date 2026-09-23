"""Hidden task tools for the Medicare Supplement policy desk (Ridgecrest Health Plans, Inc.).

Each tool performs one atomic write on a Medicare Supplement record. None of them
aggregates history, works out an amount or judges whether the write is due: the
representative reads the policy, the premium account and the crossover lines, works the
figure out from the published rules, and passes it in.
"""

from erlbench import ToolContext, tool


@tool(owner="agent", rw="write")
def post_overlap_premium_return_c83152d2(ctx: ToolContext, medigap_policy_id: str, customer_id: str,
                                         source_premium_entry_id: str, billing_period: str,
                                         returned_months: int, return_amount: float) -> str:
    """Return supplement premium that was charged for cover the policyholder could not use, by
    putting a correction entry on their Medicare Supplement premium account. One call books one
    return against one named premium charge: the money is paid back to the policyholder by the way
    their premium reaches the plan, the amount is credited against what their premium account shows
    outstanding, and the new entry appears on the account alongside the charge it corrects, carrying
    the reason the correction was made. The call has completed when the confirmation naming the new
    account entry comes back.

    Args:
        medigap_policy_id: Id class — the reference number of the Medicare Supplement policy whose
            premium account is being corrected, read from the policyholder's policy record.
        customer_id: Id class — the member reference number of the policyholder the premium is
            returned to, read from their member profile.
        source_premium_entry_id: Id class — the reference number of the single premium charge this
            return corrects, read from the entries on that policy's premium account.
        billing_period: Fixed-format class — the first month of the span whose premium is being
            returned, written as YYYY-MM.
        returned_months: Fixed-format class — how many months of cover the returned premium paid
            for, expressed as a whole number of months, one of 1, 3, 6 or 12.
        return_amount: Fixed-format class — the money handed back, in USD, recorded to 2 decimal
            places and never negative.

    Returns:
        A confirmation sentence in plain text naming the reference number of the new premium account
        entry, the policy it was booked on, the amount returned and the charge it corrects. Receiving
        that sentence is what says the return is on the account; no other value is returned.
    """
    rid = ctx.make_id("mgret_", medigap_policy_id, source_premium_entry_id, billing_period,
                      returned_months, return_amount)
    ctx.create("medigap_premium_ledger", rid,
               medigap_premium_entry_id=rid,
               medigap_policy_id=medigap_policy_id,
               customer_id=customer_id,
               event_type="medigap_premium_refund",
               billing_period=billing_period,
               period_months=int(returned_months),
               posted_date=ctx.now()[:10],
               amount=round(float(return_amount), 2),
               payment_channel="electronic_funds_transfer",
               source_premium_entry_id=source_premium_entry_id,
               refund_reason_code="rate_correction",
               remittance_reference="")
    return (f"Premium return {rid} booked on policy {medigap_policy_id}: "
            f"{round(float(return_amount), 2)} returned against charge {source_premium_entry_id}.")


@tool(owner="user", rw="write")
def remit_supplement_settlement_23b5df61(ctx: ToolContext, medigap_policy_id: str, customer_id: str,
                                         medigap_premium_entry_id: str, billing_period: str,
                                         settlement_amount: float, balance_effect: str,
                                         remittance_reference: str) -> str:
    """Pay money onto your own Medicare Supplement premium account over the telephone. One call
    hands over one payment: the amount you authorise leaves the card or bank account you are paying
    from, the money is applied to the billing period you name, your premium account shows the
    payment against that period and its outstanding balance falls by what you have paid. You can see
    the payment on the account as soon as the confirmation naming it comes back.

    Args:
        medigap_policy_id: Id class — the reference number of the Medicare Supplement policy the
            money is being paid onto, read from the policy record held for you.
        customer_id: Id class — your member reference number, read from your member profile.
        medigap_premium_entry_id: Id class — the reference number of the premium account entry the
            money is applied against, read from the entries on that policy's premium account.
        billing_period: Fixed-format class — the first month of the billing span the money is
            applied to, written as YYYY-MM.
        settlement_amount: Fixed-format class — the money you are paying now, in USD, recorded to 2
            decimal places and never negative.
        balance_effect: Enum class — what this payment does to the balance the premium account
            shows once it is applied, one of four values. not_applicable where the entry is of a
            kind that moves no balance at all. partial_payment where the money leaves part of what
            the account shows outstanding still unpaid. settles_balance where the money brings the
            account exactly to nothing owed. overpayment where the money is more than the account
            shows outstanding and leaves a credit standing.
        remittance_reference: Verbatim class — the payment reference printed on the premium notice
            you are paying from, copied character for character exactly as it is written there,
            keeping the original wording, digits and punctuation, with nothing translated,
            normalised, summarised, added or dropped (verbatim).

    Returns:
        A confirmation sentence in plain text naming the reference number of the payment entry now
        on the premium account, the policy it was paid onto, the amount taken and the billing period
        it was applied to. Receiving that sentence is what says the money has been taken and posted;
        no other value is returned.
    """
    rid = ctx.make_id("mgpay_", medigap_policy_id, medigap_premium_entry_id, billing_period,
                      settlement_amount, remittance_reference)
    ctx.create("medigap_premium_ledger", rid,
               medigap_premium_entry_id=rid,
               medigap_policy_id=medigap_policy_id,
               customer_id=customer_id,
               event_type="medigap_premium_payment",
               billing_period=billing_period,
               posted_date=ctx.now()[:10],
               amount=round(float(settlement_amount), 2),
               payment_channel="telephone_payment",
               balance_effect=balance_effect,
               remittance_reference=remittance_reference)
    return (f"Payment {rid} taken on policy {medigap_policy_id}: "
            f"{round(float(settlement_amount), 2)} applied to billing period {billing_period}.")


@tool(owner="agent", rw="write")
def book_precoverage_restatement_aba9484f(ctx: ToolContext, medigap_policy_id: str, customer_id: str,
                                          source_claim_id: str, medicare_claim_number: str,
                                          date_of_service: str, reversed_payment_amount: float,
                                          liability_restated: float) -> str:
    """Put right a single crossover claim line the supplement settled when it should not have, by
    booking the restatement of that line against the policy. One call restates one named line: what
    the supplement paid on it is taken back from whoever received it, the amount of the recorded
    liability that is no longer the policyholder's is recorded with the restatement, the year's
    deductible accumulator falls by that amount, and the restatement stands on the claim record
    beside the line it corrects with a status showing the line has been adjusted. The call has
    completed when the confirmation naming the new claim record comes back.

    Args:
        medigap_policy_id: Id class — the reference number of the Medicare Supplement policy the
            restated line sits on, read from the policyholder's policy record.
        customer_id: Id class — the member reference number of the policyholder whose line is being
            restated, read from their member profile.
        source_claim_id: Id class — the reference number of the single processed crossover line this
            restatement applies to, read from the claims that crossed over to that policy.
        medicare_claim_number: Fixed-format class — the number Medicare gave the original claim,
            carried over from the line being restated exactly as it stands there, being a
            thirteen-character Medicare claim control number.
        date_of_service: Fixed-format class — the date the service was rendered, carried over from
            the line being restated, written as YYYY-MM-DD.
        reversed_payment_amount: Fixed-format class — the money the supplement paid on the line
            being restated and is now taking back, in USD, recorded to 2 decimal places and never
            negative; it is booked against the policy as a negative payment.
        liability_restated: Fixed-format class — the part of the liability the line records that is
            no longer the policyholder's once the line is restated, in USD, recorded to 2 decimal
            places and never negative.

    Returns:
        A confirmation sentence in plain text naming the reference number of the new claim record,
        the line it restates, the payment taken back and the liability restated. Receiving that
        sentence is what says the restatement stands on the claim record; no other value is
        returned.
    """
    rid = ctx.make_id("mgadj_", medigap_policy_id, source_claim_id, reversed_payment_amount,
                      liability_restated)
    ctx.create("medigap_claim_crossovers", rid,
               medigap_claim_id=rid,
               medigap_policy_id=medigap_policy_id,
               customer_id=customer_id,
               event_type="medigap_claim_adjustment",
               medicare_claim_number=medicare_claim_number,
               date_of_service=date_of_service,
               processed_date=ctx.now()[:10],
               supplement_paid_amount=-round(float(reversed_payment_amount), 2),
               member_responsibility=round(float(liability_restated), 2),
               claim_status="adjusted",
               source_claim_id=source_claim_id)
    return (f"Restatement {rid} booked on policy {medigap_policy_id} against line {source_claim_id}: "
            f"{round(float(reversed_payment_amount), 2)} taken back and "
            f"{round(float(liability_restated), 2)} of recorded liability restated.")


@tool(owner="user", rw="write")
def repay_direct_benefit_f162ba18(ctx: ToolContext, medigap_policy_id: str, customer_id: str,
                                  source_claim_id: str, medicare_claim_number: str,
                                  date_of_service: str, repayment_amount: float,
                                  liability_credited: float) -> str:
    """Send money back to the plan yourself on a crossover claim line it paid you directly and
    should not have. One call hands over one repayment: the amount you authorise leaves the account
    you are paying from, it is booked against that named line as money the plan has recovered from
    you, the liability the line records as standing to your credit is recorded with it, the year's
    deductible accumulator falls by that credited amount, and the entry stands on the claim record
    beside the line it answers with a status showing the money has been recovered. You can see it
    on the claim record as soon as the confirmation naming it comes back.

    Args:
        medigap_policy_id: Id class — the reference number of the Medicare Supplement policy the
            line sits on, read from the policy record held for you.
        customer_id: Id class — your member reference number, read from your member profile.
        source_claim_id: Id class — the reference number of the single processed crossover line the
            money answers, read from the claims that crossed over to that policy.
        medicare_claim_number: Fixed-format class — the number Medicare gave the original claim,
            carried over from that line exactly as it stands there, being a thirteen-character
            Medicare claim control number.
        date_of_service: Fixed-format class — the date the service was rendered, carried over from
            that line, written as YYYY-MM-DD.
        repayment_amount: Fixed-format class — the money you are sending back now, in USD, recorded
            to 2 decimal places and never negative; it is booked against the policy as a negative
            payment.
        liability_credited: Fixed-format class — the liability the line records as standing to your
            credit once the money is back, in USD, recorded to 2 decimal places and never negative.

    Returns:
        A confirmation sentence in plain text naming the reference number of the new claim record,
        the line it answers, the money returned and the liability credited. Receiving that sentence
        is what says the money has been taken and the entry stands on the claim record; no other
        value is returned.
    """
    rid = ctx.make_id("mgrec_", medigap_policy_id, source_claim_id, repayment_amount,
                      liability_credited)
    ctx.create("medigap_claim_crossovers", rid,
               medigap_claim_id=rid,
               medigap_policy_id=medigap_policy_id,
               customer_id=customer_id,
               event_type="medigap_claim_adjustment",
               medicare_claim_number=medicare_claim_number,
               date_of_service=date_of_service,
               processed_date=ctx.now()[:10],
               supplement_paid_amount=-round(float(repayment_amount), 2),
               member_responsibility=round(float(liability_credited), 2),
               claim_status="recovered",
               source_claim_id=source_claim_id)
    return (f"Repayment {rid} taken on policy {medigap_policy_id} against line {source_claim_id}: "
            f"{round(float(repayment_amount), 2)} returned and "
            f"{round(float(liability_credited), 2)} of liability credited.")


@tool(owner="agent", rw="write")
def settle_crossover_benefit_9f3dc765(ctx: ToolContext, medigap_policy_id: str, medigap_claim_id: str,
                                      supplement_payment_amount: float) -> str:
    """Settle a crossover claim line that is waiting on the supplement, by paying the plan letter's
    share of it. One call settles one named line: the money is paid to whoever submitted the line,
    the amount paid is recorded against it, the line moves from waiting to paid and carries the date
    the supplement finished with it, and what the policyholder still owes stands as the line already
    records it. The call has completed when the confirmation naming the settled line comes back.

    Args:
        medigap_policy_id: Id class — the reference number of the Medicare Supplement policy the
            line sits on, read from the policyholder's policy record.
        medigap_claim_id: Id class — the reference number of the single crossover claim line being
            settled, read from the claims that crossed over to that policy.
        supplement_payment_amount: Fixed-format class — the money the supplement pays on this line,
            in USD, recorded to 2 decimal places and never negative.

    Returns:
        A confirmation sentence in plain text naming the line settled, the policy it sits on, the
        amount paid and the date the supplement finished with it. Receiving that sentence is what
        says the line is paid; no other value is returned.
    """
    ctx.update("medigap_claim_crossovers", medigap_claim_id,
               supplement_paid_amount=round(float(supplement_payment_amount), 2),
               claim_status="paid",
               denial_reason_code="not_applicable",
               processed_date=ctx.now()[:10])
    return (f"Crossover line {medigap_claim_id} on policy {medigap_policy_id} settled: "
            f"{round(float(supplement_payment_amount), 2)} paid on {ctx.now()[:10]}.")

"""Hidden task tools for the auto_loan_payment_servicing difficulty of regional_retail_bank.

Each function performs exactly one atomic auto loan servicing write. None of them applies a
policy test, aggregates history, or works a figure out on the caller's behalf: the agent reads
the loan, its ledger and the borrower's other holdings, works the figure out from the published
rules, and passes it in. The tools are hidden: they are reached only through the paired
unlock/call meta tools.
"""

from erlbench import ToolContext, tool


@tool(owner="agent", rw="write")
def correct_loan_fee_ab5fa380(ctx: ToolContext, auto_loan_id: str, customer_id: str,
                              source_item_id: str, fee_code: str,
                              correction_amount: float) -> str:
    """Correct one charge standing on an auto loan by booking a correction entry against it.

    The entry is written against the charge named by the borrower's servicing agent and is
    recorded as a bank-error adjustment, so the loan's unpaid-fee balance falls by the amount
    passed in and the corrected charge is left standing at the remainder. The borrower sees the
    correction on the loan's activity as a fee adjustment dated today, and the loan's unpaid fees
    figure drops immediately. The call has completed when the confirmation text below is returned
    with the new reference of the correction entry in it.

    Args:
        auto_loan_id: Id class — the reference number of the auto loan whose charge is being
            corrected; read it from the loan record returned by the auto loan lookup before the
            call.
        customer_id: Id class — the reference number identifying the borrower who holds that
            loan; read it from the customer profile lookup before the call.
        source_item_id: Id class — the reference number of the single ledger entry that carries
            the charge being corrected; read it from the loan activity lookup before the call.
        fee_code: Enum class — which kind of charge the corrected entry carries, exactly as the
            loan activity shows it. Pass none where the entry being corrected carries no fee kind
            at all, which is the case only for an entry that is not one of the loan fee kinds.
            Pass late_charge where the charge was assessed against an installment that stayed
            unsatisfied past its grace days. Pass extension where the charge was assessed because
            installments were deferred to the end of the loan. Pass returned_payment where the
            charge was assessed because a payment was returned unpaid by the paying bank. Pass
            settlement_reversal where the charge is one that became due again when the payment
            that had paid it was returned.
        correction_amount: Fixed-format class — the amount taken off the charge by this
            correction, in USD with 2 decimal places, always positive and never more than the
            amount standing for that charge; pass it already rounded to the cent.

    Returns:
        A confirmation sentence naming the new correction entry's reference number, the loan
        reference number, the amount taken off in USD to the cent, and the loan's unpaid fee
        balance after the correction. Receiving that sentence means the correction entry exists
        on the loan's activity and the unpaid fee balance has been reduced.
    """
    rid = ctx.make_id("atx_", auto_loan_id, customer_id, source_item_id, fee_code, correction_amount)
    booked = round(float(correction_amount), 2)
    ctx.create("auto_transactions", rid, auto_txn_id=rid, auto_loan_id=auto_loan_id,
               customer_id=customer_id, event_type="auto_fee_waiver", amount=booked,
               posted_date=ctx.now()[:10], payment_channel="none", payment_type="none",
               fees_portion=0.0, interest_portion=0.0, principal_portion=0.0,
               installment_due_date="", reference_number="", counterparty_account_id="",
               fee_code=fee_code, source_item_id=source_item_id, adjustment_reason="bank_error",
               refund_destination="none")
    rows = ctx.find("auto_loans", auto_loan_id=auto_loan_id)
    remaining = 0.0
    if rows:
        remaining = round(float(rows[0].get("fees_due") or 0) - booked, 2)
        ctx.update("auto_loans", auto_loan_id, fees_due=remaining)
    return (f"Correction {rid} booked on auto loan {auto_loan_id}: {booked:.2f} USD taken off the "
            f"charge; unpaid fees on the loan are now {remaining:.2f} USD.")


@tool(owner="user", rw="write")
def post_installment_payment_1d25a699(ctx: ToolContext, auto_loan_id: str, customer_id: str,
                                      payment_amount: float, fees_portion: float,
                                      interest_portion: float, principal_portion: float,
                                      installment_due_date: str, next_installment_due_date: str,
                                      payment_channel: str) -> str:
    """Make a payment on your own auto loan and have it credited toward one scheduled installment.

    The payment posts to the loan's activity today with the split you give between unpaid
    charges, accrued interest and principal; the loan's unpaid fees and unpaid principal fall by
    those parts, the installment you name is credited and recorded as satisfied, the loan's next
    installment date moves to the date you give, and the loan's past-due day count returns to
    zero. You will see the payment on the loan's activity straight away with its own payment
    reference number. The call has completed when the confirmation text below comes back naming
    that payment reference number.

    Args:
        auto_loan_id: Id class — the reference number of your auto loan the payment posts to; the
            servicing agent reads it from the loan record and hands it over with this tool.
        customer_id: Id class — the reference number identifying you as the borrower on that
            loan; the servicing agent reads it from your customer profile and hands it over.
        payment_amount: Fixed-format class — the total you are paying today, in USD with 2
            decimal places, positive, and exactly the sum of the three parts below.
        fees_portion: Fixed-format class — the part of the payment that goes to the unpaid
            charges standing on the loan, in USD with 2 decimal places; pass 0.00 when no part of
            the payment goes to charges.
        interest_portion: Fixed-format class — the part of the payment that goes to the interest
            accrued on the loan, in USD with 2 decimal places; pass 0.00 when no part of the
            payment goes to interest.
        principal_portion: Fixed-format class — the part of the payment that goes to the unpaid
            principal of the loan, in USD with 2 decimal places; pass 0.00 when no part of the
            payment goes to principal.
        installment_due_date: Fixed-format class — the due date of the scheduled installment this
            payment is credited toward, written as YYYY-MM-DD in the loan's own calendar dates.
        next_installment_due_date: Fixed-format class — the due date the loan's next scheduled
            installment falls on once this one is satisfied, written as YYYY-MM-DD.
        payment_channel: Enum class — how you are making this payment. Pass none where the entry
            is not a payment at all and so carries no channel. Pass autopay_pcb where the bank
            drafts the installment automatically from your Piedmont Crescent checking account
            under a standing instruction. Pass pcb_transfer where you move the money yourself from
            a Piedmont Crescent account in online or branch banking. Pass external_ach where the
            money is drawn from an account you hold at another bank. Pass mail_check where you
            post a paper check to the loan servicing address. Pass branch where you pay in person
            at a branch counter. Pass debit_card_phone where you give a debit card to the
            servicing agent on the telephone and the payment is taken on that card.

    Returns:
        A confirmation sentence naming the loan reference number, the payment reference number
        assigned to this payment, the total paid in USD to the cent, the three parts it was split
        into, the installment it was credited toward, and the loan's next installment date.
        Receiving that sentence means the payment is on the loan's activity and the loan is
        recorded as current.
    """
    rid = ctx.make_id("atx_", auto_loan_id, customer_id, payment_amount, installment_due_date)
    reference = str(int(rid[-12:], 16))[:12].zfill(12)
    total = round(float(payment_amount), 2)
    fees = round(float(fees_portion), 2)
    interest = round(float(interest_portion), 2)
    principal = round(float(principal_portion), 2)
    ctx.create("auto_transactions", rid, auto_txn_id=rid, auto_loan_id=auto_loan_id,
               customer_id=customer_id, event_type="auto_payment", amount=total,
               posted_date=ctx.now()[:10], payment_channel=payment_channel,
               payment_type="scheduled", fees_portion=fees, interest_portion=interest,
               principal_portion=principal, installment_due_date=installment_due_date,
               reference_number=reference, counterparty_account_id="", fee_code="none",
               source_item_id="", adjustment_reason="none", refund_destination="none")
    rows = ctx.find("auto_loans", auto_loan_id=auto_loan_id)
    if rows:
        ctx.update("auto_loans", auto_loan_id,
                   principal_balance=round(float(rows[0].get("principal_balance") or 0) - principal, 2),
                   fees_due=round(float(rows[0].get("fees_due") or 0) - fees, 2),
                   last_payment_date=ctx.now()[:10],
                   next_payment_due_date=next_installment_due_date,
                   days_past_due=0)
    return (f"Payment {reference} (entry {rid}) of {total:.2f} USD posted to auto loan "
            f"{auto_loan_id}: {fees:.2f} to charges, {interest:.2f} to interest, "
            f"{principal:.2f} to principal, credited to the installment due "
            f"{installment_due_date}; the next installment is due {next_installment_due_date}.")


@tool(owner="user", rw="write")
def set_loan_autopay_8313b066(ctx: ToolContext, auto_loan_id: str, autopay_source_account_id: str,
                              autopay_enrolled: bool, restated_apr: float,
                              rate_discounts: str) -> str:
    """Set or withdraw the standing instruction that drafts your own auto loan installment from a checking account, and put the loan's rate on the footing that instruction leaves it.

    The instruction on the loan is set to what you pass: when it is put in place the named
    checking account is recorded as the account the installment is drafted from, and when it is
    withdrawn the loan carries no drafting account at all and the installment must be paid some
    other way. The loan's annual percentage rate is rewritten to the figure you pass and the
    reductions recorded against the rate are rewritten to the value you pass, so the borrower sees
    the new rate on the loan straight away. The call has completed when the confirmation text
    below comes back naming the loan and the rate now recorded.

    Args:
        auto_loan_id: Id class — the reference number of your auto loan whose drafting
            instruction is being set; the servicing agent reads it from the loan record and hands
            it over with this tool.
        autopay_source_account_id: Id class — the reference number of the Piedmont Crescent
            checking account the installment is drafted from, or was drafted from up to now; the
            servicing agent reads it from the checking account lookup and hands it over.
        autopay_enrolled: Enum class — whether the loan is to carry a standing drafting
            instruction after this call. true: the installment is to be drafted automatically from
            the checking account named above on each due date. false: no automatic draft is to
            stand on the loan and the installment is to be paid by some other means.
        restated_apr: Fixed-format class — the annual percentage rate the loan is to carry from
            now on, as a percent with 2 decimal places; pass it already rounded.
        rate_discounts: Enum class — which reductions the restated rate is recorded as carrying.
            Pass none where the rate carries no reduction at all. Pass autopay where the rate
            carries only the reduction earned by the standing drafting instruction. Pass
            relationship where the rate carries only the reduction earned by the qualifying
            checking relationship held at funding. Pass autopay_and_relationship where the rate
            carries both of those reductions together.

    Returns:
        A confirmation sentence naming the loan reference number, whether a standing drafting
        instruction now stands on it and against which checking account, the annual percentage
        rate now recorded as a percent to two decimals, and the reductions recorded against it.
        Receiving that sentence means the loan record carries the new instruction and the new rate.
    """
    enrolled = bool(autopay_enrolled)
    source = autopay_source_account_id if enrolled else ""
    rate = round(float(restated_apr), 2)
    rows = ctx.find("auto_loans", auto_loan_id=auto_loan_id)
    if rows:
        ctx.update("auto_loans", auto_loan_id, autopay_enrolled=enrolled,
                   autopay_source_account_id=source, interest_rate=rate,
                   rate_discounts=rate_discounts)
    state = f"drafted from checking account {autopay_source_account_id}" if enrolled else "no standing draft"
    return (f"Auto loan {auto_loan_id} now carries {state}; the rate recorded is {rate:.2f} "
            f"percent with reductions '{rate_discounts}'.")


@tool(owner="agent", rw="write")
def change_payment_due_day_9dcc583e(ctx: ToolContext, auto_loan_id: str, realigned_due_day: int,
                                    next_installment_due_date: str) -> str:
    """Move the day of the month an auto loan installment falls due to a new day.

    The loan's due day is rewritten to the day passed in, the loan's next installment date is
    rewritten to the date passed in, and today's date is recorded on the loan as the date of its
    most recent due day change, which is what the once-per-window record is read from afterwards.
    The borrower sees the new due day and the new next installment date on the loan record; the
    maturity date and the installment amount are untouched. The call has completed when the
    confirmation text below comes back naming the new day.

    Args:
        auto_loan_id: Id class — the reference number of the auto loan whose due day is being
            moved; read it from the loan record returned by the auto loan lookup before the call.
        realigned_due_day: Fixed-format class — the day of the month the installment is to fall
            due on from now on, given as an integer 1-28 with no leading zero and no other
            punctuation.
        next_installment_due_date: Fixed-format class — the date the next installment falls due
            once the day has moved, written as YYYY-MM-DD.

    Returns:
        A confirmation sentence naming the loan reference number, the day of the month the
        installment now falls due on, the date of the next installment, and the date the change
        was recorded. Receiving that sentence means the loan record carries the new due day.
    """
    day = int(realigned_due_day)
    rows = ctx.find("auto_loans", auto_loan_id=auto_loan_id)
    if rows:
        ctx.update("auto_loans", auto_loan_id, payment_due_day=day,
                   next_payment_due_date=next_installment_due_date,
                   last_due_date_change_date=ctx.now()[:10])
    return (f"Auto loan {auto_loan_id} now falls due on day {day} of the month; the next "
            f"installment is due {next_installment_due_date} and the change was recorded "
            f"{ctx.now()[:10]}.")


@tool(owner="user", rw="write")
def post_gap_refund_16f4decd(ctx: ToolContext, auto_loan_id: str, customer_id: str,
                             refund_amount: float) -> str:
    """Give your own instruction to close out the guaranteed asset protection waiver coverage financed with your auto loan, and have the refund owed on it entered against that loan.

    One call records your confirmed cancellation instruction as a service request of its own on the
    loan, ends the coverage, records today as the date it was cancelled, and posts a refund entry on
    the loan's activity for the amount passed in, which reduces the loan's unpaid principal by that
    amount. You will see the cancellation recorded as confirmed, the coverage shown as no longer in
    force, and the refund entry dated today on the loan's activity with the principal lower by the
    refunded sum. The call has completed when the confirmation text below comes back naming the
    refund entry's reference number.

    Args:
        auto_loan_id: Id class — the reference number of your auto loan whose waiver coverage is
            being closed out; the servicing agent reads it from the loan record and hands it over
            with this tool.
        customer_id: Id class — the reference number identifying you as the borrower on that loan;
            the servicing agent reads it from your customer profile and hands it over.
        refund_amount: Fixed-format class — the refund entered against the loan, in USD with 2
            decimal places, positive and never more than the charge financed at funding; pass it
            already rounded to the cent.

    Returns:
        A confirmation sentence naming the loan reference number, the reference number of the
        recorded cancellation instruction, the new refund entry's reference number, the refunded sum
        in USD to the cent, and the loan's unpaid principal after the entry. Receiving that sentence
        means your cancellation stands recorded as confirmed, the coverage is closed out and the
        refund stands on the loan's activity.
    """
    req = ctx.make_id("areq_", auto_loan_id, customer_id, "gap_cancellation")
    ctx.create("auto_requests", req, auto_request_id=req, customer_id=customer_id,
               auto_loan_id=auto_loan_id, request_type="gap_cancellation", requested_due_day="",
               extension_installments="", payoff_date="", request_status="confirmed",
               created_at=ctx.now())
    rid = ctx.make_id("atx_", auto_loan_id, customer_id, refund_amount)
    booked = round(float(refund_amount), 2)
    ctx.create("auto_transactions", rid, auto_txn_id=rid, auto_loan_id=auto_loan_id,
               customer_id=customer_id, event_type="auto_gap_refund", amount=booked,
               posted_date=ctx.now()[:10], payment_channel="none", payment_type="none",
               fees_portion=0.0, interest_portion=0.0, principal_portion=0.0,
               installment_due_date="", reference_number="", counterparty_account_id="",
               fee_code="none", source_item_id="", adjustment_reason="none",
               refund_destination="none")
    rows = ctx.find("auto_loans", auto_loan_id=auto_loan_id)
    remaining = 0.0
    if rows:
        remaining = round(float(rows[0].get("principal_balance") or 0) - booked, 2)
        ctx.update("auto_loans", auto_loan_id, gap_coverage=False,
                   gap_cancellation_date=ctx.now()[:10], principal_balance=remaining)
    return (f"Cancellation {req} recorded as confirmed and waiver coverage on auto loan "
            f"{auto_loan_id} closed out; refund entry {rid} of {booked:.2f} USD entered against the "
            f"loan, whose unpaid principal is now {remaining:.2f} USD.")


@tool(owner="agent", rw="write")
def post_loan_payoff_a84c6454(ctx: ToolContext, auto_loan_id: str, customer_id: str,
                              settlement_amount: float, fees_portion: float,
                              interest_portion: float, principal_portion: float,
                              payment_channel: str) -> str:
    """Post a borrower's settlement of an auto loan in full to that loan and close it.

    The payment posts to the loan's activity today with the split passed in between unpaid charges,
    accrued interest and principal, and it settles the loan: unpaid principal and unpaid charges
    both fall to zero, the loan is shown as paid off with today as its closing date, the past-due
    day count returns to zero, and the lien on the vehicle is moved to awaiting release so the title
    work can start. The borrower sees the payment and the closed loan straight away with the
    payment's own reference number. The call has completed when the confirmation text below comes
    back naming that reference number.

    Args:
        auto_loan_id: Id class — the reference number of the auto loan being settled; read it from
            the loan record returned by the auto loan lookup before the call.
        customer_id: Id class — the reference number identifying the borrower on that loan; read it
            from the customer profile lookup before the call.
        settlement_amount: Fixed-format class — the total the borrower is paying to settle the loan,
            in USD with 2 decimal places, positive, and exactly the sum of the three parts below.
        fees_portion: Fixed-format class — the part of the settlement that goes to the unpaid
            charges standing on the loan, in USD with 2 decimal places; pass 0.00 when no charge
            stands.
        interest_portion: Fixed-format class — the part of the settlement that goes to the interest
            accrued on the loan, in USD with 2 decimal places; pass 0.00 when no interest is owed.
        principal_portion: Fixed-format class — the part of the settlement that goes to the unpaid
            principal, in USD with 2 decimal places; pass 0.00 when no principal remains.
        payment_channel: Enum class — how the borrower is settling the loan. Pass none where the entry is
            not a payment at all and so carries no channel. Pass autopay_pcb where the bank drafts
            the money automatically from your Piedmont Crescent checking account under a standing
            instruction. Pass pcb_transfer where you move the money yourself from a Piedmont
            Crescent account in online or branch banking. Pass external_ach where the money is drawn
            from an account you hold at another bank. Pass mail_check where you post a paper check
            to the loan servicing address. Pass branch where you pay in person at a branch counter.
            Pass debit_card_phone where you give a debit card to the servicing agent on the
            telephone and the payment is taken on that card.

    Returns:
        A confirmation sentence naming the loan reference number, the payment reference number
        assigned to this settlement, the total paid in USD to the cent, the three parts it was split
        into, the closing date recorded on the loan and the lien's new state. Receiving that
        sentence means the loan is settled and closed.
    """
    rid = ctx.make_id("atx_", auto_loan_id, customer_id, settlement_amount)
    reference = str(int(rid[-12:], 16))[:12].zfill(12)
    total = round(float(settlement_amount), 2)
    fees = round(float(fees_portion), 2)
    interest = round(float(interest_portion), 2)
    principal = round(float(principal_portion), 2)
    ctx.create("auto_transactions", rid, auto_txn_id=rid, auto_loan_id=auto_loan_id,
               customer_id=customer_id, event_type="auto_payment", amount=total,
               posted_date=ctx.now()[:10], payment_channel=payment_channel, payment_type="payoff",
               fees_portion=fees, interest_portion=interest, principal_portion=principal,
               installment_due_date="", reference_number=reference, counterparty_account_id="",
               fee_code="none", source_item_id="", adjustment_reason="none", refund_destination="none")
    if ctx.find("auto_loans", auto_loan_id=auto_loan_id):
        ctx.update("auto_loans", auto_loan_id, principal_balance=0.0, fees_due=0.0,
                   status="paid_off", closed_date=ctx.now()[:10], last_payment_date=ctx.now()[:10],
                   days_past_due=0, lien_status="release_pending")
    return (f"Settlement {reference} (entry {rid}) of {total:.2f} USD posted to auto loan "
            f"{auto_loan_id}: {fees:.2f} to charges, {interest:.2f} to interest, {principal:.2f} "
            f"to principal; the loan is closed as of {ctx.now()[:10]} and the lien is awaiting release.")

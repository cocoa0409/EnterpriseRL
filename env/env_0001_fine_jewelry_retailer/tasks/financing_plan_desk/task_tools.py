"""Hidden task tools for the Belrose Fine Jewelers promotional financing desk.

Each function performs exactly one atomic write on the financing register. None of
them aggregates history, judges eligibility, or refuses on a business ground: the
agent works the figure out from the published rules and the records and passes it in.
"""

from erlbench import ToolContext, tool


@tool(owner="agent", rw="write")
def book_returned_payment_charge_6a9e81de(ctx: ToolContext, financing_plan_id: str,
                                          source_entry_id: str, charge_amount: float) -> str:
    """Charge a promotional financing plan for a payment the bank sent back unpaid.

    One call books a single returned-payment charge against the plan's billing history,
    tied to the payment entry that came back, and dated and cycled on today's date. The
    charge is added to the plan's billing history as a new positive entry carrying the
    returned-payment charge code, so the customer will see it on the next statement and
    the plan's own balance record is left for the settlement or statement step to restate.
    The call has completed when the confirmation naming the new billing entry comes back.

    Args:
        financing_plan_id: Id class — the reference number of the promotional financing
            plan record the charge is booked to, read from the financing plan lookup for
            this customer before the call.
        source_entry_id: Id class — the reference number of the billing entry that records
            the payment the bank returned unpaid; read from the plan's billing history
            lookup, where returned payments carry the returned outcome.
        charge_amount: Fixed-format class — the money charged for the returned payment, in
            USD as a positive number with 2 decimal places, half-up at the cent and with no
            currency symbol or thousands separator; an empty value is not accepted.

    Returns:
        A single confirmation sentence in plain text. It names the reference number minted
        for the new billing entry, the plan reference it was booked to, and the charge as
        booked in USD to two decimal places. A sentence naming that new entry reference is
        what indicates the charge is on the plan's billing history.
    """
    rid = ctx.make_id("frpf_", financing_plan_id, source_entry_id, charge_amount)
    ctx.create("financing_ledger", rid, ledger_entry_id=rid,
               financing_plan_id=financing_plan_id,
               event_type="financing_returned_payment_fee_assessed",
               posted_date=ctx.now()[:10], billing_cycle=ctx.now()[:7],
               amount=round(float(charge_amount), 2), fee_code="returned_payment",
               source_entry_id=source_entry_id, allocation_bucket="fees")
    return (f"Returned-payment charge booked as billing entry {rid} on plan "
            f"{financing_plan_id} for {round(float(charge_amount), 2):.2f} USD.")


@tool(owner="agent", rw="write")
def book_lateness_charge_0092ea40(ctx: ToolContext, financing_plan_id: str,
                                  lateness_charge: float, payment_due_date: str,
                                  fee_code: str) -> str:
    """Charge a promotional financing plan for a scheduled payment that was not made in time.

    One call books a single lateness charge against the plan's billing history for one
    missed payment due date, dated and cycled on today's date. The charge goes on as a new
    positive entry carrying the lateness code given, and the customer sees it on the next
    statement; the plan record's own balance and delinquency fields are not touched by this
    call. The call has completed when the confirmation naming the new billing entry returns.

    Args:
        financing_plan_id: Id class — the reference number of the promotional financing plan
            record the lateness charge is booked to, read from the financing plan lookup for
            this customer before the call.
        lateness_charge: Fixed-format class — the money charged for the lateness, in USD as a
            positive number with 2 decimal places, half-up at the cent, with no currency
            symbol and no thousands separator; an empty value is not accepted.
        payment_due_date: Fixed-format class — the payment due date that was missed, written
            as YYYY-MM-DD in the store's own calendar dating, exactly as it is printed on the
            statement for that billing cycle and read from the plan's billing history.
        fee_code: Enum class — which priced charge this entry is. Use late_fee_first when the
            entry is the opening lateness charge of the run being priced; late_fee_repeat when
            an earlier lateness already counts against the plan in the stretch being read;
            returned_payment only where the entry prices a payment the bank sent back;
            deferred_interest only where the entry bills held-back promotional interest;
            paper_statement only where the entry prices a posted paper statement;
            prepayment only where the entry prices clearing a plan ahead of its term;
            not_applicable only where the entry prices nothing at all.

    Returns:
        A single confirmation sentence in plain text naming the reference number minted for
        the new billing entry, the plan reference it was booked to, the missed due date it
        answers, and the charge as booked in USD to two decimal places. That sentence naming
        the new entry reference is what indicates the charge is on the billing history.
    """
    rid = ctx.make_id("flf_", financing_plan_id, lateness_charge, payment_due_date, fee_code)
    ctx.create("financing_ledger", rid, ledger_entry_id=rid,
               financing_plan_id=financing_plan_id,
               event_type="financing_late_fee_assessed",
               posted_date=ctx.now()[:10], billing_cycle=ctx.now()[:7],
               amount=round(float(lateness_charge), 2), fee_code=fee_code,
               payment_due_date=payment_due_date, allocation_bucket="fees")
    return (f"Lateness charge booked as billing entry {rid} on plan {financing_plan_id} "
            f"for the {payment_due_date} due date, {round(float(lateness_charge), 2):.2f} USD.")


@tool(owner="user", rw="write")
def confirm_plan_settlement_d71750ce(ctx: ToolContext, financing_plan_id: str,
                                     settlement_amount: float) -> str:
    """Settle a promotional financing plan in full and close it, as the customer themselves.

    One call takes the money the customer puts up to clear the plan, credits it to the plan's
    billing history as a settled payment made through the finance desk today, sets what the
    plan still owes to nothing, records today as the day the plan closed and as the day of the
    most recent settled payment, and moves the plan into its settled state. Afterwards the
    customer can see the plan closed and nothing further billed on it. The call has completed
    when the confirmation naming the new billing entry and the closed plan comes back.

    Args:
        financing_plan_id: Id class — the reference number of the promotional financing plan
            record the customer is clearing, read from the financing plan lookup before the
            call and handed to the customer with the tool.
        settlement_amount: Fixed-format class — the money the customer puts up to clear the
            plan in full, in USD as a positive number with 2 decimal places, half-up at the
            cent, with no currency symbol and no thousands separator; an empty value is not
            accepted.

    Returns:
        A single confirmation sentence in plain text naming the reference number minted for
        the settled payment entry, the plan reference now closed, and the money taken in USD
        to two decimal places. That sentence naming the closed plan is what indicates the
        settlement has gone through and nothing further stands on the plan.
    """
    rid = ctx.make_id("fset_", financing_plan_id, settlement_amount)
    ctx.create("financing_ledger", rid, ledger_entry_id=rid,
               financing_plan_id=financing_plan_id,
               event_type="financing_payment_posted",
               posted_date=ctx.now()[:10], billing_cycle=ctx.now()[:7],
               amount=-round(float(settlement_amount), 2), payment_channel="phone_agent",
               payment_outcome="settled", allocation_bucket="mixed")
    ctx.update("financing_plans", financing_plan_id, status="paid_off",
               closed_date=ctx.now()[:10], last_payment_date=ctx.now()[:10],
               current_balance=0.0)
    return (f"Settled payment entry {rid} taken for {round(float(settlement_amount), 2):.2f} USD; "
            f"plan {financing_plan_id} is closed and settled.")


@tool(owner="agent", rw="write")
def issue_cycle_statement_c71da302(ctx: ToolContext, financing_plan_id: str,
                                   statement_amount: float, closing_date: str,
                                   payment_due_date: str) -> str:
    """Close a billing cycle on a promotional financing plan and present its statement.

    One call puts a statement on the plan's billing history for the cycle that closed: it records
    the amount the statement presents to the customer, the date the cycle closed and the date the
    money is due, and cycles the entry to the month the closing date falls in. Nothing else about
    the plan moves; the balance and the standing are untouched. Afterwards the customer can see the
    statement and what it asks for. The call has completed when the confirmation naming the new
    billing entry comes back.

    Args:
        financing_plan_id: Id class — the reference number of the promotional financing plan record
            whose cycle is being closed, read from the financing plan lookup for this customer
            before the call.
        statement_amount: Fixed-format class — the money the statement presents for the cycle, given
            in USD as a positive number with 2 decimal places, half-up at the cent, with no currency
            symbol and no thousands separator; an empty value is not accepted.
        closing_date: Fixed-format class — the date the billing cycle closed, written as YYYY-MM-DD
            in the store's own calendar dating; an empty value is not accepted.
        payment_due_date: Fixed-format class — the date the money the statement presents falls due,
            written as YYYY-MM-DD in the store's own calendar dating; an empty value is not
            accepted.

    Returns:
        A single confirmation sentence in plain text naming the reference number minted for the new
        billing entry, the plan reference it was booked to, the closing date of the cycle, the date
        the money falls due and the amount presented in USD to two decimal places. That sentence
        naming the new entry reference is what indicates the statement is on the billing history.
    """
    rid = ctx.make_id("fstm_", financing_plan_id, statement_amount, closing_date)
    ctx.create("financing_ledger", rid, ledger_entry_id=rid,
               financing_plan_id=financing_plan_id,
               event_type="financing_statement_issued",
               posted_date=closing_date, billing_cycle=closing_date[:7],
               amount=round(float(statement_amount), 2),
               payment_due_date=payment_due_date, allocation_bucket="not_applicable")
    return (f"Statement booked as billing entry {rid} on plan {financing_plan_id} for the cycle "
            f"closing {closing_date}, {round(float(statement_amount), 2):.2f} USD due "
            f"{payment_due_date}.")


@tool(owner="agent", rw="write")
def apply_service_recovery_giveback_b70a9c9e(ctx: ToolContext, financing_plan_id: str,
                                             source_entry_id: str, giveback_amount: float) -> str:
    """Give money back on a promotional financing plan to put right a failure of the chain's own.

    One call books a single give-back on the plan's billing history under the service-recovery
    ground, tied to the priced charge it answers, dated and cycled on today's date and allocated to
    fees. The give-back goes on as a negative entry against what is owed, so the customer sees the
    money come off the plan, and because it is recorded under the service-recovery ground it does
    not consume the courtesy allowance the plan carries. The call has completed when the
    confirmation naming the new billing entry comes back.

    Args:
        financing_plan_id: Id class — the reference number of the promotional financing plan record
            the give-back is booked to, read from the financing plan lookup for this customer before
            the call.
        source_entry_id: Id class — the reference number of the priced charge entry the give-back
            answers, read from the plan's billing history lookup, where priced charges carry the
            charge family and a positive amount.
        giveback_amount: Fixed-format class — the money given back to the plan, given in USD as a
            positive number with 2 decimal places, half-up at the cent, with no currency symbol and
            no thousands separator; the entry itself is booked negative because it reduces what is
            owed.

    Returns:
        A single confirmation sentence in plain text naming the reference number minted for the new
        billing entry, the plan reference it was booked to, the charge entry it answers and the
        money given back in USD to two decimal places. That sentence naming the new entry reference
        is what indicates the give-back is on the plan's billing history.
    """
    rid = ctx.make_id("fgb_", financing_plan_id, source_entry_id, giveback_amount)
    ctx.create("financing_ledger", rid, ledger_entry_id=rid,
               financing_plan_id=financing_plan_id,
               event_type="financing_fee_waiver_applied",
               posted_date=ctx.now()[:10], billing_cycle=ctx.now()[:7],
               amount=-round(float(giveback_amount), 2), waiver_reason_code="service_recovery",
               source_entry_id=source_entry_id, allocation_bucket="fees")
    return (f"Give-back booked as billing entry {rid} on plan {financing_plan_id} against charge "
            f"{source_entry_id}, {round(float(giveback_amount), 2):.2f} USD off what is owed.")


@tool(owner="agent", rw="write")
def update_scheduled_payment_2c04479a(ctx: ToolContext, financing_plan_id: str,
                                      rebuilt_monthly_payment: float) -> str:
    """Set the payment a promotional financing plan bills each cycle to a rebuilt figure.

    One call writes the given figure onto the plan record as the payment it will bill from the next
    cycle onward, replacing whatever the plan was billing before. Nothing else about the plan moves:
    its standing, its balance and its promotional term are untouched, and no entry is booked to the
    billing history. Afterwards the customer sees the new payment on the plan and on the next
    statement. The call has completed when the confirmation naming the plan and the new payment
    comes back.

    Args:
        financing_plan_id: Id class — the reference number of the promotional financing plan record
            whose billed payment is being set, read from the financing plan lookup for this
            customer before the call.
        rebuilt_monthly_payment: Fixed-format class — the payment the plan is to bill each cycle,
            given in USD as a positive number with 2 decimal places, half-up at the cent, with no
            currency symbol and no thousands separator; an empty value is not accepted.

    Returns:
        A single confirmation sentence in plain text naming the plan reference and the payment now
        standing on it in USD to two decimal places. That sentence naming the new payment is what
        indicates the plan record now bills that figure.
    """
    ctx.update("financing_plans", financing_plan_id,
               scheduled_monthly_payment=round(float(rebuilt_monthly_payment), 2))
    return (f"Plan {financing_plan_id} now bills "
            f"{round(float(rebuilt_monthly_payment), 2):.2f} USD each cycle.")


@tool(owner="user", rw="write")
def confirm_hardship_schedule_eb08e7db(ctx: ToolContext, financing_plan_id: str,
                                       reduced_payment_amount: float,
                                       hardship_plan_code: str) -> str:
    """Take up a replacement payment arrangement on a promotional financing plan, as the customer.

    One call commits the customer to the arrangement named and to the reduced payment given: the
    plan record moves into its arrangement standing, records which arrangement is in force, and
    bills the reduced figure each cycle in place of what it billed before. The balance, the
    promotional term and the billing history are untouched. Afterwards the customer sees the plan
    running on the arrangement at the reduced payment. The call has completed when the confirmation
    naming the plan, the arrangement and the reduced payment comes back.

    Args:
        financing_plan_id: Id class — the reference number of the promotional financing plan record
            the customer is taking the arrangement on, read from the financing plan lookup before
            the call and handed to the customer with the tool.
        reduced_payment_amount: Fixed-format class — the payment the customer commits to each cycle
            while the arrangement runs, given in USD as a positive number with 2 decimal places,
            half-up at the cent, with no currency symbol and no thousands separator; an empty value
            is not accepted.
        hardship_plan_code: Enum class — which arrangement is being taken up. Use reduced_payment
            when the customer keeps paying every cycle at a smaller figure; interest_pause when the
            arrangement stops interest running rather than lowering the payment; payment_deferral
            when whole cycles are put off to the end rather than paid at a smaller figure; and none
            only when the plan is to run on its ordinary schedule with no arrangement at all.

    Returns:
        A single confirmation sentence in plain text naming the plan reference, the arrangement now
        in force and the payment the plan will bill each cycle in USD to two decimal places. That
        sentence naming the arrangement is what indicates the plan is running on it.
    """
    ctx.update("financing_plans", financing_plan_id, status="in_hardship",
               hardship_plan_code=hardship_plan_code,
               scheduled_monthly_payment=round(float(reduced_payment_amount), 2))
    return (f"Plan {financing_plan_id} is now running on the {hardship_plan_code} arrangement at "
            f"{round(float(reduced_payment_amount), 2):.2f} USD each cycle.")

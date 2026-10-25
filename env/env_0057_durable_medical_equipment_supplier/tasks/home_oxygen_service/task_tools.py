"""Hidden task tools of the home_oxygen_service difficulty (Summit Ridge Home Medical, home oxygen).

Each tool performs one atomic write on the patient's home oxygen records with the values the
caller passes in. The tools do not look up policy, do not check whether a step is due and do not
compute any amount or date: the agent works those out from the published policies and the records,
and the tool lands the result exactly as given.
"""

from erlbench import ToolContext, tool


@tool(owner="agent", rw="write")
def record_oxygen_setup_e2e7878b(ctx: ToolContext, oxygen_holding_id: str, coverage_id: str, setup_date: str,
                                 serial_number: str) -> str:
    """Record that a home oxygen system awaiting setup has been set up, so that its payment period
    is open. One call moves the patient's oxygen record from awaiting setup to an active rental,
    names the coverage record the rental is billed to, writes the setup date as both the setup date
    and the first day of the payment period, and stores the serial number of the stationary unit now
    in use. Afterwards the oxygen record shows status rental_active with that coverage, setup date
    and serial number. Success is the confirmation line
    returned below; nothing else on the record changes.

    Args:
        oxygen_holding_id: Id class — the reference number of the patient's home oxygen record,
            read from the oxygen record lookup before the call.
        coverage_id: Id class — the reference number of the coverage record the rental is billed
            to, read from the coverage lookup before the call.
        setup_date: Fixed-format class — the date the payment period of the system begins, written
            as YYYY-MM-DD (calendar date, no time part); stored unchanged as the setup date and as
            the payment-period start date.
        serial_number: Verbatim class — the serial number of the stationary unit exactly as it
            appears on the setup delivery in the patient's oxygen service history; copy it
            character for character with no change (verbatim).

    Returns:
        A one-line text confirmation of the form "Oxygen record <oxygen_holding_id> set up: status
        rental_active, coverage <coverage_id>, setup date <setup_date>, payment period from <setup_date>, unit
        <serial_number>." Its presence means the record was updated; the oxygen record lookup then
        shows the same values.
    """
    ctx.update("oxygen_holdings", oxygen_holding_id, status="rental_active", coverage_id=coverage_id,
               setup_date=setup_date, rental_period_start_date=setup_date, serial_number=serial_number)
    return (f"Oxygen record {oxygen_holding_id} set up: status rental_active, coverage {coverage_id}, setup date {setup_date}, "
            f"payment period from {setup_date}, unit {serial_number}.")


@tool(owner="agent", rw="write")
def record_oxygen_equipment_payment_51bbc3fc(ctx: ToolContext, oxygen_holding_id: str, coverage_id: str,
                                             service_from_date: str, adjudication_date: str,
                                             claim_number: str, hcpcs_code: str, flow_modifier: str,
                                             rental_month_number: int, portable_allowed_amount: float,
                                             allowed_amount: float) -> str:
    """Post a monthly oxygen equipment claim that the patient's coverage paid in full, leaving
    nothing for the patient to pay. One call adds one paid equipment-month line to the patient's
    oxygen claim history: the payer's allowed amount is recorded as both the allowed and the paid
    amount, the patient share is recorded as 0.00, and the paid month counts toward the payment
    period. Afterwards the oxygen claim lookup shows the new paid line with the values given.

    Args:
        oxygen_holding_id: Id class — the reference number of the patient's home oxygen record,
            read from the oxygen record lookup before the call.
        coverage_id: Id class — the reference number of the coverage record that paid the month,
            read from the coverage lookup before the call.
        service_from_date: Fixed-format class — the first day of the equipment month paid,
            written as YYYY-MM-DD.
        adjudication_date: Fixed-format class — the date of the payer's remittance that paid the
            month, written as YYYY-MM-DD.
        claim_number: Verbatim class — the payer's claim control number for the month exactly as
            the patient reads it from the payer's statement; copy it character for character
            with no change (verbatim).
        hcpcs_code: Enum class — the stationary equipment code billed on the line: E1390 when the
            stationary unit is an oxygen concentrator; E0439 when the stationary unit is a liquid
            oxygen reservoir; E0442 when the line is a liquid contents month, which this tool never
            posts; E0443 when the line is a gaseous contents month, which this tool never posts.
        flow_modifier: Enum class — the flow-rate modifier on the line: QE when the prescribed
            flow in force is below the low-flow threshold; QG when it is above the high-flow
            threshold and no portable equipment is billable; QF when it is above the high-flow
            threshold and portable equipment is billable; none when the flow sits between the
            two thresholds.
        rental_month_number: Fixed-format class — the ordinal of the equipment month within the
            payment period, a non-negative integer (1 for the first month).
        portable_allowed_amount: Fixed-format class — the part of the allowed amount that pays the
            portable add-on, in USD rounded to 2 decimal places; 0.00 when no portable add-on is
            paid on the month.
        allowed_amount: Fixed-format class — the payer's allowed amount for the whole line in USD,
            rounded to 2 decimal places (stored as given, also as the amount paid).

    Returns:
        A one-line text confirmation "Posted paid-in-full equipment month <rental_month_number>
        (<service_from_date>) on oxygen record <oxygen_holding_id>: line <line id>, allowed
        <allowed_amount>, paid <allowed_amount>, patient share 0.00." where <line id> is the new
        claim line reference (prefix oxb_). Its presence means the paid line was added.
    """
    rid = ctx.make_id("oxb_", oxygen_holding_id, coverage_id, service_from_date, adjudication_date,
                      claim_number, hcpcs_code, flow_modifier, rental_month_number,
                      portable_allowed_amount, allowed_amount)
    customer = (ctx.find("oxygen_holdings", oxygen_holding_id=oxygen_holding_id) or [{}])[0].get("customer_id")
    amount = round(float(allowed_amount), 2)
    ctx.create("oxygen_billing", rid, oxygen_bill_id=rid, oxygen_holding_id=oxygen_holding_id,
               customer_id=customer, event_type="oxygen_rental_paid", coverage_id=coverage_id,
               hcpcs_code=hcpcs_code, flow_modifier=flow_modifier,
               rental_month_number=int(rental_month_number), service_from_date=service_from_date,
               adjudication_date=adjudication_date, allowed_amount=amount,
               portable_allowed_amount=round(float(portable_allowed_amount), 2),
               payer_paid_amount=amount, patient_responsibility=0.0, claim_number=claim_number,
               denial_reason="none", reversal_reason="none")
    return (f"Posted paid-in-full equipment month {int(rental_month_number)} ({service_from_date}) on oxygen "
            f"record {oxygen_holding_id}: line {rid}, allowed {amount:.2f}, paid {amount:.2f}, patient share 0.00.")


@tool(owner="agent", rw="write")
def record_oxygen_suspension_f17584ff(ctx: ToolContext, oxygen_holding_id: str, suspended_date: str) -> str:
    """Record that an active home oxygen rental is suspended for an inpatient or skilled nursing
    stay. One call moves the patient's oxygen record from rental_active to suspended and writes the
    date the suspension began; while the record is suspended no equipment month that begins is
    billed. Afterwards the oxygen record lookup shows status suspended with that date.

    Args:
        oxygen_holding_id: Id class — the reference number of the patient's home oxygen record,
            read from the oxygen record lookup before the call.
        suspended_date: Fixed-format class — the date the suspension began, written as
            YYYY-MM-DD.

    Returns:
        A one-line text confirmation "Oxygen record <oxygen_holding_id> suspended from
        <suspended_date>." Its presence means the record now shows status suspended.
    """
    ctx.update("oxygen_holdings", oxygen_holding_id, status="suspended", suspended_date=suspended_date)
    return f"Oxygen record {oxygen_holding_id} suspended from {suspended_date}."


@tool(owner="user", rw="write")
def restart_oxygen_payment_period_b66f451e(ctx: ToolContext, oxygen_holding_id: str,
                                           rental_period_start_date: str, qualifying_test_date: str,
                                           qualifying_spo2: int, rx_date: str) -> str:
    """The patient's own decision to keep their home oxygen with Summit Ridge under a new payment
    period after a long break in need. One call reopens the patient's suspended oxygen record as an
    active rental, clears the suspension date, starts a new payment period on the date given (the
    month count starts again at 1), and records the new qualifying test and the new written order
    that the new period rests on. Afterwards the oxygen record lookup shows status rental_active,
    the new payment-period start, the new test date and saturation and the new order date.

    Args:
        oxygen_holding_id: Id class — the reference number of the patient's home oxygen record,
            given to the patient by the agent from the oxygen record lookup.
        rental_period_start_date: Fixed-format class — the first day of the new payment period,
            written as YYYY-MM-DD, as the agent states it to the patient.
        qualifying_test_date: Fixed-format class — the date of the new qualifying oxygen
            saturation test shown on the patient's discharge paperwork, written as YYYY-MM-DD.
        qualifying_spo2: Fixed-format class — the oxygen saturation on that test as an integer
            percent (for example 87 for 87 percent).
        rx_date: Fixed-format class — the date of the new written oxygen order shown on the
            discharge paperwork, written as YYYY-MM-DD.

    Returns:
        A one-line text confirmation "Oxygen record <oxygen_holding_id> continued under a new
        payment period from <rental_period_start_date> (test <qualifying_test_date>, SpO2
        <qualifying_spo2>%, order <rx_date>); status rental_active." Its presence means the record
        was reopened with those values.
    """
    ctx.update("oxygen_holdings", oxygen_holding_id, status="rental_active", suspended_date="",
               rental_period_start_date=rental_period_start_date, qualifying_test_date=qualifying_test_date,
               qualifying_spo2=int(qualifying_spo2), rx_date=rx_date)
    return (f"Oxygen record {oxygen_holding_id} continued under a new payment period from {rental_period_start_date} "
            f"(test {qualifying_test_date}, SpO2 {int(qualifying_spo2)}%, order {rx_date}); status rental_active.")


@tool(owner="agent", rw="write")
def record_oxygen_contents_payment_7caaff46(ctx: ToolContext, oxygen_holding_id: str, coverage_id: str,
                                            service_from_date: str, adjudication_date: str, claim_number: str,
                                            hcpcs_code: str, rental_month_number: int, allowed_amount: float) -> str:
    """Post a monthly oxygen contents claim (gas or liquid supplied after the equipment-payment cap) that
    the patient's coverage paid in full, leaving nothing for the patient to pay. One call adds one paid
    contents-month line to the patient's oxygen claim history: the payer's allowed amount is recorded as
    both the allowed and the paid amount and the patient share as 0.00. Afterwards the oxygen claim
    lookup shows the new paid contents line with the values given.

    Args:
        oxygen_holding_id: Id class — the reference number of the patient's home oxygen record, read
            from the oxygen record lookup before the call.
        coverage_id: Id class — the reference number of the coverage record that paid the month, read
            from the coverage lookup before the call.
        service_from_date: Fixed-format class — the first day of the contents month paid, written as
            YYYY-MM-DD.
        adjudication_date: Fixed-format class — the date of the payer's remittance that paid the
            month, written as YYYY-MM-DD.
        claim_number: Verbatim class — the payer's claim control number for the month exactly as it
            is read from the payer's statement; copy it character for character with no change (verbatim).
        hcpcs_code: Enum class — the code of the contents billed: E0442 when the contents are liquid
            oxygen for a liquid system; E0443 when the contents are gaseous oxygen in portable
            cylinders; E1390 when the line is a concentrator equipment month, which this tool never
            posts; E0439 when the line is a liquid reservoir equipment month, which this tool never posts.
        rental_month_number: Fixed-format class — the ordinal of the contents month counted from the
            payment cap, a non-negative integer (1 for the first contents month after the cap).
        allowed_amount: Fixed-format class — the payer's allowed amount for the contents month in
            USD, rounded to 2 decimal places (stored as given, also as the amount paid).

    Returns:
        A one-line text confirmation "Posted paid-in-full contents month <rental_month_number>
        (<service_from_date>) on oxygen record <oxygen_holding_id>: line <line id>, allowed
        <allowed_amount>, paid <allowed_amount>, patient share 0.00." where <line id> is the new
        claim line reference (prefix oxc_). Its presence means the paid contents line was added.
    """
    rid = ctx.make_id("oxc_", oxygen_holding_id, coverage_id, service_from_date, adjudication_date,
                      claim_number, hcpcs_code, rental_month_number, allowed_amount)
    customer = (ctx.find("oxygen_holdings", oxygen_holding_id=oxygen_holding_id) or [{}])[0].get("customer_id")
    amount = round(float(allowed_amount), 2)
    ctx.create("oxygen_billing", rid, oxygen_bill_id=rid, oxygen_holding_id=oxygen_holding_id, customer_id=customer,
               event_type="oxygen_contents_paid", coverage_id=coverage_id, hcpcs_code=hcpcs_code,
               flow_modifier="none", rental_month_number=int(rental_month_number),
               service_from_date=service_from_date, adjudication_date=adjudication_date, allowed_amount=amount,
               portable_allowed_amount=0.0, payer_paid_amount=amount, patient_responsibility=0.0,
               claim_number=claim_number, denial_reason="none", reversal_reason="none")
    return (f"Posted paid-in-full contents month {int(rental_month_number)} ({service_from_date}) on oxygen record "
            f"{oxygen_holding_id}: line {rid}, allowed {amount:.2f}, paid {amount:.2f}, patient share 0.00.")


@tool(owner="user", rw="write")
def confirm_oxygen_primary_coverage_03bf25f6(ctx: ToolContext, oxygen_holding_id: str, coverage_id: str,
                                             rental_period_start_date: str) -> str:
    """The patient's own confirmation (or that of the patient's representative) of which insurance is now
    primary for the home oxygen. One call moves the patient's oxygen record to the confirmed coverage
    record and starts the payment period under that coverage on the date given; months paid under the
    earlier coverage stay on the claim history. Afterwards the oxygen record lookup shows the confirmed
    coverage and the new payment-period start date.

    Args:
        oxygen_holding_id: Id class — the reference number of the patient's home oxygen record, given
            by the agent from the oxygen record lookup.
        coverage_id: Id class — the reference number of the coverage record confirmed as primary for
            the oxygen, given by the agent from the coverage lookup.
        rental_period_start_date: Fixed-format class — the first day of service under the confirmed
            coverage, written as YYYY-MM-DD, as the agent states it.

    Returns:
        A one-line text confirmation "Oxygen record <oxygen_holding_id> now billed to coverage
        <coverage_id> from <rental_period_start_date>." Its presence means the record was moved.
    """
    ctx.update("oxygen_holdings", oxygen_holding_id, coverage_id=coverage_id,
               rental_period_start_date=rental_period_start_date)
    return f"Oxygen record {oxygen_holding_id} now billed to coverage {coverage_id} from {rental_period_start_date}."


@tool(owner="user", rw="write")
def confirm_oxygen_return_2399228d(ctx: ToolContext, oxygen_holding_id: str, oxygen_request_id: str,
                                   closed_date: str) -> str:
    """The patient's own confirmation (or that of the patient's representative) that the home oxygen
    equipment is given back. One call approves the pending return-pickup request with today's date as
    its decision date and closes the patient's oxygen record as returned on the closing date given; the
    pickup itself is scheduled separately. Afterwards the oxygen request lookup shows the request
    approved and the oxygen record lookup shows status returned with that closing date.

    Args:
        oxygen_holding_id: Id class — the reference number of the patient's home oxygen record, given
            by the agent from the oxygen record lookup.
        oxygen_request_id: Id class — the reference number of the pending return-pickup request on that
            record, given by the agent from the oxygen request lookup.
        closed_date: Fixed-format class — the closing date of the oxygen record, written as YYYY-MM-DD,
            as the agent states it.

    Returns:
        A one-line text confirmation "Return confirmed: request <oxygen_request_id> approved on
        <decision date>, oxygen record <oxygen_holding_id> returned as of <closed_date>." where
        <decision date> is today's date as YYYY-MM-DD. Its presence means both changes were made.
    """
    today = ctx.now()[:10]
    ctx.update("oxygen_requests", oxygen_request_id, request_status="approved", decision_date=today)
    ctx.update("oxygen_holdings", oxygen_holding_id, status="returned", closed_date=closed_date)
    return (f"Return confirmed: request {oxygen_request_id} approved on {today}, oxygen record {oxygen_holding_id} "
            f"returned as of {closed_date}.")

"""Hidden task tools for the meter_testing_and_metering difficulty of
env_0042_investor_owned_electric_utility (Lakeshore Power & Light Company, Metering Service).

Each tool makes one atomic write in the Metering Service tables and is reached only through
unlock_* -> call_*; its name is published by the target_tool of one extended policy in
meter.extended.yaml. No tool checks eligibility, prerequisites or amounts: the agent decides those
from the policy and the records and passes the decided values in.
"""

from erlbench import ToolContext, tool


@tool(owner="agent", rw="write")
def post_slow_meter_backbill_dc57beb1(ctx: ToolContext, meter_installation_id: str, meter_test_id: str,
                                      backbill_amount: float) -> str:
    """Record the slow-meter backbill that Lakeshore calculates for the company's own accuracy test
    of a meter that registered too little energy. One call adds one backbill entry to the meter's
    adjustment record, dated today and tied to the test result it corrects; the entry carries the
    backbill amount in US dollars, and that amount becomes the underbilled charges the customer owes
    for the meter's error. Nothing else on the meter or the service account is changed by this call.
    On success the new adjustment reference number is returned and the backbill shows when the
    meter's adjustments are looked up.

    Args:
        meter_installation_id: Id class — the meter installation reference number of the meter whose
            registration was found slow, as returned by the meter installation lookup.
        meter_test_id: Id class — the reference number of the test result (not the test request) the
            backbill corrects, as returned by the meter test lookup for that meter.
        backbill_amount: Fixed-format class — the backbill in US dollars as a positive number with 2
            decimal places, rounded half up to the cent by the caller before it is passed; 0.00 records a
            backbill below the posting threshold.

    Returns:
        A one-line confirmation string "Slow-meter backbill <meter_adjustment_id> recorded on meter
        <meter_installation_id> for test result <meter_test_id>: <amount> USD on <YYYY-MM-DD>.", where
        meter_adjustment_id is the new adjustment reference number (text), amount is the recorded
        backbill in US dollars with 2 decimals and the date is today's adjustment date; receiving this
        line means the backbill entry exists on the meter's adjustment record.
    """
    rid = ctx.make_id("madj_", meter_installation_id, meter_test_id, backbill_amount)
    found = ctx.find("meter_installations", meter_installation_id=meter_installation_id)
    inst = found[0] if found else {}
    amount = round(float(backbill_amount), 2)
    day = ctx.now()[:10]
    ctx.create("meter_adjustments", rid, meter_adjustment_id=rid, meter_installation_id=meter_installation_id,
               customer_id=inst.get("customer_id", ""), event_type="meter_accuracy_adjustment",
               meter_test_id=meter_test_id, adjustment_date=day, adjustment_direction="backbill", amount=amount)
    return (f"Slow-meter backbill {rid} recorded on meter {meter_installation_id} for test result "
            f"{meter_test_id}: {amount:.2f} USD on {day}.")


@tool(owner="user", rw="write")
def accept_referee_backbill_settlement_27524241(ctx: ToolContext, meter_installation_id: str, meter_test_id: str,
                                                settlement_amount: float) -> str:
    """The customer accepts the outcome of a Commission referee test of their meter that found it
    slow, settling the dispute over the meter's backbill. One call records the customer's accepted
    settlement as one backbill entry on the meter's adjustment record, dated today and tied to the
    referee test result; the entry carries the settlement amount in US dollars that the customer
    agrees to owe on top of whatever backbill already stands for the meter. Nothing else on the
    meter or the service account is changed by this call. On success the settlement reference
    number is returned and the settlement shows when the meter's adjustments are looked up.

    Args:
        meter_installation_id: Id class — the meter installation reference number of the meter the
            referee tested, as given to the customer by the representative from the meter
            installation lookup.
        meter_test_id: Id class — the reference number of the referee test result (not the request)
            being accepted, as given to the customer by the representative from the meter test lookup.
        settlement_amount: Fixed-format class — the settlement the customer accepts, in US dollars as a
            non-negative number with 2 decimal places, rounded half up to the cent before it is passed,
            exactly as the representative stated it.

    Returns:
        A one-line confirmation string "Referee settlement <meter_adjustment_id> accepted on meter
        <meter_installation_id> for referee result <meter_test_id>: <amount> USD on <YYYY-MM-DD>.", where
        meter_adjustment_id is the new settlement reference number (text), amount is the accepted
        settlement in US dollars with 2 decimals and the date is today's acceptance date; receiving this
        line means the settlement entry exists on the meter's adjustment record.
    """
    rid = ctx.make_id("madj_", meter_installation_id, meter_test_id, settlement_amount)
    found = ctx.find("meter_installations", meter_installation_id=meter_installation_id)
    inst = found[0] if found else {}
    amount = round(float(settlement_amount), 2)
    day = ctx.now()[:10]
    ctx.create("meter_adjustments", rid, meter_adjustment_id=rid, meter_installation_id=meter_installation_id,
               customer_id=inst.get("customer_id", ""), event_type="meter_accuracy_adjustment",
               meter_test_id=meter_test_id, adjustment_date=day, adjustment_direction="backbill", amount=amount)
    return (f"Referee settlement {rid} accepted on meter {meter_installation_id} for referee result "
            f"{meter_test_id}: {amount:.2f} USD on {day}.")


@tool(owner="agent", rw="write")
def charge_repeat_test_fee_cae4c873(ctx: ToolContext, meter_installation_id: str, meter_test_id: str,
                                    fee_amount: float) -> str:
    """Charge the repeat test fee owed for a customer-requested accuracy test of a meter that found the
    meter within tolerance after the customer's free test allowance was used. One call adds one repeat
    test fee to the meter's metering charges, tied to the test result it is charged for and dated on
    that result's test date; the fee is the amount in US dollars the customer owes for that test.
    Nothing else on the meter or the service account is changed by this call. On success the new
    charge reference number is returned and the fee shows when the meter's charges are looked up.

    Args:
        meter_installation_id: Id class — the meter installation reference number of the tested meter,
            as returned by the meter installation lookup.
        meter_test_id: Id class — the reference number of the test result (not the test request) the
            fee is charged for, as returned by the meter test lookup for that meter.
        fee_amount: Fixed-format class — the repeat test fee in US dollars as a non-negative number with
            2 decimal places, rounded half up to the cent by the caller before it is passed.

    Returns:
        A one-line confirmation string "Repeat test fee <meter_charge_id> charged on meter
        <meter_installation_id> for test result <meter_test_id>: <amount> USD dated <YYYY-MM-DD>.", where
        meter_charge_id is the new charge reference number (text), amount is the charged fee in US
        dollars with 2 decimals and the date is the test date of the charged result; receiving this line
        means the fee exists on the meter's metering charges.
    """
    rid = ctx.make_id("mchg_", meter_installation_id, meter_test_id, fee_amount)
    found = ctx.find("meter_installations", meter_installation_id=meter_installation_id)
    inst = found[0] if found else {}
    tested = ctx.find("meter_tests", meter_test_id=meter_test_id)
    day = (tested[0].get("test_date") if tested else "") or ctx.now()[:10]
    amount = round(float(fee_amount), 2)
    ctx.create("meter_charges", rid, meter_charge_id=rid, meter_installation_id=meter_installation_id,
               customer_id=inst.get("customer_id", ""), event_type="meter_test_fee", fee_date=day, amount=amount,
               meter_test_id=meter_test_id, meter_field_order_id=None)
    return (f"Repeat test fee {rid} charged on meter {meter_installation_id} for test result {meter_test_id}: "
            f"{amount:.2f} USD dated {day}.")


@tool(owner="agent", rw="write")
def post_fast_meter_refund_06e0a347(ctx: ToolContext, meter_installation_id: str, meter_test_id: str,
                                    refund_amount: float) -> str:
    """Record the fast-meter refund that Lakeshore calculates for the company's own accuracy test of a
    meter that registered too much energy. One call adds one refund entry to the meter's adjustment
    record, dated today and tied to the test result it corrects; the entry carries the refund amount in
    US dollars that is owed back to the customer for the meter's error. Nothing else on the meter or
    the service account is changed by this call. On success the new adjustment reference number is
    returned and the refund shows when the meter's adjustments are looked up.

    Args:
        meter_installation_id: Id class — the meter installation reference number of the meter whose
            registration was found fast, as returned by the meter installation lookup.
        meter_test_id: Id class — the reference number of the test result (not the test request) the
            refund corrects, as returned by the meter test lookup for that meter.
        refund_amount: Fixed-format class — the refund in US dollars as a non-negative number with 2
            decimal places, rounded half up to the cent by the caller before it is passed; 0.00 records a
            refund below the posting threshold.

    Returns:
        A one-line confirmation string "Fast-meter refund <meter_adjustment_id> recorded on meter
        <meter_installation_id> for test result <meter_test_id>: <amount> USD on <YYYY-MM-DD>.", where
        meter_adjustment_id is the new adjustment reference number (text), amount is the recorded refund
        in US dollars with 2 decimals and the date is today's adjustment date; receiving this line means
        the refund entry exists on the meter's adjustment record.
    """
    rid = ctx.make_id("madj_", meter_installation_id, meter_test_id, refund_amount)
    found = ctx.find("meter_installations", meter_installation_id=meter_installation_id)
    inst = found[0] if found else {}
    amount = round(float(refund_amount), 2)
    day = ctx.now()[:10]
    ctx.create("meter_adjustments", rid, meter_adjustment_id=rid, meter_installation_id=meter_installation_id,
               customer_id=inst.get("customer_id", ""), event_type="meter_accuracy_adjustment",
               meter_test_id=meter_test_id, adjustment_date=day, adjustment_direction="refund", amount=amount)
    return (f"Fast-meter refund {rid} recorded on meter {meter_installation_id} for test result "
            f"{meter_test_id}: {amount:.2f} USD on {day}.")


@tool(owner="agent", rw="write")
def post_non_registering_backbill_96d206ff(ctx: ToolContext, meter_installation_id: str, meter_test_id: str,
                                           backbill_amount: float) -> str:
    """Record the backbill that Lakeshore calculates for a meter whose accuracy test found it not
    registering energy at all. One call adds one backbill entry to the meter's adjustment record, dated
    today and tied to the test result that found the meter not registering; the entry carries the
    backbill amount in US dollars for the usage the meter failed to record. Nothing else on the meter
    or the service account is changed by this call. On success the new adjustment reference number is
    returned and the backbill shows when the meter's adjustments are looked up.

    Args:
        meter_installation_id: Id class — the meter installation reference number of the meter found not
            registering, as returned by the meter installation lookup.
        meter_test_id: Id class — the reference number of the test result (not the test request) that
            found the meter not registering, as returned by the meter test lookup for that meter.
        backbill_amount: Fixed-format class — the backbill in US dollars as a non-negative number with 2
            decimal places, rounded half up to the cent by the caller before it is passed; 0.00 records a
            backbill below the posting threshold.

    Returns:
        A one-line confirmation string "Non-registering backbill <meter_adjustment_id> recorded on meter
        <meter_installation_id> for test result <meter_test_id>: <amount> USD on <YYYY-MM-DD>.", where
        meter_adjustment_id is the new adjustment reference number (text), amount is the recorded
        backbill in US dollars with 2 decimals and the date is today's adjustment date; receiving this
        line means the backbill entry exists on the meter's adjustment record.
    """
    rid = ctx.make_id("madj_", meter_installation_id, meter_test_id, backbill_amount)
    found = ctx.find("meter_installations", meter_installation_id=meter_installation_id)
    inst = found[0] if found else {}
    amount = round(float(backbill_amount), 2)
    day = ctx.now()[:10]
    ctx.create("meter_adjustments", rid, meter_adjustment_id=rid, meter_installation_id=meter_installation_id,
               customer_id=inst.get("customer_id", ""), event_type="meter_accuracy_adjustment",
               meter_test_id=meter_test_id, adjustment_date=day, adjustment_direction="backbill", amount=amount)
    return (f"Non-registering backbill {rid} recorded on meter {meter_installation_id} for test result "
            f"{meter_test_id}: {amount:.2f} USD on {day}.")


@tool(owner="user", rw="write")
def accept_referee_refund_settlement_2157b6a7(ctx: ToolContext, meter_installation_id: str, meter_test_id: str,
                                              settlement_amount: float) -> str:
    """The customer accepts the outcome of a Commission referee test of their meter that found it fast,
    settling the dispute over the meter's refund. One call records the customer's accepted settlement as
    one refund entry on the meter's adjustment record, dated today and tied to the referee test result;
    the entry carries the settlement amount in US dollars owed back to the customer on top of whatever
    refund already stands for the meter. Nothing else on the meter or the service account is changed
    by this call. On success the settlement reference number is returned and the settlement shows when
    the meter's adjustments are looked up.

    Args:
        meter_installation_id: Id class — the meter installation reference number of the meter the
            referee tested, as given to the customer by the representative from the meter installation
            lookup.
        meter_test_id: Id class — the reference number of the referee test result (not the request) being
            accepted, as given to the customer by the representative from the meter test lookup.
        settlement_amount: Fixed-format class — the settlement the customer accepts, in US dollars as a
            non-negative number with 2 decimal places, rounded half up to the cent before it is passed,
            exactly as the representative stated it.

    Returns:
        A one-line confirmation string "Referee refund settlement <meter_adjustment_id> accepted on meter
        <meter_installation_id> for referee result <meter_test_id>: <amount> USD on <YYYY-MM-DD>.", where
        meter_adjustment_id is the new settlement reference number (text), amount is the accepted
        settlement in US dollars with 2 decimals and the date is today's acceptance date; receiving this
        line means the settlement entry exists on the meter's adjustment record.
    """
    rid = ctx.make_id("madj_", meter_installation_id, meter_test_id, settlement_amount)
    found = ctx.find("meter_installations", meter_installation_id=meter_installation_id)
    inst = found[0] if found else {}
    amount = round(float(settlement_amount), 2)
    day = ctx.now()[:10]
    ctx.create("meter_adjustments", rid, meter_adjustment_id=rid, meter_installation_id=meter_installation_id,
               customer_id=inst.get("customer_id", ""), event_type="meter_accuracy_adjustment",
               meter_test_id=meter_test_id, adjustment_date=day, adjustment_direction="refund", amount=amount)
    return (f"Referee refund settlement {rid} accepted on meter {meter_installation_id} for referee result "
            f"{meter_test_id}: {amount:.2f} USD on {day}.")

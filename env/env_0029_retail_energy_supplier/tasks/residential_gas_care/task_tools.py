"""Hidden task tools of the residential_gas_care difficulty (Beacon Ridge Energy, residential natural gas).

Each tool performs exactly one atomic write on the residential gas records and is reached only through
unlock_* -> call_*; its name is published by the target_tool of one extended policy in gas.extended.yaml.
No tool judges eligibility, checks a prerequisite, aggregates history or computes a value for the caller:
every figure arrives as an argument already worked out from the published policy.
"""

from erlbench import ToolContext, tool


@tool(owner="user", rw="write")
def accept_gas_recontract_offer_a9611340(ctx: ToolContext, gas_agreement_id: str, variant_name: str,
                                         term_months: int, contract_rate_usd_therm: float,
                                         contract_end_date: str) -> str:
    """The customer personally accepts the renewal offer on a residential gas agreement that has already
    rolled over to month-to-month service, putting the agreement back on a fixed term starting today.
    One call rewrites the agreement's plan in force: the plan name, the term length, the per-therm rate
    and the last day of the new term are replaced with the values given, and the date the new term
    started is recorded as today's date. The agreement stays active and keeps its number. Afterwards the
    customer can see the new plan, rate and end date on the agreement record.

    Args:
        gas_agreement_id: Id class — the residential natural gas agreement number being re-contracted,
            as shown on the agreement record returned by the gas agreement lookup.
        variant_name: Enum class — the official name of the plan the agreement moves onto, exactly one of:
            Beacon Ridge Gas Monthly Variable when the accepted offer is the month-to-month variable plan;
            Beacon Ridge Gas Capped Variable 12 when the accepted offer is the twelve-month capped variable plan;
            Beacon Ridge Gas Price Lock 12 when the accepted offer is the twelve-month fixed price plan;
            Beacon Ridge Gas Price Lock 24 when the accepted offer is the twenty-four-month fixed price plan;
            Beacon Ridge Gas Price Lock 36 when the accepted offer is the thirty-six-month fixed price plan;
            Beacon Ridge Carbon Offset Gas 12 when the accepted offer is the twelve-month carbon offset plan;
            Beacon Ridge Carbon Offset Gas 24 when the accepted offer is the twenty-four-month carbon offset plan.
        term_months: Fixed-format class — the length of the new term in integer months
            (0 only for month-to-month service).
        contract_rate_usd_therm: Fixed-format class — the per-therm supply rate of the new term in
            USD per therm, a decimal carried to 4 decimal places; the value is stored exactly at that
            precision (rounded half to even at the fifth place if more places are given).
        contract_end_date: Fixed-format class — the last calendar day of the new term, written
            YYYY-MM-DD (local service date, no time of day).

    Returns:
        A confirmation sentence (string) naming the agreement number, the plan now in force, the rate in
        USD per therm to 4 decimal places, the term in months, the new term's start date (today, YYYY-MM-DD)
        and its end date (YYYY-MM-DD); receiving it means the re-contract is recorded on the agreement.
    """
    start = ctx.now()[:10]
    ctx.update("gas_agreements", gas_agreement_id, variant_name=variant_name, term_months=int(term_months),
               contract_rate_usd_therm=round(float(contract_rate_usd_therm), 4),
               contract_end_date=contract_end_date, plan_change_date=start)
    return (f"Re-contract recorded on gas agreement {gas_agreement_id}: {variant_name} at "
            f"{round(float(contract_rate_usd_therm), 4):.4f} USD/therm for {int(term_months)} months, "
            f"term {start} through {contract_end_date}.")


@tool(owner="agent", rw="write")
def enroll_gas_added_premise_5ded636b(ctx: ToolContext, customer_id: str, premise_id: str, variant_name: str,
                                      term_months: int, contract_rate_usd_therm: float) -> str:
    """Submit a new residential natural gas enrollment for an additional premise of an existing customer,
    taken by the care agent over the phone. One call creates one new gas agreement for that premise in
    enrollment pending status, dated today, on the plan, term and per-therm rate given; the utility's
    confirmation, the switch date and the end date are left empty until the gas utility processes it.
    Afterwards the new agreement appears in the customer's gas agreement list with its own agreement
    number.

    Args:
        customer_id: Id class — the Beacon Ridge customer number of the account holder, as returned by the
            customer profile lookup.
        premise_id: Id class — the reference number of the service premise being enrolled, as returned by
            the premise lookup for that customer.
        variant_name: Enum class — the official name of the plan enrolled, exactly one of:
            Beacon Ridge Gas Monthly Variable when the premise is enrolled on the month-to-month variable plan;
            Beacon Ridge Gas Capped Variable 12 when it is enrolled on the twelve-month capped variable plan;
            Beacon Ridge Gas Price Lock 12 when it is enrolled on the twelve-month fixed price plan;
            Beacon Ridge Gas Price Lock 24 when it is enrolled on the twenty-four-month fixed price plan;
            Beacon Ridge Gas Price Lock 36 when it is enrolled on the thirty-six-month fixed price plan;
            Beacon Ridge Carbon Offset Gas 12 when it is enrolled on the twelve-month carbon offset plan;
            Beacon Ridge Carbon Offset Gas 24 when it is enrolled on the twenty-four-month carbon offset plan.
        term_months: Fixed-format class — the plan term in integer months (0 for month-to-month).
        contract_rate_usd_therm: Fixed-format class — the enrollment rate in USD per therm, a decimal
            carried to 4 decimal places; stored at that precision (rounded half to even at the fifth place
            if more places are given).

    Returns:
        A confirmation sentence (string) giving the new gas agreement number, the premise reference, the plan,
        the term in months, the rate in USD per therm to 4 decimal places and the enrollment date (today,
        YYYY-MM-DD) with status enrollment_pending; receiving it means the enrollment was submitted.
    """
    rid = ctx.make_id("gag_", customer_id, premise_id, variant_name, term_months, contract_rate_usd_therm)
    today = ctx.now()[:10]
    ctx.create("gas_agreements", rid, gas_agreement_id=rid, customer_id=customer_id, premise_id=premise_id,
               variant_name=variant_name, status="enrollment_pending", enrollment_date=today,
               enrollment_channel="phone", utility_confirmation_date="", service_start_date="",
               term_months=int(term_months), contract_rate_usd_therm=round(float(contract_rate_usd_therm), 4),
               contract_end_date="", thermostat_shipped_date="", drop_requested_date="", drop_reason="",
               drop_effective_date="", close_date="", close_reason="", plan_change_date="",
               rescinded_date="", reject_reason="")
    return (f"Gas enrollment {rid} submitted for premise {premise_id}: {variant_name}, {int(term_months)} months at "
            f"{round(float(contract_rate_usd_therm), 4):.4f} USD/therm, enrolled {today}, status enrollment_pending.")




@tool(owner="user", rw="write")
def accept_gas_renewal_offer_6e431548(ctx: ToolContext, gas_agreement_id: str, variant_name: str, term_months: int,
                                      contract_rate_usd_therm: float, plan_change_date: str,
                                      contract_end_date: str) -> str:
    """The customer personally accepts the renewal offer on a residential gas agreement that is still in its
    current term, so that the agreement continues into a new term when the current one ends. One call
    rewrites the agreement's plan in force: the plan name, the term length, the per-therm rate, the date the
    new term starts and the last day of the new term are replaced with the values given. The agreement
    stays active and keeps its number. Afterwards the customer can see the renewed plan, rate, start date
    and end date on the agreement record.

    Args:
        gas_agreement_id: Id class — the residential natural gas agreement number being renewed, as shown on
            the agreement record returned by the gas agreement lookup.
        variant_name: Enum class — the official name of the plan renewed into, exactly one of:
            Beacon Ridge Gas Monthly Variable when the accepted offer is the month-to-month variable plan;
            Beacon Ridge Gas Capped Variable 12 when the accepted offer is the twelve-month capped variable plan;
            Beacon Ridge Gas Price Lock 12 when the accepted offer is the twelve-month fixed price plan;
            Beacon Ridge Gas Price Lock 24 when the accepted offer is the twenty-four-month fixed price plan;
            Beacon Ridge Gas Price Lock 36 when the accepted offer is the thirty-six-month fixed price plan;
            Beacon Ridge Carbon Offset Gas 12 when the accepted offer is the twelve-month carbon offset plan;
            Beacon Ridge Carbon Offset Gas 24 when the accepted offer is the twenty-four-month carbon offset plan.
        term_months: Fixed-format class — the length of the new term in integer months (0 only for
            month-to-month service).
        contract_rate_usd_therm: Fixed-format class — the per-therm supply rate of the new term in USD per
            therm, a decimal carried to 4 decimal places; stored at that precision (rounded half to even at
            the fifth place if more places are given).
        plan_change_date: Fixed-format class — the first calendar day of the new term, written YYYY-MM-DD
            (local service date, no time of day).
        contract_end_date: Fixed-format class — the last calendar day of the new term, written YYYY-MM-DD
            (local service date, no time of day).

    Returns:
        A confirmation sentence (string) naming the agreement number, the plan renewed into, the rate in USD
        per therm to 4 decimal places, the term in months and the new term's start and end dates (YYYY-MM-DD);
        receiving it means the renewal is recorded on the agreement.
    """
    ctx.update("gas_agreements", gas_agreement_id, variant_name=variant_name, term_months=int(term_months),
               contract_rate_usd_therm=round(float(contract_rate_usd_therm), 4),
               plan_change_date=plan_change_date, contract_end_date=contract_end_date)
    return (f"Renewal recorded on gas agreement {gas_agreement_id}: {variant_name} at "
            f"{round(float(contract_rate_usd_therm), 4):.4f} USD/therm for {int(term_months)} months, "
            f"term {plan_change_date} through {contract_end_date}.")


@tool(owner="agent", rw="write")
def post_gas_rebill_credit_0e7c2434(ctx: ToolContext, gas_agreement_id: str, source_billing_id: str,
                                    billing_period_start: str, credit_amount_usd: float) -> str:
    """Post a rebill credit that returns money on one over-billed residential gas bill line. One call adds one
    new credit line to the agreement's bill ledger, tied to the original line it corrects, dated today and
    shown on the bill of the corrected line's billing cycle; the credit is stored as a negative amount equal
    to the value given. The original line is left as it was. Afterwards the credit appears in the
    agreement's bill lines with the corrected line's reference.

    Args:
        gas_agreement_id: Id class — the residential natural gas agreement number the corrected line belongs
            to, as returned by the gas agreement lookup.
        source_billing_id: Id class — the reference number of the original gas bill line being corrected, as
            returned by the gas bill line lookup.
        billing_period_start: Fixed-format class — the first day of the billing cycle of the corrected line,
            written YYYY-MM-DD exactly as shown on that line.
        credit_amount_usd: Fixed-format class — the credit to return, in USD, given as a positive amount with
            2 decimal places (rounded half to even at the third place if more places are given); it is posted
            as the matching negative amount.

    Returns:
        A confirmation sentence (string) giving the new credit line's reference number, the corrected line's
        reference, the billing cycle start (YYYY-MM-DD), the amount credited in USD to 2 decimal places and the
        posting date (today, YYYY-MM-DD); receiving it means the rebill credit is on the ledger.
    """
    owner = ctx.find("gas_agreements", gas_agreement_id=gas_agreement_id)
    cust = owner[0].get("customer_id") if owner else ""
    amt = round(float(credit_amount_usd), 2)
    rid = ctx.make_id("gbl_", gas_agreement_id, source_billing_id, billing_period_start, credit_amount_usd)
    today = ctx.now()[:10]
    ctx.create("gas_billing", rid, gas_billing_id=rid, gas_agreement_id=gas_agreement_id, customer_id=cust,
               event_type="gas_adjustment", line_type="rebill_credit", billing_period_start=billing_period_start,
               billing_period_end="", usage_therms=0, rate_usd_therm=0.0, amount_usd=-amt, posted_date=today,
               source_billing_id=source_billing_id, etf_months_remaining=0)
    return (f"Rebill credit {rid} posted {today} on gas agreement {gas_agreement_id}: -{amt:.2f} USD against line "
            f"{source_billing_id} (cycle starting {billing_period_start}).")


@tool(owner="agent", rw="write")
def post_gas_signup_credit_32aac0cb(ctx: ToolContext, gas_agreement_id: str, billing_period_start: str,
                                    credit_amount_usd: float) -> str:
    """Post the one-time sign-up bill credit on a residential gas agreement. One call adds one new sign-up
    credit line to the agreement's bill ledger, dated today and shown on the bill of the billing cycle
    given; the credit is stored as a negative amount equal to the value given. Afterwards the credit
    appears in the agreement's bill lines as a sign-up credit.

    Args:
        gas_agreement_id: Id class — the residential natural gas agreement number credited, as returned by
            the gas agreement lookup.
        billing_period_start: Fixed-format class — the first day of the billing cycle on whose bill the
            credit appears, written YYYY-MM-DD.
        credit_amount_usd: Fixed-format class — the credit amount in USD, given as a positive amount with 2
            decimal places (rounded half to even at the third place if more places are given); it is posted
            as the matching negative amount.

    Returns:
        A confirmation sentence (string) giving the new credit line's reference number, the agreement number,
        the billing cycle start (YYYY-MM-DD), the amount credited in USD to 2 decimal places and the posting
        date (today, YYYY-MM-DD); receiving it means the sign-up credit is on the ledger.
    """
    owner = ctx.find("gas_agreements", gas_agreement_id=gas_agreement_id)
    cust = owner[0].get("customer_id") if owner else ""
    amt = round(float(credit_amount_usd), 2)
    rid = ctx.make_id("gbl_", gas_agreement_id, "signup_credit", billing_period_start, credit_amount_usd)
    today = ctx.now()[:10]
    ctx.create("gas_billing", rid, gas_billing_id=rid, gas_agreement_id=gas_agreement_id, customer_id=cust,
               event_type="gas_credit", line_type="signup_credit", billing_period_start=billing_period_start,
               billing_period_end="", usage_therms=0, rate_usd_therm=0.0, amount_usd=-amt, posted_date=today,
               source_billing_id="", etf_months_remaining=0)
    return (f"Sign-up credit {rid} posted {today} on gas agreement {gas_agreement_id}: -{amt:.2f} USD on the bill "
            f"of the cycle starting {billing_period_start}.")


@tool(owner="agent", rw="write")
def post_gas_loyalty_credit_c1183f95(ctx: ToolContext, gas_agreement_id: str, billing_period_start: str,
                                     credit_amount_usd: float) -> str:
    """Post a renewal loyalty bill credit on a residential gas agreement for a renewal that has taken effect.
    One call adds one new renewal loyalty credit line to the agreement's bill ledger, dated today and shown
    on the bill of the billing cycle given; the credit is stored as a negative amount equal to the value
    given. Afterwards the credit appears in the agreement's bill lines as a renewal loyalty credit.

    Args:
        gas_agreement_id: Id class — the residential natural gas agreement number credited, as returned by
            the gas agreement lookup.
        billing_period_start: Fixed-format class — the first day of the billing cycle on whose bill the
            credit appears, written YYYY-MM-DD.
        credit_amount_usd: Fixed-format class — the credit amount in USD, given as a positive amount with 2
            decimal places (rounded half to even at the third place if more places are given); it is posted
            as the matching negative amount.

    Returns:
        A confirmation sentence (string) giving the new credit line's reference number, the agreement number,
        the billing cycle start (YYYY-MM-DD), the amount credited in USD to 2 decimal places and the posting
        date (today, YYYY-MM-DD); receiving it means the loyalty credit is on the ledger.
    """
    owner = ctx.find("gas_agreements", gas_agreement_id=gas_agreement_id)
    cust = owner[0].get("customer_id") if owner else ""
    amt = round(float(credit_amount_usd), 2)
    rid = ctx.make_id("gbl_", gas_agreement_id, "renewal_loyalty_credit", billing_period_start, credit_amount_usd)
    today = ctx.now()[:10]
    ctx.create("gas_billing", rid, gas_billing_id=rid, gas_agreement_id=gas_agreement_id, customer_id=cust,
               event_type="gas_credit", line_type="renewal_loyalty_credit", billing_period_start=billing_period_start,
               billing_period_end="", usage_therms=0, rate_usd_therm=0.0, amount_usd=-amt, posted_date=today,
               source_billing_id="", etf_months_remaining=0)
    return (f"Renewal loyalty credit {rid} posted {today} on gas agreement {gas_agreement_id}: -{amt:.2f} USD on the "
            f"bill of the cycle starting {billing_period_start}.")

"""Hidden task tools of the residential_electricity_care difficulty (Beacon Ridge Energy).

Each tool performs one atomic write on a residential electricity agreement or its bill lines.
None of them checks eligibility, status, timing or amounts: the care agent decides those from
the published policies and the records before calling.
"""

from erlbench import ToolContext, tool


@tool(owner="user", rw="write")
def accept_renewal_offer_e5d86473(ctx: ToolContext, power_agreement_id: str, variant_name: str, term_months: int,
                                  contract_rate_cents_kwh: float, plan_change_date: str, contract_end_date: str) -> str:
    """The account holder personally accepts the renewal offer on one of their Beacon Ridge residential
    electricity agreements. The agreement is moved onto the plan accepted for a new fixed term: its plan
    name, term length, contract rate, the start date of the new term and the new contract end date are
    replaced by the values given, and the agreement stays active. On success the agreement record shows
    the accepted plan, rate and term dates; the receipt below confirms the acceptance was recorded.

    Args:
        power_agreement_id: Id class — the residential electricity agreement number being renewed, as read from the agreement lookup for the caller's premise.
        variant_name: Enum class — the official name of the plan accepted for the new term, exactly one of: Beacon Ridge Monthly Variable when the plan accepted is the month-to-month variable plan; Beacon Ridge Price Lock 6 when it is the six-month price lock; Beacon Ridge Price Lock 12 when it is the twelve-month price lock; Beacon Ridge Price Lock 24 when it is the twenty-four-month price lock; Beacon Ridge Free Nights 12 when it is the twelve-month time-of-use plan with free nights; Beacon Ridge Clean Wind 12 when it is the twelve-month wind-matched plan; Beacon Ridge Clean Wind 24 when it is the twenty-four-month wind-matched plan.
        term_months: Fixed-format class — length of the new term in integer months (unit: integer months), a whole number with no decimals.
        contract_rate_cents_kwh: Fixed-format class — the supply rate of the new term in cents per kWh, given to 2 decimal places (for example 10.25), no currency sign.
        plan_change_date: Fixed-format class — the first day of the new term, as a calendar date in the form YYYY-MM-DD.
        contract_end_date: Fixed-format class — the last day of the new term, as a calendar date in the form YYYY-MM-DD.

    Returns:
        A confirmation sentence (string) naming the agreement number, the plan accepted, the rate in cents
        per kWh, and the new term's start and end dates; receiving it means the acceptance is recorded on
        the agreement.
    """
    ctx.update("power_agreements", power_agreement_id, variant_name=variant_name, term_months=int(term_months),
               contract_rate_cents_kwh=round(float(contract_rate_cents_kwh), 2), plan_change_date=plan_change_date,
               contract_end_date=contract_end_date)
    return (f"Renewal accepted on agreement {power_agreement_id}: {variant_name} at "
            f"{round(float(contract_rate_cents_kwh), 2):.2f} cents per kWh, term {plan_change_date} to {contract_end_date}.")


@tool(owner="agent", rw="write")
def post_renewal_loyalty_credit_25af361b(ctx: ToolContext, power_agreement_id: str, referred_customer_id: str, billing_period_start: str,
                                         credit_amount_usd: float) -> str:
    """Post one renewal loyalty bill credit to a residential electricity agreement. A new credit line of
    the renewal loyalty kind is added to the agreement's Beacon Ridge bill lines for the billing cycle
    given, carrying the amount as a negative (credit) value and today's posting date; it reduces the
    supply charges billed on the agreement and appears on that cycle's utility bill.

    Args:
        power_agreement_id: Id class — the residential electricity agreement number that receives the credit, as read from the agreement lookup.
        referred_customer_id: Id class — the Beacon Ridge customer number of a referred customer named on the line; this credit is not a referral credit and names no referred customer, so the identifier passed is the empty string "".
        billing_period_start: Fixed-format class — the first day of the billing cycle on whose bill the credit appears, as a calendar date in the form YYYY-MM-DD.
        credit_amount_usd: Fixed-format class — the size of the credit as a positive amount in USD, 2 decimal places, signed on the bill as a credit (the line stores it as USD, 2 decimal places, signed, negative), rounded half up to the cent.

    Returns:
        A confirmation sentence (string) naming the new bill line number, the agreement, the cycle start
        date and the credited amount in USD; receiving it means the credit line now stands on the bill.
    """
    amt = round(float(credit_amount_usd), 2)
    owner_rows = ctx.find("power_agreements", power_agreement_id=power_agreement_id)
    holder = owner_rows[0].get("customer_id", "") if owner_rows else ""
    rid = ctx.make_id("pbl_", "renewal_loyalty_credit", power_agreement_id, referred_customer_id, billing_period_start, amt)
    ctx.create("power_billing", rid, power_billing_id=rid, power_agreement_id=power_agreement_id,
               customer_id=holder, event_type="power_credit",
               line_type="renewal_loyalty_credit", tou_period="", billing_period_start=billing_period_start,
               billing_period_end="", usage_kwh=0, rate_cents_kwh=0.00, amount_usd=-amt, posted_date=ctx.now()[:10],
               source_billing_id="", referred_customer_id=referred_customer_id, etf_months_remaining=0)
    return f"Renewal loyalty credit line {rid} posted on agreement {power_agreement_id} for the cycle starting {billing_period_start}: -{amt:.2f} USD."


@tool(owner="agent", rw="write")
def post_referral_credit_79c21554(ctx: ToolContext, power_agreement_id: str, referred_customer_id: str,
                                  billing_period_start: str, credit_amount_usd: float) -> str:
    """Post one referral bill credit to the referring customer's residential electricity agreement for one
    referred customer. A new credit line of the referral kind, naming the referred customer, is added to
    the agreement's Beacon Ridge bill lines for the billing cycle given, carrying the amount as a negative
    (credit) value and today's posting date; it appears on that cycle's utility bill.

    Args:
        power_agreement_id: Id class — the referring customer's residential electricity agreement number that receives the credit, as read from the agreement lookup.
        referred_customer_id: Id class — the Beacon Ridge customer number of the referred friend or neighbour, as shown on that person's agreement found through the referral lookup.
        billing_period_start: Fixed-format class — the first day of the billing cycle on whose bill the credit appears, as a calendar date in the form YYYY-MM-DD.
        credit_amount_usd: Fixed-format class — the size of the credit as a positive amount in USD, 2 decimal places, signed on the bill as a credit (the line stores it as USD, 2 decimal places, signed, negative), rounded half up to the cent.

    Returns:
        A confirmation sentence (string) naming the new bill line number, the agreement, the referred
        customer number, the cycle start date and the credited amount in USD; receiving it means the
        referral credit now stands on the bill.
    """
    amt = round(float(credit_amount_usd), 2)
    owner_rows = ctx.find("power_agreements", power_agreement_id=power_agreement_id)
    holder = owner_rows[0].get("customer_id", "") if owner_rows else ""
    rid = ctx.make_id("pbl_", "referral_credit", power_agreement_id, referred_customer_id, billing_period_start, amt)
    ctx.create("power_billing", rid, power_billing_id=rid, power_agreement_id=power_agreement_id,
               customer_id=holder, event_type="power_credit", line_type="referral_credit",
               tou_period="", billing_period_start=billing_period_start, billing_period_end="", usage_kwh=0,
               rate_cents_kwh=0.00, amount_usd=-amt, posted_date=ctx.now()[:10], source_billing_id="",
               referred_customer_id=referred_customer_id, etf_months_remaining=0)
    return (f"Referral credit line {rid} posted on agreement {power_agreement_id} for referred customer "
            f"{referred_customer_id}, cycle starting {billing_period_start}: -{amt:.2f} USD.")


@tool(owner="agent", rw="write")
def post_dual_fuel_credit_18175409(ctx: ToolContext, power_agreement_id: str, referred_customer_id: str, billing_period_start: str,
                                   credit_amount_usd: float) -> str:
    """Post one dual-fuel bill credit to a residential electricity agreement for one billing cycle. A new
    credit line of the dual-fuel kind is added to the agreement's Beacon Ridge bill lines for the billing
    cycle given, carrying the amount as a negative (credit) value and today's posting date; the restored
    credit then shows against that cycle in the agreement's bill lines.

    Args:
        power_agreement_id: Id class — the residential electricity agreement number that receives the credit, as read from the agreement lookup.
        referred_customer_id: Id class — the Beacon Ridge customer number of a referred customer named on the line; this credit is not a referral credit and names no referred customer, so the identifier passed is the empty string "".
        billing_period_start: Fixed-format class — the first day of the billing cycle the credit belongs to, as a calendar date in the form YYYY-MM-DD.
        credit_amount_usd: Fixed-format class — the size of the credit as a positive amount in USD, 2 decimal places, signed on the bill as a credit (the line stores it as USD, 2 decimal places, signed, negative), rounded half up to the cent.

    Returns:
        A confirmation sentence (string) naming the new bill line number, the agreement, the cycle start
        date and the credited amount in USD; receiving it means the dual-fuel credit now stands on the bill.
    """
    amt = round(float(credit_amount_usd), 2)
    owner_rows = ctx.find("power_agreements", power_agreement_id=power_agreement_id)
    holder = owner_rows[0].get("customer_id", "") if owner_rows else ""
    rid = ctx.make_id("pbl_", "dual_fuel_credit", power_agreement_id, referred_customer_id, billing_period_start, amt)
    ctx.create("power_billing", rid, power_billing_id=rid, power_agreement_id=power_agreement_id,
               customer_id=holder, event_type="power_credit", line_type="dual_fuel_credit",
               tou_period="", billing_period_start=billing_period_start, billing_period_end="", usage_kwh=0,
               rate_cents_kwh=0.00, amount_usd=-amt, posted_date=ctx.now()[:10], source_billing_id="",
               referred_customer_id=referred_customer_id, etf_months_remaining=0)
    return f"Dual-fuel credit line {rid} posted on agreement {power_agreement_id} for the cycle starting {billing_period_start}: -{amt:.2f} USD."


@tool(owner="user", rw="write")
def change_plan_fbee8941(ctx: ToolContext, power_agreement_id: str, variant_name: str, term_months: int,
                         contract_rate_cents_kwh: float, plan_change_date: str, contract_end_date: str) -> str:
    """The account holder personally authorizes a mid-term change of one of their Beacon Ridge residential
    electricity agreements to another plan. The agreement's plan name, term length, contract rate, the date
    the new plan takes effect and the new contract end date are replaced by the values given, and the
    agreement stays active. On success the agreement record shows the new plan, rate and term dates; the
    receipt below confirms the change was recorded.

    Args:
        power_agreement_id: Id class — the residential electricity agreement number being changed, as read from the agreement lookup for the caller's premise.
        variant_name: Enum class — the official name of the plan the agreement moves to, exactly one of: Beacon Ridge Monthly Variable when the new plan is the month-to-month variable plan; Beacon Ridge Price Lock 6 when it is the six-month price lock; Beacon Ridge Price Lock 12 when it is the twelve-month price lock; Beacon Ridge Price Lock 24 when it is the twenty-four-month price lock; Beacon Ridge Free Nights 12 when it is the twelve-month time-of-use plan with free nights; Beacon Ridge Clean Wind 12 when it is the twelve-month wind-matched plan; Beacon Ridge Clean Wind 24 when it is the twenty-four-month wind-matched plan.
        term_months: Fixed-format class — length of the new plan's term in integer months (unit: integer months), a whole number with no decimals.
        contract_rate_cents_kwh: Fixed-format class — the supply rate of the new plan in cents per kWh, given to 2 decimal places (for example 10.25), no currency sign.
        plan_change_date: Fixed-format class — the date the new plan takes effect, as a calendar date in the form YYYY-MM-DD.
        contract_end_date: Fixed-format class — the last day of the new plan's term, as a calendar date in the form YYYY-MM-DD.

    Returns:
        A confirmation sentence (string) naming the agreement number, the new plan, the rate in cents per
        kWh, and the new plan's start and end dates; receiving it means the change is recorded on the
        agreement.
    """
    ctx.update("power_agreements", power_agreement_id, variant_name=variant_name, term_months=int(term_months),
               contract_rate_cents_kwh=round(float(contract_rate_cents_kwh), 2), plan_change_date=plan_change_date,
               contract_end_date=contract_end_date)
    return (f"Plan change recorded on agreement {power_agreement_id}: {variant_name} at "
            f"{round(float(contract_rate_cents_kwh), 2):.2f} cents per kWh, term {plan_change_date} to {contract_end_date}.")


@tool(owner="agent", rw="write")
def post_rebill_credit_41f05139(ctx: ToolContext, power_agreement_id: str, source_billing_id: str,
                                billing_period_start: str, rebill_amount_usd: float) -> str:
    """Post one rebill credit that corrects one over-billed Beacon Ridge electricity bill line. A new line of
    the rebill kind is added to the agreement's bill lines, pointing at the original line it corrects and
    carrying the billing cycle of that line, the amount as a negative (credit) value and today's posting
    date; it reduces the supply charges billed and appears on the customer's next utility bill.

    Args:
        power_agreement_id: Id class — the residential electricity agreement number the corrected line belongs to, as read from the agreement lookup.
        source_billing_id: Id class — the reference number of the original bill line being corrected, as read from the bill-line lookup of the agreement.
        billing_period_start: Fixed-format class — the first day of the billing cycle of the corrected line, as a calendar date in the form YYYY-MM-DD.
        rebill_amount_usd: Fixed-format class — the size of the rebill credit as a positive amount in USD, 2 decimal places, signed on the bill as a credit (the line stores it as USD, 2 decimal places, signed, negative), rounded half up to the cent.

    Returns:
        A confirmation sentence (string) naming the new rebill line number, the agreement, the corrected line
        number and the credited amount in USD; receiving it means the rebill credit now stands on the bill.
    """
    amt = round(float(rebill_amount_usd), 2)
    owner_rows = ctx.find("power_agreements", power_agreement_id=power_agreement_id)
    holder = owner_rows[0].get("customer_id", "") if owner_rows else ""
    rid = ctx.make_id("pbl_", "rebill_credit", power_agreement_id, source_billing_id, billing_period_start, amt)
    ctx.create("power_billing", rid, power_billing_id=rid, power_agreement_id=power_agreement_id, customer_id=holder,
               event_type="power_adjustment", line_type="rebill_credit", tou_period="", billing_period_start=billing_period_start,
               billing_period_end="", usage_kwh=0, rate_cents_kwh=0.00, amount_usd=-amt, posted_date=ctx.now()[:10],
               source_billing_id=source_billing_id, referred_customer_id="", etf_months_remaining=0)
    return f"Rebill credit line {rid} posted on agreement {power_agreement_id} correcting line {source_billing_id}: -{amt:.2f} USD."


@tool(owner="agent", rw="write")
def open_billing_dispute_231feff0(ctx: ToolContext, power_agreement_id: str, source_billing_id: str,
                                  disputed_amount_usd: float) -> str:
    """Refer one disputed Beacon Ridge electricity bill line to billing review by opening a billing dispute.
    A new billing dispute is created for the line, in open status, recording the agreement, the line
    disputed, the disputed amount and the moment of referral; billing review then settles it. Nothing is
    credited on the bill by this action.

    Args:
        power_agreement_id: Id class — the residential electricity agreement number the disputed line belongs to, as read from the agreement lookup.
        source_billing_id: Id class — the reference number of the disputed bill line, as read from the bill-line lookup of the agreement.
        disputed_amount_usd: Fixed-format class — the amount referred for review as a positive amount in USD, 2 decimal places, positive, rounded half up to the cent.

    Returns:
        A confirmation sentence (string) naming the new dispute number, the agreement, the disputed line and
        the disputed amount in USD, and stating that the dispute is open; receiving it means the referral is
        recorded.
    """
    amt = round(float(disputed_amount_usd), 2)
    owner_rows = ctx.find("power_agreements", power_agreement_id=power_agreement_id)
    holder = owner_rows[0].get("customer_id", "") if owner_rows else ""
    rid = ctx.make_id("pds_", power_agreement_id, source_billing_id, amt)
    ctx.create("power_billing_disputes", rid, power_dispute_id=rid, customer_id=holder, power_agreement_id=power_agreement_id,
               source_billing_id=source_billing_id, disputed_amount_usd=amt, dispute_status="open", created_at=ctx.now())
    return f"Billing dispute {rid} opened on agreement {power_agreement_id} for line {source_billing_id}: {amt:.2f} USD, status open."


@tool(owner="agent", rw="write")
def post_signup_credit_3f59f0ed(ctx: ToolContext, power_agreement_id: str, referred_customer_id: str,
                                billing_period_start: str, credit_amount_usd: float) -> str:
    """Post one sign-up bill credit to a residential electricity agreement. A new credit line of the sign-up
    kind is added to the agreement's Beacon Ridge bill lines for the billing cycle given, carrying the
    amount as a negative (credit) value and today's posting date; it reduces the supply charges billed on
    the agreement and shows against that cycle in the agreement's bill lines.

    Args:
        power_agreement_id: Id class — the residential electricity agreement number that receives the credit, as read from the agreement lookup.
        referred_customer_id: Id class — the Beacon Ridge customer number of a referred customer named on the line; this credit is not a referral credit and names no referred customer, so the identifier passed is the empty string "".
        billing_period_start: Fixed-format class — the first day of the billing cycle the credit belongs to, as a calendar date in the form YYYY-MM-DD.
        credit_amount_usd: Fixed-format class — the size of the credit as a positive amount in USD, 2 decimal places, signed on the bill as a credit (the line stores it as USD, 2 decimal places, signed, negative), rounded half up to the cent.

    Returns:
        A confirmation sentence (string) naming the new bill line number, the agreement, the cycle start
        date and the credited amount in USD; receiving it means the sign-up credit now stands on the bill.
    """
    amt = round(float(credit_amount_usd), 2)
    owner_rows = ctx.find("power_agreements", power_agreement_id=power_agreement_id)
    holder = owner_rows[0].get("customer_id", "") if owner_rows else ""
    rid = ctx.make_id("pbl_", "signup_credit", power_agreement_id, referred_customer_id, billing_period_start, amt)
    ctx.create("power_billing", rid, power_billing_id=rid, power_agreement_id=power_agreement_id, customer_id=holder,
               event_type="power_credit", line_type="signup_credit", tou_period="", billing_period_start=billing_period_start,
               billing_period_end="", usage_kwh=0, rate_cents_kwh=0.00, amount_usd=-amt, posted_date=ctx.now()[:10],
               source_billing_id="", referred_customer_id=referred_customer_id, etf_months_remaining=0)
    return f"Sign-up credit line {rid} posted on agreement {power_agreement_id} for the cycle starting {billing_period_start}: -{amt:.2f} USD."

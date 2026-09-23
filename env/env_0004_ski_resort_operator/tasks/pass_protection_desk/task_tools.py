"""Hidden task tools for the pass protection desk of the Granite Ridge Mountain Collective.

Each tool performs one atomic write on the protection records and nothing else: it neither
aggregates the account nor judges whether the write is owed. The amounts and dates handed to
these tools are worked out by the person calling them from the collective's published terms and
the records the shared finders return.
"""

from erlbench import ToolContext, tool


@tool(owner="user", rw="write")
def confirm_plan_value_amendment_50d33fe4(ctx: ToolContext, protection_plan_id: str,
                                          covered_value_usd: float,
                                          repriced_premium_usd: float) -> str:
    """The household itself confirms a change to the protection plan it holds, so that the plan
    covers the holding at the value the collective's record shows for it and carries the premium
    that goes with that value. One call rewrites two things on the named plan: the value the cover
    and the premium are worked out from becomes the value confirmed here, and the premium standing
    on the plan becomes the premium confirmed here. Nothing else on the plan moves: the plan keeps
    its state, its dates, its insured, the holding it is written over and the cover already loaded
    for the season. Once the call returns, the household can see the new covered value and the new
    premium on the plan whenever the plan is read back.

    Args:
        protection_plan_id: Id class — the reference number of the single protection plan the
            household is confirming the change on, as the protection plan lookup returns it for
            this household.
        covered_value_usd: Fixed-format class — the value the plan is to cover, in USD, given to 2
            decimal places as a plain number such as 1234.56 with no currency symbol and no
            thousands separator; it is stored to the cent exactly as passed.
        repriced_premium_usd: Fixed-format class — the premium the plan is to carry, in USD, given
            to 2 decimal places as a plain number such as 123.45 with no currency symbol and no
            thousands separator; it is stored to the cent exactly as passed.

    Returns:
        A single line of confirmation text naming the protection plan reference, the covered value
        now standing on the plan in USD to the cent, and the premium now standing on the plan in USD
        to the cent. The line beginning with the word Confirmed is the receipt that the change was
        written; any other wording means the plan was not rewritten.
    """
    ctx.update("insure_holdings", protection_plan_id,
               covered_value_usd=round(float(covered_value_usd), 2),
               premium_usd=round(float(repriced_premium_usd), 2))
    return (f"Confirmed on protection plan {protection_plan_id}: covered value now "
            f"{round(float(covered_value_usd), 2)} USD, premium now "
            f"{round(float(repriced_premium_usd), 2)} USD.")


@tool(owner="agent", rw="write")
def settle_protection_claim_ed51c2df(ctx: ToolContext, protection_plan_id: str,
                                     covered_holding_id: str, related_event_id: str,
                                     claim_reason: str, payout_method: str,
                                     payout_amount_usd: float) -> str:
    """Pay an allowed claim out on a protection plan and draw the money down from the cover the plan
    carries for the season. One call books a single payout entry on that plan's protection account
    for the amount given, tied to the holding the cover is written over, to what the household
    claimed on, and to the entry recording the paper the payout was assessed from. The household
    sees the money reach them by the route named here, and the cover left on the plan for the rest
    of the season falls by the amount paid, since the protection account balance is the sum of the
    cover loaded less every payout booked against it.

    Args:
        protection_plan_id: Id class — the reference number of the protection plan the payout is
            booked on, as the protection plan lookup returns it.
        covered_holding_id: Id class — the reference number of the holding the plan is written over
            and the claim was made about, read from the covered holding field of that plan.
        related_event_id: Id class — the reference number of the single protection account entry the
            payout is assessed from, read from the protection account entries of that plan.
        claim_reason: Enum class — what the household claimed on, exactly one of: medical_injury
            where the insured was hurt and cannot ski; medical_illness where the insured fell ill
            and cannot ski; job_loss where the household lost the employment it was relying on;
            relocation where the household has moved permanently away from the region; mountain_closure
            where the mountain itself was shut; travel_disruption where the journey to the mountain
            was lost; bereavement where a death in the household ended the season; none where the
            entry is tied to no claim at all.
        payout_method: Enum class — how the money reaches the household, exactly one of:
            resort_credit where it is placed on the household account to spend with the collective;
            original_payment_method where it goes back to the card or bank the premium was taken
            from; bank_transfer where it is sent to the household's own bank account; none where the
            entry moves no money to the household.
        payout_amount_usd: Fixed-format class — the money paid out on this claim, in USD, given to 2
            decimal places as a plain number such as 1234.56 with no currency symbol and no thousands
            separator; it is booked to the cent exactly as passed.

    Returns:
        A single line of confirmation text naming the new protection account entry reference, the
        protection plan it was booked on, the amount paid out in USD to the cent and the route it
        went by. The line beginning with the word Paid is the receipt that the payout was booked;
        any other wording means nothing was booked.
    """
    plan = (ctx.find("insure_holdings", protection_plan_id=protection_plan_id) or [{}])[0]
    rid = ctx.make_id("ins_", protection_plan_id, covered_holding_id, related_event_id,
                      claim_reason, payout_method, payout_amount_usd)
    ctx.create("insure_ledger", rid, insure_event_id=rid,
               protection_plan_id=protection_plan_id,
               customer_id=plan.get("customer_id", ""),
               event_type="insure_claim_payment",
               related_event_id=related_event_id,
               covered_holding_id=covered_holding_id,
               season_code=plan.get("season_code", ""),
               event_date=ctx.now()[:10],
               amount_usd=round(float(payout_amount_usd), 2),
               claim_reason=claim_reason,
               payout_method=payout_method)
    return (f"Paid {round(float(payout_amount_usd), 2)} USD on protection plan "
            f"{protection_plan_id} by {payout_method}; protection account entry {rid}.")


@tool(owner="agent", rw="write")
def present_plan_premium_8deb00b0(ctx: ToolContext, protection_plan_id: str,
                                  covered_holding_id: str, premium_amount_usd: float) -> str:
    """Raise premium on a protection plan, so that what the household owes for its cover is carried
    on the plan's protection account rather than left standing outside it. One call books a single
    premium entry of the amount given against the named plan, tied to the holding the cover is
    written over, and the premium still to be collected on that plan rises by exactly that amount,
    the protection account balance being the sum of everything raised on it less everything paid
    against it. The household sees the amount on the plan's protection account and is asked for it in
    the ordinary way the plan is collected.

    Args:
        protection_plan_id: Id class — the reference number of the protection plan the premium is
            raised on, as the protection plan lookup returns it.
        covered_holding_id: Id class — the reference number of the holding the plan is written over,
            read from the covered holding field of that plan.
        premium_amount_usd: Fixed-format class — the premium raised by this entry, in USD, given to 2
            decimal places as a plain number such as 123.45 with no currency symbol and no thousands
            separator; it is booked to the cent exactly as passed.

    Returns:
        A single line of confirmation text naming the new protection account entry reference, the
        protection plan it was booked on and the premium raised in USD to the cent. The line
        beginning with the word Raised is the receipt that the entry was booked; any other wording
        means nothing was booked.
    """
    plan = (ctx.find("insure_holdings", protection_plan_id=protection_plan_id) or [{}])[0]
    rid = ctx.make_id("ins_", protection_plan_id, covered_holding_id, premium_amount_usd)
    ctx.create("insure_ledger", rid, insure_event_id=rid,
               protection_plan_id=protection_plan_id,
               customer_id=plan.get("customer_id", ""),
               event_type="insure_premium_charge",
               covered_holding_id=covered_holding_id,
               season_code=plan.get("season_code", ""),
               event_date=ctx.now()[:10],
               amount_usd=round(float(premium_amount_usd), 2),
               charge_category="premium")
    return (f"Raised {round(float(premium_amount_usd), 2)} USD of premium on protection plan "
            f"{protection_plan_id}; protection account entry {rid}.")


@tool(owner="agent", rw="write")
def raise_plan_giveup_charge_59dbe3e5(ctx: ToolContext, protection_plan_id: str,
                                      fee_amount_usd: float) -> str:
    """Raise the charge a protection plan owes for being given up, so that it stands on the plan's
    protection account as an amount the household owes. One call books a single
    plan fee entry of the amount given against the named plan, marked as the charge for giving a plan
    up, and the amount still to be collected on that plan rises by exactly that amount. The household
    sees the charge on the plan's protection account whenever the account is read back to them.

    Args:
        protection_plan_id: Id class — the reference number of the protection plan the charge is
            raised on, as the protection plan lookup returns it.
        fee_amount_usd: Fixed-format class — the charge raised by this entry, in USD, given to 2
            decimal places as a plain number such as 12.34 with no currency symbol and no thousands
            separator; it is booked to the cent exactly as passed.

    Returns:
        A single line of confirmation text naming the new protection account entry reference, the
        protection plan it was booked on and the charge raised in USD to the cent. The line beginning
        with the word Charged is the receipt that the entry was booked; any other wording means
        nothing was booked.
    """
    plan = (ctx.find("insure_holdings", protection_plan_id=protection_plan_id) or [{}])[0]
    rid = ctx.make_id("ins_", protection_plan_id, fee_amount_usd, "cancellation_fee")
    ctx.create("insure_ledger", rid, insure_event_id=rid,
               protection_plan_id=protection_plan_id,
               customer_id=plan.get("customer_id", ""),
               event_type="insure_fee_charge",
               season_code=plan.get("season_code", ""),
               event_date=ctx.now()[:10],
               amount_usd=round(float(fee_amount_usd), 2),
               charge_category="cancellation_fee")
    return (f"Charged {round(float(fee_amount_usd), 2)} USD on protection plan "
            f"{protection_plan_id} for giving the plan up; protection account entry {rid}.")


@tool(owner="user", rw="write")
def confirm_plan_giveup_9d16ef5f(ctx: ToolContext, protection_plan_id: str,
                                 cancellation_reason: str,
                                 closing_premium_balance_usd: float) -> str:
    """The household itself gives up the protection plan it holds and settles the plan's protection
    account in the same step. One call moves the named plan to the given-up state, records why the
    household gave it up and the day cover last stood as today's date, and sets what the plan's
    protection account is left standing at to the amount confirmed here, so the household knows
    exactly what remains owed on the plan. Cover stops on the plan from that day and the household can see the state, the reason
    and the amount left standing whenever the plan is read back.

    Args:
        protection_plan_id: Id class — the reference number of the protection plan the household is
            giving up, as the protection plan lookup returns it for this household.
        cancellation_reason: Enum class — why the household gives the plan up, exactly one of:
            guest_request where the household simply asks to end the cover; no_reason_given where
            they end it without saying why; covered_holding_cancelled where the holding the plan is
            written over has itself been given up; non_payment where the collective ends it because
            the premium went unpaid; collective_error where it is unwound because the collective
            wrote it in error; none where the plan has not been given up at all.
        closing_premium_balance_usd: Fixed-format class — what the plan's protection account is left
            standing at, in USD, given to 2 decimal places as a plain number such as 12.34 with no
            currency symbol and no thousands separator; it is stored to the cent exactly as passed.

    Returns:
        A single line of confirmation text naming the protection plan, the reason recorded, the day
        cover last stood and the amount the protection account is left standing at in USD to the
        cent. The line beginning with the word Given is the receipt that the plan was given up; any
        other wording means the plan still stands.
    """
    ctx.update("insure_holdings", protection_plan_id, status="cancelled",
               cancellation_reason=cancellation_reason, closed_date=ctx.now()[:10],
               premium_balance_usd=round(float(closing_premium_balance_usd), 2))
    return (f"Given up: protection plan {protection_plan_id} recorded as {cancellation_reason} with "
            f"cover last standing {ctx.now()[:10]}; protection account left standing at "
            f"{round(float(closing_premium_balance_usd), 2)} USD.")

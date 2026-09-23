"""Hidden task tools of the season pass billing desk.

Each tool performs one atomic business write on a season pass record and its pass account. The
names are discoverable only through the extended charter's target_tool entries, and every call is
reached through the unlock/call meta tools. No tool judges eligibility, gathers history or works
out a policy figure: the agent reads the records, works the figure out from the published terms,
and passes it in.
"""

from erlbench import ToolContext, tool


@tool(owner="agent", rw="write")
def collect_past_due_0159c539(ctx: ToolContext, pass_id: str, presented_amount_usd: float) -> str:
    """Take one payment at the desk against a season pass account and record it as collected money.
    The payment is booked on the pass account as a cleared collection dated today, and the amount
    still to be collected on that pass record drops by the same figure, so the guest sees the
    arrears on their pass account fall the moment the call ends. Use it when money that has fallen
    due on a financed pass is being taken from the guest during the call. Success is the collection
    reference coming back with the figure collected and the new amount still to be collected.

    Args:
        pass_id: Id class — the reference number of the season pass record whose pass account the
            payment is taken against, as returned by the season pass lookup.
        presented_amount_usd: Fixed-format class — the money taken in this single payment, in USD
            to 2 decimal places, never negative and never rounded to whole dollars; the
            collection is booked at exactly this figure.

    Returns:
        A confirmation sentence carrying the new pass account entry reference (a string beginning
        pcol_), the pass record reference it was booked against, the amount collected in USD to 2
        decimal places and the amount still to be collected on that pass account afterwards, also
        in USD to 2 decimal places. The presence of that entry reference is what indicates the
        payment was recorded.
    """
    found = ctx.find("passes_holdings", pass_id=pass_id)
    row = found[0] if found else {}
    amount = round(float(presented_amount_usd), 2)
    balance = round(float(row.get("installment_balance_usd") or 0) - amount, 2)
    rid = ctx.make_id("pcol_", pass_id, amount)
    ctx.create("passes_ledger", rid, pass_event_id=rid, pass_id=pass_id,
               customer_id=row.get("customer_id", ""), event_type="passes_installment_charge",
               season_code=row.get("season_code", ""), event_date=ctx.now()[:10],
               amount_usd=amount, charge_category="pass_price",
               billing_channel="phone_service_centre")
    ctx.update("passes_holdings", pass_id, installment_balance_usd=balance)
    return (f"Collection {rid} recorded on pass {pass_id}: {amount:.2f} USD taken; "
            f"{balance:.2f} USD still to be collected on that pass account.")


@tool(owner="agent", rw="write")
def restore_pass_scanning_08275b43(ctx: ToolContext, pass_id: str, restoration_charge_usd: float) -> str:
    """Put a season pass back into the state in which it admits the holder at the lift, and place
    the charge for that restoration on the pass account. The pass record moves to the scannable
    state, a restoration charge dated today is booked on the pass account, and the amount still to
    be collected rises by that charge, so the holder can scan again from that moment and sees the
    charge on their next statement. Success is the restoration charge reference coming back with
    the charge booked and the new amount still to be collected.

    Args:
        pass_id: Id class — the reference number of the season pass record whose scanning
            privileges are being restored, as returned by the season pass lookup.
        restoration_charge_usd: Fixed-format class — the charge placed on the pass account for this
            restoration, in USD to 2 decimal places, never negative and booked at exactly the
            figure given.

    Returns:
        A confirmation sentence carrying the new pass account entry reference (a string beginning
        prst_), the pass record reference, the state the pass record now stands in, the charge
        booked in USD to 2 decimal places and the amount still to be collected on that pass account
        afterwards, also in USD to 2 decimal places. The presence of that entry reference is what
        indicates the restoration was recorded.
    """
    found = ctx.find("passes_holdings", pass_id=pass_id)
    row = found[0] if found else {}
    charge = round(float(restoration_charge_usd), 2)
    balance = round(float(row.get("installment_balance_usd") or 0) + charge, 2)
    rid = ctx.make_id("prst_", pass_id, charge)
    ctx.create("passes_ledger", rid, pass_event_id=rid, pass_id=pass_id,
               customer_id=row.get("customer_id", ""), event_type="passes_fee_charge",
               season_code=row.get("season_code", ""), event_date=ctx.now()[:10],
               amount_usd=charge, charge_category="reinstatement_fee",
               billing_channel="phone_service_centre")
    ctx.update("passes_holdings", pass_id, status="active", installment_balance_usd=balance)
    return (f"Restoration {rid} recorded on pass {pass_id}: the pass record now stands active, "
            f"{charge:.2f} USD charged; {balance:.2f} USD still to be collected on that pass account.")


@tool(owner="user", rw="write")
def elect_pass_carry_forward_09e30d1a(ctx: ToolContext, pass_id: str, next_season_code: str,
                                      carry_forward_fee_usd: float) -> str:
    """Give up the rest of this winter on a season pass and carry it to a named later season, as
    the holder's own election. The pass record moves to the carried-forward state and is stamped
    with the season it now belongs to, the fee for the election is booked on the pass account dated
    today, and the amount still to be collected rises by that fee, so the pass stops admitting the
    holder this winter and comes back for the season named. Success is the election reference
    coming back with the season stamped and the fee booked.

    Args:
        pass_id: Id class — the reference number of the season pass record being carried forward,
            as returned by the season pass lookup.
        next_season_code: Fixed-format class — the season the pass is carried to, written as the
            collective writes a season, YYYY-YY, e.g. 2027-28, with no spaces and no other
            punctuation; an empty value is not accepted.
        carry_forward_fee_usd: Fixed-format class — the fee placed on the pass account for the
            election, in USD to 2 decimal places, never negative and booked at exactly the figure
            given.

    Returns:
        A confirmation sentence carrying the new pass account entry reference (a string beginning
        pcfw_), the pass record reference, the season the pass now belongs to, the fee booked in
        USD to 2 decimal places and the amount still to be collected on that pass account
        afterwards, also in USD to 2 decimal places. The presence of that entry reference is what
        indicates the election was recorded.
    """
    found = ctx.find("passes_holdings", pass_id=pass_id)
    row = found[0] if found else {}
    fee = round(float(carry_forward_fee_usd), 2)
    balance = round(float(row.get("installment_balance_usd") or 0) + fee, 2)
    rid = ctx.make_id("pcfw_", pass_id, next_season_code, fee)
    ctx.create("passes_ledger", rid, pass_event_id=rid, pass_id=pass_id,
               customer_id=row.get("customer_id", ""), event_type="passes_fee_charge",
               season_code=row.get("season_code", ""), event_date=ctx.now()[:10],
               amount_usd=fee, charge_category="deferral_fee",
               billing_channel="phone_service_centre")
    ctx.update("passes_holdings", pass_id, status="deferred", deferred_to_season=next_season_code,
               installment_balance_usd=balance)
    return (f"Carry-forward {rid} recorded on pass {pass_id}: the pass record now stands deferred to "
            f"{next_season_code}, {fee:.2f} USD charged; {balance:.2f} USD still to be collected on "
            "that pass account.")


@tool(owner="agent", rw="write")
def apply_pass_credit_52fe36c9(ctx: ToolContext, pass_id: str, related_event_id: str,
                               credit_pot: str, credit_applied_usd: float) -> str:
    """Spend resort credit that is standing on a season pass record against the money the pass
    account still has to collect. One application is booked on the pass account dated today, the
    resort credit left on that pass record drops by the figure applied and the amount still to be
    collected drops by the same figure, so the guest sees both numbers fall at once. Success is the
    application reference coming back with the figure applied and the two new balances.

    Args:
        pass_id: Id class — the reference number of the season pass record the credit sits on and
            whose pass account is being reduced, as returned by the season pass lookup.
        related_event_id: Id class — the reference number of the pass account entry that issued the
            credit being spent, read from the pass account entry lookup.
        credit_pot: Enum class — which pot of resort credit the application is drawn from, exactly as
            the collective labels its credit. none — the entry touches no credit pot at all;
            pass_cancellation — credit issued because a pass was given up; downgrade_differential —
            credit issued because a pass was moved to a lower tier; service_recovery — credit issued
            to put right a day or a service the collective failed to deliver; protection_settlement —
            credit issued because a protection claim was settled in credit; duplicate_charge — credit
            issued to put right an amount the collective charged twice.
        credit_applied_usd: Fixed-format class — the resort credit spent in this single application,
            in USD to 2 decimal places, never negative and booked exactly as given.

    Returns:
        A confirmation sentence carrying the new pass account entry reference (a string beginning
        pcrd_), the pass record reference, the credit pot drawn from, the figure applied in USD to 2
        decimal places, the resort credit left on that pass record and the amount still to be
        collected afterwards, both in USD to 2 decimal places. The presence of that entry reference
        is what indicates the application was recorded.
    """
    found = ctx.find("passes_holdings", pass_id=pass_id)
    row = found[0] if found else {}
    applied = round(float(credit_applied_usd), 2)
    credit_left = round(float(row.get("pass_credit_usd") or 0) - applied, 2)
    balance = round(float(row.get("installment_balance_usd") or 0) - applied, 2)
    rid = ctx.make_id("pcrd_", pass_id, related_event_id, credit_pot, applied)
    ctx.create("passes_ledger", rid, pass_event_id=rid, pass_id=pass_id,
               customer_id=row.get("customer_id", ""), event_type="passes_credit_redeem",
               related_event_id=related_event_id, event_date=ctx.now()[:10], amount_usd=applied,
               credit_reason=credit_pot, billing_channel="phone_service_centre")
    ctx.update("passes_holdings", pass_id, pass_credit_usd=credit_left,
               installment_balance_usd=balance)
    return (f"Credit application {rid} recorded on pass {pass_id} from the {credit_pot} pot: "
            f"{applied:.2f} USD applied; {credit_left:.2f} USD of resort credit left on the pass "
            f"record and {balance:.2f} USD still to be collected on that pass account.")


@tool(owner="user", rw="write")
def give_up_season_pass_8c1a0eca(ctx: ToolContext, pass_id: str, protection_plan_id: str,
                                 cancellation_reason: str, retained_charge_usd: float) -> str:
    """Give up a season pass for good, as the household's own act, and have the charge the
    collective keeps placed on the pass account. The pass record moves to the given-up state, is
    stamped with today as the last date it admitted the holder and with the reason the household
    gives, the charge kept is booked on the pass account dated today, and the amount still to be
    collected rises by that charge, so the pass stops admitting the holder from that moment. Success
    is the surrender reference coming back with the reason recorded and the charge booked.

    Args:
        pass_id: Id class — the reference number of the season pass record being given up, as
            returned by the season pass lookup.
        protection_plan_id: Id class — the reference number of the protection plan record the
            collective checks the surrender against, as returned by the protection plan lookup; it
            is recorded with the surrender and the plan itself is left untouched.
        cancellation_reason: Enum class — why the household is giving the pass up, in the
            collective's own labels. none — no reason is being recorded at all; guest_request — the
            household simply no longer wants the pass; medical — the holder has been told they may
            not ski; relocation — the household has moved permanently away from the region;
            employment_loss — the household has lost the employment the pass was bought on;
            resort_closure — the collective itself has stopped running the season.
        retained_charge_usd: Fixed-format class — the charge the collective keeps and places on the
            pass account for the surrender, in USD to 2 decimal places, never negative and booked at
            exactly the figure given.

    Returns:
        A confirmation sentence carrying the new pass account entry reference (a string beginning
        pgup_), the pass record reference, the state the pass record now stands in, the reason
        recorded, the charge kept in USD to 2 decimal places and the amount still to be collected on
        that pass account afterwards, also in USD to 2 decimal places. The presence of that entry
        reference is what indicates the surrender was recorded.
    """
    found = ctx.find("passes_holdings", pass_id=pass_id)
    row = found[0] if found else {}
    charge = round(float(retained_charge_usd), 2)
    balance = round(float(row.get("installment_balance_usd") or 0) + charge, 2)
    rid = ctx.make_id("pgup_", pass_id, protection_plan_id, cancellation_reason, charge)
    ctx.create("passes_ledger", rid, pass_event_id=rid, pass_id=pass_id,
               customer_id=row.get("customer_id", ""), event_type="passes_fee_charge",
               season_code=row.get("season_code", ""), event_date=ctx.now()[:10],
               amount_usd=charge, charge_category="cancellation_fee",
               billing_channel="phone_service_centre")
    ctx.update("passes_holdings", pass_id, status="cancelled", closed_date=ctx.now()[:10],
               cancellation_reason=cancellation_reason, installment_balance_usd=balance)
    return (f"Surrender {rid} recorded on pass {pass_id}: the pass record now stands cancelled with "
            f"the reason {cancellation_reason}, {charge:.2f} USD kept; {balance:.2f} USD still to be "
            "collected on that pass account.")


@tool(owner="agent", rw="write")
def issue_settlement_credit_d3237287(ctx: ToolContext, pass_id: str, protection_plan_id: str,
                                     settlement_credit_usd: float) -> str:
    """Issue resort credit against a season pass record for what the collective returns to the
    household on that pass. The credit is booked on the pass account dated today and the resort
    credit standing on that pass record rises by the same figure, so the household can spend it
    across the collective within the tier's validity. Success is the credit reference coming back
    with the figure issued and the new resort credit standing on the record.

    Args:
        pass_id: Id class — the reference number of the season pass record the credit is issued
            against, as returned by the season pass lookup.
        protection_plan_id: Id class — the reference number of the protection plan record the
            collective checks the settlement against, as returned by the protection plan lookup; it
            is recorded with the credit and the plan itself is left untouched.
        settlement_credit_usd: Fixed-format class — the resort credit issued to the household, in USD
            to 2 decimal places, never negative and booked at exactly the figure given.

    Returns:
        A confirmation sentence carrying the new pass account entry reference (a string beginning
        pstl_), the pass record reference, the credit issued in USD to 2 decimal places and the
        resort credit standing on that pass record afterwards, also in USD to 2 decimal places. The
        presence of that entry reference is what indicates the credit was issued.
    """
    found = ctx.find("passes_holdings", pass_id=pass_id)
    row = found[0] if found else {}
    credit = round(float(settlement_credit_usd), 2)
    standing = round(float(row.get("pass_credit_usd") or 0) + credit, 2)
    rid = ctx.make_id("pstl_", pass_id, protection_plan_id, credit)
    ctx.create("passes_ledger", rid, pass_event_id=rid, pass_id=pass_id,
               customer_id=row.get("customer_id", ""), event_type="passes_credit_issue",
               season_code=row.get("season_code", ""), event_date=ctx.now()[:10],
               amount_usd=credit, credit_reason="pass_cancellation")
    ctx.update("passes_holdings", pass_id, pass_credit_usd=standing)
    return (f"Settlement credit {rid} issued on pass {pass_id}: {credit:.2f} USD of resort credit "
            f"issued; {standing:.2f} USD of resort credit now standing on that pass record.")

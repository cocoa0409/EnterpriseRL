"""Hidden task tools for the summit_miles_status_and_upgrades difficulty (Crestline Summit loyalty).

Each tool performs exactly one atomic posting on a Summit membership with the values the agent (or,
for an owner=user tool, the member) supplies; none of them computes, checks or refuses anything on
policy grounds. They are reached only through unlock_* -> call_* and named by the extended charter.
"""

from erlbench import ToolContext, tool


@tool(owner="agent", rw="write")
def post_retro_credit_03268362(ctx: ToolContext, membership_id: str, source_ticket_id: str, segment_number: int,
                               flight_number: str, flight_date: str, eligible_fare_usd: float, miles: int) -> str:
    """Credit a flown Crestline flight segment that never posted to a Summit membership (a retro credit).

    One call books one retro-credit entry for one flown segment on the membership's mileage activity,
    dated today, carrying the ticket, segment, flight, flight date, the segment's eligible fare and the
    award miles credited. The membership's award-mile balance rises by exactly those miles, its latest
    activity date becomes today, and a membership that was enrolled or dormant becomes active. No
    qualifying dollars are credited by this entry. The member sees the segment and its
    miles on the Summit activity statement; the call is complete when the receipt below comes back.

    Args:
        membership_id: Id class — reference number of the Summit membership record to credit, as returned by the Summit membership lookup for the verified caller.
        source_ticket_id: Id class — reference number of the Crestline ticket record whose flown coupon is being credited, as returned by the ticket lookup for the customer.
        segment_number: Fixed-format class — position of the flown segment on that ticket, an integer >= 0 (1 for segment one), exactly as shown on the flown-coupon entry of the ticket's fare history.
        flight_number: Fixed-format class — Crestline flight number of the flown coupon, written as CR followed by 1-4 digits with no space, exactly as shown on the flown-coupon entry.
        flight_date: Fixed-format class — scheduled local departure date of the flown coupon, formatted YYYY-MM-DD.
        eligible_fare_usd: Fixed-format class — base fare of the segment excluding government taxes, in USD, a non-negative amount with 2 decimal places.
        miles: Fixed-format class — award miles credited for the segment, a whole number of miles given as an integer >= 0 with no decimals.

    Returns:
        A dictionary rendered as text with: loyalty_activity_id (reference number of the new retro-credit entry), event_type (always loyalty_retro_credit), miles (integer miles credited), mile_balance (integer award-mile balance including the credit), status (membership status resulting from the credit, active) and activity_date (posting date, YYYY-MM-DD). A receipt carrying a loyalty_activity_id means the credit is booked.
    """
    found = ctx.find("loyalty_holdings", membership_id=membership_id)
    m = found[0] if found else {}
    rid = ctx.make_id("lra_", membership_id, source_ticket_id, segment_number, flight_number, flight_date,
                      eligible_fare_usd, miles)
    today = ctx.now()[:10]
    ctx.create("loyalty_activity", rid, loyalty_activity_id=rid, membership_id=membership_id,
               customer_id=m.get("customer_id"), event_type="loyalty_retro_credit", activity_date=today,
               miles=int(miles), qualifying_dollars=0.0, certificate_count=0, source_ticket_id=source_ticket_id,
               segment_number=int(segment_number), flight_number=flight_number, flight_date=flight_date,
               eligible_fare_usd=round(float(eligible_fare_usd), 2), fee_usd=0.0, purchase_amount_usd=0.0)
    new_balance = int(m.get("mile_balance") or 0) + int(miles)
    new_status = "active" if m.get("status") in ("enrolled", "dormant", "active") else m.get("status")
    ctx.update("loyalty_holdings", membership_id, mile_balance=new_balance, last_activity_date=today,
               status=new_status)
    return str({"loyalty_activity_id": rid, "event_type": "loyalty_retro_credit", "miles": int(miles),
                "mile_balance": new_balance, "status": new_status, "activity_date": today})


@tool(owner="agent", rw="write")
def post_segment_qualifying_dollars_d0ee7d28(ctx: ToolContext, membership_id: str, source_ticket_id: str,
                                             segment_number: int, flight_date: str,
                                             qualifying_dollars: float) -> str:
    """Post the Summit qualifying dollars of one credited Crestline flight segment to a membership.

    One call books one qualifying-dollar entry for one flown segment on the membership's activity,
    dated today, carrying the ticket, segment and flight date it belongs to. The membership's
    qualifying dollars for the current calendar year rise by exactly the amount posted; award miles,
    the tier and the latest activity date are not changed. The member sees the amount on
    the qualifying-dollar statement; the call is complete when the receipt below comes back.

    Args:
        membership_id: Id class — reference number of the Summit membership record the qualifying dollars post to, as returned by the Summit membership lookup for the verified caller.
        source_ticket_id: Id class — reference number of the Crestline ticket record of the credited segment, as returned by the ticket lookup or shown on the segment's mileage entry.
        segment_number: Fixed-format class — position of the credited segment on that ticket, an integer >= 0 (1 for segment one), exactly as shown on the segment's mileage entry.
        flight_date: Fixed-format class — scheduled local departure date of the credited segment, formatted YYYY-MM-DD, exactly as shown on the segment's mileage entry.
        qualifying_dollars: Fixed-format class — qualifying dollars posted for the segment, in USD, a non-negative amount with 2 decimal places.

    Returns:
        A dictionary rendered as text with: loyalty_activity_id (reference number of the new qualifying-dollar entry), event_type (always loyalty_mqd_accrual), qualifying_dollars (USD amount posted, 2 decimal places) and qualifying_dollars_ytd (USD qualifying dollars of the calendar year including the posting, 2 decimal places). A receipt carrying a loyalty_activity_id means the posting is booked.
    """
    found = ctx.find("loyalty_holdings", membership_id=membership_id)
    m = found[0] if found else {}
    rid = ctx.make_id("lqd_", membership_id, source_ticket_id, segment_number, flight_date, qualifying_dollars)
    today = ctx.now()[:10]
    ctx.create("loyalty_activity", rid, loyalty_activity_id=rid, membership_id=membership_id,
               customer_id=m.get("customer_id"), event_type="loyalty_mqd_accrual", activity_date=today, miles=0,
               qualifying_dollars=round(float(qualifying_dollars), 2), certificate_count=0,
               source_ticket_id=source_ticket_id, segment_number=int(segment_number), flight_date=flight_date,
               eligible_fare_usd=0.0, fee_usd=0.0, purchase_amount_usd=0.0)
    ytd = round(float(m.get("qualifying_dollars_ytd") or 0) + round(float(qualifying_dollars), 2), 2)
    ctx.update("loyalty_holdings", membership_id, qualifying_dollars_ytd=ytd)
    return str({"loyalty_activity_id": rid, "event_type": "loyalty_mqd_accrual",
                "qualifying_dollars": round(float(qualifying_dollars), 2), "qualifying_dollars_ytd": ytd})


@tool(owner="agent", rw="write")
def record_tier_requalification_84e40849(ctx: ToolContext, membership_id: str, new_tier: str,
                                         tier_valid_through: str) -> str:
    """Record the Summit tier a membership has qualified for during the current calendar year.

    One call changes the membership's current tier to the tier given, marks it as earned by
    qualification, and sets the last day the tier stays valid. Balances (award miles, qualifying
    dollars, upgrade certificates), the status and the activity history are not changed. From the
    moment the receipt comes back the member holds the new tier and every tier-based benefit and
    charge follows it.

    Args:
        membership_id: Id class — reference number of the Summit membership record whose tier is recorded, as returned by the Summit membership lookup for the verified caller.
        new_tier: Enum class — the tier now held, exactly one of: Summit Member when the membership holds the base tier with no elite status; Summit Silver when the entry-level elite tier is held; Summit Gold when the elite tier above Silver is held; Summit Platinum when the elite tier above Gold is held; Summit Diamond when the highest tier reachable by qualification is held; Summit Chairman when the invitation-only top tier is held.
        tier_valid_through: Fixed-format class — last calendar day the tier stays valid, formatted YYYY-MM-DD.

    Returns:
        A dictionary rendered as text with: membership_id (reference number of the membership), variant_name (the tier now held), tier_basis (always earned) and tier_valid_through (last valid day, YYYY-MM-DD). A receipt whose variant_name equals the tier given means the change is recorded.
    """
    ctx.update("loyalty_holdings", membership_id, variant_name=new_tier, tier_basis="earned",
               tier_valid_through=tier_valid_through)
    return str({"membership_id": membership_id, "variant_name": new_tier, "tier_basis": "earned",
                "tier_valid_through": tier_valid_through})


@tool(owner="user", rw="write")
def reinstate_expired_miles_d28241c8(ctx: ToolContext, membership_id: str, reversed_activity_id: str, miles: int,
                                     fee_usd: float) -> str:
    """Reinstate, as the member, award miles that were forfeited for inactivity, paying the reinstatement fee.

    The member confirms, for one inactivity forfeiture on their own Summit membership, that its miles
    are put back and that the reinstatement fee is charged to them. One call books one reinstatement
    entry dated today that names the forfeiture it undoes and records the miles returned and the fee
    charged; the award-mile balance rises by exactly those miles. The latest activity date and the
    status are not changed. The member sees the miles back on the balance and the fee on the receipt.

    Args:
        membership_id: Id class — reference number of the member's own Summit membership record, as the agent reads it from the Summit membership lookup and hands it over.
        reversed_activity_id: Id class — reference number of the inactivity forfeiture entry being undone, as shown on the membership's activity statement and handed over by the agent.
        miles: Fixed-format class — award miles put back, a whole number of miles given as an integer >= 0 with no decimals.
        fee_usd: Fixed-format class — reinstatement fee charged to the member, in USD, a non-negative amount with 2 decimal places.

    Returns:
        A dictionary rendered as text with: loyalty_activity_id (reference number of the new reinstatement entry), event_type (always loyalty_miles_reinstatement), miles (integer miles put back), fee_usd (USD fee charged, 2 decimal places) and mile_balance (integer award-mile balance including the miles put back). A receipt carrying a loyalty_activity_id means the reinstatement is booked and the fee charged.
    """
    found = ctx.find("loyalty_holdings", membership_id=membership_id)
    m = found[0] if found else {}
    rid = ctx.make_id("lrn_", membership_id, reversed_activity_id, miles, fee_usd)
    ctx.create("loyalty_activity", rid, loyalty_activity_id=rid, membership_id=membership_id,
               customer_id=m.get("customer_id"), event_type="loyalty_miles_reinstatement",
               activity_date=ctx.now()[:10], miles=int(miles), qualifying_dollars=0.0, certificate_count=0,
               reversed_activity_id=reversed_activity_id, fee_usd=round(float(fee_usd), 2),
               purchase_amount_usd=0.0, eligible_fare_usd=0.0)
    new_balance = int(m.get("mile_balance") or 0) + int(miles)
    ctx.update("loyalty_holdings", membership_id, mile_balance=new_balance)
    return str({"loyalty_activity_id": rid, "event_type": "loyalty_miles_reinstatement", "miles": int(miles),
                "fee_usd": round(float(fee_usd), 2), "mile_balance": new_balance})


@tool(owner="agent", rw="write")
def post_choice_bonus_miles_029b6e8c(ctx: ToolContext, membership_id: str, choice_year: str, miles: int) -> str:
    """Credit the bonus miles owed for a choice-benefit selection of bonus miles on a Summit membership.

    One call books one bonus credit entry dated today, marked as a choice-benefit bonus and carrying
    the qualification year of the selection it fulfils and the miles credited. The award-mile balance
    rises by exactly those miles; the latest activity date, the tier and the status are not changed.
    The member sees the bonus on the activity statement; the call is complete when the receipt below
    comes back.

    Args:
        membership_id: Id class — reference number of the Summit membership record to credit, as returned by the Summit membership lookup for the verified caller.
        choice_year: Fixed-format class — qualification year of the choice-benefit selection being fulfilled, four digits YYYY, exactly as shown on the selection entry.
        miles: Fixed-format class — bonus miles credited, a whole number of miles given as an integer >= 0 with no decimals.

    Returns:
        A dictionary rendered as text with: loyalty_activity_id (reference number of the new bonus entry), event_type (always loyalty_bonus_credit), choice_year (YYYY), miles (integer miles credited) and mile_balance (integer award-mile balance including the credit). A receipt carrying a loyalty_activity_id means the bonus is booked.
    """
    found = ctx.find("loyalty_holdings", membership_id=membership_id)
    m = found[0] if found else {}
    rid = ctx.make_id("lbc_", membership_id, choice_year, miles)
    ctx.create("loyalty_activity", rid, loyalty_activity_id=rid, membership_id=membership_id,
               customer_id=m.get("customer_id"), event_type="loyalty_bonus_credit", activity_date=ctx.now()[:10],
               miles=int(miles), qualifying_dollars=0.0, certificate_count=0, bonus_reason="choice_benefit",
               choice_year=choice_year, segment_number=0, eligible_fare_usd=0.0, fee_usd=0.0,
               purchase_amount_usd=0.0)
    new_balance = int(m.get("mile_balance") or 0) + int(miles)
    ctx.update("loyalty_holdings", membership_id, mile_balance=new_balance)
    return str({"loyalty_activity_id": rid, "event_type": "loyalty_bonus_credit", "choice_year": choice_year,
                "miles": int(miles), "mile_balance": new_balance})


@tool(owner="agent", rw="write")
def post_miles_upgrade_charge_7f00044a(ctx: ToolContext, membership_id: str, source_ticket_id: str, segment_number: int,
                                       miles: int, fee_usd: float) -> str:
    """Charge a cleared miles upgrade to a Summit membership: the miles and the cash co-pay of one upgraded segment.

    One call books one redemption entry of the upgrade kind dated today for one segment of a ticket that
    was confirmed in the higher cabin with miles, carrying the ticket, the segment, the miles redeemed and
    the co-pay charged in cash. The award-mile balance falls by exactly those miles and the latest activity
    date becomes today; the tier and the status are not changed. The member sees the redemption and the
    co-pay on the activity statement; the call is complete when the receipt below comes back.

    Args:
        membership_id: Id class — reference number of the Summit membership record charged, as returned by the Summit membership lookup for the verified caller.
        source_ticket_id: Id class — reference number of the Crestline ticket record whose segment was upgraded, as shown on the upgrade clearance entry.
        segment_number: Fixed-format class — position of the upgraded segment on that ticket, an integer >= 0 (1 for segment one), exactly as shown on the upgrade clearance entry.
        miles: Fixed-format class — award miles redeemed for the upgraded segment, a whole number of miles given as an integer >= 0 with no decimals.
        fee_usd: Fixed-format class — cash co-pay charged for the upgraded segment, in USD, a non-negative amount with 2 decimal places.

    Returns:
        A dictionary rendered as text with: loyalty_activity_id (reference number of the new redemption entry), event_type (always loyalty_award_redemption), award_type (always upgrade), miles (integer miles redeemed), fee_usd (USD co-pay, 2 decimal places) and mile_balance (integer award-mile balance net of the miles redeemed). A receipt carrying a loyalty_activity_id means the charge is booked.
    """
    found = ctx.find("loyalty_holdings", membership_id=membership_id)
    m = found[0] if found else {}
    rid = ctx.make_id("lup_", membership_id, source_ticket_id, segment_number, miles, fee_usd)
    today = ctx.now()[:10]
    ctx.create("loyalty_activity", rid, loyalty_activity_id=rid, membership_id=membership_id,
               customer_id=m.get("customer_id"), event_type="loyalty_award_redemption", activity_date=today,
               miles=int(miles), qualifying_dollars=0.0, certificate_count=0, source_ticket_id=source_ticket_id,
               segment_number=int(segment_number), award_type="upgrade", fee_usd=round(float(fee_usd), 2),
               eligible_fare_usd=0.0, purchase_amount_usd=0.0)
    new_balance = int(m.get("mile_balance") or 0) - int(miles)
    ctx.update("loyalty_holdings", membership_id, mile_balance=new_balance, last_activity_date=today)
    return str({"loyalty_activity_id": rid, "event_type": "loyalty_award_redemption", "award_type": "upgrade",
                "miles": int(miles), "fee_usd": round(float(fee_usd), 2), "mile_balance": new_balance})


@tool(owner="agent", rw="write")
def issue_choice_upgrade_certificates_458899d3(ctx: ToolContext, membership_id: str, choice_year: str,
                                              certificate_count: int, certificate_expiry_date: str) -> str:
    """Issue the Summit Upgrade Certificates owed for a choice-benefit selection of upgrade certificates.

    One call books one certificate issue entry dated today carrying the qualification year of the
    selection it fulfils, the number of certificates issued and the expiry date of this batch. The
    membership's unused upgrade certificates rise by exactly that number; miles, the tier and the status
    are not changed. The member sees the new batch and its expiry on the statement; the call is complete
    when the receipt below comes back.

    Args:
        membership_id: Id class — reference number of the Summit membership record receiving the certificates, as returned by the Summit membership lookup for the verified caller.
        choice_year: Fixed-format class — qualification year of the choice-benefit selection being fulfilled, four digits YYYY, exactly as shown on the selection entry.
        certificate_count: Fixed-format class — number of upgrade certificates issued in the batch, an integer >= 0.
        certificate_expiry_date: Fixed-format class — last day the batch may be used, formatted YYYY-MM-DD.

    Returns:
        A dictionary rendered as text with: loyalty_activity_id (reference number of the new issue entry), event_type (always loyalty_certificate_issue), certificate_count (integer certificates issued), certificate_expiry_date (YYYY-MM-DD) and upgrade_certificate_balance (integer unused certificates including the new batch). A receipt carrying a loyalty_activity_id means the batch is issued.
    """
    found = ctx.find("loyalty_holdings", membership_id=membership_id)
    m = found[0] if found else {}
    rid = ctx.make_id("lci_", membership_id, choice_year, certificate_count, certificate_expiry_date)
    ctx.create("loyalty_activity", rid, loyalty_activity_id=rid, membership_id=membership_id,
               customer_id=m.get("customer_id"), event_type="loyalty_certificate_issue", activity_date=ctx.now()[:10],
               miles=0, qualifying_dollars=0.0, certificate_count=int(certificate_count),
               certificate_expiry_date=certificate_expiry_date, choice_year=choice_year, segment_number=0,
               eligible_fare_usd=0.0, fee_usd=0.0, purchase_amount_usd=0.0)
    new_count = int(m.get("upgrade_certificate_balance") or 0) + int(certificate_count)
    ctx.update("loyalty_holdings", membership_id, upgrade_certificate_balance=new_count)
    return str({"loyalty_activity_id": rid, "event_type": "loyalty_certificate_issue",
                "certificate_count": int(certificate_count), "certificate_expiry_date": certificate_expiry_date,
                "upgrade_certificate_balance": new_count})


@tool(owner="user", rw="write")
def buy_miles_4af9ade8(ctx: ToolContext, membership_id: str, miles: int, purchase_amount_usd: float) -> str:
    """Buy award miles, as the member, for the member's own Summit membership and pay the price.

    The member confirms a purchase of award miles on their own membership at the price stated. One call
    books one purchase entry dated today carrying the miles bought and the price paid; the award-mile
    balance rises by exactly those miles, the latest activity date becomes today and a dormant or
    enrolled membership becomes active. The member sees the miles on the balance and the price on the
    receipt; the call is complete when the receipt below comes back.

    Args:
        membership_id: Id class — reference number of the member's own Summit membership record, as the agent reads it from the Summit membership lookup and hands it over.
        miles: Fixed-format class — award miles bought, a whole number of miles given as an integer >= 0 with no decimals.
        purchase_amount_usd: Fixed-format class — price paid for the miles, in USD, a non-negative amount with 2 decimal places.

    Returns:
        A dictionary rendered as text with: loyalty_activity_id (reference number of the new purchase entry), event_type (always loyalty_miles_purchase), miles (integer miles bought), purchase_amount_usd (USD price paid, 2 decimal places) and mile_balance (integer award-mile balance including the miles bought). A receipt carrying a loyalty_activity_id means the purchase is booked and paid.
    """
    found = ctx.find("loyalty_holdings", membership_id=membership_id)
    m = found[0] if found else {}
    rid = ctx.make_id("lmp_", membership_id, miles, purchase_amount_usd)
    today = ctx.now()[:10]
    ctx.create("loyalty_activity", rid, loyalty_activity_id=rid, membership_id=membership_id,
               customer_id=m.get("customer_id"), event_type="loyalty_miles_purchase", activity_date=today,
               miles=int(miles), qualifying_dollars=0.0, certificate_count=0, segment_number=0,
               purchase_amount_usd=round(float(purchase_amount_usd), 2), eligible_fare_usd=0.0, fee_usd=0.0)
    new_balance = int(m.get("mile_balance") or 0) + int(miles)
    new_status = "active" if m.get("status") in ("enrolled", "dormant", "active") else m.get("status")
    ctx.update("loyalty_holdings", membership_id, mile_balance=new_balance, last_activity_date=today,
               status=new_status)
    return str({"loyalty_activity_id": rid, "event_type": "loyalty_miles_purchase", "miles": int(miles),
                "purchase_amount_usd": round(float(purchase_amount_usd), 2), "mile_balance": new_balance})

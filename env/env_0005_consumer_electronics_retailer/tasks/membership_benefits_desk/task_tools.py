"""Hidden task tools for the Northbeam Circle membership benefits desk.

Each tool lands one booking on a Circle membership record. None of them works out a
figure for the caller: the desk reads the membership, the ledger and the customer's other
Northbeam records, works the figure out from the published rules, and passes it in.
"""

from erlbench import ToolContext, tool


@tool(owner="agent", rw="write")
def grant_benefit_credit_b1d93258(ctx: ToolContext, membership_id: str, benefit_code: str,
                                  grant_cycle_year: str, credit_granted_usd: float) -> str:
    """Grant a named Circle benefit credit to a membership for one membership year.

    One call books a benefit credit grant on the membership named: the ledger gains a grant
    entry carrying the named benefit, the membership year it is granted for, the credit money
    and the tier the membership stands at, and the unspent benefit credit shown on the
    membership goes up by that money. The member can then see the credit on the membership and
    spend it against the charges that named benefit covers. The receipt naming the new grant
    entry is what shows the call went through.

    Args:
        membership_id: Id class — the reference number of the Circle membership record the credit
            is granted to, read from the membership record returned when the membership is looked up.
        benefit_code: Enum class — which named Circle benefit this grant carries, exactly one of:
            anniversary_reward, the yearly reward credit that goes with the membership year itself;
            install_credit, the credit that goes toward installation labour;
            delivery_credit, the credit that goes toward a delivery charge;
            service_credit, the credit that goes toward bench or on-site repair labour;
            haul_away_credit, the credit that goes toward taking an old item away;
            business_consultation_credit, the credit that goes toward a business consultation on a
            business tier.
        grant_cycle_year: Fixed-format class — the membership year the credit is granted for,
            written as the four-digit calendar year YYYY of the day that membership year begins,
            with no month or day part and no other punctuation.
        credit_granted_usd: Fixed-format class — the benefit credit money granted, in USD to 2
            decimal places, a positive amount rounded half to even at the cent; it is stored at
            exactly that precision and no unit symbol is passed.

    Returns:
        A confirmation line naming the membership, the benefit_code granted, the grant_cycle_year
        it was granted for, the credit money booked and the reference number of the new grant
        entry; the presence of that grant entry reference is what marks the call as completed.
    """
    rows = ctx.find("membership_holdings", membership_id=membership_id)
    if not rows:
        return f"Error: no Circle membership {membership_id}."
    holding = rows[0]
    rid = ctx.make_id("mbg_", membership_id, benefit_code, grant_cycle_year, credit_granted_usd)
    amount = round(float(credit_granted_usd), 2)
    ctx.create("membership_events", rid, membership_event_id=rid, membership_id=membership_id,
               customer_id=holding.get("customer_id"), event_type="membership_benefit_grant",
               benefit_amount=amount, benefit_code=benefit_code, grant_cycle_year=grant_cycle_year,
               event_date=ctx.now()[:10], channel="phone",
               tier_at_event=holding.get("variant_name"))
    ctx.update("membership_holdings", membership_id,
               benefit_credit_balance=round(float(holding.get("benefit_credit_balance") or 0) + amount, 2))
    return (f"Benefit credit granted on membership {membership_id}: {benefit_code} of {amount} "
            f"for membership year {grant_cycle_year}, booked as grant entry {rid}.")


@tool(owner="user", rw="write")
def settle_membership_dues_c8b60f0e(ctx: ToolContext, membership_id: str, settlement_payment_usd: float,
                                    payment_method: str, applied_period_start: str) -> str:
    """Settle, as the member, the dues standing on your own Circle membership.

    The member makes this payment themselves: one call books the money received against the
    billing period named, the membership ledger gains a payment entry carrying the money, the way
    it was paid and the period it was applied to, the dues still owed on the membership drop by
    that money, and a membership whose dues had fallen overdue is put back to active standing with
    the day it fell into grace cleared. The member sees the payment on the membership straight
    away, the dues owed fall accordingly and the membership reads as active again. The receipt
    naming the new payment entry is what shows the call went through.

    Args:
        membership_id: Id class — the reference number of the Circle membership the payment is made
            against, read from the membership record returned when the membership is looked up.
        settlement_payment_usd: Fixed-format class — the money the member is paying now, in USD to 2
            decimal places, a positive amount rounded half to even at the cent; it is stored at
            exactly that precision and no unit symbol is passed.
        payment_method: Enum class — how the member is paying, exactly one of:
            card_on_file, the payment card already kept on the profile is charged;
            store_credit, the money is taken from store credit held on a Northbeam credit account;
            bank_transfer, the member sends the money from a bank account;
            in_store_cash, the member pays at a store counter;
            business_invoice, the amount is put on a business account's invoice to be settled on its
            terms.
        applied_period_start: Fixed-format class — the first day of the billing period the payment is
            applied to, written as a calendar date YYYY-MM-DD with no time part and no time zone.

    Returns:
        A confirmation line naming the membership, the money received, the payment_method used, the
        billing period the money was applied to and the reference number of the new payment entry;
        the presence of that payment entry reference is what marks the call as completed.
    """
    rows = ctx.find("membership_holdings", membership_id=membership_id)
    if not rows:
        return f"Error: no Circle membership {membership_id}."
    holding = rows[0]
    rid = ctx.make_id("mpy_", membership_id, settlement_payment_usd, payment_method, applied_period_start)
    amount = round(float(settlement_payment_usd), 2)
    ctx.create("membership_events", rid, membership_event_id=rid, membership_id=membership_id,
               customer_id=holding.get("customer_id"), event_type="membership_dues_payment",
               payment_amount=amount, payment_method=payment_method,
               applied_period_start=applied_period_start, event_date=ctx.now()[:10], channel="phone")
    ctx.update("membership_holdings", membership_id,
               dues_outstanding=round(float(holding.get("dues_outstanding") or 0) - amount, 2),
               status="active", grace_start_date="")
    return (f"Payment received on membership {membership_id}: {amount} by {payment_method} applied to "
            f"the billing period beginning {applied_period_start}; the membership now reads as active, "
            f"booked as payment entry {rid}.")


@tool(owner="agent", rw="write")
def apply_benefit_credit_8295b346(ctx: ToolContext, membership_id: str, benefit_code: str,
                                  redemption_ref: str, credit_applied_usd: float) -> str:
    """Spend granted Circle benefit credit against one charge the member is holding.

    One call books the credit against the charge reference given: the membership ledger gains a
    redemption entry carrying the named benefit, the charge reference the credit was spent against
    and the credit money, and the unspent benefit credit shown on the membership drops by that
    money. The member sees the credit taken off their side of that charge and the remaining benefit
    credit on the membership. The receipt naming the new redemption entry is what shows the call
    went through.

    Args:
        membership_id: Id class — the reference number of the Circle membership whose credit is being
            spent, read from the membership record returned when the membership is looked up.
        benefit_code: Enum class — which named Circle benefit is being spent, exactly one of:
            anniversary_reward, the yearly reward credit that goes with the membership year itself;
            install_credit, the credit that goes toward installation labour;
            delivery_credit, the credit that goes toward a delivery charge;
            service_credit, the credit that goes toward bench or on-site repair labour;
            haul_away_credit, the credit that goes toward taking an old item away;
            business_consultation_credit, the credit that goes toward a business consultation on a
            business tier.
        redemption_ref: Verbatim class — the reference of the charge the credit is being spent
            against, taken from the way the customer reads it out on the call and copied character
            for character, keeping their wording, digits, letter case and punctuation, with nothing
            translated, tidied, shortened, added or dropped (verbatim).
        credit_applied_usd: Fixed-format class — the benefit credit money set against that charge, in
            USD to 2 decimal places, a positive amount rounded half to even at the cent; it is stored
            at exactly that precision and no unit symbol is passed.

    Returns:
        A confirmation line naming the membership, the benefit_code spent, the charge reference the
        credit was set against, the credit money taken off and the reference number of the new
        redemption entry; the presence of that redemption entry reference is what marks the call as
        completed.
    """
    rows = ctx.find("membership_holdings", membership_id=membership_id)
    if not rows:
        return f"Error: no Circle membership {membership_id}."
    holding = rows[0]
    rid = ctx.make_id("mbr_", membership_id, benefit_code, redemption_ref, credit_applied_usd)
    amount = round(float(credit_applied_usd), 2)
    ctx.create("membership_events", rid, membership_event_id=rid, membership_id=membership_id,
               customer_id=holding.get("customer_id"), event_type="membership_benefit_redeem",
               benefit_amount=amount, benefit_code=benefit_code, redemption_ref=redemption_ref,
               event_date=ctx.now()[:10], channel="phone")
    ctx.update("membership_holdings", membership_id,
               benefit_credit_balance=round(float(holding.get("benefit_credit_balance") or 0) - amount, 2))
    return (f"Benefit credit applied on membership {membership_id}: {benefit_code} of {amount} set "
            f"against charge {redemption_ref}, booked as redemption entry {rid}.")


@tool(owner="agent", rw="write")
def book_purchase_points_235cc6ac(ctx: ToolContext, membership_id: str, points_earned: int,
                                  qualifying_spend_usd: float, accrual_basis: str,
                                  source_order_id: str) -> str:
    """Book reward points earned on one earning occasion onto a Circle membership.

    One call lands an earning entry on the membership named: the ledger gains a row carrying the
    points earned, the spend they were earned on, which earning occasion produced them, the purchase
    they belong to and the tier the membership stands at, and the reward point balance shown on the
    membership goes up by those points. The member sees the points on the membership and can spend
    them from that balance. The receipt naming the new earning entry is what shows the call went
    through.

    Args:
        membership_id: Id class — the reference number of the Circle membership the points are earned
            on, read from the membership record returned when the membership is looked up.
        points_earned: Fixed-format class — the reward points earned on this occasion, in whole
            points, signed, passed as a positive whole number of points with no decimal part and no
            thousands separator; it is stored as an integer count of points at exactly that precision.
        qualifying_spend_usd: Fixed-format class — the spend those points were earned on, in USD to 2
            decimal places, a positive amount rounded half to even at the cent, with no unit symbol.
        accrual_basis: Enum class — which earning occasion produced these points, exactly one of:
            store_purchase, merchandise bought at a store counter;
            online_purchase, merchandise bought through the web or mobile storefront;
            protection_plan_purchase, a ShieldCare protection plan bought by the member;
            service_visit, a TechWorks visit or bench session the member paid for;
            trade_in_bonus, points that go with a Renew trade-in;
            promotional_event, a promotion run for members over a named period;
            goodwill_adjustment, points put on or taken off the balance to put something right.
        source_order_id: Id class — the reference number of the purchase, plan or work order the
            points were earned on, read from that order record before the call.

    Returns:
        A confirmation line naming the membership, the points_earned booked, the
        qualifying_spend_usd they were earned on, the accrual_basis recorded, the source_order_id they
        belong to and the reference number of the new earning entry; the presence of that earning
        entry reference is what marks the call as completed.
    """
    rows = ctx.find("membership_holdings", membership_id=membership_id)
    if not rows:
        return f"Error: no Circle membership {membership_id}."
    holding = rows[0]
    rid = ctx.make_id("mpa_", membership_id, points_earned, qualifying_spend_usd, accrual_basis, source_order_id)
    pts = int(points_earned)
    ctx.create("membership_events", rid, membership_event_id=rid, membership_id=membership_id,
               customer_id=holding.get("customer_id"), event_type="membership_points_accrue",
               points_delta=pts, qualifying_spend_usd=round(float(qualifying_spend_usd), 2),
               accrual_basis=accrual_basis, source_order_id=source_order_id,
               event_date=ctx.now()[:10], channel="phone", tier_at_event=holding.get("variant_name"))
    ctx.update("membership_holdings", membership_id,
               points_balance=int(holding.get("points_balance") or 0) + pts)
    return (f"Reward points booked on membership {membership_id}: {pts} points on qualifying spend of "
            f"{round(float(qualifying_spend_usd), 2)} as {accrual_basis} against purchase {source_order_id}, "
            f"booked as earning entry {rid}.")


@tool(owner="agent", rw="write")
def sweep_expired_points_bcca39ef(ctx: ToolContext, membership_id: str, points_swept: int,
                                  expiry_cycle_year: str) -> str:
    """Sweep points that have reached the end of their life off a Circle membership.

    One call lands one forfeiture entry for the sweep year named: the ledger gains a row carrying the
    points taken off and the sweep year they belong to, and the reward point balance shown on the
    membership drops by those points. The member sees the forfeiture as its own entry, told apart from
    a redemption, and a lower point balance. The receipt naming the new forfeiture entry is what shows
    the call went through.

    Args:
        membership_id: Id class — the reference number of the Circle membership the points are swept
            from, read from the membership record returned when the membership is looked up.
        points_swept: Fixed-format class — the points taken off the balance, in whole points, signed,
            passed as a positive whole number of points with no decimal part and no thousands
            separator; it is stored as an integer count of points at exactly that precision and the
            entry itself carries it as a reduction.
        expiry_cycle_year: Fixed-format class — the sweep year this forfeiture belongs to, written as
            the four-digit calendar year YYYY, with no month or day part and no other punctuation.

    Returns:
        A confirmation line naming the membership, the points_swept taken off, the expiry_cycle_year
        the forfeiture belongs to and the reference number of the new forfeiture entry; the presence
        of that forfeiture entry reference is what marks the call as completed.
    """
    rows = ctx.find("membership_holdings", membership_id=membership_id)
    if not rows:
        return f"Error: no Circle membership {membership_id}."
    holding = rows[0]
    rid = ctx.make_id("mpx_", membership_id, points_swept, expiry_cycle_year)
    pts = int(points_swept)
    ctx.create("membership_events", rid, membership_event_id=rid, membership_id=membership_id,
               customer_id=holding.get("customer_id"), event_type="membership_points_expire",
               points_delta=-pts, expiry_cycle_year=expiry_cycle_year,
               event_date=ctx.now()[:10], channel="phone")
    ctx.update("membership_holdings", membership_id,
               points_balance=int(holding.get("points_balance") or 0) - pts)
    return (f"Points swept off membership {membership_id}: {pts} points forfeited for sweep year "
            f"{expiry_cycle_year}, booked as forfeiture entry {rid}.")


@tool(owner="user", rw="write")
def redeem_reward_points_8621cafe(ctx: ToolContext, membership_id: str, points_redeemed: int,
                                  redemption_kind: str, redemption_ref: str) -> str:
    """Spend, as the member, reward points standing on your own Circle membership.

    The member spends these points themselves: one call lands a redemption entry on the membership,
    the ledger gains a row carrying the points spent, the form the redemption took and the reference
    it is being spent against, and the reward point balance shown on the membership drops by those
    points. The member sees the points gone from the balance and the redemption standing against the
    reference given. The receipt naming the new redemption entry is what shows the call went through.

    Args:
        membership_id: Id class — the reference number of the Circle membership whose points are being
            spent, read from the membership record returned when the membership is looked up.
        points_redeemed: Fixed-format class — the points being spent, in whole points, signed, passed
            as a positive whole number of points with no decimal part and no thousands separator; it
            is stored as an integer count of points at exactly that precision and the entry itself
            carries it as a reduction.
        redemption_kind: Enum class — the form this redemption takes, exactly one of:
            reward_certificate, the points come back as a certificate the member spends later;
            instant_checkout_discount, the points come straight off a purchase at the till or off a charge
            already standing on the account, there and then;
            charitable_donation, the points go to the retailer's recycling fund;
            points_transfer, the points move to another profile on a tier that allows transfers.
        redemption_ref: Verbatim class — the reference the member reads out for what the points are
            being spent against, copied character for character as they say it, keeping their wording,
            digits, letter case and punctuation, with nothing translated, tidied, shortened, added or
            dropped (verbatim).

    Returns:
        A confirmation line naming the membership, the points_redeemed spent, the redemption_kind it
        was taken as, the reference it was spent against and the reference number of the new
        redemption entry; the presence of that redemption entry reference is what marks the call as
        completed.
    """
    rows = ctx.find("membership_holdings", membership_id=membership_id)
    if not rows:
        return f"Error: no Circle membership {membership_id}."
    holding = rows[0]
    rid = ctx.make_id("mpr_", membership_id, points_redeemed, redemption_kind, redemption_ref)
    pts = int(points_redeemed)
    ctx.create("membership_events", rid, membership_event_id=rid, membership_id=membership_id,
               customer_id=holding.get("customer_id"), event_type="membership_points_redeem",
               points_delta=-pts, redemption_kind=redemption_kind, redemption_ref=redemption_ref,
               event_date=ctx.now()[:10], channel="phone")
    ctx.update("membership_holdings", membership_id,
               points_balance=int(holding.get("points_balance") or 0) - pts)
    return (f"Reward points redeemed on membership {membership_id}: {pts} points taken as "
            f"{redemption_kind} against {redemption_ref}, booked as redemption entry {rid}.")

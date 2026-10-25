"""Hidden task tools of the membership_fees_and_benefits difficulty (env_0080, Northgate Stores)."""

from decimal import Decimal, ROUND_HALF_UP

from erlbench import ToolContext, tool


class _Fmt:
    """Format helpers shared by the tools of this file (values only, never writes)."""

    @staticmethod
    def money(value):
        """Return the value as a two-decimal amount (half up), or None when it is not a number."""
        try:
            d = Decimal(str(value))
        except Exception:
            return None
        return float(d.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP))

    @staticmethod
    def has_two_decimals(value):
        try:
            d = Decimal(str(value))
        except Exception:
            return False
        return d == d.quantize(Decimal("0.01"))

    @staticmethod
    def is_date(value):
        s = str(value or "")
        if len(s) != 10 or s[4] != "-" or s[7] != "-":
            return False
        y, m, d = s[:4], s[5:7], s[8:]
        if not (y.isdigit() and m.isdigit() and d.isdigit()):
            return False
        return 1 <= int(m) <= 12 and 1 <= int(d) <= 31


class _Scope:
    """Record tests naming the one record each schedule prices (reads only, never writes)."""

    @staticmethod
    def latest(rows, date_field):
        best = None
        for r in rows:
            if best is None or str(r.get(date_field) or "") > str(best.get(date_field) or ""):
                best = r
        return best

    @staticmethod
    def priced_line(ctx, customer_id):
        order = _Scope.latest(ctx.find("order_holdings", customer_id=customer_id, status="fulfilled"), "fulfilled_date")
        if order is None:
            return None, None
        lines = ctx.find("order_events", order_id=order.get("order_id"), event_type="order_post_line")
        return order.get("order_id"), (lines[0].get("order_event_id") if lines else None)

    @staticmethod
    def priced_return(ctx, customer_id):
        row = _Scope.latest(ctx.find("order_events", customer_id=customer_id, event_type="order_return_line"), "event_date")
        return row.get("order_event_id") if row else None

    @staticmethod
    def priced_refund(ctx, customer_id):
        dmg = _Scope.latest(ctx.find("order_events", customer_id=customer_id, event_type="order_refund_charge",
                                     refund_reason="item_damaged_no_return"), "event_date")
        miss = _Scope.latest(ctx.find("order_events", customer_id=customer_id, event_type="order_refund_charge",
                                      refund_reason="item_not_received"), "event_date")
        if dmg is None and miss is None:
            return None
        if miss is None or (dmg is not None and str(dmg.get("event_date")) >= str(miss.get("event_date"))):
            return dmg.get("order_event_id")
        return miss.get("order_event_id")

    @staticmethod
    def earning_of(ctx, membership_id, earning_event_id, line_id):
        rows = ctx.find("membership_events", membership_event_id=earning_event_id, membership_id=membership_id,
                        event_type="membership_cash_earn", source_order_event_id=line_id)
        return bool(rows)


@tool(owner="agent", rw="write")
def post_member_cash_earning_0c0d8435(ctx: ToolContext, membership_id: str, order_id: str, line_event_id: str,
                                      earn_date: str, basis_amount_usd: float, amount_usd: float) -> str:
    """Post the Northgate Cash a member earned on one fulfilled Northgate order line. One call books one
    earning entry on the membership's Northgate Cash ledger, linked to the order and to the order line that
    earned it, and raises the membership's Northgate Cash balance by the amount posted. The member sees the
    new earning in their Northgate Cash history and the higher balance. The call succeeds when the receipt
    reports status "posted".

    Args:
        membership_id: Id class — the membership identifier of the membership record that receives the Northgate Cash, as returned by the
            membership lookup for the member.
        order_id: Id class — the order identifier of the Northgate order the earning line belongs to, as returned by the order lookup.
        line_event_id: Id class — the order line identifier (the line's own record identifier) that earned the
            Northgate Cash, as returned by the order ledger lookup.
        earn_date: Fixed-format class — the business date the earning posts on, written YYYY-MM-DD (calendar
            date, no time part, no time zone); never empty.
        basis_amount_usd: Fixed-format class — the line amount the earning percentage was applied to, in US
            dollars as a positive number with 2 decimal places (cents); values with more decimals are refused, never rounded by the tool.
        amount_usd: Fixed-format class — the Northgate Cash posted, in US dollars as a positive number with 2
            decimal places (cents); values with more decimals are refused, never rounded by the tool.

    Returns:
        A text receipt "Northgate Cash earning <earning_ref> posted: membership <membership_id>, order
        <order_id>, line <line_event_id>, earned on <earn_date>, basis <basis_amount_usd> USD, amount
        <amount_usd> USD, new balance <balance> USD, status posted." where earning_ref is the new earning
        entry's reference, the amounts are two-decimal US dollars and balance is the membership's Northgate
        Cash balance after the posting (may be negative). A text beginning "Error:" means nothing was posted
        because an argument broke the format above, the membership's tier is outside this posting, the line
        is not the earliest-recorded line of the member's Northgate order with the latest fulfilled date
        among their orders in fulfilled status, or the membership reference is unknown.
    """
    if not _Fmt.is_date(earn_date):
        return "Error: earn_date must be written YYYY-MM-DD."
    for name, val in (("basis_amount_usd", basis_amount_usd), ("amount_usd", amount_usd)):
        if not _Fmt.has_two_decimals(val) or _Fmt.money(val) is None or _Fmt.money(val) <= 0:
            return f"Error: {name} must be a positive US dollar amount with at most two decimals."
    rows = ctx.find("membership_holdings", membership_id=membership_id)
    if not rows:
        return f"Error: membership {membership_id} is unknown."
    m = rows[0]
    if m.get("variant_name") == "Northgate+ Business":
        return "Error: this posting applies only to a Northgate Rewards or consumer Northgate+ membership."
    if _Scope.priced_line(ctx, m.get("customer_id")) != (order_id, line_event_id):
        return ("Error: the line is not the earliest-recorded line of the member's Northgate order with the latest "
                "fulfilled date among the member's orders in fulfilled status.")
    basis = _Fmt.money(basis_amount_usd)
    amount = _Fmt.money(amount_usd)
    rid = ctx.make_id("mev_", membership_id, order_id, line_event_id, earn_date, basis_amount_usd, amount_usd)
    ctx.create("membership_events", rid, membership_event_id=rid, membership_id=membership_id,
               customer_id=m.get("customer_id"), event_type="membership_cash_earn", event_date=earn_date,
               amount_usd=amount, fee_type="not_applicable", billing_period_start="",
               tier_at_event=m.get("variant_name"), payment_method_type="none", card_account_id="",
               attempt_number=0, original_event_id="", refund_basis="not_applicable",
               benefit_type="not_applicable", order_id=order_id, source_order_event_id=line_event_id,
               basis_amount_usd=basis)
    balance = _Fmt.money(float(m.get("rewards_cash_balance") or 0) + amount)
    ctx.update("membership_holdings", membership_id, rewards_cash_balance=balance)
    return (f"Northgate Cash earning {rid} posted: membership {membership_id}, order {order_id}, line "
            f"{line_event_id}, earned on {earn_date}, basis {basis:.2f} USD, amount {amount:.2f} USD, "
            f"new balance {balance:.2f} USD, status posted.")


@tool(owner="agent", rw="write")
def reverse_member_return_cash_50b9758d(ctx: ToolContext, membership_id: str, earning_event_id: str,
                                        source_order_event_id: str, order_id: str, return_date: str,
                                        refunded_merchandise_usd: float, amount_usd: float) -> str:
    """Reverse the Northgate Cash earned on an order line that the member returned for a refund. One call
    books one reversal entry on the membership's Northgate Cash ledger, linked to the earning it reduces and
    to the order return record that caused it, and lowers the membership's Northgate Cash balance by the
    amount reversed (the balance may go below zero). The member sees the reversal in their Northgate Cash
    history and the lower balance. The call succeeds when the receipt reports status "reversed".

    Args:
        membership_id: Id class — the membership identifier of the membership record whose Northgate Cash is reduced, as returned by the
            membership lookup for the member.
        earning_event_id: Id class — the ledger entry identifier of the Northgate Cash earning entry being reduced, as returned by the
            membership ledger lookup.
        source_order_event_id: Id class — the order ledger identifier of the return record that caused the reversal, as returned by the order
            ledger lookup.
        order_id: Id class — the order identifier of the Northgate order the returned line belongs to, as returned by the order lookup.
        return_date: Fixed-format class — the date the return was processed, written YYYY-MM-DD (calendar
            date, no time part, no time zone); never empty.
        refunded_merchandise_usd: Fixed-format class — the merchandise amount the return refunded, in US
            dollars as a positive number with 2 decimal places (cents); values with more decimals are refused, never rounded by the tool.
        amount_usd: Fixed-format class — the Northgate Cash reversed, in US dollars as a positive number with 2
            decimal places (cents); values with more decimals are refused, never rounded by the tool.

    Returns:
        A text receipt "Northgate Cash reversal <reversal_ref> booked: membership <membership_id>, earning
        <earning_event_id>, return <source_order_event_id>, order <order_id>, dated <return_date>, refunded
        merchandise <refunded_merchandise_usd> USD, amount <amount_usd> USD, new balance <balance> USD, status
        reversed." where reversal_ref is the new reversal entry's reference, the amounts are two-decimal US
        dollars and balance is the membership's Northgate Cash balance after the reversal (may be negative). A
        text beginning "Error:" means nothing was booked because an argument broke the format above, the membership's tier is outside this reversal, the
        record is not the member's most recent return on their Northgate orders, the earning given is not
        the earning of the returned line, or the membership reference is unknown.
    """
    if not _Fmt.is_date(return_date):
        return "Error: return_date must be written YYYY-MM-DD."
    for name, val in (("refunded_merchandise_usd", refunded_merchandise_usd), ("amount_usd", amount_usd)):
        if not _Fmt.has_two_decimals(val) or _Fmt.money(val) is None or _Fmt.money(val) <= 0:
            return f"Error: {name} must be a positive US dollar amount with at most two decimals."
    rows = ctx.find("membership_holdings", membership_id=membership_id)
    if not rows:
        return f"Error: membership {membership_id} is unknown."
    m = rows[0]
    if m.get("variant_name") == "Northgate+ Business":
        return "Error: this posting applies only to a Northgate Rewards or consumer Northgate+ membership."
    if _Scope.priced_return(ctx, m.get("customer_id")) != source_order_event_id:
        return "Error: the record is not the member's most recent return on their Northgate orders."
    src = ctx.find("order_events", order_event_id=source_order_event_id)
    if not src or not _Scope.earning_of(ctx, membership_id, earning_event_id, src[0].get("original_event_id")):
        return "Error: the earning given is not the Northgate Cash earning of the line that record refers to."
    refunded = _Fmt.money(refunded_merchandise_usd)
    amount = _Fmt.money(amount_usd)
    rid = ctx.make_id("mev_", membership_id, earning_event_id, source_order_event_id, order_id, return_date,
                      refunded_merchandise_usd, amount_usd)
    ctx.create("membership_events", rid, membership_event_id=rid, membership_id=membership_id,
               customer_id=m.get("customer_id"), event_type="membership_cash_reverse", event_date=return_date,
               amount_usd=amount, fee_type="not_applicable", billing_period_start="",
               tier_at_event=m.get("variant_name"), payment_method_type="none", card_account_id="",
               attempt_number=0, original_event_id=earning_event_id, refund_basis="not_applicable",
               benefit_type="not_applicable", order_id=order_id, source_order_event_id=source_order_event_id,
               basis_amount_usd=refunded)
    balance = _Fmt.money(float(m.get("rewards_cash_balance") or 0) - amount)
    ctx.update("membership_holdings", membership_id, rewards_cash_balance=balance)
    return (f"Northgate Cash reversal {rid} booked: membership {membership_id}, earning {earning_event_id}, "
            f"return {source_order_event_id}, order {order_id}, dated {return_date}, refunded merchandise "
            f"{refunded:.2f} USD, amount {amount:.2f} USD, new balance {balance:.2f} USD, status reversed.")


@tool(owner="user", rw="write")
def confirm_annual_membership_cancellation_fe7f482c(ctx: ToolContext, membership_id: str, original_event_id: str,
                                                    refund_basis: str, refund_amount_usd: float) -> str:
    """The member confirms, in person, the immediate cancellation of their own annual Northgate+ membership
    together with the refund of its annual fee. One call records the cancellation request as confirmed and closes the
    membership today (status canceled, auto-renew off, cancellation date today). When the refund is above 0.00 the
    call also books one refund entry against the annual fee charge, credited to the external debit or credit card
    that fee was charged to; when the refund is 0.00 it books no refund entry. The member sees the membership
    closed and, when a refund is booked, the refund on that card. The call succeeds when the receipt reports
    status "canceled".

    Args:
        membership_id: Id class — the membership identifier of the member's own membership record being cancelled, as returned by the
            membership lookup and read to the member by the agent.
        original_event_id: Id class — the ledger entry identifier of the annual fee charge the refund is booked against, as returned by the
            membership ledger lookup and read to the member by the agent.
        refund_basis: Enum class — the basis the refund is booked under; one of: "full_within_window" when the
            cancellation falls inside the annual fee's full refund window; "prorated_unused_months" when the
            cancellation falls after that window and the refund covers the unused months of the term;
            "billing_error" when the fee being refunded was charged in error (a second charge for the same
            billing period, or a charge for a period starting on or after a confirmed cancellation);
            "not_applicable" marks ledger entries that are not fee refunds and is refused on this refund.
        refund_amount_usd: Fixed-format class — the refund the member confirms, in US dollars with 2 decimal places
            (cents), 0.00 or positive; values with more decimals or below 0.00 are refused, never rounded by the
            tool. With 0.00 the cancellation is recorded and no refund entry is booked.

    Returns:
        One of two text receipts. When the refund is above 0.00: "Membership <membership_id> canceled on
        <cancel_date>: request <request_ref> confirmed, refund <refund_ref> of <refund_amount_usd> USD against fee
        <original_event_id> with basis <refund_basis> credited to the external card, status canceled." When the
        refund is 0.00: "Membership <membership_id> canceled on <cancel_date>: request <request_ref> confirmed,
        refund none of 0.00 USD, no refund entry booked against fee <original_event_id>, status canceled." Here
        cancel_date is today's date (YYYY-MM-DD), request_ref is the new request reference, refund_ref is the new
        refund entry reference and the amount is in two-decimal US dollars. A text beginning "Error:" means
        nothing was changed because an argument broke the format above or the membership reference is unknown.
    """
    if refund_basis not in ("full_within_window", "prorated_unused_months", "billing_error"):  # not_applicable refused
        return "Error: refund_basis must be full_within_window, prorated_unused_months or billing_error."
    if (not _Fmt.has_two_decimals(refund_amount_usd) or _Fmt.money(refund_amount_usd) is None
            or _Fmt.money(refund_amount_usd) < 0):
        return "Error: refund_amount_usd must be 0.00 or a positive US dollar amount with at most two decimals."
    rows = ctx.find("membership_holdings", membership_id=membership_id)
    if not rows:
        return f"Error: membership {membership_id} is unknown."
    m = rows[0]
    today = ctx.now()[:10]
    amount = _Fmt.money(refund_amount_usd)
    req = ctx.make_id("mrq_", membership_id, original_event_id, refund_basis, refund_amount_usd)
    ctx.create("membership_requests", req, membership_request_id=req, customer_id=m.get("customer_id"),
               membership_id=membership_id, request_type="cancel_immediately", request_status="confirmed",
               created_at=ctx.now())
    ctx.update("membership_holdings", membership_id, status="canceled", canceled_date=today, auto_renew=False)
    ref = "none"
    if amount > 0:
        ref = ctx.make_id("mev_", membership_id, original_event_id, refund_basis, refund_amount_usd, "refund")
        ctx.create("membership_events", ref, membership_event_id=ref, membership_id=membership_id,
                   customer_id=m.get("customer_id"), event_type="membership_fee_refund", event_date=today,
                   amount_usd=amount, fee_type="not_applicable", billing_period_start="",
                   tier_at_event=m.get("variant_name"), payment_method_type="external_card", card_account_id="",
                   attempt_number=0, original_event_id=original_event_id, refund_basis=refund_basis,
                   benefit_type="not_applicable", order_id="", source_order_event_id="", basis_amount_usd=0.0)
    if amount <= 0:
        return (f"Membership {membership_id} canceled on {today}: request {req} confirmed, refund none of 0.00 USD, "
                f"no refund entry booked against fee {original_event_id}, status canceled.")
    return (f"Membership {membership_id} canceled on {today}: request {req} confirmed, refund {ref} of "
            f"{amount:.2f} USD against fee {original_event_id} with basis {refund_basis} credited to the "
            f"external card, status canceled.")


@tool(owner="agent", rw="write")
def post_business_cash_earning_affdfb03(ctx: ToolContext, membership_id: str, order_id: str, line_event_id: str,
                                      earn_date: str, basis_amount_usd: float, amount_usd: float) -> str:
    """Post the Northgate Cash a Northgate+ Business member earned on one fulfilled Northgate order line. One call books one
    earning entry on the membership's Northgate Cash ledger, linked to the order and to the order line that
    earned it, and raises the membership's Northgate Cash balance by the amount posted. The business sees the
    new earning in their Northgate Cash history and the higher balance. The call succeeds when the receipt
    reports status "posted".

    Args:
        membership_id: Id class — the membership identifier of the membership record that receives the Northgate Cash, as returned by the
            membership lookup for the member.
        order_id: Id class — the order identifier of the Northgate order the earning line belongs to, as returned by the order lookup.
        line_event_id: Id class — the order line identifier (the line's own record identifier) that earned the
            Northgate Cash, as returned by the order ledger lookup.
        earn_date: Fixed-format class — the business date the earning posts on, written YYYY-MM-DD (calendar
            date, no time part, no time zone); never empty.
        basis_amount_usd: Fixed-format class — the line amount the earning percentage was applied to, in US
            dollars as a positive number with 2 decimal places (cents); values with more decimals are refused, never rounded by the tool.
        amount_usd: Fixed-format class — the Northgate Cash posted, in US dollars as a positive number with 2
            decimal places (cents); values with more decimals are refused, never rounded by the tool.

    Returns:
        A text receipt "Northgate Cash earning <earning_ref> posted: membership <membership_id>, order
        <order_id>, line <line_event_id>, earned on <earn_date>, basis <basis_amount_usd> USD, amount
        <amount_usd> USD, new balance <balance> USD, status posted." where earning_ref is the new earning
        entry's reference, the amounts are two-decimal US dollars and balance is the membership's Northgate
        Cash balance after the posting (may be negative). A text beginning "Error:" means nothing was posted
        because an argument broke the format above, the membership's tier is outside this posting, the line
        is not the earliest-recorded line of the member's Northgate order with the latest fulfilled date
        among their orders in fulfilled status, or the membership reference is unknown.
    """
    if not _Fmt.is_date(earn_date):
        return "Error: earn_date must be written YYYY-MM-DD."
    for name, val in (("basis_amount_usd", basis_amount_usd), ("amount_usd", amount_usd)):
        if not _Fmt.has_two_decimals(val) or _Fmt.money(val) is None or _Fmt.money(val) <= 0:
            return f"Error: {name} must be a positive US dollar amount with at most two decimals."
    rows = ctx.find("membership_holdings", membership_id=membership_id)
    if not rows:
        return f"Error: membership {membership_id} is unknown."
    m = rows[0]
    if m.get("variant_name") != "Northgate+ Business":
        return "Error: this posting applies only to a Northgate+ Business membership."
    if _Scope.priced_line(ctx, m.get("customer_id")) != (order_id, line_event_id):
        return ("Error: the line is not the earliest-recorded line of the member's Northgate order with the latest "
                "fulfilled date among the member's orders in fulfilled status.")
    basis = _Fmt.money(basis_amount_usd)
    amount = _Fmt.money(amount_usd)
    rid = ctx.make_id("mbe_", membership_id, order_id, line_event_id, earn_date, basis_amount_usd, amount_usd)
    ctx.create("membership_events", rid, membership_event_id=rid, membership_id=membership_id,
               customer_id=m.get("customer_id"), event_type="membership_cash_earn", event_date=earn_date,
               amount_usd=amount, fee_type="not_applicable", billing_period_start="",
               tier_at_event=m.get("variant_name"), payment_method_type="none", card_account_id="",
               attempt_number=0, original_event_id="", refund_basis="not_applicable",
               benefit_type="not_applicable", order_id=order_id, source_order_event_id=line_event_id,
               basis_amount_usd=basis)
    balance = _Fmt.money(float(m.get("rewards_cash_balance") or 0) + amount)
    ctx.update("membership_holdings", membership_id, rewards_cash_balance=balance)
    return (f"Northgate Cash earning {rid} posted: membership {membership_id}, order {order_id}, line "
            f"{line_event_id}, earned on {earn_date}, basis {basis:.2f} USD, amount {amount:.2f} USD, "
            f"new balance {balance:.2f} USD, status posted.")


@tool(owner="agent", rw="write")
def reverse_business_return_cash_4d4108b5(ctx: ToolContext, membership_id: str, earning_event_id: str,
                                        source_order_event_id: str, order_id: str, return_date: str,
                                        refunded_merchandise_usd: float, amount_usd: float) -> str:
    """Reverse the Northgate Cash a Northgate+ Business member earned on an order line the business returned for a refund. One call
    books one reversal entry on the membership's Northgate Cash ledger, linked to the earning it reduces and
    to the order return record that caused it, and lowers the membership's Northgate Cash balance by the
    amount reversed (the balance may go below zero). The member sees the reversal in their Northgate Cash
    history and the lower balance. The call succeeds when the receipt reports status "reversed".

    Args:
        membership_id: Id class — the membership identifier of the membership record whose Northgate Cash is reduced, as returned by the
            membership lookup for the member.
        earning_event_id: Id class — the ledger entry identifier of the Northgate Cash earning entry being reduced, as returned by the
            membership ledger lookup.
        source_order_event_id: Id class — the order ledger identifier of the return record that caused the reversal, as returned by the order
            ledger lookup.
        order_id: Id class — the order identifier of the Northgate order the returned line belongs to, as returned by the order lookup.
        return_date: Fixed-format class — the date the return was processed, written YYYY-MM-DD (calendar
            date, no time part, no time zone); never empty.
        refunded_merchandise_usd: Fixed-format class — the merchandise amount the return refunded, in US
            dollars as a positive number with 2 decimal places (cents); values with more decimals are refused, never rounded by the tool.
        amount_usd: Fixed-format class — the Northgate Cash reversed, in US dollars as a positive number with 2
            decimal places (cents); values with more decimals are refused, never rounded by the tool.

    Returns:
        A text receipt "Northgate Cash reversal <reversal_ref> booked: membership <membership_id>, earning
        <earning_event_id>, return <source_order_event_id>, order <order_id>, dated <return_date>, refunded
        merchandise <refunded_merchandise_usd> USD, amount <amount_usd> USD, new balance <balance> USD, status
        reversed." where reversal_ref is the new reversal entry's reference, the amounts are two-decimal US
        dollars and balance is the membership's Northgate Cash balance after the reversal (may be negative). A
        text beginning "Error:" means nothing was booked because an argument broke the format above, the membership's tier is outside this reversal, the
        record is not the member's most recent return on their Northgate orders, the earning given is not
        the earning of the returned line, or the membership reference is unknown.
    """
    if not _Fmt.is_date(return_date):
        return "Error: return_date must be written YYYY-MM-DD."
    for name, val in (("refunded_merchandise_usd", refunded_merchandise_usd), ("amount_usd", amount_usd)):
        if not _Fmt.has_two_decimals(val) or _Fmt.money(val) is None or _Fmt.money(val) <= 0:
            return f"Error: {name} must be a positive US dollar amount with at most two decimals."
    rows = ctx.find("membership_holdings", membership_id=membership_id)
    if not rows:
        return f"Error: membership {membership_id} is unknown."
    m = rows[0]
    if m.get("variant_name") != "Northgate+ Business":
        return "Error: this posting applies only to a Northgate+ Business membership."
    if _Scope.priced_return(ctx, m.get("customer_id")) != source_order_event_id:
        return "Error: the record is not the member's most recent return on their Northgate orders."
    src = ctx.find("order_events", order_event_id=source_order_event_id)
    if not src or not _Scope.earning_of(ctx, membership_id, earning_event_id, src[0].get("original_event_id")):
        return "Error: the earning given is not the Northgate Cash earning of the line that record refers to."
    refunded = _Fmt.money(refunded_merchandise_usd)
    amount = _Fmt.money(amount_usd)
    rid = ctx.make_id("mbr_", membership_id, earning_event_id, source_order_event_id, order_id, return_date,
                      refunded_merchandise_usd, amount_usd)
    ctx.create("membership_events", rid, membership_event_id=rid, membership_id=membership_id,
               customer_id=m.get("customer_id"), event_type="membership_cash_reverse", event_date=return_date,
               amount_usd=amount, fee_type="not_applicable", billing_period_start="",
               tier_at_event=m.get("variant_name"), payment_method_type="none", card_account_id="",
               attempt_number=0, original_event_id=earning_event_id, refund_basis="not_applicable",
               benefit_type="not_applicable", order_id=order_id, source_order_event_id=source_order_event_id,
               basis_amount_usd=refunded)
    balance = _Fmt.money(float(m.get("rewards_cash_balance") or 0) - amount)
    ctx.update("membership_holdings", membership_id, rewards_cash_balance=balance)
    return (f"Northgate Cash reversal {rid} booked: membership {membership_id}, earning {earning_event_id}, "
            f"return {source_order_event_id}, order {order_id}, dated {return_date}, refunded merchandise "
            f"{refunded:.2f} USD, amount {amount:.2f} USD, new balance {balance:.2f} USD, status reversed.")


@tool(owner="agent", rw="write")
def reverse_unreturned_refund_cash_522719bc(ctx: ToolContext, membership_id: str, earning_event_id: str,
                                        source_order_event_id: str, order_id: str, refund_date: str,
                                        refunded_merchandise_usd: float, amount_usd: float) -> str:
    """Reverse the Northgate Cash earned on an order line that was refunded without a return because the item
    was damaged on arrival or never arrived. One call
    books one reversal entry on the membership's Northgate Cash ledger, linked to the earning it reduces and
    to the order refund record that caused it, and lowers the membership's Northgate Cash balance by the
    amount reversed (the balance may go below zero). The member sees the reversal in their Northgate Cash
    history and the lower balance. The call succeeds when the receipt reports status "reversed".

    Args:
        membership_id: Id class — the membership identifier of the membership record whose Northgate Cash is reduced, as returned by the
            membership lookup for the member.
        earning_event_id: Id class — the ledger entry identifier of the Northgate Cash earning entry being reduced, as returned by the
            membership ledger lookup.
        source_order_event_id: Id class — the order ledger identifier of the refund-without-return record that caused the reversal, as returned by the order
            ledger lookup.
        order_id: Id class — the order identifier of the Northgate order the refunded line belongs to, as returned by the order lookup.
        refund_date: Fixed-format class — the date the refund was issued, written YYYY-MM-DD (calendar
            date, no time part, no time zone); never empty.
        refunded_merchandise_usd: Fixed-format class — the merchandise amount the refund repaid, in US
            dollars as a positive number with 2 decimal places (cents); values with more decimals are refused, never rounded by the tool.
        amount_usd: Fixed-format class — the Northgate Cash reversed, in US dollars as a positive number with 2
            decimal places (cents); values with more decimals are refused, never rounded by the tool.

    Returns:
        A text receipt "Northgate Cash refund reversal <reversal_ref> booked: membership <membership_id>, earning
        <earning_event_id>, refund <source_order_event_id>, order <order_id>, dated <refund_date>, refunded
        merchandise <refunded_merchandise_usd> USD, amount <amount_usd> USD, new balance <balance> USD, status
        reversed." where reversal_ref is the new reversal entry's reference, the amounts are two-decimal US
        dollars and balance is the membership's Northgate Cash balance after the reversal (may be negative). A
        text beginning "Error:" means nothing was booked because an argument broke the format above, the record is not the member's most recent
        damaged-on-arrival or never-received refund without a return on their Northgate orders, the earning
        given is not the earning of the refunded line, or the membership reference is unknown.
    """
    if not _Fmt.is_date(refund_date):
        return "Error: refund_date must be written YYYY-MM-DD."
    for name, val in (("refunded_merchandise_usd", refunded_merchandise_usd), ("amount_usd", amount_usd)):
        if not _Fmt.has_two_decimals(val) or _Fmt.money(val) is None or _Fmt.money(val) <= 0:
            return f"Error: {name} must be a positive US dollar amount with at most two decimals."
    rows = ctx.find("membership_holdings", membership_id=membership_id)
    if not rows:
        return f"Error: membership {membership_id} is unknown."
    m = rows[0]
    if _Scope.priced_refund(ctx, m.get("customer_id")) != source_order_event_id:
        return "Error: the record is not the member's most recent damaged-on-arrival or never-received refund without a return on their Northgate orders."
    src = ctx.find("order_events", order_event_id=source_order_event_id)
    if not src or not _Scope.earning_of(ctx, membership_id, earning_event_id, src[0].get("original_event_id")):
        return "Error: the earning given is not the Northgate Cash earning of the line that record refers to."
    refunded = _Fmt.money(refunded_merchandise_usd)
    amount = _Fmt.money(amount_usd)
    rid = ctx.make_id("mur_", membership_id, earning_event_id, source_order_event_id, order_id, refund_date,
                      refunded_merchandise_usd, amount_usd)
    ctx.create("membership_events", rid, membership_event_id=rid, membership_id=membership_id,
               customer_id=m.get("customer_id"), event_type="membership_cash_reverse", event_date=refund_date,
               amount_usd=amount, fee_type="not_applicable", billing_period_start="",
               tier_at_event=m.get("variant_name"), payment_method_type="none", card_account_id="",
               attempt_number=0, original_event_id=earning_event_id, refund_basis="not_applicable",
               benefit_type="not_applicable", order_id=order_id, source_order_event_id=source_order_event_id,
               basis_amount_usd=refunded)
    balance = _Fmt.money(float(m.get("rewards_cash_balance") or 0) - amount)
    ctx.update("membership_holdings", membership_id, rewards_cash_balance=balance)
    return (f"Northgate Cash refund reversal {rid} booked: membership {membership_id}, earning {earning_event_id}, "
            f"refund {source_order_event_id}, order {order_id}, dated {refund_date}, refunded merchandise "
            f"{refunded:.2f} USD, amount {amount:.2f} USD, new balance {balance:.2f} USD, status reversed.")


@tool(owner="user", rw="write")
def confirm_business_membership_closure_a0a2c96c(ctx: ToolContext, membership_id: str, original_event_id: str,
                                                    refund_basis: str, refund_amount_usd: float) -> str:
    """The business's administrator confirms, in person, the immediate closure of the business's own Northgate+ Business membership
    together with the refund of its annual fee. One call records the closure request as confirmed and closes the
    membership today (status canceled, auto-renew off, cancellation date today). When the refund is above 0.00 the
    call also books one refund entry against the annual fee charge, credited to the external debit or credit card
    that fee was charged to; when the refund is 0.00 it books no refund entry. The administrator sees the membership
    closed and, when a refund is booked, the refund on that card. The call succeeds when the receipt reports
    status "canceled".

    Args:
        membership_id: Id class — the membership identifier of the business's own membership record being closed, as returned by the
            membership lookup and read to the administrator by the agent.
        original_event_id: Id class — the ledger entry identifier of the annual fee charge the refund is booked against, as returned by the
            membership ledger lookup and read to the administrator by the agent.
        refund_basis: Enum class — the basis the refund is booked under; one of: "full_within_window" when the
            cancellation falls inside the annual fee's full refund window; "prorated_unused_months" when the
            cancellation falls after that window and the refund covers the unused months of the term;
            "billing_error" when the fee being refunded was charged in error (a second charge for the same
            billing period, or a charge for a period starting on or after a confirmed cancellation);
            "not_applicable" marks ledger entries that are not fee refunds and is refused on this refund.
        refund_amount_usd: Fixed-format class — the refund the administrator confirms, in US dollars with 2 decimal places
            (cents), 0.00 or positive; values with more decimals or below 0.00 are refused, never rounded by the
            tool. With 0.00 the cancellation is recorded and no refund entry is booked.

    Returns:
        One of two text receipts. When the refund is above 0.00: "Membership <membership_id> canceled on
        <cancel_date>: request <request_ref> confirmed, refund <refund_ref> of <refund_amount_usd> USD against fee
        <original_event_id> with basis <refund_basis> credited to the external card, status canceled." When the
        refund is 0.00: "Membership <membership_id> canceled on <cancel_date>: request <request_ref> confirmed,
        refund none of 0.00 USD, no refund entry booked against fee <original_event_id>, status canceled." Here
        cancel_date is today's date (YYYY-MM-DD), request_ref is the new request reference, refund_ref is the new
        refund entry reference and the amount is in two-decimal US dollars. A text beginning "Error:" means
        nothing was changed because an argument broke the format above or the membership reference is unknown.
    """
    if refund_basis not in ("full_within_window", "prorated_unused_months", "billing_error"):  # not_applicable refused
        return "Error: refund_basis must be full_within_window, prorated_unused_months or billing_error."
    if (not _Fmt.has_two_decimals(refund_amount_usd) or _Fmt.money(refund_amount_usd) is None
            or _Fmt.money(refund_amount_usd) < 0):
        return "Error: refund_amount_usd must be 0.00 or a positive US dollar amount with at most two decimals."
    rows = ctx.find("membership_holdings", membership_id=membership_id)
    if not rows:
        return f"Error: membership {membership_id} is unknown."
    m = rows[0]
    today = ctx.now()[:10]
    amount = _Fmt.money(refund_amount_usd)
    req = ctx.make_id("mbq_", membership_id, original_event_id, refund_basis, refund_amount_usd)
    ctx.create("membership_requests", req, membership_request_id=req, customer_id=m.get("customer_id"),
               membership_id=membership_id, request_type="cancel_immediately", request_status="confirmed",
               created_at=ctx.now())
    ctx.update("membership_holdings", membership_id, status="canceled", canceled_date=today, auto_renew=False)
    ref = "none"
    if amount > 0:
        ref = ctx.make_id("mbf_", membership_id, original_event_id, refund_basis, refund_amount_usd, "refund")
        ctx.create("membership_events", ref, membership_event_id=ref, membership_id=membership_id,
                   customer_id=m.get("customer_id"), event_type="membership_fee_refund", event_date=today,
                   amount_usd=amount, fee_type="not_applicable", billing_period_start="",
                   tier_at_event=m.get("variant_name"), payment_method_type="external_card", card_account_id="",
                   attempt_number=0, original_event_id=original_event_id, refund_basis=refund_basis,
                   benefit_type="not_applicable", order_id="", source_order_event_id="", basis_amount_usd=0.0)
    if amount <= 0:
        return (f"Membership {membership_id} canceled on {today}: request {req} confirmed, refund none of 0.00 USD, "
                f"no refund entry booked against fee {original_event_id}, status canceled.")
    return (f"Membership {membership_id} canceled on {today}: request {req} confirmed, refund {ref} of "
            f"{amount:.2f} USD against fee {original_event_id} with basis {refund_basis} credited to the "
            f"external card, status canceled.")

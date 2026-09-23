"""Hidden task tools for the micro_market_desk difficulty of
env_0013_workplace_dining_and_catering_provider.

Every function here performs one atomic posting against an unattended micro market
agreement or its settlement ledger. None of them aggregates history, derives an amount, or
judges whether the posting is due: the agent reads the agreement, its ledger and its service
request log, works the figure out from the published rules, and passes the finished number in.
"""

from erlbench import ToolContext, tool

_LEDGER = "market_ledger"
_AGREEMENTS = "market_agreements"


@tool(owner="agent", rw="write")
def post_kiosk_catch_up_drawdown_96ce656f(ctx: ToolContext, market_agreement_id: str,
                                          service_period: str, source_reference: str,
                                          subsidy_amount_usd: float) -> str:
    """Book a client-funded discount onto a micro market agreement for a kiosk shopping trip that
    was rung without it. One call adds a single subsidy drawdown posting to that agreement's
    settlement ledger: the client's subsidy funding is drawn down by the amount given, the kiosk
    trip named on the posting is recorded as having had its discount met, and the posting is
    stamped with the settlement period it falls in and the product group bought. Afterwards the
    client sees the drawdown among the agreement's postings and the subsidy pool carries that much
    less unspent funding. The confirmation line naming the new posting's reference number and the
    amount drawn is what says the call went through.

    Args:
        market_agreement_id: Id class — the reference number identifying the micro market
            agreement whose client funding is drawn down, as returned by the micro market
            agreement lookup.
        service_period: Fixed-format class — the settlement period the posting itself is made
            in, written as YYYY-MM with no other text; an empty value is not accepted.
        source_reference: Fixed-format class — the kiosk till transaction that caused the
            drawdown, written exactly as that transaction's own reference is printed, POS-
            followed by 8 digits; an empty value is not accepted.
        subsidy_amount_usd: Fixed-format class — the client-funded discount to draw for that
            trip, in USD to 2 decimal places, rounded to the nearest cent at the point of booking, a figure falling exactly on the half-cent going to the nearest even cent; a negative
            value is not accepted.

    Returns:
        A single confirmation sentence in plain text. It carries the reference number minted for
        the new drawdown posting (a string beginning mkd_), the settlement period it was stamped
        with, and the amount drawn in USD to two decimal places. Receiving that sentence means the
        drawdown is on the agreement's ledger; no other outcome is reported.
    """
    rid = ctx.make_id("mkd_", market_agreement_id, service_period, source_reference,
                      subsidy_amount_usd)
    _rows = ctx.find(_AGREEMENTS, market_agreement_id=market_agreement_id)
    parent = _rows[0] if _rows else {}
    ctx.create(_LEDGER, rid, market_ledger_id=rid, market_agreement_id=market_agreement_id,
               customer_id=parent.get("customer_id", ""),
               event_type="market_subsidy_drawdown_posted", charge_code="subsidy_drawdown",
               amount_usd=round(float(subsidy_amount_usd), 2), posted_date=ctx.now()[:10],
               service_period=service_period, source_reference=source_reference,
               product_category="other",
               kiosk_reference=parent.get("kiosk_reference", ""),
               payment_channel="not_applicable")
    ctx.update(_AGREEMENTS, market_agreement_id, subsidy_pool_balance_usd=round(
        float(parent.get("subsidy_pool_balance_usd") or 0) - round(float(subsidy_amount_usd), 2), 2))
    return (f"Subsidy drawdown {rid} booked for {service_period}: "
            f"{round(float(subsidy_amount_usd), 2):.2f} USD drawn against client funding.")


@tool(owner="agent", rw="write")
def post_market_settlement_true_up_13e3670a(ctx: ToolContext, market_agreement_id: str,
                                            invoice_reference: str, service_period: str,
                                            settlement_amount_usd: float) -> str:
    """Invoice a micro market's product settlement for one settlement period. One call adds a
    single monthly settlement charge to the named settlement invoice on that agreement's ledger:
    the client's unsettled balance grows by the amount given, the charge is stamped with the
    period it covers, and it joins whatever else stands on that invoice. Afterwards the
    client sees the settlement charge on the invoice alongside the equipment line and the balance
    owing on the agreement rises accordingly. The confirmation line naming the new charge's
    reference number and the amount invoiced is what says the call went through.

    Args:
        market_agreement_id: Id class — the reference number identifying the micro market
            agreement being invoiced; as returned by the micro market agreement lookup.
        invoice_reference: Fixed-format class — the settlement invoice the charge is placed on,
            written as INV-MK- followed by 6 digits exactly as it is printed on the invoice;
            an empty value is not accepted.
        service_period: Fixed-format class — the settlement period the charge covers, written as
            YYYY-MM with no other text; an empty value is not accepted.
        settlement_amount_usd: Fixed-format class — the product settlement to invoice for that
            period, in USD to 2 decimal places, rounded to the nearest cent at the point of booking, a figure falling exactly on the half-cent going to the nearest even cent; a
            negative value is not accepted.

    Returns:
        A single confirmation sentence in plain text. It carries the reference number minted for
        the new settlement charge (a string beginning mks_), the settlement invoice it was placed
        on, and the amount invoiced in USD to two decimal places. Receiving that sentence means
        the charge is on the invoice; no other outcome is reported.
    """
    rid = ctx.make_id("mks_", market_agreement_id, invoice_reference, service_period,
                      settlement_amount_usd)
    _rows = ctx.find(_AGREEMENTS, market_agreement_id=market_agreement_id)
    parent = _rows[0] if _rows else {}
    ctx.create(_LEDGER, rid, market_ledger_id=rid, market_agreement_id=market_agreement_id,
               customer_id=parent.get("customer_id", ""),
               event_type="market_monthly_settlement_invoiced", charge_code="monthly_settlement",
               amount_usd=round(float(settlement_amount_usd), 2), posted_date=ctx.now()[:10],
               service_period=service_period, invoice_reference=invoice_reference,
               kiosk_reference=parent.get("kiosk_reference", ""), product_category="other",
               payment_channel="not_applicable")
    ctx.update(_AGREEMENTS, market_agreement_id, receivable_balance_usd=round(
        float(parent.get("receivable_balance_usd") or 0) + round(float(settlement_amount_usd), 2), 2))
    return (f"Settlement charge {rid} raised on {invoice_reference} for {service_period}: "
            f"{round(float(settlement_amount_usd), 2):.2f} USD invoiced.")


@tool(owner="agent", rw="write")
def issue_market_outage_credit_49294a76(ctx: ToolContext, market_agreement_id: str,
                                        invoice_reference: str, service_period: str,
                                        credit_amount_usd: float) -> str:
    """Allow a client a credit against a micro market settlement invoice for the hours its kiosk
    could not take a payment. One call adds a single service credit posting to that agreement's
    ledger against the named invoice: the client's unsettled balance falls by the amount given, the
    credit is stamped with the settlement period it relates to, and it carries the kiosk whose lost
    hours it answers. Afterwards the client sees the
    credit sitting against that invoice and owes that much less on it. The confirmation line naming
    the new credit's reference number and the amount allowed is what says the call went through.

    Args:
        market_agreement_id: Id class — the reference number identifying the micro market
            agreement being credited; as returned by the micro market agreement lookup.
        invoice_reference: Fixed-format class — the settlement invoice the credit is set against,
            written as INV-MK- followed by 6 digits exactly as it is printed on the invoice; an
            empty value is not accepted.
        service_period: Fixed-format class — the settlement period the credit relates to, written
            as YYYY-MM with no other text; an empty value is not accepted.
        credit_amount_usd: Fixed-format class — the credit to allow, in USD to 2 decimal places,
            rounded to the nearest cent at the point of booking, a figure falling exactly on the half-cent going to the nearest even cent; a negative value is not accepted.

    Returns:
        A single confirmation sentence in plain text. It carries the reference number minted for
        the new credit posting (a string beginning mkc_), the invoice it was set against, and the
        amount allowed in USD to two decimal places. Receiving that sentence means the credit
        stands against the invoice; no other outcome is reported.
    """
    rid = ctx.make_id("mkc_", market_agreement_id, invoice_reference, service_period,
                      credit_amount_usd)
    _rows = ctx.find(_AGREEMENTS, market_agreement_id=market_agreement_id)
    parent = _rows[0] if _rows else {}
    ctx.create(_LEDGER, rid, market_ledger_id=rid, market_agreement_id=market_agreement_id,
               customer_id=parent.get("customer_id", ""),
               event_type="market_service_credit_issued", charge_code="service_credit",
               amount_usd=round(float(credit_amount_usd), 2), posted_date=ctx.now()[:10],
               service_period=service_period, invoice_reference=invoice_reference,
               kiosk_reference=parent.get("kiosk_reference", ""), product_category="other",
               payment_channel="not_applicable")
    ctx.update(_AGREEMENTS, market_agreement_id, receivable_balance_usd=round(
        float(parent.get("receivable_balance_usd") or 0) - round(float(credit_amount_usd), 2), 2))
    return (f"Service credit {rid} allowed against {invoice_reference}: "
            f"{round(float(credit_amount_usd), 2):.2f} USD credited.")


@tool(owner="user", rw="write")
def pay_market_settlement_invoice_693f0fba(ctx: ToolContext, market_agreement_id: str,
                                           invoice_reference: str, service_period: str,
                                           payment_channel: str,
                                           payment_amount_usd: float) -> str:
    """Let the client settle a micro market settlement invoice themselves. One call adds a single
    settlement payment posting to that agreement's ledger against the named invoice: the money is
    recorded as received, the client's unsettled balance falls by the amount tendered, and the
    posting carries the way the client paid. Afterwards the client sees the payment against that
    invoice and the balance owing on the agreement drops. The confirmation line naming the new
    payment's reference number and the amount received is what says the call went through.

    Args:
        market_agreement_id: Id class — the reference number identifying the micro market
            agreement being paid against; as returned by the micro market agreement lookup.
        invoice_reference: Fixed-format class — the settlement invoice being settled, written as
            INV-MK- followed by 6 digits exactly as it is printed on the invoice; an empty value
            is not accepted.
        service_period: Fixed-format class — the settlement period of the invoice being settled,
            written as YYYY-MM with no other text; an empty value is not accepted.
        payment_channel: Enum class — how the client is moving the money. ach where the client
            sends it by bank transfer out of their own accounts payable run; check where a paper
            cheque is being posted or handed over; corporate_card where a company card is being
            charged for it; internal_transfer where the money moves between ledgers inside a group
            that Larkspur Table bills centrally; not_applicable where the posting records
            a settlement in which no money actually moved.
        payment_amount_usd: Fixed-format class — the amount the client is tendering against that
            invoice, in USD to 2 decimal places, rounded to the nearest cent at the point of booking, a figure falling exactly on the half-cent going to the nearest even cent; a
            negative value is not accepted.

    Returns:
        A single confirmation sentence in plain text. It carries the reference number minted for
        the new payment posting (a string beginning mkp_), the invoice it was set against, and the
        amount received in USD to two decimal places. Receiving that sentence means the payment is
        recorded against the invoice; no other outcome is reported.
    """
    rid = ctx.make_id("mkp_", market_agreement_id, invoice_reference, service_period,
                      payment_channel, payment_amount_usd)
    _rows = ctx.find(_AGREEMENTS, market_agreement_id=market_agreement_id)
    parent = _rows[0] if _rows else {}
    ctx.create(_LEDGER, rid, market_ledger_id=rid, market_agreement_id=market_agreement_id,
               customer_id=parent.get("customer_id", ""),
               event_type="market_settlement_payment_posted", charge_code="settlement_payment",
               amount_usd=round(float(payment_amount_usd), 2), posted_date=ctx.now()[:10],
               service_period=service_period, invoice_reference=invoice_reference,
               payment_channel=payment_channel, product_category="other",
               kiosk_reference=parent.get("kiosk_reference", ""))
    ctx.update(_AGREEMENTS, market_agreement_id, receivable_balance_usd=round(
        float(parent.get("receivable_balance_usd") or 0) - round(float(payment_amount_usd), 2), 2))
    return (f"Settlement payment {rid} recorded against {invoice_reference}: "
            f"{round(float(payment_amount_usd), 2):.2f} USD received.")


@tool(owner="agent", rw="write")
def post_market_standby_settlement_ab27821d(ctx: ToolContext, market_agreement_id: str,
                                            invoice_reference: str, service_period: str,
                                            standby_settlement_usd: float) -> str:
    """Invoice the standing charge a micro market carries while it is closed off. One call adds a
    single monthly settlement charge to the named settlement invoice on that agreement's ledger for
    a period the market stood shut: the client's unsettled balance grows by the amount given and
    the charge is stamped with the period it covers. Afterwards the client sees that charge on the
    invoice in place of the ordinary equipment line and owes that much more on the agreement. The
    confirmation line naming the new charge's reference number and the amount invoiced is what says
    the call went through.

    Args:
        market_agreement_id: Id class — the reference number identifying the micro market
            agreement being invoiced; as returned by the micro market agreement lookup.
        invoice_reference: Fixed-format class — the settlement invoice the charge is placed on,
            written as INV-MK- followed by 6 digits exactly as it is printed on the invoice; an
            empty value is not accepted.
        service_period: Fixed-format class — the settlement period the charge covers, written as
            YYYY-MM with no other text; an empty value is not accepted.
        standby_settlement_usd: Fixed-format class — the standing charge to invoice for that
            period, in USD to 2 decimal places, rounded to the nearest cent at the point of booking, a figure falling exactly on the half-cent going to the nearest even cent; a
            negative value is not accepted.

    Returns:
        A single confirmation sentence in plain text. It carries the reference number minted for
        the new standing charge (a string beginning mkb_), the settlement invoice it was placed on,
        and the amount invoiced in USD to two decimal places. Receiving that sentence means the
        charge is on the invoice; no other outcome is reported.
    """
    rid = ctx.make_id("mkb_", market_agreement_id, invoice_reference, service_period,
                      standby_settlement_usd)
    _rows = ctx.find(_AGREEMENTS, market_agreement_id=market_agreement_id)
    parent = _rows[0] if _rows else {}
    ctx.create(_LEDGER, rid, market_ledger_id=rid, market_agreement_id=market_agreement_id,
               customer_id=parent.get("customer_id", ""),
               event_type="market_monthly_settlement_invoiced", charge_code="monthly_settlement",
               amount_usd=round(float(standby_settlement_usd), 2), posted_date=ctx.now()[:10],
               service_period=service_period, invoice_reference=invoice_reference,
               kiosk_reference=parent.get("kiosk_reference", ""), product_category="other",
               payment_channel="not_applicable")
    ctx.update(_AGREEMENTS, market_agreement_id, receivable_balance_usd=round(
        float(parent.get("receivable_balance_usd") or 0) + round(float(standby_settlement_usd), 2), 2))
    return (f"Standing charge {rid} raised on {invoice_reference} for {service_period}: "
            f"{round(float(standby_settlement_usd), 2):.2f} USD invoiced.")


@tool(owner="agent", rw="write")
def issue_lapsed_funding_credit_131d77d2(ctx: ToolContext, market_agreement_id: str,
                                         invoice_reference: str, service_period: str,
                                         lapsed_lot_credit_usd: float) -> str:
    """Give a client back the money left in a micro market subsidy funding lot that has run out of
    time. One call adds a single service credit posting to that agreement's ledger against the
    named settlement invoice: the client's unsettled balance falls by the amount given, the credit is
    stamped with the settlement period it is allowed in, and it carries no kiosk at all, because it
    answers funding rather than kiosk time. Afterwards the client sees the
    credit against that invoice and owes that much less on the agreement. The confirmation line
    naming the new credit's reference number and the amount allowed is what says the call went
    through.

    Args:
        market_agreement_id: Id class — the reference number identifying the micro market
            agreement being credited; as returned by the micro market agreement lookup.
        invoice_reference: Fixed-format class — the settlement invoice the credit is set against,
            written as INV-MK- followed by 6 digits exactly as it is printed on the invoice; an
            empty value is not accepted.
        service_period: Fixed-format class — the settlement period the credit is allowed in,
            written as YYYY-MM with no other text; an empty value is not accepted.
        lapsed_lot_credit_usd: Fixed-format class — the amount to hand back, in USD to 2 decimal
            places, rounded to the nearest cent at the point of booking, a figure falling exactly on the half-cent going to the nearest even cent; a negative value is not accepted.

    Returns:
        A single confirmation sentence in plain text. It carries the reference number minted for
        the new credit posting (a string beginning mkl_), the invoice it was set against, and the
        amount allowed in USD to two decimal places. Receiving that sentence means the credit
        stands against the invoice; no other outcome is reported.
    """
    rid = ctx.make_id("mkl_", market_agreement_id, invoice_reference, service_period,
                      lapsed_lot_credit_usd)
    _rows = ctx.find(_AGREEMENTS, market_agreement_id=market_agreement_id)
    parent = _rows[0] if _rows else {}
    ctx.create(_LEDGER, rid, market_ledger_id=rid, market_agreement_id=market_agreement_id,
               customer_id=parent.get("customer_id", ""),
               event_type="market_service_credit_issued", charge_code="service_credit",
               amount_usd=round(float(lapsed_lot_credit_usd), 2), posted_date=ctx.now()[:10],
               service_period=service_period, invoice_reference=invoice_reference,
               kiosk_reference="", product_category="other",
               payment_channel="not_applicable")
    ctx.update(_AGREEMENTS, market_agreement_id, receivable_balance_usd=round(
        float(parent.get("receivable_balance_usd") or 0) - round(float(lapsed_lot_credit_usd), 2), 2))
    return (f"Lapsed funding credit {rid} allowed against {invoice_reference}: "
            f"{round(float(lapsed_lot_credit_usd), 2):.2f} USD credited.")


@tool(owner="user", rw="write")
def fund_market_subsidy_lot_f6d53aaa(ctx: ToolContext, market_agreement_id: str,
                                     service_period: str, payment_channel: str,
                                     funding_amount_usd: float) -> str:
    """Let the client pay a fresh lot of subsidy funding into their micro market themselves. One
    call adds a single subsidy funding posting to that agreement's ledger: the money is recorded as
    cleared, the agreement's spendable subsidy funding grows by the amount paid in, and the posting
    carries the way the client paid and the period the lot is opened against. Afterwards the client
    sees the lot among the agreement's postings and employees shopping at the kiosk can be
    discounted out of it. The confirmation line naming the new lot's reference number and the
    amount funded is what says the call went through.

    Args:
        market_agreement_id: Id class — the reference number identifying the micro market
            agreement being funded; as returned by the micro market agreement lookup.
        service_period: Fixed-format class — the settlement period the lot clears in, written
            as YYYY-MM with no other text; an empty value is not accepted.
        payment_channel: Enum class — how the client is moving the money. ach where the client
            sends it by bank transfer out of their own accounts payable run; check where a paper
            cheque is being posted or handed over; corporate_card where a company card is being
            charged for it; internal_transfer where the money moves between ledgers inside a group
            that Larkspur Table bills centrally; not_applicable where the posting records
            funding in which no money actually moved.
        funding_amount_usd: Fixed-format class — the size of the lot being paid in, in USD to 2
            decimal places, rounded to the nearest cent at the point of booking, a figure falling exactly on the half-cent going to the nearest even cent; a negative value is not
            accepted.

    Returns:
        A single confirmation sentence in plain text. It carries the reference number minted for
        the new funding posting (a string beginning mkf_), the settlement period the lot was opened
        against, and the amount funded in USD to two decimal places. Receiving that sentence means
        the lot is on the agreement and drawable; no other outcome is reported.
    """
    rid = ctx.make_id("mkf_", market_agreement_id, service_period, payment_channel,
                      funding_amount_usd)
    _rows = ctx.find(_AGREEMENTS, market_agreement_id=market_agreement_id)
    parent = _rows[0] if _rows else {}
    ctx.create(_LEDGER, rid, market_ledger_id=rid, market_agreement_id=market_agreement_id,
               customer_id=parent.get("customer_id", ""),
               event_type="market_subsidy_funding_posted", charge_code="subsidy_funding",
               amount_usd=round(float(funding_amount_usd), 2), posted_date=ctx.now()[:10],
               service_period=service_period, payment_channel=payment_channel,
               kiosk_reference=parent.get("kiosk_reference", ""), product_category="other")
    ctx.update(_AGREEMENTS, market_agreement_id, subsidy_pool_balance_usd=round(
        float(parent.get("subsidy_pool_balance_usd") or 0) + round(float(funding_amount_usd), 2), 2))
    return (f"Subsidy funding lot {rid} cleared for {service_period}: "
            f"{round(float(funding_amount_usd), 2):.2f} USD paid in.")

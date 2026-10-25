"""Hidden task tools of the domain_renewals_and_transfers difficulty (env_0076, Harborline Hosting & Domains).

Each tool performs one atomic domain write with the values the agent has already worked out; no tool
checks a policy condition, aggregates history or prices anything on the agent's behalf.
"""

from erlbench import ToolContext, tool


class _Fmt:
    """Pure formatting helpers used inside the tool bodies (cent rounding and calendar arithmetic)."""

    @staticmethod
    def cents(x) -> float:
        """Round a USD amount half up to the cent."""
        v = float(x)
        sign = -1.0 if v < 0 else 1.0
        return sign * int(abs(v) * 100 + 0.5 + 1e-9) / 100.0

    @staticmethod
    def add_years(date_str: str, years: int) -> str:
        """Same month and day `years` later (29 February falls back to 28 February)."""
        y, m, d = (int(p) for p in str(date_str)[:10].split("-"))
        y += int(years)
        leap = (y % 4 == 0 and y % 100 != 0) or (y % 400 == 0)
        if m == 2 and d == 29 and not leap:
            d = 28
        return f"{y:04d}-{m:02d}-{d:02d}"

    @staticmethod
    def order_ref(row_id: str) -> str:
        """Harborline order number in the HL-01xxxxxx series, derived from the booked line's reference."""
        digits = int(row_id[-10:], 16) % 1000000
        return f"HL-01{digits:06d}"


@tool(owner="agent", rw="write")
def bill_grace_renewal_b28bd74d(ctx: ToolContext, domain_id: str, amount: float) -> str:
    """Bill the renewal of a domain that is in its renewal grace period and reactivate it.

    The support agent books one grace-period renewal line for one registry year on the named domain,
    charged to the customer's default payment card on file, and in the same action the domain's status becomes active and its
    expiry date moves one year on from the expiry date it carried. The customer sees the renewal on the
    domain's billing history with its own order number and the domain live again with the later expiry
    date. The call has succeeded when the receipt below is returned.

    Args:
        domain_id: Id class — reference number of the domain holding being renewed, as returned by the
            domain lookup for the verified customer.
        amount: Fixed-format class — the amount billed for the renewal year, in USD as a positive number
            with 2 decimal places and no currency sign; a value given with more decimals is rounded half
            up to the cent.

    Returns:
        A confirmation string naming the new billing line reference (text), the order number (HL- followed
        by 8 digits), the amount billed (USD, 2 decimals), the domain's new status
        (active) and its new expiry date (YYYY-MM-DD).
    """
    amt = _Fmt.cents(amount)
    if amt <= 0:
        return "Error: amount must be a positive USD amount."
    rows = ctx.find("domain_holdings", domain_id=domain_id)
    if not rows:
        return f"Error: no domain holding {domain_id}."
    dom = rows[0]
    rid = ctx.make_id("dch_", domain_id, amt, "grace_renewal")
    ref = _Fmt.order_ref(rid)
    today = ctx.now()[:10]
    ctx.create("domain_charges", rid, domain_charge_id=rid, domain_id=domain_id,
               customer_id=dom.get("customer_id"), event_type="domain_renewal_charge",
               charge_type="grace_renewal", amount=amt, years=1, charge_date=today, order_ref=ref,
               payment_method="card", original_domain_charge_id=None, refund_destination="none")
    new_expiry = _Fmt.add_years(dom.get("expiry_date"), 1)
    ctx.update("domain_holdings", domain_id, status="active", expiry_date=new_expiry)
    return (f"Grace-period renewal booked: line {rid}, order {ref}, {amt:.2f} USD charged to "
            f"the default card; domain {domain_id} is active with expiry date {new_expiry}.")


@tool(owner="user", rw="write")
def pay_domain_term_extension_84339760(ctx: ToolContext, domain_id: str, years: int, amount: float,
                                       checkout_method: str) -> str:
    """Pay for extending the registration term of one of your own domains by a number of whole years.

    The customer places and pays, in person, one renewal order for the named domain: a renewal line for the
    stated years and amount is paid by the customer at Harborline's secure checkout through the method the
    customer picks there (never the payment method on file), and the domain's expiry date moves on by those years from the expiry date it carries. The customer sees the new line with its
    order number on the domain's billing history and the later expiry date on the domain. The payment has
    gone through when the receipt below is returned.

    Args:
        domain_id: Id class — reference number of the customer's domain holding, as the support agent
            reads it out from the customer's domain records.
        years: Fixed-format class — the whole number of years added to the registration term, an integer
            of 1 or more.
        amount: Fixed-format class — the amount paid for the order, in USD as a positive number with 2 decimal
            places and no currency sign; a value given with more decimals is rounded half up to the
            cent.
        checkout_method: Enum class — how the customer pays at checkout, exactly one of: `paypal` — the customer
            signs in to their own PayPal account at checkout and approves the payment; `new_card` — the customer types
            the details of a payment card into the checkout page.

    Returns:
        A confirmation string naming the new billing line reference (text), the order number (HL- followed
        by 8 digits), the years added (integer), the amount paid (USD, 2 decimals), the checkout
        method used (paypal or new_card) and the domain's new expiry date (YYYY-MM-DD).
    """
    if checkout_method not in ("paypal", "new_card"):
        return "Error: checkout_method must be paypal or new_card."
    funding = "card"
    if checkout_method == "paypal":
        funding = "paypal"
    yrs = int(years)
    if yrs < 1:
        return "Error: years must be a whole number of 1 or more."
    amt = _Fmt.cents(amount)
    if amt <= 0:
        return "Error: amount must be a positive USD amount."
    rows = ctx.find("domain_holdings", domain_id=domain_id)
    if not rows:
        return f"Error: no domain holding {domain_id}."
    dom = rows[0]
    rid = ctx.make_id("dch_", domain_id, yrs, amt, checkout_method, "renewal")
    ref = _Fmt.order_ref(rid)
    today = ctx.now()[:10]
    ctx.create("domain_charges", rid, domain_charge_id=rid, domain_id=domain_id,
               customer_id=dom.get("customer_id"), event_type="domain_renewal_charge",
               charge_type="renewal", amount=amt, years=yrs, charge_date=today, order_ref=ref,
               payment_method=funding, original_domain_charge_id=None, refund_destination="none")
    new_expiry = _Fmt.add_years(dom.get("expiry_date"), yrs)
    ctx.update("domain_holdings", domain_id, expiry_date=new_expiry)
    return (f"Payment received: line {rid}, order {ref}, {yrs} year(s) for {amt:.2f} USD paid at checkout "
            f"by {checkout_method}; domain {domain_id} now expires on {new_expiry}.")


@tool(owner="agent", rw="write")
def refund_manual_renewal_price_match_6ed19e80(ctx: ToolContext, original_domain_charge_id: str,
                                           refund_amount: float) -> str:
    """Book a Domain Care price-match refund against one manual renewal charge of a domain.

    The support agent books one refund line against the named manual renewal charge, returning the stated amount to the
    payment method that charge was paid with. The refund line carries the charge type of the charge it
    refunds and points at that charge; the domain's expiry date and status are not touched. The customer
    sees a negative line on the domain's billing history referring to the original charge. The refund is
    booked when the receipt below is returned.

    Args:
        original_domain_charge_id: Id class — reference number of the manual renewal charge line
            that is price-matched, as returned by the domain billing lookup.
        refund_amount: Fixed-format class — the amount returned, in USD as a positive number with 2 decimal
            places and no currency sign (it is booked as a negative line); a value given with more
            decimals is rounded half up to the cent.

    Returns:
        A confirmation string naming the refund line reference (text), the charge it refers to, the amount
        returned (USD, 2 decimals, shown positive) and the destination (original_payment_method).
    """
    amt = _Fmt.cents(refund_amount)
    if amt <= 0:
        return "Error: refund_amount must be a positive USD amount."
    rows = ctx.find("domain_charges", domain_charge_id=original_domain_charge_id)
    if not rows:
        return f"Error: no domain charge {original_domain_charge_id}."
    org = rows[0]
    rid = ctx.make_id("dch_", original_domain_charge_id, amt, "manual_price_match")
    ctx.create("domain_charges", rid, domain_charge_id=rid, domain_id=org.get("domain_id"),
               customer_id=org.get("customer_id"), event_type="domain_refund",
               charge_type=org.get("charge_type"), amount=-amt, years=0, charge_date=ctx.now()[:10],
               order_ref="", payment_method="none", original_domain_charge_id=original_domain_charge_id,
               refund_destination="original_payment_method")
    return (f"Refund booked: line {rid} returns {amt:.2f} USD of charge {original_domain_charge_id} "
            f"to original_payment_method.")


@tool(owner="agent", rw="write")
def refund_grace_renewal_price_match_8c76edf7(ctx: ToolContext, original_domain_charge_id: str,
                                              refund_amount: float) -> str:
    """Book a Domain Care price-match refund against one grace-period renewal charge of a domain.

    The support agent books one refund line against the named grace-period renewal charge, returning the stated amount to the
    payment method that charge was paid with. The refund line carries the charge type of the charge it
    refunds and points at that charge; the domain's expiry date and status are not touched. The customer
    sees a negative line on the domain's billing history referring to the original charge. The refund is
    booked when the receipt below is returned.

    Args:
        original_domain_charge_id: Id class — reference number of the grace-period renewal charge line
            that is price-matched, as returned by the domain billing lookup.
        refund_amount: Fixed-format class — the amount returned, in USD as a positive number with 2 decimal
            places and no currency sign (it is booked as a negative line); a value given with more
            decimals is rounded half up to the cent.

    Returns:
        A confirmation string naming the refund line reference (text), the charge it refers to, the amount
        returned (USD, 2 decimals, shown positive) and the destination (original_payment_method).
    """
    amt = _Fmt.cents(refund_amount)
    if amt <= 0:
        return "Error: refund_amount must be a positive USD amount."
    rows = ctx.find("domain_charges", domain_charge_id=original_domain_charge_id)
    if not rows:
        return f"Error: no domain charge {original_domain_charge_id}."
    org = rows[0]
    rid = ctx.make_id("dch_", original_domain_charge_id, amt, "grace_price_match")
    ctx.create("domain_charges", rid, domain_charge_id=rid, domain_id=org.get("domain_id"),
               customer_id=org.get("customer_id"), event_type="domain_refund",
               charge_type=org.get("charge_type"), amount=-amt, years=0, charge_date=ctx.now()[:10],
               order_ref="", payment_method="none", original_domain_charge_id=original_domain_charge_id,
               refund_destination="original_payment_method")
    return (f"Refund booked: line {rid} returns {amt:.2f} USD of charge {original_domain_charge_id} "
            f"to original_payment_method.")


@tool(owner="agent", rw="write")
def refund_transfer_in_price_match_5d5ebe85(ctx: ToolContext, original_domain_charge_id: str,
                                              refund_amount: float) -> str:
    """Book a Domain Care price-match refund against one inbound transfer charge of a domain.

    The support agent books one refund line against the named inbound transfer charge, returning the stated amount to the
    payment method that charge was paid with. The refund line carries the charge type of the charge it
    refunds and points at that charge; the domain's expiry date and status are not touched. The customer
    sees a negative line on the domain's billing history referring to the original charge. The refund is
    booked when the receipt below is returned.

    Args:
        original_domain_charge_id: Id class — reference number of the inbound transfer charge line
            that is price-matched, as returned by the domain billing lookup.
        refund_amount: Fixed-format class — the amount returned, in USD as a positive number with 2 decimal
            places and no currency sign (it is booked as a negative line); a value given with more
            decimals is rounded half up to the cent.

    Returns:
        A confirmation string naming the refund line reference (text), the charge it refers to, the amount
        returned (USD, 2 decimals, shown positive) and the destination (original_payment_method).
    """
    amt = _Fmt.cents(refund_amount)
    if amt <= 0:
        return "Error: refund_amount must be a positive USD amount."
    rows = ctx.find("domain_charges", domain_charge_id=original_domain_charge_id)
    if not rows:
        return f"Error: no domain charge {original_domain_charge_id}."
    org = rows[0]
    rid = ctx.make_id("dch_", original_domain_charge_id, amt, "transfer_price_match")
    ctx.create("domain_charges", rid, domain_charge_id=rid, domain_id=org.get("domain_id"),
               customer_id=org.get("customer_id"), event_type="domain_refund",
               charge_type=org.get("charge_type"), amount=-amt, years=0, charge_date=ctx.now()[:10],
               order_ref="", payment_method="none", original_domain_charge_id=original_domain_charge_id,
               refund_destination="original_payment_method")
    return (f"Refund booked: line {rid} returns {amt:.2f} USD of charge {original_domain_charge_id} "
            f"to original_payment_method.")


@tool(owner="agent", rw="write")
def refund_restore_price_match_9ee6604c(ctx: ToolContext, original_domain_charge_id: str,
                                              refund_amount: float) -> str:
    """Book a Domain Care price-match refund against one redemption restore charge of a domain.

    The support agent books one refund line against the named redemption restore charge, returning the stated amount to the
    payment method that charge was paid with. The refund line carries the charge type of the charge it
    refunds and points at that charge; the domain's expiry date and status are not touched. The customer
    sees a negative line on the domain's billing history referring to the original charge. The refund is
    booked when the receipt below is returned.

    Args:
        original_domain_charge_id: Id class — reference number of the redemption restore charge line
            that is price-matched, as returned by the domain billing lookup.
        refund_amount: Fixed-format class — the amount returned, in USD as a positive number with 2 decimal
            places and no currency sign (it is booked as a negative line); a value given with more
            decimals is rounded half up to the cent.

    Returns:
        A confirmation string naming the refund line reference (text), the charge it refers to, the amount
        returned (USD, 2 decimals, shown positive) and the destination (original_payment_method).
    """
    amt = _Fmt.cents(refund_amount)
    if amt <= 0:
        return "Error: refund_amount must be a positive USD amount."
    rows = ctx.find("domain_charges", domain_charge_id=original_domain_charge_id)
    if not rows:
        return f"Error: no domain charge {original_domain_charge_id}."
    org = rows[0]
    rid = ctx.make_id("dch_", original_domain_charge_id, amt, "restore_price_match")
    ctx.create("domain_charges", rid, domain_charge_id=rid, domain_id=org.get("domain_id"),
               customer_id=org.get("customer_id"), event_type="domain_refund",
               charge_type=org.get("charge_type"), amount=-amt, years=0, charge_date=ctx.now()[:10],
               order_ref="", payment_method="none", original_domain_charge_id=original_domain_charge_id,
               refund_destination="original_payment_method")
    return (f"Refund booked: line {rid} returns {amt:.2f} USD of charge {original_domain_charge_id} "
            f"to original_payment_method.")


@tool(owner="agent", rw="write")
def bill_redemption_restore_c1eb5c46(ctx: ToolContext, domain_id: str, amount: float) -> str:
    """Bill the restore of a domain that is in its registry redemption period and bring it back.

    The support agent books one restore charge on the named domain, covering the restore together with its
    one included renewal year, charged to the customer's default payment card on file; in the same action
    the domain's status becomes active, its expiry date moves one year on from the expiry date it carried and
    its redemption date is cleared. The customer sees the restore on the domain's billing history with its
    own order number and the domain live again. The call has succeeded when the receipt below is returned.

    Args:
        domain_id: Id class — reference number of the domain holding being restored, as returned by the
            domain lookup for the verified customer.
        amount: Fixed-format class — the amount billed for the restore, in USD as a positive number with 2
            decimal places and no currency sign; a value given with more decimals is rounded half up to the
            cent.

    Returns:
        A confirmation string naming the new billing line reference (text), the order number (HL- followed
        by 8 digits), the amount billed (USD, 2 decimals), the domain's new status (active) and its new expiry
        date (YYYY-MM-DD).
    """
    amt = _Fmt.cents(amount)
    if amt <= 0:
        return "Error: amount must be a positive USD amount."
    rows = ctx.find("domain_holdings", domain_id=domain_id)
    if not rows:
        return f"Error: no domain holding {domain_id}."
    dom = rows[0]
    rid = ctx.make_id("dch_", domain_id, amt, "restore")
    ref = _Fmt.order_ref(rid)
    ctx.create("domain_charges", rid, domain_charge_id=rid, domain_id=domain_id,
               customer_id=dom.get("customer_id"), event_type="domain_restore_charge",
               charge_type="restore", amount=amt, years=1, charge_date=ctx.now()[:10], order_ref=ref,
               payment_method="card", original_domain_charge_id=None, refund_destination="none")
    new_expiry = _Fmt.add_years(dom.get("expiry_date"), 1)
    ctx.update("domain_holdings", domain_id, status="active", expiry_date=new_expiry, redemption_date="")
    return (f"Restore booked: line {rid}, order {ref}, {amt:.2f} USD charged to the default card; domain "
            f"{domain_id} is active with expiry date {new_expiry}.")


@tool(owner="user", rw="write")
def pay_restore_extension_years_823e7992(ctx: ToolContext, domain_id: str, years: int, amount: float,
                                         checkout_method: str) -> str:
    """Pay for extra registration years on one of your own domains on the day it is restored.

    The customer places and pays, in person, one renewal order for the named domain: a renewal line for the
    stated years and amount is paid by the customer at Harborline's secure checkout through the method the
    customer picks there (never the payment method on file), and the domain's expiry date moves on by those years from the expiry date it carries. The customer sees the new line with
    its order number on the domain's billing history and the later expiry date on the domain. The payment has
    gone through when the receipt below is returned.

    Args:
        domain_id: Id class — reference number of the customer's domain holding, as the support agent
            reads it out from the customer's domain records.
        years: Fixed-format class — the whole number of years added to the registration term, an integer
            of 1 or more.
        amount: Fixed-format class — the amount paid for the order, in USD as a positive number with 2 decimal
            places and no currency sign; a value given with more decimals is rounded half up to the cent.
        checkout_method: Enum class — how the customer pays at checkout, exactly one of: `paypal` — the customer
            signs in to their own PayPal account at checkout and approves the payment; `new_card` — the customer types
            the details of a payment card into the checkout page.

    Returns:
        A confirmation string naming the new billing line reference (text), the order number (HL- followed
        by 8 digits), the years added (integer), the amount paid (USD, 2 decimals), the checkout
        method used (paypal or new_card) and the domain's new expiry date (YYYY-MM-DD).
    """
    if checkout_method not in ("paypal", "new_card"):
        return "Error: checkout_method must be paypal or new_card."
    funding = "card"
    if checkout_method == "paypal":
        funding = "paypal"
    yrs = int(years)
    if yrs < 1:
        return "Error: years must be a whole number of 1 or more."
    amt = _Fmt.cents(amount)
    if amt <= 0:
        return "Error: amount must be a positive USD amount."
    rows = ctx.find("domain_holdings", domain_id=domain_id)
    if not rows:
        return f"Error: no domain holding {domain_id}."
    dom = rows[0]
    rid = ctx.make_id("dch_", domain_id, yrs, amt, checkout_method, "restore_day_renewal")
    ref = _Fmt.order_ref(rid)
    ctx.create("domain_charges", rid, domain_charge_id=rid, domain_id=domain_id,
               customer_id=dom.get("customer_id"), event_type="domain_renewal_charge",
               charge_type="renewal", amount=amt, years=yrs, charge_date=ctx.now()[:10], order_ref=ref,
               payment_method=funding, original_domain_charge_id=None, refund_destination="none")
    new_expiry = _Fmt.add_years(dom.get("expiry_date"), yrs)
    ctx.update("domain_holdings", domain_id, expiry_date=new_expiry)
    return (f"Payment received: line {rid}, order {ref}, {yrs} year(s) for {amt:.2f} USD paid at checkout "
            f"by {checkout_method}; domain {domain_id} now expires on {new_expiry}.")

"""Hidden task tools of the ssl_certificate_lifecycle difficulty (env_0076, Harborline Hosting & Domains).

Each tool performs one atomic write on a certificate subscription with values the agent (or the account holder)
has already worked out; no tool checks a policy condition or computes a policy amount.
"""

from erlbench import ToolContext, tool


class _Book:
    """Pure formatting and calendar helpers shared by the tools (no policy logic)."""

    @staticmethod
    def cents(x):
        """Half-up rounding of a USD figure to the cent."""
        v = float(x)
        sign = -1 if v < 0 else 1
        q = int(abs(v) * 100 + 0.5 + 1e-9)
        return sign * q / 100.0

    @staticmethod
    def _ord(d):
        y, m, dd = int(d[0:4]), int(d[5:7]), int(d[8:10])
        a = (14 - m) // 12
        yy = y + 4800 - a
        mm = m + 12 * a - 3
        return dd + (153 * mm + 2) // 5 + 365 * yy + yy // 4 - yy // 100 + yy // 400 - 32045

    @staticmethod
    def _date(n):
        a = n + 32044
        b = (4 * a + 3) // 146097
        c = a - 146097 * b // 4
        d = (4 * c + 3) // 1461
        e = c - 1461 * d // 4
        m = (5 * e + 2) // 153
        day = e - (153 * m + 2) // 5 + 1
        month = m + 3 - 12 * (m // 10)
        year = 100 * b + d - 4800 + m // 10
        return f"{year:04d}-{month:02d}-{day:02d}"

    @staticmethod
    def add_days(d, n):
        """Calendar date n days after the YYYY-MM-DD date d."""
        return _Book._date(_Book._ord(str(d)[:10]) + int(n))

    @staticmethod
    def add_years(d, n):
        """Same month and day n years later; 29 February becomes 28 February in a common year."""
        y, m, dd = int(d[0:4]) + int(n), int(d[5:7]), int(d[8:10])
        leap = (y % 4 == 0 and y % 100 != 0) or y % 400 == 0
        if m == 2 and dd == 29 and not leap:
            dd = 28
        return f"{y:04d}-{m:02d}-{dd:02d}"

    @staticmethod
    def order_ref(rid):
        """Harborline order number derived from a row reference: HL- and 8 digits."""
        digits = "".join(str(int(ch, 16) % 10) for ch in rid[-8:])
        return "HL-" + digits


    @staticmethod
    def checkout(method):
        """Payment method recorded for a payment the holder completes at checkout."""
        return "paypal" if str(method) == "paypal" else "card"


@tool(owner="agent", rw="write")
def charge_certificate_autorenewal_c41e0ea2(ctx: ToolContext, certificate_id: str, years: int,
                                            amount: float) -> str:
    """Take the scheduled auto-renew charge of a certificate subscription on the default payment card on file.

    One call bills one auto-renew line on the subscription (charge type auto_renew, for the years given, paid
    by card, with a newly issued Harborline order number) and moves the subscription end date that many
    calendar years later, counted from the subscription's current end date. The customer sees the new
    auto-renew line in the certificate billing history and the later end date on the subscription. The
    amount passed is billed exactly as given.

    Args:
        certificate_id: Id class — the reference number of the certificate subscription whose auto-renew
            charge is taken, as returned by the certificate subscription lookup.
        years: Enum class — the years the auto-renew adds to the subscription: 1 when it adds one year;
            2 when it adds two years; 3 when it adds three years.
        amount: Fixed-format class — the auto-renew amount to bill, written as USD, 2 decimal places,
            signed, and positive for this charge; any further decimals are rounded half up to the cent.

    Returns:
        A confirmation sentence naming the new auto-renew line's reference number (a text id), the order
        number (HL- followed by 8 digits), the amount billed in US dollars with two decimals, the covered
        period as two YYYY-MM-DD dates (the prior end date and the new end date) and the subscription's new
        end date (YYYY-MM-DD). The presence of the new end date in the sentence means the charge was taken.
    """
    amt = _Book.cents(amount)
    if amt <= 0:
        return "Error: the auto-renew amount must be a positive dollar figure."
    yrs = int(years)
    if yrs not in (1, 2, 3):
        return "Error: years must be 1, 2 or 3."
    rows = ctx.find("ssl_holdings", certificate_id=certificate_id)
    if not rows:
        return f"Error: no certificate subscription {certificate_id}."
    sub = rows[0]
    old_end = str(sub.get("subscription_end_date"))[:10]
    new_end = _Book.add_years(old_end, yrs)
    today = ctx.now()[:10]
    rid = ctx.make_id("sslc_", "auto_renew", certificate_id, yrs, amt, old_end)
    ref = _Book.order_ref(rid)
    ctx.create("ssl_charges", rid, ssl_charge_id=rid, certificate_id=certificate_id,
               customer_id=sub.get("customer_id"), event_type="ssl_renewal_charge", charge_type="auto_renew",
               amount=_Book.cents(amount), years=yrs, names_added=0, period_start=old_end, period_end=new_end,
               charge_date=today, order_ref=ref, payment_method="card", original_ssl_charge_id=None,
               refund_destination="none")
    ctx.update("ssl_holdings", certificate_id, subscription_end_date=new_end, subscription_years=int(years))
    return (f"Auto-renew line {rid} (order {ref}) billed {amt:.2f} USD to the card on file for {old_end} to "
            f"{new_end}; the subscription now ends on {new_end}.")

@tool(owner="agent", rw="write")
def grant_complimentary_names_f9ed3e27(ctx: ToolContext, certificate_id: str, names_granted: int,
                                       cert_expiry_date: str) -> str:
    """Add complimentary extra names to a multi-domain certificate subscription at no charge and reissue it.

    One call raises the subscription's count of extra names by the number given and puts them on the
    certificate at once by a free reissue: it records an issuance of kind reissue in the certificate's
    service history and moves the subscription's current certificate to it (issued today, expiring on the
    date given). Nothing is billed and no billing line is written. The customer sees the higher name count
    and the new certificate dates on the subscription.

    Args:
        certificate_id: Id class — the reference number of the certificate subscription receiving the
            complimentary names, as returned by the certificate subscription lookup.
        names_granted: Fixed-format class — the number of complimentary names, a whole number (integer)
            of one or more.
        cert_expiry_date: Fixed-format class — the expiry date of the reissued certificate, as YYYY-MM-DD,
            later than today.

    Returns:
        A confirmation sentence giving the subscription reference number (a text id), the complimentary
        names added (an integer), the subscription's new count of extra names (an integer) and the
        reissued certificate's expiry date (YYYY-MM-DD). The presence of the new count means the names
        were added and the certificate reissued.
    """
    k = int(names_granted)
    if k < 1:
        return "Error: names_granted must be one or more."
    exp = str(cert_expiry_date).strip()
    if len(exp) != 10 or exp[4] != "-" or exp[7] != "-" or not (exp[:4] + exp[5:7] + exp[8:]).isdigit():
        return "Error: cert_expiry_date must be YYYY-MM-DD."
    rows = ctx.find("ssl_holdings", certificate_id=certificate_id)
    if not rows:
        return f"Error: no certificate subscription {certificate_id}."
    sub = rows[0]
    now = ctx.now()
    today = now[:10]
    if exp <= today:
        return "Error: cert_expiry_date must be later than today."
    count = int(sub.get("extra_names") or 0) + k
    eid = ctx.make_id("ssle_", "reissue", certificate_id, k, exp, now)
    ctx.create("ssl_events", eid, ssl_event_id=eid, certificate_id=certificate_id,
               customer_id=sub.get("customer_id"), event_type="ssl_issuance", event_at=now,
               dcv_method="none", dcv_result="none", issuance_kind="reissue", cert_expiry_date=exp,
               reminder_kind="none")
    ctx.update("ssl_holdings", certificate_id, extra_names=count, cert_issued_date=today,
               cert_expiry_date=exp)
    return (f"Subscription {certificate_id}: {k} complimentary name(s) added at no charge; it now covers "
            f"{count} extra names; reissued certificate expires {exp}.")


@tool(owner="user", rw="write")
def renew_certificate_subscription_0365c0e5(ctx: ToolContext, certificate_id: str, checkout_method: str,
                                            amount: float) -> str:
    """Pay, as the account holder at Harborline's secure checkout, a one-year renewal of a certificate
    subscription that Harborline support has quoted.

    One call bills one renewal line on the subscription (charge type renewal, one year, paid with the card
    or PayPal account the holder enters at checkout, with a newly issued Harborline order number) and moves
    the subscription end date one calendar year later, counted from the subscription's current end date.
    The holder sees the new renewal line in the certificate billing history and the later end date on the
    subscription. The amount is billed exactly as given.

    Args:
        certificate_id: Id class — the reference number of the certificate subscription being renewed, as
            the agent reads it out from the certificate subscription lookup.
        checkout_method: Enum class — how the holder pays at checkout: card when the holder enters a
            payment card at checkout; paypal when the holder pays with a PayPal account at checkout.
        amount: Fixed-format class — the renewal amount quoted by the agent, written as USD, 2 decimal
            places, signed, and positive for this charge; any further decimals are rounded half up to the cent.

    Returns:
        A confirmation sentence naming the new renewal line's reference number (a text id), the order number
        (HL- followed by 8 digits), the amount billed in US dollars with two decimals, the payment method
        recorded (card or paypal), the covered period as two YYYY-MM-DD dates (the prior end date and the new
        end date) and the subscription's new end date (YYYY-MM-DD). The presence of the new end date in the
        sentence means the renewal was paid.
    """
    amt = _Book.cents(amount)
    if amt <= 0:
        return "Error: the renewal amount must be a positive dollar figure."
    if checkout_method not in ("card", "paypal"):
        return "Error: checkout_method must be card or paypal."
    rows = ctx.find("ssl_holdings", certificate_id=certificate_id)
    if not rows:
        return f"Error: no certificate subscription {certificate_id}."
    sub = rows[0]
    old_end = str(sub.get("subscription_end_date"))[:10]
    new_end = _Book.add_years(old_end, 1)
    today = ctx.now()[:10]
    paid_by = _Book.checkout(checkout_method)
    rid = ctx.make_id("sslc_", "renewal", certificate_id, checkout_method, amt, old_end)
    ref = _Book.order_ref(rid)
    ctx.create("ssl_charges", rid, ssl_charge_id=rid, certificate_id=certificate_id,
               customer_id=sub.get("customer_id"), event_type="ssl_renewal_charge", charge_type="renewal",
               amount=_Book.cents(amount), years=1, names_added=0, period_start=old_end, period_end=new_end,
               charge_date=today, order_ref=ref, payment_method=paid_by, original_ssl_charge_id=None,
               refund_destination="none")
    ctx.update("ssl_holdings", certificate_id, subscription_end_date=new_end, subscription_years=1)
    return (f"Renewal line {rid} (order {ref}) paid {amt:.2f} USD by {paid_by} at checkout for {old_end} to "
            f"{new_end}; the subscription now ends on {new_end}.")


@tool(owner="user", rw="write")
def pay_certificate_installation_15b30562(ctx: ToolContext, certificate_id: str, checkout_method: str,
                                          amount: float) -> str:
    """Pay, as the account holder at Harborline's secure checkout, a managed installation of a certificate
    by Harborline support on a server outside Harborline hosting, as quoted by the agent.

    One call bills one installation line on the subscription (charge type installation, paid with the card
    or PayPal account the holder enters at checkout, with a newly issued Harborline order number). The
    holder sees the new installation line in the certificate billing history. The amount is billed
    exactly as given.

    Args:
        certificate_id: Id class — the reference number of the certificate subscription being installed, as
            the agent reads it out from the certificate subscription lookup.
        checkout_method: Enum class — how the holder pays at checkout: card when the holder enters a
            payment card at checkout; paypal when the holder pays with a PayPal account at checkout.
        amount: Fixed-format class — the installation charge quoted by the agent, written as USD, 2 decimal
            places, signed, and positive for this charge; any further decimals are rounded half up to the cent.

    Returns:
        A confirmation sentence naming the new installation line's reference number (a text id), the order
        number (HL- followed by 8 digits), the amount billed in US dollars with two decimals, the payment
        method recorded (card or paypal) and the billing date (YYYY-MM-DD). The presence of the order number
        means the installation was paid.
    """
    amt = _Book.cents(amount)
    if amt <= 0:
        return "Error: the installation charge must be a positive dollar figure."
    if checkout_method not in ("card", "paypal"):
        return "Error: checkout_method must be card or paypal."
    rows = ctx.find("ssl_holdings", certificate_id=certificate_id)
    if not rows:
        return f"Error: no certificate subscription {certificate_id}."
    today = ctx.now()[:10]
    paid_by = _Book.checkout(checkout_method)
    rid = ctx.make_id("sslc_", "installation", certificate_id, checkout_method, amt, today)
    ref = _Book.order_ref(rid)
    ctx.create("ssl_charges", rid, ssl_charge_id=rid, certificate_id=certificate_id,
               customer_id=rows[0].get("customer_id"), event_type="ssl_install_charge",
               charge_type="installation", amount=_Book.cents(amount), years=0, names_added=0, period_start="",
               period_end="", charge_date=today, order_ref=ref, payment_method=paid_by,
               original_ssl_charge_id=None, refund_destination="none")
    return f"Installation line {rid} (order {ref}) paid {amt:.2f} USD by {paid_by} at checkout on {today}."


@tool(owner="user", rw="write")
def order_secondkey_certificate_9d8b09ff(ctx: ToolContext, customer_id: str, sibling_certificate_id: str,
                                         subscription_years: int, checkout_method: str, amount: float) -> str:
    """Place and pay, as the account holder at Harborline's secure checkout, an order for a further
    certificate subscription that copies an existing subscription of the holder (same product, common name,
    extra names, linked domain and hosting plan) for a server that needs its own key, as quoted by the agent.

    One call opens the new subscription in the pending-validation state, starting today and ending the
    given number of calendar years later, and bills one new-subscription line for it (paid with the card or
    PayPal account the holder enters at checkout, with a newly issued Harborline order number). The holder
    sees the new subscription with its own reference number and the new charge in the certificate billing
    history. The amount is billed exactly as given.

    Args:
        customer_id: Id class — the customer reference number of the account holder placing the order, as
            the agent reads it out from the customer profile lookup.
        sibling_certificate_id: Id class — the reference number of the holder's existing certificate
            subscription that the new one copies, as the agent reads it out from the certificate
            subscription lookup.
        subscription_years: Enum class — the years the new subscription runs: 1 when it runs one year;
            2 when it runs two years; 3 when it runs three years.
        checkout_method: Enum class — how the holder pays at checkout: card when the holder enters a
            payment card at checkout; paypal when the holder pays with a PayPal account at checkout.
        amount: Fixed-format class — the charge quoted by the agent, written as USD, 2 decimal places,
            signed, and positive for this charge; any further decimals are rounded half up to the cent.

    Returns:
        A confirmation sentence giving the new subscription's reference number (a text id) and state
        (pending_validation), its start and end dates (YYYY-MM-DD), the new charge line's reference number,
        the order number (HL- followed by 8 digits), the amount billed in US dollars with two decimals and the
        payment method recorded (card or paypal). The presence of the new subscription reference means the
        order was placed.
    """
    amt = _Book.cents(amount)
    if amt <= 0:
        return "Error: the order amount must be a positive dollar figure."
    yrs = int(subscription_years)
    if yrs not in (1, 2, 3):
        return "Error: subscription_years must be 1, 2 or 3."
    if checkout_method not in ("card", "paypal"):
        return "Error: checkout_method must be card or paypal."
    rows = ctx.find("ssl_holdings", certificate_id=sibling_certificate_id)
    if not rows:
        return f"Error: no certificate subscription {sibling_certificate_id}."
    sib = rows[0]
    today = ctx.now()[:10]
    end = _Book.add_years(today, yrs)
    paid_by = _Book.checkout(checkout_method)
    cid = ctx.make_id("ssl_", "second_key", customer_id, sibling_certificate_id, yrs, amt, today)
    ctx.create("ssl_holdings", cid, certificate_id=cid, customer_id=customer_id,
               variant_name=sib.get("variant_name"), status="pending_validation",
               common_name=sib.get("common_name"), extra_names=sib.get("extra_names"),
               subscription_years=int(subscription_years), subscription_start_date=today,
               subscription_end_date=end, cert_issued_date="", cert_expiry_date="", dcv_method=sib.get("dcv_method"),
               dcv_validated_date="", org_validated_date="", domain_id=sib.get("domain_id"),
               hosting_id=sib.get("hosting_id"), auto_renew=True, revocation_reason="none",
               opened_date=today, closed_date="")
    rid = ctx.make_id("sslc_", "purchase", cid, amt)
    ref = _Book.order_ref(rid)
    ctx.create("ssl_charges", rid, ssl_charge_id=rid, certificate_id=cid, customer_id=customer_id,
               event_type="ssl_purchase_charge", charge_type="new_subscription", amount=_Book.cents(amount),
               years=yrs, names_added=0, period_start=today, period_end=end, charge_date=today, order_ref=ref,
               payment_method=paid_by, original_ssl_charge_id=None, refund_destination="none")
    return (f"New subscription {cid} (pending_validation) from {today} to {end}; charge line {rid} "
            f"(order {ref}) paid {amt:.2f} USD by {paid_by} at checkout.")


@tool(owner="user", rw="write")
def add_certificate_name_7df48eab(ctx: ToolContext, certificate_id: str, checkout_method: str,
                                  amount: float) -> str:
    """Add, as the account holder at Harborline's secure checkout, one further name to a multi-domain
    certificate subscription and pay the charge the agent has quoted for it.

    One call bills one added-names line on the subscription (one name added, covering today to the
    subscription end date, paid with the card or PayPal account the holder enters at checkout, with a newly
    issued Harborline order number) and raises the subscription's count of extra names by one. The new name
    takes effect on the certificate's next free reissue, which this call does not record. The holder sees
    the new line in the certificate billing history and the higher name count on the subscription. The amount is billed exactly as given.

    Args:
        certificate_id: Id class — the reference number of the certificate subscription receiving the name,
            as the agent reads it out from the certificate subscription lookup.
        checkout_method: Enum class — how the holder pays at checkout: card when the holder enters a
            payment card at checkout; paypal when the holder pays with a PayPal account at checkout.
        amount: Fixed-format class — the charge quoted by the agent, written as USD, 2 decimal places,
            signed, and positive for this charge; any further decimals are rounded half up to the cent.

    Returns:
        A confirmation sentence naming the new added-names line's reference number (a text id), the order
        number (HL- followed by 8 digits), the amount billed in US dollars with two decimals, the payment
        method recorded (card or paypal), the covered period as two YYYY-MM-DD dates and the subscription's
        new count of extra names (an integer). The presence of the new name count means the name was added.
    """
    amt = _Book.cents(amount)
    if amt <= 0:
        return "Error: the charge must be a positive dollar figure."
    if checkout_method not in ("card", "paypal"):
        return "Error: checkout_method must be card or paypal."
    rows = ctx.find("ssl_holdings", certificate_id=certificate_id)
    if not rows:
        return f"Error: no certificate subscription {certificate_id}."
    sub = rows[0]
    today = ctx.now()[:10]
    end = str(sub.get("subscription_end_date"))[:10]
    count = int(sub.get("extra_names") or 0) + 1
    paid_by = _Book.checkout(checkout_method)
    rid = ctx.make_id("sslc_", "added_name", certificate_id, checkout_method, amt, today, count)
    ref = _Book.order_ref(rid)
    ctx.create("ssl_charges", rid, ssl_charge_id=rid, certificate_id=certificate_id,
               customer_id=sub.get("customer_id"), event_type="ssl_names_charge", charge_type="added_names",
               amount=_Book.cents(amount), years=0, names_added=1, period_start=today, period_end=end,
               charge_date=today, order_ref=ref, payment_method=paid_by, original_ssl_charge_id=None,
               refund_destination="none")
    ctx.update("ssl_holdings", certificate_id, extra_names=count)
    return (f"Added-names line {rid} (order {ref}) paid {amt:.2f} USD by {paid_by} at checkout for {today} to "
            f"{end}; the subscription now covers {count} extra names.")

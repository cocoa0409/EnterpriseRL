"""Hidden task tools of the companion_certificates_and_passes difficulty (Crestline Airways).

Each tool lands exactly one entry on the ledger of a companion certificate or pass. The amount is the
value the caller has already worked out; a tool never aggregates history, never judges eligibility or
ordering, and never refuses a call because some other entry is or is not on file.
"""

from erlbench import ToolContext, tool


@tool(owner="user", rw="write")
def pay_companion_reinstatement_fee_0c05ba56(ctx: ToolContext, companion_id: str, companion_ticket_number: str,
                                               amount: float) -> str:
    """The certificate or pass holder pays, in person, the reinstatement fee of a companion booking that was
    cancelled and whose companion trip came back to the certificate or pass. One call records one paid charge
    of component reinstatement fee, dated today, on that certificate's or pass's charge history, linked to the
    companion ticket of the cancelled booking; the holder's companion charges total rises by the amount paid.
    The holder sees the fee as paid, and the receipt below confirms the payment.

    Args:
        companion_id: Id class — reference number of the companion certificate or pass record the fee is paid
            on, as returned by the companion certificate and pass lookup before the call.
        companion_ticket_number: Fixed-format class — the companion's ticket number on the cancelled booking,
            13 digits beginning 419, digits only with no spaces, exactly as shown on that booking's entry in the
            companion trip and charge history.
        amount: Fixed-format class — the reinstatement fee being paid, in USD, a decimal number rounded to 2
            decimal places (cents), rounding half up; never negative.

    Returns:
        A dictionary receipt: charge_entry_id (string, reference number of the new paid charge), companion_id
        (string, the certificate or pass charged), companion_ticket_number (string, the 13-digit ticket the fee
        relates to), charge_component (string, always reinstatement_fee), amount_usd (number, USD with 2
        decimal places, the amount paid), entry_date (string, YYYY-MM-DD, today's business date) and status
        (string, payment_recorded when the payment is on file).
    """
    rid = ctx.make_id("cmpchg_", companion_id, companion_ticket_number, amount)
    value = round(float(amount), 2)
    holding = ctx.find("companion_holdings", companion_id=companion_id)
    ctx.create("companion_ledger", rid, companion_entry_id=rid, companion_id=companion_id,
               customer_id=holding[0].get("customer_id") if holding else None,
               event_type="companion_fare_charge", entry_date=ctx.now()[:10], trips=0, amount=value,
               charge_component="reinstatement_fee", companion_ticket_number=companion_ticket_number)
    return str({"charge_entry_id": rid, "companion_id": companion_id,
                "companion_ticket_number": companion_ticket_number, "charge_component": "reinstatement_fee",
                "amount_usd": value, "entry_date": ctx.now()[:10], "status": "payment_recorded"})


@tool(owner="agent", rw="write")
def refund_companion_fare_charge_1d800070(ctx: ToolContext, companion_id: str, reversed_entry_id: str,
                                            amount: float) -> str:
    """Refunds to the holder the companion fare of a cancelled companion booking on a certificate or pass. One
    call records one refund of component companion fare, dated today, on that certificate's or pass's charge
    history, naming the companion fare charge it refunds and carrying that charge's companion ticket number;
    the holder's companion charges total falls by the amount refunded. The holder sees the refund on the
    certificate or pass, and the receipt below confirms it was recorded.

    Args:
        companion_id: Id class — reference number of the companion certificate or pass record the refund is
            recorded on, as returned by the companion certificate and pass lookup before the call.
        reversed_entry_id: Id class — reference number of the companion fare charge entry being refunded, as
            returned by the companion trip and charge history lookup before the call.
        amount: Fixed-format class — the companion fare amount refunded, in USD, a decimal number rounded to 2
            decimal places (cents), rounding half up; never negative.

    Returns:
        A dictionary receipt: refund_entry_id (string, reference number of the new refund), companion_id
        (string, the certificate or pass), refunded_charge_entry_id (string, the charge refunded),
        charge_component (string, always companion_fare), amount_usd (number, USD with 2 decimal places),
        entry_date (string, YYYY-MM-DD, today's business date) and status (string, refund_recorded when the
        refund is on file).
    """
    rid = ctx.make_id("cmpref_", companion_id, reversed_entry_id, amount)
    value = round(float(amount), 2)
    holding = ctx.find("companion_holdings", companion_id=companion_id)
    charge = ctx.find("companion_ledger", companion_entry_id=reversed_entry_id)
    ctx.create("companion_ledger", rid, companion_entry_id=rid, companion_id=companion_id,
               customer_id=holding[0].get("customer_id") if holding else None,
               event_type="companion_fare_refund", entry_date=ctx.now()[:10], trips=0, amount=value,
               charge_component="companion_fare",
               companion_ticket_number=charge[0].get("companion_ticket_number") if charge else None,
               reversed_entry_id=reversed_entry_id)
    return str({"refund_entry_id": rid, "companion_id": companion_id,
                "refunded_charge_entry_id": reversed_entry_id, "charge_component": "companion_fare",
                "amount_usd": value, "entry_date": ctx.now()[:10], "status": "refund_recorded"})


@tool(owner="agent", rw="write")
def refund_companion_hawaii_surcharge_2c74daac(ctx: ToolContext, companion_id: str, reversed_entry_id: str,
                                                 amount: float) -> str:
    """Refunds to the holder the Hawaii surcharge of a cancelled companion booking on a certificate or pass.
    One call records one refund of component Hawaii surcharge, dated today, on that certificate's or pass's
    charge history, naming the Hawaii surcharge charge it refunds and carrying that charge's companion ticket
    number; the holder's companion charges total falls by the amount refunded. The holder sees the refund on
    the certificate or pass, and the receipt below confirms it was recorded.

    Args:
        companion_id: Id class — reference number of the companion certificate or pass record the refund is
            recorded on, as returned by the companion certificate and pass lookup before the call.
        reversed_entry_id: Id class — reference number of the Hawaii surcharge charge entry being refunded, as
            returned by the companion trip and charge history lookup before the call.
        amount: Fixed-format class — the Hawaii surcharge amount refunded, in USD, a decimal number rounded to
            2 decimal places (cents), rounding half up; never negative.

    Returns:
        A dictionary receipt: refund_entry_id (string, reference number of the new refund), companion_id
        (string, the certificate or pass), refunded_charge_entry_id (string, the charge refunded),
        charge_component (string, always hawaii_surcharge), amount_usd (number, USD with 2 decimal places),
        entry_date (string, YYYY-MM-DD, today's business date) and status (string, refund_recorded when the
        refund is on file).
    """
    rid = ctx.make_id("cmpref_", companion_id, reversed_entry_id, amount)
    value = round(float(amount), 2)
    holding = ctx.find("companion_holdings", companion_id=companion_id)
    charge = ctx.find("companion_ledger", companion_entry_id=reversed_entry_id)
    ctx.create("companion_ledger", rid, companion_entry_id=rid, companion_id=companion_id,
               customer_id=holding[0].get("customer_id") if holding else None,
               event_type="companion_fare_refund", entry_date=ctx.now()[:10], trips=0, amount=value,
               charge_component="hawaii_surcharge",
               companion_ticket_number=charge[0].get("companion_ticket_number") if charge else None,
               reversed_entry_id=reversed_entry_id)
    return str({"refund_entry_id": rid, "companion_id": companion_id,
                "refunded_charge_entry_id": reversed_entry_id, "charge_component": "hawaii_surcharge",
                "amount_usd": value, "entry_date": ctx.now()[:10], "status": "refund_recorded"})


@tool(owner="agent", rw="write")
def refund_companion_taxes_and_fees_22c15e93(ctx: ToolContext, companion_id: str, reversed_entry_id: str,
                                               amount: float) -> str:
    """Refunds to the holder the taxes and fees of a cancelled companion booking on a certificate or pass. One
    call records one refund of component taxes and fees, dated today, on that certificate's or pass's charge
    history, naming the taxes-and-fees charge it refunds and carrying that charge's companion ticket number;
    the holder's companion charges total falls by the amount refunded. The holder sees the refund on the
    certificate or pass, and the receipt below confirms it was recorded.

    Args:
        companion_id: Id class — reference number of the companion certificate or pass record the refund is
            recorded on, as returned by the companion certificate and pass lookup before the call.
        reversed_entry_id: Id class — reference number of the taxes-and-fees charge entry being refunded, as
            returned by the companion trip and charge history lookup before the call.
        amount: Fixed-format class — the taxes-and-fees amount refunded, in USD, a decimal number rounded to 2
            decimal places (cents), rounding half up; never negative.

    Returns:
        A dictionary receipt: refund_entry_id (string, reference number of the new refund), companion_id
        (string, the certificate or pass), refunded_charge_entry_id (string, the charge refunded),
        charge_component (string, always taxes_and_fees), amount_usd (number, USD with 2 decimal places),
        entry_date (string, YYYY-MM-DD, today's business date) and status (string, refund_recorded when the
        refund is on file).
    """
    rid = ctx.make_id("cmpref_", companion_id, reversed_entry_id, amount)
    value = round(float(amount), 2)
    holding = ctx.find("companion_holdings", companion_id=companion_id)
    charge = ctx.find("companion_ledger", companion_entry_id=reversed_entry_id)
    ctx.create("companion_ledger", rid, companion_entry_id=rid, companion_id=companion_id,
               customer_id=holding[0].get("customer_id") if holding else None,
               event_type="companion_fare_refund", entry_date=ctx.now()[:10], trips=0, amount=value,
               charge_component="taxes_and_fees",
               companion_ticket_number=charge[0].get("companion_ticket_number") if charge else None,
               reversed_entry_id=reversed_entry_id)
    return str({"refund_entry_id": rid, "companion_id": companion_id,
                "refunded_charge_entry_id": reversed_entry_id, "charge_component": "taxes_and_fees",
                "amount_usd": value, "entry_date": ctx.now()[:10], "status": "refund_recorded"})


@tool(owner="user", rw="write")
def pay_companion_fare_charge_130546ae(ctx: ToolContext, companion_id: str, companion_ticket_number: str,
                                        amount: float) -> str:
    """The certificate or pass holder pays, in person, the companion fare of a companion booking. One call
    records one paid charge of component companion fare, dated today, on that certificate's or pass's charge
    history, linked to the companion ticket of the booking; the holder's companion charges total rises by the
    amount paid. The holder sees the companion fare as paid, and the receipt below confirms the payment.

    Args:
        companion_id: Id class — reference number of the companion certificate or pass record the booking was
            made on, as returned by the companion certificate and pass lookup before the call.
        companion_ticket_number: Fixed-format class — the companion's ticket number on the booking, 13 digits
            beginning 419, digits only with no spaces, exactly as shown on that booking's entry in the companion
            trip and charge history.
        amount: Fixed-format class — the companion fare being paid, in USD, a decimal number rounded to 2
            decimal places (cents), rounding half up; never negative.

    Returns:
        A dictionary receipt: charge_entry_id (string, reference number of the new paid charge), companion_id
        (string, the certificate or pass charged), companion_ticket_number (string, the 13-digit ticket the
        charge relates to), charge_component (string, always companion_fare), amount_usd (number, USD with 2
        decimal places, the amount paid), entry_date (string, YYYY-MM-DD, today's business date) and status
        (string, payment_recorded when the payment is on file).
    """
    rid = ctx.make_id("cmpchg_", companion_id, companion_ticket_number, amount)
    value = round(float(amount), 2)
    holding = ctx.find("companion_holdings", companion_id=companion_id)
    ctx.create("companion_ledger", rid, companion_entry_id=rid, companion_id=companion_id,
               customer_id=holding[0].get("customer_id") if holding else None,
               event_type="companion_fare_charge", entry_date=ctx.now()[:10], trips=0, amount=value,
               charge_component="companion_fare", companion_ticket_number=companion_ticket_number)
    return str({"charge_entry_id": rid, "companion_id": companion_id,
                "companion_ticket_number": companion_ticket_number, "charge_component": "companion_fare",
                "amount_usd": value, "entry_date": ctx.now()[:10], "status": "payment_recorded"})


@tool(owner="user", rw="write")
def pay_companion_phone_booking_fee_ff06513e(ctx: ToolContext, companion_id: str, companion_ticket_number: str,
                                              amount: float) -> str:
    """The certificate or pass holder pays, in person, the phone booking fee of a companion booking made through
    the reservations call center. One call records one paid charge of component phone booking fee, dated today,
    on that certificate's or pass's charge history, linked to the companion ticket of the booking; the amount may
    be zero, in which case the fee is recorded as settled at zero. The holder's companion charges total rises by
    the amount paid, and the receipt below confirms the payment.

    Args:
        companion_id: Id class — reference number of the companion certificate or pass record the booking was
            made on, as returned by the companion certificate and pass lookup before the call.
        companion_ticket_number: Fixed-format class — the companion's ticket number on the booking, 13 digits
            beginning 419, digits only with no spaces, exactly as shown on that booking's entry in the companion
            trip and charge history.
        amount: Fixed-format class — the phone booking fee being paid, in USD, a decimal number rounded to 2
            decimal places (cents), rounding half up; zero allowed, never negative.

    Returns:
        A dictionary receipt: charge_entry_id (string, reference number of the new paid charge), companion_id
        (string, the certificate or pass charged), companion_ticket_number (string, the 13-digit ticket the
        charge relates to), charge_component (string, always phone_booking_fee), amount_usd (number, USD with 2
        decimal places, the amount paid), entry_date (string, YYYY-MM-DD, today's business date) and status
        (string, payment_recorded when the payment is on file).
    """
    rid = ctx.make_id("cmpchg_", companion_id, companion_ticket_number, amount)
    value = round(float(amount), 2)
    holding = ctx.find("companion_holdings", companion_id=companion_id)
    ctx.create("companion_ledger", rid, companion_entry_id=rid, companion_id=companion_id,
               customer_id=holding[0].get("customer_id") if holding else None,
               event_type="companion_fare_charge", entry_date=ctx.now()[:10], trips=0, amount=value,
               charge_component="phone_booking_fee", companion_ticket_number=companion_ticket_number)
    return str({"charge_entry_id": rid, "companion_id": companion_id,
                "companion_ticket_number": companion_ticket_number, "charge_component": "phone_booking_fee",
                "amount_usd": value, "entry_date": ctx.now()[:10], "status": "payment_recorded"})


@tool(owner="user", rw="write")
def pay_companion_taxes_and_fees_93ccd8f8(ctx: ToolContext, companion_id: str, companion_ticket_number: str,
                                           amount: float) -> str:
    """The certificate or pass holder pays, in person, the companion's taxes and fees of a companion booking.
    One call records one paid charge of component taxes and fees, dated today, on that certificate's or pass's
    charge history, linked to the companion ticket of the booking; the holder's companion charges total rises by
    the amount paid. The holder sees the taxes and fees as paid, and the receipt below confirms the payment.

    Args:
        companion_id: Id class — reference number of the companion certificate or pass record the booking was
            made on, as returned by the companion certificate and pass lookup before the call.
        companion_ticket_number: Fixed-format class — the companion's ticket number on the booking, 13 digits
            beginning 419, digits only with no spaces, exactly as shown on that booking's entry in the companion
            trip and charge history.
        amount: Fixed-format class — the taxes and fees being paid, in USD, a decimal number rounded to 2
            decimal places (cents), rounding half up; never negative.

    Returns:
        A dictionary receipt: charge_entry_id (string, reference number of the new paid charge), companion_id
        (string, the certificate or pass charged), companion_ticket_number (string, the 13-digit ticket the
        charge relates to), charge_component (string, always taxes_and_fees), amount_usd (number, USD with 2
        decimal places, the amount paid), entry_date (string, YYYY-MM-DD, today's business date) and status
        (string, payment_recorded when the payment is on file).
    """
    rid = ctx.make_id("cmpchg_", companion_id, companion_ticket_number, amount)
    value = round(float(amount), 2)
    holding = ctx.find("companion_holdings", companion_id=companion_id)
    ctx.create("companion_ledger", rid, companion_entry_id=rid, companion_id=companion_id,
               customer_id=holding[0].get("customer_id") if holding else None,
               event_type="companion_fare_charge", entry_date=ctx.now()[:10], trips=0, amount=value,
               charge_component="taxes_and_fees", companion_ticket_number=companion_ticket_number)
    return str({"charge_entry_id": rid, "companion_id": companion_id,
                "companion_ticket_number": companion_ticket_number, "charge_component": "taxes_and_fees",
                "amount_usd": value, "entry_date": ctx.now()[:10], "status": "payment_recorded"})


@tool(owner="agent", rw="write")
def refund_companion_phone_booking_fee_90a9c390(ctx: ToolContext, companion_id: str, reversed_entry_id: str,
                                                 amount: float) -> str:
    """Refunds to the holder the phone booking fee of a companion booking on a certificate or pass. One call
    records one refund of component phone booking fee, dated today, on that certificate's or pass's charge
    history, naming the phone booking fee charge it refunds and carrying that charge's companion ticket number;
    the holder's companion charges total falls by the amount refunded. The holder sees the refund on the
    certificate or pass, and the receipt below confirms it was recorded.

    Args:
        companion_id: Id class — reference number of the companion certificate or pass record the refund is
            recorded on, as returned by the companion certificate and pass lookup before the call.
        reversed_entry_id: Id class — reference number of the phone booking fee charge entry being refunded, as
            returned by the companion trip and charge history lookup before the call.
        amount: Fixed-format class — the phone booking fee amount refunded, in USD, a decimal number rounded to
            2 decimal places (cents), rounding half up; never negative.

    Returns:
        A dictionary receipt: refund_entry_id (string, reference number of the new refund), companion_id
        (string, the certificate or pass), refunded_charge_entry_id (string, the charge refunded),
        charge_component (string, always phone_booking_fee), amount_usd (number, USD with 2 decimal places),
        entry_date (string, YYYY-MM-DD, today's business date) and status (string, refund_recorded when the
        refund is on file).
    """
    rid = ctx.make_id("cmpref_", companion_id, reversed_entry_id, amount)
    value = round(float(amount), 2)
    holding = ctx.find("companion_holdings", companion_id=companion_id)
    charge = ctx.find("companion_ledger", companion_entry_id=reversed_entry_id)
    ctx.create("companion_ledger", rid, companion_entry_id=rid, companion_id=companion_id,
               customer_id=holding[0].get("customer_id") if holding else None,
               event_type="companion_fare_refund", entry_date=ctx.now()[:10], trips=0, amount=value,
               charge_component="phone_booking_fee",
               companion_ticket_number=charge[0].get("companion_ticket_number") if charge else None,
               reversed_entry_id=reversed_entry_id)
    return str({"refund_entry_id": rid, "companion_id": companion_id,
                "refunded_charge_entry_id": reversed_entry_id, "charge_component": "phone_booking_fee",
                "amount_usd": value, "entry_date": ctx.now()[:10], "status": "refund_recorded"})

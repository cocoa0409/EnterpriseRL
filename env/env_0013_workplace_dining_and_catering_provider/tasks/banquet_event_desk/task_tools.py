"""Hidden task tools for the banquet_event_desk difficulty.

Each tool performs one atomic write against the private event and banquet services records.
None of them aggregates history, judges eligibility, or refuses on a business ground: the
desk agent reads the agreement, the event ledger and the published rules, works the figure
out, and passes it in.
"""

from erlbench import ToolContext, tool


@tool(owner="user", rw="write")
def confirm_event_cancellation_0abc9941(ctx: ToolContext, banquet_agreement_id: str, customer_id: str,
                                        booking_reference: str, event_date: str,
                                        contracted_value_usd: float,
                                        guaranteed_headcount: int) -> str:
    """The client calls off a confirmed event themselves and puts their written notice on the
    record. One call registers the cancellation of a single booking against the event services
    agreement it sits under: a cancellation entry is written into that agreement's event ledger
    carrying the booking it concerns, the day the event was to have been held, the guest count
    standing on the booking when notice was given, the contracted event value standing at that
    day, and today as the day written notice was given. The client can see the cancelled booking, its notice day and the contracted value recorded on it on the agreement's event ledger straight away.

    Args:
        banquet_agreement_id: Id class — the reference number of the private event and banquet services agreement the booking sits under, as the agreement lookup returns it.
        customer_id: Id class — the reference number of the client organisation profile holding that agreement, as the profile lookup returns it.
        booking_reference: Fixed-format class — the single event booking being called off, written as BQ- followed by 6 digits, exactly as it stands on the booking entry in the event ledger.
        event_date: Fixed-format class — the day the event was to have been held, written as YYYY-MM-DD in the venue's own local calendar, with no time part.
        contracted_value_usd: Fixed-format class — the contracted event value standing against the booking at the day notice is given, in USD, to 2 decimal places, rounded to the nearest cent at the moment it is recorded, a half-cent going to the nearer even cent, and never left blank.
        guaranteed_headcount: Fixed-format class — the guest count standing on the booking at the day notice is given, as a whole number of guests, with no decimal part.

    Returns:
        A confirmation line of text. It names the cancellation entry reference minted for this
        registration, the booking reference it was written against, the contracted event value
        recorded on it in USD to two decimal places, and the day written notice was taken as
        given, written as YYYY-MM-DD. The line being returned is what indicates the cancellation
        was registered; the entry is then visible on the agreement's event ledger.
    """
    rid = ctx.make_id("bqcan_", banquet_agreement_id, customer_id, booking_reference, event_date,
                      contracted_value_usd, guaranteed_headcount)
    notice_day = ctx.now()[:10]
    ctx.create("banquet_ledger", rid,
               banquet_ledger_id=rid,
               banquet_agreement_id=banquet_agreement_id,
               customer_id=customer_id,
               event_type="banquet_booking_cancelled",
               booking_reference=booking_reference,
               charge_code="cancellation_fee",
               amount_usd=round(float(contracted_value_usd), 2),
               posted_date=notice_day,
               event_date=event_date,
               notice_given_date=notice_day,
               guaranteed_headcount=int(guaranteed_headcount),
               payment_channel="not_applicable")
    return (f"Cancellation {rid} registered for booking {booking_reference}: contracted event value "
            f"{round(float(contracted_value_usd), 2):.2f} USD standing at notice, written notice taken "
            f"as given on {notice_day}.")


@tool(owner="agent", rw="write")
def post_cancellation_charge_5262dfa3(ctx: ToolContext, banquet_agreement_id: str, customer_id: str,
                                      booking_reference: str, event_date: str,
                                      notice_given_date: str,
                                      cancellation_charge_usd: float) -> str:
    """Raise the charge that falls due on an event the client has called off, against the private
    event and banquet services agreement the booking sits under. One call writes a single
    cancellation charge entry into that agreement's event ledger, carrying the booking it answers,
    the day the cancelled event was to have been held, the day written notice was given, the
    amount charged, and today as the day it was raised; a bill reference is minted for the charge and printed on it. The client sees the charge and its bill
    reference on the agreement's event ledger, and it is the amount their account now carries for
    that cancelled booking.

    Args:
        banquet_agreement_id: Id class — the reference number of the private event and banquet services agreement the cancelled booking sits under, as the agreement lookup returns it.
        customer_id: Id class — the reference number of the client organisation profile charged, as the profile lookup returns it.
        booking_reference: Fixed-format class — the cancelled event booking the charge answers, written as BQ- followed by 6 digits, exactly as it stands on the cancellation entry in the event ledger.
        event_date: Fixed-format class — the day the cancelled event was to have been held, written as YYYY-MM-DD in the venue's own local calendar, with no time part.
        notice_given_date: Fixed-format class — the day the client gave written notice of the cancellation, written as YYYY-MM-DD in the venue's own local calendar, with no time part.
        cancellation_charge_usd: Fixed-format class — the amount charged for the cancelled booking, in USD, to 2 decimal places, rounded to the nearest cent at the moment it is recorded, a half-cent going to the nearer even cent, and never left blank.

    Returns:
        A confirmation line of text. It names the charge entry reference minted for the posting,
        the bill reference the charge sits on, written as INV-BQ- followed by 6 digits, the booking
        reference charged, the amount raised in USD to two decimal places, and the day it was
        raised, written as YYYY-MM-DD. The line being returned is what indicates the charge was
        raised; the entry is then visible on the agreement's event ledger.
    """
    rid = ctx.make_id("bqcfe_", banquet_agreement_id, customer_id, booking_reference, event_date,
                      notice_given_date, cancellation_charge_usd)
    bill_reference = "INV-BQ-" + str(int(ctx.make_id("", booking_reference, event_date)[:8], 16) % 1000000).zfill(6)
    ctx.create("banquet_ledger", rid,
               banquet_ledger_id=rid,
               banquet_agreement_id=banquet_agreement_id,
               customer_id=customer_id,
               event_type="banquet_cancellation_charge_posted",
               booking_reference=booking_reference,
               charge_code="cancellation_fee",
               amount_usd=round(float(cancellation_charge_usd), 2),
               posted_date=ctx.now()[:10],
               event_date=event_date,
               notice_given_date=notice_given_date,
               invoice_reference=bill_reference,
               payment_channel="not_applicable")
    return (f"Cancellation charge {rid} raised on booking {booking_reference} for "
            f"{round(float(cancellation_charge_usd), 2):.2f} USD, carried on bill {bill_reference}, "
            f"raised on {ctx.now()[:10]}.")


@tool(owner="agent", rw="write")
def raise_event_final_bill_fa928380(ctx: ToolContext, banquet_agreement_id: str, customer_id: str,
                                    booking_reference: str, event_date: str,
                                    invoice_amount_usd: float) -> str:
    """Raise the final bill for an event that has been held, against the private event and banquet
    services agreement the booking sits under. One call writes a single invoice entry into that
    agreement's event ledger, carrying the booking billed, the day the event was held, the amount
    billed, and today as the day the bill was raised; a bill reference is minted for it and printed on the bill itself. The client sees the bill and its reference
    on the agreement's event ledger, and the amount billed is what their account now carries for
    that event.

    Args:
        banquet_agreement_id: Id class — the reference number of the private event and banquet services agreement the booking sits under, as the agreement lookup returns it.
        customer_id: Id class — the reference number of the client organisation profile billed, as the profile lookup returns it.
        booking_reference: Fixed-format class — the single event booking being billed, written as BQ- followed by 6 digits, exactly as it stands on the booking entry in the event ledger.
        event_date: Fixed-format class — the day the event was held, written as YYYY-MM-DD in the venue's own local calendar, with no time part.
        invoice_amount_usd: Fixed-format class — the amount billed for the event, in USD, to 2 decimal places, rounded to the nearest cent at the moment it is recorded, a half-cent going to the nearer even cent, and never left blank.

    Returns:
        A confirmation line of text. It names the invoice entry reference minted for the posting,
        the bill reference printed on it, written as INV-BQ- followed by 6 digits,
        the booking billed, the amount billed in USD to two decimal places, and the day the bill was
        raised, written as YYYY-MM-DD. The line being returned is what indicates the bill was
        raised; the entry is then visible on the agreement's event ledger.
    """
    rid = ctx.make_id("bqinv_", banquet_agreement_id, customer_id, booking_reference, event_date,
                      invoice_amount_usd)
    bill_reference = "INV-BQ-" + str(int(ctx.make_id("", booking_reference, event_date)[:8], 16) % 1000000).zfill(6)
    ctx.create("banquet_ledger", rid,
               banquet_ledger_id=rid,
               banquet_agreement_id=banquet_agreement_id,
               customer_id=customer_id,
               event_type="banquet_event_invoiced",
               booking_reference=booking_reference,
               charge_code="invoice",
               amount_usd=round(float(invoice_amount_usd), 2),
               posted_date=ctx.now()[:10],
               event_date=event_date,
               invoice_reference=bill_reference,
               payment_channel="not_applicable")
    return (f"Final bill {rid} raised on booking {booking_reference} for "
            f"{round(float(invoice_amount_usd), 2):.2f} USD, carried on bill {bill_reference}, "
            f"raised on {ctx.now()[:10]}.")


@tool(owner="user", rw="write")
def settle_event_bill_79f0663f(ctx: ToolContext, banquet_agreement_id: str, customer_id: str,
                               booking_reference: str, invoice_reference: str,
                               payment_amount_usd: float, payment_channel: str) -> str:
    """The client settles an event bill themselves. One call records a single payment entry into
    the event ledger of the private event and banquet services agreement the bill sits under,
    carrying the bill being settled, the booking it concerns, the amount paid, how the money moved,
    and today as the day the money cleared. The client can see the payment against that bill on the
    agreement's event ledger straight away, and the account's unsettled event balance falls by what
    was paid.

    Args:
        banquet_agreement_id: Id class — the reference number of the private event and banquet services agreement the bill sits under, as the agreement lookup returns it.
        customer_id: Id class — the reference number of the client organisation profile paying, as the profile lookup returns it.
        booking_reference: Fixed-format class — the event booking the payment is allocated to, written as BQ- followed by 6 digits, exactly as it stands on the booking entry in the event ledger.
        invoice_reference: Fixed-format class — the single bill being settled, written as INV-BQ- followed by 6 digits, exactly as it is printed on that bill.
        payment_amount_usd: Fixed-format class — the amount the client pays, in USD, to 2 decimal places, rounded to the nearest cent at the moment it is recorded, a half-cent going to the nearer even cent, and never left blank.
        payment_channel: Enum class — how the money moves, one of exactly these values. ach where the client sends the money by bank transfer from their own account. check where the client posts a cheque drawn on the client organisation. corporate_card where the client puts the payment on a company card over the telephone. internal_transfer where the money is moved between balances already held on the client's own records rather than received from outside. not_applicable where no money changes hands at all.

    Returns:
        A confirmation line of text. It names the payment entry reference minted for the
        settlement, the bill reference settled, the booking it was allocated to, the amount received
        in USD to two decimal places, how the money moved, and the day it cleared, written as
        YYYY-MM-DD. The line being returned is what indicates the payment was recorded; the entry is
        then visible on the agreement's event ledger.
    """
    rid = ctx.make_id("bqpay_", banquet_agreement_id, customer_id, booking_reference,
                      invoice_reference, payment_amount_usd, payment_channel)
    ctx.create("banquet_ledger", rid,
               banquet_ledger_id=rid,
               banquet_agreement_id=banquet_agreement_id,
               customer_id=customer_id,
               event_type="banquet_payment_posted",
               booking_reference=booking_reference,
               charge_code="payment",
               amount_usd=round(float(payment_amount_usd), 2),
               posted_date=ctx.now()[:10],
               invoice_reference=invoice_reference,
               payment_channel=payment_channel)
    return (f"Payment {rid} recorded against bill {invoice_reference} on booking {booking_reference}: "
            f"{round(float(payment_amount_usd), 2):.2f} USD received by {payment_channel} on "
            f"{ctx.now()[:10]}.")

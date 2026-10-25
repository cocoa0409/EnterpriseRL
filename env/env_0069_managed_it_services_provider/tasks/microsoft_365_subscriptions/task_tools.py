"""Hidden task tools for the microsoft_365_subscriptions difficulty (Stratton Bay Technology Partners).

Each tool performs one atomic business write on a Microsoft 365 subscription that Stratton Bay resells.
The agent works out every amount from the published policy and the records; the tools only land it.
"""

from erlbench import ToolContext, tool


class _InvoiceNumbers:
    """Deterministic new invoice numbers for entries billed on their own invoice."""

    @staticmethod
    def issue(ctx: ToolContext, *parts) -> str:
        digits = int(ctx.make_id("", *parts)[-10:], 16) % 1000000
        return f"INV-{digits:06d}"


@tool(owner="agent", rw="write")
def post_reduction_credit_23f8ed2c(ctx: ToolContext, licensing_subscription_id: str,
                                   licensing_license_change_id: str, invoice_number: str,
                                   cycle_start_date: str, amount_usd: float) -> str:
    """Post the credit owed to a client for licenses removed from a Microsoft 365 subscription by an
    in-window reduction. One call books one credit entry on the subscription's billing ledger, linked to
    the reduction it credits and applied to the invoice named, and lowers the balance the client owes on
    the subscription by the amount credited. The client sees the credit on that invoice. The receipt
    returns the new ledger entry reference, the invoice credited, the amount and the new balance.

    Args:
        licensing_subscription_id: Id class — reference number of the Microsoft 365 subscription that
            received the reduction, as returned by the subscription lookup.
        licensing_license_change_id: Id class — reference number of the in-window reduction being
            credited, as returned by the license change lookup.
        invoice_number: Fixed-format class — the invoice the credit is applied to, written as INV- followed
            by 6 digits exactly as it appears on the billing ledger.
        cycle_start_date: Fixed-format class — the first day of the billing cycle the credit relates to, written
            YYYY-MM-DD exactly as the cycle start appears on the billing ledger.
        amount_usd: Fixed-format class — the credit amount in USD, a positive number to 2 decimal places,
            rounded half up to the cent.

    Returns:
        A confirmation sentence naming the credit entry reference (prefix lcr_), the invoice credited
        (INV- followed by 6 digits), the credited amount in USD to 2 decimal places and the subscription's
        new balance owed in USD to 2 decimal places; its presence means the credit is posted.
    """
    sub = ctx.find("licensing_subscriptions", licensing_subscription_id=licensing_subscription_id)[0]
    rid = ctx.make_id("lcr_", licensing_subscription_id, licensing_license_change_id, invoice_number, cycle_start_date,
                      amount_usd)
    amount = round(float(amount_usd), 2)
    ctx.create("licensing_billing", rid, licensing_billing_entry_id=rid,
               licensing_subscription_id=licensing_subscription_id, customer_id=sub["customer_id"],
               event_type="licensing_refund_credit", amount_usd=amount, invoice_number=invoice_number,
               cycle_start_date=cycle_start_date, billing_period="", posted_date=ctx.now()[:10],
               charge_reason="in_window_reduction", licensing_license_change_id=licensing_license_change_id,
               payment_reference="")
    balance = round(float(sub["balance_due_usd"]) - amount, 2)
    ctx.update("licensing_subscriptions", licensing_subscription_id, balance_due_usd=balance)
    return (f"Credit {rid} of {amount:.2f} USD applied to {invoice_number}; "
            f"balance owed on the subscription is now {balance:.2f} USD.")


@tool(owner="agent", rw="write")
def assess_late_charge_e02563fc(ctx: ToolContext, licensing_subscription_id: str, invoice_number: str,
                                amount_usd: float) -> str:
    """Assess this calendar month's late charge on a past-due invoice of a Microsoft 365 subscription. One
    call books one late-charge entry for the current month against the invoice named and raises the
    balance the client owes on the subscription by that amount. The client sees the late charge on the
    invoice. The receipt returns the new ledger entry reference, the invoice, the month assessed, the
    amount and the new balance.

    Args:
        licensing_subscription_id: Id class — reference number of the Microsoft 365 subscription whose
            invoice is past due, as returned by the subscription lookup.
        invoice_number: Fixed-format class — the past-due invoice, written as INV- followed by 6 digits
            exactly as it appears on the billing ledger.
        amount_usd: Fixed-format class — the late charge in USD, a positive number to 2 decimal places,
            rounded half up to the cent.

    Returns:
        A confirmation sentence naming the late-charge entry reference (prefix llc_), the invoice
        (INV- followed by 6 digits), the month assessed (YYYY-MM), the amount in USD to 2 decimal places
        and the subscription's new balance owed in USD to 2 decimal places; its presence means the late
        charge is assessed.
    """
    sub = ctx.find("licensing_subscriptions", licensing_subscription_id=licensing_subscription_id)[0]
    rid = ctx.make_id("llc_", licensing_subscription_id, invoice_number, amount_usd)
    amount = round(float(amount_usd), 2)
    month = ctx.now()[:7]
    ctx.create("licensing_billing", rid, licensing_billing_entry_id=rid,
               licensing_subscription_id=licensing_subscription_id, customer_id=sub["customer_id"],
               event_type="licensing_late_fee", amount_usd=amount, invoice_number=invoice_number,
               cycle_start_date="", billing_period=month, posted_date=ctx.now()[:10],
               charge_reason="not_applicable", payment_reference="")
    balance = round(float(sub["balance_due_usd"]) + amount, 2)
    ctx.update("licensing_subscriptions", licensing_subscription_id, balance_due_usd=balance)
    return (f"Late charge {rid} of {amount:.2f} USD assessed on {invoice_number} for {month}; "
            f"balance owed on the subscription is now {balance:.2f} USD.")


@tool(owner="user", rw="write")
def pay_arrangement_instalment_a0d5f2e9(ctx: ToolContext, licensing_subscription_id: str,
                                        invoice_number: str, amount_usd: float) -> str:
    """The client's authorized contact pays, by card, the instalment due today under a payment arrangement
    for a past-due Microsoft 365 subscription balance. One call books one payment entry applied to the
    invoice named and lowers the balance the client owes on the subscription by the amount paid; the
    card authorisation reference is issued by this payment. The receipt returns the payment entry, the
    card authorisation reference, the invoice paid, the amount and the balance still owed.

    Args:
        licensing_subscription_id: Id class — reference number of the Microsoft 365 subscription the
            arrangement covers, as given to the client by the service desk from the subscription lookup.
        invoice_number: Fixed-format class — the past-due invoice the instalment is applied to, written as
            INV- followed by 6 digits exactly as the service desk reads it from the billing ledger.
        amount_usd: Fixed-format class — the instalment paid today in USD, a positive number to 2 decimal
            places, rounded half up to the cent.

    Returns:
        A confirmation sentence naming the payment entry reference (prefix lpy_), the card authorisation
        reference (CARD- followed by 8 characters), the invoice paid (INV- followed by 6 digits), the
        amount paid in USD to 2 decimal places and the balance still owed on the subscription in USD to
        2 decimal places; its presence means the instalment is paid.
    """
    sub = ctx.find("licensing_subscriptions", licensing_subscription_id=licensing_subscription_id)[0]
    rid = ctx.make_id("lpy_", licensing_subscription_id, invoice_number, amount_usd)
    auth = "CARD-" + ctx.make_id("", licensing_subscription_id, invoice_number, amount_usd)[-8:].upper()
    amount = round(float(amount_usd), 2)
    ctx.create("licensing_billing", rid, licensing_billing_entry_id=rid,
               licensing_subscription_id=licensing_subscription_id, customer_id=sub["customer_id"],
               event_type="licensing_payment", amount_usd=amount, invoice_number=invoice_number,
               cycle_start_date="", billing_period="", posted_date=ctx.now()[:10],
               charge_reason="not_applicable", payment_reference=auth)
    balance = round(float(sub["balance_due_usd"]) - amount, 2)
    ctx.update("licensing_subscriptions", licensing_subscription_id, balance_due_usd=balance)
    return (f"Payment {rid} ({auth}) of {amount:.2f} USD applied to {invoice_number}; "
            f"{balance:.2f} USD remains owed on the subscription.")


@tool(owner="agent", rw="write")
def post_admin_fee_5104ae31(ctx: ToolContext, licensing_subscription_id: str, billing_period: str,
                            amount_usd: float) -> str:
    """Invoice Stratton Bay's license administration fee for one calendar month on a Microsoft 365
    subscription. One call books one administration-fee entry for the month named on a new invoice and
    raises the balance the client owes on the subscription by that amount. The client sees the fee on the
    new invoice. The receipt returns the ledger entry reference, the new invoice number, the month, the
    amount and the new balance.

    Args:
        licensing_subscription_id: Id class — reference number of the Microsoft 365 subscription the fee
            is billed on, as returned by the subscription lookup.
        billing_period: Fixed-format class — the calendar month the fee is for, written YYYY-MM.
        amount_usd: Fixed-format class — the administration fee in USD, a positive number to 2 decimal
            places, rounded half up to the cent.

    Returns:
        A confirmation sentence naming the fee entry reference (prefix laf_), the new invoice
        (INV- followed by 6 digits), the month (YYYY-MM), the amount in USD to 2 decimal places and the
        subscription's new balance owed in USD to 2 decimal places; its presence means the fee is invoiced.
    """
    sub = ctx.find("licensing_subscriptions", licensing_subscription_id=licensing_subscription_id)[0]
    rid = ctx.make_id("laf_", licensing_subscription_id, billing_period, amount_usd)
    invoice = _InvoiceNumbers.issue(ctx, "admin", licensing_subscription_id, billing_period)
    amount = round(float(amount_usd), 2)
    ctx.create("licensing_billing", rid, licensing_billing_entry_id=rid,
               licensing_subscription_id=licensing_subscription_id, customer_id=sub["customer_id"],
               event_type="licensing_admin_fee", amount_usd=amount, invoice_number=invoice,
               cycle_start_date="", billing_period=billing_period, posted_date=ctx.now()[:10],
               charge_reason="not_applicable", payment_reference="")
    balance = round(float(sub["balance_due_usd"]) + amount, 2)
    ctx.update("licensing_subscriptions", licensing_subscription_id, balance_due_usd=balance)
    return (f"Administration fee {rid} of {amount:.2f} USD for {billing_period} invoiced on {invoice}; "
            f"balance owed on the subscription is now {balance:.2f} USD.")


@tool(owner="agent", rw="write")
def post_seat_addition_charge_bba679a2(ctx: ToolContext, licensing_subscription_id: str,
                                       licensing_license_change_id: str, cycle_start_date: str,
                                       amount_usd: float) -> str:
    """Invoice the partial-cycle charge for licenses added to a Microsoft 365 subscription by one seat
    addition. One call books one charge entry for that seat addition, in the billing cycle named, on a
    new invoice, and raises the balance the client owes on the subscription by
    that amount. The client sees the charge on the new invoice. The receipt returns the ledger entry
    reference, the new invoice number, the seat addition charged, the amount and the new balance.

    Args:
        licensing_subscription_id: Id class — reference number of the Microsoft 365 subscription the
            licenses were added to, as returned by the subscription lookup.
        licensing_license_change_id: Id class — reference number of the seat addition being charged, as
            returned by the license change lookup.
        cycle_start_date: Fixed-format class — the first day of the billing cycle the charge relates to, written
            YYYY-MM-DD exactly as the cycle start appears on the billing ledger.
        amount_usd: Fixed-format class — the partial-cycle charge in USD, a positive number to 2 decimal
            places, rounded half up to the cent.

    Returns:
        A confirmation sentence naming the charge entry reference (prefix lsc_), the new invoice
        (INV- followed by 6 digits), the seat addition charged, the amount in USD to 2 decimal places and
        the subscription's new balance owed in USD to 2 decimal places; its presence means the charge is
        invoiced.
    """
    sub = ctx.find("licensing_subscriptions", licensing_subscription_id=licensing_subscription_id)[0]
    rid = ctx.make_id("lsc_", licensing_subscription_id, licensing_license_change_id, cycle_start_date, amount_usd)
    invoice = _InvoiceNumbers.issue(ctx, "seat", licensing_subscription_id, licensing_license_change_id)
    amount = round(float(amount_usd), 2)
    ctx.create("licensing_billing", rid, licensing_billing_entry_id=rid,
               licensing_subscription_id=licensing_subscription_id, customer_id=sub["customer_id"],
               event_type="licensing_prorated_charge", amount_usd=amount, invoice_number=invoice,
               cycle_start_date=cycle_start_date, billing_period="", posted_date=ctx.now()[:10],
               charge_reason="seat_addition", licensing_license_change_id=licensing_license_change_id,
               payment_reference="")
    balance = round(float(sub["balance_due_usd"]) + amount, 2)
    ctx.update("licensing_subscriptions", licensing_subscription_id, balance_due_usd=balance)
    return (f"Seat addition charge {rid} of {amount:.2f} USD for {licensing_license_change_id} invoiced on "
            f"{invoice}; balance owed on the subscription is now {balance:.2f} USD.")


@tool(owner="user", rw="write")
def cancel_subscription_in_window_d46a60fb(ctx: ToolContext, customer_id: str, licensing_subscription_id: str,
                                           invoice_number: str, cycle_start_date: str,
                                           refund_amount_usd: float) -> str:
    """The client's authorized contact e-signs the cancellation order form for a whole Microsoft 365
    subscription inside its cancellation window, and the cancellation takes effect. One call records the
    signed cancellation order form, closes the subscription as cancelled today with no licenses left,
    records the removal of all of its licenses, and books the refund credit stated on the form against
    the invoice and billing cycle named, lowering the balance owed by that amount. The receipt
    returns the order form, the removal, the refund entry, the licenses removed, the refund and the new
    balance.

    Args:
        customer_id: Id class — client reference number of the organisation signing the cancellation, as
            given to the client by the service desk from the client profile lookup.
        licensing_subscription_id: Id class — reference number of the Microsoft 365 subscription being
            cancelled, as given to the client by the service desk from the subscription lookup.
        invoice_number: Fixed-format class — the invoice the refund credit is applied to, written as INV- followed
            by 6 digits exactly as the service desk reads it from the billing ledger.
        cycle_start_date: Fixed-format class — the first day of the billing cycle the refund relates to, written
            YYYY-MM-DD exactly as the service desk reads it from the billing ledger.
        refund_amount_usd: Fixed-format class — the refund credit stated on the cancellation order form in
            USD, a positive number to 2 decimal places, rounded half up to the cent.

    Returns:
        A confirmation sentence naming the signed order form reference (prefix lcf_), the license removal
        reference (prefix lrm_), the refund entry reference (prefix lrf_), the number of licenses removed
        (integer), the refund in USD to 2 decimal places and the subscription's new balance owed in USD to
        2 decimal places; its presence means the subscription is cancelled.
    """
    sub = ctx.find("licensing_subscriptions", licensing_subscription_id=licensing_subscription_id)[0]
    amount = round(float(refund_amount_usd), 2)
    qty = int(sub["license_qty"])
    form = ctx.make_id("lcf_", customer_id, licensing_subscription_id, invoice_number, refund_amount_usd)
    ctx.create("licensing_change_requests", form, licensing_request_id=form, customer_id=customer_id,
               licensing_subscription_id=licensing_subscription_id, request_type="cancellation",
               requested_variant_name="not_applicable", requested_term_type="not_applicable",
               requested_billing_frequency="not_applicable", requested_qty=0, requested_auto_renew="unchanged",
               request_status="signed", created_at=ctx.now())
    removal = ctx.make_id("lrm_", licensing_subscription_id, refund_amount_usd)
    ctx.create("licensing_license_changes", removal, licensing_license_change_id=removal,
               licensing_subscription_id=licensing_subscription_id, customer_id=sub["customer_id"],
               event_type="licensing_licenses_removed", qty=qty, effective_at=ctx.now()[:16],
               change_reason="cancellation")
    refund = ctx.make_id("lrf_", licensing_subscription_id, refund_amount_usd)
    ctx.create("licensing_billing", refund, licensing_billing_entry_id=refund,
               licensing_subscription_id=licensing_subscription_id, customer_id=sub["customer_id"],
               event_type="licensing_refund_credit", amount_usd=amount, invoice_number=invoice_number,
               cycle_start_date=cycle_start_date, billing_period="", posted_date=ctx.now()[:10],
               charge_reason="cancellation", licensing_license_change_id=removal, payment_reference="")
    balance = round(float(sub["balance_due_usd"]) - amount, 2)
    ctx.update("licensing_subscriptions", licensing_subscription_id, status="cancelled", license_qty=0,
               closed_date=ctx.now()[:10], auto_renew=False, balance_due_usd=balance)
    return (f"Cancellation form {form} signed; removal {removal} of {qty} licenses; refund {refund} of "
            f"{amount:.2f} USD credited; balance owed on the subscription is now {balance:.2f} USD.")
